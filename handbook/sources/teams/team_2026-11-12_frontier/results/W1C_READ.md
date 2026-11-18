# W1-C read (lead, 14 Nov 2026, 05:35 IST): cv02 baselines, house vs PF, label-fix ablation, A/A margin

Source: gaint `/home/noob/work/bench_reads/w1c/{read,src_calib,dti,d0}/`, copies in `results/w1c_read/` (MD5.txt). Tools: reviewed merged tree `bench_wt_w2` c57508e (`bench_read_w1.py` b5c46550), run 04:40 to 04:54 by `harness/w1read/run_read_w1c.sh`. Inputs: the 45 W1-C runs trained on cv02 (RTX A6000) and relayed with equal checksums; split cv5v2, out-of-fold predictions pooled over all 532 train + val cells, argmax unless stated; every arm is scored on label set v1.1 (ignore px not scored). No sealed cell is in any number here. E = measured, S = judgement.

Arms: **PF** = `house_r34_unetpp_pf_v11` (U-Net++ / ResNet-34, encoder-preserving fine-tune, trained on v1.1), seeds 5 to 9. **HOUSE** = `house_r34_unetpp_v11` (same model, plain fine-tune, trained on v1.1), seeds 5, 6. **PFV1** = `house_r34_unetpp_pf` (PF trained on the old v1 labels), seeds 5, 6.

## 1. Baselines on cv02 (E; mean over seeds, sd in brackets)
| Metric | PF (5 seeds) | HOUSE (2 seeds) | PFV1 (2 seeds) |
|---|---|---|---|
| strict crack IoU | 0.365 (0.002) | 0.382 (0.001) | 0.365 (0.000) |
| crack relF1@2 | 0.844 (0.002) | 0.850 (0.000) | 0.843 (0.002) |
| crack relP@2 / relR@2 | 0.894 / 0.799 | 0.897 / 0.807 | 0.894 / 0.797 |
| crack relF1@1 | 0.756 | 0.767 | 0.755 |
| inactive IoU | 0.503 (0.012) | 0.522 (0.013) | 0.489 (0.035) |
| mIoU over 13 robust classes | 0.612 (0.001) | 0.609 (0.002) | 0.610 (0.003) |
| crack components >= 20 px found (any hit) | 0.886 | 0.888 | 0.885 |
| predicted / ground-truth crack width | 1.002 | 1.114 | 1.013 |
| crack-free cells with >= 50 false crack px | 0.8% | 1.8% | 0.7% |
| false crack px on crack-free cells (303 cells) | 357 | 732 | 324 |

Machine check (E): PF on gaint (W1-G, seeds 5, 6) read 0.362 / 0.842 / 0.498 / 0.612 for crack IoU / relF1@2 / inactive / mIoU; PF on cv02 reads 0.365 / 0.844 / 0.503 / 0.612. The two machines agree inside seed noise. Reads still never mix machines.

PF per source on cv02 (crack IoU / relF1@2 / relR@2): ARTS 0.301 / 0.821 / 0.719; BMRK 0.400 / 0.835 / 0.776; CFVS 0.371 / 0.859 / 0.831; CSIR 0.337 / 0.799 / 0.720. Mono 0.383 / 0.864, multi 0.293 / 0.791. Recall is the weak side on every source, as on gaint.

## 2. A/A null on cv02: the margin M (E)
PF seeds {5, 6} against {7, 8}, two-stage group bootstrap, argmax. M = max(0.01, 2 x SE).
| Metric | A/A delta [95% CI] | SE | M |
|---|---|---|---|
| strict crack IoU | -0.0028 [-0.0096, +0.0034] | 0.0033 | **0.010** |
| crack relF1@2 | -0.0017 [-0.0103, +0.0067] | 0.0043 | **0.010** |
| mIoU-R13 | +0.0018 [-0.0040, +0.0078] | 0.0030 | **0.010** |
| crack relR@2 | -0.0017 [-0.0147, +0.0112] | 0.0065 | 0.013 |
| crack relP@2 | -0.0016 [-0.0135, +0.0074] | 0.0051 | 0.010 |
| inactive IoU | +0.0214 [-0.0260, +0.0742] | 0.0252 | **0.050** |
| width ratio | +0.0070 [-0.0274, +0.0401] | 0.0173 | 0.035 |

- Stage A's calibration (`results/stageA/A1.md`, all 15 two-seed splits of the 5 seeds; review pending) agrees: 0 of 15 A/A splits would be promoted on any headline metric; M 0.010 / 0.010 / 0.049 / 0.010. The bootstrap is conservative (spread of A/A deltas is 0.5 to 0.7 of the bootstrap SE).
- **Inactive IoU cannot screen a trained arm at 2 seeds** (M 0.05; two identical recipes differ by +0.021 from seeds alone). This is the critic's finding Y1, now measured.
- **The cross-fitted F1 operating point (OP-F) is unstable**: the A/A difference there is -0.0118 [-0.0357, -0.0005] on crack IoU, with the fitted bias ranging from -0.5 to +3.0 between seeds and folds. OP-F is printed but decides nothing; decisions use argmax (OP-A) and the width-matched point (OP-W).

## 3. House recipe against PF (E; HOUSE minus PF, seeds 5 and 6 against PF's five)
| Metric | At argmax | At the width-matched point |
|---|---|---|
| strict crack IoU | **+0.0173 [+0.0107, +0.0241]** | **+0.0110 [+0.0028, +0.0187]** |
| crack relF1@2 | +0.0055 [-0.0034, +0.0135] | +0.0026 [-0.0065, +0.0109] |
| crack relF1@1 | +0.0105 [+0.0019, +0.0183] | +0.0070 [-0.0019, +0.0158] |
| crack relP@2 | +0.0030 [-0.0080, +0.0159] | +0.0150 [+0.0032, +0.0281] |
| crack relR@2 | +0.0074 [-0.0063, +0.0205] | -0.0071 [-0.0212, +0.0061] |
| inactive IoU | +0.0190 [-0.0304, +0.0873] | +0.0206 [-0.0281, +0.0887] |
| mIoU-R13 | -0.0030 [-0.0102, +0.0045] | -0.0033 [-0.0106, +0.0041] |
| width ratio | +0.112 [+0.064, +0.157] | -0.004 [-0.053, +0.041] |

- The plain fine-tune beats PF on strict crack IoU on the pool cells by more than M at both operating points; the screen flags it (a flag, not a result: HOUSE has 2 seeds).
- At argmax the house model draws cracks 11% wider (ARTS 24% wider, outside the 15% band), and it doubles false crack px on crack-free cells (732 against 357). After width matching (a crack bias of -1.0 to -1.75) every source is inside the band and +0.011 strict IoU remains, carried by precision.
- relF1@2, the headline tolerance metric, does not separate the two recipes (+0.003 to +0.006, inside M).
- Reading (S): on cells from known modules the plain fine-tune is the better crack segmenter by strict overlap; PF was adopted for its behaviour on unseen modules (the PF2 opening: E1 inactive IoU 0.05 to 0.24, test not distinguishable to a narrow gain on relF1@2; BRIEF.md, optimiser row). The two answer different questions. Ruling: PF stays the comparator of every arm (the deployable candidate is the PF ensemble, and wave 2a is built on it); HOUSE is a table row of its own; any arm that claims an in-distribution crack gain is also printed against HOUSE. The unseen-module instrument (U-dev, stage B3) is what can tell whether PF's transfer edge is real under the new protocol; this contrast raises its priority.

## 4. Label-fix ablation (E; PFV1 minus PF, both scored on v1.1)
strict crack IoU +0.0004 [-0.0058, +0.0069]; relF1@2 -0.0014 [-0.0099, +0.0064]; inactive IoU -0.0140 [-0.0690, +0.0362]; mIoU-R13 -0.0020 [-0.0081, +0.0038]; width +0.011 [-0.028, +0.049].
- Training on the corrected labels changes no pooled metric by a measurable amount at 2 seeds. The v1.1 fixes matter for what is scored (ignore px and corrected masks in the evaluation), not for what the model learns from 532 cells.
- Ruling (S): v1.1 stays the training and scoring label set (user's decision of 12 Nov); the benchmark text states that the training-side effect of the fix is within noise, with these intervals.

## 5. The three CPU analyses on cv02 dumps (E)
1. **src_calib: no gain, as on gaint.** Per-source bias minus global bias, strict crack IoU: PF +0.0003 [-0.0046, +0.0132], HOUSE -0.0026 [-0.0054, -0.0003], PFV1 -0.0017 [-0.0035, 0.0000]. Per-source morphology is not better than argmax on relF1@2 for any arm (PF -0.0091 [-0.0144, -0.0031], HOUSE -0.0023 [-0.0051, -0.0004], PFV1 -0.0025 [-0.0056, +0.0002]). Closed on both machines.
2. **dti_hysteresis: no gain, as on gaint.** DTI minus the bias point: relF1@2 +0.0011 [-0.0016, +0.0062] (PF), +0.0003 (HOUSE), +0.0006 (PFV1); strict IoU +0.0013 [-0.0010, +0.0049] (PF). Closed on both machines (ledger VOID stands).
3. **D0 placement: 0.606** of PF's predicted crack skeleton points lie within 1 px of the dark ridge (labels 0.495), against 0.604 on gaint. Same reading: lower edge of the undecided band; placement arms keep their prior.

## 6. What this changes (S)
- M for cv02 arms: 0.010 on crack IoU, relF1@2 and mIoU-R13; 0.013 on relR@2; inactive IoU only through count-based readouts or 5 seeds. Provisional until the stage A review passes `aa_calibration`.
- The benchmark rows now training on cv02 (tranche 1, seeds 5, 6) are read against PF (5 seeds) and printed beside HOUSE.
- Open for the gaint read (W1-G2, about 10:30): the same A/A on gaint for the wave 2a arms.
