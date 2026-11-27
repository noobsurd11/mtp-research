# OPENING_RULE: the final opening of the sealed sets (E1 opening #8, legacy test50 opening #19)

opening_builder, 21 Nov 2026. **Written before any number of the final models exists**: at the time of writing the full-pool
runs `fin_*_pool_s5..9` are not trained, no sealed-set dump of any final model exists, and no number of the fin CV5 TTA read
exists. Nothing here was chosen after looking at a sealed label, a sealed prediction or a label summary of a sealed cell.
Tags: E = in a cited file; S = judgement; D = decision with its record. T = `/home/yugma/mtp/research/team_2026-11-12_frontier`.
This file is frozen by its md5 in the registration record (`opening_register.sh`, section 9). Any change after registration is a
new registration with its own time and is reported as such.
Edit of 21 Nov 2026 (before registration and before any number of the final models; review of fin2, REVIEW_FIN2.md N3): only the checkpoint location
and provenance lines changed, for the fin2 resume repair of the full-pool runs (section 2 "All checkpoints", section 8
`train_code_revision` / `checkpoint_md5`, section 9 step 1); no candidate, readout, contrast, statistic or guard changed. The
previous version is md5 69f0c0f382083f049e676221e9d8daac.

## 0. What is decided here, and by whom (D)
- User, 21 Nov 00:22 (T/log.md): (1) legacy test50: one opening, #19, public table only, full-pool PF and the final model on the
  old masks (v0) and on v1.1, decides nothing alone, leakage disclosed; (2) E1: the one end-of-project E1 opening is this final
  evaluation, at most 3 candidates (full-pool PF; HRNet-W18 U-Net++ + SWAD, readout swad, + D4; its 5-seed ensemble); rule and
  candidates frozen and reviewed before any E1 dump; T3b few-shot only after it; (3) relF1@2 decides every crack contrast; strict
  crack IoU only with its convention band.
- Lead, 21 Nov 01:29 (T/log.md, ruling Q1): C2 (single full-pool HRNet + SWAD swad + D4) is primary, C3 (5-seed ensemble) beside.
- Protocol: T/benchmark/PROTOCOL_v0.2.md section 3.3 (sealing), 5 (metrics, statistics), 6.1 (entry classes: an ensemble is printed
  beside the equal-cost comparator), 11 item 2 (T3b only after this opening).
- This rule decides only what the user and the lead left open: the primary contrast and its statistics, guards, the tables,
  disclosures and the procedure.

## 1. Sets (one opening per set, numbered in the ledgers' style)
| Opening | Set | Cells | List (md5) | Clusters for the bootstrap | Role |
|---|---|---|---|---|---|
| **E1 opening #8** (`e1_open8_final`; ledger `team_2026-10-31_next/e1_openings.md`) | `e1_106` (E1: release `20221008` cells not in our 582 and not in the unlabelled pool; unseen modules) | 106 (CSIR 101, BMRK 5; 62 half-cut, 44 full by cells.tsv `cell_type`) | `el_f1/reports/f1/ext117/stems_eval.txt` 5266806b559f74bcf9eae167bb076b95 | 71 source images (the stem without its cell suffix; = the 71 module clusters of E1 openings #4 to #7) | **primary**: decides the final-model claim |
| **test50 opening #19** (`t50_open19_final`; ledger `T/benchmark/test_openings.md`) | `test50` (BenchmarkEL `dataset_20211104` test split) | 50 | `data/splits/test.txt` a31fad14fa27ee28e2a2319b8976aba3 | 48 source images (same rule; SDLE stems end in `-cell<n>`) | **secondary, public table**: decides nothing alone |

## 2. Candidates and exact readouts (frozen)
All checkpoints: the cv02 full-pool runs of the fin package as repaired by the resume queue fin2 (FINAL_RULE_ADDENDUM_1.md):
run dirs in the deploy of F2 = 9967d59a, `/tmp/noob_el/bench_9967d59/experiments/`, steps 1 to 18,000 trained under F = 821dfadf
and the rest under F2 by resume; `checkpoints/latest.pth` at step 20000, trained on all 532 pool cells (label set v1.1, root
`pool532_v11`, no sealed stem), seeds 5 to 9. Each dump's `checkpoint_md5` must equal the `LATEST.md5` that fin2 relayed for that
run, and its `train_code_revision` is F2 (read check, section 8).

| Id | What | Runs | Weights key | Inference | Decision rule |
|---|---|---|---|---|---|
| **C1** | full-pool PF (baseline; card `house_r34_unetpp_pf_v11`, md5 a4a46a52) | `fin_pf_v11_pool_s5..9` | `model` | plain (one view), fp32 | argmax over 24 classes (OP-A) |
| **C2** (**the final model**) | full-pool HRNet-W18 U-Net++ + SWAD (card `hrnet_w18_unetpp_swad_const_pf_v11`, md5 98f152de) | `fin_hrnet_swad_v11_pool_s5..9` | `swad` (uniform weight average over steps 10,000 to 20,000, no BN re-estimate) | D4: 8 views (rot90 by 0 to 3 quarter turns, each with and without a flip of W), softmax per view in fp32, probabilities averaged over the 8 views (`bench/tta.py` mode `d4`, scales [1.0]) | pred = argmax of log(p + 1e-12) over 24 classes (= argmax p up to float ties; `bench/tta.py cell_maps`) |
| **C3** | the 5-seed mean-softmax ensemble of C2 | the 5 C2 dumps of the set | `swad` | pbar = mean over the 5 seeds of exp(logp_s), logp_s = float16 log(p_s + 1e-12) of each seed's D4 probabilities as dumped (`bench/derived.py ens_maps`, the B5 D4ENS3 machinery) | pred = argmax of log(pbar + 1e-12) (= argmax pbar up to float ties; the ttafix rule, so the dump check cannot fail at a near-tie) |

- **No threshold, bias, class weight or view weight is set on, or chosen with, any sealed cell.** OP-A only on both sets: OP-W
  (a cross-fitted crack bias) needs folds, and a bias fitted on a sealed set would be tuning on it.
- **Deployable single model:** C2 seed 5, designated in FINAL_RULE.md section 1 before any number (no selection by score).
- **Which is "the final model":** C2 (D: lead's ruling Q1; S: deployable at 1/5 of C3's cost; the public rows are single models).
  C3 is reported beside (entry class (c), ensemble) and cannot replace C2 in the claim, whatever its numbers.
- **Comparators beside, not candidates (decide nothing):**
  - **E-PF** = the 5-seed mean-softmax ensemble of C1 (plain views; same pred rule as C3), E1 only: the ensemble comparator
    that protocol 6.1 (c) asks for beside an ensemble row (C3). Not equal in inference cost: C3 runs 8 views per model, so it
    costs 8 x E-PF (stated with every C3 - E-PF line).
  - **C1-D4** = C1 with D4 (same views as C2), on both sets, **only if** the fin CV5 TTA read (FINAL_RULE section 4, row (a)) says
    "B5 TTA RESULT REPLICATED ON CV5V3 / CV02" (FINAL_RULE section 7 item 3). The registration records which (section 9).
- **FLAGs of the fin CV5 read** (FLAG D4, FLAG C2; FINAL_RULE section 4) go to the lead and the user before registration. The
  candidates above stand unless they rule otherwise; a change of a candidate or a readout is a new version of this file (new md5,
  re-review) before registration. The registration refuses while a FLAG is present and no ruling is recorded.
- **Pre-registered contingency (plain dumps):** the plain path takes pred = argmax of the logits and checks it against the maps
  from log(p + 1e-12) (dumpfmt.check_cell); at a float32 near-tie of the two top classes a dump fails closed (rc != 0, nothing
  relayed; seen once with a random 2-channel test model, never in the CV5 plain dumps). If a C1 plain dump fails so, that one
  dump is redone with `--tta id` (the same single view through bench/tta.py, pred = argmax log(p + 1e-12), first index on
  ties) in a second sealed queue whose job list is registered as an amendment (ledger line) before it runs; the read's
  manifest expectation for that dump (tta = mode_spec('id')) is a small change reviewed before the read; nothing else
  changes, and the verdict names it.
- Dumps: cv02, deploy G (this opening's commit on F), `scripts/bench_infer.py` (G) with `--opening`, CUDA fp32, TF32 off, batch 8,
  one GPU model for all dumps of an opening (the read refuses two). E1: C1 and C2 dumps carry float16 `logp` (`--logp
  --ens-member`, the ensemble members); test50 dumps carry none.

## 3. Labels (scoring)
- **E1:** the set's own masks as in E1 openings #1 to #7: `ext117/masks` (the release `20221008` masks, class 24 (sp mono of the
  newer releases) to 2, classes 25 to 28 (scuff, corrosion cell, brightening, star) to ignore) with `ext117/ignore` (ignore px not
  scored); bench label set `set` of `e1_106`. Their md5 manifest is written at registration (before any dump) and checked by the
  read.
- **test50:** **v0** = BenchmarkEL `20211104` `labeled/masks_coded` (the labels of Pratt 2023, SEiPV-Net and, presumably, PV-S3),
  no ignore, values 0 to 23 (bench/cellmeta.py label set `v0`; the 50 files' md5 manifest written at registration); and **v1.1**
  = `bench_data/masks_v11` (MANIFEST.md5 9c0e0687; 236 scuff px in 2 cells ignored), our protocol labels.

## 4. E1: the primary contrast and what confirms the final model
**Metric:** crack relF1@2 at OP-A (relP@2 = share of predicted crack px within 2 px of GT crack; relR@2 = share of GT crack px
within 2 px of a predicted crack px; F1 of the two; counts pooled over the scored px of the 106 cells; m0core / score_ext formulas).
**Contrast P:** Delta = mean over seeds 5 to 9 of relF1@2(C2_s) minus mean over seeds 5 to 9 of relF1@2(C1_s).
**Interval:** seed-aware two-stage bootstrap (the pattern of opening #7's named claim and of protocol 5.4): per draw (i) the 71
clusters are drawn with replacement (cells weighted by their cluster's multiplicity), (ii) for each arm independently 5 models are
drawn with replacement from its 5, (iii) each drawn model's pooled relF1@2 on the weighted cells, arm value = their mean,
Delta* = C2 value - C1 value. 2,000 draws, `random.Random(0)`; 95% percentile interval (`scripts/bench_open_read.py`).
**Margin:** M = 0.010 (the protocol's relF1@2 margin on cv02, section 5.4; fixed now, not re-estimated on E1).

| Outcome of P | Condition |
|---|---|
| **CONFIRMED** | Delta >= M, lower end of the 95% interval > 0, and every guard G1 to G4 passes |
| **GAIN, FAILING GUARDS NAMED** | Delta >= M and lower end > 0, some guard fails (each failing item named); no confirmed claim |
| **NOT CONFIRMED** | otherwise; worded "WORSE" if the upper end of the interval < 0, else "interval holds 0" (with the sign of Delta) or "below M" |

**Guards** (C2 against C1, point values = means over the 5 seeds, OP-A, bounds inclusive):
- G1 width, pooled: (predicted / GT crack px of C2) / (the same of C1) in 0.85 to 1.15;
- G2 width per source with >= 40 cells in E1: CSIR (101 cells) only; same band;
- G3 false crack px on the crack-free cells of E1 (GT crack px 0 under the E1 labels; about 74 cells): C2 <= 1.5 x C1;
- G4 mIoU-R13 (the 13 robust classes with GT): Delta >= -0.010.
- **Inactive IoU is reported, never decides** (E1 has 10 inactive cells; label-noise band +-0.05 to 0.07, dataset_audit F4): printed
  with both intervals; an interval wholly below 0 is stated in the verdict as "inactive lower", without changing the outcome.

**Printed with P, deciding nothing:** relP@2 and relR@2 deltas; relF1@1; strict crack IoU delta with its seed-aware interval and
the **convention band +-0.019** (dataset_audit/REPORT.md F1; "inside" or "outside the band"); the fixed-model interval of P
(clusters only, the 10 models fixed: a statement about these trained models, not the recipe); per-seed relF1@2 of every model.

**What the claim says if CONFIRMED** (S): "On 106 cells of unseen modules (E1), the final model (C2: HRNet-W18 U-Net++ + SWAD +
D4) has a higher crack relF1@2 than the full-pool PF baseline, by Delta [lo, hi] (seed-aware, 71 clusters), with crack width and
false crack px inside the guards." Not claimed: anything about inactive, about the 50-cell test, about cells unlike E1 (101 of 106
are CSIR), or about the deployable seed 5 alone.

## 5. E1: printed beside (decide nothing)
Same statistics (both intervals where an arm has several models):
- S1 C3 - C1; S2 C3 - E-PF (the ensemble comparator, 1/8 of C3's views; fixed models); S3 C3 - C2 (the ensemble's gain over
  its own members);
- S4 C2 seed 5 (the deployable model) - C1; S5 E-PF - C1;
- if C1-D4 is in the opening: C1-D4 - C1 (TTA on PF) and C2 - C1-D4 (the candidate against the baseline with the same views);
- A/A: C1 seeds {5, 6} against {7, 8} (seed-aware; descriptive SE on E1);
- strata (point values and both intervals): CSIR (101) and BMRK (5) cells, half-cut (62) and full (44) cells, crack cells (32)
  and crack-free cells; per-class IoU of the 13 robust classes; component recall and precision (crack >= 20 px, inactive >= 100 px).

## 6. Power on 106 cells (S, stated before the opening)
- Variance from opened E1 results (E): opening #7's judge put the SE of a 5-v-5 single-model contrast of E1 relF1@2 under this
  seed-aware bootstrap at about 0.019 (cluster part about 0.013, seed composition about 0.014; `protocol_SKR2C.md` line 148).
  Per-model seed sd of E1 relF1@2 in openings #3, #5, #7: about 0.017 to 0.026 (from their R1 thresholds 0.0429 / 0.0351 / 0.0281).
- With a two-sided 95% interval, the chance that the lower end clears 0 (power = Phi(Delta / SE - 1.96)) at a true Delta of
  **+0.020 / +0.030 / +0.038 / +0.047 / +0.053** is about **18% / 35% / 52% / 70% / 80%** at SE 0.019 (22% to 88% at SE 0.017;
  16% to 71% at SE 0.021). The smallest effect with 80% power is about 2.8 x SE = **0.048 to 0.059**.
- Expected size (S): the CV5 evidence is about +0.006 to +0.010 for the swad readout over PF (c3x read, selection-biased) plus
  about +0.017 for D4 (B5, gaint, PF); if E1 behaves like the pool, the likeliest honest outcome is **"NOT CONFIRMED, interval
  holds 0"**, which is not a refutation. The fixed-model interval (clusters only; SE about 0.013) is printed beside and is the
  narrower statement about the trained artefacts.

## 7. test50 opening #19: the public table (decides nothing alone)
Rows: C1 and C2 (each: mean over the 5 seeds with min to max, and seed 5 alone), C1-D4 if in the opening; beside them the
published rows of T/harness/final/PUBLIC_BENCH.md section 2a, copied with their sources. All 50 cells, 512 px, OP-A.
- **Pratt 2023 (on v0; like-for-like):** per-image IoU, median over the cells, for crack [14], gridline [15], inactive [11],
  ribbons [4], spacing = union of [1, 2, 3]; **rule A** (cells without the class in GT left out; the reading that fits the paper)
  as the comparison, rules B (absent = 0) and C (absent = 1 if nothing predicted, else 0) printed beside; "avg defects" = mean of
  the three defect medians; median recall (rule A) of the three defects (bench/public_metrics.py).
- **PV-S3 (on v0):** pooled IoU, P, R, F1 of crack, gridline, inactive and their mean, under both background rules (all px;
  background-GT px dropped); the row says "split assumed = the release split; resolution unstated".
- **SEiPV-Net (on v0), a family of readings, never one number:** pixel accuracy, micro IoU = acc / (2 - acc), fw-IoU, support-
  weighted F1, per-image mean IoU (absent-and-unpredicted = 1; absent skipped), class means over GT classes with and without
  background, over the union classes (formulas of results/seipv_compare/miou24.py md5 787e920e).
- **Our protocol on v1.1:** relF1@2 (relP@2, relR@2), strict crack IoU (with the band), inactive IoU, mIoU-R13, width ratio, false
  crack px on crack-free cells; on all 50 cells, on the 49 without the noisy cell `CSIR_00070_r8_c4`, and on the 16 cells whose
  image id has no pool cell in its physical module (results/stageC/split_integrity/sealed/sealed_image_ids.tsv,
  `p532_cells_in_module` = 0; the list file is pinned at registration). One contrast C2 - C1 relF1@2 with the seed-aware interval
  over 48 clusters, printed as "secondary, decides nothing alone".
- Training data differ from the published rows: ours 532 cells (478 train + 54 val) with v1.1 labels, theirs 478 x 4 offline
  augmentation on the old labels; theirs single runs with unstated selection; ours final weights, 5 seeds. Rows of other test sets
  (Attention-Based SegNet, Ramadan, Hanifi, Torpey) are printed as "other test set, not comparable" only.

## 8. Read and refusals (run_opening_read.sh; the lead runs it once, after all dumps are relayed)
The read refuses, before it creates its output folder, unless: the registration record exists with the md5 the lead logged in
both ledgers, and names this file's md5, the job list md5, the opening numbers (E1 #8, test50 #19), the sealed mask manifests and
the C1-D4 choice; this file's md5 is still the registered one; the read worktree is at the pinned commit R with no tracked
change; every expected dump is relayed (`.ok` and the `relayed` log line); every manifest has the expected run id, set, opening,
seed, weights key, step 20000, fp32, tta (false or mode_spec d4), `ens_member` true exactly for the logp jobs, writer = G's
`bench_infer.py`, `train_code_revision` = F2, `checkpoint_md5` = fin2's relayed LATEST.md5 of that run; one GPU model over all dumps;
the sealed mask files still match the registered manifests. Then: per-cell records (bench_score records; E1 labels `set`,
test50 `v0` and `v11`), C3 and E-PF by `bench_ens_dump.py --opening`, the reads (`bench_open_read.py`), the verdict
(`opening_verdict.py`), MD5.txt.

## 9. Procedure (who runs what, in order; details and commands in OPENING_REQUEST.md section 4)
1. **Before:** the 10 full-pool runs end in fin2 (the resume of fin's step-18000 checkpoints; FINAL_RULE_ADDENDUM_1.md) with
   `trained fin_* rc=0` for all 10 and fin2's `BENCH CV02 Q ALL DONE`, and fin2's relay ends (RELAY ALL DONE, 10 of 10: slim.pth,
   LATEST.md5); the opening starts only after both; fin's CV5 TTA read and verdict are written; FLAGs, if any, ruled by the lead
   and the user.
2. **Independent review** of this package (OPENING_REQUEST.md): PASS, pinned to this file's md5.
3. **Registration (lead, before any sealed dump):** `opening_register.sh` writes the job list (with or without C1-D4), the sealed
   image staging dir and its MANIFEST, the sealed mask manifests (E1 masks + ignore, v0 test50), REGISTERED.txt (read-only) and
   prints its md5 and two ledger rows; the lead adds row #8 to e1_openings.md and row #19 to test_openings.md section B as
   "registered, not opened", with that md5, **before** step 4.
4. **Deploy G** to cv02 (`c3_deploy.sh <G>`), **stage** the sealed images (images and lists only) to cv02, **render** (0 FAIL),
   **place** and **arm** the queue `open` (dump-only, strict lanes); relay to gaint.
5. **Read once** (`run_opening_read.sh`): records, ensembles, reads, verdict. The ledgers get "opened <start> to <end>" and the
   result file. Sealed images are removed from cv02 after the relay check; logp dumps are kept (gaint or NAS) for the record.
6. Repeats need TAG and are not the registered read.

## 10. Disclosures (printed in the verdict and in every table that uses these numbers)
- **test50 leakage** (results/stageC/SPLIT_INTEGRITY.md 5b): 8 test cells are the same physical cell as a pool cell, 7 are
  neighbouring crops of a pool cell, 19 more share a physical module with pool cells; our full-pool models trained on all of
  them. test50 numbers are in-distribution numbers with known leakage. Published rows trained on the 478 train cells (which hold
  most of these links too).
- **Prior looks:** test50 has 18 counted openings and many uncounted reads (test_openings.md A, B); E1 has 7 registered openings,
  three looks at one contrast (#5 to #7), many reads before the 31 Oct policy, and one use of published E1 contrasts to judge
  development instruments (R0, ledger line of 15 Nov). The final models (C1, C2, C3, E-PF, C1-D4) were never scored on either set.
- **Selection:** the readout `swad` was chosen after the c3x CV5 read (FINAL_RULE section 0); D4 was adopted from the B5 CV5 read;
  both selections used pool cells only, so E1 is an unbiased test of them; the candidate list was fixed by the user before any
  number of the final models. HRNet + SWAD (swad_bn) failed its registered CV5 confirmation (C3X_READ.md: NOT CONFIRMED); the
  fin CV5 TTA verdict is quoted in the opening's verdict file as registered.
- **E1 composition:** 101 of 106 cells CSIR, 62 half-cut cells while the pool has none, 10 inactive cells, crack in 32 cells
  (handbook 04; dataset_audit F7); labels of release `20221008` (the same crack convention as v1.1). No published comparator exists.
- **Multiplicity:** one primary contrast (P) on E1; everything else printed beside is descriptive; test50 decides nothing.
- **Machine:** all dumps of an opening on cv02 (one GPU model); the read on gaint CPU.
