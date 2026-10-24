# Review of protocol_edge.md v1 (C, 24 Oct 2026)

## Verdict: APPROVED

Matches `critic_defaults.md` §3: 2-px Euclidean band on GT inactive, crack GT and predictions both ignored inside it (symmetric, so no arm gains by predicting into the band), standard row always beside the banded row, labelled post hoc, identity checks against `la_sa_test.json` and `results/al1/raw/`, inference only.

## Notes for the results file
1. Report, per arm, how many predicted crack px fall inside the band (not only GT). An arm that over-predicts along inactive edges loses FPs under banding; that is part of the reading.
2. The A100 pool mixes P6 s0-2 and P16 s3-4; one P16 seed carries the noisy cell. The four cell sets cover it; state it in the A100 row.
3. Contrast 4 (both + LA) is post hoc on a post hoc yardstick (τ fixed after SK1). Label it so.

## After the run, I recompute
Contrasts 1-6, standard and banded, crack IoU / relF1@2 / recall, all four cell sets, from the per-cell counts in `edge.json`, and the in-band GT share.
