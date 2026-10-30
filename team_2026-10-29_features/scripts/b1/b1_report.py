"""B1 report: merge the auditor-set flag tables, build list S (raw E-SCDD scuff 25 / star 28 px that are crack 14 or
inactive 11 in masks_escdd; train cells; val counted as a base rate; no test), and render the panel sheets:
sheet 1 top 30 train cells by crack ML + FL px, sheet 2 top 10 by inactive, sheet 3 every train cell in S.
Panel: image | GT | 5-auditor consensus (argmax of the mean softmax) | flags on the image (ML yellow, FL magenta, S cyan).
Usage: python b1_report.py --code EL_ROOT --out OUTDIR
"""
import argparse
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--code", required=True)
ap.add_argument("--out", required=True)
a = ap.parse_args()
D = Path(a.code) / "data"; OUT = Path(a.out)
IMG, GT = D / "labeled" / "images", D / "labeled" / "masks_escdd"
RAW = Path("/home/noob/work/el-fault-detection/data/escdd_masks")
rd = lambda p: [ln.strip() for ln in open(p) if ln.strip()]
train, val = rd(D / "splits" / "train.txt"), rd(D / "splits" / "val.txt")
twins = set(rd(D / "splits" / "d7_twin_train_cells.txt"))
role = {s: ("D7 twin" if s in twins else "train") for s in train} | {s: "val" for s in val}

# coach ruling (30 Oct): A50 (house recipe, masks_escdd, 239 OOF train cells) is primary and alone ranks and fills the
# sheets; A20 (legacy unetpp / weighted_ce, trained on labeled/masks_coded) is secondary only: in the table, marked.
NOTE = {"A50": "primary: p16_A_50pct_s0-4, house recipe, masks_escdd",
        "A20": "secondary only: sl_20pct_s0-4_cv02, legacy recipe, trained on masks_coded (flags mostly the coded->E-SCDD revision)"}
rows = []
for f in sorted(OUT.glob("b1_flags_A*.tsv")):
    for r in csv.DictReader(open(f), delimiter="\t"):
        r["note"] = NOTE.get(r["auditor_set"], ""); rows.append(r)
with open(OUT / "b1_flags.tsv", "w", newline="") as f:
    w = csv.DictWriter(f, ["cell", "source", "role", "auditor_set", "cls", "flag", "px", "components", "note"], delimiter="\t")
    w.writeheader(); w.writerows(rows)
import json
lines = []
for st in ("A50", "A20"):
    sm = OUT / f"b1_summary_{st}.json"
    if not sm.exists():
        continue
    j = json.load(open(sm)); n_train = sum(1 for s in train if s not in set(rd(j["labeled"]))); n_val = len(val)
    lines.append(f"{st} ({NOTE[st]}): audits {n_train} of {len(train)} train cells (OOF) + {n_val} val (base rate)")
    for k, v in sorted(j["summary"].items()):
        n = n_val if k.startswith("val/") else n_train
        lines.append(f"  {k}: {v['cells']} cells ({100 * v['cells'] / n:.1f} per 100), {v['px']} px, {v['components']} components")
open(OUT / "b1_coverage.txt", "w").write("\n".join(lines) + "\n")
print("\n".join(lines))

# list S (deterministic): train + val cells whose raw E-SCDD mask has classes 24-29
srows, smask = [], {}
for s in train + val:
    p = RAW / ("val" if role[s] == "val" else "train") / f"{s}.png"
    if not p.exists():
        continue
    raw, g = np.array(Image.open(p)), np.array(Image.open(GT / f"{s}.png"))
    if raw.shape != g.shape or not (raw >= 24).any():
        continue
    sc, st = raw == 25, raw == 28
    oth = (raw >= 24) & ~sc & ~st
    r = dict(cell=s, source=s.split("_")[0], role=role[s],
             scuff_to_crack=int((sc & (g == 14)).sum()), star_to_crack=int((st & (g == 14)).sum()),
             scuff_to_inactive=int((sc & (g == 11)).sum()), star_to_inactive=int((st & (g == 11)).sum()),
             other24_29_to_crack=int((oth & (g == 14)).sum()), other24_29_to_inactive=int((oth & (g == 11)).sum()),
             scuff_px=int(sc.sum()), star_px=int(st.sum()))
    srows.append(r)
    smask[s] = (sc | st) & np.isin(g, (14, 11))
with open(OUT / "b1_S.tsv", "w", newline="") as f:
    w = csv.DictWriter(f, list(srows[0].keys()) if srows else ["cell"], delimiter="\t")
    w.writeheader(); w.writerows(srows)

# rankings (train cells only; a flag from either auditor set counts, the set is named)
def px_by(cls):
    d = {}
    for r in rows:
        if r["role"] == "val" or r["cls"] != cls or r["auditor_set"] != "A50":   # A50 alone ranks (coach)
            continue
        d.setdefault(r["cell"], {}).setdefault(r["auditor_set"], 0)
        d[r["cell"]][r["auditor_set"]] += int(r["px"])
    return sorted(d.items(), key=lambda kv: -max(kv[1].values()))

# display palette: only crack is red and inactive blue; every other class a muted grey / tint (padding dark grey)
PAL = np.array([(0, 0, 0)] + [(70 + 6 * i, 70 + 4 * i, 60 + 5 * i) for i in range(1, 24)], np.uint8)
PAL[7] = (40, 40, 40); PAL[5] = (90, 70, 40); PAL[21] = (60, 60, 90); PAL[1] = (120, 110, 60); PAL[2] = (110, 120, 70)
PAL[4] = (130, 120, 90); PAL[9] = (150, 150, 150); PAL[15] = (100, 140, 100); PAL[17] = (0, 40, 120); PAL[10] = (255, 150, 150)
PAL[14] = (255, 0, 0); PAL[11] = (0, 120, 255)
from scipy import ndimage  # noqa: E402


def panel(axs, stem, sets, title):
    img = np.array(Image.open(IMG / f"{stem}.png").convert("L"))
    g = np.array(Image.open(GT / f"{stem}.png"))
    best = max(sets, key=sets.get) if sets else None
    cache = OUT / "cache" / f"{best}_{stem}.npz" if best else None
    if cache is None or not cache.exists():
        cands = sorted((OUT / "cache").glob(f"A50_{stem}.npz"))      # panels from A50 only (coach)
        cache = cands[0] if cands else None
    z = np.load(cache) if cache else None
    ov = np.stack([img] * 3, -1).astype(np.float32)
    if z is not None:
        fl = z["flags"]
        for bit, col in ((0, (255, 255, 0)), (2, (255, 255, 0)), (1, (255, 0, 255)), (3, (255, 0, 255))):
            m = ndimage.binary_dilation(((fl >> bit) & 1).astype(bool))   # +1 px for display only
            ov[m] = 0.25 * ov[m] + 0.75 * np.array(col)
    if stem in smask:
        m = ndimage.binary_dilation(smask[stem]); ov[m] = 0.25 * ov[m] + 0.75 * np.array((0, 255, 255))
    for ax, im, t in zip(axs, (img, PAL[np.clip(g, 0, 23)], PAL[np.clip(z["cons"], 0, 23)] if z is not None else img * 0,
                               ov.astype(np.uint8)), ("image", "GT (crack red, inactive blue, rest grey)",
                                                       f"consensus ({cache.name.split('_')[0] if cache else '-'})", "flags: ML yellow, FL magenta, S cyan")):
        ax.imshow(im, cmap="gray" if im.ndim == 2 else None, interpolation="nearest"); ax.set_xticks([]); ax.set_yticks([])
        ax.set_title(t, fontsize=7)
    axs[0].set_ylabel(title, fontsize=7)


def sheet(items, fname, head):
    n = len(items)
    if not n:
        return
    fig, axes = plt.subplots(n, 4, figsize=(16, 4.2 * n + 0.6), squeeze=False)
    for i, (stem, sets, extra) in enumerate(items):
        panel(axes[i], stem, sets, f"{stem}\n{stem.split('_')[0]} {role[stem]}\n{extra}")
    H = 4.2 * n + 0.6
    fig.suptitle(head, fontsize=12, y=1 - 0.15 / H); fig.tight_layout(rect=(0, 0, 1, 1 - 0.6 / H))
    fig.savefig(OUT / fname, dpi=110); plt.close(fig)


cr, ina = px_by("crack"), px_by("inactive")
sheet([(s, v, "crack px " + ", ".join(f"{k} {x}" for k, x in sorted(v.items()))) for s, v in cr[:30]], "b1_sheet1_crack_top30.png",
      "B1 sheet 1: top 30 train cells by crack ML + FL px (A50 OOF auditors, 239 of 478 train cells; mark each: label error / true hard case / unsure)")
sheet([(s, v, "inactive px " + ", ".join(f"{k} {x}" for k, x in sorted(v.items()))) for s, v in ina[:10]], "b1_sheet2_inactive_top10.png",
      "B1 sheet 2: top 10 train cells by inactive ML + FL px (A50)")
st = [r for r in srows if r["role"] != "val"]
sheet([(r["cell"], {}, f"S: scuff->crack {r['scuff_to_crack']}, star->crack {r['star_to_crack']}, ->inactive {r['scuff_to_inactive'] + r['star_to_inactive']}")
       for r in st], "b1_sheet3_S_train.png", "B1 sheet 3: train cells in list S (E-SCDD scuff/star px that are crack/inactive in masks_escdd)")
print(f"flags rows {len(rows)}; crack-flagged train cells {len(cr)}; inactive {len(ina)}; S cells train {len(st)} val {len(srows) - len(st)}")
