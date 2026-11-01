import torch, segmentation_models_pytorch as smp, time
torch.set_num_threads(4)
x = torch.randn(1, 1, 512, 512)
tests = [("UnetPlusPlus", "resnet34"), ("UnetPlusPlus", "tu-convnext_tiny"), ("Unet", "tu-convnext_tiny"),
         ("UnetPlusPlus", "tu-sam2_hiera_tiny"), ("Unet", "tu-sam2_hiera_tiny"),
         ("DPT", "tu-vit_small_patch16_dinov3"), ("UPerNet", "tu-convnext_tiny"), ("Unet", "tu-vit_small_patch16_dinov3")]
for arch, enc in tests:
    try:
        kw = dict(encoder_name=enc, encoder_weights=None, in_channels=1, classes=24)
        m = getattr(smp, arch)(**kw).eval()
        p = sum(t.numel() for t in m.parameters())
        with torch.no_grad():
            t0 = time.time(); y = m(x); dt = time.time() - t0
            feats = m.encoder(x)
        print(f"{arch}+{enc}: OK params={p/1e6:.1f}M out={tuple(y.shape)} cpu_fwd={dt:.1f}s enc_strides={[512//f.shape[-1] if f.dim()==4 and f.shape[-1]>0 else None for f in feats]} chs={[f.shape[1] for f in feats]}")
    except Exception as e:
        print(f"{arch}+{enc}: ERR {repr(e)[:250]}")
