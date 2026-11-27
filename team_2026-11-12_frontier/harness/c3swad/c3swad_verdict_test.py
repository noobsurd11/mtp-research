"""c3swad: mechanics tests of c3swad_verdict.py (the registered rule of LAUNCH_REQUEST_c3swad.md section 7).

Base = the published SCREEN read (cv5v2, 2 seeds; /home/noob/work/bench_reads/w2a/read/read.json, read only; its numbers
are in results/W2A_READ.md). Each case is a copy of that read.json in which single values are changed by hand, so the
cases are SYNTHETIC: they test the rule's branches, they are not results. No cv5v3 number is involved.

Cases (the lead asked for B and C on 17 Nov, 09:35):
  A  screen as it is: swad_bn fails only per-source width (ARTS, OP-A, both cell sets)      -> carried by swad
  B  swad_bn's only failing item is a per-source width at OP-W (ARTS, clean cells)          -> carried by swad
  C  a pooled width of swad_bn fails (beside nothing else)                                  -> not confirmed, guards named, no carry
  D  swad_bn passes everything                                                              -> confirmed (primary)
  E  swad_bn fails the headline: delta below M at one of the four values                    -> not confirmed (no confirmed gain)
  F  swad_bn fails the headline: interval's lower end not above 0                           -> not confirmed (no confirmed gain)
  G  carry possible, but swad fails a guard (false alarms)                                  -> not confirmed, guards named
  H  carry possible, but swad fails the headline                                            -> not confirmed, guards named
  I  swad_bn fails a per-source width AND the inactive guard                                -> not confirmed, guards named, no carry
  J  a source with fewer than 40 cells (SDLE) far outside the band, all else passing        -> confirmed (primary; not judged)
  K  band edge: per-source ratio 1.1499 passes, 1.1501 fails (then carried by swad)
  L  false alarms: 1.49 x passes, 1.51 x fails (swad_bn; not a per-source width, so no carry)
Cases A to L run with --mechanics (the screen read has 2 seeds, cv5v2 sets and another A/A arm); each output must carry
the mark "MECHANICS TEST, NOT A VERDICT" in its first line and in its verdict line.
Review F8 (the check of the read, and undefined values):
  M1 the screen read WITHOUT --mechanics                                                    -> refused (A/A spec)
  M2 a copy shaped like the registered read (A/A spec PF:5,6:7,8; 25 run ids per arm, seeds 5 to 9, cv5v3 sets;
     the numbers are still the screen's), without --mechanics                               -> a verdict, no mark
  M3 M2 with 24 runs in one arm; M4 M2 with seed 9 missing; M5 M2 with one cv5v2 set; M6 M2 with another A/A spec in
     the clean-cells block                                                                  -> refused, each with its reason
  N1 a judged width is null; N2 the false crack px are null                                 -> refused in plain words, no file

Usage: python -B c3swad_verdict_test.py <new work dir>     (CPU, a few seconds; writes only into the work dir)
"""
from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE_READ = Path("/home/noob/work/bench_reads/w2a/read/read.json")
PY = "/home/noob/work/el-fault-detection/.venv/bin/python"
X = "x416"
SETS = {"532": lambda d: d, "416": lambda d: d[X]}


def width(doc, arm, op, sn, ratio, sets=("532", "416")):
    """set arm's width ratio on subset sn to ratio x PF's"""
    for k in sets:
        D = SETS[k](doc)
        D["summary"][arm][op][sn]["width_ratio"]["mean"] = ratio * D["summary"]["PF"][op][sn]["width_ratio"]["mean"]


def arts_ok(doc):
    """bring swad_bn's ARTS width at OP-A inside the band on both cell sets (the screen has 1.203 and 1.218 there)"""
    width(doc, "SWADBN", "OP-A", "src:ARTS", 1.10)


def metric(doc, arm, op, key, k, **kw):
    SETS[k](doc)["contrasts"][f"{arm} - PF"][op]["metrics"][key].update(kw)


def fa(doc, arm, op, k, factor):
    D = SETS[k](doc)
    D["summary"][arm][op]["all"]["fa_px"]["mean"] = factor * D["summary"]["PF"][op]["all"]["fa_px"]["mean"]


def cases(base):
    def c():
        return copy.deepcopy(base)
    out = []
    out.append(("A screen as it is", c(), "CONFIRMED, CARRIED BY THE DECLARED SECONDARY READOUT swad", ["width_source src:ARTS OP-A"]))
    d = c(); arts_ok(d); width(d, "SWADBN", "OP-W", "src:ARTS", 1.16, sets=("416",))
    out.append(("B only failing item: per-source width at OP-W (ARTS, clean cells)", d,
                "CONFIRMED, CARRIED BY THE DECLARED SECONDARY READOUT swad", ["width_source src:ARTS OP-W 416 clean cells"]))
    d = c(); arts_ok(d); width(d, "SWADBN", "OP-A", "all", 1.20, sets=("532",))
    out.append(("C pooled width fails", d, "NOT CONFIRMED, reported as a gain with the failing guards named",
                ["width_pooled all OP-A 532 cells", "No carry by swad: a failing guard item of swad_bn is not a per-source width"]))
    d = c(); arts_ok(d)
    out.append(("D everything passes", d, "CONFIRMED: the primary readout swad_bn", []))
    d = c(); metric(d, "SWADBN", "OP-W", "relF1_2", "416", delta=0.005)
    out.append(("E headline: delta below M (OP-W, clean cells)", d, "NOT CONFIRMED (no confirmed gain)", []))
    d = c(); arts_ok(d); metric(d, "SWADBN", "OP-A", "relF1_2", "532", lo=-0.0001)
    out.append(("F headline: lower end not above 0 (OP-A, 532 cells)", d, "NOT CONFIRMED (no confirmed gain)", []))
    d = c(); fa(d, "SWAD", "OP-W", "532", 1.6)
    out.append(("G carry possible, swad fails the false-alarm guard", d, "NOT CONFIRMED, reported as a gain with the failing guards named",
                ["No carry by swad: swad does not pass every guard (false_alarm OP-W 532 cells)"]))
    d = c(); metric(d, "SWAD", "OP-A", "relF1_2", "416", delta=0.009)
    out.append(("H carry possible, swad fails the headline", d, "NOT CONFIRMED, reported as a gain with the failing guards named",
                ["No carry by swad: swad does not pass the headline"]))
    d = c(); metric(d, "SWADBN", "OP-A", "inact_iou", "532", delta=-(base["M"]["inact_iou"] + 0.01))
    out.append(("I per-source width and inactive IoU fail", d, "NOT CONFIRMED, reported as a gain with the failing guards named",
                ["inactive OP-A 532 cells", "width_source src:ARTS OP-A", "not a per-source width"]))
    d = c(); arts_ok(d); width(d, "SWADBN", "OP-A", "src:SDLE", 3.0, sets=("532",))
    out.append(("J source below 40 cells outside the band", d, "CONFIRMED: the primary readout swad_bn", []))
    d = c(); arts_ok(d); width(d, "SWADBN", "OP-W", "src:CFVS", 1.1499)
    out.append(("K1 per-source ratio 1.1499", d, "CONFIRMED: the primary readout swad_bn", []))
    d = c(); arts_ok(d); width(d, "SWADBN", "OP-W", "src:CFVS", 1.1501)
    out.append(("K2 per-source ratio 1.1501", d, "CONFIRMED, CARRIED BY THE DECLARED SECONDARY READOUT swad", ["width_source src:CFVS OP-W"]))
    d = c(); arts_ok(d); width(d, "SWADBN", "OP-A", "src:BMRK", 0.8499)
    out.append(("K3 per-source ratio 0.8499 (too thin)", d, "CONFIRMED, CARRIED BY THE DECLARED SECONDARY READOUT swad", ["width_source src:BMRK OP-A"]))
    d = c(); arts_ok(d); fa(d, "SWADBN", "OP-A", "532", 1.49)
    out.append(("L1 false alarms 1.49 x", d, "CONFIRMED: the primary readout swad_bn", []))
    d = c(); arts_ok(d); fa(d, "SWADBN", "OP-A", "532", 1.51)
    out.append(("L2 false alarms 1.51 x", d, "NOT CONFIRMED, reported as a gain with the failing guards named",
                ["false_alarm OP-A 532 cells", "not a per-source width"]))
    return out


MARK = "MECHANICS TEST, NOT A VERDICT"


def registered_shape(base):
    """a copy with the SHAPE of the registered read: A/A spec, 25 run ids per arm, seeds 5 to 9, cv5v3 sets (numbers unchanged)"""
    d = copy.deepcopy(base)
    d["aa_spec"] = d[X]["aa_spec"] = "PF:5,6:7,8"
    names = {"PF": "c3_pf_v11_f{k}_s{s}", "SWADBN": "c3s_swad_v11_f{k}_s{s}", "SWAD": "c3s_swad_v11_f{k}_s{s}.swad"}
    d["runs"] = [{"arm": arm, "seed": s, "run_id": pat.format(k=k, s=s), "set": f"cv5v3_f{k}", "fold": k}
                 for arm, pat in names.items() for s in (5, 6, 7, 8, 9) for k in range(5)]
    return d


def run(work, name, doc, mechanics):
    d = work / name.split()[0]
    (d / "read").mkdir(parents=True)
    (d / "read" / "read.json").write_text(json.dumps(doc))
    r = subprocess.run([PY, "-B", str(HERE / "c3swad_verdict.py"), "--read", str(d), "--out", str(d / "verdict.txt")]
                       + (["--mechanics"] if mechanics else []), capture_output=True, text=True)
    txt = (d / "verdict.txt").read_text() if (d / "verdict.txt").exists() else ""
    return r, txt


def main() -> int:
    work = Path(sys.argv[1])
    if work.exists():
        sys.exit(f"refuse: {work} exists")
    base = json.loads(BASE_READ.read_text())
    assert X in base and {"PF", "SWADBN", "SWAD"} <= set(base["summary"])
    npass = nfail = 0
    for name, doc, want, must in cases(base):
        r, txt = run(work, name, doc, True)
        v = txt.split("## verdict\n", 1)[1].split("\n", 1)[0] if "## verdict\n" in txt else f"(no verdict; rc {r.returncode}: {r.stderr[-200:]})"
        marked = txt.startswith(f"# {MARK}") and v.startswith(f"[{MARK}] ")
        v = v[len(f"[{MARK}] "):] if marked else v
        ok = r.returncode == 0 and marked and v.startswith(want) and all(m in v for m in must)
        npass += ok; nfail += not ok
        print(f"{'PASS' if ok else 'FAIL'} {name}\n     -> {v}")
    # ---- review F8: the check of the read (no --mechanics) and undefined values
    reg = registered_shape(base)
    r24 = copy.deepcopy(reg); r24["runs"] = [x for x in r24["runs"] if x["run_id"] != "c3s_swad_v11_f4_s9.swad"]
    rs9 = copy.deepcopy(reg)
    for x in rs9["runs"]:
        if x["arm"] == "PF" and x["seed"] == 9:
            x["seed"] = 8; x["run_id"] += "_again"
    rv2 = copy.deepcopy(reg); rv2["runs"][30]["set"] = "cv5v2_f0"
    raa = copy.deepcopy(reg); raa[X]["aa_spec"] = "PF:5,6:7,9"
    nw = copy.deepcopy(base); nw["summary"]["SWADBN"]["OP-A"]["src:ARTS"]["width_ratio"]["mean"] = None
    nf = copy.deepcopy(base); nf[X]["summary"]["PF"]["OP-W"]["all"]["fa_px"]["mean"] = None
    extra = [("M1 screen read without --mechanics", base, False, None, "refuse: A/A spec of the 532 cells block is 'PFAA:5,6:7,8'"),
             ("M2 registered shape, no --mechanics", reg, False, "CONFIRMED, CARRIED BY THE DECLARED SECONDARY READOUT swad", None),
             ("M3 24 runs in one arm", r24, False, None, "refuse: arm SWAD has 24 runs with 24 different run ids"),
             ("M4 seed 9 missing in PF", rs9, False, None, "refuse: arm PF has seeds [5, 6, 7, 8]"),
             ("M5 one cv5v2 set", rv2, False, None, "holds sets that are not cv5v3_f<k>: ['cv5v2_f0']"),
             ("M6 other A/A spec in the clean-cells block", raa, False, None, "refuse: A/A spec of the 416 clean cells block is 'PF:5,6:7,9'"),
             ("N1 judged width null", nw, True, None, "refuse: width ratio undefined for a judged subset (src:ARTS, OP-A, 532 cells)"),
             ("N2 false crack px null", nf, True, None, "refuse: false crack px undefined (OP-W, 416 clean cells)")]
    for name, doc, mech, want, refusal in extra:
        r, txt = run(work, name, doc, mech)
        if want is not None:
            v = txt.split("## verdict\n", 1)[1].split("\n", 1)[0] if "## verdict\n" in txt else f"(no verdict; rc {r.returncode}: {r.stderr[-200:]})"
            ok = r.returncode == 0 and v.startswith(want) and MARK not in txt
        else:
            v = r.stderr.strip().split("\n")[-1] if r.stderr.strip() else "(no message)"
            ok = r.returncode != 0 and txt == "" and refusal in v and "Traceback" not in r.stderr
        npass += ok; nfail += not ok
        print(f"{'PASS' if ok else 'FAIL'} {name}\n     -> {v}")
    print(f"VERDICT TEST: {npass + nfail} cases, {npass} passed, {nfail} failed (base {BASE_READ}; synthetic changes, not results)")
    return 1 if nfail else 0


if __name__ == "__main__":
    sys.exit(main())
