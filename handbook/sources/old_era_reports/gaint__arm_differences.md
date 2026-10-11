# SL-20 vs the MT-20 student at λ = 0: code-path differences

Written Mon 2026-10-05 night on gaint, code at `d920cd6` (no training code changed for this report). No training was run.
Line numbers refer to that revision. The empirical check is `scripts/arm_differences_check.py`. Its outputs are in
`reports/diagnostics/arm_differences_check_s{0,1,2}.json`: the first 100 labelled batches of each arm, built exactly as
`scripts/train.py` builds them, on the CPU, without a model.

## Split seed and training seeds of the existing runs

All existing 20 % runs use **split seed 0**: the labelled subset is `data/splits/seed0/labeled_20pct.txt` (95 images), and for MT /
ALHVR the unlabelled pool is `seed0/unlabeled_20pct.txt` (383 images). `seed` is the **training seed** only.
For seeds ≥ 1, `data.split_seed=0` is passed explicitly. For seed 0, `split_seed` defaults to the training seed, which is also 0.
Some seed-0 `metrics.json` files predate the `split_seed` info key (they show `None`), but their `labeled_split` is `seed0/labeled_20pct.txt`.
No run was resumed.

| arm | gaint runs (training seed) | cv02 runs (training seed) | split seed | labelled / unlabelled | MT labelled view |
|---|---|---|---|---|---|
| SL-20 | `sl_20pct_s0`, `s1`, `s2` (0, 1, 2) | `sl_20pct_s{0..4}_cv02` (0–4) | 0 | 95 / – | – |
| MT-20 | `mt_20pct_s0`, `s1`, `s2` (0, 1, 2) | `mt_20pct_s{0,1,2}_cv02` (0–2) | 0 | 95 / 383 | strong (all six) |
| ALHVR-20 | `alhvr_20pct_s0`, `s1` (0, 1) | `alhvr_20pct_s{1..4}_cv02` (1–4) | 0 | 95 / 383 | – |
| SL-100 (for step 2) | `sl_100pct_s0` (0) | `sl_100pct_s{0,1,2}_cv02` (0–2) | – (`train.txt`, 478) | 478 / – | – |

The weak-view MT run, archived as `mt_20pct_s0_weakview_stopped`, never finished and is in no table.
No existing BenchmarkEL run uses 10 % labels, on either machine (see the note on step 2c at the end).

## Differences: SL-20 vs the MT-20 student with λ = 0

"MT student, λ = 0" means `method: mean_teacher` with the consistency term switched off. With λ = 0 the consistency loss is not
even called (`trainer.py:338-341`). The actual MT runs are in this state for steps 0–1,999 only: λ = 0 during
`ssl.warmup_steps` = 2,000, then a linear ramp to 1.5 over 2,000–3,999.

| # | item | SL-20 | MT-20 student, λ = 0 | same? | code |
|---|---|---|---|---|---|
| 1 | **images per forward pass** (training) | 4 (labelled) | **8**: 4 labelled + 4 unlabelled, in one forward pass | **differs** | `trainer.py:317-319` vs `:326-329` |
| 2 | labelled images in the supervised loss per step | 4 | 4 (`student_logits[:n_l]`) | same | `trainer.py:319` vs `:336` |
| 3 | supervised loss | weighted CE, Σ w·ce / Σ w over the 4 labelled images | the same function on the same 4 labelled images | same | `weighted_ce.py:57-71` |
| 4 | **class-weight subset** | the 95 labelled images (`count_class_pixels(labeled_stems)`) | the same 95 images, so identical weights (identical in every 20 % `metrics.json`; 6 zero-weight classes: sp_dogbone, clamp, rings, dead_cell, belt_mark, jbox) | same | `train.py:330` |
| 5 | labelled image order | `BatchStream(stream_id=0, seed, batch 4)` | the same stream definition, over the same stem order | **same** (verified 400 / 400 samples × 3 seeds) | `train.py:300` vs `:315` |
| 6 | labelled augmentation: operations | one Compose: resize, h/v flip, rot90, rotate ±5° (p 0.5) + blur (p 0.3), brightness/contrast (p 0.4), noise (p 0.3) + normalise | the same ops and parameters, split into two Composes: geometric, then strong photometric (`ssl.labeled_view: strong`) | same distribution | `augmentations.py:38-59, 77-90, 115-147` |
| 7 | labelled augmentation: **geometric draw** | per-transform seeds from `SeedSequence(item_seed)` | the same seeds: the geometric transforms sit at positions 0–5 of the seeded list in both arms | **same** (masks after augmentation equal in 400 / 400 × 3 seeds) | `stream.py:77-82` |
| 8 | labelled augmentation: **photometric draw** | blur / jitter / noise get seed positions 6 / 7 / 8 | MT's extra photometric Compose takes position 6, so blur / jitter / noise get 7 / 8 / 9. The draws are shifted, not independent: SL's jitter coin uses the generator MT's blur coin uses | **differs** (image into the loss bitwise equal in only 87 / 70 / 73 of 400 samples, seeds 0 / 1 / 2) | `stream.py:77-82`, `train.py:297` |
| 9 | **BatchNorm batch contents** (train mode) | batch statistics over the 4 labelled images | batch statistics over 4 labelled + 4 unlabelled images (unlabelled pool of 383). So the unlabelled images change the normalised labelled features, and with them the supervised gradient, even at λ = 0. Running statistics (momentum 0.1) are updated from the mixed batches | **differs** | `trainer.py:326-329`; `sa_unetpp.py` ConvBnRelu |
| 10 | Dropout2d (p 0.2: after pool in enc2 / enc3, every decoder node) | masks for 4 images from the CUDA RNG | masks for 8 images; the RNG stream diverges from step 0 | differs (realisation only) | `sa_unetpp.py:79, 166-167` |
| 11 | **model that is evaluated** (val every 500, best.pth, test, final step) | the trained network | **the EMA teacher** (α 0.999, BN buffers EMA'd as well), never the student. Every MT number in the reports, including `results_consolidated`, is the teacher's | **differs** | `trainer.py:255-257`, `ema.py`, `runs.py:47-49` |
| 12 | teacher forward | – | 4 unlabelled weak views, eval mode, no grad, every step even at λ = 0. No effect on the student when λ = 0 | – | `trainer.py:333-335` |
| 13 | initial weights | `torch.manual_seed(seed)`; `build_model` | the same; the teacher is a deep copy (it consumes no RNG) | same | `train.py:218-219`, `trainer.py:213-218` |
| 14 | optimiser, LR schedule, steps, clip, bf16 | Adam 1e-3, wd 1e-4, cosine with 200 warm-up, 20,000 steps, clip 1.0 over the student's parameters | the same | same | `train.py:103-114`, `trainer.py:196-200, 344-351` |
| 15 | SemiCE loss object | built (the factory always builds it), never used | built, never called at λ = 0 | no effect | `loss_factory.py`, `trainer.py:338` |
| 16 | unlabelled stream | – | its own `BatchStream(stream_id=1)`. The Compose objects are shared with the labelled dataset, but each stream's DataLoader workers are separate processes and every sample reseeds every transform, so nothing crosses over | no effect on the labelled stream | `train.py:297-301` |
| 17 | throughput / memory (gaint, alone) | 4.35 it/s, 9.03 GiB reserved | 2.98 it/s, 10.27 GiB | – (not math) | `metrics.json` timing |

**Summary of what differs** (MT student at λ = 0 vs SL), beyond the realisation of random draws:
1. Forward-pass size 8 vs 4.
2. BN statistics over a half-unlabelled batch, both in training and in the running statistics used at evaluation.
3. The reported MT model is an EMA of the student.

Identical: labelled images and their order, geometric augmentation, class weights, loss, optimiser, initialisation.
The photometric augmentation has the same distribution but different realised draws.

### ALHVR-20 (for reference: step 3 compares against it)

* The labelled stream is SL's own code path (`get_strong_augmentation`, `stream_id=0`, batch 4; `train.py:314-315`). With the same
  training seed, network A therefore sees **the same labelled images with the same geometric and photometric draws as SL**.
  Network A has the same initialisation as SL; network B is seeded with `seed + 1`.
* Each network runs its forward passes on 8 images (4 labelled + 4 unlabelled; `alhvr_trainer.py:95`), so the BN batch is 8 with
  half unlabelled, as in MT. Each step adds a second decoder pass on perturbed encoder features (`forward_dual`).
* The unsupervised weight is λ(t) = 0.1·exp(−5(1 − t/T)²). That is nonzero from step 0 (6.7e-4) and reaches 0.1 at the end. There is no EMA:
  network A is evaluated and reported.

### What "labelled batch 8" in SL does and does not match (step 2)

It changes one config key, `training.labeled_batch_size` 4 → 8, but that key moves several quantities together:

| quantity | SL-20, batch 4 | SL-20, batch 8 | MT-20 student |
|---|---|---|---|
| images per forward pass / BN batch size | 4 | 8 | 8 |
| BN batch contents | 4 labelled | 8 labelled | 4 labelled + 4 unlabelled |
| labelled images in the loss per step | 4 | **8** | 4 |
| presentations of each labelled image in 20,000 steps | 842 | 1,684 | 842 |
| labelled images dropped per epoch (n mod batch) | 3 of 95 | 7 of 95 | 3 of 95 |
| evaluated model | network | network | EMA teacher |

So batch 8 matches MT's forward-pass and BN batch size. It does not match MT's BN batch contents, its labelled pixels per step, or
its EMA evaluation. A batch-8 SL arm that moves toward MT is therefore compatible with a batch-size/BN explanation, and also with more
labelled presentations per step. It cannot separate those two.

**Step 2c (SL-10, batch 8) has no existing arm of the same label fraction.** No SL-10 / MT-10 run exists on gaint or in
`cv02_sync`, so "changes one thing relative to the existing arm" has no batch-4 reference at 10 %. `seed0/labeled_10pct.txt` has 47
images; at batch 8 that is 5 batches per epoch, with 7 images dropped per epoch.
