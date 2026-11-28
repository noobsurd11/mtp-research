# D22 Detail-preserving and high-resolution architectures

Scout: D22 literature agent. First pass 12 Nov 2026 (cut short by MCP outage and web budget), resumed and completed 13 Nov 2026.
Tags: R = what a paper measured, E = what our files measured, S = my judgement.

## 0. Bottom line (S)
- The house model loses little to resolution on in-distribution crack: R5 (1024 px bilinear input, logits pooled to 512, house recipe) was n.d. on test crack IoU (-0.0046) and mIoU_rob at 4x compute; E1 crack recall rose 0.178 -> 0.204 (E, handbook 18 M5). 70% of crack IoU loss lies within 2 px of the label (BRIEF 2). So a detail-preserving decoder alone is unlikely to move strict test crack IoU by more than the 0.012 detection floor.
- Where this direction can pay: (a) making foundation ViTs usable for 1 to 2 px lines. E: frozen DINOv3 ViT-S/16 probe crack AP 0.147 at 512 px vs 0.212 at 1024 px (handbook 11 row 38), so token resolution is a real limit for ViTs, unlike for ResNet-34. This is the route to the E1 context gap. (b) gridline (IoU 0.283, recall 0.33) and other small classes. (c) heterogeneous ensemble members: the 5-seed ensemble is the only clear win so far; a structurally different detail-path model is the cheapest diversity.
- Ranked arms: (1) zero-shot feature upsamplers on frozen / LoRA DINOv3 (NAF, AnyUp; JAFAR trained label-free on the EL pool); (2) CNN detail path + frozen ViT context (ViTC-UNet style; DINOv3-PEFT dual-branch shows the same pattern on thin SAR roads); (3) anti-aliasing / frequency-aware down and up sampling in the house net (SFM, FreqFusion); (4) full-resolution skip or raw-image re-injection (DPN, BiRefNet, UNet 3+) as a 1-day test aimed at gridline; (5) ViT-Adapter, HRNet-OCR, HrSegNet, UNet 3+ as benchmark baselines.
- Code fact to check first (S, recalled from the segmentation_models_pytorch source, not verified on the server): the smp U-Net / U-Net++ decoders drop the stride-1 skip (`features = features[1:]`), so the last decoder block upsamples stride-2 features with no full-resolution input. The house net never sees full-resolution pixels after conv1 (7x7 stride 2). If confirmed, arm X3 below is a direct fix.

## 1. Queries run
Research MCP search_papers (limit 15, abstract 250), first pass:
1. "high resolution representation thin structure segmentation" (2020+)
2. "ViT-Adapter dense prediction" (2020+)
3. "dual super-resolution learning semantic segmentation" (2020+)
4. "PointRend point-based rendering segmentation refinement" (2020+)
5. "patch size vision transformer small objects segmentation pixel-level" (2023+)
6. "UNet 3+ full-scale skip connections" (2020+)
7. "HRNet object-contextual representations semantic segmentation" (2020+)
8. "feature upsampling vision foundation model dense prediction" (2024+)
9. "thin crack segmentation high-resolution detail preserving network" (2024+)
10. "detail branch context branch dual-branch segmentation thin structures" (2025+)
11. "vision transformer smaller patch size higher token resolution semantic segmentation accuracy" (2024+)
12. "super-resolution auxiliary task segmentation small thin objects feature affinity" (2022+)
13. "high-resolution feature preservation encoder thin curvilinear structure segmentation" (2025+)
14. "DINOv2 adapter fine-tuning retinal vessel segmentation thin structures" (2024+)

Resumed pass (13 Nov):
15. "high-resolution representation semantic segmentation thin structures" (2020+)
16. "patch size 8 vision transformer thin structure segmentation vessel" (2023+)
17. "FlexiViT patch size resizing dense prediction" (2022+)
18. "thin crack segmentation high-resolution branch transformer CNN hybrid" (2025+)
19. "feature upsampler foundation model thin structures fine-grained segmentation" (2025+)
20. "super-resolution auxiliary branch segmentation small targets" (2023+)
21. "space-to-depth lossless downsampling small object thin structure segmentation" (2022+)
22. "UNet 3+ full-scale skip connection deep supervision defect segmentation" (2024+)
23. "adapter plain vision transformer dense prediction spatial prior DINOv2 fine-tuning segmentation" (2025+)
24. "point-based refinement uncertain points thin structure segmentation" (2023+)

search_snippets: 3 attempts ("smaller patch size improves thin structures ViT", "ViT patch size 8 vs 16 thin vessels", "full resolution skip stride 1 decoder thin vessel"). All failed: Semantic Scholar rate-limited on both days. No snippet evidence.
Snowball: get_citations DSRL (25) and AnyUp (22, found NAF, UPLiFT, Upsample Anything, SPAR, PEPA); similar_papers DPN + BiRefNet (15).
get_paper on about 30 ids. Full text read: STC-Net (2608.01714, local), AnyUp (2510.12764), Docherty et al. (2508.21529).
WebSearch (code verification and 2026 sweep): LoftUp / AnyUp / JAFAR code; EL crack transformer 2025 and 2026; STC-Net; nnU-Net ResEnc; ViT patch size on thin vessels; full-res stem; ViT-CoMer code; FreqFusion code; AnyUp code; JAFAR code; Hybrid-Segmentor code; ViTC-UNet code; HrSegNet code; SFM code; NAF code.

## 2. Selected papers (18)
Score = value for OUR scores (task rubric). Bench = value for the benchmark suite or its design. Code column: "verified" means the paper or a web search names the repo; I did not open the repos.

| # | id | year | venue | code | mechanism | adaptation to our data | score | bench |
|---|---|---|---|---|---|---|---|---|
| 1 | arxiv:2511.18452 NAF | 2025 | CVPR 2026 | github.com/valeoai/NAF (paper abstract) | Zero-shot, encoder-agnostic upsampler: cross-scale neighbourhood attention with RoPE, guided only by the high-res image (a learned joint bilateral filter). R: DINOv3-B VOC 87.85 mIoU vs JAFAR 87.10; runs on DINOv3-7B where VFM-specific upsamplers run out of memory | Lift frozen DINOv3 ViT-L/16 (or 7B) tokens 32x32 -> 512x512 with the 1-ch EL image (x3) as guidance. Because the guidance is image-only, EL fingers / busbars / grain edges become the "bilateral" edges; check that cracks are not smoothed away (their contrast can be under 2%) | 60 | 45 |
| 2 | arxiv:2510.12764 AnyUp | 2025 | ICLR 2026 (oral) | github.com/wimmerth/anyup (paper), torch.hub | Encoder-agnostic window-attention upsampler, any layer, any resolution, feature-consistency regularised; keeps the input feature space (unlike LoftUp) | Second zero-shot arm next to NAF in the probe (X1). Same inputs. Zero training, so the decision costs hours | 58 | 45 |
| 3 | doi:10.52202/085713-3316 JAFAR (arXiv 2506.11136) | 2025 | NeurIPS | github.com/PaulCouairon/JAFAR (mirror page; DINOv3 checkpoints listed) | Attention upsampler: high-res queries from low-level image features, SFT-modulated low-res keys; trained at low ratios, works at high ratios | Retrain label-free on the 11.9k EL pool for the chosen DINOv3 encoder (its training command takes any timm backbone), so the upsampler learns EL texture. Arm: pool-trained JAFAR vs zero-shot NAF / AnyUp | 50 | 35 |
| 4 | arxiv:2605.16393 ViTC-UNet | 2026 | arXiv | not released ("url will be released after publication") | Frozen ViT (DINOv2 or SAM2) -> SAM-style two-way attention decoder with learnable tokens -> conditions an nnU-Net pixel decoder; built for domain-adaptive segmentation (MRI / CT) | This is the E1 arm: keep the house U-Net++ / ResNet-34 as the pixel path (1 to 2 px localisation), add cross-attention from its bottleneck and decoder stages to frozen DINOv3 ViT-L tokens of the same cell. Context for half-cut layout and scuff comes from the ViT. Implement ourselves (about 200 lines) | 55 | 35 |
| 5 | doi:10.3390/rs18070973 DINOv3-PEFT | 2026 | Remote Sensing | not found | Dual encoder: adapter-tuned frozen DINOv3 stream for long-range connectivity + conv stream for narrow elongated geometry, fused by a topological-geometric module. R: SAR roads (thin, speckle, weak contrast), F1 82.61, IoU 76.51 averaged over 4 resolutions, beats 6 baselines | Supporting evidence for #4 on a thin-line task with noise. Use only its fusion pattern: house ResNet-34 stream + DINOv3 adapter stream, fused at stride 4 and 8. Run as the same arm as #4 if #4's cross-attention is unstable | 40 | 20 |
| 6 | arxiv:2205.08534 ViT-Adapter | 2022 | ICLR 2023 | github.com/czczup/ViT-Adapter (paper) | Pretraining-free conv spatial-prior branch plus injector / extractor cross-attention turns a plain ViT into a 1/4 to 1/32 pyramid | DINOv3 ViT-B/16 or L/16 + ViT-Adapter -> U-Net++ decoder, plus a stride-1/2 conv stem skip; 1-ch replicated; PF-style schedule (frozen 1k steps, 0.1x lr, layer-wise lr decay). Standard ViT dense baseline for the benchmark | 50 | 75 |
| 7 | doi:10.1109/cvpr52733.2024.00525 ViT-CoMer (arXiv 2403.07392) | 2024 | CVPR | github.com/Traffic-X/ViT-CoMer (paper; repo not opened) | Bidirectional CNN-ViT fusion with a multi-receptive-field conv pyramid injected into a plain ViT. R: ADE20K 62.1 mIoU (ViT-CoMer-L) | Same slot as #6; run only whichever ports to the DINOv3 timm model with less work | 40 | 50 |
| 8 | doi:10.1109/tpami.2025.3592621 SFM (arXiv 2507.11893) | 2025 | TPAMI | github.com/Linwei-Chen/SFM (arXiv listing), Apache-2.0, mmseg 0.x / 1.x | Anti-aliasing for strided layers: adaptive resampling densely samples high-frequency areas before downsampling (lowers their frequency), multi-scale adaptive upsampling demodulates them back. R: +1.5 mIoU Mask2Former-Swin-T, +1.4 InternImage-T on ADE20K | A 1 to 2 px crack is pure high frequency and is aliased by conv1 (stride 2) and every maxpool / stride-2 block in ResNet-34. Insert ARS before conv1-stride and layer2 downsampling, MSAU in the last two U-Net++ decoder nodes. Port the two modules out of mmseg (no install) | 50 | 35 |
| 9 | doi:10.1109/tpami.2024.3449959 FreqFusion (arXiv 2408.12879) | 2024 | TPAMI | github.com/Linwei-Chen/FreqFusion (web search; not opened) | Decoder fusion with adaptive low-pass (inside regions), offset resampling, adaptive high-pass to restore boundary detail lost in downsampling | Replace nearest-upsample + concat in each U-Net++ decoder node with FreqFusion; the high-pass path is what matters for cracks and gridlines. Same author as #8; test #8 and #9 as one family | 45 | 35 |
| 10 | doi:10.1007/s12652-021-03422-3 DPN (arXiv 2009.12053) | 2021 | J. Ambient Intell. Humaniz. Comput. | not given | Detail-preserving blocks with no downsampling; full resolution throughout; about 120k parameters; DRIVE (20 train images), CHASE_DB1, HRF | DPN-style full-resolution branch (8 blocks, 16 to 32 ch, on the 1-ch input) concatenated into the house decoder's last block. Cheapest test of "keep 1 to 2 px lines"; about +10% compute, 1 day of code | 45 | 25 |
| 11 | doi:10.26599/air.2024.9150038 BiRefNet | 2024 | CAAI AIR | github.com/ZhengPeng7/BiRefNet (paper) | Localisation + reconstruction modules with bilateral reference: raw image patches re-injected at each decoder stage, gradient maps as auxiliary targets; built for thin high-res structures (DIS) | (a) Pixel-unshuffle the raw 512 px image into each decoder scale; gradient-map auxiliary loss restricted to a 3 px band around crack / gridline labels. (b) Bench: BiRefNet as a binary crack segmenter at 512 px | 50 | 55 |
| 12 | doi:10.1109/icassp40776.2020.9053405 UNet 3+ | 2020 | ICASSP | github.com/ZJUGiveLab/UNet-Version (paper) | Full-scale skips, full-scale deep supervision, classification-guided module (CGM) that suppresses false positives in images without the class | Full-scale skips that include a stride-1 stem; CGM as an image-level "inactive present" gate (42 train cells have inactive; may cut BMRK inactive false positives) | 40 | 50 |
| 13 | doi:10.1109/tpami.2020.2983686 HRNet + doi:10.1007/978-3-030-58539-6_11 OCR | 2020 | TPAMI / ECCV | github.com/HRNet, git.io/openseg (papers) | Parallel streams with a 1/4 stream kept throughout; OCR aggregates soft class-region descriptors back to each pixel | HRNet-W18/W32 (timm) under PF + stride-1 stem skip + OCR head. OCR fits inactive: 99% of inactive regions touch a crack, so a crack-region descriptor per cell is useful context. Standard benchmark baseline | 40 | 70 |
| 14 | doi:10.1016/j.autcon.2023.105112 HrSegNet (arXiv 2307.00270) | 2023 | Automation in Construction | github.com/CHDyshli/HrSegNet4CrackSegmentation (web; B16 / B32 / B48 weights) | High-resolution path kept throughout, low-res semantic guidance branch injected into it; crack-specific. R: CrackSeg9k 80.56 mIoU (B48), 182 FPS (B16) | Most-cited crack-specific HR network with code: run as a benchmark entry (1-ch replicated, 512 px, our protocol). As a score arm it is a smaller HRNet; expect n.d. on test crack IoU | 35 | 60 |
| 15 | doi:10.1007/978-3-032-37627-5_22 PEPA (arXiv 2606.23486) | 2026 | LNCS | not found | Post-encoder plug-in: target-conditioned snake upsampling for thin tortuous structures + target-adaptive differentiable thresholding; about 0.26M params; gains on 5 medical / industrial curvilinear sets, clDice gains larger than IoU gains (R) | Attach to the house decoder (or a frozen DINOv3 pipeline) for crack and gridline only; TADT replaces the fixed val-chosen crack bias with a per-image threshold (relevant to the 5 sources' contrast spread) | 45 | 30 |
| 16 | doi:10.1109/cvpr42600.2020.00383 DSRL (+ DS2F doi:10.1109/tpami.2023.3322735) | 2020 / 2023 | CVPR / TPAMI | github.com/wanglixilinx/DSRL (paper) | Segmentation super-resolution + single-image SR streams with feature affinity; DS2F shows the affinity is too weak for small-proportion targets and adds a target-focused proxy loss | Label-free SR auxiliary: reconstruct native-res crops (part of the pool is 1200 px) from decoder features; affinity weighted on a dilated crack + gridline band (DS2F idea). Unlabelled pool cells train the SR stream | 35 | 25 |
| 17 | doi:10.1109/cvpr42600.2020.00982 PointRend (+ RLCSN doi:10.1111/mice.13290) | 2020 / 2024 | CVPR / CACAIE | detectron2 projects/PointRend | Point head predicts labels at uncertain points from fine + coarse features with iterative subdivision; RLCSN adapts it to 0.15 mm cracks on UAV images (R) | Point head on stride-1/2 features, top-k uncertain points per image. Risk (S): the uncertain band is exactly the 1 to 2 px label jitter, so it may learn the jitter | 30 | 30 |
| 18 | arxiv:2608.01714 STC-Net | 2026 | MERCon 2026 (doi 10.1109/mercon71835.2026.11691399) | not found | EL crack net: fixed Sobel edge pyramid + FFT high-pass spectral pyramid injected into the decoder, boundary-topology refiner, crack-to-inactive power-loss proxy. R: PVEL-S (840 / 360) test mIoU 72.52, mDice 80.16 | Same task and modality: reimplement as a benchmark entry (spec in paper: base 32 ch, depths [2,2,4,2], 120 epochs). Its power-loss proxy informs the severity extension. Its edge / spectral priors are one cheap ablation on the house model | 30 | 60 |

## 3. Experiments (cheapest decisive first)
All on the module-grouped 5-fold CV over the 532 train+val cells (fold roots exist) unless stated; baseline = house PF; 1 seed per fold (5 runs). Primary: CV crack IoU, CV crack relF1@2, CV gridline IoU, CV inactive IoU. Secondary: F51 crack AP; E1 crack relF1@2 and E1 inactive IoU at the end only.

- **X0 Code check (0 GPU-h).** Confirm whether the smp U-Net++ decoder drops the stride-1 skip. Decides whether X3 is a fix or a duplicate.
- **X1 Upsampler probe (#1, #2, #3), about 6 GPU-h.** Frozen DINOv3 ViT-S/16 and ViT-L/16, 1x1 probe over 24 classes, as in the old P8 probe. Arms: bilinear 512, bilinear 1024 input (existing 0.212 AP for ViT-S), NAF 512, AnyUp 512, JAFAR trained on the pool. Metric: F51 + CV crack AP, gridline AP. Kill: no upsampler at 512 beats bilinear at 1024 input on crack AP. Pass -> X2.
- **X2 Foundation arms (#1/#4/#5/#6), about 60 GPU-h.** (a) DINOv3 ViT-L/16 + best upsampler + conv head + full-res stem, LoRA or PF; (b) house U-Net++ conditioned on frozen ViT-L tokens (#4, fusion as #5); (c) ViT-Adapter + U-Net++ decoder. Kill: E1 crack relF1@2 gain < +0.03 over PF and CV crack IoU drop > 0.012.
- **X3 Full-res path (#10, #11, #12), about 15 GPU-h.** One arm = DPN branch + raw-image re-injection (pixel-unshuffle) into the last two decoder nodes. Kill: CV gridline IoU < +0.03 and CV crack IoU n.d. Also score as a 6th ensemble member next to the 5 PF seeds (kill: ensemble crack IoU < +0.005).
- **X4 Anti-aliasing / frequency-aware sampling (#8, #9), about 10 GPU-h each.** SFM (ARS + MSAU) in the house net; FreqFusion in the decoder. Same kill as X3, plus CV crack components >= 20 px found must not drop.
- **X5 Plug-ins (#15, #17), about 10 GPU-h each.** PEPA on crack / gridline; PointRend head. Kill: CV crack relF1@2 n.d. and gridline IoU < +0.02.
- **X6 SR auxiliary (#16), about 15 GPU-h.** Label-free SR stream on the pool with band-weighted affinity. Kill: CV crack relF1@2 n.d. and E1 relF1@2 < +0.02.
- **Bench only (#6, #7, #11, #12, #13, #14, #18):** run under the benchmark protocol as named baselines; no extra tuning beyond the protocol.

## 4. Prior overlap with BRIEF section 5 (honest)
- R5 (2x input) tested "more pixels per crack" for ResNet-34 U-Net++ under the house optimiser: n.d. This partly covers DPN / full-res stem / HRNet / HrSegNet ideas for in-distribution crack IoU. Not covered: a true full-res skip at native receptive field, anti-aliased downsampling (SFM), gridline as a target, the PF optimiser, ensemble diversity.
- Foundation encoders were tested only as frozen linear probes with bilinear upsampling and one ConvNeXt-T screen; no ViT fine-tune, no adapter, no learned upsampler, no CNN + ViT fusion. All ViT arms here are open.
- MIM and DDeP were pretraining objectives, not a joint SR auxiliary at native resolution; DSRL / DS2F stay open but share the "reconstruction does not help" risk.
- No transformer, HRNet, OCR, UNet 3+, PointRend, SFM, FreqFusion or BiRefNet run exists.

## 5. Notable papers rejected or folded in
- arxiv:2608.02792 PixelUp (2026): third zero-shot upsampler; keep as an optional X1 arm only, NAF and AnyUp have stronger venues and code.
- arxiv:2601.17950 UPLiFT, arxiv:2511.16301 Upsample Anything: more upsamplers; Upsample Anything is per-image test-time optimisation (slow at 159k cells). Optional X1 arms.
- arxiv:2604.02252 SPAR (code github.com/naomikombol/SPAR): distils a fine-stride sliding-window ViT teacher into a single-pass student. Interesting because our 1024-px probe beat 512 px, but it targets open-vocabulary CLIP-type models; revisit only if X1 shows 1024-px features win and are too slow.
- arxiv:2508.21529 Docherty et al. "Maybe you don't need a U-Net": CNN upsampler of DINO features + XGBoost, separates hairline cracks in micrographs with 4 sparse-labelled images; but its own Fig. 7 shows a fully trained U-Net++ / ResNet-50 overtakes it with full labels (R). Supports using upsampled ViT features as context, not as a replacement for our CNN.
- doi:10.1016/j.autcon.2024.105960 Hybrid-Segmentor (code github.com/junegoo94/Hybrid-Segmentor, per paper): CNN + transformer dual path for fine cracks, CrackVision12K, IoU 0.631. Mechanism covered by #4 / #5 / #13; possible extra bench entry.
- arxiv:2504.14032 LoftUp: AnyUp Table 5 shows it does not keep the input feature space and smooths within objects.
- arxiv:2603.04892 LocAtViT: Gaussian locality bias in ViT attention; needs pretraining the ViT itself, so it cannot be applied to DINOv3 cheaply.
- doi:10.1109/cvpr52734.2025.02356 EoMT, arxiv:2603.25398 PMT: encoder-only mask transformers; left to D23.
- doi:10.1364/boe.522482 FRD-Net: same full-resolution mechanism as DPN.
- doi:10.1109/tits.2022.3228042 DDRNet, doi:10.1109/cvpr46437.2021.00959 STDC: real-time, high-res branch at 1/8 only.
- doi:10.1109/cvpr52688.2022.00137 UHR segmentation, doi:10.1109/cvpr52688.2022.00432 ISDNet: built for 4K to 6K images; our cells are 512 px.
- doi:10.1109/cvpr52688.2022.00437 Mask Transfiner, doi:10.1007/978-3-030-58610-2_29 SegFix: instance / boundary refinement; left to D26.
- doi:10.1111/mice.13052, doi:10.1111/mice.70118 (HR crack, implicit / Mamba): HR UAV images, no code found.
- doi:10.3390/a19030219 DCDRNet, doi:10.1016/j.rineng.2026.112287 Crack-UHRNet, doi:10.1016/j.rineng.2026.114095 HFCSNet, doi:10.3390/s26051667 CNN-ViT cascade upsampling: applied crack papers, no code found, no mechanism beyond HRNet / dual-branch.
- arxiv:2510.18091 APT, doi:10.1109/cvpr52729.2023.01393 FlexiViT: efficiency / any-patch-size, no thin-structure evidence; FlexiViT-style patch resizing is the tool for a patch-8 DINOv3 probe (gap below).
- doi:10.1109/iccvw69036.2025.00028 upsampler benchmark (iSegProbe): reference for comparing upsamplers.
- doi:10.1109/iccv51701.2025.02100 FDAM: ViT low-pass fix; left to D28.

## 6. Gaps
- No paper found that measures ViT patch size (8 vs 14 vs 16) on thin structures. One probe arm: DINOv3 ViT-S/16 with patch embedding resized to 8 (FlexiViT resize) vs DINO v1 ViT-S/8 vs 1024-px input.
- No paper evaluates feature upsamplers on 1 to 2 px lines; all upsampler evidence (R) is object-scale (VOC, ADE20K, COCO). Docherty et al. is the closest (hairline cracks, qualitative).
- search_snippets failed on both days (Semantic Scholar rate limit), so no passage-level evidence for patch size or full-res skips.
- Code unverified (not found): ViTC-UNet (not released), PEPA, STC-Net, DINOv3-PEFT, DPN. Repos named but not opened: NAF, AnyUp, JAFAR, SFM, FreqFusion, ViT-CoMer, HrSegNet, Hybrid-Segmentor.
- smp U-Net++ dropping the stride-1 skip: to be checked in the server code (X0).
- arxiv:2607.00687 LUMA (a fixed lightweight mask adapter to compare backbones fairly): relevant to benchmark design but get_paper returned 502; deserves a look by the benchmark-design scout.
- nnU-Net ResEnc (arXiv 2404.09556) left to D25.
