# D40 notes (WIP)
Queries run:
1. surface defect segmentation mixed supervision KolektorSDD2 (2020+)
2. few-shot defect segmentation industrial surface (2020+)
3. steel surface defect segmentation transformer (2022+)

Candidates:
- doi:10.1016/j.compind.2021.103459 Bozic 2021 mixed supervision (arXiv 2104.06064) image+pixel labels, KSDD2
- arxiv:2408.10031 Dynamic Label Injection imbalanced industrial defect seg (2025 LNCS)
- arxiv:2510.13226 Sample-centric multitask det+seg industrial defects
- doi:10.3390/app13020826 Balanced loss surface defect seg
- arxiv:2506.22866 Region-aware CAM weakly sup defect seg
- doi:10.1016/j.measurement.2023.112614 Defect transformer (arXiv 2207.08319)
- arxiv:2609.21424 P3-SAM few-shot steel (2026)
- doi:10.3390/s24186016 LDM synthetic steel defects
4. tiny defect segmentation industrial small defects (2022+)
5. supervised anomaly detection limited anomalous samples segmentation (2022+)
6. SuperSimpleNet unifying unsup and sup (2023+)
7. prototypical residual network anomaly seen anomalies (2022+)
More candidates:
- doi:10.1007/978-3-031-78192-6_4 SuperSimpleNet ICPR 2024 (arXiv 2408.03143)
- doi:10.1007/s10845-025-02680-8 No label left behind (SSN2, arXiv 2508.19060) all supervision regimes
- doi:10.1109/cvpr52729.2023.01562 PRN CVPR23 (arXiv 2212.02031)
- doi:10.1109/cvpr52733.2024.01668 AHL OSAD CVPR24 (2310.12790)
- doi:10.1109/cvpr52688.2022.00724 DRA CVPR22 (2203.14506)
- doi:10.1016/j.jmsy.2025.11.022 survey real-world industrial defect detection (2507.13378) benchmark relevance
- doi:10.1109/tim.2023.3293561 NRSD rail seg (2306.15442)
- doi:10.1007/s10845-025-02778-z ISP-AD dataset synthetic+real defects (2503.04997)
8. Segment Anything fine-tuning industrial defect (2024+) [openalex timed out]
9. defect segmentation noisy annotations (failed, rate limit)
10. WebSearch KSDD2 SOTA; WebSearch noisy annotations thin scratch
11. PCB defect segmentation small targets (2022+) -> mostly YOLO, reject
12. magnetic tile defect segmentation (2021+) -> arch tweaks
13. surface defect segmentation (2025+, min cites 3)
14. industrial AD benchmark realistic evaluation (2024+)
More:
- SSN2 read: truncated L1 seg loss th=0.5 + focal; latent Perlin-noise feature anomalies on top of real labels; cls head; KSDD2 sup APdet 97.8 / APloc 81.3 (DSR 85.5 loc); weak (no pixel) APloc 47.6. code github.com/blaz-r/SuperSimpleNet
- arxiv:2604.11162 Boxes2Pixels (CVPR26 per web): SAM pseudo-masks from boxes, one-sided self-correction relaxes bg loss when student confident; recall +18.56; code github.com/CLendering/Boxes2Pixels
- arxiv:2510.13226 sample-centric MTL: image cls + seg boosts recall slender/low contrast; Seg_mIoU/Seg_Recall metrics
- arxiv:2607.21456 SPDCN strip deformable conv steel cracks/scratches (2026)
- doi:10.1109/cvpr52733.2024.01681 Supervised AD complex industrial images (SegAD, VAD dataset) 2405.04953
- arxiv:2603.13507 MIRAGE realistic anomaly generation
- arxiv:2309.12639 CINFormer
15. get_citations Bozic 2021; similar_papers(SSN2, sample-centric, SPDCN)
- Bozic 2021 read (fetch 1/3): end-to-end seg+cls; gamma disables seg loss only for positive images without pixel labels, negatives still train seg; dynamic balance lambda=n/nep seg->cls; stop-grad cls->seg; distance-transform weight on positive pixels Omega=w_pos*(D/Dmax)^p, p=1 or 2; KSDD2 AP 95.4 full; ablations on DAGM/KSDD/Severstal all components help.
- doi:10.1109/tii.2023.3348835 combined anomaly-aware weakly sup lightweight (2024)
- doi:10.1016/j.patrec.2024.05.017 one-shot defect seg w fake defects
16-24: domain generalization defect seg (2610.19540 covered by D30); Severstal winning (nothing); scratch strip conv (2023+); weakly sup defect seg image labels (2023+); normal reference residual; MVTec AD2 (covered D07); fabric (reject); 
Overlaps: SSN in D07/D21/D36; Bozic in D27/D36; Boxes2Pixels D15/D36; GFDS/SOFS D38; PRN/SegAD/NDP-Net D39; MVTec AD2 D07; IDA2026 D30.
New: Balanced loss (app13020826): dynamic class weights + truncated CE + label confusion suppression at boundary; +5-30%.
Conformal seg (2504.17721) CRC thresholds Mask R-CNN.
CADNet siamese change (2409.00589) code github.com/HATFormer/CADNet.
LAVSS Mamba small defects TII25 (no code seen).
DLI code github.com/covisionlab/dynamic-label-injection (web) ECCVW24.
25-30: mixed sup 2025; few-shot VFM 2025; boundary ambiguity loss (found rough-set noisy labels 2301.10441, SAM Era); rail NRSD 2024+; web: sample-centric code (none), SPDCN (profile only), balanced loss details (KSDD2, Severstal, aluminium), rough set.
Read sample-centric (fetch 2/3): CaP cls head on encoder, grads into encoder only; KSDD2 DLv3+ mIoU 53.24->58.21, Seg_Recall 72.7->82.7; SegNet 55.05->61.85; DLv3 Seg_Recall dropped 71.7->65.5. Crack road dataset small/mixed.
Read 2211.05295 (already downloaded): PV mono THC448 1:2000; DIBE focal with FP/FN regulators alpha 0.3 beta 0.7; U-Net Dice 0.641 vs DIBEReg 0.652 (single run).
Writing final file next.
