# Literature survey: training methodology for rare, thin defects in EL segmentation

Date: 2026-10-08. Form: a narrative/integrative literature map (ARS `lit-review` mode). The parent session's directive set the form; the review-form note was not shown because this ran as a non-interactive worker. Scope: A EL defect segmentation, B rare-class SSL, C thin structures, D fair SSL evaluation, E unlabelled data without pseudo-labels.
Every source has a verified URL or arXiv ID (arXiv IDs checked through the arXiv API). Per-paper notes are in `notes/`; the full list is in `papers_index.md`. Labels: [author-acknowledged], [reader-inferred], [ours] = our measured numbers (handoff 2026-10-07 and `analysis/`). Read scope is given per paper in the notes. Abstract-only papers get no method critique.

**Correction to `analysis/papers_metrics.md`:** Fioresi et al. 2022 does state "a mean intersection over union score of 57.3%" in its abstract. That is most likely a 5-class mean including background [reader-inferred]. The earlier claim that 57.3 "is not in Fioresi's paper" is wrong. The point that it cannot be a 4-defect IoU mean still stands.

---

## A. EL / PV defect segmentation: what the field has, and its problems

The field is small. Pixel-level, multi-class EL segmentation rests on two public datasets: BenchmarkEL (Pratt et al. 2021, 2023; Torpey et al. 2024; Pratt thesis 2024) and UCF-EL (Fioresi et al. 2022; Jha et al. PV-S3 2025). Other work uses private or newer data (MultiSolSegment 2026, SEiPV-Net 2023, STC-Net 2026) or neighbouring tasks (ELPV classification, PVEL-AD detection, weakly supervised cracks by Mayr et al. 2019).
**Semi-supervised work on EL segmentation is limited to two efforts:**
- **PV-S3**: Mean Teacher with SemiCE.
- **Torpey et al. 2024**: CCT and U2PL as pretraining regimes, at the full label budget only.
No EL paper we found reports an SSL label-efficiency curve against step-matched supervised baselines with loss-off controls. [bounded: searches in this pass, plus the full texts of Pratt 2023, Fioresi 2022, PV-S3 and the Torpey 2024 sections read]

### Issues in existing EL papers

| Paper | Issue | Effect on reported numbers | Provenance |
|---|---|---|---|
| Pratt 2023 (BenchmarkEL) | Test set hand-picked for defects; all 50 test images contain crack | inflates crack recall, hides label effects on inactive | [author-acknowledged §3.2; effect ours §6.7] |
| Pratt 2023 | Per-image **median** IoU; absent-class rule not stated | changes the mean by about 3x depending on the rule | [reader-inferred] |
| Pratt 2023 | One run per model; no optimiser, LR or epoch details; custom weights tuned by DOE on an unstated split | not reproducible; possible selection on test | [checked §3: none found] |
| Fioresi 2022 (UCF-EL) | "validate the model on the validation/testing set" each epoch | likely model selection on test | [author quote; effect reader-inferred] |
| Fioresi 2022 | Paper has 17,064 images; public release about 11,851 | headline not reproducible on public data | [ours] |
| Fioresi 2022 | mIoU 57.3% next to F1 per defect | likely includes background; not comparable to defect-only IoU | [reader-inferred] |
| PV-S3 2025 | Released loss `ignore_index=0`: the model never predicts background; metric drops background-GT pixels | 0.828 under their convention vs 0.050 standard | [ours, code] |
| PV-S3 2025 | Released split lists put 1,769/2,289 public test images in train and 437 in val | leakage | [ours] |
| PV-S3 2025 | Supervised baseline at 30 epochs, "not able to learn" | SSL gain inflated; our step-matched SL beats every PV-S3 arm | [author-acknowledged §4.2; ours] |
| PV-S3 2025 | Table 6 copies Pratt's per-image-median numbers next to their dataset-level background-free IoU | invalid cross-paper comparison | [ours] |
| Torpey 2024 | Full label set only; best-val checkpoint | says nothing about SSL at low budgets | [reader-inferred from sections read] |
| SA-UNet++ 2025 | Not EL data; per-image mean including background; single run | no evidence for EL | [ours] |
| MultiSolSegment 2026 | Headline pixel accuracy 98.2% vs mean IoU 0.384; flip augmentation reported with the split counts | pixel accuracy is dominated by background; possible augmented-copy leakage | [reader-inferred] |
| STC-Net 2026 | Train mIoU 95.98 reported next to test 72.52 | overfitting or shift; dataset not described in the abstract | [abstract] |
| Field-wide | No tolerance-aware or skeleton-based crack metric among the four EL papers read in full; no multi-split, multi-seed protocol except Torpey (multi-run + Tukey HSD) | crack IoU on 2–3 px cracks punishes 1 px offsets; single-split results are fragile | [bounded: Pratt 2023, Fioresi 2022, PV-S3, Torpey 2024] |

**One structural point from MultiSolSegment applies to BenchmarkEL.** Single-label masks force crack pixels that cross busbars, gridlines or ribbons into one class. BenchmarkEL has 24 mutually exclusive classes, including gridline, busbar and ribbon. So crack labels are likely inconsistent where cracks cross metallisation [reader-inferred; testable on our data]. That is label noise placed exactly on the rare class.

---

## B. SSL for rare classes: mechanisms and the evidence behind them

| # | Mechanism | Representative work | Evidence for rare/tail classes | Strength | Fit to our case |
|---|---|---|---|---|---|
| 1 | **Rare-class-biased sampling and mixing** | AEL (adaptive equalization sampling, adaptive CutMix/Copy-Paste); DAFormer Rare Class Sampling; BCP; ClassMix | AEL cumulative ablation (Cityscapes 1/32): 69.1 → +DR 70.3 → +AES 72.5 → +ACM 73.4 → +ACP 74.3 (1/16: 72.1 → 73.9 → 74.4 → 75.1 → 75.8). Tail classes +10 to +22 IoU vs CutMix-Seg | **Strong** (multi-split ablation; natural images) | Easy to test: oversample labelled crack/inactive images, crack-aware mixing. Copy-pasting 2–3 px cracks needs care (texture, busbars) |
| 2 | **Distribution-aligned / class-wise thresholds** | DARS; CReST; FreeMatch; AEL confidence bank | DARS Cityscapes 1/8: tail mIoU 54.0 → 57.9 vs ST. Over-confidence makes single thresholds degenerate (81.3% of road pixels at confidence 1) | **Moderate** | Directly addresses our pathologies: UCF corrosion pseudo-labels at 23x their labelled share [ours]; crack over-prediction |
| 3 | **Class-aware loss re-weighting from pseudo-label statistics or difficulty** | DHC (DistDW + DiffDW); GA loss; Basak 2022 | DHC Synapse 20%: 33.6 (CPS) → 48.6 Dice, 3 seeds; esophagus and left adrenal 0 → 10–13. GA: +17.9 with CPS | **Moderate** (6 test scans; medical) | Our 24-class weighted CE gives weight 0 to absent classes (12 classes at 2% labels) [ours]. Same failure mode |
| 4 | **Use unreliable pixels as negatives** | U2PL | Strong on VOC/Cityscapes; **on EL: 0.448 mIoU, below random-init supervised 0.486 (Torpey 2024)** | **Conflicting**; negative evidence on our domain | Low priority |
| 5 | **Region-specific learning in ambiguous regions** | ALHVR (DTCT, CG-CPCL); MCF (competitive pseudo-labels); BUR (opposite allocation) | ALHVR Table 1 (ACDC 10%, CPS): masking the reliable-stable region gives the best Dice. No rare-class analysis | **Weak for rare classes** (few-class medical; no imbalance study) | Premise holds structurally: Ω3 holds 71% of crack pixels [ours]. But the winner is right on only about 62% of crack pixels there [ours]. BUR's alternative (labelled loss on uncertain regions; unlabelled loss on certain regions only) is untested here |
| 6 | **Prototype / memory-bank features** | ALHVR CG-CPCL (per-batch); U2PL memory bank; USRN subclasses | Per-batch cross-network prototypes: crack accuracy 4.6% (1.1% per-batch) [ours] | **Negative** (per-batch, unlabelled); labelled-GT memory banks untested | Only labelled-GT prototypes with EMA memory are worth considering |
| 7 | **Strong pretrained encoder** | UniMatch V2 (DINOv2); Torpey 2024 | UniMatch V2: SSL gain about +3 mIoU on Cityscapes 1/16 with DINOv2. EL: COCO ≈ IN-SimCLR ≈ CCT (statistically equivalent) | **Moderate** | Our from-scratch 5M U-Net++ is a weak base; SSL gains measured on it may not transfer |
| 8 | **Thin-structure supervised losses** | clDice; Skeleton Recall (multi-class); focal Tversky; boundary loss | Vessels, roads, neurons, concrete cracks; Skeleton Recall >90% cheaper than clDice | **Moderate–strong** (supervised side) | Crack is **fit-limited** (train IoU 0.33 on 47 images) [ours], so the supervised loss is a first-order lever |
| 9 | **Operating point / logit adjustment** | Menon et al. 2021; Pratt 2023 ("dilated predictions") | Long-tail classification theory. Our crack-logit bias: +0.03 test defect mIoU, more than any SSL arm [ours] | **Moderate** | Must be separated from any SSL gain, or the SSL "gain" may just be a threshold shift |

### Lineage relevant to an ALHVR-inspired design
- MCF (CVPR 2023): dynamic competitive pseudo-labels between two heterogeneous subnets.
- ALHVR (ICCV 2025): DTCT, with competition per pixel, applied to perturbed predictions in the doubly unconfident region. It also adds a prototype path for the singly confident region.
- BUR (2025): argues the reverse allocation.
- DHC / GA / AEL / DARS: the only lines that address class imbalance explicitly. **None of them uses region-aware routing; ALHVR's line uses no class awareness.** That is an unoccupied intersection in what we found [bounded: this survey's searches].

---

## C. Thin structures

- **Losses:**
  - clDice is skeleton-based and topology-preserving.
  - Skeleton Recall is cheap and multi-class, and its datasets include concrete cracks.
  - Persistent-homology losses are expensive.
  - Focal Tversky sets the P/R trade-off explicitly.
  - Boundary loss is distance-based.
  - For a 24-class single-label EL setup, Skeleton Recall is the only one that is explicitly multi-class capable [author-acknowledged in its abstract].
- **Metrics:**
  - Metrics Reloaded recommends clDice for connectivity and NSD (surface Dice with tolerance) for boundaries.
  - Crack literature uses 2 px or 5 px tolerance precision/recall and ODS/OIS.
  - **Caution (What's Cracking, §VI-B3):** tolerance metrics can be gamed by wider predictions. Our models already over-predict crack width (precision about 0.3) [ours]. So any relaxed recall must be reported with relaxed precision and a width-insensitive score. Threshold-free AP and ODS/OIS remove operating-point effects.
- **SSL for thin structures:** in the searches made, crack and vessel SSL methods are generic consistency or pseudo-labelling. **No SSL objective was found that is tolerance- or skeleton-aware** (e.g., a consistency loss on skeletons rather than pixels) [bounded].

## D. Fair SSL evaluation

- Oliver et al. 2018:
  - tuned baselines close much of the gap;
  - SSL is sensitive to the labelled set and to out-of-distribution unlabelled data.
- nnU-Net Revisited 2024: inadequate baselines invalidate many claims.
- UniMatch V2: gains shrink with strong encoders.
- Yuan et al. 2021: BN statistics are corrupted by strong-augmentation streams. This is the published precedent for our unexplained "4+4 inactive gain with loss off" [ours].
- EL-specific: Torpey et al. are the only EL authors with multi-run statistics (Tukey HSD), and they still report test results of the best-val model.
- **Protocol we should hold ourselves to** (each item backed above):
  - step-matched supervised baselines;
  - loss-off controls with an identical forward pass;
  - multiple labelled splits, not just seeds;
  - a fixed checkpoint rule;
  - per-class and threshold-free metrics plus a thin-structure metric;
  - multiple-comparison correction.

## E. Unlabelled data without pseudo-labels

- On EL, in-domain SimCLR (22k images) gave 0.517 against 0.486 from scratch, below COCO (0.544) and IN-SimCLR (0.534), at full labels (Torpey 2024).
- A small-domain industrial study (AOI-SSL 2026) found MAE the most effective self-supervised method and better than ImageNet under a fixed fine-tune budget.
- Medical evidence (Models Genesis; Azizi et al.) favours domain-specific self-supervision when labels are scarce.
- **Untested on EL:**
  - masked-image pretraining;
  - any self-supervised pretraining at low label fractions;
  - supervised transfer UCF-EL → BenchmarkEL.
- Hypothesis [reader-inferred]: augmentation-invariance objectives (SimCLR blur and crop) may erase 2–3 px cracks, while masked reconstruction keeps local detail.

---

## Gaps and open questions for the thesis (grounded in our measured facts)

1. **Is there room for SSL at all, and where?**
   - BenchmarkEL test defect mIoU is flat from 10% to 100% labels [ours].
   - UCF-EL has a clean gap (0.536 / 0.493 / 0.415 / 0.227 at 100/20/5/1%) [ours].
   - No EL paper reports an SSL label-efficiency curve under a fair protocol. **A properly controlled label-efficiency study on EL is itself missing from the literature.**
2. **Rare thin classes live in the ambiguous region, where teachers are worst.**
   - ALHVR's premise matches our data: Ω3 holds 71% of crack pixels [ours].
   - The literature offers three ways to get usable targets there:
     - (a) anchor ambiguous regions on labelled data (BUR);
     - (b) class-aware thresholds or distribution alignment so rare classes are neither drowned nor run away (DARS, FreeMatch, AEL);
     - (c) class-aware weighting from pseudo-label statistics (DHC, GA).
   - **No work combines region routing with class awareness** [bounded].
3. **Geometry-aware supervision for 2–3 px cracks.**
   - Crack is fit-limited even on training images [ours].
   - Pixel-exact consistency and pseudo-labels on 2–3 px structures are fragile under geometric augmentation and 1 px offsets.
   - Gap: SSL consistency defined on skeletons or with tolerance (no prior found) [bounded].
4. **Label definition.** Single-label 24-class masks force crack/busbar/gridline choices (MultiSolSegment's argument). Whether BenchmarkEL's crack labels are inconsistent at crossings is checkable on our data before any method work.
5. **Evaluation.**
   - No EL paper reports thin-structure metrics.
   - Most use test-set or best-val selection.
   - PV-S3 drops background.
   - A metric section (tolerance-aware P/R with the width caveat, clDice or skeleton recall, AP, per-class IoU, multiple splits) would be a contribution in itself.
6. **Unlabelled data without pseudo-labels** (masked-image pretraining on the 12k–150k cells; UCF → BenchmarkEL transfer) is untested at low label budgets on EL. It is the main competitor any ALHVR-style method must beat.
7. **Operating point vs learning.** Class weighting and logit bias move crack along a P/R curve (our +0.03 from bias). Any claimed gain must be shown at a fixed or optimised operating point (AP, ODS) to rule out a threshold effect.

## Limitations of this survey
- Many entries were read at abstract level; method critiques are given only where the full text or sections were read.
- No PRISMA-style search: queries are logged implicitly in the notes.
- Journal-only EL papers (MDPI, Elsevier) behind 403s were not read.
- Pratt 2021 and the Pratt 2024 thesis were not read in full, and they are probably the richest sources on BenchmarkEL's annotation protocol.
- No citation-graph crawl of ALHVR's citing works: the Semantic Scholar API was rate-limited, and web search found no successors as of 2026-10-08.
- AI-assisted: this survey was compiled by an AI agent with web search; every link was retrieved, but the user should read the primary sources before citing.
