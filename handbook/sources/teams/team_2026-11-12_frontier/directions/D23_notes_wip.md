# D23 resume notes (13 Nov)
MCP back up (OpenAlex works; S2 rate-limited at times).
New since 12 Nov file:
- get_citations EoMT (56 total): EoSeg arxiv:2607.00223 (encoder-only ViT for medical, 7 datasets, code github.com/Retinal-Research/EoSeg); LUMA arxiv:2607.00687 (backbone-agnostic mask head, 20 backbones, pretraining objective governs quality, code github.com/tobna/LUMA); UDA in VFM era doi:10.1109/cvprw63382... (cvprw67362.2025.00238); PMT arxiv:2603.25398; token-space mask prediction arxiv:2605.18177
- iFAN arxiv:2608.03216: APMR ranking + cross-layer self-distillation, training-only, +0.63 mIoU avg
- Frequency-based matcher LTSS arxiv:2406.03917 (TMM 2024): one-to-many matching, number of queries per class from frequency; LT benchmark + dual metric
- Devil is in the Queries arxiv:2304.00212 (CVPR 2023): MaxQuery OOD + query-distribution loss; +5.27 DSC over nnU-Net on pancreas/liver tumours
- Enhanced M2F bridge crack doi:10.1109/tits.2025.3578810: multi-scale fusion + high-res WTConv module, mIoU 86.33
- Zhu M2F pavement crack doi:10.3390/electronics14142834: LPM + aux conv high-res, +3.2 mIoU over baseline
- feature upsamplers: LoftUp arxiv:2504.14032 (ICCV25, github.com/andrehuang/loftup), JAFAR arxiv:2506.11136 (NeurIPS25), NAF arxiv:2511.18452, Upsample Anything arxiv:2511.16301, "Maybe you don't need a U-Net" arxiv:2508.21529 (micrographs, hairline cracks)
- Primus arxiv:2503.01835, MedDINOv3 arxiv:2509.02379 (D25/D24 territory)
- WebSearch: EoMT repo DINOv3 configs, EoMT-L DINOv3 ADE 59.5 mIoU at 512; HF transformers has eomt_dinov3
- search hits: MR-Former doi:10.1016/j.aej.2025.09.072; Mask2Anomaly doi:10.1109/tpami.2024.3419055; PDeT doi:10.3390/s24216908 (PV deformable transformer seg); Hijjawi doi:10.1016/j.solener.2025.114083; SegMAN doi:10.1109/cvpr52734.2025.01777
