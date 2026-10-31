"""B2 v2 selection (coach CHANGES 30 Oct). Half-cells only (986). score = mean percentile rank of a, b_len, c (v2 c: dead_cell
17 and inactive 11 excluded as well as the structural classes; thin components only, width = area / major axis <= 12 px),
ranks within the 986 half-cells. 90 ranked half-cells (<= 13 per module) + 10 random half-cells (seed 0, not selected) as a
blinded control; the 100 are shuffled (seed 0) into 4 sheets of 25 whose titles show only the panel number and stem; only the
TSV marks ranked vs random. OOF validation (A50 primary, A20 secondary) re-run with the v2 c. Top-20 (c) class mix again.
Usage: python b2v2_select.py --code EL_ROOT --dir OUTDIR --runs FINAL_RUN x5
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
ap.add_argument("--mode", choices=["abc", "ab", "auto"], default="auto")
ap.add_argument("--gate-only", action="store_true")
a = ap.parse_args()
sys.path.insert(0, a.code)
from src.models.model_factory import build_model  # noqa: E402
from src.utils.config import load_config  # noqa: E402

torch.set_num_threads(12)
OUT = Path(a.dir); D = Path(a.code) / "data"
NAMES = ["background", "sp_multi", "sp_mono", "sp_dogbone", "ribbons", "border", "text", "padding", "clamp", "busbars",
         "crack_rbn_edge", "inactive", "rings", "material", "crack", "gridline", "splice", "dead_cell", "corrosion",
         "belt_mark", "edge_dark", "frame_edge", "jbox", "meas_artifact"]
STRUCT = np.array([c in (1, 2, 3, 4, 5, 6, 7, 8, 9, 21, 22, 17, 11) for c in range(24)])
GEOM = np.array([c in (1, 2, 3, 4, 5, 6, 7, 8, 9, 21, 22) for c in range(24)])
DISKN = (lambda r: (lambda y, x: (x * x + y * y) <= r * r)(*np.ogrid[-r:r + 1, -r:r + 1]))
NOMED = np.array([c in (5, 7, 21) for c in range(24)])
S8 = np.ones((3, 3), bool)
load = lambda f: [json.loads(l) for l in open(f) if l.strip()]


GATE = json.load(open(OUT / "b2v2_gate.json")) if (not a.gate_only and (OUT / "b2v2_gate.json").exists()) else None
MODE = a.mode if a.mode != "auto" else (GATE["mode"] if GATE else "abc")
OVERRIDE = ("# Mode ab by coach override (30 Oct): numeric gate said abc, but v2 c > 0 in 14/986 half-cells, all on image-border "
            "background outside the cell (artefact); c dropped.") if (GATE and MODE != GATE["mode"]) else None
KEYS = ("a", "b_len", "c") if MODE == "abc" else ("a", "b_len")


def score(rows):
    for k in KEYS:
        r = rankdata([x[k] for x in rows]) / len(rows)
        for x, v in zip(rows, r):
            x[f"r_{k}"] = float(v)
    for x in rows:
        x["score"] = sum(x[f"r_{k}"] for k in KEYS) / len(KEYS)


def auroc(pos, neg):
    if not pos or not neg:
        return float("nan")
    r = rankdata(np.array(pos + neg))[:len(pos)]
    return float((r.sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


L = []
for st in ("A50", "A20"):
    v = load(OUT / f"val_v2_{st}.jsonl"); score(v)
    P = [x for x in v if x.get("scuff_px", 0) > 0]; N = [x for x in v if x.get("scuff_px", 0) <= 0]
    per = {k: auroc([x[k] for x in P], [x[k] for x in N]) for k in ("a", "b_len", "c")}
    L.append(f"validation v2 {st} ({'primary' if st == 'A50' else 'secondary, legacy masks_coded'}): {len(v)} OOF train cells, n_pos {len(P)} "
             f"({', '.join(x['stem'] for x in P)}); AUROC score {auroc([x['score'] for x in P], [x['score'] for x in N]):.3f} "
             f"(a {per['a']:.3f}, b_len {per['b_len']:.3f}, c {per['c']:.3f})")
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
    near = ndimage.binary_dilation(GEOM[cons], DISKN(6))
    lb, _ = ndimage.label((g < med - 20) & ~STRUCT[cons], S8)
    streak = np.zeros(g.shape, bool)
    for j, sl in enumerate(ndimage.find_objects(lb), 1):
        mm = lb[sl] == j; ys, xs = np.nonzero(mm)
        if len(ys) < 20 or near[sl][mm].any():
            continue
        cov = np.cov(np.stack([ys - ys.mean(), xs - xs.mean()])); l2, l1 = np.linalg.eigvalsh(cov)
        if np.sqrt(max(l1, 0) / (max(l2, 0) + 1 / 12)) > 10 and np.sqrt(max(l2, 0)) <= 2.5:
            streak[sl] |= mm
    return g, pm[14] > 0.5, streak, cons


half = load(OUT / "pool_v2_half.jsonl"); assert len(half) == 986
if a.gate_only:
    top = sorted(half, key=lambda x: -x["c"])[:20]
    G = ["gate (coach): top 20 half-cells by v2 c, FINAL-consensus class mix of streak px and share of streak px within 12 px of the structural / frame mask"]
    fig, axes = plt.subplots(4, 5, figsize=(15, 13)); P_tot = P_n12 = P_bad = 0
    for ax, x in zip(axes.ravel(), top):
        g, pc, streak, cons = infer(x["stem"])
        cnt = np.bincount(cons[streak], minlength=24); tot = max(cnt.sum(), 1)
        n12 = float((streak & ndimage.binary_dilation(GEOM[cons], DISKN(12))).sum() / tot)
        P_tot += int(streak.sum()); P_n12 += int((streak & ndimage.binary_dilation(GEOM[cons], DISKN(12))).sum()); P_bad += int(STRUCT[cons][streak].sum())
        G.append(f"  {x['stem']} c {x['c']} comps {x['c_comps']}: " + ", ".join(f"{NAMES[k]} {100 * cnt[k] / tot:.0f}%" for k in np.argsort(-cnt)[:4] if cnt[k])
                 + f"; within 12 px of gaps/frame {100 * n12:.0f}%")
        rgb = np.stack([g] * 3, -1).astype(np.float32); rgb[pc] = 0.3 * rgb[pc] + 0.7 * np.array((255, 0, 0))
        rgb[ndimage.binary_dilation(streak & ~ndimage.binary_erosion(streak))] = (0, 255, 255)
        ax.imshow(rgb.astype(np.uint8)); ax.set_title(f"{x['stem']} c {x['c']}", fontsize=8); ax.axis("off")
    fig.suptitle("B2 v2 gate: top 20 half-cells by v2 c (thin dark streak cyan, crack p > 0.5 red)", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.97)); fig.savefig(OUT / "b2v2_gate_top20.png", dpi=80); plt.close(fig)
    G.append(f"half-cells with v2 c > 0: {sum(x['c'] > 0 for x in half)} of 986")
    s12, sbad = P_n12 / max(P_tot, 1), P_bad / max(P_tot, 1)
    mode = "ab" if (s12 > 0.5 or sbad > 0.5) else "abc"
    G.append(f"GATE (coach, numeric, stated before the numbers): pooled top-20 streak px {P_tot}; within 12 px of the gap/frame mask "
             f"{100 * s12:.1f}% (> 50% -> drop c); consensus dead_cell / inactive / structural {100 * sbad:.1f}% (> 50% -> drop c) -> mode {mode}")
    json.dump({"pooled_streak_px": P_tot, "share_within_12px_gap_frame": s12, "share_deadcell_inactive_structural": sbad, "mode": mode},
              open(OUT / "b2v2_gate.json", "w"), indent=1)
    (OUT / "b2v2_gate.txt").write_text("\n".join(G) + "\n"); print("\n".join(G)); sys.exit(0)
score(half)
ranked, mod = [], {}
for x in sorted(half, key=lambda x: -x["score"]):
    if len(ranked) >= 90:
        break
    if mod.get(x["module"], 0) < 13:
        ranked.append(x); mod[x["module"]] = mod.get(x["module"], 0) + 1
for i, x in enumerate(ranked, 1):
    x["kind"], x["rank"] = "ranked", i
rng = np.random.default_rng(0)
rest = [x for x in half if x["stem"] not in {r["stem"] for r in ranked}]
rand = [rest[i] for i in sorted(rng.choice(len(rest), 10, replace=False))]
for x in rand:
    x["kind"], x["rank"] = "random", ""
allc = ranked + rand
order = np.random.default_rng(0).permutation(len(allc))
panels = [allc[i] for i in order]
for p, x in enumerate(panels, 1):
    x["panel"] = p
stmt = ("# validation AUROC 0.33 (A50, n_pos 4) / 0.40 (A20, n_pos 9), below chance; train scuffs are small full-cell scuffs, not the "
        "target context; the ranking is unvalidated; the 10 blinded random cells measure it")
hdr = ["# B2 v2 candidates (coach CHANGES 30 Oct; mine only, no labels). Half-cells only (986, CSIR, 7 modules 297-299, 301, 333-335: low diversity).",
       "# Proposer: FINAL members (p6_L3_100pct_s0-2 + p16_A_100pct_s3-4), mean softmax. a = crack px (p > 0.5); b_len = ellipse major axis of the",
       "#   largest predicted crack component (underestimates curved / branched cracks); c = px of dark (< median - 20 GL) components >= 20 px,",
       "#   elongation sqrt(l1 / (l2 + 1/12)) > 10 (length >= 10 x width), minor-axis sd sqrt(l2) <= 2.5 px (width about <= 10 px), not within 6 px",
       "#   of the structural / frame mask (classes 1-9, 21, 22), consensus not 1-9, 21, 22, 17 or 11.",
       f"# GATE (numeric, stated before the numbers): pooled top-20 streak px within 12 px of gaps/frame {100 * GATE['share_within_12px_gap_frame']:.1f}%, "
       f"(1); on dead_cell / inactive / structural {100 * GATE['share_deadcell_inactive_structural']:.1f}% (2) (either > 50% -> drop c) -> gate mode {GATE['mode']}" if GATE else f"# GATE: mode {MODE} (manual)",
       "# Both gate conditions are weakened by the v2 exclusions. (1) measures only the 6-12 px band, because components within 6 px of gaps/frame are",
       "#   already dropped. (2) is ~0% by construction. The real tests are the re-run OOF AUROC (with n_pos) and the user's hit rate on ranked vs the",
       "#   10 blinded random cells.",
       f"# score = mean percentile rank of {', '.join(KEYS)} within the half-cells (mode {MODE}; see b2v2_gate.txt). 90 ranked (<= 13 per module) + 10 random (seed 0); panel order shuffled (seed 0).",
       stmt] + ([OVERRIDE] if OVERRIDE else [])
cols = ["panel", "stem", "module", "kind", "rank", "a", "b_px", "b_len", "c", "c_comps", "score"]
fmt = lambda v: str(round(v, 4)) if isinstance(v, float) else str(v)
tsv = "\n".join(hdr) + "\n" + "\t".join(cols) + "\n" + "".join("\t".join(fmt(x[c]) for c in cols) + "\n" for x in panels)
(OUT / "b2v2_candidates.tsv").write_text(tsv)
lst = "".join(f"{x['stem']}\n" for x in panels); (OUT / "b2v2_list.txt").write_text(lst)
L.append(f"selected 90 ranked (modules {dict(sorted(mod.items()))}) + 10 random; panel list md5 {hashlib.md5(lst.encode()).hexdigest()}")
L.append(f"half-cells with a > 0: {sum(x['a'] > 0 for x in half)}; with v2 c > 0: {sum(x['c'] > 0 for x in half)}")



# coach / team-lead: judging sheets are PLAIN thumbnails titled "panel N stem" only (overlays would cue the ranked cells and break
# the blinded random control); overlay versions go to overlays/, to be opened only after the user has marked every panel.
(OUT / "overlays").mkdir(exist_ok=True)
for sh in range(4):
    items = panels[25 * sh:25 * (sh + 1)]
    figs = {k: plt.subplots(5, 5, figsize=(15, 16)) for k in ("plain", "overlay")}
    for k, (fig, axes) in figs.items():
        for ax in axes.ravel():
            ax.axis("off")
    for i, x in enumerate(items):
        g, pc, streak, _ = infer(x["stem"])
        rgb = np.stack([g] * 3, -1).astype(np.float32)
        ax = figs["plain"][1].ravel()[i]; ax.imshow(g, cmap="gray", vmin=0, vmax=255); ax.set_title(f"panel {x['panel']}  {x['stem']}", fontsize=8)
        rgb[pc] = 0.3 * rgb[pc] + 0.7 * np.array((255, 0, 0))
        rgb[ndimage.binary_dilation(streak & ~ndimage.binary_erosion(streak))] = (0, 255, 255)
        ax = figs["overlay"][1].ravel()[i]; ax.imshow(rgb.astype(np.uint8)); ax.set_title(f"panel {x['panel']}  {x['stem']}", fontsize=8)
    for k, (fig, _) in figs.items():
        fig.suptitle(f"B2 v2 sheet {sh + 1}/4: panels {items[0]['panel']}-{items[-1]['panel']}" + (" (mark each: scuff / crack / both / neither)" if k == "plain" else
                     " OVERLAYS (crack p > 0.5 red, thin dark streak cyan): open only after every panel is marked"), fontsize=11)
        fig.tight_layout(rect=(0, 0, 1, 0.97))
        fig.savefig(OUT / (f"b2v2_sheet{sh + 1}.png" if k == "plain" else f"overlays/b2v2_overlay_sheet{sh + 1}.png"), dpi=150); plt.close(fig)
L.insert(0, OVERRIDE.lstrip("# ")) if OVERRIDE else None
L.insert(0, f"ranking mode: {MODE} ({'a, b_len and c' if MODE == 'abc' else 'a and b_len only: c dropped by coach override'})" + (f"; gate: within 12 px {100 * GATE['share_within_12px_gap_frame']:.1f}%, dead_cell/inactive/structural {100 * GATE['share_deadcell_inactive_structural']:.1f}%" if GATE else ""))
(OUT / "b2v2_report.txt").write_text(stmt.lstrip("# ") + "\n" + "\n".join(L) + "\n")
print("\n".join(L))
