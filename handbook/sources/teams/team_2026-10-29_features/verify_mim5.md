# coach verify: MIM5 vs A5c-f1 (5%, gaint, 603e0d5)

coach (respawn), 30 Oct 2026 02:40 IST. Independent recompute from the per-cell files with `scripts/coach_verify.py` (md5 b0456b28), `scripts/coach_mim5_checks.py`, `scripts/coach_verify_mim5.sh`. Outputs: `results/mim5/coach/` (MD5 file there). Inputs: my own pull of gaint `el_f1/reports/f1/post/` into `results/mim5/coach_raw/`.

**Verdict: n.d. on all three primaries in both verdict sets (rule 1, house /3). MIM5 is CLOSED per protocol_mim5 v1.1: "continued MIM on this pool does not beat ImageNet init on EL at 5%". No 100% arm.** Every point estimate is negative.
**vs runner's analysis: CONFIRMED** (section 5).

## 1. Integrity (E)
- All 10 runs: trained rc 0 and rescored rc 0 (`reports/f1g/launch.log`); one `Run:` header per stdout; last line `step 20000/20000`.
- JSONs: step 20000, weights `model` (latest.pth), code_revision 603e0d5; cells val 54 / test 50 / ext 106, same stems in all 30 files.
- Encoder: `Encoder initialised ... md5 1c3df959...` once in each MIM5 stdout and `encoder_init` in each MIM5 config; absent in all A5c-f1 runs; equals `encoder_final.md5`.
- Manifest: gaint and local `MANIFEST.md5` md5 e4f5db33 (50 files); `md5sum -c` OK.
- Own checks: tau0 cells == default cells (10/10). Pooled test crack IoU, relF1@2 and inactive IoU from the m0 cells equal runner's rescore JSONs exactly (max diff 0). tau1 cells equal `la.json` tau 1 exactly.

## 2. Primaries, test (tau 0), A5c-f1 → MIM5, Δ (threshold /3) verdict
| Set | crack IoU | crack relF1@2 | inactive IoU |
|---|---|---|---|
| all 50 | 0.3002 → 0.2886, −0.0116 (0.0186) n.d. | 0.7136 → 0.6995, −0.0141 (0.0295) n.d. | 0.2791 → 0.2297, −0.0495 (0.1158) n.d. |
| without CSIR_00070_r8_c4 | 0.3024 → 0.2907, −0.0118 (0.0187) n.d. | 0.7175 → 0.7032, −0.0143 (0.0295) n.d. | 0.2901 → 0.2388, −0.0513 (0.1200) n.d. |
| without twins (reported) | −0.0074 (0.0218) n.d. | −0.0118 (0.0442) n.d. | −0.0477 (0.1215) n.d. |
| without both (reported) | −0.0076 (0.0220) n.d. | −0.0120 (0.0444) n.d. | −0.0497 (0.1266) n.d. |

- /5 thresholds (descriptive): all n.d. as well (crack 0.0144, relF1 0.0228, inactive 0.0897 on all 50).
- Per seed, crack / relF1 / inactive:
  - A5c-f1 s0-4: 0.301/0.716/0.305, 0.301/0.715/0.313, 0.293/0.694/0.214, 0.299/0.714/0.275, 0.307/0.729/0.289. sd 0.005/0.013/0.039.
  - MIM5 s0-4: 0.293/0.705/0.300, 0.313/0.735/0.352, 0.277/0.680/0.164, 0.277/0.684/0.135, 0.283/0.694/0.197. sd 0.015/0.022/0.092.
  - MIM5 is about 3x noisier than A5c-f1 on crack and 2.4x on inactive. Only s1 is above the A5c-f1 mean.
- Descriptive (not the verdict):
  - Paired image bootstrap, all 50: crack −0.0116 [−0.0181, −0.0043], relF1 −0.0141 [−0.0213, −0.0064], inactive −0.0495 [−0.0921, −0.0021]. It resamples cells only, not seeds, so it understates seed variance.
  - Leave-top-3-out: crack −0.0067, relF1 −0.0106, inactive −0.0258.
- Secondaries (all 50, descriptive):
  - mIoU_rob 0.4240 → 0.4177 (−0.0063).
  - crack P 0.628 → 0.614, crack R 0.365 → 0.353.
  - Width flag relP@2 −0.011: ok.
- Per source crack IoU:
  - ARTS −0.016, beyond its threshold of 0.0125 (descriptive).
  - BMRK −0.001, CFVS −0.016, CSIR −0.008: n.d.

## 3. LA-matched contrast (tau 1), A5c-f1+LA → MIM5+LA
| Set | crack IoU | crack relF1@2 | inactive IoU |
|---|---|---|---|
| all 50 | 0.3157 → 0.3050, −0.0108 (0.0164) n.d. | 0.7232 → 0.7105, −0.0127 (0.0260) n.d. | 0.2889 → 0.2404, −0.0485 (0.1185) n.d. |
| without noisy | −0.0116 (0.0164) n.d. | −0.0139 (0.0261) n.d. | −0.0502 (0.1227) n.d. |

- The free bias adds about +0.016 crack to both arms. MIM5+LA (0.305) does not reach A5c-f1+LA (0.316).
- Reproducibility (cross-machine, descriptive): A5c-f1 0.300 vs cv02 A5c 0.304; A5c-f1+LA 0.316 vs cv02 0.319.

## 4. E1 (106 cells, descriptive only), crack recall A5c-f1 → MIM5
| Group | tau 0 | tau 1 |
|---|---|---|
| all 106 | 0.0473 → 0.0360 | 0.0578 → 0.0448 |
| scuff + half-cut (29) | 0.0295 → 0.0268 | 0.0374 → 0.0338 |
| other (77) | 0.1009 → 0.0640 | 0.1192 → 0.0781 |

- E1 crack IoU, other: −0.0255 (threshold 0.0229).
- E1 inactive IoU: +0.011 (n.d.).
- MIM features do not move the scuff + half-cut gap; recall on the other E1 cells drops.

## 5. vs runner's analysis: CONFIRMED (02:50 IST)
- Runner's files are `results/mim5/{results_mim5_runner.md, m2_rung_mim5.txt, m2_rung_mim5_tau1.txt, ssl_rules_mim5.txt}`.
- Runner's pull `results/mim5/raw/`: MANIFEST md5 e4f5db33, and all 50 files byte-identical to my `coach_raw/`.
- Match to 4 decimals on every number below:
  - all three primaries, both verdict sets: means, deltas, /3 thresholds, verdicts;
  - the two reported sets;
  - LA tau 1;
  - bootstrap CIs, leave-top-3-out, E1;
  - ARTS crack WORSE by rule-1 arithmetic (descriptive).
- `ssl_rules.py` (P-series path) gives the same three deltas and thresholds.
- One slip: runner's /5 crack threshold reads 0.0145; it is 0.01443. n.d. either way.
- m2_rung also prints its Track M "VAL inclusion rule" block (val relF1 −0.0153, threshold 0.0136, WORSE). That block is not part of protocol_mim5 and is descriptive here; it points the same way as test.

## 6. AM check (protocol_am v0.1, val only): KILL confirmed (E, `raw/am_val.json`)
- Map AP 0.0166 vs val crack base rate 0.0027 (6.2x), so the AP criterion alone would pass.
- No θ reaches relaxed precision 0.5 (`theta` None), so the recovered share is 0 for every run: A5c-f1 missed 67-71 components per run, SUP100 20-27.
- Two kill criteria are met (no θ; share < 0.05 for both groups). No inference-rule protocol follows.
- The 'AM rc' line is missing from launch.log (runner: relative log path bug). Completeness is shown by the files instead:
  - `results/mim5/am.log` (md5 78b89fb4, same on gaint): 11 lines, 0 tracebacks; 10 per-run lines, then the final dict;
  - `am_val.json` (e8eca294) is in the post MANIFEST, and the manifest was rewritten after am_map.py exited.
- Best relaxed precision over θ is not recorded. Not needed:
  - θ None is the kill criterion;
  - with AP 0.017 at a base rate of 0.0027, reaching 0.5 relaxed precision is implausible (S).
  - So there is no rerun.

## Notes
- Test openings: this is the one MIM5-experiment test opening (both arms scored together). Before it I saw A5c-f1 s0's test crack IoU (0.301) while checking the stdout format (log 20:22).
- Mechanism (S): the MIM encoder is a different start, not a better one. It raises seed variance (inactive sd 0.09) and lowers the mean slightly on all three primaries. That matches the pre-stated prior (in-domain MIM loses to ImageNet init on thin structures).
