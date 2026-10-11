# P15: UCF-EL-pretrained encoder vs ImageNet encoder, fine-tuned on BenchmarkEL at 5% and 10% labels (gaint). Results

Protocol: `protocols/P15_ucf_encoder_transfer.md`, locked before any P15 fine-tuning run.

**Runs**
- **Pretraining** (cv02, one run, `p15_ucf_pre_dlv3p_r34`, el_p13 `bac5264`):
  - DeepLabV3+ with a ResNet-34 encoder (ImageNet init), 22.4M parameters;
  - all 9,562 UCF-EL train cells; 59,760 steps (100 epochs); seed 0.
  - UCF test, final step: crack IoU 0.666, defect mIoU 0.487 (`experiments/p15_ucf_pre_dlv3p_r34/metrics.json` on cv02). This score was not used for any decision.
- **Fine-tuning** (gaint, RTX PRO 4500): 6 runs, 11 Oct 17:01–22:26 IST, all rc = 0.
  - Worktree `el_p14` at `be67787`, with `model.encoder_init=pretrained/p15_ucf_pre_dlv3p_r34.pth`.
  - The 216 encoder tensors are copied and the first conv is summed over its 3 input channels; the decoder starts fresh.
  - P6 L3 options verbatim; 20,000 steps; final weights.
- **References** (gaint, ImageNet encoder, same options and seeds):
  - A5 = P10 `p10_A_5pct` (`0367079`);
  - gA10 = P12 `p12_gA_10pct` (`24590fb`).
  - The supervised path is unchanged across these commits (the protocol's premise).
- **Leakage check** (in the protocol): UCF train vs BenchmarkEL val + test, max normalised correlation 0.79; none ≥ 0.90.

**Files**
- `raw/`: re-score JSONs and `launch_gaint.log`.
- `p15_rules.txt`.
- `dedup.py`: the leakage check.
- E1 per-cell metrics and the bootstrap: `../e1/e1_p15.md`. E1's pooled IoU equals the re-score exactly.
- Reproduce with `bash scripts/post_p15.sh <cv02 gpu>`.

## Results
Test, revised labels, mean ± sd over seeds 0–2; all gaint except the P6 rows.

| Arm | Encoder init | crack IoU | inactive IoU | crack relF1@2 | crack relP@2 | crack AP | inactive AP |
|---|---|---|---|---|---|---|---|
| A5 (P10) | ImageNet | 0.298±0.005 | 0.277±0.055 | 0.708±0.012 | 0.890±0.014 | 0.282±0.003 | 0.270±0.050 |
| **gU5** | UCF-EL | 0.308±0.006 | 0.265±0.046 | 0.723±0.015 | 0.872±0.023 | 0.292±0.008 | 0.253±0.035 |
| gA10 (P12) | ImageNet | 0.400±0.007 | 0.351±0.046 | 0.820±0.010 | 0.903±0.010 | 0.407±0.003 | 0.359±0.038 |
| **gU10** | UCF-EL | 0.389±0.006 | 0.265±0.023 | 0.806±0.006 | 0.898±0.016 | 0.394±0.003 | 0.273±0.020 |
| L3 10% (P6, cv02) | ImageNet | 0.396±0.003 | 0.294±0.019 | 0.814±0.003 | 0.910±0.006 | 0.400±0.004 | 0.302±0.018 |
| L3 100% (P6, cv02) | ImageNet | 0.471±0.001 | 0.429±0.011 | 0.876±0.003 | 0.939±0.003 | 0.593±0.003 | 0.420±0.018 |

## Locked rules
Rule 1 is "U helps": U − reference under P8 rule 1. Each cell gives the difference, then the threshold in brackets.

| Contrast | crack IoU | inactive IoU | crack relF1@2 | Verdict |
|---|---|---|---|---|
| **gU5 − A5** | +0.0096 (0.0100) | −0.012 (0.083) | +0.015 (0.022) | **fails**: n.d. on all three. Crack misses the threshold by 0.0004. Width relP@2 −0.017, ok |
| **gU10 − gA10** | **−0.012** (0.011) | **−0.086** (0.059) | **−0.014** (0.013) | **fails: worse on all three.** Width −0.005, ok |

**Rule 3, descriptive.**
- gU5 − gA10 (does UCF pretraining stand in for doubling the labels?): crack −0.092, inactive −0.086, relF1@2 −0.097. No.
- Gap closed against L3 100% (cross-machine, descriptive only):
  - gU5: crack +6%, inactive −8%, relF1@2 +9%;
  - gU10: crack −16%, inactive −110%, relF1@2 −26%.

**Calibration** (P12 rule 7, repeated here): gA10 − cv02 L3 10% is n.d. on all three. So gaint and cv02 supervised agree on crack within 0.006.

## Robustness (rule 2)
Paired image bootstrap over the 50 test cells (2,000 resamples), then the Δ without the top-3 cells (`../e1/e1_p15.md`).

| Contrast | crack IoU | crack relF1@2 | inactive IoU |
|---|---|---|---|
| gU5 − A5 | +0.010 [+0.006, +0.014]; +0.010 | +0.015 [+0.007, +0.023]; +0.014 | −0.012 [−0.051, +0.035]; +0.018 |
| gU10 − gA10 | −0.012 [−0.026, −0.002]; −0.015 | −0.014 [−0.030, −0.004]; −0.020 | −0.086 [−0.135, −0.030]; −0.067 |

- **At 10%, the harm is robust over cells on all three metrics,** including inactive without the top-3 cells.
- **At 5%, the crack gain is small and consistent over cells** (+0.010, CI above 0). It fails the seed rule by 0.0004, so it is not claimed.

## E1 per-cell metrics (secondary)

| Set | Contrast | Metric | Δ | 95% CI |
|---|---|---|---|---|
| Test | gU10 − gA10 | inactive cell IoU | −0.078 | [−0.121, −0.035] |
| Test | gU5 − A5 | crack tolF1 | +0.004 | [−0.032, +0.031] |
| Unseen modules (106 cells) | gU5 − A5 | inactive cell IoU | +0.062 | [+0.002, +0.122] |
| Unseen modules (106 cells) | gU5 − A5 | crack tolF1 | −0.034 | [−0.068, −0.004] |

On unseen modules, gU10 − gA10 is n.d. on every metric.

## Reading
- **Under the locked rules, an encoder pretrained on UCF-EL labels does not beat ImageNet initialisation on BenchmarkEL.**
  - At 10% labels it is worse on all three primaries, robust over cells.
  - At 5% it is about equal; there is a +0.010 crack effect that just misses the seed threshold.
- **Not tested, so possible reasons are hypotheses only:**
  - Scale: UCF cells are resized to 295 px and cropped to 256, while BenchmarkEL cells are 512 px. Crack labels are about 9 to 15 px wide on UCF and about 2 px on BenchmarkEL (`03_datasets_and_splits.md`).
  - Architecture: only the encoder transfers; the pretrained head was DeepLabV3+, the target is U-Net++.
  - Class taxonomy differs between the datasets.
  - The input normalisation is the same (mean 0.5, sd 0.25 in both configs).
- **This weakens the "related labelled data beats unlabelled data" direction** (directions rows 3 and 5) for this recipe. It does not test MIM or self-supervised pretraining (not claimed).

**Not claimed:** MIM or self-supervised pretraining, other UCF recipes, freezing schedules, pretraining length, pooling with cv02.
