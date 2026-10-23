# AL1 v2 results: ALHVR adapted to EL, 5% labels, D7 pool (23 Oct 2026)

Status: CONFIRMED by the critic (agent 2) by independent recompute: `alhvr/verify_a2.md`, review_v2 addendum 5, 23 Oct 06:55 IST. Wording requests (a)-(d) applied. Inactive precision/recall are test-only; the critic corrected verify_a2.md to the same values.

**Setup**
- Protocol: `alhvr/protocol_v2.md` (APPROVED, review_v2 addenda 1-3). Code `3a94457`, cv02 `/tmp/noob_el/el_alhvr`. No amendment, no λ change, no resume.
- **D7 pool:** every two-network arm and BsM5 train on the 448-cell unlabelled pool (7 train twins of test cells excluded; each stdout logs "excluded 7 stems").
- 35 runs (7 arms × seeds 0-4), all trained and rescored rc 0. One "Run:" header and no Traceback per stdout.
- Scoring: `latest.pth`, step 20,000 for all 70 re-score entries (test + val). Network A (`model`) for two-network arms and A5, EMA teacher for BsM5. `best.pth` and best-val never read.
- A5 is bit-identical to the old A5c (P12 s0-2, P13 s3-4): same test crack and inactive IoU per seed to all printed digits, as C1 predicted.
- Rules: P8 rule 1, 5 vs 5, as `scripts/ssl_rules.py` (Δ > max(0.01, 2·sqrt((sd_A² + sd_B²)/3)) on a primary, none worse).

**Files** (local `~/mtp/research/`)
- `results/al1/al1_analysis.md`: from `scripts/al1_analysis.py`. Per-arm tables, every contrast in the 4 cell sets, cell bootstrap, noisy-cell FP, leave-top-3-out, source split, bin-0, regions. Sanity line: E1 pooled minus re-score JSON = 0.0 over 35 runs × 4 metrics.
- `results/e1/e1_al1.md`: `scripts_cv02/e1_aggregate.py`, test and the 106-cell extension.
- `results/al1/watch_4k_20k.txt` (`shares.py`, steps 4k-20k) and `results/al1/gshare_series.txt` (every gshare_a sample).
- Raw: `results/al1/raw/` (re-score JSONs), `results/al1/per_image.json`, `results/al1/hist_revised.npz`, `results/e1/raw_v2/al1_*.json`, `results/al1/regions/*.csv`, `results/al1/launch.log`.
- cv02 post-scoring: `scripts_cv02/al1_post.sh`, outputs in `/tmp/noob_el/el_alhvr/reports/al1post/`.

## 1. Results (test, revised masks, 50 cells, mean ± sd over 5 seeds)
| Arm | crack IoU | inactive IoU | crack relF1@2 | crack relP@2 | crack AP | bin-0 crack / inactive |
|---|---|---|---|---|---|---|
| A5 (supervised) | 0.304±0.008 | 0.253±0.037 | 0.720±0.014 | 0.893±0.016 | 0.287±0.007 | 0.569 / 0.688 |
| AL5 (ALHVR-EL, λ 0.1) | 0.287±0.008 | 0.121±0.055 | 0.688±0.012 | 0.898±0.023 | 0.276±0.007 | 0.596 / 0.844 |
| ALd5 (AL5, CPCL off) | 0.295±0.005 | 0.104±0.040 | 0.705±0.010 | 0.892±0.013 | 0.284±0.007 | 0.578 / 0.867 |
| ALdh5 (ALd5, λ 0.3) | 0.299±0.012 | 0.148±0.029 | 0.709±0.022 | 0.872±0.055 | 0.292±0.014 | 0.560 / 0.816 |
| CPS5 (λ 1) | 0.307±0.009 | 0.327±0.052 | 0.726±0.019 | 0.902±0.021 | 0.308±0.009 | 0.547 / 0.521 |
| CPSm5 (CPS5, Ω1 masked) | 0.305±0.012 | 0.315±0.072 | 0.724±0.018 | 0.902±0.011 | 0.305±0.012 | 0.550 / 0.539 |
| BsM5 (re-run, D7 pool) | 0.331±0.010 | 0.385±0.033 | 0.761±0.012 | 0.907±0.018 | 0.367±0.013 | 0.449 / 0.449 |

Val (54 cells, descriptive only): crack IoU 0.273-0.297 for all arms. Inactive val IoU is noisy (sd up to 0.10) and does not track test.

## 2. Locked verdicts (all 50 cells; Δ, then threshold in brackets)
| # | Contrast | crack IoU | inactive IoU | crack relF1@2 | Verdict |
|---|---|---|---|---|---|
| **P** | **AL5 − A5** | **−0.0169 (0.0131)** | **−0.1324 (0.0761)** | **−0.0312 (0.0216)** | **WORSE on all three** |
| S1 | CPSm5 − CPS5 (routing) | −0.0025 (0.0171) | −0.0125 (0.1031) | −0.0026 (0.0303) | n.d. |
| S2 | AL5 − ALd5 (CPCL) | −0.0079 (0.0103) | +0.0169 (0.0785) | −0.0167 (0.0180) | n.d. |
| S3 | ALd5 − A5 | −0.0089 (0.0109) | **−0.1493 (0.0631)** | −0.0145 (0.0202) | WORSE |
| S3 | ALdh5 − A5 | −0.0044 (0.0173) | **−0.1056 (0.0539)** | −0.0101 (0.0302) | WORSE |
| S3 | CPS5 − A5 | +0.0034 (0.0143) | +0.0736 (0.0737) | +0.0068 (0.0276) | n.d. (inactive misses by 0.0001) |
| S3 | CPSm5 − A5 | +0.0010 (0.0166) | +0.0611 (0.0938) | +0.0041 (0.0265) | n.d. |
| S6 | ALdh5 − ALd5 (λ) | +0.0045 (0.0152) | +0.0437 (0.0571) | +0.0044 (0.0278) | n.d. |
| S4 | AL5 − CPSm5 (method) | **−0.0178 (0.0162)** | **−0.1935 (0.1048)** | **−0.0354 (0.0249)** | WORSE |
| S5 | CPS5 − BsM5 (descriptive; CPS5 chosen post hoc as the best two-network arm by mean on all three primaries) | −0.0240 (0.0154) | −0.0583 (0.0710) | −0.0345 (0.0263) | WORSE |
| ref | BsM5 − A5 (descriptive) | +0.0274 (0.0148) | +0.1320 (0.0567) | +0.0412 (0.0219) | passes |

- **Primary (H1): rejected.** ALHVR-EL is worse than step-matched supervised on all three primaries. The paired cell-bootstrap CIs exclude 0 on all three: crack IoU [−0.0287, −0.0065], inactive IoU [−0.1906, −0.0750], relF1@2 [−0.0536, −0.0118].
- **Gap closed vs L3@100%** (descriptive, cross-commit, cv02 P6 s0-2 + P16 s3-4: 0.435 / 0.436 / 0.828):
  - AL5: −0.13 / −0.73 / −0.29;
  - CPS5: +0.03 / +0.40 / +0.06;
  - BsM5: +0.21 / +0.72 / +0.38.
- **Width check:** no flag. The largest relP@2 drop is ALdh5 vs A5, −0.021 (bar −0.05), driven by ALdh5 s0 on the noisy cell (§4).
- **H2 (routing, S1): n.d.** Masking Ω1 does not change CPS. Inactive IoU leans negative over cells, [−0.0317, −0.0001], but well inside the seed threshold. Wording: no evidence for or against ALHVR's routing premise at this power.
- **H3 (CPCL, S2): n.d.** No evidence that CG-CPCL adds anything over DTCT alone.
- No single secondary passes in the locked all-50 set. Every ALHVR-family arm (AL5, ALd5, ALdh5) is WORSE than A5 on inactive IoU.
- Contrast count: protocol §5 lists 8 secondary contrasts (S1, S2, 4 × S3, S6, S4), though its text says 9. All 8 are reported. Only P carries a claim.

## 3. Robustness: four cell sets (`results/al1/al1_analysis.md`)
Verdict per set (rule-1 arithmetic recomputed in each set from E1 counts):

| Contrast | all 50 | without CSIR_00070_r8_c4 | without 7 twins | without both |
|---|---|---|---|---|
| **AL5 − A5** | WORSE | WORSE | WORSE | WORSE |
| CPSm5 − CPS5 | n.d. | n.d. | n.d. | n.d. |
| AL5 − ALd5 | n.d. | n.d. | n.d. | n.d. |
| ALd5 − A5 | WORSE | WORSE | WORSE | WORSE |
| ALdh5 − A5 | WORSE | WORSE | WORSE | WORSE |
| CPS5 − A5 | n.d. | n.d. | passes (inactive +0.0719 > 0.0646) | passes (inactive +0.0702 > 0.0619) |
| CPSm5 − A5 | n.d. | n.d. | n.d. | n.d. |
| ALdh5 − ALd5 | n.d. | n.d. | n.d. | n.d. |
| AL5 − CPSm5 | WORSE | WORSE | WORSE | WORSE |
| CPS5 − BsM5 (descr.) | WORSE | WORSE | n.d. | n.d. |

- **The primary verdict holds in every cell set.** AL5 − A5 crack IoU ranges from −0.0169 to −0.0198 across the four sets, every bootstrap CI below 0.
- CPS5 − A5 passes only in the two post hoc sets without the twins, by a margin of 0.007-0.008 on inactive IoU, with the bootstrap CI touching 0 ([−0.0004, +0.1460] and [−0.0095, +0.1479]). This is a weak, secondary, post hoc pass, not a finding.
- ALdh5 − ALd5 without the noisy cell: crack +0.0080 (0.0100), relF1@2 +0.0111 (0.0159); cell CIs exclude 0 on all three primaries, but the seed rule is n.d.
- **Primary, leave-top-3-out** (by GT area, all 50 otherwise): crack −0.014, inactive −0.114 (crack top-3 out) / −0.156 (inactive top-3 out), relF1@2 −0.027 to −0.030. Still negative.
- **Primary, source split:**
  - CSIR+ARTS (21 cells): crack −0.036, inactive +0.007, relF1@2 −0.052;
  - other sources (29 cells): crack −0.014, inactive −0.146, relF1@2 −0.028.

## 4. Noisy cell `CSIR_00070_r8_c4`: crack FP px per run (E1 crack_pred − crack_tp)
- A5: 106, 62, 176, 11, 33.
- AL5: 206, 46, 26, 14, 0.
- ALd5: 397, 86, 59, 23, 14.
- **ALdh5: 7,236 (s0)**, 86, 0, 125, 82.
- CPS5: 25, 29, 0, 41, 6.
- CPSm5: 20, 16, 2, 1, 0.
- BsM5: 1, 32, 0, 206, 0.

Effect: ALdh5 s0 is the only run that fires on this cell. Without the cell, ALdh5's crack IoU sd drops from 0.012 to 0.007 and its relP@2 drop vs A5 from −0.021 to −0.0005. No locked verdict changes.

## 5. E1 per-cell task metrics (`results/e1/e1_al1.md`, secondary)
- **AL5 − A5, test:**
  - crack tolF1 −0.025 [−0.043, −0.007];
  - crack length error +0.066 [+0.013, +0.104];
  - inactive detection F1 −0.227 [−0.432, −0.057];
  - inactive cell IoU −0.131 [−0.205, −0.067].
- AL5 − A5, extension (106 cells): every CI includes 0; the closest is inactive detection F1 −0.044 [−0.114, +0.000].
- CPS5 − A5, extension: inactive detection F1 +0.165 [+0.021, +0.310]. Crack metrics flat.
- ALdh5 − ALd5, extension: crack tolF1 +0.032 [+0.018, +0.047] and crack IoU pooled +0.008 [+0.004, +0.012]. Stronger DTCT is better than weak DTCT, but neither beats A5.

## 6. Training-log watches (steps 4,000-20,000; never test numbers)
| Arm | share_a (seed means) | gshare_a median per seed | gshare samples > 3 | Ω2+Ω3 px | A/B disagreement |
|---|---|---|---|---|---|
| AL5 | 0.54-0.66 | 0.70-1.48 | 17 / 165 (max 8.35) | 0.11-0.21 | 0.61-0.97% |
| ALd5 | 0.36-0.50 | 0.48-0.79 | 5 / 165 (max 9.20) | 0.15-0.24 | 1.17-1.97% |
| ALdh5 | 0.45-0.74 | 0.95-1.66 | 22 / 165 (max 11.74) | 0.18-0.27 | 1.39-1.96% |
| CPS5 | 0.33-0.38 | 0.29-0.43 | 2 / 165 (max 5.67) | 0.066-0.072 | 0.66-0.78% |
| CPSm5 | 0.30-0.37 | 0.24-0.42 | 0 / 165 | 0.072-0.081 | 0.62-0.78% |
| BsM5 (reference) | 0.34-0.38 (λ·L_con/L_sup) | – | – | – | – |

- **ALdh5 gshare watch (review_v2): intermittently unlabelled-dominated.** 22 of 165 samples exceed 3, spread over all 5 seeds (s0 3, s1 6, s2 1, s3 7, s4 5), max 11.74. The per-seed median is ≤ 1.66 (0.95-1.66), the per-seed mean 1.36-2.08. AL5 has 17 such samples.
- **Activity rule:** every arm's 4k-20k share_a is inside [0.03, 3].
- **Routing flag** (Ω2+Ω3 < 1%): not fired; the lowest is CPS5 at 6.6%.
- **Collapse flag** (disagreement < 0.5%): not fired. The lowest seed mean is AL5 s3 at 0.61%, close to the bar.
- **Regions** (`regions.csv`, hidden GT of unlabelled cells, logging only; mean over 4k-20k and seeds):

| Arm | Ω1 / Ω2 / Ω3 px | GT crack in Ω1 / Ω2 / Ω3 | GT inactive in Ω1 / Ω2 / Ω3 |
|---|---|---|---|
| AL5 (P) | 0.836 / 0.129 / 0.035 | 0.650 / 0.236 / 0.114 | 0.556 / 0.275 / 0.169 |
| ALd5 | 0.821 / 0.148 / 0.031 | 0.698 / 0.219 / 0.083 | 0.571 / 0.293 / 0.136 |
| ALdh5 | 0.781 / 0.198 / 0.021 | 0.700 / 0.240 / 0.060 | 0.596 / 0.307 / 0.097 |
| CPS5 (S1) | 0.932 / 0.027 / 0.041 | 0.587 / 0.185 / 0.228 | 0.343 / 0.162 / 0.495 |
| CPSm5 (S1) | 0.924 / 0.033 / 0.043 | 0.547 / 0.207 / 0.247 | 0.339 / 0.185 / 0.476 |

- **Reading, not a claim:**
  - In the ALHVR-family arms, 56-60% of GT inactive and 65-70% of GT crack sit in Ω1, where they get no unlabelled loss. Ω3 holds only 10-17% of inactive.
  - In the CPS arms, about half of GT inactive falls in Ω3.
  - The ALHVR-family arms also push inactive scores to bin 0 (0.82-0.87 of inactive GT pixels vs 0.69 for A5).
  - Inactive precision / recall (test, revised, seed means from the re-score JSONs): A5 0.771 / 0.276; AL5 0.827 / 0.124; ALd5 0.790 / 0.108; ALdh5 0.799 / 0.154; CPS5 0.649 / 0.400; CPSm5 0.620 / 0.389; BsM5 0.746 / 0.444. The ALHVR-family arms halve inactive recall and predict inactive only where they are sure; the CPS arms and BsM5 raise recall by 1.4-1.6×.
  - DTCT alone is enough for the harm (ALd5 is as bad as AL5), while CE to the partner's argmax (CPS) does not harm. Reading (critic's): the sharpened-MSE plus entropy-minimisation loss on Ω2/Ω3 suppresses the minority class. Not tested by a one-change arm.
  - This is consistent with the DTCT/CPCL targets teaching background on inactive regions. It was not tested by a one-change arm; AL5 − CPSm5 changes the loss form and λ together.

## 7. H-cm predictions (review_v2 addendum 4, written by the critic before any AL1 test number was opened)
| Prediction | Outcome | Held? |
|---|---|---|
| 1. AL5 − A5 crack IoU is no larger than +0.024 | −0.0169 | held |
| 2. AL5 crack bin-0 share within ±0.03 of A5 | 0.596 vs 0.569, +0.027 | held |
| 3. S1 (CPSm5 − CPS5) n.d. or worse on crack IoU | −0.0025 (0.0171), n.d. | held |
| 4. Any SSL gain is larger on inactive than on crack | CPS5 +0.074 vs +0.003; BsM5 +0.132 vs +0.027 | held |

These were weak predictions (all four are compatible with "nothing works"). The inactive harm of the ALHVR family was not predicted.

## 8. Not done (protocol §5 secondary, descriptive)
- Network B and the A+B ensemble were not scored. `per_image_scores.py` and the rescorer load only `model` (network A). Scoring B needs a scorer change, which I did not make without review.

## 9. Verdict
- **AL1 answers its question: no.** ALHVR adapted to 2-D EL at 5% labels, with an active unlabelled loss (share 0.5-0.7, routing and co-training not collapsed), is **worse** than step-matched supervised on crack IoU, inactive IoU and crack relF1@2 under P8 rule 1. This holds in all four cell sets. Most of the damage is inactive recall (0.276 → 0.124).
- Neither ALHVR module helps in a one-change contrast: routing (S1) and CPCL (S2) are both n.d. The same two-network pipeline with plain cross pseudo-labels (CPS5, CPSm5) is level with supervised (n.d.) and below BsM5.
- The project's best SSL recipe at 5%, BsM5, re-run on the D7 pool, still beats A5 (descriptive): +0.027 / +0.132 / +0.041.
