# Launch request final: D4 TTA dumps of the cv5v3 c3x and PF runs + full-pool training of the candidate and PF, one cv02 queue `fin` (final_builder, 21 Nov 2026)

Status: built and tested on gaint CPU (plus two CPU-only smokes on cv02 in a scratch dir of ours, since removed). **Nothing
launched, no GPU used, no queue placed or armed, no deploy made, no commit pushed; commit F made locally only.** User's request
(19 Nov): "go for the two things on cv02: the registered HRNet + SWAD + TTA final model and the public scores on cv02, nothing
to be kept idle". This request covers the trained artefacts of the final model and the CV5 TTA reads. The user's decisions
of 20/21 Nov (relayed by the lead) are built in: relF1@2 decides, strict IoU only with its convention band; the E1 opening
(candidates C1 full-pool PF, C2 full-pool HRNet + SWAD (swad) + D4, C3 the 5-seed ensemble of C2) and test50 opening #19 are
approved and built by opening_builder; their sealed-set dump lines stay OUT of this queue (plug-in point: section 11). E = measured by a command of this build, S = judgement, D = decision with its record.
Notation: T = /home/yugma/mtp/research/team_2026-11-12_frontier, H = T/harness/final (md5 in section 12), F = commit
821dfadf49116cc6d5fdbd6697e263dd7cf0f834 (tree 114d5469340e7bfd496f290c18dccb7d4f13bdd3) in /home/noob/work/bench_wt_fin,
FB = cv02 /tmp/noob_el/bench_821dfad (its deploy, made by step 2), Q = cv02 /tmp/noob_el/bench_q/fin, IO = gaint
/home/noob/work/bench_fin_io. cv02 was reached only as `ssh -n -a -o BatchMode=yes cv02@10.8.1.106` from gaint.
**Fix round 1** (T/harness/REVIEW_FINAL.md 9ac03c77, verdict FIX; lead's message of 21 Nov): B2 = this text (lane configuration
(a1) in sections 0, 3, 4 (steps 7, 8, 8b, tick checks), 6, 9; disk lines); B3 = selection-bias and convention-band labels in
final_verdict.py; N1 = run_read_final.sh refuses a D4 dump whose checkpoint_md5 differs from its plain dump's. B1 (cv02 free
space) is the lead's. FINAL_RULE.md (82867156), commit F and the job list are unchanged.

## 0. What runs (one queue, 85 jobs, no sealed set, logp 0)
| Kind | Jobs | What | Where it writes |
|---|---|---|---|
| full-pool training | 10 | `fin_hrnet_swad_v11_pool_s5..9` (card hrnet_w18_unetpp_swad_const_pf_v11, slim keeps swad_bn + swad) and `fin_pf_v11_pool_s5..9` (card house_r34_unetpp_pf_v11) on root `pool532_v11` (all 532 pool cells; no dump: no held-out cell) | FB/experiments, FB/runs |
| dump-only, D4 | 25 | CS_D4: `c3x_hrnet_swad_v11_f<k>_s<s>.swad.tta_d4` = the 25 c3x checkpoints of bench_03375d4, readout swad, `--tta d4`, own held-out fold | FB/dumps, FB/runs |
| dump-only, D4 | 25 | PF_D4: `c3_pf_v11_f<k>_s<s>.tta_d4` = the 25 c3_pf_v11 checkpoints of bench_89b9ea5, readout model | FB/dumps, FB/runs |
| dump-only, D4 | 25 | CB_D4: `c3x_hrnet_swad_v11_f<k>_s<s>.swad_bn.tta_d4` (readout swad_bn; descriptive; cheap, so included) | FB/dumps, FB/runs |
GPU (S): about 22 GPU-h; wall about 3.5 to 5 h on cv02 if GPUs are free (section 6). Lane configuration (a1): MAXC 8, LPG 1,
SHARE_TRAIN 20480, SHARE_DUMP removed right after arming (step 8b), GAPSEC 30: one process of ours per GPU at all times.
Disk (S): cv02 peak +18 GB before removals (guard floor 20 GB; arm only if cv02 df /tmp shows >= 39 GB right before `arm`; never DISK_OK near the 20 GB floor (the lead frees space by moving old dirs of ours to the NAS, see log.md)), gaint +12 GB relayed (section 5).

## 1. Commit F and the three test failures of 491e460 (E)
- F = 491e460 (previous builder: cv02 queue job kinds, pool-root builder) + one commit 821dfad that changes two tests only
  (no code). On top of: e25728e (ttafix) on 03375d4 (c3x).
- `test_bench_cards_cv02.py::test_variants_exist`: fails already at 03375d4 and at e25728e (scratch archives of each, same
  error: the cv02 variant set gained `swad_const_pf_v11` in 5437778 and `hrnet_w18_unetpp_swad_const_pf_v11` in 03375d4
  without the test's set). Not environment, not caused by 491e460: a stale expectation. Fixed: the set `C3` of those two names.
  Evidence: H/evidence/pytest_2files_03375d4.log and H/evidence/pytest_2files_e25728e.log (1 failed, 22 passed at each).
- `test_bench_cq_cv5v3.py::test_cv5v3_root_must_be_v11_of_the_jobs_fold` (2 cases): pass at 03375d4 and e25728e; fail at
  491e460 because cq.sh's refusal text was widened ("... or DATA_F/roots/pool532_v11; not starting"). Same refusal (rc 1,
  nothing rendered), new words. Fixed: the test expects the new text.
- **Full pytest at F: 808 passed, 5 skipped, 0 failed** (H/evidence/pytest_full_821dfad.log, 164 s, CPU, nice 19).

## 2. Code proof (`H/final_codeproof.sh`; E: H/evidence/codeproof/)
`bash H/final_codeproof.sh 821dfadf49116cc6d5fdbd6697e263dd7cf0f834` with CV02=1 (script e7c299e5; run 21 Nov 00:38 to
01:27 IST on gaint CPU, nice 19, 6 threads; output H/evidence/codeproof/codeproof_821dfad.out): **0 FAIL.**
| # | Item | Result (E) |
|---|---|---|
| 1 | `git diff --name-status 03375d4 F` | exactly the 10 paths: bench/q/cv02/cq.sh, cq_setup.sh, bench/tta.py, scripts/bench_infer.py, scripts/bench_make_pool_root.py (new), 5 tests; nothing under src/ configs/ data/; train.py, bench/methods*, cards.py, dumpfmt.py, sets.py, bench_lib.sh, slim_ckpt.py, cvcard.py, cq_gpumem.sh, cq_rescue.sh byte-equal |
| 1 | training code path | runtime trace of train.py: the same 39 repo modules at both commits, all 39 byte-equal; none is bench.tta, bench_infer or the root builder (train_modules.txt). Training of the existing cards is byte-identical in code |
| 1 | TTA lineage | 03375d4's bench/tta.py and bench_infer.py = ae4dd10's (the gaint udev_tta deploy that made B5's dumps, pre-ttafix); F's = 2933146's (the reviewed ttafix) |
| 1 | queue | old-style lines render byte-equal to 03375d4's cq.sh (sandbox test in the archive of F) |
| 2 | deploy | CODE.md5 of an archive of F built as c3_deploy.sh does: 780 lines, md5 6667cb18c7d216a72de474b04e943164; against cv02 bench_03375d4's CODE.md5 (read by ssh; = its stage copy, REVISION 03375d4) only the 10 paths (+ REVISION) differ |
| 3i | `--tta none`, real cells, old (03375d4 archive) vs F | c3_pf_v11_f0_s5 key model on cv5v3_f0: 107 of 107 npz byte-identical (140,388,811 bytes); c3x_hrnet_swad_v11_f0_s5 key swad_bn: 107 of 107 byte-identical (139,355,971 bytes). Manifests differ only in code_repo, writer, written |
| 3ii | `--tta d4`, old (= gaint TTA code) vs F | PF key model and c3x key swad: oth, m_crack, p_crack, p_inact bit-equal in 107 of 107 cells; pred differs at 0 px (the ttafix kind would be argmax p != argmax log p: 0 here); npz byte-identical 107 of 107 for both |
| 3iii | readouts under `--tta d4` at F | c3x key swad_bn: rc 0, 107 cells, manifest tta = {mode d4, scales [1.0], d4 True, views 8}, step 20000; key swad and PF key model: rc 0 (3ii) |
Inputs of item 3: scratch run dirs = the relayed config_used.yaml with data.root moved to gaint's cv5v3 root (1 line) and
the relayed slim.pth (step 20000) as latest.pth; gaint's train.txt md5 = the cv02 dump's split_md5 (d7069b34);
ROOTS_cv5v3_v11.md5 checks on gaint (only MASKLINKS.tsv differs from cv02: absolute link targets). CPU wall per dump
(6 threads): plain 57 s (PF) and 84 s (c3x); D4 386 s (PF) and 627 s (c3x); D4 dumps without logp are 131 MiB (PF, E).
Negative tests (a scratch commit with another log epsilon in tta.py cell_maps and bench_infer.py maps, plus one comment
line in src/models/model_factory.py): DUMPS=0: 5 FAIL (path list, src change, F's code against the ttafix, train.py trace,
CODE.md5; negative_paths.out); FAST=1: 7 FAIL (the same 5, plus (3i) 0 of 107 npz identical and (3ii) m_crack bit-equal in
0 of 107 cells; negative_fast.out). Scratch dumps and clones deleted; only evidence kept.

## 3. Job list, root and smokes
- `H/final_make_jobs.py` -> 85 lines (md5 cc4d7006ab0c4e23bba896474c0f7169, H/jobs/jobs_fin.txt); its own asserts: 85 distinct
  names, 10 full-pool + 75 dump-only, exact fields per kind, no sealed token, order below. Lines (cq.sh format of F):
  - `fin_hrnet_swad_v11_pool_s5|bench/methods/hrnet_w18_unetpp_swad_const_pf_v11.yaml|5|/tmp/noob_el/bench_data_fin/roots/pool532_v11|0|11510|6200|0||swad`
  - `fin_pf_v11_pool_s5|bench/methods/house_r34_unetpp_pf_v11.yaml|5|/tmp/noob_el/bench_data_fin/roots/pool532_v11|0|9000|5262|0|`
  - `c3x_hrnet_swad_v11_f0_s5.swad.tta_d4|bench/methods/hrnet_w18_unetpp_swad_const_pf_v11.yaml|5|/tmp/noob_el/bench_data_v3b/roots/cv5v3_v11_f0|0|11510|6200|0|--dumpof /tmp/noob_el/bench_03375d4/experiments/c3x_hrnet_swad_v11_f0_s5 --key swad --tta d4`
  - `c3_pf_v11_f0_s5.tta_d4|bench/methods/house_r34_unetpp_pf_v11.yaml|5|/tmp/noob_el/bench_data_v3b/roots/cv5v3_v11_f0|0|9000|6200|0|--dumpof /tmp/noob_el/bench_89b9ea5/experiments/c3_pf_v11_f0_s5 --key model --tta d4`
- **Order** (S, lead's choice, section 9 Q4): the 8 long trainings first (candidate s5 to s9, PF s5 to s7), then the 75 dump-only
  jobs (CS_D4, PF_D4, CB_D4; seed, then fold), then PF s8, s9. With LPG 1 the 8 trainings take the 8 GPUs. Lane configuration
  (a1) (lead's ruling of 21 Nov; approved in REVIEW_FINAL.md "Lane configuration": in a sandbox run of F's real cq.sh at most 1
  process of ours per GPU and 0 SHARED lines): MAXC 8 and Q/SHARE_DUMP absent (removed right after arming, step 8b), so the
  dump-only jobs take only strict lanes (a GPU with no lane of ours; the dump runs on that same GPU) and start as the PF
  trainings end; one process of ours per GPU at all times. PF s8, s9 start when the dumps are dispatched, on a GPU with no lane
  of ours. Trainings keep SHARE_TRAIN 20480 (a shared training start is never beside our own login).
- **Gates** (E, cv02 gpumem logs of c3x / c3base): candidate training 11510 (the c3x job gate; cv02 peak of the 25 c3x runs
  9,386 MiB), PF 9000 (card gate; cv02 peak 5,740). Dump gate of every D4 line 6200: cv02 plain-dump peaks 3,944 (c3x) and
  3,212 MiB (PF); D4 adds the accumulator, p, the view logits and the inverse view, 4 x (8, 24, 512, 512) float32, about 0.8 GB
  (S; review N2): c3x about 4.7 GB < 6200; under (a1) every dump runs in a strict lane (>= 9,000 / 11,510 MiB free) anyway. cq.sh refuses a job gate below the card's.
- **Source runs** (E, cv02, read only): all 50 dirs complete (config_used.yaml + checkpoints/latest.pth): 25 c3x in
  bench_03375d4 (REVISION 03375d4), 25 c3_pf_v11 in bench_89b9ea5 (REVISION 89b9ea5). cq.sh's dump-only kind cfgchecks each
  run's config_used.yaml against card, seed, run name and root at arming. The dump manifests carry train_code_revision =
  the source deploy's REVISION and writer = F's bench_infer.py (32e0b67c).
- **Full-pool root** `pool532_v11` (F's scripts/bench_make_pool_root.py): train = the 532 pool cells (md5 d374fd84 = the
  cv5v3.json pool), val = test = cv5v3 fold-0 held-out list (79816ba6; training cells here: an in-sample monitor whose numbers
  are never read), masks = v1.1 train masks; asserts no stem of forbidden_v1.txt (167 = legacy test 50 + ext117 incl. E1 106)
  in any list. E: built on gaint and on cv02 from each machine's pinned inputs: same train.txt, test.txt, SPLITS.md5 cec1396e
  and DATA_MANIFEST.md5 33e65b3f (the same 532 image and mask bytes); --check OK (H/evidence/render_smoke/pool_root_cv02.out).
  cv02 holds only the 532 pool images (bench_data/labeled: 532 files), so no sealed image is even present there.
- **Smoke 1, full-pool training path** (`H/final_poolsmoke.sh`, gaint CPU, E: H/evidence/poolsmoke/): archive of F, the root
  built in scratch, F's train.py started exactly as cq.sh renders a full-pool line plus `--exit_after_step 1`: both cards
  rc 3 (by design) in 25 / 39 s, first `Labelled:` line = cq.sh's want_line (`Labelled: 532 (...)  unlabelled: 0 (-)  val: 107
  test: 107`), cfgcheck `config OK (= card)`, 0 Traceback lines; the candidate's averagers built as carded (WAVG line).
- **Smoke 2, render on cv02** (`H/final_render_smoke.sh`, E: H/evidence/render_smoke/): an archive of F staged as c3_deploy.sh
  does (CODE.md5 md5 6667cb18, the value c3_deploy.sh must print for F) into a NEW scratch dir of ours
  /tmp/noob_el/bench_finsmoke_11210041, the pool root built there by the real builder, F's real cq.sh run render-only on the
  85 lines (root path mapped to the scratch root; real DATA, DATA_V3, source runs, cards, cv02 card variants and weights md5):
  it passed every arming check of all 85 lines (incl. the 50 cfgchecks of the source configs) and stopped at the logger check
  (`gpumem logger (cq_gpumem.sh) not running; not starting`, 70 s); `final_rendercmp.py`: **0 FAIL** (85 lines = 10 training
  + 75 dump; every line equal to the template built from the list; semantics: no --logp, no --opening, no sealed name, each
  dump's --set = cv5v3_f<its fold>, --run = its --dumpof dir, --run-id = its name, --tta d4, the job's key; no dump for a
  full-pool job). The scratch dir was removed afterwards (`removed /tmp/noob_el/bench_finsmoke_11210041`). A first attempt
  (my wrong variable on the command line) stopped at its own "root mapping" check after creating /tmp/noob_el/bench_finsmoke_11210040;
  that dir was removed too (E: ssh ls + rm of that one path); nothing else on cv02 was written.

## 4. Launch steps (all on gaint, by the lead, after the review PASS; write T and H out in full)
| # | Command | Stop path |
|---|---|---|
| 1 | Review of this request, FINAL_RULE.md, the H scripts, commit F (`git -C /home/noob/work/bench_wt_fin show 821dfad`; `git diff 03375d4 821dfad`). Pin FINAL_RULE.md's md5 (section 12) in the review. | |
| 2 | `bash T/harness/c3base/c3_deploy.sh 821dfadf49116cc6d5fdbd6697e263dd7cf0f834` : stage /home/noob/work/bench_c3_io/stage/bench_821dfad and FB. Must print `CODE.md5 6667cb18c7d216a72de474b04e943164 (780 lines)` and `CV02_CODE_OK 821dfad...`. | Refuses if either dir exists; an unused deploy dir is harmless. |
| 3 | `CV02=1 SCR=<new scratch dir> bash H/final_codeproof.sh` (0 FAIL; about 43 min of CPU for the real-cell dumps; `FAST=1` = the PF run only, about 16 min; `DUMPS=0` skips item 3 if the lead accepts the builder's run in H/evidence/codeproof/). | read only |
| 4 | `IO=/home/noob/work/bench_fin_io bash H/final_queue.sh build` (85 lines, md5 cc4d7006; no name in use on cv02 or in a gaint relay; 50 source runs complete). | gaint only |
| 5 | `F=821dfadf49116cc6d5fdbd6697e263dd7cf0f834 FB=/tmp/noob_el/bench_821dfad bash H/final_queue.sh root` (cv02: builds /tmp/noob_el/bench_data_fin/roots/pool532_v11; pins train.txt d374fd84, test.txt 79816ba6, SPLITS.md5 cec1396e, DATA_MANIFEST.md5 33e65b3f). `DRY=1` first prints the command. | refuses if the dir exists; a built root is inert |
| 6 | `F=... FB=... bash H/final_queue.sh render` (render-only cq.sh of FB in a scratch dir /tmp/noob_el/bench_fin_render/<stamp>; `final_rendercmp.py` must print `render compare: 0 FAIL`). | nothing starts; the scratch dir may be removed after |
| 7 | `MAXC=8 IO=/home/noob/work/bench_fin_io bash H/final_queue.sh place` (Q: jobs.txt read-only, LPG 1, MAXC 8, SHARE_TRAIN 20480, SHARE_DUMP 10240 until step 8b) ; `bash H/final_queue.sh guard` (disk guard 5, tmux bench_diskguard5, HOLD in fin below 20 GB free). | Before `arm` nothing runs. Guard: `touch /tmp/noob_el/bench_q/DISKGUARD5_STOP`. |
| 8 | `DRY=1 MAXC=8 F=... FB=... GAPSEC=30 bash H/final_queue.sh arm`, then the same without DRY (MAXC=8 to both `place` and `arm`: `arm` compares Q/MAXC with it). Pre-checks: render passed; qscan: no other live queue can start training (E now: c3all, c3all2, c3base, c3hrnet alive with MAXC 0, all others ended); Q placed and unused; data md5; FB check (REVISION, CODE.md5, 14 pins, diff to bench_03375d4 = the 10 paths); root pins; 50 source runs; guard 5 running; no HOLD in fin; free >= 39 GB: arm only if cv02 df /tmp shows >= 39 GB right before `arm`; never DISK_OK near the 20 GB floor (the lead frees space by moving old dirs of ours to the NAS, see log.md). Reports armed only with the `cv02 q armed:` line naming SHARE_TRAIN 20480 / SHARE_DUMP 10240 (its value at arming; step 8b removes it) and gap 30 s. Then step 8b at once. Owed at the first start: `fin_hrnet_swad_v11_pool_s5 config OK (= card)` and `startup line OK: Labelled: 532 (...)  unlabelled: 0 (-)  val: 107  test: 107`; at the first dump-only job: `dump-only c3x_hrnet_swad_v11_f0_s5.swad.tta_d4 on GPU g`, `dumped dump_c3x_hrnet_swad_v11_f0_s5.swad.tta_d4 rc=0`, `RUN.md5 ... (dump-only)`. | `ssh -n -a -o BatchMode=yes cv02@10.8.1.106 'touch /tmp/noob_el/bench_q/fin/HOLD'` (no new training or dump start; running ones go on). Training sharing off: `rm` of Q/SHARE_TRAIN (SHARE_DUMP is already gone after 8b). A running job by hand: compare `ps -o args= -p $(cat Q/pids/<job>.pid)` with `Q/pids/<job>.cmdline`, then `kill` that PID only. **A refused arm** (`; not starting`): end the logger by `touch Q/GPUMEM_STOP` or by its recorded PID (`p=$(cat Q/gpumem.pid); ps -o args= -p $p` must show cq_gpumem.sh, then `kill $p`); move the used dir aside `mv Q /tmp/noob_el/bench_q/fin_refused_$(date +%H%M)`; `place` and `arm` again. |
| 8b | Immediately after `arm` returns, whatever its rc, and only if cq.sh armed: the SHARE_DUMP removal command below (reviewer's amendment 1). Record its `SHARE_DUMP off` line in IO/queue.log (the `cv02 q armed:` line still says SHARE_DUMP 10240). Equivalent to removal before arming: the list starts with 8 trainings, and with MAXC 8 no dump-only job can start before all 8 have started (at least 7 x 30 s plus 8 live checks) and one of them has ended; cq.sh reads SHARE_DUMP live before every start. | If `SHARE_DUMP off` is not printed within about 3 min of the armed line: `ssh -n -a -o BatchMode=yes cv02@10.8.1.106 'touch /tmp/noob_el/bench_q/fin/HOLD'`. A refused arm (no `cv02 q armed:` line) leaves SHARE_DUMP in place, so the dir stays re-armable as in step 8. |
| 9 | `FB=/tmp/noob_el/bench_821dfad bash H/final_relay.sh` (relay_w1c.sh 74a2ec3d unchanged; N 85; session bench_relay_fin; gaint free >= 25 GB, else `RD=/mnt/nas/noob_el_archive/bench_relay/fin` and later `RELAY_FIN=` that dir for the read) ; `tmux new-session -d -s bench_relayguard_fin "bash H/final_relayguard.sh"`. | `touch /home/noob/work/bench_relay/fin/STOP` ; `touch /home/noob/work/bench_c3_io/RELAYGUARD_FIN_STOP`. Restart: `RESUME=1 FB=... bash H/final_relay.sh`. |
| 10 | Ticks: `F=... FB=... bash H/final_queue.sh status`, plus the two tick checks below (reviewer's amendment 2; `status` does not show SHARE_DUMP, review N8). cv02 removal of relayed D4 dumps (reviewed tool, unchanged; it keeps runs/ and every checkpoint): `RD=/home/noob/work/bench_relay/fin B=/tmp/noob_el/bench_821dfad NAMES_RX='\.tta_d4$' CUDA_VISIBLE_DEVICES= nice -n 19 ionice -c3 bash T/harness/c3base/c3_f81_list.sh <out>` then `ssh -a -o BatchMode=yes cv02@10.8.1.106 "bash -s" < <out>`. | as 8 |
| 11 | When all 75 dump-only units are relayed (`ls /home/noob/work/bench_relay/fin/.ok | grep -c 'tta_d4$'` = 75): `bash H/run_read_final.sh` in tmux, ONCE (about 16 CPU-min, nice 19, 8 workers). Output /home/noob/work/bench_reads/final_tta (read/, class_guard.txt, verdict.txt, MD5.txt). | refuses and writes nothing until every input checks |
| 12 | Full-pool runs: relayed as slim.pth + config + LATEST.md5 (+ enc_probe.jsonl); latest.pth stays on cv02 for the opening. Nothing is read from them (never print or tail their .stdout or train.log; their end-of-run numbers are in-sample). | |

Commands of the reviewer's two amendments (verbatim; outside the table so that no pipe sign is lost):
- Step 8b, immediately after `arm` returns, whatever its rc, only if cq.sh armed:
  `ssh -n -a -o BatchMode=yes cv02@10.8.1.106 'Q=/tmp/noob_el/bench_q/fin; grep -q "cv02 q armed:" $Q/launch.log && rm $Q/SHARE_DUMP && test ! -e $Q/SHARE_DUMP && echo SHARE_DUMP off'`;
  if "SHARE_DUMP off" is not printed within about 3 min of the armed line, touch Q/HOLD.
- Each tick: `grep -c 'SHARED lane\|SHARED dump' Q/launch.log` = 0 and `test ! -e Q/SHARE_DUMP` (a `SHARED start` line, a training
  beside another user by SHARE_TRAIN, is allowed); record the 'SHARE_DUMP off' line in IO/queue.log. On cv02, e.g.
  `ssh -n -a -o BatchMode=yes cv02@10.8.1.106 'Q=/tmp/noob_el/bench_q/fin; grep -c "SHARED lane\|SHARED dump" $Q/launch.log; test ! -e $Q/SHARE_DUMP && echo SHARE_DUMP absent'`
  must print 0 and `SHARE_DUMP absent`; otherwise touch Q/HOLD and look.

## 5. Disk plan (E free space 21 Nov 00:45 IST; sizes E where measured, else S)
| Where | Now free | What this package writes | Peak | Stays |
|---|---|---|---|---|
| cv02 /tmp (guard floor 20 GB, disk guard 5) | arm only if cv02 df /tmp shows >= 39 GB right before `arm`; never DISK_OK near the 20 GB floor (the lead frees space by moving old dirs of ours to the NAS, see log.md) | FB code 35 MB; pool root links < 1 MB; 75 D4 dumps x about 0.14 GB (no logp; plain dumps of these runs are 0.13 to 0.14 GB, E) = 10.5 GB in FB/dumps until relayed and removed (step 10); 10 full-pool runs = 5 x 0.96 GB (candidate: latest 0.76 + best 0.08 + slim 0.17, E from c3x runs) + 5 x 0.60 GB (PF, E) = 7.8 GB | +18.3 GB if no dump is removed (free about 24 GB, 4 GB above the floor); about +10 GB with removals at ticks | 7.8 GB (latest.pth of the 10 full-pool runs, kept for the sealed opening) |
| gaint / (relay floor 25 GB at start, relay guard 15 GB) | 46 GB | relay fin: 75 dumps x 0.14 = 10.5 GB + 5 x 0.17 + 5 x 0.10 GB slim = 1.4 GB; read output and cache about 0.55 GB | +12.5 GB (free about 33 GB) | all (the read's inputs) |
| NAS /mnt/nas/noob_el_archive (nfs4, 8.4 TB free) | 8,381 GB | nothing by default; fallback relay dir if gaint < 25 GB at step 9; archive of the relay after the read (lead's choice) | | |
- `arm` refuses below 39 GB free on cv02 without DISK_OK=1 (5 x 1.0 + 5 x 0.62 + 75 x 0.14 + 20, rounded up). The margin
  is thin: if other users write 4 GB more before the dumps are removed, disk guard 5 HOLDs fin (no new training start and no
  dump start; running jobs go on; nothing is lost). Removing relayed dumps at each tick (step 10) keeps the peak near +10 GB.
- No logp anywhere: a logp D4 dump is about 1 GB (E: B5 udev_tta dumps 0.96 to 1.0 GB per 107 cells), 25 GB per arm, which
  cv02 cannot hold beside this package (section 9, Q2).

## 6. GPU-h and wall time on cv02 (S, from E timings)
- Lane configuration (a1): MAXC 8, LPG 1, SHARE_DUMP absent, GAPSEC 30 (section 3).
- Training (E, cv02 launch logs, start to trained): c3x runs median 2.58 h (1.93 to 4.48, n 25); c3_pf_v11 median 1.01 h
  (0.98 to 2.25, n 25). Full-pool runs have the same 20,000 steps: 5 x 2.6 + 5 x 1.0 = **about 18 GPU-h**.
- D4 dumps: plain dumps take 26 to 31 s (c3x) and 84 to 93 s (PF, with a 1 GB logp write) per fold on cv02 (E); D4 = 8 forward
  passes per cell, no logp: about 2 to 4 min each (S; on gaint CPU with 6 threads a D4 dump took 386 s (PF) and 627 s (c3x), E) = **about 3 to 4 GPU-h** for 75.
- **Total about 22 GPU-h.** Wall (S): the 8 trainings start within about 15 min (live check per start); the dump-only jobs
  start one per GPU as GPUs free: PF s5 to s7 end near 1.0 to 1.2 h, then 3 GPUs carry the 75 dumps (about 3 min each plus two
  gaps of GAPSEC = 30 s per job), more GPUs as the candidate runs end (from about 2 h); all dumps are dispatched near 2.3 to
  2.6 h; PF s8, s9 then start and end near 3.3 to 3.8 h; the candidate runs end near 2 to 4.5 h. **About 3.5 to 5 h.** The TTA
  read is possible about 3 h after arming (last dump relayed + 300 s poll), CPU 16 min.
- With the default GAPSEC 120 the 85 jobs would take up to 170 gaps = 5.7 h of dispatch alone: hence GAPSEC 30 (cq_setup.sh of
  F accepts 30 and up; approved with MAXC 8 in REVIEW_FINAL.md; section 9, Q4).

## 7. Pre-registered rule and read
- Rule: **H/FINAL_RULE.md** (written 21 Nov 00:45 IST before any number of this package; clarified before pinning, its
  section 7; updated with the user's decisions U1, U2 before any number): selection bias of the swad readout stated first;
  the approved E1 candidates C1 to C3 and what each needs (HRNet-W18 U-Net++ + swad_const, full pool, seeds 5 to 9, readout
  swad, D4, argmax; C2 single model with seed 5 as the deployable one; C3 the 5-seed ensemble; which of C2 / C3 is "the final
  model" is the opening rule's call, recommendation C2 primary); primary CV5 reads (a) PF_D4 - PF, (b) CS_D4 - CS, (c) CS_D4 - PF
  (selection-biased); relF1@2 decides with M from the PF A/A of the same read; c3x guards on both cell sets; strict crack IoU
  only with its convention band +-0.019 (centreline / v1.1 / 3 px, audit F1). A CV5 read never changes the approved
  candidates: it reports "D4 supported" or FLAG D4, "C2 passes its CV5 check" or FLAG C2, for the lead (and the user) before
  the E1 opening is frozen.
- Read: `H/run_read_final.sh` (bench_wt_final 89b9ea5, bench_read_w1.py fdb56b78 unchanged; 6 arms, 7 pairs, 532 + 416
  cells, OP-A and OP-W); class table `H/final_class_guard.py` (= c3x_class_guard.py byte-equal); rule `H/final_verdict.py`.
  The read refuses before creating its folder unless: worktree clean at 89b9ea5, tool and inputs md5, F commit and tree, 150
  dump folders relayed, every manifest as FINAL_RULE section 6 (run id, fold, seed, key, step 20000, set, fp32, open, revision,
  tta field), one device, exactly two writers (afd91642 plain, 32e0b67c D4), and (review N1, fix round 1) each D4 dump's
  checkpoint_md5 = its plain dump's for the same run and key. The verdict labels every line of a contrast of CS or CS_D4
  against PF or PF_D4, and every level line of CS and CS_D4, "selection-biased"; lines of (b) CS_D4 - CS say "read on the
  cells that selected the readout"; every arm-contrast strict crack IoU is printed with "(convention band +-0.019; decides
  nothing)" (review B3). Command (SHOW=1):
  `scripts/bench_read_w1.py --arm PF=L/house_r34_unetpp_pf_v11:c3_pf_v11_f[0-4]_s[5-9] --arm PF_D4=L/house_r34_unetpp_pf_v11:c3_pf_v11_f[0-4]_s[5-9]\.tta_d4 --arm CS=L/hrnet_w18_unetpp_swad_const_pf_v11:c3x_hrnet_swad_v11_f[0-4]_s[5-9]\.swad --arm CS_D4=L/hrnet_w18_unetpp_swad_const_pf_v11:c3x_hrnet_swad_v11_f[0-4]_s[5-9]\.swad\.tta_d4 --arm CB=L/hrnet_w18_unetpp_swad_const_pf_v11:c3x_hrnet_swad_v11_f[0-4]_s[5-9] --arm CB_D4=L/hrnet_w18_unetpp_swad_const_pf_v11:c3x_hrnet_swad_v11_f[0-4]_s[5-9]\.swad_bn\.tta_d4 --pair PF=PF_D4 --pair CS=CS_D4 --pair PF=CS_D4 --pair CB=CB_D4 --pair PF=CB_D4 --pair PF=CS --pair PF_D4=CS_D4 --labels v11 --workers 8 --cache O/cache_c --baseline PF --aa PF:5,6:7,8 --groups /home/noob/work/bench_data_v3b/meta/cv5v3_groups.tsv --score-exclude T/benchmark/splits/score_exclude_v3.txt --out O/read` (L = /home/noob/work/bench_reads/final_tta/links/elbench1, O = /home/noob/work/bench_reads/final_tta; cwd bench_wt_final, nice 19). Relay paths: RELAY_FIN (default /home/noob/work/bench_relay/fin) for the 75 D4 units, bench_relay/c3base and bench_relay/c3x for the plain arms. If (b) does not support D4 the verdict prints FLAG D4 and CS - PF with the (c) criteria as information (FINAL_RULE section 4); (c) is always CS_D4 - PF; no flag changes the approved candidates.

## 8. Tests (E; CPU only, nice 19; outputs in H/evidence)
| Test | Result |
|---|---|
| pytest at F (full) | 808 passed, 5 skipped, 0 failed (pytest_full_821dfad.log) |
| the 2 stale test files at 03375d4 / e25728e (scratch archives) | 1 failed (test_variants_exist), 22 passed at both: the failure predates 491e460 |
| final_codeproof.sh (CV02=1, full) | 0 FAIL (section 2); tampered commit: 5 FAIL (DUMPS=0), 7 FAIL (FAST=1) |
| final_make_jobs.py | 85 lines, md5 cc4d7006; own asserts; refuses an existing output |
| final_poolsmoke.sh (both cards) | rc 3 by design, startup line = want_line, cfgcheck OK, 0 Traceback (poolsmoke/) |
| final_render_smoke.sh on cv02 (real cq.sh of F, 85 lines) | all arming checks passed, stopped at the logger check; render compare 0 FAIL (render_smoke/) |
| final_queue.sh DRY / refusals (queue_dry/queue_dry.out) | build OK (85 lines, 50 sources complete, no name in use); refused: second build, wrong F, wrong FB, FB not deployed (root, render), bad MAXC, GAPSEC 20, arm without render; place / guard DRY print their writes; status read only |
| read script (final_read_test.sh, fake relay root + STUB) | 22 of 22: positive path (150 links, 6 arms, 7 pairs reach the tool; each arm regex fullmatches exactly its 25 names; TAG repeat); refusals with no folder written: a missing relay unit, a missing `relayed` log line, one wrong manifest field each (CS_D4 key, PF_D4 tta false, PF_D4 revision, CB_D4 step, a plain arm with the D4 writer, plain CS with tta d4), a third writer, two devices, review N1: a D4 dump from another checkpoint and a plain dump without checkpoint_md5, wrong F, F_REPO without F, existing output folder; RELAY_FIN outside the relay root (read_tests/final_read_test.out); with the N1 check disabled both N1 cases fail (read_tests/final_read_n1_mutant.out) |
| verdict (final_verdict_test.py, synthetic read.json) | 68 of 68: every outcome of (a), (b), (c); every row of FINAL_RULE section 4 (D4 supported; FLAG D4 for each failure kind; C2 passes; FLAG C2; both flags; CS - PF information pass or fail per criterion under FLAG D4); false_alarm_pf; band labels; inclusive and strict edges; refusals; --mechanics; and (review B3) rvB3: on the base and the FLAG D4 outputs every line carrying a CS / CS_D4 number is labelled (317 lines) and every arm-contrast crack_iou line carries the convention band (116 lines). Tampered verdicts: five earlier copies caught (66, 65, 62, 63, 61 of 67); three B3 copies (no CS-vs-PF label, no band, no level label) caught by rvB3 (read_tests/final_verdict_test.out, final_verdict_mutants.out, final_verdict_b3_mutants.out) |
| verdict on a relabelled copy of the real c3x read.json, --mechanics | reproduces the C3X_READ guard counts (COMBO_SWAD - PF fails only the 2 ARTS width items on 416 cells; COMBO - PF 8 items); refused without --mechanics |

## 9. Choices for the lead (my recommendation first; built as recommended)
1. **Openings (approved by the user, built by opening_builder).** Nothing of them is in this queue. What this package hands
   over: the 10 full-pool checkpoints (section 11) and the CV5 verdict with its flags. Single-model D4 dumps on sealed sets
   need no code change at F; F's queue tool cannot render them (section 11), and C3 needs logp or an in-process ensemble on a
   sealed set: both are opening_builder's reviewed changes.
2. **C2 vs C3 as "the final model"**: the opening rule's call. Recommendation (S): C2 primary (deployable single model,
   1/5 of C3's inference cost, the public rows are single models), C3 beside. This package has **no CV5 ensemble read**: it
   needs logp dumps (about 1 GB each, 25 GB on cv02 for the CS_D4 arm) that cv02 cannot hold beside this package (section 5).
   If the lead wants one before the opening: after fin's D4 dumps are relayed and removed, one more dump-only queue of 25
   lines with logp 1 (the job kind supports it; same F) and bench_ens_dump on gaint; about 1.5 GPU-h, 25 GB transient on
   cv02 and on gaint (or the NAS), and its own registered read.
3. **CB_D4 (swad_bn + D4) included** as descriptive: 25 dumps, about 1 GPU-h, 3.5 GB transient. It shows whether D4 removes
   swad_bn's false-crack excess; it decides nothing (swad is fixed post hoc, FINAL_RULE section 0). Drop by deleting those 25
   lines in a new IO (then the read refuses: it expects 150 dumps; the read script would need the arm removed: re-review).
4. **Queue shape** (lead's ruling of 21 Nov; approved in REVIEW_FINAL.md "Lane configuration"): one queue (only one cv02 queue
   that can start training), MAXC 8, LPG 1, SHARE_TRAIN 20480, SHARE_DUMP absent (step 8b), GAPSEC 30; order trainings / dumps /
   last two PF trainings (section 3); one process of ours per GPU at all times.
5. **FINAL_RULE clarifications** made before pinning (its section 7 and the U-update): (b) is read with the tool's
   unpaired-seed bootstrap (conservative); C1 shown with D4 in the opening iff (a) CONFIRMED; false_alarm_pf counts as a
   false-alarm item; a CV5 read FLAGS, never drops (the user's approved candidates stand until the lead and the user decide).
   Please confirm or rule otherwise before the read.
6. **Disk** (lead's ruling of 21 Nov): arm only if cv02 df /tmp shows >= 39 GB right before `arm`; never DISK_OK near the 20 GB floor (the lead frees space by moving old dirs of ours to the NAS, see log.md). Remove relayed D4 dumps at every tick (step 10).
7. Old queues: c3all, c3all2, c3base, c3hrnet still have live cq.sh processes with MAXC 0 and HOLD (E); they cannot start
   training, so qscan passes. Untouched, as the rules say.

## 10. Not tested
- Anything on a GPU: the 85 jobs, D4 dump time and memory on cv02 (estimates only), the full-pool runs beyond 1 CPU step.
- `final_queue.sh` root / render / place / guard / arm for real (FB does not exist yet): DRY and refusal paths only; the same
  cq.sh render ran for real in the render smoke against a scratch deploy.
- The relay of a dump-only unit (relay_w1c.sh relays what RUN.md5 lists; dump-only RUN.md5 = the dump files, by cq.sh of F,
  covered by test_bench_cq_final.py) and c3_f81_list.sh on such a unit (read: its regexes accept the dotted names).
- The real read: synthetic and relabelled inputs only; no end-to-end bench_read_w1 run with the 6 arms (about 60 CPU-min).

## 11. Plug-in point for opening_builder (sealed-set dumps; not in this queue)
- Checkpoints (cv02, deploy of F): `/tmp/noob_el/bench_821dfad/experiments/fin_pf_v11_pool_s<5..9>` (C1, key model) and
  `/tmp/noob_el/bench_821dfad/experiments/fin_hrnet_swad_v11_pool_s<5..9>` (C2 / C3, key swad; swad_bn also there), each with
  config_used.yaml, checkpoints/latest.pth (all readouts; kept on cv02, never removed by this package's tools) and
  checkpoints/slim.pth (relayed to gaint with LATEST.md5 = the md5 of latest.pth). One machine (cv02 A6000), fp32.
- Same deploy and queue tool: a sealed-set dump line can use F's dump-only job shape
  (`<run>.<key>.tta_d4|<card>|<seed>|<root>|0|<gate>|<dgate>|<logp>|--dumpof /tmp/noob_el/bench_821dfad/experiments/<run> --key <key> --tta d4`),
  but cq.sh at F takes the set from the root and refuses dump-only lines on the full-pool root, and bench_infer at F refuses
  `--logp` on sealed sets. So the opening needs a reviewed commit G on F (a set token with `--opening <protocol>` for dump-only
  lines; the C3 path), a deploy of G, and a new queue made with final_queue.sh's pattern (build, render, place, guard, arm;
  one queue that cannot train). G's dumps can read F's run dirs: the dump-only kind accepts any
  `/tmp/noob_el/bench_<7 hex>/experiments/<run>` (cfgcheck against card, seed, run name and root at arming).
- The opening must run after fin's 10 trainings end (`trained fin_* rc=0`, slim and RUN.md5 written); fin's relayed RUN.md5
  and LATEST.md5 pin the checkpoint bytes the opening reads.

## 12. Files (H; md5sum at the end of the build)
| File | md5 | Role |
|---|---|---|
| FINAL_RULE.md | 82867156eb2a469b5f9328bd766da0c9 | registered rule (pin in the review) |
| PUBLIC_BENCH.md | 136e27cb6904f1967034df8a17c57d75 | public benchmark note (previous builder, 19 Nov; unchanged) |
| final_codeproof.sh | e7c299e5a22cc219986bce02e241fda1 | step 3, code proof of F |
| final_make_jobs.py | 4c062f8391d98066166d72cd84dacc16 | job list builder (85 lines) |
| jobs/jobs_fin.txt | cc4d7006ab0c4e23bba896474c0f7169 | the job list (= IO/jobs.txt of step 4) |
| final_queue.sh | e574e25f5f5cb98f525918838af6b251 | steps 4 to 8 and 10 (build, root, render, place, guard, arm, status) |
| final_rendercmp.py | 0b244a0df82c6d0945d588bf3773741b | render check (templates + semantics) |
| final_render_smoke.sh | fbef08cfc4c3c21a16e07f2fd75430d9 | builder's cv02 render smoke (done; evidence/render_smoke) |
| final_poolsmoke.sh | e875c58398fa9252601357d62b24601a | builder's CPU smoke of the full-pool training path (done; evidence/poolsmoke) |
| diskguard5.sh | 2719c5f703c0fe6b42436e07cff68d81 | cv02 disk guard for fin (= diskguard4.sh, queue/stop/log changed) |
| final_relay.sh | 281469bafecc1e47d9cd6d6ae21aa80c | step 9 relay start (relay_w1c.sh 74a2ec3d unchanged) |
| final_relayguard.sh | 2907baa610395d1ccb94cd1fa6bd696a | step 9 gaint relay guard (= c3x_relayguard.sh, relay/stop/log changed) |
| run_read_final.sh | a6e952ecbe17ae182a6a8963e1971d05 | step 11 read |
| final_verdict.py | 5acea6c48c9804cb5b7b1a3326a37fc4 | step 11 rule (FINAL_RULE sections 2 to 4) |
| final_class_guard.py | c9022bcc9ddb964298bcd38bf01ab375 | per-class table (= c3x_class_guard.py, byte-equal) |
| final_verdict_test.py | cd44a24686ad53a22bcf98b2ed8122ac | verdict tests (68) |
| final_read_test.sh | 94370004d92bd5ae8cac6357bc8ec376 | read script tests (22) |
| evidence/ | see evidence/MD5_evidence.txt (ce7db1d2f35d922a72f66b3f52d02e8e, 41 files) | outputs of section 8 |
Commit F: 821dfadf49116cc6d5fdbd6697e263dd7cf0f834 (tree 114d5469340e7bfd496f290c18dccb7d4f13bdd3; parent 491e460; bench_wt_fin clean). Pinned in the scripts: F and its tree (final_queue.sh, run_read_final.sh), the 14 FB file md5s and the 10-path diff to bench_03375d4 (final_queue.sh), the root pins (final_queue.sh), relay_w1c.sh 74a2ec3d (final_relay.sh), bench_read_w1.py fdb56b78, groups d880a769, score_exclude 6d48dfbd, writers afd91642 / 32e0b67c (run_read_final.sh). evidence/MD5_evidence.txt is a snapshot: evidence/codeproof/negative_fast.out was still being written by the FAST negative run when the table was first taken; refreshed after it ended.

