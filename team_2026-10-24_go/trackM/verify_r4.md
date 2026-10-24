# MC verification of R4 (+107 leakage-free E-SCDD cells)

MC, 24 Oct 2026. **Verified: n.d. on all four primaries in both cell sets, none worse. Val inclusion: EXCLUDE.** Recomputed with `mc_verify/mc_rung.py` from `r4/m_r4_extra107_s0..4.json`.
- MD5 OK against `r4/md5_cv02.txt`.
- Step 20000 and code `0642889` for all 5 runs.
- Comparator: SUP100 from `m0/`.

## Rule 1, 5 v 5 (test)
| set | crack IoU | inactive IoU | relF1@2 | mIoU_rob |
|---|---|---|---|---|
| all 50 | +0.0065 (thr 0.116) n.d. | +0.0111 (0.019) n.d. | +0.0094 (0.156) n.d. | +0.0029 (0.019) n.d. |
| without noisy | +0.0010 (0.0100) n.d. | +0.0085 (0.018) n.d. | +0.0012 (0.0100) n.d. | −0.0032 (0.013) n.d. |

- **Bootstrap without noisy:** crack +0.0010 [−0.0026, +0.0065]; inactive +0.0085 [−0.0054, +0.0280]; mIoU −0.0032 [−0.0092, +0.0040].
- **Width flags:** none. Precision changes are between −0.001 and +0.012.
- **Val:** crack +0.0044, relF1 +0.0026, mIoU_rob +0.0050, all under 0.0100. So **EXCLUDE.**

## Descriptive (no verdict)
- **Per source** (all 50):
  - ARTS crack +0.027 (thr 0.023) and BMRK inactive +0.011 (thr 0.010) pass the arithmetic. These are post hoc per-source contrasts; read them as leads at most.
  - CSIR crack +0.006 (thr 0.26 on all 50; that sd comes from the noisy cell).
- **Noisy cell:** s0 fails on it (57,152 crack px); the others predict 0 to 188 px.
- **Dead cell FP on test** (class 17, absent from test GT, now in training): 85 / 5,548 / 357 / 414 / 0 px per seed.
- **E1 ext** (106 unseen-module cells): crack IoU 0.148 → 0.146, crack recall 0.178 → 0.166, inactive 0.064 → 0.070. Identical without `CSIR_00300_r25_c1`.

## Reading
- 107 mostly-CSIR cells (+12% crack px) do not move the 100% model on test, nor on the 101 CSIR cells of E1.
- This fits C's Track D result that added crack px predicts the gain: these cells add little crack, and in the wrong source.
- More labelled data remains the main lever for BMRK and unseen modules, but it would have to be new BMRK-like or unseen-module labels. That is a user decision.
