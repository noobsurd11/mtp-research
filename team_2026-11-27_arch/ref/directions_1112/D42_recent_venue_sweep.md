# D42: Open sweep of 2025 and 2026 venues

Scout: D42 literature agent, 13 Nov 2026. Notes trail: `D42_notes_wip.md`.
Legend: (R) = what the paper measured, (E) = what our files measured (BRIEF), (S) = my judgement.

## Bottom line

- (S) The other 41 directions already cover most topic keywords (about 1,390 distinct ids across D01 to D44 files). I checked every candidate against that list and kept mainly papers that no other direction cites. Two kept papers sit next to covered work (FAST next to SARD, SegRCDB next to InsCore), and I say so in their rows.
- (S) The three most useful new finds:
  1. **DINOv3-IML** (arXiv 2604.16083, 2026, code). Frozen DINOv3 ViT-L, LoRA, and a 9.1 M-parameter conv decoder localise tiny manipulated regions. (R) On the data-scarce protocol it reached pixel F1 0.774 against 0.530 for the best earlier method, and LoRA beat full fine-tuning at every backbone scale. Full fine-tuning was unstable. (E) That matches our own finding that the house fine-tune wipes the encoder and PF keeps it. Large ViT with LoRA is listed as open in BRIEF section 5.
  2. **CSWinUNETR** (arXiv 2606.19824, MICCAI 2026, code). A 2D/3D backbone for thin structures using cross-shaped stripe attention and sparse-control snake convolution. (R) FIVES Dice 90.71 against 89.26 for nnU-Net v2. FFHQ-Wrinkle Dice 64.75 against 63.27, and wrinkles are thin, low-contrast, 1-to-few-px lines with 800 training images. No topology loss was used. No transformer segmenter has been tried on our data.
  3. **Learn2Synth** (arXiv 2411.16719, ICCV 2025, code). Hypergradients tune the parameters of a synthesis or augmentation engine so that a network trained on synthetic data scores best on a small real labelled set. (S) This is the missing piece for any EL crack or half-cut synthesizer: the knobs are learned on real validation cells instead of hand-tuned.
- (S) Bold bets: Learn2Synth on a parametric EL renderer, and formula-driven thin-curve pretraining (SegRCDB style).
- (S) For E1, two cheap UDA-style options use the 1,152 unlabelled multi half-cut pool cells as the target domain: DiDA (NeurIPS 2025) and ConformalSAM-style class-conditional calibrated pseudo-labels (ICCV 2025).
- (S) For the benchmark: DINOv3-IML and CSWinUNETR are recent, simple, public-code baselines a credible EL suite should include. KαLOS (CVPR 2026) gives a principled way to report annotator agreement as the label-noise ceiling.

## Queries run (about 50 tool calls)

Research MCP `search_papers` (limit 15 to 20, abstract_chars 250). Scopus and ScienceDirect returned 401 and Semantic Scholar was rate-limited all session, so hits came from OpenAlex and arXiv.
1. thin structure segmentation noisy annotations misaligned labels (2025+)
2. curvilinear structure segmentation foundation model fine-tuning (2025+)
3. tiny defect segmentation few labeled images synthetic data diffusion (2025+)
4. learning segmentation from imprecise boundary annotations label shift tolerant (2024+)
5. DINOv3 dense features segmentation small dataset fine-tuning (2025+)
6. feature upsampling high-resolution features foundation model thin structures (2025+); mostly covered by D22 / D24
7. diffusion model prior dense prediction segmentation few labels (2025+)
8. sub-pixel line segmentation centerline uncertainty annotation offset (2023+); noise
9. multi-source dataset heterogeneous annotation conventions (2025+); noise
10. segmentation small training set beats foundation models (2026)
11. crack segmentation label noise annotation width tolerance (2025+)
12. rare class segmentation copy-paste generative augmentation (2025+)
13. RankSEG consistent ranking-based segmentation (2022+); covered by D18
14. rotation equivariant convolution segmentation thin structures (2024+); noise
15. hard negative / confounder suppression / outlier exposure (2024+); noise
16. formula-driven supervised pretraining segmentation (2023+)
17. domain-specific normalization / mixture of experts multi-domain segmentation (2024+); noise
18. learnable non-uniform downsampling small objects (2023+)
19. large kernel CNN thin elongated structures (2023+)
20. procedurally generated synthetic curves pretraining thin structures (2021+)
21. training data attribution / mislabeled training images in segmentation (2023+)
22. spurious context / unseen layout segmentation (2024+); noise
23. synthetic-only / domain randomization thin crack fracture (2024+)
24 to 33. Title lookups: HarmonySeg, GLARE, Learn2Synth, CrackSSM, MatchMask, Structure-Aware Distillation, Dual-level Adapter, ConformalSAM, DiDA, SDD, KαLOS, Torch-Uncertainty

Other Research MCP calls: `similar_papers` on CSWinUNETR + FAST; `get_citations` on NSegment+ (2508.10383) and Learn2Synth; `get_paper` on 12 candidates; `fetch_fulltext` + `read_paper` on CSWinUNETR and ConformalSAM (2 of 3 allowed).

WebSearch (12 calls): CVPR 2026 thin / noisy labels; NeurIPS 2025 boundary label noise; ICCV 2025 thin structure + code; MICCAI 2025 vessel noisy annotation; ICLR 2026 small-data FM adaptation; arXiv 2026 crack label noise (extended); arXiv 2026 EL foundation model; ECCV 2026 thin / label noise (extended); CVPR 2026 defect synthesis; Dual-level Adapter (CVPR 2026); MatchMask (CVPR 2026); 2607.05965 details.
WebFetch (3 calls): papernotes accepted-paper lists for NeurIPS 2025 segmentation (45 entries), CVPR 2026 segmentation (125 entries, first 100k chars read) and ICCV 2025 segmentation (75 entries).

## Selected papers

Code is listed only when the paper's abstract (retrieved by tool) gives the URL. Score = value for our scores. Bench = value for the benchmark.

| # | id | year | venue | code | mechanism | adaptation to our data | score | bench |
|---|---|---|---|---|---|---|---|---|
| 1 | arxiv:2604.16083 (DINOv3-IML) | 2026 | arXiv | github.com/Irennnne/DINOv3-IML | Frozen DINOv3 ViT (S to L) + LoRA + light conv decoder for pixel localisation of tiny forged regions. (R) +17.0 pixel-F1 over the previous SOTA on 4 benchmarks; data-scarce protocol F1 0.774 v 0.530; LoRA > full FT at all scales; full FT unstable | 1-channel EL repeated to 3 channels, 512 px input (1024 px for a 2x token grid). Keep the conv decoder, add a shallow full-res stem skip so 1 to 2 px cracks are not lost at patch 16. 24-class CE + Dice on crack / inactive as house. DINOv3 weights are gated (user OK needed); fallback DINOv2-L or C-RADIOv4 | 62 | 72 |
| 2 | arxiv:2606.19824 (CSWinUNETR) | 2026 | MICCAI | github.com/labhai/CSWinUNETR | Cross-shaped stripe self-attention with cyclic shift (long-range context along principal axes), detail-enhanced multi-scale attention, sparse-control dynamic snake conv. (R) FIVES Dice 90.71 v nnUNetv2 89.26; FFHQ-Wrinkle 64.75 v 63.27; 31 M params; Dice + CE only | Use the 2D variant, 1-channel input, 512 px, house loss and schedule. Stripes fit busbar-aligned and diagonal cracks and long scuff streaks (E1). Trained from scratch: check whether 478 cells is enough (FIVES had 500, Wrinkle 800). Pair with PF-style care only if a pretrained encoder is swapped in | 55 | 62 |
| 3 | arxiv:2411.16719 (Learn2Synth) | 2025 | ICCV | github.com/HuXiaoling/Learn2Synth | Learn the parameters of a synthesis / augmentation engine by hypergradients, so a net trained on synthetic or augmented images scores best on a small real labelled set; real images are never trained on directly | Engine = parametric EL augmentations: crack contrast and width, blur matching the 4 px FWHM, scuff streak rendering, half-cut masking, per-source gamma. Outer objective = val crack soft-IoU on 54 val + F51 (and H36 for half-cut). Start parametric (about 10 params). Bold bet | 45 | 30 |
| 4 | arxiv:2509.20295 (FAST) | 2025 | NeurIPS | github.com/Chhro123/fast-foreground-aware-anomaly-synthesis | Foreground-aware diffusion for segmentation-oriented anomaly synthesis: noise inside the mask is adjusted at each step (FARM), and 10-step accelerated sampling (AIAS) gives image-mask pairs | Train on our 478 cells with inactive and crack masks as foreground. Synthesise inactive regions (only 42 train cells) on clean pool cells; masks are drawn from real inactive shapes, so they stay touching cracks (99% in real data). Grayscale 512 px. Same group as SARD (arXiv 2508.03143, covered elsewhere) | 48 | 35 |
| 5 | arxiv:2412.10339 (DiDA) | 2025 | NeurIPS | github.com/Woof6/DiDA | UDA by degradation-based intermediate domains (blur / noise at graded strength), with a diffusion-encoder term that compensates semantic shift; plug-in to existing self-training UDA | Source = 478 labelled cells; target = 1,152 unlabelled multi half-cut pool cells (E1-like, not E1). Degradations matched to EL: blur, gain, vignetting. Use with the existing Mean-Teacher code | 42 | 28 |
| 6 | arxiv:2507.15803 (ConformalSAM) | 2025 | ICCV | not in abstract | Calibrate a foundation-model teacher on the labelled set with class-conditional conformal prediction, keep only pixels inside the calibrated set, favour minority classes over background, then self-train. (R) VOC full split +1.7 mIoU over AllSpark; ADE 1/128 +10.0; gains shrink as labels grow | Teacher = our 5-seed PF ensemble or the DINOv3-IML model (SEEM has no EL concepts). Calibration set = val 54 + F51. Unlabelled = half-cut pool for E1. The class-conditional rule keeps crack pixels a plain confidence threshold drops | 38 | 30 |
| 7 | doi:10.1145/3832783.3837428 (SegFaultLoc) | 2026 | ASE | not stated | Training-free annotation fault localisation: split masks into connected components, score each with features from frozen pretrained encoders, using a semantic spectrum (class / missing faults) and a geometric spectrum (localisation / fragmentation faults), then rank by suspiciousness. (R) up to +22.4% nDCG@10% over 7 baselines; fixing the faults it found on COCO-Stuff raised segmentation scores | Run on train crack and inactive components across 5 sources. Use the ranking to (a) check the 24 of 239 cells the audit flagged, and (b) drop or down-weight the worst components automatically (no hand labelling) | 40 | 45 |
| 8 | arxiv:2607.05965 | 2026 | MICCAI | stated, URL unverified | Training-free single-mask noise detection: sample cross-sectional patches, retrieve intensity-matched neighbour patches by vector search, and score label noise from mask disagreement among neighbours. (R web) transverse / oblique vessels had 5.1x higher error rates | Patches orthogonal to crack skeletons; retrieve similar-profile patches from other cells and sources; flag cells where the label line sits off the dark ridge compared with peers. Gives a per-source offset estimate. Overlaps with D16 / D17 goals but uses a distinct, training-free mechanism | 35 | 40 |
| 9 | arxiv:2401.12736 (ShiftwiseConv) | 2025 | CVPR | github.com/lidc54/shift-wiseConv | Large-kernel effect from shifted small kernels across multiple paths; pure CNN; beats SLaK and UniRepLKNet in classification, segmentation and detection | ImageNet-pretrained SW backbone as the U-Net++ encoder (1-channel stem), PF fine-tune. Long sparse context may separate scuff streaks from cracks on E1 | 35 | 30 |
| 10 | arxiv:2309.17083 (SegRCDB) | 2023 | ICCV | github.com/dahlian00/SegRCDB | Formula-driven supervised segmentation pretraining: procedurally drawn radial contours with free masks; beat COCO-Stuff pretraining at equal image count on ADE20k and Cityscapes | Swap radial contours for EL-like primitives: thin dark polylines (1 to 4 px, with branching), dark blobs attached to lines (inactive), periodic gridlines and busbars on textured grey background. Pretrain the house encoder + decoder on 100k+ generated images, then house / PF fine-tune. Bold bet. InsCore (arXiv 2505.13099, same lab) is covered elsewhere | 30 | 20 |
| 11 | arxiv:2602.07590 | 2026 | arXiv | not stated | Parametric (discrete fracture network) synthesis of thin joint traces, then segmentation. (R) Mixed real + synthetic training works when real labels are consistent; pretrain-then-fine-tune is more robust when real labels are noisy or biased; zero-shot from synthetic alone is limited | Design rule for any EL crack synthesizer (D06 / D33): our crack labels are noisy and source-biased, so use synthetic data for pretraining and fine-tune on real, rather than mixing. Cheap to check as an arm | 30 | 15 |
| 12 | arxiv:2512.06870 (ECOCSeg) | 2025 | NeurIPS | github.com/Woof6/ECOCSeg | Replace one-hot classes with error-correcting output codes: per-pixel attribute bits plus bit-level label denoising; more robust to wrong pseudo-labels | 24 classes as codewords that share bits for related classes (crack and inactive share a "defect" bit, busbar / ribbon / splice share "metallisation"). Two side effects: a multi-label-like head (never tried) and a softer penalty for crack-versus-inactive confusion | 28 | 15 |
| 13 | arxiv:2510.17299 (SDD / DSE) | 2025 | NeurIPS | github.com/EldercatSAM/SSL-Degradation | Longer SSL training can hurt dense tasks (16 methods). A label-free Dense representation Structure Estimator selects checkpoints. (R) +3.0 mIoU on average from DSE-based selection | Only if the team runs pool SSL on a new backbone (D32): score checkpoints with DSE on pool cells instead of training to the end. A possible reason our MIM / DDeP runs gave n.d. | 25 | 15 |
| 14 | arxiv:2603.27197 (KαLOS) | 2026 | CVPR | not in abstract | Meta-algorithm for inter-annotator agreement in vision tasks with instance correspondence; validates agreement metrics without circularity; argues benchmark progress is limited by label noise | Benchmark only: report crack annotator agreement on the doubly annotated cells (IoU 0.21 to 0.26, 0.82 to 0.99 within 2 px) as a KαLOS-style agreement number, so model gaps are judged against label noise | 8 | 55 |

## Minimum experiments

Default instrument: test clean 49 + E1, 5 seeds against the stated baseline, the BRIEF seed rule, and the existing module-grouped 5-fold roots where noted. A 5 v 5 crack IoU change under 0.012 counts as n.d.

1. **DINOv3-IML recipe** (row 1). Arm: frozen DINOv3 ViT-L/16 + LoRA (rank 16) + conv decoder with a stride-2 CNN stem skip, 1024 px input, 20k steps. Baseline: house PF 5-seed. Metrics: test crack relF1@2, crack IoU, inactive IoU, E1 crack relF1@2, E1 inactive IoU. Kill: E1 crack relF1@2 below PF + 0.02 and test crack relF1@2 below PF after 2 seeds. Cost: about 4 GPU-h per seed at 1024 px. Total about 20 GPU-h.
2. **CSWinUNETR** (row 2). Arm: 2D CSWinUNETR from scratch, house loss, 20k and 40k steps. Baseline: house model. Metrics: crack IoU, relF1@2, mIoU_rob, gridline IoU. Kill: 2-seed mean crack IoU more than 0.02 below house, or mIoU_rob more than 0.02 below. About 2 GPU-h per seed, 15 GPU-h total.
3. **Learn2Synth on EL augmentation** (row 3). Arm: an augmentation engine with about 10 continuous params (crack-region contrast scaling, Gaussian blur, scuff-streak overlay intensity and angle, half-cut mask, per-source gamma), learned by hypergradient against val + F51 crack soft-IoU, then fixed for a full house run. Baseline: house with label-safe augmentation. Metrics: E1 crack relF1@2 (main), test crack IoU. Kill: E1 relF1@2 below house + 0.02 with test crack IoU down by more than 0.012. About 30 GPU-h including the bilevel search.
4. **FAST inactive synthesis** (row 4). Arm: train FAST on the 478 cells; generate 2,000 pool cells with synthetic inactive regions (real inactive mask shapes plus their crack) and add them at 25% of each batch. Baseline: PF 5-seed. Metrics: test inactive IoU, BMRK inactive IoU, E1 inactive IoU, and module-grouped 5-fold CV inactive IoU (test inactive depends on 3 cells). Kill: CV inactive IoU gain under 0.02. About 40 GPU-h (diffusion training dominates).
5. **DiDA for E1** (row 5). Arm: Mean Teacher + DiDA degradations, target = 1,152 half-cut pool cells. Baseline: PF and the existing MT-with-pool run. Metrics: E1 crack relF1@2, E1 inactive IoU; test must not drop. Kill: E1 relF1@2 gain under 0.02 over PF. About 10 GPU-h.
6. **CP-calibrated pseudo-labels** (row 6). Arm: teacher = PF ensemble; per-class (crack, inactive, background) conformal quantiles fitted on val + F51; pseudo-label the half-cut pool, then train the student on labelled + pseudo-labelled cells. Baseline: the existing hard and tolerant pseudo-label runs at 100% with the pool. Metric: E1 crack recall and relF1@2. Kill: no E1 relF1@2 gain over the old pseudo-label run. About 8 GPU-h.
7. **Label fault ranking** (rows 7, 8). Arm: rank train crack components by SegFaultLoc suspiciousness (DINOv3-S or DINOv2 features); drop the top 5% of components (set to ignore) and retrain. Baseline: house. Metrics: test crack IoU and relF1@2, plus overlap with the 24 audited cells (precision at 24). Kill: precision at 24 below 0.3 or crack IoU change under 0.012. Under 1 GPU-h for the ranking, 6 GPU-h for training.
8. **ShiftwiseConv encoder** (row 9). Arm: SW-pretrained encoder in U-Net++, PF. Baseline: PF ResNet-34. Kill: E1 relF1@2 and test crack IoU both within noise after 3 seeds. About 5 GPU-h.
9. **Formula-driven thin-curve pretraining** (rows 10, 11). Arm: 100k procedural EL-like images, pretrain the house net 20k steps, then PF fine-tune. Baseline: ImageNet house PF. Kill: test crack IoU and E1 relF1@2 both n.d. after 3 seeds. About 8 GPU-h.
10. **ECOC head** (row 12). Arm: house net with a 24-class ECOC codebook head (32 bits). Baseline: house. Kill: crack and inactive IoU both n.d. 6 GPU-h.
11. **DSE checkpoint selection** (row 13): only alongside a D32 pool SSL run. Kill: DSE choice no better than the last checkpoint on val.

## Notable papers rejected

- arxiv:2504.01527 Beyond nearest-neighbour interpolation in augmentation (2026): our augmentation is flips and rot90 only, which need no interpolation. It matters only if scale or rotation augmentation is added.
- arxiv:2511.10282 Torch-Uncertainty (NeurIPS 2025): tooling for calibration metrics; useful for benchmark reporting but adds no method.
- arxiv:2603.13507 MIRAGE, arxiv:2604.08301 GroundingAnomaly: already covered by D33 / D39.
- CVPR 2026 "Dual-level Adapter Boosting Prompt-free Curvilinear Structure Segmentation" (SACM, oral; trained on 18 images, evaluated on 12 curvilinear sets): relevant, but I found no arXiv id or DOI through the tools, only the CVF page. Same group as UCS (arXiv 2504.04034, covered by D14). Worth a later lookup.
- CVPR 2026 MatchMask (mask-centric generative augmentation for label-scarce segmentation): no arXiv id found and code unverified. D33 covers the same idea.
- CVPR 2026 CrackSSM, MixerCSeg (crack Mamba / mixer): seen only in the papernotes listing, with no id from the tools. They belong in the benchmark suite if D09 has not listed them.
- arxiv:2510.15362 RankSEG-RMA, arxiv:2508.10383 NSegment+, arxiv:2504.04034 UCS, arxiv:2607.07123 WPRF, arxiv:2606.24935 SEMIR, doi:10.1109/iccv51701.2025.02188 HarmonySeg, arxiv:2509.17816 GLARE, arxiv:2505.13099 InsCore: good, but already covered by D18 / D15 / D14 / D10 / D11 / D09 / D32 / D33.
- arxiv:2409.11355 Fine-tuning image-conditional diffusion is easier than you think (WACV 2025): depth-focused; generative segmentation is covered by D23 / D33 (arxiv:2604.24575).
- arxiv:2512.17263 AnyCXR conditional joint annotation regularisation: the source-conditional idea is interesting but the mechanism is X-ray specific and closer to D17.

## Gaps

- Semantic Scholar was rate-limited all session, so `search_snippets` failed. Evidence numbers come from abstracts, two full texts (CSWinUNETR, ConformalSAM) and web summaries.
- The CVPR 2026 segmentation list was read only up to 100k of 111k characters. The ECCV 2026 and MICCAI 2026 accepted lists were not scanned directly (no papernotes page found). A dedicated pass over the MICCAI 2026 and ECCV 2026 proceedings would probably find more thin-structure papers.
- Not verified: code URLs for 2607.05965, SegFaultLoc, ConformalSAM and KαLOS. SACM, MatchMask, CrackSSM and MixerCSeg have no arXiv ids.
- A sub-direction that deserves its own search: **learned augmentation / synthesis parameter search against a real validation metric** (Learn2Synth, bilevel augmentation search). It links D06 / D21 / D33 to E1 and is not covered elsewhere.
- Another: **LoRA on large ViTs for tiny-region localisation outside medicine** (forensics, change detection). DINOv3-IML suggests these fields have recipes that transfer to 1 to 2 px targets better than medical PEFT work does.
