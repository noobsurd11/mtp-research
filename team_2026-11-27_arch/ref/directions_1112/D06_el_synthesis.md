# D06 Synthetic EL data: physics simulation and generative models

Scout: literature agent, 12 Nov 2026. Tags: R = the paper measured it, E = our files show it, S = my judgement.

## 1. Bottom line (S)

1. No paper reports a pixel-level segmentation gain from synthetic EL images. PV-DDPM (Hanifi 2025, the E-SCDD paper) is the only EL generator with masks and code. Its only downstream number is an anomaly-detection gain from a dataset that mixes 110 new real cells with the synthetic ones, with no synthetic-only ablation (R). Its released synthetic images are hand re-annotated, which suggests the conditioning mask was not trusted as a label (R, S).
2. The strongest evidence comes from thin-crack work outside EL. CrackSegFlow (Automation in Construction 2026) renders crack images from masks in pixel space with flow matching. It gained +11.3 mIoU on CrackTree260 (1 px centreline labels, about 400 training crops) and +13 mIoU cross-domain when masks are rendered onto target-domain crack-free backgrounds (R). That second setting is our E1 problem: render cracks onto the 1,152 unlabelled multi half-cut pool cells, with their scuffs as hard negatives.
3. For inactive (42 train cells), the physics is simple enough to use as a rule: a region is inactive when cracks cut it off from every busbar (Kikelj 2020 quasi-SPICE model, active vs inactive cracks). We can draw crack curves on the 167 train cells that have crack but no inactive, compute the isolated region, and either darken it with source-measured statistics (rule renderer) or render it with a PV-DDPM retrained on our 478 train cells. This is the cheapest new route to more inactive examples. No paper has tested it on EL segmentation (S).
4. Latent diffusion (Stable Diffusion, ControlNet, AnomalyDiffusion, SeaS) works in an 8x down-sampled latent. CrackSegFlow shows it blurs or shifts hairline cracks (R, qualitative). For our 1 to 2 px cracks, use pixel-space renderers. Keep latent methods for blobby classes (inactive, material, corrosion, splice) and as benchmark baselines (S).
5. Training-side recipes matter as much as the generator: FreeMask filtering of noisy synthetic regions plus hardness-aware resampling (NeurIPS 2023, code), and label-confidence weighting of synthetic pixels by an ensemble trained on real data (arXiv 2609.12431). Both are cheap add-ons to any synthetic arm (S).
6. Benchmark hygiene (E, S): the E-SCDD release puts 93 synthetic cells, made from 4 base cells, in train. PV-DDPM was trained on SCDD 20221008, whose splits were reshuffled against our 20211104 split, and 105 E-SCDD real cells are E1 cells (handbook doc 17). Any released PV-DDPM checkpoint may have seen our test or E1 cells. Retrain generators on the 478 train cells only. The benchmark should state this rule.

## 2. Prior overlap (E, from BRIEF section 5 and handbook doc 19)

- CP100: real labelled crack components pasted onto pool cells, house model, 100% labels: n.d. on test. That closes naive copy-paste of real crack pixels. It does not close (a) a renderer that adapts crack appearance to the new background, (b) new crack shapes, widths and contrasts, (c) target-selected backgrounds (half-cut cells with scuffs) scored on E1, (d) the PF fine-tune.
- Synthetic half-cut views: n.d. on test and E1, fewer half-cut false alarms. That changed cell layout, not crack content.
- "diffusion or GAN data synthesis, physics simulation of EL" is listed as never tried.

## 3. Queries run (26)

Research MCP search_papers (OpenAlex answered; Scopus, ScienceDirect 401; S2 rate-limited; arXiv mostly timed out):
1. electroluminescence image simulation crack finite element solar cell (2015+)
2. synthetic electroluminescence images GAN solar cell defect (2020+)
3. diffusion model solar cell defect image generation (2022+)
4. EL image generation data augmentation photovoltaic defect segmentation (2020+)
5. Photovoltaic Defect Image Generator Boundary Alignment Smoothing Constraint
6. Polyp-DDPM diffusion semantic synthesis enhanced segmentation
7. simulated electroluminescence images cracked cells deep learning training physics-based (2018+)
8. 2D distributed diode network model EL image series resistance finger interruption (2012+)
9. generated near-infrared crack defect dataset StyleGAN poly-Si
10. few-shot anomaly image generation diffusion mask industrial defect segmentation (2023+)
11. diffusion synthesis crack image mask pairs thin crack segmentation augmentation (2023+)
12. EL image simulation cracked cell isolated area SPICE model finger grid (2019+, 0 hits)
13. cell cracks electrically isolated inactive area busbar fingers power loss EL (2010+)
14. synthetic images from mask-conditioned generative model, filtering noisy synthetic regions (2023+)
15. EL domain adaptation image translation CycleGAN (2020+)
16. photovoltaic electroluminescence defect image generation diffusion (2025+)
17. controllable diffusion layout-to-image synthetic data rare classes small dataset (2024+)
Snowballing: similar_papers on {PV-DDPM, CrackSegFlow, SIGAN}; get_citations on Kikelj 2020 and SIGAN.
search_snippets: 2 attempts, both rate-limited.
WebSearch (6): synthetic EL crack simulation 2025; CrackSegFlow code; FreeMask code; PV-DDPM / E-SCDD repo; SeaS code; physics-simulated EL crack training 2025/2026.
Full text read: PV-DDPM (already local), CrackSegFlow (already local), FMS2 (fetched), PDIG (fetched).

## 4. Selected papers

Score = value for our metrics (rubric in the task). Bench = value for the benchmark.

| # | id | year | venue | code | mechanism | adaptation to our data | score | bench |
|---|---|---|---|---|---|---|---|---|
| 1 | arxiv:2601.03637 CrackSegFlow | 2026 | Automation in Construction | unverified (dataset link only) | Pixel-space flow-matching mask-to-image renderer with topology-preserving mask injection and boundary gating; class-conditional mask generator by sparsity bin; rectified-flow injection of a mask onto a given crack-free background | 1-channel, 256 crops at native 512 scale from the 478 train cells; condition on the crack mask dilated to 3 px plus a source one-hot (5 sources), so it learns each source's line width; inject onto pool multi half-cut cells (1,152) and scuff cells for E1 | 70 | 55 |
| 2 | arxiv:2511.09604 PV-DDPM / E-SCDD | 2025 | arXiv | github.com/sntubix/pv-ddpm (stated in paper, not opened) | Pixel DDPM, binary layout masks concatenated with the noisy image; whole-cell EL generation for 4 cell types; same data family as ours | Retrain on our 478 train cells only (leakage); condition on the 24-class one-hot plus source; use it for inactive and other blobby classes, not 1 px cracks; feed it physics-edited layouts (row 7) | 62 | 80 |
| 3 | arxiv:2603.13659 FMS2 (SynFlow + SegFlow) | 2026 | arXiv | not released ("after acceptance") | SynFlow: mask-to-image flow matching with multi-scale mask injection, Lite-SPADE GroupNorm and boundary gating; morphology-controlled mask generator (width, branching, sparsity). SegFlow: segmentation as image-to-mask transport | Build SynFlow blocks into row 1 renderer; width-controlled masks let us sample 1.5 to 3.25 px per source; SegFlow is also a thin-structure baseline for the benchmark | 58 | 60 |
| 4 | arxiv:2609.12431 controllable crack synthesis pipeline | 2026 | arXiv | unverified | Bezier skeletons with guaranteed geometry, GAN to crack masks, dual ControlNet render; ensemble of real-trained segmenters gives pixel-wise label confidence that weights the synthetic loss; probability-of-detection vs crack width as a metric | Use the 5-seed house ensemble as the confidence model for any synthetic pair; report POD vs crack width (a90/95) on test and E1 in the benchmark | 58 | 75 |
| 5 | arxiv:2310.15160 FreeMask | 2023 | NeurIPS | github.com/LiheYoung/FreeMask (verified by web search) | Train on mask-conditioned synthetic images; drop synthetic pixels whose loss under a real-trained model exceeds a per-class threshold; generate more samples for harder masks | Filter with the house ensemble's per-class loss; hardness = per-cell crack / inactive loss on train; applies to rows 1, 2, 6, 7 | 60 | 45 |
| 6 | arxiv:2307.07245 FreeCOS | 2023 | ICCV | github.com/TY-Shi/FreeCOS (stated in abstract) | Fractal L-system curvilinear structures blended into unlabelled images with Fourier domain adaptation, plus intensity-order alignment | Procedural crack skeletons drawn with a measured dark-line profile (about 4 px FWHM, per-source contrast, finger breaks), FDA-blended onto pool half-cut cells; no generator training | 55 | 35 |
| 7 | doi:10.1002/pip.3348 Kikelj quasi-SPICE crack model | 2020 | Progress in Photovoltaics | none | Spatially resolved circuit model of active and inactive microcracks from EL damage maps; inactive area arises where cracks isolate cell parts from the busbars | Rule renderer: draw crack curve on a train cell, find regions cut off from all busbars along finger direction, darken them by source-measured inactive/active intensity ratio, label inactive; gives crack+inactive pairs that respect "inactive always touches crack" | 50 | 55 |
| 8 | arxiv:2505.06068 Siamese-Diffusion | 2025 | CVPR | unverified | Mask-only and mask+image diffusion branches trained with a noise-consistency loss so the mask-only sampler keeps real morphology | Train-time add-on to row 2 PV-DDPM; check mask adherence by house-model IoU on synthetic pairs | 45 | 40 |
| 9 | arxiv:2410.14987 SeaS | 2025 | ICCV | github.com/HUST-SLOW/SeaS (verified by web search) | Few-shot Stable Diffusion fine-tune with one normal token and several anomaly tokens; generates images and masks; +12.79% IoU for supervised segmentation on MVTec (R) | Fine-tune on rare blobby classes (splice, material, corrosion, inactive); replicate grey to 3 channels; not for cracks (latent blur) | 45 | 55 |
| 10 | arxiv:2306.10941 OCTA vessel simulation | 2024 | IEEE TMI | public per abstract, not opened | Space-colonization simulation of vessels plus three contrast adaptation pipelines; trained on simulation only, beats human-annotation-trained models on the finest capillaries (R, qualitative claim) | Moonshot: train crack on procedural cracks only (exact labels) with contrast adaptation, real labels for other classes; tests whether exact synthetic labels beat jittered human labels on faint cracks | 42 | 40 |
| 11 | doi:10.24963/ijcai.2025/162 Free Lunch image-mask alignment | 2025 | IJCAI | github.com/huan-yin/anomaly-alignment (stated in abstract) | Dual-branch generator produces image and mask with an alignment loss; the generator later gives a feedback loss to the segmenter; +5.0 IoU Real-IAD, +5.7 polyp (R) | Generator for inactive / material; mask branch absorbs label jitter instead of trusting the conditioning mask | 42 | 40 |
| 12 | arxiv:2312.05767 AnomalyDiffusion | 2024 | AAAI | github.com/sjtuplayer/anomalydiffusion (stated in paper) | Latent diffusion with spatial anomaly embedding and adaptive attention re-weighting for aligned anomaly image-mask pairs, few-shot | Most-cited few-shot anomaly generator; run as the latent-diffusion baseline in the benchmark synthetic track | 38 | 60 |
| 13 | arxiv:2408.13509 DualAnoDiff | 2025 | CVPR | "will be made available" | Two interrelated diffusion models generate the whole image and the anomaly part jointly, so the mask follows the generated defect | Same use as row 12; only if code appears | 35 | 45 |
| 14 | arxiv:2505.06117 PDIG | 2026 | IEEE TMM | unverified | Stable Diffusion with semantic concept embedding, industrial style adaptor, and box-position constraints for PV EL defects; YOLOv5 mAP +5.8 / +6.3 on time-shifted EL groups (R) | Boxes only; useful as EL evidence that synthesis helps under a domain shift, and as an EL generator baseline | 30 | 50 |
| 15 | arxiv:2104.04953 SIGAN | 2021 | arXiv | unverified | GAN removes the defect while a strong identity loss keeps the background; difference image segments the defect; also used for augmentation | Defect-free twins of cracked train cells as paired negatives, or residual map as a second input channel | 30 | 40 |

Bets: row 1 medium (E1), row 7 medium (inactive), row 10 moonshot.

## 5. Minimal experiments (one per row, short form)

All arms on PF (encoder-preserving fine-tune), 5 seeds, same commit and data as PF baseline. Synthetic share capped at 30% of each batch. Inactive decisions use module-grouped 5-fold CV over 532 train+val cells, because 3 test cells hold 59% of inactive pixels.

1. CrackSegFlow-style renderer onto half-cut pool cells: PF+syn vs PF. Metric E1 crack relF1@2 and recall@2; test crack IoU clean 49 as guard. Kill: E1 relF1@2 gain < +0.03 or test crack IoU drop > 0.01. About 30 GPU-h renderer + 6 GPU-h seg.
2. PV-DDPM retrained on 478 train, rendering physics-edited inactive layouts (row 7 masks): PF+500 synthetic inactive cells vs PF. Metric CV inactive IoU, E1 inactive IoU. Kill: CV inactive IoU gain < +0.03. About 60 GPU-h.
3. SynFlow blocks (LSGN, boundary gate, width-controlled masks) vs plain mask-concat renderer in arm 1. Metric house-ensemble IoU on rendered pairs (adherence) then E1 relF1@2. Kill: adherence gain < 0.05 IoU.
4. Confidence-weighted synthetic loss vs unweighted, inside arm 1. Metric E1 relF1@2, test crack relP@2. Kill: < +0.01.
5. FreeMask filter + hardness resampling vs unfiltered, inside arm 1 or 2. Kill: < +0.01 on the arm's main metric.
6. Procedural cracks + FDA onto half-cut pool cells: PF+proc vs PF. Metric E1 relF1@2. Kill: < +0.02. About 7 GPU-h, 1 to 2 days work. Run first; it prices row 1.
7. Rule renderer only (no diffusion) for inactive: PF+rule vs PF. Metric CV inactive IoU and BMRK inactive IoU. Kill: < +0.02. About 8 GPU-h.
8. Siamese noise-consistency in PV-DDPM training vs plain. Metric adherence IoU on synthetic inactive. Kill: < +0.05.
9. SeaS on splice / material / corrosion: PF+SeaS vs PF. Metric mIoU_rob, splice IoU (now 0.000). Kill: mIoU_rob < +0.01 and splice still 0.
10. Crack trained on procedural cracks only + real other classes vs house. Metric test relF1@2 and recall of cracks < 2% contrast. Kill: relF1@2 < 0.80 (keeps the idea only if detection holds without human crack labels).
11. Free Lunch generator for inactive vs PV-DDPM in arm 2. Metric CV inactive IoU. Kill: not better than arm 2.
12. AnomalyDiffusion as benchmark baseline: crack and inactive synthesis vs arm 1 / arm 2 at matched count. Metric as arms 1, 2. No kill; reported.
13. DualAnoDiff: only if code is public by 20 Nov.
14. PDIG: no score experiment; cite as EL domain-shift evidence.
15. SIGAN twins: add residual channel vs PF. Metric test crack IoU, E1 relF1@2. Kill: < +0.01.

## 6. Rejected (one line each)

- doi:10.3390/su15097175 Mateo-Romero 2023 DCGAN EL dataset: whole-cell images with no masks; no segmentation use.
- doi:10.1109/eeeic/icpseurope64998.2025.11169106 low-resource GAN EL generation 2025: image-level, no masks, quality metrics only.
- doi:10.1109/tase.2026.3685808 LLM-prompt DreamBooth mask diffusion for PV (TASE 2026): closest EL mask-controlled generator but paywalled, no code found, abstract gives no numbers; recheck if a preprint appears.
- doi:10.1117/12.3037042 StyleGAN NIR EL crack generation 2024: abstract only, detection not segmentation.
- doi:10.1109/jphotov.2025.3542829 DCGAN perceptual loss EL 2025, doi:10.1109/access.2025.3565002 multi-scale attention GAN 2025: classification-level augmentation.
- arxiv:2402.04031 Polyp-DDPM: the base of PV-DDPM; covered by row 2.
- doi:10.1109/ted.2015.2409058 PVONA and doi:10.1016/j.solmat.2022.111990 Kikelj 2022 luminescence model: full device simulators, too slow to build in a month; row 7 uses only their isolation logic.
- doi:10.1364/ao.555991 SPICE-simulated EL to train a 1D CNN (GaAs, 2025): shows sim-to-real for Rs estimation, wrong task and cell type.
- arxiv:2509.06693 STAGE, arxiv:2604.08301 GroundingAnomaly, arxiv:2607.29533 OSAGEN: MVTec anomaly synthesis variants without code verified; rows 9, 11, 12 cover the family.
- arxiv:2606.08033 masonry crack overlay: shows a 20/80 synthetic/real mix helps, but overlay tool is crude and RGB.
- arxiv:2605.19289 SENSE and arxiv:2312.03048 DGInStyle: natural-scene synthetic data; DGInStyle abstract not retrieved.
- doi:10.1016/j.joule.2022.05.001 Buratti 2022 luminescence reconstruction GAN for loss analysis: abstract not retrieved; possibly relevant to severity, see gaps.

## 7. Gaps

- No measured EL segmentation gain from synthetic data exists. Our arms would be the first; that is also a benchmark contribution.
- No open physics simulator that outputs EL images of cracked c-Si cells was found. Row 7 rule renderer is our own construction from the isolation logic.
- CrackSegFlow and FMS2 code is not public (verified only that the dataset link exists). Renderer must be written (U-Net with SPADE-style mask injection, flow-matching loss): about 3 to 5 days.
- PV-DDPM repo and HF link were taken from the paper, not opened. Two different HF ids appear (snt-ubix/e-scdd in arXiv text; shivahanifi/extended-scdd in a workshop copy); the handbook confirms snt-ubix/escdd.
- Severity (power loss from crack + inactive) deserves its own search: Kikelj 2020, doi:10.1051/epjpv/2026017 (crack length vs power loss, 230 mini-modules, 2026), Buratti 2022 Joule, STC-Net arXiv 2608.01714 (crack segmentation for power loss, from web search, not verified via tool).
- Snippet search was rate-limited for the whole session, so SIGAN's and SeaS's segmentation-gain tables were not checked.
