# el-fault-detection

Semantic segmentation of defects in electroluminescence (EL) images of PV
modules, on the 24-class BenchmarkELimages benchmark (`dataset_20211104`).
Supervised and Mean Teacher semi-supervised training share one iteration-based
trainer, so runs with equal `training.total_steps` are directly comparable.

The previous SA U-Net++ SSL project this repo was rebuilt from is preserved
as tag `v0-sa-failed` in
[noobsurd11/sa-unetpp-ssl-el](https://github.com/noobsurd11/sa-unetpp-ssl-el).
Its reported results are not reproducible and are not carried over; see
`reports/setup_check.md` for the audit.

## Setup

```bash
python3.12 -m venv .venv
.venv/bin/pip install torch torchvision --index-url https://download.pytorch.org/whl/cu130
.venv/bin/pip install -r requirements.txt

# symlink the dataset (nothing is copied)
.venv/bin/python scripts/link_data.py --dataset_dir /path/to/BenchmarkELimages/dataset_20211104
```

## Data and splits

* Masks are the dataset's index PNGs (pixel value == class id 0–23), read
  directly from `data/labeled/masks_coded/`.
* Split files are committed under `data/splits/` and are required; a missing
  split file is an error.
  * `train.txt` / `val.txt` / `test.txt`: official split, 478 / 54 / 50.
  * `seed{0,1,2}/labeled_{50,20,10}pct.txt`: nested labelled subsets of train
    (239 / 95 / 47), stratified on whether an image contains crack (14) and
    inactive (11). `unlabeled_<P>pct.txt` is the rest of train.
  * Regenerate with `scripts/make_splits.py`; per-split class pixel counts are
    in `reports/split_class_pixel_counts.{md,csv}` (`scripts/split_class_stats.py`).
* Class weights for weighted CE are computed at startup from the labelled
  subset in use: sqrt-inverse-frequency, capped at 10× the median, mean 1;
  classes with no pixels get weight 0.

## Training

```bash
# supervised, 20% labels, split seed 0
.venv/bin/python scripts/train.py --config configs/supervised.yaml \
    --opts data.labeled_fraction=0.2 seed=0

# Mean Teacher SSL, same budget
.venv/bin/python scripts/train.py --config configs/ssl_mean_teacher.yaml \
    --opts data.labeled_fraction=0.2 seed=0
```

* Model: U-Net++ (`model.name: unetpp`, 4.98M parameters); `model.sa_gating: true`
  adds the SA gate of tag `v0-sa-failed` to every decoder node (5.44M).
  `configs/pratt_unet.yaml`: smp U-Net with an ImageNet VGG16 encoder (Pratt et al.).
* Checkpoints: `checkpoints/best.pth` (best val) and `checkpoints/latest.pth`
  (full training state every `training.checkpoint_every` = 2000 steps).
  `--resume` continues an interrupted run exactly (bitwise in strict
  deterministic mode, `scripts/resume_test.py`); a run directory with outputs
  needs `--resume` or `--overwrite`.
* bf16 autocast (`training.amp_dtype`).  Training batches are a pure function of
  (seed, step) (`src/data/stream.py`).
* Launch long runs with `scripts/launch.py` (GPU memory guard: free >= expected
  peak + 2 GiB, at most 2 of our jobs, resume-once watchdog), detached:

```bash
setsid nohup .venv/bin/python scripts/launch.py --name <run> --peak <GiB> -- \
    --config configs/supervised.yaml --opts run_name=<run> ... > /dev/null 2>&1 < /dev/null &
```
* Every `training.val_every` steps the model (the EMA teacher in SSL) is
  evaluated on val; the checkpoint with the best val `defect_miou` is kept,
  and test is evaluated once at the end on that checkpoint.
* Each run writes `experiments/<run_name>/config_used.yaml`, `train.log`,
  `metrics.json` (tracked in git; test results at the best-val step and at the final step) and `checkpoints/best.pth` (ignored).

## UCF-EL

`configs/ucf_deeplab.yaml` (supervised, Fioresi recipe: smp DeepLabV3+ R50,
SGD poly, batch 16, 295 → 256 crop) and `configs/ucf_pvs3.yaml` (PV-S3 mean
teacher).  `data/ucf_el` is a symlink to the UCF-EL-Defect repo's `training/`
folder; committed splits and manifest in `data/splits/ucf_el/`
(`scripts/make_ucf_splits.py`).  UCF runs have no val: test at the final step.

PV-S3 variants: `configs/ucf_pvs3.yaml` (v1, failed recipe), `configs/ucf_pvs3_v2.yaml`
(labelled loss on the weak view = the SL-arm augmentation) and
`configs/ucf_pvs3_v2_classthr.yaml` (per-class pseudo-label thresholds capping each
class at 2x its labelled-GT share).  PV-S3 runs log per-class pseudo-label pixel
counts every 500 steps to `experiments/<run>/pseudo_labels.csv`.

## Queues, probes and diagnostics

* `scripts/night_queue.py`: lanes of jobs under the launch guard; restartable
  (finished jobs skipped, running ones adopted, interrupted ones resumed).
  `--dry_run` checks every job's config and split files.
* `scripts/probes.py`: metric probes on a finished UCF-EL run (all-crack predictor,
  predictions dilated by 3 px, background-threshold sweep), standard + pvs3.
* `scripts/pseudo_label_share.py`: a PV-S3 run's predicted / pseudo-label class shares on
  its unlabelled pool vs the labelled ground truth (optionally per confidence threshold).
* `scripts/results_table.py`: every result in two tables (pilot code / current code);
  final-step test primary.  `scripts/evaluate.py --split valtest --weights final` gives the
  BenchmarkEL secondary metric (val + test pooled).
* `scripts/resume_test.py`: N steps straight vs N/2 + crash + resume, bitwise, per trainer.

## Metrics (`src/evaluation/metrics.py`)

One module for every evaluation path.  Conventions (in `metrics.json` under
`conventions`): `standard` (global confusion matrix), `pvs3` (pixels whose
ground truth is background dropped) and `pratt_median` (median over images of
the per-image IoU, rules A/B/C for images without the class).  Classes absent
from the evaluated ground truth are NaN and excluded from means.  The keys
below are the `standard` convention on BenchmarkEL.

| key | meaning |
|---|---|
| `defect_miou` | **headline**: mean IoU over crack (14) and inactive (11) |
| `miou_defects_all` | mean IoU over the 12 defect classes |
| `miou_all` | mean IoU over all 24 classes |
| `crack_recall` | pixel recall of crack |
| `crack_recall_relaxed` | a GT crack pixel counts as found if a predicted crack pixel is within 2 px |
| `crack_fpr_image` | share of crack-free images with ≥ 20 predicted crack pixels (NaN if the set has no crack-free image) |

```bash
.venv/bin/python scripts/evaluate.py --run experiments/<run> --weights best|final --split test
```

## Tests

```bash
.venv/bin/python -m pytest tests
```

## Citation

```bibtex
@article{pratt2021defect,
  title   = {Defect detection and quantification in electroluminescence images of
             solar PV modules using U-net semantic segmentation},
  author  = {Pratt, Lawrence and Govender, Devashen and Klein, Richard},
  journal = {Renewable Energy},
  volume  = {178},
  pages   = {1211--1222},
  year    = {2021}
}
```
