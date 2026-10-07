# ALHVR's neighbourhood: dual-network and region-aware medical SSL
- **MCF** (Wang et al., CVPR 2023): Mutual Correction Framework. https://openaccess.thecvf.com/content/CVPR2023/html/Wang_MCF_Mutual_Correction_Framework_for_Semi-Supervised_Medical_Image_Segmentation_CVPR_2023_paper.html · code https://github.com/WYC-321/MCF
  - Two heterogeneous subnets. A contrastive difference review re-trains inconsistent regions. Dynamic competitive pseudo-label generation picks the better subnet in real time; it is the ancestor of ALHVR's DTCT. ALHVR's critique: MCF fails when both predictions are wrong. Read: abstract.
- **BUR** (Zhou, Zhao, Sun, arXiv 2502.07457, 2025): Bidirectional Uncertainty-Aware Region Learning. https://arxiv.org/abs/2502.07457
  - The *opposite* allocation to ALHVR. On labelled data it focuses the loss on **high-uncertainty** regions, where the true label is known. On unlabelled data it uses only **low-uncertainty** regions. Read: abstract.
  - **Relevance: a strong alternative hypothesis for rare thin classes.** Ambiguous crack pixels may be better learned from labelled images than from pseudo-labels.
- **ABD** (Chi et al., CVPR 2024, arXiv 2405.00378): Adaptive Bidirectional Displacement, a perturbation scheme. Title verified; not read.
- **AD-MT** (Zhao et al., arXiv 2311.17325): Alternate Diverse Teaching. Title verified; not read.
- **BCP** (Bai et al., CVPR 2023, arXiv 2305.00673): Bidirectional Copy-Paste between labelled and unlabelled images in Mean Teacher. +21% Dice on ACDC 5% (abstract). Relevance: copy-paste across the labelled/unlabelled boundary is one way to put rare structures into unlabelled batches. Read: abstract.
- Weaknesses: not assessed for any of these (read scope: abstract_only), except as noted.
