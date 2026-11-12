# Thermal: the top 3, with first steps

Owner: synth. Date: 4 Nov 2026. Status: v1.4: Om's decisions of 4 Nov applied; pick 2 re-planned from `ideas/drone_only.md` and `capture/replan_pick2.md`; check's pass-1 and pass-2 fixes applied. Waiting for check's re-check.
Ranking and scores: `ranked_ideas.md` (all scores S). Tags: E = our files, R = source (via the three input files), S = my judgement.
**Timeline basis:** "about 7 weeks left" is team-lead's figure. I read it as weeks W1 = 4-10 Nov to W7 = 16-22 Dec (S, calendar arithmetic).

**The three, chosen to spread risk (S):**

| Pick | Route | Ideas | Data | Starts | Main target |
|---|---|---|---|---|---|
| 1 | Public data, deployment / thesis | T26 + G0 + T27 + T39 (T08 later) | ~1.2 GB public (R sizes, check S-1) | **download approved by Om 4 Nov**; datascout downloads, then executes | WattCycle pipeline, part 3 chapter |
| 2 | WattCycle drone thermal now, low-cost EL soon (re-planned 4 Nov) | W02 + W03 + W01 + W08 + W11, then X6 → X1 / X2 | 1 visit day + 1 night; X6 kit about ₹25k + lens and filter | on WattCycle's answers + Om's funding OK | deployment triage now; scuff + half-cut if X6 works |
| 3 | Public data, model side | T15 → T02 → T12, with T37 as output | same download as pick 1 | **approved 4 Nov**; ideas executes | small inactive |

Picks 1 and 3 share one download and one registration tool.

**Status after Om's decisions (4 Nov, `om_2026-11-04_decisions.md`):**
- Downloads for picks 1 + 3 are approved: about 1.2 GB by Om's count, CPU only, with a disk check first. datascout downloads and then executes pick 1; ideas executes pick 3 (team-lead, log 12:39).
- The later A1 extension is **not** approved. Any extension needs Om's OK with its size.
- E-PF inference is **held** until Om picks the machine, so weeks 1-2 run on the EL dark-area threshold.
- WattCycle is confirmed as WattCycle Sustainable Solutions, but it has only drone thermal now; its EL rig is 2-3 months away. Pick 2 is re-planned below (from `ideas/drone_only.md` and `capture/replan_pick2.md`).

---

## Pick 1: What thermal catches. IR screening vs EL on open pairs

**Why**
- Highest score in the table (T26: V 7, P 0.55; S).
- The data is richer than first read. About 215 public modules have EL + IR: A1 157, A2 15, A3 43 (R, check D-24). A1's IR is dark forward bias at ≈ 1 × Isc, with EL at the same current for each module (R: OSF listing, check D-5).
- It answers Om's pipeline question directly ("drone IR for screening, EL for detail"; E: `om_2026-11-04_thermal.md`). It does so on the one open set built for it: DTU A3 has 43 modules with cracks, interconnect disconnection, PID, glass cracks, shorted bypass diodes and soiling. It holds drone IR at 8-20 m and 200-1000 W/m2 from a DJI Mavic 3T, plus EL at 100% and 10% Isc and I-V (R: datascout A3; doi:10.1051/epjpv/2025020; DTU slides via check pass 3).
- Caveat on size: per-class counts are small (R: DTU slides via check pass 3). Cracks: 8 mono PERC modules, 69 cracked cells, 4-5% loss. Interconnections: 8 modules, 98 cells. The classes sum to 31 degraded + 12 soiled = 43 (the abstract reads as 43 degraded; S). So the per-class AUROC in step 2 rests on about 8 positives per class, with wide intervals (S). The module ranking (T26) uses all 43.
- A3's drone is the same class as the one capture plans flights around for WattCycle (Mavic 3T; WattCycle's model unconfirmed, capture Q1), so A3 is a close public calibration for pick 2 (S).
- It fits the physics: thermal should catch disconnection / inactive / hot spots and miss cracks that isolate nothing (R: ideas §0). Either outcome is a measured table for the deployment (part 3) chapter (E: thesis parts, `handbook/02` §1).
- WattCycle's site lists thermal + RGB drone flights (R: capture §1.1). Om confirmed the company on 4 Nov, and it has drone thermal now (`om_2026-11-04_decisions.md`). A screening-recall table tells them what their drone already catches and what needs EL.
- G0 also tells capture whether steady-state IR is enough or lock-in is needed (ideas §1.1).

**Week 1 (W1)**
1. **Download (approved by Om, 4 Nov; executor datascout).** Target `~/mtp/datasets/thermal_public/<set>/`, each set in its own new, empty folder, with no code run from inside it. Floor: 4.0 GB free after the download, else stop and report (team-lead, log 12:39). Sets: A3 (642.6 MB, R); A2's IR folder (32 files, 15 modules) and one EL per module; A1, 10 modules (one EL exposure, IR jpg + radiometric txt, UVF) and the `EL-Derived_Cell_Dark_I-V` folder.
2. **A3, module level (no model needed):** per module, an IR anomaly score from the radiometric 363 × 605 arrays (R; resampled, native < 1 to 3 cm/px, about 5-16+ px per cell, check D-17), e.g. max cell ΔT over the module median, using frames at ≥ 600 W/m2. Then AUROC of the score per folder defect class. Expected (S): high for disconnection / diode, near 0.5 for cracks.
3. **Registration tool:** cell-grid homography IR ↔ EL per module. A2 first: IR at 5.289 A as text plus converted jpg (R: OSF; that the text is a temperature matrix is S). Then A1: one raw txt per module at 3.393 A, 180 s after current on, with EL at the same current (R: OSF listing, check D-3 / D-5). Report the residual at cell corners.
4. **G0 on A2 + the 10 approved A1 modules** (not ideas' 157-module step 1, which needs Om's OK): per cell, IR ΔT vs the EL dark-area fraction (fixed threshold). Read Spearman ρ, AUROC and the sign (ideas §1.1).
5. **E-PF inference is held** until Om picks gaint CPU or a local copy. PF2E already runs E-PF on gaint CPU fp32 (E: `handbook/14` l.419). Once he decides, the threshold is swapped for E-PF inactive / crack maps. Until then, T26 and G0 use the threshold and A3's folder labels.

**Week 2-4:** T26 with E-PF maps: share of predicted inactive area and crack length in the top 10 / 20 / 30% of IR-ranked modules. T27: AUROC of an E-PF risk score for IR-hot cells. T39: share of E-PF crack components in thermally anomalous cells. Optional T08 (small IR student; ~3 GPU-h, needs a GPU OK) in W3-4.

**Data, downloads, OKs**
- Downloads, picks 1 + 3 together: about 1.2 GB (1.19 GB, R: OSF / Figshare listings via check S-1 to S-4):
  - A3: 642.6 MB, one 7z (R).
  - A2: 16 EL frames at 5.289 A for the 15 IR modules, 0.237 GB, plus IR 15.7 MB: about 0.25 GB (R, check S-2).
  - A1, 10 modules: EL NEF ≈ 14.4 MB + IR 1.6 MB + UVF ≈ 12.6 MB each: about 0.29 GB (R, check S-3).
  - A1 dark I-V: 158 txt + 1 xls, 3.8 MB (R, check S-4).
- Approved 4 Nov (Om), executed by datascout.
- E-PF CPU inference: **open** (machine choice; held).
- No GPU unless T08 is added.

**Cost:** about 6-7 dev days CPU (G0 2, T26 3, T27 + T39 2; S); 0 GPU-h; ₹0.

**Success / kill (pre-stated in ideas)**
- **G0:** go if AUROC ≥ 0.8 with the predicted sign (cooler under forward bias). Kill the fusion / weak-label families if |ρ| < 0.3 and AUROC < 0.7.
- **T26:** success if the top 20% of IR-ranked modules hold ≥ 60% of E-PF-predicted inactive area. Kill if ≤ 20% (no better than random).
- **T27:** kill if AUROC < 0.7.
- A T26 "kill" is still a reportable result: the table, by defect mode, of what IR misses.

**Timeline:** W1 download, A3 table, registration. W2 G0 read, E-PF maps. W3 T26 / T27 / T39 figures (T08 if OK). W4 written section. Done before the W6-7 writing block (S).

---

## Pick 2 (re-planned 4 Nov): WattCycle drone thermal now, low-cost EL soon

**Why the change.** Om confirmed WattCycle on 4 Nov. It has drone thermal only, and its EL rig is 2-3 months away (E: `om_2026-11-04_decisions.md`). So the paired EL + IR capture day (old pick 2: X1 scuff arbiter + X2 WattCycle EL set) cannot run soon. Without EL they fell to P 0.10; with the low-cost EL path (X6) they stand at 0.15 (X1) and 0.20 (X2) (`ranked_ideas.md` §4). The drone-only rows outrank them: W03 rank 4, W02 rank 6, W01 rank 7, W11 rank 10, W08 rank 12. The new pick 2 packages those rows. A cheap EL camera (X6) can bring X1 / X2 back within the thesis (S). Sources: `ideas/drone_only.md` v1 (28f5b0a5), `capture/replan_pick2.md` v1.2 (9d6a4885; §8 has its ranked drone-only actions and the EL-sooner dates).

**What drone IR can and cannot do (R: DTU paper doi:10.1051/epjpv/2025020 and Spataru's IEA PVPS 2025 slides, via capture replan §2.1)**
- It cannot see our crack lines. Cracked cells differ by about 1 °C at most and become unidentifiable below 600 W/m2.
- It can see disconnected interconnects from 600 W/m2 (the worst type > 3 °C), and shorted diodes and heavy soiling (> 10 °C even at 200 W/m2).
- So drone IR is for **triage and pairing**, not crack labels (S). This is the same split pick 1 expects on public data.

**The package (S; scores in `ranked_ideas.md`)**
1. **Desk, now, on approved public data (shared with pick 1):**
   - W03: physics-rule IR scores on A3 (= pick 1 step 2);
   - W05: irradiance / altitude normalisation fitted on A3;
   - W07 / T19: an "expected EL" mapper.
2. **One WattCycle visit day (flight set F1-F4, capture replan §2.2):**
   - F1: survey at ≤ 20 m (≤ 3 cm/px), giving the W02 module ID map and a **half-cut survey** (does the scuff + half-cut context exist on their sites?);
   - F2: a ~10 m cell pass (~1.44 cm/px on a Mavic-3T-class camera, S);
   - F3: a repeat pass 30-60 min later (test-retest noise floor);
   - F4: 6-8 m hovers on flagged modules.
   - All at ≥ 600 W/m2 and wind < 28 km/h, as raw R-JPEG with metadata.
   - Same day, on end-of-life modules on the ground: W08 (open circuit vs load vs short circuit: regions that do not cool under load are inactive candidates) and W10 / W12 (close IR, RGB).
   - That night: W11 (UV torch, crack lines in aged encapsulant).
3. **W01: freeze the EL queue.** After the first flight, freeze `w01_prereg.md` (md5-logged). It lists 20-40 modules (top IR-flagged, a random audit sample, all reachable half-cut ones) and written predictions, e.g. "IR-flagged modules hold ≥ 60% of E-PF-predicted inactive area". The first WattCycle EL session, from X6 or WattCycle's rig, then becomes a prospective test and a fresh unseen-module set nobody has tuned on.
4. **X6: EL sooner, cheapest path (capture replan §3.3).**
   - Kit: a Raspberry Pi HQ camera (IMX477, IR-cut filter removed, exposures to 670 s, ₹4,990, R not re-verified), a Pi 5 (~₹5.1k-6.5k, R not re-verified), a 6-8 mm C/CS lens and an 850 nm long-pass filter (prices unconfirmed), and the 300 W OWON supply (₹12,099; 1-5 day shipping; R, neither re-verified). About ₹25k plus lens and filter.
   - Kit and bench test: W2.
   - A first EL night is possible in W3-4 (18 Nov-1 Dec).
   - The pre-registered queue session follows in W4-5, once W01 is frozen: the W01 queue modules that sit on the ground. It also runs X1 (scuff arbiter with UVF) and X2 (capture replan §8.1 rank 7, §8.2).
   - Fallback: ZWO ASI678MM, ₹62,145 (R), giving EL in W4-5.
   - Free option: borrow an astro-modified or full-spectrum camera at IIT Mandi, if anyone owns one (W2-3; capture Q20).
   - Optional in parallel, X7: ship 3-5 modules to NISE Gurugram for reference EL + STC I-V. The EL fee is not public (R).

**Week 1 (W1, 4-10 Nov)**
1. **Om sends the WattCycle questions (SUMMARY §4).** The gating answers are:
   - the drone and camera model, and whether raw radiometric R-JPEGs are kept (W03 / W05 / W06 need them);
   - sites and module types (any half-cut?);
   - end-of-life modules on the ground, and permission to test them;
   - a contact and a visit date.
2. **Om decides capture funding:** X6 kit about ₹25k + lens and filter, UV torch ₹1,790-4,522 (₹1,790 is an old price; ₹4,522 not re-checked), and optionally the ₹62k fallback and NISE fees. If yes, order X6 parts from Indian sellers (Pi 5 stock uncertain).
3. **Desk (no new data):** W05 / W03 on A3 as part of pick 1 step 2; write the visit sheet (flight set, metadata CSV, ground-test forms; capture replan §2.3); draft the `w01_prereg.md` template.
4. **Public pre-checks for X1 (optional):** T32 on the 10 approved A1 modules (UVF lines vs EL cracks), and X3 (Polenghi abrasion / scrape stages; a 1.13 GB download that is not approved).

**Data, downloads, OKs**
- WattCycle: raw R-JPEGs and flight logs with irradiance, site layouts, a contact, and data terms (thesis, paper, release).
- Om: capture funding (open), E-PF inference location (open; needed for W01's E-PF predictions and the X2 readout).
- No public download beyond pick 1's. No GPU.

**Cost (S)**
- Dev: about 8-10 days (W02 2-3, W03 2 after pick 1, W01 2, W08 2, W11 2; partly shared).
- Field: 1 visit day + 1 UVF night, plus X6's bench day and 1 EL night.
- Money: about ₹27k-30k (X6 + UV torch), optional ₹62k fallback, and NISE fees (unknown).

**Success / kill (pre-stated by ideas and capture)**
- **W02:** ≥ 98% of modules re-identified across two flights. Kill below 90%, in which case W01 / W06 need physical tags.
- **W03 on A3:** disconnection and diode classes separated at AUROC ≥ 0.8; kill below. On WattCycle flights there is no truth yet, so only the flagged share is reported.
- **W01:** the pre-registration is frozen, with 20-40 modules, before any EL image exists. Kill if modules cannot be re-found (W02 fail).
- **W08:** success if some cells do not cool under load; kill if the load-minus-open-circuit difference is below test-retest noise on every module.
- **W11:** kill if aged modules show no UVF crack lines.
- **X6 bench test:** success if crack lines and inactive regions are visible at ≤ 120 s per frame after stacking. Otherwise switch to the ASI678MM or stop.
- **X1, if X6 passes:** as in the old pick 2. EL streaks on half-cut cells split into "UVF line" and "no UVF / RGB / thermal" groups, both non-empty. Kill if UVF and RGB show nothing.

**Timeline (S; W3 = 18-24 Nov throughout, counting W1 from Wed 4 Nov)**
- W1: questions (including the raw R-JPEG archive), funding, desk work on A3 (W03 + W05).
- W2-3 (11-24 Nov): WattCycle visit day (F1-F4, ground tests, UVF night); X6 kit and bench test in W2.
- W3-4 (18 Nov-1 Dec): W03 scores on WattCycle flights; W01 frozen; a first X6 EL night is possible.
- W4-5 (25 Nov-8 Dec): the X6 EL session on the W01 queue, with the predictions read once; then X1 / X2. If no EL exists by then, write up the drone-only results.
- W6-7: writing.
- WattCycle's own EL rig: about Jan-Feb 2027 (S: 2-3 months from 4 Nov), after the thesis.

**Honest limit (S).** Without EL, pick 2 serves deployment (triage, pairing, a frozen prospective test) more than E1 crack recall. Only W11 (UVF crack lines) and X1 / X2 (if X6 works) reach the scuff + half-cut problem. WattCycle's own EL rig (2-3 months) probably lands after the thesis. So W01's prospective test will be read after the thesis, unless X6 passes its bench test and runs the W4-5 session.

---

## Pick 3: Inactive from physics labels on open data

**Why**
- Inactive is data-limited: it appears in 43 of 478 train cells on the old masks (E: `handbook/02` §7 via ideas T12), and E1 inactive is a 3-image readout (E).
- A1 ships EL-derived per-cell dark I-V data (R: datascout A1). These are an "electrically degraded" label that needs no annotator (T15). ideas' frozen plan (`pick3/plan_pick3.md` §3.1) uses the 158 per-module curve txt files: P = cell voltage at ~3.393 A, deficit d = module median − P. It does not use the two-diode fits, which sit in an .xls the venv cannot read.
- Thermal ΔT is a second, independent physics label (T02, T12).
- The registered A1 cell set (T37) is a thesis output in its own right. We found no public set registered EL + IR at cell level (S). Check's re-search found none either, and Almukhtar 2026 §2.1 says the same (check S-11). A1 has bias-matched EL + dark IR on about 157 modules (R, check D-5), so a registered derivative could cover about 157 × 36 ≈ 5,650 cells (S: 36-cell Shell M55, R). It shares pick 1's download and registration code.

**Week 1 (W1)**
1. **T15:** read the A1 EL-derived curves. Measure coverage (valid cells / 158 × 36), the spread of d, and the correlation with the EL dark-area fraction per cell (plan_pick3 §3.1).
2. **Count candidate inactive cells in A1** (EL dark-area threshold now, E-PF later). This is the first risk: A1's losses are mainly resistive, from rear-contact Ag / solder corrosion (R: Colvin et al. 2023, doi:10.1109/jphotov.2023.3238278, the csr6t paper, via check D-6).
3. **T37 first experiment:** register the 10 A1 modules and report the error at cell corners (shared with pick 1, step 3).

**Week 2-5**
- **T02:** AUROC for "degraded cell" (T15 label): E-PF inactive mass alone vs plus IR ΔT.
- **T12:** flag cells by ΔT; count them; check purity on 20 flagged cells (a 0.5 h glance by the user, or E-PF overlap).
- **Only if T12 passes and Om OKs GPU:** one 5-seed mixed-supervision arm vs SUPPF with an inactive guard. About 5.5 GPU-h (E basis: 1.1 GPU-h per run, `handbook/14` l.320-323). Protocol locked first, val + F51 / H36 first, and any test / E1 opening on the user's OK (house rules, E: `handbook/21`).

**Data, downloads, OKs**
- Pick 1's download (approved 4 Nov); executor: ideas.
- If T12 needs ≥ 200 flagged cells, more A1 modules are needed. That extension is **not approved**; it needs Om's OK with its size. ideas' proposed first step is A1's whole IR folder (157 modules, 0.26 GB, R); the remaining A1 EL (about 2 GB) would follow only if the 10-module step shows a signal. At about 16 MB per module for EL + IR without UVF, 30 modules ≈ 0.48 GB (Om's note says 0.55 GB, v1.1's estimate with the 16.7 MB TIF size). All modules at one bias: EL 2.27 GB + IR 0.26 GB ≈ 2.5 GB, or ≈ 4.5 GB with UVF (2.01 GB) (R, check S-5 / S-6). Without it, T12 runs on the 10 approved modules (about 360 cells; S: 36-cell M55) and is judged against the same < 50-cell kill line.
- E-PF inference: **open** (held).
- GPU about 5.5 GPU-h in W4-5, only after the gate.
- Release of T37: the user's call. CC BY 4.0 allows a derivative with attribution (R: datascout); check to verify.

**Cost:** about 9-10 dev days net of pick 1's shared work (T15 2, T02 2, T12 4, T37 5; S). GPU 0 until W4, then about 5.5 GPU-h. ₹0.

**Success / kill (ideas)**
- **T15:** kill if valid cells are < 50%, or d shows no spread: robust SD < 0.1 V_t and < 1% of cells with d ≥ 1 V_t (plan_pick3 §3.1).
- **T37:** kill if registration error is > 5% of a cell side.
- **T02:** kill if ΔT adds < +0.03 AUROC; success if ≥ +0.05.
- **T12:** kill if < 50 flagged cells or purity < 70%; success if ≥ 200 cells at ≥ 70%, then the arm.

**Timeline**
- W1-2: T15, counts, registration.
- W2-3: T02, T12 counts.
- W4-5: GPU arm, if gated in.
- W5-6: T37 package, if the user wants a release.
- W6-7: writing.

---

## How the three fit 7 weeks (S)

| Week | Pick 1 (screening; datascout) | Pick 2 (drone now, EL soon) | Pick 3 (inactive; ideas) |
|---|---|---|---|
| W1 4-10 Nov | download, A3 module table, registration | WattCycle questions, funding, W05 / W03 on A3, visit sheet | T15, A1 counts |
| W2 11-17 Nov | G0 read; E-PF maps once Om picks the machine | visit day (W2-3: F1-F4, W08, W11 night); X6 kit and bench test | T02, registration of more modules |
| W3 18-24 Nov | T26 / T27 / T39 tables | W03 on WattCycle flights; W01 frozen (W3-4); first X6 EL night possible | T12 count and purity |
| W4 25 Nov-1 Dec | section written | X6 EL session on the W01 queue (W4-5) | GPU arm if gated (needs OK) |
| W5 2-8 Dec | | X1 / X2 readout if EL exists, else a drone-only write-up | arm readout |
| W6-7 9-22 Dec | writing | writing | T37 package, writing |

**Not now (S):** fusion (T01, T03, T11), pretraining (T09, T10, T23, T40), reverse bias (T36), time series (T28). They need P1 data, masks, or a better record than A8 / MIM / P15 (E). They come back only if WattCycle's EL rig (or X6) gives paired data, P1 runs and pick 1's G0 passes.
