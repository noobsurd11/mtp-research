"""ALHVR trainer: two networks, two optimizers, no EMA.

Each step: 4 labelled + 4 unlabelled images (one augmented view, shared by both
networks).  Each network runs a main and a perturbed pass
(``forward_dual``).  Loss per network = the repo's supervised loss on the
labelled part + lambda(t) * (CG-CPCL + DTCT) on the unlabelled part
(``src/losses/alhvr.py``).  ``loss_a + loss_b`` is backpropagated jointly (as
in the reference), then each optimizer steps.

Network 1 (A) drives validation, the best checkpoint and test.  The
two-network ensemble (mean softmax) is logged as a secondary evaluation.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Iterator

import torch
import torch.nn as nn
from torch.utils.data import DataLoader

from .trainer import Trainer, build_lr_lambda
from ..losses.alhvr import ALHVRConfig, alhvr_unsup_losses, unsup_weight
from .alhvr_diagnostics import RegionCSV, region_diagnostics

logger = logging.getLogger(__name__)


class EnsembleModel(nn.Module):
    """Mean of two networks' softmax; returns log-probabilities (argmax = ensemble prediction)."""

    def __init__(self, a: nn.Module, b: nn.Module) -> None:
        super().__init__()
        self.a, self.b = a, b

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        p = (torch.softmax(self.a(x).float(), 1) + torch.softmax(self.b(x).float(), 1)) / 2
        return torch.log(p + 1e-12)


class ALHVRTrainer(Trainer):
    """See module docstring.  ``model``/``optimizer`` are network A; ``model_b``/``optimizer_b`` network B."""

    def __init__(self, *, model_b: nn.Module, optimizer_b: torch.optim.Optimizer, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        if self.unlabeled_loader is None:
            raise ValueError("ALHVR needs an unlabeled_loader")
        self.model_b = model_b
        self.optimizer_b = optimizer_b
        t = self.cfg["training"]
        self.scheduler_b = torch.optim.lr_scheduler.LambdaLR(
            optimizer_b,
            build_lr_lambda(self.total_steps, int(t.get("warmup_steps", 0)), t.get("lr_scheduler", "cosine")),
        )
        self.acfg = ALHVRConfig.from_dict(self.cfg.get("alhvr"))
        self.ensemble = EnsembleModel(self.model, self.model_b)
        self.diag_every = int(self.cfg.get("logging", {}).get("region_diag_every", 100))
        self.region_csv = RegionCSV(self.run_dir / "regions.csv")
        self._last_aux: dict[str, Any] | None = None

    @property
    def mode_name(self) -> str:
        return "alhvr"

    # ------------------------------------------------------------------
    def compute_losses(self, step: int, images: torch.Tensor, masks: torch.Tensor, n_l: int) -> dict[str, Any]:
        """Forward both networks on ``images`` (labelled first) and return all loss terms.

        ``masks`` are the labelled masks only.  Unlabelled images enter as
        pixels only, so no label of an unlabelled image can reach a loss.
        """
        layer = self.acfg.feature_layer
        with self.autocast():
            a1, a2, fa1, fa2 = self.model.forward_dual(images, layer)
            b1, b2, fb1, fb2 = self.model_b.forward_dual(images, layer)
            sup_a = self.sup_criterion(a1[:n_l], masks)
            sup_b = self.sup_criterion(b1[:n_l], masks)
        u = alhvr_unsup_losses(a1[n_l:], a2[n_l:], fa1[n_l:], fa2[n_l:],
                               b1[n_l:], b2[n_l:], fb1[n_l:], fb2[n_l:], self.acfg)
        lam = unsup_weight(step, self.total_steps, self.acfg.lambda_max)
        u["sup_a"], u["sup_b"] = sup_a.float(), sup_b.float()
        u["loss_a"] = u["sup_a"] + lam * u["unsup_a"]
        u["loss_b"] = u["sup_b"] + lam * u["unsup_b"]
        u["loss"] = u["loss_a"] + u["loss_b"]
        u["lambda"] = lam
        return u

    def _train_step(self, step: int, lab_it: Iterator, unl_it: Iterator | None) -> dict[str, float]:
        self.model.train()
        self.model_b.train()
        lab, unl = next(lab_it), next(unl_it)
        n_l = lab["image"].shape[0]
        images = torch.cat([lab["image"], unl["image"]]).to(self.device, non_blocking=True)
        masks = lab["mask"].to(self.device, non_blocking=True)

        # Only images go to the losses.  The unlabelled batch's ``hidden_mask``
        # (if present) is kept aside for region diagnostics and never moved to
        # the loss computation.
        u = self.compute_losses(step, images, masks, n_l)
        loss = u["loss"]
        for opt in (self.optimizer, self.optimizer_b):
            opt.zero_grad(set_to_none=True)
        self.scaler.scale(loss).backward()
        for model, opt in ((self.model, self.optimizer), (self.model_b, self.optimizer_b)):
            if self.grad_clip and self.grad_clip > 0:
                self.scaler.unscale_(opt)
                torch.nn.utils.clip_grad_norm_(model.parameters(), self.grad_clip)
            self.scaler.step(opt)
        self.scaler.update()
        self.scheduler.step()
        self.scheduler_b.step()

        regions = u["_aux"]["regions"]
        self._last_aux = {**u["_aux"], "gamma": u["gamma"].detach(), "lambda": u["lambda"],
                          "hidden_mask": unl.get("hidden_mask")}
        out = {k: float(u[k].detach()) for k in ("loss", "loss_a", "loss_b", "sup_a", "sup_b", "ce_a", "cos_a",
                                        "mse_a", "ent_a", "ce_b", "cos_b", "mse_b", "ent_b", "gamma")}
        out["lambda"] = u["lambda"]
        for name, m in regions.items():
            out[f"frac_{name}"] = float(m.float().mean())
        return out

    # ---- hooks ----
    def _on_step_end(self, done: int, out: dict[str, float]) -> None:
        if self.diag_every <= 0 or done % self.diag_every or self._last_aux is None:
            return
        hidden = self._last_aux.get("hidden_mask")
        if hidden is None:
            return
        row = {"step": done, "lambda": self._last_aux["lambda"]}
        row.update(region_diagnostics(self._last_aux, hidden))
        self.region_csv.write(row)

    def _models(self) -> dict[str, nn.Module]:
        return {"model": self.model, "model_b": self.model_b}

    def _optimizers(self) -> dict[str, torch.optim.Optimizer]:
        return {"model": self.optimizer, "model_b": self.optimizer_b}

    def _schedulers(self) -> dict[str, Any]:
        return {"model": self.scheduler, "model_b": self.scheduler_b}

    def _on_resume(self, step: int) -> None:
        self.region_csv.truncate_after(step)

    def _best_payload(self, step: int, val_scalars: dict) -> dict[str, Any]:
        return {"step": step, "model_state_dict": self.model.state_dict(),
                "model_b_state_dict": self.model_b.state_dict(), "metrics": val_scalars}

    def _load_best(self, path: Path) -> None:
        state = torch.load(path, map_location=self.device, weights_only=False)
        self.model.load_state_dict(state["model_state_dict"])
        self.model_b.load_state_dict(state["model_b_state_dict"])
        logger.info("Loaded %s (step %s) for networks A and B", path, state.get("step"))

    def _secondary_eval(self, loader: DataLoader) -> dict[str, Any]:
        return self.evaluate(self.ensemble, loader)
