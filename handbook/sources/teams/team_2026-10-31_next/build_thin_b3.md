# Build: thin-crack losses (Skeleton Recall, clDice), B3 scuff class, distance-map costing

builder, 31 Oct 2026 (v2, after coach's review). Code only, no verdict runs. Tags: E = measured (file or command named), R = Research MCP id, S = judgement.

## Q. Questions to coach and rulings (coach, 31 Oct ~14:1x-14:29; also in `log.md` and `protocol_thin_b3.md` v0.1 §3-4)
| # | Question | Ruling | Where it lands |
|---|---|---|---|
| B3-1 | Dice on scuff? Spec says "CE + Dice on all trained classes"; house Dice is on (14, 11) only | Dice stays (14, 11); scuff in CE only | code default, §8 |
| B3-2 | Scuff → background map: primaries already score `pred == c`, so the map only matters for the 24×24 confusion | agree; disclose the 25-channel softmax for AP. A margin score's "max over k ≠ crack" includes scuff, consistent with the 24 → 0 map | §8, §11 |
| B3-3 | LA τ 1 prior over 25 classes from masks_escdd_s | agree (each arm's own train prior); disclosed | §8 |
| B3-4 | Build E1 scuff masks (raw class 25) for secondary 1 under the E1 seal? | YES: a diagnostic read for a pre-registered descriptive secondary, never training or selection. n = 105 (1 cell has no raw mask), md5 manifest. (An old-run cross-check was first requested, then dropped by the FINAL S4 ruling below) | released, §8 |
| B3-5 | Descriptive test set with the 236 raw-scuff px ignored | agree; the same mask files serve PF2's scuff-ignored set | `el_thin/data/test_scuff`, §8 |
| B3-6 | 5 train cells without a raw E-SCDD mask stay unchanged | OK | §8 |
| B3-7 | 25-channel head init differs; identity gate = flags off vs e544133 | agree; disclose the head init / RNG shift | §11 |
| B3-8 | Val has 0 scuff px: nothing about scuff is tunable on val | OK | §8 |
| T-a | Weights | w = 1 for both, additive (house + w · L), **fixed, no val grid**; log each term | §7 |
| T-b | clDice k | **k = 10** (official code). Raised only if the p99.9 train crack radius exceeded 10; it is ≤ 4.24 | §7 |
| T-c | SR tube | paper version: diamond r 2, clipped to GT. Note for the protocol: on our 1-3 px cracks the tube is ~the whole mask, so SR is a soft crack-recall term | §6, §7 |
| T-d | skeletonizer port | good | §6 |
| T-e | co-primary scorer (component recall at precision ≥ 0.90, relR@2 at relP@2 ≥ 0.90) | calib's scorer, md5 frozen before launch; not in this build | n/a |
| T-f | losses in float32 outside autocast; ignore px excluded from targets and predictions; zero-crack batch finite, no NaN; unit-tested | done (d93d9a1). clDice keeps the paper form on crack-free batches (ruling below) | §3, §5, §11 |
| G | GPU identity length | S0 runs to **2,000 steps** (protocol_PF2 §7) | §9 |
| G | smokes | through runner's shared gate (`gpu_gate.sh`), one at a time, ~22:00-23:30 beside a lone RN50-PF run | §9 |
| S4 | old-run scorer passes (FINAL, via runner) | **identity pass only** (no-flag `m0_audit_b3.py` on f3_SUPPF_100pct_s0 vs the opening-1 JSON). No `--test-scuff` and no `--ext-scuff` on any old run: a test read outside an opening. The B3 E1 crack-on-scuff baseline comes from `--ext-scuff` on pf2_SUPPF s5-9 inside THIN-B3's own opening; `test_noscuff` likewise only inside an opening | §4b, §9 |
| R | arXiv 2508.11374 MCP-returned? | yes: `get_paper arxiv:2508.11374` returned "Does the Skeleton-Recall Loss Really Work?" (Arora, Kumar, Gupta, 2025) | §7 |
| D | distance-map arm | agree, no third arm now; it would need the user's OK anyway (Om approved SKR / CLD / B3 only) | §10 |

**Ruling on T-f (coach, 31 Oct): keep the paper / official form.** On a crack-free batch L_srec is exactly 0 (empty tube). The smoothed L_cl is finite but not 0: Tsens = 1, Tprec = 1 / (|S(p)| + 1), so it pushes the predicted soft skeleton down, which is part of the method. A batch of 8 has no crack with probability (269/478)^8 ≈ 1%. Tested: finite, with finite gradients. Coach's "term 0" requirement was only there to rule out NaN.

## 0. Summary
- **Code.** Worktree `/home/noob/work/el_thin` (branch `thin`, from e544133). Commits:
  - 9461ecc code + tests;
  - c66850f smoke + E1-scuff scripts;
  - d93d9a1 (coach fixes: float32 thin terms, scorer counts, smoke on the shared gate): smokes ran at this commit;
  - b4ddb08 (1 Nov): crack-on-scuff counting as a tested helper (`src/evaluation/b3_scuff.py`); suite 314 passed, 3 skipped;
  - **c9bbb02 = deploy** (1 Nov): `scuff_train_iou.py` writes the 20k readout (md5 f6d77562); `m0_audit_b3.py` md5 7aa7d6d8. No training-code change since d93d9a1; stamp `reports/thin/DEPLOY`.
  - **THIN-B3 deploy = c9bbb02** (coach ruled; runner arms with REVISION = c9bbb02). The opening asserts scuff_train_iou f6d77562 and runs it on CPU fp32 for B3 s5-9 and pf2_SUPPF s5-9. **el_thin is frozen until the opening ends.**
- **Three opt-in switches, all off by default:** `loss.skel_recall.weight`, `loss.cldice.weight`, `data.scuff_class=24`.
- **Bit identity (E, CPU):** with all switches off (or weight 0), el_thin = e544133 bit for bit over 5 real training steps, house and PF recipes, at 9461ecc and again at d93d9a1 (§4). The B3 scorer copy without flags writes a byte-identical JSON to `m0_audit_tau.py` (CPU). **GPU (smoke S0, runner): IDENTICAL to f3_SUPPF_100pct_s0 over 2,000 steps (80 / 80 lines).**
- **Disclosed slip (§4b):** a CPU batch at 14:46-14:54 also ran the scuff scorer passes on two already-opened runs before coach's ruling reached me. Outputs quarantined; no value from them is used or reported.
- **Tests (E):** 314 passed, 3 skipped (285 + 29 new), CPU only.
- **Skeleton (E):** numpy port of scikit-image's `skeletonize`, identical to skimage 0.26 on 400 random blobs and all 423 E-SCDD crack masks. Tube precompute: mean 2.9 ms per mask, in the data workers, no RNG.
- **Facts for the protocol (E):**
  - the r-2 tube covers **99.2%** of our crack px, so SR acts as a soft crack-recall term;
  - max crack radius 4.24 px (p99 3.61), so clDice k = 10 is safe (GT skeleton identical to k 5).
- **Distance-map target: no third arm now (S, §10; coach agrees).**

## 1. Worktree, commits, data
- **Worktree:** `/home/noob/work/el_thin`, branch `thin`, created 31 Oct 13:53 IST (`git worktree add ../el_thin -b thin e544133`). The main tree and el_f1/f2/f3 were never modified; el_f3 / el_f1 / cv02_noob_el files were only read.
- **Commits on top of e544133:**

| Commit | Content |
|---|---|
| `9461ecc` | THIN / B3 code + tests (16 files, +1,386 / −15) |
| `c66850f` | `scripts/thin/smoke_thin_b3.sh` v1, `scripts/b3/build_ext_scuff.py` |
| `d93d9a1` | coach-review fixes: `thin_crack.py` (terms under autocast-disabled; docstring), `test_thin_crack.py` (+1 test), `m0_audit_b3.py` (crack-on-ignored; binary `--test-scuff`), `smoke_thin_b3.sh` v2. The GPU smokes ran here |
| `b4ddb08` | `src/evaluation/b3_scuff.py` (fold + scuff counts, pure numpy) used by `m0_audit_b3.py`; known-overlap test. **Deploy**; `reports/thin/DEPLOY` = b4ddb08 (untracked stamp, like el_f3's REVISION). Training path identical to d93d9a1 |

- **Data (`el_thin/data`, gitignored as in el_f3):**
  - `labeled/{images,masks_coded,masks_escdd}` → `el-fault-detection/data/labeled/*`;
  - `escdd_masks` → `el_f1/data/escdd_masks`; `unlabeled` → `el-fault-detection/data/unlabeled`;
  - real dirs: `labeled/masks_escdd_s/` (B3 train masks), `ext_scuff/` (E1 scuff, 38 PNGs, manifest md5 8a7a028b), `test_scuff/` (2 PNGs, 236 px, manifest md5 81bdc3ba).
  - Copies of `ext_scuff/` and `test_scuff/` for calib / runner on the laptop: `team_2026-10-31_next/scuff_masks/` (md5-checked).

## 2. Switches (all opt-in; absent or weight 0 = the e544133 path)
| Arm | Opts added to SUP100-PF (BEST: `training.encoder_pf` freeze 1000 / ramp 1000 / lr_mult 0.1 / wd 0) | What changes |
|---|---|---|
| SKR (Skeleton Recall) | `loss.skel_recall.weight=1.0` | loss = house CE + Dice + 1 · L_srec on crack (14); data workers add `skel_tube` per augmented sample |
| CLD (clDice) | `loss.cldice.weight=1.0 loss.cldice.iters=10` | loss = house CE + Dice + 1 · L_clDice on crack (14) |
| B3 (scuff) | `data.scuff_class=24 model.num_classes=25 data.mask_subdir=labeled/masks_escdd_s` | 25-channel head; train masks with scuff = 24 (12 cells); evaluation maps predicted 24 → 0 |

- **Defaults:** `loss.skel_recall.tube_radius` 2 and `smooth` 1e-5; `loss.cldice.smooth` 1.0; `loss.thin_class` 14. The code default of `loss.cldice.iters` is 5, so the protocol must pass `iters=10` explicitly (the smoke does).
- **Refused at start (ValueError):** any switch with SSL, alhvr, `cp`, `absh` or a non-ce_dice loss; scuff with `mask_ignore_value`; `scuff_class` ≠ 24 or `num_classes` ≠ 25.
- No config file mentions any switch (a test checks this).

## 3. Diff summary (`git diff e544133 d93d9a1`)
**New files**

| File | Content |
|---|---|
| `src/data/skeleton.py` | `skeletonize_2d` (numpy port of skimage's 2-D `skeletonize`; LUT copied with the BSD-3 notice), `diamond`, `tubed_skeleton` (skeleton, diamond r 2, × crack mask) |
| `src/data/thin_targets.py` | `TubedSkeletonDataset`: adds `skel_tube` (uint8) computed from the *augmented* mask; draws no random numbers, so the stream's images and masks are unchanged with the flag on (test + E §4) |
| `src/losses/thin_crack.py` | soft skeleton (clDice App. G.2), `soft_cldice_loss`, `skeleton_recall_loss`, `ThinCrackLoss` = `base(logits, targets)` unchanged + w_srec · L_srec + w_cl · L_cl; the thin terms run under `torch.autocast(enabled=False)` in float32 on p(crack) = softmax(logits.float())[:, 14] × valid; targets × valid; `last_terms` for the log |
| `scripts/b3/build_masks_escdd_s.py` | deterministic B3 mask build (§8) |
| `scripts/b3/m0_audit_b3.py` | B3 copy of `el_f1/reports/f1/m0_audit_tau.py` (md5 d77241bb) (§8) |
| `scripts/b3/scuff_train_iou.py` | smoke metric: scuff IoU on the 12 train scuff cells |
| `scripts/b3/build_ext_scuff.py` | binary scuff masks (raw class 25) + manifest; used for `ext_scuff` and `test_scuff` |
| `scripts/thin/identity_cpu.py` | CPU identity harness (§4) |
| `scripts/thin/smoke_thin_b3.sh` | runner's smoke script (§9) |
| `tests/test_thin_crack.py`, `tests/test_b3_scuff.py` | 28 tests (§5) |

**Edits (each guarded; flags off = the old code path)**

| File | Lines | Edit |
|---|---|---|
| `src/losses/loss_factory.py` | +13 | wraps ce_dice in `ThinCrackLoss` only if a thin weight > 0 |
| `src/trainers/trainer.py` | +25 | supervised branch passes `tube=batch["skel_tube"]` only when SR is on (else the old call); thin terms on their own line `thin loss_srec=... loss_cldice=... at step N` (log-window mean; the step line keeps its keys, as PF did); `evaluate` uses `fold_to_bg=24` and 24 metric classes only when `data.scuff_class` is set; thin refused with SSL / absh |
| `scripts/train.py` | +50 / −4 | `check_thin_b3`; B3 labelled dataset accepts 24 and counts 25 classes; `TubedSkeletonDataset` wrap; zero-pixel class names from a list (same names when off) |
| `src/data/benchmark_el.py`, `src/data/class_stats.py` | +14, +14 | optional `num_classes` (default None = the 24-class check) |
| `src/evaluation/evaluator.py` | +8 | optional `fold_to_bg` (default None) |
| `scripts/rescore_logit_adjust.py` | +5 | `log_prior`: 25 counts when `data.scuff_class` is set |

`scripts/rescore_label_versions.py` is unchanged: crack and inactive are scored as `pred == c` (a scuff argmax is "not crack"), and the model is built from `config_used.yaml`.

## 4. Bit-identity proof
**4a. CPU training path (E; harness `el_thin/scripts/thin/identity_cpu.py`)**
- **Reference:** e544133 exported by `git archive` to `/home/noob/work/builder_scratch/e544133` (same data links), so el_f3 is never imported.
- **Per code root:** the root's own `apply_opts`, `build_benchmark_data`, `build_model`, `build_losses`, `build_optimizer`, `Trainer._train_step`. Real labelled stream (seed 0, 478 cells, batch 8), fp32 on CPU, 8 threads, nice 19, `CUDA_VISIBLE_DEVICES=""`, 5 steps.
- **Recorded:** per step the exact loss repr, lr per param group, a sha256 over every parameter and buffer, and a sha256 of the eval-mode logits on a fixed batch (stream batch 0, 8 × C × 512 × 512); also loss class, init-state hash, class-count hash, fixed-batch image / mask hashes.

| Pair | Opts | 9461ecc (`reports/thin/idchk/`) | d93d9a1 (`builder_scratch/idchk2/`) |
|---|---|---|---|
| e544133 vs el_thin, flags off | SUP100 house | **IDENTICAL** 5/5 (losses 4.6675262451171875, 4.657222747802734, 4.688233375549316, 4.656167030334473, 4.725292682647705) | **IDENTICAL** 5/5 |
| e544133 vs el_thin, flags off | SUP100-PF | **IDENTICAL** 5/5 (encoder lr 0.0 in the freeze) | **IDENTICAL** 5/5 |
| flags off vs weight 0 (`skel_recall.weight=0 cldice.weight=0`) | SUP100-PF | **IDENTICAL** | **IDENTICAL** (vs e544133 PF) |
| SR on (w 1) | SUP100-PF | differs as designed: step-1 loss 5.6444 = house 4.6675 + L_srec 0.9769; fixed-batch image and mask hashes = flags-off (data stream unchanged with the flag on) | identical to 9461ecc SR (the autocast-disabled block changes nothing in fp32) |
| clDice on (w 1) | SUP100-PF | k 5: step-1 5.6671 = 4.6675 + L_cl 0.9996 | k 10: step-1 5.6671 (L_cl 0.99960); L_cl 0.9970 at step 5; finite; CPU 14.0-14.5 s/step |
| B3 on | SUP100-PF | differs as designed: +145 params (head 16 × 9 + 1), logits 8 × 25 × 512 × 512, 25-class counts; same image / mask bytes on the fixed batch (no scuff cell in it) | not re-run (B3 code unchanged since 9461ecc) |

- **md5 (9461ecc records):** A 30f6266c, B 1006dad8, C 594b62ea, D 4a6810d4, H 473f4c59, E be59bf49, F e6c3a9a1, G b2148755.
- **CPU s/step (median of 5, fp32, noisy because PF2's loaders share the CPUs):** off 13.07, SR 13.41, clDice k 5 15.0, B3 15.4. GPU speed comes from S1-S3.
- `loss_sup` in the step line is the full supervised loss (house + thin term); the term alone is on the `thin` line.

**4b. CPU scorer identity (E) and a disclosed slip**
- **After the counting refactor (b4ddb08), val only (1 Nov, CPU fp32, `builder_scratch/m0val/`):** `m0_audit_tau.py` (el_f1, d77241bb) vs the refactored `m0_audit_b3.py` without B3 flags, on f3_SUPPF_100pct_s0 with `--sets val`: **byte-identical JSON** (md5 6a2d1fa3 both; val + val_tta). Test and E1 were not touched (coach: the re-check on val only).
- **Identity.** On el_f3 `f3_SUPPF_100pct_s0` (read-only), cell sets test + ext, CPU fp32: `m0_audit_tau.py` (el_f1, md5 d77241bb) and `m0_audit_b3.py` without B3 flags wrote **byte-identical JSONs** (md5 61530adc both). So the copy changes nothing for a 24-class run. The GPU check vs the opening-1 JSON is runner's identity-only S4 (§9).
- **Slip (31 Oct, 14:46-14:54 IST, `builder_scratch/idchk2/run.sh`).** That batch:
  - recomputed the test + ext cells of an opened run for the identity pair;
  - also ran `m0_audit_b3.py --ext-scuff --test-scuff` on `f3_SUPPF_100pct_s0` and `p6_L3_100pct_s0`.
  The second pass produced test (incl. `test_noscuff`) and E1 scuff numbers for already-opened runs outside any opening. It started before coach's S4 ruling reached me, but the README rule (test only at a pre-registered opening) already applied.
  - Nothing from it is used for any choice, and no value from it appears in this file.
  - All outputs moved to gaint `builder_scratch/quarantine_test_reads_2026-10-31/`. Coach ruling: KEEP as the audit trail, outputs unreadable (chmod a-r); only README.txt and MANIFEST.md5 (md5 e367b101) stay readable. No impact on any verdict: those runs are in no PF2 / THIN-B3 contrast, and THIN-B3 uses seeds 5-9 with its own opening. Disclosed in protocol_thin_b3 §0 and `log.md`.

**4c. GPU (E, smoke S0, runner, 31 Oct 23:36).** The flags-off run at d93d9a1 matches `el_f3/experiments/f3_SUPPF_100pct_s0.stdout` on step + `PF encoder lr=` lines to step 2,000: **IDENTICAL, 80 / 80 lines**. The B3 path off (24 classes, old masks) is that same flags-off run. That meets protocol_PF2 §7's ≥ 2,000-step condition for the shared baseline.

## 5. Unit tests (E; `el_thin/reports/thin/suite_v1.txt`)
- **Full suite** (`CUDA_VISIBLE_DEVICES="" F1_IMAGENET=1 HF_HUB_OFFLINE=1`, nice 19, 8 threads): **313 passed, 3 skipped, 26.6 s, rc 0**. protocol_100 had 285 passed, 3 skipped; +28 new.
  - (The v0 suite run at 14:14, 312 passed, ran without `CUDA_VISIBLE_DEVICES=""` and held a 254 MiB CUDA context for ~25 s; see `log.md`.)
- **`tests/test_thin_crack.py` (23):**
  - **Skeleton:** matches skimage on 7 toy masks (its docstring ellipse, 3-px bar, 7×7 and 2×2 squares, 3-px diagonal, ring, L); edge cases (empty; a 1-px line and a dot are their own skeleton; border; crop = full image); keeps the 8-connected component count on 60 random blobs; the ring stays closed.
  - **Tube:** inside the crack mask, contains the skeleton, 5 px wide on a 7-px bar; for a 1-px crack the tube equals the crack.
  - **Perfect prediction:** SR < 1e-6, clDice < 1e-4; > 0.99 / > 0.9 at p(crack) = 0.
  - **Gradients:** finite; SR gradient only on tube px and negative on the crack logit there; clDice gradient non-zero.
  - **Zero-crack batch:** SR = 0 exactly with zero gradient; clDice (k 10) finite in [0, 1) with finite gradients; terms float32 under a bf16 autocast.
  - **Ignore px:** change neither term.
  - **Wrapper:** = base + Σ w·term; precomputed tube = on-the-fly tube.
  - **Factory:** absent or weight 0 builds the plain `CEDiceLoss`.
  - **Trainer:** house path unchanged with or without a `skel_tube` key; the SR path gets the tube; the step dict keeps its 4 keys; `fit()` writes `thin ...` lines and no thin keys on step lines; thin + SSL refused.
  - **Data wrapper:** BatchStream over `TubedSkeletonDataset` = plain dataset (images, masks, stems) for 7 batches; the tube is that of the augmented mask.
  - **Configs:** no switch in `configs/*.yaml`.
- **`tests/test_b3_scuff.py` (5):**
  - default loading and counting reject 24; the switch accepts and counts it;
  - fold = a 24-channel model predicting background on those px (same confusion matrix);
  - without the fold a predicted 24 raises;
  - switch checks;
  - mask build changes only train cells with raw scuff, byte copies of all else, refuses to overwrite;
  - LA prior has 25 entries with the switch, and raises on B3 masks without it.

## 6. Skeleton port and precompute cost
- **Why a port:** scikit-image is not in the training venv (no installs). Skeleton Recall skeletonizes 2-D masks with Zhang-Suen "using libraries such as scikit-image" (R doi:10.1007/978-3-031-72980-5_13, Sec. 3.2, ref. [42]).
- **Textbook Zhang-Suen** differed from skimage on 365/400 random blobs and 413/423 crack masks; skimage's table keeps line ends. So I copied skimage's 256-entry LUT and pass rule from its open-source Cython file (`_skimage2/morphology/_skeletonize_various_cy.pyx`, BSD-3) into a vectorised numpy loop.
- **Cross-check (E, laptop, skimage 0.26):** 400/400 random blobs and 423/423 E-SCDD crack masks identical, 0 differing px of 191,984.
- **Precompute cost (E, gaint, 1 thread, 478 train masks):**
  - mean **2.86 ms**, median 0.08 (269 crack-free cells return early), p95 11.1, max 42.9 ms;
  - about 23 ms per batch of 8, spread over 4 loader workers, about 1.3% of their CPU per GPU step at 2.25 steps/s (S).
- **On our data (E):** 209 crack cells, 271,805 crack px, 113,300 skeleton px, tube 269,606 px = **99.2% of crack px**.
  - (S) So SR is close to "1 − soft recall of crack": a recall push, not a centerline term.
  - Coach: no tube_radius-0 arm in this protocol.

## 7. Hyperparameters (fixed from the papers; no tuning)
| Loss | Parameter | Value | Source and why for 1-3 px cracks |
|---|---|---|---|
| SR | w | **1.0**, additive | official trainer default `weight_srec = 1`; the paper tested w ∈ {0.1, 1.0} (R doi:10.1007/978-3-031-72980-5_13, Sec. 4.4 and App. A Fig. 8) |
| SR | tube | diamond r 2, × GT crack | paper Sec. 3.2 / Alg. 1. On our cracks (E: 99.2% coverage) it is ~the crack mask |
| SR | smooth | 1e-5, batch sums | official trainer (`batch_dice`, smooth 1e-5) |
| CLD | w | **1.0**, additive: house + w · L_cl | the SR paper's Eq. 2 form for its clDice baseline. The clDice paper's own form is (1 − α) softDice + α clDice, α ∈ [0.1, 0.5], no single best α (R doi:10.1109/cvpr46437.2021.01629, Sec. 4.2, Table 1); code default α 0.5 = equal weight to Dice. **α (mix) is not used**; the house Dice stays at full weight |
| CLD | k | **10** | clDice paper: k ≥ max structure radius, they used 5-25 (Sec. 4.1); official code hard-codes 10. E radius distribution below |
| CLD | smooth | 1.0 | official code |
| CLD | channel | crack (14) only | clDice paper Sec. 4.3 (foreground only for imbalanced data) |

- **k = 10 for 1-3 px cracks.** The GT soft skeleton is the same for k 5 and 10, because every GT crack is fully eroded by iteration 5. k only changes the skeleton of soft predictions wider than ~5 px, where 10 is truer.
- **Radius distribution (E, max inscribed radius by EDT, 1,000 train crack components):** median 1.41, p90 2.24, p99 3.61, max 4.24 px. So p99.9 ≤ 4.24 < 10. ≤ 2 px for 82.3%, ≤ 3 px for 97.8%.
- **No tuning** (coach): w, tube and k are fixed. Val has 23 crack cells, too noisy to choose on. Test and E1 are never used.
- **Term magnitudes** are logged on the `thin` line; S1 / S2 report them at 2k.
- **Risk (R arXiv:2508.11374, "Does the Skeleton-Recall Loss Really Work?", returned by Research MCP `get_paper`):** on concrete cracks over 5 seeds, SRL left DSC n.s., lowered FNR and significantly raised FPR; its gradient never penalises false positives.
  - (S) With our tube ≈ mask, expect crack recall up and crack precision down.
  - The co-primaries at precision ≥ 0.90 and the relP@2 width check are the guard.

## 8. B3 (spec_b3_scuff.md)
**Masks (E; `el_thin/data/labeled/masks_escdd_s/`)**
- Built with `scripts/b3/build_masks_escdd_s.py --base data/labeled/masks_escdd --raw el-fault-detection/data/escdd_masks/train`.
- 582 files (478 train + 54 val + 50 test). **12 train cells, 3,246 px → class 24** (from bg 1,207, material 1,390, crack 649), exactly the spec §1 numbers.
- The other 570 files are byte copies (md5 asserted).
- Files: `masks_escdd_s.diff.tsv` md5 e0e8a3b8; `MANIFEST.md5` md5 107d0d1c; `summary.json`.
- 5 of the 478 train cells have no raw mask and are unchanged.

**Model, loss, metrics**
- `model.num_classes=25`: the head grows by one channel.
- House CE over 25 classes; **Dice stays on (14, 11)** (ruling B3-1).
- Class counts have 25 entries.
- In-training val/test: predicted 24 → 0, then the 24-class metrics.

**Scorers**

| Scorer | B3 handling |
|---|---|
| `rescore_label_versions.py` (primaries) | unchanged: `pred == 14 / 11`; p(crack) for AP = softmax over all 25 channels (disclosed) |
| `rescore_logit_adjust.py` (LA τ 0/1) | prior over 25 classes from masks_escdd_s (scuff π = 3,246 / all train px); each arm's own train prior (disclosed) |
| `scripts/b3/m0_audit_b3.py` (m0 per cell, E1) | copy of `m0_audit_tau.py` (md5 d77241bb) + three additions, below |

The three additions in `m0_audit_b3.py`:
1. argmax ≥ 24 → 0 (plain and val TTA); a no-op for 24 channels.
2. `--ext-scuff data/ext_scuff`: per E1 cell a `scuff` dict:
   - scuff_px, crack_on_scuff;
   - scuffpred_on_scuff, scuffpred_px (argmax 24 before the map);
   - ignored_px, crack_on_ignored (on the ext117 ignore mask; the 27 Oct `crack_pred_on_ignored` definition).
   These are descriptive secondary 1: a diagnostic read of E1, never training or selection.
3. `--test-scuff data/test_scuff`: extra cell set `test_noscuff` = the 50 test cells with the 236 raw-scuff px ignored (option b, descriptive). It uses the same mask files as PF2's scuff-ignored set.

`--ext-scuff` and `--test-scuff` are run only inside a pre-registered opening (THIN-B3's, on its own arms and baseline), never on an already-opened run.

**E1 and test scuff masks (`scripts/b3/build_ext_scuff.py`)**
- **E1** (from laptop `~/mtp/datasets/escdd_full`): 105 of 106 E1 cells have a raw mask (missing `CSIR_00308_r5_c3`, so n = 105); **38 have scuff, 84,511 px**; manifest md5 **8a7a028b**. Released to `el_thin/data/ext_scuff` per ruling B3-4.
- **Test** (from gaint `el-fault-detection/data/escdd_masks/test`): 50/50 raw masks; 2 cells with scuff (ARTS_00047_r3_c1 34 px, ARTS_00051_r3_c2 202 px = 236); manifest md5 **81bdc3ba**. At `el_thin/data/test_scuff`.
- **Laptop copies:** `team_2026-10-31_next/scuff_masks/{ext_scuff,test_scuff}`.

## 9. GPU smokes (runner, 31 Oct 23:36 to 1 Nov 00:22 IST; DONE)
Runner ran `el_thin/scripts/thin/smoke_thin_b3.sh S0 S1 S2 S3` at deploy **d93d9a1** (script md5 **92956d86**), then its own identity-only S4; side queue done 00:22 IST, 1 Nov.
- **Gate:** sources runner's `el_f3/reports/pf2/scripts/gpu_gate.sh` (md5 00fabfdd): one shared flock, free ≥ need, ≥ 120 s since any start, HOLD honoured.
- **Needs:** training 9,000 MiB (fine-tune peak + 2 GB); thin 10,000 (peak unknown); scoring 7,154.
- **Order:** one job at a time.
- **Run setup:** `--exit_after_step 2000` (latest.pth is written at 2,000 first; rc 3 = planned exit); rc before `date`; deploy check HEAD = DEPLOY with 0 tracked changes.
- **Reported per run:** peak `max_memory_reserved` from `latest.pth["trainer"]["peak_reserved"]`, per-process nvidia-smi max (runner also logs at 1 s), steps/s, finite losses, thin term lines.
- **Do not run the script's own S4 block:** it still contains the scuff passes the FINAL ruling forbids. Runner's identity-only S4 replaces it. The script is not edited, so DEPLOY and md5 stay as pinned.

| Smoke | What | Result (E) |
|---|---|---|
| S0 | flags off, SUP100-PF s0, 2,000 steps; 80 step + PF lines vs `f3_SUPPF_100pct_s0.stdout` | **IDENTICAL** (80 / 80 lines). Peak nvidia-smi 6,826 MiB (peak_reserved 6.35 GiB); 3.36 steps/s |
| S1 | SKR w 1, 2,000 steps | finite; L_srec 0.968 (step 50) → 0.195 (500) → 0.175 (1k) → 0.150 (1.5k) → **0.181 at 2k**; peak **7,020 MiB** (6.54 GiB reserved); **3.26 steps/s (−3% vs S0)** |
| S2 | CLD w 1 k 10, 2,000 steps | finite; L_cl 0.995 → 0.493 → 0.448 → 0.422 → **0.410 at 2k**; peak **8,374 MiB** (7.86 GiB reserved; +1.5 GB over the house; coach's soft-skeleton concern measured); **3.02 steps/s (−10%)** |
| S3 | B3, 2,000 steps, val at 1k / 2k + scuff IoU on the 12 train cells | finite. The val fold path ran: defect_miou 0.341 (1k), 0.366 (2k). Peak 5,738 MiB; 3.42 steps/s. **Scuff IoU 0.0**: 0 px predicted scuff at 2k; GT scuff px predicted as bg 2,372 / crack 501 / class 18 185 / ribbons 182 (see below) |
| S4 (runner) | no-flag `m0_audit_b3.py` on f3_SUPPF_100pct_s0 vs the opening-1 m0 JSON | **identical** cells (val, val_tta, test, ext) |

- **Setup:** one at a time, beside one RN50-PF run and finllm (steps/s are not single-run speeds), 23:36-00:19 IST.
- **Logs:**
  - `el_thin/reports/thin/smoke/smoke.log`, `pids.txt`, `*.gpumem.txt` (5 s);
  - runner's `el_f3/reports/pf2/side/side.log`;
  - the 1 s window `el_f3/reports/pf2/gpumem.log` 23:32-00:22, whose per-process maxima match.
  - Minimum free 6,232 MiB at 23:57:53, during clDice startup.
- **Start gates from measured peak + 2,048 MiB:**

  | Arm | Gate (MiB) |
  |---|---|
  | SKR | **9,068** (just above the house 9,000) |
  | CLD | **10,422** |
  | B3 | 7,786 (the house 9,000 covers it) |

- **B3 scuff diagnostic** (E; train cells only; 2k checkpoints; CPU fp32; one-off `builder_scratch/b3diag/scuff_prob.py` md5 1cdabfe0, output md5 e9cc84ae):
  - **The scuff channel is learning, but weakly.** On the 12 train scuff cells, mean p(scuff) is 1.3e-4 on GT scuff px vs 3.2e-5 elsewhere: 4.2× enriched. The "elsewhere" level is about scuff's train pixel frequency (3,246 px ≈ 2.6e-5). No scuff px reaches p > 0.1, so the argmax is never scuff at 2k.
  - **Crack predicted on GT scuff px:** B3 490 vs the house S0 checkpoint (same seed, step, data) 617, i.e. −21%. One seed at 2k, descriptive. That fits the label change: 649 scuff px are no longer crack.
  - (S) At this frequency and with no class weight (spec: none, one change), B3 v0 may never predict scuff at argmax by 20k. Its effect would then come from removing the "scuff = crack" labels, not from a learned scuff class. The spec's mechanism ("explicit streak = scuff target") is weaker than written.
  - Reporting the train-cell scuff IoU and p(scuff) at 20k is descriptive. A class weight or Dice on scuff would be a separate, pre-registered arm (coach's call).
- **Coach ruling (1 Nov):** B3 runs as spec'd (one change, no class weight). The 2k numbers go into protocol_thin_b3 §8. At 20k, per seed on the 12 train scuff cells:
  - scuff IoU (pre-stated: < 0.10 = not learned);
  - mean p(scuff) on GT scuff vs elsewhere;
  - crack px on GT scuff vs the comparator.
  A weighted / Dice-on-scuff B3 is a separate later arm with its own OK; I draft a one-paragraph spec only if B3 reads "not learned".
- **Readout script:** `scripts/b3/scuff_train_iou.py` at **c9bbb02** (md5 **f6d77562**). It writes all three, per cell and pooled, for B3 runs (25 channels) and comparator runs (24 channels; scuff positions from `--scuff-masks`, default masks_escdd_s).
  - Checked on the 2k checkpoints (CPU fp32): B3 crack-on-scuff 490, p(scuff) 1.32e-4 vs 3.17e-5 (ratio 4.16), IoU 0.0; house 617. Equal to the one-off diagnostic. Outputs: `reports/thin/smoke/sti_*.json`.
  - **Score both arms on the same device:** the GPU bf16 smoke gave 501 where CPU fp32 gives 490.

## 10. Distance-map target (third candidate arm): costing
**Variants (S)**
- **V1, auxiliary head:** 1-channel regression head on the decoder output; target = truncated distance to the nearest GT crack px, min(d, τ)/τ, τ ≈ 5-10 px; smooth-L1, weight λ; discarded at inference.
- **V2, boundary loss** (R doi:10.1016/j.media.2020.101851): Σ φ_G · p(crack) with the signed distance map φ_G; for 1-3 px structures mostly a far-false-positive penalty.
- **V3, DDT-style scale classes** (R doi:10.1109/cvpr42600.2020.00389): quantised inside distance + geometry-aware refinement at inference.

**Cost**
- **Code:**
  - V1 ≈ 1 day: target wrapper with EDT in the workers; aux head behind a `model.*` flag so scorers build the same state dict; trainer encoder → decoder → (head, aux) split as in the absh path; tests; CPU identity.
  - V2 ≈ 0.5 day.
  - V3 2-3 days (inference change; every scorer changes).
- **CPU per step (E, gaint, 1 thread, 209 crack masks):** truncated outside EDT 6.6 ms per mask (p95 10.7); SDM 17.2 ms (p95 25.5). That is 50-140 ms per batch over 4 workers.
- **GPU memory and time (S):** one extra 1×1 output channel (V1) or a weighted sum (V2): < 2% step time, < 0.1 GB.
- **GPU-h:** 5 runs × ~2.5 h = 12.5 lane-hours on gaint with 3 lanes sharing the GPU, ≈ 4 GPU-h of whole-GPU time (R34 alone ~7 steps/s, so ~0.8 h per 20k-step run); ~5 h wall if 3 lanes are free. Plus about 0.5 GPU-h of smokes.

**Expected effect**
- **Premise in data (E, masks_escdd train):**
  - inside distance of crack px: 1.0 for **75.5%**, 1.41 for 15.3%, 2.0 for 7.4%; ≤ 1.5 for 90.8%;
  - max inscribed radius ≤ 2 px for 82% of components.
  - So an *inside* distance map (V3, the inner half of an SDM) is almost constant on our cracks.
- **Outside distance (V1)** is a jitter-tolerant proximity target (R doi:10.1109/cvpr.2014.351, Sironi et al.). The closest repo analogue, P14 `tol_dice` (offset-tolerant supervised loss, R = 2), left crack unchanged and recovered 0% of the label-noise gap (E handbook 11, claim 6; `results/p14/README.md`).
- **Literature (R):**
  - Ma et al. MIDL 2020 (openalex:W3018023895): gains on V-Net for 3-D organs, but "not all the methods hold the benefits on different datasets";
  - DDT +1.3 to +8 DSC on multi-voxel CT tubes (aorta, veins, pancreatic duct);
  - further: doi:10.1609/aaai.v34i07.6946, doi:10.1016/j.cviu.2019.102809, arxiv:1908.03679.
- **(S) Test crack IoU −0.005 to +0.010**, below the clean MDE 0.012; relF1@2 n.d.; E1 n.d. (nothing here addresses the domain shift).
- **(S) vs SKR / CLD:** same family (crack-shape supervision). SKR targets recall and CLD targets connectivity; a distance target overlaps both and has the weakest premise on 1-3 px labels.

**Recommendation (S; coach agrees): no third arm now.** It would need the user's OK in any case (Om approved SKR, CLD and B3 only). Revisit if:
- (a) SKR or CLD passes (then V1 is a cheap mechanism follow-up); or
- (b) idea 6 (2× input) is adopted (radii double, inside distances become informative).
- If SKR raises crack false positives (arXiv 2508.11374), V2 is the cheap precision companion.

## 11. Disclosures
- **PF grad clip:** encoder gradients during the PF freeze still enter the global clip norm (as protocol_100). The thin terms add head / decoder gradient, so the clip may bind more often. Logged only with `training.log_grad_norm`.
- **B3 head init:** smp initialises the head with xavier_uniform, whose bound depends on fan_out (25 vs 24 channels), so every head weight differs from the 24-class head, not only the new channel. The encoder (ImageNet) and decoder (initialised before the head) are unchanged. The global RNG position after the build also differs. A grep of the supervised path (trainer, losses, stream, augmentations) found no later global-RNG draw (streams and augmentations use their own seeded generators), so the shift has no downstream effect here (S: seed-like noise in the head only).
- **AP / margins with 25 channels:** p(crack) = softmax over 25 channels; any margin "crack logit − max over k ≠ crack" includes scuff.
- **LA prior:** each arm's own train prior (25 classes for B3).
- **Val loss with SR on:** tubes are computed on the CPU from the val masks (val only at 20k). No effect on training.
- **clDice GT skeleton:** the soft skeleton (paper form) is computed per step on the GPU, not the exact skeleton.
- **clDice on crack-free batches (~1% of batches):** paper form, finite and not 0: it penalises predicted crack-skeleton mass. L_srec is 0 there.
- **masks_escdd_s, ext_scuff, test_scuff** are outside git (`/data/*` is gitignored); manifests above.
- **GPU incident (14:12-14:15):** see `log.md`.
