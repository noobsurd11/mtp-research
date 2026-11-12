# Pick 3b plan: physics labels for inactive-like damage on A3 (DTU), against drone IR

Owner: `ideas`. Written 4 Nov 2026 from 13:37 IST, **before A3 is extracted and before any A3 value is read** (the 7z was still downloading at 13:37; E: `ls` of `A3_dtu/archive`). Version **v1** (v0.95 + `check` PB-1 to PB-3, factcheck §35), frozen by md5 in `log.md` before A3 extraction; v1 is frozen by md5 in `log.md` before any A3 value is read. Changes after the freeze are dated amendments only.
Origin: team-lead's redirect after pick 3's A1 arm stopped (`pick3/out/PICK3_A1_REPORT.md`). Tags: E = our files, R = source, S = my reasoning.

## 0. Rules and scope
- CPU only, `~/mtp/research/.venv/bin/python -I`. Tools: **only frozen, reviewed md5s** (registration: `scripts/frozen/cellreg_7d9a9fe0.py`, v0.4.1), recorded in every run log. Scripts live in `scripts/`, outputs in `pick3/out/b/`. Data folders are read by path; nothing in them is executed.
- Data: A3 as verified by datascout (`datasets/download_verified.md`), nothing else. E-PF is HELD (Om), so EL-only proxies are used. No GPU. No test, E1 or BenchmarkEL read.
- **No duplication of pick 1** (`pick1/plan_pick1.md`):
  - pick 1's R1 (module IR score S_IR by defect class, AUROC vs reference), R2 (IR screening recall of the EL dark area) and R3b (cell-level sunlit ΔT vs EL dark fraction, pooled) are **not recomputed here**;
  - pick 3b **reuses pick 1's frozen per-module S_IR and EL dark fraction** from `pick1/out/A3_module_table.tsv` (definitions in pick 1 R1 / R2) when they exist, citing that file's md5;
  - what pick 3b adds: (i) a **physics label independent of both EL and IR**, the measured STC I-V per module; (ii) the cell-level IR readout **stratified by the induced cause**, not pooled; (iii) a two-current EL label, conditional on the data.
- Known before writing (R, stated expectations, not results):
  - the DTU paper: cracked modules are hard to tell from healthy in drone IR; disconnected interconnects are visible from 600 W/m² (doi:10.1051/epjpv/2025020);
  - class sizes from the DTU slides via `check`: cracks 8, interconnection 8, PID 6, diode 7, glass 2, soiling 6 + 6; module types mono PERC 305 W, bifacial PERC 295 W, bifacial PERC 540 W half-cut;
  - the slides' ΔTmax per class (via pick 1 §0);
  - **the slides' per-class power loss (R via `check` PB-3): cracks 4-5%, interconnections 3-14%, PID 5%, diodes 33-66%, glass < 1%;**
  - the slides say EL at 100% and 10% Isc, while the README says one EL per module; discovery decides 3b-R4;
  - expected strata for 3b-R3: interconnect 8 modules / 98 cells, cracks 8 / 69 (`check`).
  - No threshold below was chosen from them; the PB-3 reading rule in §2 was added after learning the power-loss ranges and says so.
- Literature anchor for the label (R via handbook): power loss tracks the inactive / disconnected area, not crack length (`handbook/02` §9; `literature/notes/F04_el_datasets_census.md` §4).

## 1. Format discovery (allowed after freeze; facts only, logged before any readout)
- The folder structure; per defect class, the module count; module type per module (from names or README).
- **Number of EL images per module and their bias currents** (decides §4). Whether a healthy / reference folder exists.
- The I-V file format: does it give Pmax (or V and I to compute it), Isc, Voc, FF; STC flag; "mean of 3" (R: README).
- How IR frames encode irradiance and altitude.
- Module layout (rows × cols), detected from the EL cell gaps by cellreg v0.4.1.
- No statistic of P, IR or EL is computed during discovery.

## 2. Readout 3b-R1: does the EL inactive proxy track measured power loss? (module level; label validity)
- **Physics label (frozen):**
  - ΔP = 1 − Pmax / Pnom, with Pnom the module type's nameplate power (305 / 295 / 540 W, R via `check`). If the README or I-V files give a pre-damage Pmax per module, that replaces Pnom (choice logged at discovery).
  - **If the module type cannot be recovered** for a module (folder or file names, README, or the I-V file; datascout's table leaves it blank then), ΔP is not computed for that module. If that leaves < 15 modules, the primary label becomes **FF loss = 1 − FF / median FF over all non-soiling modules** (fill factor is roughly comparable across the PERC types, S), and the report says so.
  - Secondary: FF loss = 1 − FF / median FF of the same module type.
- **EL proxy:** pick 1's module EL dark-area fraction (R2 definition: module interior, 3% inset, < 0.5 × module median, opening with radius 2% of a cell). It is computed by pick 1 if available; otherwise with the identical definition, run by me with the frozen tool and logged.
- **Sample:** all non-soiling modules with EL and I-V (expected 31; soiling modules have no EL, R: README via pick 1).
- **Readout:** Spearman ρ(EL dark fraction, ΔP), all modules and within module type, with a module-bootstrap 95% CI (2,000).
- **Verdict line (frozen):**
  - **label-valid** if ρ ≥ 0.5 with CI lower bound > 0;
  - **label-invalid** if ρ < 0.3. The EL dark proxy is then not a physics-anchored inactive label on A3, and 3b-R3 is read as "IR vs EL-dark", not "IR vs inactive";
  - in between: "weak".
  - Too few modules (< 15 with both EL and I-V): not computed.
- **Diodes and label range (pre-stated after `check` PB-3, before any A3 value):**
  - a shorted bypass diode removes a substring from EL and from power (33-66% loss, R), so diode modules alone can drive ρ. 3b-R1 is therefore computed on all non-soiling modules **and** on non-diode modules;
  - the claim "the EL dark proxy is a physics-anchored inactive label on A3" needs **label-valid on the non-diode set**;
  - without diodes, ΔP spans only ~0-14% (R), close to nameplate tolerance (S). So a non-diode ρ < 0.3 is read as **"not separable from a too-narrow label range"**, not as "EL proxy invalid";
  - the same reading applies to 3b-R2's non-diode results.

## 3. Readout 3b-R2: does drone IR track measured power loss, and does it add to EL? (module level)
- **IR score:** pick 1's frozen S_IR (p99 − median of the module array, frames ≥ 600 W/m², median over eligible frames). Same file and md5 as 3b-R1.
- **Readouts:**
  - (a) Spearman ρ(S_IR, ΔP), all non-soiling modules, with a module-bootstrap CI;
  - (b) leave-one-module-out linear models of ΔP on [EL dark fraction] vs [EL dark fraction, S_IR]. Report the held-out R² of each and the increment ΔR², with a bootstrap CI;
  - (c) the same on FF loss, reported.
- **Verdict lines (frozen):**
  - drone IR is a **power-loss proxy** on A3 if ρ(S_IR, ΔP) ≥ 0.5 with CI lower > 0;
  - **not** a power-loss proxy if ρ < 0.3;
  - IR **adds to EL** if ΔR² ≥ 0.10 with CI lower > 0;
  - "no added value" if ΔR² < 0.05.
- **Caveat (S):** a shorted bypass diode removes a substring's power and is very hot in IR (R: slides via pick 1), while its EL may look normal or dark per substring. So the diode class can drive ρ by itself. Hence (a) and (b) are also reported **without the diode class**. Read with that as the "inactive-like" result.

## 4. Readout 3b-R4 (conditional): two-current EL physics label (team-lead's candidate)
- **Runs only if** discovery finds, per module, EL at two currents, one ≤ 0.2 × Isc and one ≥ 0.8 × Isc (expected 10% and 100% Isc). Otherwise it is **not run**, and the report says so. No single-current substitute: that would be pick 1's R3b.
- **Label (frozen):** both EL frames are registered per module with cellreg v0.4.1 to the same canonical grid. Per cell:
  - dark fraction at each current (§3.3 of the pick 3 plan: < 0.5 × module median, opening radius 2% of a cell, inner 90%);
  - **persistent-dark (PD)** fraction = share of pixels dark at both currents, read as inactive-like: an isolated region emits at neither current (S);
  - **resistive-dark (RD)** = dark at high current only (S: series resistance dims EL mainly at high injection).
  - A cell is a PD-candidate if PD ≥ 5%, and an RD-candidate if RD ≥ 5% and PD < 5%.
- **Readout:**
  - per module class, the counts of PD- and RD-candidate cells;
  - Spearman ρ(module PD area, ΔP) vs ρ(module RD area, ΔP). Expected (S, R anchor above): PD tracks ΔP more than RD does;
  - **Verdict line (frozen):** the PD label is "physics-supported" if ρ(PD, ΔP) ≥ 0.5 and exceeds ρ(RD, ΔP) by ≥ 0.1; otherwise not supported.

## 5. Readout 3b-R3: cell level, stratified by induced cause (needs registration)
- **Cells come from pick 1, no re-registration** (agreed with datascout, 4 Nov). 3b-R3 reads datascout's R3b registered cells (cells.tsv per module) from its **QA-passing set only**, after its v0.4 visual-QA criteria and `check`'s co-sign, and cites those files' md5s. The registration choices below are pick 1's (frozen in `pick1/plan_pick1.md` and its amendments). They are restated for reference, not re-run:
  - frozen cellreg v0.4.1, EL in detect mode;
  - IR: the 363 × 605 array. The README says only "sampled to 363x605", so "module-rectified" is **S, not R** (`check` PB-2). **Lesson from A1** (`PICK3_A1_REPORT.md` §3): the array is not assumed to be exactly the module. **Rule agreed with pick 1 before extraction (`check` PB-2):** IR quad = Otsu outline (`--quad-ir otsu`) with a detect grid, and the array-border-vs-outline offset logged per module as a structure fact. A module passes only if the visual QA confirms the outer cells are complete;
  - if pick 1's R3b registers A3 IR any other way, 3b-R3 does not reuse its cells until a dated amendment, written before any 3b-R3 value, resolves it;
  - orientation: the same primary as pick 1's R3b for A3, all 4 orientations reported. If pick 1 has not fixed it at my freeze, the primary is identity, with the 4-way robustness and best-of-4 vs a within-module permutation null that also takes the best of 4 (datascout's Amendment 1 form).
- **QA (pick 1's, applied by datascout and co-signed by `check`; pick 3b adds no QA of its own):**
  - EL or IR inner residual RMS > 5% of a cell → excluded;
  - **visual QA** with pick 1's v2 criteria (md5 fae36d53, per `check` PB-1): 10% bars, plus pick 1's numeric edge check (an outer grid edge > 0.25 cell from the set median → excluded). The ¼-cell visual bar was pick 1's v0.2 Amendment 4 and is superseded;
  - calls are pick 1's (logged before any value, co-signed blind by `check`);
  - > 30% of A3 modules excluded by pick 1's QA → 3b-R3 not run.
- **Cells and label:** per cell, EL dark fraction as pick 3 §3.3; candidate-inactive cell = dark fraction ≥ 5%.
- **IR feature:** ΔT = inner-80% median minus the module median of cell medians, frames ≥ 600 W/m², lowest altitude first (8 m; best native resolution, < 1 cm/px, R). Secondary: the row / column-centred ΔT (pick 1 Amendment 4 form).
- **Readout, per stratum** (interconnect-disconnection modules; crack modules; PID modules; diode modules, reported):
  - AUROC of **+ΔT (warmer)** for candidate-inactive cells vs the other cells. Predicted sign in sunlight: isolated area exports no power, so it reads warmer (S, ideas §0);
  - AUROC of −ΔT, reported;
  - a module-bootstrap 95% CI;
  - all cells and inner cells only.
  - A stratum needs ≥ 10 candidate cells in ≥ 3 modules, else it is not computed. This is stricter than datascout's suggested ≥ 5 positives.
- **Verdict lines (frozen), on the interconnect stratum (primary):**
  - **success** = AUROC(+ΔT) ≥ 0.8 and the row/col-centred AUROC ≥ 0.7: drone IR tracks inactive-like cells at cell level where the cause is disconnection;
  - **kill** for the drone-IR cell-level weak-label route (ideas T12 on sunlit IR) = AUROC(+ΔT) < 0.7 **and** row/col-centred AUROC < 0.6;
  - **opposite sign** = AUROC(+ΔT) ≤ 0.2, reported as "signal, opposite sign", not a kill;
  - **crack stratum:** expected ≈ 0.5 (R: paper). Reported, no verdict.
  - If the primary stratum is not computable (too few cells or modules), 3b-R3 reports "not computable", and the route stays open.

## 6. Order and reporting
1. Discovery facts (logged).
2. 3b-R1 and 3b-R2, which need no registration. If pick 1's A3 module table exists, it is used; else these wait for it, or are computed by its frozen definitions with the md5 logged.
3. 3b-R4, if two EL currents exist.
4. 3b-R3, after pick 1's A3 visual QA is co-signed and its R3b cells exist.

Each readout states n, the frozen rule, the value with its CI, the verdict, and the script and data md5s. The first report to team-lead is 3b-R1 / 3b-R2.

## 7. Known weaknesses (S)
- n ≈ 31 modules, so module-level CIs are wide; ρ ± ~0.35.
- The nameplate power is a weak reference (manufacturer tolerance; no pre-damage Pmax unless the README gives it).
- The induced defects are artificial (lab-induced cracks and disconnections), not field aging.
- The resampled 363 × 605 IR has sub-cell blur at higher altitudes.
- NEF previews are tone-mapped.
- No half-cut module has a crack or scuff (R via pick 1), so nothing here speaks to E1's scuff + half-cut gap.
