"""Synthetic test of score.py. Never reads the real key: builds synthetic keys and rater files in a scratch folder.
Checks: Fleiss kappa against the published example (Fleiss 1971 data as given on Wikipedia, kappa 0.210); the A/B mapping;
parsing rules (first valid line counts, invalid / unknown / missing lines); perfect raters; raters with known error rates
(per-rater and majority sensitivity / specificity, Rogan-Gladen recovery of a known prevalence); random raters (kappa ~ 0,
gates fail). Usage: nice -n 19 python -I test_score.py [--scratch DIR]"""
from __future__ import annotations

import argparse
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402

import score as S  # noqa: E402

COLS = ["id", "set", "cls", "type", "truth", "label_is", "stem", "source", "group", "bbox", "window_y0x0side", "px", "z",
        "kind", "replicated_w1g", "classes_under", "cand_row", "plant", "side", "plant_info"]


def synth_key(path, n_cal_cls, n_cand_cls, prev, rs):
    """Synthetic key: per class n_cal_cls calibration items (half label_error) and n_cand_cls candidates with a hidden truth
    (label_error with probability prev[cls]); candidates spread over cells of 1 to 4 candidates."""
    rows, hidden = [], {}
    k = 0
    for cls in ("crack", "inact"):
        for i in range(n_cal_cls):
            k += 1
            pid = f"C{k:05d}"
            side = "L" if i % 2 == 0 else "C"
            rows.append({"id": pid, "set": "cal", "cls": cls, "type": "MC", "truth": "label_error" if side == "L"
                         else "label_correct", "label_is": rs.choice("AB"), "stem": f"SYN_{k:05d}", "source": "SYN",
                         "group": "g", "bbox": "0,0,9,9", "window_y0x0side": "0,0,96", "px": "", "z": "", "kind": "",
                         "replicated_w1g": "", "classes_under": "", "cand_row": "", "plant": "DEL", "side": side,
                         "plant_info": "{}"})
        cell = 0
        left = 0
        for i in range(n_cand_cls):
            if left == 0:
                cell += 1
                left = rs.randint(1, 4)
            left -= 1
            k += 1
            pid = f"K{k:05d}"
            rows.append({"id": pid, "set": "cand", "cls": cls, "type": "MC" if cls == "crack" else "SI",
                         "truth": "NA", "label_is": rs.choice("AB"), "stem": f"SYN_{cls}_{cell:04d}", "source": "SYN",
                         "group": "g", "bbox": "0,0,9,9", "window_y0x0side": "0,0,96", "px": str(rs.randint(20, 400)),
                         "z": "-1", "kind": "whole", "replicated_w1g": "1", "classes_under": "", "cand_row": str(i),
                         "plant": "", "side": "", "plant_info": ""})
            hidden[pid] = "label_error" if rs.random() < prev[cls] else rs.choice(["convention", "ambiguous", "model_error"])
    with open(path, "w") as f:
        f.write("# synthetic key\n" + "\t".join(COLS) + "\n")
        for r in rows:
            f.write("\t".join(r[c] for c in COLS) + "\n")
    return {r["id"]: r for r in rows}, hidden


def answer_for(cat, label_is):
    """The rater line that maps to the given category."""
    other = "B" if label_is == "A" else "A"
    return {"label_error": other, "model_error": label_is, "convention": "CONVENTION", "ambiguous": "AMBIGUOUS",
            "unverifiable": "UNREADABLE"}[cat]


def simulate(path, key, hidden, sens, spec, rs, mode="noisy"):
    """mode noisy: on a true label_error the rater says label_error with prob sens, else ambiguous; on a true
    non-label-error it says label_error with prob 1 - spec, else the true category (or model_error on calibration)."""
    with open(path, "w") as f:
        f.write("# synthetic rater\n")
        for pid, r in key.items():
            truth = r["truth"] if r["set"] == "cal" else hidden[pid]
            truth = "model_error" if truth == "label_correct" else truth
            if mode == "random":
                cat = rs.choice(S.CATS)
            elif truth == "label_error":
                cat = "label_error" if rs.random() < sens else "ambiguous"
            else:
                cat = "label_error" if rs.random() > spec else truth
            f.write(f"{pid}\t{answer_for(cat, r['label_is'])}\t{'high' if rs.random() < 0.7 else 'low'}\tsynthetic\n")


def run(scr, n_cal, n_cand, prev, sens, spec, seed, mode="noisy", boot=300):
    rs = random.Random(seed)
    kp = os.path.join(scr, f"key_{seed}.tsv")
    key, hidden = synth_key(kp, n_cal, n_cand, prev, rs)
    paths = []
    for r in range(3):
        p = os.path.join(scr, f"r{r + 1}_{seed}.tsv")
        simulate(p, key, hidden, sens, spec, rs, mode)
        paths.append(p)
    gates = S.main(["--key", kp, "--ratings", *paths, "--out", os.path.join(scr, f"out_{seed}"), "--boot", str(boot)])
    return key, hidden, gates, paths


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scratch", default="/home/noob/work/bench_int_io/rater/test_score")
    a = ap.parse_args()
    os.makedirs(a.scratch, exist_ok=True)
    import contextlib
    import io
    quiet = contextlib.redirect_stdout(io.StringIO())
    # 1. Fleiss kappa, published example: 10 subjects, 14 raters, 5 categories -> 0.210
    M = [[0, 0, 0, 0, 14], [0, 2, 6, 4, 2], [0, 0, 3, 5, 6], [0, 3, 9, 2, 0], [2, 2, 8, 1, 1], [7, 7, 0, 0, 0],
         [3, 2, 6, 3, 0], [2, 5, 3, 2, 2], [6, 5, 2, 1, 0], [0, 2, 2, 3, 7]]
    k = S.fleiss_kappa(M)
    assert abs(k - 0.210) < 0.0005, k
    assert S.fleiss_kappa([[3, 0], [3, 0]]) == 1.0
    assert abs(S.fleiss_kappa([[3, 0], [0, 3]]) - 1.0) < 1e-12
    print(f"ok 1 Fleiss kappa example {k:.4f} (published 0.210)")
    # 2. mapping
    assert S.map_verdict("A", "A") == "model_error" and S.map_verdict("B", "A") == "label_error"
    assert S.map_verdict("A", "B") == "label_error" and S.map_verdict("B", "B") == "model_error"
    assert S.map_verdict("CONVENTION", "A") == "convention" and S.map_verdict("UNREADABLE", "B") == "unverifiable"
    assert S.majority(["label_error", "label_error", "ambiguous"]) == "label_error"
    assert S.majority(["label_error", "convention", "ambiguous"]) == "no_majority"
    lo, hi = S.wilson(17, 20)
    assert abs(lo - 0.640) < 0.002 and abs(hi - 0.948) < 0.002, (lo, hi)
    assert abs(S.rogan_gladen(0.5, 0.8, 0.9) - (0.5 + 0.9 - 1) / 0.7) < 1e-12
    print("ok 2 A/B mapping, majority, Wilson (17/20 -> [0.640, 0.948]), Rogan-Gladen")
    # 3. parsing rules
    ids = {"AAAAA", "BBBBB", "CCCCC", "DDDDD"}
    p = os.path.join(a.scratch, "parse.tsv")
    open(p, "w").write("# comment\nAAAAA\tA\thigh\tfirst\nAAAAA\tB\tlow\trepeat ignored\nbbbbb\tbogus\thigh\tx\n"
                       "BBBBB\tconvention\tLOW\tvalid after invalid\nZZZZZ\tA\thigh\tunknown\nCCCCC  AMBIGUOUS  high  "
                       "space separated note\n")
    got, st, unk = S.read_ratings(p, ids)
    assert got["AAAAA"][0] == "A" and got["BBBBB"] == ("CONVENTION", "low", "valid after invalid"), got
    assert got["CCCCC"][0] == "AMBIGUOUS" and "DDDDD" not in got
    assert st["repeat_ignored"] == 1 and st["invalid_verdict"] == 1 and st["unknown_id"] == 1 and st["missing"] == 1, st
    print("ok 3 parsing: first valid line counts, repeats / invalid / unknown counted, missing counted")
    # 4. perfect raters on a key shaped like the real one (36 + 24 calibration, 78 + 46 candidates)
    rs = random.Random(7)
    kp = os.path.join(a.scratch, "key_perfect.tsv")
    key, hidden = synth_key(kp, 30, 62, {"crack": 0.4, "inact": 0.4}, rs)
    paths = []
    for r in range(3):
        pp = os.path.join(a.scratch, f"perfect_r{r + 1}.tsv")
        simulate(pp, key, hidden, 1.0, 1.0, rs)
        paths.append(pp)
    with quiet:
        g = S.main(["--key", kp, "--ratings", *paths, "--out", os.path.join(a.scratch, "out_perfect"), "--boot", "300"])
    for cls in ("crack", "inact"):
        assert g[cls]["sens"] == 1.0 and g[cls]["spec"] == 1.0 and g[cls]["kappa"] == 1.0, g[cls]
        assert all(g[cls][x] for x in ("G1", "G2", "G3", "G4"))
        true_share = np.mean([hidden[p] == "label_error" for p in hidden if key[p]["cls"] == cls])
        assert abs(g[cls]["share"] - true_share) < 1e-12 and abs(g[cls]["rg"] - true_share) < 1e-12
    print("ok 4 perfect raters: sens = spec = 1, kappa 1, all gates pass, share = hidden truth")
    # 5. noisy raters with known rates on a large synthetic set: estimates converge
    with quiet:
        key, hidden, g, _ = run(a.scratch, 3000, 3000, {"crack": 0.3, "inact": 0.6}, 0.8, 0.9, seed=11, boot=200)
    maj_sens = 0.8 ** 3 + 3 * 0.8 ** 2 * 0.2           # P(>= 2 of 3 say label_error | label error)
    maj_fpr = 0.1 ** 3 + 3 * 0.1 ** 2 * 0.9
    for cls, prev in (("crack", 0.3), ("inact", 0.6)):
        assert abs(g[cls]["sens"] - maj_sens) < 0.03, (cls, g[cls]["sens"], maj_sens)
        assert abs(g[cls]["spec"] - (1 - maj_fpr)) < 0.02, (cls, g[cls]["spec"])
        assert abs(g[cls]["rg"] - prev) < 0.04, (cls, g[cls]["rg"], prev)
        assert g[cls]["rg_ci"][0] < prev < g[cls]["rg_ci"][1], (cls, g[cls]["rg_ci"])
    print(f"ok 5 known rates (rater sens 0.8, spec 0.9): majority sens {g['crack']['sens']:.3f} (expected {maj_sens:.3f}), "
          f"spec {g['crack']['spec']:.3f} (expected {1 - maj_fpr:.3f}); corrected share crack {g['crack']['rg']:.3f} "
          f"(true 0.3), inactive {g['inact']['rg']:.3f} (true 0.6), CIs cover the truth")
    # 6. random raters: kappa ~ 0, gates fail
    with quiet:
        _, _, g, _ = run(a.scratch, 1000, 1000, {"crack": 0.4, "inact": 0.4}, 0, 0, seed=13, mode="random", boot=200)
    for cls in ("crack", "inact"):
        assert abs(g[cls]["kappa"]) < 0.05, g[cls]["kappa"]
        assert not (g[cls]["G1"] and g[cls]["G2"] and g[cls]["G4"]), g[cls]
    print(f"ok 6 random raters: candidate kappa {g['crack']['kappa']:.3f} / {g['inact']['kappa']:.3f}, gates fail")
    # 7. realistic size, decent raters: report renders, decision lines present
    with quiet:
        _, _, g, _ = run(a.scratch, 30, 62, {"crack": 0.4, "inact": 0.3}, 0.85, 0.92, seed=17, boot=500)
    rep = open(os.path.join(a.scratch, "out_17", "score_report.txt")).read()
    assert "Pre-registered decision" in rep and rep.count("STAYS SUGGESTIVE") + rep.count("MEASURED") == 2
    print("ok 7 realistic-size run: report written with one decision per class")
    # 8. a rater missing > 5% of the panels makes the run invalid
    rs = random.Random(19)
    kp = os.path.join(a.scratch, "key_missing.tsv")
    key, hidden = synth_key(kp, 30, 62, {"crack": 0.4, "inact": 0.4}, rs)
    paths = []
    for r in range(3):
        pp = os.path.join(a.scratch, f"missing_r{r + 1}.tsv")
        simulate(pp, key, hidden, 0.9, 0.9, rs)
        paths.append(pp)
    lines = open(paths[0]).read().splitlines()
    open(paths[0], "w").write("\n".join(lines[:150]) + "\n")
    with quiet:
        S.main(["--key", kp, "--ratings", *paths, "--out", os.path.join(a.scratch, "out_missing"), "--boot", "100"])
    assert "INVALID RUN" in open(os.path.join(a.scratch, "out_missing", "score_report.txt")).read()
    print("ok 8 a rater missing > 5% of panels flags the run invalid")
    print("ALL SCORER TESTS PASSED")


if __name__ == "__main__":
    main()
