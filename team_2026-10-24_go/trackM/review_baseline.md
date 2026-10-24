# MC review of `baseline.md` (M0, inference only)

MC, 24 Oct 2026. **Verdict: APPROVED**, with 5 notes (none changes a number).

## 1. Independent recompute (E)
Code: `trackM/mc_verify/mc_score.py`, `mc_agg.py`, `mc_base.py`, `mc_base2.py`. They share no code with MD's `m0_analyze.py`; they read only the per-cell confusion matrices, relaxed counts, component lists and p-bands in `m0/*.json`.
- **Inputs.** MD5 of all 10 JSONs = `m0/md5_cv02.txt`. All runs have step 20000.
- **Against the original rescores.** My crack IoU, inactive IoU and relF1@2 equal the P6 and P16 raw JSONs (`results/p6/raw`, `results/p16/raw`) for all 5 SUP100 runs, to the last printed digit (for example A100 s3: 0.29654 / 0.45420 / 0.64062).
- **Against baseline.md.** Every number below matches to 3 decimals:
  - §2 table, all four rows: crack IoU, P, R, relP@2, relR@2, relF1@2, inactive IoU, P, R, mIoU_rob, mIoU_rob without 0/7;
  - §2 per-seed crack IoU and mIoU_rob, both cell sets;
  - §2.2 per-class IoU (all 15 classes);
  - §3 per-source mIoU_rob, relP@2 and relR@2;
  - §4 component recall and precision (crack 0.790 / 0.837 all; 0.798 / 0.924 without noisy; inactive 0.757 / 0.755);
  - §4 p(crack) bands, test and ext;
  - §5 ext crack IoU / P / R, inactive IoU;
  - §6 plain and TTA single-model val crack IoU (0.423, 0.433) and inactive IoU (0.411, 0.453).
- **Not recomputed:** the §6 ensemble, LA, bias and cross-fit rows. They need the val logits, which sit on cv02 only. They are val-only explorations and enter no claim; they get recomputed when a rung uses them.

## 2. Checks against the fake-gain list
| Risk | Status |
|---|---|
| Test used for tuning | None. Test and ext get plain argmax only; every tuned variant is val only (§6) |
| Best-val checkpoint | None; final step asserted |
| Seeds | 5. Pools P6 s0-2 (`824fab0`) with P16 s3-4 (`bac5264`), same precedent as P16's A100 (handbook 13 C12) |
| Noisy cell | Reported in every table; its mIoU effect is quantified (§2.1) |
| Twins | Reported |
| mIoU convention | Fixed before reading; robust list from test GT only |
| Recall without precision | Precision is beside every recall |

## 3. Notes for design.md
1. **The baseline to beat is SUP100 at 5 seeds, both cell sets.** The README's "0.471" is the 3-seed P6 mean. With 5 seeds it is 0.435±0.078 on all 50, because one seed fails on the noisy cell. Every rung is judged on both rows. Any "beats the baseline" that holds only on all 50 is a noisy-cell effect until shown otherwise.
2. **Subset mIoU convention.** In a subset, a class with no GT becomes NaN even if predicted, so per-source mIoU_rob hides false positives of absent classes. Keep it, but print FP px of subset-absent classes beside the per-source table.
3. **The crack target (§4) is accepted as a descriptive, user-facing target, not a decision rule.** Val already shows ensemble + crack bias +1 at relR@2 0.895 / relP@2 0.898, so the target is mostly an operating point.
   - Rungs are decided by rule 1 on the primaries (crack IoU, inactive IoU, relF1@2, mIoU_rob), on both cell sets.
   - The operating point that meets the target is chosen on val and frozen in a protocol.
   - Report the target on all 50 too, and always with pixel precision and crack IoU.
4. **Val mIoU in §6** is over val's 17 GT classes. Define a val robust list (classes in at least 3 val cells) now, for any val-based choice that involves mIoU.
5. **Inactive on val** (6 cells, 3 of them holding 89% of the px): the TTA inactive +0.042 and the 24-class bias's inactive −3.0 are not evidence. Per rule (b), no inactive bias without a positive gain in both folds.

## 4. Readings I agree with (R)
- At 100% labels, 28% of GT crack is in the 0.001 to 0.95 band (8% at 5%), so operating point, TTA and ensembles have real room. 19% is a confident miss, which needs a better model.
- Weak spots for the ladder: BMRK (crack relR@2 0.745, inactive recall 0.39), CFVS without twins (relR@2 0.681), gridline (recall 0.33), splice (never predicted).
- Unseen modules: 70% of GT crack below 0.001; no operating-point rung can reach it.
