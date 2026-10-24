# Protocol R5: internal resolution ×2 (input upsampled to 1024, logits pooled back to 512), 100% labels

MD, 24 Oct 2026. Status: **for MC review**. Only the < 1,000-step identity check and smoke before APPROVED.

## What I had seen when writing this
- M0, R1 (verified), R2 (WORSE, draft under MC recompute), the P-cnxt pilot (val only).
- MC's `ideas.md` ranks input upsampling first.
- No R5 run exists.

## Question
Does running U-Net++/ResNet-34 at twice the resolution internally, with labels, losses and scoring unchanged at 512, raise crack recall and IoU at 100% labels?

## Hypothesis
- Cracks are 1.75-2.5 px wide (handbook 13 A5). The ResNet stem halves the resolution before the first skip, and stage 1 quarters it, so a 1-2 px crack survives only in the highest-resolution features.
- At ×2 the same crack is 3.5-5 px inside the network.
- Expected (S): crack recall and relR@2 up, crack IoU +0.00 to +0.02, faint and thin cracks the most. BMRK, the blurriest source with 4-px labels, may gain least. Inactive and large classes about unchanged.
- **Literature:**
  - High-resolution representations matter for position-sensitive tasks (Wang et al., HRNet, `doi:10.1109/tpami.2020.2983686`).
  - Crack work on degraded images couples super-resolution with segmentation (Kondo & Ukita, `arxiv:2302.12491`, via MC's ideas.md).
  - No EL evidence exists.

## The one change
- **Switch:** `model.upsample_input=2` (`el_m` commit `1be64e1`, opt-in). The model becomes `UpsampledInput(core, 2)`:
  - forward: bilinear ×2 on the normalised input → core U-Net++/R34 → `avg_pool2d(·, 2)` on the logits;
  - so the logits are 512×512 again, and the loss (CE + Dice on crack, inactive), metrics, val/test scoring and TTA all stay at 512 against the same masks;
  - default (`upsample_input` absent or 1) returns the plain model; the core init is identical for the same seed.
- **Tests:** `tests/test_m_upsample.py` (3): default = plain model with identical state dict; ×2 keeps output shape with gradient flowing; equals the manual formula. Full suite: 235 passed, 11 skipped.
- **Identity:** the SUP100 config at the new deployment (`el_mt5`, `1be64e1`, switch off), 1,000 steps vs `p16_A_100pct_s3`.
- **Compute:**
  - about 4× FLOPs per forward (measured in the smoke and reported with steps/s and peak memory);
  - same batch (8), same 20,000 steps, same optimizer and schedule.
  - Not changed: batch, crop, steps, LR. If memory forces fewer runs per GPU, that changes speed only.

## Fixed
Everything else as SUP100 (U-Net++/R34 ImageNet, CE + Dice on 14 and 11, labelsafe, batch 8, 20k steps, Adam 1e-3, wd 1e-4, cosine, clip 1.0, bf16, deterministic, split seed 0). Final weights.

## Arms
| Arm | Runs | Seeds | Code |
|---|---|---|---|
| SUP100 | existing | 0-4 | identity-checked |
| R5 | `m_r5_up2_s0..4` | 0-4 | cv02 `/tmp/noob_el/el_mt5` (REVISION `1be64e1`) |

**Opts:** the SUP100 opts + `model.upsample_input=2 training.log_grad_norm=true` (logging only).

## Decision
As protocol_r2/r4, with the same scorer (`m0_audit.py`; its `build_model` reads `upsample_input` from `config_used.yaml`):
- rule 1, 5 v 5, 4 primaries, both cell sets;
- **pass** = passes in both, or passes in one and same-sign n.d. in the other; **worse** on any primary in either set fails;
- stack inclusion on val only (C1);
- multiplicity: 8 tests.

**Named secondaries:**
- crack recall, relR@2 and component recall, with precision;
- BMRK and ARTS crack recall/IoU;
- crack AP per source;
- E1 ext crack recall.

**Reported:** all cell sets, per source, per class, bootstrap, top-3-out, width flags, GPU-h vs SUP100.

## Smoke (< 1,000 steps)
300 steps: finite loss, steps/s, peak memory (nvidia-smi + `torch.cuda.max_memory_allocated` from the log), and the resolved config showing `upsample_input: 2`.

## Compute
- About 4 × 1.1 ≈ 4-5 GPU-h per run, so 20-25 GPU-h for 5 runs.
- cv02 Track M lanes (GPUs 6-7), as memory allows (expected 2-3 per GPU). Ledger before launch.

## Not claimed
- That ×2 is the best factor (×1.5 is untested).
- That gains come from "resolution" rather than from the bilinear interpolation's smoothing. This is one implementation of higher internal resolution.
