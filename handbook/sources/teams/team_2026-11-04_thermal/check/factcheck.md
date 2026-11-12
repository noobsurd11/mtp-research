# Fact-check, pass 1 (datasets, ideas, capture)

Owner: `check`. Date: 4 Nov 2026 (IST). Status: pass 1 v1, sent to owners; re-check after their fixes. Pass 2 (synth) pending.

Files checked (md5 at start): `datasets/dataset_table.md` ebc9a40b, `datasets/notes.md` c6501936, `ideas/ideas_long.md` 1b3f6f3e, `capture/capture_plan.md` 4c80b741.

**Method.** Dataset facts from the source's own metadata: OSF API (`api.osf.io/v2/nodes/<id>` and the osfstorage file listings: names and sizes only), Figshare API (DTU), Zenodo API, Mendeley Data public API, Hugging Face API, GitHub API / READMEs, OSTI. Papers via Research MCP `get_paper` (abstracts); full text only for Li 2024 (already in the local library), Chen 2025 review (local) and Almukhtar 2026 (local), sections read with `read_paper`. Web pages via WebFetch / WebSearch. No dataset files, archives or PDFs downloaded; retail pages that returned 403 / 429 were not retried by other means and are marked UNVERIFIABLE. The E check was re-run on CPU, read-only, on the UCF-EL annotation CSV only. No test, E1 or B2 files opened.

**Verdicts.** OK = source exists and says what is claimed. FIX = wrong, outdated, mis-tagged or missing a fact the source gives (fix text in the last column). UNVERIFIABLE = I could not reach or read the source.

**Counts (pass 1):** 110 items: **OK 73, FIX 31, UNVERIFIABLE 6** (rows marked "OK + FIX" count as FIX; "OK + add" as OK). Most FIXes make the picture better, not worse (section 6).

---

## 1. The E claim (ideas T38, §1): re-run on CPU

| # | File | Claim | Verdict | Correct fact and source |
|---|---|---|---|---|
| E-1 | ideas §1, T38 | UCF-EL annotations hold 373 module ids, 201 with exactly 60 annotated cells, none with 36; names anonymised `M####C######` | OK | Reproduced exactly (E: `~/mtp/datasets/UCF-EL-Defect/AnnotationsCombined.csv`, 89,087 rows, 16,941 unique file names; 16,205 `M####C######.jpg` + 256 `.png` (the 256 simulated cells of Fioresi 2022, S) + 8 named lab-test groups of 60 cells each) |
| E-2 | ideas §1, T38 ("Prior now L (A1 ruled out by cell count)"; table "A1 ruled out by cell count") | the count rules out A1 (36-cell Shell M55) as a UCF-EL source | FIX (over-read E) | Only the 201 complete 60-cell modules are excluded. The other 172 are partly annotated: 109 have a highest cell position ≤ 36 (46 stop at 12, 28 at 32, 1 at 36; E, same CSV, cell id `C` + 2-digit position + 3-digit suffix). So the count cannot exclude 36-cell modules. Say "201 of 373 UCF-EL modules are 60-cell, so not A1; the rest are partial, link not excluded". UCF-EL's own README also assumes 72-cell modules for its cropper (E: `UCF-EL-Defect/README.md`). The prior is synth's call |
| E-3 | notes §5 | UCF-EL size: Chen 2025 says 17,064; F04 measured 11,851 | OK (both true) | Local `Test_Images/` holds 17,064 files (E, `ls` count today) = the paper's 17,064 incl. 256 simulated (R: doi:10.1109/jphotov.2021.3131059 abstract). 11,851 is the official train / test split (E: F04 census l.66) |

## 2. Datasets (`datasets/dataset_table.md`, `datasets/notes.md`)

### 2.1 Top 5 (every row checked)

| # | Row | Claim | Verdict | Correct fact and source |
|---|---|---|---|---|
| D-1 | A1 | OSF csr6t exists; title; 180 installed, 156 characterised, 3 controls; CC BY 4.0 | OK | OSF API node csr6t: "Monocrystalline Silicon Photovoltaic Modules From a 10-Year-Old Rooftop System in Florida", created 2025-03-11; licence id 563c1cf88c5e4a3877f9e96a = "CC-By Attribution 4.0 International" (OSF licences API) |
| D-2 | A1 | modalities (EL sweep 0.01 to 1 × Isc, indoor IR, indoor UVF, visual, light / dark / pseudo I-V, EL-derived cell dark I-V, close-up EL + PL) | OK | OSF description lists exactly these, plus carrier lifetime vs excess carrier density; sweep levels 0.01, 0.05, 0.1, 0.4, 0.7, 1 × nameplate Isc. Outdoor UVF of the same modules is in t8x9k under FSEC/SHELL (same page) |
| D-3 | A1 | "IR folder 473 jpg"; "IR file names are `<serial>_cropped.jpg`" | FIX | 473 files = 157 `<serial>_cropped.jpg` (~1 MB) + 157 `<serial>_cropped.txt` (43 to 51 kB) + 159 raw `<date>_SHELL_M55_<serial>_180s_3.393A.txt` (537,840 B); folder total 0.26 GB (OSF file listing) |
| D-4 | A1 | "EL folder 1,044 files"; "EL raw TIF 16.7 MB each"; name pattern `..._RAW.tif` | FIX | 1,044 = **946 Nikon `.NEF`** (Jan 2022, ~13.8 MB, 3 s, 6 currents 0.025 / 0.195 / 0.296 / 1.392 / 2.394 / 3.393 A, i.e. the 0.01 to 1 × Isc sweep) + **98 `_RAW.tif`** (Apr 2018, 16.7 MB, a few modules with 22 to 25 bias steps); 14.95 GB total (OSF listing) |
| D-5 | A1 | "OSF IR pixel size unconfirmed"; "that the OSF IR files follow [Li 2024's] protocol is likely but unconfirmed [S]" | FIX (upgrade) | The file names give the protocol: **forward bias 3.392 to 3.393 A (≈ 1 × Isc), 180 s after current on, for 157 modules** (2 extra files at 1.354 A), dates 14 Jan to 3 Feb 2022; EL at the same 3.393 A exists for each (OSF listing, R). So A1 has bias-matched EL + dark forward-bias IR for essentially every module, at 180 s, not Li 2024's 10 min. The raw txt is the same size as A2's IR txt (537,840 B); a 320 × 240 temperature matrix is likely (S: 76,800 values × ~7 B) |
| D-6 | A1 | "In the companion paper, EL (Sensovation HR-830 ...) and IR (Fluke Ti55 ...)" (Li 2024 as companion) | FIX | The OSF page names **Colvin et al. 2023, IEEE JPV, doi:10.1109/jphotov.2023.3238278** (Research MCP) as the study using this data (180 modules, Cocoa FL, 156 characterised, 3 controls; losses mainly resistive from rear-contact Ag / solder corrosion). Li 2024 is a separate 9-module study by an overlapping team (Fang Li, Colvin, TamizhMani, Davis); its 3 FL Shell modules may come from this system (S). The Sensovation CCD / Fluke Ti55 setup is Li 2024's; A1's bulk EL is Nikon NEF (S, from the extension), so the camera differs |
| D-7 | A1 | Shell M55 are 36-cell | OK | Li 2024 §2.1: "These 36-cell modules" (R). A1 EL voltages of ~16 to 26 V fit 36 cells (S) |
| D-8 | A1 | Li 2024: SSIM 0.82 (solder bond, FL #321), 0.61 (AZ #193), whole-cell hotspot with no EL signature put down to microcracks | OK | Li 2024 §4 (full text). Also: unexposed module 0.53 |
| D-9 | A1 | "Dominant defects: solder bond / series resistance, EVA browning; cracks present but not the main mode [R]" | FIX (tag) | Solder / Rs: R (Colvin 2023 abstract; Li 2024 §2.1 attributes Isc loss to EVA browning). "Cracks present" is in neither abstract: tag S or drop |
| D-10 | A1 | per-cell dark I-V in `EL-Derived_Cell_Dark_I-V/diode_fit_outputs.xls` | OK | OSF description (two-diode fit, n1 = 1, n2 = 2) and listing (158 txt + 1 xls) |
| D-11 | A2 | OSF ar76v: 42 modules, 19 years, Orange County Convention Center, CC BY 4.0, "camera suddenly failed" | OK | OSF API node ar76v (created 2025-12-08). One control is the 165 W variant, rest 175 W |
| D-12 | A2 | EL "bias levels about 0.1 to 3.7 A" | FIX | 6 levels: 0.096, 0.296, 0.496, 2.092, 3.692, **5.289 A**; 270 NEF = 43 serials × 6 (+ 1 module with 18); 3.82 GB (OSF listing) |
| D-13 | A2 | IR: 32 files, jpg + txt pairs, "about 16 captures"; 5.289 A, 60 s | FIX (refine) | Folder `indoor_IR`: 16 jpg + 16 txt (537,840 B) = 16 captures of **15 modules**, all at 5.289 A, 60 s; all 15 have EL at the same current (OSF listing). Folder total 0.02 GB |
| D-14 | A2 | SolarWorld SW-175 cell count unconfirmed | OK (still unconfirmed) | Hint only (S): EL at 0.1 A runs at ~36 V, about 72 cells at ~0.5 V |
| D-15 | A3 | DTU 10.11583/DTU.29665346.v1; CC BY 4.0; 642.6 MB; NEF EL per module; IR .raw float32 363 × 605; I-V mean of 3 at STC; folder per defect | OK | Figshare API (published 2025-10-14; files `IRT DATASET.7z` 642,610,942 B + README 1,161 B; author Rodrigo Del Prado Santamaria) |
| D-16 | A3 | 43 artificially degraded modules; 8 / 10 / 14 / 20 m; 200 to 1000 W/m²; cracks hard to tell from healthy; disconnections visible from 600 W/m² | OK | doi:10.1051/epjpv/2025020 abstract (Research MCP). Also R: PID and glass cracks showed no pronounced anomaly; shorted diodes and heavy soiling gave 80 to > 100 °C hotspots; altitude effect small vs irradiance |
| D-17 | A3 | "about 60 px per cell side for a 6 × 10 module" | FIX | 363 × 605 is a **resampled** grid. Native resolution is "< 1 cm/pixel to 3 cm/pixel" (paper abstract), i.e. about 5 to 16+ native px per 156 mm cell (S arithmetic). Cell count of the DTU modules is unconfirmed |
| D-18 | C1 | Polenghi, Mendeley 10.17632/pxyzzkbs4b.1; 84 conditions × 3 = 252 PNG; 500 DPI; CC BY 4.0; pixel-aligned; Dauerhaft AP130 × 150 mm 4.5 Wp poly cell | OK | Mendeley API (v1, 2026-02-09, 260 files); DiB 2026 doi:10.1016/j.dib.2026.113109 abstract: "pixel-level aligned HDR, monochrome, and electroluminescence images". EL and NIR share one camera ("almost perfect pixel-pixel correspondence"); HDR is a second camera in a calibrated binocular rig |
| D-19 | C1 | "Progressive crack damage" | FIX (add) | Damage types are wider: soiling, blunt impact, **cuts, abrasions, scrapes**, bending, smashing, cracking, flames, Joule overheating (DiB abstract). The abrasion / scrape stages are a public EL + NIR + visible look at surface scuffs, which bears on the scuff question (S) |
| D-20 | Rank #5, D1 | InfraredSolarModules: 20,000 (table sums to 20,006); 24 × 40 px; 12 classes; MIT | OK | GitHub README (sum is 20,006, discrepancy real); GitHub API licence MIT |
| D-21 | Rank #5, D1 | "941 'Cracking'" listed as a crack-relevant class | FIX (wording) | README: Cracking = "Module anomaly caused by cracking on module surface", i.e. surface / glass cracking, not cell cracks |
| D-22 | Rank #5, D2 | OSF 7v5zt: 1,898 IR + visual pairs, 20 make-models, raw TIFF + converter; naming aligned with t8x9k | OK | OSF API description. "Outdoor" is not stated (fielded modules imaged by FSEC; S) |
| D-23 | Rank #5, D3 | OSF t8x9k: 7,190 modules, 26 make-models, FL / OH / MA; 2,989 JPG | OK | OSF description; Chen 2025 §5.5.2 (full text). Page: "Most of the modules with UVF images in Florida have corresponding IR images in 7v5zt"; links csr6t for SHELL |
| D-24 | Rank #1 and bottom line | "473 IR images" for A1; "at least 59 have IR (A2 about 16, A3 43) plus an unconfirmed share of A1" | FIX (upgrade) | **About 215 modules have IR:** A1 157 (forward bias ≈ 1 × Isc), A2 15 (5.289 A), A3 43 (drone, sunlit). See D-3, D-5, D-13 |
| D-25 | notes §6 Q1 | A1 EL folder ~15 GB (S) | OK | 14.95 GB (listing). Add: A1 IR folder is only 0.26 GB for all 157 modules |

### 2.2 Other rows (sample of 20)

| # | Row | Claim | Verdict | Correct fact and source |
|---|---|---|---|---|
| D-26 | B1 | csr6t close-up EL + PL: 11 files, 2 modules, 2020-10-27, 300 s | OK | OSF listing `close-up_EL_PL`: 6 tif + 5 jpg, serials 6320427744 and 6330431478 |
| D-27 | B2 | Zenodo 15020575: 2 OME-TIFF stacks, 264.9 MB each, CC BY 4.0; paper 10.3390/s24051539 | OK | Zenodo API (files "EL 4ms 6A inv", "PL 4ms 6A"; relation isSupplementedBy s24051539) |
| D-28 | B2 | "daylight / passive acquisition by inverter switching" | FIX | Redondo-Plaza 2024 abstract: an **electronic board** reverses the module's polarity (string current injected, EL) or bypasses it to open circuit (sunlight PL); InGaAs camera + bandpass filter with a lock-in technique. Inverter switching is a different method (doi:10.1002/pip.3525, doi:10.1002/pip.3807) |
| D-29 | B3 | NREL BEST, DOE Data Explorer 10.21948/2462712: I-V, EQE, EL, PL; control and 5-year bifacial; count and licence not stated | OK | OSTI page: authors Ovaitt, Kern, Deline, Johnston, Palmiotti, Tonita, Jordan, Hacke; 2024-08-23; PERC and SHJ |
| D-30 | B5 | NREL field PL: 856 half-cut-cell images, 4056 × 3040 | OK | Chen 2025 §5.4.2 (full text) |
| D-31 | C2 | IBC4EU Zenodo 19880941: EL of cells + visual of modules, spreadsheets, 6.7 GB zip, CC BY 4.0 | OK | Zenodo API (2026-04-29; ISC Konstanz, UAB Metsolar) |
| D-32 | C3 | TECNALIA Zenodo 18306410: 5.9 MB archive, CC BY 4.0 | OK | Zenodo API (`TECNALIA.rar` 5.9 MB) |
| D-33 | C4 | PV-LLM Zenodo 15930823: 3 modalities, 50 labelled images per category, 310.1 MB, CC BY 4.0; README classes | OK | Zenodo API; GitHub DuraMAT/PV-LLM README (bird droppings / surface contamination; IR hotspots; EL microcracks, broken cells) |
| D-34 | D4 | PVF-10: "DOI unconfirmed" | FIX | doi:10.1016/j.apenergy.2024.124187 (Research MCP): 5,579 crops, 8 plants, 10 classes (5 repairable / 5 irreparable). ideas already cites this DOI |
| D-35 | D5 | SolarFCD arXiv 2604.23662: 4,435 images, 4 classes, 3 public sets, RGB / drone + thermal | OK | arXiv abstract (Research MCP) |
| D-36 | D5 | "3,078 unique"; "CC BY 4.0 + source licences"; "EL absent, thermal from one source" | UNVERIFIABLE | Not in the abstract; full text not read |
| D-37 | D6 | Ferdous DiB 2026: 50 raw → 5,000, boxes, 1 class, MLX90640 + Pi NoIR | OK | doi:10.1016/j.dib.2026.113288 abstract (Dhaka, 06 and 22 June 2026; 4,626 labelled instances in train) |
| D-38 | D7 | Univ. del Valle 82vzccxb6y v2: 277 images, Zenmuse XT on Matrice 100, CC BY 4.0; review says 67 | OK | Mendeley API; Chen 2025 §5.3.2. Add: the imaged array is one string of 4 mono panels |
| D-39 | D8 | bird-droppings set: licence unconfirmed; "tagged for segmentation" | FIX | Mendeley API: **CC BY 4.0**; UTi165A, 160 × 120; v1 410 images (304 / 70 / 36) **after** flips / rotations, resized to 640 × 640; v2 850; files are YOLOv11 exports, so boxes rather than masks (S from format) |
| D-40 | D9 | PVMD: licence unconfirmed; "self-acquired + augmented"; label type unconfirmed | FIX | Mendeley API: **CC BY 4.0**; 1,000 images = Hotspots 350, Cracks 350, Shadings 300 (folder = image-level class); DJI Mavic 3 Thermal, 5 Sep 2024, Tshwane University of Technology. "Augmented" is not stated |
| D-41 | D10 | OpenUVF counts (50 + 100 module, 3,000 + 21,600 cell images); "No License Provided" on the hub | OK + add | Chen 2025 §5.5.1 (full text). Add: GitHub `southern-company-r-d/OpenUVF` is Apache-2.0 (code; whether it covers the Dropbox data is unconfirmed); labels via LabelImg / PASCAL VOC, so boxes likely (S) |
| D-42 | D11 | HF Manishsahu53/...: Apache-2.0, 10K to 100K, DJI drone, India, no labels | OK + add | HF API. Add: 3 zips (Plot_16 / 17 / 18 "50MW"), 2.25 + 8.56 + 8.29 GB ≈ 19.1 GB |
| D-43 | E1 | Li 2024: 9 M55 modules (3 FL + 1 control Shell, 5 AZ Siemens 18 y); 5 bias levels × 2 exposures (60, 300 s) | OK | Li 2024 abstract and §2.1, §2.2 |
| D-44 | E2, E3, E4 | Gallardo-Saavedra Energy 2020 (60-cell poly ad hoc module, cells reachable from the back); Lai ECM 2025 (drone IR + RGB + darkroom CCD EL, 21 types); Johnston PVSC 2023 (PL + EL + DLIT, half-cut and EWT modules, DH / LID / TC / HF) | OK | Research MCP abstracts (doi:10.1016/j.energy.2020.117930; doi:10.1016/j.enconman.2025.119783; doi:10.1109/pvsc48320.2023.10359835) |
| D-45 | E5, E6, E10 | Asadpour 2020 (DLIT, doublet, OSTI OA); Bommes 2021 (4.3 M IR images, 107,842 modules, 7 plants, 10 classes); Mantel 2019 (982 images, 47,244 cells after blur filter, crack A / B / C + fingers) | OK | Research MCP abstracts. Bommes "640 × 512 (XT2)" is not in the abstract (snippet only) |
| D-46 | E8 | JRC105705: dark IR gives little local information; illuminated IR separates damage classes in line with EL | OK + add | JRC repository page: Berardone, Paggi, Lopez Garcia (2017), "Image analysis of aged PV modules: electroluminescence versus infrared thermography"; dark IR "provide few local information"; illuminated IR "promising to distinguish between classes of damage in line with EL data" |

## 3. Papers (load-bearing, spot-checked)

All ids below were returned by the Research MCP this session.

| # | File(s) | Claim | Verdict | Source says |
|---|---|---|---|---|
| P-1 | ideas §0, §0.1, §3; datascout | Dhimish 2021: no hotspot for micro-cracks (mode 2); "shaded area" (3) and "breakdown" (4) give hotspots; 12 cells; worst at 40 to 60% shading | OK | doi:10.1038/s41598-021-03498-z abstract: temperature rose "from 25 °C to 100 °C" for modes 3 / 4; worst case 40 to 60% shading ratio, up to 105 °C |
| P-2 | ideas §0.1 row "Crack, no isolation (14; Köntges mode A) ... no hot spot (R: Dhimish)" | Dhimish's "micro-crack" = Köntges mode A | FIX (tag) | Dhimish uses his own 4-mode scheme; mapping it to Köntges A is S. Keep the R for "micro-cracks gave no hotspot", tag the A-mapping S |
| P-3 | ideas §0 | "if the lost current forces the whole cell into reverse bias it becomes a hot cell or hot spot (R: Dhimish 2021, 2022)" | FIX (tag) | Neither abstract mentions reverse bias. The observation (hotspots for modes 3 / 4, and with crack area) is R; the reverse-bias mechanism is S (standard physics) |
| P-4 | ideas §0, T27 | Dhimish 2022: 10 cells, cracks 1 to 58%, minor cracks no hotspot, > 46% cracked no hotspot, PID hotspots ~50 °C | OK | doi:10.1038/s41598-022-16546-z abstract |
| P-5 | all three | DTU drone IR (A3 paper) findings | OK | see D-16 |
| P-6 | all three | Li 2024 Solar Energy: EL then IR per condition in a dark room; Sensovation HR-830 cooled CCD + 850 nm LP, 16-bit; Fluke Ti55, cropped / rescaled 320 × 240; 0.1 to 1.0 × Isc; SSIM analysis at Isc, EL 5 min, IR after 10 min stabilisation; "within 60 s" recommendation; up to 23% Rs underestimate from IR temperature errors; bloom by lateral heat flow; steady-state IR maps inactive regions (cited); gridline breakage and metallisation corrosion EL-only | OK | doi:10.1016/j.solener.2024.112704, full text §2.1, §2.2, §3, §4, §6 |
| P-7 | capture §7 | "At Isc in the dark, a module warmed to ~43 °C after 10 min in Li 2024 (R §3)" | FIX | §3: the Fig. 3 IR images "were displayed in the same scale between 24 °C and 43.5 °C". That is a display scale, not a measured module temperature. Say "IR shown on a 24 to 43.5 °C scale" |
| P-8 | ideas §0, T05; capture | Asadpour 2020: DLIT, failed solder joint → point-like "asymmetric doublet" heating | OK | doi:10.1109/jphotov.2020.3003781 abstract |
| P-9 | ideas, capture | Köntges 2020 UVF review: cracks in chronological order, hot parts, BOM; manual 250 modules/h | OK | doi:10.1109/jphotov.2019.2961781 abstract (hood 200, drone up to 720 modules/h) |
| P-10 | ideas T32, capture | Kern 2020: UVF crack detection in the field; patterns vary with module and stress | OK | doi:10.1109/pvsc45281.2020.9300901 abstract |
| P-11 | ideas, capture | Berardone 2018: forward-bias and illuminated IR + EL histograms separate disconnected interconnects, humidity corrosion, broken fingers (20-year mono modules) | OK | doi:10.1016/j.solener.2018.07.055 abstract |
| P-12 | capture §1.2, §6 | Roy and Gupta 2019, Kumar and Gupta 2024, Puranik et al. 2023: "Institute affiliation ... unconfirmed" | FIX (upgrade) | OpenAlex authorships: **all IIT Bombay** (Rajesh Gupta's group). Roy and Gupta 2019 = EL + DLIT shunt severity on commercial modules (doi:10.1088/1361-6501/ab0265). The same group wrote the inverse-IR PID paper ideas cite (doi:10.1016/j.seja.2023.100049). A concrete Indian lead for P2 lock-in / IR |
| P-13 | ideas §0, §0.1 | PID-shunted cells black in EL, seen by IR | OK | doi:10.1016/j.seja.2023.100049 (Kumar, Puranik, Gupta 2024): inverse IR maps severely PID-s cells "with no EL emission" |
| P-14 | capture | Kwapil 2009 breakdown near −10 V tied to recombination-active defects; Bothe 2009 pre-breakdown light + heat; Geisemeyer 2014 LIT-based hotspot prediction | OK | doi:10.1063/1.3224908; doi:10.1063/1.3256199; doi:10.1016/j.solmat.2013.09.016 abstracts (all on mc-Si cells) |
| P-15 | ideas §0, T27, T36 | Ramspeck 2014 in-line reverse-bias thermography predicts in-module hotspot temperature | OK | doi:10.1016/j.egypro.2014.08.097 abstract (60 ms reverse-bias frames) |
| P-16 | ideas §0 | Käsemann 2008 IR methods, breakdown sites | OK | doi:10.1109/pvsc.2008.4922478 abstract (local breakdown at −7 V; ~10 ms hotspot detection) |
| P-17 | ideas T35 | ultrasound lock-in thermography finds cracks in wafers and cells, incl. optically invisible ones | OK | openalex:W2189012330 (Rakotoniaina et al. 2004) abstract. Wafers and cells only, not laminated modules (ideas already flags this as S risk) |
| P-18 | capture §2, §5 | Gallardo-Saavedra 2020 Sensors: illuminated and dark IR complementary | OK | doi:10.3390/s20164395 abstract |
| P-19 | capture §3 | Ciocia 2019: low-cost Si-sensor EL camera, lab and field | OK | doi:10.1109/pvsc40753.2019.8980711 abstract |
| P-20 | capture §2 PL row | "passive EL/PL by inverter switching outdoors (R: doi:10.3390/s24051539)" | FIX | as D-28: electronic board switching module polarity / open circuit, InGaAs + bandpass, lock-in |
| P-21 | ideas T20, T21, T28 | Paggi 2014: geometric inactive-area criteria exist; cracks recover conductivity on unloading; fatigue under cyclic bending | OK | doi:10.1038/srep04506 abstract |
| P-22 | ideas §0, T31 | "daylight PL is reported to identify inactive areas" | FIX (wording) | doi:10.1002/pip.3525 is a proof of concept: lower image quality; "promising for identification of ... large area damage and inactive areas". Say "proposed as promising for" |
| P-23 | ideas T26, T29 | drone IR > 1 module/s; drone daylight EL at 120 fps, SNR 4.6 near one sun; aircraft daylight PL over 149 MW by inverter switching; aerial PL (night, own light source) | OK | doi:10.1088/2516-1083/ac890b; doi:10.1109/jphotov.2020.2978068; doi:10.1002/pip.3807; doi:10.1002/pssr.202300059 abstracts |
| P-24 | ideas T08 | cross-plant IR: ResNet-34 + SupCon + kNN, AUROC 73.3 to 96.6%, 2.92 M images | OK | doi:10.1002/pip.3518 abstract |
| P-25 | ideas T18 | AC-GAN on InfraredSolarModules, FID 35.4, ECE 1.5% | OK | doi:10.1038/s41598-026-67806-1 abstract |
| P-26 | ideas T30, datascout E9 | Kunze 2025 QAM: EL + thermography + reflectance; finger interruptions lower FF locally | OK | doi:10.1002/solr.202500253 abstract |
| P-27 | ideas T34, T32 | snail trails correlate with microcracks; UVF varies with encapsulant / backsheet | OK | doi:10.1109/jphotov.2014.2330495; doi:10.1002/solr.202400566 abstracts |
| P-28 | ideas §5 | factory EL + electro-thermography fusion detects "scratches, covers, cracks" | OK | doi:10.3901/jme.2021.08.098 abstract (which modality sees the scratches is not stated) |
| P-29 | ideas T01, capture §4; datascout E7 | Almukhtar 2026: homography + ECC; "statistically paired"; synthetic triplets from ELPV + Kaggle RGB; calls ELPV pixel-masked | OK | doi:10.3389/feart.2025.1702396 abstract and §2.1 (full text, local) |
| P-30 | ideas T38 | Fioresi 2022 (UCF-EL) authors include D. J. Colvin | OK | doi:10.1109/jphotov.2021.3131059: Fioresi, Colvin, Frota, Gupta, Li M., Seigneur, Vyas, Oliveira, Shah, Davis |
| P-31 | ideas §0.1, §3 | aerial IR per IEC TS 62446-3 ~3 cm/px, ~5 × 5 px per 15 to 16 cm cell (FLIR, Raptor Maps, Sitemark) | OK + FIX (link) | Sitemark: "maximum Geometric resolution of 3cm/pixel", "about 25 measurements per cell", 600 W/m² minimum. The Raptor Maps URL now redirects to a page with no GSD figure (it states ≥ 640 × 512 sensors and ≥ 600 W/m² POA): cite Sitemark, drop or re-label Raptor Maps. FLIR page not read |
| P-32 | capture §2 | IEC TS 60904-13 uses 0.1 × Isc for crack quantification | OK | VDE preview TOC: "Figure C.1 – Single cell region of a module with 0,1 × Isc applied showing crack types" (via search). The 1.0 × Isc point is already tagged weak by capture |

## 4. Capture facts: WattCycle, IIT Mandi, prices

| # | Claim | Verdict | Correct fact and source |
|---|---|---|---|
| C-1 | Powar founder and PI of WattCycle Sustainable Solutions; PV recycling; ₹10 crore CSR grant from GIC Re | OK | https://is4ie.org/members/5321 (also: "Associate Professor & Dean Finance at IIT Mandi", leads the Energy Engineering Laboratory) |
| C-2 | "DPIIT-recognised deeptech startup"; "June 2025 to present" (from the CV PDF) | UNVERIFIABLE | Not on the profile page; I did not open the CV PDF. Incorporation date is confirmed separately (C-3) |
| C-3 | Incorporated 17 Jun 2025, active; Village Salgi, P O Kamand, Mandi, HP 175075; directors Priyanka Kajal, Atul Dhar; MCA "business activities n.e.c." | OK | Tracxn page (same URL as capture) |
| C-4 | wattcycle.ai: tagline; Atlas digital twin; drone health monitoring ("thermal and RGB drone flights ..."); ReVive Solar; GIC Re; IIT Mandi Catalyst. Tagged R from search snippets | OK + FIX (source) | Verified from the site's own JS bundle text (`wattcycle.ai/assets/index-*.js`, read as text): "Thermal and RGB drone inspections for hotspot detection, fault identification, soiling maps, and structural checks"; "ReVive Solar ... PV module recycling and circularity services"; GIC Re CSR; "Incubated at IIT Mandi Catalyst"; location Himachal Pradesh. Cite the site, not snippets |
| C-5 | "Conflict": handbook calls WattCycle "a solar asset-management company"; same company "likely, not confirmed" | FIX (resolves toward a match) | The site's Atlas manual text says "WattCycle Atlas is a comprehensive solar asset management platform", and its menu has "Asset Management – Plants, module batches, inventory, recycling" (same JS bundle). So the handbook wording fits this company; still confirm the contact with Om. Caveat: the Atlas app in the bundle runs on demo seed data ("Defect zones reflect drone inspection seed data"), so the site does not show that real drone IR archives exist |
| C-6 | ~14% of modules that passed I-V + EL screening failed wet leakage | OK | pv-magazine 2026-08-19 ("around 14%") |
| C-7 | IIT Mandi AMRC lists ~36 instruments; no IR camera, thermography, EL, PL imaging, solar simulator, source meter, InGaAs camera | OK | https://amrc.iitmandi.ac.in/exbook.php: 36 listed; only spectroscopic PL (Raman & PL spectrometer) |
| C-8 | Topdon TC001: 256 × 192, 8 to 14 µm, 25 Hz, NETD < 40 mK; ₹20,010 (Aajjo, undated) | OK | au.topdon.com (radiometric export not stated; Windows "TCView" app listed); Aajjo page ₹20,010, no date |
| C-9 | InfiRay P2 Pro: 256 × 192, 12 µm, 25 Hz, NETD ≤ 40 to 50 mK; €206 ex VAT (eleshop) | OK | Search of eleshop: €205.79 ex VAT; official sheet NETD ≤ 50 mK, retailer ≤ 40 mK |
| C-10 | InfiRay P2 Pro US$349 (Newegg US) | UNVERIFIABLE | Page 403; search shows Newegg listings ~$238 to $399 by seller / bundle |
| C-11 | HIKMICRO Pocket2 ₹78,269 incl. GST, 256 × 192 | OK | Toolbuy page (₹66,330 + ₹11,939 GST) |
| C-12 | FLIR E8 Pro US$3,249 (FLIR US); 320 × 240, 40 mK | FIX | flir.com today: **US$3,299**; 320 × 240; < 40 mK at 30 °C. India listings not re-checked |
| C-13 | DJI Mavic 3 Thermal ₹5.29 lakh ex GST (XBoom) | OK (clarify) | XBoom: ₹528,571 ex GST is the "Mavic 3 Thermal Enterprise (TE)" listing; the shoulder-bag combo is ₹570,476 ex GST |
| C-14 | MavDrones ₹5.77 lakh incl. GST | UNVERIFIABLE | Page 403 |
| C-15 | Wanptek KPS6020D 60 V 20 A 1,200 W ₹19,701 incl. GST (Zbotic; 20 to 25 day delivery) | OK (price) / UNVERIFIABLE (delivery) | Search snippet of the Zbotic page: ₹16,696 + GST ≈ ₹19,701; page itself 403 |
| C-16 | OWON SPE6103 ₹12,099 (Robocraze), 300 W cap | UNVERIFIABLE | Page 429 |
| C-17 | Tonghui RK-6020P 60 V 20 A 1,200 W ₹1,14,900 (Cart2India) | OK | Cart2India: ₹114,900, "inclusive of custom duties, GST, freight" |
| C-18 | UV torch 365 nm 10 W ₹1,790 lowest recorded | OK (stale) | price-history.in: ₹1,790, but "last checked 672 days ago"; mark as an old price |
| C-19 | FLIR E96 £9,899 ex VAT (RS UK) | UNVERIFIABLE | Page 403 |
| C-20 | P0 kit ₹45k to ₹55k (S) | OK (arithmetic) | ₹20k to 30k + ₹19.7k + ₹1.8k to 4.5k = ₹41.5k to 54.2k, plus small items (S) |
| C-21 | 256 px over a 1.65 m module ≈ 6.4 mm/px, ≈ 24 px per 156 mm cell; 24 MP ≈ 0.28 mm/px | OK (arithmetic) | 1650 / 256 = 6.45 mm; 156 / 6.45 = 24.2; 1650 / 6000 = 0.275 mm (S) |
| C-22 | E-tagged project facts: handbook/01 l.18 "solar asset-management company"; handbook/13 l.175 (~300 µm per px), l.203; spec_b3_scuff.md 649 px and 2.5k to 4.6k px; B2 scuff gate sens 1/8 | OK | grep of the cited files |

## 5. Tags and unsourced numbers (cross-file)

| # | File | Item | Verdict | Fix |
|---|---|---|---|---|
| T-1 | ideas, E-tagged numbers | 1.1 GPU-h per R34 run (doc 14); inactive in 43 / 478 train (doc 02 §7); top 3 test cells 59%; inside / ring 0.34 vs 0.55; 99% of inactive components touch a crack; HC −0.0228, CI [−0.054, +0.005] (doc 21 §2); SUPPF 0.4289 vs SKR2 0.4567 (doc 21 §4.3); SC recall 0.126, 75% (doc 18 §U) | OK | All found in the cited files, at the cited lines (doc 14 GPU-h row is l.323, as ideas wrote; my earlier "l.322" was a miscount, corrected 4 Nov) |
| T-2 | datascout A1 | "cracks present but not the main mode [R]" | FIX | S (see D-9) |
| T-3 | ideas §0, §0.1 | reverse-bias mechanism and Köntges-A mapping tagged R | FIX | S (see P-2, P-3) |
| T-4 | ideas T38 | "ruled out by cell count" presented as E | FIX | over-read (see E-2) |
| T-5 | ideas §1, datascout A1 notes | "A1's IR is forward-bias thermography at known currents (S)"; "OSF IR follows this protocol ... unconfirmed [S]" | FIX (upgrade S → R) | R from the OSF file names (see D-5) |
| T-6 | capture §1.1 | wattcycle.ai facts tagged R from snippets | FIX (source) | R from the site itself (see C-4) |
| T-7 | all | numbers with no source | none found in the sampled rows | Every sampled number carried an E / R / S tag; S arithmetic checked in C-20, C-21 |

## 6. What changes for synth (the optimistic reading, now on firmer facts)

1. **A1 has bias-matched EL + dark forward-bias IR on about 157 modules, not an "unconfirmed share".** IR at 3.39 A (≈ 1 × Isc) after 180 s, raw txt + cropped jpg per module; EL at the same 3.393 A in the 6-level NEF sweep (R: OSF listing). The whole A1 IR folder is 0.26 GB. So G0 and the A1-based ideas (T02, T06, T07, T12, T15, T26, T27, T37) have about 10 times more paired IR than datascout's bottom line implied, at a small download (S: IR 0.26 GB + one EL frame per module ≈ 2.2 GB for all 157, or ~0.15 GB for 10).
2. **Public modules with EL + IR: about 215** (A1 157, A2 15, A3 43), not "at least 59".
3. **csr6t's paper is Colvin 2023 IEEE JPV**, not Li 2024 (ideas Q6 answered). Li 2024's protocol facts still hold as a capture template.
4. **Physics calibration, not a kill:** A1 / A2 IR is dark forward-bias IR. JRC 2017 (Berardone et al.) found dark IR gives "few local information" while illuminated IR separates damage classes; Li 2024 got SSIM 0.82 on solder-bond modules. So G0's expected signal is per-cell (Rs, hot cells), as ideas already assumes.
5. **C1 (Polenghi) includes abrasion and scrape damage** with EL + NIR + visible and power: a public probe of what a surface scuff does in EL (S).
6. **Capture partners:** WattCycle's own site calls Atlas "a comprehensive solar asset management platform", so the handbook wording fits; and **IIT Bombay (Rajesh Gupta's group)** does module EL + DLIT + IR in India, a lead for P2 lock-in.
7. **A3 drone IR is ~1 to 3 cm/px native**, i.e. cell-level (5 to 16+ px per cell); the 363 × 605 arrays are resampled.

## 7. FIX lists sent (pass 1)
- `datascout`: D-3, D-4, D-5, D-6, D-9, D-12, D-13, D-17, D-19, D-21, D-24, D-28, D-34, D-39, D-40; adds D-25, D-41, D-42, D-46.
- `ideas`: E-2, T-5 (§1 A1 IR and Q6), §1 download sizes (A1 bulk EL is NEF ~13.8 MB; A1 IR folder 0.26 GB for all modules; A2 IR folder 0.02 GB), P-2, P-3, P-22, P-31; note §6 items 1, 2, 4, 5.
- `capture`: C-4, C-5, C-12, C-13 (clarify), P-7, P-12, P-20; mark C-2, C-10, C-14, C-15 delivery, C-16, C-19 as not re-verifiable; C-18 as an old price.

## 8. Re-check log
- **capture** v1.2 (md5 3340e047, read 4 Nov after pass 1): C-2, C-4, C-5, C-12, C-13, P-7, P-12, P-20 applied correctly; MARKs added. One residual: §5.1 "Delivery (R)" still cites the Zbotic 20 to 25 day delivery and the 1 to 5 day OWON seller as R; both pages refused me (403 / 429), so add "not re-verified by check" there too (R-1). Otherwise **closed**.
- **datascout** v3 (table 0288457c, notes 56a144f8): all 15 FIX + 4 ADD applied correctly. Three small residuals (sizes, R from the OSF listing): R-2 A1 `EL-Derived_Cell_Dark_I-V` is 158 txt + 1 xls (`diode_fit_outputs.xls`, 1.6 MB), 3.8 MB, not "159 txt, about 2 MB"; R-3 A1 UVF is 8.1 to 13.1 MB per jpg, 2.01 GB (R, not S); R-4 A2 one-bias EL for the 15 IR modules is 16 frames, 0.237 GB, not ~0.21 GB. Plus the new A3 facts from the DTU slides (RP-2 below). **Closed** once those are in.
- **ideas** v1.2 (c9239651): all fixes applied. My pass-1 note "doc 14 is l.322" was my miscount; ideas' l.323 is right (corrected in T-1 and S-12). Residuals: R-5 the FLIR link in §0.1 now redirects to a 404 page (flir.com/en-ca/...), so its "5 × 5 px per six-inch cell" example cannot be re-verified; Sitemark alone supports the figure. R-6 T22 still writes "mode-A branch cracks also silent (R: Dhimish)"; the mode-A mapping is S, as fixed elsewhere. R-7 G0 step 1 "≈ 0.65 GB" is 0.26 + (10 to 20 × 14.4 MB) + 0.25 ≈ 0.65 to 0.80 GB. **Rules note RN-1:** G0 step 1 uses all 157 A1 IR captures, but Om approved only the 10-module A1 subset (`om_2026-11-04_decisions.md` (1)); the other ~147 modules' IR (≈ 0.24 GB) is an extension and needs Om's OK. **Closed** apart from these.

---

# Pass 2: synth (`synth/ranked_ideas.md` 9fc511af, `synth/top3.md` 3d8da1f7, `synth/SUMMARY.md` 7aa627a3)

**Method.** Every number in SUMMARY.md was traced to its input file and, where it is a public-data size, recomputed from the OSF / Mendeley file listings (names and sizes only; scratchpad JSON). E paths were opened at the cited lines. The novelty claim was searched again (Research MCP ×2, web ×1, Zenodo API ×3, Hugging Face API). Scores and probabilities are S by design and were not "checked", only their factual premises.

**Sizes recomputed from the listings (R for counts and bytes; sums are arithmetic):**
- A1 per module: one EL NEF at 3.39 A ≈ 14.4 MB (158 such files, 2.27 GB); IR ≈ 1.62 MB (raw txt + cropped jpg + cropped txt; folder 257.8 MB for 157 modules); UVF jpg mean 12.65 MB (8.1 to 13.1; 159 files, 2.01 GB). So 10 modules with EL + IR + UVF ≈ 0.29 GB.
- A1 `EL-Derived_Cell_Dark_I-V`: 158 txt + 1 xls = 3.82 MB (the xls is 1.6 MB). `dark_I-V` (module level) 158 txt 0.24 MB; `I-V` 160 txt 0.23 MB; `pseudo_I-V` 159 txt 4.03 MB.
- A1 full 6-level EL sweep ≈ 84 MB per module (NEF). `close-up_EL_PL` 11 files 111 MB.
- A2: 16 EL frames at 5.289 A for the 15 IR modules = 237 MB; `indoor_IR` 15.7 MB; together ≈ 0.25 GB.
- A3 642.6 MB (Figshare API). C1: EL 84 PNG 204 MB, HDR 929 MB, BN 242 MB, total 1,375 MB (Mendeley API).
- Picks 1 + 3 download: 0.643 + 0.25 + 0.29 + 0.004 ≈ **1.19 GB**, so "about 1.2 GB" holds.

| # | File | Claim | Verdict | Correct fact and source |
|---|---|---|---|---|
| S-1 | SUMMARY §3.1, top3 pick 1, ranked | picks 1 + 3 download about 1.2 GB | OK | 1.19 GB (sum above) |
| S-2 | SUMMARY §3.1; top3 pick 1 data | A2: 15 IR modules with one EL each ≈ 0.23 GB (SUMMARY) / 0.21 GB + 15 MB (top3) | FIX (minor) | 16 EL frames at 5.289 A (one module has two) 0.237 GB + IR 15.7 MB ≈ **0.25 GB** |
| S-3 | SUMMARY §3.1; top3 pick 1 data; ranked T37, T32 | A1 10 modules ≈ 0.29 GB, "EL 16.7 MB + IR ~1.6 MB + UVF ~10.5 MB each"; T32 "UVF 8.1-12.9 MB + EL 16.7 MB" | FIX (components; totals OK) | EL is a Nikon NEF ≈ **14.4 MB** (16.7 MB is the 2018 TIF); UVF mean **12.6 MB** (8.1 to 13.1). Totals 0.29 GB and T32's 0.27 GB stand |
| S-4 | SUMMARY §3.1 ("about 2 MB"); top3; ranked T15 ("159 txt ≈ 2.2 MB") | A1 dark I-V files | FIX (minor) | `EL-Derived_Cell_Dark_I-V` = **158 txt + 1 xls, 3.8 MB**; module `dark_I-V` adds 0.24 MB |
| S-5 | SUMMARY §3.1; top3 pick 3 | 30 more A1 modules (EL + IR) ≈ 0.55 GB ("about 18 MB per module") | FIX | 14.4 + 1.6 = 16 MB per module, so **≈ 0.48 GB** |
| S-6 | top3 pick 3; ranked T37 | "all 159 at one EL bias ≈ 2.7 GB EL + 0.25 GB IR (+ 2.0 GB UVF)" | FIX | **158 modules** have an NEF at 3.39 A, **2.27 GB**; IR 0.26 GB covers **157** modules; UVF 2.01 GB (159 files). All three ≈ 4.5 GB |
| S-7 | SUMMARY §3.1; ranked T31 | A1 close-up EL + PL ≈ 0.18 GB (11 × 16.7 MB) | FIX | **0.11 GB** (6 TIF at 16.7 MB + 5 JPG) |
| S-8 | SUMMARY §3.1; ranked X3 | Polenghi EL ≈ 0.20 GB; whole set ≈ 1.38 GB | OK | Mendeley API: EL 204 MB; total 1,375 MB |
| S-9 | ranked X4 | "A1 I-V files (size unconfirmed)" | FIX (fill in) | `I-V` 160 txt 0.23 MB, `pseudo_I-V` 4.0 MB, `dark_I-V` 0.24 MB: ≈ 4.5 MB in all |
| S-10 | ranked T33 | "A1 sweep (more EL files per module; size unconfirmed)" | FIX (fill in) | 6-level NEF sweep ≈ 84 MB per module (S from listing): 10 modules ≈ 0.84 GB; whole EL folder 14.95 GB |
| S-11 | top3 pick 3 (item b) | "no public set is registered EL + IR at cell level" (S) | OK (as S, reworded) | Not found in datascout's sweep, nor in my re-search (Research MCP ×2, web, Zenodo API ×3, HF API); Almukhtar 2026 §2.1 also states the absence of physically paired sets. Write "we found no public set ..." rather than "none exists". Near hits are not registered EL + IR: Polenghi C1 (EL + NIR + visible), Zenodo 14971611 (EL of shunted cells, 8 MB), Zenodo 13862021 (perovskite EL / PL / DLIT figure data only) |
| S-12 | all three (item c) | E paths: handbook/18 l.357, l.362; handbook/11 row 42; handbook/14 l.320-323, l.419; handbook/02 §7 (43 of 478, old masks) | OK | l.357: 75%, 0.126; l.362: "0 half-cut cells" and "649 crack in 6 cells"; handbook/11 row 42 (file l.112): train scuff IoU 0.000 in all 5 seeds; handbook/14 l.323: 1.1 GPU-h per R34 run; l.419: PF2E, `pf2e_infer.py`, CPU fp32, gaint; handbook/02 §7 l.249: 43 of 478 train (old masks) |
| S-13 | ranked §2, SUMMARY | other E: E1 crack recall 0.215 (handbook/00 fact 10); 3 images hold 87% of E1 inactive (session record §0); thesis parts (handbook/02 §1); power out of scope (handbook/02 §9); handbook/13 l.203; BenchmarkEL no licence file; E1 106 cells | OK | handbook/00 l.119; SESSION_RECORD l.12; handbook/02 l.45, l.295; F04 census l.64 ("no licence file; public"); team README |
| S-14 | top3 pick 3 step 2; ranked §4, §5 | "A1's dominant defect is solder-bond Rs, not cracks (R: Li 2024 via datascout)" | FIX (source) | Cite csr6t's own paper: Colvin et al. 2023, doi:10.1109/jphotov.2023.3238278: "losses are primarily resistive ... corrosion of the rear contact Ag/solder interface" (check D-6) |
| S-15 | SUMMARY §1(3), decision 5; top3 pick 1 "Why", pick 2 step 1 | WattCycle identity "unconfirmed"; "our docs say asset management" | FIX (update) | The company's own site calls Atlas "a comprehensive solar asset management platform" (check C-5), so the handbook wording fits; only the contact needs Om's confirmation. Keep the caveat: the site's Atlas app runs on demo seed data, so it does not prove that drone IR archives exist |
| S-16 | SUMMARY §4 U1 | ask UCF: "IR bias, current and camera for csr6t ... is Li et al. 2024 the csr6t paper?" | FIX | Answered from the OSF page and file names: IR at 3.39 A (≈ 1 × Isc), 180 s; the paper is Colvin 2023 (check D-5, D-6). Keep: camera / emissivity, format of the raw txt, UCF-EL overlap, AZ modules of Li 2024 |
| S-17 | SUMMARY §1(1) | A1 "156 modules; EL bias sweep, IR, UVF, I-V, per-cell dark I-V" | FIX (add the key fact) | Add: forward-bias IR at ≈ 1 × Isc on **157 modules**, EL at the same current (check D-5). Public modules with EL + IR ≈ 215 (A1 157, A2 15, A3 43). This is the fact picks 1 and 3 rest on |
| S-18 | SUMMARY §1(1) | "None has half-cut cells or scuff" | FIX (tag) | A1 / A2 are full-cell mono Al-BSF (R: OSF titles and tags; A1 36-cell). A3's cell count and technology are unreported (datascout asks DTU, U2), so for A3 this is S |
| S-19 | SUMMARY §1(1) | "5 EL + PL sets, 4 EL + VIS / NIR sets (one pixel-aligned)" | FIX (wording) | B4 and B5 are PL-only pools (not paired with EL), so 3 EL + PL sets + 2 PL pools. Of C1 to C4 only C1 pairs images of the same cell (C2 pairing unconfirmed, C3 is time series, C4 unpaired pools) |
| S-20 | top3 pick 1 step 3 | "A2 first: temperature matrices at 5.289 A (R)" | FIX (tag) | R: the OSF page says "The IR images have both text and converted jpg images", 537,840 B each; that the text is a temperature matrix is S (same as datascout's tag) |
| S-21 | SUMMARY decision 4; top3 pick 2; ranked §5 | 300 W OWON "1-5 day shipping, R" | UNVERIFIABLE | Seller page (theengineerstore.in) returned 429 to me; capture's R, not re-verified |
| S-22 | top3 pick 2 | 1.2 kW Wanptek "20 to 25 day delivery (R)" | UNVERIFIABLE | Zbotic page 403; the price ₹19,701 is confirmed via a search snippet (check C-15) |
| S-23 | top3 pick 2 | UV torch ₹1,790-4,522 (R) | FIX (minor) | ₹1,790 is an old price (price-history.in last checked ~672 days ago); ₹4,522 not checked |
| S-24 | top3 timeline; capture §5.1 | W3 = 18-24 Nov (synth) vs "Week 3 (16 to 22 Nov)" (capture) | FIX (consistency) | Synth counts W1 = Wed 4 to Tue 10 Nov; capture uses calendar weeks. Give Om one range in SUMMARY |
| S-25 | ranked T38 (P 0.05) | premise "A1 ruled out by cell count" (ideas T38) | FIX (premise) | Over-read (check E-2): only the 201 complete 60-cell UCF-EL modules are excluded; 109 partial modules have highest cell position ≤ 36. The P is synth's call |
| S-26 | top3 pick 3 data | "CC BY 4.0 allows a derivative with attribution (R: datascout); check to verify" | OK | CC BY 4.0 (the licence OSF links, creativecommons.org/licenses/by/4.0/legalcode) lets you share and adapt for any purpose with credit, a licence link and a note of changes, without implying endorsement (same terms quoted in Mendeley's licence text). Caveat (S): bundling E-PF predictions from a model trained on BenchmarkEL (no licence file, E: F04 l.64) is a separate question for Om, already in decision 8 |
| S-27 | SUMMARY §1(1) | A3: 43 artificially degraded modules; drone IR + EL + I-V; 642.6 MB; A2 42 modules, about 16 forward-bias captures; all CC BY 4.0; no masks | OK | check D-11, D-13, D-15, D-16 |
| S-28 | SUMMARY §1(2) | thermal misses cracks that isolate nothing (R: Dhimish 2021 / 2022; DTU 2025); pretraining weak (E: A8 KILL, MIM n.d., P15 null) | OK | P-1, P-4, D-16; handbook/00 l.16. Optional nuance: Li 2024 §4 put one whole-cell hotspot with no EL signature down to microcracks |
| S-29 | SUMMARY §1(3) | P0: 1 day, 5-6 modules, EL 0.1 and 1.0 × Isc, ₹45k-55k if an EL rig exists; IIT Mandi central facility lists no IR camera or EL rig | OK | capture §0, §3, §5; check C-7, C-20 |
| S-30 | SUMMARY §2 | kill rules for picks 1 to 3 | OK | match ideas G0 / T26 / T15 / T12 and capture §5 |
| S-31 | SUMMARY §1(2) | "40 ideas, 43 after merging" | OK | 40 − 2 (T22, T34 into X1) + 5 (X1 to X5) = 43 |
| S-32 | ranked T26 | A3 pairs drone IR with EL on modules with induced cracks and disconnections | OK | D-15, D-16 |
| S-33 | ranked T08 (add, optional) | out-of-domain IR checks use D1 / D4 / D11 | OK + add | New thermal-only set not in datascout's table: Zenodo 10.5281/zenodo.20860870, "sUAS Infrared Image Dataset for Photovoltaic Module Fault Classification" (2026-06-25, CC BY 4.0, 4.0 MB): 3,675 grey crops in 8 classes (Cell 249, Multi-Cell 96, Open-Circuit 431, ... Normal 2,835), annotated on a 3.13 cm/px orthomosaic (Zenodo API) |

**Pass 2 counts:** 33 items: **OK 13, FIX 18, UNVERIFIABLE 2** ("OK + add" counted as OK).

**Does anything change the top 3? No (S).** No pick rests on a wrong fact. The fixes strengthen picks 1 and 3 (A1 has Isc-level forward-bias IR on 157 modules; the shared download is ~1.2 GB as stated) and make pick 2's partner more likely to be the right company. T38's low P loses its main premise, but T38 is far from the top band.

## 9. Pass 2 re-check log
- (pending synth's reply)

---

# Pass 3: new deliverables after Om's decisions (team-lead's items a to c)

## 10. (a) Quick review: `pick3/plan_pick3.md` v0.9 (b56afa38), before freeze
Scope: do the readouts and kill signals match `synth/top3.md` pick 3, and are they fixed before any number is read? No redesign.

| # | Item | Verdict | Note and source |
|---|---|---|---|
| PL-1 | Kill / success rules vs top3: T15 (< 50% coverage or no spread), T37 (> 5% of a cell side), T02 (kill Δ < +0.03, success ≥ +0.05), T12 (kill < 50 flagged or purity < 70%; success ≥ 200 at ≥ 70%) | OK | Same thresholds as top3 / ideas. The added operational choices (no spread = both spreads < 0.05; pick-level T37 kill > 30% of modules; T12 read on the 157-module projection) are additions frozen before reading, not changes |
| PL-2 | Frozen before any number is read | OK | v0.9 from metadata only; v1 md5 to `log.md` before reads; format discovery allowed after freeze; amendments dated |
| PL-3 | T15 parameter P: "the per-cell series-resistance-like parameter if the file has one", read from `<serial>_EL-derived_cell-dark-I-V.txt` | FIX (fact) | The per-cell two-diode **fit outputs** are in one file, `EL-Derived_Cell_Dark_I-V/diode_fit_outputs.xls` (1,615,360 B; OSF description: "The analysis outputs are found in ... diode_fit_outputs.xls", n1 = 1, n2 = 2, other parameters free). The 158 txt files (13,958 B) are the EL-derived cell dark I-V curves (S from name). The project venv has **no .xls reader** (xlrd, openpyxl, pandas absent; E: import test 4 Nov) and installs are not allowed. So state before freeze: either P comes from the frozen fallback (current at the highest common voltage, from the txt curves), or Om allows a reader / conversion. Also confirm the xls is in datascout's download (it sits in the approved dark I-V folder) |
| PL-4 | §1 "13,958 B each, 159 rows in the listing" | FIX (minor) | 158 txt + 1 xls (OSF listing) |
| PL-5 | §3.3 NEF at 3.392 A is "~2 weeks after the 2022 IR captures" | FIX | Per module, EL (NEF at 3.39 A) date minus IR date: **median +4 days, range −7 to +15, same day for 58 of 156 modules** (R: OSF file-name dates) |
| PL-6 | §1 "every A1 IR is forward-bias at 3.393 A" | FIX (minor) | 78 files at 3.392 A, 79 at 3.393 A, plus 2 at 1.354 A (no exposure field) |
| PL-7 | T12 purity: top3 says E-PF overlap or a 0.5 h glance; the plan uses an EL-threshold proxy (EL dark ≥ 5%) and kills on proxy purity < 70% with ≥ 10 flags | FIX (label only) | A proxy is fine while E-PF is held. Label it "proxy purity" and the kill "provisional until E-PF / glance", so a proxy kill is not read as top3's T12 kill. No change to the rule |
| PL-8 | Data scope | OK | Dark I-V of all modules + 10-module subset = Om's approval; extension flagged as needing OK; E-PF held; no GPU; no test / E1 / BenchmarkEL reads |

## 11. (c) Fact-check: `ideas/drone_only.md` v1 (28f5b0a5)

| # | Claim | Verdict | Correct fact and source |
|---|---|---|---|
| DO-1 | §0: drone IR "can see ... PID-type warm cells (R: doi:10.1016/j.seja.2023.100049)" | FIX | The DTU drone study found "Modules affected by PID and glass cracks did not exhibit pronounced thermal anomalies under the tested conditions" (doi:10.1051/epjpv/2025020 abstract; slides: PID ΔTmax 2 °C vs healthy 1.5 °C). seja 2024 mapped PID-s cells with forward-bias ("inverse") IR in the dark, not sunlit drone IR; Dhimish 2022 saw ~50 °C PID hot spots on single cells under STC. Say: severe PID can heat (lab), early PID was not pronounced in drone IR |
| DO-2 | W09: "the worst hot spots occur at 40-60% shading (R: Dhimish 2021)" used for opaque-card shading of a module cell | FIX (tag) | Dhimish 2021 (full text, §Results "Shading ratio vs hotspots development"): 12 single poly cells dismounted from modules, under a sun simulator at STC, IR from the rear after 10 min; "progressive shading of a solar cell affected by mode 3 crack" at 25 / 40 / 60 / 80 / 100%; no hot spot at 80 to 100%. Not an in-module reverse-bias test, so its use for W09 is S |
| DO-3 | W02: the aerial IR review says orthomosaicking and path planning are rarely automated | OK | doi:10.3390/en15062055 abstract ("only a few studies explored the automation ... optimal path planning, the orthomosaicking ...") |
| DO-4 | W12: UAV thermal + RGB fusion for PV inspection exists | OK | doi:10.32620/reks.2025.4.13 (Lysyi et al. 2025; PVF-10 mAP@0.5 0.903) |
| DO-5 | W14: active / transient IR review | OK | doi:10.3390/s23218780 (Zhao et al. 2023; pulsed, lock-in, ultrasonic, eddy current; PV section) |
| DO-6 | W05: irradiance matters more than altitude; soiling hotspots 5-10 °C cooler higher up; W10: < 1 cm/px at 8 m | OK | doi:10.1051/epjpv/2025020 abstract |
| DO-7 | W01: E1 opened many times (handbook/21 §9) | OK | §9 ledger: six registered openings |
| DO-8 | W04, W06, W08, W11, W12 citations (D1 / PVF-10 numbers; pip.3518 AUROC 73.3-96.6%; srep04506; s20164395 incl. "fourth quadrant"; Köntges 250 / 720 modules/h; snail trails) | OK | as P-24, P-21, P-18, P-9, P-27 |
| DO-9 | W11 UV torch "₹1,790-4,522" | FIX (minor) | ₹1,790 is an old price (C-18); ₹4,522 not checked |

## 12. (c) Fact-check: `capture/replan_pick2.md` v1.1 (0858bc3a)
The DTU slides (Spataru, IEA PVPS Task 13, ISFH 2025, the URL capture cites) were read as text (`pdftotext` on the copy WebFetch saved; 26 slides).

| # | Claim | Verdict | Correct fact and source |
|---|---|---|---|
| RP-1 | §2.1 / §2.2 from the DTU slides: cracks ΔT max ~1 °C, hard at 600 W/m², unidentifiable below; < 10% and < 30% cracked cells warmer than > 30%; type 4 disconnections > 3 °C, identifiable to 600 W/m²; diodes and soiling ΔT > 10 °C even at 200 W/m²; IEC TS 62446-3 via slides: > 600 W/m², wind < 28 km/h, low cloud, max 3 cm/px; drone + RGB + LWIR ~6 k€, SWIR ~10-15 k€, EL at night needs back-powering | OK | Slide text matches each item (slides 2, 4, 5, 9-14) |
| RP-2 | (new facts from the same slides, for datascout / synth) | ADD | Slide table (R): cell cracks **8 modules** (mono PERC 305 W, 69 cells cracked by mechanical stress, 4-5% power loss); interconnections 8 (ribbon cut from the backsheet, 98 cells, 3-14%); PID 6 (5%); shorted bypass diode 7 (mono PERC 305 W, bifacial PERC 295 W, **bifacial PERC 540 W half-cut**, 33-66%); glass crack 2 (bifacial PERC 540 W **half-cut**, < 1%); soiling 1 and 2: 6 each. EL "100% and 10% Isc"; drone DJI Mavic 3T. Two consequences: (1) **A3 does contain half-cut modules** (diode, glass-crack and soiling groups), so "none has half-cut cells" is false for A3; (2) the per-class counts sum to 31 degraded + 12 soiled = 43, so the paper's "43 ... artificially degraded" probably includes the soiled modules (S; the abstract reads otherwise), and pick 1's A3 crack group is only 8 modules |
| RP-3 | Pi HQ camera: IMX477, 4056 × 3040, 1.55 µm, C/CS mount, max exposure 670.74 s; IR-filter removal irreversible and voids the warranty; Camera Module 3 NoIR: IMX708, 4608 × 2592, 1.4 µm, 112 s | OK | raspberrypi.com camera documentation (HQ camera also has an M12 variant) |
| RP-4 | Resolution arithmetic (0.41 mm/px and ~380 px per cell for 4056 px; 0.36 for 4608; 0.43 for 3840; 0.55 for 3008; 0.28 for 24 MP); Mavic 3T GSD ≈ altitude / 696 px | OK | 1650 mm / px count; 696 px = half-diagonal 409.8 px / tan(30.5°) for DFOV 61° on 640 × 512 (S arithmetic, matches DTU's < 1 to 3 cm/px at 8-20 m) |
| RP-5 | ZWO ASI678MM ₹62,145 incl. GST and import duty (Tanotis) | OK | Tanotis listing title via search |
| RP-6 | Pi HQ ₹4,990, NoIR ₹2,919, Pi 5 ₹5,799 (Robocraze) | UNVERIFIABLE | Robocraze returned 429 |
| RP-7 | NISE Gurugram lists an EL test per module and STC testing; fee not public | OK | testing.nise.res.in page ("Electroluminescence Test – Test per sample of PV module"; fees need login). Snippet fees (₹4,550 STC etc.) not re-verified |
| RP-8 | NIT Hamirpur: teaching kits, DC regulated supply, meters; no EL or IR camera | OK | nith.ac.in inventory PDF (text extracted): Ecosence PV kits, "Kaptel MAKE dc regulated power Supply", panel meters |
| RP-9 | Aerial EL review; Si vs InGaAs outdoor EL comparison | OK | doi:10.1016/j.solmat.2024.113210 (Mahdavipour 2024); doi:10.1515/zna-2019-0025 (Doll et al. 2019, reference spots; Si and InGaAs compared for signal levels) |
| RP-10 | Li 2024 cooled Si CCD + 850 nm LP; Ciocia low-cost Si EL camera; s20164395; Köntges 250 modules/h; IIT Bombay group | OK | as P-6, P-19, P-18, P-9, P-12 |
| RP-11 | Mobile PV labs (Mahindra Susten 2017, DNV GL 2018, UL 2019) | not checked | marked "current service unconfirmed" by capture; low weight |

## 13. (a) Quick review: `pick3/plan_pick3.md` v0.95 (24791ad4), supersedes §10
PL-3 to PL-7 from §10 are applied (fit outputs not used, curves used; 158 txt + 1 xls; date gap; IR currents; proxy purity and provisional kill). New items:

| # | Item | Verdict | Note and source |
|---|---|---|---|
| PL-9 | §3.1 T15 on the curves: P = EL-derived cell voltage at the highest current (~3.393 A); d = module median P − P; valid 0.3 < P < 0.8 V; no-spread kill robust SD(d) < 0.1 V_t and < 1% of cells with d ≥ 1 V_t; D90 / DVt | OK | Frozen in physical units before reading; "d ≥ 1 V_t ≈ 2.7× dimmer EL" follows from EL ∝ exp(V / V_t) (S, standard). V_t is 25.7 mV at 25 °C; at a module temperature of ~40 °C it is ~27 mV (S), immaterial at these thresholds. The 3-value disclosure is recorded. Trivial: "~159 modules" in the sample note should read 158 files |
| PL-10 | §2 self-test criteria: "recover corners within 1 px and residual < 1% of cell side" | FIX (consistency) | The logged self-test (log 12:50, cellreg.py dded0f03) gives IR inner residual ~1.1% of a cell side and extrapolated IR corners off 6.6 to 9.0% of a cell (~2 IR px); EL corners 1.5 to 2.6%. By the plan's own stated criteria the IR part does **not** pass (1.1% > 1%; ~2 px > 1 px), yet the log says PASS. Before freeze, either record "IR self-test: fail on the stated criteria" or amend the criteria with a dated note and a reason (e.g. inner-80% crops leave ~10% margin per side). Also state that T37's QA residual measures fit consistency, not true error: the self-test shows true IR edge error (6.6 to 9.0%) above the 5% T37 bar while inner residuals pass, so the outer ring (22 of 36 cells on a 4 × 9 grid) is the risk |
| PL-11 | §3.5 T02 headroom | Note (optional pre-statement) | The T15 label is the EL-derived cell voltage at 3.393 A, very likely computed from the same 2022 NEF sweep whose 3.393 A frame gives the EL feature (S: the 6 NEF currents match the EL-derived levels). AUROC(a) may then be near 1, leaving no room for Δ ≥ +0.03. ideas already calls T02 "conservative". Optimistic option, no redesign: pre-state that if AUROC(a) ≥ 0.97 a Δ < +0.03 reads as "no headroom", and the IR-only AUROC (c), already reported, is the independent signal |
| PL-12 | §2 / §3.3 NEF preview threshold "< 0.5 × module median" | Note | The preview is gamma-encoded 8-bit, so 0.5 on preview values is about 0.2 of linear intensity (S, sRGB-like curve). Already flagged approximate; say the threshold is on preview values |
| PL-13 | Kill and success rules vs top3 | OK | Unchanged from §10 PL-1 |

## 14. (a) Quick review: `pick1/plan_pick1.md` v0.9 (96da3a82)

| # | Item | Verdict | Note and source |
|---|---|---|---|
| P1-1 | T26 (R2): success top 20% ≥ 60% of EL dark area, kill ≤ 20%; labelled EL-proxy | OK | matches top3 pick 1 / ideas T26 (proxy because E-PF is held) |
| P1-2 | G0 (R3): go AUROC ≥ 0.8 with predicted sign; kill only if \|ρ\| < 0.3 and AUROC < 0.7 in both dark (A1 / A2) and sunlit (A3) conditions; opposite sign reported as signal | OK | matches ideas v1.2 §1.1 and top3 |
| P1-3 | T27 (< 0.7) and T39 (< 5%) held for E-PF; no invented crack proxy | OK | matches ideas |
| P1-4 | R1: frames ≥ 600 W/m²; S_IR = p99 − median; AUROC per class descriptive, no kill; class sizes from the slides; n < 3 descriptive | OK | matches top3 pick 1 step 2 (no kill there either) |
| P1-5 | §4: "A3 module type is unconfirmed. None are half-cut cells" | FIX | Contradicts R1's own half-cut note. Slides (R): mono PERC 305 W, bifacial PERC 295 W and bifacial PERC 540 W half-cut modules; half-cut ones sit in the diode, glass-crack and soiling groups. Correct: "no half-cut module has an induced crack or a scuff, so nothing here speaks to E1's scuff + half-cut gap" |
| P1-6 | §1: layout "expected 60-cell 6 × 10 from the 363 × 605 aspect" | FIX (caution) | All arrays share one aspect because they are resampled, so the aspect cannot reveal the layout; the 540 W half-cut modules (typically 144 half-cells, S) are not 6 × 10. Detect rows × cols per module type at discovery |
| P1-7 | §4: "43 modules over ~6 classes: 5-10 per class" | FIX (minor) | Slide counts: 8, 8, 6, 7, 2, 6, 6 (glass has 2), total 43 incl. 12 soiled |
| P1-8 | R4: E-PF inputs as "EL crop rectified to the canonical cell", 512 × 512 | FIX (format) | BenchmarkEL images are 512 × 512 **module crops: one central cell plus fragments of its neighbours** (E: handbook/02 §4). Match that geometry for E-PF inputs, not a tight single-cell crop |
| P1-9 | §1 A2: IR at 5.289 A, one module at 5.089 A | OK | listing: 30 files at 5.289 A, 2 at 5.089 A (408181737, whose EL is also at 5.089 A) |
| P1-10 | Freeze discipline and disclosure | OK | v0.9 before values; the 3-value dark I-V disclosure and the known published A3 results are recorded as expectations |

## 15. Re-checks: capture v1.3 / replan v1.2, synth final
- **capture** `capture_plan.md` v1.3 (66d2270b): R-1 and S-24 applied. `replan_pick2.md` v1.2 (9d6a4885): RP-2 (A3 Mavic 3T, half-cut groups, 8 crack modules) and RP-6 (Robocraze not re-verified) applied; §8 short lists consistent with §2 to §4. New minor prices (ZWO 850 nm filter £25 / US$37.90; ASI585MM ₹82,760 with its colour / mono conflict noted) not checked, low weight. **Closed.**
- **synth** files as read (ranked d36d70f7, top3 6ded6462, SUMMARY 6549ff4d): all S-1 to S-33 applied; every size in SUMMARY §3 and top3 "Data" now matches the listings (1.19 GB; A2 0.25; A1 0.29; dark I-V 3.8 MB; 0.26 / 0.48 / 2.5 / 4.5 GB; B1 0.11; C1 1.13 / 1.38 GB). Remaining:

| # | File | Claim | Verdict | Fix |
|---|---|---|---|---|
| F-1 | SUMMARY l.3 | "This was a desk study: no downloads, no GPU" | FIX | Outdated since Om's OK: the approved public downloads for picks 1 + 3 (~1.2 GB, CPU only) started 4 Nov 12:43 (log) |
| F-2 | SUMMARY l.14 | "11 thermal-only sets" | FIX | 12: datascout added D12 (Zenodo 20860870) |
| F-3 | SUMMARY l.10 | A2: IR and EL "at 5.289 A" | FIX (minor) | one module (408181737) at 5.089 A for both |
| F-4 | SUMMARY U2 | ask DTU for "cell count and technology" | FIX (minor) | Technology is answered by the slides (mono PERC 305 W; bifacial PERC 295 W and 540 W half-cut; EL at 100% and 10% Isc; Mavic 3T). Keep: EL camera and resolution, cell layout per type, per-cell crack locations, any lab IR |
| F-5 | top3 pick 2 "Why" | "X1 and X2 fell to P 0.10" | FIX | ranked v1.4: X1 P 0.15, X2 P 0.20 |
| F-6 | top3 pick 2 "Why" | "W03 rank 3" | FIX (minor) | rank 4 (T15 is rank 3; both score 1.41) |
| F-7 | top3 pick 2 "Honest limit" | "W01's prospective test will most likely be read after [the thesis]" | FIX (consistency) | The same pick's timeline reads W01 in W4-5 via X6. Say "after the thesis unless X6 passes its bench test" |
| F-8 | top3 pick 3 l.145, l.150, l.169; SUMMARY §2 row 3 | T15 uses "dark I-V fits"; kill "fits on < 50% of cells" | FIX (match the frozen plan) | pick 3 uses the 158 EL-derived voltage curves (P = cell voltage at ~3.393 A, d = module median − P); the fit outputs sit in an .xls the venv cannot read (check PL-3). Kill: valid cells < 50%, or no spread as defined in plan_pick3 §3.1 |
| F-9 | SUMMARY §4 header | "replan_pick2.md v1.1 §4" | FIX (trivial) | v1.2 (§4 unchanged) |

**Pass 2 closes when F-1 to F-9 are in.** No fix changes the top 3.

## 17. Audit for team-lead: `pick3/plan_pick3.md` v1.1 (6e9d9af2) relaxation and timing

**Timeline (E: `log.md` and file mtimes, `ls --time-style=+%H:%M:%S`):**
- 12:50: cellreg self-test logged as "PASS" (IR corners 6.6-9.0% of a cell, IR inner residual ~1.1%).
- 12:53:47: v1 frozen (5c272fe9). Its §3.1 T15 rules (robust SD(d) < 0.1 V_t **and** < 1% of cells with d ≥ 1 V_t; D90; DVt) predate any A1 number except the 3 disclosed values.
- **12:55 (log l.61) and 12:55:01 (`datasets/download_selection_A1.tsv`): datascout puts real A1 numbers on record:** per-module worst-cell deficit s = median − min cell V at the top current, quintile edges 2.6 / 4.9 / 5.8 / 6.9-7.0 / 8.4 / 19.3 mV, max 19.3 mV (< 1 V_t), plus the txt layout (72 columns = V / I × 36 cells, 7 current rows, top 3.392-3.393 A).
- 12:56:06: v1.1 frozen (6e9d9af2; mtime equals the log line). **So v1.1 came about one minute after those numbers were public in `log.md`.** §6 says "No data value has been read (only the 3 values quoted in datascout's plan)". Whether ideas read the 12:55 line is not recorded.

**What v1.1 changed (diff v1 → v1.1):** only a new §6 was appended; §0 to §5, including every T15 / T02 / T12 / T37 threshold, are byte-identical. §6: A, self-test acceptance criteria for the tool (synthetic); B, a reading rule for T02 when AUROC(a) ≥ 0.97; C, wording (preview values); D, an xls contingency only if the txt format fails; E, a count fix.

| # | Item | Verdict | Note |
|---|---|---|---|
| AU-1 | §6A relaxation: tool acceptance moved from "corners within 1 px, residual < 1%" to "corner error below the feature margin (EL < 5%, IR < 10% of a cell side), inner residual EL < 1%, IR < 2%" | Reasonable for cell-level readouts; **label it post hoc** | Geometry supports it: the IR features use the inner 80% of each cell, a 10% margin per side, so an edge displacement below 10% keeps the window inside the true cell; heat blur is larger anyway (S). It changes a **synthetic tool-acceptance** test, not any real-data kill: the T37 kill (> 5% residual per module, > 30% modules excluded) is unchanged. But the new IR bar (10%) was set after seeing the result (max 9.03%), and matches the "looser thresholds coded in the script after the first run". §6A discloses the failure and the late script thresholds, but does not use the words "post hoc". Ask for one line: "these criteria were set after the synthetic self-test results were known (post hoc); IR passes with 1% headroom". The added inner-14-cell readout and the "registration-sensitive" label are good mitigation |
| AU-2 | Timing: v1.1 frozen after the 12:55 numbers | **Disclosure needed** | §6's "no data value has been read" needs a line: "datascout's 12:55 log line (deficit quintiles 2.6-19.3 mV, max < 1 V_t; txt layout) was on record before this freeze; [read / not read by me]" |
| AU-3 | Threshold-adjacent changes in v1.1 | **None found** | No T15 rule changed. §6B (T02 headroom) and §6C do not depend on the deficit values. §6D was written when the txt layout was already known to parse (12:55 line), so it is moot, not a lever |
| AU-4 | What the 12:55 numbers mean for the frozen T15 kill | Note for the readout | Max per-module deficit 19.3 mV < 1 V_t (25.7 mV), so **no cell has d ≥ 1 V_t**: the second clause of the no-spread kill ("< 1% of cells with d ≥ 1 V_t") is already met, and **T15's kill now rests on robust SD(d) < 2.6 mV alone**. With worst-cell deficits of 2.6-19.3 mV per module, the pooled robust SD may sit near that line (S), so it is threshold-adjacent and must not move. DVt will be empty by construction; report it as 0, as frozen |
| AU-5 | `pick1/plan_pick1.md` v1 (28b58cc9) | OK | md5 matches the log (12:56); P1-5 to P1-8 and the edge caveat applied. Its re-freeze at 12:56 also follows the 12:55 numbers, but pick 1 uses no dark I-V value and the change was G0 verdict wording. Trivial: its header says "~13:00 IST", ahead of the clock (written by 12:56) |

## 18. Closures (4 Nov)
- **synth pass 2 closed:** `ranked_ideas.md` d36d70f7, `top3.md` fa6da29f, `SUMMARY.md` 00f17af7. F-1 to F-9 verified in the text (header now says downloads started 12:43; 12 thermal-only sets; A2's 5.089 A module; U2 trimmed; X1 / X2 P 0.15 / 0.20 and W03 rank 4; W01 read after the thesis "unless X6 passes its bench test"; pick 3's T15 and kill wording match plan_pick3 §3.1; replan v1.2 cited).
- **pick 3 audit closed:** `pick3/plan_pick3_notes.md` (668db9c1) adds N1 (12:55 numbers on record before the 12:56 freeze; not read by ideas before it, learned from check's 12:58 message), N2 (§6A criteria labelled post hoc; T37 real-data kill unchanged) and N3 (T15 kill rests on robust SD < 2.6 mV; DVt 0 by construction). Plan v1.1 6e9d9af2 untouched.
- **pick 3 v1.2** (2893a817, frozen 12:59:20): diff vs v1.1 = an appended §7 disclosure only (post hoc IR bar, synthetic only; v1.1 timing; T15 kill on SD alone, DVt 0). §1 to §6 and all thresholds unchanged. OK.
- **ideas** `ideas_long.md` ba9c0038 and `drone_only.md` 50a13aeb: R-5, R-6, RN-1, DO-1, DO-2, DO-9 verified in the text. Closed.
- **capture**: closed (§15). **datascout** table: closed (§8).

## 20. Independent recompute of pick 3's T15 (team-lead request)
- **Inputs:** the 158 `*_EL-derived_cell-dark-I-V.txt` files in `~/mtp/datasets/thermal_public/A1_osf_csr6t/darkIV/` (layout: 36 voltage / current column pairs, 7 rows: 6 currents + a zero row). ideas' outputs were not read. Script: scratchpad `t15chk/t15_check.py` (md5 972c7210), system `python3 -I`, pure Python, read-only.
- **Definitions (plan v1.2 2893a817, §3.1, unchanged since v1):** P = cell voltage at the row with the highest current (3.392-3.393 A); valid 0.3 < P < 0.8 V; d = module median P − P; robust SD = 1.4826 × MAD of d pooled over valid cells; kill = coverage < 50% or (robust SD < 0.1 V_t **and** < 1% of cells with d ≥ 1 V_t), V_t = 25.7 mV; D90 = d ≥ 90th percentile (linear interpolation).
- **My result:** 158 files, 5,688 / 5,688 cells valid (coverage 100%); P 0.643 to 0.791 V; median d 0, MAD 2.198 mV, **robust SD 3.258 mV** vs the 2.57 mV line; 0 cells with d ≥ 1 V_t (max d 19.3 mV, as datascout logged); **90th percentile 4.234 mV, D90 = 569 cells**; T15 kill **not** triggered → **PASS, narrow** (robust SD is 1.27× the line).
- **ideas' reported values** (via team-lead: coverage 5,688 / 5,688, robust SD 3.26 mV, D90 = 569 at d ≥ 4.23 mV): **match** on every figure.
- **Order:** plan v1.2 frozen 12:59:20 (file mtime; log l.70); `t15_discover.json` 12:59:28, `t15_cells.tsv` (c365ce09) and `t15_summary.json` (320ad9e9) 12:59:49. The kill rule itself was frozen in v1 at 12:53:47. Plan before readout: confirmed.
- **Side note (S):** one cell has d ≤ −1 V_t (module 6320427387, cell 2, −27 mV: brighter than its module median); no rule uses negative d.

## 21. Review: `pick1/plan_pick1.md` Amendments 1-3 (8983bc9d), before G0
- **Order (E: log l.75, l.78, l.80, l.84; mtimes):** Amendment 1 13:00 (A2 discovery), Amendment 2 13:02, Amendment 3 13:05, clarified 13:07 (8983bc9d). cellreg runs: A2 13:02-13:04, A1 13:08. **The run logs hold registration QA only** (orientation, residual % of cell, line-fallback flags, grid consistency); no ΔT, ρ or AUROC field (checked by field names with digits masked, values not read). Per-cell tables are not opened (datascout). So the A2 primary switch (identity → rot180, 13:05) came before any outcome.

| # | Item | Verdict | Note |
|---|---|---|---|
| AM-1 | A1 primary = raw IR `--orient rot180` = authors' `_cropped.txt` with identity | OK | Non-outcome evidence: the authors' own crop is the raw window rotated 180° (max abs difference 0.000 in 10/10, E). Same orientation as pick 3 (crop, identity; notes N5) |
| AM-2 | A2 primary = rot180 by inference (same lab and IR rig) | OK (S) | Reasonable and non-outcome, but an inference; report A2's G0 with "orientation inferred (S)" beside the four-orientation table |
| AM-3 | "Orientation unresolved" if another orientation beats the primary by > 0.15 AUROC with best-of-4 within-module permutation p < 0.01 (1,000, seed 20261104) | OK | Outcome used only as a flag, never to choose; frozen before G0 |
| AM-4 | Inner-cell readout on the real grids | Note | Pick 1 defines it as "edge cells (the outer ring) reported separately". On A1 3 × 12 that leaves **10 inner cells per module (26 of 36 on the ring)**; on A2 6 × 12, **40 inner (32 on the ring)**. State these counts before computing; A1's inner verdict rests on ~100 cells |
| AM-5 | Format facts | OK + FIX elsewhere | A1 Shell M55 is 3 × 12 (E, discovery), so datascout's table A1 row "36-cell (4 x 9) [R: Li 2024]" over-tags: Li 2024 says only "36-cell"; the 3 × 12 layout is E. A2 SolarWorld is 72-cell 6 × 12 (E), which answers "SW-175 cell count unconfirmed" in the table. IR 240 × 320 in °C fits the 537,840 B txt size |

**Pick 3 notes N4 to N6 (a6039800), read for consistency:**
- N4 / N5 OK: identity on the cropped txt = rot180 on raw = pick 1's primary; inner set on 3 × 12 = 10 cells; IR ≈ 11 px per cell.
- **N6 (cell numbering → grid, chosen by max pooled Spearman ρ between dark I-V P and EL cell median over 16 orderings): note before any A1 image value is read.** A pooled ρ includes between-module offsets in P and in EL brightness, which are the same for all 16 orderings. That can lift every candidate's ρ, so "best ρ < 0.5 → unresolved" and "best − second < 0.05 → ambiguous" lose meaning. Suggest the criterion on **module-centred** values (d vs module-centred EL median, or the mean of within-module ρ). Same intent, no threshold change. Choosing by EL, not IR, is correctly disclosed as conservative for T02's Δ.

## 22. Review: pick 1 G0 dark-IR readout (`pick1/out/G0.md` 73ede14a, `G0_results.json` 1da5ae53)
**Recompute (E):** from datascout's per-cell tables (`G0_A{1,2}/<orient>/*_cells.tsv`, QA-excluded modules removed as listed in the JSON), with my own pure-Python Spearman / AUROC (scratchpad `t15chk/g0_rowcheck.py`, md5 d1b9a83e): A2 rot180 ρ −0.550, AUROC(cooler) 0.736; flipv −0.564 / 0.762; id +0.080 / 0.446; A1 rot180 −0.285 / 0.689; flipv −0.326 / 0.710; id −0.307 / 0.619. **Match** with G0.md on every value checked. (Registration and features were not recomputed from images.)

| # | Item | Verdict | Note |
|---|---|---|---|
| G0-1 | A2 "between" (AUROC 0.736 < 0.8, \|ρ\| 0.55 ≥ 0.3); A1 "null" (\|ρ\| 0.285 < 0.3, AUROC 0.689 < 0.7); all and inner agree in both | OK | Matches R3's frozen numbers. "Between" is not an R3 label; the JSON's "between (no go, no null)" is the clearer wording |
| G0-2 | "Not a go, not a kill. The G0 kill needs the sunlit A3 arm as well" | FIX (wording) | R3 kills only if the null holds in both conditions. The dark condition is **not null** (A2 and pooled, \|ρ\| 0.55 / 0.45), so G0 **cannot be killed** whatever A3 shows; only A1 alone is null. Say so, and keep A3 as the sunlit readout |
| G0-3 | Orientation reading: "the vertically flipped maps carry the signal; the horizontal axis is not resolved" | Fair, but add the reason | Descriptive diagnostic (E, same tables): after subtracting each row's median within each module, A2 gives ρ −0.42 / −0.44 / −0.46 under rot180 / flipv / id (AUROC 0.59 / 0.62 / 0.60). So **all orientation dependence comes from row-level (top-bottom) structure.** After subtracting row and column medians, the signal is gone in every orientation (A2 ρ −0.07 to 0.00, AUROC 0.49 to 0.52; A1 ρ −0.17 to +0.05, AUROC 0.52 to 0.57). Reading (S): G0's dark-IR signal is carried by additive row (top-bottom) and column (left-right symmetric) patterns, not by single cells departing from their row and column. That fits real string or edge-row degradation, and equally fits shared artefacts: a vertical convection gradient on a hanging module plus an EL top-bottom gradient, and frame heat-sinking plus lens vignetting at the edges. These data cannot tell them apart. Suggest one descriptive line in G0.md; no verdict change |
| G0-4 | QA exclusions: A2 6 / 15 (40%), A1 3 / 10 | OK + note | Disclosed, including that the failures hit degraded modules (S). For context: 40% exceeds pick 3's pick-level T37 line (> 30%), which pick 1 did not adopt; state it, so the reader knows A2 rests on 9 modules |
| G0-5 | Script fixes after a first run (g0_stats.py e3f818bb → 27f7bff1, 13:09:51; results 13:09:57) | OK + disclosure | NaN parsing and NaN cells in the permutation null. The second fix touches only the permutation null and p-values, not the AUROC / ρ point estimates; my recompute without any permutation gives the same point estimates, so the verdicts do not depend on the fixes. Wording: "before any verdict was used" should add "after a first run whose output (a null of −1) was seen" |
| G0-6 | Orientation unresolved rule | OK | best-of-4 flipv beats the primary by 0.026 (A2) and 0.021 (A1), < 0.15 → not unresolved, as written |

## 23. (b) Download verification, A1 and A2 (`datasets/download_verified.md` e2a0e7f6)
- **Independent check (E):** my own script (scratchpad `t15chk/verify_dl.py`, md5 3ee17487, `python3 -I`) fetched OSF's published `extra.hashes` per folder via the API and hashed every local file. **A1 209 / 209 and A2 47 / 47 match on size, md5 and sha256**, 0 mismatches, 0 files not in the OSF folder; bytes 286,886,436 and 237,009,189, as datascout reports. Each set dir also holds `MANIFEST.md5` and the verify TSV (2 non-data files).
- **Approved set only:** A1 = `darkIV` (all 159 items incl. the xls) + 5 files × 10 modules; every A1 image file belongs to one of the 10 serials in `download_selection_A1.tsv` (da419f33). No A1 extension. A2 = all 32 `indoor_IR` files + 15 EL NEF (one per IR module). Consistent with Om's approval and `download_plan.md`.
- The selection's max-severity module (6320427439, s 19.32 mV) equals my T15 max d (19.3 mV, §20).
- **A3:** pending (archive partly down, 315.7 of 642.6 MB at 13:12). To verify: figshare md5 of the 7z and README; extraction only after the md5 matches.

## 24. Independent G0 v1 recompute from raw files, QA gate, timing (team-lead request)
- **Method (E):** scratchpad `t15chk/g0_recompute.py` (md5 706862a5), venv `python -I` (numpy / scipy / skimage / PIL; system python has no numpy). Own NEF-preview extractor (largest decodable embedded JPEG, luminance), own IR txt reader, own 4-corner projective warp from the **frozen v0.2 grid corners** in each module's `reg.json` (the registration geometry is the one thing taken from cellreg; it is the instrument under review in item (a)), own EL / IR features per plan R3 + pick3 §3.2-3.3, own QA gate (EL or IR RMS residual > 5% of a cell side, from `reg.json`), own orientation maps, Spearman / AUROC, and a best-of-4 within-module permutation null (1,000, seed 20261104).
- **Result: MATCH.** A2: 9 / 15 kept, 648 cells, 230 positives, ρ −0.550, AUROC(cooler) 0.736, inner 360 / 96 / −0.554 / 0.757. A1: 7 / 10, 252 / 50, −0.285 / 0.689, inner 70 / 13 / +0.042 / 0.528. Pooled 900 / 280, −0.451 / 0.708 (inner 0.718). Orientations: A2 flipv 0.762, fliph 0.433, id 0.446; A1 flipv 0.710, fliph 0.595, id 0.619. Best of 4 vs null: A2 0.762, p 0.001 (q95 0.555); A1 0.710, p 0.001 (q95 0.607 vs datascout's 0.612, a permutation-stream difference).
- **QA gate applied as frozen: yes.** Excluded = exactly the modules with EL or IR RMS > 5%: A2 408330775 (5.74 / 9.93), 409008047 (5.81 / 4.09), 409049465 (8.32 / 5.32), 409049991 (8.47 / 9.96), 409050368 (10.61 / 9.89), 409050506 (6.33 / 7.86); A1 6330431480 (1.33 / 10.98), 6320427398 (1.24 / 7.29), **6320427439 (7.59 / 7.30), the most severe module (s 19.32 mV): dropped by the gate.** Near the line and kept: A2 408332844 IR 4.90, 409001724 EL 4.44; A1 6330431031 IR 4.84, 6320427227 EL 4.49 (the module ideas found visually misregistered).
- **Timing:** all `log.md` stamps are monotonic (no line earlier than its predecessor). datascout's "~40% at 13:20" was in a message, not a log stamp; datascout logged a correction at 13:11 (l.88). The current plan's bytes before "## Amendment 4" hash to **8983bc9d**, so Amendments 1-3 are unchanged; their final mtime (13:07:57) precedes the v1 outputs (`G0_results.json` 13:09:57, `G0.md` 13:10:56). The v0.2 registration runs (A2 13:02-13:04, A1 13:08) only wrote QA plus per-orientation cell tables, as checked in §21.
- **Issues:** (1) `G0_results.json` was **rewritten at 13:16:54** (now 2b25cfc5) by `g0_stats.py` 5870e041 with post hoc row / column-centred fields added; the v1 primary values are unchanged (equal to my recompute), but the frozen v1 bytes (1da5ae53) were not kept. Keep an immutable v1 copy and name post hoc outputs separately. (2) Amendment 4 (13:14, visual QA, v0.4) and an interim visual-QA G0 (13:17) came after the v1 readout and before check's co-sign; datascout logged the slip (l.98) and labels the section "INTERIM, QA NOT CO-SIGNED".

- **Resolved 13:20:** datascout rebuilt the frozen stats script (`scripts/frozen/g0_stats_27f7bff1.py`, md5 27f7bff1, read-only) and regenerated `pick1/out/G0_v1_frozen.json` from the unchanged v0.2 cell tables: **md5 1da5ae53, byte-identical to the original v1 output** (checked). The integrity issue is closed.

## 25. (a) Review of `scripts/cellreg.py` v0.4 (04fac77a) and (b) ideas' T37 v2 rule (notes N7, e8cb8027)
**(a) v0.4 code and self-test.**
- **Self-test reproduced (E):** I ran `cellreg.py --selftest` myself (venv `python -I`, output in scratchpad `selftest_v04/`): **PASS**, same numbers as ideas'. 4 × 9 trials: EL corner 1.47-2.62% of a cell, IR 6.62-9.03%; inner residual EL 0.06-0.10%, IR 1.05-1.12%; orientation test (only fliph recovers the mirrored cell); crop test 3 × 12 (IR residual 0.34%; planted cell found in EL and IR); band test 3 × 12 at 50% / 70% depth: corner error 2.06% / 1.52%, grid_vs_quad 8.53% / 8.52%. In-code bars: EL corner < 3%, IR < 10%, residual EL < 1%, IR < 2%, band < 5%.
- **Code (registration core):** iteration 0 searches pitch in 0.98-1.02 of the quad-implied cell and offset ±6%; iterations 1-2 fix the pitch at the current homography's scale, with ±3% offset and ±10% local line refinement; outline step closes gaps and bands (radius 3% of the short side); new `grid_vs_quad_max_pct_cell`. Notes:
  - V-1: **"pitch anchored to the module quad (no drift)" is stronger than the code.** After iteration 0 the reference is the previous fit, not the quad, and local refinement plus the homography refit can still move the scale a little each iteration. The real guard is the new grid-vs-quad check plus visual QA; say so in the version string or the notes.
  - V-2: the band test plants the band at 0.42-0.58 of each cell, half a pitch from the gaps and outside the ±10% refinement window, so it is easier than an off-centre band. ideas' N7 already says the drift cause is "suspected, not shown" (v0.3 did not drift on the 50% band and failed at the outline step at 70%). Optional extra test: a band near a cell edge (e.g. 0.10-0.25 of the cell). The real acceptance is that v0.4 fixes the visibly misregistered 6320427227 on real data.
- Verdict: **OK to use**, with V-1 wording and visual QA as the actual guard.

**(b) N7 rule (written 13:16, before v0.4 ran on real data; no T02 / T12 value computed).** Rules: frozen 5% residual; EL grid_vs_quad > 20% of a cell; visual QA fail with a one-line reason per module in `pick3/out/t37_v2_visual.tsv` before any T02 / T12 value; pick kill > 30% as frozen; v2 labelled post hoc beside v1.
- OK on structure, labelling and timing.
- B-1: the 20% grid-vs-quad bar is lenient next to the synthetic 8.5% (the Otsu quad itself sits ~8.5% off); fine as a coarse drift catch, but the visual QA carries the weight.
- B-2: apply grid_vs_quad to IR too, or say why not (with `--quad-ir full` the crop boundary is the quad, so it is a natural check of the IR grid).
- B-3: visual QA is a judgement by someone who has seen T15 and the v1 T37 numbers (not T02 / T12). Write the fail criteria before looking (e.g. any grid line off its inter-cell gap by more than ~10% of a cell; grid past the module edge; a cell window crossing a gap), then check co-signs the calls blind to outcomes, as team-lead asked for pick 1.

## 26. (c) Co-sign: datascout's v0.2 visual QA calls (`pick1/out/qa/visual_qa.tsv` 80a44fb2), blind to per-module G0
- **Frozen v1 values (team-lead's match request):** `G0_v1_frozen.json` A2 0.735927 / −0.550442, A1 0.689010 / −0.285264, pooled 0.707546 / −0.450916; my raw-file recompute gives 0.735927 / −0.550442, 0.689010 / −0.285264, 0.707546 / −0.450918. **Match** (the pooled ρ differs at 2e-6).
- **Method:** I viewed the 10 montages (A1 EL / IR, A2 EL / IR parts 1-4) and one native-size overlay, made my calls under datascout's stated rule (grid line inside a cell, or grid overrunning the module edge by more than ~1/4 cell), and only then compared. As objective support I computed, per module, the offset of each grid edge from the module's own outline (`quad` vs `grid_corners` in reg.json, % of a cell), and for A1 IR the offset from the authors' crop window located in the raw IR. The crop is a **fixed window (rows 137-172, cols 90-224) for 9 of 10 modules**, so it is a ruler only where the module sits in that position; 6330431038 has its own window and its grid fits it to ±5% of a cell.

| Module | datascout | check | Basis |
|---|---|---|---|
| A1 6320427227 EL | fail (pitch drift) | **agree** | vertical lines run through cell centres; grid overruns the right edge by ~1/2 cell |
| A1 6320427802 IR | fail (one row high) | **agree** | top grid row over background; top edge 1.0 cell above the outline |
| A1 6330431031 IR | fail (squashed) | **agree** | grid covers only the upper module; bottom edge 0.9 cell short |
| A2 409001724 EL | fail (~1/2 row low) | **agree** | bottom grid row over background; edges +0.6 / +0.8 cell vs the set's typical |
| A1 6320427793 IR | keep | **fail under your rule** | bright strip of the top cell row above the grid in the montage and at native size; top edge +60% of a cell vs the set's typical −4% (outline) and +64% vs the authors' crop. The top grid line sits ~0.6 cell inside the top row |
| A1 6330431484 IR | keep | **borderline** | grid shifted down ~0.3-0.4 cell by both rulers (outline +33 / +60 vs typical −4 / +32; crop +33 / +43); over the ~1/4-cell bar |
| A2 408330104 EL, 408332881 EL | keep | **borderline** | grid shifted / stretched down ~0.25 cell (edges +20 / +40 and +18 / +42 vs the set's typical −5 / +15), at the bar |
| all other kept modules (A1 6330431038, 6330431479; A2 408181737, 408322647, 408332844, 408380306, 409049092, 409052375) | keep | **agree** | lines on gaps in EL and IR; edge offsets at the set's typical values (A1 6330431479's −38% vs the fixed crop is a placement offset; its outline offsets are typical) |
| residual-gate exclusions | exclude | agree | as §24 |

- **Verdict:** rule application is **sound but lenient on A1 IR**: 6320427793 fails your own rule; 6330431484 and A2 408330104 / 408332881 sit at the bar. The montage scale with thick red lines on ~12 px IR cells hides offsets of 0.3-0.6 cell.
- **For the v0.4 QA (before any G0 v2 number):** (1) pre-state a numeric edge check per modality, e.g. "any grid edge offset from the module outline differs from the set's median offset by > 25% of a cell → fail", which is objective and blind; (2) overlays at native resolution with 1 px lines; (3) list borderline modules explicitly and report G0 v2 with and without them (sensitivity, no verdict change).

## 27. datascout's G0 v2 visual QA criteria (`pick1/out/qa_v04/visual_qa_v04_criteria.md` 16e888f0)
- Written 13:23:09 (log l.102), before any v0.4 run for pick 1 (no `G0_*v04*` output existed at review). Fail if: inner line > ~10% of a cell off its gap; grid overruns or stops short of the module edge by > ~10%; a cell window crosses a gap; wrong count or orientation. Keep only if EL and IR both pass and residual ≤ 5%. Calls recorded before any G0 v2 number; flagged modules excluded unless check and datascout agree on a pass.
- **OK**: tighter than Amendment 4 (10% vs ~1/4 cell), pre-stated, conservative on disagreement.
- Note: on A1 IR, 10% of a cell is ~1.2 IR px, below what the eye can judge on blurred thermal images. When co-signing I will add my numeric edge offsets (grid_corners vs module outline, against the set's median) as support, and say where a call rests on them.

- **Addendum (criteria md5 fae36d53, 13:26:55, log l.104; no v0.4 output for pick 1 existed):** (5) numeric edge check per side, grid edge minus Otsu outline in cells, fail if > 0.25 cell from the set median for that side and modality (`scripts/edge_check.py` ab09f284, reads reg.json only); (6) 1 px full-grid overlays, IR ×8 nearest (`scripts/qa_overlay.py` 7059794b); (7) borderline list named before G0 v2, plus a sensitivity readout without them. **OK.**
- **Calibration check (E):** I computed the same rule on the v0.2 reg.json files with my own code. The flagged module × modality set is the same as datascout's `edgecheck_A*_v02.tsv` (4b935137, 7e035886): A1 227 EL + IR, 398 IR, 439 EL, 793 IR, 802 IR, 031 IR, 480 IR, 484 IR; A2 408330104 EL, 408330775 EL + IR, 408332844 EL, 409001724 EL, 409049465 IR, 409049991 EL + IR, 409050368 IR, 409050506 EL + IR. One at-the-bar difference: I also flag A2 409050368 EL (bottom, 0.25), already excluded by the residual gate. Per-side values differ in sign convention, not in the calls. (Retracted 4 Nov: my note that A1 6320427227 "appears twice" was wrong; the file has one EL and one IR row per module by design, and my own command printed both files.)

## 28. cellreg change 04fac77a → 95e0ca3e (team-lead flag) and pre-outcome QA of pick 3's v0.4 run
**The change (code read; ideas' log l.105; literal diff not yet received):** `find_quad` now computes the module outline on a block-mean copy downsampled to ≤ 1000 px and scales the corners back (`(q + 0.5) k − 0.5`, correct for block means). Corners are quantised to k px (k = 5 on 4928 × 3264 EL previews, ≈ 2.6% of an A1 EL cell); the refined grid then refits lines. The self-test's built-in EL corner bar moved from 3% to 5% after the new build reached 3.57% (disclosed; aligns with plan §6A, which is itself post hoc).
- **Self-test re-run by me on 95e0ca3e (E, scratchpad `selftest_v04b/`):** PASS; EL corner 2.19-3.57%, IR 6.62-9.03%, residual EL 0.11-0.14%, IR 1.05-1.12%; band test 2.18% / 2.50%, grid_vs_quad 9.4% / 9.9%. Matches ideas' log.
- **CR-1 traceability:** both builds write `version: "cellreg 0.4"`, so a reg.json cannot tell 04fac77a from 95e0ca3e. Bump the string (e.g. 0.4.1) and write the script md5 into each reg.json / summary.
- **CR-2 order:** pick 3's real-data v0.4 registration (`pick3/out/reg_v04_id/`, all files 13:27:10-13:27:20) ran on 95e0ca3e (changed 13:27:02) before this review. Registration only; no T02 / T12 value computed.

**Pre-outcome QA facts, pick 3 v0.4 (E, `reg_v04_id/*_reg.json`, `summary.json`; compared with `t37_v03_summary.json`):**
- **CR-3: the frozen 5% rule now excludes 4 / 10 = 40%, over the 30% pick-level line.** EL improves where v0.3 drifted (6320427227 4.49 → 1.32%; 6320427439 7.59 → 1.89%), but IR residual rises: 6320427227 2.99 → 6.66, 6320427802 3.25 → 7.57, 6330431038 1.99 → 3.81, 6330431479 1.57 → 2.99. Excluded under v0.4: 227, 398, 439, 802 (v0.3: 398, 439, 480).
- **CR-4: N7 rule 2 (EL grid_vs_quad > 20%) is miscalibrated for real data.** All 10 modules show 24-35% (synthetic ~9.5%); on v0.2 the EL grids I passed visually also had 22-31%. The Otsu outline sits systematically off the cell-grid corners on real modules, so an absolute 20% bar would exclude every module. A relative rule (as datascout's: deviation from the set median > 0.25 cell) measures what is meant; changing it is a post hoc amendment and must be logged before any T02 / T12 value.
- **CR-5: likely cause of the IR rise, and a false premise in N5.** N5 says the authors' `_cropped.txt` "is the module itself, with no background". It is not. In the raw 240 × 320 IR, the module's warm region (half-maximum) spans **~144-146 × 36-37 px** (e.g. cols 82-227, rows 135-171), while the crop is a **fixed 134 × 35 window (cols 90-223, rows 137-171) for 9 of 10 modules**: it trims ~0.9 cell horizontally (~0.65 cell on the left, ~0.3 on the right). For 6330431480 the module sits at rows 126-162, cols 73-218, so the fixed crop misses ~0.9 row at the top and holds background at the bottom; 6330431479 sits 4 px (~0.33 cell) higher than the crop. With `--quad-ir full` the crop boundary is taken as the module edge, so 12 columns are forced into 134 px (~11.2 px per cell against ~12.1 px true, ~7% pitch error), and v0.4's pitch anchoring locks that in. Suggest, before any T02 / T12 value: register pick 3's IR on the raw frame with the Otsu outline (as pick 1 does), by dated amendment. (This also refines my §26 ruler note: the crop is a good vertical ruler only where the module sits in the fixed window, and it is never a horizontal ruler.)
- **CR-6:** UVF grids come out transposed (12 × 3) on 6 of 10 modules, so `grid_consistent` is false there. UVF is not used for T02 / T12; fix `orient_grid` for UVF or report it.
- Pick 1 is not affected by CR-5: datascout registers raw IR with the Otsu outline, whose width (~145 px) matches the warm region.

## 29. Status after team-lead's pick 3 decision (A)
- **cellreg diff review for datascout's G0 v2:** no copy of 04fac77a survives (no frozen release yet), so a literal diff is not possible. Reviewed instead: the full registration core (§25, at 04fac77a) plus the changed `find_quad` and self-test bars in 95e0ca3e (§28), and a self-test re-run on 95e0ca3e (PASS). **OK for pick 1's G0 v2** (raw-frame IR with the Otsu outline, so CR-5 does not apply), provided the frozen release ideas cuts has md5 95e0ca3e (else I re-review) and each reg.json records the script md5 (CR-1).
- ideas' T37 v2 log line (l.108) says "3 modules > 5%" but lists four (6320427439 at 5.40% is over 5%); 4 / 10 is the count, as CR-3.
- ideas' proposed "v3: IR uniform 12 × 3 grid on the authors' module crop" rests on the crop-is-module premise that CR-5 shows is false; under decision (A) it is not run.
- To check when they land: `PICK3_A1_REPORT.md` (T15 PASS narrow, §20; T37 v1 3 / 10 at the line plus the visual fail on 6320427227 EL; T37 v2 4 / 10 by the 5% rule and 10 / 10 by N7 rule 2; no T02 / T12), and the pick3b A3 plan before its freeze.

## 30. cellreg release check (team-lead: accept only a version-string-only change)
- Reference: `check/cellreg_95e0ca3e.py` (read-only copy, md5 95e0ca3e, saved 13:32 while `scripts/cellreg.py` still had that md5).
- First release offered, `scripts/frozen/cellreg_91c3c81e.py` (v0.5, 13:33): **not version-only.** The diff vs 95e0ca3e adds an opt-in `uniform` IR grid mode, an `el_p99` feature field, rejection of non-EL modalities whose grid is transposed vs EL, off-centre band self-tests and extra summary fields. The default path (Otsu outline + detected grid) was unchanged in that diff. It was withdrawn before I finished: the file is no longer in `scripts/frozen/` (its self-test JSON remains in `pick3/out/`).
- **Release accepted: `scripts/frozen/cellreg_7d9a9fe0.py` (v0.4.1, read-only, 13:34:52; `scripts/cellreg.py` has the same md5).** `diff -u` against the 95e0ca3e copy: **one line, the VERSION string only** ("cellreg 0.4.1 ... = 95e0ca3e + this version string only; pitch searched ±2% in iteration 1 only (limits, not prevents, drift) ..."), which also fixes V-1's wording and CR-1's traceability. **Go md5 for datascout's G0 v2: 7d9a9fe0.**
- Note: ideas' notes N8.3 (v3, option B only) cite `cellreg_91c3c81e`, which no longer exists as a frozen file; moot under team-lead's decision (A).

## 31. Colvin 2023 full text (section numbers corrected 4 Nov: the methods text is §II.A, not §II.B) (doi:10.1109/jphotov.2023.3238278; Research MCP, IEEE): ideas' N8.4 / N8.5 claims and new A1 facts
| # | Claim (where) | Verdict | Source text |
|---|---|---|---|
| CV-1 | each cell's voltage is computed from "a bright pixel from each cell" (N8.4) | OK | §II.A: "This technique uses a bright pixel from each cell to calculate a cell voltage"; one image per bias gives one (I, V) point per cell; biases 0.01, 0.05, 0.1, 0.4, 0.7, 1 × Isc |
| CV-2 | per-cell RS and J01 "mapped onto the modules for visual representation" (Fig. 4d / e), no numbering convention (N8.4) | OK | §III.B: same words; no cell numbering is stated |
| CV-3 | "Cells with bright spots in high injection EL show higher RS values because of high-resistance interconnection issues leading to current crowding" (N8.5) | OK | §III.B, verbatim. Also: "Darker cells in low injection EL show higher J01 values" |
| CV-4 | "Dark regions in EL show bright in PL", so EL darkening is not recombination (N8.5) | OK | §III.B, verbatim (Fig. 6) |
| CV-5 | IR taken after "a bias of ISC was applied for 5 min", while the file names say 180 s (N8.5) | OK | §II.A, verbatim. File names: `_180s_3.39xA` (OSF listing). Discrepancy stands; which is right is unconfirmed |
| CV-6 | N8.5 reading: a high-RS cell may show a higher EL-derived voltage at high injection, so "lower P = worse" may be inverted for A1 | OK as S | follows from CV-1 + CV-3 (bright-pixel voltage of a current-crowded cell is higher); not stated by the authors |
- **New R facts for the A1 row and SUMMARY U1 (§II.A):** IR camera **ICI 8320P** (not Li 2024's Fluke Ti55); EL cameras a **Nikon D5100 with a 950 nm long-pass** (matches the NEF files) and a Sensovation HR-830 cooled CCD with an 850 nm long-pass; PL qualitative with the CCD, 850 nm + InP filters and a low-intensity light; UVF at FSEC with a Sony α7S + UV-pass flash.
- **Optimistic R fact for pick 1 (module level):** Fig. 5, "Standard deviation of module temperature from IR thermography images is plotted as a function of module power loss rate", linear fit **R² = 0.429**; and "That these regions appear hotter in IR images also confirms current crowding" with bright EL regions. The authors add: "The IR heterogeneity may be exaggerated in dark injection when compared to outdoor operation under load". So on A1, dark-IR heterogeneity carries a module-level degradation signal (R), consistent with G0's module / row-level structure (S).

## 32. v0.5 (91c3c81e) assessment for pick 1, on team-lead's request, and the single go md5
- **State (E, 13:3x):** `scripts/cellreg.py` = `scripts/frozen/cellreg_7d9a9fe0.py` = 7d9a9fe0 (v0.4.1). v0.5 is archived as `pick3/out/archive/cellreg_v0.5_91c3c81e_UNREVIEWED_not_for_use.py` (md5 91c3c81e), withdrawn by ideas, never run on real data (ideas). ideas' `pick3/out/cellreg_95e0ca3e_reconstructed.py` is byte-identical to my saved `check/cellreg_95e0ca3e.py` (`cmp`).
- **91c3c81e vs 95e0ca3e (my diff, §30):** outside VERSION, (1) `register(..., grid_mode="detect")`: the detect path is unchanged apart from an added `"grid_mode": "detect"` QA field; the uniform branch runs only on request; (2) `el_p99`: an extra EL output field, other EL features unchanged; (3) transposed-modality rejection in `process_module`: this **is** on pick 1's IR path, but it acts only when a modality's grid shape differs from EL's (all pick 1 v0.2 runs had consistent shapes), and then it rejects instead of mis-mapping; (4) self-test only (off-centre band); (5) CLI and summary fields. The downsampled quad was already in 95e0ca3e, not new in v0.5.
- **Verdict:** v0.5 would also be acceptable for pick 1's paths (raw-frame IR detect, EL detect, no UVF), but it is withdrawn and labelled not-for-use, while 7d9a9fe0 is version-only. **The single go md5 for datascout stays 7d9a9fe0**, to avoid two releases in play.
- CR-1: ideas records the md5 in run logs, not in reg.json; fine as long as datascout's G0 v2 manifest records 7d9a9fe0 (asked, §30).

## 33. Review: `pick3/out/PICK3_A1_REPORT.md` (2eb8400b)
- **Numbers OK** against my checks: T15 coverage 5,688 / 5,688, robust SD 3.26 mV, D90 569 cells at d ≥ 4.23 mV, DVt 0 (§20); T37 v1 3 / 10 excluded with the listed residuals; T37 v2 4 / 10 by the 5% rule (227 IR 6.66, 398 IR 7.22, 439 IR 5.40, 802 IR 7.57) and grid-vs-outline EL 23.9-35.4%, IR 44.6-81.7% (§28); G0 row / column-centred AUROC A2 0.49-0.52, A1 0.52-0.57 (§22); crop root cause and fix (§28 CR-5); Colvin quotes and section numbers (§31, §II.A and §III.B are right).
- **Disclosures OK:** freezes, the 12:55 timing, hand-typed times, post hoc self-test criteria and the 3% → 5% bar, the run before review, v0.5 withdrawn, v0.4.1 provenance.
- Minor: (1) "messages of 4 Nov ~13:4x" was typed at 13:36 (file mtime), ahead of the clock; team-lead's decision reached `check` at ~13:3x. (2) T15 margin: the frozen line is 0.1 V_t = 2.57 mV, so the margin is 0.69 mV (the report rounds the line to 2.6 mV, margin 0.66 mV); immaterial.
- Verdict: **OK**, two trivial fixes.

## 34. (c) Co-sign: datascout's G0 v2 QA table (`pick1/out/qa_v04/visual_qa_v04.tsv` 8557c658), before any G0 v2 number
- **Runs:** all 25 reg.json files in `pick1/out/G0v2_A{1,2}/rot180/` carry `cellreg 0.4.1` (E). No G0 v2 value exists; I saw none.
- **Numeric (E, my own code on the v0.4.1 reg.json):** residuals and edge deviations from the set median per side match the table for every module (sign convention aside). All 9 kept modules have EL and IR residual ≤ 5% (max: A2 409001724 EL 4.47%) and edge deviation ≤ 0.18 cell. One at-the-bar difference: A2 409008047 EL is 0.24 cell on my measure vs 0.26 on datascout's; the borderline call stands.
- **Visual (E, 1 px overlays and montages):**
  - A1 IR: agree with all 10 calls. The keeps (227, 802, 038, 484) sit on the module outline. 398 and 480 overrun the top. 793, 031 and 479 stop short at the bottom. 439 fails on residual.
  - A2 IR: agree with all 15. In the 5 kept modules the dark corner dots sit on grid intersections. 408181737 (outline caught the hot cable), 409049991 and 409050368 (lines off the dots) fail.
  - A1 / A2 EL: agree for 408322647, 408380306, 409049092 and 409052375 (lines on the gaps).
- **Flag: A2 409001724 EL.** At native size the top grid line sits ~0.15-0.2 cell inside the top cell row and the bottom ~0.12 cell short; a row-profile measure gives the module's top edge 0.20 cell above the grid top, against 0.00 for the reference modules 408380306 and 409049092. That exceeds criterion 2 (grid stops short of the module edge by > ~10% of a cell). Its residual is 4.47%, the highest among the keeps. **Call: borderline fail**; under the criteria file, a flagged module is excluded unless check and datascout agree on a pass.
- **Co-signed result:** keep **A1 4 / 10** (6320427227, 6320427802, 6330431038, 6330431484) and **A2 4 / 15** (408322647, 408380306, 409049092, 409052375). **Borderline list, 6:** A1 6320427793 IR, A1 6330431479 IR, A2 408332881 EL, A2 409008047 EL, A2 408330104 EL (residual 5.37), A2 409001724 EL (new). Sensitivity B adds back these 6, as pre-stated, with no verdict.

## 35. Quick review: `pick3/plan_pick3b.md` v0.95 (ae1758d8), before freeze; A3 not extracted (only `archive/` exists)
- **OK:** no duplication of pick 1 (reuses its S_IR, EL dark fraction and R3b cells); a physics label independent of EL and IR (STC I-V ΔP); verdict lines pre-stated (R1 label validity 0.5 / 0.3; R2 proxy 0.5 / 0.3 and ΔR² 0.10 / 0.05; R3 interconnect primary, success ≥ 0.8 with row / col-centred ≥ 0.7, kill < 0.7 and centred < 0.6, not computable < 10 cells / < 3 modules; R4 conditional); diode class reported separately; frozen tool 7d9a9fe0; written before any A3 value.
- PB-1 (FIX): §5 cites the QA criteria as `16e888f0` with "overrunning the module edge by more than ~¼ cell". The ¼-cell bar was pick 1's v0.2 Amendment 4; the v2 criteria are 10% bars plus the numeric edge check (set-median deviation > 0.25 cell), file md5 **fae36d53** (§27). Cite that.
- PB-2 (FIX, both plans): pick 3b says the A3 IR quad is the Otsu outline (the A1 lesson), but pick 1's R3b, whose cells pick 3b reuses, registers EL to the 363 × 605 array "by the module-quad homography (IR is already rectified)", and R1 takes "module area = the whole 363 × 605 array, which is module-rectified (R: README)". The README says only that the arrays are "sampled to 363x605 pixels" (R, figshare); that they are exact module crops is S. Align before extraction: Otsu outline on the IR array, detect grid, with a structure-only discovery fact of array border vs outline offset per module; pick 1's R1 3% inset rule can stay for S_IR.
- PB-3 (add disclosure and a reading): the DTU slides also give **per-class power loss** (R): cracks 4-5%, interconnections 3-14%, PID 5%, shorted diodes 33-66%, glass < 1% (soiling 33% / 66%, no EL). These are known before the freeze and should be listed with the ΔTmax values. Without the diode class, ΔP spans ~0-14%, close to nameplate tolerance (S), so a ρ < 0.3 there cannot tell "EL proxy invalid" from "label range too narrow"; pre-state that reading.
- PB-4 (note): the slides say "High res ELs 100% and 10% Isc" (R), while the figshare README describes one EL per module; discovery decides whether 3b-R4 runs.
- PB-5 (note): expected stratum sizes (R, slides): interconnections 8 modules / 98 affected cells; cracks 8 / 69; so the interconnect stratum is likely computable.

- **PICK3_A1_REPORT.md now 55fcf923:** both trivial fixes are in (decision time "~13:3x" with the ahead-of-clock note; T15 line 2.57 mV, margin 0.69 mV). Closed.

## 36. Independent recompute of G0 v2 (post hoc instrument fix; cellreg 0.4.1; co-signed QA)
- **Order (E):** keep lists `qa_v04/keep_v2_primary.tsv` (484fa349) and `keep_v2_sensB.tsv` (db548f73), the co-signed table (a9a3f454) and `scripts/frozen/g0_stats_0190cba5.py` all at 13:42:17, before the outputs `G0v2_primary.json` (f1e904e7, 13:42:30) and `G0v2_sensB.json` (efe6f4ee, 13:42:35), both read-only. The keep lists equal my co-signed sets (§34): primary A1 227 / 802 / 038 / 484 and A2 408322647 / 408380306 / 409049092 / 409052375; sens B adds the 6 borderlines.
- **Method:** my `g0_recompute.py` extended to G0 v2 (scratchpad `t15chk/g0v2_recompute.py`, md5 f5499938): raw EL NEF preview + raw IR txt, warp from the v0.4.1 grid corners, own features, the frozen keep list, own Spearman / AUROC / best-of-4 null, plus the frozen row / column-centred ΔT (Amendment 4: ΔT minus row median, then column median; EL label unchanged).
- **Result: MATCH on every value.**

| Set | Cells / pos | ρ | AUROC(cooler) | inner | row / col-centred | frozen-rule reading |
|---|---|---|---|---|---|---|
| A2 primary (4 modules) | 288 / 75 | −0.515 | 0.732 | 0.739 | 0.525 | between (no go, not null); all and inner agree |
| A1 primary (4) | 144 / 36 | −0.246 | 0.621 | 0.394 | 0.343 | null; inner also null, so not edge-sensitive |
| pooled primary (8) | 432 / 111 | −0.403 | 0.687 | 0.681 | 0.462 | between |
| sens B pooled (14) | 792 / 254 | −0.431 | 0.706 | 0.719 | 0.500 | descriptive |

- Orientation: A2 best flipv 0.760 vs rot180 0.732; A1 best id 0.709 vs rot180 0.621 (gap 0.088 < 0.15), p 0.001 vs the best-of-4 null: not unresolved, as datascout reports. A1's preferred orientation moved (v1 flipv, v2 id) on 4 modules, so A1's orientation is weakly determined (S).
- Reading (S, post hoc): G0 v2 repeats v1, with no cell-level signal once rows and columns are removed (A2 0.525). On A1 the centred AUROC(cooler) 0.343 means EL-dark cells read **warmer** within their row and column, which fits Colvin 2023's resistive current crowding (R) but is weak and not a frozen readout.

- **Closed (13:45):** pick 1 Amendment 5 (`plan_pick1.md` d1e6777b, 13:43:32) tags "module-rectified" S and sets R3b's IR quad to the Otsu outline + detect grid under the v2 QA, with border-vs-outline offsets logged at discovery and R1's switch rule decided from them before any S_IR value. `plan_pick3b.md` v1 frozen **eaec6f26** (13:43:34, read-only copy): PB-1 (fae36d53, ¼-cell marked superseded), PB-2 (same IR rule as pick 1, reuse only if matching), PB-3 (per-class power loss listed as known; non-diode reading rule, disclosed as added after learning the ranges) all applied. A3 was not extracted at either freeze (`A3_dtu/` holds only `archive/`, still being written at 13:45:46).

## 37. Still to come
- A3 verification.
- (b) ideas' per-module `t37_v2_visual.tsv`; (c) datascout's v0.4 per-module visual QA table (co-sign blind); (d) recompute both v2 readouts.
- (b) `datasets/download_verified.md`: A1 dark I-V 159/159 and A2 47/47 reported verified in the log (12:55, 12:59); A1 images and A3 still running.
