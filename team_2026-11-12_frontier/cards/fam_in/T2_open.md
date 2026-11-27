# T2 open papers: 19 scout records the first T2 team did not take (best first)

## P031 | Image-Level Regression for Uncertainty-Aware Retinal Image Segmentation (SAUNA)
- id doi:10.1109/wacv61041.2025.00412 | 2025 | WACV | score 68 | bench 55 | dirs D18 | code https://github.com/Oulu-IMEDS/SAUNA
- mechanism: Convert hard thin-structure masks to soft targets from distance to the annotation boundary and local thickness, then train as regression with a generalised JML plus a stable Focal-L1 loss.
- scout's adaptation: Crack only: SAUNA transform of the 1-2 px crack labels, thickness term normalises source width (ARTS 1.5 px to SDLE 3.25 px); separate sigmoid crack head with GJML + SF-L1 next to the 24-class softmax trained with house CE; crack threshold re-picked on val. BMRK (downscaled ELPV) is the aliasing ...
- evidence: R: FIVES, low-res input, UNet++ BCE+Dice hard 74.05 IoU; JML+BLS 81.77; SAUNA+GJML+SF-L1 84.75; UNet++ high-res hard 81.70. +0.4 to +2.3 IoU over BLS on STARE, DRIVE, CHASEDB1, HRF. | prior overlap: none: soft-label regression targets never run; offset-tolerant CE and Skeleton Recall are different mechanisms.

## P117 | TRACE: Topology-Aware Reconnection via Prediction-Adaptive Connectivity Enforcement for Thin-Structure Segmentation
- id arxiv:2610.22210 | 2026 | arXiv | score 58 | bench 50 | dirs D10,D11 | code none found
- mechanism: For each skeleton point whose removal splits the local target skeleton, find the easiest valid reconnection under the current prediction among nearby target pixels and supervise its bottleneck pixel with a centred logit margin, so supervision follows the pr...
- scout's adaptation: Implement in-house (3x3 local search, about 150 lines). As published the candidates are only label pixels, so on 1 to 2 px labels it stays on the drawn line; widen the candidate support to the crack label dilated by 1 px for this term only so the reconnection can follow the true dark ridge. Crack...
- evidence: R: nnU-Net style training, 6 benchmarks. DeepCrack (270 train, CS2-Net backbone): Dice 82.78 to 85.20, beta error 6.16 to 3.69, clDice 89.03 to 91.10; SkelRecall 84.26 / 4.74; clDice 84.58 / 5.06. Stacks with SCNP on ... | prior overlap: Partial: Skeleton Recall (fixed skeleton recall) and offset-tolerant CE were run; prediction-adaptive bottleneck supe...

## P206 | Dice Semimetric Losses: Optimizing the Dice Score with Soft Labels
- id doi:10.1007/978-3-031-43898-1_46 | 2023 | MICCAI | score 50 | bench 40 | dirs D18 | code https://github.com/zifuwanggg/JDTLosses
- mechanism: Dice loss that equals soft Dice on hard labels but is minimised at prediction = target for soft labels.
- scout's adaptation: Drop-in replacement for the house soft Dice in every soft-target arm (KD, SVLS, GeoLS, SoftSeg, dilated labels); run DML vs house soft Dice on the same soft targets to show whether the house loss breaks.
- evidence: R (web summary): better Dice and calibration than soft Dice with soft labels on QUBIQ, LiTS, KiTS; numbers not read. | prior overlap: Dice on 3 classes (hard labels) n.d.; DML is identical there, so only the soft-label use is open.

## P243 | Widest-Path Reachability Fields for Connectivity-Preserving Slender Structure Segmentation
- id arxiv:2607.07123 | 2026 | arXiv | score 48 | bench 40 | dirs D10 | code none found
- mechanism: A differentiable max-min (widest path) reachability objective on a domain-restricted graph sends gradient to the sparse bottleneck pixels that break connectivity. No inference overhead.
- scout's adaptation: Domain = crack label dilated by 2 px to absorb jitter, endpoints from the label skeleton, DP on GPU. An alternative solver to TRACE for the same goal, so pick one.
- evidence: R (abstract): 9 architectures, 6 datasets including cracks. Improved 87% of experiments with fixed hyperparameters, clDice +7.2 points on fragile datasets. | prior overlap: none

## P268 | The Lovasz-Softmax Loss: A Tractable Surrogate for the Optimization of the Intersection-Over-Union Measure in Neural Networks
- id doi:10.1109/cvpr.2018.00464 | 2018 | CVPR | score 45 | bench 65 | dirs D18 | code none found
- mechanism: Convex surrogate of the Jaccard loss via the Lovasz extension of sorted errors.
- scout's adaptation: Lovasz hinge on crack and Lovasz-softmax over present classes, computed over the whole batch (not per image) to match pooled IoU; hard labels only (cannot take soft targets). smp, the house library, ships an implementation.
- evidence: R: widely used IoU surrogate (1239 cites); JML paper App. E finds it equal to JML with hard labels (Cityscapes 75.53 vs 75.55). | prior overlap: none

## P305 | Improving Semantic Segmentation via Video Propagation and Label Relaxation
- id doi:10.1109/cvpr.2019.00906 | 2019 | CVPR | score 45 | bench 30 | dirs D18 | code none found
- mechanism: Boundary label relaxation: at boundary pixels maximise the summed probability of all classes in a small window, so small misplacements are not punished.
- scout's adaptation: Within a 3x3 window of crack label pixels the target is crack OR neighbour class (log of summed probabilities); elsewhere standard CE; tolerates 1 px jitter without widening the target.
- evidence: R: Cityscapes 83.5 mIoU, robustness to boundary annotation noise and propagation artefacts. | prior overlap: Partial: offset-tolerant CE (P14) at 10% labels used a min over shifts and was n.d.; summed-probability relaxation at...

## P324 | Unified Focal loss: Generalising Dice and cross entropy-based losses to handle class imbalanced medical image segmentation
- id doi:10.1016/j.compmedimag.2021.102026 | 2022 | Computerized Medical Imaging and Grap... | score 44 | bench 65 | dirs D18 | code https://github.com/mlyg/unified-focal-loss
- mechanism: Compound of asymmetric focal CE and asymmetric focal Tversky with three hyperparameters, generalising Dice, CE, focal and Tversky losses.
- scout's adaptation: Replace CE + Dice; asymmetry set to favour crack and inactive recall toward the relR@2 >= 0.90 target, with relP@2 watched as the width check.
- evidence: R: imbalanced medical segmentation tasks (884 cites); numbers not read. | prior overlap: none (focal / Tversky family untested)

## P332 | Boundary-Local Soft Supervision for Reliable Calibration in Defect Segmentation
- id doi:10.1109/lsp.2026.3731530 | 2026 | IEEE Signal Processing Letters | score 42 | bench 45 | dirs D18 | code none found
- mechanism: Boundary-gated label smoothing: local-mean soft targets only inside a morphological boundary band, hard BCE + Dice elsewhere.
- scout's adaptation: 2 px band around crack and inactive labels gets local-mean soft targets; main use is calibrated crack probabilities for decoding, ensembling and severity, not raw IoU.
- evidence: R: 4 defect datasets incl. DeepCrack, 20 seeds: boundary-band ECE down 28-49%, no Dice or Boundary-Dice degradation; weaker on Magnetic Tile. | prior overlap: none

## P356 | Skeleton Recall Loss for Connectivity Conserving and Resource Efficient Segmentation of Thin Tubular Structures
- id doi:10.1007/978-3-031-72980-5_13 | 2024 | ECCV 2024 | score 40 | bench 85 | dirs D10 | code none found
- mechanism: Soft recall loss on a tubed label skeleton. Cheap and GPU-friendly.
- scout's adaptation: Already run here. Open item: score the trained w 0.1 fresh-seed replication and add the width diagnostic. Keep it as a benchmark baseline loss.
- evidence: R (TopoMortar): best topology under noisy labels, but CrackTree Dice 0.32 vs 0.78 for CEDice. E: w 1.0 widened predictions and lowered test IoU while raising E1 detection. w 0.1 narrow E1 pass. | prior overlap: Same mechanism and conditions run (Loss row). Only the replication scoring is open.

## P359 | How Do Label Errors Affect Thin Crack Detection by DNNs
- id doi:10.1109/cvprw59228.2023.00464 | 2023 | CVPRW | score 40 | bench 75 | dirs D11,D16,D18 | code none found
- mechanism: Label cracks as 1 px curves with matching training and evaluation, then synthesise annotation errors: under-annotation hurts more than over-annotation; polyline approximation has modest impact.
- scout's adaptation: Benchmark: score crack as curves (relF1 on skeletons) and add a label-error robustness column (train on CV labels with synthetic 1 px jitter and 20% dropped segments). Model side: favour recall when refining labels; polyline-simplified labels are acceptable targets.
- evidence: Synthetic error study on 1 px curve labels; qualitative findings in abstract; numbers not read. | prior overlap: none

## P385 | SoftSeg: Advantages of soft versus binary training for image segmentation
- id doi:10.1016/j.media.2021.102038 | 2021 | Medical Image Analysis | score 40 | bench 35 | dirs D18 | code none found
- mechanism: Train on non-binarised soft labels as regression (normalised ReLU output, regression loss) instead of classification.
- scout's adaptation: Crack channel regresses a blurred crack map (soft band) while other classes stay softmax; threshold chosen on val.
- evidence: R: Dice +2.0% (gray matter), +3.3% (MS lesions), +6.5% (brain tumour) across random splits; higher sensitivity for small objects. | prior overlap: none

## P413 | Topologically faithful image segmentation via induced matching of persistence barcodes (Betti matching)
- id arxiv:2211.15272 | 2022 | arXiv (ICML 2023) | score 38 | bench 60 | dirs D10 | code https://github.com/nstucki/Betti-matching
- mechanism: Persistent-homology loss that matches predicted and label barcode features by their induced spatial correspondence, then penalises unmatched or shifted features. The efficient C++ version is arxiv:2407.04683.
- scout's adaptation: Crack class, 0-dimensional features. Compute it only on label components >= 20 px so that tiny label fragments (76 to 88% of components) are not enforced. Could raise the share of components found (0.798).
- evidence: R (web summary of abstract): better topology on six datasets with volumetric performance kept. TopoMortar shows a different PH loss (TopoLoss) dropping CrackTree Dice to 0.52. | prior overlap: none. No PH loss was run here.

## P434 | Topograph: An efficient Graph-Based Framework for Strictly Topology Preserving Image Segmentation
- id arxiv:2411.03228 | 2025 | ICLR 2025 | score 36 | bench 60 | dirs D10 | code https://github.com/AlexanderHBerger/Topograph
- mechanism: A component graph of prediction and label finds topologically critical regions, and the loss aggregates over them. It also defines a strict homotopy metric. About 5x faster than PH losses.
- scout's adaptation: Same use as Betti matching on crack (8-connectivity, components >= 20 px). Its homotopy metric is a candidate topology score for the benchmark.
- evidence: R (abstract): state-of-the-art topology on binary and multi-class datasets, up to 5x faster loss than PH methods. | prior overlap: none

## P435 | RankSEG-RMA: An Efficient Segmentation Algorithm via Reciprocal Moment Approximation
- id doi:10.52202/085713-5452 | 2025 | NeurIPS | score 36 | bench 50 | dirs D18 | code https://github.com/ZixunWang/RankSEG-RMA
- mechanism: Replace argmax with the decision rule that maximises expected Dice / IoU per image, now O(d) and for non-overlapping classes; the 2026 follow-up (arxiv:2609.38930, RankSEG-DEP) adds local label dependence for small low-contrast objects.
- scout's adaptation: Post-process FINAL crack probabilities per cell. It maximises per-image IoU, while our decision metric is pooled IoU, and at 100% labels a val bias adds only about +0.004, so expected gain on test is small; more useful for per-cell benchmark metrics.
- evidence: R: RankSEG almost guarantees improved Dice/IoU over argmax; RMA keeps comparable performance at O(d) (LiTS RankSEG took 16.33 s vs 0.01 s argmax). | prior overlap: Partial: logit bias tuning was run (+0.014 to +0.023 at 5%, about 0 at 100%); per-image metric-optimal decoding not run.

## P477 | Structure-Aware Image Segmentation with Homotopy Warping
- id doi:10.52202/068431-1746 | 2022 | NeurIPS 2022 | score 34 | bench 45 | dirs D10 | code none found
- mechanism: Warp the prediction homotopically toward the label and penalise only the critical pixels whose flip changes topology.
- scout's adaptation: A jittered but topologically equal prediction adds no extra loss, which fits our labels. Crack class only. CPU warping cost over 20k steps needs a profile first.
- evidence: R (TopoMortar): CrackTree Dice 0.77 vs 0.78 CEDice. beta0 46 vs 52 under Adele, no gain in supervised training. | prior overlap: none

## P481 | Efficient Betti Matching Enables Topology-Aware 3D Segmentation via Persistent Homology
- id arxiv:2407.04683 | 2024 | arXiv | score 33 | bench 60 | dirs D10 | code https://github.com/nstucki/Betti-Matching-3D
- mechanism: Persistent-homology loss with spatially induced matching between predicted and label barcodes (Betti matching, arxiv:2211.15272), in a fast C++ implementation.
- scout's adaptation: Crack class, components only, on label components >= 20 px. Weight 1e-5 to 1e-2 chosen on val (TRACE paper notes larger weights drop Dice).
- evidence: R (abstract): large speed-up over Cubical Ripser; improved topological correctness on several datasets. R (TRACE tables): Betti matching weaker than TRACE on DeepCrack. | prior overlap: none.

## P486 | Centerline Boundary Dice Loss for Vascular Segmentation (cbDice)
- id doi:10.1007/978-3-031-72111-3_5 | 2024 | MICCAI 2024 | score 32 | bench 65 | dirs D10 | code https://github.com/PengchengShi1220/cbDice
- mechanism: clDice extended with boundary and radius-normalised skeleton terms to balance thin and thick branches.
- scout's adaptation: Crack radius is about 1 px, so on crack cbDice is close to clDice (which failed here). The only distinct use is multi-class balancing of thick inactive / ribbons against thin crack / gridline (beta 0.5 to 1 for 2D).
- evidence: R (full text): DRIVE 2D Dice 82.5 (best), gains under 1 point over clDice. TopCoW small-artery Dice 43.4 vs 38.5 for clDice. R (TopoMortar): CrackTree Dice 0.76, no topology gain over CEDice. | prior overlap: Close to soft clDice (failed, same conditions) on the crack class. Untested for multi-class width balance.

## P534 | Optimization for Medical Image Segmentation: Theory and Practice When Evaluating With Dice Score or Jaccard Index
- id doi:10.1109/tmi.2020.3002417 | 2020 | IEEE TMI | score 28 | bench 55 | dirs D18 | code none found
- mechanism: Theory and six tasks: Dice and Jaccard losses approximate each other, weighted CE has no weighting that optimises them, Tversky drifts from the optimum as weights move.
- scout's adaptation: Guides the benchmark loss axis (CE vs CE+Dice vs CE+JML vs Lovasz under one protocol) and warns that Tversky trades IoU for recall.
- evidence: R: metric-sensitive losses beat CE-based losses on six medical tasks, across object sizes and class ratios. | prior overlap: none

## P563 | TOPO-Loss for continuity-preserving crack detection using deep learning
- id doi:10.1016/j.conbuildmat.2022.128264 | 2022 | Construction and Building Materials | score 25 | bench 40 | dirs D10 | code https://github.com/eesd-epfl/topo_crack_detection
- mechanism: Connectivity-oriented loss (adapted from road delineation) designed to encourage crack continuity and to accommodate imprecise annotations, combined with MSE and Dice.
- scout's adaptation: Crack class on U-Net++, as an extra term with low weight. It is the only crack-domain topology loss with code and an imprecise-label design.
- evidence: R: improved topology on masonry crack sets. R (TopoMortar): TOPO unstable (CREMI Dice 0.63 +- 0.22) and over-segments OOD images. | prior overlap: none

