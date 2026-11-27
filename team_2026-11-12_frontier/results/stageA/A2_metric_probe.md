# A2 metric_validity_probe (stage A, builder A2, 14 Nov 2026)

Spec: `cards/T12_benchmark_protocol_spec.md` section 2 (and `bench_ens_dump.py` there). Critic: `cards/WAVE3_REVIEW.md` section 2 line "metric_validity_probe" (FIX scope: rules as written; add Y13; confirm on W1-C1 before v0.2 text changes), Y8 (W1-G explores, W1-C1 confirms with the same script unchanged), Y13 (headline stability). Lead: L7 (Y13 accepted).
Tools (branch `bench_a`): S1 `bench/derived.py` + `scripts/bench_ens_dump.py` (derived and ensemble dumps, `derived_from` in the manifest); `bench/metrics_v02.py` (candidate metrics, probe transforms, `boot_fn`); `bench/ensread.py` (shared preparation with P1 / G5); `scripts/bench_metric_probe.py`. Tests `tests/test_bench_a2.py`.

## 1. Reading rule (fixed before any number; written about 05:10, before any tool ran on real dumps (driver started 05:11:34))
Definitions as built (the spec made concrete where it was open):
- Cells: the 532 cv5v2 out-of-fold pool cells, label set v1.1 (strict + ignore px not scored). One machine per read.
- Ensemble (P-real's "known real gain"): `pf_v11_ens2` = per cell mean of the two seeds' softmax (from the dumped float16 `logp`), argmax; written as a derived dump. Singles = the same two seeds.
- Operating points: OP-A argmax; OP-W = crack bias cross-fitted per fold (`crossfit_op.operating_points`, other folds only) so the ensemble's width ratio matches the mean of the singles' argmax width ratio on the fit cells; the singles at OP-W target their own width (argmax).
- Probes P-wide, P-thin, P-drop and P-shift are applied to the single-seed argmax maps (OP-A) and read paired (one seed draw per fold for both sides). P-drop: per seed, the pooled list of predicted crack components (8-connected, on scored px) with a px within 2 px of GT crack, in stem then label order; round(10%) of them chosen by `random.Random(0).sample`, replaced by `oth`.
- Bootstrap: `metrics_v02.boot_fn`, the same random sequence as `crossfit_op.boot_pair` (unit-tested equal on pooled metrics), 330 groups of `cv5v2_groups.tsv`, 2,000 draws, seed 0; P-real unpaired (one seed per fold and arm). z_real = delta / SE.
- Candidate crack metrics: strict IoU; relF1@1, @2, @3; centreline F1@2 (`clF1_2`, skeleton `bench/skel.py`, frozen at md5 804e4162); component F1 (harmonic mean of `cc_rec50_20` and `cc_prec_20`); per-cell crack IoU over cells with >= 20 GT crack px (`cellIoU`; GT-absent cells left out, P134); worst-10% per-cell relF1@2 over the same cells (mean of the lowest 10%, k = ceil(0.1 n); `worst10_relF1_2`); worst-source relF1@2 over sources with >= 40 cells (`worstsrc_relF1_2`). Inactive (reported, probes not applied): pooled IoU, per-cell IoU over cells with GT inactive >= 0.5% of scored px, region F1. Boundary IoU skipped (no T10 P549 code exists).
- S_j = (m(GT) - m(GT shifted 1 px right, ignore mask shifted with it)) / m(GT), mean over the two seeds, OP-A.

Rules (spec section 2, unchanged):
1. A crack metric is eligible to lead the table if all hold: E1 z_real at OP-W >= 2; E2 P-wide delta <= 0, or its 95% CI includes 0; E3 P-drop delta < 0 with CI high < 0.
2. The headline crack metric of v0.2 is the eligible metric with the largest z_real(OP-W); among metrics within 10% of that z, the lower S_j wins. Strict IoU stays printed beside its ceiling band.
3. If relF1@2 fails E2, it stays in the table only as the pair (relF1@2, width ratio), never alone, and loses the first column.
4. If z_real < 2 for every metric, E1 is re-read with the 5-seed ensemble on W1-C1 (same code) before any metric is dropped (spec "Risks").
Limits from the critic (Y13, L7), applied to whatever the rules give:
5. Arms whose primary is already pre-declared (all of wave 2 and wave 3) keep it. A new headline applies to the benchmark table and to arms specified after the change.
6. relF1@1, @2, @3 and the width ratio are always printed together; the width band (0.85 to 1.15 x baseline, pooled and per source with >= 40 cells) stays a pass condition whatever metric leads the table.
7. One skeleton implementation (`bench/skel.py`, md5 804e4162) is frozen: `metrics_v02.check_skel` fails if it changes. Tested on blobby predictions (section 2).
8. Y8: the W1-G read is exploration. The outcome becomes a result only after the same script, unchanged, gives the same eligibility and headline on W1-C1 (cv02); v0.2 text changes wait for that and for the lead.

## 2. Numbers (all E unless marked S)
Runs: tool commit **b036906** (`bench_metric_probe.py` 05c2caed, `bench_ens_dump.py` 80f93914, code md5 566a523e over metrics_v02, skel, crossfit_op, m0core, score_ext, derived), driver `/home/noob/work/bench_reads/stageA/A2/run_a2.sh`, tmux `bench_a_A2`, 05:11:34 to 05:16:06, nice 19, 8 workers, no GPU. Both reads used the same commit and the same command; only the dump folder differs.
- **W1-G (gaint, exploration):** `house_r34_unetpp_pf_v11` seeds 5, 6, 10 runs (manifest md5s in `A2/logs/probe_w1g.log`), NVIDIA RTX PRO 4500, fp32. Ensemble `A2/dumps_w1g/elbench1/pf_v11_ens2/w1g_pf_v11_ens2_s56_f[0-4]` (fold manifests 0aab4e49, 685b6723, 1352d864, 08be9145, 41a84d4a; 0 ties; 621 MB without logp). Out `A2/probe_w1g/` (probe.txt 93a6421c, probe.json ef78f21d), 83 s.
- **W1-C1 (cv02, confirmation, Y8):** `w1c1_pf_v11_f[0-4]_s[56]` via the symlink folder `stageA/links/w1c/house_r34_unetpp_pf_v11`, RTX A6000, fp32. Ensemble `A2/dumps_w1c1/...` (manifests 9f90c86c, 2b1106be, 8f697019, ab6e4837, bd49c0c0; 0 ties). Out `A2/probe_w1c1/` (probe.txt 40e99144, probe.json 252ceb3e), 84 s.
- Derived-dump check on real data: a one-member "ensemble" from the dumped float16 `logp` of w1g f2 s5 (11 cells) differs from the member's own fp32 argmax at 15 of 2,883,584 px, 0 crack px.
- Tests: 21 in `tests/test_bench_a2.py` (the spec's four, the frozen skeleton on blobby predictions, record_v02 = the reviewed `crossfit_op.record`, metrics = `score_ext.summarize`, `boot_fn` = `boot_pair` value for value on pooled metrics, transforms, sealed-set and forbidden-stem refusal, ensemble dump end to end, refusal to overwrite). Full suite 488 passed, 4 skipped.

Point values, mean over seeds 5, 6, OP-A (W1-G / W1-C1):
| Metric | singles | ens2 | P-wide | P-thin | P-drop |
|---|---|---|---|---|---|
| strict crack IoU | 0.362 / 0.366 | 0.374 / 0.378 | 0.362 / 0.366 | 0.183 / 0.186 | 0.343 / 0.345 |
| relF1@1 | 0.753 / 0.758 | 0.767 / 0.771 | 0.742 / 0.746 | 0.638 / 0.645 | 0.720 / 0.721 |
| relF1@2 | 0.842 / 0.845 | 0.853 / 0.856 | 0.838 / 0.841 | 0.792 / 0.797 | 0.803 / 0.803 |
| relF1@3 | 0.879 / 0.882 | 0.888 / 0.890 | 0.882 / 0.885 | 0.859 / 0.863 | 0.839 / 0.838 |
| centreline F1@2 | 0.853 / 0.856 | 0.862 / 0.865 | 0.867 / 0.869 | 0.817 / 0.820 | 0.814 / 0.812 |
| width ratio | 1.006 / 0.998 | 1.020 / 1.012 | 1.704 / 1.698 | 0.380 / 0.382 | 0.928 / 0.914 |
The 2-seed ensemble is not wider in CV (width ratio +0.014 [-0.007, +0.034] on W1-G, +0.014 [-0.002, +0.029] on W1-C1), so its cross-fitted OP-W is argmax in every fold on both machines: P-real at OP-W equals P-real at OP-A.

Contrasts, delta [95% CI] and the rule columns (W1-G | W1-C1). z = z_real at OP-W (= OP-A here). S_j from the 1-px GT shift.
| Metric | P-real (ens2 - singles) | z | P-wide | P-drop | E1 E2 E3 | S_j |
|---|---|---|---|---|---|---|
| strict crack IoU | +0.0116 [0.0068, 0.0168] \| +0.0116 [0.0080, 0.0155] | 4.44 \| 6.12 | -0.0004 [-0.016, 0.016] \| -0.0001 [-0.013, 0.014] | -0.020 [-0.029, -0.013] \| -0.021 [-0.031, -0.015] | yes yes yes \| yes yes yes | 0.318 \| 0.318 |
| relF1@1 | +0.0134 \| +0.0132 | 6.19 \| 4.71 | -0.012 [-0.023, -0.000] \| -0.011 [-0.021, -0.001] | -0.034 \| -0.036 | yes yes yes \| yes yes yes | 0.152 \| 0.149 |
| relF1@2 | +0.0108 [0.0071, 0.0147] \| +0.0106 [0.0053, 0.0172] | 5.60 \| 3.48 | -0.0039 [-0.0087, 0.0011] \| -0.0037 [-0.0083, 0.0006] | -0.039 \| -0.042 | yes yes yes \| yes yes yes | 0.058 \| 0.057 |
| relF1@3 | +0.0087 \| +0.0084 | 4.32 \| 2.98 | +0.0024 [-0.0001, 0.0047] \| +0.0026 [0.0001, 0.0050] | -0.040 \| -0.044 | yes yes yes \| yes **no** yes | 0.014 \| 0.013 |
| centreline F1@2 | +0.0090 \| +0.0089 | 4.08 \| 3.34 | **+0.0137 [0.0103, 0.0170] \| +0.0136 [0.0107, 0.0165]** | -0.039 \| -0.044 | yes **no** yes \| yes **no** yes | 0.049 \| 0.046 |
| component F1 | +0.0158 \| +0.0109 [-0.0015, 0.0239] | 2.56 \| 1.65 | -0.006 \| -0.001 | -0.049 \| -0.052 | yes yes yes \| **no** yes yes | 0.014 \| 0.015 |
| per-cell crack IoU | +0.0115 \| +0.0106 | 2.82 \| 3.17 | +0.006 [-0.005, 0.017] \| +0.004 [-0.007, 0.016] | -0.027 \| -0.032 | yes yes yes \| yes yes yes | 0.371 \| 0.372 |
| worst-10% cell relF1@2 | +0.014 [-0.038, 0.081] \| +0.009 | 0.50 \| 0.37 | +0.006 \| +0.004 | -0.029 [-0.142, 0.000] \| -0.012 [-0.128, 0.000] | **no** yes **no** \| **no** yes **no** | 0.249 \| 0.540 |
| worst-source relF1@2 | +0.011 \| +0.010 [-0.000, 0.046] | 1.59 \| 0.82 | +0.003 \| +0.001 | -0.056 \| -0.057 | **no** yes yes \| **no** yes yes | 0.077 \| 0.077 |
Inactive (reported, probes not applied), P-real: pooled IoU +0.019 [-0.009, +0.054] | +0.015 [-0.012, +0.044]; per-cell IoU +0.023 | +0.018; region F1 +0.014 | -0.003. P-wide (crack dilation) lowers inactive IoU by 0.019 | 0.020 (dilated crack px overwrite inactive px).
P-drop removed 127, 127 (W1-G) and 128, 125 (W1-C1) of 1,270, 1,266, 1,284, 1,252 touching components (seeds 5, 6). worst-source is read over ARTS, BMRK, CFVS, CSIR (SDLE has 17 cells).

Y13, the frozen skeleton on blobby predictions (unit tests, synthetic, E): a smooth 15 x 61 px blob over a 1-px GT line leaves no spur (Tp = Ts = 1; centreline F1 = 1 while strict IoU < 0.1). A jagged blob (random edges, half-width h +- 2 px) grows spurs, and Tp falls with width: about 0.68 (h = 3), 0.51 (h = 5), 0.39 (h = 8), 0.29 (h = 12). On the real maps the skeleton side of the metric barely moves under P-wide (Tp +0.0001): Zhang-Suen thins the smoothly dilated cracks back to the same centre line.
Why centreline F1@2 rewards the dilation (E, from the counts; S for the cause): Ts = share of GT skeleton px within 2 px of the predicted MASK; dilating the mask by 1 px brings more GT skeleton px within 2 px (Ts +0.025 | +0.025), while Tp cannot fall because the predicted skeleton is unchanged. The spec's formula measures Ts against the mask, not against the predicted skeleton.

## 3. Outcome under the rules
1. **W1-G (exploration):** eligible = strict IoU, relF1@1, relF1@2, relF1@3, component F1, per-cell IoU. Largest z: relF1@1 (6.19); within 10% of it: relF1@1 and relF1@2 (5.60, inside the band by 0.03); lower S_j: **relF1@2 (0.058 against 0.152) would lead.**
2. **W1-C1 (confirmation, same script unchanged):** eligible = strict IoU, relF1@1, relF1@2, per-cell IoU (relF1@3 fails E2 by a CI low of +0.0001; component F1 fails E1 at z 1.65). Largest z: strict IoU (6.12); nothing else within 10% (relF1@1 4.71); **strict IoU would lead.**
3. **The headline does not reproduce between the two reads, so under rule 8 (Y8) the probe gives no v0.2 headline change.** The ranking by z_real moves with the seed pair and the machine (strict IoU 4.44 vs 6.12, relF1@2 5.60 vs 3.48); one 2-seed contrast does not separate the leading metrics. The rule is usable but not decisive at this instrument; the lead decides (options in section 4). Rule 4 (re-read with the 5-seed ensemble) is written only for "z < 2 for every metric", which did not happen, so it was not run.
4. **Stable on both machines (these parts are results under Y8):**
   - relF1@2 passes E2 on both (P-wide -0.004, CI holds 0): it does not reward a 1-px dilation. **Rule 3 does not fire; relF1@2 keeps its place** (as the pair with the width ratio, which Y13 requires anyway). relF1@2 also has the lowest S_j among the eligible metrics (0.057), strict IoU the highest but one (0.318).
   - **Centreline F1@2 is not eligible on either machine: it fails E2** (rewards the 1-px dilation, +0.0137 [0.0103, 0.0170] and +0.0136 [0.0107, 0.0165]). The spec's expected candidate for the first column is out under its own rule. relF1@1 fails nothing but is punished by P-wide (-0.012); strict IoU and per-cell IoU are eligible on both.
   - Worst-10% per-cell relF1@2 is not eligible on either (E1 and E3 fail; the lowest 10% of cells score near 0, so the metric has no signal). Worst-source relF1@2 fails E1 on both (z 1.59, 0.82).
   - Inactive: no inactive metric moves detectably with the 2-seed ensemble (all CIs hold 0).
5. Y13 limits stand under any outcome: pre-declared primaries of wave 2 and wave 3 stay; relF1@1, @2, @3 and the width ratio are printed together; the width band stays a pass condition. The skeleton is frozen at 804e4162 (`check_skel` fails on any change).
S (outside the rules): the probe confirms the v0.1 order is defensible (relF1@2 with width, strict IoU beside it); the only change the evidence supports on both machines is negative: do not promote centreline F1@2 (as specified) to the first column. A centreline variant that measures Ts against the predicted skeleton would not see the dilation, but it was not pre-declared and is not read here.

## 4. Not run yet, and the commands that finish it
- Nothing owed under the rules: W1-G and the W1-C1 confirmation both ran (05:11 to 05:16).
- For the lead (only if a headline decision is wanted from this instrument; not pre-declared, so its outcome is a lead's call): the 5-seed ensemble on W1-C1 gives a larger real gain and five single seeds. Commands (about 3 min, CPU):
  `cd /home/noob/work/bench_wt_a && export CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 P=/home/noob/work/el-fault-detection/.venv/bin/python O=/home/noob/work/bench_reads/stageA/A2 ARM="PF=/home/noob/work/bench_reads/stageA/links/w1c/house_r34_unetpp_pf_v11:w1c1_pf_v11_f[0-4]_s[5-9]"`
  `nice -n 19 $P scripts/bench_ens_dump.py --arm "$ARM" --seeds 5,6,7,8,9 --seed-id 56789 --method pf_v11_ens5 --run-prefix w1c1_pf_v11_ens5_s56789 --dumps $O/dumps_w1c1 --workers 8 > $O/logs/ens5_w1c1.log 2>&1`
  `nice -n 19 $P scripts/bench_metric_probe.py --arm "$ARM" --ens "ENS5=$O/dumps_w1c1/elbench1/pf_v11_ens5:w1c1_pf_v11_ens5_s56789_f[0-4]" --labels v11 --workers 8 --cache $O/cache_w1c1 --out $O/probe_w1c1_ens5 > $O/logs/probe_w1c1_ens5.log 2>&1`
- gaint with seeds 7, 8 (W1-G2) adds nothing the rules need; the same two commands with the W1-G folder and `s[5-8]` would give a 4-seed gaint read if the lead wants it.
