# NOTES for ch10_deployment.tex (Chapter 10, "Towards deployment: severity and inference cost")

Written 23 Nov 2026. Read-only sources; nothing sealed was read (result text files, docs and tables only).
Short paths (relative to T = /home/yugma/mtp/research/team_2026-11-12_frontier; md5 prefix as read 23 Nov):
- SEV = results/severity/SEVERITY_SUMMARY.md (57e2bb4c). S0 = results/severity/S0_DOWNLOADS.md.
- IC = thesis/INFERENCE_COST.md (1e5a9002): CPU s3.3 (l58 to l67), GPU s3.4 (l70 to l85), wall time s4 (l87 to l112).
- TT = thesis/THESIS_TABLES.md (81c54378): T18 (l598 to l612), T22 (l729 to l745), T9 (l284 to l300), T10 (l304 to l320), T8 (l257), T20 (l650 to l678), T7a (l218 to l237).
- LIC = benchmark/release_v1/LICENCE_AUDIT.md (f267ea23). P10 = benchmark/PROTOCOL_v1.0.md (eeb3379a).
- RUL = log.md l363 ("22 Nov 12:49 (lead, user rulings)"). IST = benchmark/INFO_SHEET_TEMPLATE.md (97c3029e).
Chapter line numbers (lN) refer to ch10_deployment.tex as delivered (md5 in the final report).

## 1. Numbers, with sources
| ch | value | source | note |
|---|---|---|---|
| l19 | band 0 / under 1% / 1% or more | SEV:l6 | |
| l24 | MAE 0.12 pp over 532 cells | SEV:l12; TT:l606 | |
| l25 | bias -0.08 pp; 48 cells, about 1.25 pp (post hoc) | SEV:l12, l13 | |
| l26 | kappa 0.78; 0.5% threshold; sensitivity 0.73 | SEV:l14; TT:l606 | |
| l27 | false alarm 0.25%; CSIR sensitivity 0.20 | SEV:l14 | |
| l28 | 1% or more truly 1% or more in 93% | SEV:l15 | |
| l29 | E1 101 of 106 cells CSIR | P10:l53; TT:l88 | |
| l33 | F18 caption: 532 cells | SEV:l12 | caption only |
| l33 | F18 caption: 467 cells sit at (0, 0) | FIGURES_B.md l191 (b2c8d9fb); F18_data.csv (ea76bbf6), pool rows with a_gt_pct = 0 and a_pred_mean_pct = 0: 467 | caption only; added 23 Nov (TRACE_REPORT s4) |
| l41 | 84 cumulative damage stages; 2 panels | SEV:l19 | "polycrystalline": S0:l15 ("2 small poly devices") |
| l42 | about 50 W/m2; rho 0.56 | SEV:l19, l20 | |
| l43 | 0.65; 0.91; n = 2 | SEV:l20, l21 | |
| l47 | 137 module instances | SEV:l24 | CC BY version not stated: S0:l14 |
| l48 to l49 | rho 0.87 [0.80, 0.91] (129 modules); 0.89; 0.83 | SEV:l25, l26 | |
| l50 | rho 0.02 (near-clean type T1); 59 modules (T3) | SEV:l27, l28 | |
| l51 | 0.93 against 0.83, post hoc | SEV:l27 | |
| l55 to l56 | 24 non-diode modules; rho 0.64 [0.24, 0.87] | SEV:l31 | |
| l56 to l57 | 16 modules; 0.90 against 0.44 | SEV:l32 | |
| l58 | 9 of the 16 modules within about 0.8% of zero | SEV:l36 | |
| l62 | claim 21 | TT:l678 (T20 #21) | |
| l70 | rho 0.19; Delta R2 +0.10, interval -0.18 to +0.40 | SEV:l40, l41 | |
| l71 | 16 to 38 deg C; about 1 deg C | SEV:l42 | |
| l79 | 1 x 512 x 512 random tensors | IC:l10 | |
| l79 to l80 | Threadripper 7960X, 24 cores; 16 threads; batch 1 | IC:l12, l58 | |
| l80 to l81 | RTX A6000, fp32, TF32 off; batch 1 and 8; 200 timed cells | IC:l70, l81 | |
| l84 | PF 26.1 M, 148.0 GFLOPs per view; HRNet-W18 U-Net++ 20.8 M, 218.1 | IC:l31, l33 | IC:l20, l21 give 26,075,672 / 20,795,692 and 147.98 / 218.06 |
| l85 | per cell 148, 740, 1,184, 1,744, 8,722 GFLOPs | IC:l23; TT:l737 to l741 | |
| l85 to l86 | 8 x C1 in forwards, 11.8 x in FLOPs | IC:l24 | |
| l86 | CPU 0.216, 2.23, 3.88 s; 18.0 x C1 | IC:l61, l63, l64; TT:l737, l739, l740 | |
| l87 | GPU b1 0.0112, 0.0911, 0.174 s; 15.5 x C1; b8 0.133; views batched 0.134 | IC:l73, l75, l76, l77; TT:l737, l739, l740 | |
| l88 | HRNet view 2.3 x PF view (GPU), 1.9 x (CPU), 1.47 x FLOPs | IC:l84, l67 | |
| l89 | C2 peak GPU allocation 445 MiB (b1), 2,993 MiB (b8) | IC:l76; TT:l740 | torch max_memory_allocated, not process total (IC:l115) |
| l90 | C2 peak RSS 1,376 MiB (CPU, b1) | IC:l33 ("1376 / 4382"); P10:l258 ("1,376 MiB") | |
| l90 | about 20,700 cells per hour (GPU), about 930 (CPU) | IC:l76, l64 | marked S in IC (3600 / median) |
| l92 | about 100 s for 106 cells (one C2 seed, E1 jobs, with logp) | IC:l94, l85 | |
| l93 | 106 x 0.174 = 18 s; under a fifth | IC:l85 | IC's own S note, copied |
| l99 | F19 caption: seeds 5 to 9 | TT:l332 to l334 (T11a models column) | caption only |
| l100 | +0.0430 [+0.0013, +0.1043], CONFIRMED; 101 of 106 CSIR | TT:l265 (T8); P10:l28 | E1 scope sentence per OUTLINE s0 rule 3 |
| l101 | C2 - C1-D4 +0.0451 [+0.0173, +0.0699] | TT:l292 (T9) | ER item 2 wording |
| l102 | C1-D4 - C1 -0.0021 [-0.0423, +0.0575] | TT:l293 (T9) | |
| l102 to l103 | C3: 40 forwards, 8,722 GFLOPs; C2: 8, 1,744 | IC:l23; TT:l740, l741 | |
| l103 | C3 - C2 -0.0025 [-0.0254, +0.0157] | TT:l294 (T9) | |
| l104 | C2 seed 5 - C1 +0.0189 [-0.0403, +0.1068] | TT:l297 (T9) | |
| l105 | seed 5 designated before any number; about 0.17 s per cell | IST:l96; IC:l85 | |
| l107 | CS_D4 - CS +0.0055 [-0.0002, +0.0115], NOT CONFIRMED, NO LOSS, selection-biased | TT:l227 (T7a (b)) | |
| l113 | 50 BMRK cells; CC BY-NC-SA 4.0 | P10:l88; LIC:l32 | |
| l114 to l115 | likely extends to models; untested in law | LIC:l32 | S in LIC |
| l116 | BenchmarkEL: no licence file, citation asked; E-SCDD MIT, cannot clear BenchmarkEL | LIC:l27, l29 | |
| l117 | HRNet-W18 weights MIT | LIC:l37 | |
| l117 to l118 | SegFormer MiT-B2 non-commercial (research / evaluation) | LIC:l38 | |
| l120 | decision of 22 November: no commercial model on BMRK cells or MiT-B2 | RUL (log.md:l363, R8 "D4 (a)"); P10:l471 | |
| l121 | retrain without the 50 BMRK cells or holder's permission | LIC:l100 (D4 recommendation) | |
| l124 | E1 not zero-shot after opening #9 | P10:l126, l28 | |
| l131 | drone thermal at 600 W/m2 or more; EL at two currents | SEV:l56, l57 | |
| l133 to l134 | about 31 modules for a true rho of 0.5; about 90 for 0.3 | SEV:l62 | |
| l135 to l136 | primary: module sum of predicted inactive area vs relative Pmpp loss, within type, against crack length | SEV:l63 | |
| l136 | as of 4 November; EL rig 2 to 3 months away | SEV:l64 | |
| l137 | 62 half-cut cells; +0.0110 [-0.0289, +0.0722] | TT:l314 (T10); TT:l659 (T20 #2) | |

## 2. Judgement sentences kept (S), with their basis
1. l9 to l11 "A model that WattCycle could use for inspection needs more than a crack score ..." (S framing).
2. l29 to l31 "We note, as judgement, that E1 is 101 of 106 CSIR cells, so the source on which the output is weakest is the main source of E1." (S, this writer; numbers SEV:l14, P10:l53.)
3. l43 to l44 "With n = 2 devices and damage that only accumulates, this record cannot tell damage measures apart" (SEV:l21).
4. l44 to l45 "so the null is not evidence against inactive area" (SEV:l22).
5. l59 "We read it as borderline, on a selected subset." (SEV:l37).
6. l72 to l73 "Thermal is therefore a screen for diode and soiling faults ...; it is not a crack-severity measure." (SEV:l43).
7. l82 to l83 "host load can only slow a run, so the times are upper bounds for idle hardware" (IC:l82, S there for the GPU; this writer extends it to the CPU runs, whose host was also shared, IC:l13, l39).
8. l88 "so FLOPs understate HRNet's time on both devices" (S from IC:l67, l84 numbers).
9. l104 to l106 "Our judgement: since the ensemble adds nothing, the deployable unit is one C2 checkpoint (seed 5 ...) ... its expected gain rests on the recipe result." (S, this writer.)
10. l106 to l107 "Whether the eight D4 views ... earn their cost on new modules is not resolved by E1" (S, from the ER item 2 wording "The D4 part is not resolved on E1").
11. l114 to l115 "The licence audit judges that this likely extends to models trained on those images, a point untested in law." (S in LIC:l32.)
12. l116 "that claim cannot clear the BenchmarkEL images" (S in LIC:l29).
13. l120 to l122 "A model WattCycle could sell therefore needs ...; BenchmarkEL's own terms for commercial use stay unclear until its authors answer." (ruling + LIC:l100, l27.)
14. l122 to l124 "A retrained model is a new model: CV5 can describe it, but E1 is no longer a zero-shot set for us after opening #9, so its unseen-module quality would need new labelled data." (S, this writer; P10:l126.)
15. l130 to l136 pilot paragraph (SEV s6, tagged S there: "from the numbers above").
16. l137 to l138 "so a pilot on half-cut modules would also test the model" (S, this writer).

## 3. Scope and wording rules applied
- E1 sentence (l99 to l107) carries the scope: unseen modules supported, not proven; recipe averaged over seeds 5 to 9; OP-A only; 101 of 106 cells CSIR; carried by the full cells (OUTLINE s0 rule 3; G-W7).
- ER wording for D4 (G-W2): "Most of the gain is the model ... The D4 part is not resolved on E1".
- A6 / A7: one checkpoint n.d.; ensemble adds nothing (C3 cost given in forwards and GFLOPs, both copied; no ratio computed).
- A11: no watt figure or power band (l22 to l23, l63 to l64).
- G-N11 (no severity number for the final model) stated at l29 to l30.
- CV5 D4 increment labelled selection-biased (l107).

## 4. Placeholders
- \PENDING: 0. \CITE: 0.
- \FIG{F18} (severity, OUTLINE s4 F18) and \FIG{F19} (cost against quality, OUTLINE s4 F19; F19 was "pending (IC latency)" in OUTLINE, now unblocked by IC 1e5a9002).

## 5. Citations
- polenghi2026data (ch10_deployment.bib): dataset record as fetched, results on disk at /home/yugma/mtp/datasets/severity_public/polenghi/repository_record_mendeley_api.json
  (name PV_EL_HDR_BW_Test_DB, version 1, 7 contributors, DOI 10.17632/pxyzzkbs4b.1, published 2026-02-09); README.md there. The data
  paper (Data in Brief, doi:10.1016/j.dib.2026.113109, named in that README and in S0) is not cited because its title and authors were
  not verified.
- hoffmann2020elpvpower: Dataverse record on disk (/home/yugma/mtp/datasets/severity_public/elpvpower/repository_record_dataverse_api.json):
  title, 11 authors, DOI 10.26165/JUELICH-DATA/TVWUUP, version 1.3, first published 2020-08-28. The paper (Prog. Photovolt.
  doi:10.1002/pip.3416, arXiv 2009.14712) is not cited (title not verified).
- delpradosantamaria2025drone: paper of the DTU A3 data; DOI from results/severity/S4_DTU_THERMAL.md l11 and
  team_2026-11-04_thermal/datasets/dataset_table.md l16; title, 9 authors, EPJ Photovoltaics 16, article 31, 2025 from the Crossref API
  (fetched 23 Nov). The dataset itself (DTU figshare doi:10.11583/DTU.29665346.v1) has no verified author list on disk, so the chapter
  cites the paper; the lead may add a dataset entry.
- deitsch2019elpv, xie2021segformer: defined in ch06_protocol.bib (see its NOTES). wang2021hrnet: refs_extra.bib.

## 6. Things in OUTLINE (or the task) that turned out different
- OUTLINE 10.4 marks latency "pending (IC sections 3, 6; G-N7)"; IC 1e5a9002 has CPU and GPU and G-N7 is closed (GAPS l17).
- OUTLINE 10.1 status "final model: gap G-N11" still holds; stated in text.
- The task brief groups the SegFormer MiT-B2 licence with C2. C2 uses HRNet-W18 (MIT; LIC:l37, l100), not MiT-B2. C2 is research-only because of the ELPV (BMRK) cells; the chapter names MiT-B2 only as the SegFormer benchmark row's weights.
- Page budget: the chapter is about 2,000 words, about 4.4 pages at 450 words per page, slightly over the 4-page budget; the
  lead can drop the DTU limits sentence or the wall-time paragraph if needed.
