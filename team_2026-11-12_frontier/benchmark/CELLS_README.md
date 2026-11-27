# benchmark/cells.tsv: one row per real labelled cell (benchdesign, 12 Nov 2026)

816 rows, 29 tab-separated columns, md5 a50521b4 (`cells.md5`). Built by `scripts/make_cells_table.py` (50104bae) from the local dataset copies; no prediction or result file was read. Synthetic E-SCDD files are not listed.

| Column | Meaning |
|---|---|
| `stem` | file stem; the cell id used everywhere |
| `source` | ARTS, BMRK, CFVS, CSIR, SDLE (stem prefix) |
| `image_id` | module image the cell was cropped from (`CFVS_00031`); for BMRK / SDLE one id per cell |
| `position` | `rR_cC` in the module image; `-` for BMRK / SDLE |
| `module_group` | physical-module group: image ids of the same module at different times are merged; named after the smallest image id. 463 groups |
| `cell_id` | physical cell = `module_group` + position. 787 unique |
| `n_images_of_cell` | how many of the 816 images show this physical cell (1 to 6) |
| `cell_type` | from the spacing classes of the mask: `mono`, `multi`, `halfcut_multi`, `halfcut_mono`, `dogbone`, `no_spacing` (padded single-cell crops: no type in the mask) |
| `label_source` | `pratt` (BenchmarkEL releases) or `hanifi` (E-SCDD `_rf` cells) |
| `mask_version` | release whose mask the counts use: `escdd` (= `20221008` for crack and inactive), `20221008`, `20211104` |
| `role` | `train`, `val`, `test` (legacy split), `E1`, `ext_in_pool` (new in `20221008`, also in the unlabelled pool), `rf_in_pool`, `rf_not_pool` |
| `bench_set` | `cv5v2:f0` to `cv5v2:f4` (held-out fold), `test50`, `e1_106`, `aux_ext11`, `aux_rf117` |
| `rf_set` | for `_rf` cells: `F51`, `H36`, `F19` (judge's sets) or `excluded` |
| `e1_stratum` | for E1: `halfcut+scuff`, `halfcut`, `full+scuff`, `full` (scuff = at least 500 px of class 25) |
| `in_unlabelled_pool` | 1 if the image is also in the 11,938-cell unlabelled pool |
| `has_crack`, `has_inactive`, `has_scuff` | any pixel of class 14 / 11 / 25 in the release mask |
| `crack_px`, `inactive_px`, `scuff_px` | pixel counts in the release mask |
| `crack_comp20` | 8-connected crack components of at least 20 px |
| `inactive_area_pct` | inactive px as % of non-padding px |
| `crack_px_v1`, `inactive_px_v1` | legacy cells only: counts in label set v1 (= `masks_escdd`, rebuilt locally) |
| `crack_px_v11`, `ignore_px_v11` | legacy cells only: counts in label set v1.1 (`LABELS_V11.md`) |
| `noise_sigma` | robust pixel-noise sigma of the grey image, 1.4826 x median \|x - median5x5(x)\| (the P16 rule) |
| `flags` | `;`-separated, see below |

| Flag | Cells | Meaning |
|---|---|---|
| `noisy` | 5 | `noise_sigma` > 10: `CSIR_00070_r8_c4` (test), `CSIR_00070_r7_c2` (fold 0), `CSIR_00069_r7_c1` (fold 1), 2 `_rf` cells. No E1 cell |
| `twin_test_d6` | 7 | test cell that is the same physical cell as a train cell (`decision.md` D6) |
| `twin_train_d7` | 7 | train twins to drop from every unlabelled pool (D7) |
| `module_link_test` | 4 | test cell whose physical module has train or val cells under another image id, not a D6 twin |
| `twin_candidate_unchecked` | 2 | `CFVS_00063_r3_c1`, `ARTS_00030_r8_c6`: need a visual check |
| `dup_image` | 2 | pixel-identical images under two stems |
| `mask_copy_exact` / `mask_copy_near` | 4 / 8 | crack mask identical to (IoU >= 0.999), or nearly identical to (>= 0.85), the mask of another image of the same cell |
| `wrong_mask_v1` / `mask_donor` | 1 / 1 | `BMRK_00031_cell0091` carries the mask of `BMRK_00075_cell0255` in v1 |
| `scuff_or_star_v1` | 17 | legacy cell with E-SCDD scuff or star pixels (ignore in v1.1) |
| `scuff_or_star_as_crack_v1` | 9 | of those, cells where v1 labels some of these pixels crack |
| `rf_speck_crack_labels` | 36 | H36 half-cuts: crack labels not scoreable |
| `inactive_without_crack` | 3 | `_rf` cells; never happens in Pratt labels |
| `same_module_as_e1` | 7 | `_rf` cells of image id `CSIR_00300`: never train on them when E1 is a test set |
| `dropped_from_20221008` | 4 | legacy train cells absent from the later release |
| `not_in_escdd` | 6 | cells with no E-SCDD mask |

Counts to check a copy against: `bench_set` cv5v2 107 / 111 / 104 / 104 / 106, `test50` 50, `e1_106` 106, `aux_ext11` 11, `aux_rf117` 117; 491 image ids.
