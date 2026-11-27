# D14 Foundation models for crack and thin-structure segmentation

Scout report, 13 Nov 2026. Literature phase only (no servers, no test or E1 predictions read).
Labels: R = what a paper measured, E = what our files measured (from BRIEF), S = my judgement.

## 1. Queries run

Research MCP `search_papers` (OpenAlex answered; S2, arXiv, Scopus, ScienceDirect timed out or refused on most calls):
1. segment anything crack segmentation fine-tuning (2020+)
2. CrackSAM parameter-efficient fine-tuning segment anything crack (2020+)
3. DINOv2 crack segmentation (2023+)
4. SAM adapter thin structure segmentation vessel (2023+)
5. SAM 2 fine-tuning retinal vessel thin structure segmentation (2024+)
6. SAM 3 segment anything with concepts (2025+)
7. SAM2-UNet Hiera encoder U-Net segmentation adapter (2024+)
8. DINOv3 dense features high-resolution segmentation fine structures (2025+)
9. vision transformer patch size thin structure segmentation failure small objects (2023+)
10. segment anything electroluminescence solar cell defect (2023+)
11. Rein vision foundation model domain generalized semantic segmentation parameter-efficient (2023+)
12. foundation model photovoltaic defect segmentation DINOv2 SAM (2024+)
13. feature upsampling vision foundation model features pixel-level LoftUp JAFAR FeatUp (2024+)
14. crack segmentation foundation model low-rank adaptation small dataset generalization (2025+)
15. high-quality segment anything fine detail HQ-SAM thin (2023+)
16. dual encoder CNN and frozen foundation model feature fusion crack segmentation (2024+)
17. distilling vision foundation model features into small CNN for dense prediction (2024+)
18. segment anything refine noisy pseudo labels thin crack annotation (2023+)
19. SAM2 crack segmentation adapter (2025+)
20. DINOv3 crack defect segmentation fine-tuning (2025+)
21. OmniCrack30k crack segmentation benchmark (2023+)
22. SAM2-UNeXT improved high-resolution baseline auxiliary DINOv2 encoder (2025+)
23. ViT-Adapter spatial prior module plain vision transformer dense prediction (2022+)
24. Conv-LoRA convolution meets LoRA segment anything (2024+)

Snowballing: `similar_papers` on CrackSAM + TopoLoRA-SAM + Fontaneli 2026; `get_citations` on CrackSAM (98 citing papers, 29 screened).
`search_snippets`: 4 attempts, all rate-limited (S2 keyless pool). Evidence was read from full text instead (Fontaneli 2026, TopoLoRA-SAM, CoRe-SAM3; all three already in the local library, so no new fetches used).
WebSearch (8): CrackSAM code, Segment Any Crack code, SAM2-UNet repo, SAM3 zero-shot crack prompt, Cekmeceli DG paper, CrackGeoFM code, JAFAR + EoMT repos, Conv-LoRA repo.

## 2. What the literature says about our core worry (patch size vs 1 to 2 px cracks)

- R (Fontaneli and Comin 2026, arXiv 2611.00396): fine-tuned MedSAM (plain ViT-B, patch 16, 1024 px input, decoder at 1/4 resolution) had thin-vessel (radius < 1.5 px) centerline recall not significantly different from the best CNN on all 4 datasets (-0.6 to +2.5 points). Pretraining raised thin recall by 17.6 and 12.4 points on DRIVE and VessMap; the same ViT from scratch was significantly worse than the best CNN. Upscaling small images to 1024 was significantly better than padding them (Dice and thin recall). Tuned with 100-trial searches per configuration (2,093 GPU-h total).
- R (Zhang et al. WACV 2026, arXiv 2412.04243): zero-shot / prompted SAM, SAM 2, HQ-SAM fail in proportion to tree-likeness and low textural separability; targeted fine-tuning did not remove the effect.
- R (SERD, arXiv 2607.12292; CoRe-SAM3, arXiv 2609.05816): SAM 3 with the text prompt "crack" already gives usable zero-shot crack responses on civil datasets (native SAM3 Crack500 IoU 41.3%; internal semantic response recall 82.7% vs 74.7% for its final masks). Input 1008 px.
- S: The patch-size failure is real for frozen probes at native scale (matches E: our frozen probes showed nothing), but the evidence says it goes away with (a) full or PEFT fine-tuning of a pretrained encoder, (b) 2x upscaling so a 16 px token covers 8 x 8 original px, and (c) a decoder with a high-resolution skip path. SAM 2 Hiera already has a stride-4 first stage, which is the cheapest way to get fine detail from a foundation encoder. None of (a) to (c) were tested here (BRIEF section 5, "Foundation encoders" row, leaves them open).

## 3. Selected papers

Baseline for every experiment: house U-Net++ / ResNet-34 (5-seed means, clean 49: crack IoU 0.474, relF1@2 0.881, inactive IoU 0.449, mIoU_rob 0.580; E1 crack relF1@2 about 0.42, E1 inactive 0.05 house / 0.24 PF). Screens should use the module-grouped 5-fold CV roots (problem 5) plus test-clean-49 and E1 as read-outs.

| # | id | year | venue | code | mechanism | adaptation to our data | score | bench |
|---|---|---|---|---|---|---|---|---|
| 1 | arxiv:2408.08870 SAM2-UNet | 2024/26 | Visual Intelligence | github.com/WZH0120/SAM2-UNet (verified via web) | SAM 2 Hiera encoder (frozen + small adapters) feeding a plain U-Net decoder; Hiera has a stride-4 stage so fine detail survives | 1-ch EL copied to 3 ch; Hiera-B+ or Hiera-L; 512 input and a 1024 (2x bilinear) arm; replace binary head with 24-class head + CE + soft Dice on crack/inactive (house loss); label-safe aug only; crack logit bias from val. Also ensemble with house U-Net++ (heterogeneous ensemble, untested here) | 74 | 85 |
| 2 | arxiv:2508.20909 Dino U-Net | 2025/26 | LNCS (MICCAI-W) | github.com/yifangao112/DinoUNet (from abstract) | Frozen DINOv3 ViT with an adapter that fuses ViT semantics with a conv low-level spatial branch, plus a fidelity-aware projection into a U-Net decoder; gains grow with backbone size up to 7B | DINOv3 ViT-L/16 (and ViT-7B if memory allows on A6000 48 GB with frozen backbone), 1024 input, 24-class head; the conv spatial branch is what carries 1-2 px cracks | 66 | 70 |
| 3 | arxiv:2512.01789 SAM3-UNet | 2025 | arXiv | github.com/WZH0120/SAM3-UNet (from abstract) | SAM 3 image encoder + light adapter + U-Net decoder, < 6 GB at batch 12 | Same recipe as #1 on SAM 3 perception encoder; 1008 px input (2x upscale of 512 then crop/pad); 24-class head. Gives the SAM3 arm of the benchmark | 62 | 75 |
| 4 | arxiv:2611.00396 Fontaneli and Comin | 2026 | arXiv | none found | Evidence + protocol: pretrained plain ViT matches CNNs on < 1.5 px vessels when fine-tuned and inputs are upscaled to 1024; padding loses | Use as the design rule for every ViT arm here: upscale 512 to 1024, full or PEFT fine-tune, never frozen probe; measure crack recall binned by width (our labels give width per source) | 58 | 70 |
| 5 | arxiv:2312.04265 Rein | 2024 | CVPR | github.com/w1oves/Rein (from abstract) | Learnable tokens refine each frozen VFM layer (about 1% params); beat full fine-tuning for domain-generalised segmentation | DINOv2/v3 ViT-L, Mask2Former head as in paper or our U-Net decoder; 24 classes; train on 478, judge mostly on E1 (unseen modules, half-cut, scuff). Aimed at problem 3 | 60 | 65 |
| 6 | arxiv:2504.14138 Segment Any Crack | 2025/26 | J. Computing in Civil Eng. | not found (web search, no repo) | Fine-tune only normalisation (LayerNorm) parameters of SAM; beat full FT and LoRA on OmniCrack30k (IoU 0.441) and was best on 3 zero-shot crack sets | SAM ViT-B/L or SAM2 Hiera with a trainable conv decoder, encoder LN-only; tests whether less encoder drift helps E1 the way PF did for inactive (E: PF raised E1 inactive 0.05 to 0.24) | 58 | 55 |
| 7 | arxiv:2401.17868 Conv-LoRA | 2024 | ICLR | autogluon repo examples/automm/Conv-LoRA (paper footnote, via web; not opened) | LoRA bottleneck with convolution experts (MoE over scales) to inject local prior into SAM ViT | LoRA rank 8-32 in SAM ViT-B/L at 1024 input; local conv prior is exactly what a 16 px patch lacks for 2 px cracks; prompt-free, multi-class decoder | 55 | 50 |
| 8 | arxiv:2601.02273 TopoLoRA-SAM | 2026 | arXiv | github.com/salimkhazem/Seglab (from abstract) | LoRA in frozen SAM ViT-B + depthwise conv adapter on the embedding + optional clDice; prompt-free | Use LoRA + conv adapter only; drop clDice (E: soft clDice failed here). 1024 input. Weak absolute numbers in paper (retina Dice 0.595), so treat as recipe, not evidence | 50 | 50 |
| 9 | arxiv:2409.07960 Cekmeceli et al. | 2024/25 | ECCV-W | github.com/kerem-cekmeceli/Foundation-Models-for-Medical-Imagery (via web) | Benchmarks DINOv2, SAM, MedSAM, MAE with Ladder / Rein(+LoRA) PEFT and decode heads (HQHSAM) for domain generalisation; FMs beat U-Net on unseen domains | Direct template for an E1 study: same PEFT grid, our 5 sources as domains (leave-one-source-out folds), E1 as the external domain | 50 | 60 |
| 10 | arxiv:2504.04034 UCS | 2025 | arXiv | github.com/kylechuuuuu/UCS (from abstract) | Sparse adapters in SAM encoder + FFT high-pass prompt generator + hierarchical feature compression decoder for curvilinear structures across domains | Binary crack-only branch (crack + inactive heads) next to house model; high-pass prompt suits EL cracks (dark lines) but also fires on gridlines and scuffs, so needs the multi-class context | 48 | 50 |
| 11 | arxiv:2606.23486 PEPA | 2026 | LNCS | not found | Post-encoder plug-in: snake-like target-conditioned upsampling + per-target learned differentiable threshold; 0.26M params | Attach to any FM decoder (#1 to #3) for crack only; the learned threshold overlaps with our val-chosen crack logit bias, so the test is the snake upsampler | 42 | 35 |
| 12 | arxiv:2506.11136 JAFAR | 2025 | NeurIPS | github.com/PaulCouairon/JAFAR (via web; DINOv3 checkpoints listed) | Attention-based upsampler that lifts frozen VFM features to any resolution using the image as guide | Upsample DINOv3 features to 512 x 512 and feed them as an extra input to the house decoder (side branch); cheap test of whether FM semantics help once resolution is restored | 42 | 30 |
| 13 | arxiv:2609.05816 CoRe-SAM3 | 2026 | arXiv | not found | Keep SAM3 "crack"-prompted prediction; learn tiny calibration + bounded zero-init residual from native visual features (18.9K params); mean crack IoU 62.3 to 70.5 on 5 datasets | Only worth it if SAM3 "crack" zero-shot fires on EL cracks (test #14 first). Then train on 478 cells, crack class only, fuse with house for other classes | 40 | 40 |
| 14 | arxiv:2607.12292 SERD | 2026 | arXiv | not found | Training-free: decode SAM3 internal "crack" semantic response (not its masks) and calibrate with Sobel; recall 82.7% vs 74.7% for SAM3 masks; also width / length measurement | Zero-shot crack-likelihood map for E1, where the house model gives p < 0.001 to 70% of crack pixels; use as (a) diagnostic, (b) extra input channel, (c) severity width estimate | 40 | 40 |
| 15 | arxiv:2503.19108 EoMT | 2025 | CVPR | github.com/tue-mps/eomt (via web) | Plain DINOv2 ViT jointly encodes patches and mask queries; no adapter, no pixel decoder | A credible "modern ViT mask-classification" baseline for the benchmark; at 512 px patch 16 gives 32 x 32 tokens, so run at 1024 and expect crack weakness; good for inactive / material / other classes | 35 | 75 |
| 16 | arxiv:2312.04233 CrackSAM | 2024 | Constr. Build. Mater. | not found (web search) | Adapter and LoRA PEFT of SAM for semantic crack segmentation; strong zero-shot to unseen crack sets | The most cited SAM crack method (98 citations); recipe is covered by #6 to #8; include as benchmark baseline | 45 | 70 |
| 17 | arxiv:2605.18413 Cracks in the Foundation | 2026 | arXiv | HF ibm-research/cif-dataset (from abstract) | 150k-tile civil crack instance dataset; shows zero-shot FMs and VLMs fail and specialised models plateau near 25% mAP; flags centre bias and shape reliance | Benchmark design: centre-bias check (our cracks vs cell position), report zero-shot FM rows; possible extra crack pretraining data (different modality, low score) | 28 | 65 |
| 18 | arxiv:2412.04243 Zhang et al. (limits of SFMs) | 2024/26 | WACV | github.com/mazurowski-lab/SAMFailureMetrics (from abstract) | Interpretable metrics for tree-likeness and textural separability that predict SFM failure | Compute both metrics per crack component in test / E1; stratify benchmark results (low-contrast cracks: 7% are < 2% darker than surroundings) | 25 | 60 |

## 4. Minimum experiments (S)

Ordered by expected value per GPU-hour.

1. **SAM2-UNet (#1)**. Arms: Hiera-L adapters at 512; same at 1024 input; baseline house U-Net++ (and PF). 3 seeds each, 20k steps, house loss and aug, 24 classes. Read-outs: clean-49 crack IoU, relF1@2, inactive IoU, mIoU_rob; E1 crack relF1@2, E1 inactive IoU; 5-fold CV crack IoU. Also score the 2-model ensemble (SAM2-UNet + house) against the 5-seed house ensemble at equal model count. Kill: single-model 3-seed mean crack IoU < 0.465 and relF1@2 < 0.875 and E1 relF1@2 < 0.43, and the heterogeneous ensemble adds < +0.01 crack IoU over the house ensemble. About 3 to 8 GPU-h per run, about 40 GPU-h total.
2. **Dino U-Net (#2)** with DINOv3 ViT-L at 1024 (and one ViT-7B frozen run). Same read-outs. Kill as above. About 40 to 60 GPU-h.
3. **Zero-shot SAM3 probe (#14)**, no training: run SAM3 "crack" prompt and the SERD decoding on val + F51 (not test or E1 until the protocol is fixed), measure relR@2 / relP@2. If relR@2 >= 0.5 on F51 crack, open CoRe-SAM3 (#13) and the SAM3-UNet arm (#3); else close the SAM3 text-prompt route and keep SAM3 only as an encoder. Under 2 GPU-h.
4. **E1-targeted PEFT grid (#5, #6, #9)**: on the best encoder from steps 1 to 2, compare full FT vs LN-only vs Rein vs LoRA, 3 seeds. Primary read-out E1 crack relF1@2 and E1 inactive IoU; kill if no arm beats house PF on E1 relF1@2 by +0.03. About 60 GPU-h.
5. **JAFAR side branch (#12)**: frozen DINOv3 ViT-L features upsampled to 512 concatenated into the house decoder; 3 seeds; kill if crack IoU and E1 relF1@2 both within noise (0.012). About 10 GPU-h.

## 5. Rejected (one line each)

- doi:10.1016/j.engappai.2025.113688 Topology-aware SAM for domain-invariant crack seg: no abstract and no open access through the tools; could not verify.
- arxiv:2606.05641 CrackGeoFM: multi-task (mask, skeleton, uncertainty) on a frozen FM; backbone unnamed in what I could read, no code found. Skeleton head idea belongs to the loss / topology direction.
- arxiv:2610.14274 Inspect Any Crack: SAC v2 + concrete crack severity index from width and area with ground-sampling calibration; concrete-specific, our severity needs inactive fraction and crack mode. Reference for D-severity only.
- arxiv:2609.00469 SAM3-LoRA for structural defects: instance-level concept prompts; its one transferable lesson (issue every absent class as a hard-negative prompt or presence collapses) matters only if a SAM3 text-prompt arm is opened.
- arxiv:2501.18855 FlexiCrackNet: EdgeSAM CNN encoder fused with a task CNN by gated attention; weaker encoder than #1 / #2, same idea as a side branch.
- doi:10.1609/aaai.v40i25.39182 CoGenSAM and doi:10.1609/aaai.v40i5.37315 CaPro: annotation-free or single-image SAM adaptation; we have labels, so the gain path is unclear.
- arxiv:2511.19046 MedSAM3, arxiv:2408.04579 SAM2-Adapter, doi:10.1177/14759217241261089 SAM LoRA crack, doi:10.3390/s25092642 SECrackSeg: same mechanisms as rows 1, 7, 8 with less evidence.
- arxiv:2306.01567 HQ-SAM: prompt-driven mask quality; we need prompt-free multi-class semantic output.
- arxiv:2509.06467 DINOv3 medical benchmark, arxiv:2603.28480 INSID3: few-shot / training-free; we have 478 labelled cells, not a few-shot problem.
- doi:10.1109/icsmd64214.2024.10920517 Unsupervised SAM on ELPV: the only EL + SAM hit; unsupervised, image-level ELPV, no pixel metrics comparable to ours.

## 6. Gaps

- No paper applies SAM / SAM2 / SAM3 / DINOv3 fine-tuning to EL cell segmentation with pixel labels. Our runs would be the first evidence.
- No paper studies FM fine-tuning under 1 to 2 px label jitter. Expect FMs to inherit the same labelling ceiling (crack IoU near 0.5); the gain path is recall on faint cracks and E1, so relF1@2 and E1 must be the primary read-outs.
- Snippet search was rate-limited all session; claims about SAM2-UNet, Dino U-Net and Rein come from abstracts only, not from their full text.
- Code for CrackSAM, Segment Any Crack, CoRe-SAM3, SERD, PEPA not found.
- Gated downloads: SAM 3 and DINOv3 weights need a licence click on Hugging Face / Meta; that needs the user's OK (BRIEF section 6).
- Sub-directions worth their own scout: heterogeneous ensembles and distillation from an FM teacher into the house model; FM-teacher pseudo-labelling on the 11.9k pool (BRIEF says SSL with FM teachers is open); feature upsamplers (LoftUp, NAF, AnyUp) compared head to head.
