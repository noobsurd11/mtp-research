# SK1 results: SKCDF's auxiliary balanced head (ABSH) at 5% labels, D7 = yes (22 Oct 2026)

Status: CONFIRMED by the critic (independent recompute to 4 decimals; final verdict in `review_v2.md`), 22 Oct 2026.

**Protocol and setup**
- Protocol: `skcdf/protocol_v2.md` (APPROVED; decisions: cv02, D7 yes).
- Code: training `0ea71df`; logit-adjustment rescorer `96dd86a` (path fix; logic as reviewed in `41869d6`).
- Machine: cv02. All 20 runs: trained and rescored with rc = 0, no resume.
- Scoring: every number uses final-step weights (step 20,000):
  - EMA teacher main head for SSL arms;
  - model main head for supervised arms.
- **A5c**: reused (P12 s0–2, P13 s3–4) after three exact log-identity checks.
- **BsD5**: re-run on the reduced pool (`sk1_BsD`): 448 cells, the 7 train twins removed (D7).

**Files** (local `~/mtp/research/results/sk1/` unless stated)
- `sk1_rules.txt`: `scripts/ssl_rules.py`, locked rules.
- `sk1_cellsets.md`: `scripts/sk1_analysis.py`. Four cell sets, cell bootstrap, noisy-cell FP. Sanity check: E1 pooled minus re-score = 0.
- `sk1_la.md`: `scripts/sk1_la_compare.py`, prior-shift control. Inputs `la_test.json`, `la_val.json`.
- `pl_counts_4k_20k.md` and `pl_confident_bg_20k.txt`: pseudo-label diagnostics.
- `secondary_paths.txt`: decoder_u and aux-head paths.
- `results/e1/e1_sk1.md`: E1 per-cell metrics, test and the 106-cell extension.
- Raw re-score JSONs: `raw/`. Per-image counts: `per_image.json`. Histograms: `hist_revised.npz`.

## 1. Results (test, revised masks, 50 cells, mean ± sd over 5 seeds)
| Arm | crack IoU | inactive IoU | crack relF1@2 | crack relP@2 | crack AP | crack bin-0 |
|---|---|---|---|---|---|---|
| A5c (supervised) | 0.304±0.008 | 0.253±0.037 | 0.720±0.014 | 0.892±0.016 | 0.287±0.007 | 0.569 |
| AB5 (A5c + ABSH) | 0.295±0.007 | 0.245±0.046 | 0.713±0.008 | 0.886±0.030 | 0.284±0.005 | 0.572 |
| BsD5 (re-run, 448-cell pool) | 0.328±0.003 | 0.384±0.018 | 0.755±0.005 | 0.889±0.024 | 0.314±0.004 | 0.523 |
| **BsDB5** (BsD5 + ABSH, band 2) | 0.324±0.005 | 0.373±0.016 | 0.760±0.004 | 0.902±0.014 | 0.324±0.007 | 0.515 |
| BsDBn5 (BsDB5 without band) | 0.338±0.006 | 0.390±0.036 | 0.765±0.008 | 0.876±0.014 | 0.366±0.013 | 0.422 |
| BsD5 + LA τ=1 (no training) | 0.341±0.007 | 0.389±0.017 | 0.759±0.012 | – | 0.329±0.006 | 0.482 |
| A5c + LA τ=1 (no training) | 0.319±0.009 | 0.264±0.037 | 0.728±0.015 | – | 0.303±0.006 | 0.530 |

Reference rows, descriptive (full 455-cell pool, other experiments):
- P17 BsD5: 0.327 / 0.371 / 0.756;
- P13 BsM5: 0.333 / 0.360 / 0.764.

## 2. Locked verdicts (P8 rule 1, 5 vs 5; Δ, then threshold in brackets)
| Contrast | Role | crack IoU | inactive IoU | crack relF1@2 | Verdict |
|---|---|---|---|---|---|
| **BsDB5 − BsD5** | rule 1, primary | −0.0044 (0.0100) | −0.0113 (0.0282) | +0.0044 (0.0100) | **n.d.**; width ok (relP@2 +0.013) |
| AB5 − A5c | rule 2, secondary | −0.0083 (0.0128) | −0.0083 (0.0681) | −0.0065 (0.0189) | n.d. |
| BsDB5 − BsDBn5 | rule 3, secondary | **−0.0145 (0.0100)** | −0.0173 (0.0452) | −0.0049 (0.0103) | **WORSE** (the band hurts crack IoU) |

- **Primary: n.d.** As shares of BsD5's gain over A5c (+0.0243 / +0.1311 / +0.0359), the thresholds are 41% (crack), 22% (inactive) and 28% (relF1@2).
- **AB5 − A5c** is n.d. by the seed rule. Over cells, crack IoU is −0.0083 [−0.0121, −0.0051] (paired bootstrap, 2,000): ABSH lowers supervised crack IoU slightly but consistently across cells.
- Descriptive:
  - BsDB5 − A5c: +0.020 / +0.120 / +0.040, passes;
  - BsD5 (re-run) − A5c: +0.024 / +0.131 / +0.036, passes. SSL still beats supervised with the twins out of the pool.

## 3. Robustness: four cell sets (`sk1_cellsets.md`)
Each cell gives Δ (threshold) [95% paired cell-bootstrap CI].

| Contrast | all 50 | without CSIR_00070_r8_c4 | without 7 twins | without both |
|---|---|---|---|---|
| BsDB5 − BsD5, crack IoU | −0.0044 (0.0100) [−0.0099, +0.0016] | −0.0060 (0.0100) [−0.0111, −0.0013] | −0.0045 (0.0100) [−0.0127, +0.0046] | −0.0066 (0.0100) [−0.0142, +0.0015] |
| BsDB5 − BsD5, verdict | n.d. | n.d. | n.d. | n.d. |
| AB5 − A5c, verdict | n.d. | n.d. | n.d. | n.d. |
| BsDB5 − BsDBn5, verdict | WORSE (crack) | WORSE | WORSE | WORSE |
| BsDBn5 − BsD5 (exploratory), crack IoU | +0.0101 (0.0100) | +0.0085 (0.0100), n.d. | +0.0159 (0.0134) | +0.0139 (0.0127) |

- **No locked verdict changes across the four sets.**
- Over cells, BsDB5 − BsD5 inactive IoU leans negative in every set (−0.011 to −0.022) but stays inside its CI.
- Noisy-cell crack FP px per run:
  - A5c ≤ 176; AB5 ≤ 150;
  - BsD5 up to 2,153 (s4) and 1,052 (s0);
  - BsDB5 up to 812 (s3);
  - BsDBn5 up to 1,038 (s4).
  - These confirm the critic's 2,153 max.
- E1 per-cell (`results/e1/e1_sk1.md`, secondary):
  - BsDB5 − BsD5: no per-cell CI excludes 0 on test. On the extension, crack false alarm is +0.032 [−0.003, +0.073].
  - AB5 − A5c, test: crack tolF1 −0.019 [−0.037, +0.000], inactive detection F1 −0.070 [−0.155, +0.003].

## 4. Prior-shift control (descriptive, protocol §8.6; `sk1_la.md`)
- **Setup.** Logit adjustment z_c − τ·log π_c on the BsD5 and A5c final checkpoints:
  - π comes from the 23 labelled cells; τ = 1 was fixed in advance.
  - The τ = 0 run reproduces the re-score JSONs exactly (max diff 0).
  - At τ = 1 the share of test pixels predicted as a class absent from the labelled cells is ≤ 0.0001, so the masked variant is not needed (all four masked numbers agree to ±0.001).
  - The critic's expectation of heavy over-prediction did not happen: crack precision drops by only 0.03–0.04 and recall rises by 0.04.
- **What a free bias does.** BsD5+LA vs BsD5: crack IoU +0.0126 (0.0100) and A5c+LA vs A5c: +0.0154 (0.0140). Both clear the threshold arithmetically; descriptive.
- **The ABSH arms against the matched bias:**
  - **BsDB5 − (BsD5+LA): crack IoU −0.0170 (0.0100), below.**
  - BsDBn5 − (BsD5+LA): −0.0025 / +0.0013 / +0.0056, all inside thresholds. On IoU, BsDBn5 ≈ a fixed logit bias.
  - AB5 − (A5c+LA): crack IoU −0.0237 (0.0132), below.
- **Ranking.** BsDBn5 ranks crack pixels better than BsD5+LA: crack AP 0.366 vs 0.329, crack bin-0 share 0.422 vs 0.482. BsDB5 and AB5 do not (AP 0.324 and 0.284).
- **Val τ grid** (val only, never used for test): BsD5 crack IoU 0.295 → 0.302 from τ 0 to 2; A5c 0.278 → 0.293. Inactive is flat.

## 5. Mechanism logs (`pl_counts_4k_20k.md`, `pl_confident_bg_20k.txt`)
**conf_frac.** Values are the 500-step window from `pseudo_labels.csv`, used throughout. The stdout line at step 20,000 is a 50-step average and differs slightly; for example BsDB5 s1 reads 0.357 there vs 0.410 in the window.

| Arm | conf_frac at 4k | conf_frac at 20k |
|---|---|---|
| BsD5 | 0.86 | 0.96 (all seeds) |
| BsDB5 | 0.22–0.32 | 0.87–0.94; s1 0.41 |
| BsDBn5 | 0.26–0.82 | 0.27 (all seeds) |

**What the confident 27% in BsDBn5 is made of (critic's question).** At step 20,000:
- **background is 0.0000–0.0003 of unlabelled pixels**;
- padding is 0.166 and other structure classes 0.10–0.11.

Background has dropped out of the confident set. For comparison, confident background is 0.686 of unlabelled pixels in BsD5 (0.713 of its confident pixels), and 0.60–0.66 of unlabelled pixels in BsDB5 (s1: 0.14). All shares in this section are of unlabelled pixels unless stated. So from some point after step 4,000, BsDBn5's main unlabelled loss contains no background pseudo-labels.

**Head transfer.** head_drift is 3–5 at step 4,000 and about 0.001 at step 20,000. The evaluated main head equals the balanced head at the end, as the test numbers confirm (main and aux heads agree to ≤ 0.002 in every run).

**Pseudo-label crack share.** Main pseudo-labels: 0.0013–0.0017 of unlabelled px at 20k in all SSL arms. Balanced-head pseudo-labels at 4k: about 2× that in BsDBn5, about 1× in BsDB5 (the band).

**decoder_u path** (secondary): above the teacher on crack IoU in all 15 decoupled runs, by 0.002 to 0.011 (`secondary_paths.txt`), as in P17.

## 6. Reading (interpretation, separate from the verdicts)
- **The pre-registered question has a clear answer:** adapted ABSH (with the 2 px band) does not detectably improve the decoupled recipe at 5% (n.d.), and it is not SSL-specific: on the supervised arm it is n.d. and slightly negative over cells.
- **The band, our thin-structure adaptation, made things worse,** not better: BsDB5 is worse than BsDBn5 on crack IoU in all four cell sets. My a-priori argument (keep the negatives next to cracks so cracks don't fatten) protected precision (relP@2 +0.026), but at the cost of recall and IoU.
- **BsDBn5 (SKCDF's own mask) is exploratory only:**
  - it beats BsD5 on crack IoU by +0.0101 against a threshold of 0.0100 (a margin of 0.0001), and is n.d. without the noisy cell;
  - it is not a locked contrast.
  - Two observations stop it being read as "head rebalancing works":
    1. A free logit bias on BsD5 gives the same IoU (−0.0025 difference). Only BsDBn5's AP / bin-0 improvement goes beyond a prior shift.
    2. Its teacher stopped producing confident background pseudo-labels, so its main unlabelled loss changed character (no background PL; 27% confident vs 96%). The AP gain may come from that, not from the head.
  - The extra crack also brings more false alarms on unseen modules: E1 extension, BsDBn5 − BsD5 crack false alarm +0.105 [+0.066, +0.149] (`results/e1/e1_sk1.md`).
  - Separating the two would need a new arm (e.g. BsD5 with background excluded from pseudo-labels). Not run; not proposed without the user's and critic's agreement.
- **Thesis-relevant side result:** with the 7 train twins removed from the pool (D7), the decoupled SSL recipe still beats supervised on all three primaries in all four cell sets (BsD5 − A5c +0.024 / +0.131 / +0.036 on all 50).

## 7. Not claimed
- SKCDF itself, or any comparison with its Synapse numbers.
- That class rebalancing of the head helps or hurts in general (one recipe, one fraction, one split).
- Any BsDBn5 finding beyond exploratory.
- τ tuning for test.
