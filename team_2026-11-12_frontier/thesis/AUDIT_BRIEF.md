# Thesis audit brief (27 Nov 2026)

Goal: an independent check of the MTP thesis draft (last built 23 Nov 22:07, 126 pages) so that it holds **no factual mistakes**. Fix only verified errors. Do not restyle prose.

## Where things are
- Working copy (edit here only): `/tmp/claude-1000/-home-yugma-mtp-research/2702d0bd-61fc-421d-8eb2-2bf4956d23c8/scratchpad/thesis_work/`
  - `chapters/chNN_*.tex` (the text), `chapters/chNN_*_NOTES.md` (the writer's source for every number), `main.tex`, `thesis_tables.tex` + `THESIS_TABLES.md` + `SOURCES.tsv` (generated, 1,600+ traced values), `RELATED_WORK.md`, `INFERENCE_COST.md`, `GAPS.md`, `TRACE_REPORT.md`.
  - Do not edit generated files (`thesis_tables.tex`, `related_work.tex`, `SOURCES.tsv`, `THESIS_TABLES.md`). If one is wrong, report it.
- Pristine copy for diffs: `.../scratchpad/thesis_orig/` (never edit).
- Compiled PDF text: `.../scratchpad/thesis.txt` (pdftotext of the 23 Nov PDF).
- Primary records live on the server `giant`: `ssh -o BatchMode=yes noob@172.18.22.20`, research root `/home/yugma/mtp/research/` (benchmark at `team_2026-11-12_frontier/`, lead log `team_2026-11-12_frontier/log.md`, results under `team_2026-11-12_frontier/benchmark/...`, handbook `handbook/`). A local copy of the older research repo is at `/home/yugma/mtp/research/` (handbook docs 00 to 22, guide context `to_human/ee511_deck/guide_ctx/` incl. `THESIS_TABLES.md`, `FINAL_OPENING_READ.md`, `FINAL_OPENING_READ_ERRATA.md`, `t3b_verdict.txt`, `INFERENCE_COST.md`, `RELATED_WORK.md`).
- **Server is read only for you**: only read commands (cat, sed -n, grep, ls, md5sum, find). No writes, no training, no queue/tmux/process changes, no installs. Never print credentials, tokens or keys.

## What counts as an error (fix it)
1. A number in the text that differs from its primary source (result file / read output / verdict file), or from the traced table cell for the same quantity. Rounding is fine only if it is correct rounding.
2. The same quantity given two different values in two places of the thesis (check across chapters, abstract and tables, not only your own).
3. A verdict / robustness check / reading mixed up: a verdict is a rule fixed before the run; a robustness check is printed beside and decides nothing; a reading is interpretation. "n.d." means not detectable (interval includes 0 or effect below the margin M = 0.010); it must never be worded as "worse" or "no effect".
4. Old-era numbers (before 7 Oct: SemiCE Mean Teacher, ALHVR-20, the first pipeline) presented as valid current results instead of history / reproduction records.
5. A claim stronger than its evidence (e.g. a selection-biased CV5 number called a test result; a few-shot result called zero-shot; E1 called unseen after opening #9).
6. Wrong cross-references, wrong chapter / table / figure numbers in the text, wrong dates or counts (cells, clusters, seeds, folds).
7. Leftover placeholders (\PENDING, \CITE, \FIG with no file), "??", or dash characters (em/en dash used as punctuation; the thesis uses none).

## What is NOT an error (leave it)
- Wording you would phrase differently. Style, order, length.
- A value you cannot locate: do not change it; list it under UNVERIFIED with what you searched.

## Rules for every change
- Smallest possible edit, in the working copy only, in your own files only.
- Log each change in your report file (see your task) as: file:line | old text | new text | evidence (source path:line, quoted exactly).
- If two sources disagree with each other, do not pick one: report under CONFLICTS.
- Do not add new claims or new numbers that are not in a primary record.
- Keep the thesis's existing conventions: four decimals for deltas and intervals as `+0.0430 [+0.0013, +0.1043]`, no em dashes.

## Report format (your report file, Markdown)
1. CHANGES (table as above)
2. CONFLICTS (sources disagree)
3. UNVERIFIED (could not find a source)
4. CROSS-CHAPTER (inconsistencies involving chapters you do not own; do not edit those, describe them)
5. One line: how many numbers you checked, how many against a primary record vs only against NOTES/SOURCES.
