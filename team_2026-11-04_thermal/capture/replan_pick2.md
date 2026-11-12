# Pick 2 re-plan: drone thermal now, EL sooner (WattCycle)

Owner: capture. Date: 4 Nov 2026. Status: v1.2 (v1.2: check §12 RP-6 price marks, RP-2 A3 note; v1.1 adds §8, short lists for synth, and synth's week numbering), desk study (no contact, no downloads, no GPU).
Weeks follow synth: W1 = Wed 4 to Tue 10 Nov, W2 = 11 to 17 Nov, W3 = 18 to 24 Nov, W4 = 25 Nov to 1 Dec, W5 = 2 to 8 Dec, W6 = 9 to 15 Dec, W7 = 16 to 22 Dec.
Basis (E): `om_2026-11-04_decisions.md` (2): WattCycle is confirmed as WattCycle Sustainable Solutions. It has **only a drone thermal setup** now, and its EL rig is 2 to 3 months away. Merges `ideas/drone_only.md` v1 (W01 to W14). Extends `capture/capture_plan.md` v1.2.
Tags: **E** = our files (path); **R** = source (Research MCP id or URL); **S** = my reasoning. "unconfirmed" = not verified. Prices are listings seen on 4 Nov 2026.

## 0. Summary

We can start useful work now with WattCycle's drone alone, and we can probably get some WattCycle-domain EL within 3 to 4 weeks for well under ₹1 lakh.

**What drone IR can and cannot do (R, DTU 2025 study on 43 degraded modules):**
- It **cannot** see our crack lines: cracked cells differ by at most ~1 °C and become unidentifiable below 600 W/m2.
- It **can** see disconnected interconnects (identifiable down to 600 W/m2, worst type > 3 °C), shorted bypass diodes and heavy soiling (> 10 °C even at 200 W/m2).

So drone IR is a **triage and pairing** tool, not a crack labeller (S). The plan for the next 2 to 3 months (S, merging ideas W01 to W13):
1. Fly a fixed protocol: ≥ 600 W/m2, wind < 28 km/h, ≤ 3 cm/px survey, ≤ ~1.5 cm/px cell passes, radiometric R-JPEG, full metadata.
2. Build a module ID map with a half-cut survey.
3. Run physics-rule scores calibrated on the public DTU set (shared with pick 1).
4. Freeze a pre-registered "EL queue" of modules before any EL exists, so the first WattCycle EL is a clean, prospective unseen-module test.
5. On end-of-life modules on the ground, get physics labels with no EL rig: open-circuit / MPP / short-circuit thermography, single-cell shading, close-range IR, and night UV fluorescence with a ₹2k to ₹5k torch.

**EL sooner, cheapest path (S):** a Raspberry Pi HQ camera (Si sensor, IR filter removable, exposures to 670 s, C/CS lens mount; ₹4,990) on a Pi 5 (~₹5.1k to ₹6.5k), plus a C-mount lens and an 850 nm long-pass filter, plus the 300 W OWON supply (₹12,099). Images go in a dark shed or at night. Kit is about ₹25k plus lens and filter, in Indian stock, with a bench test in week 2 and the first WattCycle EL in week 3 to 4. A better-sensor fallback is a ZWO ASI678MM mono camera (₹62,145 incl. GST and duty).

**In parallel:** NISE Gurugram lists a per-module EL test (fee not public) and STC testing. Shipping 3 to 5 modules there gives a reference-grade EL + I-V of the same modules (R; fee and turnaround unconfirmed).

WattCycle's drone cannot do EL: drone EL needs a SWIR camera (~€10k to 15k) and back-powering (R). Other nearby institutes: NIT Hamirpur lists only teaching PV kits; nothing public was found for IIT Ropar or PEC.

## 1. What changed and what still holds
- **Changed (E):** no WattCycle EL for 2 to 3 months, so capture_plan P0 (paired EL + dark thermal on one mount) cannot run as planned.
- **Still holds (S):** the registration method (capture_plan §4), the P0 per-module protocol (§5, run as soon as *any* EL camera exists), the safety rules (§7), the data format (§5). The new low-cost EL camera (§3) plugs straight into P0.
- **Thermal camera for P0 dark thermography:** WattCycle has a drone thermal camera, but a handheld or phone IR camera (₹20k to ₹30k, capture_plan §3) is simpler indoors. Using the drone camera on the ground is unconfirmed; see Q7.

## 2. (a) What we can do NOW with WattCycle's drone thermal alone

### 2.1 What drone IR shows for our classes
| Defect | Drone IR signal | Tag / source |
|---|---|---|
| Cell cracks (our crack class) | ΔT max ~1 °C; hard to assess at 600 W/m2, unidentifiable below. Cells with < 10% and < 30% cracked area ran *warmer* than > 30% ones | R: DTU slides (Spataru, IEA PVPS T13 meeting, ISFH 2025), https://iea-pvps.org/wp-content/uploads/2025/08/07_S.-Spataru_Framing-Drone-IRT-Conditions.pdf , slide 13; paper doi:10.1051/epjpv/2025020 ("cell cracks are difficult to distinguish from healthy ones") |
| Broken cell interconnections (inactive-like) | identifiable down to 600 W/m2; "type 4" disconnections > 3 °C; elongated patterns | R: same slides, slide 14; paper abstract |
| Shorted bypass diode, heavy soiling | > 10 °C even at 200 W/m2; soiling hotspots 80 to > 100 °C | R: slides 9 to 12; paper abstract |
| PID, glass cracks | no pronounced anomaly at the tested conditions | R: paper abstract |
| Scuff (cosmetic) | none expected | S |
| Half-cut layout | visible as a split module layout at cell-level GSD | S (ideas W02) |

**Reading (S):** drone IR helps for inactive / disconnection / hotspot triage and for picking *which* modules get EL first. It cannot replace EL for crack and scuff. That matches pick 1's expected outcome on public data (`synth/top3.md` pick 1).

### 2.2 Flight protocol (for our purposes)
| Item | Setting | Tag / source |
|---|---|---|
| Irradiance | ≥ 600 W/m2 in the module plane; prefer ≥ 800 W/m2 for interconnect signals; stable (no cloud passages during a pass) | R: DTU slide 4 ("IEC TS 62446-3: > 600 W/m2"); slide 14; S for "prefer" |
| Wind | < 28 km/h | R: DTU slide 4. Vendor summaries conflict (one says 4 m/s): https://sinovoltaics.com/field-inspection-services/pv-field-inspection/thermography/ ; record the measured wind |
| Sky | low cloud cover | R: DTU slide 4 |
| Plant state | inverters on, at MPP, not curtailed; log the state | S (IR contrast needs current flow); vendor summary lists "plant operating state" as a record item (R, secondary: https://thermalvariations.com/learn/iec-62446-3-thermal-inspection ) |
| Survey GSD | ≤ 3 cm/px on the modules | R: DTU slide 5 ("IEC TS 62446-3: spatial resolution max. 3 cm/pixel"; slide reading, the standard's text not read) |
| Cell-level GSD | ≤ ~1.5 cm/px (~10 px per 156 mm cell; ~12 px per 182 mm cell) | S |
| Close pass on flagged modules | ~1 cm/px or better (DTU reached < 1 cm/px at 8 m) | R: doi:10.1051/epjpv/2025020; S target |
| Altitude (DJI Mavic 3T-class camera: 640 x 512, 12 µm, DFOV 61°, 40 mm equiv., focus 5 m to ∞) | GSD ≈ altitude / 696 px: 8 m → 1.15 cm, 10 m → 1.44 cm, 14 m → 2.0 cm, 20 m → 2.9 cm. So survey ≤ 20 m, cell passes ~10 m, flagged modules ~6 to 8 m | R for specs: https://volatusdrones.ca/products/dji-mavic-3-thermal-advanced (DFOV, equiv. focal), https://cliftoncameras.co.uk/dji-mavic-3-thermal (focus range listing); S for the arithmetic (consistent with DTU's 8 to 20 m → < 1 to 3 cm/px, R). **WattCycle's actual drone is unconfirmed (Q1)** |
| Altitude vs irradiance | within 8 to 20 m, altitude matters much less than irradiance; soiling hotspots read 5 to 10 °C cooler at higher altitude | R: doi:10.1051/epjpv/2025020 |
| Public analogue | DTU A3 was flown with a DJI Mavic 3T. It includes bifacial PERC 540 W **half-cut** modules (shorted-diode, glass-crack and soiling groups) and EL at 100% and 10% Isc. Its crack group is only 8 mono PERC 305 W modules (69 cracked cells). So A3 is a half-cut drone-IR source, but not a half-cut *crack* source | R: DTU slides (check RP-2, read via pdftotext) |
| View angle | close to perpendicular to the module plane, but tilt a few degrees off the specular direction so the camera does not see sun or drone reflections in the glass | R: one provider says perpendicular, https://www.solarthermografie.de/en/pv-thermography-inspection/ ; S for the reflection tilt; the standard's angle table was not read |
| Time | late morning to early afternoon on clear days, for irradiance and stability | S |
| File format | radiometric R-JPEG (16-bit), not palette JPEG | R: listing "JPEG (8-bit), R-JPEG (16-bit)" for Mavic 3T; per-pixel temperatures via DJI Thermal SDK tools (R, community / preprint: https://www.npmjs.com/package/dji-thermal-sdk ; https://www.researchsquare.com/article/rs-10826739 ). Official SDK docs not read; one forum report says some Mavic 3T (EU) files failed in a converter (R: https://mavicpilots.com/threads/dji-thermal-images-processing-converter-to-tiff-solved.142872 ) |
| Camera parameters | keep emissivity, reflected temperature and distance settings fixed across flights and log them; analyse raw values | S |
| Overlap / speed | enough overlap for an orthomosaic (W02); slow enough to avoid motion blur at 30 Hz | S |
| RGB | take the drone's visible images at the same time if the drone has RGB (Mavic 3T does; WattCycle's model unconfirmed) | R: Mavic 3T has a wide RGB camera (listings above); S for use |

**Flight set per site visit (S, from ideas W02, W06, W10, W14):**
1. **F1 survey:** whole site, ≤ 20 m, grid with overlap → orthomosaic, module IDs, half-cut survey (W02), physics-rule scores (W03).
2. **F2 cell pass:** ~10 m over rows with flagged modules and all half-cut rows.
3. **F3 repeat:** F1 or F2 again 30 to 60 min later at similar irradiance → test-retest noise floor (W06).
4. **F4 close hovers:** 6 to 8 m over the top ~10 to 20 flagged modules (W10).
5. **F5 optional:** 5 to 10 min hover video over 3 to 5 modules through a cloud passage (W14, low prior).
6. Revisit monthly if WattCycle flies the site anyway (W06 change detection).

### 2.3 Metadata to log per flight (S)
- **Site:** name / location, capacity, row and string map, module make / model / type (full or half-cut, mono / multi, cells per module), installation year, last cleaning date.
- **Flight:** date, start / end time, drone and camera model + serial, firmware, altitude AGL, GSD, gimbal pitch, speed, overlap, pilot.
- **Environment:** plane-of-array irradiance with timestamps (pyranometer or plant SCADA), ambient temperature, wind speed, cloud notes, module back-sheet temperature if a sensor exists.
- **Plant state:** inverter status, curtailment, known outages.
- **Camera settings:** emissivity, reflected temperature, distance, palette (irrelevant if raw is kept).
- **Files:** raw R-JPEG + embedded EXIF/XMP (GPS, altitude, gimbal angles; S), flight log export, Atlas report if any.
- One `flight_log.csv` row per flight; one `site_meta.json` per site.

### 2.4 Ground tests on end-of-life modules (no EL rig, no or cheap kit)
WattCycle's recycling stream (ReVive) implies end-of-life modules on site (R: capture_plan §1.1; counts unconfirmed). On a rack in sun, using the drone camera hovering low or a handheld / phone IR camera (S):

| Test | What | Gives | Kit / cost | Source |
|---|---|---|---|---|
| W08 operating-point differential IR | each module at open circuit, then near MPP (resistor or DC load), then short circuit; 2 frames each, irradiance logged | MPP-minus-OC map: regions that do not cool at MPP are candidate inactive areas (S, energy balance); illuminated vs dark IR give complementary results (R: doi:10.3390/s20164395) | MC4 leads, shorting lead, load (unconfirmed cost) | ideas W08 |
| W09 single-cell shading | cover one cell with an opaque card at short circuit for ≤ 1 to 2 min; watch ΔT | reverse-bias hotspot / shunt labels without a supply; the IEC 61215-2 MQT 09 idea (R: TOC, capture_plan §2) | card, timer | ideas W09; R: doi:10.1016/j.egypro.2014.08.097 (per ideas) |
| W10 close-range IR | 6 to 8 m hover or handheld at 1 to 2 m on flagged modules | sub-cell structure of disconnections | none | ideas W10 |
| W11 UV fluorescence at night | 365 nm torch, phone or Pi camera, fiducials on the frame | crack lines in aged encapsulant, crack chronology; 250 modules/h by hand (R: doi:10.1109/jphotov.2019.2961781) | torch ₹1,790 (old price) to ₹4,522 (capture_plan §3) | ideas W11 |
| W12 / W13 RGB + soiling check | RGB photos; re-image flagged modules after cleaning | snail trails as a crack proxy (R via ideas: doi:10.1109/jphotov.2014.2330495); drop soiling-only flags | phone | ideas W12, W13 |

Safety: capture_plan §7 applies (DC up to Isc, connect / disconnect at open circuit, hotspots, broken glass, UV glasses). Shading only on sacrificial modules (S).

### 2.5 Analysis we can run now (desk, CPU; S unless tagged)
1. **W05 + W03 on public A3 first** (DTU set, already approved for pick 1; E: `om_2026-11-04_decisions.md` (1)): fit ΔT vs irradiance per defect class; build physics-rule scores (hot cell, hot substring, elongated warm pattern); per-class AUROC. This is pick 1 step 2 (E: `synth/top3.md`).
2. **W02 module ID map** on the first WattCycle flight: detect modules, assign stable IDs, re-identify on F3; target ≥ 98% matched (ideas threshold, S). The same homography code as capture_plan §4.
3. **W01 pre-registered EL queue:** after one flight, freeze `w01_prereg.md` (md5-logged) listing 20 to 40 modules for the first EL session:
   - the top IR-flagged modules;
   - a random audit sample;
   - all reachable half-cut modules;
   - written predictions, e.g. "IR-flagged modules hold ≥ 60% of E-PF-predicted inactive area".

   The first EL session, from the low-cost camera in §3 or WattCycle's rig later, is then a prospective test and a fresh unseen-module set nobody has tuned on (ideas W01).
4. **W07 IR → expected-EL mapper** on public A1 / A2 / A3, applied to WattCycle flights as one more pre-registered prediction (ideas W07).

### 2.6 What to ask WattCycle to share (S)
- Raw radiometric R-JPEGs (not only palette JPEGs or Atlas screenshots) of past and new flights, with flight logs and irradiance.
- Site layouts / string maps / module datasheets; which sites have half-cut modules.
- Any follow-up truth on flagged modules: replacements, I-V, EL by others, warranty claims. Even a few dozen labelled anomalies give real labels (S).
- Atlas exports of anomaly lists per flight.
- Permission terms (thesis, paper, derivative release).

## 3. (b) Getting EL sooner: options, costs, lead times

### 3.1 What any EL capture needs
- Silicon EL light sits at ~1,100 to 1,200 nm (E: `handbook/02_domain_primer_EL_and_defects.md` §3). A Si sensor still works if it has **no IR-cut filter**, long exposures, darkness and dark-frame subtraction.
  - Li 2024 used a cooled Si CCD with an 850 nm long-pass filter (R: doi:10.1016/j.solener.2024.112704 §2.2).
  - Ciocia et al. built a low-cost Si-sensor EL camera for lab and field use (R: doi:10.1109/pvsc40753.2019.8980711).
  - Outdoor EL with Si vs InGaAs detectors has been compared quantitatively (R: doi:10.1515/zna-2019-0025).
  - IEC TS 60904-13 covers frame subtraction and 0.1 x Isc imaging (R: preview TOC, capture_plan §2).
- A forward-bias supply: the 300 W OWON gives 0.1 x Isc easily and ~0.4 to 0.75 x Isc whole-module (S; capture_plan §5.1).
- Resolution target ~0.3 to 0.45 mm/px (~350 to 500 px per cell edge) to resemble BenchmarkEL (~0.3 mm/px, E: `handbook/13_problems_pitfalls_open_issues.md` l.175).
- **Quality caveat (S):** uncooled consumer Si sensors have low QE at 1,100 nm (no wavelength-resolved figure found; unconfirmed) and more noise than a cooled EL camera. Expect usable crack and inactive contrast at higher current with stacked exposures, but treat these images as a WattCycle-domain *test* set, not training data, until quality is measured.

### 3.2 Options
| # | Option | Kit and cost | Lead time | Resolution on a 1.65 m module | Pros / cons | Tag / sources |
|---|---|---|---|---|---|---|
| A | **Raspberry Pi HQ camera, IR filter removed** | HQ camera (Sony IMX477, 4056 x 3040, 1.55 µm, C/CS mount, max exposure 670.74 s) ₹4,990 (Robocraze; not re-verified by check, 429); Pi 5 4 GB ₹5,799 (Robocraze, sold out; not re-verified) / ₹5,085 ex GST (SRK, out of stock) / "₹5,500 to 6,200" typical (ThinkRobotics blog); C/CS lens 6 to 8 mm (price unconfirmed); 850 nm long-pass (ZWO 1.25" £25 FLO / US$37.90 Astroshop; mounting adapter unconfirmed); OWON 300 W ₹12,099 | days to ~2 weeks (Indian sellers; Pi 5 stock uncertain) | ~0.41 mm/px (4056 px), ~380 px per 156 mm cell (S) | cheapest real-sensor route; long exposures; scriptable capture (raw). IR filter removal is irreversible and voids the warranty (R). NIR QE unconfirmed | R: https://www.raspberrypi.com/documentation/accessories/camera.html ; https://robocraze.com/products/raspberry-pi-high-quality-camera-with-interchangeable-lens-base ; https://robocraze.com/products/raspberry-pi-5-4gb ; https://thinkrobotics.com/blogs/product-reviews-buying-guides/raspberry-pi-5-price-india-complete-cost-analysis-and-buying-guide ; https://agenaastro.com/zwo-1-25-inch-850nm-ir-pass-filter.html ; filter prices: https://www.astroshop.eu/filters/pass-filters/15_15_35/a,Zubehoer.Leistung.Fassung=1%2C25%22 |
| A' | Pi Camera Module 3 **NoIR** | ₹2,919 (Robocraze; not re-verified by check, 429); IMX708, 4608 x 2592, 1.4 µm, max exposure 112 s, fixed lens | days | ~0.36 mm/px if the module fills the frame (S) | cheapest; a 1-hour feasibility test only (fixed wide lens, no filter thread; S) | R: https://robocraze.com/products/raspberry-pi-camera-module-3-noir ; Pi docs above |
| B | **ZWO ASI678MM** mono astro camera (no Bayer; vendor claims "outstanding near-infrared response") | ₹62,145 incl. GST and import duty (Tanotis); US$359 to 399 abroad; + lens + ZWO 850 nm filter. ASI585MM ₹82,760 (Tanotis; its spec table says "colour", conflict) | Tanotis stock unconfirmed (page 429 on re-check) | 3840 px → ~0.43 mm/px (S) | better sensitivity and astro capture software (S); USB3; still uncooled | R: https://www.tanotis.com/products/zwo-asi678mm-usb-3-0-monochrome-astronomy-camera (via search snippet) ; https://astronomics.com/collections/zwo-summer-savings?page=3 ; https://agenaastro.com/zwo-asi678mm-cmos-monochrome-astronomy-camera.html ; https://www.tanotis.com/collections/vendors/products/zwo-asi585mm-usb-3-0-monochrome-astronomy-camera |
| B' | Cooled mono astro (ZWO ASI533MM Pro) | ~€1,390 / US$1,430 (Astroshop); India price not found | import, weeks (S) | 3008 px → ~0.55 mm/px (sensor format from vendor; S) | cooled = cleaner long exposures | R: https://www.astroshop.eu/astrophotography/15_35/a,Zubehoer.Allgemein.Serie=ASI+533/a,Zubehoer.Leistung.Anschluss-Teleskopseitig=1%2C25%22+%26+2%22+%26+T2 ; https://bintel.com.au/products/zwo-asi533mm-pro-cooled-mono-camera |
| C | Full-spectrum converted DSLR / mirrorless | conversion US$199 to 275 (US), £437 (UK); no Indian service found; + body | weeks (international shipping), so likely misses 3 to 4 weeks | 24 MP → ~0.28 mm/px (S) | best resolution; borrow route only: someone at IIT Mandi may already own an astro-modified camera (S; ask) | R: capture_plan §3; https://repair.wexphotovideo.com/service/full-spectrum-conversion/ |
| D | CCTV day / night camera with switchable IR-cut | low (unconfirmed) | days | 2 to 8 MP | auto exposure and video compression make quantitative EL hard (S) | S |
| E | **Ship 3 to 5 modules to NISE Gurugram** | NISE lists "Electroluminescence Test: test per sample of PV module" and STC performance; EL fee not public. A search snippet of NISE order form 1.1 gave STC of field-deployed modules ₹4,550, visual inspection ₹1,300, insulation ₹800 per sample, ex GST (form PDF now 404) | ordering via NISE login / order forms; turnaround unconfirmed | lab-grade (unconfirmed camera) | reference-quality EL **and I-V** on the same modules (power-loss data); costs shipping + fees; Gurugram ~400+ km by road (S) | R: https://testing.nise.res.in/testing-service-detail/testing-of-solar-pv-modules-YWYqWR ; https://testing.nise.res.in/uploads/order_form/pvtf_1.1.pdf (snippet only) |
| F | Mobile PV test lab visit (flash + EL + IR) | price not public | unconfirmed | lab-grade | Mahindra Susten (2017), DNV GL (2018) and UL (2019) launched mobile labs in India; current service unconfirmed; mobilisation cost likely dominates for 5 to 20 modules (S) | R: https://www.electronicsb2b.com/?p=66600 ; https://www.dnv.com/news/2018/dnv-gl-s-on-site-solar-lab-brings-advanced-and-reliable-pv-testing-to-the-field-in-india-135116/ ; https://www.energetica-india.net/news/ul-launches-first-mobile-pv-test-laboratory-in-india- |
| G | IIT Bombay (Rajesh Gupta's group) | research collaboration, not a service (S) | slow (S) | lab-grade + lock-in | the module EL + DLIT experts (R: doi:10.1088/1361-6501/ab0265, doi:10.1016/j.seja.2023.100049; affiliation per check P-12). Far for shipping (S) | R + S |
| H | NIT Hamirpur (~nearby) | inventory PDFs list teaching kits (Ecosence PV kit, solar-cell I-V setups), DC regulated supply, meters, small modules; no EL or IR camera listed | n/a | n/a | possibly borrow a DC supply (rating unknown) | R: https://www.nith.ac.in/uploads/topics/solar-photovoltaic-lab16493145379132.pdf ; https://www.nith.ac.in/uploads/topics/spvlab16548356722733.pdf |
| I | IIT Ropar, PEC Chandigarh, other MNRE / BIS labs in the north | nothing found publicly on EL / IR facilities | n/a | n/a | ask Om; the BIS recognised-lab list was not found for the north (R: search found only NISE as a northern module lab, secondary) | S / unconfirmed |
| J | WattCycle's drone for EL | drone EL needs a SWIR camera (~€10k to 15k on a ~€10k drone) and back-powering at night (or special inverters by day) | n/a | n/a | the Mavic 3T-class RGB cameras are visible-light cameras with IR-cut filters (S), so **no drone EL** from their current kit. Our ground Si camera can do night EL of single modules in the field with the 300 W supply (S) | R: DTU slide 2 (same URL as §2.1); aerial EL review doi:10.1016/j.solmat.2024.113210 |
| K | 300 W OWON supply | ₹12,099 | 1 to 5 days (one Bengaluru seller) | n/a | 0.1 x Isc EL fine; ~0.4 to 0.75 x Isc whole module; or full Isc per substring via the jbox (capture_plan §5.1) | R: capture_plan §3, §5.1 |

### 3.3 Pick: cheapest path to some WattCycle-domain EL in 3 to 4 weeks (S)
**Path 1 (do first):** Option A + K. Raspberry Pi HQ camera with the IR filter removed, Pi 5, 6 to 8 mm C/CS lens, 850 nm long-pass, OWON 300 W.
- **Cost:** about ₹25k for camera + Pi + supply, plus lens and filter (unconfirmed, small).
- **W1 (by 10 Nov):** order after Om's go (Indian sellers). Check that the Pi 5 is in stock; any Pi 4 / 5 works (S).
- **W2 (11 to 17 Nov): bench test on one healthy module, then one cracked module.** At night or in a dark shed:
  - EL at 0.1 x Isc and at the OWON maximum;
  - exposures 5 s to 120 s;
  - 10 dark frames + 10 signal frames, stacked.

  Success (S, pre-stated): crack lines and inactive regions visible on the cracked module at ≤ 120 s per frame after stacking.
- **W3 to W4 (18 Nov to 1 Dec): first WattCycle EL night.** Run the W01 queue modules that are on the ground (end-of-life stock), plus half-cut modules. Use capture_plan §5 P0 with the thermal step done by phone IR or the drone camera if possible (Q7).
- **If Path 1 fails the bench test:** Option B (ASI678MM, ₹62k) uses the same lens / filter / supply. It adds ~1 to 2 weeks (S).

**Path 2 (in parallel, reference quality):** Option E. WattCycle (or we) ship 3 to 5 W01 modules to NISE for EL + STC I-V.
- It gives a lab-grade EL to calibrate Path 1 images against, and I-V for power loss.
- Fee and turnaround are unconfirmed (Q20).

**Not in 3 to 4 weeks (S):** C (import), F (unconfirmed availability), G (collaboration time), J (no SWIR camera).

**Expected yield by week 4 (S):**
- 5 to 15 end-of-life modules with low-cost EL + phone / drone IR + UVF + RGB;
- 1 to 3 site flights with an ID map and a frozen W01 queue;
- possibly NISE EL + I-V on 3 to 5 modules.

That is enough to measure whether IR / UVF separate scuff-like streaks from real cracks on WattCycle modules (capture_plan §8) months before WattCycle's own rig.

## 4. (c) Updated questions for WattCycle (for Om; agents made no contact)

**Drone and camera**
1. Drone and thermal camera model (e.g. Mavic 3T / 3TA / M30T / M4T / other), firmware. Is radiometric R-JPEG enabled? Are raw R-JPEGs kept, or only palette JPEGs / Atlas outputs? What emissivity and distance settings do you use?
2. Does the drone have RGB? Any NIR or multispectral camera?
3. Usual altitude / GSD and overlap. Can you fly a ~10 m pass over chosen rows, 6 to 8 m hovers over ~20 flagged modules, and a repeat pass 30 to 60 min later?

**Flights and sites**
4. Which sites do you fly, how often, and since when? How many past flights are archived?
5. Module types per site (make / model, full vs **half-cut**, mono / multi, cells per module, age).
6. Do you log plane-of-array irradiance (pyranometer or SCADA), wind, and plant state per flight? Do you keep flight logs?
7. Is there a handheld or phone thermal camera, or can the drone's thermal camera be used on the ground (props off) for indoor dark thermography?
8. Do you follow up flagged anomalies (replacement, I-V, EL by a contractor, warranty claims)? Any records we could use as labels?
9. Can modules be re-identified across flights (string maps, orthomosaics, serial lists)?

**End-of-life modules (ReVive)**
10. How many end-of-life modules are on site now, and of which types and ages? Any half-cut?
11. May we test some in sun (open circuit / load / short circuit), shade single cells on 2 to 3 sacrificial ones, and image them at night with a UV torch and a low-cost EL camera?
12. Is there a dark shed or room and a module rack? Is there mains power for a 300 W supply at night?

**EL**
13. Which EL rig is coming, from whom, and when? Camera type, resolution, filter, raw export? Could we suggest a spec: ≥ 0.3 to 0.45 mm/px on a module, 16-bit raw, 850 nm long-pass, current control 0.1 to 1.0 x Isc?
14. Would you be willing to try a low-cost EL camera (about ₹25k, Path 1) with us before the rig arrives?
15. Do you have any DC power supply (V, A, W)? Who can supervise the electrical work (trained person), and is there an SOP for energising used modules?
16. Could 3 to 5 modules be shipped to NISE Gurugram for EL + STC I-V? Who would pay test fees and freight?

**People, data, money**
17. Contact person for flights and for the ground tests.
18. Data terms: may the thesis and a paper use the IR, UVF and EL images? May a derived dataset be released (licence)?
19. Funding: Path 1 kit (~₹25k + lens / filter), fallback camera (~₹62k), NISE fees, UV torch, phone IR (~₹20k to ₹30k).
20. For IIT Mandi or Om directly: does anyone at IIT Mandi own an astro-modified / full-spectrum camera, a ZWO-type mono camera, a handheld IR camera, or a ≥ 60 V / ≥ 10 A supply we could borrow? Does NISE's EL fee schedule apply to research customers, and what is its turnaround?

## 5. Safety deltas (S, on top of capture_plan §7)
- **Night work:** head torches (red light during EL exposures), two people, cables taped down, first-aid kit.
- **Field DC:** one module at a time on the 300 W supply. Never energise strings. Connect only at open circuit.
- **Drone:** WattCycle's pilots fly under their own permissions; low hovers (6 to 8 m) only with a clear area and no one under the drone. India's drone rules apply (unconfirmed details).
- **Shading test:** time-limited (≤ 1 to 2 min per cell), sacrificial modules only, IR watched live, stop above a set temperature.

## 6. Sources
- **Research MCP ids:**
  - doi:10.1051/epjpv/2025020 (DTU drone IR, irradiance / altitude);
  - doi:10.1016/j.solmat.2024.113210 (aerial EL review);
  - doi:10.1515/zna-2019-0025 (outdoor EL, camera choice);
  - doi:10.1109/pvsc40753.2019.8980711 (low-cost Si EL camera);
  - doi:10.1016/j.solener.2024.112704 (EL + IR protocol);
  - doi:10.3390/s20164395 (illuminated vs dark IR);
  - doi:10.1109/jphotov.2019.2961781 (UVF review);
  - doi:10.1088/1361-6501/ab0265, doi:10.1016/j.seja.2023.100049 (IIT Bombay group).
  - ideas' ids are cited in `ideas/drone_only.md` §4.
- **Slides:** Spataru (DTU), "Frame conditions for thermography inspections of photovoltaic plants", IEA PVPS Task 13 meeting, ISFH 2025: https://iea-pvps.org/wp-content/uploads/2025/08/07_S.-Spataru_Framing-Drone-IRT-Conditions.pdf (read slides 2 to 14).
- **Web:** inline in §2.2 and §3.2.
- **Project files (E):** `om_2026-11-04_decisions.md`; `ideas/drone_only.md`; `capture/capture_plan.md` v1.2; `synth/top3.md`; `handbook/02` §3; `handbook/13` l.175.

## 7. Unconfirmed / open
- WattCycle's drone model, radiometric archive, RGB, ground use of its thermal camera.
- NIR QE of IMX477 / IMX678 at 1,100 to 1,200 nm (no figure found; the bench test decides).
- Lens and filter-adapter prices; Pi 5 stock; Tanotis stock for ASI678MM.
- NISE EL fee, turnaround, research-customer terms.
- Current availability of mobile EL labs in north India.
- IEC TS 62446-3 text itself (wind, angle, GSD read via slides and vendor summaries only).
- Any EL / IR equipment at IIT Ropar, PEC, other northern labs.

## 8. Short lists for synth (S unless tagged; weeks as in the header)

### 8.1 Drone-only actions, ranked by value per cost for W1 to W7
| Rank | Action (ideas id) | When | Cost (dev d / field d / ₹) | Data | First signal | Kill line |
|---|---|---|---|---|---|---|
| 1 | Physics-rule IR scores + irradiance normalisation on public A3 (W03 + W05) | W1 to W2 | 3 to 5 / 0 / 0 | A3 (approved; E: `om_2026-11-04_decisions.md` (1)) | per-defect-class AUROC; ΔT-vs-irradiance slope per class | rules unusable for triage if disconnection or diode AUROC < 0.8 (ideas W03) |
| 2 | Send the §4 questions; get raw R-JPEG archive + logs | W1 | 0 / 0 / 0 | WattCycle archive | radiometric raw exists, plus irradiance logs | if only palette JPEG / Atlas output exists, past flights drop out; use new flights only |
| 3 | First site visit: F1 survey, F2 ~10 m cell pass, F3 repeat, F4 hovers; ID map + half-cut survey (W02, W06, W10) | W2 to W3 | 2 to 3 / 1 / 0 | new flights | ID match rate F1 vs F3; test-retest ρ of cell ΔT; count of half-cut modules | IDs: < 90% matched → physical tags needed (ideas W02); change detection dropped if ρ < 0.7 (ideas W06) |
| 4 | Ground tests on end-of-life modules, same visit (W08 OC/MPP/SC, W09 shading, W11 night UVF, W12 RGB) | W2 to W3 | 2 / 0.5 to 1 + 1 night / ~₹2k to ₹5k (torch) + leads (unconfirmed) | 5 to 15 end-of-life modules | regions that do not cool at MPP; UVF crack lines; shaded-cell ΔT | W08: MPP-OC below noise on every module; W11: no UVF lines on aged modules; W09: no cell > median + 10 K (ideas thresholds) |
| 5 | Freeze the pre-registered EL queue + predictions (W01) | W3 to W4 | 2 / 0 / 0 | flight scores + ID map | md5-frozen `w01_prereg.md` with 20 to 40 modules | void if modules cannot be re-found (rank 3 fails) |
| 6 | IR → expected-EL mapper on public A1 / A2 / A3 (W07) | W3 to W5 | 4 / 0 / 0 | public pairs (approved subsets) | Spearman of module IR score vs EL dark-area fraction | Spearman < 0.5 on A3 held-out (ideas W07) |
| 7 | Low-cost EL session on the W01 queue modules on the ground; read predictions once (W01 payoff; §3.3 Path 1) | W4 to W5 | 1 / 1 night / Path 1 kit | Path 1 EL + same-day IR / UVF | pre-registered numbers read once | Path 1 bench test fails (then Option B, +1 to 2 weeks) |
| 8 | Public-trained IR model applied to WattCycle flights (W04) | W5 to W6 | 4 / 0 / 0 (+ GPU-h 0 to 3 only with OK) | A3 + other public IR (D1 / PVF-10 need download OKs) | agreement with rank-1 rules on WattCycle | κ < 0.6 and a 50-flag spot check < 50% real (ideas W04) |
| 9 | Soiling filter: re-image flagged modules after cleaning (W13) | when WattCycle cleans | 1 / 0.5 / 0 | WattCycle IR | share of flags that were soiling | < 5% → drop the step (ideas W13) |
| 10 | Natural-transient IR video (W14) | optional, W5+ | 3 / 0.5 / 0 | hover video | time-constant maps | no structure beyond noise (ideas W14, low prior) |

### 8.2 "EL sooner" options with dates
| Option | Earliest EL (synth weeks) | Cost | Main dependency | Tag |
|---|---|---|---|---|
| **Path 1: Pi HQ camera (IR filter removed) + Pi 5 + lens + 850 nm LP + OWON 300 W** | kit W2; bench test end W2; first WattCycle EL night W3 to W4 (18 Nov to 1 Dec) | ~₹25k + lens / filter (unconfirmed) | Om's go in W1; Pi 5 stock; NIR QE (bench test decides) | R prices §3.2; S dates |
| Borrowed astro-modified / full-spectrum camera at IIT Mandi | W2 to W3 if one exists | ₹0 + filter | someone owns one (unknown, Q20) | S |
| Option B: ZWO ASI678MM | W4 to W5 (Path 1 fails → +1 to 2 weeks) | ₹62,145 + lens / filter | Tanotis stock (unconfirmed) | R price; S dates |
| NISE Gurugram EL (+ STC I-V) on 3 to 5 shipped modules | results ~W4 to W6 (turnaround unconfirmed) | EL fee not public; STC ₹4,550 / module (snippet); freight | WattCycle agrees to ship; NISE order (Q16, Q20) | R service listed; S dates |
| Converted DSLR / mirrorless (import) | W6 or later | US$199 to 275 conversion + body + freight | no Indian service found | R price; S dates |
| 300 W OWON fallback supply (part of Path 1) | arrives W1 to W2 (1 to 5 days, not re-verified) | ₹12,099 | none | R (not re-verified) |
| Phone IR for dark forward-bias thermography beside Path 1 EL | W2 | ₹20k to ₹30k | budget (Q19) | R prices capture_plan §3 |
| WattCycle's own EL rig | ~Jan to Feb 2027 (2 to 3 months from 4 Nov) | WattCycle's | WattCycle (E: Om's decisions) | E |
| Drone EL, mobile labs, IIT Bombay | not within W7 | high / unknown | SWIR camera; availability; collaboration | R / S |

### 8.3 Question list
§4 is the deduped, numbered list (Q1 to Q20) and can replace `synth/SUMMARY.md` §4 W1 to W12. It includes ideas' 8 drone-only questions (`ideas/drone_only.md` §3):
- radiometric export → Q1;
- RGB → Q2;
- low passes and repeat flights → Q3;
- irradiance logs → Q6;
- sites, half-cut modules and re-identification → Q5, Q9;
- sun tests and night UVF on end-of-life modules → Q11;
- data terms → Q18.
