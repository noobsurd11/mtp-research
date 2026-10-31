"""B2 mining, step 2: score, select 100 candidates, validate, contact sheets (coach rulings 30 Oct). CPU.
score = mean of the percentile ranks of a, b_len and c (ties averaged), computed over the pool set.
List: 70 half-cells by score (<= 10 per module; all half-cells are CSIR from 7 modules: 297-299, 301, 333-335) +
30 full cells by c (ties by score; <= 3 per module, <= 40 per source).
Validation (descriptive): AUROC of the score (ranks within the set) for train cells with raw E-SCDD scuff (25) vs the other
cells of each out-of-fold set (A50 primary, A20 secondary); FINAL is never used for validation (it trained on those cells).
Also: the FINAL-consensus class mix of the streak px of the top 20 cells by c, and 4 contact sheets of 25
(thumbnail | crack p > 0.5 red | streak mask outline cyan).
Usage: python b2_select.py --code EL_ROOT --dir OUTDIR --runs FINAL_RUN x5
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import torch  # noqa: E402
from PIL import Image  # noqa: E402
from scipy import ndimage  # noqa: E402
from scipy.stats import rankdata  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--code", required=True)
ap.add_argument("--dir", required=True)
ap.add_argument("--runs", nargs=5, required=True)
a = ap.parse_args()
sys.path.insert(0, a.code)
from src.models.model_factory import build_model  # noqa: E402
from src.utils.config import load_config  # noqa: E402

torch.set_num_threads(16)
OUT = Path(a.dir); D = Path(a.code) / "data"
NAMES = ["background", "sp_multi", "sp_mono", "sp_dogbone", "ribbons", "border", "text", "padding", "clamp", "busbars",
         "crack_rbn_edge", "inactive", "rings", "material", "crack", "gridline", "splice", "dead_cell", "corrosion",
         "belt_mark", "edge_dark", "frame_edge", "jbox", "meas_artifact"]
STRUCT = np.array([c in (1, 2, 3, 4, 5, 6, 7, 8, 9, 21, 22) for c in range(24)])
NOMED = np.array([c in (5, 7, 21) for c in range(24)])
S8 = np.ones((3, 3), bool)
load = lambda f: [json.loads(l) for l in open(f) if l.strip()]


def score(rows):
    if not rows:
        return
    for k in ("a", "b_len", "c"):
        r = rankdata([x[k] for x in rows]) / len(rows)
        for x, v in zip(rows, r):
            x[f"r_{k}"] = float(v)
    for x in rows:
        x["score"] = (x["r_a"] + x["r_b_len"] + x["r_c"]) / 3


def auroc(pos, neg):
    if not pos or not neg:
        return float("nan")
    allv = np.array(pos + neg); r = rankdata(allv)[:len(pos)]
    return float((r.sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


lines = []
for st in ("A50", "A20"):
    f = OUT / f"val_{st}.jsonl"
    if not f.exists():
        continue
    v = load(f); score(v)
    pos = [x["score"] for x in v if x.get("scuff_px", 0) > 0]; neg = [x["score"] for x in v if x.get("scuff_px", 0) <= 0]
    per = {k: auroc([x[k] for x in v if x.get("scuff_px", 0) > 0], [x[k] for x in v if x.get("scuff_px", 0) <= 0]) for k in ("a", "b_len", "c")}
    lines.append(f"validation {st} ({'primary' if st == 'A50' else 'secondary, legacy masks_coded'}): {len(v)} OOF train cells, "
                 f"{len(pos)} with E-SCDD scuff ({', '.join(x['stem'] for x in v if x.get('scuff_px', 0) > 0)}); "
                 f"AUROC score {auroc(pos, neg):.3f} (a {per['a']:.3f}, b_len {per['b_len']:.3f}, c {per['c']:.3f}); n_pos {len(pos)}, n_neg {len(neg)}")
pool = load(OUT / "pool_FINAL.jsonl"); score(pool)
half = sorted([x for x in pool if x["halfcut"]], key=lambda x: -x["score"])
full = sorted([x for x in pool if not x["halfcut"]], key=lambda x: (-x["c"], -x["score"]))
sel, mod, src = [], {}, {}
for x in half:
    if len([s for s in sel if s["halfcut"]]) >= 70:
        break
    if mod.get(x["module"], 0) < 10:
        sel.append(x); mod[x["module"]] = mod.get(x["module"], 0) + 1
for x in full:
    if len([s for s in sel if not s["halfcut"]]) >= 30:
        break
    if mod.get(x["module"], 0) < 3 and src.get(x["source"], 0) < 40:
        sel.append(x); mod[x["module"]] = mod.get(x["module"], 0) + 1; src[x["source"]] = src.get(x["source"], 0) + 1
for i, x in enumerate(sel, 1):
    x["rank"] = i
hdr = ["# B2 candidates (coach 30 Oct; mine only, no labels). Proposer: FINAL members p6_L3_100pct_s0-2 + p16_A_100pct_s3-4, mean softmax.",
       "# a = predicted crack px (p > 0.5); b_px / b_len = largest predicted crack component px / ellipse major axis 4*sqrt(l1)",
       "#   (stand-in for skeleton length; underestimates curved or branched cracks); c = px of dark (< median - 20 GL) components",
       "#   >= 20 px with elongation > 10, excluding FINAL-consensus structural classes 1-9, 21, 22; score = mean percentile rank of a, b_len, c.",
       "# 70 half-cells by score (<= 10 per module; all CSIR, 7 modules 297-299, 301, 333-335: low diversity by construction) +",
       "#   30 full cells by c (<= 3 per module, <= 40 per source). Candidates: pool part of mim_pool_v11 (R1-R4), 11,219 cells."]
cols = ["rank", "stem", "source", "module", "halfcut", "a", "b_px", "b_len", "c", "c_comps", "score"]
tsv = "\n".join(hdr) + "\n" + "\t".join(cols) + "\n" + "".join("\t".join(str(x[c] if not isinstance(x[c], float) else round(x[c], 4)) for c in cols) + "\n" for x in sel)
(OUT / "b2_candidates.tsv").write_text(tsv)
lst = "".join(f"{x['stem']}\n" for x in sel); (OUT / "b2_list.txt").write_text(lst)
lines.append(f"selected {len(sel)} ({sum(x['halfcut'] for x in sel)} half-cells, {sum(not x['halfcut'] for x in sel)} full); list md5 {hashlib.md5(lst.encode()).hexdigest()}")
lines.append(f"pool: {len(pool)} cells ({len(half)} half-cells); cells with a > 0: {sum(x['a'] > 0 for x in pool)}; with c > 0: {sum(x['c'] > 0 for x in pool)}")
lines.append("full-cell sources in list: " + ", ".join(f"{k} {v}" for k, v in sorted(src.items())))

models = []
for r in a.runs:
    r = Path(r); stt = torch.load(r / "checkpoints" / "latest.pth", map_location="cpu", weights_only=False)
    assert int(stt["step"]) == 20000
    mc = {k: v for k, v in load_config(r / "config_used.yaml")["model"].items() if k not in ("encoder_init", "decoder_init")}
    mc["encoder_weights"] = None
    m = build_model(mc); m.load_state_dict(stt["models"]["model"]); m.eval(); models.append(m)


def infer(stem):
    g = np.array(Image.open(D / "unlabeled" / "images_512" / f"{stem}.png").convert("L"))
    xt = torch.from_numpy((g.astype(np.float32) / 255.0 - 0.5) / 0.25)[None, None]
    with torch.no_grad():
        pm = torch.stack([torch.softmax(m(xt).float(), 1)[0] for m in models]).mean(0).numpy()
    cons = pm.argmax(0)
    med = float(np.median(g[~NOMED[cons]])) if (~NOMED[cons]).any() else float(np.median(g))
    lb, n = ndimage.label((g < med - 20) & ~STRUCT[cons], S8)
    streak = np.zeros(g.shape, bool)
    for j, sl in enumerate(ndimage.find_objects(lb), 1):
        mm = lb[sl] == j; ys, xs = np.nonzero(mm)
        if len(ys) < 20:
            continue
        cov = np.cov(np.stack([ys - ys.mean(), xs - xs.mean()])); l2, l1 = np.linalg.eigvalsh(cov)
        if np.sqrt(max(l1, 0) / (max(l2, 0) + 1 / 12)) > 10:
            streak[sl] |= mm
    return g, pm[14] > 0.5, streak, cons


topc = sorted(pool, key=lambda x: -x["c"])[:20]
lines.append("top 20 pool cells by c: FINAL-consensus class mix of their streak px")
for x in topc:
    g, pc, streak, cons = infer(x["stem"])
    cnt = np.bincount(cons[streak], minlength=24); tot = max(cnt.sum(), 1)
    mix = ", ".join(f"{NAMES[k]} {100 * cnt[k] / tot:.0f}%" for k in np.argsort(-cnt)[:4] if cnt[k])
    lines.append(f"  {x['stem']} ({'half' if x['halfcut'] else 'full'}) c {x['c']}: {mix}")
for sh in range(4):
    items = sel[25 * sh:25 * (sh + 1)]
    if not items:
        continue
    fig, axes = plt.subplots(5, 5, figsize=(15, 16))
    for ax in axes.ravel():
        ax.axis("off")
    for ax, x in zip(axes.ravel(), items):
        g, pc, streak, _ = infer(x["stem"])
        rgb = np.stack([g] * 3, -1).astype(np.float32)
        rgb[pc] = 0.3 * rgb[pc] + 0.7 * np.array((255, 0, 0))
        edge = streak & ~ndimage.binary_erosion(streak)
        rgb[ndimage.binary_dilation(edge)] = (0, 255, 255)
        ax.imshow(rgb.astype(np.uint8)); ax.set_title(f"#{x['rank']} {x['stem']} {'half' if x['halfcut'] else 'full'}\n"
                                                      f"score {x['score']:.2f} a {x['a']} c {x['c']}", fontsize=7)
    fig.suptitle(f"B2 contact sheet {sh + 1}/4 (crack p > 0.5 red, dark-streak outline cyan); ranks {items[0]['rank']}-{items[-1]['rank']}", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.97)); fig.savefig(OUT / f"b2_sheet{sh + 1}.png", dpi=80); plt.close(fig)
(OUT / "b2_report.txt").write_text("\n".join(lines) + "\n")
print("\n".join(lines))
