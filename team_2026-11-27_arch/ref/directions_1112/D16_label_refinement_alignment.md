# D16: Automatic label correction and alignment to image evidence

Scout: D16 literature agent, 13 Nov 2026. Literature phase only: no servers, no test data read.
Tags: R = what the paper measured, E = what our files measured (from BRIEF), S = my judgement.

## Why this direction (E, from BRIEF section 2)
- Crack labels: 1 to 2 px lines on a ~4 px dark ridge; half of label points sit > 1 px from the darkest ridge.
- Label width differs by source: ARTS 1.5, CFVS/CSIR 1.75, BMRK 3.0, SDLE 3.25 px.
- 1 px shift of a perfect mask gives test crack IoU 0.56; two annotations agree at IoU 0.21 to 0.26.
- 70% of crack IoU loss lies within 2 px of ground truth. The 2022 relabelling gave +0.05 to +0.08 crack IoU, more than any method.
- Never tried: automatic label refinement, noise-robust training, source-style modelling. Tried and n.d.: offset-tolerant CE.

Key caution (S): test labels carry the same jitter. Snapping TRAIN labels to the ridge sharpens the training signal but the strict test IoU is still scored against jittered labels. Gains on strict IoU are therefore bounded; gains are more likely on relF1@2, recall of faint cracks, and on a re-scored test set with snapped labels (a benchmark question). The source-width part (match each source's convention at inference) is what can move strict IoU on the original labels.

## Queries run (32 total)
search_papers (OpenAlex only answered; S2, arXiv, Scopus rate-limited or 401):
1. label alignment misregistered annotations road extraction (2020+)
2. noisy map labels alignment deep learning building segmentation (2020+)
3. segment anything mask refinement noisy labels (2023+)
4. learning to segment with misaligned annotations label offset correction (2018+)
5. self-correction noisy labels semantic segmentation label refinement during training (2020+)
6. active contour snake refinement of noisy annotations curvilinear structures (2019+)
7. crack segmentation inaccurate annotations noisy labels (2020+)
8. imprecise centerline annotations thin structure delineation training (2019+)
9. learning to segment from noisy annotations spatial correction Markov label noise (2021+)
10. joint registration and segmentation misaligned training labels deformation field (2020+)
11. label refinement noisy segmentation annotations (2025+)
12. disentangling human error from ground truth segmentation annotator confusion matrices (2020+)
13. annotator style modeling segmentation multiple annotators personalized labels (2022+)
14. simultaneous edge alignment and learning noisy edge labels (2018+)
15. Devil is in the edges learning semantic boundaries from noisy annotations (2018+)
16. adaptive early-learning correction segmentation noisy annotations (2021+)
17. noisy labels thin curvilinear structure segmentation vessel crack label noise robust (2024+)
18. SAM pseudo label refinement crack segmentation (2024+)
19. multi-dataset segmentation inconsistent annotation protocols dataset-conditioned heads (2021+)
20. automated detection of label errors in semantic segmentation datasets (2022+)
21. denoising diffusion label refinement segmentation mask image-conditioned (2023+)
22. misaligned labels segmentation alignment correction (2025+)

Snowballing: get_citations on Rill-Garcia 2022, Yao 2023 (SC), Oner 2022; similar_papers on {Oner 2022, PNT-Edge, Rill-Garcia 2022} (this surfaced Crispness TIP 2023 and Xu CVPRW 2023).
search_snippets: 3 attempts, all rate-limited.
WebSearch (7): Align and Segment code; CVPR 2026 offset correction (OMAF); Rill-Garcia code; SC code; STEAL code; Crispness code; Zhang 2020 code.
Full text read: Oner 2022 (method, results), Yao 2023 (method), PNT-Edge (results), Crispness (method).

## Selected papers

| # | id | year | venue | code | mechanism | adaptation to our data | score | bench |
|---|---|---|---|---|---|---|---|---|
| 1 | doi:10.1109/tip.2023.3289296 (arXiv 2306.15172) Crispness | 2023 | IEEE TIP | not found (unverified) | Keep only the part of each human edge label that coincides with an over-detected low-level edge map (Canny on several blurs); inpaint gaps; ignore unmatched label pixels. R: crispness 17.4% to 30.6%, ODS +12.2% on Multicue with PiDiNet. | Replace Canny with a dark-ridge map (Hessian / min-intensity along the label normal, scales 1 to 3 px). Move each crack skeleton point to the darkest pixel along its normal within 2 px, reconnect, redraw at a canonical width; pixels with no ridge support within 2 px keep the original label (7% of cracks are < 2% darker; do not drop them). Then optionally redraw at each source's median width. | 74 | 50 |
| 2 | doi:10.1109/tmi.2022.3193072 (arXiv 2112.02781) Oner et al. | 2022 | IEEE TMI | github.com/doruk-oner/AdjustingAnnotationswithSnakes (stated in paper) | Annotation centerline is a snake (graph of vertices) that deforms during training toward the network's predicted distance map, with elasticity and spring terms that keep it smooth and keep its topology. R: better APLS/TLTS than training on original annotations and than NR-Dice, QAM, DS6 on 3 delineation sets; robust as synthetic deformation grows; pixel quality about equal. | 2D version: skeletonize each crack label into polylines, add an auxiliary truncated-distance regression head to U-Net++, update the snake every few steps (SnakeFast) with max displacement 2 px; train the crack channel on the dilated adjusted snake. Source-specific redraw width at the end. | 66 | 35 |
| 3 | doi:10.1016/j.neucom.2022.01.051 Rill-Garcia et al. | 2022 | Neurocomputing | not found | Crack labels with tolerance-free scoring; studies weakly supervised label noise correction for inaccurate crack annotations; Syncrack synthetic benchmark with controlled label noise. R: inaccurate labels cost up to 20% F; corrected labels gain up to 12% on Syncrack; also helps CrackForest, Aigle-RN. | Closest domain (thin cracks, strict pixel metric). Use as the reference recipe: train house model, use its own confident predictions within 2 px of the label to replace the label, retrain. Also copy the Syncrack idea for the benchmark: synthetic EL cracks with exact labels plus controlled jitter to measure what jitter costs. | 68 | 55 |
| 4 | arxiv:2007.15963 Zhang et al. (NeurIPS 2020) | 2020 | NeurIPS | github.com/UCLBrain/Modelling_Segmentation_Annotators_Pytorch (per arXiv PDF, unverified live) | Two coupled CNNs: one predicts the latent true label, the other a pixel-wise confusion matrix per annotator; trace regularizer makes annotators maximally unreliable so the true label is disentangled. R: beats baselines on MSLSC, BraTS, LIDC, strongest when annotations are few and disagree. | Treat each of the 5 sources as an annotator. The per-source spatial confusion head learns how each source widens or shifts crack labels (BMRK 3.0 px vs ARTS 1.5 px). Train on the 478 cells; at test score both the latent head and the source-styled head (source is known from the filename for test and E1). | 62 | 45 |
| 5 | arxiv:2308.02498 Yao et al. Spatial Correction (ICLR 2023) | 2023 | ICLR | github.com/michaelofsbu/SpatialCorrection (from paper, unverified live) | Models label noise as a Markov boundary process with a systematic bias; estimates the bias as a mean signed-distance offset between the model's prediction and a small clean set, then shifts the logit-level boundary to correct training labels; 1 iteration usually enough. | No clean set exists, so estimate the bias per source relative to the ridge-snapped labels of #1 on val, or relative to a chosen reference source. Use it in two ways: correct training labels per source, and apply the per-source offset at inference to match each source's label width. | 60 | 50 |
| 6 | arxiv:2307.14070 PNT-Edge | 2023 | ACM MM | github.com/DREAMXFAR/PNT-Edge (stated as "will be available", unverified) | Pixel-wise Shift Learning module predicts a displacement field that warps the clean prediction into the noisy label; loss is on the warped output; the unwarped output is used at test. R: SBD ODS-F +2.4 / +4.7 points over CASENet-S, competitive with STEAL; thinner edges. | Add a small shift head (2 channels, max 2 px, smoothness prior) conditioned on source ID, so it learns each source's offset and width. Warp crack probability before CE + Dice; predict unwarped. Honest note: offset-tolerant CE (fixed tolerance) was n.d. here; a learned, source-conditioned field is a different mechanism but related. | 55 | 35 |
| 7 | arxiv:2110.03740 ADELE | 2022 | CVPR | github.com/Kangningthu/ADELE (stated in paper) | Detects per class when the network leaves the early-learning phase and starts memorizing noise, then replaces labels with confident predictions for that class; multi-scale consistency regularizer. R: SOTA on PASCAL VOC with WSSS noisy labels and on synthetic medical noise. | Per-class timing matters here: crack memorizes jitter late and slowly, gridline / splice / edge_dark have incomplete labels. Apply correction only to crack and the weak structural classes, only within 2 px of the original label for crack. 20k-step schedule makes the memorization curve easy to log. | 58 | 55 |
| 8 | doi:10.1016/j.engappai.2026.115849 Ahmed et al. | 2026 | Eng. Appl. AI | not stated | Foundation-model masks used only inside a narrow trust region around the expert label, with an instance IoU gate and minimal closing; unconstrained FM masks as labels degrade results. R: modest gain in 5-fold CV on ultra-thin bone fractures; MedSAM unconstrained supervision hurt. | Use our 5-seed ensemble (or a SAM2 / DINOv3 refiner) as the proposal; accept a refined crack component only if it lies within the 2 px band of the label and its IoU with the dilated label exceeds a gate. Supports keeping refinement anchored to the original labels. | 57 | 30 |
| 9 | doi:10.1016/j.ress.2025.110909 SelectSeg | 2025 | Reliab. Eng. Syst. Saf. | not found | Deep ensemble uncertainty flags unreliable crack annotations; flagged images become unlabeled data for SSL; selective prediction abstains on hard cases. R: beats baselines on real crack sets with noisy annotations (numbers not read, paywalled). | We already have 5-seed ensembles: rank train cells (and components) by ensemble disagreement with the label, demote the worst 5 to 10% (the audit flagged 24 of 239 cells) to unlabeled or ignore-region status. Differs from past SSL runs: it removes noisy labels rather than adding pool data. | 50 | 35 |
| 10 | arxiv:2509.17951 DragOSM | 2025 | arXiv | github.com/likaiucas/DragOSM (stated in abstract) | Label alignment as iterative denoising: train a model to move randomly perturbed labels back to their position (Gaussian perturbations), then apply it iteratively to real misaligned labels. R: new ReBO dataset, 179k buildings. | BOLD BET. Train a small "label snapper" (input: EL image + crack label perturbed by 1 to 3 px shifts and width changes; target: the unperturbed label). Because annotator jitter is random but the ridge is consistent, the snapper learns E[label position given image], which should sit on the ridge. Apply to all train labels, retrain house model. | 45 | 25 |
| 11 | arxiv:1904.07934 STEAL | 2019 | CVPR | github.com/nv-tlabs/STEAL (verified listing; training code presence unverified) | Thin-boundary loss forcing max response along the normal of each label edge, plus level-set active alignment of labels during training. R: +4% MF(ODS), +18.6% AP over CASENet on SBD; refines coarse labels. | The "max response along the normal" loss maps directly to cracks: along each label normal, the predicted crack probability should peak once. Use as an auxiliary loss on crack only, with normals from the label skeleton. The level-set alignment part overlaps with #2. | 50 | 30 |
| 12 | arxiv:2207.06104 Rottmann and Reese | 2023 | WACV | not checked | Component-level uncertainty meta-classifier flags label errors (missing or spurious components). R: detects most dropped labels on Cityscapes and CARLA with controlled false alarms. | Run on train + val with the existing ensemble to rank missing crack / inactive components and spurious ones; output an audit list instead of auto-fixing. Main value is benchmark hygiene: flag test cells like CSIR_00070_r8_c4 automatically. | 40 | 62 |
| 13 | doi:10.1109/cvprw59228.2023.00464 Xu, Zou, Okatani | 2023 | CVPRW | not found | Synthesizes annotation errors on 1 px crack curves and measures their effect. R: under-annotation hurts more than over-annotation; polyline approximation has modest impact. | Guidance: any refinement should never delete label pixels it cannot place (keep originals where ridge support is weak); a benchmark should report recall-oriented tolerant metrics. | 35 | 58 |
| 14 | arxiv:2502.06756 SAMRefiner | 2025 | arXiv | github.com/linyq2117/SAMRefiner (stated in abstract) | Mines points, elastic boxes and Gaussian masks from coarse masks to prompt SAM; split-then-merge for multi-object; IoU adaptation step. | Weak fit for 1 to 2 px cracks (SAM masks are blob-oriented; #8 found unconstrained MedSAM hurts on thin fractures). Possible fit for inactive, material, edge_dark and splice region boundaries. Test only on those classes. | 30 | 30 |
| 15 | CVPR 2026 OMAF, Xu et al. "Revisiting the Necessity of Full Accuracy" | 2026 | CVPR | github.com/dayunyan/OMAF-Building-Alignment (per third-party summary, unverified) | Object-level offset estimation by differentiable self-alignment with edge and variance constraints, Bayesian confidence filtering, then an offset regression network. Details from a summary page, not the paper. | Per crack component offset (not per pixel): estimate the shift that best puts each label component on the ridge, keep only confident shifts. A component-level alternative to #1. No paper id from the Research MCP: cite as CVF open access, unverified. | 35 | 20 |

Notes on ids: #15 has no DOI/arXiv id returned by a tool; the CVF page was found by WebSearch only.

## Minimum experiments (all on the house model, 5 seeds, 100% labels, clean-49 test + E1, as in BRIEF section 3)
- E-check first (no training, val only): measure predicted crack width per source vs label width per source on val. If the house model already matches each source's width, the source-width arms (#4, #5, #6) have less room.
- A1 ridge snap (#1): train on snapped labels, redrawn at each source's median width. Baseline: house model. Metrics: crack IoU on original test labels, relF1@2, components found >= 20 px; secondary: crack IoU on snapped test labels. Kill: original-label crack IoU below baseline by > 0.012 and relF1@2 not up by >= 0.01. Cost about 6 GPU-h.
- A2 snake adjustment (#2): same evaluation. Kill as A1. Cost about 10 to 15 GPU-h plus 3 to 5 days of code.
- A3 source-styled output (#4 or #5): train house model + per-source style head, score the source-styled output. Kill: crack IoU not above baseline by 0.012 on clean-49.
- A4 ADELE (#7): baseline house; kill if crack IoU and mIoU_rob both n.d.
- A5 ensemble-flagged demotion (#9): baseline house; kill if crack IoU n.d. and no E1 change.
- A6 label snapper (#10): kill if the snapper's output on val moves labels less than 0.3 px on average toward the ridge, before any segmentation run.

## Rejected (one line each)
- doi:10.1109/tpami.2020.3048039 Self-Correction for Human Parsing: label refinement by model averaging over cycles; generic, close to ADELE/EMA, no thin-structure evidence.
- arxiv:2005.13180 Fobi et al. Alignment Correction Network: global shift of building labels, needs paired aligned labels.
- arxiv:2607.10841 Align and Segment (2026): building-level misalignment; no abstract returned by the tool, code not found.
- doi:10.1109/icpr48806.2021.9412054 Henry et al.: topological (missing road) noise, not position jitter.
- arxiv:2406.10891 Kimhi et al. COCO-N: instance-segmentation noise benchmark; reference for how to simulate noise, no method.
- arxiv:2504.14795 Tadokoro et al.: Bayesian spatially correlated noise; similar aim to #5 with less evidence.
- arxiv:2503.12218 Adaptive label correction (medical): generic pixel-flip noise, no thin structures.
- arxiv:2212.05566 YoloCurvSeg: learns from one noisy skeleton via synthesis; our labels are already full.
- doi:10.1016/j.media.2025.103489 UMA-Net: multi-annotation uncertainty; we have one annotation per cell.
- arxiv:2312.12425 SegRefiner, arxiv:2407.09918 DiffRect: diffusion mask refiners trained on object masks; heavy for 1 to 2 px lines.
- doi:10.1109/lsp.2024.3358078 vessel edge-buffer self-correction: very close idea (treat the label boundary band separately) but paywalled and no code found; folded into A1 / A4 design.
- arxiv:2403.13417 D-Persona, arxiv:2306.01340 TAB: multi-rater style heads; #4 covers the same idea with code.

## Gaps
- No paper found that snaps thin labels to an intensity ridge in EL or any inspection domain; A1 is our own adaptation of Crispness.
- No evidence found on whether models trained on refined labels score higher against the ORIGINAL noisy test labels (all papers score against clean or re-annotated labels). This is exactly our case and needs E.
- search_snippets was rate-limited all session; quantitative details of SelectSeg, Rill-Garcia and Xu CVPRW were not read.
- Code for Rill-Garcia, Crispness, SelectSeg not found. STEAL repo may hold only inference code.
- Sub-direction worth its own search: evaluating thin-structure segmentation against noisy ground truth (benchmark scoring with label uncertainty, e.g. scoring against snapped labels or with per-source tolerance).
