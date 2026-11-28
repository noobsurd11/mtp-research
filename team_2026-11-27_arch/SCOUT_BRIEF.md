# Scout brief

Read `CONTEXT.md` (same folder) first, then the directions files of the 12 Nov sweep that overlap your family (`ref/directions_1112/`), so you know what was already searched.

## Your job
Exhaustive search of one family (given in your task) for papers that could improve our model, in any field: natural images, medical, remote sensing, cracks in concrete/pavement, vessels, roads, industrial inspection, documents, anything. Not only supervised: self-, semi-, weakly-, un-supervised, foundation models, generative models, test-time methods. Priority venues: CVPR, ICCV, ECCV, NeurIPS, ICLR, ICML, AAAI, MICCAI, WACV, BMVC; journals TPAMI, IJCV, TIP, TMI, MedIA, Pattern Recognition, TGRS, Automation in Construction, Solar Energy, Progress in PV, IEEE JPV. Include strong arXiv preprints 2024 to 2026. Cover 2015 to now; weight 2023 to 2026.

## How
- Use the Research MCP (`search_papers`, `get_paper`, `get_citations`, `get_references`, `similar_papers`, `search_snippets`; load them with ToolSearch "select:mcp__claude_ai_Research_MCP__search_papers,..."). Run **many** queries (at least 25), with synonyms; snowball: for the 5 to 10 most important papers, check who cites them (`get_citations`) and what they cite. Semantic Scholar is rate-limited; if it errors, keep going with the other sources and retry later.
- Fetch full text (`fetch_fulltext` / `read_paper` with specific sections) only for your top 10 or so; publisher downloads are capped per day.
- Cite only papers returned by the tools, with their ids. Never invent a paper, number or venue. If you know of a paper the tools cannot find, list it under NOT_FOUND with what you searched.
- Check every paper against `ref/MASTER.tsv` (by id and by title): NEW, or the existing pid.

## Output (in `scouts/<your_id>/`)
1. `papers.tsv`, one row per paper, tab-separated, header:
   `paper_id	title	year	venue	family	new_or_pid	what_it_is	why_it_could_help_us	cost_to_try	risk_or_reason_against	code_available	fit_score_0_to_5`
   `what_it_is` and `why...` are one or two plain sentences each, specific to OUR task (1 to 2 px cracks, rare inactive regions, 532 grey-scale cells, unseen module layouts, tolerant metric, small data). `cost_to_try`: config-only / new head or loss / new backbone / new pipeline / new data. `code_available`: yes (repo) / no / unknown.
2. `REPORT.md`: queries run (list), counts (found, after dedupe, NEW vs already in MASTER), your **top 10** with a short argument each (what result in the paper supports it, on which data, and how it maps to our failure modes: recall on unseen modules, half-cut layout, thin-line precision, rare inactive), and **NOT_FOUND**.
3. Do not train, do not touch any server, do not edit files outside your folder.

## Rules
Every claim about a paper comes from the paper (abstract or full text you read through the tools). Say "abstract only" when you did not read more. Plain English, no hype. Final message: counts, the top 10 ids with one line each, and the path of your folder.
