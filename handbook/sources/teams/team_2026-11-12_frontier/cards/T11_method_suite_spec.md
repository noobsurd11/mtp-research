# T11 spec: the benchmark method suite (13 Nov 2026)

Analyst T11. Tags: R = paper or repository (fetched), E = our files, S = my judgement. Paper cards: `T11_method_suite_family.md`. Ledger: `ledger/T11.tsv`. Nothing was run, installed or downloaded.

## 0. Common frame

- **Comparator:** card `house_r34_unetpp_pf_v11`. Screens on cv02 against W1-C1 PF seeds 5, 6 (A/A from PF {5,6} v {7,8}); pathfinders on gaint against W1-G PF fold 0 seed 5. One machine per comparison (WAVE2 X10).
- **Screen:** cv5v2, folds 0 to 4, seeds 5 and 6, 20k steps, batch 8, 512 px, label set v1.1, final weights, argmax; held-out fold dumped in canonical fp32 with `logp` (needed by H1); F51 dumped too (read ledger, X9). Score with `bench_read_w1.py` (E, `harness/W1_READ.md`): OP-A, OP-F, OP-W from `crossfit_op`, all WAVE2 section 5 guards, two-stage bootstrap (330 groups, then seeds).
- **What a suite row is:** a benchmark table entry. Default recipe = the house PF recipe, so the architecture is the only difference. Exceptions, stated per row: models with no pretrained encoder cannot use PF (the trainer refuses PF without `encoder.*` parameters, and freezing a random encoder is meaningless), so they use the house recipe without PF (= card `house_r34_unetpp_v11` opts); where the paper's own recipe is a defining part of the method, a second row carries it.
- **Pre-declared primary for every suite row:** crack relF1@2 at OP-A, read as a table entry, not a pass. A row is flagged as a candidate to beat the house model only if it passes the standard rule on that primary (delta >= M, interval above 0, present at OP-A and OP-W, width ratio 0.85 to 1.15 x PF); then it goes to seeds 7 to 9 like any arm. Every row enters the 5-seed table later regardless (PROTOCOL decision 9: 2 seeds to screen, 5 for table entries); that is a second tranche, not this spec's budget.
- **Failure gates (pathfinder, fold 0, seed 5; catch failures only, never rank):** loss finite; step-20k train loss <= 1.5 x PF's; OP-A crack relF1@2 >= PF fold 0 minus 0.15 (scratch rows) or minus 0.10 (pretrained rows); width ratio 0.6 to 1.8 x PF; inactive IoU and mIoU-R13 not NaN; peak memory <= 40 GB; step time <= 4 x PF. On failure: one documented retry (named per row), then the row is published as "does not train under the protocol" with the reason. That is a valid benchmark outcome.
- **Sealed:** legacy test and E1 never read here. F51 only through the read ledger; H36 in no rule.
- **Not duplicated (E):** UPerNet + ConvNeXt-T IN-1k (harness milestone card), HR-stem U-Net++ ConvNeXt-T and every foundation, ViT, SAM and nnU-Net row (T6). W1-C2 (house fine-tune) and W1-C3 (PF on v1 labels) are already table rows. None of the 29 wave-2 arms changes the architecture (WAVE2 section 2).

## Priority table

Order = value per build hour. GPU-h are S estimates from FLOPs relative to the house model (1.1 GPU-h per run on an A6000, E); each pathfinder smoke measures the real figure.

| # | Name | Papers | Route | Build h | GPU-h (pathfinder + screen) | Gate | Priority |
|---|---|---|---|---|---|---|---|
| A0 | `head_res_ceiling` (CPU) | P259, P261, P191 (all stride-4 heads) | analysis_only | 1 | 0 | none | 90 |
| 1 | `dlv3p_r34_pf` | P259 (+Torpey R0) | config_only (bench_smp) | 0.5 | 1 + 8 | none | 85 |
| 2 | `unet_r34_pf` | P485, P259 | config_only (bench_smp) | 0.3 | 1 + 10 | none | 80 |
| 3 | `segformer_mitb2_pf` | P261 | config_only (bench_smp) | 0.5 | 1.5 + 14 | weights download | 78 |
| 4 | `rift_b` | P191 | new_model_code (vendored file) | 2.5 (incl. 1.5 shared registry) | 0.5 + 5 | none | 75 |
| 5 | `hrnet_w18_unetpp_pf` | P361 | config_only (bench_smp tu-) | 0.5 | 1.5 + 15 | CPU build | 70 |
| H1 | `suite_hetero_ens` (CPU) | P171 question, all rows | inference_only | 2 | 0 | >= 2 rows screened | 68 |
| 6 | `pratt_dlv3p_wcec` | P259 | config_only | 0.3 | 0 + 8 | weighted_ce ignore test | 65 |
| 7 | `scsegamba` | P354 | new_model_code + isolated venv | 6 | 2 + 20 | G-MAMBA | 60 |
| 8 | `dscnet_2d` | P104 | new_model_code (vendored) | 2 | 2.5 + 25 | memory | 55 |
| 9 | `hrsegnet_b48` | P446 | new_model_code (port) | 3.5 | 0.6 + 6 | port test | 50 |
| 10 | `ucf_dlv3_r50_pf` | P485 | config_only | 0.3 | 2 + 20 | none | 45 |
| 11 | `hanifi_vgg16_unet_pf` | extra (IEA 2025) | config_only (factory smp_unet) | 0.2 | 1.5 + 15 | none | 45 |
| 12 | `rift_b_paper` | P191 | config_only (after row 4) | 0.2 | 0 + 5 | row 4 trains | 40 |
| 13 | `mixercseg` | P408 | new_model_code + venv | 6 | 1.5 + 15 | G-MAMBA, G-VMAMBA | 30 |
| 14 | `hybrid_segmentor` | P329 | new_model_code (vendored) | 5 | 1.5 + 15 | none | 25 |

**Tranche 1 (recommended now):** A0, rows 1 to 5: 5.3 build h (1.5 of it the shared vendored-model registry, reused by rows 7 to 9, 12 to 14), about 57 GPU-h. It gives the classic CNN rows, the EL transformer row, the first crack specialist and the high-resolution row. **Tranche 2:** H1, rows 6 to 10 (14.1 build h, about 86 GPU-h). **Wave 3:** rows 11 to 14 (11.4 build h, about 55 GPU-h).
**First arm:** A0 (CPU, 1 h, uses the W1-G PF `logp` dumps and `bench_score.py`); first GPU row: `dlv3p_r34_pf` (0.5 h, uses `bench_smp` and `training.encoder_pf`).

**Rows that might also beat the house model (S):** `hrnet_w18_unetpp_pf` (keeps the house decoder and PF, swaps in an encoder that never drops below a stride-4 stream) and H1 (heterogeneous ensembles were never tried, BRIEF 5; the 5-seed homogeneous ensemble is the only clear win so far, +0.014 to +0.018 crack IoU, E BRIEF 5). Every stride-4-head row (DeepLab, SegFormer, RIFT, UPerNet) is expected below PF on strict crack IoU; A0 measures how much of that is the head alone.

---

## A0. `head_res_ceiling`: what a stride-s output head costs, measured on PF itself (CPU)

- **Question:** how much crack IoU, relF1@1, relF1@2 and width does a model lose only because it predicts at stride 4 (or 2, 8) and upsamples bilinearly? It decides how to read rows 1, 3, 4, 6, 10, 12 and the harness UPerNet row, and whether any of them can be a candidate.
- **Input (E):** W1-G PF dumps (10 runs, 532 cells, `logp` float16 24 x 512 x 512).
- **Method:** new script `bench/a0_headres.py` (numpy + torch CPU). For s in {1, 2, 4, 8}: `z = F.avg_pool2d(logp, s)` (24 x 512/s x 512/s), `z_up = F.interpolate(z, 512, mode="bilinear", align_corners=False)`, `pred = argmax(z_up)`; write `pred`, `oth`, `m_crack` in the dump format (`bench/dumpfmt.py` writer, so `m_crack = z_up[14] - max_{k != 14} z_up[k]`) into a scratch dump root; score with `bench_read_w1.py --arm S1=... --arm S4=...` against s = 1 (which must reproduce PF exactly: assert). Also a GT-only ceiling: one-hot GT pooled and upsampled the same way, argmax (ties to the GT class), scored against GT.
- **Output:** per s: crack strict IoU, relF1@2, relF1@1, relP@2, relR@2, width ratio, component recall, inactive IoU, mIoU-R13, gridline IoU; per source.
- **Reading rule (fixed now):** if s = 4 loses >= 0.05 strict crack IoU or >= 0.02 crack relF1@2 against s = 1, every stride-4 row is printed with the s = 4 ceiling beside it and none of them can be flagged as a candidate on crack; their crack numbers then measure the head, not the encoder. If s = 4 loses < 0.01 on both, output resolution does not bind and stride-4 rows compete on equal terms. In between: printed, no rule.
- **Unit test:** s = 1 reproduces the PF dump byte for byte (`pred`); a synthetic 1 px line at s = 4 is lost or widened (expected).
- **Cost:** build 1 h; CPU about 30 min (1,064 cell-dumps x 4 scales). Risk: pooling log-probabilities is not pooling logits; a real stride-4 model learns to place its coarse output, so this is an upper bound on the loss of the head as trained at s = 1, not a prediction of a stride-4 model's score. Said so in the table.

---

## Row 1. `dlv3p_r34_pf`: DeepLabV3+ / ResNet-34 under PF (Pratt 2023 architecture, Torpey R0)

- **Problem:** benchmark_row. **Primary:** crack relF1@2, OP-A.
- **Change (config only, harness `bench_smp`):** card `bench/methods/dlv3p_r34_pf_v11.yaml` = `house_r34_unetpp_pf_v11` with `model.name=smp_unetpp` replaced by
  ```
  - model.name=bench_smp
  - model.decoder=deeplabv3plus
  - model.encoder_name=resnet34
  - model.encoder_weights=imagenet
  ```
  `papers: [doi:10.1016/j.sasc.2023.200048, arXiv:2402.17611]`, `diff_ref: house_r34_unetpp_pf_v11`, weights = the house R34 file (same md5).
- **One code change (0.3 h), in `build_bench_smp`:** for `deeplabv3` and `deeplabv3plus`, replace every `nn.AdaptiveAvgPool2d(1)` by the `GlobalAvgPool` of `src/models/deeplabv3plus.py` (same value, deterministic backward; the old wrapper does this, E l.66-69). Unit test: with seed 0, `bench_smp` DLV3+ R34 and `DeepLabV3PlusWrapper(encoder_name="resnet34")` have equal state dicts after stripping the wrapper's `model.` prefix and equal outputs on a (2, 1, 512, 512) input; every encoder parameter starts with `encoder.`; PF builds two groups.
- **Pathfinder (gaint):** 1,000-step smoke (peak, step time), then fold 0 seed 5, 20k. If the harness W1c DeepLabV3+ R34 pathfinder card already ran, reuse its fold-0 run and skip this.
- **Expectation (S, from P259's "dilated predictions" and A0):** width ratio up (1.1 to 1.4 x PF), relR@2 near PF, strict crack IoU and relF1@1 below PF by 0.03 to 0.08; gridline below PF. Inactive near PF (blobby).
- **Cost:** 0.5 build h; about 0.8 GPU-h per run (S), 1 + 8.
- **Needs:** nothing new. **Risks:** the dilated output looks good on relR@2 (guard: relF1@1, width, OP-W). The bilinear upsampling in the decoder has a non-deterministic backward under cuDNN deterministic mode (the trainer does not set strict mode, E `seed.py` l.37-41), so reruns are not bit-identical; harmless for the screen.

## Row 2. `unet_r34_pf`: U-Net / ResNet-34 under PF (the U-Net family of Pratt and the EL lines)

- **Problem:** benchmark_row. **Primary:** crack relF1@2, OP-A.
- **Change:** as row 1 with `model.decoder=unet`. No code. Unit test: CPU build, output (1, 24, 512, 512), `encoder.` prefix, PF groups.
- **Expectation (S):** within about 0.01 to 0.02 of PF on every headline (U-Net++ adds nested skips; same encoder, same full-resolution head). This row shows what the house's U-Net++ choice is worth.
- **Cost:** 0.3 build h; 1 + 10 GPU-h. **Risks:** none specific. A difference smaller than M is the expected and informative outcome.

## Row 3. `segformer_mitb2_pf`: SegFormer MiT-B2 under PF (P261, the EL SegFormer)

- **Problem:** benchmark_row. **Primary:** crack relF1@2, OP-A; mIoU-R13 reported beside (the row's likely strength).
- **Change (config only):**
  ```
  - model.name=bench_smp
  - model.decoder=segformer
  - model.encoder_name=mit_b2
  - model.encoder_weights=imagenet
  ```
  PF keys unchanged (MiT parameters are under `encoder.`; E: the smp class puts the encoder there). smp patches the first patch embedding to 1 channel (E: the random-init CPU test builds with in_channels 1).
- **Weights:** smp-hub `mit_b2` ImageNet file, public HF download (repo id `smp-hub/mit_b2.imagenet`, unverified), placed in the HF cache on gaint and cv02 before the smoke (jobs run with `HF_HUB_OFFLINE=1`, E). Card md5 after download. Unit test: the first patch-embedding weight equals the RGB sum of the file's.
- **Deviation:** P261's MiT variant is unverified; B2 (25M parameters) is chosen to match the house size (26.1M, E). SegFormer's own recipe (AdamW 6e-5, poly) is not used: the house PF recipe keeps the architecture as the only change.
- **Expectation (S):** stride-4 head (A0 applies); crack strict IoU below PF; context classes (material, frame edge, border) at or above PF.
- **Cost:** 0.5 build h; about 1.4 GPU-h per run (S), 1.5 + 14.
- **Risks:** NVIDIA's SegFormer weight licence is non-commercial (unverified); state it in the table. LayerNorm encoder under PF's 0.1x lr may under-adapt; one retry with `training.encoder_pf.lr_mult=0.3` if the failure gate trips.

## Row 4. `rift_b`: RIFT-B, scratch, house recipe without PF (P191)

- **Problem:** benchmark_row (crack specialist 1). **Primary:** crack relF1@2, OP-A.
- **Shared code first (1.5 h, reused by rows 7, 8, 9, 12 to 14): `model.name=bench_vendored`.**
  - File `src/models/vendored/__init__.py`: `REGISTRY = {"rift_b": ..., "rift_t": ..., "dscnet2d": ..., "hrsegnet_b48": ..., "scsegamba": ...}`; `build_bench_vendored(cfg)` reads `model.arch` and `model.arch_kwargs`, builds with `in_channels=1`, `num_classes=24`, and returns a module whose `forward(x: (B,1,H,W)) -> logits (B,24,H,W)` (auxiliary heads, if any, are not returned).
  - One `elif name == "bench_vendored"` in `_build_core` (model factory), error message updated. Flag-off identity unchanged (house and PF cards IDENTICAL on the 5-step CPU check, WAVE2 guard 10).
  - Each vendored file carries the upstream repository URL, commit hash, licence text and a list of every edit.
  - Card validation: a `bench_vendored` card with `training.encoder_pf` set fails `bench.cards validate` (no pretrained encoder), unless the arch declares `pretrained_encoder: true`.
  - Tests (`tests/test_bench_vendored.py`): every registered arch builds on CPU, forward (2, 1, 512, 512) -> (2, 24, 512, 512), finite; deterministic forward in eval; parameter count printed and compared with the paper at the upstream configuration (in 3, out 1) within 3%.
- **RIFT file (1 h):** copy `rift.py` (MIT, imports torch only, R) to `src/models/vendored/rift.py`. Edits: `in_ch=1`; head `nn.Conv2d(decoder_dim, 24, 1)`; final upsample to `x.shape[-2:]` instead of the fixed `out_size`; `kernel_size=13` (README training flag and the paper's best kernel, R; code default 11). Unit test: at in 3 / out 1 / k 13, parameters = 1.69M +/- 3% (R, Table 3).
- **Card `rift_b_v11.yaml`:** `house_r34_unetpp_v11` opts (no PF keys) with `model.name=bench_vendored`, `model.arch=rift_b`. Everything else house: Adam 1e-3, 200-step warmup, cosine, wd 1e-4, CE + Dice (14, 11), labelsafe aug, batch 8, 20k steps.
- **Deviations from the paper and why:** 24 classes with softmax CE + Dice (the benchmark trains 24 classes, PROTOCOL 4.2) instead of binary BCE + Dice; batch 8 and 20k steps (160k samples) instead of batch 1 x 50 epochs (about 21k samples on 425 cells), so the sample budget equals every other row; house optimiser (row 12 carries the paper optimiser).
- **Expectation (S):** below PF on strict crack IoU (scratch, stride-4 head) and on mIoU-R13 (64-channel decoder for 24 classes); the paper's own ablation (R, Table 4) gives the directional strips +0.5 mIoU over local-only blocks, so no crack-specific edge is expected on EL. The row's value: the smallest model in the table (T4 track: 3.34 GFLOPs at 512 against 148 for the house model) and a current crack-specialist reference.
- **Cost:** 2.5 build h; about 0.5 GPU-h per run (S; data loading bound), 0.5 + 5.
- **Risks:** scratch versus pretrained is a confound in every comparison with PF; the table labels "pretraining: none". GroupNorm at batch 8 is fine.

## Row 5. `hrnet_w18_unetpp_pf`: HRNet-W18 encoder in the house U-Net++ under PF (P361)

- **Problem:** benchmark_row; also flagged as a candidate (crack). **Primary:** crack relF1@2, OP-A (candidate rule applies).
- **CPU gate (0.3 h):** build `bench_smp` with `decoder=unetplusplus`, `encoder_name=tu-hrnet_w18` (timm `hrnet_w18.ms_aug_in1k` file). smp's timm-universal encoder accepts only reductions (4, 8, ...), (2, 4, ...) or (1, 2, ...) and Unet++ needs the stride-2 one (E, smp050 `timm_universal.py` l.105-121). Pass = builds, output (1, 24, 512, 512), first conv = RGB sum. Fallback: `bench_timm` with `decoder=unetplusplus`, `backbone=hrnet_w18` (HR stem supplies stride 2), if timm's HRNet supports `forward_intermediates` (unverified). If neither builds: PARKED, reason "HRNet does not fit the registry".
- **Change (config only):** as row 1 with `model.decoder=unetplusplus`, `model.encoder_name=tu-hrnet_w18`, `model.encoder_weights=imagenet`, `model.encoder_weights_file=<local timm file>`.
- **Weights:** `timm/hrnet_w18.ms_aug_in1k` (public HF, licence not verified), downloaded to the weights folder, md5 in the card.
- **Hypothesis (S):** the same decoder, head and PF, with an encoder whose features keep a stride-4 stream through every stage; more spatial detail for 1 to 2 px cracks at layer3 / layer4 depth than ResNet-34 gives. 21M encoder parameters, close to R34.
- **Expected effect:** no paper evidence on thin lines (R: Cityscapes, pose); S: crack relF1@1 and strict IoU +0 to +0.02. Drop rule: the standard rule; a pass promotes to seeds 7 to 9.
- **Cost:** 0.5 build h; about 1.5 GPU-h per run (S), 1.5 + 15.
- **Risks:** the ResNet-50 row was worse on inactive (BRIEF 5): a bigger encoder can lose inactive; guard inactive P / R. HRNet's many BN layers under PF's frozen first 1k steps: watch the step-1k loss jump in the pathfinder.

## H1. `suite_hetero_ens`: do different architectures add to the house model? (CPU readout)

- **Problem:** crack. **Primary:** crack relF1@2 at OP-A, hetero pair minus homo pair (also required at OP-W).
- **Gate:** at least two suite rows screened on cv02 with `logp` dumps (rows 1 to 5; W1-C1 PF already dumps `logp`, E W1-C jobs `logp 1`).
- **Method (script `bench/h1_hetero.py`, numpy):** per fold k and pair j: homo_j = mean softmax of PF seeds (5, 7) for j = 0 and (6, 8) for j = 1; hetero_j = mean softmax of PF seed (5 + j) and row X seed (5 + j). Write both as dumps (`pred = argmax`, `m_crack`, `oth`) and score with `bench_read_w1.py`, treating j as the seed. One contrast per row X (pre-declared list: rows 1 to 5 in order; the count of contrasts goes into the ledger). This separates "a second model" from "a different second model" at equal member count and equal inference cost.
- **Pass rule:** hetero minus homo >= M (M from the A/A, X1) with interval above 0, at OP-A and OP-W, width ratio inside 0.85 to 1.15. A pass promotes to a 5-member check (PF seeds 5 to 9 against PF 5 to 7 + two X seeds) on the 5-seed table runs.
- **Expected effect (S):** small; homogeneous 5-seed ensembling gave +0.014 to +0.018 crack IoU (E). A stride-4 row averaged in will widen cracks (guard: OP-W).
- **Cost:** 2 build h; CPU about 30 min per row. **Risks:** logp is float16 (fine for averaging); multiplicity of up to 5 contrasts, stated.

## Row 6. `pratt_dlv3p_wcec`: Pratt 2023's own recipe (weighted CE, set C)

- **Problem:** benchmark_row (published recipe); also reads the weak classes. **Primary:** crack relF1@2, OP-A; gridline IoU and recall printed beside.
- **Change:** row 1's card with `loss.supervised=weighted_ce` and `loss.weight_set=C` (E: `pratt_weights("C")` = background 0.2, ribbons 3, gridline 10, inactive 10, crack 20, others 1). One change against row 1: the loss.
- **Pre-check (unit test, 0.2 h):** `WeightedCrossEntropyLoss(weight=...)` must ignore 255 (v1.1 train masks hold ignore px, E LEAD_INSTRUCTIONS). The factory passes no `ignore_index` in the weighted branch (E, `loss_factory.py` l.57-63); if the class default is not 255, pass `ignore_index=int(cfg.get("ignore_index", 255))` there (flag-off identity unaffected: the house cards use `ce_dice`). Test: a mask with 255 px gives a finite loss equal to the loss on the same mask with those px removed.
- **Expectation (R, P259 abstract and section 4):** crack recall up, precision down from dilated predictions. S: relR@2 up, width ratio 1.3 to 2 x PF, strict IoU and relF1@1 down; gridline recall up (weight 10).
- **Cost:** 0.3 build h; 8 GPU-h. **Risks:** this is the textbook width-inflation case; OP-W and relF1@1 decide how it reads. Pratt's weights were tuned on their split and labels (R, DOE on an unstated split); the row is "their recipe, our protocol".

## Row 7. `scsegamba`: SCSegamba, scratch (P354, the Mamba row)

- **Problem:** benchmark_row (Mamba representative, crack specialist 2). **Primary:** crack relF1@2, OP-A.
- **Gate G-MAMBA (before any port beyond the files, 2 build h, CPU + 5 GPU-min):** isolated venv `venv_mamba` on gaint with the `venv_sam2` pattern (shares the house torch 2.14 read-only via a `.pth`, E DESIGN 1.10); `pip install mamba-ssm` (the release that builds with torch 2.x; 1.2.0 is the pinned upstream version and targets torch 1.13) with `--no-build-isolation`. Pass = it builds, and `selective_scan_fn` matches `selective_scan_ref` (pure PyTorch, same module) on random inputs (B 2, D 64, L 1024, N 16, fp32) within 1e-3, forward and backward, on the gaint GPU. Fail = PARK with reason "selective-scan kernel does not build on torch 2.14 / cu130"; the pure-PyTorch reference loops over 4,096 tokens per scan (64 x 64 patches at 512 px) and is too slow for 20k steps (S; measure one step to confirm before parking).
- **Port (4 h):** vendor `models/{GBC,MFS,PAF,DySample,decoder}.py` and `mmcls/SAVSS_dev/models/{SAVSS/SAVSS.py, SAVSS/SAVSS_layer.py, modules/patch_embed.py}` into `src/models/vendored/scsegamba/` (Apache-2.0 header). Remove mmcv / mmcls: `BaseBackbone` -> `nn.Module`; `build_norm_layer(dict(type="LN"), C)` -> `("ln", nn.LayerNorm(C))`; `mmcv.runner.base_module.ModuleList` -> `nn.ModuleList`; `mmcv` `trunc_normal_` -> `timm.layers.trunc_normal_`; `build_dropout(dict(type="DropPath", drop_prob=p))` -> `timm.layers.DropPath(p)`; drop the `@BACKBONES.register_module()` decorator; `resize_pos_embed`, `to_2tuple` from timm. Keep `selective_scan_fn` and the triton `RMSNorm` from `mamba_ssm`. First conv: in 1. Final MFS output conv: 24 channels. `arch='Crack'` defaults as upstream.
- **Unit tests:** module builds without mmcv / mmcls importable; forward (2, 1, 512, 512) -> (2, 24, 512, 512); parameters at in 3 / out 1 = 2.80M +/- 3% (R, Table 2); the scan check of G-MAMBA in the test suite (skipped without CUDA).
- **Card:** `scsegamba_v11.yaml`, house recipe without PF, `model.name=bench_vendored`, `model.arch=scsegamba`; `external: {venv: venv_mamba}` so the queue launches the house trainer with that venv's python (the trainer code is unchanged; the venv only adds mamba_ssm).
- **Deviations:** as row 4 (24 classes, house optimiser, sample budget). Public crack checkpoints (TUT etc.) are not used for the primary row (S: binary pavement-crack pretraining is a different track; an optional "crack-pretrained init" variant may follow if the row trains).
- **Expectation (S):** below PF (scratch, 2.8M parameters, 425 cells); full-resolution output through DySample, so A0 does not apply. The structure-aware scan is the only published mechanism here built for line continuity; component recall and any-hit recall are the interesting guards.
- **Cost:** 6 build h; about 2 GPU-h per run (S: 18 GFLOPs, but the scan kernel is slow at inference, R: 13 FPS in RIFT Table 3), 2 + 20. Gate on step time <= 4 x PF.
- **Risks:** the triton RMSNorm needs a triton matching torch 2.14 (bundled with torch, S). A build that succeeds but returns wrong gradients is caught only by the scan test; keep it in the suite.

## Row 8. `dscnet_2d`: DSCNet 2D, scratch (P104)

- **Problem:** benchmark_row (thin-structure representative). **Primary:** crack relF1@2, OP-A.
- **Change (2 h):** vendor `S3_DSCNet.py` and `S3_DSConv.py` (MIT, verified by T5 and here) into `src/models/vendored/dscnet/`. Edits: `n_channels=1`, `n_classes=24`, remove the final sigmoid (return logits), `number=16`, `kernel_size=9`, `extend_scope=1.0`, `if_offset=True` (upstream defaults, R `S0_Main.py`); replace the `device` constructor argument by tensors created on `x.device` inside DSConv. Unit tests as row 4; plus `if_offset=False` gives a plain-conv network (DSConv degenerates, R docstring) for a CPU sanity check.
- **Card:** house recipe without PF, `model.arch=dscnet2d`.
- **Memory gate (pathfinder smoke):** peak at batch 8, 512 px. If > 40 GB: one retry with `training.accum_steps=2` at batch 4 if the harness has built accumulation (DESIGN step 9, planned), else PARK with reason "does not fit batch 8 at 512 px". Upstream trains 224 crops at batch 1 (R), so memory at our size is unmeasured.
- **Deviation:** upstream 400 epochs, lr 1e-4, batch 1 (R); ours = house recipe (sample budget equal across rows).
- **Expectation (R, scout):** DRIVE Dice 82.06, roads +1.31 Dice over U-Net at best. S: below PF (scratch, full-resolution head though); E1 long cracks are where snakes could help, and E1 is sealed, so this row's value is the table.
- **Cost:** 2 build h; about 2.5 GPU-h per run (S), 2.5 + 25.

## Row 9. `hrsegnet_b48`: HrSegNet-B48, scratch, PyTorch port (P446)

- **Problem:** benchmark_row (crack specialist 3, high-resolution path). **Primary:** crack relF1@2, OP-A.
- **Port (3.5 h):** translate `models/hrsegnet_b48.py` (Apache-2.0, about 210 lines, R) to `src/models/vendored/hrsegnet.py`: `nn.Layer` -> `nn.Module`, `Conv2D` -> `Conv2d`, `Conv2DTranspose` -> `ConvTranspose2d`, `BatchNorm2D(momentum=0.9)` -> `BatchNorm2d(momentum=0.1)`, `AvgPool2D` -> `AvgPool2d`, `F.interpolate(..., align_corners=True)` kept, `paddle.shape(x)[2:]` -> `x.shape[2:]`, kaiming / constant init via `nn.init`; `in_channels=1`, `num_classes=24`, `base=48`. Training-mode auxiliary heads are not built (deviation: the trainer takes one logit tensor; deep supervision dropped, stated in the card).
- **Unit test:** forward shapes; parameter count of the port at in 3 / classes 2 printed and compared with the count from the released Paddle checkpoint's state dict (download optional; if not downloaded, compare against a hand count of the layer list).
- **Card:** house recipe without PF, `model.arch=hrsegnet_b48`.
- **Expectation (S):** a stride-2 head and a stride-4 high-resolution path from scratch; below PF overall, closest of the scratch rows on crack relF1@1.
- **Cost:** 3.5 build h; about 0.6 GPU-h per run (S), 0.6 + 6.

## Row 10. `ucf_dlv3_r50_pf`: DeepLabv3 / ResNet-50 under PF (Fioresi 2022, UCF-EL)

- **Problem:** benchmark_row. **Primary:** crack relF1@2, OP-A.
- **Change:** row 1 with `model.decoder=deeplabv3`, `model.encoder_name=resnet50` (the house cache holds smp-hub resnet50, E DESIGN 1.10). The deterministic pooling swap of row 1 covers `deeplabv3`.
- **Deviations:** ImageNet R50 instead of COCO (smp has no COCO encoder; Torpey: COCO 0.544 against ImageNet 0.508 mIoU on their split, R via handbook 05 3.4); no auxiliary head; house PF recipe instead of SGD 0.005 poly (E, `ucf_deeplab.yaml`). A paper-recipe row is not proposed: our UCF reproduction already showed the 30-epoch PV-S3 / UCF budgets are under-trained (E, handbook 05 4.2).
- **Expectation (S):** the weakest thin-structure decoder (output stride 8, no low-level skip). ResNet-50 encoder was worse on inactive in the U-Net++ (BRIEF 5).
- **Cost:** 0.3 build h; about 2 GPU-h per run (S, OS 8 at 512), 2 + 20.

## Row 11. `hanifi_vgg16_unet_pf`: VGG16-UNet under PF (Hanifi 2025, the E-SCDD authors)

- **Problem:** benchmark_row. **Primary:** crack relF1@2, OP-A.
- **Change:** `house_r34_unetpp_pf_v11` with `model.name=smp_unet` (factory default `encoder_name=vgg16`, `encoder_weights=imagenet`; E factory l.67-75; smp.Unet keeps `encoder.` so PF applies). Weights: smp-hub vgg16 (in the HF cache, E).
- **Deviation:** their custom class weights are not on the README (R) and are not used; house loss.
- **Cost:** 0.2 build h; about 1.5 GPU-h per run (S), 1.5 + 15. **Risks:** VGG16 without BN under PF; fine in our old-era runs (E, Pratt-A row).

## Row 12. `rift_b_paper`: RIFT-B with the paper's optimiser and schedule

- **Change (against row 4, one change = the recipe):** `training.optimizer=adamw`, `training.lr=5e-4`, `training.weight_decay=0.01`, `training.lr_scheduler=poly`, `training.poly_power=0.9`, `training.warmup_steps=0` (poly refuses warmup, E trainer l.92-95), `loss.dice_weight=0.2` (the paper's BCE : Dice = 5 : 1 carried over as CE : Dice). Steps and batch unchanged.
- **Primary:** crack relF1@2, OP-A, against row 4 (and PF). **Cost:** 0.2 build h; 5 GPU-h. Runs only if row 4 passed its failure gates.

## Row 13. `mixercseg` (P408), wave 3
- Gate G-MAMBA passed, then G-VMAMBA: VMamba's `kernels/selective_scan` builds in `venv_mamba` and matches its reference within 1e-3. Port as row 7 (strip mmcv-full). 6 build h; 1.5 + 15 GPU-h. RIFT's table already ranks it below RIFT-B on all four crack sets (R), so it runs only if the cv02 queue is idle.

## Row 14. `hybrid_segmentor` (P329), wave 3
- Vendor the Lightning model class only (MIT); backbones read from the source (not named on the README); our trainer. 5 build h; 1.5 + 15 GPU-h. Lowest prior of the coded crack rows.

---

## GPU and build totals

| Tranche | Rows | Build h | GPU-h (2-seed screen + pathfinders) |
|---|---|---|---|
| 1 | A0, 1, 2, 3, 4, 5 | 5.3 | about 57 |
| 2 | H1, 6, 7, 8, 9, 10 | 14.1 | about 86 |
| 3 | 11, 12, 13, 14 | 11.4 | about 55 |
| All | 16 items | 30.8 | about 198 |

Table entries need seeds 7 to 9 later: about +1.5 x each row's screen. Legacy-test and E1 runs for the final table are a separate, locked step (PROTOCOL 6).

## What the lead must decide (S)
1. Tranche 1 now (5.3 build h, about 57 GPU-h): A0 is free and decides how four stride-4 rows are read.
2. The shared `bench_vendored` registry (1.5 h) unlocks six rows; it should be built once by the harness builder, with the flag-off identity check.
3. G-MAMBA is an install in an isolated venv (approved pattern). If it fails, the suite has no Mamba row with code that runs on our stack; PV-MambaSeg has no code; say so in the benchmark.
4. Suite rows must dump `logp` on the held-out fold (about 1 GB per run, E dump test 976 MiB) for H1.
5. Weight licences to confirm before a public release: MiT (NVIDIA), timm HRNet; none is gated.
