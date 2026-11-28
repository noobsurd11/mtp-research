# D17 Annotator-style, multi-rater and dataset-conditioned segmentation

Scout report, 13 Nov 2026 (second pass; replaces the 12 Nov version that was cut short by an MCP outage).
R = what a paper measured, E = what our files measured (from BRIEF), S = my judgement.

## Tool status
- Research MCP: search_papers worked (OpenAlex only; S2, arXiv, Scopus, ScienceDirect errored inside each call). search_snippets failed twice (S2 rate limit). get_paper, get_citations, similar_papers, fetch_fulltext, read_paper worked.
- Full text read: Nichyporuk 2022 (already in library), PNT-Edge (already in library), MultiTalent (already in library); fetched 3: Vorontsov 2021, Zepf 2023, Abhishek 2024 (StyleSeg).
- WebSearch: 9 calls this pass (code checks), plus 12 in the 12 Nov pass.

## Queries run
search_papers (limit 10 to 20, abstract_chars 250):
1. annotator style segmentation multiple annotators (2020+)
2. Pionono probabilistic annotator modeling segmentation (2020+)
3. multi-rater medical image segmentation calibration (2020+)
4. disentangling human error from ground truth segmentation annotator confusion matrices (2019+)
5. dataset-specific prompts universal segmentation partial labels multiple datasets (2020+)
6. probabilistic U-Net ambiguous segmentation conditional latent (2018+)
7. MultiTalent multi-dataset medical image segmentation conflicting label conventions (2020+)
8. annotation style conditioning segmentation label style different datasets (2020+)
9. learning from crowds segmentation noisy annotators confusion matrix (2025+)
10. cohort bias adaptation aggregated datasets lesion segmentation conditional instance normalization (2020+)
11. MultiTalent multi-dataset approach medical image segmentation (2023+)
12. annotator-specific heads segmentation single annotation per image inter-observer bias (2020+)
13. vessel segmentation annotation width inconsistency label noise thin structures (2020+)
14. multi-rater segmentation personalized annotator prompt (2025+)
15. crack segmentation cross-dataset annotation inconsistency label width (2020+)
16. UniSeg prompt-driven universal segmentation task prompt multi-dataset (2022+)
17. learning semantic boundaries from noisy annotations active alignment thin boundary labels (2019+)
18. misaligned segmentation labels spatial transformer label registration noisy annotation offset (2020+)
19. dataset embedding conditioning joint training heterogeneous segmentation datasets label bias (2025+)
20. uncertainty-aware edge detection multiple annotators label distribution BSDS (2022+)
21. controllable line thickness segmentation conditioning annotation granularity curvilinear (2021+)
22. multi-head network per annotator site-specific decoder heads segmentation multi-site (2021+)
Plus the 12 Nov pass (10 searches, overlapping 1 to 9).
search_snippets (2, both rate-limited): annotator CMs with one label per image; biased vs random label error.
Snowballing: get_citations on arxiv:2210.17398 (19 citing), arxiv:2007.15963 (30 of 100), arxiv:2303.15850 (10); similar_papers on {2210.17398, 2303.15850, 2007.15963}. Snowballing found MuGE (CVPR 2024), Vorontsov 2021, the cohort-bias paper and the TPAMI transition-matrix paper.
WebSearch (code checks): MuGE, Pionono, Zepf, PNT-Edge, MultiTalent, Nichyporuk, Zhang 2020 (+ 12 Nov: D-Persona, TAB, spatial correction, U-Harmony and others).

## Why this direction fits our data (S)
- On our data "annotator" is close to "source": each cell has one label, and the 5 sources use different crack widths (ARTS 1.5 px, CFVS / CSIR 1.75, BMRK 3.0, SDLE 3.25; E). A source-blind model must either infer the source from the image or predict one compromise width. Source ID is known at test and E1 time (filename prefix), so conditioning on it is legal; the benchmark should report "source-aware" next to "source-blind".
- R (Vorontsov 2021): segmentation nets are robust to unbiased label errors (random warp) but lose about 10% Dice under a constant 5 px shift (biased error). Width and any constant offset per source are biased errors in this sense; the 1 px jitter within a source is mostly unbiased. So the part of the crack IoU loss that conditioning can recover is exactly the biased, per-source part.
- R (Nichyporuk 2022, 2,340 patients, 6 trials): naive pooling lost 0.01 to 0.03 Dice against single-trial models; trial-conditioned CIN matched or beat every single-trial model (for example 0.766 to 0.787, 0.754 to 0.789).
- R (Zepf 2023, ISIC, 179 train pairs over 3 styles): style-conditioned Probabilistic U-Net IoU 0.77 / 0.78 / 0.76 per style versus 0.65 / 0.65 / 0.69 pooled. Evidence on small data, but blob lesions, not 1 to 2 px lines.
- Limits (S): conditioning fixes the source convention (width, any constant offset), not the within-source jitter (two annotations of a cell agree at IoU 0.21 to 0.26, E). Inactive labels are clean (1 px shift IoU 0.94, E), so expect little there except perhaps BMRK. E1 is recall-limited (70% of crack pixels get p < 0.001, E); conditioning will not fix that.
- The model may already infer source from appearance (BMRK padding and downscaling, SDLE contrast). The zero-GPU diagnostics below decide how much room there is.

## Zero-GPU diagnostics (run first; they decide the whole direction)
D0a. Per-source predicted crack width (area / skeleton length) on out-of-fold predictions of the module-grouped 5-fold CV roots (not test), against per-source label width. Flat predicted widths across sources = room for conditioning.
D0b. Per-source signed offset of label skeleton to the darkest ridge, separately in x and y, on train labels only. A non-zero per-source mean (for example a +0.5 px rasterisation offset in one source) is a biased error that a shift-aware conditional head (PNT-Edge style) can remove; a zero mean means only width matters.
D0c. Linear probe for source on frozen house encoder features (bottleneck, global pool). Accuracy near 100% for BMRK / SDLE and low for CFVS vs CSIR tells which sources need explicit conditioning.
D0d. Post-hoc width match on CV OOF: per-source crack logit bias, or skeletonise and redraw at the source median width. This is the zero-training control every learned arm below must beat. It differs from the failed "per-module thresholds" (modules, not sources).

## Selected papers

| # | id | year | venue | code | mechanism | adaptation (our data) | score | bench |
|---|---|---|---|---|---|---|---|---|
| 1 | arxiv:2210.17398 (+ arxiv:2108.00713) | 2022 | MELBA (+ MICCAI DART 2021) | none found | Conditional instance norm: per-dataset scale / shift parameters in every norm layer let one network learn each dataset's annotation style; few-shot adaptation to a new style by refitting only those parameters | 5-way source ID drives FiLM / conditional-BN scale and shift in the U-Net++ decoder blocks only (encoder shared, PF schedule). Init gamma 1, beta 0. 10% source dropout to a 6th "consensus" ID for source-blind use and for WattCycle's future rig. At test condition on filename source; E1 uses CSIR / BMRK | 70 | 55 |
| 2 | arxiv:2303.14444 | 2023 | MICCAI | github.com/MIC-DKFZ/MultiTalent (web) | Treat each dataset's class as its own class even when the name matches; one sigmoid output per (dataset, class); loss only on the outputs that dataset labels | 5 per-source crack channels (and optionally per-source inactive) as sigmoid outputs next to the 24-class softmax with crack removed or kept as a shared channel; at test read the image's source channel. Same head admits UCF-EL "crack" (crack + inactive region) as its own channel for joint training, which BRIEF section 5 lists as open | 68 | 60 |
| 3 | arxiv:2303.15850 | 2023 | ICLR | none found | Condition stochastic segmentation models (Prob. U-Net, SSN) on a discrete label-style variable, p(a given x, style) instead of p(a given x) | Style = source. Cheapest form is #1 with a one-hot added to the decoder; the stochastic part adds a crack sample distribution per source, useful for calibrated crack uncertainty in severity reports. R on 179 train pairs gives the small-data evidence for #1 | 62 | 45 |
| 4 | doi:10.1109/cvpr52733.2024.02452 | 2024 | CVPR | github.com/ZhouCX117/UAED (MuGE scripts, web) | MuGE: a granularity value is estimated from each individual edge annotation and injected into multi-scale and high-frequency features, so one edge detector outputs thin or coarse maps on demand | Replace the discrete source ID by a continuous per-cell label width w (crack area / skeleton length of that cell's label, 1 to 3.5 px) fed through FiLM. Captures within-source annotator variation too. At test set w to the source median, or tune w per source on CV folds. Thin-line evidence (edges), closest domain in this direction | 64 | 35 |
| 5 | arxiv:2007.15963 | 2020 | NeurIPS | github.com/moucheng2017/Learn_Noisy_Labels_Medical_Images (web) | Two coupled CNNs: one for the latent true mask, one for per-pixel, image-dependent confusion matrices per annotator; trace regularisation makes annotators "maximally unreliable" so the latent mask absorbs the shared truth; works with one label per image | Annotator = source; CMs over {background, crack, inactive, other} to keep memory low. Score the source-CM output on strict IoU against source labels; score the latent output on relF1@2 and E1 | 55 | 45 |
| 6 | arxiv:2307.14070 | 2023 | ACM MM | github.com/DREAMXFAR/PNT-Edge (web) | Label noise on thin edges modelled as a displacement field: a small FCN predicts per-pixel shifts that warp the clean prediction into the noisy label (STN sampler), with smoothness and local-density priors; detector then fits clean labels. R: SBD ODS-F +2.4 / +4.7 points over CASENet-S | Make the shift head source-conditioned (#1 FiLM). Train detector + shift on crack only. Use the warped output for strict IoU on source labels, the unwarped one for relF1@2. Only worth it if D0b shows a per-source offset | 52 | 30 |
| 7 | arxiv:2408.02787 | 2024 | ISIC workshop (LNCS 2025) | github.com/sfu-mial/StyleSeg (from paper) | StyleSeg: M output heads plus a style classifier on (image, mask); winner-take-all plus classifier-weighted Dice discovers M styles without annotator IDs | Within a source there may be several annotators. Use M = 3 crack heads; after training, take each source's majority style from train cells and use that head at test. Combine with #1 (source ID) so heads model within-source styles | 45 | 30 |
| 8 | arxiv:2403.13417 | 2024 | CVPR | github.com/ycwu1997/D-Persona (from abstract) | Stage 1 Prob. U-Net on multi-rater masks builds a shared latent space; stage 2 attention heads query expert-specific prompts | Two "raters" per cell exist for crack / inactive: the 2021 original masks and the 2022 revised masks. Train with version as rater, output the revised persona. Uses the old labels instead of discarding them | 45 | 40 |
| 9 | arxiv:2307.11397 | 2023 | ICCV | not found (web) | Pionono: each rater is a Gaussian in a latent space; a sample is fused with image features to give that rater's mask; variational inference end to end | Rater = source (5 Gaussians); sampling models within-source jitter. Small head on the house decoder; rater mean at test | 42 | 35 |
| 10 | arxiv:2306.01340 | 2023 | MICCAI | github.com/Merrical/TAB (web, 12 Nov) | TAB: one learnable transformer query per annotator extracts preference features; also models stochastic error | One query per source in a light transformer block at the U-Net++ bottleneck. Old PyTorch, re-implement the head | 40 | 35 |
| 11 | doi:10.1109/cvpr52733.2024.01064 | 2024 | CVPR | unverified | Hermes: learned task and modality prior tokens let one model train jointly on many partially labelled datasets | Prior tokens = {5 BenchmarkEL sources, UCF-EL, MultiSolSegment}. Alternative to #2 for joint multi-dataset training | 40 | 40 |
| 12 | arxiv:2601.14605 | 2026 | ISBI | unverified | U-Harmony: normalise then de-normalise features per domain, with a domain-gated head that picks the domain without an ID at inference | Source-gated decoder for cells of unknown source (benchmark new-module track, WattCycle rig). Compare gate-inferred source with the true source on E1 | 38 | 35 |
| 13 | arxiv:2410.13822 | 2024 | arXiv | unverified | Post-training style conversion: a linear probe detects dataset origin from encoder features; adversarial input perturbation toward a chosen dataset makes a frozen model segment in that style | Bold bet, no retraining: probe source on the frozen house encoder (D0c), then push each test image toward its own source (or toward ARTS for thin output) with a few PGD steps; measure crack width and IoU | 35 | 25 |
| 14 | arxiv:2107.02189 | 2021 | MICCAI UNSURE | n/a | Evidence paper: random (unbiased) label errors barely hurt; constant shifts (biased) cost about 10% Dice at 5 px | Not an arm. Justifies D0b and tells the benchmark to report biased-error sensitivity (per-source width / offset) separately from jitter | 30 | 55 |
| 15 | arxiv:2409.09893 | 2024 | arXiv | unverified | Class-name language embeddings plus label-space-specific queries handle inconsistent class semantics across datasets | Map UCF-EL / MultiSolSegment / PVEL-S classes onto our 24 classes for joint training and for a cross-dataset benchmark track | 32 | 45 |
| 16 | arxiv:2006.06015 | 2020 | NeurIPS | unverified | Stochastic Segmentation Networks: low-rank Gaussian over logits gives spatially coherent samples | Low-rank Gaussian crack head (base of #3). Mainly calibrated crack uncertainty for severity and review flags | 28 | 40 |
| 17 | arxiv:2307.02191 | 2025 | MedIA | unverified | Evaluate models when ground truth is uncertain: aggregate annotations into a distribution, report metrics with uncertainty | Benchmark design: treat crack ground truth as a distribution (2021 and 2022 label versions, 2 px band); report strict IoU, relF1@2 and an interval | 15 | 70 |

## Minimum experiments (priority order)
0. D0a to D0d above. No GPU. Kill the whole learned direction if D0a shows predicted widths already within 0.15 px of label widths in every source and D0d gains < +0.005 crack IoU on CV.
1. #1 source-FiLM decoder on house PF, 5 seeds, vs house PF 5 seeds. Metrics: clean-49 crack IoU; per-source crack IoU in 5-fold CV; BMRK inactive IoU. Kill if 5-seed mean crack IoU gain < +0.012 and no source gains >= +0.03 in CV. About 5.5 GPU-h (+16 for CV).
2. #2 per-source crack channels, same protocol and kill line. About 5.5 GPU-h. Then the joint UCF-EL variant (own channel) judged on E1 crack recall and relF1@2, kill if E1 relF1@2 gain < +0.03.
3. #4 continuous width conditioning, same protocol; test w = source median vs w tuned on CV. About 5.5 GPU-h.
4. #6 only if D0b finds a per-source offset > 0.3 px; #5 if #1 to #3 show a gain (CM model as the probabilistic version). About 8 GPU-h each.

## Rejected (one line each)
- arxiv:2308.02498 spatial correction (ICLR 2023): label correction, not style; covered by D15 / D16.
- arxiv:2511.08046 ProSona (ISBI 2026): text-prompt persona interpolation needs several expert masks per image.
- arxiv:2512.00748 probabilistic multi-rater (2025): needs multi-rater masks per image; #8 and #9 cover it.
- arxiv:2605.08210 harmonized feature + frequency-prompt rater conditioning (2026): #1 with more parts, no code found.
- doi:10.1016/j.patcog.2023.109400 (Zhang 2023): journal extension of #5.
- doi:10.1016/j.media.2023.103028 (Liao 2023, MPN): predecessor of #10, same mechanism.
- doi:10.1109/cvprw53098.2021.00203 D-LEMA: ensembles from multiple annotations per image; we have one.
- doi:10.1109/cvpr52729.2023.01488 UAED: needs several edge annotations per image (BSDS); we have one.
- doi:10.1109/tpami.2024.3388209 annotator- and instance-dependent transition matrices: classification, not dense.
- arxiv:2605.02437 multi-rater calibrated models: calibration only, needs multi-rater data.
- doi:10.1109/iccv51070.2023.01934 CLIP-driven universal model: organ / tumour class prompts, our label spaces are small; #2 does the same job more simply.
- doi:10.1109/cvpr52733.2024.01061 Tyche: in-context stochastic segmentation; needs a context set per task, no gain path for strict IoU.

## Gaps
- No paper found that conditions on annotator style for 1 to 2 px lines or cracks. MuGE (edges) is the closest. Transfer from blob lesions to lines is untested.
- search_snippets was rate-limited, so per-paper evidence beyond abstracts comes only from the 6 full texts read.
- Code for Nichyporuk (#1), Zepf (#3), Pionono (#9), Hermes (#11), U-Harmony (#12) not found or not verified.
- Sub-directions worth their own search: (a) label version as rater (2021 vs 2022 masks), (b) source or style embeddings for mixing foundation-model pseudo-labels with human labels, (c) per-source subpixel offset estimation from the ridge (D0b) as a label-processing step rather than a model change.
