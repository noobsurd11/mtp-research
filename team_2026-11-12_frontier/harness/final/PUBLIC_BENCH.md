# Public scores: published results on our label family, what is comparable, and the metric code it needs

public_scout, 19 Nov 2026 (01:11 to 01:40 IST), for the lead. Asked by the user on 19 Nov ("the public scores on cv02"): our final model and our baseline scored the way published papers on this dataset score, next to their numbers.
Written from papers, split files and our code only. No GPU job, no queue armed, no sealed label or prediction read (the overlap counts in section 3 use file names and split lists only).
Tags: E = measured or read in a cited file or paper. S = judgement. D = a decision with its record. Papers are cited by their Research MCP id; nothing here is cited that the tools did not return.
Scratch: `/home/noob/work/bench_int_io/public/` (`overlap.py`, page renders of one PDF). Paper PDFs and texts stay local.

## 0. Short answer
1. **Only one published test set can take our final models: the legacy test, 50 cells** (BenchmarkEL `dataset_20211104`). Three papers report on it: Pratt 2023 (dataset paper), SEiPV-Net 2023, PV-S3 2025 (subset CSB-S1, split not stated). All three score on the **old 20211104 masks** and train on the 478 train cells (x4 offline augmentation). (E, section 2)
2. **Every newer paper scores on another test set** that our full-pool models trained on: the 72-cell test of release `20221008` (Attention-Based SegNet 2024, Ramadan 2026) holds **51 cells of our pool**; Hanifi 2025 used an unreleased re-split of the same 695 cells; Torpey 2024 used release `20220723` (66 test cells, 51 in our pool). These rows are **not comparable and cannot be made comparable** without models trained on those release splits, whose train sets hold 38 of our 50 test cells and up to 82 of the 106 E1 cells. (E, section 3)
3. **No paper reports on E1.** E1 is our construct (106 cells new in `20221008`, unseen modules). A public-protocol number on E1 has no published comparator. (E)
4. **The published metrics are reproducible from our per-cell confusion records,** with one new label-set option (old masks `masks_coded` as "v0") and a small CPU module (section 6). Two published metrics are undefined in their papers (SEiPV-Net's averaging; PV-S3's background rule), so those rows get a family of readings, never a single "we beat X" number. (E, S)
5. **Label version:** published test50 rows use the old masks; our models train on v1.1 (crack labels of `20221008`: joined, about 21 to 39% more crack px). Scoring on the old masks is possible and like-for-like for the published rows, but penalises a model trained on the revised convention on crack. Report both (old masks = the comparison; v1.1 = our protocol). No test50 row is made impossible by labels; the `20221008` rows are impossible for split reasons first. (E, S; section 5)
6. **Recommendation:** E1 is the primary set for the final-model claim; the legacy test 50 is a secondary, descriptive public-comparison track inside the same one-shot opening (section 8; `OPENING_DRAFT.md`). A 19th test50 opening goes against D `brief` 1 ("no further opening planned") and needs the lead's and the user's explicit go.

## 1. Search record
- **Queries (Research MCP search_papers, all sources):** BenchmarkEL / Pratt segmentation; EL semantic segmentation crack inactive mIoU (2023+); SEiPV-Net; EL multi-class segmentation benchmark DeepLabv3+ U-Net (2024+); SCDD dataset; arXiv-only EL segmentation (2025+); Pratt thesis. Semantic Scholar snippet search was rate-limited all session, so body-text search was replaced by forward citations.
- **Forward citations walked:** Pratt 2023 `doi:10.1016/j.sasc.2023.200048` (68 of 70 listed), SEiPV-Net `doi:10.3390/en16237726` (32), Attention-Based SegNet `doi:10.1109/access.2024.3431098` (22), Hanifi IEA/AIE `doi:10.1007/978-981-96-8892-0_4` (3), PV-S3 `doi:10.1016/j.engappai.2025.111790` (33). Earlier scan: `literature/notes/F06_post_torpey_scan_2026-10-13.md`.
- **Full text read this session (sections only):** Pratt 2023, Attention-Based SegNet (incl. Tables 1 to 4 from the page images), Ramadan 2026, Torpey 2024, PV-S3 (arXiv copy), MCX-Net, EFSegNet, Saleh 2026, Bramantyo 2026, Elbahri 2026, Sohail 2023. Relied on earlier full reads: Hanifi IEA/AIE (note A10, reproduction P19), E-SCDD paper (note A09, doc 17), SEiPV-Net (F06 "FULL", 13 Oct; the MDPI PDF did not download today, so its numbers below are cross-checked against Attention-Based SegNet Table 1, which copies them).
- **Not resolved (no full text, abstract does not name the data):** Gómez-López 2026 `doi:10.17163/ings.n35.2026.08` ("a publicly available benchmark" plus lab images; P/R/F1 only), Ababneh and Al-Otum `doi:10.2139/ssrn.6293244`, Mo et al. `doi:10.2139/ssrn.7387390`, Narayanan 2024 `doi:10.1109/icces63552.2024.10860045` (binary Jaccard 0.913). None of them claims the 50-cell test set in its abstract (S: low risk of a missed comparable row).

## 2. Published results on our image family (BenchmarkEL releases and E-SCDD)

### 2a. On the legacy test set (release `20211104`, 50 cells, old masks): the only rows our models can meet
| Paper (id) | Test set | Labels | Classes trained / scored | Metric as computed | Absent / background rule | Res. | Training data, selection, runs | Reported numbers |
|---|---|---|---|---|---|---|---|---|
| **Pratt, Mattheus, Klein 2023** (`doi:10.1016/j.sasc.2023.200048`) | the 50 test cells ("fifty images with a prevalence of cracks, gridline defects and inactive areas", hand-picked) | `20211104` (old) | 24 / 5 (crack, gridline, inactive, ribbons, spacing) | **IoU per image and class, median over the 50 test images** (§3.4 "median IoU ... for each image/class combination"); also median recall | not stated; the paper's own numbers fit rule A (cells without the class left out), not B or C (handbook 05 §3.1, inferred) | 512 | 478 train x4 offline aug = 1,912; 54 val; optimiser, epochs, checkpoint not stated; one run per model | best defect model 4c (DeepLabv3+, custom weights): **crack 0.25, gridline 0.20, inactive 0.38, mean of 3 = 0.28**; ribbons 0.63, spacing 0.77; median recall crack 0.86. Best per class over the 12 models: crack 0.26 (1c), gridline 0.32 (1a, 2a), inactive 0.38 (4c). (Fig. 7 / 8; the same values are printed in Attention-Based SegNet Tables 2 and 3) |
| **SEiPV-Net**, Eesaar et al. 2023 (`doi:10.3390/en16237726`) | the 50 test cells, 54 val (F06; `results/seipv_compare/README.md`) | `20211104` (old; also stated by Attention-Based SegNet §III.A) | 24 / all | "mIoU", "IoU", Dice, F1, P, R over the test set; **averaging not defined, no per-class numbers, no code** | not stated | 512 (S) | 1,912 (478 x4); one run per loss | equal weights: **mIoU 0.8604, IoU 0.7447, Dice 0.8531, F1 0.9426, P 0.9491, R 0.9362**; custom weights: 0.8573 / 0.7124 / 0.8312 / 0.9375 / 0.9463 / 0.9290. Its U-Net / PSPNet / DeepLabV3+ baselines: mIoU 0.8065 to 0.8416 (Attention-Based SegNet Table 1, copied from SEiPV). Note (E, arithmetic): IoU = Dice / (2 - Dice) within 0.001 (0.8531 -> 0.7438), so "IoU" and "Dice" are one pooled pixel quantity dominated by background and padding; Ramadan 2026 reads SEiPV's "mIoU" as frequency-weighted IoU (its Table 11) |
| **PV-S3**, Jha, Rawat, Vyas 2025 (`doi:10.1016/j.engappai.2025.111790`, arXiv 2404.13693), subset **CSB-S1** | "CSB-Dataset-S1, 593 images" = Pratt 2023's count; **split not stated**; data link = the BenchmarkEL repo | not stated (S: old, the only labels of that image set when written) | 12 defects / 3 (crack, gridline, inactive) | per-class IoU "averaged across all classes" (Eq. 9, dataset level per handbook 05); P, R, F1 per class | **background treatment not stated**; their released code (UCF-EL) uses `ignore_index = 0`, i.e. background never predicted and background-GT pixels dropped (handbook 05 §4.2) | not stated for CSB (UCF: base 299, crop 224) | 100% (FSL) and 20% (SSL) labels; DeepLabv3+ R50; 30 epochs; one run | FSL 100%: **crack 0.58 (P 0.86, R 0.64), gridline 0.83, inactive 0.50 (P 0.62, R 0.71); mean 0.6367**; SSL 20%: 0.50 / 0.74 / 0.50, mean 0.58 (Table 5). Their Table 6 sets this against Pratt's per-image medians (a different metric; handbook 05 §4.2 item 4) |

### 2b. On other test sets of the same images (not comparable with our models; section 3)
| Paper (id) | Test set | Labels / classes | Metric as computed | Res. | Training | Reported numbers |
|---|---|---|---|---|---|---|
| **Attention-Based SegNet**, Mazen et al. 2024 (`doi:10.1109/access.2024.3431098`) | release `20221008` split: 2,212 train (= 553 x4) / 70 val / 72 test (§III.A) | `20221008`, 29 classes | pooled Dice, IoU, P, R, F1, "mIoU"; **Eqs. 7 and 8 print recall as TP/(TP+FP) and precision as TP/(TP+TN)**; IoU = Dice/(2 - Dice) within 0.002, so a pooled pixel quantity; Pratt-style per-image **median IoU over the 72 cells** for 5 classes | 512 | VGG16 SegNet + CBAM, ImageNet, Adam 1e-4, 30 epochs, batch 8; one run | mIoU 0.9101, IoU 0.8902, Dice 0.9408, F1 0.9538 (Table 1); median IoU **crack 0.42, gridline 0.26, inactive 1.00**, ribbons 0.68, spacing 0.90 (Table 2). Inactive median 1.00 means cells without inactive and without a prediction score 1 (rule C; S, from the value). Table 1 and 2 put these next to SEiPV's and Pratt's numbers from the 50-cell test on old masks: a cross-test-set comparison |
| **Ramadan et al. 2026** (`doi:10.1038/s41598-026-57859-7`) | release `20221008` split: 2,212 / 70 / 72 ("Benchmark EL dataset", BenchmarkEL GitHub) | `20221008`, 29 classes, 25 present in test | per-class P, R, F1 from one pooled matrix; **mIoU = mean over the 25 classes present in test** (E: mean of F1/(2 - F1) over Table 10 = 0.4926 = their 0.493); also wIoU, "gIoU" | **160 x 160** (E: Table 10 pixel counts sum to 1,843,200 = 72 x 160 x 160) | hybrid CNN + transformer U-Net, from scratch, weighted CE equal weights; one run (plus 3-fold CV on train: IoU 0.4653 +- 0.0099) | mIoU 0.493, mDice 0.593, wIoU 0.912, acc 0.950; per class F1 crack 0.2975 (IoU 0.175), inactive 0.5945 (IoU 0.423), gridline 0.3479 (IoU 0.211); baselines VGG-UNet 0.459, FPN 0.458, Res-UNet 0.416 (Tables 10, 11) |
| **Hanifi et al. 2025, IEA/AIE** (`doi:10.1007/978-981-96-8892-0_4`) | `20221008` re-split 551 / 67 / 77, **not released** | `20221008`, 29 classes | IoU pooled over the test images; group means over 12 features / 16 defects / 29, **absent class = 0**; fw-IoU | 208 x 304 output (416 x 608 input) | 6 Keras models, weighted CE (hand-set), early stopping on val loss; one run each | VGG16-UNet: defects (16) 0.326, features (12) 0.663, crack 0.335, inactive 0.550 (note A10). Our P19 reproduction on the release split, 3 seeds: crack 0.352 +- 0.008, inactive 0.469 +- 0.032 (`results/p19/README.md`) |
| **Torpey, Pratt, Klein 2024** (`arxiv:2402.17611`) | release `20220723`, 642 images; split not stated in the sections read (S: the release split, 511 / 65 / 66) | `20220723`, 28 classes | mIoU and wIoU (frequency-weighted); class set of the mean not stated; **best checkpoint on validation mIoU**; crack IoU only as block-centred Tukey intervals (Fig. 6) | 512 | DeepLabV3 R50, custom weights, 1,000 epochs; several runs for most regimes | R0 (Pratt's DeepLabv3+ R34) 0.506; random init 0.486; COCO 0.544; CCT 0.550; U2PL 0.448 (Table 1) |
| **E-SCDD / PV-DDPM**, Hanifi et al. 2025 (`arxiv:2511.09604`) | own E-SCDD test | E-SCDD, 30 classes | anomaly detection (AA-CLIP pixel AP / AUC) only | | | no segmentation score (doc 17 §3) |

### 2c. Found and excluded (not our images)
UCF-EL: MCX-Net `doi:10.1109/aimlsystems67835.2025.11330719` (mIoU 0.486 at 224 px), SegFormer `doi:10.1109/jphotov.2024.3450009`, EFSegNet `doi:10.1016/j.ecmx.2026.101847` (UCF-EL + LBNL PV-EL; mIoU 0.699 / 0.794), Hijjawi `doi:10.1016/j.solener.2025.114083`. PVEL-AD / PVEL-S: Saleh 2026 `doi:10.1016/j.compeleceng.2026.111338` (mIoU 97%, background included), Duan 2025 `doi:10.1016/j.energy.2025.136711`, Çalışan 2026 `doi:10.3390/su182010677`. DuraMAT / LBNL crack set: Elbahri 2026 `doi:10.1016/j.solener.2026.114362`, Sohail 2023 `doi:10.1016/j.egyr.2023.03.094`, Bramantyo 2026 `doi:10.1109/infinitys69204.2026.11666283`, MultiSolSegment `doi:10.1016/j.solener.2026.114469`. Classification only: Sharma and Mishra 2025 `doi:10.56042/ijpap.v63i11.20991`. Fielded modules, no benchmark score: Pratt 2025 ICTAS `doi:10.1109/ictas64866.2025.11155421`.

## 3. Which published test sets our full-pool models can be scored on (E)
Counted by stem name against `benchmark/splits/legacy.json` (pool 532 = legacy train + val; test50) and E1 `ext117/stems_eval.txt` (md5 5266806b, 106 lines); script `/home/noob/work/bench_int_io/public/overlap.py`, no image or mask opened.

| Release split | Cells | In our pool P532 | In legacy test50 | In E1 | Other |
|---|---|---|---|---|---|
| `20221008` train | 553 | 425 | **38** | **82** | 8 |
| `20221008` val | 70 | 52 | 4 | 13 | 1 |
| `20221008` test (Attention-Based SegNet, Ramadan) | 72 | **51** | 8 | 11 | 2 |
| `20220723` train | 511 | 427 | 38 | 38 | 8 |
| `20220723` test (Torpey, S) | 66 | **51** | 8 | 5 | 2 |

- Our full-pool models train on all 532 pool cells, so 51 of 72 (and 51 of 66) release-test cells are training cells for them. Scoring them there is leakage; the published number is over all 72, so the 21 leftover cells would not match it either. (S)
- The reverse is also closed: a model trained on a release train split for a like-for-like row would have trained on 38 of the 50 test cells and 82 (or 38) of the 106 E1 cells, i.e. burn both sealed sets. (S)
- So the public comparison is the legacy test set or nothing. (S)

## 4. Comparability verdict per row (for models trained on P532, v1.1 labels, 512 px, final weights)
| Row | Verdict | Conditions that must be met, or why not |
|---|---|---|
| Pratt 2023 (median IoU, 3 defects + 2 features) | **comparable with conditions** | score the 50 cells on the old masks (v0) at 512 px; per-image IoU, median over cells; rule A as the like-for-like reading with B and C printed; "spacing" defined as the union of sp multi, sp mono, sp dogbone (S: the paper names one "spacing" class, the 24-class list has three); our training set is 532 cells (their 478; +54 val cells), our labels revised; theirs are single runs with unstated selection |
| SEiPV-Net (pooled pixel metrics) | **comparable only as a family of readings** | averaging undefined: print pixel accuracy, pooled micro IoU = acc / (2 - acc), fw-IoU, support-weighted F1, per-image mean IoU with absent-and-unpredicted = 1, class mean over GT classes; never one headline. Our older L3 already reached F1w 0.933 against their 0.9426 and per-image absent=1 0.840 against their 0.8604 (`results/seipv_compare/README.md`, old recipe, descriptive) |
| PV-S3 CSB-S1 (pooled 3-class IoU) | **comparable with conditions, unverified split** | pooled per-class IoU, P, R, F1 for crack, gridline, inactive on old masks; print both background conventions (all pixels; background-GT pixels dropped = `pvs3`); their split and resolution are unstated, so the row says "split assumed = release split" |
| Attention-Based SegNet, Ramadan, Hanifi, Torpey | **not comparable** | test sets overlap our training pool (section 3); also 29 or 28 classes, other resolutions (160, 208 x 304), absent = 0 (Hanifi), best-val selection (Torpey). Printed in the thesis table as "other test set, not comparable", never beside our numbers as a ranking |
| any row on E1 | **no published comparator** | public-protocol numbers on E1 are ours only, labelled as such |

## 5. Label versions: what differs and what it does to a fair comparison
- **Versions in play** (handbook 17 §2; `benchmark/LABELS_V11.md`):
  - v0 = BenchmarkEL `20211104` masks (`labeled/masks_coded` on gaint): what Pratt 2023, SEiPV-Net and (S) PV-S3 scored on.
  - v1 = our `masks_escdd`: the `20221008` crack / inactive labels via E-SCDD, classes >= 24 mapped back.
  - v1.1 = v1 with scuff and star pixels set to ignore and one BMRK mask fixed: our training and scoring labels.
  - `20221008` / E-SCDD 29 / 30 classes: what Attention-Based SegNet, Ramadan and Hanifi scored on; E1's own masks (class 24 to sp mono, 25 to 28 to ignore).
- **Size of the v0 to v1 change** (E, handbook 17 §5.8, §5.9; 05 §7; `results/pratt_compare/summary.txt`): crack labels joined and widened (on 265 cells: crack px +21%, width 2.17 to 2.52 px, fragments 4.2x fewer); on the 50 test cells 42 masks changed, crack px +39%, crack IoU old vs new 0.745 pooled; test cells with gridline 37 (v0) against 45 (v1); with inactive 17 against 16; with crack 50 against 48 (46 in v1.1).
- **Consequences** (S):
  1. The test50 public rows are reproducible exactly on v0 for our models. That is the like-for-like scoring. It needs a label-set option v0 in the scorer (section 6).
  2. A model trained on the revised (wider, joined) crack convention loses crack precision against thin, dotted v0 labels. Our old P-series check shows the size: the same checkpoints score crack IoU 0.05 to 0.07 higher on revised labels (P3). So a v0 row understates our crack quality, and any "beats Pratt on crack" is conservative on v0, never inflated.
  3. Published models cannot be re-scored on v1.1 (no weights). So v1.1 rows are ours only; the comparison table pairs v0 with v0.
  4. Scuff / star ignore (v1.1) touches 2 test cells, 236 px, all crack in v1 and v0-era labels. Irrelevant on v0 (no ignore).
  5. No test50 row is made impossible by label version. The `20221008`-split rows are impossible by split (section 3); their labels would actually match ours for crack and inactive.
  6. E1 has only `20221008` labels: same crack convention as our training labels, so no label shift there; but no published row.

## 6. Metric code: our scorer against what the published metrics need
### 6a. Our scorer (E, read 19 Nov)
- `bench/m0core.py` (line-identical copy of `m0_audit.py` d36f7438): `cell_stats(pred, gt, keep)` builds one 24 x 24 confusion matrix per cell over kept pixels at native 512 x 512 (ignore 255 not scored), plus crack rel@2 counts (EDT, radius 2), crack and inactive components (8-connected). `agg()` sums the matrices over cells: per-class IoU = TP / (TP + FP + FN), NaN when the denominator is 0; `miou_rob` = mean over the 13 robust classes with GT; relP@2, relR@2, relF1@2.
- `scripts/bench_score.py records` writes these per-cell records (the `conf` key is the full per-cell matrix) for a named set; sealed sets need `--opening`. `bench/cellmeta.py` label sets: `set`, `v11`, `v1`, `manifest`. **No v0 (old masks) option.**
- `scripts/bench_read_w1.py` and `bench/w1read.py` are the CV5 out-of-fold read with the two-stage bootstrap and A/A margin; **w1read refuses sealed sets**, so an opening needs its own read script (as `harness/c3x/run_read_c3x.sh` for the c3x read; and the frozen readouts of E1 openings #5 to #7).

### 6b. Differences, per published metric
| Published metric | Ours today | Difference | What to add |
|---|---|---|---|
| Pratt median IoU (per image, per class, median over cells) | pooled IoU over cells | unit and aggregation; absent rule | per-cell IoU from each cell's `conf`; median; rules A / B / C; merged-class IoU for "spacing" |
| Pratt median recall | pooled recall | same | per-cell recall, median, rule A |
| PV-S3 per-class IoU, P, R, F1 (3 classes) | pooled IoU, P, R | same unit; background rule unknown | the `pvs3` variant: drop GT row 0 (background) from the pooled matrix before IoU, P, R |
| SEiPV-Net mIoU / IoU / Dice / F1 / P / R | pooled per-class only | undefined averaging; background included | pixel acc = trace / sum; micro IoU = acc / (2 - acc); fw-IoU = sum_c IoU_c x GT_c / sum GT; support-weighted F1; per-image mean IoU with absent-and-unpredicted = 1 and with absent skipped; class mean over GT classes, with and without background (all already in `results/seipv_compare/miou24.py`, md5 787e920e) |
| Attention-Based SegNet, Ramadan, Hanifi, Torpey | | other test sets | none (not comparable); resolution changes (160, 208 x 304) are not implemented on purpose |
| old masks v0 | v11, v1 | label set | `cellmeta` / `sets` option `v0` = `<labeled>/masks_coded`, no ignore, 582 legacy cells only, manifest md5 pinned; values 0 to 23 (asserted by `cell_stats`) |

### 6c. The module to build (spec; CPU only; for the opening's read)
`bench/public_metrics.py`, numpy only, input = the per-cell records of `bench_score.py records` (no new dump format):
```
C_s            = np.array(rec[s]["conf"]).reshape(24, 24)        # per cell s; rows = GT, cols = pred
merge(C, S)    : tp = C[S][:, S].sum(); gt = C[S, :].sum(); pr = C[:, S].sum()   # S = list of class ids
iou_cell(s, S) : tp / (gt + pr - tp) if gt + pr - tp > 0 else None
pratt_median(cells, S, rule):
    A: median of iou_cell over cells with gt > 0
    B: as A, but cells with gt == 0 score 0
    C: as A, but cells with gt == 0 score 1 if pr == 0 else 0
pratt_recall_median(cells, S): median over cells with gt > 0 of tp / gt
classes: crack [14], gridline [15], inactive [11], ribbons [4], spacing [1, 2, 3]; "avg defects" = mean of the 3 defect medians
pooled(cells, drop_bg_gt): C = sum_s C_s; if drop_bg_gt: C[0, :] = 0; per class IoU, P, R, F1 for [14], [15], [11]; mean of 3
seipv_family(cells): pixel_acc, micro_iou = acc / (2 - acc), fw_iou, f1_weighted, per_image_miou_absent1, per_image_miou_skip,
                     miou_gt_bg, miou_gt_nobg (formulas of miou24.py summarise(), copied with its md5 in the header)
```
Tests before the opening (S): synthetic fixtures for every rule; and equality with `scripts_cv02/pratt_scores.py` (md5 2ebb158b) and `miou24.py` run on the same **open** dumps (cv5v3 held-out fold dumps of the c3x or c3_pf runs, v1.1 labels). No sealed cell is needed to test the code.

## 7. What earlier (already opened) reads say about where we stand (descriptive; old models, not blind)
- `results/pratt_compare/README.md` (13 Oct, P-series L3 100%, 5 seeds, old masks, rule A): crack 0.354, gridline 0.303, inactive 0.443, mean 0.367, against Pratt 4c 0.25 / 0.20 / 0.38 (0.28). Rules B / C give means 0.202 / 0.538 for the same models.
- `results/seipv_compare/README.md` (13 Oct, same models): pixel-weighted F1 0.933, per-image mean IoU absent = 1 0.840, fw-IoU 0.886, plain class mean 0.46 to 0.51; SEiPV-Net F1 0.9426, "mIoU" 0.8604.
- These were part of the uncounted test reads before 24 Oct (`benchmark/test_openings.md` §A). The final and full-pool PF models have never been scored on test50 or E1. (E)

## 8. E1 or the legacy test 50 as primary for the final-model claim (S)
**E1 primary, legacy test 50 secondary (public-comparison track).** Reasons:
1. **Leakage.** The legacy test has 8 cells that are the same physical cell as a pool cell, 7 neighbouring crops and 19 more sharing a module (`results/stageC/SPLIT_INTEGRITY.md` §5b); our full-pool models train on all of those pool cells. E1 has no pixel link to any training image id (protocol §11 item 10). A final-model claim on test50 is an in-distribution claim with known leakage; on E1 it is a generalisation claim.
2. **Prior looks.** Test50 has 18 counted openings and many uncounted reads of the house recipe (`test_openings.md`); E1 has 7 registered openings, 3 looks at one contrast, and was used once to judge development instruments (R0, ledger line of 15 Nov). The final candidate and the full-pool PF have never been scored on either set.
3. **Labels.** E1's masks are the `20221008` convention our models are trained on; test50's public rows need the old masks.
4. **Selection.** Test50 was hand-picked for defects (Pratt 2023 §3.2); it suits a public, continuity table, not a deployment claim.
5. **Costs of E1, stated:** no published comparator; 101 of 106 cells CSIR; about 58 to 62 half-cut cells while the pool has none (a layout shift the CV5 work could not measure); only 10 inactive cells, so E1 inactive IoU is a reported number, not a primary; crack is in 32 cells.
6. **Consequence:** the public comparison (what the user asked for) can only come from test50, so the opening covers both sets once: E1 decides the final-model claim; test50 gives the public table and one secondary contrast that decides nothing alone.

## 9. Open questions
1. **Test50 opening #19** (lead and user): D `brief` 1 says no further test50 opening is planned. The public table needs exactly one. Go or no go?
2. **E1 opening** (user): protocol Open 3 awaits the user's confirmation of the one end-of-project E1 opening (at most 3 candidates). Is this it? If yes, the T3b few-shot track can only run after it (protocol §11 item 2).
3. **Like-for-like training set** (lead): our full-pool models train on 532 cells; the published rows trained on the 478 train cells. Add PF and final candidate trained on the legacy 478 (10 runs on cv02) for an exact public row, or disclose the +54 val cells? (S: disclose; the extra runs buy little.)
4. **PV-S3's CSB-S1 split** is unstated; the row stays "assumed release split" unless the authors' repository shows the lists (not checked: outside the tools allowed).
5. **"Spacing"** in Pratt's 5-class table: union of the three spacing classes is our reading; the paper does not say.
6. **Ensembles on sealed sets** need a code change: `bench_infer.py` refuses `--logp` on sealed sets and `bench_ens_dump.py` refuses sealed sets. Published rows are single models, so single models are the public rows; 5-seed ensembles only if the lead wants them and a reviewed change lands before the opening is frozen.
