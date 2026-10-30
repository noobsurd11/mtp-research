# Spec B3: scuff as its own class (draft for a protocol after protocol_100)

coach, 30 Oct 2026. User decision (via team-lead): train scuff as its own class. It runs on the best recipe from protocol_100 and is not folded into its 4 arms. Tags: E measured, S judgement.

## 1. Labels that exist today (E; raw E-SCDD masks `el-fault-detection/data/escdd_masks` vs our `labeled/masks_escdd`, CPU read 30 Oct)
- **Train: 12 cells carry E-SCDD scuff (class 25), 3,246 px.**

  | Source | Cells (scuff px) |
  |---|---|
  | ARTS | ARTS_00039_r10_c1 (151), ARTS_00039_r6_c4 (90), ARTS_00041_r9_c4 (200), ARTS_00048_r2_c5 (404), ARTS_00051_r6_c2 (47, 5% list) |
  | BMRK | BMRK_00055_cell0115 (1,013) |
  | CSIR | CSIR_00092_r11_c5 (310), CSIR_00117_r8_c4 (437), CSIR_00155_r5_c5 (139, 5% list), CSIR_00161_r4_c6 (183), CSIR_00175_r8_c3 (225), CSIR_00176_r5_c2 (47) |

- **What masks_escdd calls those px today** (P6 remapped them to the old labels, `handbook/17` l.119): background 1,207, material (13) 1,390, **crack (14) 649** in 6 cells.
  - So our training labels already teach "scuff streak = crack" on 649 px, and "= material" on 1,390.
- **Star (28):** 238 px in 3 train cells, remapped to bg 176 / crack 54 / sp_multi 8. Not part of B3; star stays as now.
- **Test:** 2 cells, ARTS_00047_r3_c1 (34) and ARTS_00051_r3_c2 (202). All 236 px are crack in our test GT.
- **Val:** 0 scuff px.
- **E1:** scuff sits in the ext117 ignore masks. The 4 largest E1 half-cut crack cells carry a 2.5k-4.6k px scuff streak each, with the crack GT branching off it (`team_2026-10-27_unlabelled/ideas.md` F11).

## 2. Does it need new labels?
- **No, for a first test.** The 12 train cells give 3,246 scuff px from the raw E-SCDD masks; no annotation is needed.
- **But it is thin.** 12 cells, 0 half-cut cells and about 0.1% of train px. The E1 failure context (half-cut + scuff, 0.13 recall) has no train example.
- The B2 mined cells, if the user later labels 20-40 of them (crack + scuff), are what would make B3 strong. So B3 v0 is the label-definition fix; B3 + B2 labels is the real test (S).

## 3. Design (one change vs the best recipe)
- **Masks `masks_escdd_s`:** masks_escdd with the raw E-SCDD scuff px set to a new class 24 "scuff", in the 12 train cells only. Val, test and E1 masks are unchanged.
  - The 649 scuff px now labelled crack stop being crack in train. That is part of the change and is disclosed.
- **Model:** 25 output classes (the head grows by one channel); the loss as the house recipe (CE + Dice on all trained classes).
  - Scuff is weighted like any other class. No class weighting is added; that would be a second change.
- **Scoring on the 24-class metrics:** a predicted scuff px is mapped to background (0) before the confusion matrix (pre-stated). Crack metrics only see it as "not crack".
- **Arms:** BEST (from protocol_100: SUP100-g or SUP100-PF, whichever is chosen by its own verdict) vs BEST+S. 5 v 5, seeds 0-4, same commit and machine. BEST may be reused from protocol_100 only after a no-switch identity at the B3 commit.

## 4. Primaries, rule, and the metrics that matter for B3
- **Primaries unchanged** (rule 1 /3, two-set verdict): test crack IoU, crack relF1@2, inactive IoU. A WORSE fails B3.
- **Named secondaries, the reason for B3:**
  1. E1 crack px predicted on E1 scuff px (raw class 25; 27 Oct `scuff_check.py`), per run. Today about 8.7k px per run for L3 100%.
  2. E1 crack recall in the scuff + half-cut group, and E1 crack precision.
  3. Test crack precision and relP@2.
- **Test-label caveat:** 236 test crack px are E-SCDD scuff. B3 is scored on the frozen test GT, and also, descriptively, with those 236 px set to ignore.
- **Explicit user decision, before the B3 protocol is frozen** (team-lead, 30 Oct: test masks are not touched now):
  - **What happened:** P6 put scuff px back to their old labels. That made 649 train px and 236 test px (ARTS_00047_r3_c1, ARTS_00051_r3_c2) crack.
  - **Option (a):** keep the test GT as it is. B3 is penalised on 236 px for calling scuff "not crack"; that is about 0.26% of test crack px, so small.
  - **Option (b):** a new test mask version with those px as ignore. Every past number keeps its old-mask value, and both versions are reported from then on.
  - **Coach recommends (a) for the verdict and (b) as descriptive.** Changing test GT mid-series breaks comparability with FINAL and every P-series number.
  - The train-side change (the 649 px become scuff) is part of B3's one change and is disclosed.

## 5. Expected effect (S)
- **Test primaries:** n.d. (|Δ crack| < 0.005; 649 of about 272k train crack px change label). Below the 0.012 MDE, so this is run because the user asked, not because it can pass (`coach_strategy.md` rule 3).
- **E1 crack-on-scuff false alarms:** −20% to −60% per run. The model gets an explicit "streak = scuff" target instead of crack/material/background.
- **E1 crack recall, scuff + half-cut:** −0.02 to +0.03. Suppressing the streak can also suppress crack branching off it, and with 0 half-cut train cells there is little to learn the branch from.
- **E1 crack precision:** +0.01 to +0.04. Test crack precision: 0 to +0.01.
- **With B2 labels (20-40 scuff + crack half-cells):** E1 scuff-group recall +0.03 to +0.12 (27 Oct estimate). This is the version worth running if the user labels.

## 6. Code and gates (runner)
- A `data.mask_subdir=labeled/masks_escdd_s` build script (deterministic, per-cell px diff list, md5) and `model.num_classes=25` with the 24-class scoring map.
- Identity: the new commit with the old masks and 24 classes reproduces BEST for 1,000 steps.
- Smoke: 2k steps, the scuff class IoU logged on train cells only. No val/test scuff exists.
- Cost: 5 runs (about 12.5 h on gaint, 3 lanes), plus BEST if it is not reusable.
