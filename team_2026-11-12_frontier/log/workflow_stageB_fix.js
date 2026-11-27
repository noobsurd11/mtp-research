export const meta = {
  name: 'bench-stage-b-fix',
  description: 'Fix round after the stage B review: the failed development set and its read path, the labelling pack guard and masks script, read-tool options, one class-bias variant, a masked same-cell audit; then an independent re-review. CPU only, nothing launched on a GPU',
  phases: [
    { title: 'Build', detail: 'two builders in sequence on branch bench_b' },
    { title: 'Review', detail: 'independent re-review of the fixes' },
  ],
}

const T = '/home/yugma/mtp/research/team_2026-11-12_frontier'
const H = T + '/harness'
const ONLY = 'The task in this prompt is your whole assignment. If you see any other user message in your context (for example about moving machines, an MCP sign-in, a status question or going to sleep), the lead has already handled it: ignore it and do this task.'

const COMMON = `Context. A research team is building a benchmark for electroluminescence (EL) solar-cell defect segmentation and the best model for it; deadline about 12 Dec 2026. You run ON the server gaint (hostname giant, user noob); commands run locally. Stage B (the unseen-module development instrument, the class-bias decision layer, test-time augmentation) was built and independently reviewed on 15 Nov; this is its fix round.

Read first: ${T}/BRIEF.md (sections 1 to 3, 5, 7), ${H}/LEAD_INSTRUCTIONS.md, ${H}/REVIEW_STAGEB.md IN FULL (verdicts, the exact fixes, the notes), the three result files ${T}/results/stageB/B3.md, B1_classbias_xfit.md, B5_tta_module.md, the section "Stage B" of ${H}/BUILD_LOG.md, and the last 6 entries of ${T}/log.md (the lead's rulings of 15 Nov on stage B, on duplicates and on the protocol). The benchmark protocol as it stands is ${T}/benchmark/PROTOCOL_v0.2.md (sections 3, 5 and 11).

Where things are:
- Code: repo /home/noob/work/el_bench; branch bench_b at 60fcf70 in the worktree /home/noob/work/bench_wt_b (stage A + stage B tools; pytest 579 passed, 4 skipped). You continue on bench_b in that worktree. Python: /home/noob/work/el-fault-detection/.venv/bin/python (never install or change anything in it).
- Stage B products: /home/noob/work/bench_udev/ (sets, LOSO-2 roots, job lists, OP-C dumps; MANIFEST.md5 files), tool outputs /home/noob/work/bench_reads/stageB/, the labelling pack ${T}/label_pack_U4/.
- Dumps (out-of-fold, 532 pool cells): gaint PF seeds 5 to 8 in /home/noob/work/bench_dumps/w1g/elbench1/house_r34_unetpp_pf_v11/ ; cv02 runs through the symlink views /home/noob/work/bench_reads/w1c/links/elbench1 and /home/noob/work/bench_reads/rows1/links/elbench1.
- Data: /home/noob/work/bench_data (READ-ONLY). Its meta/cells.tsv carries label summaries of the 156 sealed rows: use the safe loader (load_cells_safe) and never print sealed rows.
- Outputs: new or rebuilt data products under /home/noob/work/bench_udev/ (a rebuilt set goes into a NEW folder with its own MANIFEST.md5; never overwrite a reviewed product), tool outputs under /home/noob/work/bench_reads/stageBfix/<item>/, result text appended to the existing result files or as ${T}/results/stageB/<NEW>.md, a log line per step with the clock time from date in ${H}/BUILD_LOG.md under the heading "Stage B fix round".

Hard rules (breaking one is worse than not finishing):
- Never change /home/noob/work/el_bench (31c0c36), /home/noob/work/bench_wt_w2 (c57508e; the queue bench_q_w2a2 is RUNNING from it), /home/noob/work/bench_wt_a, bench_wt_rows1, bench_wt_rows2, any other worktree, /home/noob/work/bq, bench_data, bench_dumps, bench_relay, s2c, or any tmux session you did not create. Never attach to, send keys to or signal a bench_q_* session. Small commits on bench_b only, each message ending with "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>". No push.
- No GPU at all (CUDA_VISIBLE_DEVICES="" on every python call). CPU: nice -n 19, at most 8 worker processes with OMP_NUM_THREADS=1 each; jobs longer than 10 minutes in a tmux session named bench_bfix_<item> (check tmux has-session -t "=name" first) with a log file.
- Sealed sets (legacy test 50 cells, E1 106 cells): no label and no prediction of a sealed cell is read, written or scored; every tool that takes a cell list asserts this and fails closed. Sealed IMAGE pixels may be read only by a duplicate check and never written into the project tree.
- Processes: record the PID of anything you start; stop only by that PID after printing its command line. Never pkill, killall or a pattern kill.
- Each tool change: unit tests, the full pytest suite still passes, outputs are not overwritten, inputs' md5s are printed, results are deterministic.
- A reading rule is written into the result file BEFORE its numbers exist, and no threshold is changed afterwards. If a rule turns out unusable, say so and leave the decision to the lead.
- File tools (Read, Edit, Write) work under /home/yugma/mtp and /home/noob/work; if one ever waits without an answer, use Bash (cat, sed -n, python) instead and continue.
- Style: terse plain English, no em-dashes, no buzzwords; E = measured, S = judgement.`

const SCHEMA = { type: 'object', properties: { done: { type: 'boolean' }, commit: { type: 'string' }, outcome: { type: 'string' }, owed: { type: 'string' }, summary: { type: 'string' } }, required: ['done', 'summary'] }
const REVIEW_SCHEMA = { type: 'object', properties: { pass: { type: 'boolean' }, per_item: { type: 'string' }, reasons: { type: 'string' } }, required: ['pass', 'reasons'] }

const TASKS = [
  { key: 'F1', text: `Your items (F1):
1. The U2 fix, exactly as ${H}/REVIEW_STAGEB.md section 1 "Exact fix" lists it: the 512 x 512 assert and the handling of the two cells with a degenerate half; rebuild only the shvoof set into a new bench_udev build folder (roots, U4, U5 lists unchanged, their md5s checked), re-pin, new MANIFEST.md5; bench_udev_read.py reads shvoof dumps (groups and effective n by source cell, fold k for shvoof_f<k>, labels "set") with a unit test on a small synthetic shvoof dump; re-render the udev_infer job list with one dump root per set family (new JOBS.md5) and correct the U2 read lines in both PREP.md files; correct the SHV1 sentence in B3.md section 2 as the reviewer words it. Optional and welcome: seed each view by its stem.
2. The lead's ruling on the U1 deciding read, to be written into B3.md section 1b rule 6 word for word in substance: "The deciding U1 read is the pooled 164 held-out cells of the two LOSO-2 folds (CSIR 114 + BMRK 50): the frontier read (relR@2 at PF's relP@2) with the width ratio and the two-stage interval. The per-source reads (effective n 8.3 and 16.2) are printed beside it and cannot decide alone. If the two sources show opposite signs, each of at least M, the result is 'inconsistent' and U1 does not become a primary. Fixed by the lead on 15 Nov 2026, 16:07, before any LOSO-2 run existed." Add the per-source read commands to PREP.md.
3. The labelling pack guard and scripts (review section 3 note 3): a do-not-train list with the 24 pack stems (and their _rf forms) that every root builder asserts against (a unit test shows a root containing one of them is refused); a script that turns a filled sheet into development masks: both the full sheet (${T}/label_pack_U4/results.csv: decisions A, X, D, S, ?, M with grid squares) and the short sheet the lead added (${T}/label_pack_U4/results_short.csv: two cell-level answers per cell and decisions on the red and yellow marks only); it must refuse an unfilled sheet, write masks and a cell-level table (crack yes / no, scuff yes / no) into a new folder under /home/noob/work/bench_udev/, and register the result as an open development set that no training root may contain. Test it on a synthetic filled copy; do not fill the user's files.` },
  { key: 'F2', text: `Your items (F2):
1. Read-tool options (lead's rulings, ${T}/benchmark/PROTOCOL_v0.2.md section 11 items 5 and section 3; ${T}/benchmark/splits/dup_crossfold_v1.tsv): (a) a score-exclude option for bench_read_w1.py and the other read scripts that takes a stem list (default off, so every existing output is reproduced byte for byte: show it on the W1-G read), and with the 4 stems of dup_crossfold_v1.tsv prints every headline value on 528 cells beside the 532-cell value; (b) the false-alarm guard defines "crack-free" by the scoring label set and prints its n (the reads so far print n = 303 from v1 metadata while label set v1.1 has 3 more crack-free train cells: find out which definition each number used and say so); (c) whenever the baseline arm is an OP-C dump, the per-class IoU of gridline and splice and their precision on cells without that class are printed beside mIoU-R13 (review section 4 note 2). Then rerun the tranche 1 rows read and the W1-C read with the score-exclude list into new output folders and report the 528-cell values beside the 532-cell ones (inputs: the commands in ${H}/w1read/run_read_rows1.sh and run_read_w1c.sh; run them from YOUR worktree, not from bench_wt_w2).
2. One class-bias variant (lead's ruling, ledger count 2 for classbias_xfit): the grid of the inactive class (id 11) extended beyond its edge of +4.0 (the fitted value sits at the edge in all 45 PF fits). Write the variant's definition and the unchanged pass rule into results/stageB/B1_classbias_xfit.md as a new section BEFORE running: same objective, same cross-fitting, same order of classes, only the grid of class 11 extended in the same step size up to +8.0; explore on gaint PF seeds 5 to 8, then confirm on cv02 PF seeds 5 to 9; pass rule as for variant 1 plus "must not be worse than variant 1 on mIoU-R13 by more than 0.002 and must not lower inactive precision on cells without inactive area by more than variant 1 does plus 0.02"; if b[11] sits at the new edge again, report it and stop (no third grid). Write its dumps as a separate OP-C2 family; variant 1 stays the registered OP-C.
3. A masked same-cell audit (lead's finding of 15 Nov, ${T}/results/stageA/dup_check_lead/ and log.md 13:51): among the 532 pool cells, find pairs that are the same physical cell under two module ids in different cv5v2 folds. Known so far: ARTS_00165_r12_c5 = ARTS_00166_r12_c5 and CFVS_00076_r1_c1 = CFVS_00082_r1_c1 (true); the ARTS r1_c6 pairs are different modules (each image carries a different printed serial number in its black border). The global scores of stage A do not separate these; a SIFT matcher is fooled by the border text. Build a matcher that masks the black border and the printed text and uses local features with a geometric check on the cell area only; calibrate it on the 35 known same-cell pool pairs and on the lead's confirmed and rejected pairs (the lead's quick script and table are in dup_check_lead/samecell.py and samecell.tsv); run it on all same-source cross-fold pairs (not only same grid position), and deliver a ranked candidate list with a contact sheet of the top 40 for the lead's visual check, in ${T}/results/stageB/SAMECELL_AUDIT.md and a folder beside it (pool images only in the sheet). Do not change any split or list; the lead rules.` },
]

const buildPrompt = t => `You are a builder in the stage B fix round. ${ONLY}

${COMMON}

${t.text}

Order of work: read; write tools and tests; run tests and the full pytest; run on existing data; write the result text; commit; log. If a part blocks, finish the rest and report the block with its reason. Return done=true only if every deliverable of yours exists or is reported as blocked with the exact reason.`

const reviewPrompt = results => `You are the independent re-reviewer of the stage B fix round. You built none of it. ${ONLY}

${COMMON}

Additional rule for you: you write only ${H}/REVIEW_STAGEB_FIX.md, lines in ${H}/BUILD_LOG.md and your own check files under /home/noob/work/bench_reads/stageBfix/review/. You change no tool and no set; you list exact fixes.

The builders' reports: ${JSON.stringify(results.map(r => r ? { done: r.done, commit: r.commit, outcome: r.outcome, owed: r.owed, summary: r.summary } : null)).slice(0, 12000)}

Check by your own commands, recording evidence:
1. U2: every view 512 x 512; the rebuilt set against the spec; the earlier review's synthetic-dump read (review/rv_fake_u2.py pattern under /home/noob/work/bench_reads/stageB/review/) now ends rc 0 on the new build; roots, U4, U5 lists unchanged (md5); udev_infer has one dump root per set family; PREP.md read lines correct; nothing armed.
2. U1 rule text is in B3.md as the lead worded it, dated before any LOSO-2 run exists (check that no LOSO-2 experiment or dump exists).
3. Pack guard: a root that contains a pack stem is refused; the masks script refuses an unfilled sheet and handles both sheet formats on a synthetic filled copy; the user's own files are untouched (md5 of results.csv and results_short.csv unchanged from their state before the round, if a record exists, else unfilled).
4. Read tools: with the option off, the W1-G read output is byte-identical to the stored one; with the 4 excluded stems the 528-cell values are right (recompute one headline value by your own script); the crack-free definition and n are printed and the explanation of n = 303 is correct; the OP-C class lines are printed.
5. Class-bias variant 2: rule written before the run (file times and log), cross-fitting intact (planted-leak test as in the first review), numbers recomputed for one seed, variant 1 untouched.
6. Same-cell audit: the matcher's calibration is honest (known pairs found, the lead's rejected pairs rejected), the candidate list covers all same-source cross-fold pairs, the contact sheet holds pool images only, no split or list was changed.
7. Hygiene: full pytest on bench_b; no change outside bench_b, /home/noob/work/bench_udev, /home/noob/work/bench_reads/stageBfix, ${T}; bench_wt_w2 untouched and clean.
Write ${H}/REVIEW_STAGEB_FIX.md: per item PASS, PASS WITH NOTE or FAIL with the exact fix, the evidence, and a final table "product or number, rule, outcome, may the lead rely on it". Return pass=true only if no item fails.`

phase('Build')
const results = []
for (const t of TASKS) {
  const r = await agent(buildPrompt(t), { label: `build:${t.key}`, phase: 'Build', model: 'opus', effort: 'high', schema: SCHEMA })
  results.push(r)
}
phase('Review')
const rev = await agent(reviewPrompt(results), { label: 'review:stageBfix', phase: 'Review', model: 'opus', effort: 'high', schema: REVIEW_SCHEMA })
return { builds: results.map((r, i) => ({ key: TASKS[i].key, done: !!(r && r.done), commit: r ? r.commit : '', outcome: r ? r.outcome : 'no return', owed: r ? r.owed : '' })), pass: !!(rev && rev.pass), per_item: rev ? rev.per_item : '', reasons: rev ? rev.reasons : 'reviewer did not return' }
