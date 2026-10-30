# Track D: inactive-edge re-score, results (DX, 24 Oct 2026)

Protocol `protocol_edge.md` v1, APPROVED by C (`review_edge_v1.md`). **Post hoc**: written after every arm's standard numbers were known. Banded rows sit beside the standard rows; they never replace them.
**Status: CONFIRMED by C** (`verify_edge.md`): every contrast, threshold and band share recomputed to 3 decimals.

**Run:** cv02 GPU 6, tmux `=dxedge`, 24 Oct about 11:31-11:34 IST, rc 0. Inference only, 68 checkpoints, τ 0 and 1.
**Files:**
- `results/trackD_edge/edge.json`: per run, τ and cell: standard and banded crack counts with relaxed@2, inactive counts, band px, crack GT and predicted px in the band.
- `results/trackD_edge/analysis.txt`: full tables, from `scripts/trackD_edge_analysis.py`.
- Script `scripts_cv02/trackD_edge_rescore.py`, md5 `f66336e1`, el_sk1 code `0ea71df`.

**Band:** GT inactive dilated by 2 px (Euclidean). Crack GT and predictions inside the band are ignored for crack metrics.

## Checks
- **Standard τ 0 rows** match `la_sa_test.json` (P-series) and `results/al1/raw` (AL1) on crack IoU, inactive IoU and relF1@2: max |diff| = 0. τ 1 rows match `la_sa_test.json` wherever it has them; AL1 has no τ 1 reference.
- Every run is at step 20,000.
- `al1_A5` reproduces A5c to 4 decimals on every row. So its gap is the same supervised base on the D7 code.

## 1. How much crack sits on inactive edges (E)
- **All test cells:** 10,650 of 92,074 GT crack px (11.6%) lie within 2 px of GT inactive.
- **By source:** BMRK 22.6% (5,692 / 25,235), CSIR 7.9%, CFVS 7.6%, ARTS 2.5%.
- **Recall inside the band** (seed means):
  - A5c 0.178;
  - BsM5 0.241, CsM5 0.251, BsD5 0.240;
  - A10 0.350, A100 0.469.
  - Outside the band, A5c recalls 0.397 of crack.

## 2. Per arm, all 50 cells (E)
| Arm | n | crack IoU std → banded (paired Δ, n>0) | relF1@2 std → banded | recall std → banded | pred crack px in band |
|---|---|---|---|---|---|
| A5c | 5 | 0.304 → 0.328 (+0.024, 5/5) | 0.720 → 0.750 | 0.371 → 0.397 | 5,321 |
| A5c+LA | 5 | 0.319 → 0.346 (+0.027, 5/5) | 0.728 → 0.763 | 0.409 → 0.436 | 7,153 |
| BsM5 (P13) | 5 | 0.333 → 0.351 (+0.019, 5/5) | 0.764 → 0.782 | 0.411 → 0.434 | 5,193 |
| BsM5+LA | 5 | 0.356 → 0.379 (+0.023, 5/5) | 0.776 → 0.800 | 0.500 → 0.522 | 9,882 |
| CsM5 | 5 | 0.317 → 0.335 (+0.018, 5/5) | 0.752 → 0.771 | 0.398 → 0.417 | 6,178 |
| BsD5 (P17) | 5 | 0.327 → 0.346 (+0.019, 5/5) | 0.756 → 0.777 | 0.411 → 0.433 | 5,552 |
| al1 BsM5 (D7) | 5 | 0.331 → 0.350 (+0.019, 5/5) | 0.761 → 0.780 | 0.409 → 0.433 | 4,720 |
| al1 AL5 | 5 | 0.287 → 0.310 (+0.024, 5/5) | 0.688 → 0.719 | 0.342 → 0.364 | 5,403 |
| al1 ALd5 / ALdh5 / CPS5 / CPSm5 | 5 each | +0.024 / +0.021 / +0.022 / +0.022 | | | 5,503 / 5,845 / 4,582 / 4,487 |
| L3 10% | 3 | 0.396 → 0.417 (+0.021, 3/3) | 0.814 → 0.834 | 0.507 → 0.527 | 8,019 |
| A50 | 5 | 0.408 → 0.420 (+0.012, 4/5) | 0.808 → 0.812 | 0.574 → 0.597 | 7,009 |
| A100 | 5 | 0.435 → 0.442 (+0.007, 4/5) | 0.828 → 0.827 | 0.637 → 0.659 | 7,390 |

**A100 caveat:** this row mixes P6 seeds (s0-2) with P16 seeds (s3-4), and one of its seeds carries the noisy cell. Hence sd 0.078 on all 50 cells; without the noisy cell the A100 − A5c rows tighten (`analysis.txt`). The same holds for A50 (sd 0.076).

## 3. Contrasts: standard vs banded (rule 1, 5 v 5, crack IoU / relF1@2 / recall)
**All 50 cells.** Δ (threshold) verdict.
| Contrast | Standard | Banded | Sign flip |
|---|---|---|---|
| BsM5 − A5c | +0.029 (0.016) B / +0.045 B / +0.040 B | +0.023 (0.015) B / +0.032 B / +0.037 B | no |
| CsM5 − A5c | +0.014 (0.016) n.d. / +0.033 B / +0.027 B | +0.008 (0.017) n.d. / +0.021 n.d. / +0.020 n.d. | no |
| BsD5 − A5c | +0.023 (0.010) B / +0.037 B / +0.040 B | +0.018 (0.011) B / +0.027 B / +0.037 B | no |
| (BsM5+LA) − (A5c+LA), post hoc | +0.037 (0.013) B / +0.048 B / +0.090 B | +0.033 (0.012) B / +0.037 B / +0.087 B | no |
| al1 BsM5 − al1 A5 | +0.027 (0.015) B / +0.041 B / +0.038 B | +0.022 (0.014) B / +0.030 B / +0.037 B | no |
| al1 AL5 − al1 A5 | −0.017 (0.013) W / −0.031 W / −0.029 W | −0.017 (0.015) W / −0.031 W / −0.032 W | no |

B = BETTER, W = WORSE, **per crack metric**. These are not full rule-1 verdicts: the rule-1 primaries also include inactive IoU, which banding leaves untouched, so every BsM5/BsD5 − A5c rule-1 verdict stays BETTER through inactive (C, verify_edge.md).

**Verdicts that change between standard and banded** (Δ shrinks; no sign flip):
- **All 50:** CsM5 − A5c relF1@2 and recall, B → n.d.
- **No 7 twins** (and "neither"):
  - BsM5 − A5c crack IoU: +0.019 (0.018) B → +0.014 (0.018) n.d.;
  - BsD5 − A5c crack IoU: +0.018 (0.013) B → +0.013 (0.015) n.d.;
  - al1 BsM5 − al1 A5 crack IoU: +0.020 (0.018) B → +0.015 (0.018) n.d.;
  - the relF1@2 rows of the same contrasts, B → n.d.;
  - BsD5 − A5c crack recall stays BETTER (+0.027, threshold 0.025).
- **(BsM5+LA) − (A5c+LA)** passes on all three metrics in every cell set, banded or not.

Full four-cell-set tables: `analysis.txt`.

## 4. Per source, crack IoU std → banded (all 50, seed means)
| Arm | ARTS | BMRK | CFVS | CSIR |
|---|---|---|---|---|
| A5c | 0.164 → 0.167 | 0.165 → 0.168 | 0.360 → 0.384 | 0.350 → 0.375 |
| BsM5 | 0.138 → 0.136 | 0.168 → 0.163 | 0.403 → 0.419 | 0.371 → 0.398 |
| L3 10% | 0.220 → 0.220 | 0.219 → 0.216 | 0.483 → 0.503 | 0.389 → 0.416 |
| A100 | 0.456 → 0.456 | 0.379 → 0.389 | 0.522 → 0.523 | 0.379 → 0.399 |

- BMRK holds the largest band share (22.6% of its crack), but banding moves BMRK IoU by at most ±0.01 in any arm.
- The SSL − sup crack gain stays on CFVS in both versions: BsM5 − A5c +0.044 B → +0.035 B.

## 5. Verdict against the protocol
- **Kill (a gap changes sign past its threshold): not triggered.** No contrast flips sign in any cell set, on any metric.
- **Hypothesis "every arm +0.01 to +0.03, gap unchanged within its threshold":**
  - **Holds** at 5% and 10%: +0.018 to +0.027 per arm, 5/5 seeds each.
  - **Not** at 50% and 100%: +0.012 and +0.007, 4/5 seeds.
  - The SSL − sup gaps shrink by 0.004 to 0.006 crack IoU. Every change stays inside its threshold.

## 6. Reading (R)
- **About a fifth of SSL's crack-IoU gain over A5c sits in the inactive-edge band.** SSL recalls band crack better (0.24 vs 0.18), consistent with SSL extending inactive regions (C0.3). Banding removes that part, which tips the twin-free crack IoU rows from BETTER to n.d.
- **The inactive-edge convention is not what makes BMRK hard.** BMRK has the most band crack, yet banding leaves its IoU unchanged in every arm, and its recall outside the band stays low. This supports R1's "BMRK partly intrinsic" over "BMRK is a label-convention artefact" for this part of the convention; the 40-component audit is still the direct test.
- **The convention costs every arm about 0.02 crack IoU at low label fractions** (rather than at 50-100%). A thesis table can carry both rows; the user's answer to convention Q1 decides which row is primary.

## 7. Limits
- Post hoc.
- One band width (2 px).
- 50 test cells; 16 inactive cells define the band.
- The A100 and A50 rows mix protocols and carry noisy-cell seeds.
- relF1@2 in the banded rows uses the same band on both sides, so a prediction just outside the band can no longer match GT just inside it. This slightly penalises banded relF1@2 near edges.
