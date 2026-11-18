# cv5v3 balance (scripts/bench_make_cv5v3.py; held-out cells per fold; crack / inactive from the v1.1 training masks)

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
| 0 | 104 | 59 | 48 | 12 | 56251 | 57585 | 35 | 10 | 33 | 22 | 4 | 2 | 45 | 46 | 11 |
| 1 | 124 | 66 | 48 | 8 | 60972 | 57565 | 45 | 10 | 41 | 24 | 4 | 1 | 55 | 55 | 13 |
| 2 | 102 | 56 | 43 | 7 | 56738 | 57142 | 36 | 10 | 31 | 22 | 3 | 0 | 36 | 54 | 12 |
| 3 | 98 | 57 | 47 | 14 | 92831 | 56334 | 30 | 10 | 32 | 23 | 3 | 0 | 51 | 35 | 12 |
| 4 | 104 | 61 | 43 | 7 | 40754 | 56394 | 36 | 10 | 32 | 23 | 3 | 0 | 54 | 39 | 11 |

## Side by side (cv5v2 / cv5v3)

| fold | cells | groups | crack cells | inactive cells | crack px | inactive px | src ARTS | src BMRK | src CFVS | src CSIR | src SDLE | type dogbone | type mono | type multi | type no_spacing |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 107 / 104 | 66 / 59 | 51 / 48 | 10 / 12 | 49311 / 56251 | 56753 / 57585 | 36 / 35 | 10 / 10 | 34 / 33 | 23 / 22 | 4 / 4 | 2 / 2 | 47 / 45 | 47 / 46 | 11 / 11 |
| 1 | 111 / 124 | 67 / 66 | 44 / 48 | 8 / 8 | 60467 / 60972 | 57565 / 57565 | 39 / 45 | 10 / 10 | 36 / 41 | 22 / 24 | 4 / 4 | 1 / 1 | 49 / 55 | 48 / 55 | 13 / 13 |
| 2 | 104 / 102 | 63 / 56 | 46 / 43 | 7 / 7 | 57196 / 56738 | 57142 / 57142 | 37 / 36 | 10 / 10 | 31 / 31 | 23 / 22 | 3 / 3 | 0 / 0 | 36 / 36 | 56 / 54 | 12 / 12 |
| 3 | 104 / 98 | 67 / 57 | 46 / 47 | 15 / 14 | 99932 / 92831 | 56785 / 56334 | 34 / 30 | 10 / 10 | 34 / 32 | 23 / 23 | 3 / 3 | 0 / 0 | 53 / 51 | 39 / 35 | 12 / 12 |
| 4 | 106 / 104 | 67 / 61 | 42 / 43 | 8 / 7 | 40640 / 40754 | 56775 / 56394 | 36 / 36 | 10 / 10 | 34 / 32 | 23 / 23 | 3 / 3 | 0 / 0 | 56 / 54 | 39 / 39 | 11 / 11 |
| spread | 7 / 26 | 4 / 10 | 9 / 5 | 8 / 7 | 59292 / 52077 | 812 / 1251 | 5 / 15 | 0 / 0 | 5 / 10 | 1 / 2 | 1 / 1 | 2 / 2 | 20 / 19 | 17 / 20 | 2 / 2 |

## Classes with held-out px and 0 training px

- cv5v2: belt_mark (19) fold 0 (21935 px); rings (12) fold 2 (1204 px); clamp (8) fold 3 (1238 px)
- cv5v3: belt_mark (19) fold 0 (21935 px); clamp (8) fold 1 (1238 px); rings (12) fold 2 (1204 px)

## Cells for the cv5v2 against cv5v3 comparison

compare_set: clean_unmoved = not on score_exclude_v2c and same fold in both splits (all clean cells keep their fold); affected_unmoved = on score_exclude_v2c, same fold (its module-mates in other folds left its training set); affected_moved = on score_exclude_v2c, fold changed. Relation = closest training cell of the same module in cv5v2 (SPLIT_INTEGRITY 4a; open_pair = the 8 cells of the 4 open pairs).

| compare_set | relation | cells | crack cells | inactive cells |
|---|---|---|---|---|
| affected_moved | neighbour_crop | 18 | 7 | 2 |
| affected_moved | no_shared_area | 11 | 4 | 0 |
| affected_moved | open_pair | 4 | 2 | 0 |
| affected_moved | same_cell | 2 | 1 | 0 |
| affected_unmoved | neighbour_crop | 20 | 7 | 0 |
| affected_unmoved | no_shared_area | 38 | 15 | 6 |
| affected_unmoved | open_pair | 4 | 0 | 0 |
| affected_unmoved | same_cell | 2 | 1 | 0 |
| clean_unmoved | - | 433 | 192 | 40 |

