# R2: method side. What the SOTA SSL methods assume, and why those assumptions break on EL (24 Oct 2026)

Author: R2 (method/literature). Status: v1, before discussion rounds (section 9 records changes).

**Conventions**
- Tags: **[E]** evidence (a measured number, ours or a paper's table), **[R]** reading (interpretation), **[S]** speculation.
- Our facts cite `file` (relative to `~/mtp/research/`) and the number. Papers cite the Research MCP id; "read" says which part I read in full text this session.
- Scope (C's challenge 1): "fails here" is claimed only for what we ran: Mean Teacher/FixMatch-style (P8-P18, BsM5, CsM5), CPS (AL1 CPS5/CPSm5), ALHVR-EL (AL1), SKCDF DF (P17) and ABSH (SK1), UCF-EL transfer (P15). For untried methods (UniMatch feature dropout, class-adaptive thresholds, foundation teachers, copy-paste, MIM) I give only a prediction, tagged [S] or [R].

## 0. Bottom line (verdict, separate from the reading below)
1. **The SOTA methods we ran are tuned to a regime we are not in.** Their published gains come from (a) weak or from-scratch baselines, often with tail classes at 0 Dice, or (b) blob-like classes that a confident teacher gets mostly right. Our base is an ImageNet-pretrained, CE+Dice U-Net++ whose crack scores are bimodal. 57% of test GT crack scores < 0.001, 35% scores ≥ 0.95, and only 8.4% lies between them, where a threshold, a routing rule or a rebalancing can act (`results/al1/hist_revised.npz`, §1). **[E]+[R]**
   - Joint reading with R1 and C: this is the same mechanism as R1's coverage cause, seen from the method side. The teacher is confidently wrong exactly on the sources the labelled set does not cover (BsM5 − A5 crack IoU BMRK +0.002 at 5%). When a labelled draw covers BMRK, SSL reaches it: BsM20 − L3_20 BMRK +0.066, P18 exploratory, C's recompute. **[R]**
2. **Public thin-crack SSL results are mixed, single-run, and give no strong prior either way** (revised after C round 1). SemiCurv (doi:10.1109/tip.2022.3189823, Table III, read) at 5% labels:
   - Gaps384 (23 labelled / 442 unlabelled, almost our 23/455): MT 34.3, CutMix 33.5, VAT 29.6, cGAN 33.7 vs U-Net 34.9, but TCSM 37.8 and SemiCurv 38.0. The 5% → 100% headroom is only +4.1 (34.9 → 39.0), so this is partly a ceiling.
   - CrackForest (2.5% foreground): generic SSL +6 to +7 IoU (MT 66.9, CutMix 66.0, cGAN 67.0 vs U-Net 60.1). **[E]**
   - Reading: generic SSL can help thin cracks when the supervised base is weak and has headroom; it gives no evidence of large gains on a strong base near its ceiling. **[R]**
3. **SSL does move crack, a little.** BsM5 cuts test crack bin-0 from 0.569 to 0.449 and lifts crack AP from 0.287 to 0.367 (`team_2026-10-21/alhvr/results.md` §1). Its argmax IoU gain is the size of a free logit bias, but with the bias on both sides it still passes (+0.037, `results/sk1/la_sa.md` §2). So the honest method-side claim is "confidence-gated SSL helps crack ranking modestly and does not reach the true misses", not "cannot help crack". **[E]** (changed after C's challenge 3)
4. **Most of the crack deficit is not addressable by any unlabelled-loss mechanism we know of.** About 38% of pool crack is a true miss more than 2 px from any prediction. Removing every confident-background pseudo-label recovers about 12% of it (`team_2026-10-21/skcdf/second_opinion_a2.md`, probe result: 0.378 → 0.332). **[E]** Reading: the lever is which cracks the labelled set shows, not how pseudo-labels are chosen. **[R]**
5. **Ranked direction (§8):** stop SSL method development for crack; spend effort on the labelled set (retrospective budget test) and keep BsM5 (+LA) as the inactive and ranking result. Cheap inference-only probes come before any new SSL training.

## 1. Mechanism: confidence thresholding and confirmation bias for rare classes

**What the methods assume**
- FixMatch-style self-training (our BsM5, τ = 0.95) assumes the confident set is mostly correct and that under-confident correct pixels are the main waste. Adaptive and class-wise thresholds (FlexMatch arxiv:2110.08263; DARS doi:10.1109/iccv48922.2021.00685) assume the problem is too *few* tail pseudo-labels at a fixed cutoff.
- DARS shows the tail bias on Cityscapes 1/8 (372 labels, DeepLabv3+): single-threshold self-training lifts tail mIoU 47.2 → 54.0, DARS to 57.9 (Table 4, read). Over-confidence makes many pixels tie at confidence 1, so a threshold cannot set class proportions ("confidence overlapping", §1, read). **[E]**
- CSL (doi:10.1109/iccv51701.2025.02031, abstract): correct and wrong predictions overlap heavily at high confidence, so fixed thresholds amplify the model's bias. **[E]**
- CW-BASS v2 (arxiv:2608.12773, §VI, read): with a strong (DINOv2) teacher, 98% of Pascal pixels sit at ≥ 0.95. Adaptive and per-class thresholds then flood the mask (retention → 1.0, 99.9% of teacher errors admitted vs 63% for strict 0.95) and decline after an early peak. Strict 0.95 beats every adaptive rule on average (86.19 vs 79.36-84.35, 3 seeds, Table IX). **[E]**

**What we measured**
- **Class-conditional, on test (main evidence; C's computation, re-derived by R2 from `results/al1/hist_revised.npz`, H[crack, 0] = GT-crack px, seed means, D7 pool arms):**

  | Arm | p(crack) < 0.001 | [0.001, 0.1) | [0.1, 0.5) | [0.5, 0.95) | ≥ 0.95 | GT-crack px in [0.001, 0.95) | GT-negative px in [0.001, 0.95) |
  |---|---|---|---|---|---|---|---|
  | A5 | 0.569 | 0.042 | 0.018 | 0.024 | 0.347 | 7,750 (8.4%) | 13,395 |
  | BsM5 | 0.449 | 0.098 | 0.044 | 0.049 | 0.360 | 17,583 (19.1%) | 44,793 |
  | CPS5 | 0.547 | 0.057 | 0.024 | 0.030 | 0.342 | 10,242 (11.1%) | 17,816 |
  | AL5 | 0.596 | 0.043 | 0.019 | 0.025 | 0.317 | 7,971 (8.7%) | 15,423 |

  **[E]** Crack scores are bimodal: only 8.4% of GT crack lies in the band any threshold rule can act on, and that band holds more negatives than positives. BsM5 does not raise the ≥ 0.95 share (0.347 → 0.360); it moves crack out of bin 0 into the middle band, which is the ranking gain LA then converts to IoU. AL5 pushes more crack into bin 0.
- Global saturation, for context only (background-dominated): BsM5 confident fraction 0.965 at steps 4k-20k (`results/p13/README.md` line 120). D0's BsM-like rule on the 455-cell pool pseudo-labels 96% of pixels, crack precision 0.48 strict (0.86-0.88 within 2 px), covering only 35-37% of GT crack as crack (`team_2026-10-21/alhvr/design.md`, D0 table). **[E]**
- Of BsD5's true misses on the pool, 70.5% get a confident-background pseudo-label (CSIR/ARTS 83.6%). **[E]** (`skcdf/second_opinion_a2.md`, probe result)
- But removing them barely helps: BsDBn5 has 0.2% confident-background on its misses and still truly misses 0.332 of crack vs BsD5 0.378; LA cuts the share to 46% with true misses 0.359 (same file). **[E]**
- Per-class thresholds were probed once (P5): γ_crack 0.70 moves crack into the "both sure" region only by lowering strict precision to 0.42 (Ω3: 0.17) (`results/p5_region_pl/README.md`, crack table). **Old-era ALHVR nets on the 20% split, not the P-series base**; supporting only. **[E]**

**Reading**
- Confirmation bias is present (confident background on most true misses) but is a minor cause. The bound on any threshold rule is the class-conditional one above: at most 8.4% of GT crack (19.1% for BsM5) sits where a cutoff can act, against more negatives in the same band. BsDBn5 (−0.046 true miss) and LA are consistent with this but are not bounds themselves: BsDBn5 removes background PLs and is confounded with the ABSH head overwrite (`skcdf/null_diagnosis.md` §1.2-1.3), and neither adds crack PLs at lower cutoffs. **[R]**
- Class-adaptive thresholds (DARS/FreeMatch) are predicted to admit mostly negatives for crack. CW-BASS's saturation failure is an analogy, not evidence for our data. **[S]**, never run.

## 2. Mechanism: consistency under strong augmentation for thin structures

**What the methods assume.** Perturbation consistency (Mean Teacher, CutMix-Seg, UniMatch's image + feature dropout) assumes the label survives the perturbation and that the class is large enough for the consistency target not to collapse to background.

**Literature**
- SemiCurv (doi:10.1109/tip.2022.3189823, read §III-D, Tables I-III, V):
  - MSE consistency "collapses to all zeros" on CrackForest 1% (Fig. 8a); they need N-pair consistency.
  - Without geometric augmentation, MT on Gaps384 1% scores 19.2 IoU vs 28.3 supervised: SSL hurts (Table V).
  - At 5%: Gaps384 (1.2% foreground; our crack is 0.19%) is mixed (TCSM +2.9, SemiCurv +3.1, the others ≤ 0) with only +4.1 headroom to 100% labels; CrackForest generic SSL +6 to +7; Crack500 MT +1.5. Single runs as far as the paper states (§0.2). **[E]**
- UniMatch V2 (doi:10.1109/tpami.2025.3528453, §4.4.6, read): τ = 0.95 is best in 4 of 8 settings; on Cityscapes no filtering (τ = 0) is best. The recipe is tuned on blob-dominated benchmarks. **[E]**

**Ours**
- Blur and rotation on 1-2 px labels destroy crack fitting (P1: train AP 0.929 → 0.587; handbook 11 (d) timeline). **[E]**
- UniMatch-style FeatureDropout erases the encoder: the dropout pass keeps 2% of clean crack predictions (D0 keep 0.019-0.022), Gaussian feature noise keeps 91% (`alhvr/design.md` D0 table). **[E]** So a faithful UniMatch port would give crack a near-empty or background target. **[S]** (never run; D0 is inference only)
- CutMix is the only perturbation with a crack signal: CsM5 − Cs5 over cells +0.010 crack IoU, n.d. by seeds (handbook 11 row 11). **[E]**

**Reading.** Our BsM5 crack gain (+0.029, 5 seeds) is about the size of the best Gaps384 gains at the same 23-image regime (+2.9 to +3.1 IoU, single runs). Bigger perturbations are not available for 1-2 px structures without breaking the label. **[R]**

## 3. Mechanism: dual-network disagreement routing (ALHVR, CPS)

**What the method assumes.** Pixels where both networks are confident (Ω1) are already learnt; value lies in disagreement (Ω2/Ω3). ALHVR's premise is its Table 1: CPS on ACDC 10% with Ω1 masked is best (88.58 vs 85.34) (`alhvr/design.md` §2, from the paper PDF).
- ALHVR's own Table 5: the unnamed two-network baseline gives +5.0 of the +9.0 Dice over supervised; both modules add +3.95 (same file). **[E]**

**Ours**
- Ω1 holds 65-70% of unlabelled GT crack and 56-60% of inactive in the ALHVR arms; no loss reaches them (`alhvr/results.md` §6 regions table). **[E]**
- Routing contrast CPSm5 − CPS5 is n.d. (−0.0025 crack IoU, thr 0.0171); AL5 − A5 is WORSE on all three primaries (−0.0169 / −0.1324 / −0.0312) (`alhvr/results.md` §2). **[E]**
- Our pair agrees on 98-99% of pixels (A/B disagreement 0.6-2.0%, same file §6). γ = 0.989 under noise in D0b. **[E]**

**Reading.** On a pretrained, CE+Dice base, the confident-but-wrong crack pixels sit in Ω1. Agreement-based routing cannot see them by construction: two networks from the same ImageNet init and labelled set share the same blind spot. **[R]**
- CSL (doi:10.1109/iccv51701.2025.02031) reaches the same "confident regions are not safe" conclusion on natural images and responds by masking reliable pixels, class-agnostic. **[E]** for its claim; untested here.

**The inactive harm (C's challenge 4).** DTCT (sharpened MSE + entropy minimisation on Ω3) halves inactive recall (0.276 → 0.124) (`alhvr/results.md` §6). Oliver et al. (arxiv:1804.09170, App. E, read) show entropy minimisation drives confident decision boundaries through unlabelled data. The link is a **[R]**, untested by a one-change arm.
- Arm that would test it: ALd5 with the entropy term off, i.e. DTCT MSE only at λ 0.1, against ALd5 (5 v 5). Prediction if the reading holds: inactive recall back to ≥ 0.2. No GPU requested; it does not affect the crack question.

## 4. Mechanism: prototypes
- **Ours:** the reference-code 1/8-resolution prototypes of two independently initialised networks are orthogonal (cos 0.000); at full resolution `x_0_4` cross-network crack accuracy on Ω2a is 0.086 / 0.330 (`alhvr/design.md` D0-1). CG-CPCL adds nothing (AL5 − ALd5 n.d., `alhvr/results.md` §2 S2). Old port: 4.6% correct on Ω3 crack (handbook 13 B3). **[E]**
- **Reading:** cross-network prototype methods assume a shared embedding space. Two decoders with different random inits do not share one, and a 1-2 px class has almost no pixels to average at 1/8 resolution. **[R]**
- Not worth more work. I found no returned paper that makes cross-network prototypes work for thin classes; I do not cite the labelled-anchored prototype papers in `literature/notes/F01` because the tool did not return them this session.

## 5. Mechanism: class-balanced heads and debiased weighting (SKCDF ABSH, DHC)

**Benchmark regime (C's challenge 2).** DINO-Mix's Table 1 (arxiv:2602.07819, read) reproduces the Synapse 20% comparison these methods win on:
- 3D V-Net from scratch, 4 labelled scans, 6 test scans, 3 seeds.
- Generic SSL baselines sit at 0.0 Dice on 4-6 of 13 classes: CPS esophagus 0.0, RAG 0.0, LAG 0.0; UA-MT average 20.26.
- DHC 48.61, SKCDF 64.27, DINO-Mix 66.45. Fully supervised V-Net is 62.09, so SKCDF and DINO-Mix with 20% labels **beat** the fully supervised baseline. **[E]**
- Reading: these gains are rescues of collapsed classes against weak, unthresholded baselines with tiny test sets, not refinements of a working class. **[R]**

**Ours**
- Crack is not collapsed: test IoU 0.30 at 5%, labelled-batch predicted/GT crack 0.99-1.01 (`skcdf/second_opinion_a2.md` §2). **[E]**
- SK1: BsDB5 − BsD5 crack IoU −0.0044, CI [−0.0099, +0.0016], informative null (`skcdf/null_diagnosis.md` §1.1). **[E]**
- The parts of SKCDF's baseline that left room (no threshold, joint BN, λu 10) are already fixed in P13 (`null_diagnosis.md` §1.5). **[E]**

## 6. Mechanism: unlabelled pool size and composition
- **Size is not the problem.** In pixels our 5% pool (455 cells at 512²) is 119.3M against ACDC 10%'s 77.1M; U:L 19.8 vs 8.6 (`alhvr/design.md` §2). SemiCurv's Gaps384 5% is 442 images, the same order. P9: a 28× external pool adds nothing (handbook 11 row 5). **[E]**
- **Rare-class content is small in the labelled set, not in the pool.** The 448-cell pool holds 216,353 GT crack px (`skcdf/second_opinion_a2.md`, probe), including ARTS 10,458 / BMRK 25,811 / CSIR 56,628 (R1, `r1_data_side.md`). The 5% labelled set holds 0 ARTS and 548 CSIR crack px on E-SCDD's own masks (the 47 ARTS and 139 CSIR px in `skcdf/labelling_plan.md` §1 are P6 remap px; R1 correction). **[E]**
- **Why self-training cannot reach an uncovered source [R].** Wei et al. (arxiv:2010.03622, abstract) prove self-training and consistency work under "expansion" (a labelled subset expands through augmentation neighbourhoods) and minimal overlap of class neighbourhoods. Our label-safe augmentation never maps a CFVS crack onto an ARTS crack (0 labelled px), and the faint, wide BMRK cracks (2 labelled cells) overlap background, so they stay under-scored rather than unseen. R1's per-source data fits: BsM5 − A5 crack IoU CFVS +0.042, BMRK +0.002, ARTS −0.022 (ARTS = 3% of test crack px, few cells), while 5% → 100% labels lift BMRK +0.215 (`r1_data_side.md`). Inactive is large, high-contrast and source-invariant, so it expands even into CSIR with 0 labelled CSIR inactive. Chen et al. (doi:10.1609/aaai.v34i04.5763, abstract) is the wrong frame: it concerns unseen classes in the unlabelled set.
- **Literature on when unlabelled data stops helping:**
  - Oliver et al. (arxiv:1804.09170, §4.2-4.5, read): with an equally tuned supervised baseline, the SSL gap shrinks (MT on CIFAR-10 4k: reported 20.66 → 12.31, theirs 20.26 → 15.87); ImageNet transfer (12.09) beats every SSL method; mismatched unlabelled classes can hurt; gains level off as unlabelled data grows. They name the conditions where SSL is the right choice: no related labelled data, labelled set i.i.d. with the pool, and a validation set large enough to tune. **[E]**
  - UniMatch V2 (§4.5, Table 13, read): with a strong labelled baseline, gains are marginal (Cityscapes 3K + 20K: 85.2 → 85.5). **[E]**
- **Reading:** we fail two of Oliver's three conditions. The labelled 23 are not representative of the pool for crack (source mix), and val has 54 cells, 6 with inactive (handbook 11 (b)), so SSL hyperparameters cannot be tuned (handbook 13 C5). **[R]**

## 7. Mechanism: pretrained backbones and foundation models
- **SSL gains shrink as the encoder gets stronger and more confident.** CW-BASS v2's saturation result (98% ≥ 0.95 with DINOv2) and UniMatch V2's real-world table (§6) are the general case. **[E]** for those papers; analogy to us **[R]**: our crack scores are bimodal (§1 table). Reading: the SSL headroom left by our encoder is mostly in classes it gets wrong confidently, which self-training cannot fix. **[R]**
- **EL-specific evidence:** Torpey et al. (arxiv:2402.17611, §4.3-4.4, read), full labels, DeepLabV3-R50: U2PL scores below random init (0.448 vs 0.486 mIoU); CCT ties COCO-supervised; in-domain EL SimCLR (0.517) loses to ImageNet SimCLR (0.534); crack is best with COCO or ImageNet-SimCLR (p ≤ 0.0001). They posit the multi-view nature of these methods is ill-suited to EL. **[E]**
- **Ours:** P15 UCF-EL encoder transfer is n.d. at 5% and worse at 10% (handbook 11 row 7). P4 frozen probe: DINOv2 ViT-S/14 crack AP 0.183 vs ImageNet ResNet-50 0.321 and ConvNeXt-T 0.331 (`results/p4_feature_probe/README.md`). **[E]**
- **SAM-type teachers:** segmentation foundation models fail on tree-like and low-contrast objects, and targeted fine-tuning does not fix it (doi:10.1109/wacv61042.2026.00505, abstract). UniMatch V2 finds SAM's encoder poor for SSL segmentation (§4.4.5, read). Our true misses are exactly low-contrast: relaxed recall 0.42 in the faintest third vs 0.80 in the darkest (`skcdf/null_diagnosis.md` §0.3). **[E]** Prediction: a SAM or DINOv2 teacher will not recover the faint/edge misses. **[S]**, never run; cheap to check (§8, D4).
- **DINO-Mix** (arxiv:2602.07819, ablation, read): on Synapse, the DINOv3 distillation adds +6.6 Dice (48.14 → 54.72) and the minority copy-paste curriculum +16.8 (→ 64.97). The larger lever is class-aware *mixing*, on a baseline with 0-Dice classes. **[E]** Reading: if any outward-looking idea transfers, copy-paste of labelled rare-class content is the better bet than the foundation teacher. **[R]**

## 8. Directions (method side), ranked

Thresholds: rule 1 (P8) on 5 v 5 seeds; crack claims against base+LA (S-a). BsM5 5% run ≈ the AL1 small-queue lane; supervised run ≈ 1.5 h (`skcdf/labelling_plan.md` §2a).

| # | Direction | Falsifiable hypothesis | Evidence for | Cheapest test | Cost | Expected effect vs rule 1 / S-a | Kill result |
|---|---|---|---|---|---|---|---|
| D1 | **Stop SSL method development for crack; invest in the labelled set** | Source-targeted +12 cells (BMRK/ARTS/CSIR crack cells, random within source) beat +12 random at equal budget on crack; a separate arm with inactive-edge cells tests convention (R1's split). +6 BMRK cells is 25% of BMRK's 24 crack cells, so the expected BMRK effect is large | True misses not reached by any PL rule (§1); source-skewed labelled set (§6); Oliver's i.i.d. condition fails; active-learning lines target exactly this (doi:10.1109/wacv56688.2023.00591; doi:10.1109/cvpr52688.2022.00790, abstracts) | Retrospective, supervised only: `skcdf/labelling_plan.md` §2a | ~20 runs × 1.5 h ≈ 30 GPU-h | [S] T − R crack IoU above threshold (≥ 0.01 floor) vs R+LA; ARTS/BMRK relaxed recall +0.1 | T − (R+LA) n.d. and ARTS/BMRK recall < +0.05 |
| D2 | Keep BsM5 (+LA) as the SSL result, scoped to inactive and crack ranking | Already measured | `results/sk1/la_sa.md` §2; `alhvr/results.md` §1 | None (reporting) | 0 | Inactive +0.10 to +0.12 survives LA; crack AP +0.08 | n/a |
| D3 | Inference probe: can any frozen external encoder see the missed cracks? | A frozen CNN (ConvNeXt-T / DINOv3-ConvNeXt) linear probe recalls ≥ 0.3 of the 40 always-missed components or the faint tertile where A5c recalls < 0.1 | P4 shows CNN features carry crack (AP 0.33); the missed cracks are faint (§7) | P4 probe re-scored per source (BMRK/ARTS/CSIR) and on `skcdf/audit_sheet.csv` components; inference only. Pass bar: BMRK crack recall above A5c+LA per source (BMRK is under-scored, not unseen: LA lifts BsM5 BMRK recall 0.191 → 0.279, C's C0.2 via R1), and ARTS (0 labelled px) above A5c+LA | ~1 GPU-h, team-lead OK needed | [S] probably < 0.2. Bound: the 40 components are 5.4% of test crack px, so full recovery there is worth at most about +0.02-0.03 pooled IoU. The informative part is the BMRK slice (27% of test crack) | Probe relaxed recall on the 40 components ≤ A5c's. Then no foundation teacher or distillation run is justified |
| D4 | Rare-class copy-paste into BsM5 (paste labelled crack/inactive patches into unlabelled images) | Raises crack relaxed recall on BMRK/ARTS by pasting the few labelled examples into many contexts | DINO-Mix PIC +16.8 (0-Dice regime); AEL arxiv:2110.05474 adaptive copy-paste +0.7-0.85 mIoU on Cityscapes; CutMix is our only perturbation with a crack signal (§2) | One arm vs BsM5, 5 v 5 | 10 runs, ~10-15 GPU-h | [S] about 0 on crack vs BsM5+LA: it pastes the same 8 labelled crack cells (0 ARTS), so it adds context, not new crack appearance, and §1 leaves almost no score band to move. Inactive possibly + | **Downgraded: not proposed at 5%.** Reconsider only as an add-on after D1, with the new source-covering cells as paste sources |
| D5 | Class-adaptive thresholds (DARS/FreeMatch style) | — | — | Not proposed | — | Upper bound ≈ BsDBn5 / LA (§1); CW-BASS saturation argument | Already effectively killed by the pool probe |
| D6 | MIM pretraining of the U-Net++ encoder on the pool | Masked reconstruction beats ImageNet init on crack at 5% | Torpey: contrastive in-domain lost; MIM never tried on EL. AOI-SSL arxiv:2605.12430 (abstract only) reports MAE wins in a small inspection domain | Pretrain once, fine-tune A5 vs MIM5 | ~1-2 GPU-days pretrain + 10 runs | [S] small; P15 transfer was n.d./worse | MIM5 − (A5+LA) crack IoU n.d. and BMRK recall gain < 0.05. Ranked above D4 and after D3, which gates it (C round 2) |

Not proposed: more routing or prototype variants (§3, §4); balanced heads (§5); skeleton losses (Skeleton Recall, doi:10.1007/978-3-031-72980-5_13, targets broken connectivity, while our misses are faint or edge-type; P14 tolerant loss null).

## 9. Discussion log (R1, C)
- C challenge 1 (survivorship): accepted; scope stated at the top, untried methods tagged [S].
- C challenge 2 (benchmark regimes): §5 now cites DINO-Mix Table 1 (from-scratch V-Net, 0-Dice classes, SKCDF > fully supervised). DARS's regime added in §1.
- C challenge 3 (BsM5+LA passes): conceded in §0.3. SSL improves crack ranking (AP +0.08, bin-0 −0.12); the IoU gain over A5c alone is the LA size. Position narrowed to "does not reach true misses".
- C challenge 4: §3 tags the inactive-harm link [R] and names the one-change arm.
- C challenge 5 (untuned): partly conceded. Independent of λ and τ: the Ω1 crack share (D0 on supervised pairs) and pool true misses (supervised features). The threshold axis is bracketed by BsDBn5 (no background PLs) and LA, both ≤ 12% of true misses. Not separated: CutMix strength, EMA rate and BsM5's λ; a tuned recipe could add about 0.01 crack IoU that rule 1 cannot see.
- R1 round 1: accepted "SSL crack gain is source-bound" as the main data fact (BMRK is the load-bearing source, ARTS is too small to lean on). Took R1's labelled-px correction. D1 now targets by source only, with convention as a separate arm. Agreed no reviewed method predicts recognition on a source with zero labelled crack; D3 (per-source frozen-encoder probe) is the only cheap test that could overturn D1. R1 round 2: BMRK is under-scored, not uncovered (2 labelled BMRK crack cells, 5,387 px; LA lifts BsM5 BMRK recall 0.191 → 0.279); only ARTS is truly uncovered. D3 is now scored against A5c+LA per source.
- C round 1 (all accepted):
  - (1) SemiCurv was quoted selectively: I had omitted TCSM 37.8 on Gaps384, the +4.1 ceiling and CrackForest's +6 to +7. §0.2 and §2 now say "mixed, single-run".
  - (2) Cause 1 now rests on the class-conditional test histogram (8.4% of GT crack in the actionable band; re-derived from `results/al1/hist_revised.npz`). Global 0.965 is kept as context, CW-BASS as analogy, and P5 is tagged old-era.
  - (3) BsDBn5 is no longer called an upper bound (ABSH confound; it adds no crack PLs).
  - (4) Agreed: my cause 1/2 and R1's coverage cause are one mechanism. The teacher is confidently wrong where labels do not cover. What my side adds: why the loop cannot escape (no expansion path, Wei et al.) and why routing or threshold variants cannot reach it (bimodal scores). BsM20 BMRK +0.066 (exploratory) is the best evidence that coverage, not the SSL algorithm, gates the crack gain.
  - (5) D3 bounded at about +0.02-0.03 on the 40 components; D4 downgraded.
