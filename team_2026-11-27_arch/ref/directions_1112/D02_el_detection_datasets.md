# D02: EL defect detection / classification ideas and public EL dataset census

Scout: D02. Date: 12 Nov 2026. Status: DONE (literature phase only, no servers, no test data).
Labels: R = what a paper or page reported, E = what our own files measured (from BRIEF), S = my judgement.

## 1. Queries run (31)
Research MCP search_papers (OpenAlex answered; Scopus, ScienceDirect returned 401, Semantic Scholar was rate-limited for the whole session, arXiv timed out):
1. "electroluminescence solar cell defect dataset pixel annotation" (2020+)
2. "photovoltaic electroluminescence dataset release segmentation masks" (2024+)
3. "PVEL-AD near-infrared solar cell anomaly detection dataset" (2021+)
4. "solar cell crack detection electroluminescence YOLO small defect attention" (2024+)
5. "solar cell electroluminescence background suppression busbar finger periodic texture removal defect" (2020+, 1 hit)
6. "few-shot photovoltaic cell defect electroluminescence" (2021+)
7. "electroluminescence images dataset Data in Brief photovoltaic modules annotated" (2022+)
8. "half-cut cell electroluminescence defect segmentation dataset" (2022+)
9. "monocrystalline silicon photovoltaic cell defect segmentation dataset pixel-level crack busbar black spot" (2025+)
10. "electroluminescence crack mode classification inactive area power loss prediction deep learning" (2021+)
11. "unsupervised anomaly detection electroluminescence solar cell normal images reconstruction" (2022+)
12. "weakly supervised segmentation solar cell defects electroluminescence class activation map bounding box" (2020+)
13. "photovoltaic defect segmentation frequency domain high-frequency wavelet electroluminescence crack" (2024+)
14. "cross-dataset generalization electroluminescence defect detection domain shift different manufacturers" (2021+)
15. "Segment Anything fine-tuning photovoltaic electroluminescence defect segmentation" (2024+)
16. "long-tailed imbalanced photovoltaic cell defect electroluminescence rare classes" (2022+)
17. "solar cell crack segmentation electroluminescence transformer thin crack continuity" (2025+)
18. "electroluminescence defect semantic segmentation photovoltaic" (2025+)
19. "new public electroluminescence dataset solar cells annotations benchmark" (2025+)
20. "electrically inactive area dark region segmentation electroluminescence cracked cells quantification" (2020+)

Snowball: similar_papers on (STC-Net, MultiSolSegment, Hijjawi 2025) and on (NWG-DETR, YOLO-PVELAD); get_citations on PVEL-AD (30 most cited). search_snippets x2 failed (rate limit). fetch_fulltext x3 (arXiv only): MultiSolSegment 2603.13337, Yi 2022 2211.05295; STC-Net 2608.01714 and the Chen 2025 review were already in the local library.

WebSearch (11): EL segmentation datasets 2025 with masks; MSPS / DACN; Kaggle PVEL-S; PV-Multi-Defect; ELPV licence; EL-VQA; Zenodo record; PVEL-AD access; Hijjawi code; pv-vision licence; MultiSolSegment code; STC-Net code.

## 2. Census of public labelled EL datasets (2020 to 2026, plus older ones still in use)
Sources: Chen et al. 2025 Applied Energy review doi:10.1016/j.apenergy.2025.126132 section 5.2 (read in full), the dataset papers, and WebSearch summaries of repo pages (pages themselves not opened; treat licence lines as "to verify").

| Dataset | Year | Size | Labels | Access / licence | Use for us (S) |
|---|---|---|---|---|---|
| BenchmarkEL / Wits (Pratt) | 2021 to 2023 | 1,266 labelled (582 + 684 batches) + 2,573 unlabelled, 512 px (R, Chen 2025) | 24-class pixel masks | github.com/TheMakiran/BenchmarkELimages; licence not checked | in use (main set) |
| SCDD / E-SCDD (Torpey 2024 arxiv:2402.17611, Hanifi 2025 arxiv:2511.09604) | 2024, 2025 | 642 labelled + about 22k unlabelled (R, WebSearch summary of 2402.17611) | pixel masks, same CSIR lineage | HF sasan/scdd-unlabeled (BRIEF) | in use (pool, `_rf` cells) |
| Hanifi 2025 LNCS 29-class set doi:10.1007/978-981-96-8892-0_4 | 2025 | not stated in abstract | 29-class pixel masks | code github.com/sntubix/pv-defect-segmentation (from abstract) | likely the SCDD family; check overlap before use |
| UCF-EL-Defect (Fioresi 2022) | 2022 | 17,064 cells (R, Chen 2025); BRIEF counts 9,562 / 2,289 | 10 categories grouped to 5, pixel masks (crack is a region class) | github.com/ucf-photovoltaics/UCF-EL-Defect; licence not checked | joint training only with its own head (leakage, different crack convention) |
| PVEL-AD (Su 2023, doi:10.1109/tii.2022.3162846) | 2021 / 2023 | 36,543 NIR cells, 1024 px; 21,044 boxes, 8 defect classes (line crack, star crack, finger interruption, black core ...); 4,148 image-level labels (R, Chen 2025) | boxes + image labels | github.com/binyisu/PVEL-AD reportedly posted a new Google Drive link and public test labels on 30 Jan 2026; IEEE DataPort node 9119 still asks a signed form from an institutional email; no licence stated (WebSearch summary, verify) | largest crack-box source; box-supervised auxiliary pretraining |
| PVEL-S (subset of PVEL-AD; Chen et al. CMC 2024 doi:10.32604/cmc.2024.058063) | 2024 | 1,200 poly cells, 840 / 360 (R, STC-Net) | binary refined defect masks | hosting unverified (a Kaggle listing was claimed by a search summary, not confirmed) | extra crack masks, poly only |
| SolarCells, SolarCells-S (same CMC 2024 paper) | 2024 | not found | mono pixel masks | unverified | check in the PDF |
| LBNL crack segmentation (Chen 2022/2023, OSTI doi:10.21948/1871275) | 2022 | 1,837 cells, 400 px, plus 576 module images (R) | pixel masks: crack, cross crack, busbar, dark area, background | DuraMAT datahub; pv-vision code github.com/hackingmaterials/pv-vision; licence field not found | best second crack-mask source; has "dark area" (inactive-like) |
| Sandia crack masks for VAE | 2023 | 1,180 masks (R) | model-made by retrained PV-Vision, not human | DuraMAT | do not use as ground truth |
| MultiSolSegment (Sanghi 2026, doi:10.1016/j.solener.2026.114469) | 2026 | 585 mono cells (ASU 92, CWRU-DuPont 123, CWRU-SunEdison 250, LBNL 120 relabelled) (R) | multi-hot 4-channel masks: dark, busbar, crack, non-cell (overlap allowed) | DuraMAT doi:10.21948/2587738; no code repo found; data licence not checked | only public set with overlapping crack + dark labels |
| MSPS (Zhao 2026, Zenodo doi:10.5281/zenodo.21549572) | 2026 | 1,500 mono production-line cells, 640 x 590, 1,000 train / 500 test (R) | pixel masks: busbar break, black spot, crack; two experts + adjudicator | github.com/wch313/MSPS-Dataset (from the Zenodo record); licence not checked; paper "DACN" not found by search | double-annotated crack masks: also a label-noise reference |
| ELPV (Deitsch 2019) | 2018 / 2019 | 2,624 cells 300 px, 44 modules | 4-level defect probability per cell | CC BY-NC-SA 4.0 images, Apache 2.0 code (WebSearch summary) | image-level weak labels; = our BMRK source, so check overlap |
| ELPVPOWER (Hoffmann 2021, doi:10.1002/pip.3416) | 2021 | 718 module images | module Pmp | public (R, Chen 2025) | severity (power) track |
| SDLE damp heat (CWRU) | 2020s | 60 cells per 500 h step to 3,000 h | good / cracked / corroded | OSF (R, Chen 2025) | corrosion examples |
| EPRI PREDICTS2 | 2020s | 108 module images, 36 poly modules, 3 time points | flash I-V per image | public (R) | severity track |
| NREL time-series EL | 2020s | 146,226 images of one cell under DMX cycling | pressure level only | public (R) | crack growth sequences, no masks |
| SolarVQA (HF masked-token/solarVQA-Evaluation) | 2025/26 | 130,712 QA pairs over 16,339 UCF-EL images | text | images from UCF | not useful for masks |
| EL-VQA (unibz) | 2025/26 | unknown | VQA text | unknown | skip |
| Haider 2026 EU PVSEC doi:10.4229/eupvsec2026/3do.16.5 | 2026 | 2,894 images, 61,331 boxes, 14 classes (R) | boxes | access unknown | ask authors only if boxes are needed |
| Aktouf 2024 doi:10.3390/solar4040030 | 2024 | 10,500 cells, 12 classes (R) | boxes | access unknown (class names look PVEL-AD derived) | skip |
| Aktas 2026 doi:10.3390/s26082450 | 2026 | 37,538 production-line cells, 8 classes (R) | image labels | "original dataset", access unknown | skip |
| Polenghi 2026 Data in Brief doi:10.1016/j.dib.2026.113109 | 2026 | small number of damaged cells (R) | EL + VIS + NIR + power + text | public | severity track |
| Pratt 2025 ICTAS doi:10.1109/ictas64866.2025.11155421 | 2025 | 680 modules = 48,960 cells with EL + I-V, CSIR lab (R) | module electrical data | not found public | same lab as our CSIR source: ask Pratt for severity data |

Census summary (S): beyond BenchmarkEL / SCDD, the public human-labelled pixel crack masks are LBNL (1,837), MSPS (1,500), PVEL-S (1,200, hosting unclear), MultiSolSegment (585) and UCF-EL (region-style crack). That is about 5,000 extra cells with thin-crack masks, 10x our 478, but each has its own crack width convention, resolution and cell type. No public set with half-cut cells and pixel masks was found, so none of these addresses the E1 half-cut gap directly. PVEL-AD (36.5k, boxes, test labels now reportedly public) is the largest crack source and is mostly poly.

## 3. Selected papers

| # | id | year | venue | code | mechanism | adaptation to our data | score | bench |
|---|---|---|---|---|---|---|---|---|
| 1 | doi:10.1016/j.solener.2026.114469 (arxiv:2603.13337) MultiSolSegment | 2026 | Solar Energy | none found (data: DuraMAT) | per-channel sigmoid multi-label output so a pixel can be crack and busbar, or crack and dark, at once | keep softmax for the 22 other classes, add independent sigmoid channels for crack and inactive; build overlap targets (inactive channel = inactive label closed over enclosed crack pixels; crack channel unchanged); threshold each channel on val; add MultiSolSegment's 585 cells with a masked loss on the shared channels | 65 | 55 |
| 2 | doi:10.5281/zenodo.21549572 MSPS | 2026 | Zenodo dataset | github.com/wch313/MSPS-Dataset | 1,500 double-annotated crack / busbar-break / black-spot masks from a production line | joint training with a separate output head per dataset (no shared label space), shared encoder + decoder; resample so crack width in px matches ours; mono only | 55 | 70 |
| 3 | doi:10.1109/jphotov.2023.3249970 Chen 2023 PV-Vision + LBNL crack set doi:10.21948/1871275 | 2023 | IEEE JPV | github.com/hackingmaterials/pv-vision | crack segmentation plus crack features (length, maximum isolated area) from 1,837 labelled cells | same per-dataset-head joint training as #2; its "dark area" class is a second inactive source; also the cleanest external crack test set for the benchmark | 55 | 80 |
| 4 | doi:10.1109/tii.2022.3162846 PVEL-AD | 2023 | IEEE TII | github.com/binyisu/PVEL-AD | 36.5k NIR cells with crack / star-crack / finger / black-core boxes | box-supervised auxiliary loss (mask must fill each crack box projection, background outside boxes) to pretrain the decoder, then PF fine-tune on our 478 | 40 | 70 |
| 5 | doi:10.4229/eupvsec2026/3do.16.5 Haider 2026 long-tail EL | 2026 | EU PVSEC | none | diagnosis that tail EL classes fail on localisation (predicted as background); cell-grid-aware copy-paste lifts tail AP | paste inactive+crack pairs, splice, edge_dark and corrosion only onto labelled train cells at grid-consistent places (between busbars, aligned to finger direction), never onto pool cells | 48 | 60 |
| 6 | arxiv:2211.05295 Yi 2022 DIBE loss + OII | 2022 | arXiv | none found | focal loss with separate FP and FN weights plus a region term; an output imbalance index picks the weights so the FP/FN balance at inference matches the target | crack channel only; compute OII on val with 2 px tolerant TP/FP/FN, set FN weight to move relR@2 up (0.866) while relP@2 (0.930) has room | 48 | 30 |
| 7 | arxiv:2608.01714 STC-Net | 2026 | arXiv (MERCon) | none found | fixed Sobel edge prior and FFT high-pass prior as parallel pyramids fused into decoder skips, plus coarse / edge / topology auxiliary heads; crack-to-inactive proxy for power loss | feed Sobel magnitude and a high-pass residual (cutoff above finger pitch, or a notch that removes finger periodicity) as extra input channels to U-Net++; auxiliary head on 2 px dilated crack instead of edge labels; reuse its inactive proxy only as a severity baseline | 42 | 35 |
| 8 | doi:10.1007/s44443-026-00566-0 YOLO-PVELAD | 2026 | J. King Saud Univ. CIS | none found | directional crack-aware attention (strip pooling along H and W with 1-D convs) and DCT high-frequency injection into the FPN | add strip-attention blocks to the two finest U-Net++ decoder stages; add diagonal strips because our cracks are often oblique while busbars / ribbons are axis aligned (strip pooling alone may amplify busbars) | 40 | 20 |
| 9 | doi:10.1088/2631-8695/aea73d NWG-DETR | 2026 | Eng. Res. Express | none found | grid-line-aware gating to damp repetitive grid lines, learnable wavelet down / up sampling that keeps high-frequency detail | replace the ResNet-34 stem max-pool and first stride with Haar wavelet downsampling (LL + LH/HL/HH as channels); gate on gridline / busbar prior from our own structural classes | 35 | 15 |
| 10 | doi:10.1016/j.solener.2026.114943 (arxiv:2608.12725) Mueez 2026 GDI | 2026 | Solar Energy | LaMa public (repo URL unverified) | LaMa inpainting removes chosen defects to make single-defect samples; rare-class F1 up to +63.6% in low data | inpaint inactive regions to normal brightness to make crack-only twins (inactive never occurs without crack in our data), and inpaint cracks out to make clean negatives with identical context; label edits follow the masks | 42 | 30 |
| 11 | doi:10.1039/d5ee05042a Lin 2025 EI-AE | 2025 | Energy Environ. Sci. | none found | iterative autoencoder trained on normal EL only gives pixel anomaly maps; few-shot extension with a handful of masks | train on pool cells the house ensemble calls defect-free (incl. 1,152 half-cut pool cells), feed the residual map as a 2nd input channel; aims at E1 where 70% of crack pixels get p < 0.001 | 35 | 25 |
| 12 | doi:10.1016/j.solener.2025.114083 Hijjawi 2025 | 2025 | Solar Energy | stated public, URL not found | instance seg benchmark on UCF-EL: ConvNeXt-V2 best (seg mAP50 0.602, mIoU 0.650) over Mask R-CNN and Mask2Former, MMDetection | run Mask2Former / ConvNeXt-V2 as semantic baselines in mmseg on 1-ch input replicated to 3, 512 px | 38 | 75 |
| 13 | doi:10.1109/tii.2022.3228680 Otamendi 2022 | 2022 | IEEE TII | arxiv 2212.07768 (code unverified) | data-driven annotation pipeline that reuses public datasets to propose anomaly masks; 60% annotation cost cut | turn house-ensemble + PV-Vision predictions on pool cells into candidate masks, keep only cells where two models agree within 2 px, add as soft-weighted extra training | 30 | 30 |
| 14 | arxiv:2402.17611 Torpey 2024 | 2024 | arXiv | not checked | large evaluation of pretraining paradigms (COCO supervised, SSL) for EL defect seg on SCDD | protocol template for the benchmark's pretraining axis; overlaps our MIM / DDeP nulls | 20 | 60 |
| 15 | doi:10.3390/s26123775 Bayat 2026 | 2026 | Sensors | none | controlled benchmark: 6 backbones, identical pipeline, stratified 5-fold, 150 runs, calls for module-grouped CV | copy the protocol shape (fixed pipeline, many seeds, grouped folds) but with module-grouped folds over our 532 cells | 10 | 65 |
| 16 | doi:10.1051/epjpv/2024039 Jaeckel 2024 | 2024 | EPJ PV | n/a | consensus nomenclature for EL observations: single cracks, multi-cracks, electrical-circuit anomalies, misc; risk classes tied to power loss and safety | defines the crack-mode labels for a severity add-on (map our crack + inactive outputs to its classes) | 10 | 60 |
| 17 | doi:10.1109/ictas64866.2025.11155421 Pratt 2025 ICTAS | 2025 | ICTAS | none | 29-class EL segmentation over 48,960 cells of 680 CSIR modules, per-module defect fraction regressed on fill factor (r2 = 0.42) | same lab as our CSIR source; template for a severity post-evaluation (predicted inactive fraction vs measured power) | 10 | 55 |

Bets: safe = 1, 5, 6; medium = 2, 3, 4, 7, 8, 10, 12, 13; moonshot = 9, 11.

### Minimum experiments (house = U-Net++ / ResNet-34 recipe; PF = encoder-preserving variant; 5 seeds each unless stated; test = clean 49)
1. Multi-label heads: house + sigmoid crack / inactive channels vs house. Metrics: inactive IoU, crack IoU, relF1@2. Kill if inactive IoU gain < 0.02 and crack relF1@2 gain < 0.01. About 12 GPU-h.
2. MSPS joint: PF + MSPS with own head vs PF. Metrics: E1 crack relF1@2 and recall, test crack IoU. Kill if E1 relF1@2 gain < 0.03 or test crack IoU drops > 0.012. About 20 GPU-h.
3. LBNL joint: same design as 2 with LBNL (crack + dark area to inactive head). Kill line as 2, plus inactive IoU on BMRK cells. About 20 GPU-h.
4. PVEL-AD box pretrain: box-projection pretrain (20k steps) then PF vs PF. Kill if E1 relF1@2 gain < 0.03 and test crack IoU flat. About 30 GPU-h.
5. Grid-aware rare-class paste: vs house. Metrics: inactive IoU, mIoU_rob, splice / edge_dark IoU. Kill if inactive < +0.02 and mIoU_rob < +0.005. About 10 GPU-h.
6. DIBE-style FN-weighted focal on crack: vs house. Metric relR@2 at relP@2 >= 0.92. Kill if relR@2 gain < 0.015. About 10 GPU-h.
7. Prior channels (Sobel + high-pass): vs house. Kill if crack IoU < +0.012 and E1 recall < +0.03. About 8 GPU-h.
8. Strip attention: vs house. Same kill as 7. About 8 GPU-h.
9. Wavelet stem: vs house. Kill if crack components >= 20 px found does not rise by 0.02. About 8 GPU-h.
10. Inpainted twins: LaMa fine-tune on pool (about 20 GPU-h) then house + twins vs house. Kill if inactive IoU < +0.02 and crack precision flat. About 35 GPU-h.
11. Anomaly channel: AE on pool (about 15 GPU-h) then house 2-channel vs house. Kill if E1 relF1@2 < +0.03. About 25 GPU-h.
12. Mask2Former baseline: 3 seeds, 40k iters vs house. Bench entry regardless; kill as a score arm if crack IoU < house - 0.02. About 30 GPU-h.

## 4. Notable papers rejected (one line each)
- doi:10.1016/j.solener.2025.113546 Liu 2025 few-shot rare-defect detector: no abstract or full text retrievable off campus; mechanism unverified.
- doi:10.1016/j.solener.2025.114145 Song 2025 SAM + domain knowledge: no abstract retrievable; SAM fine-tuning belongs to the foundation-model direction.
- doi:10.1109/tsm.2022.3197933 ERDCF-Net crack seg: refined side outputs, generic deep supervision, paywalled.
- doi:10.3390/mi16091003 PSDD, doi:10.1038/s41598-026-70180-7 ECF-DETR, doi:10.3390/s26092616 MSW-Mamba-Det, doi:10.3390/s26041373 MambaVSS-YOLO, YOLO-ACF, MRA-YOLOv8, CCA-YOLO, PA-YOLO: detector-neck tweaks measured as mAP50 on PVEL-AD, single seed, no thin-structure evidence; the transferable parts are covered by #8 and #9.
- doi:10.1016/j.renene.2025.124549 CrackNet transformer: no abstract.
- doi:10.1038/s41598-026-63443-w ordinal severity grading: image-level, method not inspected; keep for the severity scout.
- arxiv:2603.14869 SEPDD self-evolving pipeline: AutoML retraining loop for detection, not a segmentation mechanism.
- doi:10.32604/cmc.2024.058063 lightweight multiscale network: value is its datasets (PVEL-S, SolarCells), not the network.
- doi:10.3390/s26082450, doi:10.1038/s41598-025-14478-y, many ELPV classifiers: image-level classification on private or ELPV data.
- doi:10.1109/tie.2021.3070507 BAF-Detector: older multiscale attention FPN for boxes; superseded.

## 5. Gaps
- No public half-cut EL set with pixel masks found; E1 half-cut + scuff gap is not addressable by public data alone.
- Licences for MSPS, LBNL, MultiSolSegment, BenchmarkEL, UCF-EL not read from the pages; must be read before any use (and before a benchmark redistributes splits).
- PVEL-AD new download and public test labels: reported by a search summary of the GitHub README, not opened.
- PVEL-S / SolarCells / SolarCells-S hosting not confirmed; read the CMC 2024 PDF.
- DACN (MSPS paper) not found; MSPS crack width convention unknown.
- Overlap check needed: ELPV vs our BMRK cells; LBNL 120 cells reused inside MultiSolSegment; SCDD vs Hanifi 29-class set.
- Semantic Scholar snippets were rate-limited all session, so evidence questions (e.g. measured crack width per dataset) were not answered.
- Sub-direction worth its own scout: box- and image-label weak supervision for thin cracks (BoxInst-style projection, CAM) using PVEL-AD and ELPV.
