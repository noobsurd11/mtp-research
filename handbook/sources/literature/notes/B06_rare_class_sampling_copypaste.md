# Rare-class sampling and copy-paste (from UDA and instance segmentation)
- **DAFormer** (Hoyer, Dai, Van Gool, CVPR 2022, arXiv 2111.14887). Read: abstract.
  - **Rare Class Sampling (RCS)**: source images containing rare classes are sampled more often, which "improves pseudo-label quality by mitigating confirmation bias toward common classes". Enables learning of train, bus and truck.
  - Relevance: a cheap knob for us. Oversample labelled images with crack or inactive in the labelled stream, and decouple the operating-point effect from class weights.
- **Simple Copy-Paste** (Ghiasi et al., CVPR 2021, arXiv 2012.07177). Read: abstract. Copy-paste of instances is a strong augmentation. For 2–3 px cracks the blending and the cell-texture context matter. [reader-inferred]
- **AEL** adaptive copy-paste (see B04): in AEL's cumulative ablation ACP added +0.85 (1/32) and +0.71 (1/16). AES added +2.24 (1/32) but only +0.54 (1/16), and DR +1.16 / +1.72. No single component dominates across splits.
