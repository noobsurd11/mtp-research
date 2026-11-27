"""elbench registry CPU build tests: parameter counts, 1-channel stem = RGB sum of the pretrained file, `encoder.` prefix,
forward shape (1, 24, 512, 512). Local weight files only (HF_HUB_OFFLINE); a missing file skips its test."""
import os
from pathlib import Path

import pytest
import torch

from src.models.model_factory import build_model

os.environ.setdefault("HF_HUB_OFFLINE", "1")
TV_CONVNEXT_T = "/home/noob/.cache/torch/hub/checkpoints/convnext_tiny-983f1562.pth"
DINOV3_VITS16 = "/home/noob/work/weights/dinov3_vits16_lvd1689m_timm.safetensors"
DINOV3_CNXT_T = "/home/noob/work/weights/dinov3_convnext_tiny_lvd1689m_timm.safetensors"
R34_HF = ("/home/noob/.cache/huggingface/hub/models--smp-hub--resnet34.imagenet/snapshots/"
          "7a57b34f723329ff020b3f8bc41771163c519d0c/model.safetensors")
REPORT = Path(os.environ.get("BENCH_MODEL_REPORT", "/tmp/bench_model_report.txt"))


def _need(p):
    if not Path(p).exists():
        pytest.skip(f"missing {p}")


def _report(name, m, extra=""):
    n = sum(p.numel() for p in m.parameters())
    ne = sum(p.numel() for k, p in m.named_parameters() if k.startswith("encoder."))
    with open(REPORT, "a") as f:
        f.write(f"{name}\tparams {n:,}\tencoder.* {ne:,}\t{extra}\n")
    return n, ne


def _fwd(m):
    m.eval()
    with torch.no_grad():
        y = m(torch.zeros(1, 1, 512, 512))
    assert tuple(y.shape) == (1, 24, 512, 512), y.shape


def _sf(path):
    from safetensors.torch import load_file
    return load_file(path)


def test_house_and_bench_smp_unetpp_equal():
    _need(R34_HF)
    torch.manual_seed(0); a = build_model({"name": "smp_unetpp", "encoder_name": "resnet34", "encoder_weights": "imagenet",
                                          "in_channels": 1, "num_classes": 24})
    torch.manual_seed(0); b = build_model({"name": "bench_smp", "decoder": "unetplusplus", "encoder_name": "resnet34",
                                          "encoder_weights": "imagenet", "in_channels": 1, "num_classes": 24})
    sa, sb = a.state_dict(), b.state_dict()
    assert list(sa) == list(sb) and all(torch.equal(sa[k], sb[k]) for k in sa)
    w = _sf(R34_HF)["conv1.weight"]
    assert torch.allclose(a.encoder.conv1.weight, w.sum(1, keepdim=True))
    _report("smp_unetpp R34 (house) == bench_smp unetplusplus R34", a, "state dicts equal at seed 0; conv1 = RGB sum")
    _fwd(b)


def test_bench_timm_upernet_convnext_t():
    _need(TV_CONVNEXT_T)
    m = build_model({"name": "bench_timm", "decoder": "upernet", "backbone": "convnext_tiny",
                     "backbone_weights": TV_CONVNEXT_T, "backbone_weights_format": "torchvision_convnext"})
    sd = torch.load(TV_CONVNEXT_T, map_location="cpu", weights_only=True)
    assert torch.allclose(m.encoder.stem[0].weight, sd["features.0.0.weight"].sum(1, keepdim=True))
    assert not [k for k, _ in m.named_parameters() if not k.split(".")[0] in ("encoder", "decoder", "segmentation_head")]
    _report("bench_timm UPerNet ConvNeXt-T (torchvision IN-1k)", m, "stem = RGB sum")
    _fwd(m)


def test_bench_timm_unetpp_equals_f8_hrstem():
    _need(DINOV3_CNXT_T)
    cfg = {"backbone": "convnext_tiny.dinov3_lvd1689m", "backbone_weights": DINOV3_CNXT_T, "backbone_weights_format": "timm"}
    torch.manual_seed(0); a = build_model({"name": "hrstem_unetpp", **cfg})
    torch.manual_seed(0); b = build_model({"name": "bench_timm", "decoder": "unetplusplus", **cfg})
    sa, sb = a.state_dict(), b.state_dict()
    assert list(sa) == list(sb) and all(torch.equal(sa[k], sb[k]) for k in sa)
    _report("bench_timm Unet++ (HR stem) DINOv3 ConvNeXt-T == f8 hrstem_unetpp", b, "state dicts equal at seed 0")


def test_bench_timm_unet_hrstem():
    _need(DINOV3_CNXT_T)
    m = build_model({"name": "bench_timm", "decoder": "unet", "backbone": "convnext_tiny.dinov3_lvd1689m",
                     "backbone_weights": DINOV3_CNXT_T, "backbone_weights_format": "timm"})
    w = _sf(DINOV3_CNXT_T)["stem.0.weight"]
    assert torch.allclose(m.encoder.stem[0].weight, w.sum(1, keepdim=True))
    _report("bench_timm Unet (HR stem) DINOv3 ConvNeXt-T", m, "stem = RGB sum")
    _fwd(m)


def test_bench_smp_segformer_mit_b2_random():
    m = build_model({"name": "bench_smp", "decoder": "segformer", "encoder_name": "mit_b2", "encoder_weights": None})
    _report("bench_smp SegFormer MiT-B2 (random init; no local weights)", m)
    _fwd(m)


def test_bench_timm_dpt_dinov3_vits16():
    _need(DINOV3_VITS16)
    m = build_model({"name": "bench_timm", "decoder": "dpt", "backbone": "vit_small_patch16_dinov3.lvd1689m",
                     "backbone_weights": DINOV3_VITS16, "decoder_kwargs": {"img_size": 512}})
    w = _sf(DINOV3_VITS16)["patch_embed.proj.weight"]
    pe = [p for k, p in m.named_parameters() if k.endswith("patch_embed.proj.weight")]
    assert len(pe) == 1 and torch.allclose(pe[0], w.sum(1, keepdim=True))
    _report("bench_timm DPT DINOv3 ViT-S/16 (local file)", m, "patch embed = RGB sum")
    _fwd(m)


def test_inference_cfg_builds_without_files():
    """bench_infer nulls pretrained keys: the same architecture must build with no weight file."""
    m = build_model({"name": "bench_timm", "decoder": "upernet", "backbone": "convnext_tiny", "backbone_weights": None})
    assert sum(p.numel() for p in m.parameters()) > 0
