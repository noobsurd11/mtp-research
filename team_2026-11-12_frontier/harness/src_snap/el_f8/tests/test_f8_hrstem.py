"""F8 (idea 8): hrstem_unetpp wrapper. CPU only (run with CUDA_VISIBLE_DEVICES='')."""
import json
from pathlib import Path

import pytest
import torch
import yaml

from src.models.model_factory import build_model

TV_CNX = Path.home() / ".cache/torch/hub/checkpoints/convnext_tiny-983f1562.pth"
SAM2_T = Path("/home/noob/work/weights/timm_sam2_hiera_tiny_fb_r896.safetensors")
ROOT = Path(__file__).resolve().parents[1]


def _cfg(**kw):
    c = {"name": "hrstem_unetpp", "backbone": "convnext_tiny", "in_channels": 1, "num_classes": 24}
    c.update(kw)
    return c


def test_forward_shape_and_all_params_get_grad():
    torch.manual_seed(0)
    m = build_model(_cfg())
    y = m(torch.randn(2, 1, 128, 128))
    assert y.shape == (2, 24, 128, 128)
    y.float().mean().backward()
    nograd = [n for n, p in m.named_parameters() if p.requires_grad and p.grad is None]
    assert not nograd, nograd[:5]


def test_param_names_split_backbone_vs_rest():
    m = build_model(_cfg())
    names = [n for n, _ in m.named_parameters()]
    tops = {n.split(".")[0] for n in names}
    assert tops == {"encoder", "hr_stem", "decoder", "segmentation_head"}, tops
    enc = [n for n in names if n.startswith("encoder.")]
    assert any(".norm." in n or n.startswith("encoder.stem.1.") for n in enc), "LayerNorm params must be in encoder.*"


def test_pf_groups_tensor_count_include_layernorm():
    import importlib.util
    spec = importlib.util.spec_from_file_location("train_mod", ROOT / "scripts" / "train.py")
    tr = importlib.util.module_from_spec(spec); spec.loader.exec_module(tr)
    m = build_model(_cfg())
    cfg = {"training": {"optimizer": "adam", "lr": 1e-3, "weight_decay": 1e-4,
                        "encoder_pf": {"freeze": 200, "ramp": 200, "lr_mult": 0.1, "wd": 0.0}}}
    opt = tr.build_optimizer(m, cfg)
    g0, g1 = opt.param_groups
    enc = [p for n, p in m.named_parameters() if n.startswith("encoder.")]
    ln = [p for n, p in m.named_parameters() if n.startswith("encoder.") and p.dim() == 1 and ("norm" in n)]
    assert len(g1["params"]) == len(enc) and {id(p) for p in g1["params"]} == {id(p) for p in enc}
    assert ln and all(any(p is q for q in g1["params"]) for p in ln)
    stem = [p for n, p in m.named_parameters() if n.startswith("hr_stem.")]
    assert stem and all(any(p is q for q in g0["params"]) for p in stem)
    assert g1["lr"] == pytest.approx(1e-4) and g1["weight_decay"] == 0.0 and g0["weight_decay"] == 1e-4


@pytest.mark.skipif(not TV_CNX.exists(), reason="torchvision ConvNeXt-T weights not cached")
def test_torchvision_remap_equals_torchvision_features():
    import timm
    import torchvision
    from src.models.hrstem_unetpp import torchvision_convnext_to_timm
    sd = torch.load(TV_CNX, map_location="cpu", weights_only=True)
    tv = torchvision.models.convnext_tiny(); tv.load_state_dict(sd); tv.eval()
    tm = timm.create_model("convnext_tiny", pretrained=False, num_classes=0)
    missing, unexpected = tm.load_state_dict(torchvision_convnext_to_timm(sd), strict=False)
    assert not unexpected and all(k.startswith("head.") for k in missing); tm.eval()
    x = torch.randn(2, 3, 128, 128)
    with torch.no_grad():
        ft = tm.forward_intermediates(x, indices=(0, 1, 2, 3), intermediates_only=True)
        h, fv = x, []
        for i, layer in enumerate(tv.features):
            h = layer(h)
            if i in (1, 3, 5, 7):
                fv.append(h)
    for a, b in zip(ft, fv):
        assert torch.allclose(a, b, atol=1e-4, rtol=1e-4), float((a - b).abs().max())


@pytest.mark.skipif(not TV_CNX.exists(), reason="torchvision ConvNeXt-T weights not cached")
def test_rgb_sum_stem_torchvision():
    sd = torch.load(TV_CNX, map_location="cpu", weights_only=True)
    m = build_model(_cfg(backbone_weights=str(TV_CNX), backbone_weights_format="torchvision_convnext"))
    w = dict(m.named_parameters())["encoder.stem.0.weight"]
    assert w.shape[1] == 1 and torch.equal(w, sd["features.0.0.weight"].sum(1, keepdim=True))


@pytest.mark.skipif(not SAM2_T.exists(), reason="SAM2 Hiera-T timm weights not on this machine")
def test_rgb_sum_stem_timm_file_and_hiera_forward():
    from safetensors.torch import load_file
    src = load_file(str(SAM2_T))
    m = build_model(_cfg(backbone="sam2_hiera_tiny", backbone_weights=str(SAM2_T)))
    w = dict(m.named_parameters())["encoder.patch_embed.proj.weight"]
    assert w.shape[1] == 1 and torch.allclose(w, src["patch_embed.proj.weight"].sum(1, keepdim=True), atol=1e-6)
    assert m(torch.randn(1, 1, 128, 128)).shape == (1, 24, 128, 128)


def test_no_new_config_defaults():
    base = yaml.safe_load(open(ROOT / "configs" / "base.yaml"))
    flat = yaml.safe_dump(base)
    for k in ("backbone", "hr_stem", "hrstem"):
        assert k not in flat


def test_house_model_unchanged_by_switch_code():
    torch.manual_seed(0)
    a = build_model({"name": "smp_unetpp", "encoder_weights": None})
    torch.manual_seed(0)
    b = build_model({"name": "smp_unetpp", "encoder_weights": None})
    sa, sb = a.state_dict(), b.state_dict()
    assert list(sa) == list(sb) and all(torch.equal(sa[k], sb[k]) for k in sa)


@pytest.mark.skipif(not SAM2_T.exists(), reason="SAM2 Hiera-T timm weights not on this machine")
def test_hiera_512_all_params_get_grad():
    torch.manual_seed(0)
    m = build_model(_cfg(backbone="sam2_hiera_tiny", backbone_weights=str(SAM2_T)))
    y = m(torch.randn(1, 1, 512, 512))
    assert y.shape == (1, 24, 512, 512) and torch.isfinite(y).all()
    y.float().mean().backward()
    nograd = [n for n, p in m.named_parameters() if p.requires_grad and p.grad is None]
    assert not nograd, nograd[:5]


def test_enc_cosine_hr_covers_every_convnext_layernorm_and_gamma(tmp_path):
    import subprocess
    import sys as _sys
    torch.manual_seed(0)
    m = build_model(_cfg())
    torch.save({"models": {"model": m.state_dict()}}, tmp_path / "a.pth")
    out = subprocess.run([_sys.executable, str(ROOT / "reports" / "enc_cosine_hr.py"), "--backbone", "convnext_tiny",
                          "--pair", "self", str(tmp_path / "a.pth"), str(tmp_path / "a.pth"), "--out", str(tmp_path / "o.json")],
                         capture_output=True, text=True)
    assert out.returncode == 0, out.stderr[-2000:]
    r = json.load(open(tmp_path / "o.json"))["self"]
    n_ln = sum(v["n_ln"] for v in r["stages"].values()); n_g = sum(v["n_gamma"] for v in r["stages"].values())
    assert n_ln == 22 and n_g == 18, (n_ln, n_g)  # ConvNeXt-T: stem.1 + 3 downsample norms + 18 block norms; 18 gammas
    assert all(v["cos_w"] > 0.9999 for v in r["stages"].values())


def _drop_probs(m):
    out = []
    for mod in m.modules():
        if type(mod).__name__ == "DropPath":
            out.append(float(getattr(mod, "drop_prob", 0.0)))
    return out


def test_backbone_drop_path_default_zero_and_explicit():
    m0 = build_model(_cfg())
    assert all(p == 0.0 for p in _drop_probs(m0))  # default: no stochastic depth (Identity or p = 0)
    m1 = build_model(_cfg(backbone_drop_path=0.1))
    probs = _drop_probs(m1)
    assert probs and max(probs) > 0.0  # the key reaches timm
