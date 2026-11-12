# What we can do NOW with WattCycle drone thermal alone (no EL for 2-3 months)

Owner: `ideas`. 4 Nov 2026, v1.1 (check fixes DO-1, DO-2, DO-9 applied). For `capture` (pick 2 re-plan) and `synth`. Desk study: nothing run, nothing downloaded for this file.
Basis: Om's decisions (`om_2026-11-04_decisions.md`): WattCycle is WattCycle Sustainable Solutions; it has only a drone thermal setup now; its EL rig is 2-3 months away.

**Tags.** E = our files (path). R = source (Research MCP id or URL). S = my reasoning. Codes as in `ideas/ideas_long.md`: targets **SC** scuff + half-cut, **UR** unseen-module recall, **IN** inactive, **DE** deployment, **SV** severity. Cost = dev days / GPU-h / field days / labelling hours (S unless tagged).

## 0. The one-paragraph logic
Drone IR cannot see the crack pixels we segment (R: cracked modules "difficult to distinguish from healthy ones" in drone IR, doi:10.1051/epjpv/2025020; no hot spots for Dhimish's micro-crack mode, doi:10.1038/s41598-021-03498-z). It can see disconnected interconnects (visible from 600 W/m², R: same DTU paper), hot cells, shorted bypass diodes and heavy soiling (80 to > 100 °C, R: same). It does **not** clearly see PID or glass cracks: in the same drone study they "did not exhibit pronounced thermal anomalies" (R abstract; `check` adds the slides' PID ΔTmax ~2 °C vs 1.5 °C healthy); PID shows clearly in forward-bias ("inverse") IR in the dark (R: doi:10.1016/j.seja.2023.100049), not in sunlit drone IR. So the optimistic plan for the next 2-3 months (S) is: (1) use drone IR to **choose and fix in advance** which modules the EL rig images first, with **pre-registered predictions**, so the first WattCycle EL session is at once a triage test and a fresh unseen-module test set nobody has tuned on; (2) build the **module identity map** so every later EL image pairs automatically with months of IR; (3) get **physics labels without an EL rig** from simple sunlit tricks on end-of-life modules (operating-point and shading thermography, UVF with a torch); (4) build the **drone-IR side of the pipeline** on public data now (DTU A3, InfraredSolarModules, PVF-10) and transfer it to WattCycle flights.

## 1. Ideas (14)

| ID | Idea | Targets | Data | Cost (dev d / GPU-h / field d / label h) | Prior (S) |
|---|---|---|---|---|---|
| W01 | IR-ranked EL queue with pre-registered predictions (prospective test) | DE, UR, SV | WattCycle IR now; EL later | 2 / 0 / 0 / 0 | H |
| W02 | Module identity map and fleet inventory (incl. half-cut survey) | DE, SC | WattCycle IR (+ RGB if any), site plans | 2-3 / 0 / 0.5 / 0 | H (enabler) |
| W03 | Physics-rule baseline on flights (cell ΔT, hot cell, substring, diode) | DE, SV | WattCycle IR | 3 / 0 / 0 / 0 | H |
| W04 | Public-trained drone-IR model applied to WattCycle flights | DE | A3, D1, PVF-10, D2; WattCycle IR | 4 / 0-3 / 0 / 1 | M |
| W05 | Irradiance / altitude normalisation from A3; domain-gap check | DE, UR | A3 (downloaded for pick 1) | 2 / 0 / 0 / 0 | M-H (enabler) |
| W06 | Repeat flights: test-retest noise floor and change detection | SV, DE | WattCycle repeat IR | 3 / 0 / 1 extra flight / 0 | M |
| W07 | IR → "expected EL" mapper trained on public pairs | IN, DE, SV | A3, A1, A2; WattCycle IR | 4 / 0-3 / 0 / 0 | M |
| W08 | Operating-point differential IR on ground modules (OC vs MPP vs SC) | IN, SV | WattCycle camera + end-of-life modules | 2 / 0 / 0.5-1 / 0 | M-H |
| W09 | Shading test: field reverse-bias thermography without a supply | SV, IN | WattCycle camera + end-of-life modules | 2 / 0 / 0.5 / 0 | M |
| W10 | Low-altitude / handheld close-range IR at cell resolution | IN, SV | WattCycle drone or handheld | 1 / 0 / 0.5 / 0 | M |
| W11 | UVF with a UV torch at night: crack lines now, no EL rig | SC, UR | WattCycle aged modules | 2 / 0 / 1 night / 0 | M-H |
| W12 | Drone / phone RGB: snail trails, surface streaks, soiling | SC, DE | RGB if WattCycle has it; phone | 2 / 0 / 0.5 / 0 | M |
| W13 | Soiling vs electrical anomaly: IR before / after cleaning or with RGB | DE | WattCycle IR (+ RGB) | 1 / 0 / 0.5 / 0 | M |
| W14 | Natural-transient thermography (cloud passages, morning warm-up) | IN, SV | WattCycle IR video | 3 / 0 / 0.5 / 0 | L |

### W01. IR-ranked EL queue with pre-registered predictions
- **Mechanism:** rank every module WattCycle flies by an IR anomaly score (W03 / W04). Before the EL rig arrives, freeze a file listing the modules for the first EL session (top-k IR-flagged + a random audit sample + half-cut modules from W02) and our predictions (e.g. "IR-flagged modules hold ≥ 60% of E-PF-predicted inactive area"; "IR misses most crack-only modules"). When EL arrives, the session is a **prospective** screening test and a **new unseen-module EL set** that no model or person has tuned on (S). It mirrors pick 1's T26 table on public data, now on WattCycle's own fleet.
- **Targets:** DE, UR (a second unseen-module set besides E1, chosen before seeing it), SV.
- **Data:** WattCycle IR now; WattCycle EL in 2-3 months.
- **Cost:** 2 / 0 / 0 / 0 now (the EL session is capture's).
- **First experiment:** after one flight: score modules, write `w01_prereg.md` (md5-frozen, as house protocols), pick 20-40 modules (S) stratified as above.
- **Kill / success:** kill if WattCycle cannot re-find the same physical modules later (no identity map, W02). Success at EL time: the pre-registered T26-style numbers are read once, with the random audit giving the base rate.
- **Tags:** R: drone IR > 1 module/s (doi:10.1088/2516-1083/ac890b, abstract); S for the design. E: E1 has been opened many times (`handbook/21` §9); a fresh set chosen in advance avoids that.

### W02. Module identity map and fleet inventory (incl. half-cut survey)
- **Mechanism:** an orthomosaic or a row / string / position index per site that gives each module a stable ID, so every later EL, UVF or RGB image pairs with all earlier IR flights. In the same pass, count module types: half-cut vs full, mono vs multi (half-cut modules show a centre split in IR and RGB, S). If WattCycle's fleet holds half-cut multi modules, the scuff + half-cut context exists on site, and those modules go into W01's EL queue.
- **Targets:** DE (the enabler for every pairing), SC (finding the context).
- **Data:** WattCycle IR (+ RGB if their drone has it), site layout.
- **Cost:** 2-3 / 0 / 0.5 / 0.
- **First experiment:** one site: module-detection and ID assignment on one flight; re-identify the same modules on a second flight; report the ID match rate.
- **Kill / success:** success ≥ 98% of modules matched across two flights (S threshold). Kill if under 90%: then W01 / W06 need physical tags.
- **Tags:** R: module extraction and mapping from aerial IR video (doi:10.1002/pip.3448); aerial IR review notes orthomosaicking and path planning are rarely automated (doi:10.3390/en15062055). Capture's homography / fiducial code (pick 2) is reusable (S).

### W03. Physics-rule baseline on flights
- **Mechanism:** without ML: per module, cell-level ΔT over the module (or string) median, counts of hot cells, hot substrings (bypass diode active), whole-module warm (open string), and patchy warm cells (PID-like; weak in sunlit IR, see §0), at irradiance ≥ 600 W/m². Outputs a per-module anomaly class and score for W01, and weak labels for W04.
- **Targets:** DE, SV.
- **Data:** WattCycle radiometric IR (needs radiometric export, not only palette JPGs; capture Q5).
- **Cost:** 3 / 0 / 0 / 0 (CPU).
- **First experiment:** run the rules on A3 first (known induced defects): per-class AUROC, which is pick 1's step 2; then on one WattCycle flight.
- **Kill / success:** kill on A3 if disconnection and diode classes are not separated (AUROC < 0.8; the DTU paper says they are visible, R). On WattCycle there is no truth yet, so report the flagged share.
- **Tags:** R: doi:10.1051/epjpv/2025020; Sitemark's reading of IEC TS 62446-3 (≥ 600 W/m², max 3 cm/px; [Sitemark](https://www.sitemark.com/blog/is-sitemark-iec-compliant/), secondary).

### W04. Public-trained drone-IR model applied to WattCycle flights
- **Mechanism:** train a small cell / module anomaly model on public IR (A3 drone IR; InfraredSolarModules, 20,000 crops at 24 × 40 px, 12 classes, MIT, R: datascout D1; PVF-10, 5,579 crops from 8 plants, R: doi:10.1016/j.apenergy.2024.124187; FSEC IR-visual pairs D2) and apply it to WattCycle flights, with W03's rules as a cross-check. Cross-plant shift is the known problem: ResNet-34 + supervised contrastive + kNN gave AUROC 73.3% to 96.6% over 9 source-target plant pairs (R abstract: doi:10.1002/pip.3518).
- **Targets:** DE.
- **Data:** public (D1 / PVF-10 need a download OK; A3 is approved with pick 1), WattCycle IR.
- **Cost:** 4 / 0-3 (a small CNN on 24 × 40 crops may train on CPU, S) / 0 / 1 h (spot-check 50 WattCycle flags).
- **First experiment:** leave-one-plant-out on PVF-10 + A3 to estimate cross-plant AUROC before touching WattCycle.
- **Kill / success:** kill if agreement with W03 rules on WattCycle is < 0.6 (Cohen κ, S) and the 50-flag spot check finds < 50% real anomalies.
- **Tags:** R as above; S.

### W05. Irradiance / altitude normalisation from A3; domain-gap check
- **Mechanism:** A3 imaged the same modules at 200-1000 W/m² and 8-20 m; irradiance mattered far more than altitude, and soiling hot spots read 5-10 °C cooler at higher altitude (R abstract: doi:10.1051/epjpv/2025020). Fit ΔT vs irradiance per defect class on A3, then normalise WattCycle flights to a reference irradiance, so W01's ranking and W06's change detection compare like with like. Also compare WattCycle image statistics (GSD, camera, ΔT spread) with A3 / D1 / PVF-10 to pick W04's training set.
- **Targets:** DE, UR (domain shift on the IR side).
- **Data:** A3 (in the approved download), WattCycle flight logs with irradiance (pyranometer or plant SCADA; capture question).
- **Cost:** 2 / 0 / 0 / 0.
- **First experiment:** A3: per module, ΔT at each irradiance; fit a per-class slope; report residual spread.
- **Kill / success:** kill the normalisation if the per-class slope varies more across modules than the effect it corrects (S); then fly only above a fixed irradiance.
- **Tags:** R, S.

### W06. Repeat flights: test-retest noise floor and change detection
- **Mechanism:** two flights on the same day give the noise floor of cell ΔT (S); flights weeks apart, normalised by W05, give per-module change. Modules whose hot-cell count or ΔT grows go up W01's EL queue. Cracks can reopen or close with load and temperature (R: doi:10.1038/srep04506, recovery on unloading), so a module can change thermal state between visits (S).
- **Targets:** SV, DE.
- **Data:** WattCycle repeat IR (they may already fly sites repeatedly; capture question).
- **Cost:** 3 / 0 / 1 extra flight / 0.
- **First experiment:** two flights 30-60 min apart at stable irradiance on one site: per-cell ΔT test-retest correlation and the minimum detectable change.
- **Kill / success:** kill change detection if test-retest ρ < 0.7 (S threshold); success ≥ 0.9.
- **Tags:** R, S. Prior M because thesis time is short (7 weeks; E: `synth/top3.md` timeline).

### W07. IR → "expected EL" mapper trained on public pairs
- **Mechanism:** on public modules with EL + IR (A3 drone IR; A1 / A2 forward-bias IR), learn a per-module or per-cell mapping from IR features to EL-derived quantities (EL dark-area fraction now; E-PF inactive fraction once E-PF inference is approved). Apply it to WattCycle flights to predict "expected EL inactive" per module, which becomes one of W01's pre-registered predictions. This is the "link drone IR to our model" route (ideas T08 / T19).
- **Targets:** IN, DE, SV.
- **Data:** A1, A2, A3 (approved downloads), WattCycle IR.
- **Cost:** 4 / 0-3 / 0 / 0.
- **First experiment:** on A3, Spearman between module IR score and EL dark-area fraction, by defect class (CPU; shares pick 1's tables).
- **Kill / success:** kill if Spearman < 0.5 on A3 held-out modules; success ≥ 0.7.
- **Tags:** R: doi:10.1109/cvpr.2016.309 (supervision transfer across paired modalities); doi:10.1051/epjpv/2025020. S.

### W08. Operating-point differential IR on ground modules (OC vs MPP vs SC)
- **Mechanism:** a recycler has end-of-life modules on the ground (R via capture §1.1: ReVive recycling). Image each module in sun with the same thermal camera at open circuit, then at a load near MPP (a resistor bank or cheap DC load), then short circuit. At open circuit no power leaves, so all absorbed light becomes heat; at MPP the active regions export ~20% and should cool, while isolated (inactive) regions stay at their open-circuit temperature (S, energy balance). At short circuit a cell with less current is pushed into reverse bias and heats (S; cells with larger cracked areas run hotter, R: doi:10.1038/s41598-022-16546-z). The MPP-minus-OC difference image marks where power is extracted, a sunlit stand-in for an EL inactive map at IR resolution. IR in illumination and dark gives complementary results for the same defects (R abstract: doi:10.3390/s20164395).
- **Targets:** IN (inactive candidates without an EL rig), SV.
- **Data:** WattCycle thermal camera (handheld mode or drone hovering low), 10-20 end-of-life modules, an MC4 shorting lead and a load.
- **Cost:** 2 / 0 / 0.5-1 / 0. Safety: DC up to Isc ~10 A per module; connect and disconnect only at open circuit or with a DC switch; PPE (S; capture's safety section applies).
- **First experiment:** 5 modules, 3 operating points each, 2 frames per point, irradiance logged.
- **Kill / success:** kill if MPP-OC differences are below the camera's test-retest noise on every module (S); success if some cells show a region that does not cool at MPP. When EL arrives, those modules go first in W01 and test the prediction.
- **Tags:** S (mechanism), R as cited. Outdoor IRT "in the fourth quadrant" with a bidirectional inverter is proposed in the same R paper.

### W09. Shading test: field reverse-bias thermography without a power supply
- **Mechanism:** cover one cell (opaque card) on a module in sun at short circuit; the string current drives the shaded cell into reverse bias, as in a hot-spot test, and shunts or pre-breakdown sites heat. Reverse-bias thermography predicts hot-spot temperature and reveals the causes of reverse currents (R abstract: doi:10.1016/j.egypro.2014.08.097). Single-cell tests under a sun simulator found the worst hot spots when a mode-3 cracked cell was 40-60% shaded (R: doi:10.1038/s41598-021-03498-z, full text via `check`); that this carries to a shaded cell inside a module in the field is S. Gives hot-spot-risk labels (ideas T27, T36) with no EL rig and no supply.
- **Targets:** SV, IN (shunt-like dark cells are partly our "dead cell" / "material"; S).
- **Data:** WattCycle camera + sacrificial end-of-life modules only.
- **Cost:** 2 / 0 / 0.5 / 0. Safety: hot spots can damage the module and backsheet; limit to ≤ 1-2 min per cell and a temperature cut-off (S); never on customer modules.
- **First experiment:** 3 modules, 5 cells each, ΔT curves over 60 s.
- **Kill / success:** kill if no cell exceeds module median + 10 K (S threshold).
- **Tags:** R, S.

### W10. Low-altitude / handheld close-range IR at cell resolution
- **Mechanism:** fly lower or use the camera by hand on selected modules: A3 reached < 1 cm/px at 8 m (R: doi:10.1051/epjpv/2025020), about 15+ px per 16 cm cell (S arithmetic), enough for within-cell patterns such as the elongated pattern of a disconnected interconnect (R: same). Use for the W01-flagged modules only, so W07 / W08 get cell-level detail.
- **Targets:** IN, SV. **Data:** WattCycle drone or handheld. **Cost:** 1 / 0 / 0.5 / 0.
- **First experiment:** the same 5 flagged modules at survey altitude and at 8 m; does the anomaly resolve to a cell or a cell part?
- **Kill / success:** kill if close range adds no structure beyond the survey image on any flagged module.
- **Tags:** R, S.

### W11. UVF with a UV torch at night: crack lines now, without an EL rig
- **Mechanism:** not thermal, but it needs no EL rig: UV fluorescence shows cell cracks in aged modules, in order of occurrence (R abstract: doi:10.1109/jphotov.2019.2961781), handheld at ~250 modules/h or by drone at up to 720 modules/h (R: same). End-of-life modules are aged (S), so crack lines should be present. On half-cut multi modules from W02, UVF lines are crack evidence that does not depend on EL texture (S), and they can be paired with EL when the rig arrives, giving the crack vs scuff split (ideas T32, pick 2's X1). Kit: a UV torch (a few thousand rupees; the ₹1,790 quote is an old price and ₹4,522 is unchecked, per `check`) and a phone camera.
- **Targets:** SC, UR.
- **Data:** WattCycle aged modules; capture at night or in a dark shed.
- **Cost:** 2 / 0 / 1 night / 0.
- **First experiment:** 10 end-of-life modules incl. any half-cut: count modules with UVF crack lines; photograph with fiducials for later EL pairing. Public pre-check runs first on A1's UVF (pick 2 step 3).
- **Kill / success:** kill if no UVF crack lines on aged modules (fresh or non-fluorescing encapsulant; UVF depends on encapsulant / backsheet type, R: doi:10.1002/solr.202400566).
- **Tags:** R, S.

### W12. Drone / phone RGB: snail trails, surface streaks, soiling
- **Mechanism:** snail trails correlate with cell microcracks (R abstract: doi:10.1109/jphotov.2014.2330495), so close-range RGB is a crack proxy on aged modules; surface streaks visible in RGB are scuff candidates if scuff is a surface mark (S). RGB also maps soiling, which causes strong IR hot spots (R: doi:10.1051/epjpv/2025020) that are not our EL classes (W13). UAV thermal + RGB fusion for PV inspection exists (R abstract: doi:10.32620/reks.2025.4.13). Public probe for the scuff analogy: C1's abrasion and scrape stages with aligned EL and visible images (R: doi:10.1016/j.dib.2026.113109).
- **Targets:** SC, DE. **Data:** WattCycle's RGB sensor if any (their site lists thermal and RGB flights, R via capture §1.1; Om says thermal only, so ask), or a phone. **Cost:** 2 / 0 / 0.5 / 0.
- **First experiment:** RGB of the W11 modules; count snail-trail modules; later compare with EL.
- **Kill / success:** kill the RGB crack proxy if snail trails appear on < 10% of UVF-cracked modules (S).
- **Tags:** R, S.

### W13. Soiling vs electrical anomaly: IR before / after cleaning, or with RGB
- **Mechanism:** heavy soiling makes 80 to > 100 °C hot spots (R: doi:10.1051/epjpv/2025020), which would fill W01's EL queue with modules that are electrically fine. Re-fly after cleaning (or use RGB) and drop anomalies that vanish.
- **Targets:** DE (queue precision). **Data:** WattCycle IR (+ RGB). **Cost:** 1 / 0 / 0.5 / 0.
- **First experiment:** one site, flagged modules re-imaged after routine cleaning.
- **Kill / success:** report the share of flags that were soiling; kill if < 5% (not worth the step; S).
- **Tags:** R, S.

### W14. Natural-transient thermography (cloud passages, morning warm-up)
- **Mechanism:** irradiance steps (clouds, sunrise) act as a free heat pulse; regions with different heat paths (delamination) or no electrical export (isolated area) may follow different time constants (S). Needs IR video at a fixed position.
- **Targets:** IN, SV. **Data:** WattCycle IR video (hover or tripod). **Cost:** 3 / 0 / 0.5 / 0.
- **First experiment:** 10 min of IR video of 3 modules through a cloud passage; per-cell time constant map.
- **Kill / success:** kill if time-constant maps show no structure beyond noise.
- **Tags:** S; active / transient IR review (R abstract: doi:10.3390/s23218780). Prior L.

## 2. Suggested order for the next 2-3 months (S)
1. **Week 1-2 (desk, public):** W05 and W03 on A3 (shares pick 1's download and step 2); W07 first readout on A3.
2. **First WattCycle visit (one day):** a flight, W02 IDs and inventory, a second flight 30-60 min later (W06 noise floor), W08 and W09 on 5-10 end-of-life modules, W10 on flagged modules; that night W11 (UVF) on the same end-of-life modules; RGB (W12).
3. **Then:** write and freeze `w01_prereg.md` (the EL queue with predictions) before the EL rig arrives.
4. **When EL arrives:** image the W01 queue first; read the pre-registered predictions once; run E-PF on WattCycle EL (needs Om's inference decision).

## 3. Questions for WattCycle (drone-only version; for capture to merge)
1. Drone and camera model; radiometric export (raw temperature per pixel, not palette JPG only)? GSD at survey altitude; can you fly at ~8 m over selected rows? (W03, W05, W10)
2. Do you log irradiance (pyranometer, SCADA) and time per flight? (W05)
3. Which sites and module types do you fly; any half-cut multi modules? Can modules be re-identified across flights (string maps, orthomosaic)? (W02)
4. Do you fly the same site repeatedly; how often? Can we add a second pass 30-60 min after the first? (W06)
5. Does the drone carry an RGB sensor too? (W12, W13)
6. Do you hold end-of-life modules on the ground we may test in sun at open circuit, load and short circuit, and shade single cells on 2-3 sacrificial ones? (W08, W09)
7. Can we image those modules at night with a UV torch? (W11)
8. Data terms: may thesis and paper use the IR data; may a derivative be released? (all)

## 4. Sources
- PV physics and IR: doi:10.1051/epjpv/2025020; doi:10.1038/s41598-021-03498-z; doi:10.1038/s41598-022-16546-z; doi:10.1016/j.seja.2023.100049; doi:10.1016/j.egypro.2014.08.097; doi:10.1038/srep04506; doi:10.3390/s20164395; doi:10.3390/s23218780.
- Drone IR tools and data: doi:10.1088/2516-1083/ac890b; doi:10.3390/en15062055; doi:10.1002/pip.3448; doi:10.1002/pip.3518; doi:10.1016/j.apenergy.2024.124187; doi:10.32620/reks.2025.4.13; InfraredSolarModules via `datasets/dataset_table.md` D1.
- Other modalities: doi:10.1109/jphotov.2019.2961781; doi:10.1002/solr.202400566; doi:10.1109/jphotov.2014.2330495; doi:10.1016/j.dib.2026.113109.
- Methods: doi:10.1109/cvpr.2016.309.
- Web (secondary): [Sitemark](https://www.sitemark.com/blog/is-sitemark-iec-compliant/).
- Project files (E): `om_2026-11-04_decisions.md`; `synth/top3.md`; `capture/capture_plan.md` §1.1; `ideas/ideas_long.md`; `handbook/21` §9.
