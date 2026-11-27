# CS_D4 - HOUSE and CS - HOUSE on cv5v3: the HOUSE rule on the C2 recipe (house_cs_read, 22 Nov 2026, 15:30 IST)

**Printed intervals only. No verdict; nothing here decides. Every CS and CS_D4 number is selection-biased**: the swad readout was chosen after the c3x read on these cells; the unbiased test is the E1 opening (FINAL_TTA_READ.md l9 to l10). Goal approved by the user 22 Nov ("run the HOUSE read"). Rule: PROTOCOL_v1.0.md section 7.1, HOUSE rule (l312). E = measured, S = judgement. Files below without a folder are in /home/noob/work/bench_reads/housecs_read/.

## Run record and pins (E)
- Runner run_read_housecs.sh (e00dfa83): a copy of housepf_read/run_read_housepf.sh (8c5bdb36) plus the manifest field checks of harness/final/run_read_final.sh (a6e952ec); the old runners are not edited. Run once, 22 Nov 15:06:33 to 15:17:26, gaint CPU (nice -n 10, CUDA_VISIBLE_DEVICES empty, 8 workers, OMP_NUM_THREADS 1), rc 0 (run.log l1, l10, l14).
- Tool bench_wt_final 89b9ea5, `git status --porcelain` 0 lines before and after (run.log l1, l14); scripts/bench_read_w1.py fdb56b78; --labels v11, --groups cv5v3_groups.tsv (d880a769, 285 groups), --score-exclude score_exclude_v3.txt (6d48dfbd), --baseline PF, --aa PF:5,6:7,8, B 2000, boot seed 0 (tables.txt l2 to l3). Tables: housecs_tables.py (38454c02).
- Arms (cv02 runs relayed to gaint, cv5v3 folds 0 to 4, seeds 5 to 9, read only): PF c3_pf_v11 (relay c3base; baseline, A/A, OP-W width reference); HOUSE c3_house_v11 (c3base); CS c3x_hrnet_swad_v11 .swad (c3x; single view); CS_D4 c3x_hrnet_swad_v11 .swad.tta_d4 (fin; 8-view D4 on the same checkpoints). Pairs: HOUSE=CS_D4 and HOUSE=CS (the rule); PF=CS_D4 and PF=CS (reproduction of final_tta_read); PF=HOUSE (reproduction of housepf_read).
- Pre-checks before anything was written (run.log l3): 100 dumps, 10,640 npz files md5-verified against their manifests; 100 of 100 manifest md5s equal to expected_manifests.tsv (b11105a1) and to the prior read.json files (results/final_tta_read e9692e7e: PF, CS, CS_D4; housepf_read ec78a82a and results/c3hrnet_read a67e8024: PF, HOUSE); each CS_D4 checkpoint_md5 = its CS dump's (25 runs); manifest fields (run id, fold, seed, weights key, step 20000, set, fp32, open set, train code revision, tta, writer) as expected; one device (RTX A6000); no sealed-set path; no path under the live T3b relay. PID 5104 alive before and after (run.log l2, l13). Pool cells only; no E1 or test50 file was read.
- Outputs: read/read.txt (c65458ee), read/read_x416.txt (22faa38e), read/read.json (4b46165f), tables.txt (6097540b), dumps.tsv (2417d4a7), run.log (cdf12bd6); output md5s in read_MD5.txt (3bf4503a). Pins in MD5.txt (5995f030, written before the run): scripts, expected_manifests.tsv, tool, inputs, prior read files, tool commit, 100 dump manifest md5s.
- M from this read's A/A (tables.txt l4, l6), equal to the final TTA read (tables.txt l313, l316): relF1@2 0.0100 (532 and 416); strict crack IoU 0.0100 / 0.0105; inactive IoU 0.0462 / 0.0539; mIoU-R13 0.0100.

## 1. CS_D4 - HOUSE, the rule as written (E; tables.txt l11 to l42; read.txt l270 to l293; read_x416.txt l263 to l286; selection-biased)
| Metric | 532, OP-A | 532, OP-W | 416 clean, OP-A | 416 clean, OP-W |
|---|---|---|---|---|
| crack relF1@2 | +0.0163 [+0.0051, +0.0284] | +0.0194 [+0.0080, +0.0319] | +0.0164 [+0.0033, +0.0318] | +0.0204 [+0.0073, +0.0369] |
| relP@2 | +0.0240 [+0.0133, +0.0371] | +0.0111 [-0.0020, +0.0246] | +0.0278 [+0.0141, +0.0434] | +0.0124 [-0.0035, +0.0288] |
| relR@2 | +0.0100 [-0.0096, +0.0284] | +0.0258 [+0.0052, +0.0459] | +0.0075 [-0.0147, +0.0317] | +0.0261 [+0.0033, +0.0514] |
| strict crack IoU (band +-0.019) | +0.0110 [+0.0029, +0.0198], inside | +0.0179 [+0.0082, +0.0281], inside | +0.0095 [-0.0004, +0.0197], inside | +0.0181 [+0.0083, +0.0296], inside |
| inactive IoU | +0.0229 [-0.0317, +0.0831] | +0.0207 [-0.0354, +0.0820] | +0.0168 [-0.0402, +0.0829] | +0.0137 [-0.0453, +0.0806] |
| mIoU-R13 | +0.0167 [+0.0085, +0.0264] | +0.0170 [+0.0089, +0.0268] | +0.0161 [+0.0064, +0.0283] | +0.0165 [+0.0067, +0.0288] |
- The tool prints its screen flag PASS* on relF1@2 at all four values, on strict crack IoU at three (not 416 OP-A) and on mIoU-R13 at all four (read.txt l270, l271, l273, l286, l287, l289; read_x416.txt l264, l266, l279, l280, l282). PASS* is a screen flag, not a result (read.txt l391) (E).

## 2. CS - HOUSE, single view on both sides (E; tables.txt l43 to l74; read.txt l294 to l317; read_x416.txt l287 to l310; selection-biased)
| Metric | 532, OP-A | 532, OP-W | 416 clean, OP-A | 416 clean, OP-W |
|---|---|---|---|---|
| crack relF1@2 | +0.0107 [-0.0009, +0.0229] | +0.0140 [+0.0017, +0.0269] | +0.0110 [-0.0028, +0.0264] | +0.0155 [+0.0013, +0.0320] |
| relP@2 | +0.0141 [+0.0018, +0.0273] | +0.0001 [-0.0144, +0.0141] | +0.0170 [+0.0007, +0.0331] | +0.0004 [-0.0175, +0.0178] |
| relR@2 | +0.0080 [-0.0120, +0.0269] | +0.0249 [+0.0048, +0.0443] | +0.0062 [-0.0169, +0.0304] | +0.0265 [+0.0026, +0.0513] |
| strict crack IoU (band +-0.019) | -0.0018 [-0.0109, +0.0078], inside | +0.0060 [-0.0041, +0.0165], inside | -0.0029 [-0.0138, +0.0082], inside | +0.0070 [-0.0038, +0.0192], inside |
| inactive IoU | +0.0062 [-0.0525, +0.0685] | +0.0038 [-0.0562, +0.0669] | +0.0011 [-0.0654, +0.0711] | -0.0022 [-0.0685, +0.0693] |
| mIoU-R13 | +0.0123 [+0.0043, +0.0222] | +0.0128 [+0.0045, +0.0226] | +0.0119 [+0.0019, +0.0248] | +0.0124 [+0.0025, +0.0255] |
- Tool flag PASS* on relF1@2 at OP-W (both cell sets) and on mIoU-R13 at all four values (read.txt l297, l311, l313; read_x416.txt l290, l304, l306) (E).

## 3. CS_D4 - HOUSE_D4: not read, no HOUSE D4 dump exists (E)
- Relay fin holds only c3_pf_v11.tta_d4, c3x_hrnet_swad_v11.swad.tta_d4 and .swad_bn.tta_d4, 25 each (the fin queue, run_read_final.sh l7 to l13).
- No directory matching `*house*tta*` under /home/noob/work (bench_relay, bench_dumps, bench_*_io, bench_reads and the rest; bq, bench_q, bench_t3b_io* not entered) or /mnt/nas/noob_el_archive/gaint_relay.
- The gaint B5 TTA (cv5v2) ran PF only (results/stageB/b5_cv5_read/run_cv5_read.sh l18 to l24). log.md names no HOUSE D4 dump.
- Not searched: /mnt/nas/noob_el_archive/bench_relay (live T3b relay root, off limits) and cv02.

## 4. Guard items (E; final_verdict.py definitions, reference R = HOUSE; point values, bounds inclusive; tables.txt l78 to l149; selection-biased)
| CS_D4 - HOUSE | 532, OP-A | 532, OP-W | 416, OP-A | 416, OP-W |
|---|---|---|---|---|
| width pooled, CS_D4 / HOUSE (0.85 to 1.15) | 0.893 | 1.005 | 0.872 | 0.997 |
| width ARTS / BMRK / CFVS / CSIR | **0.847** / 0.956 / 0.882 / 0.917 | 0.961 / 1.066 / 0.994 / 1.025 | **0.846** / 0.956 / 0.853 / 0.902 | 0.974 / 1.082 / 0.978 / 1.022 |
| false crack px on crack-free cells (303 / 226; max 1.5 x HOUSE) | 98 vs 774 = 0.13 x | 102 vs 586 = 0.17 x | 67 vs 717 = 0.09 x | 63 vs 502 = 0.13 x |
| beside: same against PF | 0.46 x | 0.48 x | 0.34 x | 0.32 x |
| inactive IoU delta (>= -M) | +0.0229 | +0.0207 | +0.0168 | +0.0137 |
| mIoU-R13 delta (>= -0.0100) | +0.0167 | +0.0170 | +0.0161 | +0.0165 |

| CS - HOUSE | 532, OP-A | 532, OP-W | 416, OP-A | 416, OP-W |
|---|---|---|---|---|
| width pooled, CS / HOUSE | 0.881 | 1.002 | 0.863 | 0.999 |
| width ARTS / BMRK / CFVS / CSIR | 0.861 / 0.956 / 0.867 / 0.904 | 0.985 / 1.076 / 0.989 / 1.018 | 0.865 / 0.956 / **0.841** / 0.888 | 1.010 / 1.095 / 0.977 / 1.017 |
| false crack px (max 1.5 x HOUSE) | 213 vs 774 = 0.28 x | 224 vs 586 = 0.38 x | 171 vs 717 = 0.24 x | 173 vs 502 = 0.34 x |
| beside: same against PF | 1.01 x | 1.06 x | 0.87 x | 0.88 x |
| inactive IoU delta (>= -M) | +0.0062 | +0.0038 | +0.0011 | -0.0022 |
| mIoU-R13 delta (>= -0.0100) | +0.0123 | +0.0128 | +0.0119 | +0.0124 |
- Outside a bound (bold): CS_D4 - HOUSE 2 items, ARTS width at OP-A 0.847 (532) and 0.846 (416), below 0.85 (tables.txt l79, l97). CS - HOUSE 1 item, CFVS width 0.841 (416, OP-A) (l135). All other items inside (E).
- Share of crack-free cells with >= 50 false px: CS_D4 0.0013 / 0.0013 / 0.0000 / 0.0000 against HOUSE 0.0119 / 0.0099 / 0.0159 / 0.0133 (l83, l92, l101, l110) (E).
- OP-W matches every arm to PF's width (--baseline PF, as in the final TTA read), so at OP-W both sides carry PF's width (E, bench_read_w1.py l138).

## 5. Per-seed deltas (E; X seed s - HOUSE seed s, independent runs, nominal pairing; tables.txt l172 to l217; selection-biased)
relF1@2 / strict crack IoU:
| Contrast, cells, op | s5 | s6 | s7 | s8 | s9 |
|---|---|---|---|---|---|
| CS_D4 - HOUSE, 532, OP-A | +0.0144 / +0.0071 | +0.0216 / +0.0150 | +0.0151 / +0.0096 | +0.0156 / +0.0130 | +0.0146 / +0.0101 |
| CS_D4 - HOUSE, 532, OP-W | +0.0185 / +0.0152 | +0.0239 / +0.0199 | +0.0180 / +0.0175 | +0.0190 / +0.0198 | +0.0177 / +0.0171 |
| CS_D4 - HOUSE, 416, OP-A | +0.0140 / +0.0054 | +0.0225 / +0.0147 | +0.0163 / +0.0079 | +0.0148 / +0.0108 | +0.0143 / +0.0088 |
| CS_D4 - HOUSE, 416, OP-W | +0.0191 / +0.0148 | +0.0246 / +0.0198 | +0.0204 / +0.0179 | +0.0200 / +0.0201 | +0.0181 / +0.0180 |
| CS - HOUSE, 532, OP-A | +0.0123 / -0.0045 | +0.0165 / +0.0035 | +0.0100 / -0.0015 | +0.0086 / -0.0011 | +0.0064 / -0.0053 |
| CS - HOUSE, 532, OP-W | +0.0157 / +0.0043 | +0.0191 / +0.0090 | +0.0130 / +0.0079 | +0.0126 / +0.0066 | +0.0094 / +0.0024 |
| CS - HOUSE, 416, OP-A | +0.0129 / -0.0044 | +0.0176 / +0.0044 | +0.0109 / -0.0037 | +0.0072 / -0.0031 | +0.0063 / -0.0077 |
| CS - HOUSE, 416, OP-W | +0.0179 / +0.0061 | +0.0207 / +0.0109 | +0.0151 / +0.0076 | +0.0126 / +0.0066 | +0.0111 / +0.0037 |
- relF1@2 is positive in 5 of 5 seeds in all 8 rows; CS - HOUSE strict IoU at OP-A in 1 of 5. relP@2, relR@2, inactive IoU and mIoU-R13 per seed: tables.txt l173 to l219 (E).

## 6. Levels (E; OP-A, mean over 5 seeds; tables.txt l153 to l168)
| Arm | cells | strict crack IoU | relF1@2 | relP@2 | relR@2 | inactive IoU | mIoU-R13 | width ratio | false crack px |
|---|---|---|---|---|---|---|---|---|---|
| PF | 532 | 0.3653 | 0.8463 | 0.8953 | 0.8024 | 0.5042 | 0.6116 | 1.019 | 212 |
| HOUSE | 532 | 0.3832 | 0.8522 | 0.8976 | 0.8112 | 0.5141 | 0.6066 | 1.133 | 774 |
| CS (selection-biased) | 532 | 0.3814 | 0.8629 | 0.9117 | 0.8191 | 0.5203 | 0.6189 | 0.999 | 213 |
| CS_D4 (selection-biased) | 532 | 0.3942 | 0.8684 | 0.9216 | 0.8211 | 0.5370 | 0.6232 | 1.012 | 98 |
| PF | 416 | 0.3476 | 0.8264 | 0.8882 | 0.7726 | 0.5050 | 0.6049 | 0.951 | 196 |
| HOUSE | 416 | 0.3657 | 0.8330 | 0.8888 | 0.7838 | 0.5135 | 0.5987 | 1.091 | 717 |
| CS (selection-biased) | 416 | 0.3628 | 0.8439 | 0.9058 | 0.7900 | 0.5146 | 0.6106 | 0.942 | 171 |
| CS_D4 (selection-biased) | 416 | 0.3753 | 0.8494 | 0.9166 | 0.7913 | 0.5303 | 0.6148 | 0.951 | 67 |

## 7. Reproduction check (E; tables.txt l294 to l359)
- CS_D4 - PF and CS - PF from this read equal results/final_tta_read/read.txt exactly: the lines starting "CS_D4 - PF" and "CS - PF" are 48 and 48 here and there, identical in content and order; in read_x416.txt 24 and 24, identical to bench_reads/final_tta/read/read_x416.txt (l308 to l311). Example: CS_D4 - PF relF1@2 532 OP-A +0.0222 [+0.0138, +0.0308], CS - PF +0.0166 [+0.0082, +0.0263] (read.txt l319, l343; FINAL_TTA_READ.md l17, l18).
- In read.json every number of both contrast blocks (9 metrics x OP-A / OP-F / OP-W x delta, lo, hi, SE, plus B, boot seed, units, seeds: 147 per block and cell set) is exactly equal, max abs difference 0, on 532 and 416 cells (l301 to l304).
- Also exactly equal: M and the A/A blocks (l313 to l318); levels, per-seed tables and OP-W bias choices of PF, CS, CS_D4 (l320 to l338); HOUSE - PF and the PF / HOUSE levels against housepf_read (l305, l306, l340 to l352); manifest md5s 25 of 25 per arm (l355 to l359).
- Point additivity (X - HOUSE) + (HOUSE - PF) - (X - PF): residual at most 8.7e-19 over 27 metric deltas per arm and cell set (l294 to l297).

## 8. Deviations from the final TTA read's settings (E)
- Runner: the new one above, not run_read_final.sh. The brief's path /home/noob/work/bench_reads/final_tta/run_read_final.sh does not exist; a6e952ec is harness/final/run_read_final.sh (bench_reads/final_tta/MD5.txt).
- nice -n 10 instead of 19 (lead's instruction). No effect on numbers (section 7).
- Arms PF, HOUSE, CS, CS_D4 (no PF_D4, CB, CB_D4); pairs as above. Each contrast draws its own bootstrap stream (random.Random(0) in bench/crossfit_op.py l300), so the pair set changes no interval (section 7).
- Fresh cache (cache_c).
- final_verdict.py and final_class_guard.py not run: no verdict by design; the per-class table is descriptive. Guard items by housecs_tables.py with the final_verdict.py definitions (l16 to l18, l68 to l71); reference R = HOUSE; false crack px against PF printed beside.
- The F-commit checks of run_read_final.sh (bench_wt_fin 821dfad, tree, 10-path code proof) not repeated. The dumps were checked instead by manifest fields (D4 writer 32e0b67c, tta spec, CS_D4 checkpoint = CS checkpoint) and by manifest md5 equality with the final read's read.json (100 of 100).
- Added: every npz md5 against its manifest; manifest md5s against the prior read.json files; sealed-set and live-relay path refusals; PID 5104 and worktree before and after. One path-only dry pass (ROWS_ONLY=1: no md5, nothing written) ran before the read.
- Same otherwise: tool and commit, labels v11, groups, score-exclude, --baseline PF, --aa PF:5,6:7,8, B 2000, boot seed 0, 8 workers, OMP_NUM_THREADS 1, CUDA_VISIBLE_DEVICES empty.

## 9. What this means for protocol 7.1 (S)
- The HOUSE rule is now applied to C2 on CV5. CS_D4 - HOUSE relF1@2 has its lower end above 0 at all four values, points +0.0163 to +0.0204, all >= M 0.0100. It is selection-biased and has no registered rule, so it confirms nothing. It closes the open item "no CS_D4 - HOUSE read exists" (7.1 l312, section 11 l478, row 25 l553).
- C2's edge over HOUSE is smaller than over PF (+0.0163 against +0.0222, 532 OP-A) by HOUSE - PF +0.0059.
- Model part and TTA part: at OP-A, CS_D4 - HOUSE +0.0163 = CS - HOUSE +0.0107 plus CS_D4 - CS +0.0055 (final read.txt l409), about two thirds model and one third D4. CS - HOUSE alone holds 0 at OP-A on both cell sets and excludes 0 at OP-W.
- Strict crack IoU is the metric behind the rule (W1C_READ.md l53 to l56). CS is level with HOUSE (-0.0018 / -0.0029 at OP-A, intervals hold 0). An edge appears only with D4 (+0.0095 to +0.0181), every value inside the band +-0.019. So the HRNet+SWAD model alone does not beat HOUSE on strict IoU in distribution; D4 does.
- Guards against HOUSE: C2's false crack px are 0.09 to 0.17 x HOUSE's. ARTS width at OP-A falls just below 0.85 (0.847, 0.846) because HOUSE draws wide ARTS cracks (1.307 x PF, HOUSEPF_READ.md l26). Against a reference that is itself outside the width band, the width guard measures HOUSE's width as much as C2's.
- As written, the rule compares an 8-view arm with a single-view reference. D4 alone adds +0.0134 to PF (final read.txt l385), so a HOUSE_D4 would likely close part of the gap (not measured). A like-for-like CS_D4 - HOUSE_D4 needs 25 dump-only GPU jobs on cv02: a new run, outside this read and the user's 22 Nov 11:40 ruling (PROTOCOL 5.6). Options for the lead: (a) keep the rule and cite CS - HOUSE as the like-for-like line; (b) say in 7.1 that the HOUSE line is single view against the arm's own inference mode; (c) ask the user for HOUSE_D4 dumps.
- Possible 7.1 row (the lead edits): "CS_D4 - HOUSE (HOUSE rule; selection-biased; printed intervals, no registered rule) | +0.0163 [+0.0051, +0.0284] | +0.0194 [+0.0080, +0.0319] | +0.0164 [+0.0033, +0.0318] | +0.0204 [+0.0073, +0.0369] | strict +0.0110 [+0.0029, +0.0198], inside the band | ARTS width 0.847 / 0.846 (OP-A, 532 / 416) | decides nothing | HOUSECS_READ.md s1, s4".

## 10. Limits (S)
One machine for training (cv02), one split (cv5v3), 5 seeds, argmax and width-matched operating points, development pool cells only. CS arms selection-biased; HOUSE single view only. Nothing here is a verdict.
