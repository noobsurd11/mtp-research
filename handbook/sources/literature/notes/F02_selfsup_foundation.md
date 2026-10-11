# F02: unlabelled EL data without pseudo-labels, and foundation models

Date: 2026-10-10 (scout pass, about 1 h).
- Read scope is given per entry: *abstract*, *html-sections* (tables pulled from the arXiv HTML), or *search-abstract* (search snippet only).
- arXiv API timed out this session. Links were checked through arxiv.org/abs pages instead.
- Tags: [paper] = reported by the authors; [inferred] = my reading; [ours] = our measured facts (data reports, P1/P2).

## Constraints these directions must respect (from our docs)
- **Deployment:** part 3 is real-time, so the deployed model stays small (our U-Net++ is 5M parameters). Big models are allowed only as pretraining sources or teachers.
- **Geometry:** BenchmarkEL crack labels are 1.75 px on a ~4 px visible line [ours].
  - UCF crack is a region class (closed crack 3.5–5 px, resistive crack 21–24 px) [ours].
  - So a 14/16 px ViT patch is 4–9× wider than a BenchmarkEL crack.
- **Unlabelled pools:**
  - 11,938 CSIR/ARTS cells already prepared (up to 150k on Dropbox); 57% of them have half the contrast of the labelled images [ours].
  - About 4.5k UCF cells, almost all defect-free [ours].
  - ELPV: 2.6k cells.
  - PVEL-AD: 36,543 images. Access needs a hand-signed request form from an institutional email (IEEE DataPort).
  - Torpey's 22k EL set: no public link (arXiv v1, "redacted for blind review").
- **Compute:** gaint, 1×32 GB, shared with a ~6 GB tenant; cv02 A6000s, shared.

## Papers

### EL-specific
1. **Torpey, Pratt, Klein 2024**, arXiv 2402.17611 (v1 only; no journal ref on the abs page). Read: html-sections + earlier note A02.
   - Regimes:

     | Regime | Pretraining |
     |---|---|
     | R1 | random |
     | R2 | COCO supervised segmentation |
     | R3 | ImageNet supervised |
     | R4 | ImageNet SimCLR |
     | R5 | ImageNet MoCov2 |
     | R6 | EL SimCLR (22k images, 500 epochs) |
     | R7 | CCT |
     | R8 | U2PL |

   - mIoU (DeepLabV3-R50, full labels): R1 0.486, R2 0.544, R4 0.534, R6 0.517, R7 0.550, R8 0.448.
   - **Crack: "R2 and R4 outperform all other models"** (p ≤ 0.0001), including CCT. Also: "R4 performed better than R6" [paper].
   - The SimCLR augmentations were the defaults. The authors note that two random crops of one multi-defect image may contain different defects [paper].
   - Single runs for R7/R8.
   - **Lesson:** in-domain *contrastive* pretraining lost to ImageNet contrastive, and the gap is largest on crack. No label-fraction curve and no masked-image modelling were tested.
2. **EI-AE**, Lin et al., Energy Environ. Sci. 2026, 19, 513–526, DOI 10.1039/d5ee05042a (open access but bot-blocked; PAYWALLED_FOR_PARENT).
   - Method: unsupervised pixel-level EL defect segmentation from normal images only (enhanced iterative autoencoder), plus a few-shot extension with a few masks [search-abstract].
   - The only recent EL paper found that does label-free *pixel* segmentation. Numbers not read.
3. **SE-PatchCore**, Ren & Zhou, Tehnički vjesnik 33(1) 2026, DOI 10.17559/TV-20250320002496. On ELPV: image AUROC 98.7%, pixel AUROC 98.5% (+0.2/+0.6 over PatchCore) [abstract].
   - Pixel AUROC is insensitive to thin structures. No crack-specific localisation metric is given [inferred].
4. **Otamendi et al. 2021**, Solar Energy 220, DOI 10.1016/j.solener.2021.03.058, arXiv 2106.10962: weakly supervised autoencoder segmentation of cell-level anomalies [abstract].
   - Otamendi et al., IEEE TII 2022 (arXiv 2212.07768, DOI 10.1109/TII.2022.3228680): annotation framework; −60% annotation cost [abstract].
5. **Korovin et al. 2022** (arXiv 2208.05994): Mahalanobis anomaly detection on HJT EL; trainable with few defective images [search-abstract].
6. **GDDS** (arXiv 2407.13417): single-domain generalisation for PV defect detection under shift, on an EL shift dataset [search-abstract]. The only EL cross-domain paper found.
   - **No paper found** that transfers UCF-EL → BenchmarkEL (or the reverse), or uses PVEL-AD boxes to pretrain a segmenter [bounded: this pass].

### Masked-image modelling (MIM) vs contrastive, small domains, thin structures
7. **AOI-SSL**, Figueira et al., CVPR-W 2026, arXiv 2605.12430. Read: html-sections.
   - Data: 7k unlabelled and 625 labelled semiconductor inspection images.
   - mIoU:

     | Model | Pretraining | mIoU |
     |---|---|---|
     | FasterViT-0 (conv stages) + UPerNet | MAE | **60.3** |
     | FasterViT-0 + UPerNet | iBOT | 53.7 |
     | ViT-Tiny + UPerNet | MAE | 53.5 |
     | ViT-Tiny + UPerNet | iBOT | 41.6 |
     | ViT-Tiny + UPerNet | DINO | 40.0 |
     | ResNet18 + U-Net++ (closest to our setup) | ImageNet | 52.4 |

   - **Thin wires: FasterViT MAE wire IoU 66.7 vs ViT-Tiny MAE 43.0.** The authors blame non-overlapping 16×16 patchify for fragmenting thin, elongated structures [paper].
   - **The most direct evidence that (a) MIM beats contrastive/DINO in a small industrial domain, and (b) pure-ViT patching hurts thin structures.**
8. **VasoMIM**, AAAI 2026, arXiv 2508.10794. Read: html-sections.
   - Setup: ViT-B/16 with a U-Net decoder, X-ray angiogram vessels.
   - ARCADE Dice at 25 / 50 / 100% labels:

     | Pretraining | 25% | 50% | 100% |
     |---|---|---|---|
     | Scratch | 38.1 | 50.7 | 58.3 |
     | MAE | 56.6 | 63.0 | 68.2 |
     | VasoMIM | 56.9 | 63.6 | 68.9 |

   - Full labels, three datasets: MAE > SimMIM > DINO > scratch.
   - **The gain from MIM over scratch is largest at low labels (+18.5 Dice at 25%).**
   - A moderate masking ratio (0.5, best 0.3–0.5) beats MAE's 0.75 when the foreground is a thin, small fraction [paper].
9. **SparK**, arXiv 2301.03580: MIM for any CNN via sparse convolution; +3.5 on detection/instance segmentation for ResNet/ConvNeXt [abstract].
   - Means we can MIM-pretrain *our own* U-Net++ encoder without changing it.
   - HySparK (arXiv 2408.05815) carries it to medical imaging [title].
10. **ConvNeXt V2 / FCMAE**, arXiv 2301.00808: fully convolutional MAE; the Atto model has **3.7M parameters** (deployable size) [abstract].
11. **Kalapos & Gyires-Tóth**, ECCV-W 2022, arXiv 2209.00314 (ACDC cardiac). In-domain SSL gives 4–5× faster fine-tuning convergence, **but supervised ImageNet was the most accurate at < 100 labelled samples** [search-abstract]. A counterweight: MIM gains are not guaranteed against a good ImageNet init.

### Foundation features and patch size
12. **DINOv3**, arXiv 2508.10104 + GitHub.
    - Gram anchoring keeps dense features stable at high resolution.
    - **Released distilled ConvNeXt-T/S/B/L (29/50/89/198M)** plus ViT-S/16 (21M) and ViT-S+/16 (29M). DINOv3 licence [abstract + README].
    - The ConvNeXt variants avoid the 16 px patch problem: stride-4 stem, hierarchical.
    - Thin-structure adaptations in other domains change the first downsampling stride (NeurINO, neuron tracing) [search-abstract].
13. **JAFAR** (NeurIPS 2025, arXiv 2506.11136): learned upsampler for low-resolution foundation features to any resolution [search-abstract].
    - The materials paper arXiv 2508.21529 found plain bilinear upsampling cheap and effective, but FeatUp/LiFT produce artefacts [search-abstract].
14. **AM-RADIO** (CVPR 2024, arXiv 2312.06709): multi-teacher distillation (CLIP + DINOv2 + SAM) into one student; **E-RADIO ≥ 7× faster than the teachers** [abstract].

### SAM and anomaly models on defects
15. **SemiSAM+** (arXiv 2502.20749). Read: html-sections.
    - Specialist 3D U-Net proposes prompts; frozen SAM-Med3D returns pseudo-labels.
    - Left atrium (LA) MRI segmentation, 1 label: MT 40.6 → 48.9, DAN 44.6 → 62.3.
    - **But on PET heart: MT + SAM-Med3D 34.2 < MT 35.7.**
    - Limitation: point prompts handle *non-compact, irregular* targets poorly [paper].
16. **Quantifying the Limits of Segmentation Foundation Models** (arXiv 2412.04243, Zhang et al.): SAM, SAM 2 and HQ-SAM fail on dense, branching thin structures (retinal vessels) [search-abstract].
    - FineSAM++ (NeurIPS 2025, "Gate to the Vessel") patches SAM's local failures on vessels [search-abstract].
17. **Crack-adapted SAM:**
    - CrackSAM (arXiv 2312.04233): adapter/LoRA. Large model; strong zero-shot across materials [abstract].
    - Segment Any Crack (arXiv 2504.14138): OmniCrack30k F1 61.2, IoU 44.1, tuning normalisation parameters only [search-abstract].
    - All are far too large to deploy. Usable only as teachers.
18. **Boxes2Pixels** (CVPR-W 2026, arXiv 2604.11162). Read: abstract.
    - Method: boxes → SAM pseudo-masks treated as a *noisy teacher*. Student = frozen DINOv2 + light CNN + binary localisation head + one-sided self-correction (relaxes background loss where the student is confident).
    - Results (wind-turbine defects): +6.97 anomaly mIoU, +18.6 recall from self-correction, 80% fewer trainable parameters.
    - **Template for using PVEL-AD boxes.**
19. **No paper found** applying SAM/SAM2/SAM3, CLIP zero-shot (WinCLIP, AnomalyCLIP) or DINOv2/v3 frozen features to EL defect *segmentation* [bounded].
    - An ICSMD 2024 poster used SAM + VGG16 + ORB unsupervised on ELPV [search-abstract].

## Synthesis [inferred]
- **Patch size:** for 1.75 px crack labels, pure ViT patch features (14/16 px) are the wrong tool on their own (AOI-SSL wire result, SAM thin-structure failures). Convolutional or hierarchical encoders (ConvNeXt, SparK-pretrained CNN, DINOv3-ConvNeXt) are the right family. Region classes (inactive, UCF crack/corrosion) may still benefit from ViT semantics.
- **Objective:** MIM, not contrastive, is the in-domain objective with evidence in small domains and thin structures (AOI-SSL, VasoMIM). On EL the only test was contrastive (Torpey R6), which lost.
  - "MIM on EL at low labels" is untested: a real gap.
  - Use a moderate mask ratio, and possibly darkness/line-guided masking, the analogue of VasoMIM's vessel-guided masking.
- **Foundation models:** realistic roles are (a) a pretraining source for the encoder (DINOv3-ConvNeXt-T, or distilled into our 5M U-Net++); (b) a feature-distillation teacher on unlabelled cells (RADIO-style, no pseudo-labels); (c) a box → mask converter for PVEL-AD (Boxes2Pixels). SAM pseudo-labels for 2 px cracks are expected to be poor.
- **Anomaly detection:** the UCF defect-free cells (~4.5k) are exactly the "normal-only" set anomaly detection needs. AD gives a class-agnostic prior that could seed rare classes. Pixel AUROC hides thin-structure failure, so report AP / tolerance F1.

## PAYWALLED_FOR_PARENT
- 10.1039/d5ee05042a: EI-AE, Energy Environ. Sci. 2026. Open access but bot-blocked.
- 10.1016/j.solener.2021.03.058: Otamendi et al., Solar Energy 2021. arXiv copy exists: 2106.10962.
- 10.1109/TII.2022.3228680: Otamendi et al., IEEE TII 2022. arXiv copy: 2212.07768.
- PVEL-AD: Su, Zhou, Chen, IEEE TII 19(1):404–413, 2023. Article DOI not confirmed; likely 10.1109/TII.2022.3162846 (verify on Xplore). The dataset itself needs a signed request form.
- 10.17559/TV-20250320002496: SE-PatchCore, Tehnički vjesnik 2026. Probably open on hrcak.
