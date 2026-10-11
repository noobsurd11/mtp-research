# F04: census of EL datasets and EL training-methodology papers (2019–2026)

Compiled 10 Oct 2026, 09:36–10:05 IST, by the F4 scout. Links were checked through Crossref, Unpaywall, OpenAlex, DataCite, the GitHub API and the publisher pages.

Read scope per item:
- **[meta]**: metadata or abstract only.
- **[page]**: repository or dataset page.
- **[ours]**: measured by us today; scripts in the scratchpad `f4/scripts/`, data pulled from the public repos.

The paywalled papers are in `F04_paywalled_queue.md`.

---

## 1. Two first-hand findings from today [ours]

### 1a. BenchmarkEL has two newer releases, and the newest revised the crack labels heavily

GitHub tree of `TheMakiran/BenchmarkELimages` at HEAD (2024-03-10 push):

| Release | Train / val / test (originals) | Total | Notes |
|---|---|---|---|
| `dataset_20211104` (**the one we use**, and Pratt 2023's 50-image test) | 478 / 54 / 50 | 582 | `masks_coded_*` |
| `dataset_20220723` | 511 / 65 / 66 | **642** | = Torpey et al. 2024's "642-image CSIR dataset", so Torpey almost certainly used this release |
| `dataset_20221008` | 553 / 70 / 72 | **695** | +113 images over ours (mostly CSIR, some BMRK); 72-image test |

**Splits were reshuffled between releases.** From 20211104 to 20220723:
- 48 of our train images moved to test;
- 38 of our test images moved to train;
- 48 train images moved to val and 45 val images moved to train.

Numbers from different releases are therefore not comparable. In particular, Torpey's mIoU 0.486–0.550 is on a different test set from Pratt 2023 and from ours.

**Mask revisions** (pixel comparison of every mask whose git blob changed; class 14 = crack, 11 = inactive):

| Comparison | Masks changed | Crack-label change on changed images |
|---|---|---|
| 20220723 → 20221008 (images identical, 637/638) | 207 / 638 | 113 crack images relabelled; crack px 117,676 → 168,530 (+43%); pooled crack IoU old vs new 0.613 (per-image median 0.51); inactive IoU 0.821 |
| Our 20211104 → 20221008, **train** (474 common) | 156 | 81 crack images changed; crack IoU old/new 0.567; px +51% |
| Our 20211104 → 20221008, **val** (54) | 18 | 14 crack images; IoU 0.638 |
| Our 20211104 → 20221008, **test** (50) | **42 / 50** | **35 test images' crack labels changed; px +39%; IoU old/new 0.693**; inactive IoU 0.909 |

**What the revision did to crack labels** (changed images, 20220723 → 20221008):
- Mean label width (pixels per skeleton pixel) went from 1.82 to 2.55.
- 8-connected crack fragments went from 3,707 to 549, a 7× drop: dotted labels were joined.
- 100% (median) of new crack pixels lie within 1.5 px of the old label.

**Reading:** the newest release fixes exactly the two crack-label defects we measured on 20211104 (dotted labels, and labels about 1.75 px wide on a crack about 4 px visible). It is a cleaned re-annotation, not an independent one.

### 1b. BenchmarkEL's "BMRK" images are ELPV cells

Four of four checked, normalised cross-correlation 1.000. Each BMRK image is the ELPV cell with the same number (`BMRK_xxxxx_cellNNNN` ↔ ELPV `cellNNNN.png`), rotated 90° and downscaled from 300 to 256 px inside a 512 × 512 padded canvas. Best match with any other cell: 0.33–0.56.

Implications:
- ELPV (2,624 cells) is *not* an independent pool or test set for BenchmarkEL. Its cells can be excluded by number.
- ELPV's image-level defect probabilities provide weak labels for the same distribution, including the BMRK cells that have pixel masks.
- BMRK cracks sit at about 0.85× native resolution in a padded canvas. This partly explains the large padding share and BMRK's wider crack labels (about 3 px).

---

## 2. Public EL datasets

| Dataset | Images | Resolution | Labels | Classes | Licence / access | Overlap risk with ours | Unlabelled pool |
|---|---|---|---|---|---|---|---|
| **BenchmarkEL** (Pratt 2021/2023; GitHub TheMakiran) [page, ours] | 582 / 642 / **695** labelled (3 releases) | 512 × 512 (cells padded) | pixel, single-label | 24 (12 features + 12 defects) | no licence file; public | sources: CSIR, CFVS (CFV Labs), ARTS (ARTsolar), SDLE (CWRU), BMRK (= ELPV/ZAE Bayern) | **>150k cells** (Dropbox; 2,573 modules, >2,000 from one CSIR rooftop); we hold 11,938 |
| Torpey 2024 EL set [meta] | 22k unlabelled (of a 64k collection) + 642 labelled | – | – | 28 (15 defect + 13 feature) | URLs redacted in arXiv v1 | 642 = BenchmarkEL 20220723 | 22k |
| **UCF-EL** (Fioresi 2022; GitHub ucf-photovoltaics) [ours, page] | 11,851 released (9,562 / 2,289; the paper says 17,064) | 190–600 px (mode 290) | pixel (polygons/rectangles → masks; instance-capable) | crack, contact, interconnect, corrosion (+ ignore) | no licence file | official split by cell; 25–44% of test cells have a physical twin in train | about 5.2k extra cells, almost all defect-free |
| UCF-EL-GDI (HF `mueez-underflow`) [page] | defect-removed synthetic UCF images | – | per defect folder | UCF classes | no licence in card | derived from UCF | – |
| **ELPV** (Deitsch/Buerhop, ZAE Bayern) [page, ours] | 2,624 cells, 44 modules | 300 × 300 | image-level defect probability {0, ⅓, ⅔, 1} + mono/poly | 1 | CC BY-NC-SA 4.0 | **contains BenchmarkEL BMRK (verified)** | – |
| **PVEL-AD** (Su et al. TII 2021/2023) [page] | 36,543 NIR EL cells | about 1024² (paper; unverified) | **boxes** (40,358) | 12 defects + normal (crack, star_crack, finger, black_core, thick_line, dislocations, short_circuit, printing_error, corner, fragment, scratch) | request form, institutional email, research only (repo Apache-2.0) | production-line mono cells, different source; low risk | normal class (count not stated); test annotations public in the newer note |
| **PV-Vision crack benchmark** (Chen, Karin, Jain; LBNL) [meta] | about 1 GB; count not stated | – | pixel: crack, busbar (+ dark) | 2–4 | DOI 10.21948/1871275 (OSTI) | LBNL source; possible overlap with MultiSolSegment's LBNL 120 | module EL from field surveys |
| **MultiSolSegment** (Sanghi 2026; DuraMAT) [meta] | 585 (CWRU 373, ASU 92, LBNL 120) | – | **multi-label** pixel masks | crack, busbar, dark, non-cell | CC BY-NC-ND 4.0; DOI 10.21948/2587738 (DuraMAT datahub moved; old URL 404s) | **CWRU = BenchmarkEL's SDLE source** (check by hash); LBNL ↔ PV-Vision | – |
| PVELNet set (Sensors 2026) [meta] | 37,538 cells | – | image-level, 8 classes | – | not stated as public | – | – |
| Korovin HJT (Solar Energy 2023) [meta] | 68,748 HJT cells | – | image-level + few masks | – | private | – | normal-heavy |
| Data in Brief 2026, damaged-cell multispectral [meta] | small, single technology | – | EL + VIS + NIR + power records per damage stage | – | OA | – | controlled damage → power: a severity ground truth |
| Sandia/OSTI 2024, crack image generation [meta] | synthetic | – | – | – | OA report 10.2172/2999409 | – | – |

Not found / not EL: "ELDDS" (no EL dataset of that name verified); "PVEL-S" (named in STC-Net, undescribed); SolarFCD (2026, RGB/thermal, not EL); ISP-AD (2026, screen printing, not EL). The *Applied Energy* 2025 review "Open data sets for assessing PV system reliability" (10.1016/j.apenergy.2025.126132, OA) is the place to sweep for anything missed.

---

## 3. EL papers using semi-, self-, weakly supervised, unsupervised or few-shot learning (2019–2026)

| Paper | Supervision | Task / data | Numbers (as reported) | Evaluation flaws / notes |
|---|---|---|---|---|
| Mayr et al., ICIP 2019 (arXiv 2001.11248) [meta] | weak, image-level | crack segmentation from CAMs (normalised Lp pooling), ResNet-50 | – | evaluation scope unknown |
| Balzategui et al., Sensors 2021 [meta] | normal-only GAN → automatic labelling → supervised | manufacturing cells | – | auto-labels as pseudo-labels; same-line data |
| Korovin et al., arXiv 2022 / Solar Energy 2023 [meta] | "semi-supervised" Mahalanobis anomaly (SeMaCNN) | 68,748 HJT cells; classification + segmentation | acc 92.5%, F1 95.8% | private data; image-level metrics |
| Torpey, Pratt, Klein, arXiv 2024 [sections] | in-domain SimCLR, IN-SimCLR/MoCo, CCT, U2PL | BenchmarkEL-642 (20220723) | mIoU: random 0.486, COCO 0.544, IN-SimCLR 0.534, EL-SimCLR 0.517, CCT 0.550, U2PL 0.448 | full labels only; best-val checkpoint; CCT/U2PL single run; no MAE |
| Kang et al., IEEE Access 2024 [meta] | weak, module-level (MIL) | cell-level defect detection | – | – |
| Jha et al., PV-S3 (arXiv 2024 / EAAI 2025) [full, code] | Mean Teacher + SemiCE | UCF-EL segmentation | 0.828 under its own metric | background dropped from the metric; test images in train lists; under-trained baseline (ours) |
| Gil et al., ICEIC 2025 [meta] | semi-supervised, module + cell labels, two-stage | cell defect detection | "improves on same dataset" | conference, paywalled |
| Liu et al., Solar Energy 2025 [meta] | **few-shot detector for rare defects** | EL cell defects | – | paywalled; the only rare-defect-targeted EL paper |
| Demant group, Solar RRL 2025, Quality Activation Maps [meta] | weakly supervised regression (global IV → local maps) | inline EL/thermography | – | weak labels from measurements, not annotators |
| Lin et al., EES 2026 (10.1039/d5ee05042a) [meta] | **unsupervised (iterative AE, "EI-AE") + few-shot pixel segmentation** | PV EL | – | OA (CC BY-NC); publisher blocks scripts (read via browser) |
| Lv et al., Solar Energy 2026 [meta] | unsupervised anomaly detection, normal-only | multi-line module manufacturing | – | paywalled |
| MS-OSSLNet, Sci. Rep. 2026 [meta] | DINO self-supervised + ordinal (CORAL) | **severity grading** of EL defects | – | classification; imbalance claimed |
| PVELNet, Sensors 2026 [meta] | (search snippet says SimCLR pretraining) | 37,538 cells, 8 classes | about 98% acc | classification |
| ICSMD 2024, SAM + feature fusion [meta] | zero-training SAM with point prompts | ELPV | "confidence 0.597 → 0.677" | no IoU against ground truth |
| PV-SAM (SSRN 2025) / Solar Energy 2025, fine-tuned SAM [meta] | foundation model fine-tuned | cell-level defect segmentation | – | check whether trained on UCF-EL with the leaky split |
| Jost et al., PVSC 2025; `pvcracks` VAE (OSTI 10.21948/2997860) [meta] | unsupervised VAE crack parametrisation → power loss | cracks | – | – |
| Hijjawi et al., Solar Energy 2026 [meta] | supervised **instance** segmentation (ConvNeXt-V2, Mask2Former) on UCF-EL | UCF-EL | mAP50 0.602 | "benchmarked against all studies on UCF EL", likely the official leaky split |

Pattern:
- Fully semi-supervised **pixel segmentation** on EL is still only PV-S3 and Torpey's CCT/U2PL arms.
- Everything else is weak (image or module labels), normal-only anomaly detection, or self-supervision for *classification*.
- None reports a label-budget curve with matched supervised baselines, and none evaluates on a physical-module-disjoint split.

---

## 4. Practical constraints (thesis parts 2–3; brief)

**Throughput** (vendor figures):
- Combined flasher/EL/hipot module testers run under 24 s per module (Endeas QuickSun 650, about 150 modules/h).
- Inline EL tools have run under 30 s per module since at least 2016 (ISRA MOD-Q EL).
- At 60–144 cells per module, that is about 3–6 cells/s per line, roughly 0.2 s per cell.
- PV-Vision reports 0.18 s/cell and 0.72 s/module.
- So a 5–25M-parameter CNN is ample. Real-time is not the binding constraint; foundation models can be teachers, but should not be deployed.

**Severity:**
- Crack modes after Köntges et al.: A (no inactive area), B (partly disconnected), C (fully inactive). The IEC TS 60904-13 nomenclature matches (primary sources not read yet).
- Power loss tracks the **inactive / disconnected area**, not crack length (Chen PVSC 2022, "maximum inactive area"; Pratt ICTAS 2025; Hoffmann *Prog. PV* 2021).
- Consequence for part 1: errors in the *inactive* class and in crack *connectivity*, i.e. whether a crack closes off an area, matter more for severity than pixel-exact crack IoU. That supports topology- or tolerance-aware crack metrics and losses.
