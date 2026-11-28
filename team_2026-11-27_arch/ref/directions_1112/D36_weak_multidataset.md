# D36: Weak and heterogeneous supervision; multi-dataset training

Scout: literature phase only. Pass 1 on 12 Nov 2026, pass 2 (resume, gap filling) on 13 Nov 2026. No servers, no test data read.
Legend: R = what the paper measured, E = what our files measured (from BRIEF), S = my judgement.

## 1. Why this direction is open (from BRIEF section 5)

- The only multi-dataset run so far was UCF-EL supervised pretraining of the encoder followed by the house fine-tune, which erased the encoder (n.d. / worse). BRIEF says this does NOT close joint multi-dataset training, nor pretraining that the fine-tune keeps.
- Never tried: multi-label heads, source-conditional prediction, cross-dataset joint training, noisy-label methods.
- External data on hand or public: UCF-EL (9,562 train cells, polygons, crack-as-region, contact, interconnect, corrosion), MultiSolSegment (585 mono cells, 4 overlapping sigmoid channels), PV-Vision / LBNL crack set (crack + busbar masks), ELPV (2,624 cells, image-level defect probability; BMRK = ELPV cells), PVEL-AD (36,543 NIR cells, boxes, by request so needs the user's OK).

## 2. Queries run

Research MCP `search_papers` (year_from 2020 unless stated). In both passes Semantic Scholar was rate-limited and Scopus / ScienceDirect returned HTTP 401; pass 2 results came almost only from OpenAlex.

Pass 1 (12 Nov):
1. multi-dataset semantic segmentation different taxonomies label space unification
2. partially labeled datasets segmentation marginal loss multiple datasets
3. box-supervised instance segmentation SAM pseudo masks
4. mixed supervision surface defect segmentation weak and strong labels
5. electroluminescence solar cell defect weakly supervised segmentation image-level labels
6. weakly supervised crack segmentation box or scribble annotations
7. dataset-specific heads conditional segmentation annotation style multiple datasets inconsistent labels
8. taxonomy adaptive domain adaptation semantic segmentation
9. universal medical segmentation dataset prior prompt multiple datasets annotation protocol (2022+)
10. learning segmentation from coarse polygon annotations noisy boundaries
11. multi-dataset joint training semantic segmentation partial labels (2025+)
12. SAM generated pseudo masks from bounding boxes defect segmentation weak supervision (2025+)
13. PVEL-AD photovoltaic electroluminescence anomaly detection dataset
14. learning from multiple annotators segmentation annotator-specific style conditioning
15. weakly supervised semantic segmentation image-level labels thin crack CAM refinement (2023+)
16. label space unification multi-dataset segmentation conflicting class definitions (2025+)
17. BoxInst projection loss pairwise affinity
18. electroluminescence segmentation cross-dataset generalization combined datasets cracks (2024+)
19. mixed supervision segmentation image-level and pixel-level labels small dataset (2022+)
20. unified defect segmentation model trained on multiple industrial datasets heterogeneous annotations (2024+)

Pass 2 (13 Nov):
21. annotation style conditioning segmentation multiple datasets inconsistent annotation protocols (2023+)
22. dataset-aware prompt multi-dataset segmentation partially labeled (2024+)
23. point supervision crack segmentation weak labels (2022+)
24. multi-dataset training industrial defect segmentation unified model heterogeneous labels (2024+)
25. photovoltaic electroluminescence defect segmentation multiple datasets cross-dataset evaluation (2024+)
26. hierarchical label space semantic segmentation coarse and fine labels different datasets (2021+)
27. box-supervised segmentation thin curvilinear structures vessel crack (2021+)
28. mixed supervision segmentation pixel-level and image-level labels defect (2025+)
29. SAM 2 box prompts pseudo masks weakly supervised segmentation noisy pseudo-label filtering (2025+)
30. dataset-specific normalization multi-site joint training segmentation heterogeneous annotations (2021+)
31. learning segmentation from coarse region labels to fine boundaries label refinement weak annotations (2024+)
32. defect-free negative images reduce false positives segmentation training image-level labels (2021+)
33. universal taxonomy multi-dataset semantic segmentation partial label loss (2025+)
34. ELPV dataset weakly supervised localization class activation defect electroluminescence (2022+)
`search_snippets` ("naive pooling of datasets with different annotation protocols degrades ...") failed on the S2 rate limit in both passes.

Snowballing: pass 1 `similar_papers` on MultiTalent + Nichyporuk, `get_citations` on MultiTalent (72 citing, 25 read). Pass 2 `get_citations` on Nichyporuk (19 citing, all read: only Expert-Adaptive 2402.07330 is on-topic), `similar_papers` on {MultiTalent, Shi marginal loss, UniSeg} (found Bevandić 2108.11224) and on {Boxes2Pixels, Božič} (industrial mixed supervision, nothing stronger).
Full text read (pass 1): MultiTalent (2303.14444), Nichyporuk (2210.17398), MultiSolSegment (2603.13337).
WebSearch: verified repos for MultiTalent, Boxes2Pixels, Božič mixed supervision (pass 1); MultiSolSegment code at sandialabs/pvcracks and the PVEL-AD repo listing (pass 2). No repo found for Nichyporuk or Bevandić.

## 3. Selected papers (18)

`score` = value for raising our numbers (task rubric), `bench` = value for the benchmark.

| # | id | year | venue | code | mechanism (R) | adaptation to our data (S) | score | bench |
|---|---|---|---|---|---|---|---|---|
| 1 | arxiv:2210.17398 | 2022 | MELBA | none found | Conditional instance norm: per-dataset scale/shift in every norm layer, rest shared. R: on 6 MS trials, naive pooling was worse than single-trial models (0.766 vs 0.784 Dice on RRMS-A); trial-conditioned matched or beat every single-trial model (0.787 to 0.789) and can output any style for any image; few-shot fine-tune to a new style. | Our 5 sources have measured label-width conventions (ARTS 1.5 px ... SDLE 3.25 px). Add per-source affine params (ARTS, CFVS, CSIR, BMRK, SDLE, later UCF, MSS, PV-Vision) to decoder BN layers of U-Net++; encoder BN shared. Test: condition on the cell's known source; E1 conditioned as CSIR. Lets UCF-EL region-cracks, MSS and PV-Vision cracks join training without polluting BenchmarkEL style. Benchmark tool: report crack IoU "in source style". | 74 | 60 |
| 2 | arxiv:2303.14444 | 2023 | MICCAI | github.com/MIC-DKFZ/MultiTalent (3D nnU-Net; verified) | Every dataset's classes kept distinct, one sigmoid head per class on a shared backbone, BCE + batch Dice only on classes that dataset annotates, losses summed not averaged, sampling prob ~ 1/sqrt(n). R: 13 CT datasets, +1.26 Dice average, biggest gains on difficult and cancer classes; as pretraining it beat SSL baselines. | Keep the house 24-class softmax head for BenchmarkEL. Add sigmoid heads UCF_crack_region, UCF_contact, UCF_interconnect, UCF_corrosion, MSS_crack, MSS_dark, MSS_busbar, MSS_noncell, PVV_crack. Each batch mixes BenchmarkEL with external cells; loss on a head only for cells from its dataset. Joint from step 0, so nothing is "erased" by a later fine-tune (the failure mode in section 5). | 72 | 60 |
| 3 | arxiv:2007.03868 | 2021 | MedIA | unverified (loss is a few lines) | Marginal loss: when a dataset merges several classes into one label, sum the model's probabilities over those classes before CE / Dice. Exclusion loss: labelled class A pixels push down probability of disjoint classes. | UCF "crack" polygon = {crack OR inactive} in our 24-class space: supervise log(p_crack + p_inactive). UCF background = marginal over all structural classes it does not label (gridline, busbar, ribbons, frame_edge ...) plus background, so no wrong negatives. UCF contact / corrosion / interconnect pixels: exclusion on crack. Same single softmax head; no new heads. | 68 | 45 |
| 4 | arxiv:2108.11224 | 2022 | WACV | none found (follow-up 2212.10340 says code released; URL not seen) | Universal taxonomy: each dataset class is a union of universal classes; train one softmax over universal classes with a partial-label NLL (log of summed probability of the union). R: competitive within- and cross-dataset, state of the art on WildDash 2; learns concepts never labelled separately in any dataset. | The principled general form of row 3. Universal classes = our 24 classes plus any UCF / MSS class with no BenchmarkEL counterpart (e.g. contact, interconnect). Write the dataset-to-universal map by hand (3 to 4 datasets, so no automatic taxonomy needed). Arm B of experiment 2 should follow this formulation rather than an ad-hoc version. | 62 | 45 |
| 5 | arxiv:2502.19177 | 2025 | IROS | unverified | Teacher trained on one taxonomy pseudo-labels other datasets; the other datasets' GT (mapped to the source taxonomy) constrains which classes the teacher may predict per pixel; students beat teachers on 12 urban / 7 off-road datasets. | Teacher = house 5-seed ensemble. Pseudo-label UCF-EL, MSS and PV-Vision cells in the 24-class space with GT constraints: inside a UCF crack polygon only crack / inactive allowed; inside MSS / PV-Vision crack mask crack forced; outside any defect GT crack and inactive forbidden. Different from the section 5 pool SSL (unconstrained pseudo-labels on unlabelled cells). | 66 | 40 |
| 6 | arxiv:2603.13337 | 2026 | Solar Energy | github.com/sandialabs/pvcracks (web search listing, BSD-3; weights and data DOIs listed) | Multi-channel sigmoid U-Net for EL: dark, busbar, crack, non-cell as independent channels so a crack crossing a busbar stays continuous. R: 585 mono cells (ASU 92, CWRU 123 + 250, LBNL 120), 256 px, mean IoU 0.384; crack in 77% of images. Split was random 80/20 after 4x flip augmentation (flipped copies of one cell can land in train and val: leakage). | Two uses. (a) Data: 585 extra crack-labelled mono cells with their own style, for experiments 2 to 4. (b) Mechanism: add independent sigmoid channels for crack and inactive on top of the softmax head; 20% of our train crack pixels lie in or at inactive regions, where argmax must drop one. Benchmark: an example of split leakage to cite and an extra cross-dataset test set. | 60 | 70 |
| 7 | doi:10.1109/jphotov.2023.3249970 | 2023 | IEEE J. Photovoltaics | stated open source in abstract (PV-Vision; URL not opened) | U-Net (VGG16) crack + busbar segmentation on EL cells and crack feature extraction (isolated area, its brightness, length). R: average F1 0.875, IoU 0.782 on its test set; annotated dataset released as a crack segmentation benchmark. | Third pixel-labelled EL crack source. Its IoU 0.782 vs our 0.47 suggests much wider crack labels (unverified; check masks), so it must enter only through source conditioning (row 1) or a separate head (row 2). Its "crack-isolated area" features are a ready severity baseline. | 50 | 70 |
| 8 | arxiv:2104.06064 | 2021 | Computers in Industry | github.com/vicoslab/mixed-segdec-net-comind2021 (verified) | SegDec-Net: segmentation + classification head; trains on any mix of image-level and pixel-level labels. R: on KolektorSDD2 / DAGM / Severstal, a handful of pixel labels plus weak labels approach full supervision. | ELPV: 2,624 cells with image-level defect probability; BMRK (our weakest source: crack 0.379, inactive 0.324) is ELPV cells. Add a cell-level defect head; ELPV cells with p = 0 give full-image negatives for crack / inactive; p = 1 cells give MIL-style "some defect here". Must hash-match and drop any ELPV cell that is (or shares a module with) a BenchmarkEL val / test BMRK cell. | 62 | 40 |
| 9 | arxiv:2610.15612 | 2026 | arXiv | unverified | Two-branch mixed supervision: masks for base lesion types, image-level labels for more types; a lesion-wise attentive classifier keeps per-class prototypes and pools features only over lesion-like regions, so image labels shape the segmentation features. R: gains over open-vocabulary baselines on several mammography sets, reported to help small, low-contrast findings. | Alternative to the plain MIL head of row 8 for ELPV labels: prototype-attention pooling stops the cell label being explained by gridlines or borders. Expect value mainly on BMRK inactive and on false alarms, not on thin-crack IoU. | 42 | 30 |
| 10 | arxiv:2202.14030 | 2022 | ECCV | project page only (unverified) | UniSeg: class-independent BCE removes gradient conflict from mismatched label spaces; extra loss uses cross-dataset class relationships. R: road scenes, more than +8 IoU on unseen KITTI, 39.4 IoU WildDash2 zero-shot. | The R gain is on unseen domains, which is our E1 problem. Swap softmax CE for per-class BCE in the joint run and score E1. Class relationships: UCF crack_region is a parent of {crack, inactive}. | 58 | 45 |
| 11 | doi:10.1016/j.engappai.2026.115849 | 2026 | EAAI | unverified | Thin-structure label refinement: foundation-model masks used only inside a narrow trust region around expert labels, an IoU gate rejects bad cases, minimal closing; unconstrained MedSAM pseudo-labels degraded training. R: modest gain on bone fractures (5-fold CV), mAP50 0.63. | Needed when turning UCF polygons (region-cracks) into thin crack lines, and for our own 1 to 2 px jittered crack labels: allow refinement only within 2 px of the given label, gate by agreement with the ridge. Also a warning: never train on raw SAM / SAM2 crack masks. | 58 | 35 |
| 12 | arxiv:2007.15963 | 2020 | arXiv (MIDL line) | unverified | Two coupled CNNs: one estimates the true segmentation, the other a per-annotator pixel-wise confusion matrix; trace penalty forces the annotator model to absorb the noise. R: MSLSC, BraTS, LIDC; best when annotations are few and disagree. | Treat each source (and UCF, MSS, PV-Vision) as an "annotator". The annotator branch learns e.g. "SDLE draws cracks 3 px wide, UCF draws regions". Clean head scored on test. Restrict confusion maps to crack / inactive / background (3x3) to keep it small. | 52 | 35 |
| 13 | arxiv:2402.19340 | 2024 | IJCARS | unverified | Combine binary single-class datasets: positives of other classes act as negatives, background of a binary set is excluded from the loss. R: +4.4% Dice over per-class ensemble, 24% less stomach / colon confusion. | Simpler variant of row 3 for MSS / PV-Vision: their busbar / non-cell positives are negatives for our crack (except where their crack overlaps), their background excluded from loss for classes they do not label. 2D DeepLabV3 evidence, close to our setting. | 50 | 30 |
| 14 | arxiv:2604.11162 | 2026 | arXiv (CVPR 2026 per one site, unverified) | github.com/CLendering/Boxes2Pixels (verified) | Boxes to SAM pseudo-masks treated as a noisy teacher: frozen DINOv2 features + hierarchical decoder, binary "any defect" head, one-sided self-correction that relaxes background loss where the student is confident. R: wind-turbine defects, +6.97 anomaly mIoU, +9.71 binary IoU, +18.56 binary recall from self-correction. | PVEL-AD crack / finger / black-core boxes (needs the user's OK; repo listing shows 1,260 trainval crack boxes). SAM misses thin defects, so make box-gated pseudo-masks with the house ensemble instead of SAM; keep the one-sided rule: outside all boxes = hard background, inside a box = soft. NIR polycrystalline: own source flag (row 1). | 48 | 45 |
| 15 | arxiv:2012.02310 | 2021 | CVPR | AdelaiDet (unverified) | BoxInst: mask from boxes via projection loss (mask max-projected onto x and y axes must match the box) + pairwise colour-affinity loss. | For a crack box the projection term says the crack spans the box in both axes, which suits long thin cracks; affinity on EL intensity says neighbouring pixels of similar brightness share a label. Auxiliary loss on the crack channel for PVEL-AD boxes. No SAM needed. | 45 | 40 |
| 16 | arxiv:2508.19060 | 2025 | J. Intelligent Manufacturing | unverified | SuperSimpleNet: one model for unsupervised, weak, mixed and full supervision, with synthetic anomaly generation and a classification head. | Benchmark baseline that can use ELPV image labels and the unlabelled pool under one protocol; unlikely to beat the house model on thin crack IoU. | 35 | 55 |
| 17 | doi:10.1016/j.solener.2025.114083 | 2025 | Solar Energy | stated public in abstract (URL not verified) | Instance-seg benchmark on UCF-EL with MMDetection: ConvNeXt-V2 best, seg mAP50 0.602, mIoU 0.650; Mask R-CNN, Mask2Former also run. | Little direct score value (UCF-EL test leaks per BRIEF). Benchmark: the existing "EL benchmark" to cite and to show why a clean split is needed; Mask2Former / ConvNeXt-V2 belong in the method suite. | 25 | 65 |
| 18 | arxiv:2001.11248 | 2020 | arXiv | unverified | Weakly supervised crack segmentation on EL from image-level labels: ResNet-50 activation maps aggregated by a normalized Lp layer. | EL-specific image-label baseline using ELPV labels; for a "weak supervision" track of the benchmark. Not expected to beat pixel-supervised cracks. | 25 | 45 |

## 4. Minimum experiments (priority order)

All arms: house U-Net++ / ResNet-34, 512 px, label-safe aug, bf16; 5 seeds per arm; baseline = existing house 5-seed runs (PF where the arm involves a later fine-tune). Metrics: crack IoU and relF1@2 on clean-49, inactive IoU, mIoU_rob, E1 crack relF1@2 / recall, E1 inactive IoU, per-source crack IoU (BMRK). Detectable crack IoU change is about 0.012 (BRIEF 4.5), so kill lines sit at or above that. Inactive claims should also be checked on the module-grouped 5-fold CV roots.

1. **Source-conditioned decoder (row 1), BenchmarkEL only.** Per-source affine in decoder BN, 20k steps. Kill if crack IoU < +0.012 and per-source crack IoU on BMRK / CFVS not up by 0.02. About 6 GPU-h. Cheapest, no new data, and a prerequisite for adding external crack data of other styles.
2. **Joint UCF-EL + MSS + PV-Vision training (rows 2, 3, 4).** Arm A: extra sigmoid heads per external class (MultiTalent). Arm B: single softmax over a universal taxonomy with partial-label (marginal) NLL and exclusion. 50% of each batch BenchmarkEL, 30k steps. Both with source conditioning if step 1 passed. Kill if crack IoU < +0.012 AND E1 crack relF1@2 < +0.03 AND inactive IoU not up. About 30 GPU-h.
3. **GT-constrained pseudo-labels (row 5).** Teacher = house ensemble; student on BenchmarkEL + constrained external labels. Same kill line as 2. About 15 GPU-h.
4. **ELPV image labels (rows 8, 9).** Cell-level head + full-image negatives from p = 0 ELPV cells, positives as MIL (row 8), optional prototype pooling (row 9). Kill if BMRK inactive IoU < +0.05 on 5-fold CV and crack precision not up. About 8 GPU-h, plus ELPV de-duplication against val / test.
5. **Multi-label crack / inactive channels (row 6b).** 2 extra sigmoid channels; argmax for the 24-class map, sigmoid for crack and inactive scoring. Kill if crack relR@2 < +0.02 at equal relP@2 and inactive IoU not up. About 6 GPU-h.
6. **PVEL-AD boxes (rows 14, 15)** only if 2 or 3 show gain from extra crack data, and only after the user OKs the request.

## 5. Notable papers rejected

- MSeg, doi:10.1109/cvpr42600.2020.00295 (TPAMI version doi:10.1109/tpami.2022.3151200): manual taxonomy reconciliation for natural scenes; our taxonomy is small and mapped by hand in row 4.
- GNN label unification (arxiv:2407.10534, NeurIPS 2024) and automatic universal taxonomies (arxiv:2207.08445): learn label mappings among many datasets; with 3 to 4 EL datasets the mapping can be written by hand.
- DoDNet (arxiv:2011.10217), COSST (arxiv:2304.14030), deep mutual learning (arxiv:2407.12611), CLIP-Driven Universal Model (arxiv:2301.00785), labeled-to-unlabeled alignment (arxiv:2409.03228): 3D medical partial-label methods; MultiTalent covers the idea more simply and beat DoDNet / Universal Model on BTCV.
- Federated multi-organ segmentation with inconsistent labels (arxiv:2206.07156): marginal-style loss in a federated setting; federation adds nothing for us.
- Expert-Adaptive segmentation (arxiv:2402.07330): multi-expert multi-task heads + light fine-tune to a new expert; same idea as row 1 with weaker evidence (brain MRI, small study).
- TACS (arxiv:2109.04813), DynAlign (arxiv:2501.16410), inconsistent-taxonomy UDA with VLMs (arxiv:2408.02261): UDA with taxonomy change; target is unlabelled, ours is labelled. For E1 only via the UDA scout.
- LMSeg (arxiv:2302.13495), sentence-embedding multi-domain segmentation (arxiv:2202.02002): text embeddings add nothing for 1-channel EL classes.
- BoxTeacher (arxiv:2210.05174), Box2Mask (arxiv:2212.01579), BoxSnake (arxiv:2303.11630), box-constrained prompt learning (arxiv:2507.02743): box supervision for objects with area; Boxes2Pixels and BoxInst are closer to thin defects.
- SAMRefiner (arxiv:2502.06756, code github.com/linyq2117/SAMRefiner per abstract), SAM-enhanced WSSS pseudo-labels (arxiv:2305.05803), BoxCell (arxiv:2311.17960), SAM2-ELNet (arxiv:2503.12404), SeSAM (arxiv:2604.11170): SAM-based mask refinement; SAM misses thin low-contrast defects (Boxes2Pixels R; bone fracture paper R). SAMRefiner might tighten UCF region polygons for inactive; visual check only, too speculative to rank.
- YoloCurvSeg (arxiv:2212.05566): one noisy skeleton label for curvilinear structures; needs a full synthetic pipeline; belongs with the synthesis / label-refinement scouts.
- UMA-Net multi-source annotations (arxiv:2304.00466): multiple annotations of the same images; we have that only for the 2-annotator crack agreement.
- Label-Assemble (arxiv:2109.12265): negatives from other datasets help detection; folded into experiment 4 (ELPV negatives).
- Crack WSSS from civil engineering (CrackCLIP doi:10.3390/e27020127, CAC doi:10.3390/e26040328, WP-CrackNet arxiv:2510.17566, weakly supervised crack detection arxiv:2206.06743, affine + pseudo-label refinement doi:10.1038/s41598-025-93196-x): patch-level or image-level labels on concrete / road, wide cracks; our cracks are 1 to 2 px labels on 4 px lines.
- PVEL-AD dataset paper (doi:10.1109/tii.2022.3162846) and UCF-EL paper (doi:10.1109/jphotov.2021.3131059): data sources, not methods.

## 6. Gaps

- No paper found that jointly trains on several EL segmentation datasets with different taxonomies or label styles. MultiSolSegment pooled 4 sources under one relabelled taxonomy with a leaky split. A clean joint-training study would be new and is itself a benchmark contribution.
- Label width of PV-Vision and MSS crack masks is unverified (PV-Vision crack IoU 0.782 hints at wide labels). Measure the median crack label width of each external set before any joint run; this decides whether source conditioning is required.
- Whether UCF-EL, MSS or PV-Vision contain half-cut cells (relevant to E1) is unverified.
- Exact class list and image format of PVEL-AD (NIR, polycrystalline) not read; dataset by request.
- Code repos for rows 1, 3, 4, 5, 7, 9, 10, 11, 12, 13, 15, 16, 17, 18 are unverified or not found.
- `search_snippets` failed in both passes (S2 rate limit), so no full-text evidence check on "naive pooling hurts" beyond Nichyporuk.
- ELPV / BMRK overlap: the de-duplication rule for using ELPV beside BenchmarkEL (and for the benchmark split) needs a concrete check (image hashes, module ids).
- Sub-direction worth its own search: source-conditional prediction as a benchmark protocol ("score in each source's labelling style") versus a canonical-style label set.
