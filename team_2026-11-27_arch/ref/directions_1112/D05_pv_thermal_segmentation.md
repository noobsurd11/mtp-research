# D05. Thermal (IR) PV fault detection and segmentation from drones, 2020 to 2026

Status: DONE (12 Nov 2026). Scout: D05.
Tags: R = what a paper or dataset page states, E = what our own files measured, S = my judgement.

## 0. Bottom line (S)
- Thermal literature gives almost nothing that raises our EL crack score directly. The physics says why: cracks that isolate no area are thermally silent (R: Dhimish 2021, 12 cells, modes 1 and 2 show no hot spot; R: DTU 2025, cracked modules "difficult to distinguish from healthy ones"). Our own G0 check found dark-IR signal only at row / edge level (E, handbook doc 22 section 8).
- Three things are worth taking into the EL work: (1) the cross-plant evaluation framing of Bommes 2022 (train on one plant, test on another) as a model for the benchmark's unseen-module split; (2) the anomaly-residual prior of MGDT 2026 as an extra input or attention bias for inactive and E1; (3) SegFormer as a cheap transformer-segmenter arm, which has never been run here (BRIEF section 5, "never tried").
- For a second deliverable (WattCycle drone thermal), a one-month project is feasible on public data: module extraction (PV-Hawk, code), a module-level fault classifier trained on PVF-10 + InfraredSolarModules and tested cross-plant on our A3 (DTU) set, Corley-style max-median hot-spot severity bands, and a table that maps thermal classes to expected EL findings. A real WattCycle flight is needed to test it; no public set gives cell-level pixel masks on more than 4 panels.

## 1. Queries run
Research MCP search_papers (OpenAlex answered every time; Scopus and ScienceDirect returned HTTP 401, Semantic Scholar was rate-limited or timed out, arXiv answered 3 times):
1. photovoltaic infrared thermography dataset fault classification (2020+)
2. PVF-10 UAV infrared photovoltaic fault dataset (2020+)
3. UAV thermal solar panel hotspot semantic segmentation (2020+)
4. InfraredSolarModules anomaly classification infrared solar modules (2020+)
5. electroluminescence and infrared thermography comparison same photovoltaic modules defects correlation (2020+)
6. photovoltaic module instance segmentation aerial thermal images Mask R-CNN (2020+)
7. photovoltaic thermal infrared fault recognition self-supervised foundation model (2025+)
8. unsupervised anomaly detection thermal images photovoltaic plant domain shift cross-plant (2020+)
9. solar cell cracks hot spots thermal impact power loss electroluminescence (2020+)
10. drone infrared thermography irradiance flight altitude detectability cracks interconnect PID degraded modules (2022+)
11. thermal image to electroluminescence image translation generative photovoltaic (2020+)
12. photovoltaic module power loss estimation infrared thermography deep learning regression (2020+)
13. segment anything thermal infrared photovoltaic panel segmentation zero-shot (2023+)
14. photovoltaic infrared dataset pixel-level annotation defect segmentation benchmark (2025+)
15. dataset for recognition of snail trails and hot spot failures in monocrystalline Si solar panels (no year)
16. thermal infrared photovoltaic hotspot segmentation dataset masks (2025+)
17. lock-in thermography solar cell defects deep learning segmentation shunts cracks (2020+)
18. cross-modal knowledge distillation segmentation auxiliary modality available only during training (2021+)
19. daylight electroluminescence photoluminescence outdoor drone imaging PV modules (2020+)
20. UAV infrared photovoltaic defect detection small hotspot (2025+)

search_snippets: 4 attempts (InfraredSolarModules facts; EL vs IR crack visibility, twice; PVF-10 data availability). All 4 failed: Semantic Scholar keyless pool rate-limited.
Snowballing: get_citations on PVF-10 (53 citing) and on Bommes 2022 SupCon (68 citing).
get_paper on 22 papers. fetch_fulltext: Corley 2025 (arXiv, read data / architecture / results), Joshi and Pal 2026 (arXiv, read split / results), DTU EPJ PV 2025 (failed, no PDF).
WebSearch (7): InfraredSolarModules repo and licence; PVF-10 repo; PV-Hawk repo; Li and Jain code; PVF-10 download; Mendeley 82vzccxb6y; Zenodo 16420123 (no match).

## 2. Public thermal PV datasets (R unless tagged)

| Dataset | Labels | Size | Licence | Source of the facts |
|---|---|---|---|---|
| PVF-10 (Wang et al. 2024) | image level, 10 classes (5 repairable, 5 not) | 5,579 module crops, 8 plants, UAV | unverified; download location not found | doi:10.1016/j.apenergy.2024.124187; a 2026 paper states a 112x112 version and a fixed train / test split ship with it |
| InfraredSolarModules (Raptor Maps, 2020) | image level, 12 classes (11 anomaly + no-anomaly) | 20,000 crops, 24 x 40 px | MIT (repo LICENSE, per web search of a mirror) | github.com/RaptorMaps/InfraredSolarModules (via web search); used by JEFFNet and MGDT |
| Alfaro-Mejía 2019, Mendeley 82vzccxb6y | cell condition scheme (hot spot, snail trail, sound) on 4 panels; masks only in follow-up papers | 277 images, 336 x 256 JPG, one string of 4 mono panels, Cali | CC BY 4.0 (Mendeley page) | doi:10.1016/j.dib.2019.104441; web search |
| DTU drone IR (A3, on our disk) | induced fault type per module (cracks 8, interconnect 8, PID 6, diode 7, glass 2, soiling 12), STC I-V, one EL per degraded module | 43 modules, 4 altitudes, 200 to >800 W/m2 | CC BY 4.0 (E, doc 22) | doi:10.1051/epjpv/2025020 |
| UCF OSF csr6t / ar76v (A1, A2, on disk) | dark forward-bias IR + EL + UVF + I-V, module level pairing | 157 + 15 modules with IR | CC BY 4.0 (E, doc 22) | handbook doc 22 |
| Fengguo et al. 2026 EL + IR | boxes, unified label scheme | 359 EL + 569 IR images | unverified; availability unverified | doi:10.1109/isitia71267.2026.11642343 |
| SolarFCD 2026 | image level, 4 merged classes, RGB + thermal | 4,435 images merged from 3 public sets | states open release (not checked) | arxiv:2604.23662 |
| Li and Jain 2026 benchmark | image level, visible / EL / IR | "benchmark dataset of diverse labeled PV images" released; size not read | unverified | doi:10.1016/j.solener.2026.114801 |
| Corley et al. 2025 (CVPRW) | orthomosaic-level GeoJSON polygons, >6,000 US farms | private | not released | arxiv:2503.02128 (full text read) |
| Peng 2026, DM-PV (Wang 2026), Joshi-annotated masks | boxes / OBB / masks | 5,583; DM-PV size not read; 277 | not released or unverified | doi:10.3390/s26123736; doi:10.3390/rs18152607 |

Finding (S): no public thermal set gives pixel masks across many plants. The only mask work (Joshi and Pal 2026) annotated 277 images of the same 4 panels and split them at random, so its 0.83 mIoU is a within-panel number. For a one-month thermal deliverable the realistic label level is image / module level plus rule-based hot-spot localisation.

## 3. How thermal findings map to EL findings (R from the sources, S where tagged)

| EL finding (our class) | Sunlit drone IR | Source |
|---|---|---|
| crack, no isolated area (mode A, "micro-crack") | no hot spot | R: Dhimish 2021 (12 cells); R: DTU 2025 (cracked modules hard to tell from healthy) |
| crack with isolated / inactive area (modes B, C; "shaded area", "breakdown") | hot spot likely, cell 25 to 100 C; worst at 40 to 60 % shading ratio (105 C) | R: Dhimish 2021 |
| interconnect / ribbon disconnection (dark region in EL) | elongated thermal pattern, detectable from 600 W/m2 | R: DTU 2025 |
| PID (dark cells at module edge in EL) | no pronounced anomaly in early stage | R: DTU 2025 |
| bypass diode short (whole substring dark or dim in EL) | strong hot strip, 80 to >100 C, visible at 200 W/m2 | R: DTU 2025 |
| soiling / bird drop (EL normal) | hot spot without an EL defect: a thermal false alarm for EL purposes | R: DTU 2025; S |
| scuff (E1 confounder) | unknown, no public evidence | S |

Reading (S): thermal is a triage signal for inactive area, disconnections and diodes, and a severity signal, not a crack detector. Matches doc 22.

## 4. Selected papers

Score = value for raising our EL scores (rubric in the task). Bench = value for the benchmark vision. Code column: only repos I saw through a tool.

| # | Paper id | Year | Venue | Code | Mechanism | Adaptation to our data | Score | Bench |
|---|---|---|---|---|---|---|---|---|
| 1 | doi:10.1002/pip.3518 (arXiv 2112.02922) Bommes et al., SupCon + kNN anomaly | 2022 | Prog. Photovolt. | unverified | Train ResNet-34 with supervised contrastive loss, score anomalies by kNN distance; evaluated train-on-plant-A, test-on-plant-B (AUROC 73.3 to 96.6 % on 9 pairs, 2.92 M images) | Add a SupCon auxiliary loss on cell-level pooled encoder features (defective vs clean cells, grouped by source) to the PF fine-tune, aimed at E1; and adopt the source-to-target protocol as the benchmark's unseen-module split | 35 | 60 |
| 2 | doi:10.1088/1361-6501/ae90d6 MGDT, Xu and Wang | 2026 | Meas. Sci. Technol. | none found | Autoencoder trained on normal thermal crops gives a residual anomaly mask; mask is an attention bias in a ViT and weights a conditional diffusion model that synthesises minority classes (+3.66 macro-F1 on ISM) | Train a conv AE (or patch-memory model) on the 11.9k unlabelled pool; feed its residual map as a 2nd input channel to U-Net++ (anomaly prior; BRIEF lists anomaly priors as never tried). Diffusion half is a separate, costlier step | 35 | 25 |
| 3 | arxiv:2507.20680 (doi:10.1016/j.solener.2026.114402) Joshi and Pal, SegFormer on thermal | 2026 | Solar Energy | none found | Customised SegFormer; on 277 images B2 mIoU 0.86 vs U-Net 0.76, DeepLabv3 0.80, Mask2Former 0.62 (random split, same 4 panels) | SegFormer-B2 encoder (ImageNet or ADE20k weights), 1-ch EL copied to 3 ch, 512 px; its decoder outputs at 1/4 resolution, which will blur 1 to 2 px cracks, so add a full-resolution refinement head or judge it on relF1@2 rather than strict IoU | 40 | 55 |
| 4 | doi:10.1016/j.solener.2026.114801 Li and Jain, unified MLLM PV image diagnosis | 2026 | Solar Energy | unverified | Task-aware prompting of multimodal LLMs for visible / EL / IR; zero-shot ELPV crack 83.5 % (2.8 points under a supervised CNN); GPT-5.1 few-shot >97.3 % | Benchmark: an image-level MLLM baseline (crack present / inactive present per cell) under our split; deliverable: zero-label thermal triage; possible label-audit helper on the 24 flagged train cells | 25 | 60 |
| 5 | arxiv:2503.02128 (doi:10.1109/cvprw67362.2025.00431) Corley et al., aerial IR at scale | 2025 | CVPRW | none released | Cascade: table U-Net (mIoU 97.9) then rotated Faster R-CNN panels (mAP@75 83.3) then YOLOv5 anomalies (P@50 89.8); hot spot = max minus median of a panel sub-grid above 5 C, five severity bands by delta T up to >=15 C | Blueprint for the thermal deliverable; the banded, physically defined severity output is a template for an EL severity layer (inactive area fraction bands per cell) | 15 | 45 |
| 6 | doi:10.1038/s41598-021-03498-z Dhimish and Lazaridis, cracks vs hot spots | 2021 | Sci. Rep. | n/a | Four crack modes measured on 12 cells: modes 1-2 no hot spot, modes 3-4 heat to 100 C | Defines a severity label we can compute from our own masks: crack mode from the predicted inactive fraction per cell; gives the EL-to-thermal mapping for the deliverable | 15 | 50 |
| 7 | doi:10.1051/epjpv/2025020 Del Prado Santamaría et al. (DTU), irradiance and altitude | 2025 | EPJ PV | data: figshare 29665346 (E, on disk) | 43 degraded modules, 4 altitudes, 200 to 1000 W/m2: cracks not separable, interconnects from 600 W/m2, diodes and soiling 80 to >100 C even at 200 W/m2 | Our A3 set; the cross-plant test set for any thermal classifier, and the only public place where IR and EL meet on the same induced faults | 15 | 25 |
| 8 | doi:10.1016/j.apenergy.2024.124187 PVF-10, Wang et al. | 2024 | Applied Energy | unverified | 5,579 UAV crops, 8 plants, 10 classes; 5 CNN / ViT models >83 % OA, best 93.3 % | Training set for the drone deliverable's module classifier; test cross-plant on A3 rather than on PVF-10's own split | 10 | 30 |
| 9 | arxiv:2607.09205 JEFFNet, Azimidokht et al. | 2026 | arXiv | github.com/Azimi2kht/JEFFNet (stated in abstract) | JEPA-pretrained ViT fused with EfficientNetV2-S; PVF-10 10-class F1 93.2, ISM 12-class F1 72.6 | Ready baseline for the thermal deliverable; no EL use expected (frozen foundation features already n.d. on EL, BRIEF section 5) | 10 | 25 |
| 10 | doi:10.3390/en19020462 Ayunts et al., hierarchical thermal classification | 2026 | Energies | none found | Two-stage hierarchy (normal vs fault, then fault type) plus contrast-preserving MixUp for low-contrast, imbalanced thermal crops; Swin-T 89.5 % acc, F1 80.5 | For EL: an image-level "cell has crack / inactive" gate that multiplies the pixel logits (cuts false alarms on clean E1 cells); for thermal: the ISM 8-class recipe | 20 | 20 |
| 11 | doi:10.1002/pip.3448 (arXiv 2106.07314) PV-Hawk, Bommes et al. | 2021 | Prog. Photovolt. | github.com/LukasBommes/PV-Hawk (web search) | Detect, track and georeference modules in drone IR video; extracts per-module image stacks; ResNet-50 >90 % on 10 anomaly classes; SfM version mapped 99.3 % of 35,084 modules (R, via web summary of arXiv 2204.02733) | The module-ID map and per-module crops for WattCycle flights; lets a later EL session be matched module by module (pre-registered EL queue) | 10 | 15 |
| 12 | doi:10.1109/jphotov.2020.2978068 Benatto et al., drone daylight EL | 2020 | IEEE JPV | n/a | 120 fps EL / background pairs from a drone under ~1 sun with modulated bias; module EL at SNR_avg 4.6 | Moonshot route to field EL for WattCycle; our model would face a resolution and SNR shift like E1. Cheap proxy now: degrade test cells to drone-EL resolution and SNR and measure the drop | 25 | 30 |
| 13 | doi:10.1002/pssr.202300059 Doll et al., aerial PL | 2023 | pss RRL | n/a | Hexacopter with light source and NIR camera images PL at night; cracks and PID identified, checked against indoor EL; 13.6 modules / min | Same as 12; PL without contact also separates isolated (inactive) area from dark material in principle (S) | 20 | 25 |
| 14 | arxiv:2604.23662 SolarFCD, Ijaz et al. | 2026 | arXiv | states open code and data (not checked) | Merges 3 public sets with label mapping and near-duplicate removal, 16 classifiers benchmarked | Benchmark-building lesson: unified class map and de-duplication across releases, which is exactly the BenchmarkEL 2021 / 2022 / E-SCDD problem; its 80:10:10 random split still mixes plants, which our protocol should avoid | 10 | 45 |
| 15 | doi:10.1016/j.rser.2026.117457 Pillai et al., benchmarking imaging techniques | 2027 | RSER | n/a | Fault-centric comparison of IR, EL, UVF, PL by visibility and TRL; states that published accuracies come from different data and protocols and are not comparable | Cite in the benchmark chapter as independent support for "numbers are not comparable"; its fault by modality table is the frame for the EL-to-thermal mapping | 5 | 50 |
| 16 | doi:10.1109/isitia71267.2026.11642343 Fengguo et al., EL vs IR multimodal dataset | 2026 | ISITIA | unverified | 359 EL + 569 IR images with weak boxes under one label scheme, YOLO cross-modal fusion | The only labelled EL + IR set found; if public, check whether EL and IR show the same modules, which would allow a cell-level mapping study | 15 | 30 |
| 17 | doi:10.1016/j.dib.2019.104441 Alfaro-Mejía et al., snail trail / hot spot dataset | 2019 | Data in Brief | Mendeley 82vzccxb6y (CC BY 4.0) | 277 drone IR images of a 4-panel string with cell condition layout | Only public IR set with cell-level fault positions; a sanity set for hot-spot segmentation in the deliverable, not a generalisation test | 5 | 10 |

### Minimum experiments (one per paper; all GPU work only after the literature phase)
1. SupCon (1): arm = PF + SupCon aux loss (weight 0.1) on cell-pooled layer4 features, positives = same label (crack / inactive / clean), 3 seeds; baseline = PF 3 seeds; metrics = E1 crack relF1@2 and inactive IoU, test clean-49 crack IoU; kill if E1 relF1@2 gain < 0.02 or test crack IoU drops > 0.01. About 4 GPU-h.
2. MGDT prior (2): arm = PF with 2-ch input (EL + AE residual from an AE trained 2 GPU-h on the 11.9k pool); baseline = PF; metrics = test inactive IoU, E1 crack relR@2; kill if inactive IoU gain < 0.02 and E1 relR@2 gain < 0.03 at 3 seeds. About 8 GPU-h.
3. SegFormer (3): arm = SegFormer-B2 + full-res refinement head, AdamW 6e-5, 20k steps, house augmentation; baseline = house U-Net++ and PF; metrics = test relF1@2, crack IoU, inactive IoU, mIoU_rob, 3 seeds; kill if relF1@2 < house minus 0.01 and mIoU_rob not above house. About 6 GPU-h. Also a benchmark baseline whatever the result.
4. MLLM (4): arm = an open-weight VLM (e.g. Qwen-VL, licence permitting) few-shot "crack present / inactive present" on the 51 F51 val cells; baseline = house model image-level max-probability; metric = AUROC per class; kill as a scorer if AUROC < house minus 0.10 (keep as benchmark row). About 2 GPU-h.
5. Corley severity (5): CPU only. Define EL severity bands from predicted inactive fraction per cell; check band agreement with ground-truth masks on val (weighted kappa); kill the band scheme if kappa < 0.6.
6. Dhimish crack mode (6): with E-PF masks on A3 crack modules (needs Om's open decision on inference location), Spearman between predicted inactive fraction per cell and sunlit IR cell delta T; kill the mapping claim if rho < 0.3. CPU, under 1 GPU-h.
7. DTU A3 (7): resume pick 1 R1 / R2 / R3b exactly as frozen in doc 22 section 11; deliverable table of IR screening recall by fault type. CPU.
8. PVF-10 (8): ResNet-34 / ConvNeXt-T on PVF-10 + ISM; test on A3 module crops (healthy vs induced fault); metric = AUROC per fault type; kill the "train on public, deploy at WattCycle" claim if A3 diode / interconnect AUROC < 0.7. About 3 GPU-h.
9. JEFFNet (9): run official code on PVF-10 fixed split, then on A3 as in 8; compare with the ResNet-34 of 8; keep the cheaper if within 2 F1 points. About 4 GPU-h.
10. Hierarchical gate (10): arm = PF + image-level crack / inactive head whose sigmoid gates pixel logits at inference; baseline = PF; metric = E1 crack relP@2 at fixed relR@2, test relF1@2; kill if E1 relP@2 gain < 0.03. About 4 GPU-h.
11. PV-Hawk (11): run on a public sample video, then on the first WattCycle flight; deliverable metric = share of modules mapped; no kill line (tooling).
12. Drone EL proxy (12): degrade test clean-49 cells (downsample to 32 to 128 px per cell, add noise to SNR 4.6, upsample) and score the house ensemble; report crack relF1@2 and inactive IoU per level. Decision aid for WattCycle, not a model change. Under 1 GPU-h.
13. Aerial PL (13): no experiment possible without hardware; record as future work.
14. SolarFCD (14): CPU. Run a perceptual-hash near-duplicate check across BenchmarkEL 2021 / 2022 / E-SCDD / UCF-EL train vs test; report duplicates found. Kill nothing; this is a benchmark hygiene step.
15. Pillai (15): none; citation.
16. Fengguo (16): find the data; if public and paired, count modules with both modalities. CPU.
17. Alfaro-Mejía (17): use only as a smoke test of the deliverable hot-spot localiser.

## 5. Notable papers rejected (one line each)
- doi:10.1109/eespe68405.2026.11649036 DINOv3 cross-domain thermal: classification only, frozen DINOv3 features already showed no sign of a gain on EL (BRIEF section 5).
- doi:10.1038/s41598-026-50451-z SolarIR-DETR; doi:10.3390/jimaging12060221 PHSNet; doi:10.3390/s26123796 GHM-DEIM; doi:10.1088/2631-8695/ae77a3 IRH-DETR: detector tweaks on private data, random splits, no code seen.
- doi:10.3390/en19030845 Shamisavi 2026 (RF-DETR best on thermal): useful only if the deliverable needs boxes; detection, not segmentation.
- doi:10.3390/s26123736 Peng 2026 OBB + GNSS row / column localisation: overlaps PV-Hawk, no code seen.
- doi:10.3390/rs18152607 FAF-YOLO IR + visible under weak misalignment: needs RGB + IR pairs; nothing for EL.
- doi:10.32620/reks.2025.4.13 Lysyi 2025 thermal + RGB fusion: same reason.
- doi:10.1051/epjpv/2025010 GPT-4o vs ResNet on aerial IR: covered by Li and Jain 2026.
- doi:10.1016/j.infrared.2026.106906 IR diagnosis with RGB prototypes under class-level weak pairing: idea fits (class-level pairing like our module-level EL + IR), but no abstract or full text available.
- Cross-modal distillation (doi:10.1109/tpami.2022.3159589 xMUDA and similar): needs pixel-registered EL + IR training pairs; none exist publicly and our G0 found only row-level signal.
- doi:10.3390/en13246496 solAIr 2020 and doi:10.1016/j.heliyon.2024.e27973 Oulefki 2024: older Mask R-CNN / unsupervised on the same 277-image set.
- doi:10.3390/en18246472 Pratticò 2025 attentive U-Net: small private set, no code.

## 6. What a one-month thermal deliverable could be (S)
Week 1: PV-Hawk (or a simple module detector) on a WattCycle flight; module ID map. Week 2: module classifier trained on PVF-10 + ISM, cross-plant test on A3; JEFFNet as the strong baseline. Week 3: Corley max-median hot-spot rule with delta-T bands; the EL mapping table of section 3; pick 1 R1 / R2 on A3. Week 4: frozen, pre-registered list of modules for the first WattCycle EL session (prospective unseen-module test for the EL benchmark). GPU need under 20 GPU-h. Dependencies: one WattCycle flight, Om's open decisions (doc 22 section 11).

## 7. Gaps
- Semantic Scholar snippets were rate-limited on all 4 tries, so no passage-level evidence was checked; Scopus and ScienceDirect returned 401.
- PVF-10 download location and licence not verified; PV-Hawk licence not verified; Li and Jain code and dataset location not verified; Fengguo 2026 data availability not verified.
- No public thermal dataset with pixel masks across several plants was found; no public pixel-registered EL + IR set exists.
- Daylight EL / PL from drones deserves its own search (it is the only route by which a drone feeds our EL model directly).
- UV fluorescence for crack vs scuff (E1 confounder) is out of this direction's scope but relevant to problem 3.
- Hand-off to the EL-generative scout: doi:10.1016/j.solener.2026.114943 (Mueez, Rawat, Vyas 2026, generative defect isolation for multi-label EL classification) turned up here.
