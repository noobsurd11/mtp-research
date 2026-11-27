"""Stage A5 head_res_ceiling: stride-s head simulation (T11 A0 unit tests) and the GT-side ceilings. CPU only."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from bench import dumpfmt, headres  # noqa: E402

CR, NC = 14, 24
HW = (512, 512)


def rand_logp(seed=0):
    rng = np.random.default_rng(seed)
    z = rng.normal(0, 2, (NC, *HW)).astype(np.float32)
    z -= np.log(np.exp(z).sum(0, keepdims=True))
    return z.astype(np.float16)


def line_logp(row=200, c0=100, c1=300):
    z = np.full((NC, *HW), -8.0, np.float32)
    z[0] = -0.01
    z[CR, row, c0:c1] = -0.01
    z[0, row, c0:c1] = -6.0
    return z.astype(np.float16)


def test_s1_is_argmax_of_logp_byte_for_byte():
    lp = rand_logp()
    m = headres.stride_maps(lp, 1)
    assert np.array_equal(m["pred"], lp.astype(np.float32).argmax(0).astype(np.uint8))
    assert m["pred"].tobytes() == lp.astype(np.float32).argmax(0).astype(np.uint8).tobytes()


@pytest.mark.parametrize("s", [1, 2, 4, 8])
def test_maps_pass_dump_check(s):
    m = headres.stride_maps(rand_logp(1), s)
    info = dumpfmt.check_cell(m)
    assert info["ties"] >= 0
    assert m["m_crack"].dtype == np.float16 and m["p_crack"].dtype == np.float32


def test_one_px_line_lost_or_widened_at_s4():
    lp = line_logp()
    p1 = headres.stride_maps(lp, 1)["pred"] == CR
    assert int(p1.sum()) == 200 and p1[200, 100:300].all()
    p4 = headres.stride_maps(lp, 4)["pred"] == CR
    n4 = int(p4.sum())
    # pooled over 4 x 4 the line holds 1/4 of the window: lost (0 px) or widened (more rows than one)
    assert n4 == 0 or len(np.unique(np.nonzero(p4)[0])) > 1


def test_pool_up_shapes_and_identity():
    x = np.random.default_rng(2).random((3, *HW)).astype(np.float32)
    assert np.array_equal(headres.pool_up(x, 1), x)
    y = headres.pool_up(x, 4)
    assert y.shape == x.shape and y.dtype == np.float32
    c = np.full((1, *HW), 0.3, np.float32)
    assert np.allclose(headres.pool_up(c, 8), 0.3, atol=1e-6)


def test_crack_fraction_line():
    gt = np.zeros(HW, np.uint8)
    gt[200, 100:300] = CR
    f1 = headres.crack_fraction_up(gt, None, 1)
    assert np.array_equal(f1 > 0.5, gt == CR)
    f4 = headres.crack_fraction_up(gt, None, 4)
    assert f4.max() <= 0.25 + 1e-6 and f4.max() > 0.1          # a 1 px line fills at most a quarter of a 4 x 4 cell
    keep = np.ones(HW, bool); keep[200, 100:200] = False
    assert headres.crack_fraction_up(gt, keep, 1).sum() == pytest.approx(100)


def test_onehot_ceiling_identity_and_ties():
    rng = np.random.default_rng(3)
    gt = rng.integers(0, NC, HW).astype(np.uint8)
    assert np.array_equal(headres.onehot_ceiling(gt, 1), gt)
    g2 = np.zeros(HW, np.uint8)
    g2[:, 256:] = 5                                             # boundary on a stride-8 cell edge: exact at s = 8
    assert np.array_equal(headres.onehot_ceiling(g2, 8)[:, :250], g2[:, :250])
    g3 = np.zeros(HW, np.uint8); g3[100:102, :] = CR           # 2-row band: pooled crack <= 0.5 at s = 4; ties to GT
    out = headres.onehot_ceiling(g3, 4)
    assert out.dtype == np.uint8
    g4 = g3.copy(); g4[0, 0] = 255                             # ignore value is not a class: no crash, any class there
    headres.onehot_ceiling(g4, 2)


def test_band_rule():
    sys.path.insert(0, str(ROOT / "scripts"))
    import bench_headres as B
    assert B.band(-0.05, 0.0) == "binds"
    assert B.band(-0.001, -0.02) == "binds"
    assert B.band(-0.009, -0.009) == "free"
    assert B.band(-0.02, -0.005) == "between"
    assert B.band(-0.005, -0.015) == "between"


def _fake_run(root: Path, run_id="w1g_pf_v11_f0_s5", stems=("ARTS_00011_r1_c1", "ARTS_00011_r1_c4")):
    sd = root / "elbench1" / "house_r34_unetpp_pf_v11" / run_id / "cv5v2_f0"
    cells = {}
    for i, st in enumerate(stems):
        lp = rand_logp(10 + i)
        m = headres.stride_maps(lp, 1)
        cells[st] = dumpfmt.write_cell(sd / f"{st}.npz", m["pred"], m["oth"], m["m_crack"], m["p_crack"], m["p_inact"], lp)
    meta = {k: None for k in dumpfmt.MANIFEST_KEYS}
    meta.update({"bench": "elbench1", "method": "house_r34_unetpp_pf_v11", "run_id": run_id, "seed": 5,
                 "split_def": "/x/cv5v2_v11_f0", "split_md5": "x", "fold": 0, "set": "cv5v2_f0", "stems_md5": "x",
                 "code_repo": "x", "code_commit": "x", "step": 20000, "weights_key": "model", "device": "cpu",
                 "precision": "fp32", "tta": False, "decision_rule": "argmax24", "writer": "test", "set_kind": "open",
                 "opening": None})
    dumpfmt.write_manifest(sd, meta, {s: {k: c[k] for k in ("md5", "ties", "bytes")} for s, c in cells.items()})
    return sd.parent.parent


def test_dumps_end_to_end_and_refusal(tmp_path):
    sys.path.insert(0, str(ROOT / "scripts"))
    import bench_headres as B
    mdir = _fake_run(tmp_path / "in")
    out = tmp_path / "out"
    B.main(["dumps", "--arm", f"PF={mdir}:w1g_.*", "--strides", "1,4", "--dumps", str(out), "--workers", "1"])
    for s in (1, 4):
        sd = out / "elbench1" / f"headres_s{s}" / f"w1g_pf_v11_f0_s5_hs{s}" / "cv5v2_f0"
        doc = dumpfmt.read_manifest(sd, verify=True)
        assert doc["method"] == f"headres_s{s}" and doc["seed"] == 5 and doc["fold"] == 0
        assert doc["derived_from"][0]["run_id"] == "w1g_pf_v11_f0_s5"
        assert doc["derivation"] == f"avgpool{s}_bilinear_of_logp"
    a = dumpfmt.read_cell(out / "elbench1" / "headres_s1" / "w1g_pf_v11_f0_s5_hs1" / "cv5v2_f0" / "ARTS_00011_r1_c1.npz")
    b = dumpfmt.read_cell(mdir / "w1g_pf_v11_f0_s5" / "cv5v2_f0" / "ARTS_00011_r1_c1.npz")
    assert np.array_equal(a["pred"], b["pred"])
    with pytest.raises(SystemExit):
        B.main(["dumps", "--arm", f"PF={mdir}:w1g_.*", "--strides", "1", "--dumps", str(out), "--workers", "1"])


def test_dumps_refuse_sealed_stem(tmp_path):
    sys.path.insert(0, str(ROOT / "scripts"))
    import bench_headres as B
    from bench import derived
    sealed = sorted(derived.forbidden())[0]
    mdir = _fake_run(tmp_path / "in", stems=(sealed,))
    with pytest.raises(dumpfmt.SealedSetError):
        B.main(["dumps", "--arm", f"PF={mdir}:w1g_.*", "--strides", "1", "--dumps", str(tmp_path / "o"), "--workers", "1"])
