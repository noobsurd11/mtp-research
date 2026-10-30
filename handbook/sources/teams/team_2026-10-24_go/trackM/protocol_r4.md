# Protocol R4: + 107 leakage-free E-SCDD labelled cells (585 train cells), 100% labels

MD, 24 Oct 2026. Status: **APPROVED by MC** (`review_r4.md`). Launch after the `el_mt4` identity check is IDENTICAL and recorded.

## What I had seen when writing this
- M0 (APPROVED) and R1 (VERIFIED).
- MC's `data_addendum.md`, with its eligible list `mc_data/escdd_extra_train_eligible.tsv` (107 cells: 104 CSIR, 3 ARTS) and MC's mapping ruling (24 Oct): 29 → 1, 24 → 2, 25-28 → ignore.
- No R4 run exists. No wave-1 result had been opened when this was written.

## Question
Does adding the 107 extra labelled cells, all real and leakage-free, to the 478 train cells raise test scores? The cells add about 12% crack px and 14% inactive px, almost all CSIR.

## Hypothesis
- Labels are the largest lever measured (5 → 100%: +0.17 crack IoU). But these cells are CSIR, where SUP100 already scores best without the noisy cell (crack 0.475).
- Expected (S): pooled crack +0.00 to +0.01, CSIR inactive and crack slightly up; BMRK/ARTS/CFVS unchanged.
- The informative readouts are CSIR per source and E1 ext, which is 101/106 CSIR from unseen modules.

## The one change: the training set (478 → 585 cells)
**Data root `/tmp/noob_el/data_r4`** (cv02), built 24 Oct:
- `labeled/images` and `labeled/masks_escdd`:
  - symlinks to the shared 582 images and `masks_escdd` (unchanged files);
  - plus the 107 new images (E-SCDD bytes, copied unchanged) and masks (mapped below).
  - 689 files each.
- `splits/train.txt`: the 478 original lines, byte-identical (md5 of the first 478 lines = md5 of the original, `842f27c4...`), then the 107 stems.
- `val.txt` and `test.txt` are md5-identical to `el_p7/data/splits` (`9dcccf00...`, `a31fad14...`).
- `escdd_masks` (val/test scoring), `masks_coded` and `unlabeled` are symlinks to the originals.
- No name collides between the 107 and the 582.
- Spot md5 of 3 shared images (`ARTS_00001_r6_c2`, `CFVS_00006_r5_c5`, `CSIR_00070_r8_c4`): identical to `el_p7`.
- Build script: `scripts/m4_build_r4.py` (laptop, `-I`). File list md5: `r4_build/data_extra/md5.txt`, verified on cv02 after transfer. Tarball md5 `e879d576...`.

**Mask mapping** (MC ruling): E-SCDD ids 0-23 unchanged; 29 sp multi halfcut → 1 sp multi; 24 sp mono halfcut → 2 (none present); 25 scuff, 26 corrosion cell, 27 brightening and 28 star → **255 = ignore**.

| class | cells / px before | cells / px after |
|---|---|---|
| 1 sp_multi | 27 / 231,548 | 74 / 955,175 |
| 11 inactive | 10 / 39,509 | same |
| 14 crack | 48 / 27,016 | same |
| 17 dead_cell | 5 / 192,662 | same (absent from our test; it enters training) |
| 25 scuff | 12 / 7,355 | → 255 |
| 26 corrosion cell | 13 / 62,697 | → 255 |
| 27 brightening | 13 / 109,829 | → 255 |
| 28 star | 2 / 135 | → 255 |
| **255 ignore** | – | **32 cells / 180,016 px** (0.64% of the 107 cells' px) |

Full table: `r4_build/data_extra/class_hist.tsv`.

**Grey conversion.**
- The 107 images are RGBA, 55 of them with colour. They go through the same loader call as our images (PIL `convert("L")`).
- Check on the 577 cells shared by E-SCDD and our 582: 576 are grey-identical after `convert("L")`.
- The exception is `CSIR_00062_r5_c4` (train), which differs at 261,022 px (max diff 255): E-SCDD's file is a different image or orientation. It does not matter here, because our runs use our own file for all 582. It is reported to MC as a data note.

**Ignore switch.** `data.mask_ignore_value=255` (`el_m` commit `0642889`, opt-in, default off):
- `load_index_mask` accepts that one extra value; other out-of-range ids are still rejected;
- class counts skip it;
- val/test masks stay strict;
- supervised runs only.

`ce_dice` already uses `ignore_index=255` for CE and masks both p and y of every Dice term (`vf`). Tests in `tests/test_m_ignore.py` (5) check:
- the default path rejects 255;
- with the switch, 255 is accepted and not counted;
- loss and gradient do not depend on logits at ignored px, for CE and the 12-class Dice;
- the label-safe augmentation (resize at 512, flips, rot90; no rotation fill) preserves the 255 count and every class histogram, over 20 random draws;
- the dataset passes the switch.

Full suite: 232 passed, 11 skipped.
- **Identity:** the SUP100 config at `el_mt4` (`0642889`, switch off), 1,000 steps vs `p16_A_100pct_s3`. Result in `identity_check.txt` before launch.
- **Steps matched, not epochs:** with 585 cells each cell is seen about 18% less often (20k × 8 / 585 ≈ 274 epochs vs 335).

## Fixed (identical to SUP100)
U-Net++/ResNet-34 ImageNet, CE + Dice (crack, inactive), labelsafe, batch 8, 20k steps, Adam 1e-3, wd 1e-4, cosine, clip 1.0, bf16, deterministic. Final weights.

## Arms
| Arm | Runs | Seeds | Code |
|---|---|---|---|
| SUP100 | existing (M0) | 0-4 | identity-checked |
| R4 | `m_r4_extra107_s0..4` | 0-4 | cv02 `/tmp/noob_el/el_mt4` (REVISION `0642889`) |

**Opts:** the SUP100 opts + `data.root=/tmp/noob_el/data_r4 data.mask_ignore_value=255`.

## Decision
As protocol_r2: rule 1, 5 v 5, 4 primaries, on all 50 and without the noisy cell.
- **Pass** if a primary passes in both sets, or passes in one and is n.d. with the same sign in the other.
- **Worse** on any primary in either set fails.
- Stack inclusion is decided on val only (C1). Multiplicity: 8 tests.

**E1 independence (MC):** the 107 share one module with one E1 cell. E1 `CSIR_00300_r25_c1` (0 crack, 0 inactive px) shares module CSIR_00300 with 7 of the 107. Image correlation against all 106 E1 cells peaks at 0.675 (twins score 0.93+), so E1 stays unseen. E1 is reported with and without that cell.

**Controls and extra reports (MC):**
- BMRK and ARTS crack IoU are controls: no gain is expected there.
- dead_cell (17) FP px on test, since it now enters training from 5 cells.
- Epochs: 274 vs 335 (steps matched).
- Peak memory with `=mq4` beside `=mq`.

**Named secondaries:** CSIR crack and inactive IoU (with and without the noisy cell); E1 ext crack IoU, crack recall and inactive IoU (101 CSIR cells; the most relevant readout for this data).

**Reported:** every M0 cell set, per source with FP px of subset-absent classes, per class, crack capture, bootstrap, leave-top-3-out.

## Compute
- 5 runs at about 1.1-1.5 GPU-h each.
- cv02, in the Track M lanes after wave 1 frees slots (a second lane session on `el_mt4`, `=mq4`). Ledger before launch.

## Not claimed
- That more labels from other sources would behave the same. These cells are CSIR.
- Anything about the ignored classes 25-28. They are neither learned nor scored.
