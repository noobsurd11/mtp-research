# D35 notes (work in progress)

14:34 start. Research MCP returned 502 on first 4 calls. WebSearch budget exhausted for the session (shared limit), so no web verification of repos is possible in this phase.
14:36 MCP still 502 (7 tries). Fallback: WebFetch arXiv abs pages for known ids (verified):
- arxiv:2202.10054 LP-FT, ICLR 2022 oral. FT vs LP: +2% ID, -7% OOD; LP-FT vs FT +1% ID, +10% OOD (10 shift datasets). No code on page.
- arxiv:2210.11466 Surgical FT, ICLR 2023. Shift type picks layers; corruptions -> first layers. No code on page.
- arxiv:2102.08604 SWAD, NeurIPS 2021, github.com/khanrc/swad. +1.6 avg OOD acc on 5 DG benchmarks.
- arxiv:2109.01903 WiSE-FT, CVPR 2022. Weight interp. +4-6 pp under shift, +0.8-3.3 pp transfer. No code on page.
- arxiv:2010.01412 SAM, ICLR 2021 (page shows no venue), github.com/google-research/sam. Label-noise robustness.
- arxiv:2405.03676 Why is SAM robust to label noise (Baek et al. 2024). Largest SAM gains under label noise; Jacobian effect; cheaper explicit regularisers recover much.
- arxiv:2310.19182 FTP, NeurIPS 2023, github.com/GT-RIPL/FTP. Per-layer learned projection, AdamW plug-in.
- arxiv:2411.18704 EMA of weights, TMLR. EMA robust to label noise, better transfer, calibration, needs less lr decay.
14:40 MCP back (S2 rate-limited). Queries so far: (1) LLRD seg, (2) robust FT preserve features 2023+, (3) SAM medical seg, (4) L2-SP, (5) nnU-Net revisited, (6) EMA seg, (7) BN small batch, (8) LP-FT seg, citations of surgical FT, similar to LP-FT+FTP.
- arxiv:2411.01713 SPD (NeurIPS 2024) code github.com/GT-RIPL/Selective-Projection-Decay. PASCAL seg Swin-T IN21k Table 4 mIoU ID / OOD avg: Vanilla FT 66.03/44.00, L2-SP 73.47/56.70, LLRD 72.09/54.47, TPGM 72.56/56.96, FTP 73.79/58.45, Adam-SPD 74.27/60.06. lr 1e-4, lambda 2.2, 60 epochs.
- arxiv:1802.01483 L2-SP (2018). arxiv:2406.10050 FT strategies med cls (LP-FT helps >50% cases; Auto-RGN up to 11%).
- arxiv:2502.15895 DiGraP 2025 (classif + VQA only). arxiv:2303.10720 TPGM CVPR 2023.
- doi:10.3390/s24134267 SAM on retinal vessel RF-UNet DRIVE (val acc 0.940->0.968; weak paper).
- doi:10.1007/978-981-96-6688-1_7 SAM-FT single-source DG med seg (Fundus, Prostate), no numbers in abstract.
- arxiv:2505.11769 GOOSE challenge: photometric aug + EMA, 88.8 mIoU val.
- arxiv:2105.07576 Rethinking batch in BatchNorm. arxiv:1903.10520 BCN+WS micro-batch.
- arxiv:2203.05482 model soups. arxiv:2402.09240 Switch EMA.

## Resume pass, 13 Nov 2026
Prior file D35_recipe_finetuning.md (12 Nov) was complete. This pass fills its gaps: code verification (WebSearch), 2025-2026 work, schedule length, augmentation for thin labels, BN at batch 8, AdamW.
Queries this pass (openalex only; S2/scopus/arxiv down): LP-FT distort 2020+, LLRD seg 2020+, SAM seg 2020+, surgical FT 2020+, L2-SP, nnU-Net recipe 2020+, SWAD 2020+, vessel aug thin 2020+.
New candidates: arxiv:2601.22637 Grokking nnU-Net (training beyond convergence, schedule length), arxiv:2009.01907 minimalistic vessel models (Galdran), arxiv:2304.01973 ERM++ (WACV 2025 DG recipe), arxiv:2309.06337 flat minima large lr, arxiv:2607.00634 loss smoothing 2026.
More queries: EMA 2025, robust FT dense 2025, crack aug 2022, fg oversampling patch 2020, GN/BN small batch 2020, SAM med seg 2024, optimizer compare U-Net 2021, weight averaging seg OOD 2024, ImageNet vs scratch defect 2021, gradual unfreezing 2023, schedule length 2022, single-source DG aug 2020, similar_papers(SPD,SWAD,SurgFT), citations(SPD). Web: SPD repo verified (github.com/GT-RIPL/Selective-Projection-Decay, official per NeurIPS paper), Grokking nnU-Net numbers (secondary).
Fulltext read:
- ERM++ (arxiv:2304.01973, WACV 2025, code github.com/piotr-teterwak/erm_plusplus per abstract). ResNet-50 DomainBed avg 68.9; w/o MPA (average all iterates) 65.9 (-3.0, largest); w/o full data 67.7; w/o strong init 67.6; w/o warm start 68.7; w/o unfreeze BN 68.3; w/o Auto-LR 68.4.
- Ghaffari & Wang 2026 (doi:10.21203/rs.3.rs-11088886/v1) Crack500 full-res, U-Net from scratch, AdamW 3e-4, 20k updates, batch 16, BCE+Dice, 3 seeds, AP at 2 px tolerance. Random crops AP2 0.812 (BN) vs aggressive positive-only 0.789 (-0.023); 10% positive 0.730. GroupNorm: random 0.844 vs BN 0.812 (+0.032), aggressive 0.786. Positive-only sampling made 47% of image area unreachable.
- PGPS (arxiv:2510.23241, MedIA 2026): small to large patch curriculum, +1.28% rel Dice over 15 3D tasks, best on severe fg imbalance, lower seed variance.
- Episodic sampling (arxiv:2605.20405, code github.com/iasonsky/episodic-sampling per abstract): iteration budget is a confound; class-balanced batches help in low data.
- SAM in medical (arxiv:2408.04065, IEEE Access 2025): only plain SAM consistently helps; variants inconsistent (classification).
- ASFR (doi:10.1007/s11548-025-03404-2): Fisher + sensitivity regularization for thin vessel seg transfer; Dice 41.3.
13 Nov resume: final file written, 18 papers.
