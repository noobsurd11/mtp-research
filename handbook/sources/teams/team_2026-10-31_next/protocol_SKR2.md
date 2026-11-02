# Protocol SKR2 (sketch): Skeleton Recall at a lower weight, with a precision guard, on SUP100-PF

**SUPERSEDED 2 Nov by `protocol_SKR2_HC2.md` (user chose SKR2 + HC2 in one protocol).** coach, 1 Nov 2026, **v0 SKETCH. NOT LOCKED.** User decides after the A8 screen and HC results (team-lead, 1 Nov ~21:45). Written after THIN-B3's opening (`verify_thin_b3.md`), so the THIN-B3 numbers are known; the design below is chosen from them and says so. Tags: E / S.

## 0. Why (E, `verify_thin_b3.md`, judge-confirmed)
- SKR w 1.0 FAILED on the pre-registered rule: test crack IoU WORSE (−0.0136 / −0.0140), because predictions widen (test predicted / GT crack px 0.954 → 1.545; relP@2 flag −0.070).
- It is the only arm so far with a large E1 crack gain on width-robust measures: E1 relF1@2 +0.059 BETTER; any-hit component recall 0.381 → 0.523 (judge). Pixel recall is inflated by the fattening (E1 GT ~1.5× wider). Costs: E1 crack-free px ×2.4, scuff px ×2.0.
- At matched val precision the gain partly survives on test (B5 comp recall +0.041 BETTER). But SKR's pooled val relP@2 does not reach 0.90 anywhere on the grid (max 0.894 at b −4.0), so the precision-matched co-primary could not be read properly.
- S: a lower weight should keep part of the recall push with less widening. The paper tested 0.1 and 1.0 (R arXiv 2404.03010 Sec. 4.4). This is a dose question chosen after seeing w 1.0; disclosed.

## 1. Question
Does SUP100-PF + Skeleton Recall at **w 0.1** raise E1 crack detection (width-robust) without a test cost and within a precision guard? Contrast: SKR0.1 − SUP100-PF, 5 v 5, seeds 5-9. (Optional second arm w 0.3, its own contrast; user's choice: +5 runs.)

## 2. Baseline and code
- **Code:** el_thin **c9bbb02**, the THIN-B3 deploy. Its training code equals the smoked d93d9a1 (c9bbb02 vs d93d9a1: m0_audit_b3, the b3_scuff helper, scuff_train_iou and tests only; E). **Shared-baseline condition:** S0 (switches off, 2,000 steps) IDENTICAL to `f3_SUPPF_100pct_s0.stdout`, already shown at d93d9a1 (smoke S0, 1 Nov 00:19). So PF2's `pf2_SUPPF_100pct_s5..9` stay the comparator; their per-cell files are reused unchanged (MANIFEST 3827f7c0 re-checked).
- **Arm opts:** pf2_SUPPF opts + `loss.skel_recall.weight=0.1` (one change); run names `skr2_SKR01_100pct_s5..9`; 20,000 steps; final weights.
- Reported reference (already opened, not a contrast): THIN's SKR w 1.0 s5-9.

## 3. Co-primaries (draft; rule 1 /3; PASS = ≥ 1 BETTER, none WORSE; test with the two-set rule)
1. Test crack IoU, crack relF1@2, inactive IoU (argmax).
2. **B5 on a wider grid:** comp recall at comp P ≥ 0.90 and relR@2 at relP@2 ≥ 0.90, arm-pooled OP chosen on val over b ∈ **−8.0 … +12.0** (step 0.1; the wider floor so a precision-target OP is reachable for SKR arms); SUPPF's OP re-chosen on the same wider grid from its frozen val records (unchanged unless its optimum lies below −4, E: SUPPF pooled b 3.9).
3. **E1 (second test set, read once):** crack relF1@2 (all 106, argmax) and **E1 any-hit component recall** (GT crack components ≥ 20 px with ≥ 1 px within 2 px of a prediction; from the m0 `crack_cc` hits), the width-robust pair (judge).
- **Precision guard (pre-registered FAIL conditions, not just flags):** test relP@2 at argmax drops by > 0.03, or E1 crack px on the 74 crack-free cells > 1.5 × SUPPF's (seed means). Either trips → the arm FAILS, whatever else passes.
- Reported: pred / GT crack px (test, E1), crack precision, E1 scuff px, strata, any-hit recall on test, the w 1.0 reference, LA tau 1, B5 per-run OPs, cosines, thin-term magnitudes.

## 4. Expectations (S)
- Test crack IoU −0.005 to +0.005 (widening ~1.1-1.2× instead of 1.5×); relF1@2 n.d.
- E1 relF1@2 +0.01 to +0.04; any-hit comp recall +0.03 to +0.10; crack-free E1 px ×1.2-1.6 (guard at 1.5× may bind).
- Likeliest: n.d. on test, E1 n.d. or a small BETTER. A clean pass is possible but not likely.

## 5. Cost and order
- 5 runs × ~2.5 h in 3 packed lanes ≈ 12.5 lane-h (SKR peak 7,020 MiB, gate 9,100; ~3.3 steps/s alone). On gaint after HC and the A8 screen (and after the A8 full arm if GO, unless the user orders otherwise). Optional w 0.3 arm: +12.5 lane-h.
- Opening: thin_post.sh pattern (m0_audit default + tau 0/1, rescore, LA, frozen B5 with the wider grid as a NEW frozen scorer version, md5 before launch), E1 opening #5 (if registered).

## 6. Open before lock
- User: go / no-go, one or two arms.
- B5 wider-grid scorer: calib's el_metrics records already store b −4..+12 only; a wider floor needs records re-made from the dumps (dumps on gaint for THIN / PF2 val) with a new frozen version (GRID extended, OPGRID to −8). Builder or runner; md5 frozen before launch.
- judge: review of the guard thresholds (0.03 relP@2; 1.5× crack-free px) and the any-hit definition.
