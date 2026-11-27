# D34 notes (work in progress)

Queries run:
1. WebSearch: ensemble distillation semantic segmentation single student 2024 2025 arXiv -> MTED (2023), DUDES arXiv 2303.09843, JMI 2022 ensemble KD medical seg, BRD arXiv 2401.13174
2. WebSearch: model soups segmentation medical -> FissionFusion arXiv 2403.13341 (classification only)
(MCP 502 at 14:33, retrying)
(WebSearch budget exhausted after 2 calls; MCP back at ~14:40)
3. MCP: knowledge distillation semantic segmentation (2020+) -> CIRKD doi:10.1109/cvpr52688.2022.01200 (arXiv 2204.06986); BPKD doi:10.1109/wacv57701.2024.00110 (2306.08075); FAKD 2208.14143; SSTKD
4. MCP: ensemble distillation into single network segmentation -> Noothout JMI 2022 doi:10.1117/1.jmi.9.5.052407; DUDES arXiv 2303.09843; Allen-Zhu arXiv 2012.09816; retinal vessel ens distill arXiv 2509.11689; crop seg SEKD arXiv 2304.01029; adaptive multi-teacher med seg limited data doi:10.1016/j.knosys.2025.113196
5. MCP: model soups -> arXiv 2203.05482; Model Stock arXiv 2403.19522; Quantized soup shake-up KDD 2026 doi:10.1145/3770855.3817826; Branch Soup neucom 2026
Handbook facts: TTA "closed" in doc 20 = test-time BN adaptation, NOT flip TTA. EMA teacher vs student within +-0.005 in MT runs (EMA effect ~0, under MT). A3 soup of 5 PF seeds proposed 30 Oct, not run. Doubling RN34 ensemble did not move E1 target (+0.001). E5 distillation to 2-5M not run.
6. MCP: stochastic weight averaging segmentation generalization -> SWAD arXiv 2102.08604; mostly DG noise
7. MCP: self-distillation semantic segmentation noisy labels -> pixel-wise adaptive label smoothing self-KD doi:10.3390/s22072623; OPAB rs 2025 doi:10.3390/rs18010022; BPKD again
8. MCP: test-time augmentation segmentation aggregation -> Better Aggregation in TTA doi:10.1109/iccv48922.2021.00125 (2011.11156)
9. MCP: heterogeneous ensemble CNN transformer segmentation -> Nanni Sensors 2023 doi:10.3390/s23104688 (polyp); rest classification noise
10. MCP: KD crack segmentation lightweight -> arXiv 2404.06258 robust feature KD crack; EL NAS+KD Applied Energy 2024 doi:10.1016/j.apenergy.2023.122184 (2302.07455); MambaU-Light multi-teacher (UNet++/TransUNet) doi:10.1080/10589759.2025.2505089; jobe 2023; mice 2025
11. MCP: KD patient consistent -> Beyer doi:10.1109/cvpr52688.2022.01065 (2106.05237); Stanton arXiv 2106.05945
12. MCP: EMA of weights dynamics -> Morales-Brotons arXiv 2411.18704
13. MCP: diverse weight averaging OOD -> DiWA arXiv 2205.09739; Ratatouille 2212.10445
14. MCP: packed ensembles -> Packed-Ensembles arXiv 2210.09184; BatchEnsemble calibration 2601.16936; Network Fission Ensembles 2408.02301
15. MCP: weight averaging KD domain shift -> Berezovskiy arXiv 2309.11446; Stanton 2106.05945
16. MCP (2025+): ensemble KD segmentation -> uncertainty-driven adaptive self-KD med seg doi:10.1109/tetci.2025.3526259; heterogeneous snapshot distillation 3D seg arXiv 2606.25278; task-performance routing multi-teacher CT arXiv 2610.41362
17. MCP (2025+): KD semantic segmentation logits -> canonical KD surprising effectiveness arXiv 2604.25530; HeteroAKD arXiv 2504.07691 (AAAI25); DIST+ TPAMI 2025; RLD ICCV25
18. MCP: noisy student self-training seg -> Noisy Student doi:10.1109/cvpr42600.2020.01070; SelectSeg crack noisy ann doi:10.1016/j.ress.2025.110909
19. MCP: uncertainty weighted fusion ensemble seg -> EL CNN-Transformer ensemble INFINITYS 2026 doi:10.1109/infinitys69204.2026.11666283 (SegFormer-B0+Edge-LDRM 0.55 / UNet++ 0.45 soft fusion, 5 classes, defect mIoU 0.7786 internal test); AUE Salvi asoc 2024 doi:10.1016/j.asoc.2024.112081; Buddenkotte calibrating ensembles arXiv 2209.09563; Layer Ensembles 2203.08878
20. similar_papers(Noothout, Fadugba, DUDES) -> Qin TMI 2021 EMKD arXiv 2108.09987; Holder ICCVW21; MTED
21. get_citations(model soups) -> Fisher merging 2111.09832; nothing seg-specific
22. MCP: model soup weight averaging seg medical -> IMWA arXiv 2404.16331 (PR 2025: iterative parallel-from-same-init averaging, class-imbalanced, early-epoch avg best); Rethinking WA merging 2411.09263
23. MCP: snapshot ensembles FGE -> Ashukha pitfalls arXiv 2002.06470; DICE 2101.05544
24. MCP: TTA aleatoric seg -> timed out
Paper details: canonical KD 2604.25530 (Brox group): compute-matched canonical logit/feature KD beats seg-specific KD; R18 student 79.0 vs R101 teacher 79.8 Cityscapes. Noothout: distilled single CNN matched ensembles (uniform seeds and diverse) on 3 datasets, beat same net trained on reference labels. EL NAS+KD 2302.07455: classification, 1.85M params, 91.74% acc ELPV.
--- resumed 13 Nov ---
25. MCP: ensemble distillation semantic segmentation (2020+) -> DUDES, XDED arXiv 2211.14058 (ECCV22 cross-domain ensemble distill DG), Chao CVPRW21 2104.14203, Self-Decoupling ens distill AAAI23
26. MCP: knowledge distillation semantic segmentation (2020+) -> CIRKD, BPKD, FAKD, SSTKD (repeat)
27. MCP: TTA thin structure seg vessel crack -> TopoTTA ICCV25 arXiv 2508.00442 (test-time adaptation, not plain TTA); nothing on flip-TTA for thin structures
28. MCP (2023+): self-distillation dense prediction -> USKD ICCV23 arXiv 2303.13005; Af-DCD NeurIPS23 2312.04168; BRD 2401.13174
29. MCP: SWA medical seg -> noise
30. WebSearch: model soup segmentation 2025 -> no seg-specific soup paper; Rethinking WA merging 2411.09263
31. MCP (2025+): ensemble KD segmentation -> multi-teacher KD retinal vessel HISS 2025 doi:10.1007/s13755-025-00356-4; heterogeneous snapshot distill 2606.25278; task-perf routing 2610.41362
Verified: Noothout JMI22 abstract (distilled = ensemble, beats same net on labels); canonical KD 2604.25530; Fadugba 2509.11689 (FR-UNet, DRIVE/FIVES, 5-model ensemble)
32. MCP: self-distill label noise -> DLB CVPR22 arXiv 2203.16172; label relaxation AAAI21
33. MCP (2023+): heterogeneous ensemble CNN transformer seg -> Nanni polyp Sensors23 (again); classification noise
34. MCP: TTA aggregation learned seg -> Better Aggregation TTA ICCV21; Discard-in-subsampling ECCV24 arXiv 2410.01083 (code github.com/ca-joe-yang/discard-in-subsampling, seg tested)
35. search_snippets flip TTA thin -> S2 rate-limited
Verified: MTKD retinal thin/thick specialist teachers (HISS 2025, +8.44 F1 over U-Net, code claimed public, URL unverified); IMWA PR 2025; Beyer CVPR22; EMA dynamics 2411.18704 (noisy-label robustness); SWAD code github.com/khanrc/swad; DiWA; Model Stock code github.com/naver-ai/model-stock; Packed-Ensembles code torch-uncertainty; INFINITYS 2026 EL ensemble
36. similar_papers(Noothout, Fadugba) -> Qin TMI21 EMKD, Asif ensemble KD, Layer Ensembles, MTED
37. get_citations(Beyer) -> model soups, Stanton, Distillation Scaling Laws 2502.08606
38. MCP: KD lightweight crack seg <5M (2024+) -> RFKD arXiv 2404.06258 (0.5M PCT student)
39. MCP (2024+): weight averaging checkpoints seg DG -> ERM++ WACV25 2304.01973; flat minima large LR 2309.06337
40. WebSearch x2: MTKD retinal code (not found, unverified); CIRKD code github.com/winycg/cirkd (verified via search)
Read: canonical KD 4.3/4.4: Pure logit KD + 20k unlabelled images reaches 79.0 (99% teacher); feature KD does not gain from unlabelled; Mask2Former teacher not better than aligned PSPNet teacher.
Read: IMWA results: IMWA +0.8 to +1.8 top1 over base; vanilla MWA +0.2; IMWA+EMA additive.
Selection done, writing D34 file.
