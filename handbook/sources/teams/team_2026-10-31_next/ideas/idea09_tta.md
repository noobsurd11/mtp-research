# Idea 9: test-time adaptation, label-free (found, 31 Oct 2026)

Om's idea 9: adapt BN statistics or minimise entropy per new panel at inference (TENT-style); check how much BN-HC already covers. Tags: E measured (file), R literature (Research MCP id), S judgement. CPU / read-only; no GPU, no test cell read. E1 numbers below are descriptive (diagnostic re-reads of D's existing per-cell outputs) and are never used for selection.

**v2, 31 Oct 14:18 IST (log.md): judge's 5 T9 conditions folded into §5.**
- V4 is dropped entirely.
- The rule gains a module-cluster bootstrap term, a per-module sign count and the 51 unseen full cells.
- Sibling counts are corrected to judge's post-hygiene count.
- The "calibration" claim is scoped to D's 5 bands.

**Files (md5):** `found_scripts/bnhc_anatomy.py` 918cd282, output `bnhc_anatomy.txt` 8a616453 (input `team_2026-10-29_features/d_checks/d_cells.json`, MANIFEST OK); judge reproduced every §2 number with independent code.

**Verdict proposed: PASS to a small CPU check only (no training arm); low priority; descriptive by construction.**
- **Run:** per-panel BN statistics (AdaBN per module), checked label-free on the Hanifi `_rf` non-E1 panels, whose pool siblings give each panel 20 to 144 unlabelled cells.
- **DROP TENT / entropy minimisation entirely** (judge agreed): the mechanism, two papers and ALHVR's in-repo harm predict it moves crack the wrong way. No sanity run.
- **Read BN-HC as mostly a calibration shift (E, at D's 5-band resolution):** a threshold on the source model reproduces its mid-precision gain. So the operating-point part belongs with calib (idea 1). T9's 1,000-bin AP is the instrument that settles it.

## 1. What BN-HC already did (E, `team_2026-10-29_features/d_prereg.md`, `verify_d.md`, `scripts/d/d_infer.py`)
- **Method:** each FINAL member is copied and all BN running stats (encoder and decoder) are reset. They are re-estimated by a cumulative average (momentum None) over the **986 pool half-cells** (7 CSIR modules 297-335), in train mode, no grad, batch 8.
  - This is AdaBN (R: arxiv:1603.04779) at cell-type level, from other panels. It is not per test panel.
  - E1 half-cuts come from 43 modules in CSIR 1621-2328 (vetter finding 4), so the statistics are from a different module family.
- **Routed:** BN-HC members score only the 58 E1 half-cut cells.
- **Pre-registered read at bias +0.75:** target recall 0.299 (+0.174), E1 crack precision cost 0.085 > 0.05. **Fails.**
- **Global:** val relF1@2 −0.151, so the adapted statistics are wrong for in-family cells.

## 2. Why BN-HC routed fails on precision (E, new; `ideas/found_scripts/bnhc_anatomy.py` → `bnhc_anatomy.txt`, from `d_checks/d_cells.json`)
On the 58 E1 half-cut cells, BN-HC routed = BN-HC global. p(crack) is the 5-member mean softmax; the band edges are 0.001 / 0.1 / 0.5 / 0.95 (D's per-cell bands).

| 58 half-cut cells | crack P | crack R | IoU | GT crack px with p < 0.001 | pred crack px > 2 px from GT | crack px on 32 crack-free half-cut cells |
|---|---|---|---|---|---|---|
| FINAL, bias 0 (argmax) | 0.691 | 0.124 | 0.118 | 0.625 | 1,034 | 231 |
| BN-HC, bias 0 (argmax) | 0.514 | 0.243 | 0.198 | 0.323 | 4,972 | 1,630 |
| **FINAL, p(crack) ≥ 0.1** (a threshold, no adaptation) | **0.507** | **0.252** | | | | |
| BN-HC, p(crack) ≥ 0.5 | 0.537 | 0.216 | | | | |
| FINAL, p ≥ 0.95 | 0.846 | 0.043 | | | | |
| BN-HC, p ≥ 0.95 | 0.836 | 0.070 | | | | |
| FINAL, bias +0.75 (the read) | 0.609 | 0.165 | 0.149 | | 2,087 | 603 |
| BN-HC, bias +0.75 (the read) | 0.394 | 0.339 | 0.223 | | 11,803 | 4,381 |

- **Mid precision: mostly a calibration shift, not better ranking (E, 5 bands; 3 PR points per arm, so the curves are coarse).**
  - Judge's reading: FINAL is slightly better near R 0.22 (interpolated P ≈ 0.56 vs 0.537); BN-HC is better at the confident end.
  - At P ≈ 0.51 the source model with a lower threshold already recalls 0.252, vs BN-HC 0.243. Linear interpolation at P 0.52 gives FINAL ≈ 0.24 and BN-HC ≈ 0.23.
  - BN-HC does rank better only at the confident end: R 0.070 vs 0.043 at P ≈ 0.84.
- **The extra false positives are global, not a few bad cells.**
  - At bias 0: +4,655 FP px, more on 52 of 58 cells, top-5 cells 35% of them. At +0.75: +11,143, 57 of 58 cells, top-5 28%.
  - 91% fall on GT background (5,621 of 6,143 crack-predicted non-crack px), mostly > 2 px from any GT crack.
- **It hurts where the source was right.**
  - On the 29 half-cut cells without scuff, crack precision 0.900 → 0.572 (bias 0) and 0.803 → 0.345 (+0.75).
  - Recall 0.479 → 0.651. The FP there is 133 → 1,213, of which 662 on crack-free cells.
- **Stacking.** The +0.75 bias was chosen for the source statistics (val). Adding it on top of a BN shift that already raised p(crack) counts the same shift twice. That is the bulk of the pre-registered cost.
- **Mechanism (S).** Re-normalising with half-cell statistics shifts per-channel means everywhere in the cell. The crack logit is a near-linear readout, so most pixels move together: a prior shift plus a small ranking change. Domain shift here is mostly a change in what the cell contains (half-cut spacing, scuff), not a global intensity or style shift that BN can undo.

## 3. Would TENT, entropy minimisation or per-module BN behave differently?
- **TENT / entropy minimisation: likely worse for crack (R + E).**
  - R arxiv:2310.05341:
    - in semantic segmentation every TENT variant was worse than source-only;
    - "BN-fixed" TENT (affine only) was about equal to source;
    - BN statistics from test batches were estimated imprecisely;
    - segmentation TTA suffers a strong long-tail bias toward dominant classes.
  - R arxiv:2609.21743: in imbalanced binary segmentation, mean-entropy updates are dominated by the majority predicted class. They pull minority predictions toward it and collapse the mask; this is proven in a shared-shift model. The authors' fix (class-balanced anchors) is built on a vision-language prompt framework, not on BN.
  - E: crack is 0.18% of px on the 58 E1 half-cut cells (26,737 GT px). The failure is under-prediction: 62.5% of GT crack is at p < 0.001 and 26% in 0.001-0.5.
  - Entropy minimisation sharpens uncertain pixels toward their current argmax. That pushes the 0.001-0.5 crack band to background: **recall down, the opposite of the goal (S).**
  - Origin: TENT, arxiv:2006.10726. Stability fixes (SAR, arxiv:2302.12400) address batch size and label shift in classification, not segmentation imbalance.
- **Per-module (per-panel) BN: the realistic deployment form, untested here.**
  - At deployment a panel's 60-144 cells are all available unlabelled, so BN stats can come from the panel itself rather than from 7 other modules.
  - **E1 cannot test it:** 71 modules, 54 with one scored cell, 9 with ≥ 3 (`scripts/e1_context.tsv`). No E1 module has pool siblings (pool has no CSIR 400-2362; vetter §13).
  - **The Hanifi `_rf` panels can** (E, `~/mtp/datasets/escdd_full` and `splits_benchmark/external_unlabeled.txt`):
    - the 8 half-cut modules (CSIR 297-301, 333-335) each have **144** pool cells (whole panels) and hold the 43 `_rf` half-cuts;
    - full-cell `_rf` modules with ≥ 20 pool siblings: 46 modules / 65 cells before hygiene, and **43 modules / 61 cells after dropping the 4 val/test-module cells** (judge's recount; use 43 / 61).
  - **Shallow-only variant** (encoder conv1/layer1/layer2 BN re-estimated, deeper and decoder BN kept): the BN twin of idea 2 (per-module intensity normalisation). It limits the deep prior shift seen in §2 (S).
- **Note:** 35 of the 43 `_rf` half-cells are inside the 986 that BN-HC used (vetter finding 3). Label-free, so allowed for TTA, but stated.

## 4. Prior tries (E)
- **7 Oct, old era:** BN recalibration on own, train or pool images "never raised" defect_miou. The external pool was worst (gaint `reports/bn_recalibration.md`; handbook 06 l.228).
- **P13 audit:** `results/p13_audit/bn_diag.py`. Recalibration about +0.01 crack, gaps unchanged (handbook 10 l.190-210).
- **D(c) BN-HC routed / global** (§1). The 27 Oct item 4 named BN re-estimation (handbook 18 §U).
- **No entropy-minimisation TTA was ever run.** grep `tent|entropy minimi[sz]ation|test-time adapt` over the repo finds literature and plans only:
  - 27 Oct `lit.md` row 15d: Tent +7.0 and BN re-estimation +2.6 mIoU on GTA → Cityscapes, Tent fails on a hard shift (arxiv:2006.10726); TTAB finds model selection "exceedingly difficult" (arxiv:2306.03536);
  - `ideas.md` row 5: inference-only V0-V4. Its AdaBN part ran as D(c).
- **Entropy minimisation as a training loss did run, and suppressed the minority class:** ALHVR's DTCT (sharpened MSE + entropy minimisation on Ω3) halved inactive recall, 0.276 → 0.124 (`team_2026-10-24_why/r2_method_side.md` l.80; `team_2026-10-21/alhvr/verify_a2.md` l.39). This is the in-repo analogue of §3's prediction.
- **27 Oct reading, still holding:** 75% of E1 crack px are a missing context (scuff + half-cut), which "BN re-estimation and Tent cannot add" (`team_2026-10-27_unlabelled/lit.md` l.129). §2 agrees: the BN shift recovers recall only as calibration.

## 5. Protocol sketch: T9, a label-free TTA check on `_rf` (CPU; E1 descriptive)
**Superseded by `ideas/t9_prereg.md`** (judge APPROVED with A1-A3; md5 0eae681e). The binding version differs from this sketch:
- the deciding set is P (36 eligible unseen-module full cells, 24 modules, 8 crack modules), because H36 crack labels are unusable; H36 carries false alarms only;
- AP is on a common recall range;
- the false-alarm floor is max(1.5×V0, V0 + 200);
- every variant scores the pool copies;
- the scope is unseen full-cell panels only.

Launched 31 Oct 14:27 IST on gaint CPU (tmux t9); done 21:13 IST. **Result: no variant passes for either model family (all comparisons informative), so TTA is CLOSED. Details are in `t9_prereg.md` RESULT.** Per-panel BN of all layers multiplies false alarms (as BN-HC); the shallow variant is flat (ΔAP +0.015, bootstrap lower bound < 0). The sketch below is kept for the record.
- **No confirmatory path, stated up front (judge 1).**
  - Per-panel BN cannot be evaluated on E1 (1 of 71 modules has siblings), and test is in-family, so T9 can only give a descriptive `_rf` result.
  - A pass means "worth a deployment note and a place in the final candidate's inference pipeline, decided on val + `_rf`". It is not a claim.
- **One harness with calib's idea 1 (judge 4):** the `_rf` per-panel set, the 1,000-bin p(crack) dumps and the matched-precision readout are shared with calib's per-panel quantile threshold. Two variant families in one evaluator.
- **Image-identity check first (judge 3).** BN statistics come from our 512-px pool conversions (1,200-px multi cells area-downsampled), but the scored `_rf` cells are E-SCDD's images.
  - Before any number, compare the ~100 `_rf` cells that have a pool copy (pixel difference and correlation; gaint CPU, minutes).
  - If they differ (resize, sharpness), score the pool copies of the `_rf` cells with the `_rf` masks where they align. Otherwise V2/V3 partly adapt to a preprocessing gap.
- **Models:**
  - FINAL (link to D);
  - BEST after PF2 (SUP100-PF 5-seed ensemble), at its val-chosen bias and at bias 0.
- **Variants:**
  - V0 source;
  - V1 BN-HC (as D);
  - **V2 per-panel BN:** re-estimate all BN from that module's pool cells, score that module's `_rf` cells;
  - **V3 per-panel BN, shallow** (conv1-layer2 only);
  - (V4 TENT: dropped, judge agreed.)
- **Scored cells:** `_rf` non-E1 after hygiene (drop the 7 CSIR_00300 and the 4 val/test-module cells):
  - **H36:** 36 half-cut cells, from 7 modules (1,792 crack px in 17 cells with ≥ 20 px; judge);
  - **F51:** the 51 unseen-module full cells; per-panel variants only where the module has ≥ 20 siblings (43 modules / 61 cells counted before the unseen filter; the exact F51 ∩ sibling count goes in the protocol);
  - the 19 full cells in train modules reported separately.
  - Labels as in the R4 build (`trackM/r4_build`, scuff → ignore). Crack labels are speckled, so add a ≥ 20 px component readout.
- **Metrics:**
  - **crack AP (1,000-bin): threshold-free, so it separates ranking from calibration;**
  - crack recall at matched precision (P* = V0's precision at its operating point);
  - crack px on crack-free `_rf` cells at V0's operating point;
  - inactive AP;
  - module-cluster bootstrap (7 half-cut clusters: wide CIs, stated).
- **Operating point without labels (judge 5).** A V2/V3 model is scored at the source model's val-chosen bias (BEST: its val rule; FINAL: +0.75) and at calib's label-free per-panel quantile rule, if that passes in idea 1. No bias is chosen on `_rf`. AP is threshold-free, so the rule below does not depend on this.
- **Rule (fixed before any number):** a variant passes if all five hold, for both models:
  1. H36 crack AP ≥ V0 + 0.03;
  2. **module-cluster bootstrap** (2,000 resamples over the 7 H36 modules): lower 95% bound of the H36 AP gain > 0;
  3. **per-module sign count:** AP up in ≥ 6 of the 7 H36 modules;
  4. F51 crack AP ≥ V0 − 0.01;
  5. crack px on crack-free H36 + F51 cells at the fixed operating point ≤ 1.5× V0.
- **E1 descriptive:** V1 and a per-cell-type V3 on the 29 + 29 half-cut cells (per-panel is impossible on E1).
- **Kill:** no variant passes. Then close TTA. Operating-point adaptation stays with calib's idea 1, which E §2 shows covers BN-HC's mid-precision gain.
- **Expected (S):**
  - V1 ≈ V0 on AP, recall up at argmax;
  - V2 slightly better than V1 (own-panel statistics);
  - V3 smaller shift, AP ± 0.01;
  - P(any passes) ≈ 0.25.
- **Cost:**
  - CPU on gaint, nice 19, ≤ 8 threads, outside runner's critical windows. D's BN pass was 986 images × 5 members in 2,013 s at 16 threads (`d_checks/d.log`).
  - V2/V3 need ~3,300 sibling images per model family, so ~4 h per family at 8 threads, ~8 h for both.
  - Check the PF2 data-loader CPU load before starting (judge).
  - Code: ~0.5 day (builder or me), reusing `d_infer.py`'s `bn_reestimate` with a per-module grouping.
- **Needs:** no labels beyond Hanifi's existing ones; no download; no user hours.

## 6. Expected E1 and test effect (S)
- **Test:** none by design. TTA would be routed per panel, and test panels are in-family.
- **E1:** at best a few points of crack AP on half-cut panels if V2 passes. Most of BN-HC's E1 recall gain is reproducible by a threshold, which costs nothing and needs no BN pass.
- The decision of what operating point to use on an unseen panel without labels is the real open problem. It belongs to idea 1 (per-panel quantile thresholds) and needs labelled out-of-E1 half-cells to set: the `_rf` set, or B2 labels.

---

## judge verdict (31 Oct 2026, 14:16 IST per log.md; report md5 ca5fb8c7 as reviewed)

**Verdict:**
- **DROP TENT / entropy minimisation (V4): agreed.** Drop V4 entirely. The literature plus A13 are enough, and it saves a GPU slot.
- **T9 per-panel AdaBN: PASS-to-protocol, low priority, CPU only, with the conditions below.** Its result is descriptive by construction (item 1), so it cannot change BEST or a deployment claim on its own.

### What I reproduced (E)
- **§2 anatomy:** every number in the table and the FP-spread bullets, recomputed independently from `d_checks/d_cells.json` (my own code, not `bnhc_anatomy.py`):
  - FINAL b0: half-cut 58 P 0.691 R 0.124;
  - BN-HC b0: P 0.514 R 0.243;
  - FINAL p ≥ 0.1: P 0.507 R 0.252; p ≥ 0.5: 0.707 / 0.117; p ≥ 0.95: 0.846 / 0.043;
  - BN-HC p ≥ 0.5: 0.537 / 0.216; p ≥ 0.95: 0.836 / 0.070;
  - no-scuff precision 0.900 → 0.572 (b0) and 0.803 → 0.345 (b0.75);
  - extra FP 4,655 on 52 of 58 cells, top-5 share 0.354;
  - BN-HC routed = global on the half-cut cells.
- **Band sanity:** the p-band counts exclude ignore px (band sums equal conf sums on scuff cells), so the "p ≥ t" rows are on the same pixel set as argmax.
- **§3 per-panel premise:**
  - the 7 hygiene-kept `_rf` half-cut modules (CSIR 297 to 299, 301, 333 to 335) each have exactly 144 pool cells;
  - E1 has 71 modules, 54 with one cell, 9 with ≥ 3, and 1 with any pool sibling (CSIR_00300).
  - Small difference: I count 43 full-cell modules with ≥ 20 siblings holding 61 kept cells (found: 46 / 65), after dropping the 4 val/test-module cells.
- **Literature:** all 6 ids resolve (arxiv:1603.04779, 2006.10726, 2310.05341, 2609.21743, 2302.12400, 2306.03536 via the 27 Oct notes).
  - 2310.05341 §3.1, full text: "all TENT variants perform worse than the Source Only", and the BN-fixed variant is "only similar to SO". **Match.**
  - 2609.21743 abstract: entropy collapse in imbalanced binary segmentation; fix via prompt-only adaptation of a vision-language model. **Match.**

### Reading check
- **"BN-HC's mid-precision gain is a calibration shift" holds at the resolution D's 5 bands allow.** With 3 PR points per arm, the curves cross: FINAL is a little better near R 0.22 (interpolated P ≈ 0.56 vs 0.537), and BN-HC is better at the confident end (0.836 vs ≈ 0.80 at R 0.07).
- That is coarse. T9's 1,000-bin AP is the right instrument; until it runs, keep the claim as "mostly calibration (E, 5 bands)".

### Conditions for the T9 protocol
1. **No confirmatory path; say so up front (E).** Per-panel BN cannot be evaluated on E1 (1 of 71 modules has siblings), and test is in-family. So T9 can only ever produce a descriptive `_rf` result. A pass means "worth a deployment note and a place in the final candidate's inference pipeline, decided on val + `_rf`", not a claim.
2. **The pass rule is underpowered (E).**
   - The 36 half-cut `_rf` cells hold 1,792 crack px in 17 cells, in 7 modules, with speckled SAM labels (my recount; see the idea08 verdict).
   - A fixed +0.03 AP margin is inside plausible noise. Add both:
     - (a) the module-cluster bootstrap lower bound > 0, as a rule term, not only reported;
     - (b) a per-module sign count (≥ 6 of 7 half-cut modules with AP up).
   - Add the 51 unseen-module full cells to rule 2. Rule 2 as written uses all full cells, including 19 in train modules.
3. **Image-identity check before any number.** BN stats come from pool siblings: our 512 conversions, with 1,200 px multi cells area-downsampled. The scored `_rf` cells are E-SCDD's images. If the `_rf` image of a cell differs from its pool copy (resize or sharpness), V2/V3 adapt partly to a preprocessing gap, not to the panel. Compare the ~100 `_rf` cells that have a pool copy (pixel diff or correlation); gaint CPU, minutes.
4. **Share the harness with calib's idea 1.** The `_rf` per-panel set, the 1,000-bin dumps and the matched-precision readout are the same as for calib's per-panel quantile threshold. The operating-point question belongs there, as found says. One harness, two variant families, avoids two half-built evaluators.
5. **Operating point at deployment.** V2/V3 change calibration as well as ranking. The protocol must state how the bias/threshold for a V2-adapted model would be chosen without labels (e.g., the source model's val bias, or calib's quantile rule). Otherwise a V2 "recall gain" at argmax repeats BN-HC's stacking problem (§2).

### Cost, effect, kill (S)
- **Cost:** about 8 h of gaint CPU at ≤ 8 threads, plus 0.5 day of code. Outside runner's critical windows; check the PF2 data-loader load before starting.
- **Expected:** found's P(pass) ≈ 0.25 is plausible. Test effect none; E1 not measurable.
- **Kill:** real ("no variant passes" closes TTA), once item 2 is in the rule.

### Tags
- E: §2 fully reproduced; sibling premise verified.
- R: 6 ids resolved; 2 claims checked in text.
- S: items 1 and 5.
