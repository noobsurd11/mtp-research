# 04 Glossary and naming

**What this covers.** Every term, acronym and piece of jargon used in this project's notes, protocols and results, in alphabetical order. Each entry gives a plain definition, then how this project uses the term ("Here"), then where to look ("See"). The second half decodes the run and arm names (`p13_CsM_5pct_s3` and so on), with a table of every arm from P6 to P16. If a term in any other handbook file is unclear, it should be here; if it is not, check the sources below and add it.

**Sources**
- `protocols/P1_*.md` to `protocols/P16_*.md` (arm definitions, rules, metric choices)
- `results/*/README.md`, `results/e1/README.md` (metric definitions, numbers)
- `scripts/ssl_rules.py`, `scripts/per_image_analysis.py`, `scripts_cv02/e1_aggregate.py`, `scripts_gaint/rescore_label_versions.py` (exact metric and rule code)
- `data_analysis/benchmark_el_report.md` (class ids, sources, crack width)
- `to_human/proposal_reframe_2026-10-11.md` (O1-O3, E1-E6 numbering)
- `~/mtp/MTP_session_handoff_2026-10-07.md` and the phase 0 / phase 1 handoffs the user pasted on 11 Oct (copy: `sources/chat/phase0_phase1_handoffs_pasted_2026-10-11.md`)
- gaint code: `/home/noob/work/el_p13/src/trainers/ssl_ops.py` (CutMix, `frozen_bn_stats`)

Times are IST (UTC + 5:30) unless marked UTC. Conventions used below: "P-series" means the experiments P1 to P17 run from 8 Oct 2026 on. "Old era" means everything before that (phase 0 and phase 1). Class ids are BenchmarkEL ids: background 0, padding 7, ribbons 4, busbars 9, crack rbn edge 10, inactive 11, crack 14, gridline 15 (`data_analysis/benchmark_el_report.md`; phase 1 handoff section 4).

---

## Part 1: Glossary (A to Z)

**A (arm letter).** Supervised reference arm, no unlabelled data. See Part 2.

**A5c.** The cv02 supervised 5% arm. In P12 it is `p12_A_5pct` seeds 0-2. In P13 and later it is the pooled arm `p12_A_5pct` s0-2 + `p13_A_5pct` s3-4 (5 seeds; pooled with `--merge` in the analysis scripts). The "c" means cv02, to separate it from P10's gaint A5. See `protocols/P13_cutmix_separate_bn.md` Amendment 1, `results/p13/README.md`.

**Absent-class rule (A, B, C).** How a per-image metric treats a test image in which the class does not appear. Pratt et al. score each image separately and take the median. Rule A excludes images without the class; rule B scores them 0; rule C scores 1 if the model also predicts nothing. *Here:* rule B reproduces Pratt's numbers; under rule B any class present in fewer than half the test images has median 0 by construction. Old-era reproduction topic only. *See:* phase 1 handoff section 5; `analysis/papers_metrics.md`.

**Adam, cosine schedule, warm-up.** The optimiser and learning-rate schedule. *Here (P-series):* Adam, learning rate 1e-3, weight decay 1e-4, 200-step warm-up, then cosine decay to 0, gradient clipping at 1. *See:* `protocols/P6_corrected_baseline.md` "Fixed for all arms".

**ALHVR.** "Adaptive Learning of High-Value Regions", Lei et al., ICCV 2025: a semi-supervised method with two independently trained networks. Each unlabelled pixel is put in a region by confidence against a batch threshold γ: Ω1 (both networks confident, no unlabelled loss), Ω2 (one confident; trained with CG-CPCL, a prototype-based loss), Ω3 (neither confident; trained with DTCT, where the more confident network teaches the other). *Here:* the user's starting inspiration ("something inspired by ALVHR to focus the rare classes", 7 Oct). It was ported in the old era; its gain over SL-20 equals its λ = 0 control, so the gain is batch composition, not the method (memory note `mtp-el-ssl-project.md`). P5 measured rare-class pseudo-label precision inside its regions. The proposed tolerant pseudo-label loss was "rarity-routed" in its spirit. *See:* phase 1 handoff section 10; `analysis/alhvr_audit.md`; `protocols/P5_region_pseudolabel_precision.md`.

**Amendment.** A change to a locked protocol made after locking. Every amendment states what results, if any, had been seen when it was written. *Here:* e.g. P13 Amendment 1 (5% only, Ds5 dropped, A5c becomes the loss-off control), P13 Amendment 2 (BsM5 seeds 3–4, added after the 3-seed result was seen, to meet the 5-seed rule), P16 Amendment 1 (Part B, the SSL arms, locked after the user chose "pick CutMix on P13 val"), the E1 amendment (ignore mask for four defect types). *See:* the "Amendment" sections in `protocols/`, `results/e1/README.md`; `07_methodology_rules_and_statistics.md`.

**AP (average precision), binned pixel AP.** A threshold-free score: rank every pixel by the model's softmax probability for a class and measure how well the ranking separates true pixels from the rest (area under the precision-recall curve). *Here:* computed over 1,000 uniform probability bins, dataset-level (`scripts_gaint/rescore_label_versions.py`). It was the primary metric of P6 and P7 only. It was demoted to secondary from P8 because many models put a large share of true pixels into the lowest bin, where AP cannot rank them (see **bin-0 share**). *See:* `protocols/P8_tolerant_pl_on_l3.md` "Metrics"; `results/p6/README.md` "Exploratory 1".

**Area error (inactive area error).** Per cell, the absolute difference between predicted and true inactive area, in percentage points of the cell's non-padding area; mean over all cells. E1 metric. *See:* `results/e1/README.md`.

**Argmax vs threshold.** Argmax: each pixel gets the class with the highest predicted probability. Threshold: a class is predicted when its probability passes a chosen cut. *Here:* every P-series IoU and relaxed-F1 number uses argmax; no thresholds are tuned. Old-era work found that thresholds picked on val (a "crack-logit shift") changed arm rankings, which is one reason argmax is fixed. *See:* phase 1 handoff section 9d; `protocols/P8_tolerant_pl_on_l3.md`.

**Arm.** One experimental condition (a fixed recipe), trained with several seeds. *Here:* named by letters (Part 2). An experiment compares arms that differ in exactly one thing.

**Background, head classes, rare classes.** Background (class 0) and the frequent structural classes (padding, ribbons, busbars, spacing) are "head" classes: most pixels. Crack (14) and inactive (11) are the "rare" classes this project targets. Crack is 0.186% of train pixels; background 69.2%, padding 17.3% (`data_analysis/benchmark_el_report.md` section 0). *Here:* the tolerant pseudo-label loss routes rare and head classes differently.

**BatchNorm (BN).** A network layer that normalises each feature channel using the mean and variance of the current batch during training, and keeps running averages of those statistics for use at test time. *Here:* central to the SSL story. Mean Teacher pipelines before P13 put 8 labelled + 8 unlabelled images (4 + 4 in the old era) through one forward pass, so BN statistics mix the two. This handicapped the student even with the unlabelled loss off (P11 Dm − A crack −0.007; P12 Dm5 − A5c −0.017). P13 introduced the separate forward. *See:* **joint vs separate forward**, `results/p11/README.md`, `results/p12/README.md`, `results/p13/README.md`.

**BN recalibration.** Recomputing BN running statistics after training by passing a set of images through the network. *Here:* a diagnostic before P13 (`results/p13_audit/bn_diag.*`): recalibrating on all 478 train images lifted every arm by about +0.01 crack IoU but left the D5 − A5 gap at −0.06, so the handicap is in the trained weights, not the statistics. *See:* `protocols/P13_cutmix_separate_bn.md` "What I had seen".

**BenchmarkEL releases (`20211104`, `20220723`, `20221008`).** The public repo has three labelled versions: `dataset_20211104` (ours: 478 / 54 / 50 = 582 cells, 24 classes), `dataset_20220723` (642 originals) and `dataset_20221008` (695 originals, 29 classes). The later two ship 4× pre-augmented train copies and reshuffle the splits. *Here:* only `20211104` is trained on; the E-SCDD masks are built on `20221008`; E1's 106-cell extension comes from `20221008`. *See:* `~/mtp/MTP_session_handoff_2026-10-07.md` §3.1; `03_datasets_and_splits.md` §1, §9.

**Best-val vs final-step weights.** Best-val: keep the checkpoint with the best validation score. Final-step: keep the weights at the last training step. *Here:* final-step is always primary. Val has 54 cells and best-val selection flipped the sign of several comparisons in the old era. *See:* `~/mtp/MTP_session_handoff_2026-10-07.md` line 178; memory `mtp-el-ssl-project.md`.

**bf16 (bfloat16) autocast.** Training with 16-bit brain-float arithmetic for speed. *Here:* used everywhere. fp16 produced NaN in old-era DeepLabV3+ runs. In P1, arm B (bf16) and arm D (fp32) fit crack equally over 3 seeds (0.668 ± 0.031 vs 0.656 ± 0.048). *See:* `results/p1/README.md`; phase 1 handoff section 8.

**Bin-0 share (AP saturation).** The share of true pixels of a class that the model scores below 0.001 probability (bin 0 of 1,000). Those pixels are tied with nearly all background in the ranking, so AP cannot rank them. *Here:* L3 at 10% puts 42% of true crack and 65% of true inactive pixels in bin 0 (`results/p6/README.md`, exploratory 1). Reported as a secondary metric from P8 on (`scripts/ssl_figure.py` prints it). Tolerant supervision raised it (P14), SSL lowered it (P13).

**Bootstrap (image bootstrap).** A way to ask "would this difference survive a different test set?". Resample the 50 test cells with replacement many times, recompute the metric difference each time, and read off the spread. *Here:* 2,000 resamples, paired (the same resampled cells for both arms), random generator seed 0. For each resample, dataset-level IoU is recomputed per seed from summed per-cell counts, then averaged over the arm's seeds. Reported as a 95% CI and P(Δ>0). *See:* `scripts/per_image_analysis.py`, `scripts_cv02/e1_aggregate.py`; `07_methodology_rules_and_statistics.md`.

**Busbar, ribbon, gridline, padding, spacing.** Structural or minor classes in BenchmarkEL. Ribbons (4) are the vertical interconnect ribbons; busbars (9); gridline (15) marks short horizontal finger interruptions and is a noisy defect class excluded from headline metrics; padding (7) surrounds downscaled BMRK/SDLE cells; `sp multi` / `sp mono` are the dark spacing between cells. *See:* `data_analysis/benchmark_el_report.md` section 1; `02_domain_primer_EL_and_defects.md`.

**CE (cross-entropy), weighted CE, CE+Dice (`ce_dice`).** CE is the standard per-pixel classification loss. Weighted CE multiplies each class's loss by a weight. *Here (old era and L0-L2):* weights are √(inverse frequency), capped at 10× the median, normalised to mean 1, zero for absent classes. Crack ends up weighted 15-19× background, which made models over-predict crack (old-era crack precision 0.22-0.35 at recall about 0.70). CE+Dice (`loss.supervised=ce_dice`) is unweighted CE plus a soft Dice loss on crack and inactive; it is the L3 recipe used from P8 on. *See:* `protocols/P6_corrected_baseline.md`; phase 1 handoff section 9d; `data_analysis/benchmark_el_report.md`.

**Cell.** One solar-cell image (a 512 × 512 crop: the central cell plus fragments of neighbours). "Cell" and "image" mean the same here. Stems look like `CFVS_00143_r4_c3` or `BMRK_00073_cell0253`. *See:* `03_datasets_and_splits.md`.

**CG-CPCL, DTCT, Ω1/Ω2/Ω3.** ALHVR internals: CG-CPCL is the prototype-based loss for region Ω2; DTCT ("dynamic teacher") is the loss for Ω3. Old-era diagnostics found the prototypes "dead" (cross-network prototypes label 4.6% of Ω3 crack pixels correctly) and that 73-76% of crack pixels sit in Ω3. *See:* phase 1 handoff sections 9e, 9f, 10.

**CI (confidence interval).** Here always the 95% image-bootstrap percentile interval [2.5th, 97.5th percentile] of a difference. "CI excludes 0" means the sign is robust to which test cells were sampled. It does not account for seed noise beyond the seeds actually run.

**Class weights.** See **CE**. Old-era weights were computed over train+val+test (a leak, matching to 5e-7). *See:* phase 1 handoff section 4.

**Collapse (pseudo-label collapse).** When pseudo-labels feed back on themselves and a class is predicted more and more (or less and less). *Here:* the old UCF PV-S3 reimplementation collapsed (teacher predicted corrosion on 0.96% of unlabelled pixels, 23× the labelled share). P13 tracked `rare_frac` as a collapse watch and found none. *See:* phase 1 handoff section 7b; `results/p13/README.md`.

**conf_frac, rare_frac.** Training-log quantities of the tolerant pseudo-label loss. `conf_frac`: share of unlabelled pixels whose teacher confidence passes t_pos. `rare_frac`: share of unlabelled pixels pseudo-labelled crack or inactive. *Here:* P13 rare_frac 0.0064-0.0087 at step 4,000 and 0.0070-0.0109 at step 20,000 over the Cs5 and CsM5 seeds (CsM5 alone: 0.0064-0.0084 and 0.0070-0.0109). In P10, the collapsed seed 2 of C5 sat at 0.001-0.002 against 0.007-0.009 (`results/p10/README.md`). `confidence_ce` (BsM5) logs only conf_frac. *See:* `results/p13/README.md` "Collapse watch".

**confidence_ce (hard pseudo-labels, "B" arms).** The standard pseudo-label loss: take the teacher's argmax class where its confidence is ≥ t_pos (0.95), apply CE, normalise by all unlabelled pixels. FixMatch-style. *Here:* arms B (P7, P8), Bx (P9), B5 (P10), BsM5 (P13). In P13, hard pseudo-labels with CutMix gave the largest crack gain over A5c: +0.036 on 3 seeds, +0.029 on 5 (Amendment 2), secondary. P17's BsD5 is BsM5 with a decoupled decoder. *See:* `protocols/P7_tolerant_pl_pilot.md`; `results/p13/README.md`.

**Confirmatory, exploratory, descriptive, pilot, "Reading".** Confirmatory: a verdict from a locked rule. Exploratory: an analysis no protocol fixed in advance (P3, the "Exploratory" sections of P6 and P7, histograms). Descriptive: numbers reported but not gated by a rule (gap closed, gaint replications, E1 tables). Pilot: an experiment the locked rules declare underpowered (P7, because P6 rule 3 found headroom −0.001 < 0.02). "Reading": the interpretation section of a README, allowed to be wrong. Only confirmatory verdicts count as findings. *See:* `07_methodology_rules_and_statistics.md` §2; `protocols/P7_tolerant_pl_pilot.md` rule 4.

**Consistency loss (unlabelled loss).** The loss on unlabelled images that asks the student to agree with the teacher. In this codebase `loss.consistency` selects it: `tolerant_pl`, `confidence_ce`, or the old `semi_ce`. Weighted by λ.

**CPS (cross pseudo supervision).** Chen et al., CVPR 2021: two networks supervise each other with hard pseudo-labels. *Here:* never run; an old-era poster caption wrongly said ALHVR is built on CPS. *See:* phase 1 handoff sections 10, 12.

**Crack (class 14).** A fracture in the silicon cell; dark thin line in EL. Labels are a median 1.75 px wide while the visible dark line is about 4 px (`data_analysis/benchmark_el_report.md` section 2). Crack appears in 48 of 50 test cells (`results/p6/README.md` exploratory 4); `data_analysis/benchmark_el_report.md` says 50/50 on the old masks. *See:* `02_domain_primer_EL_and_defects.md`.

**CSB-S1, CSB-S2, CSB-S3.** Jha et al.'s (PV-S3) names for the BenchmarkEL releases `20211104` (24 classes; our dataset), `20220723` and `20221008`. *See:* phase 1 handoff §4; `05_literature_and_baselines.md` §4.2.

**CutMix.** A data-mixing perturbation: paste a rectangular box from one image into another. For segmentation SSL, the teacher's prediction gets the same box, so the student must predict the mixed image consistently. *Here:* `ssl.cutmix_p=0.5`: per unlabelled image, with probability 0.5, a box from the next image in the batch is pasted into the strong view; box area U(0.02, 0.4) of the image, aspect U(0.3, 3.33), as UniMatch; draws are a pure function of (seed, step). It copies pixels and never resamples them, so it is label-safe for 1-2 px cracks. P13 CsM5 − Cs5 was n.d. under the seed rule (crack +0.010 [+0.004, +0.017] over cells). P16 runs with CutMix off, chosen on P13 val (score = mean of the three val primaries' seed means: CsM5 0.3507 vs Cs5 0.3652; cv02 `el_p16/reports/p16b/selection.txt`). *See:* `protocols/P13_cutmix_separate_bn.md`; `/home/noob/work/el_p13/src/trainers/ssl_ops.py`.

**cv02.** The shared university GPU server `cv02@10.8.1.106`: 8 × RTX A6000 48 GB, shared by many users. Workspace `/tmp/noob_el` (wiped on reboot). Primary machine for every locked rule from P6 on. *See:* `14_code_and_infrastructure.md`; memory `server-runs-tmux-parallel.md`.

**Decoupled decoder (`ssl.decouple_decoder`, `decoder_u`; P17).** SKCDF's "data flow decoupling", ported alone. The student's unlabelled forward goes through the shared encoder into a second decoder and head (`decoder_u`, copies made at step 0), so pseudo-labels never reach the labelled decoder. `decoder_u` follows the labelled decoder by a parameter EMA, ω = 0.99. Pseudo-labels and test still use the EMA teacher (encoder + labelled decoder). *Here:* arm BsD5; BsD5 − BsM5 n.d. on all three primaries. *See:* `protocols/P17_decoupled_decoder.md`; `results/p17/README.md`.

**D (arm letter), loss-off control, loss-off twin.** The SSL arm with λ_final = 0: identical pipeline, forward pass and data streams, but the unlabelled loss contributes nothing. Comparing C − D isolates the effect of the loss. *Here:* D, Dx, D5, Dx5, Dm, Dmx, Dm5, Dmx5, gDm5. From P13 on, the separate forward makes the λ = 0 student bit-identical to the supervised run, so A becomes the loss-off control.

**Defect mIoU.** Old-era headline metric: mean of crack IoU and inactive IoU, on the old labels. Not used in P-series rules. *See:* phase 1 handoff section 4.

**Detection F1 (inactive).** Per-cell detection: a cell is "positive" if inactive covers ≥ 0.5% of its area (in GT and in the prediction separately); F1 over cells. E1 metric. *See:* `results/e1/README.md`.

**Dice loss (soft Dice).** A loss that directly optimises the overlap between the predicted probability map and the mask of a class; insensitive to class frequency. *Here:* part of CE+Dice, applied to crack and inactive.

**DINOv2, DINOv3 (foundation models).** Large self-supervised vision transformers (DINOv3 also ships distilled ConvNeXt CNNs). Their 14 to 16 px patches are much wider than a BenchmarkEL crack. *Here:* P4's frozen-feature probe found DINOv2 ViT-S/14 weak on crack (AP 0.183 vs 0.321 for ImageNet ResNet-50) and on par for inactive (0.384), so ViT-patch features were dropped for crack; considered only as teachers, never deployed or fine-tuned. *See:* `results/p4_feature_probe/README.md`; `05_literature_and_baselines.md` §13.

**E1 (and E2-E6).** Experiment numbers from `to_human/proposal_reframe_2026-10-11.md`. E1: task-aligned per-cell evaluation plus the extension set (done; `results/e1/`). E2: tolerance with human labels (run as P14). E3: encoder transfer from UCF-EL (run as P15). E4: clean-pipeline SSL (run as P13). E5: small model by distillation (not run). E6: severity pipeline (not run). *See:* `to_human/proposal_reframe_2026-10-11.md` lines 87-96.

**E-SCDD, revised labels.** A dataset on HuggingFace (`snt-ubix/escdd`, MIT; Hanifi et al. 2025, arXiv 2511.09604) built on the BenchmarkEL `20221008` release. It has 903 files: 693 `20221008` cells, 117 new real cells (`_rf`) and 93 synthetic images, with 30 classes. **For crack and inactive its masks are exactly `20221008`'s;** the crack cleaning is BenchmarkEL's own correction (audit 12 Oct, `17_escdd_dataset_audit.md`). It covers 577 of our 582 images. Changed crack masks have a median 1.67× more crack pixels and are almost entirely within 2 px of the old ones: a cleaning (dotted labels joined, widened), not a re-annotation. Crack IoU between old and revised labels: test 0.745, val 0.732, train 0.81; inactive 0.93-0.96. *Here:* from P6 on, all training and scoring uses the revised masks (`data.mask_subdir=labeled/masks_escdd`), with the old mask for 5 train stems missing from E-SCDD. *See:* `results/p3_label_versions/README.md`; `protocols/P6_corrected_baseline.md`.

**SCDD.** The E-SCDD paper's name for BenchmarkEL (its `20221008` release: 695 cells, 29 classes). *See:* `17_escdd_dataset_audit.md`.

**`_rf` files, synthetic files (E-SCDD).** `CSIR_00067_r4_c3_rf.png` is a newly annotated real cell. `10-CFVS_00114_r2_c5_crack_rf.png` is synthetic: sample 10, generated from base cell `CFVS_00114_r2_c5`, conditioned on its crack layout. Filter the synthetic files with `^\d+-.+_rf\.png$`. *See:* `17_escdd_dataset_audit.md` §5.4–5.5.

**PV-DDPM.** The E-SCDD paper's mask-conditioned diffusion model, which generates EL cell images from a layout mask. Not used here. *See:* `literature/notes/A09_hanifi2025_escdd.md`.

**EL (electroluminescence) imaging.** Driving current through a solar cell makes it emit near-infrared light; a camera records it. Working regions glow, damaged or disconnected regions look dark. *See:* `02_domain_primer_EL_and_defects.md`.

**ELPV.** Public EL cell dataset from ZAE Bayern (Deitsch et al.): 2,624 cells of 300 × 300 px with image-level defect probabilities. BenchmarkEL's BMRK cells are ELPV cells (4 of 4 checked, normalised cross-correlation 1.000; rotated 90° and downscaled to 256 px inside a padded 512 × 512 canvas), so it is not an independent pool or test set. Not used. *See:* `literature/notes/F04_el_datasets_census.md` §1b; `03_datasets_and_splits.md` §9.

**EMA, EMA teacher.** Exponential moving average of the student's weights: teacher = 0.999 × teacher + 0.001 × student after each step. *Here:* EMA 0.999; for Mean Teacher runs the evaluated weights are the EMA teacher's (`rescore_label_versions.py` picks `teacher` when `method == mean_teacher`). Old era: EMA added nothing measurable. *See:* `protocols/P7_tolerant_pl_pilot.md`; phase 1 handoff section 9c.

**EMA-only effect.** The difference made by evaluating the EMA teacher instead of the trained weights themselves. From P13 on, the supervised arm A (no EMA) is the loss-off control while SSL arms are scored on the EMA teacher, so SSL − A also contains any EMA effect. Not measured directly (Ds5 was dropped); evidence says it is about 0: phase 1 teacher − student +0.000 ± 0.002, P8 student = teacher, and on 13 Oct teacher − student within ±0.005 at step 20,000 for BsM5, CsM5 and BsD5 (`results/ema_check/README.md`). *See:* `13_problems_pitfalls_open_issues.md` C11; `protocols/P13_cutmix_separate_bn.md` Amendment 1.

**Encoder, ImageNet init, encoder transfer (`encoder_init`).** The encoder is the first half of a segmentation network that extracts features. ImageNet init: start the encoder from weights trained on ImageNet photos. Encoder transfer: start it from weights trained on another task. *Here:* L2/L3 use a ResNet34 encoder with ImageNet weights. P15 starts it from a DeepLabV3+ trained on UCF-EL (`model.encoder_init=<checkpoint>`, copies 216 encoder tensors, sums the first conv over 3 input channels). *See:* `protocols/P15_ucf_encoder_transfer.md`.

**Evidence table.** The numbered table of claims, each with its evidence and status (for example "not supported"), in `to_human/results_2026-10-12.md` section 3, and in tightened form in `11_results_synthesis_and_claims.md` (a). "Evidence row N" refers to its rows.

**Extension set ("ext", 106 cells).** Extra test cells from BenchmarkEL release `20221008` that are not among our 582 and not in the external pool: 106 cells, 101 CSIR and 5 BMRK, 32 with crack, 10 with inactive, from 67 modules (only 1 shared with our 582). Four defect types our taxonomy lacks (scuff, corrosion cell, brightening, star) are marked ignore. It measures transfer to unseen modules: L3 100% crack IoU 0.471 on test vs 0.152 on ext. Its files sit in cv02 `/tmp/noob_el/ext117/` (named for the release's 117 extra cells, of which 106 are scored; `stems_eval.txt` has 106 lines), so it is also written "ext117" or "ext106". Note: the proposal planned 117 cells (112 CSIR, 5 BMRK; 35 crack); 11 were dropped because they are in the external pool. *See:* `results/e1/README.md`; `to_human/proposal_reframe_2026-10-11.md` line 87.

**External pool (`data.unlabeled_pool=external`, "x").** 11,938 unlabelled cells (512 px grayscale) downloaded from a Dropbox share of BenchmarkEL-related images, filtered against labelled cells by cell id. 77% CSIR, 23% ARTS; no CFVS, BMRK or SDLE. List: `data/splits/external_unlabeled.txt`. *Here:* used in P9, P10, P11, P12 and P16's Sx100. Its one seed-rule pass (P9 Cx − Dx, inactive +0.056 against a threshold of 0.046) was not robust over cells and no larger than with the in-domain pool; in P10 to P12 it gave no loss effect, and in P10 it made crack worse on its own sources (`results/p9/README.md`, `results/p10/README.md`). *See:* `protocols/P9_external_pool.md`.

**False alarm (crack false alarm).** Share of cells with almost no true crack (< 20 GT px) on which the model predicts ≥ 50 crack pixels. E1 metric. Uninformative on test (almost no crack-free test cells) but the most sensitive crack metric on the extension. *See:* `results/e1/README.md`.

**Final-step weights.** See **best-val vs final-step weights**. Every BenchmarkEL training run from P6 on is scored at step 20,000 (P1's overfit fits ran 3,000 steps).

**FixMatch-style.** Hard pseudo-labels from a weakly augmented view at a high confidence threshold, applied to a strongly augmented view. *Here:* describes `confidence_ce`.

**FSL / SL / SSL (old-era abbreviations).** FSL = fully supervised on all labels (100%); SL = supervised on a label subset; SSL = semi-supervised. E.g. "SL-20" = supervised at 20%. *See:* Part 2, old-era names.

**frozen_bn_stats.** A context manager in the P13 code: inside it, a training-mode forward still normalises with the batch's own statistics, but every BN running mean, variance and count is restored afterwards. *Here:* the separate forward runs the unlabelled images inside it, so they never enter the BN running statistics. *See:* `/home/noob/work/el_p13/src/trainers/ssl_ops.py` lines 9-10, 46-57.

**FWHM.** Full width at half maximum: the width of the dark crack line in the intensity profile across it, measured where the dip is half its depth. *Here:* visible crack lines are a median 4.0 px FWHM against labels a median 1.75 px wide (`data_analysis/benchmark_el_report.md` §2).

**g (prefix).** The run was on gaint. E.g. gCm5, gDm5, gA10, gU5. Never pooled with cv02 seeds.

**gaint.** The lab GPU server `noob@172.18.22.20`: one RTX PRO 4500 Blackwell 32 GB. The code repo lives there (`/home/noob/work/el-fault-detection`, worktrees `el_p13`, `el_p14`, `el_p16`, `el_p17`; copies of cv02's run dirs in `/home/noob/work/cv02_noob_el`). Its results are descriptive only when cv02 holds the rule. Its `noob` account was reset once in the old era, losing earlier code and results. *See:* `14_code_and_infrastructure.md`.

**Gap closed.** The share of the distance to the 100%-labels model that an arm recovers: (X − A) / (L3@100% − A) per primary metric. P8 to P10 used (C − D) / (L3@100% − D). Descriptive, never a gate. *See:* `07_methodology_rules_and_statistics.md`.

**GaussNoise bug.** Old-era bug: albumentations 2.x silently ignores the old `var_limit` argument, so noise was about 16× too strong and erased cracks. Every result before the fix is invalid (including the old SA ablation and SSL sweep). *See:* phase 0 handoff; phase 1 handoff section 8.

**Handoffs (phase 0, phase 1, 10-07).** The documents describing the work before this session: the phase 0 and phase 1 handoffs pasted by the user on 11 Oct (`sources/chat/phase0_phase1_handoffs_pasted_2026-10-11.md`), and `~/mtp/MTP_session_handoff_2026-10-07.md` ("handoff 10-07", 7 Oct ~22:15 IST). See **Phase 0, phase 1**.

**Headroom (SSL headroom).** P6 rule 3: base@100% − base@10%, pooled val+test, mean of (crack AP + inactive AP)/2. Below 0.02 the next experiment is a pilot. L0's headroom was −0.001, so P7 was a pilot; L3's large 10% → 100% gap (pooled AP +0.159) is why P8 moved to L3. *See:* `results/p6/README.md`; `protocols/P8_tolerant_pl_on_l3.md`.

**Herald connectors.** Exec tools that earlier sessions used to reach the servers: `Gaint_Herald` (gaint) and `Yugma_Herald` or `noob_herald` (ssh to cv02), each with a command allowlist. *See:* `~/mtp/MTP_session_handoff_2026-10-07.md` §2.3; `00_START_HERE.md` §5.

**In-domain pool.** The unlabelled pool made of the other training cells with their labels hidden: 455 cells at 5%, 431 at 10%, 383 at 20%, 239 at 50%, 0 at 100%. *See:* `protocols/P16_label_fraction_curve.md`.

**Inactive (class 11).** A region of the cell electrically cut off (usually by cracks), so it does not glow: a dark area. 99% of inactive components touch a crack within 3 px, and inactive never occurs without crack (`data_analysis/benchmark_el_report.md` section 1). Present in 16 of 50 test cells (top 3 hold 59% of its pixels) and 6 of 54 val cells (top 3 hold 89%) on the revised labels (`results/p6/README.md` exploratory 4; the old-mask count in `data_analysis/benchmark_el_report.md` is 17/50). Labelled cells containing inactive: 2 at 5%, 4 at 10%, 9 at 20%, 20 at 50% (`protocols/P16_label_fraction_curve.md`).

**IoU (intersection over union), pooled IoU, per-cell IoU, mIoU.** IoU = TP / (TP + FP + FN) for one class. Pooled (dataset-level) IoU sums TP, FP, FN over all test pixels first, then divides: big cells dominate. Per-cell IoU computes IoU per cell and averages: each cell counts equally. mIoU is the mean over classes. Per class, IoU = F1 / (2 − F1). *Here:* the primary IoUs are pooled, argmax, revised labels, test set. E1 adds inactive cell IoU (cells with GT inactive ≥ 0.5%). *See:* `scripts_gaint/rescore_label_versions.py`; `results/e1/README.md`.

**Joint vs separate forward (`ssl.student_forward`).** Joint (default, old code): the student sees `cat([labelled view, unlabelled strong view])` in one forward pass, so BN batch statistics mix 8 + 8 images. Separate (P13 on): a labelled forward, then an unlabelled forward inside `frozen_bn_stats`. At λ = 0 the separate-forward student is bit-identical to the supervised run (verified on GPU for 100 steps, `results/p13_audit/smoke_gpu.log`). *See:* `protocols/P13_cutmix_separate_bn.md`.

**Köntges A/B/C (crack modes).** A crack classification after Köntges et al.: A, no inactive area; B, partly disconnected; C, fully inactive. Power loss tracks the inactive or disconnected area, not crack length (literature; primary sources not read). *Here:* the grade at the end of the planned severity pipeline (thesis part 3, E6); not built. *See:* `literature/notes/F04_el_datasets_census.md` §4; `02_domain_primer_EL_and_defects.md` §9.

**L0, L1, L2, L3.** P6's supervised recipe ladder, one change per step. L0: old recipe (`unetpp` 5M from scratch, strong augmentation, weighted CE). L1: + label-safe augmentation. L2: + ImageNet ResNet34 encoder (`smp_unetpp`, 26M). L3: + CE+Dice instead of weighted CE. L3 is the base of everything from P8 on. *See:* `protocols/P6_corrected_baseline.md`; `results/p6/README.md`.

**L3o, L3To, L3T.** P14 arms: L3 trained on old masks (L3o), old masks with the tolerant supervised loss (L3To), revised masks with the tolerant loss (L3T). *See:* `protocols/P14_tolerant_supervision.md`.

**Label fraction (`data.labeled_fraction`).** Share of the 478 train cells whose labels are used: 5% = 23 cells, 10% = 47, 20% = 95, 50% = 239, 100% = 478. Subsets are committed files (`data/splits/seed0/labeled_5pct.txt` etc.). The user wrote "592 images" on 11 Oct; the correct count is 582 (478 + 54 + 50). *See:* `protocols/P16_label_fraction_curve.md`; `03_datasets_and_splits.md`.

**Label gap, label-noise gap (G).** Label gap: the score difference between more and fewer labels, e.g. L3 10% → 100%: crack IoU +0.075, inactive +0.135 (`results/p6/README.md`); on UCF-EL (old era) the 4-class mean is 0.54 / 0.41 / 0.23 at 100 / 5 / 1% labels (`06_history_phase0_phase1.md` §5.7). Label-noise gap G (P14 rule 1): L3 − L3o, revised vs old training masks at 10%, crack IoU +0.082 (`results/p14/README.md`).

**Label-safe augmentation (`data.augmentation=labelsafe`).** Augmentation that never resamples pixels geometrically except by exact flips and 90° rotations, plus photometric changes (brightness/contrast). No small-angle rotation, no blur, so 1-2 px crack labels stay aligned. Supervised label-safe view: brightness/contrast ±0.2 with p 0.4, no noise. SSL "strong" label-safe view: ±0.25 with p 0.8 plus mild Gaussian noise with p 0.3. *See:* `protocols/P6_corrected_baseline.md`; `protocols/P11_matched_pipeline.md`.

**`labeled_aug=supervised` ("m", matched view).** P11 switch: the Mean Teacher's labelled images get exactly the supervised arm's label-safe view instead of the SSL strong view. Removes one of three differences between SSL and supervised pipelines. Arms with "m" (Dm, Cm, Dmx, Cmx, Dm5, ...) use it; every later SSL arm does too. *See:* `protocols/P11_matched_pipeline.md`.

**Labelled / unlabelled pool.** The labelled set is the cells whose masks training uses. The unlabelled pool is images whose masks training never sees: in-domain (rest of train) or external.

**λ (lambda), warm-up, ramp, λ_final.** The weight of the unlabelled loss: total loss = supervised loss + λ × unlabelled loss. *Here (P-series):* λ = 0 for 2,000 steps, then a linear ramp over 2,000 steps to λ_final = 1.0. λ_final = 0 makes a loss-off control. Old era: MT ramp to 1.5; ALHVR max 0.1. *See:* `protocols/P7_tolerant_pl_pilot.md`; phase 1 handoff section 9.

**Leave-top-3-out.** Recompute a difference after removing the 3 test cells with the most ground-truth pixels of that class. Tests whether a result rests on a few large cells. Important for inactive (top 3 test cells hold 59% of inactive pixels; crack 32%). *See:* `scripts/per_image_analysis.py`.

**Length error (crack length error).** Per cell, |L_pred − L_gt| / L_gt, with L the pixel count of the skeleton (skimage `skeletonize`); median over cells with GT crack ≥ 20 px. E1 metric. *See:* `results/e1/README.md`.

**Locked protocol, locking.** A protocol file committed to `~/mtp/research/protocols/` before any run of the experiment, fixing question, arms, metrics and decision rules. *See:* `07_methodology_rules_and_statistics.md`.

**masks_coded vs masks_escdd (old vs revised labels).** `data/labeled/masks_coded`: original BenchmarkEL `dataset_20211104` masks ("old", also `old_20211104` in re-score JSONs). `data/labeled/masks_escdd` (training) and `data/escdd_masks/<split>/` (scoring): E-SCDD revised masks ("new", `new_escdd` in JSONs). *See:* `scripts_gaint/rescore_label_versions.py`; **E-SCDD**.

**Mean Teacher (MT).** Tarvainen and Valpola 2017. A student network trains on labelled images and on a consistency loss toward a teacher on unlabelled images; the teacher is the EMA of the student. *Here:* the SSL framework of every P-series SSL arm (`configs/ssl_mean_teacher.yaml`, `method: mean_teacher`).

**Metric conventions (`standard`, `pvs3`, `pratt_median`).** The ways the old-era metrics module computed IoU to match papers. `standard`: one dataset-level confusion matrix, background included (ours). `pvs3`: first drop every pixel whose ground truth is background (Jha's code), which hides false positives on background. `pratt_median`: per-image IoU, median over test images, with an absent-class rule A, B or C. *See:* `05_literature_and_baselines.md` §2; `analysis/papers_metrics.md`.

**MoE (Mixture of Experts).** An advisor suggestion from the old era. The phase 1 position was to gate it on a specialist-vs-generalist diagnostic (about 2 GPU hours), never run; standard load balancing balances pixel counts, i.e. background. Not part of the P-series. *See:* phase 1 handoff §11; `06_history_phase0_phase1.md` §11.

**Module-disjoint split.** A split in which no physical module (or physical cell) appears on both sides. UCF-EL's official split is by cell: 25% (confirmed) to 44% (possible) of test cells have their physical twin in train, so a module-disjoint re-split is needed before a UCF label-efficiency claim; none was made. BenchmarkEL's official split also shares modules (24 of 50 test cells). *See:* `data_analysis/ucf_el_report.md`; `03_datasets_and_splits.md` §2.2, §8.4.

**Multiple contrasts.** Each experiment tests several arm pairs; no multiplicity correction is applied. Protocols name a primary claim and disclose the number of contrasts (P13: 1 primary + 5 secondary; P16: 3 primary).

**n.d. ("not detectable").** The rule-1 verdict when |Δ| does not exceed the threshold. It means "no difference shown", not "no difference".

**Old era vs P-series.** Old era: before 8 Oct 2026 (original masks, from-scratch U-Net++, weighted CE, batch 4, SemiCE Mean Teacher, ALHVR port). P-series: P1 to P16 and E1 (P1 to P5 are probes; revised masks from P6, L3 base from P8). Their numbers are never put in the same table (user's standing rule).

**One change per arm.** Each arm differs from its comparison arm in exactly one setting, so a difference can be attributed. User's standing rule.

**Operating point.** The decision rule turning probabilities into a mask (argmax or a threshold). IoU depends on it; AP does not.

**O1, O2, O3.** Objectives in `to_human/proposal_reframe_2026-10-11.md`: O1 measurement (task-aligned, variance-aware metrics), O2 learning from imprecise thin labels (offset-tolerant objective), O3 using unlabelled EL data fairly (pseudo-label SSL vs pretraining vs distillation). The user's rule: framing depends on final results.

**P(Δ>0).** Share of the 2,000 bootstrap resamples in which the difference is positive. 1.00 or 0.00 means every resample agrees on the sign.

**P-numbers (P1-P17).** Protocol / experiment numbers in time order. P1 overfit check, P2 SemiCE gradient probe, P3 label versions (exploratory), P4 frozen-feature probe, P5 region pseudo-label precision, P6 corrected baseline ladder, P7 tolerant PL on L0 (pilot), P8 tolerant PL on L3, P9 external pool, P10 SSL at 5%, P11 matched pipeline at 10%, P12 matched at 5% + gaint replication, P13 separate BN + CutMix, P14 tolerant supervision, P15 UCF encoder transfer, P16 label-fraction curve, P17 SKCDF-style decoupled decoder. *See:* `08_experiments_P1_P7_diagnostics.md`, `09_experiments_P8_P12_ssl_series.md`, `10_experiments_P13_P16_E1.md`.

**Phase 0, phase 1.** The user's names for the work before this session. Phase 0: the earliest work (SA U-Net++, Mean Teacher + SemiCE, first reproductions), mostly lost in the gaint account reset. Phase 1: the rebuild, 2 to 7 Oct 2026 (repo `el-fault-detection`, ALHVR port, cv02 replication, loss-off controls). Both are "old era". Inside the phase 1 documents, "Phase 0" can also mean the 2 Oct foundation rebuild. *See:* `06_history_phase0_phase1.md` §1.

**Primary metrics.** From P8 on: test crack IoU, test inactive IoU, test crack relaxed F1@2; argmax, revised labels, final weights. A rule passes if any primary improves and none worsens. P6/P7 used crack AP and inactive AP.

**Protocol.** The markdown file that defines an experiment before it runs. See **locked protocol**.

**Pseudo-label.** A label for an unlabelled pixel produced by the teacher's prediction. Hard: the argmax class (often only where confidence passes a threshold). Soft: the probability vector.

**PV-S3, PV-S3 metric.** Jha et al. 2025 (EAAI), a Mean Teacher SSL method on UCF-EL. Its metric drops every pixel whose ground truth is background before scoring, which hides false positives on background; its released code sets `ignore_index = 0` and never models background (old-era finding: standard 0.050 vs PV-S3 metric 0.828). *See:* phase 1 handoff sections 5, 7c; `analysis/papers_metrics.md`.

**R (tolerance radius).** The pixel offset a tolerant loss or metric forgives. *Here:* R = 2 px everywhere (`loss.tolerance_radius=2`), never tuned.

**Relaxed precision / recall / F1 at r px (relP@2, relR@2, relF1@2).** Crack metrics that forgive small offsets. relP@r: share of predicted crack pixels within r px of a true crack pixel. relR@r: share of true crack pixels within r px of a predicted crack pixel. relF1@r = 2PR / (P + R). Pooled over the test set; r = 2 primary (r = 1 also computed). *Here:* relF1@2 is a primary metric; relP@2 is the width check. *See:* `scripts_gaint/rescore_label_versions.py` `relaxed()`.

**Re-score JSON, rescoring.** After training, `scripts/rescore_label_versions.py` (read-only) scores the final checkpoint on test (50) and val (54) against both label versions. Output per run: `reports/<exp>/<run>.json` with keys `test/<run>` and `val/<run>`, each holding `old_20211104` and `new_escdd` blocks with crack and inactive iou, precision, recall, ap, rel_f1_1/2, rel_p1/2, rel_r1/2. Copies live in `results/<exp>/raw/`. All rule scripts read these.

**ResNet34, `smp_unetpp`, `unetpp`.** `unetpp`: the project's own U-Net++, about 5M parameters, trained from scratch (L0, L1, old era). `smp_unetpp`: U-Net++ from the segmentation_models_pytorch library with a ResNet34 ImageNet encoder, about 26M parameters (L2, L3, all P8+ runs). The user said model size is not a constraint for this phase ("not a constraint even 5M works", 11 Oct).

**Robust over cells.** Shorthand for: the paired image-bootstrap 95% CI of a difference excludes 0, and the difference keeps its sign without the top-3 cells. Checked separately from the seed rule; it never changes a verdict. *See:* `07_methodology_rules_and_statistics.md` §8; `16_faq_for_the_guide.md` Q15.

**Run.** One training of one arm with one seed, e.g. `p13_CsM_5pct_s3`. Its directory holds `config_used.yaml`, `checkpoints/latest.pth`, `train.log`, `metrics.json`.

**SA-UNet++ (SA block).** Gangopadhyay et al. 2025: U-Net++ with "self-attention" blocks that are actually elementwise sigmoid gates (`sigmoid(Q+K)*V`). *Here:* the project's first model. The old "removing SA helps" result is invalid (GaussNoise); a corrected rerun showed no effect (test 0.3399 ± 0.0104 vs SL-20 0.3435 ± 0.0329). *See:* phase 0 and phase 1 handoffs.

**sd (standard deviation over seeds).** The spread of an arm's metric across training seeds, sample sd (ddof = 1). Tables show mean ± sd.

**Seeds (training seed vs split seed).** The split seed fixes which cells are train/val/test and which are labelled; it is always 0 (`data.split_seed=0`). The training seed (`seed=`) changes initialisation, data order and augmentation; arms use seeds 0-2, 0-4, or 3-5 (gaint replications). *See:* `07_methodology_rules_and_statistics.md`.

**SKCDF, DCA (CVPR 2025, CVPR 2026).** Two class-imbalanced semi-supervised medical segmentation methods, both 3D. SKCDF (Zhang et al.) decouples data flow: pseudo-labels train the encoder and an unlabelled decoder, not the labelled decoder; it adds cross-attention and class-balanced heads. DCA (Liu et al.) splits classes into head/medium/tail groups with one expert decoder each and stitches their logits into pseudo-labels. *Here:* P17 ports SKCDF's decoupling only (named "SKCDF-style decoupling"); DCA was not run (13 Oct). *See:* `literature/notes/F01_rareclass_ssl_2024_2026.md`; `10_experiments_P13_P16_E1.md` P17.

**Self-supervised learning.** Learning features from unlabelled images with a pretext task (e.g. masked image modelling, MIM). Different from semi-supervised. *Here:* considered (P4, directions row 3; E3's MIM arm), not run.

**Semantic segmentation.** Assigning a class to every pixel of an image. The task here: 24 BenchmarkEL classes, scored on crack and inactive.

**Semi-supervised learning (SSL).** Training with a few labelled images plus many unlabelled ones. *Here:* Mean Teacher with a pseudo-label loss.

**SemiCE.** The old-era consistency loss (`src/losses/semi_ce.py`): per-class binary CE on softmax logits, with "confident" sets chosen by raw-logit thresholds t_pos = 0.5·freq and t_neg = 0.5·(1 − freq). P2 showed it is not a valid consistency loss: 100% of pixels have ≥ 2 positive classes, and its gradient is nearly orthogonal to the supervised one (cosine 0.07). Every old Mean Teacher result used it and is invalid. *See:* `protocols/P2_semice_gradient_probe.md`; `results/p2/README.md`; memory `mtp-el-ssl-project.md`.

**Source, source split.** BenchmarkEL cells come from five sources (labs / module sets). Train: ARTS 162, CFVS 146, CSIR 111, BMRK 42, SDLE 17 (`data_analysis/benchmark_el_report.md`); all 582: ARTS 195, CFVS 187, CSIR 122, BMRK 60, SDLE 18 (`03_datasets_and_splits.md` §2.2). Test: 18 CFVS, 13 ARTS, 10 BMRK, 8 CSIR, 1 SDLE. The "P9 source split" reports a contrast separately on the 21 CSIR + ARTS test cells (the sources in the external pool) and the 29 CFVS + BMRK + SDLE cells. Descriptive. *See:* `protocols/P9_external_pool.md`.

**Split (train / val / test).** 478 / 54 / 50 cells, fixed, split seed 0 (`data/splits/{train,val,test}.txt`). Never reshuffled. *See:* `03_datasets_and_splits.md`.

**Step matching.** Comparing arms at the same number of optimizer steps (20,000 for every arm from P6 on). Old-era lesson: an 8× step mismatch once produced a fake +7.4 gain. User's standing rule.

**Strong / weak views.** In Mean Teacher, the teacher sees a weak view (normalisation only) and the student a strong view (label-safe photometric jitter and noise; plus CutMix in "M" arms). Geometry (flips, 90° turns) is shared between views.

**Student, teacher.** The student is the network trained by gradient descent. The teacher produces pseudo-labels; in Mean Teacher it is the EMA of the student, in eval mode, detached.

**Subpath A, Subpath B.** Phase 0 plans for thesis part 3. Subpath A: post-processing into per-cell measurements (connected components, skeleton length, isolation via a busbar/ribbon topology mask, Köntges grading; 57 tests; code lost in the reset). Subpath B: compression for the Jetson (native narrow models, Torch-Pruning to about 2M, INT8 + TensorRT). Neither exists now. *See:* phase 0 handoff; `06_history_phase0_phase1.md` §4.

**Supervised.** Training only on labelled cells. The "A" arms.

**t_pos.** Confidence threshold for pseudo-labels. *Here:* 0.95 (`loss.t_pos=0.95`) for `confidence_ce` and for head-class pixels in `tolerant_pl`. Old SemiCE used logit thresholds (see **SemiCE**). P5: at confidence ≥ 0.95 crack pseudo-label precision is 0.59 strict vs 0.96 within 2 px, and the threshold keeps only 8% of GT crack.

**tol_dice.** P14's tolerant supervised loss: `ce_dice` with its CE replaced by the tolerant rule applied to the ground truth (rare labels credited if predicted within 2 px; head-class pixels within 2 px of a rare label not scored; plain CE elsewhere; Dice unchanged). At R = 0 it equals `ce_dice`. *See:* `protocols/P14_tolerant_supervision.md`.

**tolF1@2 (crack tolerance F1, per cell).** Per cell, 2PR / (P + R) with P = share of predicted crack pixels within 2 px of GT crack, R = share of GT crack within 2 px of predicted crack; 0 if nothing predicted; mean over cells with GT crack ≥ 20 px. The per-cell version of relF1@2. E1 metric. *See:* `results/e1/README.md`.

**Tolerant pseudo-labels (`tolerant_pl`, "C" arms).** The project's proposed unlabelled loss (`src/losses/tolerant_pl.py`). Per unlabelled pixel: if the teacher's argmax is a rare class (crack or inactive), confident or not, the loss is −p_t[r] · log(max-pool over 5 × 5 of p_s[r]), i.e. the student is credited for predicting that class anywhere within 2 px; if the teacher is confident (≥ t_pos) on a head class and the pixel is outside a 2 px band around rare targets, plain CE; everything else, no loss. Motivated by P5 (pseudo-labels hit the right crack but the wrong pixels). *See:* `protocols/P7_tolerant_pl_pilot.md`.

**UCF-EL-Defect (UCF-EL).** Fioresi et al. 2022 dataset: 9,562 train / 2,289 test EL cells, 5 classes (background, crack, contact, interconnect, corrosion) plus ignore 128; crack is a region class, per-component median width 9.2 px at shorter side 295 (`data_analysis/ucf_el_report.md` §4; the phase 1 handoff §4 gives 15.2 px by an unstated method). *Here:* old-era reproductions; P15 pretrains an encoder on all 9,562 train cells. *See:* `data_analysis/ucf_el_report.md`; `03_datasets_and_splits.md`.

**U-Net, U-Net++.** Encoder-decoder segmentation networks with skip connections; U-Net++ adds nested dense skip paths. *Here:* U-Net++ in both the own 5M version and the smp ResNet34 version.

**Val (validation set).** 54 cells. Used to select P6's base (rule 2) and P16's CutMix setting (user's choice), never to select checkpoints. Inactive in only 6 val cells, top 3 hold 89%, so val inactive is close to uninformative; P13 val and test disagree on inactive. *See:* `results/p13/README.md` "Secondary".

**WattCycle.** The solar asset-management company behind the MTP. Its mandate: detect defects, grade severity, estimate power loss. Power loss is outside this project unless valid data appears (user, 11 Oct). *See:* `01_project_overview_and_scope.md`.

**Width check.** A guard against "fattening" (predicting thick cracks to boost tolerant metrics): if an arm's crack gain comes with crack relP@2 falling by more than 0.05 against its comparison arm, it is flagged. *See:* `07_methodology_rules_and_statistics.md`.

**Worktree, commit, REVISION.** Each experiment's code change lives in its own git worktree and branch on gaint (`el_p13` = branch p13 at `bac5264`, `el_p14` = p14 at `be67787`, `el_p16` = p16 at `d51b60f`, `el_p17` = p17 at `f2f20d3`; main at `24590fb`). The exact commit is deployed to cv02 by `git archive` and recorded in the deployment directory's `REVISION` file (`el_p16` has none; its commit `d51b60f` is recorded in P16 Amendment 1). *See:* `14_code_and_infrastructure.md`.

**x (suffix letter).** The arm uses the external pool. Dx, Cx, Bx, Dmx, Cmx, Dx5, Cx5, Dmx5, Cmx5, Sx100.

---

## Part 2: Naming

### Run names
A run name has three parts: `p<N>_<arm>_<fraction>pct_s<seed>`.
- `p<N>`: the experiment (P6 to P16). E.g. `p12`.
- `<arm>`: the arm code (table below).
- `<fraction>pct`: label fraction, `5pct`, `10pct`, `20pct`, `50pct`, `100pct`.
- `s<seed>`: training seed.

Examples: `p6_L3_10pct_s0` (P6, ladder step L3, 10% labels, seed 0); `p12_gCm_5pct_s4` (P12, gaint tolerant-PL matched arm at 5%, seed 4); `p16_Sx_100pct_s2`.

In the analysis scripts an arm is written `<exp>:<arm>_<fraction>pct`, e.g. `p13:CsM_5pct`. Pooled arms get a short name with `--merge`, e.g. `p13:A5c=p12:A_5pct+p13:A_5pct` or, in E1 files, `p13_A5c`.

In prose and README tables, arms are written with the fraction as a trailing number: Cm5 = `Cm_5pct`, S20 = `S_20pct`, A100 = `A_100pct`. An arm without a number in P7-P9 and P11 is at 10%.

### Arm letters
| Code | Meaning |
|---|---|
| A | supervised reference (no unlabelled data) |
| B | hard pseudo-labels (`confidence_ce`, t_pos 0.95) |
| C | tolerant pseudo-labels (`tolerant_pl`, R = 2 px), the proposed loss |
| D | loss-off control: the C arm with λ_final = 0 |
| m | matched labelled view (`ssl.labeled_aug=supervised`, P11 on) |
| x | external unlabelled pool (11,938 cells) instead of in-domain |
| s | separate BN forward (`ssl.student_forward=separate`, P13 on) |
| M | CutMix on unlabelled images (`ssl.cutmix_p=0.5`, P13) |
| g (prefix) | run on gaint, not cv02 |
| c (suffix, A5c only) | cv02 supervised 5% (vs P10's gaint A5) |
| L0-L3 | P6 supervised ladder steps |
| o / T (P14) | o = trained on old masks; T = tolerant supervised loss `tol_dice` |
| U (P15) | encoder initialised from the UCF-EL-trained network |
| D (P17, BsD5 only) | decoupled decoder (`ssl.decouple_decoder=true`). Not the loss-off "D" of P7 to P12 |
| S / Sx (P16) | SSL arm with P13's separate-forward tolerant recipe at P16's fraction; Sx uses the external pool. Note "S" here is not the "s" of P13 |

### Every arm, P6 to P17
| Exp | Arm (run prefix) | Fraction | Machine | Seeds | What it is |
|---|---|---|---|---|---|
| P6 | L0 (`p6_L0_10pct`, `p6_L0_100pct`) | 10, 100 | cv02 | 0-2 | `unetpp` 5M from scratch, strong aug, weighted CE (old recipe) |
| P6 | L1 (`p6_L1_10pct`) | 10 | cv02 | 0-2 | L0 + label-safe aug |
| P6 | L2 (`p6_L2_10pct`) | 10 | cv02 | 0-2 | L1 + `smp_unetpp` ResNet34 ImageNet |
| P6 | L3 (`p6_L3_10pct`, `_20pct`, `_100pct`) | 10, 20, 100 | cv02 | 0-2 | L2 + CE+Dice. The base from P8 on; "A" at 10% |
| P7 | A | 10 | cv02 | 0-2 | P6 L0 10% (no new runs) |
| P7 | B (`p7_B_10pct`) | 10 | cv02 | 0-2 | MT + hard PL, L0 base |
| P7 | C (`p7_C_10pct`) | 10 | cv02 | 0-2 | MT + tolerant PL, L0 base |
| P7 | D (`p7_D_10pct`) | 10 | cv02 | 0-2 | C with λ = 0 |
| P8 | A | 10 | cv02 | 0-2 | P6 L3 10% |
| P8 | B, C, D (`p8_*_10pct`) | 10 | cv02 | 0-2 | as P7, on the L3 base |
| P9 | Bx, Cx, Dx (`p9_*_10pct`) | 10 | cv02 | 0-2 | as P8 with the external pool |
| P10 | A5 (`p10_A_5pct`) | 5 | gaint | 0-2 | supervised 5%, reference only |
| P10 | A50 (`p10_A_50pct`) | 50 | gaint | 0-2 | supervised 50%, reference only |
| P10 | D5, C5 (`p10_D_5pct`, `p10_C_5pct`) | 5 | cv02 | 0-2 | P8-style MT, in-domain pool (455) |
| P10 | Dx5, Cx5 | 5 | cv02 | 0-2 | same, external pool |
| P10 | B5 (`p10_B_5pct`) | 5 | cv02 | 0-2 | hard PL, in-domain (amendment) |
| P11 | Dm, Cm (`p11_Dm_10pct`, `p11_Cm_10pct`) | 10 | cv02 | 0-2 | matched labelled view, in-domain (431) |
| P11 | Dmx, Cmx | 10 | cv02 | 0-2 | matched view, external pool |
| P12 | A5c (`p12_A_5pct`) | 5 | cv02 | 0-2 | supervised 5% on cv02 |
| P12 | Dm5, Cm5, Dmx5, Cmx5 | 5 | cv02 | 0-2 | P11 arms at 5% |
| P12 | gDm5, gCm5 | 5 | gaint | 3-5 | replication of Dm5, Cm5 |
| P12 | gA10 (`p12_gA_10pct`) | 10 | gaint | 0-2 | supervised 10% on gaint (calibration) |
| P13 | A5c (`p13_A_5pct`) | 5 | cv02 | 3-4 | extra supervised seeds; pooled with P12's s0-2 |
| P13 | Cs5 (`p13_Cs_5pct`) | 5 | cv02 | 0-2 | tolerant PL, separate BN, no CutMix |
| P13 | CsM5 (`p13_CsM_5pct`) | 5 | cv02 | 0-4 | Cs5 + CutMix. Primary arm |
| P13 | BsM5 (`p13_BsM_5pct`) | 5 | cv02 | 0-4 | hard PL, separate BN, CutMix (s3-4 post hoc, Amendment 2, 13 Oct) |
| P13 | Ds5, 10% arms, gDs5, gCsM5 | | | | planned, dropped by Amendment 1 (not run) |
| P14 | L3o (`p14_L3o_10pct`) | 10 | cv02 | 0-2 | L3 on old masks |
| P14 | L3To (`p14_L3To_10pct`) | 10 | cv02 | 0-2 | old masks + `tol_dice` |
| P14 | L3T (`p14_L3T_10pct`) | 10 | cv02 | 0-2 | revised masks + `tol_dice` |
| P15 | pretraining (`p15_ucf_pre_dlv3p_r34`) | UCF full | cv02 | 0 | DeepLabV3+ ResNet34 on all 9,562 UCF train cells |
| P15 | U5 / gU5 (`p15_gU_5pct`) | 5 | gaint | 0-2 | L3 with UCF-trained encoder; reference P10 A5 |
| P15 | U10 / gU10 (`p15_gU_10pct`) | 10 | gaint | 0-2 | same at 10%; reference P12 gA10 |
| P16 | A20 (`p6_L3_20pct` + `p16_A_20pct`) | 20 | cv02 | 0-2 + 3-4 | supervised 20%, 5 seeds pooled |
| P16 | A50 (`p16_A_50pct`) | 50 | cv02 | 0-4 | supervised 50% |
| P16 | A100 (`p6_L3_100pct` + `p16_A_100pct`) | 100 | cv02 | 0-2 + 3-4 | supervised 100%, 5 seeds pooled |
| P16 | S20 (`p16_S_20pct`) | 20 | cv02 | 0-4 | SSL, in-domain pool 383, CutMix off |
| P16 | S50 (`p16_S_50pct`) | 50 | cv02 | 0-4 | SSL, in-domain pool 239, CutMix off |
| P16 | Sx100 (`p16_Sx_100pct`) | 100 | cv02 | 0-4 | SSL, external pool 11,938, CutMix off |
| P17 | BsD5 (`p17_BsD_5pct`) | 5 | cv02 | 0-4 | BsM5 + decoupled decoder (SKCDF-style) |
| P18 (exploratory) | BsM20 (`p18_BsM_20pct`), BsM10 (`p18_BsM_10pct`) | 20, 10 | cv02 | 0-4, 0-2 | BsM5's recipe at more labels |
| P19 (reproduction) | Hanifi 2025: `vgg_unet` (s0–2), `mobilenet_unet`, `resnet50_unet`, `vgg_segnet`, `mobilenet_segnet`, `resnet50_segnet` (s0) | 100 (release split 553/70/72, 29 classes) | cv02 | see left | their Keras code unchanged; not a P-series arm |

Status (13 Oct): every arm above finished with rc = 0 (P17 and BsM5 s3-4 at 04:08 IST; P18 at 19:40 IST, 13 Oct).

### P1 to P5 and E1
P1 to P5 are probes, not arm comparisons. P1 arms A-E are overfit-check variants on 10 crack images (loss, augmentation, precision); P2, P4 and P5 are read-only measurements on existing checkpoints; P3 has no protocol (exploratory). E1 scores existing checkpoints. *See:* `08_experiments_P1_P7_diagnostics.md`, `10_experiments_P13_P16_E1.md`.

### Old-era names (kept separate from P-series tables)
| Name | Meaning |
|---|---|
| SL-20, SL-100, SL-10, SL-5, SL-2 | supervised at 20%, 100%, 10%, 5%, 2% labels (old recipe, batch 4) |
| SL-20-b8, `sl_20pct_b8_s0` | supervised, 20%, batch 8 ("b8"), seed 0 |
| MT-20, `mt_20pct_s0` | Mean Teacher with SemiCE at 20% (invalid: SemiCE) |
| MT-20 λ0 | same with λ = 0 (equals MT-20) |
| ALHVR-20, `alhvr_20pct_s0` | ALHVR port at 20% (gain equals its λ0 control) |
| SA-SL-20, SA-SL-100, SA-MT-20 | SA-UNet++ (SA gate on) supervised at 20% or 100%, or Mean Teacher (SemiCE) at 20% |
| Pratt-A, Pratt-C | old-era reproduction of Pratt 2023 (smp U-Net VGG16, weight set A or C) |
| PV-S3 v1, v2 | the old-era UCF-EL reimplementations of PV-S3 (both failed; `05_literature_and_baselines.md` §4.2) |
| MT 5%, MT 1% (UCF) | Mean Teacher (SemiCE) on UCF-EL, cv02, 7 to 8 Oct (invalid: SemiCE) |
| FSL | fully supervised (100%), mostly UCF-EL reproductions |
| `pilot` runs | 2 Oct runs with coupled augmentation; not comparable |

### Other identifiers
- "Directions rows": numbered rows 0-9 of the table in `to_human/directions_2026-10-10.md`: 0 fix the ground (revised labels, label-preserving augmentation, metrics); 1 tolerance / noise-aware supervision for thin labels; 2 ALHVR-inspired rarity-aware routing; 3 unlabelled data without pseudo-labels (MIM pretraining); 4 weak and mixed supervision; 5 cross-dataset transfer; 6 foundation-teacher distillation; 7 rare-class synthesis; 8 anomaly prior from normal cells; 9 active learning. Protocols cite them: P5 decides row 2, P4 rows 3 and 6, P14 is row 1, P15 rows 3 and 5.
- "Rule 1" without context means P8 rule 1, the detectability threshold. "R1" to "R8" is the rule list the user was given on 11 Oct (`07_methodology_rules_and_statistics.md`).
- **Doc-local IDs** (not arm names or experiments): D1 to D33 are decisions in `12_decisions_log.md`; in `13_problems_pitfalls_open_issues.md`, A1 to A10, B1 to B14, C1 to C13, D1 to D18 and E1 to E14 are problem, invalid-result, design-weakness, infrastructure and open-question IDs (its E1 is not the E1 experiment); A01 to F05 are the literature note files in `literature/notes/`.
- `rc = 0`: return code of a training or rescoring job; 0 means it finished without error. Launch logs (`launch.log`) record "trained <run> rc=..." and "rescored <run> rc=...".

---

## Related docs
- `00_START_HERE.md`, `01_project_overview_and_scope.md`
- `02_domain_primer_EL_and_defects.md`, `03_datasets_and_splits.md`
- `05_literature_and_baselines.md`, `06_history_phase0_phase1.md`
- `07_methodology_rules_and_statistics.md`
- `08_experiments_P1_P7_diagnostics.md`, `09_experiments_P8_P12_ssl_series.md`, `10_experiments_P13_P16_E1.md`
- `11_results_synthesis_and_claims.md`, `12_decisions_log.md`, `13_problems_pitfalls_open_issues.md`
- `14_code_and_infrastructure.md`, `15_status_remaining_work.md`, `16_faq_for_the_guide.md`
