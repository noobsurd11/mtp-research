"""F18: severity. (a) predicted vs labelled inactive area fraction a on the P532 pool, PF out of fold (cv5v2 folds, cv02,
seeds 5 to 9; S1). (b), (c) ELPVPower S137 rows (129 used): relative power loss L against predicted inactive area A and
against predicted crack length C (S3).

Sources (read-only): /home/noob/work/bench_reads/severity/S1/cv02/cells/PF/w1c1_pf_v11_f*_s*_*.json (per-cell a in %,
derived inactive region), .../S1/cv02/cells/gt_cddf394e4614.json (GT a), .../S1/cv02/post_eval.txt (pooled values);
/home/noob/work/bench_reads/severity/S3/stats/rows_summary.tsv (per row A, C, L, type) and stats.txt (rho values).
Plotted pool value per cell = mean over the 5 seeds of the predicted a (each seed scores the cell once, out of fold).
"""
import glob
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402

import figB_common as C  # noqa: E402

NAME = "F18"
S1 = Path("/home/noob/work/bench_reads/severity/S1/cv02")
S3 = Path("/home/noob/work/bench_reads/severity/S3/stats")
TYPE_COL = {"T1": C.OI["sky"], "T2": C.OI["orange"], "T3": C.OI["vermillion"]}
TYPE_MARK = {"T1": "o", "T2": "s", "T3": "^"}


def rd(p):
    C.guard_path(p)
    C.log_read("severity_read", p)
    return open(p).read()


def main():
    C.set_fig(NAME)
    plt = C.rcparams()
    P = C.pool()
    gt = json.loads(rd(S1 / "cells" / "gt_cddf394e4614.json"))
    assert set(gt) == P, "GT json is not the 532 pool cells"
    pred = {}
    files = sorted(glob.glob(str(S1 / "cells" / "PF" / "w1c1_pf_v11_f*_s*_*.json")))
    assert len(files) == 25, len(files)
    for f in files:
        k, s = map(int, re.search(r"_f(\d)_s(\d)_", f).groups())
        d = json.loads(rd(f))
        for st, v in d.items():
            C.guard_stem(st)
            pred.setdefault(st, {})[s] = v["a"]
    assert set(pred) == P and all(len(v) == 5 for v in pred.values())
    post = rd(S1 / "post_eval.txt")
    m = re.search(r"^PF\t(\S+ \[\S+ \S+\])\t(\S+ \[\S+ \S+\])\t\S+ \[\S+ \S+\]\t\S+ \[\S+ \S+\]\t(\S+ \[\S+ \S+\])\t\S+ \[\S+ \S+\]\t"
                  r"(\S+ \[\S+ \S+\])", post, re.M)
    mae, bias, sens, kappa = m.groups()
    pc = C.pool_cells()
    rows3 = [l.rstrip("\n").split("\t") for l in rd(S3 / "rows_summary.tsv").splitlines()]
    h3 = rows3[0]; rows3 = [dict(zip(h3, r)) for r in rows3[1:]]
    assert len(rows3) == 129
    stats = rd(S3 / "stats.txt")
    rhoA = re.search(r"rho_A = (\S+ \[\S+ \S+\])", stats).group(1)
    rhoC = re.search(r"rho_C = (\S+ \[\S+ \S+\])", stats).group(1)
    Dm = re.search(r"D = (\S+) \[", stats).group(1)
    tstat = {t: re.search(rf"type {t}: n (\d+) rho_A (\S+) \[(\S+) (\S+)\] rho_C (\S+)", stats).groups() for t in TYPE_COL}

    plt.rcParams.update({"axes.labelsize": C.fs(6.5), "xtick.labelsize": C.fs(6), "ytick.labelsize": C.fs(6)})
    fig, axes = plt.subplots(1, 3, figsize=(7.0, 2.6), gridspec_kw={"wspace": 0.4})
    ax = axes[0]
    data = []
    for src in ("ARTS", "BMRK", "CFVS", "CSIR", "SDLE"):
        st = sorted(s for s in P if pc[s]["source"] == src)
        x = np.array([gt[s]["a"] for s in st]); y = np.array([np.mean([pred[s][k] for k in (5, 6, 7, 8, 9)]) for s in st])
        ax.scatter(x, y, s=9, marker=C.SRC_MARK[src], facecolor="none", edgecolor=C.SRC_COL[src], lw=0.7,
                   label=f"{src} ({len(st)})")
        for s, a, b in zip(st, x, y):
            data.append(["pool", s, src, f"{a:.4f}", f"{b:.4f}", *[f"{pred[s][k]:.4f}" for k in (5, 6, 7, 8, 9)], "", "", "", ""])
    n00 = sum(1 for s in P if gt[s]["a"] == 0 and all(pred[s][k] == 0 for k in pred[s]))
    lim = 40
    ax.plot([0, lim], [0, lim], color=C.OI["grey"], lw=0.7, ls="--", zorder=0)
    ax.set_xscale("symlog", linthresh=0.1, linscale=0.5); ax.set_yscale("symlog", linthresh=0.1, linscale=0.5)
    ax.set_xlim(-0.02, lim); ax.set_ylim(-0.02, lim)
    ax.set_xlabel("labelled inactive area a, %\n(v1.1)")
    ax.set_ylabel("predicted a, %, mean of 5 seeds")
    ax.set_title("(a) P532 pool cells\nPF, out of fold (cv5v2, seeds 5 to 9)", fontsize=C.fs(6.5))
    ax.text(0.03, 0.97, f"MAE {mae.split(' ')[0]} pp\n{mae.split(' ', 1)[1]}\nkappa (3 bands) {kappa.split(' ')[0]}\nsens. at 0.5% {sens.split(' ')[0]}\n{n00} cells at (0, 0)",
            transform=ax.transAxes, va="top", fontsize=C.fs(5.6))
    ax.legend(loc="lower right", fontsize=C.fs(5.2), frameon=False, handletextpad=0.1, borderaxespad=0.1, labelspacing=0.25)
    for j, (key, lab) in enumerate((("A", "predicted inactive area A\n(cell equivalents)"),
                                    ("C", "predicted crack length C\n(skeleton px)"))):
        ax = axes[j + 1]
        for t in ("T1", "T2", "T3"):
            rr = [r for r in rows3 if r["type"] == t]
            ax.scatter([float(r[key]) for r in rr], [float(r["L"]) for r in rr], s=10, marker=TYPE_MARK[t], facecolor="none",
                       edgecolor=TYPE_COL[t], lw=0.7, label=f"{t} (n {len(rr)})")
            if j == 0:
                for r in rr:
                    data.append(["elpvpower", r["idx"], t, "", "", "", "", "", "", "", r["A"], r["C"], r["L"], r["inst"]])
        ax.set_xscale("symlog", linthresh=(0.1 if key == "A" else 100), linscale=0.5)
        ax.set_xlabel(lab)
        if j == 0:
            ax.set_ylabel("relative power loss L = 1 - Pmpp / Pref")
        ax.set_ylim(-0.04, 0.56)
        rho = rhoA if key == "A" else rhoC
        sub = "\n".join(f"{t}: rho {tstat[t][1] if key == 'A' else tstat[t][4]} (n {tstat[t][0]})" for t in TYPE_COL)
        ax.set_title(f"({'bc'[j]}) ELPVPower modules, 129 rows\nrho_{key} {rho}", fontsize=C.fs(6.5))
        ax.text(0.03, 0.97, sub + (f"\nD = rho_A - rho_C {Dm}: NULL" if key == "A" else ""), transform=ax.transAxes,
                va="top", fontsize=C.fs(5.6))
        if j == 1:
            ax.legend(loc="lower right", fontsize=C.fs(5.6), frameon=False, handletextpad=0.2)
    C.save(fig, NAME)
    C.write_csv(NAME, ["panel", "id", "source_or_type", "a_gt_pct", "a_pred_mean_pct", "a_pred_s5", "a_pred_s6", "a_pred_s7",
                       "a_pred_s8", "a_pred_s9", "A_cell_eq", "C_skel_px", "L", "instance"], data)
    with open(C.FIG / f"{NAME}_data.csv", "a") as f:
        f.write(f"# pool: {S1}/cells/PF/w1c1_pf_v11_f*_s*_*.json and gt_cddf394e4614.json; post_eval.txt PF MAE {mae}, "
                f"kappa {kappa}, sens@0.5% {sens}\n# elpvpower: {S3}/rows_summary.tsv; stats.txt rho_A {rhoA}, rho_C {rhoC}, "
                f"D {Dm}\n")
    print("MAE", mae, "kappa", kappa, "sens", sens, "rhoA", rhoA, "rhoC", rhoC, "D", Dm, "n00", n00, tstat)


if __name__ == "__main__":
    main()
