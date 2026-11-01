# S10-inactive pre-registration (idea 10; found, 31 Oct 2026)

Written before any S10 number exists.
- **Approval:** judge (CPU-only, descriptive; team-lead's T9 precedent). The user OK'd the sam2 venv and the SAM2.1 Hiera-T weights.
- **Spec:** `idea10_runspec.md`.
- **Design:** `idea10_ai_labelling.md` §6 v2.1.
- **Scope:** no test, no E1, no `_rf`, no training.

## 1. Question
On cells the model did not train on, does SAM2.1 Hiera-T, prompted only by the model's own inactive components, give inactive masks closer to the Pratt labels than the model's masks? Zero human time.

## 2. Cells, labels, models
- **Decision set (OOF):** the 239 train cells outside `splits/seed0/labeled_50pct.txt` (B1's A50 out-of-fold set; 3 D7 twins included, harmless here since no test is read).
  - Labels: `labeled/masks_escdd` class 11 (Pratt 20221008 inactive).
  - Judge's count from the release masks: 22 inactive cells, 142,791 px. The script reports its own count from masks_escdd.
- **Report-only:** val 54 (6 inactive cells, 3 holding 89% of px).
- **Model:** the A50 5-seed ensemble `cv02_noob_el/el_p13/experiments/p16_A_50pct_s0..4`, step 20,000, mean softmax, argmax. Inactive = class 11; no bias (the crack bias does not apply to inactive). Checkpoint md5s are recorded at run time.
- **SAM:** `sam2.1_hiera_tiny.pt` (md5 6aa6761c), config `configs/sam2.1/sam2.1_hiera_t.yaml`, Meta sam2 @ 2b90b9f, venv `/home/noob/work/venv_sam2`, CPU.

## 3. Procedure (`scripts/s10_inactive.py`, md5 e7e9cd04 → A1 version, md5 in log.md)
- **Prompts:** for each 8-connected predicted inactive component ≥ 100 px, its bounding box and its deepest interior point (max EDT), from the model only.
- **SAM:** `multimask_output=True`; keep the mask with the highest predicted IoU; union per cell. Cells without prompts get an empty SAM mask.
- **Variants:** (a) model mask; **(a′) the model mask restricted to its prompted components (≥ 100 px)** (judge A1); (b) SAM mask; (c) a ∧ b.

## 4. Metrics and rule (fixed now)
- **Primary:** pooled inactive IoU over **all 239 OOF cells**, so false positives on cells without GT inactive count.
- **Rule, per variant X ∈ {b, c}:** pass if both hold:
  1. pooled IoU(X) − max(pooled IoU(a), pooled IoU(a′)) ≥ +0.05. Judge A1: a pass cannot come from dropping small components alone;
  2. paired cell bootstrap over the 239 OOF cells (2,000 resamples, seed 0) of X − ref, where ref is whichever of a / a′ is higher on the full set, gives a lower 95% bound > 0.
  - a, a′, b and c are reported side by side.
- **Two comparisons (b, c) are tested with no correction: disclosed.** A pass names which variant passed.
- **Reported, not in the rule:**
  - per-cell IoU on the GT-inactive cells;
  - mean boundary F1 at 2 px on those cells;
  - predicted inactive px on cells without GT inactive;
  - all of the above for val.
- **Kill:** neither b nor c passes. Then drop SAM from the pipeline: model masks alone are pseudo-label SSL, already n.d. at 100%.
- **A pass means:** a thesis-method note ("SAM refines model-proposed inactive regions on unseen cells"). It does not open a training arm by itself (low downstream value, `idea10_ai_labelling.md` §6).

## 5. Run
- gaint CPU: `CUDA_VISIBLE_DEVICES=""`, nice 19, ≤ 8 threads. The script asserts CPU.
- Stages, in order:
  1. `model` (el-fault-detection venv);
  2. `sam` (venv_sam2);
  3. `score`.
- Outputs go to `/home/noob/work/found/s10/`. ~15 min.
- tmux `s10`; PID in `log.md`.
- **Starts only after judge's OK.**

---

## judge review (31 Oct 2026, 17:43 IST from date; prereg md5 6c75e279, script e7e9cd04 as reviewed; no S10 number existed)

**APPROVED, subject to A1.** Write A1 into §3 and §4 and the script before the run. Then S10 may start as in §5.

**A1, a size-matched reference (one-change comparison).**
- SAM is prompted only for model components ≥ 100 px. So (b) also drops every model component < 100 px, and (c) = a ∧ b drops them too.
- A "SAM pass" could then come from removing small components alone, not from SAM.
- Add **(a′)**: the model mask restricted to the prompted components (≥ 100 px).
- The rule's reference becomes **max(IoU(a), IoU(a′))**: X must beat both by ≥ +0.05.
- Run the paired cell bootstrap against whichever of a and a′ is higher.
- Report a, a′, b, c side by side.

**The rest is sound:**
- Pratt-labelled references only (masks_escdd class 11), out of sample for the A50 models.
- Widening the pooled IoU to all 239 OOF cells is better than my 22-cell wording: false blobs on cells without inactive now count.
- The two comparisons are disclosed; val is report-only.
- No test, no E1, no `_rf`, no training.
- The kill is real.
- The venv reuses torch read-only and leaves the el venv unchanged (log 17:41). Team-lead and the user approved the venv and weights.

**Expectation (S):** SAM can sharpen the boundaries of found regions but cannot add missed ones. Most of the inactive IoU loss on unseen cells is in missed or partial regions, so a pass is plausible, but on boundary F1 more than on pooled IoU.

## judge verdict on the S10 result (31 Oct 2026, 18:06 IST from date)

**PASS via (b) SAM confirmed; (c) SAM ∧ model FAILS. Accepted as a method note only, with the caveats below.**

**Reproduced** with my own scorer (`judge/s10_recompute.py`, md5 1fbd16f4, run on gaint CPU).
- **Inputs:**
  - found's `model.npz` (7bf1e049) and `sam.npz` (627fe970);
  - GT from el_f3 `labeled/masks_escdd` class 11;
  - a′ recomputed by me from a's 8-connected components ≥ 100 px.
- **Numbers, all exact:**

  | Variant | pooled IoU | recall | precision |
  |---|---|---|---|
  | a | 0.4925 | 0.542 | 0.842 |
  | a′ | 0.4898 | | |
  | b | 0.5653 | 0.669 | 0.785 |
  | c | 0.4864 | | |

  - b − a = +0.0728, bootstrap [+0.013, +0.135];
  - c − a = −0.006;
  - FP px on the 217 no-GT cells: 2,120 → 2,711.
- **Added by me:**
  - leave-top-3-GT-cells-out (they hold 48% of GT px): b − a = **+0.056**, so the gain is not carried by 3 cells;
  - per cell, b beats a in 10 of 22 GT cells and loses in 5.

**Caveats (S):**
1. **SAM is an expander here, not a sharpener.** Recall rises +0.13, precision falls −0.06, boundary F1 is flat (0.356 → 0.349).
   - It helps where the A50 model under-segments inactive regions. A 100%-label model (BEST) may under-segment less, so the gain may shrink there.
   - The test was on A50 by design (out-of-fold), so this is untested at 100%.
2. **Val goes the other way:** 0.442 → 0.402, report-only, 6 inactive cells. It does not overturn a pre-registered pass, but it is the reason the note must say "on the 239-cell OOF set".
3. **Two comparisons, uncorrected.** b's bootstrap lower bound (+0.013) would likely survive a 2-way correction; that is not tested.
4. **Wording:** "Prompted by the model's own inactive components, SAM2.1 Hiera-T raises pooled inactive IoU on unseen train cells (+0.07, A50 models), by extending under-segmented regions at a precision cost. It does not sharpen boundaries." No training arm follows (idea 10 §6). The scuff half stays PARKED.
