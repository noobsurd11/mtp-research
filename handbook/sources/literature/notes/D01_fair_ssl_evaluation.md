# Critical evaluation of SSL
- **Oliver et al. 2018**, Realistic Evaluation of Deep SSL Algorithms (NeurIPS 2018, arXiv 1804.09170). https://arxiv.org/abs/1804.09170
  - Read: abstract. Findings:
    - simple, well-tuned baselines often match reported SSL gains;
    - SSL methods differ in sensitivity to labelled and unlabelled amounts;
    - performance degrades with out-of-distribution unlabelled data.
  - Relevance: our external pool is half-contrast and from two sources only, which is class-distribution and appearance mismatch.
- **Zoph et al. 2020**, Rethinking Pre-training and Self-training (NeurIPS 2020). https://mlanthology.org/neurips/2020/zoph2020neurips-rethinking
  - Read: abstract. Self-training helps even where pre-training does not; stronger augmentation reduces pre-training value.
- **nnU-Net Revisited** (Isensee et al., MICCAI 2024, arXiv 2404.09556). https://arxiv.org/abs/2404.09556
  - Read: abstract. "many recent claims ... fail to hold up when scrutinized for ... inadequate baselines, insufficient datasets". A strong, properly tuned baseline is the bar.
- **You et al. 2023**, Rethinking SSL medical segmentation, a variance-reduction perspective (arXiv 2302.01735), and **SemiSAM+** (Zhang et al., arXiv 2502.20749). Titles verified; not read.
- **UniMatch V2** (see B05): SSL gains shrink with strong encoders (Cityscapes about +3).
- Protocol lessons for us (synthesised; each has a source above or in our handoff):
  1. Step-matched supervised baseline: PV-S3's baseline was under-trained; our UCF SL-20 went 0.448 → 0.491 when step-matched.
  2. Loss-off control with an identical forward pass (ours; it isolates BN and stream effects, cf. Yuan et al. 2021).
  3. Multiple labelled splits, not just seeds (Oliver: sensitivity to the labelled set).
  4. A single checkpoint rule fixed in advance, never best-on-test (Fioresi and Torpey use val/test selection; ALHVR uses best-val).
  5. Report per-class and threshold-free metrics (AP) plus a thin-structure metric.
