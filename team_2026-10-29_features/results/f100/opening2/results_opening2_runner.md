# protocol_100 opening 2: runner's analysis of CP100 (CONFIRMED by coach, 31 Oct)

runner, 31 Oct 2026 07:12 IST; coach CONFIRMED by 07:14 (pull byte-identical, all numbers match to 4 dp; C3 note wording OK). CP100 (`f3_CP_100pct_s0..4`; gaint, e544133, house optimizer, `cp` stream λ 1, frozen library 554 components, val off, 20,000 steps, final weights) vs SUP100-g (opening-1 per-cell files, unchanged).

## Inputs
- gaint `el_f3/reports/f100/post_opening2/` (post rc=0 07:07:24) pulled to `results/f100/opening2/raw/`; `MANIFEST.md5` (md5 1f307099) checks OK, 42 files. Opening-1 comparator manifest re-checked on gaint by the post and again locally (`results/f100/opening1/raw/MANIFEST.md5`, OK).
- All 5 CP runs: step 20000, code_revision e544133; tau 0 == default per cell (`raw/tau0_check.txt`); `raw/init_check.txt` has each run's `cp:` config.
- Per-cell files for the recompute: CP `raw/m0/f3_CP_100pct_s{0..4}.json`, `.tau0.json`, `.tau1.json`; SUP100-g `results/f100/opening1/raw/m0/f3_SUP_100pct_s{0..4}.*`; rescore JSONs in both `raw/rescore/`; `raw/la.json`; `raw/decoy_final.{json,log}`; `raw/crackfree_fp.{json,txt}`; `raw/enc_cosine_20k.*`.
- My outputs: `m2_rung_C1.txt` (C1, tau 0; md5 d18e55d0), `m2_rung_C2.txt` (C2, both arms tau 1; 513a67cd), `m2_rung_C3.txt` (C3, CP tau 0 vs SUP100-g tau 1; first-line note added, 0bb94230, a29aa024 before), `ssl_rules_opening2.txt` (efc61421), `o2_extra.txt` (5ea6d057; `scripts/f100_o1_extra.py` md5 45b03c2f, which now takes ARM=DIR pairs; on opening 1 it still gives o1_extra.txt md5 120f2cf9). Driver `scripts/f100_post_local_o2.sh`.

## Verdict (protocol_100: CP crack claim needs C1 BETTER on crack IoU or relF1@2 AND C2 BETTER on the same primary, worse on none, two-set rule)
| Contrast | Set | crack IoU d (thr) | relF1@2 d (thr) | inactive IoU d (thr) |
|---|---|---|---|---|
| C1 CP100 − SUP100-g, tau 0 | all 50 | +0.0076 (0.0307) n.d. | +0.0102 (0.0379) n.d. | +0.0020 (0.0277) n.d. |
| | −noisy | +0.0003 (0.0100) n.d. | +0.0012 (0.0100) n.d. | +0.0007 (0.0299) n.d. |
| C2 both tau 1 (LA) | all 50 | +0.0086 (0.0311) n.d. | +0.0101 (0.0354) n.d. | +0.0016 (0.0274) n.d. |
| | −noisy | +0.0004 (0.0100) n.d. | +0.0002 (0.0101) n.d. | +0.0005 (0.0297) n.d. |
| C3 CP tau 0 vs SUP100-g tau 1 (reported) | all 50 | +0.0090 (0.0309) n.d. | +0.0096 (0.0363) n.d. | +0.0008 (0.0274) n.d. |
| | −noisy | +0.0023 (0.0100) n.d. | +0.0015 (0.0100) n.d. | −0.0004 (0.0297) n.d. |

- **No CP crack claim** (C1 not BETTER on any primary). Per the Kill line (n.d. on all three primaries in both sets): **the copy-paste pool contrast is closed at 100%.** No ensemble step, no further test opening.
- ssl_rules cross-check (rescore path, all 50): +0.0076 / +0.0020 / +0.0102, thresholds 0.0307 / 0.0277 / 0.0379, n.d.; width check crack relP@2 +0.0188 ok.
- m2_rung "RUNG VERDICT": C1 n.d., C2 n.d.; C3 prints PASS on mIoU_rob only: that compares tau 0 with tau 1, and LA lowers mIoU_rob by itself (SUP100-g 0.5405 → 0.4716), so it is a tau effect; first-line note in the file. mIoU_rob C1 +0.0046 / −0.0015, C2 +0.0098 / +0.0045, n.d.
- Against the pre-stated expectations (S): crack 0 to +0.015 at tau 0: observed +0.0076 / +0.0003 (inside); n.d. after LA: yes; **crack precision −0.01 to −0.03: observed +0.019 (all 50) / +0.006 (−noisy), the opposite sign**; inactive n.d.: yes.
- Multiplicity (protocol): 3 contrasts × 3 primaries × 2 sets + C2, no correction.

## Spread and the noisy cell
- Per-seed test crack IoU all 50 / −noisy: CP s0-s4 0.4640 / 0.4758, 0.4679 / 0.4709, 0.4721 / 0.4751, 0.4751 / 0.4800, 0.4578 / 0.4714 (sd 0.0068 / 0.0037); SUP100-g as opening 1 (s0 0.4143 fails on CSIR_00070; sd 0.0257 / 0.0038). Predicted crack px on CSIR_00070_r8_c4 (787 GT crack px): CP 2,357 / 0 / 0 / 496 / 2,807.
- Bootstrap (B−A, 95%): C1 −noisy crack +0.0003 [−0.0039, +0.0048], relF1 +0.0012 [−0.0029, +0.0054]. Leave-top-3-out crack d: C1 +0.0086 / −0.0006; C2 +0.0089 / −0.0016.

## Reported (never change a verdict)
- **Cell sets:** −twins and −both: all n.d. on the primaries for C1 and C2 (C1 −both crack +0.0011, thr 0.0100).
- **Per source (C1, all 50, SUP → CP):** crack IoU ARTS 0.457 → 0.482 (named secondary +0.0256, thr 0.0405 n.d.), BMRK 0.378 → 0.377, CFVS 0.523 → 0.522, CSIR 0.404 → 0.423 (−noisy 0.474 → 0.475), SDLE (1 cell) 0.001 → 0.046. CSIR FP-absent px 43,120 → 17,168. All named secondaries n.d.
- **Crack capture (C1 all 50):** crack precision 0.623 → 0.642, recall 0.638 → 0.632; −noisy precision 0.644 → 0.650, recall 0.643 → 0.638.
- **E3b decoy at 20k** (`raw/decoy_final.json`; 248 held-out cells, 553 components; mean of 5): SUP100-g real 0.2943, decoy 0.0028, background 0.0008; CP100 real 0.4025, decoy **0.0125** (per seed 0.0118 / 0.0127 / 0.0099 / 0.0104 / 0.0175), background 0.0008. CP decoy = **4.41 × SUP**, so the original gate-6 rule (flag if > 2 × SUP or > 0.05) gives **FLAG** at 20k; against gate 6b's conditions: (1) ≤ 0.05 yes, (2) ≤ 2 × SUP or ≤ 0.0094 no, (3) decoy / real 0.031 ≤ 0.036 yes. Reported only; it does not change the verdict (which is n.d. anyway).
- **Crack px on crack-free cells** (`raw/crackfree_fp.txt`, mean of 5): test (2 cells) 0 / 0 (tau 1: 0 / 1); val (31) **178 → 389** (tau 1: 245 → 558); ext (74) 3,181 → 3,408 (tau 1: 3,950 → 4,478).
- **E1 (ext 106; `o2_extra.txt`), SUP100-g → CP100, mean of 5:** crack recall all 0.169 → 0.193, scuff + half-cut (29) 0.094 → 0.115, other (77) 0.393 → 0.429; crack IoU all 0.141 → 0.158, scuff + half-cut 0.086 → 0.105, other 0.261 → 0.268; inactive IoU all 0.041 → 0.089.
- **Encoder cosine at 20k (vs ImageNet, layer3 / layer4, mean of 5):** CP100 0.011 / 0.001 (house optimizer erases them, as SUP100-g 0.015 / 0.001).
- **LA tau 1:** see C2; per-cell tau 0 == default for CP.

## Reading (mine, for coach to check)
At 100% labels, copy-paste of the 554-component crack library (house recipe) does not change test crack or inactive segmentation measurably: C1 and C2 are n.d. on all three primaries in both sets, with −noisy deltas at or below +0.0012. CP clearly changes the model in the paste domain (pasted real cracks detected 0.40 vs 0.29 on held-out backgrounds) and makes it more trigger-happy on decoys (4.4×) and on crack-free val cells (crack px 2.2×), without a test gain. No CP seed fails on the noisy cell as badly as SUP100-g s0 (all-50 minus −noisy crack IoU gap at most 0.014 vs 0.061), though s0 and s4 still put 2.4-2.8k crack px on it; this shows on all 50 only. With opening 1, all three protocol_100 contrasts (recipe, pool via encoder, pool via copy-paste) are closed n.d. at 100%.
