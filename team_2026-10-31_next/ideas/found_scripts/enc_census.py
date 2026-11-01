import timm, torch
torch.set_num_threads(4)
names = ["convnext_tiny.dinov3_lvd1689m","convnext_small.dinov3_lvd1689m","convnext_base.dinov3_lvd1689m",
 "vit_small_patch16_dinov3.lvd1689m","vit_small_plus_patch16_dinov3.lvd1689m","vit_base_patch16_dinov3.lvd1689m","vit_large_patch16_dinov3.lvd1689m",
 "vit_small_patch14_dinov2.lvd142m","vit_small_patch14_reg4_dinov2.lvd142m","vit_base_patch14_reg4_dinov2.lvd142m",
 "samvit_base_patch16.sa1b","samvit_large_patch16.sa1b",
 "sam2_hiera_tiny.fb_r896","sam2_hiera_small.fb_r896","sam2_hiera_base_plus.fb_r896","sam2_hiera_large.fb_r1024",
 "resnet34.tv_in1k","resnet50.tv_in1k","convnext_tiny.fb_in1k"]
for n in names:
    try:
        m = timm.create_model(n, pretrained=False)
        p = sum(x.numel() for x in m.parameters())
        cfg = m.pretrained_cfg
        print("%s\tparams=%.1fM\tfp32MB=%.0f\thub=%s\tlic=%s\tin=%s\tmean=%s" % (n, p/1e6, p*4/2**20, cfg.get("hf_hub_id"), cfg.get("license"), cfg.get("input_size"), cfg.get("mean")))
        fi = getattr(m, "feature_info", None)
        if fi:
            print("   feat", [(f.get("module"), f.get("reduction"), f.get("num_chs")) for f in fi][:6])
        del m
    except Exception as e:
        print(n, "ERR", repr(e)[:300])
