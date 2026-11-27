# EE511 presenter script (deck of 25 Nov 13:50, 19 slides, ~15 min)
Written by the guide session. Every number is from a file; source in brackets. "Say" = what to speak. Q = likely panel question, A = answer.

## 1. Title (15 s)
Say: "I'm Yash Patil. My project segments cracks and inactive regions in electroluminescence images of solar cells, pixel by pixel, and builds a fair way to measure it. The picture is one cell: a crack, and a dark fragment the current no longer reaches."
- Q: Module or cell? A: Cells cut from module images, 512 x 512.

## 2. The problem (45 s)
Say: "In EL imaging we drive current through the cell and it glows in the near-infrared; cracked or cut-off parts glow less, so they look dark. Two classes matter most. Crack is 0.19% of the pixels and is labelled 1 to 2 px wide, so a 1 px offset already costs a lot of overlap. Inactive area is rare. Each cell has 24 classes. The one idea: published EL scores don't compare, so I first built a fair measurement, then tested what improves it."
- Q: Why is crack hard for a CNN? A: Rare, thin, and a network that predicts at reduced resolution loses it: width-matched, output stride 4 costs about 0.02 and stride 8 about 0.08 to 0.10 on the crack metrics [doc 23 s4.4]. And the label width is a drawing convention.
- Q: Why not weight the loss by class frequency? A: Pratt's weighted CE drew cracks 3.05x too wide (precision 0.648) and was 0.093 below the baseline on relF1@2 [T15, T16a].
- Q: What is inactive? A: Cell area electrically cut off, usually by cracks; dark in EL, loses power.

## 3. Related work (50 s)
Say: "Pixel-level EL segmentation is a short line: Pratt 2021, a U-Net on 148 cells; Fioresi 2022, DeepLabV3 on UCF-EL; Pratt 2023, BenchmarkEL, the 24-class dataset I use; Hanifi 2025, a VGG16 U-Net on 29 classes. I read 22 papers with pixel-level EL numbers in full. None states a split that keeps a module's cells together, and 18 give no interval, seed count or repeat. So their numbers can't be compared. Below are the general CV methods I brought in."
- Q: Did you read 639 papers? A: Agent teams screened 639 across 44 search directions and gave each a status; the 22 are the EL papers with pixel numbers, read in full [doc 23 s3; RELATED_WORK s4].
- Q: Why does a module-disjoint split matter? A: Cells of one module share manufacture and imaging, and neighbouring crops can overlap; one cell in train and its neighbour in test inflates the score.
- Q: Do you beat Pratt 2023? A: Not a claim. In their convention on test50 our crack median IoU is 0.383 vs their 0.25, but 8 test cells are the same physical cell as our training cells and their averaging rule is inferred: context only [FINAL_OPENING_READ].

## 4. Dataset (50 s)
Say: "Development uses 532 labelled BenchmarkEL cells, the old train and val sets, from five sources. I use 5-fold cross-validation where all cells of one physical module stay in one fold, so every cell is predicted by a model that never saw its module. The pool has no half-cut cells. Two sets stay sealed. E1: 106 cells from unseen modules, 101 from CSIR, 62 half-cut; the final models were scored on it once, under a rule fixed before the read. test50 is the old official test set; 8 of its cells are the same physical cell as a pool cell, so it is context only."
- Q: Why CV and not a fixed split? A: With 532 cells, CV scores every cell once out of fold: 532 test cells, not 50, so tighter intervals.
- Q: How do you know modules? A: Image ids, serial numbers printed on ARTS images, SDLE file names, pixel matching (md5, correlation, DINOv2 embeddings). The first split had 24 modules across two folds (91 cells); the leak check found no measurable inflation ("not separated"), and the split was rebuilt as cv5v3, 285 groups [T2; doc 24 s1-2].
- Q: Was E1 used before? A: Yes, 7 registered openings for earlier models plus reads before 31 Oct. The final models were never scored on it before [verdict.txt l138].
- Q: Is E1 truly unseen? A: A pixel check links no E1 image to any training image: "supported, not proven" [T2].
- Q: Labels? A: v1.1 = BenchmarkEL masks with scuff and star marks set to ignore and one cell restored; training on v1 vs v1.1 changes nothing measurable; the fix matters for scoring [T3a, T3c].

## 5. Research path (30 s)
Say: "Three questions in order. Does semi-supervised learning help? Yes at 5% labels, not detectable from 20%. Do recent methods help at full labels? Mostly not detectable; I kept one change, an encoder-preserving fine-tune. Measured fairly, what helps? A small confirmed gain on unseen modules; labelled cells of the new layout give much more, but that is a different comparison."
- Q: What does "exploratory" mean? A: Reads without a rule fixed in advance; they are labelled and decide nothing.

## 6. Experiments I: semi-supervised (60 s)
Say: "Inactive IoU on the old test set against the share of labelled cells. Grey is supervised only, purple is Mean Teacher using unlabelled cells too. At 5% labels, 23 cells, Mean Teacher lifts inactive from 0.253 to 0.370, interval +0.042 to +0.189. From 20% the lines nearly touch: +0.029, +0.006, +0.003, none detectable. Unlabelled data helped only when labels were scarcest."
Methods: Mean Teacher = teacher is a moving average of the student; it labels unlabelled cells; the student matches those labels on a harder-augmented copy plus the real labels. Separate BatchNorm = labelled and unlabelled cells in separate passes (before this fix the loss-off SSL arm was 0.017 crack IoU below supervised at 5%). CutMix = paste a box from one image into another and mix the teacher's prediction the same way.
- Q: Why inactive, not crack? A: Inactive was the clearest gain; crack relF1@2 +0.033 at 5%; crack n.d. from 20% [handbook 11 r3].
- Q: Are the bars intervals? A: No, seed sd; the 5% verdict used the pre-set rule plus a cell bootstrap.
- Q: Why does the gain vanish? A (reading): at 5% only 2 labelled cells have inactive, at 20% 9, at 50% 20; with many examples pseudo-labels add little.
- Q: Trust inactive on test50? A: Partly: 16 cells, 3 hold 59% of its pixels, and test50 was opened many times.
- Trap: say "not detectable with this recipe", never "SSL doesn't work".

## 7. Experiments II: what we tried (70 s)
Say: "Everything I tried, against the supervised baseline. On the old test set: Mean Teacher with CutMix helped inactive at 5% only. Two parts of SKCDF: not detectable. ALHVR, the 2025 method the project started from, was worse on all three metrics. Using 11,938 unlabelled cells by masked-image pretraining, DDeP or copy-paste: not detectable. A DINOv3 foundation encoder: no sign of a gain at the screen. Skeleton Recall gained once on E1, +0.036, and failed its guards on fresh seeds. clDice lost recall. Synthetic half-cuts: not detectable. One change I kept: the encoder-preserving fine-tune, because our standard fine-tune erased the pretrained encoder. Under the benchmark protocol, the final recipe gained +0.043 on E1."
One line per method if asked:
- SKCDF (CVPR 2025): we ran two parts: pseudo-labels kept out of the labelled decoder, and a balanced head. Full SKCDF never run.
- ALHVR (ICCV 2025): two networks; pixels split into regions by confidence, a different loss per region. Ours: -0.017 crack IoU, -0.132 inactive IoU, -0.031 relF1@2; post hoc, it halves inactive recall (0.276 to 0.124) [handbook 11 r17].
- MIM: hide image patches, train the encoder to rebuild them. DDeP: denoising pretraining. Copy-paste: paste labelled cracks onto unlabelled cells.
- DINOv3: self-supervised foundation encoder; screen F51 crack AP -0.0243, 2 seeds: KILL [handbook 11 r43].
- Skeleton Recall (ECCV 2024): a loss rewarding recall of the crack's centreline. clDice (CVPR 2021): Dice on soft skeletons.
- Encoder erasure: the standard fine-tune (Adam lr 1e-3, weight decay 1e-4, 20k steps) left ResNet-34 layer3/4 at cosine about 0 to their ImageNet start within 2,000 steps; PF (encoder frozen 1k steps, then 0.1x lr, no encoder weight decay) keeps 0.93 to 0.96 [handbook 16 Q29; 11 r23].
- Q: Why did almost nothing work? A: Most effects were below what we can detect; n.d. is not "no effect". The baseline is strong in-distribution (relF1@2 0.846); the real failure is unseen layouts, which most methods don't target.
- Q: Was ALHVR's loss a bug in your port? A: The port fixed the earlier port's problems and had a bit-identical loss-off control; the same two networks with plain cross pseudo-labels were level with supervised.

## 8. Methodology I: protocol (60 s)
Say: "How a method earns a claim. Split: 5 folds by physical module. Metric: relF1@2: precision is the share of predicted crack pixels within 2 px of a labelled crack pixel, recall the share of labelled crack pixels within 2 px of a prediction, and relF1@2 their F1. Margin M: the larger of 0.01 and twice the standard error of an A/A comparison, baseline seeds against other baseline seeds, so pure noise; M = 0.010. A method wins only if its gain is at least M and the lower end of the 95% interval is above 0. Guards stop it winning by drawing wider cracks, adding false cracks or hurting other classes. Stages: 2-seed screen, 5-seed row on the corrected split, at most 3 candidates read on E1."
- Q: Why not IoU? A: Same predictions score strict IoU 0.233 / 0.365 / 0.414 on 1 px / v1.1 / 3 px labels, and method contrasts change sign; relF1@2 contrasts move by at most 0.003 [thesis p. 27; slide 17].
- Q: Why 2 px? A: The 95th percentile of the distance between two annotations of one crack is 2.000 px [thesis s6.3].
- Q: What interval? A: CV5: two-stage group bootstrap (resample module groups, then one seed per fold), 2,000 draws. E1: seed-aware bootstrap over 71 clusters and the 5 models per arm.
- Q: Is the rule too strict? A: Of 15 two-seed A/A splits, none would be promoted, so the rule controls false wins; smallest detectable effect at 5 seeds 0.0055 [doc 23 s4.2; T4].
- Q: Why guards? A: A loss can buy recall with width: Skeleton Recall drew cracks 13% wider at argmax [doc 24 s3].

## 9. Methodology II: final model (50 s)
Say: "An HRNet-W18 encoder, which keeps a high-resolution branch in parallel with lower ones instead of downsampling and upsampling, and a U-Net++ decoder with nested skip connections. PF fine-tune keeps the ImageNet encoder. SWAD averages the weights from step 10k to 20k. D4 test-time augmentation averages predictions over 8 flips and rotations. CE plus Dice loss, 20k steps, all 532 pool cells. Cost 0.174 s per cell on one GPU for 8 views."
- U-Net: encoder downsamples, decoder upsamples, skips copy fine detail across. U-Net++: nested, dense skip paths refine features before they meet.
- SWAD: average weights over many training steps; the average sits in a flatter part of the loss surface, which tends to generalise. Ours: constant lr after warm-up, uniform average of steps 10k to 20k.
- D4: the 8 symmetries of a square; predict each, undo the transform, average the softmax.
- CE + Dice: per-pixel cross-entropy plus a Dice term that targets overlap and is not swamped by background.
- Q: Why HRNet? A: The only arm whose headline gain held at 5 seeds; the gain is recall at equal precision (relR@2 +0.015) [doc 24 s6.2].
- Q: Why not the 5-model ensemble? A: On E1 it adds nothing over its members (-0.0025) and costs 5x (0.855 s) [T9, T22].
- Q: Deployable speed? A: About 20,000 cells per hour of network time on one A6000 [T22 reading].

## 10. Quantitative I: 10 models, same training (50 s)
Say: "Ten models trained the same way on the pool cells. Baseline 0.844 relF1@2. Two EL-paper models fall 0.08 to 0.09 below: UCF-EL's DeepLabV3, 0.767, and Pratt's DeepLabV3+ with weighted CE, 0.751. Hanifi's VGG16 U-Net is level, 0.838. HRNet-W18 is highest at 0.856, and was promoted. These are 2-seed screens: a screen only promotes."
- Q: Why are the DeepLabs worse? A: Output stride: stride 8 costs 0.08 to 0.10, stride 4 about 0.02, width-matched; Pratt's weights draw cracks 3x too wide [doc 23 s4.4].
- Q: Plain fine-tune scores higher; why is PF the baseline? A: PF was adopted for unseen modules earlier; plain draws cracks wider (1.11x) and has 3.7x the false crack pixels on crack-free cells; at 5 seeds plain minus PF is +0.0059 [-0.0043, +0.0152], no verdict; its strict IoU edge sits inside the label-convention band [T6; doc 24 s6.2].
- Q: Faithful re-implementations? A: Their architectures under our training (same steps, crops, labels), except Pratt's loss; each card lists deviations.
- Q: SegFormer? A: Stride-4 decoder; cracks 20% wider; screen FAIL [doc 24 s3].

## 11. Quantitative II: 5-seed confirmation (60 s)
Say: "Promoted arms at 5 seeds on the corrected split. Right: difference from the baseline with 95% intervals; dashed line is the margin. HRNet passes the headline but fails two guards: more false crack pixels on crack-free cells, and crack width on one source. SWAD alone doesn't reach the margin. HRNet plus SWAD passes but fails guards. D4 on the baseline is confirmed, +0.013. The final recipe passes its CV5 check, +0.022, but I chose its readout on these same cells, so it is selection-biased; E1 is the real test. No trained arm was confirmed under its rule."
- Q: How bad is HRNet's guard fail? A: 767 vs 212 false crack px over 303 crack-free cells (3.6x, limit 1.5x), about 1.8 px per cell; PF is unusually clean [doc 24 s6.2].
- Q: Is HRNet's gain robust? A: Fragile: removing one module group drops it below M, and on 3 px labels it doesn't pass; HRNet plus SWAD passes under all label variants [thesis p. 27 to 28].
- Q: SWAD raised strict IoU? A: +0.018 with interval above 0, as precision at unchanged recall; the tolerant metric doesn't reward it; reported, not claimed [T20 r11].

## 12. Quantitative III: sealed E1 (70 s)
Say: "The sealed test, read once for these models. Baseline relF1@2 0.447, final 0.490: +0.043, interval +0.001 to +0.104, all guards pass: confirmed. False crack pixels drop from 3,218 to 2,421. Below, printed beside and deciding nothing: with the same 8 views on both sides, +0.045 with a tighter interval, so most of the gain is the model; D4 alone on E1 is not resolved; one single final model is +0.019, not significant; baseline seeds against each other, +0.002, the noise. The gain sits in the 44 full cells, +0.146; on half-cut cells +0.011, not detectable. Levels near 0.45 to 0.49, against 0.85 in-distribution, show a large domain gap."
- Q: The lower bound is nearly 0. A: Yes; the claim is small and its size uncertain; quote the interval, not the point [FINAL_OPENING_READ reading 1].
- Q: Smallest detectable effect on E1? A: About 0.074 [T4, derived].
- Q: Why precision 0.6, recall 0.4? A: Half-cut layout absent from training, scuff streaks, and E1 labels are wider (predictions are about half the label width).
- Q: Ensemble? A: Final 5-model ensemble 0.487, no better than its members.

## 13. Quantitative IV: few-shot (50 s)
Say: "Can labelled cells of the new layout do better? E1 is split into 5 folds by image; each fold is predicted by a model trained on the pool plus the labelled E1 cells of the other folds. Zero-shot 0.488; with half of those images 0.692; with all 0.709. All minus zero-shot is +0.22, interval +0.10 to +0.35, confirmed. Largest on half-cut cells with scuff, +0.30; half-cut without scuff not detectable. These models also learn E1's wider labels."
- Q: Isn't this training on the test set? A: Each cell is predicted by a model that didn't see its fold; the zero-shot table was frozen first; after this, no zero-shot claim on E1 [t3b_verdict].
- Q: Just wider labels? A: Partly (1.43x wider), which is why relF1@2 decides; crack components found rise 0.400 to 0.666.
- Q: Half vs all? A: All minus half +0.017, not detectable: half the images give about the same gain.
- Q: Why 0.488 not 0.490? A: Zero-shot uses seeds 5 to 7 only.
- Q: Realistic for a new site? A: Maybe optimistic: folds are by image id, and nearby CSIR ids may share handling marks.

## 14. Qualitative I: EL-paper models (40 s)
Say: "Pool cells picked by a fixed rule: median, 25th percentile and worst of our baseline's gain over the three EL-paper models. On typical cells all four find the crack; Pratt's weighted loss draws it too wide. The worst row is a 77 px crack our seed 5 finds but most of our seeds miss: mean 0.17."
- Ours here = PF baseline on the same split as the paper rows.
- Q: Cherry-picked? A: Rule over 190 cells with at least 20 crack px. Honest detail: a first version with another rule was viewed before this rule was fixed [fig/QUAL_NOTES.md].

## 15. Qualitative II: E1 baseline vs final (45 s)
Say: "Same rule on E1's 32 crack cells. 90th percentile, a full cell: final traces more of the crack, 0.58 to 0.64. Median, a half-cut cell: both near perfect. 25th percentile is already a loss: a half-cut cell with a dark scuff streak, hard for both. Worst: a 55 px crack at a BMRK cell edge, missed by both. An illustration after the registered read; it decides nothing."
- Point: on at least a quarter of E1 crack cells the final scores lower per cell; the pooled gain comes from cells like the full-cell row.
- Grey = padding around half-cut cells.

## 16. Qualitative III: few-shot (40 s)
Say: "Zero-shot is the final model; few-shot adds labelled E1 cells of other folds; every map is out of fold. 90th percentile: zero-shot finds nothing on a scuff cell, few-shot finds the crack, 0.00 to 0.78. Median: another scuff cell, small gain. Easy cells don't change. Worst: few-shot drops a crack at a busbar, 0.70 to 0.00, in all 3 seeds."

## 17. Conclusion I: questioning the dataset (50 s)
Say: "(a) The same baseline predictions on four label versions: strict IoU from 0.233 to 0.414, relF1@2 only 0.82 to 0.85. (b) Method contrasts in strict IoU change with the labels: plain fine-tune minus baseline from +0.0015 to +0.0367, HRNet even changes sign. (c) In relF1@2 they move by at most 0.003. Plus: the label release alone moves strict IoU by +0.045; scuff was labelled crack in 8 cells of the original release; E1 labels are 1.5x wider; 24 modules sat in two folds, with no measurable inflation, fixed anyway; 11,938 unlabelled cells gave no detectable gain at full labels; no paper had a module-disjoint split. And label errors are a minority: they move no contrast by more than 0.003."
- Trap: not "the dataset is bad"; the problem is convention and splits, not mass errors [T20 r17 to r19].

## 18. Conclusion II + further discussion (40 s)
Say: "Measurement first: module-grouped splits, a tolerant crack metric, sealed reads. Two EL-paper models are 0.08 to 0.09 below a U-Net++ baseline. The best method gives a small confirmed gain on unseen modules, +0.043, low end near 0. Labelled target-layout cells give +0.22, a different comparison. Limits: E1 is 101 of 106 cells from one source; inactive is unresolved with 10 E1 cells; only gains above about 0.07 are detectable on E1; no half-cut cells in training. Next: a few labels per new layout; thermal imaging, which shows inactive area and hot spots, not thin cracks; severity."
- Q: Gains are small; is this a contribution? A: The protocol (splits, scoring code, rules) is released, and it shows which published differences survive noise; the measured lesson is that target-layout labels matter more than architecture.
- Q: Severity? A: Per-cell predicted inactive area, mean error 0.12 percentage points on the pool; no power-loss claim holds [doc 23 s7b].
- Q: What is released? A: Protocol, split lists, scoring code; not images, masks or weights [abstract].

## 19. Thank you / questions

## Rapid-fire extras
- Augmentation: label-safe only (exact flips, 90 degree rotations, brightness/contrast); blur and small rotations shift 1 to 2 px labels (crack AP on train images 0.929 to 0.587) [handbook 11 (d)].
- Rare-class sampling? Screen FAIL: crack -0.0085, false crack px 1.68x [T16a].
- Seeds: 2 to screen, 5 for a row; seeds 5 to 9 for the final.
- Hardware: 8 RTX A6000 (cv02) + 1 RTX PRO 4500 (gaint) [doc 23 s2].
- Unseen sources (hold out a whole source): baseline drops from 0.844 to 0.733 relF1@2 [doc 24 s5].
- Who ran the experiments: decide your wording in advance; keep it true and short.
