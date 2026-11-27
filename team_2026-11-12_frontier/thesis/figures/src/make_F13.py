"""F13: E1 opening #8, primary contrast P = C2 - C1 and the contrasts printed beside (forest), M 0.010 and MDE 0.074 lines.

Sources: results/final_opening_read/verdict.txt (V8) l11, l43 to l50; verdict.json (cross-check of P);
thesis/THESIS_TABLES.md T8 note (MDE, derived).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matplotlib.transforms as mtransforms  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

import figA_common as C  # noqa: E402

V8 = "results/final_opening_read/verdict.txt"
TT = "thesis/THESIS_TABLES.md"

C.setup()

rows = []  # label, delta, lo, hi, hit, kind
p = C.find(V8, rf"^Delta ({C.NUM}), seed-aware 95% interval \[({C.NUM}), ({C.NUM})\] \(SE ({C.NUM})\); M ({C.NUM})$")
P, PLO, PHI, PSE, M = (p.f(i) for i in range(5))
vj = C.load_json("results/final_opening_read/verdict.json")
assert abs(vj["delta"] - P) < 5e-5 and abs(vj["lo"] - PLO) < 5e-5 and abs(vj["hi"] - PHI) < 5e-5, "text vs json"
rows.append(("P: C2 - C1 (primary, decides)", P, PLO, PHI, p, "P"))

beside = [
    ("C2 - C1-D4 (both 8 views)", r"^C2 - C1-D4 \(same views; descriptive\): relF1@2 "),
    ("C1-D4 - C1 (D4 on PF)", r"^C1-D4 - C1 \(D4 on PF; descriptive\): relF1@2 "),
    ("S1: C3 - C1", r"^S1 C3 - C1 .*?: relF1@2 "),
    ("S2: C3 - E-PF", r"^S2 C3 - E-PF .*?: relF1@2 "),
    ("S3: C3 - C2", r"^S3 C3 - C2 .*?: relF1@2 "),
    ("S4: C2 seed 5 - C1", r"^S4 C2 seed 5 \(deployable\) - C1: relF1@2 "),
    ("S5: E-PF - C1", r"^S5 E-PF - C1: relF1@2 "),
]
for lab, pat in beside:
    h = C.find(V8, pat + C.IV)
    rows.append((lab, h.f(0), h.f(1), h.f(2), h, "beside"))
aa = C.find(V8, r"^A/A C1 \{7,8\} - \{5,6\} \(descriptive\): relF1@2 " + C.IV + rf", SE ({C.NUM})$")
rows.append(("A/A: C1 seeds {7,8} - {5,6}", aa.f(0), aa.f(1), aa.f(2), aa, "aa"))

mde_h = C.find(TT, r"MDE = 2\.80 x SE = 2\.80 x (0\.0265) = (0\.0742)", section=r"^### T8\. ")
MDE = mde_h.f(1)
assert abs(mde_h.f(0) - PSE) < 1e-9

# ---- plot
n = len(rows)
fig = plt.figure(figsize=(C.WIDTH, 7.6 * C.CM), layout="constrained")
gs = fig.add_gridspec(1, 2, width_ratios=[1.85, 1.35], wspace=0.0)
ax = fig.add_subplot(gs[0])
axt = fig.add_subplot(gs[1], sharey=ax)
ys = list(range(n))[::-1]
for (lab, d, lo, hi, h, kind), y in zip(rows, ys):
    col = C.BLUE if kind == "P" else (C.GREY if kind == "aa" else C.MUTED)
    mk = "s" if kind == "P" else "o"
    ax.plot([lo, hi], [y, y], color=col, lw=1.6 if kind == "P" else 1.0, solid_capstyle="butt", zorder=3)
    ax.plot([d], [y], marker=mk, color=col, ms=5.5 if kind == "P" else 4.5, zorder=4, ls="none")
    axt.text(1.0, y, f"{d:+.4f} [{lo:+.4f}, {hi:+.4f}]", va="center", ha="right", fontsize=8,
             color=C.DARK if kind == "P" else C.MUTED)
C.zero_line(ax)
ax.axvline(M, color=C.DARK, lw=0.8, ls=(0, (4, 2.5)), zorder=1)
ax.axvline(MDE, color=C.DARK, lw=0.8, ls=(0, (1, 1.8)), zorder=1)
tr = mtransforms.blended_transform_factory(ax.transData, ax.transAxes)
ax.text(M, 1.005, "M 0.010", transform=tr, ha="right", va="bottom", fontsize=8, color=C.DARK)
ax.text(MDE, 1.005, "MDE about 0.074\n(derived)", transform=tr, ha="left", va="bottom", fontsize=8, color=C.DARK)
ax.axhline(ys[0] - 0.5, color=C.GRID, lw=0.8, zorder=0)
ax.set_yticks(ys)
ax.set_yticklabels([r[0] for r in rows])
ax.get_yticklabels()[0].set_fontweight("bold")
ax.set_ylim(-0.6, n - 0.4)
ax.set_xlim(-0.06, 0.125)
ax.set_xlabel("Difference in crack relF1@2 (E1, OP-A), 95% interval")
ax.grid(axis="x")
axt.set_axis_off()
axt.set_xlim(0, 1)
axt.text(1.0, 1.005, "delta [seed-aware 95%]", transform=axt.transAxes, ha="right", va="bottom", fontsize=8, color=C.MUTED)
C.save(fig, "F13")

hdr = ["row", "contrast", "delta", "lo95", "hi95", "interval", "source"]
out = [[i + 1, r[0], *r[4].groups[:3], "seed-aware 95%", r[4].src] for i, r in enumerate(rows)]
out.append([n + 1, "M (decision margin)", p.groups[4], "", "", "", p.src])
out.append([n + 2, "MDE (derived: 2.80 x SE 0.0265)", mde_h.groups[1], "", "", "derived", mde_h.src])
fx = C.find(V8, rf"^   fixed-model interval of P .*: \[({C.NUM}), ({C.NUM})\]$")
out.append([n + 3, "P fixed-model interval (not drawn)", p.groups[0], *fx.groups, "fixed-model 95%", p.src + "; " + fx.src])
C.write_csv("F13", hdr, out)
print("F13 ok", len(rows), "contrasts")
