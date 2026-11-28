# D26 Refinement stages and coarse-to-fine cascades

Scout: literature only. No servers, no test data read. R = what a paper measured, E = what our files measured (from BRIEF), S = my judgement.

## Queries run

Research MCP `search_papers` (year_from 2020 unless noted; Scopus / ScienceDirect returned 401 and Semantic Scholar was rate-limited for the whole session, so results come mostly from OpenAlex + arXiv):
1. SegRefiner diffusion segmentation refinement
2. CascadePSP class-agnostic segmentation refinement high resolution
3. coarse-to-fine thin structure segmentation refinement crack
4. vessel segmentation refinement network error correction cascade
5. boundary patch refinement segmentation
6. mask refinement segment anything coarse mask prompt (2023+)
7. SegFix model-agnostic boundary refinement offset
8. iterative refinement retinal vessel segmentation missing segments IterNet
9. PointRend uncertain point refinement segmentation rendering
10. diffusion model crack segmentation (2023+)
11. segmentation refinement 2025 model-agnostic mask refiner (2025+)
12. learning to refine noisy boundary annotations alignment semantic edges (2019+)
13. road extraction connectivity refinement network gaps iterative
14. denoising autoencoder post-processing segmentation refinement anatomical plausibility (2019+)
15. two-stage crack detection then segmentation patch high resolution (2021+)
16. conditional random field layer thin structure segmentation deep learning
17. SAM refine crack mask prompt from coarse segmentation thin structure (2024+)
18. cascaded refinement stage segmentation small dataset second network input image and probability map
19. segmentation error correction network predicts corrections to initial prediction
20. thin structure segmentation refinement vessel topology post-hoc refiner (2025+)
21. discrete diffusion mask refinement medical segmentation low data (2025+)
22. crack segmentation refinement connectivity gap completion post-processing network (2024+)
23. auto-context stacked segmentation network previous stage probability map input (2019+)

Snowballing: `get_citations` on SegRefiner (41 citing papers; found Deep Closing, Minimum Strip Cuts, BRNCA, UnfoldCRF line), `similar_papers` on Chen 2024 label refinement + rNCA (found VSR-Net, Med-NCA, MAE mask refinement).
`search_snippets`: 2 attempts, both refused (Semantic Scholar rate limit).
Full text read (arXiv): SegRefiner (method, training data, implementation), rNCA (training, DRIVE comparison table, appendix C).
WebSearch / WebFetch (9): code checks for SegRefiner, SAMRefiner, CascadePSP, rNCA, Chen 2024, Universal Topology Refinement, VSR-Net, IterNet, CurvSegFlow; one fetch for the Minimum Strip Cuts paper (no abstract available).

## The one result that shapes this whole direction

R (rNCA, arXiv 2512.13397, Table 1 and App. C): on DRIVE (20 retinal images, thin vessels, 3 folds), every generic refiner trained on the same U-Net predictions gave no Dice gain: SegFix 0.761 -> 0.759, SegRefiner 0.761 -> 0.760, DenseCRF 0.761 -> 0.760, and a conditional U-Net refiner (image + initial mask, residual) 0.761 -> 0.761. Only the iterative local refiner (rNCA) moved Dice to 0.777 and clDice 0.802 -> 0.820, and cut beta0 (fragment count) error by about 45%. The gain held on masks from an unseen Swin model.

S: so a one-pass refiner on thin structures mostly re-learns the base model. What helps is (a) iterative, local, topology-driven repair and (b) training on error patterns the base model actually makes. On our data, 70% of crack IoU loss lies within 2 px of GT (E), which no refiner can fix against jittered test labels. The realistic targets for D26 are: fragments and missed faint continuations of detected cracks (component recall, relR@2), crack width calibration per source, inactive region boundaries and region growth from cracks, and crack / gridline / inactive class confusions. E1 pixels with p(crack) < 0.001 carry no signal for a mask refiner; refiners will not fix E1 recall beyond gap-bridging.

## Key adaptation shared by every learned refiner here

- The house model's predictions on its own 478 train cells are near-perfect, so a refiner trained on them learns nothing. Train the refiner on out-of-fold predictions: the module-grouped 5-fold roots over the 532 train + val cells already exist (BRIEF section 4.5). One base model per fold (5 x 1.1 GPU-h) gives realistic error masks for all 532 cells.
- Add synthetic errors on GT: random breaks along the crack skeleton, deletion of the lowest-contrast segments, 1 px shifts toward / away from the dark ridge, width changes to other sources' conventions (ARTS 1.5 px ... SDLE 3.25 px), and gridline-like false fragments.
- Input: 1-channel EL + softmax probabilities (at least crack, inactive, gridline, background) + optional source id. Output: corrected probabilities, scored with the house metrics.
- Score every arm by 5-fold CV over the 532 cells plus clean-49 test and E1; this is the better instrument from BRIEF section 4.5.

## Selected papers

| # | id | year | venue | code | mechanism | adaptation (short) | score | bench |
|---|---|---|---|---|---|---|---|---|
| 1 | arxiv:2512.13397 rNCA | 2025 | MIDL 2026 | github.com/maltesilber/rnca (search hit, not opened) | Neural cellular automaton refiner: small local update rule, iterated 32-250 steps on image + mask, trained on imperfect masks, reconnects broken thin structures and prunes fragments | Train on out-of-fold crack probability maps from the 5 fold models, 64 px patches around predicted or GT cracks, plus synthetic skeleton breaks; refine crack channel only, keep argmax for other classes | 62 | 45 |
| 2 | arxiv:2610.30007 BRNCA | 2026 | arXiv | not found | Multiclass NCA on the class-probability simplex (log-space Aitchison update + hidden channels) on top of a frozen segmenter; +2.36 boundary IoU, +8.5 on the most irregular class | Multiclass version of #1 for our 24-class softmax; lets one refiner trade crack / inactive / gridline pixels instead of a binary crack repair | 52 | 30 |
| 3 | arxiv:1912.05763 IterNet | 2020 | WACV | github.com/conscienceli/IterNet | Base U-Net followed by several weight-shared mini-U-Nets that read the previous segmentation and re-segment it, deep supervision on each; built for 20-40-image vessel sets | End-to-end: append 3 weight-shared mini-U-Nets on U-Net++ output (probabilities + last decoder features), CE + crack/inactive Dice at every stage | 55 | 40 |
| 4 | arxiv:2402.03166 RRWNet | 2024 | ESWA | github.com/j-morano/rrwnet (stated in abstract) | Base subnetwork + recursive refinement subnetwork that iteratively fixes class confusions in multi-class thin structures (artery / vein); also usable as post-processor for other models | Target class confusions: crack vs inactive (20% of crack pixels at inactive), crack vs gridline; recursive module on 24-class probabilities | 55 | 40 |
| 5 | arxiv:2209.06353 Label refinement network from synthetic error augmentation | 2024 | Medical Image Analysis | unverified | Synthetic structural-error generator + a label-appearance simulation network that makes synthetic errors look like real predictions; refiner trained on image + corrupted mask; larger gains with extra unlabeled data | 2D version; error model = skeleton breaks, faint-segment deletion, width / 1 px offset per source; appearance net trained to mimic out-of-fold crack probability maps; pool cells add base-model predictions to correct | 55 | 30 |
| 6 | arxiv:2409.09796 Universal Topology Refinement | 2024 | MICCAI | github.com/smilell/Universal-Topology-Refinement | Plug-and-play topology refiner trained on synthetic perturbation masks built from random orthogonal-polynomial fields, so the error distribution is not limited to a small labelled set | Generate perturbations on all crack GT (478 + E-SCDD train cells) and on UCF-EL crack polygons (label-only use); test as cheap alternative error model to #5 | 45 | 25 |
| 7 | doi:10.1109/tmi.2024.3405982 Deep Closing | 2024 | IEEE TMI | github.com/5k5000/DeepClosing (stated in abstract) | Masked-image-modelling autoencoder on labels learns a tubular shape prior, flags likely disconnections; a simple-components erosion keeps only topologically meaningful additions | Shape prior trained on label masks only (no images), so it can use every crack label we have (BenchmarkEL, E-SCDD, UCF-EL thin parts); closes gaps of detected cracks | 45 | 25 |
| 8 | doi:10.1109/tip.2025.3526061 VSR-Net | 2025 | IEEE TIP | unverified | Clusters ruptured sub-segments of a coarse curvilinear mask (graph clustering) and merges them; also improves calibration | Apply to crack components < 20 px that lie on one line (76-88% of crack components are < 20 px) | 40 | 25 |
| 9 | arxiv:2606.21608 CurvSegFlow | 2026 | arXiv | not found | Segmentation as time-conditioned flow matching: a U-Net integrates a learned velocity field from a noisy start to the mask, giving gradual error correction; best gains at low SNR for thin filaments | Moonshot: flow-matching refinement head initialised from house-model probabilities instead of noise; aimed at the 7% of crack components < 2% darker than background | 42 | 35 |
| 10 | arxiv:2312.12425 SegRefiner | 2023 | NeurIPS | github.com/MengyuWang826/SegRefiner (cited in rNCA) | Discrete diffusion over pixel states (coarse -> fine), U-Net on image + mask at 256 px, T = 6 steps, trained on GT degraded by morphological perturbation (DIS5K + ThinObject-5K for HR model) | Fine-tune on our cells for inactive (blob, well labelled) and per-crack crops; R: no gain on DRIVE vessels (rNCA Table 1), so expect crack n.d. | 32 | 60 |
| 11 | arxiv:2502.06756 SAMRefiner | 2025 | ICLR | github.com/linyq2117/SAMRefiner | Training-free: mines distance-guided points, elastic boxes and Gaussian mask prompts from a coarse mask and feeds SAM; optional self-boosted IoU adaptation (SAMRefiner++) with no labels | Zero-training test on inactive regions and on BMRK cells (weak source); crack lines 1-2 px are unlikely to suit SAM | 36 | 50 |
| 12 | arxiv:2005.02551 CascadePSP | 2020 | CVPR | github.com/hkchengrex/CascadePSP (pip segmentation-refinement) | Class-agnostic global-then-local cascade refiner trained on perturbed masks; refines any mask at any resolution | Inference-only test on inactive masks (repeat 1-channel EL to 3 channels); fine-tune on inactive GT perturbations if promising | 30 | 50 |
| 13 | arxiv:2609.33996 UnfoldCRF | 2026 | arXiv | "will be released" (unverified) | Refinement as unrolled mean-field CRF over pixel labels + latent regions; pairwise terms fix boundaries, region terms fix non-boundary errors; compared against capacity-matched black-box refiners | Multiclass CRF refiner over our 24-class output; its matched-control protocol is the right design for any refiner arm we run | 40 | 45 |
| 14 | arxiv:2506.10712 UMBD | 2025 | arXiv | "will be released" (unverified) | Bernoulli diffusion applied only to pixels an uncertainty network flags, leaving confident pixels untouched | Restrict refinement to the uncertain 2-4 px band around predicted cracks and inactive borders; protects the 0.93 relP@2 already reached | 35 | 25 |
| 15 | arxiv:1904.07934 STEAL (Devil is in the edges) | 2019 | CVPR | unverified | Treats the true thin boundary as latent; actively aligns noisy labels to the network's edges during training (active contour) and adds an NMS-style loss for 1-px-thin outputs | Align jittered 1-2 px crack labels to the dark ridge during training, and the NMS loss to control predicted width; refines labels, not predictions | 40 | 35 |
| 16 | arxiv:2602.05880 Contour discrete diffusion, low data | 2026 | arXiv | not found | Lightweight discrete diffusion that denoises a sparse contour representation conditioned on a mask; designed for < 500 training images | Inactive region outlines (42 train cells); long shot | 25 | 15 |

## Minimum experiments (cheapest decisive ones first)

1. rNCA crack repair (paper 1). Arm: house 5-fold models -> out-of-fold crack maps -> rNCA trained on them; at test, refine the house 5-seed ensemble probabilities. Baseline: same ensemble without refiner. Metrics: 5-fold CV + clean-49 crack relF1@2, components >= 20 px found, crack IoU; E1 relR@2. Kill: relF1@2 gain < +0.005 and components found < +0.02 on 5-fold CV. About 8 GPU-h (folds) + 2 GPU-h (NCA).
2. IterNet stages (paper 3). Arm: U-Net++ + 3 weight-shared mini-U-Net stages, 20k steps, 5 seeds. Baseline: house and PF. Metrics: crack IoU, relF1@2, mIoU_rob, inactive IoU. Kill: crack IoU < +0.012 (the 5 v 5 detection limit) and no relF1@2 gain. About 7 GPU-h.
3. Synthetic-error refiner (papers 5, 6). Arm: U-Net refiner (image + 24-class probabilities) trained on out-of-fold maps + synthetic errors; matched-capacity control trained on out-of-fold maps only (UnfoldCRF-style control). Kill: the arm does not beat its control by >= 0.01 relF1@2 on 5-fold CV.
4. Inactive zero-shot (papers 11, 12). Arm: SAMRefiner and CascadePSP applied to predicted inactive components. Baseline: house / PF ensemble inactive masks. Metric: inactive IoU on 5-fold CV + E1 (PF). Kill: < +0.01 inactive IoU or any drop on BMRK. Under 1 GPU-h, no training.
5. RRWNet recursive class correction (paper 4). Arm: recursive module on 24-class probabilities. Metrics: crack/inactive confusion matrix, inactive IoU, gridline IoU, mIoU_rob. Kill: mIoU_rob < +0.005 and inactive IoU < +0.01.

## Rejected (one line each)

- PointRend / Mask Transfiner / BPR (arXiv 2104.05239) / PatchDCT / SharpContour: instance-mask refiners for low-resolution heads; U-Net++ already decodes at full 512 px.
- SegFix (arXiv 2007.04269, code in openseg.pytorch): replaces boundary pixels with interior pixel labels; a 1-2 px crack has no interior, and on DRIVE it did not help (rNCA Table 1). Only fits structural class borders that already score 0.7-0.99.
- DenseCRF: no Dice gain on DRIVE vessels (rNCA Table 1); classic CRFs erase 1-2 px lines.
- Automatic HR wire segmentation (arXiv 2304.00221), CascadePSP-style HR crack cascades (Chu et al. mice.13111): coarse-to-fine across resolution needs native detail above 512 px; labelled cells are 512 px and 2x input was n.d. (BRIEF section 5).
- Diffusion crack segmenters (CrossDiff 2501.12860, CrackSegDiff 2410.08100): full generative segmenters, belong with a generative-segmentation direction, not a refinement stage.
- HQ-SAM, SAM2Refiner (arXiv 2502.09660), UCS (2504.04034): fine-grained SAM variants; belong to the foundation-model direction; interactive prompts are needed.
- G4Seg, LawDIS, BiRefNet: text-to-image or DIS models for natural images; not a refinement stage for our labels.
- Cascade of organ-scale networks (G-CASCADE, multi-organ cascades): ROI cropping for large organs; our structures are not localisable by a coarse box.

## Gaps

- "Segmentation refinement of thin cracks with Minimum Strip Cuts" (doi:10.1016/j.aei.2025.103249, AEI 2025) is the closest-domain paper (thin-crack refinement) but no abstract or full text was reachable off campus; needs a campus fetch.
- No paper found that tests a refiner on 1-2 px labels with label jitter or on EL; all thin-structure evidence is vessels (DRIVE, airways, microtubules).
- Semantic Scholar snippet search was down all session; evidence on refiner failure modes on thin structures rests on the rNCA comparison table only.
- Code for Chen 2024, VSR-Net, UnfoldCRF, UMBD, CurvSegFlow, BRNCA, STEAL not verified.
- Sub-direction worth its own search: source-conditional refinement (a refiner that maps a source-neutral crack centreline to each source's label width and offset); I found no paper on it.
