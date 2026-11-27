# AUDIT_C: ch09, ch10, ch11, ch12, main.tex (27 Nov 2026)

Scope: chapters/ch09_t3b.tex, ch10_deployment.tex, ch11_limitations.tex, ch12_conclusion.tex, main.tex (working copy).
Short paths: T = server `/home/yugma/mtp/research/team_2026-11-12_frontier`. Server md5s were checked against the NOTES pins:
T/results/t3b_open9_read/verdict.txt bfe583db (= local `to_human/ee511_deck/guide_ctx/t3b_verdict.txt`), read_t3b/read.txt 922b965e,
T/harness/t3b/T3B_RULE.md 0c006d44, T/benchmark/T3B_PROPOSAL.md 569fbcb0, T/results/final_opening_read/verdict.txt bbb5f3b4,
T/results/severity/SEVERITY_SUMMARY.md 57e2bb4c, T/benchmark/release_v1/LICENCE_AUDIT.md f267ea23, T/thesis/INFERENCE_COST.md 1e5a9002
(= working-copy INFERENCE_COST.md = local guide_ctx copy). Every pin matched.

Before my edit, my 5 files were byte-identical to thesis_orig.

## 1. CHANGES

| file:line | old text | new text | evidence |
|---|---|---|---|
| main.tex:31 | `\author{\PENDING{author, roll number, guide}}` | `\author{Yash Patil (B23222)\\ Muskan (B23274)\\[2ex] Guide: Dr.\ Praful Hambarde\\[2ex] Major Technical Project\\ IIT Mandi}` | Details from the user via the team lead's task. I left out `\and`: in the report class it opens a second column, so the guide / project / institute lines would sit under Muskan only. One centred column renders cleanly. Title not changed. |

No other change. I found no number in ch09 to ch12 that differs from its primary record or its traced table cell. I found no verdict / robustness check / reading mix-up, no n.d. worded as "worse" or "no effect", no placeholder (`\PENDING`, `\CITE`, `??`) and no em or en dash in ch09 to ch12. Figures F18, F19 and F20 exist as `figures/F18.pdf`, `F19.pdf` and `F20.pdf`. Every `\ref` target exists (tab:T3b, T9, T18, T20, T22; ch:e1_result, methods, protocol, limitations). The hard-coded "Chapter~6" and "Chapter~8" in ch10 (l12, l20, l104, l126) match main.tex's order (ch06 = protocol, which defines the image window at l72 and opening #9 at l68; ch08 = E1 result).

### Key checks that passed (selection)
- ch09 result (l81 to l141, Table tab:t3b-strata, F20 caption): every value matches verdict.txt l6 to l60 and read.txt (levels in subset all; no-scuff levels; BMRK HALF 0.5443 [0.0000, 0.9908]; false crack px 541 / 1366 / 2231). That covers Delta +0.2213 [+0.0977, +0.3504], SE 0.0643, fixed-model [+0.1066, +0.3390], G1 541 v 2231 ratio 0.242, G2 +0.1385, width 1.426 (0.631 / 0.443), all 8 strata rows × 3 contrasts with cells / clusters, components, per-class IoU, inactive and strict IoU.
- ch09 design and rule (l20 to l77) against T3B_RULE.md: folds 22/22/20/21/21 and 12/14/14/16/15 at l28; shares at l36 to l40; 33 trainings at l45 to l47; recipe at l48 to l53; monitor 107 at l60; outcome table at l102 to l106; guards at l108 to l109; power 52/76/91 %, +0.085 and SE 0.0265 to 0.030 at l143 to l147. Also checked against T3B_PROPOSAL.md: 106/71, 62, 37, 32/32,294/296, 20 hard cells in 10 ids at 75 %, 0.22/0.50/0.69/0.86, effective n 8.6, ids 300 to 2,328, 14 to 18 hard crack cells for K = 5, and 0.126 recall.
- ch09 run facts (l49 to l57) against the ledger e1_openings.md l35 and l38 (03:13 registration; 08:40:46 to 13:39:27; read 13:38:00 to 13:39:27) and log.md l382, l384, l386, l418 and l419 (33 rc 0, "registered repairs: none", strict lanes 4096 MiB, SHARE_DUMP 13:34:35 to 13:35:49, one strict start and one SHARED start). run.log l2 to l6 confirms the manifest check, A6000 and the ZS IDENTICAL re-score.
- ch09 scope: "few-shot", "out of fold inside E1" and "does not show that the model handles a new layout without labels" are stated, and E1 is never called unseen after #9. HALF − ZS and ALL − HALF are worded "printed beside", and strata "decide nothing".
- ch10 severity, external sets and pilot (l18 to l74, l129 to l141) against SEVERITY_SUMMARY.md l6 to l64. "Polycrystalline" and "137 module instances, 3 types" are checked against S0_DOWNLOADS.md l14 to l15.
- ch10 cost (l79 to l95) against INFERENCE_COST.md s2, s3.3, s3.4 and s4: 26.1 M / 148.0, 20.8 M / 218.1, 148/740/1,184/1,744/8,722, 11.8×, CPU 0.216/2.23/3.88 at 18.0×, GPU 0.0112/0.0911/0.174 at 15.5×, b8 0.133, views batched 0.134, 2.3× / 1.9× / 1.47×, 445 / 2,993 MiB, RSS 1,376, about 20,700 and about 930 per hour, 100 s / 106 cells, 18 s. These also match T22.
- ch10 licences (l116 to l127) against LICENCE_AUDIT.md (ELPV CC BY-NC-SA 4.0, "likely models ... untested in law", BenchmarkEL no licence file, E-SCDD MIT card cannot clear BenchmarkEL, HRNet-W18 MIT, MiT-B2 non-commercial research / evaluation, D4 recommendation). The 22 Nov decision is checked against log.md l363 (R8 D4 (a)). Seed 5 "designated before any number" is checked against INFO_SHEET_TEMPLATE.md l96.
- ch11 and ch12 E1 values against final_opening_read/verdict.txt: l11 (+0.0430 [+0.0013, +0.1043], SE 0.0265), l17 (inactive), l46 (seed 5), l55 (half-cut), l63 to l75 (material / edge dark 0.0000) and l136 to l142 (prior looks, leakage, OP-A deviation, 101 CSIR). E1 C2 relP@2 0.5995 / relR@2 0.4157 come from read_e1/read.txt l7. CV5 0.9216 / 0.8211 come from final_tta_read/read.txt l14. The audit values (0.259 / 0.829, 57 % / 71 %, 33 of 285 and Kish 12.9, 1.59 / 3.09, 0.94, 125 groups, 17 and 31, ±0.05 to ±0.06, 49 cells, 2 to 3 h) come from dataset_audit/REPORT.md. OP-C +0.0126 [+0.0077, +0.0167] comes from PROTOCOL_v0.2.md l260, and "about a third" from l262. The target 0.90 / 0.90 comes from BRIEF.md l57.
- ch12 claim count: T20 has 22 rows. By the Class column: 1 confirmed (#1), 1 few-shot confirmed (#22), 1 confirmed CV5 (#6), 1 passes selection-biased (#8), 3 measured, 8 n.d. (#3, 4, 7, 10, 12, 13, 15, 20), 2 failed (#9, 21) and 5 descriptive (#2, 5, 11, 14, 16), which sums to 22. That is correct.
- Claim strength: ch11 and ch12 stay within ch08 and ch09. The CV5 C2 number is called "selection-biased" and "no confirmation". The half-cut zero-shot result is "not detected". The few-shot result is "a few-shot result inside E1 ... says nothing about a new layout without labels". The ch12 half-cut few-shot stratum is flagged "a stratum that decides nothing".

## 2. CONFLICTS
None that affect the text. Two minor source differences, recorded for completeness; the text follows the right source in both:
- Read start time: the ledger e1_openings.md l38 says "13:38:00 to 13:39:27", while run.log l1 has its first timestamp at 13:38:26. This is consistent: the wrapper starts before the first logged line. The text uses the ledger.
- The lead's brief (per ch09_t3b_NOTES l152) said both of the last two dumps ran shared. log.md l419 records one strict start (half_f3_s7) and one SHARED start (all_f3_s7). The text follows the log, which is correct.

## 3. UNVERIFIED
- main.tex:32 `\date{December 2026}`: I found no source. Not changed.
- ch10:118 "BenchmarkEL, which holds all pool cells": LICENCE_AUDIT.md gives the BMRK cells' source as ELPV and the SDLE cells' as CWRU. It does not say in so many words that BenchmarkEL contains every pool cell. Not changed; the lead may want a source line.
- ch12:65 "the 49 pool cells with an image-supported candidate": dataset_audit/REPORT.md l192 says "the 49 cells with an image-supported candidate". I did not confirm the word "pool", although the audit covers P532 only, so it is very likely right.
- Checked only against the traced tables (THESIS_TABLES.md / SOURCES), not the raw read files: ch10 l102 to l111 and ch11 / ch12 E1 secondary contrasts (C2 − C1-D4, C1-D4 − C1, C3 − C2 from T9), CV5 contrasts (+0.0222, +0.0055, +0.0134, +0.0107 from T7a), ch12 claim 19 (0.320 / 0.365 / +0.0333 / +0.025 / +0.0243 / 0.97 from T20 row 19), the ch11 rater interval 0.244 [0.105, 0.436] (T20 row 18) and the F18 caption "467 cells at (0, 0)".

## 4. CROSS-CHAPTER
- abstract l13 to l17, ch01 l109 to l121, ch06 l68 and ch08 l183 / l259 give the same T3b and cost values as ch09, ch10 and ch12 (+0.2213 [+0.0977, +0.3504], +0.2530, −0.0701, +0.0171, 1,744 GFLOPs, 11.8×, 0.17 s, 8,722). No inconsistency found.
- ch12_NOTES l63 flagged an un-narrowed "label release moves levels more than any method" in ch06. The current ch06 l29 is narrowed to strict crack IoU ("more than any method gain over PF"), as are the abstract l8 and ch01 l95. Resolved.
- Abstract l16 "carried by the half-cut cells": this is a stratum reading (strata decide nothing). ch09 l104 says the same thing as a reading, so it is consistent. Abstract owner may want "(a stratum, deciding nothing)" for strictness. Not an error by rule 3 as worded.
- main.tex l3 comment "Not compiled yet: no TeX engine on gaint or cv02" is stale (the PDF was built 23 Nov). It is a comment only and does not render. Not changed.

## WATTCYCLE
12 mentions, each on its own line:
- chapters/ch09_t3b.tex:18
- chapters/ch09_t3b.tex:159
- chapters/ch10_deployment.tex:9
- chapters/ch10_deployment.tex:70
- chapters/ch10_deployment.tex:113 (section title)
- chapters/ch10_deployment.tex:123
- chapters/ch10_deployment.tex:129 (section title)
- chapters/ch10_deployment.tex:132
- chapters/ch10_deployment.tex:138
- chapters/ch11_limitations.tex:78
- chapters/ch12_conclusion.tex:75
- chapters/ch12_conclusion.tex:77

main.tex: 0.

## 5. Count
I checked about 300 numbers and facts. About 255 were checked against a primary record (server result, read, rule, ledger, log or audit files, or INFERENCE_COST.md, whose md5 equals the server copy). About 45 were checked only against THESIS_TABLES / SOURCES / NOTES (listed under UNVERIFIED).
