# Scout `general`: general semantic-segmentation architectures, 2015 to 2026

Date: 27 Nov 2026. Read only; nothing trained. Files: `papers.tsv` (104 rows, sorted by fit score), this report.

## 1. Bottom line

- The family is huge, but very little of it carries evidence on 1 to 2 px structures. The papers that do measure thin lines all point to the same place: **what happens to high frequencies at the strided downsampling and upsampling steps**, not to a different encoder family.
- Thin-crack evidence (width-stratified): FACS-net shows DeepLabV3+ and Hybrid-Segmentor lose most cracks of 2 px or less (0-2 px IoU 0.079 and 0.160), while a frequency-aware decoder with a full-resolution stem skip keeps them (0.356). Swapping only the decoder upsampling inside FACS-net then gives 0-2 px IoU 0.373 (CARAFE), 0.397 (FADE) and 0.451 (SUPER). These are the only controlled thin-crack comparisons of upsampling operators I found.
- Anti-aliased or polyphase downsampling (BlurPool, LPS, CAPS) is the second cheap lever. On micro surface defects, with the same U-Net, CAPS raised recall from 83.1 to 93.0 and mIoU from 69.8 to 78.2. Recall on unseen modules is our weak point.
- Encoder swaps (VMamba, MambaVision, SegMAN, UniRepLKNet, HRViT, HRFormer) have no thin-structure evidence. A controlled encoder-only benchmark (IGARSS 2026) found the same result for every strong encoder: boundary mIoU stays about 30 points below interior mIoU, and the drop under domain shift falls mostly on boundary pixels. Within-family scaling barely helps. I would not spend the A6000 time on another encoder swap before the decoder and downsampling arms.
- Real-time two-branch networks (PIDNet, DDRNet, BiSeNet/STDC, RTFormer) keep their detail branch at 1/8 resolution, which is coarser than the 1/4 top stream of HRNet-W18. As whole networks they are unlikely to beat HRNet-W18 on 1 to 2 px lines. Only their training-only detail or boundary heads are worth borrowing.
- The HRNet successor that drops in at the same cost is U-HRNet (more stages at low resolution, same interface). Evidence is natural-scene mIoU only, plus one low-tier crack paper.
- Caveat for E1: the FACS-net authors say their architecture alone did not generalise under domain shift; nnU-Net pretrained on many datasets did better. Architecture arms here mainly target **thin-line precision and in-distribution recall**. They are not a fix for unseen-module recall.

## 2. Queries run (47 search_papers, 4 citation snowballs, ~25 get_paper, 7 full texts)

Semantic Scholar was rate-limited for nearly the whole session. Results came mainly from OpenAlex, ScienceDirect, Scopus and arXiv. Both `search_snippets` attempts failed (S2 rate limit).

search_papers (year lower bound in brackets):
1. HRNet high-resolution representation semantic segmentation lightweight (2019)
2. real-time semantic segmentation detail branch boundary PIDNet DDRNet (2020)
3. dynamic upsampling operator dense prediction DySample CARAFE FADE SAPA (2019)
4. FADE SAPA feature upsampling semantic and detail task-agnostic (2022)
5. large kernel convolution dense prediction UniRepLKNet RepLKNet InternImage segmentation (2022)
6. vision Mamba state space model semantic segmentation backbone VMamba (2024)
7. Mamba crack segmentation thin structure (2024)
8. anti-aliasing downsampling CNN segmentation shift invariance blur pool (2019)
9. gated shape CNN boundary stream semantic segmentation thin objects (2019)
10. HRNet thin structure segmentation vessel crack high-resolution stream comparison U-Net (2021)
11. ConvNeXt V2 fully convolutional masked autoencoder segmentation (2022)
12. SegNeXt multi-scale convolutional attention strip convolution segmentation crack road (2023)
13. benchmark backbones crack segmentation comparison encoder ConvNeXt Swin HRNet ResNet (2022)
14. full-resolution residual network segmentation keep full resolution stream boundary (2016)
15. SegFix boundary refinement model-agnostic offset (2019)
16. HRFormer high-resolution transformer dense prediction (2021)
17. xLSTM vision backbone segmentation OR RWKV vision segmentation U-Net (2024)
18. Kolmogorov-Arnold network U-Net segmentation U-KAN (2024)
19. efficient vision backbone semantic segmentation ADE20K 2025 convolution attention hybrid (2025)
20. PointRend point-based rendering refinement segmentation thin crack (2020)
21. pixel shuffle sub-pixel convolution decoder segmentation fine structures (2018)
22. BiSeNet STDC detail guidance real-time segmentation (2018)
23. dilated convolution versus strided downsampling gridding thin structures segmentation output stride (2017)
24. HRNet retinal vessel segmentation high resolution (2020)
25. HRNet crack segmentation pavement concrete high-resolution network (2021)
26. DySample upsampling crack segmentation thin defect (2024)
27. controlled comparison CNN transformer Mamba segmentation fair benchmark small datasets (2024)
28. InternImage deformable convolution large-scale vision foundation model (2022)
29. EfficientViT multi-scale linear attention high-resolution dense prediction (2022)
30. Mamba retinal vessel segmentation thin vessels state space (2024)
31. Haar wavelet downsampling semantic segmentation preserve detail information loss (2021)
32. implicit feature alignment upsampling semantic segmentation high resolution output IFA (2021)
33. vision transformer semantic segmentation SETR Segmenter DPT plain ViT decoder (2020)
34. full-resolution branch crack detection lightweight network without downsampling measurement-grade precision (2022)
35. spectral bias thin structures segmentation high-frequency fine cracks network design (2023)
36. lightweight high-resolution network semantic segmentation transformer HRViT Dite-HRNet RTFormer comparison HRNet-W18 (2021)
37. HRNet medical image segmentation thin structure comparison nnU-Net high resolution branch benefit (2022)
38. shift-equivariant semantic segmentation polyphase sampling anti-aliasing improves segmentation (2020)
39. CARAFE content-aware reassembly of features upsampling (2019)
40. MambaVision LocalMamba Spatial-Mamba semantic segmentation ADE20K local scan (2024)
41. U-HRNet improving semantic representation of high resolution network dense prediction (2021)
42. pyramid scene parsing UPerNet DeepLabv3+ feature pyramid semantic segmentation encoder-decoder atrous (2016 to 2019)
43. large kernel convolution thin structure segmentation vessel crack receptive field (2023)
44. backbone architecture domain generalization semantic segmentation CNN versus transformer robustness distribution shift (2022)
45. BEiT EVA masked image modeling pretraining semantic segmentation ADE20K transfer (2021)
46. MetaFormer PoolFormer Visual Attention Network FastViT MaxViT backbone segmentation (2021)
47. OneFormer MaskFormer universal image segmentation transformer (2021)

Snowball (`get_citations`): HrSegNet (doi:10.1016/j.autcon.2023.105112, 30 citing papers checked), DySample (30), SFM (25), FACS-net (all 9). These turned up HACNet V2, FACS-net, SUPER, RIFT and FDAM.
search_snippets: 2 attempts ("HRNet outperforms U-Net on thin structures…", "dynamic upsampler improves thin structures…"). Both failed: S2 rate limit.
Full text read (sections named in `papers.tsv`): FACS-net, SUPER, DySample, RIFT, controlled SSM benchmark (arxiv:2604.18721), CAPS (doi:10.1109/tim.2023.3325514), SFM. Everything else is abstract only and marked so.

## 3. Counts

- Result lines viewed: about 620 across the 47 searches and 4 snowballs. Many were duplicates or off-family; I did not keep an exact unique count.
- Kept after title/abstract screening and dedupe: **104 papers** (`papers.tsv`).
- Checked against `ref/MASTER.tsv` by DOI, arXiv id and title: **90 NEW, 14 already in MASTER**: P038 SUPER, P191 RIFT, P218 SFM, P299 FreqFusion, P056 frequency aliasing, P446 HrSegNet, P392 Gated-SCNN, P528 rendering crack net, P174 ConvNeXt V2, P408 MixerCSeg, P354 SCSegamba, P285 ViT-CoMer, P193 ViT-Adapter, P462 SegFix.
- FACS-net is named in the D09 text ("abstract not retrievable"), but it has no MASTER row, so I marked it NEW.
- Fit scores: 4 (4 papers), 3 (8), 2 (21), 1 (49), 0 (22).

## 4. Top 10

Mapping key: **R-unseen** = recall on unseen modules; **HC** = half-cut layout; **TL** = thin-line precision/recall at 2 px tolerance; **INA** = rare inactive.

1. **doi:10.1016/j.autcon.2025.106719 FACS-net (Automation in Construction 2026), NEW, fit 4. Full text read.**
   - Evidence: on CrackVision12K, cracks were stratified by width. For cracks of 2 px or less, the models without frequency-aware decoding (DeepLabV3+, Hybrid-Segmentor, FCN) miss most cracks, while FACS-net keeps them. In the SUPER paper's table: 0-2 px IoU 0.356 (FACS) vs 0.160 (Hybrid-Segmentor) vs 0.079 (DeepLabV3+); CTS 0.872 vs 0.585 vs 0.101.
   - Two parts transfer to our U-Net++: (a) a stride-1 CNN head whose full-resolution features skip straight to the last decoder stage (D22 suspected that smp U-Net++ drops the stride-1 skip); (b) an FFT low/high-band split plus CBAM refinement at the last decoder stage.
   - Maps to: TL (recall of the faintest cracks).
   - Against: baselines are weak; 256 px, binary task; the authors report that it does not fix domain shift, so it does not address R-unseen.

2. **doi:10.1007/s11263-024-02191-8 FADE (IJCV 2024), NEW, fit 4. Abstract, plus results read in DySample and SUPER.**
   - Evidence: a guided upsampler (kernels built from the encoder skip plus a detail gate). ADE20K SegFormer-B1 boundary IoU 27.80 → 31.68. As the FACS-net upsampler, 0-2 px crack IoU 0.356 → 0.397.
   - This is a config-level swap of the U-Net++ upsampling steps. Official code exists.
   - Maps to: TL.
   - Against: the thesis saw no U-Net vs U-Net++ decoder effect, so expect a small change; screen with 2 seeds first.

3. **doi:10.1109/tim.2023.3325514 CAPS (IEEE TIM 2023), NEW, fit 4. Full text read.**
   - Evidence: polyphase down/upsampling with attention over all polyphase components replaces the U-Net sampling layers. On micro surface defects (MSD): mIoU 69.8 → 78.2, recall 83.1 → 93.0. That beats BlurPool (73.2), LPS (72.0) and APS (68.4) in the same U-Net. The output barely changes under 1-px shifts (mvIoU 0.0062 → 0.0010).
   - Maps to: TL and recall. Also D4 TTA: a shift-consistent net makes the TTA vote less noisy.
   - Against: tested on a small U-Net trained from scratch, not a pretrained HRNet; replacing strided convs disturbs pretrained weights, which the PF schedule protects. Cost: new backbone layers.

4. **arxiv:2511.11015 SUPER (arXiv 2025), already P038 (RUN_AFTER_GATE), fit 4. Full text read.**
   - I confirm the MASTER numbers and add the head-to-head result: inside FACS-net, 0-2 px IoU is SUPER 0.451 vs FADE 0.397 vs CARAFE 0.373, with decoder MACs down 66% vs FACS-net.
   - It is a decoder block for U-Net variants (wavelet split of the skip, bounded suppression, exact-reconstruction fallback).
   - Maps to: TL.
   - Against: no code (MASTER also notes this); one dataset, no seeds. Run FADE first (code exists); run SUPER if FADE shows a signal.

5. **arxiv:1904.11486 BlurPool (ICML 2019), NEW, fit 3. Abstract; effect measured in the CAPS full text.**
   - Evidence: the cheapest anti-aliasing arm. In CAPS's controlled U-Net, mIoU 69.8 → 73.2. Antialiased ResNet weights are public, so a U-Net++ R34 (PF) variant is close to config-only. For HRNet, the blur must go into the strided convs.
   - Maps to: TL.
   - Against: recall fell slightly (83.1 → 80.2) and SFM argues blur removes detail. Treat it as the control for CAPS/SFM, not the main arm.

6. **doi:10.52202/068431-1519 SAPA (NeurIPS 2022), NEW, fit 3. Abstract and DySample table.**
   - Evidence: second guided upsampler (boundary IoU 30.96 vs 27.80 bilinear on ADE20K). Run it in the same screen as FADE.
   - Maps to: TL.
   - Against: same as FADE.

7. **doi:10.1016/j.eswa.2025.128144 HACNet V2 (ESWA 2025), NEW, fit 3. Abstract only.**
   - Evidence: a dual-branch crack net with an explicit full-resolution branch next to a high-resolution one; 0.52 M params; best mIoU/F1 on BCL and CHCrack5K per the abstract.
   - Use it as a structurally different, cheap ensemble member (5 folds × 5 seeds is affordable), or as a design template for a full-resolution side branch beside HRNet-W18.
   - Maps to: TL, ensemble diversity.
   - Against: abstract only; a model this small trained from scratch may lack context for INA and mIoU-R13.

8. **arxiv:2210.07140 U-HRNet (arXiv 2022), NEW, fit 3. Abstract only.**
   - Evidence: a direct replacement for the HRNet-W18 encoder with the same interface. It keeps the high-resolution stream and moves compute to extra low-resolution stages at "almost no" extra cost, with gains on several segmentation sets under identical training. Crack-UHRNet (doi:10.1016/j.rineng.2026.112287) applies it to concrete cracks.
   - Of everything found, this is the encoder most likely to "beat HRNet-W18 at similar cost" while keeping its 1/4 stream.
   - Maps to: R-unseen, HC (more semantic context), INA.
   - Against: no thin-structure numbers; weights are in PaddleSeg and need porting.

9. **arxiv:2604.18721 Controlled benchmark of visual SSM backbones (IGARSS 2026), NEW, fit 3 as decision evidence. Full text read.**
   - Evidence: only the encoder varies, under one U-Net decoder. VMamba/MambaVision beat the CNN reference on LoveDA (55 vs 43 mIoU). But for every strong encoder, boundary mIoU (~28-29) stays ~30 points below interior, and cross-domain loss concentrates on boundary pixels. Scaling within a family adds under 1 mIoU.
   - Supports ranking decoder/downsampling arms above encoder swaps for R-unseen and TL.
   - Against: the CNN reference was a DeepLabv3 encoder, not HRNet; the task is regions, not lines.

10. **doi:10.1109/tpami.2025.3592621 SFM (TPAMI 2025), already P218 (PARKED). Fit 3; I suggest moving it up. Full text sections read.**
    - Evidence: adaptive resampling before downsampling plus multi-scale adaptive upsampling. Cityscapes UPerNet-R50 78.1 → 79.5 vs BlurPool 78.8. +3.3 mIoU on PSPNet when both halves are used; the downsampling half alone costs -0.5.
    - With FACS/SUPER/CAPS now showing that detail lost at sampling steps is what hurts thin cracks, SFM belongs in the same anti-aliasing arm as CAPS and BlurPool, not in PARKED.
    - Maps to: TL.
    - Against: invasive (every downsampling layer); mIoU-only evidence.

Next in line (fit 2): PIDNet / STDC detail-guidance heads (borrow the training-only boundary/detail head, not the network); RIFT (P191, already in MASTER; best cross-dataset transfer among light crack nets, but its own ablation says the directional part is small); SegMAN and MambaVision (encoder swaps without thin-line evidence); MatchDown (only matters if any head is supervised below full resolution).

## 5. Suggested minimal screen (2 seeds, protocol M = 0.010 on crack relF1@2)

On the C2 recipe (HRNet-W18 + U-Net++ + PF + SWAD + D4), in order of cost:
- (a) FADE and SAPA upsamplers in the U-Net++ decoder (config-only).
- (b) A stride-1 full-resolution stem skip into the last decoder block, with and without an FPCM/FFT high-band refinement (FACS-net's two parts).
- (c) BlurPool vs CAPS in the HRNet stem's strided convs; SFM only if (c) shows a signal.
- (d) U-HRNet in place of HRNet-W18.

Guards matter here: guided upsamplers and high-pass modules can widen cracks or add false lines, so check crack width (0.85 to 1.15) and false crack pixels on crack-free cells before reading relF1.

## 6. NOT_FOUND / not returned by the tools

I searched these by name in queries 5, 33, 36, 42, 45, 46 and 47; the tools did not return the original paper, so I did not cite them:
- Swin Transformer
- PSPNet, UPerNet, FPN, DeepLabv3+ (original papers; DeepLab was already tested in the thesis)
- RepLKNet
- LocalMamba
- Visual Attention Network (VAN)
- PoolFormer / MetaFormer
- MaxViT, CMT
- BEiT
- BiSeNet V1/V2 (originals)
- Dite-HRNet
- PP-LiteSeg, SeaFormer, TopFormer
- ESPCN pixel shuffle

Classic Segmenter, Mask2Former, SegNeXt, HRNet (TPAMI) and nnU-Net are already in MASTER from D22/D23.

"What Does the Encoder Actually Decide?" (arxiv:2609.13232) was found, but its indexed abstract still contains template placeholders ([N], [BestEncoder]). I list it with fit 0 and use none of its claims.
