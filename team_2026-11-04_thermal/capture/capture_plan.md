# Capture plan: paired EL + thermal on a few modules at WattCycle / IIT Mandi (Om's question 3)

Owner: capture. Date: 4 Nov 2026. Status: v1.3 (v1.3: check re-check nits R-1, S-24; v1.1: §5.1 lead time; v1.2: check pass-1 fixes C-2, C-4, C-5, C-12, C-13, P-7, P-12, P-20 and MARKs applied), desk study (no contact, no downloads, no GPU).
Tags: **E** = measured in our files (path); **R** = from a source (Research MCP id or URL); **S** = my reasoning or speculation. "unconfirmed" = I could not verify it. Prices are listing prices seen on 4 Nov 2026; they change, and GST status is as the listing states.

## 0. Summary

Yes, a paired EL + thermal capture looks feasible and cheap, and the partner may be better placed than we thought. WattCycle Sustainable Solutions Pvt. Ltd. was founded in June 2025 by an IIT Mandi associate professor, has its registered office at Kamand, Mandi, and describes itself as a pilot-scale PV recycling startup. Its site lists drone thermal + RGB health monitoring, a digital-twin platform (Atlas) and a recycling service (ReVive) (R, §1). Its Atlas manual calls Atlas "a comprehensive solar asset management platform" (R, check C-5), which matches our handbook's "solar asset-management company"; Om should still confirm the contact. It likely has a stream of end-of-life modules and offers thermal drone inspections (R; whether real drone IR archives exist is not shown, since the site's Atlas app runs on demo seed data). Whether it owns an EL rig is unconfirmed. Minimal pilot (P0, about 1 day, about ₹45k to ₹55k of new kit if an EL rig exists): 5 to 6 recycler modules (at least 2 half-cut, 2 with scuff-like EL streaks, 1 healthy). Each module stays on one mount while we take EL at two currents, then dark thermography under the same forward bias with a phone-attachment microbolometer (256 x 192), then a UV-fluorescence photo and an RGB photo. Aluminium-tape corner fiducials plus a per-module homography align the images to cell level. No hand labels are needed (S, §5). Extended plan (P1, 4 to 5 days, 15 to 20 modules): a bias sweep, a 640 x 480 or tiled camera, low-cost lock-in thermography with a switched supply, reverse-bias hotspot imaging on 2 to 3 sacrificial modules, outdoor and drone IR of the same modules, and the modules' I-V data (S, §6). The point for our open problem: an EL-dark streak with no thermal or UVF signature is a candidate scuff, while EL-dark plus a thermal anomaly is a candidate crack or inactive area. That gives an automatic weak label exactly where E1 fails (scuff + half-cut), plus a WattCycle-domain unseen-module set (S). IIT Mandi's central facility list shows no IR camera, EL rig or solar simulator (R); other labs are unconfirmed.

## 1. What we found: WattCycle and IIT Mandi

### 1.1 WattCycle
| Claim | Tag | Source |
|---|---|---|
| WattCycle Sustainable Solutions Pvt. Ltd., founder and principal investigator Dr Satvasheel Powar, June 2025 to present; "India's first pilot-scale photovoltaic recycling initiative"; "DPIIT-recognised deeptech startup"; ₹10 crore CSR grant from GIC Re; "advanced materials recovery" for end-of-life panels. "DPIIT-recognised" and "June 2025 to present" appear in the CV PDF only, not on the profile page (check C-2) | R | Powar's CV (AIMA fellowship, Mar 2026), https://is4ie.org/mediafiles/cv/69c423258f4e7.pdf ; profile https://is4ie.org/members/5321 |
| Powar: Associate Professor, School of Mechanical and Materials Engineering, IIT Mandi (SJVN Chair); established the Energy Engineering Laboratory (2015 to 2022); research areas include solar PV and circular economy | R | CV above; IIT Mandi IPTT team page as indexed by search (https://iitmandi.ac.in/sric/iptt/our-team.php, 404 when fetched on 4 Nov) |
| Company incorporated 17 Jun 2025, active; registered address Village Salgi, P O Kamand, Mandi, HP 175075; directors Priyanka Kajal, Atul Dhar; MCA class "business activities n.e.c." | R | https://tracxn.com/d/legal-entities/india/wattcycle-sustainable-solutions-private-limited/__unHpXEMyS-nJu_ZSEKYWwHwJ8nu4vQrSV4hmBg_pKxY |
| Website wattcycle.ai: "Deeptech for Solar Performance and Circularity"; **WattCycle Atlas** (digital twin for plants and storage: performance monitoring, O&M workflows, module batch tracking, end-of-life signals); drone service: "Thermal and RGB drone inspections for hotspot detection, fault identification, soiling maps, and structural checks"; **ReVive Solar** (PV recycling); GIC Re CSR; "Incubated at IIT Mandi Catalyst"; Himachal Pradesh | R (verified by check from the site's own JS bundle text, wattcycle.ai/assets/index-*.js; check/factcheck.md C-4) | https://wattcycle.ai/ |
| Same postal area as the IIT Mandi campus (Kamand, 175075), so logistics should be short | S | inference from the address above |
| "WattCycle" is also an unrelated Shenzhen LiFePO4 battery brand (wattcycle.com) | R | https://ca.wattcycle.com/ , https://wattcycle.com.cn/en/about-us/ |
| **Name match, largely resolved:** local docs call WattCycle "a solar asset-management company" (`handbook/01_project_overview_and_scope.md` l.18) and say no WattCycle data is available (`handbook/02_domain_primer_EL_and_defects.md` §9). The site's Atlas manual says "WattCycle Atlas is a comprehensive solar asset management platform", menu "Asset Management: Plants, module batches, inventory, recycling" (R: JS bundle, check C-5). So the handbook's wording fits this company; Om should still confirm the contact. **Caveat:** the Atlas app in the bundle runs on demo seed data ("Defect zones reflect drone inspection seed data"; R: check C-5), so the site does not show that real drone IR archives exist | E (paths) + R + S | ask Om (Q1, Q10) |
| What equipment this implies: a recycler or reuse grader typically runs I-V, EL and wet-leakage tests to sort reuse vs recycle (R: pv-magazine 2026, https://www.pv-magazine.com/2026/08/19/i-v-screening-for-decommissioned-pv-modules/ ; an Austrian reuse line runs EL first, https://taiyangnews.info/technology/2nd-cycle-evaluates-used-pv-modules-for-upcycling ). So WattCycle *may* own or plan an EL rig and a flash tester. **Unconfirmed**: nothing public lists WattCycle's lab equipment | R for industry practice, S for WattCycle | Q2 to Q4 |
| A drone thermal payload is implied by the drone service (R); model and resolution unconfirmed | R + S | Q3 |

### 1.2 IIT Mandi
| Claim | Tag | Source |
|---|---|---|
| AMRC (central facility) lists ~36 instruments (SEM, TEM, XRD, XPS, NMR, Raman/PL **spectrometer**, UV-Vis-NIR, etc.); no IR camera, thermography, EL, PL imaging, solar simulator, source meter or InGaAs camera is listed | R | https://amrc.iitmandi.ac.in/exbook.php ; https://scs.iitmandi.ac.in/amrc.html |
| Old School of Engineering pages list a "Solar Thermal Utilization and Thermal Energy Storage Lab", an "Energy Engineering Lab" (teaching) and a "Thermo-Fluids Laboratory"; equipment not listed; both pages returned 404 on 4 Nov | R (search index only) | https://research.iitmandi.ac.in/main/Schools/SE/labs.php ; .../solar_thermal.php |
| CAIR has a "Drone Lab" page (no equipment text indexed); iHub runs agricultural drone pilot training | R | https://cair.iitmandi.ac.in/dronelab.php ; https://news.careers360.com/iit-mandi-showcases-drone-didi-programme-success-president-droupadi-murmu-kaushal-bhavan/amp |
| A campus solar-potential study exists (Arka 360); no commissioned campus PV plant capacity found | R | https://www.casestudies.com/company/arka-360/case-study/solar-potential-estimation-at-iit-mandi |
| Any thermal camera, EL rig, PV module rack or DC supply at IIT Mandi | **unconfirmed** (not found publicly) | Q12, Q13 |
| Nearest public EL + lock-in module work in India: Roy and Gupta 2019 (EL + DLIT shunt severity on commercial modules), Kumar and Gupta 2024 (shunt review), Puranik et al. 2023 (quantitative module EL review). All three are from Rajesh Gupta's group at **IIT Bombay** (R: OpenAlex authorships, per check P-12). The same group did inverse-IR (forward-bias) thermography of PID-shunted modules and found steady state with medium input current most suitable for quantitative work (R: doi:10.1016/j.seja.2023.100049). A concrete P2 lead in India for lock-in and IR if WattCycle cannot do it (S) | R (ids) + S | doi:10.1088/1361-6501/ab0265 ; doi:10.1016/j.solmat.2024.113121 ; doi:10.1016/j.solener.2023.111994 ; doi:10.1016/j.seja.2023.100049 |

## 2. Imaging modes and what each shows for our classes

Our classes: crack (14), inactive (11), scuff (E-SCDD class 25, not in our 24-class scheme; `handbook/17_escdd_dataset_audit.md` §5.11), half-cut cells (geometry, not a class), shunts and hotspots (not labelled in BenchmarkEL).

**Why scuff + half-cut matter (E):** 75% of missed E1 crack px sit on scuff + half-cut cells (README, project context). The 4 largest E1 half-cut crack cells carry 2.5k to 4.6k px scuff streaks with crack GT branching off them (`team_2026-10-29_features/spec_b3_scuff.md` §1). Our train masks call 649 scuff px "crack" (same file). Agent raters failed the scuff gate (sens 1/8; `SESSION_RECORD_2026-11-01_to_11-03.md` §0). EL alone does not separate scuff from crack well.

| Mode | How | Crack | Inactive | Scuff | Half-cut | Shunts | Hotspots | Cost / effort |
|---|---|---|---|---|---|---|---|---|
| **Forward-bias EL** (baseline) | Dark room; DC forward current; Si or InGaAs camera at ~1,100 to 1,200 nm (`handbook/02` §3). IEC TS 60904-13 uses 0.1 x Isc for crack quantification (R: TOC figure captions, VDE preview of IEC TS 60904-13:2018) ; a search summary says its reference method uses 0.1 and 1.0 x Isc (R, weak: summary of search results incl. https://proceedings.ises.org/conference/swc2025/papers/swc2025-0207-Alc%C3%A2ntaraNeto.pdf , attribution unconfirmed); Li 2024 imaged at 0.1 to 1.0 x Isc (R: doi:10.1016/j.solener.2024.112704) | dark line (E: our labels) | fully dark region (E) | dark streak; looks crack-like (E, above) | dark cut line and spacing (E: H36 cut-line / spacing false alarms, `SESSION_RECORD_2026-11-01_to_11-03.md` §5 and §9) | dark at low current, but hard to tell from other defects (R: doi:10.1088/1361-6501/ab0265) | indirect | needs a rig; WattCycle may have one (unconfirmed) |
| **Steady-state dark thermography under forward bias** | Same mount, same bias, LWIR camera; image after ~1 min and after ~10 min at Isc. Li et al. 2024 took EL then IR at each bias in a dark room, IR after 10 min stabilisation (R: doi:10.1016/j.solener.2024.112704 §2.2, §4) | open or resistive cracks heat at current-crowding points; one whole-cell hotspot with no EL signature was attributed to microcracks (R: same paper §4) | Li 2024 cites steady-state IR as able to map inactive regions via thermal gradients (R: §2.2); physics: no current reaches the disconnected part, so it should stay cooler than its active neighbours (S) | gridline breakage, metallization corrosion and "scratches" were EL-only or poorly correlated with IR (R: §4). So a cosmetic scuff should have **no** thermal signature (S): this is the separating signal | the cut line carries no current; expect no anomaly (S) | hot (R: DLIT literature; doi:10.1088/1361-6501/ab0265) | resistive solder bonds and ribbons heat and "bloom" by lateral heat flow (R: Li 2024 §3) | cheap: microbolometer + the EL supply; heat blurs features at mm scale (S) |
| **Lock-in thermography (DLIT)** | Square-wave the current (switched supply), stream camera frames, demodulate amplitude and phase. Suppresses lateral heat spread and noise (S, standard LIT rationale) | crack edges that shunt; failed solder joints give point-like "asymmetric doublet" heating (R: doi:10.1109/jphotov.2020.3003781) | weaker than steady state at sub-cell scale (S) | as steady state, plus better SNR to *prove* "no signal" (S) | as steady state (S) | the classic LIT target; EL + DLIT give shunt severity on modules (R: doi:10.1088/1361-6501/ab0265; thin film: doi:10.1016/j.solmat.2014.09.020) | yes | needs raw radiometric streaming + sync; free software (S); commercial LIT systems price unconfirmed |
| **Reverse-bias hotspot imaging** | Cannot reverse-bias cells through the module terminals: the bypass diodes conduct (S, general background). Options: (a) shade one cell under sun or a lamp with the module shorted (the IEC 61215-2 MQT 09 hot-spot test idea; R: TOC clause 4.9, https://standards.iteh.ai/catalog/standards/iec/be1602da-b7b1-42f4-9e94-9e0700a71130/iec-61215-2-2021 ; details unconfirmed); (b) on a sacrificial recycler module, open the jbox, isolate a diode, reverse-bias one substring with a hard current limit | breakdown sites often sit at cracks and defects (S); pre-breakdown sites emit visible light and heat (R: doi:10.1063/1.3256199) | little (S) | none expected (S) | none (S) | yes | yes; breakdown types near -10 V tied to recombination-active defects (R: doi:10.1063/1.3224908); LIT predicts hotspot temperature (R: doi:10.1016/j.solmat.2013.09.016) | (a) cheap; (b) higher voltage, trained person only (§7) |
| **Outdoor / illuminated IR (handheld or drone)** | Module in sun, at operating point or short circuit; IEC TS 62446-3 is the outdoor thermography spec (R: VDE preview); 600 W/m2 minimum irradiance per a vendor summary (R: https://www.sitemark.com/?p=295 , secondary) | only via inactive or hot areas (S) | hot (inactive area under light behaves like a shaded part; S) | none (S) | none (S) | yes | yes: hot cells, diode substrings (R: datascout D1/D2) | WattCycle already flies thermal drones (R §1.1). Illuminated and dark IR give complementary results for the same defects (R: doi:10.3390/s20164395) |
| **UV fluorescence (UVF)** | 365 nm UV torch in the dark, ordinary camera. Detects cracks in chronological order, hot parts, and bill-of-material differences; manual 250 modules/h (R: doi:10.1109/jphotov.2019.2961781); field crack detection (R: doi:10.1109/pvsc45281.2020.9300901) | yes, on field-aged modules (needs aged encapsulant; patterns vary by material: R: same) | via crack outline (S) | **likely none**: a scuff that is not a crack should not change encapsulant fluorescence (S). Strong second arbiter | none (S) | no | "hot parts" (R) | very cheap (§3) |
| **PL (photoluminescence)** | Strong NIR-filtered illumination, EL camera. Outdoor options: an electronic board that reverses the module's polarity (EL) or opens it (sunlight PL), with an InGaAs camera, bandpass filter and lock-in (R: doi:10.3390/s24051539); or daylight PL by switching the string inverter's operating point (R: doi:10.1002/pip.3525; doi:10.1002/pip.3807) | yes | yes | likely similar to EL (S) | yes | partly | no | skip for P0; light source cost unconfirmed |
| **RGB photo** | Phone, front and back | glass breakage only | no | surface marks on glass only (S) | shows cell cut layout (S) | no | burn marks, browning (S) | free |

**Reading (S):** the useful pair for our weak spot is EL + (dark thermography and UVF). Neither thermal nor UVF reaches EL's crack-line resolution, but both can say "electrically or mechanically real" vs "cosmetic". That is the label EL lacks for scuff + half-cut cells.

## 3. Equipment (costs and sources)

| Item | Class / spec | Price seen | Source | Role | Tag |
|---|---|---|---|---|---|
| InfiRay P2 Pro | phone USB-C microbolometer, 256 x 192, 12 µm, 25 Hz, NETD ≤ 50 mK (official sheet; one retailer says ≤ 40) | US$349 (Newegg US; not re-verified, listings range ~US$238 to 399 per check); €205.79 ex VAT (eleshop.eu); India price not found | https://www.newegg.com/p/0AF-0314-00154 ; https://eleshop.eu/infiray-p2-pro-thermal-camera-for-android.html ; spec sheet https://ar.infiray.com/uploads/file/p2-pro-thermal-camera-for-smartphone.pdf | P0 thermal | R |
| Topdon TC001 | phone USB-C, 256 x 192, 8 to 14 µm, 25 Hz, NETD < 40 mK | ₹20,010 (Aajjo, undated); TC001 Plus ₹29,999 on Amazon.in (price history ₹18.7k to ₹30k) | https://au.topdon.com/products/tc001 ; https://www.aajjo.com/product/topdon-tc001-android-devices-thermal-imager-camera-in-mahesana-dhuni-international ; https://www.cheapestinindia.com/price-history/topdon-tc001-plus-thermal-camera-for-android-512-x-384-super-resolution-with-visual-camera-256-x-192-ir-resolution-dual-lens-thermal-imaging-camera-for-smartphones-and-tablets-pc-not-for-ios--681452309fc2664cab0d416e | P0 thermal (Windows / Android) | R |
| FLIR ONE Edge Pro | phone, 160 x 120, NETD 70 mK | US$550 at launch; £418.80 lowest (PriceRunner UK) | https://www.gizmochina.com/?p=494824 ; https://www.pricerunner.com/pl/345-3204478569/Power-Tools/Flir-One-Edge-Pro-Compare-Prices | weaker than the 256 x 192 options | R |
| HIKMICRO Pocket2 | handheld, 256 x 192 | ₹78,269 incl. GST (Toolbuy) | https://www.toolbuy.com/tp/hikmicro-20%C2%B0c-to-400%C2%B0c-high-performance-compact-thermal-imaging-camera-pocket2 | P0 alternative | R |
| FLIR E8 Pro | handheld, 320 x 240, NETD < 40 mK | ₹4.07 lakh (IndiaMART), ₹4.62 lakh (TradeIndia), US$3,299 (flir.com, per check C-12) | https://m.indiamart.com/comet-instruments/thermal-imaging-camera.html ; https://vamaratechwaree.tradeindia.com/flir-e8-pro-9743934.html ; https://prodindustrial.flir.com/products/e8-pro | P1 option | R |
| 640 x 480 uncooled (FLIR E96 / T560, HIKMICRO SP60 30 mK) | handheld or lab | E96 £9,899 ex VAT (RS UK; not re-verified by check); T560 US$25,490 (TEquipment); SP60 €12,999 (NL retailer); India price not found | https://uk.rs-online.com/web/p/thermal-imaging-cameras/2825336 ; https://www.tequipment.net/flir/series_t560/ ; https://thermobeeldcamera.nl/en/thermal-imaging-cameras/handheld-cameras/page2.html | P1: whole module at ~60 px per cell edge | R |
| Cooled MWIR camera / commercial LIT system | high-end LIT | **unconfirmed** (no public price found) | none | P2 only, via a partner lab | S |
| DJI Mavic 3 Thermal | drone, thermal 640 x 512 | ₹5.29 lakh ex GST for the "Mavic 3 Thermal Enterprise (TE)" listing (₹528,571, XBoom); XBoom's shoulder-bag combo is ₹570,476 ex GST (check C-13); ₹5.77 lakh incl. GST Basic Combo (MavDrones; not re-verified) | https://www.xboom.in/product-category/brands/dji/dji-enterprise-series/page/2/ ; https://mavdrones.com/product/best-dji-mavic-3-thermal-m3t-drone | WattCycle may already own a drone (Q3) | R |
| EL camera: WattCycle's own rig | unknown | n/a | Q2 | P0 if it exists | unconfirmed |
| EL camera: full-spectrum converted mirrorless (IR-cut filter removed) + long-pass filter | Si sensor; Ciocia et al. built a low-cost Si-sensor EL camera for lab and field (R: doi:10.1109/pvsc40753.2019.8980711) | conversion US$199 to 275 (+ body; filter extra, unconfirmed) | https://www.lifepixel.com/shop/our-services/full-spectrum-camera-conversion/canon-mirrorless-full-spectrum-conversion ; https://acceptance.reach.dog/shop/astrogear/products/sony-mirrorless-aps-c-full-spectrum-conversion | fallback EL; slow exposures (S) | R |
| EL camera: portable EL tester | e.g. 24 MP (6000 x 4000), 0.33 mm/px on a 1 x 2 m module | "contact us" | https://www.frbiz.com/j120189106-portable-el-tester-with-high-resolution-cameras-for-solar-panel-production-line.html | what a recycler might own (S) | R spec, price unconfirmed |
| DC supply, budget | OWON SPE6103: 0 to 60 V, 0 to 10 A, **300 W cap**, programmable | ₹12,099 (Robocraze; not re-verified by check) | https://robocraze.com/products/owon-spe6103-60v-10a-programmable-lab-dc-power-supply | enough for 0.1 x Isc EL; not for Isc on a ~45 V module (45 V x 10 A = 450 W > 300 W; S) | R + S |
| DC supply, P0 pick | Wanptek KPS6020D: 0 to 60 V, 0 to 20 A, 1,200 W | ₹19,701 incl. GST (Zbotic; price confirmed by check via snippet; 20 to 25 day delivery not re-verified) | https://zbotic.in/product/wanptek-kps6020d-60v-20a-high-precision-high-power-adjustable-led-dual-display-switching-dc-power-supply/ | Isc forward bias for one 60 / 72 / 144 half-cut module (S: 144 half-cut Isc ~13 to 14 A at ~50 V ≈ 700 W, typical datasheet values, not checked) | R + S |
| DC supply, programmable 1.2 kW | Tonghui RK-6020P, 60 V, 20 A, 1,200 W | ₹1,14,900 (Cart2India) | https://www.cart2india.com/lab-supply-dispensers/rk6020p-programmable-dc-stabilized-power-supply-voltage-060v-current-020a-power-1200w-with-led-digital-display-and-storage-functions/00000000004392353368 | P1 lock-in (remote on/off) | R |
| Lock-in switch | MOSFET or relay switch + microcontroller to square-wave the supply output, with a sync line to the PC | small; **unconfirmed** price | none | P1 LIT on a budget | S |
| UV torch 365 nm | 10 W | ₹1,790 lowest recorded, an old price (price-history.in last checked ~672 days ago, per check) (RDR Innovations); ₹4,522 (TNATRA) | https://price-history.in/product/rdr-innovations-10watts-aluminium-uv-flashlight-uM94Xnmb ; https://poshace.com/tnatra-uv-flashlight-365nm-395nm-portable-zoomable-led-for-uv-glue-curing-pet-stain-detection-rocks-minerals-hunting-scorpion-finder.html | UVF arbiter | R |
| Dark room, mounts | blackout cloth, 2 tripods or one rigid bar, module easel with end stops | unconfirmed (small) | none | registration (§4) | S |
| Fiducials | aluminium tape (IEC TS 60904-13 itself uses aluminium-tape edges for EL sharpness, Fig. 4; R: VDE preview TOC) | small | VDE preview of IEC TS 60904-13 | visible in EL (opaque) and IR (low emissivity) (S) | R + S |
| Meter | DMM or clamp meter to log V and I per image (Li 2024 did this; R: §2.2) | small | doi:10.1016/j.solener.2024.112704 | metadata | R |
| PPE | insulated gloves, cut-resistant gloves (broken recycler glass), glasses, CO2 extinguisher | small | none | §7 | S |

**Is a phone-attachment IR camera enough for a first pilot? Yes, for cell-level questions (S).** Whole 60-cell module (~1.65 m long side) on 256 px: ~6.4 mm/px, ~24 px per 156 mm cell edge. Enough to say "this cell, or this half of a cell, is hot or cool"; not enough for sub-cell maps. Fix: tile, e.g. 2 x 2 cells per frame (~1.2 mm/px, ~125 px per cell), at the cost of more frames and a mosaic step (S). Two things to check before buying (unconfirmed): raw radiometric export (not just a colour JPEG), and PC streaming for lock-in. The 160 x 120 FLIR ONE gives ~15 px per cell on a whole module (S).

**EL resolution to match BenchmarkEL:** about 0.3 mm per pixel (`handbook/13_problems_pitfalls_open_issues.md` l.175, a literature value). That is ~500 to 600 px per cell edge, so ~18 MP for a whole 60-cell module, or EL tiles (S). A 24 MP sensor over a 1.65 m module gives ~0.28 mm/px (S).

**Cost bands (S, from the rows above):**
- **P0, if an EL rig exists:** phone IR (₹20k to ₹30k) + 1.2 kW supply (₹19.7k) + UV torch (₹2k to ₹4.5k) + tape, tripods and cloth (small, unconfirmed). About ₹45k to ₹55k.
- **P0 with no EL rig:** add a converted mirrorless camera (conversion US$199 to 275 plus a body, unconfirmed) and a filter, or borrow a rig.
- **P1:** add a 640 x 480 camera (₹4 lakh to ₹20 lakh range from listings; India price for 640 x 480 unconfirmed), or rent or borrow one, plus the programmable supply (₹1.15 lakh) or a DIY switch.

## 4. Registration to cell level

EL (~1.1 µm, `handbook/02` §3) and LWIR thermal (8 to 14 µm; R: Topdon spec) need different sensors, so the images come from two cameras and must be registered (S).

1. **Shared rigid geometry (S).** The module sits on an easel with end stops. Both cameras sit on one bar or two locked tripods. Take EL then IR at the same bias **without touching the module** (Li 2024 did EL then IR per test condition; R). Do not move the cameras between modules of the same size.
2. **Lens calibration once (S).** Checkerboard for the EL camera. For IR, an aluminium-on-paper checkerboard warmed by a lamp, or a heated resistor grid. Undistort both before any homography.
3. **Fiducials (S).** Four aluminium-tape squares at the module corners on the glass. Optionally two small NIR LEDs (seen by EL) next to two warm resistors (seen by IR) at the frame. The aluminium frame edge itself is usually visible in both.
4. **Homography per module (S).** The module is planar, so after undistortion one 3 x 3 homography maps IR to EL exactly. Estimate it from the 4 fiducials, then refine on cell-grid edges. The ribbons and busbars run hot under bias (R: Li 2024 §3) and dark in EL. A multimodal PV paper used homography + ECC refinement for RGB-EL-IR alignment (R: doi:10.3389/feart.2025.1702396; its data are "statistically paired", so treat the result with care).
5. **Canonical cell grid (S).** Warp both to a rectified module of n_rows x n_cols cells (6 x 10, 6 x 12, or 6 x 24 half-cells). Every EL cell crop then has a one-to-one IR crop. That gives cell-level pairing at least, and pixel-level pairing up to the IR blur.
6. **Check (S).** Report the residual at the grid intersections. Target ≤ 1 IR pixel. The EL crop can then be cut 512 x 512 like BenchmarkEL (central cell plus neighbour fragments; `handbook/02` §4).

Resolution needed per cell (S): EL ≥ ~500 px per cell edge (above). IR ≥ ~20 to 30 px for per-cell hot / cool flags and per-cell ΔT statistics; ≥ ~60 to 120 px for sub-cell maps of an inactive region's shape. In steady state, lateral heat flow through glass and silicon blurs features to several mm anyway (S; R for "bloom": Li 2024 §3), so more IR pixels give diminishing returns there; lock-in sharpens this.

## 5. Minimal pilot plan (P0): 1 day, 5 to 6 modules

**Goal (S):** prove that we can (a) capture EL + dark thermal + UVF of the same modules, (b) register them to cell level, and (c) see whether EL-dark scuff-like streaks lack a thermal and UVF signature while cracks and inactive areas have one.

**Modules (S):** 5 to 6 from WattCycle's recycling or reuse stream:
- at least 2 half-cut (120 / 144 half-cell) modules, our weak spot;
- at least 2 modules with scuff-like EL streaks or cracks (pick from an EL screen if they have one, else from drone hotspots or visible damage);
- 1 module with an inactive area if possible;
- 1 healthy control of a common type.

Even 6 modules give ~360 to ~800 cells or half-cells, comparable to BenchmarkEL's 582 labelled cells (`handbook/03`), though unlabelled (S).

**Per module, in this order, module not moved (S unless tagged):**
1. RGB photo (front), read the label (Isc, Voc, cell count); log the serial.
2. Ambient IR frame (no current): the emissivity / reflection baseline.
3. EL at 0.1 x Isc and at 1.0 x Isc. 0.1 x Isc is the IEC TS 60904-13 crack-quantification level; 1.0 x Isc as in Li 2024 (R, §2). With the 300 W supply, use 0.1 x Isc and the highest current it allows. Log V and I with the DMM.
4. Keep Isc on. IR frames at ~1 min and at ~10 min. Li 2024 recommends imaging within 60 s of current start for Rs work and used 10 min stabilisation for contrast (R: doi:10.1016/j.solener.2024.112704 §3, abstract). Public precedents in datascout's sets: OSF csr6t IR at 3.39 A (≈1 x Isc) after 180 s; OSF ar76v at 5.289 A after 60 s (R: file names, per check).
5. Switch off. Record a 2-min IR video of the cool-down, a "poor man's" transient thermography that is free to collect.
6. UVF photo: dark room, 365 nm torch, phone or the EL camera with its IR-pass filter removed or swapped (unconfirmed which works best).
7. Remove the module.

**Time (S):** mount 5 min, RGB + label 3 min, EL 5 to 15 min (depends on the camera), IR 12 min, cool-down 2 min, UVF 5 min, unmount 5 min. That is ~40 to 50 min per module, so 5 to 6 modules fit in one day after a ~1 h morning setup and calibration (checkerboards, fiducial test).

**Who (S):** a WattCycle technician runs the module, the power and safety. The user runs the cameras, registration and logging. The user is at IIT Mandi (the Research MCP runs on the user's laptop there, per its tool description), and WattCycle's registered office is at Kamand (R §1.1). Om approves and asks WattCycle (§9).

**Data format (S):**
- EL: camera RAW or 16-bit TIFF.
- IR: radiometric raw (temperature array; for example a `.npy` / 16-bit TIFF plus the camera's own file), plus the video.
- UVF / RGB: JPEG + RAW if available.
- One sidecar JSON per image: module serial, type, cell layout, mode, current, voltage, exposure / frame rate, time since current on, ambient T, camera id, lens, distance.
- Names: `<module>_<mode>_<Ifrac>_<tsec>.<ext>`, for example `WC0003_EL_0.10_0.tiff`, `WC0003_IR_1.00_600.tiff`.
- A `capture_log.csv` row per image; registration outputs (`H_ir2el.json`, rectified grids) beside them.
- ~0.5 GB per module (S).

**Labels: none needed for P0 (S).**
- Crack and inactive maps come from running our E-PF ensemble on the new EL. That is inference only, on Om's OK for compute, and it may be CPU-feasible (unconfirmed).
- Thermal and UVF give automatic per-cell scores (ΔT vs neighbours, UVF line presence).
- If later we want to *score* the model on WattCycle cells, a small hand-labelled set is needed. Rough guess: 1 to 3 min per cell for crack polylines and inactive polygons, so 100 cells is ~2 to 5 h (S). It would make WattCycle's own cells a real unseen-module test. Optional; the user decides.

**Pilot success (S, pre-stated):**
1. Registration residual ≤ 1 IR px on all modules.
2. At least some EL inactive regions show a measurable ΔT, and at least some EL scuff-like streaks show none in IR and UVF.
3. The files load and pair automatically.

If (2) fails on every module, report it as a negative result, not a kill: lock-in in P1 may still recover the contrast.

### 5.1 Lead time and the low-power fallback (added 4 Nov after synth's question)
- **Delivery (R, not re-verified by check; pages 403 / 429):** the Wanptek KPS6020D lists 20 to 25 day delivery (Zbotic) and is out of stock at Robu. One Indian seller of the OWON SPE6103 ships in 1 to 5 days from Bengaluru (https://www.theengineerstore.in/products/owon-spe6103-60v-10a-programmable-lab-dc-power-supply , price not shown there).
- **Fallback A, whole module on the 300 W OWON (S):**
  - EL at 0.1 x Isc is fine.
  - The highest current is about 300 W / module voltage: ~0.6 to 0.75 x Isc on a 60-cell full-cell module, ~0.4 to 0.5 x Isc on a 144 half-cut (typical datasheet values, not checked).
  - Dark-IR heat input is then ~half of that at Isc. The inactive-region deficit scales about linearly with power. Resistive (I²R) hotspots fall to ~1/4.
  - Judgement (S): with NETD ≤ 50 mK, inactive areas of about a quarter cell or more should still show a usable ΔT after ~10 to 15 min. Small inactive slivers and weak solder faults may not. Averaging many frames helps. Partial support (R): for PID-shunted modules, Kumar et al. found steady state with *medium* input current most suitable for quantitative forward-bias IR (doi:10.1016/j.seja.2023.100049); that is PID-s, not inactive areas, so it is only indirect.
- **Fallback B, one substring at a time (S):**
  - On recycler modules where the jbox may be opened, inject current between the bypass-diode terminals of one substring.
  - That is about a third of the module voltage (~13 to 17 V), so Isc fits in 300 W: full Isc on full-cell modules, ~0.7 x Isc on half-cut ones (OWON 10 A limit).
  - It is three captures per module and needs jbox access (Q9). It is also safer (lower V).
- **Fallback C:** borrow a ≥ 60 V, ≥ 15 A, ≥ 1 kW supply from WattCycle or an IIT Mandi lab (unconfirmed; Q6, Q12).
- **Earliest P0 date (S, from Om's go on 4 Nov):**
  - **Synth's W3 (18 to 24 Nov; W1 = Wed 4 to Tue 10 Nov):** fair if WattCycle replies within ~1 week and either has an EL rig and a supply, or we accept Fallback A or B. Phone IR camera, OWON and UV torch should arrive within ~1 week (delivery for the camera and torch unconfirmed).
  - **~25 Nov to early Dec:** if we insist on the Wanptek for whole-module Isc.
  - **December or later:** if there is no EL rig and a converted camera must be imported (shipping time unconfirmed), or if the safety SOP sign-off is slow.

## 6. Extended plan (P1): 4 to 5 days, 15 to 20 modules; plus P2 options

**Modules (S):** 15 to 20, stratified: 6 to 8 half-cut (with and without scuff), 4 to 6 with cracks and inactive areas, 2 to 3 with known hotspots (from drone IR), 2 healthy, mixed mono / multi. 20 modules give ~1,200 to ~2,800 cells (S).

**Additions to P0 (S unless tagged):**
1. **Bias sweep** 0.1, 0.3, 0.5, 0.7, 1.0 x Isc for EL and IR, as in Li 2024 (R). Per-cell EL-vs-current curves give local series-resistance cues (R: same).
2. **Higher IR resolution:** a 640 x 480 camera (borrow, rent or buy), or the 256 x 192 camera tiled 2 x 2 cells per frame.
3. **Low-cost lock-in thermography:** the programmable supply or a MOSFET switch square-waves the current; the camera streams raw frames; demodulate on CPU. Frequencies of ~0.1 to 1 Hz and some tens of periods per module are my guess for glass-covered modules (S, to be tuned on the first module). Output: amplitude and phase per pixel.
4. **Reverse-bias hotspot imaging** on 2 to 3 sacrificial modules (recycling stock): (a) the shading method under sun or lamp with the module shorted (MQT 09 idea; R §2); (b) if a trained person agrees, jbox open, one substring reverse-biased with a hard current limit and a short time, imaged in IR and with a visible camera for breakdown light (R: doi:10.1063/1.3224908; doi:10.1063/1.3256199).
5. **Outdoor IR of the same modules:** on a rack in sun above 600 W/m2 (R, secondary, §2), handheld IR, plus one WattCycle drone pass if they have one. This ties our dark-lab thermal to the field thermal WattCycle already collects (R §1.1) and supports the "drone for screening, EL for detail" pipeline in Om's brief.
6. **I-V / flash test per module** if WattCycle has a tester (Q4). Our handbook says power loss is out of scope "unless we get some valid data" (`handbook/02` §9). This would be that data (S).
7. **UVF on all modules**; PL only if a light source is at hand.

**Time (S):** ~60 to 75 min per module in the lab (sweep + LIT), about 6 modules per day, so ~3 lab days. Add 0.5 day setup, 0.5 day outdoor + drone, and 0.5 day reverse bias: 4 to 5 days in all. Spread over 2 weeks so each day's data is checked before the next.

**P2 options (S):**
- Ask a group with module-scale EL + DLIT experience (Rajesh Gupta's group, IIT Bombay, per OpenAlex via check P-12; doi:10.1088/1361-6501/ab0265, doi:10.1016/j.seja.2023.100049) to image 3 to 5 of our P1 modules with a cooled LIT system. That gives a high-quality reference for our low-cost lock-in.
- Repeat EL + IR on a few modules after a mechanical load or thermal cycle (if WattCycle has a chamber, unconfirmed). That gives controlled crack growth and inactive formation, i.e. before / after pairs.

## 7. Safety (S unless tagged; for the technician and Om, not a substitute for WattCycle's own SOP)

- **Voltage.** One module in forward bias runs at about Voc (roughly 40 to 50 V DC for 60 / 72 / 144 half-cut types; S, typical datasheet values). That is below common DC extra-low-voltage limits (general background, not checked here). **Never connect modules in series** for capture.
  - Reverse bias of a substring (P1 item 4b) can need ~10 V or more per cell; breakdown near -10 V is reported for one type (R: doi:10.1063/1.3224908). For a 20 to 24 cell substring that is hundreds of volts: a trained person, an interlock and a hard current limit, or skip it.
- **Current.** 10 to 14 A DC. Use rated leads and MC4 adapters, and switch the supply off before connecting or disconnecting (DC arcs). Fuse the lead.
- **Light.** A module in daylight makes its own Voc and current. Connect in the dark or with the module covered.
- **End-of-life modules.** Insulation may be damaged: about 14% of decommissioned modules that passed I-V + EL screening failed wet-leakage tests (R: https://www.pv-magazine.com/2026/08/19/i-v-screening-for-decommissioned-pv-modules/ ). Do not touch the frame while energised unless it is grounded and insulation is checked. Expect broken glass (cut gloves) and soldered parts (wash hands).
- **Heat.** At Isc in the dark, Li 2024 displayed their 10-min IR images on a common 24 to 43.5 °C scale (R §3). That is a display scale, not a measured module temperature, so it only suggests that warming of order ten degrees is typical (S). Reverse-bias or shaded hotspots can get much hotter (R: doi:10.1016/j.solmat.2013.09.016 predicts hotspot temperatures). Limit time and current, keep an IR camera on the cell, have a CO2 extinguisher, and nothing flammable on the backsheet.
- **UV.** A 365 nm torch needs UV-blocking glasses; avoid skin exposure.
- **Drone.** India's drone rules (DGCA / Digital Sky registration and pilot certificate) apply; unconfirmed details; WattCycle's pilots handle it.

## 8. How this serves the EL segmentation problem (S, for synth)

1. **Weak labels for scuff vs crack.** Per cell: EL-dark streak + no ΔT + no UVF line → "scuff candidate"; EL-dark + ΔT or UVF line → "real defect". A crack-vs-scuff signal with no hand labels, on half-cut cells, where E1 fails (E: README).
2. **Inactive weak labels.** Cool regions under forward bias that match EL-dark regions → an inactive pseudo-mask check, for the data-limited class (`handbook/02` §7).
3. **WattCycle-domain unseen modules.** Even unlabelled, they are a deployment-domain check ("WattCycle's cells would be another unseen source", `handbook/13_problems_pitfalls_open_issues.md` l.203, E).
4. **Paired data** for cross-modal pretraining or a thermal teacher (ideas agent).
5. **Field link.** Dark-lab IR ↔ outdoor IR ↔ drone IR on the same modules: the industrial pipeline.
6. **Power.** I-V per module (P1) re-opens the severity and power-loss chain.

## 9. Questions for Om (to ask WattCycle / IIT Mandi; agents made no contact)

**Identity and access**
1. Is our partner "WattCycle Sustainable Solutions Pvt. Ltd." (Dr Satvasheel Powar, IIT Mandi Catalyst; wattcycle.ai: Atlas, drone monitoring, ReVive recycling)? Its Atlas platform is described as solar asset management, which fits our docs; please confirm, and who is our contact there?
2. Can the images be used in the thesis and a paper, and released (for example CC BY) with module serials anonymised?

**Equipment**
3. Do you have an EL rig? Camera type (cooled Si CCD / CMOS, InGaAs, modified DSLR, portable EL tester), resolution, filter, raw 16-bit export, dark room size?
4. Do you have an I-V / flash tester or wet-leakage test for incoming modules? Can we get per-module I-V for the modules we image?
5. Which IR cameras do you have (drone payload model, handheld)? Resolution, NETD, lens FOV, closest focus. Can they export **radiometric raw** data and stream to a PC?
6. DC power supplies: max V, A, W; programmable or remote on / off?
7. Do you have a module rack or easel, and outdoor space with an irradiance meter (pyranometer)?

**Modules**
8. How many end-of-life or returned modules are on site now, and of which types (full vs half-cut, mono / multi, 60 / 72 / 120 / 144 cells, age, field history)? Can you pick ~6 (P0) and ~20 (P1): half-cut with scuff-like streaks, cracked or inactive, hotspot, healthy?
9. Are some destined for destructive recycling, so the jbox can be opened for reverse-bias tests (P1)?
10. Do you already hold EL or drone IR images of the same modules or plants, with any notes or diagnoses?

**People, time, safety**
11. Who can operate the electrical side (trained person)? Do you have an SOP for energising used modules, and PPE?
12. IIT Mandi: does the Energy Engineering Laboratory (Powar) or any SMME / SCEE lab have an IR camera, solar simulator, I-V tracer or DC supply we could borrow? Does the CAIR Drone Lab have a thermal payload?
13. Budget: can WattCycle or the lab fund the P0 kit (~₹45k to ₹55k: phone IR camera, 1.2 kW supply, UV torch, tape and mounts)? Or does WattCycle already own equivalents?
14. When could we do a one-day P0 session (next 2 to 3 weeks)? Can the module and cameras stay fixed between EL and IR shots, and can we stick aluminium tape on the glass?
15. Is reverse-bias imaging allowed at all? If yes, who signs off and what current and time limits?
16. Would you be interested in the outputs (per-cell defect maps, the registered EL + IR set) for Atlas or ReVive grading? That makes it a two-way exchange (S).

## 10. Sources

**Research MCP ids (all returned by the tool):**
- doi:10.1016/j.solener.2024.112704: Li et al. 2024, EL + IR of fielded modules (full text read: §2.2, §3, §4).
- doi:10.1088/1361-6501/ab0265: Roy and Gupta 2019, EL + lock-in on modules.
- doi:10.1109/jphotov.2020.3003781: Asadpour et al. 2020, DLIT and solder bonds.
- doi:10.1016/j.solmat.2014.09.020: Gerber et al. 2015, EL + DLIT on thin film.
- doi:10.3390/s20164395: Gallardo-Saavedra et al. 2020, IR in illumination vs dark.
- doi:10.1016/j.energy.2020.117930: Gallardo-Saavedra et al. 2020, EL + IRT + I-V on a purpose-built module.
- doi:10.1016/j.solener.2018.07.055: Berardone et al. 2018, EL + IR (forward bias and illuminated).
- doi:10.1109/pvsc40753.2019.8980711: Ciocia et al. 2019, low-cost Si-sensor EL camera.
- doi:10.1063/1.3224908: Kwapil et al. 2009, reverse-bias breakdown.
- doi:10.1063/1.3256199: Bothe et al. 2009, forward / reverse luminescence + DLIT.
- doi:10.1016/j.solmat.2013.09.016: Geisemeyer et al. 2014, hotspot prediction by LIT.
- doi:10.1109/jphotov.2019.2961781: Köntges et al. 2020, UVF review.
- doi:10.1109/pvsc45281.2020.9300901: Kern et al. 2020, UVF field cracks.
- doi:10.3390/s24051539: Redondo Plaza et al. 2024, passive EL / PL (polarity-reversing / opening board, InGaAs + lock-in).
- doi:10.1002/pip.3525: Vuković et al. 2022, PL of modules in a string via inverter operating-point switching.
- doi:10.1002/pip.3807: Weber et al. 2024, daylight PL with inverter-based switching.
- doi:10.1016/j.seja.2023.100049: Kumar, Puranik and Gupta 2024, inverse-IR thermography of PID-s modules.
- doi:10.3389/feart.2025.1702396: Almukhtar and Kurnaz 2026, RGB-EL-IR fusion with homography + ECC.
- doi:10.1016/j.solmat.2024.113121: Kumar and Gupta 2024, shunt review.
- doi:10.1016/j.solener.2023.111994: Puranik et al. 2023, module QEL review.

**Standards (previews / TOCs only):** IEC TS 60904-13:2018, VDE preview (TOC, scope); IEC TS 62446-3:2017 (scope via search; camera minimums in clause 4.2 not read, unconfirmed); IEC 61215-2:2021 (MQT 09 TOC).

**Web URLs:** listed inline in §1 and §3.

**Team files:** datascout's table (`datasets/dataset_table.md`, A1 / A2: public EL + forward-bias IR sets from UCF, same protocol family as Li 2024).

## 11. Unconfirmed / open
- WattCycle identity match; any WattCycle EL, I-V or IR equipment; drone model.
- Any IR camera or PV kit at IIT Mandi.
- India prices for P2 Pro and the 640 x 480 cameras; filter and body prices for the converted camera.
- Radiometric raw export and PC streaming for the phone IR cameras.
- IEC TS 62446-3 numeric camera minimums; IEC 61215-2 MQT 09 procedure details.
- Lock-in frequencies suitable for glass-covered modules with a microbolometer (to tune in P1).
- Module Isc / Voc values (read from each module's label).
