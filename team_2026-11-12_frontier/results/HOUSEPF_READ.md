# HOUSE - PF, HRNET - PF, COMBO - PF intervals on cv5v3 (house_pf_read, 22 Nov 2026, 12:10 IST)

**Printed intervals only. No verdict; nothing here decides.** Closes thesis gaps G-N1 (HOUSE - PF with intervals) and G-N2 (strict crack IoU intervals of HRNET - PF and COMBO - PF), GAPS.md section A. Goal approved by the user 22 Nov.

Read: /home/noob/work/bench_reads/housepf_read/run_read_housepf.sh (8c5bdb36), run once, 22 Nov 11:51:51 to 12:06:02 on gaint CPU (nice -n 10, CUDA_VISIBLE_DEVICES empty, 8 workers), rc 0. Tool bench_wt_final 89b9ea5 (`git status --porcelain` 0 lines before and after) scripts/bench_read_w1.py fdb56b78; --labels v11, --groups cv5v3_groups.tsv (d880a769, 285 groups), --score-exclude score_exclude_v3.txt (6d48dfbd), --baseline PF, --aa PF:5,6:7,8, B 2000, boot seed 0. Tables: housepf_tables.py (146af19d). Arms, cv02 runs relayed to gaint, cv5v3 folds 0 to 4, seeds 5 to 9, read only: PF c3_pf_v11, HOUSE c3_house_v11 (relay c3base), HRNET c3h_hrnet_w18_unetpp_pf (relay c3hrnet, resolves to /mnt/nas/noob_el_archive/gaint_relay/c3hrnet), COMBO c3x_hrnet_swad_v11 swad_bn readout (relay c3x; the c3x primary, = "COMBO" of C3X_READ.md and T6, "C3X" in dataset_audit/REPORT.md l158). Pairs: PF=HOUSE, PF=HRNET, PF=COMBO. Pre-checks before anything was written: 100 dumps, 10,640 npz files md5-verified against their manifests; all 100 manifest md5s equal to those in results/c3hrnet_read/read.json (a67e8024) and results/c3x_read/read.json (47ba2005); one device (RTX A6000); step 20000, fp32, open sets only; no sealed-set path; no path under the live T3b relay. PID 5104 alive before and after. Pool cells only; no E1 or test50 file was read. Outputs (all in /home/noob/work/bench_reads/housepf_read/): read/read.txt (bb805994), read/read_x416.txt (4038090b), read/read.json (ec78a82a), tables.txt (db250cfa), dumps.tsv (3eb8bee9), run.log (a9d1147a); pins in MD5.txt (42551d4c: scripts, tool commit, inputs, 100 dump manifest md5s); output md5s in read_MD5.txt. E = measured, S = judgement.

M from this read's A/A (E, tables.txt l4 to l5): relF1@2 0.0100 on 532 and 416 cells; strict crack IoU 0.0100 (532) and 0.0105 (416); inactive IoU 0.0462 / 0.0539; mIoU-R13 0.0100.

## 1. HOUSE - PF (E; read.txt l270 to l289, read_x416.txt l263 to l282)
| Metric | 532 cells, OP-A | 532 cells, OP-W | 416 clean, OP-A | 416 clean, OP-W |
|---|---|---|---|---|
| crack relF1@2 | +0.0059 [-0.0043, +0.0152] | +0.0034 [-0.0075, +0.0127] | +0.0066 [-0.0068, +0.0191] | +0.0025 [-0.0116, +0.0156] |
| strict crack IoU | +0.0179 [+0.0093, +0.0266] | +0.0120 [+0.0022, +0.0216] | +0.0182 [+0.0065, +0.0295] | +0.0093 [-0.0036, +0.0215] |
| inactive IoU | +0.0099 [-0.0486, +0.0691] | +0.0120 [-0.0471, +0.0715] | +0.0086 [-0.0583, +0.0758] | +0.0117 [-0.0564, +0.0799] |
| mIoU-R13 | -0.0050 [-0.0144, +0.0041] | -0.0053 [-0.0147, +0.0038] | -0.0062 [-0.0179, +0.0035] | -0.0066 [-0.0184, +0.0031] |
| relP@2 / relR@2 | +0.0023 / +0.0088 | +0.0144 / -0.0053 | +0.0006 / +0.0112 | +0.0164 / -0.0078 |
- The tool prints its screen flag PASS* on strict crack IoU at 532 OP-A, 532 OP-W and 416 OP-A (read.txt l270, l286; read_x416.txt l263). PASS* is a screen flag, not a result (E, read.txt rules line).
- Per seed, 532 OP-A, relF1@2 / strict IoU: s5 +0.0027 / +0.0175, s6 +0.0051 / +0.0172, s7 +0.0085 / +0.0177, s8 +0.0055 / +0.0210, s9 +0.0077 / +0.0160 (E, tables.txt section 4).
- The point values match the dataset audit (relF1@2 +0.0059, strict IoU +0.0179, REPORT.md l155) (E).
- S: HOUSE's strict IoU edge (+0.018) sits inside the convention band +-0.019 (T6 note) at every value; its relF1@2 interval includes 0 at every value.

## 2. HOUSE - PF guard items, C3HRNET layout (E; point values, inclusive bounds; tables.txt l84 to l115)
| Guard | 532, OP-A | 532, OP-W | 416, OP-A | 416, OP-W |
|---|---|---|---|---|
| width ratio pooled (HOUSE / PF; 0.85 to 1.15) | 1.112 | 0.998 | 1.147 | 1.000 |
| width per source ARTS / BMRK / CFVS / CSIR | **1.307** / 1.063 / 1.123 / 1.055 | **1.167** / 0.961 / 1.006 / 0.957 | **1.370** / 1.063 / **1.164** / 1.090 | **1.190** / 0.935 / 1.011 / 0.962 |
| false crack px on crack-free cells (303 / 226 cells; max 1.5 x) | **774 vs 212 = 3.66 x** | **586 vs 212 = 2.77 x** | **717 vs 196 = 3.65 x** | **502 vs 196 = 2.55 x** |
| inactive IoU delta (>= -M) | +0.0099 | +0.0120 | +0.0086 | +0.0117 |
| mIoU-R13 delta (>= -0.010) | -0.0050 | -0.0053 | -0.0062 | -0.0066 |
Outside a bound (bold): 9 items. ARTS width at all four values, CFVS width at 416 OP-A, false crack px at all four values. Pooled width, inactive and mIoU-R13 are inside at all four. Share of crack-free cells with >= 50 false px: HOUSE 0.0119 / 0.0099 / 0.0159 / 0.0133 against PF 0.0013 / 0.0013 / 0.0018 / 0.0018.

## 3. Strict crack IoU for HRNET - PF and COMBO - PF (E; read.txt l294, l310, l318, l334; read_x416.txt l287, l303, l311, l327)
| Contrast | 532 cells, OP-A | 532 cells, OP-W | 416 clean, OP-A | 416 clean, OP-W |
|---|---|---|---|---|
| HRNET - PF | +0.0008 [-0.0105, +0.0111] | +0.0050 [-0.0070, +0.0156] | -0.0004 [-0.0123, +0.0121] | +0.0030 [-0.0092, +0.0166] |
| COMBO - PF | +0.0099 [-0.0007, +0.0207] | +0.0109 [+0.0002, +0.0217] (tool flag PASS*) | +0.0099 [-0.0020, +0.0224] | +0.0096 [-0.0027, +0.0223] |
- Reproduction (E, tables.txt section 5): every contrast number of HRNET - PF and COMBO - PF (9 metrics x 3 operating points x delta, lo, hi, SE, on 532 and on 416 cells: 432 numbers) equals the earlier reads exactly (max abs difference 0). The manifest md5s of all 50 runs behind each contrast are equal too.
- These intervals were already printed before this read: results/c3hrnet_read/read.txt l213, l229 and read_x416.txt l208, l224 (HRNET - PF); results/c3x_read/read.txt l327, l343 and read_x416.txt l318, l334 (COMBO - PF) (E). GAPS.md G-N2 and T6 missed them; this read reproduces them with the same tool and dumps (S).
- relF1@2 of HRNET - PF and COMBO - PF in this read equals the C3HRNET and C3X reads (E, tables.txt section 1), for example COMBO - PF 532 OP-W +0.0158 [+0.0069, +0.0264], 416 OP-W +0.0166 [+0.0054, +0.0298].

## 4. Levels (E, OP-A, mean over 5 seeds; tables.txt section 3)
| Arm | cells | crack IoU | relF1@2 | inactive IoU | mIoU-R13 | width ratio | false crack px |
|---|---|---|---|---|---|---|---|
| PF | 532 | 0.3653 | 0.8463 | 0.5042 | 0.6116 | 1.019 | 212 |
| HOUSE | 532 | 0.3832 | 0.8522 | 0.5141 | 0.6066 | 1.133 | 774 |
| PF | 416 | 0.3476 | 0.8264 | 0.5050 | 0.6049 | 0.951 | 196 |
| HOUSE | 416 | 0.3657 | 0.8330 | 0.5135 | 0.5987 | 1.091 | 717 |
PF and HOUSE levels equal those of the C3HRNET read (E, compare C3HRNET_READ.md section 3).

## 5. What changes in T6 (S; the lead edits THESIS_TABLES.md and GAPS.md)
Row "HOUSE - PF (no registered cv5v3 read; dataset audit)":
- relF1@2 532 OP-A: "+0.0059, point value, no interval (audit)" -> +0.0059 [-0.0043, +0.0152]
- relF1@2 532 OP-W (empty) -> +0.0034 [-0.0075, +0.0127]
- relF1@2 416 OP-A (empty) -> +0.0066 [-0.0068, +0.0191]
- relF1@2 416 OP-W (empty) -> +0.0025 [-0.0116, +0.0156]
- strict crack IoU 532 OP-A: "+0.0179 PASS, point value, no interval (audit)" -> +0.0179 [+0.0093, +0.0266], inside the convention band
- Failing guard items (empty) -> outside bounds 9: ARTS width at all four values (1.307 / 1.167 / 1.370 / 1.190); CFVS width 1.164 (416, OP-A); false crack px 2.55 to 3.66 x PF (all four values)
- Verdict column: "no interval in any file (GAPS.md G-N1)" -> printed intervals only, no registered rule, decides nothing (HOUSEPF_READ.md)
- Row label: the "dataset audit" source can become HOUSEPF_READ.md
Row "HRNET - PF": strict crack IoU 532 OP-A "+0.0008, point value, no interval (audit)" -> +0.0008 [-0.0105, +0.0111] (C3HRNET read.txt l213; reproduced here).
Row "COMBO - PF (c3x HRNet + SWAD, swad_bn, primary)":
- strict crack IoU 532 OP-A "+0.0099, point value, no interval (audit)" -> +0.0099 [-0.0007, +0.0207] (c3x read.txt l327; reproduced here)
- also without interval in T6 today: relF1@2 532 OP-W "+0.0158" -> +0.0158 [+0.0069, +0.0264]; 416 OP-W "+0.0166" -> +0.0166 [+0.0054, +0.0298] (c3x read.txt l344, read_x416.txt l335; reproduced here)
GAPS.md: G-N1 and G-N2 can move to closed, citing this file.

## 6. Deviations from the C3HRNET read settings (E)
- nice -n 10 instead of 19 (lead's instruction). No effect on numbers.
- Arms and pairs: COMBO added; pairs PF=HOUSE, PF=HRNET, PF=COMBO instead of PF=HRNET, HOUSE=HRNET. Each contrast uses its own bootstrap stream (boot seed 0), so the set of pairs does not change any interval (E: section 3 reproduction).
- Fresh cache (housepf_read/cache_c), not the c3hrnet cache.
- Added pre-checks: manifest md5s against the prior read.json files, every npz md5 against its manifest (the tool also does this), sealed-set and live-relay path refusals, PID 5104 and worktree before and after.
- Guard items computed by housepf_tables.py from read.json, not by hand. Bounds as in results/c3x_read/verdict.txt: width 0.85 to 1.15 pooled and per source with >= 40 cells, false crack px max 1.5 x PF, inactive allowed drop = A/A M (0.0462 / 0.0539), mIoU-R13 allowed drop 0.0100.
- Same as C3HRNET otherwise: tool, commit, labels v11, groups, score-exclude, A/A PF:5,6:7,8, B 2000, 8 workers, OMP_NUM_THREADS 1. Strict crack IoU M on 416 cells is 0.0105 from the A/A rule max(0.01, 2 SE), as in the C3HRNET read's own x416 table (E, results/c3hrnet_read/read.json x416 M).

## 7. Limits
One machine for training (cv02), one split (cv5v3), 5 seeds, argmax and width-matched operating points, development pool cells only. HOUSE has no registered rule; nothing in this file is a verdict (S).
