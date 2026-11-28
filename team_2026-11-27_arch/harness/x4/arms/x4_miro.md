# Arm x4_miro: handover (builder miro, 27 Nov 2026)

E = measured, S = judgement. Full step log: harness/x4/arms/BUILD_miro.md.

## What the arm changes
COMBO (hrnet_w18_unetpp_swad_const_pf_v11) plus MIRO, a mutual-information regulariser that keeps the tuned encoder features close to a frozen pretrained copy (SHORTLIST_1127 A03). Nothing else changes: PF schedule, SWAD 10k to 20k, ema_9998, BN re-estimate, readouts, weights_key swad_bn, swad readout for the x4 comparison.

Paper: Cha et al., "Domain Generalization by Mutual-Information Regularization with Pre-trained Models", ECCV 2022, doi:10.1007/978-3-031-20050-2_26. Method read through the Research MCP (arXiv copy: sections 3.1, 3.3, 4.1, 4.2, A, B.1, B.2) and the official code github.com/kakaobrain/miro (domainbed/algorithms/miro.py md5 e2c59c10ed46a91d8aaf76be99177eb4, README md5 a5f11341f712b185f2bc3004f697c914).

### Equations used
- Paper Eq. 6, constants dropped: L = E_S(h) + lambda * E[ log|Sigma(z_f)| + ||z_f0 - mu(z_f)||^2 in the Sigma(z_f)^-1 metric ].
- Implementation, as in the official code: reg = sum over layers l of 0.5 * mean over (N, C, H, W) of [ (f_l - f0_l)^2 / var_l[c] + log var_l[c] ]; loss = house CE + Dice + lambda * reg. Computed in float32.
- Mean encoder = identity. Variance encoder = one bias per channel, var = softplus(b) + 1e-5, initialised to 0.1 (paper 3.3 and B.2, and the code).
- Layers (S): the 5 features the tu-hrnet_w18 encoder hands to the U-Net++ decoder: the stem at /2 with 64 channels, and the incre outputs of the 4 stage-4 branches (/4 128, /8 256, /16 512, /32 1024). This matches the paper's ResNet choice (stem + blocks 1 to 4). Index 0, the input image, is excluded.
- f0 = a frozen deep copy of the encoder as built (ImageNet weights, timm hrnet_w18.ms_aug_in1k md5 e6bb005d), with no gradient. Its BN layers normalise with batch statistics at momentum 0, so their running stats never change (S). Reason: the tuned encoder trains BN with batch statistics, so f = f0 exactly at the start, as in the paper (there DomainBed freezes BN in both copies). Eval-mode ImageNet statistics on grey EL would give f0 a different normalisation from f and pull toward another target. The copy is not checkpointed: train.py rebuilds the same encoder before a resume (exact-resume unit test).
- lambda = 0.1 (S). Source: the official SWAD commands for ImageNet RN50 use 0.1 on OfficeHome, TerraIncognita and DomainNet, and 0.01 on PACS and VLCS. The paper text gives only the grid 1, 0.1, 0.01, 0.001. TerraIncognita (camera-site shift, many grey infrared frames) is the DG shift closest to ours, and it shows the largest MIRO+SWAD gain (52.9 vs ERM+SWAD 50.0). Caveat: paper Figs. 3 and 5 show that with ImageNet backbones the gain falls as lambda grows on far domains. lambda 0.01 is the natural second arm if 0.1 hurts.
- Variance-encoder lr (S): its own Adam, lr = 10 x the encoder lr (paper B.2) = 1e-3 x 0.1 x 10 = 1e-3, weight decay 0, no clipping (MIRO clips nothing; the model clip is unchanged). It follows the encoder PF multiplier: 0 for 1,000 steps, then a 1,000-step ramp. During the freeze, f = f0 and var stays 0.1, so MIRO starts from the paper's initial state when the encoder starts to move. Without this, var would collapse toward 1e-5 during the freeze, and the term would act as a near-hard anchor at unfreeze.

## Code
- Branch x4_miro, commit 00635fd0d323a1d9b742735cf766aeb2e2a234d2 (= bench_x4 b3ec7a5 + 1 commit). Files:
  - src/losses/miro.py (new)
  - src/trainers/trainer.py: opt-in training.miro (build; step branch with an explicit smp forward that keeps the encoder features; separate optimizer and scheduler; checkpoint keys models.miro_var, optimizers.miro, schedulers.miro; its own log line)
  - src/trainers/weight_avg.py: RESERVED + miro_var
  - card bench/methods/x4_miro.yaml (md5 f75b8c69f5d8cffce1f80b51326c3c20) and bench/methods_cv02/x4_miro.yaml (weights path only)
  - tests/test_x4_miro.py, tests/test_x4_miro_card.py
- Card = COMBO + training.miro.lambda=0.1, training.miro.var_init=0.1, training.miro.lr_mult=10.0. bench.cards diff lists exactly these 3 keys; validate OK; cvcard OK. The card memory fields are provisional (peak null, gate 11,434): fill them after the x4_w1 smoke, or pass @PEAK to x4_make_jobs.py.
- Deployed: cv02 /tmp/noob_el/bench_00635fd (CODE.md5 013169b5, 785 files, CV02_CODE_OK).
- Log: one extra line per log window, "miro reg=.. d1..d5=.. var1..var5=.. at step N" (d_l = mean (f - f0)^2, var_l = mean variance). The step line keeps its keys; its loss includes lambda x reg.

## Tests (E)
- tests/test_x4_miro.py, 8 passed:
  - variance init is 0.1
  - hand-computed value 10.19741 (layer 1: f [1, 3], f0 [0, 1], var 0.1; layer 2: f = f0)
  - equal to the official code formula on random tensors
  - gradients: d reg/d f = (f - f0)/(var N); no gradient into f0; analytic gradient on b
  - the variance optimum is the per-channel mean squared deviation
  - trainer on a CPU HRNet-small U-Net++: the reference equals the built encoder; during the PF freeze d = 0 exactly and var = 0.1; both move after it; reference weights and BN running stats unchanged; exact resume, miro_var included
  - keys off: no MIRO state
- With test_weight_avg, test_trainer_utils, test_absh, test_thin_crack: 59 passed.
- Card tests: 63 passed, 1 failed = test_bench_cards_cv02.py::test_variants_exist. This failure predates the arm (BUILD_LOG_x4 22:54:20).

## Identity (E)
IDENTICAL. Check: identity_cpu.py (962379a6) and compare_id.py (3b83b364), COMBO card opts, seed 5, cv5v3_v11_f0, 5 CPU steps, git archive 399f963 vs bench_wt_x4_miro at 5da7137. Result: "IDENTICAL (5 steps, all fields except code / sec)", covering loss values, lrs, the sha256 of every parameter and buffer, and the eval logits. 5da7137 -> 00635fd is a rebase onto b3ec7a5 with 0 lines changed in src, scripts, configs, tests and bench/methods*. Log: /home/noob/work/builder_scratch/miro/check/run.log.

## Memory
- Not measured on a GPU (lead ruling: arch_harness runs the 200-step smoke in x4_w1). My own queue x4_mirosmoke was placed but never armed, and HOLD is set (cv02 /tmp/noob_el/bench_q/x4_mirosmoke holds jobs.txt only). It can be deleted.
- Same-conditions reference (E): x4_ressmoke smoke_x4_combo_f0_s5 (COMBO, f0 s5, 200 steps) peaked at 8,638 MiB; the full COMBO run peaks at 9,386 MiB (c3x). Full-run estimate for x4_miro = 9,386 + (x4_miro 200-step peak - 8,638).
- Expected extra memory (S, from tensor sizes at batch 8 and 512 px; the 5 layers hold 8.13 M feature elements per image):

  | Item | Extra |
  |---|---|
  | frozen copy weights | 42 MiB |
  | reference features kept for the loss (bf16) | 124 MiB |
  | fp32 tensors autograd saves for the MIRO term (diff for pow, sq for the division) | about 496 MiB |
  | frozen forward under no_grad, transient at the end of the tuned forward | a few hundred MiB |
  | **total over COMBO** | **about +0.7 to 1.2 GiB** |

  Expected peak: about 10.1 to 10.6 GiB, so the gate is about 12.2 to 12.7k MiB. Suggested smoke gate: 12,548 (as in jobs/mirosmoke.tsv) or 13,000.
- Step time (S): one extra encoder forward without backward. Expect about 1.2 to 1.3x COMBO (the recipe report says about 1.3x).

## Precomputed inputs
None.

## Jobs (x4_make_jobs.py; PEAK from the x4_w1 smoke)
Stage P (seed 5, 5 folds):

    python x4_make_jobs.py --out jobs/<qn>.tsv --repo /home/noob/work/bench_wt_x4_miro --seeds 5 --commit 00635fd0d323a1d9b742735cf766aeb2e2a234d2 bench/methods/x4_miro.yaml=miro@<PEAK>

Stage S (add seed 6): the same command with --seeds 6.
Memory smoke (for x4_w1): the same command with --seeds 5 --folds 0 --extra "--exit_after_step 200" and @12548 (a gate guess).
Read: x4_read.sh <tag> MIRO=<qn>:miro:x4_miro:swad

## 5-step CPU smokes with MIRO on (E, 27 to 28 Nov, cv5v3_v11_f0, seed 5, real data, train.py)
- Card as is: rc 0, no Traceback. Steps 1 to 5 (inside the PF freeze): every step has d1..d5 = 0 exactly, var = 0.1 and reg = -5.756 (= 5 x 0.5 x ln 0.1). The step loss equals loss_sup + 0.1 x reg (step 1: 4.275 - 0.5756 = 3.700). This confirms that the reference equals the tuned encoder until it moves.
- With encoder_pf.freeze=2, ramp=1: rc 0. d becomes > 0 from step 4 (step 5: d1 2.4e-9 to d4 1.8e-6), and var starts to move (0.09999).
- latest.pth: models [ema_9998, ema_9998_bn, miro_var, model, raw_bn, swad, swad_bn], optimizers [miro, model], schedulers [miro, model]. SWAD, EMA and the BN re-estimate run unchanged.
- cfgcheck vs card: the only differences are the smoke overrides (steps, val, log, checkpoint, probe, swad window, workers, and in the second run freeze/ramp).
- Full pytest on the branch: 775 passed, 12 skipped, 2 failed. Both failures predate the arm: test_bench_cards_cv02::test_variants_exist (BUILD_LOG_x4), and test_bench_udev::test_shv_reproduces_shv1_on_real_val_cells, which fails identically on the 399f963 archive (its card-name set is out of date).
