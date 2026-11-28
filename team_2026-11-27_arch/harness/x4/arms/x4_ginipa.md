# x4_ginipa: GIN + IPA augmentation with consistency (builder loss; ledger P012 gin_ipa, never run)

## What it changes
Ouyang et al., Causality-inspired single-source domain generalization for medical image segmentation, IEEE TMI 2022, doi:10.1109/tmi.2022.3224067 (Sec. III-B to D, Algorithm 1). The arXiv text lost the equations, so details follow the official code (github.com/cheng-01037/Causality-Medical-Image-Domain-Generalization: models/imagefilter.py, biasfield_interpolate_cchen/adv_bias.py, models/exp_trainer.py, configs_exp.py), on the single-channel normalised network input, after the house label-safe augmentation:
- GIN: per sample a random 4-layer conv net (1 -> 2 -> 2 -> 2 -> 1 channels, kernel 1 or 3 per layer, N(0,1) kernels and biases, leaky ReLU 0.01, none after the last), mixed with the input by a ~ U(0,1), rescaled to the input's per-sample Frobenius norm. No geometric change (label-safe).
- IPA: per sample a B-spline pseudo-correlation map (6 x 6 N(0,1) control points, spacing 1/4 of the side at half resolution, quadratic B-spline, bilinear to full size, exp, min-max to [0,1]); T1 = M g1 + (1-M) g2, T2 = (1-M) g1 + M g2.
- Step: one forward of [T1 | T2 | g3] (3 x 8 images); house CE + Dice on T1 only (as their code); consistency = mean over N x C x H x W of KL(mean softmax of the 3 views || each view), no detach (their KLDivLoss 'mean'), weight 10 (their lambda_consist). Logged as loss_con and lambda on the step line.
- Draws are a pure function of (seed, step) (generator on the device seeded by (seed, 41, step)), so a resumed run draws the same views.
- Recipe change by nature (say so in the read): the loss never sees the clean image; each step costs about 3 forwards and backwards (24 images). BN re-estimate (bn_recal), SWAD and the dumps use clean images as COMBO.
- Not used (S): their Adam settings, 192 px crops, EfficientNet-b2 U-Net and 2,000-epoch schedule (the COMBO recipe is kept).
- Keys: training.ginipa.{enabled=true, n_layer=4, interm=2, scale_pool=[1,3], grid_frac=4, lambda=10.0}.
- Code: src/trainers/ginipa.py; src/trainers/trainer.py (supervised branch, opt-in).
- Precomputed inputs: none. Run time (S): about 2.5 to 3x COMBO (COMBO median 155 min on cv02).

## Common
- Branch x4_loss, worktree /home/noob/work/bench_wt_x4_loss, commit c9b93d8320504394a2d5418719f3a4a1bc85099d (arms 1 to 3 in 092026f, arm 4 in c9b93d8; both on bench_x4 41c931d, miro merged; merge is a fast-forward of bench_x4). cv02 deploy /tmp/noob_el/bench_c9b93d8 (CODE.md5 checked, CV02_CODE_OK). Queue calls need X4=c9b93d8320504394a2d5418719f3a4a1bc85099d and --repo /home/noob/work/bench_wt_x4_loss for x4_make_jobs.py (the card lives only on this branch).
- Comparator: COMBO card hrnet_w18_unetpp_swad_const_pf_v11; this arm = COMBO + exactly the keys listed (bench.cards diff and tests/test_x4_loss_cards.py). Readouts as COMBO; compare the swad readout with COMBO's swad readout.
- Identity (keys off), E: 5 CPU steps (identity_cpu.py 962379a6 / compare_id.py 3b83b364), seed 5, cv5v3_v11_f0, fresh git archive of bench_x4 41c931d vs c9b93d8: COMBO card opts IDENTICAL; x4_miro card opts IDENTICAL (the merged arm is unchanged by this branch). Earlier rounds: 23717a7 vs 34cca2f (arms 1-3) IDENTICAL; 399f963 vs ec3562e (arms 1-4) IDENTICAL. Logs: /home/noob/work/bench_x4loss_io/check{,2,3}/run.log.
- Unit tests, E: tests/test_x4_loss.py (shape, gradient, hand-computed values; factory and trainer with keys off unchanged), tests/test_x4_loss_cards.py. Full pytest at c9b93d8: 804 passed, 12 skipped, 2 failed (test_variants_exist and test_shv_reproduces_shv1_on_real_val_cells; both fail identically on 41c931d: pre-existing / data links of a fresh worktree).
- Peak and gate, E: PENDING: 200-step smoke smoke_x4_gin_f0_s5 (jobs/loss_smoke.tsv md5 0616aee5, guessed gate 28,048) to run inside x4_w1; fill peak and gate = peak + 2,048 from its gpumem.log.
- Jobs (5 folds x seeds 5, 6), on gaint in harness/x4:
  `python x4_make_jobs.py --repo /home/noob/work/bench_wt_x4_loss --commit c9b93d8320504394a2d5418719f3a4a1bc85099d --out jobs/<file>.tsv bench/methods/x4_ginipa.yaml=gin@<PEAK>`
  (10 lines x4_gin_f0..4_s5,6, 11th field = deploy c9b93d8; gate = max(card gate 11,000, peak + 2,048)); then append to the shared cq_x4.sh queue (`X4=c9b93d8320504394a2d5418719f3a4a1bc85099d bash x4_queue.sh append <qn> jobs/<file>.tsv`) or place / arm a queue of its own as RUNBOOK section 2; relay and score as usual.
- Installs: none (house venv; scipy already present). Weights: the COMBO encoder file only (md5 e6bb005ddbe1b52bde05618fc6b4b8e3).
