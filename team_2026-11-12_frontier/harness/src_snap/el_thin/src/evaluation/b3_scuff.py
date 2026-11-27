"""B3 scorer helpers (pure numpy; used by scripts/b3/m0_audit_b3.py, unit-tested in tests/test_b3_scuff.py).

``fold_scuff``: a predicted class >= 24 (the scuff channel of a 25-channel model) becomes background 0; 0-23 unchanged.
``scuff_counts``: per E1 cell, the descriptive crack-on-scuff counts of spec_b3_scuff.md 4.1:
  scuff_px            raw E-SCDD class-25 px of the cell (0 without a scuff mask);
  crack_on_scuff      folded prediction == crack (14) on scuff px;
  scuffpred_on_scuff  raw argmax == scuff (24) on scuff px (before the fold);
  scuffpred_px        raw argmax == scuff anywhere in the cell;
  ignored_px          px outside the keep mask (the ext117 ignore mask, classes 25-28);
  crack_on_ignored    folded prediction == crack on ignored px (the 27 Oct "crack_pred_on_ignored" definition).
Whole image, not limited to the keep mask. Diagnostic read of E1: only inside a registered opening.
"""
from __future__ import annotations

import numpy as np

NC, CRACK, SCUFF = 24, 14, 24


def fold_scuff(pred_raw: np.ndarray, nc: int = NC) -> np.ndarray:
    return np.where(pred_raw >= nc, 0, pred_raw)


def scuff_counts(pred_raw: np.ndarray, keep: np.ndarray, scuff: np.ndarray | None) -> dict[str, int]:
    pred = fold_scuff(pred_raw)
    ig = ~keep
    has = scuff is not None
    return {"scuff_px": int(scuff.sum()) if has else 0,
            "crack_on_scuff": int((pred[scuff] == CRACK).sum()) if has else 0,
            "scuffpred_on_scuff": int((pred_raw[scuff] == SCUFF).sum()) if has else 0,
            "scuffpred_px": int((pred_raw == SCUFF).sum()),
            "ignored_px": int(ig.sum()), "crack_on_ignored": int((pred[ig] == CRACK).sum())}
