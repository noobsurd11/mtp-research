# T6 spec: foundation and transformer backbones, PEFT, modern decoders, auto-configured pipelines (13 Nov 2026)

Analyst T6. Tags: R = from the paper (read through the Research MCP or a fetched page), E = from our files, S = my judgement. Nothing here was run. No server, no GPU, no sealed set touched. Paper cards: `T6_foundation_backbones_family.md`. Ledger: `ledger/T6.tsv` (76 papers).

## 0. Common frame and what is different from waves 1 and 2

- Baseline: card `house_r34_unetpp_pf_v11` (E). Screen: cv5v2, folds 0 to 4, seeds 5 and 6, OOF pooled, two-stage bootstrap (330 groups, then seeds), pass = delta >= M (M = max(0.01, 2 x SE of the A/A PF {5,6} v {7,8} contrast)) and CI above 0; a pass only promotes to seeds 7 to 9. Operating points from `crossfit_op` (OP-A primary, OP-F, OP-W); a crack gain counts only at OP-A and OP-W. Every arm reports the WAVE2_REVIEW section 5 guards (1 to 12).
- Machines (E, LEAD_INSTRUCTIONS 13 Nov): pathfinders and smokes on gaint against W1-G PF (same machine); screens on cv02 against W1-C1 PF.
- F51 reads (unseen-module development) follow X9: paired over the 10 fold x seed models, logged in the read ledger, promotion only. They need F51 dumps of the 10 W1-C1 PF baseline runs (seeds 5, 6): one `bench_infer --set f51` per checkpoint (about 1 GPU-min each, E: dump of 107 cells took 59 to 94 s). This job is shared by arms 1, 2 and 4.
- **No existing arm overlaps** (E, WAVE2_REVIEW 2 and 4): all 29 wave-2 arms keep the ResNet-34 U-Net++. The three W1c config-only pathfinders (UPerNet + ConvNeXt-T IN-1k, HR-stem U-Net++ + ConvNeXt-T IN-1k, DeepLabV3+ R34) are architecture rows with ImageNet-1k weights; none tests a foundation-pretrained encoder, a frozen encoder, PEFT, a VFM context branch, or nnU-Net. The HR-stem ConvNeXt-T row is the wrapper control for arm 1 (same decoder and stem, different backbone).
- **BRIEF 5 rows these arms do not repeat (E):** frozen linear probes (DINOv3 ViT-S, ConvNeXt-T, DINOv2-S, SAM2 Hiera-T; P8 probe: Hiera-T F51 crack AP 0.198, DINOv2-S 0.173); A8 = DINOv3 ConvNeXt-T v IN-1k ConvNeXt-T under PF, 2 seeds, **4k steps**, judged on F51 crack AP (76% one cell), KILL = "no sign of a gain"; ResNet-50 U-Net++ worse on inactive. None used a model above 30M encoder parameters, a full 20k schedule with a foundation encoder, CV5-G, a frozen encoder with adapters, or a VFM fused into the house model.

## Priority table

| # | Arm | Papers | Problem | Primary (OP-A, CV pooled OOF) | Route | Build h | GPU-h (pathfinder + screen) | Pre-check | Priority |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `hiera_bp_unetpp_pf` | P002 (+P092 readout) | unseen_modules | mIoU-R13 | config_only | 1.5 (+1.5 for the CPU ensemble readout) | 4 + 24 | none | 80 |
| 2 | `vfm_ctx_r34_pf` | P030, P043, P145 (+P069, P190 follow-ups) | inactive | inactive IoU | new_model_code | 5 (+1.5 pre-check) | 2.5 + 19 | inactive error anatomy (CPU, W1-G dumps) | 65 |
| 3 | `nnunet_resenc_2d` | P006, P020, P087 | benchmark_row | crack relF1@2 | external_codebase | 9 (8 = DESIGN step 12, already planned) | 2 + 15 | none | 55 |
| 4 | `hiera_bp_adapter_frozen` | P002 (+P048) | unseen_modules | mIoU-R13 | new_model_code | 2.5 | 2.5 + 20 | gated on arm 1's encoder-drift log | 40 |

Order of work (S): arm 1 card + weights + smokes (1.5 h) today; the arm 2 pre-check (CPU, 1.5 h) as soon as the W1-G dumps exist; arm 2 code only if the pre-check opens it; arm 3 when the harness builds the nnU-Net adapter; arm 4 only through its gate.

---

## Arm 1. `hiera_bp_unetpp_pf`: SAM2 Hiera-B+ encoder in the house U-Net++ under PF

**Hypothesis.** A hierarchical foundation encoder (SAM 2 Hiera-B+, 69M parameters, stride-4 first stage) fine-tuned with PF for the full 20k steps carries more context and better transfer to unseen modules than ImageNet ResNet-34, while the HR stem and the U-Net++ decoder keep the 1 to 2 px crack path.

**Evidence.**
- R (SAM2-UNet, arXiv 2408.08870, full text): frozen Hiera + adapters + U-Net decoder beats task specialists on 18 sets; backbone ablation COD10K S-alpha Hiera-T 0.822, S 0.839, B+ 0.853, L 0.880. Our only Hiera read is the frozen Hiera-T linear probe (E), the weakest size.
- R (Dino U-Net, arXiv 2508.20909, full text, nnU-Net pipeline, 7 medical sets with 25 to 1,044 cases): mean Dice UNet++ 73.42, SAM2-UNet 74.56, nnU-Net 71.45. On MyoPS20 (25 cases) SAM2-UNet 74.07 v UNet++ 67.42. Whether their UNet++ used ImageNet weights is not stated (unverified).
- R (P497 abstract): linear probing does not predict fine-tune ranking, so the probe null does not close this.
- S: the house PF finding (E: encoder preservation moved E1 inactive 0.05 to 0.24) is the reason to keep PF rather than the house fine-tune.

**Exact change (config only; uses `bench_timm` + HR stem from f8, `training.encoder_pf`).** Card `bench/methods/hiera_bp_unetpp_pf_v11.yaml` = `house_r34_unetpp_pf_v11` opts with `model.name=smp_unetpp` replaced by:
```
- model.name=bench_timm
- model.decoder=unetplusplus
- model.backbone=sam2_hiera_base_plus
- model.backbone_weights=/home/noob/work/weights/sam2_hiera_base_plus.fb_r896/model.safetensors
- model.backbone_weights_format=timm
- model.backbone_drop_path=0.0
- model.hr_stem_channels=64
```
Everything else unchanged (PF freeze 1000, ramp 1000, lr_mult 0.1, encoder wd 0; Adam 1e-3, 20k steps, batch 8, 512 px, ce_dice, labelsafe, v1.1 masks, final weights, argmax). `family: sam2-hiera-unetpp`, `papers: [arXiv:2408.08870]`, `diff_ref: house_r34_unetpp_pf_v11`. Weights md5 into the card after download.
- Add the encoder probe from builder x1 (`src/trainers/enc_probe.py`, log-only) with Hiera stage boundaries. Hiera-B+ stage depths are (2, 3, 16, 3) so stages = blocks 0-1, 2-4, 5-20, 21-23 (S: depths from SAM 2's config; verify with `len(m.blocks)` = 24 and the channel change at each stage start). If enc_probe groups parameters by top-level child, add a `stage_map` argument; log cos-to-init per stage every 2k steps.
- Unit test (CPU, `tests/test_bench_models.py`): build the card's model with `backbone_weights=null`, input (2, 1, 512, 512), output (2, 24, 512, 512); `forward_intermediates` channels (112, 224, 448, 896) (S, verify); every backbone parameter name starts with `encoder.`; the HR stem and decoder are outside `encoder.`; PF builds two groups; 1-channel patch embed has in_chans 1 after loading the file (timm RGB sum, E: works for Hiera-T in A8's wrapper).

**CPU pre-check.** None decides anything (P497: frozen features do not predict fine-tuning). A CPU build + forward test only.

**Pathfinder (gaint, against W1-G PF fold 0 seed 5).**
1. Smoke `smoke_hiera_bp_f0_s5`: 1,000 steps (`--exit_after_step 1000`), 1 s memory log: peak MiB and steps/s. Gate = peak + 2,048.
2. Smoke `smoke_hiera_l_f0_s5`: same card with `model.backbone=sam2_hiera_large` and the Hiera-L file, 1,000 steps: cost only (peak, steps/s), never trained further this week.
3. Full fold-0 run `pf_hiera_bp_f0_s5`, 20k steps, dump fold 0 in fp32 with `--logp`; also dump F51.
Failure gates (catch failures only, never a ranking): final train loss finite and <= 1.5 x W1-G PF f0 s5's at step 20k; fold-0 OP-A crack relF1@2 >= PF fold-0 minus 0.10 and width ratio in 0.7 to 1.4 x PF; inactive and mIoU-R13 not NaN; peak <= 40 GB (A6000) and step time <= 3 x house. On failure: one retry with `training.encoder_pf.lr_mult=0.05`, then drop. Record the stage-3 and stage-4 cos-to-init at 20k (it is arm 4's gate).

**Screen (cv02).** 10 runs (folds 0 to 4, seeds 5, 6) v W1-C1 PF seeds 5, 6, A/A from PF 7, 8. Dumps fold + F51 (logp on the held-out fold).
- Primary: mIoU-R13 at OP-A. Everything in WAVE2_REVIEW 5 as guards, plus per-class IoU of gridline, splice, edge_dark, material, inactive.
- Second pre-declared look (X9, promotion only): F51 crack relF1@2 and F51 inactive IoU paired over the 10 models.
- **Readout 1b (P092, CPU, 0 GPU-h, 1.5 build h): heterogeneous ensemble.** Per fold and seed s: mean of log-softmax of `pf_s` and `hiera_s` v the homogeneous PF pair (`pf_5` + `pf_6`), both from logp dumps, argmax. Primary for this readout: strict crack IoU at OP-W (the only clear win so far was the 5-seed homogeneous ensemble, +0.014 to +0.018 crack IoU on test, E). Guard: width ratio (ensembles are about 13% wider, E WAVE2_REVIEW). If T2's G5 job already averages logp dumps, reuse it.

**What it should move.** S from R: mIoU-R13 +0.005 to +0.02 (SAM2-UNet over UNet++ +1.1 Dice mean; U-Bench: in-domain top-1 gains 1 to 2% IoU, zero-shot over 3%); crack relF1@2 within +/-0.01 (label-limited); inactive uncertain in sign (ResNet-50 was worse, E). F51 is where a gain should be largest if the transfer claim holds.
**Drop rule.** No promotion unless mIoU-R13 delta >= M with CI above 0, or the F51 look passes (X9 promotion). Drop outright if crack relF1@2 at OP-A or OP-W or inactive IoU falls by more than M, or crack-free false alarms rise by more than 25%. A null closes Hiera-B+ under PF at 512 px only; it does not close Hiera-L, frozen + adapters (arm 4) or SAM3.

**Cost.** Build 1.5 h (card, download, md5, test, enc_probe stage map) + 1.5 h readout 1b. GPU: smokes 0.6, fold-0 run about 2.5 (S: 1.8 to 2.5 x house step time from Hiera-B+ 69M params at 128x128 stage-1 tokens; measured by the smoke), screen 10 x about 2.4 = 24 GPU-h. Over the 11 to 25 window only if the smoke shows > 2.3 x house step time; then the lead decides.

**Needs.** No package (timm 1.0.30 has SAM 2 Hiera, E DESIGN 1.10). Weights: `timm/sam2_hiera_base_plus.fb_r896` (SAM 2.0 encoder only, 68.7M, Apache-2.0, not gated; HF page checked 13 Nov), and for the cost smoke `timm/sam2_hiera_large.fb_r1024` (Apache-2.0, not gated; the page I checked was the `fb_r1024_2pt1` variant, 0.2B params; the plain `fb_r1024` tag is unverified, check with `timm.list_pretrained('sam2_hiera*')` on gaint). SAM 2.0 rather than 2.1 because the SAM2-UNet README says to use the original SAM 2 weights (reason in its issues 18 and 30, not read). Download on gaint with HF online once, then `HF_HUB_OFFLINE=1` as the queue sets.

**Risks and how it could mislead.**
- Confound: two things change (backbone and HR-stem decoder). Attribution needs the W1c HR-stem ConvNeXt-T row; if both pass, the wrapper is the cause.
- PF at 1e-4 Adam on a 69M transformer without layer-wise decay may wash out pretrained features (the house fine-tune erased R34 layer3 / 4, E). The enc_probe log shows it; arm 4 is the answer if it happens.
- Wider crack predictions from a stride-4 backbone would raise relR@2 for free: the width guard (0.85 to 1.15 x PF, pooled and per source) and OP-W apply.
- 2 seeds on mIoU-R13: power unknown until the A/A null exists; a null at 2 seeds is weak.
- Machine: the pathfinder is gaint v W1-G; the screen is cv02 v W1-C1. Never mix (X10).

---

## Arm 2. `vfm_ctx_r34_pf`: frozen DINOv2 ViT-L context branch fused into the house PF U-Net++

**Hypothesis.** Inactive misses and false alarms are region-level decisions (is this dark area a disconnected region or a dark material / edge / BMRK contrast artefact?) that need cell-scale context and robust semantics; a frozen ViT-L (no overfitting on 478 cells, pretrained features preserved by construction) fused at stride 8 to 32 supplies them, while the house ResNet-34 keeps every stride-2 and stride-4 path for 1 to 2 px cracks.

**Evidence.**
- R (P030, arXiv 2409.07960, full text): frozen or PEFT VFMs with a decoder match full-FT U-Nets in-domain and beat them on unseen scanners: DINOv2-L + Rein-LoRA DG Dice lumbar spine 31.30 v 2.35 (Res101-UNet, full FT), prostate 42.74 v 31.46, brain tumour 50.84 v 31.48, healthy brain 54.09 v 43.99; training sets of 10 to 198 volumes, greyscale MRI / CT. Table 3: Freeze v Rein-LoRA on DINOv2-B: DG 41.77 v 44.44, ID 80.72 v 82.08.
- R (Dino U-Net, full text): frozen DINOv3 + a conv spatial branch + U-Net decoder: mean Dice S 75.77, L 76.04 v UNet++ 73.42; size S to L adds only 0.27.
- R (Rein, arXiv 2312.04265, full text): DINOv2-L frozen 66.7, Rein 68.7 mIoU (Citys to BDD + Map); DINOv2-B full FT 56.7 v Rein 59.1: full fine-tuning loses transfer.
- R (P145 abstract only): PEFT DINOv3 branch + detail branch for thin roads in greyscale SAR.
- E: P4 probe found DINOv2-S on par with ImageNet R50 for inactive (AP 0.384) and weak for crack; so the ViT gets no crack duty here.
- Different from Om's A1 (E: dropped on the A8 KILL without a run): A1 replaced the encoder; this keeps the house model and adds a zero-initialised context branch.

**CPU pre-check (decides whether to build; 1.5 build h, about 10 CPU-min; W1-G PF dumps, 10 runs, v1.1 strict held-out masks).** Script `bench/precheck/inactive_anatomy.py`, inputs = the `--arm PF=...` dump spec of `W1_READ.md`.
- GT inactive regions = 8-connected components of class 11 >= 100 px. Coverage = share of the region predicted 11 at argmax. FN px split into "region miss" (coverage < 0.2) and "partial" (>= 0.2). Predicted inactive components >= 100 px: "false region" if < 10% of px overlap GT 11 (dilated 3 px), else "spill". Report px shares pooled over seeds and per source, and the class that takes the region-miss px (crack, material, edge_dark, background).
- Same split for splice, edge_dark and material (region classes in R13).
- **Pass rule (fixed now):** build arm 2 if region-miss share of inactive FN px >= 0.5 or false-region share of inactive FP px >= 0.5. Park it if both are < 0.3 (the errors are boundary-level, which a stride-16 branch cannot fix). In between: the lead decides. Also print the share of region-miss px in cells whose max p_inact < 0.1 ("blind"), and of false-region px in BMRK cells.

**Exact change (new code).** File `src/models/vfm_ctx.py`; factory branch `model.name=vfm_ctx_unetpp` in `model_factory._build_core` (plus the error-message list).
```
class VfmCtxUnetPP(nn.Module):
  def __init__(cfg):
    base = smp.UnetPlusPlus("resnet34", encoder_weights=cfg.encoder_weights, in_channels=1, classes=24)  # built FIRST, exactly as smp_unetpp
    self.encoder, self.decoder, self.segmentation_head = base.encoder, base.decoder, base.segmentation_head  # names unchanged -> PF split and state-dict keys = house
    with torch.random.fork_rng(devices=[]):          # the extra modules must not change the house init stream
      self.vfm = timm.create_model(cfg.vfm.backbone, pretrained=bool(cfg.vfm.weights),
                                   pretrained_cfg_overlay=dict(file=cfg.vfm.weights), img_size=448, num_classes=0)
      self.vfm.requires_grad_(False)
      L = cfg.vfm.layers                               # default [11, 17, 23] for ViT-L (24 blocks)
      D = self.vfm.embed_dim                           # 1024
      self.vfm_proj = Sequential(Conv2d(len(L)*D, 256, 1, bias=False), GroupNorm(32, 256), GELU())
      self.vfm_fuse = ModuleDict({"s8": Conv2d(256, 128, 1), "s16": Conv2d(256, 256, 1), "s32": Conv2d(256, 512, 1)})
      for c in self.vfm_fuse.values(): zeros_(c.weight); zeros_(c.bias)
  def train(self, mode=True): super().train(mode); self.vfm.eval(); return self
  def forward(x):                                      # x: (B,1,512,512), house normalisation (mean 0.5, std 0.25)
    f = self.encoder(x)                                # [x, s2 (64,256^2), s4 (64,128^2), s8 (128,64^2), s16 (256,32^2), s32 (512,16^2)]
    with torch.no_grad():
      g = (x*0.25 + 0.5).clamp(0,1).repeat(1,3,1,1)
      g = (g - IMNET_MEAN) / IMNET_STD
      g = F.interpolate(g, size=448, mode="bilinear", align_corners=False)     # 32x32 tokens at patch 14
      t = self.vfm.forward_intermediates(g, indices=L, output_fmt="NCHW", intermediates_only=True)  # 3 x (B,1024,32,32)
    z = self.vfm_proj(torch.cat(t, 1))                 # (B,256,32,32), trainable
    f[3] = f[3] + self.vfm_fuse["s8"](F.interpolate(z, scale_factor=2, mode="bilinear", align_corners=False))
    f[4] = f[4] + self.vfm_fuse["s16"](z)
    f[5] = f[5] + self.vfm_fuse["s32"](F.avg_pool2d(z, 2))
    return self.segmentation_head(self.decoder(f))
```
- Parameter groups: `encoder.*` = R34 (PF group, as now); `vfm.*` frozen (no grad, so Adam keeps no state for it); `vfm_proj.*`, `vfm_fuse.*` in the house group (lr 1e-3, wd 1e-4). No trainer change.
- Card `vfm_ctx_r34_pf_v11` = `house_r34_unetpp_pf_v11` with `model.name=vfm_ctx_unetpp`, `model.encoder_weights=imagenet`, `model.vfm.backbone=vit_large_patch14_reg4_dinov2`, `model.vfm.weights=/home/noob/work/weights/vit_large_patch14_reg4_dinov2.lvd142m/model.safetensors`, `model.vfm.layers=[11,17,23]`. The ViT weights are stored in the checkpoint (about 1.2 GB per run dir more); `bench_infer` builds with `vfm.weights=null` and loads everything from the checkpoint.
- Unit tests (CPU): (a) output (2, 24, 512, 512); (b) at init, output equals a plain `smp.UnetPlusPlus` built from the same seed, max abs diff 0 in fp32 (zero fusion + fork_rng); (c) after one backward: every `vfm.*` grad is None, `vfm_fuse.*` grads non-zero, `encoder.*` in PF group 1 and nothing else; (d) 5-step CPU identity with a test-only key `model.vfm.freeze_fuse=true` (fusion convs stay zero) v `house_r34_unetpp_pf_v11`: IDENTICAL by `identity_cpu.py`; (e) builds with `vfm.weights=null` and loads a saved state dict strictly (the dump path); (f) a stand-in ViT for speed in (a) to (c): `vit_small_patch14_reg4_dinov2` with `weights=null`, layers [3, 7, 11].

**Pathfinder (gaint v W1-G PF f0 s5).** 1,000-step smoke (peak, steps/s; S: about 9 to 11 GB and 1.5 to 1.8 x house step time, ViT-L forward over 8 x 1,024 tokens without grad), then fold 0 seed 5 for 20k with fold + F51 dumps. Failure gates as arm 1, plus: the fusion conv weight norms must leave zero (else the branch is unused; log their L2 norm every 2k steps).

**Screen (cv02).** 10 runs v W1-C1 PF 5, 6 with the A/A null.
- Primary: inactive IoU at OP-A (CV pooled OOF). Guards: inactive precision, recall and region precision (both directions must hold within M), mIoU-R13, crack relF1@2 at OP-A and OP-W, width ratio, false alarms, per-source table (BMRK row named).
- Power, stated in advance (E, PROTOCOL 3.2): the SE of an inactive IoU contrast on CV5-G at 2 seeds was 0.038 to 0.039, so M will be about 0.08. S: if the pre-check region-miss share is >= 0.6, run seeds 5, 6, 7 (15 runs, about 28 GPU-h) so the screen can see +0.05.
- Second look (promotion only, X9): F51 inactive IoU and F51 crack relF1@2, paired over the models.

**What it should move.** S from R: in-distribution about 0 to +0.03 inactive IoU (P030 ID differences within about 1 Dice); the DG evidence (P030 +8 to +29 Dice on unseen scanners) is where the size is, and our CV only partly measures that (unseen modules, seen sources). So F51 and, at confirmation, E1 inactive are the reads that matter.
**Drop rule.** As the common frame; drop outright if crack relF1@2 at OP-A or OP-W or mIoU-R13 falls by more than M. A null closes "frozen DINOv2-L, 448 px, one-way fusion at stride 8 to 32"; it leaves Rein tuning (P069), DINOv3 (P190, gated) and full ViT-Adapter injection (P193) open but parked.

**Follow-ups (not arms; only if arm 2 promotes or moves F51).** (i) Rein tokens (m = 100, rank 16, layer-shared MLPs, R: P069 settings) on the ViT: the only change is `model.vfm.tuning=rein`; backward through the ViT raises memory (S: about 20 GB). (ii) DINOv3 ViT-L/16 at 512 (32 x 32 tokens, no resize): gated, user's OK.

**Cost.** Pre-check 1.5 h build. Code + tests + card 5 h. GPU: smoke 0.3, fold 0 about 2.2, screen 10 x about 1.9 = 19 GPU-h.

**Needs.** No package. Weights: `timm/vit_large_patch14_reg4_dinov2.lvd142m` (304.4M, Apache-2.0, not gated, HF page checked 13 Nov). Optional later: `timm/vit_large_patch16_dinov3.lvd1689m` (303.1M, DINOv3 licence: **gated, user's OK needed**).

**Risks and how it could mislead.**
- Instrument mismatch: the claimed benefit is domain generalisation; CV5-G holds out modules, not sources or layouts. A CV null is weak evidence against the DG claim; a CV pass with an F51 drop would mean source-level overfitting of the fusion convs.
- Inactive IoU at 2 seeds is decided by few groups (effective n about 13, E PROTOCOL 3.2); report leave-top-3-groups-out.
- Width: the branch only touches stride >= 8, so crack width should not move; if the width ratio moves > 1.15 the decoder used the branch for crack and the arm is not what it claims.
- Leakage: none new (frozen public weights; no pool data). The resize 512 to 448 is fixed and also used at inference.

---

## Arm 3. `nnunet_resenc_2d`: nnU-Net v2, 2D, ResEnc-L preset, on our folds (benchmark row and recipe source)

**Hypothesis.** The self-configured nnU-Net recipe (deep supervision, foreground oversampling, poly SGD, heavier augmentation, residual encoder), which beat every other approach on 30k crack images (R, P087), is a missing benchmark row and may beat the house model on crack; trained from scratch, it should be weaker than PF on unseen modules (S).

**Evidence.** R (P087 scout record, abstract): nnU-Net mean clIoU@4px 64%, at least 10 points above other approaches. R (P020 scout record): ResEnc L 88.17 v nnU-Net org 86.04 Dice on KiTS (3D); transformers below nnU-Net. R (Dino U-Net table, 2D, nnU-Net pipeline): nnU-Net 71.45 v UNet++ 73.42 mean Dice, so the 2D small-data case is not a clear nnU-Net win.

**Exact change (external codebase; harness DESIGN step 12, already planned, 8 h; this spec adds the cards, 1 h).**
- Venv `venv_nnunet` sharing torch read-only (the `venv_sam2` .pth pattern); `pip install nnunetv2` pinned (version recorded; torch 2.14 / cu130 compatibility unverified).
- Export (`bench_export.py --to nnunet`, pool stems only, refuses sealed stems): `Dataset601_ELcv5v2v11/imagesTr/<stem>_0000.png` (grey, symlink or copy), `labelsTr/<stem>.png` = v1.1 training masks with ignore 255 remapped to 24, `dataset.json` with `channel_names {"0": "EL"}`, labels 0..23 by class name plus `"ignore": 24` (nnU-Net v2 requires the ignore label to be the highest value), `file_ending ".png"`, `numTraining 532`. `splits_final.json` = the 5 cv5v2 folds (train / val stem lists from `benchmark/splits/cv5v2.json`), never nnU-Net's own split.
- Plan: `nnUNetv2_plan_and_preprocess -d 601 -pl nnUNetPlannerResEncL -c 2d` (record the patch size and batch size it picks; S: patch 512 x 512).
- Two trainers, each a labelled row: **N1 step-matched**: epochs = round(160,000 / (250 x batch)) (house sample budget 20k x 8); use the nearest shipped `nnUNetTrainer_<N>epochs` variant or a 5-line subclass setting `self.num_epochs`. **N2 native** (`nnUNetTrainer`, 1,000 epochs): gated, see below.
- Inference: `nnUNetv2_predict ... -f <k> --disable_tta --save_probabilities` on the held-out fold (and F51 for N1), converter to the dump format (`pred` = argmax of the 24 probabilities, `oth`, `m_crack`, `p_crack`, `p_inact`, `logp`), manifest with the trainer and plan md5. Mirroring TTA is a separate labelled column only.
- Augmentation: nnU-Net default (rotation, scaling 0.7 to 1.4, gamma, blur, noise, mirroring) for the native row. It resamples 1 to 2 px labels; if N1's crack width ratio is outside 0.85 to 1.15 x PF, add a label-safe trainer (rot90 / flip / intensity only, 1 build h) as a third row.
- Tests: export round trip (label ids, ignore 24, 532 cases, folds equal cv5v2 by md5), converter test on a fake probability file, a sealed-stem refusal test.

**Pathfinder.** N1 fold 0, seed 5 on gaint (`--exit` after 1,000 iterations first for peak memory and s/iteration), then full N1 fold 0, dump fold 0 + F51. Failure gate: OP-A crack relF1@2 >= PF fold 0 minus 0.10, no NaN class.

**Screen (cv02).** N1: folds 0 to 4, 2 seeds (nnU-Net seeds via `torch.manual_seed` in a trainer subclass; nnU-Net is not deterministic, S), v W1-C1 PF. Primary: crack relF1@2 at OP-A; strict crack IoU, inactive IoU, mIoU-R13 as guards with all WAVE2_REVIEW 5 guards. N2 (native budget): 5 folds x 1 seed for the benchmark table only, after N1 is read and when cv02 has idle GPUs (S: about 15 GPU-h per fold, 75 GPU-h; not this week unless GPUs are idle).

**What it should move.** S: crack relF1@2 -0.02 to +0.02 against PF (P087's margin was over other crack methods on another domain); inactive and F51 likely below PF (no pretrained features).
**Drop rule.** As a score candidate: drop if primary < M or any headline falls by more than M. As a benchmark row it is reported whatever it scores.

**Cost.** Build 9 h (8 already planned by the harness). GPU: pathfinder about 2, screen N1 10 x about 1.5 = 15 GPU-h (S: unmeasured; nnU-Net 2D speed at 512 is the pathfinder's job).

**Needs.** `nnunetv2` + pins (dynamic-network-architectures, batchgenerators(v2), acvl-utils, SimpleITK) in an isolated venv; no weights. Licence: Apache-2.0 (unverified).

**Risks.** Different normalisation (per-image z-score), sampling (foreground oversampling 33%) and augmentation: a crack gain may be an operating-point shift (OP-W guard) or width (width guard). Its internal validation uses training masks with ignore; never used. Budget fairness: N1 is the comparable row; N2 is labelled "native budget".

---

## Arm 4. `hiera_bp_adapter_frozen`: SAM2-UNet's frozen Hiera with prompt adapters (RUN_AFTER_GATE)

**Gate (fixed now).** Opens if (a) arm 1's fold-0 pathfinder logs stage-3 or stage-4 cos-to-init < 0.95 at 20k (PF changed the pretrained encoder), or (b) arm 1 passes its screen (then this is its competing PEFT variant). Parked if arm 1 fails and cos >= 0.95 (PF already kept the encoder; freezing adds little).

**Hypothesis.** Keeping the whole Hiera frozen and training only small per-block adapters keeps more of the SAM 2 representation than PF (R: Rein full FT < PEFT on unseen domains; P030 Freeze / Rein-LoRA >> full-FT U-Nets on DG) and so transfers better to unseen modules.

**Exact change (2.5 build h).** In `src/models/bench_models.py`, `_HRStemUnet.__init__`, new keys `model.backbone_freeze` (bool) and `model.backbone_adapter_dim` (int, 0 = off):
```
if cfg.backbone_freeze: self.encoder.requires_grad_(False)
if cfg.backbone_adapter_dim > 0:
  self.adapters = nn.ModuleList()
  for blk in self.encoder.blocks:                       # timm HieraDet: nn.Sequential of blocks, x is (B,H,W,C)
    d = blk.attn.qkv.in_features                         # block input width (SAM2-UNet uses the same attribute)
    a = nn.Sequential(nn.Linear(d, r), nn.GELU(), nn.Linear(r, d), nn.GELU()); self.adapters.append(a)
    blk.register_forward_pre_hook(lambda m, args, a=a: (args[0] + a(args[0]),) + tuple(args[1:]))
```
Adapters are named `adapters.*` (house lr group, not the PF group). r = 32 (R: SAM2-UNet code). Card `hiera_bp_adapter_frozen_v11` = arm 1's card + `model.backbone_freeze=true`, `model.backbone_adapter_dim=32` (PF keys kept; they act on a frozen encoder).
Tests: output shape; `encoder.*` grads None and `adapters.*` grads non-zero after one backward; adapter count = len(blocks) = 24 for B+; state dict round trip and `bench_infer` rebuild re-registers the hooks (forward equal before and after reload); attribute names checked against the installed timm (`hieradet_sam2.py`; S: verify `blocks` and `attn.qkv`).

**Pathfinder, screen, metrics.** As arm 1 (same size as arm 1 screened). Primary mIoU-R13 at OP-A; the contrast that matters is arm 4 minus arm 1 on F51 (promotion only) and on mIoU-R13, plus arm 4 minus PF. Drop: as arm 1. S: memory below arm 1 (no Adam state for 69M parameters; activations still stored for backward through the frozen blocks).
**Cost.** 2.5 build h; GPU 2.5 + about 20.
**Needs.** As arm 1.
**Risks.** A frozen encoder may lose in-distribution accuracy (P030 Table 3: Freeze ID 80.72 v Ladder 84.95 on DINOv2-B) and gain only where we cannot measure well (E1). The adapter adds a learned input prompt at every block; with 478 cells it can still overfit, so watch the train-loss gap.

---

## 5. What the lead must know (S)
1. Arm 1 is config-only on code that exists (`bench_timm` + f8 HR stem + `training.encoder_pf`); it needs one public download (Apache-2.0) and a 1,000-step smoke. It can start as soon as a gaint lane is free.
2. Arm 2 is the main inactive and unseen-module bet, but the CV instrument has about 0.08 resolution on inactive at 2 seeds and does not hold out sources or layouts. Its CPU pre-check on the W1-G dumps should run first; it costs 1.5 h and decides whether 5 build hours are spent.
3. No gated weights are needed for arms 1 to 4. Gated items for the user, only if follow-ups open: DINOv3 ViT-L/16 (`timm/vit_large_patch16_dinov3.lvd1689m`, DINOv3 licence) and SAM 3 (`facebook/sam3`, HF access request).
4. Mask-classification decoders (Mask2Former, EoMT) stay benchmark rows: R (P502) EoMT-DINOv3 crack mask mAP 4.7 v YOLOv11 8.6, and Mask2Former's authors report weak small objects. They should be judged on inactive and region classes, with a per-pixel crack head (P159, P467 pattern).
5. F51 dumps of the 10 PF baseline runs are needed once for arms 1, 2, 4 (about 10 GPU-min).

## 6. Zero-build follow-up cards (not arms; listed so nobody re-derives them)
- `dinov3_cnxt_t_unetpp_fullft`: HR-stem U-Net++ + DINOv3 ConvNeXt-T (weights already local and licence-accepted, E), full fine-tune (no `encoder_pf`), 20k steps, against the W1c HR-stem ConvNeXt-T IN-1k row. Tests P195's claim (full long fine-tune, not PF / 4k as A8) on CV5-G. Prior is low (P195's own greyscale X-ray result is negative); run only on idle GPUs.
- `segformer_mitb2`: `bench_smp decoder=segformer encoder_name=mit_b2 encoder_weights=imagenet` (benchmark row; check smp mit 1-channel support first; SegFormer weight licence unverified).
- `frozen_dinov2l_dpt`: `bench_timm decoder=dpt backbone=vit_large_patch14_reg4_dinov2` with `training.encoder_pf.lr_mult=0` and freeze = total steps (benchmark reference row for P547; documents the stride-16 limit). 512 is not a multiple of patch 14: smp DPT with a tu- ViT needs `dynamic_img_size` or a 518 resize (unverified in smp 0.5.0; check on CPU first).
