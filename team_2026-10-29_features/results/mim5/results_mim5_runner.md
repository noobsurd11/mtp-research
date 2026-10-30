# MIM5 vs A5c-f1: runner's analysis (pending coach's independent recompute)

runner, 30 Oct 2026 02:42 IST. Protocol `protocol_mim5.md` v1.1. Test opened once for this experiment (A5c-f1 x5 + MIM5 x5, 30 Oct ~02:40 IST). **Coach CONFIRMED 30 Oct (verify_mim5.md §5-6): n.d. on all three primaries in both sets, closed; AM KILL.**

## Inputs (E)
- gaint `el_f1/reports/f1/post`, pulled to `results/mim5/raw/`; MANIFEST.md5 50 files, `md5sum -c` OK on the laptop.
- m0 JSONs: 10 runs, step 20,000, code_revision 603e0d5, final weights; sets val / test / ext.
- MIM5 encoder: all 5 runs logged md5 1c3df959 = `encoder_final.md5` (`raw/encoder_init_check.txt`).
- tau 0 per-cell == default per-cell for all 10 runs (`raw/tau0_check.txt`).

## Primaries, rule 1 (divisor 3), `m2_rung_mim5.txt`
| set | metric | A5c-f1 | MIM5 | Δ | thr /3 | verdict |
|---|---|---|---|---|---|---|
| all 50 | crack IoU | 0.3002±0.0053 | 0.2886±0.0153 | −0.0116 | 0.0186 | n.d. |
| all 50 | inactive IoU | 0.2791±0.0392 | 0.2297±0.0923 | −0.0495 | 0.1158 | n.d. |
| all 50 | crack relF1@2 | 0.7136±0.0125 | 0.6995±0.0222 | −0.0141 | 0.0295 | n.d. |
| −noisy 49 | crack IoU | 0.3024±0.0054 | 0.2907±0.0153 | −0.0118 | 0.0187 | n.d. |
| −noisy 49 | inactive IoU | 0.2901±0.0405 | 0.2388±0.0957 | −0.0513 | 0.1200 | n.d. |
| −noisy 49 | crack relF1@2 | 0.7175±0.0127 | 0.7032±0.0222 | −0.0143 | 0.0295 | n.d. |

- /5 thresholds (descriptive, all 50): crack 0.0144 (0.01443 from unrounded sds; coach), inactive 0.090, relF1 0.0228: all n.d.
- P-series cross-check (`ssl_rules_mim5.txt`, rescore JSONs): same means, same three n.d.; width check relP@2 −0.011 ok.
- **Protocol outcome: n.d. on all three primaries in both sets → closed** ("continued MIM on this pool does not beat ImageNet init on EL at 5%"); no 100% arm.

## Reported (never change the verdict)
- Every delta is negative. Paired image bootstrap (all 50) B−A: crack IoU −0.0116 [−0.0181, −0.0043], inactive −0.0495 [−0.0921, −0.0021], relF1 −0.0141 [−0.0213, −0.0064], mIoU_rob −0.0063 [−0.0145, +0.0008]. Leave-top-3-out: crack −0.0067, inactive −0.0258. The bootstrap is over images with seeds fixed, so it does not carry seed variance; descriptive.
- MIM5 seed sd is about 3x A5c-f1's on crack IoU (0.015 vs 0.005) and 2.4x on inactive.
- −twins / −both: same signs, all n.d.
- mIoU_rob 0.424 vs 0.418 (n.d.). Crack P 0.628 → 0.614, R 0.365 → 0.353; inactive P 0.770 → 0.795, R 0.306 → 0.248.
- Per source crack IoU (A → MIM): ARTS 0.138 → 0.122 (rule-1 arithmetic WORSE, secondary), BMRK 0.154 → 0.154, CFVS 0.364 → 0.347, CSIR 0.333 → 0.324, SDLE (1 cell) 0.101 → 0.120. CFVS inactive 0.364 → 0.257.
- Val (Track M inclusion rule, descriptive here): crack 0.273 → 0.267 n.d., relF1 0.693 → 0.678 WORSE.
- LA secondary, tau 1 both arms (`m2_rung_mim5_tau1.txt`): A5c-f1+LA crack 0.3157, MIM5+LA 0.3050, Δ −0.0108 (thr 0.0164) n.d.; inactive −0.0485 n.d.; relF1 −0.0127 n.d.; same in −noisy.
- Yardsticks (cross-machine, descriptive): old A5c cv02 0.304 vs A5c-f1 gaint 0.300 (reproduced within 1 sd); A5c+LA cv02 0.319 vs A5c-f1+LA gaint 0.316.
- E1 ext 106 (secondary): crack IoU 0.041 → 0.031, crack recall 0.047 → 0.036, inactive IoU 0.029 → 0.040.

## AM check (protocol_am v0.1, val only): KILL (E, `raw/am_val.json`)
- Map AP 0.0166 vs val crack base rate 0.0027 (6.2x), but no θ reaches relaxed precision 0.5 (θ = None), so the recovered share is 0 for both groups (A5c-f1 missed 67-71 components per run, SUP100 20-27). Kill criteria met (no θ at 0.5; share < 0.05 for both). No inference-rule protocol follows.
- The after script's 'AM rc' line was not captured (relative log path bug); am.log has no Traceback and ends with this result.

## Files for coach
`results/mim5/raw/m0/f1_{A,MIM}_5pct_s{0..4}{.json,.tau0.json,.tau1.json}`, `raw/rescore/*.json`, `raw/la.json`, `raw/am_val.json`, `raw/MANIFEST.md5`.
