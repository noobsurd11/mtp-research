# Thermal (IR) for our EL segmentation: long idea list (Om's question 2)

Owner: `ideas`. Written 4 Nov 2026 (IST), desk study: no download, no GPU, no server access, no E1 or test read.
Status: v1.2 (12:39 IST: check pass-1 fixes applied; v1.1 updated for datascout v2 and capture v1), generative list for `synth` to rank. Ranking hints are mine (S) and may be ignored.

**Tags.** E = measured in our files (path given). R = from a source (Research MCP id or URL). S = my reasoning or speculation. Every number is tagged. Where a claim rests on a paper abstract only, it says "abstract".

**Codes used below.**
- Data: **P** = public paired set (datascout's `datasets/dataset_table.md` rows A1 `osf.io/csr6t`, A2 `osf.io/ar76v`, A3 DTU, B1, C1); **T** = public thermal-only set (rows D1-D3, PVF-10); **C** = own capture (WattCycle / IIT Mandi; see `capture/`); **N** = no new data.
- Targets: **SC** = scuff + half-cut crack miss on unseen modules; **UR** = unseen-module crack recall (~0.2); **IN** = small, concentrated inactive; **DE** = deployment (WattCycle field use); **SV** = severity / power (value-chain arrows 2 and 3).
- Cost: dev days / GPU-h / capture days / labelling hours. GPU-h use 1.1 GPU-h per ResNet-34 run at 100% labels, so ~5.5 GPU-h per 5-seed arm (E: `handbook/14_code_and_infrastructure.md` l.323). Capture days are rough (S); `capture` owns the real plan.
- Prior: my guess (S) that the idea gives a measurable gain on its own target: **H** high, **M** medium, **L** low.

---

## 0. Physics primer: what thermal shows vs EL, for our classes

EL images the light from radiative recombination while current is driven forward through the module in the dark, so a pixel is bright where current reaches healthy silicon and dark where it does not (inactive area), where carriers recombine non-radiatively (material defects), or where metal shades it (E: `handbook/02_domain_primer_EL_and_defects.md` §3). A thermal camera instead images the front-glass temperature, i.e. where electrical or optical power turns into heat, blurred by heat spreading through the glass and encapsulant (S). For our classes this gives a split. **Inactive area** carries no current, so under forward bias in the dark (the EL condition) it should dissipate less heat and read cooler than connected silicon, while in sunlight it converts no light to power and should read warmer (both S, standard device physics); if the lost current forces the whole cell into reverse bias it becomes a hot cell or hot spot (mechanism S). The observation is R (abstracts, which do not name the mechanism): doi:10.1038/s41598-021-03498-z, crack modes "shaded area" and "breakdown" gave hot spots of 25 to 100 °C, 12 cells; doi:10.1038/s41598-022-16546-z, cell temperature rose with crack area, but cells > 46% cracked showed no hot spot, 10 cells. **Thin cracks that isolate nothing** gave no hot spot in the same two studies (R: Dhimish's own "micro-crack" mode 2; that it equals Köntges mode A is my mapping, S), and in drone IR of 43 artificially degraded modules "modules with cell cracks are difficult to distinguish from healthy ones", while disconnected interconnects gave elongated patterns visible from 600 W/m² (R abstract: doi:10.1051/epjpv/2025020); so the crack pixels we segment are, in passive thermography, mostly invisible; only active methods heat the crack itself, e.g. ultrasound lock-in thermography on wafers and cells (R, abstract: openalex:W2189012330). **Scuff** (E-SCDD class 25) has no physical description in our files (E: `handbook/17_escdd_dataset_audit.md` §5.11; the Pratt 2025 power-loss paper only shows an example, `literature/pdfs_inst/pratt2025_ictas_powerloss/p.txt` l.199); if it is a surface mark that does not change current paths, it should be thermally silent like a mode-A crack (S, untested), so thermal separates damage by electrical consequence, not by line shape. Thermal sees directly several things EL shows only indirectly: shunts and pre-breakdown sites (reverse-bias and lock-in thermography; R: doi:10.1016/j.egypro.2014.08.097, doi:10.1109/pvsc.2008.4922478), failed solder joints as point-like "doublet" heating (R: doi:10.1109/jphotov.2020.3003781), series-resistance defects (R: doi:10.1016/j.solener.2024.112704, EL and IR patterns correlate better where solder bonds degrade), PID-shunted cells that are black in EL (R: doi:10.1016/j.seja.2023.100049), and hot diodes / substrings in drone IR (R: doi:10.1002/pip.3518). Two other modalities are closer to our hard cases: **PL** needs no electrical contact, so isolated regions still emit and "EL dark + PL bright" marks inactive area (S; a daylight-PL proof of concept, with lower image quality, is called "promising for identification of ... large area damage and inactive areas", R abstract: doi:10.1002/pip.3525), and **UV fluorescence** shows cell cracks in aged modules, in order of occurrence (R abstract: doi:10.1109/jphotov.2019.2961781), through the encapsulant, so it does not depend on EL texture (S). **Net (S):** thermal is a strong cell-level signal for inactive area, hot spots and severity, and a weak or null pixel-level signal for cracks and scuff. Its value for our segmenter is mainly as a training-time teacher, a weak label, a triage stage or a severity output, not as a crack-pixel input; for scuff vs crack, UVF, PL and RGB are the better-placed modalities.

### 0.1 Physics table (which signal each defect gives)

| Defect (our class) | EL (forward bias) | Forward-bias dark thermography (steady / lock-in) | Reverse-bias thermography | Outdoor IR in sunlight (drone) | PL | UVF (aged modules) | RGB |
|---|---|---|---|---|---|---|---|
| Crack, no isolation (14; Köntges mode A, S mapping) | dark line ~4 px, label 1-2 px (E: doc 02 §6.1) | none expected (S) | only if a breakdown site sits on it (S) | no hot spot for Dhimish's "micro-crack" mode (R: doi:10.1038/s41598-021-03498-z, doi:10.1038/s41598-022-16546-z); cracked modules hard to tell from healthy in drone IR (R: doi:10.1051/epjpv/2025020) | weak dark line from crack-face recombination (S) | crack line (R: doi:10.1109/jphotov.2019.2961781) | invisible, unless a snail trail forms (R: doi:10.1109/jphotov.2014.2330495, snail trails correlate with microcracks) |
| Crack isolating area, i.e. inactive (11; modes B/C) | dark region bounded by cracks; 99% of inactive components touch a crack (E: doc 02 §7) | cooler region (S) | none expected (S) | warmer region (S); hot spots with larger cracked / shaded areas (R: Dhimish 2021, 2022 above; reverse-bias mechanism S) | bright at open circuit; stays bright when current is extracted (S); daylight PL proposed as "promising" for inactive areas (R: doi:10.1002/pip.3525) | crack line around it (R) | invisible (S) |
| Scuff (E-SCDD 25; not in our 24) | long dark streak, 2.5k-4.6k px in the 4 largest E1 half-cut crack cells (E: doc 17 §5.11) | unknown; silent if surface-only (S) | unknown | unknown | dark if recombination-type, bright if it only blocks current (S): a direct test of what scuff is | no crack line expected if no through-crack (S, untested) | visible if a surface mark (S) |
| Half-cut cut line / spacing (feature) | dark gap (E: doc 18 §U) | gap carries no current (S) | edge shunts possible (S) | n/a | dark gap (S) | edge frame pattern (S) | visible (S) |
| Finger interruption (gridline 15) | short dark streaks (E: doc 02 §3) | small local Joule heating, likely below module-scale resolution (S); EL + IR histograms separate broken fingers in aged mono modules (R abstract: doi:10.1016/j.solener.2018.07.055) | n/a | not visible (S) | weak (S) | no (S) | no (S) |
| Shunt / PID-s (dead cell 17, partly) | dark cell or dark spots (S) | hot spot (S; R: doi:10.1109/pvsc.2008.4922478) | hot spot (R: doi:10.1016/j.egypro.2014.08.097) | warm cell; PID hot spots near 50 °C (R: doi:10.1038/s41598-022-16546-z) | dark (S) | no (S) | no (S) |
| Solder bond / ribbon failure (crack rbn edge 10, ribbons 4) | darker cell or region (S) | point-like doublet heating at joints (R: doi:10.1109/jphotov.2020.3003781) | n/a | warm joint / ribbon (S) | n/a | hot parts shown (R: doi:10.1109/jphotov.2019.2961781) | burn marks if severe (S) |
| Material (13) | dark texture (E: doc 02 §5) | recombination-active regions draw more diode current, slightly warm (S; grain-boundary recombination by LIT, R: doi:10.1016/j.egypro.2013.07.263) | n/a | none (S) | dark (S) | no | no |

Resolution check (R, web; secondary sources, standard text not read): Sitemark reads IEC TS 62446-3 as max 3 cm per pixel and about 25 measurements per cell, with ≥ 600 W/m² ([Sitemark](https://www.sitemark.com/blog/is-sitemark-iec-compliant/)) (Sitemark alone; the FLIR page cited in v1.1 now redirects to a 404, per `check`). The A3 drone study flew at < 1 to 3 cm per pixel (R: doi:10.1051/epjpv/2025020). So drone IR is a **cell-level** signal; our EL crops are 512 × 512 per cell neighbourhood (E: doc 02 §4). Indoor or close-up IR is finer; lock-in improves spatial resolution and sensitivity (R abstract: doi:10.21611/qirt.2018.b).

---

## 1. The data reality (from datascout's table v2, read 12:15 IST; capture plan v1)

- **No public pixel-labelled EL + thermal set exists in datascout's table** (R via `datasets/dataset_table.md` v2). The open EL + IR pairs, all CC BY 4.0 and paired at module level, are:
  - **A1 `osf.io/csr6t`**: Shell M55 modules, EL bias sweep 0.01-1 × Isc, indoor UVF, I-V, EL-derived per-cell dark I-V fits; about 156 × 36 ≈ 5,600 cells (S, datascout). **IR is forward-bias thermography at 3.392-3.393 A (≈ 1 × Isc), 180 s after current on, for 157 modules, and each module's 6-level EL sweep includes 3.393 A** (R: OSF file names, read by `check`). The study is Colvin et al. 2023 (R: doi:10.1109/jphotov.2023.3238278, named on the OSF page per `check`): 156 modules characterised; losses "primarily resistive" (rear-contact Ag / solder corrosion), and the EL pattern is shown to be resistive by comparison with PL (abstract). So A1 is a series-resistance set more than a crack / inactive set (S).
  - **A2 `osf.io/ar76v`**: 42 modules; forward-bias IR at 5.289 A, 60 s, for 16 captures of 15 modules (R: `check`); EL at several currents.
  - **A3 DTU 10.11583/DTU.29665346**: 43 artificially degraded modules (cell cracks, PID, interconnect disconnection, glass cracks, shorted bypass diodes, soiling), drone IR at 8-20 m and 200-1000 W/m², EL and I-V per module, module-level defect class by folder (R: datascout A3; doi:10.1051/epjpv/2025020). The only set with cracks induced on purpose and imaged in both EL and drone IR.
  - No masks in any (R: datascout). About 215 public modules have EL + IR (A1 157, A2 15, A3 43; R: `check`).
- **Li et al. 2024 is a separate 9-module study** (3 Florida Shell + 1 control + 5 Arizona Siemens) by an overlapping team (R: `check`; doi:10.1016/j.solener.2024.112704); overlap of its Florida modules with A1 is plausible (S).
- **Calibration for G0 (R via `check`, JRC report JRC105705, Berardone, Paggi, Lopez Garcia 2017, not read by me):** dark IR gave "few local information", while illuminated IR was "promising to distinguish between classes of damage in line with EL data". So a weak G0 result on A1 / A2 dark IR is expected and is not by itself a kill for illuminated-IR ideas (A3, own capture).
- **A1 / A2 are mono Al-BSF full-cell modules** (R: datascout). Our failure context is half-cut multi cells with scuff (E: doc 18 §U; doc 20 l.71). So public pairs serve **inactive, severity and deployment**, and very likely **not** the scuff + half-cut context (S). Only own capture (C) reaches that context.
- **WattCycle may be better placed than the handbook says** (R via `capture/capture_plan.md` §1.1): a June 2025 IIT Mandi PV-recycling startup whose site lists thermal + RGB drone flights, a digital-twin platform and a recycling service; same company as ours is likely, not confirmed (capture flags this for Om). If so: (a) drone IR already exists in its workflow, which raises the deployment ideas (T08, T26, T27, T29); (b) end-of-life modules are aged, so UVF crack lines should exist (T32), and sacrificial modules allow reverse-bias work (T36) (S).
- **BenchmarkEL, test and E1 have no thermal** (E: doc 03). Any gain on our benchmarks must come from an EL-only model that used paired data at training time (sections 2B, 2C), or from new labels.
- **Downloads need Om's OK** (README rules). Sizes (R from `check` and datascout; S arithmetic): A1's whole IR folder is 0.26 GB (157 modules); A1 bulk EL is Nikon NEF ~13.8 MB per frame (98 older TIF are 16.7 MB), so one 3.393 A EL frame per module is ≈ 2.2 GB for all 157 or ≈ 0.15 GB for 10 (S); A2's IR folder is 0.02 GB and its 15 matching 5.289 A EL frames ≈ 0.2 GB (S); A3's archive is 0.64 GB.
- **UCF-EL link (E, CPU count today on our local copy `~/mtp/datasets/UCF-EL-Defect/AnnotationsCombined.csv`, reproduced by `check`):** 373 module ids; 201 have exactly 60 annotated cells, so they are 60-cell modules and not A1's 36-cell Shell M55 (S, datascout for 36). The other 172 are partial: 109 have highest cell position ≤ 36 (46 stop at 12, 28 at 32, 1 at 36), so a link to A1 is **not excluded** for them. Names are anonymised (`M####C######`). See T38.

### 1.1 One shared gate before most ideas: G0 "is there a thermal signal at cell level?"
- **What (CPU), scope set by Om's decisions of 4 Nov (`om_2026-11-04_decisions.md`; `synth/top3.md` l.29-42):** on the **approved set only**: A3, A2's IR folder + its matching EL, A1's 10 modules (EL, IR, UVF) + all dark I-V files. **Proposal, not approved (sent to synth for SUMMARY):** all 157 A1 IR captures (0.26 GB) for fleet-level thermal statistics, and later the remaining A1 EL (≈ 2 GB) if the 10-module step shows a signal; both need Om's OK. A3 gives the sunlit drone-IR condition on modules with induced cracks and disconnections; per the JRC calibration above, A3 is the fairer test for inactive-like defects, since A1 is mostly resistive (S).
- **Read:** Spearman ρ between EL dark-area (or predicted inactive) fraction and ΔT within modules; AUROC of ΔT for cells with predicted inactive ≥ 5% of cell area; sign vs the primer (cooler under forward bias, S).
- **Kill for the fusion / weak-label families:** |ρ| < 0.3 and AUROC < 0.7 in both conditions (dark forward-bias IR on A1 / A2, and sunlit IR on A3). A null on dark IR alone moves those families to illuminated IR, not to the bin (JRC calibration above). **Go:** AUROC ≥ 0.8 with the predicted sign in either condition.
- **Cost:** 2 dev days CPU, 0 GPU, 0 capture. Also feeds `capture` (is steady-state IR enough or is lock-in needed).

---

## 2. Ideas (40)

### Summary table

| ID | Idea | Family | Targets | Data | Cost (dev d / GPU-h / capture d / label h) | Prior (S) |
|---|---|---|---|---|---|---|
| T01 | Early fusion: EL + registered thermal as input channels | fusion | IN, SV | C (+P for pretrain) | 4 / 11 / 3-5 / 2-6 | M (needs capture) |
| T02 | Late fusion: thermal ΔT updates each cell's inactive prior | fusion | IN, DE | P, C | 2 / 0 / 0-3 / 0 | M |
| T03 | Guided fusion: low-res thermal map modulates the decoder | fusion | IN | C | 6 / 15 / 3-5 / 2-6 | L |
| T04 | Missing-modality training (modality dropout) | fusion | DE, IN | BenchmarkEL + P/C | 4 / 11 / as T01 / 0 | M (enabler) |
| T05 | Multi-condition thermal "fingerprint" to type EL-dark regions | fusion | IN, SC, SV | C | 5 / 3 / 3-5 / 1 | M |
| T06 | Auxiliary thermal-prediction head (train only) | distil | IN, UR | P | 3 / 11 / 0 / 0 | M |
| T07 | Thermal teacher → EL student, cell-level consequence | distil | IN, SV | P | 4 / 11 / 0 / 0 | M |
| T08 | EL teacher → thermal student for drone IR | distil | DE, SV | P, T | 4 / 3 / 0 / 0 | H (for DE) |
| T09 | Contrastive EL-thermal pretraining (CMC) | pretrain | UR, IN | P | 5 / 20-30 / 0 / 0 | L |
| T10 | Cross-modal masked autoencoding (EL → thermal) | pretrain | UR, IN | P | 6 / 25-40 / 0 / 0 | L |
| T11 | Thermal-privileged hard-pixel weighting | distil | IN | C | 3 / 11 / as T01 / as T01 | L |
| T12 | Thermal cell-level inactive labels + mixed supervision | weak label | IN, UR | P | 4 / 11 / 0 / 0.5 | M-H |
| T13 | Cross-modal agreement filter on pseudo-labels (new-domain pool) | weak label | IN, UR | P | 3 / 11 / 0 / 0.5 | M |
| T14 | Hot-spot labels → crack-mode (A vs B/C) head | weak label | SV | P, C | 3 / 3 / 0 / 0 | M |
| T15 | A1's per-cell dark I-V as a physics weak label | weak label | IN, SV | P | 2 / 3-11 / 0 / 0 | M |
| T16 | Thermal-disagreement active learning and label QA | weak label | IN, UR | C | 2 / 1 / as T01 / 1.5-3 | M |
| T17 | Physics EL → thermal simulator (signal calculator, synthetic pairs) | synthesis | IN, DE | N | 5-8 / 0 / 0 / 0 | H (as a tool) |
| T18 | Learned EL → thermal translation for rare-defect IR training | synthesis | DE | P, T | 4 / 6 / 0 / 0 | M |
| T19 | Thermal → EL coarse inverse (inactive fraction from IR) | synthesis | DE, SV | P | 4 / 5 / 0 / 0 | L-M |
| T20 | Physics-consistent inactive in synthetic half-cuts (HC follow-up) | synthesis | SC, IN | N | 4 / 11 / 0 / 0 | M |
| T21 | Inactive-strength augmentation (thermo-mechanical crack opening) | synthesis | IN, UR | N | 2 / 11 / 0 / 0 | M |
| T22 | Thermal-silence test for scuff (Om's "check") | generalise | SC | C (+P scan; C1 abrasion probe) | 1 / 0 / 1-2 / 0 | H (as a test) |
| T23 | Thermal as a domain-invariant anchor (DADA-style alignment) | generalise | UR | P | 5 / 15 / 0 / 0 | L |
| T24 | Test-time per-module bias from thermal | generalise | UR, IN, DE | C | 2 / 0 / as T01 / 0 | M |
| T25 | Temperature-normalised field EL | generalise | UR, DE | C | 2 / 0 / 1 / 0 | L-M |
| T26 | Drone IR screening → targeted EL: screening-recall table | pipeline | DE, SV | P | 3 / 0 / 0 / 0 | H (for DE) |
| T27 | Hot-spot risk score from the EL segmentation | pipeline | SV, DE | P | 2 / 0 / 0 / 0 | M-H |
| T28 | IR + EL time series: crack-to-inactive progression | pipeline | SV, DE | C (multi-visit) | 3 / 0 / 2+ visits / 0 | L (thesis) |
| T29 | One drone flight: IR + daylight EL/PL; segmenter robust to daylight EL | pipeline | DE, UR | P (B2), C | 4 / 11 / 2-3 / 0 | M |
| T30 | Inline EL + thermography → local loss maps (QAM-style) | pipeline | SV | C (factory) | 8 / 10 / n/a / 0 | L (now) |
| T31 | EL / PL contrast → automatic inactive masks | other modality | IN | P (B1, B2), C | 3 / 0 / 2-3 / 0 | H |
| T32 | UVF crack lines → crack vs scuff labels | other modality | SC, UR | P (A1), C | 3 / 0 / 1-2 / 0 | M-H |
| T33 | Multi-current EL (bias sweep) as an extra channel / label | other modality | SC, IN | P (A1, A2), C | 2 / 0-11 / 1 / 0 | M |
| T34 | RGB photo: surface streaks and snail trails | other modality | SC | C1 probe, then C | 2 / 0 / 0.5 / 0 | M |
| T35 | Ultrasound lock-in thermography as crack-only ground truth | other modality | SC | C (lab) | 2 / 0 / 2-5 / 0 | L |
| T36 | Reverse-bias thermography for shunts / hot-spot-prone cells | other modality | SV | C | 2 / 3 / 1-2 / 0 | L (for seg) |
| T37 | Registered cell-level EL + IR + UVF benchmark from A1 (release) | data | IN, DE | P | 5 / 0 / 0 / 0 | H (as output) |
| T38 | UCF-EL ↔ FSEC IR / UVF link: labelled pairs for free | data | IN, UR | P + UCF-EL | 1-2 / 0 / 0 / 0 | L-M (201 of 373 UCF-EL modules are 60-cell, so not A1; 172 partial ones not excluded) |
| T39 | Thermal-outcome-weighted evaluation (severity-aware metric) | eval | SV, DE | P | 2 / 0 / 0 / 0 | M |
| T40 | Thermal-only pretraining of the EL encoder (PVF-10 etc.) | pretrain | UR | T | 3 / 10 / 0 / 0 | L |

### 2A. Multimodal fusion (thermal at training and at deployment)

**T01. Early fusion: EL + registered thermal as input channels**
- **Mechanism:** add 1-2 input channels (forward-bias thermography; optionally illuminated IR) to U-Net++ R34, zero-initialised so the start equals E-PF's recipe; the network can use "carries current / dissipates" to tell inactive from other dark EL (S).
- **Targets:** IN (small, concentrated inactive), SV.
- **Data:** C with masks (no public masked pairs, section 1). P (A1) only as unlabelled pretraining.
- **Cost:** 4 / 11 (2 arms × 5 seeds) / 3-5 capture days for ~20 modules (S) / 2-6 h if inactive masks are drawn on new cells (S: ~200 cells with E-PF pre-masks, 1-2 min each to accept or fix); 0 h if E-PF masks are accepted unchecked (circular, not advised).
- **First experiment:** G0 (section 1.1).
- **Kill / success:** kill at G0; then, on held-out captured modules, inactive IoU Δ vs EL-only on the same cells (rule 1 style). Success: Δ ≥ 0.05 with no crack loss.
- **Tags:** R: RGB-thermal fusion networks (doi:10.1109/lra.2019.2904733, RTFNet); EL + IR + RGB feature-level fusion claims gains "particularly for heat-related fault patterns" (R abstract: doi:10.3389/feart.2025.1702396; its pairing is "statistically paired", so not physically co-registered, S). S for the inactive mechanism.

**T02. Late fusion: thermal ΔT updates each cell's inactive prior**
- **Mechanism:** keep E-PF unchanged; per cell, a logistic model on (E-PF inactive probability mass, IR ΔT vs string median) sets a per-cell inactive bias. Tolerates 5 × 5 px drone IR (S).
- **Targets:** IN precision and recall on unseen modules; DE.
- **Data:** P to fit (A1: label = A1's per-cell dark I-V degradation, T15, not E-PF itself, to avoid circularity); C to validate with masks.
- **Cost:** 2 / 0 / 0 (P) or 3 (C) / 0.
- **First experiment:** G0, then on A1: AUROC for "degraded cell" (from A1 dark I-V) of E-PF inactive mass alone vs plus ΔT.
- **Kill / success:** kill if ΔT adds < +0.03 AUROC; success ≥ +0.05.
- **Tags:** S; per-cell dark I-V exists in A1 (R: datascout A1).

**T03. Guided fusion: low-res thermal map modulates the decoder**
- **Mechanism:** thermal enters as a blurred guidance map (FiLM or cross-attention at the 1/8 to 1/16 decoder stages), not as a pixel channel, so a few pixels of misregistration and heat blur do not matter (S).
- **Targets:** IN.
- **Data:** C with masks.
- **Cost:** 6 / 15 / 3-5 / 2-6.
- **First experiment:** after T01 has data: T03 vs T01 on the same split.
- **Kill / success:** kill if not ≥ T01 by +0.02 inactive IoU.
- **Tags:** R: RGB-T fusion designs (doi:10.1109/tcsvt.2023.3281419 SGFNet; doi:10.1109/icra57147.2024.10611200 complementary random masking). S for EL.

**T04. Missing-modality training (modality dropout)**
- **Mechanism:** one network that runs on EL alone (BenchmarkEL, E1, most field data) and uses thermal when present; train with the thermal branch randomly dropped, and with BenchmarkEL always EL-only. This is how any fusion must be built here, since our labelled set has no thermal (E: section 1).
- **Targets:** DE; IN when thermal is present.
- **Data:** BenchmarkEL + P or C pairs.
- **Cost:** 4 / 11 / as T01 / 0.
- **First experiment:** EL-only guard: the fused model with thermal absent vs E-PF on val (no test read): crack AP and inactive IoU within E-PF's seed spread.
- **Kill / success:** kill if the EL-only path loses > 0.01 val crack AP; success = guard held and T01-level gain when thermal is present.
- **Tags:** R: doi:10.1609/aaai.v35i3.16330 (SMIL, severely missing modality); doi:10.1109/wacv57701.2024.00106 (missing-modality robustness in semi-supervised multimodal segmentation); doi:10.1109/tpami.2024.3476487.

**T05. Multi-condition thermal "fingerprint" to type EL-dark regions**
- **Mechanism:** capture each module under forward-bias dark, illuminated and reverse-bias thermography; the sign pattern per EL-dark region (cool / warm / hot-in-reverse) types it: inactive (cool forward, warm illuminated), shunt / PID (hot forward and reverse), material (slightly warm forward), surface mark such as scuff (silent everywhere) (S; R: doi:10.1016/j.solener.2018.07.055 uses forward-bias and illuminated IR with EL to separate interconnect, corrosion and broken fingers, abstract).
- **Targets:** IN, SC (what scuff is), SV.
- **Data:** C (lab or field with a power supply and shading).
- **Cost:** 5 / 3 (cell classifier) / 3-5 / 1 (spot checks).
- **First experiment:** 5 modules with known EL defects incl. a scuffed half-cut module; tabulate signs per defect type.
- **Kill / success:** kill if inactive and scuff give the same sign pattern in all conditions; success if ≥ 3 of the defect types separate.
- **Tags:** R above, plus doi:10.1016/j.energy.2020.117930 (EL + IRT + I-V + visual on a purpose-built defect module, abstract). S for the sign table.

### 2B. Cross-modal pretraining and distillation (thermal at training only)

**T06. Auxiliary thermal-prediction head (train-time only)**
- **Mechanism:** multi-task: the EL network also regresses the cell's thermal map (or ΔT) on paired cells; predicting heat requires knowing which regions carry current, so the shared encoder learns connectivity (S). At deployment the head is dropped: EL-only, zero runtime cost.
- **Targets:** IN, UR (A1 adds Florida mono modules: a new domain).
- **Data:** P (A1/A2 pairs, no masks) + BenchmarkEL masks.
- **Cost:** 3 / 11 / 0 / 0.
- **First experiment (CPU):** how much of cell ΔT is predictable from simple EL cell statistics (held-out modules, R²). If R² > 0.9 the head learns nothing new; if < 0.1 it is noise; 0.2-0.8 → go (S).
- **Kill / success:** protocol on val + F51 / H36 (no test until a locked protocol): kill if val inactive and F51 crack AP both n.d.; success then needs a registered test / E1 opening.
- **Tags:** R: doi:10.1109/cvpr.2016.309 (supervision transfer across paired modalities); doi:10.1007/978-3-031-19836-6_20 (MultiMAE, multi-task). E: PF keeps encoder layers that the house fine-tune erases (doc 00 fact 10), so an auxiliary task has a chance to persist under PF (S).

**T07. Thermal teacher → EL student for cell-level consequence**
- **Mechanism:** train a small teacher on thermal (and I-V) to score "electrically consequential damage" per cell; distil its soft score into an EL cell-level head that sits beside the segmentation head (learning using privileged information).
- **Targets:** IN, SV.
- **Data:** P.
- **Cost:** 4 / 11 / 0 / 0.
- **First experiment:** G0; then teacher AUROC for A1's degraded cells (T15 label).
- **Kill / success:** kill if teacher AUROC < 0.8; success if the EL student's cell score reaches ≥ 0.9 of the teacher's AUROC on held-out A1 modules and val inactive is not worse.
- **Tags:** R: doi:10.1109/tpami.2019.2929038 (adversarial discriminative modality distillation, LUPI); doi:10.1109/cvpr.2018.00926 (privileged information via heteroscedastic dropout); doi:10.1016/j.inffus.2025.103572 (cross-modal distillation for incomplete multimodal industrial anomaly detection).

**T08. EL teacher → thermal student for drone IR (reverse supervision transfer)**
- **Mechanism:** our EL model labels the EL half of each pair (inactive fraction, crack mode); a thermal cell classifier learns those labels from IR. WattCycle gets an IR model that knows which hot or cool cells are inactive-area cells, trained without IR annotators. Keep it small (the advisor wants a lightweight model, remembered as ~2M or ~4M parameters; the user allows up to ~5M; E: doc 01 l.25, l.89).
- **Targets:** DE, SV.
- **Data:** P (A1, A2); T (PVF-10 doi:10.1016/j.apenergy.2024.124187, 5,579 crops from 8 plants; InfraredSolarModules) for out-of-domain checks.
- **Cost:** 4 / 3 / 0 / 0.
- **First experiment:** G0 is this idea's first experiment.
- **Kill / success:** kill at G0; success if the IR student reaches AUROC ≥ 0.8 on held-out A1 modules for E-PF-inactive cells.
- **Tags:** R: doi:10.1109/cvpr.2016.309; cross-plant IR domain shift: ResNet-34 + supervised contrastive + kNN, AUROC 73.3-96.6% over 9 source-target pairs, 2.92 M IR images (R abstract: doi:10.1002/pip.3518).

**T09. Contrastive EL-thermal pretraining (CMC) at cell level**
- **Mechanism:** align EL and thermal embeddings of the same cell (InfoNCE). Features that predict heat should ignore thermally silent texture (grain, rings, maybe scuff) (S). Then PF fine-tune on BenchmarkEL.
- **Targets:** UR, IN.
- **Data:** P (A1: 156 modules, ≈ 5,600 cells; S, datascout).
- **Cost:** 5 / 20-30 / 0 / 0.
- **First experiment:** frozen linear probe, as in the A8 screen: F51 crack AP and val inactive vs ImageNet R34 features (2-3 GPU-h).
- **Kill / success:** kill if the F51 AP difference's bootstrap lower bound < 0 and val inactive not better (same gate style as A8).
- **Tags:** R: doi:10.1007/978-3-030-58621-8_45 (CMC); doi:10.1109/lgrs.2021.3109345 (CMC with a second modality helps SAR segmentation). E against: A8 foundation encoder KILL (doc 21 §1); MIM n.d. at 5% and under PF (doc 11 rows 22, 25); P15 transfer null (doc 00 fact 10). Hence prior L.

**T10. Cross-modal masked autoencoding (EL → thermal)**
- **Mechanism:** MultiMAE-style: mask EL patches, reconstruct EL and the thermal map; a variant of T09 with a generative target.
- **Targets:** UR, IN. **Data:** P. **Cost:** 6 / 25-40 / 0 / 0.
- **First experiment / kill:** as T09 (frozen probe, A8-style gate).
- **Tags:** R: doi:10.1007/978-3-031-19836-6_20; MultiMAE robust to missing inputs in MRI (R: doi:10.1007/978-3-032-09513-8_55). E against: as T09. Prior L.

**T11. Thermal-privileged hard-pixel weighting**
- **Mechanism:** during training only, up-weight the EL loss in regions where thermal is anomalous but the EL model is unsure (hard pixels that matter physically).
- **Targets:** IN. **Data:** C with masks. **Cost:** 3 / 11 / as T01 / as T01.
- **First experiment / kill:** vs T04's EL-only path on the same captured split; kill if Δ inactive IoU < +0.02.
- **Tags:** R: doi:10.1109/tmm.2020.3035231 (hard pixel mining for depth-privileged segmentation). Prior L.

### 2C. Thermal (and physics) as weak labels

**T12. Thermal cell-level inactive labels + mixed supervision**
- **Mechanism:** inactive is data-limited (in 43 of 478 train cells, old masks; the top 3 test cells hold 59% of its px; E: doc 02 §7). Thermal flags give cell-level "has consequential inactive" labels on thousands of unlabelled A1 cells; train with mixed supervision (pixel masks on BenchmarkEL, cell labels on A1).
- **Targets:** IN, UR (new modules).
- **Data:** P (A1).
- **Cost:** 4 / 11 / 0 / 0.5 (user glances at 20 flagged cells to estimate purity).
- **First experiment:** G0, then count A1 cells flagged by ΔT, and purity on 20 flagged cells (E-PF overlap or a 10 min glance).
- **Kill / success:** kill if < 50 flagged cells or purity < 70%; success ≥ 200 cells at ≥ 70% purity, then a 5 v 5 arm with an inactive guard (as SKR2_HC2's G1).
- **Tags:** R: doi:10.1016/j.compind.2021.103459 (mixed supervision: a few pixel masks plus many image labels approach full supervision on KolektorSDD2). E: inactive scarcity (doc 02 §7); E1 inactive is a 3-image readout (doc 21 §6), so any E1 inactive claim stays fragile.

**T13. Cross-modal agreement filter on pseudo-labels (new-domain pool)**
- **Mechanism:** pseudo-label A1 EL cells with E-PF; keep inactive pseudo-labels only where thermal and A1's per-cell dark I-V agree; add as extra training data. Our pseudo-label SSL was a tight null at 20 to 100% labels on the CSIR / ARTS pool (E: doc 00 fact 10, 27 Oct synthesis); here the pool is a new domain and the filter is independent of the model (S), which is the case the null did not test.
- **Targets:** IN, UR.
- **Data:** P.
- **Cost:** 3 / 11 / 0 / 0.5.
- **First experiment:** precision of filtered vs unfiltered pseudo-inactive on 30 A1 cells (glance, 0.5 h).
- **Kill / success:** kill if filtered precision < 0.8 or not ≥ unfiltered + 0.1.
- **Tags:** R: doi:10.1109/iccv.2017.211 (distillation from noisy labels). E: in-domain SSL null (doc 00 fact 10, doc 18). S for the new-domain argument.

**T14. Hot-spot labels → crack-mode (A vs B/C) head for severity**
- **Mechanism:** label each E-PF crack component by whether its cell is thermally anomalous; train a crack-mode head. Gives WattCycle the severity step (value chain arrow 2; E: doc 02 §1).
- **Targets:** SV.
- **Data:** P, C.
- **Cost:** 3 / 3 / 0 / 0.
- **First experiment:** on A1, share of E-PF crack components in thermally anomalous cells; does per-cell E-PF inactive area predict ΔT?
- **Kill / success:** kill at G0 or if mode labels are < 10% positive (too few B/C cells).
- **Tags:** R: crack modes vs hot spots (doi:10.1038/s41598-021-03498-z); worst hot spots at 40-60% shaded fraction (same, abstract; per `check`, that is progressive shading of a single mode-3 cracked cell under a sun simulator, so reading it as an in-module inactive fraction is S). E: Köntges modes in F04 §4.

**T15. A1's per-cell dark I-V as a physics weak label (no thermal needed)**
- **Mechanism:** A1 ships EL-derived per-cell dark I-V fits (R: datascout A1). Cells with high series resistance or low current are "electrically degraded" without any annotator; use as a cell label (T12) or as the independent reference for T02 / T07 / T13.
- **Targets:** IN, SV. **Data:** P. **Cost:** 2 / 3-11 / 0 / 0.
- **First experiment:** read A1's per-cell fit files; distribution of the degraded share; correlation with EL dark-area fraction (CPU).
- **Kill / success:** kill if fits exist for < 50% of cells or show no spread.
- **Tags:** R: datascout A1; EL series-resistance imaging (doi:10.1002/pssa.202000546). S.

**T16. Thermal-disagreement active learning and label QA**
- **Mechanism:** among captured cells, label first where EL model and thermal disagree (predicted inactive but thermally normal, or the reverse); the same disagreement list audits existing inactive labels.
- **Targets:** IN, UR.
- **Data:** C.
- **Cost:** 2 / 1 / as T01 / 1.5-3 h (30-60 cells at ~3 min, S).
- **First experiment:** rank captured cells by disagreement; check the top 30 vs 30 random for label value.
- **Kill / success:** kill if the top 30 hold no more inactive / mislabel cases than random.
- **Tags:** S. E: targeted crack cells beat random cells at +12 labels (doc 00 Track D, oracle-selected). The user avoids labelling: hours stated.

### 2D. Synthesis (EL ↔ thermal)

**T17. Physics EL → thermal simulator (signal calculator and synthetic pairs)**
- **Mechanism:** from an EL image and its inactive mask, solve a 2D diode-network (local junction voltage, sheet and finger resistance) and a heat-spreading model through glass, giving the forward-bias and illuminated thermal maps. Uses: (a) tell `capture` whether steady-state IR can see a small inactive region or lock-in is needed; (b) synthetic pairs for T04 / T06 before any capture; (c) "what a drone sees" for T26.
- **Targets:** IN, DE. **Data:** N. **Cost:** 5-8 / 0 / 0 / 0 (CPU).
- **First experiment:** simulated ΔT for an inactive region of 5%, 10% and 25% of a cell at Isc forward bias; compare with the camera noise floor `capture` lists.
- **Kill / success:** kill as a capture guide if no plausible parameters reproduce the sign and size of G0's measured ΔT; success = matches G0 within 2× and gives a minimum detectable inactive area.
- **Tags:** R: finite-element electrothermal model compared with IR and DLIT images (doi:10.1016/j.solener.2020.08.058, thin-film OPV, abstract); local I-V from lock-in thermography (doi:10.1016/j.egypro.2016.07.003). S for c-Si.

**T18. Learned EL → thermal translation to train IR models on rare defects**
- **Mechanism:** pix2pix on A1 pairs; feed EL cells with rare defects (inactive, large cracks) to generate realistic IR crops; add them to IR training for WattCycle's drone model (T08).
- **Targets:** DE. **Data:** P, T. **Cost:** 4 / 6 / 0 / 0.
- **First experiment:** train on 80% of A1 modules; per-cell ΔT error on 20% held out vs a mean-ΔT baseline.
- **Kill / success:** kill if no better than the baseline by 20%.
- **Tags:** R: doi:10.1109/cvpr.2017.632 (pix2pix); class-conditioned thermal GAN on InfraredSolarModules, FID 35.4, better calibration (ECE 1.5%) than reweighting (R abstract: doi:10.1038/s41598-026-67806-1).

**T19. Thermal → EL coarse inverse (inactive fraction from IR)**
- **Mechanism:** predict per-cell inactive fraction (not cracks) from IR alone, for sites with drone IR but no EL. Cracks are not in thermal (section 0), so only coarse damage is recoverable (S).
- **Targets:** DE, SV. **Data:** P. **Cost:** 4 / 5 / 0 / 0.
- **First experiment:** on A1 held-out modules, correlation of predicted vs E-PF inactive fraction.
- **Kill / success:** kill if Spearman < 0.5.
- **Tags:** S; R: no-hot-spot cracks (doi:10.1038/s41598-022-16546-z).

**T20. Physics-consistent inactive in synthetic half-cuts (HC follow-up)**
- **Mechanism:** HC leaned worse on test inactive (−0.0228, seed-aware CI [−0.054, +0.005]; E: doc 21 §2) and HC2's ignore design failed (E: doc 21 §4). An electrical-connectivity rule (which region stays connected to a busbar after the virtual cut; geometric criteria for inactive area, R: doi:10.1038/srep04506) could relabel synthetic views consistently instead of ignoring inactive. EL-only, born from the thermal / electrical model of T17.
- **Targets:** SC, IN. **Data:** N. **Cost:** 4 / 11 / 0 / 0.
- **First experiment (CPU):** on SHV1 (frozen synthetic half-cut val, E: doc 21 §0), count views where the cut leaves a region whose connectivity label is wrong under the rule.
- **Kill / success:** kill if < 2% of synthetic views are affected (cannot explain HC's lean). The user kept the HC route open (E: doc 21 §4.4).
- **Tags:** E above; R: Paggi 2014 (abstract: simple geometric criteria exist, but cracked regions can reconnect on unloading); S.

**T21. Inactive-strength augmentation (thermo-mechanical crack opening)**
- **Mechanism:** a crack can open or close with load and temperature, so the same crack may isolate fully, partly or not at all (R: doi:10.1038/srep04506, recovery on unloading). Augment EL by dimming the region beyond labelled cracks to a sampled darkness, and train inactive at each darkness level. Test inactive is darker relative to its surround than train (median inside/ring 0.34 vs 0.55; E: doc 02 §7), so a darkness range is a real shift (S).
- **Targets:** IN, UR. **Data:** N. **Cost:** 2 / 11 / 0 / 0.
- **First experiment (CPU):** inside/ring darkness distribution of val inactive vs the augmentation range; then a 5 v 5 arm with an inactive guard.
- **Kill / success:** kill if val inactive IoU n.d. and F51 / H36 false alarms rise (G2-style).
- **Tags:** R, E above; S.

### 2E. Thermal for unseen-panel generalisation

**T22. Thermal-silence test for scuff (Om's "is thermal less sensitive to scuff texture? check")**
- **Mechanism:** measure IR contrast along EL scuff streaks, along the crack branches beside them, and on background, under forward bias and in sunlight, on real half-cut multi modules with scuff. Expected (S): scuff silent and branch cracks that isolate nothing also silent (R: no hot spot for Dhimish's micro-crack mode, doi:10.1038/s41598-021-03498-z; reading that mode as Köntges mode A is S), so thermal cannot fix crack recall in this context directly; it can only mark cells where the streak or branches isolate area.
- **Targets:** SC (decides whether any thermal idea can touch it).
- **Data:** C (WattCycle half-cut modules). Public pre-check: A3's cell-crack modules in drone IR (R: the A3 paper already reports cracked modules hard to tell from healthy, doi:10.1051/epjpv/2025020); scan P for any half-cut module (S: unlikely). Public scuff analogue (no thermal): C1 (Polenghi et al. 2026, doi:10.1016/j.dib.2026.113109) has pixel-aligned EL + NIR + visible HDR of one poly cell type through abrasion, scrape and cut stages with power; do abrasion / scrape stages give an EL streak like E-SCDD scuff, and does power drop? (R abstract; the analogy to scuff is S).
- **Cost:** 1 / 0 / 1-2 / 0.
- **First experiment:** 3-5 scuffed half-cut modules, EL + forward-bias IR + one illuminated IR frame.
- **Kill / success:** kill "thermal for SC" if neither scuff nor branch cracks show contrast above noise (my expected outcome, S); success if scuff is silent and branch cracks with isolation are visible (then T05 / T24 apply to SC).
- **Tags:** R, S as stated. E: the SC context (75% of E1 crack px, recall 0.126 under FINAL; doc 18 §U), training has 0 half-cut cells (doc 18).

**T23. Thermal as a domain-invariant anchor (DADA-style alignment)**
- **Mechanism:** EL appearance varies by source (CSIR intensity sd 24 vs 34-48 for others; E: doc 02 §8); thermal physics may vary less (S). Align EL features of paired cells to thermal features across modules, as depth is used to adapt segmentation across domains.
- **Targets:** UR. **Data:** P. **Cost:** 5 / 15 / 0 / 0.
- **First experiment:** frozen-probe gate as T09.
- **Kill / success:** as T09.
- **Tags:** R: doi:10.1109/iccv.2019.00746 (DADA). E against: Om's A2 (instance-norm) was dropped because the style premise was contradicted on non-E1 data (doc 21 §7). Prior L.

**T24. Test-time per-module bias from thermal**
- **Mechanism:** on a new site with IR of the same modules, raise the inactive (and crack) bias in thermally anomalous cells, lower it in normal ones. Bias matters on E1: SKR2's E1 gain held at matched volume, and SUPPF's best constant E1 bias reached 0.4289 vs SKR2's 0.4567 (E: doc 21 §4.3); a per-cell signal is a non-constant bias (S). Inference-only.
- **Targets:** UR, IN, DE. **Data:** C (with masks to validate). **Cost:** 2 / 0 / as T01 / 0.
- **First experiment:** on captured modules: relF1@2 and inactive IoU with the thermal-driven bias vs b 0.
- **Kill / success:** kill if no gain over the best constant bias chosen on the same captured val split.
- **Tags:** E, S.

**T25. Temperature-normalised field EL**
- **Mechanism:** EL intensity depends on module temperature, and wrong IR temperatures caused up to 23% underestimation in EL-based series resistance (R abstract: doi:10.1016/j.solener.2024.112704). Normalise field EL by the module temperature from IR (or a thermocouple) before segmentation, to reduce cross-capture intensity shift.
- **Targets:** UR, DE. **Data:** C (same modules at two temperatures). **Cost:** 2 / 0 / 1 / 0.
- **First experiment:** EL of 3 modules at two temperatures; E-PF predictions with and without normalisation.
- **Kill / success:** kill if E-PF output changes by < 2% predicted px between temperatures (no problem to fix).
- **Tags:** R above; S.

### 2F. Industrial pipeline and deployment

**T26. Drone IR screening → targeted EL: a screening-recall table**
- **Mechanism:** drone IR runs at > 1 module/s (R abstract: doi:10.1088/2516-1083/ac890b); EL is slow (night, or daylight EL with bias). Screen with IR, image the flagged modules (plus a random audit sample) with EL, segment with E-PF. The thesis can measure what share of EL-visible damage the IR screen catches.
- **Targets:** DE, SV. **Data:** P (A3 is the best fit: drone IR + EL on modules with known induced defects; A1 / A2 indoor IR). **Cost:** 3 / 0 / 0 / 0 (CPU).
- **First experiment:** on A3 (and A1), rank modules by an IR anomaly score; share of E-PF-predicted inactive area and crack length in the top 10 / 20 / 30% of modules.
- **Kill / success:** kill if the top 20% hold ≤ 20% of predicted inactive area (no better than random); success ≥ 60%. Expect low recall for mode-A cracks (S; R: no hot spots for micro-cracks).
- **Tags:** R: doi:10.3390/en15062055 (aerial IR review); doi:10.1002/pip.3448 (module extraction from aerial IR video); doi:10.1109/jphotov.2020.2978068 (drone daylight EL, 120 fps, SNR 4.6 near one sun).

**T27. Hot-spot risk score from the EL segmentation**
- **Mechanism:** from E-PF's per-cell inactive fraction, crack mode and position, predict hot-spot risk; validate against paired IR. The worst hot spots sit at 40-60% shaded fraction (single cells shaded under a sun simulator, so its use for in-module inactive fraction is S, per `check`) and none above ~46% cracked (R abstracts: doi:10.1038/s41598-021-03498-z, doi:10.1038/s41598-022-16546-z), so risk is non-monotone in inactive area (S).
- **Targets:** SV, DE. **Data:** P. **Cost:** 2 / 0 / 0 / 0.
- **First experiment:** on A1 (and A2 forward-bias IR): AUROC of the risk score for IR-hot cells.
- **Kill / success:** kill if AUROC < 0.7.
- **Tags:** R above; reverse-bias thermography predicts in-module hot-spot temperature at the cell stage (R abstract: doi:10.1016/j.egypro.2014.08.097).

**T28. IR + EL time series: crack-to-inactive progression**
- **Mechanism:** frequent cheap drone IR plus occasional EL per module; a change in IR flags a re-EL. Cracks can reopen or close with load (R: doi:10.1038/srep04506), so a single EL snapshot may miss consequential cracks (S).
- **Targets:** SV, DE. **Data:** C (repeat visits). **Cost:** 3 / 0 / 2+ visits / 0.
- **First experiment:** WattCycle question: do they hold repeat drone IR of sites with one EL campaign?
- **Kill / success:** thesis-scale kill if no repeat data exists before submission.
- **Tags:** R, S. UVF also dates cracks (R: doi:10.1109/jphotov.2019.2961781, "chronological order", abstract).

**T29. One drone flight: IR + daylight EL / PL; segmenter robust to daylight EL**
- **Mechanism:** daylight EL and PL from drones exist (R: doi:10.1109/jphotov.2020.2978068; aerial PL doi:10.1002/pssr.202300059; inverter-switched daylight PL from an aircraft over a 149 MW plant, doi:10.1002/pip.3807). If WattCycle flies IR and daylight EL together, our segmenter must work at daylight-EL SNR (4.6 reported, R) with IR for triage and registration. Add an SNR-degradation augmentation (S).
- **Targets:** DE, UR. **Data:** P (datascout B2 passive EL / PL stacks, Zenodo 10.5281/zenodo.15020575), C. **Cost:** 4 / 11 / 2-3 / 0.
- **First experiment (CPU):** degrade val EL to SNR 4.6 with matched noise; E-PF val crack AP drop.
- **Kill / success:** if the drop is < 0.02 AP, no augmentation needed (idea closes as solved); if > 0.05, run the augmentation arm.
- **Tags:** R as above; S.

**T30. Inline EL + thermography → local loss maps (QAM-style)**
- **Mechanism:** inline cell testers already record EL and thermography; a weakly supervised model maps global I-V to local loss maps (R abstract: doi:10.1002/solr.202500253, EL + thermography + reflectance; finger interruptions lower fill factor locally). For WattCycle's power-loss arrow (out of scope now; E: doc 02 §9).
- **Targets:** SV. **Data:** C (factory). **Cost:** 8 / 10 / n/a / 0.
- **First experiment:** question for Om: does any partner have inline EL + thermography with I-V?
- **Kill / success:** kill if no such data.
- **Tags:** R above. Prior L for this thesis.

### 2G. Other modalities and physics links

**T31. EL / PL contrast → automatic inactive masks (no annotator)**
- **Mechanism:** isolated regions are dark in EL but still emit in PL at open circuit, and do not change when current is extracted; connected regions dim under extraction (S, device physics; R: a daylight-PL proof of concept is called "promising" for inactive areas, doi:10.1002/pip.3525; PL review doi:10.1016/j.egypro.2012.02.016). A ratio or difference image gives pixel-level inactive masks without humans. It also tells what scuff is: PL-dark (recombination) or PL-bright (current blocking) (S).
- **Targets:** IN (and SC, as a physics probe). **Data:** P (B1: A1's close-up EL + PL, 11 files, 2 modules; B2 Zenodo passive EL/PL stacks), C. **Cost:** 3 / 0 / 2-3 (PL needs a light source and filters, `capture`) / 0.
- **First experiment (CPU, ~0.2 GB with OK):** B1 EL / PL ratio map vs E-PF inactive prediction on the EL.
- **Kill / success:** kill if the ratio does not separate predicted-inactive from other dark EL (AUROC < 0.8); success → propose a 20-module EL + PL capture as an inactive ground-truth set for unseen modules.
- **Tags:** R, S as stated.

**T32. UVF crack lines → crack vs scuff labels**
- **Mechanism:** UVF shows cell cracks in aged modules (R: doi:10.1109/jphotov.2019.2961781; doi:10.1109/pvsc45281.2020.9300901) through the encapsulant, independent of EL texture (S). On modules with EL + UVF, an EL streak with a UVF line is a crack; without one it is a candidate scuff. That gives crack vs scuff labels, which the B3 scuff class lacked (B3 not learned, train scuff IoU 0.000; E: doc 11 row 42) and the B2 agent raters could not provide (scuff gate 1/8; E: doc 21 §8).
- **Targets:** SC, UR. **Data:** P (A1 has EL + UVF on 156 modules, but likely full-cell mono; S), C (WattCycle half-cut multi modules, UVF at night). **Cost:** 3 / 0 / 1-2 / 0.
- **First experiment:** 10 A1 modules: register UVF to EL; share of E-PF crack components with a UVF line within ~5 px; list EL streaks without one.
- **Kill / success:** kill if < 30% of clear EL cracks have a UVF line (too sparse to label); success ≥ 60%. Caveats (R): fresh cracks lack UVF; UVF patterns vary with module type and stress (doi:10.1109/pvsc45281.2020.9300901, abstract) and with encapsulant / backsheet type (doi:10.1002/solr.202400566).
- **Tags:** R, E, S as stated.

**T33. Multi-current EL (bias sweep) as an extra channel or label**
- **Mechanism:** regions limited by series resistance (behind cracks, broken fingers) change EL contrast with current differently from recombination-limited regions (material; scuff if recombination-type) (S; R: EL at 5 injection levels used for series resistance, doi:10.1016/j.solener.2024.112704; doi:10.1002/pssa.202000546). A second EL frame at low current is cheap in the field (S).
- **Targets:** SC, IN. **Data:** P (A1 sweep 0.01-1 × Isc, A2), C. **Cost:** 2 / 0 (test) or 11 (arm) / 1 / 0.
- **First experiment (CPU):** low / high current ratio maps on A1; do E-PF crack and inactive regions separate from dark texture?
- **Kill / success:** kill if AUROC < 0.75.
- **Tags:** R, S.

**T34. RGB photo: surface streaks and snail trails**
- **Mechanism:** a visible-light photo shows surface marks (S: a scuff, if surface) and snail trails, which correlate with cracks (R: doi:10.1109/jphotov.2014.2330495). An RGB channel or label could split "visible surface streak" from "invisible crack".
- **Targets:** SC. **Data:** C (phone photos; minutes per module); public probe first: C1 (doi:10.1016/j.dib.2026.113109), whose abrasion and scrape stages come with pixel-aligned EL and visible HDR images (R abstract). **Cost:** 2 / 0 / 0.5 / 0.
- **First experiment:** photograph 5 scuffed half-cut modules, register to EL, check whether scuff streaks are visible.
- **Kill / success:** kill if scuff is not visible in RGB.
- **Tags:** R, S. Visual faults (snail trail, burn marks, delamination) are detectable from RGB (R abstract: doi:10.1016/j.egyr.2022.10.427).

**T35. Ultrasound lock-in thermography as crack-only ground truth**
- **Mechanism:** ultrasound makes crack faces heat; it found cracks in wafers and cells, including optically invisible ones (R abstract: openalex:W2189012330). A surface scuff has no internal faces, so it should stay cold (S). A few cells imaged this way give crack vs scuff truth.
- **Targets:** SC. **Data:** C (lab). **Cost:** 2 / 0 / 2-5 / 0.
- **First experiment:** ask IIT Mandi whether any lab has lock-in thermography with an ultrasound or other active source.
- **Kill / success:** kill if no access, or if the method does not work through a laminate (S risk).
- **Tags:** R, S. Prior L.

**T36. Reverse-bias thermography for shunts and hot-spot-prone cells**
- **Mechanism:** reverse-bias thermography finds pre-breakdown sites and predicts hot-spot temperature (R abstracts: doi:10.1016/j.egypro.2014.08.097; doi:10.1109/pvsc.2008.4922478). Gives labels for shunt-like dark spots (part of our "dead cell" / "material") and a hot-spot risk target (T27).
- **Targets:** SV. **Data:** C. **Cost:** 2 / 3 / 1-2 / 0.
- **Kill / success:** kill for segmentation if shunt sites do not coincide with any of our EL classes.
- **Tags:** R, S. Prior L for segmentation.

### 2H. Data, benchmark and evaluation

**T37. Registered cell-level EL + IR + UVF benchmark from A1 (release)**
- **Mechanism:** register A1's EL, IR and UVF per module, crop cells, attach per-cell dark I-V, E-PF predictions and the physics weak labels (T12, T15, T31, T32). CC BY 4.0 allows a derivative with attribution (R: datascout A1). A first public, cell-registered EL + thermal + UVF set: a thesis contribution in its own right, and the substrate for T02, T06-T09, T12-T15, T26-T27.
- **Targets:** IN, DE. **Data:** P. **Cost:** 5 / 0 / 0 / 0 (CPU; E-PF CPU inference).
- **First experiment:** register 10 modules; report registration error (px) at cell corners.
- **Kill / success:** kill if registration error > 5% of a cell side after a homography.
- **Tags:** R: datascout A1; the IR review asks for public IR data sets (R abstract: doi:10.1088/2516-1083/ac890b). Licence reading to be checked by `check`.

**T38. UCF-EL ↔ FSEC IR / UVF link: labelled pairs for free**
- **Mechanism:** UCF-EL is Fioresi et al. 2022 (E: doc 02 §10), whose authors include D. J. Colvin (R: doi:10.1109/jphotov.2021.3131059), also an author of Li et al. 2024 on 10-year Florida modules (R: doi:10.1016/j.solener.2024.112704); csr6t is a UCF / FSEC Florida set (R: datascout A1). Same group, so overlap is plausible (S). If UCF-EL cells come from csr6t modules, UCF-EL masks (crack incl. "Crack_Isolated" ≈ inactive; E: doc 02 §10) label cells that have IR and UVF pairs.
- **Targets:** IN, UR. **Data:** P + our local UCF-EL. **Cost:** 1-2 / 0 / 0 / 0.
- **First experiment (CPU, done today, E; reproduced by `check`):** UCF-EL annotations hold 373 module ids (E: `~/mtp/datasets/UCF-EL-Defect/AnnotationsCombined.csv`). 201 have exactly 60 annotated cells, so they are not A1's 36-cell Shell M55 modules (S, datascout for 36). The other 172 are partial (109 with highest cell position ≤ 36), so an A1 link is not excluded for them. The FSEC UVF set (D3, 7,190 modules) and IR-visual set (D2, 1,898 pairs) may hold the 60-cell ones (S). Next: image correlation of A1 EL frames (≈ 0.15 GB for 10 modules) against the partial UCF-EL modules, or a question to the authors.
- **Kill / success:** kill if no A1, D2 or D3 module matches any UCF-EL module by normalised cross-correlation (as the BMRK = ELPV check, E: F04 §1b). Prior L-M; `synth` decides.
- **Tags:** E, R, S as stated.

**T39. Thermal-outcome-weighted evaluation (severity-aware metric)**
- **Mechanism:** weight segmentation errors by consequence: a missed crack in a thermally anomalous cell costs more than one in a normal cell. Gives WattCycle a task metric (E: doc 01 notes pixel IoU is a proxy no one uses directly).
- **Targets:** SV, DE. **Data:** P. **Cost:** 2 / 0 / 0 / 0.
- **First experiment:** on A1: share of E-PF's crack components that sit in thermally anomalous cells.
- **Kill / success:** kill if < 5% of components (weights would be degenerate).
- **Tags:** E, S.

**T40. Thermal-only pretraining of the EL encoder**
- **Mechanism:** pretrain on large IR sets (PVF-10, InfraredSolarModules, OSF 7v5zt) then fine-tune on EL.
- **Targets:** UR. **Data:** T. **Cost:** 3 / 10 / 0 / 0.
- **First experiment / kill:** frozen-probe gate as T09.
- **Tags:** E against: A8 KILL, P15 null, MIM n.d. (doc 21 §1; doc 00 fact 10; doc 11 rows 22, 25); IR crops are module-level (InfraredSolarModules 24 × 40 px, R: datascout D1). Prior L. Listed for completeness.

---

## 3. What thermal will not do (honest limits, to keep the ranking calibrated)
- **No direct fix for scuff + half-cut crack recall** (S with R): branch cracks that isolate nothing give no hot spot (doi:10.1038/s41598-021-03498-z, doi:10.1038/s41598-022-16546-z), and E1-like modules are absent from public pairs (section 1). The routes that can touch SC are UVF (T32), PL (T31), RGB (T34), multi-current EL (T33) and active thermography (T35), all physics labels for crack vs scuff, plus the T22 test that decides it.
- **No gain on BenchmarkEL test or E1 from thermal inputs**, since they have no thermal (E: doc 03); only EL-only models trained with paired data (2B, 2C) can move them, and each E1 read is a registered opening (E: doc 21 §9).
- **Pretraining routes start with a weak prior** (E: A8 KILL, MIM n.d., P15 null); they are listed with an A8-style cheap kill.
- **Cell-level, not pixel-level** (R web): drone IR is ~5 × 5 px per cell; indoor and lock-in IR are finer.

## 4. Questions for Om (to pass on; no outside contact made)
1. **Downloads:** may we fetch ~0.5 GB from OSF `ar76v` and `csr6t` (A2's IR + matching EL; 10 A1 modules; B1's EL + PL close-ups), plus optionally DTU A3 (0.64 GB), for G0, T26, T31, T32, T37? CPU only.
2. **CPU inference of E-PF** on those images: allowed, and on which machine?
3. **WattCycle** (capture asks whether it is the IIT Mandi recycling startup): do they have (a) drone IR of sites where EL was also taken; (b) half-cut multi modules with scuff streaks we could image (T22, T32, T34); (c) UVF or daylight EL / PL kit; (d) repeat IR visits (T28); (e) module temperature logs at EL capture (T25); (f) an EL rig for end-of-life sorting?
4. **IIT Mandi:** lock-in thermography (dark, illuminated, reverse bias, ultrasound), PL light source and filters, a UV lamp: which exist (T05, T31, T35, T36)? Capture found none in the central facility list (R via `capture/capture_plan.md` §1).
5. **For the FSEC / UCF-EL authors (later, by Om):** are UCF-EL cells cropped from modules in the FSEC IR (OSF 7v5zt) or UVF (OSF t8x9k) sets (T38)? Under what bias and current was the csr6t IR taken? Which camera and emissivity?
6. ~~Is Li et al. 2024 the paper for csr6t?~~ Answered by `check`: the OSF page names Colvin et al. 2023 (doi:10.1109/jphotov.2023.3238278); Li 2024 is a separate 9-module study.

## 5. Sources (all ids returned by the Research MCP this session unless marked web or datascout)
- Physics, EL vs thermal: doi:10.1038/s41598-021-03498-z; doi:10.1038/s41598-022-16546-z; doi:10.1109/jphotov.2020.3003781; doi:10.1016/j.solener.2024.112704; doi:10.1016/j.solener.2018.07.055; doi:10.1016/j.energy.2020.117930; doi:10.3901/jme.2021.08.098 (factory EL + electro-thermography fusion, detects "scratches, covers, cracks", abstract); doi:10.1016/j.seja.2023.100049; doi:10.1016/j.egypro.2014.08.097; doi:10.1109/pvsc.2008.4922478; doi:10.21611/qirt.2018.b; doi:10.1016/j.egypro.2013.07.263; doi:10.1016/j.egypro.2016.07.003; openalex:W2189012330; doi:10.1038/srep04506; doi:10.1016/j.solener.2020.08.058.
- Reviews: doi:10.1088/2516-1083/ac890b; doi:10.3390/en15062055; doi:10.1177/27533735241282603.
- PL, UVF, RGB, daylight EL: doi:10.1002/pip.3525; doi:10.1002/pip.3807; doi:10.1002/pssr.202300059; doi:10.1016/j.egypro.2012.02.016; doi:10.1002/pssa.202000546; doi:10.1109/jphotov.2019.2961781; doi:10.1109/pvsc45281.2020.9300901; doi:10.1002/solr.202400566; doi:10.1109/jphotov.2014.2330495; doi:10.1016/j.egyr.2022.10.427; doi:10.1109/jphotov.2020.2978068.
- A1 and C1 studies: doi:10.1109/jphotov.2023.3238278 (Colvin et al. 2023, the csr6t study); doi:10.1016/j.dib.2026.113109 (Polenghi et al. 2026, C1: pixel-aligned EL + NIR + visible HDR with abrasion, scrape, cut and crack stages and power, CC BY). JRC105705 (JRC 2017 report, via `check`, not in Research MCP).
- PV IR ML and data: doi:10.1051/epjpv/2025020 (DTU drone IR of 43 degraded modules, A3's paper); doi:10.1002/pip.3518; doi:10.1002/pip.3448; doi:10.1016/j.apenergy.2024.124187; doi:10.1038/s41598-026-67806-1; doi:10.3389/feart.2025.1702396; doi:10.1002/solr.202500253.
- EL datasets: doi:10.1109/jphotov.2021.3131059 (UCF-EL, Fioresi et al.).
- ML methods: doi:10.1109/cvpr.2016.309; doi:10.1109/tpami.2019.2929038; doi:10.1109/cvpr.2018.00926; doi:10.1109/tmm.2020.3035231; doi:10.1109/iccv.2019.00746; doi:10.1609/aaai.v35i3.16330; doi:10.1109/wacv57701.2024.00106; doi:10.1109/tpami.2024.3476487; doi:10.1007/978-3-031-19836-6_20; doi:10.1007/978-3-032-09513-8_55; doi:10.1007/978-3-030-58621-8_45; doi:10.1109/lgrs.2021.3109345; doi:10.1109/cvpr.2017.632; doi:10.1109/lra.2019.2904733; doi:10.1109/tcsvt.2023.3281419; doi:10.1109/icra57147.2024.10611200; doi:10.1016/j.inffus.2025.103572; doi:10.1016/j.compind.2021.103459; doi:10.1109/iccv.2017.211.
- Web (secondary, for drone IR resolution): the Sitemark page linked in §0.1 (Raptor Maps and FLIR dropped: their URLs now redirect to pages without the figure or to a 404, per `check`).
- Datasets: `datasets/dataset_table.md` v2 (datascout), rows A1-A3, B1, B2, C1, D1-D3. WattCycle facts: `capture/capture_plan.md` §1.1 (capture's R).
- Project files (E): `handbook/00`, `02`, `03`, `11` (rows 21, 22, 25, 42), `14` l.323, `17` §5.11, `18` §U, `20` l.71, `21` §1-9; `~/mtp/datasets/UCF-EL-Defect/AnnotationsCombined.csv`.
