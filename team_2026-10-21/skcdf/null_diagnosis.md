# Why SK1 (SKCDF's balanced head) gave no gain: null diagnosis

Agent 4 (SKCDF critic), lead author, 22 Oct 2026. Second opinion: agent 2, `second_opinion_a2.md`, kept as a separate file.

**Inputs**
- My own inference probes on cv02 GPU 5 (inference only, booked in the ledger):
  - `verify_a4/c4_percell.json`: per-cell counts for 25 runs;
  - `verify_a4/c4_probe.json`: per test-crack component, 211 components, all 25 runs;
  - `verify_a4/probe_summary.txt`, `missed_all.png`, `adj.json`.
- Agent 3's data pack `diag_agent3.md`: training-log trajectories.
- `results.md`, `review_v2.md`.
- The SKCDF paper and its code (`12f807d`).

**Conventions**
- Verdicts come from the locked rules. Everything marked **Reading** is interpretation.
- "Relaxed recall" is the share of GT crack px within 2 px of a predicted crack px.
- "Confident miss" is a GT crack px with p(crack) < 0.001.

## 0. Bottom line
1. **The crack null is real, not a power failure.** The paired cell bootstrap for BsDB5 − BsD5 crack IoU is [−0.0099, +0.0016]; any gain above about +0.002 is unlikely. Inactive is underpowered (threshold 0.028; 2 labelled inactive cells).
2. **ABSH was active, but it acted on the wrong thing.** It corrects the class prior on the labelled cells. On those 23 cells the prior was already right, because a 5% model memorises them. The test failure is different: crack is under-predicted (predicted/GT crack px 0.59–0.74 on test) and about half of GT crack is a confident miss. ABSH cannot reach either. Two port effects also blur the test:
   - the evaluated head is overwritten by the balanced head at the end of training;
   - background pseudo-labels are lost, early in BsDB5 and late in BsDBn5.
3. **The misses are concentrated, and not on the classes ABSH balances.** They sit in:
   - low-contrast cracks: relaxed recall 0.42 in the lowest-contrast third vs 0.80 in the highest;
   - cracks on the edge of an inactive region (12% of test crack px): recall 0.44 vs 0.69;
   - ARTS and BMRK cells: 0.30 and 0.40 vs CFVS 0.80.
   Every arm misses the same 40 components.
4. **Recommendation:**
   - stop the SKCDF line (user's go: ABSH stopped, including S-c);
   - keep S-a (logit adjustment) as the yardstick for any crack claim;
   - S-b does not run: agent 2's pool probe leaves H-cm inconclusive under its locked thresholds, so the gate is not passed (§2.5);
   - put the next effort into the low-contrast and inactive-boundary cracks (§4), which no method so far reaches.

## 1. Is the null real, or a test that could never have shown a gain?

### 1.1 Power (5 v 5, rule 1)
**Detectable differences** (rule-1 thresholds for BsDB5 − BsD5): crack IoU 0.0100 (the floor), inactive IoU 0.0282, relF1@2 0.0100. As shares of BsD5's own gain over supervised (+0.024 / +0.131 / +0.036), that is 41% / 22% / 28%.

**What the cells say** (paired image bootstrap, 2,000):

| Metric | Δ | 95% CI | Reading |
|---|---|---|---|
| crack IoU | −0.0044 | [−0.0099, +0.0016] | rules out gains above about +0.002 |
| relF1@2 | +0.0044 | [−0.004, +0.015] | |
| inactive IoU | −0.011 | [−0.036, +0.023] | uninformative |

**Verdict:**
- crack: an informative null;
- inactive: not testable at 5% (doc 13 A1/A2).

### 1.2 Was ABSH actually active? Yes.
- **Keep rates** (diag D3):
  - labelled aux keep 0.039 (no band) and 0.044 (band), as designed: crack p = 1, inactive 0.876, background 0.0049;
  - unlabelled aux keep 0.20–0.26 early, annealing to 0.04.
- **Head transfer** (diag D2):
  - head_drift 3–5 at 4k, then 0.04–0.06 at 18–20k;
  - at 20k the evaluated main head *is* the balanced head (main vs aux test IoU within 0.002 in every run).
- **The evaluated head changed:**
  - AB5 is below A5c over cells (crack −0.008 [−0.012, −0.005]);
  - BsDB5 ≠ BsDBn5 (rule 3 WORSE).
- **Supervised loss of the evaluated head at the end** (diag D2): BsD5 0.023, BsDB5 0.111, BsDBn5 0.220, AB5 0.067, vs A5c 0.013.
  - Reading: the 1%-per-step pull toward the balanced head does not decay with the cosine LR, while the fitting gradient does. So the final head is "the balanced head", not "a head nudged by it". SKCDF trains with SGD poly and selects by best val, so its evaluated state may come before this end point (not verified).

### 1.3 Did the confidence threshold or the EMA teacher suppress the balanced path?
- **Early: yes, partly.**
  - With an EMA 0.999 teacher, confident pixels were ~0 for the first few hundred steps (smoke runs).
  - BsDB5 had almost no confident background pseudo-labels until 4–6k: background 0.01–0.02 of unlabelled px at 2.5–4k, against 0.63–0.65 for BsD5 (diag D1).
  - So the main unlabelled loss lost most of its background targets early in BsDB5. That makes the primary contrast "rebalancing **plus** less background self-training": one switch, two mechanisms.
- **Late: in BsDBn5 only.**
  - Confident background fell to 0.000–0.003 from about 16k in all 5 seeds (diag D1).
  - Checked in the raw `pseudo_labels.csv` at 20k: s0 has 0 background of 282 M confident px; BsD5 s0 has 720 M of 1,009 M.
- **The balanced path itself was never starved.** aux_keep_u > 0 from about 1k. Its crack pseudo-label share was 0.0037 (BsDBn5) and 0.0010–0.0015 (BsDB5) early, against a main-PL crack share of 0.0011–0.0015.

### 1.4 Did the band hurt? Yes, on crack IoU (rule 3 WORSE in all four cell sets).
- It kept background negatives within 2 px of every crack, so it bought precision (relP@2 +0.026 vs BsDBn5) and lost recall.
- Crack IoU here is recall-limited (BsD5 precision 0.618, recall 0.412), so the trade lowers IoU.
- My review approved the band on an a-priori width argument without asking which side, precision or recall, limits IoU. That was a review miss.

### 1.5 What SKCDF's ablation assumed vs what we have

| | SKCDF (Synapse, Table 3) | SK1 |
|---|---|---|
| Data | 3-D CT, 13 organs, 20% = 4 labelled volumes, fixed anatomy | 2-D EL, 23 cells, cracks anywhere, 1–3 px wide |
| What ABSH fixed | classes at 0.0 Dice: gallbladder / esophagus 0 → 62; other small organs move little | crack is never collapsed: test IoU 0.30, labelled-batch prediction = GT rate |
| Baseline for the DF/ABSH gains | plain current-model PL, no threshold, joint BN, λu up to 10 | EMA teacher, PL ≥ 0.95, separate BN, λ = 1 (BsD5) |
| Optimiser / selection | SGD 0.3 poly, best val | Adam cosine, final step |
| Seeds | 3 | 5 |

**Reading.**
- ABSH is a cure for prior collapse: a class the model never predicts.
- Our crack is under-predicted on test (§2.1), but not collapsed on the training cells, which is the only place ABSH's loss sees.
- A null was the expected outcome. Neither critic predicted it at review.
- The parts of SKCDF that made its baseline weak (no threshold, λu = 10, joint BN) are exactly what our P13 recipe already fixed. That is the same reason P17's DF port found nothing.

## 2. Mechanism: where crack is missed

### 2.1 Under-prediction on test, not on train
- **Predicted / GT crack px on test** (pooled, seed mean): A5c 0.593, AB5 0.578, BsD5 0.667, BsDB5 0.640, BsDBn5 0.738.
- **On the labelled training batch** (diag D3; agent 2's check): main and aux predicted crack share equal GT within 5% at 4k and 20k.
- Reading: the model fits the 23 cells. ABSH's loss sees only those cells, and on them the prior is already right. The deficit appears only on unseen cells.

### 2.2 Confident misses (test, pixel-weighted, seed mean)

| Arm | px recall | relaxed recall | confident-miss share | px in components missed entirely |
|---|---|---|---|---|
| A5c | 0.371 | 0.603 | 0.569 | 0.091 |
| AB5 | 0.360 | 0.597 | 0.572 | 0.103 |
| BsD5 | 0.412 | 0.657 | 0.523 | 0.088 |
| BsDB5 | 0.401 | 0.657 | 0.515 | 0.082 |
| BsDBn5 | 0.439 | 0.679 | 0.422 | 0.073 |

- Note: relaxed recall 0.66 means about 34% of GT crack is more than 2 px from any predicted crack on test (BsD5).
- SSL (BsD5 vs A5c) lowers the confident-miss share by 0.05; ABSH with the band adds nothing.
- Only BsDBn5 moves it (−0.10). BsDBn5 is the arm that lost its background pseudo-labels, and on IoU it equals a free logit bias (LA τ = 1: BsDBn5 − (BsD5+LA) = −0.0025).

### 2.3 Which cracks are missed (211 test components; tertiles by pixel-weighted share)

**Labelled-crack contrast** = (mean intensity inside the labelled crack − mean of a 1–3 px ring) / image sd; negative means a darker crack.
- Caveat (agent 2): the revised masks widened crack labels (handbook 17 §5.9). A faint crack labelled wide gets a diluted contrast, so part of the "faint" class may be label width rather than an invisible crack.
- Tertile edges: −0.39 and −0.06.
- Shares of crack px: 48% / 28% / 24%.

| Arm | Relaxed recall, dark (high contrast) | middle | faint (≈ 0 or bright) | Confident misses, faint tertile |
|---|---|---|---|---|
| A5c | 0.745 | 0.561 | 0.364 | 0.773 |
| BsD5 | 0.802 | 0.606 | 0.424 | 0.721 |
| BsDBn5 | 0.809 | 0.645 | 0.452 | 0.636 |

**Length** (tertile edges 33 and 111 px). Short components are missed most: relaxed recall 0.34 vs 0.70 for long ones (BsD5). Short ones hold only 3% of crack px.

**Cracks on an inactive-region boundary** (> 50% of the component within 2 px of GT inactive): 25 components, 12.2% of test crack px.

| Arm | Relaxed recall, boundary | Relaxed recall, other | Confident misses, boundary |
|---|---|---|---|
| A5c | 0.352 | 0.638 | 0.78 |
| BsD5 | 0.439 | 0.688 | 0.71 |
| BsDBn5 | 0.474 | 0.708 | 0.60 |

Without the 7 twin test cells (6 of the 25 boundary components are in them): 19 components, 15% of non-twin crack px. Relaxed recall, boundary vs other: A5c 0.31 vs 0.54, BsD5 0.37 vs 0.59, BsDBn5 0.41 vs 0.62. The pattern holds.

**Source** (relaxed recall, BsD5):

| Source | Relaxed recall | Share of crack px |
|---|---|---|
| CFVS | 0.80 | 57% (includes the twins) |
| CSIR | 0.67 | 12% |
| BMRK | 0.40 | 27% |
| ARTS | 0.30 | 3% |

**Missed by every arm** (seed-mean relaxed recall < 0.1 in all 5 arms): 40 components, 5.4% of crack px.
- Median width 2.0, contrast −0.05 (invisible in intensity), length 38. Other components: 2.83 / −0.25 / 76.
- `verify_a4/missed_all.png` shows the 16 largest of the components missed on average across all 25 runs. Four kinds:
  1. **Cracks drawn along the edge of a dark inactive region** (CFVS_00018/00027 r4_c4, BMRK_00073). The image shows an intensity step, not a line. Labelling convention: crack + inactive overlap.
  2. **The noisy cell** CSIR_00070_r8_c4: the crack is not visible in the noise.
  3. **Faint thin cracks** in BMRK and CSIR_00057: visible, but at the noise level.
  4. **A few clearly visible cracks** (ARTS_00023_r7_c4, the horizontal line). These are true model failures. A 23-cell training set may hold no crack of that orientation or source.

**Reading.**
- The crack deficit is dominated by cracks the image barely shows, or shows as region edges rather than lines.
- No prior shift or pseudo-label rule can recover a crack whose evidence is a convention, not a signal.
- These are also where SSL helps least (+0.06 relaxed recall in the faint tertile), because the teacher is confidently wrong there and the ≥ 0.95 rule turns that into a background target.

### 2.4 The BsDBn5 background-PL collapse, as a mechanism
Sequence (diag D1/D2):
1. The evaluated head converges onto the balanced head, which was trained with background keep 0.005.
2. It stops reaching 0.95 on background (from about 16k).
3. The main unlabelled loss then trains only on padding / structure (0.27 of px) and a few crack and inactive pixels. No background targets remain.
4. In the same arm, confident misses drop by 0.10 and test crack prediction rises to 0.74 of GT. Crack IoU equals the logit-adjusted BsD5. On unseen modules, crack false alarms rise (+0.105).

Reading, weakened after agent 2's pool probe (§2.5). On the pool, BsDBn5's lower bin-0 share comes mostly from **offset** pixels falling (0.18 → 0.10–0.13). True misses barely move (0.37–0.39 → 0.33–0.34). So losing background PLs mainly tightens the near-miss band around cracks the model already finds; it does not recover cracks that were really missed. On IoU a free logit bias does the same. This lowers the expected value of S-b.

### 2.5 Pool probe (agent 2): true misses vs offset on the 448-cell unlabelled pool
Thresholds locked 19:33 IST in `second_opinion_a2.md`, before the probe ran:
- **supported** if true misses ≥ 30% of GT crack AND ≥ 80% of them get a confident-background PL (BsD5);
- **refuted** if true misses < 10%.

Final result (agent 2; all 20 runs rc = 0; 448-cell pool, 216,353 GT crack px, step-20k checkpoints, no test cells; full text in `second_opinion_a2.md`, files in `probe_a2/`). Seed mean ± sd, as shares of GT crack:

| Arm | bin-0 | true miss | offset | confident-bg share of true misses |
|---|---|---|---|---|
| A5c | 0.586±0.012 | 0.415±0.018 | 0.171±0.008 | 0.748±0.023 |
| BsD5 | 0.558±0.009 | 0.378±0.011 | 0.180±0.005 | 0.705±0.021 |
| BsD5+LA | 0.522±0.008 | 0.359±0.011 | 0.164±0.005 | 0.464±0.038 |
| BsDBn5 | 0.454±0.023 | 0.332±0.014 | 0.122±0.019 | 0.002±0.003 |

- Agent 4 re-derived every cell of this table from the per-run counts in `probe_a2/probe.json`: all 20 runs are at step 20,000 and the table matches exactly.
- **Source split, BsD5:**
  - CSIR/ARTS: true miss 0.461, confident-bg 0.836;
  - CFVS/BMRK/SDLE: true miss 0.341, confident-bg 0.625.
- **Verdict (locked thresholds): H-cm INCONCLUSIVE.**
  - True misses 0.378 ≥ 0.30: met.
  - Confident-bg share 0.705 < 0.80: not met.
  - **S-b's gate is not passed.**
- **Reading (both critics):**
  - The misses are real misses, not offset.
  - Background-PL reinforcement explains little of them:
    - LA cuts the confident-bg share to 0.46, but true misses only to 0.359;
    - BsDBn5 has almost no confident-bg PL on its misses (0.002), yet recovers only 0.046 of 0.378 (about 12%).
  - The test-set picture agrees: about 34% of GT crack is > 2 px from any prediction (§2.2), concentrated in faint and inactive-boundary cracks and in ARTS/BMRK (§2.3).
  - So the crack deficit is mostly cracks the 23 labelled cells do not teach the model to see. That is a label-budget and label-convention problem, not a pseudo-label problem.

## 3. What, if anything, about SKCDF is still worth testing

| Candidate | Falsifiable hypothesis | Arm (one change) | Cost | Expected effect | Recommendation |
|---|---|---|---|---|---|
| S-c: ABSH without the transfer into the evaluated head | the null is the end-of-run head overwrite (D2) | BsDB5/BsDBn5 + `absh.transfer_main_l=false` | 5 runs, about 3 h expected (reading): ≤ +0.005 crack IoU; §2.1 says the training prior was already right | **stop** (user: go). The fix answers a port artefact of a method whose precondition is absent |
| S-b: BsD5 without background PLs | background PLs on low-contrast cracks reinforce misses (H-cm) | BsD5 + `pl_exclude_classes=[0]` | 8 + 3 runs, about 7 h expected (reading): crack AP +0.03 to +0.05, IoU ≈ LA level (+0.01), more false alarms. Lowered by §2.5: true misses barely move | **gate not passed** (§2.5 H-cm inconclusive), so do not run. If the user still wants it: co-primaries crack AP and IoU, compared with BsD5+LA, 8 v 8, four cell sets, E1 false alarm |
| λu = 10 (SKCDF's value) under DF | a stronger unlabelled signal into the shared encoder raises crack | BsD5 + `ssl.lambda_final=10` | 5 runs expected (reading, not measured): ≈ 0 on crack, since the gain is gated by the same confident PLs; maybe inactive | do not run: it does not touch the misses in §2.3 |
| Balanced head without a threshold (as in the official code) | thresholding starved the balanced path | BsDBn5 with aux PL t_pos 0 | 5 runs expected (reading): negative; unthresholded PLs on 1–3 px structures are mostly noise | do not run: §1.3 shows the aux path was not starved |
| SKCM (cross-attention L↔U) | labelled features guide PLs | new module | days of work | +1.77 on Synapse (sd 0.9–2.0); its fixed-anatomy premise does not hold | do not port |

**Plain statement.** The right call is to **stop SKCDF**. Its three parts each target a problem our recipe either does not have or already solved:
- DF: P17, n.d.;
- ABSH: SK1, n.d.;
- SKCM: premise absent.

The one live thread, background pseudo-labels on missed cracks, is not SKCDF any more. It belongs to the common question shared with ALHVR (H-cm). The pool probe leaves H-cm inconclusive, and shows that removing background PLs mainly shrinks the offset band, not the true misses. So no SK2 training is recommended.

## 4. Ideas outside SKCDF that the null points to
Every citation is a paper returned by the Research MCP in this session.

1. **Prior shift as the yardstick, and as the cheap fix.**
   - **S-a result** (agent 3; 5% arms recomputed exactly by agent 4): LA τ = 1 adds +0.015 to +0.023 crack IoU to every 5% arm. With LA on both sides, SSL's crack gain survives (BsM5 +0.037, BsD5 +0.024, CsM5 +0.018, all passing). As a yardstick, though, it is no larger than LA alone gives supervised: SSL − (A5c+LA) is n.d. The SSL arms are CsM5, BsM5 and P17 BsD5, at −0.002 / +0.014 / +0.008, in all four cell sets. Inactive gains survive. LA itself gives +0.015 to +0.023 crack IoU at 5%, about +0.01 at 10–20% and about 0 at 50–100%. BsM5 loses 0.08 precision under LA.
   - Paper: logit adjustment (Menon et al., `arxiv:2007.07314`).
   - SK1 measured BsD5+LA +0.013 and A5c+LA +0.015 crack IoU at zero cost. Every SSL crack claim should be reported against its own base + LA (S-a, approved).
   - Falsifiable: on the P13/P17/P18 checkpoints, LA τ = 1 gives crack IoU ≥ +0.01 with a precision drop ≤ 0.05. Inference only.
2. **Class- and distribution-aware pseudo-label thresholds instead of a fixed 0.95.** This attacks the mechanism in §2.3/§2.5 (confident background targets on faint cracks) directly.
   - Papers: DARS, "Re-distributing biased pseudo labels" (`doi:10.1109/iccv48922.2021.00685`); FreeMatch's self-adaptive thresholds (`arxiv:2205.07246`); class-wise adaptive SSL segmentation (`doi:10.1109/access.2024.3363628`).
   - Hypothesis: a background threshold set so that PL background share matches the labelled background share (rather than 0.95) cuts the confident-miss share by ≥ 0.05 without the false-alarm cost of BsDBn5.
   - Only after the pool probe.
3. **Rare-class copy-paste that matches the hard cases.**
   - Paper: AEL's adaptive copy-paste (`arxiv:2110.05474`).
   - Paste low-contrast and inactive-boundary cracks specifically: the cases in §2.3 that every arm misses. They are only 5–12% of crack px but are where IoU is lost.
4. **Spend labels where the misses are.**
   - Paper: region-impurity / uncertainty active learning for segmentation (`doi:10.1109/cvpr52688.2022.00790`).
   - Recall is lowest for ARTS (0.30) and BMRK (0.40), which have no or few counterparts in the labelled 23 or the external pool.
   - A label-budget experiment (which 23 cells to label) may beat any SSL tweak. It also answers the split-seed weakness (doc 13 A9; ideas.md #5).
5. **Label convention for cracks on inactive-region edges.**
   - About 12% of test crack px sit on inactive boundaries, with recall 0.44.
   - Whether these should count as crack, or be scored with a tolerance band, is a labelling and metric question (doc 13 A5, P14), not a training one.
   - A per-component audit of the 40 always-missed components (montage `verify_a4/missed_all.png`) is a 1-hour human task for the user.
6. **Thin-structure losses: not first.**
   - Skeleton Recall (`doi:10.1007/978-3-031-72980-5_13`) targets connectivity, but our misses are faint or edge-type, not broken lines.
   - Its benefit is disputed (`arxiv:2508.11374`). P14 already found no gain from a tolerant loss.

## 5. Data note found during the probe (minor; for the record)
- gaint `el-fault-detection/data/escdd_masks/test` and cv02 `el_p7/data/escdd_masks/test` differ, pixel-wise, in exactly two test cells: `ARTS_00047_r3_c1` (34 crack px) and `ARTS_00051_r3_c2` (202 crack px). These are the P6 old-mask remap pixels (handbook 17 §5.3).
- cv02 has them; gaint does not. All other 102 val/test masks are pixel-identical.
- Every P-series number and every SK1/AL1 number is scored on cv02, so nothing changes. Any test number scored on gaint would differ by these 236 px (0.26% of test crack). Cross-machine comparison is already barred.
- Agent 2 confirms: every AL1 run is trained and scored on cv02. ALHVR D0/D0c ran on gaint, but only on the unlabelled pool, never on test.

## 6. Closing: SKCDF track closed (22 Oct 2026, user: "do as they say")
- **Adopted:** both critics' recommendations.
- **Not to be run:** S-b, S-c, λu = 10, an unthresholded balanced head, or a SKCM port. No SKCDF-derived training is open.
- **Kept:**
  - S-a (LA τ = 1) as the yardstick for every crack claim; verified for the 5% arms (`review_v2.md`, S-a addendum);
  - the D7 side result: BsD5 on the twin-free pool still beats supervised.
- **Next, outside SKCDF:** `labelling_plan.md`, i.e. a retrospective label-budget test (needs approval) and the user's 1-hour audit of the 40 always-missed components.
- **Code left in place, off by default:**
  - `absh.*` (0ea71df);
  - `data.unlabeled_exclude` (used by D7);
  - `pl_exclude_classes` (88a7e88, unused).
