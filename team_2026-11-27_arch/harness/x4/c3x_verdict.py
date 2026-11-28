"""c3x: the registered rule of LAUNCH_REQUEST_c3x.md section 6 (lead's rulings C6 and Q2 of 17 Nov 2026, set before any c3x
run exists), applied to a FINISHED read folder of run_read_c3x.sh (<read>/read/read.json). Built from c3swad_verdict.py
(61ce4ba0): the same headline, guards, carry rule, read check and refusals, with the arms renamed (SWADBN -> COMBO, SWAD ->
COMBO_SWAD) and three additions: the four pre-declared secondary contrasts, the final-model rule, and the encoder probe of
HRNet (one stage, 'model'). It computes nothing new: every number is taken from read.json. It reads no dump and no label.
Output: one text file (refuses to overwrite).

Arms: PF (c3_pf_v11), HRNET (c3h_hrnet_w18_unetpp_pf), SWADBN (c3s_swad_v11, readout swad_bn), COMBO (c3x_hrnet_swad_v11,
readout swad_bn, the card's weights_key), COMBO_SWAD (c3x_hrnet_swad_v11 .swad, readout swad = "COMBO.swad", the declared
secondary readout). M = that cell set's A/A margin from --aa PF:5,6:7,8 (taken at OP-A, as the read tool sets it).
Primary (c3swad rule with COMBO for swad_bn and COMBO_SWAD for swad):
  Headline, per readout R in {COMBO, COMBO_SWAD}: crack relF1@2, contrast R - PF; passes when delta >= M and the interval's
    lower end > 0 at OP-A and at OP-W, on the 532 cells and on the clean cells (four values).
  Guards, per readout, each on both cell sets and at OP-A and OP-W: width_pooled (width ratio R / PF inside 0.85 to 1.15),
    width_source (the same per source with at least 40 cells in that cell set), false_alarm (false crack px on crack-free
    cells R <= 1.5 x PF), inactive (inactive IoU delta >= -M(inactive IoU)), miou (mIoU-R13 delta >= -M(mIoU-R13)).
  Verdict (the c3swad carry rule, lead's ruling of 17 Nov 2026 09:30, with the readouts renamed): "Confirmed if the primary
    (COMBO, swad_bn) passes the headline at both operating points and every guard. If the primary passes the headline and
    every failing guard item of the primary is a per-source width (either operating point, either cell set), the confirmed
    claim is carried by the declared secondary readout COMBO.swad, provided COMBO.swad itself passes the headline at both
    operating points and every guard on both cell sets. If the primary fails the headline: not confirmed (no confirmed
    gain). In every other case: not confirmed, reported as a gain with the failing guards named."
Secondary (pre-declared; all four printed): COMBO - HRNET, COMBO - SWADBN, COMBO_SWAD - HRNET, COMBO_SWAD - SWADBN, each on
  crack relF1@2 at OP-A and OP-W on the 532 and the clean cells (baseline PF for all contrasts; OP-W matches every arm to PF's
  width, so the secondary contrasts at OP-W compare arms at the same width; lead's Q4 ruling of 17 Nov):
    adds     delta >= M and CI low > 0 at all four;
    no loss  not adds, and CI low > -M at all four;
    loses    otherwise.
  The verdict uses the readout that carries the primary claim (COMBO_SWAD if the claim is carried, else COMBO).
Final-model rule: COMBO is the final-model candidate if the primary is confirmed (directly or carried) with every guard and
  the carrying readout is "adds" or "no loss" against both HRNET and SWADBN. Otherwise the candidate is the best confirmed
  single arm; that choice rests on the single arms' own registered verdicts (c3swad verdict.txt for SWADBN; the HRNet cv5v3
  read for HRNET) and is not made by this tool, which prints HRNET - PF and SWADBN - PF (relF1@2, difference of the seed
  means, no interval) from this read as information, with no ranking (lead's Q3 ruling of 17 Nov).

Before any criterion it checks that read.json is the registered read and refuses otherwise: A/A spec PF:5,6:7,8 in both
cell-set blocks; for each of the five arms 25 runs with 25 different run ids, seeds 5 to 9, every set name cv5v3_f<k>; the
six contrasts present. An undefined (null) judged width or false-alarm value is refused in plain words, and so is (review
N3) a null or NaN delta, CI end or A/A margin anywhere the rule reads one (primary, guards, secondary), in one line naming
the contrast; no file is written. Lines beside the verdict (per-seed, A/A, information) print n/a for an undefined value.
--mechanics skips the read check (tests); the first line and the verdict line then say "MECHANICS TEST, NOT A VERDICT".

  python c3x_verdict.py --read /home/noob/work/bench_reads/c3x --probes /home/noob/work/bench_relay/c3x \
      --out /home/noob/work/bench_reads/c3x/verdict.txt
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

BASE, PRIMARY, SECONDARY = "PF", "COMBO", "COMBO_SWAD"
SINGLES = ("HRNET", "SWADBN")
ARMS = (BASE, "HRNET", "SWADBN", PRIMARY, SECONDARY)
CONTRASTS = tuple(f"{r} - {b}" for b in (BASE,) + SINGLES for r in (PRIMARY, SECONDARY))
OPS = ("OP-A", "OP-W")
BAND = (0.85, 1.15)
FA_MAX = 1.5
MIN_SRC = 40
AA_SPEC, N_RUNS, SEEDS, SET_PREFIX = "PF:5,6:7,8", 25, {5, 6, 7, 8, 9}, "cv5v3_f"
MECH = "MECHANICS TEST, NOT A VERDICT"
NAMES = {PRIMARY: "COMBO (swad_bn)", SECONDARY: "COMBO.swad (swad)"}


def undefined(x) -> bool:
    return x is None or x != x


def check_read(doc: dict, sets) -> None:
    """Refuse unless read.json is the registered c3x read (see the module text)."""
    for tag, D in sets:
        if D.get("aa_spec") != AA_SPEC:
            sys.exit(f"refuse: A/A spec of the {tag} block is {D.get('aa_spec')!r}, the registered one is {AA_SPEC!r}")
        miss = [c for c in CONTRASTS if c not in D["contrasts"]]
        if miss:
            sys.exit(f"refuse: the {tag} block lacks the contrasts {miss}")
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


def f(x, nd=4):
    return "n/a" if x is None else f"{x:.{nd}f}"


def num_ok(x) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


def check_numbers(sets) -> None:
    """Review N3: every number the rule reads must be a finite number; a null or NaN delta, CI end or margin is refused in
    one line naming the contrast (never a TypeError, never a silent 'loses')."""
    for tag, D in sets:
        for k in ("relF1_2", "inact_iou", "miou_rob"):
            if not num_ok(D["M"].get(k)):
                sys.exit(f"refuse: the A/A margin M({k}) of the {tag} block is {D['M'].get(k)!r} (null or NaN); no verdict written")
        for name in CONTRASTS:
            keys = ("relF1_2", "inact_iou", "miou_rob") if name.endswith(f" - {BASE}") else ("relF1_2",)
            for op in OPS:
                for k in keys:
                    v = D["contrasts"][name][op]["metrics"][k]
                    for fld in ("delta", "lo", "hi"):
                        if not num_ok(v.get(fld)):
                            sys.exit(f"refuse: contrast {name}, {op}, {k}: {fld} is {v.get(fld)!r} in the {tag} block "
                                     f"(null or NaN); no verdict written")


def sub(a, b, nd=4):
    return f"{a - b:+.{nd}f}" if num_ok(a) and num_ok(b) else "n/a"


def headline(D: dict, arm: str, tag: str) -> list[tuple]:
    out = []
    M = D["M"]["relF1_2"]
    for op in OPS:
        v = D["contrasts"][f"{arm} - {BASE}"][op]["metrics"]["relF1_2"]
        ok = v["delta"] >= M and v["lo"] > 0
        out.append((ok, f"headline\t{tag}\t{op}\trelF1@2 {arm} - {BASE} = {v['delta']:+.4f} [{v['lo']:+.4f}, {v['hi']:+.4f}], M {M:.4f}"))
    return out


def guards(D: dict, arm: str, tag: str) -> list[tuple]:
    """-> [(ok, kind, label, text)]; label = kind, subset, operating point, cell set (names the item in the verdict)"""
    out = []
    S, C, M = D["summary"], D["contrasts"][f"{arm} - {BASE}"], D["M"]
    for op in OPS:
        for sn, g in S[arm][op].items():
            if not (sn == "all" or sn.startswith("src:")):
                continue
            if sn != "all" and g["n"] < MIN_SRC:
                continue
            a, b = g["width_ratio"]["mean"], S[BASE][op][sn]["width_ratio"]["mean"]
            if undefined(a) or undefined(b) or b == 0:
                sys.exit(f"refuse: width ratio undefined for a judged subset ({sn}, {op}, {tag}): {arm} {a!r}, {BASE} {b!r}; no verdict written")
            r = a / b
            ok = BAND[0] <= r <= BAND[1]
            kind = "width_pooled" if sn == "all" else "width_source"
            out.append((ok, kind, f"{kind} {sn} {op} {tag}", f"{kind}\t{tag}\t{op}\t{sn} (n {g['n']}): width {a:.4f} / {b:.4f} = {r:.3f} (band {BAND[0]} to {BAND[1]})"))
        a, b = S[arm][op]["all"]["fa_px"]["mean"], S[BASE][op]["all"]["fa_px"]["mean"]
        if undefined(a) or undefined(b):
            sys.exit(f"refuse: false crack px undefined ({op}, {tag}): {arm} {a!r}, {BASE} {b!r}; no verdict written")
        ok = a <= FA_MAX * b
        out.append((ok, "false_alarm", f"false_alarm {op} {tag}", f"false_alarm\t{tag}\t{op}\tfalse crack px on crack-free cells {a:.0f} against {b:.0f}"
                    f" = {f(a / b if b else None, 2)} x (max {FA_MAX}); share of crack-free cells with >= 50 px "
                    f"{S[arm][op]['all']['fa_share50']['mean']:.4f} against {S[BASE][op]['all']['fa_share50']['mean']:.4f}"))
        for key, kind, name in (("inact_iou", "inactive", "inactive IoU"), ("miou_rob", "miou", "mIoU-R13")):
            v = C[op]["metrics"][key]
            ok = v["delta"] >= -M[key]
            out.append((ok, kind, f"{kind} {op} {tag}", f"{kind}\t{tag}\t{op}\t{name} {arm} - {BASE} = {v['delta']:+.4f} [{v['lo']:+.4f}, {v['hi']:+.4f}], "
                                       f"allowed drop {M[key]:.4f}"))
    return out


def secondary(sets, arm: str, ref: str) -> tuple[str, list[str]]:
    """'adds' | 'no loss' | 'loses' for arm - ref on relF1@2 at OP-A and OP-W on both cell sets, with the four values"""
    vals, L = [], []
    for tag, D in sets:
        M = D["M"]["relF1_2"]
        for op in OPS:
            v = D["contrasts"][f"{arm} - {ref}"][op]["metrics"]["relF1_2"]
            vals.append((v["delta"], v["lo"], M))
            L.append(f"secondary\t{arm} - {ref}\t{tag}\t{op}\trelF1@2 {v['delta']:+.4f} [{v['lo']:+.4f}, {v['hi']:+.4f}], M {M:.4f}"
                     f"\tadds-item {'yes' if v['delta'] >= M and v['lo'] > 0 else 'no'}\tCI low > -M {'yes' if v['lo'] > -M else 'no'}")
    if all(d >= M and lo > 0 for d, lo, M in vals):
        lab = "adds"
    elif all(lo > -M for d, lo, M in vals):
        lab = "no loss"
    else:
        lab = "loses"
    return lab, L


def per_seed(D: dict, arm: str, tag: str) -> list[str]:
    L = []
    T = D["per_seed"]
    for op in OPS:
        for key in ("relF1_2", "crack_iou", "miou_rob"):
            a, b = T[arm][op]["all"], T[BASE][op]["all"]
            seeds = sorted(set(a) & set(b), key=int)
            L.append(f"per_seed\t{tag}\t{op}\t{key}\t{arm} - {BASE}\t" + "\t".join(f"s{s} {sub(a[s][key], b[s][key])}" for s in seeds))
    return L


def probes(root: Path) -> list[str]:
    """HRNet encoder: one probe stage, 'model' (timm tensor names encoder.model.*). Last row per step, step 20000."""
    rows = []
    for p in sorted(root.glob("*/experiments/*/enc_probe.jsonl")) + sorted(root.glob("*/enc_probe.jsonl")):
        last = None
        for line in p.read_text().splitlines():
            if line.strip():
                d = json.loads(line)
                if d.get("step") == 20000:
                    last = d
        if last:
            st = last["stages"]
            if list(st) != ["model"]:
                rows.append((p.parent.name, None, f"stages {list(st)} (expected one stage 'model')"))
            else:
                rows.append((p.parent.name, st["model"]["cos"], f"model cos {st['model']['cos']:.4f}\tnr {st['model']['nr']:.4f}\tdev {st['model']['dev']:.4f}"))
    L = [f"probe\t{n}\t{t}" for n, _, t in rows]
    cs = [c for _, c, _ in rows if c is not None]
    if cs:
        L.append(f"probe\tsummary\t{len(cs)} runs: encoder (stage 'model') cos to the ImageNet start at step 20000 {min(cs):.3f} to {max(cs):.3f}")
    if not rows:
        L.append(f"probe\tno enc_probe.jsonl with a step-20000 line under {root}")
    return L


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--read", required=True, help="output folder of run_read_c3x.sh")
    ap.add_argument("--probes", default=None, help="folder searched for */experiments/*/enc_probe.jsonl (the c3x relay)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--mechanics", action="store_true", help="skip the check of the read; the output is marked as a mechanics test, not a verdict")
    a = ap.parse_args()
    out = Path(a.out)
    if out.exists():
        sys.exit(f"refuse: {out} exists")
    doc = json.loads((Path(a.read) / "read" / "read.json").read_text())
    xk = [k for k in doc if k.startswith("x") and k[1:].isdigit()]
    assert len(xk) == 1, f"expected one kept-cells block in read.json, found {xk}"
    sets = ((f"{doc['n_stems']} cells", doc), (f"{doc[xk[0]]['n_stems']} clean cells", doc[xk[0]]))
    for _, D in sets:
        assert D["M"] and D["aa"], "no A/A margin in the read"
        for arm in ARMS:
            assert arm in D["summary"], f"arm {arm} missing"
    if not a.mechanics:
        check_read(doc, sets)
    check_numbers(sets)
    L = [f"# {MECH}: --mechanics was given, so the read was not checked to be the registered cv5v3 read "
         f"({AA_SPEC}; {N_RUNS} runs per arm; seeds {sorted(SEEDS)}; sets {SET_PREFIX}<k>)."] if a.mechanics else []
    L += [f"# c3x verdict from {a.read}/read/read.json (read tool {doc['tool_md5'][:8]}; A/A {doc['aa_spec']}; "
          f"groups {doc['groups_md5'][:8]}); rule: LAUNCH_REQUEST_c3x.md section 6; script {Path(__file__).name}"]
    res = {}
    for arm in (PRIMARY, SECONDARY):
        H, G = [], []
        for tag, D in sets:
            H += headline(D, arm, tag)
            G += guards(D, arm, tag)
        res[arm] = {"headline": all(ok for ok, _ in H), "fails": [(k, lab) for ok, k, lab, _ in G if not ok]}
        L.append(f"\n## {arm} = {NAMES[arm]} against PF ({'primary' if arm == PRIMARY else 'declared secondary readout'})")
        L += [f"{'PASS' if ok else 'FAIL'}\t{t}" for ok, t in H]
        L += [f"{'PASS' if ok else 'FAIL'}\t{t}" for ok, _, _, t in G]
        L.append(f"=> {arm}: headline {'PASS' if res[arm]['headline'] else 'FAIL'}; failing guard items {len(res[arm]['fails'])}"
                 + (": " + "; ".join(lab for _, lab in res[arm]["fails"]) if res[arm]["fails"] else ""))
    p, s = res[PRIMARY], res[SECONDARY]
    only_src = bool(p["fails"]) and all(k == "width_source" for k, _ in p["fails"])
    named = "; ".join(lab for _, lab in p["fails"])
    carrier = None
    if p["headline"] and not p["fails"]:
        carrier = PRIMARY
        v = "CONFIRMED: the primary readout COMBO (swad_bn) passes the headline at both operating points and every guard."
    elif p["headline"] and only_src and s["headline"] and not s["fails"]:
        carrier = SECONDARY
        v = ("CONFIRMED, CARRIED BY THE DECLARED SECONDARY READOUT COMBO.swad: COMBO (swad_bn) passes the headline and every "
             f"failing guard item of COMBO is a per-source width ({named}); COMBO.swad passes the headline at both operating "
             "points and every guard on both cell sets.")
    elif not p["headline"]:
        v = "NOT CONFIRMED (no confirmed gain): the primary readout COMBO (swad_bn) does not pass the headline."
    else:
        why = ("a failing guard item of COMBO is not a per-source width" if not only_src else
               "COMBO.swad does not pass " + " and ".join(x for x in (None if s["headline"] else "the headline",
               "every guard (" + "; ".join(lab for _, lab in s["fails"]) + ")" if s["fails"] else None) if x))
        v = (f"NOT CONFIRMED, reported as a gain with the failing guards named: COMBO (swad_bn) passes the headline; failing "
             f"guard items of COMBO: {named}. No carry by COMBO.swad: {why}.")
    if a.mechanics:
        v = f"[{MECH}] {v}"
    L.append(f"\n## primary verdict (COMBO - PF)\n{v}")
    used = carrier or PRIMARY
    L.append(f"\n## secondary contrasts (pre-declared; M = that cell set's A/A margin for relF1@2; baseline PF for all contrasts: "
             f"OP-W matches every arm to PF's width, so at OP-W the arms are compared at the same width). Readout used for the "
             f"final-model rule: {used} = {NAMES[used]}"
             f"{' (carries the primary claim)' if carrier else ' (the primary readout; the primary claim is not confirmed)'}")
    lab = {}
    for arm in (PRIMARY, SECONDARY):
        for ref in SINGLES:
            lab[(arm, ref)], SL = secondary(sets, arm, ref)
            L += SL
            L.append(f"=> {arm} - {ref}: {lab[(arm, ref)].upper()}{'   (used)' if arm == used else ''}")
    ok_single = all(lab[(used, ref)] in ("adds", "no loss") for ref in SINGLES)
    if carrier and ok_single:
        fm = (f"COMBO IS THE FINAL-MODEL CANDIDATE: the primary claim is confirmed{' (carried by COMBO.swad)' if carrier == SECONDARY else ''} "
              f"and {used} is '{lab[(used, 'HRNET')]}' against HRNET and '{lab[(used, 'SWADBN')]}' against SWADBN.")
    else:
        why = "the primary claim is not confirmed" if not carrier else \
            "; ".join(f"{used} '{lab[(used, ref)]}' against {ref}" for ref in SINGLES if lab[(used, ref)] == "loses")
        fm = (f"COMBO IS NOT THE FINAL-MODEL CANDIDATE ({why}): the candidate is the best confirmed single arm, decided from "
              "the single arms' own registered verdicts (c3swad verdict.txt for SWADBN; the HRNet cv5v3 read for HRNET), not by this tool.")
    if a.mechanics:
        fm = f"[{MECH}] {fm}"
    L.append(f"\n## final-model rule\n{fm}")
    if not (carrier and ok_single):   # lead's Q3 ruling: information beside the single-arm sentence, no ranking
        rm = lambda D, op, arm: D["summary"][arm][op]["all"]["relF1_2"]["mean"]  # noqa: E731
        L.append("information only, no ranking (relF1@2 from this read, difference of the seed means, no interval): " + "; ".join(
            f"{tag} {op} " + ", ".join(f"{arm} - PF {sub(rm(D, op, arm), rm(D, op, BASE))}" for arm in SINGLES)
            for tag, D in sets for op in OPS))
    L.append("\n## beside the verdict: per-seed differences (pooled out-of-fold value of the seed, arm minus PF of the same seed)")
    for arm in (PRIMARY, SECONDARY):
        for tag, D in sets:
            L += per_seed(D, arm, tag)
    for tag, D in sets:
        L.append(f"A/A\t{tag}\t" + "; ".join(f"{k} delta {sub(D['aa']['OP-A']['metrics'][k]['delta'], 0)} SE {f(D['aa']['OP-A']['metrics'][k]['se'] if num_ok(D['aa']['OP-A']['metrics'][k]['se']) else None)} M {f(D['M'][k] if num_ok(D['M'][k]) else None)}"
                                             for k in ("relF1_2", "crack_iou", "inact_iou", "miou_rob")))
    if a.probes:
        L.append("\n## beside the verdict: encoder cosine to the ImageNet start at step 20000 (enc_probe.jsonl of each c3x run)")
        L += probes(Path(a.probes))
    out.write_text("\n".join(L) + "\n")
    print(f"wrote {out} ({len(L)} lines): {v[:70]} | {fm[:60]}")


if __name__ == "__main__":
    main()
