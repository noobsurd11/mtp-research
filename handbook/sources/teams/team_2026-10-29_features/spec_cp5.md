# spec_cp5: crack copy-paste onto unlabelled backgrounds, 5% labels (v1.1, scout, 29 Oct 2026)

**Status: APPROVED by coach as the spec runner implements** (`review_spec_cp5_v1.md`); v1.1 folds in coach's edits E1-E6. The launch gate is `protocol_cp5.md`, its diff and its smoke.

Goal: tight enough for runner to implement without design choices left open. Every choice marked (S) is judgement; coach may change any of them before `protocol_cp5.md` is written. Tags: E measured (path), R literature (Research MCP id), S judgement.

## 0. What the arm is (one change vs A5c)
CP5 = A5c exactly (smp U-Net++, ImageNet R34, CE + Dice, labelsafe, Adam 1e-3, wd 1e-4, 200-step warmup + cosine, 20k steps, batch 8, 512 px, bf16, final-step weights, `masks_escdd`, fraction 0.05, split seed 0) **plus** a second stream of 4 unlabelled backgrounds per step, each carrying 1-3 pasted labelled crack components, trained with a crack / not-crack loss on the paste and a thin ring only. Nothing else changes: no EMA teacher, no pseudo-labels, no change to the labelled stream.

## 1. Paste source (the library)
- **Cells:** the fraction's labelled cells only (5%: `splits_benchmark/seed0/labeled_5pct.txt`, 23 cells). Masks from the training mask dir the arm uses (`labeled/masks_escdd`), never from val/test/E1.
- **Components:** 8-connected components of crack (id 14), area ≥ 20 px.
- **Exclusions** (computed on the source cell's own mask and image):
  1. ring touches inactive: more than 20% of the source ring R8 = dilate(M, 8) \ dilate(M, 1) is class 11 (inactive-edge cracks carry the region's darkness into the residual);
  2. R8 touches padding (7), frame edge (21) or border (5) (residual would carry the cell edge);
  3. crack contrast < 3 GL, contrast = median(source grey on R8 \ crack) − median(source grey on M) (a non-dark label would teach "crack = nothing visible").
- **No inactive pastes** in this arm. Inactive regions are bounded by cracks and cell edges, so a free paste is implausible, and CP5 tests crack only. An inactive variant is a separate arm.
- **Expected size (E, local E-SCDD masks, `scripts/scout/cp_library_stats_out.txt`; all 23 cells found locally, but locally 8 have crack vs 9 in `handbook/03` §4.2, so recount on the server masks):** 37 components ≥ 20 px in 8 crack cells; 22 pass exclusions 1-2; 17 also pass 3, 11,819 px, mostly CFVS (BMRK 2 kept, ARTS 0 crack cells at 5%). Component size median 208 px, p90 1,153; bbox extent median 61 px, max 234. Crack contrast median 5.5 GL at 5% (13.0 GL over the 466 non-twin train cells with a local mask); ring texture robust sd median 19.3 GL. **[Correction 29 Oct: ARTS has 1 labelled crack cell at 5%, not 0: `ARTS_00051_r6_c2`, 47 crack px on the server masks (coach, `review_ddep5_cp5_v0.md` P2; team-lead commit 882f929). The local E-SCDD mask has 0 crack px for that cell, which is the 8 vs 9 crack-cell difference.]**
- **Precompute once per run** (deterministic, CPU): for each kept component store the crop of `M`, the residual `r` on `T = dilate(M, 2)`, and the source ring robust sd `sd_src` (1.4826 × MAD of grey on R8 \ crack). Write the library list (stem, component id, px, contrast) and its md5 into the protocol.

## 2. Residual (blending)
- **Source background estimate** (normalised convolution, no inpainting library needed): E = dilate(M, 2); `bg = G * (src · (1 − E)) / G * (1 − E)`, G a Gaussian with σ = 3 px; computed on the grey uint8 source as float.
- **Residual:** `r = src − bg` on T, 0 elsewhere. Keep its sign.
- **Transfer:** at the chosen location in the target, `new = clip(round(tgt + s · r), 0, 255)` on T, with `s = clip(sd_tgt / sd_src, 0.5, 2.0)`, `sd_tgt` = 1.4826 × MAD of the target grey on the target's own ring at that location.
- This moves the crack's darkness, not the source's pixels: the target's fingers, grain and brightness stay, so no seams; the line cannot come out brighter than its surroundings unless the source label was (filtered by exclusion 3).
- **No Poisson blending, no alpha.** Poisson gave no gain over direct paste in Synth4Seg (R [F] doi:10.1109/tase.2025.3583713 §III-A); residual transfer is stricter than direct paste.
- **Label-safe:** the component geometry is moved by integer translation and one of the 8 dihedral transforms (h/v flip, 90° rotations) only. No scaling, rotation by other angles, blur or warping, so a 2 px label stays exactly on its 2 px line.

## 3. Backgrounds
- **Lists:**
  - (a) the pool part of the final MIM image list (`coach_mim5.md` §B: pool minus val/test/E1 modules, ext117 stems, near-duplicates of val/test/ext117 and of the 7 twins), **minus** CP's own 256 held-out pool cells (E4): drawn from that pool part with a fixed seed, never used as backgrounds, used only for the decoy control (§7.5); list and md5 in the protocol;
  - (b) the fraction's unlabelled train cells (`seed0/unlabeled_5pct.txt`, 455) minus the 7 D7 twins.
  - Never the 23 labelled cells (their full labels exist; keep one label rule for the stream), val, test or E1.
- **Sampling:** 50% from (a), 50% from (b), uniform within each (S: (b) is i.i.d. with test and holds the CFVS/BMRK/SDLE contexts the pool lacks; uniform over the union would make (b) 4%).
- **Cell area (no masks used for backgrounds):** grey in [15, 245] → binary open with a 5×5 square → largest connected component → erode by 10 px. A placement is valid only if dilate(M, 6) of the placed component lies inside this area.
- **Dark-target rule:** reject a placement if the target ring median < 30 GL (inactive areas, busbars, dark edges: the pasted line would be invisible and become label noise).
- **No busbar avoidance** (S): real cracks cross fingers and busbars; avoiding them would teach "no crack on a busbar". Source rings never touched a labelled busbar (E, 0 of 37 components).
- State both list sizes and md5s in the protocol.

## 4. Sampling per image
- Every stream image gets pastes (p = 1). K ~ uniform{1, 2, 3} components, each drawn uniformly from the library (with replacement), each with a uniform dihedral transform.
- Location: uniform over valid placements; up to 50 tries per component; components must not overlap: the new dilate(M, 6) must not intersect earlier ones. If no component of an image can be placed, draw a new background (same RNG stream, next index).
- Expected crack px per step (S, from §1 sizes): 4 images × 2 components × ~695 px ≈ 5.6k, against ~6.2k crack px in the labelled batch (8 × 262k px × 0.295%). So the stream roughly doubles crack positives per step. This is the prior shift §8 controls for.
- Determinism: background choice, K, components, transforms and locations are a pure function of (seed, stream id 3, index), like `stream.py` (stream ids 0-2 are taken by labelled, unlabelled and CutMix; runner confirms the free id).

## 5. Targets and ignore
Per stream image a uint8 target map:
- 1 = crack: M (the placed component's own label pixels);
- 0 = ignore: dilate(M, 1) \ M (label width uncertainty, consistent with the 2 px relaxed metrics);
- 2 = not crack: R6 = dilate(M, 6) \ dilate(M, 1) (ring, 2-6 px from the label);
- 0 = ignore: everything else (backgrounds carry unlabelled real cracks, about 0.19% of px; a full background label would teach misses).
Ring overlap with an unseen real crack is label noise at roughly 0.2-0.4% of ring px (S); accepted.

## 6. Loss, BN and augmentation
- **Augmentation of the stream:** compose first, then apply `get_labelsafe_augmentation` to (image, target map) jointly; flips and rot90 are exact on the map; brightness/contrast acts on the image only.
- **Forward:** a separate student forward for the 4 stream images inside `frozen_bn_stats` (the P13 `student_forward=separate` mechanics), so labelled BN statistics evolve exactly as in A5c.
- **Loss:** `L = CE_lab + Dice_lab + λ · (Σ_{t=1} −log p14 + Σ_{t=2} −log(1 − p14)) / N_lab`, p14 = softmax crack probability (fp32), N_lab = number of valid (non-ignored) pixels in the labelled batch, **λ = 1**. A stream pixel then weighs exactly as one labelled pixel in the CE mean. No Dice on the stream (Dice is a batch-level ratio and would let 4 pasted images dominate it).
- λ = 0 must skip the stream forward entirely and draw no RNG from the labelled stream.
- **Evaluation:** the model itself at step 20,000, as A5c (no EMA teacher).

## 7. Checks before launch (smoke ≤ 2,000 steps)
1. **Identity (E5):** on the run machine, the CP commit with the switch absent, and again with λ = 0, reproduces A5c-f1's stdout bit for bit for 1,000 steps. Only then may CP5 share A5c-f1 and its seeds; otherwise A5c is re-run at the CP commit. This proves the wiring, not the paste code.
2. **Unit tests for the paste code (E2, CPU):**
   - dihedral and translation exactness: label footprint and residual footprint coincide pixel for pixel after every transform;
   - target-map values per zone: 1 only on M, 0 on the 1 px band, 2 only on R6, 0 everywhere else;
   - determinism per (seed, stream id, index);
   - every placement inside the cell-area mask (dilate(M, 6) included);
   - no placement whose target ring median is < 30 GL.
3. **Library recount on the server masks (E6):** print the kept list and md5. If it differs from §1 by more than 3 components or 20% of px, write the new numbers into the protocol before any run. The kept list and md5 are frozen there. (Locally all 23 cells were found, but 8 had crack vs 9 in `handbook/03` §4.2.)
4. **Visual (smoke):** one PNG of 32 stream samples (background, composed image, target map in 3 colours), plus the per-step log: pasted crack px, ring px, failed placements, target ring median, s distribution.
5. **Decoy control (E3)**, run twice with the same flag thresholds: (a) go/no-go at the smoke checkpoint (step 2,000) vs an A5c-f1 step-2,000 checkpoint of the same seed; (b) as a reported diagnostic on the five final (20k) checkpoints of both arms, since a shortcut can appear after 2k. Procedure: on the 256 held-out pool cells, paste (i) real components as in training and (ii) decoys: the same mask shape M with a residual taken from a crack-free spot of the same source cell (same §2 recipe, no crack inside). Report the fraction of M px with argmax crack for (i) and (ii), for both checkpoints. Flag a shortcut if CP's decoy rate exceeds 2× A5c's decoy rate or 0.05 absolute.
6. Loss logging every 50 steps: `loss_sup`, `loss_cp`, `cp_crack_px`, `cp_ring_px`, `cp_p14_mean_on_crack`, `cp_p14_mean_on_ring`.

## 8. Logit adjustment and the decision rule
Pasting adds crack positives, which shifts the crack prior. Logit adjustment does that for free (A5c+LA τ = 1: crack 0.319, +0.0154 over A5c; `results/sk1/la_sa.md` §1). So:
- **LA definition:** `scripts/rescore_logit_adjust.py`, z_c − τ·log π_c, π from the run's own **labelled** cells only (pastes are not counted), τ ∈ {0, 1}.
- **Contrasts (5 v 5, rule 1 with the house divisor 3; /5 descriptive only; three primaries: test crack IoU, crack relF1@2, inactive IoU):**
  - C1: CP5 − A5c at τ = 0;
  - C2: (CP5 + LA) − (A5c + LA) at τ = 1, matched bias;
  - C3: CP5 (τ = 0) − (A5c + LA, τ = 1), the S-a yardstick.
- **Verdict sets (E1):** all 50 cells and without the noisy cell `CSIR_00070_r8_c4`. Two-set rule as MIM5: pass on both, or on one with a same-sign n.d. on the other; worse on either fails. The other two cell sets (without twins, without both) are reported.
- **Crack claim** requires C1 BETTER on crack IoU or relF1@2 **and** C2 BETTER on the same primary, worse on none, under the two-set rule. C3 is reported, not decisive. BsM5 (0.331) stays a reported yardstick.
- **Width flag:** crack relP@2 drop > 0.05 in C1.
- **Secondaries:** per source (ARTS, BMRK, CFVS, CSIR) crack IoU and relR@2; crack px predicted on crack-free test cells; E1 crack recall split scuff + half-cut / other, descriptive only, no claim (the scuff + half-cut gap is a missing context no paste of these 17 components supplies).
- **Pre-stated expectation (S):** C1 crack IoU +0.01 to +0.03; net of LA (C2) −0.005 to +0.025 (coach), so n.d. on C2 is the likeliest outcome; with 17 mostly-CFVS components any gain must come from backgrounds, not shape diversity (crack threshold about 0.015 with A5c sd 0.008, `coach_mim5.md` §F); inactive n.d.; precision −0.01 to −0.04.
- **Kill:** C1 n.d. on crack IoU and relF1@2, or C2 not BETTER on either, or the width flag. Then CP is closed at 5% and not run at 100%. Variants (CP-pre, inactive paste) only if C1 passes and C2 is n.d. with the same sign.
- **Multiplicity:** 3 contrasts × 3 primaries × 2 sets; shared A5c with MIM5 and DDeP5 if they run on the same commit and machine.

## 9. Cost
Per step 8 + 4 images forward/backward ≈ 1.5× A5c compute (S): about 1.6 GPU-h per seed on an A6000, about 8 GPU-h for 5 seeds, plus A5c 5 seeds (5.5) if not already shared. Library precompute: seconds on CPU.

## 10. Evidence
- Cut&Paste vs global aug, U-Net R18-ImageNet, MVTec textures, 3 seeds: defect IoU +0.05 to +0.10; learned paste locations up to +18% vs random; Poisson no gain (R [F] doi:10.1109/tase.2025.3583713).
- Crack masks pasted onto new concrete backgrounds, as pretraining: F1 76.1 → 92.3 and 88.6 → 90.6 (R [A] doi:10.1111/mice.12844).
- Copy-paste for rare classes: LVIS rare +3.6 mask AP (R [A] doi:10.1109/cvpr46437.2021.00294).
- Ours: CutMix was the only perturbation with a crack signal (+0.010 over cells), and the 5% SSL crack gain was −0.030 on ARTS, which has no labelled crack cell at 5% (E, `team_2026-10-24_why/SYNTHESIS.md` §1-2). **[Correction 29 Oct: ARTS has 1 labelled crack cell at 5%, not 0: `ARTS_00051_r6_c2`, 47 crack px on the server masks (coach, `review_ddep5_cp5_v0.md` P2; team-lead commit 882f929). The local E-SCDD mask has 0 crack px for that cell, which is the 8 vs 9 crack-cell difference.]**

## Changelog
- v1: scout. v1.1: coach's APPROVED edits E1 (two verdict sets: all 50, without noisy cell), E2 (paste unit tests), E3 (decoy control at 2k and at 20k on both arms), E4 (CP's own 256 held-out pool cells), E5 (A5c-f1 sharing only after bit-identity at the CP commit), E6 (server recount gate); expectation net of LA. Loss normalisation stays / N_lab (agreed in the review).
