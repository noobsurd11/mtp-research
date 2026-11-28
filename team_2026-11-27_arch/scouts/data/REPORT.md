# Scout `data`: data and labels (generative data, augmentation, label noise and width, resolution, new EL datasets)

27 Nov 2026. Literature only: no training, no server access. Every number below comes from a paper read through the Research MCP. I say "full text" when I read the paper's sections and "abstract only" when I did not. The full table is in `papers.tsv` (49 rows).

## Tool status
- `search_papers`: OpenAlex and ScienceDirect answered, and Scopus answered sometimes. Semantic Scholar was rate-limited for the whole session. The arXiv back-end timed out on most calls; two arXiv-only queries returned nothing.
- `search_snippets`: one try, rate-limited (Semantic Scholar).
- `fetch_fulltext`: 7 new full texts. Four came from arXiv (Preserve-the-Hard, SynthSeg, vesselFM, Label-Free Liver Tumor) and three from Elsevier (Dhimish 2026, DiffCrack, Akram & Bai 2025). EFSegNet was already in the library. DSDINet was not fetched. Two fetches timed out: arXiv 2407.08209 (curvilinear dataset expansion) and the first vesselFM try, which worked on retry.

## Queries run (45 `search_papers` + snowballing)
1. photovoltaic electroluminescence dataset pixel-level segmentation annotations public (2023+)
2. synthetic data generation diffusion model semantic segmentation training DatasetDM DiffuMask (2023+)
3. half-cut solar cell electroluminescence defect (2021+)
4. mask-conditioned diffusion synthetic image-mask pairs medical segmentation small dataset gain (2023+)
5. crack image synthesis generative model crack segmentation data augmentation (2023+)
6. label noise thin structure segmentation boundary annotation inconsistency vessel width (2022+)
7. sliding window inference versus whole image high resolution segmentation thin structures patch size (2020+)
8. super-resolution preprocessing improves segmentation of small thin objects low resolution images (2020+)
9. domain randomization synthetic training from label maps generalization unseen contrast segmentation (2021+)
10. photovoltaic defect image generation diffusion segmentation mask electroluminescence (2024+)
11. ControlNet synthetic training data segmentation domain generalization rare classes (2024+)
12. solar cell crack segmentation dataset released 2025 microcrack pixel annotation benchmark (2024+)
13. noisy boundary labels segmentation learning tolerance annotation offset loss (2022+)
14. class-aware copy-paste mixing rare class semantic segmentation supervised small dataset (2022+)
15. vessel segmentation foundation model trained on synthetic data domain randomization zero-shot (2023+)
16. procedural synthetic curvilinear structures pretraining segmentation fractal cracks exact labels (2022+; 0 hits)
17. few-shot industrial defect generation diffusion image mask pairs segmentation improvement (2025+)
18. electroluminescence image simulation cracked solar cell physics model synthetic training deep learning (2022+; no relevant hit)
19. elastic deformation augmentation thin structures topology preserving label (2019+)
20. annotation width inconsistency multi-dataset training thin structure segmentation dataset-specific conditioning (2022+)
21. test-time upsampling input resolution effect thin vessel crack segmentation accuracy (2021+)
22. DatasetGAN label-efficient generative model synthesizes annotated images few labels (2021+)
23. crack segmentation inaccurate annotations label correction weakly supervised thin crack (2022+)
24. electroluminescence images dataset photovoltaic modules Data in Brief Zenodo 2025 2026 annotated defects masks (2024+)
25. cross-domain cross-resolution crack segmentation generalization unseen dataset augmentation (2023+)
26. hard sample synthesis segmentation model feedback generative augmentation failure cases (2024+)
27. synthetic data thin structure segmentation diffusion (arXiv only; timed out)
28. electroluminescence solar cell segmentation (arXiv only; timed out)
29. Distribution-aware noisy-label crack segmentation SAM adapter (2023+)
30. mosaic tiling layout augmentation structured periodic background industrial image segmentation (2021+)
31. multi-scale inference test-time augmentation scale segmentation small object recall (2020+)
32. label-free tumor segmentation synthetic tumors handcrafted rules realistic (2022+)
33. Label-Free Liver Tumor Segmentation synthetic tumors (2023+)
34. new dataset photovoltaic cell defect segmentation pixel-level labels publicly available electroluminescence crack finger (2025+)
35. PSCDE polycrystalline solar cell defect segmentation dataset
36. soft segmentation labels averaged across annotations thin structure contrast-agnostic training (2022+)
37. learning segmentation from imprecise annotations label tolerance distance-based loss misaligned thin labels (2023+)
38. RERN rich edge features polycrystalline solar cell defect segmentation dataset public (2022+)
39. half-cell photovoltaic module electroluminescence deep learning crack detection multi-busbar (2022+)
40. scale augmentation resolution randomization segmentation robustness across image resolutions fine structures (2021+)
41. defect removal inpainting hard negative augmentation segmentation false positives (2022+)
42. crack copy-paste augmentation crack segmentation background images synthetic composition (2021+)
43. photoluminescence silicon wafer defect image synthesis generative augmentation segmentation (2021+)
44. uncertainty-guided inpainting context augmentation keep labelled pixels loss only original pixels segmentation (2023+)
45. image-to-image translation style transfer augmentation defect segmentation domain generalization unseen production line (2023+)

Snowballing:
- `get_citations`: CrackSegFlow (12 citers), PV-DDPM / E-SCDD (0 citers), FreeMask (30 of 84), SynthSeg (30 of 1,007), Label-Free Liver Tumor (25 of 159), Chen 2025 "Open data sets for PV reliability" (30 of 36), Chen 2023 JPV LBNL crack set (40 of 55).
- `similar_papers`: on {Preserve-the-Hard, Label-Free Liver Tumor, SynthSeg}.
- `get_paper`: about 30 abstracts.

Full text read (sections named in the table): Preserve-the-Hard (method, results, ablations), SynthSeg (generator, ablations), vesselFM (data-source ablations), Label-Free Liver Tumor (results, ablation), DiffCrack (conditioning, downstream, limitations), Dhimish 2026 half-cut (data, model, data availability), Akram & Bai 2025 (data, results, research-data statement), EFSegNet (datasets).

## Counts
- Records shown by the tools: about 800. Each query shows up to 25 of about 40 to 48 merged results, so many records repeat across queries.
- After dedupe by id and an on-topic filter: about 110 distinct papers judged against our task.
- Kept in `papers.tsv`: 49 rows. 39 are NEW and 10 are already in MASTER (P024, P042, P197, P262, P270, P283, P419, P556, P572, P584). I checked every row against `ref/MASTER.tsv` by id and by normalised title with a script, and checked arXiv ids by grep.
- Already in MASTER and not repeated as rows: P012 GIN-IPA (RUN_NOW), P057 SLAug, P294 Siamese-Diffusion, P105 controllable crack synthesis, P109 FMS2, P118 Fourier-Morphology UDA, P155 UnAICorN, P219 UAV pavement ControlNet, P317 MCPMix, P339 DGSSA, P380 LSDM, P393 UniVG, P454 DualAnoDiff, P512 DGInStyle.

## What the prior sweep already settled (and I did not reopen)
- D06, D21 and D33 cover mask-to-image renderers (CrackSegFlow, PV-DDPM, FMS2, SeaS, AnomalyDiffusion), copy-paste variants (CarveMix, Soft-CP, TumorCP, Synth4Seg), GDI inpainting, rare-class sampling and supervised CutMix.
- D15 to D17 cover noisy-label methods, ridge snapping and annotator-style heads.
- D02 covers the EL dataset census.

My rows add six things: (a) domain randomisation from label maps; (b) rule-based lesion synthesis that matches real labels; (c) uncertainty-guided context regeneration; (d) soft targets for width inconsistency and for label down-sampling; (e) one new half-cut data source; (f) one new public poly-Si set name (PSCDE).

## Top 10

**1. arxiv:2606.31603, Preserve the Hard, Regenerate the Rest (2026, arXiv, code public). Full text.**
- *What the paper did:* for each training image, the classes where the baseline is most uncertain are kept pixel-exact (about 10% of the image). The rest is regenerated by an off-the-shelf inpainter, and the loss is computed only on the kept pixels.
- *Evidence:* on Cityscapes 10% (5 seeds), mIoU went from 69.60 to 71.67, and rare classes gained up to +11.9 IoU. The inpainting is what carries the gain: keeping the uncertain pixels without new context gave only 70.13. Paste-back and the ignore mask each matter. The best settings were τ = 0.10 and a 1:1 synthetic:real ratio, and three iterations reached 72.24.
- *Mapping:*
  - Recall on unseen modules and half-cut layout: real crack and inactive pixels, with their true labels, are shown on new backgrounds. Examples are other sources' textures and multi half-cut pool cells, if the inpainter can produce them.
  - Thin-line precision: generated pixels are never supervised, so the seam-decoy failure of CP100 cannot arise.
- *Caveats:*
  - The inpainter must be EL-capable: LaMa (as in GDI), or PV-DDPM retrained on train cells only (P042).
  - The crack preserve mask must include the dark-line band (about 4 px), not only the 1 to 2 px label.

**2. doi:10.1016/j.media.2023.102789, SynthSeg (MedIA 2023), with doi:10.59275/j.melba.2026-6e4e FetalSynthSeg (MELBA 2026).** SynthSeg full text; FetalSynthSeg abstract only.
- *What the papers did:* the segmenter is trained on images whose per-label intensities, bias field, gamma and simulated resolution are fully randomised, while it always predicts the high-resolution labels.
- *Evidence:*
  - SynthSeg: making the intensity priors more realistic, or domain-specific, cost 1.4 to 2.6 Dice. Removing the bias field cost 3.7 and removing deformation cost 4.3.
  - FetalSynthSeg: plain Gaussian-mixture intensity models beat physics simulation, and splitting classes into intensity clusters helps out-of-domain.
- *Mapping (recall on unseen modules):* our five sources and E1 differ mostly in contrast and blur. The variant worth testing is a hybrid on real cells:
  - per-label-region intensity remap, with crack contrast drawn independently and allowed to be near-invisible;
  - background split into busbar, finger and grain clusters;
  - bias field;
  - random blur plus down/up-sampling.
- *How it differs from P012 GIN-IPA and P057 SLAug:* it is label-conditioned and simulates resolution.
- *Risk:* brain MRI, not 1 to 2 px lines. SynthSeg itself notes a small drop on thin structures at low resolution.

**3. doi:10.1109/cvpr52729.2023.00717, Label-Free Liver Tumor Segmentation (CVPR 2023). Full text.**
- *What the paper did:* hand-built synthetic tumours (deformed shapes, edge blur, texture) were pasted into healthy CT.
- *Evidence:*
  - DSC 59.77 vs 57.51 for real labels (U-Net, LiTS), with no significant difference on Swin UNETR.
  - Higher specificity on external healthy scans.
  - Better small-tumour detection. The ablation shows that small-tumour recall collapses without synthetic small tumours.
- *Mapping:*
  - Rare inactive (42 train cells): it is external evidence that a rule renderer can equal real labels. This supports the D06 inactive rule renderer: a region cut off from the busbars by a drawn crack, darkened by the source-measured ratio, with "inactive touches crack" kept.
  - Recall: generating many faint, short cracks targets low-contrast recall.
- *Risk:* tumours are blobs, and crack renderers must be artefact-free at 1 to 2 px.

**4. doi:10.1016/j.solcom.2026.100196, Dhimish & Lee 2026, half-cut modules (Solar Compass). Full text. MASTER P572, parked as severity; new angle here: data.**
- *What the data is:* 1,000 module EL images of 144-half-cell mono PERC modules, with pixel masks for crack and low-luminescence region and measured I-V. U-Net R34 reached crack Dice 0.82 and LLDR Dice above 0.89.
- *Access:* data "available on reasonable request".
- *Mapping:* it is the only half-cut EL set with pixel crack masks found in this sweep and in D02. It is the natural candidate for the new unseen zero-shot test set that CONTEXT says we now need, and a source of half-cut layouts (low-luminescence is close to our inactive).
- *Risks:*
  - Licence unknown.
  - One module type and one lab.
  - Unknown crack width convention, so it needs a relabel check or tolerant-metric scoring only.
  - Module-level DSLR images must be cropped into cells.

**5. doi:10.1109/cvpr52734.2025.01944, vesselFM (CVPR 2025, code public). Full text.**
- *Evidence (zero-shot on an unseen MRA set):*

  | Training data | Dice | clDice |
  |---|---|---|
  | real only | 65.45 | 63.53 |
  | + domain randomisation | 69.38 | 72.10 |
  | + flow-matching samples | 74.66 | 75.27 |

  - Drawing the generator's masks from a synthetic mask generator instead of real masks gave +4.54 Dice, which the paper attributes to annotator errors in real masks.
  - Synthetic-only training was poor (domain randomisation alone 55.34; flow samples alone 14.33).
- *Mapping:* recall and connectivity on unseen domains for thin structures; generator-drawn exact masks sidestep our width and jitter inconsistency. Synthetic data works as a complement, not a replacement.

**6. doi:10.1016/j.media.2025.103473, Contrast-agnostic soft segmentation of the spinal cord (MedIA 2025). Abstract only.**
- *What the paper did:* the soft ground truth is the average of the binary masks over 6 contrasts, trained with a regression loss.
- *Evidence:* lower cross-contrast variability (p<0.05) and better generalisation to unseen sites, vendors and contrasts.
- *Mapping (thin-line precision and cross-source transfer):* our crack label width is a per-source convention (1.5 to 3.25 px). One soft target per crack would be the average of its skeleton rendered at every source's width convention, trained with a soft/regression loss. That removes the incentive to learn source-specific widths.
- *Risks:* the averaging is over synthetic widths, not real raters; the crack-width guard (0.85 to 1.15) must be re-checked.

**7. doi:10.26599/cvm.2025.9450470, Soft-labelling for label down-sampling (CVM 2026). Abstract only.**
- *What the paper did:* labels are down-sampled to soft class proportions instead of nearest-neighbour. It beats other down-sampling strategies and preserves under-represented classes.
- *Mapping (resolution handling):* nearest-neighbour label resampling deletes 1 to 2 px cracks. Any scale augmentation, multi-scale training, or the SynthSeg resolution randomisation in item 2 needs soft label resampling to keep crack supervision. It is a cheap prerequisite, not a standalone arm (we train on fixed 512 px crops today).

**8. doi:10.1016/j.patcog.2026.113771, DiffCrack (Pattern Recognition 2026). Full text.**
- *Evidence:*
  - Replacing real CrackTree260 images with synthetic ones raised precision but lowered recall and F1.
  - Fine-tuning on 1,000 synthetic images raised F1 on EdmCrack600 complex scenes by 17 to 28 points (3 backbones, 3 seeds).
  - The paper says masks that are too narrow give too-subtle cracks (it normalises widths to 20 to 23 px).
- *Mapping:* a warning plus a design rule.
  - Synthetic cracks can trade recall for precision, and recall on unseen modules is our weak point, so every synthetic crack arm must be judged on relR@2.
  - Per-sample width/contrast control is how to cover faint cracks.
  - Latent diffusion is unlikely to render 1 to 2 px EL cracks.

**9. doi:10.1109/cvpr52733.2024.01060, Towards Generalizable Tumor Synthesis (CVPR 2024). Abstract only.**
- *What the paper did:* a diffusion model trained on few tumours from one organ generates small tumours in other organs.
- *Evidence:* segmenters trained on these synthetic tumours generalise across demographics, protocols and hospitals.
- *Mapping:* same shape as our problem (few labelled defects, unseen modules). It supports training one defect generator on all five sources and rendering small, faint defects onto target-type pool cells. Risk: latent blur for cracks (keep it for inactive).

**10. doi:10.1016/j.apenergy.2026.128093, DSDINet / PSCDE (Applied Energy 2026, code public). Abstract only.**
- *What it gives us:* the evaluation uses a "public polycrystalline silicon defect segmentation dataset PSCDE" that is not in the D02 census.
- *Mapping:* a possible extra poly-Si pixel set, either as extra training data with its own head or as an extra unseen test.
- *Open points:* I could not find its hosting or licence with the tools. It is likely related to RERN (P197), but that is not verified.

Runners-up:
- `arxiv:2406.01264` FreeTumor, `doi:10.52202/079017-2126` MaskFactory and `doi:10.1016/j.media.2023.102937` YoloCurvSeg: skeleton supervision plus synthesis is a route around width conventions.
- `doi:10.1016/j.energy.2025.139611` (Akram & Bai 2025): the only other open EL generator (Hugging Face `mwaqarakram/PVEL-Text-to-image-Generator-1/-2`). Full text read: module-level and boxes only; crack and low-cell recall stayed low.

## Suggested order (my judgement)
1. Request the Dhimish half-cut data now; it costs no GPU and it is the test set the protocol needs.
2. Cheap arms on PF / C2:
   - the SynthSeg-style hybrid intensity and resolution randomisation (with soft label down-sampling from item 7);
   - the multi-width soft crack target (item 6).
3. Then Preserve-the-Hard with LaMa as inpainter, which shares the inpainting pass with GDI (D21 arm 4).
4. Rule-based inactive synthesis (item 3), judged by module-grouped CV for inactive.

## NOT_FOUND
- **Public EL dataset with half-cut cells and pixel masks (2023 to 2026):** none open. The only one found is Dhimish 2026, on request.
- **Open physics simulator of EL images of cracked c-Si cells:** none. Query 18 had no relevant hits, which agrees with D06.
- **Super-resolution as preprocessing for EL crack segmentation:** nothing found beyond D08's notes. The only crack SR+DA paper is interactive (doi:10.1016/j.autcon.2025.106141).
- **Controlled study of sliding-window vs whole-image inference for thin structures:** none found (query 7). For input resolution, the 2026 retinal study (doi:10.1007/s10278-026-02135-3) has no abstract in the index and was not read.
- **Elastic or grid distortion validated on 1 to 2 px labels:** none found, same as D21. The only thin-crack elastic use deforms skeletons before rasterising (D21 row 11).
- **Geometric layout synthesis (half-cut, tiling) for structured industrial images:** nothing found (query 30).
- **"Enriching Information ... Expanding Curvilinear Object Segmentation Datasets" (ECCV 2024, arXiv 2407.08209):** found, but the abstract is not in the index and the full-text fetch timed out. Read it when arXiv responds.
- **PSCDE dataset hosting and licence:** only named in the DSDINet abstract (queries 35 and 38).
- **Licences not verifiable with the tools:** the Akram Hugging Face weights, the Dhimish data, PSCDE, and the vesselFM, Preserve-the-Hard and DIDEX repositories (repo links come from the papers; the pages were not opened).
- **Not searched separately:** AnyStar, which vesselFM cites as a SynthSeg extension to star-convex instances. It is not relevant to thin cracks.
