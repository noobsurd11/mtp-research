D30 WIP notes (DG / UDA)

WebSearch (4 calls, then session budget exhausted):
- Rein: arXiv 2312.04265, CVPR 2024, code github.com/w1oves/Rein (web-verified). Rein++ arXiv 2508.01667 (covered by D24 #1, #2).
- MIC: arXiv 2212.01322, CVPR 2023, code github.com/lhoyer/MIC (web-verified). R: 75.9 mIoU GTA->Cityscapes.
- DGInStyle: arXiv 2312.03048, ECCV 2024, code github.com/yurujaja/DGInStyle and prs-eth listing (two accounts; unverified which current).
- SSDG medical: ICMSeg arXiv 2411.05223 WACV 2025 code github.com/ratschlab/ICMSeg; MEDU MICCAI 2025 code github.com/wrf-nj/MEDU; FA-SAM arXiv 2507.17281 (no code seen); SRCSM arXiv 2512.01510 (code on acceptance); color-quality invariance arXiv 2502.07200.
Overlap: FDA, FACT/APR, DFF in D28; Rein, Rein++, Causal-Tune, spectral tokens in D24.
Research MCP: 502 errors at 14:29 (4 tries).

14:31 MCP still 502 (7 tries). Fallback: WebFetch of arXiv abs pages (verified):
- arxiv:2111.12525 GIN-IPA causality SSDG medical, code github.com/cheng-01037/Causality-Medical-Image-Domain-Generalization (peer-reviewed version in IEEE TMI per page note)
- arxiv:2211.14805 SLAug, code github.com/Kaiseem/SLAug (AAAI 2023 from memory, page shows no venue)
- arxiv:2304.00424 Pro-RandConv CVPR 2023, no code on page
- arxiv:2312.03048 DGInStyle ECCV 2024, dginstyle.github.io
- arxiv:2204.13132 HRDA ECCV 2022, github.com/lhoyer/HRDA, +5.5 mIoU GTA->CS (73.8)
- arxiv:2206.01737 MaxStyle MICCAI 2022, github.com/cherise215/MaxStyle
- arxiv:2112.11177 Dual-Normalization CVPR 2022, github.com/zzzqzhou/Dual-Normalization
- arxiv:2312.09788 CLOUDS CVPR 2024, github.com/yasserben/CLOUDS
- arxiv:2407.09033 tqdm ECCV 2024, 68.9 GTA->CS
- arxiv:2303.11546 TLDR ICCV 2023, github.com/ssssshwan/TLDR
- arxiv:2412.04077 SoMA CVPR 2025, project page only
- arxiv:2007.13003 RandConv ICLR 2021, github.com/wildphoton/RandConv
Rein++ html table: SoMA 68.2 avg, MFuser 68.2, FisherTune 66.6, FADA 66.1, tqdm 66.1, Rein 64.9, CLOUDS 61.5, DGInStyle 57.8 (GTAV->CS/BDD/Map). UDA: MICDrop ECCV24 76.6, QuadMix TPAMI25 76.1, Rein++ Rein-A 78.2.

14:40 arXiv API search (export.arxiv.org) used as fallback index; PDFs read with pdftotext in scratchpad.
- GIN-IPA (2111.12525) Table II, U-Net EffNet-b2: abdominal CT->MRI avg Dice ERM 77.31 -> 86.31 (RandConv 80.66); cardiac bSSFP->LGE 75.99 -> 85.01 (RandConv 83.73); prostate cross-center 56.59 -> 70.37 (RandConv 57.74). GIN-only prostate 65.10 (IPA adds 5.3). Default GIN 4 layers, 2 hidden channels.
- SLAug (2211.14805, AAAI 2023 per pdf footer): abdominal avg 88.63 / 83.05 both directions; +2.49 Dice over CSDG(GIN-IPA) cross-modality.
- MIC (2212.01322): b=64, r=0.7, lambda 1, EMA 0.999; +1.2 to +4.7 mIoU over UDA methods incl. DeepLabV2 CNN; supervised only +0.3; most gain on sidewalk, fence, pole, traffic sign, rider (thin/context classes).
- DAFormer (2111.14887): RCS + thing-class ImageNet feature distance + warmup; ablation 58.2 ST -> 61.7 +FD, 64.0 +RCS, 66.2 both; source-only DG: RCS+FD +5.1 mIoU (supp Tab S3); works on DeepLabV2 too.
- SoMA (2412.04077) code github.com/ysj9909/SoMA (in paper); SVD minor component init of LoRA, block freeze, annealing wd.
- arXiv DGSS 2025-26: MFuser 2504.03193 CVPR25 github.com/devinxzhang/MFuser; FisherTune 2503.17940 CVPR25; DepthForge 2504.12753 ICCV25; HPI 2609.05864 ECCV26 github.com/MosukFate/HPI; RecycleLoRA 2603.28142 CVPR26 Findings; LoCA 2607.06918 ECCV26 (low-rank conv adaptation); SCSD 2412.12050; semantic rearrangement 2404.13701 (Neural Networks 2025).
- SSDG medical 2024-26: RaffeSDG 2405.01228 (code liamheng), FreeSDG 2307.09005, MoreStyle 2403.11689 MICCAI24 code, RAS4DG 2409.04768 MICCAI24, UniDDG 2501.04741, AngioDG 2511.17724 (thin vessels), WISER 2603.28463, SRCSM 2512.01510 IEEE Access.
- Thin: CrackUDA 2412.15637 ICPR24; AdaptDiff 2410.04648; FreeCOS 2307.07245 (D06).
