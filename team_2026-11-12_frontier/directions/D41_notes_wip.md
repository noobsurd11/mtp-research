# D41 notes (wip)
q1 Metrics Reloaded -> doi:10.1038/s41592-023-02151-z (MR), doi:10.1038/s41592-023-02150-0 (pitfalls), arxiv:2410.02630 (distance metric impl pitfalls), arxiv:2509.05670 MeshMetrics
q2 thin structure eval tolerance -> arxiv:2607.00886 (decomposing seg metrics 2026)
q3 stat significance small test -> arxiv:2411.03670 Touchstone, arxiv:2110.01052 LTT
q4 boundary IoU -> arxiv:2103.16562 BoundaryIoU, arxiv:2603.00163 whiteboard stroke boundary protocol 2026
q5 CI seg -> doi:10.1016/j.media.2025.103565 ElJurdi CI brain MRI; arxiv:2210.14677 ISBI precision; arxiv:2601.17103 Andre CI large-scale 2027 MedIA; arxiv:2410.03406 conformal sets
q6 variance -> arxiv:2103.03098 Bouthillier
--- resume 13 Nov ---
q7 CI seg small test (2020) -> doi:10.1007/978-3-032-05663-4_2 Andre CI coverage traps 2025; Takahashi F1 CI doi:10.1007/s10489-021-02635-5
q8 tolerance thin curvilinear metric -> nothing new (VEELA arxiv:2605.22357 clinically constrained benchmark)
q9 NSD tolerance -> Centerline boundary dice loss doi:10.1007/978-3-031-72111-3_5 (loss); tolerance dice loss doi:10.1007/s11760-023-02790-x; Panella crack seg data challenges doi:10.1016/j.autcon.2021.104110
q10 variance seeds -> Bouthillier; Ash 2025 practically significant comparison doi:10.1021/acs.jcim.5c01609 (repeated CV + Tukey HSD); Madaan arxiv:2406.10229
q11 CV CI -> Bates/Hastie/Tibshirani doi:10.1080/01621459.2023.2197686 (nested CV CI); Bradshaw CV guide doi:10.1148/ryai.220232; Schulz-Kumpel arxiv:2409.18836 CI generalization error benchmark; Cai bootstrap CV doi:10.1214/25-aoas2036
q12 inter-rater eval -> Yang IAA seg doi:10.1109/access.2023.3249759
q13 crack eval tolerance -> Rill-Garcia Syncrack doi:10.1016/j.neucom.2022.01.051 (inaccurate annotations, eval); SEMIR arxiv:2606.24935; conformal seg industrial doi:10.3390/math13152430
q14 label errors test -> Northcutt arxiv:2103.14749; Benchmark lottery arxiv:2107.07002
q15 fine-grained IoU -> arxiv:2310.19252 Wang/Berman per-image & worst-case mIoU (code?)
q16 Betti matching -> arxiv:2211.15272; clDice doi:10.1109/cvpr46437.2021.01629
q17 2025 label-uncertainty eval -> TwinTrack arxiv:2604.15950; Penquitt arxiv:2609.21822 detection benchmarks incomplete; underwater multi-annotator arxiv:2608.15363; Nogueira label noise ranking doi:10.1016/j.neucom.2026.134891
q18 paired stat test seg 2024 -> nothing
got: ElJurdi ISBI ~8 Dice pts CI for n=20; Pang decomposing metrics code github lartpang/PySODMetrics; Podobnik HD impl pitfalls; Andre CI MedIA (macro needs more obs than micro)
q19 challengeR -> Wiesenfarth doi:10.1038/s41598-021-82017-6
q20 hierarchical bootstrap -> Saravanan arxiv:2007.07797 / doi:10.1101/819334
q21 val overfitting/model selection -> Gorriz kfold doi:10.1016/j.inffus.2026.104404; DOME doi:10.1038/s41592-021-01205-4
web1 thin metric 2025 -> arxiv:2311.13319 (NSD 1px tolerance +25%); SAM3-LoRA arxiv:2609.00469 (crack IoU low recall high); whiteboard arxiv:2603.00163; FMS2 arxiv:2603.13659 (betti on crack)
web2 MetricsReloaded code github.com/Project-MONAI/MetricsReloaded (verified via search; unmaintained since 2023 per fork note)
q22 noisy GT eval -> nothing direct (training noise papers only)
q23 boundary IoU -> arxiv:2103.16562 CVPR21; wIoU doi:10.1016/j.patrec.2024.07.011
q24 corrected t-test -> Bouckaert & Frank 2004; Raschka arxiv:1811.12808; Vanwinckelen repeated CV
q25 crack ODS/OIS -> CrackCue arxiv:2507.16851
q26 seeds power -> Colas arxiv:1806.08295; Picard seed arxiv:2109.08203
q27 NSD origin -> Nikolov doi:10.2196/26151 (arXiv 1809.04430), code google-deepmind/surface-distance (verify)
q28 soft reference eval -> nothing usable
q29 leakage -> Kapoor doi:10.1016/j.patter.2023.100804; REFORMS doi:10.1126/sciadv.adk3452
Wang fine-grained IoU code github.com/zifuwanggg/JDTLosses (from abstract)
snippets: S2 rate-limited x4
snowball similar(ElJurdi MedIA, Bouthillier) -> **arxiv:2606.12552 Eve/Varoquaux/Moreau 2026 CV sample gain** (fetched: MCCV K=20 gives test-sample gain 5-15x; repeated kfold comparable; early-stop CV via redundancy score; Benchopt); Christodoulou arxiv:2409.17763 (MICCAI23 median CI width 0.03 = 3x gap 1st-2nd)
q30 panoptica arxiv:2312.02608; q31 ranking 2025 -> Urooj polyp audit arxiv:2607.08203; q32 road completeness -> nothing
web3-5 verified repos: bowenc0221/boundary-iou-api, google-deepmind/surface-distance, wiesenfa/challengeR; MeshMetrics gasperpodobnik/MeshMetrics (from abstract)
Syncrack Rill-Garcia details got. Writing final file now.
done: final file written
