# ideas: every credible way to turn unlabelled data into higher scores (27 Oct, v4)

Author: `ideas`. No GPU used. **E** = measured here or in a cited file; **R** = reasoned or literature (paper id); **S** = speculation.

**Independence note:** I read `lead_position.md` before drafting v1. §4 quotes it. My facts F1-F18 came from my own scripts. The scuff facts (F15-F18) were prompted by `evalx` (`eval.md` §5) and `judge` (j5, j6), and I re-measured them here.

Scripts and outputs are in `ideas_scripts/` (CSVs beside them):
- `e1_shift.py`, `format_stats.py`, `pool_stats.py`, `cell_pitch.py`, `halfcut_scale.py`, `ridge_search.py`;
- `e1_halfcut_recall.py`, `e1_halfcut_rungs.py`, `e1_halfcut_boot.py`, `e1_crack_confusion.py`, `e1_halfcut_allruns.py`, `e1_ladder_halfcut.py`;
- `scuff_check.py`, `scuff_proposer.py`.

Pool sample: 700 random pool cells copied read-only from cv02 (`pool_sample700.txt`). Masks: E-SCDD (`~/mtp/datasets/escdd_full`) and release `20221008`; for crack and inactive they are identical (handbook 17).

## 0. Bottom line
1. **E1's crack loss is one conjunction: branch cracks off scuff streaks on half-cut multi cells.**
   - Scuff is class 25, not in our taxonomy and ignored in scoring.
   - Scuff + half-cut: 20 crack cells, 75% of E1 crack px, FINAL recall 0.126.
   - Half-cut without scuff: 6 cells, 0.552. Scuff without half-cut: 2 cells, 0.51. Neither: 4 cells, 0.29.
   - Sources: `eval.md` §5, judge j6; my F15 agrees.
   - Our 473 train and 50 test cells contain no half-cut cells, and only 1 train cell has scuff ≥ 500 px (no crack).
   - The model paints the scuff streak as crack (L3: ~8.7k px per run on ignored px) and misses the branches: 71% of their GT px are called background.
2. **What the unlabelled pool offers for this.**
   - The 1,152 pool half-cells (8 modules) are at E1's scale (F7).
   - 5 of the 43 labelled `_rf` copies from those modules carry scuff, 4 with crack (F15). So scuff + crack cells likely exist in the pool slice: roughly 10% of 1,152, about 100-150 cells (S).
   - No external-pool SSL arm in our history moved E1 half-cut recall by more than +0.023 (F13). Pool SSL treats the pool as a whole; the target is a ~1% slice.
3. **Ranked levers for E1, all using unlabelled data as a source to mine:**
   1. propose scuff cells in the pool from the model's own crack-on-streak response (AUROC 0.80 on E1, F17), then pixel-label 20-40 scuff + crack cells and give every pool half-cell a cell-level crack yes/no (mixed supervision);
   2. synthetic branch cracks pasted along real scuff streaks;
   3. a scuff class in the taxonomy instead of ignore (user decision; 7 labelled scuff cells exist outside E1).
4. **In-split test.** At 100% labels, crack gains under +0.01 cannot be seen. Sx100 − A100 is −0.002 [−0.005, +0.002] on clean cells (`eval.md`), and finding every missed crack is worth about +0.09 IoU at most. So no unlabelled-data idea should be sold on in-split pooled crack IoU. ELPV (for BMRK, the weakest source) is the only in-split idea left; it must be judged on BMRK recall, not the pooled number.
5. **The user's intuition (self-supervised features) has never been tested.** One honest run is cheap if it continues from ImageNet with a short schedule: 1-5 GPU-h of pretraining (§2 basis), not 1-2 GPU-days.
   - Literature: continued pretraining beats ImageNet transfer on most of 16 datasets, but gains are small for segmentation (HPT `doi:10.1109/wacv51458.2022.00112`, via `lit`).
   - EL: in-domain SimCLR from scratch lost to ImageNet (Torpey `arxiv:2402.17611`).
   - Expected effect: about 0 in-split. On E1 it cannot supply crack-vs-scuff labels it never sees (S).

## 0a. Scuff vs half-cut, reconciled (answer to team-lead and judge)
- **Numbers, all agreed (judge j6, `eval.md` §5, my `scuff_check.py`).** E1 crack recall (FINAL):
  - scuff + half-cut: 20 cells, 75% of E1 crack px, 0.126;
  - half-cut alone: 6 cells, 0.552;
  - scuff alone: 2 cells, 0.51.
  Train has 12 cells with any scuff (3,246 px in total), only 1 of them at ≥ 500 px, and 0 half-cut cells. Scuff is ignore in every run.
- **Q1. Half-cut, scuff, or the combination?** The combination.
  - Half-cut alone is found at about in-split BMRK level, so my v1-v3 "unseen cell type" account was incomplete.
  - Scuff alone has only 2 cells, so "scuff alone is fine" is weak.
  - Reading (R): the failure is branch cracks off a broad dark streak the model was never taught to separate from crack (it paints the streak, F18) on a multi-crystalline half-cut background it has never seen. Neither factor alone explains 0.126.
- **Q2. Does it change ranks 1 and 2?** Yes.
  - Rank 1 now targets **scuff + crack half-cells**, not half-cells in general; labels cover crack and scuff. The proposer is the model's crack-on-streak response (F17).
  - Rank 2's backgrounds are **real scuff streaks on half-cells** (mined cells plus the 6 `_rf` scuff cells), with branches pasted off the streak edge. It no longer uses the plain letterboxed half-cells.
  - Frame and scale are demoted to rank 5.

## 1. Measured facts (E)
| # | Fact | Number | Script |
|---|---|---|---|
| F1 | E1 cells that are half-cut multi (class 29) | 58 / 105; 26 of 32 crack cells (16 modules); 83% of E1 crack px. Top-3 cells hold 27%, top-3 modules 60% | `e1_halfcut_recall.py` |
| F2 | Train / test half-cut cells | 0 / 473 (E-SCDD masks exist for 473 of 478) and 0 / 50 | same |
| F3 | FINAL (+0.75) E1, half-cut vs other | recall 0.165 vs 0.454; IoU 0.153 vs 0.342; relR@2 0.285 vs 0.691 (field order checked on test clean, 0.930 / 0.866); 61% vs 26% of GT px at p < 0.001 | same |
| F4 | E1 half-cut recall per Track M rung (5 seeds) | SUP100 0.133; R3 RN50 0.183; R5 ×2 0.161; R4 +107 0.123 | `e1_halfcut_rungs.py` |
| F4b | Contrasts vs SUP100 (post hoc subset, descriptive; cell bootstrap, not module-clustered) | R3 +0.050 (thr 0.014) [+0.026, +0.074]; R5 +0.027 (0.013) [+0.007, +0.050]; R4 −0.011 (0.013) [−0.023, +0.005] | `e1_halfcut_boot.py` |
| F5 | Where half-cut GT crack px go (FINAL) | bg 0.71, crack 0.17, border 0.08, inactive 0.00 (test: crack 0.70, bg 0.19, inactive 0.09) | `e1_crack_confusion.py` |
| F6 | Frame: landscape window | Rule: a row or column is "white" if ≥ 98% of its px are ≥ 250 (grey via PIL `L`). Content = non-white rows × columns. "Landscape half-cell window" = content aspect ≥ 1.6 and content height ≤ 360. Hits: 55 of 58 E1 half-cuts; 0 of 478 train, 0 of 50 test, 0 of 700 pool. White padding as such is common in train: BMRK and SDLE squares (59), plus ARTS and CFVS side pads. That is why judge's cruder rule flags 145 train cells. Frame matters little anyway: letterboxed half-cuts without scuff have recall 0.552 (judge j6) | `format_stats.py` |
| F7 | Scale: cell pitch from spacing-class lines in masks (x × y px) | train full 256 × 256 (all sources); E1 full 257 × 248; E1 half-cut 365 × 147; `_rf` half-cut 342 × 166. Pool and E1 half-cells share one scale (my eyeballed "0.5×" in v2 was wrong) | `cell_pitch.py` |
| F8 | Pool half-cells | 1,152 = 8 complete modules (CSIR 297-301, 333-335), the whole Dropbox half-cell folder (gaint `_inventory.json`). E1 half-cut modules: 43; overlap module 300 only. `lit`: 0 of 32 E1 crack cells share a module with any pool cell | inventory |
| F9 | `_rf` half-cuts (in R4) | 43 from the same 8 modules; 24 with crack; 2,855 crack px; width 2.70 px | `halfcut_scale.py` |
| F10 | Pool cells from E1's module era (CSIR ≥ 1600) | 1,228 multi + 1,068 mono, full cells | `pool_stats.py` |
| F11 | **E1 crack morphology (corrected)** | In the 4 largest E1 half-cut crack cells, the long dark streak is **scuff (class 25)**: 2.5k-4.6k px per cell. The crack GT is branches off it, a median 7.6-31 px from scuff. My v2/v3 wording, "dendritic cracks, GT as a line plus branches", was wrong: the line is scuff | `scuff_check.py` |
| F12 | Label-free ridge-filter crack search | fails at cell level (AUROC 0.47 on E1 half-cuts, 0.49 on train) | `ridge_search.py` |
| F13 | External-pool SSL vs matched in-domain arms, E1 half-cut recall | Sx100 0.121 vs A100 0.129-0.136; P9-P12 x-arms within −0.017 to +0.023 of their pairs. In-domain SSL did move scuff cells a little: S50 − A50 recall 0.080 → 0.110, BsM20 − A20 0.058 → 0.094 (`eval.md` §5) | `e1_halfcut_allruns.py` |
| F14 | Best half-cut recall in our history | P6 L0 100% (scratch, strong aug, weighted CE): 0.362, but precision 0.325 and crack predicted on 90% of crack-free half-cut cells (L3 100%: 0.136, 0.691, 7%). A discrimination gap, not a missed operating point | `e1_ladder_halfcut.py` |
| F15 | Scuff ≥ 500 px by group (cells / with crack ≥ 20 px); train with any scuff: 12 cells, 3,246 px total, 4 with crack | train 1 / 0; test 0 / 0; **`_rf` half-cut 5 / 4**; `_rf` other 1 / 1; E1 37 / 22 | `scuff_check.py` |
| F16 | Scuff labels outside E1 | 7 cells (6 `_rf`, 1 train). R4 mapped class 25 to ignore, so no run has ever trained on scuff | `scuff_check.py`; R4 mapping in `protocol_r4.md` |
| F17 | Label-free proposer for scuff cells, tested on E1 (labels only to score the proposer) | L3 100% total predicted crack px (incl. on ignored px): AUROC 0.80 for scuff, 0.82 for scuff + crack; precision@10 0.80 at base rate 0.35. FINAL's largest predicted crack component: AUROC 0.74 / 0.83. Within half-cuts only: 0.76 | `scuff_proposer.py` |
| F18 | L3 crack px on ignored px over E1 | 8,659 per run (mostly scuff) | `scuff_proposer.py` |

**Caveat on F17.** It uses E1 labels to score a proposer, so the proposer design has seen E1. Before mining, the proposer is re-checked on the 43 `_rf` half-cuts (5 with scuff, labelled, outside E1), and E1 is not used again.

## 2. Ranked table
Cost basis:
- R34 supervised run ~1.1 GPU-h (batch 8 at 512, 20k steps, packed lanes): 5 seeds ≈ 5.5 GPU-h. RN50 ~2 GPU-h per run (`results_r3.md`).
- Human-h are estimates (S). Expected effects are S, against SUP100 / FINAL.
- "E1-sh" = E1 scuff + half-cut crack recall (FINAL 0.126, 20 cells, 16 modules or fewer).
- `evalx` floor: in-split pooled crack effects < +0.01 are undetectable at 100% labels.

| Rank | Idea | Mechanism, and why it would or would not work here | Lit | GPU-h / human-h | Cheapest decisive test | Kill | Expected effect (S) |
|---|---|---|---|---|---|---|---|
| **1** | **Mine scuff + crack cells from the pool half-cell slice; pixel-label 20-40, cell-level crack yes/no on all 1,152 (mixed supervision).** Labels: crack and scuff | The failure is a defect context never trained (F11, F15, F16). Labels are the lever with proof here (Track D: targeted crack cells beat random, `verify_labelset.md`). Mixed supervision: a few pixel masks plus many cell labels ≈ full supervision on KolektorSDD2 (via `lit`). R4 is not counter-evidence: its 107 cells had 4-5 scuff + crack cells, and scuff was ignored | Mixed supervision `doi:10.1016/j.compind.2021.103459`; AL survey `doi:10.1016/j.media.2024.103201` | 5.5 / 1 h proposer + 2 h cell labels (~5 s each) + 6-10 h pixel labels | (a) re-validate the F17 proposer on the 43 `_rf` half-cuts; (b) run it over the 1,008 pool half-cells outside module 300 (inference, ~0.2 GPU-h); (c) human checks the top 100 and counts scuff + crack cells | < 15 scuff + crack cells in the top 100, so go to 2. After labelling (≥ 15k crack px): E1-sh Δ < +0.05 | E1-sh +0.05 to +0.20; E1 crack recall +0.04 to +0.15; in-split 0 |
| **2** | **Synthetic branch cracks along real scuff streaks**: backgrounds = pool half-cells with scuff (from 1) and the 6 `_rf` scuff cells; paste labelled train crack masks (×1.3, F7) and procedural branches starting on the streak edge, median 8-30 px long and branching outward (F11) | Gives the missing context without more labels. Risks: paste artefacts, and a model that learns "crack near streak" too broadly | Fractal crack sim `doi:10.1109/wacv57701.2024.00844`; SinGAN cracks `doi:10.1109/access.2025.3576335`; Copy-Paste `doi:10.1109/cvpr46437.2021.00294`; diffusion defects `doi:10.1609/aaai.v38i8.28696`. `lit`: segmentation evidence for synthetic cracks is thin | 5.5-11 / 12-20 h dev | One 5-seed rung (SUP100 + synthetic in 20% of batches): E1-sh, E1 crack-free false alarm; in-split guard | E1-sh Δ < +0.05, or in-split crack precision −0.05 | E1-sh +0.03 to +0.12 |
| **3** | **Scuff as a trained class (taxonomy change) instead of ignore.** User decision | The model spends crack on the streak (F18) and misses the branches. A scuff class gives the streak its own target, and may free crack for the branches, or suppress crack near streaks further. Labels exist: 7 cells outside E1 (F16), plus those from 1 | none found (S) | 5.5 / 0 now, + labels from 1 | R4 data with class 25 → a new scuff class (not ignore) vs R4, 5 v 5; read E1-sh and E1 crack-on-ignored px. Only 6 scuff cells, so it is weak alone; combine with 1 | E1-sh Δ < +0.03 and crack-on-scuff px not lower | E1-sh −0.02 to +0.08 |
| 4 | **ELPV as BMRK's unlabelled and weak-label pool.** **Hard gate:** dedupe against all 60 BMRK cells (10 are test) before any use; ELPV download (~0.1 GB) needs the user's OK | BMRK is the weakest in-split source and has no pool data. ELPV is the one source-matched (i.i.d.-like) pool we can get, the condition under which SSL gains persist (UniMatch V2 ablation via `lit`). Mine 12-20 BMRK crack cells (Ts arm: BMRK recall 0.312 vs R 0.242, `verify_labelset.md`) | ELPV `doi:10.1016/j.solener.2019.02.067`; UniMatch V2 `doi:10.1109/tpami.2025.3528453` | 5.5 / 1 h dedupe + 4-6 h | CPU: download, normalised-correlation dedupe calibrated on our 60 known BMRK cells; count non-duplicate defective cells | Dedupe uncertain for any test cell, or < 200 non-duplicate defective cells; or BMRK recall Δ < +0.03 | BMRK relR@2 +0.02 to +0.05; pooled test < +0.01, i.e. not detectable (`evalx` floor) |
| 5 | **Inference-only E1 checks** (white → grey frame; AdaBN on pool half-cells; AdaBN on E1 itself, transductive, declared) | Prior now lower: half-cuts without scuff already score 0.552 (judge j6), so frame and BN statistics are not the failure | Tent `arxiv:2006.10726` (`lit`: BN re-estimation +2.6, Tent +7.0 mIoU GTA→Cityscapes; fails on hard shift) | 0.5 / 1 | Pre-registered V0-V4 (§3.4) | No variant raises E1-sh ≥ +0.05 at precision drop < 0.05 | E1-sh 0 to +0.03 |
| 6 | **Self-supervised continued pretraining** (SparK MIM on our RN34, from ImageNet, short schedule) on pool + train (+ ELPV after dedupe); the user's intuition | Never run. HPT supports continuing from ImageNet with a short schedule; overfits past ~5k steps on small sets (`lit`). Against: Torpey, P15, Zoph (pretraining's value shrinks with more labels), `evalx` floor. Variant from `lit`: pretrain on ridge-filter pseudo-labels (VasoMIM SPT), but F12 shows ridge filters are weak on EL | SparK `arxiv:2301.03580`; HPT `doi:10.1109/wacv51458.2022.00112`; MIM small data `arxiv:2112.10740`; Torpey `arxiv:2402.17611`; Zoph `arxiv:2006.06882` | **1-5 pretrain** + 5.5 / 4 | One SparK run, 5-seed fine-tune as SUP100; BMRK AP, E1-sh, in-split as guard | In-split n.d. and E1-sh Δ < +0.03 | in-split 0 to +0.01 (undetectable); E1-sh 0 to +0.03 |
| 7 | **Encoder capacity** (RN50; R34 + RN50 union) | Not unlabelled data, but R3 moved E1 half-cut recall the most (F4b, +0.050) and lost inactive. A union could keep both | Track M R3 | 0.5 inference / 1 | Ensemble existing R3 + SUP100 checkpoints (inference only) | Union E1-sh ≤ R3's, or test inactive worse than SUP100 | E1-sh +0.03 to +0.06 |
| 8 | **Whole-pool active learning** (uncertainty band 0.001-0.95 + k-center diversity + source quota) | General form of 1 and 4. On CSIR/ARTS full cells it is capped: R4's +104 CSIR cells gave n.d. | Gaillochet `doi:10.1016/j.media.2023.102958` | 5.5 / 8-12 | Top 50 inspected for type spread | > 80% CSIR full cells | in-split < +0.01 |
| 9 | **Human-verified pseudo-labels alone** | Adds only what the model already sees: 61% of half-cut GT is at p < 0.001 (F3). Useful as the correction step inside 1 | – | 5.5 / 3-5 | 50 cells, timed | < 5k accepted px | ≤ +0.01 |
| 10 | **Anomaly / normality channel** | Low precision on multi grain; the frozen probe ranks only at low precision (`verify_probe.md`). Plausible as a scuff proposer, but F17's model-based proposer is already 0.80 | AD survey `doi:10.1007/s11633-023-1459-z` | 1-2 / 3 | Cell AUROC for scuff on `_rf` | AUROC ≤ F17's | triage only |
| 11 | **Foundation distillation / SAM** | DINOv2 failed the BMRK probe (`verify_probe.md`). SAM fails on thin, low-contrast structures, and fine-tuning does not fix it (`lit`: `doi:10.1109/wacv61042.2026.00505`). Use a brush plus model proposals for labelling, not SAM | DINOv2 `arxiv:2304.07193` | – | – | – | ≤ +0.01 |
| 12 | Pool filtering / curriculum SSL; noisy student | Pool SSL limited by the expansion step (SYNTHESIS §1); no pool arm moved E1 half-cut (F13). A scuff-slice pool (~1%) would need a teacher that already finds branches | Expansion `arxiv:2010.03622`; Zoph `arxiv:2006.06882` | 14-20 / 1 | Only after 1 | E1-sh Δ < +0.03 | 0 to +0.03 |
| 13 | Other sets as mining sources (Torpey's 22k, PV-Vision crack set, unlisted Dropbox folders, UCF-EL) | Worth it only if they hold half-cut cells with scuff, or BMRK-like cells | Torpey `arxiv:2402.17611`; PV-Vision `doi:10.1109/jphotov.2023.3249970` | 0 / 2 | Cell-type inventory | none found | 0 unless found |
| n/a | Readouts (`evalx`): E1 as two sealed readouts (scuff + half-cut; other) with module-cluster CIs; component recall | Not a method | – | 0 | – | – | – |

**MIM cost basis (judge item 4).** SUP100's U-Net++ R34 takes 148 GFLOPs forward per 512 image (`results_r3.md`). It runs 20k steps × batch 8 = 160k samples in ~1.1 GPU-h, i.e. ~40 samples/s. A SparK R34 encoder with a light decoder at 512 is ~25-30 GFLOPs forward, ~5× cheaper per sample, so ~200 samples/s (S). Budgets on ~15k images:
- HPT short schedule, 5k steps × batch 64 = 320k samples: ~0.5 GPU-h;
- 200 epochs = 3M samples: ~4 GPU-h;
- SparK's paper-style 800-1,600 epochs from scratch: 16-33 GPU-h, about the 24 Oct "1-2 GPU-days".

Hence 1-5 GPU-h, plus 5.5 GPU-h fine-tuning.

**Run order** (cheapest decisive first; not the value rank):
1. Rank 1 (a)-(c): ~0.2 GPU-h inference + ~3 human-h. In parallel: ELPV dedupe (CPU, after the user's OK) and rank 7's inference-only union.
2. Then rank 1 labelling, or rank 2 if the count fails. Rank 3 rides on rank 1's labels.
3. Rank 6 runs once, as the honest test of the user's intuition, when GPU is idle.

## 3. Top 3 in detail
### 3.1 Mine scuff + crack cells (rank 1)
- **Where:** the pool's 1,008 half-cells outside module 300 (F8). Then pool multi ≥ 1600 (F10) and unlisted Dropbox folders if the half-cell slice runs dry.
- **Proposer:**
  - L3 / FINAL total predicted crack px, including where crack is predicted on a streak (F17).
  - Re-validate on the 43 `_rf` half-cuts first (5 scuff); E1 is not touched again.
  - The ridge filter does not work (F12).
- **Labels:**
  - pixel masks for crack and scuff on 20-40 proposed cells, following E1's convention (branches off the streak; streak as scuff);
  - cell-level crack yes/no for all 1,152 half-cells (~5 s each).
  - Train with mixed supervision (Bozic): segmentation loss on pixel cells, a cell-level classification loss on the rest.
- **Rule fixed before any E1 number:** label every proposed cell the human confirms; no selection on E1 scores. E1 stays sealed.
- **Decision:** one 5-seed rung vs SUP100; E1-sh is the named secondary with module-cluster CIs; in-split primaries guard.

### 3.2 Synthetic branch cracks along scuff streaks (rank 2)
- **Backgrounds:** pool half-cells with scuff (mined in 3.1) and the 6 `_rf` scuff cells, plus streak-free half-cells as negatives.
- **Cracks:** short branches starting at the streak edge and running outward 8-30 px, branching; width 3-4 px (E1 width 3.65, `eval.md`); darkness matched to E1 (ring minus crack ~11 grey levels).
- **Labels:** crack on the branches; the streak is scuff (if rank 3 is adopted) or ignore.
- **Guards:** in-split crack precision; E1 crack-free-cell false alarm.

### 3.3 Scuff as a class (rank 3)
- **Why cheap:** a mapping change. 7 labelled scuff cells exist outside E1 (F16). It is a taxonomy decision for the user, because it adds a 25th class to every model.
- **Test:** R4 data, class 25 mapped to a new trained class instead of ignore, 5 v 5 against R4. Read E1-sh and E1 crack px predicted on scuff (F18: 8.7k per run now).
- **Expectation:** weak alone (6 scuff cells); its real test is jointly with rank 1's labels.

### 3.4 Pre-registration stub for the inference-only checks (rank 5)
- **Models:** FINAL (+0.75 and 0) and 5 SUP100 seeds.
- **Cells:** E1 106, read as scuff + half-cut and other; test 50 as a control.
- **Variants:**
  - V0, as is;
  - V1, white letterbox → cell-median grey;
  - V2, content ×0.77;
  - V3, AdaBN on E1 (transductive, declared);
  - V4, AdaBN on the 1,152 pool half-cells.
- **Decision:** works if E1-sh recall rises ≥ 0.05 at precision drop < 0.05, on FINAL and the SUP100 seed mean.

## 4. Where I disagree with earlier rankings
- **SYNTHESIS (24 Oct) §2 row 1, "stop new SSL methods for crack"**: holds for the in-split test (`evalx` floor). E1's failure (scuff branch cracks on half-cuts) is invisible to the in-split test, so that verdict says nothing about E1.
- **Lead position point 3** ("pool CSIR/ARTS only; Sx100 n.d. on E1"): correct outcome. The sharper reason: the relevant slice is ~1% of the pool and the defect context was never trained (scuff ignored). Mining, not propagation, is how the pool can help.
- **Lead position point 5** ("pool's best use: choose what to label"): agree, and it can now be specific: scuff + crack half-cells, with a measured proposer (F17).
- **MIM gated out by the frozen probe:** that probe was BMRK in-split. I keep MIM as one cheap honest test (1-5 GPU-h pretraining), not out.
- **My own v1-v3:**
  - "frame and scale" as rank 1 was wrong; half-cuts without scuff score 0.552;
  - F7's 0.5× scale was wrong;
  - F11's "dendritic crack" was the scuff streak.
  All three are corrected above.

## 5. Response to judge
- **r1.1 / r2 (scuff).** Accepted and re-measured.
  - The long dark line in my F11 cells is class 25 (F11); §0 and ranks 1-3 are re-targeted at scuff + crack.
  - Frame/scale is demoted to rank 5, with lower expected effect.
- **r1.2 (letterbox rule).** Exact rule in F6. Its "landscape half-cell window" test, not white padding as such, gives 0 of 478 train. Your cruder rule counts BMRK/SDLE squares and ARTS/CFVS pads.
- **r1.3 (do pool modules contain scuff?).** Yes in the labelled sample: 5 of 43 `_rf` half-cuts, 4 with crack (F15). The no-label proposer is in F17 (AUROC 0.80 on E1), to be re-validated on `_rf`.
- **r1.4 / r2.c (MIM GPU-h).** Basis above: 1-5 GPU-h for a continued short schedule; 16-33 GPU-h for paper-length from-scratch schedules.
- **r1.5 (ELPV).** Dedupe is a hard gate (rank 4); the download needs the user's OK.
- **r1.6 / r2.d.** Independence note at the top: I read `lead_position.md` before drafting.
- **r2.b (scuff class vs more crack labels).** A scuff class is the cheaper change (mapping plus 7 existing cells), but it is weak alone. More scuff + crack labels (rank 1) is the stronger lever. I rank labels first and the class third; the class is a user decision.
