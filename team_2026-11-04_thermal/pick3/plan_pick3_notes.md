# Notes on the frozen pick 3 plan (disclosures; no rule change)

Owner: `ideas`. These notes leave the frozen plan untouched: `pick3/plan_pick3.md` v1.1, md5 6e9d9af2 (read-only; copy `plan_pick3_v1.1_FROZEN_6e9d9af2.md`). They come from `check`'s audit (`check/factcheck.md` §17, AU-1, AU-2, AU-4) and add disclosure only. No threshold, label or kill line changes.

## N1. Timing of the v1.1 freeze vs datascout's 12:55 log line (AU-2). Written 2026-11-04 12:58 IST.
- datascout's 12:55 lines in `log.md` (l.61-62) put real A1 dark I-V numbers on record about a minute before v1.1 was frozen. Per `check`, these were the deficit quintiles 2.6-19.3 mV, max 19.3 mV < 1 V_t, and a txt layout of 72 columns × 7 current rows. v1.1's §6 says "No data value has been read".
- **Read / not read by me:**
  - Before the v1.1 freeze I did **not** read those lines. My last reads of `log.md` before the freeze were the tails at 12:39-12:53, which showed only lines up to my own 12:53 line. At 12:54 and 12:56 I only appended to the log.
  - I first learned those numbers from `check`'s message at ~12:58, **after** the freeze. At 12:58 I located l.61 with a 60-character cut that showed only "A1 dark I-V folder verifi".
- So §6's statement held for me at freeze time. The numbers were on record in the shared log, and they are now known to me (after the freeze).

## N2. Self-test criteria in §6A are post hoc (AU-1)
- The amended self-test criteria in v1.1 §6A (corner error EL < 5% and IR < 10% of a cell side; inner residual EL < 1% and IR < 2%) were set **post hoc**, after the synthetic results were known (IR corner maximum 9.03%).
- The geometric reason (corners are extrapolated and unused; feature windows keep a 5% / 10% margin) is unchanged. The real-data T37 kill (inner residual > 5% of a cell side per module; pick kill if > 30% of modules are excluded) was set before any result and is unchanged.

## N3. T15 kill on the numbers now on record (AU-4)
- If no cell can have d ≥ 1 V_t, as datascout's module-level maximum of 19.3 mV < 25.7 mV implies (S, pending my own read), then the second "no spread" clause (< 1% of cells with d ≥ 1 V_t) is met automatically.
- The T15 "no spread" kill then rests on **robust SD of d < 0.1 V_t (2.6 mV) alone**. That line stays where v1 froze it.
- **DVt** (d ≥ 1 V_t) will then be 0 by construction. It is reported as frozen, not replaced.
- Format: 72 columns × 7 current rows (per `check`, from datascout's line). Format discovery will map this to per-cell voltage at the highest current under v1 §3.1, for example if the columns are 36 (current, voltage) pairs or 36 voltages plus 36 other values. Adapting the parser to the layout is not a rule change. If the layout does not give per-cell voltage at a current level, §6D's contingency applies before any statistic is computed.

## N4. EL-to-IR orientation (raised by datascout; written 2026-11-04 13:01 IST, after the T15 read, before any A1 image value is read). No rule change.
- A uniform grid is symmetric under rot180 and both mirrors, so registering EL and IR separately cannot tell which IR cell matches which EL cell (datascout). Plan v1.2 §2 maps each modality through the canonical grid with corners ordered TL, TR, BR, BL in image coordinates, with no flip. That is the **identity** orientation: it is the primary, as frozen.
- **Added, descriptive only, never used for a verdict:** T02 and T12 are also computed under fliph, flipv and rot180 (`cellreg.py` v0.2 `--orient`). If any of them gives a different verdict, the report says "orientation-sensitive". datascout's pick 1 uses the same primary (identity) with all 4 as robustness (its Amendment 1).
- Tool: `scripts/cellreg.py` v0.2. Its orientation self-test (IR mirrored left-right) recovers the cooled cell only under fliph: id → (1,5), fliph → (1,3) = truth, flipv → (2,5), rot180 → (2,3). The earlier geometry self-test numbers are unchanged.

## N5. A1 grid and IR file choice (format facts from datascout, written 2026-11-04 13:05 IST, before any A1 image value is read by me). No rule change.
- **Grid:** Shell M55 is **3 × 12** cells (datascout, from one EL preview), not the 4 × 9 I expected. Plan §1 said the layout is detected from the images, not assumed; cellreg runs with `--grid 3x12`.
- **Inner-cell robustness readout (§6A):** v1.1 wrote "rows 2-3 × columns 2-8 on 4 × 9 (14 cells)". Its definition is the cells off the outer ring. On 3 × 12 that is row 2 × columns 2-11, i.e. **10 cells per module** (26 of 36 cells are on the outer ring).
- **IR file:** plan §2 says to prefer the raw `*_3.39xA.txt` but to use `*_cropped.txt` if it is a module-only crop, decided at format discovery. datascout found that `<serial>_cropped.txt` (35 × 134; 35 × 138 for one module) is exactly the raw 240 × 320 IR window rotated 180° (max abs difference 0.000 at the best offset). So it is the authors' module-only crop, and **pick 3 uses the cropped txt**, per §2.
- **Orientation:** with the cropped txt, the frozen primary (identity, N4) equals "raw IR rotated 180°". That matches datascout's pick 1 primary (rot180 on the raw IR, its Amendment 3). The other three orientations stay descriptive (N4).
- **Resolution:** 134 px / 12 cells ≈ 11 IR px per cell side (S arithmetic), so the IR inner-80% window is ≈ 9 × 9 px per cell. `_cropped.jpg` is a matplotlib plot with a colour bar, not used.
- **Addendum to N5 (2026-11-04 13:06 IST, before any A1 image value is read):** the cropped IR is the module itself, with no background. For it, §2's "module quad" is the image boundary (`cellreg.py` v0.3 `--quad-ir full`); grid detection and refinement are as frozen. EL and UVF keep the Otsu quad. Synthetic module-only 3 × 12 crop at ~11 px per cell (self-test, scratchpad `selftest3/`): IR inner residual 0.34% of a cell; the planted cell is found as coolest IR and darkest EL.

## N6. Dark I-V cell numbering → EL grid (written 2026-11-04 13:08 IST, before any A1 image value is read; procedure needed to execute frozen §3.5 / §3.6; no threshold changes)
- **Gap:** the dark I-V files label cells `Cell1`..`Cell36`. The OSF page, wiki (none) and node description give no numbering or orientation convention (checked 4 Nov via the OSF API). T02 / T12 need each label on a grid cell.
- **Rule (fixed now):**
  - **Candidates:** 16 orderings of 1..36 onto the 3 × 12 EL grid (rows × columns in EL image orientation): start corner {TL, TR, BL, BR} × first direction {along the 12-cell rows, along the 3-cell columns} × path {raster, serpentine}.
  - **Criterion:** pooled Spearman ρ, over all registered cells of the 10 modules, between the dark I-V voltage P (highest current) and the cellreg EL cell median (`el_med`, NEF preview; rank-based, so the tone curve does not matter). Expected sign: positive (S).
  - **Choice:** the candidate with the largest ρ.
  - **Ambiguity:** if best minus second-best ρ < 0.05, T02 and T12 are reported under both, with "mapping-sensitive" if a verdict differs.
  - **Unresolved:** if the best ρ < 0.5, the mapping is not resolved and T02 is reported as **blocked**, with no fallback.
- **Bias disclosure:** choosing the mapping by EL-P agreement inflates AUROC(a) (EL alone) a little. That makes Δ harder to pass (conservative). IR is not used in the choice, so the IR-only AUROC (c) under the chosen mapping stays an independent test. The within-module deficit d and D90 are per cell and do not depend on the mapping except through which grid cell they land on.

## N7. Registration v2, post hoc (written 2026-11-04 13:16 IST, after the v1 T37 readout, before running v0.4 on real data; no T02 / T12 / R34 value computed). Rule for T37 v2; whether T02 / T12 use v2 is team-lead's decision.
- **Why:** the v1 T37 readout (cellreg v0.3, `pick3/out/t37_v03_summary.json`) passes the frozen numeric rule at the line (3/10 excluded). But visual QA found 6320427227's EL grid stretched past the module edge at a 4.49% residual (log 13:1x). The residual measures fit consistency, not true error.
- **Tool:** `scripts/cellreg.py` v0.4 (md5 04fac77a). Changes:
  - pitch is searched only in iteration 1, within 0.98-1.02 of the quad-implied cell, and offset within ±6%; later iterations use a fixed pitch with ±3% offset and ±10% local refinement;
  - the module-outline step closes gaps and inner bands (radius 3% of the short side) before taking the largest blob;
  - a new QA field `grid_vs_quad_max_pct_cell`.
- **Self-test:** PASS, now including an A1-like inner-band test (50% and 70% band depth: corner error 2.06% and 1.52% of a cell). Diagnosis caveat (S): v0.3 did not drift on the 50% synthetic band; at 70% it failed at the outline step instead. So "pitch drift" is the suspected cause, not shown, and v0.4 guards against both.
- **T37 v2 rule (fixed now, post hoc):** a module is excluded from T02 / T12 if any of:
  1. EL or IR inner residual RMS > 5% of a cell (the frozen rule);
  2. EL grid_vs_quad_max > 20% of a cell (a grid that does not fit the module outline; synthetic values are ~8.5%);
  3. **visual QA fails** (my judgement), with the overlay saved and a one-line reason per module written in `pick3/out/t37_v2_visual.tsv` **before** any T02 / T12 value is computed.

  The pick-level kill (> 30% of modules excluded) is as frozen. v2 is reported beside v1, labelled post hoc. UVF stays reported, not used.

## N8. Instrument and ordering route, frozen before any T02 / T12 / R34 value (written 2026-11-04 13:33 IST). Required by team-lead (13:2x messages) and `check` §21 / §25.

### N8.1 Tool status and disclosure
- **Frozen release:** `scripts/frozen/cellreg_91c3c81e.py` (read-only), cellreg v0.5. Self-test PASS: `pick3/out/cellreg_91c3c81e_selftest.json`.
- **Changes since `check` reviewed 04fac77a:**
  1. The module outline is computed on a ≤ 1000 px downsampled copy (the full-resolution closing was too slow).
  2. The script's built-in EL corner bar went from 3% to 5% of a cell, to match plan §6A (post hoc).
  3. `--grid-ir uniform`: a plain uniform grid inside the IR quad, for module-only crops.
  4. A modality whose grid is transposed against EL (portrait UVF, found by datascout) is rejected, not guessed. Its cells no longer leak into cells.tsv.
  5. Off-centre band tests (`check` V-2): band at 0.10-0.25 of a cell, depth 50% / 70%; corner error 2.17% / 1.55% of a cell.
  6. `el_p99` per cell.
  7. summary.json carries grid_vs_quad.
- I did not keep a copy of 04fac77a. The full diff from v0.3 (cb9ad392) is `pick3/out/cellreg_diff_v03cb9ad392_to_91c3c81e.diff`; items 1-7 are the changes since 04fac77a.
- **Wording fix (`check` V-1):** "pitch anchored, no drift" overstated the code. Pitch is searched within ±2% in iteration 1 only; later iterations refine locally against the previous fit, so scale can still move a little. The guards are visual QA and grid_vs_quad.
- **Disclosure:** before `check` reviewed it, I ran v0.4 (95e0ca3e) on the 10 real A1 modules (registration only; `pick3/out/reg_v04_id/`, `t37_v04_summary.json`). I viewed 2 EL overlays (6320427227, 6330431031) and all 10 IR overlays (10× montage). No T02 / T12 / R34 value was computed. From now on, both picks run only the frozen md5, and each run log records it.

### N8.2 T37 results so far (as they stand)
- **v1 (frozen, cellreg v0.3):** PASS by the numeric rule at the line (3/10 excluded). UVF fails as built (9/10 over 5%). Visual QA found 6320427227's EL misregistered at a 4.49% residual.
- **v2 (post hoc instrument fix, cellreg v0.4 95e0ca3e, rule N7):** **FAIL by its own rule.** EL grid_vs_quad is 23.9-35.4% and IR 44.6-81.7% on all 10 modules, over the 20% bar. Visually, the EL grids are right on the 2 checked, so the grid_vs_quad bar is miscalibrated on real images: the Otsu outline, not the grid, is off.

### N8.3 Proposed v3 (post hoc instrument fix #2; used only if team-lead chooses option B; T02 / T12 rules unchanged)
- **EL:** `cellreg_91c3c81e`, detect mode. Excluded if residual RMS > 5% of a cell (frozen) or visual QA fails. grid_vs_quad is reported, not used.
- **IR:** the authors' module crop with `--quad-ir full --grid-ir uniform --orient id`. Residual is undefined (no detected lines), so IR is judged by visual QA only.
  - B-2: in uniform mode grid_vs_quad = 0 by construction, so it is not used.
  - The detect-mode IR grid is run too, and its line positions are compared with the uniform grid's: max line offset in IR px per module, reported.
- **UVF:** reported only, never used.
- **Visual QA criteria (fixed now, before viewing any v0.5 overlay).** Per module and modality, FAIL if any of:
  1. The grid runs outside the visible module outline anywhere by more than 5% of a cell.
  2. EL: any grid line sits more than ~2% of a cell side off its visible inter-cell gap. Judged on 4× zooms of the 4 module corners and the centre.
  3. IR: any grid line sits more than ~1 IR px off a visible gap. Judged on 10× zooms of the whole crop; where no gap is visible, judged on the cell blobs, as a line through a blob.
  4. Any inner-90% (EL) or inner-80% (IR) cell window crosses a gap.
  5. The IR crop is not a module (e.g. 6330431480).
- **Procedure:** each call goes, with a one-line reason and the overlay path, into `pick3/out/t37_v3_visual.tsv` **before** any T02 / T12 / R34 value. `check` co-signs the calls blind to outcomes, which do not yet exist.
- **Pick-level rule:** as frozen, > 30% of modules excluded kills T02 / T12.

### N8.4 Cell ordering (team-lead route)
- **Documentation checked first (non-outcome evidence):**
  - OSF csr6t: 10 top-level folders, no README or cell map (API listing); the node description is silent; there is no wiki.
  - Colvin et al. 2023, full text (R: doi:10.1109/jphotov.2023.3238278): the per-cell RS and J01 values are "mapped onto the modules for visual representation" (Fig. 4d / e), but no numbering convention is given in the text.
  - So the ordering is **undocumented**.
- **Hence check's module-centred criterion:** over the 16 orderings of N6, the **mean of the 10 within-module Spearman ρ** between P (EL-derived voltage at the highest current) and the per-cell EL brightness **el_p99**. el_p99, not el_med, because the authors derive each cell's voltage from "a bright pixel from each cell" (R: same paper, §II.A). el_med is reported beside it.
- **Thresholds as N6:** best mean ρ < 0.5 → unresolved, T02 blocked. Best minus second < 0.05 → ambiguous, both reported, and a verdict that differs is "mapping-sensitive". EL modules excluded by v3 QA are left out of the criterion.
- **Bias (team-lead):** choosing the ordering by EL-label agreement inflates EL-only AUROC (a). That biases T02 against thermal, towards "no headroom". The **IR-only AUROC (c) under the same ordering is the independent readout**, reported with equal prominence.

### N8.5 Finding on the T15 label's direction (R; frozen label unchanged; read before any T02 value)
- Colvin 2023 (full text, §III.B): in A1, "Cells with bright spots in high injection EL show higher RS values because of high-resistance interconnection issues leading to current crowding". EL "dark regions ... show bright in PL", i.e. the EL darkening is resistive, not recombination. Each cell's voltage is computed from "a bright pixel from each cell".
- **So a degraded, high-RS cell may have a HIGHER EL-derived voltage at high injection,** and the frozen deficit direction (lower P = worse; plan §3.1, tagged S) may be inverted for this dataset (S, from R). The frozen D90 label stays as frozen, and T02 / T12 are reported under it.
- **Reading:** D90 is read as "cells with the dimmest brightest-pixel voltage relative to their module", not as "degraded".
- A reverse-direction label (the top 10% of P above the module median) would be a new, post hoc, descriptive analysis. It runs only if team-lead OKs it, and only beside the frozen readout.
- **Also noted (R, same paper):** IR was taken after "a bias of ISC was applied for 5 min", while the file names say 180 s (3 min). Hot IR regions mark current crowding near failing joints, not inactive area.

### N8.6 Descriptive extra for T12 (datascout / `check` §22)
- T12's flags are also read against **row- and column-centred ΔT**: ΔT minus the module's row and column medians. This is descriptive only, because datascout found the dark-IR ↔ EL-dark signal carried by row and edge structure: centred AUROC ≈ 0.50.
