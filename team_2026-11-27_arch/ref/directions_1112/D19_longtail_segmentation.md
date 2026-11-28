# D19 Long-tailed and class-imbalanced segmentation (full supervision)

Scout: D19, 13 Nov 2026. Status: final (resumed from the 12 Nov WIP notes after the Research MCP outage).
Labels used below: R = what a paper measured, E = what our files measured, S = my judgement.

## 1. Why this direction matters for us (E, from BRIEF and handbook)
- mIoU_rob averages the 13 classes with ground truth in at least 3 test cells. **splice is one of them (4 test cells) and scores 0.000 because it is never predicted.** Lifting splice from 0 to 0.30 alone would add about +0.023 mIoU_rob, more than any method has moved mIoU_rob so far. gridline +0.10 would add about +0.008.
- splice is present in 53 of 478 train cells; edge_dark in 41; inactive in 42 (handbook `trackM/design.md`). They are rare per batch of 8, and tiny in pixel share.
- gridline: inter-annotation IoU is 0.24 to 0.36 (handbook benchmark_el_report), so gridline 0.28 is already near its label ceiling for strict IoU. The main mIoU lever is splice, then edge_dark and material.
- Already tested (BRIEF section 5 and `trackM/results_r2*.md`): soft Dice on 12 classes (R2, WORSE on crack through gradient clipping, gridline 0.283 -> 0.381 by recall, splice still 0.000); Dice on crack + inactive + gridline (R2c, n.d., gridline 0.283 -> 0.357 with precision 0.68 -> 0.57, splice 0.001); a val-chosen crack logit bias at inference (part of the best ensemble, crack only); per-module thresholds (fail).
- Never tested: training-time logit adjustment, per-class post-hoc bias for all classes, class-balanced or rare-class sampling, margin losses, logit variation, recall-weighted CE, pixel contrast, prototypes, region-level balancing, AUC losses.

## 2. Queries run (22 tool queries this session, plus about 14 in the 12 Nov WIP session)
search_papers (year_from 2020 unless noted):
1. long-tailed semantic segmentation
2. region rebalance semantic segmentation
3. logit adjustment semantic segmentation class prior
4. rare class sampling semantic segmentation
5. supervised pixel contrastive learning semantic segmentation
6. long-tailed semantic segmentation tail classes (2025+)
7. class imbalance segmentation overfitting under-represented classes medical
8. neural collapse imbalanced semantic segmentation classifier
9. hard pixel mining segmentation pixel hardness
10. episodic sampling rare class segmentation (2024+)
11. balanced softmax seesaw loss dense prediction segmentation
12. class-specific threshold post-hoc calibration semantic segmentation imbalanced
13. application of decision rules for handling class imbalance in semantic segmentation (2019+)
14. decoupled classifier re-training class-balanced fine-tuning segmentation head
15. long-tail learning via logit adjustment
16. rethinking semantic segmentation prototype view nonparametric (2021+)
17. class imbalance loss semantic segmentation small rare classes mIoU (2025+)
18. sigmoid multi-label segmentation head versus softmax rare overlapping classes
19. logit adjustment pixel-level segmentation imbalance (2025+)
20. repeat factor sampling rare category image oversampling segmentation (2019+)

Snowball: get_citations on BLV (arXiv 2306.02061, 30 citers); similar_papers on RR + CeCo + AUCSeg.
search_snippets: 2 attempts, both rate-limited (Semantic Scholar keyless pool). Evidence was taken from abstracts and one full text (Li et al. TMI, arXiv 2102.10365) instead.
WebSearch: 5 (recent long-tail seg with code; ProtoSeg / ContrastiveSeg repos; RR repo; DAFormer repo; CeCo repo), plus 2 on 12 Nov (BLV, AUCSeg repos).

## 3. Selected papers

| # | id | year | venue | code | mechanism | adaptation to our data | score | bench |
|---|---|---|---|---|---|---|---|---|
| 1 | arXiv:1901.08394 (Chan et al., decision rules) | 2019 | arXiv / ESREL 2020 | none found | Replace MAP argmax by a prior-corrected decision: divide posteriors by class priors (global or pixel-wise priors). R: pedestrian instance recall +25%, info signs +23.4%, non-detection -61% / -38%. | Post-hoc, zero training. Fit one bias per class (13 robust classes, plus splice) on out-of-fold logits from the existing module-grouped 5-fold roots, not on 54 val cells. Pixel-wise priors by position make sense for edge_dark / frame_edge / border (they live at cell edges) but not for crack. Apply to the 5-seed ensemble logits. | 72 | 45 |
| 2 | arXiv:2007.07314 (Menon et al., logit adjustment) | 2020 | ICLR 2021 | unverified | Add tau * log(prior_c) to the logits inside the CE during training (or subtract it at test). Fisher-consistent for balanced error. | Priors = train pixel frequencies of the 17 present classes, with padding and background kept. Apply only to the CE term; keep the crack + inactive Dice unchanged. tau grid {0.5, 1.0}. Expected effect: splice and edge_dark start being predicted; crack gets wider (risk, crack prior is 0.19%). | 66 | 70 |
| 3 | doi:10.1016/j.patcog.2026.114961 (arXiv 2607.22258, Generalised Balanced Softmax) | 2026 | Pattern Recognition | unverified | Same family as #2 but treats the coefficient beta as finite-data tunable. R: beta = 1 is not best on most benchmarks; tuned beta lowers a "model imbalance" metric and raises average recall. | Gives the grid for #2: with 478 cells and 1-2 px crack labels, beta below 1 is the likely optimum. Pick beta on fold OOF, not test. Run as the beta arm of #2, not as its own line. | 55 | 40 |
| 4 | doi:10.1109/tmi.2020.3046692 (arXiv 2102.10365, Li, Kamnitsas, Glocker) | 2020 | IEEE TMI | unverified | Under small data, test-time logits of the rare class shift toward the decision boundary while the majority class does not, giving under-segmentation. Fix: asymmetric losses that apply margin / focal only to the rare class. R (full text, KiTS tumor, 100% data, post-processed): DSC 79.2 -> 82.3, sensitivity 77.0 -> 81.4 with asymmetric large margin. | Directly matches "70% of E1 crack pixels get p(crack) < 0.001" and the crack / inactive / gridline recall shortfalls. Asymmetric large margin on crack, inactive, gridline, splice, edge_dark, material: subtract margin m from the true-class logit only for those classes. Before training, check the logit-shift claim on our data: compare crack-logit distributions on train vs val / E1 from existing checkpoints (no new training). | 70 | 55 |
| 5 | doi:10.1109/cvpr52688.2022.00969 (DAFormer, Rare Class Sampling) | 2022 | CVPR | github.com/lhoyer/DAFormer (web) | Sample a class c with probability proportional to exp((1 - f_c) / T), then an image containing c. Introduced for UDA source data; widely reused. | Cell-level class presence is cheap from our masks. f_c = fraction of train cells containing c (splice 53/478, inactive 42/478, edge_dark 41/478). T in {0.1, 0.01}. Keep the 20k-step budget fixed (see #6 for why). Also the natural sampler for E1-like half-cut views. | 63 | 70 |
| 6 | arXiv:2605.20405 (episodic class-balanced batches, CT) | 2026 | arXiv | github.com/iasonsky/episodic-sampling (from abstract) | Build each batch so that the classes appear in balance (episodic sampling from few-shot learning) in a fully supervised setup. R: 210 CT scans, 9 classes: full data Dice 0.882 vs 0.878 (equal); low data 0.787 vs 0.758, mostly from a 12x iteration difference; under matched budgets random sampling overfits about 3x earlier. | Our house run is fixed at 20k steps, so the iteration confound is controlled. Batch of 8: force at least 1 cell with inactive, 1 with splice / edge_dark / material, rest random. Also a benchmark lesson: report iteration budgets when comparing samplers. | 55 | 50 |
| 7 | doi:10.1109/icra46639.2022.9811702 (arXiv 2106.14917, Recall loss) | 2022 | ICRA | github.com/PotatoTian/recall-semseg (from abstract) | CE weighted per class by (1 - running recall), moving between plain CE and inverse-frequency CE. R: Synthia, +9% relative mean accuracy, mIoU competitive. | gridline recall 0.33 and splice recall 0 are what it targets. Compute recall per class with an EMA across batches (most batches lack splice). Expect the same recall-for-precision trade seen with Dice on gridline (R2c); pair with #1 post-hoc bias to restore precision. | 58 | 45 |
| 8 | doi:10.1109/cvpr52729.2023.01874 (arXiv 2306.02061, BLV) | 2023 | CVPR | github.com/grantword8/BLV (web, 12 Nov) | During training add Gaussian noise to logits with a per-class scale, larger for rare classes; removed at test. R: gains mainly on tail classes; fully supervised ViT-B + UperHead 77.7 mIoU, ahead of logit adjustment and Lovasz in their Table 5. | Noise scale from log inverse pixel frequency over our 17 present classes; crack would get a large sigma, so cap crack at the inactive value or exclude crack in a second arm (its labels are already jittered). One-line change on the U-Net++ head. | 60 | 65 |
| 9 | arXiv:2204.01969 (Region Rebalance) | 2022 | arXiv | not released (PaCo README says "soon", web) | Pool pixel features of each class in an image into one region feature; train an auxiliary balanced region classifier. Region counts are far less imbalanced than pixel counts. R: +0.7 mIoU on ADE20K for BEiT. | Our region-level imbalance is mild (splice 53 cells vs 478) while pixel-level is extreme, so the premise fits. Pool full-res U-Net++ decoder features per class per cell; auxiliary linear classifier with balanced CE; drop at test. About 50 lines. | 55 | 55 |
| 10 | doi:10.1109/cvpr52729.2023.01873 (arXiv 2301.01100, CeCo) | 2023 | CVPR | github.com/dvlab-research/Imbalanced-Learning (web; release status unclear) | Imbalance breaks the equiangular structure of class feature centers; a regularizer pulls centers toward a simplex ETF. R: gains on 2D and 3D seg; ScanNet200 test 1st place (+6.8 mIoU). | Same plumbing as #9 (class centers from decoder features). With 17 present classes and a 16-channel final decoder stage, add a projection of at least 32 dims. Could help crack vs inactive vs scuff separation for E1 (S). | 48 | 50 |
| 11 | doi:10.52202/079017-4029 (arXiv 2409.20398, AUCSeg) | 2024 | NeurIPS | github.com/boyuh/AUCSeg (web) | Pixel-level AUC loss (ranking of class scores) plus a tail-class memory bank so each batch sees tail pixels. R: tail-class gains on Cityscapes, ADE20K, COCO-Stuff. | Bold bet. AUC is threshold-free, which suits crack (we tune a crack bias anyway) and splice. Memory bank stores small crops of splice, inactive, edge_dark, material pixels from earlier batches. More engineering than #1 to #8. | 45 | 60 |
| 12 | doi:10.1007/s11263-025-02416-4 (arXiv 2305.08462, pixel hardness) | 2025 | IJCV | github.com/Menoly-xin/Hardness-Level-Learning (from abstract) | A gradient-isolated branch learns a stable hardness map by maximising hardness-weighted loss; the seg head minimises it. R: +1.37 mIoU on average over popular models on Cityscapes; aimed at small objects and thin parts. | Thin parts = gridline and crack. Risk: on 1-2 px jittered crack labels, "hard" pixels are often label noise; mask hardness weighting to within 2 px of the label, or use it only for non-crack classes. | 48 | 45 |
| 13 | arXiv:2104.04465 (ReCo) | 2021 | ICLR 2022 | github.com/lorenmt/reco (from abstract) | Pixel contrastive loss on a sparse set of hard negative pixels, small memory. R: consistent gains in supervised and semi-supervised seg, strongest with very few labels (5 per class). | Projection head on the full-res U-Net++ decoder stage (not 1/4, which would erase 1-2 px cracks). Class-balanced anchor sampling capped per class so crack and splice anchors are not swamped. Hard negatives for crack = scuff / gridline / busbar pixels. | 50 | 50 |
| 14 | doi:10.1109/iccv48922.2021.00721 (cross-image pixel contrast) | 2021 | ICCV | github.com/tfzhou/ContrastiveSeg (web) | Supervised pixel-to-pixel and pixel-to-region contrast across images with class memory banks. | A memory bank across the 5 sources would pull BMRK / CFVS / CSIR crack embeddings together: a source-invariance push for the weak sources. Same full-res caveat as #13. Run #13 or #14, not both. | 45 | 55 |
| 15 | doi:10.1109/cvpr52688.2022.00261 (ProtoSeg) | 2022 | CVPR (oral) | github.com/tfzhou/ProtoSeg (web) | Replace the parametric softmax head by several non-learnable prototypes per class (class centers from online clustering); pixels classified by nearest prototype. | Bold bet: several prototypes per class can hold the five sources' crack conventions and half-cut vs full-cell inactive looks as separate modes, which one linear weight cannot. 3 to 5 prototypes for crack, inactive, gridline; 1 for the rest. | 40 | 55 |
| 16 | doi:10.1109/cvpr46437.2021.00957 (arXiv 2008.10032, Seesaw loss) | 2021 | CVPR | unverified | Per class pair, scale down negative gradients that frequent classes put on rare classes (mitigation), and scale them back up when the rare class is wrongly predicted (compensation). | Pixel version: background, ribbons and busbar push splice down at every pixel; seesaw reduces this. Crack vs inactive (20% of crack pixels touch inactive) is a pair where compensation matters. | 45 | 50 |
| 17 | doi:10.1609/aaai.v39i8.32956 (inter / intra-class Balance loss) | 2025 | AAAI | unverified | Hard-example mining strength on majority pixels set by the frequency of minority classes present in each image; plus within-class hard mining. R: better than common losses on 5 medical tasks. | Per-cell control fits our data: cells without crack get light majority mining, cells with cracks heavy. Overlaps #4 and #12; keep as an alternative. | 40 | 35 |
| 18 | doi:10.1109/tmm.2024.3407679 (arXiv 2406.03917, Frequency-based Matcher, LTSS benchmark) | 2024 | IEEE TMM | unverified ("will be public") | Builds a long-tailed seg benchmark with a dual-metric evaluation, and a one-to-many query matcher for mask-classification decoders. | Mostly for the benchmark: head and tail reported separately fits our per-class tables. The matcher only applies if a Mask2Former-type decoder is adopted (D23). | 25 | 60 |
| 19 | doi:10.1007/978-3-032-31673-8_35 (arXiv 2607.21089, Savva et al.) | 2026 | LNCS | unverified | R: 11 imbalance methods vs plain CE on 3D point clouds: CE within 0.8 to 3.3 mIoU; specialised methods risk large drops when poorly tuned. | Benchmark guidance: the suite must include tuned plain CE (+Dice) as the control and report tuning budgets per method. Also a prior: expect small gains from loss-level fixes alone. | 15 | 50 |

Scores follow the team rubric (expected gain x probability x feasibility). bench = value for the benchmark suite or protocol.

## 4. Minimum experiments (cheapest first)
Common setup: house U-Net++ / R34 (SUP100 config); compare against SUP100 5-seed. Use module-grouped 5-fold OOF on the 532 train + val cells for choosing anything (biases, tau, T); report test clean 49 once. Primary: mIoU_rob. Guards: crack IoU, crack relF1@2 and inactive IoU must not drop beyond the BRIEF detection thresholds (about 0.01 for crack).

1. **Diagnostic D0 (0 GPU-h, do first).** From saved val / OOF logits of SUP100, compute per-class AP and where splice / edge_dark / gridline pixels rank. If splice AP > 0.2, a post-hoc bias (#1) can recover it; if splice AP is near 0, only training-time changes (#2, #5, #4) can. Also plot train vs val crack-logit histograms to check the Li et al. logit-shift claim (#4).
2. **#1 per-class post-hoc bias.** Arm: bias vector b (14 entries, grid -2 to +4 logit units) fitted per class by coordinate ascent on OOF mIoU_rob, applied to the 5-seed ensemble. Baseline: ensemble with crack bias only. Kill: test mIoU_rob gain < +0.01 or splice IoU still < 0.05.
3. **#2 / #3 logit-adjusted CE.** Arms: tau (beta) in {0.5, 1.0}, 3 seeds each, about 7 GPU-h. Baseline SUP100. Metric mIoU_rob plus splice / gridline / edge_dark IoU. Kill: mIoU_rob < +0.01 on folds, or crack IoU drop > 0.01 after re-tuning the crack bias.
4. **#5 / #6 rare-class sampling.** Arm: RCS with T = 0.01 over cell-level class presence, 20k steps fixed, 5 seeds. Baseline SUP100. Metric mIoU_rob and inactive IoU (inactive cells sampled about 3x more often). Kill: mIoU_rob < +0.01 and inactive n.d.
5. **#4 asymmetric large margin.** Arm: margin m in {0.5, 1.0} on the rare-class true logit (crack, inactive, gridline, splice, edge_dark, material), 3 seeds; E1 crack recall as a secondary. Baselines SUP100 and PF. Kill: test crack recall gain < 0.02 and E1 recall gain < 0.03.
6. **#8 BLV.** Arm: sigma from log inverse frequency, crack capped, 3 seeds. Kill as in 3.
7. **#7 recall loss.** Arm with EMA recall, then the #1 bias. Kill: gridline IoU not above R2c's 0.357, or mIoU_rob < +0.01.
8. **#9 / #10 / #13 / #15 feature-level arms** only if steps 3 to 7 give at least one positive arm, as add-ons on top of it. Kill: no gain over the best loss / sampling arm.

Total for steps 2 to 7: about 35 to 45 GPU-h, 1 to 2 days on cv02.

## 5. Notable papers rejected
- Remix (doi:10.1007/978-3-030-65414-6_9): classification mixup; the label-safe augmentation rule and thin labels make pixel mixup a poor fit.
- Equalized Focal Loss (doi:10.1109/cvpr52688.2022.00686), Equalization losses (doi:10.1109/tpami.2023.3298433): detection-specific sigmoid heads; Seesaw (#16) covers the gradient-balance idea for us.
- MEDOE multi-expert decoder (arXiv 2308.08213): extra cost; our seed ensemble already gives the ensemble gain.
- PAT (arXiv 2404.05393): class-wise gradient homogenisation; weak evidence (preprint) and overlaps #4 / #7.
- SegFace (doi:10.1609/aaai.v39i6.32661), GOOSE-M2F (arXiv 2606.15937), SRMF (doi:10.1109/tgrs.2025.3565600): domain-specific long-tail fixes (faces, terrain, satellite) with no transferable core beyond #2 / #5.
- Diffusion augmentation for tail classes (arXiv 2602.04749, arXiv 2607.08201): belongs to D33 generative data.
- Long-tail point cloud papers (doi:10.1109/icra57147.2024.10610029, doi:10.1109/cisat62382.2024.10695176): 3D-specific.
- Neural collapse theory papers (arXiv 2208.05512, arXiv 2309.09725): theory only; CeCo (#10) is the applied form.
- "Long-Tail Learning with Foundation Model: Heavy Fine-Tuning Hurts" (arXiv 2309.10019): classification; its point (light fine-tuning keeps tail performance) is already covered by our PF finding.
- Local temperature scaling (doi:10.1109/iccv48922.2021.00681): calibration, not decision; #1 covers the decision part.
- Balanced Meta-Softmax (arXiv 2007.10740): its balanced softmax is #2 with tau = 1; the meta-sampler adds cost without a dense-prediction result.

## 6. Gaps
- search_snippets was rate-limited all session, so paper numbers come from abstracts plus one full text (Li et al.). The RR, BLV and AUCSeg tail-class tables were not read in detail.
- No paper found that tests long-tail methods on thin-structure classes with jittered 1-2 px labels; how rebalancing interacts with label jitter (wider crack predictions) is untested anywhere I could find.
- No 2025 to 2026 CVPR / ICCV fully supervised long-tail semantic segmentation paper with code turned up in Research MCP or web search; recent work moved to foundation-model and UDA settings.
- Why splice is never predicted (rarity vs confusion with ribbons / busbars) is unknown; the D0 diagnostic answers it and decides between post-hoc and training-time fixes.
- Sub-direction worth its own search: multi-label (sigmoid) heads for overlapping crack / inactive, with per-class thresholds; one query found nothing directly usable.
- Code for Seesaw, Menon LA, GBS, the AAAI 2025 Balance loss and the Frequency-based Matcher not verified.
