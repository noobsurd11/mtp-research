# 06. History before the P-series: phase 0, phase 1, the reset, and the analysis-first restart

## What this covers

The full story of the project before the locked P-series experiments, and how the P-series began. It covers the earliest work (the user's "phase 0": SA-UNet++ with Mean Teacher + SemiCE, first reproductions), the gaint account reset that destroyed most of it, the rebuild and second round of work from 2 to 7 Oct ("phase 1": a new repo, ALHVR port, reproductions in a new pipeline, cv02 replication), the user's starting worry ("trained on 47 images, 0.3 crack IoU, something is wrong"), the analysis-first restart on 7–8 Oct that produced the first protocols (P1, P2), and the 11 Oct exchange in which the user pasted the phase 0 / phase 1 handoffs and answered questions about the older work.

It also records which old results were found invalid, and why. **All numbers in this file are old-era numbers** (original BenchmarkEL masks, from-scratch U-Net++, weighted CE, labelled batch 4 unless stated, SemiCE for Mean Teacher). They must never be put in the same table as P-series numbers (revised E-SCDD masks, ImageNet ResNet-34 U-Net++, CE + Dice, batch 8). This is one of the user's standing rules.

## Sources

- The user's pasted phase 0 and phase 1 handoffs and their answers about the older work, pasted 11 Oct 2026 (copy: `sources/chat/phase0_phase1_handoffs_pasted_2026-10-11.md`). Phase 1 doc: snapshot "00:04 IST, Tue Oct 6 2026", written 11 Oct from conversation history and memory; numbers "not re-verified against files".
- `~/mtp/MTP_session_handoff_2026-10-07.md` (snapshot 7 Oct ~22:15 IST; written from chat history plus a fresh read of both servers). Cited below as "handoff 10-07".
- gaint `/home/noob/work/el-fault-detection/reports/`: `summary.md` (2 Oct setup check), `day1.md` (running log 3–6 Oct), `results_consolidated.md`, `stats_tests.md`, `arm_differences.md`, `precision_diagnostic.md`, `bn_recalibration.md`, `external_pool.md`, `fit_vs_generalise.md`. Read-only.
- cv02 `~/noob/el_results/cv02.md` (cv02 report; UCF Mean Teacher table generated 8 Oct 10:10 UTC).
- `~/mtp/research/analysis/alhvr_audit.md`, `analysis/papers_metrics.md`, `to_human/situation_report_2026-10-08.md`, `results/p1/README.md`, `results/p2/README.md`.
- Session record of this conversation (`sources/chat/claude_session_summaries_2026-10-07_to_11.md`, `sources/chat/user_messages_2026-10-07_to_11.md`), and `~/mtp/research` git log.
- Memory file `mtp-el-ssl-project.md` (standing rules and the invalid list).

---

## 1. Naming: what "phase 0" and "phase 1" mean here

The word "phase" is used for two different things in the sources. Keep them apart:

| Term | Meaning in this handbook | Period | Where documented |
|---|---|---|---|
| **Phase 0** (user's term) | The earliest work: SA U-Net++ ported to PyTorch, Mean Teacher + SemiCE, the first SA ablation and SSL sweep, the first reproductions of four papers, the ALHVR port design notes, severity/compression plans | before the gaint reset; mostly September 2026 and earlier (exact dates unknown) | the user's first pasted doc ("phase0") |
| **Phase 1** (user's term) | The rebuild after the reset: new repo `el-fault-detection`, ALHVR port, reproductions in a new pipeline, cv02 replication, loss-off controls, diagnostics | 2 Oct to 7 Oct 2026 | the user's second pasted doc ("phase1"), snapshot 6 Oct 00:04 IST; handoff 10-07 (snapshot 7 Oct 22:15) |
| "Phase 0 rebuild" / "foundation" (inside the phase 1 docs) | The first step of phase 1 on 2 Oct: rebuilding the data, split, metric and trainer foundation in the new repo (96 tests) | 2 Oct | handoff 10-07 §4.2, §5 |
| P-series (P1–P16, E1) | Locked-protocol experiments run in this conversation | from 7–8 Oct | `protocols/`, `results/`, docs 08–10 |

The phase 1 author did not know the phase 0 decisions or the P-numbering (user's pasted answers, item 4).

---

## 2. Project context at the start

From the phase 0 and phase 1 handoffs:

- **Project:** an MTP (master's thesis project) with **WattCycle**, a solar asset-management company. Semi-supervised segmentation of defects in electroluminescence (EL) images of solar cells. Datasets: BenchmarkELimages (582 labelled, about 12k unlabelled, 512 × 512, 24 classes) and UCF-EL (phase 0 handoff, Part 1).
- **Dual mandate:** WattCycle wants something deployable that detects defects, grades severity and estimates power loss. The faculty advisor wants a submittable paper with a lightweight model (about 2M params in the phase 1 notes; about 4M on the poster; the phase 1 answers say the ~4M figure "came from your own thinking"). Advisor directives listed: reproduce a prior paper (done), explore Mixture of Experts (gated on a diagnostic; uncertain whether required), lightweight model (phase 1 handoff §1; answers item 6). On 11 Oct the user said model size is "not a constraint even 5M works" (see `01_project_overview_and_scope.md`).
- **Stated resolution of the dual mandate** (phase 1 answers item 4): full-accuracy results as the headline, a lightweight variant as a secondary point. The phase 0 doc instead recorded "Goal order: (1) something WattCycle can pilot, with the quantification pipeline as core claim, (2) paper with accuracy contribution"; the phase 1 author had no record of that ordering.
- **Course deliverables:** an EE511 Computer Vision poster (done; content partly outdated) and two paper presentations (Mean Teacher; ALHVR). The phase 1 handoff (§1) says both presentations were done (with slips noted in the ALHVR practice run: γ vs λ confusion, module-to-region routing, dataset conflation). The phase 0 doc's "one conflict to resolve" records that its author believed they were prepared while the user had said neither was presented yet. The MTP progress report in LaTeX had not been started (phase 1 handoff §0).
- **Identity details are inconsistent across sources** (phase 1 handoff §1). The poster lists the author as Yash Vijay Patil, IIT Mandi, course EE511, supervisor Dr. Dinesh Singh; other memory notes give other names and an institute (RGIPT). The handoff asks to confirm which institute and report template apply; the report template and page limit were never given.
- **Three-part thesis plan** (user, 7 Oct): (1) training methodology, the current focus; (2) architecture; (3) real-time deployment concerns (severity detection and others). See `01_project_overview_and_scope.md`.

---

## 3. Timeline at a glance

| When | Event | Source |
|---|---|---|
| Up to Aug 8 2026 | Old repo `noobsurd11/sa-unetpp-ssl-el`; last real commit Aug 8; later tagged `v0-sa-failed` (failed SA experiment only). Earlier TF-era code existed (user's answers mention it; nothing known) | handoff 10-07 §4.1; phase 0 handoff |
| September 2026 (phase 0) | SA U-Net++ in PyTorch; MT + SemiCE; SA ablation; SSL sweep; first reproductions of Fioresi, Pratt, Jha (PV-S3), Gangopadhyay; ALHVR port analysis; post-processing (Subpath A, 57 tests) and compression (Subpath B) plans; poster | phase 0 and phase 1 handoffs |
| Before 2 Oct | **The `noob` user on gaint was reset.** Reproduction code, UCF val split, Subpath A code, label splits and predictions were lost. The GitHub repo was two months stale; all September work is unrecoverable | phase 0 handoff ("What was lost"); handoff 10-07 §1, §5 |
| Fri 2 Oct | Gaint found empty. Public datasets and the ALHVR reference cloned. External pool (11,993 cells) downloaded via the Dropbox API. Setup check (`reports/summary.md`). New repo `el-fault-detection` created; "Phase 0" foundation rebuilt (96 tests). ALHVR port (phase 1a) and pilots started. ALHVR pilot killed at step 13,600 by an orderly OS shutdown at 21:34 IST | handoff 10-07 §5; gaint `reports/summary.md`, `day1.md` §1 |
| Sat 3 Oct | Shutdown diagnosed; resume and watchdog built; coupled-augmentation bug found, pilots rerun on fixed code; SA gate ported; Pratt reproduction; UCF pipeline and PV-S3 reimplementation; night queue. PV-S3 v1 at 0.200 | handoff 10-07 §5; `day1.md` |
| Sun 4 Oct | ALHVR seed 0 finished (0.370). PV-S3 v2 0.276 / 0.283; collapse traced to corrosion pseudo-labels. Step-matched UCF supervised control 0.491. cv02 set up as a second machine | handoff 10-07 §5 |
| Mon 5 Oct | cv02: MT with λ = 0 equals MT. Released PV-S3 code run as shipped (0.050 standard / 0.828 pvs3). Prototype diagnostic. Consolidation, stats tests, `numbers.tex`. Precision diagnostic; batch-8 supervised queue on gaint; ALHVR loss-off control and batch-8 runs on cv02 | handoff 10-07 §5; cv02 report |
| Tue 6 Oct | Batch-8 results (machines disagree). ALHVR loss-off control: no detectable effect. AP diagnostic, fit check, 5% and 2% splits, external pool filtered to 11,938. UCF label sweep (clear label gap). Gaint rebooted and lost its queue. Phase 1 doc snapshot at 00:04 | handoff 10-07 §5; phase 1 handoff §14 |
| Wed 7 Oct | Gaint rebooted again; resume-after-reboot added; BN recalibration; low-label runs (SL-5, SL-2). cv02: Mean Teacher (SemiCE) on UCF-EL at 5% and 1% with loss-off controls launched. Handoff 10-07 written (~22:15 IST); while writing it the ALHVR λ × learning-rate problem was noticed | handoff 10-07 §5, §9.1 |
| Wed 7 Oct ~23:16 IST onward | **This conversation starts.** The user points to the 10-07 handoff ("read the markdown", 23:37), states their worry, asks for analysis first. P1 and P2 protocols locked (`f9708c0`, 7 Oct 23:59) | git log; user messages |
| Thu 8 Oct 00:12–02:52 | Literature survey (69 sources), BenchmarkEL first-hand data analysis, situation report; P2 run (00:44) and P1 run (00:46–01:52) with replicates. The user held the gaint external-pool queue by hand (logged 01:18) | git log; `results/p1/`, `results/p2/` |
| Thu 8 Oct 12:27 | UCF-EL first-hand data analysis; situation report section 9 | git log; `data_analysis/ucf_el_report.md` |
| Sat 10 Oct | Directions survey; P3 (label versions, exploratory), P4, P5; P6 locked and run; P7, P8 locked and launched; the P-series proper begins | git log; `to_human/directions_2026-10-10.md` |
| Sun 11 Oct 11:24–12:46 IST | The user asks "supervised beating ssl, hows that possible" (11:24), mentions "SA SSL unetpp had raised the iou", then pastes the phase 0 and phase 1 handoffs (12:16) and the phase 1 answers (12:32), and answers the batched questions (12:46) | session record (`sources/chat/user_messages_2026-10-07_to_11.md`, `sources/chat/phase0_phase1_handoffs_pasted_2026-10-11.md`) |

Gaint instability (handoff 10-07 §2.1): orderly shutdown Oct 2 21:34 (who triggered it unknown; needs `adm`/sudo), reboot Oct 6 about 18:22–18:47 (killed two runs at step 12,500), reboot Oct 7 about 10:30. Its hardware clock holds IST while Linux reads UTC, so boot-time log stamps can be 5.5 h off.

---

## 4. Phase 0 (the earliest work, mostly lost)

Everything in this section comes from the user's pasted phase 0 handoff unless stated. None of its code or raw results survive.

**Setup and model.** SA U-Net++ ported to PyTorch; Mean Teacher + SemiCE. Defect mIoU (crack + inactive) as the headline metric; gridline (class 15) excluded as noisy.

**Findings recorded then (with their later status):**

| Phase 0 finding | Status |
|---|---|
| Old SA ablation "removing SA helps" (0.2028 vs 0.1792) and the SSL sweep (20%: 0.2580, 10%: 0.1323) | **Invalid.** They predate the GaussNoise fix (albumentations 2.x ignored `var_limit`; noise erased cracks) |
| SSL vs SL must match optimiser steps: an 8× step mismatch fake-produced a +7.4 gain | Kept as a standing rule |
| Reproduction gaps were metric-convention mismatches (Fioresi includes background, Pratt per-image median, PV-S3 ignores background-GT pixels) | Confirmed and detailed later (`analysis/papers_metrics.md`; `05_literature_and_baselines.md`) |
| UCF-EL 20% labels, equal steps: SL 48.9 / 60.8 (PV-S3 metric), PV-S3 reimplementation SSL 46.4 / 58.9, FSL 100% 50.2 | The SSL 46.4 record was **not reproduced** in phase 1 (old code lost) |
| Class weights: sqrt-inverse-frequency (~310:1), not raw (98,000:1) | Later found computed over train + val + test (a leak; see §6) |
| Topology mask for Subpath A: {1, 2, 3, 4, 9}, so busbars and ribbons don't create fake isolated gaps | Code lost with the reset |

**ALHVR port notes from phase 0:** Eq. 22 sharpening breaks at C = 24 (use softmax temperature sharpening); the cosine-logit ceiling at C = 24 caps the max softmax at about 0.24 (use τ ≈ 0.1); "Eq. 15 prototype problem is NaN from division by zero on rare classes" (later corrected: the code gives zero prototype vectors, no NaN; phase 1 handoff §10, §13 item 9); top risk: DTCT teaching background over cracks.

**Decisions recorded in the phase 0 chat ("Part 2"):**
- Keep Mean Teacher; add class-adaptive thresholding (FlexMatch style), decoupled from UniMatch's dual stream.
- Architecture work before further SSL method changes.
- Goal order: WattCycle pilot first (quantification pipeline as the core claim), paper second.
- No paired I-V data, so power loss would rely on published correlations; Köntges A/B/C: power loss tracks isolated (type C) area, not total crack pixels. Open check: does the BenchmarkEL taxonomy distinguish isolating cracks?

**Architecture findings (phase 0):** the SA block is `sigmoid(Q+K)*V`, an elementwise gate, not dot-product attention. Parameter counts from the repo code: SA U-Net++ 4,589,880; SA blocks 88,000 (1.9%); no-SA 4,501,880; base-20 1.79M; base-24 2.58M (no single base width gives exactly 2M). Jetson has no FP8 (use INT8 + TensorRT). Stage-2 ideas: non-local attention at a coarse level, axial/strip attention, thin-structure-preserving downsampling.

**Plans (not executed; code lost):**
- Subpath A (post-processing): per-class connected components, `regionprops`, boundary-truncation flag, skeleton length, isolation detection, mm calibration, a fixed output schema, manual check on 10–15 images (57 tests existed; lost).
- Subpath B (compression): SA vs no-SA on uncompressed models; native-narrow controls (base-20, base-24); latency harness on the Jetson; Torch-Pruning to ~2M; INT8 + TensorRT; rerun Subpath A on every compressed model; Pareto plot.

**What was lost and what survived:** lost: reproduction code, the UCF val split, Subpath A code (57 tests), label splits, predictions. Survived: the private repo `noobsurd11/el-fault-detection` (rebuilt foundation) and `sa-unetpp-ssl-el` (tag `v0-sa-failed`). cv02 was being set up with files copied from gaint.

**The poster (done; partly outdated).** "Label-Efficient Segmentation of Rare Defects in Electroluminescence Images of Solar Cells", projector format, LaTeX with `numbers.tex` macros. Method figure: (a) backbone (~4M-param U-Net, pretrained light encoder, full-resolution skip for 2 px cracks); (b) ALHVR-inspired SSL with M1 defect-aware sampling, M2 per-class thresholds γ_k, M3 EMA prototype memory; (c) severity grading (instances, crack skeleton via `skan`, electrical isolation via a topology mask, Köntges modes A/B/C, grade agreement by Cohen's kappa). Items needing update as of 6 Oct: the Fig. 3 caption cites CPS (wrong: ALHVR has no CPS term); M3 prototypes are dead; new step-matched number 0.491 ± 0.009; the PV-S3 released-code finding; numbers moved to final-step values (phase 1 handoff §12).

**First-pipeline reproduction records used on the poster (phase 1 handoff §7a; old era, lost pipeline):**

| Baseline | Published | Ours | Note |
|---|---|---|---|
| Fioresi FSL 4-class / 5-class | 48.15 / 57.30 | 50.21 / 59.42 | per-class IoU ours 66.89 / 44.43 / 33.20 / 56.35 |
| Pratt U-Net (rule B) | 13.33–16.00 | 15.01 | rule A 29.22, C 26.87; our model 23,751,576 params |
| Jha SL 20%, 30 epochs | 8.76 | 13.13 (PV-S3 metric), 10.83 standard | same under-trained regime |
| Jha SL 20%, 12.0k steps | n/a | 56.61 / 39.00 | converged |
| Jha SSL 20% (our reimplementation), 95.7k steps | 67.00 | 58.85 / 46.40 | 8.15 short on their metric |
| SL 20% step-matched, 95.8k steps | n/a | 60.79 / 48.90 | beats SSL |
| FSL 100%, 59.8k steps | 70.84 | 65.84 / 50.21 | |

The early claim "SSL doubles performance 10.83 to 21.19" is invalid (both runs under-trained) (phase 1 handoff §7a).

The Pratt row uses rule B as the phase 1 handoff did ("primary, reproduces Pratt"). The 8 Oct metric analysis infers the paper used rule A instead (the paper's nonzero inactive medians, e.g. 0.38 for 4c, are impossible under rule B, which forces the median to 0 when inactive is in only 17 of 50 test images), and under rule A no reproduction gap remains (`analysis/papers_metrics.md` §1.4; `05_literature_and_baselines.md`).

---

## 5. Phase 1 (2–7 Oct): the rebuild and what it measured

### 5.1 The rebuilt foundation (2 Oct; handoff 10-07 §4.2)

| Piece | Decision |
|---|---|
| Masks | read index masks directly; a value outside 0–23 is an error |
| Splits | a missing split file is a hard error. "The old code silently trained on all 582 images, test included" (handoff 10-07 §4.2); the 2 Oct setup check says that would happen whenever a split file was missing (`reports/summary.md`) |
| Augmentation | flips, 90° turns, ±5° rotation with constant border, blur, noise, brightness/contrast; GaussNoise `std_range=(0.0124, 0.0277)` |
| Class weights | from the labelled subset in use, train only; square-root inverse frequency, mean 1 over classes with pixels, capped at 10× the median, **weight 0 for absent classes** |
| Metrics | one module; dataset-level confusion matrix; absent class is NaN and left out of means; headline `defect_miou` = mean IoU of crack and inactive; also 24-class mIoU, 12-defect mIoU, crack recall, relaxed crack recall (2 px), image-level crack false-positive rate, pixel AP, and the `standard`, `pvs3`, `pratt_median` conventions |
| Trainer | step-based, one trainer for supervised and SSL; 20,000 steps; Adam 1e-3, wd 1e-4, 200-step warm-up, **cosine decay to zero**, grad clip 1, bf16 autocast |
| Model | plain U-Net++, 4,981,368 parameters, **trained from scratch**; SA variant 5,440,120 |
| Evaluation rule | **final-step test is primary**; best-val secondary because val has 54 images and best-val selection flips the sign of several comparisons; val+test pooled (104 images) secondary |

The 2 Oct setup check (gaint `reports/summary.md`) found, before any training: the loader expected colour masks while the shipped masks were class indices (so all classes except background would have become "ignore", 24.6% of pixels; 582 colour masks were generated); class frequencies hard-coded in `class_info.py` matched all 582 images including test (a leak; recomputed on train only the weight ratio is 615:1, not 313:1); the silent fallback to all images; UCF masks contain 128 (ignore); rotation can crop up to 81% of a crack; splits share whole modules. No unlabelled-set manifest existed. It also found GaussNoise falling back to its default (about 10–15× stronger than intended, on 30% of samples), the 50/20/10% split files never committed (`prepare_splits.py` would reshuffle to 466/58/58, so the old subsets cannot be recovered), and the UCF 957-image val split not checkable (no generator or seed on the box) (`reports/summary.md`, `setup_check.md`).

### 5.2 Method implementations (handoff 10-07 §4.4)

| Method | Notes |
|---|---|
| Supervised (SL) | weighted CE |
| Mean Teacher (MT) | EMA 0.999; λ 0 for 2,000 steps, linear ramp to 1.5 over 2,000–3,999; **SemiCE** consistency with thresholds from class frequencies; labelled view = the SL arm's augmentation ("strong"); the **EMA teacher is evaluated**; 4 labelled + 4 unlabelled per step |
| ALHVR | two networks, two optimisers, no EMA, clean + perturbed decoder pass each; follows the reference code where paper and code disagree; network A evaluated; λ max 0.1 ramped over the whole run; 18.3 GiB, 0.70 steps/s alone on gaint |
| SA gate | flag `model.sa_gating`, byte-identical to the old SA block |
| Pratt reproduction | `smp.Unet` VGG16 ImageNet, 23.75M params, weight sets A and C |
| UCF pipeline | DeepLabV3+ ResNet-50 ImageNet (Fioresi recipe), shorter side 295, 256 crops |
| PV-S3 reimplementation | mean teacher with paired geometry, confidence CE, a per-class threshold variant |

Common BenchmarkEL setup: U-Net++ 4.98M, 512 input, 20,000 steps, lr 1e-3 cosine, labelled batch 4, class-weighted CE, split seed 0, training seeds vary, final-step weights, bf16, Dropout2d 0.2. Speeds on gaint: SL 8.3 it/s, MT 3.5, ALHVR 0.72 (phase 1 handoff §9).

### 5.3 Old-era BenchmarkEL results (20% and 100% labels, batch 4)

**Old era; original masks.** Final step, 20,000 steps, split seed 0, standard convention; test = 50 images; val+test = 104 images. Pooled over gaint (g) + cv02 (c). Source: gaint `reports/results_consolidated.md`; handoff 10-07 §6.1.

| Arm | n (g + c) | Test defect mIoU | Val+test defect mIoU | Test crack IoU | Test inactive IoU |
|---|---|---|---|---|---|
| SL-20 | 8 (3 + 5) | 0.3435 ± 0.0329 | 0.3137 ± 0.0195 | 0.2489 ± 0.0544 | 0.4381 ± 0.0243 |
| SL-100 | 4 (1 + 3) | 0.3383 ± 0.0060 | 0.2956 ± 0.0107 | 0.2719 ± 0.0045 | 0.4047 ± 0.0117 |
| MT-20 (SemiCE) | 6 (3 + 3) | 0.3662 ± 0.0061 | 0.3415 ± 0.0059 | 0.2759 ± 0.0033 | 0.4565 ± 0.0137 |
| ALHVR-20 | 6 (2 + 4) | 0.3724 ± 0.0103 | 0.3472 ± 0.0108 | 0.2929 ± 0.0057 | 0.4518 ± 0.0201 |
| SA-SL-20 | 4 (1 + 3) | 0.3399 ± 0.0104 | 0.2926 ± 0.0201 | 0.2765 ± 0.0019 | 0.4032 ± 0.0224 |
| SA-SL-100 | 1 | 0.3197 | 0.2893 | 0.2606 | 0.3788 |
| SA-MT-20 | 1 | 0.3384 | 0.3162 | 0.2734 | 0.4035 |
| Pratt-A-100 (U-Net VGG16, no weights) | 1 | 0.3386 | 0.3284 | 0.2535 | 0.4238 |
| Pratt-C-100 (U-Net VGG16, Pratt weights) | 1 | 0.3149 | 0.2975 | 0.2417 | 0.3881 |

Per-run SL-20 values: gaint 0.3059, 0.3679, 0.3786; cv02 0.3385, 0.3467, 0.3709, **0.2848** (seed 3, crack IoU 0.133), 0.3546. Seeds 0–2 run on both machines share initialisation and data stream, so pooled n overstates independence (`results_consolidated.md` header).

Welch tests on pooled runs (gaint `reports/stats_tests.md`; no multiple-comparison correction):

| Comparison | Test Δ, p | Val+test Δ, p |
|---|---|---|
| ALHVR vs SL-20 | +0.029, p 0.045 | +0.034, p 0.002 |
| MT vs SL-20 | +0.023, p 0.095 | +0.028, p 0.004 |
| ALHVR vs MT | +0.006, p 0.24 | +0.006, p 0.29 |
| SL-100 vs SL-20 | −0.005, p 0.68 | −0.018, p 0.066 |
| SA-SL-20 vs SL-20 | −0.004, p 0.78 | −0.021, p 0.135 |

Pilot runs on the buggy coupled augmentation (kept apart; do not compare): SL-20 0.3360, SL-100 0.3436, MT 0.3515, ALHVR interim at step 13,500 0.3294 (handoff 10-07 §6.1).

### 5.4 Loss-off controls: the unlabelled losses did nothing (cv02)

Old era. Source: handoff 10-07 §6.2; cv02 report.

| Arm | Seeds | Test defect mIoU |
|---|---|---|
| MT-20 | 0, 1, 2 | 0.3700, 0.3567, 0.3679 → 0.3648 ± 0.0071 |
| MT-20, λ = 0 | 0, 1, 2 | 0.3451, 0.3809, 0.3698 → 0.3653 ± 0.0183 |
| ALHVR-20 | 1, 2, 3 | 0.3599, 0.3704, 0.3762 |
| ALHVR-20, unlabelled weight 0 | 1, 2, 3 | 0.3757, 0.3708, 0.3461 → 0.3642 ± 0.016 |

- MT paired (λ 1.5 − λ 0, teacher): −0.000 ± 0.024. MT teacher − student at the final step: +0.000 ± 0.002 (the EMA adds nothing because the learning rate ends at zero).
- ALHVR paired (on − off): −0.016, −0.000, +0.030 → **+0.005 ± 0.023**.
- In both controls the unlabelled images still pass through the network and the unlabelled loss is exactly 0 on every logged step.
- Part of MT's gap over SL-20 is SL-20's seed-3 outlier: against SL-20 without seed 3 (0.3527), MT-20 is +0.012 and MT-20 λ = 0 is +0.013 (cv02 report, "MT EMA control").
- `arm_differences.md` (5 Oct) listed every code-path difference between SL-20 and the MT student at λ = 0: identical labelled images, order, geometric augmentation, class weights, loss, optimiser, initialisation; different: forward-pass size 8 vs 4, **BatchNorm statistics over a half-unlabelled batch** (in training and in the running statistics used at evaluation), the reported MT model being an EMA teacher, and shifted photometric draws (bitwise-equal labelled inputs in only 87 / 70 / 73 of 400 samples).
- **Reading at the time:** the SSL arms' gain over SL-20 did not come from their unlabelled losses. The leading hypothesis was BatchNorm batch composition ("4 + 4"). It was not shown in phase 1.

### 5.5 Batch 8 and the label sweep (supervised, old era)

Source: handoff 10-07 §6.3; gaint `reports/results_consolidated.md`, `day1.md` (6 Oct).

| Arm | Labelled images | gaint | cv02 | Pooled |
|---|---|---|---|---|
| SL-2-b8 | 9 or 10 | 0.1860, 0.1780, 0.2086 | not run | 0.191 ± 0.016 (3) |
| SL-5-b8 | 23 or 24 | 0.3531, 0.3202, 0.3218 | not run | 0.332 ± 0.019 (3) |
| SL-10-b8 | 47 | 0.3550, 0.3641, 0.3628 | 0.3421, 0.3428, 0.3743 | 0.357 ± 0.013 (6) |
| SL-20-b8 | 95 | 0.3218, 0.3652, 0.3500 | 0.3691, 0.3541, 0.3635 | 0.354 ± 0.017 (6) |
| SL-100-b8 | 478 | 0.3577, 0.3459, 0.3387 | 0.3500, 0.3412, 0.3393 | 0.346 ± 0.007 (6) |
| SL-20-b8, no class weights | 95 | 0.3110 | not run | 1 run |

- **Test defect mIoU was flat from 10% to 100% labels and broke at 2%** (handoff 10-07 §7, certain item 7).
- **The machines disagreed on batch 8:** gaint SL-20-b8 mean 0.346, cv02 0.362. cv02's summary: every arm whose BatchNorm sees 8 images lands at 0.362–0.370, every arm with 4 at 0.339–0.343; gaint does not show that. Batch 8 also doubles labelled presentations per step, so it cannot isolate BatchNorm (`arm_differences.md`).
- Gaint's tests on the batch-8 arms (Welch, uncorrected; `day1.md` 6 Oct, `stats_tests.md`): SL-100-b8 below MT-20 on val+test (−0.025, p 0.003) and below ALHVR-20 (test −0.025, p 0.020; val+test −0.031, p 9.6e-4); SL-10-b8 above SL-20 on val+test (+0.025, p 0.011). Only SL-100-b8 vs ALHVR-20 on val+test survives Bonferroni over the 38 tests then in the file.
- Class weights differ per subset (crack 0.559 / inactive 0.641 at 20%, 0.738 / 0.790 at 10%, 1.440 / 1.007 at 5%, 1.668 / 1.573 at 2%), so fractions were not compared at the same operating point. The seed-0 subsets hold inactive in only 4 of 47 (10%), 2 of 23 (5%) and 1 of 9 (2%) images, and 7 / 10 / 12 classes have zero pixels (gaint `reports/split_class_pixel_counts.md`).

### 5.6 Diagnostics (old era)

**Crack precision** (gaint `reports/precision_diagnostic.md`; handoff 10-07 §6.4): crack precision 0.22–0.35 and recall 0.67–0.73 in every class-weighted run. Example `alhvr_20pct_s1`: 70,626 true crack px, 143,570 predicted (handoffs; the generated table in `precision_diagnostic.md` gives 144,428); 85% of false crack pixels are true background; under `pvs3` crack IoU is 0.585 vs 0.30 standard. Relaxed precision (2 px) 0.49–0.75, so 25–51% of predicted crack pixels lie more than 2 px from any true crack. Without class weights: crack precision 0.63, recall 0.29, IoU 0.245 (32k predicted crack px vs 70.6k true; `day1.md`). A crack-logit bias chosen on val (subtract b, typically 1.25–1.75): SL-20 0.351 → 0.382 (+0.031), MT-20 0.368 → 0.387 (+0.019), ALHVR-20 0.369 → 0.381 (+0.013), SL-100 −0.005; on gaint the three arms end within 0.005 of each other, while cv02's report says "the SSL lead survives it" (cv02 gains SL-20 +0.019, MT-20 +0.016, MT λ = 0 +0.027, ALHVR +0.020; after the bias ALHVR 0.393, MT λ = 0 0.392, MT 0.381, SL-20 0.358, SL-100 0.338; cv02 report Block A). The machines read this differently and it was never reconciled.

**Threshold-free AP** (handoff 10-07 §6.5): crack: nothing beats plain supervised at batch 8 (cv02 SL-20-b8 crack AP 0.494 highest). Inactive on cv02: every arm that forwards unlabelled images is at 0.665–0.676 (loss on or off), every supervised arm at 0.616–0.637. SL-100 has the lowest crack AP on both machines. On gaint (`reports/threshold_free.md`, gaint runs only): Pratt-A (ImageNet VGG16 U-Net, one run) has the highest crack AP (0.499); gaint's batch-4 SL-20 has inactive AP 0.659, which blurs cv02's split; crack AP's seed sd is 0.39–0.46× that of crack IoU, so AP is the quieter crack metric, but not for inactive (1.07–1.22×).

**BatchNorm recalibration** (gaint `reports/bn_recalibration.md`, 7 Oct; no training): recomputing BN running statistics of supervised batch-8 models on their own labelled images, all 478 train images, or the external pool **never raised** mean `defect_miou` (SL-20-b8 and SL-10-b8, n 3 each; mean changes −0.002 to −0.022 over test and val+test; the external pool was worst). cv02's re-estimation (cv02 report Block E4; SL-20 and SL-20-b8, own labelled or all 478 train images) moved test by −0.004 to +0.008 and val+test by −0.005 to −0.023, so no consistent gain either. So BN *running* statistics do not explain the "4 + 4" inactive gain. BN statistics *during training* remained a candidate (published precedent: Yuan et al., ICCV 2021).

**Fit vs generalisation** (gaint `reports/fit_vs_generalise.md`; supervised batch-8 models, no augmentation at evaluation):

| Model | Crack IoU / P / R / AP on its own labelled train images | Crack IoU on test | Inactive IoU on own labelled | Inactive IoU on never-labelled train | Inactive IoU on test |
|---|---|---|---|---|---|
| SL-10 (47 images) | 0.325 / 0.33 / 0.95 / 0.64 | 0.304 | 0.881 | 0.340 | 0.417 |
| SL-20 (95) | 0.304 / 0.31 / 0.90 / 0.55 | 0.273 | 0.783 | 0.456 | 0.418 |
| SL-100 (478) | 0.239 / 0.26 / 0.72 / 0.37 | 0.283 | 0.539 | none left | 0.412 |

- **Crack was not fitted even on training images** (0.33 on the 47 images after 20,000 steps). This is the number behind the user's starting worry (§7).
- **Inactive was the opposite:** memorised on train (0.88) and poorly generalised; on train images never labelled, inactive IoU rose from 0.34 (10%) to 0.46 (20%), a real label effect that the 50-image test set does not show (test flat at 0.41–0.42).

**ALHVR region statistics and prototype diagnostic** (handoff 10-07 §6.8; phase 1 handoff §9e–9f):
- Pilot run (`pilot_alhvr_20pct_s0`, coupled augmentation, died at step 13,600; phase 1 handoff §9e): 73–76% of crack pixels sat in Ω3 and 6–7% in Ω1; DTCT's chosen teacher predicted background on 55% falling to 35% of the crack pixels it supervised (the "crack-erasing channel" of §11); pseudo-label accuracy Ω1 97%, Ω2 about 88%, Ω3 about 66%; λ had reached only 0.06.
- Training-time regions (`alhvr_20pct_s0`): γ rose 0.21 → 0.89 over training; Ω1 grew from 28% to 68% of pixels; Ω3 15–33%.
- On final weights over the 383 held-out train images: Ω3 is 15.6% of all pixels and holds **71% of true crack pixels** (119,384 of 168,511). DTCT winner accuracy in Ω3: crack 61.9%, inactive 51.2%, background 64.7%. 20.7% of Ω3 crack pixels are taught "background" (32.4% over the whole run in the logs).
- Cross-network prototypes label 4.6% of Ω3 crack pixels correctly (per-batch as in training 1.1%); own-network prototypes 43–49%, below the classifier head (62%). The relabel rule recovers about 6,600 crack pixels and mislabels about 12.5–12.6 million background pixels. No EMA or temperature fix rescues this: **prototypes are dead, a negative result with evidence**.

**External unlabelled pool** (gaint `reports/external_pool.md`, 6 Oct): 11,993 downloaded files; 55 dropped because the cell is a labelled image (48 train, 6 val, 1 test); **11,938 kept**, converted to 512 × 512 grayscale. Only ARTS (2,734) and CSIR (9,204); 43% of labelled train images (CFVS, BMRK, SDLE) have no counterpart. 57% of the pool (native 512 px) has about half the contrast of labelled images (median per-image sd 26–29 vs 43–50). No intensity harmonisation. Handoff 10-07 §3.3 says the Dropbox folder holds more than 150k cell images (the phase 1 answers say "about 12k"), and `external_pool.md` read an `_inventory.json` on gaint listing 15,388 entries, every pool file among them (the phase 1 answers believed it lost). The selection (DFS walk, per-leaf cap 2,500, `random.seed(42)`, round-robin) had no surviving manifest; the phase 1 answers note a pool of only CSIR/ARTS suggests a listing or capping effect, or that the share lacks other cell types, untested. See `03_datasets_and_splits.md`.

### 5.7 UCF-EL in phase 1 (old era)

**Supervised label sweep** (cv02, 6 Oct; 95,760 steps, batch 16, SGD poly lr 0.005; DeepLabV3+ R50; handoff 10-07 §6.9; cv02 report Block E):

| Labels | Images | n | 4-class mean | 3-class mean | Crack | Contact | Interconnect | Corrosion | Crack AP |
|---|---|---|---|---|---|---|---|---|---|
| 100% | 9,562 | 2 | 0.5364 ± 0.0042 | 0.4951 | 0.675 | 0.479 | 0.332 | 0.660 | 0.851 |
| 20% | 1,912 | 3 | 0.4932 ± 0.0045 | 0.4461 | 0.651 | 0.442 | 0.245 | 0.635 | 0.807 |
| 5% | 478 | 3 | 0.4146 ± 0.0017 | 0.3953 | 0.618 | 0.404 | 0.165 | 0.472 | 0.766 |
| 1% | 96 | 3 | 0.2265 ± 0.0017 | 0.3021 | 0.529 | 0.351 | 0.026 | no labelled examples | 0.690 |

UCF-EL has a clean label gap with seed sd 0.002–0.005 (about ten times tighter than BenchmarkEL). The machines agree on SL-20 (gaint 0.491 vs cv02 0.493). The earlier impression "no gap at 20%" came from one SL-100 run at fewer steps and was wrong. The 1% subset has no corrosion image.

Gaint's earlier UCF supervised runs (3–4 Oct; handoff 10-07 §6.9; phase 1 handoff §7b): SL-20 at 12,000 steps 0.448; FSL 100% at 59,760 steps 0.497 (Fioresi 4-class 0.482: reproduced); SL-20 step-matched at 95,760 steps 0.501, 0.486, 0.487 → 0.491 ± 0.009. Detail in `05_literature_and_baselines.md`.

**PV-S3:** reimplementation v1 0.200, v2 0.276 / 0.283, v2 + per-class cap 0.418, against step-matched SL 0.491 ± 0.009; released code as shipped 0.050 standard / 0.828 pvs3 (never predicts background). Full detail in `05_literature_and_baselines.md` §4.2.

**Mean Teacher (SemiCE) on UCF-EL at 5% and 1%** (cv02, launched 7 Oct, finished 8 Oct; cv02 report table generated 8 Oct 10:10 UTC; 16 labelled + 16 unlabelled, 95,760 steps, EMA teacher evaluated, paired λ = 0 controls):

| MT arm | vs | 4-class mean | 3-class mean | Crack | Contact | Interconnect | Corrosion |
|---|---|---|---|---|---|---|---|
| MT 5% | SL 5% (paired, n 3) | −0.0913 ± 0.0362 | −0.0507 ± 0.0366 | −0.0481 ± 0.0162 | −0.0386 ± 0.0075 | −0.0653 ± 0.0945 | −0.2130 ± 0.0845 |
| MT 5% | MT 5% λ = 0 | −0.0688 ± 0.0531 | −0.0349 ± 0.0407 | −0.0458 ± 0.0175 | −0.0345 ± 0.0042 | −0.0245 ± 0.1062 | −0.1704 ± 0.1008 |
| MT 5% λ = 0 | SL 5% | −0.0225 ± 0.0173 | −0.0157 ± 0.0113 | −0.0023 ± 0.0048 | −0.0041 ± 0.0045 | −0.0408 ± 0.0257 | −0.0426 ± 0.0560 |
| MT 1% | SL 1% | −0.0742 ± 0.0275 | −0.0990 ± 0.0367 | −0.1745 ± 0.0570 | −0.1165 ± 0.0438 | −0.0059 ± 0.0239 | n/a |
| MT 1% | MT 1% λ = 0 | −0.0521 ± 0.0216 | −0.0694 ± 0.0288 | −0.1100 ± 0.0342 | −0.0820 ± 0.0485 | −0.0163 ± 0.0170 | n/a |
| MT 1% λ = 0 | SL 1% | −0.0222 ± 0.0074 | −0.0295 ± 0.0099 | −0.0645 ± 0.0270 | −0.0344 ± 0.0055 | +0.0103 ± 0.0076 | n/a |

All MT arms are below supervised and below their own loss-off controls. These runs used SemiCE, which P2 later showed is not a valid consistency loss, so **they test SemiCE, not Mean Teacher**, and are on the invalid list (memory `mtp-el-ssl-project.md`). The phase 1 answers (item 3) say that author had no record of these runs or of any decision made from them.

### 5.8 SA U-Net++ redone correctly (phase 1)

Corrected rerun on BenchmarkEL with current code (old era): SA-SL-20 pooled 4 seeds 0.3399 ± 0.0104 (val+test 0.2926 ± 0.0201) vs SL-20 0.3435 ± 0.0329; **no effect** (p 0.78 test, 0.135 val+test). SA-SL-100 0.3197 and SA-MT-20 0.3384, one run each (handoff 10-07 §6.11; phase 1 handoff §7d).

### 5.9 Where phase 1 stood on 7 Oct (handoff 10-07 §1, §7, §11)

"On BenchmarkEL no unlabelled loss has shown any effect, and label count does not move the score between 5% and 100%. The crack class cannot even be fitted on training images. UCF-EL does show a clean label gap (0.54 at 100%, 0.41 at 5%, 0.23 at 1%) with very low seed noise, so the SSL question moved there." Its own opinions (§11): BenchmarkEL at ≥ 10% is the wrong place to test SSL; BenchmarkEL has two separate problems (crack fit-limited, inactive generalisation-limited); pseudo-label methods are structurally weak for these defects; published SSL gains are not trustworthy as published; the most defensible thesis is a careful negative-plus-diagnosis study; the most promising use of unlabelled data is probably not pseudo-labelling (self-supervised pretraining, or UCF-EL → BenchmarkEL supervised pretraining, both untested); ALHVR has not had a fair test (§9.1).

**§9.1 (found while writing the 10-07 handoff):** ALHVR's λ reaches 0.1 only at the final step while Adam's cosine learning rate reaches zero, so for most of training the unlabelled terms contributed a few percent of the gradient at most. "ALHVR equals ALHVR with losses off" is close to true by construction and does **not** show DTCT is useless. Mean Teacher was not affected (λ = 1.5 from step 4,000). The audit (`analysis/alhvr_audit.md` §1) quantified this on 8 Oct.

---

## 6. Bugs and traps found in phases 0–1 (all silently corrupted results)

From the phase 1 handoff §8 and handoff 10-07 §4.3.

| # | Bug or trap | Effect | Status |
|---|---|---|---|
| 1 | GaussNoise 16× too strong: albumentations 2.x renamed `var_limit` to `std_range` and silently ignores the old argument (measured σ ≈ 68 instead of ≈ 4 on 0–255; the 2 Oct setup check measured 51–86 against an intended 2.9–6.7, "about 10–15×") | erases cracks; invalidates the phase 0 SA ablation and SSL sweep | fixed (`std_range=(0.0124, 0.0277)`) |
| 2 | fp16 autocast NaN in DeepLabV3+/R50 within about 2 SGD steps | training fails | use bf16 |
| 3 | metrics code indexed a 5-class tensor with 24-class defect indices | CUDA device assert | fixed |
| 4 | runner-script self-deadlock: a `pgrep -f "run_x.sh"` guard matched its own parent | 80 min idle GPU | use `[r]un_x.sh` patterns |
| 5 | smp needs H, W divisible by 16 | Fioresi crop 250 became 256 | noted |
| 6 | strong augmentation applied without the paired mask | collapsed an earlier SSL sweep | geometry shared; strong aug photometric only |
| 7 | coupled augmentations (H and V flips fired together; blur and noise together; DataLoader workers shared one augmentation seed) | **pilot-era numbers are not comparable** | fixed 3 Oct |
| 8 | worker-seed bug found in the phase 1 foundation rebuild | "confirmed old results doubly invalid" | fixed |
| 9 | class weights computed over test labels (leak); Fioresi upstream validates on test; UCF has no val | leakage | weights recomputed from the labelled subset |
| 10 | full deterministic mode 5× slower | – | used only for the resume test |
| 11 | resume after crash | tested bit-exact for all 7 trainers | built |
| 12 | `scikit-image` 0.26: `remove_small_objects` semantics inverted | – | noted |
| 13 | disk full (`ENOSPC`) breaks tools | – | `save_every == total steps` |
| 14 | `.gitignore` rule `data/` also matched `src/data/` | first import dropped the data-loading code | fixed before push |
| 15 | weighted CE on CUDA not deterministic | small run-to-run differences | reimplemented |
| 16 | silent fallback: a missing split file trained on all 582 images, test included | possible test leakage in old code | hard error since 2 Oct |
| 17 | old loader expected colour masks; the shipped index masks, symlinked directly, turned every non-background class into ignore (24.6% of pixels) | only background would be learned | colour masks generated 2 Oct; the rebuild reads index masks directly (`reports/summary.md`; §5.1) |

---

## 7. The user's starting worry and what answered it

On 7 Oct (23:37 IST) the user asked to "read the markdown" (the 10-07 handoff) and pasted this note (quoted from `sources/chat/user_messages_2026-10-07_to_11.md`, typos as written): "were workin gon this MTP Project, i feel lost, coz it trained on 47 images and tested on sam e47, to get 0.3 iou on cracks, definitely dsomething wrong, my goal is to work son something sinspired by ALVHR to focus the rare classes, be skeptic ... analysis first, the datasets, the mmodels, the issues ... i strongly doubt there are some bugs in the trainning(minor misconfigurations) causing the unlabelled losses having zero effect".

They then set the pace (23:55 IST): "lets take our time, understand teh situation, the dataset, the prblem more clearly and grounded, then will, like find out the issues the existing paers in this fiedl are having", with the three-part thesis plan, and asked for P1 and P2 to be run while they read the literature (8 Oct 00:37 IST: "add the ssh allow rules and run P1 and P2, till then ill read the literature part").

**What answered "47 images, 0.3 crack IoU":** P1, the overfit check (8 Oct; `results/p1/README.md`; protocol locked before running). Ten crack-containing train images, 3,000 steps, scored on the same images:

| Arm | Setting | Crack IoU | Crack AP |
|---|---|---|---|
| A | weighted CE, no augmentation, bf16 | 0.612 | 0.929 |
| B | plain CE, no augmentation | 0.677 | 0.884 |
| C | plain CE + soft Dice, no augmentation | **0.861** | 0.953 |
| D | plain CE, fp32 | 0.605 | 0.838 |
| E | weighted CE, **training augmentation** | **0.381** | 0.587 |

Verdict: **not a code or data bug** (masks aligned exactly; bf16 equals fp32 over 3 seeds: 0.668 ± 0.031 vs 0.656 ± 0.048). Training augmentation was the largest single factor capping crack fit (AP 0.93 without, 0.59 with); class weights cost precision but were not the main cap; CE + Dice fits crack to 0.86, so label inconsistency does not cap fitting. Detail in `08_experiments_P1_P7_diagnostics.md`.

**What answered "unlabelled losses have zero effect, maybe a bug":**
- No wiring bug was found in the SSL losses (`analysis/alhvr_audit.md` §7: gradient path, sign, masks, regions, two optimisers, loss-off control all correct).
- ALHVR: the loss was barely applied (λ × learning-rate schedule; §5.9 above).
- Mean Teacher: P2 (8 Oct; `results/p2/README.md`) found SemiCE as implemented is **not a valid consistency loss**: 100% of unlabelled pixels have ≥ 2 positive classes (background flagged positive on 98.9% of pixels, padding 92.1%, crack 20.3%), so the target is incoherent. The gradient was real (0.25 ± 0.35 of the supervised gradient, only 0.041 along the softmax-invariant direction) but nearly orthogonal to the supervised one (cosine 0.07). So **every MT result run with this loss tests SemiCE, not Mean Teacher** (BenchmarkEL 20%, the external-pool queue, UCF-EL on cv02).
- Side finding of P2 that shaped later work: a correct confidence-thresholded rule (max-prob ≥ 0.95) would put crack in only 0.024% of confident pixels, about 8× under its labelled share. That is the rare-class problem in SSL, measured on our data.
- Our "SemiCE" also deviated from PV-S3's released SemiCE (per-class BCE on raw logits vs softmax CE on probabilities; `analysis/alhvr_audit.md` §2; `05_literature_and_baselines.md` §4.2).

---

## 8. The analysis-first restart (7–8 Oct)

The user asked for analysis before any new method. What was produced, in order (git log of `~/mtp/research`):

| Commit | Time (IST) | Output |
|---|---|---|
| `f9708c0` | 7 Oct 23:59 | research repo initialised; P1 and P2 protocols locked before running; ALHVR audit; paper notes |
| `980e6af` | 8 Oct 00:12 | literature survey (69 verified sources), reading list, per-topic notes; Fioresi 57.3 correction |
| `aa1135b` | 8 Oct 00:24 | first-hand BenchmarkEL analysis (inventory, crack geometry, 1 px IoU ceiling, annotation consistency, duplicates, class-weight operating point) |
| `727f081` | 8 Oct 00:27 | situation report |
| `771240a` | 8 Oct 00:51 | P2 result |
| `fa373ed`, `d05091e` | 8 Oct 01:54, 02:52 | P1 result and replicates |
| `0deaf3c`, `d92f582` | 8 Oct 12:27–12:28 | UCF-EL first-hand analysis; situation report section 9 |

The situation report of 8 Oct (`to_human/situation_report_2026-10-08.md` §0) gave five bottom-line points:
1. **On BenchmarkEL, strict crack IoU is already where label noise dominates.** One image appears twice in train with two independent masks: their crack IoU is 0.257 (tolerance F1 0.82 at 2 px). A perfect mask shifted by 1 px scores 0.47–0.56. Our models scored 0.27–0.35. So ±0.03 strict-IoU differences between methods cannot be interpreted for crack [inferred].
2. Crack labels are a median 1.75 px wide on a visible line about 4 px wide, within 1 px of the darkest pixel only 48% of the time, dotted along continuous cracks in 22 images; class weights make the loss prefer crack once p(crack) > 0.05–0.06 (later revised by P1: augmentation is the larger factor for fitting).
3. **Neither SSL method had actually been tested** (ALHVR loss near zero under the LR schedule; MT with a nonstandard loss and mild perturbation; CutMix existed but was never called). "Unlabelled losses have no effect" was therefore not a finding.
4. Inactive is the opposite problem: consistent labels (duplicate pair tolerance F1 0.92; 1 px shift 0.89–0.94), memorised on train, poor generalisation, a real label effect hidden by the 50-image test set.
5. The field's evaluation is weak (hand-picked test sets, validation on test, conventions that drop background or take medians, leakage, under-trained baselines, single runs, no thin-structure metric); under Pratt's own rule there is no reproduction gap.

The UCF-EL analysis added: validation = test in the official `train.py`; 25–44% of test cells have the same physical cell (another stress stage) in train; UCF "crack" is a region class (1 px IoU ceiling 0.95 vs 0.50–0.56 on BenchmarkEL); the 100% → 1% label gap is 64–78% interconnect and corrosion. UCF could carry a label-efficiency claim only after a physical-module-disjoint re-split (situation report §9; `data_analysis/ucf_el_report.md`; see `03_datasets_and_splits.md`).

**The held queue.** The gaint external-pool MT queue (`mt_20pct_ext_s0..2` and λ = 0 controls, `consistency: semi_ce`) was armed to start about 01:08 on 8 Oct. Because it would test the invalid SemiCE, it was held. The assistant's own attempt to hold it (kill plus crontab edit) was denied by the auto-mode permission check as interfering with workloads; the user ran the hold command themselves (logged 01:18:25; crontab now relaunches only `lowlabel_20261006`). It has stayed held and untouched since, by the user's rule (relaunch command: `bash scripts/resume_queues.sh extpool_20261007`).

From 10 Oct the directions survey (`05_literature_and_baselines.md` §18) and the P-series proper followed: P3–P5 probes, P6 corrected supervised baseline on revised labels, then the SSL series. See `08_experiments_P1_P7_diagnostics.md` onward and `12_decisions_log.md`.

---

## 9. The 11 Oct exchange: the handoffs and the user's answers about the older work

After P7–P10 had shown no unlabelled loss beating supervised training (P11 and P12 were still running), the user wrote (11 Oct, 11:24 IST): "cant believe bro, supervised beating ssl, hows that possible, so many papers showed it, we doing something wrong? be skeptical, work like 11years experienced and look if anything wrong with our experiment, even earleir I tried in the SA SSL unetpp which had raised the iou, seems contradicting". They then pasted the phase 0 and phase 1 handoffs ("unfortunately most of the codes and results we lost coz of user reset ... first we tried SA SSL on unet++ and then we reproduced all the paers ... now tell me if we are wrong at something now"). Questions were batched and asked; the user relayed answers from the phase 1 author, noting "the answers were from phase1 work, it gently declined all the phase0 answers which cant answer anymore".

**The phase 1 author's answers (pasted 11 Oct; they answered only what they had worked on):**

1. **"SA SSL raised IoU."** Never reported by them. The likely source is a misreading of a table relayed on 4 Oct that listed **SA SL-20% seed 0 only**: final-step test 0.338 and best-val-step test 0.301. Both numbers belong to one arm at two checkpoints; they are not SA-MT vs SA-SL. The older SA ablation (0.2028 vs 0.1792; SSL-20% 0.2580) predates the GaussNoise fix and is invalid. SA-SL-20% pooled over 4 seeds showed no effect (0.3399 vs SL-20 0.3435). No SA-MT result was seen by them (one run exists: 0.3384, §5.3). Nothing known about the TF-era code.
2. **Where SemiCE came from.** Unknown to them. Jha et al.'s PV-S3 describes SemiCE as CE on pseudo-labels with two thresholds; their UCF reimplementation took t_pos 0.6, t_neg 0 from that. Their notes also link SemiCE with Gangopadhyay's SA-UNet++ (Mean Teacher + SemiCE). No record of an advisor suggesting it. On UCF, their reimplementation failed through rare-class pseudo-labels (99.4% of pixels pass t_pos 0.6; corrosion over-predicted 23×); a per-class share cap fixed corrosion (0.067 → 0.631), which points at thresholding, not necessarily the SemiCE idea.
3. **The 6–8 Oct UCF MT runs (1% and 5%).** No record of them or of decisions made from them; their last session ended 6 Oct 00:04 IST.
4. **Phase 0 decisions.** Unknown to them, as is the P-numbering. They knew the dual mandate and the resolution "full-accuracy headline, lightweight variant secondary"; no record of "WattCycle pilot first". A three-way architecture comparison (SA-UNet++, UNet++ R34, DeepLabV3+ R50) had been dispatched earlier; its results were never seen. The old code trained from scratch with no pretrained encoder, while published work reports much higher crack IoU with pretrained encoders. Their data supported "supervised and architecture before SSL changes" (SL-100 = SL-20; MT with loss off = MT; crack over-prediction the measured bottleneck), leaving the order to the user.
5. **Unlabelled data.** The share held about 12k images; their selection gave 11,993 after failures; they never saw 11,938 (presumably post-filtering). The share leaks labelled images by filename (filter by cell ID). A pool with only CSIR/ARTS suggests a listing or capping effect, or that the share lacks other cell types; the cheap test is to re-walk the share listing without downloading (`_inventory.json` was lost and must be regenerated).
6. **Advisor directives.** About 2M params in their notes; the ~4M on the poster came from the user. No deadline known. MoE listed as an advisor directive in their notes, but the user had called it an uncertain suggestion; their position: gate it on a specialist-vs-generalist diagnostic (about 2 GPU hours). No report due date known.

**What the 11 Oct audit concluded about the old work** (session record; memory `mtp-el-ssl-project.md`):
- No SSL code bug. The P-series handicaps came from the labelled view (fixed by P11's matched view), BatchNorm mixing (P13 separate forward) and weak perturbation (P13 CutMix).
- The old SA "gain" was a checkpoint artefact (one arm at final vs best-val), not an SA effect.
- Old MT, UCF and ALHVR results used invalid SemiCE or equal their λ = 0 controls.

**User decisions that came out of this exchange** (11 Oct, after the batched questions): "framing depends on final results, no presumptions, ever"; cv02/gaint allocation "your call"; extended test set: "conside rit"; WattCycle data: none; "youve 1 day for the work then ill startr on ppt"; model size "not a constraint even 5M works"; power loss "will work on that later, not part of this project unless we get some valid data". Recorded in `12_decisions_log.md`.

**Standing rules carried over from the handoffs** (memory `mtp-el-ssl-project.md`; phase 1 handoff §16): match optimiser steps across arms; final-step weights primary (best-val on 54 val cells flips signs); never compare arms across machines; seeds at least 3, and 5–8 for effects < 0.05; one change per arm; old-era numbers in separate tables from the P-series. Detail and how they were applied: `07_methodology_rules_and_statistics.md`.

---

## 10. What was found invalid or superseded, and why

| Old result or claim | Why invalid or superseded | Evidence |
|---|---|---|
| Phase 0 SA ablation "removing SA helps" (0.2028 vs 0.1792) | predates the GaussNoise fix (noise erased cracks); worker-seed and coupled-augmentation bugs | phase 0 / phase 1 handoffs; §6 |
| Phase 0 SSL sweep (20%: 0.2580, 10%: 0.1323) | same | same |
| "SSL +7.4" (phase 0) | 8× optimiser-step mismatch | phase 0 handoff |
| "SSL doubles performance 10.83 → 21.19" (UCF, early) | both runs under-trained | phase 1 handoff §7a |
| Pilot-era BenchmarkEL runs (2 Oct, coupled augmentation, fp16) | not comparable with current-code runs | handoff 10-07 §4.3 |
| BenchmarkEL MT-20 gain over SL-20 (+0.023 test, +0.028 val+test) | **SemiCE is not a valid consistency loss (P2)**; MT equals its λ = 0 control (−0.000 ± 0.024) | `results/p2/README.md`; §5.4 |
| ALHVR-20 gain over SL-20 (+0.029 test, p 0.045) | equals its loss-off control (+0.005 ± 0.023); the loss was barely applied (λ × cosine LR); the gain did not come from the ALHVR losses (batch composition is the leading hypothesis, not shown) | §5.4, §5.9; `analysis/alhvr_audit.md` §1 |
| "ALHVR +0.064 over SL-20" | measured against the worst SL seed | phase 1 handoff §13 item 14 |
| "SSL beats supervised (p ≈ 0.05, 0.004)" | premature; unlabelled-loss effect not measured | phase 1 handoff §13 item 11 |
| UCF MT 5% / 1% (cv02, SemiCE) | tests SemiCE; below SL and below λ = 0 controls | §5.7 |
| External-pool MT queue (gaint) | would have tested SemiCE; held, never run | §8 |
| PV-S3 "SSL 46.4" record (lost pipeline) | not reproduced by v1 or v2; old code lost | phase 1 handoff §7b |
| "SA gating hurts" (old memory note) | retired; corrected rerun shows no effect | §5.8 |
| "No UCF gap at 20%" | from one SL-100 run at fewer steps; the gap is 0.043 | handoff 10-07 §6.9 |
| "Rule A Set C 0.283 is the paper's best 0.28" | the paper's 0.28 is DeepLabv3+ 4c; claim to avoid | phase 1 handoff §7b; `analysis/papers_metrics.md` |
| "The 12k unlabelled set cannot be reconstructed" | it can be re-downloaded (method documented) | phase 1 handoff §13 item 15 |
| "Prototype per-batch divides by zero / NaN" | the code gives zero vectors | phase 1 handoff §13 item 9 |
| "PV-S3 collapse caused by strong-view supervised loss" | only −0.045; real cause is rare-class pseudo-label over-prediction | phase 1 handoff §13 item 12 |
| "EMA prototypes in Ω3 could be the most important change"; "add clDice (M5)" | both refuted by measurement (prototypes dead; bottleneck is over-prediction, not recall) | phase 1 handoff §11, §13 item 10 |

**What remains valid from the old era** (useful facts, still old-era numbers): the metric-convention analysis of the four papers; the PV-S3 released-code findings (`ignore_index = 0`, split leakage); the UCF-EL supervised label sweep; the fit-vs-generalisation facts; crack over-prediction under class weights; the BN running-statistics result; the prototype negative result; SA gate no effect; data facts about both datasets.

---

## 11. Proposal history (what was alive and dead before the P-series)

From the phase 1 handoff §11.

| Idea | Status on 6 Oct |
|---|---|
| Mandatory ALHVR fixes (τ, softmax sharpening, skip absent classes) | needed if CG-CPCL were used; CG-CPCL itself looked inert |
| **M2' class-prior-aligned routing** (per-class γ_k + two-sided pseudo-label share control 0.5×–2× of labelled share) | **strongest evidenced**: UCF corrosion collapse fixed by a one-sided cap (0.067 → 0.631); crack is under-labelled on BenchmarkEL |
| M3 EMA prototypes / prototype-guided DTCT | **dead** (prototype diagnostic) |
| M4 asymmetric DTCT (background label needs both networks to agree) | untested; targets the 35–55% crack-erasing channel |
| M5 clDice topology loss | dropped: bottleneck is over-prediction, not recall |
| M1 defect-aware sampling | deprioritised: the BenchmarkEL pool then was only 383 images |
| MoE (advisor) | gated on a specialist diagnostic (~2 GPU hours); standard load balancing balances pixel counts, i.e. background |
| ALHVR attribution runs (without CG-CPCL, without DTCT, λ 0) | only λ 0 ran |
| Pretrained backbone (SegFormer/DINOv2), pruning/INT8 for Jetson | future work |

"Current direction (set by the data)" on 6 Oct: fix the supervised recipe first (class-weight over-prediction, normalisation, batch composition), then test SSL only where a label gap exists (SL-10%, UCF-EL at 1–5%, or a genuine ~12k unlabelled set). Success criterion fixed in advance: full method beats step-matched SL by more than seed noise (Welch p < 0.05 at ≥ 5 seeds, and rare-class IoU), at ≤ 5% labels.

What the P-series actually did with this: the supervised recipe was fixed in P6 (revised labels, label-safe augmentation, ImageNet ResNet-34, CE + Dice: the "L3" base); SSL was tested at 10% (P7–P9, P11), 5% (P10, P12, P13) and later 20/50/100% (P16, added on the user's request). See `08`–`10` and `12_decisions_log.md`.

---

## 12. Corrections logs from phases 0–1 (errors made, so they are not repeated)

From the phase 1 handoff §13 and handoff 10-07 §10. The pattern behind them is the meta-lesson: "every 'the method differs' explanation turned out to be a comparison-convention or control mistake. Check conventions, steps, and controls before believing a method difference."

By the phase 1 chat (selection):
- "Fioresi shortfall of 7.1 is real": was 4-class vs 5-class mixing.
- "Width explains Pratt 13–16 vs Jha 67–88": overclaim (Jha's own CSB-S1 results contradict it); annotation width is one of three confounders (width, metric, absent-class rule).
- "All four baselines reproduce": SL 20% compared across metrics.
- "SL best over budgets": withdrawn (selection on test).
- "SSL gain disappears" stated before seeds; "reverses" too strong at one seed.
- ALHVR described as built on CPS with Ω1 pseudo-labels: wrong.
- Told Claude Code to switch the MT labelled view to weak: wrong rule; the rule is "the labelled loss gets the augmentation of the matching SL arm".

By Claude Code in phase 1 (caught in review): "we beat Pratt 2×" (empty-image rule); "equal budget" off by 8× in steps; "UCF val stays clean" (FSL trains on all 9,562; the SSL pool contains val); "every run far below Jha's 67–71" compared unlike arms.

By the 10-07 handoff author (handoff 10-07 §10): called ALHVR "CPS plus modules"; specified the region test wrongly (per-image, 75%, clean confidence vs the code's batch, 80%, perturbed); chose labelled batch 4 without checking BatchNorm; called false crack "a thick halo" (half is elsewhere); declared batch size ruled out from three runs on one machine; parked the 12k external pool on day one; suggested BN running statistics (ruled out); did not ask for an overfit check on day one; read "ALHVR equals loss-off" as evidence against the modules for two days without checking the logged λ; several times stated a leading hypothesis as if it were the finding. **The user's "don't presume" rule exists because of this.**

---

## 13. Open items inherited from phase 1 and what became of them

From handoff 10-07 §12–13 and phase 1 handoff §17; fate from the session record and later docs.

| Open item (7 Oct) | Fate |
|---|---|
| Overfit check (asked for twice, never run) | done as P1 (8 Oct) |
| ALHVR / DTCT with a fair weight schedule | not run; the P-series used Mean Teacher with tolerant pseudo-labels instead |
| Self-supervised (MIM) pretraining on the unlabelled cells | not run in P1–P16 |
| Pretrain on UCF-EL, fine-tune on BenchmarkEL | P15 (gaint; pending at 11 Oct ~22:00) |
| Evaluate on more than 50 images | E1's 106-cell unseen-module extension (`10_experiments_P13_P16_E1.md`) |
| More labelled subsets (split seeds 1, 2) | not done; one labelled split (seed 0) throughout (see `13_problems_pitfalls_open_issues.md`) |
| BN mixing controls | P11–P13 (matched view; separate-BN forward) |
| Pretrained encoder for the BenchmarkEL model | P6 (ImageNet ResNet-34 U-Net++) |
| UCF module-disjoint re-split | no record of it being done |
| Re-download the genuine unlabelled set with cell-ID filtering | the 11,938-cell pool was used as converted (P9 onward); no new download |
| Rebuild post-processing (Subpath A) and Köntges grading | not rebuilt (power loss out of scope unless valid data) |
| Rotate the Dropbox app secret (pasted in chat on 2 Oct) | still a standing instruction; never expose it |
| Who shuts gaint down (needs sudo) | unknown |
| Copy cv02 patches to gaint | later experiments deploy one git commit per worktree to both machines (`14_code_and_infrastructure.md`) |
| Institute report template and page limit | never given |

---

## Related docs
- `00_START_HERE.md` (index)
- `01_project_overview_and_scope.md` (mandate, three-part plan, scope decisions)
- `03_datasets_and_splits.md` (BenchmarkEL, UCF-EL, external pool facts referenced here)
- `04_glossary_and_naming.md` (SemiCE, Ω regions, DTCT, λ, loss-off control, run names)
- `05_literature_and_baselines.md` (the four reproduced papers in detail; ALHVR; the directions survey)
- `07_methodology_rules_and_statistics.md` (standing rules that came out of these failures)
- `08_experiments_P1_P7_diagnostics.md` (P1 and P2 in full)
- `12_decisions_log.md`, `13_problems_pitfalls_open_issues.md`, `14_code_and_infrastructure.md`
