# Protocol DDeP5: decoder denoising pretraining, then fine-tune at 5% (v0, draft)

runner, 29 Oct 2026. Status: **v1, APPROVED by coach** (`review_ddep5_cp5_v0.md`, D1-D2 applied). Launch after I1-f2, the smoke and gate F2-DDeP; never ahead of MIM5. Direction #2 of `directions.md` (§3.2, settings agreed by coach and team-lead). Joint with MIM5: same machine (gaint), shared A5c-f1 arm, same rule.

## What I had seen when writing this
- MIM5 protocol v1.1 and its smoke/identity outputs; no MIM5 or A5c-f1 fine-tune number (runs in progress, not opened).
- No DDeP output of any kind.

## Question
Does a decoder pretrained by denoising on ~11.7k unlabelled EL cells (ImageNet encoder frozen) give a better 5% fine-tune than A5c's randomly initialised decoder, everything else fixed?
A win answers "decoder init helps at 5%", not "the pool's features help": the paper's Tab. 3 has ImageNet-21k decoder pretraining beating target data (R arxiv:2205.11423).

## Pre-stated expectation (S)
- Most likely n.d. (power as MIM5: crack threshold about 0.015, inactive about 0.05).
- If it helps: crack 0 to +0.03, inactive 0 to +0.05 (directions.md row 2). Our CNN U-Net++ decoder may train well from random, and lr 1e-3 for 20k steps may erase the pretraining.

## Arms (one change: the decoder init)
| Arm | Decoder init | Runs | Seeds |
|---|---|---|---|
| **A5c-f1** (shared with MIM5) | smp default (random, seeded) | `f1_A_5pct_s0..4` (gaint, 603e0d5) | 0-4 |
| **DDeP5** | `decoder_final.pth` of the one DDeP run | `f2_DDeP_5pct_s0..4` | 0-4 |

- Fine-tune opts: A5c verbatim (`protocol_mim5.md`) + `model.decoder_init=<decoder_final.pth>`. Nothing else: no lr change, no freezing (team-lead and coach: one change per arm).
- `decoder_init` loads `decoder.*` only (strict), never `segmentation_head`, after the build, with no random draw (tested): per seed the encoder (ImageNet), the 24-class head init, the data stream and augmentations equal A5c-f1's.

## Pretraining (one run, seed 0, final weights, no selection)
- **Code (D2):** gaint `el_f2`, branch `f2`, **deploy commit `2751aa8` for every f2 run**. `git diff 42bf7d1 2751aa8` touches only `scripts/cp_decoy.py`, `scripts/am_map.py`, `src/data/copy_paste.py` (CP residual fix P3, used only when `cp` is on) and tests, so the train path is 42bf7d1 (= 603e0d5 + DDeP `c33ed65` + CP hook): `scripts/pretrain_ddep.py`, `load_decoder_init` in `src/models/encoder_init.py`, 4 lines in `scripts/train.py`. Suite 277 passed, 3 skipped (6 DDeP tests: decoder-only load keeps encoder, head and RNG; strict; encoder frozen while decoder trains; noise formula; exact deterministic crops; switch off by default).
- **Network:** A5c's exact smp U-Net++ (ImageNet R34, 1 channel). Encoder weights frozen (no grad); **encoder BN in train mode** (batch statistics), so the decoder learns on the feature statistics it sees in fine-tuning. Decoder trainable plus a temporary 1x1 head (16 → 1 channel). The segmentation head is unused and not saved.
- **Noise:** x' = sqrt(γ)·x + sqrt(1 − γ)·ε on the normalised input, **γ = 0.95** (σ = 0.224 normalised, about 14 GL), the paper's tuned value; **predict ε**, MSE over all pixels.
- **Data:** the MIM5 list `mim_pool_v11.txt` (11,690, md5 `f0a5d74a...`), monitor `mim_monitor_v11.txt` (256, md5 `4a09f598...`). Random native-scale **256 x 256 crops** (integer offsets, no resizing; my choice, for speed: 4x cheaper than 512 and still 8 x 8 cells at the decoder's coarsest skip), then the label-safe set (h/v flip, rot90, brightness/contrast ±0.2 at p 0.4; D1: kept). Noise is added after normalisation, as in MIM and fine-tuning.
- **Optimisation:** Adam, lr 1e-4 after a 500-step linear warmup, cosine to 0; batch 32; **40,000 steps** (1.28M crops, about 110 epochs of crops); grad clip 1.0; bf16 autocast; wd 0.
- **Monitor:** held-out ε-MSE on the 256 monitor cells (full 512 cells, eval mode, fixed noise) every 2,000 steps; overfit check only.
- **Saved:** `dec_step0.pth` (random start), `decoder_final.pth` (+ md5) as `{"models": {"model": {"decoder.<key>": ...}}}`, including the decoder's BN running statistics.

## Checks before fine-tunes (gaint)
- **I1-f2:** commit 2751aa8 with no switch reproduces A5c-f1 s0's stdout (loss, lr, val lines) bit-identically for 2,000 steps (also the CP identity, protocol_cp5). Only then may DDeP5 share A5c-f1; otherwise A5c is re-run at 42bf7d1.
- **Smoke:** ≤ 500 DDeP steps: loss falls below the ε variance (1.0), no NaN, samples/s and peak memory; then a 200-step fine-tune with `decoder_init=` the smoke file: log line "Decoder initialised from ... (N tensors, md5 ...)" with the right md5, finite loss.
- **Gate F2-DDeP:** the same 200-step fine-tune smoke with `decoder_final.pth` (md5 match) before the five DDeP5 runs.

## Rule, sets, outcomes
As `protocol_mim5.md` v1.1: three primaries (test crack IoU, crack relF1@2, inactive IoU), rule 1 with the house divisor 3 (/5 descriptive), verdict on all 50 and without `CSIR_00070_r8_c4` (pass on both, or on one with a same-sign n.d. on the other; worse on either fails); without twins and without both reported; width flag relP@2 drop > 0.05.
- n.d. on all three: closed ("a denoising-pretrained decoder does not beat a random decoder at 5% on EL"); no 100% arm.
- **Multiplicity:** MIM5, DDeP5 and CP5 share A5c-f1: up to 3 arms x 3 primaries x 2 sets (+ CP's LA contrasts), no correction, disclosed.

## Reported (never change the verdict)
As MIM5 (four cell sets, per source, per class, crack capture, bootstrap, leave-top-3-out, LA secondary, E1 descriptive). Plus the free diagnostic: per-module relative decoder change ||θ_20k − θ_init|| / ||θ_init|| for A5c-f1 (θ_init rebuilt from the seed) vs DDeP5 (θ_init = decoder_final), to show whether fine-tuning erased the pretraining.

## Compute and machine (team-lead amendment, 29 Oct)
- **Pretraining (not pinned):** queued on cv02 (`/tmp/noob_el/el_f2`, REVISION 2751aa8, tmux `=f2ddep`, `scripts/f2_ddep_cv02.sh`): first GPU with < 1,000 MiB used; the 500-step smoke runs first with an automatic gate (finite, step-500 loss < 1.0, monitor at 500 below step 0) and a data gate (coach: the run's pool image-bytes manifest md5 must equal gaint's `855daabd...` and REVISION must be 2751aa8, else abort), then the full 40k-step run; the queue never takes a GPU with ≥ 1,000 MiB used, so never one another user holds above 4 GB. Pool bytes on cv02 equal gaint's (manifest md5 `855daabd` on both). If gaint has room (own peak + 2 GB free) before a cv02 GPU frees, the run moves to gaint (STOP file on cv02, logged). `decoder_final.pth` travels to the fine-tune machine with its md5 (laptop relay, MD5 both hops).
- **Fine-tunes:** gaint against A5c-f1 by default. If 3 or more cv02 GPUs free before DDeP5/CP5 are ready, DDeP5 + CP5 + a fresh A5c run on cv02 (one commit, identity checks there). The choice is written here before launch.
- Cost: DDeP pretraining to be measured in the smoke (S: 1-2 GPU-h on a free GPU). Fine-tunes 5 x about 1.2-1.7 h. Neither delays MIM5.


**Machine decision (19:50 IST, before launch):** fine-tunes on **gaint** against A5c-f1 (cv02 had 1 free GPU, used by the DDeP pretraining). I1-f2 passed (identity_f1.txt §5). Lanes: tmux `=f2g` (`scripts/f2_lanes_gaint.sh`): lane X starts after the MIM5 lane M2 ends, runs the CP smoke + decoy go/no-go, then gate F2-DDeP (decoder file from cv02, relayed via the laptop, md5 checked at both hops and again before use), then DDeP5 s0/2/4; lane Y after M1 ends: DDeP5 s1/3; so concurrency stays at 3 and MIM5 is never slowed. Every start waits for its own peak + 2 GB free.

## Not claimed
- That pool data is what helps (Tab. 3 caveat above). That another γ, target or schedule would not help.
