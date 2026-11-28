# Scout `unsup`: segmentation beyond full supervision

27 Nov 2026. Family: industrial anomaly detection (AD) and AD maps as a prior, unsupervised semantic segmentation, weak and mixed supervision, self-training and self-distillation at full labels, pixel contrastive learning, semi-supervised methods after 2024.
The question for every paper: can it raise recall on unseen modules or on rare classes when all 532 cells are labelled?

Overlap: D39 (AD as a prior), D07 (AD, PV pretraining), D29 (semi-supervised), D32 (dense SSL) and D40 (Bozic mixed supervision) already covered parts of this family. I read D39 and D29 in full and skimmed D32. I did not re-score their rows (WeakREST P112, SuperADD P266, ResAD P370, DeSTSeg P328, GLASS P409, CoMet P537, Noisy Student P180, Zoph P051, ensemble KD P014). Below I mark only what is new, or where my reading changes an existing row.

## Counts
- search_papers: 42 queries (list below). The per-query totals after each query's own merge add up to 1,688 hits, and I looked at 646 result titles and abstracts. Snowballing: get_citations on 4 seeds (SegAD, Bozic mixed supervision, MuSc, ContrastSeg; 139 citers listed) and similar_papers on [SegAD, WeakREST, SuperSimpleNet] (20). I called get_paper on about 25 candidates.
- search_snippets: 1 try. It failed because Semantic Scholar was rate-limited all session. Scopus and Semantic Scholar returned almost nothing, and arXiv timed out on most queries, so OpenAlex and ScienceDirect did most of the work.
- Full text read (sections): 9 papers. They are SegAD, ISP-AD, MuSc-V2, GMMSeg, MetaUAS, BGAD, CSST (Zhu et al. TPAMI), Cross-Image Pixel Contrasting (TPAMI version) and RPL.
- `papers.tsv`: **75 rows after dedupe: 64 NEW and 11 already in MASTER.** The 11 are P449, P620, P623, P275 (as its TPAMI version), P200, P086, P535, P239, P079, P290 and P473. Most results were surveys, off-topic hits or near-duplicates of D39/D29 rows, and I did not list those.
- Fit score spread: 1 paper scored 4, 5 scored 3, 9 scored 2, 27 scored 1 and 33 scored 0. Most zeros are unsupervised semantic segmentation and CLIP/LVLM zero-shot AD. I listed them because the brief asks for family coverage, not because they are candidates.

## Main reading
1. **No paper adds an AD prior to a supervised multi-class pixel segmenter and measures per-class pixel gains at full labels.** D39 found the same. The closest evidence is image-level: SegAD (FPR@95TPR 32.8 to 16.4 when AD maps join a supervised classifier) and ISP-AD (recall 76.8 to 95.8 with mixed synthetic and real defects). Any AD-prior arm is still a bet.
2. **AD maps from foundation-model patches are too coarse for 1 to 2 px cracks.** MuSc-V2, UniVAD, FoundAD, AnomalyCLIP, AA-CLIP and WinCLIP all work on ViT patches. The exceptions keep a full-resolution path: MetaUAS has a U-Net decoder to full resolution, and PyramidFlow is a flow without a pretrained bottleneck. Only these two fit as crack priors. The patch-level methods can serve as inactive or unknown-region priors.
3. **Unsupervised semantic segmentation (STEGO, HP, EAGLE, U2Seg, CutLER, EmerDiff, DiffCut, SmooSeg, CUPS) has nothing for us.** All of it finds large semantic regions from ViT or diffusion features at 1/8 to 1/32 resolution. None reports thin structures, and none helps at full labels. Every row scores 0.
4. **At full labels, the methods that report gains in their papers are train-time losses and offline self-training with class-aware sampling, not online consistency.** Pixel contrast gave +1.0 on Cityscapes test with HRNetV2-W48, GMMSeg +0.5 to +1.7, and CSST +1.2 to +1.9 at full Cityscapes labels. This fits our null: Mean Teacher helped only at 5 to 10% labels.
5. **Weak supervision matters here only as extra data, not as a cheaper label.** Examples are box-labelled external EL (PVEL-AD) or synthetic curves on inpainted half-cut backgrounds (YoloCurvSeg). I found no evidence that either helps 1 to 2 px lines.

## Top 10

**1. MetaUAS** (doi:10.52202/079017-1257, NeurIPS 2024, NEW, code yes). Full text read.
- **Mechanism:** a query image and one normal prompt image pass through a frozen EfficientNet-b4. Soft feature alignment matches them at three deep scales, and a U-Net decoder returns to full resolution. It is meta-trained only on synthetic change pairs from natural images.
- **Evidence:** with one prompt it reaches MVTec pixel AP 59.3, against 44.7 for UniAD trained on all normal images and 37.1 for one-shot PatchCore. On VisA it reaches 42.7, against 34.3 for UniAD.
- **Our failure modes:** *half-cut layout and unseen modules.* The prompt is a clean cell of the same layout, for example a pool half-cell for half-cut cells. The output is a "differs from normal" map that does not depend on which layouts were in training. It is the only reference-based method found with a full-resolution decoder, which matters for *thin-line* recall.
- **Arm:** zero-shot map as an input channel or a 6th ensemble member. Second step: meta-train it on EL change pairs made by pasting our labelled crack and inactive masks onto clean cells.
- **Risk:** VisA PRO is 60.4 against PatchCore's 84.6, so faint thin defects are not shown to work. The prompt must match the query geometrically.

**2. Cross-Image Pixel Contrasting** (doi:10.1109/tpami.2024.3367952; ICCV version is P275, PARKED; code unknown). Full text read.
- **Mechanism:** a supervised pixel-to-pixel and pixel-to-region contrastive loss across images, with memory banks and "segmentation-aware hard" anchors, meaning pixels the model currently gets wrong. It is a train-time loss only.
- **Evidence:** HRNetV2-W48 on Cityscapes val 78.1 to 81.0 (40k-iteration ablation); test +1.0, PASCAL-Context +1.1, COCO-Stuff +0.6, CamVid +0.5. All at full labels.
- **Our failure modes:** *rare classes and recall.* Our winning encoder is HRNet. Hard anchors are missed crack and inactive pixels. The memory bank lets the 42 inactive cells and the 0.19% crack pixels contrast against many cells per step.
- **Recommendation:** promote P275 from PARKED. It costs a new loss and no new backbone.
- **Risk:** the reported gains are mIoU on large classes. Embeddings at 1/4 resolution can blur 1 to 2 px lines, so sample crack anchors at the stride-2 head.

**3. GMMSeg** (doi:10.52202/068431-2274, NeurIPS 2022, NEW). Full text read.
- **Mechanism:** a dense generative classifier with a Gaussian mixture per class, updated by EM, while the backbone trains discriminatively.
- **Evidence:** closed-set gains at full labels of +0.8 (HRNetV2-W48 OCR, Cityscapes) and +1.5/+1.6 (ADE20K/COCO-Stuff with the same backbone). The same model with no outlier data gives Fishyscapes L&F AP 43.5 against 6.0 for MSP.
- **Our failure modes:** *rare classes, unseen modules, false cracks.* Several components per class fit multi-modal classes: a crack looks different in each of the 5 sources and on mono versus multi cells. The class likelihood is a free "unknown region" map on E1 (scuff, cut edge) that could stop false cracks.
- **Risk:** not tested on thin or rare classes. EM on a few crack pixels may be noisy.

**4. CSST, efficient self-training** (doi:10.1109/tpami.2021.3138337, TPAMI, NEW). Full text read.
- **Mechanism:** an offline teacher writes pseudo-labels on unlabelled images. *Centroid sampling* crops patches around the centroid of every class region, so rare classes appear in every epoch. Pseudo and real labels are mixed at a fixed ratio.
- **Evidence:** at FULL Cityscapes labels, mIoU went from 78.1 to 79.3 at a 1:1 pseudo:real ratio and to 80.0 at 7:1. Students with other architectures gained +1.7 to +3.9. Centroid sampling was worth +1.1, and without it adding pseudo-labels hurt (78.9 to 78.7).
- **Our failure modes:** *recall on unseen modules and half-cut.* Our SSL null was online Mean Teacher without class-aware crops. The arm: the C2 ensemble labels the 11.9k pool including the 1,152 half-cells, crops are centred on pseudo crack and inactive components, and the ratio is 7:1.
- **Risk:** teacher errors on half-cut cells are the E1 failure itself. Combine with a robust pseudo-label rule (ECOCSeg P473, or the ICCV 2025 selection paper). D29's offline-teacher rows (P051, P180) are the same family; CSST adds the rare-class sampler, which is the part their gains depended on.

**5. BGAD** (doi:10.1109/cvpr52729.2023.02346, CVPR 2023, NEW, code yes). Full text read.
- **Mechanism:** a normalizing flow on normal features sets an explicit boundary from the normal distribution alone. A semi-push-pull loss pushes known anomalies only beyond a margin, so they do not bias the detector.
- **Evidence:** when trained with one anomaly class and tested on the others (Table 4), pixel AUROC does not drop: carpet 0.994 to 0.995, metal nut 0.966 to 0.975. MVTec pixel AUROC/PRO is 0.992/0.976.
- **Our failure modes:** *unseen modules.* An auxiliary defect-versus-normal flow head on HRNet features uses our crack and inactive pixels as "known anomalies". Its boundary is set by crack-free pixels only, so defects that look unlike training cracks (new module, new contrast) should still fall outside it.
- **Risk:** the gains are at AUROC 0.97 to 0.99, not in tolerant F1. The flow at 1/4 resolution may be coarse.

**6. MuSc-V2** (doi:10.1109/tpami.2026.3688174, TPAMI 2026, NEW; MuSc v1 is P272, BENCH_ONLY; code announced). Method and results read.
- **Mechanism:** a zero-shot score in which each unlabelled sample scores every other sample's patches. Normal patches find many matches; anomalies stay isolated.
- **Evidence:** splitting the data into 2 or 3 subsets costs at most 1.0 to 1.2% AP.
- **Our failure modes:** *unseen modules.* Batch all cells of one new module. Its own layout and contrast then become "normal" with no reference set from our pool, so half-cut cells do not need half-cut references.
- **Risk:** the patch grid is coarse, so use it as an inactive prior and a cell-level flag, not a crack prior. Module-wide repeated defects are not isolated and get low scores.

**7. ISP-AD** (doi:10.1007/s10845-025-02778-z, J. Intelligent Manufacturing 2026, NEW). Full text read.
- **Mechanism:** a mixed supervised stream. Clean patches carry model-free synthetic defects, and real defects are injected at probability 1/32.
- **Evidence:** the background is a periodic printed pattern with small, weak-contrast defects, like fingers and busbars. LSM-1 recall went from 76.8% to 95.8% (false negatives 22 to 4), and 10 real defects alone raised MCC from 0.81 to 0.91. ASM MCC went from 0.70 to 0.97. Real defects of types the generator cannot make were recovered.
- **Our failure modes:** *rare inactive and half-cut.* The recipe mirrored for us: keep the 532 real cells and add a controlled synthetic dark-line and dark-region stream on clean pool cells, including half-cells.
- **Risk:** classification at patch level, not pixel segmentation. Our crack copy-paste, HC and HC2 failed. The open question is whether the injection-rate control is what was missing.

**8. RPL** (doi:10.1109/iccv51070.2023.00112, ICCV 2023, NEW). Full text read.
- **Mechanism:** a residual block between the *frozen* backbone and head. It keeps inlier predictions and raises energy on outlier pixels, with context-robust contrastive learning.
- **Evidence:** the inlier segmentation is untouched. On Fishyscapes, SMIYC and RoadAnomaly it improves on the state of the art by about 10% FPR and 7% AuPRC.
- **Our failure modes:** *precision under half-cut layout.* Train only the block on top of frozen C2, using pool cells with pasted nuisance textures (scuffs, cut edges), to flag E1 false cracks. This guards precision while other arms push recall.
- **Risk:** it does not add recall. Its value depends on an outlier source that looks like E1 nuisances.

**9. SegAD** (doi:10.1109/cvpr52733.2024.01681, P449, PARKED). Full text read.
- **Mechanism:** a boosted random forest on per-segment statistics of AD maps, plus a supervised classifier score.
- **Evidence:** adding AD maps to the supervised WRN classifier gives FPR@95TPR 32.8 to 16.4 and AUROC 95.0 to 96.5. The score distribution of unseen defects moves up to that of seen defects. Per-segment features beat a global maximum (+2.1 AUROC in the ablation).
- **Our failure modes:** *unseen modules.* This is the cleanest evidence that an AD map adds information a supervised model lacks on unseen defects. A cheap use: a cell-level "missed defect" flag from MetaUAS or MuSc maps per structural segment (busbar zone, edge, cut gap), used to trigger a lower crack threshold on that cell.
- **Risk:** image-level only, measured on one product.

**10. YoloCurvSeg** (doi:10.1016/j.media.2023.102937, MedIA 2023, NEW, code yes). Abstract only.
- **Mechanism:** inpaints dilated skeletons to make realistic backgrounds, renders random curves (space colonisation) with a contrastive synthesiser, and trains on the result. With one noisy skeleton label it reaches more than 97% of full supervision on four vessel datasets.
- **Our failure modes:** *half-cut layout.* Inpainted backgrounds from real pool half-cells plus rendered cracks give pixel-exact labelled half-cut cells. This differs from our copy-paste, which reused real crack crops on full cells.
- **Risk:** rendered curves may not look like EL cracks. Vessels are wider and brighter.

Below the top 10 (scores 1 to 2): PyramidFlow (full-resolution AD, abstract only), UniVAD, ADShift (AD under distribution shift), the combined anomaly-aware weakly supervised model (TII 2024) and anomaly-guided OCT WSSS (two more examples of "AD map as prior to a downstream net", both weakly supervised), BoxTeacher with PVEL-AD boxes, Tree Energy Loss (±2 px band as unlabelled), ReContrast (domain-adapted AD encoder), and diffusion AD (DiAD, DiffusionAD, the CVPR 2025 reformulated diffusion) as a CrackCue-style residual channel.

## Cheapest decisive checks (no training for the first two)
1. MetaUAS zero-shot maps, with the prompt being a clean same-layout pool cell, on CV validation folds and on held-out half-cut pool cells. Measure the fraction of crack components ≥20 px that C2 misses and that fall in the top 1% of the map. Kill the arm if this is under 30% (same rule as D39 #1).
2. MuSc batch maps per module on the CV folds, used as an inactive prior. Measure the AUROC for inactive pixels that C2 misses.
3. Pixel contrast loss on C2, 2 seeds. Then GMMSeg head on C2, 2 seeds. Then CSST pool self-training with centroid crops (teacher = C2 ensemble), 2 seeds. Each is judged by the standard M = 0.010 rule plus the guards.

## Queries run (search_papers; year filter in brackets)
1. anomaly map as input prior supervised segmentation rare defect (2022+)
2. MVTec AD 2 benchmark anomaly segmentation small defects (2025+)
3. unsupervised semantic segmentation self-supervised features STEGO (2022+)
4. supervised segmentation network with anomaly detection branch unseen defects generalization (2023+)
5. self-training full labeled data segmentation improves distillation self-distillation (2021+)
6. pixel-level contrastive learning supervised semantic segmentation rare classes (2021+)
7. exploring cross-image pixel contrast for semantic segmentation (2021+)
8. CutLER cut and learn unsupervised object detection instance segmentation (2022+)
9. diffusion model features unsupervised segmentation EmerDiff emerging (2023+)
10. weakly supervised crack segmentation scribble point box annotation (2021+)
11. mixed supervision segmentation combining pixel labels and weak labels improves fully supervised (2020+)
12. AA-CLIP anomaly-aware CLIP zero-shot anomaly segmentation (2024+)
13. semi-supervised semantic segmentation full labeled set extra unlabeled data gains AllSpark CorrMatch (2023+)
14. photovoltaic electroluminescence anomaly detection unsupervised defect localization (2022+)
15. pseudo-healthy reconstruction residual input channel improves supervised lesion segmentation (2019+)
16. anomaly segmentation outlier exposure semantic segmentation unknown objects mask transformer (2022+)
17. diffusion model industrial anomaly detection localization reconstruction DiAD (2023+)
18. Real-IAD real-world multi-view industrial anomaly detection dataset (2024+)
19. few-shot anomaly segmentation foundation model reference normal images DINOv2 patch matching unseen products (2024+)
20. supervised anomaly detection seen and unseen anomalies pixel-level segmentation few labeled defects (2024+)
21. fusion of unsupervised anomaly score and supervised defect segmentation hybrid improves recall unseen defect types (2021+)
22. anomaly detection thin scratch crack hairline defect localization resolution (2023+)
23. supervised contrastive loss curvilinear vessel segmentation pixel embedding hard negatives (2021+)
24. contrastive learning crack segmentation pixel-wise (2022+)
25. AllSpark reborn labeled features from unlabeled transformer semi-supervised (2023+)
26. CorrMatch label propagation correlation matching semi-supervised segmentation (2023+)
27. AnomalyGPT large vision-language model industrial anomaly detection (2023+)
28. unified model multi-class anomaly detection UniAD transformer reconstruction (2022+)
29. RealNet feature selection realistic synthetic anomaly strength-controllable diffusion (2024+)
30. self-knowledge distillation semantic segmentation without teacher improves fully supervised baseline (2020+)
31. image-level labels plus pixel labels multi-task weak supervision improves segmentation rare class large unlabeled pool (2020+)
32. SimpleNet PaDiM DRAEM anomaly localization VisA benchmark (2020+)
33. box-supervised segmentation thin structures bounding box annotations crack defect (2021+)
34. partially labeled multi-dataset segmentation extra weakly annotated images boxes improve fully supervised model (2021+)
35. long-tailed semantic segmentation pixel contrastive learning tail classes recall (2022+)
36. combining unsupervised anomaly detection with supervised segmentation lesions improves detection of rare unseen pathologies (2021+)
37. anomaly-aware semantic segmentation known classes plus unknown defect fusion industrial open-set segmentation (2023+)
38. self-training pseudo-labels unlabeled target domain fully supervised source improves generalization unseen domain segmentation medical (2022+)
39. anomaly detection under distribution shift test-time normal reference domain generalization industrial (2023+)
40. SimpleNet / PaDiM / SPot-the-difference VisA (2020 to 2023)
41. PaDiM patch distribution modeling framework anomaly detection localization (2020 to 2022)
42. SPot-the-difference self-supervised pre-training anomaly detection segmentation VisA dataset (2022)

Also run: search_snippets "anomaly map as an additional input channel to a supervised segmentation network improves recall" (failed, Semantic Scholar rate-limited). get_citations on SegAD, Bozic 2021, MuSc and ContrastSeg (ICCV). similar_papers on [SegAD, WeakREST, SuperSimpleNet].

## NOT_FOUND / gaps
- **AD prior fused into a supervised multi-class pixel segmenter at full labels, with per-class pixel gains.** Searched through queries 1, 4, 15, 21, 36 and 37, the snippet query, and SegAD citations and similar papers. I found none; the nearest are image-level (SegAD, ISP-AD) or weak-label (TII 2024, MedIA 2024).
- **Contrastive or prototype losses evaluated on thin cracks or vessels at full labels.** Queries 23 and 24 returned only architecture papers.
- **Self-training at full labels on a thin-structure or defect task with an unseen-domain test.** Query 38 returned only UDA, source-free DA and SSL-at-low-labels papers.
- **EL-specific pixel-level AD beyond what MASTER already holds** (EI-AE P235, PV-ReAD P551, E-SCDD P042). New finds were SeMaCNN (heterojunction, abstract preview only) and a few-shot rare-defect EL detector (no abstract in index).
- Papers I expected but did not search for by name, so they are not in the TSV: RbA and PEBAL (driving OOD segmentation; RPL, Mask2Anomaly and GMMSeg cover the role), DINO-Mix (already in D29). I am not claiming these as findings.
- Not verified: code for GMMSeg, RPL, CSST, PyramidFlow and ContrastSeg (repo links were not in the text I read). MuSc-V2 code is "will be available" in its abstract.
