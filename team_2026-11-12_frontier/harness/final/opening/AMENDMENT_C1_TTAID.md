# AMENDMENT C1 ttaid: pre-written, NOT applied (opening_builder, review round 1 N12, 21 Nov 2026)

**Status: written and tested on copies only; no H file is changed by it.** It is applied only if, during the opening, a C1
plain dump (key model, `--tta none`) fails closed at dumpfmt.check_cell (a float32 near-tie of the two top classes: the plain
path's pred = argmax of the logits disagrees with the maps from log(p + 1e-12); OPENING_RULE.md section 2 "Pre-registered
contingency"). Symptom in the cv02 queue `open`: `dumped dump_<name> rc=1` with `pred disagrees with where(m_crack > 0, 14,
oth)` in dlogs/dump_<name>.stdout; no RUN.md5, so the relay never gets that unit and stops at "RELAY DONE: cv02 queue ended"
with N - 1 (or fewer) units.

## What changes (and nothing else)
- That one dump is redone with `--tta id`: the same single view through bench/tta.py (predict_tta with no D4, p = softmax of
  the one view; pred = argmax log(p + 1e-12), first index on ties: the ttafix rule, consistent with oth and m_crack by
  construction). Same checkpoint, same set, same logp setting (E1: logp 1 and `--ens-member`, so E-PF keeps 5 members). New
  run id `<run>.ttaid.<set>` (the failed dump's partial dir in GB/dumps blocks the old name; bench_infer refuses an existing dir).
- C1 stays "PF, one view, argmax"; only the pred tie rule differs, and only at merged float pairs. The verdict gets one line
  naming the amendment.

## Files (in H/amendment_c1_ttaid/; md5)
| File | md5 | What |
|---|---|---|
| make_amend.py | 2546103d | writes IO/amend/jobs.txt (one `--tta id` line per failed C1 plain job) and IO/amend/AMEND.txt (failed names, `amend_jobs <md5>`, `registered_base <REGISTERED.txt md5>`) + AMEND.md5, read-only; refuses a name not in IO/jobs.txt, a non-C1-plain line, or an existing IO/amend |
| opening_rendercmp.py.patch | 2f317ce0 | kind C1ID = key model with `--tta id`, allowed only with a name containing `.ttaid.`; its logp rule = C1's |
| opening_queue.sh.patch | bcfec40d | AMEND=1 + AMEND_MD5: queue `open2`, list IO/amend/jobs.txt, outputs in IO/amend/; unstage covers the base jobs minus the failed ones plus the amendment's, and removes the failed jobs' partial dump dirs (only if they have no RUN.md5, i.e. were never relayed) |
| opening_relay.sh.patch | 66e2bf8a | AMEND=1 + AMEND_MD5: Q = open2, RESUME=1 on the same RD (N stays the registered count: the failed units never get .ok) |
| run_opening_read.sh.patch | 49271426 (regenerated against run_opening_read.sh of the fin2 change set; the same 29 changed lines as 0bcfae8e) | if IO/amend/AMEND.txt exists, AMEND_MD5 must be its md5; the expected rows = the registered list with the failed lines replaced by the amendment's (same length); tta expectation mode_spec('id') = {mode id, scales [1.0], d4 false, views 1} for those; the C1 record globs and the E-PF regex accept `.ttaid.`; one line naming the amendment is appended to verdict.txt (before MD5.txt) |
The patches are unified diffs against the current files (after the fin2 change set: opening_rendercmp.py, opening_queue.sh and
run_opening_read.sh regenerated with the same changed lines; opening_relay.sh unchanged; md5s in OPENING_REQUEST.md section 12); `patch --dry-run -p1` applies all four cleanly in H (E).

## Procedure (lead), only if the symptom above occurs
1. Let the queue `open` finish (other dumps continue); note the failed name(s) from launch.log. Nothing else is rerun.
2. Before anything runs again: `python H/amendment_c1_ttaid/make_amend.py --io /home/noob/work/bench_open_io --failed <name> ...`;
   log AMEND.txt's md5 in both ledgers as an amendment line of E1 #8 / test50 #19 ("C1 <name> redone with --tta id, OPENING_RULE
   section 2 contingency").
3. Apply the four patches (`cd H && patch -p1 < amendment_c1_ttaid/<file>.patch`) and send the four diffs to the reviewer, who
   checks they equal these pre-reviewed patches (md5 above) and nothing else changed.
4. `AMEND=1 AMEND_MD5=<md5> G=<G> bash H/opening_queue.sh check | render | place | arm` (queue open2: the amendment lines only;
   disk guard 7 already covers `open`; for open2 the lead runs `guard` with the queue name changed or keeps the window short);
   `AMEND=1 AMEND_MD5=<md5> G=<G> bash H/opening_relay.sh` (continues the same RD).
5. The read as registered, with `AMEND_MD5=<md5>` added: `REG_MD5=<reg md5> AMEND_MD5=<md5> bash H/run_opening_read.sh`.
6. `AMEND=1 AMEND_MD5=<md5> G=<G> bash H/opening_queue.sh unstage` (removes the relayed dumps, the failed partial dirs and DS).

## Tests run (E: evidence/amendment_test.out)
- make_amend.py: refuses a C2 line, a C1-D4 line, an unknown name, an existing IO/amend; writes 2 lines for 2 failed C1 plain
  jobs (E1 with logp 1, test50 with logp 0) with names `<run>.ttaid.<set>` and `--tta id`.
- Patched opening_rendercmp.py: 0 semantic FAIL on the amendment lines (the unpatched one: 2 FAIL, so the patch is needed) and on
  the 30-line base list; a misnamed id line and a flipped logp are FAILs; template = rendered, `render compare: 0 FAIL` for both.
- Patched opening_queue.sh, opening_relay.sh, run_opening_read.sh: `bash -n` passes; `patch --dry-run` applies all four in H.
- Not tested: a real run of the amended queue, relay and read (cv02, GPU), and a render of an `id` line through G's cq.sh (its
  dump-only mode check accepts none / id / d4 / d4ms, E code; the tests render `none` and `d4`).
