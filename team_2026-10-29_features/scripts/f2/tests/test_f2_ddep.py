"""F2 / DDeP5: decoder denoising pretraining helpers and the opt-in model.decoder_init switch."""
import sys
from pathlib import Path

import pytest
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "scripts"))

from src.models.encoder_init import load_decoder_init  # noqa: E402
from src.models.model_factory import build_model  # noqa: E402
from pretrain_ddep import DDePNet, noised, random_crops  # noqa: E402
from pretrain_mim import step_generator  # noqa: E402

CFG = {"name": "smp_unetpp", "encoder_name": "resnet34", "encoder_weights": None, "in_channels": 1, "num_classes": 24}


def test_decoder_init_loads_decoder_only_keeps_head_encoder_rng(tmp_path):
    torch.manual_seed(0); ref = build_model(dict(CFG))
    torch.manual_seed(5); src = DDePNet("none")
    path = tmp_path / "dec.pth"; torch.save(src.decoder_file(), path)
    torch.manual_seed(0); net = build_model(dict(CFG))
    rng = torch.get_rng_state()
    msg = load_decoder_init(net, path)
    assert torch.equal(rng, torch.get_rng_state()) and "md5" in msg
    sd, rs, ss = net.state_dict(), ref.state_dict(), src.net.state_dict()
    for k in sd:
        if k.startswith("decoder."):
            assert torch.equal(sd[k], ss[k]), k
        else:  # encoder and segmentation_head: as the plain seeded build
            assert torch.equal(sd[k], rs[k]), k
    assert not torch.equal(sd["segmentation_head.0.weight"], ss["segmentation_head.0.weight"])


def test_decoder_init_strict_and_no_head(tmp_path):
    torch.manual_seed(0); src = DDePNet("none")
    f = src.decoder_file()
    assert all(k.startswith("decoder.") for k in f["models"]["model"])
    k0 = next(iter(f["models"]["model"]))
    f["models"]["model"].pop(k0)
    path = tmp_path / "bad.pth"; torch.save(f, path)
    torch.manual_seed(0); net = build_model(dict(CFG))
    with pytest.raises(RuntimeError):
        load_decoder_init(net, path)


def test_ddep_encoder_frozen_decoder_trains():
    torch.manual_seed(0); m = DDePNet("none"); m.train()
    enc0 = {k: v.clone() for k, v in m.net.encoder.state_dict().items() if "running" not in k and "num_batches" not in k}
    dec0 = {k: v.clone() for k, v in m.net.decoder.state_dict().items()}
    opt = torch.optim.Adam([p for p in m.parameters() if p.requires_grad], lr=1e-2)
    x = torch.randn(2, 1, 64, 64)
    xn, eps = noised(x, 0.95, torch.Generator().manual_seed(0))
    loss = ((m(xn) - eps) ** 2).mean(); loss.backward(); opt.step()
    assert all(p.grad is None for p in m.net.encoder.parameters())
    es = m.net.encoder.state_dict()
    assert all(torch.equal(es[k], v) for k, v in enc0.items())
    assert any(not torch.equal(m.net.decoder.state_dict()[k], v) for k, v in dec0.items())


def test_noise_formula():
    x = torch.ones(1, 1, 8, 8)
    xn, eps = noised(x, 0.95, torch.Generator().manual_seed(1))
    assert torch.allclose(xn, 0.95 ** 0.5 * x + 0.05 ** 0.5 * eps)


def test_random_crops_exact_and_deterministic():
    xb = torch.randint(0, 256, (3, 1, 64, 64), dtype=torch.uint8)
    a = random_crops(xb, 32, step_generator(0, 3)); b = random_crops(xb, 32, step_generator(0, 3))
    assert torch.equal(a, b) and a.shape == (3, 1, 32, 32)
    g = step_generator(0, 3)
    oy = torch.randint(0, 33, (3,), generator=g); ox = torch.randint(0, 33, (3,), generator=g)
    for i in range(3):
        assert torch.equal(a[i], xb[i, :, int(oy[i]):int(oy[i]) + 32, int(ox[i]):int(ox[i]) + 32])


def test_train_py_decoder_switch_default_off():
    src = (ROOT / "scripts" / "train.py").read_text()
    assert 'cfg["model"].get("decoder_init")' in src
    assert "decoder_init" not in (ROOT / "configs" / "base.yaml").read_text()
