"""Scorer of the AI-rater check (PREREG.md section 6 and 7). Run only after the three rating files are final and their md5s are
logged, and after the key is unsealed (chmod 700 key). Reads the key and the rating files; writes a report and two tables.

Mapping of a rater's answer (the rater never knows which overlay is the label):
  A / B chosen and it is the label overlay        -> model_error  (label judged correct)
  A / B chosen and it is the consensus overlay    -> label_error
  CONVENTION -> convention; AMBIGUOUS -> ambiguous; UNREADABLE -> unverifiable; missing ID -> ambiguous (counted)
Calibration: positive = truth label_error; a rater (or the majority, >= 2 of 3) is positive when it answers label_error.
Every non-label_error answer (model_error, convention, ambiguous, unverifiable) counts as negative.

Usage: nice -n 19 python -I score.py --key ../key/key.tsv --ratings r1.tsv r2.tsv r3.tsv --out ../out
       [--visual ../../out/a_visual_check.tsv] [--boot 2000]"""
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import math
import os
import sys

import numpy as np

VERDICTS = ("A", "B", "CONVENTION", "AMBIGUOUS", "UNREADABLE")
CATS = ("label_error", "convention", "ambiguous", "unverifiable", "model_error")
CLASSES = ("crack", "inact")
FINDING = {"crack": "F5 (crack label errors)", "inact": "F4 (inactive label errors)"}
# pre-registered thresholds (PREREG.md section 7)
G1_SENS, G1_SPEC = 0.70, 0.80
G2_JLB = 0.30
G3_SENS, G3_SPEC, G3_MIN_RATERS = 0.60, 0.70, 2
G4_KAPPA = 0.40
MAX_MISSING = 0.05
SEED = 1


# ---------------------------------------------------------------- reading
def read_key(path):
    rows = [l for l in open(path) if not l.startswith("#")]
    key = {r["id"]: r for r in csv.DictReader(rows, delimiter="\t")}
    assert key, "empty key"
    return key


def read_ratings(path, ids):
    """First valid line per ID counts. Lines starting with '#' are comments. Returns ({id: (verdict, conf, note)}, stats)."""
    got, st = {}, collections.Counter()
    unknown = []
    for raw in open(path, encoding="utf-8", errors="replace"):
        line = raw.rstrip("\n")
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        st["lines"] += 1
        parts = line.split("\t") if "\t" in line else line.split(None, 3)
        pid = parts[0].strip().upper()
        verdict = parts[1].strip().upper() if len(parts) > 1 else ""
        conf = parts[2].strip().lower() if len(parts) > 2 else ""
        note = parts[3].strip() if len(parts) > 3 else ""
        if pid not in ids:
            st["unknown_id"] += 1
            unknown.append(pid)
            continue
        if verdict not in VERDICTS:
            st["invalid_verdict"] += 1
            continue
        if pid in got:
            st["repeat_ignored"] += 1
            continue
        if conf not in ("high", "low"):
            st["conf_missing"] += 1
        got[pid] = (verdict, conf, note)
    st["missing"] = len(set(ids) - set(got))
    return got, st, unknown[:10]


def md5(path):
    return hashlib.md5(open(path, "rb").read()).hexdigest()


# ---------------------------------------------------------------- mapping and statistics
def map_verdict(verdict, label_is):
    if verdict in ("A", "B"):
        return "model_error" if verdict == label_is else "label_error"
    return {"CONVENTION": "convention", "AMBIGUOUS": "ambiguous", "UNREADABLE": "unverifiable"}[verdict]


def majority(cats):
    c = collections.Counter(cats).most_common()
    return c[0][0] if c[0][1] >= 2 else "no_majority"


def wilson(k, n, z=1.96):
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (max(0.0, c - h), min(1.0, c + h))


def fleiss_kappa(counts):
    """counts: N x k array, counts[i, j] = raters putting item i in category j (same number of raters per item)."""
    M = np.asarray(counts, float)
    if M.size == 0:
        return float("nan")
    n = M.sum(1)
    assert np.all(n == n[0]) and n[0] >= 2, "Fleiss kappa needs the same number (>= 2) of raters per item"
    n = n[0]
    N = M.shape[0]
    p = M.sum(0) / (N * n)
    P = (np.sum(M * M, 1) - n) / (n * (n - 1))
    Pbar, Pe = P.mean(), np.sum(p * p)
    if abs(1 - Pe) < 1e-12:
        return 1.0 if abs(1 - Pbar) < 1e-12 else float("nan")
    return float((Pbar - Pe) / (1 - Pe))


def kappa_of(rows, cats=CATS, binary=False):
    """rows: list of per-item lists of mapped categories (one per rater)."""
    if not rows:
        return float("nan")
    if binary:
        M = [[sum(c == "label_error" for c in r), sum(c != "label_error" for c in r)] for r in rows]
    else:
        M = [[sum(c == k for c in r) for k in cats] for r in rows]
    return fleiss_kappa(M)


def sens_spec(pos_calls, neg_calls):
    """pos_calls: bool list (said label_error) on truth-positive items; neg_calls: the same on truth-negative items."""
    tp, n_pos = int(np.sum(pos_calls)), len(pos_calls)
    tn, n_neg = int(len(neg_calls) - np.sum(neg_calls)), len(neg_calls)
    return tp, n_pos, tn, n_neg


def rogan_gladen(p_obs, sens, spec):
    j = sens + spec - 1
    if j <= 0:
        return float("nan")
    return float(min(1.0, max(0.0, (p_obs + spec - 1) / j)))


# ---------------------------------------------------------------- scoring
def score(key, ratings, boot=2000, visual=None):
    """key: {id: row}; ratings: list of 3 dicts {id: (verdict, conf, note)}. Returns (report lines, cand rows, cal rows, gates)."""
    R = len(ratings)
    ids = sorted(key)
    mapped = {}
    for pid in ids:
        li = key[pid]["label_is"]
        mapped[pid] = [map_verdict(rt[pid][0], li) if pid in rt else "ambiguous" for rt in ratings]
    maj = {pid: majority(mapped[pid]) for pid in ids}
    majLE = {pid: sum(c == "label_error" for c in mapped[pid]) >= 2 for pid in ids}
    cal = [pid for pid in ids if key[pid]["set"] == "cal"]
    cand = [pid for pid in ids if key[pid]["set"] == "cand"]
    L = []
    P = L.append
    rng = np.random.default_rng(SEED)
    gates = {}
    P("## Calibration (truth known): sensitivity = label_error called on planted label errors; "
      "specificity = no label_error called where the label is correct")
    for cls in CLASSES + ("all",):
        cc = [p for p in cal if cls == "all" or key[p]["cls"] == cls]
        pos = [p for p in cc if key[p]["truth"] == "label_error"]
        neg = [p for p in cc if key[p]["truth"] == "label_correct"]
        P(f"\n### class {cls}: {len(pos)} planted label errors, {len(neg)} correct labels")
        indiv_ok = 0
        for r in range(R):
            tp, npos, tn, nneg = sens_spec([mapped[p][r] == "label_error" for p in pos],
                                           [mapped[p][r] == "label_error" for p in neg])
            se, sp = tp / max(npos, 1), tn / max(nneg, 1)
            side = sum(mapped[p][r] == "model_error" for p in neg)
            nonc = sum(mapped[p][r] in ("ambiguous", "unverifiable", "convention") for p in cc)
            ok = se >= G3_SENS and sp >= G3_SPEC
            indiv_ok += ok
            P(f"rater {r + 1}: sens {tp}/{npos} = {se:.3f} [{wilson(tp, npos)[0]:.3f}, {wilson(tp, npos)[1]:.3f}]  "
              f"spec {tn}/{nneg} = {sp:.3f} [{wilson(tn, nneg)[0]:.3f}, {wilson(tn, nneg)[1]:.3f}]  "
              f"label-side correct on correct labels {side}/{nneg}  non-committal {nonc}/{len(cc)}  "
              f"individual gate (sens >= {G3_SENS}, spec >= {G3_SPEC}) {'yes' if ok else 'no'}")
        tp, npos, tn, nneg = sens_spec([majLE[p] for p in pos], [majLE[p] for p in neg])
        se, sp = tp / max(npos, 1), tn / max(nneg, 1)
        js = []
        pa, na = np.array([majLE[p] for p in pos]), np.array([majLE[p] for p in neg])
        for _ in range(boot):
            bp = pa[rng.integers(0, len(pa), len(pa))] if len(pa) else pa
            bn = na[rng.integers(0, len(na), len(na))] if len(na) else na
            js.append(bp.mean() + (1 - bn.mean()) - 1 if len(pa) and len(na) else float("nan"))
        jlb = float(np.nanpercentile(js, 2.5)) if len(pa) and len(na) else float("nan")
        P(f"MAJORITY (>= 2 of {R}): sens {tp}/{npos} = {se:.3f} [{wilson(tp, npos)[0]:.3f}, {wilson(tp, npos)[1]:.3f}]  "
          f"spec {tn}/{nneg} = {sp:.3f} [{wilson(tn, nneg)[0]:.3f}, {wilson(tn, nneg)[1]:.3f}]  "
          f"Youden J {se + sp - 1:.3f}, bootstrap 95% lower bound {jlb:.3f}")
        P(f"Fleiss kappa on these calibration items: binary {kappa_of([mapped[p] for p in cc], binary=True):.3f}, "
          f"5 categories {kappa_of([mapped[p] for p in cc]):.3f}")
        # per plant type x side
        byp = collections.defaultdict(list)
        for p in cc:
            byp[(key[p]["cls"], key[p]["plant"], key[p]["side"], key[p]["truth"])].append(p)
        for k in sorted(byp):
            v = byp[k]
            hit = sum(majLE[p] == (k[3] == "label_error") for p in v)
            P(f"   {k[0]} {k[1]} planted in {'label' if k[2] == 'L' else 'consensus'} (truth {k[3]}): majority right "
              f"{hit}/{len(v)}; majority verdicts {dict(collections.Counter(maj[p] for p in v))}")
        if cls in CLASSES:
            gates[cls] = {"sens": se, "spec": sp, "jlb": jlb,
                          "indiv_ok": indiv_ok, "G1": se >= G1_SENS and sp >= G1_SPEC, "G2": jlb >= G2_JLB,
                          "G3": indiv_ok >= G3_MIN_RATERS}
    # ---- candidates
    P("\n## Candidates (124 image-supported audit candidates): majority verdict of 3 raters")
    cand_rows = []
    for p in cand:
        k = key[p]
        cand_rows.append({"id": p, "stem": k["stem"], "source": k["source"], "group": k["group"], "cls": k["cls"],
                          "type": k["type"], "kind": k["kind"], "px": int(k["px"]), "z": k["z"], "bbox": k["bbox"],
                          "cand_row": k["cand_row"], "label_is": k["label_is"],
                          **{f"r{r + 1}": mapped[p][r] for r in range(R)},
                          **{f"r{r + 1}_conf": (ratings[r][p][1] if p in ratings[r] else "") for r in range(R)},
                          "majority": maj[p], "majority_label_error": int(majLE[p])})
    for cls in CLASSES:
        cr = [c for c in cand_rows if c["cls"] == cls]
        kb = kappa_of([mapped[c["id"]] for c in cr], binary=True)
        k5 = kappa_of([mapped[c["id"]] for c in cr])
        gates[cls]["kappa"] = kb
        gates[cls]["G4"] = (not math.isnan(kb)) and kb >= G4_KAPPA
        n = len(cr)
        nle = sum(c["majority_label_error"] for c in cr)
        lo, hi = wilson(nle, n)
        pxle = sum(c["px"] for c in cr if c["majority_label_error"])
        pxall = sum(c["px"] for c in cr)
        P(f"\n### class {cls}: {n} candidates in {len({c['stem'] for c in cr})} cells; Fleiss kappa binary {kb:.3f}, "
          f"5 categories {k5:.3f}")
        P(f"majority verdicts: {dict(collections.Counter(c['majority'] for c in cr))}")
        P(f"label error (>= 2 of 3): {nle}/{n} = {nle / max(n, 1):.3f}, Wilson [{lo:.3f}, {hi:.3f}]; px-weighted "
          f"{pxle}/{pxall} = {pxle / max(pxall, 1):.3f}")
        # cell-cluster bootstrap of the share; joint bootstrap of the Rogan-Gladen corrected share
        cells = sorted({c["stem"] for c in cr})
        by_cell = {s: [c for c in cr if c["stem"] == s] for s in cells}
        cc = [p for p in cal if key[p]["cls"] == cls]
        pa = np.array([majLE[p] for p in cc if key[p]["truth"] == "label_error"])
        na = np.array([majLE[p] for p in cc if key[p]["truth"] == "label_correct"])
        se, sp = gates[cls]["sens"], gates[cls]["spec"]
        rg = rogan_gladen(nle / max(n, 1), se, sp)
        sh, rgs = [], []
        for _ in range(boot):
            pick = [cells[i] for i in rng.integers(0, len(cells), len(cells))]
            rows = [c for s in pick for c in by_cell[s]]
            ps = np.mean([c["majority_label_error"] for c in rows])
            sh.append(ps)
            bse = pa[rng.integers(0, len(pa), len(pa))].mean()
            bsp = 1 - na[rng.integers(0, len(na), len(na))].mean()
            rgs.append(rogan_gladen(ps, bse, bsp))
        slo, shi = np.percentile(sh, [2.5, 97.5])
        rgs = np.array(rgs, float)
        n_undef = int(np.isnan(rgs).sum())
        rlo, rhi = (np.nanpercentile(rgs, [2.5, 97.5]) if n_undef < len(rgs) else (float("nan"), float("nan")))
        gates[cls].update({"n": n, "nle": nle, "share": nle / max(n, 1), "share_ci": (slo, shi), "rg": rg,
                           "rg_ci": (float(rlo), float(rhi)), "rg_undefined_draws": n_undef})
        P(f"cell-cluster bootstrap 95% CI of the share: [{slo:.3f}, {shi:.3f}]")
        P(f"Rogan-Gladen share corrected for rater sens / spec: {rg:.3f}, joint bootstrap 95% CI [{rlo:.3f}, {rhi:.3f}] "
          f"({n_undef} of {boot} draws undefined, J <= 0)")
        for t in sorted({c["type"] for c in cr}):
            v = [c for c in cr if c["type"] == t]
            k_ = sum(c["majority_label_error"] for c in v)
            P(f"   type {t}: {k_}/{len(v)} label error, Wilson [{wilson(k_, len(v))[0]:.3f}, {wilson(k_, len(v))[1]:.3f}]; "
              f"verdicts {dict(collections.Counter(c['majority'] for c in v))}")
        for so in sorted({c["source"] for c in cr}):
            v = [c for c in cr if c["source"] == so]
            P(f"   source {so}: {sum(c['majority_label_error'] for c in v)}/{len(v)} label error; "
              f"verdicts {dict(collections.Counter(c['majority'] for c in v))}")
    # ---- decision (PREREG section 7)
    P("\n## Pre-registered decision")
    for cls in CLASSES:
        g = gates[cls]
        ok = g["G1"] and g["G2"] and g["G3"] and g["G4"]
        P(f"{FINDING[cls]}: G1 majority sens {g['sens']:.3f} >= {G1_SENS} and spec {g['spec']:.3f} >= {G1_SPEC}: "
          f"{'pass' if g['G1'] else 'FAIL'}; G2 J lower bound {g['jlb']:.3f} >= {G2_JLB}: {'pass' if g['G2'] else 'FAIL'}; "
          f"G3 raters passing alone {g['indiv_ok']} >= {G3_MIN_RATERS}: {'pass' if g['G3'] else 'FAIL'}; "
          f"G4 candidate kappa {g['kappa']:.3f} >= {G4_KAPPA}: {'pass' if g['G4'] else 'FAIL'}")
        if not ok:
            P(f"  -> raters not trusted for {cls}: {FINDING[cls]} STAYS SUGGESTIVE. The verdict counts above are "
              f"uncalibrated rater opinion (S) and may only be cited as such.")
            continue
        lo, hi = g["rg_ci"]
        if not (lo > 0):
            claim = "no measurable excess of label-error calls over the raters' false-positive rate"
        elif lo > 0.5:
            claim = "MOST image-supported candidates are label errors"
        elif hi < 0.5:
            claim = "label errors exist but are a MINORITY of the image-supported candidates"
        else:
            claim = "label errors exist; whether they are most of the candidates is undetermined"
        P(f"  -> {FINDING[cls]} MEASURED: {g['nle']}/{g['n']} candidates label error by majority "
          f"(share {g['share']:.3f}, cell-bootstrap [{g['share_ci'][0]:.3f}, {g['share_ci'][1]:.3f}]); corrected "
          f"{g['rg']:.3f} [{lo:.3f}, {hi:.3f}]. Pre-registered reading: {claim}.")
    # ---- descriptive: the auditor's one-look verdicts
    if visual:
        vrows = [r for r in csv.DictReader([l for l in open(visual) if not l.startswith("#")], delimiter="\t")]
        P("\n## Descriptive: the auditor's one non-expert look (out/a_visual_check.tsv) vs the rater majority "
          "(matched on stem, type, px; only rated, image-supported candidates)")
        tab = collections.Counter()
        for v in vrows:
            m = [c for c in cand_rows if c["stem"] == v["stem"] and c["type"] == v["type"] and str(c["px"]) == v["px"]]
            if len(m) == 1:
                tab[(v["verdict"], m[0]["majority"])] += 1
        for k, n in sorted(tab.items()):
            P(f"   auditor {k[0]:<20} raters {k[1]:<14} {n}")
        P(f"   matched {sum(tab.values())} of {len(vrows)} auditor rows (the rest are unsupported candidates, not rated)")
    cal_rows = [{"id": p, "cls": key[p]["cls"], "plant": key[p]["plant"], "side": key[p]["side"], "type": key[p]["type"],
                 "truth": key[p]["truth"], "label_is": key[p]["label_is"], "stem": key[p]["stem"],
                 **{f"r{r + 1}": mapped[p][r] for r in range(R)}, "majority": maj[p],
                 "majority_label_error": int(majLE[p])} for p in cal]
    return L, cand_rows, cal_rows, gates


def write_tsv(path, rows):
    if not rows:
        return
    with open(path, "w") as f:
        f.write("\t".join(rows[0]) + "\n")
        for r in rows:
            f.write("\t".join(str(v) for v in r.values()) + "\n")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--key", required=True)
    ap.add_argument("--ratings", nargs=3, required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--visual", default=None)
    ap.add_argument("--boot", type=int, default=2000)
    a = ap.parse_args(argv)
    key = read_key(a.key)
    ids = set(key)
    ratings, head = [], []
    head.append(f"# AI-rater check score report. key md5 {md5(a.key)}")
    valid = True
    for k, path in enumerate(a.ratings, 1):
        got, st, unk = read_ratings(path, ids)
        ratings.append(got)
        miss = st["missing"] / len(ids)
        head.append(f"rater {k}: {path} md5 {md5(path)}; lines {st['lines']}, rated {len(got)}/{len(ids)}, missing "
                    f"{st['missing']} ({miss:.1%}, counted as AMBIGUOUS), invalid verdict {st['invalid_verdict']}, "
                    f"repeats ignored {st['repeat_ignored']}, unknown IDs {st['unknown_id']} {unk}, "
                    f"confidence missing {st['conf_missing']}")
        if miss > MAX_MISSING:
            valid = False
            head.append(f"  !! rater {k} misses more than {MAX_MISSING:.0%} of the panels: PREREG section 4 says this rater "
                        f"must be replaced BEFORE the key is unsealed; the scores below are not valid.")
    L, cand_rows, cal_rows, gates = score(key, ratings, a.boot, a.visual)
    os.makedirs(a.out, exist_ok=True)
    text = "\n".join(head + ([""] if valid else ["", "!! INVALID RUN (see above)", ""]) + L) + "\n"
    open(os.path.join(a.out, "score_report.txt"), "w").write(text)
    write_tsv(os.path.join(a.out, "candidate_verdicts.tsv"), cand_rows)
    write_tsv(os.path.join(a.out, "calibration_items.tsv"), cal_rows)
    print(text)
    return gates


if __name__ == "__main__":
    sys.exit(0 if main() is not None else 1)
