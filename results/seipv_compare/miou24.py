"""24-class mIoU on the 50 BenchmarkEL test cells under several averaging rules (read-only CPU inference).
For comparison with SEiPV-Net (Energies 2023, 16(23):7726), whose averaging rule is not stated.
Old labels = masks_coded (20211104); revised = escdd_masks/test with ids >= 24 mapped back to the old label."""
import argparse, json, os, sys
from pathlib import Path
import numpy as np, torch
from PIL import Image
from torch.utils.data import DataLoader
CODE = Path("/home/noob/work/el_p13")
sys.path.insert(0, str(CODE)); os.chdir(CODE)
from src.data.augmentations import get_weak_augmentation
from src.data.benchmark_el import BenchmarkELDataset
from src.data.splits import load_split
from src.models.model_factory import build_model
from src.utils.config import load_config
DATA = CODE / "data"
IMG, MSK, NEW = DATA / "labeled" / "images", DATA / "labeled" / "masks_coded", DATA / "escdd_masks"
K = 24
BASE = Path("/home/noob/work/cv02_noob_el")
DEFECT3 = (("crack", 14), ("gridline", 15), ("inactive", 11))


def find_run(run):
    hits = sorted(BASE.glob("*/experiments/" + run + "/checkpoints/latest.pth"))
    if not hits:
        raise SystemExit("missing " + run)
    return hits[0].parent.parent


def cm_of(pred, gt):
    m = (gt >= 0) & (gt < K)
    return np.bincount(K * gt[m] + pred[m], minlength=K * K).reshape(K, K)


def summarise(cms):
    cm = sum(cms)
    tp = np.diag(cm).astype(float); gt = cm.sum(1).astype(float); pr = cm.sum(0).astype(float)
    union = gt + pr - tp
    iou = np.where(union > 0, tp / np.maximum(union, 1), np.nan)
    dice = np.where(gt + pr > 0, 2 * tp / np.maximum(gt + pr, 1), np.nan)
    pu, pg, fg = union > 0, gt > 0, np.arange(K) != 0
    out = {"miou_union_bg": float(np.mean(iou[pu])), "miou_union_nobg": float(np.mean(iou[pu & fg])),
           "miou_gt_bg": float(np.mean(iou[pg])), "miou_gt_nobg": float(np.mean(iou[pg & fg])),
           "fw_iou": float(np.nansum(iou * gt) / gt.sum()), "pixel_acc": float(tp.sum() / gt.sum()),
           "dice_macro_gt_bg": float(np.mean(dice[pg])), "f1_weighted": float(np.nansum(dice * gt) / gt.sum()),
           "n_classes_gt": int(pg.sum()), "n_classes_union": int(pu.sum()),
           "per_class_iou": {int(c): (None if np.isnan(iou[c]) else float(iou[c])) for c in range(K)},
           "per_class_gt_px": {int(c): int(gt[c]) for c in range(K)},
           "per_class_pred_px": {int(c): int(pr[c]) for c in range(K)}}
    skip, one = [], []
    for c in cms:
        t = np.diag(c).astype(float); u = c.sum(1) + c.sum(0) - t
        v = np.where(u > 0, t / np.maximum(u, 1), np.nan)
        skip.append(np.nanmean(v)); one.append(np.mean(np.where(u > 0, v, 1.0)))
    out["per_image_miou_skip"] = float(np.mean(skip)); out["per_image_miou_absent1"] = float(np.mean(one))
    out["defect3_iou"] = {n: out["per_class_iou"][c] for n, c in DEFECT3}
    return out


@torch.no_grad()
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", nargs="+", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--threads", type=int, default=16)
    a = ap.parse_args()
    torch.set_num_threads(a.threads)
    stems = sorted(load_split(DATA / "splits" / "test.txt"))
    res = {}
    for run in a.runs:
        rd = find_run(run)
        cfg = load_config(rd / "config_used.yaml"); d = cfg["data"]
        ds = BenchmarkELDataset(IMG, MSK, stems, get_weak_augmentation(d.get("mean", [0.5]), d.get("std", [0.25]), d["input_size"]))
        dl = DataLoader(ds, batch_size=4, shuffle=False, num_workers=2)
        st = torch.load(rd / "checkpoints" / "latest.pth", map_location="cpu", weights_only=False)
        key = "teacher" if cfg.get("method") == "mean_teacher" and "teacher" in st["models"] else "model"
        m = build_model(cfg["model"]); m.load_state_dict(st["models"][key]); m.eval()
        cms = {"old": [], "new": []}; got = []
        for b in dl:
            pred = m(b["image"]).argmax(1).numpy().astype(np.int64)
            for i, s in enumerate(b["stem"]):
                old = b["mask"][i].numpy().astype(np.int64)
                newp = NEW / "test" / (s + ".png")
                new = np.array(Image.open(newp)).astype(np.int64) if newp.exists() else old.copy()
                new = np.where(new >= K, old, new)
                cms["old"].append(cm_of(pred[i], old)); cms["new"].append(cm_of(pred[i], new)); got.append(s)
        assert got == stems, "stem order mismatch"
        r = {lab: summarise(v) for lab, v in cms.items()}
        res[run] = dict(weights=key, step=int(st.get("step", -1)), rundir=str(rd), n=len(stems), **r)
        o, n = r["old"], r["new"]
        print("{:22s} {:7s} crack old/new {:.3f}/{:.3f} inact {:.3f}/{:.3f} | mIoU bg {:.3f} nobg {:.3f} | fwIoU {:.3f} F1w {:.3f} | perimg abs1 {:.3f}".format(run, key, o["defect3_iou"]["crack"], n["defect3_iou"]["crack"], o["defect3_iou"]["inactive"], n["defect3_iou"]["inactive"], o["miou_union_bg"], o["miou_union_nobg"], o["fw_iou"], o["f1_weighted"], o["per_image_miou_absent1"]), flush=True)
        Path(a.out).write_text(json.dumps(res, indent=1))
    print("wrote", a.out)


if __name__ == "__main__":
    main()
