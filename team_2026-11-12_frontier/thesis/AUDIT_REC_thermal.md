# Audit of the thermal appendix (27 Nov 2026)

Files: `chapters/app_thermal.tex`, `chapters/app_thermal_NOTES.md`. Originals before the audit are backed up outside the working copy (checker scratchpad `app_thermal.tex.orig`, `app_thermal_NOTES.md.orig`).

Source keys as in NOTES: TF = server `team_2026-11-04_thermal/`; LOG = `TF/log.md`; S4 = server `team_2026-11-12_frontier/results/severity/S4_DTU_THERMAL.md`; FLOG = server `team_2026-11-12_frontier/log.md`; H22 = `handbook/22_thermal_desk_study.md` (local and server md5 d7b88c3e, identical). Each primary file was read on the server through `cat` (read only).

## CHANGES (.tex)

| # | file:line (after edit) | old | new | evidence |
|---|---|---|---|---|
| C1 | app_thermal.tex:28 | "a brief from the project coordinator" | "a brief from a collaborator" | lead's instruction (role unconfirmed); OMT l.1 "# Om: thermal (IR) direction (3 Nov 2026)" |
| C2 | app_thermal.tex:154 | "the project coordinator's decisions arrived" | "a collaborator's decisions arrived" | lead's instruction; OMD l.1 |
| C3 | app_thermal.tex:281 | "the report to the project coordinator had not been sent" | "the report to a collaborator had not been sent" | lead's instruction; LOG l.150 "the report to the user and Om was NOT sent" |
| C4 | app_thermal.tex:334 | "the report to the project coordinator, whose addendum" | "the report to a collaborator, whose addendum" | lead's instruction |
| C5 | app_thermal.tex:335 | "stayed with the project coordinator" | "stayed with a collaborator" | lead's instruction; H22 l.156 "**Open for Om:** ..." |
| C6 | app_thermal.tex:71 | "the brief named that gap as missed cracks in half-cut cells with scuff streaks" | "the team's brief named that gap ..." | The collaborator's brief (OMT l.5, verbatim) does not mention scuff or half-cut; the team README does: README l.16 "75% of missed crack px sit on scuff + half-cut cells". In this section "the brief" refers to the collaborator's brief (l.28). |
| C7 | app_thermal.tex:157-158 | "our model was not run on these sets;" | "our model was not run on these sets in the 4 November study;" | Unqualified, the sentence is false for the record as a whole: S4 l.42 "Models. The PF baseline ... seed 5, folds 0 to 4 ... the predict path ... CPU" was run on A3 EL crops on 15 Nov (S4-Q3). |
| C8 | app_thermal.tex:302 | "the EL dark fraction does not track FF loss" | "the EL dark fraction is label-invalid against FF loss (its interval includes 0)" | Wording rule 3 (n.d. never as "no effect"). S4 l.77: "all non-soiling \| 31 \| +0.006 [-0.380, +0.425] \| label-invalid (< 0.3)". The interval reaches +0.425, so "does not track" is stronger than the source; the verdict word is kept. |
| C9 | app_thermal.tex:303 | "the most EL darkness and the largest maximum-power loss" | "the most EL darkness and a large maximum-power loss" | S4 l.114: "diode modules have the most EL darkness (missing substrings) and large Pmax loss, but FF does not see it". "largest" is not in the source. |
| C10 | app_thermal.tex:332-333 | "pick 1's A3 screening table by class and its recall readout (R1, R2)" | "pick 1's A3 screening readouts as frozen, the class table with its AUROCs (R1; the severity track gave only per-cause medians of $S_\mathrm{IR}$) and the recall readout (R2)" | The appendix itself (l.304-305) reports per-cause S_IR medians computed by R1's frozen S_IR definition (S4 l.32 "pick 1 R1 as amended by Amendment 6 rule 1"; S4 l.97-102), so "the class table was not done" contradicted the page. What stays undone: R1a in its frozen form (PP1 l.25 "n modules, median S_IR (IQR), median ΔT_max") and R1b (PP1 l.26 "AUROC of S_IR for each defect class"), neither in S4; R2 not done (LOG l.150; HB15 l.312 row 3, 18 Nov). |

## CHANGES (NOTES)

| # | Row | Change | Evidence |
|---|---|---|---|
| N1 | Wording choices, l.18 | "the project coordinator" changed to "a collaborator", with the reason | lead's instruction |
| N2 | 16 Nov review row | citation "FLOG l.83, l.86 ... 'Severity wording fixes done by the lead ... no existing number changed'" replaced: that quote does not exist and l.86 is an unrelated tick. Correct source: FLOG l.83 (end of line) "Owed: the reviewer's four wording fixes (F2.1, F3.3, F4.1, F4.2; no number changes)" + S4 l.117 "[wording fixed 16 Nov, review F4.1]" | FLOG l.83, l.86 read in full |
| N3 | decisions (3) row | adds that "not run" applies to 4 Nov (S4 l.42) | C7 |
| N4 | all-module 3b-R1 reading row | verdict quote added (S4 l.77), "large" Pmax loss quote (S4 l.114) | C8, C9 |
| N5 | E1 gap row | notes that the gap is named in README l.16, not in OMT | C6 |
| N6 | not-done row | R1 narrowed with PP1 l.25-26 and S4 l.32, l.97-102 | C10 |
| N7 | UNSOURCED, l.~196 | "report to the project coordinator" changed to "report to the collaborator" | N1 |
| N8 | new section "Audit 27 Nov" | points to this file | |

## REMOVED
None. Every number in the .tex has a primary source.

## CONFLICTS
1. **Main text wording vs this appendix (n.d. wording).** ch10_deployment.tex l.71 (and THESIS_TABLES l.617, handbook 23 l.105): drone thermal "does not track FF loss ... ($\rho$ 0.19)". The source verdict is "not a proxy" (S4 l.84: +0.192 [-0.305, +0.626], interval includes 0). By rule 3 this should read as the verdict ("not a proxy by the pre-set bar"), not as "does not track". The appendix now uses verdict words only. The values agree; only the main-text wording is stronger. Not edited (outside my files).
2. **Main text: "soiling strongly: 16 to 38 °C".** ch10 l.72. S4 l.102: soiling 1 median 4.2 [1.2, 22.8], soiling 2 median 18.3 [0.7, 37.5]; S4 l.115: "most soiling modules (up to 38; two near 1)". So "16 to 38 °C" holds for diode modules (16.5 to 29.7) and some soiling modules, not for soiling as a class. The appendix gives the per-cause medians (4.2 and 18.3) correctly. Main text not edited.
3. Writer's conflicts, re-checked against the primary files and confirmed as stated: (a) A1 IR exposure 180 s by file names vs 5 min in Colvin 2023 (LOG l.117 "IR after 5 min at Isc vs 180 s in names"; H22 l.86; the .tex gives both); (b) pick 3 decision time: retrospective log 13:28 (LOG l.149), P3R l.3 "~13:3x", LOG l.113 notes it at 13:35; "about 13:30" in the .tex is within that range; (c) T15 margin 0.66 vs 0.69 mV (LOG l.74 vs l.123; not in the .tex); (d) A3 "43 degraded" (abstract) vs 31 degraded + 12 soiled (slides) (H22 l.88; RANK l.11); the .tex says "43 in all".

## OPEN
1. The claim that cracks isolating nothing show no hot spot rests on Dhimish and Lazaridis 2021 via the ideas file (`TF/ideas/ideas_long.md` l.24: "no hot spot for Dhimish's 'micro-crack' mode"); the mapping to Köntges mode A is flagged as ours in the .tex. I did not read the paper itself.
2. The JRC finding (dark IR "few local information") is tagged in the dataset table as "[R: snippet]" with the study's data "unconfirmed" (DT l.67). The .tex states it as the study's finding, with `\CITE{...}` (no bib key). Someone should check it against the report before the citation is finalised.
3. Table `tab:thermal-physics`: the shunt / PID row's "hot spot" is a sourced (R) entry in H22 l.73 with no citation in the table, but the caption calls uncited entries "expected" (judgement) only when marked so. A reader cannot tell this one is sourced. This is a style point and was left as is.
4. NOTES quotes still contain the collaborator's first name and the industry partner's name (in quoted source text and in the "Wording choices" line). Neither appears in the .tex. The lead decides whether NOTES must be scrubbed too.

## Verification scope
All numbers, counts, dates and times in the .tex (about 165) were checked against the primary files on the server: LOG, README, OMT, OMD, PP1 (plan_pick1.md), G0.md, G0v2.md, PICK3_A1_REPORT.md, download_verified.md, dataset_table.md, ranked_ideas.md, top3.md, SUMMARY.md, capture_plan.md, replan_pick2.md, factcheck.md, S4, FLOG and handbook 15. H22 was used as the primary only for the desk-study physics table and the summary lines it alone records (process-fault list, dataset rows), each cross-checked with LOG or DT where a line existed. None was checked against NOTES alone. Every NOTES line reference was re-opened; one was wrong (N2). Every `\ref` target exists (`sec:deploy-thermal`, `sec:deploy-power` in ch10; `ch:t3b`; `ch:legacy`). Every `\citep` key exists in references.bib (`kontges2011risk`, `dhimish2021hotspots`, `delpradosantamaria2025drone`, `polenghi2026data`). `\CITE` is defined in main.tex. Labels are unique across `chapters/*.tex`. Environments are balanced (13/13). The .tex has no non-ASCII characters, no dash punctuation, no host, user or path names, and no partner or collaborator name. Note for the lead: main.tex does not yet `\input` app_thermal.tex, so the appendix will not appear in the build until it is added after `\appendix`.
