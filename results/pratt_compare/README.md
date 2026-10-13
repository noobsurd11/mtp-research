# Our models in Pratt 2023's metric convention (descriptive, 13 Oct 2026)

**Why:** the deck needs "where do we stand against the published BenchmarkEL numbers?". The old-era comparison (handbook doc 05 §3.1, `analysis/papers_metrics.md` §1.4) predates the P-series recipe.

**How (`summary.txt`):**
- Read-only inference on cv02 (`scripts_cv02/pratt_scores.py`): 23 runs, final weights (teacher for Mean Teacher runs), argmax, bf16, the 50 test cells.
- Per-image TP/FP/FN for crack, gridline and inactive (`pratt_a.json`), against the old labels (`dataset_20211104`, which the paper used) and the revised labels.
- Pratt's convention: per-image IoU, then the median over test cells. Rule A: cells without the class in GT are left out.
- Sanity: pooled crack/inactive IoU from these counts equals the re-score JSONs exactly, on both label versions.

## Old labels (the paper's), rule A, mean ± sd over seeds
| Model | crack | gridline | inactive | mean of 3 |
|---|---|---|---|---|
| supervised 100% (L3, 5 seeds) | 0.354±0.004 | 0.303±0.010 | 0.443±0.028 | **0.367±0.012** |
| supervised 10% (L3, 3 seeds) | 0.240±0.016 | 0.218±0.009 | 0.272±0.039 | 0.243±0.013 |
| supervised 5% (A5c, 5 seeds) | 0.193±0.020 | 0.147±0.010 | 0.160±0.082 | 0.167±0.026 |
| SSL 5%, CsM5 (5 seeds) | 0.170±0.029 | 0.159±0.033 | 0.360±0.033 | 0.230±0.014 |
| SSL 5%, BsM5 (5 seeds) | 0.194±0.032 | 0.173±0.032 | 0.352±0.031 | 0.239±0.023 |
| Pratt 2023 4c (DeepLabv3+, custom weights; headline) | 0.25 | 0.20 | 0.38 | 0.28 |
| Pratt 2023 2a (U-Net, equal weights) | 0.15 | 0.32 | 0.09 | 0.19 |

Test cells with the class (old labels): crack 50, gridline 37, inactive 17.

Revised labels (same models): supervised 100% 0.461 / 0.281 / 0.494, mean 0.412; A5c mean 0.192; BsM5 mean 0.286 (`summary.txt`).

## Caveats
- **The paper's rule is inferred.** The paper does not state how absent classes are handled; rule A is the reading its numbers allow (`analysis/papers_metrics.md` §0). Under rule B (absent = 0) every mean drops to 0.10–0.24; under rule C it rises to 0.44–0.58.
- **The paper's numbers are read off its Fig. 7** (about ±0.01), and they are single runs with partly unstated training details.
- **Which release the paper used** is an open question (doc 05 version caveat).
- **Our P-series models were trained on the revised masks** and are scored here on the old ones; the paper trained and scored on the old masks.
- **Per-image medians and pooled IoU disagree.** On old labels, CsM5's median crack IoU (0.170) is below A5c's (0.193), while its pooled crack IoU is above (0.317 vs 0.304, revised labels). The locked rules use pooled IoU.

## Reading
Under the paper's likely convention and on its labels, the P-series supervised recipe at 100% labels is above the paper's headline model on all three classes (crack 0.354 vs 0.25, mean 0.367 vs 0.28). It is not a like-for-like benchmark claim (caveats above).
