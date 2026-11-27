# EL defect segmentation benchmark: lists and code (release v1, staged 22 Nov 2026)

> **Not published.** Staged locally for the owner's review. Before any publication: choose a licence for this code and these
> lists (LICENCE_AUDIT D2), settle the unclear items (D1), and fill the citation block (section 8).

Tags: E = measured in the project's files, S = judgement.

## 1. What this is
A fixed protocol for pixel-level semantic segmentation of electroluminescence (EL) images of silicon solar cells (24 classes,
512 x 512 grey cells), built on the public BenchmarkEL data. Published EL segmentation numbers cannot be compared: three
releases of one dataset with reshuffled splits, train/test leakage, different class lists and metrics, strict IoU on 1 to 2 px
crack labels, single runs without intervals (S, from the project's audit). This release fixes the split, the label set, the
metrics, the operating points and the decision rule, and gives the code that scores a model under them.

| Item | Value |
|---|---|
| Pool | 532 labelled cells (BenchmarkEL `dataset_20211104` train 478 + val 54); sources ARTS 182, BMRK 50, CFVS 169, CSIR 114, SDLE 17 (E) |
| Split | `cv5v3`: 5-fold CV grouped by physical module, 285 groups, none spans folds; held-out sizes 107 / 110 / 103 / 101 / 111 (E) |
| Clean cells | 416 of 532 (`lists/score_exclude_v3.txt` excludes 116); scored beside the 532 (E) |
| Labels | v1.1 = BenchmarkEL 2021 masks with the E-SCDD crack / inactive corrections; scuff and star pixels set to ignore (255, not scored); one swapped BMRK mask restored. Rebuilt by script from public masks (E) |
| Unseen-module set E1 | 106 cells of release `20221008` whose modules match no pool image in a pixel audit (supported, not proven) (`code/bench/sets/e1_106_stems.txt`) (E) |
| Legacy test (test50) | 50 cells; overlaps the pool by physical module (8 same physical cells), so continuity only (E) |

## 2. What is in this release, and what is not
| Folder | Content |
|---|---|
| `lists/` | split definitions (`cv5v3.json` final, `cv5v2.json` screens, `legacy.json`), group files, score-exclude lists, module identity of all 700 image ids, the 816-row cell table (`cells.tsv`, columns in `CELLS_README.md`), the unlabelled-pool list after leakage rules (`pool_t9_v2.txt`), and `labels_v11/` (pixel md5s and edit list of the v1.1 masks, pool cells only) |
| `code/bench/`, `code/scripts/` | the scorer (`bench_score.py`), the CV5 read (`bench_read_w1.py`), the opening read (`bench_open_read.py`), their library, set lists in `code/bench/sets/`; the cv5v3 split builder as provenance |
| `code/benchmark_scripts/` | `make_masks_v11.py` (builds v1.1 from public masks) and the scripts that built the cell table and the splits (provenance; they need project-internal inputs to rerun) |
| `code/tools/prepare.py` | writes the legacy lists and the CV roots from the JSON, and checks a v1.1 rebuild against `lists/labels_v11/MANIFEST_pool532.tsv` |
| `results/BASELINES.md` | baseline and final-model tables (CV5 on the pool; E1 aggregates) |

Not included: images, masks, checkpoints, and any label or per-cell result of test50 or E1. In `cells.tsv` the 156 sealed rows
(test50, E1) carry identity columns only. Machine names in the code and tables are replaced (machA, machB); every change from
the project's files is listed in `SANITIZE.md` of the staging package.

## 3. Data you need (public)
| Data | Where | Terms found (22 Nov 2026) |
|---|---|---|
| BenchmarkEL `dataset_20211104`, `dataset_20220723`, `dataset_20221008` | https://github.com/TheMakiran/BenchmarkELimages | no licence file; the README asks users to cite Pratt et al. 2021 / 2023 |
| E-SCDD (revised crack / inactive masks) | https://huggingface.co/datasets/snt-ubix/escdd | MIT (dataset card) |
| BMRK cells come from ELPV | https://github.com/zae-bayern/elpv-dataset | images CC BY-NC-SA 4.0 |
| SDLE cells come from the CWRU SDLE set | https://osf.io/4qrtv/ | CC BY 4.0 (OSF licence field) |

Lay them out as below (`BenchmarkEL_releases` may be a symlink to the same clone):

```
DATASETS/
  BenchmarkELimages/dataset_20211104/      masks_coded_{train_original,val,test}/, images_*/
  BenchmarkEL_releases/dataset_20220723/   el_masks_{train,val,test}/
  BenchmarkEL_releases/dataset_20221008/   el_images_*/, el_masks_*/        (E1 cells)
  escdd_full/                              el_masks_{train,val,test}/        (E-SCDD)
  splits_benchmark/                        train.txt, val.txt, test.txt      (step 4.1)
```

## 4. Rebuild label set v1.1
Needs Python 3 with numpy and Pillow.
```
cd code
python -I tools/prepare.py legacy-lists --lists ../lists --out DATASETS/splits_benchmark
python -I benchmark_scripts/make_masks_v11.py --datasets DATASETS --out V11
python -I tools/prepare.py check-v11 --lists ../lists --masks V11
```
- `make_masks_v11.py` writes `V11/masks` (values 0 to 23 and 255 = ignore), `V11/masks_strict` (no 255) and `V11/ignore`.
- `check-v11` compares the pixel md5 of every pool mask with the release manifest (pixel md5 = md5 of the raw uint8 array, so the
  PNG encoder does not matter). On the project's own build: 532 cells, 1,064 files match, 0 mismatch (E).
- The legacy lists written by `legacy-lists` reproduce the md5s of the dataset's 478 / 54 / 50 lists (E).

## 5. Score a model
Needs numpy, scipy and Pillow; `bench_read_w1.py` also imports torch (CPU is enough). Everything runs on CPU.

**5.1 Folds.** Train one model per cv5v3 fold `k` on `train` of `lists/cv5v3.json` folds[k] and predict its `heldout` cells.
Seeds: 2 for a screen, 5 for a table row. Final-step weights only (no best-validation checkpoint). Train only on the fold's
`train` list; unlabelled data must come from `lists/pool_t9_v2.txt`. No training list may hold a stem of
`lists/forbidden_v1.txt` (167 stems: test50, the 106 E1 cells and 11 more cells of release `20221008`).

**5.2 Dumps.** One compressed npz per cell, written with `bench/dumpfmt.py` (numpy only):
`<DUMPS>/<bench>/<method>/<run_id>/cv5v3_f<k>/<stem>.npz` with keys `pred` (uint8 class map), `oth` (argmax over the 23
non-crack classes), `m_crack` (crack log-margin), `p_crack` (float32), `p_inact`; plus `manifest.json` from
`dumpfmt.write_manifest` (all keys of `dumpfmt.MANIFEST_KEYS`). From per-class softmax scores, `dumpfmt.maps_from_scores`
gives `oth`, `m_crack`, `p_crack` and `p_inact`. Cells must be in the order of the fold's held-out list.

**5.3 Environment.**
```
python -I tools/prepare.py cv-roots --lists ../lists --split cv5v3 --out ROOTS
export BENCH_CV5V3_ROOTS=ROOTS BENCH_MASKS_V11=V11 BENCH_META=../lists BENCH_META_V3=../lists CUDA_VISIBLE_DEVICES=""
```

**5.4 Per-run records and summaries.**
```
python -I scripts/bench_score.py records --dumps <run dir>/cv5v3_f0 --set cv5v3_f0 --out rec_f0.json
python -I scripts/bench_score.py summary --records rec_*.json --arms MINE='<run_id regex>' BASE='<run_id regex>' \
    --pairs MINE=BASE --groups ../lists/cv5v3_groups.tsv --group-col group --out sum.json
```
Check run in staging: oracle dumps of fold 0 score 1.000 on every headline metric; the same dumps shifted 1 px score strict
crack IoU 0.370 and relF1@2 0.999 (E). This is why strict IoU does not decide.

**5.5 The protocol read** (pooled out-of-fold, operating points, guards, intervals, A/A margin):
```
python -I scripts/bench_read_w1.py --arm BASE=<DUMPS>/<bench>/<base method>:'<run regex>' \
    --arm MINE=<DUMPS>/<bench>/<method>:'<run regex>' --baseline BASE --labels set \
    --groups ../lists/cv5v3_groups.tsv --score-exclude ../lists/score_exclude_v3.txt --out READ
```
Use `--labels set`: it scores against `V11/masks` + `V11/ignore`. The default `--labels v11` also checks the md5 of the
original build's `MANIFEST.md5`, which a rebuild need not reproduce byte for byte.

## 6. The decision rule in brief
- **Headline:** crack relF1@2 (P = share of predicted crack px within 2 px of a ground-truth crack px; R = the reverse), printed
  with relP@2 and relR@2. Strict crack IoU is printed and decides nothing (re-scoring the same predictions on other label
  conventions moves a contrast by up to 0.019). Inactive IoU and mIoU over 13 robust classes (mIoU-R13) are printed.
- **Operating points:** OP-A (argmax) and OP-W (crack bias cross-fitted on the other folds to match the baseline's crack width)
  decide; OP-F (bias for F1) is printed only.
- **Interval:** two-stage group bootstrap (module groups, then one seed per fold and arm), 2,000 draws, 95% percentile.
- **Margin:** M = max(0.01, 2 x SE of an A/A contrast of the baseline), per machine; 0.010 for relF1@2.
- **A crack gain counts** only if, at OP-A and at OP-W, delta >= M and the interval's lower end > 0, and the guards pass: crack
  width ratio 0.85 to 1.15 x the baseline's (pooled and per source with >= 40 cells), false crack px on crack-free cells
  <= 1.5 x the baseline's, mIoU-R13 drop <= 0.010. Inactive IoU never promotes a 2-seed arm (it moves by 0.02 between seeds).
- **Report** 532 cells and the 416 clean cells side by side; never mix machines in one read; state entry class (single model,
  decision layer, ensemble with its equal-cost comparator, source metadata used or not).
- **E1** is a sealed unseen-module test: one registered opening per locked protocol. **test50** is continuity only.

## 7. Baselines
`results/BASELINES.md` holds the tables. PF (U-Net++ / ResNet-34, ImageNet weights, encoder-preserving fine-tune), cv5v3,
5 seeds, OP-A, 532 cells: strict crack IoU 0.3653, relF1@2 0.8463, inactive IoU 0.5042, mIoU-R13 0.6116; relF1@2 on the 416
clean cells 0.8264 (E, table T5). On E1 the final recipe (HRNet-W18 U-Net++ + SWAD + 8-view TTA) beats PF by +0.0430 crack
relF1@2 [+0.0013, +0.1043] (E, table T8).

Known limits (S): one dataset family; BMRK cells carry no module id (grouped by image id); the pool has no half-cut cells;
the E1 label view (release `20221008` masks: class 24 to 2, classes 25 to 28 to ignore) has no builder script in this release.

## 8. Citation
Fill before publication (D2):
```
@misc{el_benchmark_release_v1,
  title  = {<title>},
  author = {<authors>},
  year   = {2026},
  note   = {EL defect segmentation benchmark, lists and code, release v1}
}
```
Cite the data you use. BenchmarkEL asks for (verbatim from its README):
```
@article{pratt2021defect,
  title={Defect detection and quantification in electroluminescence images of solar PV modules using U-net semantic segmentation},
  author={Pratt, Lawrence and Govender, Devashen and Klein, Richard},
  journal={Renewable Energy},
  volume={178},
  pages={1211--1222},
  year={2021},
  publisher={Elsevier}
}
@article{pratt2023benchmark,
  title={A benchmark dataset for defect detection and classification in electroluminescence images of PV modules using semantic segmentation},
  author={Pratt, Lawrence and Mattheus, Jana and Klein, Richard},
  journal={Systems and Soft Computing},
  pages={200048},
  year={2023},
  publisher={Elsevier}
}
```
E-SCDD (verbatim from its dataset card):
```
@misc{hanifi2025bridgingdatagapspatially,
      title={Bridging the Data Gap: Spatially Conditioned Diffusion Model for Anomaly Generation in Photovoltaic Electroluminescence Images},
      author={Shiva Hanifi and Sasan Jafarnejad and Marc Köntges and Andrej Wentnagel and Andreas Kokkas and Raphael Frank},
      year={2025},
      eprint={2511.09604},
      archivePrefix={arXiv},
      primaryClass={eess.IV},
      url={https://arxiv.org/abs/2511.09604},
}
```
ELPV (BMRK cells) and the CWRU SDLE set (SDLE cells): cite the publications their pages list.

## 9. Licence
Not chosen yet (D2). Until a licence file is added, no permission is granted.
