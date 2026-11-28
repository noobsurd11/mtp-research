# Scout `recipe`: architecture-agnostic training and inference recipes

Scope: weight averaging and relatives, flatness-seeking optimisers, fine-tuning schedules, distillation for dense prediction, TTA beyond D4, calibration and threshold choice, refinement, boundary/distance losses, precision-recall losses, long-training and augmentation recipes. Literature only; nothing trained, no server touched.

Overlap with the 12 Nov sweep was checked first: D18 (IoU/soft-label losses), D19 (long tail), D20 (small-object losses), D25 (medical pipelines), D26 (refinement), D31 (TTA). MASTER already holds SWAD (P039, in use), soups (P122), WiSE-FT (P123), DiWA (P211), EMA (P049), IMWA (P169), SAM (P142, RUN_NOW, never run), SAGM/DGSAM/Focal-SAM, LP-FT, surgical FT, ensemble KD (P014, RUN_NOW), canonical KD (P022), CascadePSP, SegRefiner, Lovasz, Unified Focal, Recall loss and cbDice. Those appear in `papers.tsv` with their pid for completeness, but the ranking favours NEW items.

## Tool conditions (affects coverage)
- Semantic Scholar was rate-limited for the whole session, so `search_snippets` failed (1 attempt) and S2-only hits are missing.
- arXiv search timed out on most queries. Results came mainly from OpenAlex, Scopus and ScienceDirect.
- `fetch_fulltext` timed out, but the arXiv copies were saved anyway. I read sections of Model Stock, MIRO, FAD, Lookaround and FMS2. Every other entry is **abstract only**: either the full abstract via `get_paper`, or the 200 to 300 character preview from search, marked "abstract preview" in the TSV.

## Queries run (59 `search_papers` + 1 `search_snippets` + 6 citation snowballs + about 25 `get_paper`)
1. weight averaging semantic segmentation generalization
2. sharpness-aware minimization semantic segmentation
3. model soups segmentation fine-tuned models averaging medical image
4. lookaround optimizer weight averaging
5. model ratatouille recycling diverse models out-of-distribution
6. stochastic weight averaging medical image segmentation
7. channel-wise knowledge distillation dense prediction
8. self-distillation semantic segmentation same architecture born-again
9. ensemble distillation medical image segmentation single model
10. Tversky loss focal Tversky lesion segmentation precision recall
11. F-measure loss optimizing F1 score directly segmentation
12. tolerance boundary F-measure loss edge detection crack thin structure
13. Hausdorff distance loss segmentation distance transform
14. test-time augmentation segmentation multi-scale learned aggregation uncertainty
15. linear probing then fine-tuning segmentation dense prediction LP-FT
16. Model Stock: all we need is just a few fine-tuned models
17. When do flat minima optimizers work? SWA SAM comparison
18. flatness-aware minimization domain generalization zeroth first order flatness
19. ASAM adaptive sharpness-aware minimization scale-invariant
20. sharpness-aware minimization medical image segmentation U-Net generalization
21. local temperature scaling calibration semantic segmentation
22. margin-based label smoothing calibration segmentation neighbor-aware
23. thresholding classifiers to maximize F1 score optimal threshold
24. test-time augmentation cell segmentation microscopy improves accuracy
25. aleatoric uncertainty estimation test time augmentation medical image segmentation
26. learning loss for test-time augmentation
27. Monte Carlo dropout test-time crack segmentation uncertainty
28. active boundary loss semantic segmentation
29. Boundary difference over union loss medical image segmentation
30. InverseForm boundary-aware segmentation loss
31. loss function comparison crack segmentation thin structure Dice focal Tversky Lovasz benchmark
32. layer-wise learning rate decay fine-tuning semantic segmentation pretrained encoder
33. transfer learning medical image segmentation which layers to fine-tune freezing encoder small data
34. data augmentation strategies small dataset segmentation systematic evaluation training schedule longer training
35. TrivialAugment RandAugment semantic segmentation automated augmentation
36. confidence calibration predictive uncertainty deep medical image segmentation ensembles Dice
37. uncertainty-guided refinement segmentation thin structure second stage
38. weight averaging segmentation domain shift unseen domain fundus prostate SWA ensemble
39. knowledge distillation retinal vessel segmentation thin structures teacher student
40. knowledge distillation crack segmentation
41. diffusion model segmentation refinement crack mask 2025
42. Diverse weight averaging out-of-distribution DiWA segmentation
43. hierarchical multi-scale attention semantic segmentation inference scales
44. road extraction relaxed precision recall tolerance loss training buffer
45. Lovasz hinge loss thin structure crack vessel IoU surrogate (0 results)
46. AdamW versus SGD fine-tuning convolutional networks dense prediction comparison generalization
47. (snippets) loss tolerating small spatial misalignment of thin-structure labels (failed: S2 rate limit)
48. ODS OIS optimal threshold crack detection evaluation tolerance
49. distance transform regression auxiliary loss crack segmentation skeleton distance map
50. The devil is in the margins: label smoothing under class imbalance calibration segmentation
51. Tversky loss function image segmentation fully convolutional deep networks
52. masked generative distillation logit standardization knowledge distillation segmentation
53. early weight averaging high learning rates trainable weight averaging
54. stochastic weight averaging crack segmentation
55. sharpness-aware minimization domain generalization semantic segmentation Cityscapes dense
56. nnU-Net data augmentation ablation training epochs small dataset segmentation what matters
57. SegFix model-agnostic boundary refinement OR boundary patch refinement crack thin
58. snapshot ensembles cyclic learning rate checkpoint ensemble segmentation
59. distilling test-time augmentation ensemble into single segmentation network consistency
60. Friendly sharpness-aware minimization GSAM surrogate gap fine-tuning pretrained

Citation snowballing (`get_citations`) was run on SWAD (40 citing papers shown), Lookaround (15), Model Stock (24), MIRO (25), CWD (25) and boundary loss (25). It added EoA, MIRO, Model Stock, Ratatouille, Fisher SAM, DaWin, Structural and Statistical Texture KD, Masked Generative Distillation, Loss odyssey and the Distance Map Loss Penalty. Most citers of the weight-merging papers are LLM-merging work, which I skipped.

## Counts
- Listings shown to me: about 640 across all queries and snowballs (lists capped at 5 to 40 each). After removing duplicates and off-topic hits, I screened about 450 distinct papers.
- Kept in `papers.tsv`: **95** (74 NEW, 21 already in MASTER).
- By family: weight averaging 16, flatness 12, distillation 12, precision-recall losses 10, calibration/threshold 9, boundary/distance losses 9, fine-tuning schedule 7, TTA 7, refinement 7, long training/augmentation 6.
- NEW or pid was checked against MASTER by DOI or arXiv id and by title prefix, with a script. There were no mismatches.

## What our situation implies for this family
From the context and thesis: E1 recall is the weak point (relR 0.416 vs relP 0.600). A post-hoc crack bias raises recall but trips the width guard and the false-pixels-on-crack-free-cells guard (PF2E, SKR2E). The 5-seed PF ensemble gave E1 inactive +0.21 (PASS) and E1 crack +0.035 (n.d.). Plain fine-tuning erases pretrained deep layers, which is why PF exists. So the useful recipes are ones that:
- keep the ensemble's gain in one model,
- keep pretrained features without a hard freeze,
- generalise across sources, or
- move recall without widening cracks.

Nearly all evidence in this family comes from classification domain generalisation (DomainBed) or blob-like medical segmentation. **No paper I found tests a weight-averaging, flatness or distillation recipe on 1 to 2 px structures under a tolerant metric.** Every top-10 item is therefore a transfer bet, and its cost is the main reason to rank it.

## Top 10 (NEW only, ranked by expected value per GPU-hour)

1. **Model Stock** (doi:10.1007/978-3-031-72784-9_12, ECCV 2024; method section read). Merges N fine-tuned models layer by layer toward the pretrained weights. The ratio t = N cos(theta) / (1 + (N - 1) cos(theta)) comes from the angle between the fine-tuned weights, so nothing is tuned. With only 2 CLIP fine-tunes it beats Model Soup on ImageNet and five OOD sets.
   - *Mapping:* we already have 5 seeds of PF and C2 from one ImageNet init. A post-hoc merge, with BN statistics recomputed and a plain average for the decoder, which has no pretrained anchor, gives one model at single-model cost. It may keep part of the PF2E gain on E1 inactive, half-cut cells and crack recall.
   - *Cost:* minutes of CPU/GPU. Uniform soup (P122) is the control.
   - *Risk:* CNN with BN, not ViT. The PF freeze may leave the seeds nearly collinear, which would leave little to gain.
2. **MIRO, MI regularisation with pretrained features** (doi:10.1007/978-3-031-20050-2_26, ECCV 2022; full text read). Keeps intermediate features informative about a frozen pretrained copy.
   - *Evidence:* DomainBed RN50 average 65.9 vs ERM 64.2, and **MIRO+SWAD 68.1 vs ERM+SWAD 66.9** (TerraIncognita 52.9 vs 50.0). This is the one recipe here shown to add on top of SWAD.
   - *Mapping:* a soft, always-on version of the PF finding that plain fine-tuning erases pretrained deep layers. It applies to the HRNet-W18 stage outputs. It targets recall on unseen modules through better-preserved generic features.
   - *Cost:* new loss, about 1.3x step time.
   - *Risk:* the ImageNet anchor may be weak for grey-scale EL. The weight lambda needs CV tuning.
3. **Ensemble-to-single distillation with CWD** (doi:10.1109/iccv48922.2021.00526, ICCV 2021; abstract). CWD normalises each channel spatially and matches teacher and student with KL. Abstract: PSPNet-R18 +5.81 mIoU on Cityscapes. Pair it with P014 (Noothout, already RUN_NOW), which shows seed ensembles distil into one CNN without loss.
   - *Mapping:* the teacher is PF2E or a C2 5-seed ensemble with D4. The per-channel spatial softmax concentrates the loss on the most salient crack and inactive locations, which suits 0.19%-frequency classes. It is the trained route to the same goal as #1.
   - *Cost:* about 1.5x training (teacher logits can be cached).
   - *Risk:* reported gains are for small students. Same-size distillation gains are smaller. Teacher errors on E1 transfer.
4. **Ensemble of Averages (EoA)** (doi:10.52202/068431-0601, NeurIPS 2022; abstract). Ensemble the moving-average models of independent runs. DomainBed RN50 68.0% vs ERM about 64%. Averaging also improves the in-domain/out-of-domain rank correlation used for model selection.
   - *Mapping:* PF2E ensembled plain PF models. Ensembling the 5 C2 (SWAD) seeds is EoA and needs no training. The rank-correlation result also bears on our noisy CV-to-E1 selection.
   - *Cost:* inference only (5 x 8 passes).
   - *Risk:* deployment cost. It may only re-measure the n.d. ensemble effect on E1 crack.
5. **Boundary loss (signed-distance-weighted)** (doi:10.1016/j.media.2020.101851, MedIA 2021; abstract). A distance-on-contours loss written as a regional integral of a signed distance map, added to a regional loss. Abstract: gains and more stable training on highly unbalanced problems.
   - *Mapping:* for a 1 to 2 px crack, each predicted crack pixel costs in proportion to its distance from the nearest GT crack. A 1 to 2 px offset is nearly free, as in relF1@2, while false cracks on gridlines or on crack-free cells cost the most (guard G2b). This is the only loss found whose geometry matches the tolerant metric.
   - *Cost:* new loss term with precomputed distance maps.
   - *Risk:* built for blob boundaries. It gives a weak recall signal on its own. Pair it with the existing CE/Dice and ramp it in.
6. **Lookaround optimizer** (doi:10.52202/075280-1247, NeurIPS 2023; experiments section read). Trains k copies from a common point, each on a different augmentation, and averages them every few steps. It beats SWA-type baselines on CIFAR and ImageNet (CNNs and ViTs, scratch and fine-tuning).
   - *Mapping:* the k augmentations can be the 8 D4 transforms we already use at test time. Training then directly seeks D4-consistent flat weights, and SWAD can still average the trajectory.
   - *Cost:* k-fold compute per step (fits the 8 A6000s).
   - *Risk:* no dense-prediction evidence. It may overlap with SWAD.
7. **FAD, flatness-aware minimisation for DG** (doi:10.1109/iccv51070.2023.00479, ICCV 2023; results section read). Joint zeroth- and first-order flatness. Averaged over 6 DG sets: FAD 67.6, GAM 66.6, SAM 66.4, AdamW 66.0, Adam 65.6.
   - *Mapping:* our unseen modules and the CSIR shift are DG problems. Run it together with the never-run P142 (SAM) and ASAM (arxiv:2102.11600, scale-invariant, safer with BN).
   - *Cost:* optimizer swap, about 2 to 3x step cost.
   - *Risk:* I did not read the SWAD-combination table. The text says AdamW was the best base optimizer with SWAD, so the gain on top of SWAD is uncertain. Classification only.
8. **Model Ratatouille** (arxiv:2212.10445; abstract). Fine-tune one pretrained model on auxiliary tasks, use those weights as inits for target fine-tunes, then average all target fine-tunes. Abstract: improves the DomainBed state of the art.
   - *Mapping:* we own labelled auxiliary crack/defect sets (E-SCDD, UCF-EL, pavement-crack sets). These give real diversity for averaging, aimed at recall on unseen modules, where seed-only diversity is small.
   - *Cost:* about 2x a 5-seed run.
   - *Risk:* heads must be re-initialised. UCF-EL pretraining was tested before as an init, but not as a recycled average.
9. **Focal Tversky / Tversky loss** (doi:10.1109/isbi.2019.8759329; doi:10.1007/978-3-319-67389-9_44; abstracts).
   - *Tversky* (MS lesions): imbalance pushes models to high precision and low recall; Tversky improves F2, Dice and PR-AUC.
   - *Focal Tversky:* better precision/recall trade-off than Dice on small lesions, +25.7% BUS and +3.6% ISIC vs U-Net (confounded with an improved attention U-Net).
   - *Mapping:* E1 recall 0.42 vs precision 0.60. A train-time FN weight on the crack channel moves the learned operating point rather than adding a post-hoc bias.
   - *Cost:* loss only.
   - *Risk:* the post-hoc bias already showed that recall bought this way widens cracks and trips guards. Tversky may simply do the same at train time. Screen on the width and crack-free-cell guards first.
10. **Learned multi-scale inference (HMSA)** (arxiv:2005.10821; abstract). Learned attention over predictions from several input scales instead of averaging them. Moshkov et al. (doi:10.1038/s41598-020-61808-3) also show simple TTA with the right merge improves U-Net nuclei segmentation.
    - *Mapping:* upscaled views (1.5x, 2x) may recover faint 1 to 2 px cracks on low-contrast CSIR cells. A learned per-pixel scale weight avoids widening cracks everywhere.
    - *Cost:* the plain multi-scale TTA probe is config-only. A learned head is small.
    - *Risk:* downscaling destroys thin cracks. 2x input training (Track M) was already tried, so the TTA-only version is the new part. 4x inference cost at 2x scale.

Near misses (NEW, fit 3):
- **How to Fine-Tune Vision Models with SGD** (arxiv:2211.09359): freezing only the stem/embedding closes the AdamW vs SGD gap under shift. It gives a cheap PF ablation.
- **Karimi et al. 2021** (doi:10.1016/j.artmed.2021.102078): feature reuse can be larger in deeper layers, and frozen-encoder FCNs are accurate. Supports deep-stage freezing or layer-wise LR.
- **ASAM** (arxiv:2102.11600): see #7.
- **Local Temperature Scaling** (doi:10.1109/iccv48922.2021.00681): per-pixel temperature instead of a global crack bias.
- **Lipton et al. 2014** (arxiv:1402.1892): for calibrated outputs, the F1-optimal threshold is half the optimal F1. That predicts different optimal biases in-domain (relF1 about 0.87) and on E1 (about 0.49), which is consistent with CV-fitted biases not transferring.

## Suggested order (cheapest decisive first)
1. #1 Model Stock and uniform soup, plus #4 EoA. Both are post-hoc on existing C2/PF seeds, scored on CV5 and E1-as-is (keeping in mind E1 is now training data for the few-shot track, so zero-shot claims need the new unseen set).
2. #10 plain multi-scale TTA probe. Inference only.
3. #5 boundary loss and #9 focal Tversky as 2-seed loss screens, with the width and crack-free guards read first.
4. #2 MIRO+SWAD and #7 FAD/ASAM (with P142 SAM): optimizer/regulariser screens.
5. #3 CWD distillation of the best ensemble, then #6 Lookaround and #8 Ratatouille (most compute).

## NOT_FOUND / gaps
- **"When do flat minima optimizers work?" (Kaddour et al., NeurIPS 2022, SWA vs SAM across tasks).** Searched the title words; got SWAD, Fisher SAM and the federated flat-minima paper, but not this paper.
- **GSAM-for-segmentation, SAM+SWA combination studies on dense prediction.** None found. The only thin-structure SAM evidence is a DRIVE study in Sensors (doi:10.3390/s24134267), which is weak.
- **Trainable weight averaging (TWA), PAPA (population parameter averaging), Hierarchical weight averaging.** Searched "early weight averaging high learning rates trainable weight averaging". Not returned.
- **A training loss for thin structures with an explicit pixel tolerance (relaxed or buffered precision/recall, as used in road-extraction evaluation).** No paper found that trains with a distance-tolerant precision/recall loss matching relF1@2. Searched queries 11, 12, 44, 47 and 49. A tolerant soft-F1 (sigmoidF1 on a 2 px band) would be our own construction.
- **Minimum Strip Cuts** (doi:10.1016/j.aei.2025.103249). Found again, still no abstract in any index (same gap as D26).
- **Layer-wise LR decay studies for CNN segmentation fine-tuning.** Query 32 returned only ViT/transformer segmentation papers. No direct study found.
- **Logit Standardization in KD (CVPR 2024)** and **Masked Generative Distillation abstract.** MGD was found by snowball but has no abstract in the index. Logit standardization was not returned by query 52.
