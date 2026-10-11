# 07 Methodology, rules and statistics

**What this covers.** How an experiment is run in this project from question to verdict, and why each step exists. It covers protocol locking and amendments; how arms are designed (one change each, loss-off controls, step matching, final weights, seeds, one machine per rule); how runs are scored (revised labels, argmax, test set, primary metrics); the decision rule ("P8 rule 1"), with intuition, a worked example and its true strictness; the full rule list as given to the user on 11 Oct (R1 to R8) and the per-experiment rules; the user's standing rules and where each came from; the robustness layer (image bootstrap, leave-top-3-out, source split, E1 per-cell metrics); why val is not used for selection; what these statistics cannot tell us; and the critique of the design given to the user on 11 Oct. A checklist for reading any results README is at the end.

**Sources**
- `protocols/P6_corrected_baseline.md` to `protocols/P16_label_fraction_curve.md` (rule sections, amendments)
- `scripts/ssl_rules.py` (rule 1 code), `scripts/per_image_analysis.py` (bootstrap, leave-top-3-out, source split), `scripts_cv02/e1_aggregate.py` (E1 metrics), `scripts_gaint/rescore_label_versions.py` (scoring), `scripts/post_ssl.sh`, `scripts/post_p16.sh` (the analysis pipeline)
- `results/p6/README.md`, `results/p11/README.md`, `results/p12/README.md`, `results/p13/README.md`, `results/p14/README.md`, `results/e1/README.md`
- `~/mtp/MTP_session_handoff_2026-10-07.md`; the phase 0 and phase 1 handoffs pasted by the user on 11 Oct (copy: `sources/chat/phase0_phase1_handoffs_pasted_2026-10-11.md`)
- Memory notes `~/.claude/projects/-home-yugma/memory/mtp-el-ssl-project.md`, `server-runs-tmux-parallel.md`, `ask-before-assuming.md`
- The assistant's answer to the user on 11 Oct ~17:30 IST listing all locked rules (transcript `~/.claude/projects/-home-yugma/57bebbba-992f-43ae-8c6c-f7004d0f15c5.jsonl`, line 6728)

---

## 1. The life of one experiment

1. **Question.** One question per experiment, usually prompted by the previous result or by the user (e.g. P16 came from the user's "why we using 5 or 10% for ssl?").
2. **Protocol, locked.** A markdown file in `~/mtp/research/protocols/` is written and committed (local git repo `~/mtp/research`) before any run. It fixes the question, the arms, everything held constant, the metrics, the decision rules, the robustness checks and what is not claimed (section 2).
3. **Code.** If the experiment needs a code change, it is made as an opt-in switch whose default leaves old runs bit-identical, with unit tests, in a separate git worktree on gaint (e.g. `el_p13` for P13). The commit hash goes into the protocol.
4. **Deploy.** The exact commit is copied to cv02 with `git archive` into a fresh directory under `/tmp/noob_el/` and recorded in a `REVISION` file (`el_p16` has none; P16 Amendment 1 records its commit, `d51b60f`). Data and splits are checked identical across machines (md5).
5. **Queue.** Runs go into a GPU queue on one machine: at most 3 runs per GPU, only on a GPU with < 1,000 MiB used (so never on another user's GPU), queues chained rather than run concurrently. Training is deterministic per machine, so packing runs on a GPU changes speed, not results (`protocols/P12_matched_5pct.md` "Scheduling").
6. **Train.** `scripts/train.py` with `configs/supervised.yaml` or `configs/ssl_mean_teacher.yaml` plus `--opts` overrides. All BenchmarkEL training runs from P6 on: 20,000 steps, batch 8 labelled (+ 8 unlabelled for SSL), Adam 1e-3, weight decay 1e-4, 200-step warm-up then cosine to 0, gradient clip 1, bf16 autocast (`protocols/P6_corrected_baseline.md`).
7. **Rescore.** `scripts/rescore_label_versions.py` (read-only) scores the final checkpoint (EMA teacher for Mean Teacher runs) on test (50 cells) and val (54) against both label versions. One JSON per run.
8. **Post-analysis.** A script per experiment (`scripts/post_ssl.sh pN <gpu> <n>`, `scripts/post_p15.sh`, `scripts/post_p16.sh`) pulls the JSONs, runs per-image scoring and histograms on cv02, applies the locked rules (`scripts/ssl_rules.py`), runs the image bootstrap and source split (`scripts/per_image_analysis.py`) and draws bars (`scripts/ssl_figure.py`). E1 per-cell scoring follows (`scripts_cv02/e1_task_metrics.py` v2, `scripts_cv02/e1_aggregate.py`).
9. **README.** `results/pN/README.md` states: runs and return codes, code commit, a results table, the locked verdicts, the robustness checks, secondary metrics, E1, and a "Reading" section clearly marked as interpretation.
10. **Summary to the user.** Results against their locked rules, then an evidence table (`to_human/results_2026-10-12.md`).

---

## 2. Protocol locking

**What "locked" means.** The protocol is committed before the first training run of that experiment. After that, the question, arms, primary metrics and rules do not change silently. The verdict is whatever the locked rule says, even if the result is disappointing or a different rule would look better.

**Why.** The old era produced several fake gains that came from choices made after seeing numbers: an 8× optimizer-step mismatch that produced a fake +7.4 gain; best-val checkpoint selection that flipped signs; metric conventions chosen after the fact (phase 0 handoff; phase 1 handoff section 13, "Corrections log"). Locking removes the freedom to pick the comparison that wins.

**What a protocol contains.** Lock date and time; "What I had seen when locking" (which results existed and whether any were opened); why the experiment exists; the code commit; what is fixed for all arms; the arms table (run names, seeds, machine); the metrics (primary and secondary); numbered decision rules; required robustness reporting; "Not claimed".

**Disclosed post-hoc choices.** When a question was chosen after seeing interim results, the protocol says so and notes that the choice applies equally to every arm. Examples:
- P8: the L3 base was chosen after P6's results, because P6's locked rule picked L0, which then had no label headroom (`protocols/P8_tolerant_pl_on_l3.md` "Why this exists").
- P9 and P10: questions chosen after interim P7/P8 numbers (`protocols/P9_external_pool.md`, `protocols/P10_ssl_5pct.md`).
- P11: motivated by P8's finding that the loss-off control D was below supervised (`protocols/P11_matched_pipeline.md`).

**Amendments.** A change after locking is written as a dated amendment that states what had been seen. Examples:
- P10 amendment: arm B5 added before any B5 run, no P10 result seen.
- P13 Amendment 1 (before any P13 run): 5% only, Ds5 dropped (the separate-forward λ = 0 student is bit-identical to supervised), 5 seeds for CsM5 and A5c, gaint arms dropped.
- P16 Amendment 1 (Part B, the SSL arms): locked after the user chose "Pick on P13 val"; 3 of 13 P13 runs had finished but none of their numbers was opened. CutMix on or off is decided automatically from P13 val numbers only (`scripts_cv02/p16b_auto.sh`).
- E1 amendment: after seeing first-pass extension numbers, four defect types missing from our taxonomy were marked ignore instead of background; disclosed, first pass kept in `raw/`.

**Confirmatory vs exploratory.** Locked rules give confirmatory verdicts. Anything else (P3, the P6 "Exploratory" sections, histogram diagnostics, E1 tables) is labelled exploratory or descriptive and never overrides a verdict.

---

## 3. Designing arms

**One change per arm.** Each arm differs from its comparison arm in exactly one setting. P6's ladder is the clearest case: L0 → L1 adds label-safe augmentation, L1 → L2 the ImageNet encoder, L2 → L3 the CE+Dice loss (`protocols/P6_corrected_baseline.md`).

**Loss-off control (the D arm).** To test whether an unlabelled loss helps, compare the SSL arm with an identical arm whose λ_final = 0: same forward pass, same augmentation, same data streams; only the loss's contribution is zero. Why it matters: in the old era Mean Teacher and ALHVR "beat" supervised, but their λ = 0 controls scored the same, so the gain came from batch composition, not the loss (phase 1 handoff section 9c). In P8, D itself sat below supervised A (crack IoU −0.013, CI [−0.028, −0.001]; inactive −0.101, CI [−0.171, −0.031]; `protocols/P11_matched_pipeline.md`), which showed the SSL pipeline handicapped the student before the loss did anything.

From P13 on, the separate BN forward makes the λ = 0 student bit-identical to the supervised run (verified on GPU, `results/p13_audit/smoke_gpu.log`). So the supervised arm A is also the loss-off control, and "the loss helps" and "SSL beats supervised" become one contrast (P13 Amendment 1; P16 Amendment 1).

**Step matching.** Every arm trains for the same number of optimizer steps: 20,000 in every experiment from P6 on (P1's overfit fits used 3,000 steps; P15's single UCF pretraining run used 59,760; `results/p1/README.md`, `protocols/P15_ucf_encoder_transfer.md`). An SSL loop that iterates over a large unlabelled set does many more steps per "epoch" than a supervised loop, so epochs are never matched.

**Final-step weights.** Every run is scored at its final step (20,000). The checkpoint with the best validation score is never used (section 7).

**Seeds.** The split seed is fixed at 0 for everything. Training seeds vary: 0-2 in P6 to P12, 0-4 for P13's primary arms and P16, 3-5 for gaint replications (fresh seeds, never pooled with cv02). The user's rule: at least 3 seeds per arm, and 5 to 8 when the expected effect is below 0.05. P8 to P12 used 3 seeds for effects of 0.01-0.02, which breaks that rule; this was acknowledged on 11 Oct and fixed from P13 on.

**Pooling seeds across experiments.** Allowed only when the configs are identical except seed (checked by diff) and the code path is unchanged: A5c pools P12 seeds 0-2 with P13 seeds 3-4 (both `smp_unetpp` supervised, same options); P16's A20 and A100 pool P6 seeds 0-2 with new seeds 3-4 (`protocols/P16_label_fraction_curve.md` Part A). The README checks the two halves agree (P13: P12 − P13 seeds n.d. on every primary).

**One machine per rule.** cv02 (8 × RTX A6000) and gaint (RTX PRO 4500) give different numbers for the same config. Arms in a locked rule all run on cv02. gaint runs are descriptive: they can replicate a cv02 result but never rescue a failed one. P12 measured the cross-machine offset with identical configs (gaint gA10 − cv02 L3 10%): crack IoU +0.004 (threshold 0.010), inactive IoU +0.056 (threshold 0.057), crack relF1@2 +0.006 (threshold 0.012), all n.d. Crack can be read across machines to within about 0.005; inactive cannot (`results/p12/README.md`).

---

## 4. Scoring

**What is scored.** The final-step checkpoint (EMA teacher for Mean Teacher runs, the model otherwise), on the 50 test cells, against the E-SCDD revised masks, at argmax. Val (54 cells) and old-label scores are computed and reported as secondary.

**How metrics evolved.**
| Period | Headline metric | Why it changed |
|---|---|---|
| Old era | defect mIoU = mean(crack IoU, inactive IoU), old labels | |
| P6, P7 | crack AP and inactive AP, revised labels | Threshold-free; chosen so recipes with different calibration compare fairly |
| P8 on | test crack IoU, inactive IoU, crack relF1@2 (argmax, revised labels) | AP turned out to be dominated by unrankable pixels: L3 at 10% puts 42% of GT crack and 65% of GT inactive below 0.001 probability (bin 0), tied with ≥ 98.5% of background (`results/p6/README.md`, exploratory 1). A pseudo-label loss can change that saturation without changing the segmentation, so P8 fixed argmax metrics as primary before any P8 run |

**Primary metrics (P8 on).** Test crack IoU, test inactive IoU, test crack relaxed F1@2. Pooled (dataset-level). See `04_glossary_and_naming.md` for definitions.

**Secondary metrics.** Crack and inactive AP with the bin-0 share; crack relaxed precision@2 (the width check); val; old-label scores; E1 per-cell metrics (from P13 on, labelled secondary).

---

## 5. The decision rule ("P8 rule 1", R1)

### The formula
An arm B is **detectably better** than arm A if, on at least one primary metric,

  Δ = mean(B) − mean(A) > max(0.01, 2 · √((sd_A² + sd_B²) / 3))

and no primary metric is **worse** by the same threshold (Δ < −threshold). Means and sds are over training seeds (sample sd). Code: `scripts/ssl_rules.py`, function `cmp`:
```python
thr = max(0.01, 2 * np.sqrt((sd(xa) ** 2 + sd(xb) ** 2) / 3))
return dl, thr, (1 if dl > thr else -1 if dl < -thr else 0)
```
Verdict words: BETTER, WORSE, n.d. (not detectable).

### Intuition
- With 3 seeds per arm, the standard error of a difference of two means is √(sd_A²/3 + sd_B²/3) = √((sd_A² + sd_B²)/3). So the threshold is **2 standard errors**: "the difference is about twice as large as the wobble you would expect from seeds alone".
- The 0.01 floor means a difference below 0.01 never counts, however consistent the seeds. When seeds agree closely the floor decides (e.g. P14 L3T − L3 crack IoU: sds 0.005 and 0.003 give 2 SE = 0.0067, so the threshold is the floor 0.0100; `results/p14/README.md`).
- "Any primary passes, none worse" means a method can win on one metric only if it does not lose detectably on another.

### How strict it really is
- **3 vs 3 seeds:** 2 SE is roughly a one-sided t-test at p ≈ 0.06 (t = 2 with about 4 degrees of freedom gives 0.058). A two-sided 95% test would need t ≈ 2.78. So R1 at 3 seeds is lenient. It was described to the user as lenient on 11 Oct.
- **5 vs 5 seeds:** the divisor stays 3 in the code, while the true standard error uses 5. The threshold is then about 2.58 SE (one-sided p ≈ 0.016 at about 8 degrees of freedom). So the primary contrasts of P13 and P16 face a stricter bar than P8 to P12.
- **5 vs 3 seeds** (e.g. P13 BsM5 vs A5c): about 2.24 SE with equal sds (one-sided p ≈ 0.03).
- No correction for multiple contrasts. Protocols name a primary claim and disclose the number of contrasts instead (P13: 1 primary + 5 secondary; P16: 3 primary).
- R1 measures **seed noise on a fixed test set**. It says nothing about whether the result would hold on other test cells. That is what the bootstrap is for (section 6).

### Worked example: P13 CsM5 − A5c (5 vs 5 seeds; `results/p13/README.md`, `results/p13/p13_rules.txt`)
| Metric | CsM5 mean ± sd | A5c mean ± sd | Δ | 2·√((sd_A²+sd_B²)/3) | Threshold | Verdict |
|---|---|---|---|---|---|---|
| inactive IoU | 0.370 ± 0.026 | 0.253 ± 0.037 | +0.117 | 2·√((0.037² + 0.026²)/3) ≈ 0.052 | 0.052 (code: 0.0518 from unrounded sds) | BETTER |
| crack relF1@2 | 0.752 ± 0.016 | 0.720 ± 0.014 | +0.033 | | 0.0245 | BETTER |
| crack IoU | 0.317 ± 0.011 | 0.304 ± 0.008 | +0.014 | 2·√((0.008² + 0.011²)/3) ≈ 0.016 | 0.0160 | n.d. |

Two primaries pass, none is worse, so the rule passes. The width check (relP@2 −0.019) is within 0.05. Robustness (reported, not part of the verdict): inactive bootstrap CI [+0.042, +0.189], +0.103 without the top-3 cells; relF1@2 CI [+0.006, +0.055].

A counter-example from P12 (`results/p12/p12_rules.txt`): Cm5 − A5c crack IoU +0.0056 against a threshold of 0.0144: n.d.; the rule fails on all three primaries.

---

## 6. The rule list (R1 to R8) and experiment-specific rules

### R1 to R8, as given to the user on 11 Oct
This numbering was used in the assistant's answer of 11 Oct ~17:30 IST. Protocols number their rules per experiment; the mapping is given.
| # | Rule | In the protocols |
|---|---|---|
| R1 | "Detectably better": the formula in section 5, on ≥ 1 primary (test crack IoU, inactive IoU, crack relF1@2), none worse | "P8 rule 1"; every protocol from P8 on |
| R2 | "The loss helps": SSL arm vs its loss-off twin (same pipeline, λ = 0), under R1 | P8-P10 rule 1 (C − D); P11 rule 2 (Cm − Dm); P12 rule 2; P13 rule 2 |
| R3 | "SSL beats supervised": SSL arm vs the step-matched supervised arm under R1, credited only if R2 passes for that arm | P11 rule 3, P12 rule 3, P13 rule 3; from P13 on R2 and R3 are the same contrast |
| R4 | Width check: a crack relaxed-precision@2 drop > 0.05 (against the loss-off twin) is flagged as possible mask fattening | P7 rule 3, P8 rule 3, ... P13 rule 7; P14 builds it into the recovery rule |
| R5 | Gap closed: (X − A) / (L3@100% − A), descriptive | P8-P10 used (C − D) / (L3@100% − D); P11 rule 5 on |
| R6 | gaint replication is descriptive and can't rescue a cv02 failure; seeds are never pooled across machines | P12 rule 6 ("replicated" = same sign and at least half the size on each passing metric), P13 rule 9 |
| R7 | Image bootstrap plus leave-top-3-out are reported for every R2/R3 contrast; they never change the verdict | "Required robustness reporting" sections from P9 on |
| R8 | Protocol committed before runs; any amendment states what had been seen | Every protocol header |

**R3 "credited only if R2 passes", in practice.** P11 Cmx − A passed the R1 arithmetic on inactive (+0.061, threshold 0.049), but Cmx − Dmx failed R2 (inactive +0.054, threshold 0.072), so Cmx's "win" over supervised was not credited (`results/p11/README.md`). The reason: if the loss itself does not help, any gain over supervised comes from something else in the pipeline.

**R4 against which arm.** The protocols compare relP@2 with the matching loss-off arm. In P12 the script flagged Cmx5 − A5c (−0.056), but the protocol's check is against the matching loss-off arm, here Dmx5 (−0.044, within limits); the README discloses this (`results/p12/README.md`). From P13 on the loss-off arm is A.

### Experiment-specific rules
- **P6** (`protocols/P6_corrected_baseline.md`): rule 1, a ladder step helps if Δ crack AP or inactive AP > 0.01 and > 2·SE; rule 2, the base for the next experiment is the 10% arm with the best **val** mean of (crack AP + inactive AP)/2 (it picked L0); rule 3, SSL headroom = base@100% − base@10% on pooled val+test AP; if < 0.02, the next experiment is a pilot (L0: −0.001, so P7 became a pilot).
- **P7** rule 4: if P6 rule 3 found headroom < 0.02, all P7 outcomes are a pilot.
- **P7/P8 rule 2:** "C beats B" (tolerant vs hard pseudo-labels) under the same rule. If C helps but does not beat B, the claim reduces to "a correct pseudo-label loss helps", not "tolerance helps".
- **P9 rule 5, P10 rule 4:** pool-size and label-budget interactions: (Cx − Dx) − (C − D), (C5 − D5) vs (C − D) at 10%; secondary.
- **P11/P12 rule 1:** pipeline check Dm − A, descriptive.
- **P12 rule 7:** cross-machine calibration gA10 − L3 10%, descriptive.
- **P13:** primary claim CsM5 − A5c, 5 vs 5 seeds; secondary BsM5 − A5c, Cs5 − A5c, CsM5 − Cs5 (CutMix), CsM5 − BsM5 (tolerant vs hard), Cs5 − Cm5 (separate vs joint BN, descriptive); collapse watch on rare_frac at steps 4,000 and 20,000.
- **P14** (`protocols/P14_tolerant_supervision.md`): rule 1, the label-noise gap G = L3 − L3o exists on a metric if it passes R1 arithmetic; rule 2, tolerance "recovers" label noise if L3To − L3o passes R1 arithmetic **and** is ≥ 0.5·G **and** the relP@2 drop vs L3o is ≤ 0.05; rule 3, L3T − L3 under R1 plus the width check.
- **P15** (`protocols/P15_ucf_encoder_transfer.md`): U − reference (gaint, same seeds and options, ImageNet encoder) under R1 plus the width check; gap closed against cv02's L3@100% is cross-machine and descriptive.
- **P16** (`protocols/P16_label_fraction_curve.md`): S20 − A20, S50 − A50, Sx100 − A100, each under R1, 5 vs 5 seeds, all three reported. CutMix on/off chosen from P13 **val** numbers only (score = mean over the three val primaries of the seed means; on if CsM5 > Cs5). Result: CsM5 0.3507 vs Cs5 0.3652, so CutMix is off (cv02 `el_p16/reports/p16b/selection.txt`, `CUTMIX=0`; rounded to 0.351 and 0.365 in `results/p13/README.md` "Secondary").

---

## 7. The user's standing rules

These come from the phase 1 handoff (section 16) and are recorded in memory (`mtp-el-ssl-project.md`). Each one exists because breaking it once produced a fake result.
| Rule | Origin |
|---|---|
| Match optimizer steps across arms | An 8× step mismatch produced a fake +7.4 gain (phase 0 handoff) |
| Final-step weights are primary; best-val only secondary and flagged | Val has 54 images; best-val selection flipped the sign of several comparisons (`~/mtp/MTP_session_handoff_2026-10-07.md` line 178) |
| Never compare arms across machines | cv02 and gaint differ; seeds on one machine are not exchangeable with the other (phase 1 handoff sections 0, 16) |
| At least 3 seeds per arm; 5-8 for effects < 0.05 | At 95 labelled images seed noise was ±0.03-0.04 defect mIoU (phase 1 handoff section 2) |
| One change per arm | Needed to attribute any difference |
| Old-era numbers (original masks, from-scratch U-Net++, weighted CE, batch 4) in separate tables from the P-series | Different labels, recipe and code; pilot-era coupled-augmentation numbers are not comparable either (phase 1 handoff section 8, item 7) |
| SemiCE results are invalid | P2: SemiCE's positive sets are incoherent (100% of pixels have ≥ 2 positives) and its gradient is nearly orthogonal to the supervised one (cosine 0.07) (`results/p2/README.md`) |

Also from the phase 1 handoff (section 16): report the standard metric as headline (the PV-S3 and Pratt metrics only when comparing with those papers, always labelled); never select checkpoints on test; bf16, GaussNoise via `std_range` only, paired geometric augmentation, strong augmentation photometric only.

And working rules from memory (`ask-before-assuming.md`): batch open questions and ask the user rather than act on an assumption; hold launches while questions are open; "framing depends on final results, no presumptions, ever" (user, 11 Oct).

---

## 8. The robustness layer

R1 only asks "is the difference bigger than seed noise on these 50 test cells?". Four checks ask whether it depends on which cells were tested. They are reported for every R2/R3 contrast and never change a verdict.

**Paired image bootstrap.** `scripts/per_image_analysis.py`: per-image argmax counts (TP, FP, FN per class) come from `per_image_scores.py`; summed, they reproduce the re-score IoU exactly (the README prints "sanity: max |summed per-image IoU − re-score IoU| = 0"). The script resamples the 50 test cells with replacement 2,000 times (generator seed 0). For each resample it recomputes pooled IoU per seed from the resampled counts, averages over the arm's seeds, and takes the difference between arms using the same resample for both (paired). Output: the 95% percentile CI and P(Δ>0), the share of resamples with a positive difference.

**Leave-top-3-out.** The same difference after dropping the 3 test cells with the most ground-truth pixels of that class. In test, the top 3 cells hold 32% of crack pixels and 59% of inactive pixels. A result that vanishes without them rests on 3 cells. Example: P6's "inactive puzzle" (L1 at 10% beating L3 at 100% on inactive IoU) flips sign without the top 3 (−0.044 → +0.088), so it is not a finding (`results/p6/README.md`, exploratory 5).

**Source split (from P9).** BenchmarkEL cells come from five sources. The external pool is 77% CSIR and 23% ARTS, with no CFVS, BMRK or SDLE. So contrasts are also reported separately on the 21 CSIR + ARTS test cells and the 29 CFVS + BMRK + SDLE cells (test composition: 18 CFVS, 13 ARTS, 10 BMRK, 8 CSIR, 1 SDLE; `protocols/P9_external_pool.md`). Descriptive. In the CSIR/ARTS group all inactive pixels sit in 3 cells, so its inactive numbers are uninformative (`results/p13/README.md`).

**E1 per-cell metrics** (`results/e1/README.md`; definitions fixed before any E1 number). Prediction is argmax at final weights (teacher for Mean Teacher runs). Two cell sets: the 50 test cells and the 106-cell extension from unseen modules.
| Metric | Definition | Cells |
|---|---|---|
| crack tolF1@2 | 2PR/(P+R); P = share of predicted crack px within 2 px of GT crack; R = share of GT crack px within 2 px of predicted crack; 0 if nothing predicted | GT crack ≥ 20 px; mean |
| crack length error | \|L_pred − L_gt\| / L_gt, L = skeleton pixel count | same; median |
| crack false alarm | share of cells with predicted crack ≥ 50 px | GT crack < 20 px |
| inactive area error | \|a_pred − a_gt\| in percentage points of non-padding area | all; mean |
| inactive detection F1 | positive if area ≥ 0.5% | all |
| inactive cell IoU | per-cell IoU | GT inactive ≥ 0.5%; mean |

Contrasts get the same paired bootstrap (2,000 resamples) and leave-top-3-out (`scripts_cv02/e1_aggregate.py`). E1's verdict on itself, over 23 contrasts: crack per-cell metrics are not more sensitive than pooled crack IoU or relF1@2 on test (CI excludes 0 in 8 contrasts for tolF1 vs 13 for pooled IoU), so pooled metrics stay primary; inactive cell IoU is more sensitive than pooled inactive IoU (test 9 vs 7; extension 17 vs 10). Crack false alarm is useless on test but the most sensitive crack metric on the extension. E1 enters P13 to P16 only as labelled secondary metrics.

**How to read the robustness columns together.**
- Seed rule passes, CI excludes 0, survives top-3 removal: strongest result available here (e.g. P13 CsM5 − A5c inactive).
- Seed rule passes, CI includes 0: the seeds agree but the effect depends on which cells are tested (e.g. P14 L3T − L3 inactive +0.037, CI [−0.016, +0.093]).
- Seed rule n.d., CI excludes 0: consistent over cells but too small for the seed rule (e.g. P13 CsM5 − Cs5 crack +0.010, CI [+0.004, +0.017]).

---

## 9. Why val is not used for selection

- Val has 54 cells. Only 6 contain inactive, and 3 of those hold 89% of val's inactive pixels (test: 16 of 50, top 3 hold 59%) (`results/p6/README.md`, exploratory 4).
- In the old era, picking best-val checkpoints flipped the sign of several comparisons.
- In P13, val and test disagree on inactive: val inactive IoU A5c 0.106, Cs5 0.098, CsM5 0.081, BsM5 0.061, while on test every SSL seed beats every supervised seed (`results/p13/README.md`).
- Val is still used in two places by decision: P6 rule 2 (base recipe, which picked L0) and P16 Part B (CutMix on/off, the user's choice "Pick on P13 val"). Val also informed P6's base choice, which is why E1 does not use val.

---

## 10. What these statistics cannot tell us

- **One split.** Every result is on split seed 0. A different train/test partition could change conclusions; this was never tested.
- **50 test cells.** On the revised masks crack appears in 48 of them (50 on the old masks); inactive in 16 (17 on the old masks), and 3 cells hold 59% of inactive pixels. Inactive results are fragile by construction.
- **Seed noise vs generalisation.** R1 measures training noise on a fixed set of cells (`results/p6/README.md` exploratory 5 says this about its own inactive verdicts).
- **Unseen modules.** The 106-cell extension shows every model loses most of its crack performance on modules it never saw: L3 100% crack IoU 0.471 on test vs 0.152 on the extension (`results/e1/README.md`). In-split numbers do not describe deployment on new modules.
- **Label quality.** Old vs revised labels move crack IoU by +0.05 to +0.07 for every model (P3), larger than any SSL effect measured; P14 measured a +0.082 crack IoU gap between training on old and revised labels at 10%.
- **Tuning.** No SSL hyperparameter (λ, t_pos, R, CutMix probability) was ever tuned. Results say "this recipe", not "SSL".
- **Low label counts.** At 5% and 10% labels only 2 and 4 labelled cells contain inactive (`protocols/P16_label_fraction_curve.md`).

---

## 11. The critique of the design (given to the user on 11 Oct)

The user asked (11 Oct, 17:24 IST): "can you for once tell me all the locked rules, i things we self sabotaging our project in a way..." (`sources/chat/user_messages_2026-10-07_to_11.md`). The answer (transcript line 6728): the rules, no; the design, yes.

**The rules are lenient.** R1 at 3 seeds is about one-sided p ≈ 0.06. They credited SSL whenever a gain was there: P11 passed R2 and R3; P12 passed R2. At 5% on cv02, SSL vs supervised was +0.006 crack IoU against a seed sd of 0.007-0.010, which "would pass only at a 1-SE bar (p ≈ 0.2)". Check of that arithmetic: 1 SE = √((0.007² + 0.010²)/3) ≈ 0.007, so +0.0056 is about 0.8 SE and would not pass even at 1 SE (`results/p12/README.md`). The one positive result the rules excluded was gaint's 5% "SSL beats supervised" (R6), where SSL seeds 3-5 differ from supervised seeds 0-2 and cv02 disagrees; P13 was set up to settle it with 5 seeds.

**Where the design hurt:**
1. **Regime.** SSL was tested at 5-10% labels, where inactive is in only 2-4 labelled cells and the teacher is weakest. P16 (20/50/100%) was added in response.
2. **A handicap built into every SSL arm until P13.** Shared BatchNorm between labelled and unlabelled images cost −0.007 crack IoU at 10% and −0.017 at 5% before the loss did anything. P13's separate forward removes it.
3. **3 seeds for effects of 0.01-0.02**, which breaks the user's own ≥ 5 rule. Fixed from P13 on.
4. **Tuning asymmetry.** The supervised recipe (L3) came from a 4-step ladder; SSL's λ, thresholds and R were fixed up front and never tuned.
5. **Small in-domain pool and a mismatched external pool.** The in-domain pool is 239-455 cells; the 11,938-cell external pool comes from 2 sources (CSIR, ARTS) and never helped (its one seed-rule pass, P9 Cx − Dx inactive +0.056 against 0.046, was not robust over cells; `results/p9/README.md`).

What followed: P13 (separate BN + CutMix, 5 vs 5 seeds) passed its primary claim (inactive +0.117, relF1@2 +0.033; crack IoU n.d.). P16 tests 20%, 50% and 100%. See `10_experiments_P13_P16_E1.md` and `11_results_synthesis_and_claims.md`.

---

## 12. Checklist for reading any results README

1. Which protocol, locked when, and what had been seen? Any amendments?
2. Which machine, which code commit, how many seeds, all rc = 0?
3. Which contrast is primary? How many contrasts in total?
4. For each contrast: Δ and threshold per primary metric; does any primary pass; is any worse?
5. For SSL claims: did R2 (loss helps) pass before R3 (beats supervised) was credited?
6. Width check: relP@2 drop ≤ 0.05?
7. Robustness: bootstrap CI, leave-top-3-out, source split. Is the inactive result carried by 3 cells?
8. Is the "Reading" section interpretation (allowed to be wrong) or a verdict?
9. Are any numbers from another machine, the old era, or val? Keep them apart.

---

## Related docs
- `00_START_HERE.md`, `01_project_overview_and_scope.md`
- `03_datasets_and_splits.md` (splits, label fractions, sources)
- `04_glossary_and_naming.md` (metric and arm definitions)
- `06_history_phase0_phase1.md` (where the standing rules came from)
- `08_experiments_P1_P7_diagnostics.md`, `09_experiments_P8_P12_ssl_series.md`, `10_experiments_P13_P16_E1.md` (the rules applied)
- `11_results_synthesis_and_claims.md`, `12_decisions_log.md`, `13_problems_pitfalls_open_issues.md`
- `14_code_and_infrastructure.md` (scripts, queues, machines)
- `15_status_remaining_work.md`, `16_faq_for_the_guide.md`
