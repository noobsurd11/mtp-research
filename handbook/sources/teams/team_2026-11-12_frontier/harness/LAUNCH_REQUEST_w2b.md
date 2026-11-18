# Launch request: wave 2b on gaint, la_ce and layered_ci (w2b builder, 17 Nov 2026, 17:28 to 19:18 IST; revision 3: the lead's la_ce rulings of 17:33, REVIEW_W2B round 1, the K0 to K4 rulings and the read tools)

Status: built and checked on CPU, queues PREPARED (harness/w2b/bq_local/), **nothing armed, no GPU used**. E = measured
by my own command, S = judgement. Pre-registered reads: `harness/w2b/READ_PLAN_w2b.md`. Evidence: `harness/w2b/evidence/`.
**Ruled (lead, log.md "17 Nov 17:33"):** la_ce Q1 to Q7; the card at 73540e7 matches Q1 (per fold) and is unchanged since
(REVIEW_W2B round 1 PASS, 5377ef47; its N6 test gap is closed in f678381). READ_PLAN section 1 is the Q6 rule with a
source for every element. **Ruled (lead, received 19:10 to 19:16):** K0 to K4 and the Q6 corrections (a: P1, P2 and L1
must hold on the 532 AND the 416 clean cells, guards judged on the 532 and printed for both; b: G5 false px bound 1.5 x
PF at OP-C), and the pre-declared la_ce_full follow-up (log 18:00), all in READ_PLAN revision 3. The read script, count
step and verdict step are built and tested (step 6). Nothing is open. Repo, cards and queue pins unchanged since the
f678381 re-pin.

## 1. Code
- Worktree `/home/noob/work/bench_wt_w2b`, branch `bench_w2b` (new; from c57508e, the wave 2a deploy), **commit
  f678381b1906575a69403e54f9c823f5f02bee28** (f678381, the DEPLOY), tree clean (untracked: the data/ links as in
  bench_wt_w2). Not pushed. History: 73540e7 la_ce (reviewed, round 1 PASS); 4ef349e layered_ci; 5995379 SCHEMA.md line;
  f678381 review N6 test. `git diff --stat c57508e f678381`: 17 files, +1,103 -11.
- **Files changed after 73540e7** (E, `git diff --stat 73540e7 f678381`, 15 files): la_ce's own files ce_dice.py and
  la_ce_pf_v11.yaml unchanged; tests/test_w2b_la_ce.py +17 (N6: the matching row in the middle and last; a first-row
  resolver mutant fails it, E 19:06); src/losses/loss_factory.py +4 and scripts/train.py +6 (layered_ci hooks only:
  `loss.aux` -> losses["aux"], `data.aux_targets` builders; flag-gated); layered_ci files: bench/cards.py, bench/decision.py,
  bench/dumpfmt.py, bench/methods/SCHEMA.md, bench/methods/layered_ci_pf_v11.yaml, scripts/bench_infer.py,
  src/data/aux_targets.py, src/losses/aux_losses.py, src/models/aux_heads.py, src/models/model_factory.py,
  src/trainers/trainer.py, tests/test_w2b_layered_ci.py.
- **la_ce offsets (D Q1 to Q4):** per fold k, o^(k)_c = -mean over seeds 5 to 8 of the classbias_xfit bias b_{s,k,c}
  (gaint PF fits, classbias_b.tsv d6a2bf00), FREE classes only; one card with 5 rows keyed by the md5 of the root's
  splits/train.txt, picked in train.py, fail closed, logged (`LA_CE:` line). **Deviation from the spec text** (T10 spec
  l.156: "o_c = -mean over folds and seeds of b_c"): the pooled vector is rejected because the fits b_j (j != k) use
  fold-k labels, so they would set training scalars of the fold-k run; b_k is fitted on folds != k only, the status of
  OP-C itself (reviewer N1: fold-k labels still reach b_k at second order through the fold-j models, as for OP-C).
  **Inactive offset -4.0 sits at the edge of the fit grid** (-1.5 to +4.0; b_11 = +4.0 in all 45 PF fits, B1 2d); the
  wider grid failed its rule, so the registered OP-C value is used (D Q4). Unstable classes keep their means (D Q3).
- Every new behaviour is behind a key that no existing card has (E: render check, section 2):
  `loss.logit_offset` / `loss.logit_offset_by_train_md5` (la_ce; CE term only); `model.aux_heads`, `data.aux_targets`,
  `loss.aux`, `eval.decision` (layered_ci; the trainer refuses any one without the others); `bench_infer --decision`
  (default `card` = the card's rule; argmax24 cards unchanged); `dumpfmt.write_cell(extra=)` (default None).
- bench_wt_w2, bench_wt_final, bench_wt_c3s, bench_wt_b, bench_wt_udev, el_bench: untouched (E: 0 tracked changes, HEADs
  as before, logged at every check start).

## 2. Proofs (E, gaint CPU, nice 19, 2 lanes x 4 threads; ref = git archive c57508e, new = git archive 5995379, both under
/home/noob/work/bench_w2b_io; script harness/w2b/run_w2b_check.sh; log /home/noob/work/bench_w2b_io/check_5995379/run.log)
The DEPLOY f678381 differs from 5995379 in tests/test_w2b_la_ce.py only (E: `git diff --stat 5995379 f678381` = 1 file,
+17; md5 of every file of the two git archives equal except that one), so every run-path proof below holds for f678381;
full pytest re-run on a git archive of f678381: **471 passed, 4 skipped** (evidence/pytest_f678381.log).
| Check | Result (E) |
|---|---|
| Flag-off 5-step identity (identity_cpu.py 962379a6, compare_id 3b83b364), ref c57508e vs 5995379 | **IDENTICAL, 10 of 10**: PFV11 (house_r34_unetpp_pf_v11), HV11 (house_r34_unetpp_v11) on cv5v2_v11_f0; PFV1 (house_r34_unetpp_pf), HV1 (house_r34_unetpp) on cv5v2_v1_f0; RCS, SBJ (soft_band_jml), JMLH, EMA, SWAD, SPD (wave 2a cards) on cv5v2_v11_f0 |
| Render check: every card of c57508e (14), seeds 5, 6, five cv5v2_v11 roots, rendered at ref and at 5995379 | 140 of 140 md5-equal; card files equal |
| cfgcheck at 5995379 of existing run configs | W1-G 10 of 10, wave 2a (bq/w2a/jobs.txt d8be4f16) 61 of 61 `config OK (= card)` |
| PF train.py 5-step smoke, ref vs new code (train, val, final test) | metrics.json IDENTICAL without timing / run name / steps_per_sec |
| Dump writer flag off: W1-G w1g_pf_v11_f0_s5 dumped on CPU fp32 by the c57508e and the 5995379 bench_infer | IDENTICAL, 107 cells, 535 arrays; manifests differ only in code / writer / time fields |
| Full pytest | f678381: **471 passed, 4 skipped**; 5995379: 470; c57508e archive: 446 passed, 4 skipped. New: tests/test_w2b_la_ce.py 10 (9 + N6) + tests/test_w2b_layered_ci.py 13 = 23 (all pass; evidence/pytest_w2b_unit.log); the other 2 are `tests/test_bench_cards.py::test_card_model_builds_on_cpu` on the 2 new cards (14 -> 16 cases, E by --collect-only) |
| New-card 5-step train.py smokes (fold 0 and fold 3) | la_ce f0, f3: rc 0, 0 Traceback, 0 nan, Labelled 425 / 428, cfgcheck = card except the 5 smoke overrides, `LA_CE:` line with the fold's own row (f0 train.txt 96d3154c..., f3 b65ff0f2...); layered_ci f0, f3: rc 0, 0 Traceback, 0 nan, step lines carry loss_aux / aux_inact_region_bce / _dice (loss = loss_sup + loss_aux), final test ran the layered rule (`TEST ... decision rule layered_ci_replace`, metrics.json test_final_rules) |
| Layered dump path on a trained core (harness/w2b/layered_dump_shim_test.sh; shim = W1-G f0 s5 weights + the aux head at its seed-5 init; mechanics, not a result) | argmax24 readout = plain PF dump of the same checkpoint, IDENTICAL (107 cells, 535 arrays); layered_ci_replace and layered_ci_union: 107 of 107 cells pass the writer check on read, crack px per cell = the argmax readout's in 107 of 107, p_inact_softmax = the plain p_inact in 107 of 107, manifest decision_rule and decision_t_I 0.5; 176 MB per fold (134 MB argmax) |
| Unit tests of note | P532 crack px inside the layered target: 48,934 of 307,593 = **15.9%** (spec band 15 to 25%, spec E "about 20%"); target = augmented-target for the 8 dihedral ops on 20 real masks; core init, global RNG state and z24 equal to the bare PF model at seed 5; crack px count of the layered decision = argmax's on 50 real W1-G cells; la_ce absent / zero offset = the c57508e loss bit for bit |
| Count tool `harness/w2b/w2b_counts.py` (READ_PLAN R1 to R5, G4, G5) | test_w2b_counts.py on the finished wave 2a read: PF and RCS inactive IoU, precision, region recall = bench_read_w1 (6 dp); RCS - PF inactive IoU delta and 95% bounds = bench_read_w1 (4 dp): PASS |
| Read tools (run_read_w2b.sh, w2b_verdict.py, w2b_counts.py) | w2b_verdict_test.py 43 of 43 synthetic cases (every branch and boundary); w2b_verdict_shape_test.py PASS on the real wave 2a read (arms renamed, no number printed); test_run_read_w2b.sh 20 of 20 (SHOW for both arms and PF4, 11 refusal cases, complete fixtures pass); test_w2b_counts.py PASS after the JSON output was added |
| Queue arming (harness/w2b/w2b_armcheck.sh: bench_setup refusals + bench_q arming checks, read-only) | 4 of 4 `ARMCHECK PASS` on the prepared copies (evidence/armcheck_bq_local.txt) |

**Found, pre-existing, not changed (E):** a dump of a 5-step (untrained) model fails the c57508e writer's own check: the c57508e
bench_infer on a 5-step PF smoke model stops with "pred disagrees with where(m_crack > 0, 14, oth) at 1 px" (18:55). Cause
(evidence/find_px_writer_tie.py): classes 7 and 5 with logits 6e-8 apart and equal float32 softmax; pred = argmax(logits) = 7,
oth = argmax(log p) = 5, m_crack = -0.80, and the check's tie tolerance looks at |m_crack| only. Trained models do not hit it
(every W1-G and wave 2a GPU dump; the CPU dump identity above). So the 5-step dump test of my check script fails for every card
including PF; the trained-core shim test replaces it. S: a later writer fix could allow non-crack ties; not in this branch.
Also stopped by me (PID, logged): a first check at 17:38 that ran on the live worktree (restarted on a git archive), and the
73540e7 check's pytest at 18:01 (its identity, render and cfgcheck lines stand; the full set re-ran on 5995379).

## 3. Arms and cards (config diff against house_r34_unetpp_pf_v11, `python -m bench.cards diff`)
| Arm (run prefix) | Card (md5) | Rendered config diff | Decision / dumps |
|---|---|---|---|
| la_ce (`w2b_lace`) | la_ce_pf_v11 (8bcd481a) | 5 keys `loss.logit_offset_by_train_md5.<md5 of the fold's train.txt>` = [24 floats] (fold k: -mean over seeds 5-8 of the classbias_xfit b_k; inactive -4.0, splice -1.75..-2.0, material -1.19..-1.44, gridline -1.0, edge_dark -0.5..-0.63, ribbons -0.38..-0.5, sp_multi / sp_mono -0.13..-0.25, border / padding / frame_edge -0.31..+0.19; background and crack 0) | argmax24; 1 dump per run |
| layered_ci (`w2b_lci`, pathfinder `w2b_lcipath`) | layered_ci_pf_v11 (50b62a11) | model.aux_heads.inact_region {channels 1, kernel 3}; data.aux_targets [inact_region_fill]; loss.aux.inact_region {bce_dice, weight 1.0}; eval.decision {layered_ci_replace, t_I 0.5} | layered_ci_replace (primary) + `<run>.argmax24` + `<run>.layered_ci_union` |
Comparators (no new runs): W1-G PF seeds 5, 6 (A/A with W1-G2 7, 8) and PF at OP-C (bench_udev/opc/dumps_gaint, seeds 5, 6).

## 4. Queues (generator harness/w2b/make_w2b.py; copies in harness/w2b/bq_local/<q>; each launch.sh exports the pins and
execs bench_setup.sh; DEPLOY f678381, REPO /home/noob/work/bench_wt_w2b, MAXH 120)
| Queue dir (copy from harness/w2b/bq_local/) | jobs.txt md5 (lines, MAXC) | dump/jobs.txt md5 (lines, MAXC) | launch.sh md5 |
|---|---|---|---|
| bq/w2b_smoke | 973308a9f2dd5f384b2826930b4be23c (3, 1): PF, la_ce, layered_ci, fold 0 seed 5, `--exit_after_step 200` | none | cf438b5a35f1af7fc2c01852d07ff011 |
| bq/w2b_lcipath | 06752167e7dd291c053de9197c7ec667 (1, 1): w2b_lcipath_f0_s5 | b798b2a67007bb909f32254387d34073 (3, 1) | 66fbf7f72df03903ab5ce3a5e171ea1a |
| bq/w2b_lace | f89627eb2034c22a3af2ed3c5e594e23 (10, 2): w2b_lace_f0..4_s5, then _s6 | 3759e8249fa4a112493f0258e11e9adb (10, 1) | 34b4e0ded926036266e007fcd7c3654b |
| bq/w2b_lci | cd7d1c9d220254fc598f216ed1b38d74 (10, 2): w2b_lci_f0..4_s5, then _s6 | 135778ff7c09635d98cf6de59cf16b10 (30, 1): layered, then argmax24, then union | 3b63508b1f9a2a684c12520acc7cdadf |
Dumps go to /home/noob/work/bench_dumps/w2b (cuda fp32, no logp; W1-G settings).
- Pins: the launch.sh md5s above are for DEPLOY f678381 (re-pinned 19:07, jobs and dump jobs md5s unchanged). Superseded pins for DEPLOY 5995379 (not to be used): smoke 0bb7e20a, lcipath 67535151, lace e097d77f, lci 1cd4a391.
- Gates: 11,000 MiB per training start (card gate; peaks unmeasured), 6,200 per dump (W1-G: fp32 dump peak 4,098 + 2,048);
  120 s between starts (shared gpu_gate); a queue waits while any GPU process not its own holds > 1,024 MiB, so the w2b
  queues run after LOSO-2 / w2a3, never beside them. finllm 6206 protected (PROTECT default).
- Memory (S): la_ce adds one broadcast add; layered_ci one 3x3 conv (16 -> 1) at 512 px, a (B, 1, 512, 512) map and its
  loss, about +0.1 GB in training; its final test (eval batch 8) clones the 24 logits about 3 times for the decision
  (about +0.8 GB transient, after training). Measured by step 2 (smoke, training peak) and by the pathfinder (whole run).
  MAXC rule: if a smoke peak > 8,000 MiB, `echo 1 > /home/noob/work/bq/<q>/MAXC` before arming that screen.
- Time (S, from wave 2a / LOSO-2 logs: 1.68 h of wall time per run at 2 lanes, 0.87 h alone; dumps 1 to 2 min + 120 s
  gaps): smoke about 10 min; pathfinder about 1 h + 3 dumps 10 min; la_ce screen about 8.5 h + 10 dumps 0.4 h; layered_ci
  screen about 8.5 h + 30 dumps 1.2 h. GPU-h: about 0.1 + 1 + 9 + 10 = 20.
- Disk (S): a run folder about 0.5 GB (w2a: 499 MB), a dump without logp about 0.14 GB (w2a rcs fold 0: 137 MB):
  la_ce 5 + 1.4 GB, layered_ci 5 + 4.9 GB (layered and union dumps 176 MB per fold in the shim test, argmax 134 MB), pathfinder 0.5 + 0.5 GB, smokes < 0.01 GB: about 17 GB. gaint free 114 GB (E, 17:5x).

## 5. Launch steps (lead, on gaint; every launch.sh refuses and starts nothing if a pin, HEAD or a folder check fails)
Shorthand: `B=/home/noob/work/bq; H=/home/yugma/mtp/research/team_2026-11-12_frontier/harness/w2b`.
0. Check (read-only): `git -C /home/noob/work/bench_wt_w2b rev-parse HEAD` = f678381b1906575a69403e54f9c823f5f02bee28 and
   `git -C /home/noob/work/bench_wt_w2b status --porcelain -uno | wc -l` = 0; `grep -c "IDENTICAL" /home/noob/work/bench_w2b_io/check_5995379/run.log` = 12
   (10 identity arms, the PF smoke, the dump identity; section 2); `cd $H && md5sum -c MD5.txt` and `cd /home/noob/work/bench_wt_w2b && md5sum -c $H/REPO_MD5.txt` (all OK; the repo list = the 17 files changed since c57508e, equal to HEAD f678381).
1. Place: `for q in w2b_smoke w2b_lcipath w2b_lace w2b_lci; do [ -e $B/$q ] && echo "$q exists" || cp -r $H/bq_local/$q $B/$q; done`;
   then `for q in w2b_smoke w2b_lcipath w2b_lace w2b_lci; do bash $H/w2b_armcheck.sh $B/$q; done` (4 x ARMCHECK PASS).
   Stop / undo: `rm -r $B/w2b_<q>` (nothing armed yet).
2. Memory smoke, after the gaint chain ahead of it has written `chain done` (today: udev_loso2, then w2a3). Unattended:
   `tmux new-session -d -s bench_wait_w2b_smoke "PREV=$B/w2a3 Q=$B/w2b_smoke PIN=cf438b5a35f1af7fc2c01852d07ff011 bash /home/yugma/mtp/research/team_2026-11-12_frontier/harness/udev/wait_then_arm.sh"`
   (reviewed waiter 871d3334; or by hand `bash $B/w2b_smoke/launch.sh` once `grep -c "chain done" $B/w2a3/chain.log` = 1).
   Read: `grep -E "config OK|CONFIG FAIL|startup line|trained smoke|HOLD" $B/w2b_smoke/launch.log` (3 config OK, 3 startup OK,
   3 rc=3); peaks `for a in pf lace lci; do echo $a $(grep -o "run_name=smoke_w2b_${a}_f0_s5:[0-9]*" $B/w2b_smoke/gpumem.log | cut -d: -f2 | sort -n | tail -1); done`;
   `grep -c Traceback /home/noob/work/bench_wt_w2b/experiments/smoke_w2b_*.stdout` (0 each); `grep -m1 "LA_CE:" /home/noob/work/bench_wt_w2b/experiments/smoke_w2b_lace_f0_s5/train.log`
   (the fold-0 row, train.txt md5 96d3154c...); `grep -m1 -o "loss_aux=[0-9.]*" /home/noob/work/bench_wt_w2b/experiments/smoke_w2b_lci_f0_s5/train.log`.
   Keep the smoke folders (no checkpoint; the pathfinder check reads their logs).
   Stop: `touch $B/w2b_smoke/NOSTART` (waiter) / `touch $B/w2b_smoke/HOLD` (queue); a running job only by `$B/w2b_smoke/pids/<name>.pid`
   after `ps -o pid,user,args -p <pid>`. Never a pattern kill.
3. layered_ci pathfinder: `tmux new-session -d -s bench_wait_w2b_lcipath "PREV=$B/w2b_smoke Q=$B/w2b_lcipath PIN=66fbf7f72df03903ab5ce3a5e171ea1a bash /home/yugma/mtp/research/team_2026-11-12_frontier/harness/udev/wait_then_arm.sh"`.
   First-job live check: `grep -E "armed|w2b_lcipath_f0_s5 (config|startup)" $B/w2b_lcipath/launch.log` = `config OK (= card)` and
   `startup line OK: Labelled: 425 (/home/noob/work/bench_data/roots/cv5v2_v11_f0/splits/train.txt)  unlabelled: 0 (-)  val: 107  test: 107`.
   After `chain done`: `cd /tmp && CUDA_VISIBLE_DEVICES="" nice -n 19 /home/noob/work/el-fault-detection/.venv/bin/python $H/lci_pathfinder_check.py --out /home/noob/work/bench_w2b_io/pathfinder_check.txt`
   (C1 to C4, last line `PATHFINDER PASS` or `NOT PASSED`). Stop: as step 2 with `w2b_lcipath`.
4. la_ce screen (Q1 to Q7 ruled 17:33): `tmux new-session -d -s bench_wait_w2b_lace "PREV=$B/w2b_lcipath Q=$B/w2b_lace PIN=34b4e0ded926036266e007fcd7c3654b bash /home/yugma/mtp/research/team_2026-11-12_frontier/harness/udev/wait_then_arm.sh"`.
   Live check: `w2b_lace_f0_s5 config OK (= card)`, startup line as step 3, and `grep -m1 "LA_CE:" /home/noob/work/bench_wt_w2b/experiments/w2b_lace_f0_s5/train.log`.
   Stop: as step 2 with `w2b_lace`.
5. layered_ci screen, only if step 3 printed `PATHFINDER PASS`: `tmux new-session -d -s bench_wait_w2b_lci "PREV=$B/w2b_lace Q=$B/w2b_lci PIN=3b63508b1f9a2a684c12520acc7cdadf bash /home/yugma/mtp/research/team_2026-11-12_frontier/harness/udev/wait_then_arm.sh"`
   (or by hand after the la_ce chain). Live check as step 4 (`w2b_lci_f0_s5`, and `loss_aux=` on its step lines).
   Stop: as step 2 with `w2b_lci`.
6. Reads (CPU, once an arm's dump chain is done; READ_PLAN_w2b.md sections 1, 2 and 5):
   `ARM=lace bash /home/yugma/mtp/research/team_2026-11-12_frontier/harness/w2b/run_read_w2b.sh` and later `ARM=lci bash /home/yugma/mtp/research/team_2026-11-12_frontier/harness/w2b/run_read_w2b.sh`
   (output /home/noob/work/bench_reads/w2b_<arm>: run.log, read/, counts_532.txt, counts_416.txt, verdict.txt with one
   PASS / FAIL line per element and one `VERDICT <arm>: PROMOTE / DROP / PARK` line, MD5.txt). It refuses, writing
   nothing, if a pin, a dump, a trained line or a manifest field is not as expected. Optional sensitivity read (never the
   verdict): `PF4=1 ARM=<arm> bash /home/yugma/mtp/research/team_2026-11-12_frontier/harness/w2b/run_read_w2b.sh` (folder w2b_pf4_<arm>). Preview without checks: `SHOW=1 ARM=<arm> ...`.
   Stop: it is a CPU job in the caller's shell (about 15 min, bench_read_w1 with 8 workers); Ctrl-C, or `kill <pid>` of
   its bench_read_w1 process after `ps -o pid,user,args -p <pid>`; a partial output folder is then removed by hand before a rerun.
   If la_ce comes out null on mIoU-R13 or inactive, the pre-declared follow-up is la_ce_full (READ_PLAN 1), not a closure.

## 6. md5 (full md5: harness/w2b/MD5.txt for harness files, harness/w2b/REPO_MD5.txt for the repo files; worktree paths)
| File | md5 (8) |
|---|---|
| harness/w2b/bq_local/w2b_lace/dump/jobs.txt | 3759e824 |
| harness/w2b/bq_local/w2b_lace/jobs.txt | f89627eb |
| harness/w2b/bq_local/w2b_lace/launch.sh | 34b4e0de |
| harness/w2b/bq_local/w2b_lci/dump/jobs.txt | 135778ff |
| harness/w2b/bq_local/w2b_lci/jobs.txt | cd7d1c9d |
| harness/w2b/bq_local/w2b_lci/launch.sh | 3b63508b |
| harness/w2b/bq_local/w2b_lcipath/dump/jobs.txt | b798b2a6 |
| harness/w2b/bq_local/w2b_lcipath/jobs.txt | 06752167 |
| harness/w2b/bq_local/w2b_lcipath/launch.sh | 66fbf7f7 |
| harness/w2b/bq_local/w2b_smoke/jobs.txt | 973308a9 |
| harness/w2b/bq_local/w2b_smoke/launch.sh | cf438b5a |
| harness/w2b/dump_compare.py | eb515ae4 |
| harness/w2b/layered_dump_shim_test.sh | 579e01a4 |
| harness/w2b/lci_pathfinder_check.py | ec96c6e8 |
| harness/w2b/make_la_ce_card.py | d671b90d |
| harness/w2b/make_w2b.py | d73386e3 |
| harness/w2b/READ_PLAN_w2b.md | 3f38d910 |
| harness/w2b/run_read_w2b.sh | 8d644288 |
| harness/w2b/run_w2b_check.sh | 2407c83b |
| harness/w2b/test_run_read_w2b.sh | e60c4695 |
| harness/w2b/test_w2b_counts.py | 78f16810 |
| harness/w2b/w2b_armcheck.sh | ec809a7b |
| harness/w2b/w2b_counts.py | a23dd544 |
| harness/w2b/w2b_verdict.py | 1ace40f7 |
| harness/w2b/w2b_verdict_shape_test.py | 56ad06a1 |
| harness/w2b/w2b_verdict_test.py | 23b16576 |
| bench/cards.py | a9ac5911 |
| bench/decision.py | abb06863 |
| bench/dumpfmt.py | 808a49f8 |
| bench/methods/SCHEMA.md | 17f00b07 |
| bench/methods/la_ce_pf_v11.yaml | 8bcd481a |
| bench/methods/layered_ci_pf_v11.yaml | 50b62a11 |
| scripts/bench_infer.py | ce9422fe |
| scripts/train.py | 396cdca3 |
| src/data/aux_targets.py | 3df49656 |
| src/losses/aux_losses.py | cb148f89 |
| src/losses/ce_dice.py | 7f6cf1f9 |
| src/losses/loss_factory.py | 7c76af73 |
| src/models/aux_heads.py | cd030aa1 |
| src/models/model_factory.py | ab41a019 |
| src/trainers/trainer.py | 022c13e5 |
| tests/test_w2b_la_ce.py | c4feb0c6 |
| tests/test_w2b_layered_ci.py | cd8382c3 |
| harness/w2b/MD5.txt, REPO_MD5.txt | (full md5 of every file above and of the MAXC files) |

## 7. Not tested / owed (S)
- No GPU run: peak memory and step time of both arms are unmeasured until step 2; the pathfinder is the first full run
  of the aux head (CPU: 5-step train.py smokes and 107-cell dumps from the 5-step checkpoint).
- The read script was tested on fixtures (manifests only), synthetic verdict cases and the real wave 2a read (shapes,
  counts reproduction), not on w2b dumps (none exist yet): its first real run is the first la_ce read.
- The atlas bucket FP-on-crack on the layered_ci dumps (READ_PLAN 2, printed only) needs `t10_atlas.py` pointed at the arm.
- la_ce reviewer notes carried (REVIEW_W2B r1): N4, the inactive Dice on softmax(z) may pull back much of the -4.0 CE offset, so an inactive null of la_ce may come from the spec's 'CE term only' design; N5, a root with no row passes the live check and dies at the loss build (all queue roots have rows, E: 4 x ARMCHECK PASS and the f0 / f3 smokes).
