# Label set v1.1 for the 582 legacy cells (benchdesign, 12 Nov 2026)

Status: built locally and ready; **using it was decision D3, with the user: decided, the user approved v1.1 for all new runs on 12 Nov 2026 (20:15).** Nothing in any existing mask folder was touched.
Script: `scripts/make_masks_v11.py` (4467261c). Output: `out/masks_v11/` (8.4 MB). Tags: E = measured here; S = judgement.

## 1. Definition
- **v1** = the project's `masks_escdd`: the E-SCDD mask (577 cells) with classes >= 24 set back to the `20211104` label, and the `20211104` mask for the 5 cells missing from E-SCDD. The script rebuilds v1 from the public files; the rebuild gives the handbook's counts (crack cells 209 / 23 / 48, inactive 42 / 6 / 16, test crack px 92,074).
- **v1.1** = v1 with:
  - **E1:** every pixel that E-SCDD labels scuff (25) or star (28) becomes **ignore (255)**. No other class >= 24 occurs in the 582 cells (asserted).
  - **E2:** `BMRK_00031_cell0091` gets its `20220723` mask (identical to its `20211104` mask). Its `20221008` / E-SCDD mask is, pixel for pixel, the mask of `BMRK_00075_cell0255`.
  - **E3:** no mask change; noise flags live in `cells.tsv`.

## 2. What changes (E, `out/masks_v11/SUMMARY.txt`, `CHANGES.tsv`)
| Split | Cells | Cells changed | Px to ignore (scuff / star) | of which v1 crack / material / background / other | Crack cells v1 to v1.1 | Crack px v1 to v1.1 |
|---|---|---|---|---|---|---|
| train | 478 | 16 | 3,484 (3,246 / 238) | 703 / 1,390 / 1,383 / 8 | 209 to 206 | 271,805 to 269,608 |
| val | 54 | 0 | 0 | 0 | 23 to 23 | 37,938 (same) |
| test | 50 | 2 | 236 (236 / 0) | 236 / 0 / 0 / 0 | 48 to 46 | 92,074 to 91,838 |

- Inactive is untouched in every split (42 / 6 / 16 cells; 272,743 / 12,277 / 92,125 px).
- **E2:** `BMRK_00031_cell0091` (train, cv5v2 fold 4): 10,556 px of its mask change over all classes; crack 1,560 px to 66 px.
- Cells that lose all crack: `ARTS_00051_r6_c2`, `CSIR_00117_r8_c4`, `CSIR_00176_r5_c2` (train); `ARTS_00047_r3_c1`, `ARTS_00051_r3_c2` (test).
- Cells with ignore px per cv5v2 held-out fold: 3 / 3 / 0 / 5 / 4. Per-cell list: `CHANGES.tsv` (40 rows) and `cells.tsv`.
- On v1.1 the test set equals E-SCDD's own masks for crack (46 crack cells, 91,838 px).

## 3. Files in `out/masks_v11/`
| Path | Content |
|---|---|
| `masks/<stem>.png` | v1.1, uint8, values 0 to 23 and 255 |
| `masks_strict/<stem>.png` | v1.1 with the ignore pixels carrying their v1 label; values 0 to 23 only. Differs from v1 in one cell (`BMRK_00031_cell0091`) |
| `ignore/<stem>.png` | 255 where v1.1 is ignore, else 0 (same use as `ext117/ignore`) |
| `CHANGES.tsv` (da2315bb) | stem, split, edit, class from, class to, px |
| `MANIFEST.tsv` (f88907f2) | per stem: pixel md5 of v1 (rebuilt), v1.1, v1.1 strict; ignore px |
| `SUMMARY.txt` | the counts above |

Pixel md5 = md5 of the raw uint8 512 x 512 array, so it does not depend on the PNG encoder.

## 4. What the house trainer needs for an ignore value (E, `harness/src_snap/el_f3`)
| Part | Behaviour | Line |
|---|---|---|
| Train dataset | accepts 255 only with `data.mask_ignore_value=255` (opt-in, not in `base.yaml`); supervised runs only, the option raises for SSL methods | `scripts/train.py` l.437 to 443 |
| Val and test datasets | built **without** `ignore_value`: a 255 in a val or test mask raises `ValueError` in `load_index_mask` | `scripts/train.py` l.463 to 464; `src/data/benchmark_el.py` l.53 to 58 |
| Losses | `ce_dice` and `weighted_ce` use `ignore_index` 255 for CE and Dice; the thin-crack wrapper is tested with ignore pixels | `src/losses/ce_dice.py` l.27 to 49 |
| In-run metrics | `ignore_index` 255 is excluded from every count | `src/evaluation/metrics.py` l.170, l.223 |
| Class counts | `count_class_pixels` skips the ignore value | `src/data/class_stats.py` l.13 to 20 |

Consequences (S):
1. In a CV root the held-out fold is both `val.txt` and `test.txt`, and folds 0, 1, 3, 4 hold cells with ignore pixels, so `mask_subdir` cannot point at `masks/` as it is. Two ways, both prepared:
   - **No code change:** a per-root mask folder of links, train stems to `masks/`, held-out stems to `masks_strict/`, plus `data.mask_ignore_value=255`. The trainer's own val numbers then count the 3,484 px by their v1 label; they are not used for any verdict.
   - **Two-line change in `el_bench`:** pass the ignore value to the val and test datasets. Cleaner; needs the usual flag-off identity check.
2. The frozen scorer should take `masks/` + `ignore/` as ground truth for v1.1, as it does for E1.
3. Semi-supervised baselines cannot use `data.mask_ignore_value`; they can train on `masks_strict/` (they keep the 703 scuff-or-star crack px, and get the `BMRK_00031` fix).
4. Albumentations must keep masks on nearest-neighbour resampling for any method that resizes (255 must not blend). Not checked for the synthetic half-cut and copy-paste transforms.

## 5. Check to run on gaint before use (harness)
`make_masks_v11.py --base-masks <labeled/masks_escdd>` asserts that the rebuilt v1 equals the real `masks_escdd` pixel for pixel in all 582 cells, and stops before writing anything if not. Until that passes, v1.1 is "built from a local rebuild that matches every published count", not "verified against the training masks".

## 6. Recommendation for D3 (S)
Use v1.1 for all new CV5-G training and scoring. Score the legacy test on both v1 (continuity with every past number) and v1.1. Reasons: the three edits are mechanical; v1 teaches "scuff streak = crack" on 649 px in 6 train cells, the failure seen on E1; v1 trains one BMRK cell on another cell's mask. Cost: a fresh baseline on v1.1, which CV5-G needs anyway. Risk: none of the edits has a measured effect on scores (the scuff-as-class arm was n.d.; `H20` §6.0).
