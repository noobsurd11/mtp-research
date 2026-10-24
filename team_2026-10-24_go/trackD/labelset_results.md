# Track D: labelled-set experiment, results (DX, 24 Oct 2026)

Protocol `protocol_labelset.md` v1, APPROVED by C (`review_labelset_v1.md`, GO in addendum 2). Draws were committed before training (`draws/`).
**Status: CONFIRMED by C** (`verify_labelset.md`): every draw-mean and contrast in all four cell sets reproduced by C's own script, written before this file.

**Runs:**
- 27 supervised runs (R / Tc / Ts × 3 draws × 3 seeds), cv02 GPUs 0-3, 2 lanes each, tmux `=d1`, 24 Oct 11:38-20:02 IST.
- Code `86197f3`. Identity vs `p12_A_5pct_s0` was IDENTICAL to step 500.
- **Completion:** all 27 at rc 0 for training and re-score. Each stdout has exactly one header and one `TEST (final weights, step 20000)` line, and every re-score JSON is at step 20,000 (`results/trackD_labelset/completion.txt`).

**Post-processing:** `d1_post.sh` on GPU 0, 20:02-20:06.
- Per-cell scoring with `trackD_d1_score.py`, τ 0 and 1, plus the 24×24 confusion matrices.
- E1 on the 106 extension cells.

**Files:** `results/trackD_labelset/`:
- `d1_score.json`, `d1_score_confusion.npz`;
- `rescore/` (lane re-score JSONs);
- `e1/`;
- `absent_classes.json`;
- `analysis.txt`, from `scripts/trackD_labelset_analysis.py`.

## Checks
- Per-cell sums reproduce the lane re-score JSONs (crack IoU, relF1@2, inactive IoU) and `la_sa_test.json` for A5c: max |diff| = 0.
- Every run is at step 20,000.
- Relayed to gaint `cv02_noob_el/el_trackD/el_d1` in four passes, MD5 manifests identical.

## 1. Arms (test, all 50; arm = mean of 3 draw-means; draw-mean sd in brackets)
| Arm | crack IoU | crack relF1@2 | crack recall | relP@2 | inactive IoU | mIoU (15 classes in test GT) | + LA τ 1: IoU / recall / relP@2 |
|---|---|---|---|---|---|---|---|
| R | 0.324 (0.007) | 0.757 (0.003) | 0.402 (0.015) | 0.888 | 0.331 | 0.439 | 0.337 / 0.447 / 0.846 |
| Tc | 0.337 (0.007) | 0.787 (0.009) | 0.419 (0.012) | 0.901 | 0.328 | 0.432 | 0.352 / 0.466 / 0.866 |
| Ts | **0.352** (0.017) | **0.795** (0.018) | **0.444** (0.021) | 0.901 | 0.348 | 0.428 | **0.365 / 0.487 / 0.871** |
| *A5c (5 seeds)* | 0.304 | 0.720 | 0.371 | 0.893 | 0.253 | 0.410 | 0.319 / 0.409 / 0.865 |
| *BsM5, D7 (5)* | 0.331 | 0.761 | 0.409 | 0.907 | 0.385 | 0.423 | 0.356 / 0.499 / 0.838 |
| *L3 10% (3)* | 0.396 | 0.814 | 0.507 | 0.910 | 0.294 | 0.486 | 0.407 / 0.552 / 0.886 |

Per draw (crack IoU, mean of 3 seeds; added crack px in brackets):

| Arm | d0 | d1 | d2 |
|---|---|---|---|
| R | 0.327 (8,761) | 0.316 (5,309) | 0.330 (1,327) |
| Tc | 0.337 (18,962) | 0.330 (11,070) | 0.345 (13,642) |
| Ts | 0.359 (21,184) | 0.333 (8,315) | 0.365 (20,318) |

The pre-stated expectation was R ≈ A5c + 0.04 (≈ 0.34). **Measured: R = A5c + 0.020.** +12 random cells bought about half of what the expectation assumed, and R is below BsM5 (0.331).

## 2. Primary contrasts (draw-level rule; seed-level 9 v 9 in brackets)
Δ (threshold) verdict per metric.

**Primary 2, Tc − R (the user's question): BETTER in all 50 and without the noisy cell.**
- **All 50:** crack IoU +0.013 (0.012) B [seed n.d.]; relF1@2 +0.030 (0.011) B [seed B]; recall +0.017 (0.022) n.d.
- **No noisy cell:** IoU +0.011 (0.010) B; relF1@2 +0.026 (0.013) B.
- **No twins / neither** (co-equal, because draws add cells at test module positions): IoU n.d.; relF1@2 +0.028 (0.025) B and +0.023 (0.018) B. So BETTER through relF1@2 in every cell set.
- relP@2 Δ +0.013; no width flag.
- **Bootstrap** (all 50, 2,000 paired resamples): IoU +0.013 [+0.005, +0.021]; relF1@2 +0.030 [+0.020, +0.042]; recall +0.017 [+0.004, +0.029].

**Primary 1, Ts − Tc (mechanism): n.d. in all 50 and without the noisy cell; BETTER without twins, on recall only.**
- **All 50:** IoU +0.015 (0.021) n.d.; relF1@2 +0.007 (0.023) n.d.; recall +0.026 (0.028) n.d.
- **No twins:** IoU +0.023 (0.027) n.d.; relF1@2 +0.025 (0.032) n.d.; recall +0.036 (0.033) B [seed B].
- **Neither:** recall +0.036 (0.034) B.
- **Bootstrap** (all 50): IoU +0.015 [+0.005, +0.027]; recall +0.026 [+0.008, +0.046]; relF1@2 +0.007 [−0.006, +0.024].
- The rule's unit is the draw, and Ts's draw-mean sd (0.017) is the largest. One Ts draw (d1, 8,315 crack px) sits at Tc's level.
- The power sentence in the protocol applies: an all-50 n.d. here is not evidence of no effect.

**Secondary, Ts − R: BETTER on all three primaries in all four cell sets.** IoU +0.028 (0.021); relF1@2 +0.037 (0.021); recall +0.042 (0.030), all 50.

## 3. Per source (all 50; recall / IoU; draw-level arithmetic, descriptive)
| Source (cells) | R | Tc | Ts | A5c | Ts − Tc recall | Tc − R recall | Ts − R recall |
|---|---|---|---|---|---|---|---|
| BMRK (10) | 0.242 / 0.207 | 0.265 / 0.223 | **0.312 / 0.259** | 0.186 / 0.165 | +0.047 (0.072) n.d. | +0.023 (0.063) n.d. | **+0.070 (0.044) B** |
| ARTS (13) | 0.279 / 0.250 | 0.235 / 0.208 | 0.272 / 0.243 | 0.179 / 0.164 | +0.037 (0.064) n.d. | −0.044 (0.096) n.d. | −0.007 n.d. |
| CFVS (18) | 0.481 / 0.378 | 0.493 / 0.389 | 0.519 / 0.399 | 0.461 / 0.360 | +0.026 (0.015) B | +0.012 n.d. | +0.038 (0.022) B |
| CSIR (8) | 0.428 / 0.338 | 0.464 / 0.361 | 0.440 / 0.352 | 0.421 / 0.350 | −0.025 n.d. | +0.037 n.d. | +0.012 n.d. |

- **Ts − Tc on BMRK alone:** IoU +0.036 (0.056) n.d. **On ARTS alone:** IoU +0.035 (0.054) n.d. Both point positive and are below the draw-level thresholds.
- **ARTS:** R does as well as Ts. R's draws hold 1-3 ARTS crack cells and up to 6 ARTS cells in total.
- **BMRK:** Ts reaches 0.259 IoU, above L3 10% (0.219, 24 more random cells).

## 4. Kill check and Direction-4 gate
- **Kill** (both primaries n.d. and BMRK/ARTS recall < +0.05): **not triggered.** Tc − R is BETTER.
- **Direction-4 gate** (critic_defaults §1: Ts − Tc BETTER, or Tc − R BETTER with BMRK recall ≥ +0.05):
  - Tc − R is BETTER, but BMRK recall moves only +0.023;
  - Ts − Tc is BETTER only in the co-equal no-twins rows, on recall alone (+0.036 vs 0.033), and n.d. in all 50.
  - **C's decision: Direction 4 (step 6, SSL on the better-covered set) is NOT opened.** Ts − Tc is n.d. on all 50; its only pass (no-twins recall, by 0.003) sits in a co-equal set that disagrees with all 50, which gives a mixed verdict. Tc − R passes, but BMRK recall moves only +0.023.

## 5. Confounds and secondaries (C's notes)
- **Crack px added:** regression of the 9 draw-means of crack IoU on added crack px gives slope +0.018 per 10k px, r = 0.82.
  - Ts adds more crack px than Tc in 2 of 3 draws.
  - Ts_d1, the one Ts draw with fewer px than every Tc draw, scores 0.333, at Tc's level.
  - So the Ts − Tc direction is entangled with crack-pixel volume. These data cannot separate "weak-source coverage" from "more crack px".
  - **C's residual fit** (descriptive, 9 points): crack volume accounts for the whole Tc − R gap (mean residuals R −0.001, Tc −0.005). Ts keeps about +0.011 beyond volume.
- **Inactive per draw** (inactive IoU vs added inactive px, r = 0.38):
  - R 0.325 / 0.352 / 0.315;
  - Tc 0.324 / 0.300 / 0.360;
  - Ts 0.352 / 0.351 / 0.342.
- **Noisy test cell CSIR_00070_r8_c4, crack FP px per run:**
  - R_d1 1,010 / 5,743 / 318;
  - Ts_d1 611 / 21 / 1,401;
  - Tc_d2 337 / 669 / 108;
  - all other draws ≤ 475.
  - The no-noisy rows change no verdict.
- **Same-module cell `CSIR_00070_r7_c2`:** labelled in R_d0 and Tc_d1. Those draws have low noisy-cell FP (≤ 54).
- **Absent classes per draw:** `absent_classes.json`.
  - Busbars are present in R_d0, R_d1, R_d2 and Tc_d0; jbox in R_d0 and R_d1. The other draws lack both, as A5c does.
  - Tc_d0 also has sp_dogbone and dead_cell.
  - All-class mIoU, draw-level, descriptive: Ts − Tc −0.004 (0.013) n.d.; Tc − R −0.007 (0.016) n.d.; Ts − R −0.011 (0.012) n.d. Crack-targeting does not detectably cost mIoU. The point estimates lean negative, plausibly because R draws carry more head-class variety.
- **E1 extension** (106 cells, arm means of 9 runs; crack false alarm / tolF1): R 0.200 / 0.236; Tc 0.302 / 0.289; Ts 0.257 / 0.277.
  - Crack-cell arms find more crack on unseen modules.
  - They also raise false alarms on crack-free cells (A5c reference in `results/e1`).

## 6. Reading (R)
- **For the user's question:** at a fixed budget of 12 cells, choosing cells that contain crack beats random choice on crack relF1@2 and IoU (all 50).
  - Choosing them from the weak sources (Ts) gives the best crack numbers of any 5%-base model so far: 0.352 IoU, 0.365 with LA.
  - That is above BsM5 (0.331) and BsM5+LA (0.356), with 12 more labels and no unlabelled pool.
- **For the mechanism:** "source coverage beyond crack count" is not established. Ts − Tc is n.d. on the full test set, and crack-pixel volume explains most of the draw-to-draw spread.
  - BMRK moves the most under Ts (+0.07 recall over R), and only Ts − R passes there.
- **Labels vs SSL at 5%:** +12 targeted cells beat BsM5 on crack. BsM5 keeps a large inactive lead: 0.385 vs 0.33-0.35.

## 7. Limits
- One base split.
- 3 draws per arm (draw variance from 3 values).
- 3 seeds per draw (user-approved deviation).
- 50 test cells: BMRK 10 cells, ARTS 13 with 2,856 crack px.
- Retrospective: existing labels, no annotation cost or error.
- Crack px and inactive px are not balanced across arms.
- cv02 only.
