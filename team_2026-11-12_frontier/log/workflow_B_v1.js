export const meta = {
  name: 'frontier-paper-cards',
  description: 'One agent per shortlisted paper reads the full text and the code and writes a hypothesis card; a critic reviews each card; planners turn the cards into an experiment plan',
  phases: [
    { title: 'Card', detail: 'one card writer per paper: full text, code check, adaptation, decisive experiment' },
    { title: 'Critique', detail: 'one adversarial critic per card' },
    { title: 'Plan', detail: 'cluster planners and a final plan' },
  ],
}

const ROOT = '/home/yugma/mtp/research/team_2026-11-12_frontier'
const MCP = 'select:mcp__claude_ai_Research_MCP__search_papers,mcp__claude_ai_Research_MCP__search_snippets,mcp__claude_ai_Research_MCP__get_paper,mcp__claude_ai_Research_MCP__similar_papers,mcp__claude_ai_Research_MCP__get_citations,mcp__claude_ai_Research_MCP__get_references,mcp__claude_ai_Research_MCP__fetch_fulltext,mcp__claude_ai_Research_MCP__read_paper'

// args: { papers: [ { n, slug, title, pub } ] }   n = rank (int), pub = 1 if a publisher download is allowed for this paper
const PAPERS = (args && args.papers) || []

const VERDICTS = ['RUN_NOW', 'RUN_AFTER_GATE', 'BENCH_ONLY', 'PARKED', 'VOID']
const ROUTES = ['config_only', 'new_loss', 'new_model_code', 'data_pipeline', 'training_recipe', 'inference_only', 'external_codebase', 'analysis_only']

const CARD_SCHEMA = {
  type: 'object',
  properties: {
    n: { type: 'integer' },
    title: { type: 'string' },
    paper_id: { type: 'string' },
    fulltext_read: { type: 'boolean', description: 'true only if you read the method and experiment sections of the actual paper' },
    code_url: { type: 'string', description: 'verified official repository, or empty' },
    code_notes: { type: 'string', description: 'licence, framework, dependencies, last activity, pretrained weights; "not checked" if you could not' },
    hypothesis: { type: 'string', description: 'one falsifiable sentence about OUR data and OUR metrics' },
    mechanism: { type: 'string' },
    cluster: { type: 'string', description: 'mechanism family slug, reuse the one in your input unless it is wrong' },
    targets: { type: 'array', items: { type: 'string' } },
    route: { type: 'string', enum: ROUTES },
    adaptation: { type: 'string', description: 'the concrete changes for our data and harness' },
    packages_needed: { type: 'array', items: { type: 'string' } },
    weights_needed: { type: 'array', items: { type: 'string' } },
    build_hours: { type: 'number' },
    screen: { type: 'string', description: 'the cheap screen: arm, baseline, folds and seeds, metric, kill line' },
    gpu_hours_screen: { type: 'number' },
    full: { type: 'string', description: 'the full experiment if the screen passes' },
    gpu_hours_full: { type: 'number' },
    expected_gain: { type: 'string', description: 'which number moves and by how much, with your probability' },
    bench_role: { type: 'string', description: 'role in the benchmark suite (baseline family, track, metric, protocol rule) or "none"' },
    risks: { type: 'string' },
    depends_on: { type: 'string' },
    verdict: { type: 'string', enum: VERDICTS },
    void_evidence: { type: 'string', description: 'required for VOID: the exact earlier run (BRIEF section 5 row or file) that tested the same mechanism under the same conditions' },
    priority: { type: 'integer', description: '0 to 100' },
  },
  required: ['n', 'title', 'fulltext_read', 'hypothesis', 'route', 'adaptation', 'screen', 'gpu_hours_screen', 'verdict', 'priority'],
}

const CRIT_SCHEMA = {
  type: 'object',
  properties: {
    n: { type: 'integer' },
    verdict: { type: 'string', enum: VERDICTS },
    priority: { type: 'integer' },
    route: { type: 'string', enum: ROUTES },
    cluster: { type: 'string' },
    changes: { type: 'string', description: 'what you changed in the card and why; "none" if you agree' },
    fatal_flaws: { type: 'string', description: 'reasons the screen as written could mislead (leakage, unfair baseline, wrong metric, cannot detect the effect); "none" if none' },
    merge_with: { type: 'string', description: 'other mechanisms or papers this should share one experiment with; empty if none' },
    one_line: { type: 'string', description: 'the card in one line for the plan: hypothesis, screen, cost' },
  },
  required: ['n', 'verdict', 'priority', 'route', 'cluster', 'changes', 'fatal_flaws', 'one_line'],
}

const COMMON = `Project context to read first (Read tool):
- ${ROOT}/BRIEF.md (all of it: facts, numbers to beat, what was run and under which conditions, the benchmark vision, team rules in section 7).
- ${ROOT}/benchmark/PROTOCOL_DRAFT.md sections 0, 3.5, 5.5 and 6 (the evaluation sets, the headline metrics, the tracks).
- ${ROOT}/harness/DESIGN.md sections 1.10, 2 and 6 (what the training harness already supports without new packages: segmentation_models_pytorch 0.5.0 decoders and losses, timm 1.0.30 backbones incl. DINOv3 and ConvNeXt, local weights; what needs a separate venv).

Screening instrument (fixed by the lead): module-grouped 5-fold cross-validation on the 532 train + val cells (CV5-G), 2 seeds to screen, 5 seeds for a table entry; development reads of unseen-module behaviour on F51 / H36 only; the legacy test set (50 cells) and E1 (106 unseen-module cells) stay sealed until a final confirmation. The house reference is U-Net++ / ResNet-34 with the encoder-preserving fine-tune (PF); one house run is about 1.1 GPU-h on an RTX A6000, so CV5-G at 2 seeds is about 11 GPU-h per arm. Available: 8 RTX A6000 (shared, often 2 to 6 free) and one 32 GB GPU. One month in total.

Verdict vocabulary:
- RUN_NOW: worth a screen in the first wave.
- RUN_AFTER_GATE: worth a screen once a named cheaper result or build step exists.
- BENCH_ONLY: not expected to raise our best score, but a credible benchmark must include it as a baseline, a track or a rule.
- PARKED: not tested for cost or priority reasons. This is NOT a closure; the hypothesis stays open and untested.
- VOID: allowed only with evidence that the same mechanism was already tested here under the same conditions (name the BRIEF section 5 row or the file). "Probably will not help" is never VOID.`

const cardPrompt = p => `You are a paper analyst on a research team whose goal is the highest-scoring model and a new benchmark for electroluminescence (EL) solar-cell defect segmentation, with one month left. You own ONE paper and turn it into a hypothesis card that an engineer can run.

Your paper: rank ${p.n}: "${p.title}". Your input record (what the scouts and judges already wrote about it) is ${ROOT}/cards/in/${String(p.n).padStart(3, '0')}.json. Read it first.

${COMMON}

Tools: load the Research MCP tools with ToolSearch, query "${MCP}" (max_results 10); load web tools with ToolSearch, query "select:WebSearch" (and use the web-fetch agent or WebFetch if you have it). If a call fails, wait and retry up to 3 times.

Do this:
1. Get the paper itself. Use get_paper, then fetch_fulltext and read_paper on the method, experiment and ablation sections (use section selections, not the whole paper). ${p.pub ? 'A publisher download is allowed for this paper if no arXiv or open-access copy exists.' : 'Use arXiv or open-access copies only for this paper (publisher downloads are capped per day and reserved for other papers); if there is no free copy, use search_snippets on this paper id and the abstract, and set fulltext_read to false.'} Never invent what the paper says.
2. Check the evidence like a reviewer: dataset sizes, whether baselines were tuned, whether gains hold in ablations, what happens with few labels or thin structures, any reported failure cases.
3. Check the code: find the official repository (WebSearch), and note licence, framework, dependencies, pretrained weights, last activity. Say "not checked" if you cannot verify it.
4. Design the adaptation for OUR data: 1-channel EL images, 512 px, 478 to 532 labelled cells, 24 classes, crack labels 1 to 2 px wide with about 1 px jitter and a source-dependent width, 42 training cells with inactive, five sources, half-cut cells absent from training. Say exactly what changes in the model, loss, data pipeline or training recipe, and which harness route it takes (config_only if the existing registry covers it).
5. Design the cheapest decisive screen on CV5-G (or a CPU-only pre-check if one can kill or support the idea first), with the baseline, the metric from the headline card, a kill line that a real effect of plausible size would clear given 2 seeds, and its GPU-hours. Then the full experiment if it passes.
6. Decide the verdict and a priority 0 to 100 (expected gain x probability x feasibility in a month, or benchmark necessity for BENCH_ONLY).
7. Write the card to ${ROOT}/cards/${String(p.n).padStart(3, '0')}_${p.slug}.md with these headings: Paper (id, venue, year, links), What it claims (R, with numbers), Evidence check, Code, Hypothesis for us, Adaptation, Harness route and needs, Screen, Full experiment, Expected gain, Benchmark role, Risks and overlaps with earlier runs, Verdict. Plain English, no em-dashes, measurements over adjectives; tag R (paper), E (our files), S (your judgement).
8. Return the structured card. n is ${p.n}.`

const critPrompt = (p, card) => `You are the critic for one hypothesis card on a research team whose goal is the highest-scoring model and a new benchmark for electroluminescence (EL) solar-cell defect segmentation, with one month left. Be the reviewer the project's earlier critics were: nothing launches on a guess, and nothing is closed without evidence.

${COMMON}

The card: ${ROOT}/cards/${String(p.n).padStart(3, '0')}_${p.slug}.md (rank ${p.n}: "${p.title}"). Read it in full. The analyst's structured summary:
${JSON.stringify(card)}

Check, and fix in the card where needed:
1. Is the hypothesis falsifiable on our data, and does the screen actually test it? Would a null be informative (enough power, right metric, right baseline, no leakage between folds, no test or E1 use)?
2. Is the adaptation right for 1 to 2 px jittered crack labels, 42 inactive training cells, 24 classes and five sources, or is it copied from the paper's setting?
3. Is the evidence in the paper as strong as the card says? You may verify a claim with the Research MCP tools (ToolSearch query "${MCP}") or a web search; do not re-read the whole paper.
4. Does BRIEF section 5 already contain the same mechanism under the same conditions? If yes the verdict is VOID with that evidence; if only something similar was run, say what differs.
5. Cost realism: build hours, packages, weights, GPU-hours.
6. Which other mechanisms should share one experiment with it (same arm can test several papers)?
7. Set the final verdict, priority, route and cluster. Be decisive; use the whole priority range.

Append a section "Critic review" to the card file with your findings and any changed fields (do not delete the analyst's text). Then return the structured result. n is ${p.n}.`

const pad = n => String(n).padStart(3, '0')

phase('Card')
const results = await pipeline(
  PAPERS,
  p => agent(cardPrompt(p), { label: `card:${pad(p.n)}:${p.slug}`, phase: 'Card', model: 'opus', effort: 'high', schema: CARD_SCHEMA }),
  (card, p) => {
    if (!card) return null
    return agent(critPrompt(p, card), { label: `crit:${pad(p.n)}:${p.slug}`, phase: 'Critique', effort: 'medium', schema: CRIT_SCHEMA })
      .then(c => ({ p, card, crit: c }))
  },
)
const done = results.filter(Boolean)
const failedCards = PAPERS.filter(p => !done.some(x => x.p.n === p.n)).map(p => p.n)
log(`cards done ${done.length}/${PAPERS.length}; failed: ${failedCards.join(',') || 'none'}`)

// ---------- Plan ----------
phase('Plan')
const fin = x => {
  const c = x.crit || {}
  return {
    n: x.p.n, title: x.p.title,
    verdict: c.verdict || x.card.verdict, priority: c.priority == null ? x.card.priority : c.priority,
    route: c.route || x.card.route, cluster: c.cluster || x.card.cluster || 'other',
    line: c.one_line || x.card.hypothesis, merge: c.merge_with || '',
    gpu_screen: x.card.gpu_hours_screen, gpu_full: x.card.gpu_hours_full, build_h: x.card.build_hours,
    pkgs: (x.card.packages_needed || []).join(', '), weights: (x.card.weights_needed || []).join(', '),
    bench: x.card.bench_role || '', flaws: c.fatal_flaws || '', critic: !!x.crit,
  }
}
const finals = done.map(fin).sort((a, b) => (b.priority || 0) - (a.priority || 0))
const row = f => `#${pad(f.n)} [${f.verdict} p${f.priority}] (${f.cluster}; ${f.route}; screen ${f.gpu_screen == null ? '?' : f.gpu_screen} GPU-h, build ${f.build_h == null ? '?' : f.build_h} h${f.pkgs ? '; pkgs: ' + f.pkgs : ''}${f.weights ? '; weights: ' + f.weights : ''}) ${f.title} :: ${f.line}${f.merge ? ' || share with: ' + f.merge : ''}${f.bench && f.bench !== 'none' ? ' || bench: ' + f.bench : ''}`
const table = finals.map(row).join('\n')

const PLAN_LENSES = [
  { id: 'score', text: 'Plan for the best model. Order the experiments so that the first week tests the ideas with the highest expected gain on crack, inactive, unseen modules and the weak classes, merging papers that share one arm, and so that later arms can build on a winner (base recipe first, then data and labels, then architecture, then inference).' },
  { id: 'bench', text: 'Plan for the benchmark. Choose the method suite a credible EL segmentation benchmark must contain (published EL methods, classic and recent architectures, losses, foundation models, semi-supervised and data methods), the tracks and the order in which to fill the tables, so that a minimum credible table exists within 10 days and grows after.' },
  { id: 'ops', text: 'Plan for execution. Group the experiments by harness route and by what they need (config only, new loss, new model code, data pipeline, external codebase, packages, gated weights), estimate build hours and GPU-hours per wave, find the critical path and the blockers, and propose which waves run on which machine. Flag every package or gated download that needs the user\'s OK.' },
]
const plans = await parallel(PLAN_LENSES.map(l => () =>
  agent(`You are a planner on a research team whose goal is the highest-scoring model and a new benchmark for electroluminescence (EL) solar-cell defect segmentation, with one month left (about 12 Dec 2026).

${COMMON}

Below are ${finals.length} hypothesis cards after critic review, one line each, sorted by priority. The full cards are in ${ROOT}/cards/ (file names start with the three-digit rank); open the ones you need.

Your lens: ${l.text}

Write ${ROOT}/plan/PLAN_${l.id}.md: waves of experiments (wave 1 = first 3 days), each experiment with the card numbers it covers, the arm, the baseline, sets and seeds, GPU-hours, build hours, needs, and the decision it feeds. Every card must appear exactly once in your file: in a wave, in a "parked, untested" list, or in a "void, with evidence" list. Total the GPU-hours per wave. Plain English, no em-dashes. Then return a summary under 40 lines.

Cards:
${table}`, { label: `plan:${l.id}`, phase: 'Plan', effort: 'high' }).then(t => ({ id: l.id, text: t }))))

const counts = {}
for (const f of finals) counts[f.verdict] = (counts[f.verdict] || 0) + 1
return {
  n_papers: PAPERS.length, n_cards: done.length, failed_cards: failedCards, verdict_counts: counts,
  top: finals.slice(0, 60).map(f => ({ n: f.n, v: f.verdict, p: f.priority, cl: f.cluster, r: f.route, t: f.title, g: f.gpu_screen })),
  plans: plans.filter(Boolean),
}
