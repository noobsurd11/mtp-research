# Qualitative panels (descriptive, 13 Oct 2026)

`fig_qualitative_5pct.png`: predictions on 4 test cells against the revised labels (crack red, inactive blue), with per-cell IoU under each panel.

**How the cells and seed were fixed (before any prediction was looked at):**
- the 2 test cells with the most inactive GT px (`BMRK_00073_cell0253` 21,382 px; `CFVS_00114_r6_c5` 19,305 px);
- the 2 with the most crack GT px (`CFVS_00018_r4_c4` 10,915 px; `CFVS_00027_r4_c4` 10,211 px);
- seed 3 for every arm, the first seed that A5c, CsM5, BsM5 and A100 share in cv02 `el_p13`.

GT counts come from `results/p13/per_image.json`.

**Models:** `p13_A_5pct_s3` (supervised 5%), `p13_CsM_5pct_s3`, `p13_BsM_5pct_s3` (EMA teacher), `p16_A_100pct_s3` (supervised 100%). Final weights, argmax, as in the re-score. Panels are cropped to the cell (padding, class 7, removed); no model predicts crack or inactive in the padding.

**What the panels show (one seed, four cells; not evidence on their own):**
- `CFVS_00114_r6_c5`: inactive IoU 0.28 (A5c), 0.62 (CsM5), 0.69 (BsM5), 0.60 (100%). One cell like this carries much of the pooled inactive gain (doc 13 A2).
- `BMRK_00073_cell0253`, the largest inactive test cell: every model misses most of its labelled inactive area, including supervised 100% (0.05). The label covers wide bands at both edges.
- Crack cells: all 5% models trace the dense crack networks similarly (IoU 0.37–0.53); supervised 100% is clearly better (0.58–0.67).

Files: `preds_p13_s3.npz` (images, revised masks, predictions); scripts `scripts_cv02/pred_dump.py` (cv02, read-only inference) and `scripts/qualitative_panel.py`.
