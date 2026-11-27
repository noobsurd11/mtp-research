"""Score extensions: rel@2 equals m0's crack_rel2; shift / dilation reference rows; summary on synthetic cells."""
import numpy as np

from bench.m0core import CRACK, cell_stats
from bench.score_ext import crack_dilated, rel_counts, shifted, summarize


def _gt(rng):
    gt = np.zeros((512, 512), np.int64)
    gt[100:300, 200] = CRACK
    gt[400:450, 50:120] = 11
    gt[:, :20] = 7
    return gt


def test_rel2_matches_m0():
    rng = np.random.default_rng(0)
    gt = _gt(rng)
    pred = shifted(gt, 1, 1)
    keep = rng.random(gt.shape) > 0.05
    assert rel_counts(pred, gt, keep, (2,))["crack_rel2"] == cell_stats(pred, gt, keep)["crack_rel2"]


def test_shift_and_dilate():
    gt = _gt(None)
    s = shifted(gt, 0, 1)
    assert (s[:, 1:] == gt[:, :-1]).all() and (s[:, 0] == gt[:, 0]).all()
    d = crack_dilated(gt)
    assert (d == CRACK).sum() > (gt == CRACK).sum() and ((gt == CRACK) <= (d == CRACK)).all()
    # 1-px vertical line dilated by the cross: 3 px wide, 2 px longer
    assert (d == CRACK).sum() == 3 * 200 + 2


def test_summarize_identity_and_shift():
    gt = _gt(None)
    cells = {"A_1": {**cell_stats(gt, gt, None), **rel_counts(gt, gt, None)}}
    m = summarize(cells)
    assert m["crack_iou"] == 1.0 and m["relF1_2"] == 1.0 and m["inact_iou"] == 1.0
    cells = {"A_1": {**cell_stats(shifted(gt, 0, 1), gt, None), **rel_counts(shifted(gt, 0, 1), gt, None)}}
    m = summarize(cells)
    assert m["crack_iou"] == 0.0 and m["relF1_1"] == 1.0
