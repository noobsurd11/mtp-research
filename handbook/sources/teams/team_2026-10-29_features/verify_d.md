# coach verify: D (inference-only E1 checks; val + E1 only, no test)

coach, 30 Oct 2026. Independent recompute from `d_checks/d_cells.json` (per-cell 24x24 confusions; MANIFEST.md5 OK), against `d_prereg.md` (md5 33778eb0, written 12:33 before any D number).

**vs runner's d_report: CONFIRMED.** Every number below matches runner's to 3 decimals.

## 1. Gate and pre-registered read (bias +0.75, variant − CPU FINAL)
- **Cross-check:** FINAL val re-scored on CPU vs cv02 bf16, max |Δ| 0.0005 (limit 0.005).

| Variant | Target recall (29 scuff + half-cut) | Must-not-hurt (29 half-cut, no scuff) | 48 full cells | E1 crack P (cost) | E1 crack IoU | crack px on 74 crack-free E1 cells | val relF1 drop | Read |
|---|---|---|---|---|---|---|---|---|
| FINAL (CPU) | 0.125 | 0.552 | 0.458 | 0.462 | 0.172 | 4,068 | 0 | reference |
| RN50-5 | 0.185 (+0.060) | 0.606 | 0.443 | 0.415 (0.047) | 0.191 | 5,966 | −0.002 | **PASSES** (narrowly) |
| BN-HC routed | 0.299 (+0.174) | 0.735 | 0.458 | 0.376 (0.085) | 0.225 | 7,846 | 0 | fails: precision cost |
| BN-HC global | 0.299 (+0.174) | 0.735 | 0.595 | 0.291 (0.170) | 0.198 | 16,306 | 0.151 | fails |
| R34-5 + RN50-5 | 0.161 (+0.036) | 0.591 | 0.461 | 0.465 (−0.003) | 0.192 | 4,493 | −0.007 | fails: gain |

## 2. Reading (S unless tagged)
- **RN50-5 passes, but narrowly:** +0.060 vs the +0.05 line, and a cost of 0.047 vs the 0.05 line.
  - One 5-member ensemble per variant, no seed CI, 29 cells. A second RN50 draw could fall either side.
  - It agrees with earlier signals: Track M R3 RN50 E1 crack recall +0.036, and 27 Oct F4 half-cut recall 0.133 → 0.183 (E).
  - But Track M R3 RN50 was **WORSE on test inactive** (−0.0251 vs threshold 0.0227, clean; `handbook/11` row 19). Val inactive rises here (0.429 → 0.457), which does not settle test.
  - These RN50s trained under the house optimizer, which erases the deep encoder (`coach_100.md` §0). So the RN50 advantage on E1 is what survives erasure. Under PF it may be larger (S).
- **BN-HC routed has the largest E1 gain but fails the pre-stated cost.**
  - Descriptive, post hoc, not a claim: at bias 0, BN-HC routed has E1 P 0.481 (≥ FINAL b0.75's 0.462) with target recall 0.201 (+0.076) and E1 recall 0.268 vs 0.215.
  - So the gain is not only a crack-prior shift. But on the routed half-cut cells, precision is 0.514 vs 0.609 (FINAL b0.75); the matched overall precision hides a half-cut precision loss.
  - Choosing BN-HC's bias would need labelled half-cells outside E1. Val has none, and E1 is never for selection. The B2 mined cells, if labelled, would be that set.
- **The size-matched R34-10 control** (after opening 1) only matters for the 10-model variant, which already failed. RN50-5 vs R34-5 is size-matched.

## 3. What follows (proposal; needs its own protocol and a test opening)
- **RN50 at 100% labels,** 5 v 5 on gaint against the matching R34 arm.
  - If protocol_100 shows SUP100-PF ≥ SUP100-g, run RN50-PF vs SUP100-PF (coach_strategy A2). Otherwise RN50 house vs SUP100-g.
  - Primaries as house (test crack IoU, relF1@2, inactive IoU; inactive is the known R3 risk). Named secondary: E1 scuff + half-cut recall at FINAL's bias.
- **BN-HC routed:** no protocol until labelled half-cells outside E1 exist (B2 labels). Then pick the bias on them, and test.

## 4. Size-matched control R34-10 (after opening 1, as pre-registered; coach recompute 31 Oct ~02:05, CONFIRMED)
- **Source:** `d_checks/d_cells_r34_10.json` (MANIFEST OK). R34-10 = FINAL 5 + SUP100-g 5 (f3, e544133); FINAL val cross-check |Δ| ≤ 0.0005.
- **Bias +0.75, R34-10 vs FINAL:**
  - target recall (29 scuff + half-cut): 0.1265 vs 0.1251 (+0.001);
  - must-not-hurt: 0.551 vs 0.552;
  - 48 full cells: 0.447 vs 0.458;
  - E1 crack P: 0.493 vs 0.462;
  - E1 crack IoU: 0.1756 vs 0.1722;
  - crack px on the 74 crack-free cells: 3,525 vs 4,068;
  - val relF1@2: 0.9004 vs 0.8963.
  - All match runner's report.
- **Reading:** doubling the R34 ensemble does not move the target (+0.001). So the +0.036 of R34-5 + RN50-5 and the +0.060 of RN50-5 come with the RN50 members, not with ensemble size. That strengthens the RN50 lead in §2-3 (still descriptive, E1 only).
