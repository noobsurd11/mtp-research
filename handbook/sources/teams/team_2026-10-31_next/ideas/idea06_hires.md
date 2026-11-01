# Idea 6: higher input resolution / HR branch (found, 31 Oct 2026)

Om's idea 6: cracks are 2-3 px and the encoder downsamples heavily, so train at 2x or add a high-resolution skip path; check the current input size and memory. Tags: E measured (file), R literature (Research MCP id), S judgement. CPU / read-only; no GPU job, no test cell read.

**v2, 31 Oct 14:18 IST (log.md):** judge's three corrections applied (E1 width ~1.5x; §3 band reading; the stride-2 reading tagged S). The verdict is unchanged and judge agreed with it.

**Files (md5):**
- `found_scripts/crack_resolution.py` b7a05fa4, output `crack_resolution.txt` 53e62e76;
- memory ratio: scratchpad `mem_check.py` (gaint CPU via stdin, output quoted in §1; not reproduced by judge; the DROP does not depend on it).

**Verdict proposed: DROP as a standalone arm (both 2x and HR-skip).**
- The 2x arm was already run (Track M R5): n.d., val EXCLUDE, at 4x compute.
- The masks show the existing stride-2 skip still holds the crack signal.
- E1 cracks are labelled wider than train cracks (about 1.5x), and the E1 failure is context (scuff + half-cut), not thinness.
- **Keep the HR-skip only as a part of idea 8's hierarchical encoders,** which lack a stride-2 stage and need a stem for U-Net++.
- Park a standalone HR-skip until the thin-crack loss arms show a localisation limit (§6).

## 1. Current input, strides, skips, memory (E)
- **Input:** 512×512 grayscale, normalised (0.5, 0.25), batch 8, bf16 autocast (`configs/base.yaml`; handbook 14 §2.2).
- **Encoder:** smp U-Net++ / ResNet-34 (gaint CPU build, `timm` 1.0.30, smp 0.5.0). Feature strides 2 / 4 / 8 / 16 / 32 with 64 / 64 / 128 / 256 / 512 channels:
  - conv1 7×7/2 gives the stride-2 map;
  - maxpool + layer1 give stride 4.
- **Decoder skips:** encoder maps at 1/2, 1/4, 1/8, 1/16. The nested blocks run at 1/16 down to 1/2 (`x_0_3`, `x_1_3`, `x_2_3`, `x_3_3` at 256², 32-64 ch).
  - **The full-resolution block `x_0_4` (512², 16 ch) has no skip.** It sees only the upsampled 1/2 features.
  - So the finest image information reaching the head is conv1's stride-2 map.
- **Memory:**
  - **Measured on gaint (handbook 14 §1.2c; `protocol_100.md` gate 7):** 6,442 MiB reserved per fine-tune; start gate 9,000 MiB; CP run 9,524 MiB; root's finllm 5,876 MiB.
  - **Budget:** 32,623 − 5,876 − 2,048 = **24,699 MiB** for all our jobs together.
  - Activation memory saved for backward (gaint CPU, fp32, batch 1, `saved_tensors_hooks`): 1,118 MiB at 512 px vs 4,172 MiB at 1024 px, **ratio 3.73**. Weights + grads + Adam: 398 MiB (26.08M params).

## 2. How much crack survives each stride (E, `ideas/found_scripts/crack_resolution.py` → `crack_resolution.txt`)
Masks are `masks_escdd` (train 478, val 54), copied read-only from gaint `el_f3/data/labeled/masks_escdd`. E1 rows are descriptive (ext117 masks, ignore removed). Column meanings:
- **lost:** share of GT crack px whose s×s block is < 50% crack (a block-level majority vote drops it);
- **< 25%:** share whose block is < 25% crack (area or bilinear downsampling dilutes it below a quarter);
- **ceilIoU:** IoU of a perfect block-level predictor upsampled by nearest;
- **merged:** share of crack components (≥ 5 px, 8-connected) that share a block-level component with another.

| Set | Stride | lost | < 25% | ceilIoU | merged |
|---|---|---|---|---|---|
| train | 1/2 | 0.079 | 0.000 | 0.637 | 0.225 |
| train | 1/4 | 0.428 | 0.085 | 0.375 | 0.574 |
| train | 1/8 | 0.881 | 0.350 | 0.219 | 0.744 |
| train | 1/16 | 0.991 | 0.707 | 0.135 | 0.790 |
| val | 1/2 | 0.070 | 0.000 | 0.647 | 0.117 |
| val | 1/4 | 0.395 | 0.078 | 0.382 | 0.531 |
| val | 1/8 | 0.896 | 0.313 | 0.221 | 0.656 |
| E1 half-cut 58 (descr.) | 1/2 | 0.057 | 0.000 | 0.708 | 0.206 |
| E1 half-cut 58 (descr.) | 1/4 | 0.270 | 0.073 | 0.446 | 0.476 |
| E1 half-cut 58 (descr.) | 1/8 | 0.829 | 0.229 | 0.246 | 0.875 |

- **Crack width** (2·EDT on the skeleton, floor 2 px): train median **2.0** (p75 2.83, p90 4.0); val the same; **E1 median 4.0** (p90 4.47), half-cut and full alike.
- **Reading (S):**
  - **(S) Label geometry, not feature capacity.** At stride 2, 92% of train crack px are a majority in their 2×2 block and none is diluted below 1/4. The nearest-upsampling ceiling (0.64) is above FINAL's clean crack IoU (0.492).
    - But conv1's stride-2 map is a single 7×7 conv, and the semantic decision is made at stride ≥ 4 (judge).
    - So this is a ceiling argument only. **The DROP rests on R5 (E, §3).**
  - It is also above the labelling ceiling: one cell labelled twice agrees at 0.53; a perfect detector 1 px off scores 0.48-0.60 (handbook 18 §U, `team_2026-10-27_unlabelled/eval.md`).
  - The signal is lost from stride 4 down, where the semantic decision is made. A 2x input moves every stage one octave finer, which is what R5 did.
  - E1 cracks are labelled **about 1.5x as wide** as train cracks: area / skeleton length 3.66 vs 2.41 px (judge, `judge/crack_width.py` md5 87f57a58). The 2·EDT medians above are quantised (2.0, 2.83, 4.0). Whether the width is a convention or real, E1's misses are not thinner cracks: they are the scuff + half-cut context (handbook 18 §U; 75% of E1 crack px, FINAL recall 0.126).

## 3. Prior tries (E)
- **Track M R5, 2x internal resolution** (input 1024 bilinear, logits avg-pooled to 512; `team_2026-10-24_go/trackM/protocol_r5.md`, `results_r5.md`, `verify_r5.md`; handbook 18 §M5):
  - **n.d. on all four primaries, both sets; val EXCLUDE.** Clean crack −0.0046 (thr 0.0100); mIoU_rob −0.0113, bootstrap [−0.022, +0.000].
  - The rung's own target got worse: confident misses (GT crack at p < 0.001) on test 0.189 → 0.208.
  - E1 crack recall 0.178 → 0.204 (+0.026, descriptive), the same pattern as RN50 (+0.036) and RN50-5 in D (+0.060).
  - 591.9 vs 148.0 GFLOPs (4.0x); about 4.2 GPU-h per run on an A6000, 1.296 steps/s almost alone (`r5/m_r5_up2_s4.stdout`). Ran 2 lanes per 49,140 MiB A6000 (`trackM/log.md` l.22), so ≤ ~24.5 GB per run.
  - Ran under the house optimizer (encoder erasure, `coach_100.md` §0). Under PF it is untested.
- **Strict IoU sits at the labelling ceiling.**
  - FINAL: clean crack IoU 0.492, but relF1@2 0.897.
  - One cell labelled twice agrees at 0.53; a perfect detector 1 px off scores 0.48-0.60 (handbook 18 §U; handbook 11 row 21).
  - The loss within 2 px is label jitter, which resolution cannot fix. With R5's worse confident misses, this is the E that resolution is not the binding limit.
  - (Corrected per judge: the +0.007 inactive-edge band re-score at A100 (handbook 18 §D2) concerns crack near inactive only, and P14 ran at 10%. Neither speaks to localisation in general.)
- **No controlled HR-skip contrast was ever run.**
  - The old-era from-scratch U-Net++ (`unetpp`, 4.98M params) had a full-resolution stage. The early poster names a "full-resolution skip for 2 px cracks" (handbook 06 l.105).
  - It was replaced at P6 by smp U-Net++ / ImageNet R34, which has no 1/1 skip. That change bundled init, encoder and skips, so it does not isolate the skip (handbook 14 §2.5).
  - A grep of `trackM/` and `team_2026-10-29_features/` finds no HR-skip arm.

## 4. Literature (R)
- **R5's protocol cited:**
  - HRNet (doi:10.1109/tpami.2020.2983686): high-resolution representations for position-sensitive tasks;
  - super-resolution coupled with crack segmentation on degraded images (doi:10.1109/tim.2024.3374293; preprint arxiv:2302.12491).
  - No EL evidence.
- **Thin-structure work that does help** pairs resolution with topology-aware losses or conv adapters, not resolution alone:
  - TopoLoRA-SAM (arxiv:2601.02273): conv adapter + clDice;
  - a plug-in adapter for curvilinear segmentation (doi:10.1007/978-3-032-37627-5_22).
- **Skeleton Recall and clDice** (doi:10.1007/978-3-031-72980-5_13, doi:10.1109/cvpr46437.2021.01629) are already approved as arms (om §A).

## 5. Costs on gaint (budget 24,699 MiB)
| Arm | Memory per run (S, from E ratios) | Fits | Time | 5 seeds |
|---|---|---|---|---|
| **2x input (R5 again, on SUP100-PF)** | activations ~5.5 GB × 3.73 ≈ 20.5 GB + ~1 GB = **~21.5 GB** (R5: ≤ 24.5 GB on cv02) | **alone only:** gate 21.5 + 2 = 23.5 GB, and 26.7 GB is free with finllm alone. No other job of ours on the GPU | ~4x FLOPs; alone ≈ 3-3.5 h per run (S: gaint fine-tune throughput ~6.75 steps/s aggregate at 1x) | **~16-18 h of exclusive GPU** (blocks PF2, B3, thin-crack) |
| 2x with batch 4 × 2 accumulation | ~11 GB | 2 lanes | as above | breaks one-change: BN batch statistics change from 8 to 4 |
| **HR-skip** (full-res stem: conv3×3 1→16, 16→16, BN-ReLU, concatenated into `x_0_4`) | +16-ch 512² tensors ≈ +0.6-1.0 GB bf16 → **~7.2-7.5 GB** | 3 lanes (gate ~9.5 GB) | +< 2% FLOPs; ~1.05-1.1x SUP100-PF | ~13 lane-h, ~5 h wall with 3 lanes; code ~0.5 day (switch + identity + tests) |

## 6. Expected effect (S) and kill
- **2x on SUP100-PF:** test n.d. again (R5 E). E1 crack recall perhaps +0.02 to +0.03. That is cheaper to get from a bigger or preserved encoder (idea 8, RN50-PF in PF2) at 1-1.5x compute instead of 4x and exclusive GPU. **DROP.**
- **HR-skip:**
  - test crack IoU −0.005 to +0.01, relF1@2 unchanged (§2: the stride-2 skip already carries the signal; labels cap strict IoU);
  - E1 effect ≈ 0 (E1 cracks wider, context failure).
  - **DROP as a standalone arm.**
  - Reopen only if Skeleton Recall or clDice raise relR@2 or component recall while strict IoU falls, i.e. a pure localisation loss. Then HR-skip on that BEST is the natural one-change follow-up (cheap, 3 lanes).
- **In idea 8:** a stride-2 stem is required for DINOv3 ConvNeXt / SAM2 Hiera inside U-Net++ (smp U-Net++ fails without it; E, gaint CPU build). Its cost is booked in that arm.
- **Kill (if anyone runs HR-skip anyway):** n.d. on crack IoU and relF1@2 in both sets with relR@2 at relP@2 ≥ 0.90 not better. Close it.

## 7. Needs from others
None, unless team-lead overrides the DROP. Then: builder (switch `model.hr_skip`, 0.5 day), coach (protocol), runner (3 lanes, ~5 h wall).

---

## judge verdict (31 Oct 2026, 14:16 IST per log.md; report md5 f5e093f9 as reviewed)

**Verdict: DROP as a standalone arm (both 2x and HR-skip). Agreed.** HR-skip goes into idea 8's wrapper (stride-2 stem) and the park trigger in §6.

### What I reproduced or checked (E)
- **R5 facts** (`trackM/verify_r5.md`):
  - n.d. on all four primaries, both sets; val EXCLUDE;
  - confident misses 0.189 → 0.208;
  - E1 recall 0.178 → 0.204;
  - 591.9 vs 148.0 GFLOPs. All match.
  - So 2x is a repeat of a closed rung. The only new element would be PF, and 2x on SUP100-PF needs about 16 to 18 h of exclusive GPU (found's estimate, S) for an expected test n.d. and an E1 effect that cannot be a co-primary outside PF2. Not worth it.
- **Crack vs stride** (§2): reproduced independently (see the idea08 verdict; `judge/crack_width.py`, ≤ 0.004).
- **Literature:** all 4 ids resolve. arxiv:2302.12491 resolves to the published doi:10.1109/tim.2024.3374293; cite that.
- **Not reproduced:** the activation-memory ratio 3.73 (scratchpad `mem_check.py`). The DROP does not depend on it.

### Corrections (do not change the verdict)
1. **"E1 cracks labelled about twice as wide" overstates it.**
   - The 2·EDT median is quantised (2.0, 2.83, 4.0, ...).
   - Area / skeleton length gives E1 3.66 px vs train 2.41 px, i.e. **about 1.5x** (E, `judge/crack_width.py`, md5 87f57a58). Use "about 1.5x".
2. **§3 misreads the inactive-edge band.**
   - The +0.007 at A100 (handbook 18 §D2) is an inference-only re-score that ignores crack within 2 px of inactive. It says the inactive-edge band is a small share of A100's crack-IoU loss. It says nothing about 1 to 2 px localisation in general.
   - P14 ran at 10%, not 100%.
   - Better evidence that resolution is not the binding limit: R5 itself (confident misses got worse), and that strict IoU sits at the labelling ceiling while relF1@2 is 0.897 (FINAL). The loss within 2 px is label jitter, which resolution cannot fix (handbook 11 row 21).
3. **"The stride-2 skip keeps the crack" is a statement about label geometry, not feature capacity.**
   - conv1's stride-2 map is a single 7×7 conv. The semantic decision is made at stride ≥ 4, as §2 says.
   - Tag the ceiling argument S. The DROP rests on R5 (E), not on it.

### Tags
- E: R5 facts and crack/stride reproduced.
- R: 4 ids resolved.
- S: the DROP rationale on cost vs authorised readouts.
