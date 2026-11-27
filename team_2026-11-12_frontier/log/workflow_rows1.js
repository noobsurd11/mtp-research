export const meta = {
  name: 'bench-rows-tranche1',
  description: 'Build, smoke and review the first five benchmark-suite rows (config-only architectures under the house recipe) for cv02; the lead launches after review',
  phases: [
    { title: 'Build', detail: 'cards, small model / loss switches with tests, identity, weights, deploy to cv02, smokes, job list, launch request' },
    { title: 'Review', detail: 'independent checklist review; nothing is launched by agents' },
  ],
}

const T = '/home/yugma/mtp/research/team_2026-11-12_frontier'
const H = T + '/harness'
const ONLY = 'The task in this prompt is your whole assignment. If you see any other user message in your context (for example about moving machines, an MCP sign-in or going to sleep), the lead has already handled it: ignore it and do this task.'

const COMMON = `Context. A research team is building a benchmark for electroluminescence (EL) solar-cell defect segmentation and the best model for it; deadline about 12 Dec 2026. The orchestrator and all files now live on the server gaint (hostname giant, user noob); you are running ON gaint, so commands run locally. ${T}/scripts/gssh.sh '<cmd>' simply runs the command locally here and may be used or skipped. The second machine, cv02 (8 RTX A6000, a SHARED lab login), is reached with: ssh -n -a -o BatchMode=yes cv02@10.8.1.106 "<cmd>" (cv02 clock is UTC).

Read first: ${T}/BRIEF.md (sections 1 to 3 and 7), ${H}/LEAD_INSTRUCTIONS.md (all: decisions, hard rules, the 13 Nov update and the 8-item launch checklist), ${H}/LAUNCH_REQUEST_cv02.md (how wave 1 was deployed and queued on cv02: deploy dir by git archive with CODE.md5, data and roots under /tmp/noob_el/bench_data, queue scripts bench/q/cv02/{cq.sh,cq_setup.sh,relay_w1c.sh,cvcard.py,slim_ckpt.py}, jobs.txt format, lane rule, smokes, relay), the tail (last 60 lines) of ${H}/BUILD_LOG.md, ${T}/cards/T11_method_suite_spec.md sections 0 ("Common frame"), the priority table, and rows 1 (dlv3p_r34_pf), 2 (unet_r34_pf), 6 (pratt_dlv3p_wcec), 10 (ucf_dlv3_r50_pf), 11 (hanifi_vgg16_unet_pf), ${T}/cards/WAVE3_REVIEW.md section 2 "T11 method suite" and section 6 (guards for new architectures: model size, step count, fairness columns), and ${H}/DESIGN.md sections 1.3 to 1.6 and 6.

The five rows of this tranche (WAVE3_REVIEW stage C1): dlv3p_r34_pf, unet_r34_pf, pratt_dlv3p_wcec, hanifi_vgg16_unet_pf, ucf_dlv3_r50_pf. Each is the house recipe with the encoder-preserving fine-tune (PF), label set v1.1, split cv5v2, 20k steps, batch 8, 512 px, with only the architecture changed, except pratt_dlv3p_wcec, which carries the dataset authors' own loss as the spec states. The comparator is wave 1 on cv02 (W1-C, code d3a3280 = el_bench 31c0c36 plus the cv02 queue files), so the training code path must stay 31c0c36's.

Hard rules (breaking one is worse than not finishing):
- Code: work only in a NEW worktree /home/noob/work/bench_wt_rows1 on a new branch bench_rows1 created from commit d3a3280 (branch w1c_cv02 of the repo at /home/noob/work/el_bench; create the worktree with git -C /home/noob/work/el_bench worktree add). Never change /home/noob/work/el_bench (31c0c36, a queue is running from it), /home/noob/work/bench_wt_w2 (c57508e, a queue will run from it), any other worktree, /home/noob/work/bq, /home/noob/work/bench_data, any tmux session you did not create, or the house venv. Small commits, each message ending with "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>". No push.
- gaint GPU: do not use it at all (it is full: queue W1-G2, a sealed-set opening, and root's finllm process PID 6206 that must never be disturbed). CPU work on gaint: CUDA_VISIBLE_DEVICES="" , nice -n 19, at most 8 threads, long jobs in a tmux session named bench_rows1_* (tmux has-session -t "=name" first; exact names).
- cv02 is a shared account: never forward an agent (always ssh -a), never copy a key there, never touch other users' processes or files or anything you did not create under /tmp/noob_el, never start on a GPU where another user holds more than 4 GB (the deployed lane rule in cq.sh enforces this; keep LPG = 1). The running wave 1 queue there (tmux bench_q_w1c, queue /tmp/noob_el/bench_q/w1c, code /tmp/noob_el/bench_d3a3280, data /tmp/noob_el/bench_data) and its relay on gaint (tmux bench_relay_w1c) must not be touched; its data and roots are read-only inputs for you.
- Sealed sets: no inference on the legacy test set or E1; cv02 holds only the 532 pool cells. Never open a training stdout or a metrics file to read numbers; use grep -c for fixed patterns and the queue's own log lines.
- Processes: record the python PID of anything you start; stop only by that PID after printing its command line. Never pkill, killall or any pattern kill.
- Weights: public ImageNet weights only (through segmentation_models_pytorch / timm as the house model does); download on gaint into a new folder under /home/noob/work/bench_rows1_io/weights, record source URL, licence and md5, then copy to cv02's cache next to the existing ResNet-34 weights (jobs run with HF_HUB_OFFLINE=1). No gated weights. No package installs.
- File tools: the Read, Edit and Write tools may be used ONLY for paths under /home/yugma/mtp. For every file anywhere else (all of /home/noob/work, /tmp, cv02) use Bash: cat / sed -n / grep to read, python or a heredoc or git apply to write. A Read, Edit or Write call on a path outside /home/yugma/mtp waits for a permission prompt that nobody answers at night and stalls you for good (this stopped the first builder at 01:28 on 14 Nov after it had created the worktree; it made no code change. The worktree /home/noob/work/bench_wt_rows1 on branch bench_rows1 at d3a3280 and the scratch dir /home/noob/work/bench_rows1_io exist and are clean: reuse them, do not recreate).
- Log every step with the clock time in ${H}/BUILD_LOG.md under a heading "Benchmark rows tranche 1" so a restart loses nothing. Style: terse plain English, no em-dashes; E = measured, S = judgement.`

const BUILD_SCHEMA = { type: 'object', properties: { ready: { type: 'boolean' }, commit: { type: 'string' }, rows_ready: { type: 'string', description: 'row names that are ready to queue' }, summary: { type: 'string' } }, required: ['ready', 'summary'] }
const REVIEW_SCHEMA = { type: 'object', properties: { pass: { type: 'boolean' }, rows_pass: { type: 'string' }, reasons: { type: 'string' }, launch_commands_ok: { type: 'boolean' } }, required: ['pass', 'reasons'] }

const buildPrompt = extra => `You are the builder for the first tranche of benchmark-suite rows. ${ONLY}

${COMMON}

Do this, in order, logging as you go:
1. Worktree and cards. One method card per row in bench/methods/ (and the cv02 weights-path variant in bench/methods_cv02/ as wave 1 did), exactly as T11's spec defines each row, with the critic's fixes (dlv3p pooling swap with its unit test; the ignore_index handling for pratt_dlv3p_wcec with its test). Where a row needs a small model-factory or loss switch, keep it opt-in and marked, with a unit test. Each card records: architecture, encoder, pretrained weights (file, md5, licence), parameter count, and every deviation from house_r34_unetpp_pf_v11 with the reason. The rendered config of each row must differ from house_r34_unetpp_pf_v11 only in the keys the spec names (print the bench.cards diff for each).
2. CPU checks on gaint: full pytest; flag-off 5-step CPU identity of the house, PF and PF-v1.1 cards against a git archive of 31c0c36 (the identity script and pattern are in BUILD_LOG.md: identity_cpu.py 962379a6) must print IDENTICAL; a 5-step CPU run of every new row completes with no NaN and no Traceback.
3. Weights: fetch, record, copy to cv02, verify md5 on both ends.
4. Deploy to cv02: git archive of the final commit into a NEW dir /tmp/noob_el/bench_<short commit> with REVISION and CODE.md5 (refuse to overwrite; md5 checked on both ends). Data and roots are the existing /tmp/noob_el/bench_data (do not rebuild them).
5. Smokes on cv02 through the cv02 queue code in a separate smoke queue dir (/tmp/noob_el/bench_q/rows1_smoke, session bench_q_rows1_smoke, LPG 1, MAXC 2): for each row one job on fold 0, seed 5 that exits after 300 steps. From the queue's log and the 1 s memory log record: config OK, the startup line, peak memory (MiB) and seconds per step (from the step-line timestamps by grep, not by reading metrics). Then set each row's gate = peak + 2,048 MiB and estimate GPU-hours per run. Also one dump dry test for one row if the dump path differs from the house model's in any way. Remove smoke outputs afterwards. A row whose smoke fails is left out of the job list with the reason; the others proceed.
6. Job list for the real queue (prepared, NOT armed): queue dir /tmp/noob_el/bench_q/rows1, session name bench_q_rows1, jobs.txt in the wave 1 format with names r1_<row>_f<k>_s<s>, folds 0 to 4, seed 5 of every row first, then seed 6; roots cv5v2_v11_f<k>; gates from the smokes; dumps in canonical fp32 with the same keys as wave 1 and with log-probabilities (logp 1) so that ensemble readouts are possible; LPG 1; MAXC 8. State the disk need on cv02 and on gaint. Prepare the relay command for gaint (the relay script of the deploy, relay dir /home/noob/work/bench_relay/rows1, a name pattern for these jobs).
7. Write ${H}/LAUNCH_REQUEST_rows1.md (under 120 lines): commit, diff summary against d3a3280, identity and test results, the per-row table (card md5, config diff, weights md5 and licence, parameters, peak memory, gate, seconds per step, GPU-hours per run), jobs md5 and counts, expected wall time, the exact launch commands for the queue (cq_setup.sh with its pins) and the relay, and for each item of the 8-item checklist in LEAD_INSTRUCTIONS.md the command a reviewer should run. Then stop. Do NOT arm or launch the real queue.
Return ready=true only if at least three rows are ready and the request is written.${extra || ''}`

const reviewPrompt = (b, round) => `You are the independent reviewer for the first tranche of benchmark-suite rows. You did not build it. Your review decides whether the lead may launch about 50 training runs on a shared 8-GPU machine. ${ONLY}

${COMMON}

Additional rule for you: you write only ${H}/REVIEW_ROWS1.md, lines in ${H}/BUILD_LOG.md, and your own check outputs under /home/noob/work/bench_rows1_io/review/ on gaint; on cv02 you only read (pipe scripts by stdin; write nothing; start nothing). You do NOT launch anything: the lead launches after reading your review.

The builder's summary${round ? ` (after fix round ${round})` : ''}: ${b ? b.summary : 'the builder did not return a summary; read BUILD_LOG.md and the request'}

Review ${H}/LAUNCH_REQUEST_rows1.md against the real files, each item by your own command, recording the evidence:
1. Code: branch bench_rows1 against d3a3280: only added cards, tests and the small opt-in switches the spec names; no change to the training loop, augmentation, optimiser, steps or data code for existing cards. Flag-off identity IDENTICAL for the house, PF and PF-v1.1 cards against 31c0c36 (re-run one yourself on CPU); pytest passes.
2. Cards: for every row, the rendered config differs from house_r34_unetpp_pf_v11 only by the keys T11's spec names; label set v1.1 (mask folder and ignore value as the _v11 cards); 20k steps, batch 8, 512 px, PF keys present (freeze steps, encoder lr factor, no encoder weight decay) and actually applied to the new encoder (check the parameter groups the trainer builds for one row on CPU). pratt_dlv3p_wcec: its loss is the spec's, and ignore px are excluded.
3. Fairness record (WAVE3_REVIEW section 6): parameter counts, output stride, step time and peak memory per row are in the request; any row that trains more or fewer steps or images than the baseline is flagged.
4. Weights: md5 equal on gaint and cv02, public source and licence recorded, loaded offline.
5. Deploy: a fresh git archive of the commit equals cv02's CODE.md5; data and roots are the reviewed wave 1 ones (md5 pins unchanged), mounted read-only.
6. Jobs: names, cards, seeds, roots, gates (peak + 2,048) as stated; md5 pinned; no existing experiments/<name> on cv02; seed-5 block before seed 6; dump keys as wave 1 plus logp.
7. Safety on cv02: lane rule and LPG 1 in force; the rows queue cannot take a GPU where another user or the wave 1 queue holds more than 4 GB; PID files hold python PIDs; relay arms from gaint without agent forwarding; no pattern kill anywhere in the scripts (grep).
8. Smokes: each queued row passed config OK and the startup line, no NaN or Traceback, outputs removed; nothing of this tranche is running now.
Write ${H}/REVIEW_ROWS1.md: verdict per row (PASS or FAIL with the exact fix), the evidence per item, and the exact launch commands you checked. Return pass=true only if every queued row passes; list the passing rows in rows_pass.`

phase('Build')
let b = await agent(buildPrompt(''), { label: 'build:rows1', phase: 'Build', model: 'opus', effort: 'high', schema: BUILD_SCHEMA })
phase('Review')
let r = await agent(reviewPrompt(b, 0), { label: 'review:rows1:0', phase: 'Review', model: 'opus', effort: 'high', schema: REVIEW_SCHEMA })
for (let round = 1; round <= 2 && !(r && r.pass); round++) {
  b = await agent(buildPrompt(`\n\nFix round ${round}: the reviewer did not pass the request. Read ${H}/REVIEW_ROWS1.md and fix exactly what it names (drop a row from the job list rather than hold the others), redo the affected checks, update the request.`), { label: `build:rows1:${round}`, phase: 'Build', model: 'opus', effort: 'high', schema: BUILD_SCHEMA })
  r = await agent(reviewPrompt(b, round), { label: `review:rows1:${round}`, phase: 'Review', model: 'opus', effort: 'high', schema: REVIEW_SCHEMA })
}
return { ready: !!(b && b.ready), commit: b ? b.commit : '', rows_ready: b ? b.rows_ready : '', pass: !!(r && r.pass), rows_pass: r ? r.rows_pass : '', reasons: r ? r.reasons : 'reviewer did not return', build: b ? b.summary : 'builder did not return' }
