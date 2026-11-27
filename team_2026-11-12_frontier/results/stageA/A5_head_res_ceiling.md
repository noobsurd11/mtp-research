# A5 head_res_ceiling (stage A, builder A5+A6, 14 Nov 2026)

Spec: `cards/T11_method_suite_spec.md` section A0, with the critic's fix (`cards/WAVE3_REVIEW.md` section 2, T11 row 1). Tags: E = measured here, S = judgement.

## 1. Reading rule (fixed before any number was computed)

Question: how much crack strict IoU, relF1@1, relF1@2 and width does a model lose only because it predicts at stride s (2, 4, 8) and is upsampled bilinearly?

Constructions (both computed; neither is a prediction of a real stride-4 model's score):
1. **Model side (spec A0).** For each W1-G PF run (house_r34_unetpp_pf_v11, seeds 5 and 6, folds 0 to 4, out-of-fold over the 532 cells): `z = avg_pool2d(logp, s)`, `z_up = bilinear(z, 512, align_corners=False)`, `pred = argmax z_up`, `m_crack = z_up[14] - max_{k != 14} z_up[k]`, `p_crack, p_inact = softmax(z_up)`. Written as derived dumps (bench/dumpfmt format, `derived_from` in the manifest) and read with the reviewed `scripts/bench_read_w1.py` (arms S1, S2, S4, S8; baseline S1; OP-A, OP-F, OP-W, two-stage bootstrap over 330 groups). S1 is argmax of the float16 `logp` (by construction byte-equal to `argmax logp`); its pixel difference from the fp32 dump `pred` is printed (A2 found 15 of 2.88 M px, 0 crack px).
   Limit (spec): pooling log-probabilities of a model trained at stride 1 is not a bound in either direction for a model trained at stride s.
2. **GT side, critic's fix: the stated lower bound of the ceiling.** Per cell, the v1.1 GT crack mask (ignore px set to 0) is average-pooled to stride s, upsampled bilinearly to 512, thresholded at t; t is swept over 0.05, 0.10, ..., 0.95 and the t with the best pooled crack strict IoU over the 532 cells is reported, with relF1@1, relF1@2, relP@2, relR@2 and width ratio at that t. A perfect stride-s head can reach at least this IoU (S: it is one fixed reconstruction; a learned head can do better).
3. **GT side, spec's one-hot ceiling.** One-hot GT (24 classes; ignore px all zero) pooled and upsampled the same way, argmax with ties to the GT class, scored against GT: crack IoU, relF1@1/2, width ratio, component recall, inactive IoU, mIoU-R13, gridline IoU; per source.

Spec's bands, kept as printed bands (fixed now; the critic removed their power to bar anything):
- s = 4 minus s = 1 (model side, OP-A, pooled over seeds) loses >= 0.05 strict crack IoU or >= 0.02 crack relF1@2: "head binds". Every stride-4 row is then printed with the s = 4 ceiling numbers beside it.
- s = 4 loses < 0.01 on both: "head does not bind".
- In between: "printed, no rule".
- **Critic's fix (in force):** whatever the band, the result is printed beside the stride-4 rows and **bars nothing**: a stride-4 row that passes the standard rule (delta >= M, interval above 0, present at OP-A and OP-W, width ratio 0.85 to 1.15 x PF) is a candidate like any other.
- Y8: W1-G is the exploration set; the same script, unchanged, is run on the W1-C1 dumps (cv02, PF v1.1, seeds 5 and 6, arms S1 and S4 only) and the band is called a result only if it is the same there.

## 2. Numbers (all E unless marked S)

Code: `/home/noob/work/bench_wt_a` branch bench_a commit 926fd6b (`bench/headres.py` 4010608e, `scripts/bench_headres.py` e0066108, 12 tests; full pytest 517 passed, 4 skipped). Driver `/home/noob/work/bench_reads/stageA/headres/run_a5.sh` (076e80ff), 05:49:58 to 05:56:52, CPU only, 8 workers. Inputs: the 10 W1-G PF manifests (md5s printed in `run_a5.log`, e.g. f0 s5 7a7ae243) and W1-C1 PF seeds 5, 6 via `bench_reads/stageA/links/w1c`. Outputs: `/home/noob/work/bench_reads/stageA/headres/` (`report/headres.txt` b65b7d3c, `headres.json` 3c8ed4d5, `gt/gt.json` 577a6109, `read_w1g/read.json` 986a96fd, `read_w1c1/read.json` 6d12466a).

S1 check: argmax of the float16 `logp` differs from the fp32 dump `pred` at 1,698 of 278.9 M px on W1-G (11 crack px) and 1,660 (7 crack px) on W1-C1; 0 ties written. S1 reproduces PF: crack IoU 0.3624, relF1@2 0.8417, inactive 0.4980, mIoU-R13 0.6117, identical to the W1-G first read to 4 decimals.

### 2.1 Model side, W1-G (532 OOF cells, seeds 5 and 6, mean over seeds)
| s | op | crack IoU | relF1@1 | relF1@2 | relP@2 | relR@2 | width ratio | comp. rec >= 20 px | inactive IoU | mIoU-R13 | gridline IoU |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | OP-A | 0.362 | 0.753 | 0.842 | 0.893 | 0.796 | 1.006 | 0.800 | 0.498 | 0.612 | 0.301 |
| 2 | OP-A | 0.328 | 0.711 | 0.805 | 0.900 | 0.728 | 0.827 | 0.713 | 0.498 | 0.603 | 0.245 |
| 4 | OP-A | 0.159 | 0.429 | 0.533 | 0.881 | 0.382 | 0.356 | 0.259 | 0.495 | 0.555 | 0.086 |
| 4 | OP-W | 0.279 | 0.615 | 0.717 | 0.820 | 0.638 | 1.015 | 0.555 | 0.473 | 0.563 | |
| 8 | OP-A | 0.023 | 0.074 | 0.105 | 0.726 | 0.057 | 0.066 | 0.010 | 0.478 | 0.442 | 0.006 |

Contrasts (two-stage group bootstrap, 95% CI):
- S4 - S1, OP-A: crack IoU **-0.203** [-0.229, -0.181]; relF1@2 **-0.309** [-0.382, -0.253]; relF1@1 -0.325; width -0.650; relP@2 -0.012 [-0.044, +0.010]; relR@2 -0.413; inactive -0.004 [-0.048, +0.041]; mIoU-R13 -0.056 [-0.062, -0.051].
- S4 - S1, OP-W (bias matched to S1's width): crack IoU -0.084 [-0.106, -0.065]; relF1@2 -0.124 [-0.172, -0.091]; width +0.009.
- S2 - S1, OP-A: crack IoU -0.034 [-0.046, -0.023]; relF1@2 -0.037 [-0.053, -0.026]; at OP-W -0.013 / -0.018.
- S8 - S1, OP-A: crack IoU -0.340; relF1@2 -0.737.
- Per source, s = 4 at OP-A, crack IoU: ARTS 0.001 (S1 0.296), BMRK 0.233 (0.397), CFVS 0.167 (0.369), CSIR 0.118 (0.335), SDLE 0.142 (0.301). ARTS labels are the thinnest (1.5 px, BRIEF 2) and vanish first.

### 2.2 Model side, W1-C1 confirmation (cv02, seeds 5 and 6, S1 and S4 only, same script)
S1 OP-A crack IoU 0.366, relF1@2 0.845; S4 0.160 / 0.539. S4 - S1 at OP-A: crack IoU **-0.206** [-0.233, -0.185]; relF1@2 **-0.306** [-0.377, -0.252]; at OP-W -0.082 / -0.121. Same band as W1-G.

### 2.3 GT side (no prediction; 532 cells, v1.1 strict GT)
| s | (a) lower bound: best t | crack IoU | relF1@1 | relF1@2 | width ratio | (b) one-hot: crack IoU | relF1@2 | width | inactive IoU | mIoU-R13 | gridline IoU |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.05 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| 2 | 0.45 | 0.822 | 0.979 | 0.986 | 1.003 | 0.830 | 0.984 | 0.915 | 0.978 | 0.945 | 0.948 |
| 4 | 0.30 | **0.521** | 0.894 | **0.955** | 1.365 | 0.359 | 0.760 | 0.456 | 0.906 | 0.819 | 0.619 |
| 8 | 0.20 | 0.323 | 0.680 | 0.803 | 1.851 | 0.064 | 0.229 | 0.100 | 0.837 | 0.607 | 0.148 |

(a) per source at s = 4, crack IoU: ARTS 0.352, BMRK 0.616, CFVS 0.509, CSIR 0.544, SDLE 0.389.

## 3. Outcome under the rule

- **Band: "head binds"** on W1-G (S4 - S1 at OP-A: crack IoU -0.203, relF1@2 -0.309) and the same on W1-C1 (-0.206, -0.306). Y8: reproduced, so it is a result. Per the spec, every stride-4 row (dlv3p_r34_pf, segformer_mitb2_pf, rift_b, pratt_dlv3p_wcec, ucf_dlv3_r50_pf, rift_b_paper, the UPerNet row) is printed with the s = 4 numbers beside it: model side OP-A 0.159 / 0.533, OP-W 0.279 / 0.717; GT lower bound 0.521 / 0.955.
- **Critic's fix in force: this bars nothing.** A stride-4 row that passes the standard rule at OP-A and OP-W inside the width band is a candidate like any other.
- How to read the two sides together (S): the GT lower bound says a stride-4 head is able to reach crack IoU 0.52 and relF1@2 0.95, both above what PF reaches at stride 1 (0.36 / 0.84), so stride 4 does not cap the score at the level the benchmark works at, provided the head learns to place a thin line and accepts about 1.36x width at the best IoU threshold. The model-side loss (-0.20) is the cost of pooling log-probabilities of a stride-1 model, which mostly erases thin cracks (width ratio 0.36, recall 0.38 at OP-A, precision unchanged); OP-W recovers about 60% of it (-0.08). So a stride-4 row that scores low on crack measures the head as trained, not a hard limit. Inactive is untouched at s = 4 (-0.004, interval spans 0) and mIoU-R13 loses 0.056 on the model side (gridline 0.30 to 0.09), so stride-4 rows should also be expected to lose gridline.
- Width watch for stride-4 rows (S): the GT lower bound reaches its best IoU at width ratio 1.36, outside the 0.85 to 1.15 band. A stride-4 row that only matches PF at a widened output fails the width guard; that guard is the one that decides, not this ceiling.

## 4. Not run yet

- W1-G seeds 7 and 8 (W1-G2, dumps about 10:30 on 14 Nov): adds seeds; the band cannot flip on these deltas (S). Command when the 10 dumps exist (new output folders, nothing overwritten):
  `cd /home/noob/work/bench_wt_a && P=/home/noob/work/el-fault-detection/.venv/bin/python && export CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=1 && O=/home/noob/work/bench_reads/stageA/headres && nice -n 19 $P scripts/bench_headres.py dumps --arm "PF=/home/noob/work/bench_dumps/w1g/elbench1/house_r34_unetpp_pf_v11:w1g_pf_v11_f[0-4]_s[78]" --strides 1,4 --dumps $O/dumps_w1g_s78 --workers 8 && nice -n 19 $P scripts/bench_read_w1.py --arm "S1=$O/dumps_w1g/elbench1/headres_s1:.*" --arm "S1=$O/dumps_w1g_s78/elbench1/headres_s1:.*" --arm "S4=$O/dumps_w1g/elbench1/headres_s4:.*" --arm "S4=$O/dumps_w1g_s78/elbench1/headres_s4:.*" --baseline S1 --labels v11 --workers 8 --out $O/read_w1g_s5678`
- W1-C1 seeds 7 to 9 and strides 2, 8 on cv02 dumps were not read (not needed for the band).
