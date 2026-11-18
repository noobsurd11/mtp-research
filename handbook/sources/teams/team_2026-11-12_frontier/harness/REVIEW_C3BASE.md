# Review of LAUNCH_REQUEST_c3base.md (PF and HOUSE baselines on cv5v3, 50 runs + 50 dumps), 16 Nov 2026

## Re-review after fix round 1 (12:41 to 12:47 IST; request md5 e339b6ec, 79 lines)

| Item | Verdict |
|---|---|
| 1 to 7 | **PASS** (round 1 evidence below still holds: E 12:41 W = 89b9ea5, porcelain 0, reflog last 01:24:22, no commit since; protected trees at their commits with 0 tracked changes; gaint pins dbd3632a / 9c7848ab / a172bf70; cv02 jobs 480b228a, LPG 1, MAXC 8, CODE.md5 -c OK 7cde26e4, REVISION 89b9ea5a...; relay stage CODE.md5 OK, relay_w1c.sh 74a2ec3d = my archive; 0 c3 outputs on cv02; bench_relay/c3base and bench_c3base absent) |
| 8. Safety | **PASS** (F8.1 and F8.2 fixed; 3 notes below, none blocks) |

**Overall PASS: the lead may launch, after the lead runs the F8.1 cleanup (lead's call) and the cv02 command no longer refuses.** Today the cv02 command refuses (85 GB free < 108), which is the intended behaviour.

Own files: /home/noob/work/bench_reads/stageC/review_c3base/r2/ (rv2_cv02_read.sh + cv02_read.out, cv02_dirs.txt, gen_list.txt, rv2_relaycheck.sh + relaycheck.out, rm_dry_rv.sh + rm_dry_rv.out, s6_cv02.txt / s6_fb.txt / s6_tick.txt + s6_exact.out, wrap_dq*.sh). cv02 read only (scripts by stdin over `ssh -a`; nothing written, nothing started). CPU only. Nothing armed.

### F8.1 cv02 disk: FIXED
E:
- **Relayed copies, my own check** (rv2_relaycheck.sh, not the integrator's script; tmux bench_c3_rv2, ended 12:43:57): for each of the 25 runs in the generated removal list, gaint `md5sum -c` of the relayed copy rc 0; md5(RUN.md5) = the `.ok` line = the list = cv02's md5(RUN.md5); dump lines in RUN.md5 = list count = files on gaint = files on cv02. **25 of 25 PASS.**
- **Removal script** c3_f81_rm_rows2_cv02.sh (cec29068, 41 lines, r--r--r--): I read every line. A dir is removed only if all four checks hold: cv02 md5(RUN.md5) = gaint's verified value; exactly one dir matches B/dumps/elbench1/*/<run>; its path matches `^/tmp/noob_el/bench_[0-9a-f]{7}/dumps/elbench1/<method>/<run>$` and lies under B; its file count = the verified count. Only that dump dir is removed (experiments, checkpoints, runs/ stay). A missing or extra file makes it SKIP (fails safe).
- **My own dry run on cv02** (rm line replaced by echo, log append removed; the 2 other pattern hits are a comment and `2>/dev/null`): 25 would remove, 0 SKIP. Nothing was written (no removal log; 26 rows2 dump dirs still there).
- **Generator** c3_f81_list.sh (d640ffe8): read-only on gaint; the `.ok` field 4 is the md5 that relay_w1c.sh writes (`date time RUN.md5 <md5> files <k>`); refuses an existing OUT and a B outside /tmp/noob_el/bench_<7 hex>.
- **Arm floor.** The exact s6 cv02 text with the arm step replaced by echo gives `REFUSED: cv02 /tmp free 85 GB < 108`. With 80 in place of 108 it reaches the arm step.
- **Safe for c3 cleanup during the run.** cq.sh reads a run's dump dir only in the RUN.md5 step (l.170-175); the job skip and ALL DONE use experiments/ and runs/*/RUN.md5, never dumps. relay_w1c.sh skips a run once `.ok/<name>` exists and counts done runs by `.ok`. So removing a relayed dump dir changes neither the queue nor the relay.
- **Tick text** (touch replaced by echo, sent to cv02 in single quotes): `cv02 free 85 GB`. An empty df parse makes `[ "$a" -ge 20 ]` fail, so it HOLDs (fails safe).

### F8.2 both queues armed: FIXED
E (s6_exact.out). The exact s6 text, copied by script, with only the final `bash .../cq_setup.sh` or `bash .../launch.sh` replaced by echo:
- **cv02 command** (checks the gaint Q):
  - REFUSED when a temp gaint Q holds queue.pid, gpumem.pid, pids/ or a non-empty launch.log (each tested alone).
  - Passes with an empty launch.log.
- **gaint fallback** (checks the cv02 Q):
  - Reaches launch.sh on the real cv02 Q.
  - REFUSED for the used cv02 dirs c3base_smoke, c3base_smoke2 and rows2.
  - REFUSED when cv02 is unreachable (port 1).
- **Markers are what arming really writes** (code read):
  - cv02: cq.sh l.42 creates pids/, queue.pid and launch.log; cq_gpumem.sh writes gpumem.pid; cq_setup.sh creates the session.
  - gaint: bench_q.sh l.33 creates pids/ and queue.pid; bench_gpumem.sh writes gpumem.pid and launch.log.
  - A queue that was armed and later stopped still leaves pids/ and a non-empty launch.log, so the check refuses for good.
- S: how the request prevents a double arm:
  - The only launch commands (s6, s9) each refuse when the other machine's queue was ever armed.
  - cq_setup.sh and bench_setup.sh each refuse when their own dir was used.
  - What is left is running launch.sh or cq_setup.sh directly. The request forbids that, except for a deliberate switch the lead makes and writes down. Note N2 closes even that, at no cost.

### Notes (S; none blocks)
- **N1, tick command wrapping.** s6 marks the tick as "C", and the C notation wraps commands in double quotes. The tick text holds double quotes and `$`. Wrapped that way, gaint's shell breaks the command (E: it tries to redirect from a file named `20; }` and ssh never runs). It fails loudly, not silently. Use this exact G form, which I checked with the touch replaced by echo:
  `ssh -n -a -o BatchMode=yes cv02@10.8.1.106 'a=$(df --output=avail -BG /tmp | tail -1 | tr -dc 0-9); echo "cv02 free ${a} GB"; [ "$a" -ge 20 ] || { touch /tmp/noob_el/bench_q/c3base/HOLD; echo "HELD: free ${a} GB < 20"; }'`
  In the in-run cleanup command, write `$H` out in full as /home/yugma/mtp/research/team_2026-11-12_frontier/harness/c3base.
- **N2, optional hardening.** Right after the cv02 arm succeeds, run G `touch /home/noob/work/bq/c3base/HOLD`; bench_setup.sh then refuses ("HOLD exists (armed or used)") even if someone runs launch.sh directly. If gaint is armed instead, run C `touch /tmp/noob_el/bench_q/c3base/HOLD`; cq_setup.sh then refuses. No pinned file changes. A deliberate switch then has to remove that HOLD by hand, which is the point.
- **N3, the margin is thin; regenerate the list first.**
  - E: free is 88,173,240 KiB = 84.1 GiB (df -BG rounds up to 85). The 25 listed dirs hold 24,320 MiB = 23.75 GiB. After removal that is about 107.8 GiB, and df -BG would show 108, just at the floor.
  - rows2 has since relayed a 26th run, r2_skr01_pf_v11_f0_s6 (988 MiB, `.ok` present).
  - Before removing, run c3_f81_list.sh again with a new OUT, so that every relayed rows2 run is listed (26 now, up to 30 when rows2 ends), and run that output instead (about +1 GiB per run).
  - If the arm still refuses, wait. Do not lower 108.

### Launch commands checked (round 2), in order
1. F8.1 cleanup (lead's call), G: `RD=/home/noob/work/bench_relay/rows2 B=/tmp/noob_el/bench_b12fca8 CUDA_VISIBLE_DEVICES= nice -n 19 ionice -c3 bash /home/yugma/mtp/research/team_2026-11-12_frontier/harness/c3base/c3_f81_list.sh /home/noob/work/bench_c3_io/f8/rm_rows2_<time>.sh` (expect `verified <n>, skipped 0`), then `ssh -a -o BatchMode=yes cv02@10.8.1.106 "bash -s" < /home/noob/work/bench_c3_io/f8/rm_rows2_<time>.sh` (expect `removed <n> dump dirs; skipped 0`). The checked c3_f81_rm_rows2_cv02.sh (cec29068, 25 runs) is equally valid.
2. Arm cv02: request s6 line "cv02 queue (G)", exactly as written (checked above; refuses below 108 GB and if the gaint Q was used). Then N2.
3. Relay: request s6, unchanged from round 1 (stage CODE.md5 OK 7cde26e4, relay_w1c.sh 74a2ec3d).
4. Every tick: the N1 G form. Relayed c3 dumps can be removed off cv02 with the two scripts and RD=/home/noob/work/bench_relay/c3base B=/tmp/noob_el/bench_89b9ea5 NAMES_RX=^c3_.
5. gaint fallback only if cv02 was never armed: request s6 line "gaint fallback", exactly as written (checked above).

---

## Round 1 review (12:21 to 12:40 IST; request md5 c78d69b2, 71 lines)

Reviewer: independent agent (built none of it). 12:21 to 12:40 IST. Request checked: md5 c78d69b2, 71 lines.
Own check files on gaint: /home/noob/work/bench_reads/stageC/review_c3base/ (rv_check.sh + run.log, id/, render/, pytest_89b9ea5.log, item1_merge.out, rv_roots.py + item3_roots_gaint.out, rv_rdiff.py + item3_rdiff.out, rv_cv02.sh + cv02_read.out + cv02_du.out, rv_cqrender.sh + item4_cqrender.out + cqsb/, rv_jobs.py + item5_jobs.out, item6_read.out + read/, did_dry*, item8_*.out; own archives arch_31c0c36, arch_89b9ea5).
CPU only (nice 19, at most 4 one-thread processes, tmux bench_c3_rv, ended by itself). On cv02 I only read (scripts piped by stdin over `ssh -a`, no python, nothing written or started). Nothing armed or launched. No training stdout or metrics file opened; no sealed set read. E = measured by my own command, S = judgement.

## Verdict

| Item | Verdict |
|---|---|
| 1. Merge | **PASS** |
| 2. Identity, renders, pytest | **PASS** |
| 3. cv5v3 data on both machines | **PASS** |
| 4. Queue code | **PASS** |
| 5. Jobs, pins, nothing armed | **PASS** |
| 6. Smokes and dump path | **PASS** |
| 7. Leakage rule | **PASS** |
| 8. Safety | **FAIL** (2 fixes, text and one operator step; no code, no re-pin) |

**Round 1 overall FAIL (superseded by the round 2 PASS at the top).** Items 1 to 7 hold. Item 8 has 2 gaps, F8.1 (cv02 disk) and F8.2 (no check that stops both queues being armed). Both fixes are below. Neither needs a commit, a redeploy or a new pin: the deploy 89b9ea5, both queue dirs and every md5 stay as they are. After the fix, a re-check of item 8 is enough.

## Required fixes (item 8)

**F8.1 cv02 disk headroom (required before arming cv02).** E: cv02 `/` (which holds /tmp) has 86 GB free at 06:55 UTC, 95% used. The request's own sizes: 50 runs x 1.6 GB = 80 GB, plus rows2's last runs (about 5 x 1.5 GB = 8 GB): 88 GB. That is more than is free. cq.sh has no disk guard. The request's only control is to delete each dump by hand once relayed, or touch HOLD, with a **daily** `df`. S: that is not enough on a shared disk. With 8 lanes free the queue can write about 13 GB per hour, and lead ticks have stopped for 10 h before (16 Nov 02:06 to 11:58). Filling the shared root filesystem would hurt other users' jobs.
Exact fix:
- (a) Before arming, make cv02 free space at least 108 GB (80 + 8 + 20). E: the clean source is the 25 rows2 dump dirs on cv02. They hold 24 GB under /tmp/noob_el/bench_b12fca8/dumps, and all 25 runs have `.ok` in /home/noob/work/bench_relay/rows2/.ok/. Remove each one only after `md5sum -c` of its relayed copy on gaint, as was done for W1-C (bench_d3a3280 dumps now 20 KB) and rows1 (bench_52e3f14 dumps 28 KB). This is the lead's call, because it is the rows2 deploy dir. With it, free space is about 110 GB, a margin of about 22 GB even with no cleanup during the run.
- (b) Put the check into the cv02 launch command, so that it refuses below 108 GB (command below).
- (c) In request s5 and s9, change "check daily" to "check at every tick; touch Q/HOLD below 20 GB".

**F8.2 Both queues armed by mistake (required, launch-command text only).** E: nothing in the code stops it today. The gaint launch.sh / bench_setup.sh never looks at cv02, and cq_setup.sh never looks at gaint. The two sessions have the same name, bench_q_c3base, on two different machines, so even that does not clash. The request prevents a double arm only in prose: s5 "never arm both", s6 "only with (a) never armed, or HELD before its first start", s9, and the launch.sh header comment. S: an agent restarted without context could arm both, which would waste up to 50 gaint GPU-h beside the udev block and mix two machines in one table. Exact fix: put the cross-machine pre-checks below into request s6 as **the** launch commands. They only read: queue.pid and launch.log on the other machine. If the lead deliberately switches to gaint after HOLDing cv02, the lead runs launch.sh by hand and writes down why.

## Evidence per item

### 1. Merge: PASS
E (item1_merge.out):
- Branch and worktree. bench_final = W HEAD = 89b9ea5a12a37a87c16c4868cc4adf00794a7610. Porcelain is 0. No upstream, 0 remote branches.
- Commits. First-parent commits since c417732: 17a18d0, 6889344, a3cf85a, 89b9ea5. Each message ends with the Opus 5.5 co-author line.
- Reflog. bench_final moved last at 01:24:22. The queue dirs were pinned at 01:51 (cv02) and 01:55 (gaint), so there is no commit after pinning.
- Ancestry. 17a18d0 has parents c417732 and 24aa039. c417732, ae4dd10 and 24aa039 are all ancestors of HEAD. Merge base b5bf0ae.
- Trees. Tree 8465e178 = `git merge-tree --write-tree c417732 24aa039`.
- Diffs. `diff c417732 17a18d0` is byte-equal to `diff b5bf0ae 24aa039`, and `diff 24aa039 17a18d0` is byte-equal to `diff b5bf0ae c417732`. So each side holds only the other side's changes, and no hunk was resolved by hand.
- cv5v3-side modules. I read the M files bench/sets.py, bench/w1read.py and bench/cellmeta.py. They only add cv5v3 (root family, pins, sizes, GROUPS_TSV_V3, and check_groups, which returns at once when no cv5v3 run is in the read). The cv5v2 path is unchanged apart from the one-family assert. All of this was reviewed at c417732 (REVIEW_CV5V3 delta).
- 17a18d0..HEAD:
  - M bench/q/cv02/cq.sh. My own `patch` of the ae4dd10 blob (cb2a4922) with ruling/cq_cv5v3b.patch (330ac850) gives 02d5ba5f = HEAD. I read all 4 hunks: DATA_V3, the BENCH_CV5V3_ROOTS export, a ROOTS_cv5v3 check only when a job names a cv5v3 root, and the set token taken from the root case.
  - A scripts/bench_leak_did.py and 2 tests.
- Unchanged against ae4dd10 (the reviewed udev deploy): bench/methods, bench/methods_cv02, bench/cards.py, bench/dumpfmt.py, src, configs, scripts/train.py, scripts/bench_infer.py, bench/q/bench_lib.sh.
- gaint queue code. md5s equal bench_wt_w2 (c57508e): bench_q 226807e0, bench_lib 1af2ed69, bench_gate 51bcf13c, bench_guard b09b53c0, bench_gpumem a939464d, bench_setup 436c32f2, bench_chain 705df27e.
- Other trees. Protected trees are unchanged: el_bench 31c0c36, bench_wt_w2 c57508e, bench_wt_udev ae4dd10, bench_wt_cv5v3 c417732, bench_wt_a 81b4505, bench_wt_b b5bf0ae, rows1 52e3f14, rows2 b12fca8, each with 0 tracked changes.

### 2. Identity, renders, pytest: PASS
E (run.log, id/, render/, pytest_89b9ea5.log):
- My own archives. 31c0c36 has 619 files and 89b9ea5 has 770. All 769 tracked files of W equal my archive of 89b9ea5 (0 differ).
- Own 5-step CPU identity, PFV11 (house_r34_unetpp_pf_v11, cv5v2_v11_f0, seed 5, 1 thread), identity_cpu.py 962379a6 / compare_id.py 3b83b364, archive 31c0c36 vs archive 89b9ea5: **IDENTICAL (5 steps, all fields except code / sec)**, 12:27:34.
- Renders. I rendered the 648 udev-review tuples (W1 125, W1-LOSO 8, W2A 61 + 90 grid, R1 50 + 50, W1-cv02 at 52e3f14 100 and at b12fca8 100, R2 30 + 30, R2-LOSO 4) at my archive. Joined by key with the udev reviewer's reference renders, made at the trees the cards were reviewed on: **648 of 648 equal**, 0 errors.
  - Note: the run.log line "133 of 648" is a row-order bug in my script's first compare (the two tables have different row orders); the keyed join is the check.
- Card files. 34 of 34 card files are byte-equal to the newest reviewed tree that holds them. bench/cards.py = c57508e. The PF and HOUSE v11 cards (a4a46a52, e8c32f22) equal 31c0c36.
- Full pytest of my archive: **748 passed, 4 skipped, rc 0** (182 s).

### 3. cv5v3 data: PASS
E (item3_roots_gaint.out, cv02_read.out, item3_rdiff.out):
- **Published files and gaint meta.** cv5v3.json 7a700b00 and cv5v3_groups.tsv d880a769. The 4 meta files in gaint bench_data_v3b/meta are cmp-equal to benchmark/splits.
- **gaint pins.** META.md5 ade72e13 -c OK. ROOTS_cv5v3_v11.md5 79e8aee8 -c OK.
- **My own rv_roots.py (stdlib, no bench import) on gaint: 61 PASS, 0 FAIL.** Per fold:
  - train / val / test = JSON lists (order included); held-out md5 = JSON; test = val.
  - No duplicates; train and held-out are disjoint; train + held-out = the 532 pool.
  - 0 forbidden (9bb4d919, 167), sealed (cells.tsv role test / E1, 156) or do-not-train (5a22e8cc, 48) stems, in all stem forms.
  - 0 cv5v3 groups, 0 cv5v2 groups and 0 image ids across train and held-out.
  - 532 mask links (train -> masks_v11/masks, held-out -> masks_strict), 0 wrong, 0 dangling; labeled -> house labeled dir.
  - Held-outs partition the pool, sizes 107 / 110 / 103 / 101 / 111.
- **cv02, read only, 06:55 UTC.**
  - Pins and checks. META.md5 ade72e13 OK; ROOTS c7bc6543 OK; per root SPLITS.md5 and DATA_MANIFEST.md5 -c OK (image and mask contents).
  - Against gaint. The 25 ROOTS lines that are not MASKLINKS are equal to gaint's, so the lists are byte-equal to the ones checked above. Each MASKLINKS.tsv, after the path rewrite, has gaint's md5 (90c65389, 69bf74f8, 04ace6e2, 11a7f821, 4abe4b6f).
  - Links. My own parse of all 5 x 532 links: stems = pool, train -> /tmp/noob_el/bench_data/masks_v11/masks, held-out -> masks_strict, 0 wrong, 0 dangling.
  - Other data. Roots and meta are read-only (dr-x / -r--). Masks MANIFEST OK (77168c5f, 1,596 lines). DEPLOY.md5 d6063fd8 OK.
- **Configs.** My own rv_rdiff.py at my archive renders all 50 c3base tuples on the cv5v3 root and on the cv5v2 root of the same fold. The flattened configs differ **only in data.root (50 of 50)**. PF vs HOUSE differ only in the 4 training.encoder_pf keys. Rendered: 20,000 steps, batch 8, masks_v11, ignore 255, smp_unetpp.

### 4. Queue code: PASS
E (item4_cqrender.out, item8_lanetest.out):
- **Sandbox render.** I ran cq.sh on gaint in my own sandbox: data paths rewritten, stub python for the card calls, the env.sh line neutralised (1 line), stopping by itself at the logger check. Pre-patch (ae4dd10) vs patched (89b9ea5) on the real lists:
  - **rows2 realq 87e0b608: 60 rendered lines IDENTICAL.**
  - **W1-C (bq/w1c, ef258b59, v11 and v1 roots): 90 lines IDENTICAL.**
  - With DATA_V3 absent, the patched script renders W1-C exactly as before.
- **c3base 480b228a on the patched script.**
  - Arming passes up to the logger check; 100 lines.
  - 50 of 50 dump lines carry `--set cv5v3_f<fold of the run's own root>`, `--device cuda --precision fp32` and `--logp`.
  - 50 of 50 train lines carry data.root=DATA_V3/roots/cv5v3_v11_f<own fold>.
  - 0 cv5v2 tokens.
  - The pre-patch script refuses this list (root not DATA/roots/cv5v2_*).
- **Refusals (patched script):**
  - a cv5v3 root under DATA;
  - a fold that does not match the root;
  - a tampered root (SPLITS check);
  - a root changed consistently but no longer matching the pinned ROOTS_cv5v3_v11.md5 ("ROOTS_cv5v3_v11.md5 check FAIL").
- **Lane rule.** test_other_on.sh (715166a0) on the patched cq.sh gives **13 of 13 PASS** (the pre-patch script gives the same). The patch changes no lane line; OTHER_MAX stays 4096.
- **gaint queue code** = the reviewed c57508e blobs (item 1). `diff c57508e HEAD -- bench/q` adds only the 6 cv02 files. bench_setup.sh lines 15 to 27 = the c57508e blob.

### 5. Jobs: PASS
E (item5_jobs.out: rv_jobs.py, own code, RESULT PASS, 19 checks; cv02_read.out; item8_armcheck.out):
- **Pins.** cv02 jobs.txt **480b228a936bd025b9e53f799eb90f78**, 50 lines, r--r--r--, LPG 1, MAXC 8. gaint jobs **dbd3632a6c3a109b6fff831f9aa47db9**, MAXC 2. gaint dump **9c7848ab2a91df58670a514a6158de62**, dump/MAXC 1. launch.sh **a172bf7091224c62bb6737396b3d4a6f** (SES bench_q_c3base, DEPLOY 89b9ea5a..., REPO bench_wt_final, MAXH 120).
- **cv02 job fields.**
  - Names and cards: c3_pf_v11_f<k>_s<s> -> house_r34_unetpp_pf_v11, c3_house_v11_f<k>_s<s> -> house_r34_unetpp_v11.
  - Order: seed-major (s5: PF f0-4, then HOUSE f0-4; then s6 to s9). The name's seed and fold match the fields.
  - Root: /tmp/noob_el/bench_data_v3b/roots/cv5v3_v11_f<k>.
  - Gates: training gate 9000 (= card floor; measured cv02 peak 5,740 + 2,048 = 7,788), dump gate 5262 (3,214 + 2,048), logp 1, no extra.
- **gaint.** Same names, cards, seeds and order; roots bench_data_v3b. Each dump line is `bench_infer --run bench_wt_final/experiments/<name> --set cv5v3_f<k> --dumps /home/noob/work/bench_c3base/dumps ... --device cuda --precision fp32 ... --logp --bench-run dump_<name>`, gate 6200.
- **Dump safety.** No sealed or other-split token in any line. bench_infer's default --forbidden is b6_forbidden.txt (md5 pinned in the script), and TF32 is off for fp32 (l.138-139).
- **No existing outputs.** 0 existing experiments/<name>, .stdout or runs/<name> for the 50 names, in bench_89b9ea5, bench_a3cf85a, bench_b12fca8 and bench_wt_final. bench_89b9ea5/experiments holds only the 53 tracked history dirs of the archive. /home/noob/work/bench_c3base and bench_relay/c3base do not exist.
- **Nothing armed.**
  - cv02: Q holds only jobs.txt, LPG and MAXC; no bench_q_c3base session (only bench_q_rows2).
  - gaint: Q holds jobs.txt, MAXC, launch.sh, prep.log and dump/; 0 c3base sessions; read-only replica rv_armcheck.sh (d04104d7): **ARMCHECK PASS**.
- **Deploy equals the pinned commit.** W = 89b9ea5 and clean. cv02 /tmp/noob_el/bench_89b9ea5: REVISION 89b9ea5a..., CODE.md5 **7cde26e41a98e095b475e8bf1a3759a3**, -c OK. My own archive passes cv02's CODE.md5 (769 of 769 files). The relay stage copy bench_c3_io/stage/bench_89b9ea5 also has CODE.md5 OK, 7cde26e4, and relay_w1c.sh 74a2ec3d = W.
- S (harmless): 3 orphan .pyc under bench_89b9ea5 come from the integrator's read-only python checks there. They are not in CODE.md5 and Python never imports a pyc without its source.

### 6. Smokes and dump path: PASS
E (cv02_read.out; item6_read.out; bench_c3_io/fix/run.log, read with grep and cut only):
- **50-step smoke c3base_smoke** (deploy a3cf85a, LPG 1, MAXC 2).
  - Start: GPU 5 qualified at 19:54:05 UTC; pid 713421 is in both the pid file and launch.log; cmdline `python -u scripts/train.py --exit_after_step 50 ...`.
  - Checks: `config OK (= card)`; `startup line OK: Labelled: 425 (/tmp/noob_el/bench_data_v3b/roots/cv5v3_v11_f0/splits/train.txt)  unlabelled: 0 (-)  val: 107  test: 107` (= my fold-0 list counts).
  - End: rc 3 by design; peak 5,736 MiB; session ended.
- **cv02 dump dry test c3base_smoke2** (fixture dumptest_c3_pf_v11_f0).
  - Start: GPU 5 qualified at 06:45:21 UTC; pid 439694 is in the pid file and launch.log; cmdline `python -u scripts/bench_infer.py ... --set cv5v3_f0 ...`.
  - Checks: `startup line OK: BENCH_START: run=dump_dumptest_c3_pf_v11_f0`; dumped rc 0, 0 Traceback; RUN.md5 111 files 9c6d19c7.
  - End: ALL DONE; dump peak 3,212 MiB; session ended; neither PID alive.
  - S: the smoke deploy differs from the queue deploy only in REVISION and scripts/bench_leak_did.py (E: CODE.md5 diff), so these proofs hold for every file the queue runs.
- **gaint CPU fixture.** fx300 rc 0, Traceback 0, nan 0, step 300, Labelled 425 / 107 / 107; bench_infer --set cv5v3_f0 --logp: 107 cells, ties 0.
- **My own read-guard run** (bench_read_w1 at my archive on that dump, runs.tsv 8ab7d30d, --pseudo-folds 5 --dry --boot 200):
  - `--groups cv5v3_groups.tsv`: **rc 0**, 0 Traceback, 0 guard lines; read.json groups_md5 **d880a769**.
  - `--groups cv5v2_groups.tsv`: **refused** (rc 1, 2 guard lines, nothing written).
  - no --groups: **refused** (rc 1, 2 guard lines, nothing written).
  - Only structure fields were read.
- **Outputs removed.** On cv02, 0 c3 / smoke / dumptest entries in either deploy's experiments; 0 files under runs/ and dumps/ of bench_89b9ea5 and bench_a3cf85a.

### 7. Leakage rule: PASS
E:
- **Written before any run.** bench_leak_did.py was committed at a3cf85a (16 Nov 01:17:37) and tightened at 89b9ea5 (01:24:22). Request s7 is fixed text. No cv5v3 run exists on either machine (item 5). I read the whole tool:
  - Statistic. Per common seed, DiD = [v3 - v2](X) - [v3 - v2](clean_unmoved), for strict crack IoU and relF1@2, pooled at argmax.
  - Interval. Two-stage bootstrap over the 285 cv5v3 groups (the same draw for both splits) and the common seeds, B 2,000, percentile.
  - Reading. Fixed 3-way sentence.
  - Refusals. Refuses a non-cv5v3 v3 side, a non-cv5v2 v2 side, a groups file that is not the cv5v3 partition, mixed device or precision, and any read that does not cover all 532 cells unless partial.
- **Strata.** results/stageC/cv5v3/cv5v3_compare_cells.tsv md5 **4d38187847a99128b98113b8f7626f8f** = the pin (file of 00:42, before the tool). The reviewed counts are 416 / 69 / 47.
- **Computable.** W1-C relayed dumps exist on gaint: bench_reads/w1c/links/elbench1 holds PF v11 w1c1 f0-4 x s5-9 (25) and HOUSE v11 w1c2 f0-4 x s5, s6 (10). The relay layout bench_relay/<q>/<name>/dumps/elbench1/<method>/<name> matches the s7 link loop.
  - Own dry run of the tool (fixture cv5v3 dump as v3 seed 5 vs w1c1_pf_v11_f0_s5, --dry --allow-partial, B 50): rc 0, both targets x both metrics. The same without --dry is refused: "mixed device ... ['NVIDIA RTX A6000', 'cpu']". So the one-machine guard works, and cv02 c3 dumps (A6000, fp32) pair with W1-C.
  - S: an affected_moved stratum is empty in a single-fold dry run by construction; the full read covers all 532 cells.
- **Seed mismatch (stated in the request, correct).**
  - PF: c3 s5-9 vs W1-C1 s5-9 = 5 pairs.
  - HOUSE: c3 s5-9 vs W1-C2 s5, s6 = **2 pairs only** (the request's command restricts v3 to s[56]; the tool uses common seeds anyway).
  - Under the gaint fallback: PF vs W1-G s5-8 = 4 pairs (E: w1g_pf_v11_f0-4_s5-8 exist), and no HOUSE DiD.
  - S: the HOUSE interval can show only a large effect; adding HOUSE cv5v2 s7-9 is the lead's call.

### 8. Safety: FAIL (F8.1, F8.2 above); the rest holds
E (item8_safety.out, item8_lanetest.out, item8_armcheck.out, cv02_read.out, cv02_du.out):
- **cv02 lanes.** Lane rule unchanged, 13 of 13 PASS; Q/LPG = 1 and MAXC = 8. cq_setup.sh refuses unless LPG is 1 or 2 and no pid file, HOLD or launch.log exists. The rows2 runs count as another user for the c3base queue, so the two queues never share a GPU (OTHER_MAX 4096; rows2 holds about 6 GB per GPU on GPUs 0 and 5).
- **Relay.** relay_w1c.sh uses `ssh -n -a -o ForwardAgent=no -o BatchMode=yes` and only read-only commands on cv02. It refuses to overwrite and runs md5 checks on both ends. The relay command checks the stage CODE.md5 and relay md5 74a2ec3d, uses tmux has-session with exact match, and refuses if bench_relay/c3base exists.
- **Pattern kills.** 0 in bench/q and bench/q/cv02. The repo's only hits are 2 `pgrep` (no kill) in the legacy scripts/resume_queues.sh, which no queue uses. 0 in the harness/c3base scripts (1 grep string). The stop commands in s6 are HOLD files and a stop by PID after `ps`.
- **gaint.** PROTECT 6206 (finllm alive, root, 16 d). Outside rule OUTSIDE_MIB 1,024 before every start. Guard THR 2,048 MiB, MAXSTOPS 2. MAXC 2, dump MAXC 1, MAXH 120 in launch.sh. deploy_ok (HEAD = DEPLOY, no tracked change) is re-checked before every start. gpu_gate has no HOLD.
- **Disk:** see F8.1. E: cv02 / has 86 GB free. /tmp/noob_el holds 306 GB in total; the rows2 deploy holds 24 GB of dumps already relayed (25 of 25 .ok on gaint).
- **Both queues:** see F8.2.

## Launch commands checked (use these after F8.1)
1. Disk and cross-check, then arm cv02 (G):
`test ! -e /home/noob/work/bq/c3base/queue.pid && test ! -s /home/noob/work/bq/c3base/launch.log && ! tmux has-session -t "=bench_q_c3base" 2>/dev/null && ssh -n -a -o BatchMode=yes cv02@10.8.1.106 'a=$(df --output=avail -BG /tmp | tail -1 | tr -dc 0-9); [ "$a" -ge 108 ] || { echo "REFUSED: cv02 /tmp free ${a} GB < 108"; exit 1; }; B=/tmp/noob_el/bench_89b9ea5 Q=/tmp/noob_el/bench_q/c3base SES=bench_q_c3base DEPLOY=89b9ea5a12a37a87c16c4868cc4adf00794a7610 JOBS_MD5=480b228a936bd025b9e53f799eb90f78 DATA_MD5=d6063fd83d20e656612540edda702cbe bash /tmp/noob_el/bench_89b9ea5/bench/q/cv02/cq_setup.sh'`
   - All values checked: B, Q and SES; DEPLOY = REVISION; JOBS_MD5 = jobs.txt; DATA_MD5 = md5 of cv02 DEPLOY.md5 (d6063fd8...); cq_setup.sh is in CODE.md5.
   - Expected output as request s6: `armed: gpumem <pid> queue <pid>`, the `cv02 q armed: 50 jobs (md5 480b228a...) ... LPG 1, MAXC 8 ... cq 02d5ba5f` line, then at the first start `config OK (= card)` and `startup line OK: Labelled: 425 (.../cv5v3_v11_f0/splits/train.txt)  unlabelled: 0 (-)  val: 107  test: 107`.
2. Relay (G), unchanged from s6: `cd /home/noob/work/bench_c3_io/stage/bench_89b9ea5 && md5sum -c --quiet CODE.md5 && echo OK && md5sum bench/q/cv02/relay_w1c.sh` (OK, 74a2ec3d48ad3cd989aa0c9b5ae69942), then the s6 `tmux has-session ... bench_relay_c3base ... relay_w1c.sh` line (B, Q, RD=/home/noob/work/bench_relay/c3base, N=50, NAMES_RX=^c3_, POLL=300). Keep bench_c3_io until the relay ends.
3. gaint fallback (G), only if cv02 was never armed:
`ssh -n -a -o BatchMode=yes cv02@10.8.1.106 'test ! -e /tmp/noob_el/bench_q/c3base/queue.pid && test ! -s /tmp/noob_el/bench_q/c3base/launch.log && ! tmux has-session -t "=bench_q_c3base" 2>/dev/null && echo CV02_C3BASE_NEVER_ARMED' | grep -qx CV02_C3BASE_NEVER_ARMED && bash /home/noob/work/bq/c3base/launch.sh`
   - launch.sh a172bf70; ARMCHECK PASS today. First-job check as s6.
   - A switch after a cv02 HOLD is a deliberate manual step, not this command.
4. Stop: as request s6 (HOLD files; one PID only, after `ps -o pid,user,args -p <pid>`; relay STOP file).

## Notes (S, none blocks beyond F8)
- Keep the s0 / s9 rule: no commit, checkout or switch in /home/noob/work/bench_wt_final until both queue dirs are retired (bench_q.sh re-checks HEAD before every start and HOLDs on mismatch). The gaint fallback writes experiments into W (untracked, as in bench_wt_w2).
- During the run, delete each cv02 dump dir once its relay `.ok` exists (net 0.6 GB per run stays: experiments with latest.pth).
- The DiD read needs every fold of a seed on both sides (no --allow-partial in a real read). A cv02 queue HELD part-way leaves that seed out of the DiD.
- gaint MAXH 120 h covers the planned 45 h plus dumps. If the fallback waits days for the GPU, the logger and guard end at 120 h and the queue holds (fails safe).
- The smoke deploy /tmp/noob_el/bench_a3cf85a and the scratch dir /tmp/noob_el/bench_c3_render may be removed after launch (36 MB). Smoke queue dirs c3base_smoke{,2} hold only logs.
