# Review of the unseen-module block integration (LAUNCH_REQUEST_udev.md) and the two T14 CPU analyses, 15 Nov 2026

Reviewer: independent agent (built none of it). Round 0: 18:47 to 19:02 and 21:37 to 21:40 IST (item 5 FAIL; copy kept at bench_reads/stageC/review/REVIEW_UDEV_round0_5280045f.md). **Re-review after integrator fix round 1: 21:42 to 21:46 IST.**
Object: branch bench_udev (merge ae4dd10 = b5bf0ae + b12fca8; T14 commits 1a7b4f2, 24aa039 on the branch only); worktree /home/noob/work/bench_wt_udev, now **detached at ae4dd10**; queue dirs /home/noob/work/bq/udev_{loso2,infer,tta_path,tta,tta_f51}; LAUNCH_REQUEST_udev.md md5 0534857d (76 lines); results/stageC/{GAP_CENSUS,LABEL_VERSION_STRATA}.md.
Own check files: /home/noob/work/bench_reads/stageC/review/ (round 0: rv_check.sh, rv_jobs.py, rv_sets_copy.py, rv_render.sh + rv_render_drv.py, rv_armcheck.sh, rv_recompute.py, item*.out, run.log, pytest_*.log, own archives arch_*; re-review: fix1_state.out, fix1_bytes.out, fix1_item1.out, fix1_rv_jobs.out, fix1_armcheck.out, fix1_safety.out). CPU only; the re-review started no tmux session and no long process; no process of mine is left.
E = measured by my own command; S = judgement. No sealed label or prediction read; no training stdout or metrics file of a benchmark run opened.

## Verdict
| Item | Verdict |
|---|---|
| 1. Merge | **PASS** |
| 2. Identity, render, pytest | **PASS** (proofs at ae4dd10 hold for the worktree: 741 of 741 tracked files byte-equal to my archive) |
| 3. skr01 on a LOSO-2 root | **PASS** |
| 4. Job lists | **PASS** |
| 5. Safety and arming commands | **PASS** (round 0 FAIL closed: HEAD = DEPLOY; 5 x ARMCHECK PASS) with one note on the TTA re-prep |
| 6. The two CPU analyses | **PASS WITH NOTE** |

Items 1 to 5 pass. The lead may arm per LAUNCH_REQUEST_udev s4, strictly after bq/w2a2 writes `chain done` (none yet at 21:43), and must keep the s0 rule: no commit, checkout or switch in bench_wt_udev until the last udev queue ends.

## Fix round 1 check (E, 21:42 to 21:44)
- `git -C /home/noob/work/bench_wt_udev rev-parse HEAD` = ae4dd1094972d00bb55000d76f94598b946a1b68, tree 2a8bf0bd = `git merge-tree --write-tree b5bf0ae b12fca8`; `symbolic-ref -q HEAD` empty (detached); branch bench_udev = 24aa039 (T14 commits kept, not checked out anywhere; `worktree list` shows bench_wt_udev "(detached HEAD)").
- `git status --porcelain` (incl. untracked) = 0 lines. Ignored only: 3 data/ links (same targets as bench_wt_w2 and as my archive) and __pycache__ dirs. Orphan pycs of the 6 T14 files remain in bench/, scripts/, tests/__pycache__ (S: harmless, Python never imports a pyc from __pycache__ without its source; not tracked, not seen by bench_setup).
- My own byte compare: all **741 of 741** tracked files of the worktree = my archive arch_ae4dd10 (0 differ; archive extras = 3 data links + REVISION). So my round 0 proofs made on that archive (identity IDENTICAL, render 648 of 648, pytest 670 passed, skr01 smoke, job checks) apply to the worktree as it is now.
- `ae4dd10..bench_udev` = 6 added files (A bench/gap_census.py, bench/label_strata.py, scripts/bench_gap_census.py, scripts/bench_label_strata.py, tests/test_gap_census.py, tests/test_label_strata.py): the fix removed only those from the worktree.
- Protected trees: el_bench 31c0c36, bench_wt_w2 c57508e, bench_wt_a 81b4505, bench_wt_b b5bf0ae, rows1 52e3f14, rows2 b12fca8: 0 tracked changes each.

## 1. Merge: PASS
E (fix1_item1.out, re-run 21:43; round 0 item1_merge.out, m_*.txt):
- ae4dd10 parents b5bf0ae and b12fca8; both ancestors of HEAD; merge base 31c0c36. bench_b HEAD = b5bf0ae = the commit REVIEW_STAGEB_FIX passed (line 3 object, line 18 "No item fails").
- `diff b5bf0ae HEAD` byte-equal to `diff 31c0c36 b12fca8` (30 paths); `diff b12fca8 HEAD` byte-equal to `diff 31c0c36 b5bf0ae` (107 paths); overlapping paths 0. HEAD tree = merge-tree of the parents: no hand-resolved hunk exists.
- The one rows2 code hunk (src/models/bench_models.py, read in full in round 0): `_swap_global_pool` only for deeplabv3 / deeplabv3plus; no udev card uses DeepLab (house_r34_unetpp_pf_v11 157 lines, ema 36, swad 36, rcs 18, soft_band_jml 18, jml_hard 18, skr01 4), so it is not reached.

## 2. Identity, render, pytest: PASS
E (round 0 run.log, id/, render/, pytest_*.log; applies via the 741-file byte compare above):
- Own 5-step CPU identity, identity_cpu.py 962379a6, compare_id 3b83b364, PFV11 (house_r34_unetpp_pf_v11, cv5v2_v11_f0, seed 5), own archive of 31c0c36 vs own archive of ae4dd10: **IDENTICAL** (5 steps, all fields except code / sec), 19:02:22.
- Rendered config of every card in bench/methods and bench/methods_cv02 at the tree it was reviewed on vs the deploy archive: W1 125, W1 on LOSO-2 roots 8, W2A 61 tuples + 90 grid, R1 50 + 50, W1 methods_cv02 at 52e3f14 100 and at b12fca8 100, R2 30 + 30, skr01 on LOSO-2 roots 4: **648 of 648 equal**, 0 errors; 34 of 34 card files byte-equal to their reviewed tree; bench/cards.py = c57508e.
- Full pytest in a fresh archive of ae4dd10: **670 passed, 4 skipped**, rc 0.

## 3. skr01 on a LOSO-2 root: PASS
E (round 0 item3_*.out, id/PFL_vs_SKL_cmp.txt, exp/):
- `bench.cards diff` PF v11 -> skr01_pf_v11: only `loss.skel_recall.weight: <absent> -> 0.1`. Rendered PF v11 on cv5v2_v11_f0 vs skr01 on cvloso2_v11_f0: only the skel_recall block and data.root.
- Own 5-step CPU train.py, skr01 on cvloso2_v11_f0 seed 5: rc 0, Traceback 0, nan 0; startup `Labelled: 418 (.../cvloso2_v11_f0/splits/train.txt) unlabelled: 0 (-) val: 114 test: 114`; 5 of 5 steps log `loss_srec=` 0.967 to 0.975 (finite, not 0). Identity PF vs skr01 on the same root: DIFF from step-0 loss onward.

## 4. Job lists: PASS
E (fix1_rv_jobs.out: rv_jobs.py, own code, no bench import, re-run 21:43: **RESULT PASS, 59 checks, 0 FAIL**; round 0 item4_*.out):
- Pins (= launch.sh, re-measured 21:43): udev_loso2 jobs 6c07b4db (12, MAXC 2) + dump 1718f618 (12, MAXC 1); udev_infer 1bcb077e (174, MAXC 1); udev_tta_path 5e1dedd3 (1); udev_tta b40046a0 (80); udev_tta_f51 ea13248c (20). Job files r--r--r--. Queue lists = stage B lists byte for byte; loso2 dump = 33c2af8a with `--logp` added only.
- loso2: PF f0 / f1 x s5 to 8 and skr01 f0 / f1 x s5, 6; card, seed, root agree with each name; gates PF 9,000, skr01 9,100 (>= card 7,622 and >= gaint SKR 7,020 + 2,048); seed-major; 12 dumps cuda fp32 `--logp` on cvloso2_f<k> of the run's own root.
- Roots (round 0): ROOTS_cvloso2_v11.md5 c82ebe1c OK, test.txt 296f2c47 / 2db4e4f1, f0 418 / 114 / 114, f1 482 / 50 / 50; masks_v11 9c0e0687; ROOTS.md5 81e7e6c1; B3 MANIFEST 41a0c35c; shvoof_v2 8dda906e = sets.py pin; stage B rv_sets.py copy ALL PASS (40).
- Inference / TTA 275 lines: latest.pth exists, root = run's fold root, set fold = run's fold, one set per run dir, 0 output collisions; test50 / e1_106 raise SealedSetError; 0 sealed words in any list. shvoof lines allowed (REVIEW_STAGEB_FIX item 1 passed U2).
- 299 names unique; 0 existing experiments/<name> or .stdout in the worktree (its 53 experiments/ entries are tracked history dirs, none a job name).
- Nothing armed (21:43): each udev dir holds only jobs.txt, MAXC, launch.sh, prep.log (+ dump/{jobs.txt, MAXC}); no queue.pid, pids/, HOLD, launch.log, chain.log; tmux has no udev or bench_int session.

## 5. Safety and arming commands: PASS (round 0 FAIL closed)
E (fix1_safety.out, fix1_armcheck.out, 21:43):
- Queue code = the reviewed one: bench_q 226807e0, bench_lib 1af2ed69, bench_gate 51bcf13c, bench_guard b09b53c0, bench_gpumem a939464d, bench_setup 436c32f2, bench_chain 705df27e at HEAD = bench_wt_w2 (c57508e, the running w2a2). `diff --stat c57508e HEAD -- bench/q/`: only 6 new cv02 files.
- Pattern kills in bench, scripts, src (tests excluded): 0. PROTECT default 6206 (bench_lib l.6, l.16); outside rule OUTSIDE_MIB 1,024 (l.39); GAPSEC 120; bench_q l.94 deploy_ok (HEAD prefix = DEPLOY and no tracked change) before every start, HOLD on mismatch. finllm 6206 alive (root, 16 d). /home/noob/work/gpu_gate holds no HOLD.
- launch.sh x 5: `export Q SES=bench_q_udev_<q> DEPLOY=ae4dd1094972d00bb55000d76f94598b946a1b68 JOBS_MD5 (+ DJOBS_MD5 loso2 only) REPO=/home/noob/work/bench_wt_udev MAXH=120; exec bash $REPO/bench/q/bench_setup.sh`; md5s 4e198a7d, bfdbc2c1, 7c53dddd, b14b5123, 31d58d5a = the request's table. MAXC loso2 2, loso2 dump 1, others 1.
- My read-only replica of bench_setup.sh lines 15 to 27 (rv_armcheck.sh; compared line by line with the ae4dd10 blob again today): **5 x `ARMCHECK PASS (bench_setup would arm)`**. prep_udev.sh guards (l.22 HEAD = DEPLOY, l.23 no tracked change) hold.
- Arming commands checked (request s4): `bash /home/noob/work/bq/udev_loso2/launch.sh` after `grep -c "chain done" /home/noob/work/bq/w2a2/chain.log` = 1; then udev_infer, udev_tta_path (peak grep), udev_tta, optional udev_tta_f51, each after the previous `chain done`. Waiter harness/udev/wait_then_arm.sh 871d3334: acts only on "chain done", sleeps 150 s, re-checks the launch.sh md5 against PIN, NOSTART stops it; its wait.log in Q is not a bench_setup refusal file. First pair: `PREV=/home/noob/work/bq/w2a2 Q=/home/noob/work/bq/udev_loso2 PIN=4e198a7d87ce9184b7f32433bf32af0d`. TTA re-prep command (s3) now uses the full path; prep_udev.sh tta refuses if bq/udev_tta exists, requires TTA_GATE >= 6,200 and a number, re-checks every stage B pin; launch.sh carries a date, so the waiter PIN after a re-prep is the new md5, as s3 says.
- **Note (S, not a fail; it fails safe).** prep_udev.sh l.27 makes its temp dir with `mktemp -d /home/noob/work/bench_int_io/prep_XXXXXX`, and the request s6 says bench_int_io may be deleted after the review. If it is deleted before the TTA pathfinder, the s3 re-prep refuses (set -e on the failed mktemp) and udev_tta cannot be re-gated. Exact fix (lead): keep /home/noob/work/bench_int_io until udev_tta is armed, or run `mkdir -p /home/noob/work/bench_int_io` before the s3 re-prep. Checklist s5 items 1 and 5 also read bench_int_io/check/{run.log, render/render.tsv}.
- State (21:43): w2a2 chain.log has no "chain done" (w2a_ema_f0_s6 started 21:05); GPU = finllm 5,876 + two w2a2 runs 6,826 and 7,032 MiB; disk 194 GB free (request planned 202 GB at 18:40; margin about 27 GB, S: pool dumps of udev_infer, 23 GB, are the first to drop if short).

## 6. The two CPU analyses: PASS WITH NOTE
E (round 0 rv_recompute.py: own code, no bench import, W1-G PF s5 to 8, 532 pool cells; result files unchanged since 18:43, before my recompute 18:54):
- Rule before run: rule-only copies 18:33:44 < commits 18:36:17 (gap_census) and 18:40:12 (label_strata) < outputs; section 1 of both result files = the rule-only copies (head md5 d4ccc513, 36d39996).
- Tests meaningful: known-answer synthetic cracks (middle gap, one end, no prediction, ignore px, Y-junction, two gaps + end), partition on random masks, partition = bench_score missed count on 20 real cells; label_strata: identical versions give recall_S = bench_score relR@2, added -> A, deleted -> D, border band, sealed and non-pool stems raise.
- Recomputed: relR@2 **0.7985**, bound_gap **0.0573**; shares small 0.0095, whole 0.1734, gap 0.2846, end 0.5324; strata S 293,554, A 7,028, recall_A - recall_S **-0.0119**: equal to the result files.
- No sealed cell: dumps read through w1read.discover (sealed sets refused), stems asserted open / in the 532 pool list. The T14 code lives on branch bench_udev (24aa039), not in the deploy worktree since the fix; to re-run it, use a new worktree of bench_udev.
Note (S): OPEN for trace_crack gate (a) is driven by long gaps (about 0.6 of gap px in runs >= 100 px; runs <= 32 px give 0.011, below M); a continuity arm's spec should say which gap lengths it targets. label_version_strata decides nothing.

## Final table
| Product | Rule | Outcome | Rely? |
|---|---|---|---|
| bench_udev ae4dd10 (merge) | parents, patches, merge-tree | clean, no resolution, rows2 hunk unreached | yes |
| Identity PFV11, render 648, pytest 670 | flag-off identity, reviewed configs | IDENTICAL; 648 of 648; rc 0; worktree = archive (741 files) | yes |
| skr01 on cvloso2_v11_f0 | only skel_recall + root; term active | holds | yes |
| 5 queue dirs, job md5s, gates, roots, sets | stage B pins, LOSO-2 review | holds; nothing armed | yes |
| launch.sh x 5, prep_udev.sh | HEAD = DEPLOY ae4dd10, clean | 5 x ARMCHECK PASS; guards pass | yes; keep the s0 no-commit rule and bench_int_io until udev_tta is armed |
| GAP_CENSUS OPEN (bound_gap 0.0573 gaint) | rule s1, written first | recomputed equal | yes, with the long-gap note |
| LABEL_VERSION_STRATA (A - S -0.012, not separated) | descriptive | recomputed equal | yes (decides nothing) |
