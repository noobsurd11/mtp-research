"""c3swad: the registered rule of LAUNCH_REQUEST_c3swad.md section 7, applied to a FINISHED read folder of
run_read_c3swad.sh (<read>/read/read.json). It computes nothing new: every number is taken from read.json (the read
tool's summary, contrasts, margins and per-seed table, for the 532 cells and for the kept clean cells). It reads no dump
and no label. Output: one text file (refuses to overwrite) with every criterion, its value and PASS / FAIL, the verdict
sentence, the per-seed differences and, with --probes, layer3 / layer4 cosine to init at step 20000 per swad run.

Rule (lead's ruling of 17 Nov 2026, 09:35, before any cv5v3 swad run exists; it replaces the first wording of 08:43):
  Headline, per readout R in {SWADBN (primary), SWAD (declared secondary)}: crack relF1@2, contrast R - PF. It passes
    when delta >= M and the interval's lower end > 0 at OP-A and at OP-W, on the 532 cells and on the clean cells
    (four values; M = that cell set's own A/A margin, taken at OP-A).
  Guards, per readout, each on both cell sets and at OP-A and OP-W:
    width_pooled   width ratio of R / width ratio of PF, all cells, inside 0.85 to 1.15
    width_source   the same per source with at least 40 cells in that cell set
    false_alarm    false crack px on crack-free cells: R <= 1.5 x PF
    inactive       inactive IoU: delta >= -M(inactive IoU)
    miou           mIoU-R13: delta >= -M(mIoU-R13)
  Verdict (lead's ruling, verbatim): "Confirmed if the primary (swad_bn) passes the headline at both operating points and
    every guard. If the primary passes the headline and every failing guard item of the primary is a per-source width
    (either operating point, either cell set), the confirmed claim is carried by the declared secondary readout swad,
    provided swad itself passes the headline at both operating points and every guard on both cell sets. If the primary
    fails the headline: not confirmed (no confirmed gain). In every other case: not confirmed, reported as a gain with
    the failing guards named."
  A guard item = one guard at one operating point on one cell set (per-source width: also one source). Here the kinds
  are width_pooled, width_source, false_alarm, inactive, miou; only width_source items allow the carry.

  python c3swad_verdict.py --read /home/noob/work/bench_reads/c3swad --probes /home/noob/work/bench_relay/c3swad \
      --out /home/noob/work/bench_reads/c3swad/verdict.txt
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

BASE, PRIMARY, SECONDARY = "PF", "SWADBN", "SWAD"
OPS = ("OP-A", "OP-W")
BAND = (0.85, 1.15)
FA_MAX = 1.5
MIN_SRC = 40


def f(x, nd=4):
    return "n/a" if x is None else f"{x:+.{nd}f}" if nd < 0 else f"{x:.{nd}f}"


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
            r = a / b if a is not None and b else None
            ok = r is not None and BAND[0] <= r <= BAND[1]
            kind = "width_pooled" if sn == "all" else "width_source"
            out.append((ok, kind, f"{kind} {sn} {op} {tag}", f"{kind}\t{tag}\t{op}\t{sn} (n {g['n']}): width {a:.4f} / {b:.4f} = {f(r, 3)} (band {BAND[0]} to {BAND[1]})"))
        a, b = S[arm][op]["all"]["fa_px"]["mean"], S[BASE][op]["all"]["fa_px"]["mean"]
        ok = a is not None and b is not None and a <= FA_MAX * b
        out.append((ok, "false_alarm", f"false_alarm {op} {tag}", f"false_alarm\t{tag}\t{op}\tfalse crack px on crack-free cells {a:.0f} against {b:.0f}"
                    f" = {f(a / b if b else None, 2)} x (max {FA_MAX}); share of crack-free cells with >= 50 px "
                    f"{S[arm][op]['all']['fa_share50']['mean']:.4f} against {S[BASE][op]['all']['fa_share50']['mean']:.4f}"))
        for key, kind, name in (("inact_iou", "inactive", "inactive IoU"), ("miou_rob", "miou", "mIoU-R13")):
            v = C[op]["metrics"][key]
            ok = v["delta"] >= -M[key]
            out.append((ok, kind, f"{kind} {op} {tag}", f"{kind}\t{tag}\t{op}\t{name} {arm} - {BASE} = {v['delta']:+.4f} [{v['lo']:+.4f}, {v['hi']:+.4f}], "
                                       f"allowed drop {M[key]:.4f}"))
    return out


def per_seed(D: dict, arm: str, tag: str) -> list[str]:
    L = []
    T = D["per_seed"]
    for op in OPS:
        for key in ("relF1_2", "crack_iou", "miou_rob"):
            a, b = T[arm][op]["all"], T[BASE][op]["all"]
            seeds = sorted(set(a) & set(b), key=int)
            L.append(f"per_seed\t{tag}\t{op}\t{key}\t{arm} - {BASE}\t" + "\t".join(f"s{s} {a[s][key] - b[s][key]:+.4f}" for s in seeds))
    return L


def probes(root: Path) -> list[str]:
    rows = []
    for p in sorted(root.glob("*/experiments/*/enc_probe.jsonl")) + sorted(root.glob("*/enc_probe.jsonl")):
        last = None
        for line in p.read_text().splitlines():
            if line.strip():
                d = json.loads(line)
                if d.get("step") == 20000:
                    last = d
        if last:
            rows.append((p.parent.name, last["stages"]["layer3"]["cos"], last["stages"]["layer4"]["cos"]))
    L = [f"probe\t{n}\tlayer3 cos {a:.4f}\tlayer4 cos {b:.4f}" for n, a, b in rows]
    if rows:
        L.append(f"probe\tsummary\t{len(rows)} runs: layer3 cos {min(r[1] for r in rows):.3f} to {max(r[1] for r in rows):.3f}, "
                 f"layer4 cos {min(r[2] for r in rows):.3f} to {max(r[2] for r in rows):.3f}; "
                 f"layer4 below 0.8 in {sum(r[2] < 0.8 for r in rows)} of {len(rows)}, layer3 below 0.8 in {sum(r[1] < 0.8 for r in rows)}")
    else:
        L.append(f"probe\tno enc_probe.jsonl with a step-20000 line under {root}")
    return L


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--read", required=True, help="output folder of run_read_c3swad.sh")
    ap.add_argument("--probes", default=None, help="folder searched for */experiments/*/enc_probe.jsonl (the c3swad relay)")
    ap.add_argument("--out", required=True)
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
        for arm in (BASE, PRIMARY, SECONDARY):
            assert arm in D["summary"], f"arm {arm} missing"
    L = [f"# c3swad verdict from {a.read}/read/read.json (read tool {doc['tool_md5'][:8]}; A/A {doc['aa_spec']}; "
         f"groups {doc['groups_md5'][:8]}); rule: LAUNCH_REQUEST_c3swad.md section 7; script {Path(__file__).name}"]
    res = {}
    for arm, role in ((PRIMARY, "primary, swad_bn"), (SECONDARY, "declared secondary, swad")):
        H, G = [], []
        for tag, D in sets:
            H += headline(D, arm, tag)
            G += guards(D, arm, tag)
        res[arm] = {"headline": all(ok for ok, _ in H), "fails": [(k, lab) for ok, k, lab, _ in G if not ok]}
        L.append(f"\n## {arm} ({role})")
        L += [f"{'PASS' if ok else 'FAIL'}\t{t}" for ok, t in H]
        L += [f"{'PASS' if ok else 'FAIL'}\t{t}" for ok, _, _, t in G]
        L.append(f"=> {arm}: headline {'PASS' if res[arm]['headline'] else 'FAIL'}; failing guard items {len(res[arm]['fails'])}"
                 + (": " + "; ".join(lab for _, lab in res[arm]["fails"]) if res[arm]["fails"] else ""))
    p, s = res[PRIMARY], res[SECONDARY]
    only_src = bool(p["fails"]) and all(k == "width_source" for k, _ in p["fails"])
    named = "; ".join(lab for _, lab in p["fails"])
    if p["headline"] and not p["fails"]:
        v = "CONFIRMED: the primary readout swad_bn passes the headline at both operating points and every guard."
    elif p["headline"] and only_src and s["headline"] and not s["fails"]:
        v = ("CONFIRMED, CARRIED BY THE DECLARED SECONDARY READOUT swad: swad_bn passes the headline and every failing guard "
             f"item of swad_bn is a per-source width ({named}); swad passes the headline at both operating points and "
             "every guard on both cell sets.")
    elif not p["headline"]:
        v = "NOT CONFIRMED (no confirmed gain): the primary readout swad_bn does not pass the headline."
    else:
        why = ("a failing guard item of swad_bn is not a per-source width" if not only_src else
               "swad does not pass " + " and ".join(x for x in (None if s["headline"] else "the headline",
               "every guard (" + "; ".join(lab for _, lab in s["fails"]) + ")" if s["fails"] else None) if x))
        v = (f"NOT CONFIRMED, reported as a gain with the failing guards named: swad_bn passes the headline; failing guard "
             f"items of swad_bn: {named}. No carry by swad: {why}.")
    L.append(f"\n## verdict\n{v}")
    L.append("\n## beside the verdict: per-seed differences (pooled out-of-fold value of the seed, arm minus PF of the same seed)")
    for arm in (PRIMARY, SECONDARY):
        for tag, D in sets:
            L += per_seed(D, arm, tag)
    for tag, D in sets:
        L.append(f"A/A\t{tag}\t" + "; ".join(f"{k} delta {D['aa']['OP-A']['metrics'][k]['delta']:+.4f} SE {D['aa']['OP-A']['metrics'][k]['se']:.4f} M {D['M'][k]:.4f}"
                                             for k in ("relF1_2", "crack_iou", "inact_iou", "miou_rob")))
    if a.probes:
        L.append("\n## beside the verdict: encoder cosine to the ImageNet start at step 20000 (enc_probe.jsonl of each swad run)")
        L += probes(Path(a.probes))
    out.write_text("\n".join(L) + "\n")
    print(f"wrote {out} ({len(L)} lines): {v[:60]}")


if __name__ == "__main__":
    main()
