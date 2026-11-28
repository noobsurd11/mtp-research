# Scout `dg`: generalising to unseen domains and new layouts

Scout dg, 27 Nov 2026. This scout only read papers. Nothing was trained or run on a server.
Family covered: domain-generalised semantic segmentation (DGSS), single-source DG in medical imaging, geometry and layout shift, test-time training and adaptation, source-free adaptation, few-shot and cross-domain few-shot segmentation, few-shot fine-tuning, and active learning (choosing which cells to label in a new layout).
Earlier sweeps of 12 Nov read first: D30 (DG/UDA) and D31 (TTA). Rows that duplicate them are marked with their MASTER pid, or with "D30/D31 judged ...". Items they had already ranked high (MIC, FDA, SLAug, DAFormer RCS, SWAD, PIE, SGP-TTA, TopoTTA) are not repeated here.

## Status of the search tools
- Semantic Scholar was rate-limited for the whole session. As a result `search_snippets` failed and `get_citations` only worked through the other indexes.
- The arXiv source timed out on most queries, so preprints from 2025 and 2026 are probably under-covered.
- Scopus, OpenAlex and ScienceDirect worked.

## Queries run (`search_papers`, 39)
1. domain generalized semantic segmentation vision foundation model (2024+)
2. cross-domain few-shot semantic segmentation (2022+)
3. active learning semantic segmentation region selection annotation budget (2020+)
4. active domain adaptation semantic segmentation few target labels (2021+)
5. style hallucination domain generalization semantic segmentation SHADE
6. instance batch normalization IBN-Net generalization
7. RobustNet instance selective whitening domain generalization urban scene segmentation
8. semantic-aware normalization whitening SAN-SAW domain generalized segmentation
9. few-shot fine-tuning segmentation new domain baseline transfer learning simple (2020+)
10. text queries language-guided domain generalized semantic segmentation tqdm (2023+)
11. spatial layout geometric shift segmentation generalization position prior shape change (2019+)
12. crack segmentation domain generalization unseen dataset cross-dataset (2021+)
13. photovoltaic electroluminescence defect detection cross-domain generalization different manufacturer (2020+)
14. test-time training auxiliary self-supervised task segmentation domain shift (2020+)
15. source-free domain adaptation segmentation thin structures vessel road (2021+)
16. semi-supervised domain adaptation semantic segmentation few labeled target images (2020+)
17. cold-start active learning medical image segmentation sample selection self-supervised features (2021+)
18. few-shot industrial defect segmentation unseen product (2021+)
19. robust fine-tuning weight interpolation WiSE-FT distribution shift zero-shot (2021+)
20. diffusion model data augmentation domain generalization medical image segmentation controllable (2023+)
21. MixStyle feature statistics uncertainty DSU domain shift (2020+)
22. test-time adaptation semantic segmentation 2025 continual robust class imbalance (2024+)
23. how many annotated images segmentation new site fine-tuning learning curve annotation efficiency (2019+)
24. single-source domain generalization segmentation augmentation shape bias location-scale (2023+)
25. how much position information do convolutional neural networks encode padding absolute position
26. context bias out-of-context segmentation spurious background co-occurrence augmentation (2019+)
27. surface defect segmentation domain generalization unseen scenarios steel rail (2021+)
28. multi-source domain generalization medical image segmentation unseen site (2020+)
29. active learning crack segmentation label-efficient annotation (2020+)
30. domain generalization curvilinear tubular structure segmentation unseen modality (2022+)
31. source-free domain adaptation medical image segmentation pseudo-label denoising (2022+)
32. domain adaptation crack segmentation few labeled target samples fine-tuning (2021+)
33. electroluminescence solar cell anomaly unsupervised segmentation new cell type half-cell (2019+)
34. which layers to fine-tune domain shift segmentation medical layer-wise transfer (2019+)
35. spatial geometric augmentation domain generalization segmentation deformation crop layout robustness (2020+)
36. cross-domain few-shot medical image segmentation fine-tuning strong baseline (2023+)
37. Active Learning for Convolutional Neural Networks: A Core-Set Approach
38. Domain Generalization with MixStyle
39. half-cut solar cell electroluminescence layout generalization segmentation (2019+)

Snowballing with `get_citations`:
- GIN+IPA (doi:10.1109/tmi.2022.3224067): 30 citing papers.
- DR-Adapter (doi:10.1109/cvpr52733.2024.02269): 25 citing papers.
- RIPU (doi:10.1109/cvpr52688.2022.00790): 25 citing papers.

`search_snippets`: 1 attempt, rate-limited.
`get_paper` (full abstracts): about 40 papers.

Full text read with `read_paper`, specific sections only:
- ABCDFSS (2402.17614)
- The Devil is in Low-Level Features (2503.21150)
- RIPU (2111.12940)
- Best Practices in AL for Segmentation (2302.04075)
- SpotTUnet (2107.04914)
- Position, Padding and Predictions (2101.12322)

Full text not available:
- Shim 2025 (doi:10.1111/mice.13517): no open copy.
- Realistic Evaluation of AL, IJCV 2025: no open copy.
- D2ADA: timed out.

## Counts
- Hits: 39 queries plus 3 citation lists returned about 1,700 merged hits. I looked at the top 10 to 25 of each, about 650 titles, many of them repeats.
- Kept after dedupe and a relevance screen: **93 papers** in `papers.tsv`.
- **84 are NEW** and 9 are already in MASTER: P012 GIN+IPA, P035 SelectSeg, P069 Rein, P110 BigAug, P123 WiSE-FT, P166 surgical fine-tuning, P262 EL instance benchmark, P427 RIPU, P512 DGInStyle.
- How the MASTER check was done: every row was matched by DOI, arXiv id and normalised title with a script.
- Fit score distribution: 5: 0, 4: 9, 3: 11, 2: 36, 1: 29, 0: 8.
- Not every row was read equally. Many low-fit rows rest on an abstract preview or the title only, and the `what_it_is` field says so.

## Reading of the family for our failure modes (my judgement)
- **Recall on unseen modules and new manufacturers.** The DGSS literature from 2022 to 2026 now mostly relies on natural-image foundation models (Rein, FADA, CLOUDS, tqdm, FisherTune). The A8 DINOv3 KILL and patch-14 resolution make these a poor fit for 1 to 2 px cracks. The cheap, label-safe, CNN-level tools are what remain:
  - feature-statistics perturbation: DSU, MixStyle, DR-Adapter's local/global perturbation;
  - normalisation: IBN-Net;
  - intensity randomisation: GIN+IPA, which was planned and never run.
  Several independent papers say shallow layers carry the source-specific signal (Devil-in-low-level, C2SDG, SpotTUnet), which agrees with our PF result.
- **Half-cut layout.** No paper studies a pure layout shift for segmentation, and the search for EL half-cut work found nothing. The closest evidence is:
  - CNNs encode absolute position through zero padding, and thin objects near borders are hurt most (Islam et al.);
  - CNNs rarely use shape unless forced to (Zhang & Mazurowski).
  Both give cheap diagnostics before spending GPU time. The only route found that produces labelled data for a layout with no labels is generative inpainting on unlabelled target images (Shim 2025: +25.8 / +17.8 % F1).
- **Labelling a new layout cheaply.** This sub-family has the strongest direct evidence:
  - Region-level active DA (RIPU) nearly matches full supervision with 2.2 % of regions.
  - Density-aware selection (D2ADA): under 5 % of target labels gives about full-supervision level.
  - Best-practice studies show that on redundant data, such as many cells of one module, uncertainty sampling picks near-duplicates and a diversity batch (Coreset) wins. This is a plausible explanation for our "half the cells gave about the same gain" result.
- **Thin-line precision and rare inactive.** Few papers in this family measure thin classes. RIPU's own table shows the thin class 'pole' lags even at 2.2 % to 5 % of regions. Every AL or DA rule taken from driving data needs a crack-weighted variant.

## Top 10
Order: my estimate of value for the next phase (new-layout recall and labelling cost), adjusted for cost.

1. **doi:10.1111/mice.13517**: Shim 2025, inpainting cracks with a fine-tuned diffusion model (NEW, abstract only).
   - Evidence: fine-tuning Stable Diffusion with DreamBooth on the new site and inpainting cracks gave average F1 gains of 25.82 % and 17.83 % on two target domains over eight models, confirmed in a tunnel field test (concrete).
   - Fit: it is the only route found that creates labelled crack data for a layout with no labels. Inpaint cracks into the 1,152 unlabelled pool half-cells (cut edge, scuff streaks), which aims straight at recall on half-cut cells.
   - Risks: our earlier copy-paste and synthetic half-cut arms were n.d. Realism of the EL crack appearance and label width are the risks. Check with a held-out real half-cut set; E1 cannot be used.

2. **doi:10.1109/tmi.2022.3224067**: GIN+IPA (P012, RUN_NOW, **never run**). D30 read the full text; abstract read here.
   - What it does: random shallow-network intensity remapping (GIN) plus spatially mixed views (IPA) to break shortcuts from context to label. Built for grey-scale CT/MRI single-source DG.
   - Fit: the cheapest zero-shot arm against contrast change from a new manufacturer and against the scuff-streak confounder on half-cut cells.
   - Note: it is config-level and still missing from the ledger of runs.

3. **doi:10.1109/cvpr46437.2021.01087**: semi-supervised DA with dual-level domain mixing (NEW, abstract only).
   - What it does: the source labels, a few labelled target images and many unlabelled target images are combined by region-level and sample-level mixing into two teachers, then distilled into one student.
   - Fit: this is the few-shot track's exact data shape (532 pool cells, a few labelled new-layout cells, 1,152 unlabelled half-cells). Region mixing pastes labelled half-cut regions into full cells, which "append E1 cells to the list" did not do.
   - Risk: teacher pseudo-labels on cracks were weak in our SSL work.

4. **doi:10.1109/cvpr52688.2022.00790**: RIPU, region impurity × uncertainty active DA (P427, PARKED; full text read).
   - Evidence: GTA→Cityscapes with 2.2 % of regions labelled gives 69.6 mIoU, against 70.2 fully supervised. With 5 % it gives 71.2 against 71.9. The thin class 'pole' lags (43.8 vs 47.6).
   - Fit: label regions of new-layout cells instead of whole cells. Change the impurity term to weight crack and inactive, otherwise busbar and gridline boundaries will dominate the selection.

5. **doi:10.1007/978-3-031-54605-1_28**: Best Practices in AL for Segmentation (NEW, full text read).
   - Findings:
     - On redundant pools, single-sample uncertainty selection collapses onto near-duplicates, and batch diversity (Coreset) wins.
     - Coreset+SSL is best on redundant data and sometimes beats 100 % labels with under 30 % labelled.
     - At very low budgets AL is volatile and Random+SSL can win.
   - Fit: cells of one new module are highly redundant, which may explain "half the cells gave the same gain". For the next layout: Coreset selection on C2 features (arxiv:1708.00489), always compared with random at equal budget.

6. **doi:10.1007/978-3-031-19818-2_26**: D2ADA, density-aware active DA (NEW, abstract only).
   - Evidence: queries target samples that are dense in the target but rare in the source. Under 5 % target labels reaches full-supervision level on GTA/SYNTHIA→Cityscapes.
   - Fit: ranks new-layout cells by how unlike the pool they are (e.g. half-cut with scuffs), using C2 features, with no labels needed.

7. **doi:10.1007/978-3-030-87199-4_20**: SpotTUnet / which U-Net layers to fine-tune (NEW, full text read).
   - Evidence: supervised DA with 8 to 800 labelled target slices (brain MRI). The learned per-layer fine-tune policy matches the best fixed scheme at every budget. Regularisation helps significantly under scarcity. Encoder blocks are chosen most often. Histogram matching (0.29 sDice) was worse than no adaptation (0.55).
   - Fit: a direct protocol for fine-tuning C2 on 10 to 40 new-layout cells: full vs encoder-only vs decoder-only vs learned policy. The policy map also shows where the layout shift lives.

8. **doi:10.1109/cvpr52734.2025.00435**: The Devil is in Low-Level Features (NEW, full text read).
   - Evidence: in CD-FSS, target accuracy peaks at early epochs because shallow layers absorb source-specific information. Fixing ResNet stages 1 and 2 beats training all stages (57.21 vs 56.64 average mIoU). Phase-preserving random-conv perturbation of low-level features (LEM) plus test-time low-level calibration gives +3.71 / +5.34 mIoU at 1 and 5 shots.
   - Fit: independent support for PF. Concrete arm: keep the HRNet stem and stage 1 frozen for the whole run, and add Fourier-phase-preserving RandConv on stem features. The phase is kept so 1 to 2 px edges survive, which plain RandConv blurs.

9. **doi:10.1109/cvpr52688.2022.00780**: WiSE-FT (P123, RUN_AFTER_GATE; abstract).
   - Evidence: interpolating original and fine-tuned weights gave +4 to 6 pp under distribution shift and +1.6 pp in-distribution on ImageNet, and +2 to 23 pp on six other shifts.
   - Fit: for few-shot models, interpolate pool-only C2 with the pool+new-layout fine-tune. This should keep the new-layout gain without losing CV5 or drifting to the 1.5× wider E1 label width that the few-shot models learned.
   - Cost: config-only, no training.

10. **doi:10.1007/s11263-024-02069-9**: Position, Padding and Predictions (NEW, full text read; ICLR version arxiv:2001.08248).
    - Evidence: zero padding makes CNNs encode absolute position. Boundary effects are strongest near borders but also present at the centre. On Cityscapes, thin objects near the border suffer most.
    - Fit: half-cut cells put cut edges, busbar ends and frames at positions the pool never shows. A cheap diagnostic: score C2 on pool cells cropped or shifted into half-cut geometry. Then a cheap arm: random translation/crop training so absolute position cannot be used.
    - This separates the layout part of the error from the scuff part, which D30 listed as a missing diagnostic.

Runners-up, each at fit 3:
- **doi:10.1109/cvpr52733.2024.02228** ABCDFSS (full text read): frozen backbone plus tiny per-stage adapters trained on the few labelled target images with view-consistency. 1-shot CD-FSS average 60.7 vs 56.1 for PATNet. Code: Vision-Kek/ABCDFSS.
- **arxiv:2202.03958** DSU and **arxiv:2104.02008** MixStyle: parameter-free feature-statistics perturbation.
- **doi:10.1007/978-3-030-01225-0_29** IBN-Net: instance normalisation in shallow blocks.
- **doi:10.1016/j.patcog.2023.110018** CNNs rarely learn shape: limited augmentations force shape use, which helps out of distribution.
- **doi:10.1007/978-3-031-43895-0_3** COLosSAL: cold-start AL.
- **doi:10.1016/j.autcon.2024.105828** partial-annotation AL in civil-engineering damage segmentation.

## Fit to grey-scale EL cells of a new manufacturer or layout, by sub-family (summary)
| Sub-family | Shown on | Size of gain (from papers) | Fit to EL new layout |
|---|---|---|---|
| Normalisation / whitening (IBN, RobustNet, SAN-SAW) | GTA/SYNTHIA → Cityscapes etc. | IBN "comparable to DA methods"; others not in abstract | medium for contrast shift, none for layout |
| Style hallucination / feature statistics (SHADE, DSU, MixStyle, DR-Adapter perturbation) | synthetic→real, classification, CD-FSS | SHADE +5.05 / +8.35 mIoU | medium, label-safe, config-level |
| VFM-based DGSS (Rein, FADA, FisherTune, CLOUDS, tqdm) | synthetic→real driving | CLOUDS +5.6 / +6.7 mIoU | low: patch resolution; A8 KILL |
| Diffusion style/content augmentation (DGInStyle, CLOUDS, Shim 2025) | driving; concrete cracks | Shim +25.8 / +17.8 % F1 | high only for crack inpainting into target layout |
| Medical SDG (GIN+IPA, C2SDG, BigAug, RandConv) | CT/MRI/fundus across sites | see D30 (GIN+IPA) | high: grey-scale native, confounder-breaking |
| Layout / position / shape | CIFAR grids, Cityscapes | diagnostic | high as a cheap diagnostic |
| TTT / TTA / source-free | classification, medical organs | SicTTA +8.2 Dice (organs) | low (D31: ranking failure, not calibration; source data available) |
| CD-FSS (PATNet, APSeg, DR-Adapter, frequency masker, ABCDFSS, ISA) | Deepglobe, ISIC, X-ray, FSS-1000 | ABCDFSS +4.6 mIoU avg 1-shot | low to medium: episodic novel-class setting; adapter ideas transfer |
| Few-shot fine-tuning (SpotTUnet, surgical FT, WiSE-FT) | MRI sites; ImageNet shifts | WiSE-FT +4 to 6 pp | high: directly the few-shot track |
| Active learning / active DA (RIPU, D2ADA, Mittal, COLosSAL) | GTA→CS, A2D2, MSD | RIPU 2.2 % regions ≈ full | high for labelling-cost planning |

## NOT_FOUND
- **Any segmentation paper on EL half-cut, shingled or multi-busbar layout shift.** Searched with queries 13, 33 and 39 plus the PV/EL terms in 11 and 35. Only reviews and datasets came back.
- **A paper that isolates pure geometric/layout shift with fixed appearance in segmentation.** Searched with queries 11, 26 and 35. Nothing direct; the position/padding and shape-bias papers are the closest.
- **Active learning or cold-start selection for PV/EL defect segmentation.** Searched with queries 29 and 33. Nothing found.
- **Thin-structure evidence for active DA.** Snippet search was rate-limited, so only RIPU's per-class table (pole) was checked.
- **Abstract of tqdm (doi:10.1007/978-3-031-72998-0_3).** The index returned no abstract and the full text was not fetched. It is kept at fit 0 on title only.
- **Full text of D2ADA, the IJCV AL study and Shim 2025.** Timed out or no open copy; their rows rest on the abstracts.
- **Original RandConv (Xu et al., ICLR 2021) and SAR/CoTTA/TENT.** Not searched again; MASTER already holds RandConv (P369 note), CoTTA (P573), TENT (P619) and SAR (P594).
