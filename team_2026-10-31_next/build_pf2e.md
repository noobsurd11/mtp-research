# PF2E build (runner, 1 Nov 2026; for coach's APPROVED)

Protocol: `protocol_PF2E.md` v1 LOCKED 14:28 (md5 4d2a2afd). Inference only, no training. E1 opening #4. The predecessor runner drafted `pf2e_infer.py` and `pf2e_boot.py` before the 14:36 usage cap. This respawned runner reviewed them, added guards and self-tests, and ran a val-only gate dry check. Tags: E = measured (file named), S = judgement.

## 1. Files
| File | md5 | Where | Role |
|---|---|---|---|
| `pf2e_infer.py` | 272463d3 | gaint `el_f3/reports/pf2e/` = local `scripts/pf2e/` | ensembles, val gate, val decisions, test + E1 per-cell JSONs |
| `pf2e_run.sh` | 9df7d9a7 | same | launcher: `gate` (val only) or `full`; CPU fp32, nice 19, 8 threads, `CUDA_VISIBLE_DEVICES=""`; rc captured before `date` |
| `pf2e_boot.py` | bee9e182 | local `scripts/pf2e/` (imports the laptop's Track M scripts) | verdict scorer on the pulled JSONs |

Imported unchanged:
- Track M `m_common.py` 10f0d37c (gaint `el_f3/reports/d/`, = laptop and cv02 copies; asserted by md5 prefix in `pf2e_infer.py`);
- `m1_analyze.py` 8e566254 (`boot`, `counts`, `prim_from`);
- `m0_analyze.py` d5adbe6b (`agg`, `TWINS`, `NOISY`);
- E1 context `team_2026-10-29_features/scripts/e1_context.tsv` 12bd1385 (= gaint `el_f3/reports/d/`).

## 2. pf2e_infer.py (protocol §2, §6)
- **Models:** E-g = `pf2_SUP_100pct_s5..9`, E-PF = `pf2_SUPPF_100pct_s5..9` (run names asserted in this order); `latest.pth` step 20000 asserted; `el_f3/REVISION` = e544133 asserted; final weights; mean softmax over 5 members; TTA off.
- **Device:** CPU fp32. Same input path as the opening: PIL `convert("L")`, (x/255 − 0.5)/0.25.
  - E: all val / test / E1 images are 512 × 512 (val, test RGBA; E1 L); `BenchmarkELDataset` reads with `convert("L")`; so no resize is needed.
- **Crack bias:** as Track M `m9_final.score` (log p, + b on crack, argmax; p(crack) renormalised); scorer Track M `cell_stats`; m0 per-cell format.
- **Order (each step's file is written before the next set is read):**
  1. **Val gate:** member s5 of each arm alone, val pooled at b 0, vs its PF2-opening m0 JSON (`el_f3/reports/pf2/post/m0`, GPU bf16). |Δ| ≤ 0.005 on crack IoU and relF1@2, else exit 3 before any test / E1 cell (`pf2e_gate.txt`).
  2. **Val sweep:** b ∈ {0, 0.25, …, 3} per ensemble. FINAL's rule D2, code lines as Track M `m9_final.py` l.133-139 (checked): the smallest b with val relR@2 ≥ 0.90, used if its relP@2 ≥ 0.90, else the b with max val relF1@2; headline b = 0 if val crack (pixel) precision drops by > 0.05 from b 0. Written to `pf2e_val_decisions.json`, md5 printed, BEFORE any test / E1 image is read.
  3. **Test (50) + E1 (ext117, 106, its ignore masks)** at b 0 and at each ensemble's chosen and headline b. Also `test_noscuff`: the 236 raw class-25 px of ARTS_00047_r3_c1 / ARTS_00051_r3_c2 set to ignore, with the same assertion as `pf2_scuffign.py` e3615fdb (counts 34 / 202, all labelled crack in the house mask). Outputs `out/E-g.b<b>.json`, `out/E-PF.b<b>.json`.
- **Guards added by me:**
  - refuses to run the decisions / test / E1 part if `out/` already holds decisions or E-*.json (the opening is read once);
  - m_common md5 and run-name order asserted;
  - meta records script / m_common / ext-stem-list md5s, device and threads.
- **Gate dry check (E):** `pf2e_run.sh gate` (val only; `--gate-only` stops before the decisions and before any test / E1 cell), gaint tmux `pf2e`, started 18:50:57. Result: §5.

## 3. pf2e_boot.py (protocol §3-4)
- **Test verdict, at each ensemble's headline b:**
  - paired image bootstrap by Track M `m1_analyze.boot`, imported unchanged (2,000 resamples, seed 0);
  - sets all 50 and clean 49 (−CSIR_00070_r8_c4); −twins / −both reported;
  - PASS if a 95% CI excludes 0 (lower bound > 0) on ≥ 1 primary in both sets, or in one set with a same-sign (> 0) estimate in the other; FAIL if any primary's CI lies wholly below 0 in either set; else n.d.;
  - primaries crack IoU, relF1@2, inactive IoU (mIoU_rob reported only).
- **E1 co-primaries (crack relF1@2, inactive IoU; all 106):**
  - paired module-cluster bootstrap (2,000, seed 0); cluster = stem without `_rN_cM` / `_cellN`; 71 clusters asserted;
  - a drawn cluster contributes all its cells, both arms on the same draws;
  - same PASS / FAIL wording, one set.
- **Reported (descriptive):** b 0 for both arms; test_noscuff; per source; crack capture (relR@2, relP@2, component R / P); crack px on crack-free cells (test, val, E1); E1 strata (scuff+half-cut 29 / other 77, half-cut 58 / full 48) with the width checks of `pf2_e1_width.py` (relR / relP / relF1, component R / P via `m0_analyze.agg`); optional `--singles PF2_M0_DIR` (ensembles vs PF2 single-seed mean ± sd, already-opened m0 JSONs); FINAL 0.492 as a descriptive line.
- **Self-test (E, `python pf2e_boot.py --selftest results/pf2/raw/m0 ext117/stems_eval.txt`; PF2 test per-cell files already opened 1 Nov, SUP s5 vs SUPPF s5): SELFTEST PASS.**
  - `m1_analyze.boot` is deterministic.
  - (1) `cluster_boot` with one cell per cluster equals `m1_analyze.boot` **exactly** (full, lo, hi, P>0; same draws).
  - (2) Module clusters on test: the point estimate equals boot's (48 test clusters).
  - (3) Each cell duplicated into a 2-cell cluster gives the same result as boot on the originals (a draw pools all of a cluster's cells).
  - (4) E1 grouping from the stem list only (no E1 score read): 106 stems, 71 clusters.
- **Pipeline dry run (E):** on fabricated files built from PF2 **val** cells only, mapped onto the test / E1 stem names (no test or E1 score used). All sections ran (rc 0, 4 s). The output has no meaning and is not kept in the results.

## 4. Not in this build (coach to rule)
- **B5 operating points and cell-level (protocol §4, reported).** These need an ensemble-aware probability dump for calib's frozen `calib_dump` / `el_metrics`. The per-run npz dumps of PF2 (`el_f3/reports/pf2/b5_work/dump`) hold single-model outputs only. Options:
  - (a) drop them for PF2E, disclosed;
  - (b) a later frozen extra pass (an ensemble wrapper for calib's dump; its own build and md5s);
  - (c) cell-level only, from the per-cell JSONs if calib's cell-level rule needs only per-cell counts.
- **Cost (S):** 10 models × 210 cells CPU forward. The gate (val, 10 models) takes the measured time in §5; the full run takes about 4× that.

## 5. Gate dry check result (E, gaint `el_f3/reports/pf2e/run_gate.log`, `out_gate/pf2e_gate.txt`; 18:50:57-18:54:34, rc 0)
- Member s5 alone, val pooled, b 0, CPU fp32 vs its PF2-opening m0 JSON (GPU bf16):
  - E-g `pf2_SUP_100pct_s5`: crack IoU 0.4270 vs 0.4269 (+0.0001); relF1@2 0.8862 vs 0.8866 (−0.0004);
  - E-PF `pf2_SUPPF_100pct_s5`: crack IoU 0.4104 vs 0.4100 (+0.0004); relF1@2 0.8803 vs 0.8799 (+0.0004) (= D's d_infer v3 gate, 08:33);
  - → within tolerance. Stopped before the val decisions and before any test / E1 cell.
- Val pass: 214 s for 10 models × 54 cells, so the full run (val + test 50 + E1 106) is ~15 min on CPU (S).
- The real run repeats the gate in its own first step; `out_gate/` is separate from `out/`.

## 6. Run plan (after APPROVED)
`bash pf2e_run.sh full` in gaint tmux `pf2e` (CPU only, so no GPU gate; nice 19, 8 threads). Then the pull of `out/` (MANIFEST md5), `python pf2e_boot.py <pulled out> e1_context.tsv --singles results/pf2/raw/m0 > results/pf2e/pf2e_boot.txt` locally, all files to coach for the recompute. No verdict goes to team-lead before coach's recompute.
