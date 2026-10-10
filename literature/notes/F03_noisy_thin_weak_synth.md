# F03: training methods that fit our label facts, beyond SSL

**Scope:** noisy, misaligned or omitted annotations; thin-structure losses; weak or mixed supervision; synthetic defects; active learning.
**Date:** 10 Oct 2026. AI-compiled (fork scout, about 1 h). Every link was retrieved in this pass.
**Read scope per entry:**
- **abs**: arXiv abstract page only.
- **sec**: sections or tables of the full text read.
- **search**: a search snippet only, not verified beyond it.

**Tags:** [ours] = our measured facts; [auth] = the authors' claim; [inf] = my inference.

## Our label facts this note is matched against [ours]

**BenchmarkEL crack labels:**
- About 1.75 px wide, drawn on a visible line of about 4 px.
- Placed with about ±1 px jitter; only 48% of label points lie within 1 px of the darkest pixel.
- Dotted along continuous cracks in 22 images.
- Two annotations of the same image agree at 0.257 IoU.

**Fitting on training images (P1):**
- Training augmentation (blur kernels 3–7 px, ±5° rotation) is the main fitting cap: crack AP 0.93 without it, 0.59 with it.
- CE + Dice fits crack to 0.86 IoU.

**UCF-EL:**
- Crack is a region class.
- Contact labels are loose boxes (twin agreement 0.25).
- Interconnect and corrosion appear in only 44 and 12 test images.

The two BenchmarkEL noise types map exactly onto the classic **registration noise** (jitter) and **omission noise** (dotted labels, missed cracks) of Mnih & Hinton 2012.

---

## 1. Noisy, misaligned and omitted annotations

| Paper | What it does | Evidence | Fit to us | Read |
|---|---|---|---|---|
| **Mnih & Hinton, ICML 2012**, "Learning to label aerial images from noisy data" (https://www.cs.toronto.edu/~vmnih/docs/noisy_maps.pdf, https://mlanthology.org/icml/2012/mnih2012icml-learning/) | Two robust losses for road maps:<br>(i) **asymmetric Bernoulli omission noise**: a 1 in the label is trusted, a 0 may be a missed road;<br>(ii) a **translational noise model**: the label patch may be shifted by one of 8 local translations, and EM marginalises over the shift | Precision/recall curves: large gains on URBAN2, which has registration problems [auth] | **Direct analogue**: dotted crack labels are omission noise and ±1 px jitter is registration noise. A modern equivalent is cheap (a soft-min over shifted label maps) [inf] | sec (§4–5, figures) |
| **STEAL**, Acuna, Kar, Fidler, CVPR 2019 (arXiv 1904.07934) | Thin-boundary detector with a normal-direction NMS loss, plus **active alignment** that re-aligns noisy boundary labels during training through level sets | +4% MF(ODS), +18.6% AP over CASENet on SBD/Cityscapes boundaries [auth]. The learned model refines coarse labels | The closest published method to "1–2 px lines placed with jitter". Boundaries ≈ crack lines [inf]. Code is inference-only | abs |
| **ADELE**, Liu et al., CVPR 2022 (arXiv 2110.03740, github Kangningthu/ADELE) | Networks first fit clean pixels, then memorise noisy ones. **Memorisation starts at different times per class**; ADELE detects the onset per class from IoU curves, then corrects labels, with multi-scale consistency | Medical task with synthetic noise; PASCAL WSSS state of the art [auth]. The authors warn of marginal or negative effect when initial labels are poor | Per-class onset suits our case: crack and inactive have opposite noise regimes. Our P1 trajectories (all arms still improving at 3k steps; seed dips) are the data to check for this [inf] | abs |
| **T-Loss**, Gonzalez-Jimenez et al., MICCAI 2023 (arXiv 2306.00753) | Student-t NLL with a learned robustness parameter | Dice gains on ISIC and lung under simulated noise [auth] | Drop-in loss; generic, not thin-aware | abs |
| **SVLS**, Islam & Glocker, IPMI 2021 (arXiv 2104.05788) | Spatially varying label smoothing: one-hot labels convolved with a Gaussian, so boundaries become soft and the interior stays hard | Better calibration and boundaries on 4 clinical tasks; handles multiple raters [auth] | Turns a 1.75 px line into a soft ~4 px band, matching visible width plus jitter. For a 2 px line almost every pixel is "boundary", so SVLS ≈ a Gaussian heatmap target [inf] | abs |
| **Zhang, Tanno et al., NeurIPS 2020** (arXiv 2007.15963) | Annotator confusion matrices jointly with the true segmentation, from noisy labels alone | MS lesion, BraTS, simulated and real multi-annotator data [auth] | We have "multiple annotators" for free:<br>• BenchmarkEL versions 20211104 / 20221008 / E-SCDD (the README says later versions contain "corrections to earlier versions of the same images");<br>• the 702 UCF twin pairs [ours + inf] | abs |
| **Fobi et al. 2020** (arXiv 2005.13180); **AnS 2026** (arXiv 2607.10841) | Alignment-correction network for misaligned map labels (needs a small verified set). AnS learns an affine label alignment with a spatial transformer, with no golden labels | AIRS mIoU 0.79 [auth]; AnS is robust to synthetic high noise [auth] | Global and affine misalignment; our jitter is local and non-rigid, so the fit is only partial [inf] | abs |
| **Distribution-aware noisy-label crack seg** (arXiv 2410.09409) | SAM-Adapter plus distribution-aware semantic knowledge against omitted or mislabelled cracks | Pavement datasets; unseen CFD [auth] | Shows that "crack labels omit cracks" is a known problem. Uses SAM, too heavy for deployment [inf] | abs |
| **Inoue & Nagayoshi, Weakly-Supervised Crack Detection**, IEEE T-ITS 2023 (arXiv 2206.06743) | Deliberately coarse, fast annotation plus a data-driven label refinement (falsely labelled pixels look like background) | 10–30× faster annotation at comparable accuracy [auth/search] | Template for a **cheap WattCycle annotation protocol** (thick or loose crack strokes, refined automatically) [inf] | abs |
| **Li et al., Front. Med. 2026**, "Few-shot annotation correction for lightweight retinal vessel segmentation" (doi 10.3389/fmed.2026.1682878) | Measures thin-vessel degradation under positional label deformation | DRIVE: F1 0.817 → 0.575 and sensitivity −31% at noise level 0.8, while accuracy falls only 3% [auth] | Confirms that thin structures lose recall and F1 first under positional noise, while accuracy hides it [inf] | sec (abstract + one table, via fetch) |

Also relevant, search level only:
- Study Group Learning for noisy vessel labels (arXiv 2103.03451).
- Iterative label correction for vessels (BMC Med Imaging 2021, doi 10.1186/s12880-021-00732-y).
- SynCrack controlled annotation noise (SciTePress 2022).

## 2. Thin-structure supervision beyond clDice / Skeleton Recall

- **Negative evidence on Skeleton Recall** (Arora, Kumar, Gupta, arXiv 2508.11374, 2025; sec):
  - Setup: nnU-Net with Dice + CE vs + SRL, 5 seeds.
  - On a concrete **Cracks** dataset: DSC 76.64 → 76.94 (n.s.), clDice 85.67 → 86.21 (n.s.), FNR 20.2 → 17.1 (sig.), **FPR 0.25 → 0.31 (sig. worse)**.
  - Significant on only 3 of 15 tubular metrics.
  - Their theory: the SRL gradient is constant on the tubed skeleton and independent of the prediction, and false positives are never penalised, so it **rewards over-prediction**.
  - Our crack models already over-predict width (precision about 0.33) [ours], so SRL is a poor fit as the main lever [inf].
- **Centerline / distance regression**:
  - Sironi, Lepetit, Fua, CVPR 2014 / TPAMI 2016 (https://openaccess.thecvf.com/content_cvpr_2014/html/Sironi_Multiscale_Centerline_Detection_2014_CVPR_paper.html; abs).
  - Regress a (scale-space) distance-to-centerline function and read centerlines off as local maxima.
  - Reason they give: a classifier cannot tell on-centerline pixels from adjacent ones, which is our jitter problem.
  - A crack head that regresses a truncated distance transform (or a Gaussian heatmap, ≈ SVLS) and is scored with tolerance metrics would be **jitter-insensitive by construction** [inf].
- **CoLeTra**, "Disconnect to Connect" (arXiv 2503.05541; abs):
  - Augmentation that makes structures look disconnected while keeping connected labels.
  - Gains in topology and often Dice/HD [auth].
  - It is the opposite of our dotted-label problem, but the same idea: an augmentation that encodes the prior [inf].
- **FMS²** (arXiv 2603.13659, 2026; abs):
  - A flow-matching segmenter (2.96 M params) for cracks and vessels, plus SynFlow, a mask → image generator for pixel-aligned synthetic pairs.
  - Small model, so deployment-compatible [inf].
- **Lesson from our P1, not from the literature:** geometric and blur augmentation applied to 1.75 px labels with nearest-neighbour interpolation breaks the label–image correspondence. Rotating soft or distance-map targets and re-thresholding is the consistent alternative [inf].

## 3. Weak and mixed supervision

| Paper | Supervision | Evidence | Fit |
|---|---|---|---|
| **Božič, Tabernik, Skočaj**, Comput. Ind. 2021 (arXiv 2104.06064; sec) | image-level for all + N pixel masks | KSDD2: AP 73.3 (N=0) → 91.5 (N=5) → 95.4 (N=all). **Metric is image-level detection AP, not pixel IoU** [auth] | Shows that "a few masks + many image labels" works for *detection*. Our target is pixel geometry, so it is weaker evidence [inf] |
| **Mayr et al.**, ICIP 2019 (arXiv 2001.11248; abs) | image-level (EL cracks), normalised Lp pooling CAM | "promising" [auth], no strong numbers in the abstract | The only EL WSSS precedent. CAMs are coarse compared with 1.75 px labels [inf] |
| **Boxes2Pixels**, CVPR-W 2026 (arXiv 2604.11162; abs) | boxes → SAM pseudo-masks as a *noisy teacher*; frozen DINOv2 + light CNN; one-sided self-correction of background | +6.97 anomaly mIoU, +9.71 binary IoU over box baselines on a wind-turbine set [auth] | Notes that BoxInst-type priors assume the object fills the box, which **fails for thin diagonal cracks** [auth]. That is exactly the case of PVEL-AD crack boxes [inf] |
| **PVEL-AD**, Su et al., IEEE TII 2023 (doi 10.1109/TII.2022.3162846; github binyisu/PVEL-AD; search) | 36,543 NIR EL images; boxes for crack, finger, black core, star crack, etc. (README: 12 categories, 40k boxes; counts differ between versions) | — | The largest weak-label pool. Mono/poly cells differ from BenchmarkEL sources; boxes are loose for cracks [inf] |
| **Otamendi et al.**, Solar Energy 2021 (arXiv 2106.10962) and **IEEE TII 2023** (arXiv 2212.07768; sec) | detector → classifier → weakly supervised autoencoder (anomaly-free reconstruction + SSIM) → annotation pipeline | **60% annotation-cost reduction** on a public EL dataset [auth] | An EL-specific annotation-assist pipeline relevant to WattCycle. Anomaly maps are blob-level [inf] |

## 4. Synthetic defects for rare classes

**PV-DDPM / E-SCDD** (Hanifi, Köntges et al., arXiv 2511.09604, Nov 2025; sec; code github sntubix/pv-ddpm; data huggingface `snt-ubix/escdd`, MIT):
- **What it is:** mask-conditioned DDPM for EL cells, **trained on BenchmarkEL (SCDD = the 20221008 version: 695 labelled, 29 classes)**.
- **E-SCDD:**
  - Composition [auth]: 1,000 pixel-annotated images = 695 + 110 new real + 195 synthetic.
  - What the HF listing shows [ours, checked]: train 731 / val 90 / test 82.
  - About 93 train files carry `k-CFVS` / `k-CSIR` prefixes, probably the synthetic ones [inf].
  - The README says it adds **refined pixel-level annotations**.
- **Downstream evidence is weak:**
  - Only AA-CLIP anomaly detection was tested.
  - The E-SCDD vs SCDD comparison changes real and synthetic data at once.
  - Few-shot results favour the *original* SCDD at 16/32 shots [auth tables].
  - No segmentation experiment, nothing crack-specific.

**Generic few-shot defect synthesis:**
- AnomalyDiffusion (arXiv 2312.05767).
- DefectFill (CVPR 2025).
- DualAnoDiff (CVPR 2025).
- All abs/search level, on MVTec-type data.

**Crack-specific synthesis:**
- **CrackForward** (arXiv 2604.19941, abs): random-walk propagation plus a learned thickening generator; improves several segmenters [auth].
- **DP + elastic deformation** synthetic cracks (Innov. Infrastruct. Solut. 2026, doi 10.1007/s41062-026-02792-x; search).
- A masonry study (search level): about 30% synthetic data cost < 2% F1, but > 2,000 synthetic patches cost > 40% F1 [search]. So synthetic data must *supplement* real data, at a capped ratio.

**SIGAN** (arXiv 2104.04953, abs): GAN that removes defects for EL segmentation by subtraction; releases EL-2019 (540 images, pixel-level, 3 classes).

## 5. Active learning / annotation budget for rare classes

- **Methods:**
  - Region-level AL with class-balancing: Casanova et al., ICLR 2020 (arXiv 2002.06583), RL region selection, about 30% fewer labels on Cityscapes, asks for more rare-class regions [auth];
  - RIPU (arXiv 2111.12940);
  - OREAL, one-vs-rest entropy (WACV 2025, arXiv 2412.06470);
  - spatial-diversity region AL (arXiv 2507.17367: ~95% of full performance with 5–9% of pixels) [auth].
  - All are on natural or driving scenes; none on EL [search].
- **Fit to us:** WattCycle will annotate new data. Choosing *which cells* to label (rare-class-rich, from the 150k pool) is a lever on the same "rare class" problem. It could be cheap: score unlabelled cells by predicted interconnect/corrosion/inactive area plus uncertainty [inf].

## 6. Notes for other scouts and for the parent

- **BenchmarkEL versions:**
  - `dataset_20221008` (695 labelled, 29 classes, test 72 / val 70) is the version Pratt 2023 describes as SCDD, and its README says later versions **correct earlier masks of the same images**.
  - E-SCDD refines annotations again.
  - So three annotation versions exist for many of our 582 images. Comparing them gives a large-n **annotation-agreement estimate** (we currently rest on one solid duplicate pair) and a multi-annotator noise model. Cost: a download plus about an hour of CPU [inf].
- The handoff says 20211104 matches Pratt 2023 (24 classes, 50 test). PV-DDPM cites SCDD = 695 / 29 classes. **Which version Pratt 2023 used should be re-checked** [open].

## PAYWALLED_FOR_PARENT

- Pratt, Govender, Klein 2021, Renewable Energy, doi 10.1016/j.renene.2021.06.086 (annotation protocol for 20211104: crack width, dotted lines)
- Su, Zhou, Chen 2023, PVEL-AD, IEEE TII, doi 10.1109/TII.2022.3162846 (box protocol, crack box statistics)
- Synthetic crack generation (DP + elastic deformation), Innov. Infrastruct. Solut. 2026, doi 10.1007/s41062-026-02792-x
- Balzategui et al. 2020, IEEE/SICE SII, doi 10.1109/SII46433.2020.9026211 (EL FCN defects; check for any synthetic or auto-label element)
