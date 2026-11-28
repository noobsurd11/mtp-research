# D28 resume notes (13 Nov 2026), MCP now up (openalex + arxiv; s2 rate-limited, scopus/SD 401)
Prior file D28_frequency_priors.md (12 Nov) built from WebFetch only. Resume = MCP searches + snowball.
q1 wavelet U-Net thin structures 2020+: SUPER arxiv:2511.11015 confirmed; CS2-Net doi:10.1016/j.media.2020.101874
q2 defect seg periodic texture 2020+: TexWDS arxiv:2603.14282 confirmed; FMR-Net doi:10.1109/tase.2022.3204368 (textured surface)
q3 learnable Frangi 2019+: FFPN = doi:10.1016/j.media.2024.103442 (MedIA 2025); Hessian vector field DG doi:10.1016/j.media.2024.103164; Frangi neuron doi:10.3390/electronics12194159
q4 wavelet crack seg 2025+: CrackLIFT doi:10.1007/s44443-026-01379-x (learnable lifting wavelet + wavelet-target alignment loss, CrackSeg9k 82.10 mIoU); MHFFNet, StarCrack, WMCrack (no abstract)
q5 freq domain thin structure 2024+: WaveInst arxiv:2505.01656 (TGRS 2026); SPIRONet doi:10.1016/j.bspc.2026.110814 arXiv 2406.19749; VFGS-Net arXiv 2602.10978; brain tumor freq TMI 2025 arXiv 2506.10142
q6 Fourier periodic removal TFT-LCD wafer PCB: nothing useful (3 results)
q7 learnable Gabor 2020+: Gabor seismic doi:10.1109/tgrs.2024.3365910 arXiv 2308.05202 (limited training data generalisation); 3D Gabor kernels arXiv 2201.03644
q8 snippets EL Fourier busbar: S2 rate-limited
q9 EL crack freq wavelet 2020+: NWG-DETR doi:10.1088/2631-8695/aea73d VERIFIED (PVEL-AD mAP50 +3.77, LWaveletPool/UnPool, grid-line gating); WASR doi:10.3390/mi17080907 (+2.4 mAP50 YOLO11); YOLO-PVELAD doi:10.1007/s44443-026-00566-0 (DCT HF FPN + directional 1D attention, +14.8 mAP50 single seed); YOLOv10-WaC doi:10.3233/atde260843
q10 similar(SUPER,TexWDS): mostly SR / wafer classification, nothing new useful
q11 XNet search 2023+: XNet doi:10.1109/iccv51070.2023.01928; XNet v2 doi:10.1109/bibm62325.2024.10822699; SFFNet doi:10.1109/tgrs.2024.3427370; IYNet BIBM 2025 LF/HF perturbation; Adaptive wavelet-VNet TTA doi:10.1002/mp.17423
q12 citations(XNet): nnWNet doi:10.1109/cvpr52734.2025.01942 (code yanfeng-zhou/nnWNet, unified benchmark, DRIVE/CREMI); WP-Former doi:10.1109/cvpr52734.2025.02222 (SDD, CrackSeg9k, ZJU-Leaper fabric; code yfhdm/WPFormer "will be"); GobletNet doi:10.1109/tmi.2024.3474028 (wavelet HF fusion EM); fractal feature maps tubular arXiv 2407.14754
q13 Fourier amplitude DG seg 2022+: Pasta doi:10.1109/iccv51070.2023.01767 (HF amplitude perturbed more, GTAV-to-real); RaffeSDG arXiv 2409.04768; FIESTA arXiv 2406.14308; RAM doi:10.1007/978-3-031-19803-8_25; freq-aware domain randomization doi:10.1002/mp.70118
q14 fabric periodic texture 2022+: WOT-AE doi:10.3390/sym17111829 (patterned fabric, low-rank); texture regularity SSL doi:10.2139/ssrn.7589368 (no abstract); FMR-Net
q15 wavelet downsampling seg 2023+: KEY aliasing line. SFM TPAMI 2025 doi:10.1109/tpami.2025.3592621 arXiv 2507.11893; Seg-Aliasing arxiv:2403.09065 (DAF + FreqMix, code Linwei-Chen/Seg-Aliasing); AAAI 2026 DGK+Gabor LFS doi:10.1609/aaai.v40i9.37713; matched wavelet pooling doi:10.1007/s00521-025-11008-9
S: finger pitch ~5-6 px at 512 -> above Nyquist after stride 2 (0.5 cyc/px at 256 means pitch < 4 px of 512-grid aliases at stride 4). Check with real pitch.
q16 Hessian ridge crack 2020+: crack-preserving downsampler doi:10.1016/j.ijfatigue.2025.109179 (Duits; steel bridge CSB); YoloCurvSeg; FreeCOS (other dirs)
q17 periodic bg suppression 2021+: nothing new
q18 Gabor crack 2022+: GRooUV arXiv 2509.00827 (Gabor + reconstruction U-Net-ViT, surface defects)
q19 orientation score: Riesz Networks arXiv 2305.04665 (scale-invariant, cracks in CT) low
q20 citations(HWD, 520 cites): pyramid HWD attention U-Net RC damage doi:10.1016/j.autcon.2024.105746 (no abstract)
q21 freq masking SSL: SpectraFlow arxiv:2605.14566 (low-data med seg, freq-directional dyn conv) low
fulltext Seg-Aliasing (ICLR 2024): DAF+FreqMix UPerNet-R50 Cityscapes 78.1->79.7 mIoU, BIoU 61.8->63.2; DAF parameter-free; cutoff from equivalent sampling rate (sqrt2/4)
Hessian vector field DG: no abstract, no full text
WebSearch EL busbar suppression 2025-26: nothing; MultiSolSegment arXiv 2603.13337 (data, in BRIEF)
- final file written 13 Nov
