# Verification of scribe's session record (3 to 4 Nov) and handbook refresh

Owner: `verifier`. Date: 12 Nov 2026 (IST). Independent fact-check before scribe commits.
Drafts checked: `SESSION_RECORD_2026-11-03_to_11-04.md` draft 1 (d48ffeca); handbook drafts: see Part B.
Method: every md5 recomputed with `md5sum` (first 8 hex); numbers traced to the cited file or log line; A3 / A1 / A2 structure facts recomputed from file names, sizes and listings only (no image or data value opened); no ssh, no downloads, no test / E1 / B2-key reads.
Verdicts: OK = matches the source; FIX = wrong, mis-tagged or missing (correction in the last column; the number in brackets is the item in the FIX list sent to scribe); UNVERIFIABLE = no file holds it.

## Part A. Session record, draft 1 (d48ffeca)

### A.1 Numbers and md5s (spot-check)
| # | Claim (record §) | Source | Verdict | Correction / note |
|---|---|---|---|---|
| N1 | protocol_SKR2C 663de96d; lock copy 91b76abd; build_s2c c6424c0f; e1_openings 365d62f3; review_SKR2C_v09 cc2a21be; review_s2c_stage1_code ddf09a9f; skr2c_power_out 2e15d408 (§0, §13) | md5sum | OK | |
| N2 | deployed s2c md5s lib 4edcae9e, guard 334742d6, queue de31c533, gpumem 06791cdd, make_jobs e7d20e79 (§2.3-2.4, §13) | md5sum `scripts/s2c/` | OK | |
| N3 | dry-run md5 lists 1f251254 / de5dbd1b / 345c825e (§2.3, §13) | md5sum `results/` | OK | |
| N4 | next log.md 7482b29e, README d1942ba9 (§13) | md5sum | OK | as of 14:46 correction line |
| N5 | v0.9 6958d22f, NOT READY 02:32 (e146f83b), v0.9.1 91f875c9, v1 cand. 5995fcd5 signed 02:36, LOCKED 02:37 91b76abd (§1, §2.1) | next log 02:28-02:37 | OK | |
| N6 | rootcheck run 2 02:33:29-02:37:24 rc 0; SPLITS 24568cdb; train 842f27c4, val 9dcccf00; "Labelled: 478 ... val: 54 test: 54"; SUPPF loss 4.154092311859131 / 4a216d9d; SKR01 4.251284599304199 / 2e44cb4d; run 1 sec 8.25 vs 8.18 (§2.2) | next log 02:33, 02:37 | OK | |
| N7 | stage-1 review b0d866a4: G1-G7 must, G8 should; G3 ~23 s (§2.3) | next log 02:38, 02:43; review file l.24, l.30 | OK | |
| N8 | v3 tests 02:48:00-02:55:11; final re-run 02:57:40-03:04:05; SIGKILL rc 137, SIGTERM rc 143, 63-64 s; gap 8-9 s (§2.3) | next log 02:56, 03:04 | OK | |
| N9 | Residual "cmdline not recorded within 20 s" accepted by team-lead 02:59 (§2.3, S5) | protocol l.266, l.276; review l.89 | OK | |
| N10 | PIDs gpumem 2343574 (03:05:56), guard 2343958 (03:05:59), queue 2345125 (armed 03:06:11); run 1 py 2345199 03:06:11, OK 03:06:16; run 2 py 2359341 03:08:17, OK 03:08:22 (§1, §2.4) | next log 03:06, 03:09 | OK | |
| N11 | GPU 5,876 + 7,018 + 6,826 MiB, free 11,947 at 03:08:54; ≥ 120 s apart (126 s) (§2.4) | next log 03:09 | OK | |
| N12 | gates 9,100 / 9,000 "(measured peaks 7,020 / 6,830 + 2,048)" (§2.4) | next log 02:23 | FIX [16] | peak + 2,048 = 9,068 / 8,878; the gates were rounded up to the earlier queues' values (s2q 9,100; pf2 9,000) |
| N13 | waves done 04:45 / 06:25 / 08:04 / 09:44 / 11:24; ALL TRAINED 11:24:04 (10 rc 0 of 10); guard end 11:24:05, stop 11:25:05; no trigger, no HOLD (§1, §2.5) | team-lead retrospective line, next log (only source; no launch.log / autostop.log copy in the repo) | OK (UNVERIFIABLE beyond that line) | correctly attributed and dated as retrospective |
| N14 | wall ~8 h 18 (03:06:11 to 11:24:04) (§2.5) | arithmetic | OK | 8 h 17 m 53 s |
| N15 | P(R PASS) 0.90 / 0.64 / 0.34 / 0.05; ~35-65%; seed-aware ~25-45%; ~15% combined (§2.1) | next log 02:24, 02:32, 02:36 | OK | |
| N16 | 7 co-primaries; 3rd look at 50 test / 106 E1 cells; 20,000 steps, batch 8, final weights (§2.1) | protocol l.26, l.34, l.123-129 | OK | |
| N17 | 3604dc7, 384 files, 02:49 (§1, §3) | next log 02:49 | OK | |
| N18 | thermal outputs md5s: dataset_table 7a48fc3b, notes 66a25beb, download_plan 409481f7, selection da419f33, verified 645d7cfc, ideas_long ba9c0038, drone_only 50a13aeb, capture_plan 66d2270b, replan 9d6a4885, ranked d36d70f7, top3 fa6da29f, SUMMARY 00f17af7, ADDENDUM 878e6bec, factcheck 879f35fa, README 45ca3b69, Om files 6677bc9f / b5f143bb (§4, §13) | md5sum | OK | |
| N19 | check pass 1: 110 items, OK 73 / FIX 31 / UNV 6; pass 2: 33, OK 13 / FIX 18 / UNV 2 (12:44 said 14 / 17) (§1, §5.6) | factcheck header; log 12:37, 12:44, 12:45 | OK | |
| N20 | A1 209 files, 286,886,436 B; A2 47, 237,009,189 B (IR 15,706,079 + EL 221,303,110) (§7) | recomputed from the data dirs; download_verified | OK | |
| N21 | A3 7z 642,610,942 B md5 2ca8adbc; README 1,161 B 8dd0b5ce; 1,414 files, 94 dirs, 1,162,474,935 B; 640 raw, 31 nef, 33 csv (§7) | recomputed (md5sum of the 7z, find / du -sb) | OK | |
| N22 | A3 EL exposures 2 s × 5, 5 s × 24, 6 s × 2; classes 8 / 8 / 6 / 2 / 7 / 6 / 6 (§8.5) | recomputed from file and folder names | OK | |
| N23 | MANIFEST lines A1 210, A2 48, A3 1,416; 1,677 files, 2.2 GB; df 52 GB; venv 3.12.16 / numpy 2.5.3 / scipy 1.18.1 / skimage 0.26.0; 7z present (§7) | recomputed (wc -l, find, du, df, venv) | OK | MANIFEST md5s 5a272616 / 8a5c7520 / 23a3c83a also OK |
| N24 | A1 selection: 155 of 158 eligible; picks and bins; max 6320427439 s 19.32 mV; bins 2.6-4.9 / ... / 8.4-19.3 mV (§7) | log 12:55; download_verified table | OK | |
| N25 | Disk 6.9 GB (12:43), 4.6 GB (13:39), 5.586 → 4.423 GB; prune 542 MB / 171 MB (§7, T15) | log 12:43, 13:40, 13:43, 13:46; download_verified | OK | |
| N26 | G0 v1: A2 9/15, 648/230, ρ −0.550, AUROC 0.736, inner 360/96/−0.554/0.757; A1 7/10, 252/50, −0.285, 0.689, inner 70/13/+0.042/0.528; pooled 16, 900/280, −0.451, 0.708, inner 430/109/−0.475/0.718 (§8.2) | `G0_v1_frozen.json` 1da5ae53 (read) | OK | |
| N27 | G0 v1 orientations A2 0.446 / 0.433 / 0.762 / 0.736, q95 0.555; A1 0.619 / 0.595 / 0.710 / 0.689; 409001724 2nd capture 0.731 / −0.544 (§8.2) | JSON; G0.md | OK | |
| N28 | G0 v1 QA exclusions A2 6/15 (40%), A1 3/10 incl. 6320427439 EL 7.59 / IR 7.30 (§8.2) | JSON `excluded` | OK | |
| N29 | Interim G0: A2 8/15 0.705; A1 4/10 0.756; pooled 0.704 (§8.2) | G0.md interim table | OK | |
| N30 | Row / col-centred v1: A2 ρ −0.07 to 0.00, AUROC 0.49-0.52; A1 −0.17 to +0.05, 0.52-0.57; row-only A2 −0.42 / −0.44 / −0.46 (§8.3) | factcheck §22 G0-3 | OK | |
| N31 | G0 v2: A2 4/15, 288/75, −0.515, 0.732, inner 160/38/−0.501/0.739, centred −0.021/0.525; A1 4/10, 144/36, −0.246, 0.621, inner 40/7/+0.168/0.394, centred +0.231/0.343; pooled 8, 432/111, −0.403, 0.687, inner 200/45/−0.369/0.681 (§8.4) | `G0v2_primary.json` f1e904e7 (read) | OK | |
| N32 | pooled centred "(check: 0.462)" (§8.4) | factcheck §36 table | OK | G0v2.md has "n.c."; attribution to check is right |
| N33 | Sens B: A2 8 mod 0.737, A1 6 mod 0.659, pooled 14 0.706 / −0.431 (§8.4) | `G0v2_sensB.json` efe6f4ee | OK | |
| N34 | v2 orientation A2 flipv 0.760, A1 id 0.709, gap 0.088 (§8.4) | G0v2.md; factcheck §36 | OK | |
| N35 | QA md5s fae36d53, 8557c658, a9a3f454, 484fa349, db548f73; criteria 13:23, addendum 13:26 (§8.4) | md5sum; log 13:23, 13:26 | OK | |
| N36 | frozen tools 7d9a9fe0 (= cellreg.py), g0_stats 27f7bff1, 0190cba5 (= g0_stats.py), pick3b_r12 dac5842b, a3_frames d94b7a89, select_a1 d40cf6d1, check/cellreg_95e0ca3e.py, A3_border_vs_outline a8be5b7e (§13) | md5sum | OK | |
| N37 | T15: 5,688/5,688; robust SD 3.26 mV (0.127 V_t); line 2.57 mV; margin 0.69; D90 ≥ 4.23 mV, 569; DVt 0 (§9.2) | `t15_summary.json` 320ad9e9 (read); factcheck §20 | OK | |
| N38 | T15 descriptive 0.0 / 2.13 / 4.23 / 5.61 / 8.62 / 19.32 mV; 144 of 158 modules; top 10 hold 18.6% (§9.2) | `t15_descriptive.json` 00919df8 (read) | OK | |
| N39 | T15 frozen rule "coverage ≥ 50%; no-spread kill = robust SD(d) < 2.57 mV" (§9.2) | plan v1.2 §3.1; factcheck §20 | FIX [5] | the no-spread kill has two clauses: robust SD < 0.1 V_t **and** < 1% of cells with d ≥ 1 V_t; the second was already met before the read, so the kill rested on SD alone (notes N3, plan §7) |
| N40 | T37 v1: 3/10 excluded (439 EL 7.59 / IR 6.81; 480 IR 8.12; 398 IR 9.73); UVF 9/10 over 5% (§9.3) | `t37_v03_summary.json` fbd466d2 (recomputed exclusions) | OK | |
| N41 | T37 v2: 4/10 (227 IR 6.66, 398 7.22, 439 5.40, 802 7.57); gvq EL 23.9-35.4, IR 44.6-81.7 (§9.3) | `t37_v04_summary.json` 0d60bd16 (recomputed); log 13:28; check CR-3 | OK | |
| N42 | crop 134 × 35 (cols 90-223, rows 137-171), 9 of 10; warm region ~144-146 × 36-37; ~7% pitch error (§9.3) | factcheck §28 CR-5 | OK | |
| N43 | pick3b v1 rules: R1 ρ ≥ 0.5 with CI lower > 0 / < 0.3; R2 ρ ≥ 0.5, ΔR² ≥ 0.10; R3 ≥ 0.8 and centred ≥ 0.7 / < 0.7 and < 0.6; Otsu clause "else a dated amendment" (§9.5) | `plan_pick3b_v1_FROZEN_eaec6f26.md` l.40-98 | OK | |
| N44 | per-class losses cracks 4-5%, interconnects 3-14%, PID 5%, diodes 33-66%, glass < 1% (§9.5) | factcheck §35 PB-3 | OK | |
| N45 | plan_pick3b.md = eaec6f26 bytes + 3,370 NULs; v1.1 file 0 B; A3_layout.tsv 0 B; log l.149 965 NULs (§9.5, T1) | recomputed (head -c 13014 | md5sum; tr | wc) | OK | |
| N46 | Amendment md5s a15275a5, 18b60398, e9f5376c → 8983bc9d, 85270857, d1e6777b, fd98e232 → fb46b6dc; plan_pick1 fb46b6dc (§8.1) | log 13:00-13:50; md5sum | OK | |
| N47 | Amendment 6: 605 × 363, 16 / 12 frames, offsets 10-537 px, 3% inset, 24 full-EL modules, 6 × 10 / 6 × 24 (§8.1) | plan_pick1 l.95-104 | OK | |
| N48 | Top 10 of ranked table T26, T37, T15, W03, T27, W02, W01, T02, X3, W11 (§5.4) | ranked_ideas.md l.74-83 | OK | |
| N49 | "58 rows after merging (T22 / T34 into X1; X1-X7; W01-W14)" (§5.4) | ranked_ideas.md l.43 | FIX [11] | W07 also merged into T19: 38 T + 7 X + 13 W = 58 |
| N50 | Pick costs / kills: pick 1 6-7 dev d, 0 GPU, top 20% ≤ 20%; pick 2 8-10 dev d, ₹27k-30k, re-ID < 90%, X6 ≤ 120 s; pick 3 9-10 dev d, ~5.5 GPU-h, < 50 cells or purity < 70% (§5.4) | top3.md l.56-172 | OK | |
| N51 | WattCycle founded June 2025, IIT Mandi associate professor, Kamand; IIT Mandi facility list: no IR / EL / simulator (§5.5) | capture_plan l.8, l.15-17, l.28 | OK | |
| N52 | Re-plan: ≥ 600 W/m², wind < 28 km/h, ≤ 3 cm/px, ~10 m; Pi HQ ~₹25k; ZWO ₹62,145; SWIR ~€10k-15k; W1 = 4-10 Nov, W7 = 16-22 Dec (§5.5) | log 12:47; top3 l.5, l.92-96; SUMMARY l.28-29 | OK | |
| N53 | "larger cracked / shaded areas gave hot spots of 25-100 °C (R, Dhimish 2021)" (§5.2) | factcheck P-1 | FIX [10] | the abstract says temperature rose "from 25 °C to 100 °C" for modes 3 / 4, up to 105 °C at 40-60% shading |
| N54 | "About 215 modules have EL + IR (A1 157, A2 15, A3 43)" (§5.1) | dataset_table bottom line ("about 215 have IR"); discovery 13:48 (A3 soiling: no EL) | FIX [2] | A3's 12 soiled modules have IR but no EL: ~215 with IR, ~203 with EL + IR (A3 31). (top3.md l.29 has the same slip; one-screen l.16 "with IR" is right) |
| N55 | A1 / A2 / A3 table rows: counts, sizes, licences, 3 × 12 / 6 × 12 (E), 5.289 A / 60 s, 3.392-3.393 A / 180 s vs 5 min (§5.1) | dataset_table A1-A3; factcheck D-3 to D-17, §31 | OK | |
| N56 | Others: B 5, C 4, D 12, E 12 rows; D1 20,000 MIT; D11 ~19.1 GB; D12 3,675; C1 1.38 GB (§5.1) | dataset_table | OK | |
| N57 | E-PF test crack IoU at argmax 0.4815; FINAL 0.492 cv02 (T18) | doc 21 at 3604dc7, SKR2E table l.130, l.137 | OK | |
| N58 | doc 15 §3e rows 24-28, §3d row 19 (§12.1) | doc 15 at 3604dc7 l.178-194 | OK | |
| N59 | tmux ls: only claude-swarm, created 12 Nov 14:42 (§3) | `tmux ls` | OK | |

### A.2 Readings, post hoc labels, E / R / S tags
| # | Claim (record §) | Source | Verdict | Correction |
|---|---|---|---|---|
| R1 | Verdicts table §10.1 only pre-registered rules; readings in §10.2 | §10 | OK | |
| R2 | G0 v2 table "Row/col-centred" column and the A1 "EL-dark cells read warmer, fits current crowding" reading (§8.4) | G0.md (rc-centred "post hoc for the dark arm, Amendment 4"); factcheck §36 ("Reading (S, post hoc)") | FIX [4] | label the column and the reading **post hoc** |
| R3 | §10.2 item 2 "row / module-level signal ... centred AUROC ~0.5" | factcheck §22, §36 | FIX [4] | label post hoc; "~0.5" holds for A2 (v1 0.49-0.52, v2 0.525) and A1 v1 (0.52-0.57), not A1 v2 (0.343) |
| R4 | "Root cause (check §28 CR-5, E)" (§9.3; one-screen l.22) | factcheck §28 CR-5 ("likely cause of the IR rise") | FIX [3] | crop geometry E; its causal role S ("likely cause") |
| R5 | §10.2 item 4 "every number that counts was frozen first and recomputed independently" | factcheck §20, §24, §36 (recomputes); §28-29 (T37 read from reg.json; N7 rule post hoc) | FIX [15] | soften: rules frozen first; T15, G0 v1 / v2 recomputed from raw files; T37 checked from reg.json, not re-registered |
| R6 | §9.1 "all before any data value was read by ideas" | plan v1 header; log 12:53 | FIX [12] | add "apart from the 3 dark I-V values quoted in datascout's download plan (disclosed)" |
| R7 | §9.3 "The frozen D90 stays; it reads as 'dimmest bright-pixel voltage'" | factcheck §31 CV-6 | OK (minor) | a reading; optional (S) tag |
| R8 | §9.4 option B "forking path for a likely null (team-lead; check §29)" | PICK3_A1_REPORT.md l.34 | OK | cite the report for the team-lead quote |
| R9 | Physics §5.2 tags (R for Dhimish, DTU; S for scuff, device physics) | ideas_long §0.1; synth §0 | OK | |
| R10 | DVt "by construction: the selection capped d below 1 V_t" (§9.2) | PICK3_A1_REPORT l.21; plan §7(c) | OK (wording) | optional: "datascout's 12:55 numbers already showed max d 19.3 mV < 1 V_t" |
| R11 | SKR2C "fresh seeds remove seed luck, not cell luck" (§2.1) | protocol §1 | OK | not presented as independent replication |

### A.3 Timeline and incidents
| # | Claim (record §) | Source | Verdict | Correction |
|---|---|---|---|---|
| T-a | 4 Nov log stamps monotonic | recomputed (awk over stamps; NULs stripped) | OK | only break: 12 Nov 14:45 hand-typed stamps |
| T-b | "judge was unreachable from 03:05" (§2.4 l.107), "judge had already gone at ~03:05" (§3), "judge unreachable from 03:05" (S5) | next log 02:58 (judge: all items closed, no process running), 02:59 (coach: "Message to judge undeliverable"), 03:05 (runner: refused) | FIX [1] | unreachable from ~02:59 (coach's send failed); runner's send refused 03:05 |
| T-c | Timeline row order: 02:37:56-02:39:52 after 02:38; 02:57:40-03:04:05 after 02:58-02:59 (§1) | next log | FIX [14] (trivial) | sort by start time, or say "logged 02:41 / 03:04" |
| T-d | Hand-typed timestamps (T2, D2) | factcheck §17 AU-5; log 12:53, 13:11, 13:39; 12 Nov correction lines | FIX [6] | add: pick 1 plan v1 header "~13:00 IST" written by 12:56 (AU-5) |
| T-e | Overwritten G0 v1 output and restore (T7) | log 13:20; factcheck §24 | OK | |
| T-f | Interim G0 before co-sign (T8) | log 13:17 | OK | |
| T-g | Post hoc self-test bars (T3) | log 12:56, 13:27; factcheck §17, §28 | OK | |
| T-h | Pre-review real-data run (T9) | log 13:30, 13:35; notes N8 | OK | |
| T-i | Withdrawn v0.5 (T9) | log 13:35; factcheck §30, §32 | OK | |
| T-j | Missed visual-QA call 6320427793 (T10) | factcheck §26; log 13:26 | OK | |
| T-k | PDF auto-saved by WebFetch (T14) | datasets/notes.md l.35 | OK | |
| T-l | capture's "asset management" vs "recycling" identity question | log 12:07; capture_plan l.21; factcheck C-4, C-5 | FIX [7] | missing: add to §11.2 (and a line in §5.5): local docs called WattCycle "a solar asset-management company"; web showed a PV-recycling startup; check C-5 resolved toward a match (Atlas "solar asset management platform", menu "Asset Management ... recycling") with the caveat that Atlas runs on demo seed data; Om confirmed the company 4 Nov |
| T-m | Unsent report to Om (T16, §6) | team-lead end-state line | OK | |
| T-n | Session ended before A3 results (T1, T16, §0) | logs; mtimes | OK | |
| T-o | ADDENDUM's stale "running, results to follow" (T16) | ADDENDUM 878e6bec §2, §3 | FIX [8] | add: the DRAFT says A3 R1 / R3b are "running" and pick3b results "to follow"; none ran, so that wording must change before it is sent |
| T-p | "No result file is affected" (T1) | `pick1/out/discovery/A3_layout.tsv` 0 B | FIX [9] | say no readout or frozen copy is affected; the discovery output A3_layout.tsv is empty (Amendment 6 does not cite it) |
| T-q | RN-1 scope note: ideas' G0 step 1 used all 157 A1 IR vs Om's 10-module subset; rescoped 12:52, nothing downloaded | log 12:52 (check RN-1, ideas, datascout) | FIX [13] | missing from §11.2; add one line |
| T-r | 12 Nov stamps hand-typed, corrected 14:46 (S6, D2) | both logs | OK | |
| T-s | tmux / Herald move (§3) | team-lead's account only | UNVERIFIABLE | correctly labelled as team-lead's account |

### A.4 State claims
| # | Claim | Source | Verdict |
|---|---|---|---|
| S-a | SKR2C trained, not opened; nothing scored; stage 2 not started | retrospective line; e1_openings 365d62f3 | OK |
| S-b | ADDENDUM still DRAFT (datascout §1-2 never confirmed) | ADDENDUM header; end-state line | OK |
| S-c | pick 1 A3 R1 / R2 / R3b not run; pick3b R1-R3 not run | end-state line; no output files | OK |
| S-d | pick3b R4 not run by rule | log 13:48; plan v1 l.64 | OK |

## Part B. Handbook drafts (as of 12 Nov 15:02: doc 22 f0ba91d5, 00 522c8200, 03 125a1cc8, 11 e34cd417, 12 3a0e4e17, 13 91c46916, 14 79d00550, 15 496b43e7, 16 4e3d4e74, 21 63386725, sync_sources.sh 57c1881a)

| # | Claim (doc) | Source | Verdict | Correction |
|---|---|---|---|---|
| B1 | doc 22 status table, §7-§9 numbers (G0 v1 / v2, T15, T37, downloads), §13 SKR2C | same sources as Part A | OK | |
| B2 | doc 22 l.71 "hot spots of 25-100 °C" | factcheck P-1 | FIX [H1 = 10] | as record FIX 10 |
| B3 | doc 22 l.91 "About 215 public modules have EL + IR" | discovery 13:48 | FIX [H1 = 2] | ~215 with IR, ~203 with EL + IR |
| B4 | doc 22 l.132, l.136 centred column and A1 "warmer" reading | G0.md; factcheck §36 | FIX [H1 = 4] | label post hoc |
| B5 | doc 22 l.140 T15 kill "robust SD(d) < 2.57 mV" | plan v1.2 §3.1 | FIX [H1 = 5] | both clauses |
| B6 | doc 22 l.142 "Root cause (check, E)" | factcheck CR-5 | FIX [H1 = 3] | cause S, crop geometry E |
| B7 | doc 22 l.148 Lesson 2 "(E, both G0 versions)" | factcheck §22 G0-3, §36 | FIX [H2] | **tag upgrade**: post hoc reading (S), not E |
| B8 | doc 22 l.151 Lesson 5 "every number ... recomputed independently" | factcheck §20, §24, §28, §36 | FIX [H1 = 15] | soften |
| B9 | doc 22 l.160 "No result file is affected" | A3_layout.tsv 0 B | FIX [H1 = 9] | |
| B10 | doc 22 l.73 PID hot spots ~50 °C (R); l.72 scuff = E-SCDD class 25; l.78 512 × 512 crops | factcheck P-4; doc 17 l.207; doc 02 l.84 | OK | |
| B11 | doc 00 note, path row, facts block (SKR2C 03:06-11:24, ~215 with IR, G0 0.736 / 0.732, post hoc label) | record; JSONs | OK | |
| B12 | doc 03 §13 table: paths, file counts, bytes, MANIFEST md5s, 1,677 files / 2.2 GB, not-downloaded list | recomputed; download_verified; factcheck pass 2 | OK | |
| B13 | doc 03 §13 "158 per-module txt, 7 currents × 36 cells" | factcheck §20 (7 rows = 6 currents + a zero row) | FIX [H10] (trivial) | "7 current rows" |
| B14 | doc 11 rows 51-55, (c) items 30-32, "cannot" lines | record; JSONs; factcheck | OK | post hoc labelled in rows 53, item 31 |
| B15 | doc 11 results block G0 v2 "(row/col-centred 0.525) ... (centred 0.343)" | G0.md | FIX [H9] | add "post hoc" in the table cell |
| B16 | doc 12 D93-D101 (times 02:38, 02:58-02:59, 03:06, 03:09, 03:10, 11:57, 12:15, 12:39-12:40, 13:13-13:20, 13:27-13:34, 13:28, 13:40) | next log; thermal log; team-lead retrospective | OK | |
| B17 | doc 13 A19, A20, C24, E35-E38 | factcheck §28, §35; dataset_table | OK | |
| B18 | doc 13 C25 "Pitch anchored to the module edges (v0.4)" | factcheck §25 V-1; v0.4.1 VERSION string | FIX [H6] | "limits, not prevents, drift" |
| B19 | doc 13 D55 "found independently by scribe and verifier" | thermal log 14:45 (verifier), 14:46 (team-lead); scribe's message | FIX [H3] | found by verifier; record T1 likewise |
| B20 | doc 13 D56 "log stamps ... stayed monotonic" | recomputed | FIX [H4] | true for 4 Nov only; add AU-5 |
| B21 | doc 13 D60 "judge unreachable ... 03:05" | next log 02:58-02:59 | FIX [H5] | ~02:59 |
| B22 | doc 13 incidents lack the WattCycle identity question and RN-1 | log 12:07, 12:52; factcheck C-5 | FIX [H7] | add |
| B23 | doc 14 §1.1b (52 GB; venv 3.12.16 / numpy 2.5.3 / scipy 1.18.1 / skimage 0.26.0; system python3 3.14.8 without numpy; 7z; tmux; tool md5s incl. pick3_t15 ac51ecd6) | recomputed | OK | |
| B24 | doc 14 §1.2f (paths, md5s, PIDs, times, gates, outcome) | next log; build_s2c; retrospective | OK | |
| B25 | doc 15 §1k, §3f rows 29-34, §4f (S-26 CC BY wording; S2 opening 1 h 22 min) | factcheck S-26; doc 15 at 3604dc7 | OK | |
| B26 | doc 16 Q61-Q68 | record; doc 22 | OK except Q66 | |
| B27 | doc 16 Q66 "the association disappears (AUROC ~0.5)" | G0v2_primary.json (A1 centred 0.343) | FIX [H8] | "on A2" |
| B28 | doc 21 SKR2C notes (02:58 ddf09a9f, 03:04, 03:06, PIDs, 11:24:04, waves, ~1 h 40) | next log; retrospective | OK | |
| B29 | sync_sources.sh: adds team_2026-11-* markdown, 7 thermal JSONs, SKIP_SERVERS switch (scp skipped when 1) | `git diff handbook/sync_sources.sh` | OK (note) | copies two NUL-containing .md files (plan_pick3b.md, thermal log.md); harmless |
| B30 | em-dashes in record, doc 22, all added handbook lines | grep | OK | 0 |

## Part C. Re-check after scribe's fixes (12 Nov ~15:20)
Revised md5s recomputed and equal to scribe's: record 8c247e88; doc 22 d13b00aa; 00 880442ac; 03 3ac37c71; 11 86933261; 12 b4c463a5; 13 d72b59c9; 14 7debf01d; 15 78561cad; 16 fc20ff83; 21 63386725 (unchanged); sync_sources.sh dca8efd9.

| Item | Where checked | Verdict |
|---|---|---|
| FIX 1 judge unreachable ~02:59 | record §1 row, §2.4, §3, S5; doc 13 D60 | OK |
| FIX 2 ~215 with IR, ~203 with EL + IR | record §5.1; doc 22 §3 | OK |
| FIX 3 likely cause (geometry E, role S) | record one-screen, §9.3, T12; doc 22 §9; doc 13 A19 | OK |
| FIX 4 post hoc labels; A1 v2 0.343 | record §8.4 header + reading, §10.2 item 2; doc 22 table, reading, Lesson 2; doc 11 G0 v2 row; doc 16 Q66 "On A2" | OK |
| FIX 5 both T15 clauses | record §9.2; doc 22 §9 | OK |
| FIX 6 pick 1 "~13:00 IST" header | record T2; doc 13 D56 | OK |
| FIX 7 WattCycle identity question | record §5.5, T20; doc 13 D59; doc 22 §12 | OK |
| FIX 8 ADDENDUM's stale "running" wording | record T16; doc 22 §11 | OK |
| FIX 9 no readout / frozen copy affected; v1.1 content unknown; governing plan v1 eaec6f26 | record §0, T1, §9.5; doc 22 §12; doc 13 D55 | OK |
| FIX 10 Dhimish 25 °C to 100 °C, up to 105 °C | record §5.2; doc 22 §2 | OK |
| FIX 11 38 T + 7 X + 13 W = 58 | record §5.4 | OK |
| FIX 12 §9.1 heading (3 disclosed values) | record §9.1 | OK |
| FIX 13 RN-1 | record T21; doc 13 D59; doc 22 §12 | OK |
| FIX 14 timeline order | record §1 | OK |
| FIX 15 softened process claim | record §10.2 item 4; doc 22 Lesson 5 | OK |
| FIX 16 gates 9,068 / 8,878 rounded up | record §2.4 | OK |
| H2 doc 22 Lesson 2 tagged S, post hoc | doc 22 l.148 | OK |
| H3 "found by verifier (14:45)" | record T1; doc 13 D55 | OK |
| H4 monotonic claim limited to 4 Nov | doc 13 D56 | OK |
| H6 C25 "limits, not prevents, drift" | doc 13 C25 | OK |
| H10 "7 current rows (6 currents + a zero row)" | doc 03 §13; record §9.2 | OK |
| Em-dashes | record, doc 22, all added handbook lines | OK (0) |
| `sync_sources.sh` | run by verifier: `PATH=<scp/ssh blocker>:$PATH env -u B2_MARKED SKIP_SERVERS=1 bash handbook/sync_sources.sh` | OK: rc 0; "B2 redaction: 2 file(s) redacted, 0 names left"; 410 files, 5.8M; no scp / ssh attempted |
| B2 names in the new texts | `cmp` of sources copies vs originals: new record and all 32 thermal .md copies byte-identical (the redaction did not touch them); added handbook lines name no Hanifi panel | OK |

Later edit (scribe, after Part C): doc 22 d7b88c3e and doc 03 a4cfe1db add one shape note each ("605 × 363 rows × cols, portrait; the README's '363x605' is width × height"). Checked: OK. Every Part C fix is still present; 0 em-dashes.

## Part D. Staged set (git index, 12 Nov ~15:30, before the commit)
Checked with my own script (path, size, type, B2 patterns) plus `git diff --cached`.

| Check | Result | Verdict |
|---|---|---|
| Count | 698 files: record 1; handbook 55 (10 docs, sync_sources.sh, 44 sources copies: 1 record, 4 next-team, 39 thermal = 32 md + 7 json); team_2026-10-31_next 46 (log, protocol_SKR2C, build_s2c, review_s2c_stage1_code, 5 scripts/s2c files, results/s2c_dry/v2 + final logs, 2 md5 lists); team_2026-11-04_thermal 596 (md 32, json 262, tsv 246, log 28, py 20, txt 5, diff 2, sh 1) | OK |
| Images (png, jpg, tif, nef, ...) | 0 | OK |
| PDFs | 0 | OK |
| Files over 1 MB | 0 | OK |
| B2 files (b2_key, b2_scores, rf_sets.tsv, b2_mining, overlays, superseded_v1) | 0 | OK |
| Out of scope (root log.md, papers/, results/seipv_compare, handbook_al1.diff, Oct team logs, B6 metrics, post_local.pid) | none staged | OK |
| Test / E1 content | none (path keyword hits are only cellreg self-test files on synthetic data) | OK |
| Deployed SKR2C scripts | s2c_lib 4edcae9e, s2c_queue de31c533, s2c_gpumem 06791cdd, s2c_make_jobs e7d20e79 already in HEAD at the deployed md5s; guard 334742d6 staged | OK |
| Staged blobs vs verified files | no unstaged difference at check time | OK |
| Note | the thermal `log.md` and `pick3/plan_pick3b.md` contain NUL bytes (crash traces, kept as evidence); git still stores them as text | OK (note) |

## Verdict
**OK to commit**, on one condition. My last log line and this file change after scribe staged them, so before committing scribe re-runs `env -u B2_MARKED SKIP_SERVERS=1 bash handbook/sync_sources.sh` (rc 0, 0 names left) and re-adds `team_2026-11-04_thermal/log.md`, `team_2026-11-04_thermal/check/verify_record_2026-11-12.md` and their two `handbook/sources/teams/team_2026-11-04_thermal/` copies. Nothing else may change.

## Counts
- Part A (record draft 1): 93 rows: OK 75, FIX 17 (16 FIX-list items), UNVERIFIABLE 1 (the tmux / Herald move: team-lead's account only). Numbers spot-checked: 59 rows covering about 300 values. The SKR2C completion facts trace only to team-lead's 12 Nov retrospective line, and the record says so.
- Part B (handbook drafts): 30 rows: OK 14, FIX 16 (10 FIX-list items H1-H10, including one tag upgrade: doc 22 Lesson 2 had a post hoc reading tagged E).
- Part C (re-check): all 26 FIX items fixed; sync rc 0, 2 files redacted, 0 names left; new texts not redacted.
- Part D (staged set): 698 files, 0 images, 0 PDFs, 0 over 1 MB, 0 B2 files, nothing out of scope.
