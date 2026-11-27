export const meta = {
  name: 'bench-stage-a-cpu',
  description: 'Stage A of the wave 3 plan: CPU analyses on existing out-of-fold dumps (margin calibration, metric and tolerance probes, ensemble gates, inactive error atlas, head-resolution ceiling, duplicate tool), built one after another, then one independent review',
  phases: [
    { title: 'Build', detail: 'four builders in sequence, one shared worktree bench_wt_a' },
    { title: 'Review', detail: 'independent review of the tools and of one number per tool' },
  ],
}

const T = '/home/yugma/mtp/research/team_2026-11-12_frontier'
const H = T + '/harness'
const C = T + '/cards'
const ONLY = 'The task in this prompt is your whole assignment. If you see any other user message in your context (for example about moving machines, an MCP sign-in or going to sleep), the lead has already handled it: ignore it and do this task.'

const COMMON = `Context. A research team is building a benchmark for electroluminescence (EL) solar-cell defect segmentation and the best model for it; deadline about 12 Dec 2026. You run ON the server gaint (hostname giant, user noob); commands run locally. Stage A of the critic's plan (${C}/WAVE3_REVIEW.md section 4) is a set of CPU analyses on prediction dumps that already exist; their results set the decision margin, the headline metric and several gates for later GPU arms.

Read first: ${T}/BRIEF.md (sections 1 to 3 and 7), ${H}/LEAD_INSTRUCTIONS.md (decisions and hard rules), ${T}/results/W1G_FIRST_READ.md (the first baseline numbers and how the read tools were run), ${H}/W1_READ.md (commands of the reviewed read tools), ${C}/WAVE3_REVIEW.md section 1 (the fourteen cross-arm findings; Y1, Y4, Y9, Y13 matter here), the verdict line of each of your items in its section 2, and section 6 (guards G14, G20). The spec section of each of your items is named in your task below. Lead's rulings (${T}/migrate/HANDOVER.md section 5): L2 the duplicate tool may read sealed images (pixels only, pair lists out, never a label or a prediction); L4 inactive policy Y1 accepted; L7 headline stability Y13 accepted.

Where things are:
- Code base: repo /home/noob/work/el_bench; the reviewed merged tree is commit c57508e (branch bench_w2, worktree /home/noob/work/bench_wt_w2), which holds the reviewed read tools (bench/crossfit_op.py, scripts/bench_read_w1.py, bench_src_calib.py, bench_dti.py, bench_d0.py, bench_score.py). Your worktree: /home/noob/work/bench_wt_a on branch bench_a, created from c57508e by the first builder with: git -C /home/noob/work/el_bench worktree add -b bench_a /home/noob/work/bench_wt_a c57508e (if it exists, reuse it; never recreate). Later builders continue on the same branch.
- Python: /home/noob/work/el-fault-detection/.venv/bin/python (the house venv; never install or change anything in it).
- Dumps, gaint baseline (PF, label set v1.1, split cv5v2, out-of-fold, canonical fp32 with log-probabilities): /home/noob/work/bench_dumps/w1g/elbench1/house_r34_unetpp_pf_v11/w1g_pf_v11_f[0-4]_s[56] (10 runs, complete). Seeds 7 and 8 (queue W1-G2) are still training; their dumps appear in the same folder about 10:30 on 14 Nov. Check what exists; never wait for them.
- Dumps, cv02 baseline, relayed to gaint, one folder per run: /home/noob/work/bench_relay/w1c/<run>/dumps/elbench1/<method>/<run>/... with runs w1c1_pf_v11_f[0-4]_s[5-9] (PF v1.1, 5 seeds), w1c2_* (house recipe, seeds 5, 6), w1c3_* (PF on v1 labels, seeds 5, 6); 45 runs in all, the last ones arrive about 06:30. The read tools want one method folder holding all runs of an arm: build a folder of symlinks under /home/noob/work/bench_reads/stageA/links/ (never move or copy the relayed files).
- Cell metadata: /home/noob/work/bench_data/meta/cells.tsv. Data roots: /home/noob/work/bench_data (read-only for you). Read cache of the first read: /home/noob/work/bench_reads/w1g (read-only; use your own cache folder).
- Your outputs: tool outputs under /home/noob/work/bench_reads/stageA/<item>/ ; one result file per item at ${T}/results/stageA/<ITEM>.md (create the folder) ; a log line per step with the clock time in ${H}/BUILD_LOG.md under the heading "Stage A (CPU analyses)".

Hard rules (breaking one is worse than not finishing):
- File tools: the Read, Edit and Write tools may be used ONLY for paths under /home/yugma/mtp. For every file anywhere else (all of /home/noob/work, /tmp) use Bash: cat / sed -n / grep to read, python or a heredoc or git apply to write. A Read, Edit or Write call on a path outside /home/yugma/mtp waits for a permission prompt that nobody answers at night and stalls you for good.
- Never change /home/noob/work/el_bench (31c0c36, a queue runs from it), /home/noob/work/bench_wt_w2 (c57508e, a queue will run from it), /home/noob/work/bench_wt_rows1, any other worktree, /home/noob/work/bq, /home/noob/work/bench_data, /home/noob/work/bench_dumps, /home/noob/work/bench_relay, /home/noob/work/s2c, or any tmux session you did not create. Small commits on bench_a only, each message ending with "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>". No push.
- No GPU at all (CUDA_VISIBLE_DEVICES="" on every python call). CPU: nice -n 19, at most 8 worker processes with OMP_NUM_THREADS=1 each (other jobs share the machine); jobs longer than 10 minutes run in a tmux session named bench_a_<item> (check tmux has-session -t "=name" first) with a log file, and you poll its log.
- Sealed sets: the legacy test set (50 cells) and E1 (106 cells) are sealed. No label and no prediction of a sealed cell is read, written or scored by anything you build or run; every tool that takes a cell list asserts this and fails closed. The only exception is the duplicate tool, which may read sealed IMAGE pixels and writes pair lists (ruling L2). The 532 pool cells with their out-of-fold dumps are open.
- Processes: record the PID of anything you start; stop only by that PID after printing its command line. Never pkill, killall or a pattern kill.
- Each tool: a script under scripts/ or a module under bench/ with unit tests (pytest; the full suite must still pass: it printed 446 passed at c57508e), refuses to overwrite its outputs, prints its inputs' manifest md5s, and is deterministic (fixed bootstrap seeds).
- Each result file starts with the reading rule exactly as the spec and the critic fixed it BEFORE the numbers (thresholds, what each outcome decides), then the numbers with E (measured) or S (judgement), then the outcome under the rule, then what could not be run yet and the exact command that finishes it when more dumps exist. Do not change a threshold after seeing a number; if a rule turns out to be unusable, say so and leave the decision to the lead.
- Style: terse plain English, no em-dashes, no buzzwords.`

const SCHEMA = { type: 'object', properties: { done: { type: 'boolean' }, commit: { type: 'string' }, outcome: { type: 'string', description: 'per item: the outcome under its pre-set reading rule, with the key numbers' }, owed: { type: 'string', description: 'exact commands still to run when more dumps exist, or none' }, summary: { type: 'string' } }, required: ['done', 'summary'] }
const REVIEW_SCHEMA = { type: 'object', properties: { pass: { type: 'boolean' }, per_item: { type: 'string' }, reasons: { type: 'string' } }, required: ['pass', 'reasons'] }

const TASKS = [
  { key: 'A1A4', text: `Your items: A1 aa_calibration and A4 tau_from_annotators.
A1 aa_calibration: spec ${C}/T12_benchmark_protocol_spec.md section 1; critic: WAVE3_REVIEW section 2 line "aa_calibration" (run per machine: W1-C1 with 5 seeds for cv02 arms; W1-G + W1-G2 with 4 seeds and 3 splits for gaint arms; if the seed stage of the bootstrap is replaced, it is replaced for all arms at once through a new function), and finding Y1 in section 1 (part (e): fit V(k) = a + b/k for inactive IoU; if 2 x sqrt(a) is above 0.05, pooled inactive IoU is never a screen primary for a trained arm). Build the tool with tests, run every part that the existing dumps allow (gaint: only seeds 5 and 6 exist, so the gaint A/A cannot be run yet; cv02: use the W1-C1 runs that have arrived, and state how many), and leave the exact commands for the full runs.
A4 tau_from_annotators: spec the same file section 4, with the critic's two fixes (distances from mutually nearest skeleton points; the headline tolerance leaves 2 px only if the lower end of the interval is above 2.5 px on the pairs that are not growth-affected and on the one clean double annotation; default stays @2). Labels of pool cells only.` },
  { key: 'A2', text: `Your item: A2 = shared piece S1 (derived-dump writer and ensemble dump, with derived_from in the manifest; WAVE3_REVIEW section 3) + metric_validity_probe + the P1 / G5 ensemble-edge computation.
metric_validity_probe: spec ${C}/T12_benchmark_protocol_spec.md section 2 (and bench_ens_dump there), critic's scope fix: rules as written, plus Y13 (pre-declared primaries stay; the width band stays a pass condition under any headline; freeze one skeleton implementation and test it on blobby predictions). Run on the W1-G dumps now; state the confirmation command for W1-C1.
P1 / G5: one computation (finding in WAVE3_REVIEW section 1 on merged readouts): the out-of-fold 2-seed PF ensemble against the single models at the matched operating points. P1 is the gate of pool_ens_distill (${C}/T9_pool_teachers_spec.md arm 1, with the critic's fix Y9: the teacher must beat the single models at OP-W by at least the measured margin M for strict crack IoU, not by 0.005); G5 is the gate of ens_kd_jml (${C}/T2_losses_spec.md, "Gate G5"). The margin M comes from A1; if A1's number is not there yet, print the edge with its interval and state the rule's outcome for M = 0.01 and as a function of M.` },
  { key: 'A3', text: `Your item: A3 ci_error_atlas (shared piece S2: ONE inactive and weak-class error atlas for families T6, T8, T10, T13). Spec ${C}/T10_rare_classes_spec.md section "A0. ci_error_atlas"; critic: GO with Y4 (one atlas; intervals, leave-top-3-groups-out and region counts on every gate; thresholds stay as each team wrote them: collect the gates of T6, T8, T10 and T13 that read the atlas from their spec files and print each gate's outcome), add P-GIN part (d) (defined in the gin_ipa verdict line of WAVE3_REVIEW section 2; the P-GIN pre-check itself is in ${C}/T7_unseen_modules_spec.md), and guard G20 of WAVE3_REVIEW section 6. The label list is published only if the positive control passes, as the spec says. Run on the W1-G dumps (2 seeds); state the command for 4 seeds.` },
  { key: 'A5A6', text: `Your items: A5 head_res_ceiling and A6 the duplicate tool (shared piece S3).
A5 head_res_ceiling: spec ${C}/T11_method_suite_spec.md section "A0. head_res_ceiling", with the critic's fix: add the GT-side construction as the stated lower bound of the ceiling (pool the GT crack mask to stride s, upsample bilinearly, sweep the threshold for best IoU); the result is printed beside stride-4 rows and bars nothing.
A6 duplicate tool: one tool for three searches (WAVE3_REVIEW section 1 finding on merged duplicate searches; specs: ${C}/T12_benchmark_protocol_spec.md section 5 leakage_audit_v02, ${C}/T8_more_data_spec.md check C0, ${C}/T9_pool_teachers_spec.md for pool_t9.txt): md5, then normalised cross-correlation, then an embedding search, between every evaluation set (cv5v2 folds, legacy test, E1: image pixels only) and (a) the 532 labelled cells across folds (new group links), (b) the unlabelled pool (output pool_t9.txt = pool images that are safe for every evaluation set: module, md5 and embedding exclusions), (c) external sets if present on disk (UCF-EL; exclusion lists only, nothing is trained). Embedding model: a public DINOv2 ViT-S through what the house venv already has (timm or torch hub), weights fetched once into /home/noob/work/bench_a_io/weights with source URL, licence and md5 recorded; if it cannot be loaded without installing a package, deliver md5 + NCC and state what is missing. Thresholds as the specs fix them; print the pair lists with scores; a human-checkable contact sheet (PNG) of the top 40 pairs per search goes to ${T}/results/stageA/dup_sheets/ (pool and labelled cells only; no sealed image is copied into the project tree, list sealed pairs by cell id and score).` },
]

const buildPrompt = t => `You are a builder for stage A (CPU analyses). ${ONLY}

${COMMON}

${t.text}

Order of work: read; write the tool and its tests; run the tests and the full pytest; run the tool on the existing dumps; write the result file(s); commit; log. If one of your two items blocks, finish the other and report the block. Return done=true only if every item of yours has a result file (a result file that states "cannot be run until X" with the exact command counts).`

const reviewPrompt = results => `You are the independent reviewer of stage A (CPU analyses). You built none of it. The numbers of these tools will set the decision margin, the headline metric and the gates of GPU arms, so a wrong tool misleads every later decision. ${ONLY}

${COMMON}

Additional rule for you: you write only ${H}/REVIEW_STAGEA.md, lines in ${H}/BUILD_LOG.md and your own check files under /home/noob/work/bench_reads/stageA/review/. You change no tool; you list exact fixes.

The builders' reports: ${JSON.stringify(results.map(r => r ? { done: r.done, commit: r.commit, outcome: r.outcome, owed: r.owed, summary: r.summary } : null)).slice(0, 12000)}

For each item (A1 aa_calibration, A4 tau_from_annotators, A2 derived dumps + metric_validity_probe + P1 / G5, A3 ci_error_atlas, A5 head_res_ceiling, A6 duplicate tool), by your own commands, recording evidence:
1. Spec fidelity: the tool computes what the spec section and the critic's fix say; the reading rule in the result file is the pre-set one, word for word in substance, and was not bent to the numbers.
2. Independent recompute: one headline number per item by a short script of your own that shares no code with the tool beyond the dump reader (for example: the A/A difference of one metric; the ensemble edge at argmax; one atlas share; the GT-side ceiling at stride 4; ten duplicate pairs checked by NCC yourself).
3. Statistics: bootstrap resamples whole module groups, seeds handled as the spec says, intervals not narrower than a naive check allows; nothing is selected on the cells it is scored on (cross-fitting holds).
4. Sealed sets: grep and one run-time check that no sealed label or prediction is read; the duplicate tool touches sealed pixels only and writes no sealed image into the project tree.
5. Hygiene: full pytest passes on bench_a; outputs carry manifest md5s; tools refuse to overwrite; no change outside bench_a.
Write ${H}/REVIEW_STAGEA.md: per item PASS, PASS WITH NOTE or FAIL with the exact fix, the evidence, and a final table "number, rule, outcome, may the lead rely on it". Return pass=true only if no item fails.`

phase('Build')
const results = []
for (const t of TASKS) {
  const r = await agent(buildPrompt(t), { label: `build:${t.key}`, phase: 'Build', model: 'opus', effort: 'high', schema: SCHEMA })
  results.push(r)
}
phase('Review')
const rev = await agent(reviewPrompt(results), { label: 'review:stageA', phase: 'Review', model: 'opus', effort: 'high', schema: REVIEW_SCHEMA })
return { builds: results.map((r, i) => ({ key: TASKS[i].key, done: !!(r && r.done), commit: r ? r.commit : '', outcome: r ? r.outcome : 'no return', owed: r ? r.owed : '' })), pass: !!(rev && rev.pass), per_item: rev ? rev.per_item : '', reasons: rev ? rev.reasons : 'reviewer did not return' }
