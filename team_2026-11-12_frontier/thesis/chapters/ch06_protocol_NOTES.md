# NOTES for ch06_protocol.tex (Chapter 6, "The benchmark protocol")

Written 23 Nov 2026. Read-only sources; nothing sealed was read (result text files, docs and tables only).
Short paths (relative to T = /home/yugma/mtp/research/team_2026-11-12_frontier; md5 prefix as read 23 Nov):
- P10 = benchmark/PROTOCOL_v1.0.md (eeb3379a). The base of the chapter. Not edited.
- RUL = log.md, entry "22 Nov 12:49 (lead, user rulings)" = log.md l363 (user: "all as recommended, D3 = a, run the HOUSE read").
- HCS = results/HOUSECS_READ.md (9efd43ac). HOUSE rule applied to C2 on CV5 (selection-biased).
- TT = thesis/THESIS_TABLES.md (81c54378); TEX = thesis/thesis_tables.tex (d92b3f0b).
- REL = benchmark/release_v1/files/README.md (690dac25). LIC = benchmark/release_v1/LICENCE_AUDIT.md (f267ea23).
- IST = benchmark/INFO_SHEET_TEMPLATE.md (97c3029e). IC = thesis/INFERENCE_COST.md (1e5a9002).
- RW = thesis/RELATED_WORK.md (f2a6adcd).
Chapter line numbers (lN) refer to ch06_protocol.tex as delivered (md5 in the final report).
Machine-check: every row below was string-checked against the cited source line by a script (23 Nov; result at the end).

## 1. Numbers, with sources
Format: ch line | value as written in the chapter | source file:line | note.

| ch | value | source | note |
|---|---|---|---|
| l8 | version 1.0 | P10:l1 | |
| l9 | draft of 15 November (v0.2) | P10:l3 | "v0.2 (15 Nov 16:00 ...)" |
| l9 to l10 | ten questions decided on 22 November | P10:l459 to l473 (R1 to R10); RUL (log.md:l363) | rulings treated as decided per the task |
| l20 | 582, 642, 695 cells; three releases | P10:l34 | P10 drops v0.2's "between the first two"; not used |
| l22 to l24 | 22 papers; 18 no interval, seed count or repeat; 0 module-disjoint; 0 distance-tolerant; 0 unseen modules | P10:l43 (from RW s4) | |
| l25 to l26 | 0.320 vs 0.365 strict; relF1@2 0.822 vs 0.846 | P10:l36 | |
| l27 | 0.233 / 0.365 / 0.414; relF1@2 0.824 / 0.846 / 0.849 | P10:l37 | |
| l29 to l30 | seven elements of a comparable number | P10:l41 | P10 lists seven (adds label set); OUTLINE 6.1 says six (from P02) |
| l34 | 18 counted openings (test50 before #19) | P10:l116 ("after 18 earlier counted openings") | |
| l40 | release 20211104, 24 classes | P10:l17 | |
| l41 | P532, 532 cells | P10:l51 | per-source counts left to T1 (TT l73 to l91) |
| l43 | 285 module groups, none spans folds | P10:l19, l96 | |
| l45 to l47 | 532 and 416 both decide; 91 cells, 8 cells of four pairs, 17 SDLE cells | P10:l99 | the 116 excluded = 91 + 8 + 17 (sum not printed in chapter) |
| l47 | cv5v2 330 groups | P10:l103 | |
| l48 | PF relF1@2 +0.0026 [-0.0092, +0.0174], not separated | P10:l104 | also T2 / T20 #15 (TT l672) |
| l49 | 0 half-cut cells in the pool | P10:l100 | |
| l52 | 8 same physical cell (7 by pixels, 1 by cell-table link) | P10:l38 | ER item 3 wording |
| l52 to l53 | 19 counted openings; #19 public table; no further opening | P10:l114, l115 | |
| l53 to l54 | E1 106 cells, CSIR 101, BMRK 5, 71 source images, 62 half-cut, 44 full | P10:l53 | |
| l55 to l56 | E1 label view: class 24 to 2, classes 25 to 28 to ignore | P10:l62 | |
| l58 | 167 forbidden stems | P10:l122 | |
| l61 | seven registered openings, 1 to 14 November | P10:l123 ("#1 to #7 (1 Nov to 14 Nov)") | |
| l61 to l62 | #8 registered 21 November 11:22:35 | P10:l123 | |
| l62 | #9 registered 22 November | P10:l123 (registration 2, 22 Nov 03:13) | |
| l66 | 13 robust classes | P10:l129 | |
| l67 | absent class never 0 or 1 | P10:l131 | |
| l68 | about 3 x 3 cells; 57% crack px, 71% inactive px outside centre cell | P10:l75, l135 | |
| l75 to l77 | 2.0 px inclusive; Euclidean; per image; pooled | P10:l141, l507 | |
| l76 to l77 | 95th percentile, 2.000 px | P10:l149 | |
| l79 | centreline F1 rewards a 1-px dilation | P10:l149 | |
| l81 | convention band +-0.019 | P10:l147; TT T4 (l155) | |
| l84 | oracle fold 0 shifted 1 px: strict 0.370, relF1@2 0.999 | REL:l95 to l96 | P10:l441 explains fold 0 (107 cells) vs 0.449 on 532 cells |
| l85 | inactive intervals about +-0.05 to 0.07 | P10:l150 | |
| l85 to l86 | 33 of 285 groups; Kish n_eff 12.9 | P10:l76 | |
| l86 to l87 | 18 spurious-inactive cells scored as labelled; 30 of 40 model errors | P10:l472 (R9), l76 | R9 (a) ruled (RUL) |
| l90 | width band 0.85 to 1.15 | P10:l155 | |
| l91 | >= 40 cells per source; 1.5 x reference | P10:l156, l157 | |
| l92 | mIoU-R13 drop <= 0.010 on a sealed set | P10:l159 | |
| l92 to l93 | E1 guards G1 to G4; inactive reported only | P10:l155 to l159 (table columns) | |
| l94 to l95 | >= 50 false px share; components >= 20 px | P10:l161 | |
| l97 | 212 false px; 303 crack-free cells | P10:l161, l157 | "under one false px per crack-free cell" P10:l163 |
| l98 to l99 | 1.5 x tight without PF's freeze; HOUSE 3.7 x | P10:l163 | R3 (a): frozen, per-cell values beside (P10:l466; RUL) |
| l105 | argmax over 24 classes | P10:l168 | |
| l107 | OP-F A/A -0.0118 [-0.0357, -0.0005] crack IoU | P10:l170 | |
| l107 to l108 | OP-C: 11 of the 13 robust classes, other folds | P10:l171 | |
| l114 | equal-cost line: 2 x house cost; 2-seed PF ensemble | P10:l252 | |
| l116 | C2 1,744 GFLOPs per cell, 11.8 x C1 | P10:l253; IC:l23, l24 | |
| l117 | same-view controls 1,184 GFLOPs, 0.68 of C2 (derived) | P10:l254 | derived in P10 (1,184 / 1,744); flagged "derived" in text |
| l118 to l119 | FLOP-matched PF comparator for later entries | P10:l470 (R7 (c)); RUL | R7 (a) for C2 + (c) for future entries |
| l123 | 50 BMRK cells, CC BY-NC-SA 4.0 | P10:l88, l87 | |
| l128 | screen 2 seeds; row and candidate 5, seeds 5 to 9 | P10:l210 | |
| l128 to l130 | L6: wholly below 0 at OP-A and OP-W stays at 2 seeds; the two EL-paper rows | P10:l211 | |
| l130 to l131 | five other closed rows; separate tier "2 seeds, cv5v2 screen, clean-cell column" | P10:l464 (R1 (a)); RUL | |
| l137 | 285 / 330 groups | P10:l178 | |
| l138 | 2,000 draws; 95% percentile; unpaired, conservative | P10:l178 | |
| l139 | M = max(0.01, 2 x SE); A/A {5,6} v {7,8} | P10:l179 | |
| l140 | M 0.010 relF1@2; cv5v3 532 A/A -0.0002, SE 0.0037 | P10:l183 to l186; TT T4 (l156) | |
| l141 | inactive M 0.049 (A6000 machine, cv5v2), 0.054 (RTX PRO 4500 machine), 0.0462 (cv5v3 TTA read) | P10:l183, l184, l186 | machine names: release SANITIZE.md l24 (machA = 1-GPU RTX PRO 4500 = gaint; machB = 8 x A6000 = cv02) |
| l142 | 0 of 15 A/A splits promoted | P10:l193 | |
| l143 to l144 | MDE relF1@2 0.0087 / 0.0071 / 0.0055; inactive 0.0518 / 0.0423 / 0.0328 | P10:l194 | |
| l146 | 71 clusters E1; 48 test50 | P10:l192 | |
| l147 | n = 5; 3 in the few-shot track; 2,000 draws | P10:l192 | |
| l149 | M 0.010 fixed, not re-estimated | P10:l188 | |
| l149 to l150 | MDE 2.80 x 0.0265 = 0.0742 (derived) | P10:l194; TT T4 (l162) | derived, flagged in text |
| l152 to l158 | verdict rules | P10:l201 to l203 | |
| l166 | HOUSE rule since 14 November | P10:l312 | |
| l167 | HRNET - HOUSE +0.0045 [-0.0069, +0.0157] | P10:l308; TT:l209 | |
| l168 | rule kept 22 November | RUL (log.md:l363, "HOUSE rule kept") | |
| l170 to l171 | CS_D4 - HOUSE +0.0163 [+0.0051, +0.0284]; +0.0194 [+0.0080, +0.0319]; +0.0164 [+0.0033, +0.0318]; +0.0204 [+0.0073, +0.0369] | HCS:l16; TT:l231 | selection-biased; no registered rule |
| l171 to l172 | false crack px 0.09 to 0.17 x HOUSE | HCS:l110 (per value l46) | |
| l172 | ARTS width 0.847 (532), 0.846 (416), OP-A | HCS:l45, l59; TT:l231 | |
| l173 | HOUSE ARTS width 1.307 x PF | HCS:l110; TT:l210 | |
| l175 to l176 | CS - HOUSE +0.0107 [-0.0009, +0.0229] OP-A; +0.0140 [+0.0017, +0.0269] OP-W | HCS:l27; TT:l232 | |
| l176 to l177 | no HOUSE D4 dump exists | HCS:l35 to l38 | no new runs: P10:l212 (no new experiments after T3b) |
| l178 | D4 adds +0.0134 to PF on CV5 | TT:l226 (T7a (a)); HCS:l111 | |
| l183 | 4,949 pool cells | P10:l261 | |
| l183 to l184 | cosine >= 0.98; band-pass NCC >= 0.80 | P10:l261 | |
| l189 | info sheet fields A to J | P10:l498; IST:l9 to l65 | |
| l189 to l191 | ten-item checklist | P10:l484 to l495 | |
| l192 to l194 | three practices as protocol text: BN re-estimate cells, post-hoc parameters with Holm, inactive read set | P10:l276; IST F4 to F6 (l51 to l53); RUL ("G17 / G19 / G20 ... become protocol text") | |
| l201 to l202 | MIT code; CC BY 4.0 lists and results | REL:l3 to l4, l174 to l176; P10:l90 | |
| l202 | 700 image ids; 816-row cell table | REL:l27 | |
| l205 | no image, mask, weight, label or per-cell result of test50 / E1 | REL:l33 to l34 | |
| l208 | 1,064 files of 532 cells match, 0 mismatch | REL:l66 | |
| l209 | PF out-of-fold per-cell records added (decided 22 November) | P10:l471 (R8 "PF records (a)"); RUL | worded "are to be added": not checked whether the staged release already holds them |
| l210 to l211 | outside entrants report E1 levels with a self-declared ledger line once a tested E1 label builder is in the release | P10:l473 (R10 (a)); RUL | |
| l218 | 10 inactive cells on E1 | P10:l53, l419 | |

Small integers that are counts of things named in the text (five folds, four values, two machines, three practices, seven
openings) come from the same lines as the row they sit in.

## 2. Judgement sentences kept (S), with their basis
1. l29 to l30 "We therefore hold that a comparable number states seven things together ..." (S; P10:l41 "Reading (S)").
2. l31 to l35 "Five choices follow from the measurements ..." (S, this writer's summary of P10 s1, s3, s5).
3. l68 to l70 "The protocol keeps the window, so every cell-level quantity in this thesis ... describes a window." (ruling R4 (a), P10:l467; RUL).
4. l90 "A crack gain counts only if it does not come from drawing differently." (S framing of the guards).
5. l97 to l100 "so 1.5 x PF is a tight bound for every arm without PF's partial encoder freeze" (P10:l163, from HRN s3, s4) and "moving the reference after reads that failed the guard would be a post-hoc change" (S; R3 reason, P10:l466).
6. l82 "Strict crack IoU is printed because the literature uses it" (TT conventions, "kept as a familiar literature metric").
7. l83 to l84 "The release's check run shows why" (S).
8. l117 to l118 "isolate the model part without being equal cost" (P10:l254).
9. l138 "Seeds are drawn unpaired, which is conservative." (P10:l178, E).
10. l147 to l148 "it speaks about the trained models, not the recipe" (P10:l192).
11. l173 "so this item measures HOUSE's width as much as C2's" (S; HCS:l110).
12. l175 "The rule as written compares an eight-view arm with a single-view reference." (S; HCS:l111).
13. l177 to l178 "We record this asymmetry as a limitation ...; a HOUSE with D4 would likely close part of the gap (judgement, not measured)." (S; HCS:l111; the task's instruction to record it as a limitation).
14. l217 to l220 limits list (P10:l191, l419 to l423; HCS:l111).

## 3. Rulings of 22 Nov as applied (RUL = log.md l363), and where they appear
- R1 (a): separate 2-seed screen tier, not ranked against the 5-seed tier: l130 to l132.
- R2 (a): research-use terms with a commercial-use column; C2 "research-only as trained": l122 to l127.
- R3 (a): false-px guard 1.5 x frozen; per-cell false px and the >= 50 px share printed beside: l94 to l100.
- R4 (a): image window as scoring unit: l67 to l70.
- R5 (a): no ranks; "not separated from PF": l160 to l161.
- R6 (a): freeze after the listed conditions: l8 to l11, l216 to l217 (\PENDING{T3b verdict}).
- R7 (a) + (c): C2 class (c) with the comparator gap disclosed; FLOP-matched PF comparator for future entries above 2 x: l113 to l119.
- R8: D4 (a) no commercial model on BMRK cells or MiT-B2 (stated in ch10_deployment.tex l120); D5 (a) scoring code only: l204 ("training code is not included"); PF records (a): l209 to l210. D3 (a) (no further approval for v1) is NOT written into the chapter text: it concerns approvals, not the protocol; the lead may add one sentence if wanted.
- R9 (a): the 18 spurious-inactive cells reported as labelled: l86 to l87.
- R10 (a): E1 for outside entries, levels only with a self-declared ledger line, once a tested builder exists: l210 to l212.
- Lead items accepted with the rulings: G17 / G19 / G20 as protocol text (l192 to l194); the three "proposed" duties as protocol text: P10 2.3 implications (l34 to l35 absolute levels; l67 to l70 window; relF1@2 decides throughout), the 5.5 robustness duty (l157 to l159, label-variant shifts and k_0), the carrying-groups clause of checklist item 9 (l191); latency scope = E1 candidates (ch10); HOUSE rule kept (l166 to l178).
- PROTOCOL_v1.0.md section 11 still lists these as proposals; the chapter states them as decided, as the task instructs.

## 4. Placeholders
- \PENDING{T3b verdict}: 0 since 23 Nov (t3b_fill; were 4: l11, l63, l211, l217 of the earlier draft; see section 8). \PENDING{release URL}: 1 (left for the release).
- \FIG{F9}: 1 (protocol flow, OUTLINE s4 F9).
- \CITE: 0.

## 5. Citations
- pratt2021defect, pratt2023benchmark (ch06_protocol.bib): authors, title, journal, volume / pages and year from the BibTeX block
  copied verbatim from the BenchmarkEL README into REL:l142 to l158; DOIs and Pratt 2023 volume 5 from RW:l17, l18 (R01, R02); the
  2023 DOI also in LIC:l35.
- hanifi2025bridgingdatagapspatially: BibTeX block copied verbatim from the E-SCDD dataset card into REL:l162 to l170; arXiv id also RW:l27 (R09).
- deitsch2019elpv: arXiv id 1807.02894 from RW:l66; title, 7 authors, DOI 10.1016/j.solener.2019.02.067 from the arXiv API
  (export.arxiv.org, fetched 23 Nov); journal Solar Energy 185:455-468 (2019) from the Crossref API record of that DOI (fetched 23 Nov).
- cha2021swad: arXiv id and title from cards/ledger/MASTER.tsv row P039; 7 authors and first-version date 2021-02-17 from the arXiv
  API (fetched 23 Nov). Venue not verified, so the entry is an arXiv @misc.
- xie2021segformer: arXiv id and title from cards/ledger/MASTER.tsv row P260; 6 authors and date 2021-05-31 from the arXiv API
  (fetched 23 Nov). Venue not verified; arXiv @misc.
- wang2021hrnet, zhou2018unetpp: thesis/refs_extra.bib (not repeated).
- Key clash risk: the ch03 writer may add the same Pratt / E-SCDD / ELPV papers under other keys. The lead should merge to one key.
- Not cited, on purpose: D4 TTA (no paper; RW:l144); the CWRU SDLE data set (OSF 4qrtv, no paper id on disk).

## 6. Things in OUTLINE (or the task) that turned out different
- OUTLINE 6.1 says "the protocol fixes all six"; P10 l41 lists seven (label set added). Chapter uses seven.
- OUTLINE 6.3 lists guards as "width band pooled and per source, false crack px, mIoU-R13"; P10 has five guards (inactive IoU too) and names the E1 subset G1 to G4. Chapter uses P10.
- OUTLINE 6.6 "plus one email to Pratt, nothing published until the user approves": superseded by the 22 Nov rulings (D3 (a)); the email is not mentioned in the chapter (a process detail).
- T4 (main table) still describes the CV5 rules as "protocol v0.2" and uses host names (cv02, gaint) and "330 module groups"; the chapter text uses v1.0, cv5v3 (285 groups) and machine descriptions. The lead may want T4's caption updated to v1.0 at the next table build.
- The GPU latency, PENDING in P10 l258 and l521, is now measured (IC s3.4, 1e5a9002); the chapter treats it as done.
- The task brief says "C2 is research-only: ELPV cells ... and the SegFormer MiT-B2 weights are non-commercial". C2 does not use MiT-B2 (it uses HRNet-W18, MIT; LIC:l37, l100); C2 is research-only because of the ELPV cells. The chapter words it that way; MiT-B2 is named only for the SegFormer benchmark row.

## 7. Machine check (23 Nov)
Script (scratchpad, not part of the thesis): for each row of section 1, every decimal or multi-digit number in the value cell must
occur in the cited chapter lines and in the cited source lines. 164 values checked, 10 flagged, all 10 parser artefacts checked by
hand: trailing commas ("642,", "20211104,", "532,"), "+-0.019" / "+-0.05" read as negative numbers, "50" and "19" from "test50" and
"#19" in the note text, "A6000" / "4500" (GPU model names, source SANITIZE.md l24, not P10), and "22 November" against log.md l363
("22 Nov"). No real mismatch.

## 8. T3b fill (23 Nov 2026, t3b_fill, after the read)
Sources: VT = T/results/t3b_open9_read/verdict.txt (bfe583db); EL = ../team_2026-10-31_next/e1_openings.md (3ead9149) l38. Numbers
copied as printed. Only what the T3b result settles was filled; the freeze itself (R6) is left to the protocol-freeze agent, and
the "One condition of the freeze remains" and "is frozen once" sentences still describe the freeze as pending.
| Former marker (line in the 12:27 draft) | Replaced by | Source |
|---|---|---|
| l11 "must be written into it \PENDING{T3b verdict}" | "That result was read once on 23 November: the primary contrast of opening #9 is CONFIRMED, as a few-shot result inside E1 (Chapter 9)." | VT l9, l76; read date EL l38 |
| l66 "its result is \PENDING{T3b verdict}" | "its result, read once on 23 November, is CONFIRMED: labelled E1 cells of the other folds raise the out-of-fold crack relF1@2 of the C2 recipe against the same recipe zero-shot by +0.2213 [+0.0977, +0.3504] (Chapter 9)" | VT l6, l9; EL l38 |
| l214 "that builder waits for the few-shot read \PENDING{T3b verdict}" | "that builder waited for the few-shot read, which ran once on 23 November." (does not say the builder is released) | EL l38 |
| l220 "is frozen once the few-shot result is written into it \PENDING{T3b verdict}" | "is frozen once the few-shot result, read on 23 November (Chapter 9), is written into it." | EL l38 |
