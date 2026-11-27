Verdict (21 Nov 2026, 07:46 IST): **PASS** for LAUNCH_REQUEST_fin2.md at md5 **c8f1df79345a56168b0c19ca18a5d2cc** with F2 = 9967d59abaab03cef83c1e3014840b2359ef45d7 (tree adcdf7ec)

# Review of the fin2 package (resume of the 10 full-pool runs under F2), round 1

Reviewer: final_reviewer (resumed; I reviewed fin as REVIEW_FINAL.md). Review 07:35 to 07:46 IST, 21 Nov 2026 (times from `date`).
E = shown by my own command, S = judgement. Limits kept: CPU only, nice 19, at most 8 threads in total; nothing on a GPU; cv02 read only
(ls of two fin run dirs, grep of one config_used.yaml for paths, counts of 'trained' / 'dumped' lines in fin's launch.log, df; the
fin queue dir and experiments dirs not touched); no deploy, no queue placed or armed; no file of the builder, of H2 or of any worktree
changed (bench_wt_fin2 and bench_wt_fin: 0 tracked changes, E); no training .stdout or train.log read or printed (the smoke's own
summary lines only). My clones, scratch and logs: /home/noob/work/bench_int_io/review_fin2/. **Disclosure:** gaint / had 21 GB free
(the fin relay guard stops the fin relay below 15 GB), so the smoke's scratch (its trees, roots and checkpoints, about 6 GB) went to a
new dir of mine on the NAS, /mnt/nas/noob_el_archive/review_fin2_scratch_0736 (5.3 GB at the end), removed at the end (E). PID 5104 untouched.

**Short form.** The fix is the smallest one that works and touches nothing else: F -> F2 is exactly 6 paths; the only behaviour
changes are (i) val / test datasets accept the ignore value 255 **only when every val and test cell is a training cell** (the
pool root's in-sample monitor) and (ii) the final BN re-estimate's overlap guard allows that same in-sample case; every held-out root
(cv5v2, cv5v3, legacy) builds exactly as before. Rerun by me: pytest at F2 **831 passed, 5 skipped, 0 failed**; final2_codeproof.sh
**0 FAIL**, my two tampered commits **2 FAIL** and **5 FAIL**; final2_smoke.sh R1 under F fails for both cards with the production error, R2 and R3 under F2 rc 0, **R3 (crash at step 8, resume from step 4) = R2 (uninterrupted) bit-equal**, R4 F = F2 at step 4, R5 held-out root F = F2; 8 comparisons, 0 not-allowed differences. The resume is exact by the code
(every state the step loop reads is in latest.pth and restored; the batch stream is a pure function of (seed, stream, batch index);
the PF encoder multiplier is a stateless function of the step) and bit-exact in the CPU smoke. The queue's `--resume` kind refuses
what it should, non-resume lines render byte-equal to F's cq.sh, `resumecopy` only reads FB, and `arm` refuses now because fin can
still start training (E: `CAN_START fin`). No blocking item for fin2 itself. Two things must be settled **before the opening**, not
before fin2: the FINAL_RULE disclosure (N1) and the opening's pointers to F's FB / fin's queue log / fin's relay, plus a **disk-guard
name collision** (both packages use `diskguard6`, N2). Smaller notes N3 to N8.

## Files reviewed (md5 on disk at 07:35 and again at the end; unchanged)
| File (H2 = T/harness/final2) | md5 | | File | md5 |
|---|---|---|---|---|
| LAUNCH_REQUEST_fin2.md | c8f1df79345a56168b0c19ca18a5d2cc | | final2_codeproof.sh | 66d5c9d0 |
| final2_queue.sh | bc232ccb | | final2_smoke.sh | 3a383bf1 |
| final2_make_jobs.py / jobs/jobs_fin2.txt | f0f86810 / 7efbf54c | | ckcmp.py | 24392110 |
| final2_rendercmp.py | 7a0bc2bc | | final2_patch_bnrecal.py | 8e663bb2 (record only, not used) |
| final2_relay.sh | f01da9c5 (= final_relay.sh with F2B, fin2, N 10; E diff) | | diskguard6.sh | 8137e124 (= diskguard5.sh with fin2; E diff) |
| evidence/MD5_evidence.txt | 0128655f (`md5sum -c` OK, 10 files) | | F2 (bench_wt_fin2, clean) | 9967d59, tree adcdf7ec |
FINAL_RULE.md 82867156 and F 821dfad unchanged (E).

## Blocking findings
None for fin2.

## Notes (must be done before the opening; not before fin2)

**N1. FINAL_RULE.md needs a dated disclosure addendum (no rule decision changes).** (S, E text) Today it says the full-pool models are
"trained on cv02 (one GPU model, fp32)" (l.38) and live "All under /tmp/noob_el/bench_821dfad/experiments/ (deploy of F)" (l.123).
After fin2 the record must say, before the E1 opening is frozen and before any number of a full-pool run is read (none is): (1) the
incident (all 10 runs stopped at the step-20000 in-sample validation; latest.pth = step 18000); (2) steps 1 to 18,000 ran under F,
steps 18,001 to 20,000, the final validation, the SWAD / EMA finalize with BN re-estimate, the step-20000 save and the post-fit test eval
under F2, resumed from the step-18000 latest.pth, possibly on another A6000 of cv02; (3) F -> F2 changes no training-step code (the
eval / monitor path and the BN re-estimate guard only); (4) the resume restores the full state (CPU proof bit-exact), but on the GPU
cuDNN-deterministic mode leaves atomics in some kernels, so the resumed segment differs from a hypothetical uninterrupted run by the same
last-bit noise any two runs of one seed show; (5) the C2 / C3 readout `swad` (uniform average, no BN re-estimate) does not pass through
the changed BN guard; swad_bn / raw_bn / ema_9998_bn do; (6) enc_probe.jsonl and train.log of each run hold the crashed segment's rows
after step 18,000 and the resumed ones (readers keep the last row per step; train.log is never read); (7) the checkpoints are in F2B =
/tmp/noob_el/bench_9967d59/experiments/, LATEST.md5 relayed by fin2; FB keeps the step-18000 originals until step 12 of the request.

**N2. Name collision: `diskguard6` is used by both fin2 and the opening.** (E) H2/diskguard6.sh 8137e124 (fin2) and
harness/final/opening/diskguard6.sh 8eb052e1 (queue open) both install /tmp/noob_el/bench_q/diskguard6.sh, tmux bench_diskguard6,
stop file DISKGUARD6_STOP and log diskguard6.log. fin2 places its guard first; then opening_queue.sh `guard` refuses ("tmux
bench_diskguard6 already runs" or "exists with another md5") and its `arm` refuses without its own guard; if fin2's guard is stopped by
DISKGUARD6_STOP, the stop file stays and a later diskguard6 exits at its first pass. Safe (refusals) but the opening cannot arm until
one side is renamed. Smallest: the opening renames to diskguard7 (diskguard7.sh, bench_diskguard7, DISKGUARD7_STOP, diskguard7.log,
GUARD6_MD5 pin and guard / arm strings in opening_queue.sh); fin2 unchanged.

**N3. What the opening package must change (listed, not changed; opening_builder's next round).** (E grep of harness/final/opening)
- opening_make_jobs.py l.14 and opening_rendercmp.py l.19: `EXP = /tmp/noob_el/bench_821dfad/experiments` -> F2B
  `/tmp/noob_el/bench_9967d59/experiments` (the `--dumpof` source of every C1 / C2 sealed dump line). Left as is, a dump would read FB's
  step-18000 latest.pth and stop on bench_infer's `step == total_steps` assertion (safe, but nothing is dumped).
- opening_queue.sh l.39-41 and fin_check (l.86-94): the run checks read `$FB/experiments/<run>/checkpoints/latest.pth`, compare with the
  LATEST.md5 relayed to RF = bench_relay/fin and grep `trained <run> rc=0` in QF = bench_q/fin/launch.log. After fin2: F2B's run dirs,
  RF = bench_relay/fin2 (or its NAS dir, N5) and fin2's launch.log. FB stays the code reference of gb_check (G is built on F; G's
  CODE.md5 against FB's is still the right comparison while the deploy dir bench_821dfad exists).
- run_opening_read.sh l.12 / l.118: `train_code_revision` expected = F; dumps of F2B runs will carry F2B's REVISION
  (9967d59abaab03cef83c1e3014840b2359ef45d7), because bench_infer takes REVISION from the run's deploy dir. RF default (l.50) ->
  bench_relay/fin2. `checkpoint_md5 = the relayed LATEST.md5` then reads fin2's relay (right).
- OPENING_RULE.md l.29 (checkpoint location, F), l.155 (train_code_revision = F), l.161 and OPENING_REQUEST.md l.91 ("fin's 10 trainings end
  with trained fin_* rc=0"): fin2's, with the N1 disclosure; opening_register.sh l.59 / l.123-125 record F and should record F2 as well.
- The test fixtures that build a fake bench_821dfad (opening_render_smoke.sh l.30-31, opening_chain_smoke.sh l.57-59) follow the path.
- The order: the opening may start only after fin2's `BENCH CV02 Q ALL DONE` and the fin2 relay (RELAY ALL DONE, 10 of 10).

**N4. The step-18000 checkpoints of PF s8 / s9 do not exist yet.** (E) fin's launch.log at 02:11 UTC: 8 `trained fin_` lines, 60 dumps
rc 0, no `all jobs dispatched`; PF s8 / s9 start after the last dump-only job. They must reach step 18000 like the others (the request's
plan); `resumecopy` refuses unless all 10 have `trained <name> rc=` and `.end` in fin and every source latest.pth is step 18000 (torch on
cv02), so a run that dies earlier is refused, not resumed (S: then it needs a fresh run, the request's fallback).

**N5. gaint disk for the fin2 relay.** (E) gaint / had **21 GB free** (07:36 and 07:43); final2_relay.sh refuses below FLOOR 25 GB on
the relay filesystem, so step 10 refuses unless gaint is freed or `RD=/mnt/nas/noob_el_archive/bench_relay/fin2` is used (the script
allows it; NAS 8.3 TB free). If the NAS dir is used, the opening's RF (N3) must point there. fin's own relay guard stops fin's relay below
15 GB on gaint (keep that margin while fin's last dumps relay).

**N6. Evidence of the queue DRY run is from the 9330f8b version of final2_queue.sh.** (E) evidence/queue2_dry/queue2_dry.out shows
"F2 must be the full commit 9330f8bd..."; the script now pins 9967d59. My own DRY / refusal run of bc232ccb (logs/queue2_dry_mine.out):
build OK (10 lines, 7efbf54c), second build refused, wrong F2 refused, resumecopy / render refused while F2B is not deployed, arm refused
without a passed render, and **with a faked render pass arm refused: `CAN_START fin` / "another queue can still start training"**; place
DRY prints LPG 1, MAXC 8, SHARE_TRAIN 20480, no SHARE_DUMP; status read only (cv02 74 GB free, fin2 no dir).

**N7. The resumed runs' logs carry two segments.** (S) train.log (appended) and enc_probe.jsonl of each run hold the crashed segment's
rows after step 18,000 and the resumed ones; enc_probe readers keep the last row per step (src/trainers/enc_probe.py l.8-9); train.log and
the in-sample val / test numbers are never read. The resumed probe compares with the same W0 (the pretrained encoder, rebuilt before
load_training_state).

**N8. Not covered by any run: the GPU segment itself.** (S) The CPU smoke proves the state restore and the data position bit-exact;
on cv02 the resumed 2,000 steps can differ in the last bits from an uninterrupted run (cuDNN deterministic, `use_deterministic_algorithms`
off: src/utils/seed.py l.10-20, configs/base.yaml l.32 `deterministic: true`), as two uninterrupted runs of one seed already do. That is the
lead's disclosed caveat; I agree the resume is preferable to a fresh 18 GPU-h rerun, which is not bitwise reproducible either.

## What I verified (E unless marked)

1. Diff F -> F2 (my own clone of the repository at 9967d59; bench_wt_fin2 clean at 9967d59, tree adcdf7ec)
- `git diff --name-status 821dfad 9967d59`: M cq.sh, M cq_setup.sh, M scripts/train.py, M src/trainers/weight_avg.py, A
  tests/test_bench_cq_resume.py, A tests/test_bench_pool_eval.py: **6 paths**, 306 insertions, 7 deletions.
- train.py: only build_benchmark_data's eval block: `ev_ign = d_cfg.get("mask_ignore_value") if (set(val_stems) | set(test_stems)) <=
  train_stems else None`, a refusal of any value other than 255, and `ignore_value=ev_ign` on the val and test datasets. val_stems,
  test_stems and train_stems are the root's lists (l.396-397). Both cards set `data.mask_ignore_value=255` (card opts, E), so on
  pool532_v11 ev_ign = 255 and on every held-out root ev_ign = None (the F objects). weight_avg.py: `if set(stems) & held:` ->
  `if set(stems) & held and not held <= set(stems):` (+ 2 comment lines); the loader that follows (train.txt, transform, batch,
  generator) is unchanged.
- final2_queue.sh PINS: all 15 equal `git show 9967d59:<path> | md5sum`; slim_ckpt.py, cvcard.py, cq_gpumem.sh, bench_lib.sh,
  bench_infer.py, bench_make_pool_root.py, cq_rescue.sh are byte-equal F vs F2.
2. Reruns
- pytest at F2 (fresh clone, data/labeled link as in the worktrees, CPU, OMP 2): **831 passed, 5 skipped, 0 failed** in 217 s
  (logs/pytest_F2.log; the 5 skips as at F).
- final2_codeproof.sh 66d5c9d0 (REPO_TEST = my clone, the script's own variable, so nothing runs in bench_wt_fin2): **9 OK, 0 FAIL**
  (paths; nothing under configs/ data/ bench/methods* bench/*.py bench_infer.py tta.py; weight_avg.py the guard only; train.py the eval
  block only, l.522 to l.560; deploy CODE.md5 against F only the 6 paths, **F2 CODE.md5 md5 751e365e217150e7efaa24d56928ab3f, 782 lines**;
  queue and eval tests 50 passed, 2 skipped in the archive; non-resume render byte-equal to F's cq.sh 1 passed); item 5 with my smoke
  log: `OK (5) ... every comparison 0 not-allowed differences`, total 10 OK, 0 FAIL.
- My negatives (not the builder's): neg1 = labelled BatchStream stream_id 0 -> 2 in train.py (a training-path line): **2 FAIL** (both
  train.py items); neg2 = the BN-recal guard replaced by `if False:` plus one comment line in src/losses/ce_dice.py: **5 FAIL** (paths,
  src, 2b, CODE.md5, and the eval test that a partial overlap still raises).
- final2_smoke.sh 3a383bf1 (all 5 items, both cards, CPU, nice 19, OMP 6; scratch on the NAS, see the header): 
  | Run | Candidate card | PF card |
  |---|---|---|
  | R1 F, uninterrupted 8 steps | rc 1 in 15 s, `ARTS_00048_r2_c5.png: mask values must be in 0..23, found [0, 2, 4, 13, ...]` (the production error); latest.pth step 4 (ema_9998, model, swad; averager n 4 / 3) | rc 1 in 10 s, the same error |
  | R2 F2, uninterrupted | rc 0 in 159 s: latest.pth step 8 with model, ema_9998, swad, raw_bn, ema_9998_bn, swad_bn (averager n 8 / 7); metrics.json with test_final | rc 0 in 27 s |
  | R3 R1's dir resumed under F2 | rc 0 in 149 s; vs R2: latest.pth 4 differing paths, all allowed (trainer/resumes, train_time, 2 x steps_per_sec), models 12,360 / optimizers 3,093 / best_payload 2,060 tensors and rng equal; metrics.json 5 allowed paths (resumes, timing) | rc 0 in 24 s; the same: 4 / 5 allowed, 0 not allowed |
  | R4 F2 exit at step 4 vs R1's step-4 state | rc 3; 2 allowed (timing), models 6,180 / optimizers 3,093 / rng equal: the training path F = F2 | rc 3; 2 allowed |
  | R5 held-out cv5v3_v11_f0, PF, 4 steps, F and F2 | | both rc 0 (23 / 21 s); latest.pth 2 allowed (timing; models 350, optimizers 528, best_payload 350 equal), metrics.json 3 allowed: nothing changes on held-out roots |
- My own independent comparison of R2 and R3 (candidate latest.pth, my flatten-and-md5 script, not ckcmp.py): 20,465 / 20,467 leaves,
  17,516 tensors; differing leaves only trainer/resumes (the resume record), train_curve steps_per_sec and train_time.
3. Resume exactness by the code
- latest.pth (trainer._training_state, l.721-750): models (incl. the averagers' running copies via wavg.save_into and the *_bn readouts),
  optimizers, schedulers (LambdaLR last_epoch), scaler, rng (python, numpy, torch CPU, CUDA), trainer history / curve / best / timing /
  resumes, best_payload, consistency and pl_window (unused here), weight_avg meta (n per averager).
- load_training_state (l.756-801): refuses any config difference (_config_diff), restores the averagers first, then every model /
  optimizer / scheduler with a key-set check, scaler, trainer state, best.pth as of the step, and **sets the RNG last**; fit() restarts
  every stream with `iterate(start)`. BatchStream (src/data/stream.py): epoch order from (seed, stream, epoch), each sample's augmentation
  seed from (seed, stream, batch index, position), own DataLoader generator: a pure function of the step, independent of workers and of
  the global RNG (tests/test_stream.py covers a resume across an epoch boundary and worker counts; tests/test_weight_avg.py a resume of
  the averagers; both in the 831).
- PF encoder lr: build_pf_lr_lambda is a stateless function of the step (0 below freeze 1000, ramp to 1 by 2000), inside LambdaLR, whose
  last_epoch is restored; at 18,000 it is the steady value. The candidate's constant schedule likewise. SWAD window 10,000 to 20,000 and
  EMA: running copies and n in latest.pth (smoke: averager n 8 / 7 after resume equal to uninterrupted).
- The step-20000 order is unchanged by F2: validation (eval mode, own loader generator: no global RNG draw, no state change), then
  wavg.finalize (BN re-estimate), then save_latest, then the post-fit test eval (trainer.py l.863-910).
- train.py --resume (l.248-273, l.363): resumes experiments/<run_name> under the cwd (= F2B), refuses a missing latest.pth, does not
  rewrite config_used.yaml, appends to train.log. The fin run config holds no FB path (E: grep of fin_hrnet_swad_v11_pool_s5's
  config_used.yaml on cv02: run_name and `root: /tmp/noob_el/bench_data_fin/roots/pool532_v11` only), so the copies resume in F2B.
4. Queue
- cq.sh resume kind (diff read): a `--resume` line needs B/experiments/<name>/config_used.yaml and checkpoints/latest.pth, no
  experiments/<name>.stdout, a cfgcheck of that config against card, seed, name and root, and is refused for smoke_* / dumptest_* names;
  it renders `train.py --resume --config ... --opts <card opts>`; the 10th field is allowed; the main loop skips it if its .stdout exists
  (starts once). cq_setup.sh: a resume line needs latest.pth and no .stdout; other lines unchanged. tests/test_bench_cq_resume.py (14, in
  the 831) covers each refusal, the mix with fresh pool lines and the byte-equal render of non-resume lines against `git show 821dfad:`.
- Step 18000 and the md5: not in cq.sh but in final2_queue.sh: `resumecopy` reads every source latest.pth's step with torch on cv02
  (refuses unless all 10 are 18000), records name / step / md5 in IO/resumecopy.tsv, copies with `cd FB/experiments && test ! -e
  F2B/experiments/<n> && cp -a <n> F2B/experiments/<n>` (FB is only read; .stdout is outside the run dir and not copied); `copy_check`
  (at resumecopy, render and arm) requires the md5 recorded, config_used.yaml present and no .stdout for all 10.
- Arm: qscan refuses while any live queue can start training (E now: CAN_START fin); `share 20480/` with no SHARE_DUMP file; MAXC 8,
  LPG 1, GAPSEC >= 30, guard 6 with its md5, no HOLD, free >= 26 GB; F2B check (REVISION, CODE.md5, 15 pins, diff to bench_821dfad = the 6
  paths); root pins. The lanes are fin's (a1) rule with no dump line at all, so one process of ours per GPU.
- Job list: final2_make_jobs.py regenerated byte-equal (7efbf54c); its 10 lines = fin's 10 full-pool lines with `--resume` in field 9
  (diff E), the candidate lines keep `swad` in field 10.
5. Disk and relay
- cv02: 74 GB free (E, 02:11 UTC); fin2 needs about +4.5 GB on top of the 3.6 GB copies (S, E sizes: candidate step-18000 latest.pth
  419,551,139 B on cv02); arm's need 26 GB holds. FB originals 3.6 GB until step 12.
- Relay: the unchanged relay_w1c.sh with B = F2B, N 10; each unit = RUN.md5 + config_used.yaml + slim.pth + LATEST.md5 (+ enc_probe.jsonl),
  as fin's full-pool units would have been. fin's own relay ends by its "cv02 queue ended" rule with 75 of 85 (the 10 full-pool runs write
  no RUN.md5 in fin); run_read_final.sh needs only the 75 D4 dumps (unaffected). gaint: N5.

## Not verified
- Anything on a GPU; the cv02 steps (deploy, resumecopy, render, place, guard, arm) for real. The render of the 10 resume lines is
  covered by the sandbox tests; the lead's step 7 renders them on cv02 with final2_rendercmp.py.
- final2_rendercmp.py was read, not run (no render output exists yet).

## Verdict
**PASS** for fin2 as pinned (request c8f1df79, F2 9967d59 / tree adcdf7ec, final2_queue.sh bc232ccb, jobs 7efbf54c, codeproof 66d5c9d0,
smoke 3a383bf1). Resume (not a fresh rerun) is exact by the code and bit-exact on CPU, so the lead's condition for the resume holds; the GPU
last-bit caveat goes into the record (N1, N8). Launch conditions already enforced by the tools: arm only after fin can no longer start
training (qscan) and after all 10 fin trainings have ended with a step-18000 latest.pth (resumecopy). Before step 10 decide the relay dir
(N5). Before the opening: the FINAL_RULE addendum (N1), the opening's pointers (N3) and the guard rename (N2).

