# Proposal for the user: track T3b, few-shot layout adaptation inside E1

benchdesign, 12 Nov 2026. A proposal, not a decision (lead decision D5 goes to the user). Counts are from ground-truth masks and lists only (`scripts/t3b_counts.py` b1b9dfb7, output `out/t3b_counts.txt`, draft folds `out/t3b_draft_folds.tsv`). Tags: E measured, R from a file of another team, S judgement.

## 1. The idea
- **T3 stays as it is:** E1 (106 cells) is the zero-shot unseen-module, unseen-layout test. No model in T3 has seen an E1 cell or a labelled half-cut cell.
- **T3b adds a second question:** how much does a model gain once it has labelled cells of the new layout, and roughly how many does it need? Method: a group K-fold inside E1 (groups = image ids). For fold k, train on the 532 cv5v2 pool cells plus the E1 cells of the other folds, score the held-out E1 cells. Pooled over folds, every E1 cell gets one out-of-fold prediction.
- **By-product:** a deployable model trained on 532 + all 106 E1 cells. It has seen half-cut cells; its expected score on such cells is the T3b out-of-fold number (it has no held-out half-cut set of its own).

## 2. What E1 holds (E)
| Quantity | Value |
|---|---|
| cells / image ids | 106 / 71 |
| half-cut cells | 62 |
| cells with a scuff streak (>= 500 px) | 37 |
| crack cells (>= 20 px) / crack px / crack components >= 20 px | 32 / 32,294 / 296 |
| crack cells in the hard stratum (half-cut + scuff) | 20, in **10 image ids**, with 24,246 px (75%) |
| crack-free cells | 74 |
| inactive cells / px / image ids | 10 / 9,158 / 7 (top 3 hold 87%) |
| share of crack px in the top 1 / 3 / 5 / 10 image ids | 0.22 / 0.50 / 0.69 / 0.86 |

## 3. Fold counts (E; deterministic greedy folds by image id, hard-stratum crack px balanced first)
**K = 3**

| Fold | Held-out cells | Half-cut | Scuff cells | Crack cells | of which hard | Crack px (share) | Components | Crack-free | Inactive cells (px) | Train side from E1: cells / half-cut / crack cells / hard crack cells |
|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 36 | 20 | 9 | 6 | 5 | 11,112 (0.34) | 83 | 30 | 1 (57) | 70 / 42 / 26 / 15 |
| 1 | 36 | 21 | 13 | 13 | 7 | 10,614 (0.33) | 108 | 23 | 8 (8,068) | 70 / 41 / 19 / 13 |
| 2 | 34 | 21 | 15 | 13 | 8 | 10,568 (0.33) | 105 | 21 | 1 (1,033) | 72 / 41 / 19 / 12 |

Largest single image id in each held-out fold: 64%, 53%, 33% of that fold's crack px.

**K = 5**

| Fold | Held-out cells | Half-cut | Scuff cells | Crack cells | of which hard | Crack px (share) | Components | Crack-free | Inactive cells (px) | Train side from E1: cells / half-cut / crack cells / hard crack cells |
|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 22 | 12 | 5 | 4 | 4 | 7,068 (0.22) | 70 | 18 | 1 (57) | 84 / 50 / 28 / 16 |
| 1 | 22 | 13 | 6 | 6 | 4 | 6,053 (0.19) | 63 | 16 | 5 (4,256) | 84 / 49 / 26 / 16 |
| 2 | 20 | 13 | 7 | 11 | 6 | 6,143 (0.19) | 51 | 9 | 2 (3,664) | 86 / 49 / 21 / 14 |
| 3 | 21 | 12 | 9 | 6 | 2 | 6,014 (0.19) | 52 | 15 | 0 (0) | 85 / 50 / 26 / 18 |
| 4 | 21 | 12 | 10 | 5 | 4 | 7,016 (0.22) | 60 | 16 | 2 (1,181) | 85 / 50 / 27 / 16 |

Largest single image id in each held-out fold: 100%, 92%, 57%, 51%, 46% of that fold's crack px.

- **Stricter grouping.** E1's CSIR image ids run from 300 to 2,328; the 10 hard image ids are 1621, 1637, 1647, 1679, 1717, 1951, 2026, 2222, 2228, 2301. Grouping consecutive ids into families gives 58 units (gap <= 1), 44 (gap <= 5) or 37 (gap <= 10); the top-3 share of crack px stays 0.50 to 0.56. Folds by family have the same crack balance but uneven sizes (14 to 50 cells per fold). Whether neighbouring ids are modules of one batch with the same handling marks is not known (not measured).

## 4. The concentration problem
- Half of all E1 crack px sit in 3 image ids, and the 20 hard crack cells in 10. With K = 5, two folds are in effect one image each (`CSIR_01717`, `CSIR_01637`).
- So a single fold's score says little. Only the score pooled over all folds is usable, and its uncertainty is that of about 9 images (effective n 8.6 for crack px).
- "How many labelled cells are needed?" can only be answered coarsely: a training side holds 12 to 18 hard crack cells from at most 9 image ids, so a learning curve has two honest points (about half, and all). Which images are in the half matters more than how many.
- Inactive cannot be answered at all (3 images).

## 5. What T3b can and cannot detect (S, anchored on E and R numbers)
| Anchor | Value | Source |
|---|---|---|
| zero-shot crack recall, hard stratum / half-cut without scuff / in-distribution test | 0.126 / 0.552 / 0.703 | E `eval.md` §5 |
| zero-shot E1 relF1@2 (single models to ensembles); any-hit component recall (ensembles) | 0.41 to 0.47; 102 to 122 of 296 | R `BRIEF.md` §3; `H21` §5 |
| seed-rule thresholds on E1, 5 v 5 single models | relF1@2 0.035 to 0.043; any-hit 0.052 | R `H20` §6.0; `H21` §2, §4 |
| half-width of 71-cluster intervals for ensemble contrasts on E1 | 0.026 to 0.057 | R `H20` §5, `H21` §5 |
| cross-validation doubled the planned standard error in B6 | 0.020 planned, 0.038 realised | R `H21` §3 |

- **Detectable:** a gain of about +0.10 or more in pooled out-of-fold relF1@2 or any-hit recall over the zero-shot model on the same 106 cells. If labels of the layout close half of the gap on the hard stratum (recall 0.13 towards 0.40), the gain is well above that.
- **Not detectable:** differences between two adapted methods below about 0.05 to 0.10; anything about inactive; a smooth learning curve.
- **Confound to control:** E1 labels are about 1.5x wider than train labels. A model trained on E1 learns that width, which lifts strict IoU and pixel recall without finding more cracks. T3b is therefore read on any-hit component recall and relF1@2, with the predicted width reported.

## 6. Rules that keep T3 clean
1. **Order.** The T3 table is frozen first. No T3b training run starts until every T3 entry has been scored at its registered opening.
2. **Separation.** A model whose training set held any E1 cell (or a `CSIR_00300` `_rf` cell) is never reported in T3, nor in an E1 column of any other track. Its run manifest carries a `trained_on_e1` mark and the scorer refuses to mix marked and unmarked runs in one table.
3. **No selection on E1, in either track.** T3b uses a recipe fixed beforehand (the recipe chosen on CV5-G), final weights, argmax. If a crack bias is used, it is fitted on the training folds only.
4. **One registered protocol and one opening,** logged in `e1_openings.md` with the note that E1 is training data for T3b models from that date.
5. **Frozen folds.** By image id, hard-stratum crack px balanced, list and md5 committed before any run (the draft is `out/t3b_draft_folds.tsv`).
6. **Labels.** E1 classes 25 to 28 (scuff, corrosion cell, brightening, star) are ignore in training as in scoring; 24 and 29 map to sp mono and sp multi.
7. **Reporting.** Pooled out-of-fold headline card on the two strata, any-hit recall, false alarms on the 74 crack-free cells, a 71-cluster interval, and the zero-shot number of the same recipe beside it.

## 7. Cost
K = 5, house recipe, 2 seeds: 10 runs for the "all E1 training folds" arm and 10 for a "half" arm, about 22 GPU-h; the zero-shot comparator is the cv5v2-pool model of the same recipe and seeds. The deployable model is one more run per seed.

## 8. Recommendation (S)
**Run T3b, late and small:** K = 5 by image id, two arms (half, all), the final recipe only, 2 seeds, one opening in the last week, after the T3 table is frozen.
- Why: modern modules are mostly half-cut, and without T3b the delivered model has never seen a half-cut label. The expected effect is large enough to see despite the concentration. It turns "the model fails on a new layout" into "this many labelled cells buy this much", which is what WattCycle needs to plan labelling.
- Why K = 5 and not 3: each fold model sees 84 to 86 E1 cells and 14 to 18 hard crack cells instead of 70 to 72 and 12 to 15, closer to the deployable model; the per-fold imbalance is bad in both and only the pooled score is used.

**Strongest argument against.** E1 is the only unseen-module set and T3b spends it. After T3b, the team has trained on these cells and seen which of them respond, so any later zero-shot claim on E1 by the same team is weaker, whatever the rules say. And the answer rests on about 10 images of one source, 3 of which hold half of the crack pixels; folds by image id cannot rule out that neighbouring modules share the same handling marks, so the out-of-fold number may be optimistic for a truly new site. If the user wants E1 to stay a clean zero-shot set beyond this thesis, T3b should not be run.
