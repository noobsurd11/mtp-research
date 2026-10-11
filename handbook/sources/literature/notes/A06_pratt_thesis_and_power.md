# Pratt 2024 PhD thesis (Wits) and Pratt 2025 power-degradation study
- Thesis: "Deep learning models for defect detection in electroluminescence images of solar PV modules", Univ. of the Witwatersrand, 2024. https://wiredspace.wits.ac.za/items/188c94a9-0c1e-45f6-92b0-ca0cf6913e71
  - 765 labelled images + 20,000+ unlabelled. Progresses from supervised to semi- and self-supervised pretraining. "DeepLabv3+ trained with custom class weights scored the highest".
- Power-degradation article (CSIR repository listing, venue not confirmed): https://researchspace.csir.co.za/signposting/describedby/e95a2cf3-bbcc-4730-8ecd-246c4d21ccb9
  - 680 fielded modules, 48,960 cells classified into 29 classes. A new "brightening" defect (24 labelled samples) correlates with module fill factor, r² = 0.42.
- Read: repository abstracts only. Weaknesses: not assessed (read scope: abstract_only).
- Relevance: the thesis is the most complete account of BenchmarkEL's evolution and its SSL attempts; read its SSL chapter before designing ours. The power study matters for thesis part 3 (severity): per-defect area, not mIoU, is what links to power loss.
