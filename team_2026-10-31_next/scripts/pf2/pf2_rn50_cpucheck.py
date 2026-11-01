"""PF2 RN50-PF CPU check (gaint, el_f3 e544133; no GPU). Builds the run models from the queue's opts exactly as train.py does
(load_config + --opts overrides -> build_model -> build_optimizer), for SUP100-PF and RN50-PF, and reports:
- params, encoder params, PF param groups (group 0 = non-encoder.*, group 1 = encoder.*), group lr / wd;
- the 1-channel stem: conv1 weight shape and equality with the RGB sum of smp-hub resnet50.imagenet;
- which weight file the ImageNet encoder came from (HF cache, offline);
- writes the ImageNet RN50 step-0 reference {"models": {"model": state_dict}, "step": 0} for enc_cosine.py (RN50-PF vs ImageNet).
Usage: HF_HUB_OFFLINE=1 CUDA_VISIBLE_DEVICES= python pf2_rn50_cpucheck.py OUT_DIR
"""
import hashlib, json, os, sys
sys.path.insert(0, os.getcwd()); sys.path.insert(0, os.path.join(os.getcwd(), "scripts"))
import torch
torch.set_num_threads(4)
import train as T  # noqa: E402  (el_f3 scripts/train.py: load_config, apply_opts, build_optimizer exactly as a run)
from src.models.model_factory import build_model  # noqa: E402

out = sys.argv[1]; os.makedirs(out, exist_ok=True)
B = ("data.labeled_fraction=1.0 training.total_steps=20000 data.split_seed=0 training.labeled_batch_size=8 "
     "data.mask_subdir=labeled/masks_escdd model.name=smp_unetpp data.augmentation=labelsafe loss.supervised=ce_dice").split()
PF = "training.encoder_pf.freeze=1000 training.encoder_pf.ramp=1000 training.encoder_pf.lr_mult=0.1 training.encoder_pf.wd=0".split()
VAL = ["training.val_every=20000"]
arms = {"SUPPF": B + PF + VAL, "RN50PF": B + PF + VAL + ["model.encoder_name=resnet50"]}
rep = {}
for arm, opts in arms.items():
    cfg = T.apply_opts(T.load_config("configs/supervised.yaml"), ["seed=5"] + opts)
    torch.manual_seed(0)
    m = build_model(cfg["model"])
    opt = T.build_optimizer(m, cfg)
    n_all = sum(p.numel() for p in m.parameters()); n_enc = sum(p.numel() for n, p in m.named_parameters() if n.startswith("encoder."))
    g = [{"n_params": sum(p.numel() for p in pg["params"]), "lr": pg["lr"], "weight_decay": pg["weight_decay"]} for pg in opt.param_groups]
    w = m.encoder.conv1.weight.detach()
    rep[arm] = {"model": cfg["model"], "params": n_all, "encoder_params": n_enc, "groups": g, "conv1": list(w.shape),
                "encoder_conv_tensors": sum(1 for n, v in m.state_dict().items() if n.startswith("encoder.") and v.dim() == 4)}
    if arm == "RN50PF":
        # the 1-channel stem must equal the RGB sum of the ImageNet stem (smp patch_first_conv)
        import segmentation_models_pytorch as smp
        rgb = smp.UnetPlusPlus(encoder_name="resnet50", encoder_weights="imagenet", in_channels=3, classes=24).encoder.conv1.weight.detach()
        rep[arm]["conv1_equals_rgb_sum"] = bool(torch.allclose(w, rgb.sum(1, keepdim=True)))
        sd = {k: v for k, v in m.state_dict().items()}
        p = os.path.join(out, "rn50_imagenet_step0.pth")
        torch.save({"models": {"model": sd}, "step": 0}, p)
        enc = torch.cat([v.flatten().float() for k, v in sorted(sd.items()) if k.startswith("encoder.")])
        rep[arm]["step0_file"] = p
        rep[arm]["encoder_tensor_sha1"] = hashlib.sha1(enc.numpy().tobytes()).hexdigest()
        # deterministic: a second build gives the same encoder
        m2 = build_model(cfg["model"])
        rep[arm]["encoder_rebuild_identical"] = all(torch.equal(v, m2.state_dict()[k]) for k, v in sd.items() if k.startswith("encoder."))
hub = os.path.expanduser("~/.cache/huggingface/hub/models--smp-hub--resnet50.imagenet")
rep["hf_cache_files"] = sorted(os.path.join(dp, f).replace(hub, "") for dp, _, fs in os.walk(hub) for f in fs)
json.dump(rep, open(os.path.join(out, "rn50_cpucheck.json"), "w"), indent=1)
print(json.dumps(rep, indent=1))
