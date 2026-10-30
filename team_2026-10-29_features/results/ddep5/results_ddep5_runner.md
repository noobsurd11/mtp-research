# DDeP5 vs A5c-f1: runner's analysis (pending coach's independent recompute)

runner, 30 Oct 2026 09:40 IST. Protocol `protocol_ddep5.md` v1. Test opened once for DDeP5 (scoring 09:13-09:28 IST; the A5c-f1 arm was already opened with MIM5). **Coach CONFIRMED 30 Oct (verify_ddep5.md): n.d. on all three primaries in both sets, closed.**

## Inputs (E)
- gaint `el_f2/reports/f2/post_ddep5` (`f2_post_gaint.sh` md5 1e06378b: the m0_audit copies d36f7438 / d77241bb, the same masks and ext117 as the MIM5 post), pulled to `results/ddep5/raw/`; MANIFEST.md5 30 files, `md5sum -c` OK on the laptop.
- m0 JSONs: 5 runs, step 20,000, code_revision 2751aa8, final weights. Disclosure: `el_f2/REVISION` was written on 30 Oct 08:46 IST, before scoring and after training (HEAD 2751aa8, 0 tracked files modified); every f2 run trained at this commit.
- A5c-f1 arm: `results/mim5/raw/m0/f1_A_5pct_s*.json` (603e0d5, verified by coach for MIM5). Sharing is valid: I1-f2 and CP λ 0 identity (identity_f1.txt §5); coach: the scoring path is code-identical between 603e0d5 and 2751aa8.
- Decoder init: all 5 runs logged "Decoder initialised ... 132 tensors, md5 dd786ff4" = `decoder_final.md5` (`raw/init_check.txt`).
- tau 0 per-cell == default for all 5 runs (`raw/tau0_check.txt`).

## Primaries, rule 1 (divisor 3), `m2_rung_ddep5.txt`
| set | metric | A5c-f1 | DDeP5 | Δ | thr /3 | verdict |
|---|---|---|---|---|---|---|
| all 50 | crack IoU | 0.3002±0.0053 | 0.3071±0.0042 | +0.0070 | 0.0100 | n.d. |
| all 50 | inactive IoU | 0.2791±0.0392 | 0.2872±0.0328 | +0.0081 | 0.0591 | n.d. |
| all 50 | crack relF1@2 | 0.7136±0.0125 | 0.7222±0.0079 | +0.0086 | 0.0170 | n.d. |
| −noisy 49 | crack IoU | 0.3024±0.0054 | 0.3098±0.0043 | +0.0073 | 0.0100 | n.d. |
| −noisy 49 | inactive IoU | 0.2901±0.0405 | 0.2985±0.0341 | +0.0084 | 0.0612 | n.d. |
| −noisy 49 | crack relF1@2 | 0.7175±0.0127 | 0.7268±0.0076 | +0.0092 | 0.0171 | n.d. |

- /5 thresholds (descriptive, all 50): crack 0.0100 (the floor; raw 0.0060), inactive 0.0457, relF1 0.0132: all n.d. The crack threshold is the 0.01 floor under both divisors.
- P-series cross-check (`ssl_rules_ddep5.txt`, rescore JSONs, p92_ mapping): same means, same three n.d.; width check relP@2 −0.024 ok (< 0.05).
- **Protocol outcome: n.d. on all three primaries in both sets → closed** ("a denoising-pretrained decoder does not beat a random decoder at 5% on EL"); no 100% arm.

## Reported (never change the verdict)
- Every primary delta is positive and small. Paired image bootstrap (all 50) B−A: crack IoU +0.0070 [+0.0014, +0.0125], inactive +0.0081 [−0.0241, +0.0547], relF1 +0.0086 [+0.0015, +0.0175], mIoU_rob −0.0045 [−0.0106, +0.0018]. Leave-top-3-out: crack +0.0068, inactive +0.0279. The bootstrap resamples images with seeds fixed (no seed variance); descriptive.
- Crack trades precision for recall: P 0.628 → 0.606, R 0.365 → 0.384; relP@2 0.893 → 0.869, relR@2 0.595 → 0.618; component recall 0.507 → 0.529, component precision 0.907 → 0.878. Inactive P 0.770 → 0.770, R 0.306 → 0.315.
- mIoU_rob 0.424 → 0.420 (n.d.); sp_multi IoU 0.738 → 0.695 (−noisy).
- −twins / −both: crack +0.0094 / +0.0099 (thr 0.0109 / 0.0111), relF1 +0.0149 / +0.0158: all n.d.; DDeP5 crack sd 0.002 there vs A5c-f1 0.009.
- Per source crack IoU (A → DDeP): ARTS 0.138 → 0.139, BMRK 0.154 → 0.161, CFVS 0.364 → 0.369, CSIR 0.333 → 0.343 (−noisy 0.355 → 0.369, rule-1 arithmetic BETTER, secondary), SDLE (1 cell) 0.101 → 0.150.
- Val (Track M inclusion rule, descriptive): crack 0.273 → 0.282 n.d., relF1 0.693 → 0.702 n.d., inactive 0.148 → 0.115 n.d.
- LA, tau 1 both arms (C2, `m2_rung_ddep5_tau1.txt`): crack 0.3157 → 0.3202, Δ +0.0045 (thr 0.0100) n.d.; inactive +0.0086 n.d.; relF1 +0.0046 n.d.; same in −noisy.
- Free-bias yardstick (C3, DDeP5 tau 0 vs A5c-f1+LA, `m2_rung_ddep5_C3.txt`): crack 0.3071 vs 0.3157, Δ −0.0086; relF1 −0.0010; inactive −0.0017. The DDeP crack gain (+0.007) is below the free logit bias (+0.0155 on A5c-f1), so it is not practically useful even if real.
  - `m2_rung_ddep5_C3.txt` prints "RUNG VERDICT: WORSE": that is the Track M mIoU_rob guard on this tau0-vs-tau1 yardstick (all 50: −0.0118 vs thr 0.0100; LA raises mIoU_rob on A5c-f1), not a protocol_ddep5 verdict (coach note). The file carries the same note in its first line.
- E1 ext 106 (secondary): crack IoU 0.041 → 0.040, crack recall 0.047 → 0.047, inactive IoU 0.029 → 0.040.
- Decoder-change diagnostic (protocol "free diagnostic", `scripts/f2_decoder_change.py`, `ddep5_decoder_change.json` md5 0ebb86cb; theta_init: DDeP5 = decoder_final.pth, A5c-f1 rebuilt as train.py l.242-243, rebuild deterministic, ImageNet encoder identical across seeds):
  - Relative L2 change of trainable decoder params, mean of 5 seeds: A5c-f1 0.970, DDeP5 0.974 (per module 0.55-1.00, same pattern in both arms). This is dominated by shrinkage: Adam with weight_decay 1e-4 over 20k steps leaves the decoder conv weights at 0.22-0.26 of their init norm (seed 0: |init| 61.5 random / 71.1 DDeP -> |final| 15.8 in both).
  - Cosine of the final decoder conv weights to the init (seed 0): DDeP5 vs the DDeP init 0.090 (vs a seed-0 random init 0.072); A5c-f1 vs its own random init 0.102 (vs the DDeP init 0.066). Fine-tuning keeps only a small trace of either init; the DDeP start is mostly overwritten, consistent with the pre-stated "lr 1e-3 for 20k steps may erase the pretraining" (S).

## Files for coach
`results/ddep5/raw/m0/f2_DDeP_5pct_s{0..4}{.json,.tau0.json,.tau1.json}`, `raw/rescore/*.json`, `raw/la.json`, `raw/init_check.txt`, `raw/MANIFEST.md5`; A arm `results/mim5/raw/m0/f1_A_5pct_s*`.
