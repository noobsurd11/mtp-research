# HRNet-W18 U-Net++ 5-seed confirmation on cv5v3 (lead, 18 Nov 2026, 06:00 IST)

**Verdict (rule pre-registered in log.md, 18 Nov 00:22, before seeds 8 and 9 existed): NOT CONFIRMED, reported as a gain with failing guard items.** The headline passes at all four required values; two guards fail: false crack pixels on crack-free cells (all four values, 2.90 to 4.15 x PF against the limit 1.5 x) and the ARTS per-source width at OP-W on the clean cells (1.162 against 1.15).

Read: /home/noob/work/bench_reads/c3hrnet_read/run_read_c3hrnet.sh (1878a322), 18 Nov 05:46 to 05:58 on gaint CPU, rc 0; tool bench_wt_final 89b9ea5 (clean before and after) scripts/bench_read_w1.py fdb56b78; --groups cv5v3 (285 groups), --score-exclude score_exclude_v3.txt (6d48dfbd), --aa PF:5,6:7,8. Inputs: cv02 runs only, relayed with checksums, 75 runs (PF = c3_pf_v11, HOUSE = c3_house_v11, HRNET = c3h_hrnet_w18_unetpp_pf; folds 0 to 4, seeds 5 to 9), every manifest RTX A6000 and step 20,000. Tables: results/c3hrnet_read/ (read.txt, read_x416.txt, read.json, run.log, the script, MD5.txt). E = measured, S = judgement.

## 1. Headline: crack relF1@2, HRNET minus PF (E)
| | 532 cells, OP-A | 532 cells, OP-W | 416 clean, OP-A | 416 clean, OP-W |
|---|---|---|---|---|
| delta [95% CI] | +0.0104 [+0.0012, +0.0203] | +0.0117 [+0.0019, +0.0220] | +0.0115 [+0.00001, +0.0259] | +0.0126 [+0.0006, +0.0273] |
| M | 0.010 | 0.010 | 0.010 | 0.010 |
All four pass (delta >= M, low end > 0; on the clean cells at OP-A the low end is 0.000014). Per seed (532 cells, OP-A): +0.0105, +0.0115, +0.0071, +0.0102, +0.0126; every seed positive. The gain is recall at equal precision (relR@2 +0.015 at OP-A, +0.023 at OP-W; relP@2 +0.004 / -0.001), as in the screen (+0.0114 / +0.0128 there).

## 2. Guards (E; point values, inclusive bounds)
| Guard | 532, OP-A | 532, OP-W | 416, OP-A | 416, OP-W |
|---|---|---|---|---|
| width ratio pooled (HRNET / PF) | 0.952 | 1.000 | 0.960 | 0.998 |
| width per source (ARTS / BMRK / CFVS / CSIR) | 1.080 / 0.995 / 0.942 / 0.943 | 1.131 / 1.035 / 0.990 / 0.992 | 1.119 / 0.995 / 0.944 / 0.963 | **1.162** / 1.027 / 0.984 / 1.001 |
| false crack px on crack-free cells (303 / 226 cells) | **767 vs 212 = 3.62 x** | **878 vs 212 = 4.15 x** | **569 vs 196 = 2.90 x** | **647 vs 196 = 3.29 x** |
| inactive IoU delta (>= -M) | +0.0100 | +0.0085 | +0.0023 | +0.0010 |
| mIoU-R13 delta (>= -M) | +0.0022 | +0.0024 | +0.0012 | +0.0014 |
Failing items: false crack px at all four values; ARTS width at OP-W on the 416 cells.

## 3. Secondary, pre-declared (E; decides nothing)
- HRNET minus HOUSE: relF1@2 +0.0045 [-0.0069, +0.0157] (OP-A), +0.0083 [-0.0041, +0.0209] (OP-W); strict crack IoU -0.0171 [-0.0291, -0.0068] at OP-A; mIoU-R13 +0.0072; inactive +0.0001.
- Levels (OP-A, 532 cells, 5 seeds): PF crack IoU 0.365, relF1@2 0.846, inactive 0.504, mIoU-R13 0.612, width 1.02; HOUSE 0.383, 0.852, 0.514, 0.607, 1.13; HRNET 0.366, 0.857, 0.514, 0.614, 0.97.
- False crack px on crack-free cells: PF 212, HOUSE 774, HRNET 767 (OP-A); the share of crack-free cells with 50 or more false px: PF 0.13%, HOUSE 1.2%, HRNET 1.5%. In absolute terms HRNET's excess is about 1.8 px per crack-free cell; PF's partial encoder freeze makes it unusually clean on these cells, so a 1.5 x PF bound is tight for every arm without the freeze (HOUSE, which is not judged here, sits at 3.7 x) (S).

## 4. Consequences (lead)
- HRNet-W18 U-Net++ is **not confirmed** under the registered rule; it is the only arm so far whose headline gain holds at 5 seeds on the corrected split (+0.010 to +0.013 relF1@2 at both operating points on both cell sets). It is reported as a gain with its failing guards named.
- Together with swad_const (not confirmed on the headline, results/C3SWAD_READ.md) there is no confirmed single arm; the c3x combination's final-model rule then has no "best confirmed single arm" to fall back on. The c3x run continues as registered; how the final model is chosen when no arm is confirmed is a question for the user (S).
- Question for the user (protocol, for later arms only; these verdicts stand as written): whether the false-crack-pixel guard should keep comparing against PF at 1.5 x when PF averages under 1 false px per crack-free cell, or use an absolute bound or HOUSE as the reference.

## 5. Limits
One machine (cv02), one split (cv5v3), 5 seeds, argmax and width-matched operating points; the clean-cell OP-A interval sits right at 0.
