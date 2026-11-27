export const meta = {
  name: 'frontier-w1c-w2-build',
  description: 'Deploy and launch wave 1 on cv02 (after an independent review), and in parallel build wave 2a features in separate worktrees, integrate, review and queue them on gaint',
  phases: [
    { title: 'cv02', detail: 'survey, deploy, queue, relay; independent review; launch W1-C' },
    { title: 'Features', detail: 'three builders in separate worktrees: trainer features, losses, CPU tools' },
    { title: 'Integrate', detail: 'merge, identity, cards, job list, launch request for wave 2a' },
    { title: 'Review w2a', detail: 'independent checklist, then arm the wave 2a queue' },
  ],
}

const T = '/home/yugma/mtp/research/team_2026-11-12_frontier'
const H = `${T}/harness`

const COMMON = `Project: a benchmark and best model for electroluminescence (EL) solar-cell defect segmentation (MTP thesis, one month left). A training harness lives in the git worktree /home/noob/work/el_bench on the server "gaint" (branch bench, commit 31c0c36). Wave 1 on gaint (set W1-G: 10 baseline runs, then held-out dumps) was reviewed and LAUNCHED at 15:28 IST on 13 Nov from that worktree, in tmux session bench_q_w1g. It will run for about 9 hours.

THE RUNNING QUEUE MUST NOT BE DISTURBED. Before every job start it checks that /home/noob/work/el_bench is at commit 31c0c36 with no tracked change; if that fails it holds the whole queue. Therefore: never commit, check out, edit or stage anything in /home/noob/work/el_bench; never touch /home/noob/work/bq/w1g, the tmux session bench_q_w1g, its processes, or /home/noob/work/bench_data (read-only for everyone now). All new code goes into NEW worktrees named /home/noob/work/bench_wt_<name> created with "git -C /home/noob/work/el_bench worktree add /home/noob/work/bench_wt_<name> -b <branch> 31c0c36" (adding a worktree and a branch does not change the el_bench working tree). The GPU on gaint is full with W1-G (3 runs plus a protected process); do not start any GPU job on gaint unless your instructions say so; CPU work only, with nice -n 19 and at most 8 threads, CUDA_VISIBLE_DEVICES="".

Read first:
1. ${H}/LEAD_INSTRUCTIONS.md, all of it (decisions in force, the 13 Nov update with the machine roles and the wave 1 run table, launch authority and checklist, hard rules).
2. ${H}/BUILD_LOG.md, all of it (what exists: commits, md5s, identity checks, masks v1.1, roots, cards, queue, smoke). Append to it after every step you finish, with clock times and your role name: you can be cut off at any moment and a successor must continue from the log alone.
3. ${H}/DESIGN.md sections 1.3 to 1.9, 2, 3, 5.
4. The code itself in /home/noob/work/el_bench (read-only; a local mirror of part of it is ${H}/el_bench_src/ but it is older than the server: read the server copy).

Access: gaint only through ${T}/scripts/gssh.sh '<remote command>' (fresh non-interactive shell per call, retries, no stdin; keep each call under about 60 s and bound its output; long jobs go in tmux on gaint with session names bench_*, exact-match addressing -t "=name"). Files: ${T}/scripts/gput.sh <local> <remote> (md5-checked; a directory goes as a tar stream; allowed targets are /home/noob/work/bq and /home/noob/work/bench_* only, so your bench_wt_* worktree is allowed), ${T}/scripts/gget.sh <remote file> <local>. cv02 is reached only from gaint: ssh cv02@10.8.1.106.

Rules that void the work if broken: never pkill / killall / pattern kills (stop only a recorded python PID after printing its command line); never open a training .stdout, metrics or results JSON to read numbers (grep only the exact lines the scripts define); no inference or scoring on the sealed sets (test50, e1_106); root's finllm on gaint (PID 6206) must never die; nothing changes in existing worktrees, data folders, mask folders or the house venv; no installs; cv02 is a shared lab account (no agent forwarding, no keys copied there, never touch other users' files or processes, never start on a GPU where another user holds more than 4,096 MiB). Every new feature is opt-in: with its flag off, the 5-step CPU identity check against el_bench 31c0c36 must stay IDENTICAL (identity_cpu.py and compare_id.py are in /home/noob/work/bench_check/). Commits are small, messages end with the line "Co-Authored-By: Claude <noreply@anthropic.com>". Files you write: terse, plain English, no em-dashes; E = measured, S = judgement.`

const BUILD_SCHEMA = {
  type: 'object',
  properties: {
    ready: { type: 'boolean' },
    worktree: { type: 'string' }, branch: { type: 'string' }, commit: { type: 'string' },
    request_file: { type: 'string' },
    summary: { type: 'string', description: 'under 20 lines: what was built, tests and identity results, what is not done, open problems' },
  },
  required: ['ready', 'summary'],
}
const REVIEW_SCHEMA = {
  type: 'object',
  properties: {
    pass: { type: 'boolean' }, launched: { type: 'boolean' },
    items: { type: 'array', items: { type: 'object', properties: { n: { type: 'integer' }, ok: { type: 'boolean' }, evidence: { type: 'string' } }, required: ['n', 'ok', 'evidence'] } },
    reasons: { type: 'string' }, launch_note: { type: 'string' },
  },
  required: ['pass', 'launched', 'items', 'reasons', 'launch_note'],
}

// ---------------- cv02 ----------------
const buildC = round => `You are the builder for wave 1 on cv02${round ? ` (fix round ${round}: the reviewer rejected the previous launch request; read ${H}/REVIEW_W1_cv02.md first and fix exactly what it names)` : ''}.

${COMMON}

Your job: deploy the reviewed code (el_bench 31c0c36) and data to cv02 and prepare sets W1-C1, W1-C2, W1-C3 of the run table (45 runs) for an independent reviewer. You do not launch. The lead reviewed the gaint artefacts with /home/noob/work/bench_check/review/review_w1g.py (ALL PASS); use the same script as the model for what must hold on cv02.
1. Survey cv02 read-only through gaint: /tmp/noob_el layout and free disk, the house venv B6 used there on 2 Nov (python, torch, torchvision, smp, timm, albumentations, numpy versions against gaint's), GPU state and which GPUs qualify now (at 15:25 today GPUs 0 to 5 held 11 to 16 GB each for other users, GPU 6 was free, GPU 7 held 7.8 GB), CPU cores and load. Record under "cv02 survey" in BUILD_LOG.md. A package difference from gaint is acceptable (all cv02 comparisons stay within cv02) but must be written down.
2. Deploy: git archive of commit 31c0c36 to a new dir /tmp/noob_el/bench_31c0c36/ with CODE.md5 checked on both ends; the ResNet-34 ImageNet weights at the path the cards expect, or cv02 card variants whose only difference is that path (md5 checked; any card change is made in a new worktree bench_wt_cv02 on gaint, never in el_bench, and the archive is then taken from that commit).
3. Data on cv02, new dir /tmp/noob_el/bench_data/: a fresh labeled/ holding ONLY the 532 pool stems' images and current masks (never the 50 test cells or any E1 cell; assert 0 forbidden stems), the v1.1 mask folders, the meta files, and the ten cv5v2 roots rebuilt there with scripts/bench_make_roots.py so that the list md5s equal gaint's. DEPLOY.md5 on both ends.
4. Queue on cv02 in tmux (session names bench_*), built from the B6 cv02 queue pattern (/home/yugma/mtp/research/team_2026-10-31_next/scripts/b6/) and the el_bench queue library: lanes on qualifying GPUs only (no process of another user over 4,096 MiB on that GPU; the account is shared, so "ours" = PIDs in our pid files and their children), at most 2 of our runs per GPU, 120 s between starts, python PIDs recorded, the card config check and startup-line check per run, a HOLD file, no pattern kills. The queue must keep waiting and pick up GPUs as other users free them. After each training run: dump its held-out fold on the same GPU (canonical fp32, TF32 off; logp for the PF v1.1 runs), write RUN.md5.
5. Relay: a loop in tmux on gaint (session bench_relay_w1c) that pulls each finished run from cv02 to /home/noob/work/bench_relay/w1c/ (model weights only as a slim checkpoint, config_used.yaml, the dumps, RUN.md5; the full latest.pth stays on cv02), verifies md5 on both ends and never deletes anything on cv02.
6. Job list: W1-C1 (house_r34_unetpp_pf_v11, folds 0 to 4, seeds 5 to 9), W1-C2 (house_r34_unetpp_v11, seeds 5, 6), W1-C3 (house_r34_unetpp_pf on the v1 roots, seeds 5, 6), ordered so that seeds 5 and 6 of all three sets come first. md5-pinned.
7. A 50-step smoke of one job through the real queue code path on one qualifying GPU, the dump step dry-tested; remove the smoke outputs after.
8. Write ${H}/LAUNCH_REQUEST_cv02.md: deploy commit and md5s, venv versions, job list md5 and counts, lanes and gates, expected wall time, the exact launch commands for the queue and the relay, and for each of the 8 checklist items of LEAD_INSTRUCTIONS.md the command the reviewer should run and what it must print. Do not launch.
Return the structured result.`

const reviewC = round => `You are the independent reviewer for the wave 1 launch on cv02${round ? ` (re-review after fix round ${round})` : ''}. You did not build any of it. Check the real files on cv02 (through gaint) and on gaint.

${COMMON}

Read ${H}/LAUNCH_REQUEST_cv02.md. Run every one of the 8 checklist items in LEAD_INSTRUCTIONS.md ("Launch authority") against the real files with your own commands, and in addition for cv02: (a) labeled/ on cv02 holds exactly the 532 pool stems and 0 forbidden stems; (b) the deployed code md5 equals the archive of the commit named in the request, and that commit differs from 31c0c36 only by what the request states; (c) the lane rule in the queue script really excludes a GPU where another user holds more than 4,096 MiB (read the code and check it against the current nvidia-smi); (d) the relay never deletes on cv02 and checks md5 on both ends; (e) pid files hold python PIDs; (f) no pattern kill in any script; (g) every root on cv02: train and held-out lists equal cv5v2.json, 0 module groups split (group = the "group" column of cv5v2_groups.tsv), mask links right, strict masks hold no ignore px. Record each item's command and result in ${H}/REVIEW_W1_cv02.md.
- If every item passes: launch the queue and the relay with the exact commands in the request, confirm the first job's live checks (or, if no GPU qualifies yet, that the queue is waiting correctly), and append the launch line to ${H}/BUILD_LOG.md and ${T}/log.md (prefix "reviewer").
- If any item fails: launch nothing; write the exact reasons and the smallest fix into REVIEW_W1_cv02.md.
Do not fix anything yourself. Return the structured result.`

// ---------------- feature builders ----------------
const FEATS = [
  { id: 'x1', name: 'trainer features', text: `Arms to make runnable (read ${T}/cards/T1_recipes_spec.md and the critic's rulings on them in ${T}/cards/WAVE2_REVIEW.md; where they disagree the critic wins): rcs (rare-class sampling; crack judged at a matched operating point), ema_wise_posthoc (weight averaging with BN recalibration on the training fold and extra weights keys in latest.pth; the raw weights of a run with the averager on must be bit-identical to a run without it), swad_const (must log encoder cosine to the pretrained weights), encoder_spd with its fold-0 control. Build: the averager module and the checkpoint keys, bench_infer --weights-key, the sampler hook, the SPD optimizer written from the paper, method cards for each arm, unit tests, and the CPU pre-check scripts the spec names. Not in this tranche: sam, modern_recipe.` },
  { id: 'x2', name: 'losses and auxiliary targets', text: `Arms to make runnable (read ${T}/cards/T2_losses_spec.md and the critic's rulings in ${T}/cards/WAVE2_REVIEW.md; the critic wins): soft_band_jml (soft labels in a band around crack labels with a Jaccard metric loss) and its control jml_hard (same loss, hard labels), including the pre-check P1 with the critic's fix (exclude cells with unchanged masks). Build: the batch["aux"] target hook (a dataset wrapper that adds precomputed targets, and the trainer passing the keys a loss declares), the loss modules behind config keys, method cards, unit tests on synthetic shifted labels, the pre-check script. If time remains, add as opt-in modules with tests but without cards: cc_dicece (component-wise Dice + CE on crack) and scnp with the critic's corrected fallback.` },
  { id: 'x3', name: 'CPU tools on dumps', text: `Tools that read prediction dumps and ground truth on CPU (read ${T}/cards/WAVE2_REVIEW.md sections on the CPU-first work and the guards, ${T}/cards/T4_label_refine_style_spec.md for src_calib and the placement analysis, ${T}/cards/T5_thin_inputs_archs_spec.md for dti_hysteresis, and ${H}/DESIGN.md section 3.2): (1) bench_score support for label set v1.1 (ground truth and ignore masks from the run manifest; ignore px not scored) and the cell-type, source and flag subsets from /home/noob/work/bench_data/meta/cells.tsv; (2) one shared crossfit_op module: the matched operating point (a crack bias chosen on the other four folds, never on the scored fold) that every arm must use, with the guards every arm reports (predicted width ratio, relP@2 beside relR@2, false-alarm px on crack-free cells, per-source rows); (3) the wave 1 read script: pooled out-of-fold headline metrics per arm with the group bootstrap (groups = cv5v2_groups.tsv), the A/A comparison of seeds {5,6} against {7,8}, and the pass margin M = max(0.01, 2 x SE of the A/A difference) per headline metric; (4) src_calib (per-source output calibration at inference, reported as a separate "uses source metadata" row with its own interval), dti_hysteresis (dual-threshold iteration on the crack margin; print relF1@1 and width), and D0, the placement diagnostic (do baseline predictions sit on the dark ridge or on the labels, per source). Test everything on dumps that already exist (/home/noob/work/bench_dumps/gpu1 and the chain dry-test dump); W1-G dumps appear tonight under /home/noob/work/bench_dumps/w1g and your scripts must run on them unattended with one command each. Write the commands into ${H}/W1_READ.md.` },
]
const featPrompt = f => `You are feature builder ${f.id} (${f.name}) for wave 2a.

${COMMON}

Your worktree: /home/noob/work/bench_wt_${f.id}, branch bench_${f.id}, created from 31c0c36 (create it if it does not exist; if it exists, continue in it). Two other builders work in their own worktrees at the same time; an integrator will merge the three branches, so keep your changes in new files where you can and keep edits to shared files (trainer, train.py, loss factory, model factory, bench_infer, bench_score) small and clearly marked.

${f.text}

Requirements: every feature opt-in by config key; flag-off 5-step CPU identity against 31c0c36 IDENTICAL for the house and PF arms; unit tests pass with the house venv python on CPU (/home/noob/work/el-fault-detection/.venv/bin/python -m pytest in your worktree, niced); each arm has a method card that validates and whose rendered config differs from house_r34_unetpp_pf_v11 only by the keys you name; a 5-step CPU run of each arm completes. No GPU. Record in BUILD_LOG.md what was built, the commit, the identity and test results, and anything the spec asked for that you did not build and why.
Return the structured result (worktree, branch, commit, summary).`

// ---------------- integrate + review wave 2a ----------------
const integPrompt = feats => `You are the integrator for wave 2a.

${COMMON}

Three feature builders worked in separate worktrees from commit 31c0c36:
${feats.map(x => `- ${x.f.id} (${x.f.name}): ${x.r ? `worktree ${x.r.worktree || '?'} branch ${x.r.branch || '?'} commit ${x.r.commit || '?'} ready=${x.r.ready}. ${x.r.summary}` : 'builder did not finish; check BUILD_LOG.md and its worktree /home/noob/work/bench_wt_' + x.f.id + ' for partial work'}`).join('\n')}

Your job:
1. Create /home/noob/work/bench_wt_w2 on a new branch bench_w2 from 31c0c36 and merge the feature branches that are ready (resolve conflicts in the shared files by keeping every feature opt-in). Run the full test suite on CPU and the 5-step CPU identity checks: flag-off house and PF arms IDENTICAL to 31c0c36, and each arm's 5-step run completes.
2. Wave 2a job list for gaint, queue dir /home/noob/work/bq/w2a, running from the bench_w2 worktree at its final commit (REPO and DEPLOY point there, not at el_bench): for each ready arm among rcs, ema_wise_posthoc, soft_band_jml, jml_hard, swad_const, encoder_spd: folds 0 to 4, seed 5 first for every arm, then seed 6 (so every arm has one full seed before any arm gets its second). Gate 11,000 MiB for arms without a measured peak. MAXC 3. A chained dump pass after training, as W1-G has (bench/q/bench_chain.sh), with dumps under /home/noob/work/bench_dumps/w2a. The comparator for these arms is W1-G (same machine, same code path for the baseline card; state in the request that the baseline card's rendered config at bench_w2 equals the one at 31c0c36).
3. The queue must start by itself when the GPU frees: it shares the gate with W1-G (free memory at least the job's gate and 120 s since any start), so arming it while W1-G runs is safe; set it up so that the reviewer can arm it with one command (a launch script like /home/noob/work/bq/w1g/launch_w1g.sh). Do not arm it.
4. Write ${H}/LAUNCH_REQUEST_w2a.md: the bench_w2 commit, the merge list, identity and test results, the arms with their cards and config diffs against the baseline card, the job list md5 and lines, gates, expected GPU-hours, the launch command, and for each checklist item of LEAD_INSTRUCTIONS.md (adapted: roots and masks are the reviewed wave 1 ones, so items 2 to 4 reduce to "the jobs point at the reviewed roots") the command the reviewer should run. Also list the pre-checks from the specs that must pass before an arm's result may be read, and which CPU tools (from builder x3) the read needs.
Return the structured result (worktree, branch, commit, request_file, summary).`

const reviewW2 = round => `You are the independent reviewer for wave 2a on gaint${round ? ` (re-review after fix round ${round})` : ''}. You did not build any of it.

${COMMON}

Read ${H}/LAUNCH_REQUEST_w2a.md, ${T}/cards/WAVE2_REVIEW.md (the critic's rulings and required fixes per arm) and the arm specs it points to. Check with your own commands, read-only:
1. The bench_w2 worktree is at the commit named, clean; the test suite passes on CPU; flag-off identity of the house and PF arms against 31c0c36 is IDENTICAL in the logs, and you re-run one identity check yourself.
2. Each arm's card: its rendered config differs from house_r34_unetpp_pf_v11 only by the keys the request names; the change implements what the spec and the critic's fixes say (read the code of each feature: look for an unintended change of the loss weighting, the sampler touching held-out cells, labels leaking from the held-out fold, a different number of optimizer steps, a different batch size, a changed augmentation, weights or data from outside the fold).
3. Jobs: point at the reviewed wave 1 roots (/home/noob/work/bench_data/roots/cv5v2_v11_f{0..4}); names, seeds and gates as stated; md5 pinned; no existing experiment dir would be overwritten; dumps go to a new folder.
4. Safety: the queue uses the shared gate, the guard and the memory logger; it cannot disturb W1-G (different queue dir, different worktree, same gate); no pattern kill.
Record each item in ${H}/REVIEW_W2A.md.
- If every item passes for at least one arm: remove from the job list any arm that failed (state which and why, re-pin the md5 in the launch script, record it) and arm the queue with the launch command; confirm it is waiting on the gate or that its first job passed the live checks; append the launch line to ${H}/BUILD_LOG.md and ${T}/log.md (prefix "reviewer").
- If no arm passes: arm nothing; write the reasons and the smallest fixes.
Return the structured result.`

async function stageCv02() {
  let b = await agent(buildC(0), { label: 'build:cv02:0', phase: 'cv02', model: 'opus', effort: 'high', schema: BUILD_SCHEMA })
  if (!b) return { error: 'builder died', pass: false, launched: false }
  let r = await agent(reviewC(0), { label: 'review:cv02:0', phase: 'cv02', effort: 'medium', schema: REVIEW_SCHEMA })
  let round = 0
  while (r && !r.pass && round < 2) {
    round++
    b = await agent(buildC(round), { label: `build:cv02:${round}`, phase: 'cv02', model: 'opus', effort: 'high', schema: BUILD_SCHEMA })
    if (!b) break
    r = await agent(reviewC(round), { label: `review:cv02:${round}`, phase: 'cv02', effort: 'medium', schema: REVIEW_SCHEMA })
  }
  return { rounds: round, build: b ? b.summary : 'builder died', pass: !!(r && r.pass), launched: !!(r && r.launched), reasons: r ? r.reasons : 'reviewer died', launch_note: r ? r.launch_note : '' }
}

async function stageW2() {
  const feats = await parallel(FEATS.map(f => () =>
    agent(featPrompt(f), { label: `feat:${f.id}`, phase: 'Features', model: 'opus', effort: 'high', schema: BUILD_SCHEMA }).then(r => ({ f, r }))))
  const got = FEATS.map(f => (feats.find(x => x && x.f.id === f.id) || { f, r: null }))
  log(`features: ${got.map(x => `${x.f.id}=${x.r ? (x.r.ready ? 'ready' : 'partial') : 'died'}`).join(' ')}`)
  const integ = await agent(integPrompt(got), { label: 'integrate:w2a', phase: 'Integrate', model: 'opus', effort: 'high', schema: BUILD_SCHEMA })
  if (!integ) return { features: got.map(x => ({ id: x.f.id, summary: x.r ? x.r.summary : 'died' })), error: 'integrator died' }
  let r = await agent(reviewW2(0), { label: 'review:w2a:0', phase: 'Review w2a', effort: 'high', schema: REVIEW_SCHEMA })
  let round = 0
  while (r && !r.pass && round < 1) {
    round++
    await agent(integPrompt(got) + `\n\nFix round ${round}: the reviewer rejected the request; read ${H}/REVIEW_W2A.md and fix exactly what it names in the bench_w2 worktree, then update the request.`, { label: `integrate:w2a:${round}`, phase: 'Integrate', model: 'opus', effort: 'high', schema: BUILD_SCHEMA })
    r = await agent(reviewW2(round), { label: `review:w2a:${round}`, phase: 'Review w2a', effort: 'high', schema: REVIEW_SCHEMA })
  }
  return { features: got.map(x => ({ id: x.f.id, ready: !!(x.r && x.r.ready), commit: x.r ? x.r.commit : '', summary: x.r ? x.r.summary : 'died' })), integ: integ.summary, commit: integ.commit, pass: !!(r && r.pass), launched: !!(r && r.launched), reasons: r ? r.reasons : 'reviewer died', launch_note: r ? r.launch_note : '' }
}

const [cv02, w2] = await parallel([() => stageCv02(), () => stageW2()])
return { cv02, w2 }
