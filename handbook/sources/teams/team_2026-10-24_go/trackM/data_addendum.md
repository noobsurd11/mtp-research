# Track M data addendum: which extra labelled cells are leakage-free

MC (Track M critic), 24 Oct 2026. Extends `team_2026-10-21/data/decision.md` (D1 to D7 stay in force). CPU only.
Scripts and outputs: `trackM/mc_data/` (`leak.py`, `base.py`, `cand.csv`, `escdd_extra_train_eligible.tsv`). Images: local `~/mtp/datasets/escdd_full` (HF snt-ubix/escdd @ 8c8cba9a), our `dataset_20211104` split.

## Verdict
1. **107 E-SCDD real cells may be added to training** (list: `mc_data/escdd_extra_train_eligible.tsv`). No image-level evidence ties any of them to a test or val cell.
2. **Everything else in E-SCDD stays out of training:** E-SCDD's own split assignment (39 of our 50 test cells are in its train), the 93 synthetic images, E1's 106 cells, the 17 `_rf` cells outside our pool, and 4 cells that share a module or cell position with a test or val cell.
3. **Expected value is small and source-mismatched** (reading): the 107 are 104 CSIR + 3 ARTS. They add about 12% crack px and 14% inactive px to our train set, almost all in CSIR, the source we already score best on. The data lever C measured (ARTS and BMRK still rising at 50 to 100%) is not what E-SCDD offers.

## 1. The candidate pool (E)
E-SCDD real cells not among our 582: 233.

| Group | Cells | Crack cells / px | Inactive cells / px | Sources | Decision |
|---|---|---|---|---|---|
| `_rf`, in our external pool | 100 | 46 / 24,610 | 10 / 39,509 | 97 CSIR, 3 ARTS | eligible (minus 4, §3) |
| `20221008` cells in our pool (not in E1's 106) | 11 | 3 / 2,940 | 0 | CSIR | eligible |
| `_rf`, not in our pool | 17 | 6 / 229 | 0 | CSIR | **out**: reserved for D5 option A (secondary test) |
| E1 extension | 105 (106 incl. `CSIR_00308_r5_c3`, absent from E-SCDD) | 32 / 32,294 | 10 / 9,158 | 100 CSIR, 5 BMRK | **out** while E1 is the unseen-module secondary |
| synthetic `^\d+-.+_rf$` | 93 | | | | **out** (D2) |

Eligible after §3: **107 cells, 48 with crack (27,016 px), 10 with inactive (39,509 px).** For scale, our 478 train cells hold 232,914 crack and 272,630 inactive px (old masks, order of magnitude only).

## 2. Twin screen against our 50 test and 54 val cells (E)
Method: 128-px grey, high-pass (image minus Gaussian sigma 3), z-scored, correlation with every test/val cell of the same source. Calibrated on our own split with the same code: the 7 known test twins score 0.934 to 0.998 against their train twins; non-twin best matches score medians of 0.86 (ARTS), 0.89 (CSIR), 0.91 (CFVS), 0.93 (BMRK; smooth images inflate r, as agent 4 found).

| Candidate source | Highest r against any test/val cell | Same-source non-twin median (test vs train) |
|---|---|---|
| CSIR | 0.797 (`CSIR_00046_r4_c5_rf` vs test `CSIR_00166_r2_c4`) | 0.894 |
| BMRK (E1 only, not eligible anyway) | 0.928 | 0.934 |
| ARTS | below 0.6 | 0.86 |

No candidate reaches the non-twin median of its source, let alone the twin range. Reading: no physical-cell twin of a test or val cell among the 233. Limit: a twin at a much later degradation stage could correlate lower; the CSIR set has no time-series structure like CFVS.

## 3. Module and position siblings (E), excluded by caution
Our split already shares modules between train and test (24 of 50 test cells), so a module sibling is not a new kind of leak. These 4 eligible cells are excluded anyway, because two of them touch the noisy cell's module or position, and the cost is 534 crack px:

| Cell | Shares with | Crack px |
|---|---|---|
| `CSIR_00042_r1_c1_rf` | position r1_c1 with val `CSIR_00046_r1_c1` | 0 |
| `CSIR_00070_r6_c2_rf` | module of the noisy test cell `CSIR_00070_r8_c4` | 0 |
| `CSIR_00074_r8_c4_rf` | position r8_c4 with the noisy test cell (r = 0.664) | 0 |
| `CSIR_00127_r7_c5_rf` | module of test `CSIR_00127_r11_c5` | 534 |

Four more sibling hits (`CSIR_00046_r4_c5_rf`, `CSIR_00046_r6_c1_rf`, `CSIR_00051_r11_c5_rf`, `CSIR_00339_r4_c6`) are in groups that are out anyway (17 non-pool `_rf`, E1). If D5 option A is built, these are module siblings of test/val cells and should be flagged there. `cand.csv` lists every hit.

## 4. Label quality (E, handbook 17 §5.5)
- 2 eligible cells have heavily fragmented crack masks: `CSIR_00087_r10_c5_rf` (982 px in 380 components) and `CSIR_00087_r4_c4_rf` (457 px in 128). The 3 ARTS cells are 1-px lines.
- Rule (fixed now, before any run): **keep all 107 as released.** No label cleaning or filtering is chosen after seeing scores. A cleaned variant would be its own rung.

## 5. Rules for any rung that adds these cells
1. One change: "train set + 107". Same steps, same recipe, same seeds as the comparator; no other change in the rung.
2. Labels: E-SCDD masks mapped to our 24-class scheme exactly as P6 built `masks_escdd` (class 29 `sp multi halfcut` → 1 `sp multi`; 25 to 28 handled as in P6). MD must state the mapping and show class histograms before and after.
3. Steps are matched, not epochs: with 585 cells instead of 478, each cell is seen about 18% less often. State this.
4. External pool (SSL rungs only): the 107 may stay in the unlabelled pool; that is not test leakage. D7 twin removal still applies.
5. Score as always on our 50 test cells with masks_escdd, with the "without twins", "without noisy cell" and per-source lines. Report CSIR separately: that is where any gain should land.
6. E1: unaffected (its 106 cells stay out). Option A secondary test (50 + 106 + 17): unaffected.
7. Never use E-SCDD's test or train assignment, and never score on E-SCDD's test.
