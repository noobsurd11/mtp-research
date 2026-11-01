# Half-cut routing pre-check (judge condition 3b): rule, written BEFORE any number

calib, 31 Oct 2026, ~17:50 IST. Status: **RULE ONLY. Nothing computed yet.** judge reviews this rule before the results section is filled. Tags: E measured, S judgement.

## Question
Do the models need a higher crack bias on synthetic half-cuts than on the original val cells? And would choosing that bias pay on the synthetic half-cuts themselves?
- This is the non-E1 pre-check that gates any half-cut routing readout (judge, log 17:33; team-lead task 31 Oct).
- No E1 and no test cell is read in this step.

## Data (all val-derived; selection allowed)
- **V0:** the 54 original val cells. Records: `calib_out/rec/<model>.val.json`, GT labeled/masks_escdd, the existing dumps.
- **V4:** domain's synthetic half-cut val. The 54 val cells through `dom_synth_variants.py` variant V4 (gap + half-cell scale + pool intensity match), both halves = 108 images.
  - Files: gaint `/home/noob/work/domain_scratch/synvar/{images,masks}/<stem>__V4h{0,1}.png`.
  - Fingerprint of the 108 image + mask pairs as of 17:45: md5 of the per-file md5 list = d2f05a79.
  - If domain freezes a different V4 file set for PF2 §13, the pre-check is rerun on it under this same rule.
  - GT: domain's transformed masks (E-SCDD masks; 24 → 2, 29 → 1, 25-28 → 0). No ignore px: crops lie inside the source.
- **Models:**
  - FINAL (5-model ensemble, mean softmax);
  - SUP100-PF s0-4 (f3_SUPPF_100pct_s0-4), per seed and pooled over the 5 seeds (as protocol_PF2 §13).
- **Dumps:** `calib_dump.py` with a new `--sets synval` (V4 only), CPU fp32, nice 19, 8 threads, CUDA hidden. Records by `el_metrics.py records --set synval`.

## Definitions (fixed now)
- **Grid:** b = −4.0 .. +12.0, step 0.1 (OPGRID). b is added to log p_crack: crack is predicted iff margin + b > 0.
- **relF1@2(b)** = harmonic mean of the pooled relP@2(b) and relR@2(b) over the set's cells (house relaxed metrics).
- **Oracle b of a set** = the grid b with the highest pooled relF1@2 on that set; ties go to the smaller b.
  - For SUP100-PF pooled: counts summed over the 5 seeds' cells before computing relF1@2 (one b for the arm).
  - For FINAL: the ensemble's own counts.
- **b_V0** = oracle b on V0. **b_V4** = oracle b on V4. **Δb = b_V4 − b_V0.**
- **Routing gain on V4:** G = relF1@2_V4(b_V4) − relF1@2_V4(b_V0).
  - This is the gain on the half-cut set from using its own bias instead of the full-cell bias. It is in-sample on V4 by design: a headroom check, not an estimate of E1 gain.

## PASS / FAIL (fixed now)
- **PASS iff, for BOTH FINAL and SUP100-PF pooled:**
  1. Δb ≥ +1.0, AND
  2. G ≥ +0.02, AND
  3. **G_cf ≥ +0.01** (judge R1, added 17:40 before any number). G_cf is the cross-fitted routing gain:
     - **Folds:** the 54 source val cells, split into 2 folds stratified by crack yes/no (GT crack px ≥ 20 in the source val cell; val has no 1-19 px cells).
       - Within each stratum, take the stems sorted, permute them with `np.random.default_rng(0)` (crack stratum first, then crack-free, same generator), and assign alternately A, B, A, B, ...
       - Both V4 halves of a source cell go to its fold.
     - **For fold k:** b_V4^k = the oracle b on fold k's V4 half-images. The gain is evaluated on the other fold k': relF1@2_V4,k'(b_V4^k) − relF1@2_V4,k'(b_V0), with b_V0 the full-V0 oracle (as PF2 §13's b_full).
     - **G_cf** = the mean of the two fold gains.
     - The in-sample G and G_cf are reported side by side.
- Otherwise **FAIL**. Per judge's ruling, a Δb < 1.0 is labelled "routing = no-op".
- Per-seed SUP100-PF values are reported, but they do not decide.

## Reported alongside (never decide)
- relR@2, relP@2 and relF1@2 on V0 and V4 at b_V0, b_V4 and the deployed b (FINAL +0.75; single runs 0).
- **False-alarm guard on V4:** crack px per crack-free V4 image and the share of crack-free V4 images flagged (≥ 20 px), at b_V0 vs b_V4. V4 inherits val's 31 crack-free cells, so it has 62 crack-free half-images.
- **Mixed-set view:** relF1@2 on V0 ∪ V4 with V4 cells at b_V4 and V0 cells at b_V0, vs all at b_V0. Descriptive.
- Matched-precision view: max relR@2 at relP@2 ≥ 0.90 / 0.80 on V0 and V4. It separates ranking from threshold, per judge's erratum that the V4 drop looks mostly like ranking.
- The relF1@2(b) curves for V0 and V4, both models, in one figure (judge).
- Per-seed Δb for SUP100-PF, to show whether the pooled Δb is carried by one seed (judge).

## What this does NOT do
- No E1 read; no test read.
- No routing protocol: PF2 §13 has its own pre-registered rule on PF2's seeds 5-9.
- This step only checks whether the premise (a cell-type bias offset visible on non-E1 synthetic half-cuts) holds for the existing models.

## Amendment A (calib, written before any number; judge + coach 31 Oct after domain froze SHV1)
- **Primary set = SHV1:** gaint `/home/noob/work/domain_scratch/shv1`, MANIFEST.md5 md5 63dd5469 (verified OK by `md5sum -c` before use).
  - Generator dom_synth_val.py 6e702c36, seed 20261031.
  - 108 half-images `<val stem>__h{0,1}` (stems_eval.txt).
  - Masks from labeled/masks_escdd, transformed. ignore/ is all zero.
  - Per-image pool intensity pairs.
  - 40 crack images (≥ 20 px), 68 crack-free.
- **"V4" in every definition and PASS term above now means SHV1.** Δb, G and G_cf (R1) are read on SHV1 only; the FA guard uses its 68 crack-free half-images.
- **Folds (R1):** unchanged, on the 54 source val cells. An SHV1 stem maps to its source by the prefix before `__`.
- **The synvar V4 set** (`/home/noob/work/domain_scratch/synvar`, `__V4h{0,1}`, fingerprint d2f05a79) is reported as a **non-deciding sensitivity row** only.
- The scorer verifies the SHV1 MANIFEST before reading (dump and records).

## Results
See "Results (calib, 31 Oct ~18:05 IST)" at the end of this file.

---

## judge review of the rule (31 Oct 2026, 17:37 IST from date; rule md5 56614bd3 as reviewed; no result existed)

**APPROVED, with one added PASS term (R1).** Write R1 into "PASS / FAIL" before any number. Then fill in the results.

**R1, a cross-fitted routing gain (required).**
- G picks b_V4 as the in-sample maximum over 161 grid points on the same 108 images, so it is biased upward by construction. With ~40 crack half-images, noise alone can make G ≥ 0.02 when the relF1 curve is flat and noisy.
- Add:
  - split the 54 **source** val cells into 2 folds (seed 0, stratified by crack yes/no), with both halves of a source cell always in the same fold;
  - choose b_V4 on fold A and evaluate G on fold B, then the reverse;
  - G_cf = the mean of the two.
- **PASS also requires G_cf ≥ +0.01, for both FINAL and SUP100-PF pooled.**
- Report the in-sample G and G_cf side by side.

**The rest is sound:**
- V4 is fingerprinted (d2f05a79), with a rerun rule if the frozen set changes.
- b_V0 is the oracle on the real val cells, matching PF2 §13's b_full.
- "Ties to smaller b" makes Δb conservative. Good for a pre-check.
- Δb ≥ 1.0 AND G ≥ 0.02 for BOTH models is a fair gate.
- FINAL is fine here: the step is non-E1. FINAL stays out of the E1 routing readout (my PF2 §13 ruling).
- No E1, no test.

**Also report (non-deciding):**
- the relF1@2(b) curves for V0 and V4, both models, as one figure;
- per-seed Δb for SUP100-PF, to show whether the pooled Δb is carried by one seed.

### judge addendum (17:38 IST from date): which synthetic set
- domain has frozen **SHV1** (gaint `domain_scratch/shv1`, MANIFEST 63dd5469; generator dom_synth_val.py 6e702c36, seed 20261031). It is unscored.
- SHV1 differs from synvar V4 (d2f05a79) only in intensity: one pool (mean, sd) pair drawn per image, instead of the fixed 154 / 24. Geometry is the same and deterministic.
- **Before any number, make SHV1 the primary set for this pre-check and for PF2 §13.** The selector and the readout must use the same frozen set.
- Run synvar V4 as a non-deciding sensitivity row.
- PASS / FAIL (Δb, G, G_cf) is read on SHV1 only.


---

## Results (calib, 31 Oct ~18:05 IST; computed under the rule as approved, R1 and Amendment A, all written before any number)
**VERDICT: FAIL. Routing = no-op for both models.** No PASS term holds for either model on SHV1.

**Run (E):**
- SHV1 dumps: CPU fp32, CUDA hidden, nice 19, 8 threads, gaint 17:47-17:59 IST. `calib_dump.py` 9694ad7d; the SHV1 MANIFEST 63dd5469 was verified before reading (328 files OK, both groups).
- Records: `el_metrics.py` f40a0efe (MANIFEST re-verified), in `calib_out/rec_shv1/` (MANIFEST f089abce).
- Sensitivity set (synvar V4, d2f05a79): records in `calib_out/rec_syn_v4/` (aec7fa2e).
- V0 = the existing val records in `calib_out/rec/`.
- Script: `scripts/routing_precheck.py` (06a3ad30). Output: `calib_out/routing_precheck.txt` / `.json`. Figure: `figs/routing_precheck.png`.

| model | b_V0 | b_SHV1 | Δb (≥ 1.0) | G in-sample (≥ 0.02) | G_cf (≥ 0.01; folds) | verdict |
|---|---|---|---|---|---|---|
| FINAL | +1.1 | +1.5 | **+0.4** | +0.008 | +0.002 (−0.005 / +0.010) | FAIL |
| SUP100-PF pooled s0-4 | +2.9 | +3.8 | **+0.9** | +0.001 | −0.003 (−0.005 / −0.000) | FAIL |
| sens. synvar V4, FINAL | +1.1 | +1.5 | +0.4 | +0.004 | +0.001 | (FAIL) |
| sens. synvar V4, SUP100-PF | +2.9 | +3.8 | +0.9 | +0.001 | −0.002 | (FAIL) |

**Reported, non-deciding:**
- **Per-seed SUP100-PF Δb:** s0 +0.9, s1 +1.8, s2 +0.8, s3 +3.2, s4 +1.1.
  - The pooled +0.9 is below the single-seed values of s1, s3 and s4, because each seed's relF1@2(b) curve on SHV1 is flat over several log-odds.
  - Per-seed G is +0.001 to +0.006 and G_cf −0.004 to 0.000: no seed gains from routing.
- **relF1@2 at each bias:**
  - FINAL: SHV1 0.815 at b_V0 vs 0.822 at its own b; V0 0.897 vs 0.894.
  - SUP100-PF pooled: SHV1 0.795 vs 0.796.
- **Ranking, not threshold.** Max relR@2 at relP@2 ≥ 0.90:
  - FINAL: V0 0.892 vs SHV1 0.730.
  - SUP100-PF: 0.876 vs 0.694.
  - At relP@2 ≥ 0.80: 0.941 vs 0.834 and 0.912 vs 0.774.
  - The SHV1 curve lies below V0's at every b (figure). Its peak is flat and only 0.4-0.9 log-odds to the right.
- **FA guard on crack-free SHV1 half-images** (FINAL 68; SUP100-PF 340 = 68 x 5 seeds pooled):
  - FINAL: crack px per image 15.1 → 21.0 and flagged share 0.147 → 0.191 at b_SHV1 vs b_V0.
  - SUP100-PF: 6.0 → 7.8 and 0.094 → 0.106.
- **Mixed V0 + SHV1 relF1@2, routed vs not:** FINAL 0.841 → 0.846; SUP100-PF 0.825 → 0.826.

**Reading (S):**
- On simulated half-cuts (geometry + pool intensity), the existing models lose ranking, not calibration. Their best bias moves by < 1 log-odds, and using it gains < 0.01 relF1@2.
- This confirms judge's 17:33 erratum on idea 5. It also says the large E1 cell-type offset (oracle half-cut bias +5.4 vs full −0.8, idea 1 v2) is not produced by half-cut geometry or intensity alone.
  - On E1 it comes with the scuff context, frame and module family that SHV1 does not simulate (SHV1 README "NOT matched").
- So a synthetic-val selector cannot choose the E1 half-cut bias: it would pick ≈ b_full. PF2 §13 would be a no-op by construction.
- Consequence for the routing line:
  - PF2 §13 is void (coach's stop rule).
  - Half-cut routing stays PARKED behind a labelled real half-cut set (Hanifi H36 cleanup or B2 masks), as in idea 1 v2.
  - Idea 5's mechanism readout (oracle-b shift V0 → SHV1) now has a baseline: Δb +0.4 FINAL, +0.9 SUP100-PF.

---

## judge verdict on the result (31 Oct 2026, 18:05 IST from date; file md5 c3fc8442 as reviewed)

**FAIL confirmed: routing = no-op on SHV1, for both models.**

**Reproduced with my own code** (`judge/routing_recompute.py`, md5 ee64ca96; records `rec_shv1/` MANIFEST 12/12 OK, V0 from `rec/`):

| Model | b_V0 | b_SHV1 | Δb | G | G_cf (my own folds) | max relR@2 at relP@2 ≥ 0.90, V0 vs SHV1 |
|---|---|---|---|---|---|---|
| FINAL | +1.1 | +1.5 | +0.4 | +0.008 | −0.001 | 0.892 vs 0.730 |
| SUPPF5 pooled | +2.9 | +3.8 | +0.9 | +0.001 | −0.001 | 0.876 vs 0.694 |

- Δb, G and the matched-precision values are **exact**.
- My G_cf uses different folds by construction (source-cell 2-fold, crack-stratified, seed 0). It is ≈ 0 for both, the same conclusion as calib's +0.002 / −0.003.
- No PASS term holds, for either model.

**Reading:**
- (E) On non-E1 synthetic half-cuts the models' loss is ranking, not threshold. Their relF1@2(b) curves are flat near the optimum, so a half-cut bias buys nothing (G ≤ 0.008) and costs false alarms (FINAL 15.1 → 21.0 px per crack-free image).
- (S) E1's large half-cut offset (+5 to +7 log-odds in the oracle analysis) is therefore not a property of half-cut geometry and intensity alone. It plausibly sits in the scuff, frame or module-family context, which SHV1 does not contain (calib's reading, agreed as S).

**Consequences:**
1. **PF2 §13:** the condition-4 gate failed. Drop the **E1 routed readout** from PF2. Reading E1 for a pre-declared no-op adds one more E1 read to the multiplicity for no information. Keep the **non-E1** part, Δb and G on SHV1 for PF2's seeds 5-9, as a cheap descriptive line: it shows whether RN50-PF or the new seeds carry a half-cut offset.
2. **Routing (idea 1 lever): PARKED.** It needs a labelled half-cut set that contains the E1-like context, not just geometry.
3. **The 2-3 h Hanifi cleanup still does not pay for routing** (S). H36 is a different module family, has no letterbox frame, and holds only ~1.8k crack px. If the offset is context-driven, cleaned H36 would likely also fail to show it.
   - The scuff + half-cut context is the target of B3 (scuff class) and of B2 marks or masks on the pool half-cells, also a different family. Those stay the route; they are the user's call.
4. **Thesis wording:** "a cell-type calibration offset exists on E1 (oracle analysis, descriptive) but is not reproduced by geometric + intensity simulation, so it cannot be selected without E1-like labelled half-cuts".

### judge note (18:26 IST from date): half-cut detector v1 (domain, frozen, MANIFEST b8badda4)
- **In-sample, it meets my targets narrowly:** pool half-cells 98.1% recall; labelled 582 FP 0.86%. But the 582 include the train cells used to fit (a, b).
- **Held out, the false-positive target is missed:**
  - val 3/54 = 5.6%;
  - pool full multi 3.5%, mostly 3 zoomed ARTS modules;
  - mono 0.3%;
  - Hanifi full 0/70;
  - recall on held-out half modules 98.1%; test 0/50 routed.
- **R1 failed** and was followed by an R2b rule fitted on DEV only, disclosed. That is acceptable process.
- **Verdict:** not usable as a deployable router as is, with a full-cell FP of ~1-5% depending on population. Routing is PARKED anyway (pre-check FAIL), so nothing waits on it. Keep it frozen as a descriptive tool (e.g. idea 5 strata), always with its held-out FP stated.
