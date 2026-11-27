# Final opening read: E1 opening #8 (decides) and test50 opening #19 (public table) (lead, 21 Nov 2026)

Rule: harness/final/opening/OPENING_RULE.md (065a7ddd; review REVIEW_OPENING.md f81cb703 PASS, request fdc08f95). FLAG D4 ruled by
the user 21 Nov about 11:21 IST: "keep D4, go ahead" (C2 and C3 with D4, as approved). E = measured (verdict.txt), S = judgement.
Every number below is copied from results/final_opening_read/verdict.txt (md5 bbb5f3b4); copies listed in MD5_copy.txt (e9169514).

## Run record (E; IST)
- Registered 11:22:35 from a clean shell: REGISTERED.txt **4c783a779208979ccbed8c13802950b2** (jobs 3a308b9c, 30 lines with C1-D4;
  stage manifest 2b838801; E1 mask/ignore and v0 test50 file hashes only). Ledger rows #8 / #19 written 11:23, before any dump.
- G 8bd1c27 deployed to cv02 (CODE.md5 d9a250a2); check OK; stage 157 files (images and lists only); render 0 FAIL; queue `open`
  armed 11:25:30 (MAXC 4, LPG 1, sharing off, disk guard 7). 30 dump-only jobs, **30 dumped rc 0**, ALL DONE 11:58:14; no HOLD.
- Relay to /mnt/nas/noob_el_archive/bench_relay/open: RELAY ALL DONE 30 of 30 at 12:00:29 (md5sum -c OK on both ends per unit).
- Read run ONCE: run_opening_read.sh (2525575e) 12:02:30 to 12:06:09, rc 0, gaint CPU; manifest check 30 dumps, one GPU model (RTX
  A6000); v1.1 file check OK 100 files; records_fail empty; read worktree R 0c72cf9 clean after the read. Output
  /home/noob/work/bench_reads/open_final (MD5.txt: every output md5 checks; its input lines equal the pins: script 2525575e,
  verdict 433f61de, rule 065a7ddd, REGISTERED 4c783a77, fin verdict a95f89e8, v11_filecheck dcc3bfe4).
- Log note (E): 6 numpy 'Mean of empty slice' warnings (bench_open_read.py lines 135 / 152: nanmean over a key that is undefined
  in a subset, e.g. no inactive cell). No read.txt holds a NaN; every decision value is finite.

## Decision (E1, 106 cells, 71 clusters, OP-A)
| Item | Value | Rule | Outcome |
|---|---|---|---|
| **P = C2 - C1, crack relF1@2** | **+0.0430, seed-aware 95% [+0.0013, +0.1043]** (SE 0.0265); fixed-model [+0.0067, +0.1007] | lo > 0 and Delta >= M 0.010 | **CONFIRMED** |
| G1 width C2 / C1 pooled | 1.013 (C2 0.463, C1 0.458) | 0.85 to 1.15 | pass |
| G2 width C2 / C1 on CSIR (101 cells) | 1.013 | 0.85 to 1.15 | pass |
| G3 false crack px, 74 crack-free cells | C2 2421 vs C1 3218 (0.75 x) | <= 1.5 x | pass |
| G4 mIoU-R13 | +0.0249 | >= -0.010 | pass |
| inactive IoU (reported only; 10 cells) | +0.0996 [-0.0310, +0.2162]; fixed-model [-0.0000, +0.2007] | never decides | n.d. |
| strict crack IoU | +0.0263 [+0.0022, +0.0651], outside the convention band +-0.019 | decides nothing | |

**FINAL OPENING VERDICT: E1 P (C2 - C1 relF1@2) CONFIRMED; Delta +0.0430 [+0.0013, +0.1043]; test50: public table only.**

Levels (relF1@2, mean over 5 seeds): C1 0.447 (0.439 to 0.457), C2 0.490 (0.466 to 0.507), C3 0.487, E-PF 0.449, C1-D4 0.445.

## Printed beside (E; decide nothing)
| Contrast | relF1@2 [seed-aware 95%] | other |
|---|---|---|
| C2 - C1-D4 (same 8 views: the model part) | **+0.0451 [+0.0173, +0.0699]** (fixed [+0.0278, +0.0597]) | strict IoU +0.0325 (outside band); mIoU-R13 +0.0043 |
| C1-D4 - C1 (D4 on PF) | -0.0021 [-0.0423, +0.0575] | inactive +0.0908 [-0.0019, +0.1936]; mIoU-R13 +0.0206 [+0.0017, +0.0419] |
| S3 C3 - C2 (ensemble over its members) | -0.0025 [-0.0254, +0.0157] | inactive +0.0274; mIoU-R13 +0.0055 |
| S1 C3 - C1 | +0.0405 [-0.0044, +0.1108] | mIoU-R13 +0.0304 [+0.0102, +0.0508]; inactive +0.1270 [-0.0001, +0.2185] |
| S2 C3 - E-PF (equal-count ensembles; C3 costs 8 x) | +0.0383 [+0.0007, +0.0904] | mIoU-R13 +0.0172 [+0.0005, +0.0363] |
| S4 C2 seed 5 (one deployable model) - C1 | +0.0189 [-0.0403, +0.1068] | inactive +0.1393 [+0.0009, +0.2103]; mIoU-R13 +0.0314 [+0.0109, +0.0508] |
| S5 E-PF - C1 | +0.0023 [-0.0165, +0.0279] | |
| A/A C1 {7,8} - {5,6} | +0.0022 [-0.0425, +0.0507], SE 0.0225 | |

Strata of P (n cells / clusters): CSIR 101 / 66 +0.0433 [+0.0015, +0.0984]; BMRK 5 / 5 -0.1843 [-0.5529, 0.0000];
**full cells 44 / 24 +0.1464 [+0.0420, +0.2278]; half-cut cells 62 / 47 +0.0110 [-0.0289, +0.0722]**; crack cells 32 / 21
+0.0340 [-0.0114, +0.0862]. Components (arm means): crack recall C1 0.262 / C2 0.257, precision 0.559 / 0.650; inactive recall
0.557 / 0.829. Per class (C1 to C2): border 0.544 to 0.682, inactive 0.291 to 0.391, frame edge 0.664 to 0.711, crack 0.163 to
0.189; sp mono 0.243 to 0.166 (the one clear loss).

## test50 #19: public table (E; decides nothing; known leakage)
- Ours on v0 (20211104 masks_coded, 50 cells, OP-A, mean over seeds): **Pratt rule A median IoU crack C2 0.383 (C1 0.337),
  inactive 0.588 (0.570), mean of 3 0.424 (0.405)**; Pratt 2023 model 4c: crack 0.25, inactive 0.38, mean of 3 0.28 (best per
  class 0.26 / 0.32 / 0.38). PV-S3 crack IoU (all px) C2 0.441 (C1 0.418) vs their 0.58 (split and background rule not stated).
  SEiPV family: micro IoU C2 0.896, fw-IoU 0.903; their 'IoU' 0.7447 / 'mIoU' 0.8604 (averaging not defined).
- Ours on v1.1 (our protocol): C2 - C1 relF1@2 +0.0102 [-0.0094, +0.0291] (all 50), +0.0102 (clean 49), +0.0322 [+0.0036,
  +0.0584] (16 cells without a pool cell in their module); strict crack IoU +0.0229 [+0.0082, +0.0368] (outside band). Levels
  C1 0.891, C2 0.901, C1-D4 0.901.
- Leakage (SPLIT_INTEGRITY 5b): 8 test cells are pool cells, 7 neighbouring crops, 19 more share a module; the full-pool models
  trained on all of them. test50 numbers are in-distribution numbers with known leakage, after 18 counted earlier openings.

## Reading (S)
1. The pre-registered primary passes: on the 106 sealed E1 cells, the final candidate (HRNet-W18 U-Net++ + SWAD, D4) beats the
   PF baseline by +0.043 crack relF1@2 at recipe level, with every guard passing. No candidate, readout or threshold was
   selected on these cells, and the final models were never scored on them before. The interval is wide and its lower end is
   near 0 (+0.0013); the fixed-model interval is [+0.007, +0.101].
2. The gain is the model, not the TTA: C2 - C1-D4 (both 8 views) is +0.045 [+0.017, +0.070], while D4 on PF is -0.002 on E1
   crack (it helped inactive and mIoU-R13). This differs from CV5, where D4 on PF gave +0.013.
3. The 5-seed ensemble C3 adds nothing over its members (-0.0025); one deployable seed (s5, the weakest C2 seed on E1) is
   +0.019, not significant. The confirmed claim is about the recipe averaged over seeds, not about one checkpoint.
4. Where it holds: the 44 full cells carry it (+0.146); on the 62 half-cut cells (a cell type absent from the training pool)
   the gain is +0.011, not significant. 101 of 106 cells are CSIR. Absolute E1 levels (relF1@2 about 0.45 to 0.49 against
   about 0.85 on the pool) show a large domain gap.
5. On E1 the effect is about 3 x its CV5 size (+0.043 vs about +0.015 to +0.022), and it is mostly in full cells, so the size
   should be quoted with its interval, not as a point.
6. test50 decides nothing. C2 - C1 there is +0.010, not significant. Against the published Pratt 2023 numbers our models are
   higher, but test50 overlaps our training pool, Pratt's averaging rule is inferred, and PV-S3's split is not stated. These
   rows are context only, never a claim to beat a published model.
