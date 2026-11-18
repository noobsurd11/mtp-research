# T4 family: offline label refinement and annotator / source style (analyst, 13 Nov 2026)

Tags: R = the paper says it (retrieved by me today unless marked), E = our files, S = my judgement.
Tools: Research MCP not loadable in this session (ToolSearch found only its authenticate stubs). Used WebFetch / WebSearch. Full text read: 2306.15172 (html), 2210.17398v3 (html), 2007.15963v5 (html), 2111.13410v3 (html), 2206.06743 (html). Not retrievable: MuGE CVF page and PDF (HTTP 403 / 404), HAL copy of the Rill-Garcia paper (bot wall), the 2026 EngAppAI paper (Elsevier redirect only). Numbers for those three are marked unverified.
Spec with the arms: `T4_label_refine_style_spec.md`. Ledger: `ledger/T4.tsv`.

## What this family can and cannot move (S, from E facts)
- E (BRIEF 2, `benchmark_el_report.md` 4.2): 48% of crack label skeleton points lie within 1 px of the darkest point along the normal, 64% within 2 px; ARTS 75% within 1 px, BMRK 38%. No large systematic offset (label-centred mean profile has its minimum at 0; sub-pixel horizontal bias of about -0.2 px).
- E: label width by source (median, profile method): ARTS 1.5, CFVS 1.75, CSIR 1.75, BMRK 3.0, SDLE 3.25 px; visible FWHM 3.0 / 4.25 / 3.5 / 5.0 / 4.5 px.
- S: because the jitter is roughly symmetric around the ridge, a ridge-centred prediction is already close to the expected-overlap optimum against jittered test labels. Moving the training labels onto the ridge therefore should not raise strict IoU through position. What it can raise: confidence and recall on faint cracks (cleaner positive pixels, fewer contradictory negatives beside the crack), relR@2, component recall, crispness. What can raise strict IoU: matching each source's width convention (part b), because the test labels keep their source widths.
- E (BRIEF 5, Labels row): human relabelling gave +0.05 to +0.08 crack IoU; automatic refinement, noise-robust training and source-style modelling were never run. Offset-tolerant CE (n.d.) is a loss, not a label edit. No row of BRIEF 5 voids any paper here.

---

## Rank 1. Delving Into Crispness: Guided Label Refinement for Crisp Edge Detection
- Ids: doi:10.1109/tip.2023.3289296; arXiv 2306.15172 (html read).
- Claims (R): refined labels = low-threshold Canny run on several blurred copies, intersected with the human label (label values below eta 0.3 zeroed), gaps filled by an EdgeConnect inpainting network gated again by Canny, iterated until the number of gap regions stops falling; human-labelled pixels absent from the refined label are set below eta so training ignores them. PiDiNet, Table I: BSDS500 average crispness (AC) 0.250 to 0.424, ODS after NMS 0.780 to 0.771 (slightly lower), before NMS 0.763 to 0.771; Multicue AC 0.204 to 0.424, ODS after NMS 0.874 to 0.892, before NMS 0.764 to 0.886, OIS before NMS 0.778 to 0.904. Ablation (Table III): Canny-intersect-label alone ODS 0.735 / AC 0.41; full iterative 0.771 / 0.424; dilated-label baseline 0.769 / 0.271. Elastic-offset study: crisp output only when more than about 90% of training labels are offset-free.
- Evidence check (S): the gain is in crispness and in pre-NMS scores; at a matched post-processed operating point BSDS500 did not improve. That is the same caution we have: strict IoU against jittered test labels need not rise. The abstract's "17.4% to 30.6%" is not traceable to one table row (the fetch flagged it). Datasets are a few hundred natural images, 3-channel, labels from 4 to 9 annotators (BSDS); ours have one annotator per cell.
- Code: no repository on the arXiv page; none found (unverified elsewhere). Our version needs no code from them: a classical CPU snap.
- Hypothesis (S): snapping each crack label cross-section by at most 2 px onto the darkest point along its normal, keeping each label's own width, gives a cleaner target. Expect relR@2 and component recall of faint cracks up, relP@2 flat, predicted width unchanged, strict IoU flat within noise. Their "ignore unmatched human pixels" rule is a second variant we do not run first (one change per arm).
- Status: **RUN_NOW** (arm `ridge_snap`, after its CPU pre-check A0a).

## Rank 6. Rethinking Generalization: The Impact of Annotation Style on Medical Image Segmentation
- Ids: arXiv 2210.17398 (MELBA 2022; html v3 read).
- Claims (R): conditional instance norm (per-dataset scale and shift, init 1 and 0, every conv block of a 3D nnU-Net, all other weights shared), categorical trial id as the condition. Six proprietary MS trials (390 patients each, 60/20/20). Dice pooled vs trial-conditioned: 0.766 / 0.787, 0.754 / 0.789, 0.756 / 0.788, 0.722 / 0.737, 0.700 / 0.709, 0.738 / 0.744 (gain +0.006 to +0.035). Conditioning on the wrong style: RRMS-A 0.787 to 0.708. A synthetic "small lesions not labelled" style is reproduced on request (small-lesion F1 0.496 vs 0.784 under the two conditions). Few-shot: 10 labelled samples, only the normalisation affine parameters tuned; best 0.834 vs naive 0.819 (the row mapping of that table was ambiguous in the extraction; treat as unverified detail). Image-conditioned FiLM variant: 0.659 to 0.762 on a synthetic dilated-label subgroup.
- Evidence check (S): the convention differences here (lesion size and boundary policy per trial) are of the same kind as our per-source crack width. Differences: blobs not 1 to 2 px lines; 2,340 patients vs our 532 cells (SDLE has 17 in P532); the trial is not visible in the image, while our source is (BMRK padding, contrast), so our model may already adapt implicitly. That is what pre-check A0b measures.
- Code: none found (unverified).
- Hypothesis (S): a 6-entry source embedding (5 sources + "unknown") driving zero-initialised FiLM on the U-Net++ decoder norms lets the model draw ARTS cracks at 1.5 px and BMRK / SDLE at 3 px. Expect per-source predicted width to move toward label width and strict crack IoU up on BMRK / SDLE; relF1@2 flat.
- Status: **RUN_AFTER_GATE** (arm `src_film`; gate = A0b / arm `src_calib` shows per-source room).

## Rank 28. MuGE: Multiple Granularity Edge Detection
- Ids: doi:10.1109/cvpr52733.2024.02452 (CVPR 2024). CVF page and PDF returned 403 / 404 to me; method known from the search-result summary of the CVF abstract only.
- Claims (R, abstract level): a granularity value in [0, 1] is estimated for each annotation by a separately trained, then frozen, granularity network; the value is fused into multi-scale features, with finer control on the high-frequency part; one model outputs edges at any requested granularity. Numbers: not read (unverified).
- Code: github.com/ZhouCX117/UAED (page opened): `train_muge.py`, `test_muge.py`, pretrained granularity network checkpoint; no licence shown on the page; PyTorch inferred from acknowledgements, not stated.
- Hypothesis (S): a continuous per-cell style value (the cell's measured label width, z-scored) is a finer condition than the source id, since width varies inside a source (IQR 1.25 to 2.5 px overall, E). At test time the value is unknown, so it is set to the source median; this makes it a follow-up of `src_film`, not a separate first arm. Their granularity network is replaced by a direct measurement (area / skeleton length of the cell's own crack label).
- Status: **RUN_AFTER_GATE** (variant of arm `src_film`; gate = `src_film` passes).

## Rank 35. PADL: Modeling annotator preference and stochastic annotation error for medical image segmentation
- Ids: doi:10.1016/j.media.2023.103028; arXiv 2111.13410 (html v3 read).
- Claims (R): ResNet-34 U-shaped net; SEM module gives a meta map (mean) and an average stochastic error (sigma) with entropy-guided attention; one HPM module per annotator gives that annotator's mean and sigma; losses BCE on sampled outputs; meta target sampled from all annotations of the image. RIGA (6 annotators, every image labelled by all): cup Dice average 84.18 vs CM-Net 82.77, without HPM 79.24, without SEM 83.65. QUBIQ mean-voting Dice e.g. kidney 80.34 vs CM-Net 76.01, prostate-1 93.30 vs 88.73.
- Evidence check (S): the ablation shows the per-annotator preference part carries most of the gain. PADL needs every image labelled by every annotator; we have one label per cell and the annotator (source) is confounded with the image domain, so preference and stochastic error are not separately identifiable from our data.
- Code: none found on the arXiv page (unverified).
- Hypothesis (S): the preference part is tested by `src_film` (conditioned decoder) and `src_cm` (per-source output model). The sigma heads add sampling cost without an identifiable target here.
- Status: **PARKED** (preference part covered by `src_film` / `src_cm`; stochastic-error part not tested, stays open).

## Rank 38. Weakly-Supervised Crack Detection
- Ids: doi:10.1109/tits.2023.3286934; arXiv 2206.06743 (html read).
- Claims (R): rough labels (pen 1 to 4 px wider than the crack) are refined by a "Myopic" model (3-layer CNN, 3x3 receptive field; loss ignores the top 90th percentile inside label regions and the bottom 90th outside) plus a shrink module that moves outer contour pixels toward the skeleton until the Myopic score rises past a threshold twice in a row; a micro branch multiplies by pixel darkness. Data: Aigle 24 / 14, CFD 71 / 47, DCD 300 / 237. Annotation 22 s vs 656 s per image (CFD). Table II, change vs full supervision: no refinement -0.188 / -0.099 / -0.074; refinement only -0.111 / -0.031 / -0.015; refinement + micro branch +0.156 / -0.026 / +0.018 (Aigle / CFD / DCD, ODS). Thresholds not given.
- Evidence check (S): built for labels that are too wide, not displaced. Our labels are already thin; coarsening them first discards information. The reusable part is the per-dataset appearance model as evidence for where the crack is.
- Code: none found (unverified).
- Hypothesis (S): a per-source myopic classifier (or sklearn model on 3x3 patches, which the paper says may be as effective) as an alternative evidence map inside `ridge_snap`, decided on CPU by pre-check A0a P4. Expected to matter for CSIR, where 16% of crack components are less than 2% darker than their surroundings (E).
- Status: **RUN_AFTER_GATE** (evidence variant of `ridge_snap`; gate = A0a P4).

## Rank 45. Foundation model-guided trust-region label refinement for single-stage bone fracture instance segmentation
- Ids: doi:10.1016/j.engappai.2026.115849 (EngAppAI 2026). The DOI resolves to Elsevier PII S0952197626021330 (E, redirect seen); abstract and full text not retrieved. Everything below is from the scout record, unverified.
- Claims (scout, unverified): FM masks are used only inside a narrow trust region around expert labels, gated by instance IoU, with minimal closing; unconstrained MedSAM pseudo-labels degraded; modest gain in sample-matched ablations under 5-fold CV; mAP@0.5 0.63.
- Evidence check (S): the trust-region rule (move only within a band, gate by agreement, original anchors) is the right safety rule for thin labels and is built into `ridge_snap` (2 px band, keep where evidence is weak). FM evidence for cracks is weak here: frozen SAM2 Hiera-T and DINO probes showed no crack signal (E, BRIEF 5 Foundation encoders row; that closes frozen probes only).
- Code: none known.
- Hypothesis (S): the evidence map can be a model's out-of-fold crack margin instead of the image ridge; with a nested split this is leak-free. Run after `ridge_snap` shows the snap direction is useful.
- Status: **RUN_AFTER_GATE** (arm `oof_snap`; gate named in the spec).

## Rank 47. Disentangling Human Error from the Ground Truth in Segmentation of Medical Images
- Ids: arXiv 2007.15963 (NeurIPS 2020; html v5 read).
- Claims (R): a segmentation net estimates the true class probabilities; an annotator net (shares all but the last decoder layer) outputs per-pixel L x L confusion matrices per annotator; each annotator's predicted distribution = CM x true probs; loss = CE to each annotator's labels + lambda x trace(CM) (lambda 0.7 MS, 1.5 BraTS, 0.9 LIDC). One label per image, MS: Dice 56.43 vs STAPLE 35.74, Spatial STAPLE 38.21, same model without trace 54.76; dense labels MS 67.55 vs 65.77 without trace; oracle CMs 78.86.
- Evidence check (S): works with one label per image, which is our case. Their annotators are simulated or real raters on the same image distribution; ours are confounded with the image domain. Lesion blobs again, not thin lines. The trace term's role (separating preference from truth) is measured: +1.7 Dice MS one-label.
- Code: github.com/moucheng2017/Learn_Noisy_Labels_Medical_Images (page opened): PyTorch per README, MIT licence badge (licence text not read), loss in `Loss.py` per README (file not opened).
- Hypothesis (S): a per-source, per-pixel 2 x 2 crack-vs-rest confusion model on top of the house logits lets the latent output stay source-neutral (for relF1@2, F51, E1) while the source output reproduces each source's width (strict IoU). It is the only arm that yields both a consensus and a source-aware output by construction.
- Status: **RUN_AFTER_GATE** (arm `src_cm`; gate in spec).

## Rank 59. Pixel-accurate road crack detection in presence of inaccurate annotations
- Ids: doi:10.1016/j.neucom.2022.01.051 (Neurocomputing 2022; Rill-Garcia, Dokladalova, Dokladal; HAL hal-03552780). Full text not retrieved (HAL bot wall); no arXiv copy found.
- Claims (R, abstract via search result): U-VGG19 F 71.77% on CrackForest with no tolerance; inaccurate annotations cost up to 20% F on the synthetic Syncrack set; weakly supervised label-noise correction gains up to 12% on Syncrack and also helps on CrackForest and Aigle-RN. Correction procedure: not read (unverified).
- Evidence check (S): direct analogue (thin cracks, misplaced labels, strict scoring). Gains are on synthetic noise; real-data size not read.
- Code: none known.
- Hypothesis (S): model-in-the-loop correction of crack labels inside a trust region, with fold-held-out evidence, is arm `oof_snap`. The Syncrack idea (exact masks + controlled jitter) belongs to the benchmark as a measurement of how much of a method's score is label placement.
- Status: **RUN_AFTER_GATE** (arm `oof_snap`), plus a benchmark note (controlled-jitter study).

---

## Family summary (S)
| Rank | Paper | Status | Arm |
|---|---|---|---|
| 1 | Guided Label Refinement (crispness) | RUN_NOW | ridge_snap |
| 6 | Annotation style (conditional norm) | RUN_AFTER_GATE (A0b) | src_film (and src_calib as its zero-training control) |
| 28 | MuGE | RUN_AFTER_GATE (src_film passes) | src_film variant |
| 35 | PADL | PARKED | (preference part in src_film / src_cm) |
| 38 | Weakly-Supervised Crack Detection | RUN_AFTER_GATE (A0a P4) | ridge_snap evidence variant |
| 45 | FM-guided trust-region refinement | RUN_AFTER_GATE | oof_snap |
| 47 | Disentangling human error (CM) | RUN_AFTER_GATE | src_cm |
| 59 | Pixel-accurate crack detection, inaccurate annotations | RUN_AFTER_GATE | oof_snap |

No paper is VOID: BRIEF section 5 has no run of label editing or source conditioning.
