"""Iteration-based trainer for supervised and Mean Teacher SSL runs.

Training length is ``training.total_steps`` optimizer steps in both modes, so
supervised and SSL runs match by construction.  Batches come from
``BatchStream``s (``src/data/stream.py``): one batch per stream per step, and
the batch at step ``s`` is a pure function of (seed, s).

Every ``training.val_every`` steps (and at the last step) the model is
evaluated on val; the checkpoint with the best val ``defect_miou`` is kept.
After training, test is evaluated on the final weights and on the best-val
checkpoint.  Without a val loader (``val_loader=None``) there is no
validation and no checkpoint selection: test is evaluated at the final step
only.

Checkpoints (``run_dir/checkpoints``): ``best.pth`` (eval weights at the best
val step) and ``latest.pth`` (full training state every
``training.checkpoint_every`` steps and at the last step: model(s),
optimizer(s), scheduler(s), grad scaler, every RNG, EMA weights, step and the
trainer's own bookkeeping).  ``fit(resume_from=latest.pth)`` continues an
interrupted run exactly where ``latest.pth`` was written.

Mixed precision: ``training.amp`` with ``training.amp_dtype`` (default
bfloat16; fp16 gave NaN in DeepLabV3+).  The grad scaler is only active for
float16 but is checkpointed either way.

Batch protocol: ``training.labeled_batch_size`` labelled images per step in
every method; SSL methods add ``training.unlabeled_batch_size`` unlabelled
images.  The supervised loss is the same in every method.

SSL mode (``method: mean_teacher`` / ``pvs3``): each step draws a labelled batch and an unlabelled
batch.  The student sees the strong view of the unlabelled images and, for the
supervised loss, the ``ssl.labeled_view`` view of the labelled images; the EMA
teacher sees the weak views (shared geometry).  Supervised CE on the labelled part, SemiCE consistency on
the unlabelled part (``ssl.consistency_on_labeled`` adds the labelled part),
weighted by λ(step): 0 for ``ssl.warmup_steps``, then a linear
ramp over ``ssl.ramp_steps`` to ``ssl.lambda_final``.  Validation and test use
the teacher.
"""

from __future__ import annotations

import json
import logging
import math
import os
import time
from pathlib import Path
from typing import Any, Iterator

import torch
import torch.nn as nn
from torch.utils.data import DataLoader

from .ema import EMAUpdater
from .ssl_ops import cutmix_boxes, frozen_bn_stats, mix_with_next
from . import absh as absh_ops
from ..data.stream import mix_seed
from ..losses.confidence_ce import ConfidenceCELoss
from ..evaluation.evaluator import argmax_rule, bg_threshold_rule, evaluate_model
from ..evaluation.metrics import format_table, scalar_metrics
from ..utils.checkpoint import atomic_save, load_checkpoint, rng_state, set_rng_state, to_cpu

logger = logging.getLogger(__name__)

AMP_DTYPES = {"bfloat16": torch.bfloat16, "float16": torch.float16}
# Config keys that may differ between the run that wrote latest.pth and the one resuming it.
RESUME_MUTABLE_KEYS = {("training", "num_workers"), ("training", "eval_batch_size")}


def consistency_weight(step: int, warmup_steps: int, ramp_steps: int, lambda_final: float) -> float:
    """λ for the given 0-based step: 0 during warmup, then a linear ramp."""
    if step < warmup_steps:
        return 0.0
    return min((step - warmup_steps + 1) / max(ramp_steps, 1), 1.0) * lambda_final


def sigmoid_rampup_weight(step: int, ramp_steps: int, lambda_final: float) -> float:
    """λ for the 0-based step with the Mean Teacher ramp-up ``exp(-5 (1 - t)^2)``, t = (step+1)/ramp_steps clipped to 1."""
    if ramp_steps <= 0:
        return lambda_final
    t = min((step + 1) / ramp_steps, 1.0)
    return lambda_final * math.exp(-5.0 * (1.0 - t) ** 2)


def build_lr_lambda(total_steps: int, warmup_steps: int, schedule: str, power: float = 0.9):
    """Per-step LR multiplier.

    ``cosine``: linear warmup, then cosine to 0.  ``constant``: warmup, then 1.
    ``poly``: ``(1 - step/total_steps) ** power`` from step 0 (no warmup), as in
    the UCF-EL / torchvision reference.
    """
    if schedule == "poly":
        if warmup_steps:
            raise ValueError("poly schedule has no warmup")
        return lambda step: max(1.0 - step / total_steps, 0.0) ** power

    def f(step: int) -> float:
        if step < warmup_steps:
            return (step + 1) / warmup_steps
        if schedule == "cosine":
            progress = (step - warmup_steps) / max(total_steps - warmup_steps, 1)
            return 0.5 * (1.0 + math.cos(math.pi * min(progress, 1.0)))
        if schedule == "constant":
            return 1.0
        raise ValueError(f"unknown lr_scheduler {schedule!r}")
    return f


def build_pf_lr_lambda(base, pf: dict):
    """F3 (opt-in ``training.encoder_pf``): encoder-group multiplier = base x (0 for steps < ``freeze``, then a linear ramp
    over ``ramp`` steps to 1; ramp 0 = no ramp). The group's lr (base lr x ``lr_mult``) and weight decay are set by
    ``build_optimizer`` in scripts/train.py. Neutral (freeze 0, ramp 0) returns exactly ``base(step)``."""
    fr, rp = int(pf.get("freeze", 1000)), int(pf.get("ramp", 1000))

    def g(step: int) -> float:
        if step < fr:
            return 0.0
        return base(step) * (min((step - fr + 1) / rp, 1.0) if rp > 0 else 1.0)
    return g


def build_lr_lambdas(t: dict, total_steps: int):
    """The scheduler's lr multiplier(s): the house lambda, or [house, encoder PF] with ``training.encoder_pf`` (F3)."""
    base = build_lr_lambda(total_steps, int(t.get("warmup_steps", 0)), t.get("lr_scheduler", "cosine"),
                           float(t.get("poly_power", 0.9)))
    pf = t.get("encoder_pf")
    return [base, build_pf_lr_lambda(base, pf)] if pf else base


def _nan_to_none(obj: Any) -> Any:
    if isinstance(obj, float) and math.isnan(obj):
        return None
    if isinstance(obj, dict):
        return {k: _nan_to_none(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_nan_to_none(v) for v in obj]
    return obj


def _better(new: float, best: float) -> bool:
    """NaN-safe comparison: NaN never counts as an improvement."""
    return not math.isnan(new) and (math.isnan(best) or new > best)


def _config_diff(a: Any, b: Any, path: tuple = ()) -> list[str]:
    if isinstance(a, dict) and isinstance(b, dict):
        out = []
        for k in sorted(set(a) | set(b), key=str):
            if path + (k,) in RESUME_MUTABLE_KEYS:
                continue
            out += _config_diff(a.get(k, "<missing>"), b.get(k, "<missing>"), path + (k,))
        return out
    if a == b:
        return []
    # A key added to the configs later with an "off" default (None / False) does not change the run.
    if (a == "<missing>" and b in (None, False)) or (b == "<missing>" and a in (None, False)):
        return []
    return [f"{'.'.join(map(str, path))}: {a!r} -> {b!r}"]


class _EncoderDecoder(nn.Module):
    """An smp model's encoder with another decoder and head (shared modules, no copies)."""

    def __init__(self, encoder: nn.Module, decoder: nn.Module, head: nn.Module) -> None:
        super().__init__()
        self.encoder, self.decoder, self.head = encoder, decoder, head

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.head(self.decoder(self.encoder(x)))


class Trainer:
    """Train for a fixed number of optimizer steps, validate, then test.

    Args:
        model:            Student / supervised model (on ``device``).
        optimizer:        Optimizer over ``model``'s parameters.
        losses:           ``{'supervised': ..., 'consistency': ...}``.
        labeled_loader:   ``BatchStream`` (``iterate(start_batch)``).
                          Supervised mode: ``{'image', 'mask'}`` batches.
                          SSL mode: ``{'image_strong', 'image_weak', 'mask'}``.
        val_loader:       Labelled val loader (weak transform), or ``None``
                          for no validation / no checkpoint selection.
        test_loader:      Labelled test loader (weak transform).
        cfg:              Full experiment config.
        device:           Torch device.
        run_dir:          ``experiments/<run_name>``; checkpoints go to
                          ``run_dir/checkpoints``.
        unlabeled_loader: SSL mode only: ``BatchStream`` of ``{'image_strong', 'image_weak'}``.
        extra_info:       Extra entries for metrics.json (e.g. split sizes).
    """

    def __init__(
        self,
        model: nn.Module,
        optimizer: torch.optim.Optimizer,
        losses: dict[str, nn.Module],
        labeled_loader: Any,
        val_loader: DataLoader | None,
        test_loader: DataLoader,
        cfg: dict[str, Any],
        device: torch.device,
        run_dir: Path,
        unlabeled_loader: Any | None = None,
        extra_info: dict[str, Any] | None = None,
        class_counts: Any | None = None,
    ) -> None:
        self.model = model
        self.optimizer = optimizer
        self.sup_criterion = losses["supervised"]
        self.con_criterion = losses.get("consistency")
        self.labeled_loader = labeled_loader
        self.unlabeled_loader = unlabeled_loader
        self.val_loader = val_loader
        self.test_loader = test_loader
        self.cfg = cfg
        self.device = device
        self.run_dir = Path(run_dir)
        self.ckpt_dir = self.run_dir / "checkpoints"
        self.ckpt_dir.mkdir(parents=True, exist_ok=True)
        self.extra_info = extra_info or {}

        t = cfg["training"]
        self.total_steps = int(t["total_steps"])
        self.val_every = int(t.get("val_every", 500))
        self.log_every = int(t.get("log_every", 50))
        self.ckpt_every = int(t.get("checkpoint_every", 2000))
        self.grad_clip = t.get("gradient_clip", 1.0)
        # Track M (opt-in, logging only): log the pre-clip global grad norm of the model and whether clipping bound.
        # Off by default; on, it reads the value clip_grad_norm_ already returns, so the update is unchanged.
        self.log_grad_norm = bool(t.get("log_grad_norm", False))
        self._gn = float("nan")
        self.amp = bool(t.get("amp", True)) and device.type == "cuda"
        self.amp_dtype = AMP_DTYPES[t.get("amp_dtype", "bfloat16")]
        self.scaler = torch.amp.GradScaler(device.type, enabled=self.amp and self.amp_dtype == torch.float16)
        # F3 (opt-in ``training.encoder_pf``): group 0 = decoder + head (house), group 1 = encoder (PF multiplier).
        self.encoder_pf = t.get("encoder_pf") or None
        if self.encoder_pf and len(optimizer.param_groups) != 2:
            raise ValueError("training.encoder_pf needs the 2-group optimizer built by build_optimizer")
        self.scheduler = torch.optim.lr_scheduler.LambdaLR(optimizer, build_lr_lambdas(t, self.total_steps))
        self.num_classes = cfg["model"]["num_classes"]
        # B3 (opt-in ``data.scuff_class``, spec_b3_scuff.md 3): the model has one extra scuff channel; every evaluation
        # maps a predicted scuff px to background before the 24-class metrics. None: evaluation unchanged.
        sc = cfg.get("data", {}).get("scuff_class")
        self.fold_classes = int(sc) if sc is not None else None
        # thin worktree (opt-in ``loss.skel_recall`` / ``loss.cldice``): ThinCrackLoss wraps the house loss; its terms go
        # on their own log line (the step line is unchanged) and Skeleton Recall reads the batch's ``skel_tube``.
        self.thin_on = hasattr(self.sup_criterion, "last_terms")
        self.thin_tube = bool(getattr(self.sup_criterion, "needs_tube", False))
        self._thin_window: list[dict[str, float]] = []
        self.exit_after_step: int | None = None  # test hook: hard-exit right after this step (simulated crash)
        # F2 CP (opt-in, set by train.py after construction): copy-paste stream and its weight; lambda 0 or no
        # stream = the plain step (no forward, no draw, no log keys).
        self.cp_loader: Any | None = None
        self.cp_lambda: float = 0.0
        self._cp_it: Iterator | None = None
        self._cp_out: dict | None = None
        self.metric_kw: dict[str, Any] = {}       # SegmentationMetrics settings for the dataset (set by train.py)
        # Secondary decision rules evaluated at the final test (e.g. UCF-EL's background threshold).
        self.bg_thresholds = [float(x) for x in cfg.get("evaluation", {}).get("bg_thresholds", [])]

        s = cfg.get("ssl", {})
        self.decouple = False
        self.method = cfg.get("method", "supervised")
        self.ssl = self.method in ("mean_teacher", "pvs3")
        if self.ssl:
            if unlabeled_loader is None or self.con_criterion is None:
                raise ValueError("SSL mode needs an unlabeled_loader and a consistency loss")
            import copy

            self.teacher = copy.deepcopy(model)
            for p in self.teacher.parameters():
                p.requires_grad_(False)
            self.ema = EMAUpdater(model, self.teacher, alpha=s["ema_alpha"])
            self.ssl_warmup = int(s.get("warmup_steps", 0))
            self.ssl_ramp = int(s["ramp_steps"])
            self.ramp_shape = s.get("ramp", "linear")  # linear (after warmup) | sigmoid (MT exp(-5(1-t)^2) from step 0)
            if self.ramp_shape not in ("linear", "sigmoid"):
                raise ValueError(f"unknown ssl.ramp {self.ramp_shape!r}")
            self.lambda_final = float(s["lambda_final"])
            self.consistency_on_labeled = bool(s.get("consistency_on_labeled", False))
            # Which view of the labelled images the student's supervised loss sees: "weak" (the
            # usual choice: the labelled branch gets the plain training augmentation) or "strong"
            # (the student's strong view; the pilots and ucf_pvs3_ssl20_s0).
            self.labeled_view = s.get("labeled_view", "strong")
            if self.labeled_view not in ("weak", "strong"):
                raise ValueError(f"ssl.labeled_view must be weak or strong, got {self.labeled_view!r}")
            # P13 switches (opt-in; the defaults keep the original step bit for bit). ``ssl.student_forward:
            # separate`` gives the student two forward passes, labelled then unlabelled, and the unlabelled pass leaves
            # the BN running statistics untouched: the supervised branch is then normalised exactly as in a supervised
            # run, and at λ = 0 the student *is* that run. ``ssl.cutmix_p``: CutMix on the unlabelled batch, the same
            # box on the student's strong view and on the teacher's logits (``ssl_ops``).
            self.student_forward = s.get("student_forward", "joint")
            if self.student_forward not in ("joint", "separate"):
                raise ValueError(f"ssl.student_forward must be joint or separate, got {self.student_forward!r}")
            self.cutmix_p = float(s.get("cutmix_p", 0.0))
            self.split_step = self.student_forward == "separate" or self.cutmix_p > 0
            if self.split_step and self.consistency_on_labeled:
                raise ValueError("ssl.student_forward=separate / ssl.cutmix_p need consistency on unlabelled images only")
            self.seed = int(cfg.get("seed", 0))
            # P17 switch (opt-in; off keeps the P13 step bit for bit). ``ssl.decouple_decoder``: SKCDF-style data-flow
            # decoupling (Zhang et al., CVPR 2025, Sec. 3.1). The unlabelled loss goes through a second decoder + head
            # (``decoder_u``) on the shared encoder, so the labelled decoder never sees a pseudo-label; ``decoder_u``
            # follows the labelled decoder by a parameter EMA after every step (their Eq. 6, ω = ``ssl.decouple_ema``)
            # and keeps its own BN statistics. Pseudo-labels still come from the EMA teacher (encoder + labelled
            # decoder), and validation / test still use the teacher. ``decoder_u`` has its own optimizer and scheduler
            # (same settings) and its own gradient clip.
            self.decouple = bool(s.get("decouple_decoder", False))
            if self.decouple:
                if self.student_forward != "separate":
                    raise ValueError("ssl.decouple_decoder needs ssl.student_forward=separate")
                if not all(hasattr(model, a) for a in ("encoder", "decoder", "segmentation_head")):
                    raise ValueError("ssl.decouple_decoder needs an smp model (encoder / decoder / segmentation_head)")
                self.decouple_ema = float(s.get("decouple_ema", 0.99))
                self.dec_u = nn.ModuleDict({"decoder": copy.deepcopy(model.decoder),
                                            "head": copy.deepcopy(model.segmentation_head)})
                self.optimizer_u = type(optimizer)(self.dec_u.parameters(), **optimizer.defaults)
                self.scheduler_u = torch.optim.lr_scheduler.LambdaLR(
                    self.optimizer_u,
                    build_lr_lambda(self.total_steps, int(t.get("warmup_steps", 0)), t.get("lr_scheduler", "cosine"),
                                    float(t.get("poly_power", 0.9))),
                )

        # SK1 switch (opt-in; off keeps the P17 step bit for bit). ``absh.enabled``: SKCDF's auxiliary balanced
        # segmentation head (Sec. 3.3), adapted (``absh.py``, SK1 design.md section 4). A second head on the labelled
        # decoder (and, in decoupled SSL, on ``decoder_u``) is trained on class-balanced pixels; the main heads follow
        # the balanced heads by a parameter EMA after every step, order H -> D -> H. Validation and test still use the
        # main head of the teacher (SSL) or the model (supervised).
        self.absh_on = bool((cfg.get("absh") or {}).get("enabled", False))
        if self.absh_on:
            import copy

            a = cfg["absh"]
            if self.method not in ("supervised", "mean_teacher"):
                raise ValueError("absh needs method supervised or mean_teacher")
            if self.ssl and not self.decouple:
                raise ValueError("absh in SSL needs ssl.decouple_decoder=true (SKCDF's H -> D -> H chain)")
            if not all(hasattr(model, x) for x in ("encoder", "decoder", "segmentation_head")):
                raise ValueError("absh needs an smp model (encoder / decoder / segmentation_head)")
            if class_counts is None:
                raise ValueError("absh needs the labelled class pixel counts")
            self.seed = int(cfg.get("seed", 0))
            self.absh_ref = tuple(int(c) for c in a.get("ref_classes", [14, 11]))
            self.absh_radius = int(a.get("band_radius", 2))
            self.absh_omega = float(a.get("head_ema", 0.99))
            self.absh_p = absh_ops.keep_probs(class_counts, self.absh_ref).to(device)
            self.absh_dice = (tuple(getattr(self.sup_criterion, "dice_classes", ())),
                              float(getattr(self.sup_criterion, "dice_weight", 0.0)))
            self.absh_ignore = int(getattr(self.sup_criterion, "ignore_index", -100))
            heads = {"aux_l": copy.deepcopy(model.segmentation_head)}
            if self.ssl:
                heads["aux_u"] = copy.deepcopy(model.segmentation_head)
            self.absh = nn.ModuleDict(heads)
            self.optimizer_a = type(optimizer)(self.absh.parameters(), **optimizer.defaults)
            self.scheduler_a = torch.optim.lr_scheduler.LambdaLR(
                self.optimizer_a,
                build_lr_lambda(self.total_steps, int(t.get("warmup_steps", 0)), t.get("lr_scheduler", "cosine"),
                                float(t.get("poly_power", 0.9))),
            )
            if self.ssl:
                self.absh_teacher = copy.deepcopy(self.absh["aux_l"])
                for p in self.absh_teacher.parameters():
                    p.requires_grad_(False)
                self.ema_a = EMAUpdater(self.absh["aux_l"], self.absh_teacher, alpha=s["ema_alpha"])
            self._absh_out: dict[str, Any] = {}
            logger.info("absh: ref %s band %d head_ema %.3f keep probs %s", self.absh_ref, self.absh_radius,
                        self.absh_omega, [round(float(x), 4) for x in self.absh_p])
        if self.thin_on and (self.method != "supervised" or self.absh_on):
            raise ValueError("loss.skel_recall / loss.cldice are implemented for method=supervised without absh")

        # Bookkeeping that is checkpointed in latest.pth.
        self.history: list[dict[str, Any]] = []
        self.train_curve: list[dict[str, float]] = []
        self.best: dict[str, Any] = {"step": None, "defect_miou": float("nan")}
        self.train_time = 0.0
        self.peak_alloc = 0.0
        self.peak_reserved = 0.0
        self.resumes: list[dict[str, Any]] = []
        self._best_cpu: dict[str, Any] | None = None  # CPU copy of best.pth's payload

        # Pseudo-label statistics (confidence-CE consistency, i.e. PV-S3): per-class counts of the
        # confident pseudo-label pixels, summed over each window of ``logging.pseudo_label_every``
        # steps and written to ``pseudo_labels.csv``.  Logging only; nothing here feeds a loss.
        self.pl_every = int(cfg.get("logging", {}).get("pseudo_label_every", 500))
        self._pl_counts: torch.Tensor | None = None
        self._pl_pixels = 0
        self._pl_csv = None
        if self.ssl and isinstance(self.con_criterion, ConfidenceCELoss) and self.pl_every > 0:
            from .alhvr_diagnostics import RegionCSV

            self._pl_csv = RegionCSV(self.run_dir / "pseudo_labels.csv")

    @property
    def eval_model(self) -> nn.Module:
        return self.teacher if self.ssl else self.model

    @property
    def mode_name(self) -> str:
        return {"mean_teacher": "ssl_mean_teacher", "pvs3": "ssl_pvs3"}.get(self.method, "supervised")

    def consistency_lambda(self, step: int) -> float:
        if self.ramp_shape == "sigmoid":
            return sigmoid_rampup_weight(step, self.ssl_ramp, self.lambda_final)
        return consistency_weight(step, self.ssl_warmup, self.ssl_ramp, self.lambda_final)

    def autocast(self):
        return torch.autocast(device_type=self.device.type, dtype=self.amp_dtype, enabled=self.amp)

    def evaluate(self, model: nn.Module, loader: DataLoader, criterion: nn.Module | None = None,
                 rules: dict | None = None) -> dict[str, Any]:
        if self.fold_classes is not None:  # B3: 25-channel model, 24-class metrics with scuff -> background
            return evaluate_model(model, loader, self.device, self.fold_classes, amp=self.amp, criterion=criterion,
                                  amp_dtype=self.amp_dtype, metric_kw=self.metric_kw, rules=rules,
                                  fold_to_bg=self.fold_classes)
        return evaluate_model(model, loader, self.device, self.num_classes, amp=self.amp, criterion=criterion,
                              amp_dtype=self.amp_dtype, metric_kw=self.metric_kw, rules=rules)

    # ---- checkpointed components; method-specific trainers extend these ----
    def _models(self) -> dict[str, nn.Module]:
        models = {"model": self.model}
        if self.ssl:
            models["teacher"] = self.teacher  # the EMA weights
        if self.decouple:
            models["decoder_u"] = self.dec_u
        if self.absh_on:
            models["absh"] = self.absh
            if self.ssl:
                models["absh_teacher"] = self.absh_teacher
        return models

    def _optimizers(self) -> dict[str, torch.optim.Optimizer]:
        return {"model": self.optimizer, **({"decoder_u": self.optimizer_u} if self.decouple else {}),
                **({"absh": self.optimizer_a} if self.absh_on else {})}

    def _schedulers(self) -> dict[str, Any]:
        return {"model": self.scheduler, **({"decoder_u": self.scheduler_u} if self.decouple else {}),
                **({"absh": self.scheduler_a} if self.absh_on else {})}

    # ---- hooks overridden by method-specific trainers ----
    def _best_payload(self, step: int, val_scalars: dict) -> dict[str, Any]:
        """What best.pth holds."""
        return {"step": step, "model_state_dict": self.eval_model.state_dict(), "metrics": val_scalars}

    def _load_best(self, path: Path) -> None:
        load_checkpoint(path, self.eval_model, device=self.device)

    def _secondary_eval(self, loader: DataLoader) -> dict[str, Any] | None:
        """Optional second evaluation (e.g. a two-network ensemble); logged, never used for selection.

        Decoupled runs: student encoder + ``decoder_u`` (SKCDF's inference path), on test only.
        """
        if not self.decouple or loader is self.val_loader:
            return None
        return self.evaluate(_EncoderDecoder(self.model.encoder, self.dec_u["decoder"], self.dec_u["head"]), loader)

    def _on_step_end(self, done: int, out: dict[str, float]) -> None:
        """Called after every optimizer step (e.g. periodic diagnostics)."""

    def _on_resume(self, step: int) -> None:
        """Called after the training state has been restored (e.g. trim diagnostics written after ``step``)."""

    def _lr(self) -> float:
        return self.optimizer.param_groups[0]["lr"]

    # ------------------------------------------------------------------
    def _train_step(self, step: int, lab_it: Iterator, unl_it: Iterator | None) -> dict[str, float]:
        self.model.train()
        if self.decouple:
            self.dec_u.train()
        batch = next(lab_it)
        lam = 0.0
        with self.autocast():
            if not self.ssl:
                images = batch["image"].to(self.device, non_blocking=True)
                masks = batch["mask"].to(self.device, non_blocking=True)
                if self.absh_on:
                    feats = self.model.decoder(self.model.encoder(images))
                    main = self.model.segmentation_head(feats)
                    loss_sup = self.sup_criterion(main, masks)
                    self._absh_labelled(step, feats, masks, main)
                elif self.thin_tube:  # thin worktree: Skeleton Recall reads the precomputed tubed skeletons
                    loss_sup = self.sup_criterion(self.model(images), masks,
                                                  tube=batch["skel_tube"].to(self.device, non_blocking=True))
                else:
                    loss_sup = self.sup_criterion(self.model(images), masks)
                loss_con = torch.zeros((), device=self.device)
                if self._cp_it is not None:
                    self._cp_out = self._cp_loss(next(self._cp_it), masks)
            elif self.split_step:
                loss_sup, loss_con, lam = self._ssl_losses_split(step, batch, next(unl_it))
            else:
                ubatch = next(unl_it)
                n_l = batch["image_strong"].shape[0]
                lab_view = batch["image_weak"] if self.labeled_view == "weak" else batch["image_strong"]
                # student input: labelled images in ``labeled_view``, unlabelled images in the strong view
                strong = torch.cat([lab_view, ubatch["image_strong"]]).to(self.device, non_blocking=True)
                weak = torch.cat([batch["image_weak"], ubatch["image_weak"]]).to(self.device, non_blocking=True)
                masks = batch["mask"].to(self.device, non_blocking=True)
                student_logits = self.model(strong)
                # Consistency on the unlabelled part only (default), so that the
                # labelled images get exactly the supervised loss, as in every method.
                c0 = 0 if self.consistency_on_labeled else n_l
                with torch.no_grad():
                    self.teacher.eval()
                    teacher_logits = self.teacher(weak[c0:])
                loss_sup = self.sup_criterion(student_logits[:n_l], masks)
                lam = self.consistency_lambda(step)
                loss_con = (
                    self.con_criterion(student_logits[c0:].float(), teacher_logits.float())
                    if lam > 0 else torch.zeros((), device=self.device)
                )
            loss = loss_sup + lam * loss_con
            if self._cp_out is not None:
                loss = loss + self.cp_lambda * self._cp_out["loss_cp"]
            if self.absh_on:  # SKCDF Eq. 20: L_sup + L_sup^bal + λ (L_unsup + L_unsup^bal)
                loss = loss + self._absh_out["loss_aux_sup"] + lam * self._absh_out["loss_aux_con"]

        self.optimizer.zero_grad(set_to_none=True)
        if self.decouple:
            self.optimizer_u.zero_grad(set_to_none=True)
        self.scaler.scale(loss).backward()
        if self.grad_clip and self.grad_clip > 0:
            self.scaler.unscale_(self.optimizer)
            gn = torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.grad_clip)
            if self.log_grad_norm:
                self._gn = float(gn)
            if self.decouple:
                self.scaler.unscale_(self.optimizer_u)
                torch.nn.utils.clip_grad_norm_(self.dec_u.parameters(), self.grad_clip)
            if self.absh_on:
                self.scaler.unscale_(self.optimizer_a)
                torch.nn.utils.clip_grad_norm_(self.absh.parameters(), self.grad_clip)
        self.scaler.step(self.optimizer)
        if self.decouple:
            self.scaler.step(self.optimizer_u)
        if self.absh_on:
            self.scaler.step(self.optimizer_a)
        self.scaler.update()
        self.scheduler.step()
        if self.decouple:
            self.scheduler_u.step()
        if self.absh_on:
            self.scheduler_a.step()
            # H: labelled main head <- its balanced head (SKCDF code :220-225), before the teacher update
            absh_ops.ema_into(self.model.segmentation_head, self.absh["aux_l"], self.absh_omega)
        if self.ssl:
            self.ema.step()
            if self.absh_on:
                self.ema_a.step()
        if self.decouple:
            self._decouple_transfer()  # D (and, with absh, the final H)
        if self._pl_csv is not None and lam > 0 and self.con_criterion.last_class_counts is not None:
            c = self.con_criterion.last_class_counts.detach()
            self._pl_counts = c if self._pl_counts is None else self._pl_counts + c
            self._pl_pixels += self.con_criterion.last_num_pixels
        out = {"loss": loss.item(), "loss_sup": loss_sup.item(), "loss_con": loss_con.item(), "lambda": lam}
        if self.thin_on:  # thin worktree: own window and log line, so ``out`` (the step line) keeps its keys
            self._thin_window.append({k: float(v) for k, v in self.sup_criterion.last_terms.items()})
        if self._cp_out is not None:
            out.update({k: float(v) for k, v in self._cp_out.items()})
            self._cp_out = None
        if self.log_grad_norm:  # Track M: mean pre-clip grad norm and clip rate over each log window
            out["grad_norm"] = self._gn
            out["clipped"] = float(self._gn > float(self.grad_clip)) if self.grad_clip else 0.0
        if self.ssl and hasattr(self.con_criterion, "last_mask_fraction"):
            out["conf_frac"] = self.con_criterion.last_mask_fraction if lam > 0 else 0.0  # share of confident pixels
        if self.ssl and getattr(self.con_criterion, "exclude_classes", ()):  # SK2: share used after class exclusion
            out["used_frac"] = self.con_criterion.last_used_fraction if lam > 0 else 0.0
        if self.ssl and hasattr(self.con_criterion, "last_rare_fraction"):
            out["rare_frac"] = self.con_criterion.last_rare_fraction if lam > 0 else 0.0  # share with a rare-class target
        if self.absh_on:
            out.update({k: float(v.detach()) for k, v in self._absh_out.items()})
            self._absh_out = {}  # drop the graph references
        return out

    # ---- F2 CP: copy-paste stream loss ----
    def _cp_loss(self, cb: dict, masks: torch.Tensor) -> dict:
        """Separate forward of the pasted images with BN running statistics frozen (P13 mechanics); crack px:
        -log p14; ring px: -log(1 - p14) (log-sum-exp of the other classes); summed and divided by the number of
        valid labelled px, so a stream px weighs as one labelled px in the CE mean. fp32 losses."""
        img = cb["image"].to(self.device, non_blocking=True)
        tgt = cb["cp_target"].to(self.device, non_blocking=True)
        with frozen_bn_stats(self.model):
            logits = self.model(img)
        from src.data.copy_paste import cp_loss
        crack, ring = tgt == 1, tgt == 2
        n_lab = (masks != 255).sum().clamp(min=1).float()
        loss, p = cp_loss(logits, tgt, n_lab)
        with torch.no_grad():
            st = {"loss_cp": loss,
                  "cp_crack_px": crack.sum().float() / img.shape[0], "cp_ring_px": ring.sum().float() / img.shape[0],
                  "cp_p14_crack": p[crack].mean() if crack.any() else torch.zeros((), device=self.device),
                  "cp_p14_ring": p[ring].mean() if ring.any() else torch.zeros((), device=self.device),
                  "cp_fails": cb["cp_fails"].float().mean(), "cp_s": cb["cp_s"].float().mean(),
                  "cp_ring_med": cb["cp_ring_med"].float().mean()}
        return st

    # ---- SK1: auxiliary balanced head ----
    def _absh_labelled(self, step: int, feats: torch.Tensor, masks: torch.Tensor, main: torch.Tensor) -> None:
        """Balanced loss of the labelled aux head on decoder features ``feats`` (SKCDF Eq. 17, adapted)."""
        valid = masks != self.absh_ignore
        keep = absh_ops.balanced_keep(masks, self.absh_p, self.absh_ref, self.absh_radius, self.seed,
                                      absh_ops.STREAM_LAB, step, valid)
        loss = absh_ops.masked_ce_dice(self.absh["aux_l"](feats), masks, keep, *self.absh_dice)
        zero = torch.zeros((), device=self.device)
        with torch.no_grad():  # mechanism log (review_v1 item 3): does the H transfer move the evaluated head?
            drift = torch.sqrt(sum(((pm.float() - pa.float()) ** 2).sum() for pm, pa in
                                   zip(self.model.segmentation_head.parameters(), self.absh["aux_l"].parameters())))
            am, aa = main.detach().argmax(1), self.absh["aux_l"](feats.detach()).argmax(1)
        self._absh_out = {"loss_aux_sup": loss, "loss_aux_con": zero, "aux_keep_l": keep.float().mean(),
                          "aux_keep_u": zero, "aux_pl_crack": zero, "aux_pl_inactive": zero,
                          "head_drift": drift, "main_pred_crack": (am == 14).float().mean(),
                          "main_pred_inactive": (am == 11).float().mean(), "aux_pred_crack": (aa == 14).float().mean(),
                          "aux_pred_inactive": (aa == 11).float().mean(), "gt_crack": (masks == 14).float().mean(),
                          "gt_inactive": (masks == 11).float().mean()}

    def _absh_unlabelled(self, step: int, s_aux: torch.Tensor, t_aux: torch.Tensor) -> None:
        """Balanced loss of ``aux_u`` against the teacher aux head's confident argmax (SKCDF Eq. 18-19, adapted)."""
        with torch.no_grad():
            conf, pl = torch.softmax(t_aux.detach().float(), 1).max(1)
            confm = conf >= float(getattr(self.con_criterion, "t_pos", 0.0))
            pt = absh_ops.annealed(self.absh_p, step, self.total_steps)
            keep = absh_ops.balanced_keep(pl, pt, self.absh_ref, self.absh_radius, self.seed,
                                          absh_ops.STREAM_UNL, step, confm)
        self._absh_out["loss_aux_con"] = absh_ops.masked_ce(s_aux, pl, keep)
        self._absh_out["aux_keep_u"] = keep.float().mean()
        self._absh_out["aux_pl_crack"] = ((pl == 14) & confm).float().mean()
        self._absh_out["aux_pl_inactive"] = ((pl == 11) & confm).float().mean()

    @torch.no_grad()
    def _absh_eval(self, loader: DataLoader) -> dict[str, Any] | None:
        """Final-step test of the balanced heads (descriptive; never used for selection)."""
        if not self.absh_on:
            return None
        if not self.ssl:
            return {"model_aux": self.evaluate(_EncoderDecoder(self.model.encoder, self.model.decoder,
                                                               self.absh["aux_l"]), loader)}
        return {"teacher_aux": self.evaluate(_EncoderDecoder(self.teacher.encoder, self.teacher.decoder,
                                                             self.absh_teacher), loader),
                "decoder_u_aux": self.evaluate(_EncoderDecoder(self.model.encoder, self.dec_u["decoder"],
                                                               self.absh["aux_u"]), loader)}

    def _ssl_losses_split(self, step: int, batch: dict, ubatch: dict) -> tuple[torch.Tensor, torch.Tensor, float]:
        """Mean Teacher losses under the P13 switches (``student_forward`` / ``cutmix_p``); runs inside autocast."""
        lab_view = batch["image_weak"] if self.labeled_view == "weak" else batch["image_strong"]
        lab = lab_view.to(self.device, non_blocking=True)
        masks = batch["mask"].to(self.device, non_blocking=True)
        u_s = ubatch["image_strong"].to(self.device, non_blocking=True)
        lam = self.consistency_lambda(step)
        with torch.no_grad():
            self.teacher.eval()
            if self.absh_on:
                t_feats = self.teacher.decoder(self.teacher.encoder(ubatch["image_weak"].to(self.device, non_blocking=True)))
                t_logits, t_aux = self.teacher.segmentation_head(t_feats), self.absh_teacher(t_feats)
            else:
                t_logits = self.teacher(ubatch["image_weak"].to(self.device, non_blocking=True))
        if self.cutmix_p > 0:
            g = torch.Generator().manual_seed(mix_seed(self.seed, 2, step))  # boxes: a pure function of (seed, step)
            box = cutmix_boxes(u_s.shape[0], u_s.shape[-2], u_s.shape[-1], self.cutmix_p, g).to(self.device)
            u_s, t_logits = mix_with_next(u_s, box), mix_with_next(t_logits, box)
            if self.absh_on:
                t_aux = mix_with_next(t_aux, box)
        zero = torch.zeros((), device=self.device)
        if self.student_forward == "separate":
            if self.absh_on:
                feats = self.model.decoder(self.model.encoder(lab))
                main = self.model.segmentation_head(feats)
                loss_sup = self.sup_criterion(main, masks)
                self._absh_labelled(step, feats, masks, main)
            else:
                loss_sup = self.sup_criterion(self.model(lab), masks)
            if lam <= 0:
                return loss_sup, zero, lam
            with frozen_bn_stats(self.model):
                if self.decouple:  # shared encoder, then decoder_u (its BN statistics do update)
                    if self.absh_on:
                        u_feats = self.dec_u["decoder"](self.model.encoder(u_s))
                        s_unl = self.dec_u["head"](u_feats)
                        self._absh_unlabelled(step, self.absh["aux_u"](u_feats), t_aux)
                    else:
                        s_unl = self.dec_u["head"](self.dec_u["decoder"](self.model.encoder(u_s)))
                else:
                    s_unl = self.model(u_s)
            return loss_sup, self.con_criterion(s_unl.float(), t_logits.float()), lam
        n_l = lab.shape[0]
        logits = self.model(torch.cat([lab, u_s]))
        loss_sup = self.sup_criterion(logits[:n_l], masks)
        loss_con = self.con_criterion(logits[n_l:].float(), t_logits.float()) if lam > 0 else zero
        return loss_sup, loss_con, lam

    @torch.no_grad()
    def _decouple_transfer(self) -> None:
        """decoder_u ← ω · decoder_u + (1 − ω) · labelled decoder, parameters only (SKCDF Eq. 6)."""
        src = list(self.model.decoder.parameters()) + list(self.model.segmentation_head.parameters())
        dst = list(self.dec_u.parameters())
        assert len(src) == len(dst)
        for pu, pl in zip(dst, src):
            pu.mul_(self.decouple_ema).add_(pl, alpha=1.0 - self.decouple_ema)
        if self.absh_on:  # SKCDF transfers both heads with the decoder (:227-231), then main_u <- aux_u (:233-238)
            absh_ops.ema_into(self.absh["aux_u"], self.absh["aux_l"], self.decouple_ema)
            absh_ops.ema_into(self.dec_u["head"], self.absh["aux_u"], self.absh_omega)

    def _validate(self) -> dict[str, Any]:
        return self.evaluate(self.eval_model, self.val_loader, criterion=self.sup_criterion)

    def _write_metrics(self, payload: dict[str, Any]) -> None:
        with open(self.run_dir / "metrics.json", "w") as f:
            json.dump(_nan_to_none(payload), f, indent=1)

    # ---- training state (latest.pth) ----
    def _training_state(self, done: int) -> dict[str, Any]:
        return {
            "format": 1,
            "step": done,
            "cfg": self.cfg,
            "models": {k: m.state_dict() for k, m in self._models().items()},
            "optimizers": {k: o.state_dict() for k, o in self._optimizers().items()},
            "schedulers": {k: s.state_dict() for k, s in self._schedulers().items()},
            "scaler": self.scaler.state_dict(),
            "rng": rng_state(),
            "trainer": {
                "history": self.history,
                "train_curve": self.train_curve,
                "best": self.best,
                "train_time": self.train_time,
                "peak_alloc": self.peak_alloc,
                "peak_reserved": self.peak_reserved,
                "resumes": self.resumes,
            },
            "best_payload": self._best_cpu,
            # stateful consistency losses (per-class thresholds); the pseudo-label log window
            "consistency": self.con_criterion.state_dict() if self.con_criterion is not None else None,
            "pl_window": {"counts": None if self._pl_counts is None else self._pl_counts.cpu(),
                          "pixels": self._pl_pixels},
        }

    def save_latest(self, done: int) -> None:
        atomic_save(self._training_state(done), self.ckpt_dir / "latest.pth")
        logger.info("saved latest.pth at step %d", done)

    def load_training_state(self, path: Path) -> int:
        """Restore everything ``save_latest`` wrote; returns the step to continue from."""
        state = torch.load(path, map_location="cpu", weights_only=False)
        diff = _config_diff(state["cfg"], self.cfg)
        if diff:
            raise ValueError(f"{path}: config differs from the run being resumed:\n  " + "\n  ".join(diff))
        for kind, live in (("models", self._models()), ("optimizers", self._optimizers()),
                           ("schedulers", self._schedulers())):
            if set(state[kind]) != set(live):
                raise ValueError(f"{path}: {kind} {sorted(state[kind])} != {sorted(live)}")
            for k, obj in live.items():
                obj.load_state_dict(state[kind][k])
        self.scaler.load_state_dict(state["scaler"])
        tr = state["trainer"]
        self.history, self.train_curve, self.best = tr["history"], tr["train_curve"], tr["best"]
        self.train_time, self.resumes = tr["train_time"], tr["resumes"]
        self.peak_alloc, self.peak_reserved = tr["peak_alloc"], tr["peak_reserved"]
        self._best_cpu = state["best_payload"]
        if state.get("consistency") is not None and self.con_criterion is not None:
            self.con_criterion.load_state_dict(state["consistency"])
        if state.get("pl_window") is not None and self._pl_csv is not None:
            c = state["pl_window"]["counts"]
            self._pl_counts = None if c is None else c.to(self.device)
            self._pl_pixels = state["pl_window"]["pixels"]
        step = int(state["step"])

        # best.pth may have been overwritten after latest.pth was written (by
        # the run that died); put back the best weights as of ``step``.
        best_path = self.ckpt_dir / "best.pth"
        if self._best_cpu is not None:
            on_disk = torch.load(best_path, map_location="cpu", weights_only=False)["step"] if best_path.exists() else None
            if on_disk != self._best_cpu["step"]:
                atomic_save(self._best_cpu, best_path)
                logger.info("restored best.pth to step %s (found step %s on disk)", self._best_cpu["step"], on_disk)
        elif best_path.exists():
            best_path.unlink()
            logger.info("removed best.pth written after step %d by the interrupted run", step)

        self.resumes.append({"from_step": step, "at": time.strftime("%Y-%m-%d %H:%M:%S")})
        if self._pl_csv is not None:
            self._pl_csv.truncate_after(step)
        self._on_resume(step)
        set_rng_state(state["rng"])  # last: nothing after this may draw random numbers before the loop
        return step

    # ------------------------------------------------------------------
    def fit(self, resume_from: Path | None = None) -> dict[str, Any]:
        """Run (or continue) training, validation and the final test evaluation."""
        n_params = sum(p.numel() for p in self.model.parameters())
        start = 0
        if resume_from is not None:
            start = self.load_training_state(Path(resume_from))
            logger.info("RESUMED from %s at step %d/%d", resume_from, start, self.total_steps)
        logger.info("Mode: %s  total_steps=%d  val_every=%s  checkpoint_every=%d  amp=%s(%s)  params=%s",
                    self.mode_name, self.total_steps, self.val_every if self.val_loader is not None else "none",
                    self.ckpt_every, self.amp, str(self.amp_dtype).replace("torch.", ""), f"{n_params:,}")

        lab_it = self.labeled_loader.iterate(start)
        unl_it = self.unlabeled_loader.iterate(start) if self.unlabeled_loader is not None else None
        if self.cp_loader is not None and self.cp_lambda > 0:
            if self.ssl:
                raise ValueError("cp is implemented for supervised runs only")
            self._cp_it = self.cp_loader.iterate(start)
        if self.device.type == "cuda":
            torch.cuda.reset_peak_memory_stats(self.device)

        window: list[dict[str, float]] = []
        t_last = time.perf_counter()
        steps_this_segment = 0

        for step in range(start, self.total_steps):
            out = self._train_step(step, lab_it, unl_it)
            if not math.isfinite(out["loss"]):
                raise FloatingPointError(f"non-finite loss {out['loss']} at step {step + 1}")
            window.append(out)
            done = step + 1
            steps_this_segment += 1
            self._on_step_end(done, out)
            if self._pl_csv is not None and done % self.pl_every == 0 and self._pl_counts is not None:
                self._write_pseudo_labels(done)

            if done % self.log_every == 0 or done == self.total_steps:
                if self.device.type == "cuda":
                    torch.cuda.synchronize(self.device)
                now = time.perf_counter()
                self.train_time += now - t_last
                t_last = now
                avg = {k: sum(w[k] for w in window) / len(window) for k in window[0]}
                avg.update(step=done, lr=self._lr(), steps_per_sec=done / self.train_time)
                self.train_curve.append(avg)
                logger.info("step %d/%d  %s", done, self.total_steps,
                            "  ".join(f"{k}={v:.4g}" for k, v in avg.items() if k != "step"))
                if self.encoder_pf:  # F3: own line, so the step line (identity checks) is unchanged
                    logger.info("PF encoder lr=%.4g at step %d", self.optimizer.param_groups[1]["lr"], done)
                if self.thin_on and self._thin_window:  # thin worktree: own line (mean over the log window)
                    tw = self._thin_window
                    logger.info("thin %s at step %d", "  ".join(
                        f"{k}={sum(w[k] for w in tw) / len(tw):.4g}" for k in tw[0]), done)
                    self._thin_window = []
                window = []

            if self.val_loader is not None and (done % self.val_every == 0 or done == self.total_steps):
                if self.device.type == "cuda":
                    torch.cuda.synchronize(self.device)
                self.train_time += time.perf_counter() - t_last
                val = self._validate()
                sv = scalar_metrics(val)
                entry = {"step": done, **sv}
                secondary = self._secondary_eval(self.val_loader)
                if secondary is not None:
                    entry["secondary"] = scalar_metrics(secondary)
                    logger.info("val (secondary) @ step %d  defect_miou=%.4f", done, entry["secondary"]["defect_miou"])
                self.history.append(entry)
                logger.info("val @ step %d  defect_miou=%.4f  miou_defects_all=%.4f  miou_all=%.4f  "
                            "crack_recall=%.4f  crack_recall_relaxed=%.4f  crack_fpr_image=%.3f",
                            done, sv["defect_miou"], sv["miou_defects_all"], sv["miou_all"],
                            sv["crack_recall"], sv["crack_recall_relaxed"], sv["crack_fpr_image"])
                if _better(sv["defect_miou"], self.best["defect_miou"]):
                    self.best = {"step": done, "defect_miou": sv["defect_miou"], "val": val}
                    payload = self._best_payload(done, sv)
                    atomic_save(payload, self.ckpt_dir / "best.pth")
                    self._best_cpu = to_cpu(payload)
                    logger.info("new best val defect_miou=%.4f at step %d", sv["defect_miou"], done)
                t_last = time.perf_counter()

            if done % self.ckpt_every == 0 or done == self.total_steps:
                if self.device.type == "cuda":
                    self.peak_alloc = max(self.peak_alloc, torch.cuda.max_memory_allocated(self.device) / 2**30)
                    self.peak_reserved = max(self.peak_reserved, torch.cuda.max_memory_reserved(self.device) / 2**30)
                self.train_time += time.perf_counter() - t_last
                self.save_latest(done)
                t_last = time.perf_counter()

            if self.exit_after_step is not None and done == self.exit_after_step:
                logger.warning("exit_after_step=%d reached: hard exit (simulated crash)", done)
                logging.shutdown()
                os._exit(3)

        if self.device.type == "cuda":
            self.peak_alloc = max(self.peak_alloc, torch.cuda.max_memory_allocated(self.device) / 2**30)
            self.peak_reserved = max(self.peak_reserved, torch.cuda.max_memory_reserved(self.device) / 2**30)

        # ---- Test: final weights first, then the best-val checkpoint ----
        rules = {"argmax": argmax_rule, **{f"bg_threshold_{t:g}": bg_threshold_rule(t) for t in self.bg_thresholds}}
        by_rule = self.evaluate(self.eval_model, self.test_loader, rules=rules)
        test_final = by_rule.pop("argmax")
        test_final_secondary = self._secondary_eval(self.test_loader)
        test_final_absh = self._absh_eval(self.test_loader)  # before best.pth is loaded into the eval model
        logger.info("TEST (final weights, step %d)\n%s\n%s", self.total_steps, format_table(test_final),
                    format_table(test_final, convention="pvs3"))
        for name, res in by_rule.items():
            logger.info("TEST (final weights, step %d, decision rule %s)\n%s\n%s", self.total_steps, name,
                        format_table(res), format_table(res, convention="pvs3"))
        test = test_secondary = None
        if self.val_loader is not None:
            best_path = self.ckpt_dir / "best.pth"
            if best_path.exists():
                self._load_best(best_path)
                test_from = f"best.pth (step {self.best['step']})"
            else:
                logger.warning("No checkpoint ever improved val defect_miou (NaN throughout); testing final weights")
                test_from = "final weights (no best checkpoint)"
            test = self.evaluate(self.eval_model, self.test_loader)
            logger.info("TEST (%s)\n%s", test_from, format_table(test))
            test_secondary = self._secondary_eval(self.test_loader)

        payload = {
            "run_name": self.run_dir.name,
            "mode": self.mode_name,
            "model": self.cfg["model"]["name"],
            "n_params": n_params,
            "total_steps": self.total_steps,
            "optimizer_steps": self.total_steps,
            "resumes": self.resumes,
            "amp_dtype": str(self.amp_dtype).replace("torch.", "") if self.amp else "float32",
            **self.extra_info,
            "timing": {
                "train_seconds": self.train_time,
                "steps_per_sec": self.total_steps / self.train_time if self.train_time else None,
                "peak_gpu_mem_allocated_GiB": self.peak_alloc or None,
                "peak_gpu_mem_reserved_GiB": self.peak_reserved or None,
            },
            "train_curve": self.train_curve,
            "val_history": self.history,
            "best": {"step": self.best["step"], "val": self.best.get("val")},
            "test_final": {"step": self.total_steps, **test_final},
        }
        if test is not None:
            payload["test_best"] = {"step": self.best["step"], "evaluated_from": test_from, **test}
        if by_rule:
            payload["test_final_rules"] = {name: {"step": self.total_steps, **res} for name, res in by_rule.items()}
        if test_final_secondary is not None:
            payload["test_final_secondary"] = test_final_secondary
        if test_final_absh is not None:
            payload["test_final_absh"] = test_final_absh
        if test_secondary is not None:
            payload["test_best_secondary"] = test_secondary
        payload.update(self._extra_metrics())
        self._write_metrics(payload)
        return payload

    def _write_pseudo_labels(self, done: int) -> None:
        raw = self.con_criterion.update() if hasattr(self.con_criterion, "update") else None
        counts = self._pl_counts.cpu().tolist()
        conf = sum(counts)
        names = self.metric_kw.get("class_names") or [str(i) for i in range(len(counts))]
        row = {"step": done, "window_steps": self.pl_every, "unlabelled_pixels": self._pl_pixels,
               "confident_pixels": conf, "confident_frac": conf / max(self._pl_pixels, 1)}
        row.update({f"n_{n}": c for n, c in zip(names, counts)})
        row.update({f"share_{n}": c / max(conf, 1) for n, c in zip(names, counts)})
        row.update({f"unl_share_{n}": c / max(self._pl_pixels, 1) for n, c in zip(names, counts)})
        if raw is not None:  # per-class thresholds used in this window -> raw value from it -> EMA for the next
            thr = self.con_criterion.thresholds.cpu().tolist()
            row.update({f"raw_thr_{n}": r for n, r in zip(names, raw)})
            row.update({f"thr_{n}": t for n, t in zip(names, thr)})
            logger.info("pseudo-label thresholds @ step %d: %s", done, "  ".join(f"{n}={t:.3f}" for n, t in zip(names, thr)))
        self._pl_csv.write(row)
        logger.info("pseudo-labels @ step %d (last %d steps): confident %.4f; share %s", done, self.pl_every,
                    row["confident_frac"], "  ".join(f"{n}={row[f'share_{n}']:.4f}" for n in names))
        self._pl_counts, self._pl_pixels = None, 0

    def _extra_metrics(self) -> dict[str, Any]:
        """Extra metrics.json entries computed after training (e.g. secondary decision rules)."""
        return {}
