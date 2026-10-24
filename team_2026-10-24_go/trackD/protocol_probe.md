# Track D probe protocol v1: frozen-encoder probe per source (DX, 24 Oct 2026)

Direction 4 in `team_2026-10-24_why/SYNTHESIS.md` §2; defaults `trackD/critic_defaults.md` §0 and §2. Inference only. Written before any probe number.

## Question
Does any frozen pretrained encoder separate crack on BMRK better than our fine-tuned 5% supervised model (A5c), when its linear probe sees the same 23 labelled cells?

## Hypothesis (falsifiable)
At least one frozen ImageNet or DINOv2 encoder gives a BMRK test crack AP at least 0.05 above A5c's.
**Expectation (S, written now):** no. P4 (10% set, old masks) put the best frozen crack AP (ConvNeXt-T 0.331 pooled) below the full SL-10% model (0.527 test); a linear probe on 2 BMRK crack cells should not beat a fine-tuned U-Net++ on BMRK.

## Encoders (frozen, eval mode, torchvision / torch.hub weights)
| id | Encoder | Features (as P4) |
|---|---|---|
| rn50_random | ResNet-50, random init, torch seed 0 | layer1 (s4) + layer2 (s8). Floor, not in the rule |
| rn34_imagenet | ResNet-34 `IMAGENET1K_V1` (our L3 init) | layer1 (s4, 64) + layer2 (s8, 128) |
| rn50_imagenet | ResNet-50 `IMAGENET1K_V2` | layer1 + layer2 |
| convnext_t | ConvNeXt-T `IMAGENET1K_V1` | stage 0 (s4) + stage 1 (s8) |
| dinov2_vits14 | DINOv2 ViT-S/14 (torch.hub) | patch tokens at 518 px (37 × 37) |
| ref_A5c_enc | A5c s0 encoder (`p12_A_5pct_s0`, final step), `encode()` e2 + e3 | reference row only, not in the rule |

- DINOv3: no checkpoint is cached on cv02, gaint or the laptop (checked 24 Oct 11:30 IST). Skipped; no gated download.
- New downloads: ResNet-34, ResNet-50, ConvNeXt-T and DINOv2-S weights into cv02 `TORCH_HOME` (~370 MB total, public). SHA256 of each file recorded in the output.
- Input: 512 px grayscale replicated to 3 channels, ImageNet normalisation; A5c encoder: its own 1-channel normalisation (0.5, 0.25).

## Probe (P4 recipe, one change: training set)
- Linear 1×1 conv head per stage, logits bilinearly upsampled to 512 and summed, plus bias. 24 classes, plain CE.
- **Training cells:** seed-0 `labeled_5pct.txt` (23 cells), revised masks `labeled/masks_escdd` (A5c's exact labelled set). P4 used the 10% set and old masks.
- Channel standardisation with mean and sd over the 23 cells' cached features.
- Adam 1e-3, 2,000 steps, batch 8 with replacement, no augmentation, probe seeds 0 and 1. No val use.

## A5c and A5c+LA (same inference pass)
- Runs `p12_A_5pct_s0..2`, `p13_A_5pct_s3..4` (cv02 `el_sk1/experiments`, symlinks), `latest.pth` step 20,000, `models.model`.
- Weak view, bf16, as `rescore_logit_adjust.py`. τ = 0 and τ = 1 (log prior from the 5% labelled cells, absent class gets the smallest non-zero π; same code path).

## Evaluation sets
- **Test:** 50 cells, `escdd_masks/test`. Four cell sets (all / no noisy cell / no 7 twins / neither); BMRK holds none of the excluded cells, so its rows are identical across sets.
- **Pool:** the 455 seed-0 unlabelled train cells minus the 7 D7 twins = 448 cells, masks `labeled/masks_escdd` (hidden from all training here). Larger BMRK sample (train has 42 BMRK cells, 24 with crack; 3 are labelled).
- **40 always-missed components:** `el_sk1/missed40.json` (stem, 8-connected component index on the test mask), all 40 counted as real (critic default).
- Per source: ARTS, BMRK, CFVS, CSIR, plus SDLE (pool only) and all.

## Metrics (crack primary; inactive the same, descriptive)
1. Pixel AP, 1,000-bin, `binned_ap` (same function as every re-score).
2. Argmax IoU, P, R; relaxed P, R, F1 at 2 px.
3. **Recall at matched precision:** target = A5c+LA (τ 1) pixel precision on that source and set, mean over 5 seeds. Probe recall at the highest-recall bin whose binned precision ≥ target. Reported for the probe and for A5c (τ 0).
4. 40 components: relaxed recall@2 per component, at the probe's argmax and at the matched-precision threshold of the all-source test set; reported as px-weighted recall and count with recall ≥ 0.5.

## Decision rule (fixed now)
- **Primary metric:** BMRK test crack AP.
- **Reference:** R = max(A5c τ 0 mean, A5c+LA τ 1 mean) over 5 seeds.
- **Pass for encoder X:** mean over the 2 probe seeds ≥ R + 0.05 **and** each probe seed alone ≥ R + 0.05.
- **Any pretrained encoder (rows 2 to 5) passes:** the encoder/distillation route stays open (input to Track M's backbone ladder) and MIM pretraining (direction 7) is gated out, because an off-the-shelf encoder already sees BMRK crack.
- **None passes:** MIM stays the only encoder bet in Track D; no encoder swap or distillation run is justified by this probe.
- **Robustness, not in the rule:** BMRK pool crack AP with the same arithmetic. If test passes and pool does not, the verdict is reported as "test only, fragile".
- Everything else (other sources, matched-precision recall, 40 components, inactive, rn50_random, ref_A5c_enc) is EXPLORATORY.

**Limit stated now:** a fail means frozen linear features do not beat the fine-tuned model; it does not show a fine-tuned stronger backbone would not help. That is Track M's question.

## Checks
- A5c τ 0 and τ 1 on test reproduce `results/sk1/la_sa_test.json` crack/inactive IoU and AP to |diff| < 1e-4 for all 5 runs (pipeline identity).
- Per-cell sums equal pooled values.
- Twins and test/val stems absent from the pool list (asserted).

## Compute and files
- cv02, one GPU (6 by agreement with MD), tmux `=dxprobe`, ~1 GPU-h; booked in `gpu_ledger.md` before start.
- Code: `~/mtp/research/scripts_cv02/trackD_probe.py`, deployed to `/tmp/noob_el/el_trackD/probe/`, importing `el_sk1` code (REVISION `0ea71df`) read-only; md5 of the script recorded in `REVISION`.
- Outputs: `probe.json` (per encoder, seed, set, source), `percell.json`, log; copied to `results/trackD_probe/` and relayed to gaint `cv02_noob_el/el_trackD` with MD5 checks.
- Analysis: `trackD/probe_results.md`; C recomputes the BMRK rule from `probe.json` histograms.
