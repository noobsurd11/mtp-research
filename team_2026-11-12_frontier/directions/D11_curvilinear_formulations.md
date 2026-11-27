# D11: Alternative output formulations for thin lines (literature scout, rerun 13 Nov 2026)

Scope: distance / centreline heat-map regression, orientation and direction fields, connectivity and affinity maps, graph and polyline extraction (roads, vessels), point / line set prediction, implicit or sub-pixel outputs. Question for each: is it robust to 1 to 2 px label jitter, and can its output be rasterised at a chosen (per-source) width?

This file replaces the 12 Nov version (that scout wrote the file but never returned a result). It keeps the 12 Nov picks that still hold, re-verifies their ids, and adds 2025 to 2026 work found today (TMAL, Kordon heatmaps, Xu / Okatani label-error study, EBT loss, SEMIR, CrackGeoFM).

Tool notes: in Research MCP only OpenAlex answered (Scopus and ScienceDirect HTTP 401, Semantic Scholar rate-limited all session, arXiv timed out on some calls). `search_snippets` failed 3 of 3 times (S2 rate limit), so there is no snippet evidence in this file. One full text read (TMAL, method and results). Code links: (A) = stated in the paper abstract as returned by the tool; (W) = seen in a web search result; "unverified" = no tool showed a repo.

## Queries run this session (32)
search_papers (OpenAlex; year_from as given):
1. centerline distance transform regression segmentation thin structures (2020+)
2. crack segmentation distance transform regression (2023+)
3. directional connectivity segmentation curvilinear (2023+)
4. road network graph extraction satellite vectorized (2024+)
5. orientation field auxiliary task thin structure segmentation connectivity (2021+)
6. Gaussian heatmap soft label crack detection annotation tolerance (2021+)
7. YoloCurvSeg noisy skeleton label curvilinear (2022+)
8. sub-pixel curvilinear structure centerline implicit representation segmentation (2021+)
9. crack centerline skeleton and width joint prediction (2022+)
10. line segment detection transformer curve set prediction lane polyline (2023+)
11. thin structure segmentation distance transform auxiliary regression (2025+)
12. crisp edge detection label noise thick annotation (2025+)
13. multiscale centerline detection regression distance function Sironi (any year)
14. crack graph extraction keypoint vectorization topology deep learning (2023+)
15. power line wire segmentation thin one pixel heatmap (2021+)
16. vector field flux representation tubular curvilinear segmentation (2021+)
17. centerline heatmap regression vessel segmentation (2025+)
18. crack segmentation soft label uncertainty boundary annotation ambiguity tolerance (2024+)
19. How Do Label Errors Affect Thin Crack Detection by DNNs (title check)
20. affinity learning crack segmentation multi-offset connectivity (2025+)
21. edge detection multiple annotators label uncertainty distribution (2024+)
22. attraction field line representation regression offset to nearest line pixel (2020+)
23. crack detection curve parametric Bezier polyline prediction (2022+)

search_snippets (all failed, S2 rate limit): distance-map regression robust to annotation misalignment; centreline regression vs classification under inaccurate annotations; thin crack label shifted by one pixel.

Snowball: similar_papers on TMAL + DconnNet + Kordon; get_citations on DconnNet (153 citing) and Deep Distance Transform (154 citing).

WebSearch (6): TMAL code; DconnNet code; YoloCurvSeg code; 2025 to 2026 crack distance-map regression with label misalignment; Kordon heatmap code; (the 12 Nov run also checked Batra, STEAL, UAED, FMS2 code).

## The judgement that applies to every paper here (S)
Strict crack IoU is scored against a jittered label (BRIEF 2: 1 px shift of a perfect mask = IoU 0.56; team E in `cards/T3_label_alignment_family.md`: 48% of label skeleton points lie within 1 px of the darkest ridge point, 36% beyond 2 px, systematic offset only 0.2 px). A jitter-robust formulation puts its line on the ridge, not on the annotator's line. On its own it should therefore raise relF1@2, component recall and E1 detection, not strict IoU. Strict IoU can rise only through the rasterisation step: draw the extracted centreline at a width chosen per source (ARTS 1.5, CFVS / CSIR 1.75, BMRK 3.0, SDLE 3.25 px). So every arm below is read first on relF1@2 and components >= 20 px found, with width ratio and strict IoU as guards, and second on strict IoU after per-source-width rasterisation.

Zero-GPU check E0 (still not run, partly covered by T4 arm 1 per-source bias / width op): skeletonise the house ensemble's crack prediction on CV out-of-fold dumps, redraw at w in {1, 2, 3, 4} px per source, measure strict IoU vs w. If no w beats the raw mask, centreline-output arms are judged on relF1@2, components and E1 only.

## Selected papers
score = value for our scores (task rubric). bench = value for the benchmark suite / scoring design. Status column = where the mechanism already sits in the team's wave-2 cards (not BRIEF 5; none of these mechanisms was run in BRIEF 5).

| # | id | year | venue | code | mechanism | adaptation to our data | score | bench | status |
|---|---|---|---|---|---|---|---|---|---|
| 1 | doi:10.1109/tmm.2022.3203870 (FIDT) | 2022 | IEEE TMM | unverified | Regress a focal inverse distance transform map (sharp peak on the label, smooth fall-off); read out by local maxima | Crack-only aux head: target from distance to the label skeleton (1.0 at 0 px, 0.5 at 1 px). Team pre-check (E): FIDT targets of a mask and its 1 px shift correlate at median 0.919 vs binary IoU 0.548 | 68 | 35 | T5 arm 4 (GO, stacked with #2) |
| 2 | doi:10.1109/cvpr.2019.01063 (Batra orientation) | 2019 | CVPR | github.com/anilbatra2185/road_connectivity (W) | Joint orientation-bin prediction along the road skeleton plus a refinement net that closes gaps | 16 orientation bins from crack skeleton second moments; team pre-check (E): 95.8% of px stay within +-1 bin under a 1 px shift. Also usable for gridline (IoU 0.283), whose orientation is fixed by layout | 62 | 35 | T5 arm 4 (GO) |
| 3 | arxiv:2611.13511 (TMAL) | 2026 | arXiv | github.com/suho-han/TMAL (A; web search did not find it) | Predict soft directional affinities at several offsets (s = 1, 2, rotated 2'), fuse them with decoder-derived weights, decode to an inverted-distance map, threshold; auxiliary mask branch | Its target (inverted EDT of the mask) is degenerate on 1 to 2 px cracks: every crack px has EDT 1, so d_max = d_min. Replace it with a Gaussian tube around the label skeleton (sigma about 1 px, the measured jitter) and build affinities as products of tube values; offsets s in {1, 2} so links bridge a 1 px gap. Crack channels only (2 x 8 + 8), house 24-class CE head kept; final crack = argmax with the TMAL map as crack logit, or TMAL map > tau chosen on val | 62 | 60 | new; not in cards (DconnNet parked in T2 for cost) |
| 4 | doi:10.1109/tip.2023.3289296 (Canny-guided label refinement) | 2023 | IEEE TIP | unverified | Refine human edge labels to the subset of over-detected Canny edges that best aligns with them; train on refined labels | Swap Canny for a multi-scale dark-ridge detector (Hessian / Frangi) on EL; snap each crack label segment to the nearest ridge within 2 px; keep unmatched px. Train on snapped labels; also yields a ridge-snapped re-scoring of test labels for the benchmark | 60 | 60 | T4 family mentions it |
| 5 | doi:10.1109/cvpr52729.2023.01109 (DconnNet) | 2023 | CVPR | github.com/Zyun-Y/DconnNet (A, W) | 8-neighbour connectivity maps per class, decoder splits directional sub-spaces; mask = connectivity vote | Connectivity output for crack and inactive only (2 x 8 channels) on the house encoder; 24-class CE head kept. Same degenerate-target caveat is milder (binary connectivity is defined on 1 px lines but flips under 1 px jitter) | 55 | 70 | T2: PARKED for cost |
| 6 | doi:10.1038/s41598-023-41221-2 (Kordon heatmaps) | 2023 | Sci. Rep. | unverified (web search found none) | Encode a curve and its positional uncertainty as a heatmap: curve distribution convolved with a filter, approximated by a distance-dependent function in linear time | Set the filter width per source from measured label-to-ridge offsets (team E, T3 family). This is the principled version of the soft band in T2 `soft_band_jml`, but as a regression target on a separate head, so it cannot widen the argmax. Read out by ridge NMS then draw at source width | 55 | 30 | close to T2 soft_band_jml (different loss and head) |
| 7 | doi:10.1109/tmi.2022.3193072 (Oner, adjusting annotations) | 2022 | IEEE TMI | github.com/doruk-oner/AdjustingAnnotationswithSnakes (A) | Treat centreline annotations as active contours that deform during training while keeping topology; network and labels optimised jointly | Crack mask -> skeleton -> polylines; each epoch let polylines move up to 2 px toward the network's ridge (snake energy = network output + smoothness); rasterise at source width as the new target. Code is 3D, the 2D port is the work | 52 | 30 | T2 notes it as label refinement (D16 family) |
| 8 | arxiv:2602.20689 (MatchED) | 2026 | arXiv (CVPR 2026 per project page) | cvpr26-matched.github.io (A) | Each iteration, one-to-one matching of confident predicted px to label px within tau_d; matched GT replaces the label | tau_d = 2 px on crack only, on PF. Differs from BRIEF 5 offset-tolerant CE by the one-to-one constraint (cannot reward width) | 52 | 45 | T3 matched_crack_head (FIX: tau_d = 0 control) |
| 9 | doi:10.1109/cvpr.2019.01133 (STEAL) | 2019 | CVPR | github.com/nv-tlabs/STEAL (W, inference only) | NMS loss: maximum response along the normal of each label edge; active alignment of labels via level sets | NMS loss across the crack normal (normal from #2's orientation) gives one peak per crack; replace level sets with a +-2 px 1D search along the normal | 50 | 35 | T3 family |
| 10 | arxiv:2507.06569 (EBT loss) | 2025 | arXiv | unverified | Split pixels into edge, boundary (near edge) and texture; give each its own weight in a weighted BCE that generalises WBCE | Crack / band of 1 to 2 px around the label skeleton / rest, with a low weight on the band so the model is not punished for firing on the ridge 1 px off the drawn line. Cheaper than #3 to #8; a config-level loss | 45 | 25 | partial overlap with BRIEF 5 offset-tolerant CE (n.d.): that run tolerated offsets by max-pool; EBT down-weights near-crack negatives instead. Open |
| 11 | doi:10.1016/j.autcon.2026.107190 (CrackGeoFM) | 2026 | Autom. Constr. (arXiv 2606.05641) | unverified | Frozen VFM backbone + frequency crack enhancement + adaptation module + one decoder for mask, skeleton and uncertainty | Take only the multi-task decoder idea: skeleton head (target = label skeleton dilated by 1 px) plus aleatoric uncertainty head on the house model; the skeleton head is the centreline output to rasterise per source. Reports few-shot adaptation from 5 labelled images, relevant to the E1 few-shot track T3b | 45 | 55 | none |
| 12 | doi:10.1109/cvpr42600.2020.00389 (Deep Distance Transform) | 2020 | CVPR | unverified | Multi-task: mask + quantised distance-to-surface map; mask refined by a shape prior rebuilt from skeleton and radius | For cracks use distance-to-skeleton bins 0..4 px; for inactive true distance-to-boundary. Radius head gives crack width per source and inactive area for severity | 45 | 30 | none |
| 13 | doi:10.1109/cvprw59228.2023.00464 (Xu, Zou, Okatani) | 2023 | CVPRW | unverified | Label cracks as 1 px curves with matching training and evaluation; synthesise annotation errors; under-annotation hurts more than over-annotation; polyline approximation costs little | Benchmark: evaluate crack as curves (relaxed F1 on skeletons, our relF1@2) and adopt their error-synthesis protocol to report each method's sensitivity to jitter / under-annotation on CV folds. Model: supports treating crack as a curve target and favouring recall in label refinement | 40 | 75 | none |
| 14 | arxiv:2603.13659 (FMS2 / SegFlow) | 2026 | arXiv | unverified | Segmentation as image-to-mask flow matching; plus mask-to-image synthesis for thin structures | Crack-only binary SegFlow head on the house encoder, or use its synthesis half for crack data. Bold bet | 38 | 50 | T5 family mentions it |
| 15 | doi:10.1007/978-3-031-19803-8_22 (PointScatter) | 2022 | ECCV | github.com/zhangzhao2022/pointscatter (A) | Split image into scatter regions, each predicts a point set; region-wise greedy bipartite matching; points rendered as mask or centreline | Points regressed with L1 after matching land at the mean of jittered labels (sub-pixel); render at source width. Crack only, stride-4 features, 16x16 regions | 42 | 35 | none |
| 16 | doi:10.52202/079017-2187 (GraphMorph) | 2024 | NeurIPS | "soon" (A), unverified | Graph decoder predicts a branch-level graph; SkeletonDijkstra morphs it onto the centreline map; graph used to delete false positives | Use only as a crack false-positive filter (drop components not on a predicted branch); gives crack topology for severity | 35 | 30 | none |
| 17 | doi:10.1109/cvprw63382.2024.00262 (SAM-Road) | 2024 | CVPRW | github.com/htcr/sam_road (A) | Fine-tuned SAM predicts vertex / intersection masks, NMS gives vertices, a small transformer predicts edges: vector graph | Severity, not IoU: crack graph gives crack mode (single line, cross, dendritic) and length per cell for a benchmark severity track | 30 | 45 | none |
| 18 | arxiv:2606.24935 (SEMIR) | 2026 | arXiv | unverified | Replace the pixel lattice with a graph minor whose contraction keeps 1 to 3 px structures connected; GNN classifies supernodes; exact lift back to pixels | Moonshot: build the minor from EL ridge filters so crack px are never merged with background; GNN on the house encoder features. Mainly a fragmentation fix (components found) | 28 | 25 | none |

### Evidence (R = what the paper measured)
1. FIDT: SOTA localisation on six crowd sets and one vehicle set; more robust on negative and very dense scenes. No thin-line test.
2. Batra: +9% (SpaceNet) and +7.5% (DeepGlobe) on the road topology metric over prior SOTA.
3. TMAL (full text read): own 512 x 512 protocol, all baselines retrained. DeepCrack (300 train): IoU 0.743 vs DconnNet 0.713 vs U-Net 0.681; clDice 0.907 vs 0.893 vs 0.859; component error delta-beta0 1.98 vs 4.51 vs 4.93. DRIVE (20 train): IoU 0.709 vs 0.635 (DconnNet), delta-beta0 24.5 vs 452.8. HD95 not best. Loss weights given (aff 0.3, dist 1.0, dice 1.0, bac 0.2, edge 1.0, aux 0.5).
4. Crispness refinement: crispness 17.4% to 30.6%; PiDiNet ODS / OIS +12.2 / +12.6% on Multicue without NMS.
5. DconnNet: several medical benchmarks; third-party pages list DRIVE and CRACK500 (W, not read). In TMAL's retrain it is the strongest baseline on DeepCrack.
6. Kordon: approximation error analysed vs curve type and SNR; applied to surgical 2D / 3D data, semantic boundaries, skeletonisation. No crack test; numbers not read (full text fetch timed out).
7. Oner: 3D delineation (neurons, vessels) with inaccurate annotations; boosts networks trained on them; numbers not read.
8. MatchED: Average Crispness up 2 to 4x; under crispness-emphasised evaluation ODS +20 to 35%.
9. STEAL: +4% MF(ODS), +18.61% AP over CASENet (SBD / Cityscapes boundaries).
10. EBT: better than WBCE on several edge benchmarks with one fixed set of hyperparameters; numbers not read.
11. CrackGeoFM: 20 crack datasets, SOTA segmentation, better topology, calibrated uncertainty, 5-shot adaptation; numbers not read.
12. DDT: six CT datasets, +13% DSC on pancreatic duct.
13. Xu et al.: synthetic error study on 1 px curve labels: under-annotation more harmful than over-annotation; polyline approximation modest impact.
14. FMS2: five crack and vessel sets, IoU 0.511 to 0.599; Betti error 82.1 to 51.5; 25% labels + synthetic near full; cross-domain IoU +0.11 (from 12 Nov abstract read).
15. PointScatter: four tubular sets, segmentation and centreline extraction.
16. GraphMorph: centreline and segmentation on several sets; fewer false positives.
17. SAM-Road: comparable to RNGDet++ on City-scale, about 40x faster.
18. SEMIR: TTPLA power lines, CrackSeg9k, SkyScapes lanes: matches or beats domain baselines on Dice, IoU, Boundary F1; fragmentation at least 4.6x lower than SLIC.

## Minimum experiments (on top of house PF; 2 seeds x 5 folds of cv5v2 for the screen, then 5 seeds on clean-49 test; E1 read last)
- E0 (no GPU): rasterisation headroom, above. Decides how arms A1, A3, A4, A6 are judged.
- A1 = T5 arm 4 as specified (FIDT + orientation aux). Nothing to add from this direction.
- A2 TMAL crack head (#3) with the Gaussian-tube affinity target. Arm: PF + TMAL crack branch (s in {1, 2}), crack logit from the TMAL map. Baseline: PF. Metrics: crack components >= 20 px found and relF1@2 (CV mean), width ratio, strict crack IoU, mIoU_rob as guard. Kill: components found +< 0.02 and relF1@2 +< 0.01, or strict crack IoU down > 0.01. About 25 GPU-h. Control: same head with s = {1} only (= DconnNet-like) to split "soft target" from "multi-offset".
- A3 Ridge-snapped labels (#4). Arm: PF trained on ridge-snapped crack labels. Score on original labels and on snapped CV labels. Kill: CV crack IoU on original labels down > 0.01 with no relF1@2 gain.
- A4 Kordon heatmap head (#6), per-source sigma. Arm: PF + regression head (MSE), dropped at inference vs used as the crack read-out (ridge NMS, draw at source width). Kill: relF1@2 +< 0.01 on CV in both read-outs.
- A5 EBT band weights (#10). Arm: PF with crack-band weight 0.2 on the 1 to 2 px ring. Kill: relF1@2 +< 0.01 or width ratio > 1.2.
- A6 Skeleton + uncertainty heads (#11). Kill: relF1@2 +< 0.01 and E1 relF1@2 +< 0.03.
- Bench (no model change, #13): report every suite method's change in CV relF1@2 when trained on labels with synthetic 1 px jitter and 20% dropped crack segments. Cost: one extra training per method per fold, so restrict to the top 5 methods.

## Notable rejects
- LETR, DT-LSD, ELSD, HAWP / attraction-field line parsers (doi:10.1109/tpami.2023.3312749): straight segments and junctions in man-made scenes; cracks branch and curve; DETR-style training on 478 cells is weak. HAWP's attraction field idea is already covered by FIDT and orientation.
- Lane / HD-map curve transformers (Bezier HD-map doi:10.1109/cvpr52729.2023.01270, CurveFormer++): a few ordered long curves per scene, not our case.
- Recent road-graph methods (doi:10.1109/cvpr52734.2025.00150, DeH4R doi:10.1109/tgrs.2026.3679934, DOGE, LineGraph2Road): large-scale satellite graphs with thousands of training tiles; SAM-Road kept as the cheapest representative, for severity only.
- WPRF (arxiv:2607.07123), TRACE (arxiv:2610.22210), CAPE (doi:10.1007/978-3-032-05162-2_18): connectivity losses, not output formulations; belong to D10.
- YoloCurvSeg (doi:10.1016/j.media.2023.102937): synthesis from one noisy skeleton by inpainting; belongs to D06 synthesis; crack copy-paste was n.d. here (BRIEF 5), though its inpainted-background trick differs.
- CurvSegFlow (arxiv:2606.21608): flow-matching segmentation for microscopy; FMS2 is the closer, crack-tested version.
- TopoTTA (doi:10.1109/iccv51701.2025.02236): test-time adaptation for tubular structures; relevant to E1 but belongs to a TTA / UDA direction.
- RankED, UAED, LIOT, HoughNet U-Net, directional-connectivity crack net (doi:10.1109/tits.2024.3488656): losses, inputs or architectures; covered by T2, T5, D12 and D13.
- Skeleton-aware distance transform (instance glands), DeepFlux (natural-image skeletons): no thin-line benefit beyond FIDT + orientation.

## Gaps
- No snippet evidence (S2 rate-limited all session) on whether distance or heatmap targets help under 1 to 2 px label jitter in published work; the team's own CPU pre-check (T5) is the only measurement, and it covers target stability, not model gain.
- No paper combines centreline output with per-source rasterisation width. That is our own idea; E0 decides it.
- No EL paper uses a non-mask output formulation (12 Nov query; nothing new today).
- TMAL's affinity target as published does not work on 1 px masks; the Gaussian-tube replacement is untested anywhere.
- Code unverified for TMAL (abstract only), Kordon, Canny refinement, EBT, CrackGeoFM, Xu et al., FMS2, GraphMorph, SEMIR, FIDT.
- Sub-directions worth their own search: (a) metric design for curve labels (Xu / Okatani's evaluation, relaxed F1 on skeletons, Betti matching) for the benchmark; (b) crack graph and width descriptors for severity; (c) test-time adaptation for thin structures under domain shift (TopoTTA) for E1.
