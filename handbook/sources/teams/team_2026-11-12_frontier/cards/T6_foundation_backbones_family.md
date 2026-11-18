# T6 family cards: foundation and transformer backbones, PEFT, modern decoders, auto-configured pipelines (13 Nov 2026)

Analyst T6. R = from the paper (read through the Research MCP or a fetched page; "scout" = only the scout record in `cards/in2/<pid>.json`), E = from our files, S = my judgement. Cards for every RUN_NOW, RUN_AFTER_GATE and BENCH_ONLY paper and every paper read in full. All 76 statuses: `ledger/T6.tsv`. Arms: `T6_foundation_backbones_spec.md`.

Read in full this session (6): P002 SAM2-UNet, P089 thin-vessel SAM study, P195 DINOv3 v ImageNet industrial, P043 Dino U-Net, P069 Rein, P030 VFM domain generalisation. Fetched pages: HF model cards of `timm/sam2_hiera_base_plus.fb_r896`, `.fb_r896_2pt1`, `timm/sam2_hiera_large.fb_r1024_2pt1`, `timm/vit_large_patch14_reg4_dinov2.lvd142m`, `timm/vit_large_patch16_dinov3.lvd1689m`, `facebook/sam3`; the SAM2-UNet GitHub README and `SAM2UNet.py`.

**Family-level reading (S).** Three facts drive the arms. (1) Every foundation result we have is either frozen (probes) or tiny and short (A8: ConvNeXt-T, 4k steps, F51 AP). Papers that report a gain from large encoders do so with full schedules and larger models (SAM2-UNet size ablation; P195's gain appears only after long full fine-tuning). (2) The consistent, large effect in the literature is out-of-domain, not in-domain: P030 (ID about equal, DG +8 to +29 Dice), Rein (frozen / PEFT > full FT on unseen domains), U-Bench (in-domain top-1 1 to 2% IoU, zero-shot over 3%, scout). That points to unseen modules and to inactive (region-level), not to strict crack IoU. (3) For 1 to 2 px lines, plain ViTs at patch 14 / 16 need either 2x upscaled input (P089) or a high-resolution conv path; a hierarchical encoder with a stride-4 stage (Hiera) or a CNN detail path (arm 2) avoids the 4x compute.

---

## P002 SAM2-UNet: Segment Anything 2 Makes Strong Encoder for Natural and Medical Image Segmentation
- arXiv:2408.08870 (Visual Intelligence 2026, doi:10.1007/s44267-025-00106-w). Code: https://github.com/WZH0120/SAM2-UNet, Apache-2.0, PyTorch (README verified; `SAM2UNet.py` read via fetch).
- R: SAM 2 Hiera encoder frozen; one adapter per Hiera block (`Linear(d,32)-GELU-Linear(32,d)-GELU`, output added to the block input); four RFB blocks to 64 channels; three U-Net decoder blocks; output at stride 4 (head upsampled 4x); deep supervision; weighted IoU + BCE; AdamW 1e-3 cosine; 352 px, batch 12, 20 to 50 epochs; flips only. Best on 18 natural / medical sets (camouflage, salient, marine, mirror, polyp). Size ablation COD10K S-alpha: Hiera-T 0.822, S 0.839, B+ 0.853, L 0.880. README: use SAM 2.0 weights, not 2.1.
- Evidence check: no thin-structure set; binary tasks; no comparison with an ImageNet CNN of equal size. Independent replication: Dino U-Net's table (P043) runs SAM2-UNet in the nnU-Net pipeline on 7 medical sets: mean Dice 74.56 v UNet++ 73.42, v nnU-Net 71.45.
- Hypothesis for EL (S): Hiera's stride-4 stage + our HR stem keep the crack path; the larger pretrained encoder helps region classes and unseen modules. Our only Hiera read was the frozen Hiera-T probe (E: F51 crack AP 0.198), the weakest size, which says nothing about fine-tuned B+ / L.
- Status: **RUN_NOW** (arm 1 `hiera_bp_unetpp_pf`, config only); arm 4 `hiera_bp_adapter_frozen` is its faithful PEFT form, RUN_AFTER_GATE.

## P089 Evaluating SAM-based and Convolutional Architectures in Thin Retinal Vessel Segmentation
- arXiv:2611.00396 (2026). Code: none found.
- R: MedSAM (plain ViT-B, patch 16, 1024 input, fine-tuned) v LiteMedSAM v three CNNs trained from scratch, 100-trial HPO per configuration, DRIVE / HRF / FIVES / VessMap. Thin-vessel centreline recall of fine-tuned MedSAM within -0.6 to +2.5 pp of the best CNN, never significantly different. Pre-training raised MedSAM thin recall by 17.6 (DRIVE) and 12.4 (VessMap) points. Inference with padding instead of upscaling to 1024 cut thin recall by 17.9 and 41.3 points.
- Evidence check (S): the CNNs had no ImageNet weights, so "ViT = CNN" is "pretrained ViT = scratch CNN"; the padding test changes the scale seen at test time, so part of the drop is a train / test scale mismatch. It does not show that ViTs beat a pretrained CNN.
- Use: design rule for plain-ViT rows (EoMT, DPT): 2x upscaled input. Hiera (arm 1) and the arm-2 branch do not need it.
- Status: **PARKED** (evidence only; applied as a rule).

## P195 Rethinking Transfer Learning for Industrial Inspection: DINOv3 v ImageNet Pretraining Across RGB and X-ray Tasks
- arXiv:2605.23472 (2026). Code: none found. Detectron2, Mask2Former head.
- R: Severstal (steel, RGB) frozen ConvNeXt-T IN 62.04 v DINOv3 62.40 mIoU; full fine-tune DINOv3 ConvNeXt-T +10.29 over IN ConvNeXt-T, +10.59 over R50, with the default Mask2Former schedule (learning curve to about 250k iterations). Rubber rings: frozen IN 73.25 v DINOv3 72.32. GDXray (greyscale X-ray, detection): frozen IN 21.32 v DINOv3 7.88 AP50; fine-tuned IN 29.74 v DINOv3 27.84.
- Evidence check (S): exactly the A8 contrast, but full fine-tune and a long schedule, where A8 was PF and 4k steps (E). EL is greyscale; the only greyscale result here is negative for DINOv3.
- Status: **PARKED** (lower prior than arm 1; zero-build card `dinov3_cnxt_t_unetpp_fullft` in spec section 6, idle GPUs only).

## P043 Dino U-Net: Exploiting High-Fidelity Dense Features from Foundation Models for Medical Image Segmentation
- arXiv:2508.20909 (LNCS 2026). Code: https://github.com/yifangao112/DinoUNet (scout record; not verified, licence unknown).
- R: frozen DINOv3 + DINO Adapter (spatial-prior conv branch + semantic branch, deformable cross-attention fusion, stride 4 to 32 maps) + Fidelity-Aware Projection + U-Net decoder; nnU-Net preprocessing / augmentation, Adam 1e-3 poly, 200 x 250 iterations, Dice + CE. Mean Dice over 7 sets (25 to 1,044 cases): nnU-Net 71.45, UNet++ 73.42, SAM2-UNet 74.56, Dino U-Net S 75.77, B 75.83, L 76.04, 7B 76.43. FAPM ablation +0.56 to +0.79 Dice.
- Evidence check (S): random 8:2 splits, one run per cell (no seeds stated); S to L adds 0.27 Dice, so size is not where the gain is; the spatial branch is.
- Hypothesis for EL: the high-resolution path must be a CNN, the VFM adds semantics. Arm 2 takes that design with the house R34 as the spatial branch and a one-way zero-initialised fusion.
- Status: **RUN_AFTER_GATE** (arm 2; gate = CPU inactive error-anatomy pre-check).

## P069 Rein: Stronger, Fewer, & Superior: Harnessing Vision Foundation Models for Domain Generalized Semantic Segmentation
- arXiv:2312.04265, doi:10.1109/cvpr52733.2024.02704 (CVPR 2024). Code: https://github.com/w1oves/Rein (scout record; licence unverified; MMSeg-based, S).
- R: per-layer learnable tokens (m = 100, rank 16, layer-shared MLPs, about 3M params) refine features of a frozen VFM; Mask2Former head; AdamW 1e-5 backbone / 1e-4 head; 40k iterations, batch 4, 512 crops. Citys to BDD + Map: DINOv2-L frozen 66.7, Rein 68.7. Full FT v Rein: DINOv2-B 56.7 v 59.1, DINOv2-S 51.8 v 55.7, ConvNeXt-L 52.2 v 55.5, R50 38.9 v 46.6. Authors: full fine-tuning loses pre-training knowledge (consistent with our PF finding, E).
- Evidence check (S): urban scenes, synthetic-to-real; no thin structures; gains are on unseen domains.
- Status: **RUN_AFTER_GATE** (arm 2 follow-up `model.vfm.tuning=rein`, only if arm 2 promotes or moves F51).

## P030 Do Vision Foundation Models Enhance Domain Generalization in Medical Image Segmentation?
- arXiv:2409.07960, doi:10.1007/978-3-031-91672-4_12 (LNCS 2025). Code: https://github.com/kerem-cekmeceli/Foundation-Models-for-Medical-Imagery (stated in the abstract; licence unverified).
- R: greyscale MRI / CT, 10 to 198 training volumes. Frozen or PEFT FMs (DINOv2, SAM, MedSAM, MAE) + HQHSAM decoder v full-FT Vanilla UNet, Res101-UNet (ImageNet), Swin-UNet. DINOv2-L Rein-LoRA DG Dice: healthy brain 54.09 v 43.99 (Res101-UNet), lumbar spine 31.30 v 2.35, prostate 42.74 v 31.46, tumour 50.84 v 31.48; ID roughly equal (e.g. healthy brain 84.61 v 86.07). PEFT on DINOv2-B: Freeze ID 80.72 / DG 41.77; Rein-LoRA 82.08 / 44.44; Ladder 84.95 / 33.53. Larger FMs: little ID change, slightly better DG. UNet decoder on FMs 79.10 ID v HQHSAM 84.98 (decoder matters).
- Evidence check (S): DG = new scanner and protocol, a larger shift than our unseen modules of seen sources; closer to E1 (new layout and scuff). The ImageNet CNN baseline was fully fine-tuned, not PF.
- Hypothesis for EL: keeping a large VFM frozen gives the decoder features that do not overfit 478 cells. Arm 2.
- Status: **RUN_AFTER_GATE** (arm 2).

## P145 DINOv3-PEFT: Dual-Branch Collaborative Network with PEFT for Road Segmentation in SAR
- doi:10.3390/rs18070973 (Remote Sensing 2026). Code: none found.
- R (scout, abstract fragment): PEFT DINOv3 branch for context + a detail branch, fused, for thin roads in speckled greyscale SAR. Numbers not read.
- Status: **RUN_AFTER_GATE** (arm 2 design support; closest domain match: thin lines in non-natural greyscale).

## P190 DINOv3
- arXiv:2508.10104 (2025). Weights: `timm/vit_large_patch16_dinov3.lvd1689m` (303.1M; licence "dinov3-license", HF page checked 13 Nov; treated as gated: user's OK needed, as the house already did for ConvNeXt-T / ViT-S, E).
- R (scout): Gram anchoring keeps dense features clean at scale; distilled ViT S to H+ and ConvNeXt T to L.
- Evidence check (E): A8 (DINOv3 ConvNeXt-T, PF, 4k) KILL; probes: DINOv3 ViT-S/16 F51 AP 0.147 at 512, 0.212 at 1024.
- Status: **RUN_AFTER_GATE** (arm 2 backbone swap; gate = arm 2 sign + user's OK).

## P092 Fracture-Informed CNN-Transformer Ensemble for Multiclass PV Defect Segmentation in EL Images
- doi:10.1109/infinitys69204.2026.11666283 (IEEE INFINITYS 2026). Code: none found.
- R (scout): SegFormer-B0 + edge-guided residual refiner soft-fused with a U-Net++ (0.55 / 0.45); ensemble mIoU 0.840 on a 5-class EL set (dataset unverified); paired bootstrap.
- Hypothesis (S): heterogeneous members err differently from same-architecture seeds, so a PF + Hiera pair may beat a PF + PF pair at equal cost.
- Status: **RUN_AFTER_GATE** (readout 1b of arm 1, CPU on logp dumps; gate = arm 1 dumps exist).

## P006 nnU-Net: a self-configuring method for deep learning-based biomedical image segmentation
- doi:10.1038/s41592-020-01008-z (Nature Methods 2020). Code: https://github.com/MIC-DKFZ/nnUNet (Apache-2.0, unverified this session).
- R (scout): fingerprint-based configuration + fixed recipe: 1000 x 250 iterations, SGD 0.01 Nesterov 0.99 poly, CE + Dice, deep supervision, foreground oversampling, heavy augmentation; 5-fold models.
- Evidence check (S): from scratch (no ImageNet), default augmentation rescales 1 to 2 px labels. The project never varied schedule length, deep supervision or oversampling (E, BRIEF 5).
- Status: **RUN_AFTER_GATE** (arm 3; gate = harness nnU-Net adapter + step-matched fold-0 pathfinder). Also the benchmark's auto-configured baseline row.

## P020 nnU-Net Revisited: A Call for Rigorous Validation in 3D Medical Image Segmentation
- doi:10.1007/978-3-031-72114-4_47 (MICCAI 2024). Code: nnUNet repo (ResEnc presets).
- R (scout): KiTS Dice 86.04 org, 86.79 ResEnc M, 88.17 L, 88.67 XL; MedNeXt best on 5 of 6; transformers below original nnU-Net; U-Mamba equals its No-Mamba control. Validation rules: equal compute, 5-fold CV, keep only datasets where inter-method SD exceeds intra-method SD.
- Status: **RUN_AFTER_GATE** (arm 3 preset ResEnc-L) and a PROTOCOL source (the SD-ratio rule for choosing headline metrics; run it on the W1 A/A null).

## P087 Omni-Crack30k
- doi:10.1109/cvprw63382.2024.00392 (CVPRW 2024). Code: none found.
- R (scout): 30k crack images from 20+ sets; nnU-Net mean clIoU@4px 64%, at least 10 points above other approaches; strict IoU favours wide cracks.
- Status: **PROTOCOL** (add centreline IoU at 2 px beside relF1@2) and evidence for arm 3.

## BENCH_ONLY rows (one paragraph each; all scout records unless stated)
- **P187 Mask2Former** (arXiv:2112.01527, CVPR 2022): masked-attention mask classification over a multi-scale pixel decoder. Authors state weak small objects. Row via the planned HF wrapper (DESIGN step 13), semantic mode, judged on inactive and region classes, with a dense per-pixel CE + Dice aux head for crack (P159 pattern). Code: official repo (scout says none found; HF `transformers` port, version unverified).
- **P067 EoMT** (doi:10.1109/cvpr52734.2025.02356): plain ViT with queries in the last blocks; R (scout): COCO PQ gap to ViT-Adapter + M2F -1.1 at ViT-L, ADE20K 58.4 mIoU at 512 (DINOv2-L). P502 (R, scout): EoMT-DINOv3 crack mask mAP 4.7. Row at 2x input (P089 rule) with a full-res per-pixel crack head. Code https://github.com/tue-mps/eomt (licence unverified).
- **P260 SegFormer** (arXiv:2105.15203): MiT encoder + all-MLP decoder, stride 4. Config only in the harness (`bench_smp`, `decoder=segformer`, `encoder_name=mit_b2`); smp 1-channel support for mit encoders unverified; SegFormer weight licence possibly non-commercial (unverified), which matters for WattCycle. Heterogeneous-ensemble member.
- **P103 MedNeXt** (doi:10.1007/978-3-031-43901-8_39): ConvNeXt-block U-Net with UpKern; R (scout via P020): best on 5 of 6 3D sets. 2D row inside the nnU-Net adapter after arm 3.
- **P135 Swin-UMamba** (doi:10.1007/978-3-031-72114-4_59): ImageNet-pretrained VMamba encoder + U-Net; needs `mamba_ssm` built for cu130 (high risk, DESIGN 6). Row only if the isolated venv builds. Code https://github.com/JiarunLiu/Swin-UMamba.
- **P407 U-Mamba** (arXiv:2401.04722): run Bot only, always with its No-Mamba control (R, P020: the control matched it on 6 3D sets). Inside the nnU-Net adapter.
- **P544 TransUNet** (arXiv:2102.04306): R50 + ViT-B/16 hybrid; suite row with PF. Low prior (P020: transformers below nnU-Net).
- **P192 RWKV-UNet** (arXiv:2501.08458): conv + RWKV linear attention; U-Bench top-1 in-domain and zero-shot (scout). Code https://github.com/juntaoJianggavin/RWKV-UNet (licence unverified).
- **P194 nnWNet** (doi:10.1109/cvpr52734.2025.01942): transformer + conv streams kept across resolutions, nnU-Net trainer; claims SOTA on DRIVE and CREMI (thin structures). Inside the nnU-Net adapter after arm 3.
- **P547 SegDINO** (arXiv:2509.00833): frozen DINOv3 multi-level features + light MLP head. Reference row with public DINOv2-L (`frozen_dinov2l_dpt`, spec section 6); not the closed ViT-S linear probe (multi-level, ViT-L).
- **P550 U-KAN** (doi:10.1609/aaai.v39i5.32491): efficiency row for the deployment axis. Code https://github.com/CUHK-AIM-Group/U-KAN.

## Weights and licences used by the arms (checked 13 Nov unless marked)
| File | Size | Licence | Gated | Used by |
|---|---|---|---|---|
| `timm/sam2_hiera_base_plus.fb_r896` (SAM 2.0 encoder) | 68.7M | Apache-2.0 | no | arms 1, 4 |
| `timm/sam2_hiera_large.fb_r1024` (SAM 2.0; page checked was `_2pt1`) | about 0.2B | Apache-2.0 | no | arm 1 cost smoke |
| `timm/vit_large_patch14_reg4_dinov2.lvd142m` | 304.4M | Apache-2.0 | no | arm 2 |
| `timm/vit_large_patch16_dinov3.lvd1689m` | 303.1M | DINOv3 licence | yes (user's OK) | arm 2 follow-up only |
| `facebook/sam3` | n.a. | "other" | yes (HF access request) | parked (P041, P175, P273, P383) |
| none (from scratch) | | nnU-Net Apache-2.0 (unverified) | no | arm 3 |
