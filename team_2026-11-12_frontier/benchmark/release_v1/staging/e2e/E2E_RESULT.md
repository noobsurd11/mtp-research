# End-to-end check of the staged scorer (bench_release, 22 Nov 2026)

E = measured here. CPU only (CUDA_VISIBLE_DEVICES empty), project venv Python, staged code `files/code`, staged lists `files/lists`.
Set: cv5v3_f0 (107 open pool cells, held-out fold 0 of the staged `cv5v3.json`). Ground truth: the existing v1.1 build
(`benchmark/out/masks_v11`: masks + ignore). No sealed set was read or dumped.

1. The held-out list written from the staged `cv5v3.json` passes `bench/sets.py`'s pinned held-out md5 (79816ba6): the
   sanitized JSON keeps the fold lists byte-identical (E).
2. `bench_score.py records` on both runs: 107 cells, ties 0 (E).
3. `bench_score.py summary --groups lists/cv5v3_groups.tsv --group-col group --boot 200` (E), subset `all`:

| Run | strict crack IoU | relF1@2 | inactive IoU | mIoU-R13 |
|---|---|---|---|---|
| oracle (pred = v1.1 strict mask) | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| oracle shifted 1 px right | 0.3696 | 0.9992 | 0.9285 | 0.8292 |

4. Note for the README (E): `summary --groups` needs `--group-col group` with the staged group files (the default
   column name is `phys_group`).

5. The protocol read as README section 5.5 states it (E): oracle dumps for all 5 cv5v3 folds, two arms (BASE = oracle,
   SHF = oracle shifted 1 px), seed 5 each; `bench_read_w1.py --labels set --groups lists/cv5v3_groups.tsv
   --score-exclude lists/score_exclude_v3.txt --boot 200 --workers 4`: rc 0 in 47 s; 532 OOF stems; score-exclude
   532 -> 416 stems; read.txt, read_x416.txt and read.json written; cells.tsv subsets resolve (crackfree n = 303, the
   protocol's count). OP-A, all 532 cells: BASE 1.0000 on every headline metric; SHF strict crack IoU 0.4492, relF1@2
   0.9990, inactive IoU 0.8809, mIoU-R13 0.8320, width ratio 1.0005. A/A skipped (one seed), as the tool states.

Dumps, records and reads were deleted after the check (script kept: `make_oracle_dumps.py`).
