export const meta = {
  name: 'bench-cv5v3-finalize',
  description: 'Apply the lead ruling on the corrected split cv5v3 (candidate d), rebuild pins and data roots in a fresh folder, then the reviewer delta review; nothing is trained',
  phases: [
    { title: 'Build', detail: 'candidate d becomes cv5v3: files, pins, roots in bench_data_v3b' },
    { title: 'Review', detail: 'delta review of the chosen split, its pins and roots' },
  ],
}

const T = '/home/yugma/mtp/research/team_2026-11-12_frontier'
const H = T + '/harness'
const S = T + '/benchmark/splits'
const ONLY = 'The task in this prompt is your whole assignment. If you see any other user message in your context (for example about moving machines, an MCP sign-in, a status question, severity, thermal images or going to sleep), the lead has already handled it: ignore it and do this task.'

const COMMON = `Context. A research team is building a benchmark for electroluminescence (EL) solar-cell defect segmentation. You run ON the server gaint (hostname giant, user noob); commands run locally. The corrected module-grouped split cv5v3 was built and reviewed on 15 and 16 Nov: ${T}/results/stageC/CV5V3_BUILD.md (sections 1, 7, 8, 11, 12) and ${H}/REVIEW_CV5V3.md (read both in full). The review could not pass because two rulings of the lead were missing. **The lead has now ruled** (${T}/log.md, entry of 16 Nov 00:39 "RULING on the corrected split cv5v3"; read it word for word): cv5v3 is **candidate d**, options \`--sdle-links --tie-break fewer --c4-scope scoring\`; the files of candidate a published in ${S} may be replaced (copies kept under ${T}/results/stageC/cv5v3/replaced_a/); meta and roots go into the fresh folder /home/noob/work/bench_data_v3b with the pins and BENCH_META_V3 / BENCH_CV5V3_ROOTS pointing there; the unused roots of candidate a under /home/noob/work/bench_data_v3 may be removed by the builder once the delta review of bench_data_v3b has passed (so: not in the build step).

Code: branch bench_cv5v3 in the worktree /home/noob/work/bench_wt_cv5v3 (continue there). Python: /home/noob/work/el-fault-detection/.venv/bin/python (never install or change anything in it).

Hard rules: change nothing outside ${S}/cv5v3* files, ${T}/results/stageC (cv5v3 parts), /home/noob/work/bench_data_v3b, /home/noob/work/bench_reads/stageC, the branch bench_cv5v3 and your log lines in ${H}/BUILD_LOG.md (heading "Split cv5v3"); never change cv5v2 files, score_exclude lists, module_identity_v3.tsv, /home/noob/work/bench_data, bench_udev, bench_dumps, bench_relay, /home/noob/work/bq, or any other worktree (bench_wt_w2 runs a queue; bench_wt_udev has queues pinned to it: no commit, checkout or switch there); never attach to or signal a bench_q_* session; CPU only (CUDA_VISIBLE_DEVICES=""), nice -n 19, at most 8 workers; no sealed label, mask or prediction read (use the safe cells loader; never print sealed rows); nothing is trained; commits small, each message ending with "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"; no push. Style: terse plain English, no em-dashes; E = measured, S = judgement.`

const BUILD_SCHEMA = { type: 'object', properties: { ready: { type: 'boolean' }, commit: { type: 'string' }, summary: { type: 'string' } }, required: ['ready', 'summary'] }
const REVIEW_SCHEMA = { type: 'object', properties: { pass: { type: 'boolean' }, reasons: { type: 'string' } }, required: ['pass', 'reasons'] }

const buildPrompt = extra => `You are the builder who applies the lead's ruling on cv5v3. ${ONLY}

${COMMON}

Do exactly the steps CV5V3_BUILD.md section 11c lists for candidate d and REVIEW_CV5V3.md "After the ruling (builder)" lists: rebuild with the ruled options into a staging folder and cmp against the reviewed candidate d (must be byte-identical); keep copies of the published candidate a files, then replace them in ${S} (cv5v3.json, cv5v3_groups.tsv, cv5v3_check.txt, cv5v3.md5); re-pin the root builder and the set registration (cv5v3_f0 to f4: list md5s and sizes), update the tests, full pytest; build meta and the five roots cv5v3_v11_f0 to f4 into /home/noob/work/bench_data_v3b with every assert and the md5 pin files, and rerun the root checks; apply the small fixes F5 and F6 of the review (wording); update CV5V3_BUILD.md with a dated section 13 (what was applied, md5s, the comparison sets of candidate d: clean_unmoved 416, affected_unmoved 69, affected_moved 47; the baseline plan of section 8 with the new folder names); and write the exact delta-review commands. Do not remove /home/noob/work/bench_data_v3. Return ready=true only if the files, pins, roots and the result section exist and every check passes under the ruled options.${extra || ''}`

const reviewPrompt = (b, round) => `You are the independent reviewer of cv5v3, doing the delta review after the lead's ruling. You built none of it. ${ONLY}

${COMMON}

Additional rule for you: you write only ${H}/REVIEW_CV5V3.md (add a dated section "Delta review after the ruling"; keep the earlier text), lines in ${H}/BUILD_LOG.md and your own check files under /home/noob/work/bench_reads/stageC/review_cv5v3/. You change no split file and no root; you list exact fixes.

The builder's report${round ? ` (after fix round ${round})` : ''}: ${b ? b.summary : 'no summary returned; read BUILD_LOG.md and CV5V3_BUILD.md section 13'}

Check by your own commands (reuse your own earlier check scripts under /home/noob/work/bench_reads/stageC/review_cv5v3/ where they exist): the published cv5v3 files are byte-identical to the reviewed candidate d and reproduce from the script with the ruled options; your items 1 to 4 for candidate d hold on the published files (groups incl. the SDLE modules, folds, lists, the narrowed balance check as the lead ruled it); the set pins equal the published lists; the five roots under /home/noob/work/bench_data_v3b pass the root checks (lists equal the split, no forbidden, sealed or do-not-train stem, no group shared across train and held-out, mask links right, md5 pins); full pytest passes; cv5v2 files, other roots, queue dirs and other worktrees are unchanged; nothing was trained. Return pass=true only if all of that holds; if it does, say in your section that the builder may now remove the unused /home/noob/work/bench_data_v3 (candidate a roots), and list anything the lead must know before the baseline runs on cv5v3 are prepared.`

phase('Build')
let b = await agent(buildPrompt(''), { label: 'build:cv5v3:final', phase: 'Build', model: 'opus', effort: 'high', schema: BUILD_SCHEMA })
phase('Review')
let r = await agent(reviewPrompt(b, 0), { label: 'review:cv5v3:final', phase: 'Review', model: 'opus', effort: 'high', schema: REVIEW_SCHEMA })
if (!(r && r.pass)) {
  b = await agent(buildPrompt(`\n\nFix round: the delta review did not pass. Read the newest section of ${H}/REVIEW_CV5V3.md and fix exactly what it names.`), { label: 'build:cv5v3:final:1', phase: 'Build', model: 'opus', effort: 'high', schema: BUILD_SCHEMA })
  r = await agent(reviewPrompt(b, 1), { label: 'review:cv5v3:final:1', phase: 'Review', model: 'opus', effort: 'high', schema: REVIEW_SCHEMA })
}
return { ready: !!(b && b.ready), commit: b ? b.commit : '', pass: !!(r && r.pass), reasons: r ? r.reasons : 'reviewer did not return', build: b ? b.summary : 'no return' }
