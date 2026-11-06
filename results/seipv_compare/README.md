# SEiPV-Net comparison: 24-class mIoU of our checkpoints (13 Oct 2026, descriptive, not a locked protocol)

**Why.** SEiPV-Net (Eesaar et al., Energies 2023, 16(23):7726) reports mIoU 0.8604, F1 0.9426, Dice 0.8531, IoU 0.7447 on the same 50 BenchmarkEL test cells (val 54, test 50; train 1,912 = likely 478 x 4 augmented). It averages over all 24 classes, gives no per-class numbers, does not define its averaging, and no code link was found.

**What.** Read-only CPU inference of 18 final checkpoints on gaint (script /home/noob/work/diag_seipv/miou24.py, copy here), code el_p13, checkpoints from /home/noob/work/cv02_noob_el. One 24x24 confusion matrix per test cell; old labels (20211104) and revised (E-SCDD, ids >= 24 mapped back to the old label). Teacher weights for Mean Teacher runs, as in the official rescore. Check: crack and inactive IoU reproduce the official rescore JSONs (e.g. p16_A_100pct_s4 crack 0.409 / 0.467 old / revised; BsM5 5-seed revised crack mean 0.333).

**Rules computed:** class mean over classes with GT or prediction (union, with and without background); class mean over classes present in test GT (16 classes on old labels); frequency-weighted IoU; pixel accuracy; macro Dice; pixel-weighted F1; per-image mean IoU with absent-and-unpredicted classes left out or scored 1.

**Results, old labels, mean over seeds** (L3 100%: 5 seeds; L3 10%: 3; A5c: 5; BsM5: 5)

| Group | mIoU union | mIoU GT classes | mIoU GT no bg | fw-IoU | pixel acc | macro Dice | weighted F1 | per-image, absent=1 | crack | gridline | inactive |
|---|---|---|---|---|---|---|---|---|---|---|---|
| L3 100% | 0.457 | 0.514 | 0.487 | 0.886 | 0.931 | 0.623 | 0.933 | 0.840 | 0.382 | 0.289 | 0.456 |
| L3 10% | 0.426 | 0.453 | 0.422 | 0.882 | 0.930 | 0.560 | 0.928 | 0.780 | 0.351 | 0.233 | 0.279 |
| A5c 5% | 0.384 | 0.384 | 0.349 | 0.875 | 0.928 | 0.471 | 0.921 | 0.733 | 0.274 | 0.160 | 0.242 |
| BsM5 5% | 0.391 | 0.391 | 0.357 | 0.872 | 0.925 | 0.478 | 0.920 | 0.806 | 0.294 | 0.188 | 0.349 |
| SEiPV-Net (paper) | mIoU 0.8604 | | | | | Dice 0.8531 | F1 0.9426 | | n/r | n/r | n/r |

Revised labels: L3 100% mIoU GT classes 0.545, weighted F1 0.931, per-image absent=1 0.848 (full table in miou24_all.json).

**Reading (descriptive).**
- SEiPV F1 0.9426 is close to our pixel-weighted F1 (0.933); their mIoU 0.8604 is close to our per-image mean with absent classes scored 1 (0.840). A plain class mean of the same model is 0.46 to 0.51. Their rule is not confirmed (no code).
- Pixel-weighted F1 moves only 0.012 from 5% to 100% labels (0.921 to 0.933): it is dominated by background and padding and does not measure defects.
- Per-class IoU of L3 100% (old labels): background 0.91, padding 0.99, frame edge 0.84, sp mono 0.77, sp multi 0.73, ribbons 0.63, corrosion 0.66, inactive 0.46, border 0.44, busbars 0.42, material 0.41, crack 0.38, edge dark 0.30, gridline 0.29; crack rbn edge and splice 0.

**Files.** miou24_all.json (per run, per label version: all rules, per-class IoU, GT and predicted pixel counts), miou24_all.log, miou24.py. Server copies in gaint /home/noob/work/diag_seipv/.
