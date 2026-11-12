# 22. Thermal (IR) imaging for our EL segmentation: the desk study, the public pairs, pick 1 G0 and pick 3 (4 Nov 2026; state 12 Nov)

## What this covers
This file explains, from zero, the thermal (infrared, IR) work of 4 Nov 2026, run by the agent team in `team_2026-11-04_thermal/` after a brief from Om. It is written for the guide agent: the user had not seen most of it when the session ended.
- **Why thermal** (§1), and the **physics** of thermal vs EL for our classes (§2).
- **The public datasets** that pair EL and IR on the same modules (§3).
- **The ideas** (40 + 14), the ranking and the **top 3** (§4, §5), and the WattCycle capture plan and its re-plan (§6).
- **Om's decisions** and the downloads (§7).
- **Results so far:** pick 1's G0 (does dark IR flag EL-dark cells?) and pick 3's A1 arm (T15, T37), stopped at T37 (§8, §9).
- **Lessons** (§10), **what is not done** and how to resume (§11), incidents (§12).

It also notes (§13) that SKR2C (doc 21 §10) finished training on 3 Nov and is not opened.

Added 12 Nov 2026. **Tags.** E = measured in our files (path given), R = from a source (paper, dataset page, API; as the team cited it), S = judgement. **Verdicts are the pre-registered ones; readings are labelled "Reading".** The thermal agents tagged every claim; this file keeps their tags.

**Status at writing (12 Nov 2026; the 4 Nov session ended ~13:50 IST)**

| Item | Verdict / state | Where |
|---|---|---|
| Desk study (datasets, ideas, capture, ranking, fact-check) | done; SUMMARY final for Om | `synth/SUMMARY.md`, `check/factcheck.md` |
| Om's decisions (4 Nov) | downloads approved (picks 1 + 3); pick 2 re-planned; 3 items open | `om_2026-11-04_decisions.md` |
| Downloads A1 / A2 / A3 | verified twice on 4 Nov; re-verified 12 Nov (0 failures) | `datasets/download_verified.md`; session record §7 |
| Pick 1 G0 v1 (dark IR) | A2 between, A1 null, pooled between: **not a go, not a kill** | `pick1/out/G0.md` |
| Pick 1 G0 v2 (post hoc instrument fix) | same as v1 | `pick1/out/G0v2.md` |
| Pick 1 A3 readouts (R1, R2, R3b) | **not run** (A3 discovery only) | `pick1/plan_pick1.md` Amendment 6 |
| Pick 3 T15 (A1 dark I-V label) | **PASS, narrow** | `pick3/out/PICK3_A1_REPORT.md` |
| Pick 3 T37 (A1 registration) | v1 PASS at the line; v2 **FAIL**; arm stopped (team-lead option A) | same |
| Pick 3b (A3 power-loss labels) | plan frozen; discovery done; **no statistic computed** | `pick3/plan_pick3b_v1_FROZEN_eaec6f26.md` |
| ADDENDUM to SUMMARY | **DRAFT** | `synth/ADDENDUM_2026-11-04.md` |
| Report to the user and Om | **not sent** | team-lead's end-state line (log, 12 Nov) |

## Sources
- `SESSION_RECORD_2026-11-03_to_11-04.md` (master for this file; §4-12).
- `team_2026-11-04_thermal/`: `README.md`, `om_2026-11-04_thermal.md`, `om_2026-11-04_decisions.md`, `log.md`; `datasets/` (`dataset_table.md`, `notes.md`, `download_plan.md`, `download_verified.md`); `ideas/` (`ideas_long.md`, `drone_only.md`); `capture/` (`capture_plan.md`, `replan_pick2.md`); `synth/` (`ranked_ideas.md`, `top3.md`, `SUMMARY.md`, `ADDENDUM_2026-11-04.md`); `check/factcheck.md` (§1-37); `pick1/` (`plan_pick1.md`, `out/G0.md`, `out/G0v2.md`); `pick3/` (`plan_pick3*.md`, `plan_pick3_notes.md`, `plan_pick3b*.md`, `out/PICK3_A1_REPORT.md`); `scripts/frozen/`.
- Copies of the markdown files: `sources/teams/team_2026-11-04_thermal/`; the session record: `sources/session_records/`.

Where a session record and a result file disagree, the result file is used.

---

## 0. Terms used here
- **EL (electroluminescence):** current is driven forward through the module in the dark; healthy silicon glows; isolated (inactive) areas, recombination-active defects and metal stay dark (doc 02). Our whole project segments EL images.
- **IR thermography:** a thermal camera images the front-glass temperature: where electrical or optical power turns into heat, blurred by heat spreading (S, ideas §0).
  - **Dark forward-bias IR:** the module is driven like EL (current in, no light) and the IR camera images the heat. A1 and A2 used this.
  - **Sunlit (drone) IR:** the module works in sunlight and a drone images it. A3 used this.
  - **Lock-in thermography:** a pulsed current and averaging give finer and more sensitive images (R). No public set here has it.
- **PL (photoluminescence)** and **UVF (UV fluorescence):** two other optical modalities. PL needs no electrical contact, so isolated regions still emit; UVF shows crack lines in aged encapsulant (R, ideas §0).
- **ΔT:** a cell's median temperature minus the module median of cell medians (°C). Under forward bias the prediction for an inactive cell is cooler (negative ΔT); in sunlight, warmer (S, device physics).
- **EL dark fraction:** the share of a cell's inner pixels below 0.5 × the module median, after a small morphological opening; a cell is "EL-dark" (a candidate inactive cell) if it is ≥ 5%. An EL-only stand-in for E-PF's inactive prediction, because E-PF inference was held (§7).
- **AUROC (cooler):** how well −ΔT ranks EL-dark cells above the others (0.5 = chance, 1 = perfect). **Spearman ρ:** rank correlation of ΔT with the dark fraction.
- **G0:** the shared gate "is there a thermal signal at cell level?". Go if AUROC ≥ 0.8 with the predicted sign; the fusion / weak-label idea families are killed only if |ρ| < 0.3 and AUROC < 0.7 in **both** dark and sunlit conditions.
- **Registration:** mapping each IR cell to its EL cell. The team's tool `cellreg.py` finds the module outline (Otsu threshold), fits a cell grid, and reports the residual as % of a cell side. **Orientation:** a regular grid looks the same flipped or rotated, so which IR cell is which EL cell needs outside evidence.
- **Row / column-centred ΔT:** ΔT minus the median of its row, then of its column, within a module. If a signal survives this, it is cell-level; if it vanishes, it was row or edge structure.
- **V_t:** the thermal voltage, ~25.7 mV at room temperature; T15's spread bar is 0.1 V_t = 2.57 mV.
- **E-PF:** the 5-member PF ensemble at argmax, the recommended deployable candidate (doc 21 §5; adoption is the user's call).

---

## 1. Why thermal?
- **The open problem (E, doc 11 / doc 18):** on unseen modules (E1, 106 cells) crack recall is ~0.2, and 75% of missed crack pixels sit in half-cut cells with scuff streaks, a context training lacks. No method so far has fixed it (doc 21).
- **Om's direction (3 Nov, `om_2026-11-04_thermal.md`, verbatim):** launch optimistic, generative agents on thermal imaging, with three questions: (1) public paired EL + thermal data (also EL + PL / UVF / RGB); (2) every way thermal could help our EL segmentation, including the industrial pipeline "drone IR for screening, EL for detail"; (3) whether WattCycle or IIT Mandi could capture paired EL + thermal on a few modules.
- **The partner angle:** WattCycle Sustainable Solutions (an IIT Mandi PV-recycling startup; R, capture §1.1) offers drone thermal inspections. Om confirmed on 4 Nov that it has only a drone thermal setup now; its EL rig is 2-3 months away.
- **Rules of the study (README):** desk study first (pages, metadata and abstracts; no downloads), no GPU, no server access, no outside contact, no test or E1 reads, no manual labelling asks, tag every claim.

## 2. The physics: what thermal shows vs EL, for our classes
EL shows where current reaches silicon and recombines radiatively; thermal shows where power becomes heat. That splits our classes (ideas §0 and §0.1; tags as given):

| Our class | EL | Dark forward-bias IR | Sunlit (drone) IR | Better second modality |
|---|---|---|---|---|
| Crack that isolates nothing (Köntges mode A, S mapping) | thin dark line | none expected (S) | no hot spot (R: Dhimish 2021, 2022); cracked modules "difficult to distinguish from healthy ones", ≤ ~1 °C (R: DTU, EPJ PV 2025) | UVF crack lines (R) |
| Inactive area (crack-isolated, modes B / C) | dark region bounded by cracks | cooler region (S) | warmer region (S); temperature rose from 25 °C to 100 °C for larger crack modes and up to 105 °C at 40-60% shading (R: Dhimish 2021 abstract) | PL: EL-dark but PL-bright marks isolated area (S; daylight PL "promising", R) |
| Scuff (E-SCDD class 25, not in our 24) | long dark streak | unknown; silent if surface-only (S) | unknown | UVF / RGB / PL decide what scuff is (S) |
| Shunt / PID | dark cell or spots | hot spot (R) | warm cell; PID hot spots near 50 °C (R) | |
| Solder / ribbon failure | darker region | point-like heating at joints (R) | warm joint (S) | |
| Interconnect disconnection (A3) | dark region | | visible from 600 W/m² (R: DTU) | |

- **Calibration (R, JRC 2017 via check):** dark IR gives "few local information"; illuminated IR separates damage classes in line with EL. So a weak dark-IR result is expected and is not a reason to drop illuminated IR.
- **Resolution (R):** drone IR at ≤ 3 cm/px gives ~5-16+ pixels across a 156 mm cell, so it is a cell-level signal; our EL crops are 512 × 512 per cell neighbourhood (doc 02).
- **Net (S, ideas and synth):** thermal is a strong cell-level signal for inactive area, hot spots and severity, and a weak or null pixel-level signal for cracks and scuff. It sees **electrical consequence, not crack lines**. So it can help as a training-time teacher, a weak label, a triage stage or a severity output, not as a crack-pixel input. And since BenchmarkEL, test and E1 have no thermal (E), any gain on our benchmarks must come from an EL-only model trained with paired data.

## 3. The datasets (`datasets/dataset_table.md`; check pass 1)
**No public set gives pixel-registered EL + thermal at cell level with crack or inactive masks** (S, after datascout's sweep). Three open sets, all **CC BY 4.0**, give EL and IR of the **same physical modules** (module-level pairing; cells must be aligned by the team's own registration):

| Set | What | Modules | IR | EL | Extras | Size |
|---|---|---|---|---|---|---|
| **A1** OSF `csr6t` (UCF; Colvin et al., IEEE JPV 2023) | 10-year Florida rooftop, Shell M55 mono Al-BSF, 36 cells in **3 × 12** (E) | 156 characterised; IR for 157 | dark forward-bias at 3.39 A (~1 × Isc), 180 s by file names (the paper says 5 min), 240 × 320 °C matrices (E); camera ICI 8320P | Nikon D5100 + 950 nm long-pass, 6 currents | UVF, I-V, **EL-derived per-cell dark I-V** (158 files) | EL 14.95 GB; IR 0.26 GB; UVF 2.01 GB |
| **A2** OSF `ar76v` (UCF) | 19-year convention-centre array, SolarWorld mono, 72 cells 6 × 12 (E) | 42; IR for 15 (camera failed) | dark forward-bias at 5.289 A, 60 s (16 captures) | 6 currents (NEF) | UVF, I-V | EL 3.82 GB; IR 0.02 GB |
| **A3** DTU figshare 29665346 (EPJ PV 2025) | artificially degraded modules: cracks 8, interconnects 8, PID 6, bypass diode 7, glass 2, soiling 6 + 6 | 43 (31 degraded + 12 soiled) | **drone** (DJI Mavic 3T), 8 / 10 / 14 / 20 m, 200 to > 800 W/m², arrays 605 × 363 °C, rows × cols, portrait (E; the README's "363x605" is width × height of the same array) | one NEF per degraded module, 2-6 s exposures (E) | STC I-V (V, I only; E) | 642.6 MB archive |

- Facts to remember: A1 and A2 are old **full-cell mono** modules (no half-cuts, no scuff); A1's losses are "primarily resistive" (R, Colvin 2023), so it is a series-resistance set more than an inactive set. A3 has half-cut bifacial PERC modules only in its diode, glass and soiling groups, **none with a crack** (R, DTU slides). No set is known to show scuff.
- About **215 public modules have IR** (A1 157, A2 15, A3 43); about 203 have both EL and IR, since A3's 12 soiled modules have IR but no EL. Enough for a feasibility study of cross-modal weak labels and a demo pipeline, not for training a fusion model at scale (S).
- Other rows (R): 5 EL + PL rows (B1-B5, e.g. 856 NREL half-cut PL images), 4 EL + visible / NIR rows (only C1, Polenghi et al., 84 pixel-aligned damage stages with power, pairs the same cell; its abrasion / scrape stages are a public scuff probe, S), 12 thermal-only labelled sets (D1-D12, e.g. Raptor Maps 20,000 crops, MIT), 12 in-paper sets not released (E1-E12).
- **Where they live (E):** only A1 (subset), A2 (subset) and A3 were downloaded, to `~/mtp/datasets/thermal_public/` (doc 03 §13).

## 4. The ideas (`ideas/ideas_long.md`, 40 ideas; `ideas/drone_only.md`, 14 ideas)
- **40 ideas T01-T40 in 8 families:** fusion of EL + thermal (T01-T05); cross-modal pretraining and distillation, e.g. a thermal teacher for an EL student (T06-T11); thermal and physics as weak labels (T12-T16, e.g. **T15** A1's per-cell dark I-V as a label, **T12** thermal cell flags as inactive labels); EL ↔ thermal synthesis (T17-T21); thermal for unseen-panel generalisation, incl. **T22** the "thermal silence" test for scuff (T22-T25); the industrial pipeline, incl. **T26** IR screening → targeted EL and **T27** a hot-spot risk score (T26-T30); other modalities, incl. **T31** EL / PL contrast for inactive masks and **T32** UVF crack lines vs scuff (T31-T36); data and evaluation, incl. **T37** a registered A1 cell-level EL + IR + UVF set as a release (T37-T40).
- **14 drone-only ideas W01-W14** (after Om's decision), for what WattCycle can do with drone thermal alone: an IR-ranked EL queue with pre-registered predictions (W01), a module ID map with a half-cut survey (W02), a physics-rule baseline (W03), operating-point differential IR on ground modules (W08), UV-torch UVF at night (W11), and others.
- **Honest limits (ideas §3):** no direct fix for the scuff + half-cut crack gap; no gain on test or E1 from thermal inputs; pretraining starts with a weak record here (A8 KILL, MIM n.d., P15 null; docs 19-21); cell-level, not pixel-level.

## 5. Ranking and the top 3 (`synth/ranked_ideas.md`, `top3.md`, `SUMMARY.md`)
- synth merged the lists (plus X1-X7 from datascout and capture, e.g. X1 a scuff arbiter on captured half-cut modules, X6 a low-cost Pi camera for EL) into **58 rows** (38 T, with T22 / T34 merged into X1; 7 X; 13 W, with W07 merged into T19) and scored each by value × probability / √effort (**all scores are S**). Top 10: T26, T37, T15, W03, T27, W02, W01, T02, X3, W11.
- **Top 3 (S picks, chosen to spread risk):**
  1. **Pick 1, "what thermal catches":** IR screening vs EL on A3 / A2 / A1 (T26 + G0 + T27 + T39); public data, CPU only; for the deployment chapter. Kill if the top 20% IR-ranked modules hold ≤ 20% of the EL dark area, or G0 is null in both conditions.
  2. **Pick 2, WattCycle drone thermal now, low-cost EL soon** (W02, W03, W01, W08, W11; then X6 → X1 / X2); a visit day and a night; ~₹27k-30k of kit.
  3. **Pick 3, inactive from physics labels:** T15 → T02 → T12, with T37 as an output; GPU (~5.5 GPU-h) only if gated.
- **Fact-check (check, `factcheck.md`):** pass 1 on datasets / ideas / capture: 110 items, OK 73, FIX 31, UNVERIFIABLE 6 (most FIXes made the picture better; e.g. A1's IR turned out to be bias-matched forward-bias IR on ~157 modules). Pass 2 on synth: 33 items, OK 13, FIX 18, UNVERIFIABLE 2. All fixes applied before the SUMMARY was final.

## 6. WattCycle capture: the plan and the re-plan (`capture/capture_plan.md`, `replan_pick2.md`)
- **Original P0 (S):** one day, 5-6 recycler modules (≥ 2 half-cut, ≥ 2 with scuff-like streaks); EL at 0.1 and 1.0 × Isc, dark IR under the same bias, UVF, RGB; aluminium-tape fiducials and a homography for cell alignment; ~₹45k-55k of kit if an EL rig exists; no hand labels. The point: an EL-dark streak with no thermal or UVF signature is a scuff candidate, while EL-dark plus a thermal anomaly is a crack or inactive candidate.
- **Re-plan after Om's decision (no EL rig for 2-3 months):** drone IR is a **triage and pairing** tool, not a crack labeller (R: DTU 2025: cracks ≤ ~1 °C; interconnect breaks visible from 600 W/m²; diodes and soiling > 10 °C even at 200 W/m²). Now: a fixed flight protocol, a module ID map and half-cut survey, physics-rule scores calibrated on A3, a frozen pre-registered list of modules for the first EL session, ground tests on end-of-life modules. EL sooner (S): a Raspberry Pi HQ camera with its IR-cut filter removed, plus a 300 W supply, ~₹25k plus lens and filter (Si sensitivity near 1,150 nm unconfirmed); fallback camera ₹62k; NISE Gurugram per-module EL. Drone EL needs a SWIR camera (~€10k-15k): no.
- **Questions:** Q1-Q20 for WattCycle and IIT Mandi, U1-U3 for dataset authors (`SUMMARY.md` §4). **Not sent** (no outside contact; the report to Om was not sent).

## 7. Om's decisions and the downloads
- **Om (4 Nov, verbatim file):** (1) downloads approved for picks 1 and 3 (A3, the A2 subset, the A1 subset with dark I-V; ~1.2 GB; CPU only; the 0.55 GB A1 extension still needs his OK); (2) WattCycle has drone thermal only, so re-plan pick 2; (3) still open for Om: **E-PF inference location** (gaint CPU vs local), **licences / release**, **capture funding**. Because of (3), E-PF was not run: picks 1 and 3 used the EL dark fraction instead.
- **Downloads (E):** A1 209 files (all 159 dark I-V files + 10 modules chosen by a frozen, seeded, severity-stratified rule), 286,886,436 B; A2 47 files (all IR + one bias-matched EL per IR module), 237,009,189 B; A3 7z (642,610,942 B) + README, extracted to 1,414 files. All verified against the publishers' hashes by datascout and independently by check; re-verified 12 Nov. Details: doc 03 §13; session record §7.

## 8. Pick 1 results: does dark forward-bias IR flag EL-dark cells? (G0)
**Plan** (`pick1/plan_pick1.md`, frozen before any number; Amendments 1-6, each frozen before the numbers it governs). Orientation of IR vs EL was fixed from non-outcome evidence: the authors' own A1 IR crop is the raw IR rotated 180°, so the primary is rot180 for A1, and for A2 by the same lab and rig (S); the other 3 orientations are reported.

**G0 v1 (frozen; `pick1/out/G0.md`; recomputed by check from raw files: MATCH)**
| Set | Modules kept | Cells / EL-dark | ρ | AUROC (cooler) | Verdict |
|---|---|---|---|---|---|
| A2 | 9 / 15 | 648 / 230 | −0.550 | 0.736 | between (predicted sign, below the 0.8 go bar) |
| A1 | 7 / 10 | 252 / 50 | −0.285 | 0.689 | null |
| Pooled | 16 | 900 / 280 | −0.451 | 0.708 | between |

**G0 v2, post hoc instrument fix (`pick1/out/G0v2.md`; recomputed by check: MATCH):** the frozen reviewed registration tool (cellreg v0.4.1), written visual QA criteria, per-module calls co-signed blind by check before any number.
| Set | Modules | Cells / EL-dark | ρ | AUROC (cooler) | Row/col-centred AUROC (post hoc) | Verdict |
|---|---|---|---|---|---|---|
| A2 | 4 / 15 | 288 / 75 | −0.515 | 0.732 | 0.525 | between |
| A1 | 4 / 10 | 144 / 36 | −0.246 | 0.621 | 0.343 | null |
| Pooled | 8 | 432 / 111 | −0.403 | 0.687 | | between |

- **Verdict (both versions): not a go, not a kill.** Because the dark condition is not null overall, G0 cannot be killed by A3 whatever A3 shows (check §22).
- **The post hoc row / column finding (check, first computed after the v1 readout):** removing each module's row and column medians takes AUROC to ~0.5 (v1: A2 0.49-0.52, A1 0.52-0.57; v2: A2 0.525). Reading (S): the dark-IR signal is **row / edge-level, not cell-level**: real string or edge degradation, or shared artefacts (convection, frame heat-sinking, vignetting); these data cannot tell which.
- **Reading (S, post hoc; A1 after centring):** EL-dark cells read slightly **warmer** than their row and column peers (centred AUROC(cooler) 0.343), the expected sign for series-resistance defects, opposite to the inactive expectation; it fits A1's resistive losses (R). 4 modules, descriptive only. Consistent with Colvin 2023's module-level finding (SD of module temperature vs power-loss rate, R² 0.429; R).
- **Not run:** the sunlit A3 arm (R3b), the A3 screening table (R1, R2) and the E-PF readouts (T27, T39). Only A3's structure was discovered (Amendment 6: the module fills the IR array, so the outline rule for A1 / A2 does not apply; R1 uses the whole array with a 3% inset).

## 9. Pick 3 results: physics labels for inactive (A1 arm)
- **T15 (does A1's EL-derived per-cell voltage make a usable label?):** 158 modules, 5,688 cells, all valid. Per cell, d = module median voltage minus the cell's voltage at the highest current (~3.39 A). Frozen kill: coverage < 50%, or "no spread" = robust SD(d) < 2.57 mV (0.1 V_t) **and** < 1% of cells with d ≥ 1 V_t; the second clause was met by construction (the module maximum, 19.3 mV < 1 V_t, was on record before the read), so the kill rested on the SD clause. Result **3.26 mV → PASS, narrow** (check's recompute matches). The label D90 (d ≥ 4.23 mV) marks 569 cells spread over 144 of 158 modules; no cell reaches 1 V_t. Reading (S): a diffuse, small resistive deficit (~1.18× EL dimming), not inactive area.
- **T37 (can the 10 A1 modules be registered EL ↔ IR at cell level?):** v1: 3 / 10 modules excluded (30%) → **PASS at the line**, but one included module was visibly misregistered at a passing residual. v2 (improved tool, post hoc): 4 / 10 excluded by the frozen rule → **FAIL**.
- **Likely cause (check CR-5; the crop geometry is E, its role in the failure is S):** the authors' A1 IR file `<serial>_cropped.txt` is a **fixed 134 × 35 pixel window**, not the module (the module is ~145 × 37 px), so it trims ~0.9 of a cell; forcing 12 columns into it gave a ~7% pitch error. Any future A1 work must register on the raw IR frame.
- **Label direction (R, Colvin 2023, verified in the full text):** the authors compute each cell's voltage from "a bright pixel from each cell", and "cells with bright spots in high injection EL show higher RS values". So a degraded cell may have a **higher** voltage, and the frozen "lower = worse" rule may be inverted for A1 (S).
- **Decision (A), team-lead ~13:28:** stop the A1 arm at T37 as pre-registered; T02 / T12 never ran. Redirect to **pick3b on A3**: does the EL dark proxy track measured power loss (3b-R1), does drone IR track it and add to EL (3b-R2), and cell-level IR by induced cause (3b-R3, interconnect stratum primary). Plan frozen before extraction (eaec6f26). Discovery: no module type in the release, so the primary label is **FF loss**; one EL per module, so the two-current label (3b-R4) is not run. **No pick3b statistic was computed.**

## 10. Lessons (readings, S unless tagged)
1. **Thermal is an electrical-consequence signal.** Plan thermal work around inactive / disconnected area, hot spots and severity, not around crack lines or scuff. For scuff vs crack, UVF, PL or RGB are better placed (R + S).
2. **Dark IR on the public pairs looks row / module-level, not cell-level** (S, a post hoc reading, check §22 G0-3 and §36; E numbers: row / column-centred AUROC A2 0.49-0.52 in v1 and 0.525 in v2, A1 0.52-0.57 in v1; A1 v2 0.343, EL-dark cells slightly warmer). The sunlit arm (A3) and lock-in IR are the fair tests for cell-level inactive flags; neither has been read.
3. **Know the dataset's physics before using it as a label:** A1 is a series-resistance set; its bright-pixel cell voltage may invert the "degraded" direction (R).
4. **Instruments fail quietly:** a passing residual can hide a drifted grid; an author-made crop is not necessarily the module; tone-mapped NEF previews limit dark fractions (E).
5. **The process mostly held:** every verdict rule was frozen before its numbers; T15 and G0 v1 / v2 were recomputed independently from raw files by check; T37 was checked from the registration outputs, not re-registered, and its v2 rule was post hoc; post hoc changes were labelled and co-signed before outcomes (session record §11).
6. **Deployment value (S, synth):** a screening-recall table by defect mode on A3 is the cheapest sure result for the deployment chapter; drone IR is for triage and pairing, and the first WattCycle EL can be pre-registered as a prospective unseen-module test.

## 11. Not done, open decisions, and how to resume
- **Not done (4 Nov end state):** pick 1 R1 / R2 / R3b on A3; pick3b 3b-R1 / R2 / R3; the ADDENDUM is still a DRAFT (its "running, results to follow" lines for A3 must change before it is sent); **the report to the user and Om was never sent.** The session ended abruptly (§12).
- **Open for Om:** E-PF inference location; licences / release (mixing CC BY sets with BenchmarkEL, which has no licence file; a CC BY derivative release of a registered A1 set); capture funding; the A1 extension; whether to send the WattCycle questions. Pick 2's week plan (W2 = 11-17 Nov) has slipped.
- **How to resume (S, the plans' order):** verify the data (`md5sum -c` of each `MANIFEST.md5`); use only the frozen tools (`scripts/frozen/cellreg_7d9a9fe0.py`, `g0_stats_0190cba5.py`); run pick 1 R1 / R2 under Amendment 6, then R3b with a co-signed visual QA; write the dated pick3b amendment for the IR rule that plan v1 §5 requires (the attempted v1.1 freeze is empty, content unknown; the governing plan is v1 eaec6f26), then 3b-R1 / R2; then finalise the ADDENDUM and send the report. Session record §12.3.

## 12. Incidents (details: session record §11; doc 13 D55 to D60)
- **Abrupt end (~13:51, 4 Nov; cause unknown; before the 12 Nov OS reinstall):** NUL bytes in `pick3/plan_pick3b.md` (v1 plus crash padding: stripped, it hashes to eaec6f26) and in the thermal `log.md` (line 149; use `grep -a`), an empty `plan_pick3b_v1.1_FROZEN_c8f57302.md` (an attempted v1.1 freeze; content lost and unknown), an empty `A3_layout.tsv` (a discovery output). Log lines written after 13:50 may be lost (S). pick3b's governing plan is v1 eaec6f26. No readout file and no frozen copy is affected.
- Hand-typed times ahead of the clock (ideas, datascout, pick 1's plan header; team-lead's 12 Nov retrospective lines; corrected). Self-test criteria for the registration tool set post hoc from synthetic results (disclosed). A results file overwritten with post hoc fields, then the frozen output restored byte-exact. A registration tool version run on real data before its review (registration only); one version announced and withdrawn. One visual-QA miss caught by check. A false premise about the A1 crop (the likely cause above). A scope slip (ideas' G0 step on all 157 A1 IR modules vs the 10 approved) caught by check before any download. The WattCycle identity question (web vs local docs), resolved toward a match by check and confirmed by Om.

## 13. SKR2C, for completeness (doc 21 §10)
SKR2C (SKR2 vs SUP100-PF on fresh seeds 10-14) launched 3 Nov 03:06 and finished training at **11:24:04 on 3 Nov: 10 rc 0 of 10**, with no guard trigger and no HOLD (team-lead's 4 Nov read-only check, logged 12 Nov). Nothing has been scored. **E1 opening #7 is registered, not opened; it needs the user's OK.** Details: session record §2; doc 21 §10.

## Questions to check understanding (for the guide)
1. Why can thermal not fix the E1 scuff + half-cut crack gap directly? (§2: thin cracks and probably scuff are thermally silent; E1 has no thermal.)
2. G0 v2 on A2 has AUROC 0.732 but row/col-centred 0.525. What does that say? (§8: the signal is row / edge-level, not cell-level.)
3. T15 passed. Why did pick 3 still stop? (§9: T37 failed on registration, and the label is a diffuse resistive deficit whose direction may be inverted.)

## Related docs
- `21_a8_hc_b6_skr2_skr2e.md` (SKR2C design, §10); `02_domain_primer_EL_and_defects.md` (EL physics); `03_datasets_and_splits.md` §13 (the public thermal sets on the laptop).
- `11_results_synthesis_and_claims.md` rows 51 to 55; `12_decisions_log.md` D93 to D101; `13_problems_pitfalls_open_issues.md` A19, A20, C24, C25, D55 to D60, E35 to E38; `14_code_and_infrastructure.md` §1.1b, §1.2f, §5e; `15_status_remaining_work.md` §1k, §3f, §4f; `16_faq_for_the_guide.md` section K.
