# x4_cra_region: crack-to-region architecture arm (builder cra, 28 Nov 2026)

## What it changes
COMBO plus Part R only: the crack-to-region head (src/models/cra.py RegionHead) adds a zero-initialised residual to the inactive logit (class 11) from the final decoder features, the detached crack probability (softmax class 14) and a large-receptive-field context path (three stride-2 convs to 1/8, dilated residual blocks 2/4/8, global mean term, nearest upsampling; about 240 px plus whole-cell context). Keys: model.cra.{region=true, region_ch=96, region_ctx=8, region_mid=16, crack_detach=true, crack_cls=14, inact_cls=11}. Params +395,393. Ablation of x4_cra (no Part D).
Papers: PSPNet global context arXiv:1612.01105; dilated context arXiv:1511.07122; zero-initialised residual (ControlNet zero conv) arXiv:2302.05543.
Card bench/methods/x4_cra_region.yaml md5 cf319db3ef76f678054f4592b4475e3c (cv02 variant: weights path only). Weights: COMBO encoder file only (e6bb005ddbe1b52bde05618fc6b4b8e3). Installs: none. Precomputed inputs: none (geomaux targets are built per augmented train cell in the data workers).

## Commit, identity, tests (shared)
- Branch x4_cra, worktree /home/noob/work/bench_wt_x4_cra, commit **613f991bd091aed4a15b339d14253909b853722d** on bench_x4 8da53f6 (fast-forward). Not pushed, not deployed.
- Identity (keys off), E: 5 CPU steps, fresh archive 8da53f6 vs 613f991 (identity_cpu 962379a6, compare_id 3b83b364): COMBO IDENTICAL, x4_geomaux IDENTICAL (geomaux.py was touched), x4_miro IDENTICAL, x4_vfmctx IDENTICAL (log /home/noob/work/bench_x4cra_io/check1/run.log).
- Unit tests, E: tests/test_x4_cra.py 22 passed (config checks; zero-init equality of RNG, pixel path, forward and pixel-path gradients with the plain model; region gradients; crack channel detached / not detached; hand-computed region Dice with ignore px; bridging on hand-drawn maps: extension follows the distance head, max_len, margin floor, linking only when the head agrees, gap limit, facing rule, direction head followed on a bend and rejected beyond ang, determinism; logit edit; bridging only in eval with the flag; geomaux heads key; SWAD keeps the flag 0 and averages the heads; trainer step with in-model heads, final-step swad_bridge, resume drops it; refusals; keys off builds nothing; cards = COMBO + exactly the named keys). Related suites 160 passed, 2 failed (test_bench_cards_cv02 test_variants_exist and [x4_vfmctx], identical on 8da53f6, pre-existing).
- CPU arm-on smokes, E: 5 steps per card, rc 0, losses finite, step-1 loss_sup = COMBO's 4.275284767150879 bit for bit (zero init); CPU step time vs COMBO (mean of steps 2 to 5, 12 runs at once on gaint): region 1.055, dir 0.985, cra 1.076, rdice 1.068 (COMBO ref vs new 0.963 = the noise level).
- End-to-end CPU check through the unchanged bench_infer.py, E (bench_x4cra_io/e2e_run.sh, e2e_prep.py; cv5v3_f0, 107 open cells, no score computed): COMBO c3x f0 s5 swad weights loaded into (a) the COMBO config and (b) the x4_cra model (region out layer zero, geo heads set to constants: distance 0, horizontal direction; surrogate), dumped on CPU fp32: COMBO swad vs x4_cra swad 107 of 107 cells byte-identical (npz md5); x4_cra swad_bridge: writer bench_infer.py afd9164264de4d91e43e258e6f8b1836 on all three dumps, ties 0, 45 cells differ from swad, 1,867 crack px added, 0 removed, 0 other class changes (76,540 crack px in swad). Dumps deleted after the check.
- Peak (S, not measured on a GPU): activations saved for backward per 512 px image (E, CPU fp32): COMBO 1,528 MiB, +Part R 128 MiB (+8.4%), +Part D 4 MiB. Scaling COMBO's 9,386 MiB: region / cra about 10,200 MiB full run, dir about 9,400 (+ geomaux targets, x4_geomaux guess 9,600). The 200-step memory smoke is inside the PF freeze, so full-run peak = smoke peak + 748 MiB (integrator's COMBO difference).
## Code (shared by the x4_cra cards)
- src/models/cra.py (new): `model.cra` keys. `RegionHead` (Part R), `GeomAuxHeads` of src/trainers/geomaux.py built inside the model (Part D heads), `bridge_added` / `bridge_logits` (Part D readout, numpy, deterministic), `region_dice` (optional region aux loss), `_CRAMixin` / `cra_class` (smp U-Net++ / U-Net subclass: `forward_cra` returns final logits, geo outputs, decoder features; `forward` = final logits, bridged only in eval mode when the buffer `cra_bridge_on` is 1).
- src/models/bench_models.py: `model.cra` branch in bench_smp (refused with vfm_ctx or other decoders). Absent key: nothing changes.
- src/trainers/geomaux.py: new key `training.geomaux.heads` = own (default, x4_geomaux unchanged) | model.
- src/trainers/trainer.py: heads=model path (one `forward_cra`, `geomaux_loss` of x4_geomaux on the model's own heads, model optimizer and clip, same 'geomaux' log line); `training.cra_region_aux` (Dice term, 'cra' log line); final-step readout `<readout>_bridge` (= the readout state dict with `cra_bridge_on` = 1) written into latest.pth, dropped again on resume; refusals for every inconsistent combination (in-model heads without heads=model, heads=model without model.cra.geo, bridge readout not in the run, dist_clip mismatch, region aux without region).
- tests/test_x4_cra.py (new).
- Not changed: scripts/bench_infer.py (md5 afd9164264de4d91e43e258e6f8b1836, so every readout, including swad_bridge, is written by the COMBO writer), bench/dumpfmt.py, data code, weight_avg.py, queue scripts.

## How the bridged readout reaches the read
- latest.pth at step 20,000 holds models[swad_bridge] (about 84 MB more on cv02 per run: one more model-shaped state dict).
- Queue: 10th field `swad,swad_bridge` (cq_x4.sh already accepts any card readout key and forms `--run-id <name>.swad_bridge --weights-key swad_bridge`).
- Relay: x4_relay.sh READ_ONLY skips only the primary dump folder `<name>/`, so `<name>.swad` and `<name>.swad_bridge` are both pulled (E: skip regex ` dumps/elbench1/[^/]+/$n/`).
- Read: read_x4.py with `--arm 'X=<template of <run>.swad_bridge>:5:swad_bridge'`; x4_read.sh maps only key swad to the `.swad` suffix today.
- Harness patch (NOT applied; proposed): /home/noob/work/bench_x4cra_io/harness_patch/x4_cra_harness.patch (copy in arms/x4_cra_harness.patch): x4_make_jobs.py `--readouts swad,swad_bridge` (checked against the card's readouts), x4_read.sh key swad_bridge -> suffix .swad_bridge.


## Readouts for the read
swad readout vs COMBO swad (crack relF1@2 and inactive IoU). x4_read.sh key `swad` (works today).
Queue 10th field: `swad`.

## Jobs (cwd harness/x4; after a merge into bench_x4 use the merged commit and --repo /home/noob/work/bench_wt_x4)
200-step memory smoke (tested, E; guess @10200):
`python x4_make_jobs.py --repo /home/noob/work/bench_wt_x4_cra --commit 613f991bd091aed4a15b339d14253909b853722d --seeds 5 --folds 0 --extra '--exit_after_step 200' --out jobs/<file>.tsv bench/methods/x4_cra_region.yaml=cra_region@10200`
Stage P (seed 5 x 5 folds) and stage S (seed 6 x 5 folds), PEAK = smoke peak + 748:
`python x4_make_jobs.py --repo /home/noob/work/bench_wt_x4_cra --commit 613f991bd091aed4a15b339d14253909b853722d --seeds 5 --out jobs/<file>.tsv bench/methods/x4_cra_region.yaml=cra_region@<PEAK>`
`python x4_make_jobs.py --repo /home/noob/work/bench_wt_x4_cra --commit 613f991bd091aed4a15b339d14253909b853722d --seeds 6 --out jobs/<file>.tsv bench/methods/x4_cra_region.yaml=cra_region@<PEAK>`
