# x4_lowfreeze: HRNet stem and stage 1 frozen for the whole run (builder geo)

## What it changes
COMBO (hrnet_w18_unetpp_swad_const_pf_v11) with the low-level layers of the HRNet-W18 encoder frozen for all 20k steps (SHORTLIST_1127 arm A11 LOWFREEZE).
- Frozen modules (timm names under encoder.model): conv1, bn1, conv2, bn2 (the stem) and layer1 (stage 1), as in timm's own group_matcher (stem = conv[12] / bn[12], stage 1 = layer1). 45 tensors, 323,904 parameters; 15 BN modules.
- From step 0: requires_grad False, and scripts/train.py build_optimizer leaves them out of both PF groups (no Adam state, no weight decay). Trainable params in the optimizer: 20,471,788 of 20,795,692 (E, CPU smoke).
- Their BatchNorm layers stay in eval mode the whole run: they normalise with the ImageNet running statistics and never update them (each frozen module gets a bound train() that always sets eval mode; it survives deepcopy). The final BN re-estimate (raw_bn, swad_bn, ema_9998_bn) skips these BN modules, so every readout keeps the frozen statistics.
- Everything else exactly COMBO: the rest of the encoder keeps the PF schedule (frozen 1,000 steps, ramp 1,000, lr x 0.1, wd 0), SWAD 10k to 20k and EMA 0.9998 average every tensor as before (the frozen tensors stay bit-equal through the average: unit test), readouts and weights_key as COMBO.
- S: incre_modules.0 (timm's feature head that turns the stage-1 output into the reduction-4 decoder feature) and transition1 stay trainable, so the decoder's stride-4 skip can still adapt; the stride-2 skip (stem output) is fully frozen. To freeze more, add names to training.lowfreeze.modules (a list key).
- Papers: doi:10.1109/cvpr52734.2025.00435 (The Devil is in Low-Level Features), arXiv:2210.11466 (surgical fine-tuning, P166), arXiv:2211.09359 (fine-tune with SGD: freezing the stem closes the AdamW vs SGD gap under shift), SpotTUnet doi:10.1007/978-3-030-87199-4_20, MASTER P179.
- Keys: training.lowfreeze.enabled=true, training.lowfreeze.modules=[conv1,bn1,conv2,bn2,layer1]. Log: one 'lowfreeze:' line at start (modules, tensors, params, BN count, trainable count).
- Code: src/trainers/lowfreeze.py; scripts/train.py (apply after the model build; optimizer filter only when the key is on); src/trainers/weight_avg.py (bn_recalibrate skips BN marked _x4_frozen; none is marked with the key off); src/trainers/trainer.py refuses a lowfreeze config whose model was not frozen.
- Precomputed inputs: none.

## Commit, identity, tests
- Branch x4_geo, worktree /home/noob/work/bench_wt_x4_geo, commit 239cb7825607140e1ffe81c3eca298f2c1333a52 on bench_x4 892fc68 (merge = fast-forward of bench_x4). The same commit holds x4_geomaux (both keys off by default). Not deployed to cv02 by me (integrator deploys).
- Identity (keys off), E: 5 CPU steps (identity_cpu.py 962379a6 / compare_id.py 3b83b364), seed 5, cv5v3_v11_f0, fresh git archive of 892fc68 vs 239cb78: COMBO card opts IDENTICAL; x4_miro card opts IDENTICAL; x4_vfmctx card opts IDENTICAL. Log /home/noob/work/bench_x4geo_io/check1/run.log (geo_check.sh 7ca5725a).
- Arm-on CPU smoke, E: 5 steps with the card opts (geo_smoke_cpu.py c67a1bf2 = identity_cpu + apply_lowfreeze): rc 0, the hash of all stem + stage-1 params and buffers equal to its start value after every step, optimizer params 20,471,788, finite losses (step-1 loss 4.2175 vs COMBO 4.2753: the stem BN now uses running statistics, so the forward differs from step 1 by design). init_state equal to COMBO's.
- Unit tests, E: tests/test_x4_geo.py (15 tests for both arms): frozen params and BN buffers bit-equal after 3 Adam steps (with and without PF) while stage 2, incre_modules.0, transition1 BN, decoder and head move; frozen params in no optimizer group and without grad; modules stay in eval after model.train(); deepcopy keeps the freeze bound to the copy; bn_recalibrate leaves frozen stats and re-estimates the others; uniform SWAD keeps frozen tensors bit-equal; keys off = no change; card = COMBO + the 2 keys, cv02 variant differs only in the weights path. Related suites (weight_avg, trainer utils, x2, f3 PF, miro, vfm_ctx, x4_res, c3x / bench cards): 151 passed. Full pytest: see BUILD_geo.md.

## Peak and gate
COMBO model and batch, so no smoke (lead ruling 27 Nov 23:33): COMBO cv02 training peak 9,386 MiB, job gate 11,434 MiB. Freezing removes gradients and Adam state of 323,904 params (about 4 MiB less).

## Jobs (5 folds x seeds 5, 6), on gaint in harness/x4
Before the merge (card read from the branch commit; needs cv02 deploy /tmp/noob_el/bench_239cb78):
`python x4_make_jobs.py --repo /home/noob/work/bench_wt_x4_geo --commit 239cb7825607140e1ffe81c3eca298f2c1333a52 --out jobs/<file>.tsv bench/methods/x4_lowfreeze.yaml=lowfreeze`
(tested, E: 10 lines x4_lowfreeze_f0..4_s5,6, gate 11,434, dump gate 6,200, readouts swad, 11th field the commit; test file md5 0631fbcb in /home/noob/work/bench_x4geo_io/jobtest, not in jobs/). After a merge into bench_x4, use the merged commit and --repo /home/noob/work/bench_wt_x4 instead. Then append to x4_w1 as RUNBOOK section 2 (integrator's call).
Installs: none. Weights: the COMBO encoder file only (md5 e6bb005ddbe1b52bde05618fc6b4b8e3).
Judged on cv5v3: in-distribution yes; the domain-generalisation claim of A11 needs U1 or the new unseen set.
