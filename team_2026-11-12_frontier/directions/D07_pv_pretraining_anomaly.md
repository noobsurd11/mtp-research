# D07: PV / EL self-supervised pretraining, foundation models, unsupervised anomaly detection

Scout: D07. First pass 12 Nov 2026, revised and re-verified 13 Nov 2026.
R = what a paper measured, E = what our files measured (from BRIEF), S = my judgement.

## 1. Queries run

Research MCP search_papers (OpenAlex and arXiv answered; Scopus 401, ScienceDirect 401, Semantic Scholar rate-limited all session):

13 Nov pass (17 searches):
1. "self-supervised learning electroluminescence solar cell" (2020+)
2. "anomaly detection electroluminescence solar cell unsupervised" (2020+)
3. "foundation model photovoltaic inspection" (2023+)
4. "contrastive pretraining electroluminescence images defect" (2020+)
5. "electroluminescence solar cell anomaly segmentation normal samples only" (2024+)
6. "masked autoencoder pretraining solar cell defect" (2022+)
7. "segment anything model electroluminescence photovoltaic defect segmentation" (2023+)
8. "DINOv2 anomaly detection industrial few-shot zero-shot segmentation" (2024+)
9. "unsupervised anomaly detection thin crack localization reconstruction" (2022+)
10. "Hanifi solar cell defect dataset electroluminescence unlabeled" (2024+)
11. "Dinomaly multi-class unsupervised anomaly detection reconstruction" (2024+)
12. "domain-specific self-supervised pretraining industrial defect segmentation large unlabeled" (2024+)
13. "photovoltaic electroluminescence anomaly detection" (2025+)
14. "vision foundation model fine-tuning solar cell defect segmentation electroluminescence" (2025+)
15. "self-supervised pretraining photovoltaic cell images unlabeled defect segmentation" (2025+)
16. "anomaly map prior fused supervised segmentation network rare defects recall" (2022+)
17. "weakly supervised anomaly segmentation few labeled anomalies pixel-level industrial" (2024+)
18. "PatchCore EfficientAD solar cell electroluminescence anomaly localization" (2022+, 1 hit)

12 Nov pass (kept, 21 searches): adds ExPLoRA, AnomalyDINO, MuSc, SuperSimpleNet, scale-aware SSL, DINOv3 gram anchoring, weakly supervised EL localisation, anomaly prior as segmentation input, BGAD, PatchCore and CCT id lookups.

Snowballing: similar_papers on [arxiv:2402.17611, doi:10.1039/d5ee05042a, arxiv:2511.09604]; get_citations on arxiv:2402.17611 (1 citer: AGSSP), Dinomaly (171 citers, found INP-Former, WSRT, MuSc-V2 line), PVEL-AD (280 citers, nearly all YOLO detectors). 12 Nov: citations of MuSc.
search_snippets: 2 tries this pass, both rate-limited (S2 keyless pool). So evidence on "cracks versus dark areas" rests on abstracts, full text of Torpey, AGSSP and Hanifi, and my judgement.
read_paper (already in library): Torpey (results, defect analysis, conclusion), AGSSP (main results table), Hanifi PV-DDPM (AD results, code). WebFetch of the EI-AE RSC full text: HTTP 403.
WebSearch (6 this pass): EL + DINOv2/v3/foundation 2026; pv-ddpm repo; AGSSP code; MuSc / AnomalyDINO / Dinomaly repos; PV-ReAD code (none found).

## 2. What the EL literature says (R) and what it means here (S)

- **Torpey, Pratt, Klein 2024 (arxiv:2402.17611)**, same CSIR / BenchmarkEL family. DeepLabV3. mIoU: random 0.486, ImageNet-sup 0.508, EL-SimCLR (in-domain unlabelled) 0.517, ImageNet-SimCLR 0.534, COCO segmentation pretraining 0.544, CCT 0.550, U2PL 0.448. Crack IoU: COCO and ImageNet-SimCLR beat all others (p <= 1e-4), including CCT. Authors: "the multiview nature of various SelfSL/SemiSL techniques is ill-suited to the EL semantic segmentation task". Release of 22k unlabelled EL images. CCT and U2PL were single runs.
  - S: agrees with our E (MIM, DDeP on the 11.9k pool: n.d.). The one distinct positive signal is a pretrained decoder from a dense task (COCO-seg). Our UCF-EL pretraining was erased by the house fine-tune, so "dense pretraining kept by PF" is still open.
- **AGSSP (arxiv:2509.18919, Pattern Recognition 2026)**, metal surfaces, 120k unlabelled industrial images. R (Table 2): plain in-domain classification or MoCo v3 pretraining is about 0 or negative (-3.6 to +2.9 mAP@.5:.95); distilling anomaly maps into the backbone (AGBP) gives -1.5 to +4.0; adding detector pretraining on pseudo-defect boxes from anomaly maps (AGSSP) gives +2.0 to +11.4 mAP@.5:.95, largest on small sets (GC10-Mini +5.4, Casting Billet-Mini50 +21.6 to +24.5). COCO detection pretraining is close to AGSSP on several sets.
  - S: same pattern as Torpey. The gain is in pretraining the localisation head on dense pseudo-targets, not in the backbone objective. This is the most transferable D07 idea for us.
- **Hanifi et al. 2025, PV-DDPM / E-SCDD (arxiv:2511.09604)**, the group that redistributed our revised labels. R: AA-CLIP (vision-language AD) trained on E-SCDD, all defects merged into one anomaly class: full-shot pixel AUROC 94.96, pixel AP 55.47; 2-shot pixel AP 17.79; image AUROC is unstable (52 to 98). Code github.com/sntubix/pv-ddpm (WebSearch confirms the link; contents not checked).
  - S: pixel AP 0.55 for a binary "any defect" map, on the same data family, is far below our supervised crack relF1@2 0.88. This is the first public AD number on our data; a benchmark AD track can cite it directly.
- **EL anomaly detection 2021 to 2026**: Balzategui 2021 (GAN), Korovin / SeMaCNN 2022-23, Otamendi 2021-22, EI-AE (Lin 2025, EES), PV-ReAD (Liu 2026, Solar Energy: pixel AUROC 99.7, AP 98.7, AUPRO 77.8 on a new U-PVEL-AD-seg), UniDisc (Lv 2026, Solar Energy: image AUROC only, multi-line shift). None reports crack-only pixel IoU on thin labels, and none uses a cross-source or unseen-module test.
  - S (cracks versus dark areas): patch-feature AD (stride 8 to 16 px) resolves blobby dark regions (inactive, dark edges, scuff) but marks a 14 to 28 px band around a crack at best. PV-ReAD's 98.7 pixel AP on PVEL-AD masks says nothing about 1 to 2 px labels. So AD is a candidate for problem 2 (inactive) and problem 3 (E1 detection, relF1@2), not for strict crack IoU. Scuff on E1 will also score as anomalous: an AD prior can raise recall where the house model has p(crack) < 0.001, not separate scuff from crack.
- No EL paper using DINOv2 / DINOv3 / SAM fine-tuning with pixel-level evaluation was found (WebSearch 13 Nov agrees). Song 2025 (doi:10.1016/j.solener.2025.114145, fine-tuned SAM + PV domain knowledge) has no abstract in any index: unverified.

## 3. Selected papers

Scores: "score" = value for raising our scores (rubric in task); "bench" = value for the benchmark suite / design.

| # | id | year | venue | code | mechanism | adaptation to our data | score | bench |
|---|---|---|---|---|---|---|---|---|
| 1 | doi:10.1016/j.patcog.2026.113788 (arxiv:2509.18919) AGSSP | 2026 | Pattern Recognition | project page clovermini.github.io/AGSSP-Dev (repo link not confirmed) | Label-free anomaly maps on a large unlabelled pool; distil them into the backbone, then pretrain the localisation head on pseudo-defects; fine-tune | AD maps (AnomalyDINO or INP-Former, refs = same source and layout) on the 11.9k pool, later 159k; pretrain whole U-Net++ (encoder + decoder) with a 1-ch soft anomaly head (soft BCE on the map) jointly with the 24-class head on the 478 labelled; PF fine-tune so the decoder survives | 55 | 45 |
| 2 | arxiv:2402.17611 Torpey et al. | 2024 | arXiv | not found | Benchmark of pretraining regimes on EL segmentation; dense-task pretraining with a transferred decoder beat in-domain SimCLR, CCT best mIoU | Pretrain U-Net++ encoder AND decoder on a dense EL task (UCF-EL 9.5k polygons + MultiSolSegment 585, mapped to a coarse 5-class space), then PF fine-tune keeping the decoder; take their 22k unlabelled release as extra pool | 50 | 85 |
| 3 | doi:10.1007/978-3-032-38082-1_10 (arxiv:2508.20909) Dino U-Net | 2026 | MICCAI (LNCS) | github.com/yifangao112/DinoUNet (from abstract) | Frozen DINOv3 + adapter fusing low-level spatial detail + fidelity-aware projection into a U-Net decoder; accuracy grows with backbone size up to 7B | 1-ch EL repeated to 3 ch; DINOv3 ViT-L/16 at 512 gives 32x32 tokens, so a conv stem skip at 1/2 and 1/4 must carry cracks; keep CE + soft Dice on crack / inactive; 24 classes | 50 | 65 |
| 4 | arxiv:2406.10973 ExPLoRA | 2024 | arXiv (ICML 2025 per earlier web check, unverified this pass) | project page samar-khanna.github.io/ExPLoRA | Continue the DINOv2 / MAE objective on the new domain with LoRA on all blocks plus 1-2 unfrozen blocks, then LoRA fine-tune | Continue DINOv2 (or v3) ViT-L SSL on the 159k CSIR / ARTS pool (crops 224 to 448, 1-ch to 3-ch, include the 1,152 multi half-cells so E1-like layouts are seen), then plug into #3 | 45 | 55 |
| 5 | doi:10.1109/icassp55912.2026.11464176 (arxiv:2601.18619) Scale-aware SSL | 2026 | ICASSP | unverified | Small-window crops in SSL augmentation so the pretext task sees fine sparse structures; up to +13% on seismic fault (thin line) segmentation, little gain on large regions | Redo pool SSL (DINO / SimCLR, ResNet-34) with 32 to 96 px windows upsampled, 50% centred on dark ridges (black top-hat / Frangi response), 50% uniform; house / PF fine-tune | 48 | 35 |
| 6 | doi:10.1109/cvpr52734.2025.00932 (arxiv:2503.02424) INP-Former | 2025 | CVPR | github.com/luow23/INPFormer (from abstract) | Normal prototypes extracted from the test image itself guide reconstruction; no external reference set needed; few-shot and some zero-shot ability | Fits E1: half-cut layouts and new modules have no matching reference in train. Train on clean pool cells (all sources and layouts); per-cell anomaly map as a recall prior for inactive and crack components; repeated within-cell structure (fingers, busbars) is self-normalised | 45 | 65 |
| 7 | arxiv:2401.16753 MuSc (and MuSc-V2, doi:10.1109/tpami.2026.3688174) | 2024 / 2026 | ICLR / TPAMI | github.com/xrli-U/MuSc (WebSearch confirmed); MuSc-V2 github.com/HUST-SLOW/MuSc-V2 (from abstract) | Training-free: each patch is scored against patches of the other unlabelled images; normal patches are common, anomalies isolated | Transductive per E1 module group and per source: score each cell against the other cells of its module and layout; scuff repeated across a module partly self-cancels (useful here); output as recall prior | 45 | 60 |
| 8 | doi:10.1109/wacv61041.2025.00136 (arxiv:2405.14529) AnomalyDINO | 2025 | WACV | github.com/dammsi/AnomalyDINO (WebSearch confirmed) | Training-free patch kNN on DINOv2 features against a few normal references | References = clean pool cells of the same source and layout (1,152 pool half-cells give half-cut references). The pool contains defects, so filter the memory bank (SoftPatch-style outlier removal, doi:10.1016/j.patcog.2024.111295) or pick refs the house ensemble calls clean; 448 px, ViT-S/14 and ViT-L/14 | 42 | 70 |
| 9 | doi:10.1007/s10845-025-02680-8 (arxiv:2508.19060) SuperSimpleNet | 2025 | J. Intell. Manuf. | github.com/blaz-r/SuperSimpleNet (from abstract) | One discriminative defect model for unsupervised, weak, mixed and full supervision; feature-space synthetic anomalies + seg and cls heads, <10 ms | Mixed supervision: 478 pixel-labelled cells + pool cells tagged image-level "clean" by the house ensemble; binary defect map (crack OR inactive OR material) as an ensemble member and as the AD-family benchmark baseline | 40 | 70 |
| 10 | arxiv:2307.07245 FreeCOS | 2023 | ICCV | github.com/TY-Shi/FreeCOS (from abstract, 12 Nov) | Label-free curvilinear segmentation: fractal curves blended into unlabelled images, Fourier domain adaptation, intensity-order alignment, mask contrastive loss | Render L-system cracks as dark Gaussian dips (FWHM 3-5 px, 2-20% contrast, per source) into crack-free pool cells, label a 1.75 px centreline; use as a crack-branch pretraining stage, then house fine-tune | 40 | 35 |
| 11 | arxiv:2502.08321 Screener | 2025 | arXiv | "will be released" (unverified) | Dense SSL features + density-based anomaly segmentation with learned masking-invariant conditioning; trained on 30k unlabelled CT; also beats other SSL pretraining when fine-tuned supervised | Two uses of one pretraining on the 159k pool: (a) dense SSL encoder for U-Net++ (the open "dense objective" row of section 5), (b) density model on the same features as label-free anomaly map; conditioning variable = cell layout / source embedding instead of position | 35 | 35 |
| 12 | doi:10.1109/cvpr52733.2024.01681 (arxiv:2405.04953) SegAD | 2024 | CVPR | github.com/abc-125/segad (from abstract) | Per-region statistics of anomaly maps inside segmentation-map regions + a supervised score feed a boosted random forest for the final decision | Post-evaluation / severity: per-cell features = house crack / inactive probabilities and AD scores inside structural regions (busbar, ribbon, cell body); BRF predicts "cell has crack >= 20 px" and inactive-fraction band; raises cell-level crack recall without touching pixel IoU | 35 | 55 |
| 13 | doi:10.1109/cvpr52734.2025.01900 (arxiv:2405.14325) Dinomaly | 2025 | CVPR | github.com/guojiajeremy/Dinomaly (WebSearch confirmed; in Anomalib 2.1) | Normal-only feature reconstruction on a DINOv2 encoder, noisy bottleneck, linear attention, loose reconstruction; one model for many classes | One model across 5 sources x mono / multi / half-cut (the "multi-class" setting) on clean pool cells; map evaluated against inactive and crack dilated by 2 px; prior channel for E1 | 35 | 75 |
| 14 | arxiv:2511.09604 PV-DDPM / E-SCDD | 2025 | arXiv | github.com/sntubix/pv-ddpm (WebSearch); data huggingface snt-ubix/e-scdd (from paper) | Mask-conditioned diffusion of EL defects across 4 cell types incl. half-cut; AA-CLIP AD trained on the result reaches pixel AUROC 94.96 / AP 55.47 | For D07: AA-CLIP on E-SCDD is the published AD baseline on our data family; rerun it under our split and metrics. For scores: half-cut synthetic cells with defects are E1-like training data (overlaps D06 / D33) | 30 | 70 |
| 15 | doi:10.1016/j.solener.2026.115300 PV-ReAD | 2026 | Solar Energy | not found (WebSearch) | EL-specific reconstruction AD: multi-layer adaptive fusion, adaptive noisy bottleneck, global cosine focal loss; pixel AUPRO 77.8 on new U-PVEL-AD-seg | EL-native AD baseline for the benchmark; reimplement as Dinomaly + their loss if no code; check whether U-PVEL-AD-seg masks are public as extra pixel labels | 25 | 60 |
| 16 | doi:10.1039/d5ee05042a EI-AE | 2025 | Energy Environ. Sci. | unverified | Iterative autoencoder for normal-only pixel segmentation of EL defects; extendable to few-shot with a few masks | EL-native AD baseline; train on clean cells per source; few-shot arm with the 42 inactive cells | 25 | 60 |
| 17 | doi:10.1109/cvpr42600.2020.01269 (arxiv:2003.09005) CCT | 2020 | CVPR | unverified | Consistency between a main decoder and auxiliary decoders fed perturbed encoder features on unlabelled images | Best mIoU in Torpey on this data family. U-Net++ with 3 to 6 auxiliary decoders, pool as unlabelled, at 100% labels; feature perturbation, not pseudo-labels | 25 | 60 |
| 18 | doi:10.1007/s11263-026-02743-0 (arxiv:2503.21622) MVTec AD 2 | 2026 | IJCV | benchmark server (from abstract, 12 Nov) | AD benchmark with hidden test ground truth, shifted-lighting test splits, very small defects; SOTA below 60% AU-PRO | Template for our benchmark: hidden E1-style test, a shift split (half-cut, unseen modules), thresholded per-image metrics, an AD track next to the supervised track | 10 | 80 |

## 4. Cheapest decisive experiments

All at 100% labels (no 5% screens), 5 seeds, primary instrument = module-grouped 5-fold CV over 532 train + val cells and F51; clean-49 test read once at the end; E1 read once at the end.

- **#1 AGSSP-EL.** Arm: U-Net++ pretrained on pool with soft anomaly head + labelled 24-class head, then PF fine-tune. Baseline: PF. Metrics: CV inactive IoU, CV crack relF1@2, then E1 crack relF1@2 and inactive IoU. Kill: CV inactive gain < +0.02 and CV crack relF1@2 gain < +0.01. About 45 GPU-h.
- **#2 dense decoder pretraining.** Arm: U-Net++ pretrained on UCF-EL + MultiSolSegment (encoder + decoder), PF fine-tune keeping the decoder. Baseline: PF from ImageNet. Metric: CV mIoU_rob, CV inactive IoU. Kill: mIoU_rob gain < +0.01 and inactive gain < +0.02. About 20 GPU-h.
- **#3 / #4 Dino U-Net, with and without ExPLoRA.** Baseline: PF. Metrics: CV crack IoU and relF1@2, then E1 crack relF1@2. Kill: both arms below PF on CV crack IoU by > 0.01 and < +0.03 on E1 relF1@2. About 30 GPU-h (#3), +150 GPU-h (#4).
- **#5 scale-aware SSL.** Arm: ResNet-34 SSL on pool with small ridge-centred windows, PF fine-tune. Baseline: PF and the existing MIM checkpoint. Metric: CV crack IoU, crack components >= 20 px found. Kill: crack IoU gain < +0.012 (smallest detectable). About 40 GPU-h.
- **#6 / #7 / #8 AD recall prior (offline first, no seg training).** Compute INP-Former, MuSc and AnomalyDINO maps on F51, H36 and the CV folds. Measure, on components the house PF ensemble misses (p < 0.001): fraction recovered at a threshold that flags 1% of cell area. Then fuse (raise crack / inactive logits inside high-AD components, threshold chosen on CV). Baseline: PF ensemble. Kill: < 30% of missed components recovered at 1% area, or fused relP@2 drops by more than relR@2 rises. Under 5 GPU-h.
- **#9 SuperSimpleNet mixed.** Arm: PF ensemble + SuperSimpleNet binary map as an extra member for crack / inactive recall. Baseline: PF ensemble. Metric: CV relR@2 at relP@2 >= 0.90. Kill: relR@2 gain < +0.02. About 10 GPU-h.
- **#10 FreeCOS-style.** Arm: crack head pretrained on synthetic fractal cracks in clean pool cells, then house fine-tune. Baseline: house. Kill: CV crack relR@2 gain < +0.02 at equal relP@2. About 15 GPU-h.
- **#11 Screener-style dense SSL.** Arm: dense SSL ResNet-34 / ConvNeXt-T on 159k pool, PF fine-tune. Baseline: PF and the MIM checkpoint. Kill: CV crack IoU gain < +0.012 and inactive < +0.02. About 60 GPU-h.
- **#12 SegAD cell-level.** Arm: BRF on house + AD region statistics. Baseline: house ensemble "max crack prob" per cell. Metric: cell-level crack recall at 95% cell-level precision on CV and E1. Kill: recall gain < +0.03. Under 2 GPU-h.
- **#13 to #16 benchmark AD track.** Train each once, report pixel AUROC, AU-PRO, relF1@2 per class, cell-level AUROC. No kill line; this is suite content.
- **#17 CCT.** Arm: U-Net++ + CCT aux decoders, pool unlabelled, 100% labels. Baseline: house. Kill: CV mIoU_rob gain < +0.01. About 30 GPU-h.

## 5. Notable papers rejected

- Dai et al. 2024, SAM + feature fusion on ELPV (doi:10.1109/icsmd64214.2024.10920517): no pixel ground truth.
- Korovin et al., SeMaCNN (arxiv:2208.05994; doi:10.1016/j.solener.2023.04.059): heterojunction cells, image-level metrics, no code.
- UniDisc (doi:10.1016/j.solener.2026.114674): module-level multi-line shift, image AUROC only; mechanism (feature decorrelation under line shift) is interesting for E1 but no pixel evidence.
- Otamendi 2022 annotation framework (doi:10.1109/tii.2022.3228680) and Balzategui 2021 GAN AD-to-label (doi:10.3390/s21134361): older AD-as-labeller ideas, superseded by #6 to #8 and owned by the label-refinement direction.
- WinCLIP / AnomalyCLIP / AdaCLIP family: text prompts on grayscale EL are unproven; AA-CLIP (#14) already covers the VLM AD baseline.
- BGAD (arxiv:2207.01463), AHL (arxiv:2310.12790), WSRT (doi:10.1109/tip.2026.3659337): few-anomaly supervised AD; we already have full pixel labels.
- Lightweight AE / CAE EL papers 2025-26 (doi:10.1016/j.solener.2026.114362, doi:10.1080/10589759.2025.2456673): no distinct mechanism beyond #15 / #16.
- Generic EL classification and YOLO papers 2025-26 (dozens in the PVEL-AD citers): classification or boxes only.
- Surveys (Cui 2023, Cheng 2026 JMS, Li 2025 AIR, Tao 2022): no new mechanism.

## 6. Gaps

- No paper reports crack-only pixel metrics for unsupervised AD on EL against thin labels, nor any cross-source or unseen-module AD test. Our offline experiment (#6 to #8) would be the first number, and a natural benchmark AD track.
- EI-AE (RSC, 403) and PV-ReAD (Elsevier) full texts were not readable off campus; their per-defect numbers (crack vs dark area) are unknown. Read on campus.
- Whether the U-PVEL-AD-seg pixel masks (PV-ReAD) are public: unknown. If so, they are extra pixel labels for multi-dataset training.
- Torpey's 22k unlabelled release: link not found; overlap with the 159k Pratt pool unknown.
- Continued DINOv2 / v3 pretraining on EL at native 1200 px: no paper found.
- EL-IR or EL-PL contrastive pretraining on paired data: no paper found (public pairs are module-level).
- search_snippets was rate-limited both passes, so evidence questions rest on abstracts and three full texts.
