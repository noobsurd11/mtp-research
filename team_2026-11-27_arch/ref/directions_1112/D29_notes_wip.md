# D29 notes (work in progress)

- 14:25-14:27 Research MCP: 502 Bad gateway on every call (search_papers x4, get_paper, server_status). WebSearch: 4 calls ok, then session budget exhausted (shared 200). Fallback: WebFetch of arXiv abs pages for ids I know, to verify each.

Verified (arXiv abs page fetched):
- arxiv:2410.10777 UniMatch V2, TPAMI (comment), code github.com/LiheYoung/UniMatch-V2
- arxiv:2311.16241 SemiVL, Hoyer et al, ECCV 2024 (web search), code github.com/google-research/semivl
- arxiv:2403.01818 AllSpark CVPR 2024, code github.com/xmed-lab/AllSpark
- arxiv:2212.01322 MIC CVPR 2023, code github.com/lhoyer/MIC
- arxiv:2006.06882 Zoph Rethinking pre-training and self-training NeurIPS 2020 (self-training +1.3 to +3.4 AP at all data sizes incl. 100%)
- arxiv:2005.10266 Naive-Student ECCV 2020
- arxiv:2401.10891 Depth Anything CVPR 2024 (strong perturbation + feature alignment to pretrained encoder on unlabeled)
- arxiv:2502.20749 SemiSAM+ (MedIA 2025 per web search)
- arxiv:2204.13132 HRDA ECCV 2022, github.com/lhoyer/HRDA
- arxiv:2208.09910 UniMatch CVPR 2023
- arxiv:2411.16949 SAMatch (preprint), github.com/apple1986/SAMatch
- arxiv:2505.19846 SAM+CLIP pseudo labels ICIP 2025, no code
- arxiv:1712.04440 Data distillation (omni-supervised), tech report
- arxiv:2106.05237 Beyer KD patient and consistent, CVPR 2022
- arxiv:2106.05095 ST++ CVPR 2022, github.com/LiheYoung/ST-PlusPlus
- arxiv:2111.14887 DAFormer CVPR 2022 (RCS, ImageNet FD), github.com/lhoyer/DAFormer
- arxiv:2305.00673 BCP CVPR 2023 (close to tried CutMix MT)
- arxiv:2406.09414 Depth Anything V2 NeurIPS 2024
- arxiv:2110.05474 AEL NeurIPS 2021, github.com/hzhupku/SemiSeg-AEL
- arxiv:2307.11960 DHC MICCAI 2023, github.com/xmed-lab/DHC
- arxiv:2312.06316 SemiSAM BIBM 2024
- arxiv:2201.08657 EPL SemiDG AAAI 2022, github.com/XMed-Lab/EPL_SemiDG
- arxiv:2306.04300 CorrMatch, github.com/BBBBchan/CorrMatch
Key numbers:
- UniMatch V2 html: Pascal full 1464 labels DINOv2-B 90.8 vs 88.3 labeled-only (+2.5); DINOv2-S 87.8 vs 85.6. Cityscapes 1/2: 85.1 vs 84.4. ADE20K 1/4: 52.0 vs 49.0. Complementary dropout = binomial channel mask on two views. tau 0.95, EMA 0.996.
- Depth Anything V1 html Table 9: unlabeled without perturbation no gain; with color jitter+blur+CutMix gain; plus feature loss (1-cos to frozen DINOv2, margin 0.85) further gain; student re-initialised; "we failed to gain improvements with such a self-training pipeline" when plain.
- MIC: patch 64, ratio 0.7, lambda 1, EMA 0.999, confidence weighting needed (-1.6 without). GTA-CS +2.1 on HRDA; DeepLabV2 R101 +1.2 to +4.5. Gains largest on low-baseline classes (fence +5.4, pole +2.6). +24% train time.
- From web search only: arxiv:2505.19846 SAM+CLIP zero-shot pseudo labels (ICIP 2025); arxiv:2411.16949 SAMatch
