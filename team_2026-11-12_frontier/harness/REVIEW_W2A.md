# Review of wave 2a on gaint (reviewer-w2a, 14 Nov 2026, 00:54 to 01:20 IST)

Reviewed: `harness/LAUNCH_REQUEST_w2a.md` (integrator), worktree `/home/noob/work/bench_wt_w2` at c57508e, queue dir `/home/noob/work/bq/w2a`.
I built none of it. All checks are my own commands, read-only on el_bench, bq/w1g, bq/w1g2, bench_data and every existing worktree. My files on gaint: `/home/noob/work/bench_review_w2a/` only (rv_jobs.py, rv_env.sh, rv_id.sh, run.log, own archive of 31c0c36), plus the waiter of section 6 in `bq/w2a/`.
E = measured, S = judgement.

## Verdict
- Items 1, 2, 3: **PASS for all 7 cards** (6 arms + the spd control). No arm removed. Job md5s unchanged.
- Item 4: **PASS only with one change to the way the queue is armed.** Arming `launch_w2a.sh` now would let w2a start between W1-G2's last training run and its dumps (section 4). So the launch command runs from a waiter after the W1-G2 chain ends, as the lead did for W1-G2.
- **Launch: not done.** The permission system refused my command that starts the waiter. Nothing of w2a is armed (section 6 has the state and the one command needed).
- Not done: the request's item 8 (GPU smoke of the 6 new cards). My task did not include it and the GPU is full until about 08:40. Consequence in section 5.

## 1. Code, tests, identity: PASS
- E: `bench_wt_w2` HEAD c57508ec458b54d935a8c3ffcfe722ff2acadb38, 0 tracked changes, 0 untracked non-ignored files. `el_bench` HEAD 31c0c36, 0 tracked changes (before and after my runs).
- E: first-parent history on 31c0c36 = e8ccc6f (x1 b725f17), d495a89 (x2 0f509e9), daa44f2 (x3 69a60f5), fcc2bc6, c57508e. The three builder heads are ancestors. x3 files equal 69a60f5. fcc2bc6..c57508e touches only `bench/q/bench_setup.sh` and `bench_chain.sh`, so the checks run at fcc2bc6 hold for the python tree of c57508e.
- E, integrator's log (`bench_w2_io/check/run.log`): flag-off identity SUP, SUPPF, SKR01, A8, PFV11, HV11 all `IDENTICAL (5 steps, all fields except code / sec)`; baseline card rendered config equal at 31c0c36 and bench_w2 for 10 of 10 W1-G jobs; 10 of 10 W1-G `config_used.yaml` pass cfgcheck at bench_w2; pytest 446 passed, 4 skipped.
- E, my own re-run (tmux bench_rv_w2a, CPU, nice 19, 4 threads per lane; `bench_review_w2a/run.log`): my own `git archive` of 31c0c36 against bench_wt_w2, card house_r34_unetpp_pf_v11 on cv5v2_v11_f0, seed 5, identity_cpu.py 962379a6, compare_id.py 3b83b364: **PFV11 IDENTICAL (5 steps, all fields except code / sec)**. Rendered opts of the baseline card equal at both commits. Full pytest of bench_wt_w2: **446 passed, 4 skipped**, tree still clean after.

## 2. Cards and feature code: PASS for all 7 cards
E: 14 cards validate. `bench.cards diff` against house_r34_unetpp_pf_v11 (a4a46a52) gives exactly the keys of the request's table. I also rendered the full train command of each arm for fold 0 seed 5 and compared it token by token with the command W1-G really ran (`bq/w1g/jobs_rendered.txt`): the only differing tokens are the keys below and run_name.

| Card (md5) | Differing keys (E) | Code read (E unless S) |
|---|---|---|
| rcs_pf_v11 (d02f82ad) | data.rcs.enable, temperature 0.01, classes R13, min_px 20 | `src/data/rcs.py` = spec. Tables from the root's train list only, with a raise if a labelled stem is in val or test. Ignore px skipped. Sampler yields the same item seeds as SeededSampler; batch size and step count untouched. Loss weights untouched (class counts as before). Critic: per-fold pre-check passed at T 0.01 (x1 log); card states that pairing is broken. |
| ema_wise_posthoc_pf_v11 (29d8f5b4) | weight_avg.ema_999, ema_9998, bn_recal | `weight_avg.py`: averagers read `model.state_dict()` after the optimizer and scheduler step, draw no random number, never write to the model. BN recal runs after the last step on a deep copy, on `splits/train.txt` only (raises on any val / test overlap), images only, eval transform, own generator. Primary ema_9998_bn against raw_bn as the critic asked. Raw-weight identity with PF: IDENTICAL over 5 CPU steps (integrator's smoke check). |
| swad_const_pf_v11 (46fb5b02) | lr_scheduler constant, weight_avg.swad 10000 to 20000, ema_9998, bn_recal, enc_probe_every 2000 | `constant` is an existing schedule (warmup kept, PF freeze / ramp kept). Window = 10,001 iterates as the spec. Critic's fix present: encoder probe every 2k, raw constant-lr weights in the dump list. |
| encoder_spd_pf_v11 (12ce9990) | optimizer adam_spd, encoder_pf.lr_mult 1.0, spd.lambda 1.0, spd.groups, enc_probe_every | `adam_spd.py` = spec Alg. 2. Same two param groups as PF (decoder group house lr and wd, encoder group wd 0). Anchors = encoder params at optimizer build (model is on the device before the optimizer is built), no outside weights. Gradient clip unchanged. |
| encoder_spd_ctrl_pf_v11 (ead7aeb1) | as spd with lambda 0.0 | Critic's X8 control (lr_mult 1.0, wd 0, lambda 0). Fold 0, seed 5 only. lambda 0 takes the plain `Adam.step` path. |
| soft_band_jml (87528ef3) | loss.supervised soft_ce_jml + jml keys + soft_target crack_band | `soft_ce_jml.py`, `aux_targets.py` = spec. CE stays unweighted and averaged over valid px as in the house loss; Dice{14,11} is replaced by JML1{14,11}, weight 1, smooth 1 (the declared change). Band built from the augmented training mask in the worker; no random draw; image and mask unchanged. Held-out masks never pass through the hook. Critic's fixes: jml_hard in the same queue; P1 with identical cells excluded (x2 log); the "cannot widen" claim removed from the card. |
| jml_hard (0d78bea7) | loss.supervised soft_ce_jml, soft_target null | Same loss class, no aux key, house call path. |

Looked for and not found: a changed loss weighting beyond the declared loss swap; a sampler or BN pass that reads held-out cells; held-out labels in any table or target; a changed step count (20,000 in every card), batch size (8) or augmentation (labelsafe); weights or data from outside the fold.

S, not blocking:
- No arm has run a step on the GPU. I read the device handling of each feature (averagers, BN recal hook, AdamSPD anchors, aux tensors, CPU band in the val path) and found no CPU / GPU mismatch, but this is reading, not a run.
- `SoftCEJMLLoss` has `last_terms`, so the trainer's thin-term window logs its terms each step (3 small syncs per step). Harmless.

## 3. Jobs: PASS
- E: `bq/w2a/jobs.txt` md5 d8be4f16 (61 lines), `dump/jobs.txt` md5 0bcef536 (161 lines) = the pins in `launch_w2a.sh` (md5 3900e54f, DEPLOY c57508e, REPO bench_wt_w2, MAXH 120).
- E, own script `bench_review_w2a/rv_jobs.py`: RV_JOBS PASS. Names `w2a_<arm>_f<k>_s<s>`; card, seed and root agree with the name on every line; roots are only `/home/noob/work/bench_data/roots/cv5v2_v11_f{0..4}`; gate 11000 and no extra args on every line; 10 runs per arm, 1 for spdctrl; every seed-5 line before any seed-6 line; 0 duplicate names.
- E: dumps: 161 unique run ids; each line's set is the root's own fold `cv5v2_f<k>`; weights keys = the card's readouts exactly (6 for ema and swad, 1 otherwise); cuda fp32, no `--logp`, no `--opening`, no sealed set; first 63 lines = primary keys (model 36, ema_9998_bn 10, raw_bn 10, swad_bn 7).
- E: no `experiments/<name>` or `.stdout` of any job exists in bench_wt_w2 or el_bench; `/home/noob/work/bench_dumps/w2a` does not exist (new folder). The integrator's `w2a_jobcheck.sh` (c3b00c93) run by me: JOBCHECK PASS.
- E: ROOTS.md5 check OK (81e7e6c1); masks_v11 MANIFEST.md5 check OK (9c0e0687); R34 weights md5 f57b4305 = cards.
- E: disk 193 GB free; the request needs about 59 GB.

## 4. Safety: PASS with the waiter; FAIL if armed directly now
- E: bench_q.sh 226807e0, bench_lib.sh 1af2ed69, bench_gate.sh 51bcf13c, bench_guard.sh b09b53c0, bench_gpumem.sh a939464d = the 31c0c36 blobs (the scripts W1-G ran). bench_setup.sh and bench_chain.sh differ from 31c0c36 only by passing MAXH. Shared gate dir `/home/noob/work/gpu_gate`, no gate HOLD. Different queue dir and worktree from W1-G / W1-G2.
- E: pattern-kill grep over bench, scripts, src and both queue dirs: 0. The only signals are `stop_verified` on a recorded, re-verified PID. finllm 6206 alive, protected by default.
- **Finding (E from the code, S on timing).** `prestart` lets a queue start whenever no outside GPU process holds more than 1,024 MiB. W1-G2 (armed by the lead at 00:00, 10 runs then 10 dumps) leaves the GPU empty between its last training run and its first dump, and for 25 to 60 s between dumps (W1-G dumps took 59 to 95 s, starts are 120 s apart). An armed w2a polls every 10 to 60 s and would take one of those moments. From then on W1-G2's dump queue waits behind w2a's lanes (about 50 h), and its logger stops after 24 h, which sets HOLD. Those 10 dumps are the seeds 7, 8 side of the A/A margin that every wave 2a read needs. The request's line "safe to arm while W1-G runs" does not cover this gap.
- Fix used: the lead's own pattern (`bq/w1g2/wait_then_launch.sh`). `bq/w2a/wait_then_launch.sh` waits for `chain done` (or `dumps not started`) in `bq/w1g2/chain.log`, sleeps 150 s, re-checks the launch script md5, then runs `launch_w2a.sh` unchanged. Stop: `touch /home/noob/work/bq/w2a/NOSTART`.
- **Second finding (E).** The SKR2C opening (tmux s2c_open, started 00:22) waits at the shared gate for 9,900 MiB free. With 3 lanes of about 6.8 GB the GPU has 4.7 GB free: 0 `s2c post` gate passes since 00:22. Three w2a lanes would hold it back the same way for about 50 h. With 2 lanes 11.6 GB are free (gate log 00:05), so its passes run beside w2a.

## 5. What I changed before arming, and why
1. **MAXC 3 -> 2** in `bq/w2a/MAXC` (not md5-pinned; read at every start; the request gives the reviewer this switch). Reasons: (a) no arm has a measured GPU peak, because the smoke of request item 8 was not run; (b) the SKR2C opening needs 9,900 MiB free. Cost (E, request section 5): W1-G with 3 lanes took 0.82 h of wall time per run, one run alone 0.87 h, so the third lane adds almost nothing. To go back: `echo 3 > /home/noob/work/bq/w2a/MAXC`.
2. **Waiter instead of a direct launch** (section 4).
3. Smoke not run. What covers it (S): every job passes the live config and startup-line check; the gate needs 11,000 MiB free per start; the guard stops our newest run under 2,048 MiB free; an arm that crashes on the GPU fails by itself (rc != 0) and the other arms go on; all seed-5 runs come first, so a broken arm shows in the first day. Peaks come from `bq/w2a/gpumem.log` (first job of each arm).

## 6. Launch: NOT DONE (refused by the permission system)
- 01:06:39 E: `bq/w2a/MAXC` set to 2; `bq/w2a/wait_then_launch.sh` (md5 b3d6d69e) placed. Job md5s and `launch_w2a.sh` md5 unchanged.
- 01:07 E: my command to start the waiter (`tmux new-session -d -s bench_wait_w2a ...`) was refused by the session's permission classifier before it ran. I tried no other route.
- State after (E, 01:07:04): no tmux bench_wait_w2a, no bench_q_w2a; `bq/w2a` holds only jobs.txt, dump/, launch_w2a.sh, MAXC (2), wait_then_launch.sh; GPU = finllm + the 3 W1-G2 runs; el_bench 31c0c36 clean; bench_wt_w2 c57508e clean; my CPU session bench_rv_w2a ended by itself. **Nothing of w2a is armed or waiting.**
- To launch (the user or the lead, on gaint), one of:
  1. Now, unattended start after W1-G2: `tmux new-session -d -s bench_wait_w2a -n wait "bash /home/noob/work/bq/w2a/wait_then_launch.sh"`, then `cat /home/noob/work/bq/w2a/wait.log` (one `wait start` line). It arms w2a 150 s after `chain done` appears in `bq/w1g2/chain.log` (S: about 09:00).
  2. By hand, only after `grep -c "chain done" /home/noob/work/bq/w1g2/chain.log` prints 1: `bash /home/noob/work/bq/w2a/launch_w2a.sh`.
- After arming: first-job check as request section 6 item 3 (`config OK (= card)`, startup line with `Labelled: 425`, the `RCS: T 0.01` line), and `MAXH=120` in the environ of the logger and guard (request section 7 item 7).

## 7. For the lead
- Do not arm `launch_w2a.sh` by hand before the W1-G2 chain has ended. If the waiter's launch is refused at about 09:00, the reason is in `bq/w2a/wait.log`.
- bench_wt_w2 must stay at c57508e with no tracked change until the queue ends (checked before every start). New work goes into a new worktree.
- Before any read: the request's section 8 list (ema raw-weight hash against W1-G, swad fold-0 pre-screen script, PF encoder-deviation pass for the spd gate) is still not built.
- Decide: MAXC back to 3 once the SKR2C opening has finished and the first peaks are in.
