"""F20: few-shot track (T3b, E1 opening #9). (a) crack relF1@2 contrasts ALL - ZS, HALF - ZS, ALL - HALF with seed-aware
95% intervals, all 106 cells and per stratum; (b) relF1@2 levels of ALL, HALF, ZS (mean over seeds 5 to 7, bar = range over
seeds, not an interval). Only P = ALL - ZS on all cells decides; strata decide nothing.

Sources (registered read outputs only):
- results/t3b_open9_read/verdict.txt (VT, md5 bfe583db): l5 (n), l6 (P, M), l9 (outcome), l17 to l18 (printed beside),
  l26 to l30 and l32 (strata), l36 to l44 (per model; check of the panel-b range ends on all cells);
- results/t3b_open9_read/read_t3b/read.txt (RT, md5 922b965e): levels per subset (mean [min, max] over the 3 seeds);
- results/t3b_open9_read/read_t3b/read.json (md5 1589711a): cross-check of every plotted contrast and level.
Not drawn: BMRK (5 cells, VT l33) and crack-free cells (74 cells, VT l31), both degenerate; they are in the CSV.
"""
import hashlib
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.transforms as mtransforms  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

import figA_common as C  # noqa: E402

VT = "results/t3b_open9_read/verdict.txt"
RT = "results/t3b_open9_read/read_t3b/read.txt"
RJ = "results/t3b_open9_read/read_t3b/read.json"
MD5 = {VT: "bfe583db", RT: "922b965e", RJ: "1589711a"}
for rel, want in MD5.items():
    with open(os.path.join(C.T, rel), "rb") as f:
        got = hashlib.md5(f.read()).hexdigest()
    assert got.startswith(want), f"{rel}: md5 {got} != {want}"

C.setup()
NUM, IV = C.NUM, C.IV

# ---- primary contrast P and the contrasts printed beside it (all cells)
hdr = C.find(VT, r"^## T3b opening #9: the primary contrast P = ALL - ZS \(pooled out-of-fold crack relF1@2, OP-A, "
                 r"(\d+) cells, (\d+) clusters\)$")
p = C.find(VT, rf"^Delta ({NUM}), seed-aware 95% interval \[({NUM}), ({NUM})\] \(SE ({NUM})\); M ({NUM})$")
outc = C.find(VT, r"^=> P: (CONFIRMED|NOT CONFIRMED|\S+)$")
M = p.f(4)
SEC_B = r"^## Printed beside \(decide nothing\)"
hz = C.find(VT, r"^HALF - ZS \(.*?\): relF1@2 " + IV, section=SEC_B)
ah = C.find(VT, r"^ALL - HALF \(.*?\): relF1@2 " + IV, section=SEC_B)

CONS = [("ALL - ZS", C.BLUE, "s"), ("HALF - ZS", C.VERM, "D"), ("ALL - HALF", C.GREEN, "^")]
ARMS = [("ALL", r"ALL", C.BLUE, "s"), ("HALF", r"HALF", C.VERM, "D"), ("ZS", r"ZS \(zero-shot comparator\)", C.GREY, "o")]

# groups: label, verdict key (None = all cells), read.txt / read.json subset key
GROUPS = [("All cells", None, "all"),
          ("Full", "strat_full", "strat_full"),
          ("Half-cut", "strat_halfcut", "strat_halfcut"),
          ("Hard", "strat_hard", "strat_hard"),
          ("Half-cut without\nscuff", "strat_halfcut_noscuff", "strat_halfcut_noscuff"),
          ("Crack cells", "crack_cells", "crack_cells"),
          ("CSIR", "src:CSIR", "src:CSIR")]
LEFT_OUT = [("BMRK", "src:BMRK"), ("Crack-free cells", "crack_free_cells")]
SEC_S = r"^## Strata \(decide nothing\)"
STRAT = (r"^[^\t]*\({key}\)\t(\d+) / (\d+)\tALL - ZS relF1@2 " + IV + "; HALF - ZS relF1@2 " + IV
         + "; ALL - HALF relF1@2 " + IV + ";")

rj = C.load_json(RJ)


def chk(a: float, b: float, what: str) -> None:
    assert abs(a - b) < 5e-5, f"{what}: printed {a} vs read.json {b}"


data = []  # per group: dict
for lab, vkey, skey in GROUPS:
    g = {"label": lab, "skey": skey, "con": {}, "lev": {}}
    if vkey is None:
        g["n"], g["ncl"], nsrc = hdr.groups[0], hdr.groups[1], hdr.src
        g["con"]["ALL - ZS"] = (p.groups[0], p.groups[1], p.groups[2], p.src)
        g["con"]["HALF - ZS"] = (*hz.groups[:3], hz.src)
        g["con"]["ALL - HALF"] = (*ah.groups[:3], ah.src)
    else:
        h = C.find(VT, STRAT.format(key=re.escape(vkey)), section=SEC_S)
        g["n"], g["ncl"], nsrc = h.groups[0], h.groups[1], h.src
        for k, (c, _, _) in enumerate(CONS):
            g["con"][c] = (*h.groups[2 + 3 * k: 5 + 3 * k], h.src)
    g["nsrc"] = nsrc
    # levels from read.txt: mean [min, max] over the 3 seeds
    sec = rf"^## subset {re.escape(skey)}: (\d+) cells, (\d+) clusters$"
    sh = C.find(RT, sec)
    assert sh.groups == (g["n"], g["ncl"]), f"{skey}: n {sh.groups} vs {g['n']} / {g['ncl']}"
    for arm, are, _, _ in ARMS:
        lv = C.find(RT, rf"^\| {are} \| 3 \| ({NUM}) \[({NUM}), ({NUM})\] \|", section=sec)
        g["lev"][arm] = (*lv.groups[:3], lv.src)
        sm = rj["subsets"][skey]["arms"][arm]["summary"]["relF1_2"]
        assert sm["n"] == 3
        chk(lv.f(0), sm["mean"], f"{skey} {arm} mean")
        chk(lv.f(1), sm["min"], f"{skey} {arm} min")
        chk(lv.f(2), sm["max"], f"{skey} {arm} max")
    # cross-check every contrast against read.json (seed-aware relF1@2)
    assert rj["subsets"][skey]["n"] == int(g["n"]) and rj["subsets"][skey]["n_clusters"] == int(g["ncl"])
    for c, _, _ in CONS:
        mj = rj["subsets"][skey]["contrasts"][c]["seed_aware"]["metrics"]["relF1_2"]
        d, lo, hi, _ = g["con"][c]
        chk(C.num(d), mj["delta"], f"{skey} {c} delta")
        chk(C.num(lo), mj["lo"], f"{skey} {c} lo")
        chk(C.num(hi), mj["hi"], f"{skey} {c} hi")
    data.append(g)
assert outc.groups[0] == "CONFIRMED"

# per-model lines (VT l36 to l44): the all-cells range ends of panel b must be per-seed values
SEC_M = r"^## Per model \(OP-A\)"
seeds = {}
for arm, _, _, _ in ARMS:
    for s in (5, 6, 7):
        h = C.find(VT, rf"^{arm} \([^)]*\)\tseed {s}\t({NUM})\t", section=SEC_M)
        seeds[(arm, s)] = h
    vals = [seeds[(arm, s)].f(0) for s in (5, 6, 7)]
    _, lo, hi, _ = data[0]["lev"][arm]
    assert C.num(lo) == min(vals) and C.num(hi) == max(vals), f"{arm}: range vs per-seed"

left = []
for lab, vkey in LEFT_OUT:
    h = C.find(VT, STRAT.format(key=re.escape(vkey)), section=SEC_S)
    left.append((lab, h))

# ---- plot
GAP = 1.2  # extra space between groups; group 0 on top, 3 rows per group
ys, ys_g = [], []
top = (len(GROUPS) - 1) * (3 + GAP) + 2
for gi in range(len(GROUPS)):
    base = top - gi * (3 + GAP)
    ys.append([base, base - 1, base - 2])  # ALL - ZS / ALL, HALF - ZS / HALF, ALL - HALF / ZS
    ys_g.append(base - 1)

fig = plt.figure(figsize=(C.WIDTH, 10.2 * C.CM), layout="constrained")
gs = fig.add_gridspec(1, 2, width_ratios=[1.55, 1.0])
axa = fig.add_subplot(gs[0])
axb = fig.add_subplot(gs[1], sharey=axa)

for gi, g in enumerate(data):
    is_all = gi == 0
    for k, (c, col, mk) in enumerate(CONS):
        d, lo, hi, _ = (C.num(v) if i < 3 else v for i, v in enumerate(g["con"][c]))
        yy = ys[gi][k]
        prim = is_all and c == "ALL - ZS"
        axa.plot([lo, hi], [yy, yy], color=col, lw=1.6 if prim else 1.0, solid_capstyle="butt", zorder=3)
        axa.plot([d], [yy], marker=mk, color=col, ms=5.5 if prim else 4.5, ls="none", zorder=4)
        if prim:
            axa.text(hi + 0.012, yy, "P (decides)", va="center", ha="left", fontsize=8, color=C.DARK)
    for k, (arm, _, col, mk) in enumerate(ARMS):
        m, lo, hi, _ = (C.num(v) if i < 3 else v for i, v in enumerate(g["lev"][arm]))
        yy = ys[gi][k]
        axb.plot([lo, hi], [yy, yy], color=col, lw=1.0, solid_capstyle="butt", zorder=3)
        axb.plot([m], [yy], marker=mk, color=col, ms=4.5, ls="none", zorder=4)
    if gi > 0:
        for ax in (axa, axb):
            ax.axhline(ys[gi][0] + GAP / 2 + 0.5, color=C.GRID, lw=0.8, zorder=0)

C.zero_line(axa)
C.m_line(axa, M)
tr = mtransforms.blended_transform_factory(axa.transData, axa.transAxes)
axa.text(M, 1.005, "M 0.010", transform=tr, ha="left", va="bottom", fontsize=8)
axa.set_yticks(ys_g)
axa.set_yticklabels([g["label"] + ("\n" if "\n" not in g["label"] else " ") + f"({g['n']} / {g['ncl']})" for g in data])
axa.get_yticklabels()[0].set_fontweight("bold")
axa.tick_params(axis="y", length=0)
axa.set_ylim(ys[-1][-1] - 0.7, ys[0][0] + 0.7)
axa.set_xlim(-0.33, 0.56)
axa.set_xlabel("Difference in crack relF1@2,\nseed-aware 95% interval")
axa.grid(axis="x")
axb.set_xlim(0.30, 0.92)
axb.set_xlabel("Crack relF1@2, seed mean\n(bar: range over seeds 5 to 7)")
axb.grid(axis="x")
plt.setp(axb.get_yticklabels(), visible=False)
axb.tick_params(axis="y", length=0)
for ax, t in ((axa, "a"), (axb, "b")):
    ax.text(0.0, 1.02, t, transform=ax.transAxes, fontweight="bold", ha="left", va="bottom")
for ax, items in ((axa, [(c, col, mk) for c, col, mk in CONS]), (axb, [(a, col, mk) for a, _, col, mk in ARMS])):
    ax.legend(handles=[Line2D([], [], marker=mk, color=col, ms=4.5, lw=1.0, label=lab) for lab, col, mk in items],
              loc="upper center", bbox_to_anchor=(0.5, -0.19), ncol=3, handletextpad=0.4, columnspacing=1.0,
              handlelength=1.4)
C.save(fig, "F20")

# ---- data CSV: every plotted value with its source file:line
out = []
for g in data:
    grp = g["label"].replace("\n", " ")
    for c, _, _ in CONS:
        d, lo, hi, src = g["con"][c]
        kind = "P (primary, decides)" if (g["skey"] == "all" and c == "ALL - ZS") else (
            "printed beside (decides nothing)" if g["skey"] == "all" else "stratum (decides nothing)")
        out.append(["a", grp, g["n"], g["ncl"], c, "contrast", d, lo, hi, "seed-aware 95%", kind, "yes",
                    src + ("; n " + g["nsrc"] if g["nsrc"] != src else "")])
    for arm, _, _, _ in ARMS:
        m, lo, hi, src = g["lev"][arm]
        out.append(["b", grp, g["n"], g["ncl"], arm, "level (mean over 3 seeds)", m, lo, hi, "range over seeds 5 to 7",
                    "level", "yes", src])
out.append(["a", "", "", "", "M (decision margin)", "line", p.groups[4], "", "", "", "line", "yes", p.src])
for lab, h in left:
    for k, (c, _, _) in enumerate(CONS):
        out.append(["", lab, h.groups[0], h.groups[1], c, "contrast", *h.groups[2 + 3 * k: 5 + 3 * k], "seed-aware 95%",
                    "stratum (degenerate)", "no (left out)", h.src])
for arm, _, _, _ in ARMS:
    for s in (5, 6, 7):
        h = seeds[(arm, s)]
        out.append(["", "All cells", hdr.groups[0], hdr.groups[1], f"{arm} seed {s}", "per-model level", h.groups[0], "",
                    "", "", "check: panel-b range ends on all cells", "no", h.src])
C.write_csv("F20", ["panel", "group", "cells", "clusters", "series", "quantity", "value", "lo", "hi", "bar",
                    "kind", "drawn", "source"], out)
print("F20 ok", len(data), "groups;", sum(1 for r in out if r[11] == "yes"), "plotted values rows; outcome",
      outc.groups[0])
