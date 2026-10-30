#!/usr/bin/env python
"""F1 / MIM5: SparK-style continued masked-image-model pretraining of the smp ResNet-34 encoder (1 channel, ImageNet
start exactly as ``smp_unetpp`` builds it) on an explicit image list (``scripts/build_mim_pool.py``).

Deterministic per machine: the epoch order is ``randperm`` seeded by (seed, epoch); augmentation and mask draws for
step s come from a generator seeded by (seed, s), so ``--resume`` continues the exact sequence and ``--max_steps``
(smoke) is a prefix of the full run (the schedule is always that of the full run).

Augmentation = the label-safe supervised set (h/v flip, rot90, brightness/contrast +/-0.2 with p 0.4), no resize,
no crop, no blur, no noise; normalisation mean 0.5, std 0.25 as in fine-tuning.

Optimisation (coach_mim5.md C): AdamW; decoder group peak --lr, encoder group --lr x --enc_lr_mult; global linear
warmup over --warmup_epochs then cosine to --min_lr; the encoder is frozen (no grad) for --freeze_enc_epochs and then
ramps linearly from 0 over --enc_warmup_steps on top of the global schedule.

Outputs in --out: train.log, args.json, pool_files.md5 (md5 of every image file), ckpt_latest.pth (resume),
mim_step0.pth (the start encoder through the same save path), encoder_ep<E>.pth (--save_epochs),
encoder_final.pth (+ .md5), recon_step<N>.png (pool images only). Encoder files are {"models": {"model":
{"encoder.<key>": tensor}}}, loadable by model.encoder_init. --monitor_list: held-out reconstruction loss (eval mode,
fixed masks) every --monitor_every steps, for an overfit check only (never selection).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import logging
import math
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import torch
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.pretrain.spark import SparKResNet, densify_  # noqa: E402

logger = logging.getLogger("pretrain_mim")


def parse_args(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--list", required=True, help="image list, one path per line relative to --data_root")
    p.add_argument("--data_root", default="data")
    p.add_argument("--out", required=True)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--epochs", type=float, default=100)
    p.add_argument("--batch", type=int, default=64)
    p.add_argument("--lr", type=float, default=1e-3, help="peak lr of the decoder group (decoder, densify, tokens)")
    p.add_argument("--enc_lr_mult", type=float, default=0.2, help="encoder peak lr = lr * this")
    p.add_argument("--enc_warmup_steps", type=int, default=1000, help="encoder lr ramp from 0 after the unfreeze")
    p.add_argument("--min_lr", type=float, default=0.0)
    p.add_argument("--wd", type=float, default=0.04)
    p.add_argument("--beta2", type=float, default=0.95)
    p.add_argument("--warmup_epochs", type=float, default=2)
    p.add_argument("--freeze_enc_epochs", type=float, default=2, help="encoder frozen (no grad) for these epochs")
    p.add_argument("--clip", type=float, default=5.0)
    p.add_argument("--mask_ratio", type=float, default=0.6)
    p.add_argument("--patch", type=int, default=32)
    p.add_argument("--width", type=int, default=512)
    p.add_argument("--p_jitter", type=float, default=0.4)
    p.add_argument("--jitter", type=float, default=0.2)
    p.add_argument("--encoder_weights", default="imagenet", help="'imagenet' or 'none'")
    p.add_argument("--max_steps", type=int, default=0, help=">0: stop after this step (smoke); schedule unchanged")
    p.add_argument("--log_every", type=int, default=50)
    p.add_argument("--ckpt_every", type=int, default=1000)
    p.add_argument("--save_epochs", default="", help="comma list of epochs to save encoder_ep<E>.pth")
    p.add_argument("--recon_every", type=int, default=0, help=">0: recon picture every N steps (plus start/end)")
    p.add_argument("--load_workers", type=int, default=16)
    p.add_argument("--monitor_list", default=None, help="held-out image list for the reconstruction monitor")
    p.add_argument("--monitor_every", type=int, default=1000)
    p.add_argument("--resume", action="store_true")
    p.add_argument("--device", default=None)
    return p.parse_args(argv)


def setup_logging(path: Path, append: bool) -> None:
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s - %(message)s")
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    for h in list(root.handlers):
        root.removeHandler(h)
    for h in (logging.StreamHandler(sys.stdout), logging.FileHandler(path, mode="a" if append else "w")):
        h.setFormatter(fmt)
        root.addHandler(h)


def file_md5(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


def load_images(paths: list[Path], workers: int) -> tuple[torch.Tensor, list[str]]:
    """All images as one uint8 tensor (N, 1, H, W) plus the md5 of each file's bytes."""
    def one(p: Path):
        b = p.read_bytes()
        from io import BytesIO
        a = np.array(Image.open(BytesIO(b)).convert("L"), dtype=np.uint8)
        return a, hashlib.md5(b).hexdigest()
    with ThreadPoolExecutor(max_workers=workers) as ex:
        out = list(ex.map(one, paths))
    shapes = {a.shape for a, _ in out}
    if len(shapes) != 1:
        raise ValueError(f"images differ in size: {sorted(shapes)[:5]}")
    arr = np.stack([a for a, _ in out])[:, None]
    return torch.from_numpy(arr), [m for _, m in out]


def step_generator(seed: int, step: int) -> torch.Generator:
    return torch.Generator().manual_seed(seed * 1_000_003 + 7919 * step + 17)


def epoch_order(seed: int, epoch: int, n: int) -> torch.Tensor:
    return torch.randperm(n, generator=torch.Generator().manual_seed(seed * 1_000_003 + 104_729 * epoch + 3))


def augment(xb: torch.Tensor, g: torch.Generator, p_jitter: float = 0.4, jitter: float = 0.2) -> torch.Tensor:
    """uint8 (B, 1, H, W) on any device -> normalised float32. Exact pixel permutations + brightness/contrast.

    Draw order per batch is fixed (h-flip, v-flip, rot90 on/off, k, jitter on/off, contrast, brightness), all from the
    CPU generator ``g``, so the result is a pure function of (images, g's seed)."""
    b = xb.shape[0]
    hf = torch.rand(b, generator=g) < 0.5
    vf = torch.rand(b, generator=g) < 0.5
    rot = torch.rand(b, generator=g) < 0.5
    k = torch.randint(0, 4, (b,), generator=g)  # albumentations RandomRotate90: k in 0..3 when applied
    jit = torch.rand(b, generator=g) < p_jitter
    alpha = 1.0 + (torch.rand(b, generator=g) * 2 - 1) * jitter
    beta = (torch.rand(b, generator=g) * 2 - 1) * jitter
    x = xb.float() / 255.0
    out = []
    for i in range(b):
        xi = x[i]
        if hf[i]:
            xi = torch.flip(xi, dims=[2])
        if vf[i]:
            xi = torch.flip(xi, dims=[1])
        if rot[i]:
            xi = torch.rot90(xi, int(k[i]), dims=[1, 2])
        if jit[i]:
            xi = (xi * float(alpha[i]) + float(beta[i])).clamp_(0.0, 1.0)
        out.append(xi)
    return (torch.stack(out) - 0.5) / 0.25


def build_encoder(weights: str):
    import segmentation_models_pytorch as smp
    w = None if weights in ("none", "None", "") else weights
    # Exactly the encoder smp.UnetPlusPlus(encoder_name="resnet34", encoder_weights=w, in_channels=1) holds.
    return smp.encoders.get_encoder("resnet34", in_channels=1, depth=5, weights=w)


def lr_at(step: int, total: int, warmup: int, peak: float, min_lr: float) -> float:
    if step < warmup:
        return peak * (step + 1) / warmup
    t = (step - warmup) / max(1, total - warmup)
    return min_lr + 0.5 * (peak - min_lr) * (1 + math.cos(math.pi * min(1.0, t)))


def enc_lr_factor(step: int, freeze: int, enc_warm: int) -> float:
    """0 while frozen; then a linear ramp (step - freeze + 1) / enc_warm, capped at 1."""
    if step < freeze:
        return 0.0
    return min(1.0, (step - freeze + 1) / max(1, enc_warm))


def encoder_file(model: SparKResNet) -> dict:
    return {"models": {"model": model.encoder_state_dict()}}


@torch.no_grad()
def monitor_loss(model: SparKResNet, mon: torch.Tensor, device, batch: int = 32) -> float:
    """Mean masked-patch loss on held-out images: no augmentation, eval mode, masks fixed by a constant seed."""
    model.eval()
    g = torch.Generator().manual_seed(999_331)
    tot, n = 0.0, 0
    for i in range(0, mon.shape[0], batch):
        x = (mon[i:i + batch].to(device).float() / 255.0 - 0.5) / 0.25
        m = model.random_mask(x.shape[0], x.shape[-2], x.shape[-1], generator=g, device=device)
        with torch.autocast(device_type=device.type, dtype=torch.bfloat16, enabled=device.type == "cuda"):
            loss, _ = model(x, m)
        tot += float(loss) * x.shape[0]
        n += x.shape[0]
    model.train()
    return tot / max(n, 1)


def save_recon(model: SparKResNet, x: torch.Tensor, mask: torch.Tensor, path: Path) -> None:
    """Rows: input, masked input, reconstruction (target scale), recon pasted into visible input."""
    model.eval()
    with torch.no_grad(), torch.autocast(device_type=x.device.type, dtype=torch.bfloat16,
                                         enabled=x.device.type == "cuda"):
        _, rec = model(x, mask)
    model.train()
    rec = model.unpatch_target(x, rec)
    m = mask.float().repeat_interleave(model.patch, 2).repeat_interleave(model.patch, 3)
    rows = [x, x * m, rec, x * m + rec * (1 - m)]
    to8 = lambda t: ((t * 0.25 + 0.5).clamp(0, 1) * 255).round().byte().cpu().numpy()
    grid = np.concatenate([np.concatenate([to8(r)[i, 0] for i in range(x.shape[0])], axis=1) for r in rows], axis=0)
    Image.fromarray(grid).save(path)


def main(argv=None) -> None:
    a = parse_args(argv)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    ck = out / "ckpt_latest.pth"
    if a.resume and not ck.exists():
        raise FileNotFoundError(f"--resume: {ck} missing")
    if not a.resume and (ck.exists() or (out / "encoder_final.pth").exists()):
        raise FileExistsError(f"{out} already has outputs; use --resume or a new --out")
    setup_logging(out / "train.log", append=a.resume)
    if not a.resume:
        (out / "args.json").write_text(json.dumps(vars(a), indent=1))
    logger.info("args %s", vars(a))

    from src.utils.seed import set_seed
    set_seed(a.seed, deterministic=True)
    device = torch.device(a.device or ("cuda" if torch.cuda.is_available() else "cpu"))

    # ---- data ----
    rels = [ln.strip() for ln in Path(a.list).read_text().splitlines() if ln.strip()]
    if len(set(rels)) != len(rels):
        raise ValueError("duplicate paths in --list")
    paths = [Path(a.data_root) / r for r in rels]
    t0 = time.time()
    imgs, md5s = load_images(paths, a.load_workers)
    man = "".join(f"{m}  {r}\n" for m, r in zip(md5s, rels))
    if not a.resume:
        (out / "pool_files.md5").write_text(man)
    data_md5 = hashlib.md5(man.encode()).hexdigest()
    logger.info("pool: %d images %s from %s (list md5 %s, files manifest md5 %s) loaded in %.0fs", len(rels),
                tuple(imgs.shape[1:]), a.list, file_md5(Path(a.list)), data_md5, time.time() - t0)
    if a.resume:
        old = (out / "pool_files.md5").read_text()
        if old != man:
            raise ValueError("pool changed since the run started")
    n, H, W = imgs.shape[0], imgs.shape[-2], imgs.shape[-1]
    if H % 32 or W % 32 or H % a.patch:
        raise ValueError("image size must be a multiple of 32 and of --patch")
    imgs = imgs.pin_memory() if device.type == "cuda" else imgs
    mon = None
    if a.monitor_list:
        mrels = [ln.strip() for ln in Path(a.monitor_list).read_text().splitlines() if ln.strip()]
        if set(mrels) & set(rels):
            raise ValueError("monitor images overlap the training list")
        mon, _ = load_images([Path(a.data_root) / r for r in mrels], a.load_workers)
        logger.info("monitor: %d held-out images from %s (list md5 %s)", len(mrels), a.monitor_list,
                    file_md5(Path(a.monitor_list)))

    # ---- model ----
    torch.manual_seed(a.seed)
    enc = build_encoder(a.encoder_weights)
    model = SparKResNet(enc, enc_channels=list(enc.out_channels)[2:], width=a.width, patch=a.patch,
                        mask_ratio=a.mask_ratio).to(device)
    logger.info("SparK: %d sparse modules; encoder %.2fM, rest %.2fM params", model.n_sparse,
                sum(p.numel() for p in model.encoder.parameters()) / 1e6,
                sum(p.numel() for n_, p in model.named_parameters() if not n_.startswith("encoder.")) / 1e6)

    enc_params = list(model.encoder.parameters())
    groups = {(e, w): [] for e in ("enc", "dec") for w in (True, False)}
    for name, prm in model.named_parameters():
        decay = prm.ndim > 1 and "mask_tokens" not in name  # no weight decay on biases, norms, mask tokens
        groups[("enc" if name.startswith("encoder.") else "dec", decay)].append(prm)
    groups = [dict(params=v, weight_decay=a.wd if w else 0.0, name=e) for (e, w), v in groups.items() if v]
    opt = torch.optim.AdamW(groups, lr=a.lr, betas=(0.9, a.beta2))

    spe = n // a.batch  # steps per epoch (drop last)
    total = int(round(a.epochs * spe))
    warm = int(round(a.warmup_epochs * spe))
    freeze = int(round(a.freeze_enc_epochs * spe))
    save_ep = {int(e) for e in a.save_epochs.split(",") if e.strip()}
    logger.info("steps/epoch %d, total %d, warmup %d, encoder frozen for %d then enc warmup %d, batch %d", spe, total,
                warm, freeze, a.enc_warmup_steps, a.batch)

    step = 0
    if a.resume:
        st = torch.load(ck, map_location="cpu", weights_only=False)
        model.load_state_dict(st["model"])
        opt.load_state_dict(st["opt"])
        step = int(st["step"])
        logger.info("resumed at step %d", step)

    # fixed recon picture inputs: first 4 list images, step-independent mask
    rx = augment(imgs[:4].to(device), torch.Generator().manual_seed(12345), p_jitter=0.0)
    rm = model.random_mask(4, H, W, generator=torch.Generator().manual_seed(54321), device=device)
    if step == 0:
        torch.save(encoder_file(model), out / "mim_step0.pth")
        logger.info("mim_step0.pth md5 %s", file_md5(out / "mim_step0.pth"))
        save_recon(model, rx, rm, out / "recon_step0.png")
        if mon is not None:
            logger.info("monitor step 0 loss=%.4f", monitor_loss(model, mon, device))

    stop = min(total, a.max_steps) if a.max_steps > 0 else total
    model.train()
    hist, t_log, s_log = [], time.time(), step
    while step < stop:
        ep, pos = divmod(step, spe)
        order = epoch_order(a.seed, ep, n)
        idx = order[pos * a.batch:(pos + 1) * a.batch]
        g = step_generator(a.seed, step)
        x = augment(imgs[idx].to(device, non_blocking=True), g, a.p_jitter, a.jitter)
        mask = model.random_mask(x.shape[0], H, W, generator=g, device=device)
        frozen = step < freeze
        for p in enc_params:
            p.requires_grad_(not frozen)
        lr = lr_at(step, total, warm, a.lr, a.min_lr)
        enc_lr = lr * a.enc_lr_mult * enc_lr_factor(step, freeze, a.enc_warmup_steps)
        for gr in opt.param_groups:
            gr["lr"] = enc_lr if gr["name"] == "enc" else lr
        with torch.autocast(device_type=device.type, dtype=torch.bfloat16, enabled=device.type == "cuda"):
            loss, _ = model(x, mask)
        opt.zero_grad(set_to_none=True)
        loss.backward()
        egn = 0.0 if frozen else float(torch.sqrt(sum((p.grad.float() ** 2).sum() for p in enc_params
                                                          if p.grad is not None)))
        gn = torch.nn.utils.clip_grad_norm_([p for p in model.parameters() if p.grad is not None], a.clip)
        if not torch.isfinite(loss):
            raise FloatingPointError(f"non-finite loss at step {step}")
        opt.step()
        step += 1
        hist.append((float(loss.detach()), float(gn), egn, float(gn) > a.clip))
        if step % a.log_every == 0 or step == stop:
            dt = time.time() - t_log
            ls, gs, es, cs = zip(*hist)
            logger.info("step %d/%d ep %.2f loss=%.4f grad_norm=%.3f enc_grad_norm=%.3f clipped=%.2f lr=%.3g "
                        "enc_lr=%.3g frozen=%d samples/s=%.1f mem=%.1fG", step, total, step / spe, float(np.mean(ls)),
                        float(np.mean(gs)), float(np.mean(es)), float(np.mean(cs)), lr, enc_lr, int(frozen),
                        (step - s_log) * a.batch / max(dt, 1e-6),
                        torch.cuda.max_memory_allocated() / 2**30 if device.type == "cuda" else 0.0)
            hist, t_log, s_log = [], time.time(), step
        if mon is not None and (step % a.monitor_every == 0 or step == stop):
            logger.info("monitor step %d loss=%.4f", step, monitor_loss(model, mon, device))
        if a.recon_every and step % a.recon_every == 0:
            save_recon(model, rx, rm, out / f"recon_step{step}.png")
        if step % spe == 0 and (step // spe) in save_ep:
            torch.save(encoder_file(model), out / f"encoder_ep{step // spe}.pth")
        if step % a.ckpt_every == 0 or step == stop:
            torch.save({"model": model.state_dict(), "opt": opt.state_dict(), "step": step}, ck)

    save_recon(model, rx, rm, out / f"recon_step{step}.png")
    if step == total:
        ef = encoder_file(model)
        torch.save(ef, out / "encoder_final.pth")
        m = file_md5(out / "encoder_final.pth")
        (out / "encoder_final.md5").write_text(f"{m}  encoder_final.pth\n")
        logger.info("DONE step %d/%d encoder_final.pth md5 %s (%d tensors)", step, total, m, len(ef["models"]["model"]))
    else:
        logger.info("STOPPED at step %d/%d (--max_steps); no encoder_final.pth", step, total)
    densify_(model.encoder)


if __name__ == "__main__":
    main()
