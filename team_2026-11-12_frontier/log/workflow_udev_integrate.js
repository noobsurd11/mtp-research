export const meta = {
  name: 'bench-udev-integrate',
  description: 'Merge the stage B tools with the reviewed tranche 2 cards into one deploy tree for the unseen-module block on gaint, prove that no existing card changes, prepare (not arm) the leave-source-out, U-dev inference and TTA queues, run two CPU analyses from the T14 cards, then an independent review',
  phases: [
    { title: 'Build', detail: 'integrator, then the CPU analyses' },
    { title: 'Review', detail: 'independent review; nothing is armed by agents' },
  ],
}

const T = '/home/yugma/mtp/research/team_2026-11-12_frontier'
const H = T + '/harness'
const ONLY = 'The task in this prompt is your whole assignment. If you see any other user message in your context (for example about moving machines, an MCP sign-in, a status question or going to sleep), the lead has already handled it: ignore it and do this task.'

const COMMON = `Context. A research team is building a benchmark for electroluminescence (EL) solar-cell defect segmentation and the best model for it; deadline about 12 Dec 2026. You run ON the server gaint (hostname giant, user noob); commands run locally. The next GPU block on gaint, after the running wave 2a queue ends, is the unseen-module block: leave-source-out training (LOSO-2), inference on the development sets (U-dev), and test-time augmentation. Its code lives on two branches that must become one deploy tree.

Read first: ${T}/BRIEF.md (sections 1 to 3, 5, 7), ${H}/LEAD_INSTRUCTIONS.md (decisions, hard rules, the 8-item launch checklist), ${H}/REVIEW_STAGEB.md and ${H}/REVIEW_STAGEB_FIX.md in full (what stage B built, what was fixed, the notes on job lists), ${T}/results/stageB/B3.md and B5_tta_module.md (the prepared job lists and their PREP.md files under /home/noob/work/bench_udev/jobs and jobs_tta), ${H}/REVIEW_ROWS2.md (the reviewed tranche 2 tree with the skr01_pf_v11 card), ${H}/LAUNCH_REQUEST_w2a.md and ${H}/REVIEW_W2A.md (how a gaint queue is prepared, pinned and reviewed: bench/q/bench_setup.sh with Q, SES, DEPLOY, JOBS_MD5, DJOBS_MD5, REPO, MAXH), the last 10 entries of ${T}/log.md, and ${T}/benchmark/PROTOCOL_v0.2.md sections 5, 8 and 11.

Branches and trees (all in the repo /home/noob/work/el_bench; none of the existing worktrees may be changed):
- el_bench main tree 31c0c36 (wave 1). bench_wt_w2 at c57508e (wave 2a; the queue bench_q_w2a2 is RUNNING from it).
- bench_wt_a at 81b4505 (stage A tools on c57508e). bench_wt_b on branch bench_b (stage A + stage B tools + the fix round; take its HEAD as the fix-round re-review names it, and check that the re-review passed that commit).
- bench_wt_rows1 at 52e3f14 and bench_wt_rows2 at b12fca8 (benchmark row cards, the cv02 queue files, one model-factory change for DeepLab decoders; branched from 31c0c36 through d3a3280, so they do not contain the wave 2a or stage A / B code).
- Python: /home/noob/work/el-fault-detection/.venv/bin/python (never install or change anything in it). Data: /home/noob/work/bench_data (READ-ONLY). Stage B products: /home/noob/work/bench_udev/.

Hard rules (breaking one is worse than not finishing):
- Never change /home/noob/work/el_bench, bench_wt_w2, bench_wt_a, bench_wt_b, bench_wt_rows1, bench_wt_rows2, /home/noob/work/bq/w2a2 or any existing queue dir, bench_data, bench_dumps, bench_relay, s2c, or any tmux session you did not create. Never attach to, send keys to or signal a bench_q_* session. Commits only on the NEW branch named in your task, each message ending with "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>". No push.
- No GPU at all (CUDA_VISIBLE_DEVICES="" on every python call): the gaint GPU is in use by the running queue, by root's finllm process (PID 6206, never to be disturbed) and by other users. Every GPU job is PREPARED (queue dir, job list, md5 pins, gates, expected time) and left for the lead to arm. CPU: nice -n 19, at most 8 worker processes with OMP_NUM_THREADS=1 each; jobs longer than 10 minutes in a tmux session named bench_int_<item> (check tmux has-session -t "=name" first) with a log file.
- Sealed sets (legacy test 50 cells, E1 106 cells): no label and no prediction of a sealed cell is read, written or scored; no job list names a sealed set. /home/noob/work/bench_data/meta/cells.tsv carries label summaries of sealed rows: use the safe loader and never print those rows.
- Processes: record the PID of anything you start; stop only by that PID after printing its command line. Never pkill, killall or a pattern kill.
- Never open a training stdout or a metrics file of a benchmark run to read numbers; use grep -c for fixed patterns and the queues' own log lines.
- Log every step with the clock time from date in ${H}/BUILD_LOG.md under the heading "Unseen-module block: integration". Style: terse plain English, no em-dashes; E = measured, S = judgement.
- File tools (Read, Edit, Write) work under /home/yugma/mtp and /home/noob/work; if one ever waits without an answer, use Bash instead and continue.`

const SCHEMA = { type: 'object', properties: { ready: { type: 'boolean' }, commit: { type: 'string' }, outcome: { type: 'string' }, owed: { type: 'string' }, summary: { type: 'string' } }, required: ['ready', 'summary'] }
const REVIEW_SCHEMA = { type: 'object', properties: { pass: { type: 'boolean' }, per_item: { type: 'string' }, reasons: { type: 'string' }, launch_commands_ok: { type: 'boolean' } }, required: ['pass', 'reasons'] }

const integratorPrompt = extra => `You are the integrator for the unseen-module block. ${ONLY}

${COMMON}

Do this, in order, logging as you go:
1. New worktree /home/noob/work/bench_wt_udev on a new branch bench_udev: bench_b's reviewed HEAD merged with bench_rows2 b12fca8 (git -C /home/noob/work/el_bench worktree add -b bench_udev /home/noob/work/bench_wt_udev <bench_b HEAD>, then merge). Resolve conflicts by keeping both sides' additions; where both sides changed one file (tests that pin card lists, the model factory, set names), keep every behaviour of both and say exactly what you did. No behaviour of any existing card may change.
2. Proof that nothing changed, on CPU: full pytest; the flag-off 5-step identity (identity_cpu.py 962379a6, pattern in BUILD_LOG.md) of the SUP, SUPPF and PFV11 cards against a fresh git archive of 31c0c36 must print IDENTICAL; every reviewed card renders to the same config on bench_udev as on the tree it was reviewed on (wave 1 cards at 31c0c36, the seven wave 2a cards at c57508e, the five tranche 1 cards at 52e3f14, the three tranche 2 cards at b12fca8): compare the rendered config md5s; a 5-step CPU run of skr01_pf_v11 on a LOSO-2 root shows the Skeleton Recall term active and no NaN; bench_infer's plain path is byte-identical to c57508e's on a few pool cells of a held-out fold (CPU).
3. Queue dirs for gaint, PREPARED and not armed, rendered for REPO=/home/noob/work/bench_wt_udev at the final commit, in the bench_setup.sh layout (jobs.txt, MAXC, dump/jobs.txt, dump/MAXC), each with a prep script kept under ${H}/udev/ and md5 pins:
   a. /home/noob/work/bq/udev_loso2: the LOSO-2 list of stage B (8 PF v1.1 runs: 2 held-out sources x seeds 5 to 8; 4 skr01_pf_v11 runs: 2 sources x seeds 5, 6; seed-major order) and their held-out dumps (canonical fp32 with logp), MAXC 2, gates = measured peak + 2,048 MiB (PF 6,826; skr01 from the tranche 2 smoke 5,574 on cv02, so use the PF gate if in doubt and say so).
   b. /home/noob/work/bq/udev_infer: the dump-only U-dev inference list after the fix round (one dump root per set family; no shvoof line unless the fix-round re-review passed the rebuilt U2), MAXC 1.
   c. /home/noob/work/bq/udev_tta: the TTA pathfinder line first as its own tiny queue dir (udev_tta_path, MAXC 1), then the rest as B5 prepared them, re-rendered for this tree.
   For each: the exact arming command (bench_setup.sh with Q, SES, DEPLOY, JOBS_MD5, DJOBS_MD5, REPO, MAXH=120), expected GPU-hours and wall time at 2 lanes, the disk need, and the read commands that follow (U1 read per the lead's rule in B3.md: pooled 164 cells decides, per-source printed).
4. Write ${H}/LAUNCH_REQUEST_udev.md (under 120 lines): the merge (what conflicted, how resolved), the proofs of item 2 with their outputs, the three queues with md5s and commands, the order the lead should arm them in after the wave 2a queue ends, and for each item of the 8-item checklist the command a reviewer should run. Then stop. Do NOT arm anything.
Return ready=true only if the merge, the proofs and the request exist.${extra || ''}`

const analysesPrompt = `You are a builder of two CPU analyses. ${ONLY}

${COMMON}

Your branch and tree: continue on bench_udev in /home/noob/work/bench_wt_udev (the integrator created it; add files only, change no existing file; if the tree does not exist, stop and report). Your items come from the T14 cards, ${T}/cards/T14_promote_spec.md:
1. gap_census (its section 1, read it in full and build it exactly as specified there: scripts/bench_gap_census.py with unit tests on synthetic masks whose answer is known; the reading rule and its threshold as the card fixes them, written into the result file BEFORE any run; run on the gaint PF dumps of seeds 5 to 8 in /home/noob/work/bench_dumps/w1g/elbench1/house_r34_unetpp_pf_v11/, confirm on the cv02 PF dumps through /home/noob/work/bench_reads/w1c/links/elbench1). Result: ${T}/results/stageC/GAP_CENSUS.md with the buckets (interior gaps, ends, whole missed components, small components), their group-bootstrap intervals, the outcome under the card's rule, and what it implies for the arms the card names (trace_crack, clce_crack, scnp_cedice, coletra_crack, cc_dicece_crack). Do not change the rule after seeing a number.
2. label_version_strata (its section for that arm): a descriptive read of crack recall on pixels that are crack in both label versions against pixels the label revision added, on the same dumps. Result: ${T}/results/stageC/LABEL_VERSION_STRATA.md. It decides nothing and says so.
Tool outputs under /home/noob/work/bench_reads/stageC/<item>/. Full pytest must still pass. Commit on bench_udev (small commits). Return ready=true only if both result files exist or a block is reported with its exact reason.`

const reviewPrompt = (a, b, round) => `You are the independent reviewer of the unseen-module block's integration. You built none of it. Your review decides whether the lead may arm about 12 training runs and three inference queues on a shared GPU, from a tree that merges two code lines. ${ONLY}

${COMMON}

Additional rule for you: you write only ${H}/REVIEW_UDEV.md, lines in ${H}/BUILD_LOG.md and your own check files under /home/noob/work/bench_reads/stageC/review/. You change no tool, no tree and no queue dir; you list exact fixes.

The integrator's report${round ? ` (after fix round ${round})` : ''}: ${a ? a.summary : 'no summary returned; read BUILD_LOG.md and the request'}
The analyses builder's report: ${b ? b.summary : 'no summary returned'}

Review ${H}/LAUNCH_REQUEST_udev.md against the real files, each item by your own command, recording the evidence:
1. Merge: bench_udev contains bench_b's reviewed HEAD and b12fca8 as ancestors; the diff against each parent holds only the other parent's changes plus the stated conflict resolutions; no behaviour change (read every resolved hunk).
2. Identity: your own 5-step CPU identity run of PFV11 against your own archive of 31c0c36 prints IDENTICAL; rendered config md5 of every reviewed card equals its value on the tree it was reviewed on (recompute for all of them); full pytest passes.
3. skr01 on a LOSO-2 root: config differs from PF v1.1 only by the Skeleton Recall key and the data root; the loss term is active on real CPU steps.
4. Job lists: names, cards, seeds, roots (LOSO-2 roots as reviewed in REVIEW_STAGEB.md: md5 pins unchanged), gates, order, dump commands (fp32, logp, no sealed set), md5 pins, no existing experiments/<name> in the deploy tree; no shvoof line unless the fix-round re-review passed U2; nothing armed (no queue.pid, no tmux session).
5. Safety on gaint: the queue code is the reviewed one (bench/q unchanged against c57508e), the guard and the outside-process rule are in force, MAXC 2, MAXH 120; the arming commands are exact.
6. The two CPU analyses: rule written before the run, unit tests meaningful, one number per analysis recomputed by a script of your own, no sealed cell read.
Write ${H}/REVIEW_UDEV.md: PASS or FAIL per item with the exact fix, the evidence, the launch commands you checked. Return pass=true only if items 1 to 5 pass; item 6 may pass with notes.`

phase('Build')
let a = await agent(integratorPrompt(''), { label: 'build:integrate', phase: 'Build', model: 'opus', effort: 'high', schema: SCHEMA })
let b = await agent(analysesPrompt, { label: 'build:analyses', phase: 'Build', model: 'opus', effort: 'high', schema: SCHEMA })
phase('Review')
let r = await agent(reviewPrompt(a, b, 0), { label: 'review:udev:0', phase: 'Review', model: 'opus', effort: 'high', schema: REVIEW_SCHEMA })
for (let round = 1; round <= 2 && !(r && r.pass); round++) {
  a = await agent(integratorPrompt(`\n\nFix round ${round}: the reviewer did not pass the request. Read ${H}/REVIEW_UDEV.md and fix exactly what it names, redo the affected proofs, update the request.`), { label: `build:integrate:${round}`, phase: 'Build', model: 'opus', effort: 'high', schema: SCHEMA })
  r = await agent(reviewPrompt(a, b, round), { label: `review:udev:${round}`, phase: 'Review', model: 'opus', effort: 'high', schema: REVIEW_SCHEMA })
}
return { ready: !!(a && a.ready), commit: a ? a.commit : '', pass: !!(r && r.pass), reasons: r ? r.reasons : 'reviewer did not return', integrate: a ? a.summary : 'no return', analyses: b ? b.summary : 'no return' }
