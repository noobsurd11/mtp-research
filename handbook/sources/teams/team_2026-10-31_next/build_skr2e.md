# SKR2E build (runner, 2 Nov 2026; for coach's review and APPROVED)

Protocol: `protocol_SKR2E.md` v1 LOCKED 21:59 (md5 cbc3e015). Inference only, gaint CPU fp32, no training. E1 opening #6. Nothing has run on gaint. No file is staged there yet: I copy after your review, with md5s checked on both ends. Tags: E = measured (file named), S = judgement.

## 1. Files (local `scripts/skr2e/`; gaint target `el_f3/reports/skr2e/`, as PF2E's `el_f3/reports/pf2e/`)
| File | md5 | From | Role |
|---|---|---|---|
| `skr2e_infer.py` | 5ba3c597 | `pf2e_infer.py` 272463d3 | ensembles, val gates, val decisions, E1 GT check, test + E1 per-cell JSONs at the union of b's, E1 aggregate sweep, checks |
| `skr2e_run.sh` | b2816cb3 | `pf2e_run.sh` 9df7d9a7 | launcher `gate` / `full`; CPU fp32, nice 19, 8 threads, CUDA hidden; own PID and python PID recorded; rc captured before `date` |
| `skr2e_boot.py` | 6de94f7e | `pf2e_boot.py` bee9e182 | verdict scorer on the pulled JSONs (laptop; imports the laptop's Track M scripts) |
| `diff_infer_vs_pf2e_272463d3.diff` | 047d3ec3 | `diff -u` | full diff, also in the appendix below |
| `diff_run_vs_pf2e_9df7d9a7.diff` | bd7d7577 | `diff -u` | |
| `diff_boot_vs_pf2e_bee9e182.diff` | 3b5373f5 | `diff -u` | |

Imported unchanged:
- Track M `m_common.py` 10f0d37c (gaint `el_f3/reports/d/`; asserted by md5 prefix);
- `m1_analyze.py` 8e566254 (`boot`, `counts`, `prim_from`);
- `m0_analyze.py` d5adbe6b (`agg`, `TWINS`, `NOISY`);
- E1 context `team_2026-10-29_features/scripts/e1_context.tsv` 12bd1385.

Gaint inputs, checked read-only (E, 22:0x):
- `el_thin/experiments/skr2_SKR01_100pct_s5..9` and `el_f3/experiments/pf2_SUPPF_100pct_s5..9` are present;
- `el_thin/REVISION` = c9bbb02 (HEAD c9bbb02, 0 tracked changes) and `el_f3/REVISION` = e544133;
- the `model:` section of skr2 s5's config_used.yaml is identical to pf2_SUPPF s5's (`diff`); the script asserts this for all 10 members;
- PF2E's `el_f3/reports/pf2e/out/` holds E-PF.b0 / E-PF.b1.5 / pf2e_val_decisions.json (405384198c…) and pf2e_infer.py 272463d3;
- `s2q/post/m0/SKR01/skr2_SKR01_100pct_s5.json` and `el_f3/reports/pf2/post/m0/pf2_SUPPF_100pct_s5.json` are present.

## 2. skr2e_infer.py: what changed vs 272463d3 (full diff in the appendix)
Unchanged, verbatim: `x_of`, `stats`, `summ`, the val loop, the D2 rule and width-flag lines, the test / test_noscuff loop body and the scuff assert, the one-opening refusal, the m_common md5 assert.

Changed, each one a protocol §6 item:
1. **Arms:** `--epf` / `--eskr`; the run names are asserted in order (pf2_SUPPF_100pct_s5..9, skr2_SKR01_100pct_s5..9). ARMS = {E-PF, E-SKR2}.
2. **Per-arm REVISION assert:** `run.parent.parent/REVISION` must be e544133 for E-PF and c9bbb02 for E-SKR2.
3. **One model code, strict load:** both arms are built by el_f3's `build_model` (`--code` el_f3), with `load_state_dict(..., strict=True)` (strict was already the default; now explicit). `load()` also returns the model config and the state-dict key → shape map. Asserted: every member's model config == pf2_SUPPF s5's, and every member's keys and shapes == pf2_SUPPF s5's. **Disclosed (S):** the model-config equality assert is one more than you listed. It only exits on mismatch.
4. **Gate (a), per-arm m0 reference:** E-PF uses `--m0ref-pf` (PF2 m0) and E-SKR2 uses `--m0ref-skr` (`s2q/post/m0/SKR01`). The check is member s5 alone, val pooled, b 0: crack IoU and relF1@2 within |Δ| ≤ 0.005 (as PF2E). New: val any-hit within |Δ| ≤ 0.01, plus equal GT component counts. any-hit = GT crack comps ≥ 20 px with hit ≥ 1, pooled; this is m0_analyze `cc_recany_20`, and self-test (3) checks it.
5. **Gate (b):** each ensemble's val GT crack comps ≥ 20 px == 125 (from the b 0 sweep cells; prediction-independent). Any failure of (a) or (b) exits 3 before the decisions.
6. **Decisions + union of b's:** `skr2e_val_decisions.json` gets `union_b` = sorted {0, b_D2(E-PF), b_D2(E-SKR2)}. It is written, md5 printed, before any test / E1 read.
7. **Gate (c):** E-PF's bias and headline must equal PF2E's `pf2e_val_decisions.json` exactly. **The drop must be within |Δ| ≤ 1e-9: please rule on this tolerance.** Exact float equality is expected (same code, CPU, threads), but a 1-ulp difference should not stop E1 #6 when b and headline agree. The result is appended to `skr2e_gate.txt`; a mismatch exits 4 before any test / E1 cell.
8. **E1 GT check before any E1 inference:** the E1 masks and ignore masks are read first, and GT crack comps ≥ 20 px are counted with `cell_stats` on a zero prediction (the GT side does not depend on the prediction). The count must equal 296, else exit 5 before any model sees an E1 image. The masks are then reused, not re-read.
9. **Test + E1, both arms at U:**
   - test and test_noscuff at b ∈ U;
   - E1 at every b of the D2 grid. Per-cell results are kept only for b ∈ U (→ `E-{PF,SKR2}.b<b>.json`, as PF2E's format plus `model_code_revision` e544133, `code_revision` = the arm's training revision);
   - **E1 aggregate sweep** `skr2e_e1_sweep.json`: per arm, per b in 0 … 3 step 0.25, the pooled pred / GT crack px, relF1@2, any-hit (hits / n), and crack-free cells and their px. Aggregates only; no per-cell E1 file at b outside U.
10. **Checks** (`skr2e_checks.txt` / `.json`, after all outputs are written):
    - **E-PF identity:** every val / test / test_noscuff / ext cell at b 0 and b 1.5 vs PF2E's `E-PF.b0.json` / `E-PF.b1.5.json`, compared as JSON values (cell sets too).
    - **any-hit self-test:** this run's E-PF b 0 E1 cells vs the sweep aggregate at b 0 vs PF2E's `E-PF.b0.json`.
    - **rc:** 6 if the sweep and the cells disagree (a code fault), or if the identity is exact and PF2E's count differs; else 0. An identity that is not exact gives rc 0, flagged "NOT EXACT: disclosed; E-PF is taken from this run". `skr2e_boot.py` refuses unless checks rc = 0, and prints the identity status in its header.
- **Cost (S):** PF2E took 11 min. The extra cost is the E1 sweep, 13 b × 2 arms × 106 `cell_stats` calls instead of ≤ 2 b; val already ran 13 b. Estimate ~18-25 min CPU at nice 19 / 8 threads. RAM: the PF2E pattern plus 13 × 2 × 106 cell dicts (tens of MB).

## 3. skr2e_boot.py (protocol §2-4)
- **Kept verbatim:** `verdict()`, `MODULE`, `cluster_boot()`, and PF2E's whole report as `pf2e_report()` (print → line list; used only by the self-test).
- **any-hit:** `cluster_boot5` = `cluster_boot` plus a 5th column. any-hit is the ratio of the pooled component counts (hits / GT comps ≥ 20 px) over the resampled clusters' cells. The draws are the same (one `rng.integers` per resample, no extra RNG use), so columns 0-3 equal `cluster_boot` exactly (self-test 3).
- **Verdict at b 0 (§3c):**
  - test primaries by `verdict()` on all 50 + clean 49 (`passing()` names every passing primary);
  - E1 co-primaries crack relF1@2 + any-hit: PASS if a CI lies above 0, FAIL if a CI lies below 0;
  - PASS = ≥ 1 primary passes, none fails, no guard trips; FAIL = a primary fails or a guard trips; else n.d.;
  - the fixed wording lines are printed (a PASS from test only adds "SKR2's single-model E1 gain is not confirmed at ensemble level.").
- **Guards (§3b), at b 0 and at the headline pair (evaluated once if the headline pair is (0, 0)):**
  - G2a: test relP@2 Δ (all 50) < −0.03;
  - G2b: E-SKR2 E1 crack-free px > 1.5 × E-PF's, with 74 crack-free cells asserted per arm. The bar uses this run's E-PF (= PF2E's 2,528 if the identity is exact);
  - G1t: test inactive Δ ≤ −0.015 in both sets;
  - G1e: E1 inactive cluster CI hi < 0.
  - At the other pairs the guards are printed as reported.
- **Readouts (§4):**
  - **Pairs:** all pairs in U × U (≤ 9). They are labelled VERDICT (0, 0), GUARDED headline pair, and reported. The (hb_SKR2, hb_SKR2) pair is tagged "= E-PF at E-SKR2's headline b".
  - **Per pair:** four cell sets with CIs; capture (relR / relP @2, pixel R / P, comp R / P, test any-hit, pred / GT); per source (crack IoU, relF1, inactive); test_noscuff; E1 width (pred / GT, relR / relP, pixel R / P, comp R / P); crack-free px (test, val, E1); E1 strata (scuff+half-cut 29 / half-cut without scuff 29 / full 48; half-cut 58; other 77) with relF1, any-hit, inactive, relR / relP, pred / GT.
  - **E1 concentration (b 0 pair):** GT inactive px and GT crack comps per image (top 3 / top 10 share, n_eff, top-3 names); any-hit comps for the top 10 images per arm; leave-top-3-images-out Δ (by inactive px and by crack comps) for relF1 / any-hit / inactive; leave-one-cluster-out range (71 drops) for relF1 and any-hit.
  - **Matched volume:** from the sweep, E-SKR2 b 0 pred / GT; E-PF is linearly interpolated between grid b's (descriptive, E1-oracle, chooses nothing). Not computed, and stated so, if E-PF's pred / GT is not monotone on the grid or the target lies outside it.
  - **Other:** `--singles` (ensembles at b 0 vs the opened single-seed m0 means ± sd, incl. any-hit); the FINAL line; the B5 line (not computed here, §5 Q5).
- **Self-tests (E, laptop, `skr2e_boot.py --selftest results/pf2e/raw results/pf2e/pf2e_boot_runner.txt e1_context.tsv results/pf2/raw/m0`; PF2E files opened 1 Nov, raw MANIFEST -c OK; 12 s): SELFTEST PASS**
  1. **PF2E reproduction:** `pf2e_report()` with E1 via `cluster_boot5` equals `pf2e_boot_runner.txt` (b1417347) **line by line, 65 / 65**; the control via `cluster_boot` also matches. I first re-ran the frozen `pf2e_boot.py` bee9e182 itself: `cmp` IDENTICAL to b1417347 (same numpy, same files).
  2. **E-PF vs itself** (PF2E E-PF.b0 as both arms): every test (4 sets × 2 splits) and E1 CI is [0, 0] incl. any-hit; no guard trips; verdicts n.d.
  3. `cluster_boot5` columns 0-3 == `cluster_boot` exactly (E-g vs E-PF, E1 b 0); the any-hit full Δ == the `agg` cc_recany_20 difference; E1 GT comps ≥ 20 px from PF2E's file = **296**.
  4. The matched-volume interpolation is checked on a synthetic sweep with a known answer.
- **Pipeline dry run (E):** fabricated directory (PF2E files relabelled as E-PF / E-SKR2 at b {0, 1.25, 1.5}; headline pair (0, 1.25); synthetic sweep; checks rc 0) run with `--singles results/pf2/raw/m0 results/s2/raw/m0/SKR01`: rc 0, 19.6 s, all sections present (9 pairs, VERDICT, concentration, matched volume, singles). The output is meaningless and is not kept (scratch only).
- **Not tested:** `skr2e_infer.py` cannot run on the laptop (no torch); only an AST check was done. Its first real execution is the run (or the gate-only dry check, Q1).

## 4. Run plan (after APPROVED)
1. Copy `skr2e_infer.py` + `skr2e_run.sh` to gaint `el_f3/reports/skr2e/` (new dir), md5 both ends.
2. Log E1 opening #6 in `e1_openings.md` at start.
3. Gaint tmux `skr2e`: `bash skr2e_run.sh full` (CPU only, no GPU gate; nice 19, 8 threads, CUDA hidden; `run_full.pid` / `py_full.pid` recorded). It starts only after B6's gaint scoring has ended. B6 scoring is GPU-light on CPU (OMP 4), but B6 keeps priority.
4. Pull `out/` with a MANIFEST (md5 both ends). Then locally: `skr2e_boot.py <pulled out> e1_context.tsv --singles results/pf2/raw/m0 results/s2/raw/m0/SKR01 > results/skr2e/skr2e_boot_runner.txt`. All of it goes to coach for the recompute; no verdict to team-lead.

## 5. Questions for coach
- **Q1. Gate-only dry check before APPROVED?** PF2E did one (val only, `--gate-only`; it stops after gates (a)/(b), before the decisions, before any test / E1 cell). It is the only way to execute `skr2e_infer.py`'s model path before the run. Your rule "nothing runs before APPROVED" applies, so I will not start it unless you allow it (≈ 4 min CPU, val only, out_gate/).
- **Q2.** Gate (c) drop tolerance 1e-9 (b and headline exact).
- **Q3.** The checks' rc logic (identity not exact → continue, disclosed; any-hit inconsistency → rc 6).
- **Q4.** U × U pairs as my reading of "every readout at the union of b's" (at most 9 blocks).
- **Q5. B5 / cell-level:** not built. `pf2e_b5.sh` 4e7bd28e would need an ensemble wrapper per arm (as PF2E's out_b5); proposal: a frozen extra pass after the verdict files are pulled, only if you want it; else omitted and disclosed (§4 allows either).

## Appendix: `diff -u pf2e_infer.py (272463d3) skr2e_infer.py (5ba3c597)`
See `scripts/skr2e/diff_infer_vs_pf2e_272463d3.diff` (047d3ec3, 266 lines); inlined:

```diff
--- scripts/pf2e/pf2e_infer.py	2026-11-01 18:49:01.341793158 +0530
+++ scripts/skr2e/skr2e_infer.py	2026-11-02 22:04:12.597209215 +0530
@@ -1,17 +1,30 @@
-"""PF2E (protocol_PF2E.md v1, locked 1 Nov 14:28): E-g (pf2_SUP_100pct_s5..9) vs E-PF (pf2_SUPPF_100pct_s5..9), 5-member
-mean-softmax ensembles, final weights, TTA off. Inference only, gaint CPU fp32 (nice 19, <= 8 threads), as D's d_infer.py
-(129edac4; same image read x_of, same Track M m_common.cell_stats 10f0d37c, same crack bias: log p, + b on crack, argmax; p(crack)
-renormalised). Order (each step's file written before the next set is read):
-  1. VAL GATE: member s5 of each arm alone vs its PF2-opening m0 JSON (GPU bf16), val pooled crack IoU and relF1@2 at b 0,
-     |delta| <= 0.005, else exit 3 before any test / E1 cell (pf2e_gate.txt).
-  2. VAL sweep b in {0, 0.25, ..., 3} per ensemble; FINAL's rule D2 exactly as Track M m9_final.py: the smallest b with val
-     relR@2 >= 0.90, used if its relP@2 >= 0.90, else the b with max val relF1@2; headline b = 0 if val crack (pixel) precision
-     drops by > 0.05 from b 0 to the chosen b. Decisions -> pf2e_val_decisions.json BEFORE any test / E1 inference.
-  3. TEST (50; plus test_noscuff = the 236 raw class-25 px of ARTS_00047_r3_c1 / ARTS_00051_r3_c2 ignored, descriptive) and
-     E1 (ext117, 106, its ignore masks) at b 0 and at each ensemble's chosen and headline b. Outputs, m0 per-cell format
-     ({"run", "step", "code_revision", "bias", "cells": {"val", "test", "test_noscuff", "ext"}}): <out>/<E>.b<b>.json.
-Usage: python pf2e_infer.py --code EL_F3 --tm DIR_WITH_m_common --out OUT --eg 5 runs --epf 5 runs --m0ref PF2_M0_DIR [--threads 8]
-       [--gate-only]
+"""SKR2E (protocol_SKR2E.md v1, locked 2 Nov 21:59, md5 cbc3e015): E-PF (pf2_SUPPF_100pct_s5..9, el_f3 e544133) vs E-SKR2
+(skr2_SKR01_100pct_s5..9, el_thin c9bbb02), 5-member mean-softmax ensembles, final weights, TTA off. Inference only, gaint CPU
+fp32 (nice 19, <= 8 threads). = pf2e_infer.py 272463d3 with only the protocol §6 changes (arms, per-arm REVISION, per-arm m0 gate
+reference, union of b's, extra gates / checks, E1 aggregate sweep); same image read x_of, same Track M m_common.cell_stats
+10f0d37c, same crack bias (log p, + b on crack, argmax; p(crack) renormalised), same D2 rule and width flag. Both arms are built
+with ONE model code (--code = el_f3 e544133), strict state-dict load; every member's model config and state-dict keys / shapes are
+asserted equal to pf2_SUPPF_100pct_s5's. Order (each step's file written before the next set is read):
+  1. VAL GATES (skr2e_gate.txt; any failure exits 3 before the val decisions and before any test / E1 cell):
+     (a) member s5 of each arm alone vs its opening m0 JSON (E-PF: PF2 m0; E-SKR2: s2q/post/m0/SKR01; GPU bf16), val pooled at
+         b 0: crack IoU and relF1@2 |delta| <= 0.005, val any-hit component recall (GT comps >= 20 px with >= 1 px within 2 px
+         of a prediction) |delta| <= 0.01;
+     (b) each ensemble's val GT crack components >= 20 px == 125 exactly (prediction-independent).
+  2. VAL sweep b in {0, 0.25, ..., 3} per ensemble; FINAL's rule D2 exactly as Track M m9_final.py (smallest b with val relR@2 >=
+     0.90, used if its relP@2 >= 0.90, else the b with max val relF1@2; headline b = 0 if val crack (pixel) precision drops by >
+     0.05 from b 0 to the chosen b). Decisions -> skr2e_val_decisions.json BEFORE any test / E1 inference.
+     (c) E-PF decisions == PF2E's pf2e_val_decisions.json (bias and headline exact, precision drop |delta| <= 1e-9), else exit 4.
+  3. E1 GT check from the masks alone (no model has seen an E1 image yet): E1 GT crack components >= 20 px == 296, else exit 5.
+  4. TEST (50; plus test_noscuff as PF2E) and E1 (ext117, 106, its ignore masks): BOTH arms at the union U = {0, b_D2(E-PF),
+     b_D2(E-SKR2)} (contains both headline b's). Outputs, m0 per-cell format: <out>/<E>.b<b>.json. E1 aggregate sweep (reported
+     only, protocol §4 matched-volume line): per arm and per b in the D2 grid, E1 pooled pred / GT crack px, relF1@2, any-hit,
+     crack px on crack-free cells -> skr2e_e1_sweep.json (aggregates only; no per-cell E1 file at b outside U).
+  5. CHECKS (skr2e_checks.txt / .json): E-PF identity (every val / test / test_noscuff / ext cell at b 0 and b 1.5 == PF2E's
+     E-PF.b0.json / E-PF.b1.5.json exactly; if not exact: disclosed, E-PF is taken from this run); any-hit self-test (E-PF b 0 E1
+     any-hit from this run's cells == the sweep aggregate == the count from PF2E's E-PF.b0.json crack_cc). Exit 6 if the sweep and
+     this run's cells disagree, or if the identity is exact and the PF2E count differs (a code fault); else 0.
+Usage: python skr2e_infer.py --code EL_F3 --tm DIR_WITH_m_common --out OUT --epf 5 runs --eskr 5 runs --m0ref-pf PF2_M0_DIR
+       --m0ref-skr S2_M0_SKR01_DIR --pf2e PF2E_OUT_DIR [--threads 8] [--gate-only]
 """
 import argparse, hashlib, json, sys, time
 from pathlib import Path
@@ -22,7 +35,8 @@
 
 ap = argparse.ArgumentParser()
 ap.add_argument("--code", required=True); ap.add_argument("--tm", required=True); ap.add_argument("--out", required=True)
-ap.add_argument("--eg", nargs=5, required=True); ap.add_argument("--epf", nargs=5, required=True); ap.add_argument("--m0ref", required=True)
+ap.add_argument("--epf", nargs=5, required=True); ap.add_argument("--eskr", nargs=5, required=True)
+ap.add_argument("--m0ref-pf", required=True); ap.add_argument("--m0ref-skr", required=True); ap.add_argument("--pf2e", required=True)
 ap.add_argument("--ext", default="/home/noob/work/el_f1/reports/f1/ext117")
 ap.add_argument("--raw-test", default="/home/noob/work/el-fault-detection/data/escdd_masks/test")
 ap.add_argument("--threads", type=int, default=8); ap.add_argument("--gate-only", action="store_true")
@@ -37,17 +51,19 @@
 D = Path(a.code) / "data"
 GRID = [round(0.25 * i, 2) for i in range(13)]
 SCUFF = {"ARTS_00047_r3_c1": 34, "ARTS_00051_r3_c2": 202}
+REV = {"E-PF": "e544133", "E-SKR2": "c9bbb02"}
 t0 = time.time()
 
 
-def load(run):  # as d_infer.py 129edac4
+def load(run):  # as d_infer.py 129edac4; + returns the model config and the state-dict key / shape map (strict load as before)
     run = Path(run); cfg = load_config(run / "config_used.yaml")
     st = torch.load(run / "checkpoints" / "latest.pth", map_location="cpu", weights_only=False)
     assert int(st.get("step", -1)) == 20000, run
     mc = {k: v for k, v in cfg["model"].items() if k not in ("encoder_init", "decoder_init")}; mc["encoder_weights"] = None
-    m = build_model(mc); m.load_state_dict(st["models"]["model"]); m.eval()
+    m = build_model(mc); m.load_state_dict(st["models"]["model"], strict=True); m.eval()
     rv = run.parent.parent / "REVISION"
-    return m, {"run": run.name, "revision": rv.read_text().strip() if rv.exists() else "?"}
+    shapes = {k: tuple(v.shape) for k, v in st["models"]["model"].items()}
+    return m, {"run": run.name, "revision": rv.read_text().strip() if rv.exists() else "?", "mc": mc, "shapes": shapes}
 
 
 def x_of(path):  # as d_infer.py 129edac4
@@ -71,19 +87,42 @@
             "relP2": float(rP), "relR2": float(rR), "relF1": float(2 * rP * rR / max(rP + rR, 1e-9)), "inact_iou": float(tp[11] / max(den[11], 1))}
 
 
+def anyhit(cs):  # protocol_SKR2_HC2 §3a.3 = m0_analyze.agg cc_recany_20: GT crack comps >= 20 px with hit >= 1, pooled counts
+    g = [c for v in cs.values() for c in v["crack_cc"]["gt"] if c[0] >= 20]
+    return sum(1 for c in g if c[1] >= 1), len(g)
+
+
+def e1agg(cs):  # E1 aggregate sweep row (aggregates only)
+    C = sum(np.array(v["conf"], np.int64).reshape(NC, NC) for v in cs.values())
+    cf = [np.array(v["conf"], np.int64).reshape(NC, NC) for v in cs.values() if np.array(v["conf"]).reshape(NC, NC)[CRACK].sum() == 0]
+    h, n = anyhit(cs)
+    return {"pred_px": int(C[:, CRACK].sum()), "gt_px": int(C[CRACK].sum()), "pred_over_gt": float(C[:, CRACK].sum() / max(C[CRACK].sum(), 1)),
+            "relF1": summ(cs)["relF1"], "anyhit": h / max(n, 1), "anyhit_hits": h, "anyhit_n": n,
+            "crack_free_cells": len(cf), "crack_free_px": int(sum(c[:, CRACK].sum() for c in cf))}
+
+
 md5 = lambda f: hashlib.md5(open(f, "rb").read()).hexdigest()
+canon = lambda x: json.loads(json.dumps(x))  # compare as written to / read from JSON (ints, floats, lists)
 # one opening only: refuse to run the val decisions / test / E1 part twice into the same output dir
-if not a.gate_only and ((OUT / "pf2e_val_decisions.json").exists() or list(OUT.glob("E-*.json"))):
-    sys.exit(f"refusing: {OUT} already holds PF2E decisions / outputs (E1 opening #4 is read once)")
+if not a.gate_only and ((OUT / "skr2e_val_decisions.json").exists() or list(OUT.glob("E-*.json"))):
+    sys.exit(f"refusing: {OUT} already holds SKR2E decisions / outputs (E1 opening #6 is read once)")
 assert md5(Path(a.tm) / "m_common.py").startswith("10f0d37c"), "m_common.py is not Track M's 10f0d37c"
-assert [Path(r).name for r in a.eg] == [f"pf2_SUP_100pct_s{k}" for k in range(5, 10)], a.eg
 assert [Path(r).name for r in a.epf] == [f"pf2_SUPPF_100pct_s{k}" for k in range(5, 10)], a.epf
-EG = [load(r) for r in a.eg]; EPF = [load(r) for r in a.epf]
-assert all(m[1]["revision"] == "e544133" for m in EG + EPF)
-meta = {"E-g": [m[1]["run"] for m in EG], "E-PF": [m[1]["run"] for m in EPF], "script_md5": md5(__file__), "m_common_md5": md5(Path(a.tm) / "m_common.py"),
-        "ext_stems_md5": md5(Path(a.ext) / "stems_eval.txt"), "device": "cpu fp32", "threads": a.threads}
+assert [Path(r).name for r in a.eskr] == [f"skr2_SKR01_100pct_s{k}" for k in range(5, 10)], a.eskr
+EPF = [load(r) for r in a.epf]; ESK = [load(r) for r in a.eskr]
+assert all(m[1]["revision"] == REV["E-PF"] for m in EPF) and all(m[1]["revision"] == REV["E-SKR2"] for m in ESK), \
+    [(m[1]["run"], m[1]["revision"]) for m in EPF + ESK]
+ref_mc, ref_sh = EPF[0][1]["mc"], EPF[0][1]["shapes"]
+for _, i in EPF + ESK:  # one architecture: same model config, same state-dict keys and shapes as pf2_SUPPF_100pct_s5
+    assert i["mc"] == ref_mc, (i["run"], i["mc"], ref_mc)
+    assert i["shapes"] == ref_sh, (i["run"], sorted(set(i["shapes"]) ^ set(ref_sh))[:5], [k for k in ref_sh if i["shapes"].get(k) != ref_sh[k]][:5])
+meta = {"E-PF": [m[1]["run"] for m in EPF], "E-SKR2": [m[1]["run"] for m in ESK], "revision": REV, "model_code": f"{a.code} (el_f3 e544133)",
+        "n_state_keys": len(ref_sh), "script_md5": md5(__file__), "m_common_md5": md5(Path(a.tm) / "m_common.py"),
+        "ext_stems_md5": md5(Path(a.ext) / "stems_eval.txt"), "pf2e_decisions_md5": md5(Path(a.pf2e) / "pf2e_val_decisions.json"),
+        "device": "cpu fp32", "threads": a.threads}
 print(json.dumps(meta), flush=True)
-ARMS = {"E-g": [m for m, _ in EG], "E-PF": [m for m, _ in EPF]}
+ARMS = {"E-PF": [m for m, _ in EPF], "E-SKR2": [m for m, _ in ESK]}
+M0REF = {"E-PF": (EPF, Path(a.m0ref_pf)), "E-SKR2": (ESK, Path(a.m0ref_skr))}
 val = sorted(l.strip() for l in open(D / "splits" / "val.txt") if l.strip()); assert len(val) == 54
 
 # ---- 1 + 2: VAL (gate members, ensemble sweep) in one pass over val
@@ -98,14 +137,20 @@
             for b in GRID:
                 sweep_cells[k][b][s] = stats(pe, gt, None, b)
 print(f"val done, {time.time() - t0:.0f} s", flush=True)
-L, bad = ["PF2E gate: member s5 of each arm alone, val pooled, b 0: gaint CPU fp32 vs its PF2-opening m0 JSON (GPU bf16); tolerance 0.005"], False
-for k, ms in (("E-g", EG), ("E-PF", EPF)):
-    r5 = ms[0][1]["run"]; ref = json.load(open(Path(a.m0ref) / f"{r5}.json"))["cells"]["val"]
+L, bad = ["SKR2E gates (a) member s5 of each arm alone, val pooled, b 0: gaint CPU fp32 vs its opening m0 JSON (GPU bf16); "
+          "tolerance 0.005 (crack IoU, relF1@2), 0.01 (any-hit); (b) ensemble val GT crack comps >= 20 px == 125"], False
+for k, (ms, rdir) in M0REF.items():
+    r5 = ms[0][1]["run"]; ref = json.load(open(rdir / f"{r5}.json"))["cells"]["val"]
     me, rf = summ(gate_cells[k]), summ({s: ref[s] for s in val})
     for q in ("crack_iou", "relF1"):
-        d = me[q] - rf[q]; bad |= abs(d) > 0.005; L.append(f"  {k} {r5} {q}: {me[q]:.4f} (ref {rf[q]:.4f}, delta {d:+.4f})")
-L.append("  -> " + ("FAIL: stop before any test / E1 cell" if bad else "within tolerance: proceed"))
-(OUT / "pf2e_gate.txt").write_text("\n".join(L) + "\n"); print("\n".join(L), flush=True)
+        d = me[q] - rf[q]; bad |= abs(d) > 0.005; L.append(f"  (a) {k} {r5} {q}: {me[q]:.4f} (ref {rf[q]:.4f}, delta {d:+.4f})")
+    (h1, n1), (h2, n2) = anyhit(gate_cells[k]), anyhit({s: ref[s] for s in val})
+    d = h1 / max(n1, 1) - h2 / max(n2, 1); bad |= abs(d) > 0.01 or n1 != n2
+    L.append(f"  (a) {k} {r5} val any-hit: {h1 / max(n1, 1):.4f} ({h1}/{n1}) (ref {h2 / max(n2, 1):.4f} ({h2}/{n2}), delta {d:+.4f})")
+    ng = anyhit(sweep_cells[k][0.0])[1]; bad |= ng != 125
+    L.append(f"  (b) {k} ensemble val GT crack comps >= 20 px: {ng} (expected 125)")
+L.append("  -> " + ("FAIL: stop before the val decisions and any test / E1 cell" if bad else "within tolerance: proceed"))
+(OUT / "skr2e_gate.txt").write_text("\n".join(L) + "\n"); print("\n".join(L), flush=True)
 if bad:
     sys.exit(3)
 if a.gate_only:
@@ -122,29 +167,57 @@
     width = sw[0.0]["crack_P"] - sw[bias]["crack_P"]
     dec[k] = {"bias": bias, "why": why, "val_crack_precision_drop_at_bias": width, "headline_bias": 0.0 if width > 0.05 else bias,
               "sweep": {str(b): v for b, v in sw.items()}}
-(OUT / "pf2e_val_decisions.json").write_text(json.dumps(dec, indent=1))
-print(f"val decisions written (md5 {md5(OUT / 'pf2e_val_decisions.json')}): " +
-      "; ".join(f"{k} b {dec[k]['bias']} ({dec[k]['why']}), headline {dec[k]['headline_bias']}" for k in ARMS), flush=True)
-
-# ---- 3: TEST + E1 at b 0 and at each ensemble's chosen / headline b
-BS = {k: sorted({0.0, dec[k]["bias"], dec[k]["headline_bias"]}) for k in ARMS}
-res = {k: {b: {"val": {s: sweep_cells[k][b][s] for s in val}, "test": {}, "test_noscuff": {}, "ext": {}} for b in BS[k]} for k in ARMS}
+U = sorted({0.0, dec["E-PF"]["bias"], dec["E-SKR2"]["bias"]}); dec["union_b"] = U
+(OUT / "skr2e_val_decisions.json").write_text(json.dumps(dec, indent=1))
+print(f"val decisions written (md5 {md5(OUT / 'skr2e_val_decisions.json')}): " +
+      "; ".join(f"{k} b {dec[k]['bias']} ({dec[k]['why']}), headline {dec[k]['headline_bias']}" for k in ARMS) + f"; union {U}", flush=True)
+pd = json.load(open(Path(a.pf2e) / "pf2e_val_decisions.json"))["E-PF"]
+dd = dec["E-PF"]["val_crack_precision_drop_at_bias"] - pd["val_crack_precision_drop_at_bias"]
+cok = dec["E-PF"]["bias"] == pd["bias"] and dec["E-PF"]["headline_bias"] == pd["headline_bias"] and abs(dd) <= 1e-9
+L = [f"  (c) E-PF val decisions vs PF2E pf2e_val_decisions.json: bias {dec['E-PF']['bias']} (PF2E {pd['bias']}), headline "
+     f"{dec['E-PF']['headline_bias']} (PF2E {pd['headline_bias']}), drop {dec['E-PF']['val_crack_precision_drop_at_bias']:.10f} (PF2E "
+     f"{pd['val_crack_precision_drop_at_bias']:.10f}, delta {dd:+.2e}) -> " + ("EQUAL: proceed" if cok else "DIFFERENT: stop before any test / E1 cell")]
+with open(OUT / "skr2e_gate.txt", "a") as f:
+    f.write("\n".join(L) + "\n")
+print("\n".join(L), flush=True)
+if not cok:
+    sys.exit(4)
+
+# ---- 3: E1 GT components from the masks alone (prediction-independent; before any model sees an E1 image)
 test = sorted(l.strip() for l in open(D / "splits" / "test.txt") if l.strip())
 test = [s for s in test if (D / "escdd_masks" / "test" / f"{s}.png").exists()]; assert len(test) == 50
 ext = [l.strip() for l in open(Path(a.ext) / "stems_eval.txt") if l.strip()]; assert len(ext) == 106
+EXTGT = {}
+for s in ext:
+    gt = np.array(Image.open(Path(a.ext) / "masks" / f"{s}.png")); keep = ~(np.array(Image.open(Path(a.ext) / "ignore" / f"{s}.png")) > 0)
+    EXTGT[s] = (gt, keep)
+ngt = sum(1 for s in ext for c in cell_stats(np.zeros_like(EXTGT[s][0]), EXTGT[s][0], EXTGT[s][1])["crack_cc"]["gt"] if c[0] >= 20)
+L = [f"  E1 GT crack comps >= 20 px (masks + ignore only): {ngt} (expected 296) -> " + ("OK" if ngt == 296 else "MISMATCH: stop before any E1 inference")]
+with open(OUT / "skr2e_gate.txt", "a") as f:
+    f.write("\n".join(L) + "\n")
+print("\n".join(L), flush=True)
+if ngt != 296:
+    sys.exit(5)
+
+# ---- 4: TEST + E1, both arms at the union U; E1 aggregate sweep over the D2 grid
+res = {k: {b: {"val": {s: sweep_cells[k][b][s] for s in val}, "test": {}, "test_noscuff": {}, "ext": {}} for b in U} for k in ARMS}
+e1sw = {k: {b: {} for b in GRID} for k in ARMS}
 with torch.no_grad():
     for sp, stems in (("test", test), ("ext", ext)):
         for s in stems:
             if sp == "test":
                 img, gt, keep = D / "labeled" / "images" / f"{s}.png", np.array(Image.open(D / "escdd_masks" / "test" / f"{s}.png")), None
             else:
-                img = Path(a.ext) / "images" / f"{s}.png"; gt = np.array(Image.open(Path(a.ext) / "masks" / f"{s}.png"))
-                keep = ~(np.array(Image.open(Path(a.ext) / "ignore" / f"{s}.png")) > 0)
+                img = Path(a.ext) / "images" / f"{s}.png"; gt, keep = EXTGT[s]
             x = x_of(img)
             for k, ms in ARMS.items():
                 pe = sum(torch.softmax(m(x).float(), 1)[0] for m in ms) / len(ms)
-                for b in BS[k]:
-                    res[k][b][sp][s] = stats(pe, gt, keep, b)
+                for b in (U if sp == "test" else GRID):
+                    cs = stats(pe, gt, keep, b)
+                    if sp == "ext":
+                        e1sw[k][b][s] = cs
+                    if b in U:
+                        res[k][b][sp][s] = cs
                     if sp == "test" and s in SCUFF:
                         sc = np.array(Image.open(Path(a.raw_test) / f"{s}.png")) == 25
                         assert int(sc.sum()) == SCUFF[s] and int((gt[sc] == CRACK).sum()) == SCUFF[s]
@@ -153,8 +226,34 @@
                         res[k][b]["test_noscuff"][s] = res[k][b]["test"][s]
         print(f"{sp} done, {time.time() - t0:.0f} s", flush=True)
 for k in ARMS:
-    for b in BS[k]:
+    for b in U:
         f = OUT / f"{k}.b{b:g}.json"
-        f.write_text(json.dumps({"run": k, "members": meta[k], "step": 20000, "code_revision": "e544133", "bias": b,
-                                 "chosen_bias": dec[k]["bias"], "headline_bias": dec[k]["headline_bias"], "cells": res[k][b]}))
-print(f"PF2E inference done, {time.time() - t0:.0f} s; files: " + ", ".join(sorted(p.name for p in OUT.glob("E-*.json"))), flush=True)
+        f.write_text(json.dumps({"run": k, "members": meta[k], "step": 20000, "code_revision": REV[k], "model_code_revision": "e544133",
+                                 "bias": b, "chosen_bias": dec[k]["bias"], "headline_bias": dec[k]["headline_bias"], "cells": res[k][b]}))
+sweep = {"note": "E1 aggregate sweep, reported only (protocol_SKR2E §4 matched-volume line); aggregates over the 106 E1 cells",
+         **{k: {str(b): e1agg(e1sw[k][b]) for b in GRID} for k in ARMS}}
+(OUT / "skr2e_e1_sweep.json").write_text(json.dumps(sweep, indent=1))
+del e1sw
+print(f"SKR2E inference done, {time.time() - t0:.0f} s; files: " + ", ".join(sorted(p.name for p in OUT.glob("E-*.json"))), flush=True)
+
+# ---- 5: checks (E-PF identity vs PF2E; any-hit self-test)
+chk, L, rc = {}, ["SKR2E checks"], 0
+for b in (0.0, 1.5):
+    pf = json.load(open(Path(a.pf2e) / f"E-PF.b{b:g}.json"))["cells"]; me = canon(res["E-PF"][b])
+    for sp in ("val", "test", "test_noscuff", "ext"):
+        diff = sorted(s for s in set(pf[sp]) | set(me[sp]) if pf[sp].get(s) != me[sp].get(s))
+        chk[f"identity_b{b:g}_{sp}"] = {"cells": len(me[sp]), "pf2e_cells": len(pf[sp]), "differ": len(diff), "first": diff[:5]}
+        L.append(f"  E-PF identity b {b:g} {sp}: {len(me[sp])} cells (PF2E {len(pf[sp])}), {len(diff)} differ" + (f" (first {diff[:3]})" if diff else ""))
+exact = all(v["differ"] == 0 and v["cells"] == v["pf2e_cells"] for v in chk.values())
+L.append("  -> E-PF identity " + ("EXACT: PF2E's E-PF files equal this run's" if exact else "NOT EXACT: disclosed; E-PF is taken from this run, PF2E's files are not used"))
+h_me = anyhit(res["E-PF"][0.0]["ext"]); h_pf = anyhit(json.load(open(Path(a.pf2e) / "E-PF.b0.json"))["cells"]["ext"])
+h_sw = (sweep["E-PF"]["0.0"]["anyhit_hits"], sweep["E-PF"]["0.0"]["anyhit_n"])
+ok_sw, ok_pf = h_me == h_sw, h_me == h_pf
+L.append(f"  any-hit self-test, E-PF b 0 E1: this run's cells {h_me[0]}/{h_me[1]}, sweep aggregate {h_sw[0]}/{h_sw[1]}, PF2E E-PF.b0.json "
+         f"{h_pf[0]}/{h_pf[1]} -> sweep {'EQUAL' if ok_sw else 'DIFFERENT'}, PF2E {'EQUAL' if ok_pf else 'DIFFERENT'}")
+if not ok_sw or (exact and not ok_pf):
+    rc = 6; L.append("  -> any-hit self-test FAIL (code fault): exit 6")
+chk.update({"identity_exact": exact, "anyhit_this_run": h_me, "anyhit_sweep": h_sw, "anyhit_pf2e": h_pf, "rc": rc})
+(OUT / "skr2e_checks.json").write_text(json.dumps(chk, indent=1)); (OUT / "skr2e_checks.txt").write_text("\n".join(L) + "\n")
+print("\n".join(L), flush=True)
+sys.exit(rc)
```
