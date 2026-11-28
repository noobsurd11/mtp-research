# x4_cra: crack-to-region architecture arm (builder cra, 28 Nov 2026)

## What it changes
THE ARCHITECTURE: COMBO + Part R (region head on the inactive logit) + Part D (geomaux heads inside the model + direction-guided bridging readout swad_bridge). One network; ablations x4_cra_region and x4_cra_dir. Params +395,461.
Papers: arXiv:1612.01105, arXiv:1511.07122, arXiv:2302.05543, doi:10.1038/s41592-022-01711-z, doi:10.1016/j.patcog.2025.112797.
Card bench/methods/x4_cra.yaml md5 733eea8a1a5d0289eed9f120974c9621 (cv02 variant: weights path only). Weights: COMBO encoder file only (e6bb005ddbe1b52bde05618fc6b4b8e3). Installs: none. Precomputed inputs: none (geomaux targets are built per augmented train cell in the data workers).

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

## Bridging thresholds (fixed in the card before any run)
Sources: cpu/REPORT.md section 4 (EXT, cross-fitted endpoint extension on COMBO out-of-fold dumps; each fold's choice made on
the other four folds) and training-target reasoning. No held-out fold, test50 or E1 read was made for these values.
| key | value | why |
|---|---|---|
| ang | 50 deg | all 10 EXT fits chose 50 (grid 30, 50) |
| trace | 4 px | 9 of 10 EXT fits chose k 4 |
| margin_floor | -8 | all 10 EXT fits chose t -8; the in-sample optimum -12 (REPORT 4.4) was not adopted |
| max_len | 12 px | EXT fits chose 24, 12 or 6: the median; the distance gate ends walks earlier anyway |
| max_gap | 16 px | largest gap an EXT fit chose; every linked px must also pass the distance gate (EXT had none) |
| walk_dist | 1.5 px | distance head = L1 regression of the clipped distance to the nearest GT crack px: 0 on the line, 1 for a 4-neighbour, 1.41 diagonal; 1.5 allows one diagonal step off the line, inside the 2 px relF1 tolerance |
| bridge_dist | 2.0 px | a straight link across a gap of a slightly curved crack may sit up to the 2 px tolerance off it |
| dir_norm | 0.5 | the head regresses unit (cos 2t, sin 2t); a predicted norm under 0.5 = ambiguous axis, then the geometric trace direction is used (as EXT) |
| add_margin | 1.0 | added px get crack logit = max other + 1: clear argmax for the writer's consistency check; a crack bias of -1 removes them again (EXT used +0.0005, which made its OP-W return COMBO) |
| dist_clip | 10 | = training.geomaux.dist_clip (trainer refuses a mismatch) |
Bridging smoke on COMBO OOF swad dumps (E; surrogate maps since COMBO has no heads: distance 0 where m_crack > -8 else 10,
direction = crack_geom of the predicted crack; no GT read, decides nothing): seeds 5 / 6, 532 cells each: 10,413 / 10,821 px
added (0.034 / 0.035 of predicted crack px), 232 / 225 cells touched, two passes equal in every cell, every edited cell passes
dumpfmt.check_cell, 7 ms per cell (bench_x4cra_io/bridge_smoke.py, bridge_smoke.json).

## Readouts for the read
PRIMARY swad_bridge readout vs COMBO swad (the full architecture: crack relF1@2 and inactive IoU); also swad vs COMBO swad (Part R + heads, no bridging step). Same read note as x4_cra_dir.
Queue 10th field: `swad,swad_bridge`.

## Jobs (cwd harness/x4; after a merge into bench_x4 use the merged commit and --repo /home/noob/work/bench_wt_x4)
200-step memory smoke (tested, E; guess @10200):
`python x4_make_jobs.py --repo /home/noob/work/bench_wt_x4_cra --commit 613f991bd091aed4a15b339d14253909b853722d --seeds 5 --folds 0 --extra '--exit_after_step 200' --out jobs/<file>.tsv bench/methods/x4_cra.yaml=cra@10200`
Stage P (seed 5 x 5 folds) and stage S (seed 6 x 5 folds), PEAK = smoke peak + 748:
`python /home/noob/work/bench_x4cra_io/harness_patch/b/x4_make_jobs.py --repo /home/noob/work/bench_wt_x4_cra --commit 613f991bd091aed4a15b339d14253909b853722d --readouts swad,swad_bridge --seeds 5 --out jobs/<file>.tsv bench/methods/x4_cra.yaml=cra@<PEAK>`
`python /home/noob/work/bench_x4cra_io/harness_patch/b/x4_make_jobs.py --repo /home/noob/work/bench_wt_x4_cra --commit 613f991bd091aed4a15b339d14253909b853722d --readouts swad,swad_bridge --seeds 6 --out jobs/<file>.tsv bench/methods/x4_cra.yaml=cra@<PEAK>`
(until the harness patch is applied, run the patched copy shown; after applying it, the same arguments with harness x4_make_jobs.py. The smoke line needs no --readouts: smokes run no dump.)
