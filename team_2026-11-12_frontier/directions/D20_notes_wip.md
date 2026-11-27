D20 WIP notes (scratch, final file is D20_small_object_losses.md)
Queries so far: blob loss instance imbalance; lesion-wise loss small lesions; CC dice loss instance-aware (2023+); small object seg loss size-aware
Candidates:
- doi:10.1007/978-3-031-34048-2_58 blob loss (Kofler 2023, IPMI) arXiv 2205.08209
- arxiv:2511.17146 CC-DiceCE (ISBI 2026) recall up, precision dataset-dependent
- arxiv:2609.30223 BiCC (2026) adds prediction-derived components, FP term, alpha; code github TIO-IKIM/BiCC-Loss
- arxiv:2604.24276 multi-class CC/blob loss + inverse-size weighting within component (BraTS-METS)
- arxiv:2604.08015 CATMIL: component-adaptive Tversky (inverse size) + lesion MIL term (max-prob per lesion); code github luumsk/SmallLesionMRI; small lesion recall 0.873 vs 0.796
- arxiv:2310.02829 All sizes matter (blob loss ensemble, BraTS-METS)
- arxiv:2407.09828 Adaptive focal loss size+smoothness, code rakibuliuict/AFL-CIBM
- arxiv:2304.06229 ICI loss
