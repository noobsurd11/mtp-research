# datascout notes: search log, near misses, open questions

Owner: datascout. Date: 2026-11-04. Companion to `dataset_table.md`. v2: check pass-1 fixes applied.
Tags: E = our files, R = source, S = my reasoning.

## 1. What I was asked
Om's question (1): public datasets with paired or co-registered EL + thermal (IR) of PV modules or cells; also EL + PL, EL + UVF, EL + RGB, thermal-only sets with defect labels, and data inside papers that may be available on request.

## 2. Headline findings
- **No public set has pixel-registered EL + thermal at cell level with crack / inactive masks** (S, after the sweep below). Almukhtar and Kurnaz 2026 say the same for RGB-IR-EL ("In the absence of publicly available datasets that provide physically paired RGB-IR-EL imagery of the same photovoltaic module") [R: doi:10.3389/feart.2025.1702396 §2.1]. They missed the three sets below, so the claim is too strong.
- **Three open, CC BY 4.0 sets have EL and IR of the same physical modules** (module-level pairing, by serial number or folder):
  - A1 OSF `csr6t` (UCF Data-Enabled PV group, 156 Shell M55 modules; EL at 6 currents, IR of 157 modules at 3.39 A (about Isc) 180 s after current on, UVF, I-V, EL-derived per-cell dark I-V; companion paper Colvin et al. IEEE JPV 2023, doi:10.1109/jphotov.2023.3238278) [R; check D-3 to D-6];
  - A2 OSF `ar76v` (42 SolarWorld modules; EL at several biases; forward-bias IR at 5.289 A for 15 modules (16 captures; only some modules were done because the IR camera failed)) [R];
  - A3 DTU Data 10.11583/DTU.29665346 (43 artificially degraded modules: cracks, PID, interconnect disconnection, glass cracks, shorted bypass diode, plus soiling; drone IR at 4 altitudes and several irradiances, EL, STC I-V) [R].
- Cell-level alignment is feasible for all three by a per-module homography from the module outline and cell grid (S). Nothing is registered out of the box.
- Physics caveat from the sources: drone IR barely separates cracked from healthy modules; disconnected interconnects and shorted diodes are visible [R: EPJ PV 2025, doi:10.1051/epjpv/2025020]. Under forward bias, EL-IR similarity is high for solder-bond (Rs) defects (SSIM 0.82) and lower for corrosion (0.61); a whole-cell hotspot with no EL signature was put down to microcracks [R: Li et al. 2024, doi:10.1016/j.solener.2024.112704 §4]. So thermal is more promising for inactive / disconnected / high-Rs areas than for thin cracks (S).

## 3. Search log (all 4 Nov 2026)
Research MCP (OpenAlex, Scopus, ScienceDirect, arXiv answered; Semantic Scholar was rate-limited all session, so search_snippets failed every time; IEEE key inactive):
- search_papers: "electroluminescence infrared thermography photovoltaic module dataset"; "paired electroluminescence and thermal images solar panel deep learning"; "multimodal dataset photovoltaic electroluminescence photoluminescence UV fluorescence images"; "open data sets for assessing PV system reliability"; "electroluminescence infrared thermography same modules comparison field inspection correlation cracks hotspots"; "UV fluorescence electroluminescence cell cracks comparison photovoltaic modules images"; "dataset thermal infrared photovoltaic defects UAV images annotated"; "drone electroluminescence and infrared thermography same PV plant cell-level comparison"; "thermal image to electroluminescence image translation generative photovoltaic"; "photoluminescence electroluminescence silicon solar cell image dataset machine learning crack"; "Luminescence and thermal imaging applied to half-cut-cell ..."; "quality activation maps ... Demant"; "solar cell production line electroluminescence and thermography images ..."; "Influence of irradiance and drone altitude ..."; DTU author query.
- get_paper: Lai 2025 (doi:10.1016/j.enconman.2025.119783), Almukhtar 2026, Chen 2025 review (doi:10.1016/j.apenergy.2025.126132), Pillai 2027 review (doi:10.1016/j.rser.2026.117457), Li 2024, Gallardo-Saavedra 2020, Asadpour 2020, Ferdous 2026, Bommes 2021, Mantel 2019.
- fetch_fulltext (3, all shortlisted, 2 OA + 1 Elsevier): Chen 2025 review (read §5 image inspection and §7.1), Almukhtar 2026 (read §2.1 to §2.2, data statement), Li 2024 (read §2.1, §2.2, §4).
- search_snippets: 4 attempts, all failed (Semantic Scholar rate limit).

Web (WebSearch / WebFetch, pages and metadata only):
- Zenodo: records 15020575 (EL + PL), 19880941 (IBC4EU EL + visual), 18306410 (TECNALIA), 15719875 (UVa DB), 15930823 (PV-LLM tri-modal), 14439369 (SIPV-EL, EL + energy; EL only, not tabled).
- OSF API: nodes muc98 (UCF DPV root, 8 children listed), t8x9k, 7v5zt, csr6t, ar76v; file listings of csr6t IR / EL / close-up EL-PL and ar76v EL / IR folders; licence id 563c1cf88c5e4a3877f9e96a = CC BY 4.0.
- Mendeley Data: pxyzzkbs4b (Polenghi), 82vzccxb6y, 8sxfmrpfpv, 5ssmfpgrpc (last three via search snippets only).
- DTU Data / Figshare API: article 29665346 metadata and file list; README.md (1,161 bytes) read with curl into the scratchpad, `--max-filesize 5000`. This is the dataset card, not data. The 642.6 MB archive was not touched.
- GitHub: RaptorMaps/InfraredSolarModules README; DuraMAT/PV-LLM README; SouthernCompany/OpenUVF returned 404 (search says the org is southern-company-r-d).
- Hugging Face API: "thermal solar" (6 ids, all the same India drone set), "electroluminescence" (none).
- DOE Data Explorer: 10.21948/2462712 (NREL BEST, EL + PL + I-V + EQE).
- DuraMAT Data Hub: every URL now 301-redirects to datahub-duramat.nlr.gov, which returned 404 (dataset pages, CKAN API and search). Facts for OpenUVF, PLatypus PL, NREL half-cut PL and PREDICTS2 come from search snippets and the Chen 2025 review only. F04 census already noted the hub move (E: literature/notes/F04_el_datasets_census.md, MultiSolSegment row).
- Blocked or unreachable: epj-pv.org (403), service.tib.eu (bot wall), vrai.dii.univpm.it (connection refused), research-hub.nrel.gov (DNS), OSTI JSON API (empty results).
- Tool side effect: WebFetch of an AAU repository PDF link (vbn.aau.dk, Mantel et al. SPIE 2019 paper) auto-saved the paper PDF under the session tool-results folder. It is a paper, not a dataset; I did not read or move it.

## 4. Near misses (looked like a fit, are not)
- Almukhtar and Kurnaz 2026 (Frontiers): RGB-EL-IR "fusion" uses synthetic triplets (ELPV + a Kaggle RGB set + their own 480 lab IR images), matched by defect type, not the same modules [R §2.1, §2.1.1]. Also misdescribes ELPV as having pixel masks (ELPV is image-level, E: F04 census). Not usable as paired data.
- PV image database for LLM evaluation (Zenodo 15930823): three modalities, but separate pools, 50 labelled images per category [R].
- SolarFCD (arXiv 2604.23662): RGB + thermal, image-level, no EL [R].
- TECNALIA benchmark (Zenodo 18306410): EL and visual were used to characterise modules, but the release is 5.9 MB of time series [R].
- UVa "Dataset for the electrical and imaging-based characterisation" (Zenodo 15719875): a MySQL DB design with a 10.1 MB sample, not an image set [R].
- Lai et al. 2025 (ECM): EL + IR + RGB, 21 defect types, but IR is drone and EL is darkroom; same-module pairing and data access unconfirmed (paywalled) [R abstract].
- SIPV-EL (Zenodo 14439369): EL + energy per cell, no second image modality [R: search snippet].
- PREDICTS2 (EPRI, DuraMAT): EL + flash I-V of 36 modules at 3 time points; no IR [R: Chen 2025 §5.2.3, snippet].
- PV-IV-EL (OpenEI / data.gov): EL at high and low injection + I-V; IR not confirmed [R: search snippet].
- PVF-10, InfraredSolarModules, Mendeley thermal sets: thermal only, module-level or box labels.

## 5. Discrepancies to flag for `check`
- InfraredSolarModules: README says 20,000 images; its class table sums to 20,006 [R].
- PVF-10: original paper 5,579 crops vs a 2025 paper's "about 8k" [R: search snippets].
- Univ. del Valle thermal set: 277 images on Mendeley v2 vs 67 in Chen 2025 review [R].
- UCF UVF set: page says 7,190 modules; Chen 2025 says 2,989 images for those modules [R]; both can be true (several modules per image).
- Bommes 2021: 107,842 modules in the dataset vs 122,865 modules in the 7 plants [R: snippet].
- UCF-EL size: Chen 2025 says 17,064 cells; our F04 census measured 11,851. Resolved by check: both true (local Test_Images holds 17,064 files; 11,851 is the official split) [check §5].
- csr6t vs Li 2024: the OSF page names Colvin et al. 2023 (JPV) as the companion paper, not Li 2024. Li 2024 is a separate 9-module study by an overlapping team; overlap of its 3 FL modules with csr6t is plausible but unconfirmed [S; check D-6]. Li 2024's camera setup (Sensovation CCD, Fluke Ti55, 10 min IR stabilisation) should not be assumed for csr6t, whose bulk EL is Nikon NEF and whose IR names say 180 s [R names].

## 6. Questions for Om (decisions, not facts)
1. Downloads need Om's OK. Sizes (R from file listings, verified by check D-3, D-4, D-12, D-13): A3 DTU 642.6 MB (one 7z); A1 IR 0.26 GB for all 157 modules; A1 UVF about 2.0 GB (S); A1 dark I-V about 2 MB; A1 EL 14.95 GB in full (946 NEF + 98 TIF), one bias per module (NEF at 3.393 A) about 2.2 GB (S: 159 x 13.8 MB); A2 EL 3.82 GB, A2 IR 0.02 GB; C1 about 1.38 GB (EL only 0.20 GB). Suggested order: A3, then A1 IR + one EL bias + dark I-V (about 2.5 GB), then A2 IR modules with their EL (about 0.2 to 1.4 GB).
2. Is a module-level pairing (EL and IR of the same module, aligned by homography) good enough for the ideas Om has in mind, or does he want pixel registration only from our own capture?
3. Licence check: all three core sets are CC BY 4.0 (R), so use in a thesis with citation is fine (S). Any objection to mixing them with BenchmarkEL (no licence file, E: F04)?
4. Should we ask WattCycle whether they already hold drone IR of plants whose modules also have EL (a private paired set may already exist)? Relayed to `capture`.

## 7. Questions for dataset authors (for Om to send if he wants; I did not contact anyone)
- UCF DPV group (OSF csr6t / ar76v; contacts are on the OSF pages, Davis / Colvin group): (a) csr6t IR: camera answered (ICI 8320P, Colvin 2023 §II.B via check); the txt is a 240 x 320 deg C matrix (E, discovery). Still open: file names say 180 s, Colvin says 5 min at Isc. Which is right? (b) Raw radiometric IR (temperature matrices) for csr6t, as provided for ar76v (.txt)? (c) Are any csr6t / ar76v cells part of UCF-EL? (d) Do the AZ (ASU) modules from Li 2024 have released EL + IR?
- DTU (Del Prado Santamaria, contact listed in the README): (a) EL camera and resolution; (b) cell count and technology of the 43 modules; (c) per-cell crack locations or EL annotations, if any; (d) any forward-bias (dark) IR taken in the lab on the same modules.
- NREL (Johnston, Kern): DLIT + EL + PL images of the half-cut-cell module from PVSC 2023; current location of the DuraMAT PLatypus and half-cut PL datasets after the hub move.
- Polenghi et al.: EL exposure / bias per stage; whether a thermal camera was used during damage stages.
- Lai et al. 2025: are EL, IR and RGB of the same modules, and is the data shareable?
- Almukhtar and Kurnaz: release of the 480 forward-bias LWIR images.
- Gallardo-Saavedra / Hernandez-Callejo (UVa): EL + IR + I-V images of the purpose-built 60-cell module.

## 8. Notes for the other agents
- `ideas`: A1 has per-cell dark I-V fitted from EL (folder `EL-Derived_Cell_Dark_I-V`, file `diode_fit_outputs.xls`) [R]. That is a physics label per cell that needs no annotator and could anchor "thermal as weak label" ideas (S).
- `capture`: A1's file names show a simpler protocol: IR at about 1 x Isc, 180 s after current on, with an EL frame at the same current [R: OSF names]. Li 2024's protocol is a fuller template: dark room, cooled Si CCD with 850 nm long-pass for EL, then IR of the same module at the same bias (0.1 to 1.0 x Isc), IR after 10 min stabilisation, EL and IR within 60 s of current injection for Rs accuracy [R: Li 2024 abstract, §2.2, §4]. The DTU paper gives drone IR settings: irradiance at least 600 W/m2 for disconnections, altitude 8 to 20 m makes little difference [R: EPJ PV 2025 abstract].

## 9. Check pass-1 fixes applied (2026-11-04)
All 15 FIX and 4 ADD items from check (check/factcheck.md §2) were applied to the table: D-3, D-4, D-5, D-6 (A1 file mix, EL composition and size, IR protocol from names, companion paper Colvin 2023, verified by me with Research MCP get_paper), D-9 (crack minor mode retagged S), D-12, D-13 (A2 EL currents and sizes, IR folder), D-17 (A3 native px per cell), D-19 (C1 damage types incl. abrasions / scrapes; camera setup), D-21 (D1 Cracking = module-surface cracking), D-24 (215 modules with IR), D-28 (B2 method), D-34 (PVF-10 DOI, verified with get_paper), D-39 (D8), D-40 (D9), D-25 / D-41 / D-42 / D-46 (adds). D5 SolarFCD details marked unverifiable.
