# Severity track: summary for the user (16 Nov 2026)

Sources: S0 to S4 in this folder; review `harness/REVIEW_SEVERITY.md` (every number below reproduced by the reviewer). Tags: E = measured, R = paper or dataset page, S = judgement. Nothing here trained a model; external data used for inference and analysis only.

## 1. What the severity output is
- **Per cell** (from the segmentation, no extra model): inactive area fraction a = predicted inactive area (plus crack px it encloses) in % of the cell; band 0 / under 1% / 1% or more; an error bar from our out-of-fold record. Crack length and orientation are printed as description only.
- **Per module:** the worst cell (largest a) with its band, and the module sum of a in cell equivalents.
- **Dropped:** the isolation-risk score (cells cut off from ribbons by cracks). It works on clean labels but not on our predictions (S1, E).
- **Not given:** a power band or a watt figure per cell. No labelled cell of ours has an electrical measurement.

## 2. How good the per-cell output is on our cells (S1, E; PF baseline, out of fold)
- MAE of a: 0.12 pp over 532 cells. Most cells have no inactive area; on the 48 cells that do, the error is about 1.25 pp (post hoc split).
- The model under-states a slightly (bias -0.08 pp).
- Band agreement: kappa 0.78. Detection at 0.5%: sensitivity 0.73, false alarm 0.25%. On CSIR cells, sensitivity is only 0.20.
- The "under 1%" band is unreliable. Cells predicted at 1% or more are truly at 1% or more in 93% of cases.
- These are pool cells "as built". The output is not validated on unseen modules or half-cut cells.

## 3. Evidence from the three external sets
- **Polenghi (2 mini-panels, 84 cumulative damage stages, V x I at about 50 W/m2):** NULL.
  - Predicted inactive area tracks the loss at rho 0.56. Predicted crack length gives 0.65, and stage number alone gives 0.91.
  - Damage only accumulates on these devices, so this record cannot tell damage measures apart. n = 2 devices.
  - The model also under-calls large dark strips here, so this null is not evidence against inactive area.
  - Side finding: knife scratches are read as cracks (+9 to +97 skeleton px).
- **ELPVPower (137 module instances, measured Pmpp; analysis only, terms unverified):** NULL by the pre-set rule.
  - Predicted inactive area ranks modules by power loss at rho 0.87 [0.80, 0.91] (129 modules). Predicted crack length does as well (0.89).
  - Most of that is module type: heavily cracked T3 against near-clean T1. The type order alone gives 0.83.
  - Within T3 (59 modules), inactive area does better than crack length (0.93 against 0.83). This was seen after the fact and is not a result.
  - Within T1, nothing the model sees tracks the loss (rho 0.02). Those losses are not visible as damage.
  - An independent duplicate check found no ELPVPower cell among our training cells.
- **DTU A3 (lab-damaged modules, STC I-V; label = fill factor (FF) loss, which misses bypass-diode loss):**
  - A simple EL darkness count tracks FF loss on the 24 non-diode modules (rho 0.64 [0.24, 0.87]).
  - On the 16 modules our cutting could handle, predicted inactive area tracks FF loss at rho 0.90, against 0.44 for EL darkness on the same modules. That meets the pre-set bar by a hair.
  - Three limits on that comparison:
    - The interval's lower end is about 0 and depends on the bootstrap seed.
    - The four highest-loss interconnect modules failed cutting, and they are the ones where EL darkness works best.
    - Nine of the 16 modules have FF losses within about 0.8% of zero.
  - **Read it as: borderline, on a selected subset.**

## 4. What thermal adds (S4, module level only)
- Drone thermal (hot-spot spread, p99 minus median) does not track FF loss for cracks, interconnects or PID: rho 0.19.
- Added to EL it shows no clear gain: ΔR2 +0.10, interval -0.18 to +0.40.
- It does flag bypass-diode faults and soiling strongly: 16 to 38 deg C, against about 1 deg C for the other defects.
- So thermal is a screen for diode and soiling faults that EL-based severity does not cover. It is not a crack-severity measure.
- No cell-level thermal claim is made (the 4 Nov study found the dark thermal signal row-level).

## 5. What is not supported
- Turning a into watts or a power band per cell or per module.
- "Inactive area predicts power better than crack length": null on Polenghi, null on ELPVPower; on A3 borderline and on a subset.
- Crack length as a severity measure (P617, R), and the isolation score.
- A module rating from our labelled crops (69% of our image ids hold one labelled cell).
- Anything on half-cut modules: the cutting failed on them in A3.

## 6. What a pilot with WattCycle's own modules would need to measure (S, from the numbers above)
- **Per module:**
  - STC I-V (Pmpp, Isc, Voc, FF) with module type and nameplate Pmax, so that diode and substring losses are scored as well.
  - EL at a known current, at two currents if possible.
  - Drone thermal at 600 W/m2 or more.
  - A repeat I-V on a few modules, to know the repeatability (A3's 1 to 2% FF differences may sit inside it).
- **Design:**
  - Modules where cracks and inactive area vary independently, within one module type: several types pooled let type drive the result, as on ELPVPower.
  - Include interconnect and half-cut modules, with a cutting tool that handles them.
- **Size:** about 31 modules for a true rho of 0.5 to show an interval above 0, 90 for 0.3, and about 64 usable modules to halve A3's interval on the inactive-versus-darkness comparison (S4, formula fixed before the data).
- **Rule:** write it before measuring. Primary: rho of the module sum of predicted inactive area with relative Pmpp loss, within type, against crack length.
- As of the 4 Nov decisions (R, thermal team), WattCycle had drone thermal only and an EL rig 2 to 3 months away. Until then a pilot can only test the thermal screen, not EL severity.
