# x4_ens_inference: out-of-fold 5-seed COMBO ensemble (builder kd, 28 Nov 2026)

E = measured, S = judgement. No training. Progress log: harness/x4/arms/BUILD_kd.md.

## Result (E)
Read kd_ens1: /home/noob/work/bench_reads/x4_kd_ens1 (verdict.txt md5 6ebe1e8a, read.json fa436014, read.txt 7215ba1c), tool bench_read_w1 fdb56b78 at bench_wt_final 89b9ea5, groups d880a769, 2,000 draws, M from the PF A/A in this read (relF1@2 0.0100, inactive 0.0462, mIoU-R13 0.0100).

| contrast, 532 cells, OP-A | relF1@2 | relP@2 | relR@2 | inactive IoU | mIoU-R13 | verdict |
|---|---|---|---|---|---|---|
| ENS - COMBO (no TTA; COMBO seeds 5 to 9) | +0.0075 [+0.0035, +0.0124] | +0.0094 [+0.0044, +0.0162] | +0.0060 [-0.0002, +0.0127] | +0.0110 [-0.0246, +0.0456] | +0.0063 [+0.0020, +0.0118] | SCREEN FAIL (NO LOSS), guards pass |
| ENS_D4 - COMBO_D4 (both with D4) | +0.0020 [-0.0013, +0.0060] | +0.0030 [-0.0016, +0.0076] | +0.0011 [-0.0039, +0.0076] | +0.0036 [-0.0216, +0.0330] | +0.0026 [-0.0011, +0.0080] | n.d. |
| ENS_D4 - COMBO (C2-style deployment against the x4 comparator) | +0.0075 [+0.0027, +0.0130] | +0.0129 [+0.0075, +0.0206] | +0.0031 [-0.0037, +0.0108] | +0.0204 [-0.0138, +0.0558] | +0.0069 [+0.0024, +0.0124] | SCREEN FAIL (NO LOSS), guards pass |

Levels (532 cells): relF1@2 COMBO 0.8629, COMBO_D4 0.8684, ENS 0.8704, ENS_D4 0.8704. 416 clean cells give the same picture (ENS - COMBO +0.0077 [+0.0028, +0.0138]). Only strict crack IoU passes (+0.0115), which decides nothing. False crack pixels on crack-free cells fall (65 vs 213), width ratio 0.993.

S: the ensemble's gain over one COMBO model is real but below the margin (+0.0075 < 0.010). It comes mostly from precision, and most of it is already captured by D4 alone (ENS_D4 over COMBO_D4 is +0.0020, n.d.). Inactive is not clearly better (interval -0.025 to +0.046). Under the lead's rule the distillation arm x4_enskd is therefore not built further (see x4_enskd.md). This agrees with E1, where C3 - C2 was -0.0025.

## What was dumped (E)
- Members per fold k: cv02 /tmp/noob_el/bench_03375d4/experiments/c3x_hrnet_swad_v11_f<k>_s{5..9}/checkpoints/latest.pth, key swad (the COMBO comparator readout). Members agree on model config and data.root; step 20,000.
- ENS = mean over the 5 members of their softmax probabilities (ensemble of averages, doi:10.52202/068431-0601; the members are SWAD averages). ENS_D4 = the same with each member's probabilities averaged over the 8 D4 views (bench/tta.py, the bench_infer D4 path). fp32, TF32 off, batch 8, eval transform, set order, pred = argmax p; m_crack, oth, p_crack, p_inact as bench_infer.py.
- Code: branch x4_kd 779e88b, scripts/bench_ens_infer.py (writer md5 410912bd), bench/ens.py; deploy cv02 /tmp/noob_el/bench_779e88b (CODE.md5 3cb37af4). Runner /tmp/noob_el/kd/kd_run.sh (lead's lane rule of 27 Nov), jobs q_ens/jobs.txt 14a0f12c; peaks 4,262 MiB (no TTA), 5,542 MiB (D4).
- Check I-ens (E): a 1-member ensemble (fold 0, seed 5, no TTA) vs the COMBO dump c3x_hrnet_swad_v11_f0_s5.swad: pred, oth, p_inact identical on 107 of 107 cells; m_crack differs in 68 px by at most one float16 step, p_crack by at most 1.8e-7 (GPU softmax per batch vs CPU softmax over the concatenated logits).
- Relayed to gaint (10 dumps, 1.3 GB): /home/noob/work/bench_relay/x4_ens/<run>/dumps/elbench1/x4_ens_mean/<run>/cv5v3_f<k>/, .ok markers in x4_ens/.ok, per-cell md5 verified on gaint, manifest md5 equal on both ends:

| run | manifest md5 | cells | MB |
|---|---|---|---|
| x4ens_mean_none_f0_s56789 | fcebd214922b5c3b5a408531b3b94271 | 107 | 128 |
| x4ens_mean_none_f1_s56789 | 65e30748594df278ed85398402791082 | 110 | 134 |
| x4ens_mean_none_f2_s56789 | c861d276cf41fdb1128b2a0d24453527 | 103 | 126 |
| x4ens_mean_none_f3_s56789 | 2ea4eabc2355cc252c93a877d1387423 | 101 | 123 |
| x4ens_mean_none_f4_s56789 | 5e29d4e662a63a62e05471ee9f29c7b1 | 111 | 134 |
| x4ens_mean_d4_f0_s56789 | 6063dc018a73aa79a78d40057918a528 | 107 | 126 |
| x4ens_mean_d4_f1_s56789 | 2a9ea557f82709a5a53a529d118660c1 | 110 | 132 |
| x4ens_mean_d4_f2_s56789 | 85a92fb8a824d05fb6c33422013ee1d8 | 103 | 124 |
| x4ens_mean_d4_f3_s56789 | bedb64a41c6f09c948018f4826e72a76 | 101 | 121 |
| x4ens_mean_d4_f4_s56789 | 8359838ec3b00381bc02d00691248760 | 111 | 132 |

- On cv02 only (not relayed): the 25 leave-one-out 4-member ensembles without TTA (x4ens_mean_none_f<k>_s<4 seeds>, about 3.1 GB, /tmp/noob_el/kd/dumps/elbench1/x4_ens_mean/). They are kept for the jackknife below; they can be deleted on request.

## What the read tool needs to treat an ensemble as one arm (E for the first three, S for the rest)
1. One record per fold: the ensemble's manifest seed is a single pseudo-seed (56789 = member seeds joined), and run_id = folder name x4ens_..._f<k>_s56789. bench_read_w1 assembles per (arm, seed), so the arm has exactly one OOF record per stem and needs no change: `--arm 'ENS=<template with {k} {s}>:56789:swad'`.
2. Writer: read_x4.py refuses more than one writer. harness/x4/arms/kd/read_x4_ens.py (md5 e8876e23) is read_x4.py b012ccfb with one change, a `--writers` allowlist of exact manifest writer strings. The COMBO D4 dumps (queue fin) are written by another bench_infer.py (32e0b67c), so the same allowlist is needed for any COMBO_D4 comparison. Device, precision, step, set and the relay .ok checks are unchanged and pass.
3. Launcher used: harness/x4/arms/kd/kd_read_ens.sh <tag> (arms COMBO and COMBO_D4 seeds 5 to 9, ENS and ENS_D4, PFAA 5 to 8; pairs COMBO=ENS, COMBO_D4=ENS_D4, COMBO=ENS_D4).
4. The interval, honestly. The ensemble arm has no seed replicate. In boot_pair its per-fold seed draw always picks the same record, so the 95% interval covers module-group resampling plus the single model's seed noise (the COMBO side draws one of its 5 seeds per fold), but **not** the ensemble's own member-sampling noise (which 5 seeds were trained). It is therefore somewhat too narrow. Proposal: (a) jackknife over members with the 5 leave-one-out ensembles already dumped: Var_J = (4/5) * sum_i (theta_(-i) - mean theta_(-i))^2 on the pooled OOF metric, total SE = sqrt(SE_boot^2 + Var_J), CI = delta +- 1.96 SE; (b) compare against the ensemble's own members (COMBO seeds 5 to 9, as done here), so delta = ensemble minus the average member; (c) a real replicate needs a second, disjoint 5-seed ensemble (25 new COMBO runs), so any confirmation would have to be planned that way. Not computed here, because the point estimate (+0.0075) is already below M, so the extra variance cannot change the verdict.
5. D4 confound: compare ENS with COMBO and ENS_D4 with COMBO_D4. ENS_D4 against plain COMBO mixes two effects.

## Model Stock (dropped by the lead, 27 Nov)
Not an arm. E: train.py seeds the model build with the run seed, so the decoder and head of the 5 seeds start from different random inits. Their weights are unrelated: mean pairwise cosine 0.001 over 68 tensors (9.8M params), against a median of 0.49 for the encoder deltas from ImageNet. Model Stock needs a shared pretrained anchor, which only the encoder has. The fold-0 merge (encoder by Model Stock, t median 0.83; decoder uniform mean; BN re-estimated on the 425 training cells) agreed with the ensemble on only 67.6% of pixels and predicted 0 crack pixels. Its dumps were deleted on cv02 and never relayed.
