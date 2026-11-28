# D03: Forward-citation snowball of the core EL dataset papers

Scout: D03. Date: 12 Nov 2026. Literature only, no servers, no test or E1 predictions read.
Labels: R = what a paper measured, E = what our files measured (from BRIEF), S = my judgement.

## 1. Core papers resolved (all via get_paper)

| Core paper | id | Citations (index) | Citers listed and scanned |
|---|---|---|---|
| Pratt 2021, U-net EL defect quantification | doi:10.1016/j.renene.2021.06.086 | 144 | 100 |
| Pratt 2023, BenchmarkEL | doi:10.1016/j.sasc.2023.200048 | 65 | 57 |
| Fioresi 2022, UCF-EL | doi:10.1109/jphotov.2021.3131059 | 112 | 100 |
| Hanifi 2025, E-SCDD / PV-DDPM | arxiv:2511.09604 | 0 | 0 |
| Su 2023, PVEL-AD | doi:10.1109/tii.2022.3162846 | 268 | 100 (mostly YOLO box detectors) |
| Deitsch 2019, ELPV | doi:10.1016/j.solener.2019.02.067 | 611 | 100 (mostly classification) |
| Sanghi 2026, MultiSolSegment | doi:10.1016/j.solener.2026.114469 (arXiv 2603.13337) | 1 | 1 |
| Jha 2025, PV-S3 | doi:10.1016/j.engappai.2025.111790 (arXiv 2404.13693) | 33 | 32 |
| Torpey 2024, pretraining paradigms | arxiv:2402.17611 | 1 | 1 (not EL) |
| Extra seed: Chen 2023, PV-Vision crack seg | doi:10.1109/jphotov.2023.3249970 | 54 | 54 |

Snowball also: similar_papers on STC-Net + MultiSolSegment + E-SCDD.

## 2. Queries run

get_citations (10): the 9 core papers above plus Chen 2023. One retry on PV-S3 after a rate limit.
similar_papers (1): [arxiv:2608.01714, doi:10.1016/j.solener.2026.114469, arxiv:2511.09604].
search_papers (13):
1. Pratt defect detection and quantification EL U-net (no year filter, to find the core paper)
2. benchmark dataset EL solar cell semantic segmentation Pratt (2022+)
3. electroluminescence solar cell defect semantic segmentation (2025+)
4. photovoltaic crack segmentation electroluminescence thin crack (2023+)
5. segment anything electroluminescence photovoltaic defect segmentation (2023+)
6. electroluminescence defect annotation noise label inconsistency (2021+)
7. photovoltaic EL domain generalization unseen modules cross-dataset (2022+)
8. diffusion model synthetic EL defect images mask-conditioned (2024+)
9. half-cut solar cell electroluminescence crack detection (2021+)
10. PV cell defect segmentation network PVEL-S PSCDE (2023+)
11. weakly supervised segmentation EL cracks image-level labels (2020+)
12. inactive area dark region crack EL power loss severity (2022+)
13. solar cell defect segmentation transformer mamba EL (2025+)
search_snippets (4 attempts): all failed, Semantic Scholar keyless pool rate-limited all session. No snippet evidence used.
read_paper (no new downloads; 3 papers were already in the library): MultiSolSegment (method, results), E-SCDD (dataset, method, code), STC-Net (method), Torpey (setup, crack analysis).
WebSearch (8): PV-Vision repo, pv-ddpm repo, MultiSolSegment code, Hijjawi code, 2026 EL + foundation-model work, SAM domain-knowledge paper, GDI code, DSDINet repo.

## 3. Selected papers

Scores follow the brief's rubric. "score" = value for raising our numbers. "bench" = value for the benchmark vision.

| # | id | Year | Venue | Code | Mechanism (one idea) | Adaptation to our data | score | bench |
|---|---|---|---|---|---|---|---|---|
| 1 | doi:10.1016/j.solener.2026.114469 (arXiv 2603.13337) MultiSolSegment | 2026 | Solar Energy | dataset on DuraMAT (DOI 10.21948/2587738); code unverified | Per-channel sigmoid multi-label U-Net so a pixel can be crack and busbar (or crack and dark) at once | Keep 24-class softmax; add 2 sigmoid channels (crack, inactive). Crack target keeps the 20% of crack pixels that the single-label masks hand to inactive. Threshold per channel on val | 70 | 75 |
| 2 | arxiv:2511.09604 E-SCDD / PV-DDPM | 2025 | arXiv | https://github.com/sntubix/pv-ddpm | Mask-conditioned DDPM that generates EL cells (mono, multi, half-cut multi, IBC) from feature/defect masks | Train on our 478 train cells only (E-SCDD H36/F51 are our val, so exclude them). Generate half-cut multi cells carrying real train crack and inactive masks to attack E1 (0 half-cut in train) and the 42-cell inactive shortage | 66 | 70 |
| 3 | doi:10.1109/jphotov.2023.3249970 PV-Vision crack seg + crack-isolated area (also doi:10.1109/pvsc48317.2022.9938503) | 2023 | IEEE JPV | https://github.com/hackingmaterials/pv-vision | From crack + busbar masks compute the area cut off from every busbar (worst-case inactive area) | Use our predicted crack + ribbon/busbar classes to build an "isolated region" map; feed it as an input channel to a second-stage inactive head (inactive touches a crack in 99% of cases). Also a severity output. Public crack set (DuraMAT DOI 10.21948/1871275) for cross-dataset tests | 60 | 80 |
| 4 | doi:10.1109/infinitys69204.2026.11666283 Fracture-informed CNN-Transformer ensemble | 2026 | INFINITYS (conf.) | none found | Small refinement module predicts residual logits from probability, uncertainty and Sobel edges, fused with a U-Net++ branch | Train a tiny refiner on out-of-fold 5-seed ensemble probs + entropy + Sobel + image, using the existing module-grouped 5-fold roots so it never sees in-fold predictions | 50 | 25 |
| 5 | doi:10.1016/j.solener.2026.114943 (arXiv 2608.12725) GDI | 2026 | Solar Energy | unverified (HF page names a repo) | LaMa inpainting erases selected defects using seg masks to make single-defect and defect-free twins | Erase cracks (and separately inactive) from the 209 crack train cells to get paired clean twins; train on originals + twins to cut decoy false positives and decouple crack from inactive | 50 | 35 |
| 6 | arxiv:2001.11248 Mayr, weakly supervised crack seg (normalized Lp) | 2020 | arXiv | none verified | Crack segmentation from image-level labels via normalized-Lp pooling of activation maps | Add an image-level crack head (Lp-pooled crack logits) trained on the 2,624 ELPV cells, the same source as our weak BMRK cells. Remove every ELPV cell that appears in BMRK val/test first | 45 | 30 |
| 7 | arxiv:2608.01714 STC-Net | 2026 | arXiv (MERCon) | none found | Fixed Sobel edge and FFT high-pass "spectral" prior pyramids injected into decoder skips, plus coarse / edge / topology auxiliary heads | Cheapest form: 2 extra input channels (Sobel magnitude, radial high-pass) on 1-ch 512 px input. Full form: prior pyramids into U-Net++ skips; edge-head target = 3 px dilated crack label to absorb 1-2 px jitter | 45 | 40 |
| 8 | doi:10.1109/tii.2023.3275705 RERN + PSCDE | 2023 | IEEE TII | none found | Crack as edge detection, scored by ODS F-measure at a distance tolerance; bidirectional strip attention (BSRA) for long thin structures | Insert BSRA (directional strip pooling) into U-Net++ decoder blocks; train crack with class-balanced edge BCE. For the benchmark, report ODS/OIS at maxDist = 2 px next to relF1@2 | 45 | 65 |
| 9 | doi:10.1016/j.solener.2025.114083 Hijjawi instance-seg benchmark | 2025 | Solar Energy | stated public, URL unverified | Mask classification (Mask2Former) and ConvNeXt-V2 backbones beat Mask R-CNN on UCF-EL | Mask2Former semantic head with ConvNeXt-V2 or Swin backbone, 1-ch replicated, 512 px, 24 classes. Mask-classification decoders were never tried here; blobby inactive and rare classes are the target | 45 | 75 |
| 10 | arxiv:2402.17611 Torpey | 2024 | arXiv | none found | COCO-supervised segmentation pretraining and ImageNet SimCLR gave the best crack IoU (p <= 0.0001); block-centred per-image IoU + Tukey HSD | Initialise the whole DeepLabV3 (encoder and decoder) from torchvision COCO weights, 1-ch input by summing RGB filters, fine-tune under PF. Adopt block-centred IoU statistics in the benchmark | 42 | 80 |
| 11 | doi:10.1109/tii.2023.3327572 SSN | 2023 | IEEE TII | none found | Background style suppression by channel-statistics matching, learned at train time without target data | Insert BSS (instance-statistics alignment / style mixing across our 5 sources) into ResNet layer1-2 of the PF model, aimed at E1 contrast and scuff shift | 42 | 30 |
| 12 | doi:10.1109/tii.2022.3228680 (arXiv 2212.07768) Otamendi annotation framework | 2022 | IEEE TII | none found | Data-driven pipeline to build "golden standard" EL anomaly masks with 60% less annotation cost | Label refinement without hand labelling: model ensemble + ridge snapping proposes corrected crack masks for the 24 flagged train cells; human-free acceptance rule | 35 | 50 |
| 13 | doi:10.1039/d5ee05042a EI-AE | 2025 | Energy Environ. Sci. | none found | Iterative autoencoder trained on normal EL cells gives unsupervised pixel anomaly maps; few-shot extension with a few masks | Train on pool cells the house model calls crack-free (incl. 1,152 multi half-cells); feed the anomaly map as an extra channel to target E1 cracks the model "does not see" (p < 0.001) | 35 | 35 |
| 14 | doi:10.3390/su182010677 Frozen DINOv2 structure-aware AD | 2026 | Sustainability | none found | Per-patch-position prototypes of normal cells on frozen DINOv2 ViT-S/14 | Position-conditioned prototypes per cell type (full / half-cut) from pool; anomaly map as auxiliary channel. Its reported failure to transfer calibration PVEL-AD to ELPV supports an unseen-source test in the benchmark | 32 | 45 |
| 15 | doi:10.1016/j.engappai.2025.111790 PV-S3 | 2025 | EAAI | https://github.com/abj247/PV-S3 | Semi-supervised seg with a Semi Cross-Entropy loss for class imbalance | Run official code under our split as a benchmark baseline; test the Semi-CE loss alone in the house model | 30 | 85 |
| 16 | doi:10.1007/978-981-96-8892-0_4 Hanifi multi-class seg baseline | 2025 | LNCS | https://github.com/sntubix/pv-defect-segmentation | Six U-Net/SegNet x VGG16/MobileNet/ResNet50 baselines with custom class weights on the 29-class SCDD | Run as the reference baseline from the label authors under our fixed protocol | 25 | 70 |
| 17 | doi:10.1109/ictas64866.2025.11155421 Pratt power-loss correlation | 2025 | ICTAS | none | 29-class seg on 48,960 cells of 680 CSIR modules; module-mean defect fraction regressed on fill factor (r2 = 0.42) | Template for a severity step: aggregate our class fractions per module and regress on electrical data, if WattCycle or CSIR data allow | 15 | 70 |
| 18 | doi:10.1051/epjpv/2024039 Jaeckel EL nomenclature | 2024 | EPJ PV | n/a | Industry/lab taxonomy of crack modes and EL observations, with a risk-based classification proposal | Map our 12 defect classes and the crack-mode / inactive-fraction severity bands onto this taxonomy so the benchmark's severity labels are standard | 8 | 65 |

### Evidence notes (R)
- MultiSolSegment (R): 4 sigmoid channels, BCE, 2,340 augmented images; overall IoU 0.384, Dice 0.503 averaged over classes; crack count per image 4.34 v GT 5.29 v PV-Vision 6.03; PV-Vision splits cracks at busbar crossings. Nested 5-fold CV for lr. No crack-IoU-only number.
- E-SCDD (R): 805 real + 195 synthetic annotated cells, 30 classes, new class sp_multi_halfcut, 43 new half-cut multi cells; FID 4.10; only evaluated with AA-CLIP anomaly detection (pixel AP +8.34), never with a segmenter. Annotation used a SAM fine-tuned on SCDD (Roboflow Smart Polygon).
- STC-Net (R): PVEL-S (840 train / 360 test); 72.52 mIoU on test, mean over classes including background, so not comparable to our crack IoU. Power loss = linear in a crack-dilated dark-pixel proxy.
- Torpey (R): R2 (COCO seg) and R4 (ImageNet SimCLR) beat all other regimes on crack IoU, p <= 0.0001, block-centred image IoU with Tukey HSD; 642-cell dataset; DeepLabV3-ResNet50.
- RERN (R): ODS F 0.854 on PSCDE with maxDist 0.0015.
- Fracture-informed ensemble (R): 0.8399 mIoU, defect mIoU 0.7786 on an internal 5-class test set; paired bootstrap over Edge-LDRM. Distant data, unknown labels.
- GDI (R): rare-class F1 up to +63.6% and 26% fewer co-occurrence errors, multi-label classification on UCF-EL, not segmentation.
- Hijjawi (R): ConvNeXt-V2 mask mAP50 0.602, mIoU 0.650 on UCF-EL (UCF-EL has known train/test leakage, E from BRIEF).
- PV-S3 (R): +9.7 mIoU over a fully supervised SOTA with 20% labels on UCF-EL.
- DINOv2 AD (R): AUROC 0.888 on deduplicated PVEL-AD; calibration transfer to ELPV collapsed to AUROC 0.500.
- Pratt ICTAS (R): FF r2 0.42 for a "brightening" class added with 24 labelled samples.
- Mayr (R): abstract only; no number retrieved.
- Otamendi (R): 60% annotation cost reduction claimed; no seg number retrieved.

## 4. Minimum experiments (arm, baseline, metric, kill line)

All on the house U-Net++ / ResNet-34 at 100% labels, 5 seeds per arm unless stated. Test = clean 49. Smallest detectable crack IoU change with 5 v 5 seeds is about 0.012 (BRIEF section 4).

1. MultiSolSegment head: arm = house PF + 2 sigmoid channels (BCE + Dice); baseline = PF. Metric = crack IoU, inactive IoU, relF1@2. Kill if crack IoU < +0.012 and inactive IoU < +0.02. About 12 GPU-h.
2. PV-DDPM: train on train split; generate 500 half-cut multi cells with transplanted train crack/inactive masks; arm = PF + synthetic at 20% sampling; baseline = PF. Metric = E1 crack relF1@2 and E1 inactive IoU; guard: test crack IoU must not fall by > 0.012. Kill if E1 relF1@2 < +0.03 and E1 inactive IoU < +0.03. About 60 GPU-h (DDPM about 40).
3. Isolated-area prior: step 0 (CPU, 1 h): on val, compute the isolated area from GT crack + ribbon/busbar masks; kill if it covers < 50% of GT inactive pixels. Step 1: arm = PF + isolated map as an extra input to a stage-2 inactive head; baseline = PF. Kill if inactive IoU < +0.02. About 8 GPU-h.
4. Out-of-fold refiner: OOF 5-fold ensemble probs on train + val; tiny refiner; baseline = 5-seed ensemble at argmax (crack IoU 0.485 to 0.488). Kill if crack IoU < +0.01 or mIoU_rob drops. About 15 GPU-h.
5. GDI twins: LaMa erase of 3 to 5 px dilated crack masks on 209 train cells; arm = house + paired twins; baseline = house. Metric = crack relP@2 and IoU. Kill if relP@2 < +0.01 and IoU < +0.012. About 10 GPU-h.
6. Lp weak loss on ELPV: arm = house + Lp image-level crack loss on ELPV (BMRK test/val cells removed); baseline = house. Metric = BMRK crack IoU (0.379) and overall crack IoU. Kill if BMRK crack IoU < +0.03. About 10 GPU-h.
7. STC priors: arm = 3-channel input (image, Sobel, high-pass), then full prior injection; baseline = house. Metric = crack relF1@2, E1 crack recall. Kill if relF1@2 < +0.01 and E1 recall < +0.02. About 12 GPU-h.
8. BSRA decoder: arm = U-Net++ + BSRA; baseline = house. Metric = relF1@2, components >= 20 px found. Kill if relF1@2 < +0.01. About 8 GPU-h.
9. Mask2Former: arm = Mask2Former + ConvNeXt-V2-T, 40k iters; baseline = house. Metric = mIoU_rob, inactive IoU. Kill if mIoU_rob < 0.580 and inactive IoU < 0.449. About 30 GPU-h.
10. COCO whole-network init: arm = DeepLabV3-R50 COCO weights, PF; baseline = same arch ImageNet encoder, and house. Metric = crack and inactive IoU. Kill if crack IoU gain < 0.012 over its own ImageNet twin. About 15 GPU-h.
11. Style suppression: arm = PF + BSS in layer1-2; baseline = PF. Metric = E1 crack relF1@2, leave-one-source-out crack IoU on val folds. Kill if E1 relF1@2 < +0.03. About 8 GPU-h.
12. Label refinement: arm = house on refined crack masks for flagged cells; baseline = house on revised masks. Metric = test crack IoU on unchanged test labels and relF1@2. Kill if both < +0.012. About 8 GPU-h.
13. EI-AE channel: arm = PF + AE anomaly channel; baseline = PF. Metric = E1 crack relR@2 at matched relP@2. Kill if < +0.03. About 20 GPU-h.
14. DINOv2 prototypes: no training. Metric = crack pixel AUROC on H36/F51 val v house p(crack). Kill if lower than the house model. About 2 GPU-h.
15 to 18: benchmark baselines and severity; run once under the fixed protocol; no kill line for scores.

## 5. Prior overlap with BRIEF section 5 (honest)
- Multi-label heads, mask-classification decoders, refinement stages, edge formulations, noisy-label / label refinement, anomaly priors, diffusion synthesis, cross-dataset training with image labels: listed as never tried. Open.
- PV-DDPM: "synthetic half-cut views (n.d.)" were not generative, so this is open. "+107 E-SCDD cells (n.d.)" covers the real new cells; whether the 195 labelled synthetic E-SCDD cells were included is unknown to me.
- GDI: "crack copy-paste onto pool cells (n.d., more decoys)" adds cracks; GDI removes them to make paired negatives. Different mechanism, open.
- Torpey COCO init: ImageNet encoders, MIM, DDeP, UCF-EL encoder pretraining and foundation probes were tested; full-network COCO segmentation pretraining was not. Note ResNet-50 hurt inactive under the house fine-tune.
- SSN style suppression: test-time per-panel BN adaptation and intensity normalisation failed; train-time style statistics suppression was not tested.
- STC priors: no overlap.
- PV-S3: SSL at 100% labels is closed (n.d.); the Semi-CE loss alone is open but low value.

## 6. Notable papers rejected (one line each)
- DSDINet doi:10.1016/j.apenergy.2026.128093 and PV-MambaSeg doi:10.1109/tii.2026.3707683: EL-specific architectures on PSCDE; no evidence on thin noisy labels; code for PV-MambaSeg not yet out. Keep as optional benchmark entries (bench about 50).
- ELMaskNet doi:10.1109/ccdc69976.2026.11559897: +2.7 mIoU over Mask2Former; conference, no code; folded into #9.
- SegFormer for EL doi:10.1109/jphotov.2024.3450009: UCF-EL only, generic; a benchmark baseline, not a score lever.
- SEiPV-Net doi:10.3390/en16237726, Attention SegNet doi:10.1109/access.2024.3431098, PDeT doi:10.3390/s24216908: architecture tweaks without small-data or thin-label evidence.
- Referring segmentation doi:10.1109/tii.2025.3567396: text-conditioned task, 60k pairs, does not address our problems.
- MSC-FPL doi:10.1016/j.rineng.2026.109782: crack-orientation classes and power-loss projection; mIoU 85% includes background; severity idea noted.
- Saborido-Barba doi:10.1016/j.solener.2026.114394: Type-C crack power loss statistics; severity reference only.
- Bayat doi:10.3390/s26123775: controlled 5-fold image-level benchmark, argues for module-grouped CV (supports our fold roots); classification only.
- PVEL-AD citers (YOLO family, VarifocalNet, DETR variants): box detection, not segmentation.
- SAM domain-knowledge doi:10.1016/j.solener.2025.114145: no abstract retrievable; could not verify the mechanism. Flag for a D-direction on SAM fine-tuning.

## 7. Gaps
- search_snippets failed all session (rate limit), so no in-text evidence on how citing papers split or score BenchmarkEL; no critique of BenchmarkEL splits was found in any citing abstract.
- No citing paper reports results on BenchmarkEL 20211104 with the revised crack labels, so there is no external number to compare with our 0.474 crack IoU.
- Full text of the SAM domain-knowledge paper (Song et al. 2025) and Song SSRN 5289330 (SAM-based PV cell segmentation) not read; deserves its own search.
- PVEL-S (1,200 refined masks) origin paper not identified.
- Sandia crack VAE / crack image generation reports (doi:10.2172/3369071, doi:10.2172/2584982) and Jost 2026 crack morphology (doi:10.2139/ssrn.7649555) have no abstracts; possible severity and synthesis leads.
- Code URLs for MultiSolSegment, Hijjawi, GDI, DSDINet are unverified.
