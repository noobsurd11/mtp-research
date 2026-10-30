"""F1 / MIM5: SparK-style sparse emulation, loss, pretraining helpers, and the opt-in model.encoder_init switch."""
import os
import sys
from pathlib import Path

import pytest
import torch
import torch.nn as nn

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "scripts"))

import segmentation_models_pytorch as smp  # noqa: E402

from src.models.encoder_init import load_encoder_init  # noqa: E402
from src.models.model_factory import build_model  # noqa: E402
from src.pretrain.spark import (SparKResNet, SparseBatchNorm2d, SparseConv2d, active_mask, densify_,  # noqa: E402
                                mask_at, sparsify_)
from pretrain_mim import augment, enc_lr_factor, encoder_file, epoch_order, lr_at, step_generator  # noqa: E402
import build_mim_pool  # noqa: E402

CFG = {"name": "smp_unetpp", "encoder_name": "resnet34", "encoder_weights": None, "in_channels": 1, "num_classes": 24}


def enc(seed=0):
    torch.manual_seed(seed)
    return smp.encoders.get_encoder("resnet34", in_channels=1, depth=5, weights=None)


def rand_mask(b, g, ratio=0.6, seed=0):
    m = torch.rand(b, 1, g, g, generator=torch.Generator().manual_seed(seed)) > ratio
    m[:, :, 0, 0] = True
    return m


# ---------- sparse emulation ----------
def test_sparsify_keeps_keys_and_roundtrips():
    e = enc(); keys = list(e.state_dict().keys())
    n = sparsify_(e)
    assert n > 0 and list(e.state_dict().keys()) == keys
    assert any(isinstance(m, SparseConv2d) for m in e.modules())
    assert densify_(e) == n
    assert not any(isinstance(m, (SparseConv2d, SparseBatchNorm2d)) for m in e.modules())


@pytest.mark.parametrize("train", [True, False])
def test_all_visible_equals_dense(train):
    torch.manual_seed(1)
    d, s = enc(), enc()
    sparsify_(s)
    d.train(train); s.train(train)
    x = torch.randn(2, 1, 64, 64)
    with active_mask(torch.ones(2, 1, 2, 2, dtype=torch.bool)):
        fs = s(x)
    fd = d(x)
    for a, b in zip(fd, fs):
        assert torch.allclose(a, b, atol=1e-4, rtol=1e-4)
    if train:
        for (ka, a), (kb, b) in zip(d.state_dict().items(), s.state_dict().items()):
            assert ka == kb and torch.allclose(a.float(), b.float(), atol=1e-5, rtol=1e-4), ka


@pytest.mark.parametrize("train,patch", [(True, 32), (False, 32), (True, 16)])
def test_masked_pixels_never_reach_encoder(train, patch):
    s = enc(); sparsify_(s); s.train(train)
    g = 128 // patch
    m = rand_mask(2, g, seed=3)
    x1 = torch.randn(2, 1, 128, 128)
    up = m.float().repeat_interleave(patch, 2).repeat_interleave(patch, 3)
    x2 = x1 * up + torch.randn_like(x1) * 5 * (1 - up)  # differs only inside masked patches
    st0 = {k: v.clone() for k, v in s.state_dict().items()}
    with active_mask(m):
        f1 = s(x1 * mask_at(128, 128))
    s.load_state_dict(st0)
    with active_mask(m):
        f2 = s(x2 * mask_at(128, 128))
    for a, b in zip(f1[1:], f2[1:]):
        assert torch.equal(a, b)
    # masked positions are exactly zero at stride 32 (patch 32) / where all children are masked (patch 16)
    with active_mask(m):
        m32 = mask_at(*f1[-1].shape[-2:])
    assert torch.all(f1[-1] * (1 - m32) == 0)


def test_sparse_bn_stats_visible_only():
    bn = SparseBatchNorm2d(3); bn.train()
    x = torch.randn(2, 3, 8, 8)
    m = rand_mask(2, 2, seed=5)
    with active_mask(m):
        mm = mask_at(8, 8).bool().expand_as(x)
        y = bn(x)
    vis = x.permute(1, 0, 2, 3)[mm.permute(1, 0, 2, 3)].view(3, -1)
    ref = (vis - vis.mean(1, keepdim=True)) / torch.sqrt(vis.var(1, unbiased=False, keepdim=True) + bn.eps)
    got = y.permute(1, 0, 2, 3)[mm.permute(1, 0, 2, 3)].view(3, -1)
    assert torch.allclose(got, ref, atol=1e-5)
    assert torch.all(y[~mm] == 0)
    assert torch.allclose(bn.running_mean, 0.1 * vis.mean(1), atol=1e-6)
    assert torch.allclose(bn.running_var, 0.9 + 0.1 * vis.var(1, unbiased=True), atol=1e-5)


# ---------- model, loss ----------
def small_spark(patch=32):
    e = enc()
    return SparKResNet(e, list(e.out_channels)[2:], width=64, patch=patch, mask_ratio=0.6)


def test_random_mask_exact_count():
    sp = small_spark()
    m = sp.random_mask(5, 512, 512, generator=torch.Generator().manual_seed(0))
    assert m.shape == (5, 1, 16, 16) and m.dtype == torch.bool
    assert (m.flatten(1).sum(1) == round(256 * 0.4)).all()


def test_forward_shapes_and_loss_only_on_masked():
    sp = small_spark().eval()
    x = torch.randn(2, 1, 128, 128)
    m = sp.random_mask(2, 128, 128, generator=torch.Generator().manual_seed(1))
    loss, rec = sp(x, m)
    assert rec.shape == x.shape and torch.isfinite(loss)
    up = m.float().repeat_interleave(32, 2).repeat_interleave(32, 3)
    rec2 = rec + torch.randn_like(rec) * up  # change visible patches only
    assert torch.allclose(sp.loss(x, rec, m), sp.loss(x, rec2, m))
    rec3 = rec + torch.randn_like(rec) * (1 - up)
    assert not torch.allclose(sp.loss(x, rec, m), sp.loss(x, rec3, m))


def test_backward_reaches_encoder_and_tokens():
    sp = small_spark().train()
    x = torch.randn(2, 1, 64, 64)
    m = sp.random_mask(2, 64, 64, generator=torch.Generator().manual_seed(2))
    loss, _ = sp(x, m); loss.backward()
    assert sp.encoder.conv1.weight.grad.abs().sum() > 0
    assert all(t.grad is not None for t in sp.mask_tokens)


def test_encoder_state_loads_into_unetpp():
    sp = small_spark()
    sd = sp.encoder_state_dict()
    torch.manual_seed(0); net = build_model(dict(CFG))
    enc_sd = {k[len("encoder."):]: v for k, v in sd.items()}
    net.encoder.load_state_dict(enc_sd, strict=True)


# ---------- pretraining helpers ----------
def test_augment_deterministic_and_label_safe():
    xb = torch.randint(0, 256, (6, 1, 32, 32), dtype=torch.uint8)
    a = augment(xb, step_generator(0, 7), p_jitter=0.0)
    b = augment(xb, step_generator(0, 7), p_jitter=0.0)
    c = augment(xb, step_generator(0, 8), p_jitter=0.0)
    assert torch.equal(a, b) and not torch.equal(a, c)
    raw = (xb.float() / 255 - 0.5) / 0.25
    for i in range(6):  # pure pixel permutation: same sorted values
        assert torch.equal(a[i].flatten().sort().values, raw[i].flatten().sort().values)


def test_epoch_order_and_lr():
    assert torch.equal(epoch_order(0, 3, 50), epoch_order(0, 3, 50))
    assert not torch.equal(epoch_order(0, 3, 50), epoch_order(0, 4, 50))
    assert lr_at(0, 100, 10, 1.0, 0.0) == pytest.approx(0.1)
    assert lr_at(9, 100, 10, 1.0, 0.0) == pytest.approx(1.0)
    assert lr_at(100, 100, 10, 1.0, 0.0) == pytest.approx(0.0, abs=1e-9)


# ---------- model.encoder_init ----------
def test_encoder_init_loads_exactly_and_keeps_decoder_and_rng(tmp_path):
    torch.manual_seed(0); ref = build_model(dict(CFG))
    src = enc(seed=9)
    path = tmp_path / "enc.pth"
    torch.save({f"encoder.{k}": v for k, v in src.state_dict().items()}, path)
    torch.manual_seed(0); net = build_model(dict(CFG))
    rng = torch.get_rng_state()
    msg = load_encoder_init(net, path)
    assert torch.equal(rng, torch.get_rng_state())
    assert "md5" in msg
    for k, v in src.state_dict().items():
        assert torch.equal(net.encoder.state_dict()[k], v)
    rs, ns = ref.state_dict(), net.state_dict()
    for k in rs:
        if not k.startswith("encoder."):
            assert torch.equal(rs[k], ns[k]), k


def test_encoder_init_strict(tmp_path):
    src = enc()
    sd = {f"encoder.{k}": v for k, v in src.state_dict().items()}
    sd.pop("encoder.layer4.1.bn2.weight")
    path = tmp_path / "bad.pth"; torch.save(sd, path)
    torch.manual_seed(0); net = build_model(dict(CFG))
    with pytest.raises(RuntimeError):
        load_encoder_init(net, path)


def test_train_py_switch_default_off():
    src = (ROOT / "scripts" / "train.py").read_text()
    assert 'cfg["model"].get("encoder_init")' in src
    assert "encoder_init" not in (ROOT / "configs" / "base.yaml").read_text()


@pytest.mark.skipif(os.environ.get("F1_IMAGENET", "0") != "1", reason="needs cached ImageNet weights (F1_IMAGENET=1)")
def test_get_encoder_equals_unetpp_imagenet_encoder():
    a = smp.encoders.get_encoder("resnet34", in_channels=1, depth=5, weights="imagenet")
    torch.manual_seed(0)
    b = smp.UnetPlusPlus(encoder_name="resnet34", encoder_weights="imagenet", in_channels=1, classes=24).encoder
    sa, sb = a.state_dict(), b.state_dict()
    assert sa.keys() == sb.keys() and all(torch.equal(sa[k], sb[k]) for k in sa)


# ---------- v1 additions (review_mim5_v0 C1, C2, C6) ----------
def test_enc_lr_factor_ramp():
    assert enc_lr_factor(0, 10, 1000) == 0.0 and enc_lr_factor(9, 10, 1000) == 0.0
    assert enc_lr_factor(10, 10, 1000) == pytest.approx(1 / 1000)
    assert enc_lr_factor(1009, 10, 1000) == pytest.approx(1.0) and enc_lr_factor(5000, 10, 1000) == 1.0


def test_encoder_file_roundtrip_is_identity(tmp_path):
    """mim_step0.pth path: saving the start encoder and loading it with encoder_init changes nothing (I2 on CPU)."""
    torch.manual_seed(0); ref = build_model(dict(CFG))
    e = enc(); sp = SparKResNet(e, list(e.out_channels)[2:], width=64)
    sp.encoder.load_state_dict(ref.encoder.state_dict())
    path = tmp_path / "step0.pth"; torch.save(encoder_file(sp), path)
    torch.manual_seed(0); net = build_model(dict(CFG))
    load_encoder_init(net, path)
    rs, ns = ref.state_dict(), net.state_dict()
    assert all(torch.equal(rs[k], ns[k]) for k in rs)


def _toy_data(root):
    sp = root / "splits"; sp.mkdir(parents=True)
    (sp / "train.txt").write_text("".join(f"CFVS_0000{i}_r1_c1\n" for i in range(1, 9)))
    (sp / "d7_twin_train_cells.txt").write_text("".join(f"CFVS_0000{i}_r1_c1\n" for i in range(1, 8)))
    (sp / "val.txt").write_text("ARTS_00050_r3_c5\n")
    (sp / "test.txt").write_text("ARTS_00047_r3_c1\n")
    ext = ["ARTS_00047_r9_c9", "ARTS_00034_r3_c1", "CSIR_00299_r8_c6", "CSIR_00100_r1_c1", "CSIR_00101_r1_c1",
           "CSIR_00102_r1_c1", "CSIR_00103_r1_c1", "CSIR_00104_r1_c1"]
    (sp / "external_unlabeled.txt").write_text("".join(x + "\n" for x in ext))
    rows = ["stem,source,split_20221008,in_external_pool,crack_px,inactive_px,remapped_px"]
    rows += [f"CSIR_00298_r8_c{k},CSIR,train,0,0,0,0" for k in range(106)] + ["CSIR_00104_r1_c1,CSIR,train,1,0,0,0"]
    rows += [f"CSIR_0090{k}_r1_c1,CSIR,train,1,0,0,0" for k in range(10)]
    (root / "man.csv").write_text("\n".join(rows) + "\n")
    nd = {"hp_pairs": [{"q": "ARTS_00047_r3_c1", "split": "test", "pool": "ARTS_00034_r3_c1", "r_hp": 0.93},
                       {"q": "ARTS_00050_r3_c5", "split": "val", "pool": "CSIR_00100_r1_c1", "r_hp": 0.80},
                       {"q": "CFVS_00001_r1_c1", "split": "train", "pool": "CSIR_00101_r1_c1", "r_hp": 0.97},
                       {"q": "CFVS_00008_r1_c1", "split": "train", "pool": "CSIR_00102_r1_c1", "r_hp": 0.99}]}
    import json
    (root / "nd.json").write_text(json.dumps(nd))
    (root / "sp.json").write_text(json.dumps([["test", "ARTS_00047_r3_c1", "CSIR_00103_r1_c1", 0.86]]))
    return root


def test_pool_builder_rules(tmp_path):
    r = _toy_data(tmp_path)
    rels, mon, info = build_mim_pool.build(r, r / "man.csv", [], r / "nd.json", r / "sp.json", 0.85, 0.95, 0)
    kept = {x.split("/")[-1][:-4] for x in rels}
    assert "ARTS_00047_r9_c9" not in kept            # R1: test module ARTS_00047
    assert "CSIR_00299_r8_c6" in kept                 # E1 module is CSIR_00298, not 00299
    assert "CSIR_00104_r1_c1" not in kept             # R2: an ext117 stem in the pool
    assert "ARTS_00034_r3_c1" not in kept             # R3: hp 0.93 to a test cell
    assert "CSIR_00100_r1_c1" in kept                 # 0.80 < 0.85
    assert "CSIR_00103_r1_c1" not in kept             # R3 via samepos 0.86
    assert "CSIR_00101_r1_c1" not in kept             # R4: copy of a D7 twin
    assert "CSIR_00102_r1_c1" in kept                 # CFVS_00008 is not a twin
    assert "CFVS_00008_r1_c1" in kept and "CFVS_00001_r1_c1" not in kept
    assert info["per_rule"]["R1_module"] == 1 and info["total"] == len(rels) == 4


def test_pool_builder_monitor_disjoint(tmp_path):
    r = _toy_data(tmp_path)
    rels, mon, info = build_mim_pool.build(r, r / "man.csv", [], r / "nd.json", r / "sp.json", 0.85, 0.95, 2, 0)
    assert len(mon) == 2 and not set(mon) & set(rels) and info["monitor"] == 2
    rels2, mon2, _ = build_mim_pool.build(r, r / "man.csv", [], r / "nd.json", r / "sp.json", 0.85, 0.95, 2, 0)
    assert mon == mon2 and rels == rels2
