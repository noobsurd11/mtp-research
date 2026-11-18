# D10: Topology- and connectivity-aware losses (literature scout, 13 Nov 2026)

Scope: losses, augmentations, small heads and post-processing steps that target connectivity of thin structures, beyond the two already run here (soft clDice: fail; Skeleton Recall w 1.0: wider predictions, test IoU worse, E1 detection up; w 0.1: narrow E1 relF1@2 pass, fresh-seed replication trained but not scored).

Tags: R = what the paper measured, E = what our files measured (from BRIEF), S = my judgement.
This is the second pass on D10. The first pass (12 Nov) left a file here; this pass re-checked its claims against full text, corrected one (TRACE, see finding 3), and added SCNP and TRACE numbers, the TopoMortar CrackTree table, Öner numbers and TopoInteraction.

## Main findings

1. **Strict overlap vs topology on cracks with rough 1 px labels (R, TopoMortar arXiv 2503.03365, Table 1, nnU-Net, 10 seeds, CrackTree 147/17/42).** Dice / beta0 error: CEDice 0.78 / 84.3, cbDice 0.76 / 84.6, Warping 0.77 / 94.9, clDice 0.54 / 22.1, Skeleton Recall 0.32 / 14.0, TopoLoss (PH) 0.52 / 145.8. The skeleton losses cut component-count error 4 to 6x and cut Dice by 0.24 to 0.46. The authors state that clDice and Skeleton Recall "produced thick segmentations" that matched the real crack better than the 1 px ground truth. With the ADELE noisy-label method, every loss got thicker again and lost Dice (CEDice 0.78 to 0.75, beta0 84 to 52). E: this is the same pattern as our Skeleton Recall w 1.0 run (wider, IoU down, detection up). S: any loss that adds recall pressure toward a fixed 1 to 2 px line will widen predictions on our data and cost strict IoU. Losses worth testing either (a) push both directions (SCNP), (b) let the supervised point move with the prediction (TRACE with a widened support, Öner snakes), or (c) work through augmentation or soft labels (CoLeTra, self-distillation).
2. **Effect on predicted width.** No paper reports predicted width directly. Indirect: TopoMortar (above); SCNP is symmetric (foreground logits take the worst foreground neighbour, background logits take the worst background neighbour), so it penalises false positives next to the line as hard as misses on it, and reported no Dice loss on Crack500, TopoMortar, FIVES (R). S: SCNP should not widen; its risk on our data is the opposite (extra penalty on pixels 1 px off a jittered label). Every arm must log predicted crack width (predicted area / predicted skeleton length) next to the ground truth median of 1.75 px.
3. **Correction to pass 1 on TRACE.** TRACE's reconnection candidates are only target pixels (Y(x) = c) inside the 3x3 neighbourhood of each skeleton point (R, Sec. 3.1). On a 1 to 2 px label it therefore stays on the drawn line; it is a hard-pixel recall term, not jitter tolerant as published. It becomes jitter tolerant only if we widen the support T_v (for example, label dilated by 1 px) for the TRACE term alone. R: DeepCrack (CS2-Net backbone, Dice+CE base): Dice 82.78 to 85.20, beta 6.16 to 3.69, clDice 89.03 to 91.10; Skeleton Recall 84.26 / 4.74; clDice 84.58 / 5.06. TRACE + SCNP also stacked on DRIVE and DSCA.
4. **Connectivity post-processing.** R (SCNP appendix E): binary closing on CEDice output cut beta0 10.82 to 8.79 on FIVES and 11.77 to 9.92 on DeepGlobe roads, less than SCNP training (6.94 / 6.56). S: closing is free to test on our val set but will widen 1 to 2 px predictions; a skeleton-gap bridge (join predicted crack endpoints within k px along the dark ridge, drawn at 1 px) is the width-safe version. For inactive, a class-interaction rule is cheap: 99% of inactive regions touch a crack label (E), so drop predicted inactive components with no predicted crack within k px.
5. **Benchmark.** Pitfalls (IPMI 2025) and TopoMortar give concrete rules for topology scoring: fix 8- vs 4-connectivity, audit ground truth for topological artefacts (our sub-20 px crack fragments), never report Betti errors without overlap, run 10 seeds with paired permutation tests (TopoMortar showed any loss can be made to look best by picking a seed). Skeleton Recall, clDice, cbDice, clCE and SCNP are the losses a credible thin-structure benchmark would include; TRACE is the newest (Oct 2026, code on acceptance).

## Queries run

This pass (13 Nov), Research MCP search_papers (Scopus and ScienceDirect returned HTTP 401, Semantic Scholar rate-limited, arXiv often timed out; most hits came from OpenAlex):
1. topology preserving segmentation loss (2020+)
2. cbDice centerline boundary aware Dice tubular (2020+)
3. Betti matching topological loss segmentation (2020+)
4. Topograph component graph topological segmentation loss (2023+)
5. warping loss homotopy critical pixels topology segmentation (2020+)
6. crack segmentation topology connectivity loss thin cracks (2022+)
7. adjusting ground truth annotations connectivity delineation imprecise labels snakes (2020+)
8. topological interactions multi-class segmentation containment exclusion constraints (2021+)
9. topology-aware loss thin structure segmentation (2025+)
10. post-processing reconnect broken segments curvilinear segmentation gap closing (2021+)
11. topology loss robust to noisy or misaligned annotations thin structures (2023+): nothing relevant
12. persistent homology loss segmentation efficient (2025+)
13. blob loss connected component wise loss instance imbalance (2022+)
14. skeleton-based loss crack segmentation pavement connectivity (2025+)
15. tolerance band distance-weighted loss thin structure label misalignment centerline (2024+): nothing relevant

search_snippets: 4 attempts (width under topology losses, clDice on 1 px crack labels, CoLeTra results, thickness), all refused by the Semantic Scholar rate limit.
Snowballing: similar_papers on SCNP + TRACE + TopoMortar; get_citations on Skeleton Recall (85 citing).
Full text read: TopoMortar (Tables 1 and 2, Sec. 4.3, 4.4), SCNP (Sec. 3.1, 4.1, 4.2, 5, App. E, F), TRACE (fetched; Sec. 3.1, 4.1 to 4.3, 5), Öner 2022 (Sec. III-B, IV-A, E, G).
get_paper: TMAL, clCE, CoLeTra, WPRF, Pitfalls, Topology-Guaranteed width constraints, Universal Topology Refinement, TopoInteraction, STC-Net.
WebSearch (6): SCNP venue and code, TMAL code (not found on the web), Topograph code, Betti-Matching-3D code, cbDice code, clCE code.
Pass 1 (12 Nov) ran 19 further searches (clCE, DconnNet, differentiable skeletonization, TopoTTA, efficient PH and others) and 9 web searches; its findings were kept where re-verified.

## Selected papers

Score = value for our scores (task rubric). Bench = value for the benchmark vision. Code "paper" = URL stated in the paper abstract or project page as retrieved; "web" = confirmed by WebSearch. No repository was opened.

| # | id | year | venue | code | mechanism | adaptation to our data | score | bench |
|---|---|---|---|---|---|---|---|---|
| 1 | arxiv:2603.18671 (SCNP) | 2026 | CVPR | github.com/jmlipman/SCNP-SameClassNeighborPenalization (paper, web) | Before the loss, each foreground logit takes the worst value among its same-class foreground neighbours and each background logit the worst among background neighbours; 3 lines, no inference cost, wraps CE / Dice / clDice / Skeleton Recall | Wrap the house CE + Dice on all 24 channels, window w = 3 (paper: best w is about the structure width; ours is 1 to 2 px). Thin classes (crack, gridline recall 0.33, splice) gain most in theory. Jitter risk: background pixels 1 px off the drawn crack get the max off-line crack logit, which may narrow and miss the true ridge; second arm applies SCNP to all classes except crack | 66 | 70 |
| 2 | arxiv:2503.03365 (TopoMortar) | 2025 | arXiv | jmlipman.github.io/TopoMortar (paper) | Controlled benchmark of 8 topology losses under small data, pseudo and noisy labels, OOD. Self-distillation (3 rounds, each trained on the previous round's soft labels) raised Dice and topology with noisy labels | Self-distillation on PF: 3 x 6.7k steps, rounds 2 and 3 trained on the round-1 / round-2 softmax for all classes (soft crack labels widen around jittered traces). Protocol (10 seeds, permutation tests, Betti next to Dice) as the benchmark template | 62 | 85 |
| 3 | arxiv:2503.05541 (CoLeTra) | 2025 | arXiv | github.com/jmlipman/CoLeTra (paper) | Augmentation: paint background-like texture over short stretches of thin structures and keep the label, so the model learns that apparent breaks are connected; claimed to work with topologically inaccurate labels | Paste same-cell local background over 3 to 10 px stretches of crack and gridline only (never over inactive). Targets faint cracks (7% under 2% contrast) and E1 misses (70% of E1 crack pixels at p < 0.001). Labels unchanged, so no width bias. Keeps the label-safe rule otherwise | 62 | 45 |
| 4 | arxiv:2610.22210 (TRACE) | 2026 | arXiv | none (on acceptance) | For each skeleton point whose removal splits the local target skeleton, find the easiest valid reconnection under the current prediction and supervise its bottleneck pixel with a centred logit margin | In-house, about 150 lines, 3x3 local search only. Widen the candidate support to the label dilated by 1 px so the reconnection can follow the true ridge (not in the paper). Crack class only, weight from {0.1, 0.3} on val. R: DeepCrack Dice +2.4, beta 6.16 to 3.69 | 58 | 50 |
| 5 | doi:10.1007/978-3-031-72111-3_67 (clCE) | 2024 | MICCAI | github.com/cesaracebes/centerline_CE (paper, web) | CE evaluated on the label skeleton (recall) and on the predicted skeleton (precision), added to CE; keeps CE's tolerance to label noise | Crack only, weight 0.25. The predicted-skeleton term penalises thin false lines (scuff on E1, gridline confusions), so it should widen less than Skeleton Recall. R (SCNP App. F, FIVES): clCE beta0 10.62 vs CEDice 10.82, SCNP 6.94, Dice equal. A reviewer flagged sign errors in Eq. 5 and 6; follow the code | 48 | 65 |
| 6 | doi:10.1109/tmi.2022.3193072 (Öner, annotations as snakes) | 2022 | IEEE TMI | github.com/doruk-oner/AdjustingAnnotationswithSnakes (paper) | Centreline annotations become active contours that move toward the network's evidence during training while keeping topology; loss on the distance map of the moved line | Skeletonise each crack label into a polyline graph, snake it toward the model's crack ridge within 2 px every N steps, redraw at each source's label width (ARTS 1.5, CSIR 1.75, BMRK 3.0). R: small pixel gains, larger APLS gains; degrades much slower than plain training as annotation deformation grows. Held by D11 too | 45 | 40 |
| 7 | arxiv:2607.07123 (WPRF) | 2026 | arXiv | none stated | Differentiable max-min (widest path) reachability on a domain-restricted graph sends gradient to the bottleneck pixels that break connectivity | Domain = crack label dilated by 2 px (absorbs jitter), endpoints from the label skeleton. Same goal as TRACE with a global solver; run only if TRACE helps. R: 87% of experiments improved (9 architectures, 6 datasets), clDice +7.2 pts on fragile sets | 42 | 35 |
| 8 | doi:10.1007/978-3-031-19818-2_40 (TopoInteraction) | 2022 | ECCV | github.com/TopoXLab/TopoInteraction (paper) | Convolutional module that penalises forbidden class adjacencies (containment, exclusion) during training | Our class layout has hard rules: inactive touches crack (99%), crack never on padding or frame_edge. Cheapest form is the inference rule (drop inactive components with no predicted crack within k px). Training form: exclusion penalty between inactive and padding / frame_edge | 40 | 25 |
| 9 | arxiv:2611.13511 (TMAL) | 2026 | arXiv | github.com/suho-han/TMAL (paper; not found by web search) | Soft directional affinities at several offsets, weighted toward thin regions, plus an auxiliary segmentation branch | Affinity head for crack and gridline on U-Net++, offsets 1, 2, 4 px so a 1 px jitter does not break the target. Held by D09 / D12; listed here because it is the newest connectivity formulation with crack evidence (DeepCrack) | 40 | 40 |
| 10 | doi:10.1007/978-3-031-72980-5_13 (Skeleton Recall) | 2024 | ECCV | nnU-Net integration (used here) | Recall loss on a tubed label skeleton | Already run. Open item: score the trained w 0.1 fresh-seed replication with the width diagnostic | 40 | 85 |
| 11 | arxiv:2411.03228 (Topograph) | 2025 | ICLR | github.com/AlexanderHBerger/Topograph (web) | Component graph of prediction and label finds topologically critical regions; strict homotopy metric; up to 5x faster than PH losses | Crack class, 0-dim (component) errors only, on label components >= 20 px. Its homotopy metric is a candidate topology score for the benchmark | 35 | 60 |
| 12 | arxiv:2211.15272 + arxiv:2407.04683 (Betti matching) | 2022 / 2024 | arXiv | github.com/nstucki/Betti-Matching-3D (web) | Persistent-homology loss with spatially induced matching between predicted and label barcodes (C++) | Crack class, components only, label components >= 20 px. Could raise component recall (0.798 at >= 20 px). R (TRACE paper): needs weights of 1e-5 to 1e-2 or Dice drops | 33 | 60 |
| 13 | doi:10.52202/068431-1746 (Warping loss) | 2022 | NeurIPS | unverified | Penalise only pixels whose flip changes topology, found by homotopic warping of the prediction toward the label | A jittered but topologically equal prediction gets no extra loss, which suits our labels. R (TopoMortar CrackTree): Dice 0.77 (kept) but beta0 94.9 vs 84.3 (no gain); with ADELE 46.4. CPU warping per batch | 32 | 45 |
| 14 | doi:10.1007/978-3-031-72111-3_5 (cbDice) | 2024 | MICCAI | github.com/PengchengShi1220/cbDice (paper, web) | clDice plus boundary and radius-normalised terms to balance thin and thick branches | Crack radius is about 1 px everywhere, so on crack cbDice reduces to near clDice (failed here). R (TopoMortar CrackTree): Dice 0.76, beta0 84.6 (no gain) | 28 | 65 |
| 15 | doi:10.1007/978-3-031-96628-6_20 (Pitfalls) | 2025 | IPMI | github.com/AlexanderHBerger/topo-pitfalls (web, pass 1) | Connectivity choice, ground-truth artefacts and metric misuse change method rankings | Benchmark rules: 8-connectivity for crack components, audit tiny label fragments, report Betti / component metrics only with IoU and relF1@2 | 15 | 80 |
| 16 | doi:10.1016/j.conbuildmat.2022.128264 (TOPO-Loss cracks) | 2022 | Constr. Build. Mater. | github.com/eesd-epfl/topo_crack_detection (paper) | Connectivity loss for masonry cracks with imprecise labels | R (TopoMortar): TOPO gave empty masks on CrackTree and beta0 33.7 vs 3.3 ID. Reference only | 15 | 35 |
| 17 | arxiv:2608.01714 (STC-Net) | 2026 | MERCon / arXiv | none stated | EL crack segmentation with edge, spectral priors and a boundary-topology refinement module | Only EL topology paper found. PVEL-S binary masks, 72.52 mIoU on test, no ablation of the topology module. Belongs in the benchmark's related work, not the method suite | 12 | 40 |

## Cheapest decisive experiments (priority order)

All arms on PF (or house), 5 seeds vs the 5-seed baseline, same commit and data. Diagnostics for every arm: clean-49 crack IoU, relF1@2 (relP@2, relR@2), crack components >= 20 px found, gridline IoU, inactive IoU, mIoU_rob, E1 crack relF1@2, and predicted crack width (predicted area / predicted skeleton length) against the 1.75 px label median. Smallest detectable crack IoU change is about 0.012.

1. **Score the Skeleton Recall w 0.1 replication** (0 GPU-h). Decides whether that line stays open.
2. **Post-processing on existing checkpoints** (0 GPU-h, val only to pick k): (a) skeleton-gap bridge for crack, (b) inactive-without-crack removal. Kill (a) if val relF1@2 gain < 0.005 or crack IoU falls; kill (b) if val inactive precision gain < 0.03 at recall loss > 0.01.
3. **SCNP** (2 arms: all classes; all except crack; about 12 GPU-h). Kill if crack IoU < baseline - 0.012 and gridline IoU gain < +0.02 and E1 relF1@2 gain < +0.02.
4. **CoLeTra** (crack + gridline, about 6 GPU-h). Kill if E1 crack relF1@2 and test component recall both gain < +0.02, or relP@2 falls > 0.02.
5. **Self-distillation** (3 rounds within 20k steps, about 6 GPU-h). Kill if crack IoU gain < 0.012 and relF1@2 gain < 0.01.
6. **TRACE with 1 px dilated support** (2 to 3 days to implement, about 6 GPU-h). Kill if relF1@2 gain < 0.01 or width rises > 15%.
7. clCE (w 0.25) only if 3 and 6 fail; Öner snakes, WPRF, Topograph and Betti matching only as one-arm long shots.

## Rejected (one line each)

- Pereira et al. 2025 clDice + IoU on road cracks (doi:10.3390/futuretransp5040177): +4.9 Dice only against BCE alone; soft clDice already failed here.
- Pereira and Fukai 2025, Skeleton Recall on road cracks (doi:10.1109/soli66289.2025.11396263): same mechanism as our Skeleton Recall run.
- DconnNet (doi:10.1109/cvpr52729.2023.01109): connectivity head, held and scored by D11.
- TopoTTA (doi:10.1109/iccv51701.2025.02236): test-time adaptation, held by D12 and D30.
- BiCC (arxiv:2609.30223) and blob loss (doi:10.1007/978-3-031-34048-2_58): component-wise losses, held by D20 / D18.
- Topology-Guaranteed segmentation with width constraints (doi:10.1137/25m1765870): variational PH + width prior; the only paper found that models width explicitly, but no code and no learning benchmark on thin labels.
- Universal Topology Refinement (doi:10.1007/978-3-031-72114-4_64): learned post-hoc refiner trained on synthetic polynomial shapes; abstract not retrievable, aimed at blobby organs.
- GLCP (doi:10.1007/978-3-032-05325-1_23): multi-head with discontinuity maps; TRACE / WPRF test the same idea as a loss.
- Menten differentiable skeleton (doi:10.1109/iccv51070.2023.01956): fixes soft-skeleton errors, but on 1 to 2 px cracks the soft skeleton is about the mask; the clDice failure is more likely the Dice-type gradient.
- Fast Euler characteristic (doi:10.1109/tmi.2025.3589495), persistence image (doi:10.1109/isbi61048.2026.11515783), spatial-aware PH matching (doi:10.1109/iccvw69036.2025.00607), supervoxel loss (doi:10.1609/aaai.v39i3.32326): compute tricks or variants of PH / critical-component losses; Betti matching and Topograph represent them.
- SEMIR graph minors (arxiv:2606.24935), FMS2 flow matching (arxiv:2603.13659), crack foundation model (arxiv:2606.05641), TopoLoRA-SAM (arxiv:2601.02273): new pipelines, belong to architecture / generative / foundation-model directions.
- Contextloss (doi:10.1109/icip55913.2025.11084563), coDice (doi:10.1117/12.3047030), HarmonySeg (doi:10.1109/iccv51701.2025.02188), CLGeoDice (doi:10.1145/3795892.3795903): vessel-specific variants with little beyond the selected losses.

## Gaps

- No paper measures predicted width under topology losses; TopoMortar only notes it qualitatively. We must measure it ourselves (diagnostic above).
- No topology loss evaluated with 1 to 2 px labels jittered by about 1 px with strict IoU as the target; CrackTree in TopoMortar is the closest (1 px labels, Dice only).
- No topology loss evaluated on EL apart from STC-Net (no ablation).
- search_snippets was unavailable all session (Semantic Scholar rate limit), so evidence questions were answered from full text of 4 papers only. CoLeTra and WPRF numbers are from abstracts.
- Code for TRACE, WPRF, warping loss unverified or unreleased. TMAL's stated repo was not found by web search.
- Sub-directions for their own search: (1) label refinement of thin structures (snakes, ridge snapping), held by D11 / D16; (2) topology metrics for the benchmark (Topograph homotopy metric, Betti at fixed connectivity, "Benchmarking evaluation metrics for tubular structure segmentation", doi:10.1007/978-3-032-06774-6_7, not read); (3) class-interaction priors for inactive given crack.
