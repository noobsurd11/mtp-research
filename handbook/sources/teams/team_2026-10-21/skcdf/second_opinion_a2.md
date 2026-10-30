# SK1 null: second opinion from agent 2 (ALHVR critic), 22 Oct 2026

**Scope.** This is an independent read of:
- `skcdf/results.md`, `review_v2.md`, `verify_a4/sk1_verify_a4.txt`, `diag_agent3.md` and `protocol_sk2_sketch.md`;
- `results/sk1/pl_counts_4k_20k.md` and `pl_confident_bg_20k.txt`;
- the SKCDF paper (local `literature/pdfs/skcdf_cvpr2025/`, Tables 1 and 3);
- the ALHVR track's D0 diagnostics (`alhvr/design.md`, `alhvr/d0/`).

I recomputed no SK1 number. Agent 4 already did that to 4 decimals. Every number below is quoted from those files. **Reading:** marks interpretation.

## 1. Was the test powerful enough? For crack, yes; for inactive, no.
- **Crack: the null is tight.** BsDB5 − BsD5 crack IoU is −0.0044, with a paired cell-bootstrap CI of [−0.0099, +0.0016]. The seed threshold is 0.0100. Any crack gain above about +0.002 is unlikely over cells, so for crack IoU this is an informative null, not a power failure. relF1@2: +0.0044 [−0.0038, +0.0154].
- **Inactive: underpowered.** −0.0113 [−0.0358, +0.0233] against a threshold of 0.0282. Inactive at 5% rests on 2 labelled cells and about 16 test cells. Nothing can be said either way.
- AB5 − A5c crack is −0.0083 [−0.0121, −0.0049]: a small harm that is consistent across cells.

## 2. Was ABSH active? Mechanically yes. But the condition it was designed for was absent.
- **Active.**
  - head_drift was 3–5 at step 4k;
  - unlabelled keep rate 0.22–0.27 at 4k, annealing to 0.03;
  - the evaluated head moved: AB5 is worse than A5c, and BsDB5 differs from BsDBn5.
  - So the switch did something.
- **What ABSH fixes in the paper.** In SKCDF Table 3 (Synapse 20%), adding ABSH to DF raises average Dice from 57.4 to 63.57 (+6.2; the text says +7.17). The gain sits mostly in a class the base model never predicts: esophagus goes from **0.0 to 62.0**. Other small organs move little (RAG 48.3 → 46.9, LAG 29.1 → 36.7). Table 1 shows the same pattern for the imbalance baselines: their gains are rescues of classes at 0.0 Dice.
- **Our crack is not a collapsed class.**
  - On the labelled batch the main head predicts crack at the GT rate, both before and after ABSH. `main_pred_crack` / `gt_crack` is 0.99–1.01 for BsDB5 at 4k and at 20k (`pl_counts_4k_20k.md`, e.g. s0 0.002779 vs 0.002793).
  - Test crack IoU is about 0.30, not 0.
  - So there is no head prior to correct on the data where ABSH's loss acts.
  - **Correction after agent 4's pushback (22 Oct).** The labelled-batch match is memorisation: a 23-cell model matches the GT rate on its own cells whatever its prior. It is not evidence about the prior. The better statement: ABSH corrects the training-set prior, which was already fine. The deficit is at test time (under-prediction, about 50% confident misses), a generalisation miss that a training-set rebalancing cannot reach. The conclusion is unchanged; the mechanism is as agent 4 states it.
- **Reading.** ABSH is a fix for prior collapse. Our crack failure is a localisation and generalisation failure (§4). A null was the expected outcome. I did not raise this at review; I should have, as an a-priori prediction.

## 3. The two confounds (agreeing with agent 3's D1/D2 and agent 4)
1. **Head overwrite (D2).**
   - The per-step transfer main_l ← aux_l (ω 0.99) does not decay, while Adam with cosine LR stops refitting.
   - By 20k the evaluated head is the balanced head: drift 0.04–0.06, and supervised loss 0.111 (BsDB5) and 0.220 (BsDBn5) against BsD5's 0.023.
   - So SK1 tested "ABSH whose transfer overwrites the labelled fit at the final step". SKCDF uses SGD poly and best-val, which may select an earlier state. SK1 is not a fair test of SKCDF's ABSH as published.
   - Given §2, I still would not expect a fair version to help crack.
2. **Fewer background pseudo-labels.**
   - BsDB5 had almost no confident background pseudo-labels until about 4–6k (0.01–0.02 of unlabelled pixels, against BsD5's 0.65).
   - BsDBn5 had none after about 16k.
   - So the primary contrast BsDB5 − BsD5 is "balancing plus less background self-training", not a single mechanism. The switch is one change, but its mechanism is two.
- **The band.** It always keeps background negatives within 2 px of crack. As intended, it raised precision (relP@2 +0.026 vs BsDBn5). Crack IoU here is recall-limited (BsD5 precision 0.618, recall 0.412), so trading recall for precision lowers IoU. "WORSE" on rule 3 is that trade, not a bug.
- **BsDBn5.**
  - On IoU it is a prior shift: BsDBn5 − (BsD5+LA) = −0.0025 / +0.0013 / +0.0056.
  - Its only unexplained gain is ranking: crack AP 0.366 vs 0.329, and bin-0 0.422 vs 0.482.
  - That gain coincides with both confounds above, so it cannot be credited to balancing.

## 4. The ALHVR view: a common cause, "confident misses that no SSL loss reaches"
**Facts:**
- **Test crack bin-0 share,** the share of GT crack pixels with p(crack) < 0.001: A5c 0.569, AB5 0.572, BsD5 0.523, BsDB5 0.515, BsD5+LA 0.482, **BsDBn5 0.422** (`results.md` §1, §4). About half of all GT crack is predicted "not crack" with high confidence by every arm.
- **ALHVR D0** (surrogate A5c pairs, 448/455-cell unlabelled pool, hidden masks): Ω1, the region where both networks are confident and ALHVR applies no unlabelled loss, holds **65–69% of GT crack** (`alhvr/d0/d0b_noise.json`: 0.689 and 0.654).
- **BsD5's main pseudo-labels** are confident background on 0.69 of unlabelled pixels. Confident crack is 0.0011–0.0016, against a GT crack share of about 0.002–0.003 on labelled batches. D0's BsM-like rule covers only 35–37% of GT crack as crack (`alhvr/design.md`).

**Reading (hypothesis H-cm).** Most crack error is confident misses. Every SSL mechanism we have tried is gated by confidence or agreement:
- the ≥ 0.95 pseudo-label turns a confident miss into a **background** target and reinforces it;
- ALHVR's Ω1 routing leaves it with **no** loss;
- ABSH reweights the labelled loss where predicted shares already equal GT.

None reaches the pixels that drive crack IoU. Only the labelled loss and whatever the encoder transfers can. Two observations fit:
- the only arm that cut bin-0 (BsDBn5) is the one that lost its confident background pseudo-labels;
- SSL gains are large on inactive (+0.11 to +0.13 IoU) but small on crack (+0.02 to +0.03) in every recipe (P13, P17, SK1).

**What could refute H-cm.**
- **Offset, not misses.** Relaxed F1@2 is about 0.75 while IoU is about 0.33. Many bin-0 pixels may sit within 1–2 px of a correct prediction, i.e. label-offset or width disagreement rather than missed cracks. If so, H-cm is wrong and the lever is the label convention (A5/P14 territory), not SSL.
- **Too few labelled cracks.** Confident misses may be cracks the 23 labelled cells never show, such as a crack type or source. Then no unlabelled loss of this family can help, and H-cm reduces to "too few labelled cracks".

## 5. Falsifiable next steps, in my order, and a stop
1. **Stop the ABSH line, including S-c.** Its precondition, a collapsed class, is absent at 5% for crack (§2). S-c would test a port artefact of a method that should not help here. I recommend no GPU time for it.
2. **Confident-miss probe (inference only, about 1 h on one GPU, no training, test not needed).**
   - Final checkpoints: A5c, BsD5, BsDBn5 and BsD5+LA, all seeds.
   - Cells: the 448-cell unlabelled pool, with hidden masks.
   - Measure:
     - (i) share of GT crack with p(crack) < 0.001;
     - (ii) of those, the share more than 2 px from any predicted crack ("true misses") vs within 2 px ("offset");
     - (iii) of the true misses, the share that receive a confident (≥ 0.95) background pseudo-label from the BsD5 teacher;
     - (iv) the same split by source (CSIR/ARTS vs CFVS/BMRK/SDLE).
   - **Fixed in advance:**
     - true misses ≥ 30% of GT crack **and** ≥ 80% of them confident-background in BsD5 → H-cm supported;
     - true misses < 10% → H-cm refuted; crack error is offset/width, and SSL work on crack should stop.
   - This can also run on the AL1 checkpoints when they finish, with the Ω1 share of true misses.
3. **AL1 as an out-of-sample check of H-cm** (already running and pre-registered; no change). H-cm predicts:
   - AL5 − A5 crack gain no larger than BsD5's;
   - AL5's crack bin-0 within ±0.03 of A5's;
   - S1 (CPSm5 − CPS5, Ω1 masked) n.d. or worse on crack.

   I state these now, before any AL1 test number exists.
4. **S-a (logit adjustment on existing checkpoints): agree.** Cheap. It should become the yardstick: any crack gain claimed for a method should also be reported against its own base + LA.
5. **S-b (BsD5 without background pseudo-labels): only if step 2 supports H-cm.** If it is run:
   - crack AP and bin-0 as declared co-primaries, with 8 v 8 seeds;
   - the E1-extension false-alarm check;
   - H-cm predicts bin-0 ≤ 0.45 and crack AP ≥ 0.35. A result near BsD5 refutes the "background-PL suppression" half of the story.
   - I rank it above S-c because it tests the common cause directly.

**Bottom line (reading).** SK1's null is real for crack (tight CI), expected given the paper's own mechanism, and doubly confounded in its mechanism. The more useful lesson is shared with ALHVR: our SSL losses never touch confident crack misses. Whether those misses are real misses or label offset is the next question. A one-hour inference probe can answer it before any further training.

## Addendum: probe (b) thresholds, locked 22 Oct 19:33 IST, before the probe runs
The coordinator gave the go: inference only, no training, no test data. These thresholds are fixed now, before any probe number exists.

**Setup**
- **Cells:** the 448-cell seed-0 5% unlabelled pool (D7 list removed), revised masks (`masks_escdd`).
- **Checkpoints:** final step-20k `latest.pth` of A5c (s0–4), BsD5 (`sk1_BsD` s0–4, EMA teacher) and BsDBn5 (`sk1_BsDBn` s0–4, EMA teacher). Also BsD5 + LA with τ = 1.
- **Inference:** weak view, bf16, as in `rescore_logit_adjust.py`.

**Definitions**
- **Confident miss (bin-0):** a GT crack pixel with p(crack) < 0.001.
- **True miss:** a confident miss lying more than 2 px (Euclidean distance transform) from every pixel predicted crack (argmax) in the same cell.
- **Offset:** a confident miss within 2 px of a predicted-crack pixel.
- **Confident-background PL:** max softmax ≥ 0.95 with argmax = background (class 0), from the same checkpoint.

**Reported per run, pooled over cells (seed mean ± sd)**
- (i) bin-0 share of GT crack;
- (ii) the true-miss share of GT crack, and the offset share;
- (iii) the share of true misses that get a confident-background PL;
- (iv) (ii) split by source: CSIR/ARTS vs CFVS/BMRK/SDLE.

**Decision for H-cm (on BsD5, seed mean)**
- **Supported:** true misses ≥ 30% of GT crack **and** ≥ 80% of true misses are confident-background PL.
- **Refuted:** true misses < 10% of GT crack. Crack error is then mostly offset or width, and SSL work aimed at crack should stop.
- **Inconclusive:** anything else, reported as is.

**Secondary (descriptive)**
- BsDBn5 vs BsD5 on (i) to (iii);
- A5c, to show whether SSL changes the miss structure at all.

## Probe (b) result, 22 Oct 19:39 IST
- **Run:** cv02 GPU 3, about 35 min, rc = 0, inference only, no test cell used.
- **Files:** `skcdf/probe_a2/`: `a2_probe.py`, `probe.json`, `probe.log`.
- **Cells:** the 448-cell pool, 216,353 GT crack px. All checkpoints are at step 20,000.

Seed mean ± sd, 5 seeds each. Shares are of GT crack px, except the last column.

| Arm | bin-0 | true miss (> 2 px) | offset (≤ 2 px) | confident-bg PL, share of true misses |
|---|---|---|---|---|
| A5c | 0.586±0.012 | 0.415±0.018 | 0.171±0.008 | 0.748±0.023 |
| **BsD5** | 0.558±0.009 | **0.378±0.011** | 0.180±0.005 | **0.705±0.021** |
| BsD5 + LA τ=1 | 0.522±0.008 | 0.359±0.011 | 0.164±0.005 | 0.464±0.038 |
| BsDBn5 | 0.454±0.023 | 0.332±0.014 | 0.122±0.019 | 0.002±0.003 |

**Split by source** (BsD5):

| Source | true miss | confident-bg share of true misses |
|---|---|---|
| CSIR/ARTS (67,549 px) | 0.461 | 0.836 |
| CFVS/BMRK/SDLE (148,804 px) | 0.341 | 0.625 |

### Verdict under the locked thresholds: H-cm INCONCLUSIVE
- **True misses ≥ 30%: met.** BsD5 has 0.378. Most of the confident crack error is real misses, more than 2 px from any predicted crack, not label offset (0.180). The "it is only offset" refutation fails clearly.
- **≥ 80% of true misses with a confident-background PL: not met.** BsD5 has 0.705. It is met only on CSIR/ARTS (0.836).
- **The gate for S-b is therefore not passed.**

### Reading
**The "misses" half of H-cm holds; the "background-PL reinforcement" half is weak.**
- **True misses persist without confident-background targets.**
  - LA cuts the confident-background share of true misses from 0.705 to 0.464, yet true misses fall only from 0.378 to 0.359.
  - BsDBn5 has no confident-background PL on its misses (0.002), yet its true misses fall only by 0.046 (0.378 → 0.332).
  - So removing background self-training entirely recovers at most about 12% of true misses (0.046 / 0.378).
- **BsDBn5's bin-0 drop (0.558 → 0.454) comes mostly from the offset band.** Offset falls 0.180 → 0.122; true misses fall 0.378 → 0.332.

**Implications.**
- **What the misses are.** Crack misses are mainly a recognition failure of the supervised features: faint, boundary-type or unseen-source cracks (agent 4 §2.3). They are not mainly a product of pseudo-label reinforcement.
- **S-b.** Whatever its outcome, S-b's upper bound on true-miss recovery is about BsDBn5's (−0.05).
- **Recommendation.** Do not run S-b. Effort on crack belongs on the label budget (which cells to label) or on the label convention for faint and boundary cracks (agent 4 §4.4–4.5), not on pseudo-label rules.

**For AL1.** The pre-stated predictions (review_v2 addendum 4) still stand. This probe raises my confidence that AL1's crack gain will be small, because confident misses cannot be reached by agreement-gated routing.
