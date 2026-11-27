"""Axis a tables: every label-error candidate (out/a_candidates.tsv), the per-cell ranking (out/a_cells.tsv) and the summary
(out/a_summary.txt): counts per type and source, image support at the fixed and the two printed z thresholds, replication on the
cv5v2 W1-G set, classes under missed-crack / missed-inactive components, share of v1.1 px. Reads out/pass_records.pkl."""
from __future__ import annotations

import collections
import os
import pickle
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402

import common as C  # noqa: E402

NAMES = {0: "background", 1: "sp_multi", 2: "sp_mono", 3: "sp_dogbone", 4: "ribbons", 5: "border", 6: "text", 7: "padding",
         8: "clamp", 9: "busbars", 10: "crack_rbn_edge", 11: "inactive", 12: "rings", 13: "material", 14: "crack", 15: "gridline",
         16: "splice", 17: "dead_cell", 18: "corrosion", 19: "belt_mark", 20: "edge_dark", 21: "frame_edge", 22: "jbox",
         23: "meas_artifact", 255: "ignore"}
SUP = {"MC": (-1.0, (-0.5, -2.0)), "MI": (-1.0, (-0.5, -2.0)), "SC": (-0.5, (0.0, -1.0)), "SI": (-0.5, (0.0, -1.0))}


def supported(t, z, thr=None):
    th = SUP[t][0] if thr is None else thr
    if not np.isfinite(z):
        return False
    return z <= th if t in ("MC", "MI") else z > th


def main():
    d = pickle.load(open(C.OUT / "pass_records.pkl", "rb"))
    cells = d["cells"]
    g3 = C.groups(C.G3)
    rows = []
    for s in sorted(cells):
        for c in cells[s]["cands"]:
            rows.append((s, c))
    # candidates table
    with open(C.OUT / "a_candidates.tsv", "w") as f:
        f.write("stem\tsource\tfold_cv5v3\tgroup\ttype\tkind\tpx\tmean_votes_of_25\tmean_score\tz\tsupported\treplicated_w1g\t"
                "repl_share\tclasses_under\tbbox_y0x0y1x1\n")
        for s, c in sorted(rows, key=lambda r: (r[1]["type"], -r[1]["px"])):
            cl = ";".join(f"{NAMES.get(k, k)}:{v}" for k, v in sorted(c["classes"].items(), key=lambda kv: -kv[1]))
            f.write(f"{s}\t{s.split('_')[0]}\t{g3[s]['fold']}\t{g3[s]['group']}\t{c['type']}\t{c['kind']}\t{c['px']}\t{c['meanV']:.2f}\t"
                    f"{c['meanQ']:.3f}\t{c['z']:.2f}\t{int(supported(c['type'], c['z']))}\t{int(c['repl'])}\t{c['repl_share']:.2f}\t{cl}\t"
                    f"{','.join(map(str, c['bbox']))}\n")
    # per-cell ranking
    with open(C.OUT / "a_cells.tsv", "w") as f:
        f.write("stem\tsource\tgt_crack_px\tgt_inact_px\tsoftmin_crack\tsoftmin_inact\tn_MC\tn_SC\tn_MI\tn_SI\tcand_px\n")
        for s in sorted(cells, key=lambda s: min(cells[s]["softmin_c"], cells[s]["softmin_i"])):
            r = cells[s]
            n = collections.Counter(c["type"] for c in r["cands"])
            f.write(f"{s}\t{s.split('_')[0]}\t{r['g_px']}\t{r['gi_px']}\t{r['softmin_c']:.4f}\t{r['softmin_i']:.4f}\t{n['MC']}\t{n['SC']}\t"
                    f"{n['MI']}\t{n['SI']}\t{r['n_ign']}\n")
    # summary
    L = []
    P = L.append
    srcs = ["ARTS", "BMRK", "CFVS", "CSIR", "SDLE"]
    G = sum(c["g_px"] for c in cells.values())
    GI = sum(c["gi_px"] for c in cells.values())
    gsrc = collections.Counter()
    gisrc = collections.Counter()
    crack_cells = collections.Counter()
    inact_cells = collections.Counter()
    for s, r in cells.items():
        gsrc[s.split("_")[0]] += r["g_px"]
        gisrc[s.split("_")[0]] += r["gi_px"]
        crack_cells[s.split("_")[0]] += r["g_px"] > 0
        inact_cells[s.split("_")[0]] += r["gi_px"] > 0
    P("# a_summary.txt: label-error candidates from the 25-model cv5v3 out-of-fold consensus (rules: PLAN.md section 1a)")
    P(f"pool cells 532; v1.1 crack px {G} in {sum(crack_cells.values())} cells; v1.1 inactive px {GI} in {sum(inactive for inactive in inact_cells.values())} cells")
    P("type | components | cells | px | px as share of v1.1 px of that class | supported (fixed z) | supported at the two printed z | replicated on W1-G")
    for t in ("MC", "SC", "MI", "SI"):
        r = [(s, c) for s, c in rows if c["type"] == t]
        px = sum(c["px"] for s, c in r)
        base = G if t in ("MC", "SC") else GI
        sup = sum(supported(t, c["z"]) for s, c in r)
        a1 = sum(supported(t, c["z"], SUP[t][1][0]) for s, c in r)
        a2 = sum(supported(t, c["z"], SUP[t][1][1]) for s, c in r)
        rep = sum(c["repl"] for s, c in r)
        suppx = sum(c["px"] for s, c in r if supported(t, c["z"]))
        P(f"{t} | {len(r)} | {len({s for s, c in r})} | {px} | {px / base:.4f} | {sup} ({suppx} px, {suppx / base:.4f}) | "
          f"{a1} at z {SUP[t][1][0]}, {a2} at z {SUP[t][1][1]} | {rep} ({rep / max(len(r), 1):.3f})")
    P("\nper source: type | source | components | cells | px | share of the source's v1.1 px of that class | supported components")
    for t in ("MC", "SC", "MI", "SI"):
        for so in srcs:
            r = [(s, c) for s, c in rows if c["type"] == t and s.startswith(so)]
            if not r:
                continue
            px = sum(c["px"] for s, c in r)
            base = gsrc[so] if t in ("MC", "SC") else gisrc[so]
            P(f"{t} | {so} | {len(r)} | {len({s for s, c in r})} | {px} | {px / max(base, 1):.4f} | {sum(supported(t, c['z']) for s, c in r)}")
    P("\nv1.1 crack px / crack cells / inactive px / inactive cells per source: " +
      "; ".join(f"{so} {gsrc[so]} / {crack_cells[so]} / {gisrc[so]} / {inact_cells[so]}" for so in srcs))
    P("\nkind of missed-crack components: " + str(dict(collections.Counter(c["kind"] for s, c in rows if c["type"] == "MC"))))
    for t in ("MC", "MI"):
        cl = collections.Counter()
        for s, c in rows:
            if c["type"] == t:
                for k, v in c["classes"].items():
                    cl[NAMES.get(k, k)] += v
        tot = sum(cl.values())
        P(f"v1.1 classes under {t} px: " + ", ".join(f"{k} {v} ({v / tot:.3f})" for k, v in cl.most_common()))
    # all v1.1 crack components: what share is 'model-rejected' at looser rules (descriptive)
    gc = [x for r in cells.values() for x in r["gcomp"]]
    gc20 = [x for x in gc if x[0] >= 20]
    P(f"\nv1.1 crack components >= 20 px: {len(gc20)}; share with >= 90% px at <= 2 of 25 models within 2 px: "
      f"{np.mean([x[1] >= 0.9 for x in gc20]):.4f}; with >= 50%: {np.mean([x[1] >= 0.5 for x in gc20]):.4f}")
    zz = np.array([x[2] for x in gc20 if np.isfinite(x[2])])
    P(f"image contrast z of all v1.1 crack components >= 20 px: median {np.median(zz):.2f}; share z > -0.5 (not darker than the ring): "
      f"{np.mean(zz > -0.5):.4f}; share z > 0: {np.mean(zz > 0):.4f}  (n {len(zz)})")
    for so in srcs:
        z = np.array([x[2] for s, r in cells.items() if s.startswith(so) for x in r["gcomp"] if x[0] >= 20 and np.isfinite(x[2])])
        if len(z):
            P(f"  {so}: n {len(z)}, median z {np.median(z):.2f}, share z > -0.5 {np.mean(z > -0.5):.3f}")
    ic = [x for r in cells.values() for x in r["icomp"] if x[0] >= 100]
    P(f"v1.1 inactive regions >= 100 px: {len(ic)}; share with >= 90% px at <= 2 of 25 votes: {np.mean([x[1] >= 0.9 for x in ic]):.4f}")
    zi = np.array([x[2] for x in ic if np.isfinite(x[2])])
    P(f"image contrast z of v1.1 inactive regions >= 100 px: median {np.median(zi):.2f}; share z > -0.5: {np.mean(zi > -0.5):.4f}")
    # top cells
    top = sorted(cells, key=lambda s: -cells[s]["n_ign"])[:15]
    P("\ncells with the most candidate px: " + ", ".join(f"{s} ({cells[s]['n_ign']})" for s in top))
    ncand = sum(1 for s in cells if cells[s]["cands"])
    P(f"cells with at least one candidate: {ncand} of 532; of the 229 crack cells: "
      f"{sum(1 for s in cells if cells[s]['g_px'] > 0 and any(c['type'] in ('MC', 'SC') for c in cells[s]['cands']))}")
    sup_cells = {s for s, c in rows if supported(c["type"], c["z"])}
    P(f"cells with at least one supported candidate: {len(sup_cells)}")
    open(C.OUT / "a_summary.txt", "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
