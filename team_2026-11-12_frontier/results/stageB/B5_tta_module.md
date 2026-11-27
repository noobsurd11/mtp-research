# B5 module: bench/tta.py (shared piece S5) and the prepared msc_tta GPU evaluation (stage B5, 15 Nov 2026)

Spec: cards/T7_unseen_modules_spec.md "Arm 3: msc_tta". Critic: WAVE3_REVIEW s2 line "msc_tta" (FIX: U2 printed as an upper bound, cannot promote; score claim on CV5; print 24 views beside D4 (8 views) and beside a 3-seed D4 ensemble at equal cost), Y10 (bounded by HC and the 2x input null), G15 (an arm tested with the simulator's transform cannot be read on that simulator), G16 (TTA rows print the view count and cost).
Tags: E = measured, S = judgement. No GPU was used; no sealed cell was read. Nothing is armed.

## 1. Reading rule for the GPU evaluation (written 15 Nov 14:40 IST, before any TTA number exists)

Checkpoints: the W1-G PF v1.1 fold models on gaint (seeds 5 to 8 exist; this read uses 5, 6 and, for the ensemble, 7). Arms, all on the same checkpoints and the same cells:
- PLAIN: the existing W1-G cv5v2 dumps (no TTA), seeds 5, 6.
- D4: `--tta d4` (8 views, scale 1), seeds 5, 6 (seed 7 is dumped only as an ensemble member).
- D4MS: `--tta d4ms` (24 views: D4 x scales 0.75, 1.0, 1.25), seeds 5, 6.
- D4ENS3: mean-softmax ensemble of the D4 dumps of seeds 5, 6, 7 (bench_ens_dump.py on their logp; 24 forward passes per cell, equal cost to D4MS).

Score claim (critic's FIX; decides whether msc_tta counts as a score arm). All of:
1. CV5 (532 pool cells, out-of-fold): D4MS - PLAIN crack relF1@2 >= -M and strict crack IoU >= -M, at OP-A and at OP-W (point values; M = 0.010 on gaint for both metrics, ROWS1_READ section 4).
2. Width band: D4MS width ratio within 0.85 to 1.15 x PLAIN's at OP-A, pooled and per source with >= 40 cells.
3. Half-cell volume guards: pooled predicted crack px D4MS / PLAIN <= 1.5 on H36 (all 36 cells, same models) and on the pool half-cells (pool_half_p0..3, the two models f0 s5 and f1 s5).
If 1 to 3 hold, msc_tta counts as a non-inferior score arm; otherwise it is dropped as a score arm (spec 3.3). In both cases it stays a benchmark TTA row (no-TTA value beside it, views and cost stated).

Printed beside, deciding nothing:
- D4MS - D4 (the spec's contrast: the scale views on top of D4) and D4 - PLAIN, at OP-A and OP-W, with intervals.
- D4MS against D4ENS3 at equal cost (24 forward passes each), at OP-A and OP-W.
- U2 (shvoof views of each model's own held-out fold): D4MS - D4 and D4MS - PLAIN crack relF1@2 at OP-A, labelled "upper bound, gamed": the 0.75 view inverts the simulator's 1.34 scale. U2 neither promotes nor drops the arm (G15); the lead may override.
- H36 crack-free cells (19): false-alarm px per cell, PLAIN / D4 / D4MS.
- F51 crack (paired over the same models): only after the plain F51 dumps (stage A7) exist; descriptive (crack effective n 1.7).
- Cost (G16): views, wall seconds per fold run from the queue log, peak MiB from the pathfinder.
Intervals: bench_read_w1.py contrasts (two-stage group bootstrap, 2,000 draws, seed 0). One variant per mode, no tuning; scales are the spec's and fixed.

## 2. What was built (E)

Code on bench_b: **6c43b48** (bench/tta.py, scripts/bench_infer.py --tta, tests/test_bench_tta.py, scripts/bench_tta_jobs.py) and **60fcf70** (job lists: one dump root per set family; test for it).
- `bench/tta.py`: `predict_tta(model, x, scales, use_d4)` exactly as the spec's pseudo-code (side = 32 x round(H s / 32): 384 / 512 / 640; bilinear, align_corners False, antialias only when shrinking; logits mapped back by the inverse view, resized to 512, softmax, mean over views). D4 convention copied from the existing D4 path (scripts/b3/m0_audit_b3.py `dihedral`). Modes: id (1 view through the module), d4 (8), d4ms (24).
- `scripts/bench_infer.py --tta {none,id,d4,d4ms}`: none (default) leaves the plain path as it was; other modes average probabilities per batch, pred = argmax p, maps and logp from p by the same `maps` function; fp32 only; manifest key `tta` = {mode, scales, d4, views}; default run id `<run>.tta_<mode>` so TTA dumps never share a folder with plain dumps. Sealed-set refusal, forbidden-list and train-overlap guards are untouched.

### 2a. Unit tests (tests/test_bench_tta.py, 11 tests, CPU, synthetic inputs)
D4 round trip exact for all 8 views and equal to the reference `dihedral` (forward and inverse); the 8 views distinct; side_of gives 384 / 512 / 640 and view counts 1 / 8 / 24; single view through the module = `softmax(model(x))` exactly (torch.equal); D4 TTA = the existing D4 code path within 1e-6; the TTA output is D4-equivariant (TTA of a rotated or flipped input = the rotated or flipped TTA output) within 1e-5, for D4 and for D4 x 3 scales, with a non-equivariant conv net; a pointwise model gives the single-view result under D4, and under D4 x scales on a constant image; p sums to 1 within 1e-5; the house R34 U-Net++ runs at 384 and 640 px and the 3-scale average on a 512 input sums to 1; job-list shape (65 / 16 / 20 lines, gate 6,200, no sealed set name, 15 logp lines, each run dir gets one set dir).

### 2b. Identity on real pool cells (CPU fp32, threads 7; W1-G model w1g_pf_v11_f0_s5 on its held-out fold cv5v2_f0, 107 cells; bench_reads/stageB/B5/run_id.sh, logs/compare.log)
- Old bench_infer (git archive of 43ebf79) against new `--tta none`: **107 of 107 cell files byte-identical** (same md5).
- New `--tta id` against new `--tta none`: pred, oth, m_crack, p_inact and logp byte-equal in all 107 cells; p_crack (float32) differs at 142 of 28.0 M px by at most 2 ulp (max abs 9.1e-13): the plain path takes one softmax over the 107 concatenated logit maps, the TTA path one softmax per batch of 8. Pred differs at 0 px. The comparison script printed "DIFF" because it demands byte equality on every key; by the 2-ulp size of the difference (S) the single-view TTA path equals bench_infer's output.
- Full pytest: 568 passed, 4 skipped at 43ebf79; 579 passed, 4 skipped at 6c43b48 (bench_reads/stageB/B5/logs/pytest_full_2.log); 579 passed, 4 skipped at 60fcf70 (logs/pytest_full_3.log), rc 0.

### 2c. GPU evaluation PREPARED, not armed (/home/noob/work/bench_udev/jobs_tta: JOBS.md5 b9d0c10a, PREP.md)
| list | md5 | lines | content |
|---|---|---|---|
| tta/jobs.txt | b0ef79e7 | 65 | pathfinder (d4ms, f0 s5, alone first); CV5 d4 x seeds 5, 6, 7 with logp (15); CV5 d4ms x seeds 5, 6 (9 more); U2 shvoof d4 / d4ms x seeds 5, 6 (20); H36 d4 / d4ms x seeds 5, 6 (20) |
| tta/pool/jobs.txt | ecccf3b6 | 16 | pool_half_p0..3 d4 / d4ms for f0 s5 and f1 s5 |
| tta/f51/jobs.txt | ea13248c | 20 | F51 d4 / d4ms x seeds 5, 6 (with stage A7's plain F51 dumps) |
Format bq/w2a2 (name|card|seed|root|gate|cmd|), cuda fp32 (TF32 off), batch 4, gate 6,200 MiB, dumps under /home/noob/work/bench_udev/tta/dumps_<family>. Cost (S): about 3 GPU-h for tta/jobs.txt, 1.5 for pool, 0.5 for F51; disk about 30 GB. Peak memory at batch 4 with 640 px views is not measured (no GPU here): the pathfinder line measures it before the rest is armed.

## 3. Outcome
- Module, tests and job lists exist; the plain inference path is unchanged (byte-identical on 107 real cells). No TTA number exists yet; the reading rule in section 1 is fixed for when it does.
- S (Y10): the expected CV5 effect is -0.005 to +0.01 relF1@2 and E1 at most about +0.015 (spec); U2 will move by construction and decides nothing.
- Found while preparing (for the lead): B3's udev_infer list writes shvoof_f<k>, h36 and pool sets of one run into one run dir under /home/noob/work/bench_udev/dumps; bench_udev_read.py (w1read.discover) asserts one set dir per run dir, so the planned U2 read of those dumps would stop with an assertion. bench_labelfree.py is not affected. My lists avoid it (one root per set family).

## 4. Owed (exact)
1. Lead: deploy worktree at a bench_b commit >= 60fcf70 (or the bench_b + rows2 merge that B3's PREP.md asks for), flag-off identity there, then arm the pathfinder line of /home/noob/work/bench_udev/jobs_tta/tta/jobs.txt alone (MAXC 1), read its peak MiB, then the rest (PREP.md has the arming lines; after bq/w2a2 and the U-dev blocks).
2. After the jobs: the reads in PREP.md (bench_ens_dump for D4ENS3, bench_read_w1 with --pair PLAIN=D4MS, PLAIN=D4, D4=D4MS, D4ENS3=D4MS; bench_labelfree on h36 and pool; bench_udev_read on U2 as an upper bound), then write results/stageB/B5_msc_tta.md under the rule in section 1.
3. Re-render B3's udev_infer list with one dump root per set family before it is armed (finding above).
