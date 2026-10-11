# 05. Literature and baselines: what the papers claim, how they measure, and what we found when we checked

## What this covers

Every paper this project uses, reproduces, argues against or borrows a mechanism from. For each one: what it claims, its data, its metric and how that metric is computed, the numbers it reports, and what happened when we reproduced it or compared against it. The central lesson of the reproduction work is that most "gaps" between our numbers and published numbers were metric conventions, checkpoint selection or training budgets, not method differences. The second half maps the wider literature (SSL, rare classes, thin structures, fair evaluation, pretraining) onto our experiments, and records the 10 Oct directions survey that shaped the P-series.

Old-era numbers (original masks, from-scratch U-Net++, weighted CE, batch 4, SemiCE) are kept in their own tables and marked. P-series numbers appear only as cross-references, with their source file.

## Sources

- `literature/survey.md` (8 Oct; 69 verified sources; ARS lit-review form)
- `literature/papers_index.md` (index of the 69 papers with links and read scope)
- `literature/reading_list.md` (prioritised reading list; top 10 in order: ALHVR, Torpey 2024, Pratt 2023 (+ Pratt 2021 and the thesis), DHC, AEL, DARS, BUR, Oliver + UniMatch V2 + Yuan, Skeleton Recall + clDice, Metrics Reloaded + What's Cracking)
- `literature/notes/A01`–`A08` (EL segmentation papers), `B01`–`B06` (SSL and rare-class SSL), `C01`–`C03` (thin structures, metrics, label-efficient crack work), `D01` (fair SSL evaluation), `E01` (pretraining without pseudo-labels), `F01`–`F05` (10 Oct scout passes: rare-class SSL 2024–2026, self-supervision and foundation models, noisy/thin/weak/synthetic, EL dataset census, institutional PDFs)
- `analysis/papers_metrics.md` (metric conventions, recipes, our numbers against theirs; with a correction appended 8 Oct)
- `analysis/alhvr_audit.md` (our ALHVR port and the shared SSL loop against the reference code)
- `to_human/directions_2026-10-10.md` (directions survey, with 10 Oct night and 11 Oct morning updates)
- `to_human/situation_report_2026-10-08.md` (sections 4 and 5)
- gaint `/home/noob/work/el-fault-detection/docs/alhvr_port_notes.md`; configs `configs/alhvr.yaml`, `pratt_unet.yaml`, `ucf_deeplab.yaml`, `ucf_pvs3*.yaml`
- `~/mtp/MTP_session_handoff_2026-10-07.md` (sections 4.5, 6.9–6.11, 9.1)
- The user's pasted phase 0 / phase 1 handoffs (11 Oct; copy in `sources/chat/phase0_phase1_handoffs_pasted_2026-10-11.md`)
- PDFs: `literature/pdfs/` (open access), `literature/pdfs_inst/` (institutional access, IIT Mandi), `~/mtp/research/papers/` (MultiSolSegment), gaint `/home/noob/work/docs/papers/` (7 PDFs: ALHVR, Mean Teacher, UniMatch, Pratt 2023, Jha PV-S3, Fioresi, Gangopadhyay). **All PDFs stay local and must not be redistributed** (`to_human/directions_2026-10-10.md` §7).

Provenance tags used below, as in the sources: **[paper]** stated by the authors; **[code]** read from released code; **[ours]** measured by us; **[inferred]** reasoning, not stated anywhere.

---

## 1. The field in one paragraph

Pixel-level, multi-class EL segmentation rests on two public datasets: **BenchmarkEL** (Pratt et al. 2021, 2023; Torpey et al. 2024; Pratt thesis 2024) and **UCF-EL** (Fioresi et al. 2022; Jha et al. PV-S3 2025). Semi-supervised (SSL) work on EL segmentation is limited to two efforts: **PV-S3** (Mean Teacher with SemiCE) and **Torpey et al. 2024** (CCT and U2PL as pretraining regimes, full label budget only). No EL paper found reports an SSL label-efficiency curve against step-matched supervised baselines with loss-off controls (`literature/survey.md` §A; bounded by the searches made). A properly controlled label-efficiency study on EL is itself missing from the literature (`literature/survey.md`, Gaps item 1).

---

## 2. Metric conventions: the central lesson

Many published numbers cannot be compared with each other or with ours unless the convention is matched. The table is from `analysis/papers_metrics.md` §0.

| Paper | Unit of IoU | Aggregation | Background | Absent classes / images | Classes scored | Checkpoint |
|---|---|---|---|---|---|---|
| **Pratt 2023** | per image, per class | **median over the 50 test images** (§3.4) | not scored | not stated (see §3.1 below) | crack, gridline, inactive (+ ribbons, spacing) of 24 trained | not stated |
| **Fioresi 2022** | pixel level, dataset level (sklearn reports) | per-class P / R / F1; IoU formula given but no IoU table | no-defect class in the weighted F1 (0.95) and unweighted F1 (0.69) | – | 4 defects (+ no-defect) | "After each epoch, we validate the model on the validation/testing set": one held-out set, so selection on test is likely [inferred] |
| **Jha PV-S3 2025** | dataset level, Eq. 9 | mean over 4 defect classes | not in the class set; released code `ignore_index=0`, background never predicted | – | 4 UCF defects; on CSB-S1: crack, gridline, inactive | not stated; released split lists put 1,769 of 2,289 public test images in train and 437 in val [ours] |
| **Gangopadhyay 2025** (SA-UNet++) | probably per image [inferred] | mean over classes | **included** (accuracy 1.00 for every model on T2) | – | MIAD: good / broken / foreign body / missing cells | ReduceLROnPlateau + EarlyStopping; monitor not stated |
| **ALHVR 2025** | per 3-D case, per foreground class (medpy `dc`) [code] | mean over cases, then classes | excluded | empty prediction scores Dice 0 [code] | 3 ACDC structures | **best val Dice**, every 200 iterations on 10 val patients [code] |
| **Ours** | one dataset-level confusion matrix (`standard`) | mean of crack + inactive (BenchmarkEL), 4 defects (UCF) | in the confusion matrix, so false positives on background count | absent class is NaN, left out of means | as left | final step (primary) |

Named conventions our metrics module computes (`MTP_session_handoff_2026-10-07.md` §4.2; phase 1 handoff §5):

| Name | Definition | Where used |
|---|---|---|
| `standard` | one global confusion matrix over all pixels (ignore label respected); mean over defect classes | our default; Fioresi 4-class |
| Fioresi 5-class | same, background included | Fioresi abstract 57.3 |
| `pvs3` | drop every pixel whose ground truth is background, then build the matrix. Recall is unchanged; only background false positives vanish (TP and FN are defect-GT pixels, so dropping background-GT pixels touches neither) | Jha's code |
| `pratt_median` | IoU per image per class, median over test images; rules A (leave absent images out), B (absent scores 0), C (absent and unpredicted scores 1) | Pratt 2023 |

Two general warnings that run through the whole project:
- **A metric that improves when predictions are dilated, or when the background threshold is raised, rewards false alarms** (phase 1 handoff §5).
- **Per class, IoU = F1 / (2 − F1) exactly** at dataset level (phase 1 handoff §2; `analysis/papers_metrics.md` §2.3). So an IoU mean over the same classes can never exceed the F1 mean when every class is strictly between 0 and 1.

---

## 3. BenchmarkEL line (Pratt, Torpey)

### 3.1 Pratt, Mattheus, Klein 2023: BenchmarkEL (Systems and Soft Computing 5, 200048)

Our main dataset's paper. Read in full (`literature/notes/A01_pratt2023_benchmarkel.md`; `analysis/papers_metrics.md` §1).

**Data [paper]**
- Abstract: "593 cell images", 24 classes (12 features, 12 defects). The public `dataset_20211104` has 478 + 54 + 50 = 582. Eleven images are unaccounted for [inferred, minor].
- §3.2: "Fifty images with a prevalence of cracks, gridline defects, and inactive areas were assigned to testing, evenly split for mono- and multi-silicon wafers." **The test set was hand-picked for defects, not random.** Fifty-four val images were random.
- Training images augmented offline with 180° rotation, mirror and flip to 1,912 = 4 × 478.
- 512 × 512 per image.
- Median ground-truth pixels per test image: crack 557, inactive 1,288, gridline 1,750, spacing 12,529, ribbons 12,871.

**Recipe [paper]**
- Four models (Table 1): U-Net_12 (12.3M params), U-Net_25 (25.9M), PSPNet (58.0M), DeepLabv3+ (22.4M). The encoder is not named. (VGG16 in our reproduction came from the user's spec, not the paper.)
- Weighted CE with three weight sets: **A** all 1; **B** inverse median pixel percentage per class; **C** custom: background 0.2, ribbons 3, gridline 10, inactive 10, crack 20, others 1 (Table 2).
- **No optimiser, learning rate, epochs, batch size or schedule stated.** Custom weights were "validated with a 16-run screening DOE" on an unstated split.
- [inferred] Set B divides by a median share that is 0 for any class absent from more than half the images, so B weights for rare classes are infinite or arbitrary; the 1b, 2b and 3b rows score 0.00 inactive IoU and recall (4b scores 0.20; `analysis/papers_metrics.md` §1.2–1.3).

**Numbers [paper, Fig. 7 median IoU, Fig. 8 median recall]** (`analysis/papers_metrics.md` §1.3)

| Model | crack | gridline | inactive | avg defects | crack recall |
|---|---|---|---|---|---|
| 1a U-Net_12 equal | 0.13 | 0.32 | 0.25 | 0.24 | 0.14 |
| 1c U-Net_12 custom | 0.26 | 0.22 | 0.00 | 0.16 | 0.90 |
| 2a U-Net_25 equal | 0.15 | 0.32 | 0.09 | 0.19 | 0.18 |
| 2c U-Net_25 custom | 0.22 | 0.18 | 0.00 | 0.13 | 0.89 |
| 3c PSPNet custom | 0.17 | 0.14 | 0.11 | 0.14 | 0.43 |
| 4b DeepLabv3+ inverse | 0.18 | 0.14 | 0.20 | 0.17 | 0.93 |
| **4c DeepLabv3+ custom (headline)** | **0.25** | 0.20 | 0.38 | **0.28** | **0.86** |

Abstract: "the mIoU for cracks is low (25%) even for the DeepLabv3+, the recall is high (86%)". §4 attributes low defect IoU to low precision "driven more by dilated predictions". So **low crack precision under weighted CE is a known property of this benchmark, not something our pipeline created** (`analysis/papers_metrics.md` §1.3).

**The absent-class rule (a documented conflict).**
- `analysis/papers_metrics.md` §0 (8 Oct): the paper's nonzero inactive medians (0.38 for 4c) with inactive in only 17 of 50 test images (old masks) rule out rule B (absent = 0 forces the median to 0); 4a's inactive median 0.13 with recall 0.15 rules out rule C. **So rule A, or a close variant, fits the paper [inferred].**
- The phase 1 handoff (§5, §7b) called rule B "primary, reproduces Pratt" and reported old-era rule-B numbers from what it calls the "new pipeline" (Set C 0.116, Set A 0.145 against the paper's U-Nets 0.133–0.160, "approximately reproduced").
- `analysis/papers_metrics.md` §1.4 resolves this as: the apparent gap in day1 came from comparing our rule-B means with the paper's numbers, which cannot be rule B. The choice of absent-class rule changes the mean about 3× (our rule B → C: 0.15 → 0.49; `analysis/papers_metrics.md` §1.5). Treat rule A as the better-supported reading; the paper itself does not say.

**Ours against theirs (old era, `analysis/papers_metrics.md` §1.4; from gaint `reports/day1.md`)**

| Our run (old-era, rule A unless stated) | crack | gridline | inactive | mean | Paper comparison |
|---|---|---|---|---|---|
| Pratt-A (smp U-Net VGG16, equal weights, final) | 0.149 | 0.339 | 0.420 | **0.303** | 2a: 0.15 / 0.32 / 0.09 (avg 0.19) |
| Pratt-C final | 0.176 | 0.207 | 0.445 | **0.276** | 2c: 0.22 / 0.18 / 0.00; 1c: 0.26 / 0.22 / 0.00 |
| Pilot U-Net++ arms (SL-100, SL-20, MT-20, ALHVR interim) | | | | 0.280 / 0.287 / 0.288 / 0.295 | best 4c: 0.28 |
| Crack median, our U-Net++ arms (crack is in all 50 test images, so every rule gives the same value) | 0.21–0.25 | | | | paper 0.13–0.26 |

**Verdict: no reproduction gap remains on BenchmarkEL once the convention is aligned** (`analysis/papers_metrics.md` §1.4). Dataset-level `standard` crack IoU (ours 0.25–0.30) is higher than per-image median crack IoU (0.15–0.25), because pooling weights big-crack images more [inferred from definitions].

**Weaknesses (`literature/notes/A01`; `literature/survey.md` §A table)**
- Hand-picked defect-rich test set: all 50 test images contain crack (old masks; 48 of 50 on the revised masks, `results/p6/README.md`); this inflates crack recall and hides label effects on inactive [author-acknowledged that the test set was chosen; effect ours].
- Per-image median IoU; absent-class rule not stated.
- One run per model; no training details; DOE weights tuned on an unstated split, possibly test.

**Version caveat (open).** `literature/notes/F03` §6: PV-DDPM cites "SCDD" = the 20221008 release (695 labelled, 29 classes), and the BenchmarkEL README says later versions correct earlier masks. The handoff says 20211104 matches Pratt 2023 (24 classes, 50 test). **Which release Pratt 2023 used should be re-checked** [open]. See `03_datasets_and_splits.md` for the three releases.

### 3.2 Pratt, Govender, Klein 2021 (Renewable Energy 178, 1211–1222)

The origin of the BenchmarkEL line: U-Net segmentation of mono and multi-Si EL images, with defect quantification at factory and plant level. Read at abstract level in the notes (`literature/notes/A05_pratt2021_unet.md`); a copy was later obtained through institutional access (`literature/pdfs_inst/pratt2021`) and "read by the parent" (`literature/notes/F05` header). It is the most likely source for the annotation protocol (crack width, crack across busbars, dotted lines), which our crack-label findings depend on (`literature/notes/F04_paywalled_queue.md` item 1).

### 3.3 Pratt PhD thesis (Wits 2024) and the Pratt group's power studies

- Thesis: 765 labelled images plus 20,000+ unlabelled; progresses from supervised to semi- and self-supervised pretraining; "DeepLabv3+ trained with custom class weights scored the highest" [abstract] (`literature/notes/A06`).
- Power-degradation study (CSIR repository, venue unconfirmed): 680 fielded modules, 48,960 cells classified into 29 classes; a new "brightening" defect (24 labelled samples) correlates with module fill factor, r² = 0.42 (`literature/notes/A06`; also Pratt 2025 ICTAS, `literature/notes/F05`).
- Relevance: part 3 of the thesis (severity). Per-defect area, not mIoU, is what links to power loss. Power loss is **not part of this project** unless valid data appears (user, 11 Oct; see `01_project_overview_and_scope.md`).

### 3.4 Torpey, Pratt, Klein 2024: pretraining paradigms for EL defect detection (arXiv 2402.17611)

**The closest prior evidence on our data family** (`literature/notes/A02`, `F02`). Read: sections.

- Data: 642 labelled EL images (= BenchmarkEL release `20220723`, per `literature/notes/F04` §1a, so a different test set from Pratt 2023 and from ours), 22,000 unlabelled EL images (`A02` says released, but arXiv v1 redacts the URLs, so no public link was found; `F02`, `F04` §2), a 5,000-image subset for the SSL regimes. Model: DeepLabV3 ResNet-50. Metric: mIoU; "results on the test set for the best model ... on a validation dataset"; several runs per regime; Tukey HSD.
- Table 1 mIoU (full labels):

| Regime | Pretraining | mIoU |
|---|---|---|
| R1 | random init | 0.486 |
| R0 | prior SOTA (DeepLabV3+ R34) | 0.506 |
| R2 | COCO supervised segmentation | 0.544 |
| R3 | ImageNet supervised | 0.508 |
| R4 | ImageNet SimCLR | 0.534 |
| R5 | ImageNet MoCov2 | 0.508 |
| R6 | **EL SimCLR (in-domain, 22k)** | **0.517** |
| R7 | **CCT (semi-supervised)** | **0.550** |
| R8 | **U2PL** | **0.448** (below random init) |

- COCO, IN-SimCLR and CCT are "statistically equivalent" [paper]. On crack, "R2 and R4 outperform all other models" (p ≤ 0.0001), including CCT; "R4 performed better than R6" [paper] (`literature/notes/F02` item 1).
- Weaknesses: full label set only (no label-fraction curve), best-val checkpoint, single runs for R7/R8, no masked-image modelling.
- Lessons for us: a standard SSL method (U2PL) is worse than no pretraining on EL; in-domain contrastive pretraining loses to ImageNet contrastive, most on crack; rare defects are "underrepresented, so training and statistical analysis are challenging" [paper].

---

## 4. UCF-EL line (Fioresi, Jha)

### 4.1 Fioresi et al. 2022: UCF-EL (IEEE J. Photovoltaics 12(1))

Read in full (`literature/notes/A03`; `analysis/papers_metrics.md` §2).

**Data [paper]**
- 17,064 images = 16,808 real + 256 Griddler-simulated. Defect-free images removed ("We ignore images without defects").
- Four defect categories: crack (closed + resistive + isolated), contact (front-grid interruption + near busbar), interconnect (highly resistive), corrosion. "Disconnected interconnects are currently ignored". A bright-spot class was tried and dropped.
- 80/20 split into "training and validation/testing sets": **one held-out set**.
- About 300 × 300 images, random resize and centre crop to 224.
- **Public release: 9,562 train + 2,289 test = 11,851 [ours]**, not the paper's 16,808 real images; the test split differs.

**Recipe [paper]**
- DeepLabv3 (not v3+) ResNet-50, COCO-pretrained, auxiliary loss, plain CE, lr 0.005; optimiser and epochs not stated.
- Augmentation: H and V flips, 90° rotation (p = 0.5 each), Gaussian blur 7 × 7, σ 2.
- **Post-processing: a pixel is background only if P(background) > 0.54**, else argmax over defect classes, tuned by "hit and trial". The phase 1 handoff notes the paper says 0.54 and the code 0.52; both are right for their source.

**Numbers [paper, Table II]**

| | crack P/R/F1 | contact | interconnect | corrosion |
|---|---|---|---|---|
| without simulated (16,808) | .81 / .80 / .80 | .68 / .46 / .55 | .14 / .34 / .20 | .73 / .79 / .76 |
| **with simulated (17,064), headline** | .81 / .80 / **.81** | .66 / .51 / **.58** | .26 / .44 / **.33** | .69 / .89 / **.78** |

Weighted F1 0.95, unweighted F1 0.69 (both include no-defect at F1 0.98). Pixel accuracy 95.4%. IoU equivalents of the headline F1 (IoU = F1/(2 − F1)) [inferred, exact identity]: crack 0.681, contact 0.408, interconnect 0.198, corrosion 0.639, mean **0.481**.

**The "mIoU 57.3" episode (a corrected error).** `analysis/papers_metrics.md` §2.4 first said 57.3 is not in Fioresi's paper. That was **wrong**: the abstract states "a mean intersection over union score of 57.3%" (correction appended 8 Oct; also `literature/survey.md` header). What still holds: it cannot be a 4-defect IoU mean next to a 4-defect F1 mean of 57.75; it is most likely a 5-class mean including background [inferred, unverified]. Jha's P/R/F1 for Fioresi (59.00 / 59.75 / 57.75) are exactly the means of the **without-simulated** row.

**Ours against theirs (old era; `analysis/papers_metrics.md` §2.4; handoff §6.9)**

| Our run | IoU crack / contact / interconnect / corrosion | As F1 | Paper F1 |
|---|---|---|---|
| SL-100 (95,760 steps) | 0.675 / 0.479 / 0.332 / 0.660 | 0.806 / 0.648 / 0.498 / 0.795 | .81 / .58 / .33 / .78 |
| SL-20 | 0.651 / 0.442 / 0.245 / 0.635 | 0.789 / 0.613 / 0.394 / 0.777 | |

So our supervised baseline equals Fioresi on crack and beats it on the other three, even at 20% labels, on a smaller public dataset and without the 0.54 threshold. Remaining differences make this not a strict reproduction: different data and split; DeepLabv3 COCO vs our DeepLabV3+ ImageNet; 224 crops vs our shorter side 295 with 256 crops; their probable test-set selection.

The phase 1 handoff (§7b) also records the new-pipeline FSL run at 100 epochs, lr 5e-3 poly, 59,760 steps: **0.497 standard / 0.636 pvs3**, "Fioresi 4-class 0.482: reproduced". The first (lost) pipeline's poster records give Fioresi FSL 4-class / 5-class published 48.15 / 57.30 against ours 50.21 / 59.42 (phase 1 handoff §7a).

**Weaknesses.** Validation equals test (confirmed later from the official `train.py`: val and test both use `set="test"`; `to_human/situation_report_2026-10-08.md` §9). The split is by cell, and 25–44% of test cells have the same physical cell (another stress stage) in train (`data_analysis/ucf_el_report.md`; see `03_datasets_and_splits.md`).

### 4.2 Jha, Rawat, Vyas 2025: PV-S3 (Eng. Appl. AI 160, 111790; arXiv 2404.13693)

The only EL semi-supervised segmentation paper besides Torpey's CCT/U2PL arms (`literature/notes/F01` §4: none found since). Read in full, plus the released code and the journal version (`literature/notes/A04`, `F05` check 1; `analysis/papers_metrics.md` §3).

**Claim:** Mean Teacher with "Semi Cross-Entropy" (SemiCE) handles class imbalance; SSL at 20% labels beats supervised at 100%.

**Recipe [paper §4]**
- DeepLabv3+, ImageNet ResNet-50, Mean Teacher; **30 epochs**, batch 16, SGD lr 0.001, wd 1e-4, momentum 0.9; consistency weight λ = 1.5; no ramp-up described; EMA decay not given numerically.
- Base size 299, crop 224. Student strong view: jitter ±50%, grey p 0.2, blur, CutMix (Beta 4, 4). Teacher weak view: normalisation only.
- SemiCE (Eqs. 2–4) with thresholds t_pos / t_neg. **Conflict inside the paper:** Tables 1–2 use (0.6, 0); §4.2 later says "we chose ... (0.2, 0.4)"; the journal version gives t_pos 0.2 / t_neg 0.4 (`literature/notes/F05`).
- As printed, the unlabelled loss uses Y_L ("the ground truth label") for the unlabelled images, and its softmax runs over H × W positions, not classes. At best a notation error [inferred; whether the code uses ground truth anywhere in the unlabelled loss was not verified].

**Numbers [paper, Tables 1–4, 6]**

| | crack | contact | interconnect | corrosion | **mean IoU** |
|---|---|---|---|---|---|
| SL 20% (Table 1) | 25.29 | 6.89 | 0.85 | 2.03 | **8.76** |
| SSL 20% (PV-S3) | 89.00 | 49.00 | 40.00 | 90.00 | **67.00** |
| FSL 100% (Table 3) | 88.38 | 52.92 | 59.70 | 82.39 | **70.84** |
| SSL 100% | 91.78 | 58.29 | 53.89 | 95.26 | **74.75** |

Table 2 (3 subsets): SL 9.06 ± 0.09, SSL 66.53 ± 1.35. CSB-S1 (= BenchmarkEL 20211104, Table 5): SSL 20% crack 50, gridline 74, inactive 50 (mean 58.0); FSL 100% 58 / 83 / 50 (63.67).

**What we measured [ours]** (`analysis/papers_metrics.md` §3.4; handoff §6.10; phase 1 handoff §7c)

*Released code, run as shipped on cv02 (old era, finished 5 Oct):*
- `ignore_index = 0` everywhere (loss, data loader with `num_classes = 5`, model, metrics, configs). UCF-EL encodes background as 0. **So the model never predicts background** (0 pixels predicted as background).
- Result: **standard 4-class defect mean IoU 0.050; under the pvs3 convention 0.828**, which matches their own validation log to 4 decimals. Corrosion predicted on 3.33M px against 102,570 true (32×). Crack precision 0.1176, recall 0.946.
- Released `saved/ssl_el/config.json` has lr **1e-2** (paper and CLI default say 1e-3). 30 epochs × 479 = 14,370 steps; batch 16 + 16; one student + two EMA teachers, 125.3M params total.
- Released split lists: 1,769 of 2,289 public test images in their train lists, 437 in val; 5,194 of their names are not in the public release. Their supervised-only mode crashes.
- Their paper's 74.75 / 70.84 are below their own code's 0.828, so paper and code are not the same configuration [inferred].

*Our reimplementation and controls (old era, gaint; UCF-EL 20%):*

| Run | Steps | standard | pvs3 | Note |
|---|---|---|---|---|
| SL-20, their budget (30 ep, lr 1e-3) | 3,585 | 0.185 | 0.230 | interconnect, corrosion ≈ 0 |
| SL-20, lr 5e-3 | 12,000 | 0.448 | 0.559 | |
| **SL-20 step-matched, seeds 0–2** | 95,760 | **0.491 ± 0.009** | | the fair control |
| PV-S3 v1 | 95,700 | 0.200 | 0.379 | failed recipe (strong view on the supervised loss) |
| PV-S3 v2, s0 / s1 | 95,700 | 0.276 / 0.283 | 0.568 / 0.436 | corrosion runaway |
| PV-S3 v2 + per-class pseudo-label cap | 95,700 | 0.418 | 0.580 | corrosion IoU 0.067 → 0.631; one seed; cap exceeded in 132 of 187 windows (EMA lag) |
| FSL 100 epochs, lr 5e-3 poly | 59,760 | 0.497 | 0.636 | |

Sources: handoff §6.9–6.10; phase 1 handoff §7b; `analysis/papers_metrics.md` §3.4. Probes: an all-crack predictor scores crack IoU 0.766 pvs3 vs 0.066 standard; dilating predictions by 3 px raises pvs3 from 0.636 to 0.717 and lowers standard from 0.497 to 0.456.

Collapse mechanism (measured, no training): the teacher labels 0.96% of unlabelled pixels as corrosion, 23× the labelled share and 16× the truth; 99.4% of pixels clear the 0.6 threshold; still 21.6× at confidence 0.99 (handoff §6.10; phase 1 handoff §7b). The pvs3 metric hides it (corrosion 0.067 standard vs 0.879 pvs3). The earlier (lost) implementation's record of "SSL 46.4" was **not reproduced** by v1 or v2.

**Explaining the mismatches** (`analysis/papers_metrics.md` §3.4):
1. Their SL-20 8.76 vs ours 23.0 (pvs3) at their budget and 55.9 at 12k steps: **their baseline is under-trained** (their §4.2: SL-20 "is not able to learn the features"); also probable step mismatch between SL and SSL "epochs" [inferred]; plus convention.
2. Their SSL-20 67.0 vs our reimplementation 0.568 pvs3 / 0.276 standard: convention (pvs3 hides runaway classes), probable split leakage, paper ≠ released code. **Under the standard metric, step-matched SL (0.491) beats every PV-S3 arm.**
3. Their FSL-100 70.84 vs our 0.636 pvs3: convention + background never predicted + leakage [inferred]; partly unexplained.
4. **Their BenchmarkEL comparison (Table 6) is invalid:** the "Pratt" baselines are copied to the digit from Pratt's Fig. 7/8 custom-weight rows, which are per-image medians from 24-class models; PV-S3's own numbers are dataset-level IoU over 3 classes without background. The "+30% over the state of the art" compares two different metrics. Our crack IoU under pvs3 was 0.585 (`alhvr_20pct_s1`) against their 50–58 (like-for-like reading).

The journal version fixed none of this (`literature/notes/F05` check 1): 30-epoch baseline, SL-20 still 8.76, background treatment never stated, no split description, Table 6 still called "a fair comparison".

**Our "SemiCE" is not PV-S3's SemiCE.** This matters because every old-era Mean Teacher result used our SemiCE (`analysis/alhvr_audit.md` §2):
- Ours (`src/losses/semi_ce.py`): per-class BCE-with-logits on softmax logits; thresholds on **raw logits** (t_pos = 0.5·freq ≈ 0.001 for crack, t_neg = 0.5·(1 − freq)); mean over all active (pixel, class) pairs.
- Released PV-S3: softmax CE against the teacher argmax, weighted by teacher max-prob, only where max-prob ≥ 0.6; negative term on non-argmax classes; thresholds on **probabilities**.
- P2 then showed our SemiCE is not a valid consistency loss at all (100% of unlabelled pixels get ≥ 2 positive classes; `results/p2/README.md`). See `06_history_phase0_phase1.md` and `08_experiments_P1_P7_diagnostics.md`.

---

## 5. SA-UNet++ (Gangopadhyay et al. 2025, IEEE TETCI 9(2))

The model of the project's first experiment. Read in full (`analysis/papers_metrics.md` §4; `literature/notes/A08`).

- **No EL data at all.** T1: satellite PV panel vs background (3,716 images); T2: MIAD UAV solar-panel defects, 4 classes, reduced to 2,700 train / 300 test; T3: FloodNet; T4: oil spill.
- TensorFlow, Adam with stepped LR and ReduceLROnPlateau/EarlyStopping, batch 16, 30–70 epochs.
- Metrics probably per image with background in the class mean [inferred]. T2 (Table I): SA U-Net++ Jaccard **0.95 ± 0.09** vs U-Net++ **0.92 ± 0.12**: +0.03, inside one sd across images; single run, no significance test.
- The "SA" block is `sigmoid(Q+K)*V`, an **elementwise sigmoid gate, not dot-product self-attention**; no spatial mixing (phase 0 handoff, confirmed in `blocks.py`; phase 1 handoff §6).
- Parameter counts from the old repo code (phase 0 handoff): SA U-Net++ 4,589,880; SA blocks 88,000 (1.9%); no-SA 4,501,880. The rebuilt repo's U-Net++: 4,981,368 params, SA variant 5,440,120 (handoff §4.2).
- **Our result (old era):** SA gate on BenchmarkEL gives −0.004 test (p 0.78) and −0.021 val+test (`analysis/papers_metrics.md` §4; gaint `reports/stats_tests.md`). Not a contradiction: the paper never tested thin defects on EL, and its gains are on large objects under a background-inclusive mean. Details of the SA story are in `06_history_phase0_phase1.md`.

---

## 6. ALHVR (Lei et al., ICCV 2025) and its lineage

The method the user wanted to be "inspired by". Read: full paper, supplement and reference code (`literature/notes/B01_alhvr2025.md`; `analysis/papers_metrics.md` §5; `analysis/alhvr_audit.md`; gaint `docs/alhvr_port_notes.md`).

### 6.1 What ALHVR is [paper + code]
- Medical SSL segmentation with **two independently trained networks** (no EMA, two SGD optimisers). **There is no cross pseudo-supervision (CPS) term**; an early project plan wrongly called ALHVR "CPS plus modules" (handoff §10 item 1).
- Each network makes a clean pass and a feature-perturbed pass (feature dropout or feature noise, one coin per forward).
- Per batch, γ = mean of the lowest β fraction (β 0.8 for ACDC) of the averaged **perturbed** confidence over the whole unlabelled batch (batch-global, not per image).
- Regions by max softmax vs γ: **Ω1** both confident (no unlabelled loss); **Ω2** exactly one confident (CG-CPCL: cross-network prototype consistency); **Ω3** neither confident (DTCT: per pixel, the more confident network's clean prediction, sharpened with T = 0.1, teaches the other's perturbed prediction by MSE, plus entropy terms).
- Premise (Table 1, CPS on ACDC 10%): masking out the reliable-stable region during training gives the best Dice, 88.58 vs 85.34 with all regions. So value lies in ambiguous regions.
- **It does not target class imbalance or rare classes.** Datasets: ACDC (3 structures), AbdomenCT-1K (4 organs), BraTS (binary tumour). Large, compact structures, few classes.

### 6.2 Recipe [paper §4.2 + code]
- SGD lr 0.01, momentum 0.9, wd 1e-4, **constant learning rate**; 30k iterations; batch 16 = 8 labelled + 8 unlabelled; ACDC patch 256².
- Supervised loss: unweighted CE + Dice.
- **λ schedule:** code `0.1 · sigmoid_rampup(iter // 150, 200)` = 0.1·exp(−5(1 − t/30000)²), reaching 0.1 only at the final iteration. `analysis/papers_metrics.md` §5.2 says the paper's equation has no square; gaint `docs/alhvr_port_notes.md` §7 writes the paper's λ(t) with the square. **The two notes disagree on the printed equation; both agree the code ramps over the whole run.** Check the PDF (Eq. 10) if it matters.
- DTCT sharpening is **elementwise binary**, P^(1/T) / (P^(1/T) + (1 − P)^(1/T)): not class-normalised; any p < 0.5 goes to ≈ 0.
- Evaluation: per case Dice/Jaccard/95HD/ASD over foreground; **best-val checkpoint** (val every 200 iterations).
- Headline: ACDC 10% (7 labelled): 81.59 → **90.56 Dice** (upper bound 91.10); 20%: 84.83 → 91.09; AbdomenCT 5%: +17.36 Dice; BraTS 10%: +5.91.

### 6.3 Our port (old era) and why it was not a fair test

Port design (gaint `docs/alhvr_port_notes.md` §9): followed the reference **code** where paper and code disagree, with flags defaulting to the code (`alhvr.sharpening`, `prototype_scale`, `pull_all_prototypes`, `dtct_detach_target`, `feature_layer`, `cpcl.enabled`, `dtct.enabled`). Deliberate protocol changes, shared with every old-era method: weighted CE instead of CE + Dice; 4 L + 4 U instead of 8 + 8; the repo's U-Net++ (32–512 channels); Adam 1e-3 with warm-up and **cosine to zero**; 20k steps; prototype feature at U-Net++ node X[3][1]. Skipping classes absent from a batch was a mandatory deviation.

Audit findings ranked by how much each could explain "the unlabelled loss has no effect" (`analysis/alhvr_audit.md`, summary table):

| # | Finding | Label |
|---|---|---|
| 1 | λ ramp over the whole run × Adam with cosine-to-zero LR: LR-weighted mean λ 0.0156 vs 0.0393 in the reference (2.5× weaker); only 8% of our LR mass falls where λ ≥ 0.05 vs 37% of the reference's iterations. λ first reaches 0.05 at step 12,554, when LR is at 31% of peak | faithful ramp + misconfigured LR |
| 2 | Our "SemiCE" (Mean Teacher arm) deviates from PV-S3 (see §4.2) | misconfig |
| 3 | Mild MT strong view (blur, brightness/contrast, noise; no CutMix, never called); 29% of unlabelled samples identical for student and teacher | misconfig |
| 4 | Elementwise sharpening with 24 classes: where the winner's max prob < 0.5, the DTCT target is ≈ the zero vector, so MSE pushes toward uniform while entropy pushes toward one-hot | faithful but harmful |
| 5 | CG-CPCL CE is 71–81% of the unlabelled loss value but sits near an irreducible floor (cosine logits with scale 1: 1.41 at K = 24, 0.34 at K = 4) | faithful but harmful |
| 6 | Decoder BN running stats updated by clean and perturbed passes over mixed batches | faithful but harmful (does not affect on/off comparisons) |
| 7 | Gradient path, sign, float32 loss, masks, γ, regions, two optimisers, loss-off control | OK |

Logged loss shares (`alhvr_20pct_s0`, network A): λ·unsup / sup was 0.7% at step 2,000, 2.8% at 5,000, 17.7% at 10,000, 57.6% at 15,000 and 89.4% at 19,000, when LR was 0.6% of peak (`analysis/alhvr_audit.md` §1). **So "ALHVR equals ALHVR with losses off" (+0.005 ± 0.023) is close to a null by construction** (handoff §9.1). What still stands regardless of λ is measured on the networks:
- Ω3 holds 71% of true crack pixels (119,384 of 168,511 on the 383 held-out train images).
- DTCT winner accuracy in Ω3: crack 61.9%, inactive 51.2%, background 64.7%; 20.7% of Ω3 crack pixels taught "background" on final weights (32.4% over the whole run in the logs).
- Cross-network prototypes: crack accuracy 4.6% (per-batch as in training 1.1%); own-network prototypes 43–49%, below the classifier head (62%). The relabel rule "use the prototype label where the winner says background" recovers about 6,600 crack pixels and mislabels about 12.6 million background pixels (handoff §6.8; the phase 1 handoff §9f says 12.5M). **Prototype-based fixes are a closed negative result.**

P5 (10 Oct, locked protocol) later measured pseudo-label precision by ALHVR region on the P-series ground: Ω3 holds 72% of GT crack; strict precision 0.27 but 0.64 within 2 px; per-class γ pulls 40 points of crack out of Ω3 only by lowering precision (`results/p5_region_pl/README.md`; `to_human/directions_2026-10-10.md` §1 item 4). That "right place, wrong pixel" finding is the origin of the tolerant pseudo-label loss used from P7 on.

### 6.4 Lineage and neighbours (`literature/notes/B02`, `F01`, `F05`)
- **MCF** (CVPR 2023): two heterogeneous subnets; dynamic competitive pseudo-labels, the ancestor of DTCT.
- **BUR** (arXiv 2502.07457, 2025): the **opposite** allocation. Labelled loss focuses on high-uncertainty regions; unlabelled loss only on low-uncertainty regions. Class-agnostic (global entropy percentile); ACDC, LA, PROMISE12. The rival hypothesis for rare thin classes: ambiguous crack pixels may be better learned from labelled images than from pseudo-labels.
- **CSL** ("When Confidence Fails", ICCV 2025): randomly masks reliable pixels; natural-image counterpart of ALHVR Table 1; class-agnostic.
- **DCF** (Wan et al., MedIA 2026; an ALHVR citer): evidential Guidance Mask with three regions (confident-agree, uncertain-agree, confident-disagree). Its "class awareness" is a peer confusion matrix, not imbalance handling. **Now the routing baseline a reviewer would ask for** (`literature/notes/F05` check 2).
- **CaPro** (Pattern Recognition 2026): class-aware subclass prototypes from reliable regions, one global threshold; no routing of unreliable regions; no imbalance study.
- ALHVR had 5 citing works by 10 Oct 2026; none has a class-imbalance or rare-class title (`literature/notes/F01` §1; titles only).

---

## 7. E-SCDD and PV-DDPM (Hanifi, Köntges et al., arXiv 2511.09604, Nov 2025)

The source of the **revised crack labels** the P-series uses (`data.mask_subdir=labeled/masks_escdd` from P6 on). `literature/notes/F03` §4; `to_human/directions_2026-10-10.md` §2.
- PV-DDPM: a mask-conditioned diffusion model for EL cells, trained on BenchmarkEL "SCDD" (the 20221008 release: 695 labelled, 29 classes).
- E-SCDD: 1,000 pixel-annotated images = 695 + 110 new real + 195 synthetic [paper]; the Hugging Face listing (`snt-ubix/escdd`, MIT licence) shows train 731 / val 90 / test 82 [ours, checked]; about 93 train files carry `k-CFVS` / `k-CSIR` prefixes, probably synthetic [inferred]. Its README says it adds refined pixel-level annotations.
- Downstream evidence in the paper is weak: only AA-CLIP anomaly detection; no segmentation experiment; nothing crack-specific.
- What the revision did to crack labels (measured on the 20220723 → 20221008 change; `literature/notes/F04` §1a): mean label width 1.82 → 2.55 px per skeleton pixel; 8-connected fragments 3,707 → 549 (dotted labels joined); 100% (median) of new crack pixels within 1.5 px of the old label. On our 50 test images (20211104 → 20221008), 42 masks changed (35 crack masks), crack px +39%, IoU old/new 0.693.
- Effect on our models (P3, exploratory): re-scoring the same checkpoints on revised labels raises crack IoU by 0.05–0.07 for every model and flips 10% vs 100% on crack AP (`results/p3_label_versions/README.md`; `to_human/directions_2026-10-10.md` §2). Counts and the 577 + 5 mask construction are in `03_datasets_and_splits.md`.

---

## 8. MultiSolSegment (Sanghi et al. 2026, Solar Energy 310; arXiv 2603.13337)

`literature/notes/A07`; local PDF `~/mtp/research/papers/MultiSolSegment.pdf`.
- Single-label masks force a choice where features overlap ("when cracks overlapped with busbars ... the model was forced to choose only one"). Method: multi-channel U-Net with independent sigmoid maps for non-cell, busbar, crack and dark.
- Data: CWRU 373 + ASU 92 + LBNL 120 mono-Si EL images (DuraMAT Data Hub; CWRU = BenchmarkEL's SDLE source, to be checked by hash per `literature/notes/F04`).
- Numbers: pixel accuracy 98.2%; mean per-class IoU 0.384 (P 0.550, R 0.507).
- Weaknesses: the headline is background-dominated pixel accuracy; flip augmentation reported with the split counts, so possible augmented-copy leakage [inferred].
- **Why it matters to us:** BenchmarkEL has 24 mutually exclusive classes including gridline, busbar and ribbon, so crack labels are likely inconsistent exactly where cracks cross metallisation: label noise placed on the rare class [inferred; testable] (`literature/survey.md` §A).

---

## 9. Core SSL methods (what the P-series builds on)

`literature/notes/B05`; `analysis/papers_metrics.md` §6.

| Paper | What it is | Defaults / key facts | Where it enters our work |
|---|---|---|---|
| **Mean Teacher** (Tarvainen & Valpola, NeurIPS 2017; read in full) | Student trained on labels plus a consistency loss to an EMA-of-weights teacher | MSE consistency ramped up over the first 80 epochs (sigmoid); EMA α 0.99 during ramp-up, 0.999 after. Input noise and dropout differ between student and teacher; without different views the consistency target equals the prediction and gives almost no gradient [inferred consequence] | Every MT arm (old era with SemiCE; P7–P13, P16 with confidence or tolerant pseudo-labels). See `04_glossary_and_naming.md` |
| **FixMatch** (Sohn et al., NeurIPS 2020; abstract) | Weak-to-strong pseudo-labelling with a confidence threshold | τ = 0.95 is the common default | Our `confidence_ce` (hard pseudo-labels at teacher confidence ≥ 0.95): the "B" arms of P7/P8/P10 and BsM5 in P13 |
| **CutMix-Seg** (French et al., BMVC 2020; abstract) | "SSL segmentation needs strong, varied perturbations"; mask-based mixing works where standard augmentation consistency gives little | CutMix copies pixels and never resamples them, so it is label-safe for 1–2 px cracks (`protocols/P13_cutmix_separate_bn.md`) | P13 CsM5/BsM5 (`ssl.cutmix_p=0.5`) |
| **UniMatch** (Yang et al., CVPR 2023; read in full) | Weak/strong image views plus a feature-perturbation stream | DeepLabv3+, 8 L + 8 U; SGD with poly decay; τ = 0.95; λ = μ = 0.5 constant from step 0; feature dropout 0.5 between encoder and decoder; CutMix box area U(0.02, 0.4), aspect U(0.3, 3.33) | P13's CutMix box law follows UniMatch |
| **UniMatch V2** (TPAMI 2025; sections) | UniMatch with DINOv2 encoders | Cityscapes 1/16: 77.2 → 80.6 (S), 80.8 → 83.6 (B), so SSL gains shrink to about +3 with strong encoders; Pascal 1/16 +9 to +12; no tail-class ablations | Caution that SSL gains shrink with strong encoders |
| **CPS** (Chen et al., CVPR 2021; title) | Cross pseudo-supervision between two networks | | ALHVR's Table 1 baseline; never run here (user objected to putting plain CPS on the critical path) |
| **CCT** (Ouali et al., CVPR 2020; title) | Cross-consistency of auxiliary decoders on perturbed features | Best regime on EL in Torpey (0.550) | Not run |
| **ClassMix** (WACV 2021), **ST++** (CVPR 2022), **CorrMatch**, **AllSpark** (CVPR 2024) | Class-aware mixing; self-training; titles only for the last two | | Not run |
| **Yuan et al. 2021, "A Simple Baseline"** (ICCV; search abstract) | "the large distribution change caused by strong augmentation harms the batch normalisation statistics"; distribution-specific BN | | **Published precedent for our BatchNorm mixing handicap** (old-era "4 + 4 inactive gain with loss off"; P10–P12 loss-off handicap); motivated P13's separate-BN forward |

---

## 10. Rare-class and class-imbalanced SSL

`literature/survey.md` §B; `literature/notes/B03`, `B04`, `B06`, `F01` §2.

| # | Mechanism | Representative work | Evidence for rare/tail classes | Strength | Fit to our case (as judged 8–10 Oct) |
|---|---|---|---|---|---|
| 1 | Rare-class-biased sampling and mixing | **AEL** (NeurIPS 2021): confidence bank driving adaptive CutMix/Copy-Paste, equalisation sampling, re-weighting; DAFormer Rare Class Sampling; BCP; ClassMix | AEL cumulative ablation (Cityscapes 1/32): 69.1 → +DR 70.3 → +AES 72.5 → +ACM 73.4 → +ACP 74.3; tail classes +10 to +22 IoU vs CutMix-Seg (e.g. motorcycle 54.8 → 74.3) | Strong (natural images) | Oversample labelled crack/inactive images; copy-pasting 2–3 px cracks needs care |
| 2 | Distribution-aligned / class-wise thresholds | **DARS** (ICCV 2021), CReST, FreeMatch | DARS Cityscapes 1/8: tail mIoU 54.0 → 57.9; over-confidence makes single thresholds degenerate ("81.3% road pixels is 1") | Moderate | Our UCF corrosion pseudo-labels at 23× their labelled share; crack over-prediction |
| 3 | Class-aware loss weighting from pseudo-label statistics or difficulty | **DHC** (MICCAI 2023), GA loss (ECCV 2024), Basak 2022 | DHC Synapse 20%, 3 seeds: 48.61 ± 0.9 vs CPS 33.55 ± 3.7; esophagus 0 → 13.2, left adrenal 0 → 10.6; 6 test scans | Moderate | Old-era 24-class weighted CE gave weight 0 to absent classes (12 at 2% labels) |
| 4 | Unreliable pixels as negatives | **U2PL** (CVPR 2022) | VOC 1/16 45.77 → 67.98; **on EL 0.448 mIoU, below random init 0.486 (Torpey)** | Conflicting | Low priority |
| 5 | Region-specific learning in ambiguous regions | ALHVR, MCF, BUR | ALHVR Table 1; no rare-class analysis | Weak for rare classes | Premise holds (Ω3 holds 71% of crack) but the teacher is right on ~62% of crack there |
| 6 | Prototype / memory-bank features | ALHVR CG-CPCL, U2PL memory bank, USRN | Our per-batch cross-network prototypes: crack accuracy 4.6% | Negative (per-batch, unlabelled) | Only labelled-GT prototypes with EMA memory worth considering (SCDL, VCDP, arXiv 2026) |
| 7 | Strong pretrained encoder | UniMatch V2; Torpey | SSL gain about +3 with DINOv2; on EL COCO ≈ IN-SimCLR ≈ CCT | Moderate | Our old from-scratch 5M U-Net++ was a weak base; P6 moved to ImageNet ResNet-34 |
| 8 | Thin-structure supervised losses | clDice, Skeleton Recall, focal Tversky, boundary loss | See §11 | Moderate–strong (supervised side) | Crack was fit-limited under the old recipe |
| 9 | Operating point / logit adjustment | Menon et al. 2021; Pratt 2023 "dilated predictions" | Old-era crack-logit bias: +0.03 test defect mIoU, more than any SSL arm [ours] | Moderate | Any SSL "gain" must be separated from a threshold shift |

Newer (2024–2026) class-imbalanced SSL found on 10 Oct (`literature/notes/F01` §2): **DCA** (CVPR 2026; head/medium/tail expert decoders with logit-stitched pseudo-labels; experts alone take tail organs from 0 to 39–48 Dice), **CGS** (TMI 2025; one-vs-rest specialist head per class, dropped at inference), **SKCDF** (CVPR 2025; unlabelled data trains the encoder, decoder protected from noisy pseudo-labels), **DINO-Mix** (arXiv 2026; frozen DINOv3 teacher + imbalance-aware CutMix), **SCDL / VCDP** (labelled-anchored prototypes), **STAC** (enlarges small organs; the opposite of what our crack metric wants).

**The claimed gap (status as of 10 Oct, `literature/notes/F01` §5, `F05` check 2):** no method found combines ALHVR-style region routing with class awareness. Class-aware without routing: DCA, CGS, DHC/GA, DINO-Mix/AEL. Routing without class awareness: ALHVR, BUR, CSL, DCF, CoraNet, deep co-training 2022. Caution recorded in the source: "a gap is not a contribution by itself"; our own measurements say the teacher is right on only about 62% of Ω3 crack pixels, so the routing *target* in Ω3 is the bottleneck, not the routing rule.

---

## 11. Thin structures, label noise and metrics

`literature/survey.md` §C; `literature/notes/C01`, `C02`, `C03`, `F03`.

**Losses**
- **clDice** (CVPR 2021): soft-skeleton Dice, topology-preserving; vessels, roads, neurons.
- **Skeleton Recall** (ECCV 2024): recall of a tubed GT skeleton; "the first multi-class capable loss function for thin structure segmentation"; > 90% cheaper than clDice; includes concrete cracks.
  - **Negative evidence** (Arora et al., arXiv 2508.11374): on a concrete Cracks dataset over 5 seeds, DSC 76.64 → 76.94 (n.s.), clDice 85.67 → 86.21 (n.s.), FNR 20.2 → 17.1 (sig.), **FPR 0.25 → 0.31 (sig. worse)**; significant on 3 of 15 tubular metrics. The SRL gradient is independent of the prediction and never penalises false positives, so it rewards over-prediction. Our crack models already over-predicted width, so SRL was judged a poor main lever.
  - clDice was dropped in the old era: the bottleneck was over-prediction, not recall (phase 1 handoff §11, M5).
- **Focal Tversky** (ISBI 2019): sets the P/R trade-off explicitly instead of through class weights. **Boundary loss** (MIDL 2019). **Persistent-homology** losses (NeurIPS 2019; expensive).
- **Centerline / distance regression** (Sironi et al., CVPR 2014): a classifier cannot tell on-centerline pixels from adjacent ones, which is our jitter problem; regressing a distance-to-centerline function would be jitter-insensitive by construction [inferred].

**Noisy and misaligned labels** (`literature/notes/F03` §1)
- **Mnih & Hinton, ICML 2012**: two robust losses for road maps: asymmetric omission noise (a 1 in the label is trusted, a 0 may be a missed road) and a translational noise model that marginalises over local shifts. **Direct analogue of BenchmarkEL**: dotted crack labels are omission noise; ±1 px jitter is registration noise. This is the literature root of P14 (offset-tolerant supervised loss).
- **STEAL** (CVPR 2019): thin-boundary detection with active label re-alignment (+18.6% AP over CASENet).
- **ADELE** (CVPR 2022): memorisation of noisy labels starts at different times per class.
- **SVLS** (IPMI 2021): spatially varying label smoothing; for a 2 px line it is close to a Gaussian heatmap target [inferred].
- **Zhang, Tanno et al.** (NeurIPS 2020): annotator confusion matrices; we have "multiple annotators" for free in the BenchmarkEL releases and E-SCDD.
- Li et al. 2026 (retinal vessels): F1 0.817 → 0.575 under positional label noise while accuracy falls 3%; thin structures lose recall and F1 first.

**Metrics**
- **Metrics Reloaded** (Nature Methods 2024): clDice for connectivity; NSD (surface Dice with tolerance) for boundaries.
- **What's Cracking?** (König et al., arXiv 2202.03714) §VI-B3: tolerance metrics (2 or 5 px allowance) "can lead to oversaturating the number of TP pixels by simply creating wider predictions". **So any relaxed recall must be reported with relaxed precision.** This is why the P-series reports crack relaxed F1@2 together with the relP@2 width check (see `07_methodology_rules_and_statistics.md`).
- ODS/OIS and pixel AP remove operating-point effects.
- Also in `literature/notes/C02` (abstracts): Reinke et al., common limitations of overlap metrics for small structures; Zhang et al. 2025 crack review, which calls for cross-dataset rather than single-dataset evaluation.
- No EL paper read in full (Pratt 2023, Fioresi 2022, PV-S3, Torpey 2024) reports a tolerance-aware or skeleton-based crack metric, and none except Torpey uses a multi-run protocol (`literature/survey.md` §A).

**SSL for thin structures** (`literature/notes/F01` §3): SemiCurv (TIP 2022; differentiable inverse transform before consistency; N-pair consistency because MSE collapses to all-background), ITC/CTC (2025; skeleton-aware distance-transform consistency), HAIC-NET (2024; centerline consistency, paywalled, unverified). The 8 Oct claim "no skeleton- or tolerance-aware SSL objective" is therefore **partly refuted**. Still unrefuted in what was found: no unlabelled loss tolerant to ±1–2 px offsets, none multi-class/rare-class aware, none on EL. Reworded gap: "tolerance-aware, class-aware unlabelled consistency for thin rare classes".

**Label-efficient crack work outside PV** (`literature/notes/C03`; `F01` §3; `F05` check 3):
- König et al. 2021 (arXiv 2109.00456; abstract): weakly supervised surface cracks from classifier localisation, "comparable performance to fully supervised" on four crack datasets.
- Crack-Segmenter (Kyem et al., arXiv 2510.10378; abstract): annotation-free self-supervised pavement cracks, claims to beat 13 supervised methods on 10 datasets. Needs the full text before citing.
- Concrete-crack SSL is generic consistency or pseudo-labelling: AutCon 2023, 2% labels within 2.6 / 4.7 mIoU of full; EAAI 2024 (mutual consistency + boundary loss), 20% labels F1 0.823 / IoU 0.689, with hyperparameters apparently picked on reported results. No tolerance metric; civil cracks are far thicker than EL cracks.

**Physical scale** (`literature/notes/F05` check 4): real single cracks are about **3.4 µm** wide under load (Haase 2018, DIC); one pixel is about 300 µm at 512 px per ~156 mm cell. The ~4 px dark line is electrical/optical spread around a sub-pixel crack, so **any annotation width is a convention**.

---

## 12. Fair SSL evaluation

`literature/notes/D01`; `literature/survey.md` §D.
- **Oliver et al. 2018** (NeurIPS): tuned baselines close much of the reported gap; SSL is sensitive to the labelled set and degrades with out-of-distribution unlabelled data.
- **Zoph et al. 2020**: self-training helps even where pre-training does not; stronger augmentation reduces pre-training value.
- **nnU-Net Revisited** (MICCAI 2024): "many recent claims ... fail to hold up when scrutinized for ... inadequate baselines, insufficient datasets".
- **Kalapos & Gyires-Tóth** (ECCV-W 2022; `literature/notes/F02` item 11, search abstract): supervised ImageNet was the most accurate at < 100 labelled samples (counterweight to in-domain SSL).
- Protocol derived from these plus our own failures (`literature/survey.md` §D; `literature/notes/D01`): step-matched supervised baselines; loss-off controls with an identical forward pass; multiple labelled splits, not just seeds; one fixed checkpoint rule (never best-on-test); per-class and threshold-free metrics plus a thin-structure metric; multiple-comparison correction. How far the P-series met this list is in `07_methodology_rules_and_statistics.md` and `13_problems_pitfalls_open_issues.md` (for example, one labelled split was used throughout).

---

## 13. Using unlabelled data without pseudo-labels, and foundation models

`literature/notes/E01`, `F02`.
- **Torpey 2024** (above): in-domain SimCLR 0.517 < COCO 0.544 and IN-SimCLR 0.534 at full labels; label-scarce regimes not tested.
- **AOI-SSL** (Figueira et al., CVPR-W 2026; 7k unlabelled + 625 labelled semiconductor images): MAE best; FasterViT-0 MAE 60.3 mIoU vs ResNet18 + U-Net++ ImageNet 52.4; thin wires: FasterViT MAE wire IoU 66.7 vs ViT-Tiny MAE 43.0 (non-overlapping 16 × 16 patches fragment thin structures).
- **VasoMIM** (AAAI 2026, vessels): MIM over scratch +18.5 Dice at 25% labels (scratch 38.1 → MAE 56.6 → VasoMIM 56.9); moderate mask ratio (0.3–0.5) better than 0.75 for thin foreground.
- **SparK** (MIM for any CNN via sparse convolution) and **ConvNeXt V2 / FCMAE** (Atto 3.7M params): ways to MIM-pretrain a small CNN encoder.
- **DINOv2 / DINOv3**: DINOv3 releases distilled ConvNeXt-T/S/B/L (29–198M); ViT patches (14/16 px) are 4–9× wider than a BenchmarkEL crack. P4 (10 Oct) measured DINOv2 patch features weak on crack (AP 0.18 vs 0.32 for ImageNet ResNet-50) and on par for inactive (0.38) (`results/p4_feature_probe/README.md`).
- **SAM family**: fails on dense, branching thin structures (arXiv 2412.04243); SemiSAM+ helps LA MRI at 1 label but hurts on PET heart; crack-adapted SAMs are far too large to deploy (teachers only).
- **AM-RADIO** (CVPR 2024): multi-teacher distillation (CLIP + DINOv2 + SAM) into one student; E-RADIO ≥ 7× faster than the teachers (`F02` item 14). The template for direction 6 in §18.
- No paper found applies SAM/SAM2/SAM3, CLIP zero-shot or frozen DINOv2/v3 features to EL defect *segmentation* [bounded] (`F02` item 19).
- Medical evidence (Models Genesis; Azizi et al. 2021) favours domain-specific self-supervision when labels are scarce (`literature/notes/E01`; `literature/survey.md` §E; abstracts).
- **EI-AE** (Lin et al., EES 2026; `F05` check 3): normal-only reconstruction gives crack pixel AP 0.14 (few-shot 0.34) on PVEL-AD; anomaly priors are weak for thin cracks. Its 438 pixel masks on PVEL-AD are a possible out-of-distribution crack test set.
- Hypothesis recorded in the survey [inferred]: augmentation-invariance objectives (blur, crop) may erase 2–3 px cracks; masked reconstruction keeps local detail.
- Supervised transfer UCF-EL → BenchmarkEL: no paper found (`literature/notes/E01`, `F02`). This is what P15 tests (ImageNet init vs a UCF-EL-trained encoder); see `10_experiments_P13_P16_E1.md`.

**Weak supervision, synthesis and active learning** (`literature/notes/F03` §3–5; directions 4, 7 and 9 in §18):
- **Božič et al.** (Comput. Ind. 2021): image labels for all plus N masks; KSDD2 AP 73.3 (N = 0) → 91.5 (N = 5) → 95.4 (all). Image-level detection AP, not pixel IoU, so weak evidence for pixel geometry.
- **Boxes2Pixels** (CVPR-W 2026; abstract): box → SAM pseudo-masks as a noisy teacher, +6.97 anomaly mIoU; notes that box priors fail for thin diagonal cracks, which is the PVEL-AD crack-box case.
- **Otamendi et al.** (Solar Energy 2021; IEEE TII, arXiv 2212.07768): EL annotation-assist pipeline, 60% annotation-cost reduction [paper].
- **Synthetic cracks:** a masonry study (search level) found about 30% synthetic data costs < 2% F1, but > 2,000 synthetic patches cost > 40% F1. So synthetic data must supplement real data at a capped ratio (the ≤ 30% cap in direction 7).
- **Active learning:** region-level, class-balancing methods (Casanova et al. ICLR 2020, about 30% fewer labels on Cityscapes; OREAL; spatial-diversity region AL, ~95% of full with 5–9% of pixels). None on EL. Relevant to WattCycle's own labelling (direction 9).

---

## 14. Other EL datasets and EL papers (census)

`literature/notes/A08`, `F04`, `F05`. Brief here; dataset detail is in `03_datasets_and_splits.md`.

| Dataset / paper | What | Relevance |
|---|---|---|
| ELPV (Deitsch et al.) | 2,624 cells, image-level defect probability | **Contains BenchmarkEL's BMRK cells** (4 of 4 checked, normalised cross-correlation 1.000); not an independent pool or test set |
| PVEL-AD (Su et al., IEEE TII 2023) | 36,543 NIR EL cells with boxes (12 defects + normal) | largest weak-label pool; access by signed request form; boxes fit thin diagonal cracks badly |
| PV-Vision (LBNL, Chen et al. PVSC 2022) | crack, busbar, dark-area pixel labels; 1,272 / 206 / 359 cells | 0.18 s/cell; "maximum inactive area" severity link |
| MultiSolSegment (DuraMAT) | 585 multi-label masks | CWRU may equal BenchmarkEL's SDLE source |
| PVEL-S (Kaggle; Duan 2025) | 1,200 binary-masked cells | mIoU ~96% including background (uninformative) |
| UCF-EL-GDI (Hugging Face) | defect-removed synthetic UCF images | – |
| SEiPV-Net (2023), STC-Net (2026; train mIoU 95.98 vs test 72.52), Mayr et al. 2019 (weakly supervised crack from image labels), Korovin (HJT anomaly), Gómez-López 2026 | other EL segmentation work | mostly abstract-level |
| Liu et al. 2025 (Solar Energy) | few-shot detection of rare defects on PVEL-AD; novel-class mAP ~19–26% | the only EL paper explicitly about rare defects; detection, not segmentation |
| Gil et al. 2025 (ICEIC) | MIL with module labels + ~5% cell labels | weak-supervision precedent |
| Hijjawi et al. 2026 (Solar Energy) | supervised instance segmentation on UCF-EL; mAP50 0.602 | "benchmarked against all studies on UCF EL", likely on the official leaky split (`F04` §3) |
| SIGAN (arXiv 2104.04953) | GAN that removes defects for EL segmentation; releases EL-2019 (540 images, pixel-level, 3 classes) | another pixel-level EL source; abstract only (`F03` §4) |

Pattern (`literature/notes/F04` §3): fully semi-supervised pixel segmentation on EL is still only PV-S3 and Torpey's CCT/U2PL arms; none reports a label-budget curve with matched baselines, and none evaluates on a physical-module-disjoint split.

---

## 15. Severity and deployment literature (context for thesis parts 2–3)

`literature/notes/F04` §4, `F05` check 4; `to_human/directions_2026-10-10.md` §1 item 5.
- Crack modes after Köntges et al.: A (no inactive area), B (partly disconnected), C (fully inactive). **Power loss tracks the inactive / disconnected area, not crack length** (Chen PVSC 2022 "maximum inactive area"; Pratt ICTAS 2025; Hoffmann Prog. PV 2021; phase 0 handoff).
- Gabor 2022 (hail-damaged fleet): a crack is "critical" when > 1% of cell area is isolated, "very critical" > 20%.
- Throughput: inline EL testers under 24–30 s per module, about 0.2 s per cell; PV-Vision 0.18 s/cell; YOLOv5-s 111 FPS on PVEL-AD. **A ~5M-parameter CNN is well within budget; real-time is not the binding constraint**; foundation models can be teachers but should not be deployed.
- Consequence drawn for part 1: errors in the inactive class and in crack connectivity matter more for severity than pixel-exact crack IoU.

---

## 16. Reproduction summary: their number vs ours, and the explanation

Old-era numbers throughout (original masks; our code before the P-series). From `analysis/papers_metrics.md` §7 unless stated.

| Paper | Their number | Our nearest like-for-like | Gap | Explained by |
|---|---|---|---|---|
| Pratt 4c, avg defect median IoU | 0.28 | U-Net++ arms rule A 0.28–0.30; Pratt-A 0.303 | none | metric convention (rule A, not rule B) |
| Pratt crack median | 0.13–0.26 | 0.15–0.25 | none | – |
| Pratt inactive median | 0.00–0.38 | 0.42–0.45 (rule A) | ours higher | convention ambiguity; their weight sets B/C zero inactive |
| Fioresi F1 crack / contact / interconnect / corrosion | .81 / .58 / .33 / .78 | SL-100 .81 / .65 / .50 / .80; SL-20 .79 / .61 / .39 / .78 | ours ≥ | different data/split; their test-set selection and 0.54 threshold |
| PV-S3 SL-20 | 8.76 (pvs3) | 0.230 at their budget; 0.559 at 12k steps | ours far higher | their baseline under-trained (budget) |
| PV-S3 SSL-20 | 67.0 (pvs3) | v2 0.568 pvs3 / 0.276 std; class-cap 0.580 / 0.418 | ours lower | convention hides runaway classes; probable split leakage; paper ≠ released code (0.828). **Under standard, step-matched SL (0.491) beats every PV-S3 arm** |
| PV-S3 FSL-100 | 70.84 (pvs3) | 0.636 pvs3 (100 epochs) | −0.07 | convention + background never predicted + leakage [inferred]; partly unexplained |
| PV-S3 "+30% over Pratt" on CSB-S1 | 58.0 vs 28.0 | – | – | **invalid comparison** (dataset-level pvs3-style IoU vs per-image median) |
| SA U-Net++ | +0.03 Jaccard (MIAD) | −0.004 (BenchmarkEL) | – | different domain and scale; within their per-image sd; single run |
| ALHVR ACDC | +9 Dice over baseline | +0.005 ± 0.023 against loss-off | – | **our port's cosine-to-zero LR cancels the late λ ramp**; also a 24-class rare-defect setting the design does not target; **not a fair test** |

Meta-lesson recorded in the phase 1 handoff (§13): "every 'the method differs' explanation turned out to be a comparison-convention or control mistake. Check conventions, steps, and controls before believing a method difference." The "Do not say" list for presentations (phase 1 handoff §12): do not say "SSL doesn't work", "Jha is wrong", "we beat Fioresi", "attention hurts", "we reproduced Jha".

---

## 17. How the literature maps onto our experiments

| Literature idea | Our experiment | Where |
|---|---|---|
| Overfit/fit check before method work (nnU-Net revisited spirit) | P1 overfit check | `08_experiments_P1_P7_diagnostics.md` |
| PV-S3 SemiCE as a consistency loss | P2 gradient probe: invalid | same |
| Label revision as a "second annotator" (Zhang/Tanno; E-SCDD) | P3 label-version re-score | same |
| Pretrained encoders, DINOv2 patch size (UniMatch V2, AOI-SSL) | P4 frozen-feature probe | same |
| ALHVR regions, DARS/FreeMatch per-class thresholds | P5 pseudo-label precision by region | same |
| Strong baselines (Oliver, nnU-Net revisited); label-safe augmentation; CE + Dice | P6 corrected supervised ladder L0–L3 | same |
| Tolerance metrics (What's Cracking), registration noise (Mnih & Hinton), ALHVR routing by rarity | P7/P8 tolerant pseudo-labels | `08_…`, `09_experiments_P8_P12_ssl_series.md` |
| Oliver: out-of-distribution unlabelled data | P9 external pool | `09_…` |
| Label budget sensitivity | P10 5%, P16 20/50/100% | `09_…`, `10_experiments_P13_P16_E1.md` |
| Identical-forward loss-off controls; Yuan BN statistics | P11/P12 matched view; P13 separate BN | `09_…`, `10_…` |
| CutMix-Seg / UniMatch strong perturbation; FixMatch hard PL | P13 CsM5, BsM5 | `10_…` |
| Mnih & Hinton translational noise; STEAL | P14 tolerant supervised loss | `10_…` |
| Supervised transfer from a neighbouring dataset (direction 5) | P15 UCF-EL encoder | `10_…` |
| Metrics Reloaded; severity-relevant task metrics; held-out source evaluation | E1 per-cell metrics and 106-cell unseen-module extension | `10_…` |

---

## 18. The 10 Oct directions survey (`to_human/directions_2026-10-10.md`)

Asked for by the user on 10 Oct ("explore all the possible directions ... dont limit to them"). Rested on 4 literature scouts + 1 reader (notes F01–F05), 15 institutional PDFs and 12 open-access ones, P3, and the earlier reports.

**Bottom line at the time (§1):**
1. The ground moved: BenchmarkEL has a newer release (`20221008`, 695 images) and E-SCDD (903 images), both cleaning crack labels; re-scoring on revised labels raises crack IoU 0.05–0.07 and flips 10% vs 100% on crack AP. So any method comparison on the old crack labels mostly measured the labels.
2. Strongest thesis bet: an ALHVR-inspired method with **class-rarity** and **label-tolerance** aware routing, on corrected ground, against a no-pseudo-label rival (MIM pretraining of the same small encoder).
3. The gap is open but narrower (DCF is the routing baseline).
4. P5: crack pseudo-labels in Ω3 point at the right crack but miss the pixels (strict P 0.27, 0.64 within 2 px), so hard pseudo-labels fail for rare thin classes while offset-tolerant targets keep most of the signal.
5. Deployment is not the binding constraint, but it shapes the design (≈5M-parameter CNN; big models only as teachers).

**Direction map (§4), with the verdict as written then:**

| # | Direction | First test / evidence | Verdict (10 Oct) | What happened next |
|---|---|---|---|---|
| 0 | Fix the ground: revised labels, label-preserving augmentation, module-disjoint UCF split, metric suite | supervised recipe sweep on revised labels | **do first** | P6 (L0–L3 ladder, revised labels). No record of a UCF module-disjoint re-split being done |
| 1 | Tolerance / noise-aware supervision for thin labels | train on old labels, test on revised; pass if ≥ 50% of the old→revised gap is recovered | strong, novel on EL | P14: recovers 0% of the gap (`results/p14/README.md`) |
| 2 | ALHVR-inspired, rarity-aware routing | P5 done: no hard pseudo-labels for rare classes in Ω3; per-class γ alone doesn't help | main method candidate, only with tolerance-aware targets | Tolerant PL (P7/P8 onward). Full two-network routing method never built |
| 3 | Unlabelled data without pseudo-labels: MIM pretraining | P4: ImageNet CNN features far above random (crack AP 0.33 vs 0.03; inactive 0.42 vs 0.10) | must-run rival; ImageNet-init CNN becomes the default baseline | ImageNet ResNet-34 adopted in P6 (L3). No MIM pretraining run in P1–P16 |
| 4 | Weak and mixed supervision (ELPV image labels, PVEL-AD boxes) | AP at 5% masks ± ELPV auxiliary loss | medium | not run |
| 5 | Cross-dataset transfer (BenchmarkEL ↔ UCF-EL) | encoder-only transfer vs ImageNet | medium, cheap | P15 (gaint; pending at 11 Oct ~22:00) |
| 6 | Foundation-teacher distillation | P4: DINOv2 weak on crack | narrowed to region classes | not run |
| 7 | Rare-class synthesis (PV-DDPM, copy-paste) | capped ≤ 30% synthetic | low priority | not run |
| 8 | Anomaly prior from normal cells | EI-AE crack pixel AP 0.14 | downgraded | not run |
| 9 | Active learning for WattCycle's labelling | – | park for part 3 | not run |

**Recommended thesis shape at the time (§5, "my pick; yours to decide"):** title idea *Learning rare, thin EL defects from few, noisy labels*; Ch.1 diagnosis and protocol; Ch.2 one tolerance mechanism for both kinds of noisy target (human labels and pseudo-labels) with per-class routing; baselines including supervised with the fixed recipe, MT/FixMatch with correct CE, ALHVR, BUR, DCF, DHC, MIM-pretrained supervised; test beds UCF-EL re-split and BenchmarkEL revised labels. Fallback: noise-aware supervision plus MIM pretraining with the diagnosis.

**Important:** on 11 Oct the user set the rule "framing depends on final results, no presumptions, ever". The directions report's thesis shape is a historical recommendation, not the current framing. Current evidence is in `11_results_synthesis_and_claims.md`.

The report's own later updates (§0, §0.1) record P6–P10 outcomes as they came in (for example "P10, label budget (5%): no loss passes"; the pipeline handicap grows as labels shrink). Those are superseded by the per-experiment READMEs.

---

## 19. Conflicts and open checks in the literature record

| Item | What the sources say | Status |
|---|---|---|
| Pratt absent-class rule | phase 1 handoff: rule B primary, "reproduces Pratt"; `analysis/papers_metrics.md`: rule A or close variant fits the paper | rule A better supported; paper silent |
| Fioresi "57.3 mIoU" | `papers_metrics.md` first said not in the paper; corrected: it is in the abstract | likely 5-class incl. background [inferred] |
| Fioresi background threshold | paper 0.54, code 0.52 | both right for their source |
| PV-S3 thresholds | Tables 1–2 (0.6, 0); §4.2 and journal (0.2, 0.4) | inconsistent inside the paper |
| PV-S3 learning rate | paper/CLI 1e-3; released config 1e-2 | paper ≠ code |
| ALHVR λ equation | `papers_metrics.md` §5.2: paper has no square; `alhvr_port_notes.md` §7: paper with square | check Eq. 10 in the PDF; code is squared and ramps over the whole run |
| ALHVR prototype "NaN" | phase 0 handoff: NaN from division by zero; phase 1 handoff and port notes: zero prototype vectors, no NaN | zero vectors (corrected) |
| Cosine ceiling at C = 24 | phase 0: ~0.24 max softmax; audit: CE floor 1.41 | consistent statements of the same limit |
| Pratt image count | paper 593; public repo 582 | discrepancy is paper vs its own repo |
| Which release Pratt 2023 used | handoff: 20211104; PV-DDPM: SCDD = 20221008 | open |
| Torpey's dataset | 642 images = release 20220723 (different test set) | resolved (`F04` §1a) |
| Torpey's 22k unlabelled set | `A02`: released; `F02`, `F04` §2: URLs redacted in arXiv v1, no public link | no public link found; open |
| PV-S3 "CSB" S2 / S3 | `F05`: S2 2,109 images (15 classes), S3 2,282 (16 classes), look like larger Pratt-group releases; handoff §3.1: train+val of the later releases with augmented copies counted; phase 1 handoff §4: 20220723 (28 classes) / 20221008 (29 classes) | unverified (`to_human/directions_2026-10-10.md` §7) |
| "No tolerance/skeleton-aware SSL objective" | survey 8 Oct claimed none; F01 found ITC, HAIC-NET, SemiCurv | reworded gap (see §11) |
| CaPro, DCF, two ALHVR citers | read at abstract/method-grep level | read in full before claiming novelty |

---

## Related docs
- `00_START_HERE.md` (index and reading order)
- `01_project_overview_and_scope.md` (the three-part thesis plan; scope decisions such as power loss)
- `02_domain_primer_EL_and_defects.md` (EL imaging, crack modes, why inactive area matters)
- `03_datasets_and_splits.md` (BenchmarkEL releases, E-SCDD masks, UCF-EL, external pool, ELPV/BMRK overlap)
- `04_glossary_and_naming.md` (Mean Teacher, pseudo-labels, CutMix, relF1@2, arm names)
- `06_history_phase0_phase1.md` (how these reproductions were done and what was lost)
- `07_methodology_rules_and_statistics.md` (the evaluation protocol the literature review motivated)
- `08_experiments_P1_P7_diagnostics.md`, `09_experiments_P8_P12_ssl_series.md`, `10_experiments_P13_P16_E1.md`
- `11_results_synthesis_and_claims.md`, `13_problems_pitfalls_open_issues.md`
