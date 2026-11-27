"""Final package: tests of final_verdict.py (harness/final/FINAL_RULE.md sections 2 to 4). Every case is a SYNTHETIC
read.json built here from scratch in the read tool's structure (bench_read_w1.py fdb56b78: summary, per_seed, contrasts,
aa, M, runs, the x416 block), with single values set by hand: the cases test the rule's branches; they are not results and
hold no measured number.

Base case: shaped like the registered read (A/A PF:5,6:7,8; 6 arms x 25 runs with the registered run-id patterns, seeds 5
to 9, cv5v3_f<k> sets; the seven contrasts); (a), (b), (c) all pass headline and guards. M(relF1@2) 0.010 on 532 cells,
0.012 on 416 cells; M(inactive) 0.05; M(mIoU-R13) 0.010. Widths 1.0 and false crack px 400 for every arm, so a guard of
one contrast is moved by changing its reference arm (e.g. CS for (b)) without touching the other contrasts.

Usage: python -B final_verdict_test.py <new work dir>     (CPU, a few seconds; writes only into the work dir)
"""
from __future__ import annotations

import copy
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PY = "/home/noob/work/el-fault-detection/.venv/bin/python"
ARMS = ("PF", "PF_D4", "CS", "CS_D4", "CB", "CB_D4")
RID = {"PF": "c3_pf_v11_f{k}_s{s}", "PF_D4": "c3_pf_v11_f{k}_s{s}.tta_d4", "CS": "c3x_hrnet_swad_v11_f{k}_s{s}.swad",
       "CS_D4": "c3x_hrnet_swad_v11_f{k}_s{s}.swad.tta_d4", "CB": "c3x_hrnet_swad_v11_f{k}_s{s}",
       "CB_D4": "c3x_hrnet_swad_v11_f{k}_s{s}.swad_bn.tta_d4"}
PAIRS = [("PF", "PF_D4"), ("CS", "CS_D4"), ("PF", "CS_D4"), ("CB", "CB_D4"), ("PF", "CB_D4"), ("PF", "CS"), ("PF_D4", "CS_D4")]
OPS = ("OP-A", "OP-F", "OP-W")
SRC = {"532": {"ARTS": 182, "BMRK": 50, "CFVS": 169, "CSIR": 114, "SDLE": 17}, "416": {"ARTS": 131, "BMRK": 50, "CFVS": 132, "CSIR": 103}}
X = "x416"
MECH = "MECHANICS TEST, NOT A VERDICT"


def m(delta, lo, hi=None, se=0.004):
    return {"delta": delta, "lo": lo, "hi": hi if hi is not None else delta + (delta - lo), "se": se}


def block(n_stems, srcs, Mr):
    g = lambda n: {"n": n, "width_ratio": {"mean": 1.0, "sd": 0.01, "n": 25}, "fa_px": {"mean": 400.0, "sd": 1, "n": 25},  # noqa: E731
                   "fa_share50": {"mean": 0.01, "sd": 0, "n": 25}, "relF1_2": {"mean": 0.85, "sd": 0, "n": 25},
                   "crack_iou": {"mean": 0.37, "sd": 0, "n": 25}, "inact_iou": {"mean": 0.50, "sd": 0, "n": 25},
                   "miou_rob": {"mean": 0.61, "sd": 0, "n": 25}}
    summ = {a: {op: {"all": g(n_stems), **{f"src:{s}": g(n) for s, n in srcs.items()}, "type:mono": g(300)} for op in OPS} for a in ARMS}
    ps = {a: {op: {"all": {str(s): {"relF1_2": 0.85, "crack_iou": 0.37, "miou_rob": 0.61} for s in range(5, 10)}} for op in OPS} for a in ARMS}
    keys = ("relF1_2", "crack_iou", "inact_iou", "miou_rob")
    con = {f"{b} - {a}": {op: {"metrics": {"relF1_2": m(0.020, 0.008), "crack_iou": m(0.0, -0.01), "inact_iou": m(0.0, -0.03),
                                           "miou_rob": m(0.0, -0.005)}} for op in OPS} for a, b in PAIRS}
    aa = {op: {"metrics": {k: m(0.001, -0.007, se=0.004) for k in keys}} for op in OPS}
    return {"n_stems": n_stems, "aa_spec": "PF:5,6:7,8", "summary": summ, "per_seed": ps, "contrasts": con, "aa": aa,
            "M": {"relF1_2": Mr, "crack_iou": 0.010, "inact_iou": 0.05, "miou_rob": 0.010}, "groups_md5": "d880a769" + "0" * 24}


def base_doc():
    doc = block(532, SRC["532"], 0.010)
    doc.update(tool="bench_read_w1.py", tool_md5="fdb56b78" + "0" * 24, labels="v11",
               runs=[{"arm": a, "seed": s, "run_id": RID[a].format(k=k, s=s), "set": f"cv5v3_f{k}", "fold": k}
                     for a in ARMS for s in range(5, 10) for k in range(5)])
    doc[X] = block(416, SRC["416"], 0.012)
    return doc


SETS = {"532": lambda d: d, "416": lambda d: d[X]}


def con(doc, name, op, k, key="relF1_2", **kw):
    SETS[k](doc)["contrasts"][name][op]["metrics"][key].update(kw)


def summ(doc, arm, op, sn, k, key, value):
    SETS[k](doc)["summary"][arm][op][sn][key]["mean"] = value


def run(wd: Path, name: str, doc: dict, extra=(), pre_out=False):
    rd = wd / name
    (rd / "read").mkdir(parents=True)
    (rd / "read" / "read.json").write_text(json.dumps(doc))
    out = rd / "verdict.txt"
    if pre_out:
        out.write_text("old\n")
    cmd = [PY, "-B", str(HERE / "final_verdict.py"), "--read", str(rd), "--out", str(out), *extra]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r, (out.read_text() if out.exists() and not pre_out else "")


def section(t, head):
    if head not in t:
        return ""
    i = t.index(head)
    return t[i:].split("\n## ")[0]


RESULTS = []


def check(name, ok, info=""):
    RESULTS.append((name, ok))
    print(f"{'PASS' if ok else 'FAIL'}\t{name}\t{info if not ok else ''}")


def main() -> int:
    wd = Path(sys.argv[1])
    if wd.exists():
        sys.exit(f"refuse: {wd} exists")
    wd.mkdir(parents=True)
    SA = lambda t: section(t, "## (a)")                   # noqa: E731
    SBb = lambda t: section(t, "## (b)")                  # noqa: E731
    SC = lambda t: section(t, "## (c)")                   # noqa: E731
    DEC = lambda t: section(t, "## decisions")            # noqa: E731
    D_A = lambda t: next((l for l in DEC(t).splitlines() if l.startswith("(a) ") or l.startswith(f"[{MECH}] (a) ")), "")  # noqa: E731
    D_B = lambda t: next((l for l in DEC(t).splitlines() if l.startswith("(b) ") or l.startswith(f"[{MECH}] (b) ")), "")  # noqa: E731
    D_C = lambda t: next((l for l in DEC(t).splitlines() if l.startswith("(c) ") or l.startswith(f"[{MECH}] (c) ")), "")  # noqa: E731

    # ---- base: everything passes
    INFO = lambda t: section(t, "## CS - PF with the (c) criteria")   # noqa: E731
    r, t = run(wd, "A_all_pass", base_doc())
    check("A1 all pass: (a), (b), (c) CONFIRMED", r.returncode == 0 and "=> (a) PF_D4 - PF: CONFIRMED; failing guard items 0" in SA(t)
          and "=> (b) CS_D4 - CS: CONFIRMED" in SBb(t) and "=> (c) CS_D4 - PF: CONFIRMED; failing guard items 0 (selection-biased)" in SC(t), r.stderr[-400:])
    check("A2 decisions: replicated (C1 also with D4), D4 supported, C2 passes its CV5 check; no CS - PF information section",
          "B5 TTA RESULT REPLICATED ON CV5V3 / CV02" in D_A(t) and "C1 (PF) is also shown with D4 in the opening (descriptive)" in D_A(t)
          and "D4 IN C2 / C3 SUPPORTED ON CV5: (b) CS_D4 - CS is CONFIRMED." in D_B(t)
          and "C2 PASSES ITS CV5 CHECK (selection-biased; the E1 opening is the test): (c) CS_D4 - PF passes the headline and no false-alarm, inactive or mIoU item fails." in D_C(t)
          and INFO(t) == "" and "FLAG" not in DEC(t) and MECH not in t and "approved E1 candidates" in DEC(t))
    check("A3 every line of the (c) section carries 'selection-biased'",
          all("selection-biased" in l for l in SC(t).splitlines()[1:] if l.strip()) and SC(t).count("\n") > 20)
    check("A4 (b) has false_alarm against CS and false_alarm_pf against PF; (a), (c) no false_alarm_pf",
          SBb(t).count("PASS\tfalse_alarm\t") == 4 and SBb(t).count("PASS\tfalse_alarm_pf\t") == 4
          and "false_alarm_pf" not in SA(t) + SC(t) and "CS_D4 400 against PF 400" in SBb(t))
    check("A5 per-source width judged only for sources with >= 40 cells (SDLE 17 not judged; type:mono not judged)",
          "src:SDLE" not in SA(t) and "type:mono" not in SA(t) and SA(t).count("width_source\t532 cells\tOP-A") == 4
          and SA(t).count("width_source\t416 clean cells\tOP-W") == 4)
    check("A6 rule md5 and sections printed", "rule: harness/final/FINAL_RULE.md (" in t and "## beside the verdict: strict crack IoU" in t
          and "## beside the verdict: descriptive contrasts" in t and "## beside the verdict: levels" in t
          and t.count("descriptive\t") == 16 and t.count("descriptive\tCS - PF\t") == 4 and t.count("A/A\t") == 2)
    check("A7 swad vs swad_bn not re-decided", "swad vs swad_bn: not re-decided" in DEC(t))
    check("A8 section 7 wording: (b) interval line; rule sections", "interval of (b): the read tool's unpaired-seed bootstrap (conservative; FINAL_RULE section 7 item 1)" in SBb(t)
          and "sections 2 to 4 and 7" in t)

    # ---- (a): replication; C1 shown with D4 iff CONFIRMED
    d = base_doc(); con(d, "PF_D4 - PF", "OP-W", "416", delta=0.0119, lo=0.001)
    r, t = run(wd, "a1_not_conf_noloss", d)
    check("a1 (a) delta < M at 416 OP-W -> NOT CONFIRMED, NO LOSS; not replicated; C1 not shown with D4; (b), (c) unaffected",
          "=> (a) PF_D4 - PF: NOT CONFIRMED, NO LOSS" in SA(t) and "B5 TTA RESULT NOT REPLICATED" in D_A(t)
          and "(failing: headline)" in D_A(t) and "C1 (PF) is not shown with D4 in the opening" in D_A(t)
          and "D4 IN C2 / C3 SUPPORTED ON CV5" in D_B(t) and "C2 PASSES ITS CV5 CHECK" in D_C(t))
    d = base_doc(); con(d, "PF_D4 - PF", "OP-A", "532", delta=-0.004, lo=-0.012)
    r, t = run(wd, "a2_loss", d)
    check("a2 (a) CI low < -M -> NOT CONFIRMED, LOSS", "=> (a) PF_D4 - PF: NOT CONFIRMED, LOSS" in SA(t) and "NOT REPLICATED" in D_A(t))
    d = base_doc(); summ(d, "PF_D4", "OP-A", "src:ARTS", "532", "width_ratio", 0.80)
    r, t = run(wd, "a3_gain_width", d)
    check("a3 (a) GAIN with ARTS width failing -> not replicated, failing part named",
          "=> (a) PF_D4 - PF: GAIN, FAILING GUARDS NAMED; failing guard items 1: width_source src:ARTS OP-A 532 cells" in SA(t)
          and "NOT REPLICATED" in D_A(t) and "width_source src:ARTS OP-A 532 cells" in D_A(t))
    d = base_doc(); con(d, "PF_D4 - PF", "OP-A", "532", delta=0.010, lo=0.0001)
    r, t = run(wd, "a4_edge", d)
    check("a4 headline delta = M exactly, CI low > 0 -> passes (inclusive)", "=> (a) PF_D4 - PF: CONFIRMED" in SA(t))
    d = base_doc(); con(d, "PF_D4 - PF", "OP-A", "532", delta=0.02, lo=0.0)
    r, t = run(wd, "a5_lo_zero", d)
    check("a5 headline CI low = 0 -> fails (strict)", "=> (a) PF_D4 - PF: NOT CONFIRMED, NO LOSS" in SA(t))

    # ---- (b): D4 supported (rows 1, 2) or FLAG D4 (rows 3, 4); never dropped
    def flagged(t):   # FLAG D4 shape: the CS - PF information section exists, is not a gate, (c) stays CS_D4 - PF
        I = INFO(t)
        return (I != "" and all("selection-biased" in l for l in I.splitlines()[1:] if l.strip()) and "not a gate" in I
                and "the lead takes it to the user before the E1 opening is frozen (keep C2 / C3 with D4 as approved, or replace D4 by plain inference)" in D_B(t)
                and t.index("## (c) ") < t.index("## CS - PF with the (c) criteria") < t.index("## decisions")
                and "(c) CS_D4 - PF" in D_C(t) and "D4 IS DROPPED" not in t and "gate is CS - PF" not in t)
    d = base_doc(); summ(d, "CS", "OP-W", "src:CSIR", "416", "width_ratio", 1 / 0.80)
    r, t = run(wd, "b1_width_source_only", d)
    check("b1 (b) GAIN, only a per-source width fails -> D4 supported, item named, re-read on E1; no information section",
          "=> (b) CS_D4 - CS: GAIN, FAILING GUARDS NAMED; failing guard items 1: width_source src:CSIR OP-W 416 clean cells" in SBb(t)
          and "D4 IN C2 / C3 SUPPORTED ON CV5: (b) passes the headline and only width items fail (width_source src:CSIR OP-W 416 clean cells); these items are handed to the opening rule to be re-read on E1" in D_B(t)
          and INFO(t) == "" and "C2 PASSES ITS CV5 CHECK" in D_C(t))
    d = base_doc(); summ(d, "CS", "OP-A", "all", "532", "width_ratio", 1 / 1.16)
    r, t = run(wd, "b2_width_pooled_only", d)
    check("b2 (b) GAIN, pooled width fails only -> D4 supported", "width_pooled all OP-A 532 cells" in D_B(t) and "D4 IN C2 / C3 SUPPORTED ON CV5" in D_B(t))
    d = base_doc(); summ(d, "CS_D4", "OP-A", "all", "532", "width_ratio", 1.15)
    r, t = run(wd, "b2e_width_edge", d)
    check("b2e width ratio exactly 1.15 passes (inclusive band; (b) and (c))", "=> (b) CS_D4 - CS: CONFIRMED" in SBb(t) and "=> (c) CS_D4 - PF: CONFIRMED" in SC(t))
    d = base_doc(); summ(d, "CS", "OP-A", "all", "532", "fa_px", 200.0)
    r, t = run(wd, "b3_fa_vs_cs", d)
    check("b3 (b) GAIN, false alarm against CS fails (2.0 x) -> FLAG D4, item named; CS - PF printed as information (meets the criteria); C2 passes",
          "false_alarm OP-A 532 cells" in SBb(t).split("=> (b)")[-1] and "=> (b)" in SBb(t) and "PASS\tfalse_alarm_pf\t532 cells\tOP-A" in SBb(t)
          and "FLAG D4: (b) passes the headline but a false-alarm, inactive or mIoU item fails (false_alarm OP-A 532 cells)" in D_B(t)
          and flagged(t) and "=> CS - PF (information for FLAG D4): GAIN, FAILING GUARDS NAMED" not in t
          and "plain swad meets the (c) criteria (headline passes; no false-alarm, inactive or mIoU item fails)" in INFO(t)
          and "C2 PASSES ITS CV5 CHECK" in D_C(t))
    d = base_doc(); summ(d, "CS", "OP-A", "all", "532", "fa_px", 266.0)
    r, t = run(wd, "b3e_fa_edge", d)
    check("b3e false alarm 400 > 1.5 x 266 = 399 -> FAIL", "FAIL\tfalse_alarm\t532 cells\tOP-A" in SBb(t))
    d = base_doc(); summ(d, "CS_D4", "OP-A", "all", "532", "fa_px", 600.0)
    r, t = run(wd, "b3f_fa_exact", d)
    check("b3f false alarm exactly 1.5 x passes (inclusive; against CS, PF, and in (c))", "PASS\tfalse_alarm\t532 cells\tOP-A" in SBb(t)
          and "PASS\tfalse_alarm_pf\t532 cells\tOP-A" in SBb(t) and "=> (c) CS_D4 - PF: CONFIRMED" in SC(t))
    d = base_doc()
    for k in ("532", "416"):
        for op in ("OP-A", "OP-W"):
            summ(d, "CS", op, "all", k, "fa_px", 1000.0); summ(d, "CS_D4", op, "all", k, "fa_px", 700.0)
    r, t = run(wd, "b4_fa_vs_pf_only", d)
    check("b4 (b) false alarm against CS passes (0.7 x) but false_alarm_pf fails (1.75 x) -> FLAG D4; (c) fails its false-alarm guard -> FLAG C2; CS - PF (2.5 x) does not meet the criteria",
          "PASS\tfalse_alarm\t532 cells\tOP-A" in SBb(t) and "FAIL\tfalse_alarm_pf\t532 cells\tOP-A" in SBb(t)
          and "FLAG D4" in D_B(t) and "false_alarm_pf OP-A 532 cells" in D_B(t) and flagged(t)
          and "FLAG C2: a false-alarm, inactive or mIoU item of (c) CS_D4 - PF fails (false_alarm OP-A 532 cells" in D_C(t)
          and "plain swad does not meet the (c) criteria (failing: false_alarm OP-A 532 cells" in INFO(t))
    d = base_doc(); con(d, "CS_D4 - CS", "OP-A", "416", key="inact_iou", delta=-0.06, lo=-0.12)
    r, t = run(wd, "b5_inactive", d)
    check("b5 (b) inactive delta < -M -> FLAG D4", "inactive OP-A 416 clean cells" in D_B(t) and D_B(t).startswith("(b) FLAG D4") and flagged(t))
    d = base_doc(); con(d, "CS_D4 - CS", "OP-W", "532", key="miou_rob", delta=-0.011, lo=-0.02)
    r, t = run(wd, "b6_miou", d)
    check("b6 (b) mIoU delta < -M -> FLAG D4", "miou OP-W 532 cells" in D_B(t) and D_B(t).startswith("(b) FLAG D4") and flagged(t))
    d = base_doc(); con(d, "CS_D4 - CS", "OP-A", "416", key="miou_rob", delta=-0.010, lo=-0.02)
    r, t = run(wd, "b6e_miou_edge", d)
    check("b6e mIoU delta = -M exactly passes (inclusive)", "=> (b) CS_D4 - CS: CONFIRMED" in SBb(t) and "D4 IN C2 / C3 SUPPORTED" in D_B(t))
    d = base_doc(); summ(d, "CS", "OP-A", "src:ARTS", "532", "width_ratio", 1 / 0.8); con(d, "CS_D4 - CS", "OP-A", "532", key="inact_iou", delta=-0.06, lo=-0.1)
    r, t = run(wd, "b7_width_and_inactive", d)
    check("b7 (b) width and inactive fail -> FLAG D4, both named", D_B(t).startswith("(b) FLAG D4") and "inactive OP-A 532 cells" in D_B(t)
          and "width items also failing: width_source src:ARTS OP-A 532 cells" in D_B(t))
    d = base_doc(); con(d, "CS_D4 - CS", "OP-A", "532", delta=0.004, lo=-0.003)
    r, t = run(wd, "b8_not_conf_noloss", d)
    check("b8 (b) NOT CONFIRMED, NO LOSS -> FLAG D4 (8x cost); C2 check still on (c) CS_D4 - PF",
          "=> (b) CS_D4 - CS: NOT CONFIRMED, NO LOSS" in SBb(t)
          and "FLAG D4: (b) is NOT CONFIRMED, NO LOSS: D4 costs 8x inference without a confirmed CV5 gain on the candidate" in D_B(t)
          and flagged(t) and "C2 PASSES ITS CV5 CHECK" in D_C(t))
    d = base_doc(); con(d, "CS_D4 - CS", "OP-W", "416", delta=-0.02, lo=-0.03)
    r, t = run(wd, "b9_loss", d)
    check("b9 (b) NOT CONFIRMED, LOSS -> FLAG D4", "=> (b) CS_D4 - CS: NOT CONFIRMED, LOSS" in SBb(t) and "FLAG D4: (b) is NOT CONFIRMED, LOSS" in D_B(t) and flagged(t))

    # ---- (c): always CS_D4 - PF; C2 passes its CV5 check (row 5) or FLAG C2 (row 6)
    d = base_doc(); summ(d, "PF", "OP-A", "src:ARTS", "416", "width_ratio", 1 / 1.20); summ(d, "PF", "OP-W", "src:ARTS", "416", "width_ratio", 1 / 1.20)
    r, t = run(wd, "c1_width_only", d)
    check("c1 (c) GAIN with ARTS width (416) failing -> C2 passes its CV5 check, width items named",
          "=> (c) CS_D4 - PF: GAIN, FAILING GUARDS NAMED; failing guard items 2" in SC(t)
          and "C2 PASSES ITS CV5 CHECK (selection-biased; the E1 opening is the test): (c) CS_D4 - PF passes the headline and no false-alarm, inactive or mIoU item fails; width items named: width_source src:ARTS OP-A 416 clean cells; width_source src:ARTS OP-W 416 clean cells." in D_C(t)
          and "NOT REPLICATED" in D_A(t))
    d = base_doc(); con(d, "CS_D4 - PF", "OP-A", "416", delta=0.008, lo=0.001)
    r, t = run(wd, "c2_headline_fail", d)
    check("c2 (c) headline fails -> FLAG C2",
          "=> (c) CS_D4 - PF: NOT CONFIRMED, NO LOSS" in SC(t)
          and "FLAG C2: (c) CS_D4 - PF does not pass the headline (selection-biased); the lead looks (and tells the user) before the E1 opening is frozen" in D_C(t)
          and "D4 IN C2 / C3 SUPPORTED" in D_B(t) and INFO(t) == "")
    d = base_doc(); con(d, "CS_D4 - PF", "OP-W", "532", key="inact_iou", delta=-0.051, lo=-0.1)
    r, t = run(wd, "c3_inactive", d)
    check("c3 (c) inactive fails -> FLAG C2", D_C(t).startswith("(c) FLAG C2") and "inactive OP-W 532 cells" in D_C(t))
    d = base_doc(); con(d, "CS_D4 - PF", "OP-A", "532", key="miou_rob", delta=-0.02, lo=-0.03)
    r, t = run(wd, "c4_miou", d)
    check("c4 (c) mIoU fails -> FLAG C2", D_C(t).startswith("(c) FLAG C2") and "miou OP-A 532 cells" in D_C(t))
    d = base_doc(); summ(d, "PF", "OP-W", "all", "416", "fa_px", 100.0)
    r, t = run(wd, "c5_fa", d)
    check("c5 (c) false alarm 4 x PF -> FLAG C2; (a) not replicated; false_alarm_pf of (b) -> FLAG D4", D_C(t).startswith("(c) FLAG C2")
          and "false_alarm OP-W 416 clean cells" in D_C(t) and "NOT REPLICATED" in D_A(t) and D_B(t).startswith("(b) FLAG D4"))
    d = base_doc(); con(d, "CS_D4 - PF", "OP-A", "532", delta=0.004, lo=-0.002); con(d, "CS_D4 - CS", "OP-A", "532", delta=0.004, lo=-0.003)
    r, t = run(wd, "c6_flag_both_cs_pf_passes", d)
    check("c6 FLAG D4 and FLAG C2 together; CS - PF meets the criteria but replaces nothing (C2 still flagged on (c))",
          D_B(t).startswith("(b) FLAG D4") and D_C(t).startswith("(c) FLAG C2: (c) CS_D4 - PF does not pass the headline") and flagged(t)
          and "plain swad meets the (c) criteria" in INFO(t))

    # ---- FLAG D4: CS - PF printed with the (c) criteria as information (guards against PF; selection-biased; never a gate)
    def flagd4(d):   # (b) NOT CONFIRMED, NO LOSS at 532 OP-A: FLAG D4; nothing else of (b), (c) changed
        con(d, "CS_D4 - CS", "OP-A", "532", delta=0.004, lo=-0.003)
        return d
    d = flagd4(base_doc())
    r, t = run(wd, "f1_flag_info_pass", d)
    I1 = INFO(t)
    check("f1 FLAG D4, CS - PF passes headline and guards -> information line, all lines selection-biased; guards against PF, no false_alarm_pf",
          r.returncode == 0 and "=> CS - PF (information for FLAG D4): CONFIRMED; failing guard items 0; plain swad meets the (c) criteria (headline passes; no false-alarm, inactive or mIoU item fails) (selection-biased; not a gate)" in I1
          and I1.count("\n") > 20 and "false crack px on crack-free cells CS 400 against PF 400" in I1 and "false_alarm_pf" not in I1
          and "(c')" not in t and "C2 PASSES ITS CV5 CHECK" in D_C(t), r.stderr[-300:])
    check("f1b FLAG D4: CS - PF stays in the descriptive section; its strict IoU and per-seed lines marked as information",
          t.count("descriptive\tCS - PF\t") == 4 and t.count("descriptive\tCS_D4 - PF\t") == 0
          and sum(1 for l in t.splitlines() if l.startswith("strict crack IoU\tCS - PF\t") and "\t(selection-biased)\t(information for FLAG D4)" in l) == 4
          and sum(1 for l in t.splitlines() if l.startswith("per_seed\t") and "\tCS - PF\t" in l and "information for FLAG D4" in l) == 12)
    d = flagd4(base_doc()); con(d, "CS - PF", "OP-W", "416", delta=0.0119, lo=0.002)
    r, t = run(wd, "f2_flag_info_headline", d)
    check("f2 FLAG D4, CS - PF delta < M at 416 OP-W -> 'does not meet the (c) criteria (headline fails)'; C2 check unchanged",
          "=> CS - PF (information for FLAG D4): NOT CONFIRMED, NO LOSS" in INFO(t) and "plain swad does not meet the (c) criteria (headline fails)" in INFO(t)
          and "C2 PASSES ITS CV5 CHECK" in D_C(t))
    d = flagd4(base_doc()); summ(d, "CS", "OP-A", "all", "416", "fa_px", 700.0)
    r, t = run(wd, "f3_flag_info_fa", d)
    check("f3 FLAG D4, CS - PF false alarm 1.75 x PF -> item named in the information line; C2 check unchanged",
          "plain swad does not meet the (c) criteria (failing: false_alarm OP-A 416 clean cells)" in INFO(t) and "C2 PASSES ITS CV5 CHECK" in D_C(t))
    d = flagd4(base_doc()); con(d, "CS - PF", "OP-A", "532", key="inact_iou", delta=-0.051, lo=-0.1)
    r, t = run(wd, "f4_flag_info_inactive", d)
    check("f4 FLAG D4, CS - PF inactive < -M -> named", "(failing: inactive OP-A 532 cells)" in INFO(t))
    d = flagd4(base_doc()); con(d, "CS - PF", "OP-W", "416", key="miou_rob", delta=-0.011, lo=-0.02)
    r, t = run(wd, "f5_flag_info_miou", d)
    check("f5 FLAG D4, CS - PF mIoU < -M -> named", "(failing: miou OP-W 416 clean cells)" in INFO(t))
    d = flagd4(base_doc()); summ(d, "CS", "OP-A", "src:ARTS", "416", "width_ratio", 1.20); summ(d, "CS", "OP-W", "src:ARTS", "416", "width_ratio", 1.20)
    r, t = run(wd, "f6_flag_info_width", d)
    check("f6 FLAG D4, CS - PF only ARTS width (416) fails -> meets the criteria, width items named",
          "=> CS - PF (information for FLAG D4): GAIN, FAILING GUARDS NAMED; failing guard items 2" in INFO(t)
          and "plain swad meets the (c) criteria (headline passes; no false-alarm, inactive or mIoU item fails; width items: width_source src:ARTS OP-A 416 clean cells; width_source src:ARTS OP-W 416 clean cells)" in INFO(t))
    d = flagd4(base_doc()); con(d, "CS - PF", "OP-W", "532", key="relF1_2", delta=-0.02, lo=-0.03)
    r, t = run(wd, "f7_flag_info_loss", d)
    check("f7 FLAG D4, CS - PF LOSS -> information only, C2 check unchanged", "=> CS - PF (information for FLAG D4): NOT CONFIRMED, LOSS" in INFO(t)
          and "C2 PASSES ITS CV5 CHECK" in D_C(t))
    d = flagd4(base_doc()); con(d, "CS - PF", "OP-A", "416", key="inact_iou", delta=None)
    r, t = run(wd, "f8_flag_info_null", d)
    check("f8 FLAG D4, a null in CS - PF is refused, nothing written",
          r.returncode != 0 and "contrast CS - PF, OP-A, inact_iou: delta is None in the 416 clean cells block" in r.stderr and not (wd / "f8_flag_info_null" / "verdict.txt").exists())
    # ---- D4 supported: CS - PF is descriptive only, never read with the criteria
    d = base_doc(); con(d, "CS - PF", "OP-A", "532", delta=-0.02, lo=-0.03); summ(d, "CS", "OP-A", "all", "532", "fa_px", 900.0)
    r, t = run(wd, "k1_supported_cs_pf_bad", d)
    check("k1 D4 supported, CS - PF LOSS and 2.25 x false alarm -> no information section, nothing flagged; CS - PF descriptive",
          "D4 IN C2 / C3 SUPPORTED ON CV5" in D_B(t) and "C2 PASSES ITS CV5 CHECK" in D_C(t) and INFO(t) == ""
          and "FLAG" not in DEC(t) and t.count("descriptive\tCS - PF\t") == 4 and "information for FLAG D4" not in t)
    d = base_doc(); con(d, "CS - PF", "OP-W", "416", key="miou_rob", delta=None, lo=None, hi=None)
    r, t = run(wd, "k2_supported_cs_pf_null", d)
    check("k2 D4 supported, a null in CS - PF is not read by the rule: no refusal, printed n/a", r.returncode == 0 and "miou_rob n/a" in t
          and "C2 PASSES ITS CV5 CHECK" in D_C(t), r.stderr[-300:])

    # ---- beside: strict crack IoU convention band, descriptive n/a
    d = base_doc(); con(d, "PF_D4 - PF", "OP-A", "532", key="crack_iou", delta=0.019, lo=0.01, hi=0.03)
    con(d, "CS_D4 - CS", "OP-A", "532", key="crack_iou", delta=0.027, lo=0.02, hi=0.034)
    con(d, "CB_D4 - CB", "OP-W", "416", key="crack_iou", delta=None, lo=None, hi=None)
    con(d, "CB_D4 - PF", "OP-W", "416", delta=float("nan"))
    r, t = run(wd, "s1_band", d)
    ST = section(t, "## beside the verdict: strict crack IoU")
    check("s1 strict IoU 0.019 inside, 0.027 outside the band; null strict IoU and NaN descriptive relF1 print n/a, no refusal",
          r.returncode == 0 and "PF_D4 - PF\t532 cells\tOP-A\t+0.0190 [+0.0100, +0.0300]\tconvention band +-0.019: inside the convention band\n" in ST
          and "CS_D4 - CS\t532 cells\tOP-A\t+0.0270 [+0.0200, +0.0340]\tconvention band +-0.019: outside the band (decides nothing)\t(read on the cells that selected the readout; FINAL_RULE section 0)\n" in ST
          and "CB_D4 - CB\t416 clean cells\tOP-W\tn/a [n/a, n/a]\tconvention band +-0.019: n/a\n" in ST
          and "re-scored on the 1-px centreline, the v1.1 and the 3-px labels, dataset_audit/REPORT.md F1" in ST
          and "descriptive\tCB_D4 - PF\t416 clean cells\tOP-W\trelF1_2 n/a" in t and ST.count("decides nothing") == 2
          and sum(1 for l in ST.splitlines() if l.startswith("strict crack IoU\t")) == 28, r.stderr[-300:])
    check("s2 strict IoU lines of (c) carry selection-biased", all("selection-biased" in l for l in ST.splitlines() if "\tCS_D4 - PF\t" in l)
          and sum(1 for l in ST.splitlines() if "\tCS_D4 - PF\t" in l) == 4)
    d = base_doc(); d["per_seed"]["CS_D4"]["OP-A"]["all"]["7"]["relF1_2"] = 0.87
    r, t = run(wd, "s3_per_seed", d)
    PS = section(t, "## beside the verdict: per-seed")
    check("s3 per-seed lines X - R per seed; (c) lines selection-biased", "per_seed\t532 cells\tOP-A\trelF1_2\tCS_D4 - CS\ts5 +0.0000\ts6 +0.0000\ts7 +0.0200" in PS
          and PS.count("per_seed\t") == 36 and all("selection-biased" in l for l in PS.splitlines() if "CS_D4 - PF" in l))

    # ---- review B3 (fix round 1): every line carrying a CS / CS_D4 number is labelled; every arm-contrast crack_iou line has the band
    arm_rx = re.compile(r"(?<![A-Za-z_])CS(_D4)?(?![A-Za-z_0-9])")
    base_rx = re.compile(r"(?<![A-Za-z_])PF(_D4)?(?![A-Za-z_0-9])")
    RBL = "read on the cells that selected the readout"
    bad_lab, bad_band, n_lab, n_band = [], [], 0, 0
    for nm, doc in (("b3_base", base_doc()), ("b3_flagd4", flagd4(base_doc()))):
        r, tt = run(wd, nm, doc)
        if r.returncode != 0:
            bad_lab.append(f"{nm} rc {r.returncode}")
            continue
        for l in tt.splitlines():
            kind = l.split("\t", 1)[0]
            if kind not in ("PASS", "FAIL", "descriptive", "strict crack IoU", "per_seed", "level") and not l.startswith("=> "):
                continue
            if arm_rx.search(l):
                n_lab += 1
                sel = (kind == "level" and l.split("\t")[3] in ("CS", "CS_D4")) or (arm_rx.search(l) and base_rx.search(l))
                ok = ("selection-biased" in l) if sel else ("selection-biased" in l or RBL in l)
                if not ok:
                    bad_lab.append(f"{nm}: {l[:120]}")
            if kind in ("descriptive", "per_seed", "strict crack IoU") and ("crack_iou" in l or kind == "strict crack IoU"):
                n_band += 1
                if "convention band +-0.019" not in l:
                    bad_band.append(f"{nm}: {l[:120]}")
    check(f"rvB3 every line carrying a CS / CS_D4 number is labelled ({n_lab} lines: 'selection-biased' against PF / PF_D4 and on CS / CS_D4 levels, "
          f"else the (b) label) and every arm-contrast crack_iou line carries the convention band ({n_band} lines)",
          not bad_lab and not bad_band and n_lab > 100 and n_band >= 40, "; ".join((bad_lab + bad_band)[:4]))

    # ---- refusals (nothing written)
    def refused(name, doc, text, extra=(), pre_out=False):
        r, t = run(wd, name, doc, extra, pre_out)
        out = wd / name / "verdict.txt"
        ok = r.returncode != 0 and text in (r.stderr + r.stdout) and (pre_out or not out.exists())
        check(f"R {name}: refused ({text[:60]})", ok, (r.stderr + r.stdout)[-300:])
    d = base_doc(); d["aa_spec"] = "PF:5,6:7,9"; refused("r01_aa_spec", d, "A/A spec of the 532 cells block is 'PF:5,6:7,9'")
    d = base_doc(); del d[X]["contrasts"]["CS_D4 - PF_D4"]; refused("r02_contrast", d, "the 416 clean cells block lacks the contrasts ['CS_D4 - PF_D4']")
    d = base_doc(); d["runs"] = [r_ for r_ in d["runs"] if not (r_["arm"] == "CB_D4" and r_["seed"] == 9 and r_["fold"] == 4)]
    refused("r03_24_runs", d, "arm CB_D4 has 24 runs with 24 different run ids")
    d = base_doc()
    for r_ in d["runs"]:
        if r_["arm"] == "PF_D4" and r_["seed"] == 9:
            r_["seed"] = 4
    refused("r04_seeds", d, "arm PF_D4 has seeds [4, 5, 6, 7, 8]")
    d = base_doc()
    for r_ in d["runs"]:
        if r_["arm"] == "CS" and r_["fold"] == 2:
            r_["set"] = "cv5v2_f2"
    refused("r05_sets", d, "arm CS holds sets that are not cv5v3_f<k>")
    d = base_doc()
    for r_ in d["runs"]:
        if r_["arm"] == "PF_D4":
            r_["run_id"] = r_["run_id"].replace(".tta_d4", ".tta_d4ms")
    refused("r06_run_id_pattern", d, "arm PF_D4 holds run ids that are not")
    d = base_doc(); d["runs"] += [{"arm": "D4MS", "seed": 5, "run_id": "x", "set": "cv5v3_f0", "fold": 0}]
    refused("r07_extra_arm", d, "arms ['D4MS'] are not arms of the registered read")
    d = base_doc(); con(d, "CS_D4 - CS", "OP-W", "416", key="inact_iou", delta=None); refused("r08_null_delta_b", d, "contrast CS_D4 - CS, OP-W, inact_iou: delta is None in the 416 clean cells block")
    d = base_doc(); d["M"]["relF1_2"] = float("nan"); refused("r09_nan_M", d, "the A/A margin M(relF1_2) of the 532 cells block is nan")
    d = base_doc(); con(d, "CS_D4 - PF", "OP-A", "532", lo=float("nan")); refused("r10_nan_lo_c", d, "contrast CS_D4 - PF, OP-A, relF1_2: lo is nan")
    d = base_doc(); con(d, "PF_D4 - PF", "OP-W", "532", key="miou_rob", hi=None); refused("r11_null_hi_a", d, "contrast PF_D4 - PF, OP-W, miou_rob: hi is None")
    d = base_doc(); summ(d, "CS", "OP-W", "src:ARTS", "416", "width_ratio", None); refused("r12_null_width_ref", d, "width ratio undefined for a judged subset (src:ARTS, OP-W, 416 clean cells)")
    d = base_doc(); summ(d, "PF", "OP-A", "all", "532", "fa_px", None); refused("r13_null_fa", d, "false crack px undefined (OP-A, 532 cells)")
    d = base_doc(); del d[X]; refused("r14_no_x_block", d, "expected one kept-cells block in read.json")
    d = base_doc(); d["M"] = None; refused("r15_no_M", d, "no A/A margin in the 532 cells block")
    d = base_doc(); del d[X]["summary"]["CB"]; refused("r16_arm_missing", d, "arm CB missing in the 416 clean cells block")
    refused("r17_out_exists", base_doc(), "exists", pre_out=True)
    d = base_doc(); con(d, "CS_D4 - CS", "OP-A", "532", key="inact_iou", delta=None)
    r, t = run(wd, "r18_null_under_mechanics", d, ["--mechanics"])
    check("R r18_null_under_mechanics: refused under --mechanics too", r.returncode != 0 and "inact_iou: delta is None" in r.stderr)

    # ---- mechanics
    d = base_doc(); d["aa_spec"] = "PLAIN:5,6:7,8"; d[X]["aa_spec"] = "PLAIN:5,6:7,8"
    for r_ in d["runs"]:
        r_["set"] = r_["set"].replace("cv5v3", "cv5v2")
    r, t = run(wd, "m1_mechanics", d, ["--mechanics"])
    vlines = [l for l in t.splitlines() if l.startswith("=> ") or l.startswith("[")]
    check("m1 --mechanics: non-registered read accepted; first line and every verdict/decision line marked",
          r.returncode == 0 and t.startswith(f"# {MECH}") and len(vlines) == 6 and all(MECH in l for l in vlines), r.stderr[-300:])
    r, t = run(wd, "m2_not_mechanics", d)
    check("m2 the same read without --mechanics is refused", r.returncode != 0 and "A/A spec" in r.stderr)
    d = base_doc(); del d["contrasts"]["CS - PF"]
    r, t = run(wd, "m3_mechanics_missing_contrast", d, ["--mechanics"])
    check("m3 --mechanics still refuses a missing contrast", r.returncode != 0 and "lacks the contrasts ['CS - PF']" in r.stderr)

    n = sum(ok for _, ok in RESULTS)
    print(f"\nfinal verdict test: {n} of {len(RESULTS)} PASS")
    return 0 if n == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
