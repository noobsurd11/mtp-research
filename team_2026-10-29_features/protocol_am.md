# Protocol AM: MIM reconstruction-error map as a crack-recall aid (val only) (v0.1)

runner, 29 Oct 2026. Status: **v0.1, APPROVED by coach** (29 Oct; one line added below). Direction #4 of `directions.md` §3.4. Inference only, on val; no test cell is touched by this protocol.

## Question
Does the reconstruction error of the MIM5 pretraining model (masked patches it cannot rebuild) point at val crack pixels that A5c (5%) and SUP100 (100%) miss?

## Fixed
- **Map model:** the full SparK state (encoder, densify, mask tokens, decoder) of `f1_mim_pre_s0` at its final step, `ckpt_latest.pth` (step 36,500 asserted), eval mode (BN running statistics).
- **Map:** per val cell, 8 random masks (ratio 0.6, 32 px patches, seed 1000 + cell index); per pixel the mean |reconstruction − per-patch-normalised target| over passes where it was masked; 0 if never masked (0.4^8 ≈ 0.07% of px).
- **Cells:** the 54 val cells, revised masks (gaint `el_f2/data/escdd_masks/val` = links to `labeled/masks_escdd`, pixel-identical to cv02).
- **Models whose misses are scored:** A5c-f1 s0-4 (gaint `el_f1`, final weights) and SUP100 = `p6_L3_100pct_s0..2` + `p16_A_100pct_s3..4` (gaint backup `cv02_noob_el`, final weights), argmax.
- **Code:** `el_f2` `scripts/am_map.py`, commit `9d37026`. A CPU smoke on the 560-step smoke encoder ran end to end (6 cells, meaningless numbers).

## Scores and rule (pre-stated)
1. Pixel AP of the map for val crack, vs the val crack base rate.
2. θ = the lowest map value (400 quantiles from the median up) whose relaxed precision (share of map > θ px within 2 px of GT crack) is ≥ 0.5 over val.
3. Per run: missed val crack components (8-connected, ≥ 20 px, relaxed recall@2 < 0.5 by its argmax) and the share recovered by the map (≥ 50% of the component's px within 2 px of map > θ). Mean per group.
- θ is chosen and scored on the same 54 val cells, so the recovered share is optimistic. That is acceptable for a kill screen; a pass means only "write the inference-rule protocol", never a claim.
- While this runs, no A5c-f1 (or any MIM5-family) test number is opened; the script reads val only.
- **Kill:** no θ reaches precision 0.5, or map AP ≤ 2x base rate, or the recovered share < 0.05 for both groups.
- **If it passes:** a separate protocol freezes an inference rule on val (z = standardised map; crack logit += β·z only where 0.001 ≤ p(crack) ≤ 0.5; β by val relF1@2), then one test opening, counted.

## Expectation (S)
Kill likely: per-patch-normalised 32 px targets make the error high on all multi grain (coach), and the map also fires on inactive, scuff, contamination.

## Compute
Minutes (CPU possible); on gaint after MIM pretraining and the A5c-f1 runs finish.
