# Wave 2a: gates before the read (builder, 17 Nov 2026, 04:00 IST)

Status: the three gates that `harness/LAUNCH_REQUEST_w2a.md` section 8 listed as NOT BUILT are built and run. **No arm result is in this file and none was read.** The read itself (`harness/w2a/read/run_read_w2a.sh`) waits for the dumps (about 08:15) and for the independent review.
All runs on gaint, CPU only. Code: `harness/w2a/read/`. Outputs: `/home/noob/work/bench_reads/w2a_gates/` (G below). E = measured, S = judgement.

## Verdicts
| Arm | Gate (section 8) | Verdict | Evidence (file; command) |
|---|---|---|---|
| ema_wise_posthoc | raw `models[model]` of w2a_ema = W1-G PF of the same fold and seed, bit for bit | **PASS** | `G/gate_ema_hash_r1/gate_ema_hash.txt`; `python gate_ema_hash.py --out G/gate_ema_hash_r1` |
| swad_const | (a) training loss over 15k to 20k not above PF's at 10k | **PASS** (10 of 10 runs) | `G/gate_swad_prescreen_r2/gate_swad_prescreen.txt` (04:59; r1 of 03:47 has the same (a) and (c)); `python gate_swad_prescreen.py --out G/gate_swad_prescreen_r2` |
| swad_const | (b) fold 0: swad_bn crack relF1@2 >= PF raw - 0.05 | **PASS** (seed 5 and seed 6) | same file; records in `G/gate_swad_prescreen_r2/b/` |
| swad_const | (c) report layer3 / layer4 cosine at 20k | reported (not pass / fail): layer4 below 0.8 in 7 of 10 runs | same file |
| swad_const | overall, stricter rule: (a) on all 10 runs and (b) on both fold-0 seeds | **PASS** (as the spec wrote it, fold 0 seed 5 only: also PASS) | `G/gate_swad_prescreen_r2/VERDICT` |
| encoder_spd | mechanism gate: C1 layer3 / layer4 cosine >= 0.8 | **FAIL** (0 of 10 runs) | `G/gate_spd_mech_r2/gate_spd_mech.txt`; `python gate_spd_mech.py --out G/gate_spd_mech_r2` |
| encoder_spd | C2 >= 0.1 above the control w2a_spdctrl_f0_s5 | **PASS**, narrow (matched run fold 0 seed 5) | same file |
| encoder_spd | C3 conv1 / layer1 deviation > PF's | **PASS** (10 of 10 runs) | same file |
| encoder_spd | overall | **FAIL** | same file |
| rcs | per-fold sampler pre-check | PASS (section 8, builder x1; not re-run here) | `harness/LAUNCH_REQUEST_w2a.md` section 8 |
| soft_band_jml | P1 (band a, sigma) | PASS (section 8, builder x2; not re-run here). Dumps incomplete until w2a_softband_f1_s6 is retrained | same |
| jml_hard | none (control) | n/a | same |

**Note to carry beside any swad_const result (E):** layer4 cosine to init at 20k is below 0.8 in 7 of 10 swad runs (0.782 to 0.810; layer3 0.827 to 0.832, none below). Section 8 only asks to report this; it is not a pass / fail item. PF keeps layer4 at 0.926 to 0.946.

Gate verdict files read by the read script: `G/<gate>_r<number>/VERDICT` with the highest number, and the file must be exactly `<gate> PASS` (state at 05:00: gate_ema_hash_r1 PASS, gate_swad_prescreen_r2 PASS, gate_spd_mech_r2 FAIL). Lead's rulings (17 Nov 04:03): an arm with a gate that did not pass is read only under `GATE_ACK`, marked in run.log and in `GATE_ACK.txt` as descriptive only, not a screen verdict; encoder_spd will be read that way. C2 is reported as the matched comparison, the other 9 runs as context.

## gate_ema_hash (E)
- All 10 runs EQUAL: every one of the 350 tensors of `latest.pth` `models['model']` (step 20000) has the same bytes in w2a_ema_f<k>_s<s> and w1g_pf_v11_f<k>_s<s>; one sha256 per state dict (sorted keys; name, dtype, shape, bytes) is equal in each pair.
- Self-test of the comparison: a state dict against itself is EQUAL; one element moved by one float step is found (1 key, 1 element); PF fold 0 seed 5 against seed 6 is DIFFERENT (292 of 350 keys).
- The md5 of each `latest.pth` equals `checkpoint_md5` in the manifests of the dumps made from it (10 PF dumps; the 10 ema dumps that existed at 03:39).
- S: the wave 2a tree (c57508e) with the averagers on reproduces W1-G (31c0c36) exactly on this GPU. So the ema arm's raw readout is PF itself, and the primary contrast ema_9998_bn minus raw_bn is a within-run contrast on PF's own weights.

## gate_swad_prescreen (E)
- (a) Source: the trainer's lines `step N/20000  loss=X` in `train.log` (one per 50 steps; X = mean loss of the 50 steps ending at N). swad side: equal-weight mean of the 100 lines N = 15050 to 20000, which is the mean loss of steps 15,001 to 20,000. PF side: the one line N = 10000 of the W1-G run of the same fold and seed (mean of steps 9,951 to 10,000). Rule: swad mean <= PF value.
- (a) Numbers: swad mean 0.299 to 0.319; PF at 10k 0.317 to 0.375; swad minus PF -0.059 to -0.018 (closest: fold 3 seed 6). 10 of 10 pass; fold 0 seed 5 (the run the spec named) passes. The full-precision values in `metrics.json` give the same verdicts. Beside, not the rule: against PF's mean over steps 9,501 to 10,500 all 10 also pass (-0.046 to -0.035).
- (b) `scripts/bench_score.py` of `bench_wt_b` b5bf0ae (f096aff7): `records --labels v11` on the fold-0 dumps, then `summary`; relF1_2 on all 107 fold-0 cells at argmax. Seed 5: PASS. Seed 6: PASS (run r2, 04:59:09 to 04:59:35, after dump job 62 `w2a_swad_f0_s6.swad_bn` ended with rc=0 at 04:58:54; in r1 at 03:47 it was OPEN because the dump did not exist). The script prints pass / fail only. Command of r2: `cd harness/w2a/read && CUDA_VISIBLE_DEVICES="" PYTHONDONTWRITEBYTECODE=1 nice -n 19 /home/noob/work/el-fault-detection/.venv/bin/python gate_swad_prescreen.py --out /home/noob/work/bench_reads/w2a_gates/gate_swad_prescreen_r2`.
- (c) Cosine to init at step 20,000 (`enc_probe.jsonl`): layer3 0.827 to 0.832 (no run below 0.8); layer4 0.782 to 0.810, **below 0.8 in 7 of 10 runs**. `cards/WAVE2_REVIEW.md` asks for this to be said beside the swad result. PF itself: layer3 0.927 to 0.929, layer4 0.926 to 0.946 (20 W1-G runs, CPU pass below).
- Verdict rule used by the script: (a) on all 10 runs and (b) on both fold-0 seeds. As the spec wrote the pre-screen (fold 0, seed 5 only): PASS.

## gate_spd_mech (E)
- SPD and control values: the step-20000 row of each run's `enc_probe.jsonl`. PF values: a CPU pass over the 20 W1-G checkpoints with the trainer's own functions (`stage_stats`, `encoder_weights` imported from `bench_wt_w2/src/trainers/enc_probe.py`) and the init rebuilt as `train.py` builds it.
- The pass is the training-time probe: it reproduces the step-20000 probe row of all 21 runs that have one (10 spd, the control, 10 swad) within 1.2e-13; the rebuilt encoder equals the SPD anchors saved in the 10 spd checkpoints bit for bit; the init is the same for seeds 5 and 6; the weights file md5 equals the card's.
- C1: layer3 cosine 0.584 to 0.598, layer4 0.526 to 0.564. All 10 runs fail the 0.8 threshold.
- C2: control (lambda 0) layer3 0.441, layer4 0.443. Matched run fold 0 seed 5: +0.157 / +0.107, PASS. Beside: against that one control, 7 of 10 runs clear 0.1 on both stages; layer4 margins +0.084 to +0.121 (mean +0.105).
- C3: conv1 deviation 0.038 to 0.045 against PF 0.023 to 0.025; layer1 0.79 to 0.82 against PF 0.189 to 0.191. 10 of 10 pass (also by 1 - cosine).
- Pre-registered consequence of C1 (section 8; `cards/T1_recipes_spec.md` line 131), stated here, **not acted on**: one re-run at lambda 2.2 (new card version); if that also fails, drop SPD and record "SPD does not preserve at lr 1e-3"; L2-SP (alpha 0.01) is then the fallback arm.
- S: with C1 failed, a read of the lambda 1.0 runs is a read of "full encoder lr with a weak pull to init", not of the preserved-encoder arm the spec describes. `run_read_w2a.sh` therefore skips spd unless the lead names it in `GATE_ACK`.

## Limits
- The gates say nothing about accuracy. They check weights, training loss and encoder drift only; (b) is one fold, 107 cells, argmax, with a 0.05 tolerance, so it catches a failed arm and nothing finer.
- gate_ema_hash covers the raw weights only. The EMA and BN-recalibrated readouts have no reference to compare with.
- (a) uses one 50-step PF window as the reference, as the spec wrote it. That window is noisy (E): over the 20 PF lines from step 9,550 to 10,500 the highest minus the lowest line is 0.045 to 0.089 per run, more than the closest pass margin (0.018). The 1,000-step PF mean shown beside gives the same 10 passes.
- C2 rests on one control run (fold 0, seed 5). Its margin on layer4 (+0.107) is close to the threshold, and the spd runs themselves spread over 0.037 on layer4. The control's own spread is not known.
- Cosine and deviation are per stage over weight tensors with at least 2 dimensions (36 tensors), as the training-time probe defines them. BN parameters and biases are not in them.
