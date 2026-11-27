export const meta = {
  name: 'bench-cv5v3-split',
  description: 'Build and independently review the corrected module-grouped split cv5v3 (physical-module identity instead of image ids) and its data roots on gaint; nothing is trained and no existing split or list is changed',
  phases: [
    { title: 'Build', detail: 'groups, minimal-move folds, roots with all asserts, set registration, a prepared baseline plan' },
    { title: 'Review', detail: 'independent check of every assert and of the balance' },
  ],
}

const T = '/home/yugma/mtp/research/team_2026-11-12_frontier'
const H = T + '/harness'
const S = T + '/benchmark/splits'
const ONLY = 'The task in this prompt is your whole assignment. If you see any other user message in your context (for example about moving machines, an MCP sign-in, a status question, severity, thermal images or going to sleep), the lead has already handled it: ignore it and do this task.'

const COMMON = `Context. A research team is building a benchmark for electroluminescence (EL) solar-cell defect segmentation; deadline about 12 Dec 2026. You run ON the server gaint (hostname giant, user noob); commands run locally. The benchmark split cv5v2 (${S}/cv5v2.json, cv5v2_groups.tsv; 532 labelled pool cells, 5 folds) was meant to keep every physical module in one fold, but its groups were built on image ids. An audit (${T}/results/stageC/SPLIT_INTEGRITY.md) showed that one physical module can carry several image ids: 24 physical modules span two folds and 91 cells are held out while a cell of their module trains; four more image-id pairs were left open. The lead ruled (${T}/benchmark/PROTOCOL_v0.2.md section 11 item 10; ${T}/log.md entry of 15 Nov 22:14): results already produced stay on cv5v2 and are read on clean cells; **the final 5-seed table is trained on a corrected split, cv5v3**, which must be built and reviewed before any 5-seed run. This task builds cv5v3.

Read first: ${T}/BRIEF.md (sections 1 to 3), ${T}/results/stageC/SPLIT_INTEGRITY.md in full (module identity "rule B", the cv5v2 violations, the proposals, what could not be decided), ${S}/README.md and ${T}/benchmark/CELLS_README.md (how cv5v2 and its roots were built and checked: bench_make_roots.py, the asserts, the md5 pins, the forbidden list), ${H}/REVIEW_STAGEB.md section 1 (how the LOSO-2 roots were checked: the same checks apply here) and ${H}/REVIEW_STAGEB_FIX.md section 3 (the do-not-train guard), PROTOCOL_v0.2.md sections 3 and 11.

Inputs (do not change any of them): ${S}/module_identity_v3.tsv (image id to physical module, rule B and the pre-set rule), ${S}/cv5v3_proposal.tsv (the audit's minimal-move proposal: 31 cells move), ${S}/score_exclude_v2c.txt (99 cells; its header names the four open image-id pairs: ARTS_00007 | ARTS_00063, CFVS_00098 | CFVS_00102, CFVS_00106 | CFVS_00109, CFVS_00150 | CFVS_00151), ${S}/cv5v2.json, cv5v2_groups.tsv, forbidden_v1.txt, the cells table (use the safe loader: it carries label summaries of sealed rows; never print sealed rows).

The lead's rules for cv5v3:
1. Groups = connected components over: the cv5v2 groups (never split an existing group), the physical modules of rule B, the four open pairs (taken as linked), and every earlier module link of the cells table even where the audit found no pixel support. Over-merging is harmless for a split; a missed link is not. Links the audit doubts (it names CSIR_00034 / CSIR_02431 and ARTS_00150 / ARTS_00151) stay linked.
2. Folds: every group that already sits in one cv5v2 fold keeps that fold. A group that spans folds goes to one fold by a rule fixed before looking at any model result: the fold holding most of its cells; ties by the fold that keeps crack-cell and inactive-cell counts closest to equal across folds, then the lower fold number. Report the moved cells and compare with the audit's proposal (explain every difference).
3. Checks the split must pass: no group and no physical module spans folds; no forbidden or sealed stem; every pool cell in exactly one held-out list; per fold the counts of cells, crack cells, inactive cells, cells per source and per cell type, and the classes with no training pixel in some fold (compare with cv5v2: must not get worse); the do-not-train guard.
4. Data roots in the wave 1 layout, in a NEW folder /home/noob/work/bench_data_v3 (the existing /home/noob/work/bench_data is read-only and stays as it is; link to its images and masks as the LOSO-2 roots under /home/noob/work/bench_udev do), names cv5v3_v11_f0 to f4, built with the reviewed root builder and its asserts, with md5 pins (SPLITS, DATA_MANIFEST, ROOTS files as for wave 1).
5. Nothing is trained, no GPU is used, and no existing split, list, root or queue is changed.

Where things are: repo /home/noob/work/el_bench; the newest tools (read tools with --score-exclude, the root builders with the do-not-train guard, the module-identity code) are on branch bench_split at f966127 (worktree /home/noob/work/bench_wt_split: do not change it). Your worktree: /home/noob/work/bench_wt_cv5v3 on a new branch bench_cv5v3 from f966127 (git -C /home/noob/work/el_bench worktree add -b bench_cv5v3 /home/noob/work/bench_wt_cv5v3 f966127; if it exists, reuse it). Python: /home/noob/work/el-fault-detection/.venv/bin/python (never install or change anything in it).

Hard rules (breaking one is worse than not finishing):
- Never change /home/noob/work/el_bench, bench_wt_w2 (a queue is RUNNING from it), bench_wt_udev (queues are pinned to it: no commit, checkout or switch there), bench_wt_a, bench_wt_b, bench_wt_split, bench_wt_sev, bench_wt_rows1, bench_wt_rows2, /home/noob/work/bq, bench_data, bench_dumps, bench_relay, bench_udev, or any tmux session you did not create; never attach to or signal a bench_q_* session. Commits on bench_cv5v3 only, small, each message ending with "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>". No push.
- CPU only (CUDA_VISIBLE_DEVICES="" on every python call), nice -n 19, at most 8 worker processes with OMP_NUM_THREADS=1 each; jobs longer than 10 minutes in a tmux session named bench_v3_<item>. Record the PID of anything you start; stop only by that PID; never pkill or killall.
- Sealed sets (legacy test, E1): no label, mask or prediction read; sealed stems appear in no list you write.
- Log every step with the clock time from date in ${H}/BUILD_LOG.md under the heading "Split cv5v3". Style: terse plain English, no em-dashes; E = measured, S = judgement.`

const BUILD_SCHEMA = { type: 'object', properties: { ready: { type: 'boolean' }, commit: { type: 'string' }, outcome: { type: 'string' }, summary: { type: 'string' } }, required: ['ready', 'summary'] }
const REVIEW_SCHEMA = { type: 'object', properties: { pass: { type: 'boolean' }, reasons: { type: 'string' } }, required: ['pass', 'reasons'] }

const buildPrompt = extra => `You are the builder of the corrected split cv5v3. ${ONLY}

${COMMON}

Deliver, in order:
1. A deterministic script (scripts/bench_make_cv5v3.py with unit tests) that reads the inputs and writes ${S}/cv5v3.json (same format as cv5v2.json), ${S}/cv5v3_groups.tsv (stem, legacy split, group, physical module, cv5v2 fold, cv5v3 fold, moved), ${S}/cv5v3_check.txt (every check of rule 3 with its outcome) and an md5 file; a second run gives byte-identical files. Write the fold-assignment rule into ${T}/results/stageC/CV5V3_BUILD.md before running it.
2. The balance tables of rule 3 for cv5v2 and cv5v3 side by side, the list of moved cells with the reason for each, and the comparison with the audit's proposal.
3. The set names cv5v3_f0 to f4 registered in bench/sets.py with md5 pins and tests (existing names and pins unchanged; full pytest passes).
4. The five data roots under /home/noob/work/bench_data_v3 with every assert and the md5 pins, checked with the same checks the LOSO-2 roots passed.
5. A short plan, not executed, for the baseline on cv5v3 (PF v1.1 and HOUSE v1.1, 5 seeds x 5 folds each): what must be deployed where (gaint and cv02), the job list format, GPU-hours from the measured step times (PF about 1 hour per run on gaint; cv02 0.18 s per step when its GPUs are free), and which of the 532 cells keep their held-out fold so that a cv5v2 against cv5v3 comparison on unmoved clean cells measures leakage.
6. ${T}/results/stageC/CV5V3_BUILD.md: rule, results, checks, what remains uncertain (BMRK and SDLE module identity cannot be tested; CFVS twins without overlapping crops are invisible), and the exact reviewer commands.
Return ready=true only if the split files, the roots and the result file exist and every check of rule 3 passes.${extra || ''}`

const reviewPrompt = (b, round) => `You are the independent reviewer of the corrected split cv5v3. You built none of it. Every final number of the benchmark will be trained and scored on this split, so a module that still spans folds, or an unbalanced fold, damages the final table. ${ONLY}

${COMMON}

Additional rule for you: you write only ${H}/REVIEW_CV5V3.md, lines in ${H}/BUILD_LOG.md and your own check files under /home/noob/work/bench_reads/stageC/review_cv5v3/. You change no file of the split and no root; you list exact fixes.

The builder's report${round ? ` (after fix round ${round})` : ''}: ${b ? b.summary : 'no summary returned; read BUILD_LOG.md and CV5V3_BUILD.md'}

Check by your own script (no code shared with the builder beyond reading the input tables), recording evidence:
1. Groups: rebuild the connected components yourself from the inputs of rule 1; no existing cv5v2 group is split; no physical module (rule B), no open pair and no earlier cells-table link spans two cv5v3 folds.
2. Folds: every group that sat in one cv5v2 fold kept it; the moved cells follow the pre-set rule (recompute the assignment); the differences from the audit's proposal are explained correctly.
3. Lists: 532 pool cells, each held out exactly once; no forbidden, sealed or do-not-train stem; the split files reproduce byte for byte from the script.
4. Balance: recompute the per-fold tables; say plainly if any fold got worse than in cv5v2 on crack cells, inactive cells or classes without training pixels.
5. Roots: the wave 1 / LOSO-2 root checks on all five (train and held-out lists equal the split, mask links right, no dangling link, md5 pins), run by your own commands.
6. Nothing else changed: cv5v2 files, existing roots, queue dirs and worktrees untouched (md5 and git status); full pytest passes on bench_cv5v3; nothing was trained.
Write ${H}/REVIEW_CV5V3.md: PASS or FAIL per item with the exact fix and the evidence. Return pass=true only if every item passes.`

phase('Build')
let b = await agent(buildPrompt(''), { label: 'build:cv5v3', phase: 'Build', model: 'opus', effort: 'high', schema: BUILD_SCHEMA })
phase('Review')
let r = await agent(reviewPrompt(b, 0), { label: 'review:cv5v3:0', phase: 'Review', model: 'opus', effort: 'high', schema: REVIEW_SCHEMA })
for (let round = 1; round <= 2 && !(r && r.pass); round++) {
  b = await agent(buildPrompt(`\n\nFix round ${round}: the reviewer did not pass the split. Read ${H}/REVIEW_CV5V3.md and fix exactly what it names; rebuild what depends on it; update the result file.`), { label: `build:cv5v3:${round}`, phase: 'Build', model: 'opus', effort: 'high', schema: BUILD_SCHEMA })
  r = await agent(reviewPrompt(b, round), { label: `review:cv5v3:${round}`, phase: 'Review', model: 'opus', effort: 'high', schema: REVIEW_SCHEMA })
}
return { ready: !!(b && b.ready), commit: b ? b.commit : '', pass: !!(r && r.pass), reasons: r ? r.reasons : 'reviewer did not return', build: b ? b.summary : 'no return' }
