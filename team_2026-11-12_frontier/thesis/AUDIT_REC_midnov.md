# Audit of the project-record appendix `midnov` (chapters/app_midnov.tex, app_midnov_NOTES.md), 27 Nov 2026

Auditor: independent checker under RECORD_AUDIT_BRIEF.md. Sources were opened directly: the laptop handbook docs 17 to 21 (md5 equal to the server copies, checked 27 Nov), the server E1 ledger `team_2026-10-31_next/e1_openings.md` (3ead9149) and `verify_skr2c.md` (0f7237da), `team_2026-10-31_next/verify_pf2.md`, the session record of 3 to 4 Nov, `om_2026-10-31.md`, `ideas/found_scripts/t9_rf_sets.tsv`, and the thesis (thesis_tables.tex T17 and T21, ch04, ch05). Line numbers below are of the .tex after the edits (the caption edit at 277-280 added one line; later lines moved down by one).

## CHANGES

| file:line | old | new | evidence (path:line, quoted) |
|---|---|---|---|
| app_midnov.tex:35 | "shared with another user's process that had to keep 2\,GB free" | "shared with another user's process, for which at least 2\,GB had to stay free" | handbook/19_feature_learning_and_100pct_plan.md:59 "Root's `finllm_chat.py` (5.9 GB) must never run out of memory, so ≥ 2 GB stays free at all times." (the 2 GB is headroom kept free, not something the process keeps) |
| app_midnov.tex:72 | "still passed with a free crack logit bias on both sides" | "still passed with a free logit bias (logit adjustment) on both sides" | handbook/18_experiments_trackD_trackM.md:59 "With the free bias on both sides it still passes: +0.037 (thr 0.013)"; :42 "LA (logit adjustment). z_c − τ·log π_c ... The free-bias yardstick" (all classes, not a crack-only bias) |
| app_midnov.tex:102 | "Tc $-$ R BETTER with BMRK recall $+0.05$" | "... BMRK recall $\geq +0.05$" | handbook/18:173 "\"Ts − Tc BETTER, or Tc − R BETTER with BMRK recall ≥ +0.05\"" |
| app_midnov.tex:189-190 | caption "... averaged per ResNet-34 stage, at step 20,000 (training only, ...)" | adds "(first column: the MIM encoder after pretraining; ...)" | handbook/19:143 column header "MIM moved it: cos(MIM, ImageNet)" (the pretrained encoder, not a step-20,000 fine-tune) |
| app_midnov.tex:220 | "Gates 1 to 4 (bit-identity of the new switches when off)" | "Gates 1 to 4 (bit-identity checks of the new switches when off and of validation off)" | handbook/19:264 "4. Val-off identity (speed-up): loss/lr lines bit-identical for 2,000 steps" |
| app_midnov.tex:252 | "gained $+0.05$ E1 crack recall" | "gained at least $+0.05$ E1 crack recall" | handbook/19:402 "kill unless a variant gains ≥ +0.05 E1 recall on the 29 scuff + half-cut cells" |
| app_midnov.tex:266 | "\section{The team member's eleven ideas and PF2 ...}" | "\section{A collaborator's eleven ideas and PF2 ...}" | lead's instruction (role unconfirmed) |
| app_midnov.tex:268 | "a team member accepted" | "a collaborator accepted" | as above |
| app_midnov.tex:277-280 | caption "The team member's eleven ... CPU checks on validation, the E-SCDD cells and earlier records; no new test50 or E1 read." | "A collaborator's eleven ... CPU checks on validation, the E-SCDD cells and earlier records; the checks of ideas 1 and 7 and the reviewer's checks also read E1 on 31 Oct, reads the ledger lists among those before the E1 policy; A1 to A6 opened no test50 or E1 file." | S:team_2026-10-31_next/e1_openings.md:12 "31 Oct (before / around the policy): calib's idea-1 and idea-7 backfill (FINAL, SUP5, SUPPF5, MIMPF5, CP5 on E1), judge's checks and idea-1 oracle split"; handbook/21:151 "(val / `_rf` records; no test or E1 file opened)" |
| app_midnov.tex:343-344 | "and doubled crack on crack-free E1 cells ($\times$2.4)" | "and raised crack on crack-free E1 cells $\times$2.4" | handbook/20:170 "crack px on crack-free E1 cells ×2.4" (2.4 is not "doubled") |
| app_midnov_NOTES.md:9 | "a team member" | "a collaborator" (role unconfirmed) | lead's instruction |
| app_midnov_NOTES.md (§SKR2C) | SR1104 "l58" | SR1104 "l24" (also l69) | handbook/sources/session_records/SESSION_RECORD_2026-11-03_to_11-04.md:24 "**12 Nov:** the laptop OS was reinstalled (disk 52 GB free, E); no agent survived" (l58 is a 4 Nov thermal row) |
| app_midnov_NOTES.md | (new entries) | sources added for each change above; F51/H36 module check; conflicts 6 and 7 | see NOTES |

## REMOVED
- The caption claim "no new test50 or E1 read" for the eleven-idea checks (unsupported, contradicted by the ledger line 12; replaced by the sourced statement above). No other claim removed.

## CONFLICTS (between sources; the .tex follows the source named)
1. protocol_100 opening 1 start: ledger l11 "00:59-01:33" vs handbook/19:359 "00:57 to 01:33" and SESSION_RECORD_2026-10-30_to_31.md:40 "31 Oct 00:57:31 to 01:33:24". The .tex keeps 00:57 (timestamped record).
2. Opening #3 end: ledger l20 "03:09:57", handbook/21:171 and handbook/20:177 "03:10". The .tex's "02:18 to 03:10" is the minute rounding; T17 prints the seconds. Not an error.
3. The writer's own conflicts 1 to 5 (FINAL "six" vs five rungs; DDeP start time; CP library 556 / 566 / 554; B2 rater thresholds v2.0 vs v2.2) re-checked against handbook/18:286 and handbook/19 §3.2, §5; the .tex follows the verify file / frozen count in each case. Agreed.
4. Thesis consistency: every value shared with T21, T17 and ch05 (FINAL +0.018 [+0.013, +0.025]; encoder cosines; protocol_100 deltas; PF2 +0.1890 (0.0433), +0.0117 / +0.0120; PF2E +0.2141 [+0.0303, +0.3820]; RN50-PF −0.0289 (0.0251); THIN-B3, A8, HC, B6, SKR2, HC2, SKR2E, SKR2C values; opening times) agrees. No disagreement found.

## OPEN
- T21's CP100 row says "closed, with a seam-sensitivity caveat"; no source for the caveat was found in docs 19 to 21 (the writer also could not source it). The appendix does not use it; the T21 wording is outside this audit's files.
- The ideas-table caption now names ideas 1 and 7 and the reviewer's checks as E1 reads, as the ledger lists them. Ideas 2, 3, 5 and 11 used E1 images or E1 strata (brightness, same-module files, half-cut levels); whether the ledger counts those image-only reads is not stated. The caption does not claim they did not read E1.

## Other checks (no change needed)
- E1 ledger table #1 to #7: protocol, opened times, rules and verdict words checked line by line against the server ledger l18 to l30, verify_pf2 l9 to l13, verify_skr2c l6 to l25, handbook/20 l132 to l168, handbook/21 l63 to l137; key values also found in the primary verify files (verify_thin_b3, verify_hc, verify_skr2_hc2, verify_skr2e, verify_pf2e, verify_a8screen, verify_b6). All correct.
- F51 / H36 "from modules not in train": the 7 H36 modules (CSIR_00297 to 00299, 00301, 00333 to 00335 in t9_rf_sets.tsv) have 0 cells in the 478-cell legacy train list. Correct.
- Claim strength: n.d. never written as worse or no effect; KILL worded "no sign of a gain"; readings marked; test50 and E1 conditions stated in §Conditions and every test50 table caption; no old-era number (the "+0.05 to +0.08" revised-label effect is presented as the earlier work's figure, as in ch05).
- Conventions: no em or en dashes, no non-ASCII characters, no host, user or path names, industry partner not named, "Om" not present; Pratt, Hanifi, Tian, Shit appear only via citations or `\CITE` (published authors).
- LaTeX: 14 \begin / 14 \end; all 19 \ref targets exist exactly once in the thesis; all 18 labels unique across `*.tex` and `chapters/*.tex`; 4 \citep keys exist in references.bib; `\CITE` is defined in main.tex:27.

Numbers checked: about 360 values checked against the source file named in NOTES (handbook docs 17 to 21, the server ledger, verify_skr2c, verify_pf2, session records); 24 key E1-opening and T21 values also matched in the underlying verify_*.md files; 0 values checked only against NOTES.
