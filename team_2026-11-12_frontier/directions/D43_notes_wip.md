# D43 notes (wip)
Q1 nnU-Net revisited -> doi:10.1007/978-3-031-72114-4_47 (arXiv 2404.09556)
Q2 metrics reloaded -> doi:10.1038/s41592-023-02151-z (2206.01653); pitfalls doi:10.1038/s41592-023-02150-0 (2302.01790); labelling instructions doi:10.1038/s42256-023-00625-5; Hirling seg metric misinterpretations doi:10.1038/s41592-023-01942-8; Podobnik HD pitfalls arxiv:2410.02630
Q3 (13 Nov resume) nnU-Net revisited again; Huang U-net scaling benchmark doi:10.1038/s41598-025-15617-1
Q4 leakage: Sasse leakage scenarios doi:10.1186/s40537-025-01193-8; Rosenblatt doi:10.1038/s41467-024-46150-w; bearing realistic eval doi:10.1016/j.ymssp.2026.114640 (2509.22267); leakage-safe vibration doi:10.36001/phme.2026.v9i1.4924; digital pathology tiles doi:10.1007/978-3-030-68763-2_13; TabArena living benchmark doi:10.52202/085713-0519
Q5 Kapoor leakage doi:10.1016/j.patter.2023.100804; REFORMS doi:10.1126/sciadv.adk3452
Q6 WILDS arxiv:2012.07421; WILDS unlabeled ext arxiv:2112.05090
Q7 EL bench: Hijjawi instance seg benchmark doi:10.1016/j.solener.2025.114083; Bayat controlled backbone EL classification doi:10.3390/s26123775; Sahin bench doi:10.3390/s26134256; MultiSolSegment doi:10.1016/j.solener.2026.114469; Otamendi scalable annotation doi:10.1109/tii.2022.3228680; Jha semi-sup EL doi:10.1016/j.engappai.2025.111790; Fioresi doi:10.1109/jphotov.2021.3131059; Chen crack feature JPV doi:10.1109/jphotov.2023.3249970
Q8 crack: OmniCrack30k doi:10.1109/cvprw63382.2024.00392; CrackSeg9k doi:10.1007/978-3-031-25082-8_12; Segment Any Crack doi:10.1061/jccee5.cpeng-7090 (2504.14138); Inspect Any Crack arxiv:2610.14274 (severity); dacl10k doi:10.1109/wacv57701.2024.00843
Q9 MSD search timed out (retry later)
Q10 anomaly bench: MVTec AD 2 doi:10.1007/s11263-026-02743-0 (2503.21622) sealed test; COCO-AD doi:10.1007/s11263-026-02809-z
Q11 CIs: El Jurdi CI brain MRI doi:10.1016/j.media.2025.103565 (2307.10926); El Jurdi precision ISBI doi:10.1109/isbi53787.2023.10230401; Christodoulou CIs uncovered doi:10.1007/978-3-031-72117-5_12; Andre large-scale CI doi:10.1016/j.media.2026.104349 (2601.17103)
Q12 challengeR Wiesenfarth doi:10.1038/s41598-021-82017-6
Q13 multi-annotator: QUBIQ arxiv:2405.18435; Lemay label fusion doi:10.59275/j.melba.2022-db5c; Yang IAA doi:10.1109/access.2023.3249759; De Sutter interobserver limits doi:10.1186/s40658-025-00767-y
Q14 tolerance metrics: Pang decomposing metrics arxiv:2607.00886; Henry road topological label noise doi:10.1109/icpr48806.2021.9412054
Q15 MSD doi:10.1038/s41467-022-30695-9 (2106.05735)
Q16 fair baselines: CT reproducibility doi:10.3390/jimaging11100344; controlled SSM remote sensing arxiv:2604.18721
Q17 label errors: Northcutt test errors arxiv:2103.14749; confident learning doi:10.1613/jair.1.12125; benchmark lottery arxiv:2107.07002
Q18 datasheets doi:10.1145/3458723
Q19 surface defect: KolektorSDD2 mixed supervision doi:10.1016/j.compind.2021.103459; Real-IAD doi:10.1109/cvpr52733.2024.02159
Q20 near-dup leakage: Truong near-dup embeddings arxiv:2312.07273; Pothole video-disjoint resplit doi:10.21203/rs.3.rs-11338135/v1; PlantSeg contamination doi:10.21203/rs.3.rs-11109696/v1; MRI near-dup MedNeXt doi:10.3389/fmed.2026.1955863; FeTS doi:10.1038/s41467-025-60466-1; RVL-CDIP overlap doi:10.1145/3820755.3821486
Q21 2025+: Konrad small organ benchmarking limited data doi:10.1016/j.bspc.2026.111226 (2509.05892); spatial transcriptomics seg bench doi:10.1038/s41592-026-03272-x; cell seg benchmark doi:10.3390/jimaging12070297
Q22 nnU-Net revisited citations: nnWNet CVPR25 doi:10.1109/cvpr52734.2025.01942 (unified eval benchmark call)
Read nnU-Net revisited sec 2: P1 confounders (ensembles, extra data, pretraining, compute), P2 standardized baseline (nnU-Net), P3 dataset suitability (statistical vs systematic variance: BTCV high variance, BraTS low), P4 R4 5-fold CV rotating val + separate test pool.
Hijjawi EL instance seg on UCF-EL (leaky split, BRIEF), MMDetection, ConvNeXt-V2 mAP50 0.602 mIoU 0.650; Bayat 20k EL cls stratified 5-fold, image-level, "motivates module-level grouped validation"
Q23 EL bench attempts: Hanifi 29-class EL seg doi:10.1007/978-981-96-8892-0_4 (VGG16-UNet, defect mIoU 0.326, code github.com/sntubix/pv-defect-segmentation); STC-Net arxiv:2608.01714 (PVEL-S, train mIoU 95.98 vs test 72.52, inactive-area proxy for power loss); Hanifi diffusion anomaly gen arxiv:2511.09604
Q24 crack annot variability: Pradhan tolerance crack width post-proc doi:10.3390/s26185853; Conformal segmentation industrial defects doi:10.3390/math13152430 (2504.17721)
Q25 test reuse: Roelofs meta-analysis openalex:W2991486856; Rip van Winkle arxiv:2102.13189; benchmark lottery arxiv:2107.07002
IDEA: nnU-Net style 5-fold CV ensemble over 532 train+val cells (fold roots exist) = score-raising arm
Web: MVTec AD 2 private test via server, 2 subs / 30 days (voxel51, verify), SegF1 metric; MedSegBench (Sci Data 2024) 35 datasets, 128/256/512 standard splits; OmniCrack30k nnU-Net clIoU@4px 64%, beats others by >=10 pts, splits 22158/13277/4582; repo github.com/ben-z-original/omnicrack30k (unverified, 3rd party catalog); MetricsReloaded github.com/Project-MONAI/MetricsReloaded (maybe unmaintained); challengeR github.com/wiesenfa/challengeR
El Jurdi read: parametric CI ~ bootstrap; 1% wide CI needs 100-200 test cases when SD ~3%; harder tasks SD 12-13% need >1000; code github.com/rosanajurdi/SegVal. Andre 2026 large-scale CIs: 24 tasks, macro needs more obs than micro, decision tree.
Q26 spatial CV: Wadoux doi:10.1016/j.ecolmodel.2021.109692 (critique: spatial CV not right for map accuracy, use probability sampling); de Bruin clustered doi:10.1016/j.ecoinf.2022.101665; CAST arxiv:2404.06978
Q27 relabel test: Beyer ImageNet ReaL arxiv:2006.07159
Q28 2025 crack bench: CrackSegFlow 50k benchmark doi:10.1016/j.autcon.2026.106938 (2601.03637); FMS2 arxiv:2603.13659; cross-val YOLO ceramic crack doi:10.18196/jrc.v7i2.29037; metal defect cross-dataset doi:10.3390/app16063022
Q29 AD eval flaws: nothing new beyond MVTec AD2 / COCO-AD
Verified: nnU-Net orig doi:10.1038/s41592-020-01008-z; Reinke pitfalls doi:10.1038/s41592-023-02150-0; WILDS code wilds.stanford.edu; Konrad 2026: 10 models, bootstrap CIs overlap, rankings change ID vs OOD; Lemay MELBA: SoftSeg + random rater sampling, ivadomed code; KolektorSDD2 code github.com/vicoslab/mixed-segdec-net-comind2021 (web); nnU-Net github.com/MIC-DKFZ/nnUNet (web)
NEXT: write D43_benchmark_design.md (18 papers selected), then StructuredOutput
