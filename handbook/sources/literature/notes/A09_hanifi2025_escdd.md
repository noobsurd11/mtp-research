# Hanifi et al. 2025: PV-DDPM (mask-conditioned diffusion for EL images) and the E-SCDD dataset
- **Citation.** Hanifi, Jafarnejad, Köntges, Wentnagel, Kokkas, Frank. "Bridging the Data Gap: Spatially Conditioned Diffusion Model for Anomaly Generation in Photovoltaic Electroluminescence Images". arXiv 2511.09604v1, 12 Nov 2025 (eess.IV), 8 pages. https://arxiv.org/abs/2511.09604
- **Affiliations:** University of Luxembourg (SnT), ISFH Hamelin, SolarCleano.
- **Read:** full text (LaTeX source and PDF), 12 Oct 2026. The PDF is at `papers/hanifi2025_escdd_2511.09604.pdf` (local only).
- **Code:** GitHub `sntubix/pv-ddpm` (README, `dataset.py`, the diffusion model, a copy of the dataset).
- **Data:** HuggingFace `snt-ubix/escdd` (the paper's `snt-ubix/e-scdd` redirects there), plus the mirror `shivahanifi/extended-scdd`.
- **Our audit of the released data:** `results/escdd_audit/README.md`.

## What it claims
- **PV-DDPM.** A DDPM with a cosine noise schedule. A U-Net denoiser gets binary conditioning masks concatenated channel-wise to the noisy image. There are two mask types:
  - a "background mask" (all non-background pixels), which generates multi-defect images;
  - a "feature-defect mask" (features plus one defect class), which generates single-defect images.
- **Training.** Adam, lr 5e-4, batch 8, EMA, early stopping on val loss (patience 10). One model on everything, then fine-tuned per cell type. Padding was removed after expert feedback about dark-edge artefacts. The paper says "1,000 diffusion steps".
- **Generation.** 10 samples per conditioning mask, 1,788 images in total: 70 half-cut multi, 180 IBC, 802 mono, 736 multi.
- **Image quality.** FID/KID computed with a DeepLabv3-ResNet101 fine-tuned on E-SCDD (real images only) as the feature extractor, instead of Inception:

  | Cell type | FID | KID |
  |---|---|---|
  | multi | 2.46 | 0.0008 |
  | mono | 3.24 | 0.0031 |
  | half-cut multi | 4.27 | 0.0009 |
  | IBC | 6.42 | 0.0044 |
  | average | 4.10 | 0.0023 ± 0.0007 |

  Also a PaCMAP plot and an expert visual review of the 20 "most visually realistic" samples per category.
- **E-SCDD.** An extension of "SCDD", which is BenchmarkEL `20221008` (695 images, 29 classes). It adds:
  - a 30th class, `sp multi halfcut` (29), with half-cut multi spacing relabelled from `sp multi`;
  - 110 new real cells from BenchmarkEL's unlabelled pool;
  - 195 annotated synthetic images;
  - 1,768 unlabelled synthetic images.

  Total: "1,000 annotated" images and "151,700 unlabelled" (the related-work table counts the 150k BenchmarkEL pool).
- **Annotation of the new cells.**
  - Done on Roboflow with "Smart Polygon", a Segment Anything model they fine-tuned on SCDD.
  - Three stages: an annotator, a CV specialist with PV expertise, then a senior PV expert's QA.
  - The paper says an annotation-assistant tool (class definitions, examples, search) is in the repo. It was not found in the repo tree on 12 Oct (last push 2025-11-17; `results/escdd_audit/out/provenance/pv-ddpm_github_tree.json`).
- **Downstream.** AA-CLIP (a CLIP-based anomaly detector), with feature classes mapped to background (binary anomaly). Synthetic images were kept in their base image's split.

  | Setting | Data | Pixel AUC | Pixel AP | Image AUC |
  |---|---|---|---|---|
  | full-shot | SCDD | 93.26 | 47.13 | 52.11 |
  | full-shot | E-SCDD | 94.96 | 55.47 | 79.60 |
  | 16-shot | SCDD | – | 39.25 | – |
  | 16-shot | E-SCDD | – | 19.69 | – |
  | 32-shot | SCDD | – | 36.66 | – |
  | 32-shot | E-SCDD | – | 25.69 | – |

## Weaknesses
**Empirical** (checked against the released data, `results/escdd_audit/`):
- **The release does not match the paper.** It has 903 annotated images (693 + 117 `_rf` + 93 synthetic) and no unlabelled synthetic images. The synthetic count is given as 1,768, 1,786 and 1,788 in different sections.
- **"Refined annotations" leave crack and inactive untouched.** Against `20221008`, only spacing classes changed in 66 masks; not one crack or inactive pixel changed. The crack cleaning visible against our `20211104` masks is the BenchmarkEL maintainers' own `20221008` correction.
- **The 93 synthetic images come from 4 base cells,** all in train, and carry 11.7% of all crack pixels.
- **The new `_rf` crack labels include speck-like fragments** (3 cells with 128 to 380 fragments) and 1-px lines (ARTS).

**Reader-inferred:**
- **The AA-CLIP comparison does not isolate the dataset effect.** It reports one number per setting with no seeds. The two test sets differ. E-SCDD is worse at 16 and 32 shots. SCDD's full-shot image AUC of 52.11 is near chance, which suggests an unstable setup.
- **The FID extractor was fine-tuned on the same data,** and the expert review saw only hand-picked samples. Neither shows that synthetic images help a segmentation model.

## Relevance to us
- **Attribution.** Our "revised (E-SCDD) masks" are, for crack and inactive, BenchmarkEL `20221008` masks. Cite Pratt et al.'s release as their source and E-SCDD as the channel we got them through.
- **Extra labelled data** (117 `_rf` cells): 100 of them are in our external unlabelled pool.
- **Mask-conditioned diffusion** is one route to more rare-class training images (inactive), but this paper gives no segmentation evidence for it.
- **SAM-assisted annotation with tiered review** is a possible WattCycle labelling workflow. The speckled `_rf` crack masks show its crack output needs cleaning.
- **Related, not read:** Hanifi et al. 2026, LNCS, "Multi-class ... Applications" (DOI 10.1007/978-981-96-8892-0_4). 29-class segmentation on SCDD with several encoder-decoders, a possible supervised reference on the newer release.
