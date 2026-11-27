# Figures from fig_maker_A (data plots, OUTLINE section 4)

fig_maker_A, 23 Nov 2026. Figures F2, F5, F6, F10 to F17 and F19. F20 is not made: it waits for the T3b read.

## How they were made
- **Files.** Each figure has `F<n>.pdf` (vector), `F<n>.png` (200 dpi preview) and `F<n>_data.csv`.
  - The CSV holds every plotted value and, per row, its source as `path:line` (paths relative to T).
  - F6 also has `F6_check_data.csv`, which checks the medians against the audit's own table.
- **Scripts.** `src/make_F<n>.py` plus the shared module `src/figA_common.py`.
  - `src/make_all_A.sh` rebuilds all twelve figures, on CPU only with `nice -n 10`.
- **How numbers are read.** Every number is parsed from a result text or json file, or a table; none was typed by hand.
  - `find()` fails unless its pattern matches exactly one line, inside the named section where one is given.
  - Check run on 23 Nov: all 923 numeric CSV values appear verbatim on their cited source line. The one exception is the F6 per-cell width, which is derived.
- **Derived values.**
  - The F6 per-cell width is crack px / skeleton px, the audit's own definition. The script asserts that the per-source medians and the n of 207 equal `labels_audit.txt` b1 (l5 to l11).
  - The F13 MDE (0.0742) is copied from the derived TT T8 note.
- **What was read.** Only result text and json files and the tables (verdict.txt, read.txt, read.json, *.md, labels_percell.tsv, contrasts.txt). No E1 or test50 dump, label, prediction or image was opened.
- **Style.**
  - matplotlib 3.11.2, 15 cm wide, DejaVu Sans 9 pt (legends and annotations 8 pt), fonts embedded (Type 42), no titles.
  - Saved with `bbox_inches="tight", pad_inches=0.03` for both PDF and PNG (fix of 23 Nov: F13's value column was clipped in the PDF). Full-width figures come out 14.9 to 15.1 cm wide (F11 15.1, F13 14.9); the narrower ones are F2 12.7, F6 11.2, F15 and F16 10.7 cm.
  - Clipping check, run on each PDF: `pdftotext -bbox` puts every word inside the page (minimum margin 0.6 pt), and a `pdftoppm -r 100` render has no ink in the outer 2 px of any figure.
  - Colours are Okabe-Ito, the palette fig_maker_B also uses: PF / C1 / reference grey #999999; C2 / CS_D4 blue; C1-D4 / PF_D4 vermillion; C3 / CS green; E-PF purple. Each colour also has its own marker shape.
  - Zero line: solid. Margin M: dashed. MDE: dotted.
- **Style difference from fig_maker_B.** B's figures use DejaVu Sans at 8 pt. Mine use 9 pt, as the brief asked. The lead decides whether to align them.

## Captions

### F2: Crack label geometry (`fig:F2`, chapter 2, section 2.3)
Caption:
> Crack label geometry on the training pool (v1.1, 229 crack cells). Strict crack IoU of the label against itself:
> - shifted by 1 px and by 2 px (mean of 8 directions);
> - reduced to its 1 px centreline;
> - redrawn 3 px wide.
>
> Bars are pooled values; markers are per source. There is no per-source value for the 2 px shift. The relF1@2 of each variant is 1.0.

- **Shown:** 19 values (4 pooled, 15 per source).
- **Source:** `dataset_audit/out/labels_audit.txt` section f1, l78 to l86.
- **Caption claim:** "relF1@2 is 1.0" is from `dataset_audit/REPORT.md` l27, not from the plotted file.

### F5: Strict IoU against relF1@2 under label conventions (`fig:F5`, chapter 4, section 4.4)
Caption:
> Strict crack IoU and relF1@2 under four crack label conventions. The same predictions (25 out-of-fold cv5v3 models, 532 pool cells, argmax) are scored on four label sets: the 1 px centreline, the 20211104 release, v1.1, and labels redrawn 3 px wide.
> - (a) PF levels.
> - (b) Strict crack IoU contrasts of HOUSE, HRNET, SWADBN and COMBO (C3X) against PF, with 95% two-stage group-bootstrap intervals.
> - (c) The same contrasts for crack relF1@2.
>
> Dashed line: M = 0.010. The strict-IoU contrasts shift with the convention by up to 0.019 (the convention band). The relF1@2 contrasts shift by at most 0.0031.

- **Shown:** 40 values (8 PF levels; 32 contrasts, each with its interval).
- **Source:** `dataset_audit/out/contrasts.txt`: l2 (M), l6 to l24 (levels), l39 to l54 (contrasts).
- **Caption claims:** "at most 0.0031" is from `dataset_audit/REPORT.md` l32; the +-0.019 band is from TT T4 / AUD F1.
- **Not drawn:** the candidate-ignore variant (candign, l30 to l35, l55 to l58) and the CONS25 arm.

### F6: Crack label width per source (`fig:F6`, chapter 4, section 4.5)
Caption:
> Crack label width per source on the pool (v1.1), in label pixels per centreline pixel. One value per cell, for the 207 cells with at least 50 centreline pixels.
> - Boxes show the quartiles; whiskers reach 1.5 x IQR; circles are cells beyond the whiskers.
> - SDLE has 2 cells and is drawn as points.
>
> Source explains 29.6% of the variance of per-cell width (eta squared 0.296).

- **Shown:** 207 per-cell values (ARTS 40, BMRK 26, CFVS 94, CSIR 45, SDLE 2).
- **Sources:** `dataset_audit/out/labels_percell.tsv` (columns area, sklen; pool cells only); check against `labels_audit.txt` b1, l5 to l11.

### F10: Every arm against PF (`fig:F10`, chapter 7)
Caption:
> Crack relF1@2 contrast of every arm against PF on the pool cells (out of fold, OP-A), with 95% two-stage group-bootstrap intervals.
> - Squares: 5-seed rows on cv5v3 (training machine).
> - Circles: 2-seed screens on cv5v2. They ran on the training machine or the second machine, and each read is against its own PF.
> - Open squares and *: CS and CS_D4. These are selection-biased, because the swad readout was chosen on these cells.
>
> Dashed line: margin M = 0.010. Verdicts are those of Tables T6, T7a, T16a and T16b; a contrast at or above M does not pass by itself. The 5-seed HOUSE row has printed intervals and no registered verdict.

- **Shown:** 24 contrasts with intervals, plus M.
- **Sources:**
  - the contrasts section of each `read.txt` in `results/`: rows1_read, rows2_full_read, w2a_read, w2a_spd_read, w2b_lace_read, w2b_lci_read, c3hrnet_read, c3swad_read, c3x_read, final_tta_read;
  - HOUSE - PF on cv5v3: `results/HOUSEPF_READ.md` l12;
  - M: `results/final_tta_read/read.txt` l356.
- **Not drawn, because they have another comparator:**
  - EMA - RAWBN (`w2a_read` l683);
  - SOFTBAND - JMLHARD (`w2a_softband_read` l275);
  - the src_calib, DTI and OP-F rows of T16a;
  - CB_D4 - PF (information only).
- **LA-CE and LCI:** both rows show the relF1@2 - PF line printed in their reads. Neither is the arm's primary contrast: LA-CE's primary is mIoU-R13 against PFC, and LCI's is inactive region recall.

### F11: Guards per arm (`fig:F11`, chapter 7)
Caption:
> Guard values per arm on cv5v3 (5 seeds, OP-A), each taken against PF.
> - (a) False crack pixels on the crack-free cells, as a multiple of PF. The shaded region is the allowed range, up to the 1.5 x bound; the grey line is PF = 1.
> - (b) Crack width ratio arm / PF, pooled and on ARTS. The shaded band is 0.85 to 1.15.
>
> Filled markers: 532 pool cells. Open markers: 416 clean cells. * marks the selection-biased arms, CS and CS_D4. HOUSE values are printed without a registered rule.

- **Shown:** 48 values (8 arms x 3 guards x 2 cell sets).
- **Sources:**
  - `results/HOUSEPF_READ.md` l25 to l27;
  - `results/C3HRNET_READ.md` l17 to l19;
  - `results/c3swad_read/verdict.txt` l8 to l68;
  - `results/c3x_read/verdict.txt` l8 to l68;
  - `results/final_tta_read/verdict.txt` l11 to l32 (PF_D4) and l94 to l115 (CS_D4).
- **Not drawn:** OP-W values and the BMRK, CFVS and CSIR widths. They are in the same source sections. Two failing items are not drawn: HRNET's ARTS width at 416 OP-W (1.162) and HOUSE's CFVS width at 416 OP-A (1.164). The OP-W false-pixel failures are not drawn either.

### F12: Operating points against the 0.90 / 0.90 target (`fig:F12`, chapters 1 and 7)
Caption:
> Crack relP@2 against relR@2 on cv5v3 (532 pool cells, out of fold) for PF, PF_D4, CS and CS_D4. Each arm is shown at three operating points on its bias curve:
> - OP-A (argmax, filled marker);
> - OP-W (width-matched);
> - OP-F (F1 bias).
>
> Points are means over seeds 5 to 9, with SD bars. Small dots show, per seed, the arm's relR@2 at PF's OP-A relP@2 and its relP@2 at PF's OP-A relR@2. Shaded: the target relR@2 >= 0.90 at relP@2 >= 0.90, which no arm reaches. PF's OP-A and OP-W coincide. CS and CS_D4 (*) are selection-biased.

- **Shown:**
  - 12 operating points, each with SD;
  - 30 per-seed frontier dots for PF_D4, CS and CS_D4. PF's own frontier points equal its OP-A, are in the CSV, and are not drawn.
- **Sources:**
  - `results/final_tta_read/read.txt` l5 to l16 (levels) and l328 to l342 (frontier);
  - the target from `BRIEF.md` l57.
- **Not done:** the full bias curve. Neither RT nor `read.json` holds the curve points (see "OUTLINE corrections").

### F13: E1 primary and printed-beside contrasts (`fig:F13`, chapter 8)
Caption:
> E1 opening #8: the primary contrast P = C2 - C1 (crack relF1@2, OP-A) and the contrasts printed beside it, with seed-aware 95% intervals. The A/A row compares C1 seeds 7 and 8 against seeds 5 and 6.
> - Dashed line: margin M = 0.010.
> - Dotted line: the derived smallest detectable effect of P, about 0.074 (2.80 x SE 0.0265).
>
> Only P decides; the other rows decide nothing. C2 recipe averaged over seeds 5 to 9; OP-A; 101 of 106 cells CSIR.

- **Shown:** 9 contrasts with intervals, plus M and the MDE.
- **Sources:**
  - `results/final_opening_read/verdict.txt` l11, l43 to l50; P cross-checked against `verdict.json`;
  - the MDE from `thesis/THESIS_TABLES.md` l287 (T8 note, derived).
- **Not drawn:** the fixed-model interval of P (l19). It is in the CSV.

### F14: E1 strata of P (`fig:F14`, chapter 8)
Caption:
> E1 opening #8: P = C2 - C1 (crack relF1@2, OP-A) by stratum, with seed-aware 95% intervals. Numbers in brackets are cells / clusters. Dashed line: M = 0.010.
>
> Strata decide nothing. The BMRK stratum rests on 5 cells (C2 0.0000, C1 0.1843). The 74 crack-free cells score 0 for every arm and are not drawn. C2 recipe averaged over seeds 5 to 9; OP-A; 101 of 106 cells CSIR.

- **Shown:** 6 contrasts with intervals, plus M.
- **Source:** `results/final_opening_read/verdict.txt` l10 to l11 and l53 to l57.

### F15: E1 per-seed relF1@2 (`fig:F15`, chapter 8)
Caption:
> E1 crack relF1@2 per trained model for C1, C1-D4 and C2 at OP-A. Within each arm, the dots run left to right from seed 5 to seed 9. Bars and numbers are the arm means over the five models. Descriptive; decides nothing. C2 recipe averaged over seeds 5 to 9; OP-A; 101 of 106 cells CSIR.

- **Shown:** 15 per-model values and 3 means.
- **Sources:**
  - per model: `results/final_opening_read/verdict.txt` l23 to l32 and l36 to l40;
  - means: `results/final_opening_read/read_e1/read.txt` l6, l7 and l11.

### F16: E1 per-class IoU (`fig:F16`, chapter 8)
Caption:
> E1 per-class IoU of the 13 robust classes, C1 (open circles) against C2 (squares), at OP-A; arm means over seeds 5 to 9. Decides nothing.
> - sp mono is the one clear loss.
> - Material and edge dark are 0 for both arms.
> - Splice has no C2 value (n/a).
>
> C2 recipe averaged over seeds 5 to 9; OP-A; 101 of 106 cells CSIR.

- **Shown:** 25 values (13 for C1, 12 for C2).
- **Source:** `results/final_opening_read/verdict.txt` l63 to l75.

### F17: Domain-gap ladder (`fig:F17`, chapter 8, section 8.6)
Caption:
> Crack relF1@2 of the PF recipe across instruments (rows of Table T14), plus C2 on E1:
> - CV5: 532 and 416 pool cells, out of fold;
> - U2: simulated unseen-module views;
> - U1: held-out sources;
> - test50: all 50 cells, and the 16 cells without a pool cell in their module (in-distribution, known leakage, context only);
> - E1: all, full and half-cut cells.
>
> Levels of different models and sets, no interval. E1 rows: C2 recipe averaged over seeds 5 to 9; OP-A; 101 of 106 cells CSIR.

- **Shown:** 10 levels.
- **Sources (the same lines `SOURCES.tsv` gives for T14):**
  - `results/final_tta_read/verdict.txt` l222 and l234;
  - `results/stageB/U2U4_READ.md` l17;
  - `results/U1_READ.md` l12;
  - `results/final_opening_read/verdict.txt` l120 and l130;
  - `results/final_opening_read/read_e1/read.txt` l6, l7, l60 and l78.
- **Not drawn:** the E1 ranges over seeds. They are in the CSV.

### F19: Cost against quality (`fig:F19`, chapter 10, section 10.4)
Caption:
> Cost against quality for the E1 candidates, against E1 crack relF1@2 (OP-A):
> - (a) GFLOPs per cell;
> - (b) GPU time per cell (one RTX A6000, fp32, batch 1, median).
>
> C1, C1-D4 and C2 are means over seeds 5 to 9; the vertical line is the range over seeds, not an interval. E-PF and C3 are one ensemble each. The x axes are log scale. These are levels of different models on one set; there is no interval for the differences beyond those of Table T9. C2 recipe averaged over seeds 5 to 9; OP-A; 101 of 106 cells CSIR.

- **Shown:** 15 values (5 arms x GFLOPs, GPU s and relF1@2).
- **Sources:**
  - `thesis/INFERENCE_COST.md` (md5 1e5a9002; the script asserts it): l61 to l65 (section 3.3 GFLOPs) and l73 to l78 (section 3.4 GPU);
  - `results/final_opening_read/read_e1/read.txt` l6 to l11 (= TT T11a).
- **Not drawn:** CPU latency (section 3.3) and batch-8 GPU times. Both are in IC and can be added as a third panel if wanted.

### Not made
- **F20:** waits for the T3b read.
- **F1, F3, F4, F7, F8, F9, F18, F21:** belong to fig_maker_B.

## OUTLINE corrections (section 4, as read 23 Nov)
1. **F12:** "check that read.json holds the curve points". It does not.
   - `final_tta_read/read.json` `frontier` holds per seed only `relR2_at_ref_relP2` and `relP2_at_ref_relR2`; RT l322 to l352 prints the same.
   - So no bias curve can be drawn from result files. F12 shows the OP-A, OP-W and OP-F points and the per-seed frontier points.
   - The ch07 placeholder caption ("along the crack bias curve") needs this wording.
2. **F11 sources.**
   - RT l4 to l16 gives absolute levels for PF, PF_D4, CS, CS_D4 and CB only.
   - The guard values (arm / PF, per source) are in the verdict files and in C3HRNET_READ.md / HOUSEPF_READ.md, which F11 uses.
3. **F17:** OUTLINE lists 6 levels, but T14 and the ch08 placeholder caption list 10. F17 plots all 10 T14 rows.
4. **F19:** the status "pending (IC latency)" and "IC l23 (+ latency tables)" are outdated.
   - IC 1e5a9002 has GPU latency (section 3.4, l73 to l78) and the headline table (section 3.3, l61 to l65).
   - OUTLINE section 2, 10.4 "latency pending" is also outdated.
5. **TT line numbers.** OUTLINE pins TT at 707c7c46 and cites TT line numbers. TT is now 8c550be1 (revised 23 Nov), and its lines have moved; for example, the MDE note is l287.
6. **BR l57:** reads "Not reached (0.866 at 0.930)". That does not match the CV5 C2-recipe values the OUTLINE uses (RT l14: relP@2 0.9216 / relR@2 0.8211). F12 takes only the 0.90 / 0.90 thresholds from BR l57.
7. **F10 sources** `w2b_lace_read/` and `w2b_lci_read/`: these arms' primary contrasts are not relF1@2 against PF (see F10 above).

## F20 (added 23 Nov, after the T3b read)
The "Not made" entry above (F20 waits for the T3b read) is superseded by this section.

### F20: Few-shot track, ZS, HALF and ALL per stratum (`fig:F20`, chapter 9, `ch09_t3b.tex`)
Caption:
> Few-shot track (E1 opening #9).
> - (a) Crack relF1@2 contrasts ALL - ZS, HALF - ZS and ALL - HALF, with seed-aware 95% intervals, for all cells and per stratum. Numbers in brackets are cells / clusters; hard = half-cut cells with scuff. Solid line: zero; dashed line: M = 0.010.
> - (b) Crack relF1@2 levels of ALL, HALF and ZS, as the mean over the three seeds. The bar runs from the lowest to the highest seed and is not an interval.
>
> ALL is trained on the pool plus the E1 cells of the other 4 folds; HALF on the pool plus a fixed half of those image ids. Only P = ALL - ZS on all cells decides (confirmed, +0.2213 [+0.0977, +0.3504]); HALF - ZS and ALL - HALF are printed beside and decide nothing. On half-cut cells without scuff, the ZS level (0.8870) is above those of ALL and HALF. BMRK (5 cells; ALL and ZS score 0) and the 74 crack-free cells (every arm scores 0) are degenerate and not drawn. E1, out of fold over 5 folds of E1, seeds 5 to 7, OP-A; ZS = zero-shot C2 seeds 5 to 7; 106 cells, 71 clusters; strata decide nothing.

- **Shown:** 21 contrasts with intervals (panel a: 7 groups x 3 contrasts), 21 levels with their seed ranges (panel b: 7 groups x 3 arms), plus M. 127 plotted numbers.
- **Groups:** all 106 cells; full; half-cut; hard; half-cut without scuff; crack cells; CSIR.
- **Sources** (registered read outputs of `results/t3b_open9_read/`; the script asserts their md5s):
  - `verdict.txt` (bfe583db): l5 (n), l6 (P and M), l9 (outcome), l17 and l18 (HALF - ZS, ALL - HALF on all cells), l26 to l30 and l32 (strata);
  - `read_t3b/read.txt` (922b965e): levels, mean [min, max] over seeds 5 to 7, l7 to l9 (all), l27 to l29 (CSIR), l57 to l59 (crack cells), l77 to l79 (full), l87 to l89 (half-cut), l97 to l99 (hard), l107 to l109 (half-cut without scuff);
  - `read_t3b/read.json` (1589711a): cross-check only, not plotted.
- **Checks in the script:**
  - every plotted contrast and level equals `read.json` (seed-aware relF1_2; summary mean, min, max) within 5e-5;
  - cells / clusters agree between `verdict.txt` and the `read.txt` subset headers;
  - on all cells, the panel-b range ends equal the lowest and highest per-model values of `verdict.txt` l36 to l44;
  - the outcome on l9 is CONFIRMED.
- **Check run on 23 Nov:** all 154 numeric CSV values (value, lo, hi) appear verbatim on their cited source line.
- **Not drawn, but in the CSV with drawn = no:**
  - BMRK (5 / 5 cells / clusters, `verdict.txt` l33): ALL - ZS +0.0000, HALF - ZS +0.5443 [+0.0000, +0.8745], ALL - HALF -0.5443;
  - crack-free cells (74 / 55, `verdict.txt` l31): every contrast +0.0000;
  - the 9 per-model values (`verdict.txt` l36 to l44), kept as the check of the panel-b ranges.
- **Not drawn, not in the CSV:** the fixed-model intervals; the `type:full` and `type:halfcut` subsets of `read.txt`, which duplicate `strat_full` and `strat_halfcut`.
- **Colours:** ALL blue square, HALF vermillion diamond, ZS grey circle (grey because ZS is the comparator). ALL - ZS and HALF - ZS take the colour of their first arm; ALL - HALF is green. P is drawn thicker and labelled.
- **Size:** 15 x 10.2 cm. `\FIG` scales to at most 0.42\textheight (about 10.4 cm on A4 with 2.5 cm margins), so F20 prints at full size and 9 pt.
- **OUTLINE wording:** "ZS, HALF, ALL relF1@2 with intervals". The read prints intervals only for contrasts; the levels carry the range over the 3 seeds, which panel b shows and the caption names.
- **Rebuild:** `src/make_all_A.sh` does not list F20. Run `CUDA_VISIBLE_DEVICES= PYTHONDONTWRITEBYTECODE=1 nice -n 10 /home/noob/work/el-fault-detection/.venv/bin/python src/make_F20.py` from `thesis/figures/`.
- **Chapter:** the caption text of `\FIG{F20}{...}` in `thesis/chapters/ch09_t3b.tex` is replaced with this caption in LaTeX form.
