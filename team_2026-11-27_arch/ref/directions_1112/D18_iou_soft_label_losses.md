# D18: Metric-aligned and soft-label losses (literature scout, 12 to 13 Nov 2026)

Scope: Lovasz and Jaccard metric losses, Dice semimetric losses, boundary and spatial label smoothing, soft-label regression, Tversky and focal families, compound and region-size losses, component-wise losses, ensemble distillation through soft labels, loss choice studies, and operating-point decoding for IoU on thin classes.

Tags: R = what the paper measured, E = what our files measured, S = my judgement.
Second pass (13 Nov) after a dropped connection: added SAUNA (WACV 2025), BLSS (SPL 2026), BiCC (arXiv 2026), Noothout ensemble KD (JMI 2022), boundary label relaxation (CVPR 2019); verified code for SVLS, GeoLS, Unified Focal, Recall loss, CC-DiceCE; moved SoftSeg and Eelbode to the rejected list.

## 1. What our files already say (E), and why it shapes this direction

- House loss = CE + soft Dice on crack and inactive. Dice on 12 classes was worse, Dice on 3 n.d., soft clDice failed, Skeleton Recall w 1.0 widened predictions, offset-tolerant CE n.d. (P14, trained at 10%). Lovasz / Jaccard metric losses, soft-label losses, focal / Tversky, region-size and component-wise losses were never run (BRIEF section 5).
- The decision metric is pooled (dataset-level) IoU over the split, not per-image IoU (handbook 04 / 07). This matters for every IoU loss and for RankSEG, which target per-image scores unless set up otherwise.
- At 100% labels a val-chosen crack logit bias adds about 0 to +0.004 crack IoU. So pure operating-point methods have little headroom on test. The E1 crack failure is a ranking failure (70% of E1 crack pixels at p < 0.001), not a threshold failure.
- The 5-seed ensemble beats a single model by +0.018 crack IoU. That gap is the most concrete target for a soft-label loss (distillation).
- JML paper (R, sec. 2.2, App. E): the L1 soft Jaccard / soft Dice form, which is what the house soft Dice is, is not a metric on soft targets and pushes predictions to 0/1; soft-label training with it can be worse than hard labels. Any soft-label arm here must swap the house soft Dice for JML or DML, or the test is invalid.
- JML paper (R, Table 6): CE alone 72.88 -> CE + JML 75.55 mIoU (Cityscapes, DL3-R18); + KD soft labels 76.16; + JML-BLS teacher 76.68. (S) Our house already has soft Dice on crack and inactive, and Dice and Jaccard losses approximate each other (Eelbode 2020), so most of the "CE -> CE + JML" gain is already in the house model. The open part is the soft-label part (KD, BLS, SAUNA-style targets).

## 2. Queries run

Research MCP search_papers (OpenAlex and arXiv answered; Scopus / ScienceDirect HTTP 401, Semantic Scholar rate-limited all session, IEEE key inactive; a 502 gateway outage for about 45 min on 12 Nov):

Session 1 (12 Nov)
1. Jaccard metric losses soft labels (2020+)
2. Dice semimetric losses soft labels segmentation (2020+)
3. Lovasz softmax loss segmentation IoU surrogate (2018+)
4. boundary label smoothing semantic segmentation (2020+)
5. spatially varying label smoothing segmentation uncertainty boundaries (2020+)
6. unified focal loss Dice cross entropy class imbalance segmentation (2020+)
7. loss functions medical image segmentation benchmark comparison study (2020+)
8. RankSEG consistent ranking segmentation Dice IoU optimal decoding (2020+)
9. Jaccard metric losses soft labels knowledge distillation label smoothing IoU (2022+)
10. blob loss instance imbalance segmentation (2022+)
11. Lovasz hinge Jaccard loss thin structure crack segmentation (2021+)
12. segmentation loss soft labels label noise boundary uncertainty (2025+)
13. Gaussian soft label distance transform thin structure segmentation vessel crack heatmap (2020+)
14. Tversky loss precision recall trade-off thin structures segmentation (2023+)
15. margin-based label smoothing calibration segmentation logit constraints (2022+)
16. IoU loss semantic segmentation small objects rare classes (2025+)
17. logit adjustment long-tailed semantic segmentation loss rare classes (2021+)
18. ensemble knowledge distillation semantic segmentation single student soft targets small dataset (2021+)
19. annotation misalignment tolerant loss thin structures label shift robust segmentation (2023+)

Session 2 (13 Nov)
20. Jaccard metric losses soft labels (2020+, rerun)
21. Dice semimetric losses soft labels segmentation (2020+, rerun)
22. Lovasz softmax loss intersection over union optimization (all years)
23. boundary label smoothing semantic segmentation (2020+, rerun)
24. unified focal loss Dice cross entropy class imbalance segmentation (2020+, rerun)
25. RankSEG consistent segmentation decision rule Dice IoU (2020+)
26. soft label loss thin structure segmentation annotation uncertainty (2025+)
27. crack segmentation loss function comparison Dice focal Tversky Lovasz (2022+)
28. Jaccard metric loss (2025+)
29. ensemble knowledge distillation segmentation soft labels single model matches ensemble (2021+)
30. threshold selection optimal IoU segmentation probability calibration small structures (2022+)
31. connected component loss instance-aware small lesion segmentation (2025+)

Snowballing: get_citations on JML (31 citing, none a stronger soft-label loss), on DML (26 citing; found SAUNA and SiNGR from the same Oulu group), on SAUNA (3 citing, none relevant); similar_papers on JML + SVLS + GeoLS (Eelbode 2020, SoftSeg, Batching Soft IoU, superpixel label softening). search_snippets failed 3 times (Semantic Scholar rate limit).
Full text read: JML (arXiv 2302.05666: sec. 2 to 4, 6, App. E), SAUNA (arXiv 2405.16815: results, Table 1).
get_paper checks: BLSS, BiCC, SAUNA, Galdran 2023, Noothout 2022, label relaxation, observer-choice 2026.
WebSearch (about 16 calls): JDTLosses, fine-grained IoU, RankSEG / RankSEG-RMA repos, Xu et al. CVPRW 2023, Rill-Garcia 2022, Nordstrom 2023, focal Tversky, 2025 to 2026 loss studies, SVLS repo, GeoLS repo, Unified Focal repo, CC-DiceCE repo, Recall loss repo.

## 3. Selected papers (18)

Score = value for our scores (task rubric). Bench = value for the benchmark.

| # | Paper id | Year | Venue | Code | Mechanism | Adaptation to our data | Score | Bench |
|---|---|---|---|---|---|---|---|---|
| 1 | doi:10.52202/075280-3289 (JML, arXiv 2302.05666) | 2023 | NeurIPS | github.com/zifuwanggg/JDTLosses | IoU loss that is a true metric on [0,1], so it accepts soft targets; used for KD and boundary label smoothing (BLS) | Distil the 5-seed FINAL (or PF) ensemble into one U-Net++ R34 with CE + JML on teacher soft maps, on the 478 train cells plus the 11.9k pool; JML only on crack + inactive, computed over the whole batch (pooled, matches our metric), active classes = LABEL (teacher confidence filter, best in R Table 7) | 72 | 50 |
| 2 | doi:10.1109/wacv61041.2025.00412 (SAUNA, arXiv 2405.16815) | 2025 | WACV | github.com/Oulu-IMEDS/SAUNA (stated in abstract) | Turn hard thin-structure masks into soft targets from distance to the annotation boundary and local thickness; train as regression with a generalised JML (any hypercube) + stable Focal-L1 | Crack only: SAUNA transform of the 1 to 2 px crack labels (thickness term makes 1.5 px ARTS and 3.25 px SDLE lines comparable); crack channel as regression head next to the 24-class softmax, or soft crack target inside the softmax with JML; threshold re-picked on val | 68 | 55 |
| 3 | doi:10.1007/978-3-030-78191-0_52 (SVLS, arXiv 2104.05788) | 2021 | IPMI | github.com/mobarakol/SVLS (CELossWithSVLS) | One-hot labels convolved with a Gaussian, so only boundary pixels get soft targets | Soft crack band: Gaussian sigma set per source from label width (ARTS 1.5 px ... SDLE 3.25 px), so the target encodes the 1 to 2 px jitter; pair with JML/DML, not the house soft Dice; re-pick crack bias on val | 63 | 40 |
| 4 | doi:10.59275/j.melba.2025-c1d9 (GeoLS) | 2025 | MELBA (MIDL 2023 origin) | github.com/adigasu/GeoLS (CELossWithGeoLS) | Soft labels from a geodesic distance on image intensity, so label mass follows image structure | Geodesic distance on the EL image from each crack label pixel: soft crack mass flows along the dark ridge, not across bright silicon, which recentres the 50% of label points that sit > 1 px off the ridge; same for inactive edges | 60 | 35 |
| 5 | doi:10.1117/1.jmi.9.5.052407 (Noothout, ensemble KD) | 2022 | J. Med. Imaging | none found | Distil a uniform (seed) or diverse ensemble into one CNN by matching class probabilities | Same teacher as row 1 but plain KL / CE on soft maps: the control arm that tells whether JML adds anything over classic KD on our data | 58 | 35 |
| 6 | doi:10.1109/isbi61048.2026.11515682 (CC-DiceCE, arXiv 2511.17146) | 2026 | ISBI | github.com/TIO-IKIM/Learning-to-Look-Closer (linked in paper; contents unverified) | DiceCE per connected-component region, paired 1:1 with global DiceCE, so each small object gets its own gradient | Per-component Dice for crack (76 to 88% of crack components are < 20 px); aimed at components found (0.834) and E1 recall | 58 | 55 |
| 7 | arxiv:2609.30223 (BiCC) | 2026 | arXiv | github.com/TIO-IKIM/BiCC-Loss (stated in abstract) | Component loss with a second branch on predicted components, so false-positive components are penalised; alpha sets component precision vs recall | Crack: GT-derived branch for small missed cracks, prediction-derived branch for decoys (scuff streaks on E1 half-cut cells, busbar edges); alpha tuned on val relP@2 / relR@2 | 56 | 55 |
| 8 | arxiv:2604.24276 (multi-class instance-aware losses) | 2026 | arXiv | unverified | One-vs-rest blob / CC loss over classes, inverse-size weighting inside each component | Apply to the rare and weak classes together (crack, inactive, splice, gridline, edge_dark, material) so each gets equal signal; targets mIoU_rob and inactive | 54 | 50 |
| 9 | doi:10.1016/j.media.2023.103015 (region-size biases, arXiv 2104.08717) | 2023 | MedIA | github.com/by-liu/SegLossBias | Dice and CE differ mainly in an implicit region-size penalty; replace it with an explicit L1 / KL term on predicted class proportions | CE + proportion term on crack and inactive per image, replacing soft Dice; direct control of crack width (precision vs recall) instead of a post-hoc logit bias | 52 | 45 |
| 10 | doi:10.1007/978-3-031-43898-1_46 (DML, arXiv 2303.16296) | 2023 | MICCAI | github.com/zifuwanggg/JDTLosses | Dice loss equal to soft Dice on hard labels but correct on soft labels | Drop-in replacement for the house soft Dice whenever targets become soft (rows 1 to 4); paired check DML vs house soft Dice on the same soft targets | 50 | 40 |
| 11 | doi:10.1109/cvpr.2018.00464 (Lovasz-Softmax) | 2018 | CVPR | smp ships LovaszLoss (house library) | Convex (Lovasz extension) surrogate of IoU | Lovasz hinge on crack and Lovasz-softmax over present classes, per batch (per_image False) to match pooled IoU; hard labels only | 45 | 65 |
| 12 | doi:10.1109/cvpr.2019.00906 (label relaxation, arXiv 1812.01593) | 2019 | CVPR | NVIDIA semantic-segmentation repo (unverified) | At boundary pixels, maximise the summed probability of all classes present in a small neighbourhood, so a 1 px offset is not punished | Crack: inside a 3x3 window around each crack label pixel the target is "crack OR neighbour class" (log(p_crack + p_other)); outside, normal CE. Tolerates jitter without widening the target | 45 | 30 |
| 13 | doi:10.1016/j.compmedimag.2021.102026 (Unified Focal, arXiv 2102.04525) | 2022 | CMIG | github.com/mlyg/unified-focal-loss (Keras; PyTorch port on PyPI, untested) | Compound of asymmetric focal CE and asymmetric focal Tversky; generalises Dice / CE / focal / Tversky | Replace CE + Dice; asymmetry favours crack and inactive recall (target relR@2 >= 0.90) | 44 | 65 |
| 14 | doi:10.1109/icra46639.2022.9811702 (Recall loss, arXiv 2106.14917) | 2022 | ICRA | github.com/PotatoTian/recall-semseg (web, unverified contents) | CE reweighted per class by running recall | Gridline recall 0.33 and splice never predicted: recall loss lifts exactly these; check it does not cost crack precision | 44 | 40 |
| 15 | doi:10.1109/lsp.2026.3731530 (BLSS) | 2026 | IEEE SPL | none found | Boundary-gated label smoothing: local-mean soft targets only inside a morphological band, BCE + Dice on hard labels elsewhere; 20 seeds, DeepCrack among 4 sets; ECE down, no Dice loss | Crack band of 2 px around labels gets local-mean soft targets; main use is calibrated crack probabilities (for RankSEG decoding, severity, ensemble weighting), not raw IoU | 42 | 45 |
| 16 | doi:10.1109/CVPRW59228.2023.00464 (Xu, Zou, Okatani, label errors in thin cracks) | 2023 | CVPRW | none found | Synthetic under / over annotation of 1 px crack curves: under-annotation hurts more than over-annotation | Our dotted, under-traced crack labels are under-annotation; train on labels dilated by 1 px (asymmetric over-annotation) or a soft band, score on original labels | 40 | 55 |
| 17 | arxiv:2310.19252 (fine-grained IoU) | 2023 | arXiv | github.com/zifuwanggg/JDTLosses | Per-image and per-class-per-image mIoU plus worst-case metrics; losses must match the metric variant | Benchmark: report pooled IoU plus per-cell IoU and worst-k cells per source; loss arm: JML per-image vs per-batch | 40 | 82 |
| 18 | doi:10.52202/085713-5452 (RankSEG-RMA, arXiv 2510.15362); also arxiv:2609.38930 (2026 follow-up) | 2025 | NeurIPS | github.com/ZixunWang/RankSEG-RMA | Replace argmax with the decision rule that maximises expected Dice / IoU per image; the 2026 follow-up drops the conditional independence assumption | Post-process FINAL crack probabilities per cell; it maximises per-image IoU, not pooled IoU, so check both | 36 | 50 |

R notes for the new rows:
- SAUNA (R, Table 1, FIVES, 1 seed group, low-res input): UNet++ BCE + Dice hard labels 74.05 IoU; JML + BLS soft 81.77; SAUNA + GJML + SF-L1 84.75 (+10.7 over hard, +3.0 over BLS); UNet++ at high-res with hard labels 81.70. On 4 more retinal sets, +0.4 to +2.3 IoU over BLS. (S) Much of the gain is at downsampled input, where hard thin labels alias; our crack labels are at native 512 px, so expect a smaller gain, but BMRK cells are downscaled ELPV cells, the same aliasing case.
- Noothout (R): distilled students of seed or diverse ensembles matched the ensemble and beat the same network trained on reference labels, on 3 datasets (CT organs, brain MRI, cardiac MRI).
- BiCC (R): nnU-Net, 5 datasets, 5-fold CV: beats CC-DiceCE on lesion-wise F1 in 4 of 5 and blob loss in 5 of 5; CC-DiceCE loses up to 0.363 precision by favouring recall.
- BLSS (R): 4 datasets x 20 seeds; boundary-band ECE down 28 to 49%, no Dice or Boundary-Dice loss; gains smaller on Magnetic Tile.

## 4. Minimum experiments

All on house U-Net++ R34, 512 px, 20k steps, 5 seeds v 5, clean-49 test with val-only choices (crack bias picked on val), E1 secondary. Baseline = SUP100 (house) unless said; repeat the winner on PF.

1. **JML-KD** (row 1, score 72). Arm: student with CE + JML (hard labels) + (CE + JML) on FINAL ensemble soft maps, on train + pool cells. Control arm from row 5: same teacher, plain KL only. Metric: crack IoU, relF1@2, inactive IoU, E1 inactive. Kill: student 5-seed mean crack IoU < SUP100 + 0.009 (half the ensemble gap) and relF1@2 n.d. Cost about 5.5 GPU-h per arm-seed set plus 2 GPU-h teacher inference. Prior overlap: pseudo-label SSL at 100% with the 11.9k pool was n.d., but it used an EMA teacher of the same model, hard / tolerant labels and the old Dice; a 5-model ensemble teacher with soft targets and a soft-compatible IoU loss is untested.
2. **SAUNA crack targets** (row 2, 68). Arm: crack target = SAUNA transform, GJML + SF-L1 on the crack channel (separate sigmoid head), house CE for the other 23 classes. Kill: crack IoU at val-chosen threshold < SUP100 + 0.012, or relP@2 drop > 0.05. Second read: BMRK crack IoU (downscaled source, where SAUNA's evidence is strongest).
3. **SVLS + JML** (row 3, 63). Arm: crack target = Gaussian-blurred one-hot (sigma 0.7 px; second arm per-source sigma), JML replaces soft Dice. Kill as arm 2. Prior overlap: offset-tolerant CE (P14) is a different mechanism (min over shifts, at 10% labels).
4. **GeoLS** (row 4, 60). Pre-check without training: on train cells, does the GeoLS soft-label peak sit closer to the darkest ridge than the raw label? If not in most cells, stop. Then the same arm as 3 with geodesic soft labels.
5. **CC-DiceCE / BiCC on crack** (rows 6, 7). Two arms. Kill: components >= 20 px found < +0.02 at relP@2 drop <= 0.02 (BiCC) or crack IoU drop > 0.012. Read E1 false-alarm components in half-cut cells for BiCC.
6. **Multi-class CC / blob** (row 8). Kill: mIoU_rob < +0.01 and inactive IoU < +0.03, with crack IoU not worse than -0.012.
7. **Region-size term** (row 9). CE + L1 proportion term; kill: crack IoU < +0.012 and no relR@2 gain at relP@2 >= 0.90.
8. **DML** (row 10): runs inside arms 1 to 4 (DML vs house soft Dice on the same soft targets).
9. **Lovasz** (row 11): CE + Lovasz hinge (crack), per batch; kill: crack IoU < +0.012.
10. **Label relaxation** (row 12): kill: crack IoU < +0.012 at equal relP@2. Prior overlap: offset-tolerant CE (P14) used a min over shifts at 10% labels; relaxation sums probabilities over the window, at 100% labels; still open.
11. **Unified Focal** (row 13): paper defaults; kill: relR@2 not up by 0.02 at relP@2 drop <= 0.05.
12. **Recall loss** (row 14): kill: gridline IoU < +0.03 and splice still 0.
13. **BLSS** (row 15): kill on calibration: crack ECE in a 2 px band not down 20% on val; IoU must stay within -0.012.
14. **1 px dilated crack labels** (row 16): kill: crack IoU on original labels < +0.012 or relP@2 drop > 0.05.
15. **Fine-grained IoU** (row 17): no training; rescore val predictions of SUP100, PF, FINAL with per-cell and worst-k IoU; keep as benchmark secondary metrics if they rank models differently or narrow CIs.
16. **RankSEG-RMA** (row 18): no training; replace argmax on FINAL probabilities; kill: pooled crack IoU < val-bias + 0.005.

Order suggested (S): 1 (with 5 as control) and 2 first (8 A6000s: 5 seeds each, about one day), 3 and 4 after the GeoLS pre-check, 5 and 6 in parallel, then 7 to 14 as one sweep day; 15 and 16 are CPU / inference only and can run any time.

## 5. Notable papers rejected

- blob loss (doi:10.1007/978-3-031-34048-2_58): superseded by CC-DiceCE and BiCC (both reported better than blob).
- SoftSeg (doi:10.1016/j.media.2021.102038): soft-label regression idea, superseded for thin structures by SAUNA (same idea plus thickness-aware targets and a soft-compatible IoU loss).
- Eelbode et al. 2020 (doi:10.1109/tmi.2020.3002417): theory that Dice and Jaccard losses approximate each other and weighted CE cannot; no own experiment, used as context for the benchmark loss axis.
- Galdran et al., optimal CE + soft Dice combination with OOD robustness (doi:10.1007/978-3-031-26354-5_4, arXiv 2209.06078): abstract not retrievable; worth reading if a CE:Dice weight sweep with E1 as the OOD read is run.
- Observer choice and threshold selection (arxiv:2609.25597): retinal vessels, random forests; supports reporting which annotation was used to tune the threshold (benchmark protocol note), no score gain.
- Margin-based label smoothing for segmentation calibration (doi:10.1016/j.media.2023.102826) and neighbour-aware calibration (doi:10.1016/j.media.2025.103501): calibration targets, little expected IoU gain; BLSS covers the boundary case.
- Nordstrom et al., noisy soft-Dice (arXiv 2304.00801): theory of soft-Dice volume bias under noisy labels; reference only.
- Batching Soft IoU (doi:10.1109/lsp.2019.2956367): covered by computing JML over the whole batch.
- Auto Seg-Loss (arxiv:2010.07930): loss search, expensive, no soft labels.
- Loss function inversion for steel bridge cracks (doi:10.1016/j.autcon.2024.105896): abstract does not define the loss.
- Rill-Garcia et al., inaccurate crack annotations (doi:10.1016/j.neucom.2022.01.051): label correction, belongs to the label-refinement direction.
- Unified loss for inter / intra class imbalance (doi:10.1609/aaai.v39i8.32956), InformationGainLoss (doi:10.1016/j.neucom.2026.133777), ABeDice (doi:10.1016/j.bspc.2025.107741): incremental compound losses, no thin-structure evidence.
- FMS2 flow matching for thin structures (arxiv:2603.13659), TMAL affinity learning (arxiv:2611.13511), TRACE (arxiv:2610.22210): formulation or topology changes, belong to D10 / D11.
- Long-tail detection losses (Seesaw, EQL v2, EFL): instance detection, not dense thin classes.

## 6. Gaps

- Semantic Scholar snippets were rate-limited in both sessions, so BLS / SVLS evidence on thin structures inside papers was not checked; only JML and SAUNA full text were read.
- No paper tests IoU or soft-label losses on 1 to 2 px jittered labels; SAUNA is the closest (thin retinal vessels). Arms 2 to 4, 10 and 14 are our own adaptation.
- Code for the 2026 multi-class instance loss and BLSS not found; label relaxation repo not verified.
- Source-conditional soft labels (sigma per source, or a source token) touch the label-style direction (D17).
- RankSEG and fine-grained IoU are per-image; no pooled-IoU decoder was found. A pooled-IoU threshold search on val is the trivial version and is already done (logit bias).
- Component-wise and topology losses beyond clDice (Betti matching, CAPE) belong to D10.
