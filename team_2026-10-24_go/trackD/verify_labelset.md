# Labelled-set experiment: independent recompute by C (24 Oct 2026, 20:15 IST)

**Verdict: CONFIRMED.** Every number in `labelset_results.md` §2 matches my recompute. **Direction 4 gate: NOT opened** (decision below).

## Checks
- My script (scratchpad `labelset_chk.py`, written before the results file existed) reads `results/trackD_labelset/d1_score.json` per-cell `crack_std` counts. It recomputes, per run and per arm:
  - crack IoU, relF1@2, recall and relP@2;
  - draw-means over 3 seeds;
  - the draw-level rule max(0.01, 2·sqrt(var_A/3 + var_B/3)) over the 3 draw-means;
  - the seed-level 9 v 9 rule;
  - the four cell sets and per source.
- 80 entries at step 20,000 (27 d1 runs × τ 0/1, plus the reference runs). `completion.txt`: 27 runs, each with one header and one final TEST line, re-score ok.
- **Draw-means, all 50, crack IoU:** R 0.327 / 0.316 / 0.330; Tc 0.337 / 0.330 / 0.345; Ts 0.359 / 0.333 / 0.365. These match §1.

| Contrast (all 50) | crack IoU | relF1@2 | recall | Verdict |
|---|---|---|---|---|
| **P2: Tc − R** | +0.0127 (0.0118) B | +0.0301 (0.0106) B | +0.0166 (0.0223) n.d. | **BETTER** |
| **P1: Ts − Tc** | +0.0151 (0.0212) n.d. | +0.0073 (0.0231) n.d. | +0.0255 (0.0275) n.d. | **n.d.** |
| Ts − R (secondary) | +0.0278 (0.0210) B | +0.0374 (0.0210) B | +0.0421 (0.0295) B | BETTER |

- **The other cell sets** match §2:
  - Tc − R is BETTER through relF1@2 in all four sets. Its crack IoU pass in all 50 is marginal: +0.0127 against 0.0118, and n.d. at seed level.
  - Ts − Tc is BETTER only without twins (and in "neither"), on recall alone: +0.036 against 0.033.
  - Ts − R is BETTER in all four sets.
- **Per source:** matches §3. BMRK recall: R 0.242, Tc 0.265, Ts 0.312. ARTS: R 0.279, Tc 0.235, Ts 0.272.
- **Crack-px confound** (my own fit on the 9 draw-means against added crack px from `draws/audit.json`): r = 0.82, slope +0.018 per 10k px, matching §5. New from the residuals, mean per arm after the px fit: R −0.001, Tc −0.005, Ts +0.006.
  - Reading: crack-pixel volume accounts for the whole Tc − R gap.
  - Ts keeps about +0.011 over Tc beyond volume.
  - Nine points, descriptive only.

## Direction 4 gate (critic_defaults §1): NOT opened
The rule: "Ts − Tc BETTER, or Tc − R BETTER with BMRK recall ≥ +0.05".
- Ts − Tc is n.d. on the full test set. Its only pass is one metric in the no-twins rows, 0.003 above the threshold.
- Tc − R is BETTER, but BMRK recall moves only +0.023.
- No-twins rows are co-equal (review addendum 2). Co-equal sets that disagree give a mixed verdict, not a pass.
- Draw-level crack px explains most of the spread.

So "coverage of weak sources matters beyond crack count" is **not established**. SSL on the Ts set does not run. If the user wants it anyway, it needs its own protocol and must set `data.unlabeled_exclude`.

## What is verified and claimable (5% base, one split, retrospective, 3 draws × 3 seeds, user-approved deviation)
1. **At +12 labelled cells, choosing cells that contain crack beats random choice:**
   - crack relF1@2 +0.030 [bootstrap +0.020, +0.042], BETTER in every cell set;
   - crack IoU +0.013, BETTER on all 50, marginal.
2. **Crack cells from the weak sources (Ts) give the best crack scores of any 5%-base model so far:**
   - 0.352 IoU, 0.795 relF1@2;
   - 0.365 IoU with LA;
   - versus BsM5 0.331 (0.356 with LA), with no unlabelled pool;
   - BMRK IoU 0.259, above L3 10%'s 0.219.
   - Whether this is source or volume is unresolved.
3. **+12 random cells bought +0.020 crack IoU, half the pre-stated +0.04.** R (0.324) is below BsM5 (0.331). For crack, random labels and SSL are roughly level at this budget; targeted labels beat both.
4. **On inactive, BsM5 keeps a clear lead:** 0.385 vs 0.33-0.35.
5. **Crack targeting costs no detectable all-class mIoU:** draw-level n.d. everywhere, though the point estimates lean negative by −0.004 to −0.011.
6. **E1 extension (descriptive):** crack-cell arms find more unseen-module crack (tolF1 0.28-0.29 vs 0.24) and raise false alarms (0.26-0.30 vs 0.20).

## For the user's best-model goal
When labelling new cells, pick cells that contain crack and prefer the under-covered sources. It costs nothing on the other classes measured here. The volume of crack pixels added is itself a predictor. That supports labelling crack-rich cells, whatever the source.
