# A6: two-stage cell gate + crack pixel head (Om, 1 Nov): premise check

arch, 2 Nov 2026. Tags: E measured (file), R literature (Research MCP id), S judgement. CPU only, no training, no GPU. No test or E1 file was opened; every new number below is on val (54) or Hanifi `_rf` (F51 51 / H36 36; F19 19 reported), from EXISTING per-cell records. E1 / test numbers quoted are from already-opened, already-verified files and are labelled.

## 0. Verdict (proposed): DROP as a training arm. Optional zero-GPU readout only.
1. A post-hoc cell gate (max crack margin, threshold from val) is close to a no-op on val for every arm, because val false-alarm px are already tiny (7-186 px of ~50k predicted; a perfect label-aware gate lifts val relP@2 by +0.0003 to +0.003).
2. **It cannot rescue SKR.** 99% of SKR w 1.0's extra off-GT px on val sit inside crack cells (+5,711 px vs SUPPF), not on crack-free cells (+69 px). SKR's precision loss is fattening on true crack cells, which a cell gate never touches. SKR's val b_rel stays unreachable after gating (relP@2 0.8942 → 0.8944).
3. On unseen-module cells the cell score discriminates poorly: cell AUROC (max margin) val 0.99, F51 0.68-0.74, H36 0.53-0.58. The "cell AUROC is already high" premise holds in-domain only (the quoted test 0.968 / 1.000 rests on 2 crack-free test cells).
4. Where FA px are large (F51 at val b_rel), the val-fixed gate removes 10-67% of them depending on the seed set, worth relP@2 +0.006 to +0.048 (perfect gate bound +0.057 / +0.071). HC (a training change) already does more on real half-cuts (H36 278 → 11 px) than any gate could on SUPPF (278 → 261).
- S: a gate is a precision tool for crack-free cells; the open failure is E1 crack recall (whole-component misses, see arch_A4 §1) and fattening inside crack cells. Neither is a gate problem.

## 1. Premise check (E)
**Code / files:** `scripts/arch/a6_gate.py` 7f789a47 (rule in its docstring, logged before any number, log 2 Nov ~11:23), `scripts/arch/a6_gate_oracle.py` 171089ef; outputs `ideas/arch_out/a6_gate_s1.txt` a9c5e95d (+ `.json` a222e97e), `a6_gate_s20.txt` 35bcac94, `a6_gate_oracle.txt` 6dd21235. Laptop CPU, seconds.
**Records used (val / rf only):** SUPPF s5-9 + HC s5-9 val + rf from the HC opening (`results/hc/raw/shv1/rec/`, MANIFEST d5c39e0d); SUPPF s0-4 + FINAL val + rf (calib backfill `ideas/calib_out/rec/`, 856faa7d); SKR w 1.0 / CLD s5-9 val (`results/thin/raw/b5/rec/`, 5d3f5b31) and SUPPF s5-9 val (`results/pf2/raw/b5/rec/`, 3827f7c0) as a same-numerics (bf16) pair. **No SKR `_rf` dump exists on gaint** (checked: `el_thin/reports/thin/b5_work/dump` holds val / test / ext only), so SKR is val-only.
**Rule:** gate score g = record `s['1']` (largest crack margin in the cell, the record's proxy for max p(crack)); per run, t = min g over that run's val crack cells (≥ 20 GT px) − 1e-3, so every val positive passes; a gated cell loses all crack px. Pixel OP: b 0, the run's ungated val b_rel (calib's rule), and b_rel re-chosen on gated val. Sensitivity: g = `s['20']`.

### 1.1 Val (54 cells; 23 crack / 31 crack-free), seed means
| arm | b | relP@2 ungated → gated | FA px (crack-free cells) ungated → gated | off-GT px on crack cells (pred − relp_tp: predicted px > 2 px from GT) | val cell AUROC (s1) |
|---|---|---|---|---|---|
| SUPPF s5-9 (bf16) | b_rel | 0.9005 → 0.9005 | 20.0 → 18.8 | 4,896 | 0.992 |
| HC s5-9 | b_rel | 0.9004 → 0.9006 | 52.6 → 43.0 | 5,376 | 0.991 |
| SKR w 1.0 s5-9 (bf16) | b_rel (−4.0, unreachable 4/5) | 0.8942 → 0.8944 | 50.8 → 35.2 | 5,698 | 0.995 |
| SKR w 1.0 s5-9 | b 0 | 0.8687 → 0.8691 | 75.4 → 46.2 | **8,418 (SUPPF 2,707)** | |
| CLD s5-9 | b_rel | 0.9003 → 0.9003 | 103.6 → 103.6 | 5,787 | 0.993 |
| FINAL ens | b_rel (+0.9) | 0.9022 → 0.9022 | 186 → 186 | 4,875 | 0.996 |
- "Off-GT" here = pred − relp_tp (predicted crack px more than 2 px from GT). Pixel-exact (pred − tp) gives SKR vs SUPPF +18,871 px on crack cells vs +69 on crack-free cells (99.6%; judge); the conclusion does not depend on the definition.
- Re-choosing b on gated val changes no OP by more than 0.1. A perfect (label-aware) gate on val: relP@2 +0.0003 (SUPPF), +0.0008 (SKR), +0.0033 (FINAL) (`a6_gate_oracle.txt`).
- **Threshold instability:** t across SUPPF s5-9 = +5.85 / −7.77 / −7.58 / −10.87 / −5.52 (set by each run's single hardest val positive); val crack-free cells gated 31 / 29 / 26 / 9 / 29 of 31. SKR's t is high and stable (8.1-8.5): it is confident on every val crack cell.

### 1.2 Hanifi `_rf` (non-E1 unseen modules), seed means, at each run's val b_rel
| arm | set | cell AUROC s1 | FA px ungated → val-gated (perfect gate 0) | relP@2 ungated → val-gated (perfect) | relR@2 change | crack cells gated (GT px) |
|---|---|---|---|---|---|---|
| SUPPF s5-9 | F51 | 0.736 | 1,231 → 1,109 | 0.794 → 0.800 (0.851) | −0.0000 | 5.0 of 12 (991 px; already missed) |
| SUPPF s0-4 | F51 | 0.722 | 1,617 → 528 | 0.781 → 0.830 (0.853) | −0.0005 | 6.4 (908) |
| HC s5-9 | F51 | 0.740 | 122 → 79 | 0.846 → 0.848 (0.851) | −0.0027 | 5.6 (1,059) |
| FINAL | F51 | 0.676 | 680 → 530 | 0.840 → 0.847 (0.871) | 0 | 5 (389) |
| SUPPF s5-9 | H36 | 0.533 | 278 → 261 | 0.217 → 0.227 | 0 | 10.4 of 17 |
| HC s5-9 | H36 | 0.532 | 10.6 → 0.8 | | −0.004 | 11.6 |
- H36 crack GT is speck-level (1,792 px in 17 cells, judge ruling), so H36 AUROC / relR are uninformative; its FA px are the usable readout.
- F51 FA px are dominated by one cell per SUPPF run (judge, verify_hc §5); the s5-9 vs s0-4 difference in gate effect is that cell's max margin vs each run's t.
- s20 gate: same picture (`a6_gate_s20.txt`).

### 1.3 Already-opened context (not new reads)
- E1 cell level (idea 7 backfill, pre-policy, "not blind"): SUPPF s0-4 cell AUROC 0.889, cell FA 0.257 at b 0; scuff + half-cut 29: AUROC 0.856, FA 0.400.
- PF2E test cell AUROC 0.968 → 1.000 (`verify_pf2e.md` B5 addendum) is computed against **2** crack-free test cells (idea7_metrics_defs §4); it is not evidence of a discriminative gate.
- SKR w 1.0 on E1 (verify_thin_b3): crack-free px ×2.4 (3,931 → 9,428). That part is gate-addressable in principle; whether a val-fixed gate transfers to E1 is unknown, and on F51 / H36 the cell score transfers poorly (§1.2).

## 2. Prior tries in the repo
- No cell classifier, gate or two-stage model has been trained here (grep over `research/` for cell classifier / gate / two-stage / classification head: none). Cell-level metrics exist as readouts only: 27 Oct `cell_detect.py` (evalx), idea 7 (`idea07_metrics.md`, el_metrics `s1 / s20 / s50`).
- Not a repeat. This file's post-hoc gate is the zero-training upper end of the idea's premise.

## 3. Literature (R)
- Tabernik et al. 2019, doi:10.1007/s10845-019-01476-x: segmentation net + decision net on top of the segmentation features (image-level defect yes/no); the decision head is the classifier, the seg output stays ungated.
- Božič et al. 2021, doi:10.1016/j.compind.2021.103459: mixed supervision, same two-head design; image-level detection is the reported target.
- Otamendi et al. 2021, doi:10.1016/j.solener.2021.03.058: EL pipeline detects cell anomalies first, then segments.
- S: these gain where the decision head sees more context than a per-pixel head and the domain is fixed. Our gap is cross-panel; §1.2 shows the cell score itself degrades off-domain, which a learned head on the same features is unlikely to escape (A8 probe: frozen-feature F51 cell AUROC 0.61-0.78 for every encoder, `idea08_foundation.md` §4c-4d). Full text not fetched.

## 4. Cost (if run anyway)
- Post-hoc gate: 0 GPU; ~0.5 day to add a reported line to an opening scorer.
- Trained gate head (cell BCE on the bottleneck, multiply crack logits): ~1 dev day + CPU identity tests; one 5-seed arm ≈ 12.5 lane-h on gaint (R34 peak ~6.4 GB + head ≈ 6.5 GB; fits beside finllm 5.9 GB + 2 GB floor with 2-3 lanes).

## 5. Expected effect (S)
- Test: n.d. (2 crack-free test cells; nothing to gate).
- E1: crack-free px down, crack recall flat or down (a val-fixed threshold on a cell score with off-domain AUROC 0.7-0.9 will gate some real crack cells: on F51, 5-6 of 12 crack cells fall below t, though those were already missed).
- With SKR: removes at most the crack-free part of its E1 cost; does nothing for its test failure (fattening in crack cells, pred / GT 1.54).

## 6. Kill criterion (met on non-E1 data)
- Pre-stated by Om: "precision gain without recall loss not shown". On val the precision gain is ≤ +0.003 even for a perfect gate; on F51 it is +0.006 / +0.048 with relR@2 −0.000 / −0.0005, seed-dependent; for SKR (the case that motivated it) +0.0002. Not shown → DROP.

## 7. What I would do instead (S, zero GPU, coach's call)
- **Withdrawn (2 Nov, after judge's review):** protocol_SKR2_HC2 is now locked for SKR2, and with a threshold this unstable (t swings ~16 margin units across seeds) the line would add an E1 readout of little value. Not proposed. Original text kept for the record: protocol_SKR2_HC2 was not locked (v0.9.1). If coach wanted the "SKR + gate" question answered at no cost, add one **reported** line (never a verdict term): each SKR2 / HC2 / SUPPF run gated at its own val t (this file's rule, s1), E1 crack-free px and E1 any-hit recall, next to G2. It costs a few lines in the opening scorer, reads E1 only at that opening, and decides nothing.

## 8. Files
| file | md5 |
|---|---|
| `scripts/arch/a6_gate.py` | 7f789a47 |
| `scripts/arch/a6_gate_oracle.py` | 171089ef |
| `ideas/arch_out/a6_gate_s1.txt` / `.json` | a9c5e95d / a222e97e |
| `ideas/arch_out/a6_gate_s20.txt` / `.json` | 35bcac94 / bac54786 |
| `ideas/arch_out/a6_gate_oracle.txt` | 6dd21235 |

## judge verdict (2026-11-02 11:43 IST; report md5 02b62868 as reviewed)
**Verdict: DROP as a training arm. Agreed.** The optional reported gate line (§7) is not needed.

### What I reproduced (E)
Own stdlib code: `judge/arch_a6_check.py` 26589eb0; output `judge/out/arch_a6_check_out.txt`.
- **(a) "99% inside crack cells":**
  - Val, b 0, seed means (bf16 records). Crack px on crack-free cells: SKR 75.4 vs SUPPF 6.8. **Match.**
  - Your "off-GT px on crack cells", 8,418 vs 2,707, is **pred − relp_tp**: predicted px more than 2 px from GT. **Match.** Say so in §1.1.
  - Under the pixel-exact definition (pred − tp) it is 34,821 vs 15,950. The extra is +18,871 on crack cells vs +69 on crack-free cells: still 99.6%. The conclusion does not depend on the definition.
- **(b) F51 FA at val b_rel, ungated → gated:**
  - SUPPF s5-9 1,231 → 1,109; SUPPF s0-4 1,617 → 528; HC 122 → 79.
  - H36: 277.8 → 260.6 (SUPPF) and 10.6 → 0.8 (HC).
  - b_rel and t per run match (t from +5.85 to −10.87). **Match.**
- **(c) Cell AUROC (s1):**
  - val 0.992 (SUPPF), 0.995 (SKR), 0.993 (CLD);
  - F51 0.736 / 0.722 / 0.740;
  - H36 0.533 / 0.578 / 0.532.
  - **Match.**

### Notes (S)
- **The gate rule is not deployable.** t is set by each run's single hardest val positive and swings by 16 margin units across seeds. That is why the gate's effect on F51 is seed-set luck (1,617 → 528 vs 1,231 → 1,109). A6 fails even under a lenient rule, which is enough for the DROP.
- **§1.3 is a useful catch.** The PF2E "test cell AUROC 1.000" rests on 2 crack-free test cells. It should never be quoted as evidence of cell-level discrimination.
- **§7 (a reported gated line in the SKR2 / HC2 opening):** protocol_SKR2_HC2 is now locked for SKR2. With a threshold this unstable, the line would add an E1 readout of little value. I recommend not adding it.
