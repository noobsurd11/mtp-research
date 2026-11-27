# Launch request fin2: resume the 10 full-pool runs of fin under F2 (incident of 21 Nov 2026; final_builder2)

Status: built and tested on gaint CPU. **Nothing launched, no GPU used (gaint's GPU holds root's finllm, PID 5104: not
used), nothing written on cv02, no deploy made, nothing pushed; commit F2 made locally only.** F (821dfad), the fin queue
dir, the experiments dirs and every latest.pth were not touched (cv02 only read). E = measured by a command of this build,
S = judgement. Notation: T = /home/yugma/mtp/research/team_2026-11-12_frontier, H2 = T/harness/final2, F = 821dfad (deploy
FB = cv02 /tmp/noob_el/bench_821dfad), F2 = 9967d59abaab03cef83c1e3014840b2359ef45d7 (tree adcdf7ec; two commits on F: 9330f8b and 9967d59; worktree
/home/noob/work/bench_wt_fin2, branch bench_fin2), F2B = cv02 /tmp/noob_el/bench_9967d59 (its deploy, step 2),
Q2 = cv02 /tmp/noob_el/bench_q/fin2, IO2 = gaint /home/noob/work/bench_fin2_io.

## 0. What runs
One cv02 queue `fin2`, 10 lines (H2/jobs/jobs_fin2.txt, md5 7efbf54c): the 10 full-pool lines of fin with the 9th field
`--resume` (same card, seed, root, gates, slim keys). Each continues F2B/experiments/<run> (a copy of the run dir from FB,
step-18000 latest.pth) with `train.py --resume`: steps 18,001 to 20,000, then the final validation (the in-sample monitor,
now accepted), SWAD / EMA finalize with BN re-estimate, latest.pth at step 20000 with all readouts, the post-fit test eval,
slim.pth (swad_bn + swad for the candidate; model for PF), RUN.md5. No dump, no sealed set. Lane rules as ruled for fin:
MAXC 8, LPG 1, SHARE_TRAIN 20480, no SHARE_DUMP file (fin2 has no dump line), GAPSEC 30. GPU about 3 GPU-h; wall about
40 min after arming (section 6).

## 1. Root cause (E)
- fin_pf_v11_pool_s5/s6/s7 and fin_hrnet_swad_v11_pool_s5..s9 ended `trained rc=1` at step 20000 (fin launch.log 00:55 to
  01:48 UTC). Their run dirs hold config_used.yaml, train.log, checkpoints/latest.pth (0.42 GB HRNet, 0.31 GB PF; no best.pth,
  no metrics.json); the HRNet dirs also enc_probe.jsonl (E, ls on cv02).
- scripts/train.py build_benchmark_data (F l.536-537) builds the val and test datasets as `BenchmarkELDataset(img_dir,
  msk_dir, stems, weak_eval)`: no ignore value, by design ("Val/test masks stay strict", l.481). The labelled training
  dataset passes `ignore_value=ign` (255).
- The full-pool root pool532_v11 links ALL 532 stems to the v1.1 TRAIN masks (masks_v11/masks; 15 pool cells hold ignore
  px 255, masks_v11/SUMMARY.txt), and its val = test = the cv5v3 fold-0 held-out list, which holds ARTS_00048_r2_c5
  (404 ignore px). load_index_mask refuses 255 without an ignore value -> ValueError at the first val batch with that cell.
- Why the cv5v3 (c3x, c3_pf_v11) and cv5v2 runs never hit it: their roots link held-out cells to masks_strict (E: cv5v3_v11_f0
  MASKLINKS.tsv: 425 `train` -> masks/, 107 `heldout` -> masks_strict/), which hold no 255. Only the full-pool root has
  training cells as val / test.
- Trainer order at the last step (trainer.py l.863-898): validation BEFORE wavg.finalize and save_latest; val_every 20000
  and checkpoint_every 2000 in the cards, so the step-20000 state and the averagers' finalize were never written; latest.pth =
  step 18000. **The post-fit test eval would fail the same way** (test = the same 107 cells, same dataset construction,
  trainer.py l.909): E in the smoke (section 4).
- **A second stop behind the first** (E, found by the smoke of section 4 with the eval fix alone): at the same step, the
  candidate's wavg.finalize re-estimates BN for the averaged readouts with src/trainers/weight_avg.py train_fold_loader,
  which refuses `training.bn_recal: train.txt overlaps val / test`: on pool532_v11 every val / test cell is a training
  cell. PF has no averagers, so only the 5 candidate runs (and their swad / swad_bn readouts) depend on it.
- Not caught before: the code proof compared dumps and imports; the full-pool smoke (harness/final/final_poolsmoke.sh) stopped
  after step 1 (`--exit_after_step 1`), so no run reached its final validation. The missing smoke is section 4.

## 2. Fix (F2) and why
- **(a') chosen, two parts** (both conditioned on the same in-sample case; F -> F2 = 6 paths):
  (i) scripts/train.py, eval block of build_benchmark_data only (10 lines added, 2 changed): `ev_ign =
  data.mask_ignore_value if every val and test cell is also a training cell else None`; the val and test datasets get
  `ignore_value=ev_ign`; a value other than 255 is refused (the metrics ignore 255 only). SegmentationMetrics excludes the
  ignore label from every count (metrics.py l.223-252: confusion, crack GT, relaxed recall, image-level FPR); the val loss
  (ce_dice, ignore_index 255) is the training criterion, which already sees 255. E: tests/test_bench_pool_eval.py (6):
  in-sample monitor accepts 255; held-out val / test stay strict (a 255 still raises); partial overlap stays strict; a card
  without the ignore value unchanged; ignore value != 255 refused; 255 px enter no count of the evaluator.
  (ii) src/trainers/weight_avg.py train_fold_loader (the final BN re-estimate): the overlap guard allows val / test only
  when ALL of them are training cells; a partial overlap still raises; the loader (train.txt stems, order, transform,
  batch 8, generator) is unchanged and runs only after the last optimizer step. E: +3 tests in test_bench_pool_eval.py
  (in-sample allowed, reads train.txt in order; partial overlap refused; held-out root unchanged): 9 in all.
- Every existing root (cv5v2, cv5v3, legacy) has held-out val / test, so ev_ign is None there and nothing changes (E:
  section 4, R5: F and F2 give bit-equal results on a cv5v3 root).
- **(b) not chosen**: a root or config without val / test needs code changes too (BenchmarkELDataset refuses an empty list;
  the post-fit test eval always runs) and a new data.root changes the run config, which `train.py --resume` refuses
  (trainer._config_diff): the step-18000 checkpoints could not be resumed; all 10 runs would start again (about 2 h wall).
- **Training path unchanged** (E, H2/final2_codeproof.sh 66d5c9d0, 0 FAIL incl. item 5 = the smoke, evidence/codeproof2_full.out): F -> F2 touches 6
  paths (scripts/train.py, src/trainers/weight_avg.py, bench/q/cv02/cq.sh, cq_setup.sh, 2 new tests); nothing under configs/
  data/ bench/methods*/ bench/*.py, bench_infer.py, tta.py; under src/ only the weight_avg.py guard (item 2b: exactly the one
  condition + 2 comment lines); the train.py diff is exactly the two val / test DataLoader lines plus the ev_ign block, all after
  `weak_eval =` inside build_benchmark_data. Negative tests: a tampered training line in train.py: 2 FAIL
  (codeproof2_negative.out, on 9330f8b); an altered BN-recal loader (batch 8 -> 4): 1 FAIL (codeproof2_negative_wavg.out).
  Deploy CODE.md5 against bench_821dfad differs in those 6 paths only (F2 CODE.md5 md5 751e365e, 782 lines). Bit-equal
  training state F vs F2: section 4, R4.
- Queue (F2): cq.sh extra `--resume` on a training line (run dir must exist in B with config_used.yaml and latest.pth; no
  `.stdout` yet: starts once; cfgcheck of its config at arming; the 10th field allowed); cq_setup.sh accepts the existing run
  dir of a resume line. Lines without `--resume` render byte-equal to F's cq.sh (E: tests/test_bench_cq_resume.py, 14 tests).
- Full pytest at F2 (9967d59): **831 passed, 5 skipped, 0 failed** (evidence/pytest_full_9967d59.log; 828 at 9330f8b).

## 3. Resume path and its exactness
Code (E, read):
- latest.pth holds models (model + the averagers' running copies), optimizers, schedulers (LambdaLR last_epoch: the PF
  encoder multiplier is a function of the step, build_pf_lr_lambda), scaler, rng (python, numpy, torch CPU, all CUDA devices),
  trainer history, weight_avg state (save_into / load_from), consistency and pseudo-label windows (unused here).
- load_training_state refuses any config difference, restores all of the above, sets the RNG last; fit() restarts the data
  stream with `labeled_loader.iterate(start)` (BatchStream: order and worker seeds from seed, stream id and batch index; own
  generator), so steps 18,001+ draw exactly the batches the uninterrupted run would have drawn.
- Not in latest.pth: the log-average window (logs only; 18000 is a log_every boundary, so it is empty there), enc_probe rows
  (log only; after a resume the step-20000 row repeats, readers keep the last row per step: enc_probe.py l.8-9), train_time.
- **GPU: bitwise exactness is impossible on cv02, for any run** (E, src/utils/seed.py l.15-41): the cards run with
  `deterministic: True` = cuDNN deterministic, benchmark off, but NOT torch.use_deterministic_algorithms (that is the
  'strict' mode, about 5x slower, tests only); some CUDA kernels (bilinear-upsampling backward) accumulate with atomics, so
  two uninterrupted GPU runs of one seed already differ in the last bits. The resume restores the exact state (model,
  optimizer, scheduler, scaler, CUDA RNG, averagers, data position; CPU proof below: bit-equal), so the resumed steps
  18,001 to 20,000 differ from a hypothetical uninterrupted run only by that same atomics noise; nothing systematic. A fresh
  rerun would not be bitwise reproducible either. (S) Recommendation: resume (section 7, item 3).
Experiment (E, gaint CPU, H2/final2_smoke.sh, evidence/smoke_resume/f2final/smoke.log; tiny settings: 8 steps,
checkpoint every 4, 128 px, batch 2, val_every left at the card's 20000 so the first validation is the last step):
R3 (the incident path: F's run crashed at the step-8 validation with latest.pth at step 4, its dir resumed under F2) against
R2 (F2 uninterrupted): **bit-equal** in every tensor of every models[] key (candidate 12,360 tensors over the six readouts
model, ema_9998, swad, raw_bn, ema_9998_bn, swad_bn; PF 350), best_payload (2,060 / 350), optimizer state (3,093 / 528),
scheduler, scaler, all RNG states, weight_avg state (ema n 8, swad n 7) and cfg; the only differing paths are
trainer/resumes, train_time and steps_per_sec; metrics.json (incl. the post-fit test eval) equal except resumes and timing.

## 4. The missing smoke (H2/final2_smoke.sh)
| Run | Candidate card | PF card |
|---|---|---|
| R1: F, uninterrupted | rc 1 in 9 s at the step-8 validation: `ARTS_00048_r2_c5.png: mask values must be in 0..23, found [0, 2, 4, 13, 14, 15, 255]` (the production error); latest.pth step 4 | the same, rc 1 in 8 s |
| R2: F2, uninterrupted | rc 0 in 125 s: validation, finalize (BN re-estimate on the 532 cells), latest.pth step 8 with the six readouts, post-fit test eval, metrics.json | rc 0 in 18 s |
| R3: R1's dir resumed under F2 | rc 0 in 143 s; bit-equal to R2 (section 3) | rc 0 in 15 s; bit-equal to R2 |
| R4: F2 --exit_after_step 4 against R1's step-4 latest.pth | bit-equal (6,180 model tensors, 3,093 optimizer tensors, RNG); only train_time and steps_per_sec differ: the training path F vs F2 is identical | bit-equal (350 / 528) |
| R5: held-out root cv5v3_v11_f0, 4 steps, F and F2 | | both rc 0; latest.pth and metrics.json bit-equal apart from timing: nothing changes on held-out roots |
With the eval fix alone (F2 part 1, 9330f8b) the candidate's R2 / R3 stopped at the finalize (`training.bn_recal: train.txt overlaps
val / test`; evidence/smoke_resume/patch0): this is how the second stop of section 1 was found; F2 part 2 (9967d59) fixes it.
Smoke script final2_smoke.sh (pins F2 9967d59; PATCH=1 applied the uncommitted candidate patch final2_patch_bnrecal.py to
9330f8b trees, now superseded by the commit; evidence/smoke_resume/patch1). CPU wall: candidate 9 + 125 + 143 + 7 s, PF 8 + 18 +
15 + 4 s, R5 14 + 16 s.

## 5. Launch steps (gaint, by the lead, after the review PASS; T and H2 written out in full)
| # | Command | Stop path |
|---|---|---|
| 1 | Review of this request, commit F2 (`git -C /home/noob/work/bench_wt_fin2 diff 821dfad 9967d59`), the H2 scripts. | |
| 2 | `bash T/harness/c3base/c3_deploy.sh 9967d59abaab03cef83c1e3014840b2359ef45d7` : stage /home/noob/work/bench_c3_io/stage/bench_9967d59 and F2B. Must print `CODE.md5 751e365e217150e7efaa24d56928ab3f (782 lines)` and `CV02_CODE_OK 9967d59...`. May run any time (no conflict with fin). | refuses if a dir exists; an unused deploy is inert |
| 3 | `SCR=<new dir> SMOKE_OUT=H2/evidence/smoke_resume/f2final/smoke.log bash H2/final2_codeproof.sh` (0 FAIL); optionally rerun the smoke: `SCR=<new dir> OUT=<new dir> bash H2/final2_smoke.sh` (gaint CPU, about 6 min) | read only |
| 4 | **Wait for fin to end** (do not HOLD fin; section 7): `grep -c 'BENCH CV02 Q ALL DONE' /tmp/noob_el/bench_q/fin/launch.log` = 1 on cv02, i.e. PF s8 / s9 have run under F and stopped at step 20000 like the others (latest.pth step 18000). | |
| 5 | `IO=/home/noob/work/bench_fin2_io bash H2/final2_queue.sh build` (10 lines, md5 7efbf54c) | gaint only |
| 6 | `DRY=1 F2=9967d59abaab03cef83c1e3014840b2359ef45d7 F2B=/tmp/noob_el/bench_9967d59 bash H2/final2_queue.sh resumecopy`, then without DRY: refuses unless all 10 fin trainings ended (`trained <name> rc=` and pids/<name>.end), every source latest.pth is step 18000 (torch on cv02 CPU) and no target exists; `cp -a` of the 10 run dirs (not their .stdout) FB -> F2B; md5 of latest.pth equal on both sides, recorded in IO2/resumecopy.tsv. The FB originals stay untouched (fallback). | a failed copy leaves new dirs in F2B/experiments only; remove them (`rm -rf` of those 10 paths only) and run again |
| 7 | `F2=... F2B=... bash H2/final2_queue.sh render` (render-only cq.sh of F2B in /tmp/noob_el/bench_fin2_render/<stamp>; `render compare: 0 FAIL`) | nothing starts |
| 8 | `bash H2/final2_queue.sh place` (Q2: jobs.txt read-only, LPG 1, MAXC 8, SHARE_TRAIN 20480, no SHARE_DUMP) ; `bash H2/final2_queue.sh guard` (disk guard 6, tmux bench_diskguard6) | Guard: `touch /tmp/noob_el/bench_q/DISKGUARD6_STOP` |
| 9 | `DRY=1 F2=... F2B=... GAPSEC=30 bash H2/final2_queue.sh arm`, then without DRY. Pre-checks: render passed; qscan (no live queue can start training: fin ended); Q2 placed, unused, `share 20480/` (no SHARE_DUMP); data md5; F2B check (REVISION, CODE.md5, 15 pins, diff to bench_821dfad = the 6 paths); root pins; the 10 copies (latest.pth md5 as recorded, config present, no .stdout); guard 6; no HOLD; free >= 26 GB. Armed only with the `cv02 q armed:` line (SHARE_TRAIN 20480, SHARE_DUMP 0, gap 30 s). Owed at the first start: `fin_hrnet_swad_v11_pool_s5 config OK (= card)`, `startup line OK: Labelled: 532 (...)  unlabelled: 0 (-)  val: 107  test: 107`; in its stdout (grep only): `RESUMED from ... at step 18000/20000`. | `ssh -n -a -o BatchMode=yes cv02@10.8.1.106 'touch /tmp/noob_el/bench_q/fin2/HOLD'`; a running job: compare `ps -o args= -p $(cat Q2/pids/<job>.pid)` with `Q2/pids/<job>.cmdline`, then `kill` that PID only; a refused arm: as in LAUNCH_REQUEST_final.md step 8 with fin2 for fin |
| 10 | `F2B=/tmp/noob_el/bench_9967d59 bash H2/final2_relay.sh` (relay_w1c.sh 74a2ec3d unchanged; N 10; session bench_relay_fin2; RD /home/noob/work/bench_relay/fin2) | `touch /home/noob/work/bench_relay/fin2/STOP` |
| 11 | Ticks: `F2=... F2B=... bash H2/final2_queue.sh status` (shows HOLD, SHARE_DUMP absent, trained rc 0, RUN.md5, RESUMED count). Expected per run in Q2/launch.log: `trained <run> rc=0`, `done <run>: final-step lines 1, Traceback lines 0`, `no dump for <run> (full-pool root: no held-out set)`, `RUN.md5 <run> rc=0`. Never print or tail a .stdout or train.log (in-sample numbers). | as 9 |
| 12 | After all 10 are relayed and checked: the FB originals (`/tmp/noob_el/bench_821dfad/experiments/fin_*_pool_s*`, 3.6 GB) may be removed by the lead; until then they are the fallback. | |

## 6. Disk, GPU-h, wall (S from E timings)
- cv02 (76 GB free at 07:19 IST; guard floor 20 GB): copies 3.6 GB (5 x 0.42 + 5 x 0.31 GB, E sizes), growing in place to
  about 8.1 GB at the end (candidate: latest with six readouts 0.76 + best 0.08 + slim 0.17 GB; PF 0.42 + 0.10 + 0.10 GB, E from
  fin / c3x runs); `arm` needs 26 GB free. FB originals 3.6 GB until step 12. gaint: relay fin2 about 1.4 GB.
- GPU: candidate 2,000 steps = 10% of a 2.6 h run (median, E) = about 16 min + BN re-estimate on 532 cells and the final
  validation and test (about 5 min); PF about 6 + 3 min. 5 x 21 + 5 x 9 min = **about 2.5 GPU-h**.
- Wall: fin ends when PF s8 / s9 (started after fin's last dump-only job, about 07:50 IST) stop at step 20000, about 08:50 IST
  (PF median 1.0 h, E); then steps 5 to 9 (about 15 min); fin2 about 25 min for the 8 first runs, the last two PF about 10 min
  later: **full-pool runs complete about 09:30 to 09:45 IST, relayed about 10 min later.**

## 7. Choices for the lead (recommendation first; built as recommended)
1. **Do not HOLD fin.** HOLD also stops the dump step of dump-only jobs (chain_after waits on HOLD) and PF s8 starts within
   a gap of the last dump-only dispatch, so a manual HOLD between them is a race. Let s8 / s9 run under F: they reach step
   18000 like the others (the same GPU time as a fresh F2 run) and are resumed in fin2 with the 8 others. One fin2 queue,
   armed after fin's ALL DONE line: never two training queues, no race.
   Alternative (not built): a fin2a with the 8 ended runs as soon as fin has dispatched all its jobs, then a fin2b with s8 / s9
   after fin ends; it uses the idle GPUs about 50 min earlier but ends only about 15 min earlier (s8 / s9 set the end) and needs
   a NAMES subset in final2_queue.sh and two arms.
2. Fix (a') over (b): section 2.
3. **Resume rather than a fresh rerun.** Bitwise exactness against an uninterrupted run is impossible on cv02's GPUs for any
   run (section 3: cuDNN-deterministic only, atomics in some kernels), so a fresh rerun buys no exactness; the resume restores
   the exact state (CPU proof bit-equal, section 4) and costs about 2.5 GPU-h and 40 min instead of about 18 GPU-h and 2 to
   4.5 h. Fallback if the lead or the reviewer wants fresh runs: the same fin2 lines without `--resume` (new run names, or a
   deploy without the copies), about 18 GPU-h, 2 to 4.5 h wall (LAUNCH_REQUEST_final.md section 6).

## 8. Tests (E; CPU only, nice 19)
| Test | Result |
|---|---|
| pytest at F2 9967d59 (full) | 831 passed, 5 skipped, 0 failed |
| tests/test_bench_pool_eval.py (eval path and the BN re-estimate guard) | 9 passed |
| tests/test_bench_cq_resume.py (queue resume kind; render of non-resume lines byte-equal to F) | 14 passed |
| final2_codeproof.sh | 0 FAIL (items 1, 2, 2b, 3, 4); tampered training line in train.py: 2 FAIL; altered BN-recal loader: 1 FAIL |
| final2_smoke.sh (F2 9967d59, both cards, R5) | R1 (F) rc 1 with the production error; R2 / R3 rc 0; R3 = R2 bit-equal; R4 = R1 bit-equal; R5 F = F2; 8 comparisons, 0 not-allowed differences |
| final2_make_jobs.py | 10 lines, md5 7efbf54c; asserts the fields equal fin's full-pool lines except the 9th |
| final2_queue.sh DRY / refusals (evidence/queue2_dry/) | build OK; refused: second build, wrong F2, F2B not deployed (resumecopy, render), arm without render; place / guard DRY print their writes; status read only |

## 9. Not tested
- Anything on a GPU (no free GPU on gaint; cv02 only read): the resumed steps on cv02, the GPU-side bit-equality.
- final2_queue.sh resumecopy / render / place / guard / arm for real (F2B does not exist); the render runs F2's real cq.sh at
  launch; the resume kind's render is covered by the sandbox tests.

## 10. Files (H2; md5sum at the end of the build)
| File | md5 | Role |
|---|---|---|
| final2_make_jobs.py | f0f868103e99a5a7ffcbffb1d2def7be | job list builder (10 resume lines) |
| jobs/jobs_fin2.txt | 7efbf54cbdbaae747781089aadb056cd | the job list (= IO2/jobs.txt of step 5) |
| final2_queue.sh | bc232ccb869ff850dfbc545f5c490ea0 | steps 5 to 9 and 11 (build, resumecopy, render, place, guard, arm, status) |
| final2_rendercmp.py | 7a0bc2bcc010f1e01d76465ca7a737a0 | render check |
| diskguard6.sh | 8137e124e6dd0ccc1d9f59ccf61483bb | cv02 disk guard for fin2 (= diskguard5.sh, queue/stop/log changed) |
| final2_relay.sh | f01da9c5f11df6ca09c007653f382d5c | step 10 relay (relay_w1c.sh 74a2ec3d unchanged) |
| final2_codeproof.sh | 66d5c9d0c6f384270636dbf4adbb34d9 | step 3, code proof F -> F2 |
| final2_smoke.sh | 3a383bf1bbd70a91fb0a32d5149b9811 | the missing smoke and the resume proof (gaint CPU) |
| ckcmp.py | 243921104765db451a4a19ccc86cec0a | checkpoint / metrics comparison used by the smoke |
| final2_patch_bnrecal.py | 8e663bb250668b33a669bdf84dd8d27f | record only: the uncommitted patch of the PATCH=1 smoke, superseded by commit 9967d59 |
| evidence/ | see evidence/MD5_evidence.txt (0128655f62d774398d9222fbb502972c, 10 files) | outputs of section 8 |
Commit F2: 9967d59abaab03cef83c1e3014840b2359ef45d7 (tree adcdf7ec59ff30e7a714808ca94dd46e4a63628f; parent 9330f8b, whose parent is F 821dfad; worktree clean); scripts/train.py 6dc3a22a, src/trainers/weight_avg.py 7fe1004f, cq.sh 08d0c308, cq_setup.sh 9684c116. Nothing committed in bench_wt_fin (F unchanged).
