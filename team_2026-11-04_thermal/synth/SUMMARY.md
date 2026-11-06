# Thermal (IR) for our EL segmentation: summary for Om (4 Nov 2026)

Team `team_2026-11-04_thermal/`. This began as a desk study (no downloads, no GPU, no outside contact). Your approved public downloads (~1.2 GB, CPU only) started on 4 Nov at 12:43; there is still no GPU use and no outside contact. E = our files, R = source, S = judgement. All scores are S. Details: `synth/ranked_ideas.md`, `synth/top3.md`. Facts as corrected by `check/factcheck.md` passes 1-3. Status: final for Om (4 Nov), pending check's last pass. Sections 1-3 are the summary; section 4 is the question list to forward.

## 1. Your three questions

**(1) Public paired EL + thermal data?** Yes, at module level.
- Three open CC BY 4.0 sets have EL and IR of the same modules, about 215 modules in all (R: `datasets/dataset_table.md`, check D-24):
  - **A1** OSF csr6t: about 157 modules with dark forward-bias IR at ≈ 1 × Isc and EL at the same current, plus UVF, I-V and per-cell dark I-V. Paper: Colvin et al. 2023 IEEE JPV.
  - **A2** OSF ar76v: 15 modules with forward-bias IR at 5.289 A (one module, 408181737, at 5.089 A) and EL at the same current.
  - **A3** DTU: 43 modules (31 artificially degraded, 12 soiled, per the DTU slides; small per class, e.g. 8 cracked and 8 disconnected modules); drone IR (Mavic 3T) + EL at 100% and 10% Isc + I-V; 642.6 MB.
- None has masks or pixel registration. Cell-level alignment by homography looks feasible (S).
- Half-cut and scuff: A1 / A2 are full-cell mono Al-BSF (R). A3 has bifacial PERC half-cut modules in its shorted-diode, glass-crack and soiling groups, but none in its crack group (R: DTU slides, check pass 3). No set is known to show scuff (S).
- Also found: 3 EL + PL sets and 2 PL-only pools; 4 EL + visible / NIR sets, of which only one (Polenghi C1) pairs images of the same cell; 12 thermal-only sets; 12 in-paper sets.

**(2) How thermal could help.** 40 ideas + 14 drone-only ideas + 7 from datascout and capture; 58 rows after merging (`synth/ranked_ideas.md`).
- The physics sets the role. Thermal sees disconnected / inactive areas, hot spots and shunts. It does not see cracks that isolate nothing (R: Dhimish 2021 / 2022; DTU EPJ PV 2025). It likely does not see scuff either (S). Dark IR gives little sub-cell detail (R: JRC 2017), so expect cell-level signals.
- Best uses:
  - IR screening, then EL for detail;
  - severity / hot-spot risk;
  - physics weak labels for inactive;
  - a scuff-vs-crack arbiter with UVF.
- Weak uses: a crack-pixel input, or pretraining (E: A8 KILL, MIM n.d., P15 null).

**(3) Can WattCycle / IIT Mandi capture paired EL + IR?** Not soon, but useful work can start now (`capture/replan_pick2.md`, `ideas/drone_only.md`).
- **Now:** WattCycle (confirmed by you) has drone thermal only, and its EL rig is 2-3 months away.
- **What the drone can do:** drone IR cannot see our crack lines (cracked cells differ by about 1 °C at most; R: DTU 2025). It does see disconnections (≥ 600 W/m2), diodes and soiling, so it is for triage and pairing: a module ID map with a half-cut survey, physics-rule scores, and a frozen list of the modules the first EL session will image, with our predictions. Ground tests on end-of-life modules need no EL: IR under load vs open circuit (inactive candidates), and a UV torch at night (crack lines).
- **EL sooner (S):** a Raspberry Pi HQ camera with its IR-cut filter removed, plus the 300 W supply, costs about ₹25k plus lens and filter. A bench test in week 2 decides whether it works (Si sensitivity near 1,150 nm is unconfirmed). A first EL night is possible in weeks 3-4 (18 Nov-1 Dec), and the session on the pre-registered modules in weeks 4-5. Other options: borrow a modified camera at IIT Mandi if one exists (free; weeks 2-3); a fallback camera at ₹62k (R; weeks 4-5); NISE Gurugram per-module EL + STC I-V (fee not public; R). WattCycle's own rig: about Jan-Feb 2027 (S).
- **Not within 4 weeks (S):** a converted DSLR, drone EL (needs a ~€10k-15k SWIR camera), IIT Bombay. With any EL camera, the paired P0 day (5-6 modules, EL + dark IR + UVF + RGB) still holds (`capture/capture_plan.md`).
- **IIT Mandi:** the central facility lists no IR camera or EL rig (R). NIT Hamirpur lists teaching kits only (R).

## 2. Top 3

| # | What | Data / cost | First signal | Kill if |
|---|---|---|---|---|
| 1 | **What thermal catches:** IR screening vs EL on A3 / A2 / A1. Screening-recall table by defect mode; hot-spot risk from E-PF maps (T26, G0, T27, T39) | public, ~1.2 GB (approved); ~6-7 dev d CPU; 0 GPU | 2-3 days | top 20% IR-ranked modules hold ≤ 20% of predicted inactive area; G0 \|ρ\| < 0.3 and AUROC < 0.7 |
| 2 | **WattCycle drone thermal now, low-cost EL soon** (re-planned after your 4 Nov decision): one visit day, frozen EL queue, ground tests, then the Pi EL camera feeds the scuff arbiter if its bench test passes (W02, W03, W01, W08, W11; X6 → X1 / X2) | 1 visit day + 1 night; ~8-10 dev d; ~₹27k-30k kit (X6 + UV torch) | bench test W2; visit day W2-3; EL on the pre-registered modules W4-5 (S) | module re-ID < 90%; no UVF lines on aged modules; X6 cracks not visible at ≤ 120 s stacked |
| 3 | **Inactive from physics labels:** A1's EL-derived per-cell voltage at ~3.393 A (deficit vs module median) + IR ΔT as cell labels; mixed-supervision arm only if gated; registered A1 cell set as a thesis output (T15, T02, T12, T37) | same download; ~9-10 dev d; ~5.5 GPU-h in W4-5 if gated | 1-2 days (T15) | valid cells < 50%, or no spread (`pick3/plan_pick3.md` §3.1); < 50 flagged cells or purity < 70% |

- Pick 1 is the cheapest sure result, for the deployment chapter.
- Pick 2 serves deployment now. It reaches scuff + half-cut (75% of missed E1 crack px, E) only through UV crack lines, or through the scuff arbiter if the low-cost EL camera works. It gives labels, not an E1 gain, inside 7 weeks (S).
- Pick 3 targets the small-inactive problem.

## 3. Decisions
**Decided by you (4 Nov, `om_2026-11-04_decisions.md`)**
- Downloads for picks 1 + 3 approved, CPU only: 1.19 GB (A3 0.64, A2 0.25, A1 0.29 GB, dark I-V 3.8 MB; R via check). datascout downloads and runs pick 1; ideas runs pick 3.
- WattCycle is confirmed as WattCycle Sustainable Solutions. It has drone thermal only, and its EL rig is 2-3 months away. Pick 2 is re-planned (section 2).

**Still open for you**
1. **E-PF inference location:** gaint CPU (as PF2E did; E: `handbook/14` l.419) or a local copy of the 5 checkpoints? Held until you choose, so picks 1 and 3 start on an EL threshold.
2. **Licences / release:**
   - May we mix the CC BY 4.0 sets with BenchmarkEL (no licence file, E) in the thesis?
   - May we release a registered A1 cell set (T37) as a CC BY derivative? CC BY 4.0 allows an adapted release with credit, a licence link and a note of changes (R, check S-26). Caveat: E-PF is trained on BenchmarkEL, which has no licence file (E), so E-PF predictions inside a release carry that question.
   - On what terms may WattCycle images be used and released?
3. **Capture funding (pick 2):** who pays for the low-cost EL kit (about ₹25k + lens and filter), the UV torch (₹1.8k-4.5k), and optionally the ₹62k fallback camera, NISE fees and a ~₹20k-30k phone IR camera? WattCycle, the lab, or you?

**Later asks (no decision needed today)**
- A1 extension (not approved; ideas proposes it in steps):
  1. A1's whole IR folder, 157 modules, 0.26 GB (R), for fleet-level thermal statistics and T12's real flag counts.
  2. The remaining A1 EL, about 2 GB, only if the 10-module step shows a signal.
  - Other sizes: 30 more modules (EL + IR) ≈ 0.48 GB; everything at one bias with UVF ≈ 4.5 GB (R, check S-5 / S-6).
- Drone-IR training sets for W04 (not approved): D1, PVF-10, D2, and D11 (Indian-plant drone thermal, about 19 GB, R via check).
- GPU: about 5.5 GPU-h for pick 3's arm in W4-5 if gated; about 3 GPU-h for pick 1's T08.
- Optional labels: about 2-5 h per 100 WattCycle cells for a scored unseen-module set (S); the user's call.
- Optional downloads: A1 close-up EL + PL, 0.11 GB (R); Polenghi EL + visible, about 1.13 GB (R), a public scuff probe.

## 4. Questions to send (capture's Q1-Q20, `capture/replan_pick2.md` v1.2 §4; it absorbs ideas' 8 drone questions and the old list; no contact made)
**WattCycle: drone and camera**
- Q1. Drone and thermal camera model and firmware. Is radiometric R-JPEG on, and are raw R-JPEGs kept (not only palette JPEGs / Atlas outputs)? Emissivity and distance settings?
- Q2. RGB on the drone? Any NIR or multispectral camera?
- Q3. Usual altitude / GSD and overlap. Can you fly a ~10 m pass over chosen rows, 6-8 m hovers over ~20 flagged modules, and a repeat pass 30-60 min later?

**WattCycle: flights and sites**
- Q4. Which sites, how often, since when? How many past flights are archived?
- Q5. Module types per site: make / model, full vs **half-cut**, mono / multi, cells per module, age.
- Q6. Per flight: plane-of-array irradiance (pyranometer or SCADA), wind and plant state logged? Flight logs kept?
- Q7. A handheld or phone thermal camera, or can the drone's camera be used on the ground (props off)?
- Q8. Do you follow up flagged anomalies (replacement, I-V, contractor EL, warranty)? Records usable as labels?
- Q9. Can modules be re-identified across flights (string maps, orthomosaics, serial lists)?

**WattCycle: end-of-life modules (ReVive)**
- Q10. How many end-of-life modules are on site, of which types and ages? Any half-cut?
- Q11. May we test some in sun (open circuit / load / short circuit), shade single cells on 2-3 sacrificial ones, and image them at night with a UV torch and a low-cost EL camera?
- Q12. A dark shed or room and a module rack? Mains power for a 300 W supply at night?

**WattCycle: EL**
- Q13. Which EL rig is coming, from whom, when? May we suggest a spec (≥ 0.3-0.45 mm/px, 16-bit raw, 850 nm long-pass, 0.1-1.0 × Isc control)?
- Q14. Would you try the ~₹25k low-cost EL camera with us before the rig arrives?
- Q15. Any DC supply (V, A, W)? Who supervises the electrical work, and is there an SOP for energising used modules?
- Q16. Could 3-5 modules go to NISE Gurugram for EL + STC I-V? Who pays fees and freight?

**WattCycle: people, data, money**
- Q17. A contact for flights and for ground tests.
- Q18. Data terms: may the thesis and a paper use the IR, UVF and EL images? May a derived dataset be released, and under what licence?
- Q19. Funding: low-cost EL kit (~₹25k + lens and filter), the ₹62k fallback camera, NISE fees, UV torch, optional phone IR (~₹20k-30k).

**IIT Mandi, or you directly**
- Q20. Does anyone at IIT Mandi own an astro-modified or full-spectrum camera, a ZWO-type mono camera, a handheld IR camera, or a ≥ 60 V / ≥ 10 A supply we could borrow? Do NISE's EL fees apply to research customers, and what is the turnaround?

**Dataset authors (later, your call)**
- U1. UCF (csr6t / ar76v): IR camera, emissivity and raw txt format; overlap with UCF-EL (the cell count does not exclude it); are Li et al. 2024's AZ modules released?
- U2. DTU (A3): EL camera and resolution, cell layout per module type, per-cell crack locations, any lab forward-bias IR. (Technology, EL currents and the drone are already in the slides.)
- U3. NREL: DLIT + EL + PL of the half-cut module (PVSC 2023); new home of the DuraMAT PL sets.
