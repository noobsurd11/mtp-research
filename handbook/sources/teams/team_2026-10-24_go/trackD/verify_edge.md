# Edge re-score: independent recompute by C (24 Oct 2026)

**Verdict: CONFIRMED**, with one wording addition.

## Checks
- My own script (scratchpad `edge_chk.py`) reads `results/trackD_edge/edge.json` per-cell counts `[TP, FP, FN, pred-within-2px, pred, GT-within-2px, GT]` and recomputes:
  - crack IoU, relF1@2 and recall per run;
  - standard and banded;
  - the four cell sets;
  - rule-1 thresholds (5 v 5).
- A5c standard all-50 τ 0 crack IoU 0.30372 equals `la_sa_test.json` (0.3037).
- **All six contrasts × 3 metrics × 2 versions × 4 cell sets match `edge_results.md` §3** (Δ and threshold to 3 decimals).
- Band share 10,650 / 92,074 = 11.6%; per source BMRK 22.6%, CSIR 7.9%, CFVS 7.6%, ARTS 2.5%; in-band recall A5c 0.178, BsM5 0.241. All match §1.

## Confirmed findings
1. **Kill not triggered.** No sign flip in any contrast, metric or cell set.
2. **Banding raises 5-10% arms by +0.018 to +0.027 crack IoU, but only +0.012 (A50) and +0.007 (A100).** The convention costs the low-label models about 0.02, not the full-label model.
3. **About a fifth of SSL's crack-IoU gain sits in the inactive-edge band.** BsM5 − A5c drops +0.029 → +0.023 (all 50); without twins, +0.019 → +0.014 (thr 0.018), BETTER → n.d. on crack IoU. Same for BsD5 and al1 BsM5.
4. (BsM5+LA) − (A5c+LA) passes on all three crack metrics in every cell set, banded or not (post hoc yardstick).
5. BMRK's 22.6% band share barely moves its IoU (±0.01). The inactive-edge convention is not what makes BMRK hard.

## Wording addition
- Verdicts here are **per crack metric**, not the full rule-1 verdict. The rule-1 primaries also include inactive IoU, and banding leaves inactive untouched, so every BsM5/BsD5 − A5c rule-1 verdict stays BETTER through inactive.
- One per-metric cell not listed in §3: without twins, banded BsD5 − A5c crack **recall** is still BETTER (+0.027, thr 0.025).
