"""ALHVR unlabelled losses: adaptive threshold, regions, CG-CPCL and DTCT.

Port of ``refs/ALHVR/train_ALHVR/code/train_ALHVR_acdc.py``; see
``docs/alhvr_port_notes.md`` for every term, the paper equation and the
differences.  Defaults reproduce the reference code; each deviation is a flag
in :class:`ALHVRConfig`.

Notation: networks A and B; ``*1`` = unperturbed (main) pass, ``*2`` =
perturbed pass.  All inputs here are the **unlabelled** part of the batch.
Everything is computed in float32.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, fields
from typing import Any

import torch
import torch.nn.functional as F

EPS_MASK = 1e-16      # masked-mean denominators (reference value)
EPS_PROTO = 1e-5      # per-image prototype denominator (reference value)
EPS_LOG = 1e-6        # entropy log (reference value)
ABSENT_LOGIT = -1e4   # logit for prototype classes skipped because absent


@dataclass
class ALHVRConfig:
    cpcl: bool = True                    # module switch: CG-CPCL on region 2
    dtct: bool = True                    # module switch: DTCT on region 3
    proportion: float = 0.8              # beta: fraction of lowest confidences averaged into gamma
    temperature: float = 0.1             # T in the sharpening function
    sharpening: str = "elementwise"      # reference | "softmax"
    prototype_scale: float = 1.0         # reference 1 | 10
    pull_all_prototypes: bool = True     # reference cosine term on | off
    dtct_detach_target: bool = False     # reference off | on
    feature_layer: str = "deep"          # reference-like "deep" | "penultimate"
    lambda_max: float = 0.1              # lambda(t) = lambda_max * exp(-5 (1 - t/T)^2)

    @classmethod
    def from_dict(cls, d: dict[str, Any] | None) -> "ALHVRConfig":
        d = dict(d or {})
        known = {f.name for f in fields(cls)}
        unknown = set(d) - known
        if unknown:
            raise ValueError(f"unknown alhvr config keys: {sorted(unknown)}")
        cfg = cls(**d)
        if cfg.sharpening not in ("elementwise", "softmax"):
            raise ValueError(f"alhvr.sharpening must be elementwise|softmax, got {cfg.sharpening!r}")
        return cfg


# ---------------------------------------------------------------------------
# Schedule, threshold, regions
# ---------------------------------------------------------------------------

def unsup_weight(step: int, total_steps: int, lambda_max: float) -> float:
    """Reference ramp ``0.1 * sigmoid_rampup``: lambda_max * exp(-5 (1 - t/T)^2), t clipped to T."""
    t = min(max(step, 0), total_steps) / max(total_steps, 1)
    return lambda_max * math.exp(-5.0 * (1.0 - t) ** 2)


def adaptive_threshold(con: torch.Tensor, proportion: float) -> torch.Tensor:
    """gamma: mean of the lowest ``int(numel * proportion)`` confidences (Eq. 11, pooled over the batch)."""
    flat = con.detach().float().flatten()
    k = max(1, int(flat.numel() * proportion))
    return torch.sort(flat).values[:k].mean()


def region_masks(con_a2: torch.Tensor, con_b2: torch.Tensor, gamma: torch.Tensor) -> dict[str, torch.Tensor]:
    """Region masks from the perturbed confidences, using the reference inequalities.

    ``r2a``: A unsure, B sure (A learns from B); ``r2b``: the reverse;
    ``r3``: both unsure; ``r1``: everything else (both sure, plus exact ties),
    so the four masks partition the pixels.
    """
    r3 = (con_a2 < gamma) & (con_b2 < gamma)
    r2a = (con_a2 <= gamma) & (con_b2 > gamma)
    r2b = (con_b2 <= gamma) & (con_a2 > gamma)
    r1 = ~(r2a | r2b | r3)
    return {"r1": r1, "r2a": r2a, "r2b": r2b, "r3": r3}


# ---------------------------------------------------------------------------
# Sharpening / entropy
# ---------------------------------------------------------------------------

def sharpen(p: torch.Tensor, temperature: float, mode: str = "elementwise") -> torch.Tensor:
    """Eq. 22.  ``elementwise`` (reference): p^(1/T) / (p^(1/T) + (1-p)^(1/T)) per class,
    not renormalised over classes.  ``softmax``: p^(1/T) renormalised over classes (dim 1)."""
    inv_t = 1.0 / temperature
    if mode == "elementwise":
        pt = p ** inv_t
        return pt / (pt + (1 - p) ** inv_t)
    if mode == "softmax":
        return torch.softmax(torch.log(p.clamp_min(1e-12)) * inv_t, dim=1)
    raise ValueError(mode)


def masked_entropy_mean(p: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
    """Reference entropy: -sum_c (p*m) log(p*m + 1e-6), averaged over ALL pixels."""
    pm = p * mask.unsqueeze(1)
    return (-(pm * torch.log(pm + EPS_LOG)).sum(dim=1)).mean()


def masked_mean(values: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
    """sum(mask * values) / (sum(mask) + 1e-16); exactly 0 for an empty mask."""
    m = mask.to(values.dtype)
    return (values * m).sum() / (m.sum() + EPS_MASK)


# ---------------------------------------------------------------------------
# Prototypes (Eq. 15) and cosine logits (Eq. 16)
# ---------------------------------------------------------------------------

def class_prototypes(feats: torch.Tensor, labels: torch.Tensor, num_classes: int) -> tuple[torch.Tensor, torch.Tensor]:
    """Reference prototypes: per-image masked mean, averaged over images.

    Args:
        feats:  (B, C, H, W) features at label resolution.
        labels: (B, H, W) pseudo-labels.

    Returns:
        (prototypes (K, C), present (K,) bool: class has >= 1 pixel in the batch).
        The reference divides the per-image sum by the batch size; since only
        cosine similarities are used, the scale does not matter, and here the
        sum is divided by the number of images that contain the class.
    """
    B, C = feats.shape[:2]
    one_hot = F.one_hot(labels.long(), num_classes).permute(0, 3, 1, 2).reshape(B, num_classes, -1).float()
    counts = one_hot.sum(dim=2)                                          # (B, K)
    sums = torch.einsum("bkn,bcn->bkc", one_hot, feats.reshape(B, C, -1).float())
    per_image = sums / (counts.unsqueeze(2) + EPS_PROTO)                 # (B, K, C)
    n_images = (counts > 0).sum(dim=0)                                   # (K,)
    protos = per_image.sum(dim=0) / n_images.clamp_min(1).unsqueeze(1).float()
    return protos, n_images > 0


def cosine_logits(feats: torch.Tensor, protos: torch.Tensor) -> torch.Tensor:
    """cos(feats[b,:,h,w], protos[k]) -> (B, K, H, W).  A zero vector gives 0, never NaN."""
    f = feats.float() / feats.float().norm(dim=1, keepdim=True).clamp_min(1e-8)
    p = protos.float() / protos.float().norm(dim=1, keepdim=True).clamp_min(1e-8)
    return torch.einsum("bchw,kc->bkhw", f, p)


def cpcl_terms(
    feat_aux: torch.Tensor,
    protos_other: torch.Tensor,
    present_other: torch.Tensor,
    target_other: torch.Tensor,
    mask: torch.Tensor,
    scale: float,
    pull_all: bool,
) -> tuple[torch.Tensor, torch.Tensor]:
    """CG-CPCL for one network (Eqs. 19-20, reference ``compute_prototype_loss``).

    Perturbed features of this network vs the other network's prototypes,
    CE against the other network's pseudo-labels, on ``mask`` (this network
    unsure, the other sure).  Classes absent from the other network's
    pseudo-labels are skipped: excluded from the CE softmax and from the
    cosine pull average.

    Returns (ce, cos): ce = masked mean CE; cos = mean over (B, present K, H, W)
    of (1 - scale*cos) * mask (reference normalisation), 0 if ``pull_all`` is off.
    """
    logits = cosine_logits(feat_aux, protos_other) * scale                  # (B, K, H, W)
    absent = ~present_other
    ce_logits = logits.masked_fill(absent.view(1, -1, 1, 1), ABSENT_LOGIT)
    ce = F.cross_entropy(ce_logits, target_other.long(), reduction="none")   # (B, H, W)
    ce_loss = masked_mean(ce, mask)
    if pull_all:
        m = mask.to(logits.dtype).unsqueeze(1)
        cos_loss = ((1 - logits[:, present_other]) * m).mean()
    else:
        cos_loss = torch.zeros((), device=logits.device)
    return ce_loss, cos_loss


# ---------------------------------------------------------------------------
# Full unlabelled loss
# ---------------------------------------------------------------------------

def alhvr_unsup_losses(
    logits_a1: torch.Tensor,
    logits_a2: torch.Tensor,
    feat_a1: torch.Tensor,
    feat_a2: torch.Tensor,
    logits_b1: torch.Tensor,
    logits_b2: torch.Tensor,
    feat_b1: torch.Tensor,
    feat_b2: torch.Tensor,
    cfg: ALHVRConfig,
) -> dict[str, torch.Tensor]:
    """All ALHVR unlabelled terms for networks A and B on an unlabelled batch.

    Takes logits and features only: there is deliberately no label argument.
    Returns scalar loss terms (``*_a``, ``*_b``), ``unsup_a`` / ``unsup_b``
    (= ce + cos + mse + ent per network, before lambda), ``gamma``, and the
    detached tensors used for diagnostics under ``"_aux"``.
    """
    sa1, sa2 = torch.softmax(logits_a1.float(), 1), torch.softmax(logits_a2.float(), 1)
    sb1, sb2 = torch.softmax(logits_b1.float(), 1), torch.softmax(logits_b2.float(), 1)
    con_a1, pl_a = sa1.max(dim=1)
    con_b1, pl_b = sb1.max(dim=1)
    con_a2, con_b2 = sa2.max(dim=1).values, sb2.max(dim=1).values

    gamma = adaptive_threshold((con_a2 + con_b2) * 0.5, cfg.proportion)
    regions = region_masks(con_a2.detach(), con_b2.detach(), gamma)
    zero = torch.zeros((), device=sa1.device)
    out: dict[str, Any] = {"gamma": gamma}

    # ---- CG-CPCL on region 2 ----
    if cfg.cpcl:
        size = logits_a1.shape[-2:]
        up = lambda f: F.interpolate(f.float(), size=size, mode="bilinear", align_corners=False)
        fa1, fa2, fb1, fb2 = up(feat_a1), up(feat_a2), up(feat_b1), up(feat_b2)
        K = logits_a1.shape[1]
        protos_a, present_a = class_prototypes(fa1, pl_a, K)
        protos_b, present_b = class_prototypes(fb1, pl_b, K)
        out["ce_a"], out["cos_a"] = cpcl_terms(fa2, protos_b, present_b, pl_b, regions["r2a"],
                                               cfg.prototype_scale, cfg.pull_all_prototypes)
        out["ce_b"], out["cos_b"] = cpcl_terms(fb2, protos_a, present_a, pl_a, regions["r2b"],
                                               cfg.prototype_scale, cfg.pull_all_prototypes)
    else:
        out["ce_a"] = out["cos_a"] = out["ce_b"] = out["cos_b"] = zero

    # ---- DTCT on region 3 ----
    if cfg.dtct:
        r3 = regions["r3"]
        a_wins = con_a1 > con_b1                                   # reference: ties go to B
        teacher = torch.where(a_wins.unsqueeze(1), sa1, sb1)
        target = sharpen(teacher, cfg.temperature, cfg.sharpening)
        if cfg.dtct_detach_target:
            target = target.detach()
        out["mse_a"] = masked_mean(((sa2 - target) ** 2).sum(dim=1), r3)
        out["mse_b"] = masked_mean(((sb2 - target) ** 2).sum(dim=1), r3)
        out["ent_a"] = masked_entropy_mean(sa1, r3) + masked_entropy_mean(sa2, r3)
        out["ent_b"] = masked_entropy_mean(sb1, r3) + masked_entropy_mean(sb2, r3)
    else:
        a_wins = con_a1 > con_b1
        out["mse_a"] = out["mse_b"] = out["ent_a"] = out["ent_b"] = zero

    out["unsup_a"] = out["ce_a"] + out["cos_a"] + out["mse_a"] + out["ent_a"]
    out["unsup_b"] = out["ce_b"] + out["cos_b"] + out["mse_b"] + out["ent_b"]
    out["_aux"] = {
        "regions": regions,
        "pl_a": pl_a.detach(), "pl_b": pl_b.detach(),
        "a_wins": a_wins.detach(),
        "winner_label": torch.where(a_wins, pl_a, pl_b).detach(),
    }
    return out
