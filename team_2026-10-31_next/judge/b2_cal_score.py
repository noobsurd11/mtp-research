"""judge b2_cal_score (2 Nov 2026): scores one rater's calibration marks per ideas/b2_agent_marking_prereg.md v2.1 (md5 dc84975b) §5-6.
Written and md5-logged BEFORE any mark exists. Reads: marks TSV (id, mark, note), judge/b2_key/key_cal.tsv, results/b6/b6_folds.tsv
(part A crack px, house masks_escdd whole crop), raw E-SCDD _rf masks (part B, whole crop: crack class 14 >= 20 px, scuff class 25 >= 1 px).
Rule (unsure = negative):
  A (40 CSIR train, crack+ = crack|both vs crack >= 100 px / 0 px): sens >= 0.70 AND spec >= 0.70 AND bootstrap 95% lower bound of
    balanced accuracy > 0.5 (2,000 cell resamples, random.Random(1); resample within the 40, BA from each resample; a resample
    lacking a class is redrawn);
  B (32 Hanifi, scuff+ = scuff|both vs class 25 >= 1 px): sens >= 0.50 AND spec >= 0.70 (weak gate);
  unsure <= 14 of 72.
Reported only: part-B crack+ / either+ 2x2, sens / spec with Wilson 95% CIs, kappa; part-A Wilson CIs; unsure share; marks distribution.
Output: full report to judge only; the rater gets PASS / FAIL.
Usage: python b2_cal_score.py MARKS.tsv KEY_CAL.tsv B6_FOLDS.tsv ESCDD_DIR OUT.txt"""
import glob, math, os, random, sys
import numpy as np
from PIL import Image

MK, KEY, FOLDS, ESC, OUT = sys.argv[1:6]
key = {l.split("\t")[0]: l.rstrip("\n").split("\t")[1:] for l in list(open(KEY))[1:] if l.strip()}
marks = {}
for l in open(MK):
    x = l.rstrip("\n").split("\t")
    if not x[0] or x[0] == "id":
        continue
    assert x[0] in key and x[0] not in marks, ("bad / duplicate id", x[0])
    m = x[1].strip().lower(); assert m in ("scuff", "crack", "both", "neither", "unsure"), (x[0], m)
    marks[x[0]] = m
assert set(marks) == set(key), ("missing ids", sorted(set(key) - set(marks))[:5])
cpx = {r[0]: int(r[5]) for r in (l.rstrip("\n").split("\t") for l in list(open(FOLDS))[1:])}
lab = {}
for i, (stem, kind) in key.items():
    if kind.startswith("csir"):
        n = cpx[stem]; assert (kind == "csir_crack" and n >= 100) or (kind == "csir_nocrack" and n == 0), (i, stem, n)
        lab[i] = {"part": "A", "crack": n >= 100}
    else:
        f = glob.glob(os.path.join(ESC, "el_masks_*", f"{stem}_rf.png")); assert len(f) == 1, (stem, f)
        m = np.array(Image.open(f[0]))
        c, s = int((m == 14).sum()) >= 20, int((m == 25).sum()) >= 1
        lab[i] = {"part": "B", "crack": c, "scuff": s, "either": c or s}
pos = {"crack": ("crack", "both"), "scuff": ("scuff", "both"), "either": ("crack", "scuff", "both")}


def wilson(k, n, z=1.96):
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n; d = 1 + z * z / n; c = p + z * z / (2 * n); h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - h) / d, (c + h) / d)


def table(ids, cls):
    tp = sum(lab[i][cls] and marks[i] in pos[cls] for i in ids); fn = sum(lab[i][cls] and marks[i] not in pos[cls] for i in ids)
    fp = sum(not lab[i][cls] and marks[i] in pos[cls] for i in ids); tn = sum(not lab[i][cls] and marks[i] not in pos[cls] for i in ids)
    n = tp + fn + fp + tn; po = (tp + tn) / n; pe = ((tp + fn) * (tp + fp) + (fp + tn) * (fn + tn)) / (n * n)
    return dict(tp=tp, fn=fn, fp=fp, tn=tn, sens=tp / max(tp + fn, 1), spec=tn / max(tn + fp, 1),
                sens_ci=wilson(tp, tp + fn), spec_ci=wilson(tn, tn + fp), kappa=(po - pe) / (1 - pe) if pe < 1 else float("nan"))


A = sorted(i for i in lab if lab[i]["part"] == "A"); B = sorted(i for i in lab if lab[i]["part"] == "B")
assert len(A) == 40 and len(B) == 32
tA = table(A, "crack")
rng = random.Random(1); bas = []
while len(bas) < 2000:
    s = [A[rng.randrange(len(A))] for _ in A]
    P = [i for i in s if lab[i]["crack"]]; N = [i for i in s if not lab[i]["crack"]]
    if not P or not N:
        continue
    bas.append((sum(marks[i] in pos["crack"] for i in P) / len(P) + sum(marks[i] not in pos["crack"] for i in N) / len(N)) / 2)
ba_lo = sorted(bas)[int(0.025 * len(bas))]
tBs = table(B, "scuff"); unsure = sum(m == "unsure" for m in marks.values())
gA = tA["sens"] >= 0.70 and tA["spec"] >= 0.70 and ba_lo > 0.5
gB = tBs["sens"] >= 0.50 and tBs["spec"] >= 0.70
gU = unsure <= 14
verdict = "PASS" if (gA and gB and gU) else "FAIL"
L = [f"marks {MK} | n {len(marks)} | distribution " + str({k: sum(v == k for v in marks.values()) for k in ('crack', 'scuff', 'both', 'neither', 'unsure')}),
     f"A crack+ (40): {tA} | BA bootstrap 95% lo {ba_lo:.3f} -> gate A {'PASS' if gA else 'FAIL'}",
     f"B scuff+ (32): {tBs} -> gate B {'PASS' if gB else 'FAIL'}",
     f"unsure {unsure} / 72 -> {'PASS' if gU else 'FAIL'}",
     f"B crack+ (reported): {table(B, 'crack')}", f"B either+ (reported): {table(B, 'either')}",
     f"VERDICT {verdict}"]
open(OUT, "w").write("\n".join(L) + "\n"); print(f"VERDICT {verdict}")
