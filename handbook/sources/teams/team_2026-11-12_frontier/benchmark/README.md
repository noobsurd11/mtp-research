# benchmark/ (benchdesign, 12 Nov 2026)

Local work only: CPU, ground-truth masks, images and list files. No server, no prediction or result file read.

| File | What | State |
|---|---|---|
| `PROTOCOL_DRAFT.md` | protocol draft v0 (8 sections) | accepted by the lead as the working base; v0.2 waits for scouts D41, D43, D44 |
| `splits/cv5v2.json`, `splits/legacy.json` | split definitions for the harness; format in `splits/README.md` | ready; cv5v2 has 0 module groups cut across folds by module id; 2 same-cell pairs under different module ids sit across folds (found 15 Nov, `splits/dup_crossfold_v1.tsv`; final tables score 528 cells) |
| `splits/forbidden_v1.txt`, `cv5v2_groups.tsv`, `cv5v2_vs_b6.tsv`, `pool532_manifest.tsv`, `cv5v2_check.txt` | sealed list, groups for the bootstrap, diff against B6, pool manifest, checks | ready (`SPLITS.md5`) |
| `cells.tsv` + `CELLS_README.md` | the 816-cell table (29 columns, flags) | ready (md5 a50521b4) |
| `LABELS_V11.md` + `out/masks_v11/` | label set v1.1 for the 582 legacy cells, change list, trainer notes | built; use is decision D3 (user) |
| `test_openings.md` | test ledger, back-filled (18 counted openings as of 14 Nov 2026; the uncounted era stated) | started |
| `T3B_PROPOSAL.md` | proposal for a few-shot layout track inside E1, with fold counts | for the user (decision D5) |
| `scripts/` | `corpus_build.py`, `groups_folds.py`, `label_checks.py`, `make_splits.py`, `make_masks_v11.py`, `make_cells_table.py`, `t3b_counts.py`, `fine_texture_check.py` | run in this order with `python -I` |
| `out/` | intermediate tables and summaries of the scripts | `out/cells.tsv` is an intermediate; the final table is `cells.tsv` here |

Checks the harness should run on gaint before use:
1. `md5sum -c splits/SPLITS.md5`; image md5s of `splits/pool532_manifest.tsv` against `labeled/images`.
2. `make_masks_v11.py --base-masks <labeled/masks_escdd>`: the rebuilt v1 must equal the real `masks_escdd` in all 582 cells.
