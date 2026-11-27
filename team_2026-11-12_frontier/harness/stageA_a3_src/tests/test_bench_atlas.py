"""Stage A3 ci_error_atlas: bench/atlas.py and scripts/bench_atlas.py (synthetic cells; no dump is read)."""
from __future__ import annotations

import importlib.util
import math
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from bench import atlas as AT  # noqa: E402
from bench import dumpfmt  # noqa: E402

H = W = 64


def mk_dump(pred, extra=None):
    """logits: 5 on the predicted class, 0 elsewhere, plus optional {class: (mask, value)} overrides."""
    z = np.zeros((24, H, W), np.float32)
    np.put_along_axis(z, pred[None].astype(np.int64), 5.0, 0)
    for c, (m, val) in (extra or {}).items():
        z[c][m] = val
    lp = z - np.log(np.exp(z).sum(0, keepdims=True))
    return {"pred": pred.astype(np.uint8), "logp": lp.astype(np.float16), "p_crack": np.exp(lp[14]).astype(np.float32),
            "p_inact": np.exp(lp[11]).astype(np.float16)}


def base_gt():
    g = np.zeros((H, W), np.uint8)
    g[10:30, 10:30] = 11                 # 400 px inactive region
    g[5:41, 31] = 14                     # crack 2 px right of the region
    return g


def feats(g, pred, keep=None, extra=None, n=1):
    r = AT.cell_atlas(g, keep, [mk_dump(pred, extra)] * n, None, "ARTS_00001_r1_c1")
    return r, r["feats"][0]


def test_perfect_prediction_has_no_error():
    g = base_gt()
    _, f = feats(g, g.copy())
    assert f["fn"] == 0 and f["fp"] == 0 and f["tp"] == 400
    assert f["r_missed"] == 0 and f["r_found50"] == 1 and f["gt_r100"] == 1


def test_overlap_bucket_first():
    g = base_gt()
    p = g.copy(); p[10:30, 10:30] = 14
    _, f = feats(g, p)
    assert f["fn"] == 400 and f["fn_ov"] == 400 and f["fn_mi"] == 0
    p2 = g.copy(); p2[5:41, 31] = 11      # inactive predicted on the GT crack: FP-on-crack
    _, f2 = feats(g, p2)
    assert f2["fp_oc"] == 36 and f2["fp"] == 36


def test_missed_region_and_oracle_o2():
    g = base_gt()
    p = g.copy(); p[g == 11] = 0
    _, f = feats(g, p)
    assert f["fn_mi"] == 400 and f["r_missed"] == 1 and f["fn_in_missed_all"] == 400
    v = AT.Vec(np.array([f[k] for k in sorted(f)], float), {k: i for i, k in enumerate(sorted(f))})
    assert AT.oracle(v, a=v["fn_in_missed_all"]) == pytest.approx(1.0)
    assert f["t6_fn_miss"] == 400 and f["t8_fn_miss50"] == 400 and f["t6_r_miss"] == 1


def test_eroded_region_goes_to_crackadj_and_boundary():
    g = base_gt()
    p = g.copy(); p[g == 11] = 0; p[11:29, 11:29] = 11
    _, f = feats(g, p)
    assert f["fn"] == 400 - 18 * 18
    assert f["fn_ca"] + f["fn_bd"] == f["fn"] and f["fn_in"] == 0 and f["fn_mi"] == 0
    assert f["fn_ca"] == 22                       # column 29 (2 px from the crack at col 31) plus 2 corner px at 3 px


def test_interior_hole_and_spurious_blob():
    g = base_gt()
    p = g.copy(); p[18:22, 18:22] = 0             # 16 px hole, > 3 px from every boundary and crack
    p[45:55, 45:55] = 11                          # 100 px false region, far from everything
    _, f = feats(g, p)
    assert f["fn_in"] == 16 and f["fn"] == 16
    assert f["fp_sp"] == 100 and f["fp_sp_gi_nopc"] == 100 and f["fp_in_spur_all"] == 100
    assert f["t6_fp_false"] == 100 and f["t6_r_false"] == 1 and f["rc_spur"] == 1
    keys = sorted(f)
    v = AT.Vec(np.array([f[k] for k in keys], float), {k: i for i, k in enumerate(keys)})
    o3 = AT.oracle(v, b=v["fp_in_spur_all"], t_loss=v["tp_in_spur"])
    assert o3 == pytest.approx(384 / 400 - 384 / 500)


def test_bucket_sums_and_region_majority():
    rng = np.random.default_rng(0)
    g = base_gt()
    p = g.copy()
    noise = rng.random((H, W)) < 0.05
    p[noise] = rng.choice([0, 11, 14], size=int(noise.sum()))
    _, f = feats(g, p)
    assert sum(f[f"fn_{b}"] for b in AT.FN_B) == f["fn"]
    assert sum(f[f"fp_{b}"] for b in AT.FP_B) == f["fp"]
    assert sum(f.get(f"rc_fn_{b}", 0) for b in AT.FN_B) == f["rc_fn_has"]
    assert sum(f.get(f"rc_fp_{b}", 0) for b in AT.FP_B) == f["rc_fp_has"]
    assert f["at_n"] + f["el_n"] == f["gc_px"] == 36


def test_ignore_px_not_scored():
    g = base_gt()
    p = g.copy(); p[g == 11] = 0
    keep = np.ones((H, W), bool); keep[10:30, 10:20] = False
    _, f = feats(g, p, keep=keep)
    assert f["gi_px"] == 200 and f["fn"] == 200


def test_crack_at_overlap_predicted_inactive():
    g = base_gt()
    g[10:30, 30] = 14                              # crack touching the region (distance 1)
    p = g.copy(); p[10:30, 30] = 11
    _, f = feats(g, p)
    assert f["at_n"] >= 20 and f["at_p11"] == 20
    assert f["crack_fn_p11"] == 20


def test_rule_a_distance_and_rule_b_holes():
    g = np.zeros((H, W), np.uint8)
    p = np.zeros((H, W), np.uint8)
    p[:, 5] = 14                                   # crack evidence
    p[5:16, 8:15] = 11                             # 3 px from the crack: kept at d = 5
    p[30:41, 13:21] = 11                           # 8 px: deleted at d = 5, kept at d = 10
    _, f = feats(g, p)
    assert f["ra_ncomp"] == 2 and f["ra5_n"] == 1 and f["ra10_n"] == 0
    assert f["ra5_px"] == 11 * 8
    # rule b: an inactive ring with a background hole; p_inact >= 0.05 in one hole only
    p = np.zeros((H, W), np.uint8)
    p[5:20, 5:20] = 11; p[9:16, 9:16] = 0          # hole A, 49 px
    p[30:45, 30:45] = 11; p[34:41, 34:41] = 0      # hole B, 49 px
    hole_a = np.zeros((H, W), bool); hole_a[9:16, 9:16] = True
    _, f = feats(g, p, extra={11: (hole_a, 3.0)})
    assert f["rb_px"] == 49 and f["rb_n"] == 1 and f["rb_gi"] == 0


def test_weak_class_oracle_and_margin():
    g = np.zeros((H, W), np.uint8)
    g[20, 5:60] = 15                               # gridline line, 55 px
    gl = g == 15
    p = np.zeros((H, W), np.uint8)                 # never predicted
    _, f = feats(g, p, extra={15: (gl, 4.0)})       # margin -1 on the line
    keys = sorted(f)
    v = AT.Vec(np.array([f[k] for k in keys], float), {k: i for i, k in enumerate(keys)})
    gain, b, i0 = AT.weak_oracle(v, 15)
    assert i0 == 0.0 and gain == pytest.approx(1.0) and b in (1.0, 1.25)   # margin -1 up to float16 rounding
    h = np.array([f.get(f"w15_mh{i}", 0) for i in range(len(AT.MH_EDGES) - 1)])
    assert h.sum() == 55
    i = int(np.nonzero(h)[0][0])
    assert AT.MH_EDGES[i] <= -1.0 < AT.MH_EDGES[i + 1] + 1e-6
    assert f["w15_fn"] == 55 and f["w15_fnby0"] == 55 and f["w15_r20"] == 1 and f["w15_r20miss"] == 1


def test_label_quality_fl_and_ml():
    g = base_gt()
    p = g.copy(); p[g == 11] = 0                    # inactive region never predicted -> FL candidate
    p[45:60, 45:60] = 11                            # 225 px confident inactive on background -> ML candidate
    ml = p == 11
    r, _ = feats(g, p, n=2, extra={11: (ml, 8.0)})
    types = {(x["class"], x["type"]) for x in r["issues"]}
    assert ("inactive", "FL") in types and ("inactive", "ML") in types
    fl = [x for x in r["issues"] if x["type"] == "FL"][0]
    assert fl["seeds_agreeing"] == 2 and fl["px"] == 400
    assert r["feats"][0]["fn_mi_fl"] == 400 and r["feats"][0]["r_missed_fl"] == 1


def test_softmin_and_shape():
    assert AT.softmin([0.5] * 10) == pytest.approx(0.5)
    assert AT.softmin([0.0] + [0.9] * 3) < 0.01
    assert math.isnan(AT.softmin([]))
    rng = np.random.default_rng(1)
    img = rng.integers(0, 255, (H, W)).astype(np.float64)
    c = np.ones((H, W), bool)
    assert AT.hist_shape(img, c) == pytest.approx(AT.hist_shape(3 * img + 7, c))


def test_control_verdict():
    sc = {f"X_{i:03d}": (10, i / 100) for i in range(100)}
    ctrl = ("X_000", "X_005", "X_009")
    assert AT.control_verdict(sc, ctrl)["pass"]
    assert not AT.control_verdict(sc, ("X_000", "X_050"))["pass"]
    assert not AT.control_verdict(sc, ("X_000", "MISSING"))["pass"]
    sc["X_001"] = (0, float("nan"))                 # crack-free cells are not ranked
    assert AT.control_verdict(sc, ctrl)["n_ranked"] == 99


def pooled(n=60, seeds=(5, 6)):
    rng = np.random.default_rng(2)
    stems = [f"ARTS_{i:05d}_r1_c1" for i in range(n)]
    names = ["a", "b", "gi_px"]
    F = rng.integers(0, 20, (n, len(seeds), 3)).astype(float)
    F[:, 1, 2] = F[:, 0, 2]
    fold_of = {s: i % 5 for i, s in enumerate(stems)}
    groups = {s: f"g{i // 3}" for i, s in enumerate(stems)}
    return AT.Pooled(stems, list(seeds), names, F, fold_of, groups, {"all": np.ones(n, bool)}), F


def test_pooled_point_boot_lt3():
    P, F = pooled()
    v = P.point()["all"]
    assert v["a"] == pytest.approx(F[:, :, 0].sum(0).mean())
    st = {"r": lambda V: AT.ratio(V["all"]["a"], V["all"]["a"] + V["all"]["b"])}
    b1, b2 = P.boot(st, n_boot=200, seed=0), P.boot(st, n_boot=200, seed=0)
    assert b1 == b2 and b1["units"] == 20
    assert b1["stats"]["r"]["lo"] <= st["r"](P.point()) <= b1["stats"]["r"]["hi"]
    tg = P.top_groups("gi_px")
    assert len(tg) == 3
    tot = {}
    for i, s in enumerate(P.stems):
        tot[P.group[i]] = tot.get(P.group[i], 0) + F[i, 0, 2]
    assert set(tg) == set(sorted(tot, key=lambda k: -tot[k])[:3])
    d = P.drop_mask(tg)
    assert d.sum() == 9
    assert P.point(drop=d)["all"]["a"] == pytest.approx(F[~d][:, :, 0].sum(0).mean())


def test_gate_outcome_rules():
    w = ("OPEN", "CLOSED")
    assert AT.gate_outcome([True], [True], "all", w) == "OPEN"
    assert AT.gate_outcome([True], [False], "all", w).startswith("LEAD DECIDES")
    assert AT.gate_outcome([False], [True], "all", w) == "CLOSED"
    assert AT.gate_outcome([None], [True], "all", w) == "NOT READABLE"
    assert AT.gate_outcome([False, True], [False, True], "any", w) == "OPEN"
    assert AT.t6_outcome(0.6, 0.1) == "BUILD" and AT.t6_outcome(0.2, 0.1) == "PARK"
    assert AT.t6_outcome(0.4, 0.1) == "LEAD DECIDES"
    assert AT.holds(0.25, ">=", 0.25) and AT.holds(float("nan"), ">=", 0) is None


def test_stat_defs_on_one_cell():
    g = base_gt()
    p = g.copy(); p[g == 11] = 0; p[45:55, 45:55] = 11
    r, f = feats(g, p, n=2)
    keys = sorted(f)
    F = np.array([[[x[k] for k in keys] for x in r["feats"]]], float)
    subs = {"all": np.array([True]), "src:ARTS": np.array([True]), "pg_top": np.array([True]),
            "pg_rest": np.array([False]), "pgw_top": np.array([True]), "pgw_rest": np.array([False]),
            "pg_top&src:ARTS": np.array([True]), "pg_rest&src:ARTS": np.array([False]), "fold:0": np.array([True])}
    P = AT.Pooled(["ARTS_00001_r1_c1"], [5, 6], keys, F, {"ARTS_00001_r1_c1": 0}, {"ARTS_00001_r1_c1": "g"}, subs)
    S = AT.stat_defs(["src:ARTS"], [0], 5)
    V = P.point()
    assert S["G-paste px"][0](V) == pytest.approx(1.0)
    assert S["T6 miss px"][0](V) == pytest.approx(1.0) and S["T6 false px"][0](V) == pytest.approx(1.0)
    assert S["T8 a px"][0](V) + S["T8 c px"][0](V) + S["T8 b px"][0](V) == pytest.approx(1.0)
    assert AT.scoped(S["G-paste px"][0], "src:ARTS")(V) == pytest.approx(1.0)


def _script():
    spec = importlib.util.spec_from_file_location("bench_atlas", ROOT / "scripts" / "bench_atlas.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_script_refuses_sealed_stems_and_overwrite(tmp_path):
    m = _script()
    fb = Path("/home/noob/work/b6/b6_forbidden.txt")
    if not fb.exists():
        pytest.skip("forbidden list not on this machine")
    sealed = next(l.strip() for l in open(fb) if l.strip())
    with pytest.raises(dumpfmt.SealedSetError):
        m.check_open([], [sealed])
    (tmp_path / "x").write_text("1")
    with pytest.raises(FileExistsError):
        m.main(["--arm", "PF=/nonexistent:x", "--out", str(tmp_path)])
