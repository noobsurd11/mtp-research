# benchmark/ (benchdesign, 12 Nov 2026)

Local work only: CPU, ground-truth masks, images and list files. No server, no prediction or result file read.

| File | What | State |
|---|---|---|
| `PROTOCOL_DRAFT.md` | protocol draft v0 (8 sections) | accepted by the lead as the working base; v0.2 waits for scouts D41, D43, D44 |
| `splits/cv5v2.json`, `splits/legacy.json` | split definitions for the harness; format in `splits/README.md` | ready; cv5v2 has 0 module groups cut across folds by module id; 2 same-cell pairs under different module ids sit across folds (found 15 Nov, `splits/dup_crossfold_v1.tsv`); the 528-cell rule is superseded: final tables score all 532 cells and the 416 clean cells of `splits/score_exclude_v3.txt` (PROTOCOL_v1.0 3.1; updated 23 Nov) |
| `splits/forbidden_v1.txt`, `cv5v2_groups.tsv`, `cv5v2_vs_b6.tsv`, `pool532_manifest.tsv`, `cv5v2_check.txt` | sealed list, groups for the bootstrap, diff against B6, pool manifest, checks | ready (`SPLITS.md5`) |
| `splits/cv5v3.json`, `cv5v3_groups.tsv`, `score_exclude_v3.txt`, `pool_t9_v2.txt` | the split of record since 16 Nov (cv5v3: 285 groups, none spans folds; cv5v2 holds the 2-seed screens only), its groups, the clean-cell list (116 excluded, 416 left), the unlabelled pool list (4,949 cells) | ready (`splits/cv5v3.md5`; score_exclude_v3 6d48dfbd, pool_t9_v2 39877ede); PROTOCOL_v1.0 3.1, 6.5 (row added 23 Nov) |
| `cells.tsv` + `CELLS_README.md` | the 816-cell table (29 columns, flags) | ready (md5 a50521b4) |
| `LABELS_V11.md` + `out/masks_v11/` | label set v1.1 for the 582 legacy cells, change list, trainer notes | built; use is decision D3 (user) |
| `test_openings.md` | test ledger, back-filled (19 counted openings to 21 Nov 2026, the last a public table only, no further opening; the uncounted era stated; updated 23 Nov) | started |
| `T3B_PROPOSAL.md` | proposal for a few-shot layout track inside E1, with fold counts | for the user (decision D5) |
| `scripts/` | `corpus_build.py`, `groups_folds.py`, `label_checks.py`, `make_splits.py`, `make_masks_v11.py`, `make_cells_table.py`, `t3b_counts.py`, `fine_texture_check.py` | run in this order with `python -I` |
| `out/` | intermediate tables and summaries of the scripts | `out/cells.tsv` is an intermediate; the final table is `cells.tsv` here |

Checks the harness should run on gaint before use:
1. `md5sum -c splits/SPLITS.md5`; image md5s of `splits/pool532_manifest.tsv` against `labeled/images`.
2. `make_masks_v11.py --base-masks <labeled/masks_escdd>`: the rebuilt v1 must equal the real `masks_escdd` in all 582 cells.
