"""F21: qualitative CV5 examples on P532 pool cells: image, v1.1 label, PF and C2-recipe (CS_D4) out-of-fold predictions.

Dumps (all cv5v3 held-out folds, pool cells only):
  PF    = c3_pf_v11_f{k}_s{s} plain, relay c3base   (the comparator of FINAL_TTA_READ.md; OP-A = argmax = dump 'pred')
  CS_D4 = c3x_hrnet_swad_v11_f{k}_s{s}.swad.tta_d4, relay fin (queue fin, 75 D4 dumps; FINAL_TTA_READ.md l4)
Per-cell relF1@2 = the frozen per-cell formula (bench/metrics_v02.py cell_values, md5 2f95427d; counts as
bench/score_ext.py rel_counts, md5 75ae55e9): P = pred crack px within 2 px of GT crack / pred crack px (0 if none),
R = GT crack px within 2 px of pred crack / GT crack px, F1 = 2PR / (P + R) (0 if P + R = 0); keep = v1.1 not ignore.

Selection rule (fixed before any per-cell value was computed):
  candidates = the 416 clean cells (benchmark/splits/score_exclude_v3.txt removed) with >= 20 v1.1 GT crack px
  (the frozen per-cell eligibility, MIN_GT_CELL = 20). Per cell and arm, relF1@2 per seed, mean over seeds 5 to 9.
  gain = CS_D4 mean - PF mean. Sort by (gain, stem); n candidates; pick index floor(0.50 (n - 1)) (median) and
  floor(0.25 (n - 1)) (25th percentile); plus one failure. Failure rule changed by the lead on 23 Nov (the first rule was
  the lowest CS_D4 mean relF1@2): the largest loss of the C2 recipe against PF on the 5-seed mean relF1@2 (lowest gain)
  among the candidates, ties by stem, skipping a cell already picked. Panels show seed 5 of each arm.
Check: pooled relF1@2 (sum counts over the 532 cells per seed, mean over seeds) must equal T5 / FINAL_TTA_READ levels
(PF 0.846, CS_D4 0.868).
"""
import math
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
from scipy import ndimage as ndi  # noqa: E402

import figB_common as C  # noqa: E402

NAME = "F21"
SEEDS = (5, 6, 7, 8, 9)
RELAY = Path("/home/noob/work/bench_relay")
EXCL = C.BENCH / "splits" / "score_exclude_v3.txt"
CACHE = C.LOGS / "F21_percell_counts.tsv"


def dump_path(arm: str, k: int, s: int, stem: str) -> Path:
    if arm == "PF":
        run = f"c3_pf_v11_f{k}_s{s}"
        return RELAY / "c3base" / run / "dumps" / "elbench1" / "house_r34_unetpp_pf_v11" / run / f"cv5v3_f{k}" / f"{stem}.npz"
    if arm == "CS_D4":
        run = f"c3x_hrnet_swad_v11_f{k}_s{s}.swad.tta_d4"
        return (RELAY / "fin" / run / "dumps" / "elbench1" / "hrnet_w18_unetpp_swad_const_pf_v11" / run / f"cv5v3_f{k}"
                / f"{stem}.npz")
    raise ValueError(arm)


def rel2(pred: np.ndarray, gt: np.ndarray, keep: np.ndarray) -> list[int]:
    """[pred px within 2 of GT, pred px, GT px within 2 of pred, GT px] (score_ext.rel_counts, r = 2)."""
    g, p = (gt == C.CRACK) & keep, (pred == C.CRACK) & keep
    dg = ndi.distance_transform_edt(~g) if g.any() else np.full(g.shape, np.inf)
    dp = ndi.distance_transform_edt(~p) if p.any() else np.full(g.shape, np.inf)
    return [int((dg[p] <= 2).sum()), int(p.sum()), int((dp[g] <= 2).sum()), int(g.sum())]


def cell_job(stem: str):
    k = C.fold_of()[stem]
    gt = C.mask_v11(stem)
    keep = gt != C.IGN
    out = []
    for arm in ("PF", "CS_D4"):
        for s in SEEDS:
            p = dump_path(arm, k, s, stem)
            d = C.load_npz(p, stem)
            out.append((stem, k, arm, s, *rel2(d["pred"], gt, keep)))
    return out


def f1cell(a, b, c, d):
    P = a / b if b > 0 else 0.0
    R = c / d if d > 0 else 0.0
    return 2 * P * R / (P + R) if P + R > 0 else 0.0


def compute():
    stems = sorted(C.pool())
    rows = []
    with ProcessPoolExecutor(max_workers=8, initializer=_init) as ex:
        for r in ex.map(cell_job, stems, chunksize=8):
            rows.extend(r)
    with open(CACHE, "w") as f:
        f.write("stem\tfold\tarm\tseed\tr2p\tr2pp\tr2g\tr2gg\n")
        for r in rows:
            f.write("\t".join(map(str, r)) + "\n")


def _init():
    C._FIGNAME = NAME  # workers append to the same read log


def load_cache():
    rows = [l.rstrip("\n").split("\t") for l in open(CACHE)][1:]
    return [(r[0], int(r[1]), r[2], int(r[3]), *map(int, r[4:])) for r in rows]


def main():
    C.set_fig(NAME)
    if "--plot-only" not in sys.argv or not CACHE.exists():
        compute()
    rows = load_cache()
    # pooled check against FINAL_TTA_READ levels
    pooled = {}
    for arm in ("PF", "CS_D4"):
        vals = []
        for s in SEEDS:
            S = np.sum([r[4:] for r in rows if r[2] == arm and r[3] == s], axis=0)
            P, R = S[0] / S[1], S[2] / S[3]
            vals.append(2 * P * R / (P + R))
        pooled[arm] = float(np.mean(vals))
    print("pooled relF1@2 (532 cells, OP-A, mean over seeds):", {k: round(v, 4) for k, v in pooled.items()})
    assert abs(pooled["PF"] - 0.8463) < 6e-4 and abs(pooled["CS_D4"] - 0.8684) < 6e-4, pooled
    excl = {l.strip() for l in open(EXCL) if l.strip() and not l.startswith("#")}
    per = {}
    for r in rows:
        per.setdefault(r[0], {"fold": r[1], "gp": r[7]}).setdefault(r[2], {})[r[3]] = f1cell(*r[4:])
    table = []
    for st, d in per.items():
        pf = np.mean([d["PF"][s] for s in SEEDS]); cs = np.mean([d["CS_D4"][s] for s in SEEDS])
        table.append(dict(stem=st, fold=d["fold"], gt_crack_px=d["gp"], clean=st not in excl, pf=pf, cs=cs, gain=cs - pf,
                          pf5=d["PF"][5], cs5=d["CS_D4"][5]))
    cand = sorted([t for t in table if t["clean"] and t["gt_crack_px"] >= 20], key=lambda t: (t["gain"], t["stem"]))
    n = len(cand)
    i50, i25 = math.floor(0.50 * (n - 1)), math.floor(0.25 * (n - 1))
    picks = [("median gain", cand[i50]), ("25th percentile gain", cand[i25])]
    for t in sorted(cand, key=lambda t: (t["gain"], t["stem"])):
        if t["stem"] not in {p[1]["stem"] for p in picks}:
            picks.append(("failure: largest C2 loss vs PF", t)); break
    print(f"candidates n = {n}; median index {i50}, 25th index {i25}")
    for lab, t in picks:
        print(lab, t)
    plot(picks, n)
    sel = {t["stem"]: lab for lab, t in picks}
    out = []
    for t in sorted(table, key=lambda t: t["stem"]):
        out.append([t["stem"], C.pool_cells()[t["stem"]]["source"], t["fold"], t["gt_crack_px"], int(t["clean"]),
                    int(t["clean"] and t["gt_crack_px"] >= 20), f"{t['pf']:.4f}", f"{t['cs']:.4f}", f"{t['gain']:+.4f}",
                    f"{t['pf5']:.4f}", f"{t['cs5']:.4f}", sel.get(t["stem"], "")])
    C.write_csv(NAME, ["stem", "source", "cv5v3_fold", "gt_crack_px_v11", "clean416", "candidate", "relF1_2_PF_mean_s5to9",
                       "relF1_2_CS_D4_mean_s5to9", "gain_CS_D4_minus_PF", "relF1_2_PF_s5", "relF1_2_CS_D4_s5", "selected_as"], out)
    with open(C.FIG / f"{NAME}_data.csv", "a") as f:
        f.write(f"# pooled check, 532 cells, OP-A, mean over seeds 5-9: PF {pooled['PF']:.4f} (T5 0.8463), "
                f"CS_D4 {pooled['CS_D4']:.4f} (T5 0.8684); candidates {n}; PF dumps relay c3base c3_pf_v11_f*_s*, "
                f"CS_D4 dumps relay fin c3x_hrnet_swad_v11_f*_s*.swad.tta_d4 (/home/noob/work/bench_relay)\n")


def plot(picks, n):
    plt = C.rcparams()
    from matplotlib.patches import Patch
    fig, axes = plt.subplots(len(picks), 4, figsize=(7.0, 1.95 * len(picks)))
    for i, (lab, t) in enumerate(picks):
        s, k = t["stem"], t["fold"]
        g, gt = C.grey(s), C.mask_v11(s)
        keep = gt != C.IGN
        pf = C.load_npz(dump_path("PF", k, 5, s), s)["pred"]
        cs = C.load_npz(dump_path("CS_D4", k, 5, s), s)["pred"]
        ims = [(np.repeat(g[..., None], 3, 2), "image\n"),
               (C.overlay(g, (gt == C.CRACK) & keep, (gt == C.INACT) & keep), "label v1.1\n"),
               (C.overlay(g, (pf == C.CRACK) & keep, (pf == C.INACT) & keep),
                f"PF, seed 5\nrelF1@2 {t['pf5']:.3f}"),
               (C.overlay(g, (cs == C.CRACK) & keep, (cs == C.INACT) & keep),
                f"C2 recipe (CS_D4), seed 5\nrelF1@2 {t['cs5']:.3f}")]
        for j, (im, ttl) in enumerate(ims):
            ax = axes[i, j]
            ax.imshow(im, interpolation="none")
            ax.set_xticks([]); ax.set_yticks([])
            ax.set_title(ttl, fontsize=C.fs(6.5))
        axes[i, 0].set_ylabel(f"{lab}\n{s}\nfold {k}; 5-seed mean\nPF {t['pf']:.3f}, C2 {t['cs']:.3f}, "
                              f"gain {t['gain']:+.3f}", fontsize=C.fs(6))
    fig.legend(handles=[Patch(color=C.COL_CRACK, label="crack (class 14), drawn 1 px dilated"),
                        Patch(color=C.COL_INACT, alpha=0.6, label="inactive (class 11), 45% tint")],
               loc="lower center", ncol=2, frameon=False, bbox_to_anchor=(0.5, -0.01))
    # no figure title (lead ruling 23 Nov): the caption carries the scope text
    fig.subplots_adjust(wspace=0.03, hspace=0.22, top=0.96, bottom=0.04)
    C.save(fig, NAME)


if __name__ == "__main__":
    main()
