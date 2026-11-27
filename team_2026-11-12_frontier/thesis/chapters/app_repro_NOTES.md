# app_repro NOTES: sources for every number and dated fact in `app_repro.tex`

Writer id `repro`, 27 Nov 2026. All paths are on the laptop copy of the research repo, root `/home/yugma/mtp/research/` (abbreviated `R/`), unless marked. Line numbers are `cat -n` lines at the time of writing. Quotes are copied; "…" marks a cut.

## Source key

| Key | Path |
|---|---|
| PH | `R/handbook/sources/chat/phase0_phase1_handoffs_pasted_2026-10-11.md` (phase 0 doc l.9–87; phase 1 doc l.89–473; phase 1 author's answers l.481–528) |
| HO | `R/handbook/sources/MTP_session_handoff_2026-10-07.md` (snapshot 7 Oct ~22:15 IST) |
| D1 | `R/handbook/sources/old_era_reports/gaint__day1.md` (copy of the single-GPU machine's `reports/day1.md`) |
| CV | `R/handbook/sources/old_era_reports/cv02__el_results_cv02.md` (copy of the eight-GPU machine's report) |
| ST | `R/handbook/sources/old_era_reports/gaint__stats_tests.md` |
| SU | `R/handbook/sources/old_era_reports/gaint__summary.md`; SC = `.../gaint__setup_check.md` |
| FV | `.../gaint__fit_vs_generalise.md`; PD = `.../gaint__precision_diagnostic.md` |
| PM | `R/analysis/papers_metrics.md` |
| AA | `R/analysis/alhvr_audit.md` |
| P1 | `R/results/p1/README.md`; P2 = `R/results/p2/README.md` |
| P19 | `R/results/p19/README.md`; P19c = `R/results/p19/p19_compare.txt` |
| SE | `R/results/seipv_compare/README.md` |
| PC | `R/results/pratt_compare/README.md` |
| SR | `R/to_human/situation_report_2026-10-08.md` |
| DL | `R/handbook/12_decisions_log.md` |
| H06 | `R/handbook/06_history_phase0_phase1.md` |
| UM | `R/handbook/sources/chat/user_messages_2026-10-07_to_11.md` |
| A04 | `R/literature/notes/A04_jha2025_pvs3.md`; F05 = `R/literature/notes/F05_institutional_pdfs.md` |
| TT | thesis working copy `thesis_tables.tex` (for cross-references only) |
| GIT | `git log` of `R/` |

Machine naming (no host names in the .tex): "single-GPU institute server (the second machine of later chapters)" = gaint (RTX PRO 4500, PH l.132); "shared eight-GPU server (the training machine of later chapters)" = cv02 (8x RTX A6000, PH l.140). Mapping to later-chapter names: TT l.873 row P15 says "second machine" and P15 ran on gaint (`R/handbook/10_experiments_P13_P16_E1.md` l.22 "P15 | done (6 runs, gaint)"); TT l.877 row AL1 says "training machine" and AL1 ran on cv02 (`R/team_2026-10-21/alhvr/results.md` l.6 "cv02 `/tmp/noob_el/el_alhvr`").

---

## Opening and "Conditions of every old-era number"

| .tex fact | Source | Quote |
|---|---|---|
| reproductions that ran later: 13 and 14 Oct | SE l.1; PC l.1; P19 l.3 | "(13 Oct 2026, descriptive…)"; "(descriptive, 13 Oct 2026)"; "locked 14 Oct before any run" |
| original `20211104` masks | HO l.108 | "`dataset_20211104` … **the one we use.**" |
| U-Net++ from scratch | HO l.177 | "plain U-Net++, 4,981,368 parameters, trained from scratch (no pretraining)" |
| class-weighted CE, labelled batch 4 | H06 l.7 | "original BenchmarkEL masks, from-scratch U-Net++, weighted CE, labelled batch 4 unless stated, SemiCE for Mean Teacher" |
| cosine to zero; 20,000 steps; final step | HO l.175–176; l.269 | "cosine decay **to zero**"; "All BenchmarkEL numbers: final step, 20,000 steps, split seed 0, standard convention, test = 50 images" |
| test scored in every run, primary readout | HO l.178 | "**final-step test is primary.**" |
| 24 of 50 test cells from modules with train cells (as counted then) | HO l.123 | "20 of 54 val images and 24 of 50 test images come from modules that also have train images." |
| later audit: 8 test cells = same physical cell as a pool cell | thesis ch03_related.tex l.106 (working copy) | "8 of its cells are the same physical cell as a cell of the training pool" |
| class weights over all 582 cells incl. test | SU l.22 | "class frequencies hard-coded in `class_info.py` match all 582 images (train+val+test) to 5e-7" |
| phase 0 numbers from notes, never re-verified | PH l.92 | "Numbers come from CC … reports pasted into chat and from the poster. They are not re-verified against files." |

## Section "The project start and phase 0"

| .tex fact | Source | Quote |
|---|---|---|
| industry partner wants detect / grade severity / estimate power loss; advisor wants a paper with ~2M-param model | PH l.13 | "Mandate: WattCycle wants detect, grade severity, estimate power loss. Your advisor wants a paper with a ~2M-param model." (partner name replaced by "the industry partner") |
| about 4M on the poster | PH l.115 | "lightweight model (~2M params in memory, ~4M on the poster)" |
| 582 labelled, ~12k unlabelled, 512x512, 24 classes | PH l.12 | "BenchmarkELimages (582 labeled, ~12k unlabeled, 512x512, 24 classes), plus UCF-EL." |
| SA U-Net++ ported to PyTorch, MT + SemiCE | PH l.14 | "Core model: SA U-Net++ ported to PyTorch, Mean Teacher + SemiCE." |
| SemiCE named after PV-S3 | PH l.493 (answers item 2) | "Jha et al.'s PV-S3 describes SemiCE as cross-entropy on pseudo-labels with two thresholds" |
| SA block = sigmoid(Q+K)*V, elementwise gate | PH l.46 | "The SA block is `sigmoid(Q+K)*V`, an elementwise gate, not dot-product attention" |
| 4,589,880 params; gate blocks 88,000 (1.9%) | PH l.48–49 | "SA U-Net++: 4,589,880"; "SA blocks: 88,000 (1.9%)" |
| defect mIoU headline; gridline excluded as noisy | PH l.18 | "Defect mIoU (crack + inactive) is the headline metric. Gridline (class 15) is noisy and excluded." |
| ablation 0.2028 vs 0.1792; SSL sweep 0.2580 (20%), 0.1323 (10%); invalid, predate GaussNoise fix | PH l.17 | "Old SA ablation ("removing SA helps", 0.2028 vs 0.1792) and the SSL sweep (20%: 0.2580, 10%: 0.1323) are **invalid**. They predate the GaussNoise fix (albumentations 2.x ignored `var_limit`, noise erased cracks)." |
| sigma ~68 instead of ~4 on 0–255 | PH l.264 | "Measured sigma ~68 instead of ~4 (0-255). Erases cracks." |
| +7.4 from 8x step mismatch; standing rule | PH l.19; DL l.109 (H3) | "An 8x step mismatch fake-produced a +7.4 gain."; "Match optimiser steps between SSL and SL … kept as a standing rule" |
| class weights ~310:1 | PH l.22 | "Class weights: sqrt-inverse-frequency (~310:1), not raw (98,000:1)." |
| later found computed over train+val+test | H06 l.86 | "Later found computed over train + val + test (a leak; see §6)" |
| 11 Oct recollection; table of SA-SL-20 seed 0: final 0.338, best-val 0.301; relayed 4 Oct | PH l.485–486 | "a misreading of a table I relayed on Oct 4: That table listed **SA SL-20% seed 0** only: final-step test 0.338, best-val-step test 0.301. Both numbers belong to one arm" |
| "checkpoint artefact" (our reading) | H06 l.388 | "The old SA "gain" was a checkpoint artefact (one arm at final vs best-val), not an SA effect." |
| four papers reproduced in phase 0 | HO l.21 | "Paper reproductions were done before this session (Fioresi, Pratt, Jha PV-S3, Gangopadhyay). All of that code was lost" |
| poster course EE511 Computer Vision; title | PH l.361 | "Title: "Label-Efficient Segmentation of Rare Defects in Electroluminescence Images of Solar Cells". … EE511" (author and supervisor names omitted per brief) |
| "SSL doubles performance 10.83 to 21.19" invalid | PH l.224 | "early claim "SSL doubles performance 10.83 to 21.19" is invalid (both runs undertrained)" |
| poster panels (a), (b) M1–M3, (c) | PH l.338–340 | "(a) Backbone: ~4M-param U-Net, pretrained light encoder …, **full-resolution skip** … for 2 px cracks"; "(b) SSL (ALHVR-inspired): M1 defect-aware sampling …; M2 per-class confidence thresholds gamma_k …; M3 EMA prototype memory"; "(c) Severity grading" |
| presenting line; "(8.8)" | PH l.364 | "Presenting line: "At equal compute, SSL (our reimplementation, one seed then three) showed no gain; Jha's published SL baseline (8.8) is undertrained; his code ignores background."" |
| outdated items (i)–(vii); 0.491 ± 0.009 | PH l.363 | "(i) Fig. 3 caption cites CPS: wrong, ALHVR has no CPS term; (ii) M3 prototype memory is dead; (iii) new step-matched number 0.491 +- 0.009 (3 seeds) in new code; (iv) Jha released-code finding; (v) Gangopadhyay row; (vi) crack-width claim wording; (vii) numbers moved to final-step new-pipeline values." |
| "by 6 Oct" | PH l.92 | "Status snapshot inside this doc = **00:04 IST, Tue Oct 6 2026**" |

### Table `tab:repro-poster` (all from PH l.213–221, "Records from the first (lost) pipeline, used on the poster")

| Row | Quote |
|---|---|
| Fioresi 48.15 / 57.30 vs 50.21 / 59.42 | l.215 "Fioresi FSL 4-class / 5-class \| 48.15 / 57.30 \| 50.21 / 59.42" |
| Pratt rule B 13.33–16.00 vs 15.01; A 29.22, C 26.87 | l.216 "Pratt U-Net (rule B) \| 13.33-16.00 \| 15.01 \| rule A 29.22, C 26.87" |
| Jha SL 20% 30 ep 8.76 vs 13.13 / 10.83 | l.217 |
| Jha SL 20% 12.0k: 56.61 / 39.00 | l.218 |
| Jha SSL 20% 95.7k: 67.00 vs 58.85 / 46.40 | l.219 |
| SL 20% step-matched 95.8k: 60.79 / 48.90 "beats SSL" | l.220 |
| FSL 100% 59.8k: 70.84 vs 65.84 / 50.21 | l.221 |
| "not reproduced in phase 1" (46.40) | D1 l.670 "the earlier PV-S3 implementation (your records: **46.4 standard**) is not reproduced by v1 (0.200) or v2 (0.276, 0.283)" |
| 5-class includes background | PH l.184 "Fioresi 5-class \| same but includes background class" |

Note: PH l.213 header "| baseline | published | ours | note |" gives no unit; the values are percent-scale (e.g. 8.76 = Jha's 8.76%), so the caption labels them percent.

### Severity idea, reset

| .tex fact | Source | Quote |
|---|---|---|
| components, border flag, skeleton length/width/tortuosity, topology mask, busbar test | PH l.340; PH l.58 | "crack skeleton via `skan` (length, medial-axis width, tortuosity), electrical isolation via topology mask (crack pixels as walls, flag components not touching a busbar)"; "Per-class connected components, `regionprops`, boundary-truncation flag, skeleton length, isolation detection, mm calibration" |
| topology mask {1,2,3,4,9} | PH l.23 | "Topology mask for Subpath A: `{1,2,3,4,9}`, so busbars and ribbons don't create fake isolated gaps." |
| Köntges modes A/B/C definitions; Cohen's kappa | PH l.340 | "**Kontges modes**: A crack with no isolated area; B isolated area still glowing; C isolated area dark/inactive. Grade agreement (accuracy, confusion matrix, Cohen's kappa, GT masks vs predicted masks)" |
| power loss tracks isolated (C) area; no paired I-V | PH l.42 | "No paired I-V data, so power loss relies on published correlations. Köntges A/B/C: power loss tracks **isolated (Type C) area**, not total crack pixels." |
| 57 unit tests (instances) | PH l.340 | "instances (`src/postprocess/instances.py`, 57 tests, lost)" |
| compression plan: prune to ~2M, INT8 + TensorRT, Jetson; never executed | PH l.54, l.64; H06 l.99 | "Jetson has no FP8. Use INT8 + TensorRT."; "Torch-Pruning to ~2M."; "Plans (not executed; code lost)" |
| reset before 2 Oct; lost items | PH l.32; H06 l.55 | "The `noob` user on gaint was reset. Reproduction code, UCF val split, Subpath A code (57 tests), label splits and predictions are gone."; "Before 2 Oct \| **The `noob` user on gaint was reset.**" |
| repo two months stale; September unrecoverable | HO l.224 | "Found the GitHub repo was two months stale. Everything from September was unrecoverable." |

## Section "Phase 1: the rebuild"

| .tex fact | Source | Quote |
|---|---|---|
| 2 Oct server empty; datasets and ALHVR ref cloned | HO l.223 | "Found gaint empty after the reset. Cloned the public datasets and the ALHVR reference by exec." |
| 11,993 cells downloaded | HO l.138 | "Downloaded: 11,993, seed 42" |
| colour masks; 24.6% ignore | SU l.21 | "the loader expects colour masks. Symlinked as they are, every class except background becomes "ignore" (24.6% of pixels)." |
| 615:1 not 313:1 | SU l.22 | "Recomputed on train only, the weight ratio is 615:1, not 313:1." |
| missing split trains on all 582 incl. test | SU l.23 | "if a split file is missing, `train.py` trains on every image in the folder, test set included." |
| noise 10–15x stronger | SC l.59 | "**So the noise is about 10–15× stronger than intended, on 30 % of samples.**" |
| 96 tests | HO l.226 | "foundation rebuilt in the new repo, 96 tests, pushed." |
| foundation pieces (index masks, split error, weights train-only, weight 0 absent, conventions) | HO l.168–169, l.171, l.174 | "read index masks directly"; "a missing split file is a hard error"; "computed at start from the labelled subset in use, train only. … weight 0 for absent classes"; "three conventions: `standard`, `pvs3` …, `pratt_median`" |
| 4,981,368 params | HO l.177 | as above |
| Adam 1e-3, cosine to zero, 20,000 steps | HO l.175–176 | "Adam, lr 1e-3 … cosine decay **to zero**"; "20,000 steps" |
| best-val on 54 cells flips signs | HO l.178 | "val has 54 images and best-val selection flips the sign of several comparisons" |
| coupled augmentations fixed 3 Oct; pilots kept apart | HO l.186 | "flips always fired together and blur and noise always fired together \| fixed Oct 3. **All "pilot" runs of Oct 2 used the coupled augmentation and are kept in a separate table**" |
| shutdown 21:34 on 2 Oct, ALHVR pilot step 13,600 | HO l.60 | "Oct 2, 21:34 \| orderly OS shutdown, killed the ALHVR pilot at step 13,600." |
| reboots 6 and 7 Oct killed runs | HO l.61, l.257, l.261 | "Oct 6, about 18:22 to 18:47 \| reboot, killed two low-label runs at step 12,500"; "Gaint rebooted and lost its queue."; "Gaint rebooted again. Resume-after-reboot added." |
| resume tested bit-exact | PH l.274 | "Resume: tested bit-exact for all 7 trainers" |
| eight-GPU server from 4 Oct | HO l.241 | "cv02 set up as a second machine." (under "Oct 4 (Sun)") |
| MT: EMA 0.999, λ 1.5 by step 4,000, SemiCE, teacher evaluated | HO l.196 | "EMA 0.999, λ 1.5 after 2,000 warm-up + 2,000 ramp steps, SemiCE consistency …, **EMA teacher is evaluated**" |
| 4 labelled + 4 unlabelled | HO l.228 | "labelled batch 4 in every method (SL 4, SSL 4 + 4)" |
| ALHVR port: two networks, two optimisers, clean + perturbed, follows code | HO l.197 | "two networks, two optimisers, no EMA, each with a clean and a perturbed decoder pass. Follows the reference **code**" |
| λmax 0.1 ramped over whole run | HO l.215 | "λ(t) = 0.1 · sigmoid ramp over the whole run." |
| 95 labelled cells; 383 unlabelled | PH l.173; HO l.134 | "**20% subset (seed 0): 95 labelled images**"; "the rest of the 478 train images, labels hidden (383 at 20%, 431 at 10%)" |
| MT λ=0 0.3653 ± 0.0183 vs MT 0.3648 ± 0.0071; paired −0.000 ± 0.024; teacher − student +0.000 ± 0.002 | HO l.306–307, l.311–312; CV l.53–54 | "MT-20 \| 0, 1, 2 \| … → 0.3648 ± 0.0071"; "MT-20, λ = 0 \| … → 0.3653 ± 0.0183"; "MT paired (λ 1.5 minus λ 0, teacher): −0.000 ± 0.024."; "MT teacher minus student at the final step: +0.000 ± 0.002. The EMA adds nothing because the learning rate ends at zero." |
| unlabelled images still forwarded | HO l.314 | "In both controls the unlabelled images still pass through the network" |
| ALHVR λ=0 0.3642; paired +0.005 ± 0.023 | HO l.309, l.313 | "ALHVR-20, unlabelled weight 0 \| 1, 2, 3 \| 0.3757, 0.3708, 0.3461 → 0.3642 ± 0.016"; "ALHVR paired (on minus off): −0.016, −0.000, +0.030 → **+0.005 ± 0.023**." |
| reading at the time; BN hypothesis not shown | H06 l.202 | "**Reading at the time:** the SSL arms' gain over SL-20 did not come from their unlabelled losses. The leading hypothesis was BatchNorm batch composition ("4 + 4"). It was not shown in phase 1." |
| n.d. labels on loss-off controls | derived: the ± sd (3 paired seeds) spans 0 (−0.000 ± 0.024; +0.005 ± 0.023), so not detectable; no rule was fixed in advance |

### Table `tab:repro-phase1`

| Row | Source | Quote |
|---|---|---|
| SL-20 8, 0.3435 ± 0.0329 | HO l.275 | "SL-20 \| 8 (3 + 5) \| 0.3435 ± 0.0329" |
| SL-100 4, 0.3383 ± 0.0060; Δ −0.0052 [−0.0330, +0.0226] | HO l.276; ST l.23 | "SL-100 vs SL-20 \| test (50 images) \| … \| -0.0052 [-0.0330, +0.0226]" |
| MT-20 6, 0.3662 ± 0.0061; Δ +0.0227 [−0.0050, +0.0504] | HO l.277; ST l.15 | "MT-20 vs SL-20 \| test … \| +0.0227 [-0.0050, +0.0504] … 0.095" |
| ALHVR-20 6, 0.3724 ± 0.0103; Δ +0.0289 [+0.0007, +0.0570] | HO l.278; ST l.11 | "ALHVR-20 vs SL-20 \| test … \| +0.0289 [+0.0007, +0.0570] … 0.045" |
| SA-SL-20 4, 0.3399 ± 0.0104; Δ −0.0036 [−0.0324, +0.0251] | HO l.279; ST l.27 | "SA-SL-20 vs SL-20 \| test … \| -0.0036 [-0.0324, +0.0251]" |
| SA-SL-100 0.3197; SA-MT-20 0.3384 | HO l.280–281 | |
| Pratt-A-100 0.3386; Pratt-C-100 0.3149 | HO l.282–283 | |
| "Welch 95% intervals"; uncorrected | ST l.6, l.9 | "Welch t: two-sided, Welch–Satterthwaite df"; column "Δ [95 % CI]"; HO l.298 "no multiple-comparison correction" |
| seeds 0–2 on both machines, same initialisation | HO l.298 | "seeds 0 to 2 were run on both machines with the same initialisation and data stream, so pooled runs are not fully independent" |

### Label sweeps and diagnostics

| .tex fact | Source | Quote |
|---|---|---|
| batch 8: 0.357 (10%), 0.354 (20%), 0.346 (100%), 6 runs each; 2%: 0.191, 3 runs | HO l.320, l.322–324 | "SL-2-b8 … 0.191 ± 0.016 (3)"; "SL-10-b8 … 0.357 ± 0.013 (6)"; "SL-20-b8 … 0.354 ± 0.017 (6)"; "SL-100-b8 … 0.346 ± 0.007 (6)" |
| machines disagree 0.346 vs 0.362 | HO l.328 | "Machines disagree on SL-20-b8: gaint mean 0.346, cv02 mean 0.362." |
| crack precision 0.22–0.35, recall 0.67–0.73 | PD l.42–43 | "Crack precision is 0.22–0.35; recall is 0.67–0.73." |
| fit check: crack IoU 0.325 on 47 train cells of a 10% model; inactive 0.881 own, 0.417 test | FV l.34, l.51, l.54; H06 l.234 | "SL-10-b8 \| (a) train, labelled \| 0.3252 ± 0.0023" (crack table); "SL-10-b8 \| (a) train, labelled \| 0.8814 ± 0.0017" (inactive table); "SL-10-b8 \| (d) test \| 0.4172 ± 0.0081"; H06: "SL-10 (47 images) \| 0.325 … \| 0.881 \| 0.340 \| 0.417" |
| number behind the user's worry | H06 l.238 | "Crack was not fitted even on training images (0.33 on the 47 images after 20,000 steps). This is the number behind the user's starting worry" |
| prototype diagnostic: four ALHVR runs; 383 held-out cells; 71% (119,384 of 168,511); 4.6% | HO l.422, l.424, l.427 | "Prototype diagnostic (cv02, four ALHVR runs, final weights, the 383 held-out train images, evaluation mode)"; "holds 119,384 of the 168,511 true crack pixels (71%)"; "the other network's prototypes 4.6% (this is what CG-CPCL uses)" |
| prototypes dead | PH l.315 | "### 9f. Prototype diagnostic (cv02, no training): prototypes are dead" |
| UCF sweep: DeepLabV3+ R50, 95,760 steps, batch 16 | HO l.443; HO l.434 | "cv02, Oct 6, all at 95,760 steps, batch 16, SGD poly lr 0.005"; "(DeepLabV3+ R50, 4-class defect mean IoU, test 2,289 images)" |
| 0.5364 ± 0.0042 (2), 0.4932 ± 0.0045 (3), 0.4146 ± 0.0017 (3), 0.2265 ± 0.0017 (3) | HO l.447–450 | rows "100% \| 9,562 \| 2 \| 0.5364 ± 0.0042"; "20% \| 1,912 \| 3 \| 0.4932 ± 0.0045"; "5% \| 478 \| 3 \| 0.4146 ± 0.0017"; "1% \| 96 \| 3 \| 0.2265 ± 0.0017" |
| 1% subset no corrosion | HO l.151 | "**The 1% subset has no corrosion image.**" |
| UCF MT 7 to 8 Oct | H06 l.266 | "(cv02, launched 7 Oct, finished 8 Oct …)" |
| MT 5% − SL 5% −0.0913 ± 0.0362; MT 1% − SL 1% −0.0742 ± 0.0275; below λ=0 controls | CV l.367, l.369, l.373, l.375 | "UCF MT 5 % \| UCF SL 5 % \| paired \| -0.0913 ± 0.0362 (n 3)"; "UCF MT 5 % \| UCF MT 5 % λ=0 \| paired \| -0.0688 ± 0.0531"; "UCF MT 1 % \| UCF SL 1 % \| paired \| -0.0742 ± 0.0275 (n 3)"; "UCF MT 1 % \| UCF MT 1 % λ=0 \| paired \| -0.0521 ± 0.0216" |
| these test SemiCE | H06 l.277 | "these runs used SemiCE, which P2 later showed is not a valid consistency loss, so **they test SemiCE, not Mean Teacher**" |
| "Where it stands" summary | HO l.26 | "on BenchmarkEL no unlabelled loss has shown any effect, and label count does not move the score between 5% and 100%. The crack class cannot even be fitted on training images. UCF-EL does show a clean label gap … so the SSL question moved there." |
| λ problem noticed while writing the handoff | HO l.263, l.562 | "While writing it I noticed the ALHVR loss-weight schedule problem (section 9.1)"; "Found while writing this document." |

## Section "Reproductions": Pratt

| .tex fact | Source | Quote |
|---|---|---|
| per-image IoU, median over 50 test cells, hand-picked | PM l.12, l.27 | "**median over the 50 test images**"; "Fifty images with a prevalence of cracks, gridline defects, and inactive areas were assigned to testing" |
| 12 models (4 archs × 3 weight sets) | PH l.200 | "BenchmarkEL, 12 models = 4 archs x 3 weight sets" |
| 4c 0.25 / 0.20 / 0.38 / 0.28 | PM l.48 | "4c DeepLabv3+ custom (headline) \| **0.25** \| 0.20 \| 0.38 \| **0.28** \| **0.86**" |
| weight sets A and C values | PM l.34 | "A all 1. … C custom: background 0.2, ribbons 3, gridline 10, inactive 10, crack 20, others 1" |
| no optimiser etc.; encoder not named; absent rule not stated | PM l.33, l.35; D1 l.501 | "**The encoder is not named.**"; "**No optimiser, learning rate, epochs, batch size or schedule.**"; "they do not say how images without a class are handled in the median IoU" |
| 3 Oct run | H06 l.57 | "Sat 3 Oct \| … Pratt reproduction" |
| VGG16 from user's spec; 23,750,424 params | D1 l.489–490, l.501–502 | "with **23,750,424 parameters**"; "VGG16 and the ~23.75M parameters come from your spec." |
| flips only (four images of their offline set) | D1 l.494–496 | "These are the four images of their offline augmented set. There is no photometric augmentation." |
| pilot recipe Adam 1e-3, cosine, 20,000 steps, batch 4; all 478 train | D1 l.498–500 | "Adam 1e-3 (wd 1e-4), a 200-step warmup, then cosine to 0, 20,000 steps, batch 4 … Labelled data: the full official train split (478)." |
| one seed each | D1 l.578 | "This is one seed each" |
| rules A, B, C definitions | PH l.188 | PH l.188: "**A** exclude absent images, **B** absent scores 0 …, **C** absent and unpredicted scores 1" |
| 50 / 37 / 17 test cells with class | D1 l.570 | "{'crack': 50, 'gridline': 37, 'inactive': 17} of 50." |
| set A final: 0.149 / 0.339 / 0.420, rule A mean 0.303; B 0.145; C 0.449 | D1 l.559–561 | "final (step 20,000) \| median IoU, rule B (primary) \| 0.149 \| 0.284 \| 0.000 \| **0.145**"; "rule A \| 0.149 \| 0.339 \| 0.420 \| **0.303**"; "rule C \| 0.149 \| 0.322 \| 0.877 \| **0.449**" |
| set C final: 0.176 / 0.207 / 0.445, mean 0.276; B 0.113; C 0.326 | D1 l.553–555 | "rule B … **0.113**"; "rule A \| 0.176 \| 0.207 \| 0.445 \| **0.276**"; "rule C … **0.326**" |
| standard mean of 3: 0.331 vs 0.284; paper ranks C first | D1 l.576–577 | "**Set A (equal weights) beats Set C on global IoU** (final mean over crack/gridline/inactive 0.331 vs 0.284 …) … The paper ranks C first." |
| rule B primary; "approximately reproduced"; 0.116 (best-val set C) / 0.145; U-Nets 0.133–0.160 | D1 l.572, l.574; D1 l.550; PH l.245 | "**Rule B is primary**"; "ours Set C 0.116 and Set A 0.145, against the paper's U-Nets at 0.133 to 0.160"; l.550 "pratt_unet_setC_s0 \| best val (step 17,500) \| median IoU, rule B (primary) \| … **0.116**"; PH: "**approximately reproduced**" |
| 8 Oct analysis: rule B impossible (17 of 50; 4c 0.38), 4a 0.13 at recall 0.15 rules out C; rule A inferred | PM l.12 | "Nonzero inactive medians (for example 0.38 for 4c) with inactive in only 17 of 50 test images rule out "absent = 0" (rule B) … 4a (inactive recall 0.15 …) has median 0.13, which rules out rule C … **So rule A … [inferred]**" |
| 8 Oct date of PM | PM l.246 | "## Correction (2026-10-08 …)" and GIT `980e6af` 2026-10-08 00:12 |
| no gap under A: set A 0.303 vs 2a 0.19; pilots 0.280–0.295 vs 0.28; crack medians 0.21–0.25 vs 0.13–0.26 | PM l.54, l.56–58 | "Pratt-A … mean **0.303**. Paper 2a: 0.15 / 0.32 / 0.09 (avg 0.19)"; "Pilot U-Net++ arms, rule A means: SL-100 0.280, SL-20 0.287, MT-20 0.288, ALHVR interim 0.295. Paper best 4c: **0.28**."; "our U-Net++ arms 0.21–0.25 … Paper 0.13–0.26."; "**So no reproduction gap remains on BenchmarkEL once the convention is aligned.**" |
| pilots = coupled-augmentation code | D1 l.532 | "Pratt median IoU of the pilots (**pilot, coupled-augmentation code**)" |
| rule moves mean ~3x: 0.15 (B) → 0.49 (C) | PM l.64 | "It changes the mean by about 3× (our rules B → C: 0.15 → 0.49)." |
| 13 Oct P-series rescore: 0.354 ± 0.004, 0.303 ± 0.010, 0.443 ± 0.028, 0.367 ± 0.012; 5 seeds; revised training masks | PC l.1, l.14, l.30 | "supervised 100% (L3, 5 seeds) \| 0.354±0.004 \| 0.303±0.010 \| 0.443±0.028 \| **0.367±0.012**"; "**Our P-series models were trained on the revised masks** and are scored here on the old ones" |
| not like-for-like | PC l.34 | "It is not a like-for-like benchmark claim (caveats above)." |

## Fioresi

| .tex fact | Source | Quote |
|---|---|---|
| DeepLabv3 COCO R50, plain CE, lr 0.005; bg threshold 0.54 | PM l.78, l.80 | "DeepLabv3 (not v3+) ResNet-50, **COCO-pretrained** … Plain CE … lr 0.005."; "a pixel is background only if P(background) > 0.54" |
| headline F1 0.81 / 0.58 / 0.33 / 0.78 (with 256 simulated) | PM l.87 | "**with simulated (17,064), headline** \| .81 / .80 / **.81** \| .66 / .51 / **.58** \| .26 / .44 / **.33** \| .69 / .89 / **.78**" |
| abstract 57.3%, likely 5-class with background (inferred) | PM l.247–249 | "The abstract states "a mean intersection over union score of 57.3%" … it is most likely a 5-class mean including background (unverified)." |
| one held-out set | PM l.73 | "**80/20 split into "training and validation/testing sets". There is one held-out set.**" |
| 9,562 + 2,289; 17,064 | PM l.75, l.71 | "**The public release has 9,562 train + 2,289 test = 11,851 [ours].**"; "17,064 images = 16,808 real + 256 Griddler-simulated" |
| our recipe: DeepLabV3+ ImageNet R50, shorter side 295, 256 crops, flips, SGD poly, batch 16, final step | HO l.200; D1 l.604–608 (l.604 poly schedule; l.608 "Test at the final step only: no val, no checkpoint selection") | "DeepLabV3+ ResNet-50 ImageNet (Fioresi recipe), shorter side 295, 256 crops"; "schedule: poly …; batch 16; …; train augmentation: shorter side resized to 295, random 256 crop, h/v flips"; "Test at the final step only: no val, no checkpoint selection." |
| lr 5e-3 for FSL 100 ep | PH l.233 | "**FSL 100 ep, lr 5e-3 poly** \| 59,760 \| **0.497 / 0.636**" |
| 100 epochs, 59,760 steps, 0.497 std (0.636 pvs3) | D1 l.216, l.751 | "`ucf_fsl_100ep_s0` (supervised, all 9,562, 59,760 steps) \| 0.497 …\| 0.636"; "standard defect mIoU **0.4968**, pvs3 0.6364" |
| tolerance 0.03 of 0.4815; faithful-aug run skipped | D1 l.618, l.741, l.752 | "if `ucf_fsl_100ep_s0`'s standard defect mIoU differs from 0.4815 by more than 0.03, `ucf_fsl_100ep_faithfulaug_s0` runs"; "its gate: 0.4968 is within 0.03 of 0.4815"; "so `ucf_fsl_100ep_faithfulaug_s0` will be skipped" |
| 0.481 = mean of IoU equivalents of headline F1 | PM l.90 | "IoU = F1 / (2 − F1) … crack **0.681**, contact **0.408**, interconnect **0.198**, corrosion **0.639**, mean **0.481**." DERIVED link: (0.681 + 0.408 + 0.198 + 0.639) / 4 = 0.4815, which is the 0.4815 of D1 l.618 (the identification is ours; D1 does not name its source) |
| crack F1 0.806 vs 0.81; contact/interconnect/corrosion 0.648 / 0.498 / 0.795 vs 0.58 / 0.33 / 0.78 | PM l.93 | "**SL-100 (95,760 steps):** IoU 0.675 / 0.479 / 0.332 / 0.660, which is F1 **0.806 / 0.648 / 0.498 / 0.795**." |
| from the 6 Oct sweep | HO l.443 | "cv02, Oct 6, all at 95,760 steps" |
| no deficit; not strict reproduction (data/split, model, crops, test selection) | PM l.95–100 | "**So our supervised baseline equals Fioresi on crack and beats it on contact, interconnect and corrosion** … Remaining differences, so these are not a strict reproduction: different data and test split; DeepLabv3 COCO against our DeepLabV3+ ImageNet; 224 random crops against our shorter side 295 with 256 crops; their probable test-set selection." |
| early "shortfall of 7.1" = 4- vs 5-class | PH l.372 | ""Fioresi shortfall of 7.1 is real": was 4-class vs 5-class mixing." |

## PV-S3

| .tex fact | Source | Quote |
|---|---|---|
| claim: MT + SemiCE handles class imbalance | A04 l.4 | "Mean Teacher on DeepLabv3+ with a "Semi Cross-Entropy" (SemiCE) consistency loss for class imbalance." |
| 67.00 / 8.76 / 70.84 | PM l.125–127 | "SL 20% (Table 1) … **8.76**"; "SSL 20% (PV-S3) … **67.00**"; "FSL 100% (Table 3) … **70.84**" |
| recipe: 30 epochs, batch 16, SGD 1e-3, λ 1.5; ImageNet R50 DeepLabv3+ | PM l.113–114 | "DeepLabv3+, ImageNet ResNet-50, Mean Teacher."; "**30 epochs**, batch 16, SGD lr 0.001 … Consistency weight λ = 1.5." |
| thresholds (0.6, 0) in Tables 1–2, (0.2, 0.4) in §4.2 and journal | PM l.118; F05 l.9 | "Tables 1–2 use (0.6, 0). §4.2 later says "we chose ... (0.2, 0.4)""; F05: "t_pos 0.2 / t_neg 0.4" |
| pooled IoU over 4 defect classes; split and background not described | PM l.14, l.110; F05 l.9 | "dataset level, Eq. 9"; "**The split is not described in the paper**"; F05: "background treatment not stated" |
| PV-S3 convention definition; recall unchanged | PH l.185 | "drop every pixel whose ground truth is background, then build the confusion matrix. **Recall is unchanged**, only background false positives vanish" |
| 0.230 pvs3 / 0.185 std at 30 ep, 1e-3, 3,585 steps | D1 l.628 | "`ucf_sl20_30ep_s0` \| 1,912 \| 3,585 (30) \| 1e-3 \| argmax \| 0.185 / … \| 0.230 / …" |
| 0.559 / 0.448 at 12k steps, 5e-3 | D1 l.630 | "`ucf_sl20_12k_s0` \| 1,912 \| 12,000 (100) \| 5e-3 \| argmax \| **0.448** … \| **0.559**" |
| dates 3 to 4 Oct | HO l.434 | "Gaint, Oct 3 to 4 (DeepLabV3+ R50 …)" |
| "is not able to learn the features" | PM l.141 | "Their own §4.2 says SL-20 "is not able to learn the features ... very low pixel accuracy"." |
| step-matched 0.491 ± 0.009 std, 0.607 ± 0.007 pvs3, 95,760 steps, 3 seeds | D1 l.217–220 | "`ucf_sl20_stepmatched_s0` (supervised, 1,912, 95,760 steps: the matched control)"; "**step-matched SL, 3 seeds** \| **0.491 ± 0.009** \| **0.607 ± 0.007**" |
| all-crack 0.766 pvs3 vs 0.066 std; dilation 0.636 → 0.717, 0.497 → 0.456 | D1 l.754, l.756–758 | "crack IoU 0.066 standard vs **0.766 pvs3**"; "pvs3 defect mean IoU rises from 0.636 to **0.717**; standard falls from 0.497 to 0.456." |
| v1 strong view; strong view alone −0.045 (0.448 → 0.403) | D1 l.660, l.251 | "**v1:** CE on the student's strong view"; "strong-view supervision alone costs only −0.045 (0.448 → 0.403)" |
| v2 weak view | D1 l.662 | "**v2:** CE on the **weak** view" |
| 1,465,919 vs 102,570 | D1 l.222 | "0.067 \| **1,465,919**"; header "corrosion pixels predicted (GT 102,570)" |
| 0.96%, 23×, 16× truth; 99.4%; 21.6× at 0.99 | D1 l.231, l.269, l.270, l.286, l.288 | "labels 0.96 % of the unlabelled pixels as corrosion, 23× the labelled-GT share"; "That is 23× the labelled share and 16× the truth."; "99.4 % of all pixels clear t_pos 0.6"; "**0.00896 (21.6×)**"; "It is 23× at 0.6 and 21.6× even at 0.99" |
| measured on unlabelled images, no training | D1 l.256 (heading) | "#### Pseudo-label diagnostic (no training): `ucf_pvs3_v2_ssl20_s0` on the 7,650 unlabelled images" |
| corrosion 0.067 std vs 0.879 pvs3 | D1 l.241 | "v2's corrosion scores 0.067 standard but **0.879 pvs3**" |
| cap 2× labelled share; corrosion 0.631; 0.073 below; 132 of 187; one seed | D1 l.677, l.224, l.235, l.301, l.238 | "at most **2×** its labelled-GT share"; "`ucf_pvs3_v2_classthr_s0` … **0.418** … 0.580 … **0.631**"; "Overall 0.418, still **0.073 below step-matched SL**"; "the cap is exceeded in 132 of 187 windows (EMA lag)"; "One seed." |
| our version trained background (not faithful) | PH l.254 | "our reimplementation (which trains background) was never faithful on this point" |
| "SSL 46.4" not reproduced | D1 l.239 | "**The earlier PV-S3 implementation is not reproduced.** Your records give it **46.4 standard**" |

### Table `tab:repro-pvs3`

| Row | Source |
|---|---|
| 3,585 / 0.185 / 0.230 | D1 l.628 |
| 12,000 / 0.448 / 0.559 | D1 l.630 |
| 95,760 / 0.491 ± 0.009 / 0.607 ± 0.007 | D1 l.217, l.220 |
| 59,760 / 0.497 / 0.636 | D1 l.216 |
| v1 95,700 / 0.200 / 0.379 | D1 l.221; D1 l.245 "`configs/ucf_pvs3.yaml` … 95,700 steps" |
| v2 95,700 / 0.276, 0.283 / 0.568, 0.436 | D1 l.222–223; PH l.237 "PV-S3 v2 … \| 95,700 \|" |
| cap 95,700 / 0.418 / 0.580 | D1 l.224; PH l.238 |
| released 14,370 / 0.050 / 0.828 | CV l.887, l.928 "\| **defect mean** \| 0.0500 \| … \| 0.8284 \|" |
| published 8.76 / 67.00 / 70.84 | PM l.125–127 |
| 1,912 labelled; 2,289 test; UCF no val upstream | HO l.151; HO l.434; PH l.162 "No val split exists upstream (upstream validates on test)." |
| machines: released code on cv02; the rest on gaint | CV l.887 (cv02 run); HO l.434 "Gaint, Oct 3 to 4"; HO l.458 "Our reimplementation (gaint):" |

### Released code

| .tex fact | Source | Quote |
|---|---|---|
| 5 Oct | CV l.887 | "\| 3 \| Oct 5 05:07 \| … **done**: training rc 0 at 07:22 (2.25 h, 30 epochs, 14,370 steps" |
| one student + two EMA teachers, 125.3M | CV l.850 | "one student and two EMA teachers (keep rate 0.996), with 125.3M params in total" |
| lr 1e-2 in saved config vs 1e-3 paper | PH l.249 | "lr from `saved/ssl_el/config.json` = **1e-2** (paper and CLI default say 1e-3)" |
| ignore_index 0 in loss, loader, model, metric | PH l.251 | "**`ignore_index = 0` everywhere** (`main/train.py:30`, `main/DataLoader/pvs3.py:68` …, `Model/…/EntireModel.py:51,63`, `Utils/metrics.py:73-76`, …)" |
| background encoded 0; no gradient; none predicted as bg | CV l.890–892 | "0 of the background-GT pixels (184M on eval295, 215M native) are predicted as background"; "so class 0 never receives a gradient" |
| std 0.050; corrosion 3.33M vs 102,570 (32×) | CV l.896–897 | "defect mean IoU **0.050** on eval295 … Corrosion is predicted on **3.33M px against a GT of 102,570 (32×)**" |
| pvs3 0.828 eval295, 0.791 native; val log 0.9133 / 0.7806 / 0.5959 / 0.8735 equals the native per-class values, so 0.791 (not 0.828) matches the log | CV l.899, l.903–906, l.928, l.944–948 | "defect mean IoU **0.828** on eval295 and **0.791** native."; "logged per-class IoU crack 0.9133, contact 0.7806, interconnect 0.5959, corrosion 0.8735, and background 0. These equal our **pvs3 / native** numbers to 4 decimals."; native table l.944–947 pvs3 IoU 0.9133 / 0.7806 / 0.5959 / 0.8735, mean l.948 0.7909; eval295 table l.924–928 pvs3 IoU 0.9147 / 0.7392 / 0.7866 / 0.8731, mean 0.8284 (does not match the log). AUDIT 27 Nov: settled, see CONFLICTS 1 |
| supervised-only mode cannot run | CV l.861 | "The `model.semi=false` flag exists, but the released code cannot run it." |
| 16,327 names, 5,194 not in release; 1,769 of 2,289 in train lists; 437 val | CV l.839–841; HO l.153 | "Their shipped splits cover 16,327 names. 5,194 of those are not in the public UCF-EL release."; "They also put 1,769 of the 2,289 public test images into their labelled / unlabelled training lists, and 437 more into their val list." |
| step-matched above every PV-S3 arm (standard) | PM l.148 | "**Our step-matched SL control is 0.491, above every PV-S3 arm [ours].**" |
| released SemiCE: softmax CE vs teacher argmax, max-prob ≥ 0.6, thresholds on probabilities | AA l.85–88 | "positive = **softmax CE against the teacher argmax**, weighted by teacher max-prob, only where max-prob ≥ 0.6. … Thresholds are on **probabilities**." |
| ours: per-class BCE on raw logits, thresholds 0.5·freq ≈ 0.001 crack | AA l.79–82 | "positive BCE-with-logits(z_c, 1) where the teacher **raw logit** z^T_c > t_pos[c] … t_pos = 0.5·freq … So t_pos ≈ 0.0009 for crack" (P2 l.23 gives 0.0013 for crack; "about 0.001" covers both; see CONFLICTS 3) |
| Table 6 pooled vs Pratt medians | PM l.152–155 | "**Their BenchmarkEL comparison (Table 6) is invalid.** … Those are **per-image medians from 24-class models**. PV-S3's own numbers are dataset-level IoU" |
| journal version fixed nothing | F05 l.26 | "## Check 1: did the PV-S3 journal version fix what we measured? **No.**" |

## SA-UNet++

| .tex fact | Source | Quote |
|---|---|---|
| UAV solar-panel defect set (MIAD), 4 classes, no EL | PM l.161, l.163 | "**No EL data at all.**"; "T2: MIAD UAV solar-panel defects, 4 classes" |
| J 0.95 ± 0.09 vs 0.92 ± 0.12; single run | PM l.168 | "T2 (Table I): SA U-Net++ J **0.95 ± 0.09** … U-Net++ J **0.92 ± 0.12** … Single run, no significance test." |
| per image, background in mean (inferred) | PM l.167 | "**Probably per image, with background in the class mean [inferred]**" |
| our Δ −0.0036 [−0.0324, +0.0251] test; −0.0211 [−0.0510, +0.0089] val+test | ST l.27–28 | as quoted above |
| reading: large objects, background-inclusive mean, no 2–3 px test | PM l.169 | "The paper never tested thin defects on EL, and its gains are on large objects under a background-inclusive mean." |

## ALHVR

| .tex fact | Source | Quote |
|---|---|---|
| ACDC (cardiac) 10%: 81.59 → 90.56 Dice | PM l.191, l.177 | "ACDC 10% (7 labelled): U-Net 81.59 → ALHVR **90.56 Dice**"; "ACDC (RV / LV / Myo)" |
| does not target rare classes | PM l.177 | "**It does not target class imbalance or rare classes.**" |
| port differences (optimiser, loss, batch, classes, selection) | PM l.199–204 | rows "Optimiser / LR \| SGD 0.01, **constant** \| Adam 1e-3, **cosine to 0**"; "Supervised loss \| CE + Dice, unweighted \| weighted CE"; "Batch \| 8 L + 8 U \| 4 L + 4 U"; "Classes \| 4 (ACDC) \| 24"; "Selection \| best val Dice \| final step" |
| audit 8 Oct | AA (file in R/analysis committed in GIT f9708c0, 7 Oct 23:59, msg "…audit + paper notes"); H06 l.287 "The audit (`analysis/alhvr_audit.md` §1) quantified this on 8 Oct." (see CONFLICTS 4) |
| 0.0156 vs 0.0393; 8.1% vs 37% | AA l.46–47 | "Ours (cosine to 0) \| 0.0156 \| 8.1%"; "Reference (constant) \| 0.0393 \| 37%" |
| 0.7% at 2,000; 89.4% at 19,000 when lr 0.6% of peak | AA l.56, l.60 | "2,000 \| 0.0017 \| … \| 0.7% \| 0.98"; "19,000 \| 0.0987 \| … \| 89.4% \| 0.006" |
| null by construction | AA l.66 | "The ALHVR loss-off control (+0.005 ± 0.023) is close to a null by construction." |
| no wiring error | AA l.26 | "No finding of a dropped term, a detached path or a sign error. The ALHVR losses are wired correctly." |
| fair port 23 Oct = AL1 in T21 | TT l.877 | "AL1 (training machine, 5 v 5, locked; 23 Oct)" |

## Hanifi P19

| .tex fact | Source | Quote |
|---|---|---|
| six models, 29 classes, BenchmarkEL 20221008; pooled IoU; group means | P19 l.1, l.12, l.31, l.36–38 | "29-class supervised segmentation"; "6 models at seed 0"; "their metric: IoU pooled over test images at the 208×304 output"; "mean IoU, 12 feature classes … 16 defect classes … 29 classes" |
| user request "reproduce hanifi 2025, asap"; locked 14 Oct before any run | P19 l.3 | "Protocol: `protocols/P19_hanifi2025_reproduction.md`, locked 14 Oct before any run (`8655bd6`; smoke excepted). The user: "reproduce hanifi 2025, asap"" |
| released code unchanged at fixed commit | P19 l.8 | "`github.com/sntubix/pv-defect-segmentation` @ `506aa0b` (keras_segmentation fork), run unchanged" |
| authors' TF/Keras versions; eight-GPU server (A6000); 14 Oct | P19 l.11 | "cv02 (RTX A6000), Python 3.10, TF 2.18, Keras 3.8 (the authors' versions), tmux `p19`, 14 Oct 08:58–09:31 IST. All 8 rc = 0." |
| 553 / 70 / 72; no aug; 416×608 | P19 l.14 | "BenchmarkEL `20221008` with the release split (553 / 70 / 72), no augmentation, input 416×608" |
| weighted CE Table 1 weights, Adam 1e-3, batch 8, early stopping on val loss | P19 l.15 | "weighted CE with the Table 1 weights, Adam lr 0.001, batch 8, early stopping on val loss (patience 10, best weights restored)" |
| seeds 1–2 for VGG16-UNet | P19 l.12 | "6 models at seed 0, plus VGG16-UNet seeds 1–2." |
| params equal; counts reproduce evaluate() | P19 l.19–20 | "trainable parameters equal the paper's Table 2 for all 6 models; our per-class TP/FP/FN reproduce their `evaluate()` (asserted)." |
| 208×304; absent = 0 | P19 l.26, l.31 | "Their metric scores an absent class as IoU 0."; "IoU pooled over test images at the 208×304 output" |
| 72 test cells | P19 l.25 | "our 72-cell test set" |
| Table rows | P19 l.36–44 | "0.678 ± 0.020 \| 0.663"; "0.246 ± 0.018 \| 0.326"; "0.416 ± 0.015 \| 0.494"; "0.884 ± 0.011 \| 0.879"; "0.328 ± 0.024 \| 0.369 (same 12, from Fig. 3)"; "**0.352 ± 0.008** \| 0.335"; "**0.469 ± 0.032** \| 0.550"; "**0.316 ± 0.028** \| 0.297" |
| reproduces: features, crack, gridline, fw-IoU | P19 l.62–64 | "The feature means …"; "Crack and gridline IoU for VGG16-UNet: ours are slightly higher"; "The frequency-weighted IoU (0.87–0.89)." |
| dead cell / belt mark absent; 0.502 / 0.293 | P19 l.27, l.68 | "The paper's VGG16-UNet scored 0.502 on dead cell and 0.293 on belt mark." |
| rings 0.017 vs 0.285, half the 12-class gap | P19 l.68 | "Half of that comes from **rings** (ours 0.017, paper 0.285; 1,626 GT px in our test)." |
| 9 inactive cells | P19 l.69 | "Our test has 9 inactive cells." |
| ranking: MobileNet-UNet 0.353 level; margin 0.031 under 2 sd (0.018) | P19 l.71 | "MobileNet-UNet (0.353) is level with VGG16-UNet (0.328 ± 0.024) … The paper's headline margin (VGG16-UNet over the next model, 0.031 on the 16-class defect mean) is under 2 seed sd here (VGG16-UNet sd 0.018)" |
| 29-class mean: 0.471 (28), 0.455 (29) vs 0.494 | P19 l.72; P19c l.2 | "(0.494 for VGG16-UNet) cannot be recomputed from its own Fig. 3 (0.471 with 28 classes, 0.455 with 29)" |
| 551/67/77 not released; 4× augmentation (2,204 frames) undescribed | P19 l.23–24 | "theirs is a 551 / 67 / 77 re-split, not released."; "they trained on 2,204 frames (= 551 × 4) with an undescribed augmentation." |
| neither like-for-like run | P19 l.82–85 | "A like-for-like comparison would need either … Neither was run." |

## SEiPV-Net rescoring

| .tex fact | Source | Quote |
|---|---|---|
| paper 0.8604, 0.9426, 0.8531, 0.7447; 50 test cells; 24 classes; no per-class, averaging, code | SE l.3 | "reports mIoU 0.8604, F1 0.9426, Dice 0.8531, IoU 0.7447 on the same 50 BenchmarkEL test cells … It averages over all 24 classes, gives no per-class numbers, does not define its averaging, and no code link was found." |
| 13 Oct; 18 final checkpoints; read-only; one confusion matrix per test cell; old labels 20211104 | SE l.1, l.5 | "(13 Oct 2026, descriptive, not a locked protocol)"; "Read-only CPU inference of 18 final checkpoints … One 24x24 confusion matrix per test cell; old labels (20211104)" |
| L3 100% (5 seeds): GT classes 0.514; weighted F1 0.933; per-image absent=1 0.840 | SE l.9, l.13 | "(L3 100%: 5 seeds …)"; "L3 100% \| 0.457 \| 0.514 \| 0.487 \| 0.886 \| 0.931 \| 0.623 \| 0.933 \| 0.840" |
| reading; F1 moves 0.012 from 5% to 100% | SE l.22–23 | "SEiPV F1 0.9426 is close to our pixel-weighted F1 (0.933); their mIoU 0.8604 is close to our per-image mean with absent classes scored 1 (0.840). … Their rule is not confirmed (no code)."; "Pixel-weighted F1 moves only 0.012 from 5% to 100% labels (0.921 to 0.933)" |
| "legacy-split P-series" checkpoints | SE l.5, l.9 | groups "L3 100%", "L3 10%", "A5c", "BsM5" are P-series arms (TT T21 rows P13, P6) |

## Table `tab:repro-summary`

Every cell repeats a value sourced above: Pratt (PM l.48, D1 l.560, PM l.56), Fioresi (PM l.87, l.93), PV-S3 (PM l.125–126, D1 l.628, l.630, l.222, CV l.928), SA-UNet++ (PM l.168, ST l.27), ALHVR (PM l.191, HO l.313), Hanifi (P19 l.42), SEiPV (SE l.3, l.13).

## Section "The audit and reset of 7 and 8 October"

| .tex fact | Source | Quote |
|---|---|---|
| 23:37 on 7 Oct, user message (paraphrased, typos corrected) | UM l.23, l.27; DL l.121–127 | UM l.23 "--- 2026-10-07T18:07:07.371Z" (= 23:37 IST); UM l.27 "i feel lost, coz it trained on 47 images and tested on sam e47, to get 0.3 iou on cracks, definitely dsomething wrong, my goal is to work son something sinspired by ALVHR to focus the rare classes … analysis first, the datasets, the mmodels, the issues … i strongly doubt there are some bugs in the trainning(minor misconfigurations) causing the unlabelled losses having zero effect"; DL l.121 "### D1. Restart with analysis first (7 Oct, 23:37)" |
| item 1: final-step test primary; Welch on 50 test cells; 38 tests, one survives Bonferroni | HO l.178; ST l.9–11; HO l.590 | "38 tests in `stats_tests.md`, only one survives Bonferroni" |
| "SL best over budgets" withdrawn as selection on test | PH l.376 | ""SL best over budgets": withdrawn (selection on test)." |
| UCF no val upstream; Fioresi official code validates on test | PH l.162; H05 l.195 | PH: "No val split exists upstream (upstream validates on test)."; `R/handbook/05_literature_and_baselines.md` l.195 "Validation equals test (confirmed later from the official `train.py`: val and test both use `set="test"`" |
| item 2: 20 of 54 val, 24 of 50 test | HO l.123 | |
| 55 dropped (48 / 6 / 1), exact match only; 196 val modules, 88 test modules | HO l.139–140 | "55 files dropped because the cell is a labelled image (48 train, 6 val, 1 test)"; "Only exact cell matches were dropped. 196 kept cells come from val modules and 88 from test modules." |
| UCF carved val inside unlabelled pool | PH l.162 | "Unlabelled pool for SSL = the other 7,650 official-train images (this **includes the 957 val images**, so val is not clean …)" |
| 25–44% UCF physical twins (8 Oct) | SR l.166 | "**25–44% of test cells have the same physical cell (other stress stage) in train**" |
| item 3: duplicate-pair IoU 0.257; 1 px shift 0.47–0.56; ±0.03 not interpretable | SR l.18–20; H06 l.359 | "Their crack IoU is 0.257"; "shifted by 1 px, 0.47–0.56"; H06: "So ±0.03 strict-IoU differences between methods cannot be interpreted for crack [inferred]" |
| defect mIoU measured over-prediction | PH l.104 | "**Real bottleneck:** crack over-prediction from class-weighted CE (crack precision 0.22-0.35 at recall ~0.70)." |
| item 4: P2 locked; 00:44 8 Oct; 100%; background 98.9%; crack 20.3% vs ~0.19%; 0.25 ± 0.35; cosine 0.07 | P2 l.3, l.4, l.11–12, l.21, l.23, l.29 | "Run: 8 Oct 2026, 00:44 IST"; "Protocol: `protocols/P2_semice_gradient_probe.md`"; "**0.25 ± 0.35**"; "**100%** of pixels"; "background \| 0.330 \| 98.9%"; "crack \| 0.0013 \| **20.3%** (true crack is about 0.19% of pixels)"; "cosine 0.07 ± 0.40" |
| P2 locked before running | GIT f9708c0 2026-10-07 23:59:58 | "protocols P1 (overfit check) and P2 (SemiCE probe) locked before running" |
| every MT result tested this loss | P2 l.36 | "So every MT result run with this loss (BenchmarkEL 20%, the external-pool queue, UCF-EL on cv02) tests this loss, not Mean Teacher." |
| ≥ 0.95 rule: crack 0.024%, ~8× under | P2 l.40, l.43 | "teacher max-prob ≥ 0.95"; "**crack 0.024%** (about 8× under its labelled share of about 0.19%)" |
| item 6: old split files never committed | SU l.17 | "**50/20/10% splits:** they were never committed … so they can't be rebuilt." |
| item 7: P1 locked, 8 Oct; 10 crack cells; 3,000 steps; 0.612; 0.861; 0.381; aligned; 0.668 ± 0.031 vs 0.656 ± 0.048; 1.75 px; blur and ±5° rotation | P1 l.3–4, l.9–10, l.19, l.21, l.23, l.32–33, l.45 | "Run: 8 Oct 2026, 00:46–01:52 IST"; "Protocol: `protocols/P1_overfit_check.md`, locked before running."; "10 train images that contain crack"; "3,000 steps"; "A \| weighted CE, no aug, bf16 \| 0.612"; "C \| plain CE + soft Dice … \| **0.861**"; "E \| weighted CE, **training augmentation** … \| **0.381**"; "loader mask identical to the raw PNG in 10/10 images"; "B (bf16) 0.668 ± 0.031, D (fp32) 0.656 ± 0.048"; "blur kernels of 3–7 px and ±5° rotations applied to labels a median 1.75 px wide" |
| item 8: one labelled subset; weights change with subset | HO l.132; HO l.576, l.578 | "**Every run so far uses the split of seed 0.**"; "Class weights change with the labelled subset \| label-fraction and batch-size comparisons mix in an operating-point shift" |
| repo started 23:59 on 7 Oct with P1/P2 protocols | GIT f9708c0 | "2026-10-07 23:59:58 +0530 research(init): … protocols P1 … and P2 … locked before running" |
| every experiment locked before runs; exploratory labelled | DL l.140–146 | "Every experiment gets a protocol in `protocols/`, committed before any run. … Anything outside the rules is labelled EXPLORATORY." |
| 8 Oct: survey 69 verified sources | GIT 980e6af; SR l.11 | "2026-10-08 00:12:49 … literature: verified survey (69 sources)"; "69 verified sources" |
| situation report conclusions | SR l.18, l.29, l.38–42 | "On BenchmarkEL, strict crack IoU is already at the level where label noise dominates."; "**Neither SSL method has actually been tested (measured from the code).**"; "Test sets are hand-picked or reused for validation. Metric conventions drop background or take per-image medians. Test images appear in training lists. Baselines are under-trained, results are single-run" |
| queue held 01:18 on 8 Oct; never ran | DL l.152, l.159 | "### D4. Hold the gaint external-pool queue (8 Oct, 01:18)"; "The queue has stayed held and untouched since." |
| standing rules kept | H06 l.393 | "match optimiser steps across arms; final-step weights primary …; never compare arms across machines; seeds at least 3 …; one change per arm; old-era numbers in separate tables from the P-series" |
| UCF set aside until module-disjoint re-split; never made | DL l.183–190 | "do not use UCF-EL for SSL label-efficiency claims on its official split."; "The re-split was never done." |
| P-series from 10 Oct; corrected recipe; revised labels | H06 l.65, l.443 | "Sat 10 Oct \| … the P-series proper begins"; "the supervised recipe was fixed in P6 (revised labels …)" |
| P-series still scored test50 in every run | TT T21 caption (l.853) | "test50 was scored in every P-series run" |

---

## Derived values (formula given)

1. "n.d." on the loss-off controls: paired mean ± sd over 3 seeds, −0.000 ± 0.024 and +0.005 ± 0.023 (HO l.311, l.313); n.d. because the spread includes 0 (no rule existed then).
2. "n.d." on SL-100, MT-20, SA-SL-20 rows of `tab:repro-phase1`: the Welch 95% CIs from ST include 0. ALHVR-20's CI [+0.0007, +0.0570] excludes 0; the .tex gives no verdict word for it (no rule was fixed before the runs; and its loss-off control is n.d.).
3. 0.4815 identified as the mean of the four IoU equivalents of Fioresi's headline F1: (0.681 + 0.408 + 0.198 + 0.639) / 4 = 0.4815 (PM l.90). D1 l.618 uses 0.4815 without naming its origin.
4. "about 0.001 for crack" for our SemiCE positive threshold: AA l.82 gives 0.0009, P2 l.23 gives 0.0013; both round to about 0.001.

## MISSING_CITES

- Gangopadhyay et al. 2025, "SA-UNet++" (self-attention U-Net++ for PV / remote-sensing segmentation), IEEE Transactions on Emerging Topics in Computational Intelligence 9(2), 1502 (PH l.202: "Gangopadhyay et al., IEEE TETCI 9(2):1502 (2025) \| SA-UNet++"). Not in `references.bib` (checked: no key matching gangop / sa-unet). Used as `\CITE{...}` twice in the .tex.

## UNSOURCED (left out of the .tex)

- Exact dates of phase 0 work (the handbook says "mostly September 2026 and earlier (exact dates unknown)", H06 l.27); the .tex says only "to the end of September".
- The poster file itself (not found locally; `to_human/ee511_deck/` is a later deck). Poster content is taken from PH l.359–367 only.
- When the poster was made and presented: no date found.
- SA-MT-20's provenance beyond HO l.281 (one run; PH l.258 still called it "[unverified]" on 6 Oct; HO of 7 Oct lists 0.3384).

## CONFLICTS

1. **PV-S3 released code, which number matches its validation log. SETTLED by audit 27 Nov: 0.791 (native).** The per-class log values (CV l.903–904) are identical to the native-resolution pvs3 column (CV l.944–947) and differ from the eval295 column (CV l.924–927; contact 0.7392 vs 0.7806, interconnect 0.7866 vs 0.5959). The summary wording of CV l.61, HO l.475 (handoff 6.10), PH l.101 and H05 l.224 ("0.828 … matches their own validation log") is loose: 0.828 is the same predictions on our eval295 grid. Original entry: CV l.61 (summary): "pvs3 convention: **0.828** (eval295) / 0.791 (native), which matches PV-S3's own validation log to 4 decimals." CV l.901–906 (detail): the per-class validation log "equal[s] our **pvs3 / native** numbers to 4 decimals" (native mean 0.791). H05 l.224 and PH l.101 (TL;DR item 3) repeat "0.828 … matches their own validation log". The .tex follows the detailed section: 0.828 on our grid, 0.791 native, native per-class values match the log.
2. **Pratt reproduction "approximately reproduced" mixes checkpoints.** D1 l.574 compares "Set C 0.116 and Set A 0.145": 0.116 is set C at its best-validation step (D1 l.550), 0.145 is set A at the final step (D1 l.559); set C's final-step rule-B mean is 0.113 (D1 l.553). The .tex states the 0.116 as best-validation.
3. **Our SemiCE crack threshold.** AA l.82 "t_pos ≈ 0.0009 for crack"; P2 l.23 "crack \| 0.0013". Both written "about 0.001".
4. **Date of the ALHVR audit.** H06 l.287 says it "quantified this on 8 Oct"; the file was in the first commit f9708c0 at 23:59 on 7 Oct (commit message "audit + paper notes"). The .tex says "the audit of 8 Oct" following H06; the commit time suggests 7 Oct 23:59 IST, within an hour.
5. **PV-S3 claim wording.** A04 l.4 says the paper "Claims SSL at 20% labels beats supervised at 100%", but the paper's own numbers (PM l.126–127) are SSL-20 67.00 vs FSL-100 70.84. The .tex states only "handles class imbalance" and the numbers, not the "beats 100%" claim.
6. **Pratt U-Net parameter count.** Lost pipeline: 23,751,576 (PH l.216); rebuild: 23,750,424 for a 1-channel input, 23,751,576 for 3-channel (D1 l.489–490). The .tex gives 23,750,424 (the run of 3 Oct).
7. **ALHVR λ=0 sd.** HO l.309 "0.3642 ± 0.016"; CV l.155 "0.3642 ± 0.0159". The .tex gives the mean only.
8. **Phase 1 Pratt rule-A best-val figure.** PH l.245 "Rule A Set C 0.283" (best-val step, D1 l.551); final-step rule-A Set C is 0.276 (D1 l.554). The .tex uses final-step values.
9. **Machine names.** In the old era the single-GPU server was the first machine and the eight-GPU server "a second machine" (HO l.241); in later chapters the eight-GPU server is "the training machine" and the single-GPU server "the second machine" (TT l.873, l.877). The .tex names both by hardware and gives the later-chapter name in parentheses.

## AUDIT 27 Nov 2026 (independent checker): notes for edited facts

| .tex fact (after edit) | Source | Quote |
|---|---|---|
| old-era conditions apply "on BenchmarkEL, unless stated otherwise" (UCF runs used DeepLabV3+ R50 and 3,585 to 95,760 steps; pilots and Pratt set C 0.116 are best-val) | D1 l.532–537, l.550, l.628–630 | "| run (best val) | rule B (primary) | rule A |..."; "best val (step 17,500)" |
| "SSL doubled" claim "is recorded as invalid" (not "withdrawn") | PH l.224 | "early claim "SSL doubles performance 10.83 to 21.19" is invalid (both runs undertrained)" |
| poster items (v)–(vii) were pending updates, not "needed final-step values" | PH l.363 | "(v) Gangopadhyay row; (vi) crack-width claim wording; (vii) numbers moved to final-step new-pipeline values." |
| poster Fioresi "published" 48.15 is the IoU equivalent of the published F1 (our identification) | PM l.90; D1 l.618 | "mean **0.481**" (0.681+0.408+0.198+0.639)/4 = 0.4815; D1 uses 0.4815 as the Fioresi reference |
| Pratt rule-A inference and ALHVR λ audit dated "7 and 8 Oct" | GIT f9708c0 2026-10-07 23:59:58 | `git show f9708c0:analysis/papers_metrics.md` l.12 already holds the rule-A inference; `git show f9708c0:analysis/alhvr_audit.md` l.46 already holds 0.0156 / 8.1% |
| pilot rule-A means are best-validation weights | D1 l.532–537 | "| run (best val) | rule B (primary) | rule A | rule C |"; "pilot SL-100% | 0.1524 | 0.2803"; "pilot ALHVR-20% (interim, step 13,500) | 0.1285 | 0.2948" |
| crack medians 0.21–0.25 are the U-Net++ arms; Pratt U-Nets 0.149 / 0.176 | PM l.58 | "our U-Net++ arms 0.21–0.25, Pratt-A 0.149, Pratt-C 0.176. Paper 0.13–0.26." |
| old-era rows "before 7 Oct" (pilots ran 2 Oct) | HO l.186 | "All "pilot" runs of Oct 2 used the coupled augmentation" |
| PV-S3 table scored on eval grid, shorter side 295 | D1 l.607 | "eval: the whole image with its shorter side at 295, argmax" |
| UCF physical twins 25–44% | SR l.166 | "25–44% of test cells have the same physical cell (other stress stage) in train" |
| the MT arms' semi_ce is the per-class BCE; the PV-S3 reimplementation used the softmax form | AA l.88–89; D1 l.663 | "Our `ConfidenceCELoss` (PV-S3 reimplementation) is the softmax version. The MT arm's `semi_ce` is not."; "SemiCE = CE towards the teacher's argmax where the teacher's max softmax ≥ t_pos = 0.6" |
| SEiPV re-scoring cells overlap the training pool | ch03_related.tex l.106 (working copy) | "8 of its cells are the same physical cell as a cell of the training pool" |
| P1: recipe, mainly augmentation, secondly the loss | P1 l.44–46 | "It is the training recipe."; "Augmentation (biggest factor)"; "Loss: plain or weighted CE learns a 0.2%-pixel thin class slowly." |
