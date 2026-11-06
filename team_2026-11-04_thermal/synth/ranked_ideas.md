# Thermal for our EL segmentation: all ideas, merged and ranked

Owner: synth. Date: 4 Nov 2026. Status: v1.4: Om's decisions of 4 Nov applied (WattCycle has drone thermal only; EL rig 2-3 months away). Merged ideas' `drone_only.md` (W01-W14) and capture's `replan_pick2.md` (X6, X7). Check's pass-1 and pass-2 fixes applied. Waiting for check's re-check.
Inputs: `ideas/ideas_long.md` (T01-T40, gate G0), `ideas/drone_only.md` v1 (W01-W14, 28f5b0a5), `capture/capture_plan.md`, `datasets/dataset_table.md` + `datasets/notes.md`, `check/factcheck.md` passes 1-2, `om_2026-11-04_decisions.md`, `capture/replan_pick2.md` v1.
Tags: **E** = measured in our files (path); **R** = from a source (id / URL, mostly via the three input files); **S** = my judgement. **Every score, probability and ranking in this file is S.** Facts are copied from the input files, the owners' replies and `check/factcheck.md` pass 1, with their tags; I added no new sources.

## 0. The physics finding, and how it shapes the ranking

- **Thermal sees electrical consequence, not crack lines.**
  - Cracks that isolate nothing gave no hot spot (R: doi:10.1038/s41598-021-03498-z, doi:10.1038/s41598-022-16546-z, via ideas §0).
  - In drone IR of A3's degraded modules (43 by the abstract; 31 degraded + 12 soiled by the DTU slides, check pass 3), cracked modules were "difficult to distinguish from healthy ones", while disconnected interconnects were visible from 600 W/m2 (R: doi:10.1051/epjpv/2025020, abstract).
- **What thermal does see:** disconnected / inactive areas (cooler under forward bias, warmer in sun; S, device physics), hot spots, shunts, failed solder joints (R: ideas §0.1 table).
- **Calibration, not a kill:** a JRC study of aged modules found that dark IR gives "few local information", while illuminated IR separates damage classes in line with EL (R: Berardone, Paggi, Lopez Garcia 2017, JRC105705, check D-46). A1 / A2 IR is dark forward-bias IR, so G0 should look for a per-cell signal (Rs, hot or cool cells), not sub-cell shapes (S). That favours the cell-level rows over the pixel-fusion rows.
- **Scuff:** its physical nature is not described in our files (E: `handbook/17_escdd_dataset_audit.md` §5.11 via ideas). If it is a surface mark, it should be thermally silent, like a crack that isolates nothing (S). So thermal alone cannot split scuff from a thin crack. UVF (crack lines in aged encapsulant) and RGB carry that split, with thermal as a second witness.
- **Consequence for the ranking (S):**
  - **Up:** screening, severity and inactive ideas, and the scuff arbiter with UVF.
  - **Down, not killed:** crack-pixel fusion and thermal pretraining. Fusion also cannot touch BenchmarkEL or E1, which have no thermal (E: `handbook/03`, via ideas §1). Pretraining has a weak record here (E: A8 KILL; MIM n.d.; P15 null; `handbook/00` fact 10, doc 21 §1).
  - No idea is dropped. Low ones stay in the table with their reason.

## 1. What was merged (dedupe)

| New / kept ID | Merged from | Why one row |
|---|---|---|
| **X1** scuff arbiter on captured half-cut modules | capture §8.1 ("EL-dark + no thermal / UVF signature = scuff"), T22 (thermal-silence test for scuff), T34 (RGB streaks), T32's capture part, a light T05 (forward-bias + one sunlit IR frame) | Same modules, same capture day, same output: a per-streak label "crack / scuff candidate" |
| **X2** WattCycle-domain unseen-module EL set | capture §8.3 ("WattCycle's cells would be another unseen source", E: `handbook/13` l.203) | Same capture as X1, different use (evaluation, deployment domain). Optional labels: about 2 to 5 h per 100 cells (S, capture §5) |
| **X3** severity series check on Polenghi C1 | datascout C1 note ("test whether our inactive predictions track power loss") | Not in ideas' list |
| **X4** module power loss vs EL maps on A1 I-V | datascout A1 (light / dark I-V per module, R), capture §8.6 and P1 item 6 (I-V per module) | Same question: per-module power loss vs predicted inactive / crack. Re-opens the power arrow, which is out of scope "unless we get some valid data" (E: `handbook/02` §9) |
| **X5** half-cut PL pool | datascout B4 / B5 (NREL field PL, 856 half-cut images, R) | Not in ideas' list |
| T26 | + capture §8.5 (dark-lab IR to drone IR link), datascout A3 note, datascout Q4 (WattCycle may hold drone IR + EL of the same plants) | One pipeline question |
| T08 | + datascout D-group pools (D1, D4, D11) as out-of-domain checks | Same IR student |
| T12 / T02 | + capture §8.2 (captured inactive weak labels) | Same label, other data source |
| T09 / T10 | + capture §8.4 (paired data for pretraining) | Same mechanism |
| T29 | + datascout B2 (passive EL / PL stacks) | Already its data |
| T31 | + datascout B1 (A1 close-up EL + PL) | Already its data |
| T38 | + datascout D2 / D3 naming link | Already its data |
| G0 | shared gate, not an idea | Its cost is counted once, inside top-3 pick 1 |
| W03 | its A3 part is T26's step 2 | The row keeps only the WattCycle-flight half |
| T19 | + W07 (IR → "expected EL" mapper, applied to WattCycle flights) | Same mechanism; W07 adds the WattCycle use |
| W11, W12 | X1's UVF and RGB arms, done without EL | Kept as rows because they can run now; X1 needs EL |
| W09 | field (no-supply) version of T36 | Kept apart: different cost and safety |
| W06 | overlaps T28 (IR time series) | Kept apart: W06 is IR-only and runs now |

58 rows after merging: T01-T21, T23-T33, T35-T40 (38) + X1-X7 (7) + W01-W06, W08-W14 (13). X6 and X7 come from capture's `replan_pick2.md` v1 (82ac3370): a low-cost EL camera, and reference EL + I-V at NISE. Capture's flight protocol (F1-F5) and metadata list are the method for W02 / W03 / W06 / W10 / W14, not separate rows.

## 2. Scoring (all S)

- **Value V**, 0 to 3 on each of 4 axes:
  - **UR:** crack recall on unseen modules, incl. scuff + half-cut;
  - **IN:** small, concentrated inactive;
  - **DE:** WattCycle deployment;
  - **TH:** a defensible thesis result within about 7 weeks.
  - V is the sum (0 to 12), unweighted.
- **P:** chance the idea reaches its own success signal (as written in ideas / capture, or below) before the thesis ends.
- **EV** = V × P.
- **Effort:** dev days + capture days (midpoints). GPU-h and money are listed apart, because GPU needs Om's OK and is cheap in hours: 1.1 GPU-h per R34 run at 100% labels (E: `handbook/14` l.320-323), so one 5-seed arm is about 5.5 GPU-h.
- **Score** = EV / √effort. The square root keeps cheap checks from crowding out valuable ones. Sorting is by Score.
- **Data:**
  - **none**;
  - **pub** = public download (needs Om's OK), with size;
  - **cap** = own capture.
- **First signal:** working days after the relevant OK (S).

Context numbers used in V (E):
- E1 crack recall 0.215 for FINAL (`handbook/00` fact 10).
- 75% of missed E1 crack px sit on half-cut multi cells with a scuff streak, recall 0.126 (`handbook/18` l.357).
- Training has 0 half-cut cells, and 649 scuff px are labelled crack (`handbook/18` l.362).
- The B3 scuff class was never learned: train scuff IoU 0.000 (`handbook/11` row 42).
- E1 inactive: 3 source images hold 87% of its px (`SESSION_RECORD_2026-11-01_to_11-03.md` §0).

## 3. The ranked table

| # | ID | Idea (one line) | UR/IN/DE/TH = V | P | EV | Cost: dev d / GPU-h / capture d / money | Data | First signal | Score | Pick |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **T26** | Drone / forward-bias IR screening, then EL: share of EL-visible damage (by defect mode) that an IR screen catches | 0/2/3/2 = 7 | 0.55 | 3.85 | 3 / 0 / 0 / 0 | pub: A3 DTU 642.6 MB (R; native < 1 to 3 cm/px, resampled to 363 × 605, check D-17) + A2 / A1 subsets | 2-3 d (module level, folder labels); +3 d with E-PF maps | 2.22 | **Top-3 #1** |
| 2 | **T37** | Registered cell-level EL + IR + UVF set from A1, released as a CC BY derivative | 0/1/1/3 = 5 | 0.65 | 3.25 | 5 / 0 / 0 / 0 | pub: A1, 10 modules ≈ 0.29 GB with UVF (R, check S-3: NEF EL ≈ 14.4 MB + IR 1.6 MB + UVF ≈ 12.6 MB each); all modules at one bias: EL 2.27 GB + IR 0.26 GB + UVF 2.01 GB ≈ 4.5 GB (R, check S-6) | 5 d for 10 modules | 1.45 | **#3** (thesis output) |
| 3 | **T15** | A1's EL-derived per-cell dark I-V as an annotator-free "electrically degraded" cell label | 0/2/1/1 = 4 | 0.50 | 2.00 | 2 / 0 / 0 / 0 | pub: A1 `EL-Derived_Cell_Dark_I-V`, 158 txt + 1 xls, 3.8 MB (R, check S-4) | 1-2 d | 1.41 | **#3** (reference label) |
| 4 | **W03** | Physics-rule IR anomaly score (cell ΔT, hot cell / substring / diode) on WattCycle flights; its A3 part is T26's step 2 | 0/1/2/1 = 4 | 0.50 | 2.00 | 2 / 0 / 0 / 0 (after T26) | WattCycle radiometric IR (export format unconfirmed) | 1 flight + 2 d | 1.41 | **#2** |
| 5 | **T27** | Hot-spot risk score from E-PF's per-cell inactive fraction and crack mode, checked against IR | 0/1/3/2 = 6 | 0.40 | 2.40 | 3 / 0 / 0 / 0 | pub: A1 / A2 (as G0) | ~1 week (after G0 registration) | 1.39 | **#1** |
| 6 | **W02** | Module identity map and fleet inventory, incl. a half-cut survey (does the scuff + half-cut context exist on WattCycle sites?) | 1/0/2/1 = 4 | 0.60 | 2.40 | 2-3 / 0 / 0.5 / 0 | WattCycle IR (+ RGB if any), site plans | visit day + 2 d | 1.39 | **#2** |
| 7 | **W01** | IR-ranked EL queue with pre-registered predictions: freeze which WattCycle modules the EL rig images first, and what we predict for them, before EL exists | 1/0/2/1 = 4 | 0.50 | 2.00 | 2 / 0 / shared visit / 0 | WattCycle drone IR now; WattCycle EL in 2-3 months (Om) | frozen pre-registration ~W4 (S); the test itself is read when EL arrives, likely after the thesis (S) | 1.26 | **#2** |
| 8 | **T02** | Late fusion: per-cell IR ΔT updates E-PF's inactive prior | 0/2/2/1 = 5 | 0.35 | 1.75 | 2 / 0 / 0 / 0 | pub: as G0 | ~1 week (after G0) | 1.24 | **#3** |
| 9 | X3 | Polenghi C1: does E-PF's inactive / crack area track measured power across 84 damage stages? The abrasion / scrape stages are also a public probe of what a surface scuff does in EL + NIR + visible (check D-19) | 1/1/2/1 = 5 | 0.35 | 1.75 | 2 / 0 / 0 / 0 | pub: C1 EL 0.20 GB; + visible HDR 0.93 GB; whole set ≈ 1.38 GB (R folder sizes, datascout reply) | 2 d | 1.24 | #2 (public scuff probe) |
| 10 | **W11** | UVF with a UV torch at night on end-of-life modules: crack lines now, crack vs scuff once EL arrives (X1's UVF arm without EL) | 2/0/1/2 = 5 | 0.40 | 2.00 | 2 / 0 / 1 night / UV torch ₹1,790-4,522 (R; low end is an old price) | WattCycle aged modules | visit night + 2 d | 1.15 | **#2** |
| 11 | W05 | Irradiance / altitude normalisation fitted on A3, applied to WattCycle flights | 0/0/2/1 = 3 | 0.50 | 1.50 | 2 / 0 / 0 / 0 | A3 (approved); WattCycle irradiance logs | 2-3 d | 1.06 | #2 (desk, on A3) |
| 12 | **W08** | Operating-point differential IR on end-of-life modules in sun (open circuit vs load vs short circuit): regions that do not cool under load are inactive candidates; no EL rig, no supply | 0/2/1/2 = 5 | 0.35 | 1.75 | 2 / 0 / 0.5-1 / a small DC load (price unconfirmed) | WattCycle camera + 5-20 end-of-life modules | visit day + 2 d | 1.06 | **#2** |
| 13 | T08 | EL teacher → small IR student (labels from E-PF on the EL half of each pair) for WattCycle's drone IR | 0/1/3/2 = 6 | 0.35 | 2.10 | 4 / 3 / 0 / 0 | pub: A1 / A2; D1 / D4 / D11 and Zenodo 10.5281/zenodo.20860870 (sUAS IR, 3,675 crops, 8 classes, 3.13 cm/px, CC BY 4.0; R via check S-33) for out-of-domain checks | ~1.5 weeks (after G0) | 1.05 | #1 (week 3+) |
| 14 | T19 | IR → coarse inactive fraction / "expected EL" per module, trained on public pairs, applied to WattCycle flights (T19 + W07) | 0/1/3/2 = 6 | 0.35 | 2.10 | 4 / 0-5 / 0 / 0 | pub: A1 / A2 / A3 (approved); WattCycle IR | ~1 week (A3 Spearman, shares pick 1) | 1.05 | #2 (feeds W01's predictions) |
| 15 | T39 | Thermal-outcome-weighted evaluation (a missed crack in a thermally anomalous cell costs more) | 0/1/2/1 = 4 | 0.35 | 1.40 | 2 / 0 / 0 / 0 | pub: as T26 / G0 | ~1 week | 0.99 | #1 (add-on) |
| 16 | **T12** | Thermal cell-level inactive labels on A1 + mixed supervision with BenchmarkEL masks | 1/3/1/2 = 7 | 0.25 | 1.75 | 4 / 5.5-11 / 0 / 0; 0.5 h glance | pub: as G0; all 157 A1 modules ≈ 2.5 GB if the counts need it (S) | ~2 weeks (GPU arm after) | 0.88 | **#3** (week 3+) |
| 17 | X4 | Module power loss (A1 I-V) vs E-PF inactive / crack per module | 0/1/2/2 = 5 | 0.30 | 1.50 | 3 / 0 / 0 / 0 | pub: A1 I-V 0.23 MB, pseudo I-V 4.0 MB, dark I-V 0.24 MB (R, check S-9) | 3 d | 0.87 |  |
| 18 | T31 | EL / PL contrast → automatic inactive masks (isolated areas still emit in PL) | 0/3/1/2 = 6 | 0.25 | 1.50 | 3 / 0 / 0 (PL capture later: 2-3) / 0 | pub: B1, 11 files (6 TIF + 5 JPG), 0.11 GB (R, check S-7) | 2-3 d | 0.87 |  |
| 19 | W10 | Low-altitude / handheld close-range IR on flagged modules (cell resolution) | 0/1/1/0 = 2 | 0.50 | 1.00 | 1 / 0 / 0.5 / 0 | WattCycle drone or handheld | visit day | 0.82 | #2 (visit add-on) |
| 20 | W13 | Soiling vs electrical anomaly: IR before / after cleaning, or with RGB | 0/0/2/0 = 2 | 0.50 | 1.00 | 1 / 0 / 0.5 / 0 | WattCycle IR (+ RGB) | after cleaning | 0.82 |  |
| 21 | **X2** | WattCycle-domain unseen-module EL set (E-PF run on it; labels optional) | 1/1/3/2 = 7 | 0.20 | 1.40 | 2 / 0 / shared with X6 / in X6's kit; needs EL (X6 or WattCycle's rig) | cap (about 0.5 GB per module, S, capture §5) | capture day + 2 d | 0.81 | #2 if X6 passes (W01 sets it up) |
| 22 | T32 | UVF crack lines vs EL cracks on A1 (public pre-check for X1) | 1/0/1/2 = 4 | 0.35 | 1.40 | 3 / 0 / 0 / 0 | pub: A1 UVF + EL, 10 modules ≈ 0.27 GB (R, check S-3) | 3 d | 0.81 | #2 (public UVF pre-check for W11) |
| 23 | T29 | Segmenter robust to daylight-EL SNR (drone IR + daylight EL in one flight) | 1/0/2/1 = 4 | 0.40 | 1.60 | 4 / 11 (only if the arm runs) / 0-3 / 0 | pub: B2 2 × 264.9 MB (R); val for the first CPU test | 1-2 d (CPU noise test) | 0.80 |  |
| 24 | **X6** | **Low-cost EL camera now:** Raspberry Pi HQ camera with the IR-cut filter removed, 850 nm long-pass, Pi 5 and the 300 W supply. Bench test, then a night EL session on WattCycle end-of-life modules. Treat the images as a WattCycle-domain test set, not training data (capture replan §3) | 1/0/2/1 = 4 | 0.40 | 1.60 | 2 / 0 / 1 bench + 1 night / about ₹25k + lens and filter (R/S, capture replan §3.3); fallback ZWO ASI678MM ₹62,145 (R) | cap (WattCycle end-of-life modules) | bench test ~W2; first EL night W3-4 (18 Nov-1 Dec, S) | 0.80 | **#2** (EL-sooner path) |
| 25 | T14 | Hot-spot labels → crack-mode (A vs B/C) head for severity | 0/1/2/2 = 5 | 0.25 | 1.25 | 3 / 3 / 0 / 0 | pub: A1 / A2 | ~1.5 weeks | 0.72 |  |
| 26 | T33 | Multi-current EL (A1 bias sweep) to split resistive from recombination darkness | 1/1/0/1 = 3 | 0.30 | 0.90 | 2 / 0 / 0 / 0 | pub: A1 6-level sweep ≈ 84 MB per module, 10 modules ≈ 0.84 GB (R, check S-10); a later EL session gets 2 currents free | 2 d | 0.64 | (#2 gets the data) |
| 27 | X7 | Reference EL + STC I-V on 3-5 modules at NISE Gurugram (lab-grade check on X6, plus power data) | 0/1/1/1 = 3 | 0.30 | 0.90 | 1 / 0 / shipping / EL fee not public; STC ₹4,550 per field module (R, snippet; capture replan §3.2 E) | cap (shipped modules) | turnaround unconfirmed | 0.64 | #2 (optional, parallel) |
| 28 | T17 | Physics EL → thermal simulator (min. detectable inactive area; synthetic pairs) | 0/1/1/2 = 4 | 0.40 | 1.60 | 5-8 / 0 / 0 / 0 | none | ~1.5 weeks | 0.63 |  |
| 29 | W04 | Public-trained drone-IR anomaly model applied to WattCycle flights | 0/0/3/1 = 4 | 0.30 | 1.20 | 4 / 0-3 / 0 / 1 h | A3 (approved); D1 / PVF-10 / D2 / D11 (D11 about 19 GB, the closest Indian-plant match) need a download OK (not approved); WattCycle IR | ~2 weeks | 0.60 |  |
| 30 | **X1** | Scuff arbiter: on captured half-cut modules, an EL streak with a UVF line is a crack, with no UVF line and no RGB mark it is a scuff candidate; thermal tags the streaks that isolate area | 3/1/1/3 = 8 | 0.15 | 1.20 | 3 / 0 / 1 / within X6's kit; needs EL: X6 within ~3-4 weeks (S), or WattCycle's rig in 2-3 months (Om) | cap: 5-6 modules (P0) | capture day + 3 d | 0.60 | #2 if X6 passes its bench test (was #2) |
| 31 | W12 | RGB (drone or phone): snail trails and surface streaks (X1's RGB arm, T34) | 1/0/1/1 = 3 | 0.30 | 0.90 | 2 / 0 / 0.5 / 0 | WattCycle RGB if any (Om: thermal only), or a phone | visit day + 2 d | 0.57 | #2 (visit add-on) |
| 32 | W06 | Repeat flights: test-retest noise floor and change detection | 0/0/2/1 = 3 | 0.35 | 1.05 | 3 / 0 / 1 extra flight / 0 | WattCycle repeat IR | visit day + 2 d | 0.52 |  |
| 33 | W09 | Shading test: field reverse-bias thermography with no supply, on sacrificial modules only | 0/0/1/1 = 2 | 0.40 | 0.80 | 2 / 0 / 0.5 / 0; safety (ideas W09) | WattCycle camera + sacrificial modules | visit day + 1 d | 0.51 |  |
| 34 | T21 | Inactive-strength augmentation (sampled darkness behind cracks); EL-only | 1/2/0/1 = 4 | 0.15 | 0.60 | 2 / 11 / 0 / 0 | none | 1 d CPU check | 0.42 |  |
| 35 | T20 | Connectivity-consistent inactive in synthetic half-cuts (HC follow-up; HC route open, E: doc 21 §4) | 2/2/0/1 = 5 | 0.15 | 0.75 | 4 / 11 / 0 / 0 | none | 1-2 d CPU check | 0.38 |  |
| 36 | T07 | Thermal teacher → EL student, cell-level consequence score | 0/1/1/1 = 3 | 0.25 | 0.75 | 4 / 11 / 0 / 0 | pub | ~2 weeks | 0.38 |  |
| 37 | T13 | Thermal + dark-I-V agreement filter on pseudo-labels (new-domain pool) | 1/2/0/1 = 4 | 0.15 | 0.60 | 3 / 11 / 0 / 0; 0.5 h | pub | ~2 weeks | 0.35 |  |
| 38 | T18 | Learned EL → IR translation for rare-defect IR training | 0/0/2/1 = 3 | 0.20 | 0.60 | 4 / 6 / 0 / 0 | pub | ~1.5 weeks | 0.30 |  |
| 39 | T06 | Auxiliary thermal-prediction head, train-time only | 1/1/0/1 = 3 | 0.15 | 0.45 | 3 / 11 / 0 / 0 | pub | ~2 weeks | 0.26 |  |
| 40 | T38 | UCF-EL ↔ FSEC IR / UVF module link. 201 of 373 UCF-EL modules are 60-cell, so not A1; 109 partial ones could be 36-cell, so the link is not excluded (E, check E-2) | 1/1/0/1 = 3 | 0.10 | 0.30 | 1-2 / 0 / 0 / 0 | pub (D2 / D3 subset) | 2 d | 0.24 |  |
| 41 | T04 | Missing-modality training (enabler for any fusion) | 0/1/1/1 = 3 | 0.15 | 0.45 | 4 / 11 / 0 / 0 | pub | ~2 weeks | 0.22 |  |
| 42 | T05 | Multi-condition thermal fingerprint (forward / sunlit / reverse) to type EL-dark regions | 1/1/1/2 = 5 | 0.10 | 0.50 | 5 / 3 / 3-5 / P1 kit | cap (P1) | after P1 | 0.17 | (light version in X1) |
| 43 | T16 | Thermal-disagreement active learning and label QA | 1/1/1/1 = 4 | 0.10 | 0.40 | 2 / 1 / shared / 0; 1.5-3 h labels | cap | after capture | 0.16 |  |
| 44 | T24 | Test-time per-cell bias from thermal on a new site | 1/2/2/1 = 6 | 0.05 | 0.30 | 2 / 0 / shared / 0; needs masks | cap | after capture + masks | 0.12 |  |
| 45 | T25 | Temperature-normalised field EL | 1/0/1/0 = 2 | 0.10 | 0.20 | 2 / 0 / 1 / 0 | cap | after capture | 0.12 |  |
| 46 | T36 | Reverse-bias thermography for shunts / hot-spot-prone cells | 0/0/1/1 = 2 | 0.10 | 0.20 | 2 / 3 / 1-2 / P1; safety (capture §7) | cap (P1) | after P1 | 0.11 |  |
| 47 | W14 | Natural-transient thermography (cloud passages, morning warm-up) | 0/1/0/1 = 2 | 0.10 | 0.20 | 3 / 0 / 0.5 / 0 | WattCycle IR video | visit day + 3 d | 0.11 |  |
| 48 | T09 | Contrastive EL-thermal pretraining (CMC) | 1/1/0/1 = 3 | 0.07 | 0.21 | 5 / 20-30 / 0 / 0 | pub (much of A1) | ~2 weeks | 0.09 |  |
| 49 | T28 | IR + EL time series (crack-to-inactive progression) | 0/1/2/1 = 4 | 0.05 | 0.20 | 3 / 0 / 2+ visits / 0 | cap (repeat visits) | after 2 visits | 0.09 |  |
| 50 | T35 | Ultrasound lock-in thermography as crack-only truth | 2/0/0/2 = 4 | 0.05 | 0.20 | 2 / 0 / 2-5 / lab access | cap (lab) | unknown | 0.09 |  |
| 51 | T01 | Early fusion: EL + registered IR as input channels | 0/2/1/1 = 4 | 0.05 | 0.20 | 4 / 11 / 3-5 / P1; 2-6 h masks | cap | > 4 weeks | 0.07 |  |
| 52 | T10 | Cross-modal masked autoencoding (EL → IR) | 1/1/0/1 = 3 | 0.05 | 0.15 | 6 / 25-40 / 0 / 0 | pub | ~2 weeks | 0.06 |  |
| 53 | T23 | Thermal as a domain-invariant anchor (DADA-style) | 1/0/0/1 = 2 | 0.05 | 0.10 | 5 / 15 / 0 / 0 | pub | ~2 weeks | 0.04 |  |
| 54 | X5 | NREL half-cut PL pool for the half-cut context | 1/0/0/0 = 1 | 0.05 | 0.05 | 2 / ? / 0 / 0 | pub, but the DuraMAT hub returned 404 on 4 Nov (R) | n/a | 0.04 |  |
| 55 | T30 | Inline EL + thermography → local loss maps (factory) | 0/0/1/1 = 2 | 0.03 | 0.06 | 8 / 10 / n/a | cap (factory) | n/a | 0.02 |  |
| 56 | T03 | Guided fusion (low-res IR modulates the decoder) | 0/1/0/1 = 2 | 0.03 | 0.06 | 6 / 15 / 3-5 / P1 | cap | > 5 weeks | 0.02 |  |
| 57 | T40 | Thermal-only pretraining of the EL encoder (PVF-10 etc.) | 1/0/0/0 = 1 | 0.03 | 0.03 | 3 / 10 / 0 / 0 | pub (D1 / D4) | ~1 week | 0.02 |  |
| 58 | T11 | Thermal-privileged hard-pixel weighting | 0/1/0/0 = 1 | 0.03 | 0.03 | 3 / 11 / 3-5 / P1 | cap | > 5 weeks | 0.01 |  |

## 4. Why the order looks like this (S)

- **Top band (rows 1-7): cheap, CPU-only, or one capture day. Each gives a measured answer even if it "fails".**
  - T26 leads: high P, because A3 already pairs drone IR with EL on modules with induced cracks and disconnections (R).
  - Either T26 outcome is a thesis result for the part 3 (deployment) chapter: "IR catches inactive / disconnection, misses isolated-nothing cracks", or the reverse.
  - T37, T15, T27 and T02 reuse T26's registration code and download.
  - A1 has bias-matched EL + dark forward-bias IR on about 157 modules (R: OSF listing, check D-5), and about 215 public modules have EL + IR (A1 157, A2 15, A3 43; check D-24). So the A1 rows rest on about 10 times more paired IR than the first reading implied (check §6). That raised P for T37 (0.60 → 0.65), T12 (0.20 → 0.25), T08 (0.30 → 0.35) and T07 (0.20 → 0.25).
  - X3 (Polenghi) rose (now rank 9): its abrasion / scrape stages are a public scuff probe (check D-19), so UR went 0 → 1.
- **Om's decision (4 Nov) moved pick 2.** WattCycle has drone thermal only, and its EL rig is 2-3 months away (`om_2026-11-04_decisions.md`). So every row that needs WattCycle EL lost P:
  - X1 and X2 fell first to 0.10. Capture's low-cost EL path (X6: Pi HQ camera, about ₹25k, first EL night W3-4 if a bench test passes) brings them back to 0.15 / 0.20. X6 itself is P 0.40, because the Si sensor's sensitivity near 1,150 nm is unconfirmed and the bench test decides (capture replan §3.1);
  - T01, T05, T16, T24, T25 and T36 also fell.
- X1 is still the only row with UR = 3. It returns within the thesis only if X6 passes; otherwise it waits for WattCycle's rig in 2-3 months.
- **The drone-only rows now beat X1 and take pick 2:**
  - W03 (rank 4) and W02 (rank 6) give a measured fleet readout from one flight;
  - W01 (rank 7) freezes the EL queue and its predictions before EL exists, so the first WattCycle EL session becomes a test nobody tuned on (S);
  - W11 (rank 10) and W08 (rank 12) give physics labels on end-of-life modules without an EL rig: UVF crack lines, and inactive candidates from IR under load vs open circuit.
- Honest limit (S): the drone rows serve deployment more than E1 crack recall. W11 is the only one with UR 2, through UVF crack lines on aged modules; the crack vs scuff split itself needs EL.
- **Middle band (rows 8-29): sound ideas that need G0 or a WattCycle visit first, or add little alone.** T12 (inactive mixed supervision) has the highest IN value but low P. E1 and test inactive are 3-image readouts (E). A1's losses are mainly resistive, from rear-contact Ag / solder corrosion (R: Colvin et al. 2023, doi:10.1109/jphotov.2023.3238278, the csr6t paper, via check D-6). Whether A1 holds cracks at all is not stated in the abstracts (S, check D-9). So the number of A1 inactive cells is the first risk.
- **Lower band (rows 20-56):**
  - capture-heavy fusion (T01, T03, T11): needs P1 data plus masks inside 7 weeks;
  - pretraining (T09, T10, T23, T40): weak record (E: A8 KILL, MIM n.d., P15 null);
  - P1 extras (T05, T36, T35): equipment or safety gates.
  - **Not killed.** T05 lives on inside X1 as one sunlit IR frame per module; W08 is its no-supply sunlit cousin. Fusion can come back if WattCycle's EL rig arrives and P1 runs.

## 5. Open facts that could move rows (for check / owners)
- **A1 IR format (resolved; datascout reply, check D-3 / D-5).** 473 files: 157 colour `<serial>_cropped.jpg`, 157 `<serial>_cropped.txt` and 159 raw `<date>_SHELL_M55_<serial>_180s_3.393A.txt` (537,840 B). The IR is forward bias at ≈ 1 × Isc, 180 s after current on, with EL at the same 3.393 A in each module's 6-level NEF sweep (R: OSF listing). The IR folder is 0.26 GB.
  - Because this removes the palette-inversion risk, P was raised for T02 (0.30 → 0.35) and T27 (0.35 → 0.40) in v1.1.
  - Caveat: 180 s, not Li 2024's 10 min stabilisation (check D-5). Heat has had less time to build contrast (S).
  - A2 has 15 modules in 16 captures at 5.289 A / 60 s, all with EL at the same current (R, check D-13).
- **Cracks and inactive cells in A1.** Losses are mainly resistive (R: Colvin 2023). Few inactive cells would cut P for T02, T12 and T27.
- **T38.** The UCF-EL cell count no longer rules out A1. 109 of 373 modules are partial, with a highest cell position ≤ 36 (E, check E-2). P raised 0.05 → 0.10; still low.
- **E-PF inference on new EL.** PF2E already runs E-PF on gaint CPU fp32 (E: `handbook/14` l.419). Using it on public EL needs Om's OK and a choice of machine. Without it, G0 and T26 start on a fixed EL dark-area threshold.
- **WattCycle identity and kit** (capture §1.1, §11). This decides P for X1, X2 and all capture rows.
  - Check found that the site calls Atlas "a comprehensive solar asset management platform", so the handbook wording fits this company (R, check C-5). The contact still needs Om. Caveat: the site's Atlas runs on demo seed data, so it does not show that real drone IR archives exist (check C-5).
  - Lock-in partner lead for P2: IIT Bombay, Rajesh Gupta's group (module EL + DLIT; R, check P-12).
  - Supply: capture's fallback is the 300 W OWON (1-5 day shipping; R, not re-verified, check S-21) or biasing one substring at a time (capture §5.1).
  - Whether WattCycle has an EL rig is the biggest unknown for the P0 date (capture reply).
- **WattCycle drone facts (capture replan §7).** Still unconfirmed:
  - the drone and camera model;
  - whether raw radiometric R-JPEGs are kept rather than only palette JPEGs;
  - whether the drone has RGB.
  - W03 / W05 / W06 need radiometric data; without it, P for those rows drops.
- **Drone IR physics, sharpened (R: DTU slides via capture replan §2.1).** Cracked cells differ by about 1 °C at most and become unidentifiable below 600 W/m2. Disconnections are identifiable from 600 W/m2, and the worst type exceeds 3 °C. Diodes and soiling show more than 10 °C even at 200 W/m2. This supports triage rows (W01-W03, T26), not crack labels.
- **X6 sensor.** The near-IR sensitivity of the IMX477 / IMX678 at 1,100-1,200 nm is unconfirmed. The week-2 bench test is X6's gate. The pre-stated success: cracks and inactive regions visible at ≤ 120 s per frame after stacking (capture replan §3.3).
- **A3 class sizes (check pass 3, R: DTU slides).**
  - Cracks: 8 mono PERC modules, 69 cracked cells. Interconnections: 8 modules, 98 cells.
  - Half-cut bifacial PERC modules sit only in the diode, glass-crack and soiling groups.
  - T26's per-class AUROC therefore rests on about 8 positives per class (S). The module ranking uses all 43. T26's P (0.55) is kept, because the expected disconnection signal is large (R), but its intervals will be wide.
- **PID (check DO-1).** Drone IR showed no pronounced PID anomaly in A3 (ΔTmax 2 °C vs 1.5 °C healthy; R). No row here relies on drone IR seeing PID.
