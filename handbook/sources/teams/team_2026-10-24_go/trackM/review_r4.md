# MC review of `protocol_r4.md` (+107 leakage-free E-SCDD cells)

MC, 24 Oct 2026. **Verdict: APPROVED.** It may launch after the identity check on `el_mt4` (`0642889`, switch off) is IDENTICAL over 1,000 steps and recorded.

## Checks (E)
- **Code `3c1b72b..0642889`** (read on gaint): `load_index_mask` accepts exactly one extra value when `ignore_value` is set. The check is unchanged with None. `count_class_pixels` skips it; val/test datasets are built without it (strict); SSL methods raise an error. The default path is unchanged. CE `ignore_index=255` and the Dice masking are covered by `tests/test_m_ignore.py` (per MD; 232 passed).
- **Mapping:** follows my ruling. 180,016 px ignored (0.64% of the 107 cells' px); 29 → 1 adds 723,627 px of sp_multi. **Dead cell (17)** enters training from 5 cells (192,662 px). It is a valid class of our scheme and absent from test; report whether the model starts predicting it on test (FP px on absent classes).
- **E1 independence (new check, `scratchpad e1screen.py`, copied to `mc_data/`):**
  - The 107 share **1 module with 1 E1 cell** (of 71 E1 modules).
  - The high-pass image correlation of the 107 against all 106 E1 cells peaks at **0.675**. The 7 known twins score 0.93 to 1.00, and same-source non-twins have a median of 0.89.
  - E1 stays an unseen-module readout for R4. Name the one shared-module E1 cell in the results and report E1 with and without it.
- **Splits:** train 478 lines byte-identical, then the 107; val/test md5-identical; spot image md5 identical. Good.

## Data note: `CSIR_00062_r5_c4` (E: checked by MC; a P-series fact, not an R4 problem)
- Our `dataset_20211104` image for this **train** cell is a different, offset crop from E-SCDD's file: correlation ≤ 0.42 under all 8 dihedral transforms. Its mask (identical in `20211104`, E-SCDD and our `masks_escdd`) **fits E-SCDD's image, not ours**: the grid, spacing diamonds and padding line up only with E-SCDD's.
- So every P-series run, and every Track M arm, trains on a misaligned mask for this one cell. The mask holds background, class 3 (24,030 px) and belt mark 19 (4,701 px); **no crack and no inactive**. Expected impact: negligible.
- It affects all arms equally, so no contrast changes. Record it in handbook 03/17 as a data fact. MD's check found the other 576 shared images grey-identical.
- Visual: `mc_data/csir62.png` (ours | E-SCDD | mask).

## Notes
1. **Named secondaries:** agreed (CSIR crack and inactive, E1 crack and inactive). Add BMRK and ARTS crack as controls that should not move.
2. **Steps matched:** 274 vs 335 epochs, disclosed. If R4 is n.d., one reading is "fewer passes over the hard sources". Not testable without another arm; say so.
3. **Label quality:** `CSIR_00087_r10_c5_rf` and `CSIR_00087_r4_c4_rf` (fragmented crack) and the 1-px ARTS lines are kept, per the addendum. Report them in "Not claimed".
4. **Packing:** `=mq4` beside `=mq` on the same GPUs. Check peak memory: 4 lanes per GPU plus R4 must stay below what the A6000 holds, and stay clear of other users' GPUs (4 GB rule).
