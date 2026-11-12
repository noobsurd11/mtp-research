# Visual QA criteria for G0 v2 (cellreg v0.4 runs), written before any v0.4 run or overlay is seen

Owner: datascout; co-sign: check (blind to per-module G0 values). Applies to every A1 and A2 module, EL and IR overlay (IR viewed upscaled about 6-10×).
A modality **fails** if any of these is seen:
1. Any inner grid line lies more than about 10% of a cell side off the visible cell gap it should sit on (EL: dark gap between cells; IR: the cooler gap / cell-block boundary).
2. The grid runs past the module edge (beyond the outermost cell edge) by more than about 10% of a cell, or stops short of it by more than that.
3. Any cell window visibly crosses a cell gap (part of two cells in one window).
4. The grid has the wrong count or wrong orientation of rows / columns against the visible cells.
A module is **kept** only if EL and IR both pass and the residual rule (RMS ≤ 5% of a cell side, per modality) passes.
Calls are recorded in `visual_qa_v04.tsv` (module, el_call, ir_call, criterion number if fail, note) before any G0 v2 number is computed, then sent to check with the overlay paths; G0 v2 runs only after check co-signs or flags each module. Flagged modules: excluded unless check and I agree on a pass.
Note: these criteria are tighter than Amendment 4's "about a quarter cell" overrun (now 10%); they replace it for v2 as check suggested.

## Addendum (check §26 asks; written before any v0.4 run)
5. **Numeric edge check (pre-stated):** for each module, modality and side (top, bottom, left, right), the edge offset = signed distance between the registered grid edge (from `grid_corners`) and the module outline edge (`quad`, Otsu), in cell sides, averaged over the side's two corners. Per set (A1, A2) and modality, take the median offset per side over all modules. A modality **fails** if any side's offset differs from that set median by more than 0.25 cell. Computed by `../../scripts/edge_check.py` from reg.json only (no feature values), before G0 v2.
6. **Overlays for QA:** drawn by `../../scripts/qa_overlay.py`: the image is upscaled (IR × 8 nearest, EL to about 1,800 px wide) and the full grid (outer + inner lines) is drawn with 1 px lines from the homography defined by the four `grid_corners` (cellreg maps a uniform canonical grid by one homography, so the corners fix every line).
7. **Borderline list and sensitivity:** modules called borderline by me or by check (within about 0.25-0.4 cell of failing, or a disagreement) are named in the table before G0 v2 is computed. G0 v2 is reported on the co-signed keep set (primary), and again with the borderline modules removed (sensitivity only, no verdict).
v0.2 co-sign outcome (check §26, for the record; the v0.2 interim stays "not co-signed" and does not count): agreed on my 4 extra fails and all residual exclusions; check fails A1 6320427793 IR (top grid line ~0.6 cell inside the top row, which I missed); borderline: A1 6330431484 IR, A2 408330104 EL, A2 408332881 EL.
