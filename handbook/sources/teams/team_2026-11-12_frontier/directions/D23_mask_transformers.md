# D23 Transformer segmenters and mask classification

Scout: D23 literature agent. First pass 12 Nov 2026 (MCP down most of the session), resumed and completed 13 Nov 2026 with snowballing.
R = what a paper measured, E = what our files measured (BRIEF), S = my judgement.

## 0. Tool status
- 12 Nov: 4 MCP searches, then Cloudflare 502 on every MCP call for 14 min; 6 WebSearch queries; 19 WebFetch reads of arXiv pages and GitHub READMEs.
- 13 Nov: MCP back (OpenAlex and arXiv; Semantic Scholar rate-limited all session, so `search_snippets` failed 3 times). fetch_fulltext timed out twice on arXiv:2607.00223; arXiv HTML read with WebFetch instead. 3 WebSearch queries.
- Every id below was returned by a Research MCP call or read on a fetched arXiv / GitHub page. Where a code URL is only stated in an abstract and was not opened, it is marked "stated".

## 1. Queries run
| # | Day | Tool | Query | Useful hits |
|---|---|---|---|---|
| 1 | 12 | search_papers 2024+ | encoder-only mask transformer segmentation ViT | EoMT, VidEoMT |
| 2 | 12 | search_papers 2020+ | Mask2Former small dataset defect segmentation | Hijjawi EL benchmark, Defect-Mask2Former |
| 3 | 12 | search_papers 2021+ | electroluminescence solar cell segmentation transformer SegFormer | EL classification only |
| 4 | 12 | search_papers 2022+ | crack segmentation transformer thin structures SegFormer | DSCformer, Hybrid-Segmentor |
| 5-10 | 12 | WebSearch | EoMT repo; DINOv3 EoMT small data; M2F vs per-pixel long tail; SegFormer vs U-Net small medical; M2F thin structure limits; PMT | GOOSE-M2F, GP-VM x SMA, PMT |
| 11 | 13 | search_papers 2020+ | Mask2Former masked-attention universal segmentation | M2F, OneFormer, MP-Former, Mask DINO, Mask2Anomaly, MR-Former |
| 12 | 13 | search_papers 2024+ | encoder-only mask transformer EoMT ViT segmentation | PMT, Token-space mask prediction, LUMA, EoSeg ("Does your ViT still need U-Net") |
| 13 | 13 | search_papers 2021+ | SegFormer defect segmentation small dataset industrial | DSCformer, PV thermal transformer, SegFormer corrosion |
| 14 | 13 | search_papers 2021+ | transformer solar cell electroluminescence defect segmentation | PDeT, Hijjawi, SEiPV-Net, EL classification papers |
| 15 | 13 | search_papers 2022+ | SegNeXt convolutional attention semantic segmentation | SegNeXt (NeurIPS 2022 confirmed), SegMAN |
| 16 | 13 | search_papers 2021+ | per-pixel classification is not all you need mask classification | MaskFormer, Segmenter, prototype view |
| 17 | 13 | get_citations | EoMT (56 citing) | EoSeg, LUMA, UDA in VFM era, PMT |
| 18 | 13 | search_papers 2022+ | mask transformer vessel segmentation thin curvilinear query | vessel / curvilinear nets (D11 / D12 territory) |
| 19 | 13 | search_papers 2022+ | mask classification long-tailed semantic segmentation rare classes queries | Frequency-based matcher (LTSS), Devil is in the Queries |
| 20 | 13 | search_papers 2023+ | Mask2Former few training images data-efficient fine-tuning | Defect-Mask2Former, nothing on small-data M2F |
| 21 | 13 | search_papers 2022+ | high-resolution mask refinement mask transformer fine details | Mask Transfiner, SAMRefiner |
| 22 | 13 | search_papers 2025+ | mask transformer semantic segmentation improvement | iFAN, FFMask DINO |
| 23 | 13 | search_papers 2024+ | ViT versus U-Net small medical dataset benchmark | nnU-Net revisited, endoscopy CNN vs transformer |
| 24 | 13 | search_papers 2024+ | DINOv2 backbone segmentation fine-tuning industrial defect few hundred images | only anomaly detection |
| 25 | 13 | search_papers 2023+ | OmniCrack30k crack segmentation benchmark nnU-Net transformer | none useful |
| 26 | 13 | search_papers 2023+ | Mask2Former crack segmentation | Enhanced M2F bridge crack (TITS 2025), M2F pavement crack (Electronics 2025) |
| 27 | 13 | search_papers 2023+ | SegFormer crack segmentation thin cracks comparison | crack hybrids (D09 territory) |
| 28 | 13 | similar_papers | EoMT + EoSeg | SegViT v2, TransUNet line |
| 29 | 13 | search_papers 2024+ | feature upsampling VFM LoftUp JAFAR FeatUp | LoftUp, JAFAR, NAF, Upsample Anything, "Maybe you don't need a U-Net" |
| 30 | 13 | search_papers 2025+ | Primus transformer medical nnU-Net | Primus, MedDINOv3 (D24 / D25 territory) |
| 31 | 13 | search_papers 2023+ | photovoltaic EL Mask2Former OR SegFormer | EL SegFormer + U-Net++ ensemble (INFINITYS 2026), MultiSolSegment |
| 32 | 13 | search_papers 2025+ | SegFormer small training set data efficiency | nothing decisive |
| 33 | 13 | search_papers 2025+ | Cracks in the Foundation civil infrastructure VFM | CIF dataset (EoMT DINOv2 / v3 on cracks) |
| 34-36 | 13 | WebSearch | EoMT DINOv3 small data; fracture-informed EL ensemble; DINOv2/v3 Mask2Former crack | EoMT-DINOv3 in HF transformers; CIF evidence |
| 37-39 | 13 | search_snippets | M2F small objects; EoMT APs gap | all failed (S2 rate limit) |
| fetch | 13 | WebFetch | arXiv html 2607.00223 (EoSeg), abs 2607.00687 (LUMA), abs 2406.03917, abs + html 2605.18413 (CIF) | |

## 2. The core question for our data (S)
Mask classification (MaskFormer family) predicts N binary masks plus one class per mask; semantic output = sum over queries of class prob x mask prob.
1. **Resolution.** Mask2Former / Mask DINO predict masks on 1/4-resolution pixel features; EoMT / EoSeg predict on ViT patch tokens (1/14 to 1/16) and upsample. A 1.75 px crack at 512 px input is 0.44 px wide at 1/4 and about 0.11 px at 1/16. Strict crack IoU will drop unless input is 1024+ or a full-resolution path is added (feature upsampler like LoftUp, or a conv refinement head). Two crack papers had to add high-resolution conv modules to Mask2Former to keep thin cracks (TITS 2025, Electronics 2025). On a 150k-tile civil-infrastructure set, EoMT with DINOv2 / DINOv3 was the best overall instance segmenter but crack mask mAP was 4.7 to 5.0 (R, arXiv:2605.18413).
2. **Point-sampled mask loss.** Mask2Former trains masks on about 12.5k importance-sampled points. Crack is 0.19% of pixels. Add a dense per-pixel CE + Dice head (GOOSE-M2F did; we already use CE + Dice) on the final semantic map.
3. **Where it should win.** Blobby, rare, region-like classes where a global per-image decision matters: inactive (42 train cells, one or two regions per cell, bounded by cracks / busbars), splice (never predicted), material, edge_dark, corrosion. And ViT-L with DINOv2 / DINOv3 pretraining is the untested route to E1 robustness (BRIEF tested only ViT-S / ConvNeXt-T probes and one ConvNeXt-T fine-tune). EoSeg (R) shows an encoder-only DINOv2-L query model trained on 18 to 70 volumes (Synapse, ACDC) and on GlaS / MoNuSeg with 5-fold CV beating TransUNet / Swin-UNet; it did not compare to nnU-Net, so this is weak evidence against a tuned U-Net.
4. **Ensembling.** The only clear win so far is the 5-seed house ensemble. A transformer model makes different errors from a U-Net++; the one EL paper that fused SegFormer-B0 with U-Net++ (soft fusion 0.55 / 0.45) reports gains over its best single branch by paired bootstrap (R, internal 5-class set). Heterogeneous ensembles are untested here.

Plan this direction supports: transformer mask classifiers as (a) inactive / other-class / E1 models, (b) heterogeneous ensemble members with the house U-Net++, (c) mandatory benchmark baselines. Not as a replacement crack model at 512 px.

## 3. Selected papers
| # | id | year | venue | code | mechanism | adaptation to our data | score | bench |
|---|---|---|---|---|---|---|---|---|
| 1 | doi:10.1109/cvpr52734.2025.02356 (EoMT, arXiv 2503.19108) | 2025 | CVPR | github.com/tue-mps/eomt (verified; DINOv2 + DINOv3 configs; also `eomt_dinov3` in HF transformers) | Plain ViT; learnable queries joined to patch tokens for the last 4 blocks; class + mask from those tokens; mask annealing drops masked attention at inference. R: ADE20K 58.4 mIoU ViT-L DINOv2 at 512; DINOv3 EoMT-L 59.5 (repo); gap to ViT-Adapter + M2F shrinks with scale | ViT-L DINOv2-reg (DINOv3 needs user OK, gated) from the ADE20K semantic checkpoint, `load_ckpt_class_head False`; grey replicated to 3 ch; 1024 px input; full-res head (LoftUp-style or 2-layer conv on upsampled mask logits + raw image); dense CE + Dice on crack / inactive on the final semantic map; layer-wise lr decay 0.8 (PF analogue); 24 classes, 2 queries per class | 62 | 90 |
| 2 | arxiv:2607.00223 (EoSeg) | 2026 | arXiv | github.com/Retinal-Research/EoSeg (stated) | Encoder-only query model for small medical sets: queries in last 3 DINOv2-L blocks, a gated fusion of per-block predictions, 2 queries per class. R: Synapse (18 train vols) 85.50 DSC vs TransUNet 77.48; ablation linear head 82.40 to query masks 83.70 to multi-level 84.34 to fusion 84.78 to 2 queries/class 85.50; DINOv2-L beat DINOv3-L (81.86 vs 81.60) | Closest small-data recipe for #1: copy its 2-queries-per-class and block-fusion gate; AdamW 5e-4, layer decay, 200 epochs ~ 12k steps at batch 8 on 478 cells; same full-res head and 1024 input; judge on inactive and E1. S: baselines are weak (no nnU-Net), so treat gains as unproven against our tuned U-Net++ | 58 | 55 |
| 3 | doi:10.1109/cvpr52688.2022.00135 (Mask2Former, arXiv 2112.01527) | 2022 | CVPR | project page bowenc0221.github.io/mask2former links the code (repo URL not opened) | Masked cross-attention restricted to each query's predicted region; multi-scale decoder; point-sampled mask loss. R: SOTA ADE20K at the time; authors note weak small objects | Semantic mode, Swin-B or R50 from ADE20K weights, 512 and 1024 px; the reference mask classifier for the benchmark; aim at inactive and splice / material / edge_dark; raise `num_points` and add the dense aux head (#4) | 50 | 95 |
| 4 | arxiv:2606.15937 (GOOSE-M2F) | 2026 | arXiv (ICRA 2026 challenge, 3rd place) | github.com/Aditya-Lingam-9000/GOOSE-M2F (verified 12 Nov) | Auxiliary per-pixel CE head next to the M2F loss for rare classes under 50 px, 200 queries, distribution-balanced loss, rare-class copy-paste, EMA. R: aux head +3.4 mIoU in their ablation (table has inconsistencies) | Add the dense head to any mask classifier we run, at full res, with our CE + Dice on crack and inactive; copy-paste only inactive regions with their bounding cracks (crack copy-paste alone was n.d.) | 55 | 35 |
| 5 | doi:10.1109/infinitys69204.2026.11666283 (EL SegFormer + U-Net++ ensemble) | 2026 | INFINITYS (IEEE conf.) | none seen | SegFormer-B0 with an edge-guided residual-logit refiner (probability, uncertainty, Sobel cues) soft-fused with a compact U-Net++ (0.55 / 0.45). R: 5-class EL, mIoU 0.840, defect mIoU 0.779 internal test; ensemble beats refiner alone by paired bootstrap. Dataset unverified | The only EL evidence for a transformer + U-Net++ heterogeneous ensemble. Ours: house 5-seed U-Net++ ensemble + a SegFormer-B2 / EoMT member, fusion weight chosen on val per class (crack, inactive, rest) | 60 | 50 |
| 6 | arxiv:2504.14032 (LoftUp) | 2025 | ICCV | github.com/andrehuang/loftup (stated) | Coordinate-based cross-attention upsampler that takes the full-res image + low-res VFM features; trained with mask-based pseudo-GT features. R: beats prior upsamplers on dense tasks. Related: JAFAR arXiv:2506.11136 (NeurIPS 2025); arXiv:2508.21529 shows upsampled VFM features separate hairline cracks in battery micrographs | The full-res path for #1 / #2 / #8: upsample DINOv2 tokens to 512 using the EL image as guide, then dot with query embeddings. Pretrained upsampler is RGB natural-image; fine-tune it end to end on our cells | 48 | 25 |
| 7 | arxiv:2406.03917 (Frequency-based matcher, TMM 2024) | 2024 | IEEE TMM | promised, unverified | Long-tailed semantic segmentation benchmark + one-to-many matching where the number of queries matched to a class is set from class frequency, to stop rare-class oversuppression; dual-metric evaluation | For mask classifiers on our 24 classes: allow inactive, splice, corrosion, material more matched queries; S: in semantic mode each class is one target per image, so one-to-many gives rare classes several gradient paths. Also their dual metric (frequent vs rare) fits our mIoU_rob vs all-class reporting | 45 | 50 |
| 8 | arxiv:2304.00212 (Devil is in the Queries / MaxQuery) | 2023 | CVPR | not seen | Queries as feature-level cluster centres; pixel-to-query similarity gives an OOD map (MaxQuery); a query-distribution loss separates targets from background. R: small tumour segmentation +5.27 DSC over nnU-Net; OOD AUROC +7.39 | E1 problem: scuff streaks and half-cut layouts are OOD for our training set. Use the MaxQuery map to flag pixels far from all queries and suppress crack calls there (decoy control), or report it as an abstention score in the benchmark | 45 | 40 |
| 9 | arxiv:2603.25398 (PMT) | 2026 | arXiv (CVPR 2026 workshop per README) | github.com/tue-mps/pmt (verified 12 Nov) | Plain Mask Decoder on a frozen VFM, mimicking EoMT's last blocks. R: matches frozen-encoder SOTA, up to 3x faster | Frozen DINOv3 / DINOv2 ViT-L + PMD + full-res head, 1024 px, E1-oriented (frozen encoder cannot overfit 5 sources). Closest to the failed probes, so scored lowest of the VFM arms | 40 | 45 |
| 10 | doi:10.52202/068431-0084 (SegNeXt, arXiv 2209.08575) | 2022 | NeurIPS | github.com/Visual-Attention-Network/SegNeXt | Convolutional attention from multi-branch strip convolutions (k x 1, 1 x k); ham decoder. R: +2.0 mIoU ADE20K at equal or lower compute | Strip kernels match long axis-aligned gridlines (gridline recall 0.33) and long cracks; MSCAN-B, 1-ch replicated, plus a full-res skip; cheap enough for 5-fold CV | 52 | 70 |
| 11 | arxiv:2105.15203 (SegFormer) | 2021 | NeurIPS | github.com/NVlabs/SegFormer | Hierarchical MiT encoder without positional encoding + all-MLP decoder (1/4 output) | MiT-B2 / B5 ADE20K weights, 1024 px or full-res skip; main heterogeneous ensemble member (see #5); D01 already lists the EL SegFormer paper | 45 | 90 |
| 12 | arxiv:2205.08534 (ViT-Adapter) | 2023 | ICLR | github.com/czczup/ViT-Adapter | Conv spatial-prior branch injected into a plain ViT for multi-scale features | Strong counterpart to EoMT at ViT-B (where EoMT loses most); ViT-B DINOv2 + adapter + M2F or UPerNet at 1024; conv branch gives the 1/4 path thin cracks need | 45 | 60 |
| 13 | doi:10.1109/tits.2025.3578810 (Enhanced M2F bridge crack) | 2025 | IEEE T-ITS | none seen | M2F + multi-scale RepBlock fusion + high-res wavelet conv (WTConv + DEConv) branch. R: bridge crack mIoU 86.33, each module adds; see also doi:10.3390/electronics14142834 (M2F + local perception + aux conv, +3.2 mIoU on pavement cracks) | Confirms plain M2F loses thin cracks and needs a high-res conv path; in our M2F arm use a stride-2 or stride-1 conv branch from the raw EL image into the pixel decoder | 40 | 25 |
| 14 | doi:10.1109/cvpr52729.2023.01733 (MP-Former) | 2023 | CVPR | github.com/IDEA-Research/MP-Former (instance / panoptic scripts) | Noised GT masks fed into masked attention; model reconstructs them; fixes layer-to-layer mask inconsistency. R: +1.6 mIoU Cityscapes R50; M2F accuracy in half the epochs on ADE20K | Few-data convergence add-on for M2F; noise model = our measured label jitter (1 to 2 px shifts, width changes per source) | 38 | 30 |
| 15 | doi:10.1109/cvpr52729.2023.00297 (Mask DINO) | 2023 | CVPR | github.com/IDEACVR/MaskDINO | DETR-style denoising queries + masks from high-res pixel embedding; unified det / seg. R: 60.8 mIoU ADE20K | Benchmark entry; query denoising may help 478-image convergence; same 1/4 limit for crack | 30 | 55 |
| 16 | arxiv:2605.18413 (Cracks in the Foundation, CIF) | 2026 | arXiv | data: huggingface.co/datasets/ibm-research/cif-dataset | 150k-tile infrastructure defect set; EoMT DINOv2 / DINOv3, Mask DINO, YOLO, RF-DETR under one protocol at 1024 tiles. R: EoMT best overall mask mAP 24.2, but crack mask mAP 4.7 (DINOv3) / 5.0 (DINOv2) vs YOLOv11-xl 8.6 | Evidence that VFM mask classifiers do not solve thin-crack masks by themselves; keeps our crack head per-pixel. For the benchmark: report crack by tolerant metrics (relF1@2) next to strict IoU, as CIF's collapse is partly a strict-mask artefact | 30 | 60 |
| 17 | doi:10.1007/978-3-031-72114-4_47 (nnU-Net revisited, arXiv 2404.09556) | 2024 | MICCAI | github.com/MIC-DKFZ/nnUNet (general knowledge, unverified for this paper) | Re-benchmark: tuned CNN U-Nets beat transformer and Mamba segmenters; weak baselines and small test sets caused false claims | Every transformer arm must beat the tuned house U-Net++ on module-grouped 5-fold CV, not the 50-cell test only; nnU-Net 2D as a suite entry | 25 | 92 |
| 18 | arxiv:2607.00687 (LUMA) | 2026 | arXiv | github.com/tobna/LUMA (stated) | One fixed light mask-transformer head on any backbone (ViT, hierarchical, conv, MoE); 20 backbones, 11 pretrainings under one recipe. R: matches EoMT at cost parity; pretraining objective, not architecture, governs quality | Benchmark design: hold the head fixed and vary the encoder (ResNet-34 ImageNet, ConvNeXt, DINOv2 / v3 ViT) to separate backbone from decoder effects; also a cheap way to put a mask head on our ResNet-34 encoder | 30 | 70 |

Bets: #1 + #2 + #6 together are the medium bet (bold if DINOv3 ViT-L at 1024, judged on E1). #8 (MaxQuery for E1 decoys) and #9 (frozen PMT) are moonshots. #4, #5, #10, #11 are safe to medium.

## 4. Minimum experiments
House = U-Net++ R34 1-ch 512 px 20k steps; PF as in BRIEF. Screen on the existing module-grouped 5-fold CV over 532 train + val cells (1 seed per fold); test clean-49 and E1 with 5 seeds only for survivors.

1. **EoMT / EoSeg ViT-L (#1, #2, #4, #6).** Arm: EoMT ViT-L DINOv2 at 1024 px, 2 queries per class, block-fusion gate, full-res LoftUp-style or conv head, dense CE + Dice aux, layer-wise lr decay, 20k steps. Baseline: house PF. Metrics: inactive IoU, mIoU_rob, E1 crack relF1@2, E1 inactive IoU, crack IoU. Kill (alone): inactive IoU < 0.449 and mIoU_rob < 0.570 and E1 relF1@2 < 0.43. About 8 GPU-h per run; 5 folds + 5 seeds = 80 GPU-h.
2. **Heterogeneous ensemble (#5, #11, plus #1 if trained).** Arm: house 5-seed ensemble + SegFormer-B2 (1024 px) or EoMT member, fusion weight per class group chosen on val. Baseline: house 5-seed ensemble. Metrics: crack IoU, relF1@2, inactive IoU, mIoU_rob, E1 relF1@2. Kill: no metric gains more than its noise floor (crack IoU 0.012) fold-paired. SegFormer about 3 GPU-h per run, 30 GPU-h.
3. **Mask2Former semantic (#3, #4, #7, #13, #14).** Arm A: Swin-B M2F ADE20K at 512. B: + dense aux head + high-res conv branch. C: B + frequency-scaled query matching or mask-piloted jittered GT. Baseline: house. Metrics: inactive IoU, splice / material / edge_dark IoU, mIoU_rob. Kill: B if mIoU_rob < house - 0.01 and inactive IoU not above house; C only if B survives. About 4 GPU-h per run, 45 GPU-h.
4. **SegNeXt-B (#10).** Arm: MSCAN-B + ham + full-res skip at 512. Baseline: house. Metrics: gridline IoU / recall, crack relF1@2, mIoU_rob. Kill: gridline IoU < 0.313 and crack relF1@2 < 0.881. 20 GPU-h.
5. **MaxQuery decoy filter (#8).** Arm: from arm 1 or 3, compute max pixel-query similarity; suppress crack where it is below a val-chosen threshold. Baseline: same model without filter. Metric: E1 crack relP@2 at fixed relR@2, false-alarm px on half-cut scuff cells. Kill: E1 relF1@2 gain < 0.01. Under 1 GPU-h (inference only).
6. **PMT frozen (#9).** Arm: frozen DINOv2 (DINOv3 if user OKs) ViT-L + PMD + full-res head at 1024. Baseline: house PF. Metric: E1 only. Kill: E1 relF1@2 < 0.45 and E1 inactive < 0.24. About 30 GPU-h.
7. **Benchmark entries (#3, #11, #15, #17, #18).** Run SegFormer-B2, Mask2Former, Mask DINO, EoMT, nnU-Net 2D once under the fixed protocol; a LUMA-style fixed head across 3 to 4 encoders. No kill line.

## 5. Prior overlap with BRIEF section 5 (honest)
- Transformer segmenters and mask-classification decoders: never tried (BRIEF). Open.
- Foundation encoders: only frozen probes (ViT-S, ConvNeXt-T, SAM2 Hiera-T) and one ConvNeXt-T PF fine-tune screen (2 seeds, 4k steps, judged on F51 crack AP). ViT-L, mask decoders, 1024 input and 20k-step schedules are open. PMT (frozen) is closest to what failed, so it is scored lowest.
- Resolution: 2x input was n.d. for the house CNN. For 1/4 or 1/16 output models, 2x input restores output resolution; different mechanism. Open.
- Heterogeneous ensembles: never tried. Open.
- Crack copy-paste was n.d.; GOOSE-style rare-class copy-paste of inactive regions with their bounding cracks is not the same run. Open, low priority.
- MP-Former's jittered-GT training is unrelated to the offset-tolerant CE that was n.d.

## 6. Rejected or deferred
- arxiv:2211.06220 OneFormer: gains come from joint semantic / instance / panoptic training with text queries; we have one task, no panoptic labels.
- arxiv:2107.06278 MaskFormer: superseded by Mask2Former; its own claim (mask classification helps most with many classes) predicts little gain at 24 classes. Reference only.
- arxiv:2608.03216 iFAN: training-only ranking + cross-layer self-distillation, +0.63 mIoU average on ADE20K / COCO / Cityscapes; add only if a mask classifier survives.
- arxiv:2603.13044 GP-VM x SMA: mixed-effects analysis for small-data benchmarks; useful for benchmark statistics but belongs with the evaluation direction.
- doi:10.1016/j.solener.2025.114083 Hijjawi EL instance-seg benchmark (Mask2Former included): covered by D01 / D02.
- doi:10.1109/cvprw67362.2025.00238 UDA in the VFM era: source-only VFM fine-tuning closes most of the UDA gap; belongs to D30 (DG / UDA), but supports trying VFM segmenters for E1.
- arxiv:2207.04044 kMaX-DeepLab, arxiv:2210.05844 SegViT: superseded by EoMT line.
- arxiv:2602.17807 VidEoMT, arxiv:2605.18177 token-space mask prediction: video / efficiency, no accuracy lever for us.
- doi:10.3390/s26072254 Defect-Mask2Former (timber): same idea as #13.
- doi:10.3390/s24216908 PDeT (PV deformable transformer): numbers not retrieved; deformable attention covered by D09 / D22.
- doi:10.1109/tpami.2024.3419055 Mask2Anomaly: open-set road anomalies; MaxQuery (#8) is the cleaner small-data version.
- arxiv:2503.01835 Primus, arxiv:2509.02379 MedDINOv3: 3D medical / VFM adaptation; D24 / D25.
- arxiv:2411.09371 DSCformer, arxiv:2409.02866 Hybrid-Segmentor: crack hybrids, D09.

## 7. Gaps
- No controlled study found of mask classification vs per-pixel on 1 to 2 px structures. Our run would be the first.
- No paper with ViT segmenters on a few hundred greyscale industrial images. EoSeg (medical, small, but weak baselines) and CIF (cracks, large, instance mAP) are the nearest.
- `search_snippets` failed all session (S2 rate limit): could not pull EoMT's small-object table or the frequency-based matcher's tail-class numbers. Code for the matcher and iFAN unverified.
- Not searched here: Mamba segmenters (D22 / others), SAM-family mask decoders (D14 / D38).
- Fused-ensemble EL paper (#5): dataset and code unknown; worth a direct read if the user can get IEEE full text on campus.
