"""Thin worktree: Skeleton Recall and clDice on the crack class (src/losses/thin_crack.py, src/data/skeleton.py).

Checks: the numpy skeletonizer reproduces scikit-image's skeletonize on toy masks (expected outputs generated with
scikit-image 0.26 on the laptop, which matched it on 400 random blobs and 423 E-SCDD crack masks) and keeps the
number of 8-connected components; the tubed skeleton; both losses ~0 on a perfect prediction; gradients flow (Skeleton
Recall only at tube pixels); absent crack; ignore pixels; the factory builds nothing new with the switches absent or 0;
the trainer passes ``skel_tube`` and logs the terms on their own line; the data wrapper leaves image and mask unchanged.
"""
import logging
import sys
from pathlib import Path

import numpy as np
import pytest
import torch
from PIL import Image
from scipy import ndimage as ndi

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.data.augmentations import get_labelsafe_augmentation  # noqa: E402
from src.data.benchmark_el import BenchmarkELDataset  # noqa: E402
from src.data.skeleton import diamond, skeletonize_2d, tubed_skeleton  # noqa: E402
from src.data.stream import BatchStream  # noqa: E402
from src.data.thin_targets import TubedSkeletonDataset  # noqa: E402
from src.losses.ce_dice import CEDiceLoss  # noqa: E402
from src.losses.loss_factory import build_losses  # noqa: E402
from src.losses.thin_crack import (ThinCrackLoss, skeleton_recall_loss, soft_cldice_loss, soft_skel,  # noqa: E402
                                   tubes_from_targets)
from src.trainers.trainer import Trainer  # noqa: E402
from tests.test_ssl_split import TinySmp  # noqa: E402

S8 = np.ones((3, 3), bool)


# ---------------- skeleton ----------------
def _toys():
    X, Y = np.ogrid[0:9, 0:9]
    t = {"ellipse": (1. / 3 * (X - 4) ** 2 + (Y - 4) ** 2 < 3 ** 2)}
    a = np.zeros((7, 12), bool); a[2:5, 1:11] = 1; t["bar3"] = a
    b = np.zeros((9, 9), bool); b[1:8, 1:8] = 1; t["square7"] = b
    t["sq2"] = np.pad(np.ones((2, 2), bool), 2)
    d = np.zeros((14, 14), bool)
    for k in range(1, 12):
        d[k, k - 1:k + 2] = 1
    t["diag3"] = d
    y, x = np.ogrid[-8:9, -8:9]; t["ring"] = ((y ** 2 + x ** 2) <= 49) & ((y ** 2 + x ** 2) >= 16)
    L = np.zeros((16, 16), bool); L[2:14, 2:5] = 1; L[11:14, 2:14] = 1; t["L"] = L
    return t


# scikit-image 0.26 skeletonize() of the toys above (the ellipse is skimage's own docstring example)
SKIMAGE = {
    "ellipse": [(3, 4), (4, 4), (5, 4), (6, 4)],
    "bar3": [(2, 9), (3, 1), (3, 2), (3, 3), (3, 4), (3, 5), (3, 6), (3, 7), (3, 8)],
    "square7": [(3, 4), (3, 5), (4, 3)],
    "sq2": [(2, 2), (2, 3)],
    "diag3": [(1, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10), (11, 11),
              (11, 12)],
    "ring": [(3, 6), (3, 7), (3, 8), (3, 9), (3, 10), (4, 5), (4, 11), (5, 4), (5, 12), (6, 3), (6, 13), (7, 3),
             (7, 13), (8, 3), (8, 13), (9, 3), (9, 13), (10, 3), (10, 13), (11, 4), (11, 12), (12, 5), (12, 11),
             (13, 6), (13, 7), (13, 8), (13, 9), (13, 10)],
    "L": [(2, 3), (3, 3), (4, 3), (5, 3), (6, 3), (7, 3), (8, 3), (9, 3), (10, 3), (11, 3), (11, 12), (12, 4), (12, 5),
          (12, 6), (12, 7), (12, 8), (12, 9), (12, 10), (12, 11)],
}


@pytest.mark.parametrize("name", sorted(SKIMAGE))
def test_skeleton_matches_skimage_on_toys(name):
    a = _toys()[name]
    s = skeletonize_2d(a)
    assert sorted(map(tuple, np.argwhere(s).tolist())) == SKIMAGE[name]
    assert not (s & ~a).any()  # inside the mask


def test_skeleton_edge_cases():
    assert not skeletonize_2d(np.zeros((5, 7), bool)).any()
    line = np.zeros((9, 20), bool); line[4, 2:18] = 1
    assert np.array_equal(skeletonize_2d(line), line)  # a 1-px line is its own skeleton
    dot = np.zeros((5, 5), bool); dot[2, 2] = 1
    assert np.array_equal(skeletonize_2d(dot), dot)
    edge = np.zeros((6, 10), bool); edge[0:3, :] = 1  # touches the border: outside counts as background
    s = skeletonize_2d(edge)
    assert s.any() and ndi.label(s, S8)[1] == 1
    big = np.zeros((40, 50), bool); big[30:33, 5:45] = 1  # bounding-box crop gives the full-image result
    assert np.array_equal(skeletonize_2d(big)[30:33, 5:45], skeletonize_2d(big[29:34, 4:46])[1:4, 1:41])


def test_skeleton_keeps_components_and_ring_hole():
    rng = np.random.default_rng(1)
    for _ in range(60):
        h, w = rng.integers(10, 60, 2)
        a = ndi.gaussian_filter(rng.random((h, w)), rng.uniform(0.7, 4)) > rng.uniform(0.45, 0.6)
        s = skeletonize_2d(a)
        assert ndi.label(a, S8)[1] == ndi.label(s, S8)[1]
        assert not (s & ~a).any()
    ring = skeletonize_2d(_toys()["ring"])
    assert ndi.label(ring, S8)[1] == 1 and ndi.label(~ring)[1] == 2  # closed loop: inside and outside stay apart


def test_tubed_skeleton():
    m = np.zeros((20, 30), np.int64); m[5:12, 3:27] = 14  # 7-px-wide crack bar
    m[0, 0] = 255  # ignore px
    sk = skeletonize_2d(m == 14)
    tube = tubed_skeleton(m, 14, 2)
    assert tube.dtype == np.uint8 and set(np.unique(tube)) <= {0, 1}
    assert not (tube.astype(bool) & (m != 14)).any()  # clipped to the crack mask
    assert (tube.astype(bool) | ~sk).all()  # contains the skeleton
    col = tube[:, 15]
    assert col.sum() == 5 and col[6:11].all()  # mid-bar: skeleton row 8 +- 2
    assert np.array_equal(tube, (ndi.binary_dilation(sk, structure=diamond(2)) & (m == 14)).astype(np.uint8))
    thin = np.zeros((10, 10), np.int64); thin[3, 1:9] = 14
    assert np.array_equal(tubed_skeleton(thin, 14, 2), (thin == 14).astype(np.uint8))  # 1-px crack: tube = crack
    assert not tubed_skeleton(np.zeros((8, 8), np.int64), 14).any()
    assert np.array_equal(tubed_skeleton(m, 14, 0), (sk & (m == 14)).astype(np.uint8))
    assert int(diamond(2).sum()) == 13


# ---------------- losses ----------------
def _crack_batch(seed=0, c=24, cls=14, n=2, h=32, w=32):
    g = torch.Generator().manual_seed(seed)
    t = torch.zeros(n, h, w, dtype=torch.long)
    t[0, 10:13, 2:30] = cls  # 3-px crack
    t[0, 4:28, 20] = cls      # 1-px crack
    t[1, 5:9, 5:25] = 3       # another class, no crack in image 1
    logits = torch.randn(n, c, h, w, generator=g)
    return logits, t


def _perfect(t, c=24):
    return torch.nn.functional.one_hot(t, c).permute(0, 3, 1, 2).float() * 30.0


def test_losses_near_zero_on_perfect_prediction():
    _, t = _crack_batch()
    p = torch.softmax(_perfect(t), 1)[:, 14:15]
    y = (t == 14).float()[:, None]
    tube = tubes_from_targets(t, 14, 2)[:, None]
    assert float(skeleton_recall_loss(p, tube)) < 1e-6
    assert float(soft_cldice_loss(p, y, iters=5)) < 1e-4
    assert float(soft_cldice_loss(y, y, iters=5)) < 1e-6
    # and clearly positive on a bad prediction (crack probability ~0)
    assert float(skeleton_recall_loss(torch.zeros_like(p), tube)) > 0.99
    assert float(soft_cldice_loss(torch.zeros_like(p), y, iters=5)) > 0.9


def test_soft_skel_of_binary_line_and_bar():
    y = torch.zeros(1, 1, 16, 16); y[0, 0, 7, 2:14] = 1  # 1-px line: its own soft skeleton
    assert torch.equal(soft_skel(y, 5), y)
    b = torch.zeros(1, 1, 16, 16); b[0, 0, 6:9, 2:14] = 1
    s = soft_skel(b, 5)
    assert float(s.sum()) > 0 and not bool((s * (1 - b)).any())  # non-empty, inside the bar


@pytest.mark.parametrize("which", ["srec", "cldice"])
def test_gradients_flow(which):
    logits, t = _crack_batch()
    logits.requires_grad_(True)
    p = torch.softmax(logits.float(), 1)[:, 14:15]
    if which == "srec":
        tube = tubes_from_targets(t, 14, 2)[:, None]
        loss = skeleton_recall_loss(p, tube)
    else:
        loss = soft_cldice_loss(p, (t == 14).float()[:, None], iters=5)
    loss.backward()
    g = logits.grad
    assert torch.isfinite(g).all() and float(g[:, 14].abs().sum()) > 0
    if which == "srec":  # only tube pixels carry gradient, and it raises the crack logit there
        tube = tubes_from_targets(t, 14, 2).bool()
        assert g.abs().sum(1)[~tube].max() == 0
        assert (g[:, 14][tube] < 0).all()


def test_absent_crack_and_ignore():
    logits, t = _crack_batch()
    t0 = t.clone(); t0[t0 == 14] = 0
    p = torch.softmax(logits, 1)[:, 14:15].requires_grad_(True)
    ls = skeleton_recall_loss(p, tubes_from_targets(t0, 14, 2)[:, None])
    assert float(ls.detach()) == 0.0  # empty tube: (0 + s) / (0 + s) = 1
    ls.backward(); assert p.grad.abs().max() == 0
    # ignore px: logits there do not change either term (they are masked out of p and y)
    base = CEDiceLoss()
    loss = ThinCrackLoss(base, srec_weight=1.0, cldice_weight=1.0)
    ti = t.clone(); ti[:, :, :3] = 255
    a = logits.clone(); b = logits.clone(); b[:, :, :, :3] = torch.randn(2, 24, 32, 3) * 5
    loss(a, ti); ta = {k: float(v) for k, v in loss.last_terms.items()}
    loss(b, ti); tb = {k: float(v) for k, v in loss.last_terms.items()}
    assert ta == pytest.approx(tb, abs=1e-6)


def test_zero_crack_batch_and_float32_under_autocast():
    logits, t = _crack_batch()
    t0 = t.clone(); t0[t0 == 14] = 0  # no crack anywhere in the batch
    lg = logits.clone().requires_grad_(True)
    loss = ThinCrackLoss(CEDiceLoss(), srec_weight=1.0, cldice_weight=1.0, cldice_iters=10)
    v = loss(lg, t0)
    assert float(loss.last_terms["loss_srec"]) == 0.0  # empty tube: exactly 0
    lc = float(loss.last_terms["loss_cldice"])
    assert np.isfinite(lc) and 0.0 <= lc < 1.0  # finite; the smoothed form penalises predicted crack skeleton mass
    v.backward()
    assert torch.isfinite(lg.grad).all()
    with torch.autocast(device_type="cpu", dtype=torch.bfloat16):
        loss(logits.bfloat16(), t)
    assert all(x.dtype == torch.float32 for x in loss.last_terms.values())


def test_wrapper_is_base_plus_weighted_terms():
    logits, t = _crack_batch()
    base = CEDiceLoss()
    ref = base(logits, t)
    for ws, wc in [(1.0, 0.0), (0.0, 1.0), (0.3, 0.7)]:
        loss = ThinCrackLoss(base, srec_weight=ws, cldice_weight=wc, cldice_iters=5)
        v = loss(logits, t)
        terms = loss.last_terms
        expect = ref + ws * terms.get("loss_srec", 0.0) + wc * terms.get("loss_cldice", 0.0)
        assert torch.allclose(v, expect, atol=1e-7, rtol=0)
        assert set(terms) == ({"loss_srec"} if ws else set()) | ({"loss_cldice"} if wc else set())
    tube = tubes_from_targets(t, 14, 2)
    l1 = ThinCrackLoss(base, srec_weight=1.0)
    assert torch.equal(l1(logits, t, tube=tube), l1(logits, t))  # precomputed tube = on-the-fly tube
    with pytest.raises(ValueError):
        ThinCrackLoss(base)


def test_factory_off_on():
    house = {"supervised": "ce_dice", "consistency": None}
    for cfg in (house, {**house, "skel_recall": {"weight": 0}}, {**house, "cldice": {"weight": 0.0}}):
        sup = build_losses(cfg, None)["supervised"]
        assert type(sup) is CEDiceLoss
    sup = build_losses({**house, "skel_recall": {"weight": 1.0}}, None)["supervised"]
    assert isinstance(sup, ThinCrackLoss) and sup.needs_tube and sup.srec_weight == 1.0 and sup.srec_radius == 2
    assert sup.criterion is sup.base.criterion and sup.weight is None
    sup = build_losses({**house, "cldice": {"weight": 1.0, "iters": 7}}, None)["supervised"]
    assert isinstance(sup, ThinCrackLoss) and not sup.needs_tube and sup.cldice_iters == 7
    with pytest.raises(ValueError):
        build_losses({"supervised": "ce", "consistency": None, "cldice": {"weight": 1.0}}, None)


# ---------------- trainer ----------------
def _trainer(tmp_path, name, loss):
    torch.manual_seed(0)
    model = TinySmp()
    cfg = {"seed": 0, "method": "supervised", "model": {"num_classes": 3, "name": "tiny"},
           "training": {"total_steps": 10, "lr": 1e-2, "lr_scheduler": "constant", "warmup_steps": 0, "amp": False,
                        "gradient_clip": 1.0}}
    return Trainer(model, torch.optim.Adam(model.parameters(), lr=1e-2), {"supervised": loss}, labeled_loader=None,
                   val_loader=None, test_loader=None, cfg=cfg, device=torch.device("cpu"), run_dir=tmp_path / name)


def _sup_batches(n=3, tube=False):
    g = torch.Generator().manual_seed(1)
    for _ in range(n):
        x = torch.randn(4, 1, 16, 16, generator=g)
        m = torch.randint(0, 3, (4, 16, 16), generator=g)
        b = {"image": x, "mask": m}
        if tube:
            b["skel_tube"] = tubes_from_targets(m, 1, 2)
        yield b


def test_trainer_house_path_unchanged_and_thin_path(tmp_path):
    house = _trainer(tmp_path, "h", CEDiceLoss(dice_classes=(1, 2)))
    assert not house.thin_on and not house.thin_tube
    tubed = _trainer(tmp_path, "h2", CEDiceLoss(dice_classes=(1, 2)))
    for step, (a, b) in enumerate(zip(_sup_batches(), _sup_batches(tube=True))):
        oa = house._train_step(step, iter([a]), None)
        ob = tubed._train_step(step, iter([b]), None)  # an extra batch key is ignored by the house path
        assert oa == ob and set(oa) == {"loss", "loss_sup", "loss_con", "lambda"}
    sr = _trainer(tmp_path, "sr", ThinCrackLoss(CEDiceLoss(dice_classes=(1, 2)), crack_class=1, srec_weight=1.0))
    assert sr.thin_on and sr.thin_tube
    seen = []
    orig = sr.sup_criterion.forward
    sr.sup_criterion.forward = lambda lg, t, tube=None: (seen.append(tube is not None), orig(lg, t, tube=tube))[1]
    for step, b in enumerate(_sup_batches(tube=True)):
        out = sr._train_step(step, iter([b]), None)
        assert set(out) == {"loss", "loss_sup", "loss_con", "lambda"}  # the step line keeps its keys
    assert seen == [True] * 3 and len(sr._thin_window) == 3 and set(sr._thin_window[0]) == {"loss_srec"}
    cl = _trainer(tmp_path, "cl", ThinCrackLoss(CEDiceLoss(dice_classes=(1, 2)), crack_class=1, cldice_weight=1.0))
    assert cl.thin_on and not cl.thin_tube
    for step, b in enumerate(_sup_batches()):
        cl._train_step(step, iter([b]), None)
    assert set(cl._thin_window[0]) == {"loss_cldice"} and all(np.isfinite(w["loss_cldice"]) for w in cl._thin_window)


def test_trainer_refuses_thin_with_ssl(tmp_path):
    from src.losses.confidence_ce import ConfidenceCELoss
    model = TinySmp()
    cfg = {"seed": 0, "method": "mean_teacher", "model": {"num_classes": 3},
           "training": {"total_steps": 10, "lr": 1e-2, "lr_scheduler": "constant", "warmup_steps": 0, "amp": False},
           "ssl": {"ema_alpha": 0.9, "warmup_steps": 0, "ramp_steps": 1, "lambda_final": 0.0}}
    losses = {"supervised": ThinCrackLoss(CEDiceLoss(dice_classes=(1, 2)), crack_class=1, cldice_weight=1.0),
              "consistency": ConfidenceCELoss(t_pos=0.9)}
    with pytest.raises(ValueError):
        Trainer(model, torch.optim.Adam(model.parameters()), losses, labeled_loader=None, val_loader=None,
                test_loader=None, cfg=cfg, device=torch.device("cpu"), run_dir=tmp_path / "x",
                unlabeled_loader=object())


# ---------------- data wrapper ----------------
def test_wrapper_keeps_stream_images_and_masks(tmp_path):
    rng = np.random.default_rng(0)
    stems = [f"c{i}" for i in range(6)]
    for s in stems:
        m = np.zeros((32, 32), np.uint8); m[rng.integers(2, 28), 3:29] = 14; m[5:9, 5:9] = 11
        Image.fromarray(m, mode="L").save(tmp_path / f"{s}.png")
    img_dir = tmp_path / "img"; img_dir.mkdir()
    for s in stems:
        Image.fromarray(rng.integers(0, 256, (32, 32)).astype(np.uint8), mode="L").save(img_dir / f"{s}.png")
    aug = lambda: get_labelsafe_augmentation(32, [0.5], [0.25])  # noqa: E731
    plain = BatchStream(BenchmarkELDataset(img_dir, tmp_path, stems, aug()), 2, seed=3, stream_id=0, num_workers=0,
                        pin_memory=False)
    wrapped = BatchStream(TubedSkeletonDataset(BenchmarkELDataset(img_dir, tmp_path, stems, aug()), 14, 2), 2, seed=3,
                          stream_id=0, num_workers=0, pin_memory=False)
    ia, ib = plain.iterate(0), wrapped.iterate(0)
    for _ in range(7):
        a, b = next(ia), next(ib)
        assert torch.equal(a["image"], b["image"]) and torch.equal(a["mask"], b["mask"]) and a["stem"] == b["stem"]
        assert b["skel_tube"].dtype == torch.uint8 and b["skel_tube"].shape == b["mask"].shape
        assert torch.equal(b["skel_tube"], tubes_from_targets(b["mask"], 14, 2))  # tube of the augmented mask


def test_thin_switches_off_in_configs():
    root = Path(__file__).resolve().parent.parent
    for f in (root / "configs").glob("*.yaml"):
        txt = f.read_text()
        assert "skel_recall" not in txt and "cldice" not in txt and "scuff_class" not in txt, f


class _Stream:
    def __init__(self, tube):
        self.tube = tube

    def iterate(self, start=0):
        def gen():
            while True:
                yield from _sup_batches(1, tube=self.tube)
        return gen()


def test_thin_log_line_in_fit(tmp_path, caplog):
    tr = _trainer(tmp_path, "fit", ThinCrackLoss(CEDiceLoss(dice_classes=(1, 2)), crack_class=1, srec_weight=1.0,
                                                 cldice_weight=0.5))
    tr.labeled_loader = _Stream(tube=True)
    tr.test_loader = list(_sup_batches(1))
    tr.metric_kw = {"crack_class": None}
    tr.total_steps, tr.log_every, tr.ckpt_every = 4, 2, 100
    with caplog.at_level(logging.INFO):
        tr.fit()
    lines = [r.getMessage() for r in caplog.records]
    thin = [m for m in lines if m.startswith("thin ")]
    step = [m for m in lines if m.startswith("step ")]
    assert len(thin) == 2 and thin[0].startswith("thin loss_srec=") and "loss_cldice=" in thin[0]
    assert thin[0].endswith("at step 2") and thin[1].endswith("at step 4")
    assert all("srec" not in m and "cldice" not in m for m in step)  # the step line keeps the house keys
