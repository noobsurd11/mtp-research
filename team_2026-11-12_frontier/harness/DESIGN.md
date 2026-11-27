# Benchmark harness: survey and design (harness, 12 Nov 2026)

Read-only survey of gaint plus the local team files. Tags: **E** = measured in a file or by a read-only command (path given), **S** = my judgement. Line numbers refer to the `el_f3` snapshot in `harness/src_snap/` (copied from gaint by `tar` to stdout, source only). Running notes: `harness/notes.md`.

Nothing was started, installed, written or killed on gaint. No stdout, metrics, rescore or results JSON was opened.

---

## 1. What exists (E)

### 1.1 Branches and which tree is most complete
- `git log` on gaint: `main 24590fb → p13 → p17 → sk1 → m 1be64e1 → f1 → f2 → f3 e544133` is one linear chain. `thin c9bbb02`, `f8 c280e8c`, `hc c2e6973` and `hc2 0405151` are siblings branched at e544133 (`git merge-base f8 thin` = e5441339). No branch merges them. `p14` (tol_dice, be67787) and `p16` (d51b60f) are not in f3.
- `git diff --stat main f3`: 33 files, +3,749 / −26 (PF, CP, MIM/DDeP pretrain, encoder/decoder init, grad-norm log, ignore value, upsample_input, absh, SSL split).
- `f3..thin`: 19 files, +1,639 (`src/losses/thin_crack.py` Skeleton Recall + clDice, `src/data/skeleton.py`, `thin_targets.py`, scuff class B3, trainer and train.py hooks).
- `f3..f8`: 4 files, +386 (`src/models/hrstem_unetpp.py`, factory entry, `reports/enc_cosine_hr.py`, tests).
- `f3..hc2`: 11 files, +2,389 (synthetic half-cut transform and its two inactive keys).
- **Most complete: `el_f3` e544133** (base of every 100% run since 30 Oct; B6 and SKR2C used it). thin and f8 add the only loss and architecture extensions; each was CPU-identity-tested against e544133 with its flags off (handbook 14 §1.2d).

### 1.2 Entry point and config system
- `scripts/train.py` (553 l.). `--config` YAML, `--opts k.a.b=v ...`, `--resume`, `--overwrite`, `--exit_after_step`.
- `apply_opts` l.92-101: dot path, missing dicts created, value parsed by `yaml.safe_load`. `load_config` (`src/utils/config.py` l.12-41) resolves `defaults: [base]` with a deep merge (l.60-71; the docstring says shallow, the code is deep).
- `configs/base.yaml` holds old-era defaults (unetpp, weighted_ce, batch 4, labeled_fraction 0.2). Every P6+ run overrides them; the 100% recipe is the `pf2_jobs.txt` opts string (210d0d6f). New keys are opt-in and never written to base.yaml, so old configs stay resumable.
- Run dir `experiments/<run_name>/`: `config_used.yaml` (l.235-237), `train.log`, `metrics.json`, `checkpoints/{latest,best}.pth`.

### 1.3 Model factory (`src/models/model_factory.py`, 100 l.)
- `model.name`: `unetpp` / `sa_unetpp` (from scratch, l.53-65), `smp_unet` (VGG16, l.67-75), **`smp_unetpp`** (house, `encoder_name` default resnet34, `encoder_weights` imagenet, `in_channels` 1, l.77-87), `deeplabv3plus` (l.89-95). `model.upsample_input` wraps any model (l.13-32).
- f8 adds `hrstem_unetpp` (factory l.89-93): a timm backbone via `forward_intermediates` + a stride-2 conv stem + smp's `UnetPlusPlusDecoder` (`hrstem_unetpp.py` l.73-121); weights from a timm file or a torchvision ConvNeXt state dict; 1-channel stem by RGB sum.
- `model.encoder_init` / `decoder_init` copy weights after the build (train.py l.263-268, `encoder_init.py`).
- **Adding a model today:** a new `if name == ...` branch in `_build_core` plus an error-message edit, in a new worktree. Parameter naming matters: `training.encoder_pf` splits groups on the `encoder.` prefix (train.py l.117-123).

### 1.4 Losses (`src/losses/loss_factory.py`, 96 l.)
- `loss.supervised`: `ce`, `ce_dice` (house: CE + batch soft Dice on `dice_classes` (14, 11), `dice_weight` 1.0; `ce_dice.py` l.10-50, ignore 255), `weighted_ce`. Consistency: `none`, `confidence_ce`, `tolerant_pl`, `class_threshold_ce`, `semi_ce` (l.67-94).
- thin adds `loss.skel_recall.weight` / `loss.cldice.weight`, wrapping `ce_dice` in `ThinCrackLoss` (thin `loss_factory.py` l.66-78).
- **Call signature:** `sup_criterion(logits, masks)` (trainer l.466-473). The only extra-target path is thin's `tube=batch["skel_tube"]` (thin trainer diff at f3 l.465).

### 1.5 Optimizer, schedule, EMA
- `build_optimizer` (train.py l.108-131): adam (house), adamw, sgd. PF: two groups split on `encoder.`, group 1 lr × `lr_mult`, own wd (l.113-123).
- `build_lr_lambda` (trainer l.85-107): warmup then cosine, constant, poly. PF multiplier: freeze then linear ramp (l.109-127). `LambdaLR` stepped per optimizer step (l.240, l.521).
- bf16 autocast (l.395-396), grad clip 1.0 (l.503-506), deterministic cuDNN, `CUBLAS_WORKSPACE_CONFIG` (train.py l.33).
- **EMA weights exist only for Mean Teacher** (`teacher` deep copy + `EMAUpdater`, l.262-265; `eval_model` = teacher if SSL, l.383-384). A supervised run has no EMA.

### 1.6 Data and augmentation
- `build_benchmark_data` (train.py l.325-476) reads `<data.root>/splits/{train,val,test}.txt` (l.330, l.346-353), images `<root>/labeled/images`, masks `<root>/<data.mask_subdir>` (l.333). Log line `Labelled: N (...)  unlabelled: ...  val: n  test: n` (l.390-391): the queues' start check.
- `BenchmarkELDataset` (`src/data/benchmark_el.py`): grayscale uint8 (H, W, 1), index mask int64 with value check 0..23 (or `ignore_value`), Albumentations on image + mask, returns `image`, `mask`, `stem`.
- Label-safe pipeline (`augmentations.py` l.115-139): resize, h/v flip, rot90, brightness/contrast ±0.2 (p 0.4), normalise mean 0.5 std 0.25. Eval: resize + normalise (l.62-74).
- `BatchStream` (`src/data/stream.py` l.128-152): every batch is a function of (seed, stream id, index), so resume and worker count do not change batches.
- **The trainer evaluates `splits/test.txt` at the end of every run** (trainer l.858-866, and again from best.pth l.867-877). The data-root trick (test.txt = held-out list) keeps sealed cells out.

### 1.7 Checkpoints
- `latest.pth` every `checkpoint_every` (2,000) and at the end (l.843-847): `{"format", "step", "cfg", "models": {"model", ["teacher"], ...}, "optimizers", "schedulers", "scaler", "rng", "trainer", ...}` (l.691-715). `best.pth` = eval weights at the best val defect mIoU (never used for reported numbers). One R34 run dir on gaint is 499 MB (`du`, `cv02_noob_el/el_b6/experiments/b6_SUP_f0_s5`).

### 1.8 Scorers (local copies; md5 prefixes)
| Scorer | Input | Output | Notes |
|---|---|---|---|
| `rescore_label_versions.py` 1e41202b (`scripts_gaint/`) | run names under `ROOT/experiments`, `data/splits/<split>.txt`, GT `data/escdd_masks/<split>` and `masks_coded` | JSON `split/run` → `old_20211104` / `new_escdd` → crack / inactive → iou, P, R, AP (1,000 bins), rel P/R/F1 at 1 and 2 px | CUDA and `data/` hard-wired (l.32-33, l.68); crack + inactive only |
| `m0_audit.py` d36f7438 (`team_2026-10-24_go/trackM/scripts/`) | `--code`, `--runs <dir>`, sets val / test / ext | per run JSON `cells/<set>/<stem>` = m0 record: `conf` 24×24, `crack_rel2` [pred px ≤2 px of GT, pred px, GT px ≤2 px of pred, GT px], `crack_cc`, `inact_cc` ([size, hit] per component), `crack_pband_gt/neg` (5 bands), `crack_h1000_pos/neg` | asserts step 20,000; builds with `encoder_weights=None`, drops `encoder_init`; bf16 batch 8; val also dihedral-8 TTA; ext uses the ignore mask |
| `m0_analyze.py` d5adbe6b | m0 JSONs | pooled per-class IoU / P / R, `miou_rob` (classes with GT in ≥ 3 cells), `miou_fix`, `miou24`, relP2 / relR2 / relF1, `cc_rec50_20`, `cc_recany_20`, `cc_prec_20`, `in_cc_rec50` (≥ 100 px), `in_cc_prec`, subsets all / -noisy / -twins, per source = stem prefix | aggregation only, CPU |
| `m0_audit_tau.py` d77241bb (`team_2026-10-29_features/scripts/score/`) | as m0 | as m0 (+ tau variants) | frozen opening scorer |
| `b6_score.py` 981b5f29 (`team_2026-10-31_next/scripts/b6/`) | run dirs + held-out stem files, forbidden list (md5 pinned), folds file | `<run>.b6.json`, m0 schema | `comps`, `BANDS`, `cell_stats`, `dihedral`, `predict` line-identical to m0_audit_tau; GT from the run's own `data.root`; `--device`. **GPU bf16 reproduced the opening-1 m0 val block 54/54 cells exactly**; CPU fp32 differs (inactive IoU +0.0034) (build_b6 §5.3, §9) |
| `calib_dump.py` c172717e + `el_metrics.py` 6e73ff11 (B5; `ideas/scripts/frozen_pf2/`) | npz per model × set: `stems`, `margin` f16 (log p_crack − max other log p), `oth` u8 (argmax of the 23 non-crack classes), `pc` f16 | per-cell records at every crack bias b in −4..+12; operating point chosen on val only; cell-level AUROC; inactive area error | the only existing dump format; self-check vs m0 at b = 0 with tolerance 0.0005 (bf16) |
| `e1_task_metrics.py` 839789f4 (`scripts_cv02/`) | runs, test + ext117 | per cell crack counts, relaxed hits (only when GT crack exists), skeleton lengths (skimage), inactive areas | superseded by m0's `ext` set for pixel metrics |
| `b6_verdict.py` 6d807784 | 20 b6 JSONs, folds, groups | pooled OOF IoU, two-stage paired bootstrap (334 module groups, then seed per fold × arm), 2,000 resamples | stdlib only |
| `scripts/ssl_rules.py` | rescore JSONs | rule R1: Δ > max(0.01, 2·√((sd_A²+sd_B²)/3)) | local |

### 1.9 Launch, queue and guard scripts (all in `team_2026-10-31_next/scripts/`)
- `pf2/gpu_gate.sh` 00fabfdd (24 l.): `gate_wait` / `gate_try MIB LABEL` under `flock /home/noob/work/gpu_gate/gate.lock`: free ≥ MIB and ≥ 120 s since any start, stamps `last_start`, logs `gate.log`; a `HOLD` file stops new starts.
- `s2c/s2c_lib.sh` 4edcae9e (69 l.): `SMI` = `timeout 5 nvidia-smi`; `verify NAME PID` (alive, not 6206, owner noob, live cmdline equals the one recorded at launch, holds `scripts/train.py` and `run_name=NAME`); `stop_verified` (SIGTERM, ≤ 30 s, re-verify, SIGKILL); `outside` (non-ours compute apps > 1,024 MiB); `prestart`; `startcheck` (first `Labelled:` line); `launch_run` (python started as a plain background command so the pid file holds the python PID; rc written by the subshell after `wait`).
- `s2c/s2c_queue.sh` de31c533: jobs file md5-pinned; data-root re-check (SPLITS.md5, test = val, link target); deploy check (HEAD, clean tree, REVISION); MAXC file; per start prestart → MAXC → `gate_try` → HOLD re-check → launch → cfgcheck (config diff vs a reference = expected diff file) → startcheck; mismatch → HOLD + `stop_verified`.
- `s2c/s2c_guard.sh` 334742d6: 1 s samples; free < 2,048 MiB on 3 consecutive samples → HOLD, stop the newest verified own run; second stop only on a fresh trigger ≥ 30 s later; cap 2; 10 failed reads → HOLD. `s2c_gpumem.sh` 06791cdd: 1 s log.
- `b6/b6_cv02_queue.sh` 56f9e72d: lanes on qualifying GPUs; `lane_ok` = no non-ours compute process > 4,096 MiB on that GPU (shared account: anything not in `pids/` or their children), < LPG of ours, free ≥ gate; ≥ 120 s; cfgcheck + databuild lines vs `exp/<arm>_f<k>.txt`. Its pid files held the subshell PID (fixed in s2c's `launch_run`).
- `b6/b6_make_roots.py` fe70fbaf (roots + manifests + forbidden list), `b6_relay.sh` a23ab50d (cv02 → laptop tar stream → gaint, RELAY.md5 checked both ends, refuses to overwrite), `b6_score_gaint.sh` e6f1259d.
- Measured peaks (handbook 14 §1.2d-e; MiB): R34 fine-tune 6,826-6,830; SKR 7,020; CLD 8,374; hrstem ConvNeXt-T / Hiera-T (A8) 9,254; RN50-PF 11,186; m0 scoring 4,002-5,254; LA 7,758; b6 scorer 3,292; root finllm 5,876. Speed: one R34 alone 5.6-7.1 steps/s, 3 at once 2.25 each (gaint).

### 1.10 gaint state now (read-only queries, 12 Nov)
- GPU: 2,787 MiB free of 32,623 (finllm PID 6206 5,876 MiB; `llama-server` from `/home/noob/.local/src/llama.cpp`, 22,382 MiB). **No training or GPU scoring can start until the llama-server is stopped by the user.**
- Disk `/`: 250 GB free of 1.6 TB.
- House venv: Python 3.12.3, torch 2.14.1+cu130, torchvision 0.29.1, timm 1.0.30, smp 0.5.0, albumentations 2.0.8, numpy 2.5.2, scipy 1.18.1, scikit-learn 1.9.1, opencv-headless 5.0, safetensors 0.8.0, einops 0.8.2. Absent: scikit-image, transformers, monai, nnunetv2, mmcv / mmseg.
- smp 0.5.0 ships decoders `unet unetplusplus fpn deeplabv3 pspnet linknet manet pan upernet segformer dpt`, encoders incl. `timm_universal` (tu-*), `timm_vit`, `mix_transformer`, and losses `dice focal jaccard lovasz tversky soft_bce soft_ce mcc`.
- timm 1.0.30 has DINOv3 ViT S/B/L/H+/7B (`eva.py`), DINOv3 ConvNeXt T/S/B/L (`convnext.py`), SAM2 Hiera, Swin v1/v2, MambaOut, `param_groups_layer_decay`, `ModelEmaV3`.
- Local weights `/home/noob/work/weights/` (MD5SUMS): SAM2.1 Hiera-T (Meta and timm formats), DINOv3 ConvNeXt-T, DINOv3 ViT-S/16. HF cache: smp-hub resnet34 / resnet50 / vgg16. torch hub: torchvision `convnext_tiny-983f1562.pth`, `dinov2_vits14_pretrain.pth`, `resnet50-11ad3fa6.pth`.
- `venv_sam2`: its own venv with `zz_reuse_el_venv_readonly.pth` (adds the house site-packages, so torch is shared read-only) and `found_sam2_src.pth` (SAM2 source at 2b90b9f). This is the pattern for every new venv.

---

## 2. Gaps for a benchmark

| Need | Gap (E) | Change (S) |
|---|---|---|
| (a) other smp decoders | factory hard-codes Unet / Unet++ / DLV3+ names (l.67-95) | one generic `bench_smp` entry: `decoder` ∈ smp's 11 classes, `encoder_name` passed through; 1-channel by smp; keep `encoder.` prefix for PF |
| (a) timm encoders (ConvNeXt, Swin, Hiera, MiT, ViT DINOv2 / DINOv3) | only f8's `hrstem_unetpp` (ConvNeXt / Hiera + Unet++); Unet++ needs a stride-2 skip that these backbones lack (hrstem docstring l.15-16) | generalise f8's `build_backbone` (local weight files, RGB-sum stem, `prune_intermediate_layers`) into `bench_timm`: stride-4 decoders (UPerNet, FPN, SegFormer head) direct; Unet / Unet++ via the HR stem; plain ViTs (DINOv2 / DINOv3) via smp DPT or a ViT-Adapter-style neck. Patch 16 at 512 px gives 32×32 tokens: thin cracks need the HR stem or a high-res branch (S) |
| (a) memory for large backbones | batch 8 at 512 px; no grad accumulation, no activation checkpointing for smp / timm models | add `training.accum_steps` (sample budget fixed: 20k × 8 images) and timm `set_grad_checkpointing` |
| (b) Lovasz, Jaccard / Tversky / focal | not in loss_factory | wrap `smp.losses` (present in smp 0.5.0) as `loss.supervised=composite` with a list of terms {name, weight, classes}; keeps `ce_dice` byte-identical when unused |
| (b) Jaccard metric loss (soft labels), boundary / distance losses, cbDice, topology losses | none (clDice and Skeleton Recall exist in el_thin only) | port thin's `ThinCrackLoss` and its `tube` plumbing; generalise to `batch["aux"]` dict of precomputed targets (distance maps, skeletons) built by a dataset target hook; losses declare which aux keys they need |
| (c) AdamW, LLRD, EMA | AdamW exists (l.126); no layer-wise decay; no EMA for supervised runs | `training.param_groups=llrd` using timm `param_groups_layer_decay` on `encoder.*` (PF becomes a special case); `training.ema.decay` for supervised runs, saved as `models.ema`, dump picks the weights key declared in the method card |
| (c) other schedules | cosine / constant / poly only | add `cosine_restarts` only if a paper needs it (S) |
| (d) multi-label heads | 24-way softmax everywhere; mask check 0..23; `evaluate_model` uses argmax | `model.head=multilabel` with K sigmoid channels, a target hook (multi-hot from the index mask + derived targets), BCE + Dice loss, and a declared **decision rule** (sigmoid → single-label map, e.g. priority crack > inactive > argmax rest) used by both the in-training eval and the dump |
| (e) codebases with their own trainer (nnU-Net v2, Mask2Former, SAM 2, crack repos) | nothing: the scorers load our checkpoints through our factory (m0 l.150-155) | they never touch our trainer: harness exports the data (§4), they train, then write **dumps** (§3) through a numpy-only writer; one scorer reads every dump |
| Sealed sets | guards are scattered (calib_dump `--opening`, b6 forbidden list, data-root trick) | one guard in the dump writer and the infer script: `test50`, `e1_106` refused without `--opening <protocol>`; forbidden list md5-pinned |
| End-of-run TEST pass | trainer always scores `splits/test.txt` (l.858-877) | keep the root trick for every harness run (test.txt = held-out set); set `val_every = total_steps` so best.pth is written once and not used |
| Code layout | each extension lives in its own worktree; thin and f8 are siblings | new worktree `el_bench` from e544133 with thin + f8 cherry-picked (CPU identity per flag-off arm, §7) |

---

## 3. The unifying piece: prediction dumps and one frozen scorer

### 3.1 Dump format (one file per cell; numpy only; any codebase can write it)
Path: `<DUMPS>/<bench>/<method>/<run_id>/<set>/<cell_id>.npz` (`np.savez_compressed`), `cell_id` = image stem (`CSIR_00070_r8_c4`), source = stem prefix.

| key | dtype, shape | meaning |
|---|---|---|
| `pred` | uint8 (512, 512) | the method's final class map at its declared decision rule (argmax over 24 for softmax heads). Authoritative for every argmax metric |
| `oth` | uint8 (512, 512) | argmax over the 23 non-crack classes (as calib_dump), so crack-bias sweeps are exact |
| `m_crack` | float16 (512, 512) | log s_crack − max_{k≠crack} log s_k (calib_dump's margin) |
| `p_crack`, `p_inact` | float16 (512, 512) | per-class score in [0, 1] (softmax; sigmoid for multi-label; Mask2Former semantic score) |
| `logp` (optional) | float16 (24, 512, 512) | only for runs marked for ensembling / 24-class bias studies, and only on val / dev sets |

- Per run: `<run_id>/manifest.json` = method, run_id, seed, split definition name + md5, fold, set names, code repo + commit, venv, checkpoint path + md5 + step, weights key (model / ema / teacher), device, precision, TTA flag, decision rule, writer version, per-file md5 (`MANIFEST.md5`).
- Sets: `val54`, `cv5v1_f{k}` (held-out fold k of split def `cv5v1`), `f51`, `h36`, sealed `test50` and `e1_106`. Fold and split live in the set name and the manifest, never in the file name.
- Writer checks (in `bench/dumpfmt.py`, numpy only): shape 512×512, pred < 24, `pred == where(m_crack > 0, 14, oth)` except where |m_crack| < 2⁻¹⁴ (float16 ties; count logged), stem in the set list, sealed set guard.
- Size (S, to measure at milestone 1): pred + oth compress to tens of kB; three float16 maps ≤ 1.5 MB raw, about 0.5-1 MB compressed; a 107-cell fold ≈ 50-100 MB; 450 runs ≈ 25-45 GB of the 250 GB free (E). `logp` is 12.6 MB raw per cell, so it stays optional.
- Precision (S): canonical dumps in **fp32 on GPU with TF32 off**, which removes most of the bf16 device dependence (B6 measured bf16 vs fp32 at up to 0.0046 on pixel metrics, 0.0069 inactive IoU; handbook 14 §1.2d). bf16 mode is kept only for the identity check against the legacy m0 files. All runs of one comparison use one precision and one device type (recorded; the scorer refuses mixtures inside a comparison).
- TTA off for the primary. External codebases must disable their own TTA (nnU-Net mirroring) for the primary; TTA is a separate, labelled column.

### 3.2 The scorer `bench_score.py` (CPU, numpy + scipy; runs on gaint CPU or the laptop venv)
- **Built from:** `cell_stats`, `comps`, `BANDS` copied line-identical from `m0_audit.py` d36f7438 (= m0_audit_tau d77241bb = b6_score 981b5f29; checked by AST extraction as build_b6 §5.1 did); aggregation from `m0_analyze.agg` d5adbe6b; crack-bias sweep and val-only operating points from `el_metrics.py` 6e73ff11 (`cell_record` on `m_crack` / `oth`); bootstrap from `b6_verdict.py` 6d807784 and `scripts/per_image_analysis.py`; R1 from `ssl_rules.cmp`.
- **GT:** one source, `<labeled>/masks_escdd/<stem>.png` for the 582 cells (val masks byte-identical to `escdd_masks/val`, build_b6 §5.1; gaint's own `escdd_masks/test` has scuff at 2 cells, handbook 14 §1.2b, so it is not used); E1: `el_f1/reports/f1/ext117/{masks,ignore}`; rf: `calib/data/rf/{masks,ignore}`. GT md5 manifest pinned.
- **Per-cell record = the m0 schema** (so every old analysis runs unchanged), plus `inact_rel2` and bias-sweep counts when `m_crack` is present.
- **Fixed metric list** (written into the benchmark definition before any number):
  - per class (24): pooled IoU, P, R, GT px, GT cells;
  - `mIoU_rob` over the fixed 13 classes {0, 1, 2, 4, 5, 7, 11, 13, 14, 15, 16, 20, 21} (Track M list, used for every set; a class with no GT in a subset is NaN and named), `mIoU_rob_no07`, `mIoU_fix` (15);
  - crack: IoU, P, R, relP@2, relR@2, relF1@2, component recall (GT ≥ 20 px, ≥ 50% within 2 px), any-hit recall, component precision; binned AP and the bin-0 share;
  - inactive: IoU, P, R, component recall (≥ 100 px, ≥ 50% covered) and precision;
  - absent-class FP px;
  - optional operating point: crack bias chosen on val (legacy split) or by cross-fitting on the other four folds (CV), never on the scored set.
- **Subsets:** all; without the noisy cell list (`CSIR_00070_r8_c4` on test; a list fixed per set); without twins; per source (ARTS, BMRK, CFVS, CSIR, SDLE).
- **Uncertainty:** test: paired cell bootstrap (2,000). CV: two-stage paired bootstrap over the 334 module groups of `b6_groups.tsv` (5ff33e20), then seed per fold × arm (b6_verdict). Seed rule R1 as `ssl_rules.cmp`.
- **Asserts:** manifest md5s; one precision, device type, scorer md5 and split md5 per comparison; dumped cell set == the set's stem list; no forbidden stem; step and weights key as declared.

### 3.3 Identity checks (the scorer must reproduce existing numbers exactly)
- **I1a (CPU, possible today):** `bench_infer --precision fp32 --device cpu` on `f3_SUPPF_100pct_s0`, val 54 → `bench_score` records must equal b6's CPU check record (`/home/noob/work/b6_build/check/out_cpu/f3_SUPPF_100pct_s0.check.json`, 1ee0b18d per build_b6 §5.3) field for field.
- **I1b (GPU, when free):** the same in bf16 on gaint → equal to the opening-1 m0 **val block** 54/54 (as `b6_valcmp.py --expect exact` did; only `cells.val` is indexed).
- **I2 (house OOF, GPU bf16):** `b6_SUP_f0_s5` (relayed, `cv02_noob_el/el_b6/experiments/`) on fold 0 → equal to its `b6_score` record (`/home/noob/work/b6_score/out/b6_SUP_f0_s5.b6.json`). Compared by script; no number printed.
- **I3 (dump format round trip):** records from `pred` alone equal records from `where(m_crack > 0, 14, oth)` except the logged float16 ties.

---

## 4. Data roots and split definitions

### 4.1 What is on gaint (E)
- **Legacy split:** each worktree's `data/` = symlinks: `labeled` → `el-fault-detection/data/labeled` (`images` 582, `masks_escdd` 583 files, `masks_coded`), `escdd_masks` → `el_f1/data/escdd_masks` (per-stem links to `labeled/masks_escdd`), `unlabeled`; `splits/{train,val,test}.txt` 478 / 54 / 50 (md5 842f27c4 / 9dcccf00 / a31fad14), `splits/seed{0,1,2}/labeled_<P>pct.txt`, `external_unlabeled.txt`.
- **5 fold roots** `/home/noob/work/b6/b6_root_{0..4}`: `labeled` symlink, `splits/train.txt` (the other 4 folds, 425-426), `val.txt` = `test.txt` (fold k, 106-107), `SPLITS.md5`, `DATA_MANIFEST.md5` (1,064 lines, 2630f630); `b6/ROOTS.md5` e4100381, `b6_forbidden.txt` 9bb4d919 (test 50 + ext117 117). Folds group cells by physical module (334 groups, none split; `b6_folds.tsv` e2cafce1).
- Other roots of the same pattern: `a8_root`, `s2c_root` (train 478, val = test = real val).
- E1: `el_f1/reports/f1/ext117/` (images, masks, ignore, `stems_eval.txt` 106). `/home/noob/work/ext117/` has no `stems_eval.txt`. rf (F51 / H36): `calib/data/rf/` (images, masks, ignore, `stems_eval.txt`, `rf_context.tsv`).

### 4.2 Adding a split without copying images (S)
- A split definition is one file `bench/splits/<name>.json`: name, version, pool source + DATA_MANIFEST md5, the forbidden list md5, and for each fold or set the train and held-out stem lists (order rule as b6). Committed and md5-pinned before use.
- `bench_make_roots.py` (generalised `b6_make_roots.py` fe70fbaf, same asserts: no group split, 0 forbidden stems, held-outs partition the pool, re-read after write, refuse to overwrite) writes `<ROOTS>/<name>_f<k>/` = `labeled` symlink + `splits/{train,val,test}.txt` (val = test = held-out) + `SPLITS.md5` + `DATA_MANIFEST.md5`. The trainer needs no change (it reads only `<root>/splits/*.txt` and `<root>/labeled/...`; train.py l.329-353).
- External codebases get the same split through an exporter (`bench_export.py --to nnunet|hf|mmseg`): symlinked or converted images, and the fold lists written in their format (nnU-Net `splits_final.json` with our 5 folds; never its own random split).
- On cv02 a root gets a fresh `labeled/` holding only the pool stems (b6 deploy rule), so sealed images never reach cv02.

---

## 5. Run management

### 5.1 gaint launcher (`bench_q.sh`, from s2c v3)
- Queue dir `/home/noob/work/bq/<batch>/`: `jobs.tsv` (md5-pinned; `name|machine|worktree|python|cmd|gate_MiB|check`), `MAXC`, `HOLD`, `pids/`, `launch.log`.
- **Reuse unchanged:** `gpu_gate.sh` (flock gate, free ≥ gate, ≥ 120 s since any start by anyone, HOLD), `s2c_guard.sh` (free < 2,048 MiB on 3 consecutive 1 s samples → HOLD, stop only the newest verified own job, cap 2), `s2c_gpumem.sh`, `stop_verified`.
- **Generalise:** `launch_run` takes any command (house trainer, nnU-Net, HF trainer) and a verify token (`run_name=NAME` or `--bench-run NAME`), still starts python as a plain background child so the pid file holds the python PID; `verify` checks that token instead of `scripts/train.py`; `rc=$?` right after `wait`, before any `$(date)`; done line with grep counts of the final-step line and `Traceback` (never reading the stdout further).
- **Start gate per job = max(smoke peak, last real peak) + 2,048 MiB**, from a 1,000-step smoke with the 1 s logger (nvidia-smi per process, includes the CUDA context). Dump passes get their own gate.
- **Live check** per job type: house trainer = cfgcheck (config diff vs the method card's expected diff) + `Labelled:` line; external = a `BENCH_START <json>` line the adapter prints (split md5, fold, seed, commit), compared with the job line.
- **Other people's processes:** `prestart` keeps s2c's rule as an option (`OUTSIDE_MIB`, default 1,024: new starts wait while a non-ours process > 1 GB is present). Today that blocks everything: llama-server (22.4 GB, the user's) is such a process.
- tmux: one session per batch, always addressed as `-t "=bq_<batch>"`; `tmux has-session -t "=bq_<batch>"` before creating. Stops only by recorded python PID via `stop_verified`; never pattern kills.
- Scoring: CPU only (`nice -n 19`, ≤ 8 threads, `CUDA_VISIBLE_DEVICES=""`), so it never competes for GPU memory.

### 5.2 cv02 (S; not reachable by me; from b6)
- Deploy: `git archive <bench commit>` + `CODE.md5` to `/tmp/noob_el/bench_<commit>/`; roots with a fresh `labeled/` of the pool stems only; DEPLOY.md5 both ends. House venv `/tmp/noob_el/el-fault-detection/.venv` (B6 ran e544133 on it); new venvs under `/tmp/noob_el/venvs/<name>` built from a pinned lock file, rebuilt after any wipe.
- Queue: `b6_cv02_queue.sh` lanes (`lane_ok`: no non-ours process > 4,096 MiB on the GPU, < LPG of ours, free ≥ gate, ≥ 120 s between starts) with s2c's `launch_run` (python PID, not the subshell). One GPU set per comparison.
- After each run: dump on the same GPU (own gate), write `RUN.md5`, then relay **per run** (not per batch) through the laptop with `b6_relay.sh`'s tar stream and md5 on both ends to gaint `/home/noob/work/bench_relay/<batch>/`. Relay a slim checkpoint (`models.*` only, no optimizer) + config + train.log + dumps; keep the full `latest.pth` on cv02 until the relay is verified. The laptop must stay on; it is the only bridge (gaint has no key to cv02 by design, handbook 14 §1.2d).
- Machine rule: seeds and arms of one comparison on one machine. The house reference is trained on every machine that hosts arms (S: one house run per fold × seed on each).

---

## 6. Packages and weights (nothing installed)

| Family | Need | Status / version (E = present) | Venv |
|---|---|---|---|
| smp decoders (Unet, Unet++, FPN, DLV3+, PSP, Linknet, MAnet, PAN, UPerNet, SegFormer, DPT) and losses | smp 0.5.0 | E present | house |
| timm backbones (ConvNeXt, Swin, Hiera, MiT via smp, DINOv2, DINOv3 ViT / ConvNeXt, MambaOut), LLRD, EMA | timm 1.0.30 | E present | house |
| Weights: ImageNet R34 / R50 (E), torchvision ConvNeXt-T (E), DINOv2 ViT-S/14 (E), DINOv3 ConvNeXt-T, ViT-S/16 (E), SAM2.1 Hiera-T (E) | larger DINOv3 (ViT-B/L, ConvNeXt-S/B/L) | DINOv3 downloads are licence-gated (Meta); user's OK needed. DINOv2 B/L, smp-hub `mit_b*`, SAM2.1 S/B+/L: public downloads (unverified for each URL) | files |
| skeletons / E1 lengths | scikit-image | absent on gaint (E); laptop venv has 0.26.0 (handbook 14 §1.1b) | scorer can avoid it |
| nnU-Net v2 | `nnunetv2` (current 2.x) + its pins (dynamic-network-architectures, batchgenerators, acvl-utils, SimpleITK) | absent; torch 2.14 compatibility unverified | **separate venv** sharing torch via a `.pth` (venv_sam2 pattern) |
| Mask2Former / UPerNet-Swin / HF DINOv3 | `transformers` (a version with DINOv3 and Mask2Former; exact version unverified) | absent; pure PyTorch (deformable attention has a PyTorch path) | separate venv sharing torch |
| mmsegmentation | mmseg 1.2.x + mmcv 2.1 + mmengine | absent; mmcv needs compiled ops and has no wheels for torch 2.14 / CUDA 13 (S) | avoid unless one method needs it; prefer the HF port |
| SAM 2 fine-tuning | facebookresearch/sam2 | E present: `venv_sam2` + src 2b90b9f | existing |
| Medical / topology losses (optional) | monai | absent; pure Python | house or separate |
| Mamba segmenters | `mamba_ssm`, `causal_conv1d` | absent; CUDA builds on cu130 high risk (S) | separate, only if a card needs it |

Separate venvs (S): yes for anything that pins numpy, torch or huggingface_hub (nnU-Net, transformers, mmseg). The house venv is shared by every frozen deploy; changing it could break bit-identity of old runs.

---

## 7. Implementation plan (S; hours are build time, not GPU time)

| # | Step | h |
|---|---|---|
| 1 | Worktree `el_bench` from e544133; cherry-pick thin (9461ecc..c9bbb02, code only) and f8 (063f74f..c280e8c); suites; CPU identity 5 steps with `identity_cpu.py` 962379a6: house and PF vs e544133, SKR01 vs c9bbb02, A8 vs c280e8c → IDENTICAL | 3 |
| 2 | `bench/dumpfmt.py` (numpy only), `scripts/bench_infer.py` (from b6_score `predict` + calib_dump margin; weights key; sealed-set guard; fp32 / bf16; device) | 3 |
| 3 | `scripts/bench_score.py` (m0 `cell_stats` line-identical, `agg`, el_metrics sweep, bootstrap, R1); AST identity test vs m0 | 4 |
| 4 | Identity I1a (CPU, now), I3; I1b and I2 when the GPU is free | 2 |
| 5 | Model registry + `bench_smp` / `bench_timm` (stride-4 decoders, HR stem for Unet / Unet++, DPT for ViT); CPU build tests (params, 1-channel stem = RGB sum, `encoder.` prefix) | 4 |
| 6 | `bench_q.sh` from s2c v3 (generic command, verify token, per-job gate) + dry tests with dummies (reuse s2c dry harness) | 4 |
| 7 | **Milestone 1** (below) | 2 + GPU ~3 h |
| 8 | Losses: composite smp losses, JML, boundary; `batch["aux"]` target hook | 4 |
| 9 | AdamW + LLRD, supervised EMA (`models.ema`), grad accumulation, grad checkpointing | 3 |
| 10 | `bench/splits/*.json` + `bench_make_roots.py` (from b6_make_roots) | 2 |
| 11 | cv02 deploy, queue, per-run dump + relay (from b6) | 4 |
| 12 | nnU-Net v2 adapter: export, `splits_final.json`, step-matched and default-budget trainers, `--save_probabilities` → dump converter | 8 |
| 13 | HF Mask2Former / UPerNet wrapper (own-loss interface `model.loss(images, batch)`) | 6 |
| 14 | Multi-label head + decision rule | 4 |
| 15 | SAM 2 variants (Hiera + our decoder exists in f8; SAM2-UNet-style adapters) | 6 |

**Milestone 1 (smallest end-to-end):** in `el_bench`, `model.name=bench_timm`, backbone ConvNeXt-T from the local torchvision file (no download), smp UPerNet decoder, house recipe otherwise (ce_dice, Adam 1e-3, 20k steps, batch 8, label-safe aug), `data.root=/home/noob/work/b6/b6_root_0`, seed 5. Steps: (1) I1a / I1b / I2 pass for the house model; (2) 1,000-step smoke with the 1 s logger → gate; (3) one run through `bench_q.sh`; (4) dump fold 0 (fp32); (5) `bench_score` against the house B6 fold-0 records of seeds 5 and 6 dumped the same way. One fold and one seed decide nothing; the milestone proves the path, the gate and the dump size.

**Risks (E where stated):**
- gaint GPU blocked: 2,787 MiB free (E) while the user's llama-server holds 22.4 GB. Training and GPU identity checks wait for the user.
- cv02: 0 of 8 GPUs usable on 30 Oct (E, handbook 14 §1.3b); reachability from the laptop untested since the reinstall (E, §1.1b); `/tmp` wipes; the laptop is the only relay.
- Precision and device move pixel metrics by up to 0.005 and inactive IoU by 0.007 (E, B6). Mixing them inside a comparison would fake effects; the scorer refuses it.
- Budget fairness: external codebases bring their own budgets, crops and TTA (nnU-Net: 1,000 epochs, mirroring). Each needs a step-matched (160k images) row and its native row, both labelled.
- Frozen deploys: nothing may change in `el_f3`, `el_thin`, `el_f8`, `el-fault-detection` or the house venv.
- Disk: 250 GB free (E); R34 run dir 499 MB (E); large backbones several GB per run (S). Delete optimizer state after a verified relay or slim copy (user's OK).
- Class coverage in CV: belt_mark, rings and clamp have no training px in folds 0, 2, 3 (E, build_b6 §3.2); none is in the fixed 13-class list, so `mIoU_rob` is unaffected; per-class tables flag them.
- Package compatibility with torch 2.14 / cu130 is unverified for nnU-Net, transformers, mmcv, mamba.

## Not read / not checked
- cv02 (not reachable, by instruction): venv versions, disk, GPU state.
- Contents of any stdout, metrics, rescore, b6 or m0 JSON (sealed by rule). The identity checks above compare them by script.
- `el_hc`, `el_hc2`, `el_p14`, `el_p16`, `el_m` source beyond `git diff --stat`.
- smp 0.5.0 `tu-*` support for stride-4 backbones inside Unet / Unet++ (f8's docstring says Unet++ fails; plain Unet unverified).
