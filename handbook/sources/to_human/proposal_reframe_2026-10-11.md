# Rethinking the problem from all evidence so far (11 Oct 2026)

Draft for the mid-term proposal. Every claim cites a measurement (P-number, or "phase 1" for the pre-reset handoff) or is marked **lit**. Phase-0 history is unrecoverable and is not used.

## 1. What the problem actually is

**The request:**
- WattCycle: detect defects in EL images, grade their severity, estimate power loss, on deployable hardware.
- Advisor: a paper and a lightweight model.

**The chain that delivers value:**
EL image → defect maps → per-cell quantities (crack length and connectivity, isolated area, inactive area fraction) → severity grade (Köntges A/B/C) → power-loss band.
- Power loss tracks the isolated and inactive area, not crack pixels. **lit**
- So pixels matter only through these quantities.

**Classification:** this is not mainly a semi-supervised learning problem. It is
> thin-structure and region segmentation, from few labels with imprecise geometry, with a long-tailed class distribution, several image sources, and a small test set, whose real output is a measurement.

Each part of that sentence is measured:

| Property | Evidence |
|---|---|
| **Thin structures with imprecise geometry** | Crack labels have a median width of 2 px. A real crack is about 3.4 µm wide against 300 µm per pixel (**lit**), so label width is a convention.<br>Two annotations of one image agree at 0.26 IoU (one pair, P1). The old vs revised labels agree at 0.73–0.81 IoU, but 0.98 within 2 px (P3). |
| **Few labels and a long tail** | Crack is 0.2% of pixels.<br>Inactive is in 2 of 23 labelled cells at 5% and 4 of 47 at 10%. |
| **Several sources** | 5 sources in BenchmarkEL.<br>The unlabelled pool is CSIR/ARTS only, and 57% of it has half the contrast.<br>That pool hurts crack on its own sources: −0.065 [−0.092, −0.026] (P10). |
| **Small test set** | Inactive appears in 16 test cells, and the top 3 hold 59% of its pixels. Most inactive differences flip without them (P6). |
| **Output is a measurement** | The headline metric so far has been pixel IoU or AP, which neither WattCycle nor the grading uses directly. |

## 2. Where the error comes from: an effect-size budget

| Source of change in our numbers | Size | Evidence |
|---|---|---|
| Label version (old → revised crack masks) | crack IoU +0.05 to +0.07; flips 10% vs 100% | P3 |
| Supervised recipe (augmentation, loss, encoder) | crack IoU +0.05 (robust over cells); fitting 0.38 → 0.86; inactive ±0.18 (3-cell driven) | P1, P6 |
| Operating point and calibration (Dice saturation) | 42% of GT crack scored < 0.001; AP not comparable across recipes; a val-picked crack-logit shift gave +0.03 | P6; phase 1 |
| Label quantity (L3, 10% → 100%) | crack IoU +0.075, inactive +0.135; 10% → 20% crack: +0.002 | P6 |
| Pipeline confound (BN mixing in SSL arms) | −0.015 to −0.028 crack (within gaint) | P12 |
| Unlabelled loss (SSL) | crack ≈ 0 to +0.01; inactive +0.05 (fragile); one seed in three collapses at 5% | P8–P10 |
| Test-cell sampling, inactive | decided by about 3 cells | P6 |
| Seeds | crack sd 0.003–0.005; inactive sd 0.02–0.06 | P6, P10 |

**Reading:**
- The levers rank: measurement and labels, then the supervised recipe, then label quantity. The unlabelled loss is the smallest effect we have measured.
- Since 10 Oct we ran five SSL protocols (P8–P13).
- In the same time we ran none of the three directions our own report rated strong and cheap:
  - row 1, tolerance-aware supervision;
  - row 3, pretraining without pseudo-labels;
  - row 5, cross-dataset transfer.

  That allocation is the main thing to correct.

## 3. What we have that others do not (our lead)

1. **Rigour where the EL literature has none.**
   - Reproductions show published SSL gains depend on conventions: Jha's code never models background; Pratt's metric uses per-image medians.
   - Our protocols are locked in advance, use loss-off controls and an image bootstrap, and we measured failure modes rather than tuning past them.
   - No EL paper evaluates label-efficient methods this way. In the spirit of Oliver et al. (NeurIPS 2018), a realistic evaluation is itself a contribution. **lit**
2. **A measured, specific mechanism for thin rare classes.**
   - Teacher crack pseudo-labels are right within 2 px (precision 0.96) but wrong pixel-exactly (0.59), and the confident ones cover 8% of crack (P5).
   - Human labels have the same 1–2 px ambiguity (P1, P3).
   - So one offset-tolerant objective for both kinds of target is a method grounded in measurement. No paper combines rarity-aware routing with offset tolerance (searched to 2026). **lit**
3. **Measured failure modes with candidate fixes:**

   | Failure mode | Evidence | Candidate fix |
   |---|---|---|
   | Rare-class collapse at 5% (rare pseudo-targets 5× rarer) | P10 | a share floor |
   | Rare-class over-prediction on UCF (corrosion 23× its labelled share) | phase 1 | a share cap; it raised corrosion IoU 0.067 → 0.631 |
   | BN mixing | P9, P12 | separate forward, bit-exact control (P13) |
   | Mismatched unlabelled pool | P10 | match the pool to the target source |
   | Invalid consistency loss (SemiCE) | P2 | check what a loss's target says before training |

## 4. Goal

> Make EL defect assessment reliable from few, imprecise labels: measure what matters, learn under label ambiguity and scarcity, and deliver it in a small model.

| Objective | Output | Success criterion (pre-registered per protocol) |
|---|---|---|
| **O1 Measurement** | A task-aligned, variance-aware protocol:<br>• per-cell crack tolerance-F1 and skeleton-length error;<br>• per-cell inactive area-fraction error;<br>• isolation and Köntges-grade agreement (GT-derived vs predicted);<br>• an error budget and the minimum detectable effect per metric;<br>• an extended test set. | Metric spread across seeds and cells is small enough to detect the effects in §2 at a practical seed count |
| **O2 Learning from imprecise thin labels** | One offset-tolerant objective for human labels and pseudo-labels, plus rarity-aware routing with a two-sided class-share control | Beats the step-matched supervised recipe on O1 metrics at ≤ 10% labels, ≥ 5 seeds, and survives the cell bootstrap |
| **O3 Using unlabelled EL data, compared fairly** | Three uses on one footing:<br>(a) pseudo-label SSL on a clean pipeline;<br>(b) in-domain pretraining, or transfer from UCF-EL's 9.5k labelled cells;<br>(c) distillation into the small model | A ranked answer with effect sizes. Prior from evidence: (b) and (c) are safer for thin cracks. P4: pretrained features beat random by +0.30 crack AP and our own trained encoder by +0.08. P5: pseudo-labels are imprecise at pixel level |
| **O4 Deliverable** | A 2–5M-parameter model (INT8) plus a severity pipeline that outputs per-cell quantities and a grade | Grade agreement (Cohen's κ) close to the GT-derived grades, at ≥ 5 cells/s on the target device |

## 5. Next experiments, ordered by information per cost

| # | Question | Design | Cost | Decision rule |
|---|---|---|---|---|
| E1 | Do task metrics measure more stably and rank methods differently? | Re-score all existing checkpoints (P6–P13) with the O1 metrics; error budget; minimum detectable effect; add the 117 cells of BenchmarkEL `20221008` not in our 582 (112 CSIR, 5 BMRK; 35 with crack, 10 with inactive) | CPU, about 1 day | Adopt as primary metrics if the bootstrap CI on per-cell metrics is narrower than on pooled IoU |
| E2 | Does tolerance help with human labels too? (directions row 1) | Supervised L3: CE+Dice vs offset-tolerant loss. Train on old labels, test on revised; also train on revised at 10% and 100% | about 12 runs, one night; about 2 h of code | Recovers ≥ 50% of the old → revised gap, with no relaxed-precision drop > 0.05 |
| E3 | Is unlabelled or related data worth more as pretraining than as pseudo-labels? (rows 3, 5) | Encoder init: ImageNet vs UCF-EL-supervised vs in-domain MIM; fine-tune at 5% and 10% | UCF transfer about 1 night; MIM 1–2 GPU-days | Beats ImageNet init on O1 metrics at 5% |
| E4 | Clean-pipeline SSL (P13; protocol locked, launch on hold) | CutMix and separate BN; then the class-share floor | P13: one night on cv02 | As locked (amended) |
| E5 | Small model | Distil the L3 teacher into a 2–5M student using labelled + in-domain unlabelled cells | about 6 runs | Within a set margin of the teacher on O1 metrics |
| E6 | Severity pipeline | Rebuild post-processing (lost in the reset): components, skeleton, isolation via the busbar/ribbon topology mask, Köntges A/B/C; GT-derived grades as reference | CPU, 2–3 days | Grade κ on GT masks vs predictions |

E1 comes first because every later decision depends on what we measure.

E2, E3 and E4 can share GPUs tonight. E5 and E6 follow the mid-term.

## 6. Mistakes we own, and the rule each one left

| Mistake | Rule we now follow |
|---|---|
| Ran a consistency loss (SemiCE) for weeks before checking its target | Probe what a loss's target says before running it (P2) |
| Compared against baselines that did not use their labels (SL-100 = SL-20) | Show the baseline's label scaling first (P6 rule 3) |
| One headline metric, confounded by operating point and saturation | Task metrics plus a calibration report (E1) |
| Joint-BN SSL arms, so the controls were not controls | Loss-off control is bit-identical to supervised (P13) |
| 3 seeds for effects under 0.05; inactive measured on ~3 cells | Seed count set by the minimum detectable effect; per-cell metrics and an extended test set |
| Several cross-machine comparisons | Within-machine only; calibration runs when crossing |
| Effort concentrated on SSL after the evidence pointed at measurement and supervision | Allocate by the effect-size budget (§2) |

## 7. Open inputs needed from the user

Listed in the chat message of 11 Oct.
