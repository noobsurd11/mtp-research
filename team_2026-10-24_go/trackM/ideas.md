# Track M ideas (MC)

MC, 24 Oct 2026. Papers cited only by Research MCP ids returned in this session. **E** measured here, **R** reading, **S** speculation. These are proposals for MD's ladder, not approvals; each still needs a protocol.

## 0. Facts that shape the ladder (E)
- **Every released cell is already 512 x 512** (test: 50 of 50, all sources; E-SCDD masks are 512 too). L3 trains at 512, so "no downscaling" is already true. The open resolution lever is **upsampling the input** (for example 768 or 1024) so that a 1.75 to 2.5 px crack survives the encoder's stride-4 and stride-8 stages, then scoring at 512.
- Crack belief at 5% is bimodal: 8% of GT crack sits in 0.001 to 0.95 (C, `results/al1/hist_revised.npz`). Thresholds and LA can only move that band. MD will measure it at 100% in M0.
- At 100%, ARTS and BMRK crack IoU still rise from 50% to 100% labels (C's recompute). CFVS and CSIR flatten.
- A 1-px shift of a perfect crack mask scores 0.47 to 0.56 IoU (handbook 13 A5). For "almost all cracks", crack recall and relaxed recall@2 are the honest targets; strict IoU caps out early.

## 1. Ranked rung candidates (critic's view of expected value per GPU-h)

| # | Rung (one change vs current best) | Why (evidence) | Risk to watch | Paper |
|---|---|---|---|---|
| 1 | **Input upsampling x1.5 or x2, score at 512** | Cracks are 1.75 to 2.5 px wide; a stride-32 encoder sees them only in its first stages. High-resolution crack work keeps detail by not shrinking thin cracks (R). BMRK is the blurriest source with 4-px labels, so upsampling may help it least: report per source | 2.25x to 4x compute per step: state GPU-h; batch or crop changes are a second change unless held fixed | Chu & Chun 2023, `doi:10.1111/mice.13111`; Kondo & Ukita 2024 (joint super-resolution + crack segmentation for degraded images), `arxiv:2302.12491` |
| 2 | **Skeleton Recall loss added to CE+Dice** | Built for thin structures including cracks; multi-class; cheap (CPU skeletons). Targets recall of thin components, the user's "almost all cracks" | P14's offset-tolerant loss was null, and C says misses are faint, not broken (R). Watch crack precision and relP@2 (R4 flag at 0.05) | Kirchhoff et al. 2024, `doi:10.1007/978-3-031-72980-5_13` (`arxiv:2404.03010`) |
| 3 | **Encoder swap at fixed decoder (U-Net++ with ConvNeXt-T or a larger ResNet)** | P4 frozen probe: ConvNeXt-T crack AP 0.331 vs DINOv2 0.183 (`results/p4_feature_probe/README.md`). A properly configured U-Net often beats newer architectures | Pretraining and compute change together; state params and FLOPs. Stem stride matters for 2-px cracks (ConvNeXt's stem is stride 4) | Isensee et al. 2024, nnU-Net revisited, `arxiv:2404.09556` |
| 4 | **Transformer decoders (SegFormer etc.)**: low priority | SegFormer predicts at 1/4 resolution; for 2-px cracks that is a structural handicap (R) | Same as 3 | Xie et al. 2021, `arxiv:2105.15203` |
| 5 | **Recall-weighted CE (dynamic per-class weights)** for crack and inactive | Re-weights by running recall, between CE and inverse-frequency; the paper itself warns fixed up-weighting causes false positives | Exactly the "recall bought with precision" failure: precision must be reported and bounded in the protocol | Tian et al. 2022, `arxiv:2106.14917` |
| 6 | **IoU-surrogate loss (Lovasz or Jaccard metric loss) in place of Dice** for the mIoU goal | Directly optimises per-class IoU; helps the "balanced mIoU" part | Small effect expected over CE+Dice (S) | Berman et al. 2018, `doi:10.1109/cvpr.2018.00464`; Wang et al. 2023, `arxiv:2302.05666` |
| 7 | **Seed ensemble + dihedral TTA**, operating point frozen on val | Cheap at inference; probably reduces the noisy-cell failure (1 run in 6) by averaging (S) | 5x training compute; comparator is the 5-seed mean of single models, never the best seed. Validate uncertainty and TTA effects with a proper protocol | Kahl et al. 2024, ValUES, `arxiv:2401.08501` |
| 8 | **+107 E-SCDD cells** (`data_addendum.md`) | +12% crack px, +14% inactive px | Nearly all CSIR, our best source; expected small (R) | data audit only |

## 2. Not recommended, or only with a new reason
- **Logit adjustment at 100%:** about 0 gain at 50 to 100% labels, costs about 0.03 crack precision (C, `results/sk1/la_sa.md`).
- **Fixed inverse-frequency class weights:** the old era did this; the Recall-loss paper documents the false-positive cost. Use 5 if anything.
- **Topology-specific crack architectures from EL papers** (STC-Net, `arxiv:2608.01714`): reports 95.98 mIoU on train vs 72.52 on unseen test, on another dataset (PVEL-S) with an unstated split. No transferable evidence.
- **Ensembles of different architectures picked on test:** never.

## 3. Domain references (context only)
- Chen et al. 2023, crack segmentation and features in EL modules, `doi:10.1109/jphotov.2023.3249970`.
- Pratt et al. 2023, the BenchmarkEL dataset, `doi:10.1016/j.sasc.2023.200048`.
