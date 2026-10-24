# Protocol R2: soft Dice on 12 foreground classes (CE + Dice), 100% labels

MD, 24 Oct 2026. Status: **APPROVED by MC** (review_r2.md) after fixes F1 (pass rule) and F2 (grad-norm logging), applied 24 Oct.

## What I had seen when writing this
- M0 (`baseline.md`, APPROVED): per-class test and val IoU / P / R of SUP100 (gridline R 0.326, splice never predicted, edge_dark R 0.394).
- No R2 run exists. This rung was chosen from those M0 per-class numbers, so it is test-informed at the level of "which classes are weak". Disclosed. The class list below is fixed from **train** GT counts only.

## Question
Does adding a soft-Dice term for the other well-represented classes, at the same per-class weight crack and inactive already have, raise all-class mIoU without costing crack or inactive?

## Hypothesis
- Under CE alone, thin and rare classes are under-called: gridline R 0.33, splice 0, edge_dark R 0.39.
- A batch Dice term per class targets overlap directly, as it did for crack and inactive in P6 (L2 → L3).
- Expected (S): mIoU_rob +0.02 to +0.04; crack IoU within ±0.01.

## The one change
- **Comparator SUP100** (L3): `loss.supervised=ce_dice`, defaults `dice_classes=(14, 11)`, `dice_weight=1.0`, so the loss is CE + 0.5·(Dice_crack + Dice_inactive).
- **R2:** `loss.dice_classes=[1,2,4,5,9,11,13,14,15,16,20,21] loss.dice_weight=6.0`, so the loss is CE + 0.5·Σ_c Dice_c over 12 classes.
  - Crack and inactive keep their L3 weight of 0.5 each; 10 classes are added at 0.5 each.
  - **Class list rule** (train GT, 478 cells, masks_escdd): classes with GT in ≥ 40 train cells, excluding background (0) and padding (7).
  - Train cell counts: 1: 206, 2: 218, 4: 469, 5: 261, 9: 49, 11: 42, 13: 106, 14: 209, 15: 318, 16: 53, 20: 41, 21: 97.
  - Excluded rare classes (≤ 15 cells): 3, 6, 8, 10, 12, 17, 18, 19, 22, 23.
- **Absent-class behaviour** (MC C5): per class, soft Dice is computed over the whole batch, (2Σpy+1)/(Σp+Σy+1). A class absent from the batch therefore contributes 1 − 1/(Σp+1), which pushes its predicted mass down. This is the L3 behaviour for crack and inactive. For splice (in 53 of 478 cells), about 61% of batches of 8 contain it.
  - Shown in `el_m/tests/test_m_dice.py` (commit `34feea9`): the default equals L3; the absent-class term equals 1 − 1/(Σp+1); R2 = L3 + the added classes at 0.5 each; the factory reads the list.
  - Full suite: 225 passed, 11 skipped.
- **No code change.** Both are existing config keys of `ce_dice` (`src/losses/loss_factory.py`).
- **Side effect, disclosed:** the total loss is larger (12 Dice terms instead of 2), and gradient clip 1.0 may bind more often, which lowers CE's effective step. That is part of the change, not a second one.
  - **F2:** every R2 run sets `training.log_grad_norm=true`, a logging-only switch in `el_m` commit `3c1b72b`, default off. With unit tests showing the update is unchanged, it logs the mean pre-clip grad norm and the clip rate per 50 steps.
  - The SUP100 config gets the same logging in one descriptive run, `m_sup_gn_s0` (seed 0, full 20k steps, same switch). It also checks that the new deployment reproduces `p6_L3_100pct_s0` (its final test/val JSON should match P6 s0; reported, not part of any rule).
  - Before launch, the new deployment is identity-checked against `p16_A_100pct_s3` for 1,000 steps with the switch on (losses must match).

## Fixed (identical to SUP100)
- smp U-Net++ with ImageNet ResNet-34, 1-channel input;
- `data.labeled_fraction=1.0` (478 cells), masks_escdd, labelsafe augmentation;
- batch 8, 20,000 steps, Adam 1e-3, wd 1e-4, 200-step warmup then cosine, clip 1.0, bf16, deterministic, split seed 0.
- Final weights at step 20,000.

## Arms
| Arm | Runs | Seeds | Where |
|---|---|---|---|
| SUP100 (comparator) | `p6_L3_100pct_s0..2` (`824fab0`), `p16_A_100pct_s3..4` (`bac5264`) | 0-4 | cv02, existing; the code path is identity-checked at `el_m` `86197f3` over 1,000 steps (`identity_check.txt`) |
| R2 | `m_r2_dice12_s0..4` | 0-4 | cv02 `/tmp/noob_el/el_mt` (REVISION `3c1b72b` = `86197f3` + tests + the logging switch) |

**Opts** (as SUP100 plus the change): `supervised.yaml seed=<s> data.labeled_fraction=1.0 training.total_steps=20000 data.split_seed=0 training.labeled_batch_size=8 data.mask_subdir=labeled/masks_escdd model.name=smp_unetpp data.augmentation=labelsafe loss.supervised=ce_dice loss.dice_classes=[1,2,4,5,9,11,13,14,15,16,20,21] loss.dice_weight=6.0 training.log_grad_norm=true`

## Metrics and decision
- Scored with `trackM/scripts/m0_audit.py` (the M0 scorer) on val, test and ext, plus the P-series `rescore_label_versions.py` JSON per run.
- Primaries: crack IoU, inactive IoU, crack relF1@2, mIoU_rob (test list 0, 1, 2, 4, 5, 7, 11, 13, 14, 15, 16, 20, 21).
- **Rule 1** (P8), 5 v 5, on **all 50** and **without `CSIR_00070_r8_c4`** (design §1, C6):
  - **pass** if rule 1 passes on at least one primary in both sets, or passes in one set and the same primary is n.d. with the same sign in the other;
  - **worse** on any primary in either set fails the rung;
  - otherwise n.d.
- **Stack inclusion (C1), decided on val only:** R2 enters the stack if, on val, it beats SUP100 by rule 1 on val crack IoU, val relF1@2 or val mIoU_rob (val list 0, 1, 2, 4, 5, 7, 9, 11, 13, 14, 15, 16, 21), and is worse on none of the three. Val inactive is reported only. The test verdict is confirmatory and does not decide inclusion; a disagreement goes to team-lead.
- **Width flag:** a crack relP@2 drop > 0.05, or a crack or inactive precision drop > 0.05.
- **Multiplicity:** 4 primaries × 2 cell sets = 8 tests, no correction, disclosed.
- **Robustness** (reported, never decisive):
  - paired image bootstrap (2,000) and leave-top-3-out per primary;
  - cell sets without twins and without both;
  - per source with FP px of subset-absent classes;
  - per-class IoU / P / R for all 13 robust classes, on test and val;
  - crack capture measures (baseline §4);
  - E1 ext 106 (secondary).
- **If R2 is worse on crack** (rule 1, either set): R2b (crack and inactive at 0.5 each, the other 10 classes at a combined 0.5) is the fallback. It needs its own amendment before it runs.

## Smoke (before APPROVED, < 1,000 steps)
- Done 24 Oct: `m_smoke_r2`, 300 steps, finite loss.
- `scripts/m_ce0_check.py`: the resolved config has dice_classes = the 12-class list and dice_weight 6.0. Step-0 CE = 3.66866 in both configs, on the same first batch (checksum equal); the full loss is 4.669 vs 9.599. Output in `log_smoke_checks.txt`.

## Compute
- About 1.1 GPU-h per run at 3 per GPU, so 5 runs ≈ 6 GPU-h.
- Launch on cv02 GPUs 6-7 via fixed lanes popping from a flock-locked queue file (`lanes_m.sh`, one tmux session `=mq`). Training is deterministic per machine, so packing changes speed only.
- Ledger row before launch. Outputs relayed to gaint `cv02_noob_el/el_m` with MD5.

## Not claimed
- Anything about rare classes with < 3 test cells (busbars 9, corrosion 18): reported, but not in mIoU_rob.
- That Dice is the best overlap loss (Lovász etc. untested).
