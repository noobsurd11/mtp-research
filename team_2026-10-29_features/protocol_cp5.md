# Protocol CP5: crack copy-paste onto unlabelled backgrounds, 5% labels (v0, draft)

runner, 29 Oct 2026. Status: **v1, APPROVED by coach** (`review_ddep5_cp5_v0.md`: P1 held-out accepted, P2 disclosed, P3 code fix applied in `2751aa8`). Launch after the identity runs, smoke and decoy go/no-go; never ahead of MIM5. Implements `spec_cp5.md` v1.1 (APPROVED as spec, `review_spec_cp5_v1.md` E1-E6). Same machine (gaint), shared A5c-f1, same rule family as MIM5/DDeP5.

## What I had seen when writing this
- spec_cp5 v1.1, coach's review, MIM5/DDeP5 protocols; the CP library recount and 32 preview composites (no model output).
- No CP training step has run. No MIM5 or A5c-f1 fine-tune number opened.

## Question
At 5% labels, does adding a stream of unlabelled backgrounds carrying pasted labelled crack components (crack / not-crack loss on paste and ring only) raise test crack scores beyond what the crack prior shift alone (logit adjustment) gives?

## Arms
| Arm | Change | Runs | Seeds |
|---|---|---|---|
| **A5c-f1** (shared) | none | `f1_A_5pct_s0..4` (gaint, 603e0d5) | 0-4 |
| **CP5** | `cp` stream, λ 1 | `f2_CP_5pct_s0..4` | 0-4 |

- CP5 opts: A5c verbatim + `cp.lambda=1.0 cp.batch=4 cp.bg_pool_list=/home/noob/work/el_f1/reports/f1/mim_pool_v11.txt cp.heldout_list=/home/noob/work/el_f1/reports/f1/mim_monitor_v11.txt cp.bg_train_exclude=data/splits/d7_twin_train_cells.txt` (defaults: `p_pool 0.5, kmax 3, tries 50, ring_min 30, min_area 20, min_contrast 3`).
- The labelled stream, its augmentation, BN statistics (the CP forward runs inside `frozen_bn_stats`), optimizer, schedule and evaluation (the model at step 20,000, no EMA) are A5c's.

## Code
gaint `el_f2`, branch `f2`, **deploy commit `2751aa8`** (train path = `42bf7d1`; later commits add `scripts/cp_decoy.py`, `scripts/am_map.py` and the P3 fix: the residual is 0 on other crack px inside T, so a nearby fragment cannot carry crack darkness into the ring or ignore band; test added; suite 278 passed). `src/data/copy_paste.py` (library, residual transfer, placement, targets, `cp_loss`), trainer hook (stream id 3; λ 0 or no `cp` section: no forward, no draw, no log keys), `scripts/cp_preview.py`, `scripts/cp_decoy.py`. Suite 277 passed, 3 skipped; 7 CP tests (spec §7.2 / E2): library exclusions and residual sign; dihedral exactness of M, T and residual footprint; target zones (1 only on M, 0 on the 1 px band, 2 only on dilate(M,6) minus dilate(M,1), 0 elsewhere), placements inside the eroded cell area, ring median ≥ 30, only T pixels change; dark-ring rejection; determinism per seed; loss formula.

## Library (E6 recount on the server masks, frozen here)
- 23 labelled cells (`seed0/labeled_5pct.txt`, md5 `b4f6c78c...`), `labeled/masks_escdd`. 41 crack components ≥ 20 px; dropped: edge ring 7, inactive ring 8, contrast < 3 GL 6; **kept 20, 11,978 px** (CFVS 13, CSIR 4, BMRK 2, ARTS 1). Kept list `el_f2/reports/f2/cp_preview/cp_library_kept.tsv`, md5 `1c833a6c220412b41731d510d2e8332e`.
- Scout's local count was 17 / 11,819 px: +3 components, +1.3% px, inside E6's tolerance (> 3 components or 20% px). Disclosed (P2): one ARTS component (`ARTS_00051_r6_c2`, 47 px, contrast 42 GL) is kept. The server mask has 47 crack px in this 5% cell, so "ARTS has 0 labelled crack cells at 5%" (why-SYNTHESIS §1) is wrong on these masks (coach verified 9 crack cells at 5%); flagged to team-lead by coach.

## Backgrounds
- (a) pool part of `mim_pool_v11.txt`: 11,219 cells (list md5 `f0a5d74a...`, R1-R4 already applied).
- **Held-out (E4):** the 256 cells of `mim_monitor_v11.txt` (md5 `4a09f598...`): pool cells drawn by a fixed seed (0) from the same R1-R4-filtered pool part, never backgrounds, used only for the decoy control. They are also outside MIM pretraining. Accepted by coach (P1).
- (b) `seed0/unlabeled_5pct.txt` (455, md5 `520c9bb1...`) minus the 7 D7 twins: 448.
- 50/50 between (a) and (b), uniform within each, per item from the item seed.

## Composition, targets, loss (spec §2-6, as implemented)
- Residual r = src − bg on T = dilate(M, 2), bg by normalised Gaussian convolution (σ 3); new = clip(round(tgt + s·r)), s = clip(sd_tgt / sd_src, 0.5, 2), robust sds on R8 rings; dihedral + integer translation only.
- Placement: K ~ U{1,2,3}; dilate(M, 6) inside the cell area (grey [15, 245], 5x5 opening, largest component, eroded 10 px) and clear of earlier pastes; target ring median ≥ 30 GL; ≤ 50 tries per component; a background with no placement is redrawn. Dilations are Euclidean.
- Targets: crack on M, ignore on the 1 px band, not-crack on the 2-6 px ring, ignore elsewhere; label-safe augmentation applied jointly.
- Loss: CE + Dice (labelled, unchanged) + λ · (Σ_crack −log p14 + Σ_ring −log(1 − p14)) / N_lab, λ = 1, fp32; no Dice on the stream.
- Preview (32 composites, seed 0): placed 1.88 per image (1-3), crack px 1,130 (42-3,826), ring px 3,003, s 0.97 (0.5-2.0), target ring median 148 GL, 0 background redraws, 14 of 32 from the pool. Expected crack px per step ≈ 4 x 1,130 ≈ 4.5k vs ≈ 6.2k labelled.
- Logged every 50 steps: `loss_cp, cp_crack_px, cp_ring_px, cp_p14_crack, cp_p14_ring, cp_fails, cp_s, cp_ring_med`.

## Checks before launch (gaint; smoke ≤ 2,000 steps)
1. **Identity (E5):** commit 2751aa8 with no `cp` section, seed 0, 2,000 steps, reproduces `f1_A_5pct_s0`'s stdout (loss, lr, val lines) bit-identically; and with the `cp` section at λ = 0, 1,000 steps, the same. Only then CP5 shares A5c-f1; otherwise A5c is re-run at c60d6e8. The 2,000-step no-switch run also leaves the A5c step-2,000 checkpoint for check 3.
2. **Smoke:** CP5 seed 0 at λ 1 to step 2,000: finite losses, `cp_*` logs as above, samples/s and memory.
3. **Decoy go/no-go (E3a):** `scripts/cp_decoy.py` on the 256 held-out cells (19 of 20 components have a crack-free decoy spot; placements identical between real and decoy composites, asserted): crack rate on M for real, decoy and untouched background, CP smoke step 2,000 vs A5c step 2,000. **Flag** if CP's decoy rate > 2x A5c's or > 0.05 absolute: then no launch, report to coach.
4. Decoy diagnostic on the five final checkpoints of both arms (E3b), reported, same thresholds.

## Contrasts and rule (spec §8, E1)
- LA: `scripts/rescore_logit_adjust.py`, z_c − τ·log π_c, π from the run's own 23 labelled cells (pastes not counted), τ ∈ {0, 1}.
- C1: CP5 − A5c-f1 at τ 0. C2: (CP5+LA) − (A5c-f1+LA) at τ 1. C3: CP5 (τ 0) − (A5c-f1+LA) (S-a yardstick, reported).
- Rule 1 (house divisor 3; /5 descriptive), three primaries, verdict on all 50 and without `CSIR_00070_r8_c4` (two-set rule as MIM5); without twins / without both reported.
- **Crack claim:** C1 BETTER on crack IoU or relF1@2 and C2 BETTER on the same primary, worse on none, under the two-set rule. Width flag: crack relP@2 drop > 0.05 in C1.
- **Kill:** C1 n.d. on crack IoU and relF1@2, or C2 not BETTER on either, or the width flag: CP closed at 5%, no 100% arm.
- Pre-stated expectation (S, spec): C1 crack +0.01 to +0.03; C2 −0.005 to +0.025, n.d. likeliest; inactive n.d.; crack precision −0.01 to −0.04.
- Multiplicity: 3 contrasts x 3 primaries x 2 sets, plus MIM5 and DDeP5 against the same A5c-f1; no correction, disclosed.
- Secondaries: per source crack IoU and relR@2 (ARTS, BMRK, CFVS, CSIR); crack px on crack-free test cells; E1 crack recall split scuff + half-cut / other (descriptive).

## Compute and machine (team-lead amendment, 29 Oct)
About 1.5x an A5c run per seed (spec §9). Default gaint against A5c-f1, after the MIM5 fine-tunes are under way, each run gated on own peak + 2 GB free. If 3 or more cv02 GPUs free before CP5 is ready, CP5 + DDeP5 + a fresh A5c run on cv02 (one commit, identity there); the choice is written here before launch.


**Machine decision (19:50 IST, before launch):** **gaint** against A5c-f1 (cv02 had 1 free GPU). E5 identity passed: no switch IDENTICAL for 2,000 steps, λ = 0 IDENTICAL for 1,000 steps (identity_f1.txt §5). Lanes (`=f2g`): the CP smoke (2k) and decoy go/no-go run in lane X after the MIM5 lane M2 ends; CP5 s0/2 in lane Y after DDeP5 s1/3, CP5 s1/3/4 in lane Z after the A5c-f1 lane ends, only if the decoy check writes CP_PASS (flag: CP decoy rate > 2x A5c's or > 0.05). Every start waits for its own peak + 2 GB free (12 GB for CP).

## Not claimed
- Anything at 100%. Shape diversity (20 mostly-CFVS components). Anything about E1 scuff + half-cut.
