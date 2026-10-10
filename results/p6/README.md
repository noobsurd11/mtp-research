# P6: corrected supervised baseline ladder (Experiment 1). Results

Protocol: `protocols/P6_corrected_baseline.md`, locked before any run (db76a8c).

**Runs**
- 21 runs on cv02 (8× RTX A6000), 10 Oct 2026, 11:46–15:32 IST. Every run has rc = 0.
- Code: commit `824fab0` (`REVISION` in the run dir).
- Weights: final step, 20,000 for every run.
- Scoring: `scripts/rescore_label_versions.py`, read-only, on test (50 images) and val (54 images).

**Files**
- `raw/`: re-score JSONs and `launch.log`.
- `p6_summary.{md,json,png}`: `scripts/aggregate_runs.py`.
- `p6_rules.txt`: `scripts/p6_rules.py`, the locked rules applied.
- `hist_revised.npz` and `hist_analysis.txt`: the exploratory score-histogram diagnostic (below).

## Results
Test, revised (E-SCDD) labels, mean ± sd over seeds 0–2. Val AP is in the last two columns.

| Arm | crack AP | inactive AP | crack IoU | inactive IoU | crack relF1@2 | crack relP@2 | val crack AP | val inactive AP |
|---|---|---|---|---|---|---|---|---|
| L0 10% (old recipe) | 0.553±0.015 | 0.621±0.003 | 0.319±0.051 | 0.439±0.015 | 0.746±0.078 | 0.690±0.126 | 0.466±0.006 | 0.494±0.054 |
| L1 10% (+label-safe aug) | 0.574±0.006 | **0.649±0.017** | 0.368±0.004 | **0.473±0.014** | 0.806±0.004 | 0.803±0.015 | 0.478±0.002 | 0.349±0.159 |
| L2 10% (+ImageNet resnet34) | 0.519±0.003 | 0.477±0.018 | 0.392±0.003 | 0.383±0.024 | 0.806±0.003 | 0.838±0.009 | 0.394±0.003 | 0.397±0.025 |
| L3 10% (+CE+Dice) | 0.400±0.004 | 0.302±0.018 | 0.396±0.003 | 0.294±0.019 | 0.814±0.003 | 0.910±0.006 | 0.288±0.011 | 0.303±0.050 |
| L3 20% | 0.433±0.004 | 0.335±0.042 | 0.398±0.002 | 0.347±0.043 | 0.822±0.008 | 0.939±0.006 | 0.309±0.003 | 0.462±0.019 |
| L0 100% | 0.545±0.003 | 0.612±0.006 | 0.337±0.004 | 0.391±0.008 | 0.782±0.008 | 0.744±0.010 | 0.484±0.006 | 0.597±0.026 |
| L3 100% | **0.593±0.003** | 0.420±0.018 | **0.471±0.001** | 0.429±0.011 | **0.876±0.003** | 0.939±0.003 | 0.511±0.004 | 0.413±0.020 |

Old-label (20211104) columns are in `p6_summary.md`.

## Locked decision rules (confirmatory)
**Rule 1: ladder steps on test AP.** A step counts if Δ > 0.01 and Δ > 2·SE.

| Step | crack AP | inactive AP | Verdict |
|---|---|---|---|
| L0→L1, label-safe augmentation | +0.020 | +0.028 | **Helps both** |
| L1→L2, ImageNet encoder | −0.054 | −0.172 | **Hurts both** |
| L2→L3, CE+Dice | −0.119 | −0.174 | **Hurts both** |

- Labels, L0 10% → 100%: no detectable effect (−0.009 / −0.009).
- Labels, L3 10% → 100%: helps (+0.193 / +0.117).
- Secondary, at the argmax operating point:
  - L1→L2 raises crack IoU (+0.024) but lowers inactive IoU (−0.089).
  - L2→L3 has no detectable effect on crack IoU and lowers inactive IoU (−0.089).

**Rule 2: base for Experiment 2 = L0 10%.** Val mean of (crack AP + inactive AP)/2:

| Arm | Val score |
|---|---|
| L0 | **0.480** |
| L1 | 0.414 (seed 2 collapsed on val inactive: 0.324) |
| L2 | 0.396 |
| L3 | 0.296 |

P7 therefore runs on L0's model and loss (`unetpp`, weighted CE) with P7's fixed label-safe views.

**Rule 3: headroom, computed literally as AP on the pooled val+test pixels (histograms summed).**
- L0 @100% = 0.5591 and L0 @10% = 0.5601, so the headroom is **−0.001 < 0.02**.
- Under the locked rules, **Experiment 2 (P7) is underpowered on BenchmarkEL and is reported as a pilot** (P7 rule 4).
- Correction: an interim figure of +0.026 averaged the per-split APs. That is not "pooled". Val has 12k inactive GT pixels against test's 92k, so the split mean over-weights val. The pooled number above is the rule's answer.

## Exploratory (not covered by the locked rules)
**1. AP is not comparable across these loss and encoder changes.**
- The ImageNet and Dice arms push many GT pixels to softmax < 0.001 (bin 0 of 1000). There they are tied with ≥ 98.5% of the background, so AP cannot rank them.
- Test, mean over seeds, `hist_analysis.txt`:

| Arm | GT crack px < 0.001 | GT inactive px < 0.001 |
|---|---|---|
| L0 10% | 3% | 19% |
| L1 10% | 5% | 19% |
| L2 10% | 19% | 41% |
| L3 10% | 42% | 65% |
| L3 100% | 20% | 40% |

- Rule 1's "hurts" for L2 and L3 is therefore partly a ranking (calibration) effect. At the argmax operating point:
  - crack IoU rises L1→L2 and is flat L2→L3;
  - crack relaxed precision@2 rises 0.80 → 0.84 → 0.91.
- The inactive drop is real at every operating point: IoU 0.473 → 0.383 → 0.294.

**2. The label-efficiency gap depends on the recipe.**

| Recipe, 10% → 100% labels | pooled AP | crack IoU | inactive IoU |
|---|---|---|---|
| L0 | −0.001 | +0.017 (not detectable) | −0.048 |
| L3 | **+0.159** | +0.075 | +0.135 |

- L0 does not convert extra labels into better test scores at all. L3 does.
- SSL can only close a gap that exists, so L3 is the base where Experiment 2 has room. That motivates P8.

**3. Inactive class: the best inactive IoU at any label budget is L1 at 10% (0.473).**
- It beats L3 at 100% (0.429).
- L0's inactive IoU falls with more labels (0.439 → 0.391).
- Unexplained. Candidates:
  - label noise in inactive masks: few large blobs, and test inactive is dominated by few images;
  - Dice/encoder effects on large dark regions.
- Do not interpret before a per-image check.

**4. Inactive pixels sit in a few cells.** Revised labels; computed from `data/escdd_masks/{test,val}`.

| Split | Cells with any inactive | Share held by the top 3 | Largest single cell |
|---|---|---|---|
| test | 16 of 50 | 59% | BMRK_00073_cell0253, 23% |
| val | 6 of 54 | 89% | CFVS_00143_r4_c3, 35% |

- For comparison, crack appears in 48 of 50 test cells, and the largest single cell holds 12%.
- Any dataset-level inactive metric (AP or IoU) is therefore decided by about 3 cells. That plausibly explains:
  - the large inactive sds (L1 val inactive AP 0.349 ± 0.159);
  - the "inactive puzzle" in point 3.
- `fig_overlays.png`, row 3: the top test cell has two large dark side strips labelled inactive, which every model largely misses.

## Figures
- `fig_ladder.png`: AP vs IoU along the ladder at 10% labels.
- `fig_label_scaling.png`: L0 vs L3 at 10/20/100% labels.
- `fig_saturation.png`: CDF of GT-pixel scores.
- `fig_overlays.png`: 3 test cells chosen by a fixed rule (top-2 crack area, top-1 inactive area), seed 0. Made by `scripts_gaint/overlay_figure.py`, read-only inference on cv02.

## Caveats
- One split (seed 0); 3 training seeds; BenchmarkEL 20211104 images with E-SCDD revised masks.
- 50 test images. The inactive class is dominated by few images.
- AP uses 1000 uniform bins, the same as all earlier work.
- The bin-0 tie effect is a property of the metric on these models, not a bug: the histogram-based AP reproduces the rescore JSON exactly (max abs diff 0).
