"""ALHVR region diagnostics (logging only).

Uses the hidden ground-truth masks of the *unlabelled* training images, which
travel through the data pipeline under the key ``hidden_mask`` purely for this
module.  Nothing here returns a tensor that is used by a loss: inputs are
detached, the computation runs under ``torch.no_grad`` and the output is a
dict of Python floats written to ``regions.csv``.
"""

from __future__ import annotations

import csv
import math
from pathlib import Path
from typing import Any

import torch

from ..data.class_info import CRACK_CLASS, INACTIVE_CLASS

BACKGROUND_CLASS = 0
REGIONS = ("r1", "r2a", "r2b", "r3")


def _frac(num: torch.Tensor, den: torch.Tensor) -> float:
    d = float(den.sum())
    return float(num.sum()) / d if d > 0 else float("nan")


@torch.no_grad()
def region_diagnostics(aux: dict[str, Any], hidden_mask: torch.Tensor) -> dict[str, float]:
    """One row of diagnostics for the current unlabelled batch.

    Args:
        aux:         ``alhvr_unsup_losses(...)["_aux"]`` plus ``gamma`` (all detached).
        hidden_mask: (B, H, W) ground truth of the unlabelled images (diagnostics only).

    Columns:
        gamma; ``frac_<region>`` pixel fraction of each region (r2 = r2a + r2b);
        ``crack_in_<region>`` / ``inactive_in_<region>``: share of GT crack /
        inactive pixels in each region;
        ``acc_<src>_<region>``: pseudo-label accuracy per region for src in
        {a, b, winner, target}; ``target`` is the label actually used as a
        target there (r2a: B's, r2b: A's, r3: DTCT winner's; r1 has none);
        ``crack_as_bg_<src>_<region>``: share of GT crack pixels in the region
        predicted as background;
        ``dtct_winner_bg_on_crack_r3`` / ``_all``: how often the winning (teacher)
        prediction on a GT crack pixel is background, in region 3 / anywhere;
        ``a_wins_r3``: share of region-3 pixels where network A is the teacher.
    """
    regions = {k: v.bool() for k, v in aux["regions"].items()}
    regions["r2"] = regions["r2a"] | regions["r2b"]
    gt = hidden_mask.to(regions["r1"].device).long()
    crack, inactive = gt == CRACK_CLASS, gt == INACTIVE_CLASS
    srcs = {"a": aux["pl_a"], "b": aux["pl_b"], "winner": aux["winner_label"]}
    target = torch.full_like(gt, -1)
    target[regions["r2a"]] = aux["pl_b"][regions["r2a"]]
    target[regions["r2b"]] = aux["pl_a"][regions["r2b"]]
    target[regions["r3"]] = aux["winner_label"][regions["r3"]]
    srcs["target"] = target

    row: dict[str, float] = {"gamma": float(aux["gamma"])}
    n = gt.numel()
    row["crack_px"] = float(crack.sum())
    row["inactive_px"] = float(inactive.sum())
    for r in REGIONS + ("r2",):
        m = regions[r]
        row[f"frac_{r}"] = float(m.sum()) / n
        row[f"crack_in_{r}"] = _frac(m & crack, crack)
        row[f"inactive_in_{r}"] = _frac(m & inactive, inactive)
    for r in REGIONS + ("r2",):
        m = regions[r]
        for s, lab in srcs.items():
            if s == "target" and r == "r1":
                continue
            row[f"acc_{s}_{r}"] = _frac(m & (lab == gt), m)
            row[f"crack_as_bg_{s}_{r}"] = _frac(m & crack & (lab == BACKGROUND_CLASS), m & crack)
    win_bg = aux["winner_label"] == BACKGROUND_CLASS
    row["dtct_winner_bg_on_crack_r3"] = _frac(regions["r3"] & crack & win_bg, regions["r3"] & crack)
    row["dtct_winner_bg_on_crack_all"] = _frac(crack & win_bg, crack)
    row["a_wins_r3"] = _frac(regions["r3"] & aux["a_wins"].bool(), regions["r3"])
    return row


class RegionCSV:
    """Append-only CSV writer; NaN is written as an empty cell."""

    def __init__(self, path: Path) -> None:
        self.path = Path(path)
        self.fields: list[str] | None = None

    def truncate_after(self, step: int) -> None:
        """On resume: keep the header and the rows up to ``step``, then keep appending."""
        if not self.path.exists():
            return
        with open(self.path, newline="") as f:
            rows = list(csv.DictReader(f))
            self.fields = list(rows[0]) if rows else None
        if self.fields is None:
            self.path.unlink()
            return
        with open(self.path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=self.fields)
            w.writeheader()
            w.writerows(r for r in rows if int(r["step"]) <= step)

    def write(self, row: dict[str, float]) -> None:
        clean = {k: ("" if isinstance(v, float) and math.isnan(v) else v) for k, v in row.items()}
        new = self.fields is None
        if new:
            self.fields = list(row)
        with open(self.path, "w" if new else "a", newline="") as f:
            w = csv.DictWriter(f, fieldnames=self.fields)
            if new:
                w.writeheader()
            w.writerow(clean)
