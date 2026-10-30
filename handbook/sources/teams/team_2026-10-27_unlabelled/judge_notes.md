# judge: independent take, written before reading lead_position.md or any teammate draft

27 Oct 2026. Tags: E measured (file), R reasoned, S speculation. Scripts in `judge_scripts/`.

## 1. What has actually been tested with unlabelled data
- **Pseudo-label / consistency SSL only** (Mean Teacher family, hard or tolerant PL, CutMix, separate BN), plus 2-network variants (ALHVR-EL, CPS, SKCDF head, P17 decoupled decoder). All propagate teacher predictions; none learns features from unlabelled data without labels.
- **In-domain pool** (train minus labelled, 455 to 239 cells): 5% to 50%. **External pool** (11,938 CSIR/ARTS cells): joint-BN arms at 5-10% (P9-P12, broken BN), and one separate-BN arm at 100% with the weakest recipe (Sx100, tolerant, no CutMix).
- **Not tested at all:**
  1. the user's literal intuition: learn features from unlabelled cells (MIM / contrastive / DINO-style) then fine-tune. Gated out by Track D's probe rule, never run (handbook 13 C13 says the same);
  2. the best SSL recipe (BsM) with the 11,938-cell pool under separate BN, at any fraction; BsM at 50% or 100%;
  3. any use of unlabelled data aimed at unseen modules (BN re-estimation on target cells, self-training on target-like cells, teacher = the strong 100% ensemble);
  4. the rest of the Dropbox (>150k cells, 2,573 modules; only 11,993 downloaded, handbook 03 §6);
  5. more than one split.

## 2. What the null means (and what it does not)
- **E:** SSL is not null everywhere. At 5% BsM5 passes on all three primaries (+0.027 / +0.132 / +0.041, D7 rerun). At 10-20% BsM passes on inactive (+0.132, +0.060; P18 exploratory). P16's null at 20/50/100% is the Cs recipe (weakest crack arm in P13), on the 50-cell test.
- **E:** what labels buy dwarfs SSL on crack: +24 labelled cells +0.092 crack IoU vs BsM5 +0.029. Targeted +12 crack cells (Ts) reach 0.352 without any pool, above BsM5 0.331 (Track D).
- **E (Track M):** at 100% labels the in-distribution test is saturated against every lever tried: ResNet-50, +107 E-SCDD cells, 2x resolution, Dice variants all n.d. on test; only the 5-seed ensemble passes (+0.018 crack IoU clean). Crack IoU 0.47-0.49 sits near the label-noise ceiling (1-px shift of a perfect mask: 0.47-0.56; duplicate masks 0.257; handbook 13 A5).
- **R:** so "unlabelled data did not improve scores" means: pseudo-label SSL cannot beat a laddered supervised model on an in-distribution test whose crack metric is near its noise ceiling and whose inactive metric rests on ~3 cells. It does not mean unlabelled data cannot help; the representation-learning route and the unseen-module route were never tested.

## 3. My own recompute: where unlabelled data has shown its biggest effect (E1, unseen modules)
`judge_scripts/e1_seedrule.py`, `j2_e1_inactive_cells.py`; per-cell counts in `results/e1/raw_v2/`. Rule 1 on pooled IoU, seed means.
- **E1 inactive pooled IoU:** SUP100 (A100) 0.064; Sx100 0.107 (+0.042, thr 0.052, n.d.); BsM5 0.148, CsM5 0.139, BsM10 0.182, BsM20 0.135 (all BETTER vs their supervised, +0.11 to +0.13).
  - **A 5%-label SSL model beats the 100%-label supervised model on unseen-module inactive** (0.148 vs 0.064).
  - Caveat (E): 10 inactive cells, 9,158 px, from about 6 modules; one cell holds 35%, one module (CSIR_01637) 4 cells / 40%. Without the top 3 cells: BsM5 0.119 vs A100 0.020. Direction holds, sample is tiny.
- **E1 crack pooled IoU:** SSL − sup +0.003 (5%), +0.029 BETTER (BsM20), +0.019 BETTER marginal (S50, thr 0.018), −0.006 (Sx100). All absolute values 0.05-0.17; the best is SUP100-ensemble 0.172, recall 0.215.
- **E:** E1 modules are essentially absent from the external pool (1 of 71 parsed module ids; 0 of the 32 crack and 10 inactive E1 cells) (`j1_pool_e1_overlap.py`). So Sx100 was not a target-domain test either.
- **R:** the user's goal includes unseen modules. That is where the model is worst (crack recall 0.18-0.22, about 70% of GT crack at p < 0.001) and where SSL has its largest relative signal (inactive). The primary metric (50-cell test, 24 of 50 cells from train modules, 7 twins, all cells contain crack, cracks darker than val) does not measure that goal.

## 4. Test set and metric: my position before debate
- **Do not swap the 50-cell test or re-judge past verdicts.** That would be p-hacking.
- **Yes, add a pre-registered module-disjoint evaluation as a co-primary for new work**, declared before any new run. E1 (106 cells) has been opened as a secondary for every experiment, so it is not clean for selection; it can be a co-primary going forward only if no selection is ever made on it. A cleaner path: label a fresh module-disjoint set (S: 60-100 cells, about 6-10 human-h) and seal it.
- **Crack: report capture, not strict IoU, as the goal metric:** relR@2 at relP@2 >= 0.90 and component recall (Track M definitions already exist). Strict IoU stays as a continuity row.
- **Inactive:** component recall and pooled IoU need many more inactive cells (test 16 cells, 3 hold 59%; E1 10 cells). Any honest change here needs more labelled inactive cells in the evaluation, not a different statistic.

## 5. Draft ranking (to be challenged)
1. Fix the measurement first: module-disjoint sealed set + capture metrics, pre-registered. 0 GPU-h, ~6-10 human-h.
2. Cheapest unlabelled test on the unseen-module gap: BN statistics re-estimated on unlabelled target cells (inference only, ~1 GPU-h). Kill: E1 crack recall +0.03 or less and inactive IoU flat.
3. Self-training at 100% with the FINAL ensemble as teacher on a pool that resembles the target (CSIR modules not in train), student scored on the sealed unseen set. ~30 GPU-h. S: test flat; unseen inactive and crack recall up.
4. Targeted labels (crack cells, weak sources, unseen modules): Track D says this beats SSL on crack at equal small budget. Human-h, ~1 min/cell? (check labelling cost).
5. MIM / self-supervised pretraining on the pool (the user's literal idea): 1-2 GPU-days + 10 runs. R against: P15 transfer n.d./worse, bigger ImageNet encoder n.d. at 100%. Only after 2/3 show the unseen gap moves with unlabelled data, or as a single thesis-closing test of the intuition.
- "Stop chasing unlabelled data for in-distribution crack IoU" I already believe (E: saturated). Whether to stop entirely depends on the unseen-module result.

## 6. Added after notes v1 (still before teammate drafts): unseen module is not what kills E1 crack
`judge_scripts/j3_test_by_module.py` on Track M `final/final_cells.json` (test without the noisy cell; module = first two stem fields; "seen" = module has a train cell).
| | seen-module test cells (23) | unseen-module test cells (26) | E1 (106) |
|---|---|---|---|
| FINAL b0.75 crack IoU / recall | 0.499 / 0.711 | 0.486 / 0.697 | 0.172 / 0.215 |
| FINAL b0.75 inactive IoU / recall | 0.583 / 0.915 | 0.352 / 0.424 | 0.086 / 0.243 (results_final) |
| single seeds crack IoU | 0.481-0.487 | 0.460-0.469 | 0.148 |
- **E:** inside our test, a crack cell from a module never seen in training loses only ~0.015 crack IoU. Unseen modules cost **inactive** (recall 0.92 -> 0.43), not crack.
- **R:** E1's crack collapse (0.15-0.17) is not "unseen module" as such. It is something specific to the E1 cells: 101 CSIR cells from the 20221008 release (different imaging, contrast, crack type, or labelling convention). The unseen-module test cells are mostly BMRK/CFVS/ARTS (only 2 CSIR), so a CSIR-specific shift is not excluded. ideas is measuring image and crack stats on E1 (`ideas_scripts/e1_shift.py`); wait for it.
- **Consequence:** "unseen modules = domain shift = textbook place for unlabelled data" (a natural reading) needs care. For inactive it fits (seen/unseen gap inside test, and SSL's largest gains are on unseen-module inactive). For crack, the E1 gap must first be explained (image regime vs label convention) before spending GPU on adaptation.

## 7. E1 regime (from ideas' `e1_shift.csv`, summarised with their `e1_summary.py`; my mode check `j4_e1_modes.py`)
- E (ideas' numbers, not yet recomputed by me): E1 CSIR vs train CSIR, medians: brightness 180 vs 135, sd 57.7 vs 37.4, crack darkness vs ring 9 vs 16 (relative 0.071 vs 0.119), crack label width 3.6 vs 2.5 px. E1 per-cell crack recall median 0.14; 41% of E1 crack cells have recall < 0.1 (test 8%).
- E (mine): E1 images are RGBA grey 512 px like test (1 of 106 colourful), so not a conversion artefact.
- E (handbook 03 §6): pool CSIR brightness matches labelled CSIR (141 vs 142). So the 11,938 pool does not resemble E1 either.
- R: E1 = brighter, higher-contrast images with fainter, wider-labelled cracks. That is a covariate shift plus perhaps a label-width convention. The existing pool is not E1-like, which explains why Sx100 could not help E1 crack, and it means "use unlabelled data for unseen modules" first needs E1-like unlabelled images (Dropbox has 150k cells; unknown how many look like E1).
