# T9 pre-registration: per-panel AdaBN on Hanifi `_rf` panels (idea 9; found, 31 Oct 2026)

Written before any T9 outcome number exists. The only numbers below are set composition and the image gates (§2), which contain no model output.
- Approval: judge (CPU-only, descriptive; team-lead 31 Oct).
- Runs on gaint CPU: `CUDA_VISIBLE_DEVICES=""`, nice 19, ≤ 8 threads, outside runner's critical windows, after checking the PF2 data-loader load.
- **E1 and test are not read.**
- Tags: E measured (file), R literature (Research MCP id), S judgement.

## 0. What T9 can and cannot show (judge condition 1)
- **Descriptive by construction.** Per-panel BN cannot be evaluated on E1: 1 of 71 E1 modules has pool siblings (`idea09_tta.md` §3). Test is in-family.
- A pass means "worth a deployment note and a place in the final candidate's inference pipeline, decided on `_rf` evidence". It is not a claim, and it cannot change BEST.
- A fail closes TTA for this thesis (idea 9 kill).

## 1. Question
Does re-estimating BN statistics per panel, from that panel's own unlabelled cells, improve crack ranking on panels the model never saw, without raising false alarms? Here ranking means AP over the crack-bias grid, threshold-free.

## 2. Sets and image gates (E, done before writing the rule)
**Scripts (gaint CPU, read-only):**
- `found_scripts/t9_sets.py` md5 6dd2e427 → `t9_sets.txt` 156b532a;
- `t9_identity.py` 01ae6650 → `t9_identity.txt` dffd85d1;
- `t9_align.py` ce76abe8 → `t9_align.txt` 327dd5df.

**Source data:**
- calib's `_rf` set: gaint `/home/noob/work/calib/data/rf`, 106 cells after hygiene; masks remapped 25-28 → ignore, 29 → 1, 24 → 2; context `rf_context.tsv`.
- Pool images: `el-fault-detection/data/unlabeled/images_512` (11,938).

**Sets.** "Eligible" = the cell has a pool copy and its module has ≥ 20 pool cells.

| Set | Definition | Cells (eligible) | Crack cells ≥ 20 px (eligible) | Crack px (eligible) | Modules (eligible; with crack) |
|---|---|---|---|---|---|
| **P = F51-eligible** | full cells from modules not in train | 51 (36) | 12 (8) | 14,639 (14,373) | 36 (24; 8) |
| **H36** | half-cut cells, all unseen-module | 36 (36) | 17 (17) | 1,792 | 7 (7; 7), 144 pool cells each |
| **F19-eligible** | full cells from train modules (in-family) | 19 (16) | 9 (9) | 6,811 | 14 (12; 7) |

**Gate 1, identity (judge condition 3).**
- 91 of the 106 `_rf` cells have a pool copy. **0 of 91 are byte-identical.**
- Mean |Δ| median 0.90 grey levels (max 5.1). Pearson r median 0.998 (min 0.984). Mean and sd agree within 0.2 GL.
- So E-SCDD's `_rf` images and our pool conversions differ by resampling, not by global intensity.
- **Consequence:** every T9 variant, V0 included, scores the pool copy of each `_rf` cell. The scored image and the BN siblings then share one preprocessing.
- E-SCDD-image V0 is reported once as a sensitivity row. calib's existing dumps are on E-SCDD images, so they are not reused as V0.

**Gate 2, alignment.** Phase correlation gives a zero integer shift for all 91 pool copies vs the `_rf` images (`t9_align.txt`). So the `_rf` masks and ignore maps score the pool copies directly.

**Why P decides and H36 does not (S, from calib E).**
- calib's idea 1 shows FINAL reaches relR@2 0.036 on H36 crack, and 84% of H36 GT crack is unreached even at b +12 (`idea01_calibration.md` §1.1, §2 A3).
- domain finds H36 crack GT is "tiny edge marks" (`log.md` 14:14).
- H36 crack AP is therefore near zero for any variant, and a gain on it is uninterpretable. That changes judge's condition 2, which assumed H36 decides, and needs judge's OK.
- H36 is kept for the precision side, which is BN-HC's failure mode: false-alarm px on its crack-free cells.
- Judge accepted this. Its own check: 48% of H36's 1,792 crack px lie within 10 px of spacing, border or the half-cut line.
- **Disclosure (judge):** the set choice was made after seeing the source model's (V0) H36 recall in calib's idea-1 dumps. No T9 variant output had been seen. That is direction-neutral between variants.
- **A1:** T9 does **not** test the half-cut + scuff context that motivates idea 9. P is full cells from unseen CSIR modules, a mild panel shift.

## 3. Models and variants
**Models**, as two separate families with no mixing:
- FINAL: the 5 cv02 members as D used, gaint `cv02_noob_el` copies;
- SUPPF5: `f3_SUPPF_100pct_s0-4`, e544133.
- Each member is adapted separately; then the mean softmax is taken.

**Variants** (TENT / V4 dropped: judge and team-lead):
- **V0** source (the trained BN statistics).
- **V1** BN-HC as D: all BN from the 986 pool half-cells, applied to H36 only. This links T9 to D; it is not in the rule.
- **V2 per-panel BN:** for each module, a fresh copy of the member.
  - All BN running statistics are reset and re-estimated by cumulative average (momentum None), in train mode, no grad, batch 8, over **all** pool cells of that module, the scored cell's own pool copy included. This is label-free and realistic: a deployed panel is imaged whole.
  - Then that module's `_rf` cells are scored.
  - Code: D's `bn_reestimate`, grouped by module.
- **V3 per-panel BN, shallow:** as V2, but only the encoder's `bn1`, `layer1.*` and `layer2.*` BN layers take the panel statistics. All deeper encoder BN and every decoder BN keep the source statistics.
  - The shallow statistics depend only on shallow layers, so V3 is cut from the same pass as V2.

## 4. Scoring (shared harness with calib, judge condition 4)
- **Dumps:** in calib's npz format (`calib_dump.py` v2 068ffa78: stems, margin, oth, pc). Written by `ideas/scripts/t9_dump.py` = calib_dump's load / x_of / maps / cells, plus the BN modes and the pool-copy image source. calib's files are not edited.
  - Outputs: `/home/noob/work/found/t9/dump/{FINAL,SUPPF5}__bn{V0,V1,V2,V3}.rf.npz`.
- **Records:** calib's `el_metrics.py` (46b682cc or calib's current version, md5 recorded at run time) `records --set rf`. That is per-cell counts over the bias grid b ∈ [−4, +12] (step 0.1, plus 0.75), relaxed counts, components and the cell flag score s20.
- **Crack AP:** step-wise AP over the grid's PR points (pooled pixel tp / pred / gt per b), on the cells of a set.
  - The same function is used for every variant. Pixels with margin < −4 count as never predicted for every variant alike.
- **Fixed operating point (no labels; judge condition 5):**
  - FINAL at its deployed b = +0.75;
  - SUPPF5 at its val-chosen OP-rel b from calib's V0 val records (A0).
  - Both are fixed before T9 and never re-chosen per variant or on `_rf`. b = 0 is also reported.
  - calib's label-free per-module quantile rules failed in idea 1, so they are not used.

- **Code fixed before outcomes** (laptop copies in `ideas/scripts/`; deployed to gaint `/home/noob/work/found/t9/`):
  - `t9_dump.py` md5 ae888904;
  - `t9_score.py` md5 974ef93f (applies §5 with A2 / A3 exactly: AP on [0, R_common] from the grid's PR points; uninformative flag if R_common < 0.5 on P; FA bound max(1.5×V0, V0 + 200)).
    - Synthetic end-to-end test: a pure margin shift gives ΔAP 0.000 and fails the FA term; a real separation gain passes.
  - any later change gets a new md5 in `log.md` before any outcome number.

## 5. Pass rule (fixed now; amended with judge's A1-A3 before any outcome; applied to V2 and V3 separately, each must hold for BOTH families)
**AP used in the rule (A2): AP over a common recall range.**
- For each V vs V0 comparison, on each set of cells it is computed on (the whole set, each bootstrap resample, each module):
  - R_common = min(max recall V reaches, max recall V0 reaches) within the bias grid b ∈ [−4, +12];
  - AP = the area under the step-wise PR curve from recall 0 to R_common, not normalised. The last step is clipped at R_common.
- This stops a margin shift (higher max recall inside the grid) from scoring as better ranking.
- Each variant's max recall on P is reported. **If R_common < 0.5 on P, the T9 result is "uninformative"**, neither a pass nor a fail.

1. **P crack AP:** V − V0 ≥ +0.03.
2. **Module-cluster bootstrap on P** (2,000 resamples over P's 24 eligible modules, seed 0; R_common per resample): lower 95% bound of the AP gain > 0.
3. **Per-module sign count on P:** AP (R_common per module) up in ≥ 7 of the 8 crack-bearing modules.
4. **False alarms at the fixed OP (A3):** predicted crack px on crack-free cells (0 GT crack px in keep) ≤ max(1.5 × V0, V0 + 200 px). Separately on H36 (19 crack-free cells) and on P's 26 crack-free cells; per-cell counts reported.
5. **In-family must-not-hurt:** F19-eligible crack AP ≥ V0 − 0.01.

**Reported beside the rule, not in it:**
- H36 crack AP and cell AUROC (s20), with the weak-label caveat;
- relR@2, relP@2, component R / P and cell flags at the fixed OP and at b = 0;
- inactive IoU and AP on the few inactive cells (H36 3, P 4; descriptive only);
- V1 on H36;
- the E-SCDD-image V0 sensitivity row;
- per-module tables.
- **Val** is not adapted: only 3 val cells sit in modules with ≥ 20 pool siblings. It is therefore unchanged by design and not reported as a T9 readout.

**Outcome wording:**
- All 5 hold for V2 or V3 (and R_common ≥ 0.5): "per-panel BN improves crack ranking on unseen **full-cell** panels (`_rf`, descriptive)", plus a deployment note. It says nothing about half-cut panels (A1). Inclusion in a final candidate is decided on val + `_rf` with coach.
- Otherwise: "no evidence for per-panel BN", and TTA is closed.
- Power stated now (S): P has 8 crack modules, so a +0.03 AP gain with a bootstrap lower bound > 0 is a high bar. P(pass) ≈ 0.2.

## 6. Cost and operations
- **CPU only.** BN passes over sibling images (E, `t9_sets` logic): H36 1,008, P 1,558, F19 730, so 3,296 images × 5 members per family.
  - At D's measured rate (986 × 5 in 2,013 s at 16 threads; `d_checks/d.log`), ~2.5-3 h per family at 8 threads, so **~5-6 h for both**. Dumps and records add ~0.5 h.
- **Disk:** dumps ~25 MB per variant per family on gaint `/home/noob/work/found/t9/`. Only the summaries come to the laptop.
- **Code:** `t9_dump.py` (~0.5 day). Self-check before any T9 number: `--bn none` on the E-SCDD images must reproduce calib's `FINAL.rf.npz` margins (max |Δ| ≤ 1e-2, float16).
- **Process:** tmux `t9` on gaint; PID recorded in `log.md`; stopped only by that PID.

## 7. Not done
- No E1 or test.
- No bias chosen on `_rf`.
- No TENT.
- No change to any training run.
- No download.

---

## judge review (31 Oct 2026, 14:23 IST per log.md; prereg md5 2f3a5834 as reviewed)

**APPROVED, subject to amendments A1 to A3.** Write them into §4 and §5 before any T9 outcome number. After that, T9 may run on gaint CPU as stated in §6.

**The deviation (P decides, not H36): accepted.**
- E: calib (`idea01_calibration.md` §1.1: FINAL relR@2 0.036 on `_rf` half-cut, 84% unreached at b +12) and domain (log 14:14: 1/17 cells) agree.
- My own check on the local E-SCDD masks: the 17 H36 crack cells hold 1,792 px; 48% of them lie within 10 px of spacing, border or the half-cut line (23% within 5 px).
- So H36 crack GT is mostly small edge marks plus SAM specks. Any AP gain on it would be uninterpretable.
- **Disclosure line for §2:** the set choice was made after seeing the source model's (V0's) H36 recall in calib's idea-1 dumps, not any T9 variant output. That is direction-neutral between variants.

**Amendments:**
- **A1, scope wording.** P is full cells from unseen CSIR modules: a mild panel shift, not the half-cut + scuff failure that motivates idea 9. In §5's pass wording, write "improves crack ranking on unseen **full-cell** panels (`_rf`, descriptive)". Add one line that T9 does not test the half-cut context.
- **A2, AP over a common recall range.** AP is built from the bias grid b ∈ [−4, +12], with margin < −4 never predicted. A variant that shifts margins (V2 does: BN-HC's E §2) reaches a different maximum recall inside the grid, so a truncated step-wise AP partly measures calibration again. Fix now:
  - report each variant's maximum recall reached on P;
  - compute the rule's AP on [0, R_common], where R_common is the minimum of the two maxima for each V vs V0 pair;
  - if R_common < 0.5 on P, say so and treat the result as uninformative, not as a fail or pass.
- **A3, false-alarm floor.** If V0's crack px on crack-free cells is small, "≤ 1.5× V0" is degenerate: 0 → 0, and 40 px → 60 px. Use ≤ max(1.5 × V0, V0 + 200 px) per set (H36 19 cells; P 26 cells), fixed now. Report the per-cell counts.

**Checked (E):**
- `t9_sets.txt`: P 36 eligible cells / 24 modules / 8 crack modules / 14,373 crack px; H36 36 / 7 / 17 crack cells; F19-eligible 16 / 12. These match my recount of the unfiltered sets (51 / 36 / 19, idea08 verdict).
- `t9_identity.txt`: 0/91 byte-identical; worst r 0.984, mean |d| ≤ 4.84 GL, equal means.
  - Scoring the pool copies for every variant, V0 included, removes the preprocessing confound I raised. The E-SCDD V0 sensitivity row is right.
- Self-check (`--bn none` reproduces calib's margins ≤ 1e-2) before any number: required, as written.

**Cross-impact (sent to found and coach):**
- idea 8 v2's probe and screen rules use H36 crack AP as their deciding term. By the same evidence that term is uninformative. Move them to F51 (or P) as the deciding set, with H36 for false alarms only.
- The same applies to any idea that planned to validate half-cut crack on the Hanifi half-cells (idea 5).
- **There is no usable labelled half-cut crack set outside E1.**


---

## RESULT (E; run 31 Oct 14:27-21:13 IST on gaint CPU, rc 0; awaiting judge's recompute)
**Files** (gaint `/home/noob/work/found/t9/`):
- `t9_result.json` md5 728bdbfb (local `found_scripts/t9_out/`), log `t9.log`;
- records `rec/*.json` (e.g. FINAL__V0 bb94ae3a, FINAL__V2 d56eaca9, FINAL__V3 5acebe6a, SUPPF5__V0 709e6f79, SUPPF5__V2 d5767434, SUPPF5__V3 dba6d9c2, SUPPF5.val f7f427d7);
- dumps `dump/`;
- self-check: v0 on the E-SCDD images = calib's FINAL.rf.npz, max |Δmargin| 0.

**Verdict: no variant passes for either family.** All comparisons are informative (R_common 0.87-0.92 ≥ 0.5). **Per-panel BN: no evidence of improved crack ranking on unseen full-cell panels (`_rf`, descriptive). TTA is closed (idea 9 kill).**

| Family (fixed OP b) | Variant | P crack AP on [0, R_common] | ΔAP vs V0 | module-bootstrap lo95 | sign (8 crack modules) | crack-free FA px, H36 / P | F19 ΔAP |
|---|---|---|---|---|---|---|---|
| FINAL (+0.75) | V0 | 0.603 (full-range AP) | | | | 580 / 763 | |
| | V2 per-panel, all BN | | +0.010 | −0.020 | 4/8 | **1,769** / 955 | −0.016 |
| | V3 per-panel, shallow | | +0.015 | −0.004 | 5/8 | 427 / 440 | +0.053 |
| SUPPF5 (+1.4, val OP-rel) | V0 | 0.567 | | | | 31 / 154 | |
| | V2 | | 0.000 | −0.085 | 3/8 | **2,214 / 2,665** | +0.141 |
| | V3 | | +0.016 | −0.058 | 4/8 | 319 / 117 | +0.066 |

**Failed terms:**
- FINAL V2: 1, 2, 3, 4a, 5.
- FINAL V3: 1, 2, 3 (it passes the FA and F19 terms).
- SUPPF5 V2: 1, 2, 3, 4a, 4b.
- SUPPF5 V3: 1, 2, 3, 4a (H36 FA 31 → 319 > bound 231).

**Descriptive (not in the rule):**
- V1 (BN-HC as D) on H36 raises false alarms again: FINAL 580 → 1,810, SUPPF5 31 → 2,204. This reproduces D's precision failure on a non-E1 set.
- E-SCDD-image vs pool-copy V0, P crack AP: FINAL 0.599 vs 0.603, SUPPF5 0.553 vs 0.567. The preprocessing gap is small next to any variant effect.
- H36 crack AP stays ~0.01-0.02 for every variant (labels unusable, as pre-stated).
- Per-panel BN with all layers (V2) is the BN-HC failure in per-panel form: it multiplies false alarms on crack-free cells (×3 to ×70). The shallow version (V3) leaves false alarms flat or lower and gives a small, non-significant AP gain (+0.015-0.016, 4-5 of 8 modules up).
- F19 (in-family, 16 cells, 7 crack modules) moves a lot for SUPPF5 (V2 +0.141). That is a small-set swing in the must-not-hurt direction; it is not a claim.

**Reading (S):**
- Panel-level BN statistics do not carry a usable unseen-panel signal for crack ranking on these panels.
- Re-normalising deep or decoder BN shifts calibration toward false crack (as BN-HC on E1).
- Shallow-only re-normalisation is harmless at best.
- Consistent with idea 9 §2 and the 27 Oct reading: the E1 failure is missing context, not a covariate shift BN can undo.
- **TTA (BN and entropy) is closed for this thesis.** The negative is reportable with D.

## judge verdict on the T9 result (31 Oct 2026, 21:16 IST from date; t9_result.json md5 728bdbfb)

**No variant passes, for either family. TTA is CLOSED. Confirmed.**

**Reproduced** with my own code on found's per-cell records (`judge/t9_recompute.py`, md5 0bf0524d, gaint CPU):
- P = 36 cells / 24 modules;
- pixel AP on [0, R_common];
- false alarms at each family's fixed OP (FINAL +0.75; SUPPF5 1.4, its val-chosen b).

| Family | Variant | R_common | ΔAP on P | H36 FA px | P FA px |
|---|---|---|---|---|---|
| FINAL | V2 | 0.92 | +0.010 | 580 → 1,769 | 763 → 955 |
| FINAL | V3 | 0.92 | +0.015 | 580 → 427 | 763 → 440 |
| SUPPF5 | V2 | 0.88 | −0.000 | 31 → 2,214 | 154 → 2,665 |
| SUPPF5 | V3 | 0.87 | +0.016 | 31 → 319 | 154 → 117 |

- ΔAP and the FA counts are **exact**.
- My sign count uses crack modules with any GT crack (10); found's pre-registered count uses crack-bearing modules (8). FINAL V2 5/10, V3 6/10; SUPPF5 3/10, 4/10. Same conclusion: well below the 7/8 bar.
- Every variant fails term 1 (+0.03) on its own; the bootstrap and sign terms fail too.
- All comparisons are informative (R_common ≥ 0.87 > 0.5).

**Reading (S):**
- Per-panel BN statistics do not improve crack ranking on unseen full-cell panels. Full re-estimation (V2) multiplies false alarms on half-cuts (~3x FINAL, ~70x SUPPF5).
- The shallow variant (V3) is the safe form, but it is +0.015 at best, below the bar.
- Thesis line: "test-time BN adaptation, global (D BN-HC) or per panel (T9), does not improve unseen-panel crack ranking and raises false alarms. Entropy-minimisation TTA was not run, on literature and in-repo evidence (A13)."
