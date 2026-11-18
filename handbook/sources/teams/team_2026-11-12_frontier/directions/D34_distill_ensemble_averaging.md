# D34: Ensembles, distillation and weight averaging

Scout: D34 literature agent, 13 Nov 2026. Raw log: `D34_notes_wip.md` (same folder).
Legend: R = what the paper measured, E = what our files measured (BRIEF), S = my judgement.

## Why this direction matters here
E: the 5-seed U-Net++ / ResNet-34 ensemble is the only clear win so far (+0.014 to +0.018 crack IoU, relF1@2 0.881 to 0.897, components >= 20 px 0.798 to 0.834). The ensemble raises crack recall (pixel R 0.642 to 0.703) at some precision cost. Doubling the RN34 ensemble did not move the E1 target (+0.001, handbook). EMA, SWA, soups, flip / rot TTA, heterogeneous ensembles and distillation have never been run as supervised plug-ins (BRIEF section 5, optimizer and inference rows).
S: three questions follow. (1) Can one network hold the ensemble gain (distillation), and can distillation over the unlabelled pool go past it? (2) Can weight averaging or TTA give part of the gain for free? (3) Does an ensemble of different architectures or different label views add what more RN34 seeds did not?

## Queries run (40 in total; full list in D34_notes_wip.md)
Research MCP search_papers (year_from 2020 unless noted): knowledge distillation semantic segmentation (x2, also 2025+); ensemble distillation semantic segmentation (2020+, 2025+); ensemble distillation into single network segmentation; model soups; model soup weight averaging segmentation medical; stochastic weight averaging segmentation generalization; stochastic weight averaging medical image segmentation; self-distillation semantic segmentation noisy labels; self-distillation dense prediction segmentation (2023+); self-distillation label noise soft targets; test-time augmentation segmentation aggregation (x2); TTA thin structure vessel crack; heterogeneous ensemble CNN transformer segmentation (x2); KD crack segmentation lightweight (x2, also 2024+ under 5M); KD patient consistent; EMA of weights dynamics; diverse weight averaging OOD; packed ensembles; weight averaging KD domain shift; noisy student self-training segmentation; uncertainty-weighted fusion ensemble segmentation; snapshot ensembles / FGE; weight averaging checkpoints segmentation domain shift (2024+).
Snowball: similar_papers on Noothout 2022 + Fadugba 2025 + DUDES; get_citations on model soups and on Beyer 2022.
WebSearch: ensemble distillation segmentation 2024-2025; model soups medical; model soup segmentation 2025; MTKD retinal code; CIRKD code.
search_snippets: 3 attempts, all rate-limited by Semantic Scholar.
Full text read: Canonical KD (2604.25530, sections 2, 4.3, 4.4), IMWA (2404.16331, main results), Fadugba (2509.11689, experiment section).

## Selected papers

| # | id | year | venue | code | mechanism | adaptation (short) | score | bench |
|---|---|---|---|---|---|---|---|---|
| 1 | doi:10.1117/1.jmi.9.5.052407 (Noothout) | 2022 | J. Medical Imaging | unverified | Train one CNN on the averaged class probabilities of a seed or architecture ensemble | Cache 5-seed (+D4 TTA) softmax on 478 train cells; student = house U-Net++ RN34 on CE(GT) + KL(teacher) | 72 | 55 |
| 2 | arxiv:2604.25530 (Ali, Brox) | 2026 | arXiv | unverified | Plain logit KD, compute-matched and run long, beats seg-specific KD; logit KD scales with unlabelled images, feature KD does not | Pure logit KD from the 5-seed ensemble over 478 train + 11.9k pool cells, 60k+ steps | 70 | 65 |
| 3 | arxiv:2106.05237 (Beyer) | 2022 | CVPR | unverified | "Function matching": teacher and student see the identical augmented view, aggressive mixup, very long schedules | Same crop / flip / rot90 / brightness view to teacher and student, mixup or CutMix between cells, 100k steps | 64 | 45 |
| 4 | arxiv:2509.11689 (Fadugba) | 2025 | arXiv | unverified | Ensemble distillation for thin retinal vessels keeps ensemble Dice and calibration in one FR-UNet | Closest thin-structure evidence; same arm as #1, add calibration (ECE) and crack-band uncertainty | 60 | 35 |
| 5 | doi:10.1007/s13755-025-00356-4 (Eid, MTKD) | 2025 | Health Inf. Sci. Syst. | claimed public, URL unverified | Specialist teachers trained on modified GT (thin-only, thick-only), student distils all three | Teachers on native crack labels, dilated 3 to 5 px crack labels (recall), and an inactive specialist; student on GT + mixed teachers | 62 | 30 |
| 6 | arxiv:2411.18704 (Morales-Brotons) | 2024 | arXiv | unverified | EMA of weights as a plug-in: better generalisation, robustness to noisy labels, calibration, needs less lr decay | EMA (decay 0.999 to 0.9998) on house and PF runs; evaluate EMA and last iterate from the same run | 66 | 50 |
| 7 | arxiv:2203.05482 (Model soups) | 2022 | arXiv (ICML 2022, venue not tool-verified) | unverified | Average weights of fine-tunes that share an init; greedy soup by val | Seeds must fork from a shared checkpoint (decoder is random per seed); BN re-estimation; greedy soup on F51 + val | 58 | 40 |
| 8 | arxiv:2404.16331 (IMWA) | 2025 | Pattern Recognition | unverified | Episodes: several models trained from the same start, averaged, average restarts the next episode; strongest on class-imbalanced tasks | 4 to 8 parallel copies, average every 1k to 2.5k steps over the 20k schedule | 55 | 25 |
| 9 | arxiv:2102.08604 (SWAD) | 2021 | arXiv (NeurIPS 2021, venue not tool-verified) | github.com/khanrc/swad (from abstract) | Dense SWA over iterates seeks flat minima; smaller domain gap | Average every step from ~8k to 20k at constant or cyclic lr; target E1 | 56 | 45 |
| 10 | arxiv:2205.09739 (DiWA) | 2022 | arXiv (NeurIPS 2022, venue not tool-verified) | unverified | Average weights of independent runs that differ in hyperparameters (shared init); WA helps most under covariate shift | Fork 5 to 10 runs from a shared PF checkpoint with different aug / loss weights / lr; average | 50 | 35 |
| 11 | arxiv:2011.11156 (Better Aggregation in TTA) | 2021 | ICCV | unverified | TTA can flip correct predictions to wrong; learn per-augmentation (and per-class) aggregation weights | D4 group (flips x rot90, label-safe for our labels) simple mean first, then learned per-class weights fitted on val / CV folds | 66 | 60 |
| 12 | arxiv:2410.01083 (Discard in subsampling) | 2024 | ECCV | github.com/ca-joe-yang/discard-in-subsampling (from abstract) | Stride-2 layers drop 3 of 4 phases; recover them at test time and aggregate | Run the 4 stride phases of the RN34 stem / maxpool (or 1 px shift TTA) and average; aimed at 1 to 2 px crack aliasing | 58 | 30 |
| 13 | doi:10.1109/infinitys69204.2026.11666283 (Bramantyo) | 2026 | INFINITYS | unverified | EL CNN-Transformer ensemble: SegFormer-B0 + edge refinement (0.55) fused with U-Net++ (0.45) | Add one non-RN34 member (SegFormer / ConvNeXt / DINOv3 from D23 / D24) to the 5-seed ensemble; fit fusion weights per class on CV | 55 | 60 |
| 14 | arxiv:2504.07691 (HeteroAKD) | 2025 | AAAI | unverified | KD from CNN or Transformer teachers to a student of another family via features projected into logit space plus reliability-based mixing | Heterogeneous teacher (best transformer from D23 / D24) into the house U-Net++ RN34 student | 45 | 35 |
| 15 | arxiv:2306.08075 (BPKD) | 2024 | WACV | github.com/AkideLiu/BPKD (from abstract) | Separate edge-region and body-region KD losses | "Edge" = crack pixels + 2 px band and inactive borders; "body" = rest; weight the edge term up | 48 | 45 |
| 16 | arxiv:2204.06986 (CIRKD) | 2022 | CVPR | github.com/winycg/cirkd (WebSearch) | Cross-image pixel-to-pixel and pixel-to-region relation distillation via memory banks | Benchmark KD baseline; memory bank over cells from all 5 sources | 35 | 55 |
| 17 | arxiv:2210.09184 (Packed-Ensembles) | 2022 | HAL / arXiv | github.com/ENSTA-U2IS/torch-uncertainty (from abstract) | Ensemble of M subnetworks packed via grouped convs into one forward pass | Packed decoder (M = 4) on a shared or packed RN34; one run gives an ensemble at ~1x cost | 45 | 50 |
| 18 | arxiv:2404.06258 (RFKD) | 2024 | arXiv | unverified | Logit + feature KD with mixed clean / noisy images into a 0.5 M crack student | Deployment student (2 to 5 M, e.g. U-Net MobileNetV3 / EfficientNet-B0) distilled from the ensemble; add EL noise / blur views | 42 | 30 |

## Per-paper detail

### 1. Noothout et al. 2022, KD with ensembles for medical segmentation (doi:10.1117/1.jmi.9.5.052407)
R: uniform (seed) and diverse (3 architectures x 2 losses) ensembles beat every member on chest CT, brain MRI, cardiac MRI; a single distilled student matched the ensemble and significantly beat the same network trained on reference labels.
S, adaptation: teacher = existing 5 house seeds (and the 5 PF seeds), outputs cached once per train cell under the D4 group (8 views, 478 cells, about 0.2 GPU-h). Student loss = CE(GT) + Dice(crack, inactive) + lambda * KL(T=1 to 2, teacher || student), lambda 0.5 to 1. The soft targets carry the ensemble's 2 to 4 px crack band and its source-specific width, which a 1 to 2 px jittered hard label does not; this is the mechanism by which the student could even beat the single model on strict IoU.
Min experiment: arm = KD student (house recipe, 20k steps), 5 seeds; baseline = house single model (5-seed mean 0.474 crack IoU, 0.881 relF1@2), plus the 5-seed ensemble as upper reference. Metric: crack IoU and relF1@2 on clean 49 and on the 5-fold module-grouped CV. Kill: student mean crack IoU below 0.481 (less than half the ensemble gain) and relF1@2 below 0.889. About 8 GPU-h.
Prior overlap: none. BRIEF lists model distillation as never tried.

### 2. Ali et al. 2026, canonical KD for segmentation (arxiv:2604.25530)
R: under matched wall-clock compute, plain logit and feature KD beat CIRKD-style methods. With long training, PSPNet-R18 reaches 79.0 vs teacher 79.8 mIoU on Cityscapes. Pure logit KD over 20k extra unlabelled images also reaches 79.0; feature KD does not gain from unlabelled data. A Mask2Former teacher (83.7) gave almost no student gain over an aligned PSPNet teacher (77.8 vs 77.7) at 3x compute.
S, adaptation: the pool (11.9k CSIR / ARTS cells, of them 1,152 multi half-cells) is the "Train Extra" analogue. Pure logit KD from the 5-seed ensemble (soft, full 24-class distribution) on labelled + pool cells, long schedule (60k to 100k steps). Their teacher-architecture result says keep the teacher close to the student (U-Net++ family) rather than chase a stronger exotic teacher.
Min experiment: arm = student trained on 478 GT cells + pool with KD loss on pool, 60k steps, 3 seeds; baseline = arm #1 (KD on labelled cells only) and house single. Metric: crack IoU, relF1@2, inactive IoU on clean 49 / CV; E1 relF1@2 and inactive IoU as secondary. Kill: no gain over arm #1 above 0.012 crack IoU and no E1 relF1@2 gain above 0.02. About 20 GPU-h.
Prior overlap: partial. Mean Teacher with hard / tolerant pseudo-labels on the 11.9k pool at 100% labels was n.d. That closes single-model EMA teachers with thresholded labels. It does not close a frozen 5-seed ensemble teacher with soft full-distribution targets and long schedules.

### 3. Beyer et al. 2022, a good teacher is patient and consistent (arxiv:2106.05237)
R: distillation works when teacher and student see the same augmented view ("function matching"), with aggressive mixup and very long schedules; ResNet-50 student 82.8% ImageNet.
S, adaptation: our teacher outputs must be computed online on the same view as the student (rot90 / flip / crop / brightness, plus CutMix or mixup between cells, including pool cells). Mixup on 1-channel EL is label-free because the teacher labels the mixed image. Cost of online teacher: 5 forward passes per step, fine on A6000s.
Min experiment: arm = online function matching, 100k steps, 3 seeds; baseline = arm #1 (cached, fixed-view KD). Metric: crack IoU / relF1@2 on CV and clean 49. Kill: below arm #1 or gain under 0.01 crack IoU. About 20 GPU-h.
Prior overlap: none (distillation never tried; CutMix was used only inside Mean Teacher SSL).

### 4. Fadugba et al. 2025, ensemble distillation for retinal vessels (arxiv:2509.11689)
R: on DRIVE (40 images) and FIVES (800), a single FR-UNet distilled from a 5-model ensemble (KL or contrastive representation distillation) gives Dice / MCC comparable to the ensemble and good calibration (ECE, Brier, NLL), against MC dropout and Layer Ensembles.
S: the closest thin-structure, small-data evidence that ensemble distillation keeps the gain. Adds calibration as an output: student uncertainty maps over the crack band could feed severity post-evaluation.
Min experiment: run inside arm #1; additionally report ECE on crack pixels and relF1@2 at matched precision. Kill as #1.
Prior overlap: none.

### 5. Eid et al. 2025, multi-teacher KD with specialist teachers (doi:10.1007/s13755-025-00356-4)
R: three U-Net teachers on original GT, thin-vessel GT and thick-vessel GT; distilled student improved the baseline U-Net by up to 8.44 F1 and 10.42 IoU points on two fundus and two angiography sets.
S, adaptation: specialists match our split problems. Teacher A = house (native labels). Teacher B = crack labels dilated to 3 to 5 px (the "detection" teacher, should raise relR@2). Teacher C = inactive specialist (oversample the 42 inactive cells, inactive vs rest). Teacher D = PF (E1 inactive 0.24). Student: CE(GT) + per-class teacher selection (crack from A and B, inactive from C and D).
Min experiment: arm = 4-specialist student, 3 seeds; baseline = house single and arm #1. Metric: relR@2 at relP@2 >= 0.90, inactive IoU, E1 inactive IoU. Kill: relR@2 gain below 0.015 and inactive IoU gain below 0.02. About 12 GPU-h (teachers B, C need training).
Prior overlap: none. Dilated labels were never used as a teacher; Skeleton Recall and tolerant losses are different mechanisms.

### 6. Morales-Brotons et al. 2024, EMA of weights (arxiv:2411.18704)
R: EMA solutions differ from the last iterate and generalise better, with better robustness to noisy labels, prediction consistency, calibration and transfer; EMA needs less lr decay.
S, adaptation: our crack labels are noisy in position; EMA is the cheapest noise-robust plug-in. Add EMA (decay 0.999 and 0.9998, evaluated with BN stats recomputed) to the house and PF recipes; no extra training if logged in the next seed batch.
Min experiment: arm = EMA weights of the same 5 runs; baseline = last iterate of those runs (paired, same seeds). Metric: crack IoU, relF1@2, inactive IoU on clean 49 and CV; E1 relF1@2. Kill: paired mean difference under 0.005 crack IoU and under 0.01 E1 relF1@2. About 5 GPU-h (or 0 if piggy-backed).
Prior overlap: partial. Mean Teacher runs used an EMA teacher and found it within +-0.005 of the student, but under SSL losses. EMA as a supervised plug-in on the house and PF recipes is not tested (BRIEF optimizer row: "EMA / SWA never varied").

### 7. Wortsman et al. 2022, model soups (arxiv:2203.05482)
R: averaging weights of fine-tunes with different hyperparameters from one pretrained init improves accuracy and robustness without inference cost (ImageNet, WILDS, text); fails when models sit in different basins.
S, adaptation: our 5 seeds share only the ImageNet encoder init; decoders are randomly initialised per seed and the house fine-tune moves layer3 / layer4 far from init. A direct soup of existing seeds will probably collapse. Fix: train one run to step k (2k to 5k), then fork 5 continuations with different seeds, aug order, Dice weights; uniform and greedy soup; recompute BN on train cells.
Min experiment: step 0 (free): average the 5 existing PF seeds and eval on val; expected collapse, confirms the basin issue. Arm = forked soup (k = 4k), 2 replicates; baseline = the same forked runs as an output ensemble and as singles. Metric: crack IoU on CV / clean 49. Kill: soup below the mean single of its members. About 6 GPU-h.
Prior overlap: none run (an "A3 soup of 5 PF seeds" was proposed on 30 Oct and not run).

### 8. Huang et al. 2025, IMWA (arxiv:2404.16331, doi:10.1016/j.patcog.2024.111293)
R: on long-tailed classification, semi-supervised classification and SSOD, IMWA adds 0.8 to 1.8 top-1 over strong bases where plain end-of-training averaging adds about 0.2; IMWA and EMA are additive; best with 10 to 200 episodes.
S, adaptation: crack (0.19% of pixels) and inactive (42 cells) are the imbalanced classes. 4 parallel copies on 4 GPUs, average every 1k to 2k steps, same total steps.
Min experiment: arm = IMWA (4 copies, 10 episodes over 20k steps), 3 replicates; baseline = house single. Metric: inactive IoU and crack IoU on CV. Kill: under 0.01 on both. About 13 GPU-h.
Prior overlap: none.

### 9. Cha et al. 2021, SWAD (arxiv:2102.08604)
R: dense, overfit-aware stochastic weight averaging finds flatter minima; +1.6 points mean out-of-domain accuracy over five DomainBed benchmarks; combines with other DG methods.
S, adaptation: aimed at E1 (unseen modules, half-cut cells). Average every step from about 8k to 20k under constant or cyclic lr, select the window on F51 / H36 (not E1). PF variant first, since PF already helps E1 inactive.
Min experiment: arm = PF + SWAD, 5 seeds; baseline = PF single. Metric: E1 relF1@2 and E1 inactive IoU; test crack IoU as guard. Kill: E1 relF1@2 gain under 0.02 or test crack IoU loss over 0.005. About 6 GPU-h.
Prior overlap: none (SWA never varied).

### 10. Ramé et al. 2022, DiWA (arxiv:2205.09739)
R: averaging weights of independent runs with different hyperparameters (shared init) beats single-run WA on DomainBed; WA helps most when the marginal input distribution shifts.
S: same E1 logic as SWAD but with diversity across runs. Needs the shared-init trick from #7. Members: different lr, Dice weights, synthetic half-cut views on or off, Skeleton Recall 0.1 on or off.
Min experiment: arm = DiWA of 8 forks from one PF checkpoint; baseline = their output ensemble and singles. Metric: E1 relF1@2, test crack IoU. Kill: DiWA below mean single. About 10 GPU-h.
Prior overlap: none.

### 11. Shanmugam et al. 2021, better aggregation in TTA (arxiv:2011.11156)
R: simple-average TTA can turn correct predictions wrong; a learned aggregation over augmentations gives consistent gains over mean TTA across models and datasets (classification).
S, adaptation: the D4 group (h-flip, v-flip, rot90 x4) is label-safe for EL cells and the house is trained with these augmentations, so plain D4 mean TTA is a zero-training test. Then fit per-class, per-transform weights on val or in CV (54 val cells is small, so CV only). Note that 5 seeds x 8 views = 40 passes per cell, fine offline.
Min experiment: arm = D4 mean TTA on the 5 single seeds and on the ensemble; baseline = no TTA, same checkpoints (paired). Metric: crack IoU, relF1@2, components >= 20 px, inactive IoU on clean 49 and CV. Kill: paired gain under 0.005 crack IoU on singles. Under 1 GPU-h.
Prior overlap: none. Per-panel BN adaptation (failed) is test-time adaptation, a different mechanism; flip / rot / multi-scale TTA is listed as not closed.

### 12. Yang et al. 2024, discarded activations in subsampling (arxiv:2410.01083)
R: searching and aggregating the activations that stride-2 layers drop improves test-time performance for classification and segmentation across nine architectures, on top of standard TTA.
S, adaptation: a 1 to 2 px crack lands on one of four stride-2 phases in the RN34 stem conv and again in maxpool; a 1 px input shift changes what the encoder sees. Cheap version: shift TTA by (0,1), (1,0), (1,1) px with exact un-shift, averaged; full version: their phase search on the stem and maxpool.
Min experiment: arm = shift / phase TTA on 5 singles; baseline = D4 TTA arm of #11. Metric: crack IoU and components >= 20 px. Kill: no gain over D4 TTA above 0.003. Under 1 GPU-h.
Prior overlap: none.

### 13. Bramantyo and Arifin 2026, EL CNN-Transformer ensemble (doi:10.1109/infinitys69204.2026.11666283)
R: 5-class EL segmentation; SegFormer-B0 with an edge refinement module fused 0.55 / 0.45 with a compact U-Net++; 0.8399 mIoU, 0.7786 defect mIoU on an internal test set; gain over the single branch confirmed by paired bootstrap.
S: EL-domain evidence that a transformer member adds to U-Net++. Our handbook shows more RN34 seeds saturate (E1 +0.001 when doubled), so diversity has to come from architecture or pretraining. Depends on D23 / D24 producing a member within about 0.02 crack IoU of the house.
Min experiment: arm = 5 house + 5 transformer (or 3 + 3 at equal compute) with per-class fusion weights fitted on CV; baseline = 10-seed RN34 ensemble. Metric: crack IoU, E1 relF1@2, inactive IoU. Kill: under 0.008 crack IoU and under 0.02 E1 relF1@2. About 10 GPU-h beyond the member training.
Prior overlap: none (only homogeneous RN34 ensembles were run).

### 14. Huang et al. 2025, HeteroAKD (arxiv:2504.07691)
R: KD between heterogeneous teacher / student (CNN and Transformer) for segmentation, with features projected into logit space and reliability-weighted mixing; beats prior KD on three benchmarks.
S: route to bring a transformer teacher's context (useful for E1 half-cut layout and scuff) into the house student without running the transformer at inference. Only worth it if a transformer from D23 / D24 beats the house somewhere.
Min experiment: arm = HeteroAKD student; baseline = logit KD from the same teacher (arm #1 recipe). Metric: E1 relF1@2, crack IoU. Kill: no gain over logit KD above 0.01. About 8 GPU-h.
Prior overlap: none.

### 15. Liu et al. 2024, BPKD (arxiv:2306.08075)
R: separate edge and body KD losses; state-of-the-art KD on three segmentation benchmarks across CNN and transformer students.
S: for us almost every crack pixel is "edge". Define the edge mask as crack GT dilated 2 px plus inactive borders; weight it up. Mainly a stronger KD loss variant for arm #1.
Min experiment: arm = arm #1 with BPKD loss; baseline = arm #1. Metric: crack IoU, relF1@2. Kill: gain under 0.008. About 6 GPU-h.
Prior overlap: none.

### 16. Yang et al. 2022, CIRKD (arxiv:2204.06986)
R: cross-image relational KD; the most cited segmentation KD method; repo reports students on Cityscapes, CamVid, ADE20K, VOC.
S: low expected gain for us (canonical KD paper shows it loses to plain KD at matched compute), but a credible benchmark distillation track should include it as the standard KD baseline next to logit KD.
Min experiment: benchmark-only: CIRKD student vs logit-KD student at matched GPU-h. Kill for score purposes: below logit KD.
Prior overlap: none.

### 17. Laurent et al. 2022, Packed-Ensembles (arxiv:2210.09184)
R: grouped-conv packed subnetworks keep deep-ensemble accuracy, calibration, OOD detection and shift robustness within the memory of one network.
S: one training run gives an M = 4 ensemble; cheaper way to get ensemble behaviour on the deployment side; also a candidate uncertainty baseline for the benchmark.
Min experiment: arm = packed U-Net++ decoder (M = 4, alpha = 2) on RN34, 3 seeds; baseline = house single and 4-seed ensemble. Metric: crack IoU, ECE. Kill: below the house single. About 5 GPU-h.
Prior overlap: none.

### 18. Chen et al. 2024, RFKD for lightweight crack segmentation (arxiv:2404.06258)
R: logit + feature KD with mixed clean and noisy images into a 0.5 M crack student; 62% better mean Dice on noisy images than SOTA KD methods.
S: the deployment route (WattCycle inspection rig): 2 to 5 M student (U-Net with MobileNetV3 or EfficientNet-B0 encoder) distilled from the ensemble on labelled + pool cells; add EL-like noise / blur / contrast views.
Min experiment: arm = 3 M student with ensemble KD on labelled + pool; baseline = the same 3 M student trained on GT only. Metric: crack relF1@2 and inactive IoU on clean 49 / CV; latency. Kill: KD student not above the GT-only student by 0.02 relF1@2. About 10 GPU-h.
Prior overlap: none.

## Suggested order (S)
1. Free or near-free first: D4 TTA (#11) and shift TTA (#12) on existing checkpoints; EMA (#6) logged in the next seed batch; naive soup of existing PF seeds as a sanity check (#7 step 0).
2. Ensemble distillation on labelled cells (#1, #4), then over the pool (#2) and with function matching (#3). This is the main bet.
3. Specialist teachers (#5) and SWAD / DiWA for E1 (#9, #10) in parallel on cv02.
4. Heterogeneous members (#13, #14) once D23 / D24 have a competitive transformer.
5. Deployment student (#18, #17) last.

## Bold bets
- Pool distillation past the ensemble (#2 + #3): a student trained for 100k+ steps on 11.9k pool cells (later the 159k pool) with online ensemble targets on identical views. The Cityscapes result says logit KD keeps scaling with unlabelled data; if it holds, the student could exceed the 5-seed ensemble, not just match it.
- Specialist-teacher distillation (#5): a dilated-label crack teacher plus an inactive specialist could push relR@2 toward the 0.90 target while the GT term keeps precision.

## Rejected or reference only
- arxiv:2303.09843 DUDES (2024): distils ensemble uncertainty for Cityscapes / VOC; useful only if severity post-evaluation needs per-pixel uncertainty, otherwise covered by #1 and #4.
- arxiv:2403.19522 Model Stock (ECCV 2024): two-model layer-wise averaging around a pretrained centre; needs a shared pretrained init for every layer, which our random decoder breaks; fold into #7 if forked soups work.
- arxiv:2012.09816 Allen-Zhu and Li (2020): theory for why seed ensembles help and can be distilled ("multi-view"); motivation, no new arm.
- arxiv:2106.05945 Stanton et al. (2021): students rarely match teachers, and closer fidelity does not always mean better generalisation; design note for #1 to #3 (report teacher-student agreement), no arm.
- doi:10.1016/j.apenergy.2023.122184 Zhang et al. (2024): NAS + KD for EL, but image classification (ELPV, 1.85 M, 91.74%); deployment reference only.
- doi:10.1080/10589759.2025.2505089 MambaU-Light (2025): bridge cracks, UNet++ / TransUNet / Mamba-UNet teachers to a 3.66 M student; closed access, no code; #18 covers the idea.
- arxiv:2211.14058 XDED (ECCV 2022): cross-domain ensemble distillation for DG, evaluated mainly on classification; segmentation evidence not verified.
- doi:10.1109/cvprw53098.2021.00295 Chao et al. (2021): ensemble distillation for UDA segmentation; overlaps D30 (UDA) more than this direction.
- doi:10.3390/s22072623 PALS (2022): pixel-wise adaptive label smoothing via self-KD; +1.06 mIoU at 100% Cityscapes; overlaps D18 soft-label losses.
- arxiv:2203.16172 DLB (CVPR 2022): self-distillation from the last mini-batch; classification only.
- arxiv:2303.13005 USKD (ICCV 2023): unified normalised KD / self-KD; classification only.
- doi:10.1109/tetci.2025.3526259 uncertainty-driven adaptive self-KD for medical segmentation (2025): abstract only, no code found; covered by #1 and PALS.
- arxiv:2606.25278 heterogeneous snapshot distillation (2026) and arxiv:2610.41362 task-performance routing multi-teacher KD for CT (2026): 3D point cloud and CT organ settings; #5 and #14 cover the mechanisms.
- doi:10.3390/s23104688 Nanni et al. (2023): CNN + transformer ensembles for polyps; #13 is the closer (EL) evidence.

## Gaps
- No paper tests ensemble distillation, soups or SWA on 1 to 2 px jittered labels with strict IoU; the nearest evidence is retinal vessels (#4, #5).
- No segmentation-specific model-soup paper found (WebSearch and MCP); evidence is classification / DG.
- search_snippets was rate-limited all session, so I could not pull TTA gain numbers for thin-structure segmentation or exact numbers from Noothout's tables.
- Code repositories for Noothout, Fadugba, MTKD, canonical KD, Beyer, EMA, IMWA, DiWA and RFKD were not verified (marked unverified). Verified from abstracts or WebSearch: SWAD, Model Stock, Packed-Ensembles (torch-uncertainty), BPKD, discard-in-subsampling, CIRKD.
- Sub-direction worth its own search: k-fold CV ensembles in the nnU-Net style (5 fold models as both the measurement instrument and the ensemble), which joins problem 5 (measurement) with this direction.
- Sub-direction: distillation on the 159k pool and on half-cut pool cells for E1; depends on whether the teacher sees E1 cracks at all (E: 70% of E1 crack pixels get p < 0.001), so pool KD alone is unlikely to fix E1 without a better teacher.
