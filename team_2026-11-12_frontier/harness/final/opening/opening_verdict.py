"""The registered rule of the final opening (OPENING_RULE.md sections 4 to 7, 10) applied to the opening's reads.
Reads only the read.json files of the registered read (scripts/bench_open_read.py at R): E1 (labels set), test50 v1.1,
test50 v0 (--public). Writes verdict.txt and verdict.json; refuses an existing output.

  python opening_verdict.py --e1 O/read_e1/read.json --t50 O/read_t50_v11/read.json --t50v0 O/read_t50_v0/read.json \
      --reg IO/REGISTERED.txt --fin-verdict /home/noob/work/bench_reads/final_tta/verdict.txt --out O/verdict.txt

E1 primary contrast P = C2 - C1, crack relF1@2 at OP-A, seed-aware two-stage interval (71 clusters x models):
  CONFIRMED                   Delta >= M (0.010), lower end > 0, guards G1 to G4 pass
  GAIN, FAILING GUARDS NAMED  Delta >= M and lower end > 0, a guard fails
  NOT CONFIRMED               otherwise: "WORSE" if the upper end < 0; else "interval holds 0" or "below M"
Guards (point values = means over the 5 seeds; bounds inclusive): G1 width ratio C2 / C1 pooled in [0.85, 1.15]; G2 the same
per source with >= 40 cells (CSIR); G3 false crack px on crack-free cells C2 <= 1.5 x C1; G4 mIoU-R13 Delta >= -0.010.
Inactive IoU never decides ("inactive lower" when its seed-aware interval lies wholly below 0). Every strict crack IoU
contrast is printed with the convention band (band(): "inside / outside the convention band +-0.019; decides nothing"; the
value of FINAL_RULE.md section 2). Everything else is descriptive. Round 1 fixes (REVIEW_OPENING.md 3f7d6d4e): B1 (the band on
every strict-IoU delta line), N2 (inactive fixed-model interval, per-class IoU of the 13 robust classes, component recall /
precision), N3 (the fin CV5 TTA decisions (a) / (b) / (c) quoted from the registered fin verdict), N4 / N5 (wording).
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

M = 0.010
WIDTH = (0.85, 1.15)
FA_X = 1.5
MIOU_MIN = -0.010
BAND = 0.019          # FINAL_RULE.md section 2: the largest shift of a strict-IoU contrast across the label conventions
MIN_SRC_CELLS = 40
PRIMARY = ("C1", "C2")
E1_N, E1_CLUSTERS, T50_N, T50_CLUSTERS = 106, 71, 50, 48
BESIDE_E1 = (("C1", "C3", "S1 C3 - C1 (ensemble against the baseline)"),
             ("EPF", "C3", "S2 C3 - E-PF (the ensemble comparator; C3 costs 8 x E-PF; fixed models)"),
             ("C2", "C3", "S3 C3 - C2 (the ensemble's gain over its members)"),
             ("C1", "C2S5", "S4 C2 seed 5 (deployable) - C1"),
             ("C1", "EPF", "S5 E-PF - C1"),
             ("C1", "C1D4", "C1-D4 - C1 (D4 on PF; descriptive)"),
             ("C1D4", "C2", "C2 - C1-D4 (same views; descriptive)"))
PUBLISHED = [  # T/harness/final/PUBLIC_BENCH.md section 2a (copied; old masks; single runs)
    "Pratt 2023 model 4c (DeepLabv3+, custom weights), median IoU (rule A inferred): crack 0.25, gridline 0.20, inactive 0.38, "
    "mean of 3 0.28; ribbons 0.63, spacing 0.77; median recall crack 0.86 (Fig. 7 / 8; doi:10.1016/j.sasc.2023.200048)",
    "Pratt 2023 best per class over 12 models: crack 0.26 (1c), gridline 0.32 (1a, 2a), inactive 0.38 (4c)",
    "SEiPV-Net (equal weights): 'mIoU' 0.8604, 'IoU' 0.7447, Dice 0.8531, F1 0.9426, P 0.9491, R 0.9362 (averaging not defined; "
    "doi:10.3390/en16237726)",
    "PV-S3 CSB-S1, FSL 100%: crack IoU 0.58 (P 0.86, R 0.64), gridline 0.83, inactive 0.50 (P 0.62, R 0.71), mean 0.6367 "
    "(split not stated, background rule not stated; doi:10.1016/j.engappai.2025.111790)",
    "Not comparable (other test sets that overlap our training pool): Attention-Based SegNet 2024, Ramadan 2026, Hanifi 2025, "
    "Torpey 2024"]
ROB13 = {0: "background", 1: "sp multi", 2: "sp mono", 4: "ribbons", 5: "border", 7: "padding", 11: "inactive", 13: "material",
         14: "crack", 15: "gridline", 16: "splice", 20: "edge dark", 21: "frame edge"}
DISCLOSURES = [
    "test50 leakage (results/stageC/SPLIT_INTEGRITY.md 5b): 8 test cells are the same physical cell as a pool cell, 7 are "
    "neighbouring crops, 19 more share a module with pool cells; the full-pool models trained on all of them: test50 numbers are "
    "in-distribution numbers with known leakage.",
    "prior looks: test50 18 counted openings and many uncounted reads; E1 7 registered openings (3 looks at one contrast) plus "
    "reads before 31 Oct and one use of published E1 contrasts (R0, 15 Nov); the final models were never scored on either set.",
    "selection: readout swad chosen after the c3x CV5 read; D4 adopted from the B5 CV5 read; both on pool cells only; the "
    "candidates were fixed by the user before any number of the final models; HRNet + SWAD (swad_bn) failed its CV5 "
    "confirmation (C3X_READ.md).",
    "E1: 101 of 106 cells CSIR, 62 half-cut cells (the pool has none), 10 inactive cells, crack in 32 cells; no published "
    "comparator; one primary contrast; all dumps on cv02 (one GPU model), the read on gaint CPU.",
    "entry class: C2 is entry class (c) of protocol 6.1 (D4 = 8 views) and P compares it with C1 at 1 view: P is the contrast of "
    "the whole candidate (HRNet-W18 U-Net++ + SWAD, D4: 8 views) against PF (one view). Only C1-D4 (in the opening iff the fin "
    "read (a) replicated B5) separates the D4 part from the model part; if C1-D4 is absent, nothing on E1 separates them.",
    "operating point: OP-A only, a stated deviation from protocol 5.4 (a crack gain counts at OP-A and OP-W): OP-W needs a bias "
    "fitted on held-out folds, which full-pool models do not have, and fitting it on a sealed set would be tuning; the width "
    "guards G1 / G2 (0.85 to 1.15, pooled and CSIR) take OP-W's role."]


def band(d) -> str:
    """The convention-band label of a strict crack IoU contrast (B1): never omitted, never deciding."""
    w = "inside" if nz(d) and abs(d) <= BAND else "outside"
    return f"{w} the convention band +-{BAND}; decides nothing"


def siou(m: dict) -> str:
    """strict crack IoU delta [lo, hi] with its band (every strict-IoU contrast goes through here)."""
    return f"strict crack IoU {ci(m, 'crack_iou')} ({band(m['crack_iou']['delta'])})"


def nz(x):
    return x is not None and not (isinstance(x, float) and math.isnan(x))


def f(x, nd=4, sign=True):
    if not nz(x):
        return "n/a"
    return f"{x:+.{nd}f}" if sign else f"{x:.{nd}f}"


def check_read(doc: dict, set_name: str, n: int, ncl: int, labels: str, arms_needed) -> list[str]:
    bad = []
    if doc.get("set") != set_name or doc.get("n_cells") != n or doc.get("n_clusters") != ncl:
        bad.append(f"{set_name}: set / cells / clusters = {doc.get('set')} / {doc.get('n_cells')} / {doc.get('n_clusters')}")
    if doc.get("labels") != labels:
        bad.append(f"{set_name}: labels {doc.get('labels')} != {labels}")
    if doc.get("boot") != 2000 or doc.get("boot_seed") != 0:
        bad.append(f"{set_name}: bootstrap {doc.get('boot')} draws seed {doc.get('boot_seed')} (2000, 0 registered)")
    for a in arms_needed:
        if a not in doc.get("arms", {}):
            bad.append(f"{set_name}: arm {a} missing")
    for a in ("C1", "C2"):
        if a in doc.get("arms", {}) and sorted(r["seed"] for r in doc["arms"][a]["runs"]) != [5, 6, 7, 8, 9]:
            bad.append(f"{set_name}: arm {a} seeds {[r['seed'] for r in doc['arms'][a]['runs']]}")
    return bad


def guards(doc: dict, A="C1", B="C2") -> list[tuple[bool, str, str]]:
    """[(pass, item, text)] for G1 to G4 on the E1 read."""
    out = []
    S = doc["subsets"]["all"]
    gr = S["guard_ratios"][f"{B} - {A}"]
    w = gr["width_ratio"]["B_over_A"]
    out.append((nz(w) and WIDTH[0] <= w <= WIDTH[1], "G1 width pooled",
                f"G1 width ratio {B} / {A} pooled {f(w, 3, False)} (band {WIDTH[0]} to {WIDTH[1]}; {B} "
                f"{f(gr['width_ratio']['B'], 3, False)}, {A} {f(gr['width_ratio']['A'], 3, False)})"))
    for sn, n in sorted(doc["subset_n"].items()):
        if sn.startswith("src:") and n >= MIN_SRC_CELLS:
            g = doc["subsets"][sn]["guard_ratios"][f"{B} - {A}"]["width_ratio"]["B_over_A"]
            out.append((nz(g) and WIDTH[0] <= g <= WIDTH[1], f"G2 width {sn[4:]}",
                        f"G2 width ratio {B} / {A} on {sn[4:]} ({n} cells) {f(g, 3, False)} (band {WIDTH[0]} to {WIDTH[1]})"))
    fa = gr["fa_px"]
    ok = nz(fa["A"]) and nz(fa["B"]) and fa["B"] <= FA_X * fa["A"]
    out.append((ok, "G3 false crack px", f"G3 false crack px on the {S['arms'][A]['models'][next(iter(S['arms'][A]['models']))].get('fa_cells')} "
                f"crack-free cells: {B} {f(fa['B'], 0, False)} <= {FA_X} x {A} {f(fa['A'], 0, False)} (ratio {f(fa['B_over_A'], 3, False)})"))
    d = S["contrasts"][f"{B} - {A}"]["seed_aware"]["metrics"]["miou_rob"]["delta"]
    out.append((nz(d) and d >= MIOU_MIN, "G4 mIoU-R13", f"G4 mIoU-R13 delta {f(d)} >= {MIOU_MIN}"))
    return out


def decide(doc: dict, A="C1", B="C2") -> dict:
    C = doc["subsets"]["all"]["contrasts"][f"{B} - {A}"]
    r = C["seed_aware"]["metrics"]["relF1_2"]
    d, lo, hi = r["delta"], r["lo"], r["hi"]
    head = nz(d) and nz(lo) and d >= M and lo > 0
    G = guards(doc, A, B)
    fails = [item for ok, item, _ in G if not ok]
    if head and not fails:
        oc = "CONFIRMED"
    elif head:
        oc = "GAIN, FAILING GUARDS NAMED"
    else:
        if nz(hi) and hi < 0:
            oc = "NOT CONFIRMED (WORSE: the interval lies wholly below 0)"
        elif nz(lo) and lo > 0:
            oc = "NOT CONFIRMED (below M: the interval is above 0 but Delta < M)"
        else:
            oc = f"NOT CONFIRMED (the interval holds 0; Delta {'>' if nz(d) and d > 0 else '<='} 0)"
    ina = C["seed_aware"]["metrics"]["inact_iou"]
    sci = C["seed_aware"]["metrics"]["crack_iou"]
    return {"outcome": oc, "headline": head, "delta": d, "lo": lo, "hi": hi, "se": r["se"], "guards": G, "fails": fails,
            "inactive_lower": nz(ina["hi"]) and ina["hi"] < 0, "inactive": ina,
            "inactive_fixed": C["fixed"]["metrics"].get("inact_iou", {"delta": None, "lo": None, "hi": None}),
            "strict_iou": sci, "strict_band": "inside the convention band" if nz(sci["delta"]) and abs(sci["delta"]) <= BAND
            else "outside the convention band",
            "fixed": C["fixed"]["metrics"]["relF1_2"]}


def ci(m: dict, k: str) -> str:
    x = m[k]
    return f"{f(x['delta'])} [{f(x['lo'])}, {f(x['hi'])}]"


def e1_lines(doc: dict, res: dict) -> list[str]:
    L = ["## E1 opening #8: the primary contrast P = C2 - C1 (crack relF1@2, OP-A, 106 cells, 71 clusters)",
         f"Delta {f(res['delta'])}, seed-aware 95% interval [{f(res['lo'])}, {f(res['hi'])}] (SE {f(res['se'], 4, False)}); M {M:.3f}"]
    L += [f"{'PASS' if ok else 'FAIL'}\t{t}" for ok, _, t in res["guards"]]
    L.append(f"=> P: {res['outcome']}" + (f"; failing guard items: {', '.join(res['fails'])}" if res["fails"] else ""))
    fi = res["inactive_fixed"]
    L.append(f"   inactive IoU (reported, never decides; 10 inactive cells): {f(res['inactive']['delta'])} "
             f"seed-aware [{f(res['inactive']['lo'])}, {f(res['inactive']['hi'])}], fixed-model [{f(fi['lo'])}, {f(fi['hi'])}]"
             + ("  -> inactive lower" if res["inactive_lower"] else ""))
    s = res["strict_iou"]
    L.append(f"   strict crack IoU: {f(s['delta'])} [{f(s['lo'])}, {f(s['hi'])}] ({band(s['delta'])})")
    L.append(f"   fixed-model interval of P (the 10 trained models fixed; clusters only): [{f(res['fixed']['lo'])}, {f(res['fixed']['hi'])}]")
    C = doc["subsets"]["all"]["contrasts"]["C2 - C1"]["seed_aware"]["metrics"]
    L.append(f"   relP@2 {ci(C, 'relP2')}; relR@2 {ci(C, 'relR2')}; relF1@1 {ci(C, 'relF1_1')}")
    L.append("")
    L.append("## E1 per model (OP-A): relF1@2 / strict crack IoU / inactive IoU / mIoU-R13 / width ratio / false crack px")
    for a, A in doc["subsets"]["all"]["arms"].items():
        for sd, m in A["models"].items():
            L.append(f"{a}\tseed {sd}\t{f(m.get('relF1_2'), 4, False)}\t{f(m.get('crack_iou'), 4, False)}\t"
                     f"{f(m.get('inact_iou'), 4, False)}\t{f(m.get('miou_rob'), 4, False)}\t{f(m.get('width_ratio'), 3, False)}\t"
                     f"{f(m.get('fa_px'), 0, False)}")
    L.append("")
    L.append("## E1 printed beside (decides nothing)")
    for A, B, title in BESIDE_E1:
        key = f"{B} - {A}"
        if key not in doc["subsets"]["all"]["contrasts"]:
            continue
        C = doc["subsets"]["all"]["contrasts"][key]
        sa, fx = C["seed_aware"]["metrics"], C["fixed"]["metrics"]
        L.append(f"{title}: relF1@2 {ci(sa, 'relF1_2')} (fixed-model [{f(fx['relF1_2']['lo'])}, {f(fx['relF1_2']['hi'])}]); "
                 f"{siou(sa)}; inactive IoU {ci(sa, 'inact_iou')}; mIoU-R13 {ci(sa, 'miou_rob')}")
    if doc.get("aa"):
        m = doc["aa"]["seed_aware"]["metrics"]["relF1_2"]
        L.append(f"A/A C1 {{7,8}} - {{5,6}} (descriptive): relF1@2 {f(m['delta'])} [{f(m['lo'])}, {f(m['hi'])}], SE {f(m['se'])}")
    L.append("")
    L.append("## E1 strata (decide nothing): C2 - C1 relF1@2, seed-aware interval; n cells / clusters")
    for sn, S in doc["subsets"].items():
        if sn == "all" or "C2 - C1" not in S["contrasts"]:
            continue
        m = S["contrasts"]["C2 - C1"]["seed_aware"]["metrics"]
        L.append(f"{sn}\t{S['n']} / {S['n_clusters']}\trelF1@2 {ci(m, 'relF1_2')}\t{siou(m)}")
    L.append("")
    L += classes_lines(doc)
    return L


def classes_lines(doc: dict) -> list[str]:
    """N2: per-class IoU of the 13 robust classes and component recall / precision, arm means over models (all cells)."""
    A = doc["subsets"]["all"]["arms"]
    arms = list(A)
    L = ["## E1 per-class IoU of the 13 robust classes (OP-A; arm mean over its models; decides nothing)",
         "| class | " + " | ".join(arms) + " |", "|---|" + "---|" * len(arms)]
    for c, name in ROB13.items():
        row = []
        for a in arms:
            v = [m.get("per_class_iou", {}).get(str(c), m.get("per_class_iou", {}).get(c)) for m in A[a]["models"].values()]
            v = [x for x in v if nz(x)]
            row.append(f(sum(v) / len(v), 4, False) if v else "n/a")
        L.append(f"| {c} {name} | " + " | ".join(row) + " |")
    L += ["", "## E1 components (OP-A; arm mean; decides nothing): crack >= 20 px recall (>= 50% covered within 2 px) / "
              "precision; inactive >= 100 px recall / precision",
          "| arm | crack recall | crack precision | inactive recall | inactive precision |", "|---|---|---|---|---|"]
    for a in arms:
        sm = A[a]["summary"]
        g = lambda k: sm.get(k, {}).get("mean")  # noqa: E731
        L.append(f"| {a} | {f(g('cc_rec50_20'), 3, False)} | {f(g('cc_prec_20'), 3, False)} | {f(g('in_cc_rec50'), 3, False)} | "
                 f"{f(g('in_cc_prec'), 3, False)} |")
    return L


def t50_lines(v11: dict, v0: dict) -> list[str]:
    L = ["## test50 opening #19: the public table (decides nothing alone; leakage disclosed below)",
         "### Published rows (copied, PUBLIC_BENCH.md 2a)"] + [f"- {p}" for p in PUBLISHED]
    L.append("### Ours on v0 (BenchmarkEL 20211104 masks_coded), all 50 cells, 512 px, OP-A: mean over seeds [min, max]; seed 5")
    pub = v0["public"]
    keys = [("pratt_A_crack", "Pratt A crack"), ("pratt_A_gridline", "Pratt A gridline"), ("pratt_A_inactive", "Pratt A inactive"),
            ("pratt_A_avg_defects", "Pratt A mean of 3"), ("pratt_A_ribbons", "Pratt A ribbons"), ("pratt_A_spacing", "Pratt A spacing"),
            ("pratt_B_avg_defects", "Pratt B mean of 3"), ("pratt_C_avg_defects", "Pratt C mean of 3"),
            ("pratt_recallA_crack", "Pratt median recall crack"),
            ("pvs3_all_crack_iou", "PV-S3 crack IoU (all px)"), ("pvs3_all_gridline_iou", "PV-S3 gridline IoU (all px)"),
            ("pvs3_all_inactive_iou", "PV-S3 inactive IoU (all px)"), ("pvs3_all_mean_iou", "PV-S3 mean IoU (all px)"),
            ("pvs3_dropbg_mean_iou", "PV-S3 mean IoU (bg GT dropped)"),
            ("seipv_pixel_acc", "SEiPV pixel acc"), ("seipv_micro_iou", "SEiPV micro IoU"), ("seipv_fw_iou", "SEiPV fw-IoU"),
            ("seipv_f1_weighted", "SEiPV F1 weighted"), ("seipv_per_image_miou_absent1", "SEiPV per-image mIoU absent=1"),
            ("seipv_per_image_miou_skip", "SEiPV per-image mIoU absent skipped"), ("seipv_miou_gt_bg", "SEiPV mIoU GT classes + bg"),
            ("seipv_miou_gt_nobg", "SEiPV mIoU GT classes, no bg")]
    arms = [a for a in ("C1", "C2", "C1D4") if a in pub]
    L.append("| metric | " + " | ".join(f"{a} mean [min, max] | {a} seed 5" for a in arms) + " |")
    L.append("|---|" + "---|---|" * len(arms))
    for k, lab in keys:
        row = []
        for a in arms:
            s = pub[a]["summary"][k]
            m5 = _flat5(pub[a]["models"].get("5"), k)
            row.append(f"{f(s['mean'], 3, False)} [{f(s['min'], 3, False)}, {f(s['max'], 3, False)}] | {f(m5, 3, False)}")
        L.append(f"| {lab} | " + " | ".join(row) + " |")
    L.append("### Ours on v1.1 (our protocol), OP-A: relF1@2 / strict crack IoU / inactive IoU / mIoU-R13 / width / false crack px")
    for sn in ("all", "clean49", "nolink16"):
        if sn not in v11["subsets"]:
            continue
        S = v11["subsets"][sn]
        for a, A in S["arms"].items():
            sm = A["summary"]
            g = lambda k: sm.get(k, {}).get("mean")  # noqa: E731
            L.append(f"{sn} ({S['n']} cells)\t{a}\t{f(g('relF1_2'), 4, False)}\t{f(g('crack_iou'), 4, False)}\t"
                     f"{f(g('inact_iou'), 4, False)}\t{f(g('miou_rob'), 4, False)}\t{f(g('width_ratio'), 3, False)}\t{f(g('fa_px'), 0, False)}")
        if "C2 - C1" in S["contrasts"]:
            m = S["contrasts"]["C2 - C1"]["seed_aware"]["metrics"]
            L.append(f"{sn}\tC2 - C1 (secondary, decides nothing alone): relF1@2 {ci(m, 'relF1_2')}; {siou(m)}")
    return L


R_TREE = "/home/noob/work/bench_wt_open"   # the read worktree at R (scripts/bench_open_read.py)


def fin_lines(path: str, reg: str) -> tuple[list[str], list[str]]:
    """N3: the fin CV5 TTA decisions (a), (b), (c) quoted from the fin verdict whose md5 the registration names.
    Returns (lines, problems)."""
    import hashlib
    import re
    bad = []
    m = re.search(r"^c1d4 (yes|no) \(fin verdict ([0-9a-f]{32})\)", reg, re.M)
    txt = Path(path).read_bytes() if Path(path).exists() else b""
    if not m:
        bad.append("the registration names no fin verdict md5")
    elif hashlib.md5(txt).hexdigest() != m.group(2):
        bad.append(f"fin verdict {path}: md5 {hashlib.md5(txt).hexdigest()} != the registered {m.group(2)}")
    lines = txt.decode(errors="replace").splitlines()
    if any("MECHANICS" in l for l in lines):
        bad.append("the fin verdict holds MECHANICS (test) lines")
    got = {k: [l for l in lines if l.startswith(f"({k}) ")] for k in "abc"}
    for k, v in got.items():
        if len(v) != 1:
            bad.append(f"fin verdict: decision ({k}) found {len(v)} times (1 expected)")
    out = ["## fin CV5 TTA read (FINAL_RULE section 4): its decisions, quoted as registered (OPENING_RULE section 10)"]
    out += [v[0] for v in got.values() if len(v) == 1]
    return out, bad


def _flat5(row, k):
    if row is None:
        return None
    if R_TREE + "/scripts" not in sys.path:
        sys.path.insert(0, R_TREE + "/scripts")
    from bench_open_read import _flat_public  # the read's own flattening (R)
    return _flat_public(row).get(k)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--e1", required=True)
    ap.add_argument("--t50", required=True)
    ap.add_argument("--t50v0", required=True)
    ap.add_argument("--reg", required=True)
    ap.add_argument("--fin-verdict", required=True, help="the fin CV5 TTA verdict.txt the registration names by md5 (N3)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--mechanics", action="store_true", help="tests: skip the cell / cluster count checks")
    a = ap.parse_args(argv)
    out = Path(a.out)
    if out.exists():
        sys.exit(f"refuse: {out} exists")
    e1, v11, v0 = (json.loads(Path(p).read_text()) for p in (a.e1, a.t50, a.t50v0))
    reg = Path(a.reg).read_text()
    bad = []
    if not a.mechanics:
        bad += check_read(e1, "e1_106", E1_N, E1_CLUSTERS, "set", ("C1", "C2", "C3", "EPF", "C2S5"))
        bad += check_read(v11, "test50", T50_N, T50_CLUSTERS, "v11", ("C1", "C2", "C2S5"))
        bad += check_read(v0, "test50", T50_N, T50_CLUSTERS, "v0", ("C1", "C2", "C2S5"))
        if ("c1d4 yes" in reg) != ("C1D4" in e1["arms"]) or ("c1d4 yes" in reg) != ("C1D4" in v0["arms"]):
            bad.append("C1-D4 arms do not match the registration")
    FL, fbad = fin_lines(a.fin_verdict, reg)
    runs_f2 = [l for l in reg.splitlines() if l.startswith("runs F2 ")]   # round 3 (i): the fin2 resume, as registered
    if len(runs_f2) != 1:
        fbad = fbad + [f"the registration holds {len(runs_f2)} 'runs F2' lines (1 expected)"]
    if not a.mechanics:
        bad += fbad
        if bad:
            sys.exit("refuse: " + "; ".join(bad))
    res = decide(e1)
    L = ["# Verdict of the final opening (OPENING_RULE.md; E1 opening #8 decides, test50 opening #19 is the public table)",
         "# relF1@2 decides; strict crack IoU is printed with its convention band and decides nothing; OP-A only; no threshold "
         "or bias was set on a sealed cell.",
         "# registration: " + " | ".join(l for l in reg.splitlines() if l.split(" ", 1)[0] in ("registered", "rule", "jobs", "c1d4", "flags", "TEST")),
         ""] + FL + ([f"(fin verdict problems, mechanics run only: {'; '.join(fbad)})"] if fbad else []) + [""]
    L += e1_lines(e1, res) + [""] + t50_lines(v11, v0) + ["", "## Disclosures"] + [f"- {d}" for d in DISCLOSURES]
    L.append("- fin2 resume of the full-pool runs (registration line, quoted): "
             + (runs_f2[0] if len(runs_f2) == 1 else "MISSING (mechanics run only)"))
    L.append("")
    L.append(f"FINAL OPENING VERDICT: E1 P (C2 - C1 relF1@2) {res['outcome']}; Delta {f(res['delta'])} "
             f"[{f(res['lo'])}, {f(res['hi'])}]; test50: public table only.")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L) + "\n")
    js = {k: v for k, v in res.items() if k != "guards"}
    js["guards"] = [{"pass": ok, "item": it, "text": t} for ok, it, t in res["guards"]]
    out.with_suffix(".json").write_text(json.dumps(js, indent=1))
    print(L[-1])


if __name__ == "__main__":
    main()
