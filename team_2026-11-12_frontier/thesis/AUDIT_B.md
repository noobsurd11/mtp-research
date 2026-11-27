# AUDIT_B: ch06_protocol, ch07_methods, ch08_e1_result (27 Nov 2026)

Primary records were read on giant (read-only) and copied to the auditor scratchpad: benchmark/PROTOCOL_v1.0.md (now **01804c54**, the frozen version of 23 Nov 21:40; the NOTES cite the pre-freeze eeb3379a), results/FINAL_OPENING_READ.md (16e3f1e7), FINAL_OPENING_READ_ERRATA.md, final_opening_read/verdict.txt (bbb5f3b4) and read_e1/read.txt, harness/final/opening/OPENING_RULE.md, harness/final/FINAL_RULE_ADDENDUM_1.md, HOUSECS_READ.md (9efd43ac), C3HRNET_READ.md, C3X_READ.md, ROWS2_READ.md, W2A_READ.md, FINAL_TTA_READ.md, final_tta_read/read.txt, stageB/B1_classbias_xfit.md, PROTOCOL_v0.2.md, BRIEF.md, release_v1 README (690dac25) and SANITIZE.md, e1_openings.md ledger, method card house_r34_unetpp_pf_v11.yaml, c3x_read/class_guard.txt, INFERENCE_COST.md (1e5a9002), THESIS_TABLES.md (d58e803a, identical to the working copy).

## 1. CHANGES

| file:line | old text | new text | evidence |
|---|---|---|---|
| ch06_protocol.tex:145 | `For relF1@2, $M$ is 0.010 throughout; on cv5v3` | `For relF1@2, $M$ is 0.010 throughout, except 0.0111 on the 416 clean cells of the cv5v2 screens (RTX A6000 machine); on cv5v3` | results/ROWS2_READ.md:28 "margin M 0.010 on 532 cells, 0.0111 on the clean cells" (clean cells = score_exclude_v3, 116 excluded, l5); PROTOCOL_v1.0.md:185 "\| cv02, cv5v2, 416 clean \| 0.0111 \|"; machine: release_v1/SANITIZE.md:24 "machB = the 8-GPU lab machine (RTX A6000)" = cv02 |
| ch06_protocol.tex:38 | `test set had 18 counted openings and overlaps the pool` | `test set had 18 counted openings before the final one and overlaps the pool` | Same chapter, l53 says "After 19 counted openings"; PROTOCOL_v1.0.md:114 "19 counted openings (24 Oct to 21 Nov)", l116 "read after 18 earlier counted openings". Two counts for one quantity in one chapter; the edit keeps 18 and says when |
| ch07_methods.tex:237 | `gridline (+0.060 and +0.058) and splice (+0.092 and +0.075)` | `gridline (+0.058 and +0.060) and splice (+0.075 and +0.092)` | The sentence gives the cv02 value first (+0.0126, "the machine of the 5-seed rows") and gaint second (+0.0137). results/stageB/B1_classbias_xfit.md:55-58, table "gaint \| cv02": "gridline (15) \| 0.302 -> 0.362, +0.060 [...] \| 0.304 -> 0.361, +0.058 [...]"; "splice (16) \| 0.021 -> 0.113, +0.092 [...] \| 0.013 -> 0.088, +0.075 [...]". The old text paired +0.060 / +0.092 with cv02; they are gaint's |
| ch08_e1_result.tex:58 | `lists the eight registered E1 openings.` | `lists registered E1 openings \#1 to \#8.` | E1 has nine registered openings (ch06 l61-63; e1_openings.md l35 "#9 registered", l38 "#9 OPENED"); T17 title "Registered E1 openings #1 to #8". "the eight registered E1 openings" read as the total |
| ch08_e1_result.tex:226 | `(Appendix~D) hold the values.` | `(Appendix~A) hold the values.` | main.tex:56-61: the appendices are A "Tables" (\input{thesis_tables}), B "Related-work table", C (app_t21_note). No Appendix D exists. thesis.txt l135-139 TOC: "A Tables / B Related-work table / C Reading the pre-protocol table". tab:T13a is defined in thesis_tables.tex:476 |

Considered and not changed (judgement wording, not a verified error):
- ch07 l216 "The relF1@2 contrasts survive every variant": all variant values stay positive, but T19b marks HRNET 3-px +0.0073 bold ("changes the verdict"), which the next clause states ("below M"). Reads as "keep their sign"; the author may prefer "keep their sign under every variant".

## 2. CONFLICTS (sources disagree)

1. **relF1@2 margin on clean cells.** PROTOCOL_v1.0.md:105 (from SPLIT_INTEGRITY.md:305) "excluding the 91 cells ... M stays 0.010 (inactive 0.055 to 0.061)" vs PROTOCOL_v1.0.md:185 and ROWS2_READ.md:28 "0.0111 on the clean cells". These are two different clean sets: SPLIT_INTEGRITY's set leaves out 91 cells (441 cells; its l230 gives cv02 relF1@2 0.0106, rounded to "0.010"), ROWS2 uses the 416-cell score_exclude_v3. So not a true conflict on the 416 cells, but PROTOCOL l105 sits under the 416-cell context and reads as if M = 0.010 there. The ch06 edit uses the read file (ROWS2) for the 416 cells. Flag for the lead.
2. **PROTOCOL md5.** ch06 header comment and ch06/ch07/ch08 NOTES cite PROTOCOL_v1.0.md eeb3379a; the file on giant is now 01804c54 (freeze edit, 23 Nov 21:40). Every number I checked in ch06 matches the frozen file; only the cited md5 is stale (comment line 2 of ch06, NOTES).
3. **THESIS_TABLES T4 caption** (generated file, not edited): still cites "protocol v1.0, PROTOCOL_v1.0.md, eeb3379a" (pre-freeze md5) and keeps v0.2 wording in the CV5 column; ch06 NOTES s6 already flags this for the next table build.

## 3. UNVERIFIED (no primary source located)

1. ch07 l232 "On the pool, gridline, splice, edge dark and material are the weak ones": no source names these four as the pool's weak classes (searched THESIS_TABLES.md, OUTLINE.md, PROTOCOL_v1.0.md, C3X_READ.md, final_tta_read/read.txt). c3x_read/class_guard.txt gives PF pool IoU material 0.3952, splice 0.0157, **edge_dark 0.6278** (above inactive 0.5042); PROTOCOL_v1.0.md:134 names only gridline 0.302 and splice 0.021 as weak. edge dark is weak on E1 (0.0000, verdict.txt l74), not clearly on the pool. Not changed.
2. ch07 l128-129 SWAD card details (constant lr after warm-up, uniform average 10,000 to 20,000): verified against W2A_READ.md:40 and OPENING_RULE.md:42, not against the card yaml (hrnet_w18_unetpp_swad_const_pf_v11.yaml not found under harness/el_bench_src/bench/methods).
3. ch06 l23-27 related-work counts (22 papers, 18 with no interval, 0 module-disjoint / distance-tolerant / unseen): checked against PROTOCOL_v1.0.md:43 only, not RELATED_WORK.md s4 itself (owned by the ch03 auditor).
4. ch07 T16a-only values (src_calib +0.0003 [-0.0046, +0.0132]; dti +0.0011 [-0.0016, +0.0062]; la_ce -0.0022 [...]; layered_ci -0.0140 [...]; ema +0.0018 [...]; U1 SKR01 +0.0206 [...]): matched THESIS_TABLES T16a and PROTOCOL_v1.0.md 7.2 / 8.2 tables, not the W1C / W2B / U1 read files.
5. `\PENDING{release URL}` in ch06 l205 (section Release): known open item for the user, left as is.

## 4. CROSS-CHAPTER (files I do not own; not edited)

1. **Appendix B pointers point at content that does not exist** (needs main.tex owner or the user):
   - ch06 l13 "Appendix~B holds the protocol summary, the model info sheet and the reporting checklist" and ch06 l196 "Appendix~B gives both, with C2 as the worked example".
   - ch08 l44 "The full record (hashes, times, reproduction pins) is in Appendix~B".
   - main.tex:59 makes Appendix B the Related-work table; no appendix holds the info sheet, checklist or reproduction pins (thesis.txt l135-139; grep of thesis.txt for "info sheet", "checklist", "reproduction pin" finds only these chapter sentences). Either add that appendix in main.tex (sources exist: benchmark/INFO_SHEET_TEMPLATE.md, PROTOCOL_v1.0.md s12.1) or drop the three pointers. I did not delete the sentences because the fix is structural.
2. Generated THESIS_TABLES.md / thesis_tables.tex T4 caption: pre-freeze md5 and v0.2 wording (see CONFLICTS 3).
3. Consistency checks that passed across chapters: test50 counts (ch04 l34 "19 counted times ... 24 Oct to 21 Nov", ch05 l137 "18 counted times up to 14 Nov", ch11 l69 "19 counted openings", ch08 "after 18 counted earlier openings"); C2 cost 1,744 GFLOPs / 11.8x (ch01 l109, ch10 l87-88, ch11 l37 = INFERENCE_COST.md l23-24); MDE about 0.074 (ch01 l106, ch11 l12, ch12 l20); E1 P +0.0430 [+0.0013, +0.1043] wherever quoted.

## 5. Count

About 360 numbers and dated facts checked in ch06 to ch08 (ch06 about 115, ch07 about 120, ch08 about 125); about 320 against a primary record on giant (protocol, read / verdict / errata files, opening rule, addendum, B1, ROWS2, C3X, C3HRNET, W2A, final TTA read, HOUSECS, release README, ledger, method card), about 40 only against THESIS_TABLES / PROTOCOL tables (T16a rows, related-work counts, U1). Every FINAL_OPENING_READ_ERRATA item (1 to 5) is reflected in ch08 in its corrected wording; no superseded wording ("about 3 x", "the gain is the model, not the TTA", "8 test cells are pool cells", "4th look") survives in ch06 to ch08.
