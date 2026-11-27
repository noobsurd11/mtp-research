"""B3 (data.scuff_class, spec_b3_scuff.md): scuff as class 24 of a 25-channel model; train masks only.

Checks: default mask loading / counting unchanged (24 still rejected); the switch accepts and counts 24; evaluation maps a
predicted scuff px to background before the 24-class metrics (and nothing changes without the switch); train.py's
switch checks; the mask build script changes only train cells with raw scuff, copies everything else byte for byte;
the LA prior has 25 entries for a B3 config and is unchanged otherwise.
"""
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest
import torch
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from src.data.benchmark_el import BenchmarkELDataset, load_index_mask  # noqa: E402
from src.data.class_stats import count_class_pixels  # noqa: E402
from src.evaluation.evaluator import evaluate_model  # noqa: E402

_spec = importlib.util.spec_from_file_location("b3_train_mod", ROOT / "scripts" / "train.py")
train = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(train)


def _save(p, a):
    Image.fromarray(a.astype(np.uint8), mode="L").save(p)


def test_mask_loading_default_and_switch(tmp_path):
    m = np.zeros((16, 16), np.uint8); m[2:5, 2:9] = 24; m[8, :] = 14
    _save(tmp_path / "c.png", m)
    with pytest.raises(ValueError):
        load_index_mask(tmp_path / "c.png")  # default: 24 is outside the 24-class taxonomy
    with pytest.raises(ValueError):
        count_class_pixels(tmp_path, ["c"])
    got = load_index_mask(tmp_path / "c.png", None, 25)
    assert np.array_equal(got, m.astype(np.int64))
    cnt = count_class_pixels(tmp_path, ["c"], None, 25)
    assert cnt.shape == (25,) and cnt[24] == 21 and cnt[14] == 16 and cnt.sum() == 256
    m[0, 0] = 25; _save(tmp_path / "d.png", m)
    with pytest.raises(ValueError):
        load_index_mask(tmp_path / "d.png", None, 25)
    ok = np.zeros((16, 16), np.uint8); ok[3, 3] = 14; _save(tmp_path / "e.png", ok)
    assert np.array_equal(count_class_pixels(tmp_path, ["e"]), count_class_pixels(tmp_path, ["e"], None, None))
    ds = BenchmarkELDataset(tmp_path, tmp_path, ["c"], None, num_classes=25)
    assert int((ds[0]["mask"] == 24).sum()) == 21


class _Fixed(torch.nn.Module):
    def __init__(self, logits):
        super().__init__()
        self.logits = logits
        self.p = torch.nn.Parameter(torch.zeros(()))

    def forward(self, x):
        return self.logits[: x.shape[0]] + 0 * self.p


def test_evaluation_folds_scuff_to_background():
    g = torch.Generator().manual_seed(0)
    lg25 = torch.randn(2, 25, 16, 16, generator=g)
    lg25[:, 24, 4:8, 4:8] = 50.0  # predicted scuff block
    lg25[:, 14, 0:2, :] = 40.0    # predicted crack rows
    masks = torch.randint(0, 24, (2, 16, 16), generator=g)
    loader = [{"image": torch.zeros(2, 1, 16, 16), "mask": masks}]
    r25 = evaluate_model(_Fixed(lg25), loader, torch.device("cpu"), 24, fold_to_bg=24)
    lg24 = lg25[:, :24].clone()
    sc = lg25.argmax(1) == 24     # every px whose argmax is scuff (the block, plus random ones)
    assert int(sc.sum()) > 32
    lg24[:, 0][sc] = 60.0         # the same px predicted as background by a 24-channel model
    r24 = evaluate_model(_Fixed(lg24), loader, torch.device("cpu"), 24)
    assert r25["confusion_matrix"] == r24["confusion_matrix"]
    assert r25["crack_iou"] == r24["crack_iou"] and r25["inactive_iou"] == r24["inactive_iou"]
    with pytest.raises(ValueError):  # without the fold a 25th class cannot enter the 24-class metrics
        evaluate_model(_Fixed(lg25), loader, torch.device("cpu"), 24)
    a = evaluate_model(_Fixed(lg24), loader, torch.device("cpu"), 24)
    b = evaluate_model(_Fixed(lg24), loader, torch.device("cpu"), 24, fold_to_bg=None)
    assert a["confusion_matrix"] == b["confusion_matrix"]  # switch absent: unchanged


def _cfg(**kw):
    cfg = {"method": "supervised", "model": {"num_classes": 24}, "data": {"dataset": "benchmark_el"},
           "loss": {"supervised": "ce_dice"}}
    for k, v in kw.items():
        sec, key = k.split("__")
        cfg.setdefault(sec, {})[key] = v
    return cfg


def test_switch_checks():
    train.check_thin_b3(_cfg(), "supervised")  # all off: no check
    train.check_thin_b3(_cfg(data__scuff_class=24, model__num_classes=25), "supervised")
    with pytest.raises(ValueError):
        train.check_thin_b3(_cfg(data__scuff_class=24), "supervised")  # 24-channel model
    with pytest.raises(ValueError):
        train.check_thin_b3(_cfg(data__scuff_class=25, model__num_classes=26), "supervised")
    with pytest.raises(ValueError):
        train.check_thin_b3(_cfg(data__scuff_class=24, model__num_classes=25), "mean_teacher")
    with pytest.raises(ValueError):
        train.check_thin_b3({**_cfg(data__scuff_class=24, model__num_classes=25), "cp": {"lambda": 1.0}}, "supervised")
    with pytest.raises(ValueError):
        train.check_thin_b3(_cfg(data__scuff_class=24, model__num_classes=25, data__mask_ignore_value=255), "supervised")
    train.check_thin_b3(_cfg(loss__skel_recall={"weight": 1.0}), "supervised")
    train.check_thin_b3(_cfg(loss__skel_recall={"weight": 0.0}), "mean_teacher")  # weight 0 = off
    with pytest.raises(ValueError):
        train.check_thin_b3(_cfg(loss__cldice={"weight": 1.0}), "alhvr")
    with pytest.raises(ValueError):
        train.check_thin_b3({**_cfg(loss__cldice={"weight": 1.0}), "absh": {"enabled": True}}, "supervised")


def _md5(p):
    return hashlib.md5(Path(p).read_bytes()).hexdigest()


def test_build_masks_escdd_s(tmp_path):
    rng = np.random.default_rng(0)
    base, raw, splits, out = tmp_path / "base", tmp_path / "raw", tmp_path / "splits", tmp_path / "lab" / "masks_s"
    for d in (base, raw, splits):
        d.mkdir()
    sp = {"train": ["t0", "t1", "t2", "t3"], "val": ["v0"], "test": ["x0"]}
    for k, v in sp.items():
        (splits / f"{k}.txt").write_text("\n".join(v) + "\n")
    for s in sum(sp.values(), []):
        m = rng.integers(0, 24, (20, 20)).astype(np.uint8); _save(base / f"{s}.png", m)
        r = m.copy()
        if s in ("t0", "t2", "x0"):
            r[3:6, 3:10] = 25  # raw scuff (x0 is a test cell: must not change)
        if s != "t3":            # t3: no raw mask
            _save(raw / f"{s}.png", r)
    cmd = [sys.executable, str(ROOT / "scripts" / "b3" / "build_masks_escdd_s.py"), "--base", str(base), "--raw",
           str(raw), "--splits", str(splits), "--out", str(out)]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0, res.stderr
    summ = json.loads((out.parent / "masks_s.summary.json").read_text())
    assert summ["cells_changed"] == 2 and summ["scuff_px"] == 42 and summ["n_files"] == 6
    assert summ["train_cells_with_raw_mask"] == 3
    for s in ("t1", "t3", "v0", "x0"):
        assert _md5(base / f"{s}.png") == _md5(out / f"{s}.png")
    for s in ("t0", "t2"):
        a, b = np.array(Image.open(base / f"{s}.png")), np.array(Image.open(out / f"{s}.png"))
        assert (b[3:6, 3:10] == 24).all() and np.array_equal(np.delete(a.ravel(), np.flatnonzero(b.ravel() == 24)),
                                                              np.delete(b.ravel(), np.flatnonzero(b.ravel() == 24)))
    assert len((out.parent / "masks_s.diff.tsv").read_text().splitlines()) == 3
    res2 = subprocess.run(cmd, capture_output=True, text=True)
    assert res2.returncode != 0  # never overwrites


def test_la_prior_25_classes(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)  # rescore_label_versions (imported by the LA script) chdirs to ROOT; restored after
    spec = importlib.util.spec_from_file_location("la_mod", ROOT / "scripts" / "rescore_logit_adjust.py")
    la = importlib.util.module_from_spec(spec); spec.loader.exec_module(la)
    data = tmp_path / "data"; (data / "splits").mkdir(parents=True); (data / "m24").mkdir(); (data / "m25").mkdir()
    (data / "splits" / "train.txt").write_text("a\nb\n")
    for s in ("a", "b"):
        m = np.zeros((10, 10), np.uint8); m[0, :] = 14; _save(data / "m24" / f"{s}.png", m)
        m[5, :3] = 24; _save(data / "m25" / f"{s}.png", m)
    monkeypatch.setattr(la, "DATA", data)
    lp24, ab24 = la.log_prior({"data": {"labeled_fraction": 1.0, "mask_subdir": "m24"}})
    lp25, ab25 = la.log_prior({"data": {"labeled_fraction": 1.0, "mask_subdir": "m25", "scuff_class": 24}})
    assert lp24.shape == (24,) and lp25.shape == (25,)
    assert abs(float(lp25[24].exp()) - 6 / 200) < 1e-6 and not bool(ab25[24]) and bool(ab24[1])
    with pytest.raises(ValueError):
        la.log_prior({"data": {"labeled_fraction": 1.0, "mask_subdir": "m25"}})  # scuff masks need the switch


def test_scuff_counts_known_overlaps():
    """Synthetic E1 cell with known overlaps -> known counts (the m0_audit_b3 per-cell scuff dict)."""
    from src.evaluation.b3_scuff import fold_scuff, scuff_counts
    pr = np.zeros((10, 10), np.int64)
    sc = np.zeros((10, 10), bool); sc[0:4, 0:5] = True          # 20 scuff px
    pr[0:2, 0:3] = 14                                           # 6 crack px on scuff
    pr[2, 0:4] = 24                                             # 4 scuff-pred px on scuff (fold -> 0, not crack)
    pr[8, 0:3] = 24                                             # 3 scuff-pred px off scuff
    pr[6, 6:9] = 14                                             # 3 crack px off scuff and off ignore
    keep = np.ones((10, 10), bool); keep[0:3, :] = False        # ignore = rows 0-2: 30 px
    pr[1, 8] = 14                                               # +1 crack on ignored, off scuff
    c = scuff_counts(pr, keep, sc)
    assert c == {"scuff_px": 20, "crack_on_scuff": 6, "scuffpred_on_scuff": 4, "scuffpred_px": 7,
                 "ignored_px": 30, "crack_on_ignored": 7}
    c0 = scuff_counts(pr, keep, None)
    assert c0["scuff_px"] == 0 and c0["crack_on_scuff"] == 0 and c0["scuffpred_px"] == 7 and c0["crack_on_ignored"] == 7
    f = fold_scuff(pr)
    assert (f[pr == 24] == 0).all() and (f[pr < 24] == pr[pr < 24]).all()
    pr24 = np.arange(24).repeat(4).reshape(8, 12)
    assert np.array_equal(fold_scuff(pr24), pr24)  # a 24-channel model: no-op
