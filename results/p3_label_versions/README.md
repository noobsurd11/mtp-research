# P3 (EXPLORATORY, no locked protocol): does the label version change our conclusions?

Run: 10 Oct 2026, about 09:50 IST, gaint, read-only inference (`scripts_gaint/rescore_label_versions.py`). Final-step `latest.pth` of existing runs.
Labels: our `dataset_20211104` masks ("old") against E-SCDD masks ("new"; HuggingFace `snt-ubix/escdd`, MIT, built on BenchmarkEL `20221008` and described as having "refined pixel-level annotations").
The images are pixel-identical between versions (576/577 checked, `compare.py`).
Scored on our own test (50) and val (54) stems.

## How the labels differ (`compare.py`, `per_img.json`)
- E-SCDD contains 577 of our 582 images; 185 of them are in a different split there.
- 361 of the 577 masks are identical. 129 of the 281 crack images have a changed crack mask, including 34 of the 50 test images.
- Changed crack masks have a median 1.67× more crack pixels and are almost entirely within 2 px of the old labels (relaxed agreement 0.98 / 0.98).
- So this is a cleaning (dotted labels joined, widened), not an independent re-annotation. The census agent found the same in BenchmarkEL's own `20221008` release.
- Crack IoU between the two label versions: test 0.745, val 0.732, train 0.81. Inactive: 0.93–0.96.

## Same models, two label versions (crack, dataset-level; mean ± sd over 3 seeds)

| Split | Run | IoU old → new | AP old → new | relaxed P@2 old → new |
|---|---|---|---|---|
| test | SL-10% b8 | 0.304±0.005 → 0.355±0.005 | 0.492±0.004 → 0.527±0.001 | 0.73 → 0.77 |
| test | SL-100% b8 | 0.283±0.003 → 0.339±0.006 | 0.457±0.006 → **0.541±0.001** | 0.70 → 0.76 |
| val | SL-10% b8 | 0.228±0.006 → 0.292±0.007 | 0.348±0.010 → 0.427±0.005 | 0.66 → 0.70 |
| val | SL-100% b8 | 0.224±0.001 → 0.290±0.001 | 0.371±0.007 → **0.478±0.001** | 0.64 → 0.70 |

Single runs, same pattern: SL-20% b8 s0 test IoU 0.230 → 0.280; MT-20% s0 test IoU 0.270 → 0.325.
Inactive changes little: test IoU within ±0.03, val within ±0.002.

## Reading (exploratory; one labelled subset; E-SCDD's annotation provenance is not documented)
- **Label version alone moves crack IoU by +0.05 to +0.07 for every model.** That is larger than any SSL-against-supervised difference we have measured.
- **The label-count effect depends on the label version.**
  - Old labels: 10% beats 100% on test crack AP (0.49 vs 0.46).
  - Revised labels: 100% beats 10% (0.54 vs 0.53 on test; 0.48 vs 0.43 on val).
  - So part of the handoff finding "label count does not move BenchmarkEL" may be noise in the evaluation labels.
- **Caveats:**
  - The revised crack labels are wider, which flatters our over-predicting models, so the absolute IoU gain is partly a width effect.
  - The AP *ranking* change is the more robust signal.
  - Training still used the old labels.
