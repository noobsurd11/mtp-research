# benchmark/splits: split definitions (benchdesign, 12 Nov 2026)

Built by `benchmark/scripts/make_splits.py` (md5 cfd61997). Check with `md5sum -c SPLITS.md5` in this folder.

## Format `el_bench_split/1` (one JSON file per split definition)
| Key | Meaning |
|---|---|
| `format`, `format_notes` | format id and the rules below, repeated inside the file |
| `name`, `version`, `description` | `cv5v2` version 2; `legacy` version 1 |
| `pool` | the 532 cells (legacy `train.txt` then `val.txt`), `stems_md5`, and the manifest file + md5 |
| `forbidden` | file name, count and md5 of the sealed-stem list |
| `folds` | list of `{id, n_train, n_heldout, train_md5, heldout_md5, train, heldout}` |
| `sealed_sets` | `legacy.json` only: `test50` stems, with the `noisy` and `twins_d6` subsets |
| `parent` | `cv5v2.json` only: the frozen B6 fold file md5 and the 4 moved cells |
| `groups` | `cv5v2.json` only: the group file, its md5 and the grouping rule |

- **Order rule:** every stem list is in pool order: legacy `train.txt` order, then legacy `val.txt` order (the B6 rule).
- **List md5 rule:** md5 of `'\n'.join(stems) + '\n'`, so it equals `md5sum` of the split file a root writes. Check: it reproduces the md5 of the legacy `train.txt` / `val.txt` / `test.txt` (842f27c4 / 9dcccf00 / a31fad14), and folds 0 and 4 of `cv5v2` have the same train / held-out md5s as the B6 roots 0 and 4 (96d3154c / 7e107038 and c57b0b94 / 40cda7ef), which are unchanged folds.
- **Roots:** for fold `fK`, `splits/train.txt` = `train`, `splits/val.txt` = `splits/test.txt` = `heldout`. For `legacy`, `train.txt` = 478, `val.txt` = `test.txt` = the 54 val cells (the `s2c_root` pattern); the real `test50` list is used only by the scorer at a registered opening.

## Files
| File | md5 | Content |
|---|---|---|
| `cv5v2.json` | 441d118f | module-grouped 5-fold CV over the 532 cells. Held-out sizes 107 / 111 / 104 / 104 / 106 |
| `legacy.json` | 9bacb290 | the 478 / 54 / 50 split, the sealed `test50` list, and the 7 train twins to drop from unlabelled pools (D7) |
| `forbidden_v1.txt` | 9bb4d919 | 167 stems: legacy test 50 + ext117 117. Byte copy of `b6_forbidden.txt` |
| `cv5v2_groups.tsv` | e44f0668 | stem, legacy split, physical-module group, fold. 330 groups. Use these groups for the group bootstrap |
| `cv5v2_vs_b6.tsv` | 7f4bcba8 | the diff against the frozen B6 folds: 4 rows |
| `pool532_manifest.tsv` | d352f509 | stem, legacy split, md5 of the image file (BenchmarkEL repo clone), md5 of the grey pixels |
| `cv5v2_check.txt` | 4cf472d0 | the group check and the fold tables before and after |

## cv5v2 against the frozen B6 folds (`b6_folds.tsv` e2cafce1)
| Stem | Group | B6 fold | cv5v2 fold |
|---|---|---|---|
| `ARTS_00081_r5_c1` | `ARTS_00020` | 3 | 1 |
| `ARTS_00081_r9_c6` | `ARTS_00020` | 3 | 1 |
| `CFVS_00033_r1_c4` | `CFVS_00032` | 2 | 1 |
| `CFVS_00033_r5_c3` | `CFVS_00032` | 2 | 1 |

- Groups cut across folds: B6 folds 2 (`ARTS_00020`, `CFVS_00032`); cv5v2 **0** (E `cv5v2_check.txt`). Forbidden stems in the pool: 0. Added 15 Nov: the check works on module ids; two physical cells appear under two module ids each and sit in two folds (`dup_crossfold_v1.tsv`: ARTS_00165 / ARTS_00166 r12_c5, CFVS_00076 / CFVS_00082 r1_c1). The split is not changed; final tables exclude these 4 cells from scoring.
- Folds 0 and 4 are byte-identical to B6. Inactive px per fold is unchanged (the 4 cells have none). Crack cells per fold: 52 / 46 / 46 / 46 / 42.
- Three classes still have held-out pixels and no training pixels in one fold each: belt mark (fold 0), rings (fold 2), clamp (fold 3), as in B6.
- Not grouped, by decision: ARTS clean edge cells that look alike (94 same-position pairs with high-pass correlation >= 0.90 sit in different folds; B6 disclosed the same), BMRK and SDLE (no module ids), and 5 CSIR same-position pairs with correlation 0.92 to 0.96 and no shared defect (`CSIR_00059` / `00201` r6_c1, `CSIR_00059` / `00176` r5_c2, `CSIR_00221` / `00222` / `00231` r6_c2). A fine-texture check did not separate same cells from look-alikes (`out/fine_texture_summary.txt`), so these stay candidates for a visual check.
- gaint side, to do by the harness: confirm `pool532_manifest.tsv` image md5s against `labeled/images`, and note that B6's `DATA_MANIFEST.md5` (2630f630) covers the same 532 stems.
