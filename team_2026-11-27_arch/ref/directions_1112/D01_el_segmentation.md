# D01: EL solar-cell defect semantic segmentation, 2020 to 2026

Scout: D01 literature agent, 12 Nov 2026. Tags: R = what a paper measured, E = what our files measured (from BRIEF), S = my judgement.

## 1. Queries run

Research MCP `search_papers` (limit 15 to 20, abstract_chars 250):
1. electroluminescence solar cell defect segmentation (2020+)
2. EL image crack segmentation photovoltaic deep learning (2020+)
3. E-SCDD solar cell defect dataset segmentation (2023+)
4. transformer solar cell defect segmentation electroluminescence (2022+)
5. photovoltaic cell defect segmentation Mamba (2024+)
6. UCF-EL dataset crack segmentation solar cell (2022+)
7. PVEL-S solar cell defect segmentation dataset (2021+)
8. solar cell crack segmentation electroluminescence (2025+)
9. photovoltaic electroluminescence semantic segmentation U-Net attention defects multi-class (2024+)
10. segment anything model photovoltaic defect electroluminescence (2023+)
11. micro-crack segmentation solar cell EL thin crack network (2020+)
12. electroluminescence defect segmentation domain generalization cross-dataset unseen modules (2022+)
13. solar cell electroluminescence segmentation class imbalance loss function rare defects (2021+)
14. photovoltaic defect segmentation electroluminescence edge boundary lightweight network (2025+)
15. half-cut solar cell electroluminescence defect detection segmentation (2021+)
16. synthetic electroluminescence images defect generation diffusion segmentation training photovoltaic (2024+)

Snowballing: `similar_papers` on MultiSolSegment + STC-Net + Torpey 2024; `get_citations` on Pratt 2023 (65 citing) and Fioresi 2022 UCF-EL (112 citing).
Full text read (already in local library, no new fetch needed): STC-Net, MultiSolSegment, Torpey 2024, PV-DDPM/E-SCDD, Pratt 2023. Fetch attempts: SEiPV-Net (no PDF), PV-S3 (timeout).
`search_snippets`: 5 attempts, all rejected by the Semantic Scholar rate limit.
WebSearch (7): PV-MambaSeg code, MultiSolSegment code, recent 2026 EL segmentation, PV-S3 loss, SAM + domain knowledge paper, Hijjawi code, pv-vision repo.

## 2. Landscape in one paragraph (S)

Pixel-level EL work since 2020 falls into: (a) dataset papers with U-Net / DeepLabv3+ baselines (Pratt 2021/2023, Fioresi 2022 UCF-EL, Chen 2023 LBNL, Hanifi 2025, E-SCDD 2025, MultiSolSegment 2026); (b) bespoke architectures on private or binary sets with very high but non-comparable mIoU (PDeT 88.4 on own data, ERDCF 92.8, STC-Net 72.5 test on PVEL-S, PV-MambaSeg); (c) training-regime papers (Torpey 2024 pretraining, PV-S3 semi-supervised); (d) generative data (PV-DDPM). No paper reports per-class crack IoU on BenchmarkEL with a module-disjoint split, a tolerant crack metric, or an unseen-module test. Nothing found beats a ResNet-34 U-Net++ under our protocol, because nobody ran that protocol. The strongest transferable ideas are mechanisms, not architectures: multi-label heads for overlapping crack/inactive, whole-network dense pretraining, full-resolution skips for 1 to 2 px lines, fixed high-pass priors, strip attention for long thin lines, and mask-conditioned diffusion for half-cut cells.

## 3. Selected papers

| # | id | year | venue | code | mechanism | adaptation to our data | score | bench |
|---|---|---|---|---|---|---|---|---|
| 1 | arxiv:2603.13337 (MultiSolSegment) | 2026 | Solar Energy | not found (data on DuraMAT) | Per-channel sigmoid multi-label U-Net so a pixel can be crack and busbar/dark at once; removes artificial crack breaks | Keep house U-Net++; add sigmoid crack and inactive channels trained with BCE + soft Dice; build multi-label targets: inactive = hole-filled inactive region including crack pixels inside it, crack = crack label even inside inactive; softmax head kept for the other 22 classes; crack/inactive thresholds chosen on val | 68 | 70 |
| 2 | arxiv:2402.17611 (Torpey, Pratt, Klein) | 2024 | arXiv | none verified | Whole-network COCO segmentation pretraining (encoder + decoder) gave the best crack IoU on the BenchmarkEL family (p <= 0.0001 vs all other regimes); in-domain SimCLR on ~30k EL worse than ImageNet | Use a segmentation-pretrained full model (ADE20K / COCO UPerNet, SegFormer or Mask2Former), average RGB first-conv weights to 1 channel, PF schedule so pretraining survives; compare against house, not against ResNet-50 DeepLabV3 (ResNet-50 already worse on inactive here) | 50 | 80 |
| 3 | doi:10.1007/978-981-96-8892-0_4 (Hanifi et al.) + doi:10.1109/jphotov.2023.3249970 (Chen et al.) | 2025 / 2023 | LNCS / IEEE JPV | github.com/sntubix/pv-defect-segmentation ; github.com/hackingmaterials/pv-vision | VGG16-UNet best of six models on the 29-class SCDD; LBNL crack model also VGG16-UNet. S: VGG keeps a full-resolution 64-ch skip, ResNet-34 drops to 1/2 then 1/4 in the stem | Swap the encoder to vgg16_bn (or add a full-res stem branch to ResNet-34) in U-Net++ so the decoder sees full-res features for 1 to 2 px cracks and gridlines; 1-ch input, same schedule | 52 | 75 |
| 4 | arxiv:2511.09604 (PV-DDPM, E-SCDD) | 2025 | arXiv | github.com/sntubix/pv-ddpm ; HF snt-ubix/e-scdd | Mask-conditioned DDPM generating EL cells for 4 cell types incl. half-cut multi; E-SCDD ships 195 labelled synthetic + 1,768 unlabelled synthetic cells | Cheapest arm: add the 195 labelled synthetic cells (30 half-cut) to training. Second arm: train the generator on train cells + E-SCDD half-cut cells that are NOT in H36 val, render half-cut cells from train crack masks, plus scuff-like dark streaks without crack labels as hard negatives | 55 | 60 |
| 5 | arxiv:2608.01714 (STC-Net) | 2026 | arXiv / MERCon | none found | Fixed Sobel edge map and FFT radial high-pass map, each through a small pyramid injected into decoder skips with learned fusion weights; edge, topology, coarse auxiliary heads with deep supervision | Minimal form: Sobel magnitude + high-pass residual as 2 extra input channels (3-ch first conv); full form: prior pyramids fused at each U-Net++ decoder node. Watch E1 scuff streaks and gridlines, which are also high-frequency | 48 | 35 |
| 6 | doi:10.1109/tii.2023.3275705 (RERN) | 2023 | IEEE TII | none found | Defect segmentation as edge detection with bidirectional strip refinement attention (long-range horizontal/vertical context, lightweight); scored by ODS F-measure with a distance tolerance | Insert strip attention (BSRA or strip pooling) into the last two U-Net++ decoder stages; targets gridline (weak class, long straight lines) and long cracks along busbar directions. Tolerant ODS/OIS is a template for the benchmark crack metric | 50 | 60 |
| 7 | doi:10.1016/j.sasc.2023.200048 (Pratt et al. benchmark) | 2023 | Systems and Soft Computing | dataset only | Weighted CE with engineered class weights (crack 100, gridline 10, inactive 10, ribbons 3), DOE-validated; best DeepLabv3+ crack median IoU 0.25, recall 0.86; predictions dilated | Do not reweight crack (house already balances it with Dice). Apply weights to the weak "other" classes only: gridline, splice, edge_dark, material (e.g. inverse-sqrt frequency, capped at 10) | 45 | 92 |
| 8 | doi:10.1109/jphotov.2024.3450009 (SegFormer for EL) | 2024 | IEEE JPV | none found | SegFormer (hierarchical transformer + all-MLP decoder) beat DeepLabv3, U-Net, DeepLabv3+, PAN, PSPNet, FPN on UCF-EL (mIoU 56.54, unweighted F1 81.96) | MiT-B2/B3 with ADE20K weights, 1-ch stem, 512 px; add a full-res conv skip before the head since SegFormer predicts at 1/4 res and would blur 1 to 2 px cracks; PF-style lower encoder lr | 45 | 85 |
| 9 | doi:10.1016/j.solener.2025.114083 (Hijjawi et al.) | 2025 | Solar Energy | stated public, URL not verified | Instance / mask-classification models (Mask R-CNN, ConvNeXt, ConvNeXt-V2, Mask2Former) on UCF-EL; ConvNeXt-V2 best (seg mAP50 0.602, mIoU 0.650) | Mask2Former in semantic mode (Swin-T or R50, ADE20K) at 512 px 1-ch; aimed at inactive (blobby, few regions per cell) and mIoU_rob; crack likely needs the house model in a heterogeneous ensemble | 45 | 75 |
| 10 | doi:10.3390/en16237726 (SEiPV-Net) | 2023 | Energies | none found | Lightweight encoder-decoder on the same 24-class Pratt data; compared weighted CE, weighted squared Dice and weighted Tanimoto losses with custom vs equal class weights | Test the weighted Tanimoto (Jaccard-type) loss on crack + inactive + weak classes in the house model; per-class numbers not retrieved (full text unavailable) | 35 | 55 |
| 11 | doi:10.1109/tii.2026.3707683 (PV-MambaSeg) | 2026 | IEEE TII | "will be made public", not found | Vision Mamba with omni-local multi-direction scan and global-local VSS block; claims best mIoU on two PV defect datasets at 2.77 M params, 0.78 GFLOPs | If code appears, train as-is at 512 1-ch; multi-direction scans could follow long cracks across a cell. Needs Mamba kernels (install needs user OK) | 35 | 65 |
| 12 | doi:10.1039/d5ee05042a (EI-AE) | 2025 | Energy & Env. Science | none found | Iterative autoencoder trained only on normal EL cells gives pixel-level anomaly maps for all defect types; few-shot extension with a few masks | Bold bet for E1: train on pool cells including the 1,152 multi half-cells, feed the anomaly map as an extra input channel (or as an auxiliary prior) so half-cut layouts are "normal" and cracks stand out; scuffs will also be anomalies, so the segmenter must still learn to reject them | 38 | 40 |
| 13 | doi:10.1109/jphotov.2021.3131059 (Fioresi, UCF-EL) | 2022 | IEEE JPV | not verified | Large polygon-mask EL dataset (crack region, contact, interconnect, corrosion) with a U-Net baseline (crack recall 0.82 per Pratt 2023) | Joint training with a second head for UCF-EL classes (shared encoder/decoder, separate 1x1 heads, loss only on each dataset's own labels), instead of the pretrain-then-erase run that failed | 32 | 85 |
| 14 | arxiv:2404.13693 (PV-S3) | 2025 | Eng. Appl. of AI | github.com/abj247/PV-S3 | Mean-teacher SSL with a thresholded "Semi Cross-Entropy" loss for class imbalance; +9.7 mIoU over supervised SOTA on UCF-EL with 20% labels | Only as a benchmark baseline; mean teacher at 100% labels is closed here | 15 | 70 |
| 15 | doi:10.1109/pvsc48317.2022.9938503 (Chen, maximum inactive area) | 2022 | IEEE PVSC | github.com/hackingmaterials/pv-vision | From predicted cracks + busbars, compute the worst-case isolated (potentially inactive) area per cell | Post-evaluation only: severity layer on top of our crack + busbar/ribbon predictions; compare predicted isolated area with labelled inactive fraction on test / E1 | 20 | 75 |

### Minimum experiments (all on cv02 A6000s, house = U-Net++ R34 1-ch 512 px 20k steps; 5 seeds per arm unless stated; clean-49 test, E1, F51 as in BRIEF; crack IoU detectable change about 0.012)

1. MultiSolSegment: arm = house + sigmoid crack/inactive heads with multi-label targets; baseline = house and PF; metrics = inactive IoU (clean 49 and E1), crack IoU, relF1@2; kill if inactive IoU gain < 0.02 on both test and E1 and crack IoU not >= house. About 11 GPU-h.
2. Torpey dense pretraining: arm = UPerNet or SegFormer with ADE20K full-model weights, PF schedule; baseline = house PF; metrics = crack IoU, mIoU_rob, E1 crack relF1@2; kill if crack IoU < house - 0.01 and mIoU_rob not higher. 3 seeds screen first. About 15 GPU-h.
3. Full-res skip (Hanifi/Chen VGG16): arm = U-Net++ vgg16_bn encoder (check smp exposes a full-res stage) or R34 + full-res stem branch; baseline = house; metrics = crack IoU, relF1@2, gridline IoU; kill if crack IoU < +0.012 and gridline IoU < +0.03. About 12 GPU-h.
4. PV-DDPM / E-SCDD synthetic: arm A = house + 195 labelled synthetic cells (no generator training); arm B = house + ~2k generated half-cut crack cells (1:3 mix); baseline = house; metrics = E1 crack recall and relF1@2 on the half-cut subset, clean-49 crack IoU; kill if E1 relF1@2 gain < 0.03 and test crack IoU drops > 0.01. Arm A about 11 GPU-h; arm B adds about 40 GPU-h for the generator.
5. STC-Net priors: arm = house + Sobel and high-pass input channels (then full decoder injection if positive); baseline = house; metrics = E1 crack recall / relF1@2, test crack IoU; kill if E1 relF1@2 < +0.03 and test crack IoU drops > 0.01. About 11 GPU-h.
6. RERN strip attention: arm = house + strip attention in last 2 decoder stages; baseline = house; metrics = gridline IoU / recall, crack relF1@2; kill if gridline IoU < +0.03 and crack relF1@2 not up. About 12 GPU-h.
7. Pratt class weights: arm = house + CE weights on gridline, splice, edge_dark, material; baseline = house; metrics = mIoU_rob, gridline recall, splice IoU; kill if mIoU_rob < +0.01 or crack IoU drops > 0.01. About 11 GPU-h.
8. SegFormer: arm = MiT-B2 ADE20K + full-res skip, 30k steps; baseline = house; metrics = mIoU_rob, crack relF1@2, E1 crack recall; kill if all three below house. 3 seeds screen. About 10 GPU-h.
9. Mask2Former semantic: arm = Mask2Former Swin-T ADE20K; baseline = house; metrics = inactive IoU, mIoU_rob; kill if inactive IoU < house and mIoU_rob < house - 0.01. 3 seeds. About 15 GPU-h.
10. Tanimoto loss: arm = house with weighted Tanimoto replacing soft Dice; baseline = house; metric = crack IoU, inactive IoU; kill if neither moves beyond noise. About 11 GPU-h.
11. PV-MambaSeg: only if code is released; 3 seeds vs house on mIoU_rob and crack relF1@2; kill if both below house. About 8 GPU-h.
12. EI-AE prior: train EI-AE on ~5k pool cells (incl. half-cells), arm = house + anomaly-map channel; metric = E1 crack recall at fixed test precision; kill if E1 recall gain < 0.05. About 25 GPU-h.
13. UCF-EL joint training: arm = shared model, two heads, alternating batches 1:1; baseline = house; metrics = crack IoU, E1 crack recall; kill if both within noise. About 15 GPU-h.
14. PV-S3: benchmark baseline run only.
15. Chen isolated area: zero training; compute on existing predictions; report correlation of predicted isolated area with labelled inactive fraction per cell.

### Prior overlap with BRIEF section 5 (honest)
- Multi-label heads, transformers, Mamba, mask-classification decoders, edge/strip-attention formulations, generative synthesis, anomaly priors, cross-dataset joint training: listed as never tried. Open.
- Torpey dense pretraining: foundation encoders were tested as frozen probes and one ConvNeXt-T fine-tune screen; full-network segmentation pretraining with PF was not. Open.
- Full-res skip: only ResNet-34/50 encoders tried. 2x input resolution was n.d. at 4x compute; a full-res skip is a different and cheaper change. Open.
- Class weights: Dice on 12 classes (worse) and on 3 (n.d.) tried; weighted CE for weak classes not listed. Open.
- Tanimoto: Lovasz / Jaccard losses listed as untested. Open.
- PV-DDPM: synthetic half-cut views were geometric, crack copy-paste was pasting; mask-conditioned diffusion is untested. The 107 real E-SCDD cells (n.d.) are a different thing from the 195 synthetic labelled cells. Open.
- PV-S3: mean teacher at 100% labels with external pool was n.d. Closed for raising scores; kept for the benchmark.
- UCF-EL: encoder pretraining then house fine-tune (erased) failed; joint training is open.

## 4. Benchmark notes from this direction (S, for the benchmark builder)
- Pratt 2023 reports median IoU and median recall over 50 test cells for 5 classes; Torpey 2024 reports mIoU, frequency-weighted IoU, and block-centred per-image IoU with Tukey HSD over repeated runs. Both use the 2021/2022 BenchmarkEL releases (593 / 642 cells), not ours (582, revised labels). Numbers are not comparable to ours.
- RERN uses ODS/OIS F-measure with a distance tolerance (maxDist) for thin defect edges: a published precedent for a tolerant crack metric like our relF1@2.
- Recent EL segmentation methods a credible benchmark should run under one protocol: U-Net / U-Net++ (house), DeepLabv3+ with Pratt custom weights, VGG16-UNet (Hanifi, pv-vision), SegFormer, Mask2Former, PV-S3, plus PV-MambaSeg and STC-Net if code appears.
- Severity: pv-vision's maximum isolated area is the only open-source crack-to-inactive-area tool found; STC-Net derives an "inactive-area proxy" from crack masks but only against a 1 W normalised surrogate, with no electrical ground truth.

## 5. Rejected (one line each)
- PDeT, doi:10.3390/s24216908: deformable transformer, mIoU 88.41 on a private dataset, no code; no evidence on thin cracks.
- ERDCF-Net, doi:10.1109/tsm.2022.3197933: crack-only binary seg with refined side outputs; similar deep-supervision idea already covered by STC-Net and RERN; no code.
- CrackNet, doi:10.1016/j.renene.2025.124549: transformer microcrack detector, abstract not retrievable.
- SIIF, doi:10.1016/j.apenergy.2024.123643: PV defect segmentation, abstract not retrievable.
- Song et al. SAM + domain knowledge, doi:10.1016/j.solener.2025.114145 and doi:10.2139/ssrn.5289330: likely relevant (SAM fine-tune for PV defects) but no abstract or full text retrievable; see gaps.
- Referring segmentation, doi:10.1109/tii.2025.3567396: text-conditioned task, does not raise our metrics.
- Attention SegNet (Mazen 2024, doi:10.1109/access.2024.3431098): 29-class SegNet reported by accuracy; no mechanism beyond attention gates.
- Pratt 2021 U-Net (doi:10.1016/j.renene.2021.06.086) and Otamendi 2021 (doi:10.1016/j.solener.2021.03.058): superseded baselines / module-level pipelines.
- Byford 2025 EL to I-V (doi:10.1109/jphotov.2025.3562931): module-level Swin regression; needs I-V curves we do not have. Severity reference only.
- Mueez 2026 generative defect isolation (doi:10.1016/j.solener.2026.114943) and many YOLO / classification papers: image-level or box-level, not segmentation.
- Feng and Cao 2026 structure-aware lightweight network (doi:10.1109/nesp70395.2026.11622052): abstract truncated, conference paper, no code found; worth a second look for gridline-interference handling.

## 6. Gaps
- Semantic Scholar snippet search was rate-limited for the whole session, so per-class numbers for SEiPV-Net, SegFormer-EL, Hijjawi and PV-MambaSeg are not recorded.
- No code found for PV-MambaSeg, STC-Net, MultiSolSegment, SEiPV-Net, RERN, SegFormer-EL, Hijjawi (stated public, URL unverified).
- Song et al. 2025 SAM fine-tuning for PV defects: needs full text (Elsevier, off campus) to judge.
- Thin-structure segmentation outside PV (retinal vessels, road cracks, clDice successors) is out of D01 scope but is where full-res skip and strip attention evidence lives; deserves its own direction.
- Nobody reports EL segmentation on half-cut cells with crack labels except E-SCDD; an E1-style unseen-module test does not exist in the literature.
