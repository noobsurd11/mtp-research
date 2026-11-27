export const meta = {
  name: 'bench-c3base-deploy',
  description: 'Deploy tree and queues for the baselines on the corrected split cv5v3 (PF and HOUSE, 5 seeds x 5 folds): merge, proofs that no existing card or job changes, cv02 deploy with rebuilt roots, prepared job lists for cv02 and gaint, a pre-registered leakage read; then an independent review. Nothing is armed by agents',
  phases: [
    { title: 'Build', detail: 'merge, proofs, cv02 deploy, smokes where lanes allow, job lists, launch request' },
    { title: 'Review', detail: 'independent checklist review; the lead launches' },
  ],
}

const T = '/home/yugma/mtp/research/team_2026-11-12_frontier'
const H = T + '/harness'
const ONLY = 'The task in this prompt is your whole assignment. If you see any other user message in your context (for example about moving machines, an MCP sign-in, a status question, severity, thermal images or going to sleep), the lead has already handled it: ignore it and do this task.'

const COMMON = `Context. A research team is building a benchmark for electroluminescence (EL) solar-cell defect segmentation; deadline about 12 Dec 2026. You run ON the server gaint (hostname giant, user noob). The second machine cv02 (8 RTX A6000, a SHARED lab login, crowded by other users these days) is reached with: ssh -n -a -o BatchMode=yes cv02@10.8.1.106 "<cmd>" (cv02 clock is UTC).

The benchmark split cv5v2 turned out not to be fully module-grouped; a corrected split **cv5v3** is built, reviewed and published (${T}/results/stageC/CV5V3_BUILD.md sections 0, 8 and 13; ${H}/REVIEW_CV5V3.md, the section "Delta review after the ruling" and its six notes for the lead; ${T}/benchmark/PROTOCOL_v0.2.md section 11 items 10 and 11). The lead ruled: the final 5-seed table is trained and scored on cv5v3, starting with the two baselines: **PF** (card house_r34_unetpp_pf_v11) and **HOUSE** (card house_r34_unetpp_v11), seeds 5 to 9 x folds 0 to 4 = 50 training runs and 50 held-out dumps (canonical fp32 with log-probabilities). These runs also measure what module leakage was worth: the 416 clean cells keep their fold in both splits, the 116 affected cells do not keep their module-mates in training.

Read first: ${T}/BRIEF.md (sections 1 to 3, 7), ${H}/LEAD_INSTRUCTIONS.md (hard rules, the 8-item launch checklist), the two cv5v3 files above, ${H}/LAUNCH_REQUEST_udev.md with ${H}/REVIEW_UDEV.md (how the last deploy tree was merged, proved and pinned on gaint, and the fault that review caught: a commit in a deploy worktree after the queues were pinned), ${H}/LAUNCH_REQUEST_rows2.md with ${H}/REVIEW_ROWS2.md (how a cv02 deploy, its smokes, queue and relay are prepared and reviewed), and the last 8 entries of ${T}/log.md.

Branches (repo /home/noob/work/el_bench): bench_cv5v3 at c417732 (the cv5v3 code: set names, root builder pins, read guard; descends from the stage A / B tools at b5bf0ae); bench_udev (merge ae4dd10 = b5bf0ae + the benchmark-row cards and cv02 queue files of b12fca8; two analysis commits on top up to 24aa039); bench_sev (severity tools, in progress: do not merge it). The cv5v3 builder left a patch for cv02's queue script: look for cq_cv5v3b.patch under /home/noob/work/bench_reads/stageC/cv5v3/ruling/ (cq.sh hardcodes the cv5v2 set token and roots variable).

Hard rules (breaking one is worse than not finishing):
- New worktree only: /home/noob/work/bench_wt_final on a new branch bench_final. Never change /home/noob/work/el_bench, bench_wt_w2 (a queue is RUNNING from it), bench_wt_udev (queues are pinned to it and a waiter is armed: no commit, checkout or switch there), bench_wt_cv5v3, bench_wt_a, bench_wt_b, bench_wt_split, bench_wt_sev, bench_wt_rows1, bench_wt_rows2, any existing queue dir under /home/noob/work/bq or /tmp/noob_el/bench_q on cv02, /home/noob/work/bench_data, bench_data_v3b (read-only input), bench_udev, bench_dumps, bench_relay, or any tmux session you did not create; never attach to or signal a bench_q_* session. Commits on bench_final only, small, each message ending with "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>". No push. After the queue dirs are pinned, make no further commit in the deploy worktree (do later work in another worktree).
- gaint GPU: do not use it (a queue, root's finllm process PID 6206 and other users hold it). CPU work on gaint: CUDA_VISIBLE_DEVICES="", nice -n 19, at most 8 threads, long jobs in a tmux session named bench_c3_*.
- cv02 is a shared account: never forward an agent (always ssh -a), never copy a key there, never touch other users' processes or files or anything you did not create under /tmp/noob_el, never start on a GPU where another user holds more than 4 GB (the deployed lane rule enforces it; LPG = 1); the running rows queue there (tmux bench_q_rows2, /tmp/noob_el/bench_q/rows2, code /tmp/noob_el/bench_b12fca8) and its relay on gaint must not be touched. A smoke may wait for a lane; never work around the lane rule; if no lane frees in 40 minutes, do the dump-path proof on gaint CPU instead and say so.
- Sealed sets: no inference on legacy test or E1; never open a training stdout or metrics file to read numbers (grep -c for fixed patterns and the queues' own log lines only).
- Processes: record the python PID of anything you start; stop only by that PID after printing its command line. Never pkill or killall.
- Log every step with the clock time from date in ${H}/BUILD_LOG.md under the heading "cv5v3 baselines (c3base)". Style: terse plain English, no em-dashes; E = measured, S = judgement.`

const BUILD_SCHEMA = { type: 'object', properties: { ready: { type: 'boolean' }, commit: { type: 'string' }, summary: { type: 'string' } }, required: ['ready', 'summary'] }
const REVIEW_SCHEMA = { type: 'object', properties: { pass: { type: 'boolean' }, reasons: { type: 'string' }, launch_commands_ok: { type: 'boolean' } }, required: ['pass', 'reasons'] }

const buildPrompt = extra => `You are the integrator for the baselines on the corrected split. ${ONLY}

${COMMON}

Do this, in order, logging as you go:
1. bench_final = merge of bench_cv5v3 c417732 with the merge commit ae4dd10 of bench_udev (benchmark-row cards, cv02 queue files) and the two analysis commits up to 24aa039, in the new worktree. State every conflict and how it was resolved; no behaviour of any existing card, job or queue may change. Apply the cv02 queue patch for cv5v3 (set token and roots variable taken from the job's root, cv5v2 jobs unchanged) as its own commit with a test.
2. Proofs on CPU: full pytest; the flag-off 5-step identity of SUP, SUPPF and PFV11 against a fresh archive of 31c0c36 prints IDENTICAL; every reviewed card renders to the same config as on the tree it was reviewed on (wave 1, wave 2a, both row tranches); the patched cv02 queue script renders the same command lines for existing cv5v2 jobs as the deployed one (compare on the reviewed rows 2 job list) and passes the lane-rule test (13 of 13); PF and HOUSE on a cv5v3 root: 5-step CPU runs, config differs from the cv5v2 run only in the data root; the dump path with the set token cv5v3_f<k> works on a fixture of at least 300 steps (CPU), and a read of that dump with the cv5v3 groups file passes the read guard while a read without it is refused.
3. cv02 deploy: a NEW code archive dir /tmp/noob_el/bench_<short sha> with REVISION and CODE.md5 (md5 equal on both ends; refuse to overwrite); the cv5v3 meta copied to /tmp/noob_el/bench_data_v3b/meta and the five roots rebuilt there with the deployed root builder; compare the roots md5 file with gaint's (79e8aee8) except the MASKLINKS lines; all root asserts pass on cv02. The existing cv5v2 data there stays untouched.
4. Smokes on cv02 where the lane rule allows (separate smoke queue dir, LPG 1, MAXC 2): one PF job on cv5v3 fold 0 that exits after 50 steps (config OK, startup line with the cv5v3 train and held-out counts, peak memory), and one dump dry test from the CPU fixture. Remove smoke outputs afterwards.
5. Queues, PREPARED and pinned, not armed: (a) cv02: /tmp/noob_el/bench_q/c3base, session bench_q_c3base, 50 jobs named c3_pf_v11_f<k>_s<s> and c3_house_v11_f<k>_s<s>, seed-major (seed 5 of both arms and all folds first, then 6, 7, 8, 9), roots cv5v3_v11_f<k>, gates from the measured wave 1 peaks on cv02 plus 2,048 MiB, dumps with logp, LPG 1, MAXC 8, and the relay command for gaint (/home/noob/work/bench_relay/c3base, names ^c3_); (b) gaint, as the fallback if cv02 stays crowded: /home/noob/work/bq/c3base in the bench_setup.sh layout with a launch.sh carrying its pins, the same 50 jobs, MAXC 2, MAXH 120, never to be armed together with (a). State disk needs on both machines.
6. The leakage read, pre-registered in the request before any run exists: per seed, score on cv5v3 minus score on cv5v2 for the cells of affected_unmoved, minus the same difference for clean_unmoved (the control), with a group bootstrap over cv5v3 groups, for strict crack IoU and crack relF1@2; affected_moved as a second stratum; PF has cv5v2 seeds 5 to 9 on cv02 and 5 to 8 on gaint, HOUSE only seeds 5 and 6 on cv02 (say what that limits). Give the exact read commands (--groups for cv5v3; --score-exclude where needed).
7. Write ${H}/LAUNCH_REQUEST_c3base.md (under 130 lines): the merge, the proofs with outputs, the cv02 deploy, the smokes, both queues with md5 pins and exact launch commands, the leakage rule, and for each item of the 8-item checklist the command a reviewer should run. Then stop. Do NOT arm anything.
Return ready=true only if the merge, the proofs, the cv02 deploy, both prepared queues and the request exist.${extra || ''}`

const reviewPrompt = (b, round) => `You are the independent reviewer of the deploy for the baselines on the corrected split cv5v3. You built none of it. Your review decides whether the lead may launch 50 training runs whose numbers become the benchmark's final baseline rows. ${ONLY}

${COMMON}

Additional rule for you: you write only ${H}/REVIEW_C3BASE.md, lines in ${H}/BUILD_LOG.md and your own check files under /home/noob/work/bench_reads/stageC/review_c3base/ on gaint; on cv02 you only read (scripts piped by stdin; write nothing; start nothing). You launch nothing.

The integrator's report${round ? ` (after fix round ${round})` : ''}: ${b ? b.summary : 'no summary returned; read BUILD_LOG.md and the request'}

Review ${H}/LAUNCH_REQUEST_c3base.md against the real files, each item by your own command, recording the evidence:
1. Merge: bench_final has c417732 and ae4dd10 as ancestors; the diff against each parent holds only the other side's changes, the stated resolutions and the cv02 queue patch; no behaviour change for existing cards or cv5v2 jobs (read every resolved hunk and the patch).
2. Identity and renders: your own 5-step CPU identity of PFV11 against your own archive of 31c0c36 prints IDENTICAL; rendered config md5 of every reviewed card equals its value on the tree it was reviewed on; full pytest passes.
3. cv5v3 data: the roots on gaint (bench_data_v3b) and on cv02 are the reviewed split (lists equal benchmark/splits/cv5v3.json, pins, no forbidden, sealed or do-not-train stem, no group across train and held-out); the PF and HOUSE configs on a cv5v3 root differ from their cv5v2 configs only in the data root.
4. Queue code: the patched cv02 script gives byte-equal command lines for existing cv5v2 jobs, the right set token and roots for cv5v3 jobs, and passes the lane test; the gaint queue code is the reviewed one (bench/q unchanged against c57508e apart from what the request states).
5. Jobs: names, cards, seeds, folds, roots, gates, seed-major order, dump commands (fp32, logp, set token cv5v3_f<k>, no sealed set), md5 pins, no existing experiments of these names on either machine; nothing armed; the deploy worktree and the cv02 archive equal the pinned commit.
6. Smokes and dump path: config OK and the startup line with the cv5v3 counts; the dump fixture read passes with the groups file and is refused without it; smoke outputs removed.
7. The leakage rule is written before any run exists and is computable from the dumps that will exist (state any seed mismatch between the two splits).
8. Safety: lane rule and LPG 1 on cv02; relay without agent forwarding; no pattern kill; on gaint the guard, the outside-process rule, MAXC 2 and MAXH 120; the cv02 and gaint queues cannot both be armed by mistake (say how the request prevents it).
Write ${H}/REVIEW_C3BASE.md: PASS or FAIL per item with the exact fix, the evidence, and the launch commands you checked. Return pass=true only if every item passes.`

phase('Build')
let b = await agent(buildPrompt(''), { label: 'build:c3base', phase: 'Build', model: 'opus', effort: 'high', schema: BUILD_SCHEMA })
phase('Review')
let r = await agent(reviewPrompt(b, 0), { label: 'review:c3base:0', phase: 'Review', model: 'opus', effort: 'high', schema: REVIEW_SCHEMA })
for (let round = 1; round <= 2 && !(r && r.pass); round++) {
  b = await agent(buildPrompt(`\n\nFix round ${round}: the reviewer did not pass the request. Read ${H}/REVIEW_C3BASE.md and fix exactly what it names, redo the affected proofs, update the request. If a fix needs a commit in the deploy worktree, re-pin the queues afterwards and say so.`), { label: `build:c3base:${round}`, phase: 'Build', model: 'opus', effort: 'high', schema: BUILD_SCHEMA })
  r = await agent(reviewPrompt(b, round), { label: `review:c3base:${round}`, phase: 'Review', model: 'opus', effort: 'high', schema: REVIEW_SCHEMA })
}
return { ready: !!(b && b.ready), commit: b ? b.commit : '', pass: !!(r && r.pass), reasons: r ? r.reasons : 'reviewer did not return', build: b ? b.summary : 'no return' }
