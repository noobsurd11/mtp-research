# SYNTHESIS: unlabelled data, the SSL result, and the test set

`judge`, 27 Oct 2026. Inputs: `lit.md` (literature), `eval.md` (measurement), `ideas.md` (methods), `judge_notes.md` (my independent take, written before reading the others), `critique.md` (every challenge and verdict). No GPU was used; every new number is a CPU recompute of existing outputs.
Tags: **E** measured (file), **R** reasoned or literature (Research MCP id), **S** speculation. "Clean" = the 50 test cells minus the noisy cell `CSIR_00070_r8_c4`.

## 1. How to perceive the SSL result (plain words)
1. **What was tested:** label propagation only (pseudo-labels or consistency: Mean Teacher, FixMatch-style BsM, CPS, ALHVR, SKCDF, decoupled decoder), with the in-domain pool at 5-50% labels and the 11,938-cell CSIR/ARTS pool at 100%.
2. **What was not tested:** your actual intuition, learning features from the unlabelled cells (MIM or contrastive) and then fine-tuning. The 24 Oct team ranked it 7th and gated it out on a BMRK-only probe: too early as a test of your question, though the literature gives it a low prior (§3 item 3). Also not tested: unlabelled data that looks like the cells the model fails on.
3. **Where it worked:** with few labels. At 5%, SSL beats supervised on crack (+0.029 IoU) and inactive (+0.107); inactive gains last to 20% (E, handbook 11 rows 3, 10).
4. **Where it did not:** with many labels. On clean test cells a crack gain of +0.02 or more is excluded at 20, 50 and 100%, and +0.01 at 100% (E, `eval.md` §1.3; recipe Cs; the best recipe BsM was never run at 50-100%, and at 20% it is not excluded: +0.013 [−0.002, +0.033]). The capture metrics (component recall, inactive region recall) agree.
5. **This is not a bug or a bad method choice.** The literature predicts it: with all labels, extra unlabelled data gives +0.3 to +1.6 mIoU even with a strong encoder (R, doi:10.1109/tpami.2025.3528453). Crack IoU 0.49 is near the labelling ceiling: a perfect detector off by 1 px scores 0.48-0.60 (E, `eval.md` §2.2).
6. **What it does not mean:** that unlabelled data is useless (feature learning is untested), or that inactive is settled (at 50-100% an inactive gain below 0.03-0.05 would be invisible on this test).
7. **Where the remaining errors are, and why the pool cannot fix them:** 75% of unseen-module crack sits in 20 cells that combine half-cut multi cells and scuff streaks. Training has 0 half-cut cells, 12 cells with any scuff (3,246 px), and every run so far treated scuff as ignore, so that context is close to unlabelled. The model finds 0.13 of that crack (E, `judge_scripts/j6_e1_crosstab.py`). The pool barely contains this context.
8. Unlabelled data cannot teach a context it does not contain. Labels can.

## 2. Should the test set or primary metric change?
**Test set: no replacement. Add to it, pre-registered.**
- Keep the 50 cells as the continuity set. Every past verdict stays under its locked metric and cell set.
- **Add the clean set as co-primary from now on.** Set it by an image-only rule written before any new run: robust noise sigma > 10, which in test flags only `CSIR_00070_r8_c4` (and two train cells) (E, `results/p16/cell_noise_rank.txt`; `eval.md` §4).
- **E-SCDD's official test is unusable:** 48 of its 82 cells are in our train (E, handbook 17 §5.6).
- **E1 (unseen modules) stays sealed as a secondary.** Never select on it. Report it split by cell context (scuff + half-cut / other).
  - The split comes from mask classes, but it was found after seeing per-cell recall. Declare it post hoc once, then pre-register it for every later run.
- **Module-grouped 5-fold CV** over 693 labelled cells, with E1 and 17 `_rf` cells sealed outside, is the only way to power inactive: 74 inactive cells instead of 16 (E/R, `eval.md` §4).
  - It costs about 27 GPU-h per supervised arm and about 100 GPU-h per SSL contrast.
  - Do it only if inactive at 50% labels or more becomes the question. For in-distribution crack it adds nothing the clean test does not give.

**Primary metric: change it for future protocols only.**
- **Crack goal metric:** component recall at component precision ≥ 0.90, plus relR@2 at relP@2 ≥ 0.90. The operating point is the smallest crack bias that gives val component precision ≥ 0.90 (125 val components), frozen before test (`eval.md`, response r1).
- **Keep beside it:** strict IoU and mIoU_rob, as continuity and balance checks.
- Strict IoU at 100% labels mostly measures width and offset: 70% of FINAL's IoU loss is within 2 px of GT (E, `eval.md` §2.1).
- **Honest procedure:**
  1. write the protocol and commit it before any model is scored on the new set or metric;
  2. score every existing arm once;
  3. report old and new numbers side by side;
  4. label any effect that is significant only on the new set or metric as such.
- **Changing the metric would not have rescued the SSL null:** relF1@2, recall and component recall show the same null at 20-100% (E, `eval.md` §1.3, §3).

## 3. Ranked plan (value toward the goal; run order in the last column)
Costs: supervised R34 run about 1.1 GPU-h, so 5 seeds about 5.5 GPU-h; BsM run about 2.8 GPU-h (`trackM/results_r3.md`, `results/al1/launch.log`). Human-h are S.

| # | Item | Why (evidence) | Cheapest decisive test | GPU-h / human-h | Kill | Expected effect (S) | Run order |
|---|---|---|---|---|---|---|---|
| 1 | **Use the unlabelled pool as a mining source for labels where the misses are (not as SSL input).** (a) Scuff + crack cells in the pool's 1,152 half-cells: cell-level crack yes/no on all of them, pixel masks (crack and scuff) on 20-40. (b) BMRK via ELPV. User decision alongside: train scuff as a class instead of ignoring it | E: E1 failure = scuff + half-cut (75% of crack px, recall 0.126); half-cut without scuff 0.552; crack GT branches off the scuff streak (median 12 px), which the model paints as crack (about 8.7k px per run) (`eval.md` §5, `ideas.md` F11, F18). No run has ever trained on scuff (`ideas.md` F16). R4's 107 cells held only 4-5 scuff + crack cells (judge J0.10). Labels beat SSL at equal budget for crack (Track D, oracle-selected: Ts 0.352 vs BsM5 0.331). R: a few pixel masks plus many cell labels approach full supervision (doi:10.1016/j.compind.2021.103459) | (a) Re-validate the label-free proposer (model crack px on the streak; AUROC 0.80 on E1, post hoc, `ideas.md` F17) on the 43 labelled `_rf` half-cuts, never on E1 again. Then run it on the 1,008 pool half-cells outside module 300 (about 0.2 GPU-h). A human checks the top 100 and counts scuff + crack cells (1-2 h). (b) ELPV dedupe against our 60 BMRK cells (1 h CPU). The download needs the user's OK. Dedupe is a hard gate: 10 BMRK test cells are ELPV images | 0.2 + 5.5 per 5-seed rung / 3 + 2 (cell labels) + 6-10 (pixel masks) | Fewer than 15 scuff + crack cells in the top 100: go to item 5. With 15k or more new crack px: E1 scuff-cell recall Δ < +0.05. ELPV: fewer than 200 non-duplicate defective cells, or BMRK recall Δ < +0.03 | E1 scuff + half-cut recall 0.13 to 0.18-0.33; E1 crack recall +0.04 to +0.15; BMRK crack IoU +0.02 to +0.05; pooled test ≤ +0.01 (S; pool estimate 100-150 scuff + crack cells, S) | 2 (after item 4) |
| 2 | **Stop new label-propagation SSL at 20% labels or more.** A decision, not an experiment | E: +0.02 excluded at 20/50/100% (Cs recipe); +0.01 at 100%. At 100%, Sx100 leaves unseen-module inactive recall at 0.426, the same as A100 (judge J0.12). Its crack recall is −0.011 [−0.017, −0.004] (`eval.md` §1.3). Source-matched cells show no crack gain either: CSIR+ARTS +0.005, thr 0.011 (judge J0.11). R: literature predicts +0.3 to +1.6 mIoU at full labels | none | 0 / 0 | Reopen only with a pool that is i.i.d. with the weak sources, or with a new mechanism | Continuing: ≤ +0.01 crack | now |
| 3 | **One bounded test of your intuition:** continued MIM (SparK-style) pretraining of the ResNet-34 encoder from ImageNet, on the pool plus train images (about 12.4k), then fine-tune as A5c (5% first) | Never run (lead L1, holds). The 24 Oct gate rested on a BMRK-only probe. R: low prior. Thin-structure MIM gains in the literature are over scratch or across architectures. In-domain MAE ViT-Tiny lost the thin class to an ImageNet CNN (43.0 vs 59.1, arxiv:2605.12430). In-domain SimCLR lost on EL crack (arxiv:2402.17611) | MIM5 vs A5c, 5 v 5, rule 1 on the three primaries, with BsM5 as yardstick. 5% is where the feature route has room and where a gain is visible | 1-5 pretrain (short continued schedule; 16-33 if paper-length, `ideas.md` cost basis) + 5.5; 100% arm +5.5 only if 5% passes / 4 | MIM5 − A5c n.d. on all three primaries closes the question: "feature learning from this pool does not beat ImageNet init on EL" | 5%: crack 0 to +0.02, inactive 0 to +0.05; 100%: 0 to +0.01 | 3, or in parallel if GPU is idle |
| 4 | **Inference-only checks, pre-registered, E1 descriptive:** (a) R34 + RN50 ensemble for E1 crack (RN50 lifts E1 half-cut recall 0.133 to 0.183, `ideas.md` F4); (b) FINAL + a BsM10/20 member for inactive; (c) BN re-estimation on pool half-cells; (d) frame and scale variants | E: a 5% SSL model beats SUP100 on E1 inactive (0.148 vs 0.064; 10 cells, about 6 modules; judge J0.1-J0.2). R: BN re-estimation +2.6 mIoU on GTA to Cityscapes (arxiv:2006.10726), but it cannot add an unseen context | Each variant scored once on test, val and E1, with the target metric and the precision cost | about 1-2 / 2 | No variant gains ≥ +0.05 on its target (E1 scuff-cell recall, unseen-module inactive recall) at a precision cost < 0.05 | (a) E1 half-cut recall +0.03 to +0.06; (b) unseen-module inactive recall +0.05 to +0.15 at a test-precision cost; (c, d) 0 to +0.03 | 1 |
| 5 | **Synthetic branch cracks along real scuff streaks** on pool half-cells (procedural branches or pasted train crack masks, starting at the streak edge), only if item 1 finds too few real cells | R: copy-paste lifts rare classes in natural images (doi:10.1109/cvpr46437.2021.00294); segmentation evidence for synthetic cracks is thin (`lit`). Risk: paste artefacts, or a model that learns 'crack near streak' too broadly | One 5-seed rung (SUP100 + synthetic in 20% of batches) vs SUP100: E1 scuff-cell recall and E1 crack-free false alarm, with in-split crack precision as guard | 5.5-11 / 12-20 | E1 scuff-cell recall Δ < +0.05, or in-split crack precision −0.05 | E1 scuff-cell recall +0.03 to +0.12; in-split ±0.01 | 4 (conditional) |

**Not ranked** (each argued in `critique.md` or `ideas.md`):
- more PL-SSL variants: item 2;
- foundation-model teachers: DINOv2 failed the BMRK probe (`trackD/verify_probe.md`), and SAM fails on thin, low-contrast structures (doi:10.1109/wacv61042.2026.00505);
- anomaly models: cell-level only;
- E-SCDD official test: leaks into our train.

## 4. Open disagreements
1. **Cause of the E1 crack gap: converged.** `ideas` first said unseen cell type (half-cut) and crack morphology. After the cross-tab it agrees: the cause is branch cracks off scuff streaks on half-cut cells. Its 'long dendritic crack' was the scuff streak (class 25). Still open: how many scuff + crack cells the pool really holds (S, 100-150) and whether a scuff class helps or suppresses crack near streaks (S, −0.02 to +0.08).
2. **MIM.**
   - `lit`: low prior, likely n.d. against an ImageNet init.
   - `ideas` and the lead: run it once, because it is the user's question. `ideas` fine-tunes at 100%, where it expects an undetectable in-split effect.
   - Judge: fine-tune at 5% first, where a gain could be seen; run 100% only if 5% passes.
   - Cost resolved: 1-5 GPU-h for a short continued schedule.
3. **Why the 100% null.**
   - `lit` first credited the non-i.i.d. pool.
   - Judge J0.11: the 20 test cells whose source the pool covers show no crack gain either (+0.005, thr 0.011).
   - Converged for crack: crack does not expand under self-training, and labels are many. For inactive the pool-match reading stays open and weak (3 cells).
4. **CV.**
   - `evalx`: run new arms as module-grouped CV.
   - Judge: only if inactive at 50%+ is pursued, since about 100 GPU-h per SSL contrast buys nothing for crack.
5. **The lead's point that features are not the bottleneck: weakened** (`critique.md` §1).
   - True for strict IoU in-distribution (convention ceiling).
   - Not true for the remaining capture gap: clean relR@2 0.866, component recall 0.834, BMRK.
   - Not true for E1, where 61% of half-cut crack is at p < 0.001.
6. **Independence:** `ideas` read `lead_position.md` before drafting. `lit` and `evalx` did not cite it.

## 5. What is already a thesis contribution
1. **A tight, measured null for label-propagation SSL at 20-100% labels on EL crack.**
   - On clean cells, +0.02 is excluded at 20, 50 and 100%, and +0.01 at 100% (E; Cs recipe).
   - The earlier "+0.028" at 100% was one seed failing on one noisy cell (E, `eval.md` §1.3).
2. **SSL's benefit depends on label scarcity and on the class.**
   - At 5%: crack +0.029, inactive +0.107. Inactive keeps gaining to 20%; crack fades by 10-20%.
   - This fits the expansion account (arxiv:2010.03622).
   - On unseen-module inactive, a 5% SSL model beats the 100% supervised model (0.148 vs 0.064). That is descriptive and rests on 10 cells.
3. **Crack IoU has a convention ceiling.**
   - A perfect detector off by 1 px scores 0.48-0.60.
   - The duplicate cell agrees with itself at 0.53 (n = 1).
   - At 100% labels, 70% of the IoU loss is within 2 px. So capture metrics, not IoU, should judge "catch almost all cracks" (E, `eval.md` §2).
4. **"Unseen modules" decomposed.**
   - Inside our test, cells from unseen modules lose almost no crack: 0.486 vs 0.499.
   - They lose a lot of inactive: recall 0.43 vs 0.92 (E, judge J0.4).
   - The big E1 crack loss is a missing defect context (scuff + half-cut), not a generic shift (E, `eval.md` §5, judge J0.9).
5. **Negative results with mechanisms:** ALHVR-EL WORSE; SKCDF head n.d. (no prior collapse to fix); decoupled decoder n.d.; the joint-BN handicap; SemiCE invalid (handbook 11).
6. **Labels beat SSL at equal budget for crack** (Track D, oracle-selected). The pool's proven use is choosing what to label, not label propagation.

Limits on everything above: one split, 50 test cells (49 clean), 10 E1 inactive cells, cv02 only, untuned SSL recipes, oracle selection in Track D.
