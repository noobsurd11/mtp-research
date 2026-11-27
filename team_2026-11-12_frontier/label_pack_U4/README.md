# Labelling pack U4: 24 half-cut cells (about 2 to 3 hours)

> **Lead's note, 15 Nov 2026: do the short version first (about 20 minutes).** I checked the 24 cells. They are half-cut cells, but this pool has no scuff streaks of the E1 kind, and the models draw almost no cracks on them. Of the 213 numbered marks, 194 are cyan line-filter marks that sit mostly on crystal texture; only 19 marks (5 red, 14 yellow) come from the models. A full pass would be about two hours of writing "D".
> **Short version:** open `results_short.csv`. For each cell answer two questions (any crack in the cell? any scuff or handling mark?) and judge only the red and yellow marks (A crack, D not a crack, S scuff, ?). If you see a crack that has no red or yellow mark, write the grid squares in `grid_squares` on the "Any crack" row. Ignore the cyan marks.
> What this buys: a checked set of half-cut cells to count false alarms on, and the few real cracks if any exist. The long version below (`results.csv`) stays available and is only worth it if the short pass finds real cracks in many cells.

**What this is.** 24 half-cut solar cells from the unlabelled pool. They come from 7 CSIR modules that are in neither the unseen-module test set (E1) nor the old test set, and none of them is a copy or near-copy of any labelled or test image. Our models were never trained on these modules. Your marks give us the first real half-cut cells with usable crack labels, so we can check models on half-cut cells before the single final E1 opening.

**Rule: development reads only.** These labels are never used to train a model, never used to tune a training run, and never put into any training split. (Your decision of 15 Nov.)

## What you see in each picture (folder `cells/`, one PNG per cell, `01_...png` to `24_...png`)
- Left: the cell as it is. Right: the same cell with numbered marks and a grid.
- **Red** = most of our 20 baseline models (PF) draw a crack here.
- **Orange dots** next to a red mark = the crack may continue here (the models are less sure).
- **Yellow** = some of the models (between 1 in 5 and 1 in 2) draw a crack here, or their average crack score is at least 5%.
- **Cyan** = a dark thin slanted line found by a line filter; no model drew it.
- In all there are 213 numbered marks (about 9 per cell): 5 red, 14 yellow, 194 cyan. Our models see almost no cracks in these cells (the same failure as on the unseen modules), so most marks come from the line filter and many will be crystal texture: those are a quick **D**. The red mark 1 in cell 01 shows what a model-drawn mark with an orange extension looks like.
- Grid: columns **A to H** (left to right), rows **1 to 8** (top to bottom).

## What to do for each number (file `results.csv`, column `decision`)
| Write | Meaning |
|---|---|
| **A** | It is a crack, and the mark is about right. |
| **X** | It is a crack, and it also runs along the orange dots (only for marks with `has_dotted_extension = yes`). |
| **D** | Not a crack (texture, dark spot, grid line, nothing). |
| **S** | A scuff streak or handling mark, not a crack. |
| **?** | Cannot tell. |

- A crack that is longer than drawn and has no dots: write **A** and in `note` where it ends, for example `longer, to E5`.
- **Missed cracks:** each cell has three rows `miss1`, `miss2`, `miss3`. For a crack with no mark, write **M** in `decision` and the grid squares it runs through in `grid_squares`, for example `C4 D4 D5`. Leave the rows empty if there is none.
- A dark inactive area (a whole region gone dark) is welcome too: use a `miss` row, write **M**, the squares, and `inactive` in `note`.
- Busbars, fingers, cell edges and the cut gap are never cracks; you do not need to mark them.
- No drawing is needed. The CSV opens in any spreadsheet program; keep the file name and the columns.

When you are done, save `results.csv` in this folder and tell the lead. We turn your decisions into masks from the stored marks.

## How the 24 cells were chosen (folder `selection/`)
- From 943 pool half-cells (after removing every cell that could be a copy of a labelled or test image), a picture-only rule: a half-cut check (the cell grid repeats about every 163 px down and 342 px across) and a score for long, straight, slanted dark lines. The 24 highest scores were taken, at most 4 per module.
- Honest note: we did not find clear long scuff streaks of the E1 kind in this pool (these 7 modules are a different family from E1's half-cut modules). The score mostly picks cells with the longest slanted dark lines, which can be scuff, cracks or just the multi-crystal texture. Your **S** marks will tell us how much real scuff is there.
- `sheet_selected_24.png` shows the chosen cells with what the line score found (magenta); `sheet_next_24_not_selected.png` the next 24; `sheet_score0_12.png` cells where nothing was found; `sheet_halfcut_fail_12.png` the 12 cells the half-cut check missed (they are half-cuts at a different scale).
