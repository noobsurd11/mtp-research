# R4 results: + 107 leakage-free E-SCDD cells (585 train cells), 100% labels

MD, 24 Oct 2026. Status: **VERIFIED by MC** (`verify_r4.md`): n.d. on all four primaries, val EXCLUDE.
Protocol: `protocol_r4.md` (APPROVED). Runs `m_r4_extra107_s0..4`, cv02 `el_mt4` (`0642889`), data root `/tmp/noob_el/data_r4`, `=mq4`, 24 Oct 12:37-21:21 IST. All rc = 0, step 20,000 (asserted).
Files:
- `r4/m_r4_extra107_s*.json`: M0 scorer, scored with `--code el_mt4` (its `data/` is the shared original), so val/test masks are the originals; MD5 = cv02 (`r4/md5_cv02.txt`);
- `r4/r4_tables.txt`: the `m2_rung.py` output.

Comparator: SUP100 (`m0b/`). This is Track M test opening no. 3.

## Verdict
**R4 is n.d.** on all four primaries in both cell sets; no primary is worse. **Val inclusion: EXCLUDE** (nothing passes on val), so R4 does not enter the stack.

| set | crack IoU Δ (thr) | inactive IoU Δ (thr) | relF1@2 Δ (thr) | mIoU_rob Δ (thr) |
|---|---|---|---|---|
| all 50 | +0.0065 (0.1161) | +0.0111 (0.0186) | +0.0094 (0.1556) | +0.0029 (0.0191) |
| without noisy | +0.0010 (0.0100) | +0.0085 (0.0179) | +0.0012 (0.0100) | −0.0032 (0.0129) |
| val | +0.0044 (0.0100) | +0.0288 (0.0426) | +0.0026 (0.0100) | +0.0050 (0.0100) |

- **Bootstrap, without noisy:** crack +0.0010 [−0.0026, +0.0062]; inactive +0.0085 [−0.0042, +0.0277]; relF1 +0.0012 [−0.0029, +0.0061]; mIoU_rob −0.0032 [−0.0094, +0.0038].
- **Noisy cell:** one R4 seed fails on it (s0: 57,152 crack px). The all-50 sds are inflated as for SUP100.
- **Width flags:** none. Crack precision 0.644 → 0.648 and inactive precision 0.631 → 0.641 (without noisy).
- **Multiplicity:** 8 tests.

## Named secondaries and controls (descriptive, rule-1 arithmetic)
- **CSIR** (where the 104 new cells are):
  - crack IoU without noisy 0.475 → 0.484 (+0.009, thr 0.011, n.d.);
  - inactive 0.707 → 0.758 (n.d.; 3 cells);
  - CSIR crack AP 0.607 → 0.619.
- **ARTS control** (3 new cells): crack 0.456 → 0.483, **+0.027 vs thr 0.023**. That is "better" by the arithmetic, which I did not expect; it is descriptive only (13 test cells, 1 of 6 secondaries).
- **BMRK control:** crack 0.379 → 0.382; recall 0.516 → 0.515; AP 0.462 → 0.467 (all n.d.). BMRK inactive +0.011 (thr 0.010) passes the per-source arithmetic (MC).
- **Post hoc leads only:** both per-source passes (ARTS crack, BMRK inactive) are post hoc contrasts, not findings.
- **Dead cell (17)**, newly in training from 5 cells:
  - test FP px per seed: 85, 5,548, 357, 414, 0;
  - mean about 1,280, mostly on CFVS (1,181 px mean on CFVS cells);
  - dead cell is absent from test GT.
- **E1 ext:** crack 0.148 → 0.146, crack recall 0.178 → 0.166, inactive 0.064 → 0.070, mIoU 0.411 → 0.419. Without `CSIR_00300_r25_c1`, identical. Even 104 extra CSIR cells do not help on unseen CSIR modules.

## Per class (test without noisy)
- border 0.692 → 0.712, inactive 0.449 → 0.458, crack 0.474 → 0.475.
- material 0.411 → 0.402, edge_dark 0.306 → 0.257 (3 cells); gridline and splice unchanged.
- busbars (1 cell) 0.420 → 0.566.

## Readings
1. As predicted in the protocol, these labels add little: they are CSIR, where SUP100 is already strong.
2. A trend on CSIR and inactive (all point estimates positive) is plausible, but nothing passes, and all-class mIoU is flat.
3. Steps were matched, so each cell was seen about 18% less often (274 vs 335 epochs). A longer schedule with the extra cells would be a different rung.
4. The data lever that would matter (ARTS/BMRK crack coverage) is not what E-SCDD offers. Track D's labelled-set experiment speaks to that.
