# Papers: metric conventions, recipes, and our numbers against theirs

Sources: the PDFs in `scratchpad/papers/` (text extracted with pdftotext, tables read from the page images), the ALHVR reference code (`gaint/ALHVR_ref/train_ALHVR/code/`), our metrics module (`gaint/repo/src/evaluation/metrics.py`) and our reports (`gaint/repo/reports/day1.md`, the handoff of 7 Oct).
Labels: **[paper]** quoted or read from the paper. **[code]** read from code. **[ours]** our measured numbers. **[inferred]** my reasoning, not stated anywhere.

---

## 0. Metric conventions side by side

| | Unit of IoU | How it is aggregated | Background | Images or classes absent from the ground truth | Classes scored | Checkpoint |
|---|---|---|---|---|---|---|
| **Pratt 2023** | per image, per class | **median over the 50 test images** (Fig. 6–8: "The median IoU was computed for each image/class combination", §3.4) | not scored | not stated. Nonzero inactive medians (for example 0.38 for 4c) with inactive in only 17 of 50 test images rule out "absent = 0" (rule B), which forces the median to 0. 4a (inactive recall 0.15, so it rarely predicts inactive) has median 0.13, which rules out rule C (it would give about 1). **So rule A (leave the image out) or a close variant [inferred]** | crack, gridline, inactive (+ ribbons, spacing) of 24 trained | not stated |
| **Fioresi 2022** | pixel level, dataset level (sklearn classification reports, §IV-A) | per-class P / R / F1. The IoU formula is given but **no IoU table** | the no-defect class is in the weighted F1 (0.95) and unweighted F1 (0.69). The per-class table is defects only | – | 4 defects (+ no-defect) | "After each epoch, we validate the model on the validation/testing set", and hyperparameters were set by "hit and trial". **This is a single val/test set, so selection on test is likely [inferred]** |
| **Jha PV-S3 2025** | dataset level, Eq. 9 (TPᵢ / (TPᵢ+FPᵢ+FNᵢ)) | mean over the 4 defect classes | **not in the class set.** Released code: `ignore_index=0`, so background is never predicted. Their val log is matched only by our `pvs3` convention (pixels with background ground truth dropped) [ours, handoff 6.10] | – | 4 UCF defects. CSB-S1: crack, gridline, inactive | not stated. The released split lists put 1,769 of the 2,289 public test images in train and 437 in val [ours] |
| **Gangopadhyay 2025** | probably per image ("Mean ± Standard Deviation", Table I) [inferred] | mean over classes ("The mean of these metrics over all the classes is used") | **included** (accuracy is 1.00 for every model on T2) | – | MIAD: good / broken / foreign body / missing cells | ReduceLROnPlateau + EarlyStopping. The monitor is not stated |
| **ALHVR 2025** | per 3-D case, per foreground class (medpy `dc`) [code `test_acdc.py`, `val_2d.py`] | mean over cases, then over classes | excluded (classes 1..C−1) | an empty prediction scores Dice 0 [code] | 3 ACDC structures | **best val Dice**, checked every 200 iterations on 10 val patients, then tested [code lines 254–277, `test_acdc.py:92`] |
| **Ours** | one dataset-level confusion matrix (`standard`) | mean of crack + inactive (BenchmarkEL), 4 defects (UCF) | **in the confusion matrix**, so false positives on background count | absent class is NaN and left out of means | as left | final step (primary) |

Our module also computes `pvs3` (background-GT rows dropped) and `pratt_median` rules A, B and C (`metrics.py` docstring). Rule B is our "primary" Pratt rule. **That choice is the wrong match for the paper** (section 1.3).

---

## 1. Pratt et al. 2023, BenchmarkEL (Systems and Soft Computing 5, 200048)

### 1.1 Data [paper]
- Abstract: "593 cell images", 24 classes (12 features, 12 defects). The public `dataset_20211104` has 478 + 54 + 50 = 582. **11 images unaccounted for [inferred, minor].**
- §3.2: "Fifty images with a prevalence of cracks, gridline defects, and inactive areas were assigned to testing, evenly split for mono- and multi-silicon wafers. Fifty-four images were randomly selected ... for validation." **The test set is hand-picked for defects, not random.**
- Training images augmented offline with a 180° rotation, mirror and flip: "896 mono-si ... and 1016 multi-si ... total of 1912". 1912 / 4 = 478, so it matches our train split.
- 512 × 512 per image (§3.1).
- Median ground-truth pixels per test image: crack 557, inactive 1,288, gridline 1,750, spacing 12,529, ribbons 12,871 (§4).

### 1.2 Recipe [paper]
- Four models: U-Net_12 (Divam, 12.3M), U-Net_25 (Tomar, 25.9M), PSPNet (58.0M), DeepLabv3+ (22.4M) (Table 1). **The encoder is not named. VGG16 in our reproduction came from the user's spec, not from the paper** (also noted in day1 §5).
- Weighted CE with three weight sets: A all 1. B inverse median pixel percentage per class (Eq. 1). C custom: background 0.2, ribbons 3, gridline 10, inactive 10, crack 20, others 1 (Table 2).
- **No optimiser, learning rate, epochs, batch size or schedule.** The code is "adapted from code published on the respective GitHub repositories".
- [inferred] Set B divides by the median pixel share, which is 0 for any class absent from more than half the images (inactive is in about 9% of train images). B weights for rare classes are infinite or arbitrary unless they computed something else. The B rows score 0.00 inactive IoU and recall for 1b, 2b and 3b.

### 1.3 Numbers (Fig. 7 median IoU, Fig. 8 median recall, read from the page image)

| Model | crack | gridline | inactive | avg defects | crack recall |
|---|---|---|---|---|---|
| 1a U-Net_12 equal | 0.13 | 0.32 | 0.25 | 0.24 | 0.14 |
| 1c U-Net_12 custom | 0.26 | 0.22 | 0.00 | 0.16 | 0.90 |
| 2a U-Net_25 equal | 0.15 | 0.32 | 0.09 | 0.19 | 0.18 |
| 2c U-Net_25 custom | 0.22 | 0.18 | 0.00 | 0.13 | 0.89 |
| 3c PSPNet custom | 0.17 | 0.14 | 0.11 | 0.14 | 0.43 |
| 4b DeepLabv3+ inverse | 0.18 | 0.14 | 0.20 | 0.17 | 0.93 |
| **4c DeepLabv3+ custom (headline)** | **0.25** | 0.20 | 0.38 | **0.28** | **0.86** |

Abstract: "the mIoU for cracks is low (25%) even for the DeepLabv3+, the recall is high (86%)". §4: "The low mIoU values for defects are driven by the low precision ... driven more by dilated predictions". **Low crack precision is a known property of this benchmark with weighted CE, not something our pipeline created** (our crack precision is 0.22–0.35, recall 0.67–0.73).

### 1.4 Ours against theirs
- **Under their likely convention (rule A, per image, median), our models match or beat the paper [ours, day1]:**
  - Pratt-A (U-Net VGG16, equal weights, final): crack 0.149, gridline 0.339, inactive 0.420, mean **0.303**. Paper 2a: 0.15 / 0.32 / 0.09 (avg 0.19). Crack and gridline match almost exactly; inactive is higher.
  - Pratt-C final: 0.176 / 0.207 / 0.445, mean **0.276**. Paper 2c: 0.22 / 0.18 / 0.00, 1c: 0.26 / 0.22 / 0.00.
  - Pilot U-Net++ arms, rule A means: SL-100 0.280, SL-20 0.287, MT-20 0.288, ALHVR interim 0.295. Paper best 4c: **0.28**.
  - Crack median (crack is in all 50 test images, so every rule gives the same value): our U-Net++ arms 0.21–0.25, Pratt-A 0.149, Pratt-C 0.176. Paper 0.13–0.26.
- **So no reproduction gap remains on BenchmarkEL once the convention is aligned.** The apparent gap in day1 ("ours 0.116 / 0.145 against the paper's U-Nets 0.133 to 0.160") comes from comparing our rule-B means with the paper's 1c / 2c rows. The paper's numbers cannot be rule B (1.3, section 0). Under B every model's inactive median is 0, so the B mean is capped at about 0.67 and is not what Pratt reported.
- Dataset-level `standard` crack IoU (ours 0.25–0.30) is higher than the per-image median crack IoU (0.15–0.25). Pooling weights the big-crack images more heavily [inferred from the definitions; matches both sets of numbers].
- Their test set was chosen for defect prevalence. All 50 test images contain crack. That flatters crack recall and hides the label effect on inactive (handoff 6.7).

### 1.5 Where the paper's protocol is weak
- One run per model, no seeds, no error bars, no training protocol. The custom weights were "validated with a 16-run screening DOE". **Against which split is not stated.** If against test, that is selection on test [inferred].
- The handling of absent classes in the median is not stated. It changes the mean by about 3× (our rules B → C: 0.15 → 0.49).

---

## 2. Fioresi et al. 2022, UCF-EL (IEEE J. Photovoltaics 12(1))

### 2.1 Data [paper]
- 17,064 images = 16,808 real + 256 Griddler-simulated (§II-A, Table II). Images without defects were removed to undersample ("We ignore images without defects").
- Four defect categories: crack (closed + resistive + isolated), contact (front-grid interruption + near busbar), interconnect (highly resistive), corrosion. "Disconnected interconnects are currently ignored". A bright-spot class was tried and dropped.
- **80/20 split into "training and validation/testing sets". There is one held-out set.** Simulated images are in train only.
- Images about 300 × 300. "Randomly resized, and randomly center cropped ... (224 × 224)".
- **The public release has 9,562 train + 2,289 test = 11,851 [ours].** That is not the paper's 16,808 real images, and the test split differs.

### 2.2 Recipe [paper]
- DeepLabv3 (not v3+) ResNet-50, **COCO-pretrained** (torchvision style, 21 classes replaced). Auxiliary loss. Plain CE (weights tried and dropped). lr 0.005. Optimiser and epochs not stated.
- Augmentation: H flip, V flip, 90° rotation (independent p = 0.5), Gaussian blur 7×7, σ 2 on all training images.
- **Post-processing: a pixel is background only if P(background) > 0.54**, else argmax over the defect classes (§III-D, §IV-A). This was tuned by hit and trial.

### 2.3 Numbers (Table II, read from the page image)

| | crack P/R/F1 | contact | interconnect | corrosion |
|---|---|---|---|---|
| without simulated (16,808) | .81 / .80 / .80 | .68 / .46 / .55 | .14 / .34 / .20 | .73 / .79 / .76 |
| **with simulated (17,064), headline** | .81 / .80 / **.81** | .66 / .51 / **.58** | .26 / .44 / **.33** | .69 / .89 / **.78** |

Weighted F1 0.95, unweighted F1 0.69 (these include no-defect at F1 0.98). Pixel accuracy 95.4%.
IoU equivalent of the headline F1, IoU = F1 / (2 − F1) at dataset level [inferred, exact identity]: crack **0.681**, contact **0.408**, interconnect **0.198**, corrosion **0.639**, mean **0.481**.

### 2.4 Ours against theirs [ours, handoff 6.9, converted to F1]
- **SL-100 (95,760 steps):** IoU 0.675 / 0.479 / 0.332 / 0.660, which is F1 **0.806 / 0.648 / 0.498 / 0.795**.
- **SL-20:** IoU 0.651 / 0.442 / 0.245 / 0.635, which is F1 0.789 / 0.613 / 0.394 / 0.777.
- **So our supervised baseline equals Fioresi on crack and beats it on contact, interconnect and corrosion, even at 20% labels.** That holds on a smaller public dataset and without their 0.54 background threshold.
- Remaining differences, so these are not a strict reproduction:
  - different data and test split;
  - DeepLabv3 COCO against our DeepLabV3+ ImageNet;
  - 224 random crops against our shorter side 295 with 256 crops;
  - their probable test-set selection.
- **"mIoU 57.30" attributed to Fioresi by Jha et al. (Table 4) is not in Fioresi's paper.** The paper has P/R/F1 only. Day1 says it comes from Fioresi's code and includes background (unverified here). Jha's P/R/F1 for Fioresi (59.00 / 59.75 / 57.75) are exactly the means of the **without-simulated** row, not the better headline row. Mean IoU from those F1s would be 0.442, not 0.573 [inferred]. An IoU mean of 57.30 next to an F1 mean of 57.75 is not possible over the same 4 classes, because IoU < F1 for every class strictly between 0 and 1 [inferred].

---

## 3. Jha et al. 2025, PV-S3 (Eng. Appl. AI 160, 111790)

### 3.1 Data [paper]
- UCF-EL, 4 defect classes. Healthy images' masks are background.
- CSB-Dataset S1 / S2 / S3 = Pratt's data with 593 / 2,109 / 2,282 images, scored on crack, gridline and inactive only. Handoff 3.1: the S2 and S3 counts include the pre-augmented copies.
- **The split is not described in the paper** beyond "20% of the labeled data and 80% of the unlabeled data from the training set". The released lists leak test images (section 0).

### 3.2 Recipe [paper §4]
- DeepLabv3+, ImageNet ResNet-50, Mean Teacher.
- **30 epochs**, batch 16, SGD lr 0.001, weight decay 1e-4, momentum 0.9. Consistency weight λ = 1.5. **No ramp-up is described.** EMA decay α is not given numerically.
- Base size 299 × 299, crop 224.
- Student gets the strong view: jitter ±50%, grey p 0.2, blur, CutMix (Beta 4, 4). Teacher gets the weak view, which is **normalisation only**.
- SemiCE (Eqs. 2–4) with thresholds t_pos / t_neg:
  - Tables 1–2 use (0.6, 0). §4.2 later says "we chose ... (0.2, 0.4)" (Table 7 S2: 71.75).
  - **As printed, the unlabelled loss uses Y_L, "the ground truth label", for the N_U unlabelled images, and its softmax runs over the H × W positions, not over classes.** At best the notation is wrong. Whether the released code uses ground truth anywhere in the unlabelled loss should be checked in their code [not verified here].

### 3.3 Numbers [paper, Tables 1–4, 6]

| | crack | contact | interconnect | corrosion | **mean IoU** |
|---|---|---|---|---|---|
| SL 20% (Table 1) | 25.29 | 6.89 | 0.85 | 2.03 | **8.76** |
| SSL 20% (PV-S3) | 89.00 | 49.00 | 40.00 | 90.00 | **67.00** |
| FSL 100% (Table 3) | 88.38 | 52.92 | 59.70 | 82.39 | **70.84** |
| SSL 100% | 91.78 | 58.29 | 53.89 | 95.26 | **74.75** |

Table 2 (3 subsets): SL 9.06 ± 0.09, SSL 66.53 ± 1.35.
CSB-S1 (Table 5): SSL 20% crack 50, gridline 74, inactive 50 (mean 58.0). FSL 100% 58 / 83 / 50 (63.67).

### 3.4 Ours against theirs
- **Convention.** Their per-class IoU equals F1/(2 − F1) (crack 93.83 → 88.38), so it is a dataset-level confusion matrix [inferred, consistent]. Background is not a class. With background never predicted, the task collapses to "which defect type is this already-known defect pixel". Our numbers in the same convention:
  - **SL-20 at their stated budget** (30 epochs, lr 1e-3, 3,585 steps): **0.230** pvs3, 0.185 standard [ours, day1 §7];
  - SL-20 at 12k steps, lr 5e-3: **0.559** pvs3, 0.448 standard;
  - FSL 100 epochs: 0.636 pvs3, 0.497 standard;
  - their released code as shipped, our splits: **0.828 pvs3, 0.050 standard** [ours, handoff 6.10];
  - an all-crack predictor scores crack IoU **0.766 pvs3** and 0.066 standard [ours, day1 probes]. Dilating predictions by 3 px raises pvs3 from 0.636 to 0.717 and lowers standard from 0.497 to 0.456.
- **Mismatch 1: their SL-20 is 8.76; ours under pvs3 at their budget is 23.0, and 55.9 at 12k steps.**
  - Their SL baseline is under-trained or broken. Their own §4.2 says SL-20 "is not able to learn the features ... very low pixel accuracy".
  - [inferred] With "30 epochs" counted over the labelled set (about 120 steps per epoch) for SL, but over the larger unlabelled stream for SSL, the SSL arm gets several times more optimiser steps. That is the step mismatch our step-matched control exposed: UCF SL-20 0.448 at 12k against 0.491 at 95,760 steps.
  - The handoff also notes their supervised-only mode does not run in the released code.
  - **Explained by: recipe/budget (strongly supported) plus metric convention.**
- **Mismatch 2: their SSL-20 is 67.0; our PV-S3 reimplementation v2 is 0.568 pvs3 / 0.276 standard; with the class cap 0.580 / 0.418.**
  - Partly convention. Partly the corrosion runaway, which pvs3 hides (corrosion 0.879 pvs3 against 0.067 standard).
  - Partly leakage in their evaluation, through the released splits.
  - **The size of their gain is not reproducible under the standard convention. Our step-matched SL control is 0.491, above every PV-S3 arm [ours].**
- **Mismatch 3: their FSL-100 is 70.84; our nearest is 0.636 pvs3 (FSL 100 epochs). Our SL-100 at 95,760 steps under pvs3 was not found in the local reports.**
  - Plausibly convention plus a background-never-predicted model plus leaked splits [inferred].
  - Their released code reproduces its own val log (0.828) on our splits. **Their paper's 74.75 / 70.84 are below their own code's 0.828, so the paper and the code are not the same configuration [inferred].**
- **Their BenchmarkEL comparison (Table 6) is invalid.**
  - The "Pratt" baselines are copied from Pratt's Fig. 7 / 8 custom-weight rows: 4c 0.28 / recall 0.75, 1c 0.16 / 0.58, 2c 0.1333 / 0.6067, 3c 0.14 / 0.43, all matching to the digit [inferred by matching].
  - Those are **per-image medians from 24-class models**. PV-S3's own numbers are dataset-level IoU over 3 defect classes, with background apparently not predicted.
  - The "+30% IoU over the state of the art" claim compares two different metrics. Our crack IoU under pvs3 is 0.585 (`alhvr_20pct_s1`) against their 50–58, which is the like-for-like reading.

---

## 4. Gangopadhyay et al. 2025, SA U-Net++ (IEEE TETCI 9(2))

- **No EL data at all.**
  - T1: satellite PV panel versus background (3,716 images).
  - T2: MIAD UAV solar-panel defects, 4 classes (good, broken, foreign body, missing cells), reduced to 2,700 train / 300 test by dropping 2,000 good images.
  - T3: FloodNet.
  - T4: oil spill.
- TensorFlow, Adam, LR steps 1e-3 → 2e-4 → 4e-5 → 1e-5 with ReduceLROnPlateau and EarlyStopping, batch 16, 30–70 epochs. Augmentation: flip, 90° rotation, noise, blur, brightness.
- Metrics: P, R, Jaccard, Dice, Accuracy, "mean of these metrics over all the classes", reported as mean ± sd. **Probably per image, with background in the class mean [inferred]** (accuracy is 1.00 for every model on T2).
- T2 (Table I): SA U-Net++ J **0.95 ± 0.09**, D 0.96 ± 0.08. U-Net++ J **0.92 ± 0.12**, D 0.94 ± 0.11. **+0.03 J, inside one sd across images.** Single run, no significance test. Ablation (Table II) differences are 0.91–0.95 J.
- **Ours:** SA gate on BenchmarkEL gives −0.004 test (p 0.78) and −0.021 val+test. **This is not a contradiction. The paper never tested thin defects on EL, and its gains are on large objects under a background-inclusive mean.** No mismatch to explain. The paper gives no evidence that the gate helps 2–3 px structures.

---

## 5. Lei et al. 2025, ALHVR (ICCV)

### 5.1 What it targets [paper]
- Medical SSL segmentation with dual networks. The claim is that "high-value regions", meaning **ambiguous or low-confidence pixels, typically boundaries**, deserve targeted losses. Table 1 is a CPS experiment on ACDC at 10%: masking out Region 1 (both confident) during training gives the best Dice, 88.58 against 85.34 with all regions.
- **It does not target class imbalance or rare classes.** Datasets: ACDC (RV / LV / Myo), AbdomenCT-1K (liver, kidney, spleen, pancreas), BraTS (binary tumour). All are large, compact structures with few classes.

### 5.2 Recipe [paper §4.2 + code]
- U-Net (ACDC, AbdomenCT) and V-Net (BraTS).
- **SGD, lr 0.01, momentum 0.9, wd 1e-4, constant learning rate** (no schedule in the training loop) [code lines 155–156].
- 30k iterations, batch 16 = **8 labelled + 8 unlabelled** (`labeled_bs=8`). BraTS: batch 4, 15k iterations. ACDC patch 256 × 256.
- Supervised loss: **CE + Dice**, unweighted (Eq. 3–4, code 182–189).
- **λ.** Paper Eq.: λ(t) = 0.1 × e^(−5(1 − t/t_max)) (no square). Code: `0.1 * sigmoid_rampup(iter_num // 150, 200)` = 0.1·exp(−5(1−t/30000)²). Both **reach 0.1 only at the final iteration.** Code value is 0.0029 at t = 30% and 0.029 at t = 50%. Under the reference's constant learning rate, the late, strong λ still gets full-size updates.
- γ = mean of the lowest β fraction of the **batch-global** averaged perturbed confidence. β 0.8 (ACDC), 0.7 (AbdomenCT, BraTS).
- **DTCT sharpening is elementwise binary**, P^(1/T) / (P^(1/T) + (1−P)^(1/T)) with T = 0.1 [code lines 38–41], not a class-normalised sharpening. A probability below 0.5 goes to about 0 (0.4 → 0.017) and above 0.5 to about 1. MSE is on softmax outputs.
- Feature perturbation: noise or dropout on encoder features (paper §3.1).
- Evaluation: per case, Dice / Jaccard / 95HD / ASD over foreground classes. **Best-val checkpoint** (val every 200 iterations).

### 5.3 Headline numbers [paper Tables 2–4]
- ACDC 10% (7 labelled): U-Net 81.59 → ALHVR **90.56 Dice** (upper bound 91.10 at 100%). 20%: 84.83 → 91.09.
- AbdomenCT 5%: baseline + 17.36 Dice.
- BraTS 10%: + 5.91 Dice over the baseline.

### 5.4 Our port against the reference (where the port differs)

| Item | Reference | Our port (handoff 4.5, 9.1) | Effect |
|---|---|---|---|
| Optimiser / LR | SGD 0.01, **constant** | Adam 1e-3, **cosine to 0** | when λ is large, our LR is about 0, so **the unlabelled loss is effectively never applied** |
| λ | 0.1·sigmoid ramp over the whole run | same | as above |
| Supervised loss | CE + Dice, unweighted | weighted CE (repo) | Dice matters for thin structures. Not tested |
| Batch | 8 L + 8 U | 4 L + 4 U | BN statistics and gradient noise |
| Classes | 4 (ACDC) | 24 | per-batch argmax prototypes with 24 classes, most absent in a batch. Cosine scale 1 caps the logits, so the CE floor is high (handoff: 1.41) |
| Selection | best val Dice | final step | ours is stricter; theirs flatters |

### 5.5 Does the design make sense for 2–3 px rare defects? [inferred, with our diagnostics as evidence]
1. **Region routing is class-agnostic and batch-global.** γ comes from all pixels, which are about 86% background and padding. Rare-class pixels are low-confidence almost by construction, so they fall into Ω3 en masse. Ours: 71% of true crack pixels are in Ω3. There, DTCT's "teacher" is the more confident of two unreliable networks: crack winner accuracy 61.9%, and 20.7–32% of Ω3 crack pixels are taught "background". **For rare classes DTCT's pseudo-label is wrong about 40% of the time, and wrong toward background.**
2. **Elementwise sharpening with 24 classes.** Where the winner's top probability is below 0.5 (common in Ω3 with many classes), the sharpened target is near 0 for **every** class. MSE then pushes the perturbed output's largest probabilities down, flattening predictions in the region where defects live.
3. **CG-CPCL prototypes come from per-batch argmax on unlabelled pixels.** A rare class contributes no pixels, or a few wrong ones, in most batches. Ours: cross-network prototype crack accuracy is 4.6%, and 1.1% for per-batch prototypes. Only own-network prototypes carry signal (43–49%).
4. **Scale and λ.** λ max 0.1 against a supervised CE+Dice of order 1. Even in the reference, the unlabelled terms are a small regulariser that matters late.

**What carries over to a rare-class design (ideas, not tested):**
- Keep the idea of routing losses by **joint confidence of two networks**.
- Make the threshold **class-conditional**: per-class γ_c from class-wise confidence quantiles, or from labelled-set calibration.
- Build prototypes from **labelled ground-truth pixels in an EMA memory bank** (class-balanced) rather than per-batch unlabelled argmax. Use a proper temperature on the cosine logits.
- Replace elementwise sharpening with **class-normalised sharpening** (softmax(log p / T)) and a **detached** target.
- Ramp λ to full strength early, under an LR schedule that leaves room to apply it: constant or poly, or our cosine with λ reaching full value by about 20% of training.
- Use the reference's CE + Dice (or Tversky) for the supervised part.
- Score per class with threshold-free AP alongside IoU.
- UniMatch's defaults show the alternative: constant λ = μ = 0.5 from step 0, τ = 0.95, 50% channel dropout at the encoder-decoder junction, 8 L + 8 U, poly LR.

---

## 6. Mean Teacher and UniMatch (recipe defaults) [paper]
- **Mean Teacher:** MSE consistency, weight ramped up "during the first 80 epochs" (sigmoid ramp), EMA α = 0.99 during ramp-up and 0.999 after. Input noise (translations, flips, Gaussian noise) and dropout differ between student and teacher. **Without different noise or views for the two, the consistency target equals the prediction and gives almost no gradient** (Tarvainen §2) [inferred consequence].
- **UniMatch:** DeepLabv3+ ResNet, 8 L + 8 U. SGD lr 0.001 / 0.005 / 0.004 (Pascal / Cityscapes / COCO) with poly decay. τ = 0.95 (0 for Cityscapes). λ = μ = 0.5 constant. Weak view: resize 0.5–2.0, crop, flip. Strong: colour + CutMix. Feature perturbation: `nn.Dropout2d(0.5)` between encoder and decoder.

---

## 7. Our number against theirs, explained by X

| Paper | Their number | Our nearest like-for-like | Gap | Explained by |
|---|---|---|---|---|
| Pratt 4c, avg defect median IoU | 0.28 | U-Net++ arms rule A 0.28–0.30; Pratt-A 0.303 | none | **metric convention.** Our day1 compared rule B, which is not the paper's. Matched on rule A |
| Pratt crack median | 0.13–0.26 | 0.15–0.25 | none | – |
| Pratt inactive median | 0.00–0.38 | 0.42–0.45 (rule A) | ours higher | convention ambiguity + their weight sets B / C zero inactive. Not a deficit on our side |
| Fioresi crack / contact / interconnect / corrosion F1 | .81 / .58 / .33 / .78 | SL-100 .81 / .65 / .50 / .80; SL-20 .79 / .61 / .39 / .78 | ours ≥ | different data and split; their test-set selection and 0.54 background threshold. **No deficit** |
| PV-S3 SL-20 | 8.76 (pvs3) | 0.230 at their budget; 0.559 at 12k | ours far higher | **their baseline is under-trained or broken (recipe/budget)** |
| PV-S3 SSL-20 | 67.0 (pvs3) | v2 0.568 pvs3 / 0.276 std; classthr 0.580 / 0.418 | ours lower | convention (pvs3 hides runaway classes), probable split leakage, paper ≠ released code (code val 0.828). **Under standard, step-matched SL (0.491) beats every PV-S3 arm** |
| PV-S3 FSL-100 | 70.84 (pvs3) | 0.636 pvs3 (100 epochs) | −0.07 | convention + background never predicted + leakage [inferred]; partly unexplained |
| PV-S3 "+30% over Pratt" on CSB-S1 | 58.0 vs 28.0 | – | – | **invalid comparison:** dataset-level pvs3-style IoU against per-image median from 24-class models |
| SA U-Net++ | +0.03 J (MIAD) | −0.004 (BenchmarkEL) | – | different domain and object scale; within their per-image sd; single run |
| ALHVR ACDC | +9 Dice over baseline | +0.005 ± 0.023 against loss-off | – | **our port's LR schedule (cosine → 0) cancels the late λ ramp.** Also a 24-class rare-defect setting the design does not target. Not a fair test yet |

---
## Correction (2026-10-08, verified against the paper text)
The claim above that "Fioresi mIoU 57.30" is not in Fioresi's paper is WRONG. The abstract states "a mean intersection
over union score of 57.3%" (Fioresi_UCF-EL.txt line 13). What still holds: it cannot be a 4-defect IoU mean next to a
4-defect F1 mean of 57.75; it is most likely a 5-class mean including background (unverified). PV-S3 citing it is
therefore not fabricated, but comparing it with a background-free 4-defect mean is still apples to oranges.
