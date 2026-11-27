"""The registered T3b rule (T3B_RULE.md sections 7 to 9) applied to the T3b read (scripts/bench_open_read.py --t3b ZS at K).
Reads only read_t3b/read.json and the registration; writes verdict.txt and verdict.json; refuses an existing output.
Helpers (number format, interval text, the strict-IoU convention band, ROB13) are those of the final opening's verdict tool
(harness/final/opening/opening_verdict.py, md5 pinned below).

  python t3b_verdict.py --read O/read_t3b/read.json --reg IO/REGISTERED.txt --out O/verdict.txt

Primary P = ALL - ZS: pooled out-of-fold crack relF1@2 of the all arm (3 seeds) minus the zero-shot comparator (opening #8's
C2, the same seeds), 106 E1 cells, OP-A, seed-aware two-stage interval (71 clusters x models), 2,000 draws, Random(0):
  CONFIRMED                   Delta >= M (0.010), lower end > 0, guards G1 and G2 pass
  GAIN, FAILING GUARDS NAMED  Delta >= M and lower end > 0, a guard fails
  NOT CONFIRMED               otherwise: "WORSE" if the upper end < 0; else "interval holds 0" or "below M"
Guards (point values = arm means over the 3 seeds; bounds inclusive): G1 false crack px on the crack-free cells (GT crack px 0;
74 cells) ALL <= 1.5 x ZS; G2 mIoU-R13 Delta >= -0.010. The predicted crack width ratio ALL / ZS is reported, not a guard
(E1 labels are about 1.5 x wider than the pool labels the comparator learned: a model trained on E1 learns that width).
Printed beside, deciding nothing: HALF - ZS and ALL - HALF (both intervals), any-hit and >= 50% crack component recall,
strata full / half-cut / hard (half-cut + scuff) / half-cut without scuff, inactive IoU (reported only), mIoU-R13, strict
crack IoU (with the convention band), per-class IoU, per seed.
Review round 1: the read is refused unless the arms hold exactly the registered run ids (ALL = t3b_all_s5..7.oof, HALF =
t3b_half_s5..7.oof, ZS = fin_hrnet_swad_v11_pool_s5..7.swad.tta_d4.e1_106; B2) and every model counts 74 crack-free cells
(N3); --repeat TAG labels a repeat read in the header (N5).
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

OV_PATH = Path("/home/yugma/mtp/research/team_2026-11-12_frontier/harness/final/opening/opening_verdict.py")
OV_MD5 = "433f61debeb3135c0aad51524e19add9"
assert hashlib.md5(OV_PATH.read_bytes()).hexdigest() == OV_MD5, "opening_verdict.py is not the pinned file"
_spec = importlib.util.spec_from_file_location("opening_verdict", OV_PATH)
OVM = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(OVM)
f, nz, ci, band, ROB13, BAND = OVM.f, OVM.nz, OVM.ci, OVM.band, OVM.ROB13, OVM.BAND

M = 0.010
FA_X = 1.5
MIOU_MIN = -0.010
N_CELLS, N_CLUSTERS, SEEDS = 106, 71, [5, 6, 7]
N_CRACK_FREE = 74
RUN_IDS = {"ALL": [f"t3b_all_s{s}.oof" for s in SEEDS], "HALF": [f"t3b_half_s{s}.oof" for s in SEEDS],
           "ZS": [f"fin_hrnet_swad_v11_pool_s{s}.swad.tta_d4.e1_106" for s in SEEDS]}
ARMS = ("ALL", "HALF", "ZS")
BESIDE = (("ZS", "HALF", "HALF - ZS (half of the training-side E1 image ids against the zero-shot comparator)"),
          ("HALF", "ALL", "ALL - HALF (all against half of the training-side E1 image ids)"))
STRATA = (("strat_full", "full cells"), ("strat_halfcut", "half-cut cells"), ("strat_hard", "hard = half-cut + scuff"),
          ("strat_halfcut_noscuff", "half-cut without scuff"), ("crack_cells", "crack cells (GT crack px > 0)"),
          ("crack_free_cells", "crack-free cells"), ("src:CSIR", "CSIR cells"), ("src:BMRK", "BMRK cells"))
DISCLOSURES = [
    "E1 is training data for the T3b models from the registration of this opening (user, 21 Nov 2026 about 14:35 IST, "
    "'run T3b on free GPUs'); no later zero-shot claim on E1 by this team. The T3 table (opening #8) is frozen before it.",
    "ZS = the zero-shot comparator: opening #8's C2 (full-pool HRNet-W18 U-Net++ + SWAD, swad, D4) seeds 5 to 7, the same "
    "relayed dumps, re-scored by K's scorer; it never saw an E1 cell. It is printed beside, never a T3b model.",
    "Separation: every T3b record carries trained_on_e1; every T3 / E1-column scorer refuses it; this card is the only read "
    "that holds both (bench_open_read.py --t3b).",
    "Recipe fixed before any T3b number (the C2 recipe, final weights, swad, D4, argmax): no threshold, bias or checkpoint "
    "was chosen on E1; only the training list differs (pool532_v11 + the E1 cells of the other 4 folds, or a fixed half).",
    "Concentration (proposal section 4): half of E1's crack px sit in 3 image ids and the hard-stratum crack cells in 10; "
    "the pooled score has the uncertainty of about 9 images; single folds say little and are not printed as results.",
    "Folds are by image id; whether neighbouring CSIR ids are modules of one batch with shared handling marks is unknown, so "
    "the out-of-fold number may be optimistic for a truly new site.",
    "Label width: E1 labels are about 1.5 x wider than the pool labels; a T3b model learns that width, which lifts strict IoU "
    "and pixel recall without finding more cracks. relF1@2 decides; the width ratio is printed; strict IoU only with its band.",
    "Seeds: 3 (lead's choice over the proposal's 2; the seed-aware bootstrap needs more than 2). Machine: all 33 dumps on "
    "cv02 (one GPU model); the read on gaint CPU. One primary contrast; everything else is descriptive.",
    "Inactive: E1 has 10 inactive cells in 7 image ids (3 hold 87%): reported, never decides.",
    "T3b records live only under bench_reads/t3b_open9; record readers other than bench_open_read, bench_score summary and "
    "derived (e.g. bench_headres, bench_read_w1, bench_udev_read) do not check trained_on_e1 and are never pointed at them.",
    "From staging to unstage, DT/files on the shared cv02 login held the E1 training labels of all 106 cells (each fold's "
    "held-out labels present but not linked from its root; the deploy root needs all 106); removed at unstage."]


def check_read(doc: dict) -> list[str]:
    bad = []
    if doc.get("set") != "e1_106" or doc.get("n_cells") != N_CELLS or doc.get("n_clusters") != N_CLUSTERS:
        bad.append(f"set / cells / clusters = {doc.get('set')} / {doc.get('n_cells')} / {doc.get('n_clusters')}")
    if doc.get("labels") != "set":
        bad.append(f"labels {doc.get('labels')} != set")
    if doc.get("boot") != 2000 or doc.get("boot_seed") != 0:
        bad.append(f"bootstrap {doc.get('boot')} draws seed {doc.get('boot_seed')} (2000, 0 registered)")
    t = doc.get("t3b") or {}
    if t.get("comparator") != "ZS" or sorted(t.get("trained_on_e1_arms", [])) != ["ALL", "HALF"]:
        bad.append(f"T3b card: comparator {t.get('comparator')}, marked arms {t.get('trained_on_e1_arms')}")
    for a in ARMS:
        if a not in doc.get("arms", {}):
            bad.append(f"arm {a} missing")
        elif sorted(r["seed"] for r in doc["arms"][a]["runs"]) != SEEDS:
            bad.append(f"arm {a} seeds {[r['seed'] for r in doc['arms'][a]['runs']]}")
        elif sorted(r.get("run_id") for r in doc["arms"][a]["runs"]) != RUN_IDS[a]:
            bad.append(f"arm {a} run ids {sorted(r.get('run_id') for r in doc['arms'][a]['runs'])} != {RUN_IDS[a]}")
    S = doc.get("subsets", {}).get("all", {})
    for a in ARMS:
        for sd, m in S.get("arms", {}).get(a, {}).get("models", {}).items():
            if m.get("fa_cells") != N_CRACK_FREE:
                bad.append(f"arm {a} seed {sd}: {m.get('fa_cells')} crack-free cells ({N_CRACK_FREE} registered)")
    for c in ("ALL - ZS", "HALF - ZS", "ALL - HALF"):
        if c not in doc.get("subsets", {}).get("all", {}).get("contrasts", {}):
            bad.append(f"contrast {c} missing")
    return bad


def guards(doc: dict, A="ZS", B="ALL") -> list:
    S = doc["subsets"]["all"]
    gr = S["guard_ratios"][f"{B} - {A}"]
    fa = gr["fa_px"]
    n_cf = S["arms"][A]["models"][next(iter(S["arms"][A]["models"]))].get("fa_cells")
    ok1 = nz(fa["A"]) and nz(fa["B"]) and fa["B"] <= FA_X * fa["A"]
    d = S["contrasts"][f"{B} - {A}"]["seed_aware"]["metrics"]["miou_rob"]["delta"]
    return [(ok1, "G1 false crack px", f"G1 false crack px on the {n_cf} crack-free cells: {B} {f(fa['B'], 0, False)} <= {FA_X} x "
             f"{A} (zero-shot) {f(fa['A'], 0, False)} (ratio {f(fa['B_over_A'], 3, False)})"),
            (nz(d) and d >= MIOU_MIN, "G2 mIoU-R13", f"G2 mIoU-R13 delta {f(d)} >= {MIOU_MIN}")]


def decide(doc: dict, A="ZS", B="ALL") -> dict:
    C = doc["subsets"]["all"]["contrasts"][f"{B} - {A}"]
    r = C["seed_aware"]["metrics"]["relF1_2"]
    d, lo, hi = r["delta"], r["lo"], r["hi"]
    head = nz(d) and nz(lo) and d >= M and lo > 0
    G = guards(doc, A, B)
    fails = [it for ok, it, _ in G if not ok]
    if head and not fails:
        oc = "CONFIRMED"
    elif head:
        oc = "GAIN, FAILING GUARDS NAMED"
    elif nz(hi) and hi < 0:
        oc = "NOT CONFIRMED (WORSE: the interval lies wholly below 0)"
    elif nz(lo) and lo > 0:
        oc = "NOT CONFIRMED (below M: the interval is above 0 but Delta < M)"
    else:
        oc = f"NOT CONFIRMED (the interval holds 0; Delta {'>' if nz(d) and d > 0 else '<='} 0)"
    w = doc["subsets"]["all"]["guard_ratios"][f"{B} - {A}"]["width_ratio"]
    return {"outcome": oc, "headline": head, "delta": d, "lo": lo, "hi": hi, "se": r["se"], "guards": G, "fails": fails,
            "fixed": C["fixed"]["metrics"]["relF1_2"], "width": w, "inactive": C["seed_aware"]["metrics"]["inact_iou"],
            "strict": C["seed_aware"]["metrics"]["crack_iou"]}


def contrast_line(S: dict, A: str, B: str, title: str) -> str:
    C = S["contrasts"][f"{B} - {A}"]
    sa, fx = C["seed_aware"]["metrics"], C["fixed"]["metrics"]
    return (f"{title}: relF1@2 {ci(sa, 'relF1_2')} (fixed-model [{f(fx['relF1_2']['lo'])}, {f(fx['relF1_2']['hi'])}]); "
            f"strict crack IoU {ci(sa, 'crack_iou')} ({band(sa['crack_iou']['delta'])}); inactive IoU {ci(sa, 'inact_iou')} "
            f"(reported only); mIoU-R13 {ci(sa, 'miou_rob')}; width ratio B / A {f(S['guard_ratios'][f'{B} - {A}']['width_ratio']['B_over_A'], 3, False)}")


def lab(a: str) -> str:
    return "ZS (zero-shot comparator, never trained on E1)" if a == "ZS" else f"{a} (trained on E1, out-of-fold)"


def lines(doc: dict, res: dict) -> list[str]:
    S = doc["subsets"]["all"]
    L = ["## T3b opening #9: the primary contrast P = ALL - ZS (pooled out-of-fold crack relF1@2, OP-A, 106 cells, 71 clusters)",
         f"Delta {f(res['delta'])}, seed-aware 95% interval [{f(res['lo'])}, {f(res['hi'])}] (SE {f(res['se'], 4, False)}); M {M:.3f}"]
    L += [f"{'PASS' if ok else 'FAIL'}\t{t}" for ok, _, t in res["guards"]]
    L.append(f"=> P: {res['outcome']}" + (f"; failing guard items: {', '.join(res['fails'])}" if res["fails"] else ""))
    w = res["width"]
    L.append(f"   predicted crack width ratio ALL / ZS {f(w['B_over_A'], 3, False)} (ALL {f(w['B'], 3, False)}, ZS {f(w['A'], 3, False)}; "
             "reported, not a guard: E1 labels are about 1.5 x wider than the pool labels)")
    L.append(f"   fixed-model interval of P (the 6 trained models fixed; clusters only): [{f(res['fixed']['lo'])}, {f(res['fixed']['hi'])}]")
    L.append(f"   strict crack IoU {f(res['strict']['delta'])} [{f(res['strict']['lo'])}, {f(res['strict']['hi'])}] ({band(res['strict']['delta'])})")
    L.append(f"   inactive IoU {f(res['inactive']['delta'])} [{f(res['inactive']['lo'])}, {f(res['inactive']['hi'])}] (reported, never decides)")
    m = S["contrasts"]["ALL - ZS"]["seed_aware"]["metrics"]
    L.append(f"   relP@2 {ci(m, 'relP2')}; relR@2 {ci(m, 'relR2')}; relF1@1 {ci(m, 'relF1_1')}")
    L += ["", "## Printed beside (decide nothing)"] + [contrast_line(S, A, B, t) for A, B, t in BESIDE]
    L += ["", "## Crack components >= 20 px (arm mean over 3 seeds [min, max]; decide nothing): any-hit recall (a GT component "
          "counted if any px lies within 2 px of a predicted crack px) / recall at >= 50% covered / precision"]
    for a in ARMS:
        sm = S["arms"][a]["summary"]
        g = lambda k: sm.get(k, {})  # noqa: E731
        L.append(f"{lab(a)}: any-hit {f(g('cc_recany_20').get('mean'), 3, False)} [{f(g('cc_recany_20').get('min'), 3, False)}, "
                 f"{f(g('cc_recany_20').get('max'), 3, False)}]; >= 50% {f(g('cc_rec50_20').get('mean'), 3, False)}; precision "
                 f"{f(g('cc_prec_20').get('mean'), 3, False)}")
    L += ["", "## Strata (decide nothing): seed-aware intervals; n cells / clusters"]
    for sn, title in STRATA:
        T = doc["subsets"].get(sn)
        if not T or "ALL - ZS" not in T["contrasts"]:
            continue
        parts = []
        for c in ("ALL - ZS", "HALF - ZS", "ALL - HALF"):
            mm = T["contrasts"][c]["seed_aware"]["metrics"]
            parts.append(f"{c} relF1@2 {ci(mm, 'relF1_2')}")
        mm = T["contrasts"]["ALL - ZS"]["seed_aware"]["metrics"]
        L.append(f"{title} ({sn})\t{T['n']} / {T['n_clusters']}\t" + "; ".join(parts) +
                 f"; ALL - ZS strict crack IoU {ci(mm, 'crack_iou')} ({band(mm['crack_iou']['delta'])})")
    L += ["", "## Per model (OP-A): relF1@2 / strict crack IoU / inactive IoU / mIoU-R13 / width ratio / false crack px / any-hit recall"]
    for a in ARMS:
        for sd, mo in S["arms"][a]["models"].items():
            L.append(f"{lab(a)}\tseed {sd}\t{f(mo.get('relF1_2'), 4, False)}\t{f(mo.get('crack_iou'), 4, False)}\t{f(mo.get('inact_iou'), 4, False)}\t"
                     f"{f(mo.get('miou_rob'), 4, False)}\t{f(mo.get('width_ratio'), 3, False)}\t{f(mo.get('fa_px'), 0, False)}\t"
                     f"{f(mo.get('cc_recany_20'), 3, False)}")
    L += ["", "## Per-class IoU of the 13 robust classes (OP-A; arm mean; decides nothing)", "| class | ALL | HALF | ZS (zero-shot) |",
          "|---|---|---|---|"]
    for c, name in ROB13.items():
        row = []
        for a in ARMS:
            v = [mo.get("per_class_iou", {}).get(str(c), mo.get("per_class_iou", {}).get(c)) for mo in S["arms"][a]["models"].values()]
            v = [x for x in v if nz(x)]
            row.append(f(sum(v) / len(v), 4, False) if v else "n/a")
        L.append(f"| {c} {name} | " + " | ".join(row) + " |")
    return L


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--read", required=True)
    ap.add_argument("--reg", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--mechanics", action="store_true", help="tests: skip the cell / cluster / seed checks")
    ap.add_argument("--repeat", default=None, help="TAG of a repeat read (not the registered read)")
    a = ap.parse_args(argv)
    out = Path(a.out)
    if out.exists():
        sys.exit(f"refuse: {out} exists")
    doc = json.loads(Path(a.read).read_text())
    reg = Path(a.reg).read_text()
    bad = [] if a.mechanics else check_read(doc)
    if not a.mechanics and len([l for l in reg.splitlines() if l.startswith("opening_e1 E1 opening #9 e1_open9_t3b ")]) != 1:
        bad.append("the registration does not name E1 opening #9 e1_open9_t3b once")
    if bad:
        sys.exit("refuse: " + "; ".join(bad))
    res = decide(doc)
    L = ["# Verdict of the T3b opening (T3B_RULE.md; E1 opening #9): few-shot layout adaptation inside E1",
         "# relF1@2 decides; strict crack IoU is printed with its convention band and decides nothing; OP-A only; no threshold, "
         "bias or checkpoint was chosen on E1. ZS is the zero-shot comparator, printed beside, never a T3b model.",
         *([f"# REPEAT (TAG {a.repeat}), not the registered read"] if a.repeat else []),
         "# registration: " + " | ".join(l for l in reg.splitlines() if l.split(" ", 1)[0] in ("TEST", "registered", "rule", "lists", "jobs_dump", "commits", "zs")),
         ""] + lines(doc, res) + ["", "## Disclosures"] + [f"- {d}" for d in DISCLOSURES]
    L += ["", f"T3B VERDICT: P (ALL - ZS pooled out-of-fold crack relF1@2) {res['outcome']}; Delta {f(res['delta'])} "
              f"[{f(res['lo'])}, {f(res['hi'])}]; width ratio ALL / ZS {f(res['width']['B_over_A'], 3, False)} (reported)."]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L) + "\n")
    js = {k: v for k, v in res.items() if k != "guards"}
    js["guards"] = [{"pass": ok, "item": it, "text": t} for ok, it, t in res["guards"]]
    out.with_suffix(".json").write_text(json.dumps(js, indent=1))
    print(L[-1])


if __name__ == "__main__":
    main()
