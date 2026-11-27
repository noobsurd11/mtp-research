# app_thermal.tex: sources for every number and dated fact

Writer id: `thermal`. Draft 27 Nov 2026. Appendix `\chapter{Thermal imaging study}\label{app:thermal}`.

## Source keys (paths)
- **H22** = `handbook/22_thermal_desk_study.md` (local `/home/yugma/mtp/research/handbook/22_thermal_desk_study.md` and server `/home/yugma/mtp/research/handbook/22_thermal_desk_study.md`; same md5 d7b88c3e on both, checked 27 Nov).
- **TF** = server `/home/yugma/mtp/research/team_2026-11-04_thermal/` (the current copy). Files below are relative to TF.
- **LOG** = `TF/log.md` (md5 7a99a7d9). Line numbers are file line numbers as printed by `grep -an "" log.md` (line 149 starts with NUL bytes; use `grep -a`).
- **G0** = `TF/pick1/out/G0.md`; **G0v2** = `TF/pick1/out/G0v2.md`; **PP1** = `TF/pick1/plan_pick1.md` (md5 fb46b6dc).
- **P3R** = `TF/pick3/out/PICK3_A1_REPORT.md`; **ADD** = `TF/synth/ADDENDUM_2026-11-04.md`; **SUM** = `TF/synth/SUMMARY.md`; **RANK** = `TF/synth/ranked_ideas.md`.
- **DLV** = `TF/datasets/download_verified.md`; **DT** = `TF/datasets/dataset_table.md`.
- **OMT** = `TF/om_2026-11-04_thermal.md`; **OMD** = `TF/om_2026-11-04_decisions.md`; **README** = `TF/README.md`.
- **S4** = server `/home/yugma/mtp/research/team_2026-11-12_frontier/results/severity/S4_DTU_THERMAL.md` (131 lines, post-wording version).
- **FLOG** = server `/home/yugma/mtp/research/team_2026-11-12_frontier/log.md`.
- **CH10** = thesis `chapters/ch10_deployment.tex`.

## Wording choices (for the lead)
- The person who sent the thermal brief and the 4 Nov decisions is named in the sources ("Om"); he is not one of the two students, so the .tex calls him "a collaborator" (audit 27 Nov, on the lead's instruction: the role is unconfirmed; the earlier draft said "the project coordinator").
- The industry partner is named in the sources (WattCycle Sustainable Solutions); the .tex says "the industry partner".
- The study's roles (sources: `datascout`, `ideas`, `capture`, `synth`, `check`, `team-lead`) are written as "the data role / data search", "the pick 3 role", "the checker", "the study's lead". Source: README l.26-33.
- Rupee amounts: the sources write "₹"; the .tex writes "INR" (no other change).
- "the laptop": the 4 Nov work ran on the laptop (H22 l.63 "no server access"); no host name in the .tex.

## Opening and conventions
| .tex statement | Source | Quote |
|---|---|---|
| work from 4 Nov 2026 on; A3 drone-thermal result reported in ch10 | CH10 l.67-74 | "\section{What thermal imaging adds} ... We make no cell-level thermal claim." |
| no model trained on thermal, no GPU, no test/E1 image opened | README l.35-46; H22 l.63; S4 l.4 | "no GPU work of any kind without Om's OK"; "No test or E1 reads"; S4: "nothing trains or tunes a model ... No sealed cell (legacy test, E1) is read." |
| ΔT definition | H22 l.48; G0 l.10 | "ΔT: a cell's median temperature minus the module median of cell medians (°C)" |
| EL dark fraction, 0.5 × module median, opening, EL-dark if ≥ 5% | H22 l.49; G0 l.10 | "share of a cell's inner pixels below 0.5 × the module median ... a cell is "EL-dark" ... if it is ≥ 5%. An EL-only stand-in for E-PF's inactive prediction, because E-PF inference was held" |
| AUROC (cooler), 0.5 chance; Spearman ρ | H22 l.50 | "AUROC (cooler): how well −ΔT ranks EL-dark cells above the others (0.5 = chance, 1 = perfect)" |

## Section "4 November, morning: the brief and the desk study"
| .tex statement | Source | Quote |
|---|---|---|
| brief dated 3 Nov, pasted 4 Nov | OMT l.1-3 | "# Om: thermal (IR) direction (3 Nov 2026)"; "Pasted by the user on 4 Nov 2026." |
| three questions (public paired data; ways thermal helps incl. drone IR screening / EL detail; capture by partner or IIT Mandi) | OMT l.5 | "(1) find any public datasets with paired or co-registered EL and thermal ... (2) every way thermal could help ... (3) whether WattCycle or IIT Mandi could capture paired EL + thermal" |
| optimistic; tag E/R/S | README l.6-11 | "Be OPTIMISTIC and GENERATIVE"; "Tag every claim" |
| rules: no downloads, no GPU, no outside contact, no test/E1 reads, no hand-label asks | README l.35-46 | as quoted above; "No contact with anyone outside"; "No manual labelling asks." |
| roles | README l.26-33 | table datascout / ideas / capture / synth / check |
| team started 11:56 | LOG l.1 | "2026-11-04 11:56 IST team-lead: team started from Om's brief" |
| Table thermal-physics rows (crack mode A none / no hot spot / ≤ ~1 °C; inactive cooler / warmer; scuff unknown; shunt/PID hot spot; interconnect visible from 600 W/m²) | H22 l.68-75 | table "Our class / EL / Dark forward-bias IR / Sunlit (drone) IR"; e.g. "cracked modules "difficult to distinguish from healthy ones", ≤ ~1 °C (R: DTU, EPJ PV 2025)"; "visible from 600 W/m² (R: DTU)" |
| mode A mapping is ours (S) | H22 l.70 | "Crack that isolates nothing (Köntges mode A, S mapping)" |
| JRC: dark IR "few local information"; illuminated IR separates classes | H22 l.77; RANK l.12 | "dark IR gives "few local information"; illuminated IR separates damage classes in line with EL. So a weak dark-IR result is expected and is not a reason to drop illuminated IR." |
| drone IR ≤ 3 cm/px gives ~5-16+ px across 156 mm cell | H22 l.78 | "drone IR at ≤ 3 cm/px gives ~5-16+ pixels across a 156 mm cell, so it is a cell-level signal" |
| net reading (consequence not crack lines; teacher, weak label, triage, severity; benchmarks have no thermal) | H22 l.79 | "It sees **electrical consequence, not crack lines**. ... since BenchmarkEL, test and E1 have no thermal (E), any gain on our benchmarks must come from an EL-only model trained with paired data." |
| E1 gap = cracks in half-cut cells with scuff (named in the team's brief, README, not in the collaborator's brief OMT); thermal cannot fix it directly | H22 l.60, l.167; README l.16 | "75% of missed crack pixels sit in half-cut cells with scuff streaks"; "Why can thermal not fix the E1 scuff + half-cut crack gap directly? (§2: thin cracks and probably scuff are thermally silent; E1 has no thermal.)" (the .tex gives no number here; ch09 holds the hard-stratum numbers) |

## Section "public paired data sets"
| .tex statement | Source | Quote |
|---|---|---|
| section times 11:57 to 12:53 | LOG l.3, l.56 | "11:57 IST datascout: started"; "12:53 IST datascout: applied check re-check nits ... to dataset_table.md" |
| no public pixel-registered EL + thermal with masks | H22 l.82 | "No public set gives pixel-registered EL + thermal at cell level with crack or inactive masks" |
| three sets, CC BY 4.0, same physical modules, module-level pairing | H22 l.82 | "Three open sets, all **CC BY 4.0**, give EL and IR of the **same physical modules** (module-level pairing ...)" |
| ~215 with IR, ~203 with both | H22 l.91 | "About **215 public modules have IR** (A1 157, A2 15, A3 43); about 203 have both EL and IR" |
| other rows: 5 EL+PL, 4 EL+visible/NIR (only C1 Polenghi pairs the same cell), 12 thermal-only, 12 in-paper | H22 l.92 | "5 EL + PL rows (B1-B5 ...), 4 EL + visible / NIR rows (only C1, Polenghi et al., ... pairs the same cell ...), 12 thermal-only labelled sets (D1-D12 ...), 12 in-paper sets not released (E1-E12)" |
| A1: 10-year rooftop, mono Al-BSF, 36 cells 3×12, 156 characterised, IR for 157 | H22 l.86 | "10-year Florida rooftop, Shell M55 mono Al-BSF, 36 cells in **3 × 12** (E) | 156 characterised; IR for 157" |
| A1 IR 3.39 A (~1 × Isc), 180 s by names, paper 5 min, 240 × 320 °C | H22 l.86 | "dark forward-bias at 3.39 A (~1 × Isc), 180 s by file names (the paper says 5 min), 240 × 320 °C matrices (E)" |
| A1 EL 6 currents, 14.95 GB; IR 0.26 GB; UVF 2.01 GB; dark I-V 158 files | H22 l.86 | "Nikon D5100 + 950 nm long-pass, 6 currents | UVF, I-V, **EL-derived per-cell dark I-V** (158 files) | EL 14.95 GB; IR 0.26 GB; UVF 2.01 GB" |
| A1 paper Colvin et al. 2023 IEEE JPV | H22 l.86; DT l.14 | "Colvin et al., IEEE JPV 2023, doi:10.1109/jphotov.2023.3238278" |
| A2: 19-year array, mono, 72 cells 6×12, 42 modules, IR for 15 (camera failed), 5.289 A, 60 s, 16 captures, EL 6 currents 3.82 GB, IR 0.02 GB, UVF, I-V | H22 l.87 | "19-year convention-centre array, SolarWorld mono, 72 cells 6 × 12 (E) | 42; IR for 15 (camera failed) | dark forward-bias at 5.289 A, 60 s (16 captures) | 6 currents (NEF) | UVF, I-V | EL 3.82 GB; IR 0.02 GB" |
| A3: cracks 8, interconnects 8, PID 6, diode 7, glass 2, soiling 6 + 6; 43; drone 8/10/14/20 m; 200 to > 800 W/m²; 605 × 363 °C; one NEF per degraded module; STC I-V V, I only; 642.6 MB | H22 l.88 | "cracks 8, interconnects 8, PID 6, bypass diode 7, glass 2, soiling 6 + 6 | 43 (31 degraded + 12 soiled) | **drone** (DJI Mavic 3T), 8 / 10 / 14 / 20 m, 200 to > 800 W/m², arrays 605 × 363 °C ... | one NEF per degraded module ... | STC I-V (V, I only; E) | 642.6 MB archive" |
| A3 paper = delpradosantamaria2025drone (EPJ PV 2025, doi 10.1051/epjpv/2025020) | DT l.16; references.bib l.98-106 | "paper Del Prado Santamaria et al., EPJ PV 2025, doi:10.1051/epjpv/2025020" |
| A1/A2 old full-cell, no half-cuts, no scuff; A1 "primarily resistive"; A3 half-cut only in diode/glass/soiling, none cracked; no set shows scuff | H22 l.90 | "A1 and A2 are old **full-cell mono** modules (no half-cuts, no scuff); A1's losses are "primarily resistive" (R, Colvin 2023) ... A3 has half-cut bifacial PERC modules only in its diode, glass and soiling groups, **none with a crack** ... No set is known to show scuff." |
| reading: enough for feasibility, not fusion at scale | H22 l.91 | "Enough for a feasibility study of cross-modal weak labels and a demo pipeline, not for training a fusion model at scale (S)." |

## Section "ideas, ranking and the top three"
| .tex statement | Source | Quote |
|---|---|---|
| times 12:08 to 12:59 | LOG l.7, l.71 | "12:08 IST ideas: context read; Research MCP sweep done"; "12:59 IST check: closed synth pass 2" |
| 40 ideas T01-T40 in 8 families (families listed) | H22 l.96; LOG l.10 | "**40 ideas T01-T40 in 8 families:** fusion ... (T01-T05); cross-modal pretraining and distillation ... (T06-T11); thermal and physics as weak labels (T12-T16 ...); EL ↔ thermal synthesis (T17-T21); thermal for unseen-panel generalisation, incl. **T22** the "thermal silence" test for scuff (T22-T25); the industrial pipeline ... (T26-T30); other modalities, incl. **T31** EL / PL contrast ... **T32** UVF crack lines vs scuff (T31-T36); data and evaluation, incl. **T37** a registered A1 cell-level EL + IR + UVF set as a release (T37-T40)" |
| honest limits | H22 l.98 | "no direct fix for the scuff + half-cut crack gap; no gain on test or E1 from thermal inputs; pretraining starts with a weak record here (A8 KILL, MIM n.d., P15 null; docs 19-21); cell-level, not pixel-level" |
| 14 drone-only ideas W01-W14 (queue with pre-registered predictions, ID map + half-cut survey, physics-rule baseline) | H22 l.97; LOG l.33 | "**14 drone-only ideas W01-W14** ... an IR-ranked EL queue with pre-registered predictions (W01), a module ID map with a half-cut survey (W02), a physics-rule baseline (W03)" |
| plus 7 X ideas; 58 rows; score value × probability / √effort; all scores S | H22 l.101; LOG l.16, l.41 | "merged the lists (plus X1-X7 ...) into **58 rows** ... scored each by value × probability / √effort (**all scores are S**)" |
| top ten T26, T37, T15, W03, T27, W02, W01, T02, X3, W11 | H22 l.101; RANK l.74-83 | "Top 10: T26, T37, T15, W03, T27, W02, W01, T02, X3, W11." |
| pick 1 content and kill (top 20% hold ≤ 20% of EL dark area, or G0 null in both conditions) | H22 l.103 | "Kill if the top 20% IR-ranked modules hold ≤ 20% of the EL dark area, or G0 is null in both conditions." |
| pick 2: visit day and a night; ~₹27k-30k | H22 l.104; SUM l.37 | "a visit day and a night; ~₹27k-30k of kit" |
| pick 3: T15 → T02 → T12, T37 output; ~5.5 GPU-h only if gated | H22 l.105 | "T15 → T02 → T12, with T37 as an output; GPU (~5.5 GPU-h) only if gated" |
| original capture P0: 5-6 modules (≥ 2 half-cut, ≥ 2 scuff-like); EL 0.1 and 1.0 × Isc; dark IR; UVF; RGB; Al-tape fiducials; ~₹45k-55k if EL rig exists; scuff-candidate logic | H22 l.109 | "one day, 5-6 recycler modules (≥ 2 half-cut, ≥ 2 with scuff-like streaks); EL at 0.1 and 1.0 × Isc, dark IR under the same bias, UVF, RGB; aluminium-tape fiducials ...; ~₹45k-55k of kit if an EL rig exists ... an EL-dark streak with no thermal or UVF signature is a scuff candidate, while EL-dark plus a thermal anomaly is a crack or inactive candidate." |
| re-plan: triage and pairing, not crack labeller; Pi HQ + 300 W ~₹25k plus lens and filter; Si sensitivity near 1,150 nm unconfirmed; drone EL needs SWIR ~€10k-15k: no | H22 l.110 | "drone IR is a **triage and pairing** tool, not a crack labeller ... a Raspberry Pi HQ camera with its IR-cut filter removed, plus a 300 W supply, ~₹25k plus lens and filter (Si sensitivity near 1,150 nm unconfirmed) ... Drone EL needs a SWIR camera (~€10k-15k): no." |
| Q1-Q20 and U1-U3, not sent | H22 l.111; SUM l.67-103 | "**Questions:** Q1-Q20 for WattCycle and IIT Mandi, U1-U3 for dataset authors ... **Not sent**" |
| fact-check pass 1: 110 items, OK 73, FIX 31, UNVERIFIABLE 6; A1 IR bias-matched on ~157 | H22 l.106; LOG l.21 | "pass 1 on datasets / ideas / capture: 110 items, OK 73, FIX 31, UNVERIFIABLE 6 (... e.g. A1's IR turned out to be bias-matched forward-bias IR on ~157 modules)" |
| pass 2: 33 items, OK 13, FIX 18, UNVERIFIABLE 2 | H22 l.106; LOG l.36 | "Pass 2 on synth: 33 items, OK 13, FIX 18, UNVERIFIABLE 2."; LOG l.36: "correction to the 12:44 line: pass 2 counts are OK 13, FIX 18, UNVERIFIABLE 2 (33 items)" |
| top three unchanged | LOG l.35, l.28 | "Top 3 unchanged."; "top-3 picks unchanged" |

## Section "decisions and downloads"
| .tex statement | Source | Quote |
|---|---|---|
| decisions logged 12:39 | LOG l.25 | "2026-11-04 12:39 IST team-lead: OM'S DECISIONS" |
| (1) downloads approved, CPU only, A3 + A2 subset + A1 subset with dark I-V, ~1.2 GB; 0.55 GB extension needs OK | OMD l.5 | "(1) DOWNLOAD APPROVED: the public sets for picks 1 and 3 (A3, the A2 subset, the A1 subset with dark I-V; about 1.2 GB, CPU only ...; the later 0.55 GB A1 extension still needs Om's OK)" |
| (2) partner has only drone thermal; EL rig 2-3 months away; re-plan pick 2 | OMD l.5 | "they have ONLY a drone thermal setup right now; their EL rig is 2-3 months away. So re-plan pick 2" |
| (3) open: inference location, licences / release, capture funding; so E-PF not run (in the 4 Nov study), EL dark fraction used | OMD l.5; H22 l.114; S4 l.42 (audit: the PF fold models were later run on A3 EL crops on 15 Nov, so "not run" is limited to 4 Nov) | "(3) Still open for Om: E-PF inference location (gaint CPU vs local), licences / release, capture funding."; "Because of (3), E-PF was not run: picks 1 and 3 used the EL dark fraction instead." |
| A1: all 159 dark I-V files + 10 modules by frozen seeded severity-stratified rule; 5 bins × 2; max always in; 209 files; 286,886,436 B | H22 l.115; LOG l.43; DLV l.11, l.19 | "A1 209 files (all 159 dark I-V files + 10 modules chosen by a frozen, seeded, severity-stratified rule), 286,886,436 B"; LOG l.43: "5 quintile bins x 2, rng 20261104, bin 5 always takes max s" |
| A2: all IR + one bias-matched EL per IR module; 47 files; 237,009,189 B | H22 l.115; DLV l.12 | "A2 47 files (all IR + one bias-matched EL per IR module), 237,009,189 B" |
| A3: 642,610,942 B, extracted to 1,414 files | H22 l.115; DLV l.13, l.42 | "A3 7z (642,610,942 B) + README, extracted to 1,414 files" |
| verified against publishers' hashes by data role and independently by checker | H22 l.115; LOG l.96, l.143 | "All verified against the publishers' hashes by datascout and independently by check" |
| 12 Nov re-check after OS reinstall, 0 failures | LOG l.153; H22 l.22 | "md5sum -c of each MANIFEST.md5 (A1 210 lines, A2 48, A3 1,416): 0 failures" |
| section end time 13:47 | LOG l.141 | "13:47 IST datascout: A3 extracted fully (1,414 files ...)" |

## Section "pick 1 (G0)"
| .tex statement | Source | Quote |
|---|---|---|
| plan frozen 12:55-12:56 before any pick-1 data value | LOG l.62, l.63 | "12:55 IST datascout: FROZEN pick1/plan_pick1.md v1 ... No data value read for pick 1 yet"; "12:56 IST datascout: re-FROZEN pick1/plan_pick1.md v1 md5 28b58cc9" |
| six amendments, each before the numbers it governs | PP1 l.61, 69, 73, 84, 89, 95; H22 l.117 | "Amendments 1-6, each frozen before the numbers it governs" |
| go AUROC ≥ 0.8 with predicted sign; null |ρ| < 0.3 and AUROC < 0.7; kill only if null in both conditions | PP1 l.41; G0 l.12; H22 l.51 | "go if AUROC ≥ 0.8 with the predicted sign. Kill for the fusion / weak-label families only if |ρ| < 0.3 and AUROC < 0.7 in **both** conditions" |
| "between" for anything else | G0 l.17 | "between: signal with the predicted sign, below the 0.8 go bar" |
| exclude module if residual > 5% of cell side | G0 l.11 | "QA: module excluded if EL or IR registration RMS residual > 5% of a cell side." |
| orientation: authors' A1 crop = raw rotated 180°; rot180 primary A1, A2 by same lab/rig (S); others reported | PP1 l.79-80; LOG l.80; H22 l.118 | "the authors' own A1 IR crop is the raw IR rotated 180°, so the primary is rot180 for A1, and for A2 by the same lab and rig (S); the other 3 orientations are reported" |
| G0 v1 at 13:10, tool v0.2 | LOG l.87; G0 l.6 | "13:10 IST datascout: PICK1 G0 (dark IR) readout ... g0_stats.py 27f7bff1, cellreg v0.2" |
| Table G0 v1 rows (9/15, 648/230, −0.550, 0.736, between; 7/10, 252/50, −0.285, 0.689, null; pooled 16, 900/280, −0.451, 0.708, between) | G0 l.17-19; H22 l.121-125 | "A2 ... | 9 / 15 | 648 | 230 | −0.550 | 0.736 |"; "A1 ... | 7 / 10 | 252 | 50 | −0.285 | 0.689 |"; "Pooled | 16 | 900 | 280 | −0.451 | 0.708 |" |
| G0 cannot be killed by A3 | G0 l.37 | "**G0 cannot be killed by A3.** ... the dark condition is not null (A2 |ρ| 0.55, pooled 0.45; only A1 alone is null)" |
| checker recomputed from raw files: match | LOG l.99; H22 l.120 | "G0 v1 recomputed from raw EL NEF + IR txt ...: MATCH all values" |
| robustness: A2 vertically flipped maps carry the signal; best of 4 p = 0.001 both | G0 l.26-28 | "A2 | ... | 0.762 (flipv), p = 0.001"; "A1 | ... | 0.710 (flipv), p = 0.001"; "In A2 the two vertically flipped maps (rot180, flipv) carry the signal and the two unflipped (id, fliph) do not" |
| tone-mapped 8-bit previews; IR cells 12-15 px | G0 l.7, l.38 | "EL = NEF JPEG preview (tone-mapped, 8-bit): dark fractions are approximate."; "IR cells are only 12-15 px" |
| post hoc row/col centring: AUROC A2 0.49-0.52, A1 0.52-0.57; first computed after readout; reading (string/edge vs artefacts) | G0 l.31; LOG l.89 | "Subtracting row and column medians removes the signal everywhere (A2 ρ −0.07 to 0.00, AUROC 0.49-0.52; A1 ρ −0.17 to +0.05, AUROC 0.52-0.57) ... real string / edge-row degradation, but equally fits shared artefacts" |
| 13:13 drift found by pick 3 role; v1 marked provisional | LOG l.91, l.93; G0 l.3 | "**Status: PROVISIONAL** (cellreg v0.2). `ideas` found that the residual QA can pass while the grid has drifted" |
| G0 v2 setup (frozen reviewed v0.4.1, written visual criteria, edge check, blind co-sign before any number; rules unchanged) | G0v2 l.4; LOG l.102, l.128 | "registration with the frozen, reviewed cellreg v0.4.1 ... QA = residual ≤ 5% + pre-stated visual criteria ... calls made from overlays / reg.json only and co-signed by check before any v2 number" |
| G0 v2 at 13:43 | LOG l.131 | "13:43 IST datascout: G0 v2 written pick1/out/G0v2.md" |
| Table G0 v2 rows (4/15, 288/75, −0.515, 0.732, centred 0.525, between; 4/10, 144/36, −0.246, 0.621, centred 0.343, null; pooled 8, 432/111, −0.403, 0.687, between) | G0v2 l.9-11; H22 l.130-132 | "A2 | 4 / 15 | 288 / 75 | −0.515 | 0.732 | ... | −0.021 / 0.525 | between"; "A1 | 4 / 10 | 144 / 36 | −0.246 | 0.621 | ... | +0.231 / 0.343 | null"; "Pooled | 8 | 432 / 111 | −0.403 | 0.687" |
| checker recompute of v2: match | LOG l.137 | "G0 v2 recomputed independently ...: MATCH all values" |
| sensitivity B: six borderline modules; pooled 0.706 | G0v2 l.15; LOG l.128 | "Pooled 14: 0.706"; "Borderline 6 for sensitivity B" |
| v1 finding not a misregistration artefact | G0v2 l.19 | "The v1 post hoc finding holds with the fixed registration, so it was not a misregistration artefact" |
| A1 centred AUROC 0.343, EL-dark warmer; series-resistance reading; 4 modules, 36 positives, descriptive | G0v2 l.20 | "on A1 the row/col-centred AUROC(cooler) is 0.34, i.e. EL-dark cells read **warmer** ... Descriptive only (4 modules, 36 positives)" |
| A3 R1, R2, R3b never run; A3 discovery 13:47-13:50; module fills the array; Amendment 6: R1 whole array with 3% inset | H22 l.137; LOG l.147; PP1 l.98, l.101 | "**Not run:** the sunlit A3 arm (R3b), the A3 screening table (R1, R2) ... Amendment 6: the module fills the IR array ...; R1 uses the whole array with a 3% inset" |
| R2 = screening recall, the pick's kill | PP1 l.31-34 | "### R2. A3 screening recall vs EL ... kill if ≤ 20%" |

## Section "pick 3"
| .tex statement | Source | Quote |
|---|---|---|
| section start 12:46 (plan v0.9) | LOG l.37 | "12:46 IST ideas: pick3/plan_pick3.md v0.9 written ... before any data content read" |
| plan v1.2 frozen 12:59 with disclosures | LOG l.70 | "12:59 IST ideas: FROZEN pick3/plan_pick3.md v1.2 md5 2893a817 (adds §7 disclosure" |
| d = module median voltage minus cell voltage at highest current 3.392-3.393 A | P3R l.19 | "d = module median P − P, with P the cell's EL-derived voltage at the highest current (3.392-3.393 A)" |
| kill: coverage < 50% or robust SD(d) < 2.57 mV (0.1 V_t) and < 1% of cells d ≥ 1 V_t | H22 l.140; P3R l.12 | "Frozen kill: coverage < 50%, or "no spread" = robust SD(d) < 2.57 mV (0.1 V_t) **and** < 1% of cells with d ≥ 1 V_t" |
| second clause met by construction; module max 19.3 mV on record before the read; disclosed | H22 l.140; LOG l.61, l.68 | "the second clause was met by construction (the module maximum, 19.3 mV < 1 V_t, was on record before the read), so the kill rested on the SD clause" |
| readout 13:00; 5,688/5,688 valid; SD 3.26 mV; PASS narrow | LOG l.74; P3R l.12 | "coverage 1.00 (5,688 / 5,688); robust SD(d) **3.26 mV** (0.127 V_t) ... **PASS, narrow**" |
| checker recompute match | LOG l.76 | "independent T15 recompute ... -> PASS narrow; MATCH with ideas" |
| D90 = d ≥ 4.23 mV, 569 cells, 144 of 158 modules; no cell at 1 V_t | P3R l.20-22 | "D90 = d ≥ 4.23 mV: 569 cells."; "DVt = d ≥ 1 V_t: 0 cells"; "D90 cells sit in 144 of 158 modules" |
| reading: diffuse resistive deficit, dimmest ~10%, ~1.18× EL dimming | P3R l.26 | "D90 marks roughly each module's dimmest 10% of cells, at ~1.18× EL dimming" |
| 158 modules | P3R l.12 | "**T15** dark I-V label (158 modules, 5,688 cells)" |
| T37 rule: residual > 5% excluded; pick kill if > 30% | P3R l.13 | "a module is excluded if EL or IR inner residual RMS > 5% of a cell; pick kill if > 30% excluded" |
| v1 at 13:13, 3/10 excluded = 30%, PASS at the line | LOG l.91; P3R l.13 | "3 / 10 excluded ... = 30% | **PASS at the line**" |
| included module misregistered at 4.49% | LOG l.91; P3R l.45 | "EL 6320427227 is misregistered despite 4.49%" |
| UVF 9 of 10 over 5% | P3R l.14 | "9 / 10 over 5%" |
| v2 at 13:28 (post hoc), 4/10 by frozen 5% rule, grid-vs-outline over 20% on all 10, FAIL | LOG l.108; P3R l.15 | "5% rule: 4 / 10 excluded = 40% ...; grid-vs-outline: EL 23.9-35.4%, IR 44.6-81.7% on all 10 | **FAIL** on both the frozen 5% rule and its own N7 rule" |
| root cause: fixed 134 × 35 window, module ~145 × 37 px, trims ~0.9 cell, ~7% pitch error; register on raw frame | H22 l.142; P3R l.37-41; LOG l.109 | "a **fixed 134 × 35 pixel window**, not the module (the module is ~145 × 37 px), so it trims ~0.9 of a cell; forcing 12 columns into it gave a ~7% pitch error. Any future A1 work must register on the raw IR frame." |
| crop geometry E, role S | H22 l.142 | "(check CR-5; the crop geometry is E, its role in the failure is S)" |
| quotes "a bright pixel from each cell"; "cells with bright spots in high injection EL show higher RS values"; direction may be inverted | P3R l.28-30; H22 l.143 | as quoted |
| decision (A) ~13:28 by team-lead; T02/T12 never ran | LOG l.149 (retrospective, line starting with NUL bytes); H22 l.144; P3R l.3 | "13:28 PICK 3 DECISION (A): A1 arm stops at T37 as pre-registered"; P3R: "messages of 4 Nov ~13:3x" (see CONFLICTS) |
| reasons, incl. forking path | P3R l.26-34 | "4. **A third, post hoc registration would add a forking path for a likely null** (team-lead)." |
| pick3b frozen 13:43 before extraction; 3b-R1, R2, R3 (interconnect primary) | LOG l.134; H22 l.144; ADD l.24-26 | "FROZEN pick3/plan_pick3b.md v1 md5 eaec6f26 ... A3 not extracted at freeze" |
| no module type → FF loss primary; one EL per module → 3b-R4 not run; no pick3b statistic | LOG l.144; H22 l.144 | "module type is not in folder / file names ... FF loss ... becomes the PRIMARY label"; "**No pick3b statistic was computed.**" |

## Section "abrupt end and the record"
| .tex statement | Source | Quote |
|---|---|---|
| abrupt end ~13:51, cause unknown; NULs in pick3b plan and log; empty v1.1 freeze file; empty A3_layout.tsv; no readout or frozen copy affected | H22 l.160 | "**Abrupt end (~13:51, 4 Nov; cause unknown ...):** NUL bytes in `pick3/plan_pick3b.md` ... and in the thermal `log.md` (line 149 ...), an empty `plan_pick3b_v1.1_FROZEN_c8f57302.md` ..., an empty `A3_layout.tsv` ... No readout file and no frozen copy is affected." |
| report not sent; addendum draft | LOG l.150; H22 l.30 | "ADDENDUM_2026-11-04.md (878e6bec) still DRAFT ...; the report to the user and Om was NOT sent before the session ended" |
| list of process faults | H22 l.161 | "Hand-typed times ahead of the clock ... Self-test criteria ... set post hoc ... A results file overwritten ... restored byte-exact. A registration tool version run on real data before its review ... one version announced and withdrawn. One visual-QA miss caught by check. A false premise about the A1 crop ... A scope slip (... all 157 A1 IR modules vs the 10 approved) caught by check before any download." |
| 12 Nov record and handbook written and independently verified; data re-verified | LOG l.152-166; LOG l.153 | "scribe: started session record 3-4 Nov"; "verifier: ... VERDICT: OK to commit"; "0 failures" |
| 12 Nov evening: no direct thermal pick | FLOG l.6 | "12 Nov 18:15 IST user answers: ... (3) thermal: no direct pick" |

## Section "15 and 16 November: thermal inside the severity track"
| .tex statement | Source | Quote |
|---|---|---|
| 15 Nov ask; taken up in severity track (unread A3 analyses), not a change of direction | FLOG l.71 | "15 Nov 21:46 IST user: suggested (as a question) a parallel track on defect severity ... and working on thermal images. ... thermal as part of that track (the unread A3 analyses of the 4 Nov study), not a switch of direction" |
| dated amendment 15 Nov 22:28 to 22:34, before any A3 statistic, not changed after | S4 l.7 | "written 15 Nov 2026 22:28 to 22:34 IST, before any A3 statistic of EL, I-V, thermal or prediction exists; not changed after" |
| why needed: outline rule replaced by Amendment 6; A3 module table never written; computed by pick 1's frozen definitions | S4 l.15 | "pick 1's Amendment 6 replaced that by the full array, so v1 requires a dated amendment ... pick 1's A3 module table ... was never written, so both measures are computed here by pick 1's frozen definitions" |
| S_IR = p99 − median inside 3% inset; median over frames ≥ 600 W/m² | S4 l.32 | "S_IR = p99 - median of the temperature array inside a 3% inset on every side ... Per module, S_IR = median over the frames at 600, 800 and abv800 W/m2, all altitudes." |
| bootstrap 2,000 draws | S4 l.27 | "module bootstrap 95% percentile interval (2,000 draws ...)" |
| bars: 3b-R1 valid ρ ≥ 0.5 with lb > 0, invalid ρ < 0.3; 3b-R2 same proxy bars; adds if ΔR² ≥ 0.10 with lb > 0; no added value if < 0.05; else in between | S4 l.28, l.35 | "label-valid if rho >= 0.5 with interval lower bound > 0; label-invalid if rho < 0.3"; "IR adds to EL if ΔR2 >= 0.10 with interval lower bound > 0; "no added value" if ΔR2 < 0.05; otherwise "in between"" |
| Table 3b: 3b-R1 all 31 +0.006 [−0.380, +0.425] label-invalid; non-diode 24 +0.636 [+0.236, +0.872] label-valid | S4 l.77-78 | "| all non-soiling | 31 | +0.006 [-0.380, +0.425] | label-invalid (< 0.3) |"; "| **non-diode** | 24 | **+0.636 [+0.236, +0.872]** | **label-valid**" |
| Table 3b: 3b-R2 ρ all −0.276 [−0.575, +0.114] not a proxy; ΔR² −0.021 [−67.7, +0.248] no added value; non-diode ρ +0.192 [−0.305, +0.626] not a proxy; ΔR² +0.102 [−0.177, +0.401] in between | S4 l.83-84 | "| all non-soiling | 31 | -0.276 [-0.575, +0.114] | not a proxy | ... | -0.021 [-67.7, +0.248] | no added value |"; "| **non-diode** | 24 | **+0.192 [-0.305, +0.626]** | **not a proxy** | ... | **+0.102 [-0.177, +0.401]** | **in between**" |
| non-diode numbers are those of ch10 | CH10 l.57-60, l.70-72 | "tracks FF loss on the 24 non-diode modules at $\rho$ 0.64 [0.24, 0.87]"; "($\rho$ 0.19) ... ($\Delta R^2$ +0.10, interval $-$0.18 to +0.40)" (ch10 rounds; same values) |
| all-module verdict label-invalid (interval includes 0); reading: a label effect (diode darkness and large Pmax loss not seen by FF) | S4 l.77, l.72, l.114 | "+0.006 [-0.380, +0.425] | label-invalid (< 0.3)"; "FF loss does not register the diode loss"; "The all-module null is a label effect, not a proxy failure: diode modules have the most EL darkness (missing substrings) and large Pmax loss, but FF does not see it" (audit: .tex wording changed from "does not track" / "the largest" to the verdict word / "a large") |
| per-cause S_IR medians: cracks 0.87, interconnects 1.40, PID 1.13, glass 1.57, diode 23.9, soiling 4.2 / 18.3 | S4 l.97-102 | "cracks ... | 0.87 [0.75, 1.05]"; "interconnects ... | 1.40 [0.75, 1.57]"; "PID ... | 1.13 [0.83, 1.37]"; "glass ... | 1.57 [1.47, 1.67]"; "bypass diode ... | 23.9 [16.5, 29.7]"; "soiling 1 / 2 ... | 4.2 [1.2, 22.8] / 18.3 [0.7, 37.5]" |
| 3b-R3 not run: needs R3b with co-signed QA; brief forbade cell-level claim | S4 l.36 | "**3b-R3 (cell-level thermal by cause): not run in this item.** Reasons: (1) ... R3b was never run and this item has no co-signer; (2) the lead's task for this item forbids any cell-level thermal claim" |
| 16 Nov review: no failing item, headline numbers reproduced; wording fixes changed no number | FLOG l.83; S4 l.117 | "severity track complete; review ...: no item fails (S0 to S4 PASS WITH NOTE; every headline number reproduced by the reviewer's own scripts"; same line, end: "Owed: the reviewer's four wording fixes (F2.1, F3.3, F4.1, F4.2; no number changes)"; S4 l.117: "[wording fixed 16 Nov, review F4.1]". (Audit 27 Nov: the earlier citation "FLOG l.86 ... no existing number changed" does not exist; l.86 is an unrelated tick.) |

## Section "What stays open"
| .tex statement | Source | Quote |
|---|---|---|
| not done: R1 as frozen (class table with AUROC; the severity track gave only per-cause S_IR medians, S4 l.97-102, by R1's frozen S_IR definition, S4 l.32), R2, R3b, 3b-R3, A1 extension, pick 2, report; addendum draft; open decisions (audit 27 Nov: R1 wording narrowed; PP1 l.25-26 defines R1a as n, median S_IR (IQR), median ΔT_max per class and R1b as AUROC per class, neither in S4) | H22 l.155-156; HB15 (server `handbook/15_status_remaining_work.md`) l.126, l.221-224, l.312-315; S4 l.129; ADD mtime 4 Nov 13:49 (`ls -la`, 27 Nov) | "**Not done (4 Nov end state):** pick 1 R1 / R2 / R3b; pick3b 3b-R1 / R2 / R3; the ADDENDUM is still a DRAFT ...; **the report to the user and Om was never sent.**"; "**Open for Om:** E-PF inference location; licences / release ...; capture funding; the A1 extension" |
| lessons 1-4 (our reading) | H22 l.147-150 | "1. **Thermal is an electrical-consequence signal.** ..."; "2. **Dark IR on the public pairs looks row / module-level, not cell-level** ... The sunlit arm (A3) and lock-in IR are the fair tests"; "3. **Know the dataset's physics before using it as a label**"; "4. **Instruments fail quietly:** a passing residual can hide a drifted grid; an author-made crop is not necessarily the module" |

## Audit 27 Nov
See `AUDIT_REC_thermal.md` in the working copy for every change made by the independent check.

## Count
About 165 numbers and dated facts in the .tex, each in a row above (counted by hand from the table rows; times, counts, sizes, statistics, intervals).

## MISSING_CITES
- Colvin, D. J. et al., "... (UCF fielded Shell M55 modules, OSF csr6t companion paper)", IEEE Journal of Photovoltaics, 2023, doi:10.1109/jphotov.2023.3238278 (as given in DT l.14 and ADD l.31; title not in our sources). Used as `\CITE{Colvin et al., IEEE J. Photovoltaics 2023, doi 10.1109/jphotov.2023.3238278}`.
- Berardone, I., Paggi, M., Lopez Garcia, J., 2017, "Image analysis of aged PV modules ..." (JRC report JRC105705; per RANK l.12 and DT l.67). Used as `\CITE{Berardone, Paggi, Lopez Garcia 2017, JRC105705}`.

## UNSOURCED
- None in the .tex. Left out because not found in a file: the exact title of Colvin 2023; any outcome of the pick 2 visit (nothing was done); whether the report to the collaborator was sent after 12 Nov (no source says it was; the addendum file is unchanged since 4 Nov 13:49).

## CONFLICTS (reported, not resolved)
1. A1 IR exposure: file names say 180 s, Colvin 2023 says 5 min (H22 l.86; ADD l.32). The .tex gives both.
2. Pick 3 decision time: retrospective log 13:28 (LOG l.149) and H22 l.144 "~13:28"; P3R l.3 "~13:3x"; LOG l.113 notes the decision at 13:35. The .tex says "about 13:30".
3. T15 margin: LOG l.74 "0.66 mV over the line" vs P3R l.12 "0.69 mV"; corrected to 0.69 in LOG l.123. The .tex gives no margin.
4. A3 size: the paper abstract says "43 degraded"; the DTU slides give 31 degraded + 12 soiled (DT l.16, "discrepancy, S"). The .tex says "43 in all".
5. A3 resolution in ch10 vs here: none. ch10's 3b-R1/3b-R2 values are the rounded non-diode values of S4 l.78 and l.84; consistent.
6. A3 EL in the DTU slides: "100% and 10% Isc", but the release has one EL per module (ADD l.27); the .tex says one EL image per module (what was found).
