# D27 resume notes (13 Nov 2026)
MCP up (OpenAlex only; s2 rate-limited, scopus 401, arxiv timeout).
Q1 multi-label semantic segmentation overlapping classes sigmoid (2020+): nothing new usable.
Q2 boundary aware multi-task segmentation thin structures: doi:10.1155/2023/3301106 two-stream boundary-aware concrete crack; doi:10.1016/j.autcon.2024.105354 (arXiv 2306.09196) steel crack boundary guidance; arxiv:2101.04704 BASNet-mobile.
Q3 classification guided seg FP suppression: doi:10.3390/s26165185 hard-negative background suppression crack (2026).
Q4 region-based training nested labels brain tumor: doi:10.1007/978-3-031-09002-8_2 Optimized U-Net BraTS (arXiv 2110.03352); doi:10.1007/978-3-030-72084-1_45 extra classification network BraTS (arXiv 2009.12111)
Q5 hierarchical semseg 2022+: HSSN doi:10.1109/cvpr52688.2022.00131; Poincare ball hierarchical doi:10.1109/cvpr52733.2024.02666 (arXiv 2404.03778); aorta hierarchical arXiv 2511.14187
Q6 crack multi-task boundary distance: two-stream concrete doi:10.1155/2023/3301106; steel boundary guidance doi:10.1016/j.autcon.2024.105354
Q7 inclusion/exclusion constraints: persistent-homology multiclass topo loss doi:10.1109/tmi.2022.3203309 (arXiv 2107.12689); prior loss survey 2011.08018
Q8 EL multi-task: Hijjawi 2025 instance seg benchmark doi:10.1016/j.solener.2025.114083; SeMaCNN arxiv:2208.05994; MultiSolSegment doi:10.1016/j.solener.2026.114469; SEiPV-Net doi:10.3390/en16237726
snippets: S2 rate-limited
Q9 mixed supervision: Bozic doi:10.1016/j.compind.2021.103459 (420 cites); PSIC-Net doi:10.3390/machines9100221
Q10 panoptic crack: Hijjawi EL instance bench again; SAM instance struct damage doi:10.1016/j.aei.2024.102826
Q11 multi-label medical: MultiTalent doi:10.1007/978-3-031-43898-1_62; COSST partial labels doi:10.1109/tmi.2024.3354673
Cit TopoInteraction: Topologically faithful multi-class seg arXiv 2403.11001 (MICCAI 2024); TopoSeg; TopCoW
Cit Bozic: mostly anomaly surveys
Q12 aux boundary head 2025: CTO doi:10.1016/j.media.2025.103615 (arXiv 2505.04652) READ: Sobel-operator boundary-guided decoder (BEM+BIM), ISIC2016 IoU 84.92->86.60; ablation ISIC2018 BEM +0.54 IoU, BIM +0.41; vs Boundary loss 85.25, Boundary DoU 85.70. Blob tasks only.
Q13 hierarchical 2025: Label tree semantic losses doi:10.3389/frai.2026.1841639 (arXiv 2507.15777) Wasserstein tree loss; HieraRS 2507.08741
Q14 image-level FP 2025: nothing new strong
get_paper Betti matching multi-class doi:10.1007/978-3-031-72111-3_68 (2403.11001)
similar(MultiSolSegment, SBCB): Conditional boundary loss TIP 2023 doi:10.1109/tip.2023.3290519; Chen 2023 JPV crack feature extraction doi:10.1109/jphotov.2023.3249970
Q15 partial label multi-dataset: Bevandic WACV 2022 doi:10.1109/wacv51458.2022.00248 (2108.11224); UniSeg label shifts 2202.14030; mDALU 2012.08385; COSST
Q16 crack centerline width multi-task: nothing strong
Q17 containment constraint: nothing new
Web: nnU-Net region_based_training.md (regions_class_order; later regions overwrite). Bozic code github.com/vicoslab/mixed-segdec-net-comind2021 (CC BY-NC-SA). MultiSolSegment: no code found. CTO code github.com/xiaofang007/CTO. SBCB code github.com/haruishi43/boundary_boost_mmseg (Sensors doi 10.3390/s23156980).
SDF-TopoNet arxiv:2503.14523 SDF aux pretraining for tubular (no numbers read)
READ arxiv:2609.24769 BraTS-METS 2026: Primus region-based vs label-based: ET 0.713 vs 0.710, TC 0.400 vs 0.742 (region-order bug), WT 0.680 vs 0.683, RC 0.566 vs 0.531. Lesion F1 same. Region order must go outer->inner.
final file written 13 Nov; see D27_multitask_structured.md
