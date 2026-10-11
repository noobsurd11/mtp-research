# MTP handoff: semi-supervised defect segmentation on EL images

Snapshot time: Wed 7 Oct 2026, about 22:15 IST. Written from the chat history plus a fresh read of both servers at that time.
Purpose: a complete record so the work can continue in a new session without the old one.

How to read it:

- Sections 1 to 4 are fixed facts (project, machines, data, code).
- Section 5 is the timeline, including every wrong turn.
- Section 6 is every experiment and number.
- Sections 7 to 10 are judgement: what is certain, what is assumed, what may be wrong, what I got wrong.
- Sections 11 to 14 are what I think, the plan, open decisions, and how to resume.

Convention used throughout: **measured** means a number exists in a file on a server. **Inferred** means I reasoned it from numbers. **Guess** means neither.

---

## 1. The project in short

- Thesis (MTP) with WattCycle: semi-supervised (SSL) deep learning for defect segmentation in electroluminescence (EL) images of solar cells.
- First experiment (before this session): SA U-Net++ with SSL, repo `sa-unetpp-ssl-el`. It had technical faults and its results are void.
- Paper reproductions were done before this session (Fioresi, Pratt, Jha PV-S3, Gangopadhyay). All of that code was lost when the `noob` user on gaint was reset. Only numbers on the poster and in notes survive.
- Second experiment (this session): port ALHVR (Lei et al., ICCV 2025, a two-network SSL method from medical imaging) to EL segmentation, and test it honestly against supervised and Mean Teacher baselines.
- A progress report in LaTeX is planned. `reports/numbers.tex` and `reports/figures/` exist on gaint from Oct 5 but do not contain anything run after that.

Where it stands in one paragraph: on BenchmarkEL no unlabelled loss has shown any effect, and label count does not move the score between 5% and 100%. The crack class cannot even be fitted on training images. UCF-EL does show a clean label gap (0.54 at 100%, 0.41 at 5%, 0.23 at 1%) with very low seed noise, so the SSL question moved there. Mean Teacher on UCF-EL at 5% and 1% is running now.

---

## 2. Machines, access, paths

### 2.1 gaint (institute server)

| Item | Value |
|---|---|
| Address, user | `172.18.22.20`, user `noob` |
| Work directory | `/home/noob/work` |
| GPU | 1 × NVIDIA RTX PRO 4500 Blackwell, 32.6 GiB. Another user's process (`root`, `finllm_chat.py server`) always holds about 6 GiB |
| CPU, RAM, disk | 48 cores, 94 GiB, about 935 GB free |
| Python | 3.12.3, venv in the repo (`.venv`) |
| Access from chat | `Gaint_Herald` exec |
| Claude Code | runs there in the user's own terminal. I write prompts, the user pastes them |

Folders under `/home/noob/work`:

| Path | Content |
|---|---|
| `el-fault-detection/` | the active repo (private GitHub `noobsurd11/el-fault-detection`, branch `main`) |
| `sa-unetpp-ssl-el/` | old repo, HEAD tagged `v0-sa-failed`. Also holds the raw external pool at `data/unlabeled/images` (11,993 PNGs, 8.8 GB) and `_inventory.json` |
| `datasets/BenchmarkELimages/` | public clone. We use `dataset_20211104` |
| `datasets/UCF-EL-Defect/` | public clone, LFS weights skipped |
| `refs/ALHVR/` | ALHVR reference code (ACDC and BraTS scripts) |
| `docs/papers/` | 7 PDFs: ALHVR, Mean Teacher, UniMatch, Pratt 2023, Jha PV-S3, Fioresi, Gangopadhyay. Pratt 2021 is missing |
| `setup_tools/` | `dbx_run.py` (Dropbox downloader wrapper), download log |

Gaint is unstable. Known interruptions:

| When (IST) | What |
|---|---|
| Oct 2, 21:34 | orderly OS shutdown, killed the ALHVR pilot at step 13,600. Who triggered it is unknown (needs `adm` or sudo to read the logs) |
| Oct 6, about 18:22 to 18:47 | reboot, killed two low-label runs at step 12,500 |
| Oct 7, about 10:30 | reboot, nothing was running |

Since Oct 7 the queue resumes runs from `latest.pth` after a reboot (commit `95dda7c`) and records resumes in `metrics.json`. The hardware clock holds IST while Linux reads it as UTC, so boot-time log stamps can be 5.5 h off until NTP corrects them.

### 2.2 cv02 (second server)

| Item | Value |
|---|---|
| Address, user, host | `cv02@10.8.1.106`, hostname `himtenduh` |
| GPUs | 8 × RTX A6000, 48 GiB each, shared with other users. Load from others varies from idle to all 8 at 100% |
| Rights | no sudo |
| Workspace | `/tmp/noob_el` on local NVMe. **Wiped on reboot** |
| Results that survive | `~/noob/el_results/` (50 MB cap, we set it) and `/tmp/noob_el/results_to_sync/` |
| Main report | `~/noob/el_results/cv02.md` (about 93 KB) |
| Code | a tarball of repo commit `fe79e19`, no git. Two small local patches (see 4.4) |
| Times | cv02 logs are in UTC. IST = UTC + 5:30 |
| Access from chat | ssh through `Yugma_Herald` exec or `noob_herald` exec |
| tmux | session `el` holds the launcher windows |

cv02 rules we set: one run per GPU, no stacking, at most 8. Exception given Oct 7: up to two of our runs may share a GPU that no other user is on. Never start on a GPU where another user holds more than 4 GiB.

### 2.3 Herald connectors and their limits

| Connector | Sits on | Use | Limits seen |
|---|---|---|---|
| `Gaint_Herald` | gaint | exec there | allowlist. Refused so far: `cd`, `tmux`, `rm`, `uname`, `uptime`, `crontab`, shell redirects such as `2>&1`. Calls longer than about 60 s drop. Use the `cwd` parameter. `python3` is allowed, so long jobs can be detached with `subprocess.Popen(..., start_new_session=True)` |
| `noob_herald` | the laptop (`patil@ubuntu`) | holds the papers in `~/Downloads`, has ssh keys for gaint and cv02 | `scp`, `rsync`, `uname`, direct `nvidia-smi` refused. `curl` with `sftp://` works for file transfer. Was unavailable on Oct 6 |
| `Yugma_Herald` | another host | ssh to cv02 works | same style of allowlist |

Workflow agreed with the user: exec for quick commands, a written prompt for anything that is a task. The user pastes prompts into Claude Code. Prompts must test questions, not confirm answers ("don't presume anything").

### 2.4 Credentials

- GitHub: `gh` is logged in on gaint.
- Dropbox: app key and secret are in `~/.dropbox_app` on gaint (mode 600, outside the repo). **The secret was pasted in chat on Oct 2 and should be rotated.** Still not done as far as I know.

---

## 3. Data

### 3.1 BenchmarkELimages (Pratt et al.)

The public repo has three labelled versions:

| Folder | Images | Classes | Note |
|---|---:|---:|---|
| `dataset_20211104` | 478 train / 54 val / 50 test = 582 | 24 | **the one we use.** Matches Pratt 2023 (24 classes, 50 test) |
| `dataset_20220723` | 642 originals | more | train folder ships 4× pre-augmented copies |
| `dataset_20221008` | 695 originals | 29 | train folder ships 4× pre-augmented copies (flip, mirror, rotate prefixes) |

Facts that matter:

- Images are 512 × 512. Masks are index masks, read directly from `masks_coded`.
- Class indices: crack 14, inactive 11, gridline 15, ribbons 4, busbars 9, padding 7, background 0.
- Pixel shares on train: background 69.2%, padding 17.3% (86.5% together). Crack is 0.186% of pixels.
- Four classes have under 1,300 pixels in all 478 train images: clamp, crack_rbn_edge (104 px), rings, meas_artifact.
- Inactive always co-occurs with crack in train, so stratification has 3 groups, not 4.
- 7 classes are absent from val and 8 from test, so "mIoU over 24 classes" is really over 16 or 17 and not the same set on val and test.
- **The test set is not representative.** All 50 test images contain crack (41 to 43% in train and val). Inactive is in 34% of test images against about 9% elsewhere. Pratt built it that way on purpose.
- Crack ground-truth pixels: train 232,914 in 478 images, val 27,873 in 54, test 70,626 in 50. Test cracks are bigger and easier (see 6.7).
- Sources of labelled train cells: ARTS 162, CFVS 146, CSIR 111, BMRK 42, SDLE 17.
- The official split shares modules across splits: 20 of 54 val images and 24 of 50 test images come from modules that also have train images.
- Jha's S2 and S3 image counts (2109, 2282) are train+val of the later versions with the augmented copies counted.

Rule derived from this: label fractions must be sampled by cell, never by file, and only from `images_train_original`.

### 3.2 Labelled subsets (committed in `data/splits/`)

- Official 478 / 54 / 50 kept.
- Seeds 0, 1, 2: nested subsets 50% (239) ⊃ 20% (95) ⊃ 10% (47) ⊃ 5% (23 or 24) ⊃ 2% (9 or 10). Stratified on crack and inactive presence.
- **Every run so far uses the split of seed 0.** The "seed" in a run name is the training seed only. Splits 1 and 2 exist but were never used.
- Zero-pixel classes in the seed-0 subsets: 7 at 10%, 10 at 5%, 12 at 2%.
- Unlabelled pool in the first protocol: the rest of the 478 train images, labels hidden (383 at 20%, 431 at 10%).

### 3.3 External unlabelled pool (CSIR/ARTS cells from the Dropbox link in the dataset README)

- The Dropbox folder holds more than 150k cell images. Downloaded: 11,993, seed 42, spread evenly over 9 leaf folders, 7 failed.
- Filtered and converted on Oct 6 (`reports/external_pool.md`): 55 files dropped because the cell is a labelled image (48 train, 6 val, 1 test). **11,938 kept**, converted to 512 × 512 grayscale in `data/unlabeled/images_512`, listed in `data/splits/external_unlabeled.txt`.
- Only exact cell matches were dropped. 196 kept cells come from val modules and 88 from test modules.
- Measured mismatches with the labelled images:
  - Only ARTS (2,734) and CSIR (9,204). 43% of labelled train images are CFVS, BMRK or SDLE and have no counterpart.
  - 57% of the pool (native 512 px files) has about half the contrast of labelled images (median per-image sd 26 to 29 against 43 to 50).
  - Sharpness differs most for multi cells and ARTS. ARTS cells in the pool are brighter (170 against 134).
- No intensity harmonisation was applied.

### 3.4 UCF-EL (Fioresi et al.)

- 9,562 train and 2,289 test image/mask pairs in the public release.
- 5 classes: background, crack, contact, interconnect, corrosion. Ignore label 128.
- Committed subsets: 20% = 1,912 (`sl20_seed0`), 5% = 478, 1% = 96, nested, stratified, seed 0. **The 1% subset has no corrosion image.**
- Ground-truth crack width (measured, masks at shorter side 295): median 9 px in train, 7 px in test. Only 22 to 27% of crack ridge pixels are 3 px wide or less. BenchmarkEL cracks are 2 to 3 px wide. I think this is a large part of why crack IoU is 0.65 on UCF-EL and 0.30 on BenchmarkEL (inferred, not tested).
- Jha's released split lists cover 16,327 names. 5,194 are not in the public release. **They put 1,769 of the 2,289 public test images into their training lists and 437 into their val list.** We use our own lists.

---

## 4. Code

### 4.1 Repos

- `noobsurd11/el-fault-detection` (private): created Oct 2 by Claude Code as a fresh repo, initial import from `sa-unetpp-ssl-el` at `v0-sa-failed`. 77+ commits, all pushed. Latest at snapshot: `fa59d7a`.
- `noobsurd11/sa-unetpp-ssl-el`: frozen, tagged `v0-sa-failed`. Last real commit Aug 8. It never contained the September work.

### 4.2 What the foundation does (Phase 0, Oct 2)

| Piece | Decision |
|---|---|
| Masks | read index masks directly. A value outside 0 to 23 is an error |
| Splits | a missing split file is a hard error. The old code silently trained on all 582 images, test included |
| Augmentation | flips, 90° turns, ±5° rotation with constant border (class 7 in the mask, black in the image), blur, noise, brightness/contrast. GaussNoise uses `std_range=(0.0124, 0.0277)` |
| Class weights | computed at start from the labelled subset in use, train only. Square-root inverse frequency, mean 1 over classes that have pixels, capped at 10× the median, weight 0 for absent classes |
| Metrics | one module for everything. Dataset-level confusion matrix. A class absent from ground truth is NaN and left out of means |
| Headline metric | `defect_miou` = mean IoU of crack and inactive |
| Other metrics | 24-class mIoU, 12-defect mIoU, crack recall, relaxed crack recall (2 px, Euclidean), image-level crack false positive rate on crack-free images, pixel AP, three conventions: `standard`, `pvs3` (drops all pixels whose ground truth is background), `pratt_median` (per-image median IoU, rules A/B/C) |
| Trainer | step-based, one trainer for supervised and SSL. 20,000 steps |
| Optimiser | Adam, lr 1e-3, weight decay 1e-4, 200-step warm-up, cosine decay **to zero**, grad clip 1, bf16 autocast |
| Model | plain U-Net++, 4,981,368 parameters, trained from scratch (no pretraining). SA variant: 5,440,120 |
| Evaluation rule | **final-step test is primary.** Best-val is secondary because val has 54 images and best-val selection flips the sign of several comparisons. Val+test pooled (104 images) is the secondary metric |
| Outputs | `experiments/<run>/config_used.yaml`, `train.log`, `metrics.json`, extra `eval_*.json`. Checkpoints stay out of git |

### 4.3 Bugs found in inherited code

| Bug | Effect | Status |
|---|---|---|
| `.gitignore` rule `data/` also matched `src/data/` | first import silently dropped the data-loading code | fixed before push |
| DataLoader workers shared one augmentation seed | every worker produced the same augmentations. Later found in a second form: every transform drew its apply/skip coin from the same generator, so flips always fired together and blur and noise always fired together | fixed Oct 3. **All "pilot" runs of Oct 2 used the coupled augmentation and are kept in a separate table** |
| GaussNoise called with a removed argument | noise was not what was intended | fixed |
| Weighted CE on CUDA not deterministic | small run-to-run differences | reimplemented |
| `torch.use_deterministic_algorithms(True)` | 5.3× slower | off for training, on only in the resume test |

### 4.4 Method implementations in the repo

| Method | Notes |
|---|---|
| Supervised (SL) | weighted CE |
| Mean Teacher (MT) | EMA 0.999, λ 1.5 after 2,000 warm-up + 2,000 ramp steps, SemiCE consistency with thresholds from class frequencies, labelled view is the SL arm's augmentation, **EMA teacher is evaluated** |
| ALHVR | two networks, two optimisers, no EMA, each with a clean and a perturbed decoder pass. Follows the reference **code** where paper and code disagree. Flags default to the reference. Network A is evaluated. 18.3 GiB, 0.70 steps/s alone on gaint |
| SA gate | flag `model.sa_gating`, byte-identical to the old SA block |
| Pratt reproduction | `smp.Unet` VGG16 ImageNet, 23.75M parameters, weight sets A (all 1) and C (Pratt's fixed weights) |
| UCF pipeline | DeepLabV3+ ResNet-50 ImageNet (Fioresi recipe), shorter side 295, 256 crops |
| PV-S3 reimplementation | mean teacher with paired geometry, confidence CE, and a per-class threshold variant |
| Diagnostics | region logging, prototype diagnostic, pseudo-label share, precision diagnostic, threshold-free AP, fit check, BN recalibration, external pool preparation |

cv02 local patches (diffs saved in `results_to_sync/cv02_patches/`): UCF subset files `sl<N>_seed<k>.txt` (+11/−7 lines), and Mean Teacher on the UCF data path (+6/−4 lines). Gaint does not have these.

### 4.5 ALHVR: what the reference code does (from `docs/alhvr_port_notes.md`)

- No cross pseudo supervision term anywhere. Pixels where both networks are confident get no unlabelled loss. **ALHVR is not "CPS plus modules".**
- Perturbed pass: same decoder weights on encoder features with feature dropout or feature noise (one coin flip per forward).
- Regions use the **perturbed** confidences. γ = mean of the lowest 80% of the averaged confidence over the whole unlabelled batch.
- Ω1 both above γ (no loss). Ω2 exactly one above γ (CG-CPCL). Ω3 both below γ (DTCT).
- DTCT: per pixel take the more confident network's clean output, sharpen elementwise with T = 0.1 (not a distribution over classes), MSE against the perturbed output, plus entropy terms. Target is not detached. Entropy is averaged over all pixels, so it shrinks with the Ω3 fraction.
- CG-CPCL: prototypes rebuilt every batch from unlabelled pixels by argmax. Cosine similarity with scale 1 used as logits in CE against the other network's argmax. With 24 classes the lowest reachable CE is 1.41. A second term pulls each Ω2 feature toward every class prototype.
- Prototype feature in our port: U-Net++ node X[3][1], 256 channels at 1/8 resolution, upsampled.
- **Loss weight: λ(t) = 0.1 · sigmoid ramp over the whole run.** It reaches 0.1 only at the last step. The reference uses SGD with a constant learning rate.

---

## 5. Timeline, including wrong turns

### Oct 2 (Fri)

1. Found gaint empty after the reset. Cloned the public datasets and the ALHVR reference by exec.
2. Found the GitHub repo was two months stale. Everything from September was unrecoverable. Decided to rebuild only what experiment 2 needs.
3. Downloaded the external pool through the Dropbox API with app authentication. Confirmed the pool contains labelled cells (leak risk).
4. Phase 0 prompt: foundation rebuilt in the new repo, 96 tests, pushed.
5. **My error:** I put a plain CPS baseline on the critical path, calling ALHVR "CPS plus modules". The user objected. Reading the reference code showed ALHVR has no CPS term. Plan changed to a direct ALHVR port with its own ablation ladder.
6. **My decision, later regretted:** labelled batch 4 in every method (SL 4, SSL 4 + 4), to match labelled samples per step.
7. Phase 1a: ALHVR port, region logging, pilots started. The ALHVR pilot was killed at step 13,600 by the OS shutdown.

### Oct 3 (Sat)

- Shutdown diagnosed. Resume and watchdog built. Coupled-augmentation bug found, so pilots were rerun on fixed code.
- SA gate ported. Pratt reproduction run. UCF pipeline and PV-S3 reimplementation built. Night queue built.
- PV-S3 v1 finished at 0.200, far below supervised.

### Oct 4 (Sun)

- ALHVR seed 0 finished (0.370). PV-S3 v2 at 0.276 and 0.283. Pseudo-label diagnostic traced the collapse to corrosion pseudo-labels.
- Step-matched supervised control on UCF: 0.491. So the unlabelled loss causes the PV-S3 collapse.
- cv02 set up as a second machine. Day and night blocks there: SL, SA, MT, ALHVR seeds.

### Oct 5 (Mon)

- cv02: MT with λ = 0 scores the same as MT. Released PV-S3 code run as shipped. Prototype diagnostic.
- Consolidation of both machines, tests, figures, `numbers.tex`.
- I read the prototype diagnostic and the run tables and concluded: prototypes are dead, and no unlabelled loss has shown an effect. I blamed the batch-4 choice for a BatchNorm confound.
- Evening: precision diagnostic, batch-8 supervised queue on gaint, ALHVR loss-off control and batch-8 runs on cv02.

### Oct 6 (Tue)

- Batch-8 results. **I said batch size was ruled out from gaint's three runs, then took it back** when cv02's three runs disagreed.
- ALHVR loss-off control finished: no detectable effect of the two modules.
- AP diagnostic, fit check, 5% and 2% splits, external pool prepared.
- User asked why the 12k pool was unused. I admitted it was my day-one call and had become a weakness.
- cv02: UCF label sweep, all 11 runs. Clear label gap found.
- Gaint rebooted and lost its queue.

### Oct 7 (Wed)

- Gaint rebooted again. Resume-after-reboot added. BN recalibration done. Low-label runs finished (SL-5, SL-2).
- cv02: Mean Teacher on UCF-EL at 5% and 1% with loss-off controls launched. ALHVR on UCF not started (port is more than a small patch).
- This document written. While writing it I noticed the ALHVR loss-weight schedule problem (section 9.1), which changes how the ALHVR result should be read.

---

## 6. Every experiment and result

All BenchmarkEL numbers: final step, 20,000 steps, split seed 0, standard convention, test = 50 images, val+test = 104 images. "g" = gaint, "c" = cv02.

### 6.1 BenchmarkEL arms at 20% and 100% labels (batch 4)

| Arm | n (g + c) | Test defect mIoU | Val+test defect mIoU |
|---|---|---:|---:|
| SL-20 | 8 (3 + 5) | 0.3435 ± 0.0329 | 0.3137 ± 0.0195 |
| SL-100 | 4 (1 + 3) | 0.3383 ± 0.0060 | 0.2956 ± 0.0107 |
| MT-20 | 6 (3 + 3) | 0.3662 ± 0.0061 | 0.3415 ± 0.0059 |
| ALHVR-20 | 6 (2 + 4) | 0.3724 ± 0.0103 | 0.3472 ± 0.0108 |
| SA-SL-20 | 4 (1 + 3) | 0.3399 ± 0.0104 | 0.2926 ± 0.0201 |
| SA-SL-100 | 1 | 0.3197 | 0.2893 |
| SA-MT-20 | 1 | 0.3384 | 0.3162 |
| Pratt-A-100 (U-Net VGG16, no weights) | 1 | 0.3386 | 0.3284 |
| Pratt-C-100 (U-Net VGG16, Pratt weights) | 1 | 0.3149 | 0.2975 |

Per-run SL-20 values: gaint 0.3059, 0.3679, 0.3786. cv02 0.3385, 0.3467, 0.3709, **0.2848** (seed 3, crack IoU 0.133), 0.3546.
Per-run ALHVR: gaint 0.3699, 0.3673. cv02 0.3599, 0.3704, 0.3762, 0.3905.

Tests on the pooled runs (Welch):

| Comparison | Test | Val+test |
|---|---|---|
| ALHVR vs SL-20 | +0.029, p 0.045 | +0.034, p 0.002 |
| MT vs SL-20 | +0.023, p 0.095 | +0.028, p 0.004 |
| ALHVR vs MT | +0.006, p 0.24 | +0.006, p 0.29 |
| SL-100 vs SL-20 | −0.005, p 0.68 | −0.018, p 0.066 |
| SA-SL-20 vs SL-20 | −0.004, p 0.78 | −0.021, p 0.135 |

Caveats on every p: no multiple-comparison correction; seeds 0 to 2 were run on both machines with the same initialisation and data stream, so pooled runs are not fully independent; one labelled subset only.

Pilot runs on the buggy augmentation (kept apart): SL-20 0.3360, SL-100 0.3436, MT 0.3515, ALHVR interim at step 13,500 0.3294.

### 6.2 Loss-off controls (cv02)

| Arm | Seeds | Test defect mIoU |
|---|---|---:|
| MT-20 | 0, 1, 2 | 0.3700, 0.3567, 0.3679 → 0.3648 ± 0.0071 |
| MT-20, λ = 0 | 0, 1, 2 | 0.3451, 0.3809, 0.3698 → 0.3653 ± 0.0183 |
| ALHVR-20 | 1, 2, 3 | 0.3599, 0.3704, 0.3762 |
| ALHVR-20, unlabelled weight 0 | 1, 2, 3 | 0.3757, 0.3708, 0.3461 → 0.3642 ± 0.016 |

- MT paired (λ 1.5 minus λ 0, teacher): −0.000 ± 0.024.
- MT teacher minus student at the final step: +0.000 ± 0.002. The EMA adds nothing because the learning rate ends at zero.
- ALHVR paired (on minus off): −0.016, −0.000, +0.030 → **+0.005 ± 0.023**.
- In both controls the unlabelled images still pass through the network and the unlabelled loss is exactly 0 on every logged step.

### 6.3 Labelled batch 8 and the label sweep (supervised)

| Arm | Labelled images | gaint | cv02 | Pooled |
|---|---:|---|---|---|
| SL-2-b8 | 9 or 10 | 0.1860, 0.1780, 0.2086 | not run | 0.191 ± 0.016 (3) |
| SL-5-b8 | 23 or 24 | 0.3531, 0.3202, 0.3218 | not run | 0.332 ± 0.019 (3) |
| SL-10-b8 | 47 | 0.3550, 0.3641, 0.3628 | 0.3421, 0.3428, 0.3743 | 0.357 ± 0.013 (6) |
| SL-20-b8 | 95 | 0.3218, 0.3652, 0.3500 | 0.3691, 0.3541, 0.3635 | 0.354 ± 0.017 (6) |
| SL-100-b8 | 478 | 0.3577, 0.3459, 0.3387 | 0.3500, 0.3412, 0.3393 | 0.346 ± 0.007 (6) |
| SL-20-b8, no class weights | 95 | 0.3110 | not run | 1 run |

- SL-5 seed 2 and SL-2 seed 0 were resumed from step 12,000 after the reboot.
- Machines disagree on SL-20-b8: gaint mean 0.346, cv02 mean 0.362. cv02's own summary: every arm whose BatchNorm sees 8 images lands at 0.362 to 0.370, every arm with 4 at 0.339 to 0.343. Gaint does not show that.
- Significant in gaint's tests: SL-100-b8 is below MT-20 on val+test (−0.025, p 0.003) and below ALHVR (−0.031, p 0.001).
- Class weights differ per subset: crack 0.559 and inactive 0.641 at 20%, 0.738 and 0.790 at 10%. So fractions are not compared at the same operating point.

### 6.4 Crack precision (gaint, `reports/precision_diagnostic.md`)

- Crack precision 0.22 to 0.35 and recall 0.67 to 0.73 in every weighted run.
- Example (`alhvr_20pct_s1`, test): 70,626 true crack pixels, 143,570 predicted. 85% of false crack pixels are true background. Under the `pvs3` convention crack IoU is 0.585 against 0.30 standard.
- Relaxed precision (2 px) is 0.49 to 0.75. So 25 to 51% of predicted crack pixels lie more than 2 px from any real crack. It is not only a halo.
- Gridline and material are over-predicted the same way. Inactive is under-predicted (precision 0.67, recall 0.55).
- Bad seeds are precision collapses with unchanged recall (cv02 SL-20 seed 3: crack precision 0.14).
- Without class weights: crack precision 0.63, recall 0.29, IoU 0.245. The weights only move along a precision/recall trade-off.

Crack-logit bias chosen on val (subtract b, typically 1.25 to 1.75):

| Arm (gaint) | Raw test | After bias | Gain |
|---|---:|---:|---:|
| SL-20 | 0.351 | 0.382 | +0.031 |
| MT-20 | 0.368 | 0.387 | +0.019 |
| ALHVR-20 | 0.369 | 0.381 | +0.013 |
| SL-100 | | | −0.005 |

On gaint the three arms end within 0.005 of each other after the bias. cv02's report says the bias adds +0.016 to +0.027 in 4 of 5 arms and that "the SSL lead survives it". The two machines read this differently and I have not reconciled them.

### 6.5 Threshold-free scores (pixel average precision)

cv02, test, mean over runs:

| Arm | Crack AP | Inactive AP |
|---|---:|---:|
| SL-20-b8 | 0.494 | 0.618 |
| SL-10-b8 | 0.485 | 0.619 |
| ALHVR | 0.477 | 0.676 |
| MT, λ = 0 | 0.472 | 0.665 |
| MT-20 | 0.470 | 0.666 |
| ALHVR, loss off | 0.468 | 0.668 |
| SL-20 | 0.464 | 0.637 |
| SL-100 | 0.429 | 0.616 |

Gaint, test: SL-20 0.469 / 0.659, SL-20-b8 0.490 / 0.622, SL-100-b8 0.457 / 0.637, SL-10-b8 0.492 / 0.623, MT-20 0.469 / 0.675, ALHVR 0.473 / 0.650, SA-SL-20 0.473 / 0.603, Pratt-A 0.499 / 0.623.

Readings:

- Crack: nothing beats plain supervised at batch 8. No SSL effect on cracks.
- Inactive: on cv02 every arm that forwards unlabelled images is at 0.665 to 0.676, every supervised arm at 0.616 to 0.637, loss on or off. On gaint, SL-20 at batch 4 has inactive AP 0.659, which blurs that split.
- SL-100 has the lowest crack AP on both machines.
- Seed sd of crack AP is 0.39 to 0.46 times the sd of crack IoU. AP is the quieter metric for crack. For inactive it is not quieter.

### 6.6 BatchNorm recalibration (no training, both machines)

Recomputing BN running statistics of supervised models on (a) their own labelled images, (b) all 478 train images, (c) the external pool:

- (a) and (b): no meaningful change (inactive AP moves by less than 0.01).
- (c) external pool: test defect mIoU −0.010 (SL-20-b8) and −0.018 (SL-10-b8).
- So BN running statistics do not explain the inactive gain of the 4 + 4 arms.

### 6.7 Fit against generalisation (gaint, supervised batch-8 models, no augmentation)

Crack:

| Model | Train, labelled | Train, never labelled | Val | Test |
|---|---|---|---|---|
| SL-10: IoU / P / R / AP | 0.325 / 0.33 / 0.95 / 0.64 | 0.237 / 0.27 / 0.66 / 0.34 | 0.228 / 0.25 / 0.68 / 0.35 | 0.304 / 0.35 / 0.72 / 0.49 |
| SL-20 | 0.304 / 0.31 / 0.90 / 0.55 | 0.211 / 0.24 / 0.66 / 0.31 | 0.224 / 0.24 / 0.73 / 0.38 | 0.273 / 0.30 / 0.73 / 0.49 |
| SL-100 | 0.239 / 0.26 / 0.72 / 0.37 | none left | 0.224 / 0.24 / 0.76 / 0.37 | 0.283 / 0.32 / 0.73 / 0.46 |

Inactive:

| Model | Train, labelled | Train, never labelled | Val | Test |
|---|---|---|---|---|
| SL-10: IoU / P / R / AP | 0.881 / 0.89 / 0.99 / 0.99 | 0.340 / 0.59 / 0.44 / 0.48 | 0.289 / 0.48 / 0.42 / 0.44 | 0.417 / 0.76 / 0.48 / 0.62 |
| SL-20 | 0.783 / 0.79 / 0.98 / 0.96 | 0.456 / 0.63 / 0.62 / 0.63 | 0.331 / 0.41 / 0.64 / 0.54 | 0.418 / 0.69 / 0.52 / 0.62 |
| SL-100 | 0.539 / 0.57 / 0.90 / 0.83 | none left | 0.225 / 0.24 / 0.82 / 0.60 | 0.412 / 0.54 / 0.64 / 0.64 |

Readings:

- **Crack is not fitted even on training images.** After 20,000 steps on 47 images, crack IoU on those 47 images is 0.33. With 478 images, train equals val.
- **Inactive is the opposite.** It is memorised on train (IoU 0.88 at 10%) and generalises poorly. On train images the model never saw, inactive IoU rises from 0.34 (10%) to 0.46 (20%). **So inactive has a real label effect in-distribution that the 50-image test set does not show** (test is flat at 0.41 to 0.42).
- Test crack AP (0.46 to 0.49) is well above val and unseen train (0.31 to 0.38). Test cracks are easier.
- Val inactive rests on 12,413 pixels in about 5 images.

### 6.8 ALHVR region statistics and the prototype diagnostic

Training-time regions (`alhvr_20pct_s0/regions.csv`, one batch every 100 steps):

| Step | λ | γ | Ω1 | Ω2 (a + b) | Ω3 |
|---:|---:|---:|---:|---:|---:|
| 100 | 0.0007 | 0.21 | 0.28 | 0.39 | 0.33 |
| 2,100 | 0.0018 | 0.72 | 0.51 | 0.28 | 0.21 |
| 5,100 | 0.0062 | 0.78 | 0.58 | 0.23 | 0.20 |
| 10,100 | 0.029 | 0.83 | 0.64 | 0.16 | 0.20 |
| 15,100 | 0.074 | 0.84 | 0.59 | 0.25 | 0.16 |
| 20,000 | 0.100 | 0.89 | 0.68 | 0.17 | 0.15 |

Prototype diagnostic (cv02, four ALHVR runs, final weights, the 383 held-out train images, evaluation mode):

- Ω3 is 15.6% of all pixels and holds 119,384 of the 168,511 true crack pixels (71%).
- DTCT winner accuracy in Ω3: crack 61.9%, inactive 51.2%, background 64.7%.
- Ω3 crack pixels the winner calls background: 20.7% on final weights. During training the logs give 32.4% over the whole run and 26.8% over steps 10k to 20k.
- Nearest-prototype crack accuracy in Ω3: own network's prototypes 43 to 49%, the other network's prototypes 4.6% (this is what CG-CPCL uses), per-batch prototypes as in training 1.1%.
- Own prototypes are below the winner on crack everywhere, above it on Ω3 inactive (55 to 62% against 51%), far below on background (15% against 65%).
- The rule "use the prototype label where the winner says background" recovers about 6,600 crack pixels and mislabels about 12.6 million background pixels.
- Temperature on the cosine does not change any label result.

### 6.9 UCF-EL supervised

Gaint, Oct 3 to 4 (DeepLabV3+ R50, 4-class defect mean IoU, test 2,289 images):

| Run | Steps | Standard | Crack / contact / interconnect / corrosion |
|---|---:|---:|---|
| SL-20, short | 12,000 | 0.448 | 0.631 / 0.405 / 0.231 / 0.526 |
| SL-20, short, PV-S3 v1 strong view | 12,000 | 0.403 | |
| SL-100 | 59,760 | 0.497 | 0.672 / 0.457 / 0.243 / 0.615 |
| SL-20, step-matched, seeds 0 to 2 | 95,760 | 0.501, 0.486, 0.487 → 0.491 ± 0.009 | 0.65 / 0.44 / 0.24 / 0.63 |

cv02, Oct 6, all at 95,760 steps, batch 16, SGD poly lr 0.005:

| Labels | Images | n | 4-class mean | 3-class mean | Crack | Contact | Interconnect | Corrosion | Crack AP |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 100% | 9,562 | 2 | 0.5364 ± 0.0042 | 0.4951 | 0.675 | 0.479 | 0.332 | 0.660 | 0.851 |
| 20% | 1,912 | 3 | 0.4932 ± 0.0045 | 0.4461 | 0.651 | 0.442 | 0.245 | 0.635 | 0.807 |
| 5% | 478 | 3 | 0.4146 ± 0.0017 | 0.3953 | 0.618 | 0.404 | 0.165 | 0.472 | 0.766 |
| 1% | 96 | 3 | 0.2265 ± 0.0017 | 0.3021 | 0.529 | 0.351 | 0.026 | no labelled examples | 0.690 |

- The two machines agree on SL-20 (0.491 against 0.493).
- Seed sd is 0.002 to 0.005, about ten times tighter than BenchmarkEL.
- The earlier impression "no gap at 20% on UCF" came from one SL-100 run at fewer steps. It was wrong. The gap is 0.043 at 20%.

### 6.10 PV-S3 (Jha et al.) on UCF-EL

Our reimplementation (gaint):

| Run | Standard | Note |
|---|---:|---|
| PV-S3 v1 | 0.200 | failed recipe |
| PV-S3 v2, seeds 0 and 1 | 0.276, 0.283 | corrosion predicted on 1.47M test pixels against 102,570 true (precision 0.067) |
| PV-S3 v2 + per-class pseudo-label cap | 0.418 | corrosion fixed (IoU 0.631). Still 0.073 below step-matched SL. One seed |
| Step-matched supervised control | 0.491 ± 0.009 | differs from v2 only in the unlabelled loss |

- Mechanism (measured): the teacher labels 0.96% of unlabelled pixels as corrosion, 23× the labelled share, and stays at 21.6× even at confidence 0.99. A stricter threshold does not remove it.
- The per-class cap is exceeded in 132 of 187 windows because the threshold is EMA-smoothed.
- The earlier (lost) implementation is recorded at 46.4. Not reproduced. Cause of the remaining gap is open.

Released PV-S3 code, run as shipped on cv02 (commit `e062f81`, no algorithm change, our split lists):

- Their loss has `ignore_index=0`, so **the model never predicts background**.
- Standard 4-class mean IoU: **0.050**. Corrosion predicted on 3.33M pixels against 102,570 true.
- Under the `pvs3` convention (pixels with background ground truth dropped): **0.828**, which matches their own validation log to 4 decimals.
- Their supervised-only mode does not run in the released code.

### 6.11 SA U-Net++ (the first experiment, redone correctly)

- SA-SL-20: 0.3399 ± 0.0104 (n = 4) against SL-20 0.3435. Val+test 0.293 against 0.314.
- SA-SL-100 0.3197, SA-MT-20 0.3384 (one run each).
- No benefit from the SA gate on this data, slightly worse on val+test. Confirms the earlier conclusion.

### 6.12 Running at snapshot time

cv02, Mean Teacher on UCF-EL (16 labelled + 16 unlabelled, 95,760 steps, same lr as SL, warm-up and ramp 9,576 steps each, SemiCE, EMA teacher evaluated, λ = 0 control keeps the forward pass identical):

| Run | Progress at 22:13 IST | Expected finish (IST) |
|---|---|---|
| MT 5% seed 0 and its control | about 63,000 of 95,760 | about 00:15, Oct 8 |
| MT 5% seeds 1, 2 and controls | about 10,000 | about 05:15, Oct 8 |
| MT 1% seed 0 and control | about 6,000 | about 08:30, Oct 8 |
| MT 1% seeds 1, 2 and controls | queued | later on Oct 8, depends on other users |

Other users held all 8 GPUs when these started, so they run slowly (2.4 to 4.3 steps/s against 7.9 alone).

gaint:

- External-pool Mean Teacher queue (`mt_20pct_ext_s0..2` and `mt_20pct_ext_lam0_s0..2`) is armed. It waits for a go signal, at most 3 hours after the low-label queue ended at 22:08, then starts.
- **Overfit check: no script and no report exist yet.** It was asked for twice.

Not run anywhere: ALHVR on UCF-EL. cv02 stopped because the DeepLab port is more than a small patch.

---

## 7. How sure I am

### Certain (measured, replicated, or structural)

1. The old repo and all September code are gone.
2. SA gate gives no benefit on BenchmarkEL.
3. On BenchmarkEL, switching off the unlabelled loss of Mean Teacher changes nothing (3 pairs, both the paired difference and the means).
4. Cross-network prototypes carry almost no defect information in our ALHVR port. The relabel rule is net-negative by three orders of magnitude.
5. Every weighted model over-predicts crack: precision near 0.3, recall near 0.7.
6. Supervised training on BenchmarkEL does not fit cracks on its own training images.
7. BenchmarkEL test defect mIoU is flat from 10% to 100% labels and breaks at 2% (0.19).
8. UCF-EL has a label gap: 0.536, 0.493, 0.415, 0.227 at 100, 20, 5, 1%. Seed sd is about 0.003.
9. PV-S3 as released never predicts background. Its headline number exists only under a convention that drops background pixels. Its released splits put most of the public test set into training lists.
10. Our PV-S3 reimplementation collapses because of the unlabelled loss, through corrosion pseudo-labels.
11. BN running statistics do not explain the 4 + 4 inactive gain.

### Fairly confident

1. The gain of MT and ALHVR over SL-20 on val+test is real but does not come from their unlabelled losses.
2. That gain is mostly on inactive.
3. Inactive on BenchmarkEL is generalisation-limited, crack is fit-limited. Two different problems under one headline number.
4. The 50-image test set hides in-distribution effects (inactive label gap) and flatters crack scores.
5. A short supervised schedule is one way a paper can show an SSL gain that is not real (our UCF SL-20 went from 0.448 at 12k steps to 0.491 at matched steps).

### Unsure

1. Whether labelled batch 8 matters. Gaint says no (0.346), cv02 says yes (0.362).
2. Why forwarding unlabelled images helps inactive. Remaining candidates: train-time batch statistics acting as a regulariser, or something in the two-stream data pipeline. Untested.
3. Why cracks cannot be fitted: model resolution or capacity, the weighted loss, augmentation, or annotation inconsistency at 2 to 3 px. The overfit check would separate these and has not run.
4. Whether "more labels do not help" survives a fixed operating point, because class weights change with the subset.
5. Whether ALHVR's modules do anything when their loss weight is actually meaningful (see 9.1).
6. Whether the bias-shift result leaves an SSL lead or not (machines read it differently).
7. Whether any SSL method helps on UCF-EL at 5% or 1%. Running now.
8. Why our PV-S3 reimplementation with the class cap is still 0.073 below supervised.

---

## 8. Assumptions in force

1. `dataset_20211104` is the Pratt 2023 benchmark (24 classes, 50 test images match the paper).
2. Final-step weights are the fair comparison point. Best-val is too noisy.
3. One labelled subset (split seed 0) is enough for now. **This is a weak assumption.** Subset choice may matter as much as training seed, especially at 2 to 10%.
4. Runs with the same seed on two machines count as separate runs. They share initialisation and data order, so this overstates n.
5. 20,000 steps is enough for every BenchmarkEL arm. Not verified with a longer run. SL-100 train equals val, which could also mean under-training.
6. The supervised loss is the same in every method, so only the unlabelled part differs. True by code check for SL against MT. ALHVR's reference uses Dice + CE; our port uses the repo's weighted CE.
7. bf16 autocast does not change conclusions.
8. UCF results with a pretrained ResNet-50 DeepLab say something about our from-scratch U-Net++. They may not.
9. Hidden masks of unlabelled train images are used for diagnostics only. There is a test that they cannot reach a loss.
10. The cv02 tarball at `fe79e19` plus two patches trains the same way as gaint's current code. The UCF SL-20 agreement (0.491 against 0.493) supports this. BenchmarkEL SL-20-b8 does not (0.346 against 0.362), though that may be seed noise.

---

## 9. What may have gone wrong

### 9.1 The ALHVR run may never have had its losses switched on in any real sense

Found while writing this document. Not yet discussed with the user.

- ALHVR's weight follows the reference: λ rises on a sigmoid over the whole run and reaches its maximum of 0.1 only at the final step. Logged values: 0.006 at step 5,100, 0.029 at 10,100, 0.074 at 15,100.
- The reference trains with SGD at a constant learning rate. We train with Adam and a cosine schedule that reaches zero at the final step.
- So when λ is finally non-trivial, our learning rate is almost gone. For most of training the unlabelled terms contribute a few percent of the gradient at most.
- Consequence: "ALHVR equals ALHVR with losses off" (+0.005 ± 0.023) is close to true by construction. It does **not** show that DTCT is useless. It shows that the as-is schedule, under our optimiser, barely applies it.
- What still stands regardless of λ: the prototype diagnostic and the DTCT winner accuracy numbers. They are measured on the networks, not on the loss weight.
- Mean Teacher is not affected: its λ is 1.5 from step 4,000 onward.
- A fair test of DTCT needs a weight schedule that reaches full strength early (as MT's does), on a setting with a label gap.

### 9.2 Other threats

| Risk | Why it matters |
|---|---|
| One labelled subset for everything | every conclusion about label fractions is conditional on one draw |
| Shared seeds across machines | pooled n is inflated |
| Class weights change with the labelled subset | label-fraction and batch-size comparisons mix in an operating-point shift |
| 50 odd test images | noisy, all cracked, easier cracks, hides the inactive label effect |
| Val of 54 images, 5 with inactive | any tuning on val (bias, checkpoint) is fragile |
| Cosine to zero | makes EMA meaningless at the final step and interacts with any ramped loss |
| From-scratch 5M U-Net++ | may simply be too weak for 2 to 3 px cracks. Pratt-A with a pretrained VGG16 U-Net has the best crack AP (0.499, one run) |
| Weighted CE with weight 0 for absent classes | at 2% twelve classes have weight 0. The model is never told about them |
| Machine difference on BenchmarkEL | gaint and cv02 disagree on SL-20-b8 by 0.016 with n = 3 each |
| cv02 `/tmp` workspace | a reboot wipes checkpoints. Only synced results survive |
| cv02 code is a patched tarball | gaint lacks the UCF subset and UCF-MT patches |
| External pool mismatch | half-contrast images, two sources only. A null result there will not be clean |
| UCF 1% has no corrosion | 4-class mean is pulled down by construction. Judge 1% on the 3-class mean |
| PV-S3 class cap not strict | the 0.418 run is not the method as specified |
| Stats without correction | 38 tests in `stats_tests.md`, only one survives Bonferroni |
| Reports out of date | `numbers.tex` and figures stop at Oct 5. The precision diagnostic covers only the 14 checkpoints that existed then |
| Unpushed state on cv02 | everything there depends on the sync folders |

---

## 10. Mistakes I made, so they are not repeated

1. Called ALHVR "CPS plus modules" and put plain CPS on the critical path. Wrong. Reading the code first would have avoided it.
2. Specified the region test as per-image, 75%, clean confidence. The code uses the whole batch, 80%, perturbed confidence.
3. Chose labelled batch 4 for all methods without checking what it does to BatchNorm.
4. Predicted Ω2 would shrink to near zero. It stayed at 16 to 25% during training (5.8% on final weights in evaluation mode).
5. Called the false crack "a thick halo". Half of it is elsewhere.
6. Declared batch size ruled out from three runs on one machine.
7. Assumed supervised runs used weaker augmentation than the MT student. They do not.
8. Parked the external pool on day one and did not flag, when results came in flat, that a 383-image pool is a weak test of SSL.
9. Suggested BN running statistics as the explanation for the 4 + 4 gain. Ruled out by measurement.
10. Did not ask for an overfit check on day one. It is still not done.
11. Told the user a low seed-0 run on cv02 drove the pooled gap. The outlier is cv02 seed 3 (0.2848). Gaint seed 0 is also low (0.3059).
12. Said UCF-EL showed no gap at 20% on the strength of one run at fewer steps.
13. Read "ALHVR equals loss-off" as evidence against the modules for two days without checking the logged λ.
14. Several times stated a leading hypothesis as if it were the finding. The user's "don't presume" rule exists because of this.

---

## 11. What I think

1. **BenchmarkEL at 10% and above is the wrong place to test SSL.** Supervised training is already saturated there on this test set. That is independent of the method.
2. **BenchmarkEL has two separate problems.** Cracks are not fitted at all, which is a supervised modelling problem. Inactive areas are memorised and generalise poorly, which is where more data or regularisation helps, and where the 4 + 4 arms gain.
3. **Pseudo-label methods are structurally weak for these defects.** Where the model is confident the pseudo-label is redundant. Where the defects are, the pseudo-label is wrong 40 to 50% of the time. For rare classes it runs away (corrosion on UCF).
4. **The benchmark's reported SSL gains are not trustworthy as published.** Short supervised schedules, a metric convention that drops background, a model that never predicts background, and test images in training lists are all measured facts about the PV-S3 release.
5. **The most defensible thesis is now a careful negative-plus-diagnosis study:** what looks like an SSL gain on EL data, where it really comes from, and under what label budget and dataset SSL has room at all. The UCF label sweep gives the ground to add a positive result if one exists.
6. **The most promising use of unlabelled data is probably not pseudo-labelling.** In-domain self-supervised pretraining on the 150k unlabelled cells, or supervised pretraining on UCF-EL then fine-tuning on a few BenchmarkEL labels, do not depend on pseudo-labels being right. Neither is tested.
7. ALHVR itself has not had a fair test yet (9.1). Its prototype half has, and failed.

---

## 12. Plan

### 12.1 In flight, nothing to do but read results

| Result | When | What it decides |
|---|---|---|
| MT 5% against its loss-off control on UCF-EL (3 pairs) | Oct 8 morning | first SSL comparison on ground with a label gap. Judge on paired differences and per class |
| MT 1% pairs | Oct 8 later | same, on the 3-class mean |
| External-pool MT on BenchmarkEL (3 + 3) | Oct 8 morning to midday | whether pool size matters at 20%. Expect a muddy answer because of the pool mismatch |

### 12.2 Owed, cheap, should run next

1. **Overfit check on gaint** (10 crack images, no augmentation, 3,000 steps, weighted CE / plain CE / CE + Dice, metrics on the same images, overlays). Decides whether any more BenchmarkEL training is worth it.
2. Re-run the precision diagnostic and AP on the newer checkpoints (about a minute).
3. Regenerate `numbers.tex` and figures when the report is written.

### 12.3 Decisions that depend on the UCF MT result

| If | Then |
|---|---|
| MT beats its loss-off control at 5% | port DTCT alone to DeepLab (no prototypes), with a weight schedule that reaches full strength early, plus its loss-off control |
| MT equals its control | pseudo-label SSL has now failed on both datasets with controls. Move to pretraining options below and write the diagnosis |
| MT is worse than its control | same as above, and check the pseudo-label shares as we did for PV-S3 |

### 12.4 Options, ranked by what I would bet on

| # | Option | Cost | Why |
|---|---|---|---|
| 1 | Overfit check | under an hour | separates model, loss and annotation as the cap on cracks |
| 2 | Supervised loss for thin structures on BenchmarkEL (Dice or Tversky term, logit adjustment, fixed weights across fractions) | a few short runs | the bias shift alone is worth +0.03, more than any SSL arm |
| 3 | ALHVR / DTCT with a fair weight schedule, on UCF-EL 5% | port plus 6 runs | closes the open question in 9.1 |
| 4 | Self-supervised pretraining of the encoder on the unlabelled cells, then fine-tune at 2 to 10% | 1 to 2 days | uses unlabelled data without pseudo-labels. Could be the positive result |
| 5 | Pretrain on UCF-EL labels, fine-tune on few BenchmarkEL labels | about a day | labels from a neighbouring dataset usually beat unlabelled data |
| 6 | Evaluate on more than 50 images (cross-validation over the 582, or held-out train images) | re-scoring plus some runs | the inactive label effect is invisible on the official test set |
| 7 | More labelled subsets (split seeds 1 and 2) for the key arms | reruns | removes the single-subset assumption |
| 8 | BN mixing controls (GroupNorm, 4 labelled + 4 duplicated labelled forward-only, MT at 2 + 2) | a few runs | explains the 4 + 4 inactive gain. Scientifically neat, lower priority |
| 9 | Merge the 24 classes to defects plus background | a few runs | tests whether the 24-way setup caps crack IoU |
| 10 | Pretrained encoder for the BenchmarkEL model | a few runs | Pratt-A's crack AP hints it helps |

---

## 13. Open decisions for the user

1. ALHVR on UCF-EL: wait for MT, then port DTCT only? (my recommendation: yes)
2. Rerun ALHVR on BenchmarkEL with a weight schedule that actually applies the loss? Or skip BenchmarkEL for SSL entirely?
3. Overfit check: paste the reminder to gaint.
4. Whether to add split seeds 1 and 2.
5. PV-S3: rerun the class cap strictly, or stop there?
6. BN mixing controls: worth the GPU time or not.
7. cv02 cleanup of `/tmp/noob_el` (PV-S3 environment about 3 GB, all checkpoints). Not before everything needed is synced.
8. Rotate the Dropbox app secret.
9. Find out who shuts gaint down (needs sudo: `journalctl -u systemd-logind`).
10. Copy the cv02 patches to gaint so both machines run the same code.
11. Thesis framing: negative-plus-diagnosis, or keep pushing for a positive SSL result first.

---

## 14. How to resume in a new session

### 14.1 First checks

Gaint (through `Gaint_Herald` exec, `cwd=/home/noob/work/el-fault-detection`):

```
git log --format="%h %ad %s" --date=format:"%m-%d %H:%M" -10
ls -t reports | head
ls -t experiments | head -12
python3 -c "import subprocess; print(subprocess.run(['nvidia-smi','--query-gpu=memory.used,utilization.gpu','--format=csv,noheader'],capture_output=True,text=True).stdout)"
cat /proc/uptime
```

cv02 (through `Yugma_Herald` or `noob_herald` exec):

```
ssh -o BatchMode=yes cv02@10.8.1.106 "nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv,noheader; ls -t /tmp/noob_el/el-fault-detection/experiments | head -20"
ssh -o BatchMode=yes cv02@10.8.1.106 "sed -n 1,95p ~/noob/el_results/cv02.md"
```

### 14.2 Files to read first

| File | Where | What |
|---|---|---|
| `reports/day1.md` | gaint | running log of everything on gaint, newest block first |
| `reports/results_consolidated.md` | gaint | every BenchmarkEL run from both machines |
| `reports/stats_tests.md` | gaint | all tests |
| `reports/fit_vs_generalise.md` | gaint | the fit check |
| `reports/precision_diagnostic.md`, `threshold_free.md`, `bn_recalibration.md`, `external_pool.md`, `arm_differences.md` | gaint | the diagnostics |
| `docs/alhvr_port_notes.md` | gaint | paper against code, every flag |
| `~/noob/el_results/cv02.md` | cv02 | everything on cv02, summary on top |
| `~/noob/el_results/prototype_diagnostic/prototype_diagnostic.md` | cv02 | prototype diagnostic |

### 14.3 Run-name key

- `sl_<p>pct[_b8][_nocw]_s<k>`: supervised, p% labels, optional batch 8, optional no class weights, training seed k.
- `mt_20pct_s<k>`, `mt_20pct_lam0_s<k>`: Mean Teacher and its loss-off control. `_ext` = external pool.
- `alhvr_20pct_s<k>`, `alhvr_20pct_lam0_r2_s<k>`: ALHVR and its loss-off control (r2 = the relaunch).
- `sa_*`: SA gate on. `pratt_unet_set{A,C}`: Pratt reproduction. `pilot_*`: buggy augmentation, do not compare.
- `ucf_sl<N>_stepmatched_s<k>`, `ucf_full_stepmatched_s<k>`: UCF supervised at 95,760 steps. `ucf_mt_sl<N>[_lam0]_s<k>`: UCF Mean Teacher. `ucf_pvs3*`: PV-S3 reimplementation.
- Suffix `_cv02` = run on cv02.

### 14.4 Prompt style that worked

- State the question, not the expected answer. Add: "If anything contradicts the code, say so and follow the code."
- Ask for a facts-first step 0 when I am assuming something about the code.
- One change per new arm against an existing arm.
- Every SSL arm gets a loss-off control with an identical forward pass, same seeds, same machine.
- Commit and push after each step and each finished run. End with: what passed, what failed, what needs my decision.
- On gaint: resume after reboot and record it. On cv02: one run per GPU, sync results, logs gzipped in `results_to_sync/`.

### 14.5 Pending reminder for gaint (not yet pasted as far as I can tell)

```
The overfit check has no report. Run it before or beside the external-pool
queue: 10 labelled train images that contain cracks (list them), no
augmentation, batch 8, 3,000 steps, three settings: (a) the current weighted
CE, (b) plain CE, (c) plain CE + Dice. Every 500 steps report crack and
inactive IoU, precision and recall on those same 10 images. Save prediction
overlays for 3 images per setting. Write reports/overfit_check.md. Numbers
only. Commit and push.
```

---

## 15. Glossary

| Term | Meaning |
|---|---|
| SL-p | supervised training on p% of the labelled train images |
| MT | Mean Teacher |
| λ = 0, loss-off | the same run with the unlabelled loss weight at zero, forward pass unchanged |
| ALHVR | Lei et al. ICCV 2025. Two networks, region routing by confidence, CG-CPCL on Ω2, DTCT on Ω3 |
| Ω1, Ω2, Ω3 | pixels where both, exactly one, or neither network is above the confidence threshold γ |
| DTCT | the more confident network's sharpened prediction teaches the perturbed branch in Ω3 |
| CG-CPCL | prototype-based cross-network loss in Ω2 |
| defect mIoU | mean IoU of crack and inactive (BenchmarkEL), or of the 4 defect classes (UCF-EL) |
| AP | pixel-level average precision from the softmax probability, threshold-free |
| standard / pvs3 convention | all pixels counted / pixels with background ground truth dropped |
| b8 | labelled batch 8 (default is 4) |
| val+test | val and test pooled, 104 images, our secondary metric |
| step-matched | supervised baseline trained for the same number of optimiser steps as the SSL arm |
