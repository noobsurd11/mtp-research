# T7 family cards: unseen-module gap (domain generalisation, adaptation, layout and appearance)

Analyst T7, 13 Nov 2026. Tags: R = from the paper, E = from our files, S = my judgement. No server, no GPU, no test or E1 read.
Ledger for all 67 papers: `cards/ledger/T7.tsv`. Arms: `cards/T7_unseen_modules_spec.md`.
Full text read (Research MCP, arXiv copies): P012 (GIN-IPA), P034 (MIC), P057 (SLAug). Abstract re-read: P231, P597, P373. GIN code read on GitHub (`models/imagefilter.py`). Others: scout record only.

## 0. What our files already say about the E1 gap (E), and what it means for this family (S)
These facts decide which papers matter more than any paper's own numbers.
1. **Where E1's crack loss lives** (handbook 20 2.1, PROTOCOL 3.3): 75% of E1 crack px are in 29 half-cut + scuff cells (recall 0.126); half-cuts without scuff already score recall 0.552; plain full cells hold 5% of E1 crack px.
2. **Photometry is mostly inside the training envelope** (idea 11, judge-reproduced): E1 content mean / sd reachable by the house jitter for 96 to 100% of cells; sharpness and noise inside the train range for 90 to 100%. The one photometric gap is histogram shape: 60% of E1 half-cuts lie above the train p97.5 (0.84 vs 0.83); pool and Hanifi half-cells show it milder (12 to 13% outside). The "E1 is brighter" statistic is the white letterbox of 55 of 58 E1 half-cuts, which exists in no other set.
3. **Geometry was tested** (HC, handbook 21 2): synthetic half-cut views (gap + 1.34 x 1.2-1.3 rescale + pool-matched linear intensity, p 0.35) moved the synthetic half-cut instrument SHV1 by +0.123 matched relR@2 and E1 crack relF1@2 by only +0.0135 (n.d.). **This is the measured case of a development instrument that moved while E1 did not.**
4. **Inference-time intensity mapping hurts** (idea 2): per-cell / per-module affine and histogram matching lower val relF1@2 by 0.02 to 0.06; the models use absolute grey level. Training-time shape invariance is untested.
5. **The E1 crack failure is ranking, not threshold** (routing pre-check FAIL, handbook 20 3.1): within strata, no bias recovers it.
6. **BN-statistics TTA failed** (T9, BN-HC): no ranking gain, more false alarms. Entropy TTA was never run.
7. **Pool SSL at 100% (P16 Sx100)**: Mean Teacher, tolerant PL, separate BN, no CutMix, lambda 1, uniform over the 11.9k pool, house recipe: n.d. on test and on every E1 metric; the unlabelled loss was 2 to 7% of the supervised loss at 20k steps.
8. **PF is the only E1 mover so far** (E1 inactive 0.05 -> 0.24, BRIEF 3), with B6 showing no in-distribution gain of that size. Keeping pretrained features moved E1; nothing that changed the data moved it.

Reading (S): methods that add invariance to appearance or that keep / adapt features are the plausible movers; methods that re-create half-cut geometry have been tested in their simplest form; pure calibration and BN-statistics routes are closed by evidence. The scuff + half-cut stratum has no non-E1 labelled analogue, so no development instrument can measure it.

---

## P012 GIN + IPA: Causality-inspired single-source domain generalisation (Ouyang et al.)
- **Ids:** arXiv 2111.12525; doi 10.1109/tmi.2022.3224067 (IEEE TMI 2022). Read: arXiv full text (sections III, IV, ablations).
- **Code:** https://github.com/cheng-01037/Causality-Medical-Image-Domain-Generalization. PyTorch (pins torch 1.3.0, smp 0.1.3). Verified on GitHub: `models/imagefilter.py` `GINGroupConv` defaults `interm_channel=2`, `scale_pool=[1, 3]` (kernel size drawn per layer), `n_layer=4`, `out_norm='frob'`; output `alpha * net(x) + (1 - alpha) * x`, then rescaled to the input's Frobenius norm. Licence: a LICENSE file exists, its type not read (unverified). LeakyReLU slope not read (unverified).
- **What it does (R):** GIN = a shallow random conv net (weights N(0, I), re-drawn every iteration, LeakyReLU between layers, no downsampling) re-maps intensity and texture; IPA = two GIN views blended by a low-frequency random map b (cubic B-spline interpolation of random control points, spacing 1/4 of the image side), giving each region its own appearance; training loss = segmentation loss (CE + soft Dice) on the views + lambda_div 10 x KL between the predictions of the two views.
- **Numbers (R, Dice, Table II, U-Net EfficientNet-b2, 192 px, standard geometric + intensity augmentation for all methods):** abdominal CT -> MRI ERM 77.31, RandConv 80.66, GIN-IPA 86.31; cardiac bSSFP -> LGE ERM 75.99, RandConv 83.73, GIN-IPA 85.01; cross-centre prostate ERM 56.59, RandConv 57.74, GIN-IPA 70.37. Ablation (Table IV): IPA over GIN-only +0.27 (abdominal), +1.18 (cardiac), +5.27 (prostate, the shift most like a same-modality site change). GIN layers 2 / 4 / 8 / 16 = 84.26 / 86.04 / 85.66 / 79.17; hidden channels 2 best.
- **Evidence check (S):** all three settings are cross-modality or cross-centre MRI / CT with large appearance shift and 13 to 45 training volumes. Our E1 shift is same camera family, same source (CSIR), and photometrically inside the train range except histogram shape (section 0 item 2). The cross-centre prostate row (+13.8 Dice, IPA +5.3) is the closest analogue and is the one where IPA mattered. Expect a much smaller effect here.
- **Hypothesis for our data (S):** two parts. (a) GIN's nonlinear piecewise-linear maps change histogram shape, the one photometric E1 gap the house augmentation cannot reach (gamma covers 5 to 11%, idea 11). (b) IPA gives neighbouring regions independent appearance, so a dark streak (scuff) next to a crack, or a dark inactive region next to a crack (99% of inactive touches a crack), stops being a stable cue. That is the "confounder in the background" mechanism of the paper's section III-C, and it is the only family member that speaks to the scuff + half-cut stratum at all.
- **Adaptations (S):** 1-channel; applied on GPU to the normalised batch; sign correction (if a draw inverts contrast, flip the net output), because "dark = less emission" holds for every EL camera and an inverted cell simulates no real domain; crack CNR pre-check before any GPU run; KL on non-ignore px only.
- **Status:** RUN_NOW, arm `gin_ipa`.

## P057 SLAug: saliency-balancing location-scale augmentation (Su et al.)
- **Ids:** arXiv 2211.14805; doi 10.1609/aaai.v37i2.25332 (AAAI 2023). Read: arXiv full text (method, results, ablation).
- **Code:** https://github.com/Kaiseem/SLAug (scout; not opened, licence unverified).
- **What it does (R):** GLA = global monotone cubic Bezier intensity curve (control points random inside [v_low, v_high]) plus location-scale alpha ~ TN(1, 0.1), beta ~ TN(0, 0.5); LLA = the same per labelled class region (with random inversion p 0.5); SBF fuses GLA and LLA images with a smoothed gradient-saliency map.
- **Numbers (R, Table 1, 2):** abdominal CT -> MRI 88.63 vs CSDG (GIN-IPA) 86.31; cardiac bSSFP -> LGE 86.69 vs 85.01; reverse directions 83.05 vs 80.40 and 87.67 vs 86.99. Ablation: GLA only 80.28 / 74.21 (abdominal / cardiac), LLA only 75.43 / 85.12, all three 88.63 / 86.69.
- **Evidence check (S):** the gain over GIN-IPA needs LLA, which transforms each labelled class region separately. On 1 to 2 px crack labels that sit off the dark ridge half the time (BRIEF 2), a class-wise transform paints the label, not the crack: a shortcut. GLA alone is the safe part, and GLA alone was weaker than GIN-IPA in the paper (80.28 vs 86.31 abdominal).
- **Status:** RUN_AFTER_GATE as the fallback inside `gin_ipa`: if GIN fails the crack-contrast pre-check even with pointwise kernels, GLA (monotone, pointwise, cannot blur a crack) replaces GIN.

## P034 MIC: masked image consistency for context-enhanced UDA (Hoyer et al.)
- **Ids:** arXiv 2212.01322; doi 10.1109/cvpr52729.2023.01128 (CVPR 2023). Read: arXiv full text (method, implementation, analysis, supplement C, D).
- **Code:** https://github.com/lhoyer/MIC (segmentation code in `seg/`, built on DAFormer / HRDA, mmsegmentation-based per the papers; licence not stated on the repo page, unverified). We do not use it: the mechanism is re-implemented on the house Mean Teacher path.
- **What it does (R):** EMA teacher (alpha 0.999) predicts pseudo-labels on the full target image; the student sees the target with random patches masked (patch b = 64, ratio r = 0.7) and must match them; loss weighted by a quality estimate q = share of pixels with max softmax above tau = 0.968; lambda_M = 1; added to a host UDA method (DAFormer / HRDA self-training with DACS mixing, rare-class sampling, ImageNet feature distance).
- **Numbers (R):** GTA -> CS HRDA 73.8 -> 75.9 (+2.1), DAFormer 68.3 -> 70.6 (+2.3); ablation on DAFormer: without masking 50.6 (-20.0), without colour augmentation 70.3, without EMA teacher 69.9, without quality weight 69.0; patch / ratio best at 64 / 0.7, poor at 256; lambda_M 1 best, 10 below baseline; loss on masked patches only 69.8, unmasked only 69.7, all 70.6; MIC on source only hurts GTA -> CS (-2.7) when the context gap is large; 20% pseudo-label noise costs -4 mIoU only; MIC used in supervised training adds +0.3 only.
- **Evidence check (S):** gains are on street scenes with 19 classes and rich context; the largest come on low-baseline classes. Our target pixels are 99%+ background and cracks are thin and context-poor, so the masked-region part ("infer the class from context") cannot work for crack and could teach crack hallucination. The paper's own table shows the unmasked-region loss keeps almost all of the gain (69.7 vs 70.6), which is the variant to use. What can transfer: adaptation of the encoder to the real half-cell appearance (9 busbars, smooth texture, scuffs, cut gaps), which the synthetic HC views lacked.
- **What differs from the BRIEF 5 Sx100 null (E/S):** Sx100 used the whole 11.9k pool uniformly (77% full cells of the training sources), the house recipe (not PF), tolerant PL and separate BN, no masking. This arm uses only the 1,008 pool half-cells (target-like), PF, masked consistency, a confidence threshold and a crack-safe rule. The R4 lesson (training on half-cuts whose labels say "almost no crack" lowered half-cut crack) is the main risk and is gated.
- **Status:** RUN_AFTER_GATE, arm `mic_halfcell` (gate G-MIC: teacher census on pool half-cells).

## P394 HRDA: context-aware high-resolution UDA (Hoyer et al.)
- **Ids:** arXiv 2204.13132 (ECCV 2022). Scout record: GTA -> CS 73.8 mIoU (+5.5 over the previous best) (R, not re-read).
- **Code:** https://github.com/lhoyer/HRDA (scout; not opened).
- **Status:** RUN_AFTER_GATE behind a `mic_halfcell` screen pass. The 2x input run (BRIEF 5) was n.d., so only detail / context fusion inside UDA would be new.

## P231 PIE: parameter-frozen test-time ensembling (Huang)
- **Ids:** arXiv 2609.21412 (2026 preprint). Read: abstract.
- **Code:** none found.
- **Numbers (R, abstract):** M&Ms cardiac MRI vendor stream: PIE 0.7786 mean Dice vs source-only 0.7680 vs five online CTTA baselines 0.7388 to 0.7416; saturates at 28 views; confidence weighting, class-prior correction, CC filtering, morphology give no effect or harm.
- **Evidence check (E/S):** D4 flip / rot TTA was already run here (handbook 18 R1): +0.0104 crack IoU single model (on the 0.01 floor), 0 on the 5-seed ensemble. The new element is scale views. The physical case for scale: half-cells appear at 1.34x the train cell pitch (342 vs 256 px) and E1 crack labels are ~1.5x wider (3.66 vs 2.41 px per skeleton px) (E, idea 5 1.2, handbook 20 2.1). But HC already trained a model to be scale-invariant on synthetic half-cuts and E1 moved +0.0135 n.d.; the scale component is therefore bounded small for E1 (S).
- **Status:** RUN_NOW, arm `msc_tta` (inference only; mainly a benchmark TTA row and a cheap check).

## P597 MedSeg-TTA (Yu et al.)
- **Ids:** arXiv 2512.02497 (2025). Read: abstract. Code: https://github.com/wenjing-gg/MedSeg-TTA (stated in the abstract; not opened).
- **Claims (R):** 20 TTA methods, 7 modalities, one preprocessing and backbone; no paradigm best everywhere; input-level methods most stable under mild appearance shift; several methods degrade under large inter-centre / inter-device shifts.
- **Status:** PROTOCOL: template for the benchmark's TTA track (no-TTA primary always printed; TTA rows separate with view count and cost; degradations reported).

## P612 TTAP: TTA in semantic segmentation (2023)
- arXiv 2310.05341. Abstract (scout, R): BN updating slight gain or harm; teacher-student no gain on complex shifts; long-tail imbalance breaks seg TTA even with accurate pseudo-labels. Consistent with T9 / BN-HC (E). **PROTOCOL** (TTA reported separately; class-balanced selection rule in any self-training TTA).

## P373 SGP-TTA (Jang et al.)
- arXiv 2610.11104 (2026). Read: abstract. Code: project page only (no repo verified).
- Claims (R, abstract and scout full-text notes): progressive BN + consensus skeleton recall from multi-view predictions, BN affine only; scout reports DRIVE -> STARE Dice source 51.3, Tent 71.0, SGP 74.2, and Tent / CoTTA / SAR / EATA falling from 85.56 to 62-63 where the source model was already good (scout's reading of the full text, not re-checked).
- Our data (S): ProgBN is the part that failed here (T9). CSR needs partial detection; 70% of E1 crack px have p < 0.001. **BENCH_ONLY** (thin-structure TTA row, CSR on BN affine, reset per module).

## BENCH_ONLY rows for the unseen-module and TTA tracks (scout records; S on use)
| pid | Method | Role in the benchmark | Note |
|---|---|---|---|
| P369 | RandConv (arXiv 2007.13003 / CVPR 2023 progressive) | classic DG augmentation row | GIN-IPA paper: prostate 57.74 vs 70.37 (R). 1 h on top of the gin_ipa module: n_layer 1, no IPA, no KL |
| P121 | FDA (arXiv 2004.05498) | training-time UDA row: low-frequency amplitude from pool half-cells, beta 0.01 | HC already matched pool intensity linearly with no E1 gain (E), so low prior for scores |
| P619 | Tent | entropy TTA row (BN affine, one module per episode) | BAPA (P560) predicts collapse toward background for rare binary classes; report the collapse |
| P594 | SAR | stable entropy TTA row (batch 1, reliability mask, reset) | |
| P573 | CoTTA | continual TTA row | repo segmentation part reported non-commercial by the scout (unverified) |
| P593 | VPTTA | Fourier-prompt TTA row | its signal (BN-statistics alignment) failed here (T9) |
| P373 | SGP-TTA | thin-structure TTA row | above |
| P480 | DRAEM | no-defect-label anomaly baseline | |
| P536 | CutPaste | second anomaly baseline | |
| P362 | SuperSimpleNet | unified-supervision defect baseline | |
| P608 | Simple Copy-Paste | plain copy-paste row with the decoy count | CP100 (residual paste onto unlabelled pool cells) is a different recipe |

## PROTOCOL papers (besides P597, P612)
- **P615** (doi 10.3390/s24051479): per-cell damaged-area fraction drives module power loss and the worst cell dominates (R, scout). For the post-evaluation track: module severity = max over cells, not the mean.
- **P141** (arXiv 2605.20405): sampler gains are often a training-iteration confound (R, scout: full data 0.882 vs 0.878 Dice). Rule for `rcs` in wave 2: matched iteration budgets, stated.

## Parked papers that the lead should route elsewhere (S)
- **P124 Soft-CP** (inactive copy-paste, +10.2% DSC with all data on KiTS19 per abstract, scout): inactive copy-paste has never run here (CP100 was crack only). Problem 2, not mine; worth an arm in the inactive family.
- **P108 pv-vision isolated area** (code public): a circuit prior for inactive; problem 2 / post-evaluation.
- **P023** asymmetric margin: its premise (rare-class logits shift toward the boundary on unseen data) is checkable for free on W1 OOF dumps; loss family.
- Synthesis papers (P024, P105, P158, P181, P257, P387, P390, P426, P512): generative family T8.
