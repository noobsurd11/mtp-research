# Directions for thesis part 1 (training methodology), 10 Oct 2026

What this rests on:
- 4 literature scouts plus 1 reader (notes `literature/notes/F01`–`F05`);
- 15 papers downloaded through IIT Mandi access (`literature/pdfs_inst/`), plus 12 open-access ones (`literature/pdfs/`);
- one new measurement (`results/p3_label_versions/`);
- my earlier reports (situation report, P1, P2, UCF-EL).

Tags: **measured**, **lit** (a paper says so), **inferred**.

---

## 0. Update, night of 10 Oct (P6–P8 measured; P9–P11 running)
- **P6:** label-safe augmentation helps (+0.048 crack IoU, robust over test cells).
  - The ImageNet encoder and CE+Dice saturate AP (scores pile up below 0.001), so AP is not comparable across losses.
  - Only the L3 recipe turns more labels into better scores. Most inactive differences are decided by 3 test cells. **measured** (`results/p6/README.md`)
- **P7/P8 (10% labels, 431 unlabelled):** no unlabelled loss passes its locked rule against the loss-off control. **measured** (`results/p7/`, `results/p8/`)
  - **Tolerant beats hard pseudo-labels on inactive** (P7, robust). Hard PL pushes missed defects to "certain background", a confirmation bias that the tolerant routing halves.
  - **The Mean Teacher pipeline itself handicaps L3:** with the loss off, crack IoU −0.013 and inactive −0.10 vs supervised. The cause is not the EMA teacher. Likely the stronger labelled view (noise) and/or BatchNorm over mixed batches.
- **So §1.2's bet is weakened at 10% labels with a small pool, but not refuted.** The three levers still open are being tested overnight under locked protocols:
  - P9: pool size, 12k external cells;
  - P10: label budget, 5%;
  - P11: pipeline-matched control, which asks whether SSL beats *plain supervised* training.
- If all three are null, the thesis contribution shifts towards:
  - (a) a careful negative result with diagnostics (pseudo-label confirmation bias for rare thin classes; pipeline handicaps);
  - (b) the no-pseudo-label rival (MIM pretraining, §4), moved up.

### 0.1 Update, morning of 11 Oct (P9, P10 measured; P11, P12 running)
- **P9, pool size:** a 28× larger pool does not amplify the loss effect.
  - Tolerant PL passes its locked rule on inactive (+0.056) only because seed noise dropped. The effect is the same size as P8.
  - It is not robust over test cells (CI covers 0). **measured** (`results/p9/README.md`)
- **P10, label budget (5%):** no loss passes. The expected "more gain with fewer labels" did not appear on the P8-style pipeline. **measured** (`results/p10/README.md`)
  - **Two concrete failure modes, both new:**
    - (i) **Collapse.** One seed collapses under hard *and* tolerant PL. It shows in training as a rare-class pseudo-label share about 5× lower.
    - (ii) **Pool mismatch.** The external pool's crack pseudo-labels hurt crack on the same sources' benchmark cells (−0.065 on CSIR+ARTS).
  - When PL does not collapse, it lifts the control by about +0.06 crack and +0.12 inactive (post hoc, 2 seeds).
- **Pipeline handicap:**
  - It grows as labels shrink: D − A is −0.013 crack IoU at 10% and −0.055 at 5%.
  - Swapping only the unlabelled pool with the loss off moves the control, so batch mixing is part of it.
  - P11 (10%) and P12 (5%) test the matched labelled view, with a hardware-matched supervised reference. Results are due about 14:00–17:00 IST on 11 Oct.
- **Effect on §1.2:**
  - SSL is still not shown to beat supervised training.
  - The contribution increasingly looks like (a) a diagnosed account of *why* SSL fails for rare thin classes: collapse, confirmation bias, pipeline and pool effects; plus (b) a fix aimed at collapse (rare-class quotas or thresholds). §4's MIM rival stays first in further work.

---

## 1. Bottom line

1. **The ground moved today.**
   - BenchmarkEL has a newer release (`20221008`, 695 images) and an MIT-licensed extension (E-SCDD, 903 images). Both clean the crack labels: dotted labels joined, widened. **measured**
   - Re-scoring our models on the revised labels raises crack IoU by 0.05–0.07 for every model. It also **flips 10% vs 100%** on crack AP. **measured**
   - So any method comparison on the old crack labels is mostly measuring the labels.
2. **Strongest thesis bet:** an ALHVR-inspired method whose routing is aware of **class rarity** and **label tolerance**.
   - Run on a corrected ground: revised labels, a module-disjoint UCF split, label-preserving augmentation, tolerance and AP metrics.
   - Compare it against a **no-pseudo-label rival**: self-supervised (MIM) pretraining of the same small encoder.
3. **The gap is still open but narrower.**
   - No paper combines ALHVR-style region routing with class-rarity handling (checked against 2025–26 work incl. DCF MedIA 2026, CaPro PR 2026, DCA CVPR 2026). **lit**
   - DCF is now the routing baseline a reviewer will ask for.
4. **P5 (measured today, locked protocol): crack pseudo-labels in ALHVR's uncertain region Ω3 point at the right crack but miss the pixels.**
   - Ω3 holds 72% of GT crack. Strict precision is 0.27, but 0.64 within 2 px.
   - Per-class thresholds pull 40 points of crack out of Ω3, but only by lowering precision.
   - So **hard pseudo-labels fail for rare thin classes, while offset-tolerant targets would keep most of the signal.** That is the concrete hook for the method (§5).
5. **Deployment isn't the binding constraint, but it shapes the design.**
   - About 0.2 s per cell is available. **lit**
   - Severity depends on the **isolated (inactive) area**, not crack pixels. **lit**
   - So keep a ≈5M-parameter CNN student; big models only as teachers; reward crack *connectivity* and inactive-area accuracy.

## 2. New facts that change the picture

| Fact | Consequence |
|---|---|
| **Revised crack labels.** BenchmarkEL `20221008` / E-SCDD change 34–42 of our 50 test masks. Crack px +39–67%; agreement with our labels: test IoU 0.69–0.75, relaxed (2 px) 0.98. **measured** | Our old labels are a noisy version of a cleaned set. That gives a controlled label-noise experiment no EL paper has run |
| Same checkpoints re-scored on revised labels (crack, 3 seeds, test):<br>• SL-10 IoU 0.304 → 0.355, AP 0.492 → 0.527<br>• SL-100 IoU 0.283 → 0.339, AP 0.457 → **0.541**<br>Val AP: SL-10 0.43 vs SL-100 **0.48**. **measured** | "Labels don't help on BenchmarkEL" was partly evaluation noise. Re-run key comparisons on the revised labels |
| **BMRK cells are ELPV cells** (verified on 4 cells, normalised cross-correlation 1.000). **measured by agent** | ELPV is not an independent pool or test set. But its 2,624 image-level labels are free weak labels for the same distribution |
| Real cracks are about 3.4 µm wide (Haase 2018). One pixel ≈ 300 µm at 512 px. **lit** | The 4 px dark line is optical spread, so *any* label width is a convention. That justifies losses and metrics that tolerate offsets and focus on connectivity |
| More public pixel-level EL data than assumed:<br>• PV-Vision (LBNL) crack set<br>• 438 PVEL-AD masks (Lin 2026)<br>• MultiSolSegment (585, multi-label)<br>• Pratt "CSB S2/S3" in the PV-S3 journal version (unverified) | Cross-source and held-out-source crack evaluation is now possible |
| The PV-S3 journal version fixes none of the flaws we measured: 30-epoch baseline, background convention, leakage. **lit** | Cite it critically; it stays a weak baseline |
| **EL anomaly-from-normal (EI-AE, Lin 2026):** crack pixel AP 0.14, few-shot 0.34. **lit** | Normal-only anomaly priors are weak for thin cracks. Use them only for region classes |

## 3. Constraints any method must meet

- **Data:**
  - BenchmarkEL: 582–903 labelled images, 24–29 classes; crack 0.2% of pixels; labels are a convention.
  - UCF-EL: crack is a region class; the split is leaky until we re-split by physical module.
  - Unlabelled: CSIR/ARTS pool (11.9k of 150k downloaded), UCF defect-free cells, PVEL-AD 36.5k (boxes), ELPV (image labels).
- **Compute:** gaint 1× 32 GB, shared with another process (about 6 GB). cv02 A6000s are shared: never use a GPU where another user holds more than 4 GB. Budget per idea: about 1–2 GPU-days.
- **Deployment:** a small CNN at ≥5 cells/s; foundation models only as teachers or for pretraining.
- **Evaluation discipline** (our own rules):
  - step-matched baselines;
  - loss-off controls;
  - ≥2 labelled splits × 3 seeds;
  - final-step checkpoint;
  - per class: strict IoU, AP, relaxed P/R at 1–2 px, clDice;
  - inactive-area error;
  - for BenchmarkEL, state the label release.

## 4. Direction map (cheapest falsifying test first)

| # | Direction | Evidence | Fit to our facts | Cost | Main risk | First test (decision rule) | Verdict |
|---|---|---|---|---|---|---|---|
| 0 | **Fix the ground:** revised labels; label-preserving augmentation (flips/90°, no blur on labels); module-disjoint UCF split; metric suite | P1: augmentation alone takes crack AP from 0.93 to 0.59; P3 above | prerequisite for every row below | 1–2 days, mostly CPU | none | supervised {current aug, label-preserving} × {wCE, CE+Dice} on revised labels, held-out. **Pick the base recipe** | **do first** |
| 1 | **Tolerance / noise-aware supervision for thin labels:**<br>• shift-tolerant CE (Mnih & Hinton 2012 registration noise);<br>• band/soft targets (SVLS, centerline distance);<br>• STEAL-style re-alignment | lit: Mnih 2012, STEAL (+18.6 AP). Skeleton Recall shows no significant gain on concrete cracks and more false positives (2025 study) | jitter ±1 px, 48% within 1 px; dotted labels; 3.4 µm physical width | hours per arm | rewards fat predictions; always report relaxed precision and AP | train on **old** labels, test on **revised**: noise-aware loss vs CE+Dice. Pass if it recovers ≥50% of the old→revised training gap | **strong, novel on EL** |
| 2 | **ALHVR-inspired, rarity-aware routing** (core of the user's goal):<br>• per-class thresholds γ_c for the Ω regions;<br>• rare classes in Ω3 get labelled-anchored targets (BUR direction) or tolerance-aware consistency instead of hard pseudo-labels;<br>• one-vs-rest specialist heads for crack/inactive pseudo-labels (CGS/DCA, dropped at inference) | ALHVR Table 1; DCA: tail organs 0 → 39–48 Dice; DHC; CSL. No method combines routing with rarity (checked to 2026) | Ω3 holds 71% of crack; teacher right about 62% there; UCF interconnect/corrosion carry 64–78% of the label gap | about 18 runs (two networks) on gaint + cv02 | pseudo-labels in Ω3 may be too wrong for any routing to save | **Done (P5):**<br>• crack Ω3: strict P 0.27 / 2 px 0.64 (global γ);<br>• under per-class γ_c: 2 px P 0.48, recall 0.29;<br>• inactive Ω3 strict P 0.43.<br>Rules fire: no hard pseudo-labels for rare classes in Ω3; per-class γ alone doesn't help | **main method candidate, but only with tolerance-aware targets** |
| 3 | **Unlabelled data without pseudo-labels:** MIM pretraining (SparK on our U-Net++ encoder, or ConvNeXt V2-Atto FCMAE, 3.7M params) on CSIR/ARTS + UCF-normal + PVEL-AD cells | AOI-SSL: MAE best in a 7k industrial set; VasoMIM: +18 Dice at 25% labels on vessels; Torpey: contrastive in-domain *lost* on EL | no pseudo-labels, deployable as is; untested on EL at low labels | 1–2 GPU-days | half-contrast pool; reconstruction targets may skip cracks | **Probe done (P4):** a frozen ImageNet CNN with a linear head gets crack AP 0.33 and inactive 0.42 (random: 0.03 / 0.10), above our own trained encoder's features (0.24 / 0.27). **Next:** SparK/FCMAE vs **ImageNet** init (not random) at UCF 1–5% and BenchmarkEL 10% | **must-run rival; ImageNet-init CNN becomes the default baseline** |
| 4 | **Weak and mixed supervision:**<br>• ELPV image labels (same cells as BMRK);<br>• PVEL-AD boxes (36.5k);<br>• module-level labels (Kang 2024, Gil 2025) | Božič 2021: 5 masks + weak labels reach AP 92 (image-level); Boxes2Pixels +7 mIoU | inactive/region classes yes; thin diagonal cracks fill boxes badly | 1–2 days | domain shift (PVEL-AD is NIR, mostly poly) | crack/inactive AP at 5% masks ± ELPV image-level auxiliary loss | medium |
| 5 | **Cross-dataset transfer and generalisation:** BenchmarkEL ↔ UCF-EL encoder transfer; held-out source (PV-Vision, Lin's 438 masks) as an out-of-distribution test | no EL paper does it | WattCycle data will be another source | about 1 day | class definitions differ (UCF crack = region) | encoder-only transfer vs ImageNet at UCF 5% (re-split) | medium, cheap; good for a chapter |
| 6 | **Foundation-teacher distillation** (DINOv3 ConvNeXt / RADIO features → 5M student) | DINO-Mix; E-RADIO; SemiSAM+ (+8–18 at 1 label, but fails on thin structures) | helps region classes more than 1–2 px cracks | 1 teacher pass + short runs | 16 px ViT patches miss cracks; DINOv3 weights are gated (you'd accept the licence) | **P4:** DINOv2 patches are weak on crack (0.18 vs 0.32 ImageNet ResNet-50) and on par for inactive (0.38). Use ViT teachers for region classes only; use a CNN teacher for cracks | **narrowed: region classes only** |
| 7 | **Rare-class synthesis** (PV-DDPM mask-conditioned diffusion; copy-paste of inactive/interconnect) | PV-DDPM downstream evidence is weak; masonry study: > ~2k synthetic patches cost 40% F1 | UCF corrosion appears in 12 test images | days | realism; leakage via generator training data | capped at ≤30% synthetic; UCF interconnect/corrosion IoU | low priority |
| 8 | **Anomaly prior from normal cells** (PatchCore, EI-AE) as a router or prior | EI-AE crack pixel AP 0.14 | region classes only | minutes | weak on cracks | per-class pixel AP on UCF test | downgraded |
| 9 | **Active learning / annotation budget** for WattCycle's own labelling | Otamendi 2023: −60% annotation cost (lit) | practical for parts 2–3 | – | – | later | park for part 3 |

## 5. Recommended thesis shape (my pick; yours to decide)

**Title idea:** *Learning rare, thin EL defects from few, noisy labels.*

- **Ch.1, diagnosis and protocol** (largely done):
  - label conventions and the revision;
  - metric ceilings;
  - leaky splits;
  - what earlier SSL claims really tested.
- **Ch.2, method:** *one tolerance mechanism for both kinds of noisy target* (rows 1 + 2).
  - Human crack labels are jittered ±1–2 px, and teacher pseudo-labels are off by 1–2 px (P5). So use one offset-tolerant loss for both:
    - crack target credited if the prediction lies within r px (max-pool or soft-band on the prediction side);
    - a relaxed-precision guard against fattening.
  - ALHVR-style routing decides **per class** where each target applies:
    - head classes: plain pseudo-labels in confident regions;
    - rare thin classes: tolerant consistency in Ω2/Ω3, anchored to labelled data (BUR direction) where the teacher is unsure.
  - Novel on three counts: rare-class routing (no 2026 work), tolerance-aware unlabelled loss (none multi-class or offset-tolerant), and EL.
- **Baselines:**
  - supervised with the fixed recipe;
  - MT/FixMatch with correct CE;
  - ALHVR, BUR, DCF, DHC;
  - MIM-pretrained supervised (row 3).
- **Test beds:** UCF-EL re-split (label gap, rare region classes) and BenchmarkEL revised labels (thin crack, inactive).

**Fallback, if row 2's offline check fails:** rows 1 + 3, i.e. noise-aware supervision plus MIM pretraining, with the diagnosis. That is still a complete, publishable story.

## 6. Next steps, in order (each needs your go)

1. ~~Row 2 offline check~~: **done (P5)**, see above.
2. ~~Row 3 probe~~: **done (P4).** Pretrained CNN features carry crack and inactive signal far beyond random. DINOv2 is weak for crack. Our from-scratch 5M U-Net++ is a weak base, so **every future arm should start from an ImageNet (or in-domain MIM) CNN encoder**.
3. **Row 0, ground** (protocol locked first):
   - adopt revised labels;
   - UCF module-disjoint re-split;
   - metric suite;
   - supervised recipe sweep.
4. **Row 1 experiment:** train on old labels, evaluate on revised; offset-tolerant loss vs CE+Dice.
5. **Pilot of the §5 method** on BenchmarkEL revised (inactive and crack) and UCF re-split 5%, against loss-off, ALHVR, BUR and DCF.

## 7. Caveats

- **P4 and P5** are offline probes: one labelled split, 2 seeds or runs each, eval-mode BatchNorm. P4's random baseline is near-degenerate; the margin makes this irrelevant to its verdict.

- **P3 is exploratory**, with no locked protocol, and E-SCDD's annotation process is not documented. Wider revised labels flatter our over-predicting models, so the AP ranking change is the more robust signal.
- **Agent-read sources:** many 2025–26 papers were read at abstract or section level by agents. The novelty claim rests on searches, not exhaustive coverage. Read DCF and CaPro yourself before claiming the gap.
- **Unverified:** Pratt "CSB S2/S3" (from the PV-S3 journal) and PVEL-S, until we see the data.
- **Downloads:** Elsevier PDFs came through your Chrome profile (IIT Mandi), IEEE through curl on campus IP. All PDFs stay local; do not redistribute.
