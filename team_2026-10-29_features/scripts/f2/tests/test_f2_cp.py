"""F2 / CP5: copy-paste library, residual transfer, placement rules, targets, determinism, loss (spec_cp5 §7.2)."""
import sys
from pathlib import Path

import numpy as np
import pytest
import torch
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.data.copy_paste import (CPDataset, build_library, cell_area, compose_one, cp_loss, dilate,  # noqa: E402
                                 dihedral_np, prepare_variants)
from src.data.augmentations import get_labelsafe_augmentation  # noqa: E402


def _cell(tmp, stem, img, msk):
    (tmp / "img").mkdir(exist_ok=True); (tmp / "msk").mkdir(exist_ok=True)
    Image.fromarray(img).save(tmp / "img" / f"{stem}.png"); Image.fromarray(msk).save(tmp / "msk" / f"{stem}.png")


def _textured(seed, h=128, w=128, mean=150):
    rng = np.random.default_rng(seed)
    return np.clip(rng.normal(mean, 8, (h, w)), 0, 255).astype(np.uint8)


def _library(tmp):
    img = _textured(0); msk = np.zeros((128, 128), np.uint8)
    img[40, 20:60] = 110; msk[40, 20:60] = 14                     # good dark line
    img[90, 20:60] = 149; msk[90, 20:60] = 14                     # no contrast
    img[20, 80:120] = 110; msk[20, 80:120] = 14; msk[21:30, 80:120] = 11  # inactive ring
    img[110, 80:120] = 110; msk[110, 80:120] = 14; msk[115, 70:125] = 7   # padding in ring
    _cell(tmp, "A", img, msk)
    return build_library(tmp / "img", tmp / "msk", ["A"])


def test_library_exclusions_and_residual(tmp_path):
    kept, rec = _library(tmp_path)
    reasons = sorted(r["reason"] for r in rec)
    assert reasons == ["", "edge_ring", "inactive_ring", "low_contrast"]
    assert len(kept) == 1 and kept[0]["area"] == 40
    it = kept[0]
    assert (it["r"][it["M"]] < -20).all()           # the crack's darkness moves, with its sign
    T = dilate(it["M"], 2)
    assert np.all(it["r"][~T] == 0)


def test_variants_exact_dihedral():
    M = np.zeros((23, 27), bool); M[10, 9:17] = True; M[11:14, 16] = True   # 8 px margin, as library crops (bbox of D8)
    r = np.where(dilate(M, 2), -5.0, 0.0).astype(np.float32)
    for t, v in enumerate(prepare_variants({"M": M, "r": r})):
        assert np.array_equal(v["M"], np.pad(dihedral_np(M, t), 8))
        assert v["M"].sum() == M.sum()
        assert np.array_equal(v["r"] != 0, v["T"])       # residual footprint = T, after every transform
        assert not (v["D6"] & ~v["D6"]).any() and (v["R8"] & v["M"]).sum() == 0


def _bg(seed=1):
    bg = _textured(seed, 256, 256, 150)
    bg[:, :20] = 0; bg[:, -12:] = 255        # dark and white borders outside the cell area
    return bg


def test_targets_zones_and_area_and_exact_paste(tmp_path):
    kept, _ = _library(tmp_path)
    var = [prepare_variants(k) for k in kept]
    bg = _bg()
    area = cell_area(bg)
    for seed in range(20):
        res = compose_one(bg, kept, var, np.random.default_rng(seed))
        assert res is not None
        img, tmap, st, where = res
        M_all = np.zeros_like(tmap, bool); D1_all = M_all.copy(); D6_all = M_all.copy(); T_all = M_all.copy()
        for j, t, y, x in where:
            v = var[j][t]; h, w = v["M"].shape; win = (slice(y, y + h), slice(x, x + w))
            assert area[win][v["D6"]].all()                     # inside the eroded cell area
            assert np.median(bg[win][v["R8"]]) >= 30            # ring rule
            M_all[win] |= v["M"]; D1_all[win] |= v["D1"]; D6_all[win] |= v["D6"]; T_all[win] |= v["T"]
        assert np.array_equal(tmap == 1, M_all)
        assert np.array_equal(tmap == 2, D6_all & ~D1_all)
        assert not ((tmap != 0) & ~D6_all).any()
        assert not ((img != bg) & ~T_all).any()                 # only T pixels change
        assert st["crack_px"] == int(M_all.sum()) and st["placed"] == len(where)


def test_dark_ring_rejected(tmp_path):
    kept, _ = _library(tmp_path)
    var = [prepare_variants(k) for k in kept]
    bg = np.full((256, 256), 25, np.uint8)   # everything dark: area mask rejects (< 15 is out, 25 is in) but ring < 30
    bg[:, :8] = 0
    assert compose_one(bg, kept, var, np.random.default_rng(0)) is None


def test_dataset_deterministic_per_seed(tmp_path):
    kept, _ = _library(tmp_path)
    p = tmp_path / "bg.png"; Image.fromarray(_bg(3)).save(p)
    ds = CPDataset([p], [p], kept, get_labelsafe_augmentation(256))
    a, b, c = ds.compose(11), ds.compose(11), ds.compose(12)
    assert np.array_equal(a[0], b[0]) and np.array_equal(a[1], b[1])
    assert not (np.array_equal(a[0], c[0]) and np.array_equal(a[1], c[1]))
    it = ds[0]
    assert it["image"].shape == (1, 256, 256) and it["cp_target"].dtype == torch.long
    assert set(np.unique(it["cp_target"].numpy())) <= {0, 1, 2}


def test_cp_loss_formula():
    torch.manual_seed(0)
    logits = torch.randn(2, 24, 4, 4)
    tgt = torch.zeros(2, 4, 4, dtype=torch.long); tgt[0, 1, 1] = 1; tgt[1, 2, 2] = 2; tgt[1, 0, 0] = 1
    loss, p = cp_loss(logits, tgt, torch.tensor(10.0))
    sm = torch.softmax(logits, 1)[:, 14]
    want = (-torch.log(sm[0, 1, 1]) - torch.log(sm[1, 0, 0]) - torch.log(1 - sm[1, 2, 2])) / 10
    assert torch.allclose(loss, want, atol=1e-6) and torch.allclose(p, sm)


def test_train_py_cp_switch_default_off():
    src = (ROOT / "scripts" / "train.py").read_text()
    assert 'if cfg.get("cp"):' in src
    assert "cp:" not in (ROOT / "configs" / "base.yaml").read_text()
    tr = (ROOT / "src" / "trainers" / "trainer.py").read_text()
    assert "if self.cp_loader is not None and self.cp_lambda > 0:" in tr


def test_residual_excludes_other_crack_px_within_T(tmp_path):
    """review P3: a second crack fragment 2 px from M (rows 60 and 62: not 8-connected, so separate, and < 20 px so
    it is not a library item) must get r = 0, else its darkness lands in the ring/ignore band as not-crack."""
    img = _textured(4); msk = np.zeros((128, 128), np.uint8)
    img[60, 30:70] = 110; msk[60, 30:70] = 14            # M
    img[62, 40:50] = 110; msk[62, 40:50] = 14            # fragment 2 px below, 10 px long
    _cell(tmp_path, "B", img, msk)
    kept, rec = build_library(tmp_path / "img", tmp_path / "msk", ["B"])
    assert len(kept) == 1 and kept[0]["area"] == 40
    it = kept[0]
    # locate the fragment in the crop: the crop is the bbox of dilate(M, 8), M rows/cols known
    ys, xs = np.nonzero(it["M"])
    frag_y, frag_x0 = ys.min() + 2, xs.min() + 10
    assert np.all(it["r"][frag_y, frag_x0:frag_x0 + 10] == 0)
    assert (it["r"][it["M"]] < -20).all()
