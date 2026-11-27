# T3 open papers: 17 scout records the first T3 team did not take (best first)

## P010 | Adaptive Early-Learning Correction for Segmentation from Noisy Annotations (ADELE)
- id doi:10.1109/cvpr52688.2022.00263 | 2022 | CVPR | score 72 | bench 60 | dirs D15,D16 | code https://github.com/Kangningthu/ADELE
- mechanism: Detects per class the onset of memorisation from the train IoU curve against noisy labels, then from that point replaces labels with confident, multi-scale-consistent model predictions.
- scout's adaptation: Per-class curves for crack, inactive, gridline and splice on the 478 train cells. Correction is allowed only (a) within 3 px of an existing crack label, to re-centre it on the ridge while keeping that source's width, and (b) for new components with p>0.9 at every scale, to recover missing cracks....
- evidence: R (abstract): beats standard noisy-label methods on a medical segmentation task with noisy annotations, and is SOTA for weakly supervised segmentation on PASCAL VOC 2012. Thin-structure numbers were not read because t... | prior overlap: none. BRIEF section 5 lists noisy-label methods and automatic label refinement as never tried.

## P059 | Modeling annotator preference and stochastic annotation error for medical image segmentation (PADL)
- id doi:10.1016/j.media.2023.103028 | 2023 | Medical Image Analysis | score 64 | bench 50 | dirs D15,D17 | code none found
- mechanism: A shared network with one head per annotator models each annotator's systematic preference and stochastic error (Gaussian) separately from a consensus segmentation.
- scout's adaptation: The 5 sources play the role of 5 annotators: a shared U-Net++ decoder, one 1x1 head per source, plus a consensus head. At test, use the cell's source head (source is known for every cell), which reproduces that source's crack width and placement, the only route BRIEF names to strict IoU above 0.5...
- evidence: R: multi-annotator medical segmentation; it models preference and error separately. Abstract not retrieved by the tool; numbers not read. | prior overlap: none. Source-conditional prediction and annotator / source-style modelling are on BRIEF's never-tried list.

## P081 | PNT-Edge: Towards Robust Edge Detection with Noisy Labels by Learning Pixel-level Noise Transitions
- id doi:10.1145/3581783.3612136 | 2023 | ACM MM | score 62 | bench 35 | dirs D13,D15,D16,D17 | code https://github.com/DREAMXFAR/PNT-Edge
- mechanism: Models label corruption as a smooth displacement field. A 4-layer FCN takes the image, confident predictions and the noisy label, and warps the detector output onto the noisy label, so the detector itself fits the clean, aligned edges.
- scout's adaptation: Warm up the house model only until the val crack metric saturates (the memorization point). Then train jointly with the warp module on the crack channel, max shift 3 px. Drop or replace the local-edge-density prior with ridge strength, because cracks are sparse. The warp absorbs per-source and pe...
- evidence: R: gains over CASENet-S and SEAL on SBD and Cityscapes, scored on a re-annotated clean SBD subset. Shows the memorization effect: clean-label metrics saturate early, then the model memorizes noise. Losses: MSE on conf... | prior overlap: Partly overlaps offset-tolerant CE (n.d.). A learned smooth displacement field with suppression of unmatched pixels i...

## P209 | Learning robust medical image segmentation from multi-source annotations (UMA-Net)
- id doi:10.1016/j.media.2025.103489 | 2025 | Medical Image Analysis | score 50 | bench 40 | dirs D15 | code none found
- mechanism: Pixel-level annotation-uncertainty estimates weight the loss, and an image-level quality module routes each sample to a high-quality or a low-quality decoder head.
- scout's adaptation: Image quality is set from source and label-width deviation: BMRK, SDLE and the speck-level H36 labels go to the low-quality head. Pixel weights come from 5-seed disagreement. The high-quality head is used at test.
- evidence: R (web abstract): on simulated JSRT lung data, +5.31% over single-annotation noise-robust methods and +1.47% over multi-source methods; tested on chest X-ray, fundus and breast DCE-MRI. | prior overlap: none

## P210 | Unlocking Robust Semantic Segmentation Performance via Label-only Elastic Deformations against Implicit Label Noise (NSegment+)
- id arxiv:2508.10383 | 2025 | arXiv | score 50 | bench 40 | dirs D15 | code none found
- mechanism: Elastic deformation applied to labels only (image untouched), resampled every epoch, to model implicit boundary noise; small segments exempted.
- scout's adaptation: Invert the small-object rule: apply smooth 0.5 to 1.5 px deformation to crack and inactive labels only (sigma 4 to 8 px, p 0.5), never to structural classes. One dataloader change.
- evidence: R: mIoU +2.29 Vaihingen, +2.38 LoveDA, +1.75 Cityscapes, +3.39 VOC; vs LNL methods with DeepLabV3+: +0.81 Vaihingen, +0.63 Cityscapes, beating AIO2, L2B, UCE, Compensation Learning. | prior overlap: partial: offset-tolerant CE (n.d.) also targets shift tolerance; label-only stochastic jitter is a different regulari...

## P254 | Noisy Supervision for Correcting Misaligned Cadaster Maps Without Perfect Ground Truth Data
- id arxiv:1903.06529 | 2019 | arXiv | score 48 | bench 25 | dirs D16 | code none found
- mechanism: A multi-resolution network predicts a dense displacement field that moves misaligned map polygons onto image evidence, trained on the noisy data itself and applied iteratively so dataset alignment improves round by round.
- scout's adaptation: Train a small U-Net (image + jittered label in, 2-channel displacement out) on synthetic jitter drawn from our measured offset distribution (48% within 1 px, 64% within 2 px) applied to high-confidence snapped labels (ARTS, strong ridges); apply to all train crack labels, two rounds; then train t...
- evidence: R: cadaster/OSM building alignment on aerial imagery (web search listing only; numbers not read). | prior overlap: none.

## P270 | From noisy labels to intrinsic structure: A geometric-structural dual-guided framework for noise-robust medical image segmentation (GSD-Net)
- id doi:10.1016/j.media.2026.104130 | 2026 | Medical Image Analysis | score 45 | bench 60 | dirs D15 | code https://github.com/ortonwang/GSD-Net
- mechanism: Geometric distance-aware pixel weights, structure-guided label refinement, and region swapping between image pairs for diversity.
- scout's adaptation: Distance weights from the crack distance transform down-weight the uncertain 1-2 px label edge. Region swaps pair cells from different sources. It is the most recent noise-robust baseline for the benchmark suite.
- evidence: R (web abstract): with simulated noise, +2.52% on Kvasir, +22.76% on Shenzhen, +8.87% on BU-SUC and +4.59% on BraTS2020; also tested on LIDC and MMIS-2024 with real multi-expert labels. | prior overlap: none

## P287 | Imbalanced Medical Image Segmentation With Pixel-Dependent Noisy Labels (CLCS)
- id doi:10.1109/tmi.2024.3524253 | 2024 | IEEE TMI | score 45 | bench 45 | dirs D15 | code https://github.com/Erjian96/CLCS
- mechanism: Two-branch collaborative learning votes on pixel cleanliness with a curriculum dynamic threshold that protects minority classes, and a noise balance loss on suspected noisy pixels instead of dropping them.
- scout's adaptation: Two U-Net++ decoders on one ResNet-34 encoder; noise handling restricted to crack and inactive pixels; class-wise thresholds tuned for 0.19% crack pixels.
- evidence: R: more than 3% Dice and mIoU gains on two benchmarks with different segmentation noise types (abstract). | prior overlap: none; CPS at 5% labels was a semi-supervised use of two branches, not noisy-label selection.

## P319 | DragOSM: Extract Building Roofs and Footprints from Aerial Images by Aligning Historical Labels
- id arxiv:2509.17951 | 2025 | arXiv | score 45 | bench 25 | dirs D16 | code https://github.com/likaiucas/DragOSM
- mechanism: Label alignment as iterative denoising: a model learns to move randomly Gaussian-perturbed labels back to their position, then is applied iteratively to real misaligned labels.
- scout's adaptation: Bold bet: train a small label snapper on (EL image, crack label perturbed by 1 to 3 px shifts and width changes) to recover the unperturbed label. Annotator jitter is random but the ridge is consistent, so the snapper should learn the expected label position given the image, which sits on the rid...
- evidence: R: new ReBO dataset, 179,265 buildings with OSM and corrected labels in 5,473 images; reported effective alignment (numbers not read). | prior overlap: none

## P336 | AIO2: Online Correction of Object Labels for Deep Learning With Incomplete Annotation in Remote Sensing Image Segmentation
- id doi:10.1109/tgrs.2024.3373908 | 2024 | IEEE TGRS | score 42 | bench 35 | dirs D15 | code https://github.com/zhu-xlab/AIO2
- mechanism: Adaptive correction trigger from the mean-teacher accuracy curve plus online object-wise label correction for missing objects.
- scout's adaptation: Add teacher-predicted crack components to labels only if p > 0.9, length >= 20 px and not inside scuff / edge_dark; targets missed cracks flagged by the audit and speck-level H36 labels.
- evidence: R: robust under varying building label omission on two footprint datasets; in NSegment+ comparison AIO2 gave +0.20 Vaihingen, +0.54 Cityscapes mIoU at 2x FLOPs. | prior overlap: partial: MT pseudo-labelling was run as SSL; online object-wise completion of labelled cells was not.

## P352 | Object Detection as a Positive-Unlabeled Problem
- id doi:10.5244/c.34.74 | 2020 | BMVC | score 42 | bench 25 | dirs D15 | code none found
- mechanism: Treats unlabelled regions as unlabelled rather than negative, using a non-negative PU risk with a class prior, so missing annotations stop teaching false negatives.
- scout's adaptation: nnPU risk on crack vs background pixels only inside the dark-ridge mask, where missing cracks can hide; standard CE elsewhere. The class prior is set per source from labelled crack density.
- evidence: R (abstract): a PU loss beats the standard PN loss on PASCAL VOC and COCO across levels of missing labels. Detection, not segmentation. | prior overlap: none

## P386 | A Bayesian Approach to Segmentation with Noisy Labels via Spatially Correlated Distributions
- id arxiv:2504.14795 | 2025 | arXiv | score 40 | bench 30 | dirs D15 | code https://github.com/pfnet-research/Bayesian_SpatialCorr
- mechanism: Variational inference over spatially correlated label errors via a latent Gaussian field with KMS-structured covariance (ECCD).
- scout's adaptation: Model crack labels as truth with flips correlated along the crack direction (correlation length about 10 px), covering both jitter and omission.
- evidence: R: spatial correlation modelling clearly helps on several tasks; lung segmentation near clean-label level at moderate noise (abstract). | prior overlap: none

## P400 | Prompt and Refinement: Asymmetric Mutual Learning for Infrared Small Target Detection with Noisy Labels
- id arxiv:2610.05918 | 2026 | arXiv | score 40 | bench 25 | dirs D16 | code none found
- mechanism: Two asymmetric learners, one prompt-driven and one refinement-driven, correct each other's noisy masks for small faint targets (abstract-level reading).
- scout's adaptation: Short faint crack components (76 to 88% under 20 px) are the closest analogue; would pair a prompt-based refiner with the house model to correct crack labels mutually. Details unread (MCP down).
- evidence: unverified beyond abstract fragment. | prior overlap: partial: CPS/mutual learning was run at 5% for SSL, not for correcting labelled-set labels.

## P419 | Distribution-aware Noisy-label Crack Segmentation
- id arxiv:2410.09409 | 2024 | arXiv | score 38 | bench 35 | dirs D15 | code none found
- mechanism: A SAM-Adapter for cracks, guided by distribution-aware domain knowledge so that it resists omitted and mislabelled cracks in small training sets; tested on an unseen crack dataset.
- scout's adaptation: Bold bet for E1: fine-tune a SAM / SAM2 adapter on 1-channel EL replicated to 3 channels at 1024 px, with noise guidance from the house-model 5-seed ensemble. Judge on E1 half-cut cells.
- evidence: R (abstract): beats SOTA on two pavement crack datasets and generalises to the unseen CFD dataset. | prior overlap: SAM2 Hiera-T was only linear-probed frozen (no sign of gain). Adapter fine-tuning with noisy-label guidance was not t...

## P462 | SegFix: Model-Agnostic Boundary Refinement for Segmentation
- id doi:10.1007/978-3-030-58610-2_29 | 2020 | ECCV | score 35 | bench 35 | dirs D16 | code none found
- mechanism: Predict a boundary map and a direction map; replace each boundary pixel's label with that of an interior pixel along the predicted direction; applies to predictions or labels.
- scout's adaptation: Post-processing and label cleaning for blob/band classes (inactive, ribbons, border, frame_edge, edge_dark); not for 1 to 2 px cracks (no interior).
- evidence: R: boundary quality gains on Cityscapes/ADE20K (known from paper; numbers not read here). | prior overlap: none: refinement stages never tried (BRIEF).

## P529 | IUR-Net: A Multi-Stage Framework for Label Refinement Tasks in Noisy Remote Sensing Samples
- id doi:10.3390/rs17132125 | 2025 | Remote Sensing | score 30 | bench 20 | dirs D16 | code none found
- mechanism: Multi-stage label refinement for remote-sensing samples with image-label mismatch and inconsistent annotation quality (abstract-level).
- scout's adaptation: Candidate recipe for cleaning the 24-class structural labels drawn with different conventions per source; details unread.
- evidence: unverified beyond abstract. | prior overlap: none.

## P584 | Noisy Annotations in Semantic Segmentation
- id arxiv:2406.10891 | 2024 | arXiv | score 20 | bench 58 | dirs D15,D16 | code https://github.com/eden500/Noisy-Labels-Instance-Segmentation
- mechanism: A benchmark of spatial annotation noise (boundary distortion, class confusion, tool artefacts) on COCO-N, Cityscapes-N and VIPER-N.
- scout's adaptation: Shapes the EL benchmark: add a label-noise stress track with calibrated crack jitter and source-width noise, and report each method's sensitivity. It also warns that classification-style noise-robust methods may fail on thin, boundary-dominated cracks.
- evidence: R (web abstract): mainstream label-noise robustness methods fail on boundary-sensitive segmentation; denoising gives limited benefit for instance segmentation. | prior overlap: none

