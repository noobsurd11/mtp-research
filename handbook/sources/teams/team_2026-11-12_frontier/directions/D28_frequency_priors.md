# D28 Frequency, wavelet and filter priors; patterned-background defect detection

Scout: D28. First pass 12 Nov 2026 (Research MCP down, WebFetch only). Resumed and finalised 13 Nov 2026 with the Research MCP working.
R = what a paper measured. E = what our files measured. S = my judgement.

## Tool situation
- 12 Nov: Research MCP returned HTTP 502 on every call; 9 WebSearch queries, 24 WebFetch page checks.
- 13 Nov: Research MCP up for OpenAlex and arXiv. Semantic Scholar was rate-limited all session (so `search_snippets` failed 3 times), Scopus and ScienceDirect returned 401. 24 MCP searches / snowball calls, 15 get_paper checks, 2 fetch_fulltext (1 succeeded: arXiv 2403.09065; the PMC copy of the Hessian vector-field paper failed), 1 read of the already-downloaded STC-Net text, 4 WebSearch queries.
- Every id in the table was returned by `get_paper` or `search_papers` this session, except where marked.

## Queries run
Research MCP `search_papers` (13 Nov; year_from in brackets):
1. wavelet U-Net segmentation thin structures (2020)
2. defect segmentation periodic texture background suppression deep learning (2020)
3. learnable Frangi vesselness Hessian layer neural network (2019)
4. wavelet crack segmentation (2025)
5. frequency domain learning thin structure segmentation high-frequency (2024)
6. Fourier periodic pattern removal defect detection TFT-LCD wafer PCB deep learning (2020)
7. learnable Gabor convolution layer segmentation (2020)
8. electroluminescence solar cell crack detection frequency domain wavelet (2020)
9. XNet wavelet-based low and high frequency fusion segmentation (2023)
10. Fourier amplitude augmentation domain generalization segmentation single source (2022)
11. fabric defect segmentation periodic texture reconstruction (2022)
12. wavelet downsampling semantic segmentation small objects (2023)
13. Hessian ridge filter features input convolutional network crack segmentation (2020)
14. periodic background suppression network repetitive pattern defect (2021)
15. Gabor filter bank prior crack detection deep network orientation (2022)
16. orientation score steerable equivariant network line crack vessel segmentation (2022)
17. frequency masking self-supervised pretraining dense prediction wavelet (2023)
18. wafer LCD defect segmentation periodic texture frequency domain (2025)
19. phase congruency crack detection deep learning illumination invariant (2020)

Snowball: `similar_papers` on SUPER + TexWDS; `get_citations` on XNet (ICCV 2023, 155 citing) and on HWD (520 citing).
`search_snippets` (3 attempts, all rate-limited): Fourier removal of busbars / fingers in EL; Hessian vector field method.
WebSearch (13 Nov): EL busbar / finger suppression 2025-2026; Seg-Aliasing repo; WPFormer repo; Hessian vector-field repo.
WebSearch (12 Nov, 9 queries) and WebFetch (24 pages): listed in the 12 Nov version; their results are merged below.

## Why this direction fits EL (S)
- Fingers form a dense periodic line pattern along one axis; busbars a sparse periodic pattern along the other. Both are sharp peaks in the 2D spectrum. Cracks, inactive areas, scuffs and splices are not periodic.
- **Aliasing argument (new, S, pitch unverified).** A stride-s layer can represent frequencies only up to 1/(2s) cycles per input pixel. Fingers alias at stride s whenever the finger pitch p (in px at 512) is below 2s. If p is about 4 to 6 px at 512 (a 156 mm cell with roughly 1.5 to 2 mm finger pitch; measure it on train cells), the fingers alias from the ResNet-34 stem (stride 4, after max-pool) onward: they fold into low-frequency moire. The moire depends on the exact pitch and on the source rescaling, so it is one plausible, testable cause of source dependence (BMRK = downscaled ELPV) and of E1 failure (new layouts). This is exactly what de-aliasing and wavelet-downsampling papers target.
- The weak "gridline" class (IoU 0.283, recall 0.33) is a local break in the finger periodicity. A periodicity residual targets it directly, and also cracks that cross fingers.
- A spectrum computed per image adapts to any finger pitch or busbar count with no extra labels, which matters for half-cut E1 cells.
- Limits: scuff streaks are not periodic, so periodic suppression will not remove them. Cracks parallel to fingers share their orientation; a notch removes only the periodic part, so always keep the raw image as channel 1.

## Selected papers
"score" = expected value for our metrics; "bench" = value for the benchmark suite.

| # | id | year | venue | code | mechanism | adaptation (short) | score | bench |
|---|---|---|---|---|---|---|---|---|
| 1 | arxiv:2403.09065 Seg-Aliasing (DAF + FreqMix) | 2024 | ICLR 2024 | github.com/Linwei-Chen/Seg-Aliasing (from the abstract; repo not opened) | DAF: FFT the feature map before each downsampling, zero the power above the equivalent Nyquist frequency (parameter free). FreqMix: learned channel x spatial weights on below- / above-Nyquist bands inside each encoder block. R: UPerNet-R50 Cityscapes 78.1 to 79.7 mIoU, boundary IoU 61.8 to 63.2; PASCAL VOC 74.3 to 76.1 | DAF before the ResNet-34 max-pool and the stride-2 convs of layer2/3/4 (not before conv1, so stride-2 skip features keep crack detail); FreqMix in layer1/layer2 blocks. Targets finger moire in deep features. Keeps all ImageNet weights | 66 | 30 |
| 2 | arxiv:2511.11015 SUPER | 2025 | arXiv | not released (paper says it will be) | Wavelet-domain decoder: DWT of decoder features, learned bounded suppression of LL/LH/HL/HH, IDWT replaces upsample + refine. R (12 Nov fetch): CrackVision12K, IoU on 0 to 2 px cracks 0.356 to 0.451 | Replace the U-Net++ upsample + conv at the top two decoder levels with Haar IDWT + suppression (Haar as fixed 2x2 convs, no install). Keep encoder and PF schedule | 66 | 40 |
| 3 | doi:10.1016/j.patcog.2023.109819 HWD | 2023 | Pattern Recognition (520 citations) | github.com/apple1986/HWD (12 Nov fetch: drop-in, built on smp) | Haar DWT then 1x1 conv as the downsampling op, so stride 2 keeps high-frequency detail in LH/HL/HH channels | Replace the ResNet-34 stem max-pool (and optionally the stride-2 entry of layer2). A 1 to 2 px crack is half lost at the first max-pool. Pairs with #1 (both attack stride-4 loss) | 64 | 25 |
| 4 | doi:10.1109/jphotov.2019.2895808 eCS | 2019 | IEEE J. Photovoltaics | zip on the FAU page (12 Nov fetch) | Reference EL crack algorithm: adapted vesselness for multicrystalline cells (abstract). A 12 Nov search summary said it also zeroes gridline Fourier frequencies; unverified, full text not read | Per image: 2D FFT, find finger and busbar peaks on each axis, notch them, IFFT. Feed the residual (raw minus de-gridded) as channel 2. Computed on the fly, so half-cut E1 cells get their own notch. Also a classical baseline row for the benchmark | 62 | 35 |
| 5 | arxiv:2603.14282 TexWDS / MPTCE | 2026 | arXiv | none | Feature-level periodic template: keep the dominant periodic frequencies of a feature map, reconstruct them, D = abs(F minus F_periodic), gradient attention A, output F + alpha A F. R: 4,531 wafer images, MPTCE alone recall 71.2 to 73.7, mAP50 72.7 to 76.2 | Insert after encoder layer1 (128 px) and layer2 (64 px), top-k spectral peaks per channel per image. Also expose D as an auxiliary map. Targets gridline recall and crack precision next to fingers | 60 | 30 |
| 6 | doi:10.1016/j.media.2024.103164 Hessian vector field DG | 2024 | Medical Image Analysis | github.com/MedICL-VU/Vector-Field-Transformer (WebSearch; MIDL 2022 version) | Replace intensity input by a Hessian-based vector field (scaled minor eigenvector) that is stable across imaging styles, plus a style augmentation that keeps vessel structure. R (WebSearch summary, not read): trained on fundus, tested on OCT-A | Bold bet for E1. Channels: raw + multi-scale dark-ridge Hessian eigenvector field (sigma 0.7 to 2.5 px). The vector field is contrast-invariant, aimed at E1 crack recall (70% of E1 crack pixels get p < 0.001) | 56 | 25 |
| 7 | doi:10.1109/cvpr42600.2020.00414 FDA | 2020 | CVPR 2020 (1,229 citations) | not checked | Swap the low-frequency Fourier amplitude of a source image with that of a target image; no training | Targets: pool half-cut multi cells (1,152) and CSIR pool cells (E1 is 101 CSIR). Small beta (0.005 to 0.02) so only illumination profile and contrast move; labels unchanged. Training-time augmentation for problem 3 | 58 | 40 |
| 8 | doi:10.1109/iccv51070.2023.01767 PASTA | 2023 | ICCV 2023 | not checked | Perturb the Fourier amplitude spectrum, high frequencies proportionally more than low; phase kept. R: GTAV-to-real segmentation and 4 other syn-to-real shifts, beats more complex DG methods and is complementary | Source-free version of #7: no target images needed. Keep phase, so crack positions are unchanged; cap the high-frequency amplitude jitter so 7% of cracks that are less than 2% darker are not erased. Aimed at E1 and BMRK / CFVS | 55 | 35 |
| 9 | arxiv:1711.03345 Frangi-Net | 2017 | arXiv | none | Multi-scale Frangi vesselness as a network with preset weights, then trained. R: 45 fundus images, F1 up to +17% after training | Dark-ridge variant (largest eigenvalue positive), sigma 0.7 to 2.5 px for the 4 px FWHM line. Extra input channel or parallel stem branch, trained jointly. Cheapest Hessian arm; run before #6 | 52 | 20 |
| 10 | doi:10.1088/2631-8695/aea73d NWG-DETR | 2026 | Engineering Research Express | none found | EL-specific: dark-contrast gating, cross-polarisation gating that attenuates repetitive grid-line artefacts, learnable wavelet pool / unpool. R: PVEL-AD mAP50 +3.77 over RT-DETR-r18 | Only EL paper found that targets grid lines inside a deep network. Take the learnable wavelet pool / unpool as a drop-in for max-pool + upsample in U-Net++ (overlaps #2/#3), and the grid-line gating as a skip-connection gate | 50 | 45 |
| 11 | arxiv:2408.12879 FreqFusion (doi:10.1109/tpami.2024.3449959) | 2024 | TPAMI (383 citations) | github.com/Linwei-Chen/FreqFusion | Decoder fusion with adaptive low-pass (smooth inside objects), offset resampling, adaptive high-pass (restore boundary detail) | Replace upsample + concat at each U-Net++ node. Low-pass helps blobby inactive; high-pass helps crack edges | 55 | 45 |
| 12 | doi:10.1109/bibm62325.2024.10822699 XNet v2 (XNet: doi:10.1109/iccv51070.2023.01928) | 2024 | BIBM 2024 | github.com/Yanfeng-Zhou/XNetv2 (12 Nov fetch) | Haar split into LF and HF images with random remix, three sub-networks (raw, LF, HF) with consistency and feature fusion. R (full supervision): CREMI Jaccard 75.47 to 79.80, GlaS 81.54 to 84.03 | Benchmark arm: supervised XNet v2 on 1-channel 512 px. For our model: random LF/HF remix as a label-safe augmentation on U-Net++ | 50 | 55 |
| 13 | doi:10.1109/tpami.2025.3592621 SFM | 2025 | TPAMI | github.com/Linwei-Chen/SFM (WebSearch, not opened) | Modulate high-frequency features to lower frequency by adaptive dense resampling before downsampling, demodulate with multi-scale adaptive upsampling. R: Mask2Former-Swin-T +1.5 mIoU, InternImage-T +1.4 on ADE20K | Resample densely around cracks and finger breaks before stride; heavier than #1. Try only if #1 shows a signal | 48 | 30 |
| 14 | doi:10.1609/aaai.v40i9.37713 DGK + Gabor LFS | 2026 | AAAI 2026 | not found | Anti-aliasing downsampling: dynamic Gaussian low-pass along edge normals only (keeps contours), then a learnable Gabor directional band-pass that removes residual aliasing peaks along a few dominant directions; phase-error energy metric | The directional sparsity it assumes fits EL exactly (fingers on one axis, busbars on the other). Use LFS before stride-2 layers; the phase-error metric is a cheap diagnostic of finger aliasing in our encoder | 50 | 25 |
| 15 | arxiv:2608.01714 STC-Net | 2026 | arXiv / MERCon 2026 | none | EL crack segmentation with fixed Sobel edge pyramid and FFT radial high-pass spectral pyramid injected into the decoder, plus topology refinement and an inactive-area power-loss proxy. R: PVEL-S unseen test 72.52 mIoU, 80.16 mDice; no ablation on test | Benchmark row (recent, EL, priors). Its high-pass is radial, not periodic, so it boosts fingers too; our version should use the notch residual of #4 | 42 | 60 |
| 16 | doi:10.1109/cvpr52734.2025.02222 WP-Former | 2025 | CVPR 2025 | github.com/yfhdm/WPFormer (WebSearch; mirror under iefengyan; not opened) | Query-based mask transformer for pixel-level surface defects; wavelet-enhanced cross-attention refines queries with high- and low-frequency features; prototype cross-attention for cluttered backgrounds. R: SOTA on ESDIs-SOD, CrackSeg9k, ZJU-Leaper (patterned fabric) | Benchmark arm: recent defect-segmentation method that covers both cracks and periodic fabric. Binary per class or 24-way mask queries; 1-channel stem | 42 | 60 |
| 17 | doi:10.1016/j.media.2024.103442 FFPN | 2025 | Medical Image Analysis | github.com/shigen-StoneRoot/FFPN (12 Nov fetch) | Pretrain on public unlabelled data with Frangi-filter-derived targets, then fine-tune. R: 1,510 unlabelled TOF-MRA scans, about +3% over semi- and self-supervised methods | Bold bet: pretrain the whole U-Net++ (decoder included) on the 11.9k pool to regress multi-scale dark-ridge maps plus the periodic residual of #4, then PF fine-tune so the pretraining survives | 46 | 20 |
| 18 | arxiv:2407.05848 WTConv (doi:10.1007/978-3-031-72949-2_21) | 2024 | ECCV 2024 (650 citations) | github.com/BGU-CS-VIL/WTConv | Convolution on wavelet subbands: large receptive field with log-growing parameters, more shape bias | WTConvNeXt-T as U-Net++ encoder, or WTConv2d in ResNet-34 layer3/4. The large field sees whole-cell layout, aimed at half-cut context and long scuffs on E1 | 45 | 40 |

## Minimum experiments
All: house recipe at 512 px, 20k steps, 5 seeds. Go / no-go on the module-grouped 5-fold CV (532 cells) where possible; confirm on clean-49 test and E1. A gain counts only if it beats the seed noise (crack IoU about 0.012 with 5 v 5 seeds).

0. Diagnostic first (CPU, 1 h, train cells only): measure finger and busbar pitch per source from the 2D spectrum, and compute the aliasing score of Seg-Aliasing (#1) on ResNet-34 layer1 to layer4 features of the house model for train cells. If fingers do not alias (pitch at least 8 px), lower #1, #3, #13, #14 by about 15 points.
1. Seg-Aliasing. Arm: house + DAF at max-pool and layer2/3/4 strides + FreqMix in layer1/2. Baseline: house and PF. Metric: crack IoU, relF1@2, per-source crack IoU (BMRK, CFVS), E1 relF1@2. Kill: crack IoU < +0.012 and E1 relF1@2 < +0.02. About 6 GPU-h, 1 day of code.
2. SUPER decoder. Arm: PF + SUPER at decoder levels 0 and 1. Baseline: PF. Metric: crack IoU, relF1@2, crack components >= 20 px found. Kill: crack IoU < +0.012 and relF1@2 < +0.01. About 8 GPU-h, 2 days of code.
3. HWD stem. Arm: HWD replaces stem max-pool. Baseline: house and PF. Metric: crack components found, recall at relP@2 >= 0.90. Kill: components found < +0.02 and crack IoU not up. About 6 GPU-h. If #1 and #3 both pass, test them together.
4. eCS-style notch channel. Arm: 2-channel [raw, per-image finger/busbar notch residual], channel-2 conv1 weights initialised to zero. Baseline: house. Metric: gridline IoU and recall, crack precision at fixed recall, E1 relF1@2. Kill: gridline IoU < +0.03 and crack IoU < +0.012 and E1 relF1@2 < +0.02. About 6 GPU-h.
5. MPTCE. Arm: PF + MPTCE after layer1 and layer2. Baseline: PF. Metric: gridline IoU, crack pixel precision. Kill: gridline < +0.03 and crack IoU < +0.012.
6. Hessian vector field. Arm: 3-channel [raw, minor-eigenvector field x, y at best sigma]. Baseline: house. Metric: E1 crack recall and relF1@2. Kill: E1 recall < +0.03. Run after #9 (cheaper Hessian arm).
7. FDA. Arm: house + FDA (beta 0.01, p 0.5), pool half-cut and CSIR cells as targets. Baseline: house and PF. Metric: E1 relF1@2, E1 inactive IoU; test crack IoU must not drop more than 0.01. Kill: E1 relF1@2 < +0.03.
8. PASTA. Arm: house + PASTA (amplitude jitter growing with frequency, phase kept). Same metrics and kill as #7. Run #7 and #8 side by side; they share the code.
9. Frangi-Net channel. Arm: 2-channel [raw, learnable dark-ridge Frangi, sigma 0.7 to 2.5]. Baseline: house. Metric: relF1@2, E1 crack recall. Kill: E1 recall < +0.03 and test relF1@2 < +0.01.
10. NWG-DETR parts. Arm: learnable wavelet pool in the stem + grid-line gate on the two highest skips. Baseline: PF. Kill: as #1. Only if #1 or #3 passes.
11. FreqFusion decoder. Arm vs PF. Metric: inactive IoU (CV), crack IoU. Kill: both below 1 SE.
12. XNet v2. Benchmark run (about 10 GPU-h). Separately, LF/HF remix augmentation on house; kill if CV gain below 1 SE.
13. SFM, 14. DGK + LFS: only after #1 shows a signal; same kill as #1.
15. STC-Net, 16. WP-Former: benchmark runs under the fixed protocol; no kill line, they are reference rows.
17. FFPN-style ridge pretraining: 40k steps on the 11.9k pool, PF fine-tune. Baseline: PF from ImageNet. Kill: crack IoU (CV) < +0.012 and E1 relF1@2 < +0.02. About 20 GPU-h.
18. WTConv: WTConvNeXt-T U-Net++ under PF vs ImageNet ConvNeXt-T under PF, 5 seeds, test + E1. Kill: E1 relF1@2 < +0.03.

## Prior overlap with BRIEF section 5 (honest)
- No row in section 5 tests anti-aliasing, wavelet down / up sampling, frequency-domain inputs, Hessian ridge inputs, Fourier amplitude augmentation, or periodic suppression.
- Closest rows: "intensity normalisation (fail)" and "per-panel BN adaptation (fail)" are inference-time normalisations, not training-time amplitude transfer (#7, #8). "2x input resolution n.d." is related to #1 to #3 only loosely: those change how detail survives downsampling at fixed resolution, at almost no compute. "MIM / DDeP n.d." does not close ridge-target pretraining (#17); section 5 lists "thin-structure-aware objectives" as open. The foundation-encoder ConvNeXt-T screen (DINOv3 vs ImageNet, 2 seeds, 4k steps, F51) does not test WTConv (#18).
- House augmentation is brightness / contrast only, so no spectral augmentation has been used.
- Within the team: STC-Net, SUPER, TexWDS and NWG-DETR also appear in D01 / D08 / D09 / D11 / D12. D12 reports HarmonySeg found no clear gain from vesselness input channels on 3D hepatic CT; that is evidence against #9 in another domain, not on EL.

## Recommended order (S)
1. Diagnostic 0 (finger pitch, aliasing score). It decides how much weight the stride-related arms deserve.
2. In parallel on cv02: #1 Seg-Aliasing, #3 HWD, #4 notch channel, #9 Frangi channel. Each under 1 day of code, about 6 GPU-h for 5 seeds.
3. #2 SUPER (best direct thin-crack evidence, 2 days of code).
4. #7 FDA and #8 PASTA together, scored on E1.
5. #5 MPTCE, #6 Hessian vector field, #17 ridge pretraining if 2 to 4 show a signal.
Benchmark suite from this direction: XNet v2, WP-Former, STC-Net, FreqFusion, WTConv U-Net, and eCS as the classical reference.

## Rejected (one line each)
- doi:10.1007/s44443-026-01379-x CrackLIFT (2026): learnable lifting wavelet + wavelet-target alignment loss, CrackSeg9k 82.10 mIoU; no code, and its mechanism overlaps #2 / #3. Second-tier backup to SUPER.
- doi:10.1007/s44443-026-00566-0 YOLO-PVELAD (2026, EL): DCT high-frequency FPN + 1D directional attention along the axes; detector, single seed (seed 42), +14.8 mAP50 claim. The axis-wise 1D attention is worth one line in D09.
- doi:10.3390/mi17080907 WASR (2026, EL): wavelet-aware downsampling encoder in YOLO11, +2.4 mAP50; detector, same mechanism as #3.
- doi:10.3233/atde260843 YOLOv10-WaC (2026, EL): Haar DWT in YOLOv10; detector, same mechanism as #3.
- doi:10.1016/j.ijfatigue.2025.109179 crack-preserving downsampler (2025): only matters when downscaling native-resolution images; useful for the 1200 px pool and for BMRK / ELPV re-export, not for the labelled 512 px set.
- doi:10.1109/cvpr52734.2025.01942 nnWNet (CVPR 2025, code yanfeng-zhou/nnWNet): transformer-conv W-Net inside nnU-Net with a call for unified benchmarking; not a frequency method (despite the XNet authors). Belongs in D25 / benchmark design.
- arxiv:2605.14566 SpectraFlow (2026): two-stage structural pretraining plus frequency-directional dynamic conv on ISIC / Kvasir / GlaS; too many parts, no code.
- doi:10.1109/tgrs.2024.3427370 SFFNet, doi:10.1109/tgrs.2025.3558472 AFENet, FSDENet: remote-sensing frequency fusion; no thin-structure evidence beyond #11.
- arxiv:2005.03337 WaveCNet: discards high-frequency subbands; on our data that discards cracks.
- arxiv:2002.12416 DCTNet: DCT input for compute; no thin-structure benefit at 512 px, 1 channel (WebSearch only).
- arxiv:2503.18783 FDConv, arxiv:2403.05369 FADC, arxiv:2203.12198 DFF, arxiv:2105.11120 FACT / arxiv:2108.08487 APR: generic; FACT/APR covered by #7 / #8, FADC by #1.
- arxiv:1904.13204 GaborNet, doi:10.1109/tgrs.2024.3365910 learnable Gabor kernels (seismic): Gabor stem; #14 uses Gabor where it matters (aliasing), cheaper to try there.
- arxiv:1911.08251 E(2)-steerable CNNs, doi:10.1007/s10851-024-01171-4 Riesz networks: rot90 / flip already covers D4; crack width is nearly constant here, so scale invariance buys little.
- doi:10.3390/sym17111829 WOT-AE, doi:10.2139/ssrn.7589368 texture-regularity SSL (fabric): unsupervised reconstruction for fabric; the anomaly-prior idea belongs to D07.
- arxiv:2402.14509 vesselness-stack input: merged into #9 as the same mechanism.

## Gaps
- Semantic Scholar was rate-limited for the whole session, so no `search_snippets` evidence: eCS's Fourier gridline step and its false-positive numbers remain unverified; the Hessian vector-field paper's numbers were not read (no abstract in the index, PMC download failed).
- Finger pitch per source at 512 px is not measured here (no data access in the literature phase). The aliasing argument behind #1, #3, #13, #14 depends on it; diagnostic 0 settles it in an hour.
- No paper found that suppresses EL finger / busbar periodicity inside a deep segmenter with a segmentation metric. NWG-DETR (detector) is the closest. A periodicity-residual or de-aliased U-Net++ on EL would be new, which makes #1 / #4 / #5 candidate thesis contributions.
- Not searched: golden-template or reference-cell subtraction with deep learning (PCB / wafer), learned notch filters, frequency-domain test-time adaptation (doi:10.1002/mp.17423 adaptive wavelet-VNet was seen but not assessed). Worth a short follow-up if #4 passes.
- Code not verified by opening the repository: Seg-Aliasing, SFM, WPFormer, Vector-Field-Transformer.
