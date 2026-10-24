# Protocol R3: encoder pilots (val-only selection), then the winner at 5 seeds

MD, 24 Oct 2026. Status: **APPROVED by MC** (review_r3.md) after fixes F1 to F3, applied 24 Oct. Part A (pilots) and Part B (5 seeds) are locked together here; Part B's arm is filled in by the Part A rule, which is fixed now.

## What I had seen when writing this
- M0 (`baseline.md`, APPROVED).
- Track D's verified frozen probe (`trackD/probe_results.md`, `verify_probe.md`): frozen ImageNet ResNet-50 and ConvNeXt-T features rank BMRK crack better than ResNet-34 (test AP 0.27-0.28 vs 0.19), and CSIR/ARTS worse.
- No fine-tuned run of any candidate exists.

## Question
Does a stronger ImageNet encoder, trained with the unchanged L3 recipe, beat U-Net++/ResNet-34 at 100% labels?

## Part A: pilots (val only; test is not scored for pilots)
**Candidates.** Same recipe as SUP100 (CE + Dice on crack and inactive, labelsafe, batch 8, 20k steps, Adam 1e-3, wd 1e-4, cosine, bf16), seed 0, ImageNet weights, 1-channel input (RGB filters summed by smp/timm).

| Pilot | `model.name` / `model.encoder_name` | Change vs SUP100 | Params |
|---|---|---|---|
| P-rn50 | `smp_unetpp` / `resnet50` | encoder (one change) | 49.0M |
| P-cnxt | `smp_unet` / `tu-convnext_tiny` | encoder **and** decoder (U-Net++ does not accept ConvNeXt's stride-4 stem in smp 0.5; **two changes, labelled**) | 31.9M |
| P-effb4 | `smp_unetpp` / `efficientnet-b4` | encoder (one change) | 20.8M |
| reference | `smp_unetpp` / `resnet34` | SUP100 | 26.1M |

**Pilots are scored on val only** (`m0_audit.py --sets val`; each JSON records `sets_scored` and carries no test or ext cells; MC checks).

**Pilot score** (MC C4): the mean of val crack IoU, val relF1@2 and val mIoU_rob.
- Val list: 0, 1, 2, 4, 5, 7, 9, 11, 13, 14, 15, 16, 21. Inactive is excluded.
- Plain argmax, final weights.

**Threshold, fixed now from M0.** SUP100 val score per seed: 0.6399, 0.6381, 0.6383, 0.6409, 0.6416. Mean 0.6398, sd 0.0016. **A pilot qualifies if its score > 0.6414.**

**Selection.**
- The qualifying pilot with the highest score goes to Part B.
- If none qualifies, R3 stops: no Part B and no test opening, reported as "no encoder beat R34 on val at the L3 recipe".
- If P-cnxt wins, the Part B claim is "encoder + decoder".

**Reported per pilot:**
- val crack / relF1 / mIoU_rob / inactive;
- params, FLOPs per forward at 512 (fvcore or thop on cv02, batch 1), steps/s and GPU-h at the actual packing, peak memory (`torch.cuda.max_memory_allocated` from a smoke, plus nvidia-smi).

**Under-training or divergence** at the L3 recipe is reported as such. No LR tuning inside R3 (MC C4).

## Part B: the winner, 5 seeds (cv02)
- **Arm** `m_r3_<winner>_s1..5`, **seeds 1-5** (F1: seed 0 would be bit-identical to the selected pilot, since training is deterministic, and would carry its val selection into the confirmation sample).
- **Comparator:** SUP100.
- **Rule 1**, 5 v 5, on 4 primaries (crack IoU, inactive IoU, relF1@2, mIoU_rob with the test list), on all 50 and without the noisy cell (F2, design §1 / C6):
  - **pass** if a primary passes in both sets, or passes in one and is n.d. with the same sign in the other;
  - **worse** on any primary in either set fails;
  - otherwise n.d.
- **Stack inclusion on val** (C1): rule 1 on val crack IoU, val relF1@2 or val mIoU_rob, worse on none. The test verdict is confirmatory.
- **Robustness and reporting:** exactly as protocol_r2. Per source matters most here: the probe predicts gains on BMRK/CFVS and losses on CSIR/ARTS.
- **Named secondaries (MC), so that a pooled n.d. cannot hide a source trade:**
  - BMRK crack AP (binned, 1,000 bins, as the P-series AP) and BMRK crack recall;
  - CSIR and ARTS crack IoU.

  All four get rule-1 arithmetic and the bootstrap, reported descriptively for all 50 and without the noisy cell.
  - SUP100 is re-scored with the same scorer for the per-source AP (inference only), so both sides use identical histograms.
  - Smoke check (MC): `tu-convnext_tiny` stem weight is (96, 1, 4, 4) and equals the RGB sum of timm's ImageNet stem (`log_smoke_checks.txt`).
  - Also reported for the pilots on val (val has 8 BMRK cells).
  - The scorer stores per-cell 1,000-bin crack probability histograms (`crack_h1000_pos/neg`, added to `m0_audit.py` before any R3 run).
- **Multiplicity:** 8 tests, disclosed.
- **Compute claim:** every result carries params, FLOPs/forward and GPU-h relative to R34.

## Code
- No code change. `model.name` and `model.encoder_name` are existing keys (`src/models/model_factory.py`: `smp_unetpp` and `smp_unet` read `encoder_name`, `encoder_weights` defaulting to `imagenet`).
- Deployed `el_mt` `3c1b72b` (= `86197f3` + tests + the logging-only switch, off for R3).
- Weights were checked to download on cv02 (24 Oct): resnet50, tu-convnext_tiny (timm via HF), efficientnet-b4.

## Smokes (before APPROVED, < 1,000 steps)
For each candidate, 300 steps: finite loss, steps/s and peak memory. They also set the packing (runs per GPU).

## Compute
- Pilots: 3 runs, about 1.5-2.5 GPU-h each.
- Part B: 5 runs, about 1.5-2.5 GPU-h each.
- Total ≈ 13-20 GPU-h.
- cv02 GPUs 6-7 via the Track M queue (`lanes_m.sh`, `=mq`). Ledger before launch.

## Not claimed
- That the selected encoder is the best available. Three candidates, one recipe.
- Anything from the pilots on test. They are never scored on test.
