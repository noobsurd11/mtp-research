# Scout `thin`: architectures for thin and curvilinear structures (27 Nov 2026)

Scope: crack, vessel, road, neuron/membrane, wire, edge and line architectures and full pipelines; centerline / direction / affinity heads; iterative and graph refinement; resolution-preserving designs. Topology losses were covered on 12 Nov (D10/D11/D12) and are only listed here when they come with an architecture. Literature only: nothing trained, no server touched.

Labels: "full text" = I read the method and results sections via `read_paper`; "abstract only" = abstract or search preview only.

## 1. Queries run

Research MCP `search_papers` (OpenAlex, Scopus, ScienceDirect answered; Semantic Scholar was rate-limited for the whole session; arXiv timed out on most queries, so `search_snippets` was not usable).

1. crack segmentation network thin cracks (2025+)
2. retinal vessel segmentation thin vessels architecture (2025+)
3. curvilinear structure segmentation (2025+)
4. edge detection crisp edges transformer diffusion (2024+)
5. road extraction aerial imagery connectivity graph (2023+)
6. crack segmentation Mamba state space model (2024+)
7. crack segmentation cross-dataset generalization zero-shot unseen domain (2024+)
8. photovoltaic electroluminescence crack segmentation deep learning (2024+)
9. vessel segmentation foundation model generalization fundus OCTA (2024+)
10. wireframe line segment detection (2020+, at least 5 citations)
11. distance transform regression head thin structure segmentation centerline (2020+)
12. iterative refinement network vessel segmentation connectivity recurrent (2019+)
13. high-resolution feature preservation thin object segmentation without downsampling (2022+)
14. segment anything crack segmentation fine-tuning adapter (2025+)
15. neuron membrane segmentation electron microscopy boundary affinity (2021+)
16. coronary artery angiography segmentation thin vessels X-ray (2023+)
17. crack segmentation benchmark dataset tolerance evaluation large-scale (2024+)
18. direction field orientation learning thin structure segmentation crack vessel (2021+)
19. diffusion model segmentation thin structures vessels cracks generative (2024+)
20. tubular structure segmentation deformable convolution MICCAI (2024+)
21. thin structure segmentation vision foundation model DINOv2 frozen features (2024+)
22. power line wire segmentation thin objects (2021+)
23. skeleton prediction auxiliary task segmentation thin cracks super-resolution (2022+)
24. single-source domain generalization retinal vessel segmentation unseen datasets (2023+)
25. road network graph extraction satellite SAM-Road RNGDet topology (2023+)
26. CrackFormer self-attention crack detection fine-grained (2021+)
27. DeepCrack learning hierarchical convolutional features (2018 to 2020)
28. EDTER edge detection transformer (2022+)
29. study group learning retinal vessel label noise SGL (2021+)
30. CS-Net channel and spatial attention curvilinear (2019+)
31. SA-UNet spatial attention U-Net retinal (2020 to 2022)
32. D-LinkNet road extraction (2018 to 2019)
33. CrackSeg9k crack segmentation dataset (2021+)
34. BDCN / RCF edge detection (2017 to 2022)
35. holistically-nested edge detection RCF (2015 to 2019)
36. thin structure segmentation (2026, arXiv + OpenAlex)
37. RNGDet road network graph detection (2022+)
38. spectral bias high-frequency thin crack wavelet segmentation (2024+)
39. self-supervised pretraining curvilinear vessel few labels synthetic curves (2023+)
40. scribble line annotation weakly supervised crack inaccurate width (2022+)
41. vesselFM foundation model universal vessel segmentation (2024+)
42. CT-CrackSeg CrackSeU CrackSegNet (2019+): no results
43. Holistically-nested edge detection (2015 to 2017)

Snowballing with `get_citations`: FR-UNet (311 citing, top 40), DiffusionEdge (146, top 30), UCS (4), SCSegamba (134, top 50), OmniCrack30k (53, top 40), CrackSegFlow (12), DSCNet (891, top 40: almost all YOLO add-ons, noise, as on 12 Nov).
`get_paper` on about 30 candidates. Full text read for 6: FACS-Net, RSF-Conv, Curvi-Tracker, DMSRCrack, RPCANet++, FGOS-Net. Two fetches timed out (WireSegHR, and RPCANet++ on the first try).

## 2. Counts

- Search hits returned: about 1,700 merged results over 43 queries (25 to 65 unique per query, top 3 to 25 shown each) plus about 290 citing papers screened. Most are lightweight crack/vessel modules in low venues or YOLO detectors.
- Kept after screening and dedupe: **127 unique papers** (`papers.tsv`).
- Against `ref/MASTER.tsv` (by DOI/arXiv id and by title): **95 NEW**, **32 already in MASTER** (pid given in the `new_or_pid` column).
- Fit score spread over the 127: 4 = 3 papers, 3 = 4, 2 = 14, 1 = 71, 0 = 35. (Top 10 below = the three 4s, the four 3s, three 2s.)
- Working files kept in the folder: `notes_wip.md` (query log and raw candidate notes), `cands.txt` (dedupe input).

## 3. What this family says, in short

1. **Crack and vessel architecture papers rarely beat a well-trained U-Net-type model by more than our M = 0.010, and almost never under a tolerance metric with seeds.** In RSF-Conv's controlled table, CS-Net, FR-UNet, LIOT, SwinUnet and MISSFormer are all at or below plain U-Net++ on DRIVE/STARE/CHASE; the FIVES benchmark (arXiv 2406.14994) finds U-Net matches advanced models when data are sufficient. A Research Square audit argues that crack-module gains on small sets are often seed noise. This agrees with our "no decoder effect" reading.
2. **The two levers that do show up are (a) keeping high-frequency, full-resolution evidence for the thinnest lines and (b) priors that do not depend on contrast or orientation.** FACS-Net (FFT high/low split in the decoder, full-res stem) gives the largest thin-crack gain I found; RSF-Conv (rotation-and-scale equivariant filters) gives its main gain out-of-domain. Both match our HRNet finding and our unseen-module recall gap.
3. **Cross-domain evidence in the crack literature points to training data diversity, not architecture.** FACS-Net's own authors report nnU-Net with broad pretraining as the best cross-domain model on OmniCrack30k. DMSRCrack's leave-one-dataset-out gains over U-Net++ are small and not uniform.
4. **Post-hoc refinement that adds strokes raises recall at a cost in precision.** Curvi-Tracker works at a 2 px slack (our metric family) but follows look-alike lines; on EL those are gridline fingers, busbars and scuffs.

## 4. Top 10

Ranked by expected value for raising crack relF1@2 under our protocol, then cost.

**1. FACS-Net: frequency-aware decoder for thin cracks** — doi:10.1016/j.autcon.2025.106719, Automation in Construction 2026, NEW, full text.
Mechanism: a full-resolution CNN stem feeds skips directly to the decoder; the last decoder stage splits features into low and high frequencies with an FFT Gaussian low-pass (FPCM) and reweights both bands with CBAM.
Evidence: on CrackVision12K, stratified by crack width, it beats Hybrid-Segmentor by 0.306 IoU and 0.360 CTS on the thinnest cracks (≤2 px). The DeepLabV3+ baseline "failed to detect most thin-crack structures". Overall 0.663 IoU. Tolerance: none (strict IoU, CL-IoU, CTS); images resized to 256 px.
Our failure modes: thin-line recall and precision for 1 to 2 px cracks. The FPCM+CBAM block can go into the last U-Net++ decoder stage above the HRNet stem as a new head.
Against: the authors state it does not generalise across domains (nnU-Net was best on OmniCrack30k), so it is not a fix for unseen-module recall. The baseline it beats is a stride-reducing model, not our stride-preserving HRNet. Screen it on CV5 first, then on the new unseen set.

**2. RSF-Conv: rotation-and-scale equivariant convolution** — doi:10.1109/tnnls.2025.3560082, TNNLS 2025, NEW, full text (arXiv), code: github.com/szhc0gk/RSF-Conv.
Evidence: in-domain F1 over plain U-Net is +0.27 (DRIVE), +1.12 (STARE) and +1.10 (CHASE) points, with all baselines given rotation and rescale augmentation. The paper states that out-of-domain (train on one fundus set, test on another) RSF-Conv U-Net and IterNet beat all methods "by a significant margin", mainly in sensitivity. The table values were not in the extracted text.
Our failure modes: unseen-module recall (sensitivity under source shift), small data (fewer parameters). Cracks have any orientation, while our training augmentation is rot90 and flips only.
Against: the filters cannot load ImageNet or HRNet weights. Try it in the decoder only, or in a parallel high-resolution branch, and keep the pretrained encoder.

**3. Local shape descriptors (auxiliary head)** — doi:10.1038/s41592-022-01711-z, Nature Methods 2022, NEW, abstract only.
Evidence: an auxiliary regression of local diameter, elongation and direction next to the main output gave consistent gains across EM specimens, imaging techniques and resolutions, and brought affinity methods level with flood-filling networks.
Our failure modes: thin-line recall. A dense direction and width target around cracks adds supervision beyond the 0.19% crack pixels, and it is easy to compute from our masks. Cheapest item in this list (new head).
Against: 3D neurons, not 1 to 2 px lines. Our auxiliary heads (inactive aux, skeleton recall) helped single models but not ensembles.

**4. Curvi-Tracker: iterative tracking refinement** — doi:10.1016/j.patcog.2025.112797, Pattern Recognition 2025, NEW, full text.
Evidence: run after U-Net, U-Net++ and clDice models on DRIVE, Massachusetts Roads and CrackTree200. Correctness/Completeness/Quality are scored with a 2 px slack. About 10% average improvement on the topology metrics; Completeness rises, Correctness drops slightly, Quality rises. It beats an RNGDet++-based tracker (13 to 23 times faster to train) and morphological closing, which "removes thin structures".
Our failure modes: recall on unseen modules where cracks come out fragmented. It is model-agnostic, so it runs after C2 with no retraining.
Against: on roads the trackers followed look-alike lines (driveways, railways). On EL the look-alikes are fingers, busbar edges and scuffs, so check the 1.5x false-crack guard and the width guard (strokes are jagged). The trackers need their own patch training on our crack masks (new pipeline).

**5. RPCANet++: deep-unfolded robust PCA (low-rank background, sparse object)** — doi:10.1109/tpami.2026.3697815, TPAMI 2026, NEW, full text (arXiv).
Evidence: state of the art on infrared small-target sets and on DRIVE/CHASE/STARE vessels (vessel table values truncated in what I read). On NEU-Seg defects, IoU 80.3 against U-Net 79.3 and EDRNet 80.5, with 1.4 to 4.4 M parameters.
Our failure modes: thin-line precision (gridline fingers and busbars are periodic low-rank background, cracks are sparse) and source contrast shift. The idea is untested in our suite: an explicit background model of the cell.
Against: binary output; not better than U-Net on larger defects. Best tried as an auxiliary crack branch or an input-decomposition stage, not a replacement.

**6. DMSRCrack: dual encoder with detail enhancement, leave-one-dataset-out** — doi:10.1016/j.autcon.2026.107004, Automation in Construction 2026, NEW, full text.
Evidence: one of few crack papers trained on 7 datasets and tested on an unseen 8th against U-Net/U-Net++. Best held-out IoU on DeepCrack (0.406), Rissbilder (0.354) and Crack500 (0.301). U-Net++ is better on the Volker tunnel set, where DMSRCrack recall is only 0.36. Removing the Crack Detail Enhancement Module (Sobel edges plus a predicted thickness map steering a deformable conv on the skip) costs 1.8% recall.
Our failure modes: unseen-source recall. The thickness-gated deformable skip alignment is a small decoder add-on.
Against: gains over U-Net++ are small and unseeded; strict Dice/IoU only.

**7. TopoSAM: background-adversarial twin learning** — doi:10.1016/j.engappai.2025.113688, EAAI 2026, NEW, abstract only.
Evidence: on seven public crack datasets it is reported as best in generalisation. It trains on twin samples with the same crack and different backgrounds.
Our failure modes: unseen modules and half-cut layouts. The useful part is the twin-consistency objective, not the SAM encoder: paste the same crack onto cells from other sources or layouts and penalise disagreement.
Against: our crack copy-paste and synthetic half-cuts gave no confirmed gain. The consistency term is the only new element, and it is untested on EL.

**8. Automatic High Resolution Wire Segmentation (WireSegHR)** — doi:10.1109/cvpr52729.2023.00217, CVPR 2023, NEW, abstract only.
Evidence: a two-stage global (downsampled) then local (full-resolution tiles) segmenter for thin, long, sparse wires, plus the WireSegHR benchmark. The abstract gives no numbers against a single-stage baseline.
Our failure modes: resolution. It is different from our Track M 2x input: only crack-candidate tiles are refined at higher resolution, so compute stays low.
Against: our cells are already 512 px; the gain may be small.

**9. CaPro: SAM adaptation from one unlabelled image** — doi:10.1609/aaai.v40i5.37315, AAAI 2026, NEW, abstract only.
Evidence: tested on medical curvilinear and crack sets with a single unlabelled target image. Synthetic curves are Fourier-style-transferred into the target domain, an oriented sub-curve detector is trained on them, and its filtered boxes become SAM prompts.
Our failure modes: a never-labelled new module source (the new zero-shot set we need). The Fourier style transfer of synthetic cracks into one new cell is the cheap part to reuse.
Against: binary and prompt-based; it will not beat a supervised 24-class model. Treat it as a source of pseudo-labels or augmentation.

**10. FGOS-Net: frequency-aligned anisotropic Mamba scanning** — doi:10.1007/978-3-032-37369-4_28 (arXiv 2603.28503), LNCS 2026, NEW, full text.
Evidence: better than SCSegamba on DeepCrack (clDice 97.1 vs 94.5), CrackMap (92.5 vs 59.9) and the 8-material TUT set. Applied unchanged to CHASE vessels and Massachusetts roads, clDice is +6.05 and +7.46 over SCSegamba.
Our failure modes: crack continuity across texture, which supports recall.
Against: no U-Net-type baseline; mIoU averages crack and background; 256 px resize; a new non-pretrained backbone. Ranked last of the ten because the evidence does not compare it with our model family.

**Evidence against, useful for the decision (not a method):** the FIVES benchmark, arXiv:2406.14994, NEW, abstract only. With enough well-curated data, plain U-Net equals advanced vessel architectures and image quality is the main factor. Read together with item 3 of section 3, it argues against a broad architecture sweep in this family. Only the frequency, equivariance and auxiliary-head ideas above look worth a 2-seed screen.

## 5. NOT_FOUND (known to me, not returned by the tools)

- **CT-CrackSeg**: appears only as a baseline row in FGOS-Net's table. Query 42 ("CT-CrackSeg CrackSeU CrackSegNet") returned nothing.
- **CrackSeU** and **CrackSegNet**: no results in query 42 or in queries 1, 26 and 33.
- **CFD dataset paper** (Shi et al., random structured forests, 2016) and **CrackTree** (Zou et al., 2012): not returned by queries 27 and 33. CrackTree200 is only described inside Curvi-Tracker.
- **UAED**, **PiDiNet**, **SGL**, **CoANet**, **DSCNet**, **SAM-Road**, **FR-UNet**, **IterNet**, **CrackSAM**: found or known but already in MASTER (P184, P330, P019, P139, P104, P482, P026, P127, P264); not re-proposed.
- **WireSegHR full text**: the fetch timed out; abstract only.
- Semantic Scholar was rate-limited for the whole session and arXiv timed out on most queries, so very recent arXiv-only preprints (Oct to Nov 2026) may be missing.
