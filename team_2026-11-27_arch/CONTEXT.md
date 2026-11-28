# Architecture sweep, 27 Nov 2026: context for every agent

Goal of the user: find **every** segmentation model, architecture or method family, in any field and under any supervision regime, that could raise our result, now that the data audit and protocol are settled. The training machine (8x RTX A6000, 48 GB each) is free for the next phase. This sweep only reads and ranks; nobody trains anything.

Full background: `ref/thesis_27nov.txt` (the 179-page thesis; chapters 4, 6, 7, 8, 9 and appendices E, F, H matter most) and `ref/THESIS_TABLES.md`. Facts below are copied from them; check there if in doubt.

## The task
- 24-class pixel segmentation of electroluminescence (EL) images of single solar cells (BenchmarkEL release 20211104). Grey-scale, 512 px crops of cells; five sources (ARTS, CFVS, CSIR, BMRK, SDLE) with very different contrast.
- Headline: **crack relF1@2** (precision/recall of crack pixels within a 2 px tolerance; 2 px is the 95th percentile distance between two annotators of the same crack). Strict crack IoU is printed but decides nothing (it measures the annotators' line-width convention). Also inactive IoU and mIoU over 13 robust classes (mIoU-R13).
- Cracks are 1 to 2 px wide and 0.19% of training pixels; inactive regions are rare (42 of 478 train cells).
- Data: pool P532 (478 train + 54 val of the release), 5 folds grouped by physical module (cv5v3, 285 groups). Labels v1.1. No half-cut cells in the pool.
- Unseen-module set E1: 106 cells, 101 from one source (CSIR), 62 half-cut cells. **E1 has been used as training data since 23 Nov (few-shot track), so it can no longer test zero-shot generalisation.** A new unseen set will be needed for any new zero-shot claim.
- Protocol: a gain counts only if at least M = 0.010 on crack relF1@2 with a seed-aware 95% interval above 0, plus guards (crack width within 0.85 to 1.15 of the baseline, false crack pixels on crack-free cells at most 1.5x, mIoU-R13 not down by more than 0.010). 2 seeds to screen, 5 seeds to confirm.

## Where we are
- Baseline PF: U-Net++ with an ImageNet ResNet-34 encoder and an encoder-preserving fine-tune (encoder frozen for the first 1,000 steps; the plain fine-tune was found to erase the pretrained deep layers).
- Final recipe C2: **HRNet-W18 encoder + U-Net++ decoder + PF schedule + SWAD weight averaging (steps 10k to 20k) + D4 test-time augmentation (8 flips/rotations)**. CV5 crack relF1@2 about 0.868 (selection-biased). On E1, zero-shot: crack relF1@2 0.490 (relP 0.600, relR 0.416), +0.043 over PF, confirmed; gain carried by full cells, half-cut cells n.d. Few-shot inside E1 (pool + labelled E1 cells of other folds): 0.709.
- Reading so far: resolution matters (stride-8 DeepLabV3 is 0.077 below PF; HRNet-W18, which keeps a high-resolution stream, is the only encoder above it); no decoder effect was detected (U-Net vs U-Net++). Recall on unseen modules is the weak point (0.42), and half-cut layouts are not in the training pool.

## Already tested (do not re-propose unless you have a clearly different variant; say why)
Architectures: U-Net R34, U-Net++ R34 (PF), U-Net VGG-16 (Hanifi), DeepLabV3+ R34 (stride 4), DeepLabV3 R50 (stride 8, UCF-EL), SegFormer MiT-B2, HRNet-W18 + U-Net++ (winner), ResNet-50 encoder, SA-UNet++ (old era), DINOv3 ConvNeXt-T encoder (A8 screen: KILL), 2x input resolution (Track M).
Losses / heads: weighted CE (Pratt), Dice-12, Skeleton Recall (helped on E1 opening #5 single, failed as ensembles), soft clDice, JML hard / soft band, train-time logit offsets (LA-CE), inactive auxiliary head with layered decision, scuff class (B3).
Training / data: semi-supervised Mean Teacher and pseudo-labels (5 to 100% labels; helped only at 5% and 10%), external unlabelled pool (11,938 cells), UCF-EL encoder pretraining, MIM (SparK) and decoder-denoising pretraining, crack copy-paste, synthetic half-cuts (HC, HC2), rare-class sampling, encoder SPD, +107 E-SCDD cells, ensembles (PF2E, SKR2E), post-hoc EMA, SWAD, D4 TTA.
Inference: per-class logit bias (OP-C), per-source calibration, DTI hysteresis thresholds, cross-fitted F1 bias.

## The previous sweep (12 Nov) and its ledger
`ref/MASTER.tsv`: 645 papers from 44 search directions (`ref/directions_1112/`), each with a status: RUN_NOW 44, RUN_AFTER_GATE 61, BENCH_ONLY 79, PROTOCOL 62, PARKED 396, VOID 2. Columns: pid, rank, score, bench, paper_id, title, directions, team, status, arm, note. Many RUN_NOW items were never run (the benchmark build took the time). **Every new paper you report must be checked against MASTER.tsv by DOI / arXiv id and title; mark it NEW or say which pid it already is.**
