# F05: institutional PDFs (read 10 Oct 2026)

Source: `literature/pdfs_inst/*/` (pdftotext, sections grepped; read scope per row). Pratt 2021 was read by the parent and is not repeated here.

## Compact table

| Paper | Data (public?) | Labels / budget | Method (one line) | Metric convention | Headline | Rare-class handling | Flaws | Read |
|---|---|---|---|---|---|---|---|---|
| Jha 2025 EAAI (PV-S3, journal) | UCF-EL + "CSB" = Pratt's sets S1 593 / S2 2109 / S3 2282 imgs | 20% vs 100% | DeepLabv3+ MT + SemiCE, λ = 1.5, t_pos 0.2 / t_neg 0.4 | mIoU "averaged across all classes"; background treatment not stated | UCF SSL-20 67.0 vs SL-20 **8.76** vs FSL 70.84 mIoU | SemiCE thresholds tuned on results | none of our measured issues fixed (see check 1) | sections |
| Wan 2026 MedIA (DCF) | ACDC, PROMISE12, Hippocampus, ATLAS, BraTS19, Pancreas | 5/10/20% | two nets; evidential Guidance Mask routes pixels: confident-agree → convergence, uncertain/conflict → divergent exploration | Dice, 95HD (medical) | SOTA on 6 sets; also fine-tunes MedSAM | none (few-class sets; no imbalance analysis) | — | abstract + method grep |
| Hu 2026 PR (CaPro) | LA, BraTS19, ACDC | low % | class-aware **subclass prototypes** from reliable regions (one global threshold u_th = 0.4) + cross-view contrast | Dice, 95HD | SOTA on 3 sets | prototypes per class, not per-class thresholds; no rare-class study | — | abstract + grep |
| Liu 2025 Solar Energy | few-shot PVEL-AD (5 classes, boxes) | 3/5/10-shot, 10 random draws | Faster R-CNN FSOD + contrastive loss + frozen "knowledge compensation" branch | box mAP (base / novel) | novel-class mAP ~19–26% (FsDet); all-class ~78–85% | rare classes as few-shot novel classes (star_crack 38 AP for TFA) | detection only; 10 draws is good practice | abstract + results grep |
| Lin 2026 EES (EI-AE, CC BY-NC) | PVEL-AD; **new pixel masks**: 30 "all-defect" masks + 438 masks for 4 functional types (crack, finger, scratch, star crack); in SI | normal-only (unsup) / 1–142-shot | iterative autoencoder reconstruction; few-shot U-Net head | P-AUROC, P-AP, P-F1, AUPRO | crack (non-star) unsup: **P-AP 0.14, P-F1 0.21**; few-shot: P-AP 0.34, P-F1 0.42 | none | single test set, no seeds | sections |
| Duan 2025 Energy (CAAK-Net) | **PVEL-S** (Kaggle): 1,200 poly cells from PVEL-AD, binary defect masks, 840 / 360 | 100% | K-Net + CBAM/ARM/ASPP (MMSeg) | 2-class mIoU incl. background | mIoU ~96.1% | none (all defects → one class) | offline augmentation; background-dominated metric; single split | abstract + setup |
| Gil 2025 ICEIC | private modules | module labels + ~5% cell labels | MIL (max cell probability vs module label) + SSL with cell labels | classification accuracy / F1 | beats single-level labels | none | 4-page conference paper | full (short) |
| Crack SSL EAAI 2024 (Zhejiang) | new civil-crack set (cracks ~5% of pixels) | 10–100%; 20% chosen | MC-Net-style mutual consistency + boundary (distance) loss | pixel P/R/F1/IoU, no tolerance | 20%: F1 0.823, IoU 0.689 | boundary loss vs imbalance | hyperparameters (LR, batch, T, label %) apparently picked on reported results; one split 8:1:1 | abstract + setup |
| Lv 2026 Solar Energy (UniDisc) | ELAD industrial multi-line benchmark | normal-only | multi-class UAD with feature decorrelation and channel gating | image and pixel AUROC / AP / F1 / AUPRO | +1.8% image AUROC | n/a | no speed numbers given | abstract |
| Pratt 2025 ICTAS | 680 fielded modules, 48,960 cells (CSIR) | 24 new "brightening" samples added | DeepLabV3, **29 classes** | regression of mean defect share to fill factor | brightening explains r² = 0.42 of FF | n/a | correlation only | abstract + grep |
| Chen 2022 PVSC (LBNL, PV-Vision) | 1,272 / 206 / 359 cells, open-source | 100% | UNet: crack, cross crack, busbar, dark area; worst-case inactive area from cracks | F1 / IoU | F1 0.875, IoU 0.782; **0.18 s/cell**, 0.72 s/module cropping | n/a | 1-page abstract | abstract |
| Jost 2025 PVSC | Sandia cells + IV curves | none | VAE latent space → power-loss model | — | — | — | abstract only | abstract |
| Haase 2018 JPV | lab laminates, 4-line bending | — | DIC crack-width measurement | — | single-crack width **≈ 3.4 µm** under load (DIC, ±8 µm uncertainty) | — | — | sections |
| Gabor 2022 JPV | hail-damaged fleet | — | EL grading (MBJ-based) | grade classes A–D | crack "critical" if > 1% cell area isolated, "very critical" > 20% | — | — | sections |
| Su 2021 TII (CAN) / Su 2023 TII (PVEL-AD) | 36,543 poly cells, 1024², 11,351 normal, 21,044 with 37,380 boxes, 4,148 category-only | boxes | Faster R-CNN + attention; YOLOv5-s baseline 111 FPS | box AP50 | — | "open-world" categories | boxes made with model-assisted F-labelImg by experts | sections |
| Otamendi 2021 Solar Energy | ELPV + private TecnaliaPR | image labels | Faster R-CNN cell detection → EfficientNet classification → weakly supervised AE segmentation | — | — | — | — | abstract |

## Check 1: did the PV-S3 journal version fix what we measured? **No.**
- Supervised baseline unchanged: "training process is carried out for 30 epochs", SGD 1e-3, crop 224. SL-20 is still reported at **8.76% mIoU** (Table 1).
- The failure is still blamed on the data rather than the schedule: "model is not able to learn the features accurately".
- Background treatment is never stated. mIoU is defined as "averaged across all classes", with no mention of excluding background or of `ignore_index`. The dataset note says healthy images get "pixel index same as the background".
- No train/test split description beyond "20% of the labeled data and 80% of the unlabeled data from the training set". Nothing addresses the test-in-train leakage we found in the released lists.
- Table 6 still sets their numbers beside Pratt 2023's per-image-median numbers (Deeplabv3+ 28.00), and calls it "a fair comparison with Pratt et al. (2023)".
- New: "CSB" subsets S2 (2,109 images, 15 classes) and S3 (2,282 images, 16 classes). These look like larger Pratt-group label releases. Check before claiming BenchmarkEL is only 582 images.

## Check 2: does MedIA 2026 or CaPro combine region routing with class awareness? **No; the gap stays open, with a caveat.**
- **DCF (MedIA 2026)** is the closest ALHVR-style router.
  - Its Guidance Mask splits pixels into confident-agree, uncertain-agree and confident-disagree, and treats each differently.
  - Its "class awareness" is a peer confusion matrix between classes, used to push features apart in uncertain regions. It is not imbalance handling.
  - No per-class thresholds, no rare-class weighting; datasets have 1–3 foreground classes.
- **CaPro** has class-aware (subclass) prototypes built from reliable regions with one global reliability threshold.
  - No routing of unreliable regions; no imbalance study; few-class datasets.
- **Caveat:** DCF's three-way split plus evidential uncertainty is a stronger router than ALHVR's, and it is the 2026 baseline a reviewer would ask for. Our claim must be narrowed to "routing whose thresholds and target construction are per class / rarity-aware, evaluated on rare thin classes".

## Check 3: EL rare / unsupervised / few-shot / crack SSL: competitors or baselines?
- **Liu 2025:** box-level few-shot detection on PVEL-AD; novel-class mAP ~20–26%. It is evidence that rare EL classes are hard even as boxes. Related work only, not a segmentation competitor. Its protocol of 10 random draws is a good precedent for our split-variance argument.
- **Lin 2026 (EI-AE):** the strongest relevant EL result.
  - Normal-only reconstruction gives crack P-AP **0.14** (P-F1 0.21) on PVEL-AD. Few-shot raises it to P-AP 0.34.
  - This measures how weak anomaly priors are for thin cracks, consistent with our "anomaly prior may miss thin cracks" risk.
  - Its 438 pixel masks on PVEL-AD (in SI) are a new **public pixel-level EL test set** from a different source. Worth fetching from the SI as an out-of-distribution evaluation for crack.
  - Use it as a baseline for any "unlabelled normal cells" direction, not as a competitor.
- **Duan 2025:** binary defect segmentation on PVEL-S, mIoU ~96% including background, which is uninformative.
  - Its value is the dataset: **PVEL-S (1,200 pixel-masked cells, Kaggle)**, another public pixel-level EL source.
  - Not a competitor.
- **Gil 2025:** MIL with module labels plus a few cell labels; classification only. A weak-supervision precedent (module → cell), not a segmentation competitor.
- **Crack SSL EAAI 2024:** civil cracks (~5% of pixels, far thicker than EL cracks).
  - MC-Net-style consistency plus boundary loss; no tolerance metric; hyperparameters apparently chosen on reported results.
  - At most a generic baseline idea (two-decoder consistency plus distance loss). Not EL evidence.

## Check 4: constraints for thesis parts 2–3
- **Throughput:**
  - Chen 2022 (LBNL): UNet at 0.18 s/cell, 0.72 s/module cropping.
  - PVEL-AD: YOLOv5-s at 111 FPS on a 3090 (1024² cells).
  - Lv 2026 gives no speed. A 60–72-cell module at line speed needs well under 1 s per module for all cells, so a ~5M-parameter segmenter is in budget; a ViT-L teacher is not.
- **Severity:**
  - Gabor 2022 (MBJ-based): a crack is "critical" when > 1% of cell area is isolated and "very critical" when > 20%; panel classes A–D come from counts.
  - Chen 2022: crack lines → worst-case (maximum) inactive area.
  - Pratt 2025: mean defect share per module vs fill factor (brightening, r² = 0.42).
  - Severity therefore needs **crack topology and connectivity** (does the crack isolate an area?) and inactive area, not pixel-exact crack width. This supports skeleton/connectivity metrics over strict IoU.
- **Physical crack width:** about **3.4 µm** under load (Haase 2018, DIC). At 512 px per ~156 mm cell, one pixel is ~300 µm.
  - The ~4 px dark line in EL is therefore electrical/optical spread around a sub-pixel crack, not the crack itself.
  - Any annotation width (1.75 px or 3 px) is a convention. This strengthens the case for tolerance-aware losses and metrics.
- **PVEL-AD label protocol:**
  - boxes drawn by experts with model-assisted "F-labelImg" (detector proposals, then human correction);
  - 1024² polycrystalline cells, 36,543 images: 11,351 normal, 21,044 with boxes (37,380 boxes), 4,148 with category labels only.
  - Model-assisted boxes may carry detector bias.

## Direction-ranking implications
1. **Public pixel-level EL data is larger than we assumed:**
   - PVEL-S (1,200, binary);
   - Lin 2026's 438 four-class masks on PVEL-AD;
   - LBNL PV-Vision (1,272 / 206 / 359, crack + dark area);
   - Pratt-group S2/S3 (~2.1–2.3k) and the 29-class model;
   - E-SCDD (F03).
   Cross-dataset evaluation and supervised transfer move up; a "held-out source" test for crack becomes feasible.
2. **Anomaly priors from normal-only cells are weak for thin cracks** (EI-AE crack P-AP 0.14). Keep the anomaly-prior card low, or limit it to region classes.
3. **Severity is connectivity / area-based:** crack connectivity and inactive area matter more than pixel-exact crack width. This supports skeleton/connectivity-aware losses and metrics in part 1.
4. **The novelty gap holds, but DCF (MedIA 2026) is now the routing baseline to beat.**
