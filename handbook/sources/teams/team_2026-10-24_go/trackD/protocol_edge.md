# Track D edge protocol v1: inactive-edge convention re-score (DX, 24 Oct 2026)

Direction 6 in `team_2026-10-24_why/SYNTHESIS.md` §2; `trackD/critic_defaults.md` §3. Inference only, existing checkpoints. **Post hoc** (written after every arm's standard numbers are known); every banded row is reported beside the standard row, never instead of it.

## Question
How much of the crack deficit sits on inactive edges, and does excluding that zone change any SSL − supervised verdict?

## Hypothesis (from SYNTHESIS, falsifiable)
Banding raises every arm's crack IoU by +0.01 to +0.03; every SSL − sup gap stays within its rule-1 threshold of its standard value. **Kill:** a gap changes sign (banded Δ past its threshold with the opposite sign to the standard Δ).

## Band (fixed)
- Band = GT inactive (class 11) dilated by 2 px, Euclidean (EDT of non-inactive ≤ 2).
- Banded crack scoring: GT crack and predicted crack inside the band are ignored: gt' = gt & ~band, pred' = pred & ~band; then the usual counts (IoU, P, R; relaxed P/R/F1 at 2 px on gt', pred').
- Inactive is scored as standard (unchanged).
- Labels as labelled (critic default 0.1). The audit is not used.

## Runs (final step 20,000; teacher for MT runs; test 50 cells, revised masks; τ 0 and τ 1)
| Arm | Runs | n |
|---|---|---|
| A5c | `p12_A_5pct_s0..2`, `p13_A_5pct_s3..4` | 5 |
| BsM5 (P13) | `p13_BsM_5pct_s0..4` | 5 |
| CsM5 | `p13_CsM_5pct_s0..4` | 5 |
| BsD5 (P17) | `p17_BsD_5pct_s0..4` | 5 |
| AL1 arms (D7 pool) | `al1_{A5,BsM5,AL5,ALd5,ALdh5,CPS5,CPSm5}_s0..4` | 35 |
| L3 10% | `p6_L3_10pct_s0..2` | 3 |
| A50 | `p16_A_50pct_s0..4` | 5 |
| A100 | `p6_L3_100pct_s0..2`, `p16_A_100pct_s3..4` | 5 |
Total 68 checkpoints, ~15 min on one GPU.

## Contrasts (rule 1, `scripts/ssl_rules.py` arithmetic, seeds as listed)
Primary metric crack IoU; also crack relF1@2 and crack recall. Each contrast standard and banded side by side.
1. BsM5 − A5c
2. CsM5 − A5c
3. BsD5 − A5c
4. (BsM5+LA) − (A5c+LA)
5. al1 BsM5 − al1 A5 (D7 pool)
6. al1 AL5 − al1 A5
Descriptive: A10 − A5c, A100 − A5c (labels vs SSL), the other AL1 arms, per-arm banded − standard (paired by checkpoint).

## Reporting
- Four cell sets (all 50 / no noisy cell / no 7 twins / neither) and per source (ARTS, BMRK, CFVS, CSIR).
- Share of test GT crack px inside the band (expect ~12-15%), and recall inside vs outside the band per arm.
- Verdict line per contrast: standard verdict, banded verdict, sign flip yes/no.

## Checks
- Standard τ 0 rows reproduce `results/sk1/la_sa_test.json` (P-series runs) and `results/al1/raw/*.json` (AL1) crack IoU, inactive IoU, relF1@2 to |diff| < 1e-4; τ 1 matches `la_sa_test.json` where present.
- Per-cell sums equal pooled values; step = 20,000 for every run.

## Compute and files
- cv02 GPU 6 (Track D slot while free; else one of 0-3), tmux `=dxedge`, booked in the ledger.
- Code: `~/mtp/research/scripts_cv02/trackD_edge_rescore.py` (md5 in `REVISION`), uses `el_sk1` code `0ea71df` read-only.
- Output `edge.json` (per run, τ, per cell) to `results/trackD_edge/`, relayed to gaint `cv02_noob_el/el_trackD` with MD5.
- Analysis `trackD/edge_results.md`; C recomputes the six contrasts from `edge.json`.
