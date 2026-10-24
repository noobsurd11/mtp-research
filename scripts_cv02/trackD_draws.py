"""Track D labelled-set draws (protocol team_2026-10-24_go/trackD/protocol_labelset.md). Run once; never redrawn.

Candidates: seed-0 unlabelled 5% train cells (455) minus the 7 D7 train twins = 448. Never val or test.
Crack cell: >= 20 GT crack px on masks_escdd excluding P6 remap px (crack in masks_escdd where E-SCDD's own mask is not
crack; E-SCDD masks from HF snt-ubix/escdd 8c8cba9a, copied to escdd_ref/). Arms (12 added cells each, 3 draws):
  R  : 12 random candidates                     rng seeds 101, 102, 103
  Tc : 12 random crack cells, any source        rng seeds 201, 202, 203
  Ts : 6 BMRK + 4 ARTS + 2 CSIR crack cells      rng seeds 301, 302, 303 (one generator per draw, sources in that order)
numpy.random.default_rng(seed).choice(sorted candidates, k, replace=False). List file = the 23 base cells in
labeled_5pct.txt order, then the 12 added cells sorted.
Usage: python trackD_draws.py <data dir> <escdd_ref dir> <out dir> <D7 twin list>
"""
import json, sys
from pathlib import Path

import numpy as np
from PIL import Image

DATA, REF, OUT, TWINS = (Path(a) for a in sys.argv[1:5])
OUT.mkdir(parents=True, exist_ok=True)
CR, IN, MIN_CRACK = 14, 11, 20
SEEDS = {"R": [101, 102, 103], "Tc": [201, 202, 203], "Ts": [301, 302, 303]}
TS_QUOTA = [("BMRK", 6), ("ARTS", 4), ("CSIR", 2)]

sp = DATA / "splits"
rd = lambda p: [l.strip() for l in open(p) if l.strip()]
base, unl = rd(sp / "seed0" / "labeled_5pct.txt"), rd(sp / "seed0" / "unlabeled_5pct.txt")
twins, train, val, test = rd(TWINS), rd(sp / "train.txt"), rd(sp / "val.txt"), rd(sp / "test.txt")
assert len(base) == 23 and len(unl) == 455 and len(twins) == 7 and set(twins) <= set(unl)
cand = sorted(s for s in unl if s not in twins)
assert len(cand) == 448 and not set(cand) & (set(val) | set(test) | set(base)) and set(cand) <= set(train)

ref = {p.stem: p for d in ("el_masks_train", "el_masks_val", "el_masks_test") for p in (REF / d).glob("*.png")}
info, remap_total, remap_other = {}, 0, 0
for s in sorted(set(cand) | set(base)):
    m = np.array(Image.open(DATA / "labeled" / "masks_escdd" / f"{s}.png"))
    crack = m == CR
    if s in ref:
        e = np.array(Image.open(ref[s]))
        remap = crack & (e != CR)
        remap_other += int((remap & ~np.isin(e, [25, 28])).sum())
    else:
        remap = np.zeros_like(crack)
    remap_total += int(remap.sum())
    info[s] = {"src": s.split("_")[0], "crack_px": int((crack & ~remap).sum()), "remap_px": int(remap.sum()),
               "inactive_px": int((m == IN).sum()), "in_escdd": s in ref}
    info[s]["crack_cell"] = info[s]["crack_px"] >= MIN_CRACK
    info[s]["pos"] = "_".join(s.split("_")[2:4])
# C review_labelset_v1 (1): CFVS is a time series; flag any candidate sharing source + module position (rX_cY) with a test cell
test_pos = {(t.split("_")[0], "_".join(t.split("_")[2:4])) for t in test}
for s in info:
    info[s]["shares_test_pos"] = (info[s]["src"], info[s]["pos"]) in test_pos
assert remap_other == 0, f"{remap_other} crack px differ from E-SCDD outside 25/28"

crack_cells = [s for s in cand if info[s]["crack_cell"]]
by_src = {}
for s in crack_cells:
    by_src.setdefault(info[s]["src"], []).append(s)


def summary(cells):
    out = {"n": len(cells), "crack_cells": 0, "crack_px": 0, "inactive_cells": 0, "inactive_px": 0, "by_source": {}}
    for s in cells:
        i = info[s]; b = out["by_source"].setdefault(i["src"], {"cells": 0, "crack_cells": 0, "crack_px": 0, "inactive_px": 0})
        b["cells"] += 1; b["crack_cells"] += i["crack_cell"]; b["crack_px"] += i["crack_px"]; b["inactive_px"] += i["inactive_px"]
        out["crack_cells"] += i["crack_cell"]; out["crack_px"] += i["crack_px"]
        out["inactive_cells"] += i["inactive_px"] > 0; out["inactive_px"] += i["inactive_px"]
    return out


draws = {}
for arm, seeds in SEEDS.items():
    for k, seed in enumerate(seeds):
        g = np.random.default_rng(seed)
        if arm == "R":
            add = list(g.choice(cand, 12, replace=False))
        elif arm == "Tc":
            add = list(g.choice(crack_cells, 12, replace=False))
        else:
            add = []
            for src, q in TS_QUOTA:
                add += list(g.choice(sorted(by_src[src]), q, replace=False))
        add = sorted(str(a) for a in add)
        assert len(set(add)) == 12 and set(add) <= set(cand)
        name = f"{arm}_d{k}"
        (OUT / f"{name}.txt").write_text("\n".join(base + add) + "\n")
        draws[name] = {"seed": seed, "added": add, "added_summary": summary(add), "full_summary": summary(base + add),
                       "added_sharing_test_pos": [a for a in add if info[a]["shares_test_pos"]]}
        if arm == "Ts":
            bs = draws[name]["added_summary"]["by_source"]
            assert [bs[s]["crack_cells"] for s, _ in TS_QUOTA] == [q for _, q in TS_QUOTA]

res = {"candidates": len(cand), "crack_cells_in_pool": len(crack_cells),
       "crack_cells_by_source": {k: len(v) for k, v in sorted(by_src.items())},
       "pool_by_source": summary(cand)["by_source"], "remap_px_total": remap_total,
       "base_5pct": summary(base), "draws": draws, "cells": info}
(OUT / "audit.json").write_text(json.dumps(res, indent=1))
print(f"candidates {len(cand)}, crack cells {len(crack_cells)} {res['crack_cells_by_source']}, remap px {remap_total}")
b = res["base_5pct"]
print(f"base 5%: crack cells {b['crack_cells']} crack px {b['crack_px']} inactive cells {b['inactive_cells']} px {b['inactive_px']}")
for name, d in draws.items():
    a = d["added_summary"]
    src = " ".join(f"{k}:{v['cells']}c/{v['crack_cells']}cc/{v['crack_px']}px" for k, v in sorted(a["by_source"].items()))
    print(f"{name:6s} +crack cells {a['crack_cells']:2d} +crack px {a['crack_px']:6d} +inactive cells {a['inactive_cells']} "
          f"+inactive px {a['inactive_px']:6d} | {src} | test-pos shared: {d['added_sharing_test_pos']}")
