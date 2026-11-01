# Idea 7 / Om B5: metric definitions (v0 + coach A1-A5), for protocol_PF2 §4.1-4.2 and THIN-B3

calib, 31 Oct 2026. Agreed by coach (v0 sent 14:00, amendments A1-A5 31 Oct). protocol_PF2 §4.1-4.2 is the authoritative text; this file restates it with the code that implements it.
- Scorer: `ideas/scripts/el_metrics.py`.
- Dump: `ideas/scripts/calib_dump.py`.
- Opening hook: `ideas/scripts/pf2_b5_hook.sh`.
- md5s in §8.

## 1. Knob and grid
- Crack logit bias b on log p (mean softmax for an ensemble), then argmax. This is the house mechanism (m9_final, d_infer, FINAL +0.75).
- Per pixel, crack margin m = log(p_crack + 1e-12) − max_{k≠crack} log(p_k + 1e-12). Crack is predicted iff m + b > 0; elsewhere the prediction is the argmax over the other 23 classes (`oth`).
- **Operating-point grid:** b = −4.0 .. +12.0, step 0.1 (`el_metrics.OPGRID`; widened from +8 by coach 31 Oct after judge's edge finding). A chosen b ≥ 11.5 is flagged `edge`.
- **Diagnostic grid** (curves only, never an OP): −4.0 .. +12.0 plus +0.75 (`el_metrics.GRID`).
- Every metric is exact at every grid b. The scorer uses sorted counts and one radius-2 max filter of the margin; only predicted components are relabelled per b.

## 2. Operating points (per run, val 54 only)
- **b_comp:** the OPGRID b with the highest val component recall subject to val component precision ≥ 0.90.
- **b_rel:** the same for relR@2 subject to relP@2 ≥ 0.90.
- **Ties** go to the smaller b.
- **Not reachable** (no OPGRID b reaches 0.90): the max-precision b (ties to the smaller b), flagged `reachable: false`.
  - **A2:** each run's b_comp, b_rel and flag are reported. A flagged run still enters the rule-1 table at its max-precision b, marked.
- Applied unchanged to test and to E1. **A5:** E1 numbers at the val-chosen b are descriptive and labelled so (`"descriptive": true` in the summary JSON for ext / rf).
- **Ensembles:** one b for the ensemble, by the same rule.
- **Rule 1:** uses the 5 per-seed values per arm.
- **Arm-level pooled OP (coach, 31 Oct):** ONE b per arm, chosen by the same rule on the pooled val counts of all 5 seeds. Each seed's target value is read at that b (`summary --pooled-val V1..V5`; `pf2_b5_pooled.sh`).
  - THIN-B3's co-primaries use the pooled variant. PF2 reports both, with the per-run OP as the primary text.
  - Backfill (E): the pooled OP cuts the seed sd of component recall by 15-35% (e.g. SUP100-PF E1 0.067 → 0.048), means unchanged; relR@2 unchanged.
  - Unit test: pooled curves and the chosen b equal a brute-force Track M `cell_stats` aggregation (0 mismatches).
- **Oracle readout (coach (3), E1 all and E1 sh29):** max over the grid of E1 relF1@2, labelled "oracle upper bound, chooses nothing, descriptive" (`oracle_upper_bound` in the summary JSON for ext).

## 3. Components and relaxed pixels (Track M `m0_analyze`, unchanged)
- 8-connected components of GT crack and of predicted crack, inside the keep mask (E1 / `_rf` ignore px excluded).
- **Component recall:** share of GT components ≥ 20 px with ≥ 50% of their px within 2 px (EDT ≤ 2) of a predicted crack px.
- **Component precision:** share of predicted components ≥ 20 px with ≥ 1 px within 2 px of a GT crack px.
- **relR@2 / relP@2:** pooled pixel counts as `rescore_label_versions.py`. relR@2 = GT crack px within 2 px of a predicted crack px / GT crack px. relP@2 = predicted crack px within 2 px of GT crack / predicted crack px.
- **A1 speck guard, reported at every OP:**
  - `compP_all`: component precision over ALL predicted components (≥ 1 px);
  - `speck_share`: predicted crack px in components < 20 px / predicted crack px.

## 4. Cell level (reported only)
- **Cell positive:** GT crack px in keep ≥ N = 20.
- **Ambiguous:** 1-19 px; excluded and counted.
- **Negative:** 0 px.
- **Why 20 (E):**
  - On val and E1 no cell has 1-54 GT crack px; the smallest positives are 65 and 55 px. So N anywhere in 1-50 gives the same positives.
  - 20 is the component floor and the 27 Oct evalx definition.
  - Hanifi `_rf` has 6 cells with 5-18 px (SAM specks); these are ambiguous.
- **Flag at b:** ≥ 20 predicted crack px in keep.
- **AUROC score:** s20 = the 20th-largest margin in the cell. flag(b) ⇔ s20 + b > 0, so the AUROC is that of the flag rule swept over b (ties averaged).
- **Reported:** recall, precision and false-alarm rate at b = 0, at b_comp, and at a deployed b if one exists (FINAL +0.75); AUROC.
- **Test has 2 crack-free cells:** test gives cell recall only. Precision, FA and AUROC come from val (23 positive / 31 negative), E1 (32 / 74) and `_rf` (38 / 62 / 6 ambiguous).

## 5. Inactive area % error (reported only)
- area = keep px with GT ≠ 7 (padding).
- A_gt = GT inactive px / area. A_pred = predicted inactive px (inside area) / area, at the deployed b (0 for single runs).
- error = |A_pred − A_gt| × 100 (percentage points).
- Reported: MAE over all cells, over GT-inactive cells (A_gt ≥ 0.5%) and over the rest; signed mean; max.

## 6. Inputs, self-check, refusal (A3, A4)
- **Dump** (`calib_dump.py`): per run x set, an npz with stems, margin (float16), oth (uint8), pc (float16), runs.
  - CPU fp32 by default. `--device cuda` gives bf16 autocast, batch 8, cudnn deterministic, the stem order of m0_audit.
  - Test cells only with `--sets test --opening <protocol>` (hard assert).
  - **A3:** dumps stay on gaint (/home/noob/work); the laptop gets only scored JSONs and tables.
- **Records** (`el_metrics.py records ... --m0 <run m0 JSON> --m0-set <set>`): per-cell counts over the grid.
  - With `--m0`, the b = 0 self-check runs first: pooled crack IoU, relP@2, relR@2, inactive IoU, component recall and precision vs the m0 JSON, |Δ| ≤ 0.0005 (0/0 on both sides = agreement).
  - It is written to `<records>.selfcheck.txt`.
  - **A4:** on FAIL nothing is written and the exit code is 4.
  - Without `--m0` the file says UNCHECKED (for sets or ensembles with no m0 JSON).
- **Summary** (`el_metrics.py summary --val R_val --target R_x`): refuses (exit 4, nothing written) unless both self-checks PASS. UNCHECKED is accepted only with `--allow-unchecked`; a FAIL is never accepted. The output carries the self-check status, the descriptive flag and the scorer md5.
- **Numerics (coach ruling, protocol_PF2 §4.1, pre-stated before the smoke):**
  - The opening uses `--device cuda`, tolerance profile `exact` (0.0005 on all six).
  - If runner's bf16 smoke is not exact, ALL runs of ALL arms are dumped on CPU and checked with profile `cpu`: crack IoU, relP@2, relR@2 and inactive IoU ≤ 0.01; component recall and precision ≤ 0.025.
  - Measured CPU-vs-bf16 maxima over 20 backfill runs: pixel 0.0023, inactive 0.0069, components 0.0214. All 40 run x set checks pass the cpu profile.
  - A run failing the profile in force is refused (A4).
  - Hook: `DEVICE=cpu pf2_b5_hook.sh ...` selects the cpu dump + cpu profile.
  - **GPU smoke PASS (runner, 31 Oct ~22:00):** `--device cuda` on f3_SUPPF_100pct_s0 val + records `--tol-profile exact` gives all six deltas +0.00000 vs the opening-1 m0. So B5_DEVICE = cuda for the PF2 opening. RN50 dump peak 5,252 MiB per process.
  - CPU path tested: FINAL val/E1 records vs D's d_cells.json (both CPU fp32) give |Δ| = 0.00000 on all six.

## 7. CLI sequence at an opening (runner; `pf2_b5_hook.sh` does exactly this)
```
calib_dump.py --code <worktree> --out OUT/dump --sets val test ext --opening protocol_PF2 --device cuda --batch 8 --group <run> <run_dir>
el_metrics.py records --dump OUT/dump/<run>.<set>.npz --set <set> --code <worktree> --out OUT/rec/<run>.<set>.json --m0 M0/<run>.json --m0-set <set> --procs 8   # set in val test ext
el_metrics.py summary --val OUT/rec/<run>.val.json --target OUT/rec/<run>.test.json --out OUT/sum/<run>.test.json   # and ext (descriptive)
```
- Hook usage: `[DEVICE=cuda|cpu] pf2_b5_hook.sh protocol_PF2 <worktree> <m0 dir> <out> <dir with the frozen scripts> <run dirs...>`. It logs `b5_hook.log` with the md5s and per-step rc (captured before date).
- After all 5 seeds of an arm are through the hook: `pf2_b5_pooled.sh <out> <dir with the frozen scripts> <the arm's 5 run names>`. It writes `<run>.{test,test_clean,ext}.pooled.json` and logs `b5_pooled.log`.
- Then rule-1 arithmetic on the 5 per-seed `comp_recall_at_opc` and `relR_at_opr` values per arm, in both test sets:
  - per-run OP: top-level keys;
  - pooled OP: under `pooled_op`.
  - Reported in PF2; pooled is the co-primary in THIN-B3.
- The hook also writes `<run>.test_clean.json`: `summary --exclude CSIR_00070_r8_c4`, with the OP still from val. That is rule 1's second set.

## 8. Files and md5 (at filing)
| file | md5 | role |
|---|---|---|
| `ideas/scripts/el_metrics.py` | 6e73ff11 | scorer (records, selfcheck, summary; `--exclude`; `--tol-profile exact|cpu`; `--pooled-val`; OP grid to +12 with edge flag; E1 oracle readout) |
| `ideas/scripts/calib_dump.py` | c172717e | margin dump (CPU / GPU bf16; test only with --opening) |
| `ideas/scripts/pf2_b5_hook.sh` | e06dfc5f | opening hook (summaries: test, test_clean without CSIR_00070_r8_c4, ext); env DEVICE=cuda (default) or cpu |
| `ideas/scripts/pf2_b5_pooled.sh` | 873591ff | arm-level pooled OP summaries (after the hook, per arm) |
| `ideas/scripts/test_el_metrics.py` | 9fd7293a | unit tests vs Track M `cell_stats`, incl. the pooled OP vs brute force (0 mismatches) |
