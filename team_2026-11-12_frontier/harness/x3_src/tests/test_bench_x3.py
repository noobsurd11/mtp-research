"""x3 tools on dumps: crossfit_op, src_calib, dti_hysteresis, D0 placement, cells.tsv subsets, label sets, pp cards. CPU."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pytest
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from bench import cards, cellmeta, crossfit_op as X, dumpfmt  # noqa: E402
from bench.m0core import cell_stats  # noqa: E402
from bench.placement import d0_cell  # noqa: E402
from bench.postproc import hysteresis as H, src_calib as SC, validate_postproc  # noqa: E402
from bench.score_ext import rel_counts  # noqa: E402
from bench.skel import skeletonize  # noqa: E402

CR = 14


def fake_dump(rng, n_lines=2, width=2, shape=(512, 512)):
    """Consistent dump: oth random non-crack class blocks, margin positive on a few line segments."""
    oth = np.zeros(shape, np.uint8)
    oth[:, 256:] = 1
    m = np.full(shape, -3.0, np.float32)
    for _ in range(n_lines):
        y = int(rng.integers(20, 490)); x0 = int(rng.integers(0, 200))
        m[y:y + width, x0:x0 + 200] = rng.uniform(0.2, 3.0)
        m[y - 2:y, x0:x0 + 200] = -0.6               # faint shoulder: a positive bias widens
    m = m.astype(np.float16)
    pred = np.where(m.astype(np.float32) > 0, CR, oth).astype(np.uint8)
    pc = 1 / (1 + np.exp(-m.astype(np.float32)))
    return {"pred": pred, "oth": oth, "m_crack": m, "p_crack": pc.astype(np.float32),
            "p_inact": np.zeros(shape, np.float16)}


def fake_gt(d, shift=0, dilate=False, ignore_box=True):
    gt = d["oth"].copy()
    c = d["pred"] == CR
    if shift:
        c = np.roll(c, shift, 0)
    if dilate:
        c = ndi.binary_dilation(c, ndi.generate_binary_structure(2, 1))
    gt[c] = CR
    keep = np.ones_like(gt, bool)
    if ignore_box:
        keep[:30, :30] = False
    return gt, keep


# ---------------------------------------------------------------- skeleton
def test_skeleton_bar_and_empty():
    a = np.zeros((40, 80), bool); a[18:23, 10:70] = True
    s = skeletonize(a)
    assert s.sum() > 40 and s.sum() <= 62
    assert set(np.nonzero(s)[0]) <= {19, 20, 21}
    assert not skeletonize(np.zeros((10, 10), bool)).any()
    one = np.zeros((10, 10), bool); one[5, 2:8] = True
    assert (skeletonize(one) == one).all()


# ---------------------------------------------------------------- counts = m0 formulas
@pytest.mark.parametrize("seed", [0, 1, 2])
def test_crack_counts_equal_m0(seed):
    rng = np.random.default_rng(seed)
    d = fake_dump(rng)
    gt, keep = fake_gt(d, shift=1)
    G = X.CellGT(gt, keep)
    for b in (-1.0, 0.0, 0.5, 4.0):
        mask = X.crack_mask(("bias", b), d)
        cmap = np.where(mask, CR, d["oth"]).astype(np.uint8)
        cs = cell_stats(cmap, gt, keep, None)
        rc = rel_counts(cmap, gt, keep, radii=(1, 2))
        C = np.array(cs["conf"]).reshape(24, 24)
        got = X.crack_counts(mask, G)
        want = [C[CR, CR], C[:, CR].sum(), C[CR].sum(), rc["crack_rel1"][0], rc["crack_rel1"][2],
                rc["crack_rel2"][0], rc["crack_rel2"][2]]
        assert got.tolist() == [int(x) for x in want], b
        assert rc["crack_rel2"] == cs["crack_rel2"]


def test_sweep_cache_and_crackfree():
    rng = np.random.default_rng(3)
    d = fake_dump(rng)
    gt = d["oth"].copy()                                   # crack-free cell
    G = X.CellGT(gt, None)
    cl = X.bias_cands()
    S = X.sweep_cell(d, G, cl)
    for i in (0, 5, 30):
        assert S[i].tolist() == X.crack_counts(X.crack_mask(cl[i], d), G).tolist()
    assert (S[:, 2] == 0).all() and (S[:, 0] == 0).all()


def test_record_matches_bench_score_record():
    rng = np.random.default_rng(4)
    d = fake_dump(rng)
    gt, keep = fake_gt(d, shift=1)
    r = X.record(d["pred"], gt, keep, d["p_crack"])
    want = cell_stats(d["pred"], gt, keep, d["p_crack"]); want.update(rel_counts(d["pred"], gt, keep, radii=(1, 3)))
    assert {k: v for k, v in r.items() if k != "crack_skel"} == json.loads(json.dumps(want))
    assert r["crack_skel"][0] > 0 and r["crack_skel"][1] > 0


def test_bias_zero_reproduces_pred_except_ties():
    rng = np.random.default_rng(5)
    d = fake_dump(rng)
    assert (X.class_map(("bias", 0.0), d) == d["pred"]).all()
    assert (X.class_map(("argmax",), d) == d["pred"]).all()


# ---------------------------------------------------------------- choose / crossfit
def _counts_row(tp, pp, gp, p2, g2):
    return np.array([tp, pp, gp, p2, g2, p2, g2], np.int64)


def test_crossfit_never_uses_heldout_fold_and_ties():
    cl = [("argmax",), ("bias", -1.0), ("bias", 1.0), ("bias", 2.0)]
    n = 10
    C = np.zeros((n, len(cl), 7), np.int64)
    folds = np.array([0] * 5 + [1] * 5)
    # fold 0 cells: candidate 3 (b +2) best; fold 1 cells: candidate 1 (b -1) best
    for i in range(5):
        C[i] = [_counts_row(1, 10, 10, 2, 2), _counts_row(1, 10, 10, 2, 2), _counts_row(1, 10, 10, 2, 2),
                _counts_row(9, 10, 10, 10, 10)]
        C[5 + i] = [_counts_row(1, 10, 10, 2, 2), _counts_row(9, 10, 10, 10, 10), _counts_row(1, 10, 10, 2, 2),
                    _counts_row(1, 10, 10, 2, 2)]
    ch = X.crossfit(C, folds, cl, "crack_iou")
    assert ch == {0: 1, 1: 3}                              # each fold gets the other fold's best
    T = np.tile(_counts_row(5, 10, 10, 8, 8), (4, len(cl), 1))
    assert X.choose(T.sum(0), cl, "crack_iou") == 0          # all tied: argmax first
    assert X.choose(T.sum(0), cl[1:], "crack_iou") == 0      # |b| 1 before |b| 2; -1 before +1 by order


def test_opf_guard_and_opw_target():
    cl = [("argmax",), ("bias", 0.0), ("bias", 2.0), ("bias", 4.0)]
    C = np.zeros((4, 4, 7), np.int64)
    folds = np.array([0, 0, 1, 1])
    for i in range(4):
        C[i] = [_counts_row(5, 10, 10, 9, 6), _counts_row(5, 10, 10, 9, 6),
                _counts_row(7, 20, 10, 15, 9), _counts_row(8, 40, 10, 20, 10)]
    opf = X.crossfit(C, folds, cl, "relF1_2", relp_guard=0.05)
    assert all(cl[i] == ("bias", 0.0) or cl[i] == ("argmax",) for i in opf.values())   # relP 0.75 < 0.9 - 0.05 refused
    opw = X.crossfit(C, folds, cl, "width", target_by_fold={0: 2.0, 1: 4.0})
    assert opw == {0: 2, 1: 3}


# ---------------------------------------------------------------- bootstrap and margins
def _toy_records(rng, n, shift):
    out = {}
    for i in range(n):
        d = fake_dump(rng)
        gt, keep = fake_gt(d, shift=shift)
        out[f"ARTS_{i:05d}_r1_c1"] = X.record(d["pred"], gt, keep, None)
    return out


def test_bootstrap_identical_arms_zero_and_margin_floor():
    rng = np.random.default_rng(6)
    recs = _toy_records(rng, 6, 1)
    stems = list(recs)
    fold_of = {s: i % 2 for i, s in enumerate(stems)}
    groups = {s: f"g{i // 2}" for i, s in enumerate(stems)}
    A = {5: recs, 6: recs}
    b = X.boot_pair(A, {7: recs, 8: recs}, stems, fold_of, groups, n_boot=50)
    for k, v in b["metrics"].items():
        assert v["delta"] == 0 or not np.isfinite(v["delta"])
        assert v["lo"] == 0 and v["hi"] == 0 or not np.isfinite(v["lo"])
    M = X.margins(b)
    assert M["crack_iou"] == 0.01
    g = X.guards(recs)
    assert g["width_ratio"] > 0 and np.isfinite(g["mean_width"])


# ---------------------------------------------------------------- dti (T5 spec tests a to d)
def test_dti_equal_thresholds_is_pred():
    rng = np.random.default_rng(7)
    d = fake_dump(rng)
    m = d["m_crack"].astype(np.float32)
    assert (H.dti(m, d["oth"], 0.0, 0.0) == d["pred"]).all()


def test_dti_grows_from_seed_only():
    m = np.full((40, 40), -5.0, np.float32)
    m[10, 5] = 3.0
    m[10, 6:20] = -1.0                                     # chain joined to the seed
    m[30, 5:15] = -1.0                                     # isolated faint blob
    mk = H.dti_mask(m, 0.0, -2.0)
    assert mk[10, 5:20].all() and not mk[30].any()
    out = H.dti(m, np.zeros((40, 40), np.uint8), 0.0, -2.0)
    assert out.max() < 24 and set(np.unique(out)) <= {0, 14}
    assert len(H.grid()) == 57                          # the spec grid as written (it says 60 pairs; t_lo <= t_hi leaves 57)


def test_tools_refuse_sealed_sets(tmp_path):
    from bench import w1read
    sd = tmp_path / "x" / "test50"
    sd.mkdir(parents=True)
    (sd / "manifest.json").write_text(json.dumps({"format": dumpfmt.FORMAT, "set": "test50", "cells": {}}))
    with pytest.raises(dumpfmt.SealedSetError):
        w1read._load_run("A", sd, "set")


# ---------------------------------------------------------------- src_calib (T4 spec tests 1 to 4)
def test_src_calib_none_reproduces_pred_records():
    rng = np.random.default_rng(8)
    d = fake_dump(rng)
    gt, keep = fake_gt(d, shift=1)
    a = X.record(X.class_map(("morph", "none"), d), gt, keep, d["p_crack"])
    b = X.record(d["pred"], gt, keep, d["p_crack"])
    assert a == b


def _src_cells(rng, src, n, dilate):
    cells = []
    for i in range(n):
        d = fake_dump(rng)
        gt, keep = fake_gt(d, dilate=dilate, ignore_box=False)
        cells.append((f"{src}_{i:05d}_r1_c1", d, gt, keep))
    return cells


def test_src_calib_crossfit_per_source_and_fallback():
    rng = np.random.default_rng(9)
    cl = SC.cands()
    cells = _src_cells(rng, "ARTS", 44, True) + _src_cells(rng, "CFVS", 44, False) + _src_cells(rng, "SDLE", 6, True)
    stems = [c[0] for c in cells]
    C = np.stack([X.sweep_cell(d, X.CellGT(gt, keep), cl) for _, d, gt, keep in cells])
    folds = np.array([i % 2 for i in range(len(stems))])
    ch = SC.fit(C, stems, folds, cl)
    for k in (0, 1):
        a = cl[ch["src_bias"][k]["ARTS"]]; c = cl[ch["src_bias"][k]["CFVS"]]
        assert a[1] > 0 and c[1] == 0.0                    # ARTS labels are wider: positive bias; CFVS: none
        assert cl[ch["src_morph"][k]["ARTS"]][1].startswith("dilate") and cl[ch["src_morph"][k]["CFVS"]][1] == "none"
        assert "SDLE" in ch["fallback"][k] and ch["src_bias"][k]["SDLE"] == ch["glob_bias"][k]
        assert ch["n_crack"][k]["ARTS"] == 22               # only the other fold's cells counted (>= 20: own fit)
    per = SC.choice_per_cell(ch, "src_bias", stems, folds, cl)
    assert per[0] == cl[ch["src_bias"][0]["ARTS"]]


# ---------------------------------------------------------------- D0
def test_d0_prediction_on_ridge_label_off(tmp_path):
    from PIL import Image
    img = np.full((512, 512), 200, np.uint8)
    for x in range(100, 400):
        img[250:252, x] = 90                               # dark line at rows 250-251
    Image.fromarray(img).save(tmp_path / "ARTS_00001_r1_c1.png")
    pred = np.zeros((512, 512), np.uint8); pred[250:252, 100:400] = CR
    gt = np.zeros((512, 512), np.uint8); gt[253:255, 100:400] = CR          # label 3 px below the line
    pc = np.where(pred == CR, 0.9, 0.05).astype(np.float32)
    d = {"pred": pred, "p_crack": pc}
    r = d0_cell(d, gt, None, {"images": str(tmp_path), "stem": "ARTS_00001_r1_c1", "snapped": None})
    pn, pv, p1, _ = r["pred"]; gn, gv, g1, _ = r["gt"]
    assert pv > 50 and p1 / pv > 0.9
    assert gv > 50 and g1 / gv < 0.1
    assert r["prof_n"] > 0 and r["p_ridge_sum"] > r["p_label_sum"]


# ---------------------------------------------------------------- cells.tsv, label sets, cards
def test_cellmeta_subsets_and_label_sets():
    cells = {"ARTS_1_r1_c1": {"source": "ARTS", "cell_type": "mono", "crack_px_v11": "0", "flags": "noisy"},
             "CFVS_1_r1_c1": {"source": "CFVS", "cell_type": "multi", "crack_px_v11": "12", "flags": ""}}
    S = cellmeta.subsets(list(cells), cells)
    assert S["crackfree"]("ARTS_1_r1_c1") and not S["crackfree"]("CFVS_1_r1_c1")
    assert S["flag:noisy"]("ARTS_1_r1_c1") and S["-flagged"]("CFVS_1_r1_c1")
    assert S["type:multi"]("CFVS_1_r1_c1") and S["src:ARTS"]("ARTS_1_r1_c1")
    assert cellmeta.label_set_of_root("/home/noob/work/bench_data/roots/cv5v2_v11_f3") == "v11"
    assert cellmeta.label_set_of_root("/x/cv5v2_v1_f0/") == "v1"
    assert cellmeta.label_set_of_root("/home/noob/work/b6/b6_root_0") == "v1"
    assert cellmeta.label_set_of_root("/x/other") is None


@pytest.mark.parametrize("name", ["pp_src_calib_pf_v11", "pp_dti_pf_v11"])
def test_pp_cards_validate_and_equal_pf_v11_config(name):
    c = cards.load_card(ROOT / f"bench/methods/{name}.yaml")
    assert validate_postproc(c) == []
    ref = cards.load_card(ROOT / "bench/methods/house_r34_unetpp_pf_v11.yaml")
    assert cards.config_diff(cards.expected_config(ref, 5, "x", "R"), cards.expected_config(c, 5, "x", "R")) == []
    assert c["opts"] == ref["opts"] and c["weights"] == ref["weights"]


def test_validate_postproc_catches_errors():
    for f in sorted((ROOT / "bench" / "methods").glob("*.yaml")):
        assert validate_postproc(cards.load_card(f)) == [], f.name
    bad = {"kind": "harness", "decision_rule": "argmax24", "postproc": {"name": "x", "script": "y", "uses_source_metadata": 1}}
    assert len(validate_postproc(bad)) == 2
