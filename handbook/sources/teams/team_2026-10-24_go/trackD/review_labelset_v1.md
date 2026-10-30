# Review of protocol_labelset.md v1 (C, 24 Oct 2026)

## Verdict: APPROVED, with three text additions before the draws are committed. The 27-run launch also needs my sign-off on the code diff, identity diff and smoke logs (§7.4).

Checked against `critic_defaults.md` §0-1:
- the arms and the one change;
- the candidate pool (448, twins out);
- the crack-cell definition (remap px excluded; 703 remap px matches handbook 17);
- fixed RNG seeds, no redraws, lists committed before training;
- both primaries, plus Ts − R as secondary;
- the draw-level rule and the seed-level descriptive rule;
- the yardsticks, the four cell sets and per-source rows;
- the identity check (500 steps, exceeds the 200 required);
- 3 seeds per draw, recorded as the user's approved deviation;
- the Direction 4 gate.

The dry-run table is useful. Ts is exactly 6/4/2 in every draw.

## Additions required (text only, no design change)
1. **Module-position overlap with test.** CFVS is a time series, and the defaults exclude only the 7 known twins. For every added cell, flag whether it shares source + module position (`rX_cY`) with any test cell, and list those cells in `audit.json`. Tc draws carry 4-5 CFVS cells, Ts none, so undetected same-module stages would favour Tc on CFVS test crack. The "no twins" cell set is the guard. If any flagged cell is added, the no-twins rows are co-equal with the all-50 rows in the results file.
2. **Power sentence, written now.** Draw variance is unknown. The added crack px already span 1,327 to 8,761 across R draws. Write: "if the sd of draw-means is 0.015, the threshold is 0.0245; if 0.010, it is 0.016". An n.d. is then read against a stated detectable size, not as "no effect".
3. **Bootstrap at 2,000 resamples** (project standard, handbook 07 §8), not 1,000. Pair the resamples across arms.

## Notes (results file)
- **Primary 1 is confounded with crack px.** Ts adds more crack px than Tc in 2 of 3 draws (21,184 / 8,315 / 20,318 vs 18,962 / 11,070 / 13,642), mainly via 2 large CSIR cells. The regression on added crack px is the right descriptive guard. Also report Ts − Tc on BMRK and ARTS alone, where the quota, not the px, differs most.
- **Inactive px added** varies from 0 to 29,759 (Tc_d0 adds 3 cells). Report inactive IoU per draw beside crack, because inactive-edge cracks interact.
- **Crack recall is gameable by over-prediction.** Keep the relP@2 width flag next to every recall verdict.

## Before the 27 runs (§7)
Send me:
- the code diff (`86197f3` vs `88a7e88`);
- the identity diff output;
- `audit.json` with the md5 match to staging;
- both smoke logs (peak memory, steps/s, the `Labelled: 35` line).

I reply GO or STOP.

## Addendum 1: code diff `86197f3` read (C, 24 Oct, gaint `el_d1`)
- `train.py`: `data.labeled_list` is opt-in; when it is unset, the old branches are untouched. When it is set, the stems are loaded in file order and checked against train, and duplicates are rejected. `labeled_fraction >= 1` is rejected. The supervised path reads only the labelled stems, so the 27 runs depend only on the list. OK.
- `rescore_logit_adjust.log_prior` reads the same list, so each arm's LA prior comes from its own 35 cells. OK.
- **For Direction 4 (SSL), not this run:** with `labeled_list` set, the SSL pool becomes "rest of train.txt", which **includes the 7 twins** unless `data.unlabeled_exclude` is also set. Any Direction 4 protocol must set it and log "excluded 7 stems".
- Code part of the GO: satisfied. Identity, audit and smoke still pending.

## Addendum 2: GO for the 27 runs (C, 24 Oct)
Read:
- `d1chk/identity_diff.txt`: 11 lines to step 500, IDENTICAL;
- both smoke stdouts: `Labelled: 35`, step 300 reached, 2.4 steps/s;
- `draws/audit.json`, with `lists.md5` matching the lists;
- my own grep: none of the 7 train twins is in any list.

Notes for the results file:
- **Noisy-cell module.** `CSIR_00070_r7_c2`, the same module as the noisy test cell `CSIR_00070_r8_c4` and the only other cell with sigma > 40, is added in **R_d0 and Tc_d1**. Labelling it may change how those draws behave on the noisy test cell. The "no noisy cell" set is the guard: report noisy-cell crack FP per run.
- **Module-position flags.** CFVS hits (R_d0 `CFVS_00142_r3_c1` vs test `CFVS_00063_r3_c1`; Tc_d0 `CFVS_00180_r8_c6` vs `CFVS_00104_r8_c6`; Tc_d2 `CFVS_00003_r2_c3` vs `CFVS_00174_r2_c3`) have different module IDs from the test cell. They are probably not the same physical cell, but this is unverified. No-twins rows stay co-equal as set.
- **Zero-weight classes.** The recipe gives weight 0 to classes absent from the labelled set, and that set differs by draw (e.g. R_d0 contains busbars and jbox, Ts_d0 does not). This is part of "which cells" and is inherent to the A5c recipe. It matters for the all-class mIoU secondary, so list the absent classes per draw.

**GO.** Launch per §8, with GPUs 0-3 booked in the ledger.
