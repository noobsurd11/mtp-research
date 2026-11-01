"""found, 1 Nov 2026: DINOv3 timm-mirror files on gaint: key format and output equivalence (builder review item b).
(1) strict load of the safetensors into timm's own model (no missing / unexpected keys besides the absent classifier);
(2) the timm pretrained path (pretrained_cfg_overlay=file) gives the same state and the same forward as (1);
(3) our hrstem_unetpp wrapper (in_chans 1) stem = the file's RGB stem summed over channels; forward finite at 512.
CPU only, no training, no data read."""
import os, sys, torch, timm
from safetensors.torch import load_file
assert os.environ.get("CUDA_VISIBLE_DEVICES") == ""
torch.set_num_threads(8); torch.manual_seed(0)
W = "/home/noob/work/weights"
x = torch.randn(1, 3, 224, 224)
for tag, f, stem_key in (("convnext_tiny.dinov3_lvd1689m", f"{W}/dinov3_convnext_tiny_lvd1689m_timm.safetensors", "stem.0.weight"),
                         ("vit_small_patch16_dinov3.lvd1689m", f"{W}/dinov3_vits16_lvd1689m_timm.safetensors", "patch_embed.proj.weight")):
    sd = load_file(f)
    m1 = timm.create_model(tag, pretrained=False, num_classes=0)
    miss, unexp = m1.load_state_dict(sd, strict=False)
    print(tag, "keys in file", len(sd), "missing", [k for k in miss][:6], "unexpected", [k for k in unexp][:6])
    m2 = timm.create_model(tag, pretrained=True, pretrained_cfg_overlay=dict(file=f), num_classes=0)
    s1, s2 = m1.state_dict(), m2.state_dict()
    same = all(torch.equal(s1[k], s2[k]) for k in s1) and set(s1) == set(s2)
    m1.eval(); m2.eval()
    with torch.no_grad():
        d = float((m1(x) - m2(x)).abs().max())
    print(f"  timm pretrained path == strict load: state {same}, forward max|d| {d:.2e}")
sys.path.insert(0, "/home/noob/work/el_f8")
from src.models.model_factory import build_model
m = build_model({"name": "hrstem_unetpp", "backbone": "convnext_tiny.dinov3_lvd1689m", "in_channels": 1, "num_classes": 24,
                 "backbone_weights": f"{W}/dinov3_convnext_tiny_lvd1689m_timm.safetensors", "backbone_weights_format": "timm", "backbone_drop_path": 0.0})
sd = load_file(f"{W}/dinov3_convnext_tiny_lvd1689m_timm.safetensors")
w = dict(m.named_parameters())["encoder.stem.0.weight"]
print("wrapper stem (1 ch) == file RGB stem summed:", w.shape, torch.allclose(w, sd["stem.0.weight"].sum(1, keepdim=True), atol=1e-6))
blk = [k for k in sd if k.startswith("stages.2.blocks.3.")][:3]
print("deep weights carried:", all(torch.equal(dict(m.named_parameters())["encoder." + k], sd[k]) for k in blk if ("encoder." + k) in dict(m.named_parameters())), blk)
with torch.no_grad():
    y = m.eval()(torch.randn(1, 1, 512, 512))
print("wrapper forward 512:", tuple(y.shape), bool(torch.isfinite(y).all()))
