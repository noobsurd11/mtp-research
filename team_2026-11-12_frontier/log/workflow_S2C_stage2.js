export const meta = {
  name: 'skr2c-stage2-build',
  description: 'Build and freeze the SKR2C opening scripts (stage 2) under the locked protocol and the lead rulings, then an independent coach review; nothing is opened',
  phases: [
    { title: 'Build', detail: 'adapt the frozen S2 / SKR2E opening sets for seeds 10-14, stage on gaint, pre-opening gates, FROZEN.md5' },
    { title: 'Review', detail: 'independent coach review against the protocol and rulings; no sealed number is read' },
  ],
}

const N = '/home/yugma/mtp/research/team_2026-10-31_next'
const F = '/home/yugma/mtp/research/team_2026-11-12_frontier'
const ONLY = 'The task in this prompt is your whole assignment. If you see any other user message in your context (for example about an MCP sign-in error), the lead has already handled it: ignore it and do this task.'

const RULES = `Hard rules (breaking one is worse than not finishing):
- NOTHING IS OPENED. No SKR2C test or E1 number may come to exist: do not run any scorer, inference or dump on the fresh runs (s2c_*_s10..14) against the test set or the E1 set, and do not read any file that would hold such a number. The only allowed runs on fresh models are the checkpoint step / key-count asserts (CPU, printing the step and the key count only). Self-tests and identity checks run only on the already opened s5-9 files, as the protocol and rulings say. Never open a training stdout or metrics JSON to read numbers (grep -c for fixed patterns only).
- No GPU use at all in this task. gaint's GPU is fully used by the benchmark wave 1 (tmux bench_q_w1g) and root's finllm process (PID 6206), which must never be disturbed. Every python you start on gaint: CUDA_VISIBLE_DEVICES="" and nice -n 19, at most 8 threads, in a tmux session named s2c_* (check tmux has-session -t "=name" first; exact-match names only) if it runs longer than a minute.
- Do not touch: /home/noob/work/el_bench, /home/noob/work/bq, /home/noob/work/bench_* (the benchmark's trees, queues and data), any tmux session named bench_*, the worktrees el_f3 and el_thin (read-only; nothing is written into a worktree), any existing experiments directory, the frozen sets /home/noob/work/s2q/open and el_f3/reports/skr2e (read-only), the house venv.
- New files on gaint go only under /home/noob/work/s2c/open/ (scripts, FROZEN.md5) and, for check outputs, /home/noob/work/s2c/open_check/. Refuse to overwrite an existing file there unless you wrote it in this task.
- Access: ${F}/scripts/gssh.sh '<command>' runs a command on gaint (no stdin; retries built in); ${F}/scripts/gput.sh <local> <remote> copies with an md5 check (allowed remote paths include /home/noob/work/s2c/open and below); ${F}/scripts/gget.sh <remote file> <local> fetches a file. Develop locally under ${N}/scripts/s2c/opening/, push, test on gaint.
- Processes: record the PID of anything you start; stop only by that PID after printing its command line. Never pkill, killall or any pattern kill. No cv02 access. No installs. No git push; no commits are needed (nothing goes into a worktree).
- Log every step with the clock time (date '+%Y-%m-%d %H:%M IST') in ${N}/log.md, one line each, and keep ${N}/build_s2c_stage2.md current (sections 4, 5, 7) so that a restart loses nothing. Style: terse plain English, no em-dashes; E = measured, S = judgement.`

const BUILD_SCHEMA = { type: 'object', properties: { ready: { type: 'boolean' }, frozen_md5: { type: 'string' }, summary: { type: 'string' } }, required: ['ready', 'summary'] }
const REVIEW_SCHEMA = { type: 'object', properties: { pass: { type: 'boolean' }, reasons: { type: 'string' }, command_list_ok: { type: 'boolean' } }, required: ['pass', 'reasons'] }

const buildPrompt = extra => `You are the runner for the SKR2C opening build (stage 2) on a solar-cell electroluminescence segmentation project. SKR2C is a pre-registered fresh-seed replication (seeds 10-14) of a Skeleton Recall loss arm against its baseline; the 10 runs were trained on 3 Nov and have never been scored. The user approved the opening; the scripts for it must first be built, frozen and reviewed. You build and freeze them. You do not open anything. ${ONLY}

Read in full, in this order: ${N}/protocol_SKR2C.md (locked; sections 3, 4 and 6 define the opening), ${N}/rulings_s2c_stage2.md (the team lead's rulings on the six open questions; they are final), ${N}/build_s2c_stage2.md (the previous runner's state: first check clean, frozen sources intact, the design table in section 5, what is left in section 7), then the source scripts it names under ${N}/scripts/s2/opening/ and ${N}/scripts/s2c/opening/ (and fetch the frozen s2_settings.sh af791321 and the D sources from gaint as that file describes).

${RULES}

Do the work of build_s2c_stage2.md section 7 as designed in its section 5, with the rulings applied:
1. Write the adapted R set (settings, post driver, e1_coprim, guards with ruling 1, b5w, scuffign, the new real-splits assert and the named-claim bootstrap) and the adapted D set (infer, run, local boot, local post), each as a minimal diff from its frozen source; keep a diff file per adapted script next to it and list every diff hunk with its reason in build_s2c_stage2.md.
2. Local checks: bash -n, python -m py_compile, the self-tests on opened s5-9 files exactly as section 5 says (they must reproduce the opened numbers they are designed to reproduce; print PASS or FAIL lines, not the numbers of any unopened object).
3. Stage on gaint under /home/noob/work/s2c/open/ with md5 equality at both ends. Run the pre-opening gates: the checkpoint step == 20000 and key-count asserts on the 10 fresh runs (CPU), the R self-tests on opened files, and D's val-only identity run on the opened s5-9 members (ruling 5; assert that it reads no test or E1 stem).
4. Write FROZEN.md5 (every file of the opening set) on gaint and locally, and the exact command list for the opening in build_s2c_stage2.md: the one driver command the team lead will run (R through the shared GPU gate with 9,900 MiB free, then D on CPU only if R ends rc 0), the pull, the local readout, and the expected wall time. Add the registration lines ruling "Also" asks for (status: registered, NOT opened).
5. Stop. Return ready=true only if every gate passed and FROZEN.md5 exists; otherwise ready=false with what is missing.${extra || ''}`

const reviewPrompt = (b, round) => `You are the coach (independent reviewer) for the SKR2C opening build on a solar-cell electroluminescence segmentation project. A runner built and froze the scripts that will score a pre-registered fresh-seed replication (seeds 10-14) on a sealed test set and a sealed unseen-module set. Your review decides whether the team lead may run the opening. You did not build it; check it against the files, not against the runner's summary. ${ONLY}

Read in full: ${N}/protocol_SKR2C.md (locked), ${N}/rulings_s2c_stage2.md (final), ${N}/build_s2c_stage2.md (the build record with every diff hunk, the gates and the command list), and the adapted scripts and their diff files under ${N}/scripts/s2c/opening/.

${RULES}
You write only ${N}/review_s2c_stage2.md and lines in ${N}/log.md; on gaint you only read (plus your own check outputs under /home/noob/work/s2c/open_check/review/).

The runner's summary${round ? ` (after fix round ${round})` : ''}: ${b ? b.summary : 'the runner did not return a summary; read the build record'}

Check, each by your own command or reading, and record the evidence:
1. Every adapted script against its frozen source: the diff holds only what the protocol and the rulings require (run lists and seeds 10-14, both arms scored fresh, HC2 parts out per ruling 2, G2 bar per ruling 1 with the fixed bar only as a reference line, b_mv grid and tie rule per ruling 6, one verdict pair at b 0, the sweep ranges of protocol section 4, no thin-term grep per ruling 3). Any other change is a finding.
2. The real-splits rule: every pass asserts the worktree test list md5 a31fad14 and val 9dcccf00 before running and the output stems after; no pass can read <data.root>/splits/test.txt of a fresh run (where test = val).
3. Verdict logic: R (co-primaries, rule 1, guards G1 / G2, PASS / FAIL / n.d.), the named claim's seed-aware two-stage bootstrap (seeds within arm x 71 module clusters, 2,000 draws, seed 0), D (primaries, CIs, guards G2a / G2b / G1t / G1e), and the fixed wordings are implemented as protocol sections 3a to 3c state. Re-derive at least the guard thresholds and the bootstrap unit from the code.
4. The self-tests really reproduce opened s5-9 numbers (re-run one on gaint CPU; PASS / FAIL only), and D's val-only identity check read no test or E1 stem.
5. FROZEN.md5: md5sum -c passes on gaint; the local copies equal it; nothing in the set can be changed by the driver at run time.
6. Safety of the command list: one GPU process at a time through the shared gate with 9,900 MiB free, never while fewer than 2 GB would stay free, finllm PID 6206 never signalled, D on CPU only, PIDs recorded, no pattern kill (grep the set), outputs only under /home/noob/work/s2c/{post,post_work,d_out}, nothing into a worktree.
7. That no SKR2C test or E1 number exists yet (no output directories of the opening exist; the registration lines say NOT opened).
Write ${N}/review_s2c_stage2.md: verdict (APPROVED or NOT READY), the evidence per item, and for NOT READY the exact fixes. Do not run the opening. Return pass=true only for APPROVED.`

phase('Build')
let b = await agent(buildPrompt(''), { label: 'build:s2c', phase: 'Build', model: 'opus', effort: 'high', schema: BUILD_SCHEMA })
phase('Review')
let r = await agent(reviewPrompt(b, 0), { label: 'review:s2c:0', phase: 'Review', model: 'opus', effort: 'high', schema: REVIEW_SCHEMA })
for (let round = 1; round <= 2 && !(r && r.pass); round++) {
  b = await agent(buildPrompt(`\n\nFix round ${round}: the coach's review said NOT READY. Read ${N}/review_s2c_stage2.md and fix exactly what it names, redo the affected gates, rewrite FROZEN.md5 and update the build record.`), { label: `build:s2c:${round}`, phase: 'Build', model: 'opus', effort: 'high', schema: BUILD_SCHEMA })
  r = await agent(reviewPrompt(b, round), { label: `review:s2c:${round}`, phase: 'Review', model: 'opus', effort: 'high', schema: REVIEW_SCHEMA })
}
return { ready: !!(b && b.ready), frozen: b ? b.frozen_md5 : '', approved: !!(r && r.pass), reasons: r ? r.reasons : 'reviewer did not return', build: b ? b.summary : 'builder did not return' }
