"""elbench dump format: round trip, guards, ties, manifest."""
import json

import numpy as np
import pytest

from bench import dumpfmt


def _cell(rng):
    s = rng.random((24, 512, 512)).astype(np.float32)
    s /= s.sum(0, keepdims=True)
    m = dumpfmt.maps_from_scores(s)
    pred = s.argmax(0).astype(np.uint8)
    return pred, m


def test_roundtrip_and_ties(tmp_path):
    rng = np.random.default_rng(0)
    pred, m = _cell(rng)
    info = dumpfmt.write_cell(tmp_path / "c.npz", pred, m["oth"], m["m_crack"], m["p_crack"], m["p_inact"])
    d = dumpfmt.read_cell(tmp_path / "c.npz")
    assert (d["pred"] == pred).all() and d["p_crack"].dtype == np.float32 and d["m_crack"].dtype == np.float16
    assert info["ties"] == dumpfmt.check_cell(d)["ties"]
    with pytest.raises(FileExistsError):
        dumpfmt.write_cell(tmp_path / "c.npz", pred, m["oth"], m["m_crack"], m["p_crack"], m["p_inact"])


def test_inconsistent_pred_refused(tmp_path):
    rng = np.random.default_rng(1)
    pred, m = _cell(rng)
    bad = pred.copy()
    bad[m["m_crack"].astype(np.float32) < -1] = 14          # crack where the margin is clearly negative
    with pytest.raises(AssertionError):
        dumpfmt.write_cell(tmp_path / "b.npz", bad, m["oth"], m["m_crack"], m["p_crack"], m["p_inact"])


def test_sets_and_guard():
    assert dumpfmt.check_set("val54", None) == "open"
    assert dumpfmt.check_set("cv5v1_f3", None) == "open"
    with pytest.raises(dumpfmt.SealedSetError):
        dumpfmt.check_set("test50", None)
    with pytest.raises(dumpfmt.SealedSetError):
        dumpfmt.check_set("e1_106", "")
    assert dumpfmt.check_set("e1_106", "protocol_X") == "sealed"
    with pytest.raises(ValueError):
        dumpfmt.check_set("test", None)


def test_manifest(tmp_path):
    rng = np.random.default_rng(2)
    cells = {}
    for s in ("A_1", "A_2"):
        pred, m = _cell(rng)
        cells[s] = dumpfmt.write_cell(tmp_path / f"{s}.npz", pred, m["oth"], m["m_crack"], m["p_crack"], m["p_inact"])
    meta = {k: None for k in dumpfmt.MANIFEST_KEYS}
    meta["set"] = "val54"
    dumpfmt.write_manifest(tmp_path, meta, cells)
    doc = dumpfmt.read_manifest(tmp_path)
    assert doc["n_cells"] == 2
    (tmp_path / "A_2.npz").write_bytes(b"x")
    with pytest.raises(AssertionError):
        dumpfmt.read_manifest(tmp_path)
