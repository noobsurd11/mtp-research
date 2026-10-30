# coach: MIM5 settings and launch conditions (v1, 29 Oct 2026)

Binding on `protocol_mim5.md` unless runner argues a point with evidence. Tags: E measured (path), R literature, S judgement.

## A. Blocking facts (E)
1. **`encoder_init` is not in el_m.** `load_encoder_init` (P15, `be67787`, `el_p14/scripts/train.py` l.120, l.265) is not an ancestor of `1be64e1`. New worktree `el_f1` from `1be64e1`; port only `load_encoder_init` and its 2 call lines plus a test. Not `tol_dice`.
2. **Pool vs held-out cells** (gaint `critic4_skcdf/neardup/neardup.json`, `samepos_pool.json`; `external_unlabeled.txt` md5 `34d191cb...` on gaint and cv02):
   - by stem: 0 of E1's 106 in the pool; the other 11 ext117 stems are in it;
   - by module id: 196 pool cells share a module with val, 88 with test, 144 with E1;
   - by content: E1-106 best pool match r_hp 0.912 (different row); test 0.959 (`ARTS_00047_r3_c1` ~ pool `ARTS_00034_r3_c1`); val 0.990 (`ARTS_00061_r1_c6` ~ pool `ARTS_00046_r1_c6`).
3. **Rule 1 divisor:** house code (`ssl_rules.py` `cmp`, /3). State it.

## B. MIM image list (costs under 4% of images)
- Train: 478 minus the 7 D7 twins (`CFVS_00003_r5_c5`, `CFVS_00037_r8_c4`, `CFVS_00032_r8_c4`, `CFVS_00020_r4_c4`, `CFVS_00022_r4_c4`, `CFVS_00031_r4_c4`, `ARTS_00081_r5_c1`).
- Pool: 11,938 minus
  1. every cell whose (source, module) is a val, test or E1 module;
  2. the 11 ext117 stems in the pool;
  3. every pool cell with r_hp >= 0.85 to any val, test or ext117 query (any module);
  4. pool copies (r_hp >= 0.95) of the 7 train twins.
- Why module level: E1 means unseen modules and A5c never saw them; MIM must not either, or the E1 secondary is asymmetric.
- Hold out 256 pool cells (fixed seed) for a reconstruction-loss monitor only.
- Script committed; protocol states count and md5 of the sorted list.

## C. Pretraining recipe
| Item | Setting | Why |
|---|---|---|
| Encoder | `build_model(smp_unetpp).encoder` from the same venv: ImageNet R34, 1 channel (summed RGB) | init is bit-identical to A5c's; keys match `encoder_init` |
| Input | 512 full cell, mean 0.5 / std 0.25 as training | same as fine-tune; no crop, no rescale |
| Aug | `get_labelsafe_augmentation` as is (flips, rot90, brightness/contrast 0.2 p 0.4) | no RandomResizedCrop, blur, noise or small rotation: each resamples or erases 1-2 px cracks and changes scale vs fine-tune |
| Masking | SparK sparse emulation; mask on the stride-32 grid (16x16 cells of 32 px), ratio 0.6, per image, seeded | SparK default (R arxiv:2301.03580). Smaller patches leak through stride-32 features. A crack cannot be predicted from context at any patch size; MIM learns grain, fingers, busbars, edges |
| Sparse ops | zero masked input; after every Conv2d, BN and MaxPool multiply by the mask at that resolution (nearest); BN -> SparseBN (stats over visible positions only, same params and buffers) | dense zero-fill pollutes BN stats and gamma/beta and gives a hole distribution fine-tune never sees |
| Decoder | SparK-style light U-Net decoder: per scale (4, 8, 16, 32) densify (norm, fill masked positions with a learned mask token, 1x1 proj), upsample x2 per block to stride 1, width 512 halving, 1x1 to 1 channel. Discarded after MIM | decoder transfer would be a second change |
| Loss | MSE on masked 32 px patches only, target per-patch normalised (eps 1e-6) | SparK/MAE default; predicting 0 gives loss ~1.0, a free sanity scale |
| Optim | AdamW b(0.9, 0.95), wd 0.04 on conv/linear weights only; lr encoder 2e-4, decoder + densify + tokens 1e-3 | continued, not from scratch: adapt, do not overwrite |
| Schedule | encoder frozen for the first 2 epochs (decoder warmup over them); then encoder linear warmup 1,000 steps from 0, starting at unfreeze; cosine to 0 at the end for both groups | a random decoder's early gradients should not hit ImageNet BN/filters; an unfreeze at peak lr with empty Adam state is the same jolt |
| Batch / len | v1.1 (runner's proposal accepted): 64 x 100 epochs, about 19.4k steps and 1.24M samples, which matches HPT's 5k x 256. If the smoke peak is too high for the machine: 32 x accum 2 | fixed now; **only the final checkpoint is used**; no length selection |
| Precision | bf16 autocast, clip 5.0, log clip rate | |
| Monitor | held-out 256 loss every 1k steps, fixed mask seed | overfit check only, never selection |

Cost (S): about 25-35 GFLOPs forward per sample, so 2-3 GPU-h on a free GPU; about 2x on gaint next to `q3_bignets.py` (GPU at 97% util, 9.8 GB used, 12:50 IST).

## D. Save and load
- Save `{"models": {"model": {"encoder." + k: v}}}` from the plain smp encoder keys (SparseBN must not change keys or buffers). md5 into the protocol.
- `mim_step0.pth`: the same save path applied before any MIM step.

## E. Checks before any fine-tune
- **I1:** `el_f1` with `encoder_init` unset reproduces A5c stdout bit-identically for 1,000 steps on the fine-tune machine.
- **I2:** `encoder_init=mim_step0.pth` reproduces the same 1,000 steps bit-identically (proves save/load adds nothing).
- **I3 (unit tests, CPU ok):**
  - an all-ones mask gives the plain encoder's outputs;
  - perturbing masked input pixels leaves every stage output bit-identical;
  - SparseBN batch stats equal BN over visible positions;
  - masked positions are 0 at every stage;
  - `load_encoder_init` strict-loads the saved file.
- **Smoke (at most 500 MIM steps) must show:**
  - loss starting near 1.0-1.5 and falling;
  - no NaN;
  - samples/s and peak memory (`max_memory_allocated` and nvidia-smi);
  - clip rate;
  - held-out loss at steps 0 and 500;
  - one PNG of 4 cells (input, mask, reconstruction) to catch alignment bugs.

## F. Fine-tune and rule
- **MIM5:** A5c recipe unchanged; only `model.encoder_init=<mim_20k.pth>`.
  - seeds 0-4, `data.split_seed=0`, fraction 0.05, `masks_escdd`, labelsafe, `smp_unetpp`, `ce_dice`;
  - Adam 1e-3, wd 1e-4, warmup 200, cosine, 20k steps, batch 8, bf16, final step.
  - No lower encoder lr, LLRD or freezing. Each is a separate arm that needs its own A5c twin, and nothing now justifies one.
- **Comparator:** A5c on the same machine and commit.
  - On cv02: reuse P12 s0-2 + P13 s3-4 only after I1 passes on cv02 at the `el_f1` commit; otherwise rerun 5 seeds.
  - On gaint: rerun A5c s0-4 at `el_f1`.
- **Scoring:** both arms through the same per-cell scorer (m0_audit format: per-cell confusion matrix plus `crack_rel2`) so coach can recompute.
- **Rule (v1.2, after review_mim5_v0 C4/C5):** MIM5 − A5c, 5 v 5, rule 1 with the house divisor 3 (`ssl_rules.py` `cmp`; team-lead ruling, 29 Oct), on test crack IoU, crack relF1@2 and inactive IoU. /5 is reported as descriptive only.
  - Verdict on all 50 and without the noisy cell (the clean co-primary, 27 Oct SYNTHESIS §2): pass on both, or pass on one with a same-sign n.d. on the other; worse on either set fails.
  - Without twins and without both: reported.
  - Width flag: relP@2 drop > 0.05.
  - Yardsticks, not in the rule: A5c+LA 0.319, BsM5 (D7) 0.331.
- **Power (S):** A5c crack sd 0.008, so the crack threshold is about 0.015. Inactive threshold is about 0.05 or more. The expected effect (crack 0 to +0.02, inactive 0 to +0.05; SYNTHESIS row 3) sits at or below threshold, so n.d. is the likely outcome. Write that in now.
- **Kill:** n.d. on all three primaries in both verdict sets closes "feature learning from this pool beats ImageNet init at 5%". The 100% arm runs only if 5% passes.

## Not now
- Crack-weighted masking or loss, decoder transfer, a second pretraining length, linear probes. Each is a new arm, worth considering only if MIM5 shows a same-sign hint.
