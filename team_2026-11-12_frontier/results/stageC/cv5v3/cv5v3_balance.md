# cv5v3 balance (scripts/bench_make_cv5v3.py; held-out cells per fold; crack / inactive from the v1.1 training masks)

VARIANT: L6 added: SDLE pool cells whose stem names the same module (SDLE_<n>_<module>-...) are one group
VARIANT: R3 amended: equal balance cost -> the tied fold with fewer cells after the placement, then the lowest fold
VARIANT: C4 narrowed: pass condition on crack-cell and inactive-cell spreads (not worse by more than 2) and on no source or cell type held out but absent from training; other spreads reported as [C4-info]

## cv5v2

| fold | cells | groups | crack cells | inactive cells | crack px | inactive px | src ARTS | src BMRK | src CFVS | src CSIR | src SDLE | type dogbone | type mono | type multi | type no_spacing |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 107 | 66 | 51 | 10 | 49311 | 56753 | 36 | 10 | 34 | 23 | 4 | 2 | 47 | 47 | 11 |
| 1 | 111 | 67 | 44 | 8 | 60467 | 57565 | 39 | 10 | 36 | 22 | 4 | 1 | 49 | 48 | 13 |
| 2 | 104 | 63 | 46 | 7 | 57196 | 57142 | 37 | 10 | 31 | 23 | 3 | 0 | 36 | 56 | 12 |
| 3 | 104 | 67 | 46 | 15 | 99932 | 56785 | 34 | 10 | 34 | 23 | 3 | 0 | 53 | 39 | 12 |
| 4 | 106 | 67 | 42 | 8 | 40640 | 56775 | 36 | 10 | 34 | 23 | 3 | 0 | 56 | 39 | 11 |

## cv5v3

| fold | cells | groups | crack cells | inactive cells | crack px | inactive px | src ARTS | src BMRK | src CFVS | src CSIR | src SDLE | type dogbone | type mono | type multi | type no_spacing |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 107 | 56 | 47 | 12 | 56054 | 57585 | 35 | 10 | 33 | 22 | 7 | 2 | 45 | 46 | 14 |
| 1 | 110 | 59 | 47 | 8 | 60764 | 57565 | 37 | 10 | 39 | 24 | 0 | 1 | 53 | 47 | 9 |
| 2 | 103 | 55 | 43 | 7 | 56738 | 57142 | 38 | 10 | 31 | 22 | 2 | 0 | 36 | 56 | 11 |
| 3 | 101 | 55 | 47 | 14 | 92831 | 56334 | 36 | 10 | 32 | 23 | 0 | 0 | 51 | 41 | 9 |
| 4 | 111 | 60 | 45 | 7 | 41159 | 56394 | 36 | 10 | 34 | 23 | 8 | 0 | 56 | 39 | 16 |

## Side by side (cv5v2 / cv5v3)

| fold | cells | groups | crack cells | inactive cells | crack px | inactive px | src ARTS | src BMRK | src CFVS | src CSIR | src SDLE | type dogbone | type mono | type multi | type no_spacing |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 107 / 107 | 66 / 56 | 51 / 47 | 10 / 12 | 49311 / 56054 | 56753 / 57585 | 36 / 35 | 10 / 10 | 34 / 33 | 23 / 22 | 4 / 7 | 2 / 2 | 47 / 45 | 47 / 46 | 11 / 14 |
| 1 | 111 / 110 | 67 / 59 | 44 / 47 | 8 / 8 | 60467 / 60764 | 57565 / 57565 | 39 / 37 | 10 / 10 | 36 / 39 | 22 / 24 | 4 / 0 | 1 / 1 | 49 / 53 | 48 / 47 | 13 / 9 |
| 2 | 104 / 103 | 63 / 55 | 46 / 43 | 7 / 7 | 57196 / 56738 | 57142 / 57142 | 37 / 38 | 10 / 10 | 31 / 31 | 23 / 22 | 3 / 2 | 0 / 0 | 36 / 36 | 56 / 56 | 12 / 11 |
| 3 | 104 / 101 | 67 / 55 | 46 / 47 | 15 / 14 | 99932 / 92831 | 56785 / 56334 | 34 / 36 | 10 / 10 | 34 / 32 | 23 / 23 | 3 / 0 | 0 / 0 | 53 / 51 | 39 / 41 | 12 / 9 |
| 4 | 106 / 111 | 67 / 60 | 42 / 45 | 8 / 7 | 40640 / 41159 | 56775 / 56394 | 36 / 36 | 10 / 10 | 34 / 34 | 23 / 23 | 3 / 8 | 0 / 0 | 56 / 56 | 39 / 39 | 11 / 16 |
| spread | 7 / 10 | 4 / 5 | 9 / 4 | 8 / 7 | 59292 / 51672 | 812 / 1251 | 5 / 3 | 0 / 0 | 5 / 8 | 1 / 2 | 1 / 8 | 2 / 2 | 20 / 20 | 17 / 17 | 2 / 7 |

## Classes with held-out px and 0 training px

- cv5v2: belt_mark (19) fold 0 (21935 px); rings (12) fold 2 (1204 px); clamp (8) fold 3 (1238 px)
- cv5v3: belt_mark (19) fold 0 (21935 px); rings (12) fold 2 (1204 px); clamp (8) fold 3 (1238 px)

## Cells for the cv5v2 against cv5v3 comparison

compare_set: clean_unmoved = not on score_exclude_v2c and same fold in both splits (all clean cells keep their fold); affected_unmoved = on score_exclude_v2c, same fold (its module-mates in other folds left its training set); affected_moved = on score_exclude_v2c, fold changed. Relation = closest training cell of the same module in cv5v2 (SPLIT_INTEGRITY 4a; open_pair = the 8 cells of the 4 open pairs). With L6, the SDLE cells of modules that spanned cv5v2 folds count as affected (relation sdle_module).

| compare_set | relation | cells | crack cells | inactive cells |
|---|---|---|---|---|
| affected_moved | neighbour_crop | 18 | 7 | 2 |
| affected_moved | no_shared_area | 11 | 4 | 0 |
| affected_moved | open_pair | 4 | 2 | 0 |
| affected_moved | same_cell | 2 | 1 | 0 |
| affected_moved | sdle_module | 12 | 2 | 0 |
| affected_unmoved | neighbour_crop | 20 | 7 | 0 |
| affected_unmoved | no_shared_area | 38 | 15 | 6 |
| affected_unmoved | open_pair | 4 | 0 | 0 |
| affected_unmoved | same_cell | 2 | 1 | 0 |
| affected_unmoved | sdle_module | 5 | 0 | 0 |
| clean_unmoved | - | 416 | 190 | 40 |

