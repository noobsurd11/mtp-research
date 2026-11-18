# W1-G first read (lead, 14 Nov 2026, 00:30 IST). Provisional: tools at bench_x3 69a60f5, before the w2a review

Source: gaint `/home/noob/work/bench_reads/w1g/{read,src_calib,dti,d0}/`, copies in `results/w1g_read/`. Arm = `house_r34_unetpp_pf_v11` (U-Net++ / ResNet-34, encoder-preserving fine-tune, label set v1.1), split cv5v2, out-of-fold predictions pooled over all 532 train + val cells, seeds 5 and 6, argmax. No sealed cell is in any number here. All E.

## Baseline under the new protocol (mean over 2 seeds, sd in brackets)
| Metric | Value |
|---|---|
| crack relF1@2 | 0.842 (0.001); relP@2 0.893, relR@2 0.796 |
| crack relF1@1 | 0.753 |
| strict crack IoU | 0.362 (0.003) |
| inactive IoU | 0.498 (0.007); precision 0.767 |
| mIoU over 13 robust classes | 0.612 (0.002) |
| crack components >= 20 px found | 0.800 (any hit 0.890); component precision 0.906 |
| predicted / ground-truth crack width | 1.006 |
| crack-free cells with >= 50 false crack px | 0.5% of 303 cells |

Per source (crack IoU / relF1@2 / relR@2): ARTS 0.296 / 0.830 / 0.726; BMRK 0.397 / 0.827 / 0.764; CFVS 0.369 / 0.857 / 0.829; CSIR 0.335 / 0.795 / 0.713. Mono cells 0.381 / 0.862, multi cells 0.292 / 0.795. Inactive IoU by source: CFVS 0.552, BMRK 0.469, CSIR 0.161, ARTS 0.
Reading (S): the legacy test set flatters the model (crack IoU 0.474 and relF1@2 0.881 there, 0.362 and 0.842 here on all 532 cells). Recall is the weak side everywhere (0.71 to 0.83 at precision 0.89 to 0.97). CSIR, the source of the unseen-module set, is the weakest source for crack and for inactive.

## What the three CPU analyses decide
1. **Operating point.** A cross-fitted crack bias (OP-F) moves recall +0.013 and precision -0.018; relF1@2 does not move (-0.0008). Argmax already sits at the F1 optimum. A bias is an operating-point choice, not a gain.
2. **dti_hysteresis: closed, no gain.** DTI minus bias at the cross-fitted point: relF1@2 +0.0003 [-0.0010, +0.0019], strict IoU +0.0006 [-0.0010, +0.0020]. Below any plausible margin. Ledger: VOID with this evidence.
3. **src_calib (per-source bias or morphology at inference): closed, no gain.** src_bias minus global bias: strict crack IoU -0.0015 [-0.0035, +0.0001], relF1@2 -0.0012 [-0.0032, +0.0004]; worse on CSIR (-0.0074 [-0.0138, -0.0032]); the fitted CSIR bias swings by 3 to 4.25 logits between folds. Per-source morphology is worse than argmax (relF1@2 -0.0094). So an output-side source correction cannot recover the source gap; `src_film` (source conditioning in training) loses its cheap supporting evidence and stays deferred as the wave 3 critic suggested.
4. **D0 placement: 0.604** of predicted crack skeleton points lie within 1 px of the dark ridge (labels: 0.495). The fixed reading puts this at the lower edge of the undecided band (0.60 to 0.75). Mean p(crack) is flat from the ridge to 1 px toward the label (0.41 to 0.42), so the model spreads its mass between ridge and label instead of committing. By source: ARTS 0.86 (on the ridge), CSIR 0.69, CFVS 0.54, BMRK 0.51. **Lead's ruling:** treated as "follows the jitter" (the 0.60 case): the placement arms keep their prior, in the critic's order (ridge_snap and soft_band_jml first; matched_crack_head only after its own pre-check). ARTS is the exception: predictions sit on the ridge there and the labels do not (0.73), which explains ARTS's low strict IoU (0.296) at the highest precision (0.967).

## Not yet available
Margin M (needs seeds 7 and 8: W1-G2 is training them on gaint, done about 09:00 on 14 Nov; cv02 seeds 7 to 9 are in the W1-C queue). Every "no gain" above rests on bootstrap intervals over 330 module groups, not on M.
