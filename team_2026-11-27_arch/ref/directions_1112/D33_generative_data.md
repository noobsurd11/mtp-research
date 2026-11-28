# D33 Generative data for segmentation

Scout: literature agent. First pass 12 Nov 2026, resumed and extended 13 Nov 2026 (code checks, GenSeg, CycleGAN-Turbo, StyleSPADE, rhizotron synthetic pretraining, SegGen / Dataset Diffusion triage). Tags: R = the paper measured it, E = our files show it, S = my judgement.
Companion file: D06_el_synthesis.md already covers CrackSegFlow, PV-DDPM, FMS2, controllable crack pipeline 2609.12431, FreeMask, FreeCOS, Kikelj, Siamese-Diffusion, SeaS, AnomalyDiffusion, DualAnoDiff, Free Lunch, PDIG, SIGAN. This file does not repeat those rows. It adds the general "generated image-mask pairs" literature, target-style generation and translation for E1, generator-in-the-loop (hardness / validation-driven) generation, and training recipes for synthetic pairs.

## 1. Bottom line (S)

1. A learned mask-conditioned generator trained on our pairs learns p(image | jittered mask). It will place the dark line wherever annotators put it relative to the line, that is 1 to 2 px off half the time (BRIEF section 2). So "labels aligned by construction" holds only if (a) crack labels are snapped to the darkest ridge before the generator is trained, or (b) the crack is rendered procedurally onto a crack-free canvas, or (c) the label stays the real one and only appearance changes (translation, MCPMix). Every crack-generating arm should pass a mask-adherence gate first (house 5-seed ensemble relF1@1 between predicted crack and the generated mask on 200 samples >= 0.80).
2. Latent diffusion (Stable Diffusion, ControlNet, SD-Turbo, LDM joint generators) works on an 8x downsampled latent: a 512 px cell becomes 64 x 64, so a 1 to 2 px crack is sub-latent-pixel. Use latent methods for blobby or layout classes (inactive, material, splice, edge_dark, scuff, half-cut layout, source style). For cracks use pixel-space generators (GenSeg pix2pix-style GAN, StyleSPADE, SatSynth pixel DDPM, DAKTer) or inpaint-and-render, or keep the real label (translation with skip connections, MCPMix).
3. Where generation can plausibly move our numbers: E1 (context-limited: labelled cells that look like half-cut, scuffed CSIR modules), inactive (data-limited: new inactive layouts on more backgrounds), weak sources (BMRK, CFVS without twin) and rare other classes (splice never predicted). In-distribution crack IoU is noise-limited; generation is unlikely to move it unless pairs are aligned better than the real labels.
4. Cheapest decisive entries, all with code: CycleGAN-Turbo (one-step unpaired translation train cells to half-cut CSIR style, keep labels), Uncertainty-Aware ControlNet (target-style labelled data from unlabelled pool), GenSeg (pixel-space mask-to-image GAN tuned by validation loss, tested at 8 to 480 training images), GDI-style LaMa inpainting (EL paper; crack-free twins). Run these before any large joint generator.
5. Training recipes matter as much as the generator: paired appearance mixing with the real mask kept (MCPMix), synthetic pretraining then real fine-tune (rhizotron paper), hardness-driven generation (Crucial-Diff), learned placement (Synth4Seg).

## 2. Prior overlap (E, from BRIEF section 5)

- "diffusion or GAN data synthesis" is listed as never tried.
- Copy-paste of real crack components onto pool cells: n.d. on test, more decoys. Closes naive paste of real crack pixels at random places. Does not close generated appearance, learned placement, inpainted canvases, or E1-targeted backgrounds.
- Synthetic half-cut views: n.d. on test / E1, fewer half-cut false alarms. Changed geometry only, not appearance (scuffs, CSIR contrast). Open for generated or translated target style; translation arms below should start from these views.
- Pseudo-label SSL at 100% labels with the 11.9k pool: n.d. This partly closes methods whose labels for generated images come from a model trained on our labels (DatasetDM, DiffuMask, Dataset Diffusion), since that is close to pseudo-labelling generated rather than real pool images.
- Scuff as its own class (649 px, not learned): open for generating more scuff examples as negatives.

## 3. Queries run

Research MCP search_papers: 25 (OpenAlex answered throughout; Scopus / ScienceDirect HTTP 401, S2 rate-limited, arXiv mostly timed out). WebSearch: 8. search_snippets: 5 attempts, all rate-limited. Snowballing: similar_papers x2, get_citations x2. Full text read: SatSynth (arXiv 2403.16605), Uncertainty-Aware ControlNet (arXiv 2510.11346), GenSeg (arXiv 2408.17421, methods and code sections).

12 Nov:
1. joint image mask diffusion small labelled dataset segmentation augmentation (2024+)
2. few-shot anomaly image mask pair generation diffusion segmentation (2025+)
3. unpaired image translation domain adaptation segmentation diffusion target style (2023+)
4. ControlNet synthetic training data semantic segmentation rare classes (2023+)
5. synthetic thin curvilinear structure image generation segmentation vessel few-shot generative (2024+)
6. defect inpainting diffusion generation defect-free background mask segmentation gain (2024+)
7. filtering synthetic image annotation pairs noisy labels segmentation training generated data (2024+)
8. generative data augmentation segmentation photovoltaic electroluminescence pixel-level (2024+)
9. mask-conditioned diffusion fine-tuned on small dataset synthetic pairs improve segmentation medical few hundred (2025+)
10. crack image mask co-generation diffusion segmentation limited data (2025+)
11. generative augmentation long-tailed semantic segmentation rare classes diffusion synthesized (2024+)
12. CycleGAN unpaired translation defect segmentation domain shift industrial inspection (2020+)
13. diffusion generated dataset semantic segmentation image annotation synthesis (2025+)
14. copy-paste harmonization diffusion SDEdit realistic composite segmentation augmentation (2023+)
15. label-preserving diffusion translation target domain synthetic labelled data UDA segmentation (2025+)
Snowball: similar_papers on {SatSynth, GAA, Uncertainty-Aware ControlNet}; get_citations on SatSynth.

13 Nov:
16. SegGen mask-to-image text-to-mask generation segmentation training data (2023+)
17. Dataset Diffusion pixel-level semantic segmentation synthetic dataset generation (2023+)
18. few-shot defect image generation diffusion mask industrial segmentation (2025+)
19. electroluminescence solar cell synthetic image generation diffusion defect segmentation (2025+)
20. crack image synthesis mask-conditioned diffusion thin crack segmentation augmentation (2025+)
21. diffusion image translation label-preserving unpaired domain gap segmentation synthetic target images (2025+)
22. synthetic pretraining then fine-tuning on real versus mixing generated image-mask pairs segmentation small dataset (2024+)
23. one-step unpaired image translation diffusion adversarial CycleGAN-Turbo (2024+)
24. mask-guided image synthesis medical segmentation augmentation hundreds of training images diffusion gain Dice (2025+)
25. anomaly synthesis inpainting normal image defect mask diffusion segmentation-oriented (2026)
Snowball: get_citations on GenSeg (53 citing, mostly reviews); similar_papers on {GenSeg, StyleSPADE, rhizotron}.
WebSearch: diffusion image-mask pairs 2025; few-shot defect generation code; DefectFill; img2img-turbo repo; SatSynth repo; JoDiffusion repo; GenSeg repo; UnAICorN repo; ContourDiff repo.

## 4. Selected papers (18)

Score = value for our metrics (task rubric). Bench = value for the benchmark (BRIEF section 1). Code: "verified" = repo URL confirmed by a web page or the paper itself; "stated" = only in the abstract.

| # | id | year | venue | code | mechanism | adaptation to our data | score | bench |
|---|---|---|---|---|---|---|---|---|
| 1 | arxiv:2403.12036 CycleGAN-Turbo (img2img-turbo) | 2024 | arXiv (widely used, 193 cites) | github.com/GaParmar/img2img-turbo (verified, MIT; SD-Turbo weights have own licence) | One-step SD-Turbo generator with LoRA and encoder-decoder skip connections, trained with cycle + adversarial losses on unpaired domains; skips keep input structure. R: beats GAN and diffusion translators on day/night, weather | Domain A = our 478 train cells (and the existing synthetic half-cut views), domain B = 1,152 half-cut multi pool cells plus scuffed CSIR cells. Translate train cells to B style, keep the real labels. Grayscale replicated to 3 channels. The 64 x 64 latent can blur or erase low-contrast cracks, so gate: house-ensemble crack relF1@2 on translated vs source cell >= 0.9 of the source value, else drop that sample | 55 | 35 |
| 2 | doi:10.1038/s41467-025-61754-6 GenSeg | 2025 | Nature Communications | github.com/importZL/semantic_segmentation (stated in paper code section; Gitee mirrors seen) | Pixel-space mask-to-image GAN (pix2pix style) fed with augmented real masks; generator architecture (DARTS cells) learned by multi-level optimisation so the segmenter's validation loss steers generation. R: 11 tasks, 19 datasets, 8 to 480 training images, +10 to 20% absolute in- and out-of-domain | Pixel space, so cracks survive. Train on 478 cells at 512 px (or 256 crops); mask augmentations = flips, rot90, plus crack evolution (row 15) and inactive region edits; validation = module-grouped CV fold or F51, never test. Snap crack labels to the ridge first so the GAN does not learn the jitter. Expect smaller gains than R at 478 images; aim at inactive and weak sources | 55 | 45 |
| 3 | doi:10.1109/iccvw69036.2025.00441 Uncertainty-Aware ControlNet (UnAICorN) | 2025 | ICCV Workshops | github.com/JNiemeijer/UnAICorN (verified via arXiv link) | Semantic ControlNet trained on labelled masks plus an uncertainty ControlNet trained on labelled + unlabelled images, conditioned on segmenter entropy; fused at sampling they yield labelled images in the unlabelled domain's style. R: retinal OCT Spectralis to Home-OCT "significantly improved"; web summary: +2% mIoU on ACDC with SegFormer | LDM fine-tuned on the 11.9k pool; semantic ControlNet on the 478 train masks (24-class one-hot); uncertainty control = house 5-seed mean entropy, high on half-cut / scuff CSIR cells. Feed half-cut-cropped train masks so layout and style both move toward E1. Use for inactive, scuff context, layout; crack pixels only after the adherence gate | 55 | 40 |
| 4 | doi:10.1016/j.solener.2026.114943 GDI (Generative Defect Isolation) | 2026 | Solar Energy | LaMa is public; GDI repo unverified | LaMa (Fourier-convolution inpainting) removes selected defects inside their masks in EL cells, producing single-defect or defect-free variants. R: multi-label EL classification, rare-class F1 up to +63.6%, 26% fewer co-occurrence errors | Inpaint the crack label dilated by 3 px on the 209 crack cells (inactive on the 42) to get crack-free twins. Uses: paired hard negatives that keep every decoy; clean canvases for procedural or generated cracks at known places (aligned by construction); crack-without-inactive / inactive-without-crack variants for the argmax conflict. Check no dark residue (house p(crack) < 0.01 inside the old mask) | 55 | 35 |
| 5 | doi:10.59275/j.melba.2025-79a2 ContourDiff | 2025 | MELBA | github.com/mazurowski-lab (verified lab repo via web; README not opened) | Diffusion trained only on the target domain maps a Canny contour map to a target image; contour enforced at every sampling step, so source structure and masks are preserved. R: CT to MRI, better segmentation on translated data than other unpaired translators | Train on unlabelled half-cut multi and CSIR mono pool cells; contour = edges of busbars, fingers, border plus the crack label drawn in (so low-contrast cracks are not lost). Translate the 478 train cells into half-cut CSIR style, keep labels. Pixel-space option preferred for cracks | 50 | 30 |
| 6 | doi:10.3390/app16020837 StyleSPADE | 2026 | Applied Sciences | unverified | Conditional generator combining SPADE semantic-mask normalisation with a style image, so crack geometry from the mask is kept while background texture comes from the style exemplar. R: crack IoU 0.6376 with StyleSPADE data (Mask2Former, Swin-UPerNet, K-Net), 0.6452 with a stacking ensemble | Style image = a pool cell from the target group (half-cut CSIR, BMRK, CFVS without twin); mask = a train mask. Gives every train mask in every source style, which targets the weak-source gap and E1. SPADE is pixel space, so 1 to 2 px cracks are representable. Implement from SPADE / OASIS code if no repo | 50 | 30 |
| 7 | doi:10.1016/j.cacaie.2026.100204 UAV pavement ControlNet with label generator | 2026 | Computer-Aided Civil and Infrastructure Engineering | not stated | A label generator produces multiclass structural label maps; a fine-tuned ControlNet renders aligned image-mask pairs; 3x synthetic data. R: own UAV-Road set, mIoU 83.43 to 87.92 with 3x synthetic | Closest-domain ControlNet recipe (thin low-contrast distress, limited labels). Label generator = our masks edited (inactive from crack-isolation logic, splice / gridline layouts sampled from train statistics); ControlNet on 478 cells. Use for other classes and inactive; cracks only with snapped labels | 50 | 35 |
| 8 | doi:10.1109/cvpr52733.2024.02615 SatSynth | 2024 | CVPR | unverified (web search found none) | Pixel-space DDPM on the joint (image, bit-encoded label) tensor; labels as ceil(log2 K) binary channels; joint super-resolution 128 to 256. R: generated pairs added to real give about +1 to +1.6 IoU on LoveDA / OpenEarthMap (read from a figure) | 1 image channel + 5 bit channels (24 classes). 256 crops at native scale on 478 cells; snap crack labels first. Unconditional, new layouts for all classes at once; best fit for mIoU_rob and inactive | 45 | 50 |
| 9 | doi:10.64898/2026.10.30.763050 Rhizotron synthetic pretraining | 2026 | bioRxiv | unverified | LoRA + ControlNet + inpainting generate rhizotron images with paired root masks; synthetic pretraining then real fine-tune; Soft Dice against 7-annotator consensus maps. R: synthetic-only Dice 0.60, pretrain + fine-tune 0.80; also helped unseen crop species when real labels were few | Closest analog found: thin low-contrast roots, soil particles that mimic roots (our decoys), annotator disagreement. Copy the schedule, not the weights: pretrain U-Net++ on generated EL pairs (from rows 1 to 7), then PF fine-tune on 478 real. Its Soft Dice against multi-annotator consensus is a model for the benchmark's crack metric (we have two-annotation cells) | 45 | 45 |
| 10 | arxiv:2511.03219 MCPMix | 2025 | arXiv | not stated | For each real image, generate a synthetic counterpart under the same mask; mix appearance only, supervise with the original hard mask; real-anchored annealing of mix strength and loss weight. R: gains on Kvasir-SEG, PICCOLO, CVC-ClinicDB, ISIC 2017 (no numbers in abstract) | Counterparts from rows 1, 3, 5 or 6 (target style). Supervision stays the real mask, so no new label noise even if the generator drifts. Safest way to inject E1 appearance; anneal toward real by step 20k | 45 | 25 |
| 11 | doi:10.1109/tip.2025.3625380 Crucial-Diff | 2025 | IEEE TIP | github.com/JJessicaYao/Crucial-diff (stated in abstract) | Weakness-aware miner uses the downstream model's feedback to steer generation toward hard samples. R: MVTec pixel AP 83.63, F1-max 78.12; polyp mIoU 81.64 | Feedback = house per-pixel loss on generated crack / inactive. Known hard targets: cracks under 2% contrast, BMRK inactive, CFVS without twin, half-cut with scuffs. Pair with row 4 canvases | 45 | 35 |
| 12 | arxiv:2602.13693 WDLoRA CCM synthesis | 2026 | arXiv | not stated | Foundation diffusion model fine-tuned with weight-decomposed LoRA, conditioned on thin nerve-fibre masks plus clinical prompts. R: grayscale corneal microscopy, FID 5.18, downstream segmentation +2.2% | Small-data thin-structure ControlNet/LoRA evidence on grayscale. Prompt = source and cell type ("CSIR mono half-cut", "BMRK"), so each train mask is rendered in every source style; attacks weak sources and E1 style | 45 | 30 |
| 13 | doi:10.1109/tase.2025.3583713 Synth4Seg | 2025 | IEEE TASE | unverified | Bi-level optimisation learns where to paste synthetic defects and how to weight synthetic sources by maximising validation performance. R: up to +21.3% over random paste location, +2.7% from learned source weights, limited data | Our copy-paste null used random placement. Learn placement (relative to busbars, edges, scuffs) and weights of synthetic sources (rows 1 to 8, D06 renderers) against module-grouped CV crack relF1@2 | 45 | 25 |
| 14 | doi:10.1109/tcsvt.2026.3701691 DAKTer | 2026 | IEEE TCSVT | not stated | Diffusion jointly generates SAR images and soft-label maps, SNR-based alignment of noise across modalities; student learns from soft labels. R: oil-spill SAR, scarce data, better than other generative augmentation | Soft labels suit jittered cracks: crack band about 4 px wide, inactive sharp. Joint pixel-space generation of (EL, p_crack, p_inactive). Bold bet: the generator may learn the band better than we label the line | 40 | 25 |
| 15 | doi:10.1016/j.eswa.2025.126986 LSDM + crack evolution | 2025 | Expert Systems with Applications | huggingface.co/spaces/QinLei086/LSDM (demo, stated) | Latent semantic diffusion renders crack images from masks; heuristic "crack evolution" grows and branches annotations into new masks. R: beats classic augmentation and other generators on crack segmentation | Evolution on skeletonised crack labels gives new crack masks; grown cracks that cut a region off from all busbars give new inactive masks. Render with row 2, 4 or 6 (pixel space), not the latent model | 40 | 40 |
| 16 | doi:10.1016/j.media.2026.103996 UniVG | 2026 | Medical Image Analysis | github.com/XinAloha/UniVG (stated "will be made public") | Decompose vessel structure and background, recombine with varied morphology and backgrounds, then few-shot generative adaptation per target. R: 11 vessel tasks, 5 modalities, 5 labelled images each, near fully supervised | Recombine crack structures from one source with backgrounds of another (ARTS skeletons onto CSIR half-cut canvases from row 4), then adapt on 478 cells. Bold bet for E1 | 40 | 30 |
| 17 | doi:10.1609/aaai.v40i12.37941 JoDiffusion | 2026 | AAAI | github.com/00why00/JoDiffusion (per web results and AAAI paper; weights released Dec 2025) | Annotation VAE maps masks into the image latent space; one LDM generates image and mask jointly; mask-optimisation step reduces annotation noise. R: gains over prior synthetic-data methods on VOC, COCO, ADE20K | Replace text with source + class-presence tokens; annotation VAE over 24 classes. 64 x 64 latent loses cracks; use for other classes. Strongest recent joint image-mask baseline with code for the benchmark's synthetic track | 30 | 50 |
| 18 | doi:10.1145/3746027.3754920 GAA | 2025 | ACM MM | unverified | Few-shot LDM anomaly generation with localized concept decomposition, anomaly clustering, region-guided mask generation, low-quality filtering. R: better synthesis and localisation on MVTec AD and LOCO | Per-class few-shot generation for splice (never predicted), corrosion, material; one concept per source style. Benchmark baseline beside AnomalyDiffusion / SeaS (D06) | 30 | 45 |

Bets: rows 1 to 5 medium (E1, inactive, weak sources). Row 14 (soft-label joint generation) and row 16 (compositional recombination) are the bold bets. Row 9 is mainly a recipe plus a benchmark-metric precedent.

## 5. Minimal experiments (one per row)

Common rules: all arms on PF (encoder-preserving fine-tune), 5 seeds, same commit and data as the PF baseline. Synthetic share capped at 30% of each batch unless the arm is pretrain-then-fine-tune. Inactive decisions use module-grouped 5-fold CV over 532 train + val cells. E1 is read only at the end, never for tuning. Every crack-generating arm first passes the adherence gate (section 1).

1. CycleGAN-Turbo: PF + 478 translated cells (half-cut CSIR style, real labels) vs PF. Metric E1 crack relF1@2 and E1 inactive IoU; guard clean-49 test crack IoU. Kill: E1 relF1@2 gain < +0.03 and E1 inactive gain < +0.03, or test crack IoU drop > 0.01. About 15 GPU-h translator + 6 seg runs.
2. GenSeg: PF + GenSeg pairs (2x train size, snapped labels) vs PF. Metric CV inactive IoU, BMRK crack / inactive IoU, mIoU_rob. Kill: CV inactive gain < +0.02 and mIoU_rob gain < +0.01. About 30 GPU-h (multi-level search) + 6 seg.
3. UnAICorN: PF + 2,000 generated half-cut-style cells vs PF. Metrics and kill as row 1. About 90 GPU-h.
4. GDI twins: PF + 209 crack-free twins as paired negatives vs PF. Metric test crack relP@2 and E1 crack false-positive px per cell; guard relR@2. Kill: relP@2 gain < +0.01 with relR@2 drop > 0.01. Second arm: procedural crack on twins, kill on E1 relF1@2 < +0.02. About 8 GPU-h.
5. ContourDiff: PF + 478 translated cells vs PF. Kill: E1 relF1@2 and E1 inactive gains both < +0.02. About 36 GPU-h.
6. StyleSPADE: PF + every train mask rendered with BMRK, CFVS and half-cut CSIR style exemplars vs PF. Metric BMRK and CFVS-no-twin crack IoU (CV), E1 relF1@2. Kill: weak-source CV crack IoU gain < +0.02 and E1 relF1@2 < +0.02. About 20 GPU-h.
7. Pavement-style ControlNet + label generator: PF + 1,434 synthetic vs PF. Metric mIoU_rob, CV inactive. Kill: mIoU_rob < +0.01 and CV inactive < +0.02. About 30 GPU-h.
8. SatSynth: PF + 2,000 joint samples vs PF. Metric mIoU_rob, gridline / edge_dark / splice IoU, CV inactive. Kill: mIoU_rob < +0.01. About 60 GPU-h.
9. Synthetic pretrain then fine-tune: U-Net++ pretrained on generated pairs (best generator of rows 1 to 7), then PF on real vs PF. Metric CV crack relF1@2, E1 relF1@2. Kill: both < +0.01. About 10 GPU-h once pairs exist.
10. MCPMix: paired mixing vs plain synthetic with the same counterparts. Metric E1 relF1@2. Kill: < +0.01 over plain synthetic. About 6 GPU-h.
11. Crucial-Diff feedback: guided vs unguided generator at matched count. Metric CV inactive, test relR@2 on cracks < 2% contrast. Kill: < +0.01. About 20 GPU-h.
12. WDLoRA source prompts: PF + train masks rendered in BMRK and half-cut CSIR styles vs PF. Kill: BMRK inactive CV gain < +0.03 and E1 relF1@2 < +0.02. About 30 GPU-h.
13. Synth4Seg learned placement vs random placement of the same synthetic cracks. Metric CV and E1 relF1@2. Kill: < +0.01. About 30 GPU-h.
14. DAKTer soft-label joint generation vs PF. Metric test crack relF1@2 and IoU at val-chosen bias. Kill: both < +0.005. About 60 GPU-h.
15. Crack evolution: evolved masks vs original masks through the same pixel renderer. Metric CV inactive, test relR@2. Kill: < +0.01 on both. About 20 GPU-h.
16. UniVG-style recombination vs PF. Metric E1 relF1@2. Kill: < +0.02. About 15 GPU-h.
17. JoDiffusion: benchmark baseline. PF + JoDiffusion pairs vs PF, metric mIoU_rob, reported without kill. About 50 GPU-h.
18. GAA: benchmark baseline for splice / corrosion / material; metric splice IoU (now 0.000), reported.

## 6. Rejected or demoted (one line each)

- doi:10.52202/075280-2383 DatasetDM (code showlab/DatasetDM): masks from a decoder trained on our 478 cells, close to the pseudo-labelling already n.d. at 100%; keep only as an optional benchmark baseline.
- doi:10.52202/075280-3359 Dataset Diffusion (code VinAIResearch/Dataset-Diffusion per abstract): text-prompt cross-attention masks; no text concept for EL classes, masks far too coarse for 1 to 2 px cracks.
- doi:10.1109/iccv51070.2023.00117 DiffuMask: same reason as Dataset Diffusion.
- doi:10.1007/978-3-031-73242-3_20 SegGen (ECCV 2024): text-to-mask then mask-to-image on natural scenes; abstract not returned by the tool; mask-to-image half is covered by rows 2, 3, 7.
- doi:10.1109/wacv61041.2025.00370 GAUDA: uncertainty-targeted joint LDM generation; folded into row 11 (same hardness idea, code available there).
- arxiv:2503.09221 Active-learning ControlNet guidance: training-free add-on; worth a 4 GPU-h tweak on row 3 or 7 only if those pass.
- doi:10.24963/ijcai.2025/251 DriftRemover (code JJessicaYao/DriftRemover): latent anomaly generation from coarse masks; latent resolution limits it to blobby classes, which rows 3 and 7 already cover.
- doi:10.1109/wacv57701.2024.00281 DIDEX: pseudo-target domains from text prompts; needs a text-to-EL prior we lack. Rows 1 and 3 use unlabelled target images instead.
- doi:10.1109/iccv51070.2023.00081 label-guided diffusion translation: code unverified; rows 1 and 5 do the same job with code.
- doi:10.1007/978-3-031-72933-1_6 DGInStyle: abstract not returned; natural-scene domain generalisation.
- arxiv:2605.19289 SENSE: natural-scene study of what makes synthetic data useful; not transferable to single-cell EL.
- doi:10.1145/3664647.3680692 Shape-aware ControlNet for inexplicit masks: makes the generator ignore mask noise, which breaks alignment for thin cracks.
- doi:10.1609/aaai.v39i7.32777 CLIP-based synthetic data selection: CLIP similarity meaningless on grayscale EL; FreeMask loss filtering (D06) is the better filter.
- arxiv:2406.02435, arxiv:2607.08201 TMI, doi:10.1007/s11263-024-02223-3 MosaicFusion: large-vocabulary instance segmentation on natural images.
- arxiv:2604.08915 UniDG, arxiv:2509.06693 STAGE, arxiv:2508.03143 SARD, arxiv:2607.29533 OSAGEN, doi:10.1007/978-3-032-37422-6_14 DeltaDeno, doi:10.1007/978-3-032-36987-1_6 GroundingAnomaly, doi:10.1007/s00371-025-04078-2 DefFiller, doi:10.1109/access.2025.3568866 Anodapter: MVTec-style anomaly generators; row 18 and D06 cover the family; no code verified.
- doi:10.3390/s25103038 few-shot steel defect generation: image-level generation for detection; no mask-level evidence.
- doi:10.1109/access.2020.3024554 CycleGAN defect segmentation on periodic textures: superseded by row 1.
- arxiv:2503.15056 IBCD, arxiv:2608.06240 PRISM, arxiv:2511.20307 TReFT: newer one-step unpaired translators; reasonable swaps for row 1 if CycleGAN-Turbo fails the adherence gate; code not checked.
- arxiv:2510.27646 VessShape, doi:10.1109/tmi.2025.3608467 Conditional Virtual Imaging: vessel shape priors; row 16 carries the idea.
- arxiv:2609.13226 leprosy LDM, doi:10.1049/htl2.70003 surgical class-aware diffusion, arxiv:2607.08794 sand-boil SDXL DreamBooth synthesis, arxiv:2501.09008 SimGen: same recipe as rows 7 and 12 with weaker relevance.
- doi:10.3390/jimaging12030132 bounding-box guided diffusion: boxes as control; our masks are richer.
- arXiv 2503.13985 DefectFill (CVPR 2025, WebSearch only): fine-tuned inpainting diffusion; authors note failures on global defects; row 4 gives inpainting without training.

## 7. Gaps

- No paper measures how a learned generator handles label jitter on 1 to 2 px structures. The adherence gate is our own construction and should be reported in the benchmark.
- No paper reports a pixel-level segmentation gain from generated EL images (consistent with D06). GDI is the only EL generative paper here, and its gain is in classification. PV-DDPM (D06) generates EL anomalies but reports detection-side use.
- Code still unverified: SatSynth, GAA, MCPMix, DAKTer, WDLoRA, Synth4Seg, StyleSPADE, rhizotron pipeline. GenSeg repo is from the paper's code statement plus Gitee mirrors; GitHub page not opened.
- search_snippets (S2) was rate-limited in both sessions, so no snippet evidence; UnAICorN ACDC +2% comes from a web summary, not the paper text.
- Defect Spectrum / Defect-Gen (doi:10.1007/978-3-031-72667-5_11, ECCV 2024) returned no abstract; not verified, not in the table. TF-IDG (ICCV 2025), DefectDiffu (arXiv 2408.00372), AdaBLDM (arXiv 2402.19330) seen only in web results.
- Worth its own search: label snapping to the intensity ridge before generator training (overlaps D16); pixel-space versus latent diffusion fidelity for sub-latent-pixel structures; translation-based test-time adaptation (translate E1 cells toward the training style instead of the reverse).
