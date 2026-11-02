# judge review: protocol_SKR2E v0.9 (md5 ce9e55ee), 2 Nov 2026

**Verdict: NOT READY TO LOCK.** One design change is needed (D1: a shared verdict b). Two guard changes are recommended (G1t added, G1e described honestly). There are four wording fixes. Everything else is sound.

Code: `judge/skr2e_check.py` f4193bb4 (opened files only: the S2 singles' val rec_w, PF2's m0 E1 GT component lists). Output: `judge/out/skr2e_check_out.txt` c5de7d5d. No new test or E1 read. Ensemble bias sensitivity is quoted from `verify_pf2e.md`.

## D1 (must fix): the verdict must compare the two arms at one b, not each at its own headline b (E / S)
- **E, bias moves the ensemble readouts by as much as the effect being tested** (PF2E, opened):

  | arm, b change | E1 relF1@2 | test relF1@2 | test crack IoU |
  |---|---|---|---|
  | E-PF, b 0 → 1.5 | 0.4345 → 0.4733 (**+0.039**) | 0.8942 → 0.9078 (+0.014) | 0.4815 → 0.4888 (+0.007) |
  | E-g, b 0 → 1.25 | 0.3990 → 0.4442 (**+0.045**) | | |

  - So one ensemble at b ~1.25-1.5 against the other at b 0 carries an E1 relF1@2 gap about the size of SKR2's whole expected effect (+0.02 … +0.04, §5).
  - any-hit is monotone in b, so it moves the same way.
- **E, val only, the asymmetry is plausible (singles' pooled val curves, not ensembles):**
  - SKR2 starts higher on recall (val relR@2 at b 0: 0.860 vs 0.846) and loses pixel precision slightly more slowly per unit b (−0.0129 vs −0.0145 at b 1).
  - E-SKR2 should therefore reach D2's relR@2 ≥ 0.90 at a smaller b, with a smaller precision drop, than E-PF did (b 1.5, drop 0.075).
  - The likely outcome is that E-PF's width flag trips (headline 0) and E-SKR2's does not, or is borderline (headline > 0). §5's "both headline b likely 0" is not safe.
- **Then the verdict would compare "SKR2 + a bias step" with "PF at argmax".** A pass could come from the bias alone.
- **Fix:**
  - Primaries and verdict at **b 0 for both arms** (argmax; PF2E's actual verdict point; symmetric).
  - **Guards at each arm's headline b and at b 0** (the deployed OP must not pay the precision cost; strict side).
  - Have the script write both arms at the union {0, b_D2(E-PF), b_D2(E-SKR2)}, so the following rows are reported:
    - the headline pair;
    - **E-PF at E-SKR2's headline b**, so the reader sees how much of any headline gap is bias.
  - Keep "deployable" in §7 as: E-SKR2 is recommended **at its headline b** only if the b 0 verdict passes and no guard trips at the headline pair.
- **Q6 answered:** one shared b, and that b is 0. A shared b at E-SKR2's D2 b is not right, because E-PF's own rule rejects b > 0 (flag).

## G1e and the missing test-inactive guard (S, with E)
- **G1e (E1 inactive cluster CI wholly below 0) has almost no power.**
  - PF2E's E1 inactive cluster CI half-width is ~0.18 ([+0.030, +0.382]).
  - It would not trip on HC2's single-model E1 loss (−0.080), only on a collapse.
  - The readout is 10 cells / 7 images, n_eff 3.3. Keep it if you like, but say in §3b: "trips only on a collapse (Δ ≲ −0.18)".
- **Nothing at ensemble level guards test inactive at HC-size costs.**
  - The test inactive primary "fails" only if its image CI is wholly below 0: half-width ~0.065 at ensemble level (PF2E [−0.031, +0.097]).
  - A −0.025 loss (HC / HC2) would pass silently.
- **Recommend G1t:** test inactive IoU Δ ≤ −0.015 in both sets (point estimate, at b 0 and at the headline pair) → FAIL. This is the singles' G1 carried over.
  - Null false-FAIL (S): ~8%. Ensemble Δ seed-composition noise ≈ sqrt(0.0209² + 0.0110²) / √5 ≈ 0.011 from the singles' test inactive sds; P(Z < −1.4).
  - SKR2's singles sit at +0.010, so it trips only on a real loss.
  - This is the guard the user asked every follow-up to carry. Disclose its ~8% false-FAIL cost.

## G2a / G2b at ensemble level: fine (E / S)
- **G2a** relP@2 Δ < −0.03: SKR2 singles −0.012; ensembling does not widen. Null trip ~0. Fine. At an asymmetric headline pair it penalises the bias step, which is the right side.
- **G2b** ×1.5 of E-PF's E1 crack-free px:
  - E-PF 2,528 (bar 3,792) at b 0.
  - Singles' ratio ×0.97; ensembles cut FA (E-PF 2,528 vs singles 3,931).
  - Fine, and ratio-based, so the ensemble's lower level does not matter.
  - Evaluate at b 0 and at the headline pair (D1).

## any-hit cluster pooling: right; state what it measures (E)
- Ratio of pooled component counts over the resampled clusters is correct. It is the same estimator as the singles', with clusters instead of cells.
- **E, GT-only (m0 E1 crack_cc):**
  - the 296 GT components ≥ 20 px sit in **21 of the 71 images**;
  - the top 3 images (CSIR_01717 70, CSIR_01637 59, CSIR_01679 41) hold 57% and the top 10 hold 94%; n_eff **7.1 images**;
  - **274 of 296 are in the 29 scuff + half-cut cells.**
  - So E1 any-hit is a scuff + half-cut readout on ~7 effective images. The CI will be wide: the singles' seed sd is already 0.032.
  - Expect n.d. (§5 says so). Tell the user plainly that any-hit is unlikely to settle "knife-edge" at ensemble level.
- **The component count is GT-only, so a mismatch must STOP, not be disclosed.** It would mean a different connectivity or keep mask, i.e. a different metric.
  - Add a val gate before any test / E1 read: the ensemble script's val GT component count (≥ 20 px) must equal m0's val count, 125, exactly.
  - Keep the val any-hit ±0.01 member-s5 check.
  - Assert E1 = 296 at read time, else stop before scoring.
- §4's leave-one-cluster-out range is good. Also report any-hit on the 29 scuff + half-cut cells and on the other 77.

## Multiplicity (S)
- Coach's ≤ ~12% (5 primaries × 2.5%, crude) is right **for the question as framed: these two concrete ensembles**. The fixed-model CIs are the right ones for that.
- **For a recipe reading it is understated.** The CIs leave out seed-composition noise. From the singles' sds (S, rough), per-primary one-sided false pass rises to:

  | primary | false pass |
  |---|---|
  | test crack IoU | ~5% |
  | test relF1@2 | ~4.5% |
  | E1 relF1@2 | ~4% |
  | any-hit | ~5-6% |
  | test inactive | ~3% |

  - Family-wise ~15-20% (test crack and relF1 are correlated).
- **Wording fix:**
  - §3c: "≤ ~12% for the two ensembles as objects; ~15-20% if read as a recipe claim (seed noise not in the CIs)".
  - §7: a PASS is a claim about the deployable artefact, not a second confirmation of the SKR2 recipe.

## Wording fixes
1. **§3c / §7:** a PASS must name the primary that carried it (W3 style). If it is a test crack primary, the n.d. sentence's subject is still true ("SKR2's single-model E1 gain is not confirmed at ensemble level") and must be said with the PASS. Only an E1 co-primary pass confirms the E1 gain.
2. **§0 disclosure:** add "E1 opening #6 reads the same 106 cells with the same 5 SKR2 members whose E1 numbers were opened at #5. The ensemble E1 result is a re-measurement of an opened effect, not new evidence for it" (as PF2E was for #1).
3. **§5:** change "both headline b likely 0" to "E-PF's headline is 0 (PF2E); E-SKR2's may be > 0 (smaller precision drop expected, E judge val singles); the verdict is at b 0 either way (D1)".
4. **§6 gate:** add the val GT component count = 125 exact (above), and make the E1 296 mismatch a STOP.

## What is right as drafted
- E-PF identity and reuse: decisions equal PF2E's, and cells exactly equal after the run, else E-PF is taken from this run. Good.
- Strict load with the key / shape assert for c9bbb02 checkpoints on e544133 model code, plus the member-s5 val gate against its own opening m0. Sufficient.
- The bootstrap self-test (E-PF vs E-g reproduces PF2E; arm vs itself gives [0, 0]) is good. Add one any-hit self-test: E-PF's any-hit at b 0 from this run's files equals the same count read from PF2E's E-PF.b0.json crack_cc.
- Order: val decisions to file before any test / E1 cell; one process; refusal of a second pass (as PF2E). Good.
- CPU fp32, nice 19, 8 threads, outside runner windows. Good.

## Lock condition
Apply D1 (verdict at b 0; guards at b 0 and the headline pair; union-b outputs), G1t (or a written reason for not adding it), and fixes 1-4. Then I sign v1.

## SIGNED: v1 candidate (md5 1c45ab19), 2026-11-02 21:59 IST
- Every item of this review is applied as asked:
  - D1: verdict at b 0 for both; union {0, both D2 b}; guards at b 0 and at the headline pair; E-PF at E-SKR2's headline b reported; §7 condition.
  - G1t (≤ −0.015 both sets); G1e "collapse only"; Q3 (any-hit = scuff + half-cut readout, likely n.d.; val 125 / E1 296 STOP; any-hit self-test).
  - Q5: both multiplicity figures. Wording 1-4.
- **Signed for lock.** Two non-blocking notes for the build (coach checks them at APPROVED):
  1. §4 "matched-volume check ... from the stored sweep": PF2E's script stores a val sweep only. The build must also store an **E1 aggregate sweep** (per b on the D2 grid: pred / GT crack px, relF1@2, any-hit, crack-free px; written after the val decisions; reported only). Otherwise that §4 line is omitted and disclosed.
  2. G1t is now evaluated at two OPs. If E-SKR2's headline b > 0, the null false-FAIL is ~8-10%, not ~8% (S). Say "~8-10%" in §3b / §5.
