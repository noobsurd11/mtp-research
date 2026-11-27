# T3b AMENDMENT_1: kb_check line order; re-registration of E1 opening #9 (registration 2)

t3b_builder, 22 Nov 2026, about 02:40 IST. Written after step 5 of LAUNCH_REQUEST_t3b.md refused, before any E1 file reached cv02.
Tags: E = shown by a command (file cited); S = judgement. H3 = T/harness/t3b, IO = /home/noob/work/bench_t3b_io.

## 1. What happened (E)
- Steps 1 to 4 ran (log.md 22 Nov): registration 1 at 02:24:25, REGISTERED.txt **fb2c424c2fcc0494e3b3fb73126337ce**; ledger row #9 and
  bullet; build rc 0 (MANIFEST.md5 7ab27f32, ROOTS_t3b.md5 d7d5cae6); deploy of K to KB = /tmp/noob_el/bench_cba7fbd (CODE.md5
  fe36b04e, 800 files, CV02_CODE_OK).
- Step 5 (`t3b_queue.sh check`) refused: `KB differs from F2B in other paths than K's: <.gitignore <Makefile <README.md ...`.
- Cause: kb_check diffed F2B/CODE.md5 and KB/CODE.md5 line by line without sorting. F2B's CODE.md5 (fin2's deploy, 781 lines
  without REVISION) is in another line order (starts bench/aa.py, bench/atlas.py: a locale sort) than KB's (798 lines, C order:
  .gitignore, Makefile). The unsorted diff lists 123 path entries; sorted by path, it lists exactly the 33 entries of DW
  (E: lead's read-only run; evidence/amend1/realinput_audit.out rows 1 to 3; the same 'en' order reproduced in
  evidence/amend1/kbcheck_smoke.out). KB is correct; the check was wrong. (S, incidental: c3_deploy.sh calls `sort` without
  LC_ALL, so its CODE.md5 order depends on the caller's locale; this is why the two deploys differ. Not changed here.)
- Nothing of T3b is on cv02 except the code deploy KB: no DT, no DS, no queue dir (E: audit row "stage precondition: FREE").

## 2. What changes
| File | Change | md5 (registration 1 -> amended) |
|---|---|---|
| t3b_queue.sh | kb_check: both CODE.md5 files sorted by path (`LC_ALL=C sort -k2`) before the diff; nothing else in that comparison. dt_check (audit item): the gaint side's LINKS.tsv is also `LC_ALL=C sort`ed before its md5, as the cv02 side already was (the file is Python-sorted, the same order for ASCII names: a no-op today, one assumption fewer). A 3-line header note. Diff: evidence/amend1/t3b_queue.sh.diff | cad952c0 -> **51a96237** |
| t3b_register.sh | the t3b_queue.sh entry of SCRIPT_PINS only (diff: evidence/amend1/t3b_register.sh.diff) | 547fc3a7 -> **8cecc851** |
| new: t3b_kbcheck_smoke.sh, t3b_realinput_audit.sh | the order smoke and the real-input audit (section 4) | 61d0852b, bd84f5e7 |
**Not changed:** T3B_RULE.md 0c006d44; lists/LISTS.md5 5c86318a; job lists d77f3a94 / 9423cb91 (same K); K cba7fbd (tree
b653389f); KB (stays; no redeploy); run_t3b_read.sh e4cda97a, t3b_relay.sh 2870fd43, t3b_verdict.py 7dee83d6, t3b_rendercmp.py
d6eec93f, diskguard8.sh 0fe96ad9, t3b_label_precheck.py 214d087d (their pins in SCRIPT_PINS are unchanged).

## 3. Why re-registration (registration 2) and not a smaller path (S)
- REGISTERED.txt (read-only, md5 in the ledger) pins t3b_queue.sh cad952c0 in its 'scripts' line, and the queue refuses unless its
  own md5 is that one; so the fixed queue needs a new registration record.
- Smaller paths considered and rejected: (a) a registered "script amendment" file that the queue accepts as a second md5 source
  (like the repair records): new trust code inside the registered scripts, a second place where pins live, more to review;
  (b) editing REGISTERED.txt: it is read-only and its md5 is in the ledger.
- Re-registration is safe here: no E1 file has reached cv02; registration 2 hashes the same E1 files, copies the same 106 images
  and writes the same job lists, stage manifest, E1 file hashes and zero-shot hashes, so every line of REGISTERED.txt except
  'registered' (date) and 'scripts' must be identical (step 5 below checks this); the build is deterministic (E: the chain
  smokes' builds of the same synthetic data gave identical MANIFEST / ROOTS md5s), so the rebuild must give MANIFEST 7ab27f32 and
  ROOTS d7d5cae6 again. It stays E1 opening #9 (one opening; registration 1 superseded before any data reached cv02).

## 4. Tests (E; gaint CPU; synthetic or read-only)
- `bash H3/t3b_kbcheck_smoke.sh evidence/amend1/kbcheck_smoke.out`: **"kb_check order smoke: 0 FAIL"**: registration-1 kb_check
  REFUSES F2B CODE.md5 in 'en' order (first paths bench/aa.py bench/atlas.py, the real F2B order) and in reversed order; the
  amended kb_check PASSES both; negatives for the amended one: an extra path in KB REFUSED; a changed README.md in KB REFUSED.
- `bash H3/t3b_realinput_audit.sh evidence/amend1/realinput_audit.out` (read-only; table in LAUNCH_REQUEST section 6c): amended
  kb_check on the real KB / F2B "real-input OK" (REVISION K, CODE.md5 OK, pins OK, differs from F2B only in K's paths); the
  registration-1 version refuses with 123 entries; data_check, names_check, stage precondition, arm_q's queue-dir string,
  free_gpus / df, guard preconditions, q1_done's remote part and parser, relay / .ok / LATEST.md5 formats, unstage's gaint-side
  checks, relay preconditions: all real-input OK; dt_check, ds_check, render, place / arm, relay deploy, unstage's cv02 part and
  the read are not testable before stage / the runs (stated per row).
- Reruns: guard test "guard test: 0 FAIL" (35 cases); repair smoke final gate rc 0; render smoke "render compare: 0 FAIL" for 33 /
  30 / 2 lines; chain smoke (see LAUNCH_REQUEST section 7).

## 5. Lead steps (after the review of this amendment)
1. Confirm cv02 holds nothing of T3b but KB:
   `ssh -n -a -o BatchMode=yes cv02@10.8.1.106 'ls -d /tmp/noob_el/bench_data_t3b /tmp/noob_el/bench_data_sealed /tmp/noob_el/bench_q/t3b* 2>/dev/null; true'` -> empty.
2. Keep registration 1, read-only: `mv /home/noob/work/bench_t3b_io /home/noob/work/bench_t3b_io.superseded1 && chmod -R a-w /home/noob/work/bench_t3b_io.superseded1`.
3. Ledger e1_openings.md, a dated bullet after the #9 bullets (before step 4): "- **#9 amendment 1** (lead, <date> IST):
   registration 1 (REGISTERED.txt fb2c424c, 22 Nov 02:24) superseded before any E1 file reached cv02 (only the code deploy KB
   existed): t3b_queue.sh's kb_check compared two CODE.md5 files in different line orders and refused a correct KB (fix: both
   sorted by path; harness/t3b/AMENDMENT_1.md <md5>); registration 2 follows with the same rule 0c006d44, lists 5c86318a, jobs
   d77f3a94 / 9423cb91, K cba7fbd and KB; registration 1 kept read-only in /home/noob/work/bench_t3b_io.superseded1."
4. Registration 2 from a clean shell: `env -i HOME=$HOME PATH=/usr/bin:/bin bash H3/t3b_register.sh` -> REG2 (new REGISTERED.txt md5).
5. Identity check (must print nothing): `diff <(grep -vE '^(registered|scripts) ' /home/noob/work/bench_t3b_io.superseded1/REGISTERED.txt) <(grep -vE '^(registered|scripts) ' /home/noob/work/bench_t3b_io/REGISTERED.txt)`.
6. Ledger: replace row #9's line by the row registration 2 printed (it holds REG2; build and stage refuse without a '| 9 |' row
   holding REG_MD5); log.md line.
7. `REG_MD5=$REG2 bash H3/t3b_queue.sh build`, then (must print nothing):
   `diff <(grep -E '^(data_manifest|roots|links|e1_labels) ' /home/noob/work/bench_t3b_io.superseded1/BUILD.txt) <(grep -E '^(data_manifest|roots|links|e1_labels) ' /home/noob/work/bench_t3b_io/BUILD.txt)`
   (data_manifest 7ab27f32..., roots d7d5cae6...). If anything differs: stop.
8. Step 5 of the request with the existing KB (no redeploy): `REG_MD5=$REG2 K=cba7fbdf5df1579d6efb1168eb292e637bc9fad6 bash H3/t3b_queue.sh check`
   -> "KB /tmp/noob_el/bench_cba7fbd: REVISION K, CODE.md5 OK, pins OK; differs from F2B only in K's paths (+ REVISION)".
9. Continue LAUNCH_REQUEST_t3b.md section 6 from step 6 (stage) with REG_MD5=$REG2.
