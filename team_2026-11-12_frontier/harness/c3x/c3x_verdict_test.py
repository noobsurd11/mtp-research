"""c3x: tests of c3x_verdict.py (LAUNCH_REQUEST_c3x.md section 6). Every case is a SYNTHETIC read.json built here from scratch
in the read tool's structure (bench_read_w1.py fdb56b78: summary, per_seed, contrasts, aa, M, runs, the x416 block), with
single values set by hand: the cases test the rule's branches; they are not results and hold no measured number.

Base case: shaped like the registered read (A/A PF:5,6:7,8; 5 arms x 25 runs, seeds 5 to 9, cv5v3_f<k> sets; the six
contrasts); COMBO and COMBO_SWAD pass headline and guards against PF; COMBO adds against HRNET and shows no loss against
SWADBN. M(relF1@2) 0.010 on 532 cells, 0.012 on 416 cells; M(inactive) 0.05; M(mIoU-R13) 0.010.

Usage: python -B c3x_verdict_test.py <new work dir>     (CPU, a few seconds; writes only into the work dir)
"""
from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PY = "/home/noob/work/el-fault-detection/.venv/bin/python"
ARMS = ("PF", "HRNET", "SWADBN", "COMBO", "COMBO_SWAD")
PAIRS = [("PF", "COMBO"), ("PF", "COMBO_SWAD"), ("HRNET", "COMBO"), ("HRNET", "COMBO_SWAD"), ("SWADBN", "COMBO"), ("SWADBN", "COMBO_SWAD")]
OPS = ("OP-A", "OP-F", "OP-W")
SRC = {"532": {"ARTS": 182, "BMRK": 50, "CFVS": 169, "CSIR": 114, "SDLE": 17}, "416": {"ARTS": 131, "BMRK": 50, "CFVS": 132, "CSIR": 103}}
X = "x416"
MECH = "MECHANICS TEST, NOT A VERDICT"


def m(delta, lo, hi=None, se=0.004):
    return {"delta": delta, "lo": lo, "hi": hi if hi is not None else delta + (delta - lo), "se": se}


def block(n_stems, srcs, Mr):
    g = lambda n, w=1.0, fa=400.0: {"n": n, "width_ratio": {"mean": w, "sd": 0.01, "n": 25}, "fa_px": {"mean": fa, "sd": 1, "n": 25},  # noqa: E731
                                     "fa_share50": {"mean": 0.01, "sd": 0, "n": 25}, "relF1_2": {"mean": 0.85, "sd": 0, "n": 25}}
    summ = {a: {op: {"all": g(n_stems), **{f"src:{s}": g(n) for s, n in srcs.items()}} for op in OPS} for a in ARMS}
    ps = {a: {op: {"all": {str(s): {"relF1_2": 0.85, "crack_iou": 0.37, "miou_rob": 0.61} for s in range(5, 10)}} for op in OPS} for a in ARMS}
    keys = ("relF1_2", "crack_iou", "inact_iou", "miou_rob")
    con = {f"{b} - {a}": {op: {"metrics": {"relF1_2": m(0.020, 0.008), "crack_iou": m(0.0, -0.01), "inact_iou": m(0.0, -0.03),
                                           "miou_rob": m(0.0, -0.005)}} for op in OPS} for a, b in PAIRS}
    for op in OPS:   # base: COMBO adds against HRNET; no loss against SWADBN (delta 0.0, lo -0.005 > -M)
        for r in ("COMBO", "COMBO_SWAD"):
            con[f"{r} - SWADBN"][op]["metrics"]["relF1_2"] = m(0.0, -0.005)
    aa = {op: {"metrics": {k: m(0.001, -0.007, se=0.004) for k in keys}} for op in OPS}
    return {"n_stems": n_stems, "aa_spec": "PF:5,6:7,8", "summary": summ, "per_seed": ps, "contrasts": con, "aa": aa,
            "M": {"relF1_2": Mr, "crack_iou": 0.010, "inact_iou": 0.05, "miou_rob": 0.010}, "groups_md5": "d880a769" + "0" * 24}


def base_doc():
    doc = block(532, SRC["532"], 0.010)
    doc.update(tool="bench_read_w1.py", tool_md5="fdb56b78" + "0" * 24, labels="v11",
               runs=[{"arm": a, "seed": s, "run_id": f"{a}_f{k}_s{s}", "set": f"cv5v3_f{k}", "fold": k} for a in ARMS for s in range(5, 10) for k in range(5)])
    doc[X] = block(416, SRC["416"], 0.012)
    return doc


SETS = {"532": lambda d: d, "416": lambda d: d[X]}


def con(doc, name, op, k, key="relF1_2", **kw):
    SETS[k](doc)["contrasts"][name][op]["metrics"][key].update(kw)


def width(doc, arm, op, sn, ratio, k):
    D = SETS[k](doc)
    D["summary"][arm][op][sn]["width_ratio"]["mean"] = ratio * D["summary"]["PF"][op][sn]["width_ratio"]["mean"]


def run(wd: Path, name: str, doc: dict, extra=(), probes=None):
    rd = wd / name
    (rd / "read").mkdir(parents=True)
    (rd / "read" / "read.json").write_text(json.dumps(doc))
    out = rd / "verdict.txt"
    cmd = [PY, "-B", str(HERE / "c3x_verdict.py"), "--read", str(rd), "--out", str(out), *extra] + (["--probes", str(probes)] if probes else [])
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r, (out.read_text() if out.exists() else "")


def section(t, head):
    i = t.index(head)
    return t[i:].split("\n## ")[0]


RESULTS = []


def check(name, ok, info=""):
    RESULTS.append((name, ok))
    print(f"{'PASS' if ok else 'FAIL'}\t{name}\t{info}")


def main() -> int:
    wd = Path(sys.argv[1])
    if wd.exists():
        sys.exit(f"refuse: {wd} exists")
    wd.mkdir(parents=True)
    V = lambda t: section(t, "## primary verdict")           # noqa: E731
    FM = lambda t: section(t, "## final-model rule")         # noqa: E731
    SEC = lambda t: section(t, "## secondary contrasts")     # noqa: E731

    # ---- primary branches (the c3swad rule)
    r, t = run(wd, "A_all_pass", base_doc())
    check("A all pass -> CONFIRMED, candidate", r.returncode == 0 and "CONFIRMED: the primary readout COMBO" in V(t)
          and "COMBO IS THE FINAL-MODEL CANDIDATE" in FM(t) and "=> COMBO - HRNET: ADDS   (used)" in t
          and "=> COMBO - SWADBN: NO LOSS   (used)" in t and MECH not in t, r.stderr[-300:])
    check("A2 candidate case: no single-arm information line", "information only" not in FM(t))
    d = base_doc(); con(d, "COMBO - PF", "OP-A", "532", delta=0.005, lo=-0.002)
    for k in ("532", "416"):
        for op in ("OP-A", "OP-W"):
            SETS[k](d)["summary"]["HRNET"][op]["all"]["relF1_2"]["mean"] = 0.8614
    r, t = run(wd, "A3_info_line", d)
    check("A3 not candidate: HRNET - PF and SWADBN - PF printed for both cell sets at OP-A and OP-W, no ranking",
          FM(t).count("HRNET - PF +0.0114") == 4 and FM(t).count("SWADBN - PF +0.0000") == 4 and "no ranking" in FM(t)
          and "the candidate is the best confirmed single arm" in FM(t))
    d = base_doc(); width(d, "COMBO", "OP-W", "src:ARTS", 1.16, "416")
    r, t = run(wd, "B_carry_opw_416", d)
    check("B only failing item a per-source width (ARTS OP-W 416) -> carried by COMBO.swad", "CONFIRMED, CARRIED BY THE DECLARED SECONDARY READOUT COMBO.swad" in V(t)
          and "width_source src:ARTS OP-W 416 clean cells" in V(t) and "Readout used for the final-model rule: COMBO_SWAD" in t
          and "COMBO IS THE FINAL-MODEL CANDIDATE: the primary claim is confirmed (carried by COMBO.swad)" in FM(t))
    d = base_doc(); width(d, "COMBO", "OP-A", "src:CSIR", 0.80, "532"); width(d, "COMBO", "OP-W", "src:ARTS", 1.20, "416")
    r, t = run(wd, "B2_carry_two_sources", d)
    check("B2 two per-source widths (either op, either cell set) -> carried", "CARRIED BY THE DECLARED SECONDARY READOUT" in V(t))
    d = base_doc(); width(d, "COMBO", "OP-A", "all", 1.20, "532")
    r, t = run(wd, "C_pooled_width", d)
    check("C pooled width fails -> not confirmed, named, no carry, not candidate", "NOT CONFIRMED, reported as a gain with the failing guards named" in V(t)
          and "width_pooled all OP-A 532 cells" in V(t) and "a failing guard item of COMBO is not a per-source width" in V(t)
          and "COMBO IS NOT THE FINAL-MODEL CANDIDATE (the primary claim is not confirmed)" in FM(t))
    d = base_doc(); con(d, "COMBO - PF", "OP-W", "416", delta=0.0119, lo=0.001)
    r, t = run(wd, "D_headline_delta_below_M", d)
    check("D headline delta < M at one of four (416 OP-W, M 0.012) -> no confirmed gain", "NOT CONFIRMED (no confirmed gain)" in V(t)
          and "COMBO IS NOT THE FINAL-MODEL CANDIDATE" in FM(t))
    d = base_doc(); con(d, "COMBO - PF", "OP-A", "532", delta=0.02, lo=0.0)
    r, t = run(wd, "E_headline_lo_zero", d)
    check("E headline CI low = 0 at one value -> no confirmed gain", "NOT CONFIRMED (no confirmed gain)" in V(t))
    d = base_doc(); con(d, "COMBO - PF", "OP-A", "532", delta=0.010, lo=0.0001)
    r, t = run(wd, "E2_headline_edge", d)
    check("E2 headline delta = M exactly and CI low > 0 -> passes (inclusive)", "CONFIRMED: the primary readout" in V(t))
    d = base_doc(); width(d, "COMBO", "OP-A", "src:ARTS", 1.20, "532")
    SETS["532"](d)["summary"]["COMBO_SWAD"]["OP-W"]["all"]["fa_px"]["mean"] = 700.0
    r, t = run(wd, "F_carry_but_swad_guard", d)
    check("F carry possible but COMBO.swad fails a guard (false alarms) -> not confirmed, named", "No carry by COMBO.swad: COMBO.swad does not pass every guard (false_alarm OP-W 532 cells)" in V(t))
    d = base_doc(); width(d, "COMBO", "OP-A", "src:ARTS", 1.20, "532"); con(d, "COMBO_SWAD - PF", "OP-A", "416", delta=0.005, lo=0.001)
    r, t = run(wd, "G_carry_but_swad_headline", d)
    check("G carry possible but COMBO.swad fails the headline -> not confirmed", "No carry by COMBO.swad: COMBO.swad does not pass the headline" in V(t))
    d = base_doc(); width(d, "COMBO", "OP-A", "src:ARTS", 1.20, "532"); con(d, "COMBO - PF", "OP-W", "532", key="inact_iou", delta=-0.06, lo=-0.1)
    r, t = run(wd, "H_source_plus_inactive", d)
    check("H per-source width + inactive guard -> no carry", "a failing guard item of COMBO is not a per-source width" in V(t) and "inactive OP-W 532 cells" in V(t))
    d = base_doc(); width(d, "COMBO", "OP-A", "src:SDLE", 2.0, "532")
    r, t = run(wd, "I_small_source", d)
    check("I source with 17 < 40 cells far outside -> not judged, confirmed", "CONFIRMED: the primary readout" in V(t) and "src:SDLE" not in t)
    d = base_doc(); width(d, "COMBO", "OP-W", "src:CFVS", 1.1499, "532")
    r, t = run(wd, "J1_band_1.1499", d)
    check("J1 per-source ratio 1.1499 passes", "CONFIRMED: the primary readout" in V(t))
    d = base_doc(); width(d, "COMBO", "OP-W", "src:CFVS", 1.1501, "532")
    r, t = run(wd, "J2_band_1.1501", d)
    check("J2 per-source ratio 1.1501 fails (then carried)", "CARRIED BY THE DECLARED SECONDARY READOUT" in V(t))
    d = base_doc(); width(d, "COMBO", "OP-A", "all", 0.8499, "416")
    r, t = run(wd, "J3_band_0.8499", d)
    check("J3 pooled ratio 0.8499 fails, no carry", "width_pooled all OP-A 416 clean cells" in V(t) and "NOT CONFIRMED, reported" in V(t))
    d = base_doc(); SETS["532"](d)["summary"]["COMBO"]["OP-A"]["all"]["fa_px"]["mean"] = 1.49 * 400
    r, t = run(wd, "K1_fa_1.49", d)
    check("K1 false alarms 1.49 x pass", "CONFIRMED: the primary readout" in V(t))
    d = base_doc(); SETS["532"](d)["summary"]["COMBO"]["OP-A"]["all"]["fa_px"]["mean"] = 1.51 * 400
    r, t = run(wd, "K2_fa_1.51", d)
    check("K2 false alarms 1.51 x fail, no carry", "false_alarm OP-A 532 cells" in V(t) and "NOT CONFIRMED, reported" in V(t))
    d = base_doc(); con(d, "COMBO - PF", "OP-A", "532", key="miou_rob", delta=-0.0101, lo=-0.02)
    r, t = run(wd, "L_miou_drop", d)
    check("L mIoU-R13 drop below -M fails the guard", "miou OP-A 532 cells" in V(t) and "NOT CONFIRMED, reported" in V(t))

    # ---- secondary labels (used readout COMBO in these cases: primary confirmed)
    d = base_doc()
    for k in ("532", "416"):
        for op in ("OP-A", "OP-W"):
            con(d, "COMBO - SWADBN", op, k, delta=0.03, lo=0.015)
    r, t = run(wd, "S1_adds_both", d)
    check("S1 adds against both", "=> COMBO - SWADBN: ADDS   (used)" in t and "=> COMBO - HRNET: ADDS   (used)" in t and "IS THE FINAL-MODEL CANDIDATE" in FM(t))
    d = base_doc(); con(d, "COMBO - HRNET", "OP-W", "416", delta=0.0119, lo=0.001)
    r, t = run(wd, "S2_no_loss_delta_below_M", d)
    check("S2 one value delta < M (416 M 0.012), all CI low > -M -> no loss", "=> COMBO - HRNET: NO LOSS   (used)" in t and "IS THE FINAL-MODEL CANDIDATE" in FM(t))
    d = base_doc(); con(d, "COMBO - HRNET", "OP-A", "532", delta=0.02, lo=0.0)
    r, t = run(wd, "S3_adds_lo_zero", d)
    check("S3 CI low = 0 at one value -> not adds, no loss", "=> COMBO - HRNET: NO LOSS" in t)
    d = base_doc(); con(d, "COMBO - SWADBN", "OP-W", "416", delta=-0.004, lo=-0.012)
    r, t = run(wd, "S4_loses_lo_eq_minus_M", d)
    check("S4 CI low = -M exactly (416, -0.012) -> loses; not candidate, reason named", "=> COMBO - SWADBN: LOSES   (used)" in t
          and "COMBO IS NOT THE FINAL-MODEL CANDIDATE (COMBO 'loses' against SWADBN)" in FM(t))
    d = base_doc(); con(d, "COMBO - SWADBN", "OP-W", "416", delta=-0.004, lo=-0.0119)
    r, t = run(wd, "S5_no_loss_lo_above_minus_M", d)
    check("S5 CI low = -0.0119 > -M -> no loss", "=> COMBO - SWADBN: NO LOSS   (used)" in t)
    d = base_doc(); con(d, "COMBO - HRNET", "OP-A", "532", delta=0.010, lo=0.0001)
    r, t = run(wd, "S6_adds_delta_eq_M", d)
    check("S6 delta = M exactly with CI low > 0 -> adds (inclusive)", "=> COMBO - HRNET: ADDS" in t)
    d = base_doc(); con(d, "COMBO - HRNET", "OP-A", "416", delta=-0.03, lo=-0.05)
    r, t = run(wd, "S7_loses_hrnet", d)
    check("S7 loses against HRNET -> not candidate", "=> COMBO - HRNET: LOSES   (used)" in t and "COMBO 'loses' against HRNET" in FM(t))
    r, t = run(wd, "S8_all_four_printed", base_doc())
    check("S8 all four secondary contrasts printed with 4 values each", all(t.count(f"secondary\t{c}\t") == 4 for c in
          ("COMBO - HRNET", "COMBO - SWADBN", "COMBO_SWAD - HRNET", "COMBO_SWAD - SWADBN")) and t.count("\n=> COMBO") >= 4)

    # ---- final-model rule with the carrying readout
    d = base_doc(); width(d, "COMBO", "OP-W", "src:ARTS", 1.16, "416"); con(d, "COMBO - SWADBN", "OP-A", "532", delta=-0.03, lo=-0.05)
    r, t = run(wd, "F1_carried_uses_swad_labels", d)
    check("F1 carried: COMBO loses vs SWADBN but COMBO.swad has no loss -> candidate (labels of the carrier)",
          "=> COMBO - SWADBN: LOSES\n" in t and "=> COMBO_SWAD - SWADBN: NO LOSS   (used)" in t and "IS THE FINAL-MODEL CANDIDATE" in FM(t))
    d = base_doc(); width(d, "COMBO", "OP-W", "src:ARTS", 1.16, "416"); con(d, "COMBO_SWAD - HRNET", "OP-W", "532", delta=-0.03, lo=-0.05)
    r, t = run(wd, "F2_carried_swad_loses", d)
    check("F2 carried: COMBO.swad loses vs HRNET -> not candidate", "COMBO IS NOT THE FINAL-MODEL CANDIDATE (COMBO_SWAD 'loses' against HRNET)" in FM(t))
    d = base_doc(); con(d, "COMBO - PF", "OP-A", "532", delta=0.005, lo=-0.002)
    for k in ("532", "416"):
        for op in ("OP-A", "OP-W"):
            con(d, "COMBO - SWADBN", op, k, delta=0.03, lo=0.015)
    r, t = run(wd, "F3_not_confirmed_adds_both", d)
    check("F3 primary not confirmed though COMBO adds against both -> not candidate", "NOT CONFIRMED (no confirmed gain)" in V(t)
          and "COMBO IS NOT THE FINAL-MODEL CANDIDATE (the primary claim is not confirmed)" in FM(t) and "single arms' own registered verdicts" in FM(t))

    # ---- check of the read (refusals; nothing written)
    def refused(name, doc, needle, extra=()):
        r, t = run(wd, name, doc, extra)
        check(f"{name} refused", r.returncode != 0 and needle in (r.stderr + r.stdout) and not (wd / name / "verdict.txt").exists()
              and "Traceback" not in r.stderr, (r.stderr + r.stdout)[-200:])
    d = base_doc(); d["aa_spec"] = "PF:5,6:8,9"; refused("R1_aa_spec", d, "A/A spec of the 532 cells block")
    d = base_doc(); d[X]["aa_spec"] = "HRNET:5,6:7,8"; refused("R2_aa_spec_416", d, "A/A spec of the 416 clean cells block")
    d = base_doc(); d["runs"] = [r_ for r_ in d["runs"] if not (r_["arm"] == "COMBO_SWAD" and r_["seed"] == 9 and r_["fold"] == 4)]
    refused("R3_24_runs", d, "arm COMBO_SWAD has 24 runs")
    d = base_doc(); d["runs"] = [dict(r_, seed=8, run_id=r_["run_id"] + "x") if (r_["arm"] == "HRNET" and r_["seed"] == 9) else r_ for r_ in d["runs"]]
    refused("R4_seed_missing", d, "arm HRNET has seeds [5, 6, 7, 8]")
    d = base_doc(); d["runs"][3]["set"] = "cv5v2_f3"; refused("R5_cv5v2_set", d, "holds sets that are not cv5v3_f<k>")
    d = base_doc(); del d[X]["contrasts"]["COMBO_SWAD - SWADBN"]; refused("R6_contrast_missing", d, "lacks the contrasts ['COMBO_SWAD - SWADBN']")
    d = base_doc(); SETS["416"](d)["summary"]["COMBO"]["OP-W"]["src:CSIR"]["width_ratio"]["mean"] = None
    refused("N1_null_width", d, "refuse: width ratio undefined for a judged subset (src:CSIR, OP-W, 416 clean cells)")
    d = base_doc(); SETS["532"](d)["summary"]["PF"]["OP-A"]["all"]["fa_px"]["mean"] = None
    refused("N2_null_fa", d, "refuse: false crack px undefined (OP-A, 532 cells)")
    # review N3: a null or NaN delta, CI end or margin anywhere the rule reads one -> one-line refusal naming the contrast
    d = base_doc(); con(d, "COMBO - PF", "OP-A", "532", delta=None); refused("N3a_null_delta_headline", d, "refuse: contrast COMBO - PF, OP-A, relF1_2: delta is None in the 532 cells block")
    d = base_doc(); con(d, "COMBO_SWAD - PF", "OP-W", "416", hi=float("nan")); refused("N3b_nan_hi_carry_headline", d, "refuse: contrast COMBO_SWAD - PF, OP-W, relF1_2: hi is nan in the 416 clean cells block")
    d = base_doc(); con(d, "COMBO - PF", "OP-W", "532", key="inact_iou", lo=None); refused("N3c_null_lo_inactive_guard", d, "refuse: contrast COMBO - PF, OP-W, inact_iou: lo is None in the 532 cells block")
    d = base_doc(); con(d, "COMBO - PF", "OP-A", "416", key="miou_rob", delta=float("nan")); refused("N3d_nan_delta_miou_guard", d, "refuse: contrast COMBO - PF, OP-A, miou_rob: delta is nan in the 416 clean cells block")
    d = base_doc(); con(d, "COMBO - SWADBN", "OP-W", "416", lo=float("nan")); refused("N3e_nan_lo_secondary", d, "refuse: contrast COMBO - SWADBN, OP-W, relF1_2: lo is nan in the 416 clean cells block")
    d = base_doc(); con(d, "COMBO_SWAD - HRNET", "OP-A", "532", delta=None); refused("N3f_null_delta_secondary", d, "refuse: contrast COMBO_SWAD - HRNET, OP-A, relF1_2: delta is None in the 532 cells block")
    d = base_doc(); d[X]["M"]["relF1_2"] = None; refused("N3g_null_margin", d, "refuse: the A/A margin M(relF1_2) of the 416 clean cells block is None")
    d = base_doc(); con(d, "COMBO - SWADBN", "OP-W", "416", lo=float("nan"))
    r, t = run(wd, "N3h_mechanics_also_refuses", d, ("--mechanics",))
    check("N3h a NaN is refused under --mechanics too (never a silent 'loses')", r.returncode != 0 and "lo is nan" in r.stderr + r.stdout and "Traceback" not in r.stderr)
    d = base_doc(); SETS["532"](d)["per_seed"]["COMBO"]["OP-A"]["all"]["7"]["relF1_2"] = None; SETS["416"](d)["summary"]["HRNET"]["OP-W"]["all"]["relF1_2"]["mean"] = None
    con(d, "COMBO - PF", "OP-A", "532", delta=0.005, lo=-0.002)
    r, t = run(wd, "N3i_beside_lines_na", d)
    check("N3i an undefined per-seed or information value beside the verdict prints n/a, no TypeError", r.returncode == 0 and "s7 n/a" in t
          and "HRNET - PF n/a" in t and "Traceback" not in r.stderr, r.stderr[-200:])
    d = base_doc(); d["aa_spec"] = "PF:5,6:8,9"
    r, t = run(wd, "R7_mechanics", d, ("--mechanics",))
    check("R7 --mechanics on a non-registered read: mark in first, verdict and final-model lines", r.returncode == 0 and t.startswith(f"# {MECH}")
          and f"[{MECH}] CONFIRMED" in V(t) and f"[{MECH}] COMBO IS THE FINAL-MODEL CANDIDATE" in FM(t))
    rd = wd / "A_all_pass"
    r2 = subprocess.run([PY, "-B", str(HERE / "c3x_verdict.py"), "--read", str(rd), "--out", str(rd / "verdict.txt")], capture_output=True, text=True)
    check("O1 existing output refused", r2.returncode != 0 and "exists" in r2.stderr + r2.stdout)

    # ---- probes (HRNet: one stage 'model')
    pr = wd / "probes"
    (pr / "c3x_hrnet_swad_v11_f0_s5" / "experiments" / "c3x_hrnet_swad_v11_f0_s5").mkdir(parents=True)
    (pr / "c3x_hrnet_swad_v11_f0_s5" / "experiments" / "c3x_hrnet_swad_v11_f0_s5" / "enc_probe.jsonl").write_text(
        json.dumps({"step": 18000, "stages": {"model": {"cos": 0.95, "nr": 1.1, "dev": 0.3, "n": 321}}}) + "\n"
        + json.dumps({"step": 20000, "stages": {"model": {"cos": 0.9, "nr": 1.2, "dev": 0.4, "n": 321}}}) + "\n")
    (pr / "c3x_hrnet_swad_v11_f1_s5" / "experiments" / "c3x_hrnet_swad_v11_f1_s5").mkdir(parents=True)
    (pr / "c3x_hrnet_swad_v11_f1_s5" / "experiments" / "c3x_hrnet_swad_v11_f1_s5" / "enc_probe.jsonl").write_text(
        json.dumps({"step": 20000, "stages": {"layer3": {"cos": 0.8, "nr": 1, "dev": 0.1, "n": 6}, "layer4": {"cos": 0.8, "nr": 1, "dev": 0.1, "n": 3}}}) + "\n")
    r, t = run(wd, "P1_probes", base_doc(), probes=pr)
    check("P1 probe lines: stage 'model' at step 20000; other stage names flagged", "probe\tc3x_hrnet_swad_v11_f0_s5\tmodel cos 0.9000" in t
          and "stages ['layer3', 'layer4'] (expected one stage 'model')" in t and "1 runs: encoder (stage 'model') cos" in t)

    n = sum(ok for _, ok in RESULTS)
    print(f"\nc3x verdict test: {n} of {len(RESULTS)} PASS")
    return 0 if n == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
