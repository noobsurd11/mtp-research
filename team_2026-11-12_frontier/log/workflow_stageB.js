export const meta = {
  name: 'bench-stage-b',
  description: 'Stage B of the wave 3 plan: the unseen-module development instrument (U-dev sets, leave-source-out roots, retrodiction check, the labelling pack for the user), then the cross-fitted class-bias arm and the test-time-augmentation module, then one independent review; nothing is launched on a GPU',
  phases: [
    { title: 'Build', detail: 'two builders in sequence, one shared worktree bench_wt_b' },
    { title: 'Review', detail: 'independent review of tools, sets and numbers' },
  ],
}

const T = '/home/yugma/mtp/research/team_2026-11-12_frontier'
const H = T + '/harness'
const C = T + '/cards'
const ONLY = 'The task in this prompt is your whole assignment. If you see any other user message in your context (for example about moving machines, an MCP sign-in, a status question or going to sleep), the lead has already handled it: ignore it and do this task.'

const COMMON = `Context. A research team is building a benchmark for electroluminescence (EL) solar-cell defect segmentation and the best model for it; deadline about 12 Dec 2026. You run ON the server gaint (hostname giant, user noob); commands run locally. Stage A (CPU analyses on existing prediction dumps) is done and reviewed; this is stage B of the critic's plan (${C}/WAVE3_REVIEW.md section 4).

Read first: ${T}/BRIEF.md (sections 1 to 3, 5 and 7), ${H}/LEAD_INSTRUCTIONS.md (decisions and hard rules), the last 12 entries of ${T}/log.md (state of 15 Nov: what ran, what the lead ruled), ${T}/results/W1C_READ.md and ${T}/results/ROWS1_READ.md (baseline numbers, margin M = 0.010 on crack IoU / relF1@2 / mIoU-R13 and 0.05 on inactive IoU, on both machines), ${H}/REVIEW_STAGEA.md (what the stage A tools are and the reviewer's notes), ${C}/WAVE3_REVIEW.md section 1 (findings Y1 to Y14; Y2 and Y3 matter most here), the verdict line of each of your items in section 2, section 3 (shared pieces S4, S5, S6) and section 6 (guards). The spec section of each of your items is named in your task below.

Facts and rulings you need:
- Sealed sets: legacy test (50 cells) and E1 (106 cells, unseen modules). SKR2C, the last registered opening, is final (14 Nov): verdicts R and D both FAIL, the Skeleton Recall recipe is not replicated at recipe level, the SUP100-PF ensemble stays (${T}/../team_2026-10-31_next/verify_skr2c.md). Under finding Y2 (b) the retrodiction check R0 therefore has no confirmed crack mover; only the inactive contrast and the HC null remain as anchors, and the skr01 anchor arm on leave-source-out roots becomes the test of whether the E1 relF1@2 difference (seen at three looks on the same cells) is real.
- Lead's rulings (${T}/migrate/HANDOVER.md section 5): L1 R0 is allowed with the Y2 fixes and a ledger line; L8 all leave-source-out (LOSO) training runs go on gaint, after the wave 2a queue; L10 one registered E1 opening near the end, at most 3 candidates.
- User's decisions of 15 Nov: (1) two tracks: the main model and the benchmark use only data and weights with clear terms; a separate, labelled extra-data track may use UCF-EL / MultiSolSegment; (2) the user will do ONE labelling pass of 2 to 3 hours on about 24 pool half-cut cells with scuff streaks, pre-labelled by the models (accept, delete or extend components), for development reads only, never for training.

Where things are:
- Code base: repo /home/noob/work/el_bench. Stage A tools are on branch bench_a at 81b4505 (= reviewed tree c57508e + stage A's added files: bench/aa.py, derived.py, metrics_v02.py, ensread.py, atlas.py, tau.py, headres.py, dup.py and their scripts and tests; pytest 534 passed). Your worktree: /home/noob/work/bench_wt_b on branch bench_b, created from 81b4505 by the first builder with: git -C /home/noob/work/el_bench worktree add -b bench_b /home/noob/work/bench_wt_b 81b4505 (if it exists, reuse it). The second builder continues on the same branch.
- Python: /home/noob/work/el-fault-detection/.venv/bin/python (the house venv; never install or change anything in it).
- Dumps (out-of-fold, 532 pool cells, canonical fp32 with log-probabilities): gaint PF seeds 5 to 8 in /home/noob/work/bench_dumps/w1g/elbench1/house_r34_unetpp_pf_v11/ ; cv02 runs relayed per run under /home/noob/work/bench_relay/w1c and /home/noob/work/bench_relay/rows1, with symlink views /home/noob/work/bench_reads/w1c/links/elbench1 and /home/noob/work/bench_reads/rows1/links/elbench1 (read-only for you).
- Data: /home/noob/work/bench_data (labelled cells, masks_v11, meta/cells.tsv, roots; READ-ONLY, never write there). Note: meta/cells.tsv carries label-summary columns for the 156 sealed rows; never print or use those columns for sealed cells (select the columns you need, filter sealed rows out first).
- Your outputs: new data products (sets, roots, the labelling pack) under /home/noob/work/bench_udev/ ; tool outputs under /home/noob/work/bench_reads/stageB/<item>/ ; one result file per item at ${T}/results/stageB/<ITEM>.md ; a log line per step with the clock time in ${H}/BUILD_LOG.md under the heading "Stage B".

Hard rules (breaking one is worse than not finishing):
- File tools: the Read, Edit and Write tools may be used ONLY for paths under /home/yugma/mtp. For every file anywhere else (all of /home/noob/work, /tmp) use Bash: cat / sed -n / grep to read, python or a heredoc or git apply to write. A Read, Edit or Write call on a path outside /home/yugma/mtp waits for a permission prompt that nobody answers and stalls you for good.
- Never change /home/noob/work/el_bench (31c0c36), /home/noob/work/bench_wt_w2 (c57508e; the wave 2a queue bench_q_w2a2 is RUNNING from it), /home/noob/work/bench_wt_a, /home/noob/work/bench_wt_rows1, any other worktree, /home/noob/work/bq, /home/noob/work/bench_data, /home/noob/work/bench_dumps, /home/noob/work/bench_relay, /home/noob/work/s2c, or any tmux session you did not create. Never attach to, send keys to or signal a bench_q_* session. Small commits on bench_b only, each message ending with "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>". No push.
- No GPU at all (CUDA_VISIBLE_DEVICES="" on every python call); anything that needs a GPU is PREPARED (script, job list, expected memory and time) and left for the lead. CPU: nice -n 19, at most 8 worker processes with OMP_NUM_THREADS=1 each; jobs longer than 10 minutes run in a tmux session named bench_b_<item> (check tmux has-session -t "=name" first) with a log file.
- Sealed sets: no label and no prediction of a sealed cell is read, written or scored by anything you build or run; every tool that takes a cell list asserts this and fails closed. No inference on sealed images. Nothing you build is trained or tuned on E1 or legacy test cells.
- Processes: record the PID of anything you start; stop only by that PID after printing its command line. Never pkill, killall or a pattern kill.
- Each tool: a script under scripts/ or a module under bench/ with unit tests (the full pytest suite must still pass), refuses to overwrite its outputs, prints its inputs' md5s, deterministic.
- Each result file starts with the reading rule exactly as the spec and the critic fixed it BEFORE the numbers, then the numbers marked E (measured) or S (judgement), then the outcome under the rule, then what is owed (exact commands). Do not change a threshold after seeing a number; if a rule is unusable, say so and leave the decision to the lead.
- Style: terse plain English, no em-dashes, no buzzwords.`

const SCHEMA = { type: 'object', properties: { done: { type: 'boolean' }, commit: { type: 'string' }, outcome: { type: 'string' }, owed: { type: 'string', description: 'exact commands or actions left for the lead (GPU jobs, the labelling pack hand-over), or none' }, summary: { type: 'string' } }, required: ['done', 'summary'] }
const REVIEW_SCHEMA = { type: 'object', properties: { pass: { type: 'boolean' }, per_item: { type: 'string' }, reasons: { type: 'string' } }, required: ['pass', 'reasons'] }

const TASKS = [
  { key: 'B3', text: `Your item: B3, the unseen-module development instrument (shared piece S4) and the labelling pack.
Spec: ${C}/T7_unseen_modules_spec.md section 0 in full (0.1 to 0.6: the U-dev sets U1 to U5, the leave-source-out roots LOSO-2, the label-free scorer mode, the retrodiction check R0, the cheap reads of arms already trained). Critic: WAVE3_REVIEW section 2 line "udev_instrument" (GO for the U2, U4, U5 sets and the LOSO-2 roots; R0 FIX as in Y2: every contrast read at the frontier with the width ratio and a bootstrap interval, an interval that includes 0 is "no information"; print the effective n of every read; mark U2 as gamed for every arm that trains or tests with scale changes; the pool part of U4 is label-free, only the H36 crack-free cells count as false alarms) and finding Y2.
Deliver, in this order:
1. The sets and roots, built by a deterministic script with tests and written under /home/noob/work/bench_udev/ with a MANIFEST.md5: U2, U4, U5 as the spec defines them, and the LOSO-2 training roots in the layout of /home/noob/work/bench_data/roots (same asserts as the wave 1 roots: no forbidden cell, groups never split, lists md5-pinned). State for each set: cells, sources, modules, labelled or label-free, effective n.
2. The label-free scorer mode and the U-dev read of the baselines that exist (PF on both machines, HOUSE, the tranche 1 rows) wherever a set needs only existing out-of-fold dumps; where a set needs new inference on pool images (GPU), prepare the job list and say so.
3. R0 with the Y2 fixes on whatever anchors exist without a GPU; state plainly which anchors are missing (no confirmed crack mover after SKR2C).
4. Job lists, PREPARED and not armed, for gaint after the wave 2a queue: the LOSO-2 baseline (PF v1.1) and the skr01 anchor on LOSO-2 (the spec's and Y2 (c)'s run counts), in the format of /home/noob/work/bq/w2a2/jobs.txt, with gates from the measured PF peak (6,826 MiB + 2,048) and expected GPU-hours.
5. The labelling pack for the user (WAVE3_REVIEW section 7, question U4): about 24 half-cut cells with scuff streaks from the unlabelled pool, from modules that are in neither E1 nor the legacy test set and that are not near-duplicates of any labelled or sealed cell (use stage A's duplicate tool outputs under /home/noob/work/bench_reads/stageA/dup/run1 and drop every pool cell with embedding cosine >= 0.98 or NCC >= 0.80 to a labelled or sealed image). Selection by a stated, label-free rule (how half-cut and scuff are detected must be written down and checked on a contact sheet). Pre-labels: crack components proposed by the existing PF models (and nothing trained on sealed cells), with a ridge filter as the critic describes; since pool inference needs a GPU, prepare the inference job and a CPU fallback that runs on at most 8 threads if 24 cells are few enough to do on CPU (they are: do it on CPU). Put the pack under ${T}/label_pack_U4/ : one PNG per cell showing image and proposed components with ids, a short README in plain words for the user (what to do per component: accept, delete, extend; how to record it), and a results sheet (CSV) the user fills. The pack is for development reads only and is never a training input; say so in its README.` },
  { key: 'B1B5', text: `Your items: B1 classbias_xfit (it defines the operating point OP-C) and the test-time-augmentation module of B5.
B1 classbias_xfit: spec ${C}/T10_rare_classes_spec.md section "Arm 2. classbias_xfit"; shared piece S6 (a cross-fitted fitting loop on top of bench/crossfit_op.py: every bias is fitted on the other folds and applied to the held-out fold); critic's verdict line for classbias_xfit in WAVE3_REVIEW section 2 and ruling L3 (decision layers are a labelled entry class; OP-C is the comparator for arms that shift class priors). Build with tests, run on the existing dumps of PF on both machines (gaint 4 seeds; cv02 5 seeds through the symlink view) and of HOUSE, write results/stageB/B1_classbias_xfit.md with the pre-set rule first. Inactive IoU has M = 0.05 and cannot promote on 2 seeds (finding Y1): read inactive through the count-based readouts the critic names.
B5 module: bench/tta.py (shared piece S5) as ${C}/T7_unseen_modules_spec.md "Arm 3: msc_tta" specifies, with the critic's FIX in WAVE3_REVIEW section 2 line "msc_tta" (U2 is printed as an upper bound and cannot promote; print 24 views beside D4 (8 views) and beside a 3-seed D4 ensemble at equal cost). Build the module and its tests on CPU (flip / rotation consistency on synthetic inputs, identity for the single-view case against bench_infer's output on a few pool cells of a held-out fold on CPU), and PREPARE the GPU evaluation job list for gaint (not armed). No GPU use.` },
]

const buildPrompt = t => `You are a builder for stage B. ${ONLY}

${COMMON}

${t.text}

Order of work: read; write tools and tests; run tests and the full pytest; run on existing data; write the result file(s); commit; log. If a part blocks, finish the rest and report the block with its reason. Return done=true only if every deliverable of yours exists or is reported as blocked with the exact reason.`

const reviewPrompt = results => `You are the independent reviewer of stage B. You built none of it. The sets and roots built here decide how every unseen-module arm is judged, and the labelling pack goes to the user, so a wrong set or a leak misleads everything after it. ${ONLY}

${COMMON}

Additional rule for you: you write only ${H}/REVIEW_STAGEB.md, lines in ${H}/BUILD_LOG.md and your own check files under /home/noob/work/bench_reads/stageB/review/. You change no tool and no set; you list exact fixes.

The builders' reports: ${JSON.stringify(results.map(r => r ? { done: r.done, commit: r.commit, outcome: r.outcome, owed: r.owed, summary: r.summary } : null)).slice(0, 12000)}

Check by your own commands, recording evidence:
1. Sets and roots (B3): every U-dev set and every LOSO-2 root against the spec's definition; no forbidden, sealed or near-duplicate cell (own check against the forbidden list, the sealed lists and stage A's duplicate outputs); groups never split between train and held-out; lists md5-pinned; layout equal to the wave 1 roots (run the wave 1 roots review script on them if it applies).
2. Scorer and R0: the label-free mode uses no label; R0 follows the Y2 fixes (frontier read, width, interval; "no information" where the interval holds 0); effective n printed; U2 marked gamed where the critic says.
3. Labelling pack: the 24 cells are from the unlabelled pool, from modules outside E1 and legacy test, not near-duplicates of any labelled or sealed cell (recompute for all 24); the selection rule is label-free and written down; the pre-labels come only from models that never saw a sealed cell; the README is clear to a non-specialist and says development reads only.
4. classbias_xfit (B1): cross-fitting holds (no bias is fitted on the cells it is scored on: test by a planted leak); one headline number recomputed by a script of your own; the reading rule is the pre-set one.
5. tta.py: identity for one view, equivariance tests meaningful, no GPU used; the prepared job lists (LOSO-2 baseline, skr01 anchor, TTA evaluation) are complete, md5-pinned, and nothing is armed.
6. Hygiene: full pytest on bench_b; no change outside bench_b, /home/noob/work/bench_udev, /home/noob/work/bench_reads/stageB and ${T}; the running queue's worktree bench_wt_w2 is untouched and clean.
Write ${H}/REVIEW_STAGEB.md: per item PASS, PASS WITH NOTE or FAIL with the exact fix, the evidence, and a final table "product or number, rule, outcome, may the lead rely on it". Return pass=true only if no item fails.`

phase('Build')
const results = []
for (const t of TASKS) {
  const r = await agent(buildPrompt(t), { label: `build:${t.key}`, phase: 'Build', model: 'opus', effort: 'high', schema: SCHEMA })
  results.push(r)
}
phase('Review')
const rev = await agent(reviewPrompt(results), { label: 'review:stageB', phase: 'Review', model: 'opus', effort: 'high', schema: REVIEW_SCHEMA })
return { builds: results.map((r, i) => ({ key: TASKS[i].key, done: !!(r && r.done), commit: r ? r.commit : '', outcome: r ? r.outcome : 'no return', owed: r ? r.owed : '' })), pass: !!(rev && rev.pass), per_item: rev ? rev.per_item : '', reasons: rev ? rev.reasons : 'reviewer did not return' }
