# D04. Multi-modal PV inspection: EL with thermal IR, PL, UVF, visible (scout report, 12 Nov 2026)

Scout: literature agent for D04. Tools: Research MCP (OpenAlex answered most calls; Scopus and ScienceDirect returned HTTP 401, Semantic Scholar was rate-limited, so search_snippets failed every time), WebSearch for code and datasets. No servers, no data touched.
Labels: R = what a paper measured, E = what our files measured (from BRIEF), S = my judgement.

## Bottom line (S)
- No paper in this direction has a registered, labelled EL + IR / PL / UVF cell-level dataset. Every "multimodal PV" detection paper found uses visible + thermal drone images, or pairs images that were never taken of the same module (Almukhtar 2026 matches ELPV cells to unrelated RGB modules). Our 478 labelled cells have no second modality. Fusion and cross-modal distillation in the strict sense cannot be run on our data this month.
- What can be used: (1) unpaired cross-modal / multi-source training (shared kernels, per-source or per-modality normalisation), which also covers our 5 EL sources; (2) physics that links cracks to inactive area (crack-bounded isolated regions), a cheap structural prior for inactive; (3) public module EL + power data from the same lab family as ELPV / BMRK, usable as target-like unlabelled data and as weak supervision for inactive area; (4) severity papers (power loss from inactive area, crack nomenclature) that shape the benchmark's severity extension.
- Thermal: BRIEF row "Thermal" stands. Doll 2021 (R) imaged the same defects with PL, IR, EL and UVF: cracks show in PL only under certain conditions; thermal sees disconnected areas and hot spots. Nothing found changes the desk-study verdict that thermal does not help thin-crack segmentation.

## Queries run (37 searches + 3 snowball calls + 10 web searches, over two sessions)
Research MCP search_papers (year_from 2020 unless stated):
1. electroluminescence infrared thermography fusion photovoltaic deep learning (timed out, 0)
2. multimodal PV module inspection dataset EL IR registered
3. photoluminescence electroluminescence deep learning solar cell defect
4. UV fluorescence cracks photovoltaic modules deep learning
5. electroluminescence infrared thermography fusion photovoltaic
6. electroluminescence thermal image translation generative photovoltaic module
7. daylight outdoor photoluminescence imaging photovoltaic modules crack detection
8. series resistance image dark saturation current electroluminescence deep learning solar cell
9. module power prediction electroluminescence inactive area cracks deep learning
10. lock-in thermography solar cell deep learning defect (run twice)
11. UV fluorescence imaging cell cracks PV modules field detection
12. electroluminescence two bias currents ratio image series resistance isolated cell area crack module
13. infrared thermography electroluminescence comparison cracked cells hot spot isolated area power loss
14. cross-modal knowledge distillation segmentation privileged modality training only
15. photovoltaic infrared electroluminescence image registration multimodal dataset drone
16. simulated electroluminescence images solar cell cracks finite element synthetic training data
17. empirical digital twin solar cell measurement images self-supervised representation PL EL
18. multimodal photovoltaic module inspection dataset electroluminescence thermal
19. photoluminescence imaging silicon solar cell deep learning crack (all sources timed out)
20. UV fluorescence photovoltaic module cracks imaging
21. photoluminescence images silicon wafer solar cell convolutional neural network
22. daylight electroluminescence photoluminescence outdoor imaging PV modules
23. image-to-image translation electroluminescence thermal infrared solar module
24. learning using privileged information semantic segmentation missing modality distillation (2021+)
25. luminescence images solar cells deep learning defect localization weakly supervised (2021+)
26. cell cracks inactive area power loss electroluminescence quantification
27. multimodal fusion EL IR solar panel defect segmentation cross-modal attention (2025+)
28. OpenUVF ultraviolet fluorescence crack detection cells machine learning DuraMAT (no year bound)
29. electroluminescence images different injection currents series resistance cracks isolated cell regions (2019+)
30. daylight electroluminescence deep learning crack segmentation noise (2024+)
31. photoluminescence electroluminescence half-cut cells field modules dataset machine learning (2022+)
32. generative adversarial network defect-free luminescence image reconstruction solar cell loss analysis (2021+)
33. unpaired multi-modal segmentation knowledge distillation shared convolution separate batch normalization (2019+)
34. photoluminescence electroluminescence solar module deep learning (2025+)
35 to 37. search_snippets: PL vs EL appearance of isolated areas; UVF cracks vs EL; thermal vs EL for inactive cells (all rate-limited, no result)

Snowball: similar_papers(Hoffmann 2021 pip.3416 + Chen 2023 JPV), get_citations(Hoffmann 2021 pip.3416), read_paper on the Chen 2025 open-data review (image sections) and on STC-Net (method, power loss).
WebSearch: paired EL IR PV dataset 2025; UVF PV crack DL paired EL; OpenUVF repo; Buratti Joule 2022; UMMKD code; MS-Net code; PV-Vision code; Hoffmann elpvpower code; PV-Hawk code; DuraMAT field PL dataset.

## Selected papers

| # | id | year | venue | code | mechanism | adaptation to our data | score | bench |
|---|---|---|---|---|---|---|---|---|
| 1 | doi:10.1109/tmi.2020.2974574 (MS-Net, Liu et al.) | 2020 | IEEE TMI | github.com/liuquande/MS-Net (TF1, web-verified) | One network for several heterogeneous sites: shared conv kernels, site-specific BN, site-specific auxiliary branches and multi-site knowledge transfer | Treat ARTS, CFVS, CSIR, BMRK, SDLE as 5 sites in the house U-Net++ (PyTorch re-implementation of the BN part only). Source id is known for every train / val / test / E1 cell. E1 is 101 CSIR + 5 BMRK, so E1 uses the CSIR / BMRK branches. Optional 6th site: UCF-EL joint training (never tried jointly). | 55 | 40 |
| 2 | doi:10.1109/tmi.2019.2963882 (UMMKD, Dou et al.) | 2020 | IEEE TMI | github.com/carrenD/ummkd (stated in paper, web-verified) | Unpaired CT + MRI segmentation: share all conv kernels, keep modality-specific normalisation, add a KL loss aligning per-class prediction distributions (class prototypes) across modalities | Train EL (our 478 cells) jointly with crack-labelled cells of another modality with no pairing: OpenUVF (3000 labelled UVF crack cells, see #7); UCF-EL can be a second EL "modality". Crack class only for UVF; KL prototype loss on crack and background. Tests whether crack shape knowledge transfers across modalities without fine-tune erasure. | 40 | 30 |
| 3 | doi:10.1109/jphotov.2023.3249970 (Chen et al., PV-Vision) | 2023 | IEEE JPV | github.com/hackingmaterials/pv-vision (web-verified; pip package) | U-Net crack / busbar / dark-area segmentation, then crack features (length, isolated area) for degradation studies | (a) Physics prior for inactive: inactive lies in regions cut off by cracks, busbars and the cell edge (99% of our inactive regions touch a crack label, E). Build crack-bounded regions from predicted crack + busbar + border masks; relabel a region inactive when its mean EL is below a source-wise fraction of the cell median. (b) Open baseline for the benchmark suite. | 50 | 70 |
| 4 | doi:10.1109/pvsc48317.2022.9938503 (Chen, Karin, Jain) | 2022 | IEEE PVSC | same repo as #3 | Worst-case (maximum) inactive area predicted from detected cracks and busbar geometry | Severity output for the benchmark: per-cell "potential inactive fraction" from predicted cracks, reported next to the measured inactive fraction. Also the region generator for #3. | 35 | 60 |
| 5 | doi:10.1002/pip.3416 (Hoffmann et al.) | 2021 | Prog. Photovolt. | github.com/ma0ho/elpvpower (web-verified); data Juelich DATA doi 10.26165/JUELICH-DATA/TVWUUP (web-reported) | 719 module EL images with measured Pmpp; CNN regresses power (R: MAE 7.3 W, 3.2%), CAM variant gives per-cell power loss; inactive regions and cracks dominate loss | Same lab family as ELPV, which is our BMRK source (weak: crack 0.379, inactive 0.324, E). (a) Cut modules into cells: BMRK-like unlabelled pool for BN statistics / pseudo-labels; (b) weak supervision: module Pmpp loss as a bag label for the summed predicted inactive fraction (ranking loss over module pairs); (c) severity validation: does our predicted inactive fraction track measured power loss? | 45 | 75 |
| 6 | doi:10.1016/j.joule.2022.05.001 (Buratti et al.) + doi:10.1109/pvsc43889.2021.9518512 | 2022 / 2021 | Joule / IEEE PVSC | none found | A GAN reconstructs a defect-free luminescence image; the difference to the real image isolates the defect and quantifies its efficiency loss | Anomaly prior (never tried here, BRIEF s5). Train a masked inpainting model on the 11.9k pool; feed the residual abs(EL - recon) as a second input channel. Aimed at E1, where 70% of crack pixels get p(crack) < 0.001 (E): the residual does not depend on the learned full-cell layout. Risk: scuff streaks are anomalies too. | 40 | 30 |
| 7 | doi:10.1016/j.apenergy.2025.126132 (Chen et al., open PV data review) | 2025 | Applied Energy | n/a (review) | Inventory of open PV image data. R (read in full text): OpenUVF has 50 labelled + 100 unlabelled module images and 3000 labelled + 21,600 unlabelled UVF cell images aimed at crack detection; NREL field PL has 856 half-cut cell images (4056 x 3040); EL sets from LBNL, NREL, EPRI, Sandia, FAU, PVEL-AD, Wits, UCF, CWRU | Source of the only crack-labelled second modality (OpenUVF) for #2, and of half-cut luminescence images (NREL field PL) as unlabelled half-cut context for E1. For the benchmark: the reference list of EL sets to check for leakage and to add as external tests. | 35 | 65 |
| 8 | doi:10.1016/j.dib.2026.113109 (Polenghi et al.) | 2026 | Data in Brief | data CC BY (download link not checked) | Pixel-aligned EL + NIR + visible HDR of the same cells after staged damage (impact, cuts, abrasion, scrapes, bending, cracking, heat), with Isc / Voc per stage | Only registered EL + visible + electrical set found. (a) Abrasion / scrape stages show how surface scuffs look in EL vs real cracks: candidate hard negatives for E1 scuff streaks; (b) tiny severity check: our inactive fraction vs measured Isc drop. One poly cell type, test-only. | 25 | 35 |
| 9 | doi:10.1109/ictas64866.2025.11155421 (Pratt, May, Mkasi) | 2025 | ICTAS | none | CSIR (our CSIR source; Pratt built BenchmarkEL) re-trained its 24-class model with 24 "brightening" samples, segmented 48,960 cells of 680 modules into 29 classes; module-mean brightening explains 42% of fill-factor variance (R) | Benchmark severity design: the BenchmarkEL class set already links to module electrics at CSIR. A severity track can report per-module class fractions vs FF / Pmpp, if CSIR shares the 680-module electrical data (needs user OK). | 20 | 70 |
| 10 | doi:10.1051/epjpv/2024039 (Jaeckel et al.) | 2024 | EPJ PV | n/a | Industry nomenclature (PV-Riss project) for EL observations: single cracks, multi-cracks, electrical-circuit anomalies, misc; classification proposal tied to power-loss and safety risk | Defines crack-mode labels for a severity extension (crack without isolation, crack with partial isolation, isolated area). The benchmark can derive crack mode from our crack + inactive masks without new labels. | 15 | 75 |
| 11 | doi:10.1051/epjpv/2026017 (Hashem et al.) | 2026 | EPJ PV | n/a | 230 mono-Si mini-modules (full-cell PERC, half-cut TOPCon, 2 to 12 busbars): crack length and number are not universal predictors of power loss; TOPCon shows no correlation (R) | Severity design: do not score severity from crack length. Use inactive (isolated) area as the severity driver. | 5 | 60 |
| 12 | doi:10.1016/j.matlit.2026.100093 (Peng, Chai, Lan) | 2026 | Matter & Light | none found | Device-physics inversion turns one luminescence image into a quantitative power-loss map; 300 modules, module-power error down to 0.5% (R) | Physics reference for a "power-loss band" severity output from one EL image. Our cells lack calibrated intensity and electrical data, so design guidance only. | 10 | 55 |
| 13 | doi:10.1109/pvsc59419.2025.11132985 (Del Prado Santamaria et al.) | 2025 | IEEE PVSC | none found | Benchmarks an analytic (bELMO) and an ML (DTU) power-loss model for cracked cells under dark lab vs daylight EL and two camera resolutions; error grows for severe cracks and high irradiance (R) | Benchmark protocol: report severity metrics per severity band; daylight / low-resolution as a robustness axis for WattCycle's future drone EL. | 10 | 55 |
| 14 | doi:10.1002/solr.202500592 (Javier et al.) | 2026 | Solar RRL | none found | Network trained on simulations splits one EL image into a qualitative PL (recombination) image and a series-resistance image | Bold bet: inactive and disconnected areas are Rs / isolation effects, material defects are recombination. An Rs-like channel could separate inactive from dark material / edge_dark. Needs their weights or a cell simulator; neither found. | 20 | 20 |
| 15 | arxiv:2608.01714 (STC-Net, Gunasekara et al.) | 2026 | arXiv / MERCon | none found | Fixed Sobel edge prior + Fourier high-pass "spectral" prior injected into the decoder; inactive proxy = dark-percentile pixels inside a dilated predicted-crack zone; power loss linear in that area | Cheap arm: Sobel and high-pass maps as extra input channels. The inactive proxy is a simpler form of #3. Weak evidence (R: PVEL-S, test mIoU 72.5, no electrical validation). | 25 | 30 |
| 16 | doi:10.1002/advs.202300206 (Liu et al.) | 2023 | Advanced Science | none found | CNN denoiser for luminescence images (R: PSNR +30%, SSIM +39% over classical denoisers) | (a) Noise-robustness test split for the benchmark (simulated low-exposure / daylight EL on test cells); (b) denoising noisy sources (CSIR_00070-type cells) before inference. Intensity normalisation failed here (E); denoising is a different operation. | 15 | 35 |
| 17 | doi:10.1109/jphotov.2021.3099739 (Doll et al.) | 2021 | IEEE JPV | n/a | Outdoor PL on full modules; same defects imaged with PL, IR, EL, UVF: 5 of 7 defect types visible in PL, cracks only under some conditions, interconnection failures not at all (R) | Physics reference for WattCycle deployment and the benchmark's modality notes: cracks need EL (or PL with current extraction); thermal or PL alone will not replace EL for crack segmentation. | 5 | 25 |

## Minimum experiments (cheapest decisive test per paper)
Judge on module-grouped 5-fold CV over the 532 train + val cells (fold roots exist), then clean-49 test and E1 only after CV passes. Seed rule as in BRIEF.
- #1 MS-Net source BN: arm = house U-Net++ with per-source BN (5 sets), PF fine-tune; baseline = PF. Metrics: CV crack relF1@2, inactive IoU, BMRK-only crack IoU; E1 crack recall. Kill if crack relF1@2 and inactive IoU both change < +0.01 and BMRK crack IoU < +0.02. About 5 folds x 2 arms x 2 seeds x 1.1 GPU-h = 22 GPU-h.
- #2 UMMKD with OpenUVF: arm = PF + joint batches of OpenUVF crack cells (own BN, KL prototype loss); baseline = PF. Metrics: CV crack relF1@2, E1 crack recall. Kill if both < +0.01. Download needs user OK. About 25 GPU-h.
- #3 / #4 crack-bounded inactive prior: post-processing only. Arm = house 5-seed ensemble + region rule; baseline = same ensemble. Metric: CV inactive IoU and inactive relR; tune the darkness threshold on CV folds only. Kill if inactive IoU < +0.02. Under 2 GPU-h plus CPU.
- #5 Hoffmann EL power: step 1 (decisive, cheap): run the house model on cell crops of the 719 modules, sum predicted inactive per module, Spearman vs measured power loss; kill the weak-supervision idea if rho < 0.3. Step 2: weak-sup arm (ranking loss on module pairs) vs PF on CV inactive IoU and BMRK inactive IoU; kill if < +0.02. About 2 + 25 GPU-h. Download needs user OK.
- #6 residual prior: arm = inpainting U-Net on the 11.9k pool (about 10 GPU-h) + house model with 2-channel input (EL, residual); baseline = house. Metrics: E1 crack recall and relF1@2, CV crack relF1@2 as guard. Kill if E1 crack recall < +0.03 or CV relF1@2 drops > 0.01. About 25 GPU-h.
- #8 Polenghi scuff negatives: download (open, CC BY, needs user OK), check whether abrasion EL looks like E1 scuff streaks; if yes, paste as background-labelled negatives. Arm vs PF on E1 crack relP@2 in half-cut cells. Kill at the visual check or if E1 relP@2 < +0.02.
- #14 Javier: only if weights become public; arm = PF with predicted Rs channel; metrics CV inactive IoU and material IoU; kill if both < +0.01.
- #15 STC-Net priors: arm = house with 3-channel input (EL, Sobel magnitude, high-pass); baseline = house; metrics CV crack relF1@2 and crack IoU; kill if < +0.01. About 11 GPU-h.
- #16 denoiser: benchmark use only; build a noise-degraded copy of the test set and report every method's drop. No training kill line.
- #9 to #13, #17: benchmark design, no training run; cost is writing the severity protocol (crack mode from masks, inactive fraction, power band) and, for #9 and #5, asking for electrical data.

## Prior overlap with BRIEF section 5 (honest check)
- #1, #2: "per-panel BN adaptation (fail)" was test-time BN adaptation; "separate BN" in the SSL row split labelled vs unlabelled batches. Training-time per-source BN and joint multi-dataset training are listed as never tried. Open.
- #3, #4, #15 inactive proxy: no post-processing or structural prior for inactive was run. Open.
- #5: "SSL with 11.9k external pool n.d. at 100%" used CSIR / ARTS cells, not BMRK-like data, and no electrical weak labels. Open; the SSL part alone carries a weak prior from that null.
- #6: MIM / DDeP pretraining (n.d.) learned features from reconstruction; feeding the residual as an input channel was not run. "Anomaly-detection priors" is on the never-tried list. Open.
- #15 extra channels: not run. 2x resolution (n.d.) is unrelated.
- #16: intensity normalisation (fail) is not denoising. Open for benchmark use.
- Thermal: desk study only; still no experiment possible without paired cell-level data.

## Notable papers rejected (one line each)
- doi:10.3389/feart.2025.1702396 Almukhtar 2026 (RGB + IR + EL Mask R-CNN): "pairs" are ELPV cells matched to unrelated RGB modules by class; no physical pairing.
- doi:10.1109/access.2025.3640579 He 2025 (visible + thermal cross-modal attention segmentation): needs registered visible + thermal pairs; we have neither for labelled cells.
- doi:10.1038/s41598-025-28603-4 Yu 2026 Photovoltaic-DETR: separate IR / visible detection datasets, module-level boxes, not EL.
- doi:10.1109/isitia71267.2026.11642343 Fengguo 2026: 359 EL and 569 IR images with weak boxes, not registered pairs.
- doi:10.1109/lra.2023.3247175 CEKD 2023 (RGB-T teacher, thermal-only student): no privileged modality at train time; the only candidate (native high resolution) already gave n.d. at 2x.
- doi:10.1016/j.solener.2026.114376 Kunze 2026 digital twin (EL + PL + thermography to j0 / Rs): inline industrial cells with several measurements per cell; nothing transfers to field EL cells.
- doi:10.1109/pvsc59419.2025.11133222 Li 2025 (ChatGPT / Gemini zero-shot PV faults): image-level classification, F1 0.97 on easy cases; no pixel output.
- arxiv:2108.13640 Hoffmann 2021 PL power: useful only for a future PL camera at WattCycle; inactive regions from regression maps, not segmentation.
- doi:10.1002/pip.3900 Laot 2025 physics-based ML EL models: needs voltage-dependent EL series.
- doi:10.1109/jphotov.2019.2961781 Koentges 2020 UVF review and doi:10.1002/solr.202400566 Buerhop-Lutz 2024 UVF: UVF shows crack history and encapsulant ageing; physics context for #2, no method.
- Daylight EL / PL acquisition papers (doi:10.1109/jphotov.2020.2978068, doi:10.1002/pip.3807, doi:10.1002/solr.202400654, doi:10.1063/5.0097576): hardware; relevant only to WattCycle's future rig and a benchmark robustness axis.
- doi:10.1002/pip.3448 Bommes 2021 and PV-Hawk (github.com/LukasBommes/PV-Hawk, web-verified): drone IR module extraction; deployment tooling for WattCycle's thermal camera, no effect on EL scores (D05 territory).

## Gaps
- search_snippets never ran (Semantic Scholar rate limit), so physics claims about how isolated areas look in PL vs EL, and UVF crack visibility vs EL, are not verified from text.
- No registered, cell-level, labelled EL + IR or EL + PL dataset was found.
- OpenUVF repository URL (southern-company-r-d/OpenUVF) came only from a web-search summary: unverified. Label format of the 3000 UVF crack cells not checked.
- That the Hoffmann 719-module data share camera / lab with ELPV (BMRK) is my inference from shared authors, not verified.
- Lueer 2023 (doi:10.1016/j.solmat.2023.112621) on what a power-regression CNN learns from EL had no abstract in the index; worth reading for the severity track.
- Sub-direction worth its own search: weak supervision of segmentation from module-level electrical labels (bag / count / area regression losses), the general mechanism behind #5.
- Sub-direction: inactive-region structural priors (region growing on crack graphs, crack-mode classification).
