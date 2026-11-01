# Idea 10: AI-assisted labelling with SAM (found, 31 Oct 2026)

Om's idea 10:
- Regions (inactive, scuff): SAM masks, near-automatic.
- Cracks: model + SAM proposals with a human correcting them.
- Use: the 986 pool half-cells, and cleaning the 24 Hanifi half-cut crack cells.
- Warning: Hanifi's SAM crack labels are the noisy ones.

The user prefers to avoid manual labelling. Tags: E measured (file), R literature (Research MCP id), S judgement. CPU / read-only; no GPU, no download, no test cell read.

**Files (md5):** `found_scripts/label_geometry.py` 2def1a96, output `label_geometry.txt` bf04f3b8 (local `~/mtp/datasets/escdd_full`). SAM data-engine times from arxiv:2304.02643 §4 (full text read).

**v2, 31 Oct 14:29 IST (log.md) (judge REVISE on the regions half):** v2.1, 14:31 IST: the val 6-cell term is report-only, and the two comparisons (b) and (c) are disclosed (judge); stamps corrected to log.md times.
- S10 is now inactive-only, on Pratt-labelled references: the A50 out-of-fold set (22 inactive cells), with a cell bootstrap.
- The scuff half is PARKED until B3.
- The low downstream value is stated.
- Approvals are batched with idea 8.
- The Boxes2Pixels wording is fixed.
- The crack half (SAM DROP, trust-region PARK) and the human-time figures were accepted.

**Verdict proposed: split.**
- **Inactive regions: PASS to a zero-human-time check (S10, §6),** an inference-only test of model-prompted SAM masks against Pratt labels on the A50 out-of-fold set. A pass is a method note; any training arm needs its own protocol and the user's OK, and its value is low (§6).
- **Scuff regions: PARKED** until B3 exists and a non-SAM scuff reference is defined.
- **Cracks: no fully automatic route.**
  - SAM on cracks: DROP (data and literature agree it fails on this kind of structure).
  - Model-proposal-assisted human correction is possible, but saves little where it matters: on half-cut + scuff cells the model finds 13-30% of the crack.
  - Automatic "trust-region" cleanup of the Hanifi crack labels: PARK. It cannot be validated without clean labels, and its precedent (R4) was n.d.
- **Any crack training-quality gain needs human time.** Minimal honest figures are in §5.

## 1. Premise check (E, `ideas/found_scripts/label_geometry.py` → `label_geometry.txt`)
Data: local E-SCDD (`~/mtp/datasets/escdd_full`, 30-class masks: crack 14, inactive 11, scuff 25). Two label sources:
- "Pratt" = 693 real non-`_rf` cells (BenchmarkEL 20221008 labels);
- "`_rf`" = 117 Hanifi cells, SAM-assisted (Roboflow Smart Polygon with SCDD-fine-tuned SAM, three-stage human review; `literature/notes/A09_hanifi2025_escdd.md`).

Per component (8-connected, ≥ 20 px): |ΔGL| = |mean inside − mean of a 3-8 px ring outside| in grey levels; thinness = skeleton px / area (1 = 1-px line); branch = share of components with a skeleton branch point.

| Source | Class | Components | \|ΔGL\| median (p25) | ΔGL / cell sd | thinness | with branch pt | area median (px) |
|---|---|---|---|---|---|---|---|
| Pratt | **crack** | 1,460 | **8.7** (4.3) | 0.39 | **0.37** | 0.34 | 130 |
| Pratt | inactive | 468 | 19.9 (5.4) | 0.69 | 0.14 | 0.48 | 262 |
| Pratt | scuff | 159 | 24.9 (18.8) | 1.07 | 0.12 | 0.37 | 335 |
| `_rf` | crack | 102 | 10.1 (4.0) | 0.67 | 0.36 | 0.29 | 85 |
| `_rf` | inactive | 26 | 27.2 (15.5) | 2.04 | 0.07 | 0.38 | 412 |
| `_rf` | scuff | 26 | 10.1 (4.2) | 0.92 | 0.16 | 0.19 | 180 |

- **Cracks are the SAM-unfriendly case.** Contrast is low (≈ 9 grey levels, under 0.4 of the cell's spread) and the structure is thin (thinness 0.37, about 2.7 px wide) and often branched.
  - These are exactly the factors under which SAM, SAM 2 and HQ-SAM fail, and "targeted fine-tuning fails to resolve this" (R doi:10.1109/wacv61042.2026.00505).
- **Inactive and scuff are friendlier:** 2-3× the contrast, blob- or streak-shaped.
  - A quarter of Pratt inactive regions are low contrast (p25 5.4 GL), so even regions will not all be automatic (S).
  - `_rf` scuff is lower contrast than Pratt scuff (10.1 vs 24.9 GL).
- **Hanifi's SAM-assisted crack labels are speckled (E):**
  - **75% of `_rf` crack components are < 5 px** (697 of 928), vs 4% in Pratt labels (64 of 1,645);
  - 9.4% of `_rf` crack px sit in components < 20 px, vs 0.4%;
  - one cell has 380 components (p90 31 per crack cell, vs 12).
  - This is after a three-stage human review: the SAM tool plus reviewers did not stop speckle.
- **What exists (E):**
  - **No SAM prompt decoder anywhere.** timm 1.0.30 on gaint has the SAM / SAM2 image encoders only. There is no `segment_anything` or `sam2` package (checked on gaint and the laptop `.venv`), and no SAM weights.
  - Interactive SAM labelling or prompted masks need a package install (team-lead OK) plus weights (user OK). S, from the public releases, confirm at download: SAM ViT-B checkpoint ~375 MB; SAM2.1 Hiera-T ~156 MB.
  - Roboflow's tool (Hanifi's) is a hosted service. Our images would leave the machine, which may not be acceptable for the data.

## 2. Prior tries in the repo (E)
- **Hanifi's SAM-assisted labels as training data: Track M R4.** 107 `_rf` cells including the 43 half-cuts, labels as released, scuff → ignore.
  - Test n.d.; E1 crack 0.148 → 0.146; E1 half-cut recall 0.133 → 0.123 (`trackM/results_r4.md`; vetter finding 2).
- **Fully automatic labels from our own model = pseudo-label SSL.** That is what P8-P17, BsM, CPS, ALHVR and SKCDF did.
  - Gains at 5% (crack +0.029, inactive +0.107); **n.d. at 20-100%** (handbook 18 §U; `team_2026-10-27_unlabelled/SYNTHESIS.md`).
  - Model-made masks for the pool, with or without a SAM refiner, are the same mechanism unless SAM adds information the model lacks.
- **27 Oct literature team:** "SAM-family pseudo-labels: not recommended" (`team_2026-10-27_unlabelled/lit.md` row 14 and §4 item 7).
- **B2 mining (model-based finder of scuff / crack half-cells):** against the 35 Hanifi pool half-cells, crack AUROC 0.62 [0.42, 0.81] and scuff 0.70 [0.49, 0.91] (vetter finding 3). Ranking is weakly above chance.
- **Family mismatch (vetter finding 4):** pool and Hanifi half-cells all come from CSIR 297-335 (8 modules); E1's half-cuts from CSIR 1621-2328. Labels on the pool half-cells, however made, are not E1's family.

## 3. Literature (R)
- **SAM data engine** (arxiv:2304.02643 §4): model-assisted annotation took 34 → 14 s per mask, "6.5× faster than mask annotation for COCO". Harder, less prominent objects went back up to 34 s per mask. These are natural-image objects with clear boundaries.
- **SAM-family limits on tree-like, low-contrast objects; fine-tuning does not fix it:** doi:10.1109/wacv61042.2026.00505.
- **Boxes2Pixels** (arxiv:2604.11162): human boxes → SAM pseudo-masks on industrial surfaces are "systematically noisy", "hallucinating background structure while missing sparse defects".
  - A noise-robust student (frozen DINOv2, one-sided self-correction) improves binary IoU by +9.71 over the strongest baseline under the same weak supervision. Its online self-correction alone adds +18.56 binary recall (an ablation, not a comparison with that baseline).
  - It still needs a human box per defect.
- **Ultra-thin, low-contrast fractures** (doi:10.1016/j.engappai.2026.115849): "unconstrained MedSAM mask supervision degrades performance". Foundation-model refinement only inside a narrow trust region around expert labels, with an IoU quality gate, gives "a modest improvement".
- **Annotation-free SAM fine-tuning for bridge cracks** from edge detection + VQVAE restoration (doi:10.1609/aaai.v40i25.39182): "close to fully supervised". Concrete cracks are wider and higher contrast than EL cracks (crack |ΔGL| 8.7 here).

## 4. What can be fully automatic (S, grounded in §1-§3)
| Target | Fully automatic route | Credible? | Why |
|---|---|---|---|
| Inactive regions | model-proposed inactive blobs (or dark-region detection) → SAM box prompt → mask | **boundaries: maybe; detection: no** | Inactive contrast 20-27 GL, blob-like: SAM-friendly. But on unseen modules the model's inactive recall is 0.43 (handbook 18 §U), and SAM refines only what is proposed. Gain is in mask shape, not in found regions |
| Scuff streaks | after B3, B3's scuff blobs → SAM → masks on 986 pool half-cells → scuff px for a later B3 data arm | **plausible, but not testable yet** | Streaks, 10-25 GL contrast. Scuff is the E1 failure context; training has 3,246 scuff px in 12 cells. No fair reference exists: `_rf` scuff is SAM-made (judge). PARKED until B3 and a non-SAM scuff reference |
| Cracks | SAM masks from model or point prompts | **no** | Low contrast and thin (E §1); the SAM limits (R); Hanifi speckle even after human review (E); unconstrained SAM supervision degrades thin structures (R) |
| Hanifi crack cleanup (24 half-cut crack cells) | trust-region filter: drop specks < 5 px not within 2 px of a model crack; bridge ≤ 3 px gaps along model crack | **mechanically yes; value unknown** | Removes most of the 75% speckle. It cannot be validated without clean labels and would encode the model's own bias. R4 used these cells raw and was n.d.; fracture paper: "modest" |

## 5. Human minutes per cell (S, honest; with the basis)
| Task | Minutes per cell | Basis |
|---|---|---|
| Accept / reject auto region masks (inactive, scuff), 1-3 regions | **0.5-1** | 14-34 s per assisted mask (R arxiv:2304.02643); here it is only a yes / no per region |
| Correct crack on a full cell where the model is good (relR@2 ≈ 0.87 on clean test) | 2-4 | median 3 crack components per crack cell (E §1); accept most, fix ends |
| **Correct crack on a half-cut + scuff cell** (model finds 13-30% of the crack: FINAL target recall 0.125, BN-HC 0.299; `verify_d.md`) | **6-12** | most crack length must be drawn by hand; at 2-3 px width a brush stroke per branch, ~20-40 s per component (S), and p90 12 components per crack cell |
| Clean a Hanifi half-cut crack cell (remove specks, fix 1-px lines) | 5-8 | repo estimate "2-3 h for the 24 half-cut crack cells" (`review_suggestions_2026-10-30.md` row 3) |
| Full masks on a mined B2 cell | ~15 | repo estimate "6-10 h for 20-40 cells" (vetter row 7) |

**Totals:**
- 24 Hanifi half-cut crack cells: **2-3 h** (cleanup) or ~2.5-5 h (from model proposals).
- 986 pool half-cells, crack: **~100-200 h**, infeasible. Only targeted subsets make sense: B2 top 20-40 → 6-10 h.
- Regions on 986 pool half-cells, accept / reject only: **~8-16 h**. A sample of 100 (~1-2 h) is enough to estimate the acceptance rate.
- **Zero-human-time options:** the §6 check, and the automatic trust-region crack filter (not validatable).

**Does a training-quality gain need human time? Yes, for cracks (S).**
- No automatic crack label in the evidence is clean enough to teach half-cut cracks.
- Adding Hanifi's half-cut cells with their labels did not move E1 (R4).
- The cells available (CSIR 297-335) are not E1's family.
- For regions, automatic masks may be usable. That is unproven; §6 tests it without human time.
- Ranking (S): B1 marks (1 h, pending) > the 24-cell Hanifi crack cleanup (2-3 h, only if B2 marks show ranked > random, per om §B4) > anything on the 986.

## 6. Protocol sketch: S10-inactive, SAM inactive masks vs model masks (inference only, zero human time) (v2 after judge)
- **Scope:** inactive only. **Scuff half PARKED until B3 exists** and a non-SAM, out-of-sample scuff reference is defined.
  - Val has 0 scuff; `_rf` scuff is SAM-made; train scuff is in-sample for B3. Options: B3 cross-fitted on the 12 train scuff cells, or B2-marked cells if the user masks them.
- **Reference: Pratt-labelled (20221008) masks only.**
  - Hanifi's `_rf` region labels were made with an SCDD-fine-tuned SAM (Roboflow Smart Polygon). "SAM vs `_rf`" would partly measure SAM-vs-SAM agreement, so `_rf` is not used.
- **Cells (judge, E):** B1's A50 out-of-fold set.
  - Models: `p16_A_50pct_s0-4` (house recipe, masks_escdd) scoring the 239 train cells outside the 50% labelled list (`team_2026-10-29_features/b1_audit/b1_coverage.txt`).
  - Of those, **22 inactive cells, 142,791 inactive px**: Pratt labels, out of sample for these models.
  - Val's 6 inactive cells (3 hold 89% of px) are reported, not decisive.
- **Prompts, model only (no human):** for each inactive component (≥ 100 px) of the A50 5-seed ensemble at its val-chosen operating point: its bounding box plus centroid point. SAM gives 3 masks; take the one with the highest predicted IoU.
- **Compare,** per cell, for:
  - (a) the model's inactive mask;
  - (b) the SAM mask (union over the cell's prompts);
  - (c) their intersection.
  - Metrics: per-cell inactive IoU and boundary F1 at 2 px vs the Pratt masks, plus pooled IoU.
- **Pass (fixed before any number):** (b) or (c) − (a) ≥ +0.05 in pooled inactive IoU, **and** a paired cell bootstrap over the 22 cells (2,000 resamples) gives a lower 95% bound > 0.
  - **Two comparisons, (b) and (c), are tested against (a), with no correction: disclosed.** A pass on either is reported with which one passed.
  - The 6 val inactive cells are **report-only** (3 hold 89% of px).
- **Kill:** SAM not better than the model's own masks. Then drop SAM from the pipeline: model masks alone are pseudo-label SSL, already n.d. at 100%.
- **Downstream value is low; stated now (judge item 4):**
  - an automatic-label training arm (SAM-refined inactive or, later, scuff masks on the 986 pool half-cells) is pool pseudo-labelling with a SAM refiner, and pool-label routes are n.d. at 100% (P16 Sx100, CP100);
  - the 986 are CSIR 297-335, not E1's family (vetter finding 4);
  - its only E1 readout sits in the "E1 co-primary slot (pending user)" (team-lead's interim rule).
  - So a pass is a thesis-method note on SAM as a region refiner. It does not open a training arm by itself.
  - Rank (judge): below ideas 3 / 5 / 11 for E1 value.
- **Prerequisites, batched with idea 8's ask (judge item 5):**
  - user OK for SAM2.1 Hiera-T (~156 MB, Apache-2.0);
  - team-lead OK for a `sam2` package install in a separate venv on gaint (training venv untouched).
- **Cost:** ~0.3 GPU-h inference through runner (scoring gate), or CPU; builder ~0.5-1 day (prompting script, venv); 0 user h.
- **Cracks:** no protocol. If the user ever wants crack labels, the minimal ask is the 24 Hanifi half-cut crack cells (2-3 h), conditional on the B2 marks, as om §B4 already set.

## 6b. S10-inactive RESULT (E; run 31 Oct 17:44-18:03 IST on gaint CPU; `s10_prereg.md` with judge A1; **judge CONFIRMED**: every number reproduced exactly; leave-top-3-GT-out b − a +0.056; b beats a in 10 of 22 GT cells, loses in 5)
**Files:** gaint `/home/noob/work/found/s10/`:
- `s10_result.json` md5 72967c1f (local copy `found_scripts/s10_result.json`);
- `model.npz` 7bf1e049, `sam.npz` 627fe970, `prompts.json` 982d0837;
- script `s10_inactive.py` ab367cab;
- precision / recall decomposition `found_scripts/s10_pr.py`.

**OOF set:** 239 cells; 22 GT-inactive cells, 142,791 px (equals judge's count); 78 prompts from the A50 ensemble.

| Set | a model | a′ model ≥ 100 px comps | b SAM | c a ∧ b |
|---|---|---|---|---|
| OOF pooled IoU | 0.4925 (ref) | 0.4898 | **0.5653** | 0.4864 |
| OOF pooled P / R | 0.842 / 0.542 | | 0.785 / 0.669 | |
| OOF mean boundary F1 (22 GT cells) | 0.356 | 0.347 | 0.349 | 0.349 |
| OOF median per-cell IoU (22 GT cells) | 0.425 | 0.422 | 0.572 | 0.420 |
| OOF pred px on the 217 cells without GT | 2,120 | 1,970 | 2,711 | 1,719 |
| val pooled IoU (report-only, 6 GT cells) | 0.4418 | 0.4403 | 0.4024 | 0.4428 |
| val pooled P / R | 0.548 / 0.695 | | 0.464 / 0.751 | |

**Rule (pre-registered; ref = a, since IoU(a) > IoU(a′)):**
- **b (SAM): PASS.** ΔIoU +0.0728 ≥ 0.05; paired cell-bootstrap 95% [+0.013, +0.135], lower bound > 0.
- **c (a ∧ b): FAIL.** −0.006, [−0.010, −0.001].
- Two comparisons, uncorrected (disclosed).

**Reading (S):**
- SAM acts as a region **expander**: OOF recall +0.127 at a precision cost of −0.057.
- It helps where the model under-extends regions (out-of-fold: P 0.84 / R 0.54) and hurts where the model already over-predicts (val: P 0.55, IoU −0.039, report-only, 6 cells).
- The gain is uneven: 10 of 22 GT cells improve, though the median per-cell IoU rises 0.425 → 0.572. Boundary F1 does not improve (0.356 → 0.349).
- False-alarm px on cells without GT inactive rise by 28%.
- So by its rule this is a pass, and as a method note it reads: "SAM fills partially found inactive regions on unseen cells; it does not sharpen boundaries and it adds false area where the model is already loose."
- It does not open a training arm by itself (§6: low downstream value; pool pseudo-labels; family mismatch).
- **Caveats for the method note (judge):**
  - tested on the A50 (50%-label) ensemble only, so it is untested at 100% labels;
  - val goes the opposite way (report-only, 6 cells);
  - two comparisons, uncorrected.

## 7. Expected effect (S)
- **Inactive:** SAM may sharpen boundaries (+0.02 to +0.08 inactive IoU vs model masks on the A50 OOF set), but cannot find what the model misses.
- **Downstream:** low (§6). A later scuff-auto arm would at most cut crack-on-scuff false positives further on E1. Test is unaffected (236 scuff px in 2 test cells).
- **Cracks:** no automatic gain expected. Human-corrected Hanifi half-cut cracks: E1 effect uncertain (R4 −0.011, family mismatch); test none.

---

## judge verdict (31 Oct 2026, 14:19 IST per log.md; report md5 b77012c8 as reviewed)

**Verdict:**
- **Cracks: SAM DROP, trust-region cleanup PARK. Agreed.**
- **Human-time figures: accepted as S.** They are consistent with om §B4 and the vetter's estimates.
- **Regions (S10): REVISE, then PARK the scuff half until B3 exists.** The check as written compares SAM against references that are largely SAM-made, and its sets are too small (items 1 and 2).

### What I reproduced (E)
- **Label speckle**, with independent code from the local E-SCDD (`judge/label_specks.py`):
  - `_rf` crack: 928 components, 697 < 5 px (**0.75**), 9.4% of crack px in components < 20 px, components per cell median 2 / p90 31 / max 380;
  - Pratt crack: 1,645 components, 64 < 5 px (**0.04**), 0.4%, 3 / 12 / 37.
  - **Exact match.**
- **Contrast ordering.** My ring is 3-8 px, padding excluded, cross-shaped dilation, so absolute values differ:
  - Pratt crack 10.8 < inactive 16.8 < scuff 30.9 GL (found: 8.7 / 19.9 / 24.9);
  - `_rf` crack 12.9 ≈ scuff 13.4 < inactive 35.8 (found: 10.1 / 10.1 / 27.2).
  - "Crack is the lowest-contrast class in Pratt labels" holds. "A quarter of Pratt inactive is low contrast" holds (my p25 4.8, found 5.4).
- **Literature:** all 6 ids resolve. Abstracts match the quoted claims for doi:10.1109/wacv61042.2026.00505, doi:10.1016/j.engappai.2026.115849 (bone fractures on radiographs: "modest improvement", unconstrained MedSAM degrades), doi:10.1609/aaai.v40i25.39182 and arxiv:2604.11162.
  - Small fix: Boxes2Pixels' +9.71 binary IoU is vs the strongest weak baseline. The +18.56 recall is the gain from online self-correction, not vs that baseline.
  - arxiv:2304.02643 resolves; the 34 → 14 s per mask figure is from SAM §4 (not re-read).

### What must change in S10
1. **The reference is biased toward SAM (S, from the data provenance).**
   - Hanifi's `_rf` region labels were made with an SCDD-fine-tuned SAM (Roboflow Smart Polygon). So "SAM mask vs `_rf` label" partly measures agreement between two SAM outputs.
   - A SAM win on `_rf` scuff or inactive is therefore not evidence that SAM masks are closer to the truth than model masks.
   - Use Pratt-labelled (20221008) references only.
2. **The sets are too small, and a better inactive set exists (E).**
   - Val inactive is 6 cells, with 3 holding 89% of px (handbook 13 A2). A pooled +0.05 IoU there is decided by 3 cells.
   - **Use B1's A50 out-of-fold set instead:** p16_A_50pct s0-4 scoring the 239 train cells outside the 50% labelled list (`team_2026-10-29_features/b1_audit/`).
   - Those cells hold **22 inactive cells, 142,791 inactive px**, with Pratt labels, out of sample for the A50 models (my count from the 20221008 masks).
   - Report per-cell IoU with a paired cell bootstrap.
3. **Scuff has no fair reference yet (E/S).**
   - Val has 0 scuff. `_rf` scuff is SAM-made (item 1). Train scuff (12 cells; 4 inside the A50 OOF half) is in-sample for B3. E1 scuff is descriptive only.
   - So the scuff half cannot be judged until B3 exists and a non-SAM, out-of-sample scuff reference is defined: e.g. B3 cross-fitted on the 12 train scuff cells, or the B2-marked cells if the user masks them.
   - **PARK scuff-S10 until after B3.**
4. **The downstream value is low; state it in the sketch.** "B3-auto" means auto scuff masks on the 986 pool half-cells. That is pool pseudo-labelling with a SAM refiner, and:
   - (a) pool-label routes are n.d. at 100% (P16 Sx100, CP100);
   - (b) the 986 are CSIR 297 to 335, not E1's family (vetter finding 4);
   - (c) its only E1 readout is pending the user's E1 policy (team-lead's interim rule: an "E1 co-primary slot (pending user)" line).
5. **Prerequisites need two approvals.** A package install (sam2, separate venv: team-lead) and a weights download (~156 MB: user). Both are justified only for the inactive half under item 2. Ask for them together with the other weight requests (idea 8), not separately.

### Cost, effect, kill (S)
- **Inactive S10** on the A50 OOF set: ~0.3 GPU-h at the scoring gate, ~0.5 to 1 day of code, 0 user hours.
- **Expected:** boundary IoU +0.02 to +0.08 if SAM helps (found's S); no new regions found.
- **Kill:** real (SAM not better than model masks). With the A50 OOF set it is also adequately powered for inactive.
- **Rank:** below ideas 3 / 5 / 11 for E1 value; a thesis-method note at best.

### Tags
- E: speck stats reproduced exactly; contrast ordering reproduced; the A50-OOF inactive count is new.
- R: 6 ids resolved.
- S: the SAM-reference bias and the downstream-value reading.

## judge re-review of v2 (31 Oct 2026, 14:30 IST from date; report md5 96458cf7 as reviewed)
**Regions: PASS-to-protocol, inactive only, low priority.**
- Conditions: the two approvals (sam2 venv: team-lead; ~156 MB weights: user), batched with idea 8's.
- **Scuff: PARK** until B3 and a non-SAM out-of-sample reference exist.
- **Cracks: DROP/PARK** as agreed.
- v2 applies all 5 items:
  - Pratt references only;
  - the A50 OOF set (22 inactive cells) decides, with a cell bootstrap;
  - scuff is parked;
  - low downstream value stated;
  - approvals batched.
- **Minor, for the protocol:**
  - (i) "(b) or (c)" tests two candidates against (a). Disclose this as 2 comparisons.
  - (ii) The val term (6 cells, −0.02) can fail on 3 cells. Make it reported, or widen it to −0.05, as for idea 8's screen.
