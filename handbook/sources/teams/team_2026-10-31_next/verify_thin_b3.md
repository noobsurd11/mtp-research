# coach verify: protocol_thin_b3 opening (SKR / CLD / B3 vs SUP100-PF, seeds 5-9; 100% labels, gaint, el_thin c9bbb02)

coach (successor session), 1 Nov 2026. Independent recompute. Tags: E (file), S (judgement). E1 opening #2.

## Inputs and code
- **Opening:** 15 runs trained rc 0 by 19:39:03; `thin_post.sh` ca436052, 19:40:18-21:13:45, `thin scoring done: post rc=0`. GS 9,900; min free GPU memory during the opening 19,344 MiB (`results/thin/gpumem.log`).
- **Where I recomputed (disclosed):** laptop memory was short (team-lead, ~19:10), so the recompute ran on gaint CPU (nice 19, 8 threads, CUDA hidden), reading the opening's files in place after `md5sum -c` of both MANIFESTs: THIN post **5d3f5b31** (305 files) and PF2 comparator post **3827f7c0** (= my predecessor's PF2 pull). Only text outputs came back: `results/thin/coach_v/` (MD5 file there).
- **Code (coach's own):** `scripts/coach/coach_verify_thin_gaint.sh` 4271b0e6; test primaries (two sets, tau 0 / tau 1, scuff-ignored test) by `team_2026-10-29_features/scripts/coach_verify.py` b0456b28; E1 co-primary, B5 co-primaries (recomputed from calib's raw per-cell records with my own curves / OP code) and B3 readouts by `scripts/coach/coach_thin.py` 7562d97f. Self-test before the opening: B5 reproduces all 36 PF2 B5 lines exactly; E1 relF1@2 reproduces PF2's +0.0365; gaint output byte-identical to the laptop's (a2f8e217).
- **Cross-checks:** my B5 arm-pooled values equal calib's frozen pooled summaries (`post/b5/sum/*.pooled.json`) to 4 dp for all 3 arms × 2 sets. **vs runner's local readout: CONFIRMED.** runner's pull `results/thin/raw/` (MANIFEST 5d3f5b31, 305 files) = the gaint files I read; `thin_post_local.sh` a6369600 outputs `m2_rung_{SKR,CLD,B3}.txt` (553a8419 / f95ea413 / a61235f8) and `_tau1` (77e804c8 / d2358d5f / 7cdf4d89), `thin_e1_relf1.txt` (frozen 98bcb979; 9cbe10ef): every test primary (both sets, tau 0 and tau 1), the bootstrap CIs, and the E1 relF1@2 per-seed values, means, thresholds and readings equal mine to 4 dp.

## Integrity (E, `results/thin/coach_v/integrity.txt`)
- REVISION = HEAD = c9bbb02, 0 tracked changes. 15/15: one run header, step 20000, 0 Tracebacks, 400 PF lr lines; thin-term lines 400 per SKR / CLD run, 0 for B3; configs = seed + the arm's one change (SKR `skel_recall.weight 1.0`; CLD `cldice weight 1.0 iters 10`; B3 `num_classes 25, scuff_class 24, mask_subdir masks_escdd_s`); `config OK` for all 15, no HOLD / CONFIG FAIL.
- Scorer md5s 1e41202b / 419486b1 / 7aa7d6d8 / f6d77562 (= protocol); comparator MANIFEST re-check written; tau0 == default cells, step 20000, code_revision c9bbb02 for all 15; comparator ext-scuff cells == PF2's m0 ext cells (True); scuff_train_iou 10 runs, CPU fp32, step 20000; B5 self-checks 45 / 45 PASS (exact, cuda); every secondary / extra pass rc 0.
- runner's set -e finding (an early `[ ]` failing in an `&&` chain does not abort `thin_post.sh`): the checks above re-verify those conditions independently; all hold.
- 20k encoder cosine vs ImageNet R34 (PF kept the encoder in every arm): layer3 0.925-0.932, layer4 0.927-0.946.
- Thin-term magnitudes (5k-block means): SKR 0.150 → 0.054; CLD 0.418 → 0.163 (all seeds alike).

## Verdicts (protocol_thin_b3 §4: rule 1 /3, 5 v 5; PASS = ≥ 1 co-primary BETTER and none WORSE; test co-primaries by the two-set rule)
| co-primary | SKR − SUPPF | CLD − SUPPF | B3 − SUPPF |
|---|---|---|---|
| test crack IoU (all / clean; thr) | **−0.0136 / −0.0140 (0.0100) WORSE** | −0.0041 / −0.0042 n.d. | +0.0009 / +0.0016 n.d. |
| test crack relF1@2 | +0.0028 / +0.0028 n.d. | −0.0020 / −0.0018 n.d. | −0.0008 / +0.0001 n.d. |
| test inactive IoU | −0.0170 / −0.0161 n.d. (thr 0.040) | −0.0114 / −0.0106 n.d. | −0.0099 / −0.0095 n.d. (thr 0.025) |
| B5 comp recall @ comp P ≥ 0.90, arm-pooled OP | **+0.0413 / +0.0417 (0.032) BETTER** (b 1.4) | −0.0180 / −0.0182 n.d. (b 1.8) | (reported) +0.0201 / +0.0203 |
| B5 relR@2 @ relP@2 ≥ 0.90, arm-pooled OP | +0.0114 / +0.0116 n.d. (b −4.0, **unreachable**, flagged) | **−0.0374 / −0.0376 (0.015) WORSE** (b −1.6) | (reported) +0.0011 / +0.0012 |
| E1 crack relF1@2 (all 106, one set) | **+0.0590 (0.0392) BETTER** | +0.0367 (0.0415) n.d. | +0.0013 (0.0408) n.d. |
| **Verdict** | **FAIL** (test crack IoU WORSE) | **FAIL** (B5 relR@2 WORSE) | **n.d.** |

- Flags: crack relP@2 drop at argmax > 0.05: **SKR FLAG (−0.070 / −0.070)**; CLD −0.019 ok; B3 −0.004 ok. Speck guard at the arm-pooled comp OP (test): speck share SUPPF 0.011, SKR 0.004, CLD 0.004 (lower), B3 0.015 (slightly higher; B3's B5 values are reported only); all-size comp precision SUPPF 0.598, SKR 0.662, CLD 0.837, B3 0.449.
- SKR's relR@2-at-relP ≥ 0.90 OP is **unreachable on val** (pooled val relP@2 max 0.894, at the grid floor b −4.0): by calib's frozen rule the value is read at the max-precision b and flagged; it does not change the verdict.
- LA tau 1 (reported): SKR crack IoU −0.027 WORSE, CLD −0.012 WORSE, B3 n.d. Scuff-ignored test (reported): same pattern as the verdict sets.
- Per-run OPs (reported): SKR comp recall +0.028 n.d. (b_comp −4.0 … 2.4), CLD relR@2 −0.037 WORSE, B3 n.d.

## Reading (S, with E)
- **SKR is a recall push, as expected (§6).** At argmax on test: crack recall 0.620 → 0.791, precision 0.650 → 0.513, relR@2 0.834 → 0.904, relP@2 0.942 → 0.871. The crack-IoU loss sits in CFVS (−0.040) and CSIR (−0.029); ARTS +0.074, BMRK +0.035. **Without the 7 D6 twin cells SKR is BETTER on crack IoU (+0.0116) and relF1@2 (+0.0147)** (reported subset, not a verdict set; CLD shows the same twin / no-twin split, −0.025 on the twins / +0.0100 without, judge). Both arms trained on the same twins, so the twins are not the mechanism: SKR's loss is precision from wider predictions (test predicted / GT crack px 0.954 → 1.545, coach-checked; relP@2 flag −0.070), concentrated on the largest cracks, and narrow (bootstrap all 50 [−0.036, +0.012]; leave-top-3-out +0.007 coach / +0.010 judge's variant). At precision matched on val, the recall gain survives on test (comp recall +0.041) and is large on E1 (comp recall +0.103, relR@2 +0.060). On E1 SKR is the strongest crack arm so far on the width-robust measures: **relF1@2 +0.059 (co-primary) and any-hit component recall 0.381 → 0.523 (+0.142, judge)**; pixel recall (0.199 → 0.369) and pixel IoU are inflated, because SKR's ~1.5× fattening matches E1's ~1.5× wider GT (judge). Costs: crack precision 0.428 → 0.337; crack px on E1 crack-free cells 3,931 → 9,428 (×2.4, coach-checked) and on E1 scuff 8,830 → 18,067 (×2.0).
- **CLD:** at argmax, crack recall 0.620 → 0.710 and precision 0.650 → 0.568 on test; at its arm-pooled val OP (b −1.6) its relR@2 is lower (0.872 → 0.835) while its test relP@2 is 0.932 vs SUPPF's 0.900: **over-precise on test at its val OP; no better at matched precision** (at matched test precision, descriptive, 0.868 vs 0.873; judge). E1: crack recall +0.107, crack IoU +0.049 (BETTER by the arithmetic, descriptive), relF1@2 +0.037 n.d.
- **B3: "scuff class not learned; the arm's effect is the relabelling of 649 train crack px"** (pre-stated rule: train scuff IoU 5-seed mean < 0.10; E: 0.0000 for all 5 seeds; mean p(scuff) on GT scuff px 0.0009-0.0029 vs 1.6e-5-4.3e-5 elsewhere, ratio 28-178, no px > 0.1). Train crack-on-scuff px (CPU fp32, both arms): SUPPF 222 → B3 0 (the relabelled px are now background). E1 crack-on-scuff 8,830 → 8,184 (−7.3%; expectation was −20% to −60%), and non-specific: B3's E1 crack px off scuff fall more (−32%, judge), so it is not a scuff effect. Train scuff IoU 0.000 is real (tp 0, fp 0, every seed; judge). E1 scuff px 84,511 in 38 cells (= protocol). All primaries n.d.; test inactive bootstrap all 50 [−0.024, −0.000], P > 0 0.03 (reported; rule 1 n.d.).
- **E1 strata (descriptive):** SKR gains crack in both groups (scuff + half-cut 29: relF1@2 +0.096, recall +0.144; other 77 recall +0.248); CLD gains recall in both; B3 nothing.

## What this decides (S)
- **No THIN-B3 arm passes. BEST stays SUP100-PF.** B3 as spec'd is closed (class not learned); a weighted or Dice-on-scuff variant would be a new arm needing its own OK (protocol §8).
- **SKR fails on the pre-registered rule,** but it is the first arm that moves E1 crack substantially (relF1@2 +0.059 BETTER, any-hit component recall +0.142; pixel recall is inflated by fattening) and its test loss is precision from wider predictions (pred / GT 0.95 → 1.54, relP@2 flag −0.070), concentrated on the largest cracks and narrow (bootstrap [−0.036, +0.012]). If a follow-up is wanted (user decision, not a re-reading of this opening): SKR with an operating point chosen on val, or a smaller SKR weight (paper Sec. 4.4 tested 0.1), as a new pre-registered protocol. Its val relP@2 does not reach 0.90 on the bias grid, so a precision target would need a wider grid or a lower weight.
- **CLD fails** (relR@2 at matched precision WORSE); no follow-up suggested.

## Disclosures
- judge tailed THIN stdouts at ~18:49 and saw the trainer's end-of-run TEST blocks of 13 THIN runs; nothing was recorded; judge's recompute uses opening files only (judge, log 18:58). The house trainer prints those blocks for every run (no switch); no other reader of them is known.
- builder's 31 Oct quarantined CPU batch (protocol §0) touched no seed 5-9 run.
- Comparator numbers (PF2's SUPPF s5-9) were known before this opening; this protocol was locked before PF2's opening (§2).
- E1 had been read many times before 31 Oct (e1_openings.md); this is E1 opening #2 for these 15 models.

## judge: adversarial check (2026-11-01 21:29 IST; verify_thin_b3 as of md5 a26a14a9; THIN raw MANIFEST 5d3f5b31 md5sum -c OK; comparator = PF2 raw 3827f7c0)
**Verdicts CONFIRMED: SKR FAIL, CLD FAIL, B3 n.d. ("scuff class not learned").** No arm passes; BEST stays SUP100-PF. Three readings need correcting (below).

Code (own, laptop, opening files only):
- `judge/thin_recompute.py` 823bb60e (self-tested on PF2 to 4 dp);
- `judge/thin_extra.py` 90e1f5e9 (unreachable-OP fallback = calib's max-precision rule);
- `judge/thin_skr_check.py` 0be12412.

Outputs: `judge/out/thin_{recompute,extra,skr_check}_out.txt`.

**Recompute (E):**
- Every co-primary in coach's table matches to 4 dp: test crack IoU / relF1@2 / inactive IoU in both sets, both arm-pooled B5 co-primaries in both sets, E1 relF1@2, and every threshold.
- The verdicts follow.
- So do the flags: SKR relP@2 −0.070 / −0.070; the SKR rel OP is unreachable (val relP@2 max 0.894 at b −4.0).
- The speck / all-size comp precision values match, as do E1 crack recall / IoU / precision for all arms, train crack-on-scuff (SUPPF mean 222 → B3 0) and E1 crack-on-scuff (8,830 → 8,184).

### 1. SKR: FAIL stands; the WORSE is narrow, and the no-twin subset is not evidence against it
**E:**
- The rule-1 WORSE on test crack IoU (−0.0136, thr 0.0100) rests on few cells:
  - paired image bootstrap (seed-pooled counts) [−0.036, +0.012], P(Δ < 0) 0.83;
  - **leave-top-3-cells-out +0.0097**: `CFVS_00018_r4_c4` and `CFVS_00027_r4_c4`, 10.9k and 10.2k GT px each, carry most of it.
  - It is as fragile as PF2's relF1@2 pass (leave-top-3-out +0.0015), and should be reported with the same caveat.
- The 7 D6 twin cells hold 39.5% of test crack px; they are the largest, thickest cracks.

  | Subset | crack IoU | pred/GT px | pixel P | rule 1 |
  |---|---|---|---|---|
  | 7 twins | 0.586 → 0.536 (−0.050) | 1.12 → 1.65 | 0.700 → 0.561 | – |
  | 43 others | 0.386 → 0.398 (+0.0116) | 0.85 → 1.48 | – | thr 0.0101 |

  - **CLD shows the same split** (twins −0.025; others +0.0100, thr 0.0103). So the split marks the cells where any recall-pushing loss's wider masks cost most precision. It is not an SKR-specific excuse.

**What is wrong in the verify's reading (S):**
- "the twins are cells the comparator matches closely (its train twin)" is wrong as a mechanism. **Both arms trained on the same twins.** The loss is fattening (test pred/GT 0.95 → 1.54; relP@2 −0.070, the pre-registered FLAG) on large cracks.
- The subset is a pre-registered D6 report line, not a verdict set. Coach labels it that way. But "What this decides" says "its test loss is precision on near-duplicate cells". Please replace that with: **"its test loss is precision from wider predictions (pred/GT 0.95 → 1.54, relP@2 flag −0.070), concentrated on the largest cracks; narrow (leave-top-3-out +0.010)"**.

**B5 component recall BETTER is robust (E):**
- Over the 25 LOSO operating-point choices, min +0.028 and 0/25 WORSE.
- Test comp precision at the OP is matched (0.849 vs 0.846).
- Per-run OPs give n.d. (+0.028), as coach reports.

### 2. SKR on E1: the detection gain is real; pixel recall / IoU overstate it (the width caveat)
**E:**
- The gain is detection, not width:

  | E1 readout (GT comps ≥ 20 px, 296) | SUPPF | SKR | Δ |
  |---|---|---|---|
  | any-hit component recall (≥ 1 GT px within 2 px; width-insensitive) | 0.381 | 0.523 | +0.142 |
  | protocol's ≥ 50% component recall | 0.228 | 0.365 | +0.137 |
  | relR@2 | | | +0.142 |

- It costs precision on E1:
  - pred / GT crack px 0.47 → 1.10;
  - crack px on the 74 crack-free E1 cells 3,931 → 9,428 (×2.4);
  - crack px on E1 scuff 8,830 → 18,067 (×2.0; per seed 17.2k-18.7k vs 7.5k-10.1k);
  - relP@2 −0.059 (> 0.05);
  - pixel precision 0.428 → 0.337.

**S:**
- SKR widens predictions by about 1.5x (test pred / GT 1.54). E1 GT is about 1.5x wider than train (3.66 vs 2.41 px). So **E1 pixel recall (0.199 → 0.369) and E1 crack IoU (+0.057) are inflated by a width coincidence.**
- Quote SKR's E1 gain as relF1@2 +0.059 (the co-primary), any-hit component recall +0.142 and relR@2 +0.142, each with its false-alarm cost (crack-free px ×2.4, scuff ×2.0). Do not quote pixel recall ×1.9.

### 3. CLD: FAIL stands; the B5 WORSE is mostly an operating-point transfer
**E:**
- The relR@2 WORSE is stable: LOSO pooled OPs b −1.2 to −1.9; WORSE in 25/25; both sets.
- But at its val-chosen b (−1.6), CLD lands at **test relP@2 0.932 vs SUPPF 0.900**, so it is over-precise on test.
- At matched **test** precision (test-oracle, descriptive, chooses nothing: max test relR@2 s.t. test relP@2 ≥ 0.90 per run), CLD has 0.868 vs SUPPF 0.873 (−0.006). Most of the −0.037 is the operating point's val → test shift.

**S:**
- The verdict is right by the pre-registered (deployable, val-chosen) rule.
- Coach's mechanism "its extra crack px are the less useful ones" is not shown. Write: "CLD's val-chosen OP is over-precise on test; at matched test precision it is no better than SUPPF". The conclusion (no follow-up) is unchanged.

### 4. B3: "scuff class not learned" CONFIRMED; its E1 crack-on-scuff drop is not scuff-specific
**E:**
- **Train scuff IoU is 0.000 in all 5 seeds, with tp 0 and fp 0.** The class is never predicted anywhere on the 12 train scuff cells.
- The channel exists and responds weakly: mean p(scuff) on GT scuff 0.0009-0.0029 vs 1.6e-5-4.3e-5 elsewhere (ratio 28-178; p90 ≤ 0.010). E1 scuff-predicted px = 0.
- The 0.000 is therefore a real "not learned", not a scorer artefact.
- E1 crack-on-scuff −7.3% (8,830 → 8,184) is **not specific**:
  - crack px off the scuff in the same 38 cells −32% (1,517 → 1,027); other E1 cells −2.4%;
  - per-seed ranges overlap (B3 6,252-10,437 vs SUPPF 7,522-10,127).

**S:** B3 as spec'd = a 649-px crack → background relabel with no measurable E1 scuff effect. Closed, as coach says.

### 5. Disclosure wording
- My stdout tail was at ~18:49, not ~18:52 (corrected in log 18:55).

**For the user (S):**
- No THIN-B3 arm passes.
- SKR is the first arm that clearly lifts E1 crack detection (relF1@2 +0.059 BETTER; any-hit component recall +0.142). It pays with wider masks and about 2x the false-alarm px on E1 and test.
- A follow-up is the user's call and would be a new pre-registered protocol. It should carry:
  - SKR weight 0.1 (paper) or a val OP on a wider grid;
  - a precision guard (crack-free px, relP@2) as a co-primary;
  - a width-insensitive E1 detection readout (any-hit component recall).
