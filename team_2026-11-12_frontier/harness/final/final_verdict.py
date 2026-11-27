"""Final package: the registered rule of harness/final/FINAL_RULE.md (sections 2 to 4; written 21 Nov 2026 before any D4
dump of a cv5v3 run existed) applied to a FINISHED read folder of run_read_final.sh (<read>/read/read.json). Built from
harness/c3x/c3x_verdict.py (faa2a961): the same headline and guard definitions, read check and refusals, with the arms,
contrasts and decisions of FINAL_RULE.md. It computes nothing new: every number is taken from read.json. It reads no dump
and no label. Output: one text file (refuses to overwrite).

Arms (FINAL_RULE section 2): PF (c3_pf_v11, plain), PF_D4 (the same checkpoints, --tta d4), CS (c3x_hrnet_swad_v11 .swad,
plain = COMBO_SWAD), CS_D4 (.swad.tta_d4), CB (c3x swad_bn, plain = COMBO), CB_D4 (.swad_bn.tta_d4).
M(metric) = that cell set's A/A margin from --aa PF:5,6:7,8 (taken at OP-A, as the read tool sets it).
Primary contrasts, each decided on crack relF1@2:
  (a) PF_D4 - PF   replication of the gaint TTA result (B5) on cv5v3 / cv02 / 5 seeds;
  (b) CS_D4 - CS   the TTA increment on the candidate;
  (c) CS_D4 - PF   the candidate against the baseline: SELECTION-BIASED (FINAL_RULE section 0) on every line.
  Headline of X - R: delta >= M and CI low > 0 at OP-A and OP-W on the 532 cells and on the clean cells (four values).
  Guards (each at OP-A and OP-W on both cell sets; reference R = the contrast's reference arm): width_pooled (width ratio
    X / R in 0.85 to 1.15), width_source (the same per source with >= 40 cells in that cell set), false_alarm (false crack
    px on crack-free cells X <= 1.5 x R), for (b) also false_alarm_pf (X <= 1.5 x PF), inactive (inactive IoU delta X - R
    >= -M(inactive IoU)), miou (mIoU-R13 delta X - R >= -M(mIoU-R13)).
  Outcome: CONFIRMED = headline and every guard pass; GAIN, FAILING GUARDS NAMED = headline passes, some guard fails;
    NOT CONFIRMED = headline fails, then NO LOSS if CI low > -M at all four values, else LOSS.
Decisions (FINAL_RULE section 4, updated 21 Nov with the user's decisions U1, U2: the approved E1 candidates C1 full-pool
PF, C2 full-pool HRNet + SWAD (swad) + D4, C3 the 5-seed ensemble of C2 are never changed by this read; it raises FLAGs):
  D4 (from (b)): CONFIRMED, or GAIN with only width items failing -> "D4 IN C2 / C3 SUPPORTED ON CV5" (width items named, to
    be re-read on E1); GAIN with a false-alarm (incl. false_alarm_pf), inactive or mIoU item failing, or NOT CONFIRMED (no
    loss or loss) -> "FLAG D4": the lead takes it to the user before the E1 opening is frozen (keep C2 / C3 with D4 as
    approved, or replace D4 by plain inference). With FLAG D4 only, CS - PF is printed with the (c) criteria (headline +
    guards against PF, selection-biased) as information for that decision; it is not a gate.
  C2 check (from (c), always CS_D4 - PF): headline passes and no false-alarm, inactive or mIoU item fails -> "C2 PASSES ITS
    CV5 CHECK (selection-biased; the E1 opening is the test)", width items named; else "FLAG C2": the lead looks (and tells
    the user) before the E1 opening is frozen.
  (a): "B5 TTA RESULT REPLICATED ON CV5V3 / CV02" iff CONFIRMED, else "NOT REPLICATED" with the failing parts named; C1 (PF)
    is also shown with D4 in the opening iff (a) is CONFIRMED (descriptive).
Printed beside, deciding nothing: strict crack IoU of every contrast with its interval and the convention band +-0.019
  (the largest shift of a strict-IoU contrast when the same predictions are re-scored on the 1-px centreline, the v1.1 and
  the 3-px labels, dataset_audit/REPORT.md F1; "inside the convention band" when |delta| <= 0.019, else "outside the band
  (decides nothing)"); descriptive contrasts CB_D4 - CB,
  CB_D4 - PF, CS - PF, CS_D4 - PF_D4; levels per arm; per-seed differences; the A/A.

Read check (refuses, nothing written): A/A spec PF:5,6:7,8 in both cell-set blocks; the seven contrasts present; each of the
six arms 25 runs with 25 different run ids matching the arm's run-id pattern, seeds 5 to 9, every set cv5v3_f<k>. A null or
NaN in anything the rule reads (M of relF1@2, inactive IoU, mIoU-R13; delta, CI ends of those keys in the three primary
contrasts, and of CS - PF when (b) raises FLAG D4; judged widths and false-alarm px) is refused in one line naming it. --mechanics skips the read check (tests);
the first line and every verdict line then say "MECHANICS TEST, NOT A VERDICT".

  python final_verdict.py --read /home/noob/work/bench_reads/final_tta --out /home/noob/work/bench_reads/final_tta/verdict.txt
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from pathlib import Path

ARMS = ("PF", "PF_D4", "CS", "CS_D4", "CB", "CB_D4")
ARM_RX = {"PF": r"c3_pf_v11_f[0-4]_s[5-9]", "PF_D4": r"c3_pf_v11_f[0-4]_s[5-9]\.tta_d4",
          "CS": r"c3x_hrnet_swad_v11_f[0-4]_s[5-9]\.swad", "CS_D4": r"c3x_hrnet_swad_v11_f[0-4]_s[5-9]\.swad\.tta_d4",
          "CB": r"c3x_hrnet_swad_v11_f[0-4]_s[5-9]", "CB_D4": r"c3x_hrnet_swad_v11_f[0-4]_s[5-9]\.swad_bn\.tta_d4"}
PRIMARY = (("a", "PF_D4", "PF"), ("b", "CS_D4", "CS"), ("c", "CS_D4", "PF"))
DESCR = (("CB_D4", "CB"), ("CB_D4", "PF"), ("CS", "PF"), ("CS_D4", "PF_D4"))
CONTRASTS = tuple(f"{x} - {r}" for _, x, r in PRIMARY) + tuple(f"{x} - {r}" for x, r in DESCR)
TITLE = {"a": "(a) PF_D4 - PF: replication of the gaint TTA result (B5) on cv5v3 / cv02 / 5 seeds",
         "b": "(b) CS_D4 - CS: the TTA increment on the candidate (same checkpoints, readout swad)",
         "c": "(c) CS_D4 - PF: C2 (CV5 version) against the baseline (selection-biased, FINAL_RULE section 0)"}
OPS = ("OP-A", "OP-W")
BAND = (0.85, 1.15)
FA_MAX = 1.5
MIN_SRC = 40
CONV_BAND = 0.019
RULE_KEYS = ("relF1_2", "inact_iou", "miou_rob")
AA_SPEC, N_RUNS, SEEDS, SET_PREFIX = "PF:5,6:7,8", 25, {5, 6, 7, 8, 9}, "cv5v3_f"
MECH = "MECHANICS TEST, NOT A VERDICT"
SB = "selection-biased"
SEL, BASES = ("CS", "CS_D4"), ("PF", "PF_D4")
RB = "read on the cells that selected the readout; FINAL_RULE section 0"   # (b): CS_D4 - CS, no selection of its own
BAND_TXT = f"(convention band +-{CONV_BAND}; decides nothing)"


def sb_pair(x: str, r: str) -> bool:
    """review B3: a contrast with CS or CS_D4 on one side and PF or PF_D4 on the other carries the selection-bias label"""
    return (x in SEL and r in BASES) or (x in BASES and r in SEL)


def sblab(x: str, r: str) -> str:
    """label appended to every line of contrast x - r that carries a CS / CS_D4 number (review B3)"""
    if sb_pair(x, r):
        return f"\t({SB})"
    if x in SEL and r in SEL:
        return f"\t({RB})"
    return ""
WIDTH = ("width_pooled", "width_source")


def num_ok(x) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


def f(x, nd=4, sign=False):
    return "n/a" if not num_ok(x) else (f"{x:+.{nd}f}" if sign else f"{x:.{nd}f}")


def sub(a, b, nd=4):
    return f"{a - b:+.{nd}f}" if num_ok(a) and num_ok(b) else "n/a"


def check_read(doc: dict, sets) -> None:
    """Refuse unless read.json is the registered final TTA read (see the module text)."""
    for tag, D in sets:
        if D.get("aa_spec") != AA_SPEC:
            sys.exit(f"refuse: A/A spec of the {tag} block is {D.get('aa_spec')!r}, the registered one is {AA_SPEC!r}")
        miss = [c for c in CONTRASTS if c not in D.get("contrasts", {})]
        if miss:
            sys.exit(f"refuse: the {tag} block lacks the contrasts {miss}")
    extra = sorted({r["arm"] for r in doc["runs"]} - set(ARMS))
    if extra:
        sys.exit(f"refuse: arms {extra} are not arms of the registered read {list(ARMS)}")
    for arm in ARMS:
        rs = [r for r in doc["runs"] if r["arm"] == arm]
        ids, seeds = {r["run_id"] for r in rs}, {int(r["seed"]) for r in rs}
        if len(rs) != N_RUNS or len(ids) != N_RUNS:
            sys.exit(f"refuse: arm {arm} has {len(rs)} runs with {len(ids)} different run ids, the registered read has {N_RUNS}")
        if seeds != SEEDS:
            sys.exit(f"refuse: arm {arm} has seeds {sorted(seeds)}, the registered read has {sorted(SEEDS)}")
        bad = sorted({r["set"] for r in rs if not str(r["set"]).startswith(SET_PREFIX)})
        if bad:
            sys.exit(f"refuse: arm {arm} holds sets that are not {SET_PREFIX}<k>: {bad[:5]}")
        off = sorted(r["run_id"] for r in rs if not re.fullmatch(ARM_RX[arm], r["run_id"]))
        if off:
            sys.exit(f"refuse: arm {arm} holds run ids that are not {ARM_RX[arm]}: {off[:3]}")


def check_numbers(sets, pairs=None) -> None:
    """Every number the rule reads must be finite: one refusal line naming it (never a TypeError, never a silent FAIL).
    pairs: default the three primary contrasts; CS - PF is checked when (b) raises FLAG D4 (it is then printed with the rule's criteria)."""
    for tag, D in sets:
        for k in RULE_KEYS:
            if not num_ok(D["M"].get(k)):
                sys.exit(f"refuse: the A/A margin M({k}) of the {tag} block is {D['M'].get(k)!r} (null or NaN); no verdict written")
        for x, r in (pairs or tuple((x, r) for _, x, r in PRIMARY)):
            name = f"{x} - {r}"
            for op in OPS:
                for k in RULE_KEYS:
                    v = D["contrasts"][name][op]["metrics"][k]
                    for fld in ("delta", "lo", "hi"):
                        if not num_ok(v.get(fld)):
                            sys.exit(f"refuse: contrast {name}, {op}, {k}: {fld} is {v.get(fld)!r} in the {tag} block "
                                     f"(null or NaN); no verdict written")


def headline(D: dict, x: str, r: str, tag: str) -> list[tuple]:
    out, M = [], D["M"]["relF1_2"]
    for op in OPS:
        v = D["contrasts"][f"{x} - {r}"][op]["metrics"]["relF1_2"]
        ok = v["delta"] >= M and v["lo"] > 0
        out.append((ok, v["lo"] > -M, f"headline\t{tag}\t{op}\trelF1@2 {x} - {r} = {v['delta']:+.4f} [{v['lo']:+.4f}, {v['hi']:+.4f}], M {M:.4f}"))
    return out


def _width(S, x, r, op, sn, g, tag):
    a, b = S[x][op][sn]["width_ratio"]["mean"], S[r][op][sn]["width_ratio"]["mean"]
    if not (num_ok(a) and num_ok(b)) or b == 0:
        sys.exit(f"refuse: width ratio undefined for a judged subset ({sn}, {op}, {tag}): {x} {a!r}, {r} {b!r}; no verdict written")
    q = a / b
    kind = "width_pooled" if sn == "all" else "width_source"
    return (BAND[0] <= q <= BAND[1], kind, f"{kind} {sn} {op} {tag}",
            f"{kind}\t{tag}\t{op}\t{sn} (n {g['n']}): width {a:.4f} / {b:.4f} = {q:.3f} (band {BAND[0]} to {BAND[1]}; {x} / {r})")


def _fa(S, x, ref, op, tag, kind):
    a, b = S[x][op]["all"]["fa_px"]["mean"], S[ref][op]["all"]["fa_px"]["mean"]
    if not (num_ok(a) and num_ok(b)):
        sys.exit(f"refuse: false crack px undefined ({op}, {tag}): {x} {a!r}, {ref} {b!r}; no verdict written")
    sa, sb = S[x][op]["all"].get("fa_share50", {}).get("mean"), S[ref][op]["all"].get("fa_share50", {}).get("mean")
    return (a <= FA_MAX * b, kind, f"{kind} {op} {tag}",
            f"{kind}\t{tag}\t{op}\tfalse crack px on crack-free cells {x} {a:.0f} against {ref} {b:.0f} = "
            f"{f(a / b if b else None, 2)} x (max {FA_MAX}); share of crack-free cells with >= 50 px {f(sa)} against {f(sb)}")


def guards(D: dict, x: str, r: str, tag: str, fa_pf: bool) -> list[tuple]:
    """-> [(ok, kind, label, text)]; label = kind, subset, operating point, cell set (names the item in the verdict)"""
    out, S, C, M = [], D["summary"], D["contrasts"][f"{x} - {r}"], D["M"]
    for op in OPS:
        for sn, g in S[x][op].items():
            if not (sn == "all" or sn.startswith("src:")):
                continue
            if sn != "all" and g["n"] < MIN_SRC:
                continue
            out.append(_width(S, x, r, op, sn, g, tag))
        out.append(_fa(S, x, r, op, tag, "false_alarm"))
        if fa_pf:
            out.append(_fa(S, x, "PF", op, tag, "false_alarm_pf"))
        for key, kind, name in (("inact_iou", "inactive", "inactive IoU"), ("miou_rob", "miou", "mIoU-R13")):
            v = C[op]["metrics"][key]
            out.append((v["delta"] >= -M[key], kind, f"{kind} {op} {tag}",
                        f"{kind}\t{tag}\t{op}\t{name} {x} - {r} = {v['delta']:+.4f} [{v['lo']:+.4f}, {v['hi']:+.4f}], allowed drop {M[key]:.4f}"))
    return out


def strict_iou(sets, x: str, r: str) -> list[str]:
    L = []
    for tag, D in sets:
        for op in OPS:
            v = D["contrasts"][f"{x} - {r}"][op]["metrics"].get("crack_iou", {})
            d = v.get("delta")
            band = "n/a" if not num_ok(d) else ("inside the convention band" if abs(d) <= CONV_BAND else
                                              "outside the band (decides nothing)")
            L.append(f"strict crack IoU\t{x} - {r}\t{tag}\t{op}\t{f(d, sign=True)} [{f(v.get('lo'), sign=True)}, "
                     f"{f(v.get('hi'), sign=True)}]\tconvention band +-{CONV_BAND}: {band}" + sblab(x, r))
    return L


def per_seed(D: dict, x: str, r: str, tag: str) -> list[str]:
    L, T = [], D["per_seed"]
    for op in OPS:
        a, b = T[x][op]["all"], T[r][op]["all"]
        seeds = sorted(set(a) & set(b), key=int)
        for key in ("relF1_2", "crack_iou", "miou_rob"):
            L.append(f"per_seed\t{tag}\t{op}\t{key}\t{x} - {r}\t" + "\t".join(f"s{s} {sub(a[s].get(key), b[s].get(key))}" for s in seeds)
                     + (f"\t{BAND_TXT}" if key == "crack_iou" else "") + sblab(x, r))
    return L


def descriptive(sets, x: str, r: str) -> list[str]:
    """information only: relF1@2, strict crack IoU, inactive IoU, mIoU-R13 deltas, width and false-alarm ratios; n/a when undefined"""
    L = []
    for tag, D in sets:
        S = D["summary"]
        for op in OPS:
            m = D["contrasts"][f"{x} - {r}"][op]["metrics"]
            parts = [f"{k} {f(m.get(k, {}).get('delta'), sign=True)} [{f(m.get(k, {}).get('lo'), sign=True)}, {f(m.get(k, {}).get('hi'), sign=True)}]"
                     + (f" {BAND_TXT}" if k == "crack_iou" else "") for k in ("relF1_2", "crack_iou", "inact_iou", "miou_rob")]
            wa, wb = S[x][op]["all"]["width_ratio"]["mean"], S[r][op]["all"]["width_ratio"]["mean"]
            fa, fb = S[x][op]["all"]["fa_px"]["mean"], S[r][op]["all"]["fa_px"]["mean"]
            parts.append(f"width ratio {f(wa / wb if num_ok(wa) and num_ok(wb) and wb else None, 3)}")
            parts.append(f"false crack px {f(fa, 0)} / {f(fb, 0)}")
            L.append(f"descriptive\t{x} - {r}\t{tag}\t{op}\t" + "; ".join(parts) + sblab(x, r))
    return L


def outcome(H, G) -> tuple[str, list]:
    fails = [(k, lab) for ok, k, lab, _ in G if not ok]
    if all(ok for ok, _, _ in H):
        return ("CONFIRMED" if not fails else "GAIN, FAILING GUARDS NAMED"), fails
    return ("NOT CONFIRMED, NO LOSS" if all(nl for _, nl, _ in H) else "NOT CONFIRMED, LOSS"), fails


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--read", required=True, help="output folder of run_read_final.sh")
    ap.add_argument("--out", required=True)
    ap.add_argument("--mechanics", action="store_true", help="skip the check of the read; the output is marked as a mechanics test, not a verdict")
    a = ap.parse_args()
    out = Path(a.out)
    if out.exists():
        sys.exit(f"refuse: {out} exists")
    doc = json.loads((Path(a.read) / "read" / "read.json").read_text())
    xk = [k for k in doc if k.startswith("x") and k[1:].isdigit()]
    if len(xk) != 1:
        sys.exit(f"refuse: expected one kept-cells block in read.json, found {xk}")
    sets = ((f"{doc['n_stems']} cells", doc), (f"{doc[xk[0]]['n_stems']} clean cells", doc[xk[0]]))
    for tag, D in sets:
        if not (D.get("M") and D.get("aa")):
            sys.exit(f"refuse: no A/A margin in the {tag} block")
        for arm in ARMS:
            if arm not in D["summary"]:
                sys.exit(f"refuse: arm {arm} missing in the {tag} block")
        if a.mechanics:
            miss = [c for c in CONTRASTS if c not in D.get("contrasts", {})]
            if miss:
                sys.exit(f"refuse: the {tag} block lacks the contrasts {miss}")
    if not a.mechanics:
        check_read(doc, sets)
    check_numbers(sets)
    mk = (lambda s: f"[{MECH}] {s}") if a.mechanics else (lambda s: s)
    rule = Path(__file__).resolve().parent / "FINAL_RULE.md"
    rmd5 = hashlib.md5(rule.read_bytes()).hexdigest()[:8] if rule.exists() else "absent"
    L = [f"# {MECH}: --mechanics was given, so the read was not checked to be the registered cv5v3 read "
         f"({AA_SPEC}; {N_RUNS} runs per arm; seeds {sorted(SEEDS)}; sets {SET_PREFIX}<k>)."] if a.mechanics else []
    L += [f"# final TTA verdict from {a.read}/read/read.json (read tool {doc['tool_md5'][:8]}; A/A {doc['aa_spec']}; "
          f"groups {doc['groups_md5'][:8]}); rule: harness/final/FINAL_RULE.md ({rmd5}) sections 2 to 4 and 7; script {Path(__file__).name}",
          "# relF1@2 decides; strict crack IoU is printed with its convention band and decides nothing. (c) is selection-biased: "
          "the swad readout was chosen after the c3x read on these cells; the unbiased test is the E1 opening.",
          "# every number of the CS and CS_D4 arms on these cells is selection-biased (FINAL_RULE section 0): every line of a "
          "contrast of CS or CS_D4 against PF or PF_D4, and every level line of CS and CS_D4, says so; lines of (b) CS_D4 - CS "
          f"say '{RB}'.",
          "# the approved E1 candidates (C1 full-pool PF; C2 full-pool HRNet + SWAD (swad) + D4; C3 the 5-seed ensemble of C2) are "
          "never changed by this read: where CV5 does not support a part of C2 / C3 it raises a FLAG for the lead and the user."]
    res, blk = {}, {}
    for key, x, r in PRIMARY:
        H, G = [], []
        for tag, D in sets:
            H += headline(D, x, r, tag)
            G += guards(D, x, r, tag, fa_pf=(key == "b"))
        res[key] = outcome(H, G)
        blk[key] = (H, G)
    # ---- D4 in C2 / C3 (FINAL_RULE section 4, rows (b)): supported, or FLAG D4 (never dropped by this read)
    ob, fb = res["b"]
    wfail = [lab for k, lab in fb if k in WIDTH]
    ofail = [lab for k, lab in fb if k not in WIDTH]
    ask = ("the lead takes it to the user before the E1 opening is frozen (keep C2 / C3 with D4 as approved, or replace D4 "
           "by plain inference); CS - PF is printed with the (c) criteria as information for that decision.")
    if ob == "CONFIRMED":
        flag_d4, db = False, "D4 IN C2 / C3 SUPPORTED ON CV5: (b) CS_D4 - CS is CONFIRMED."
    elif ob == "GAIN, FAILING GUARDS NAMED" and not ofail:
        flag_d4, db = False, ("D4 IN C2 / C3 SUPPORTED ON CV5: (b) passes the headline and only width items fail ("
                              + "; ".join(wfail) + "); these items are handed to the opening rule to be re-read on E1 (descriptive there).")
    elif ob == "GAIN, FAILING GUARDS NAMED":
        flag_d4, db = True, ("FLAG D4: (b) passes the headline but a false-alarm, inactive or mIoU item fails ("
                             + "; ".join(ofail) + ")" + (f"; width items also failing: {'; '.join(wfail)}" if wfail else "")
                             + "; CV5 does not support D4 on the candidate without a guard failure; " + ask)
    else:
        flag_d4, db = True, (f"FLAG D4: (b) is {ob}: D4 costs 8x inference without a confirmed CV5 gain on the candidate; " + ask)
    if flag_d4:   # information for the lead's / user's D4 decision, never a gate (section 4; section 7 item 2)
        check_numbers(sets, (("CS", "PF"),))
        H, G = [], []
        for tag, D in sets:
            H += headline(D, "CS", "PF", tag)
            G += guards(D, "CS", "PF", tag, fa_pf=False)
        res["plain"] = outcome(H, G)
        blk["plain"] = (H, G)
    for key, x, r in PRIMARY:
        H, G = blk[key]
        oc, fails = res[key]
        sfx = sblab(x, r)
        L.append(f"\n## {TITLE[key]}")
        if key == "b":
            L.append("interval of (b): the read tool's unpaired-seed bootstrap (conservative; FINAL_RULE section 7 item 1); "
                     "seed-paired differences in the per-seed section")
        L += [f"{'PASS' if ok else 'FAIL'}\t{t}{sfx}" for ok, _, t in H]
        L += [f"{'PASS' if ok else 'FAIL'}\t{t}{sblab(x, 'PF') if k == 'false_alarm_pf' else sfx}" for ok, k, _, t in G]
        L.append(mk(f"=> ({key}) {x} - {r}: {oc}; failing guard items {len(fails)}"
                    + (": " + "; ".join(lb for _, lb in fails) if fails else "") + (f" ({SB})" if key == "c" else f" ({RB})" if key == "b" else "")))
    if flag_d4:
        H, G = blk["plain"]
        op_, fp_ = res["plain"]
        L.append("\n## CS - PF with the (c) criteria: information for the FLAG D4 decision (the plain alternative to C2; guards "
                 "against PF; selection-biased; not a gate; FINAL_RULE section 4 and section 7 item 2)")
        L += [f"{'PASS' if ok else 'FAIL'}\t{t}\t({SB}; information)" for ok, _, t in H]
        L += [f"{'PASS' if ok else 'FAIL'}\t{t}\t({SB}; information)" for ok, _, _, t in G]
        pw = [lab for k, lab in fp_ if k in WIDTH]
        po = [lab for k, lab in fp_ if k not in WIDTH]
        crit = ("meets the (c) criteria (headline passes; no false-alarm, inactive or mIoU item fails"
                + (f"; width items: {'; '.join(pw)}" if pw else "") + ")") if not op_.startswith("NOT CONFIRMED") and not po else \
            ("does not meet the (c) criteria (" + ("headline fails" if op_.startswith("NOT CONFIRMED") else
                                                   "failing: " + "; ".join(po)) + ")")
        L.append(mk(f"=> CS - PF (information for FLAG D4): {op_}; failing guard items {len(fp_)}"
                    + (": " + "; ".join(lab for _, lab in fp_) if fp_ else "") + f"; plain swad {crit} ({SB}; not a gate)"))
    # ---- decisions (FINAL_RULE section 4)
    oa, fa_ = res["a"]
    if oa == "CONFIRMED":
        da = "B5 TTA RESULT REPLICATED ON CV5V3 / CV02: (a) PF_D4 - PF is CONFIRMED. C1 (PF) is also shown with D4 in the opening (descriptive)."
    else:
        why = "headline" if oa.startswith("NOT CONFIRMED") else "; ".join(lab for _, lab in fa_)
        da = (f"B5 TTA RESULT NOT REPLICATED ON CV5V3 / CV02: (a) is {oa} (failing: {why}). C1 (PF) is not shown with D4 in "
              "the opening. (a) decides nothing about C2 / C3.")
    oc_, fc = res["c"]
    cw = [lab for k, lab in fc if k in WIDTH]
    co = [lab for k, lab in fc if k not in WIDTH]
    if not oc_.startswith("NOT CONFIRMED") and not co:
        dc = (f"C2 PASSES ITS CV5 CHECK ({SB}; the E1 opening is the test): (c) CS_D4 - PF passes the headline and no "
              "false-alarm, inactive or mIoU item fails" + (f"; width items named: {'; '.join(cw)}" if cw else "") + ".")
    else:
        why = "(c) CS_D4 - PF does not pass the headline" if oc_.startswith("NOT CONFIRMED") else \
            "a false-alarm, inactive or mIoU item of (c) CS_D4 - PF fails (" + "; ".join(co) + ")"
        dc = (f"FLAG C2: {why} ({SB}); the lead looks (and tells the user) before the E1 opening is frozen; the full-pool "
              "runs stay as trained artefacts.")
    L.append("\n## decisions (FINAL_RULE section 4; the approved E1 candidates C1, C2, C3 are not changed by this read)")
    L.append(mk(f"(a) {da}"))
    L.append(mk(f"(b) {db}"))
    L.append(mk(f"(c) {dc}"))
    L.append("swad vs swad_bn: not re-decided (FINAL_RULE section 4; swad approved by the user for C2 / C3); the CB arms are information only.")
    # ---- beside
    L.append("\n## beside the verdict: strict crack IoU (decides nothing; convention band +-0.019 = the largest shift of a "
             "strict-IoU contrast when the same predictions are re-scored on the 1-px centreline, the v1.1 and the 3-px labels, "
             "dataset_audit/REPORT.md F1)")
    for key, x, r in PRIMARY:
        L += strict_iou(sets, x, r)
    for x, r in DESCR:
        L += [t + ("\t(information for FLAG D4)" if (x, r) == ("CS", "PF") and flag_d4 else "") for t in strict_iou(sets, x, r)]
    L.append("\n## beside the verdict: descriptive contrasts (decide nothing)")
    for x, r in DESCR:
        L += descriptive(sets, x, r)
    L.append("\n## beside the verdict: levels (mean over seeds; crack IoU, relF1@2, inactive IoU (label-noise band +-0.05 to 0.07, "
             "audit F4), mIoU-R13, false crack px on crack-free cells, width ratio)")
    for tag, D in sets:
        for op in OPS:
            for arm in ARMS:
                g = D["summary"][arm][op]["all"]
                L.append(f"level\t{tag}\t{op}\t{arm}\t" + "\t".join(f"{k} {f(g.get(k, {}).get('mean'), 0 if k == 'fa_px' else 4)}"
                                                                for k in ("crack_iou", "relF1_2", "inact_iou", "miou_rob", "fa_px", "width_ratio"))
                         + (f"\t({SB})" if arm in SEL else ""))
    L.append("\n## beside the verdict: per-seed differences (pooled out-of-fold value of the seed, X minus R of the same seed)")
    for key, x, r in PRIMARY:
        for tag, D in sets:
            L += per_seed(D, x, r, tag)
    if flag_d4:
        for tag, D in sets:
            L += [t + "\t(information for FLAG D4)" for t in per_seed(D, "CS", "PF", tag)]
    for tag, D in sets:
        A = D["aa"]["OP-A"]["metrics"]
        L.append(f"A/A\t{tag}\t" + "; ".join(
            f"{k} delta {f(A.get(k, {}).get('delta'), sign=True)} SE {f(A.get(k, {}).get('se'))} M {f(D['M'].get(k))}"
            for k in ("relF1_2", "crack_iou", "inact_iou", "miou_rob")))
    out.write_text("\n".join(L) + "\n")
    print(f"wrote {out} ({len(L)} lines): (a) {res['a'][0]} | (b) {res['b'][0]} -> {'FLAG D4' if flag_d4 else 'D4 supported'} | "
          f"(c) {res['c'][0]} -> {'C2 passes' if dc.startswith('C2 PASSES') else 'FLAG C2'}")


if __name__ == "__main__":
    main()
