#!/usr/bin/env python
"""F2 / DDeP5: decoder denoising pretraining (Brempong et al., arXiv:2205.11423) of the smp U-Net++ decoder of the A5c
network, with the ImageNet ResNet-34 encoder frozen (weights fixed, BN in train mode, i.e. batch statistics, so the
decoder learns on the feature statistics it sees at fine-tune), on the MIM image list (no labels).

x' = sqrt(gamma) * x + sqrt(1 - gamma) * eps on the normalised input (gamma 0.95); a temporary 1x1 head on the 16-channel
decoder output predicts eps (no input-to-output skip); MSE over all pixels. Inputs are random native-scale crops
(--crop, integer offsets, no resizing) with the label-safe set (h/v flip, rot90, brightness/contrast) as MIM.
Adam, peak --lr after a linear warmup, cosine to 0; bf16 autocast; grad clip --clip.

Deterministic per machine: crop offsets, augmentation and noise for step s are pure functions of (seed, s); the epoch
order of (seed, epoch); --resume continues the exact sequence; --max_steps (smoke) is a prefix of the full run.

Outputs in --out: train.log, args.json, pool_files.md5, ckpt_latest.pth (resume), dec_step0.pth (the random start),
decoder_final.pth (+ .md5) = {"models": {"model": {"decoder.<key>": ...}}} for model.decoder_init (the temporary head
and the segmentation head are not saved), monitor loss on --monitor_list (eval mode, full cells, fixed noise).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import logging
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "scripts"))

from pretrain_mim import augment, epoch_order, file_md5, load_images, lr_at, setup_logging, step_generator  # noqa: E402

logger = logging.getLogger("pretrain_ddep")


def parse_args(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--list", required=True)
    p.add_argument("--monitor_list", default=None)
    p.add_argument("--data_root", default="data")
    p.add_argument("--out", required=True)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--steps", type=int, default=40000)
    p.add_argument("--batch", type=int, default=32)
    p.add_argument("--crop", type=int, default=256)
    p.add_argument("--gamma", type=float, default=0.95)
    p.add_argument("--lr", type=float, default=1e-4)
    p.add_argument("--warmup_steps", type=int, default=500)
    p.add_argument("--wd", type=float, default=0.0)
    p.add_argument("--clip", type=float, default=1.0)
    p.add_argument("--p_jitter", type=float, default=0.4)
    p.add_argument("--jitter", type=float, default=0.2)
    p.add_argument("--encoder_weights", default="imagenet")
    p.add_argument("--max_steps", type=int, default=0)
    p.add_argument("--log_every", type=int, default=50)
    p.add_argument("--ckpt_every", type=int, default=1000)
    p.add_argument("--monitor_every", type=int, default=2000)
    p.add_argument("--load_workers", type=int, default=16)
    p.add_argument("--resume", action="store_true")
    p.add_argument("--device", default=None)
    return p.parse_args(argv)


class DDePNet(nn.Module):
    """A5c's smp U-Net++ (built exactly as model.name=smp_unetpp) with a temporary 1x1 eps head on the decoder output.
    The encoder is frozen (no grad) but its BN layers follow the module's train/eval mode."""

    def __init__(self, encoder_weights: str = "imagenet") -> None:
        super().__init__()
        from src.models.model_factory import build_model
        w = None if encoder_weights in ("none", "None", "") else encoder_weights
        self.net = build_model({"name": "smp_unetpp", "encoder_name": "resnet34", "encoder_weights": w,
                                "in_channels": 1, "num_classes": 24})
        for p in self.net.encoder.parameters():
            p.requires_grad_(False)
        ch = self.net.segmentation_head[0].in_channels
        self.eps_head = nn.Conv2d(ch, 1, kernel_size=1)

    def forward(self, x):
        with torch.no_grad():
            feats = self.net.encoder(x)
        return self.eps_head(self.net.decoder(feats))

    def decoder_file(self) -> dict:
        return {"models": {"model": {f"decoder.{k}": v.detach().cpu().clone()
                                     for k, v in self.net.decoder.state_dict().items()}}}


def random_crops(xb: torch.Tensor, crop: int, g: torch.Generator) -> torch.Tensor:
    """Integer-offset crops (no resampling), one offset pair per image, drawn from ``g``."""
    b, _, h, w = xb.shape
    if crop >= h and crop >= w:
        return xb
    oy = torch.randint(0, h - crop + 1, (b,), generator=g)
    ox = torch.randint(0, w - crop + 1, (b,), generator=g)
    return torch.stack([xb[i, :, int(oy[i]):int(oy[i]) + crop, int(ox[i]):int(ox[i]) + crop] for i in range(b)])


def noised(x: torch.Tensor, gamma: float, gen: torch.Generator) -> tuple[torch.Tensor, torch.Tensor]:
    eps = torch.randn(x.shape, generator=gen, device=x.device, dtype=torch.float32)
    return (gamma ** 0.5) * x + ((1 - gamma) ** 0.5) * eps, eps


def cuda_or_cpu_gen(device, seed: int) -> torch.Generator:
    return torch.Generator(device=device).manual_seed(seed)


@torch.no_grad()
def monitor_loss(model: DDePNet, mon: torch.Tensor, device, gamma: float, batch: int = 16) -> float:
    model.eval()
    gen = cuda_or_cpu_gen(device, 777_001)
    tot, n = 0.0, 0
    for i in range(0, mon.shape[0], batch):
        x = (mon[i:i + batch].to(device).float() / 255.0 - 0.5) / 0.25
        xn, eps = noised(x, gamma, gen)
        with torch.autocast(device_type=device.type, dtype=torch.bfloat16, enabled=device.type == "cuda"):
            pred = model(xn)
        tot += float(((pred.float() - eps) ** 2).mean()) * x.shape[0]
        n += x.shape[0]
    model.train()
    return tot / max(n, 1)


def main(argv=None) -> None:
    a = parse_args(argv)
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    ck = out / "ckpt_latest.pth"
    if a.resume and not ck.exists():
        raise FileNotFoundError(f"--resume: {ck} missing")
    if not a.resume and (ck.exists() or (out / "decoder_final.pth").exists()):
        raise FileExistsError(f"{out} already has outputs; use --resume or a new --out")
    if a.crop % 32:
        raise ValueError("--crop must be a multiple of 32")
    setup_logging(out / "train.log", append=a.resume)
    if not a.resume:
        (out / "args.json").write_text(json.dumps(vars(a), indent=1))
    logger.info("args %s", vars(a))
    from src.utils.seed import set_seed
    set_seed(a.seed, deterministic=True)
    device = torch.device(a.device or ("cuda" if torch.cuda.is_available() else "cpu"))

    rels = [ln.strip() for ln in Path(a.list).read_text().splitlines() if ln.strip()]
    t0 = time.time()
    imgs, md5s = load_images([Path(a.data_root) / r for r in rels], a.load_workers)
    man = "".join(f"{m}  {r}\n" for m, r in zip(md5s, rels))
    if a.resume and (out / "pool_files.md5").read_text() != man:
        raise ValueError("pool changed since the run started")
    if not a.resume:
        (out / "pool_files.md5").write_text(man)
    logger.info("pool: %d images %s from %s (list md5 %s, files manifest md5 %s) loaded in %.0fs", len(rels),
                tuple(imgs.shape[1:]), a.list, file_md5(Path(a.list)), hashlib.md5(man.encode()).hexdigest(),
                time.time() - t0)
    imgs = imgs.pin_memory() if device.type == "cuda" else imgs
    mon = None
    if a.monitor_list:
        mrels = [ln.strip() for ln in Path(a.monitor_list).read_text().splitlines() if ln.strip()]
        if set(mrels) & set(rels):
            raise ValueError("monitor images overlap the training list")
        mon, _ = load_images([Path(a.data_root) / r for r in mrels], a.load_workers)
        logger.info("monitor: %d held-out images (list md5 %s)", len(mrels), file_md5(Path(a.monitor_list)))
    n = imgs.shape[0]

    torch.manual_seed(a.seed)
    model = DDePNet(a.encoder_weights).to(device)
    model.train()
    params = [p for p in model.parameters() if p.requires_grad]
    logger.info("DDeP: trainable %.2fM (decoder + eps head), frozen encoder %.2fM", sum(p.numel() for p in params) / 1e6,
                sum(p.numel() for p in model.net.encoder.parameters()) / 1e6)
    opt = torch.optim.Adam(params, lr=a.lr, weight_decay=a.wd)
    spe = n // a.batch
    total = a.steps
    step = 0
    if a.resume:
        st = torch.load(ck, map_location="cpu", weights_only=False)
        model.load_state_dict(st["model"]); opt.load_state_dict(st["opt"]); step = int(st["step"])
        logger.info("resumed at step %d", step)
    else:
        torch.save(model.decoder_file(), out / "dec_step0.pth")
        logger.info("dec_step0.pth md5 %s", file_md5(out / "dec_step0.pth"))
        if mon is not None:
            logger.info("monitor step 0 loss=%.4f", monitor_loss(model, mon, device, a.gamma))
    logger.info("steps/epoch %d (crops of %d), total %d, warmup %d, batch %d, gamma %.3f", spe, a.crop, total,
                a.warmup_steps, a.batch, a.gamma)

    stop = min(total, a.max_steps) if a.max_steps > 0 else total
    hist, t_log, s_log = [], time.time(), step
    while step < stop:
        ep, pos = divmod(step, spe)
        idx = epoch_order(a.seed, ep, n)[pos * a.batch:(pos + 1) * a.batch]
        g = step_generator(a.seed, step)
        xb = random_crops(imgs[idx], a.crop, g)
        x = augment(xb.to(device, non_blocking=True), g, a.p_jitter, a.jitter)
        xn, eps = noised(x, a.gamma, cuda_or_cpu_gen(device, a.seed * 1_000_003 + 31 * step + 5))
        lr = lr_at(step, total, a.warmup_steps, a.lr, 0.0)
        for gr in opt.param_groups:
            gr["lr"] = lr
        with torch.autocast(device_type=device.type, dtype=torch.bfloat16, enabled=device.type == "cuda"):
            pred = model(xn)
        loss = ((pred.float() - eps) ** 2).mean()
        opt.zero_grad(set_to_none=True)
        loss.backward()
        gn = torch.nn.utils.clip_grad_norm_(params, a.clip)
        if not torch.isfinite(loss):
            raise FloatingPointError(f"non-finite loss at step {step}")
        opt.step()
        step += 1
        hist.append((float(loss.detach()), float(gn), float(gn) > a.clip))
        if step % a.log_every == 0 or step == stop:
            dt = time.time() - t_log
            ls, gs, cs = zip(*hist)
            logger.info("step %d/%d ep %.2f loss=%.4f grad_norm=%.3f clipped=%.2f lr=%.3g samples/s=%.1f mem=%.1fG",
                        step, total, step / spe, float(np.mean(ls)), float(np.mean(gs)), float(np.mean(cs)), lr,
                        (step - s_log) * a.batch / max(dt, 1e-6),
                        torch.cuda.max_memory_allocated() / 2**30 if device.type == "cuda" else 0.0)
            hist, t_log, s_log = [], time.time(), step
        if mon is not None and (step % a.monitor_every == 0 or step == stop):
            logger.info("monitor step %d loss=%.4f", step, monitor_loss(model, mon, device, a.gamma))
        if step % a.ckpt_every == 0 or step == stop:
            torch.save({"model": model.state_dict(), "opt": opt.state_dict(), "step": step}, ck)
    if step == total:
        torch.save(model.decoder_file(), out / "decoder_final.pth")
        m = file_md5(out / "decoder_final.pth")
        (out / "decoder_final.md5").write_text(f"{m}  decoder_final.pth\n")
        logger.info("DONE step %d/%d decoder_final.pth md5 %s", step, total, m)
    else:
        logger.info("STOPPED at step %d/%d (--max_steps); no decoder_final.pth", step, total)


if __name__ == "__main__":
    main()
