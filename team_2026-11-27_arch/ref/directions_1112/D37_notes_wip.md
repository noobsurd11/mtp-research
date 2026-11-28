# D37 Data-centric methods (work in progress)

Queries so far (search_papers, year_from 2020):
1. label error detection semantic segmentation
2. confident learning segmentation noisy labels
3. automatic label refinement noisy boundary annotations segmentation
4. thin structure segmentation inaccurate annotations misaligned labels vessel crack (3 hits, too long)
5. misaligned annotations curvilinear structure segmentation
6. noisy crack annotations segmentation label correction

Candidates noted: arxiv:2207.06104 (Rottmann label errors), arxiv:2307.05080 (Lad, label quality any model),
doi:10.1016/j.neucom.2022.01.051 (Rill-Garcia, Syncrack inaccurate annotations), arxiv:2410.09409,
arxiv:2106.01860 (MTCL), arxiv:2406.10891 (noisy annotations), doi:10.1016/j.ress.2025.110909 (SelectSeg)
7. active learning semantic segmentation small budget
8. data valuation pruning semantic segmentation training set (weak)
9. learning to segment from misaligned and partial labels (year_from 2019)
10. SAM label refinement pseudo label correction thin defects (2023+)
11. adaptive early-learning correction segmentation noisy annotations
12. noisy boundary label alignment edge detection active alignment (2019+)
13. label errors segmentation datasets detection (2025+)
14. crack segmentation noisy labels (2025+)
15. annotator style multi-source annotation convention segmentation (weak)
16. spatially varying label smoothing segmentation uncertainty annotation
17. training dynamics identify mislabeled pixels segmentation memorization
18. training set search target domain data selection segmentation domain shift (weak)
19. automatic annotation industrial defect segmentation foundation model pseudo labels (2025+)
Snowball: citations of Rill-Garcia 2022 and Rottmann 2023; similar_papers on Crispness+STEAL+Rill-Garcia (all 2026, off-topic).
Code verified (web): ADELE github.com/Kangningthu/ADELE; STEAL github.com/nv-tlabs/STEAL (inference only per README); cleanlab.segmentation.filter.find_label_issues in cleanlab docs.
More candidates: arxiv:2306.15172 Crispness (Canny-guided label refinement), arxiv:1904.07934 STEAL, arxiv:2110.03740 ADELE,
arxiv:2308.02498 spatial correction, arxiv:2508.17930 learning to detect label errors by making them, arxiv:2604.12832 refurbish GT errors.

## Resume session 13 Nov (earlier results lost; re-running key queries)
R1 label error detection semantic segmentation (2020+): confirms doi:10.1109/wacv56688.2023.00323 Rottmann.
get_paper: arxiv:2508.17930 (Penquitt 2025, learn-to-detect label errors by injecting them; 459 Cityscapes errors released),
doi:10.1109/isbi61048.2026.11515763 (=arxiv:2604.12832, VOG detection + pseudo-label refurbish, echo),
arxiv:2307.05080 (Lad, soft-min likelihood label quality score, cleanlab).
R2 active learning semantic segmentation small budget: doi:10.52202/085713-0757 (arXiv 2510.22229, diffusion two-stage low-budget AL, NeurIPS 2025),
doi:10.1007/978-3-031-54605-1_28 (Mittal best practices AL seg), doi:10.1007/s11263-025-02372-z (Mittal IJCV realistic eval).
R3 data pruning semantic segmentation (2022+): mostly model pruning, weak; arxiv:2303.04947 InfoBatch (dynamic data pruning).

## Resume session 2 (13 Nov evening). Sibling D15/D16 already cover label refinement, ADELE, Spatial Correction, Rottmann, SelectSeg, SAMRefiner.
D37 focus now: dataset auditing (label errors in train AND test), data valuation / pruning / curriculum, pool selection for E1, tiny-budget AL, auto-annotation of the pool, leakage / near-duplicate auditing for the benchmark.
S2 queries (session 2):
Q20 pervasive label errors in test sets benchmark (2020+): arxiv:2103.14749 Northcutt test-set errors; arxiv:2609.21822 Penquitt OD benchmarks incomplete (2026); doi:10.5220/0014281200004084 Penquitt detection-to-correction OD.
Q21 data valuation semantic segmentation (2020+): nothing usable.
Q22 dataset cartography training dynamics segmentation: weak; doi:10.1145/3627157 survey dataset refinement.
Q23 coreset data selection pruning segmentation (2022+): arxiv:2308.01189 Data-Centric Diet multi-center pruning med seg (EL2N/gradient norm with dynamics), arxiv:2503.00828 training-free pruning instance seg, arxiv:2502.07547 instance-dependent early stopping (TPAMI 2026).
Q24 active domain adaptation semantic segmentation region selection (2021+): doi:10.1109/cvpr52688.2022.00790 RIPU (region impurity + uncertainty), LabOR, MADA, D2ADA.
Q25 label errors semantic segmentation detection (2025+): doi:10.1609/aaai.v40i7.37445 A2LC (arXiv 2506.11599); arxiv:2508.17930 again.
Q26 active label correction semantic segmentation (2022+): arxiv:2403.10820 ALC with foundation models (Kim, Kwak); arxiv:2406.10891 noisy annotations COCO-N.
Q27 data leakage near-duplicate train test split (2020+): arxiv:2508.17416 Data Leakage in Visual Datasets (ICCVW 2025); arxiv:2312.07273 near-duplicate detection medical with pretrained embeddings.
Q28 SAM auto annotation industrial defect (2024+): only arxiv:2406.20081 UnSAM; weak.
Q29 pixel-wise label quality estimation segmentation (2021+): arxiv:2603.00604 data-centric benchmark label-noise ranking (Neurocomputing 2026, code github.com/keillernogueira/label_noise_segmentation per abstract).
Q30 active learning crack segmentation (2021+): Pantoja-Rosero partial annotations AL (autcon 2024), Rieger tiny-budget AL microstructures (2024). Weak.
Q31 evaluating segmentation with noisy ground truth (2020+): arxiv:2607.11214 ARLA (adaptive-resolution evaluation on unreliable labels).
Snowball citations of Lad 2307.05080: arxiv:2608.09101 Contrastive Mask Fidelity (VLM judge, reference-free mask audit), arxiv:2506.21430 HyperSORT (MICCAI 2025), doi:10.1016/j.phro.2026.101019 SAM2 annotation error detection/correction, arxiv:2605.06891 label bias fairness seg.
Q32 data selection pool target-domain (2022+): arxiv:2607.22697 TTCov test-conditioned data curation.
Web: A2LC code github.com/ngbrjyj/A2LC (listed in AAAI version, repo not opened).
fetch_fulltext 1/3: HyperSORT (arxiv:2506.21430) read: hypernetwork predicts U-Net weights from a learned per-sample 2-D latent with L1 pull to 0; outliers = label errors / styles; infer with lambda=0. Code github.com/ImFusionGmbH/HyperSORT (stated in paper).
Q33 meta reweight pixels noisy seg: no results (openalex timeout).
Q34 label error detection segmentation (2025+, arxiv+openalex): only repeats + arxiv:2604.12832 VOG.
Q35 rare class mining unlabeled pool: arxiv:2409.15486 VLMine (WACVW 2025), arxiv:2406.02435 generative AL long-tail, AIDE CVPR 2024.
Q36 cold start low budget AL foundation features (2023+): arxiv:2510.22229 two-stage eDALD (NeurIPS 2025, code github.com/jn-kim/two-stage-edald per abstract), arxiv:2401.14555 AL with VFMs, arxiv:2606.20765 dataset-aware cold start 3D med.
Q37 repeat factor sampling rare class (2020+): arxiv:2305.08069 IRFS (instance-aware RFS, detection); FASA. Simple, no seg evidence.
Q38 variance small test CV (2020+): arxiv:2606.12552 CV reduces benchmarking variance (2026); Bouthillier 2103.03098 (already in D41). nnU-Net revisited.
Q39 ST++ selective self-training (2021+): doi:10.1109/cvpr52688.2022.00423 (already D29 notes).
Web: SAM2/SAM3 label cleaning crack -> arxiv:2410.09409 (SAM-Adapter + GMM noisy crack labels, in D15 notes), arxiv:2308.00883 SAM pseudo-label correction (label quality evaluation + uncertainty self-correction).
get_paper: Confident learning doi:10.1613/jair.1.12125 (arxiv:1911.00068).
