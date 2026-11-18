# T11 family cards: the benchmark method suite (13 Nov 2026)

Analyst T11. Tags: R = from the paper or its repository (fetched page), E = from our files (path given), S = my judgement. The Research MCP paper tools were not available in this session (ToolSearch found none), so every R below comes from arXiv HTML pages, GitHub README / raw source files fetched with WebFetch, or from the handbook where it already holds a full read (cited as E, handbook 05). Nothing was run, installed or downloaded. Ledger: `ledger/T11.tsv` (48 papers). Spec: `T11_method_suite_spec.md`.

Full text read for this card: RIFT (arXiv HTML), SCSegamba (arXiv HTML, method and experiments). Source files read: RIFT `rift.py`; SCSegamba `models/decoder.py`, `SAVSS.py`, `SAVSS_layer.py`; DSCNet `S3_DSCNet.py`, `S0_Main.py`; HrSegNet `hrsegnet_b48.py`. READMEs read: SCSegamba, RIFT, MixerCSeg, CrackMamba, HrSegNet, Hybrid-Segmentor, CoANet, BiRefNet, sntubix/pv-defect-segmentation. Handbook 05 (full reads of Pratt 2023, Torpey 2024, Fioresi 2022, PV-S3, E-SCDD, MultiSolSegment) used for the EL rows.

## 0. What the suite must answer, and what already exists (E)

- Existing or planned rows not owned by T11: house U-Net++ R34 (W1-C2), PF (W1-C1, 5 seeds), PF on v1 labels (W1-C3); harness milestone row UPerNet + ConvNeXt-T IN-1k (card `upernet_convnext_t_in1k`, gate not measured); T6: HR-stem U-Net++ ConvNeXt-T, SAM2 Hiera-B+ U-Net++, nnU-Net ResEnc-L, DINOv3 / DINOv2 rows; T5 named official DSCNet 2D as a suite entry and left it to the suite.
- Published EL numbers are not comparable (PROTOCOL 1, twelve causes). So no published EL number below is a target; each EL paper enters as a re-run row.
- Harness support (E, `harness/el_bench_src/src/models/bench_models.py`): `bench_smp` (any smp 0.5.0 decoder and encoder; MiT-B2 SegFormer builds with 1 channel in the CPU test), `bench_timm` (timm backbone + UPerNet / FPN / SegFormer head, or Unet / Unet++ through the HR stem, or DPT), PF through the `encoder.` prefix, `weighted_ce` with Pratt weight set C in `loss_factory` (E, `src_snap/el_f3/src/data/class_info.py` l.151), AdamW and poly schedule (E, train.py l.108-131, trainer l.85-107). Missing: a registry entry for small vendored model files (needed by RIFT, DSCNet, HrSegNet, SCSegamba). The old `deeplabv3plus` factory entry wraps smp under `model.` so PF refuses it (E: `deeplabv3plus.py` l.60, train.py l.118-120); suite DeepLab rows therefore go through `bench_smp`, with the wrapper's deterministic pooling swap copied in.

---

## 1. EL-specific published models

### P259 Pratt et al. 2023, BenchmarkEL (doi:10.1016/j.sasc.2023.200048)
- Claims (R, via handbook 05 3.1, full read): 593 cells, 24 classes; U-Net_12 (12.3M), U-Net_25 (25.9M), PSPNet (58.0M), DeepLabv3+ (22.4M); encoder not named; weighted CE, set C = background 0.2, ribbons 3, gridline 10, inactive 10, crack 20, others 1; headline DeepLabv3+ set C: crack median IoU 0.25, recall 0.86, defect mean 0.28; "low precision ... driven more by dilated predictions". No optimiser, lr, epochs or batch stated.
- Evidence check (E): our old-era reproduction with smp U-Net VGG16 (`configs/pratt_unet.yaml`) matched or beat the paper once the per-image median convention was aligned (handbook 05 3.1); the paper's numbers are per-image medians on a hand-picked test set.
- Code: no paper repository verified. Our harness already holds the recipe: `loss.supervised=weighted_ce`, `loss.weight_set=C` (E).
- Hypothesis for our data (S): DeepLabV3+ predicts at stride 4 and upsamples bilinearly, so crack width grows and strict IoU falls; weight set C (crack 20) raises crack recall and width further. Expected: below PF on strict crack IoU and relF1@1, near PF on relR@2, weak classes (gridline) maybe up under set C.
- Status: **BENCH_ONLY**, two rows: `dlv3p_r34_pf` (architecture under the house PF recipe; R34 as Torpey's R0 "DeepLabV3+ R34") and `pratt_dlv3p_wcec` (the paper's own loss).

### P485 Fioresi et al. 2022, UCF-EL (doi:10.1109/jphotov.2021.3131059)
- Claims (R, handbook 05 4.1): DeepLabv3 (not v3+) ResNet-50, COCO-pretrained, auxiliary loss, plain CE, lr 0.005; 224 crops; crack recall 0.82; "mIoU 57.3%" (5 classes with background). Web summaries of later papers call it a U-Net (R, web; conflicts with the full read, which the handbook verified against the PDF).
- Code: `ucf-photovoltaics/UCF-EL-Defect` (R, web; local copy E `datasets/UCF-EL-Defect/`, `ELDefectSegmentation.py`); our reproduction config `ucf_deeplab.yaml` exists (E).
- Hypothesis (S): DeepLabv3 at output stride 8 with no low-level skip is the weakest thin-structure decoder in the suite; it is the row that shows how much the decoder matters. COCO weights are replaced by ImageNet R50 (smp has no COCO encoder); Torpey's table (R, handbook 05 3.4) has COCO 0.544 against ImageNet 0.508 mIoU on their split, so the row is handicapped by about that much and says so.
- Status: **BENCH_ONLY**, rows `unet_r34_pf` (the U-Net family that both EL lines and the Hanifi paper use) and `ucf_dlv3_r50_pf`.

### P261 SegFormer for EL cell segmentation (doi:10.1109/jphotov.2024.3450009)
- Claims (R, scout record and a web listing; abstract not opened, IEEE page empty): UCF-EL, 5 classes, pixel accuracy 96.24%, mIoU 56.54%, above DeepLabv3, U-Net, DeepLabv3+, PAN, PSPNet, FPN. MiT variant: not verified. Authors: not verified (a web listing names "Mahboob et al.").
- Code: none found (WebSearch 13 Nov).
- Harness: `bench_smp decoder=segformer encoder_name=mit_b2` builds with 1 input channel (E, `test_bench_models.py` l.90-93, random init). smp 0.5.0 does not allow Unet++ with MiT (E, smp050 `unetplusplus/model.py` l.96). Weights: smp-hub `mit_b2` (public HF repo, not verified; NVIDIA SegFormer weight licence is non-commercial as far as I know, unverified).
- Hypothesis (S): first transformer row. Predicts at stride 4 (all-MLP head, x4 bilinear). Expected to lose strict crack IoU to PF, possibly gain context classes (material, frame edge).
- Status: **BENCH_ONLY**, row `segformer_mitb2_pf`.

### P444 PV-MambaSeg (doi:10.1109/tii.2026.3707683)
- Claims (R, scout): highest mIoU on two PV defect sets, 2.77M params, 0.78 GFLOPs; per-dataset numbers not retrieved.
- Code: "will be made public"; WebSearch 13 Nov found no repository.
- Status: **PARKED** (no code; a re-implementation from an abstract is more than a day; Mamba is covered by `scsegamba`).

### P448 SEiPV-Net (doi:10.3390/en16237726)
- Claims (R, abstract only): lightweight encoder-decoder on the 24-class Pratt data; custom class weights beat equal weights; beats DeepLabv3+, PSPNet, U-Net. No architecture details retrieved.
- Code: none found (WebSearch 13 Nov). Status: **PARKED** (no code; architecture unverified).

### Extra paper (outside the list): Hanifi et al. 2025, "Multi-Class Semantic Segmentation of Photovoltaic Module Defects and Features: Towards Industrial Robotic Applications" (IEA 2025; orbilu.uni.lu handle 10993/65653)
- Claims (R, repo README): 29-class EL data (the E-SCDD release), six U-Net / SegNet models with VGG16, MobileNet, ResNet50 encoders, custom class weights; VGG16-UNet best: feature mIoU 0.663, defect mIoU 0.326.
- Code: `github.com/sntubix/pv-defect-segmentation` (R, MIT; Keras, inferred from a `keras_segmentation` folder). Our P19 reproduction exists (E, PROTOCOL 7 "Hanifi 2025 VGG16-UNet ... reproduced with their code").
- Status: **BENCH_ONLY** (extra), row `hanifi_vgg16_unet_pf` = factory `smp_unet` VGG16 under PF (config only).

---

## 2. Crack specialists

### P191 RIFT (arXiv:2605.31048), full text read
- Claims (R, Table 1, 3 seeds for RIFT, single runs for reproduced baselines "under the MixerCSeg evaluation setting"): RIFT-B mIoU / F1 on DeepCrack 92.0 / 92.7, CamCrack789 86.1 / 85.2, CrackMap 82.7 / 80.0, Crack500 79.4 / 78.7; SCSegamba 90.2 / 91.1, 82.7 / 78.8, 80.9 / 76.8, 77.7 / 75.5; MixerCSeg 91.5 / 92.1, 84.1 / 82.4, 81.2 / 78.2, 78.2 / 77.6. Params / GFLOPs / training memory at 512: RIFT-B 1.69M / 3.34 / 341 MiB; RIFT-T 0.47M / 1.39; SCSegamba 2.80M / 18.16; MixerCSeg 2.54M / 2.05. Cross-dataset average mIoU (Table 6): RIFT-T 79.1, RIFT-B 77.1, SCSegamba 75.2, MixerCSeg 73.1.
- Ablations (R, Table 4, CrackMap mIoU / F1): local-only blocks 82.5 / 79.4 against full RIFT-B 83.0 / 80.3; directional + plain decoder 82.5 / 79.9. Kernel 13 best, 15 worse (Fig. 3, numbers not in text). Table 4's RIFT-B row (92.1 DeepCrack) differs from Table 1 (92.0), unexplained.
- Recipe (R): 50 epochs, lr 5e-4 to 1e-6, PolyLR power 0.9, wd 0.01, batch 1, 512 x 512, BCE + Dice at 5:1; optimiser not stated in the text read (the MixerCSeg / SCSegamba setting is AdamW).
- Evidence check (S): metrics are 2-class mIoU including background on pavement / concrete cracks whose labels are many pixels wide; no tolerance; the directional mechanism adds 0.5 mIoU over a local-only network on its own data. Nothing transfers numerically to 1 to 2 px EL labels.
- Code (R, verified): `github.com/xauat-liushipeng/RIFT`, MIT, PyTorch 2.1; `rift.py` imports only torch; stem two stride-2 convs to 1/4, four stages at strides 4 to 32 (dims 32, 64, 128, 192; depths 2, 2, 3, 2), 1 x k and k x 1 depthwise strips with a sigmoid gate, gated top-down fusion decoder at stride 4, one output channel, bilinear upsample to a fixed `out_size`; 3 input channels by default; weights on Google Drive.
- Hypothesis (S): a 1.7M-parameter scratch crack network at stride-4 output. Expected well below PF on strict crack IoU (no pretraining, stride-4 head) and on mIoU-R13 (24 classes from a 64-channel decoder); its value is as the "modern crack specialist, tiny" row and the deployment track (T4: 3.3 GFLOPs against 148 for the house model, E PROTOCOL 6).
- Status: **BENCH_ONLY**, rows `rift_b` (house recipe without PF, scratch) and `rift_b_paper` (paper optimiser and schedule).

### P354 SCSegamba (CVPR 2025; arXiv:2503.01113), method and experiments read
- Claims (R, Table 1): F1 / mIoU Crack500 0.7553 / 0.7778, DeepCrack 0.9110 / 0.9022, CrackMap 0.7678 / 0.8094, TUT 0.8390 / 0.8479; 2.80M params, 18.16 GFLOPs at 512. Recipe: AdamW 5e-4, PolyLR, wd 0.01, 50 epochs, best-val checkpoint, Dice : BCE = 1 : 5, PyTorch 1.13.1, seed 42, 7:1:2 split. No metric tolerance.
- Code (R, verified): `github.com/Karl1109/SCSegamba`, Apache-2.0. README pins torch 1.13.1+cu116, `mim install mmcv-full`, `mamba-ssm==1.2.0`. `SAVSS.py` imports `mmcv.cnn.build_norm_layer`, `mmcv.runner.base_module.ModuleList`, `mmcls` BACKBONES / BaseBackbone; `SAVSS_layer.py` calls `mamba_ssm.ops.selective_scan_interface.selective_scan_fn` once per scan direction and uses `mamba_ssm.ops.triton.layernorm.RMSNorm`. Checkpoints on Google Drive (TUT, Crack500, DeepCrack, CrackMap).
- Hypothesis (S): the Mamba row. Its structure-aware scan (two snake, two diagonal paths) is the one published idea built for thin continuous lines; output is full resolution through DySample. From scratch, 2.8M parameters, so not expected to beat PF on 425 training cells.
- Adaptation risk: the mmcv / mmcls imports are thin utilities and can be replaced by torch / timm equivalents; the selective-scan CUDA kernel must be built against torch 2.14 / cu130 in an isolated venv (approved pattern), not verified to build.
- Status: **BENCH_ONLY**, row `scsegamba`, behind gate G-MAMBA.

### P408 MixerCSeg (CVPR 2026; arXiv:2603.01361)
- Claims (R, abstract and RIFT Table 1 as an independent reproduction): 2.54M params, 2.05 GFLOPs; below RIFT-B on all four sets in RIFT's table.
- Code (R, verified): `github.com/spiderforest/MixerCSeg`, MIT, PyTorch 2.1 / cu118, `mmcv-full`, and a VMamba `selective_scan` CUDA extension built with `setup.py install`; checkpoints released.
- Status: **BENCH_ONLY**, row `mixercseg` (wave 3; after G-MAMBA and its own kernel build gate; mmcv-full with compiled ops has no wheel for torch 2.14 (DESIGN 6), so the port must strip mmcv as for SCSegamba).

### P368 CrackMamba (doi:10.1016/j.autcon.2024.105845)
- Code (R): `github.com/shengyu27/CrackMamba`; no licence on the page; built inside nnU-Net v2 with `mamba-ssm`, `causal-conv1d==1.1.1`, torch 2.0.1; ImageNet VMambaV2 encoder; weights on Google Drive.
- Status: **PARKED** (no licence; nnU-Net + two CUDA packages; Mamba covered by `scsegamba`; nnU-Net row owned by T6).

### P446 HrSegNet (doi:10.1016/j.autcon.2023.105112)
- Claims (R, scout and README): CrackSeg9k mIoU 80.56 (B48), B16 78.43 at 182 FPS.
- Code (R, verified): `github.com/CHDyshli/HrSegNet4CrackSegmentation`, Apache-2.0, PaddlePaddle 2.4.1 + PaddleSeg 2.7. `hrsegnet_b48.py` is about 210 lines: two stride-2 stems to 1/4, a 1/4 high-resolution path of three SegBlocks, per-block semantic branches at 1/8 to 1/32 added back by bilinear upsampling, a transposed-conv head to 1/2, two training-only auxiliary heads; only standard layers. Port: Conv2D, BatchNorm2D (momentum complement: Paddle 0.9 = torch 0.1), AvgPool2D, bilinear `align_corners=True`.
- Hypothesis (S): the crack network with the highest output resolution of the suite (stride 2 head) without a pretrained encoder; tests whether a high-resolution path alone, from scratch, matches an ImageNet encoder on 425 cells.
- Status: **BENCH_ONLY**, row `hrsegnet_b48` (PyTorch port, about 3.5 h).

### P329 Hybrid-Segmentor (doi:10.1016/j.autcon.2024.105960)
- Claims (R, scout): F1 0.774, IoU 0.631 on their merged CrackVision12K set.
- Code (R, verified): MIT, PyTorch Lightning 2.4 / torch 2.5; weights on OneDrive (best and ablations); the README does not name the CNN and transformer backbones. Data licence non-commercial.
- Status: **BENCH_ONLY**, row `hybrid_segmentor` (wave 3, lowest priority of the coded crack rows).

### P139 CoANet (doi:10.1109/tip.2021.3117076)
- Code (R): GPL-3.0 plus "non-commercial research only"; PyTorch >= 1.2; connectivity cubes precomputed. Status: **PARKED** (licence for a startup-linked benchmark, old stack; strip-direction context covered by `rift_b`; connectivity outputs need the aux hook).

---

## 3. Thin-structure and high-resolution general architectures

### P104 DSCNet (ICCV 2023)
- Claims (R, scout full text): DRIVE Dice 82.06, clDice 82.07; Massachusetts Roads at most +1.31 Dice over U-Net.
- Code (R, verified here and by T5): MIT, PyTorch. `S3_DSCNet.py`: 4-level U-shape, base width 16, three max-pools, 14 DSConv (x and y) branches beside standard convs at every stage, concatenated and fused; sigmoid output. `S0_Main.py`: 400 epochs, lr 1e-4, batch 1, 224 crops, kernel 9, 1 input channel.
- Hypothesis (S): snake kernels at full resolution follow long cracks; 76 to 88% of our crack components are under 20 px (BRIEF 2), so little to gain; memory at 512 px batch 8 is the main risk (deformable sampling at full resolution, 14 branches).
- Status: **BENCH_ONLY**, row `dscnet_2d`.

### P361 HRNet (TPAMI 2020)
- Code: `github.com/HRNet` org (scout); in timm as `hrnet_w18` (S: timm 1.0.30 ships HRNet; whether its `features_only` reductions are (2, 4, 8, 16, 32), which smp's Unet++ needs, is unverified).
- Hypothesis (S): keeps the house decoder and changes only the encoder to one that holds a stride-4 stream at every depth. The only CNN-classic row where crack detail is not lost by design, so the one most likely to beat PF among the classics.
- Status: **BENCH_ONLY** (flagged as a possible beater), row `hrnet_w18_unetpp_pf`, behind a CPU build gate.

### P198 BiRefNet: **PARKED** (cost). MIT, PyTorch; default Swin-L at 1024 px, "36.5G+" per GPU for training, binary DIS (R, README).

---

## 4. Protocol papers

- **P596 Pitfalls of topology-aware segmentation (IPMI 2025):** connectivity choice, GT topological artefacts and metric misuse change rankings (R, abstract via scout). PROTOCOL: the scorer fixes 8-connectivity for crack components and lists GT fragments under 3 px per source; Betti or component numbers only beside overlap and relF1@2.
- **P605 Auditing connectivity claims (Zenodo 2026):** per-paper scorecards, multi-seed files, two-annotator adjudication (R, artefact description). PROTOCOL: each suite row gets an audit line (code commit, weights, seeds, deviations from the paper recipe).
- **P500 Conformal segmentation (Mathematics 2025):** conformal risk control sets a pixel threshold with a bounded expected miss rate (R, abstract). PROTOCOL: a secondary operating point "OP-C": crack bias cross-fitted on 4 folds for expected relR@2 >= 0.90; report relP@2 at that point. Not a pass criterion.
- **P606 Inspect Any Crack (arXiv 2026):** severity index from width and area (R, abstract). PROTOCOL: template for the light post-evaluation track only (length and inactive fraction; width is not observable on EL).

---

## 5. Parked papers in one line each
See `ledger/T11.tsv` for the reason of each of the 34 PARKED papers. Summary: 13 are modules for raising scores whose mechanism a named arm of T2, T5, T6, T7, T8 or T10 already tests (P093, P096, P101, P131, P168, P207, P212, P218, P221, P244, P285, P299, P318); 9 have no code and are covered by a suite row (P148, P251, P256, P350, P437, P444, P448, P474, P531); the rest are cost or lower prior (P072, P139, P171, P176, P198, P226, P366, P368, P374, P469, P472, P475).
