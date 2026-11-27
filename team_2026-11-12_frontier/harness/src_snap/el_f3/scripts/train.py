"""Main training entry point: supervised, Mean Teacher or ALHVR (``method`` in the config).

Usage::

    python scripts/train.py --config configs/supervised.yaml \\
        --opts data.labeled_fraction=0.2 seed=0 training.total_steps=200

Labelled data: ``data/splits/train.txt`` for ``labeled_fraction: 1.0``,
otherwise ``data/splits/seed<seed>/labeled_<P>pct.txt``.  SSL runs use the
matching ``unlabeled_<P>pct.txt`` (the remaining train images).  Every split
file is required.

Outputs go to ``experiments/<run_name>/``: ``config_used.yaml``,
``train.log``, ``metrics.json`` and ``checkpoints/{best,latest}.pth``
(git-ignored).

``--resume`` continues from ``checkpoints/latest.pth`` of the same run (the
config must match the one stored in it).  Starting a run whose directory
already holds a checkpoint or metrics.json needs ``--overwrite``.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import shutil
import sys
from pathlib import Path

# Deterministic cuBLAS needs this before CUDA initialises.
os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")

import torch
import yaml
from torch.utils.data import DataLoader, Dataset

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.data.augmentations import (
    get_flip_augmentation,
    get_geometric_augmentation,
    get_labelsafe_augmentation,
    get_labelsafe_geometric,
    get_labelsafe_strong_photometric,
    get_strong_augmentation,
    get_strong_photometric,
    get_weak_augmentation,
    get_weak_photometric,
)
from src.data.stream import BatchStream
from src.data.ucf_el import (
    UCF_METRIC_KW,
    UCFELDataset,
    count_ucf_class_pixels,
    get_ucf_eval_transform,
    get_ucf_geometric,
    get_ucf_strong_photometric,
    get_ucf_train_transform,
    get_ucf_weak_photometric,
)
from src.data.benchmark_el import BenchmarkELDataset
from src.data.class_info import CLASS_INFO
from src.data.class_stats import count_class_pixels
from src.data.splits import load_split
from src.losses.loss_factory import build_losses
from src.models.model_factory import build_model
from src.models.encoder_init import load_decoder_init, load_encoder_init
from src.trainers.trainer import Trainer
from src.trainers.alhvr_trainer import ALHVRTrainer
from src.utils.config import load_config
from src.utils.seed import set_seed

logger = logging.getLogger("train")

METHODS = ("supervised", "mean_teacher", "alhvr", "pvs3")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Train a segmentation model.")
    p.add_argument("--config", required=True, help="Path to YAML config file.")
    p.add_argument("--opts", nargs="*", default=[], help="Overrides, e.g. training.lr=0.0005 seed=1")
    p.add_argument("--device", default="", help="cuda | cpu (auto-detected if empty)")
    p.add_argument("--resume", action="store_true", help="Continue from checkpoints/latest.pth of this run.")
    p.add_argument("--overwrite", action="store_true", help="Start from scratch even if the run directory has outputs.")
    p.add_argument("--exit_after_step", type=int, default=None,
                   help="Testing only: hard-exit right after this step (simulated crash).")
    return p.parse_args()


def apply_opts(cfg: dict, opts: list[str]) -> dict:
    """Apply dot-notation overrides like ``training.lr=0.0005`` (YAML-typed values)."""
    for kv in opts:
        k, _, v = kv.partition("=")
        keys = k.strip().split(".")
        node = cfg
        for part in keys[:-1]:
            node = node.setdefault(part, {})
        node[keys[-1]] = yaml.safe_load(v)
    return cfg


def frac_tag(frac: float) -> str:
    return f"{round(frac * 100)}pct"


def build_optimizer(model: torch.nn.Module, cfg: dict) -> torch.optim.Optimizer:
    t = cfg["training"]
    name = t.get("optimizer", "adam").lower()
    wd = t.get("weight_decay", 1e-4)
    pf = t.get("encoder_pf")
    if pf:  # F3 (opt-in): encoder-preserving fine-tune. Group 0 = everything but the encoder (house lr and wd); group 1 =
        # encoder.* with lr x lr_mult and its own weight decay. Freeze / ramp: the trainer's per-group lr multiplier.
        if name not in ("adam", "adamw"):
            raise ValueError("training.encoder_pf supports adam / adamw")
        named = list(model.named_parameters())
        enc = [p for n, p in named if n.startswith("encoder.")]
        if not enc:
            raise ValueError("training.encoder_pf: the model has no encoder.* parameters")
        groups = [{"params": [p for n, p in named if not n.startswith("encoder.")]},
                  {"params": enc, "lr": t["lr"] * float(pf.get("lr_mult", 0.1)), "weight_decay": float(pf.get("wd", 0.0))}]
        return (torch.optim.Adam if name == "adam" else torch.optim.AdamW)(groups, lr=t["lr"], weight_decay=wd)
    if name == "adam":
        return torch.optim.Adam(model.parameters(), lr=t["lr"], weight_decay=wd)
    if name == "adamw":
        return torch.optim.AdamW(model.parameters(), lr=t["lr"], weight_decay=wd)
    if name == "sgd":
        return torch.optim.SGD(model.parameters(), lr=t["lr"], momentum=t.get("momentum", 0.9), weight_decay=wd,
                               nesterov=bool(t.get("nesterov", False)))
    raise ValueError(f"Unknown optimizer: {name}")


class TwoViewDataset(Dataset):
    """SSL views of a raw dataset: one shared geometric draw, then a strong
    (student) and a weak (teacher) photometric view of the same geometry."""

    def __init__(self, raw: BenchmarkELDataset, geo, strong, weak) -> None:
        self.raw, self.geo, self.strong, self.weak = raw, geo, strong, weak

    def __len__(self) -> int:
        return len(self.raw)

    def __getitem__(self, idx: int) -> dict:
        s = self.raw[idx]
        if "mask" in s:
            g = self.geo(image=s["image"], mask=s["mask"])
        else:
            g = self.geo(image=s["image"])
        out = {
            "image_strong": self.strong(image=g["image"])["image"],
            "image_weak": self.weak(image=g["image"])["image"],
        }
        if "mask" in g:
            out["mask"] = torch.as_tensor(g["mask"], dtype=torch.long)
        return out


class SupervisedViewDataset(Dataset):
    """Labelled SSL stream with the supervised pipeline's single view (``ssl.labeled_aug: supervised``, P11).

    The student's labelled input is then augmented exactly as in the matching supervised arm, so a loss-off Mean
    Teacher run differs from it only in batch composition (BatchNorm over labelled + unlabelled) and data streams.
    ``image_weak`` repeats the same view; it is never used for labelled images (consistency is unlabelled-only).
    """

    def __init__(self, ds: Dataset) -> None:
        self.ds = ds

    def __len__(self) -> int:
        return len(self.ds)

    def __getitem__(self, idx: int) -> dict:
        s = self.ds[idx]
        return {"image_strong": s["image"], "image_weak": s["image"], "mask": s["mask"]}


class HiddenMaskDataset(Dataset):
    """Unlabelled view of a labelled dataset: ``{'image', 'hidden_mask'}``, no ``'mask'`` key."""

    def __init__(self, ds: BenchmarkELDataset) -> None:
        self.ds = ds

    def __len__(self) -> int:
        return len(self.ds)

    def __getitem__(self, idx: int) -> dict:
        s = self.ds[idx]
        return {"image": s["image"], "hidden_mask": s["mask"]}


def setup_logging(log_file: Path, append: bool = False) -> None:
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s — %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    for h in list(root.handlers):
        root.removeHandler(h)
    for h in (logging.StreamHandler(sys.stdout), logging.FileHandler(log_file, mode="a" if append else "w")):
        h.setFormatter(fmt)
        root.addHandler(h)


def main() -> None:
    args = parse_args()
    cfg = apply_opts(load_config(args.config), args.opts)

    seed = int(cfg["seed"])
    d_cfg, t_cfg = cfg["data"], cfg["training"]
    frac = float(d_cfg.get("labeled_fraction", 1.0))
    method = cfg.get("method", "supervised")
    if method not in METHODS:
        raise ValueError(f"method must be one of {METHODS}, got {method!r}")
    is_ssl = method != "supervised"
    if is_ssl and d_cfg.get("dataset", "benchmark_el") == "benchmark_el" and frac >= 1.0:
        raise ValueError("SSL needs labeled_fraction < 1 (the unlabelled pool is the rest of train)")

    run_name = cfg.get("run_name") or f"{Path(args.config).stem}_{cfg['model']['name']}_{frac_tag(frac)}_s{seed}"
    cfg["run_name"] = run_name
    run_dir = Path(cfg.get("logging", {}).get("experiments_dir", "experiments")) / run_name
    latest = run_dir / "checkpoints" / "latest.pth"
    if args.resume and args.overwrite:
        raise ValueError("--resume and --overwrite are mutually exclusive")
    if args.resume and not latest.exists():
        raise FileNotFoundError(f"--resume: {latest} does not exist")
    has_outputs = (run_dir / "metrics.json").exists() or (run_dir / "checkpoints").is_dir() and any(
        (run_dir / "checkpoints").iterdir())
    if not args.resume and has_outputs:
        if not args.overwrite:
            raise FileExistsError(f"{run_dir} already has outputs; use --resume or --overwrite")
        shutil.rmtree(run_dir / "checkpoints", ignore_errors=True)
        for name in ("metrics.json", "regions.csv"):
            (run_dir / name).unlink(missing_ok=True)
    run_dir.mkdir(parents=True, exist_ok=True)
    setup_logging(run_dir / "train.log", append=args.resume)
    if not args.resume:
        with open(run_dir / "config_used.yaml", "w") as f:
            yaml.safe_dump(cfg, f, sort_keys=False)

    set_seed(seed, deterministic=t_cfg.get("deterministic", True))
    device = torch.device(args.device or ("cuda" if torch.cuda.is_available() else "cpu"))
    logger.info("Run: %s  device: %s  config: %s  overrides: %s  resume: %s", run_name, device, args.config,
                args.opts, args.resume)

    dataset = d_cfg.get("dataset", "benchmark_el")
    nw = t_cfg.get("num_workers", 4)
    if dataset == "ucf_el":
        data = build_ucf_data(cfg, method, seed, device, nw)
    elif dataset == "benchmark_el":
        data = build_benchmark_data(cfg, method, seed, frac, is_ssl, device, nw)
    else:
        raise ValueError(f"unknown data.dataset {dataset!r} (benchmark_el | ucf_el)")

    # ---- Model(s) ----
    torch.manual_seed(seed)
    model = build_model(cfg["model"]).to(device)
    model_b = None
    if method == "alhvr":
        torch.manual_seed(seed + 1)  # network B: different init seed
        model_b = build_model(cfg["model"]).to(device)
        torch.manual_seed(seed)
    # ``model.encoder_init`` (opt-in, F1 / MIM5; not in base.yaml): copy encoder weights from a file after the build.
    # Loading draws no random numbers, so the decoder init for this seed is unchanged; absent = no change.
    if cfg["model"].get("encoder_init"):
        logger.info("Encoder initialised from %s", load_encoder_init(model, cfg["model"]["encoder_init"]))
    # ``model.decoder_init`` (opt-in, F2 / DDeP5; not in base.yaml): copy decoder.* weights (never the segmentation
    # head) from a file after the build; no random draw, so the head init for this seed is unchanged; absent = no change.
    if cfg["model"].get("decoder_init"):
        logger.info("Decoder initialised from %s", load_decoder_init(model, cfg["model"]["decoder_init"]))
    n_params = sum(p.numel() for p in model.parameters())
    print(f"Model {cfg['model']['name']}: {n_params:,} parameters", flush=True)
    logger.info("Model %s: %s parameters", cfg["model"]["name"], f"{n_params:,}")

    # ---- Losses (BenchmarkEL: class weights from the labelled subset in use, train only) ----
    class_counts = data.pop("class_counts")
    losses = {k: v.to(device) for k, v in build_losses(cfg["loss"], class_counts).items()}
    w = losses["supervised"].criterion.weight
    weights = w.tolist() if w is not None else None
    logger.info("CE class weights: %s", [round(x, 3) for x in weights] if weights else "none (plain CE)")
    if data["info"].get("zero_pixel_classes") is not None:
        logger.info("Zero-pixel classes in labelled subset (weight 0): %s", data["info"]["zero_pixel_classes"] or "none")

    trainer_cls, extra_kw = Trainer, {}
    if method == "alhvr":
        trainer_cls = ALHVRTrainer
        extra_kw = dict(model_b=model_b, optimizer_b=build_optimizer(model_b, cfg))
    trainer = trainer_cls(
        **extra_kw,
        model=model,
        optimizer=build_optimizer(model, cfg),
        losses=losses,
        labeled_loader=data["labeled_loader"],
        unlabeled_loader=data["unlabeled_loader"],
        val_loader=data["val_loader"],
        test_loader=data["test_loader"],
        cfg=cfg,
        device=device,
        run_dir=run_dir,
        class_counts=class_counts,  # SK1 absh keep probabilities (labelled cells only)
        extra_info={
            "method": method,
            "dataset": dataset,
            "seed": seed,
            **data["info"],
            "class_weights": weights,
            "deterministic": t_cfg.get("deterministic", True),
        },
    )
    trainer.metric_kw = data["metric_kw"]
    # ``cp`` (opt-in, F2 / CP5; not in base.yaml): copy-paste stream (stream id 3) with weight cp.lambda. Built
    # whenever the section exists (library and lists are checked), iterated only when cp.lambda > 0.
    if cfg.get("cp"):
        if dataset != "benchmark_el" or method != "supervised":
            raise ValueError("cp is implemented for supervised BenchmarkEL runs only")
        from src.data.copy_paste import build_cp_stream
        trainer.cp_loader, cp_records, cp_sum = build_cp_stream(cfg, data["info"], seed, nw,
                                                                device.type == "cuda")
        trainer.cp_lambda = float(cfg["cp"].get("lambda", 1.0))
        logger.info("CP: lambda %s  %s", trainer.cp_lambda, cp_sum)
        with open(run_dir / "cp_library.json", "w") as f:
            json.dump({"summary": cp_sum, "components": cp_records}, f, indent=1)
    trainer.exit_after_step = args.exit_after_step
    trainer.fit(resume_from=latest if args.resume else None)


def build_benchmark_data(cfg: dict, method: str, seed: int, frac: float, is_ssl: bool,
                         device: torch.device, nw: int) -> dict:
    """BenchmarkELimages streams and loaders (official split, committed labelled subsets)."""
    d_cfg, t_cfg = cfg["data"], cfg["training"]
    root = Path(d_cfg["root"])
    splits = root / "splits"
    # ``data.mask_subdir`` (opt-in, not in base.yaml so older run configs stay resumable): e.g. labeled/masks_escdd
    # for the E-SCDD revised labels (P6). Train, val, test and the class weights all use the same mask set.
    img_dir, msk_dir = root / "labeled" / "images", root / d_cfg.get("mask_subdir", "labeled/masks_coded")
    # ``data.split_seed`` picks the labelled subset (data/splits/seed<k>/); it defaults to the
    # training seed, so "seed=1 data.split_seed=0" changes the training seed only.
    split_seed = int(d_cfg.get("split_seed", seed))
    # ``data.labeled_list`` (opt-in, Track D labelled-set experiment; not in base.yaml so older run configs stay
    # resumable): an explicit file of labelled train stems replaces data/splits/seed<k>/labeled_<P>pct.txt, in the
    # file's order. The in-domain pool is then the rest of train.txt, in train.txt order. Unset: unchanged.
    labeled_list = d_cfg.get("labeled_list")
    if labeled_list:
        if frac >= 1.0:
            raise ValueError("data.labeled_list needs data.labeled_fraction < 1")
        labeled_file, unlabeled_file = Path(labeled_list), None
    elif frac >= 1.0:
        labeled_file, unlabeled_file = splits / "train.txt", None
    else:
        labeled_file = splits / f"seed{split_seed}" / f"labeled_{frac_tag(frac)}.txt"
        unlabeled_file = splits / f"seed{split_seed}" / f"unlabeled_{frac_tag(frac)}.txt"
    labeled_stems = load_split(labeled_file)
    train_list = load_split(splits / "train.txt")
    train_stems = set(train_list)
    val_stems, test_stems = load_split(splits / "val.txt"), load_split(splits / "test.txt")
    if not set(labeled_stems) <= train_stems:
        raise ValueError(f"{labeled_file} contains non-train images")
    if len(set(labeled_stems)) != len(labeled_stems):
        raise ValueError(f"{labeled_file} contains duplicate stems")
    if labeled_list:
        lab_set = set(labeled_stems)
        unlabeled_stems = [s_ for s_ in train_list if s_ not in lab_set] if is_ssl else []
    else:
        unlabeled_stems = load_split(unlabeled_file) if is_ssl else []
    # ``data.unlabeled_pool: external`` (opt-in, not in base.yaml so older run configs stay resumable): the SSL
    # unlabelled set is the external pool (scripts/prepare_external_pool.py) instead of the rest of train.
    pool = d_cfg.get("unlabeled_pool", "split")
    unl_img_dir = img_dir
    if pool == "external":
        if method != "mean_teacher":
            raise ValueError("data.unlabeled_pool=external is implemented for mean_teacher only")
        unlabeled_file = Path(d_cfg.get("external_manifest", "data/splits/external_unlabeled.txt"))
        unl_img_dir = Path(d_cfg.get("external_dir", "data/unlabeled/images_512"))
        unlabeled_stems = load_split(unlabeled_file)
        clash = set(unlabeled_stems) & (train_stems | set(val_stems) | set(test_stems))
        if clash:
            raise ValueError(f"{unlabeled_file}: {len(clash)} stems are labelled train / val / test images")
    elif pool != "split":
        raise ValueError(f"unknown data.unlabeled_pool {pool!r} (split | external)")
    # ``data.unlabeled_exclude`` (opt-in, SK1 / data decision D7): a file of stems dropped from the in-domain pool
    # (train twins of test cells). Every listed stem must be a train cell and none may be labelled.
    excl_file = d_cfg.get("unlabeled_exclude")
    if excl_file and is_ssl:
        if pool != "split":
            raise ValueError("data.unlabeled_exclude is for the in-domain pool (data.unlabeled_pool=split)")
        excl = set(load_split(Path(excl_file)))
        if not excl <= train_stems or excl & set(labeled_stems):
            raise ValueError(f"{excl_file}: stems must be unlabelled train cells")
        n0 = len(unlabeled_stems)
        unlabeled_stems = [s_ for s_ in unlabeled_stems if s_ not in excl]
        logger.info("unlabeled_exclude %s: dropped %d of %d pool cells", excl_file, n0 - len(unlabeled_stems), n0)
    logger.info("Labelled: %d (%s)  unlabelled: %d (%s)  val: %d  test: %d", len(labeled_stems), labeled_file,
                len(unlabeled_stems), unlabeled_file if is_ssl else "-", len(val_stems), len(test_stems))

    size, mean, std = d_cfg["input_size"], d_cfg.get("mean", [0.5]), d_cfg.get("std", [0.25])
    lbs, ubs = t_cfg["labeled_batch_size"], t_cfg["unlabeled_batch_size"]
    stream_kw = dict(seed=seed, num_workers=nw, pin_memory=device.type == "cuda")

    unlabeled_loader = None
    if method == "mean_teacher":
        if d_cfg.get("augmentation", "strong") == "labelsafe":
            geo, strong = get_labelsafe_geometric(size), get_labelsafe_strong_photometric(mean, std)
        else:
            geo, strong = get_geometric_augmentation(size), get_strong_photometric(mean, std)
        weak = get_weak_photometric(mean, std)
        # ``ssl.labeled_aug: supervised`` (opt-in, P11): labelled images get the supervised arm's pipeline instead of
        # the SSL two-view pipeline; implemented for the label-safe recipe only.
        lab_aug = cfg.get("ssl", {}).get("labeled_aug", "twoview")
        if lab_aug == "supervised":
            if d_cfg.get("augmentation", "strong") != "labelsafe":
                raise ValueError("ssl.labeled_aug=supervised is implemented for data.augmentation=labelsafe only")
            if cfg["ssl"].get("consistency_on_labeled", False):
                raise ValueError("ssl.labeled_aug=supervised needs consistency on unlabelled images only")
            labeled_ds = SupervisedViewDataset(
                BenchmarkELDataset(img_dir, msk_dir, labeled_stems, get_labelsafe_augmentation(size, mean, std)))
        elif lab_aug == "twoview":
            labeled_ds = TwoViewDataset(BenchmarkELDataset(img_dir, msk_dir, labeled_stems, return_raw=True), geo, strong, weak)
        else:
            raise ValueError(f"unknown ssl.labeled_aug {lab_aug!r} (twoview | supervised)")
        unl_ds = TwoViewDataset(BenchmarkELDataset(unl_img_dir, None, unlabeled_stems, return_raw=True), geo, strong, weak)
        labeled_loader = BatchStream(labeled_ds, lbs, stream_id=0, **stream_kw)
        unlabeled_loader = BatchStream(unl_ds, ubs, stream_id=1, **stream_kw)
    elif method in ("supervised", "alhvr"):
        # supervised and ALHVR: one augmented view per image (ALHVR feeds the
        # same view to both networks, as in the reference).
        aug_name = d_cfg.get("augmentation", "strong")
        if aug_name == "strong":
            strong_aug = get_strong_augmentation(size, mean, std)
        elif aug_name == "flips":
            if method != "supervised":
                raise ValueError("data.augmentation=flips is for supervised runs")
            strong_aug = get_flip_augmentation(size, mean, std)
        elif aug_name == "labelsafe":
            if method != "supervised":
                raise ValueError("data.augmentation=labelsafe is for supervised runs")
            strong_aug = get_labelsafe_augmentation(size, mean, std)
        else:
            raise ValueError(f"unknown data.augmentation {aug_name!r} (strong | flips | labelsafe)")
        # ``data.mask_ignore_value`` (Track M R4, opt-in, not in base.yaml): labelled train masks may hold this value
        # (255 = pixels of classes outside the 24-class taxonomy); the supervised losses ignore it (ignore_index 255).
        # Val/test masks stay strict. Supervised runs only.
        ign = d_cfg.get("mask_ignore_value")
        if ign is not None and method != "supervised":
            raise ValueError("data.mask_ignore_value is implemented for supervised runs only")
        labeled_ds = BenchmarkELDataset(img_dir, msk_dir, labeled_stems, strong_aug, ignore_value=ign)
        labeled_loader = BatchStream(labeled_ds, lbs, stream_id=0, **stream_kw)
        if method == "alhvr":
            # Unlabelled images keep their masks only as ``hidden_mask`` for
            # region diagnostics (augmented jointly so they stay aligned); the
            # trainer never passes them to a loss.  Own augmentation instance,
            # so the two streams never share transform objects.
            unl_ds = HiddenMaskDataset(BenchmarkELDataset(img_dir, msk_dir, unlabeled_stems,
                                                          get_strong_augmentation(size, mean, std)))
            unlabeled_loader = BatchStream(unl_ds, ubs, stream_id=1, **stream_kw)
    else:
        raise ValueError(f"method {method!r} is not available on BenchmarkEL")

    weak_eval = get_weak_augmentation(mean, std, size)
    eval_kw = dict(batch_size=t_cfg.get("eval_batch_size", 8), shuffle=False, num_workers=nw,
                   pin_memory=device.type == "cuda", generator=torch.Generator().manual_seed(seed))
    class_counts = count_class_pixels(msk_dir, labeled_stems, d_cfg.get("mask_ignore_value"))
    return {
        "labeled_loader": labeled_loader,
        "unlabeled_loader": unlabeled_loader,
        "val_loader": DataLoader(BenchmarkELDataset(img_dir, msk_dir, val_stems, weak_eval), **eval_kw),
        "test_loader": DataLoader(BenchmarkELDataset(img_dir, msk_dir, test_stems, weak_eval), **eval_kw),
        "class_counts": class_counts,
        "metric_kw": {},
        "info": {
            "labeled_fraction": frac,
            "split_seed": split_seed,
            "labeled_split": str(labeled_file),
            "n_labeled": len(labeled_stems),
            "n_unlabeled": len(unlabeled_stems),
            "unlabeled_pool": pool if is_ssl else None,
            "zero_pixel_classes": [CLASS_INFO[i]["name"] for i, c in enumerate(class_counts) if c == 0],
        },
    }


def build_ucf_data(cfg: dict, method: str, seed: int, device: torch.device, nw: int) -> dict:
    """UCF-EL streams and loaders: committed split files, Fioresi transforms, no val (test at the final step)."""
    d_cfg, t_cfg = cfg["data"], cfg["training"]
    root, splits = Path(d_cfg["root"]), Path(d_cfg["splits"])
    split_seed = int(d_cfg.get("split_seed", 0))
    subset = d_cfg["labeled_subset"]
    if subset == "full":
        labeled_file, unlabeled_file = splits / "train.txt", None
    elif subset == "sl20":
        labeled_file = splits / f"sl20_seed{split_seed}.txt"
        unlabeled_file = splits / f"unlabeled_sl20_seed{split_seed}.txt"
    else:
        raise ValueError(f"unknown data.labeled_subset {subset!r} (sl20 | full)")
    labeled = load_split(labeled_file)
    train_names = set(load_split(splits / "train.txt"))
    test_names = load_split(splits / "test.txt")
    if not set(labeled) <= train_names:
        raise ValueError(f"{labeled_file} contains non-train images")
    unlabeled = []
    if method == "pvs3":
        if unlabeled_file is None:
            raise ValueError("pvs3 needs data.labeled_subset=sl20 (the unlabelled pool is the rest of train)")
        unlabeled = load_split(unlabeled_file)
        if set(unlabeled) & set(labeled) or not set(unlabeled) <= train_names:
            raise ValueError(f"{unlabeled_file} overlaps the labelled subset or contains non-train images")
    logger.info("UCF-EL labelled: %d (%s)  unlabelled: %d  test: %d  (no val: test at the final step only)",
                len(labeled), labeled_file, len(unlabeled), len(test_names))

    resize, crop = int(d_cfg.get("resize_size", 295)), int(d_cfg["input_size"])
    geo_kw = dict(random_rescale=d_cfg.get("random_rescale"), rot90=bool(d_cfg.get("rot90", False)))
    lbs, ubs = t_cfg["labeled_batch_size"], t_cfg["unlabeled_batch_size"]
    stream_kw = dict(seed=seed, num_workers=nw, pin_memory=device.type == "cuda")
    unlabeled_loader = None
    if method == "supervised":
        labeled_ds = UCFELDataset(root, "train", labeled,
                                  get_ucf_train_transform(resize, crop, **geo_kw, photometric=d_cfg.get("photometric")))
    elif method == "pvs3":
        if d_cfg.get("photometric"):
            raise ValueError("data.photometric is for supervised runs; PV-S3 uses data.strong_aug")
        sv = d_cfg.get("strong_aug") or "v1"
        geo, strong, weak = get_ucf_geometric(resize, crop, **geo_kw), get_ucf_strong_photometric(sv), get_ucf_weak_photometric()
        labeled_ds = TwoViewDataset(UCFELDataset(root, "train", labeled, return_raw=True), geo, strong, weak)
        # Masks hidden: the unlabelled dataset never opens a mask file.
        unl_ds = TwoViewDataset(UCFELDataset(root, "train", unlabeled, labeled=False, return_raw=True),
                                get_ucf_geometric(resize, crop, **geo_kw), get_ucf_strong_photometric(sv), get_ucf_weak_photometric())
        unlabeled_loader = BatchStream(unl_ds, ubs, stream_id=1, **stream_kw)
    else:
        raise ValueError(f"method {method!r} is not available on UCF-EL (supervised | pvs3)")
    labeled_loader = BatchStream(labeled_ds, lbs, stream_id=0, **stream_kw)
    test_loader = DataLoader(UCFELDataset(root, "test", test_names, get_ucf_eval_transform(resize)),
                             batch_size=1, shuffle=False, num_workers=nw, pin_memory=device.type == "cuda",
                             generator=torch.Generator().manual_seed(seed))
    return {
        "labeled_loader": labeled_loader,
        "unlabeled_loader": unlabeled_loader,
        "val_loader": None,
        "test_loader": test_loader,
        # labelled-GT class pixel counts, needed only by the per-class-threshold pseudo-label loss
        "class_counts": (count_ucf_class_pixels(root, labeled)
                         if cfg["loss"].get("consistency") == "class_threshold_ce" else None),
        "metric_kw": UCF_METRIC_KW,
        "info": {
            "labeled_subset": subset,
            "split_seed": split_seed,
            "labeled_split": str(labeled_file),
            "n_labeled": len(labeled),
            "n_unlabeled": len(unlabeled),
            "n_test": len(test_names),
            "epochs_equivalent": cfg["training"]["total_steps"] * lbs / len(labeled),
        },
    }


if __name__ == "__main__":
    main()
