# Project-record appendices: writer brief (27 Nov 2026)

The user wants the thesis to also serve as a full **project report**: everything the team did must be in it. The main chapters (ch01 to ch12) already cover the benchmark, the final recipe, E1 and the few-shot track. You write ONE new appendix that records, chronologically and completely, one period or workstream that the main text leaves out or only summarises. Read the main chapters first so you do not repeat them: point to them instead (`Chapter~\ref{ch:legacy}`, `Table~\ref{tab:T21}` and so on).

## Where things are
- Thesis working copy: `/tmp/claude-1000/-home-yugma-mtp-research/2702d0bd-61fc-421d-8eb2-2bf4956d23c8/scratchpad/thesis_w3/` (main.tex, chapters/*.tex, chapters/*_NOTES.md, THESIS_TABLES.md, references.bib, RELATED_WORK.md). Compiled text of the current thesis: `.../scratchpad/thesis27.txt`.
- Local research repo (laptop; older snapshot to 4 Nov, plus deck work): `/home/yugma/mtp/research/`: `handbook/00..22_*.md` (the project handbook: read the docs for your period in full), `handbook/sources/` (session records, old-era reports, chat handoffs, protocols, team folders), `results/`, `analysis/`, `data_analysis/`, `literature/notes/`, `team_*` folders.
- Server `giant` (current, canonical): `ssh -o BatchMode=yes noob@172.18.22.20`, root `/home/yugma/mtp/research/` (same layout plus `handbook/23_*.md`, `handbook/24_*.md`, `team_2026-11-12_frontier/` with `log.md`, `results/`, `benchmark/`, `harness/`, `cards/`; `team_2026-11-04_thermal/`; `team_2026-10-31_next/` incl. `e1_openings.md`).
- **Server is read only for you**: cat, sed -n, grep, ls, find, md5sum only. No writes, no training, no queue/tmux/process changes, no installs. Never print credentials or tokens.

## What to write
- `chapters/app_<your_id>.tex`: one `\chapter{...}\label{app:<your_id>}` (it is placed after `\appendix`, so it becomes an appendix chapter), with `\section`s in date order. Target 4 to 9 pages. Plain, precise prose; short tables (`booktabs`, `\begin{table}[htbp]...\end{table}` with `\caption` and `\label{tab:<your_id>-...}`) where a list of experiments is clearer as rows.
- `chapters/app_<your_id>_NOTES.md`: for EVERY number and dated fact in your .tex, the source path and line (local or server path), quoted. A reviewer will check each one.
- For each experiment or decision: what was asked, what was run (data, split, labels, seeds, steps where recorded), the result with its interval if one exists, the verdict under the rule of the time if there was a rule, and what it led to. Include failures, bugs, stopped and invalid runs, with the reason.

## Hard rules
1. **Every number from a file.** Copy, do not recompute (a derived value needs its formula in NOTES). If you cannot find a source, leave the number out.
2. **Keep three things apart**: verdict (rule fixed before the run), robustness check (printed beside, decides nothing), reading (interpretation; mark it "our reading").
3. **n.d.** = not detectable (interval includes 0 or below the margin). Never write it as "worse", "no effect", "does not matter", "equals".
4. **Old-era numbers** (before 7 Oct 2026: the first pipeline, SemiCE Mean Teacher, ALHVR-20, the lost implementation, the poster numbers) are history and reproduction records only. Say so where they appear (each such table caption and the section opening must state the conditions: old pipeline, test set scored in every run, overlapping splits as later found). Never present them as valid results.
5. **Scale**: our numbers are 0 to 1; published papers often print percent. Label percent values with `\%`. Name the metric convention for every IoU (pooled vs per image, background in or out, standard vs a paper's own convention).
6. **Wording conventions of this thesis**: no em or en dashes as punctuation (use commas, colons, parentheses; `$-$` for minus); four decimals for deltas and intervals as `+0.0430 [+0.0013, +0.1043]` where the source gives four; no host names, user names or file-system paths in the .tex (say "the training machine" / "the second machine"; paths go in NOTES only); do not name the industry partner (write "the industry partner"); people other than the two students are not named except published authors (the team member who proposed ideas may be called "a team member").
7. Cite only keys that exist in `references.bib`. If a paper you need is not there, write the reference in plain text in NOTES under MISSING_CITES and use `\CITE{short description}` in the .tex; do not invent BibTeX.
8. Do not edit any file other than your two files. Do not compile.
9. Ensure LaTeX is valid: escape `%`, `&`, `_`, `#`; math in `$...$`; no unicode minus or special characters that pdfLaTeX/XeTeX would choke on (use `$\times$`, `$\pm$`, `$\geq$`, `\%`).

## Final message
List your two file paths, the page estimate, the number of numbers in NOTES, and anything you could not source (UNSOURCED) or found contradictory (CONFLICTS).
