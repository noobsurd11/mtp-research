# judge review: protocol_SKR2_HC2 v0.9 (md5 06b502a4), 2 Nov 2026 11:25 IST

**Verdict: READY TO LOCK after three wording fixes (W1-W3) and one decision for coach / team-lead (D1).** No blocker.

Code: `judge/skr2hc2_check.py` (stdlib, opened files only: PF2 / THIN / HC m0 JSONs, HC opening records). Output: `judge/out/skr2hc2_check_out.txt`. No new test or E1 read: every number below comes from files opened at PF2, THIN-B3 and HC.

## (1) G1 inactive guard: the trade-off is sound, and test-sd calibration is acceptable as disclosed (E / S)
- **E, per-seed test inactive IoU sd:**

  | Arm | sd (all 50) | sd (clean) |
  |---|---|---|
  | SUPPF | 0.0209 | 0.0205 |
  | HC | 0.0138 | |
  | CLD | 0.0123 | |
  | SKR w 1.0 | 0.0281 | |

- **G1 at -0.015 on 5-seed means:**

  | sd assumed | SE of Δ | null trip | power at -0.023 | power at -0.030 |
  |---|---|---|---|---|
  | pooled SUPPF / HC 0.0177 | 0.0112 | **9.0%** | 76% | 91% |
  | SUPPF's 0.0209 in both arms | 0.0132 | **12.8%** | 73% | |

  - SKR2's spread may be larger (SKR w 1.0: 0.028), giving ~15% null trip.
  - The both-sets condition costs little: clean drops one cell.
- **Parents vs G1:**
  - HC trips (-0.0228 / -0.0230);
  - SKR w 1.0 trips (-0.0170 / -0.0161);
  - CLD would not (-0.0114 / -0.0106).
- **S on calibrating from the opened test seed sds:** acceptable. It uses only the spread, it can only make PASS harder, and the alternative (val inactive, 6 cells) is noisier.
- **W1:** the *location* -0.015 was also set knowing the parents' -0.023 / -0.017. Say so next to the calibration. State the per-arm false-FAIL rate as **~9-15%** (not "~9%").
- The trade-off (about 1 in 10 null arms fails on G1, about 3 in 4 HC-sized costs are caught) fits a guard the user asked for.

## (2) G2 precision (SKR2): fine; it will likely bind (E)
- **Test relP@2:** SUPPF seed sd 0.0015, so -0.03 is about 30 SE below. Null trip ~0.
- **E1 crack px on the 74 crack-free cells:**
  - SUPPF per seed 3,092 / 2,718 / 5,178 / 4,179 / 4,486 (mean **3,931**, CV 0.26);
  - the 1.5x bar is 5,896; null trip ~0 for a 5-seed mean.
- **Parents vs G2:**
  - SKR w 1.0 trips both (-0.070; x2.40);
  - **CLD would have tripped the E1 arm (x1.53**, relP -0.019);
  - HC is x0.90.
- So G2 catches clDice-level widening too. Coach's own expectation for SKR2 (x1.2-1.6) straddles the bar.
- **Note:** the any-hit co-primary rewards spraying predictions over crack cells. G2's E1 term only sees crack-*free* cells, and E1 relP@2 is reported only. Optional: also report E1 pred/GT and E1 relP@2 next to any-hit in the verdict table. No change to the rule.

## (3) E1 any-hit: same definition, confirmed (E)
- My 0.381 is exactly the protocol's definition:
  - m0 `crack_cc.gt` entries `[size, hit]` on GT crack & keep, 8-connected, where hit = px within 2 px of a prediction (`dp <= 2 & keep`, as b6_score / m0_audit_tau `comps`, line-identical);
  - any-hit iff size >= 20 and hit >= 1;
  - per run, pooled over the 106 E1 cells (296 components), then the mean over seeds 5-9.
- Per seed: SUPPF 0.399 / 0.355 / 0.429 / 0.365 / 0.358 (**0.3811**).
- References: SKR w 1.0 0.523, CLD 0.410, HC 0.377.
- The scorer self-test should reproduce 0.3811 exactly from PF2's m0 files.

## (4) HC2 dose: the numbers hold, but val and SHV1 are one observation, and the independent non-E1 sets point the other way (E / S)
- **E (own, HC opening records at b 0, 5 seeds):**

  | Set | SUPPF | HC | Δ | Per seed (SUPPF / HC) |
  |---|---|---|---|---|
  | val | 0.508 | 0.468 | -0.039 | |
  | SHV1 | 0.471 | 0.383 | -0.088 | SUPPF 0.417-0.506, HC 0.325-0.418 (touch) |
  | F51 | 0.181 | **0.235** | **+0.054** | |
  | F19 | 0.222 | **0.314** | +0.092 | SUPPF 0.06-0.51 (noisy) |

  - All equal coach's.
- **The flaw (S):** SHV1 is both halves of the **same 54 val cells** (protocol_HC §5).
  - Its inactive images come from val's 6 inactive cells, in half-cut geometry.
  - So "the cost appears in-simulator (SHV1) and on val" is **one observation of 6 cells, seen twice**.
  - The two non-E1 sets that are independent of val (F51, F19) move **up** under HC.
  - The honest basis for "HC costs inactive" is test (-0.023, 11/16 cells; seed-aware P 0.95) plus val's 6 cells.
- **W2:** rewrite §0 / §2's "the inactive cost appears in-simulator and on val, so it is tied to the synthetic views". Suggested: "test (opened) and val's 6 inactive cells (also seen through SHV1, which is built from them) drop; F51 and F19 rise; the guard exists because of test".
- **What still stands:** HC is worse on inactive in its *own* simulated geometry (SHV1 -0.088). That points at the synthetic views, which is the dose argument's real support, from 6 cells.
- **D1 (decision for coach / team-lead; S):**
  - Halving p asks "less exposure, less cost?". It cannot separate dose from the inactive-bearing synthetic views:
    - if G1 still trips, the cause is unknown;
    - if it passes, the mechanism may also have halved.
  - The **inactive-source-ineligible variant** (your alternative) tests the cause directly. 41 of 353 sources carry inactive, so about 88% of synthetic views stay, and most of the crack mechanism should survive.
  - It costs a small build (a stem exclusion list in the eligibility step), a p 0 / no-list identity check and a smoke, and removes no other lever.
  - I would run it as HC2 instead of the half dose, if a 0.5-day build is acceptable.
  - If HC2 stays the half dose, add the HC p 0.35 reference row's SHV1 and val inactive to the reported dose comparison. That is already there; keep it.
- **Mechanism margin:** "+0.123 is 2.5x the kill line" is fine as S. There is no dose-response data, so a mechanism FAIL at p 0.175 is a real possibility, as stated.

## (5) B5 wider grid and multiplicity (S, with code logic E)
- **Wider grid:**
  - Under calib's rule (max val recall s.t. P >= 0.90, ties smaller b), recall is non-decreasing in b.
  - Extending the grid below -4 can only move an OP that today sits at the grid edge -4.0, or is unreachable (SKR w 1.0).
  - SUPPF's OPs (pooled b_comp 3.9; per-run b_rel 2.9-4.5) cannot move.
  - So "unchanged unless its optimum lies below -4" holds.
  - The planned self-check (records on -4..+12 equal 6e73ff11 exactly) is the right test. Also assert in the new scorer that SUPPF's chosen OPs equal the frozen ones.
- **Multiplicity:**
  - Rule 1's threshold is 2·sqrt(5/3) ≈ 2.58 SE of the 5-v-5 difference. That is a one-sided false BETTER of ~0.5% (normal) to ~1.6% (t, 8 df) per co-primary.
  - Over 7 correlated co-primaries (SKR2), the family-wise false PASS is ≤ ~10%, minus the two-set rule and the guards.
  - Against that, G1's false FAIL is 9-15%. The protocol leans strict, as intended. Disclose both rates in §3d.
- **W3:** in §3d, report which co-primary(ies) carry any BETTER, and keep the verdict table showing all 7 / 5 with the guard values.

## Minor
- The header says the user's choice came "2 Nov ~03:4x". log.md records it at 11:18 (team-lead). Please confirm the time.
- Integrity at build: el_thin was released from builder's freeze after THIN. The opening's integrity pass must show HEAD = c9bbb02 with 0 tracked changes, as planned.
- Runner should confirm that PF2's b5_work dumps (SUPPF B5 records on the wider grid) still exist on gaint before the opening is frozen.

## Delta check: v0.9.2 (md5 0964d89a), HC2 = inactive-ineligible variant (2 Nov 11:33 IST)
Verdict: (a) whole crop is right; (b) the CPU identity chain is enough, under one condition. But the variant **removes most of HC's synthetic crack signal**, and §2 / §5 / §7 must say so (**W4**). Lock after W4, and after builder's exact counts.

- **(a) Whole crop: correct.**
  - The simulator rescales and crops the split crop, so neighbour rows can enter the synthetic view.
  - A centre-only test would let inactive px into synthetic views, and the "synthetic inactive px = 0" assert could then fail.
  - Keep whole crop.
- **(b) Identity chain: sufficient by transitivity, if builder's diff c2e6973..new touches only code behind the new key.**
  - That means a new eligibility predicate plus one guarded call site, with no change to the transform order, RNG use or the loader outside the key branch.
  - Put the diff in the build note; coach or found reviews it.
  - If any line outside the key branch changes, add a GPU H0 at the new deploy: p 0, >= 1,000 steps vs f3_SUPPF_100pct_s0.stdout (~8 min).
- **E (`results/b6/b6_folds.tsv`, train, whole-crop px from masks_escdd):**
  - In HC's source families (ARTS / CFVS / CSIR; BMRK / SDLE are never sources) only **36** of 419 train cells hold any inactive px:
    - ARTS 1, CFVS 25, CSIR 10;
    - so "~41 of 353" cannot be right: at most 36, fewer within the 353.
  - **All 36 are crack cells, and they hold 58% of the crack px of those families** (CFVS: 117,352 of 171,806 in its 25 inactive-bearing cells).
  - So HC2 keeps ~90% of synthetic *views* (live share ≈ 0.35 x 0.7385 x 317/353 ≈ 0.23) but **roughly 40-50% of HC's synthetic crack px**, and loses the largest cracks (the CFVS chains).
  - Builder gives the exact numbers within the eligible set: sources kept, crack-bearing sources kept, crack px kept.
- **W4:**
  - §2: state the crack-signal loss next to "~88% of views", with builder's counts.
  - §5: lower the mechanism expectation (crack dose roughly halved, biggest cracks gone).
  - §7: "HC2 mechanism failed -> the route closes" is not supported if the crack-px dose fell below about half. A mechanism fail would then be confounded with the crack dose. Write "mechanism failed at ~X% of HC's crack-px dose; the route closes only for designs that drop inactive-bearing sources".
- **Alternative, if builder's crack-px retention is < ~60% (S; coach / team-lead's call):**
  - Keep the inactive-bearing sources eligible, but label their inactive px as ignore (255) in the synthetic views only. This needs the loss to honour an ignore index; builder checks.
  - It keeps the full crack dose and removes synthetic inactive labels (cause A), but not the dilution of real inactive views (cause B).
  - If G1 then still trips, cause B is indicated.
  - It is more diagnostic for the inactive question and keeps the mechanism intact. The current variant removes A and B together but halves the crack signal.
