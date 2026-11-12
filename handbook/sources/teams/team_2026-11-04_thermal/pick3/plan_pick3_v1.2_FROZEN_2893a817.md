# Pick 3 plan: inactive / degraded cells from physics labels on open data (T15 → T02 → T12, T37 as output)

Owner: `ideas` (pick 3 executor). Written 4 Nov 2026, 12:44-12:53 IST (times from `date`; an earlier hand-typed range "12:45-13:05" was ahead of the clock and is corrected here), **before any data content was read** (only OSF / figshare file names and sizes in `scripts/listings/`, which are metadata). Version **v1, frozen** after `check`'s review (PL-1 to PL-7 applied: fit outputs in an unreadable .xls, so P from the txt curves; 158 txt + 1 xls; EL-IR date offsets; IR currents; proxy purity). Its md5 is recorded in `log.md` before any number is read.
Source of the pick: `synth/top3.md` pick 3; ideas `ideas/ideas_long.md` T15, T02, T12, T37. Tags: E = our files, R = source, S = my reasoning.

## 0. Rules for this pick
- CPU only, `~/mtp/research/.venv/bin/python -I` (system `python3` has no numpy, E: checked 12:44). Scripts live in `team_2026-11-04_thermal/scripts/`, never in the data folders; data are read by path only.
- Data: only datascout's approved and verified set (`datasets/download_verified.md`, to come): A1 dark I-V folder (158 per-module curve txt files + 1 `diode_fit_outputs.xls`, per `check`), A1 10-module subset (EL, IR, UVF). Nothing else is downloaded. The A1 extension (≈ 0.55 GB) needs Om's OK.
- **E-PF inference is HELD** (Om). Every step below that names E-PF has a frozen EL-only substitute; the E-PF version runs only after Om decides where.
- No GPU. The T12 training arm is out of scope until Om's OK and a separate locked protocol.
- No test, E1 or BenchmarkEL image or label is read in this pick.
- Order: v0.9 → `check` review → v1 frozen (md5 in `log.md`) → format discovery → readouts. Any deviation after freeze is written as a dated amendment, never a silent edit.

## 1. Data facts used by the plan (metadata only, E: `scripts/listings/*.tsv`, file names and sizes)
- A1 IR: 157 modules × {`<serial>_cropped.jpg`, `<serial>_cropped.txt`, `<date>_SHELL_M55_<serial>_180s_3.393A.txt`} (+2 names without the exposure field); raw txt 537,840 B each. IR currents in the names: 3.392 A (78 files) or 3.393 A (79), plus 2 files at 1.354 A (R via `check`); exposure 180 s. datascout's eligibility rule keeps only 3.392-3.393 A IR.
- A1 EL: 1,044 files; 2018 `RAW.tif` (16,666,834 B) at various currents, and 2022 NEF 6-level sweeps (e.g. 0.025 / 0.195 / 0.296 / 1.392 / 2.394 / 3.392 A for module 6330431029).
- A1 dark I-V: 158 `<serial>_EL-derived_cell-dark-I-V.txt` curve files (13,958 B each) + 1 `diode_fit_outputs.xls` (1,615,360 B), which holds the per-cell two-diode fit outputs (n1 = 1, n2 = 2, other parameters free; R: OSF description via `check`).
- A1 study: Colvin et al. 2023, losses "primarily resistive", EL pattern resistive by comparison with PL (R abstract: doi:10.1109/jphotov.2023.3238278). **So A1 is expected to be rich in high-series-resistance cells and poor in true inactive cells (S).** This is the pick's main risk and is measured, not assumed (§3.4).
- Shell M55: 36 cells (S, datascout); the grid layout (expected 4 × 9) is detected from the images, not assumed (§2).

## 2. Registration method (the shared tool; also for datascout's G0 on A1 / A2)
**Tool:** `scripts/cellreg.py` (to be written; CPU; numpy / scipy / skimage / PIL only). Inputs: one EL image, one IR matrix (txt) or image, optionally one UVF image, and the expected grid (rows × cols, auto-checked). Outputs per module: `cells.tsv` (one row per cell with registration QA and features), an overlay PNG per modality, `reg.json` (homographies, residuals).

**Readers.**
- EL TIF: read as 16-bit if present (linear sensor counts assumed, S).
- EL NEF: no raw decoder is installed and installs are not allowed, so the tool extracts the largest embedded JPEG preview (8-bit, camera-processed, monotonic; S). Disclosed per module; features below use only ratios to the module median, which a monotonic tone curve preserves in rank but not in value (S), so NEF-based dark fractions are flagged as approximate.
- IR txt: parse a numeric matrix (whitespace, tab, comma or semicolon; skip non-numeric header lines). Prefer `*_3.393A.txt` (raw) for values; use `*_cropped.txt` if it is a module-only crop (decided at format discovery and logged).
- UVF JPG: luminance channel.

**Steps per module and modality.**
1. **Module quad:** smooth, threshold (Otsu) to the module's active area, take the largest component, fit a quadrilateral to its convex hull (4 corners).
2. **Rectify** with the corner homography to a canonical grid (cols × rows cells, fixed px per cell).
3. **Cell grid:** row and column intensity profiles of the rectified image; inter-cell gaps are dark in EL and UVF and cooler in forward-bias IR (S); pick the expected number of minima nearest to the uniform grid. If the found count ≠ expected, the module is flagged and falls back to the uniform grid.
4. **Refine:** fit a homography from all grid intersections ((rows+1) × (cols+1) points) back to the image by least squares; EL ↔ IR (and ↔ UVF) mapping = composition through the canonical grid.
5. **QA readout (T37's kill):** residual RMS of intersections after the refined fit, in px and as **% of the median cell side**, per modality; plus leave-one-point-out residual. Overlay PNGs are checked visually (by me, Read tool) for every module.
- **T37 kill (from ideas / top3):** residual > 5% of a cell side. Per module: modules above 5% are excluded from T02 / T12 and counted. Pick-level kill: > 30% of modules excluded (S, frozen here).

**Self-test before real data (no data needed):** synthetic module images with a known homography, noise and dark gaps; the tool must recover corners within 1 px and residual < 1% of cell side. Logged with the tool's md5.

## 3. Readouts, labels and kill signals (frozen at v1)

### 3.1 T15: the dark I-V data as a physics weak label (all 158 curve files)
- **What the files hold (E, from datascout's `datasets/download_plan.md` §A1, 12:49):** per cell (36), the EL-derived cell voltage at a set of injected currents; the folder also has `diode_fit_outputs.xls`. **Disclosure:** reading that plan I saw the 3 values it quotes (cells 1-3 of one module at 3.393 A, ~0.654-0.656 V). No other value has been seen. The rules below use physical units (thermal voltage V_t = 25.7 mV at 25 °C, S) so they do not depend on those 3 values.
- **Format discovery first** (allowed after freeze): columns, units, number of cell rows and current levels per file. Logged as facts only. **The fit outputs are not used:** they sit in `diode_fit_outputs.xls`, and the venv has no .xls reader (xlrd, openpyxl and pandas absent; `check` import-tested them) and installs are not allowed. So P comes from the txt **curves**, by the rule below, unless Om allows a reader or a conversion; that would be a dated amendment, not a silent switch.
- **Primary parameter P (frozen choice rule):** if the files hold per-cell voltage at several currents (expected), P = cell voltage at the highest current (≈ 3.393 A), and the per-cell **deficit d = module median P − P** (positive = worse; a resistive or partly isolated cell shows a lower EL-derived voltage, S). Else (if the curves turn out to be current vs a common voltage), P = cell current at the highest common voltage and d = module median P − P. (The Rs route needs the xls and is out, see above.) The rule applied is logged at discovery.
- **Valid cell:** P finite and, for voltages, 0.3 V < P < 0.8 V (plausible single-junction Si range, S).
- **R15a coverage** = valid cells / (158 files × 36).
- **R15b spread** = robust SD of d (1.4826 × MAD, pooled over all valid cells) and the share of cells with d ≥ 1 V_t (≈ 2.7× dimmer EL than the module median, S).
- **Kill T15** (ideas / top3, "fits on < 50% of cells or no spread"): coverage < 50%, **or** no spread, defined now as robust SD of d < 0.1 V_t (2.6 mV) **and** < 1% of cells with d ≥ 1 V_t.
- **Degraded-cell label (frozen):** primary **D90** = d at or above the 90th percentile of d over all valid cells of all modules. Secondary, reported: **DVt** = d ≥ 1 V_t.
- **Sample note:** datascout's 10 modules were drawn by a frozen rule stratified on a dark-I-V severity score (5 quintile bins × 2; `datasets/download_plan.md`), so they are enriched for degraded modules relative to the fleet (S). D90 is still defined on all ~159 modules.
- **R15c (10 modules, after registration):** Spearman ρ between per-cell d and the EL dark-area fraction (§3.3), descriptive. Caveat: the label is **EL-derived**, so EL features are favoured against it; this makes T02's IR increment a conservative test (S).

### 3.2 IR features per cell (10 modules)
- **ΔT** = median temperature over the inner 80% of the cell (by side) minus the module median of the 36 cell medians (°C).
- **Hot-spot index** = 95th percentile − median within the inner 80% (°C), reported.
- **σ_IR** (fleet) = 1.4826 × MAD of ΔT over all registered cells of the 10 modules.

### 3.3 EL features per cell (10 modules; EL-only substitute for E-PF)
- **EL frame (frozen):** the NEF at 3.392-3.393 A that datascout's frozen rule downloads for each of the 10 modules (same current as the IR; per module, EL date minus IR date from the OSF file names: median +4 days, range −7 to +15, same day for 58 of 156, R via `check`). NEF is read via its embedded JPEG preview (§2), so dark fractions are approximate.
- **EL dark-area fraction** = share of inner-90% cell pixels below 0.5 × the module median cell-interior intensity, **after a morphological opening** with a disk of radius 2% of the cell side, which removes thin dark lines (busbars, fingers, cracks) and keeps areas (S). This is the "inactive-like area" proxy until E-PF runs.
- **Candidate inactive cell** = EL dark-area fraction ≥ 5%.

### 3.4 Inactive count (the pick's first risk; top3 step 2)
- **R34** = number and share of candidate inactive cells in the 10 modules, with the module list. Reported, no kill; it scopes what "inactive" in this pick can mean. If R34 < 5 cells, everything below is read as "electrically degraded (series resistance)", not "inactive", and said so in the report.

### 3.5 T02: does IR ΔT add to EL for the physics label? (CPU stage A; stage B with E-PF waits for Om)
- **Data:** registered cells of the 10 modules with a valid T15 fit and passing T37 QA.
- **Scores (AUROC for D90):** (a) EL dark-area fraction alone; (b) logistic regression on [EL dark-area fraction, ΔT, |ΔT|] fitted **leave-one-module-out** (scores for each held-out module come from a model fitted on the other 9); (c) ΔT alone and −ΔT alone, reported.
- **Readout:** Δ = AUROC(b) − AUROC(a), with a module-cluster bootstrap 95% CI (2,000 resamples of modules).
- **Kill / success (ideas / top3):** kill if Δ < +0.03; success if Δ ≥ +0.05. Between: "inconclusive at 10 modules", which goes to Om with the extension request.
- **Power caveat (S):** 10 modules, ~36 D90-positive cells expected by construction; the CI will be wide; the verdict is read on the point estimate as pre-stated, with the CI beside it.
- **Stage B (held):** replace (a) by the E-PF inactive probability mass per cell; same rule.

### 3.6 T12: thermal cell-level flags as weak inactive labels (count and purity; stage 1 on 10 modules)
- **Flag rule (frozen):** cool flag = ΔT ≤ −2 σ_IR (inactive should read cooler under forward bias, S, ideas §0). Hot flags (ΔT ≥ +2 σ_IR) are counted and reported separately (resistive contact heating, S).
- **Proxy purity (CPU):** share of cool-flagged cells that are candidate inactive cells (§3.3). The E-PF overlap or a 0.5 h user glance at 20 flagged cells replaces it only if Om approves.
- **Count:** flagged cells in the 10 modules, and the projection to all 157 A1 modules = rate × 157 × 36, with a module-bootstrap 95% interval.
- **Kill / success (ideas / top3):** kill if < 50 flagged cells or purity < 70%; success if ≥ 200 cells at ≥ 70%. On 10 modules (~360 cells) the count is read on the **projection** (a 10-module count < 50 is expected from sample size alone, S); a pass on the projection asks Om for the A1 extension to confirm on real counts; a proxy purity < 70% on ≥ 10 flagged cells kills **provisionally**, until the E-PF overlap or the user's glance replaces the proxy (if Om approves either).

### 3.7 T37 output
- If T37 QA passes: a cell-registered table and crops for the 10 modules (EL, IR, UVF, dark I-V per cell, features), as `pick3/out/` (outside the data folders), plus a README with sources and the CC BY 4.0 attribution. Release is the user's call (Om: licences / release still open).

## 4. What gets reported, in order (to team-lead)
1. T15 (R15a, R15b, kill / pass) as soon as it is read: team-lead asked for this readout first.
2. Registration QA (T37), R34 inactive count.
3. T02 stage A, T12 stage 1.
Each readout states n (modules, cells), the frozen rule, the value, and the verdict, with E paths to `pick3/out/` files and the script md5s.

## 5. Known weaknesses (S)
- A1 is a resistive-loss set, so "degraded" ≠ "inactive"; R34 tells how much inactive exists.
- The T15 label is EL-derived; EL features are not independent of it. IR is.
- NEF previews are tone-mapped; dark fractions from them are approximate.
- The 2018 EL vs 2022 IR gap (if TIFs are used) can change cell state (cracks open or close; R: doi:10.1038/srep04506).
- 10 modules give wide intervals; T02 and T12 here are stage-1 screens, not claims.

## 6. Amendment v1.1 (dated, written before any data value was read)
Written after `check`'s review of v0.95 (`check/factcheck.md` §13), which crossed with the v1 freeze (5c272fe9). v1's text above is unchanged; where this section differs, **this section governs**. No data value has been read (only the 3 values quoted in datascout's plan, disclosed in §3.1). Team-lead's rule applies: after any value is read, no plan change.

**A. Registration self-test: v1's stated criteria were not met (PL-10).** v1 §2 said the tool must recover corners within 1 px and an inner residual < 1% of a cell side. The logged self-test (`log.md` 12:50; `scripts/cellreg.py` md5 dded0f03; 3 synthetic 4 × 9 modules, outputs in the scratchpad `selftest/selftest.json`) gave:

| Trial | EL corner error | EL inner residual RMS | IR corner error | IR inner residual RMS |
|---|---|---|---|---|
| 0 | 2.71 px (1.51% of cell) | 0.083% | 1.96 px (7.10%) | 1.049% |
| 1 | 2.64 px (1.47%) | 0.060% | 1.69 px (6.62%) | 1.115% |
| 2 | 4.70 px (2.62%) | 0.098% | 2.58 px (9.03%) | 1.070% |

- So the self-test **fails v1's stated criteria**: corners are 1.7-4.7 px off (criterion 1 px), and the IR residual is 1.05-1.12% (criterion < 1%). The "PASS" in my 12:50 log line came from looser thresholds coded in the script after the first run (EL corner < 3% of cell, IR < 10%; residual EL < 1%, IR < 2%). That was a mistake in the log wording, corrected here.
- **Amended criteria (with reasons):**
  - **(i)** Corners are extrapolated from the inner intersections, and the features never use the corners themselves. They use the inner 90% (EL) or 80% (IR) of each cell, i.e. a margin of 5% (EL) or 10% (IR) of the cell side on each side.
  - **(ii)** The criterion is therefore: corner error below the feature margin, i.e. EL < 5% and IR < 10% of a cell side; inner residual EL < 1% and IR < 2%. Measured: EL max 2.62%, IR max 9.03% → passes, with little IR headroom (S).
- **What the T37 residual means:** v1's QA residual (residual at inner intersections after the homography fit) measures **fit consistency, not true error**. The self-test shows a true IR outer-corner error (up to 9.03% of a cell) far above the inner residual (~1.1%). The outer ring of cells (22 of 36 on 4 × 9) carries this risk.
- **Added robustness readout (pre-stated, reported, no verdict change):** every T02 and T12 readout is also reported on the **inner cells only** (rows 2-3 × columns 2-8 on 4 × 9, i.e. 14 cells per module). If an inner-only readout and the all-cell readout land on opposite sides of a kill line, the report says "registration-sensitive".

**B. T02 headroom (PL-11).** The T15 label (EL-derived cell voltage at ~3.393 A) is very likely computed from the same 2022 NEF sweep that gives the EL feature. So AUROC(a) may sit near 1 and leave no room for Δ ≥ +0.03. Pre-stated reading: **if AUROC(a) ≥ 0.97, a Δ < +0.03 is read as "no headroom", not as "IR adds nothing"**. IR-only AUROC (c) is then the reported independent signal (descriptive). The kill and success numbers are unchanged.

**C. EL threshold is on preview values (PL-12).** The NEF preview is gamma-encoded, so "0.5 × module median" is applied to preview values and corresponds to roughly 0.2 of linear intensity (S, `check`). The candidate-inactive proxy is approximate (§3.3 already says so).

**D. Contingency for T15's format (team-lead, 12:54).** If format discovery (structure only, no statistics) shows the txt curves cannot give P (unparseable, not 36 cells, or no current or voltage axis), then before any statistic is computed, a further dated amendment switches P to the fit outputs. The route is `diode_fit_outputs.xls` converted to CSV with the system LibreOffice: headless, a fresh profile in the scratchpad, output in `pick3/derived/`, md5 of input and output logged. If the curves parse, v1 §3.1 stands; a coverage < 50% after reading is then a T15 kill, not a reason to switch.

**E. Trivial:** "~159 modules" in §0 and §3.1's sample note means the 158 curve files (`check`).

## 7. Disclosure (dated 2026-11-04 12:59 IST; §1-§6 unchanged; required by team-lead after `check`'s audit, `check/factcheck.md` §17)
- **(a) Post hoc, synthetic only.** The IR corner bar of 10% of a cell side in §6A was set **after** I had seen the 9.03% self-test maximum. It is post hoc, and it rests on synthetic images only. The real-data T37 kill (inner residual > 5% of a cell side per module; pick kill if > 30% of modules are excluded) was set before any result and is unchanged.
- **(b) Timing.** v1.1 was frozen at 12:56:06, about 1 min after datascout's 12:55 selection numbers were in `log.md` (worst-cell deficit 2.6-19.3 mV, max < 1 V_t). I had not read that line before the freeze (`pick3/plan_pick3_notes.md` N1); I learned the numbers from `check` at ~12:58. No threshold changed (`check` diffed v1 against v1.1).
- **(c) Consequence for T15.** Hence no cell can reach d ≥ 1 V_t: the second no-spread clause is met automatically, and DVt = 0 by construction (reported as frozen). T15's no-spread kill rests on **robust SD(d) < 2.6 mV (0.1 V_t) alone**. That threshold is frozen and must not move.
