# Scout `vfm`: vision foundation models and their adaptation for dense prediction

27 Nov 2026. Literature only: no training, no server access.
Labels: **R** = reported by the paper (abstract or full text read through the Research MCP), **S** = my judgement.
Scope rule: the 12 Nov sweep already covered this family in D14 (crack FMs), D22 (high-res and upsamplers) and D24 (VFM + PEFT). I did not re-argue those rows. I looked for what they missed: EL-specific VFM work, diffusion and depth backbones, generalist/in-context models, SAM variants, SSL objectives, side-tuning, and direct evidence on "VFM vs CNN" for small, thin targets.

## 1. Queries run

Research MCP `search_papers` (OpenAlex and ScienceDirect answered every time; arXiv and Scopus answered on some calls; Semantic Scholar was rate-limited for the whole session, so `search_snippets` was not used):

1. diffusion model features semantic segmentation pretrained Stable Diffusion encoder (2023+)
2. DiffusionEdge diffusion probabilistic model crisp edge detection (2023+)
3. Marigold fine-tuning diffusion model dense prediction segmentation single step (2024+)
4. diffusion model segmentation medical image thin structure vessel fine-tuned denoising UNet features (2023+)
5. Unleashing text-to-image diffusion models for visual perception VPD (2023+)
6. Depth Anything encoder semantic segmentation fine-tuning DPT head (2024+)
7. diffusion denoising crack segmentation pavement concrete generative segmentation (2023+)
8. in-context segmentation generalist SegGPT Painter universal segmentation few-shot (2023+)
9. UniverSeg Tyche in-context medical image segmentation new tasks without retraining (2023+)
10. MedSAM2 SAM 2 medical fine-tuning segment anything medical images (2024+)
11. automatic prompt-free segment anything fine-tuning semantic segmentation without prompts (2023+)
12. FeatUp model-agnostic framework features at any resolution (2024+)
13. feature upsampling vision transformer foundation model pixel-level 2026 (2025+)
14. segment anything thin structure curvilinear vessel crack high resolution fine detail adaptation (2024+)
15. solar cell electroluminescence defect segmentation segment anything vision transformer foundation model (2023+)
16. masked autoencoder pretraining grayscale industrial or medical images segmentation domain-specific self-supervised ViT (2023+)
17. AM-RADIO agglomerative model reduce all domains into one RADIO (2024+)
18. scaling language-free visual representation learning Web-SSL (2025+)
19. parameter-efficient fine-tuning segment anything medical image segmentation comparison LoRA adapter benchmark (2024+)
20. SAM2-UNet thin structure vessel crack segmentation Hiera encoder improved (2025+)
21. DINOv2 retinal vessel segmentation fine-grained thin structures foundation model frozen high-resolution branch (2024+)
22. side-tuning frozen backbone ladder side network dense prediction memory efficient (2022+)
23. visual prompt tuning semantic segmentation domain shift frozen vision transformer (2023+)
24. SAM-Adapter adapting segment anything in underperformed scenes camouflage shadow (2023+)
25. HQ-SAM segment anything in high quality fine-grained masks thin (2023+)
26. high-frequency details vision foundation model fine-tuning medical segmentation boundary loss of detail patch embedding (2024+)
27. diffusion features domain generalization semantic segmentation robust unseen domains (2024+)
28. crack segmentation DINOv2 OR DINOv3 OR SAM2 fine-tuning cross-dataset generalization 2026 (2025+)
29. EfficientSAM masked image pretraining leveraged segment anything lightweight MobileSAM (2023+)
30. SAM 3 image encoder fine-tuning semantic segmentation adapter benchmark SAM2 comparison (2025+)
31. EVA-02 OR I-JEPA OR iBOT backbone dense prediction semantic segmentation transfer (2022+)
32. DINOv3 dense features segmentation fine structure high resolution adapter medical industrial (2026+)
33. dichotomous image segmentation diffusion model fine-grained thin structures high resolution (2024+)
34. ViT patch size thin structure segmentation smaller patches high resolution token vessel crack (2023+)
35. road crack segmentation segment anything 2 low-light adapter (2025+)
36. layer-wise learning rate decay linear probing then fine-tuning vision transformer segmentation out-of-distribution (2022+)
37. foundation model versus nnU-Net small dataset segmentation benchmark SAM DINOv2 fine-tuned CNN baseline comparison (2024+)
38. GenPercept diffusion one-step deterministic dense perception segmentation fine-tuning generative prior (2024+)
39. Matcher PerSAM one-shot segmentation feature matching foundation models SEEM (2023+)
40. frequency adapter segment anything high-frequency prompt thin crack defect segmentation fine-tuning (2024+)
41. MedSAM segment anything in medical images Theia distilling vision foundation models (2024+)
42. Segment anything in medical images MedSAM (2024)
43. Theia distilling diverse vision foundation models for robot learning
44. HCFNet SAM2 hierarchical cross-branch frequency-aware industrial surface defect segmentation
45. DINOv2: Learning Robust Visual Features without Supervision
46. UniverSeg universal medical image segmentation
47. Vision Transformers for Dense Prediction DPT

Snowballing: `get_citations` on SAM2-UNet (40 of 333), DiffusionEdge (30 of 146), Dino U-Net (28 of 29), Rein (38 of 234); `similar_papers` on PV-SAM + SAM2-UNet (17).
Full text read (sections named): PV-SAM (method 3.1, 3.4, dataset, results, ablations), Kutlusan and Li 2611.14519 (4.1, 4.3, 4.4, 5.3), DiffDIS (4.1, 5.1 to 5.3), nnSAM (II.C, II.D, III, Table 1), SAUGE (implementation, comparisons), Frepa (4.2, 4.4.2, 4.5). EVP full-text fetch timed out (abstract only).

## 2. Counts

- 47 `search_papers` calls, about 1,750 merged hits as reported by the tool (overlapping across queries); about 560 titles shown and screened by title/abstract; plus 153 from snowballing.
- Kept after dedupe: **94 papers** in `papers.tsv`.
- **88 NEW**, **6 already in MASTER**: P372 SAUGE (PARKED), P208 Frepa (PARKED), P538 DiffDIS (PARKED), P442 DiffusionEdge (BENCH_ONLY), P561 GED (PARKED), P410 SANSA (RUN_AFTER_GATE). Also referred to but not re-listed: P002, P041, P069, P089, P093, P096, P140, P160, P173, P190, P225, P253, P622.
- Most NEW rows are fit 1 to 2 (base models, surveys, generalist/in-context models, depth backbones). This family was well mined on 12 Nov; what is new and useful is a short list.

## 3. What the new evidence says about our three constraints (S, built on R below)

- **Grey-scale input.** No paper here uses a 1-channel VFM stem; all replicate to 3 channels. Grey-scale evidence exists: PV-SAM (EL), Frepa (X-ray, CT, OCT, vessels), nnSAM (MR, CT, X-ray), ClassWise-SAM-Adapter (SAR). None shows that replication hurts.
- **1 to 2 px output.** The full texts agree that the ViT grid limits boundaries: Kutlusan finds U-Nets beat adapted DINOv2 on NSD at 2/224 px tolerance and DINOv2 misses small lesions entirely more often; PV-SAM's output is a 256x256 mask feature upsampled. Diffusion backbones (DiffDIS, GED, Marigold) work in a stride-8 VAE latent, so a 1 to 2 px crack sits below one latent cell. Every VFM arm must keep the house HRNet/U-Net++ as the pixel path and add VFM features as context. nnSAM, the ladder SAM and EVP are all built this way.
- **Cost on 48 GB A6000s.** Numbers from the papers: SAUGE trains on a 3090 in about 20 GPU-h at 16 GB (ViT-B SAM); nnSAM uses MobileSAM; DiffDIS trains SD at 1024 px with batch 4 on one H800; PV-SAM's best result uses ViT-H. A frozen-encoder side input (nnSAM style) needs no backprop through the VFM and is the cheapest arm. Side-tuning (E3VA, HST) is the route if adapters are needed at 1024 px.

## 4. Top 10

**1. nnSAM, doi:10.1002/mp.17481 (arXiv 2309.16967), Medical Physics 2024. NEW. Fit 4.**
R (full text): a frozen SAM encoder (MobileSAM) embedding of the image at 1024 px (64x64) is resized and concatenated into the nnU-Net decoder; the nnU-Net path is unchanged. With 20 training images: brain white matter DSC 82.8 vs nnU-Net 79.3 (ASD 1.14 vs 1.36 mm). The gain grows as the training set shrinks from 20 to 5 images.
Mapping: this is the D24 "VFM-H" side-branch idea in its cheapest form. The pixel path that carries the 1 to 2 px cracks stays the house HRNet-W18 + U-Net++. The frozen VFM can only add context, which targets recall on unseen modules and rare inactive regions. Swap MobileSAM for SAM2 Hiera-B+ / DINOv3-L / C-RADIOv4 and keep everything else. Risk: the gain is shown at 5 to 20 images, and we have 478 cells.

**2. Kutlusan and Li, arxiv:2611.14519 (2026), arXiv. NEW. Fit 4. Use it as protocol and design evidence.**
R (full text): DINOv2 adapted with BitFit, LoRA or full fine-tuning, against plain and residual U-Nets from scratch, on 3 medical domains with 8 external test sets. In domain the two are level (within a 0.013 floor). Out of distribution the adapted VFM is better on all 8 sets. The U-Nets give finer boundaries (NSD at 2/224 px), and DINOv2 misses small lesions entirely more often (13 vs 0 empty predictions on polyp). LoRA at 2.7% of parameters equals full fine-tuning. The rank needed depends on the domain (4 to 32), so it must be swept on the target data.
Mapping: this paper predicts our pattern. A VFM should help E1 recall (unseen modules) but lose thin-line precision on its own. Hence: hybrid only, small PEFT capacity, and a rank sweep chosen on the target domain. It also says why our frozen probes and the 4k-step A8 screen do not close the question.

**3. PV-SAM, doi:10.1016/j.solener.2025.114145, Solar Energy 2025. NEW. Fit 3.**
R (full text): this is the only pixel-level EL defect segmentation with a fine-tuned SAM in the results. Homomorphic filter pre-step, DBSCAN prompts, and an HQ-SAM-style side network: early and final ViT layers (64x64) upsampled to 256x256, channel attention, then fused with the mask-decoder feature. Trained on UCF-EL (9,022 / 2,234, random split). ViT-H: 54.6% mIoU, 49.4% boundary IoU. Ablation: the side network gives the largest gain; ViT-H beats ViT-B. The paper claims +20.7 mIoU over U-Net at 512 px.
Mapping: domain evidence that SAM features plus a side network can be trained on EL, and a ready design for a SAM side branch. Weak points: random image split (module leakage likely), mIoU not crack relF1@2, a weak U-Net baseline, and an output grid of 256x256 for 512 px input, so it cannot resolve 1 to 2 px cracks without our pixel path. It belongs as a benchmark row, and its side-network fusion is a candidate fusion design for item 1.

**4. Frepa, doi:10.1109/tmi.2025.3559402 (arXiv 2407.14651), TMI 2025. MASTER P208 (PARKED). Fit 3. Re-open as a different variant from SparK.**
R (full text): MAE-style pretraining with high-frequency masking, low-frequency perturbation and histogram-equalised masking. It works for ViT, Swin and ConvNeXt. With frozen encoders it gains +7 to +15% DSC on fine structures (retinal vessels, OCTA, intercellular gaps) over other FMs. The ablation shows that removing the frequency masking drops it to MAE level.
Mapping: domain pretraining on the 11.9k EL pool aimed at high-frequency detail, i.e. cracks. Our SparK MIM was null, and the ablation says plain MIM equals MAE, so this is a clearly different objective. Risk: evidence is against other FMs with frozen encoders on random splits, not against fine-tuned ImageNet CNNs.

**5. EVP, Explicit Visual Prompting, doi:10.1109/cvpr52729.2023.01862 (arXiv 2303.10883), CVPR 2023. NEW. Fit 3. Abstract only.**
R: tunes a frozen ViT with prompts built from each image's own patch embeddings and its high-frequency components, using 5.7% extra parameters. It beats other PEFT methods at equal parameter count and is SOTA on low-level structure tasks (forgery, defocus, shadow, camouflage).
Mapping: the cheapest way to push crack-scale high-frequency signal into a frozen VFM side branch (items 1 and 6). Aimed at thin-line recall where the ViT grid smooths faint cracks. Code is public. Risk: the tasks are region-level, not 1 to 2 px lines.

**6. HCFNet, doi:10.3390/s26144597, Sensors 2026. NEW. Fit 3. Abstract only (truncated).**
R: prompt-free SAM2 for industrial defects. Gated adapters in the frozen SAM2 encoder, plus a Laplacian-enhanced auxiliary branch that amplifies high-frequency components, which the abstract says SAM2 is insensitive to.
Mapping: a direct variant of P002 arm 4 (frozen Hiera + adapters) with an explicit high-frequency branch for thin defects. Cost: new head only. Risk: results unknown, low-tier venue.

**7. SAUGE, doi:10.1609/aaai.v39i6.32615, AAAI 2025. MASTER P372 (PARKED). Fit 3.**
R (full text): a frozen SAM with a 1.5% side transfer network regresses intermediate SAM layers to edges of increasing granularity. It is trained on pseudo labels made by blending annotator labels. Best ODS on BSDS and Multicue; zero-shot NYUDv2 ODS 0.794, above supervised EdgeSAM (0.783) and DiffusionEdge (0.761). About 20 GPU-h and 16 GB on a 3090.
Mapping: it models annotator granularity, i.e. our 1 to 2 px jitter, explicitly. Its cross-dataset result speaks to unseen-module generalisation. We have one annotator per cell, so the blending trick would need the two-annotator subset used to set the 2 px tolerance. Use: a crack-only SAM side head under the house model.

**8. Gu et al., arxiv:2404.09957, MELBA 2025. NEW. Fit 3. Abstract only.**
R: 18 SAM fine-tuning strategies on 17 radiology datasets. PEFT in both encoder and decoder is best. Architecture has a small impact. Further self-supervised training of SAM on domain images improves results. Fine-tuned SAM is only slightly better than earlier methods.
Mapping: the recipe for the P002 / P041 SAM-family arms (PEFT in encoder and decoder, not decoder only). It also supports continued SSL of the VFM on our 11.9k pool before supervision (same direction as ExPLoRA, P150). Code and weights are public.

**9. DiffDIS, arxiv:2410.10105, ICLR 2025. MASTER P538 (PARKED). Fit 2. Moonshot.**
R (full text): SD-Turbo UNet with one-step denoising, mask and edge latents, an auxiliary edge task, and 1024 px input. DIS5K overall max F 0.911 vs MVANet 0.908 and BiRefNet 0.900. The same network from scratch gets 0.682 vs 0.883 from SD-Turbo init on DIS-VD.
Mapping: the clearest evidence in this family that a large generative prior helps very fine, high-resolution masks (wires, meshes) with 3,000 training images. Risk: the VAE latent is stride 8, so a 1 to 2 px crack is below one latent cell. Use it only as a context branch, or run it at 2x input. Heavy (H800-class training).

**10. Ladder fine-tuning SAM with a complementary CNN, doi:10.1016/j.procs.2024.09.452 (arXiv 2306.12737), 2024. NEW. Fit 2. Abstract only.**
R: a frozen SAM encoder plus a trainable CNN (ResNet), fused, with only part of SAM tuned.
Mapping: a published form of "house CNN + VFM". Together with nnSAM (concat into the decoder) and PV-SAM (side network), it gives three fusion points to compare inside one harness: bottleneck, decoder, and output. Weak venue, medical organs only, so it is listed for the design rather than for its numbers.

Close runners-up: E3VA (memory-efficient adapters for dense prediction, which matters for ViT-L at 1024 px on 48 GB); "Fine-Tuning Image-Conditional Diffusion Models is Easier than you Think" (WACV 2025, the cheapest single-step diffusion recipe with a task loss); ViT-Up (2026, an upsampler with no image guidance, as a contrast arm for the D22 upsampler probe); DuEx-Crack (its silent-rate probe is a label-free check of whether a frozen VFM fires on EL cracks).

## 5. Rejected or low (one line each; detail in papers.tsv)
- Generalist and in-context models (SegGPT P548, UniverSeg, Tyche, MultiverSeg, PerSAM, Matcher P622, SEEM, INSID3, SANSA P410): we have 478 labelled cells. They are at most a few-shot track for new layouts, and their resolution (128 to 518 px, patch grids) loses thin lines.
- Depth/geometry backbones (Depth Anything 3, DepthForge, depth pretraining): EL cells are flat, so there is no geometric cue. Depth Anything (P080) is already used in MASTER for its pseudo-label recipe, not as an encoder.
- Open-vocabulary diffusion (ODISE, CLOUDS, VPD): the text classes do not exist for EL; they are heavy, and the stride-8 latent is too coarse.
- Plain SSL backbones (I-JEPA, EVA-02, Web-SSL, Franca, Theia, AM-RADIO, RADIOv2.5): no dense or thin-structure evidence beyond what C-RADIOv4 (P173) and DINOv3 (P190) already offer. Franca is an ungated fallback.
- SAM crack application papers with no abstract in the index (SAM2-UwMA, the in-domain adapted SAM with YOLO prompts, the pavement crack FM + skeletonization paper): kept as fit 1 so they are not lost.

## 6. NOT_FOUND (known to me, not returned by the tools)
- Painter ("Images Speak in Images"): searched in query 8; not returned.
- iBOT: searched in query 31; not returned.
- MAE (He et al., Masked Autoencoders Are Scalable Vision Learners): query 16; the original not returned.
- MobileSAM: query 29; not returned (nnSAM uses it, per its full text).
- DDP (diffusion dense prediction, Ji et al. 2023): queries 1, 3, 38; not returned.
- VPT (Jia et al., Visual Prompt Tuning, 2022): query 23; not returned.
- SAM-Med2D: not searched by name; not returned by queries 10 and 19.

## 7. Gaps
- No paper tests any VFM against a well-tuned CNN on 1 to 2 px lines with a tolerance metric. Kutlusan is the closest controlled study, and it is on lesions.
- PV-SAM is the only EL + VFM pixel paper, and it uses a random split. Our runs would be the first module-grouped evidence.
- Semantic Scholar was down all session, so citation contexts (critiques of PV-SAM or nnSAM) were not checked.
