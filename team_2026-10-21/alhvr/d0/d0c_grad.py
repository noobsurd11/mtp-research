"""D0c: gradient-share probe with the worktree's own loss code and the exact arm configs (noise perturbation).
Same surrogate pairs and batches as D0b; median |grad L_u| / |grad L_sup| at lambda 1 for network A."""
import importlib.util, json, random, sys
from pathlib import Path
import numpy as np, torch, torch.nn.functional as F
from torch.utils.data import DataLoader
sys.path.insert(0, ".")
from src.losses.alhvr import ALHVRConfig, alhvr_unsup_losses
from src.models.dual_smp import smp_forward_dual
from src.trainers.ssl_ops import frozen_bn_stats, cutmix_boxes, mix_with_next
from src.losses.ce_dice import CEDiceLoss
from src.data.augmentations import get_weak_augmentation
from src.data.benchmark_el import BenchmarkELDataset
from src.data.splits import load_split
spec = importlib.util.spec_from_file_location("d0", "/home/noob/work/alhvr_diag/d0_alhvr_probe.py"); d0 = importlib.util.module_from_spec(spec); spec.loader.exec_module(d0)
BASE = dict(forward="separate", lambda_schedule="warmup_linear", perturb="noise", feature_layer="penultimate",
            sharpening="softmax", dtct_detach_target=True, prototype_scale=10.0, pull="target", lambda_max=1.0)
ARMS = {"AL": {}, "ALd": {"cpcl": False}, "CPS": {"loss": "cps"}, "CPSm": {"loss": "cps_routed"}}
dev = torch.device("cuda"); D = Path("/home/noob/work/el-fault-detection/data"); E = "/home/noob/work/cv02_noob_el/"
pairs = [(E+"el_p11/experiments/p12_A_5pct_s0", E+"el_p11/experiments/p12_A_5pct_s1"), (E+"el_p13/experiments/p13_A_5pct_s3", E+"el_p13/experiments/p13_A_5pct_s4")]
tf = get_weak_augmentation([0.5], [0.25], 512)
unl = BenchmarkELDataset(D/"labeled/images", D/"labeled/masks_escdd", sorted(load_split(D/"splits/seed0/unlabeled_5pct.txt")), tf)
lab = BenchmarkELDataset(D/"labeled/images", D/"labeled/masks_escdd", sorted(load_split(D/"splits/seed0/labeled_5pct.txt")), tf)
crit = CEDiceLoss(); res = {}
for pi, (ra, rb) in enumerate(pairs):
    ma, _ = d0.load(Path(ra), dev); mb, _ = d0.load(Path(rb), dev)
    params = [p for p in ma.parameters() if p.requires_grad]
    gn = lambda l: d0.grad_norm(l, params)
    ldl = [b for _ in range(8) for b in DataLoader(lab, 8, shuffle=True, generator=torch.Generator().manual_seed(100+pi), drop_last=True)]
    udl = iter(DataLoader(unl, 8, shuffle=True, generator=torch.Generator().manual_seed(200+pi), drop_last=True))
    rec = {k: [] for k in ["sup", "bsm", *ARMS]}; share = {k: [] for k in ARMS}
    for i in range(12):
        xl, yl = ldl[i]["image"].to(dev), ldl[i]["mask"].to(dev).long(); xu = next(udl)["image"].to(dev)
        ma.train(); mb.train()
        with frozen_bn_stats(ma), frozen_bn_stats(mb):
            with torch.autocast("cuda", dtype=torch.bfloat16):
                lo = ma(xl)
            ls = crit(lo.float(), yl); rec["sup"].append(gn(ls))
            g = torch.Generator().manual_seed(1000 + i)
            box = cutmix_boxes(8, 512, 512, 0.5, g).to(dev)
            with torch.no_grad(), torch.autocast("cuda", dtype=torch.bfloat16):
                tl = ma(xu).float()
            with torch.autocast("cuda", dtype=torch.bfloat16):
                sl = ma(mix_with_next(xu, box)).float()
            pt = torch.softmax(mix_with_next(tl, box), 1); conf, lb = pt.max(1); m = (conf >= 0.95).float()
            rec["bsm"].append(gn((F.cross_entropy(sl, lb, reduction="none") * m).sum() / m.numel()))
            torch.manual_seed(5000 + i); st = torch.cuda.get_rng_state()
            for arm, over in ARMS.items():
                torch.cuda.set_rng_state(st)
                cfg = ALHVRConfig.from_dict({**BASE, **over})
                with torch.autocast("cuda", dtype=torch.bfloat16):
                    a1, a2, fa1, fa2 = smp_forward_dual(ma, xu, "penultimate", "noise")
                    with torch.no_grad():  # B's outputs are constants for A's gradient
                        b1, b2, fb1, fb2 = smp_forward_dual(mb, xu, "penultimate", "noise")
                u = alhvr_unsup_losses(a1, a2, fa1, fa2, b1, b2, fb1, fb2, cfg)
                rec[arm].append(gn(u["unsup_a"]))
                share[arm].append({k: float(u[k].detach()) for k in ("ce_a", "cos_a", "mse_a", "ent_a")})
                del u, a1, a2, fa1, fa2, b1, b2, fb1, fb2
    r = {f"ratio_{k}": float(np.median(np.array(rec[k]) / np.array(rec["sup"]))) for k in rec if k != "sup"}
    r["sup_loss_note"] = "final weights"
    r["terms"] = {a: {k: float(np.mean([s[k] for s in v])) for k in v[0]} for a, v in share.items()}
    res[f"pair{pi+1}"] = r; print(json.dumps(r), flush=True)
    del ma, mb; torch.cuda.empty_cache()
lam = {}
for arm in ARMS:
    vals = [res[p]["ratio_bsm"] / res[p][f"ratio_{arm}"] for p in res]
    lam[arm] = {"per_pair": vals, "mean": float(np.mean(vals))}
res["lambda_rule"] = lam; print(json.dumps(lam))
Path("/home/noob/work/alhvr_diag/d0c_grad.json").write_text(json.dumps(res, indent=1))
