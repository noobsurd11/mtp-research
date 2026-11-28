"""x4: screen printout for arm(s) against a base (default COMBO = HRNet-W18 U-Net++ PF + SWAD, swad readout, seeds 5, 6) from
a finished read_x4.py folder (<read>/read/read.json). It computes nothing new: every number is taken from read.json. The
headline and guard items are the functions of c3x_verdict.py (faa2a961, copied unchanged next to this file) with the
comparator name set to --base; per-seed lines likewise.

Per arm X, on the 532 cells and the 416 clean cells (score_exclude_v3), at OP-A and OP-W:
  headline  crack relF1@2 X - base: delta >= M and CI low > 0 (M = max(0.01, 2 SE) of the A/A in the same read, per cell set)
  guards    width ratio pooled and per source (>= 40 cells) in 0.85 to 1.15; false crack px on crack-free cells <= 1.5 x base;
            inactive IoU delta >= -M(inactive); mIoU-R13 delta >= -M(mIoU-R13)
  printed   relP@2, relR@2, strict crack IoU, inactive IoU, mIoU-R13 levels and deltas with 95% intervals; per-seed deltas
Screen word (PROTOCOL v1.0 s5.4 screen row, read against the comparator; 2 seeds screen, 5 seeds confirm):
  SCREEN PASS                       headline at all four values and no failing guard item
  SCREEN PASS, FLAGGED              headline passes; the only failing items are per-source widths (re-check at 5 seeds)
  HEADLINE PASS, GUARDS FAIL        headline passes; other guard items fail (named)
  SCREEN FAIL (NO LOSS | LOSS)      headline fails; NO LOSS if CI low > -M at all four values
A 2-seed screen is never a result; a pass only promotes to a 5-seed confirmation.
Usage: python x4_verdict.py --read <read_x4 out> --base COMBO --arms X[,Y] --out <file>   (refuses to overwrite)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import c3x_verdict as cv  # noqa: E402  (unchanged copy; only its module constant BASE is set below)

LEVELS = (("relF1_2", "relF1@2"), ("relP2", "relP@2"), ("relR2", "relR@2"), ("crack_iou", "strict crack IoU"),
          ("inact_iou", "inactive IoU"), ("miou_rob", "mIoU-R13"), ("fa_px", "false crack px (crack-free)"),
          ("width_ratio", "width ratio"))
DELTAS = ("relF1_2", "relP2", "relR2", "crack_iou", "inact_iou", "miou_rob")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--read", required=True)
    ap.add_argument("--base", default="COMBO")
    ap.add_argument("--arms", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--header", default="")
    ap.add_argument("--stage", default="", help="P: also print the stage-P promotion rule of PATHFINDER_RULE.md (26474b34)")
    a = ap.parse_args()
    out = Path(a.out)
    if out.exists():
        sys.exit(f"refuse: {out} exists")
    doc = json.loads((Path(a.read) / "read" / "read.json").read_text())
    xk = [k for k in doc if k.startswith("x") and k[1:].isdigit()]
    if len(xk) != 1:
        sys.exit(f"refuse: expected one clean-cell block x<n> in read.json, found {xk}")
    sets = [(f"{doc['n_stems']} cells", doc), (f"{xk[0][1:]} clean cells", doc[xk[0]])]
    cv.BASE = a.base
    arms = a.arms.split(",")
    for tag, D in sets:
        for k in ("relF1_2", "inact_iou", "miou_rob"):
            if not cv.num_ok(D["M"].get(k) if D.get("M") else None):
                sys.exit(f"refuse: margin M({k}) of the {tag} block is undefined (A/A seeds missing?); no verdict written")
        for arm in arms:
            for op in cv.OPS:
                for k in ("relF1_2", "inact_iou", "miou_rob"):
                    v = D["contrasts"][f"{arm} - {a.base}"][op]["metrics"][k]
                    if not all(cv.num_ok(v.get(f)) for f in ("delta", "lo", "hi")):
                        sys.exit(f"refuse: {arm} - {a.base} {op} {k} has an undefined delta or CI end ({tag}); no verdict written")
    seeds = {arm: sorted({r["seed"] for r in doc["runs"] if r["arm"] == arm}) for arm in arms + [a.base]}
    L = ([a.header] if a.header else []) + [f"# x4 screen printout from {Path(a.read) / 'read' / 'read.json'} (tool {doc['tool_md5'][:8]}; A/A {doc['aa_spec']}; "
         f"groups {doc['groups_md5'][:8]}); base {a.base} seeds {seeds[a.base]}; script x4_verdict.py, guard code c3x_verdict.py",
         "# margins (A/A in this read, OP-A): " + "; ".join(
             f"{tag}: M relF1@2 {D['M']['relF1_2']:.4f} (A/A delta {D['aa']['OP-A']['metrics']['relF1_2']['delta']:+.4f}, "
             f"SE {D['aa']['OP-A']['metrics']['relF1_2']['se']:.4f}), M inactive {D['M']['inact_iou']:.4f}, M mIoU-R13 "
             f"{D['M']['miou_rob']:.4f}" for tag, D in sets)]
    for arm in arms:
        L += ["", f"## {arm} (seeds {seeds[arm]}) against {a.base} (seeds {seeds[a.base]})"]
        hl, gd = [], []
        for tag, D in sets:
            for ok, text in cv.headline(D, arm, tag):
                hl.append(ok); L.append(("PASS" if ok else "FAIL") + "\t" + text)
        for tag, D in sets:
            for ok, kind, label, text in cv.guards(D, arm, tag):
                gd.append((ok, kind, label)); L.append(("PASS" if ok else "FAIL") + "\t" + text)
        L.append("# levels (mean over seeds, all cells of the set)")
        for tag, D in sets:
            S = D["summary"]
            for op in cv.OPS:
                L.append(f"level\t{tag}\t{op}\t" + "\t".join(
                    f"{lab} {cv.f(S[arm][op]['all'][k]['mean'])} / {cv.f(S[a.base][op]['all'][k]['mean'])}" for k, lab in LEVELS)
                    + f"\t({arm} / {a.base})")
        L.append("# deltas with 95% intervals (two-stage group bootstrap, 2,000 draws)")
        for tag, D in sets:
            for op in cv.OPS:
                C = D["contrasts"][f"{arm} - {a.base}"][op]["metrics"]
                L.append(f"delta\t{tag}\t{op}\t" + "\t".join(
                    f"{lab} {C[k]['delta']:+.4f} [{C[k]['lo']:+.4f}, {C[k]['hi']:+.4f}]" for k, lab in LEVELS if k in DELTAS))
        for tag, D in sets:
            L += cv.per_seed(D, arm, tag)
        fails = [lab for ok, kind, lab in gd if not ok]
        nonsrc = [lab for ok, kind, lab in gd if not ok and kind != "width_source"]
        if all(hl):
            word = "SCREEN PASS" if not fails else ("SCREEN PASS, FLAGGED (per-source width; re-check at 5 seeds)" if not nonsrc
                                                    else "HEADLINE PASS, GUARDS FAIL")
        else:
            lows = [D["contrasts"][f"{arm} - {a.base}"][op]["metrics"]["relF1_2"]["lo"] > -D["M"]["relF1_2"]
                    for tag, D in sets for op in cv.OPS]
            word = "SCREEN FAIL (" + ("NO LOSS" if all(lows) else "LOSS") + ")"
        if a.stage == "P":
            C = sets[0][1]["contrasts"][f"{arm} - {a.base}"]["OP-A"]["metrics"]
            dF, dP, dR, dI = (C[k]["delta"] for k in ("relF1_2", "relP2", "relR2", "inact_iou"))
            ca, cb, cc = dF >= 0.005, (dR >= 0.010 and dP >= -0.005), dI >= 0.030
            L.append(f"stageP\t{sets[0][0]}\tOP-A\trelF1@2 {dF:+.4f} (a: >= +0.005 {'yes' if ca else 'no'}); relR@2 {dR:+.4f} and relP@2 "
                     f"{dP:+.4f} (b: >= +0.010 and >= -0.005 {'yes' if cb else 'no'}); inactive IoU {dI:+.4f} (c: >= +0.030 {'yes' if cc else 'no'})")
            L.append(f"=> {arm}: STAGE P (PATHFINDER_RULE.md 26474b34): " + (
                "PROMOTE to stage S (" + ", ".join(x for x, y in (("a", ca), ("b", cb), ("c", cc)) if y) + ")" if (ca or cb or cc)
                else "pathfinder: not promoted") + " [descriptive, decides nothing about the method; the screen word below is printed only]")
        L.append(f"=> {arm}: {word}; headline items passing {sum(hl)} of {len(hl)}; failing guard items {len(fails)}"
                 + (": " + "; ".join(fails) if fails else ""))
    L.append("")
    L.append("Screen (2 seeds) is never a result; SCREEN PASS promotes to a 5-seed confirmation (PROTOCOL v1.0 s5.4).")
    text = "\n".join(L) + "\n"
    out.write_text(text)
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
