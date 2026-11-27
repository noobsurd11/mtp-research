# GAPS: what the thesis tables cannot fill, where sources disagree, and wording that overstates (thesis_tables, round 4, 22 Nov 2026)

T = `/home/yugma/mtp/research/team_2026-11-12_frontier`. Line numbers are of the files as hashed in `SOURCES.tsv`. Tags: E = stated in
the cited file; S = my judgement. Round 2 status words: **open**, **resolved by errata** (`results/FINAL_OPENING_READ_ERRATA.md`,
af55915f; the tables use its wording and cite it), **resolved by derivation** (flagged `derived = yes` in SOURCES.tsv), **closed**.
Round 4 (22 Nov): G-N1, G-N2, G-N7 and G-N10 closed by the results of 22 Nov; each row names the closing file, its md5 and lines.

## A. Numbers the thesis needs that no result file states
| # | Missing number | What exists | Status | Why it matters (S) |
|---|---|---|---|---|
| G-N1 | HOUSE - PF on cv5v3 at 5 seeds, with intervals (relF1@2, strict crack IoU, guards) | `results/HOUSEPF_READ.md` (71e5a382) section 1, l12 to l13: relF1@2 532 OP-A +0.0059 [-0.0043, +0.0152], strict crack IoU +0.0179 [+0.0093, +0.0266], and the OP-W and 416-cell values; guard items section 2, l26 to l30 (9 outside a bound: ARTS width at all four values, CFVS width at 416 OP-A, false crack px at all four). Raw: `/home/noob/work/bench_reads/housepf_read/read/read.txt` (bb805994) l270, l271, l286, l287 and `read_x416.txt` (4038090b) l263, l264, l279, l280. "Printed intervals only. No verdict; nothing here decides." (l3). In T6 (HOUSE - PF row; strict IoU at the other three values in a T6 note). | **closed** (22 Nov) | PROTOCOL section 7: HOUSE is a row of its own; an in-distribution crack gain is also printed against HOUSE (now T7a, HOUSE rule rows; section D item 5). |
| G-N2 | Strict crack IoU intervals for HRNET - PF and COMBO - PF on cv5v3 | Printed before round 3 and missed by it (E, `HOUSEPF_READ.md` l38): `results/c3hrnet_read/read.txt` (d22b9855) l213, l229 and `read_x416.txt` (4ad98717) l208, l224; `results/c3x_read/read.txt` (95a3a5ca) l327, l343 and `read_x416.txt` (4328a4a5) l318, l334. house_pf_read reproduces them exactly (`HOUSEPF_READ.md` l35 to l37). T6 now: HRNET - PF +0.0008 [-0.0105, +0.0111], COMBO - PF +0.0099 [-0.0007, +0.0207] (532 OP-A); the other values in a T6 note. Also filled in the same row: COMBO - PF relF1@2 532 OP-W +0.0158 [+0.0069, +0.0264] and 416 OP-W +0.0166 [+0.0054, +0.0298] (c3x `read.txt` l344, `read_x416.txt` l335; `HOUSEPF_READ.md` l39). | **closed** (22 Nov) | |
| G-N3 | E1 numbers for HRNet alone, SWAD alone, HOUSE | None. E1 has C1, C2, C3, E-PF, C1-D4 only (`final_opening_read/verdict.txt` l23 to l39). | **open** (needs a new sealed read; not proposed) | E1 separates the model part from D4 (C2 - C1-D4), not HRNet from SWAD. |
| G-N4 | Smallest detectable effect of the E1 opening | No read prints it. Lead ruling: MDE = 2.80 x SE (two-sided 0.05, power 0.80, normal approximation) with the opening's printed seed-aware SE 0.0265 (`verdict.txt` l11) = **0.0742** (about 0.074). In T4 and the T8 notes; SOURCES.tsv rows derived = yes with the command `python3 -c "print('%.4f' % (2.80*0.0265))"`. The log's "about 0.05" (`log.md` l250, from opening #7's SE 0.019) is not used. | **resolved by derivation** | The n.d. rows of T9 / T10 (half-cut, S4, C3 - C2) cannot exclude effects below about 0.074 at 80% power. |
| G-N5 | E1 at OP-W | Not computed: a stated deviation; width guards G1 / G2 take its role (`verdict.txt` l142). | **closed** (stated in T4) | |
| G-N6 | Any held-out score of the two full-pool models themselves | None by design; the CV5 rows describe the recipe through the cv5v3 fold models. Full-pool runs: steps 1 to 18,000 under F, the rest under F2 by resume (`verdict.txt` l143; `harness/final/FINAL_RULE_ADDENDUM_1.md`). | **open** (state it in the text) | The thesis should say C1 / C2 have no CV5 number of their own. |
| G-N7 | Inference cost of C2 (latency, wall time per cell) | `thesis/INFERENCE_COST.md` (1e5a9002): CPU headline section 3.3, l58 to l65 (C2 3.88 (4.38) s per cell, gaint CPU, 16 threads, batch 1, l64); GPU section 3.4, l70 to l78 (C2 0.174 (0.177) [200] s per cell, one cv02 RTX A6000, fp32, TF32 off, batch 1, l76); cv02 dump wall time section 4 (E1 C2 jobs 100 (100 to 101) s for 106 cells, l94). New table T22 copies 3.3 and 3.4. | **closed** (22 Nov) | Network time only; image read, preprocessing and writes excluded (l14). The GPU numbers are upper bounds on a shared host (S, as written in l82). |
| G-N8 | The 528-cell table | PROTOCOL l52 ruled it; superseded by the 433-cell and then the 416-cell clean set (PROTOCOL section 11 items 10, 11). | **closed** (one sentence in the text: tables use 532 and 416) | |
| G-N9 | test50 "clean 42 without twins" for opening #19 | Verdict prints all 50, clean49, nolink16 only (`verdict.txt` l120 to l134); the clean-42 convention is in PROTOCOL l57. | **open**, low priority | Only if #19 is compared with the earlier 18 openings. |
| G-N10 | A related-work table (every published EL number with release, split, convention, interval) | `thesis/RELATED_WORK.md` (f2a6adcd): main table section 1, l13 to l42 (22 full-text papers; columns release, split and module-disjointness, classes, metric and averaging, number, interval / seeds / repeats, comparability, l15); abstract-level rows section 2, l50 to l60; counts section 4, l84 to l101. Own generator `build/related_work/gen.py` with `related_work.tex` and `RW_SOURCES.tsv`. Not repeated in THESIS_TABLES.md (pointer in its section 3). | **closed** (22 Nov) | |
| G-N11 | Severity numbers for the final model, E1 or half-cut cells | S1 used PF out of fold on pool cells; "not validated on unseen modules or half-cut cells" (`SEVERITY_SUMMARY.md` l16). | **open** | Limits the severity section to PF and pool cells. |
| G-N12 | Recall of the label-error detector; a second annotation | Unknown (REPORT section 5(a)); one double annotation (F2). | **open** | F2 stays suggestive. |
| G-N13 | T3b few-shot numbers | Pending (`log.md` l291 to l292). | **open** (pending) | |
| G-N14 | Record-level trace for the T21 rows | Round 3: all 38 rows now trace to handbook doc 11 and to the primary record it cites (SOURCES.tsv). The 16 rows that were handbook-only now trace to `results/p3_label_versions`, `p6`, `p10`, `p11`, `p12`, `p13`, `p14`, `p15`, `p16`, `p17`, `e1/README.md`, `trackD/labelset_results.md` + `verify_labelset.md`, `coach_100.md`, `verify_pf2.md` and `verify_thin_b3.md`; every record line was checked by eye for context and column order. Where the record prints the value in another layout (lo and hi in separate columns, "(0.018)" for "thr 0.018", "0.005-0.018" for "0.005 to 0.018", "n.d." per fraction for "n.d. at 20%, 50%, 100%"), each number is the same string and is traced on its own; no value needed a transform, so no row is derived. No record contradicts a handbook value. | **closed** (0 dagger rows) | |

## B. Disagreements between sources (the result file wins)
| # | Item | Source A | Source B | Status and use in the tables |
|---|---|---|---|---|
| G-D1 | How many test50 cells are pool cells | `FINAL_OPENING_READ.md` l61 "8 test cells are pool cells" | `SPLIT_INTEGRITY.md` l207, l211: one of the 8 is a cells.tsv link only, "not confirmed and not refuted" | **resolved by errata** item 3 (l18 to l21): T2 and the T13 notes use "8 ... same physical cell ...: 7 confirmed by pixels, 1 (CFVS_00063_r3_c1) on the cells.tsv link only". |
| G-D2 | Verdict word for TTA item (c) | `final_tta_read/verdict.txt` l126: "=> (c) CS_D4 - PF: GAIN, FAILING GUARDS NAMED; failing guard items 2: ..." | same file l170 and `FINAL_TTA_READ.md` l17: "C2 PASSES ITS CV5 CHECK" | **closed**: T7a prints both verbatim with their line numbers. On the thesis sentence see section D item 1. |
| G-D3 | E1 composition | `BRIEF.md` l25: "67 modules ... 58 of them are half-cut" | `SPLIT_INTEGRITY.md` 5a: 71 image ids; `verdict.txt` l55, l140: 62 half-cut | **closed**: tables use 71 / 62. |
| G-D4 | Source of the E1 level line in FINAL_OPENING_READ.md | l5: "Every number below is copied from ... verdict.txt" | l33's levels are not in verdict.txt; they are `read_e1/read.txt` l6 to l11 at 3 dp | **closed**: T8, T10, T11a copy read.txt. |
| G-D5 | HRNET - PF relF1@2 interval | `C3HRNET_READ.md` l10 [+0.0012, +0.0203] | `REPORT.md` l11 to l12 [+0.0010, +0.0209] (a different draw, stated there) | **closed**: C3HRNET used. |
| G-D6 | cv02 inactive margin | 0.049 (`stageA/A1.md`; PROTOCOL l113) | 0.050 (`W1C_READ.md` l34; `ROWS1_READ.md` l16) | **closed**: 0.049, as PROTOCOL section 11 item 3 rules. |
| G-D7 | Two "bands" for strict crack IoU | PROTOCOL l85: a level band 0.48 to 0.60 on the legacy test masks | the convention band +-0.019 on contrasts (audit F1; FINAL_RULE, OPENING_RULE) | **closed**: tables use only the convention band (a standard note on every table with a strict column). |
| G-D8 | T3b design | `T3B_PROPOSAL.md` l79: K = 5, 2 seeds | `log.md` l291: K = 5, 3 seeds (lead's disclosed choice) | **closed** (pending track, no number). |
| G-D9 | "4th look at these 106 cells" (E1 ledger row #8, `team_2026-10-31_next/e1_openings.md` l27 and l30) | ambiguous: counts registered looks at one cell set without counting the pre-policy reads or R0 | `verdict.txt` l138: "E1 7 registered openings (3 looks at one contrast) plus reads before 31 Oct and one use of published E1 contrasts (R0, 15 Nov); the final models were never scored on either set." | **resolved by errata** item 5 (l26 to l29): T17 row 8, the T8 notes and T20 claim 1 use the l138 wording; "4th look" is not used. |

Checked and consistent (E): every E1 and TTA number in `log.md` (21 Nov 08:15 and 12:08 entries) equals the result files; the pins
`FINAL_OPENING_READ.md` 16e3f1e7, `verdict.txt` bbb5f3b4, `final_tta_read/verdict.txt` a95f89e8 hold; the errata file is af55915f.
Round 4 pins (E, SOURCES.tsv): `HOUSEPF_READ.md` 71e5a382, `HOUSECS_READ.md` 9efd43ac, `INFERENCE_COST.md` 1e5a9002; raw reads housepf
`read.txt` bb805994 / `read_x416.txt` 4038090b, housecs `read.txt` c65458ee / `read_x416.txt` 22faa38e. `RELATED_WORK.md` f2a6adcd (not traced by
make_tables.py; it has its own RW_SOURCES.tsv).

## C. Wording in the sources that overstates
| # | Where | As written | Status | Wording now used |
|---|---|---|---|---|
| G-W1 | `FINAL_OPENING_READ.md` l76 | "about 3 x its CV5 size" | **resolved by errata** item 1 (l9 to l13) | T8 note: "about 2 to 3 x ...; against CS_D4 - PF (+0.0222, selection-biased) it is about 2 x; the E1 interval [+0.0013, +0.1043] contains the CV5 values". |
| G-W2 | `FINAL_OPENING_READ.md` l69 to l70 | "The gain is the model, not the TTA" | **resolved by errata** item 2 (l14 to l17) | T9 note, T20 claims 5 and 6: "Most of the gain is the model ... The D4 part is not resolved on E1". |
| G-W3 | `FINAL_OPENING_READ.md` l61; `verdict.txt` l137 | "8 test cells are pool cells" | **resolved by errata** item 3 | see G-D1. Note: `verdict.txt` l137 says "the same physical cell as a pool cell" and is itself not wrong. |
| G-W4 | `FINAL_OPENING_READ.md` l47 | BMRK stratum given without levels | **resolved by errata** item 4 (l22 to l25) | T10 note and T16b: C2 relF1@2 0.0000 [0.0000, 0.0000], C1 0.1843 [0.0000, 0.9216]; C1-D4, C3 and E-PF also 0.0000; the delta rests on 5 cells. (C2S5 also scores 0.0000, `read_e1/read.txt` l28; the errata does not list it.) |
| G-W5 | `FINAL_TTA_READ.md` l26 | TTA on PF "is the most robust gain in the project" | **open** | Restrict to CV5 / known modules; on E1 the D4 part is not resolved. |
| G-W6 | `stageB/B5_msc_tta.md` l30 | "the largest crack gain this benchmark has measured" | **open** | Date it (18 Nov) or drop it. |
| G-W7 | E1 described as "unseen modules" | "unseen modules" | **open** | `SPLIT_INTEGRITY.md` l200: "supported, not proven". |
| G-W8 | `C3SWAD_READ.md` l29; handbook doc 11 claim 35 | "found no measurable leak"; "had no measurable effect" | **open** | "not separated (every interval holds 0)" (`C3_LEAK_READ.md` l21). |
| G-W9 | `U1_READ.md` l29 | "The unseen-source gap is real and large" | **open** | descriptive levels only (T14). |
| G-W10 | `dataset_audit/REPORT.md` l48 (F2) | "models already sit at the agreement level of two drawings of one image" | **open** | keep "one double annotation" every time. |
| G-W11 | `FINAL_OPENING_READ.md` l66 to l67 | "No candidate, readout or threshold was selected on these cells" | **resolved by errata** item 5 (l29) | T8 note: holds for E1, but C2's readout (swad) and D4 were chosen on pool cells. |
| G-W12 | handbook doc 11 row 2, P11 / P12 status (copied in T21) | "supported for inactive" | **open**, S | These P-series "supported" words use the old locked rule (P8 rule 1) on test50, which overlaps the pool (T2). T21's caption says not comparable; quote with that caveat. |

## D. For the lead (S)
1. **The TTA (c) sentence.** The proposed sentence, "C2 passes its CV5 check; ARTS width guard fails on the 416 clean cells (named)",
   is supported by `final_tta_read/verdict.txt`, with three precisions the sources force:
   (a) "selection-biased" is part of the decision line (l170) and must stay in the sentence;
   (b) the ARTS failure is at both OP-A and OP-W on the 416 clean cells, 1.159 against the 1.15 band (l111, l119), while ARTS passes
   on the 532 cells (1.107 OP-A l95, 1.121 OP-W l103);
   (c) "C2" here is the CV5 version CS_D4 (cv5v3 fold models), not the full-pool C2.
   A sentence the sources support exactly: "On CV5 the C2 recipe (CS_D4) passes its check against PF (selection-biased); the ARTS
   width guard fails on the 416 clean cells at OP-A and OP-W (1.159 against the 1.15 band; named) and passes on the 532 cells."
2. **Abstract sentence** (replaces round 1's guidance): it must carry the recipe averaged over seeds 5 to 9; full cells carry it,
   half-cut n.d.; 101 of 106 cells CSIR; OP-A only; prior looks as in `verdict.txt` l138 (7 registered openings, 3 looks at one
   contrast, reads before 31 Oct, one use of published contrasts; the final models never scored on E1 before); interval
   [+0.0013, +0.1043] with lower end near 0; MDE about 0.074 (derived).
3. **G-N1 / G-N2** closed 22 Nov by house_pf_read (`HOUSEPF_READ.md`, 71e5a382); T6 updated (HOUSE - PF row, two strict IoU cells, two COMBO
   OP-W cells, two notes). The strict IoU intervals of HRNET - PF and COMBO - PF were in the c3hrnet and c3x reads all along (l38).
4. **T21 length**: 38 rows, one per arm or decision, all traced to a primary record (G-N14 closed).
5. **HOUSE rule on C2** (`results/HOUSECS_READ.md`, 9efd43ac). Placed as two rows at the end of T7a, not in T6: T6 holds contrasts
   against PF, T7a holds the C2 recipe contrasts, and the HOUSE line is the companion of item (c). Both rows say selection-biased and
   "Printed intervals only. No verdict; nothing here decides." (l3). CS_D4 - HOUSE relF1@2 532 OP-A +0.0163 [+0.0051, +0.0284]
   (l16; raw `read.txt` c65458ee l271). Open: the rule compares an 8-view arm with a single-view HOUSE (l111); no HOUSE D4 dump exists
   (l35). HOUSECS_READ.md l111 lists the options: (a) cite CS - HOUSE as the like-for-like line, (b) say in PROTOCOL 7.1 that the HOUSE
   line is single view, (c) ask the user for HOUSE_D4 dumps.
6. **T22 placement**: appendix, by the round 2 placement rule (T22 is not in the main list). If the deployment section needs it in
   the main chapter, add 'T22' to `_MAIN` in `build/tables_data.py` and rerun.
7. **Ledger change seen on the round 4 rerun**: `team_2026-10-31_next/e1_openings.md` changed (md5 03ad99de to 52432548, mtime 22 Nov
   03:13): row #9 (T3b, registered, NOT opened) was added. T17 rows 1 to 8 resolve on the same lines (l18 to l27) with the same
   values; only the md5 column of 35 SOURCES.tsv rows (T17, T21) changed. T17 does not list #9 (no numbers yet).
8. **Section 1 Sources column** of THESIS_TABLES.md prints basenames, so the raw read files show as `read.txt` / `read_x416.txt`;
   SOURCES.tsv has the full paths. Showing the folder needs a change to `make_tables.py`.
