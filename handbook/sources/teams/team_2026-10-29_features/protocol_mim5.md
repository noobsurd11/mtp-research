# Protocol MIM5: continued SparK-style MIM of the ResNet-34 encoder on the pool, then fine-tune at 5% (v1)

runner, 29 Oct 2026. Status: **v1.1, APPROVED by coach** (`review_mim5_v1.md`: pretraining approved after A1, R3 threshold 0.95; fine-tunes approved once gates F1-F2 are logged). v0 got CHANGES C1-C6 (`review_mim5_v0.md`); settings binding from `coach_mim5.md`. **Machine (team-lead ruling, 29 Oct): gaint for pretraining and all 5% fine-tunes; A5c-f1 is shared with other directions' 5% arms.** cv02 yardsticks (A5c 0.304, A5c+LA 0.319, BsM5 0.331) are cross-machine and descriptive only. Plan item 3 of `team_2026-10-27_unlabelled/SYNTHESIS.md`: the user's own intuition (learn features from the unlabelled cells, then use the labels).

## What I had seen when writing this
- All P-series, Track D and Track M results in the session record (A5c, BsM5, SUP100, FINAL).
- No MIM fine-tune exists. MIM outputs so far: smoke loss curves, reconstruction pictures, a width timing and an identity check on training logs (no test or val number of any MIM-initialised model).

## Question
Does continued masked-image-model pretraining of the ImageNet ResNet-34 encoder on ~11.7k unlabelled EL cells give a better 5% fine-tune than the ImageNet encoder itself, everything else fixed?

## Pre-stated expectation (S)
- Most likely **n.d. on all three primaries.** The literature prior is low: in-domain MIM/contrastive lost to an ImageNet init on thin structures (arxiv:2605.12430, arxiv:2402.17611), and P15's UCF-EL pretraining was n.d. at 5%.
- If it helps: crack IoU 0 to +0.02, inactive IoU 0 to +0.05, relF1@2 0 to +0.02 (SYNTHESIS row 3).
- **Power (coach):** A5c crack sd is about 0.008, so the crack threshold is about 0.015; the inactive threshold is about 0.05 or more. The expected effect sits at or below threshold, so n.d. is the likely outcome even if MIM helps a little.
- A crack gain below the free logit bias (+0.015 at A5c, tau 1) would not be practically useful.

## Arms (one change: the encoder init)
| Arm | Encoder init | Runs | Seeds |
|---|---|---|---|
| **A5c-f1** | ImageNet (smp default) | `f1_A_5pct_s0..4` | 0-4 |
| **MIM5** | `encoder_final.pth` of the one MIM run | `f1_MIM_5pct_s0..4` | 0-4 |

- **Fine-tune opts (both arms), A5c verbatim** (`scripts_cv02/p12_A_queue.spec`):
  `supervised.yaml seed=K data.labeled_fraction=0.05 training.total_steps=20000 data.split_seed=0 training.labeled_batch_size=8 data.mask_subdir=labeled/masks_escdd model.name=smp_unetpp data.augmentation=labelsafe loss.supervised=ce_dice` (23 labelled cells, `seed0/labeled_5pct.txt`).
- MIM5 adds only `model.encoder_init=<encoder_final.pth>`. No lower encoder lr, LLRD or freezing in fine-tuning.
- The encoder is loaded after the model is built; loading draws no random numbers (tested), so per seed the decoder/head init, data stream and augmentations are identical between arms (paired by seed).
- Matched optimizer steps (20,000, batch 8), final weights (step 20,000 asserted), one machine type, one commit, md5-identical data.
- **A5c is re-run** on the f1 commit (old A5c: cv02 at `24590fb` / `bac5264`). Old A5c is reported next to A5c-f1 as a reproducibility check (descriptive).

## Pretraining (MIM arm only; one run, seed 0, final weights, no selection)
- **Code:** gaint worktree `el_f1`, branch `f1`, commit `603e0d5` (= `1be64e1` + F1: `scripts/pretrain_mim.py`, `src/pretrain/spark.py`, `scripts/build_mim_pool.py`, `src/models/encoder_init.py`, 5 lines in `scripts/train.py`). Suite: 264 passed, 3 skipped (21 F1 tests).
- **Start:** `smp.encoders.get_encoder("resnet34", in_channels=1, weights="imagenet")`, tested equal tensor for tensor to the encoder `smp_unetpp` builds. `mim_step0.pth` = this start, saved through the same path as the final file (for check I2).
- **Pool v1.1** (`scripts/build_mim_pool.py --hp_thr 0.95 --twin_thr 0.95 --monitor 256 --monitor_seed 0`; inputs `neardup.json` md5 `e4b41b61...`, `samepos_pool.json` md5 `24e72e80...`, ext117 `manifest.csv` md5 `a8423a81...`, copied into `reports/f1/`):

  | Step | Cells |
  |---|---|
  | external pool | 11,938 |
  | R1 module: (source, module) of any val, test or E1 cell (159 modules) | −413 (411 by this rule only) |
  | R2 ext117 stems in the pool | −11 (2 only) |
  | R3 content: high-pass r ≥ 0.95 to any val, test or ext117 cell (neardup 128 px any position, or samepos full-res) | −50 (39 only) |
  | R4 pool copies (r_hp ≥ 0.95) of the 7 D7 train twins | 0 |
  | external dropped (union) | −463 (3.9%) |
  | held-out monitor (seed 0) | −256 → `mim_monitor_v11.txt`, md5 `4a09f5988a09cf4dfa4f8843ab31a93b` |
  | external kept | 11,219 |
  | train 478 − 7 D7 twins | +471 |
  | **training list** `mim_pool_v11.txt` | **11,690**, list md5 `f0a5d74acfc84b6a888c76b7022799ab` |

  - Builder checks: no val, test or E1 stem in either list.
  - Train images include the 23 labelled 5% cells and the train cells of val/test modules (they are train images; MIM sees no labels). Disclosed.
  - v1 used R3 at 0.85 (780 cells, 23% of the pool's ARTS cells, the same-position shading family). Coach's A1 set 0.95: it still drops every exact or near copy and the top test candidates (0.953-0.959). v1 lists are kept on gaint, unused.
- **Method** (SparK, arxiv:2301.03580; dense emulation of sparse conv, as SparK's code):
  - mask on the stride-32 grid (16 x 16 cells of 32 px at 512), ratio 0.6, exactly 102 visible cells per image, seeded;
  - masked input pixels zeroed; every encoder conv and maxpool output re-masked; BN statistics over visible positions only (tested: perturbing masked pixels changes no stage output, train and eval mode; masked positions are 0 at every stage; all-visible equals the plain encoder);
  - SparK light decoder (5 upsampling blocks, width W halving, 1x1 to 1 channel); densify per scale (strides 32/16/8/4): sparse BN, learnable mask token, projection. Discarded after MIM;
  - loss: MSE on masked 32 px patches only, against per-patch normalised targets (eps 1e-6);
  - input: full 512 cell, native scale, normalised as fine-tuning (mean 0.5, std 0.25);
  - augmentation: the label-safe set (h/v flip, rot90 k in 0-3, brightness/contrast ±0.2 at p 0.4); no resize, crop, blur, noise or small rotation.
- **Optimisation:** AdamW, betas (0.9, 0.95), wd 0.04 on conv weights only (not biases, norms or mask tokens). Peak lr: decoder group (decoder, densify, tokens) 1e-3, encoder 2e-4. Global linear warmup over 2 epochs, then cosine to 0 at the end for both groups. Encoder frozen (no grad) for the first 2 epochs, then its lr ramps linearly from 0 over 1,000 steps on top of the schedule. Grad clip 5.0 (clip rate logged), bf16 autocast.
- **Batch, width, length:** 100 epochs (1.17M samples).
  - Batch 64 on an A6000; on gaint (the launch machine) batch 32: 365 steps/epoch, 36,500 steps, freeze and warmup 730 steps, then the 1,000-step encoder ramp. Same lrs (C3).
  - Decoder width 256 if a 100-step timing shows ≥ 1.6x samples/s over 512; else 512. Measured on gaint (`reports/f1/width_choice.txt`, batch 16, encoder unfrozen, steps 51-100, only finllm on the GPU): w512 76.1, w256 88.4 samples/s, ratio 1.16, so **width 512**.
  - Memory (S1 smoke): 8.0 GB peak allocated at batch 16 unfrozen, so about 30 GB at 64. Batch 64 on an A6000; batch 32 on gaint (beside finllm's 5.9 GB).
- **Monitor:** held-out reconstruction loss on the 256 monitor cells (eval mode, no augmentation, fixed mask seed) at step 0, every 1,000 steps and at the end. Overfit check only, never selection.
- **Determinism:** epoch order and per-step draws are pure functions of (seed, epoch/step); resume is bit-identical to an uninterrupted run (tested on CPU across the freeze boundary).
- **Kept from pretraining:** encoder weights and BN running statistics, saved as `{"models": {"model": {"encoder.<key>": ...}}}`; md5 recorded in `encoder_final.md5` and here before any fine-tune.

## Checks before any fine-tune (on the fine-tune machine)
- **I1:** `el_f1` with `encoder_init` unset reproduces the A5c stdout bit-identically for 1,000 steps (loss, lr and val lines; timestamps and speed stripped). On cv02 against the original `p12_A_5pct_s0.stdout`; on gaint against `el_m` `1be64e1`. Done on gaint for 500 steps (`identity_f1.txt`); the 1,000-step check is repeated on the launch machine.
- **I2:** `encoder_init=mim_step0.pth` reproduces the same lines bit-identically for ≥ 300 steps.
- **I3:** unit tests above (CPU).
- **Smoke (S1-S3):** at most 1,000 MIM steps on the real step schedule (freeze, then the encoder ramp); loss near 1.0 and falling, no spike at the unfreeze, encoder grad norm and clip rate logged, enc_lr ramping from 0, held-out loss at step 0 and later, samples/s and peak memory, one reconstruction PNG. Pool builder counts and md5 (table above).

## Primaries and decision rule
- **Primaries:** test crack IoU, crack relF1@2, inactive IoU (revised masks, argmax, final weights).
- **Rule 1** (`handbook/07` §5, house code `ssl_rules.py` `cmp` / `m1_analyze.thr`): Δ = mean(MIM5) − mean(A5c-f1) > max(0.01, 2·sqrt((sd_A² + sd_B²)/3)) on a primary is BETTER, < −threshold is WORSE. The divisor is 3 also at 5 v 5 (team-lead ruling, 29 Oct; as BsM5, CsM5, P16). The /5 threshold is printed as descriptive only.
- **Verdict sets:** all 50 cells and without `CSIR_00070_r8_c4` (the clean co-primary, 27 Oct SYNTHESIS §2). **Pass** = a primary BETTER in both sets, or BETTER in one and n.d. with the same sign in the other, and no primary WORSE in either set. Without the 7 twins and without both: reported, not in the verdict.
- **Outcomes:**
  - pass: the 100% arm (MIM100 vs SUP100 re-run on the same commit and machine, 5 v 5, same rule) gets its own protocol;
  - n.d. on all three primaries in both sets: **closed** ("continued MIM on this pool does not beat ImageNet init on EL at 5%"); no 100% arm;
  - WORSE on any primary: closed, reported as worse;
  - mixed (a gain in one set only): reported, closed unless coach and team-lead decide otherwise before any further run.
- Multiplicity: 3 primaries x 2 sets = 6 tests, no correction, disclosed.

## Reported for every contrast (never change the verdict)
- All four cell sets: all 50 / without the noisy cell / without the 7 twin test cells / without both.
- Per source (CFVS, BMRK, ARTS, CSIR, SDLE) with FP px of subset-absent classes; per-class IoU / P / R for the 13 robust classes; mIoU_rob.
- Crack capture: precision, recall, relP@2, relR@2, component recall and precision. Width flag (R4): crack relP@2 drop > 0.05 (also crack or inactive precision drop > 0.05).
- Paired image bootstrap (2,000, seed 0) and leave-top-3-out.
- Yardsticks, not in the rule: A5c+LA 0.319 and BsM5 (D7) 0.331 (other commits, descriptive); both arms re-scored with the logit adjustment tau 1 (`scripts/rescore_logit_adjust.py`), MIM5+LA − A5c-f1+LA as a secondary.
- **E1 (secondary only, never for selection):** 106 ext cells, crack IoU, crack recall, inactive IoU and the E1 cell metrics of `results/e1`.
- Mechanism (descriptive): pretraining and monitor curves, reconstruction pictures, encoder weight change per stage vs ImageNet (relative L2).

## Scoring
- `trackM/scripts/m0_audit.py` (per-cell 24x24 confusion, `crack_rel2`, components; val, test, ext; asserts step 20,000; records `code_revision` from the deployment's `REVISION`) with `--code` = the f1 deployment; analysis `trackM/scripts/m2_rung.py --a A5c-f1 x5 --b MIM5 x5`; plus `rescore_label_versions.py` JSONs through `scripts/ssl_rules.py` as the P-series cross-check.
- **Masks:** cv02 `el_p7/data/escdd_masks` (pixel-identical to `labeled/masks_escdd`). gaint's `data/escdd_masks/test` differs at 2 cells (`ARTS_00047_r3_c1` 34 px, `ARTS_00051_r3_c2` 202 px: class 25 on gaint, crack on cv02), so if the runs are on gaint, scoring uses a data root whose `escdd_masks` are the `labeled/masks_escdd` files (md5-checked against cv02), never gaint's `escdd_masks`.
- Per-cell outputs go to coach for an independent recompute before any result goes to team-lead.

## Compute and logistics
- Pretraining: one run, about 1.1M samples. gaint unloaded about 75 samples/s at batch 16 (width 512, first 50 steps); A6000 to be measured. Budget 3-5 GPU-h.
- Fine-tune: 10 runs, about 1.1 GPU-h each on an A6000, about 1.7 h on gaint.
- **Machine: gaint** (team-lead ruling). tmux `=f1g` (`scripts/f1_gaint_lanes.sh`): lane `pre` (pretraining, batch 32, about 16 GB); lane `A` (A5c-f1 s0-4 one after another, alongside pretraining); lanes `M1`/`M2` wait for `encoder_final.md5`, run gate F2, then MIM5 s0/2/4 and s1/3. Every fine-tune waits for ≥ 7,000 MiB free before it starts (the user's jobs first). Gates F1 (I1/I2, done on gaint, `identity_f1.txt`) and F2 (200-step smoke with `encoder_final.pth`, md5 match, finite loss) are logged in `reports/f1g/launch.log`. The cv02 orchestrator (`f1_orchestrate.sh`, batch 64) is kept unused.
- Deployment: `git archive` of the approved commit to cv02 `/tmp/noob_el/el_f1` with `REVISION`, `data -> /tmp/noob_el/el_p7/data`. Split md5s equal gaint's (train `842f27c4`, val `9dcccf00`, test `a31fad14`, external `34d191cb`); pool image bytes equal on both machines (v0 list checked; v1 list re-checked before launch).
- tmux: one window per run, chained queues; finished cv02 runs relayed to gaint `cv02_noob_el/` via the laptop with MD5 on both hops.

## Not claimed
- That MIM cannot help with a longer schedule, another objective (contrastive, distillation), another mask or another pool. One schedule, one objective.
- Anything at 100% labels unless the 100% arm runs.
- Anything about E1 beyond the descriptive secondary.
