# Idea 1: E1 threshold / calibration check (diagnostic)

calib, 31 Oct 2026, v1. Tags: E measured (file path), R literature (Research MCP id), S judgement.
- **E1 is sealed.** Every E1 number here is DESCRIPTIVE. "Oracle" columns use the set's own labels as upper bounds on what any threshold could do; they choose nothing.
- **Selection / measurement set** for the adaptation tests: Hanifi `_rf` (106 after hygiene: −7 CSIR_00300, −4 val/test-module cells).
  - The deciding subset is **F51**: the 51 full cells from modules not in train; 12 crack cells, 36 modules. It is the same as found's `t9_rf_sets.tsv` and judge's ruling.
  - The 36 `_rf` half-cuts (H36) are reported, but their crack labels are unusable (§2).
- No test cell was read.

## Verdict v2 (S, from E below; revised 31 Oct after judge's review)
**Within each E1 stratum the crack failure is ranking (features). Across strata there is a large cell-type calibration offset: half-cuts are under-confident by about 5-7 in crack log-odds.**
- **DROP:** label-free per-panel threshold adaptation (per-module quantile, tail shift).
- **PARK:** half-cut routing (one bias for half-cut cells, one for full). It is deployable, since cell type is visible in the image, but blocked until a labelled half-cut crack set outside E1 exists to choose its bias.
- **KEEP:** the diagnostic.

**What changed from v1.** Items 2-3 said "calibration is minor" and "thresholds close at most ~38%". judge showed, and I reproduced, that a two-parameter cell-type split recovers about half of the per-module oracle gain:
- E1 relF1@2 with one oracle bias for half-cuts and one for full cells (exhaustive pair search on E1's own labels; diagnostic only):
  - FINAL 0.432 (deployed) → 0.461 (one bias) → **0.518** (two biases, b +5.4 / −0.8);
  - SUP100-PF 0.445 → **0.490**; SUP100-g 0.381 → **0.443**.
  - A sh29 / other split gives 0.522 / 0.485 / 0.451, but it needs scuff labels, so it is not deployable.
- Caveat (S): 2 parameters fitted on 106 cells are mildly optimistic, and the half-cut bias may not transfer across module families.
  - The only non-E1 half-cut labels (Hanifi H36) ask for b −0.8, but they are unusable SAM specks.
  - A legitimate test needs that set cleaned (~2-3 h, user's call) or B2 masks. Then choose the half-cut bias there and read E1 once.

v1 items, with 2, 3 and 6 superseded as marked:
1. **The PR curve itself is worse, not just shifted** (FINAL, `figs/idea1_FINAL.png`).
   - E1 never reaches relP@2 0.90 at any bias.
   - At relP@2 ≥ 0.70, val recovers relR@2 0.954; E1 recovers 0.226 (other 77 cells: 0.542; 29 scuff + half-cut cells: 0.187).
   - Crack-free E1 cells draw ~10x the false crack px of crack-free val cells.
2. **[Superseded by v2: across strata, calibration is large.]** Calibration is stratum-specific:
   - The 29 scuff + half-cut cells are under-confident: the best bias on their own labels is +6.8 for FINAL and +9.6 to +9.7 for the single-model arms, against about +1 on val.
   - The other 77 cells are over-confident: best bias −0.8 (FINAL) to −4 (grid edge, single models).
   - One global shift cannot serve both.
3. **Upper bound with labels** (v2: a two-bias cell-type split gets 0.518 of this; see above). Per-module biases chosen with E1's own labels lift FINAL's E1 relF1@2 0.432 → 0.610 (val 0.896), so thresholds close at most ~38% of the gap.
4. **Label-free rules realise none of it.** The pre-stated per-module quantile rule (Om's), a tail-shift variant and half-cut routing all lose on `_rf` F51 and on E1, for FINAL and for both 5-seed arms. The quantile rule turns 61-100% of crack-free cells into false alarms.
5. **PF's E1 gain (descriptive) is part ranking, part operating point.**
   - E1 relF1@2 at b = 0: SUP100-PF 0.445 vs SUP100-g 0.381 (+0.064).
   - At each arm's best E1 bias (oracle): 0.453 vs 0.403 (+0.050).
   - On the 29 scuff + half-cut cells: +0.106 at b = 0 but +0.044 at the oracle, so about 60% of PF's gain there is where its threshold lands, not better ranking.
   - On the other 77 cells PF ranks slightly worse (oracle relF1 0.576 vs 0.589), matching the reported crack IoU drop there.
6. **Consequence (v2):**
   - Per-run, val-chosen operating points (idea 7) handle the global offset.
   - The cell-type offset needs half-cut routing, which is blocked until labelled non-E1 half-cuts exist. That raises the value of the Hanifi half-cut crack cleanup or B2 masks: the user's call, via team-lead.
   - Within-stratum ranking, the larger part, needs features or input (ideas 3, 5, 8) and the scuff context (B3).
   - For PF2 (S, judge relayed to coach): report "E1 sh29 oracle relF1@2" beside the argmax E1 crack-recall co-primary, as a ranking-only readout. Part of PF's sh29 gain is operating point.

## 1. Premise check (E)
**Run (gaint CPU, nice 19, 8 threads; 14:00-14:41 IST; no test):**
- **Dump:** `scripts/calib_dump.py` (v1 a2e088ed for these dumps; the current version c172717e is functionally identical on CPU).
  - Per cell: crack margin m = log p_crack − max_{k≠crack} log p_k, plus the other-class argmax.
  - FINAL (p6_L3_100pct_s0-2 + p16_A_100pct_s3-4, mean softmax, D's gaint copies).
  - SUP100-PF and SUP100-g (f3_SUPPF / f3_SUP_100pct_s0-4, e544133), per seed. MIM100-PF and CP100 for idea 7.
  - Sets: val 54, E1 106 (ext117 ignore applied), `_rf` 106.
  - Dumps on gaint `/home/noob/work/calib/out/dump/` (~10 GB).
- **Records:** `scripts/el_metrics.py` makes per-cell records over b = −4 .. +12 (step 0.1, + 0.75), with b added to log p_crack: FINAL's +0.75 mechanism, higher b = lower threshold.
  - Records are in `calib_out/rec/` (90 files, MANIFEST.md5 856faa7d, 54 MB).
  - Per cell, per b: crack predicted / TP (FP = pred − tp, FN = n_gt − tp), rel2 counts, components, inactive.
- **Scorer checks (E):**
  - FINAL val/E1 records equal D's `d_checks/d_cells.json` at b 0 (|Δ| 0 on all pooled metrics).
  - **judge check 1:** E1 pixel crack recall at b = 0, seed mean, records vs o1_extra / m0:
    - SUP100-PF 0.2133 vs 0.2133; SUP100-g 0.1689 vs 0.1687;
    - on the 29 scuff + half-cut cells, 0.1522 vs 0.1521 and 0.0939 vs 0.0941.
  - **judge check 2, val:** 0.5961 vs 0.5960 and 0.6503 vs 0.6504.
  - Per-seed |Δ| ≤ 0.0022: CPU fp32 records vs GPU bf16 m0.
- **Width (judge):** E1 GT crack is about 1.5x wider than train, so pixel recall has a width ceiling.
  - The verdict therefore rests on relR@2, relP@2 and component recall, which tolerate a 1-2 px width mismatch. Pixel recall is shown beside them (fourth panel of each figure).
  - The scuff + half-cut gap shows in all three (FINAL at b +0.75: pixel R 0.125, relR@2 0.234, component recall 0.172; val: 0.706 / 0.887 / 0.832), so it is not a width artefact.

### 1.1 Val vs E1 strata vs `_rf` F51 (E, `calib_out/idea1_summary.txt`)
relF1@2 = harmonic mean of relP@2 and relR@2. "dep" = deployed bias (FINAL +0.75, single runs 0). Seed arms: mean (sd) of 5.

| stratum | metric | FINAL | SUP100-PF | SUP100-g |
|---|---|---|---|---|
| **val 54** | relR@2 / relP@2 at dep | 0.887 / 0.906 | 0.846 / 0.929 | 0.851 / 0.918 |
| | relF1@2 at dep / oracle | 0.896 / 0.897 | 0.886 / 0.889 | 0.883 / 0.885 |
| | oracle b | +1.1 | +2.4 (0.9) | +1.0 (0.7) |
| **E1 all 106** | relR@2 / relP@2 at dep | 0.356 / 0.550 | 0.380 / 0.540 | 0.292 / 0.556 |
| | relF1@2 at dep | 0.432 | 0.445 (0.025) | 0.381 (0.025) |
| | relF1@2 at oracle b (E1 labels) | 0.461 | 0.453 (0.022) | 0.403 (0.024) |
| | relF1@2 at per-module oracle | 0.610 | 0.537 (0.026) | 0.521 (0.015) |
| | invisible at b +12 (1 − relR@2) | 0.262 | 0.402 | 0.415 |
| **E1 scuff + half-cut 29** (75% of E1 crack px) | relR@2 / relP@2 at dep | 0.234 / 0.665 | 0.270 / 0.650 | 0.178 / 0.639 |
| | relF1@2 dep / oracle / per-module oracle | 0.346 / 0.490 / 0.556 | 0.381 / 0.447 / 0.479 | 0.275 / 0.403 / 0.457 |
| | oracle b | +6.8 | +9.7 (1.9) | +9.6 (1.2) |
| | invisible at b +12 | 0.338 | 0.493 | 0.504 |
| **E1 other 77** | relR@2 / relP@2 at dep | 0.724 / 0.484 | 0.710 / 0.448 | 0.638 / 0.507 |
| | relF1@2 dep / oracle / per-module oracle | 0.580 / 0.623 / 0.764 | 0.548 / 0.576 / 0.665 | 0.563 / 0.589 / 0.688 |
| | oracle b | −0.8 | −4.0 (grid edge) | −3.4 |
| **`_rf` F51** | relR@2 / relP@2 at dep | 0.867 / 0.848 | 0.813 / 0.860 | 0.838 / 0.833 |
| | relF1@2 dep / oracle | 0.857 / 0.866 | 0.835 / 0.838 | 0.836 / 0.837 |

- **Per-module oracle:** coordinate ascent on the pooled relF1@2 over one b per module, starting from the global oracle. E1 has 71 modules for 106 cells, so this is near a per-cell oracle and optimistic.
- **F51** (unseen modules, full cells, Hanifi labels) sits near val for every model. Unseen panels as such are not the problem; the failure is concentrated in the E1 half-cut + scuff context and in E1 false positives.

**Matched precision (FINAL): max relR@2 subject to relP@2 ≥ x.**

| x | val | E1 all | E1 other 77 | E1 scuff + half-cut 29 |
|---|---|---|---|---|
| 0.90 | 0.892 | not reached | not reached | not reached |
| 0.80 | 0.941 | 0.157 | 0.456 | 0.060 |
| 0.70 | 0.954 | 0.226 | 0.542 | 0.187 |
| 0.60 | 0.964 | 0.300 | 0.630 | 0.346 |

**Crack-free cells (FINAL, +0.75):**
- val: 5.8 predicted crack px per cell, 3.2% flagged (≥ 20 px);
- E1: 55.0 px per cell, 28.4% flagged.

## 2. Label-free per-module adaptation
Stated in `scripts/idea1_adapt.py` (docstring) before any of its numbers. Measured on `_rf`; E1 descriptive.

| scheme | rule |
|---|---|
| A0 | global b = the run's val-chosen OP-rel b (max val relR@2 s.t. val relP@2 ≥ 0.90) |
| A1 (Om's per-module quantile) | per module, the b at which the module's predicted crack area fraction reaches val's at A0 |
| A2 (tail shift) | b_A0 + (module b − val b), each taken where 0.01% of px are predicted crack |
| A3 (cell-type routing) | half-cut cells get the b with max relF1@2 on `_rf` half-cuts; full cells keep A0 |

**Kill criterion (stated with the rules):** beat A0 on F51 relF1@2 by ≥ 0.02 without raising crack-free false alarms by > 5 points.

**E (`calib_out/idea1_adapt.txt`); relF1@2, and false-alarm rate on crack-free cells in brackets:**

| set | scheme | FINAL | SUP100-PF (5) | SUP100-g (5) |
|---|---|---|---|---|
| **`_rf` F51** | A0 | **0.855** (20.6%) | **0.811** (7.1%) | **0.829** (17.1%) |
| | A1 | 0.434 (100%) | 0.588 (61.2%) | 0.452 (98.8%) |
| | A2 | 0.500 (88.2%) | 0.494 (55.3%) | 0.350 (89.4%) |
| | A3 | = A0 (no half-cuts) | = A0 | = A0 |
| **E1 all** (descriptive) | A0 | **0.436** (29.7%) | **0.450** (32.7%) | **0.393** (35.4%) |
| | A1 | 0.335 (100%) | 0.369 (86.8%) | 0.288 (99.2%) |
| | A2 | 0.356 (91.9%) | 0.389 (84.3%) | 0.273 (93.2%) |
| | A3 | 0.345 (25.7%) | 0.445 (38.6%) | 0.365 (32.4%) |

- **All fail the kill criterion.**
- **A1/A2, structural reason (S):** crack prevalence differs by module, and most modules have no crack. Matching a predicted-area quantile forces cracks onto clean modules. That is the known weakness of quantile / prevalence-matching thresholds.
- **A3:**
  - `_rf` half-cuts ask for b −0.8 (FINAL), while E1's half-cuts need a higher b.
  - FINAL reaches only relR@2 0.036 on the H36 crack labels, and 84% stay unreached at b +12. Judge found 48% of those px lie within 10 px of spacing, border or cut lines.
  - So H36 crack labels cannot select a half-cut bias. Judge and coach have ruled H36 out for crack selection.
  - S: no labelled half-cut crack set exists outside E1, so no half-cut-specific threshold can be chosen legitimately today.

## 3. Prior tries in the repo
- **Track M R1 / FINAL:** the crack bias was chosen on val by relF1@2 (+0.75). On clean test, 9.5% of GT crack px have p < 0.001 (`trackM/results_final.md`).
- **LA tau 1 (class-prior logit shift):** n.d. on test (`verify_100_o1.md`).
- **D (`verify_d.md`):** BN-HC routed (BN-statistic adaptation) lifts E1 target recall +0.174 at an E1 precision cost of 0.085, failing the pre-stated cost.
  - That fits §1: the scuff + half-cut cells are under-confident, but buying recall there costs precision at about the PR-curve rate.
- **27 Oct:** E1 half-cut analysis in `team_2026-10-27_unlabelled/ideas.md` (F11 scuff streak; F17 proposer).
- **New here:** the stratified bias sweep, the matched-precision comparison, the oracle upper bounds and the label-free tests. No earlier run did these.

## 4. Literature (R)
- **Ovadia et al.** (arxiv:1906.02530): under dataset shift, calibration and accuracy degrade together, and ensembles degrade least. That matches FINAL ranking better than single models on E1 (oracle relF1@2 0.461 vs 0.403; 26% vs 41% invisible at b +12).
- **Test-time adaptation survey** (doi:10.1007/s11263-024-02181-w): label-free target adaptation (BN statistics, entropy) is the standard family. Per-panel thresholds are not. Idea 9 (T9) covers the BN route.

## 5. Cost, expected effect, kill, protocol
- **Cost so far:** ~0.75 CPU-h on gaint (dump 32 min + records 8 min); laptop analysis minutes.
- **Expected E1 effect of a per-panel threshold method (S):** ≤ 0 label-free (§2). The upper bound with labels is +0.18 relF1@2 (FINAL), unreachable without E1-like labelled half-cuts.
- **Kill:** met for the label-free rules (§2), so **DROP** them. No protocol.
- **v2:** half-cut routing (two biases by cell type) is **PARKED**, not dropped. It is worth up to +0.05-0.06 relF1@2 on E1 (oracle, descriptive). Its gate is a labelled non-E1 half-cut crack set (Hanifi H36 cleanup or B2 masks) to choose the half-cut bias, then one E1 read. Cost then: 0 GPU-h, CPU minutes.
- **Keep as diagnostics** (cheap, CPU, no selection):
  - the stratified bias sweep and oracle bounds, for any new arm (PF2, THIN-B3, idea 3/5/8 arms);
  - "oracle relF1@2 on E1 scuff + half-cut", as a ranking-only readout that a threshold shift cannot fake. Descriptive only.

## 6. Files (md5, first 8)
| file | md5 |
|---|---|
| `scripts/calib_dump.py` (current; dumps made with v1 a2e088ed) | c172717e |
| `scripts/el_metrics.py` | 3f71a000 |
| `scripts/idea1_analysis.py` | e1714aac |
| `scripts/idea1_adapt.py` | 538b5206 |
| `scripts/calib_pull_analyse.sh` | a3e3c908 |
| `calib_out/rec/MANIFEST.md5` (90 per-cell record files) | 856faa7d |
| `calib_out/idea1_summary.txt` | b8ef0ef4 |
| `calib_out/idea1_adapt.txt` | ac61cbdb |
| `calib_out/idea1_rows.json` (all rows and curves) | c5d027cb |
| `calib_out/F51.txt` | b04d15d8 |
| `figs/idea1_FINAL.png` | 26392db3 |
| `figs/idea1_SUPPF5.png` | 377a2174 |
| `figs/idea1_SUP5.png` | 267d0488 |

---

## judge verdict (31 Oct 2026, 14:48 IST from date; report md5 7a61c382 as reviewed)

**Verdict:**
- **DROP label-free per-panel thresholds** (A1/A2/A3): agreed; the kill is met and reproduced.
- **PASS the diagnostic** (stratified sweep, oracle bounds) as a standing reported readout.
- **REVISE one headline claim before this goes into the handbook.** "Calibration is a minor part" understates a cheap, deployable cell-type split (item 1 below).

### What I reproduced (E)
Own aggregation code on calib's records (`judge/idea1_recompute.py`, md5 c156951b; inputs `calib_out/rec/`, MANIFEST 856faa7d, 90/90 files OK).
- **Matched-precision table, FINAL** (max relR@2 at relP@2 ≥ 0.90 / 0.80 / 0.70 / 0.60):

  | Set | 0.90 | 0.80 | 0.70 | 0.60 |
  |---|---|---|---|---|
  | val | 0.892 | 0.941 | 0.954 | 0.964 |
  | E1 | n/r | 0.157 | 0.226 | 0.300 |
  | other 77 | n/r | 0.456 | 0.542 | 0.630 |
  | scuff + half-cut 29 | n/r | 0.060 | 0.187 | 0.346 |

  **Exact.**
- **relF1@2, deployed / global oracle:**
  - FINAL: val 0.896 / 0.897 (b +1.1); E1 0.432 / 0.461 (b +2.1); other77 0.580 / 0.623 (b −0.8); sh29 0.346 / 0.490 (b +6.8); F51 0.857 / 0.866.
  - SUPPF5 vs SUP5 (seed means): E1 0.445 vs 0.381 at b 0, 0.453 vs 0.403 at oracle; sh29 0.381 vs 0.275, oracle 0.447 vs 0.403.
  - **All exact.**
- **Label-free rules, `_rf` F51, FINAL:** A0 0.855 at 20.6% false alarms (exact). A1 0.414 at 100% (calib 0.434 / 100%).
  - The small difference is my reading of "reaches": the smallest b whose module crack-area fraction is ≥ val's at A0. The fail is the same either way.
- **The judge self-checks** (E1 and val recall vs `o1_extra` / m0): reported in §1 and consistent with my `e1_boot.py`.
- **Selection discipline:**
  - every operating point is chosen on val;
  - the A rules were stated in `idea1_adapt.py`'s docstring (I can see the text, not its timing relative to numbers; calib's log says before);
  - E1 is descriptive throughout, the oracles are labelled, and test was not read.

### 1. What must change: cell-type calibration is not minor (E, new)
- A **deployable** split uses cell type only, which is visible in the image: half-cut (58) vs full (48), one bias each.
- With oracle biases it lifts E1 pooled relF1@2:

  | Model | deployed | one global bias | two biases (half-cut / full) |
  |---|---|---|---|
  | FINAL | 0.432 | 0.461 | **0.518** (b +5.4 / −0.8) |
  | SUPPF5 (seed mean) | 0.445 | | **0.490** |
  | SUP5 (seed mean) | 0.381 | | **0.443** |

  Splitting sh29 vs the other 77 instead gives FINAL 0.522, but that split needs scuff labels.
- So two parameters recover about half of the per-module oracle gain (0.086 of 0.178 for FINAL).
- Correct reading:
  - **within each stratum** the E1 failure is ranking (the matched-precision rows, reproduced);
  - **across strata** there is a large, cell-type-shaped calibration offset (half-cuts under-confident by ~5 to 7 in log-odds);
  - one global threshold cannot serve both.
- **Caveat (S):** these are oracle numbers on E1's own cells (2 parameters on 106 cells: mildly optimistic). The half-cut bias may not transfer across module families. Hanifi's half-cuts asked for b −0.8, but on unusable labels.
- **Consequence:** half-cut routing is a near-free inference lever. It is blocked only because no labelled half-cut crack set exists outside E1 (A3, H36).
  - That raises the value of the 2 to 3 h Hanifi half-cut crack cleanup, or of B2 masks: the user's call, via team-lead.
  - With such a set, A3 becomes a legitimate test: choose the half-cut bias there, then read E1 once.
  - Replace verdict items 2 and 3 ("minor", "close at most ~38%") with this reading.

### 2. For PF2 (S)
- calib's §1 point 5: PF's sh29 gain is +0.106 relF1 at b 0 but +0.044 at each arm's oracle bias. So about 60% of it is where PF's argmax lands.
- PF2's E1 crack-recall co-primary is read at argmax, so it can pass partly through operating point.
- coach's precision flag covers part of this. Add calib's "E1 sh29 oracle relF1@2" as a **reported** ranking-only readout beside it, no verdict change. I'm passing this to coach.

### Cost, effect, kill
- Spent ~0.75 CPU-h.
- No method arm. The kill for label-free thresholds is met.
- The diagnostic is cheap and should run for every new arm (PF2, THIN-B3, ideas 5 and 8).

### Tags
- E: matched-precision, oracle and adaptation numbers reproduced; the cell-type split is new.
- R: arxiv:1906.02530 and doi:10.1007/s11263-024-02181-w resolve (the latter via get_paper; the former not re-read).
- S: the "ranking within, calibration across" reading.

### judge ruling on half-cut routing in PF2 §13 (31 Oct 2026, 17:35 IST from date; answer to coach)
**V4 synthetic val is a legitimate selector for b_hc for the PF2 arms (seeds 5-9). The readout stays descriptive. FINAL is left out of the routing readout.**

**Why legitimate (E/S):**
- V4 is built only from val cells plus non-E1 pool targets (1,008 pool half-cells, CSIR_00300 excluded; `idea05` §1.2). No E1 number entered its design; the E1 comparison in idea 5 was made after the V-series was fixed.
- PF2's seeds 5-9 have never been scored on E1, so their E1 b-curves are unseen. The readout is blind for them.

**What coach's §13 wording must change:**
1. **"Under-confidence signature" is not supported** (my erratum in `idea05`, E from `domain_out/synvar.log`).
   - Pixel precision rises on V4, but relP@2 falls slightly: FINAL +0.75, 0.910 → 0.895; b 0, 0.931 → 0.922.
   - At matched relP@2 ≈ 0.91, V4 relR@2 is ≈ 0.75 vs V0 0.887.
   - So the V4 drop is mostly ranking, and V4 may show only a small bias offset.
   - Phrase the premise as "V4 reproduces the half-cut-without-scuff recall drop (geometry + intensity), not scuff; whether it carries a calibration offset is measured by the V4 − V0 oracle-b shift below".
2. **Report the selector's own offset beside b_hc:** Δb = b_hc − b_full (both on 5-seed pooled val / V4).
   - If Δb < 1.0 log-odds, label the routing readout "selector saw no half-cut offset; routing ≈ no-op". Do not read it as evidence against routing.
3. **Freeze before the opening:**
   - V4 image set and simulator (md5 of `dom_synth_variants.py` and of the 108 V4 images + masks);
   - the b_hc rule: argmax pooled 5-seed relF1@2 on V4, grid −4..+12, ties to the b nearest b_full;
   - the E1 routing key.
4. **E1 routing key:** `e1_context.tsv` halfcut=1 comes from E1 masks (classes 24/29). Label the readout "routing by known cell type".
   - A deployable version needs a label-free detector validated on non-E1 data: pool half-cells and the 582 full cells.
   - Report how many E1 cells such a detector would route differently, if one exists by then; otherwise state that it is not built.
5. **False-alarm side, reported with it:** crack px on crack-free E1 half-cut cells (routed vs unrouted), and the same on crack-free V4 cells.

**FINAL: leave it out of the routing readout.**
- Its E1 b-curves were seen on 31 Oct: calib's backfill and my two-bias oracle (half-cut +5.4, full −0.8).
- The choice to pursue routing at all, and to pick V4 as its selector, was made knowing that.
- A FINAL routed E1 number would be neither blind nor confirmatory, even with the rule fixed.
- If wanted, put it in an appendix labelled "not blind; E1 curves seen 31 Oct". It enters no conclusion.
- The same applies to SUPPF5 and SUP5 seeds 0-4 (their E1 oracles were also computed on 31 Oct).

**Expectation (S):** V4 has no scuff, and scuff + half-cut is 75% of E1 crack. Any routed E1 gain for the PF2 arms will be well below the oracle headroom. A small or null routed gain is the expected outcome, not a refutation of the cell-type offset.

### judge, 18:05 IST: routing pre-check outcome
The non-E1 pre-check FAILED for both models (SHV1: Δb +0.4 / +0.9, G +0.008 / +0.001, G_cf about 0; reproduced, see `routing_precheck.md`). Half-cut routing stays PARKED. The PF2 §13 E1 routed readout should be dropped; the non-E1 Δb / G line on SHV1 stays as a descriptive readout.
