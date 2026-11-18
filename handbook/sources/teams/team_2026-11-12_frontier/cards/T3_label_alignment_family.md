# T3: training-time handling of misaligned and noisy thin labels (family cards)

Analyst T3, 13 Nov 2026. Tags: **R** = from the paper or its code, **E** = measured in our files (path given), **S** = my judgement.
Research MCP was not available in this session (its tools did not load), so papers were read on arXiv through WebFetch and `pdftotext` copies in the session scratchpad. Code was checked on GitHub.
Companion files: `T3_label_alignment_spec.md` (the arms), `ledger/T3.tsv`.

## 0. Verdicts at a glance

| Rank | Paper | Status | Arm |
|---|---|---|---|
| 4 | MatchED (arXiv:2602.20689) | RUN_NOW | `matched_crack_head` |
| 10 | Study Group Learning (arXiv:2103.03451) | RUN_NOW | `oof_soft_distill` |
| 31 | STEAL (arXiv:1904.07934) | RUN_NOW (with a CPU kill check) | `ridge_snap_labels` (alignment part); NMS loss parked |
| 20 | SelectSeg (doi:10.1016/j.ress.2025.110909) | RUN_AFTER_GATE (G1: nested OOF teachers built and pass the teacher check) | `oof_selective_ignore` |
| 5 | ADELE (arXiv:2110.03740) | RUN_AFTER_GATE (G2: OOF false-alarm audit says confident unlabelled detections are mostly real ridges) | `adele_confident_add` |
| 46 | Spatial Correction (arXiv:2308.02498) | PARKED | none |
| 49 | PNT-Edge (arXiv:2307.14070) | PARKED | none |
| 51 | Align and Segment (arXiv:2607.10841) | PARKED | none |
| 83 | Self-Correction for Human Parsing (arXiv:1910.09777) | PARKED | none (label-averaging idea folded into `adele_confident_add` as a note) |

No paper is VOID. The only related run here is P14 (offset-tolerant CE, R = 2 px, 10% labels, 3 seeds; BRIEF section 5, "Loss" row; `handbook/sources/results/p14__README.md`). It is a many-to-one, max-pool tolerance on the ground truth. None of the nine papers uses that mechanism.

## 1. What this family can and cannot move here (the analysis the arms rest on)

### 1.1 The noise in our crack labels, measured
- **Placement is random, not systematic (E, `data_analysis/benchmark_el_report.md` §4.2).** Over 61,176 label skeleton points, the darkest point along the normal (search ±4 px) is within ±1 px for 48% of points, within ±2 px for 64%, beyond 2 px for 36% (null for random background points: 11%, 21%, 79%). The label-centred mean profile has its minimum at 0 for most source and split groups. The only systematic offset is 0.2 px to the left (−0.09 to −0.47 px by source; ribbons show the same, so it is likely rasterisation).
- **Width is systematic per source (E, same file §4.1).** Label width median ARTS 1.5, CFVS 1.75, CSIR 1.75, BMRK 3.0, SDLE 3.25 px. Visible dark-line FWHM 3.0 to 5.0 px.
- **The labels that mattered most were structural, not offsets (E, P14).** Old labels against revised labels: crack IoU gap +0.082 at 10% labels, robust. The tolerant loss recovered 0% of it (L3To − L3o = −0.004, threshold 0.015). The revision joined dotted labels and added segments. Dotted labels remain in 14 train, 3 val and 5 test cells (≥ 30% of crack px in components ≤ 10 px; 2.5% of train crack px). Unlabelled cracks exist (`CSIR_00094_r16_c5`), and their rate is not measured (benchmark_el_report §4.4, §4.5). The B1 audit flagged crack issues in 24 of 239 train cells (handbook 15).

### 1.2 How tolerance interacts with the metrics
1. **relF1@2 cannot see re-placement within 2 px.** relP@2 counts predicted px within 2 px of ground truth, and relR@2 counts ground-truth px within 2 px of a prediction. If a method only moves where, inside a 2 px band, the model draws a crack, both stay the same to first order. An alignment arm can move relF1@2 only through second-order effects: higher confidence on faint cracks (recall), or fewer stray detections (precision). S.
2. **Strict IoU is where alignment acts, and it sits near a floor.** E (`eval.md` §2.1, BRIEF §3): the 5-seed ensemble scores 0.492 on the clean test, and 70% of its loss (about 0.36 of 0.508) lies within 2 px. A perfect mask shifted 1 px scores 0.547, so all of its 0.453 loss is near-error. The ensemble's near-error loss is therefore already below that of a perfect detector placed 1 px off. S: with random placement, the expected strict IoU of a ridge-centred, label-width prediction against jittered labels is about what the house already gets. Alignment arms should not be expected to add more than about +0.01 to +0.02 strict crack IoU, and the band 0.48 to 0.60 stays the ceiling.
3. **relF1@1** (the lead added relaxed P / R / F1 at 1 and 3 px to the scorer, `LEAD_INSTRUCTIONS.md`) is the metric that sees a ±1 px change. Every T3 arm reports it as the mechanism check, not as a headline.
4. **Width is the trap.** A max-pool tolerance (P14) credits any prediction within R px, so it does not penalise extra width. P14 saw crack AP fall (0.400 to 0.380) and the bin-0 share rise (0.422 to 0.441), with argmax unchanged. One-to-one assignment (MatchED) keeps the number of target px equal to the label count, so it cannot reward width. S: in a 24-class softmax, any re-placement must also say which class the vacated px take. I use the nearest non-crack label of the original mask, never "background" by default (20% of train crack px lie in or at inactive regions, BRIEF §2).
5. **Label correction is scored against uncorrected held-out labels.** A model that learns to find unlabelled cracks is charged false positives on held-out cells that have the same gaps. Arms that add crack (SGL, ADELE) should move relR@2 and component recall up, and may lower relP@2. They are compared at matched predicted width (cross-fitted crack bias) so that an operating-point shift is not read as a gain. S.

### 1.3 Which mechanism fits 1 to 2 px cracks in a 24-class softmax (S)
- **Model-driven one-to-one alignment (MatchED)** fits best mechanically. It removes random placement and keeps width and any convention the model has learned, because the target moves to where the model already fires, at most 2 px, one label px per predicted px. As a separate binary crack head on top of the unchanged 24-class base, it leaves the other 23 classes and the mIoU-R13 path untouched. Its decision rule is exactly the dump format's `pred = where(m_crack > 0, 14, oth)`.
- **Image-driven re-placement (STEAL-style alignment toward the dark ridge)** has a decisive CPU test: do two independent annotations of the same crack agree more after both are snapped? Without that, it is just a different convention from the annotators.
- **Out-of-fold label refinement and selection (SGL, SelectSeg)** attack the structural noise that P14 showed matters (missing and dotted segments, wrong masks). They need a nested fold design to avoid leaking held-out labels.
- **In-run early-learning correction (ADELE, SCHP)** is the same idea without teachers. It risks self-confirmation on scuff and gridline look-alikes, so it waits for an audit.
- **Learned displacement fields (PNT-Edge, AnS)** model systematic or smooth offsets. Measured systematic offset here is 0.2 px, so they are parked.

## 2. Paper cards

### Rank 4. MatchED: Crisp Edge Detection Using End-to-End, Matching-based Supervision
- **Ids / links:** arXiv:2602.20689, CVPR 2026. Project https://cvpr26-matched.github.io. Code https://github.com/Bedrettin-Cetinkaya/MatchED (verified, 16 commits).
- **What it claims (R, HTML full text, first half read: method, ablations, main tables).** A head of about 21K parameters (five Conv-ReLU-Norm blocks plus a final conv and sigmoid) is appended to a base edge detector. Each step, confident predicted px (`E^c ≥ τc`) are matched one-to-one to ground-truth edge px by linear sum assignment with cost `d(p_c, p_g) − α·E^c(p_c)` (d = Manhattan distance; cost ∞ if d ≥ τd). Matched ground truth moves to the prediction's position; unmatched ground truth stays; the head is trained with pixel BCE; `L = β·L_MatchED + L_f`. The base trains alone for the first half of the epochs, then jointly. Numbers:
  - BSDS, crispness evaluation (no NMS): PiDiNet ODS 0.578 to 0.800, AC 0.202 to 0.919; SAUGE 0.700 to 0.854.
  - NYUD: PiDiNet 0.399 to 0.736.
  - BIPED (thin, standard): PiDiNet post-processed base 0.892 to 0.900 without post-processing; DiffusionEdge 0.885 to 0.889.
  - Ablations (BSDS, PiDiNet): τc 0.01 to 0.10 gives ODS 0.799 to 0.800, 0.30 gives 0.761; τd 2 to 8 gives 0.797 to 0.800; α 5 gives 0.630, α 25 gives 0.800.
  - Memory 28.32 GB at 320 × 320 with a low τc; splitting into 4 patches reduces it.
- **Evidence check.** The large gains are against thick raw outputs under crispness-emphasised evaluation. On BIPED, the closest to thin, standard evaluation, the gain is +0.004 to +0.008 ODS (R). The paper text has small inconsistencies: its runtime claims disagree with its own table (NMS 25.69 s against MatchED 32.98 s), and α / τd per dataset differ between the paper and the code comment (code: BSDS τd 4, α 5; NYUD 8, 20; BIPED 11, 55). The second half of the HTML and the supplement (Multi-Cue) were not read. No one-to-one against many-to-one ablation was found.
- **Code (R, `utils.py` read).** `create_1to1_Label`: candidates `pred ≥ delta`, cost `|Δw| + |Δh| − weight·pred`, entries with spatial distance above `max_toleration` set to 10000, `scipy.optimize.linear_sum_assignment`. The new target is 1 at matched predictions and at unmatched ground truth, and 0 elsewhere, including confident unmatched predictions. `bce_entropy` tiles each image into 4 × 4 patches before matching. PyTorch, built on PiDiNet. **No licence file**: treat as all rights reserved and reimplement (about 80 lines).
- **Our data (E).** The house output is not thick: the predicted / ground-truth crack px ratio is 0.95 on test (PROTOCOL_DRAFT §5.1). So the headline mechanism (thinning thick output) does not apply.
- **Hypothesis (S).** Random ±1 to 2 px placement makes the same crack appearance carry inconsistent targets across cells. That lowers confidence on faint cracks, and component recall and relR@2 suffer. A matched crack head gets consistent, width-preserving targets. Expected: relF1@1 +0.01 to +0.03; strict crack IoU +0.00 to +0.015; relR@2 and component recall up by about 0.01; width ratio unchanged (one-to-one); false alarms flat or down (confident unmatched px become negatives). A CPU simulation decides first whether plain CE argmax already centres lines under random jitter (spec, P-M4).
- **Status: RUN_NOW**, arm `matched_crack_head`. Bench: if it passes, it is the benchmark's "noisy-label training" entry.

### Rank 10. Study Group Learning: Improving Retinal Vessel Segmentation Trained with Noisy Labels (SGL)
- **Ids / links:** arXiv:2103.03451, MICCAI 2021. Code https://github.com/SHI-Labs/SGL-Retinal-Vessel-Segmentation (verified; MIT; PyTorch; `sgl_labeling/run_drive_k8.sh`, `sgl_training/run_train.sh`).
- **What it claims (R, PDF read).** Split the training set into K subsets and train K models, each on the other K−1 subsets. Each model predicts its held-out subset, giving pseudo-labels Ĩ. Train a final model from scratch with `L = CE(Î, I) + λ·CE(Î, Ĩ)`, λ = 1. Also proposes label erasing (remove thin vessel segments by rank of thickness) to simulate missing labels. Numbers, single runs, no seeds:
  - DRIVE Dice 0.8262 to 0.8316 (K = 8), AUC 0.9867 to 0.9886.
  - CHASE_DB1 Dice 0.8232 to 0.8271, AUC 0.9913 to 0.9920.
  - K ablation (DRIVE, clean labels), AUC: K 1 0.9867, K 2 0.9884, K 4 0.9887, K 8 0.9886.
  - With 30% of vessel labels erased: AUC 0.9858 (K 1) to 0.9882 (K 8).
- **Evidence check.** Gains are small (Dice +0.004 to +0.005) and from one run each. Thin structures and tens of images make it the closest setting to ours. Erasing only simulates missing labels, never misplacement.
- **Hypothesis (S).** Out-of-fold soft targets carry (a) segments that annotators missed or dotted, and (b) ensemble-like smoothing (our only clear win so far is a 5-seed ensemble, +0.014 to +0.018 crack IoU, E BRIEF §3). Distilling them should raise relR@2 and component recall at equal relP@2.
- **Adaptation.** Distil on a 3-way grouping {crack, inactive, rest} so that the other classes keep their exact supervision. The OOF teachers must be nested so that no held-out label reaches a student: 10 teachers, each trained on 3 folds. Label erasing is parked.
- **Status: RUN_NOW**, arm `oof_soft_distill`.

### Rank 31. STEAL: Devil Is in the Edges: Learning Semantic Boundaries From Noisy Annotations
- **Ids / links:** arXiv:1904.07934 (doi:10.1109/cvpr.2019.01133), CVPR 2019. Code https://github.com/nv-tlabs/STEAL (verified; NVIDIA BSD-style licence text in the README; PyTorch 0.4; **inference code only**, so the NMS loss and active alignment are not released).
- **What it claims (R, PDF read).** Two parts:
  - **Thinning layer / NMS loss:** at each positive ground-truth px, a softmax with temperature τ = 0.1 over 2L + 1 = 5 samples along the ground-truth normal (bilinear), with a Dirac target, plus a direction loss. Weights α1 = 1 (BCE), α2 = 10 (NMS), α3 = 1.
  - **Active alignment:** the noisy edge is evolved as a level set (geodesic active contour, `g = λ/√(1+y) + 1/√(1+f)`) toward high network response near the label, every 5k iterations from 55k of about 70k, λ = 1.
  - Results, SBD re-annotated test, MF(ODS) %: CASENet 63.52; NMS loss without test NMS 64.99; with test NMS 67.87; plus active alignment 68.15. On the original noisy test set alignment scores 64.83 against 65.93. Row mapping inferred from the text's quoted deltas (+1.94 / +1.47), so it is S on the exact row labels.
  - Table 4: alignment 64.10 to 68.15 on real noise (about 4 px error); 52.69 to 56.41 with +8 px synthetic error.
  - Evaluation tolerance 0.0075 of the diagonal (SBD).
- **Evidence check.** The labels are 1 px boundaries with about 4 px error, larger than ours (1 to 2 px). Alignment helps on the clean re-annotated test and not on the noisy original test. That is the same trap we face: scoring is on unaligned labels.
- **Hypothesis (S).** The NMS loss targets thick, multi-peak output. Ours is 0.95 width ratio, and for 2 to 3 px wide labels a Dirac target per positive px is ill-posed (adjacent positives compete), so it is parked. The alignment idea is tested in the form with a decisive CPU check: snap train labels toward the image's dark ridge within ±2 px, keeping each component's width. The CPU check asks whether snapping makes independent annotations of the same crack agree more. The model-driven variant of alignment is covered by `matched_crack_head`.
- **Status: RUN_NOW**, arm `ridge_snap_labels`; its CPU pre-check can kill it before any GPU use.

### Rank 20. SelectSeg: Uncertainty-based selective training and prediction for accurate crack segmentation under limited data and noisy annotations
- **Ids / links:** doi:10.1016/j.ress.2025.110909, Reliability Engineering & System Safety 259 (2025). No code found. Companion data: "CRACK500 with noisy annotation masks", Mendeley doi:10.17632/wddt4gbttd.1 (10, 20, 50, 100% of masks noised).
- **What it claims (R, web listing only; full text not reachable off campus).** Four stages: a deep ensemble estimates crack uncertainty, uncertainty filtering removes likely mislabelled annotations, training on the rest, and selective prediction (abstention). It beats existing methods on real crack data with noisy annotations; both selective training and selective prediction help. **No number retrieved. Unverified whether filtering is per pixel or per image.**
- **Hypothesis (S).** Supervising against wrong crack px (a mask from another cell, as in `BMRK_00031`, which v1.1 fixes; scuff-like px; px with no visible ridge) teaches false alarms and suppresses true ones. Ignoring px where the nested OOF teacher strongly disagrees should raise relP@2 and strict IoU without new labels. It reuses `oof_soft_distill`'s teachers, so it costs about 11 GPU-h.
- **Status: RUN_AFTER_GATE.** Gate G1: the 10 nested teachers exist and pass the teacher check in the spec (OOF crack relF1@2 ≥ 0.75, crack IoU ≥ 0.30), and the flag-rate pre-check passes. Arm `oof_selective_ignore`. Abstention belongs to the benchmark's reliability output, not to this arm.

### Rank 5. ADELE: Adaptive Early-Learning Correction for Segmentation from Noisy Annotations
- **Ids / links:** arXiv:2110.03740 (doi:10.1109/cvpr52688.2022.00263), CVPR 2022. Code https://github.com/Kangningthu/ADELE (verified; MIT; label correction included: `--label-correction`, `tau_fg`, `tau_bg`).
- **What it claims (R, PDF read including Appendix B).** Memorisation starts at different times per class. Per class, fit `f(t) = a(1 − exp(−b·t^c))` to the training IoU against the noisy labels. Start correcting class c when `|f′(1) − f′(t)| / |f′(1)| > r = 0.9`. Then set `y[q_c ≥ τ] = argmax q` with τ = 0.8, where q averages outputs over scales 0.7, 1, 1.5. Multiscale consistency regulariser: KL to the average, where max q > ρ = 0.8, λ = 1. Numbers:
  - SegTHOR with simulated dilation / erosion noise (noisy-label mIoU 0.6), last-epoch val mIoU %: single scale 58.8 to 65.2 with correction; multiscale input 60.7 to 69.8; plus consistency 62.5 to 72.2.
  - PASCAL VOC WSSS: 64.5 to 65.6, 65.5 to 67.3, 66.7 to 69.3.
  - Correcting all classes at once is detrimental (text, Table 1).
- **Evidence check.** The noise is blob dilation and erosion of organs, not thin-line placement. Rescaling by 0.7 / 1.5 changes crack width in px and is not label-safe here.
- **Hypothesis (S).** After the early-learning point, confident (q ≥ 0.8) crack components that lie mostly outside the 2 px label band are unlabelled cracks. Adding them stops the loss from suppressing real faint cracks, so relR@2 and component recall rise. Additions inside the band are banned, so labels cannot widen. Risk: confident scuff, gridline or dark-spot detections become crack labels. That is why gate G2 exists.
- **Status: RUN_AFTER_GATE.** Gate G2 (CPU, on the wave-1 OOF dumps of `house_r34_unetpp_pf`): among confident (p ≥ 0.8) predicted crack components of at least 10 px that lie more than 2 px from ground-truth crack, at least 50% of px have a visible dark ridge (relative darkness ≥ 0.03 against a 2 to 4 px ring, as in benchmark_el_report §4.3), and such components occur in at least 20 cells. Arm `adele_confident_add`.

### Rank 46. Learning to Segment from Noisy Annotations: A Spatial Correction Approach
- **Ids / links:** arXiv:2308.02498, ICLR 2023. Code https://github.com/michaelofsbu/SpatialCorrection (link from the paper; repository contents and licence not checked).
- **What it claims (R, method and Algorithm 1 read; result tables not read).** Label noise is a Markov chain of boundary expansion and shrinkage steps with bias θ1 and marching probability θ2. Correction:
  - estimate the boundary bias Δ (in px of signed distance) on a **small clean validation set** (Eq. 6);
  - shift the logits by `λ·exp(−φ̂² / (2(γΔ)²))` (Eq. 8);
  - retrain; repeat while |Δ| ≥ 1 px (usually one iteration).
  Datasets: JSRT, ISIC 2017, BraTS 2020 (synthetic noise), Cityscapes (real noise). It needs clean validation labels, and the paper proves only a few clean images are needed.
- **Evidence check (E).** We have no clean crack labels (one double-annotated image, `CFVS_00015` = `CFVS_00016`, IoU 0.259). The measured systematic offset is 0.2 px, below the algorithm's own stopping rule of |Δ| < 1 px, so it would stop at once. Width bias per source (BMRK 3.0 against FWHM 5.0) is a convention that the held-out labels share.
- **Status: PARKED.** It could become useful only as a noise generator for a benchmark stress track (inject controlled boundary noise into labels and measure each method's drop). That is a benchmark design choice for the lead, not a score arm. Its "correct toward the true boundary" idea is tested by `ridge_snap_labels` with the image ridge in place of clean validation labels.

### Rank 49. PNT-Edge: Towards Robust Edge Detection with Noisy Labels by Learning Pixel-level Noise Transitions
- **Ids / links:** arXiv:2307.14070 (doi:10.1145/3581783.3612136), ACM MM 2023. Code https://github.com/DREAMXFAR/PNT-Edge (verified; torch 1.8.1; PSL training script present; **no licence file seen**).
- **What it claims (R, HTML read).** A 4-layer FCN (PSL) takes the image, confident predictions (τ = 0.1) and the noisy label, and outputs a displacement field that warps the **prediction** onto the noisy label. Loss weights: shift MSE on confident px α1 = 0.01, similarity α2 = 1, smoothness α3 = 0 ("useless"), local edge density α4 = 3. Then joint training with the PSL frozen, plus an unmatched-px loss −log(1 − ŷ). Warm-up is selected at the memorisation point (about epoch 20 of 30). Numbers:
  - SBD re-annotated, raw ODS-F: CASENet 0.559, CASENet-S 0.603, SEAL 0.644, STEAL 0.606, PNT-Edge 0.667; thinned: 0.635 / 0.658 / 0.669 / 0.677 / 0.682.
  - Ablation (val-clean): ODS-F 0.653 to 0.666, mAP 0.579 to 0.623 at τ 0.1, α4 3.
  - Label correction instead of joint training: 0.610 against 0.652.
  - Tolerance about 4 px (SBD).
- **Evidence check.** The gains are 1 to 2 ODS points at a 4 px tolerance on 1 px boundaries. The memorisation-point warm-up is borrowed from ADELE.
- **Status: PARKED.** It models a smooth, partly systematic displacement. Ours is random per point (E §1.1), and a dense warp per cell adds about 10 build hours and three training stages. Revive if `matched_crack_head` passes and its τd = 0 control shows the gain comes from alignment: a learned smooth warp is then the next step. Its "mean learned shift per source" would also be a label-quality number for the benchmark.

### Rank 51. Align and Segment: Unsupervised Learning for Building Segmentation From Misaligned Labels (AnS)
- **Ids / links:** arXiv:2607.10841 (v1, 12 Jul 2026; no venue on the listing). Code https://github.com/venkanna37/align-and-segment (link from the abstract page; not opened).
- **What it claims (R, abstract only).** A spatial transformer applies an **affine** transform to the labels during training. A self-supervised regulariser plus augmentation stop the segmenter from learning the misalignment. No golden labels are needed. Synthetic and real misaligned OpenStreetMap building labels in several cities. No number read.
- **Evidence check.** Abstract-level only. A per-image affine model fits systematic map-to-image offsets, not per-point jitter (E §1.1: no systematic offset beyond 0.2 px).
- **Status: PARKED.** The scout's per-source renderer adaptation (learn width and sub-pixel shift per source) addresses a real systematic effect (label width 1.5 to 3.25 px by source, E). But the 24-class model already sees the source in the image (BMRK cells are downscaled and padded), so the expected gain is small (S). Revive only if per-source tables on CV5-G show strict IoU losses that a width change explains, for example if BMRK predicted width differs from its 3.0 px labels by more than 30%.

### Rank 83. Self-Correction for Human Parsing (SCHP)
- **Ids / links:** arXiv:1910.09777 (doi:10.1109/tpami.2020.3048039). Code https://github.com/PeikeLi/Self-Correction-Human-Parsing (from the abstract page; not opened).
- **What it claims (R, abstract).** Cyclical learning rate. At each cycle, the model is aggregated with its best earlier version and pseudo-masks are refined, so model and labels improve together. First place in the CVPR 2019 LIP challenge; best on LIP and Pascal-Person-Part. No number read here.
- **Status: PARKED.** It has two parts. Weight aggregation (an SWA / EMA relative) belongs to the optimizer family (BRIEF §5: EMA / SWA never varied), not to label handling. Label averaging is a soft form of ADELE's correction; it is noted as a variant inside `adele_confident_add`. Its main target (ambiguous boundaries between many parts) maps to gridline, splice and edge_dark (BRIEF §3). Those classes are not label-alignment problems in our evidence, and their recall (gridline 0.33) is a detection problem.

## 3. What the family adds to the benchmark (S)
- **Measured label agreement after alignment:** pair IoU and relF1@1 of independent annotations before and after ridge snapping (pre-check P-RS1). This is a label-ceiling number the benchmark can print beside strict IoU, at no GPU cost.
- **relF1@1 as the alignment-sensitive column**, beside relF1@2 (invariant to ≤ 2 px re-placement) and strict IoU.
- **A "noisy-label training" row:** whichever of `matched_crack_head` or `oof_soft_distill` passes, run at 5 seeds under the protocol.
- **A nested OOF teacher set** (10 models, 3 folds each), which is also a 60%-data point on the label-efficiency curve.

## 4. Sources actually read
- arXiv HTML: 2602.20689 (first 100k characters), 2307.14070v2. arXiv PDFs via `pdftotext`: 1904.07934, 2110.03740, 2103.03451, 2308.02498 (method and Algorithm 1). Abstract pages: 2607.10841, 1910.09777. Web listing: doi:10.1016/j.ress.2025.110909.
- GitHub pages: MatchED (and `utils.py`), STEAL, ADELE, SGL, PNT-Edge.
- Project files: `BRIEF.md`; `benchmark/PROTOCOL_DRAFT.md`; `benchmark/LABELS_V11.md`; `harness/DESIGN.md`; `harness/LEAD_INSTRUCTIONS.md`; `harness/src_snap/el_f3/src/losses/{tolerant_pl,ce_dice}.py`; `harness/src_snap/el_thin/src/losses/{loss_factory,thin_crack}.py`; `harness/src_snap/el_thin/src/trainers/trainer.py` (loss call); `el_f3/scripts/train.py` (PF split); `smp050/base/model.py`; `protocols/P14_tolerant_supervision.md`; `handbook/sources/results/p14__README.md`; `data_analysis/benchmark_el_report.md` §4.
