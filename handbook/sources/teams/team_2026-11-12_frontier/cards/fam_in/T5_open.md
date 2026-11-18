# T5 open papers: 19 scout records the first T5 team did not take (best first)

## P056 | When Semantic Segmentation Meets Frequency Aliasing
- id arxiv:2403.09065 | 2024 | ICLR 2024 | score 66 | bench 30 | dirs D28 | code https://github.com/Linwei-Chen/Seg-Aliasing
- mechanism: De-aliasing filter zeroes feature-map frequencies above the equivalent Nyquist frequency before each downsampling (parameter free); FreqMix learns channel x spatial weights for below/above-Nyquist bands inside encoder blocks.
- scout's adaptation: Put DAF before the ResNet-34 max-pool and the stride-2 convs of layer2/3/4 (not before conv1, so stride-2 skips keep crack detail); FreqMix in layer1/2. EL fingers (pitch likely 4 to 6 px at 512, unverified) alias into moire from stride 4 onward; moire depends on source rescaling, a plausible cau...
- evidence: R: UPerNet-R50 Cityscapes 78.1 to 79.7 mIoU, boundary IoU 61.8 to 63.2; PASCAL VOC 74.3 to 76.1; ADE20K 38.9 to 40.4. Large datasets, not thin structures. | prior overlap: none; section 5 never varied downsampling or anti-aliasing. 2x resolution n.d. is a different mechanism (compute, not...

## P149 | A Fourier-based Framework for Domain Generalization (FACT); see also arxiv:2108.08487 Amplitude-Phase Recombination
- id arxiv:2105.11120 | 2021 | CVPR 2021 oral | score 55 | bench 40 | dirs D28 | code none found
- mechanism: Amplitude-spectrum mixing between images plus a co-teacher consistency between original and mixed views, so the model relies on phase (structure) rather than amplitude (style).
- scout's adaptation: Treat the 5 sources as domains: mix amplitudes across ARTS / CFVS / CSIR / BMRK / SDLE and with pool cells; keep masks. Aimed at E1 and at the weak BMRK and CFVS sources.
- evidence: R: state of the art on three domain-generalisation classification benchmarks. APR (ICCV 2021): gains in corruption robustness and OOD. No segmentation or EL numbers. | prior overlap: none. Section 5 used brightness / contrast augmentation only.

## P151 | Frequency-aware Feature Fusion for Dense Image Prediction
- id arxiv:2408.12879 | 2024 | TPAMI | score 55 | bench 40 | dirs D28 | code https://github.com/Linwei-Chen/FreqFusion
- mechanism: Decoder feature fusion with an adaptive low-pass filter (consistent interiors), offset resampling, and an adaptive high-pass filter (restores boundary detail lost in downsampling).
- scout's adaptation: Replace the upsample + concat at each U-Net++ decoder node with FreqFusion on 1-channel EL features. The low-pass is meant for blobby inactive regions, the high-pass for 1 to 2 px crack edges.
- evidence: R: gains on semantic, instance and panoptic segmentation and detection (abstract). No thin-structure numbers seen. | prior overlap: none

## P162 | Pasta: Proportional Amplitude Spectrum Training Augmentation for Syn-to-Real Domain Generalization
- id doi:10.1109/iccv51070.2023.01767 | 2023 | ICCV 2023 | score 55 | bench 35 | dirs D28 | code none found
- mechanism: Perturb the Fourier amplitude spectrum with jitter that grows with frequency, keeping phase, to generate augmented views.
- scout's adaptation: Source-free counterpart of FDA: phase kept so crack positions are unchanged; cap the high-frequency jitter so faint cracks (7% are under 2% darker) survive. Aimed at E1 and weak sources BMRK/CFVS.
- evidence: R: beats more complex DG methods on 5 syn-to-real shifts incl. GTAV-to-real segmentation; complementary to them. | prior overlap: none; house augmentation is brightness/contrast only

## P164 | A principled representation of elongated structures using heatmaps
- id doi:10.1038/s41598-023-41221-2 | 2023 | Scientific Reports | score 55 | bench 30 | dirs D11 | code none found
- mechanism: Encode a curve's nominal position and positional uncertainty as a heatmap by convolving the curve distribution with a filter, approximated in linear time by a distance-dependent function.
- scout's adaptation: Filter width per source set from measured label-to-ridge offsets (team E: 48% of label points within 1 px of the ridge); regression head separate from the CE head so it cannot widen the argmax; read out by ridge NMS and draw at per-source width.
- evidence: Approximation error analysed vs curve type and SNR; applied to surgical 2D/3D data, semantic boundaries, skeletonisation. No crack test; numbers not read. | prior overlap: none in BRIEF 5; related to T2 soft_band_jml (soft band inside the CE target) but different head and loss

## P215 | PointScatter: Point Set Representation for Tubular Structure Extraction
- id doi:10.1007/978-3-031-19803-8_22 | 2022 | ECCV | score 50 | bench 35 | dirs D11 | code https://github.com/zhangzhao2022/pointscatter
- mechanism: Split the image into scatter regions, each predicting a small point set, trained by greedy region-wise bipartite matching; points rendered as mask or centreline.
- scout's adaptation: Crack only on stride-4 features (16x16 regions); L1 point regression after matching lands at the mean of jittered labels (sub-pixel); render at source width.
- evidence: R: four public tubular datasets, segmentation and centreline extraction tasks. | prior overlap: None.

## P220 | Wavelet Convolutions for Large Receptive Fields
- id arxiv:2407.05848 | 2024 | ECCV 2024 | score 50 | bench 35 | dirs D28 | code https://github.com/BGU-CS-VIL/WTConv
- mechanism: Convolution applied to wavelet subbands, giving very large receptive fields with log-growing parameters, more shape bias and more robustness to corruption.
- scout's adaptation: WTConvNeXt-T (timm) encoder in U-Net++, or WTConv2d replacing the 3x3 convs in ResNet-34 layer3/4. A whole-cell receptive field should help the half-cut layout and long scuff streaks on E1.
- evidence: R: ImageNet-1K top-1 82.5 / 83.6 / 84.1 (T/S/B, README); better corruption robustness and shape bias. | prior overlap: Only the DINOv3 vs ImageNet ConvNeXt-T 2-seed F51 screen was run; WTConv was never tested.

## P229 | Revisiting Downsampling in Semantic Segmentation: Fighting Aliasing with Dynamic Gaussian and Gabor Frequency Filters
- id doi:10.1609/aaai.v40i9.37713 | 2026 | AAAI 2026 | score 50 | bench 25 | dirs D28 | code none found
- mechanism: Dynamic Gaussian low-pass along edge normals only, then a learnable Gabor directional band-pass that removes residual aliasing peaks concentrated along a few dominant directions; phase-error energy metric.
- scout's adaptation: EL aliasing is directionally sparse (fingers one axis, busbars the other), matching its assumption. Use the Gabor selector before stride-2 layers; use phase-error energy as a diagnostic of finger aliasing in the house encoder.
- evidence: R: consistent gains and sharper boundaries across segmentation datasets (abstract; numbers not read). | prior overlap: none

## P258 | Benefit from public unlabeled data: A Frangi filter-based pretraining network for 3D cerebrovascular segmentation
- id doi:10.1016/j.media.2024.103442 | 2025 | Medical Image Analysis | score 46 | bench 20 | dirs D28 | code https://github.com/shigen-StoneRoot/FFPN
- mechanism: Pretrain on public unlabelled data with Frangi-filter-derived multi-task targets, then fine-tune.
- scout's adaptation: Bold bet: pretrain whole U-Net++ (decoder included) on the 11.9k pool to regress multi-scale dark-ridge maps plus the periodic notch residual; PF fine-tune so the pretraining survives.
- evidence: R: 1,510 unlabelled TOF-MRA scans, about +3% over semi- and self-supervised methods. | prior overlap: partial: MIM and DDeP pool pretraining n.d. (section 5), but ridge-target / thin-structure objectives are listed as open

## P313 | A Directional Connectivity Feature Enhancement Network for Pavement Crack Detection
- id doi:10.1109/tits.2024.3488656 | 2024 | IEEE Transactions on Intelligent Tran... | score 45 | bench 25 | dirs D11 | code none found
- mechanism: Multi-directional enhanced convolution plus a directional-connectivity loss on neighbouring pixels for cracks.
- scout's adaptation: Port only the directional-connectivity loss to the crack head of the house model; closest-domain evidence for DconnNet-style outputs.
- evidence: R: +2.2% ODS and +1.8% mIoU on DeepCrack; +1.2 ODS, +0.9 mIoU on Crack500; six crack datasets. | prior overlap: None.

## P320 | Edge-Boundary-Texture Loss: A Tri-Class Generalization of Weighted Binary Cross-Entropy for Enhanced Edge Detection
- id arxiv:2507.06569 | 2025 | arXiv | score 45 | bench 25 | dirs D11 | code none found
- mechanism: Split pixels into edge, boundary (near-edge) and texture classes, each with its own supervisory weight, generalising weighted BCE.
- scout's adaptation: Crack / 1-2 px ring around the label skeleton / rest; low weight (0.2) on the ring so firing on the ridge 1 px off the drawn line is barely punished; applied to the crack channel of the 24-class CE.
- evidence: Beats WBCE across several edge benchmarks with one fixed hyperparameter set; numbers not read. | prior overlap: partial: BRIEF 5 offset-tolerant CE (n.d.) used tolerance, not near-crack down-weighting; open

## P321 | Frequency-Adaptive Dilated Convolution for Semantic Segmentation
- id arxiv:2403.05369 | 2024 | CVPR 2024 highlight | score 45 | bench 25 | dirs D28 | code https://github.com/Linwei-Chen/FADC
- mechanism: Per-pixel dilation rate set from local frequency content; AdaKern balances low / high kernel parts; FreqSelect damps high frequency in background regions.
- scout's adaptation: Put FADC + FreqSelect in ResNet-34 layer3/4 at output stride 16. FreqSelect could learn to damp the finger frequency band away from defects.
- evidence: R: gains on semantic segmentation and detection (abstract); numbers not read. | prior overlap: none

## P331 | Wavelet and Prototype Augmented Query-based Transformer for Pixel-level Surface Defect Detection
- id doi:10.1109/cvpr52734.2025.02222 | 2025 | CVPR 2025 | score 42 | bench 60 | dirs D28 | code none found
- mechanism: Query-based mask transformer whose queries are refined by wavelet-domain cross-attention (high and low frequency) and prototype cross-attention for cluttered backgrounds.
- scout's adaptation: Benchmark arm: recent pixel-level defect method validated on cracks (CrackSeg9k) and patterned fabric (ZJU-Leaper); 1-channel stem, 24-way queries or per-class binary.
- evidence: R: SOTA on ESDIs-SOD, CrackSeg9k, ZJU-Leaper. Code listed as github.com/yfhdm/WPFormer by a WebSearch summary, not opened. | prior overlap: none; no mask-classification decoder was ever tried (section 5)

## P349 | Deep Frequency Filtering for Domain Generalization
- id arxiv:2203.12198 | 2023 | CVPR 2023 | score 42 | bench 25 | dirs D28 | code none found
- mechanism: FFT of intermediate feature maps with a learned spatial attention mask over frequencies that keeps transferable components and damps the rest.
- scout's adaptation: Insert DFF at layer2 and layer3 of ResNet-34, train with source-balanced batches over the 5 sources, and score on E1.
- evidence: R: beats prior SOTA on closed-set classification and open-set retrieval domain generalisation (abstract). | prior overlap: none

## P401 | Enhancing recall in asphalt pavement crack segmentation using a HoughNet-extended U-Net architecture with reconstruction head
- id doi:10.1038/s41598-025-31492-2 | 2025 | Scientific Reports | score 40 | bench 20 | dirs D11 | code none found
- mechanism: Voting-based (HoughNet) segmentation head plus a reconstruction head to raise crack recall at similar precision.
- scout's adaptation: Swap the crack logit for a log-polar voting head; aimed at relR@2 toward the 0.90 target.
- evidence: R: Crack500 higher recall at similar precision; GAPS384 thin cracks best F1. | prior overlap: None.

## P424 | GraphMorph: Tubular Structure Extraction by Morphing Predicted Graphs
- id doi:10.52202/079017-2187 | 2024 | NeurIPS | score 38 | bench 30 | dirs D11 | code none found
- mechanism: Graph decoder predicts branch-level graph per patch; SkeletonDijkstra morphs it onto the centreline probability map; graph used to remove false positives.
- scout's adaptation: Use only as a crack false-positive filter (drop components not on predicted branches) and as crack topology for severity.
- evidence: R: centreline and segmentation tasks on several vessel and road datasets; fewer false positives. | prior overlap: None.

## P476 | GaborNet: Gabor filters with learnable parameters in deep convolutional neural networks
- id arxiv:1904.13204 | 2019 | arXiv | score 35 | bench 15 | dirs D28 | code none found
- mechanism: First-layer convolution filters constrained to Gabor functions whose parameters are learned by backpropagation.
- scout's adaptation: A parallel stem of 16 learnable Gabor filters (8 orientations x 2 scales, wavelength 4 to 8 px) on the 1-channel EL input, concatenated to the conv1 output.
- evidence: R: faster convergence and better accuracy than plain CNNs on several recognition datasets (abstract). | prior overlap: none

## P482 | Segment Anything Model for Road Network Graph Extraction
- id doi:10.1109/cvprw63382.2024.00262 | 2024 | CVPRW | score 33 | bench 45 | dirs D11 | code https://github.com/htcr/sam_road
- mechanism: Fine-tuned SAM encoder predicts vertex and intersection masks, NMS gives vertices, a small transformer predicts edges, giving a vector graph.
- scout's adaptation: Severity, not IoU: a crack graph per cell gives crack mode (single line, dendritic, cross) and length; benchmark severity track.
- evidence: R: comparable to RNGDet++ on City-scale, 40x faster. | prior overlap: None.

## P542 | SEMIR: Topology-Preserving Graph Minors for Thin-Structure Segmentation
- id arxiv:2606.24935 | 2026 | arXiv | score 28 | bench 25 | dirs D11 | code none found
- mechanism: Replace the pixel lattice with a graph minor whose contraction preserves 1-3 px structures; a GNN classifies supernodes and an exact map lifts predictions to pixels.
- scout's adaptation: Build the minor with EL ridge filters so crack px are never merged into background; GNN on house encoder features; aimed at fragmentation (components found).
- evidence: TTPLA power lines, CrackSeg9k, SkyScapes lanes: matches or beats domain baselines on Dice, IoU, Boundary F1; fragmentation at least 4.6x lower than SLIC. | prior overlap: none

