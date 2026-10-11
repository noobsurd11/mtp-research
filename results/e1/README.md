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
