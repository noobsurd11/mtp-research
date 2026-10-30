# Track M design: the ladder to the best-scoring model (v2)

MD, 24 Oct 2026. Status: **draft for MC**. It builds on `baseline.md` (M0), which is not yet verified. The numbers below are M0's, on val unless stated.

## 0. v2 changes (MC review_design.md, C1 to C7; these override anything below that conflicts)
- **C1 (inclusion on val).** A rung enters the stack only if, **on val**, it beats its comparator by rule 1 on at least one of: val crack IoU, val relF1@2, or val mIoU_rob (val list). It must be worse on none. Val inactive is reported but decides nothing.
  - Test is still scored once per rung as the confirmatory verdict. It never decides inclusion.
  - A val/test disagreement is reported to team-lead, and the val decision stands.
  - The final protocol scores the stack + R1 layer once, against SUP100 and against the best single rung, and states how many test openings preceded it.
- **C2 (ensemble verdict).** The R1b verdict is the paired image bootstrap (2,000 resamples) of ensemble minus the mean single seed, on both cell sets. It is read on the without-noisy set; the 5 leave-one-out 4-member ensembles give the spread. R1a (TTA) uses rule 1 plus paired per-seed differences.
- **C3 (R1c grid).** Crack bias 0 to +3 in steps of 0.25, on the crack logit only, chosen on val for the model it is applied to.
  - Descriptive only, never a rule-1 "better".
  - Test reports its cost in crack precision, crack IoU and mIoU_rob.
- **C4 (R3 pilots).**
  - Score = mean of val crack IoU, val relF1@2 and val mIoU_rob (val list), no inactive.
  - Threshold = SUP100 val sd of that score: 0.0016 (mean 0.6398, 5 seeds), so a pilot must score > 0.6414.
  - L3 recipe for all encoders, no LR tuning. Params, FLOPs/step, GPU-h and memory reported. Separate `protocol_r3.md`.
  - **Candidates, updated with Track D's verified probe** (trackD/probe_results.md: frozen ImageNet ResNet-50 and ConvNeXt-T rank BMRK crack better than ResNet-34, AP 0.27 vs 0.19, but CSIR/ARTS worse):
    1. U-Net++ + ResNet-50 (one change);
    2. U-Net + ConvNeXt-T (two changes, labelled);
    3. U-Net++ + EfficientNet-B4 (one change).
- **C5 (R2 Dice).**
  - The batch soft Dice of class c is (2Σpy+1)/(Σp+Σy+1). A class absent from the batch therefore contributes 1 − 1/(Σp+1), which pushes its predicted mass down. This is the same treatment crack and inactive have had since L3.
  - The class list is fixed from train GT: classes with GT in ≥ 40 of 478 train cells, excluding 0 and 7. That gives 1, 2, 4, 5, 9, 11, 13, 14, 15, 16, 20, 21 (12 classes; splice is in 53 train cells, edge_dark in 41).
  - The per-class Dice weight is kept at L3's 0.5 (dice_weight = 12/2 = 6), so crack and inactive keep their L3 gradient.
  - A unit test documents the absent-class behaviour.
- **C6.** "Worse" on either cell set fails a rung. Contrast count disclosed per protocol (4 primaries × 2 cell sets).
- **C7.** Identity check passed at 1,000 steps (`identity_check.txt`): `el_m` @ `86197f3` reproduces `p16_A_100pct_s3` exactly. The losses, lr, the val lines at 500 and 1,000, and the "Labelled: 478 (data/splits/train.txt)" line all match, so `data.labeled_list` is off by default. New switches default bit-identical, with tests.

## 1. Goal and how it is measured
**User:** "highest scores, a model which captures almost all of the cracks, inactive and other important defects balancing the miou for other classes as well."

**Primary metrics** (test, 50 cells, masks_escdd, final weights):
- crack IoU, inactive IoU and crack relF1@2 (the P-series three);
- **mIoU_rob**, added as a fourth primary: mean IoU over the 13 classes with GT in at least 3 test cells (0, 1, 2, 4, 5, 7, 11, 13, 14, 15, 16, 20, 21), list fixed (baseline §1).

**Rule.** Rule 1 (P8), 5 v 5 seeds: "better" on at least one primary and "worse" on none.
- It is applied on all 50 cells **and** without `CSIR_00070_r8_c4`, because that cell moves mIoU_rob by 0.033 and crack IoU by up to 0.18.
- A rung passes only if it passes on both cell sets, or passes on one and is n.d. on the other with the same sign. The second case is reported as such.
- Also reported, never part of the verdict:
  - without the 7 twins, and without twins + noisy cell;
  - per source (CFVS, BMRK, ARTS, CSIR; SDLE has 1 cell);
  - paired image bootstrap (2,000 resamples) and leave-top-3-out per primary;
  - E1 ext 106 as a secondary.

**"Captures almost all cracks"** (a descriptive target, per MC: rungs are decided by rule 1 only; reported on all 50 and without the noisy cell, always with precision):
- relR@2 ≥ 0.90 at relP@2 ≥ 0.90;
- crack component recall ≥ 0.90 (GT components ≥ 20 px, ≥ 50% of px within 2 px of a prediction), with component precision reported beside it;
- crack IoU not worse by rule 1.

Baseline: relR@2 0.830 at relP@2 0.938, component recall 0.798. On val, the 5-seed ensemble at crack bias +1 already reaches relR@2 0.895 at relP@2 0.898. So the target is met by **a better model plus an operating point chosen on val**, never on test.

**Val class list for any val-based mIoU choice** (pilot selection, bias fitting): classes with GT in at least 3 of the 54 val cells, **0, 1, 2, 4, 5, 7, 9, 11, 13, 14, 15, 16, 21**, fixed now. "val mIoU_rob" below means this list.

**Inactive and other defects.** Inactive component recall (≥ 100 px, ≥ 50% predicted) is reported with precision.
- Baseline: 0.773 without the noisy cell.
- No numeric target: test has 16 inactive cells, and val has 6, so val cannot set one.

**Width check (R4).** A crack relP@2 drop > 0.05, or a crack or inactive precision drop > 0.05, is flagged for every rung.

## 2. Standing discipline (from MC's checklist; applies to every rung)
1. Selection on val only. Thresholds, TTA, ensemble members, and the choice among pilot variants are made on val and frozen in the protocol before test is scored. Test is opened once per locked protocol.
2. Final-step weights (20,000 unless the rung is the schedule).
3. Same optimizer steps and batch across arms. Schedule length is its own rung. Backbone and resolution rungs state GPU-h and FLOPs per step.
4. 5 seeds per arm (0-4).
5. **Comparator:** SUP100 = P6 L3 100% s0-2 + P16 A100 s3-4, scored in M0. These sit on older commits (`824fab0`, `bac5264`). Before the first rung, a log-identity check is required: re-run `p16_A_100pct_s3`'s exact config from the Track M deployment for 1,000 steps on cv02 and match its stdout losses (D3 rule). If that fails, the comparator is re-run on the new deployment (5 runs, ~6 GPU-h).
6. One change per rung. cv02 only. Worktree `el_m` on gaint (branch `m`, from Track D's `86197f3`, which adds only `data.labeled_list` on top of the SK1 line), deployed with `git archive` and `REVISION`. Ledger booking.
7. **Rungs in the same wave** are each tested against the same current best. Winners are then stacked into one combined arm, tested 5 v 5 against the best single rung. A stack is never assumed additive.
8. **Ensembles and TTA** carry their compute in every claim. The ensemble's comparator is the mean single seed of the same recipe, never the best seed.

## 3. Compute
- Track M lanes: cv02 GPUs 6 and 7, plus 4-5 when the other user frees them. Track D holds 0-3 until about 21:00 IST (DX's plan).
- At 3 runs per GPU: 6 concurrent runs on 2 GPUs.
- A U-Net++/R34 supervised run at 20k steps takes about 3-3.5 h at 3 per GPU (P14), about 1.1 GPU-h. A 5-seed arm at 512 px costs about 6 GPU-h, about 3.5 h wall in one wave.

## 4. The ladder (ranked by expected gain per GPU-h)
Expected effects are **S** (speculation) unless marked **E** (our evidence).

| # | Rung (one change) | Why (evidence) | Cost | Expected | Kill / caution |
|---|---|---|---|---|---|
| **R1** | **Post hoc layer on the existing SUP100 checkpoints:** (a) dihedral-8 TTA, (b) 5-seed mean-softmax ensemble, (c) a crack operating point chosen on val to hit relR@2 ≥ 0.90 at the highest relP@2 | **E (val):** TTA +0.010 crack IoU (seed sd 0.002); ensemble +0.012 crack IoU, +0.012 relF1; ensemble + crack bias +1 gives relR@2 0.895 / relP@2 0.898. 28% of GT crack sits in the middle probability band (baseline §4). Deep ensembles: Lakshminarayanan et al. (`scopus:2-s2.0-85046740096`) | inference only, ~1 GPU-h (8× and 5× inference) | crack IoU +0.01, relF1 +0.01, recall target met on test (S) | (a) and (b) are paired contrasts: same checkpoints, TTA on vs off. (c) needs MC's rule on the operating point. Noisy-cell FP checked with and without TTA |
| **R2** | **Soft Dice on all foreground classes** (`loss.dice_classes` = every train-present class except 0 and 7; config only) | **E:** gridline R 0.326 / IoU 0.278 (45 cells), splice never predicted, edge_dark R 0.394: CE alone under-calls thin and rare classes. L2 → L3 (adding Dice on crack and inactive) was the P6 step that turned labels into gains (handbook 11 row 13). Lovász-style region losses target IoU directly (Berman et al., `doi:10.1109/cvpr.2018.00464`) | 5 × 1.1 ≈ 6 GPU-h | mIoU_rob +0.02 to +0.04 via gridline, splice, edge_dark (S) | Crack's Dice share falls from 1/2 to about 1/18, so crack IoU and recall may drop. Guarded by "none worse"; if crack drops, R2b keeps crack + inactive at weight 0.5 each and the rest at 0.5 / k |
| **R3** | **Encoder:** ResNet34 → stronger, decoder kept where smp allows. Pilot 1 seed × 3 candidates (U-Net++ + EfficientNet-B4; U-Net++ + RegNetY-040; U-Net + ConvNeXt-T), **chosen on val** (mean of the val primaries), then the winner 5 seeds | **E:** P4 frozen probe, ConvNeXt-T best on crack AP (0.331). nnU-Net Revisited (`doi:10.1007/978-3-031-72114-4_47`): ResNet/ConvNeXt U-Nets plus scaling beat newer architectures under rigorous validation. Torpey et al. (`arxiv:2402.17611`): on EL, pretraining sources tie on mIoU, so gains here come from capacity, not pretraining choice. U-Net++ does not take ConvNeXt in smp 0.5 (tested: stride-4 stem), so ConvNeXt means a U-Net decoder (two changes; labelled) | pilots 3 × ~1.5 GPU-h; arm 5 × ~1.5-2.5 GPU-h ≈ 15 GPU-h | crack +0.01 to +0.03, BMRK recall the informative part (S) | Pilot choice on val only; FLOPs and GPU-h per step reported. If no candidate beats R34 on val by > 1 seed sd, the rung is dropped without opening test |
| **R4** | **Extra labelled data:** + 107 leakage-free E-SCDD cells (MC's `data_addendum.md`) | **E:** labels are the largest lever we measured (5 → 100% +0.17 crack IoU). But the 107 are 104 CSIR + 3 ARTS, +12% crack px, in the source we already score best on | data prep + 6 GPU-h | crack +0.00 to +0.01, CSIR only (S) | Needs a code switch (labelled list at fraction 1.0) and the P6 class mapping with histograms (MC §5). Steps matched, so each cell is seen ~18% less often |
| **R5** | **Input upsampling ×2** (1024 px in, logits pooled back to 512 for scoring) | **R:** cracks are 1-2 px; the R34 stem halves the resolution before the first skip, so a 1-px line lives in the stride-2 features. HRNet-type designs keep high-resolution features for position-sensitive tasks (Wang et al., `doi:10.1109/tpami.2020.2983686`). No EL evidence | code switch; ~4× FLOPs ≈ 20-25 GPU-h for 5 seeds | crack recall on faint/thin cracks (S), unknown | Expensive; only after R2/R3. Labels stay at 512 (nearest-upsampled for training), so it is not "native resolution". Our cells are 512 natively; there is no higher-resolution source |
| **R6** | **Longer schedule** 20k → 40k steps (cosine stretched) | **R:** at 100% labels 20k × 8 ≈ 335 epochs; P16 A100 shows no sign of under-training (val and test agree). Low expected value | 2× ≈ 12 GPU-h | ≤ +0.01 (S) | Its own rung. Run only if R2/R3 show the new loss or model is still improving at 20k (val curve) |
| **R7** | **Thin-structure loss on crack:** skeleton recall (Kirchhoff et al., `doi:10.1007/978-3-031-72980-5_13`) added to CE+Dice | Mixed: Arora et al. (`arxiv:2508.11374`) find SRL does not beat baselines and raises false positives; P14's tolerance loss was null. clDice (`doi:10.1109/cvpr46437.2021.01629`) targets connectivity, not our error. Our crack recall is reachable by operating point at flat IoU (val) | 6 GPU-h + code | small; recall up, precision down (S) | Run only if R1(c) cannot meet the recall target at relP@2 ≥ 0.90 on val |
| **R8** | **SSL on top** (BsM-style hard PL, separate BN, CutMix; external pool) | **E against:** P16 Sx100 − A100 n.d. on all three at 100%. Context: on val the Sx100 ensemble scores inactive 0.478 vs 0.424, crack equal (6 val cells; noise) | 5 × ~2.8 GPU-h ≈ 14 GPU-h | ≈ 0 (E, P16) | Not proposed unless the user wants an SSL line in the final model |
| **R9** | **Pretraining on the unlabelled pool** (MIM, e.g. ConvNeXt V2 FCMAE, `doi:10.1109/cvpr52729.2023.01548`) | Track D's frozen-encoder probe gates it (SYNTHESIS direction 7). Torpey: in-domain SimCLR lost to ImageNet on EL | 1-2 GPU-days + 6 GPU-h | small (S) | Not before Track D's probe result |
| – | Not proposed: LA / class-prior weighting | **E:** val LA τ ≥ 0.5 leaves crack IoU flat and lowers mIoU (0.511 → 0.434 at τ 1); S-a: A100 + LA crack −0.002. Menon et al. (`arxiv:2007.07314`) is for balanced error, not IoU | – | – | – |
| – | Not proposed now: Focal Tversky (`doi:10.1109/isbi.2019.8759329`), SegFormer (`arxiv:2105.15203`), UPerNet (`doi:10.1007/978-3-030-01228-1_26`), Mask2Former (`doi:10.1109/cvpr52688.2022.00135`) | Tversky: the same P/R trade the val bias already gives at no cost. SegFormer/Mask2Former: 4-px patch or query decoders at 1/4 resolution, against 1-2 px cracks; P4 measured ViT-patch features weak on crack (DINOv2 AP 0.18) | – | – | Revisit only if R3's CNNs fail on val |

## 5. Order of work
- **Wave 0 (now, about 1 h): identity check** on cv02 GPU 7 (1,000 steps), plus a smoke of the new switches.
- **Wave 1 (GPUs 6-7, 6 slots, about 4-6 h):**
  - R2, 5 seeds;
  - R3 pilots, 3 × 1 seed;
  - in parallel, R1 (inference only, needs MC's operating-point rule).
- **Wave 2:**
  - the R3 winner, 5 seeds;
  - R2b if R2 hurts crack;
  - R4 data prep.
- **Wave 3:** the stack (best of R2/R3/R4 together) vs the best single rung, 5 v 5.
- Then R5/R6 if compute and val curves justify them.
- **Final:** the best stacked recipe with:
  - the 5 seeds as an ensemble (R1b);
  - TTA (R1a), if R1 passes;
  - the crack operating point and any class bias fixed on val (R1c, plus MC rule (b) for inactive).

  It is scored once on test in a locked final protocol, with the full reporting set, and MC recomputes it.

## 6. What the user can expect (reading, not a promise)
- crack IoU ≈ 0.48-0.50 without the noisy cell (baseline 0.474);
- relR@2 ≈ 0.90 at relP@2 ≈ 0.90;
- mIoU_rob ≈ 0.60-0.62 without the noisy cell (baseline 0.580);
- inactive roughly unchanged within its 16-cell noise.

Unseen modules will stay far lower (crack recall 0.18 today): that needs data, not tuning.

## 7. Decisions for MC now
Already settled (MC, review_baseline.md): baseline = SUP100 judged on both cell sets; the crack target is descriptive; no inactive bias without positive gains in both folds; per-source tables print FP px of subset-absent classes.
1. Accept mIoU_rob as a fourth primary, and the two-cell-set pass rule in §1.
2. R1c: the operating point is the smallest crack bias whose val relR@2 is at least 0.90. If that costs relP@2 below 0.90 on val, the bias with the highest val relF1@2 is used instead. Accept?
3. R1 now, on the baseline checkpoints, as its own locked protocol (gives the user an early verified number), or only at the final? I prefer now: it costs about 1 GPU-h, and the final re-applies the same frozen rules.
4. R3 pilot design: 1 seed per candidate, chosen on val. Is that acceptable as "selection on val"?
