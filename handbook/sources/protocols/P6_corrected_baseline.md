# P6 protocol (Experiment 1 for the mid-term): corrected supervised baseline, a one-change-per-step ladder

Locked 10 Oct 2026, before any run. Code: gaint repo `el-fault-detection`, commit recorded in each run dir (`REVISION`). The same commit is deployed to cv02.

## Question
How much of the low crack/inactive score comes from the recipe and the labels? How much room is left for SSL at 10% labels under a corrected recipe?

## Fixed for all arms
- BenchmarkEL `20211104` images, our official split, seed-0 labelled subsets.
- **Labels:** `data/labeled/masks_escdd`, i.e. E-SCDD revised masks for 577/582 stems, with the old mask for 5 train stems absent from E-SCDD (none in the 10% subset).
  - E-SCDD classes 24–29 are mapped back to the old label at those pixels.
  - The same mask set is used for train, val, test and the class weights.
- **Training:** 20,000 steps; batch 8 labelled; Adam 1e-3 with weight decay 1e-4; 200-step warm-up then cosine to 0; grad clip 1; bf16 autocast; `deterministic: true`.
- Training seeds 0, 1, 2. Checkpoint: final step (primary rule, as in all our work).
- **Hardware:** all arms on cv02 (RTX A6000), at most 3 runs per GPU. Co-location changes speed, not results.

## Arms (each step changes one thing)

| Arm | Model | Augmentation | Loss | Labels |
|---|---|---|---|---|
| L0 | `unetpp` (5M, from scratch) | `strong` (flips/rot90 + ±5° rotation + blur + noise + brightness/contrast) | weighted CE (√inv-freq, cap 10) | 10%, 100% |
| L1 | `unetpp` | `labelsafe` (flips/rot90 + brightness/contrast only) | weighted CE | 10% |
| L2 | `smp_unetpp` (resnet34 ImageNet, 26M) | `labelsafe` | weighted CE | 10% |
| L3 | `smp_unetpp` | `labelsafe` | CE + soft Dice (crack, inactive) | 10%, 20%, 100% |

21 runs in total.

## Evaluation
`scripts/rescore_label_versions.py` (read-only) on final weights, for test (50) and val (54), against revised labels (**primary**) and old labels (secondary).
- **Primary metrics:** crack AP and inactive AP (dataset-level, binned).
- **Secondary:** crack IoU, relaxed F1@1/2 with relaxed precision@2, inactive IoU. Plus the trainer's own test summary (defect mIoU).

## Decision rules
1. **A ladder step helps** if the mean change (3 seeds, test, revised) in crack AP or inactive AP exceeds 0.01 **and** exceeds 2 × √((sd_a² + sd_b²)/3). Otherwise it is "no detectable effect".
2. **Base for Experiment 2:** the 10% arm with the highest **val** mean of (crack AP + inactive AP)/2 (revised). Selected on val, reported on test.
3. **SSL headroom:** base@100% − base@10% on pooled val+test, mean of (crack AP + inactive AP)/2.
   - If < 0.02, Experiment 2 is underpowered on BenchmarkEL and is reported as a pilot.
   - If ≥ 0.02, that difference is the gap Experiment 2 tries to close.

## Not claimed
- Within-step attribution (e.g. blur vs ±5° rotation inside L1).
- Generalisation beyond this split and dataset.
