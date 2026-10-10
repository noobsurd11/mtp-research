"""P5: rare-class pseudo-label precision inside ALHVR regions, global vs per-class gamma (offline, read-only).

Protocol: ~/mtp/research/protocols/P5_region_pseudolabel_precision.md (locked before running).
Usage: .venv/bin/python scripts/p5_region_pl_precision.py --runs alhvr_20pct_s0 alhvr_20pct_s1
"""
from __future__ import annotations

import argparse, json, os, random, sys
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from scipy import ndimage as ndi
from torch.utils.data import DataLoader

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
from src.data.augmentations import get_weak_augmentation  # noqa: E402
from src.data.benchmark_el import BenchmarkELDataset  # noqa: E402
from src.data.class_info import CRACK_CLASS, INACTIVE_CLASS  # noqa: E402
from src.data.splits import load_split  # noqa: E402
from src.losses.alhvr import adaptive_threshold, region_masks  # noqa: E402
from src.models.model_factory import build_model  # noqa: E402
from src.utils.config import load_config  # noqa: E402

DATA = ROOT / "data"
IMG, MSK, NEW = DATA / "labeled" / "images", DATA / "labeled" / "masks_coded", DATA / "escdd_masks" / "train"
CLS = {"crack": CRACK_CLASS, "inactive": INACTIVE_CLASS}
REG = ("r1", "r2a", "r2b", "r3")


@torch.no_grad()
def forward_run(run: str, stems: list[str], dev) -> list[dict]:
    cfg = load_config(ROOT / "experiments" / run / "config_used.yaml")
    d = cfg["data"]
    st = torch.load(ROOT / "experiments" / run / "checkpoints" / "latest.pth", map_location=dev, weights_only=False)
    keys = list(st["models"].keys())
    ka, kb = "model", [k for k in keys if k != "model"][0]
    nets = []
    for k in (ka, kb):
        m = build_model(cfg["model"]).to(dev); m.load_state_dict(st["models"][k]); m.eval(); nets.append(m)
    layer = cfg["alhvr"].get("feature_layer", "deep"); prop = float(cfg["alhvr"].get("proportion", 0.8))
    ds = BenchmarkELDataset(IMG, MSK, stems, get_weak_augmentation(d.get("mean", [0.5]), d.get("std", [0.25]), d["input_size"]))
    dl = DataLoader(ds, batch_size=4, shuffle=False, num_workers=2)
    random.seed(0); torch.manual_seed(0)
    out = []
    for b in dl:
        x = b["image"].to(dev)
        with torch.autocast("cuda", dtype=torch.bfloat16):
            a1, a2, _, _ = nets[0].forward_dual(x, layer)
            b1, b2, _, _ = nets[1].forward_dual(x, layer)
        sa1, sa2, sb1, sb2 = (torch.softmax(t.float(), 1) for t in (a1, a2, b1, b2))
        con_a1, pl_a = sa1.max(1); con_b1, pl_b = sb1.max(1)
        con_a2, con_b2 = sa2.max(1).values, sb2.max(1).values
        ens = (sa1 + sb1) / 2; ens_max, ens_pl = ens.max(1)
        gamma = adaptive_threshold((con_a2 + con_b2) * 0.5, prop)
        rg = region_masks(con_a2, con_b2, gamma)
        reg = torch.zeros_like(pl_a, dtype=torch.uint8)
        for i, r in enumerate(REG): reg[rg[r]] = i
        for j in range(x.shape[0]):
            out.append({"stem": b["stem"][j], "old": b["mask"][j].numpy().astype(np.uint8),
                        "con_a1": con_a1[j].cpu().numpy().astype(np.float16), "con_b1": con_b1[j].cpu().numpy().astype(np.float16),
                        "con_a2": con_a2[j].cpu().numpy().astype(np.float32), "con_b2": con_b2[j].cpu().numpy().astype(np.float32),
                        "pl_a": pl_a[j].cpu().numpy().astype(np.uint8), "pl_b": pl_b[j].cpu().numpy().astype(np.uint8),
                        "ens_pl": ens_pl[j].cpu().numpy().astype(np.uint8), "ens_max": ens_max[j].cpu().numpy().astype(np.float16),
                        "reg_global": reg[j].cpu().numpy(), "gamma_batch": float(gamma)})
    return out


def per_class_gamma(recs: list[dict], prop: float = 0.8, C: int = 24) -> np.ndarray:
    g = np.full(C, np.nan)
    m2 = np.concatenate([((r["con_a2"] + r["con_b2"]) * 0.5).ravel() for r in recs])
    cl = np.concatenate([r["ens_pl"].ravel() for r in recs])
    for c in range(C):
        v = np.sort(m2[cl == c])
        if v.size: g[c] = v[: max(int(v.size * prop), 1)].mean()
    return g


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", nargs="+", default=["alhvr_20pct_s0", "alhvr_20pct_s1"])
    ap.add_argument("--out", default="reports/probes/p5_region_pl_precision.json")
    a = ap.parse_args()
    dev = torch.device("cuda")
    stems = sorted(load_split(DATA / "splits" / "seed0" / "unlabeled_20pct.txt"))
    stems = [s for s in stems if (NEW / f"{s}.png").exists()]
    new = {s: np.array(Image.open(NEW / f"{s}.png")) for s in stems}
    # counts[variant][label][class][region] = [n_gt_c_in_R, n_tgt_c, n_tgt_c_and_gt_c, n_tgt_c_within2px]
    variants = ("global", "per_class")
    cnt = {v: {L: {c: {r: np.zeros(4) for r in REG + ("all",)} for c in CLS} for L in ("old", "new")} for v in variants}
    ref = {L: {c: np.zeros(5) for c in CLS} for L in ("old", "new")}  # n_gt, n_pl, n_pl&gt, n_pl_within2, covered_pixels
    gammas, n_pix = {}, 0
    for run in a.runs:
        recs = forward_run(run, stems, dev)
        gc = per_class_gamma(recs)
        gammas[run] = {"per_class": {k: float(gc[c]) for k, c in CLS.items()} | {"background": float(gc[0])},
                       "global_batch_mean": float(np.mean([r["gamma_batch"] for r in recs]))}
        for r in recs:
            n_pix += r["pl_a"].size
            winner = np.where(r["con_a1"] > r["con_b1"], r["pl_a"], r["pl_b"])
            sure_a = r["con_a2"] > gc[r["pl_a"]]; sure_b = r["con_b2"] > gc[r["pl_b"]]
            reg_pc = np.zeros_like(r["pl_a"]); reg_pc[sure_a & ~sure_b] = 2; reg_pc[~sure_a & sure_b] = 1; reg_pc[~sure_a & ~sure_b] = 3
            regs = {"global": r["reg_global"], "per_class": reg_pc}
            for v, R in regs.items():
                tgt = np.full_like(r["pl_a"], 255)
                agree = (R == 0) & (r["pl_a"] == r["pl_b"]); tgt[agree] = r["pl_a"][agree]
                tgt[R == 1] = r["pl_b"][R == 1]; tgt[R == 2] = r["pl_a"][R == 2]; tgt[R == 3] = winner[R == 3]
                for L, gt in (("old", r["old"]), ("new", new[r["stem"]])):
                    for cname, c in CLS.items():
                        g = gt == c; t = tgt == c
                        near = ndi.distance_transform_edt(~g) <= 2 if g.any() else np.zeros_like(g)
                        for i, rn in enumerate(REG):
                            m = R == i
                            cnt[v][L][cname][rn] += ((g & m).sum(), (t & m).sum(), (t & g & m).sum(), (t & near & m).sum())
                        cnt[v][L][cname]["all"] += (g.sum(), t.sum(), (t & g).sum(), (t & near).sum())
                        if v == "global":
                            pl = (r["ens_max"] >= 0.95) & (r["ens_pl"] == c)
                            ref[L][cname] += (g.sum(), pl.sum(), (pl & g).sum(), (pl & near).sum(), (r["ens_max"] >= 0.95).sum())
        del recs
    res = {"runs": a.runs, "n_images": len(stems), "gammas": gammas, "variants": {}}
    for v in variants:
        res["variants"][v] = {}
        for L in ("old", "new"):
            for cname in CLS:
                tot_gt = cnt[v][L][cname]["all"][0]
                for rn in REG + ("all",):
                    ngt, nt, ntg, nt2 = cnt[v][L][cname][rn]
                    res["variants"][v][f"{L}/{cname}/{rn}"] = {
                        "gt_share": ngt / max(tot_gt, 1), "prec": ntg / max(nt, 1), "relprec2": nt2 / max(nt, 1),
                        "recall": ntg / max(ngt, 1), "n_target": int(nt), "n_gt": int(ngt)}
    res["reference_pl095"] = {f"{L}/{c}": {"prec": float(v[2] / max(v[1], 1)), "relprec2": float(v[3] / max(v[1], 1)),
                                           "recall_of_all_gt": float(v[2] / max(v[0], 1)), "n_pl": int(v[1])}
                              for L in ref for c, v in ref[L].items()}
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(res, indent=1))
    print(json.dumps(res["gammas"], indent=1))
    for v in variants:
        for L in ("old", "new"):
            for cname in CLS:
                row = " | ".join(f"{rn}: sh {res['variants'][v][f'{L}/{cname}/{rn}']['gt_share']:.2f} P {res['variants'][v][f'{L}/{cname}/{rn}']['prec']:.2f}"
                                 f" P2 {res['variants'][v][f'{L}/{cname}/{rn}']['relprec2']:.2f} R {res['variants'][v][f'{L}/{cname}/{rn}']['recall']:.2f}"
                                 for rn in REG)
                print(f"{v:9s} {L} {cname:8s} {row}")
    print("PL>=0.95:", json.dumps(res["reference_pl095"]))
    print("wrote", a.out)


if __name__ == "__main__":
    main()
