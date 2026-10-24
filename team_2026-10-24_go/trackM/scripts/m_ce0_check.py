"""Track M R2 smoke check (MC review_r2): with the R2 opts, the resolved loss config is dice_classes=[...12], dice_weight 6.0,
and at step 0 (same seed, same init, same first batch) the CE part equals the SUP100 config's, while the full loss differs
only by the added Dice terms. Run from a cv02 code root: python m_ce0_check.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd())); sys.path.insert(0, str(Path.cwd() / "scripts"))
import torch  # noqa: E402
import torch.nn.functional as F  # noqa: E402
import train as T  # noqa: E402  (scripts/train.py)
from src.losses.loss_factory import build_losses  # noqa: E402
from src.models.model_factory import build_model  # noqa: E402
from src.utils.config import load_config  # noqa: E402
from src.utils.seed import set_seed  # noqa: E402

BASE = ("seed=0 data.labeled_fraction=1.0 training.total_steps=20000 data.split_seed=0 training.labeled_batch_size=8 "
        "data.mask_subdir=labeled/masks_escdd model.name=smp_unetpp data.augmentation=labelsafe loss.supervised=ce_dice").split()
R2 = BASE + ["loss.dice_classes=[1,2,4,5,9,11,13,14,15,16,20,21]", "loss.dice_weight=6.0"]
dev = torch.device("cuda")
res = {}
for name, opts in (("SUP100", BASE), ("R2", R2)):
    cfg = T.apply_opts(load_config("configs/supervised.yaml"), opts)
    set_seed(0, deterministic=True)
    data = T.build_benchmark_data(cfg, "supervised", 0, 1.0, False, dev, 0)
    torch.manual_seed(0)
    m = build_model(cfg["model"]).to(dev).train()
    loss = build_losses(cfg["loss"], data["class_counts"])["supervised"].to(dev)
    b = next(iter(data["labeled_loader"].iterate(0)))
    x, y = b["image"].to(dev), b["mask"].to(dev)
    with torch.autocast("cuda", dtype=torch.bfloat16):
        lg = m(x)
    ce = F.cross_entropy(lg.float(), y)
    res[name] = (cfg["loss"].get("dice_classes"), cfg["loss"].get("dice_weight"), float(ce), float(loss(lg, y)), x.sum().item())
    print(name, "dice_classes", res[name][0], "dice_weight", res[name][1], "CE", res[name][2], "loss", res[name][3],
          "batch checksum", res[name][4])
assert res["SUP100"][2] == res["R2"][2] and res["SUP100"][4] == res["R2"][4], "CE or batch differs"
assert list(res["R2"][0]) == [1, 2, 4, 5, 9, 11, 13, 14, 15, 16, 20, 21] and float(res["R2"][1]) == 6.0
print("OK: step-0 CE identical; R2 resolves 12 classes, weight 6.0")
