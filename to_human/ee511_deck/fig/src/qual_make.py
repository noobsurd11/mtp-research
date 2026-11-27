"""EE511 talk: three qualitative comparison figures (Q1 pool methods, Q2 E1 final vs baseline, Q3 E1 few-shot).

Runs on gaint, CPU only, output in /home/noob/work/ee511_qual/out. Reads only; writes nothing outside that folder.
Per-cell crack relF1@2 = the frozen per-cell formula (bench/metrics_v02.py cell_values; same as make_F21.f1cell) applied to
the crack_rel2 counts [pred px within 2 px of GT, pred px, GT px within 2 px of pred, GT px] of the benchmark's own per-cell
records (bench_score / bench_read_w1 cache), i.e. the records the reads used. Nothing is rescored for selection.
Q1 literature rows: their .npz dumps were deleted after the read; the shown seed-5 maps are re-inferred on CPU from the kept
slim checkpoints with the bench_infer predict path (bench_wt_w2), and checked against the read's record counts.
"""
from __future__ import annotations

import glob
import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

OUT = Path("/home/noob/work/ee511_qual/out")
CRACK, INACT = 14, 11
COL_CRACK = np.array([0xD5, 0x5E, 0x00], np.float32)
COL_INACT = np.array([0x00, 0x72, 0xB2], np.float32)
MINPX = 20   # F21 rule: the frozen per-cell eligibility MIN_GT_CELL = 20

T = Path("/home/yugma/mtp/research/team_2026-11-12_frontier")
EXCL = T / "benchmark" / "splits" / "score_exclude_v3.txt"
POOL_IMG = Path("/home/noob/work/el-fault-detection/data/labeled/images")
V11 = Path("/home/noob/work/bench_data/masks_v11")
E1 = Path("/home/noob/work/el_f1/reports/f1/ext117")
ROWS1 = Path("/home/noob/work/bench_reads/rows1/cache")
OPEN = Path("/home/noob/work/bench_reads/open_final/records/set")
T3B = Path("/home/noob/work/bench_reads/t3b_open9")
RELAY_OPEN = Path("/mnt/nas/noob_el_archive/bench_relay/open")
RELAY_T3B = Path("/mnt/nas/noob_el_archive/bench_relay/t3bopen")
RELAY_W1C = Path("/home/noob/work/bench_relay/w1c")
RELAY_ROWS1 = Path("/home/noob/work/bench_relay/rows1")
WT = Path("/home/noob/work/bench_wt_w2")


def f1(c):
    a, b, cc, d = c
    P = a / b if b > 0 else 0.0
    R = cc / d if d > 0 else 0.0
    return 2 * P * R / (P + R) if P + R > 0 else 0.0


def rel2(pred, gt, keep):
    g, p = (gt == CRACK) & keep, (pred == CRACK) & keep
    dg = ndi.distance_transform_edt(~g) if g.any() else np.full(g.shape, np.inf)
    dp = ndi.distance_transform_edt(~p) if p.any() else np.full(g.shape, np.inf)
    return [int((dg[p] <= 2).sum()), int(p.sum()), int((dp[g] <= 2).sum()), int(g.sum())]


def pick_idx(n, q):
    return math.floor(q * (n - 1))


# ------------------------------------------------------------------ Q1 pool (cv5v2)
Q1_ARMS = {"PF": ("PF", "w1c1_pf_v11"), "hanifi": ("hanifi_vgg16_unet_pf", "r1_hanifi_vgg16_unet_pf"),
           "ucf": ("ucf_dlv3_r50_pf", "r1_ucf_dlv3_r50_pf"), "pratt": ("pratt_dlv3p_wcec", "r1_pratt_dlv3p_wcec")}
Q1_SEEDS = {"PF": (5, 6, 7, 8, 9), "hanifi": (5, 6), "ucf": (5, 6), "pratt": (5, 6)}   # all available seeds per arm
REDUMP = Path("/home/noob/work/ee511_qual/redump")


def f21_picks(cand, fourth=False):
    """F21 rule on cand sorted by (gain, stem): median, 25th percentile, largest loss (lowest gain not already picked);
    with fourth, a 90th percentile row first."""
    n = len(cand)
    picks = [("90th pct gain", cand[pick_idx(n, 0.90)])] if fourth else []
    picks += [("median gain", cand[pick_idx(n, 0.50)]), ("25th pct gain", cand[pick_idx(n, 0.25)])]
    used = {p[1]["stem"] for p in picks}
    assert len(used) == len(picks), "percentile picks coincide"
    picks.append(("largest loss", next(t for t in cand if t["stem"] not in used)))
    return picks


def q1_records():
    per, fold = {}, {}
    for arm, (d, pre) in Q1_ARMS.items():
        for k in range(5):
            for s in Q1_SEEDS[arm]:
                fs = glob.glob(str(ROWS1 / d / f"{pre}_f{k}_s{s}" / "rec_argmax_*.json"))
                assert len(fs) == 1, (arm, k, s, fs)
                rec = json.load(open(fs[0]))
                for st, c in rec.items():
                    per.setdefault(st, {}).setdefault(arm, {})[s] = c["crack_rel2"]
                    if arm == "PF":
                        assert fold.setdefault(st, k) == k
    return per, fold


def q1_select():
    per, fold = q1_records()
    excl = {l.strip() for l in open(EXCL) if l.strip() and not l.startswith("#")}
    assert len(per) == 532, len(per)
    tab = []
    for st, d in per.items():
        gp = d["PF"][5][3]
        m = {a: float(np.mean([f1(d[a][s]) for s in Q1_SEEDS[a]])) for a in Q1_ARMS}
        s5 = {a: f1(d[a][5]) for a in Q1_ARMS}
        lit = np.mean([m["hanifi"], m["ucf"], m["pratt"]])
        tab.append(dict(stem=st, fold=fold[st], gp=gp, clean=st not in excl, mean=m, s5=s5, gain=m["PF"] - lit,
                        rec5={a: d[a][5] for a in Q1_ARMS}))
    cand = sorted([t for t in tab if t["clean"] and t["gp"] >= MINPX], key=lambda t: (t["gain"], t["stem"]))
    n = len(cand)
    picks = f21_picks(cand)
    pooled = {a: float(np.mean([f1(np.sum([per[s][a][sd] for s in per], 0)) for sd in Q1_SEEDS[a]])) for a in Q1_ARMS}
    return picks, n, pooled


def _wt_imports():
    import importlib
    sys.path.insert(0, str(WT))
    aug = importlib.import_module("src.data.augmentations")
    bel = importlib.import_module("src.data.benchmark_el")
    mf = importlib.import_module("src.models.model_factory")
    cfgm = importlib.import_module("src.utils.config")
    return aug, bel, mf, cfgm


def q1_predict(arm, k, stems):
    import torch
    from torch.utils.data import DataLoader
    aug, bel, mf, cfgm = _wt_imports()
    torch.set_num_threads(8)
    pre = Q1_ARMS[arm][1]
    run = f"{pre}_f{k}_s5"
    ed = RELAY_ROWS1 / run / "experiments" / run
    cfg = cfgm.load_config(ed / "config_used.yaml")
    st = torch.load(ed / "checkpoints" / "slim.pth", map_location="cpu", weights_only=False)
    assert int(st["step"]) == 20000 and "model" in st["models"]
    mc = {kk: v for kk, v in cfg["model"].items() if kk not in ("encoder_init", "decoder_init", "encoder_weights_file")}
    for kk in ("encoder_weights", "backbone_weights"):
        if kk in mc or kk == "encoder_weights":
            mc[kk] = None
    m = mf.build_model(mc)
    m.load_state_dict(st["models"]["model"])
    m.eval()
    d = cfg["data"]
    ds = bel.BenchmarkELDataset(POOL_IMG, None, stems, aug.get_weak_augmentation(d.get("mean", [0.5]), d.get("std", [0.25]),
                                                                              d["input_size"]))
    out = {}
    with torch.no_grad():
        for b in DataLoader(ds, batch_size=4, shuffle=False, num_workers=0):
            lg = m(b["image"]).float()
            for s, p in zip(b["stem"], lg.argmax(1).numpy().astype(np.uint8)):
                out[s] = p
    od = REDUMP / run / f"cv5v2_f{k}"
    od.mkdir(parents=True, exist_ok=True)
    for s, p in out.items():
        np.savez_compressed(od / f"{s}.npz", pred=p)
    json.dump({"run": run, "set": f"cv5v2_f{k}", "stems": sorted(out), "checkpoint": str(ed / "checkpoints" / "slim.pth"),
               "step": int(st["step"]), "weights_key": "model", "device": "cpu", "precision": "fp32", "decision": "argmax24",
               "predict_path": "bench_infer.py predict (eval transform, logits argmax), code /home/noob/work/bench_wt_w2",
               "note": "EE511 figure re-dump; the original cv02 dumps were deleted"}, open(od / "manifest.json", "w"), indent=1)
    return out, str(ed / "checkpoints" / "slim.pth")


def pool_gt(stem):
    gt = np.array(Image.open(V11 / "masks" / f"{stem}.png"))
    keep = ~(np.array(Image.open(V11 / "ignore" / f"{stem}.png")) > 0)
    return gt, keep


def pf_dump(k, stem, s=5):
    run = f"w1c1_pf_v11_f{k}_s{s}"
    return RELAY_W1C / run / "dumps" / "elbench1" / "house_r34_unetpp_pf_v11" / run / f"cv5v2_f{k}" / f"{stem}.npz"


# ------------------------------------------------------------------ Q2 / Q3 E1
E1_SEEDS = (5, 6, 7, 8, 9)
T3B_SEEDS = (5, 6, 7)


def c1_name(s):
    return f"fin_pf_v11_pool_s{s}.e1_106"


def c2_name(s):
    return f"fin_hrnet_swad_v11_pool_s{s}.swad.tta_d4.e1_106"


def c1_dump(stem, s=5):
    n = c1_name(s)
    return RELAY_OPEN / n / "dumps" / "elbench1" / "house_r34_unetpp_pf_v11" / n / "e1_106" / f"{stem}.npz"


def c2_dump(stem, s=5):
    n = c2_name(s)
    return RELAY_OPEN / n / "dumps" / "elbench1" / "hrnet_w18_unetpp_swad_const_pf_v11" / n / "e1_106" / f"{stem}.npz"


def t3b_fold():
    fold = {}
    for k in range(5):
        n = f"t3b_all_f{k}_s5.swad.tta_d4.e1t3b_f{k}"
        dd = RELAY_T3B / n / "dumps" / "elbench1" / "hrnet_w18_unetpp_swad_const_pf_v11" / n / f"e1t3b_f{k}"
        for f in dd.glob("*.npz"):
            assert f.stem not in fold
            fold[f.stem] = k
    assert len(fold) == 106, len(fold)
    return fold


def all_dump(stem, k, s=5):
    n = f"t3b_all_f{k}_s{s}.swad.tta_d4.e1t3b_f{k}"
    return RELAY_T3B / n / "dumps" / "elbench1" / "hrnet_w18_unetpp_swad_const_pf_v11" / n / f"e1t3b_f{k}" / f"{stem}.npz"


def oof_check(stem, k):
    """The ALL map of stem comes from model t3b_all_f{k} on its held-out set e1t3b_f{k}; the stem is not in that run's
    train list when the list is readable here (bench_infer also refused any overlap at dump time)."""
    d = all_dump(stem, k).parent
    m = json.load(open(d / "manifest.json"))
    assert m["run_id"] == f"t3b_all_f{k}_s5.swad.tta_d4.e1t3b_f{k}" and m["set"] == f"e1t3b_f{k}", (m["run_id"], m["set"])
    assert stem in m.get("cells", {stem: 1}), stem
    tr = Path(str(m.get("split_def", ""))) / "splits" / "train.txt"
    out = {"run_id": m["run_id"], "set": m["set"], "split_def": m.get("split_def"), "split_md5": m.get("split_md5")}
    if tr.exists():
        trs = {l.strip() for l in open(tr) if l.strip()}
        assert stem not in trs, (stem, tr)
        out["train_list_checked"] = str(tr)
    else:
        out["train_list_checked"] = "not on gaint (bench_infer overlap guard at dump time)"
    return out


def subsets():
    return {k: {l.strip() for l in open(T3B / "subsets" / f"{k}.txt") if l.strip()} for k in ("full", "halfcut", "hard")}


def e1_gt(stem):
    gt = np.array(Image.open(E1 / "masks" / f"{stem}.png"))
    keep = ~(np.array(Image.open(E1 / "ignore" / f"{stem}.png")) > 0)
    return gt, keep


def recs(paths):
    return [json.load(open(p))["cells"] for p in paths]


def q2_select():
    C1 = recs([OPEN / f"{c1_name(s)}.json" for s in E1_SEEDS])
    C2 = recs([OPEN / f"{c2_name(s)}.json" for s in E1_SEEDS])
    S = subsets()
    tab = []
    for st in C1[0]:
        a = [f1(r[st]["crack_rel2"]) for r in C1]
        b = [f1(r[st]["crack_rel2"]) for r in C2]
        tab.append(dict(stem=st, gp=C1[0][st]["crack_rel2"][3], c1=float(np.mean(a)), c2=float(np.mean(b)),
                        c1s5=a[0], c2s5=b[0], gain=float(np.mean(b) - np.mean(a)),
                        kind="full" if st in S["full"] else "half-cut", hard=st in S["hard"]))
    cand = sorted([t for t in tab if t["gp"] >= MINPX], key=lambda t: (t["gain"], t["stem"]))
    picks = f21_picks(cand, fourth=True)
    # pooled check against the opening read levels (C1 0.447, C2 0.490)
    pooled = {}
    for nm, R in (("C1", C1), ("C2", C2)):
        pooled[nm] = float(np.mean([f1(np.sum([r[s]["crack_rel2"] for s in r], 0)) for r in R]))
    return picks, dict(n=len(cand)), pooled


def q3_select():
    ZS = recs([T3B / "records" / "zs" / f"{c2_name(s)}.json" for s in T3B_SEEDS])
    AL = recs([T3B / "records" / "oof" / f"t3b_all_s{s}.oof.json" for s in T3B_SEEDS])
    S = subsets()
    tab = []
    for st in ZS[0]:
        a = [f1(r[st]["crack_rel2"]) for r in ZS]
        b = [f1(r[st]["crack_rel2"]) for r in AL]
        assert ZS[0][st]["crack_rel2"][3] == AL[0][st]["crack_rel2"][3]
        tab.append(dict(stem=st, gp=ZS[0][st]["crack_rel2"][3], zs=float(np.mean(a)), al=float(np.mean(b)), zss5=a[0],
                        als5=b[0], gain=float(np.mean(b) - np.mean(a)),
                        kind="full" if st in S["full"] else "half-cut", hard=st in S["hard"]))
    cand = sorted([t for t in tab if t["gp"] >= MINPX], key=lambda t: (t["gain"], t["stem"]))
    picks = f21_picks(cand, fourth=True)
    pooled = {}
    for nm, R in (("ZS", ZS), ("ALL", AL)):
        pooled[nm] = float(np.mean([f1(np.sum([r[s]["crack_rel2"] for s in r], 0)) for r in R]))
    return picks, dict(n=len(cand)), pooled


# ------------------------------------------------------------------ drawing
def grey(path):
    return np.array(Image.open(path).convert("L"), dtype=np.uint8)


def overlay(g, crack, inact, alpha=0.45):
    rgb = np.repeat(g[..., None].astype(np.float32), 3, axis=2)
    if inact is not None and inact.any():
        rgb[inact] = (1 - alpha) * rgb[inact] + alpha * COL_INACT
    if crack is not None and crack.any():
        c = ndi.binary_dilation(crack, structure=np.ones((3, 3), bool))
        rgb[c] = COL_CRACK
    return np.clip(rgb, 0, 255).astype(np.uint8)


PADV = 222   # display grey for padding px (image 255 where the GT is class 7 = padding)


def padg(g, gt):
    g = g.copy()
    g[(gt == 7) & (g == 255)] = PADV
    return g


def ov(g, m, keep):
    return overlay(g, (m == CRACK) & keep, (m == INACT) & keep)


def figure(rows, titles, path, cap_fs=None, footer=""):
    """rows: list of lists of (image RGB, caption). One PNG, 16 in wide at 150 dpi (2400 px)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch
    plt.rcParams.update({"font.family": "DejaVu Sans"})
    ncol = len(titles)
    W, lm, gap = 16.0, 0.06, 0.07
    pw = (W - 2 * lm - (ncol - 1) * gap) / ncol
    cap_fs = cap_fs or (19 if ncol > 4 else 22)
    sub_fs = 17 if ncol > 4 else 20
    top = 0.16 + 26 / 72 * 1.25 + (sub_fs / 72 * 1.3 if any(t[1] for t in titles) else 0) + 0.12
    caph = cap_fs / 72 * 1.45 + (cap_fs - 4) / 72 * 1.35 + 0.08
    rowgap = 0.16
    leg = 0.85 + (0.45 if footer else 0)
    H = top + len(rows) * (pw + caph) + (len(rows) - 1) * rowgap + leg
    fig = plt.figure(figsize=(W, H), dpi=150, facecolor="white")
    for j, (t, sub) in enumerate(titles):
        x = (lm + j * (pw + gap) + pw / 2) / W
        fig.text(x, 1 - 0.12 / H, t, ha="center", va="top", fontsize=26, fontweight="bold")
        if sub:
            fig.text(x, 1 - (0.16 + 26 / 72 * 1.25) / H, sub, ha="center", va="top", fontsize=sub_fs)
    y = H - top
    for row in rows:
        y -= pw
        for j, (im, cap) in enumerate(row):
            ax = fig.add_axes([(lm + j * (pw + gap)) / W, y / H, pw / W, pw / H])
            ax.imshow(im, interpolation="antialiased" if pw * 150 < 512 else "nearest")
            ax.set_xticks([]); ax.set_yticks([])
            for sp in ax.spines.values():
                sp.set_color("#8c8c8c"); sp.set_linewidth(0.8)
            cx = (lm + j * (pw + gap) + pw / 2) / W
            c1, c2 = (cap if isinstance(cap, tuple) else (cap, ""))
            fig.text(cx, (y - 0.06) / H, c1, ha="center", va="top", fontsize=cap_fs)
            if c2:
                fig.text(cx, (y - 0.08 - cap_fs / 72 * 1.3) / H, c2, ha="center", va="top", fontsize=cap_fs - 4,
                         color="#444444")
        y -= caph + rowgap
    fig.legend(handles=[Patch(color=COL_CRACK / 255, label="crack (class 14)"),
                        Patch(color=COL_INACT / 255, alpha=0.6, label="inactive area (class 11)"),
                        Patch(facecolor=(PADV / 255,) * 3, edgecolor="#8c8c8c", label="padding (outside the cell)")],
               loc="lower center", ncol=3, frameon=False, fontsize=22,
               bbox_to_anchor=(0.5, (0.15 + (0.45 if footer else 0)) / H),
               handlelength=1.6, handleheight=1.0, columnspacing=2.5)
    if footer:
        fig.text(0.5, 0.12 / H, footer, ha="center", va="bottom", fontsize=18, color="#444444", style="italic")
    fig.savefig(path, dpi=150, facecolor="white")
    plt.close(fig)


E1_FOOT = "E1 illustration after the registered read; decides nothing."


def src_of(stem):
    return stem.split("_")[0]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    notes = {}
    # ---------------- Q1
    picks, n, pooled = q1_select()
    print("Q1 candidates", n, "pooled relF1@2 (all seeds per arm)", {k: round(v, 4) for k, v in pooled.items()})
    pred = {a: {} for a in ("hanifi", "ucf", "pratt")}
    ckpt = {a: {} for a in pred}
    byfold = {}
    for _, t in picks:
        byfold.setdefault(t["fold"], []).append(t["stem"])
    for a in pred:
        for k, stems in byfold.items():
            p, c = q1_predict(a, k, sorted(stems))
            pred[a].update(p)
            ckpt[a][k] = c
    rows, q1n = [], []
    for lab, t in picks:
        s, k = t["stem"], t["fold"]
        gt, keep = pool_gt(s)
        g = padg(grey(POOL_IMG / f"{s}.png"), gt)
        pf = np.load(pf_dump(k, s))["pred"]
        chk = {"PF": rel2(pf, gt, keep) == t["rec5"]["PF"]}
        for a in pred:
            chk[a] = (rel2(pred[a][s], gt, keep), t["rec5"][a])
        print("Q1", lab, s, "fold", k, "check (recomputed vs record):", chk)
        m2 = lambda a: f"mean {t['mean'][a]:.2f} ({len(Q1_SEEDS[a])} seeds)"  # noqa: E731
        rows.append([(np.repeat(g[..., None], 3, 2), (f"{src_of(s)} cell", f"{t['gp']} crack px")),
                     (ov(g, gt, keep), (lab, "of Ours vs the 3 others")),
                     (ov(g, pf, keep), (f"relF1@2 {t['s5']['PF']:.2f}", m2("PF"))),
                     (ov(g, pred['hanifi'][s], keep), (f"relF1@2 {f1(rel2(pred['hanifi'][s], gt, keep)):.2f}", m2("hanifi"))),
                     (ov(g, pred['ucf'][s], keep), (f"relF1@2 {f1(rel2(pred['ucf'][s], gt, keep)):.2f}", m2("ucf"))),
                     (ov(g, pred['pratt'][s], keep), (f"relF1@2 {f1(rel2(pred['pratt'][s], gt, keep)):.2f}", m2("pratt")))])
        q1n.append(dict(label=lab, stem=s, fold=k, gt_crack_px=t["gp"], gain=t["gain"], mean=t["mean"], s5=t["s5"],
                        s5_cpu={a: f1(rel2(pred[a][s], gt, keep)) for a in pred},
                        rec_check={a: (v if isinstance(v, bool) else v[0] == v[1]) for a, v in chk.items()},
                        pf_dump=str(pf_dump(k, s))))
    figure(rows, [("Image", ""), ("Ground truth", ""), ("Ours", "U-Net++ PF"), ("Hanifi 2025", "VGG16 U-Net"),
                  ("UCF-EL", "DeepLabV3 R50"), ("Pratt", "DeepLabV3+ wCE")], OUT / "qual_pool_methods.png")
    notes["Q1"] = dict(n_cand=n, pooled=pooled, rows=q1n, ckpt={a: {str(k): v for k, v in d.items()} for a, d in ckpt.items()})
    # ---------------- Q2
    picks, n, pooled = q2_select()
    print("Q2", n, "pooled", pooled)
    rows, q2n = [], []
    for lab, t in picks:
        s = t["stem"]
        gt, keep = e1_gt(s)
        g = padg(grey(E1 / "images" / f"{s}.png"), gt)
        c1 = np.load(c1_dump(s))["pred"]
        c2 = np.load(c2_dump(s))["pred"]
        assert abs(f1(rel2(c1, gt, keep)) - t["c1s5"]) < 1e-9 and abs(f1(rel2(c2, gt, keep)) - t["c2s5"]) < 1e-9, s
        kind = "half-cut + scuff" if t["hard"] else t["kind"]
        rows.append([(np.repeat(g[..., None], 3, 2), (f"{src_of(s)} {kind} cell", f"{t['gp']} crack px")),
                     (ov(g, gt, keep), (lab, "of Final vs Baseline")),
                     (ov(g, c1, keep), (f"relF1@2 {t['c1s5']:.2f}", f"mean {t['c1']:.2f} (5 seeds)")),
                     (ov(g, c2, keep), (f"relF1@2 {t['c2s5']:.2f}", f"mean {t['c2']:.2f} (5 seeds)"))])
        q2n.append(dict(label=lab, **t, c1_dump=str(c1_dump(s)), c2_dump=str(c2_dump(s))))
        print("Q2", lab, s, t)
    figure(rows, [("Image", ""), ("Ground truth", ""), ("Baseline", "PF (C1)"), ("Final", "HRNet + SWAD + D4 (C2)")],
           OUT / "qual_e1_final.png", footer=E1_FOOT)
    notes["Q2"] = dict(n_cand=n, pooled=pooled, rows=q2n)
    # ---------------- Q3
    picks, n, pooled = q3_select()
    print("Q3", n, "pooled", pooled)
    fold = t3b_fold()
    rows, q3n = [], []
    for lab, t in picks:
        s = t["stem"]
        gt, keep = e1_gt(s)
        g = padg(grey(E1 / "images" / f"{s}.png"), gt)
        zs = np.load(c2_dump(s))["pred"]
        al = np.load(all_dump(s, fold[s]))["pred"]
        oofchk = oof_check(s, fold[s])
        print("Q3 OOF check", s, oofchk)
        assert abs(f1(rel2(zs, gt, keep)) - t["zss5"]) < 1e-9 and abs(f1(rel2(al, gt, keep)) - t["als5"]) < 1e-9, s
        kind = "half-cut + scuff" if t["hard"] else t["kind"]
        rows.append([(np.repeat(g[..., None], 3, 2), (f"{src_of(s)} {kind} cell", f"{t['gp']} crack px")),
                     (ov(g, gt, keep), (lab, "of Few-shot vs Zero-shot")),
                     (ov(g, zs, keep), (f"relF1@2 {t['zss5']:.2f}", f"mean {t['zs']:.2f} (3 seeds)")),
                     (ov(g, al, keep), (f"relF1@2 {t['als5']:.2f}", f"mean {t['al']:.2f} (3 seeds)"))])
        q3n.append(dict(label=lab, fold=fold[s], **t, zs_dump=str(c2_dump(s)), all_dump=str(all_dump(s, fold[s])), oof=oofchk))
        print("Q3", lab, s, t)
    figure(rows, [("Image", ""), ("Ground truth", ""), ("Zero-shot", "final model C2"), ("Few-shot", "C2 fine-tuned on E1 (ALL)")],
           OUT / "qual_e1_fewshot.png", footer=E1_FOOT)
    notes["Q3"] = dict(n_cand=n, pooled=pooled, rows=q3n)
    json.dump(notes, open(OUT / "qual_notes.json", "w"), indent=1, default=float)
    print("DONE")


if __name__ == "__main__":
    main()
