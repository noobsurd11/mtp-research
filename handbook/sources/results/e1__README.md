# E1: task-aligned, per-cell evaluation (definitions fixed 11 Oct 2026, ~14:00 IST, before any E1 number)

**Why:** pooled pixel IoU and AP are dominated by a few cells (inactive: top 3 test cells hold 59% of pixels, P6). They also depend on the operating point and on saturation (P6, P8). The use case needs per-cell quantities.

## Evaluation cells
- **test:** the 50 BenchmarkEL test cells, scored against the E-SCDD revised masks.
- **ext:** 106 cells of BenchmarkEL release `20221008`:
  - not among our 582 cells, and not in the external unlabelled pool (11 of the release's 117 extra cells were in that pool and are dropped);
  - 101 CSIR, 5 BMRK; 32 contain crack and 10 contain inactive;
  - masks are the release's own (cleaned, like E-SCDD);
  - classes 24–28 do not exist in our 24-class taxonomy and are remapped (24 → 2, 25–28 → 0). Crack and inactive are untouched;
  - `ext117_manifest.csv` lists them.
- Models never saw either set. Val is not used: it informed P6's base choice.

## Per-cell metrics (prediction = argmax, final weights; teacher for Mean Teacher runs)
| Metric | Definition | Over which cells |
|---|---|---|
| crack tolF1@2 | 2PR/(P+R): P = share of predicted crack px within 2 px of GT crack, R = share of GT crack px within 2 px of predicted crack; 0 if nothing predicted | cells with GT crack ≥ 20 px; mean |
| crack length error | \|L_pred − L_gt\| / L_gt, with L the pixel count of the skeleton (skimage `skeletonize`) | same cells; median |
| crack false alarm | share of cells with predicted crack ≥ 50 px | cells with GT crack < 20 px |
| inactive area error | \|a_pred − a_gt\| in percentage points; a = inactive px / non-padding px of the cell | all cells; mean |
| inactive detection F1 | positive if a ≥ 0.5% (GT and prediction separately) | all cells |
| inactive cell IoU | per-cell IoU | cells with GT inactive ≥ 0.5%; mean |

**Reporting:**
- Arms are averaged over seeds.
- Contrasts get a paired image bootstrap (2,000 resamples) and leave-top-3-out.
- The 95% CI half-width of each per-cell metric is compared with that of the pooled IoU on the same cells. That answers "does it measure more stably?".
- E1 is descriptive. It enters P13–P15 only as labelled secondary metrics.

Files: `scripts_cv02/e1_task_metrics.py` (per-cell scoring, cv02), `raw/<run>.json`, `scripts_cv02/e1_aggregate.py`.

## Amendment (11 Oct, ~14:15 IST, after the first-pass extension numbers had been seen)

**What was wrong:**
- Release `20221008` labels four defect types our taxonomy lacks: 25 scuff, 26 corrosion cell, 27 brightening, 28 star. They appear in 95 of the 117 extension cells.
- The first pass remapped them to background. A crack prediction on a "star" defect therefore counted as a false alarm, which confounds the extension's crack metrics.

**Fix:** those pixels are marked ignore (`ext117/ignore/`) and scored neither way for crack or inactive.
- They are also excluded from the cell area.
- Predictions that fall on them are recorded separately (`crack_pred_on_ignored`, `inact_pred_on_ignored`).
- Class 24 (sp mono halfcut, 4 cells) stays remapped to sp mono.

**Why it is disclosed:** the fix was prompted by the first-pass extension numbers. All arms are scored the same way, and the first pass is kept in `raw/`.

**Other observations about the extension:**
- It comes from 67 modules, of which only 1 has cells among our 582.
- It looks visibly different from our cells (`ext_montage.png`: rows 1–2 are extension cells, row 3 our CSIR test cells).
- So it measures transfer to unseen modules, not in-distribution performance.

The scored output is `raw_v2/`; test-set numbers are identical to the first pass.

## Results (11 Oct; P6–P12 checkpoints, 73 + 33 runs)
Tables: `e1_tables_p6_p10.md`, `e1_ext_v2.md`, `e1_p11.md`, `e1_p12.md`. E1's pooled test IoU equals each run's re-score exactly, and its leave-top-3-out equals `per_image_analysis.py`.

**Does a per-cell metric measure more stably?** Count of paired contrasts whose 95% CI excludes 0, and the median |Δ| / CI half-width, over the 23 contrasts scored on both sets (11 on "both"). The contrasts were picked for the protocols, not at random, so this is descriptive.

| Metric | test: CI excl. 0 | test: median \|Δ\|/hw | ext: CI excl. 0 | ext: median \|Δ\|/hw |
|---|---|---|---|---|
| crack IoU (pooled) | **13** | 0.93 | 4 | 0.57 |
| crack relF1@2 (pooled) | 11 | 0.86 | 6 | 0.62 |
| crack tolF1@2 (per cell) | 8 | 0.83 | 6 | 0.59 |
| crack length error | 6 | 0.63 | 8 | 0.67 |
| crack false alarm | 0 | – | **16** | 1.43 |
| inactive IoU (pooled) | 7 | 0.85 | 10 | 0.68 |
| inactive cell IoU | **9** | 0.80 | **17** | 1.45 |
| inactive area error | 1 | 0.41 | 11 | 0.86 |
| inactive detection F1 | 0 | 0.40 | 7 | 0.86 |

**Reading:**
- **Crack:** the per-cell metrics are not more sensitive than pooled IoU or relF1@2 on the test set. The criterion in `to_human/proposal_reframe_2026-10-11.md` (E1) is not met for crack; pooled IoU and relF1@2 stay primary.
- **Inactive:** per-cell IoU separates more contrasts than pooled IoU (test 9 vs 7; ext 17 vs 10; both 8 vs 2). It is less dominated by the few large cells.
- **Crack false alarm** is uninformative on the test set (almost no arm fires on a crack-free test cell) but is the most sensitive crack metric on the extension.
- **The extension is a different regime.** Every model loses most of its crack performance there (L3 100%: crack IoU 0.471 → 0.152, tolF1 0.80 → 0.41). It measures transfer to unseen modules.
- **A pattern across P11 and P12 (descriptive):** tolerant pseudo-labels raise crack false alarms on unseen modules by about 0.10 of crack-free cells, and improve inactive there.
