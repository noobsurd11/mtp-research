# P9 protocol: P8's arms with the 12k-cell external unlabelled pool (L3 base)

Drafted 10 Oct 2026, 22:35 IST, before any P9 run. Locked once the commit that adds it exists. Launch needs the user's go-ahead.

## Why this exists
Interim results (P7 5/9 runs, P8 5/9) show no detectable gain from the unlabelled loss with the in-domain pool. That pool is the other 431 training cells with labels hidden: about 9× the labelled set, and from the same cells' distribution.

ALHVR-style methods are normally reported with unlabelled pools 10–100× larger. The external pool is 11,938 cells. It was prepared on 6 Oct (commits `0136855`, `46dfe92`):
- filtered against labelled cells;
- stems checked disjoint from train/val/test at startup.

This experiment asks whether the null comes from the method or from the pool size. The question was chosen after seeing interim P7/P8 numbers. That is disclosed here. It applies equally to every P9 arm.

## Fixed for all arms
P8's protocol verbatim, except:
- **Unlabelled set:** `data.unlabeled_pool=external`, which uses `data/splits/external_unlabeled.txt` (11,938 cells, 512 px grayscale) instead of the 431 hidden-label training cells.
- **Same code:** commit `0367079`, already on cv02 (`/tmp/noob_el/el_p7`).
- Base L3: `model.name=smp_unetpp loss.supervised=ce_dice`.
- Labels: revised masks; seed-0 split; 10% labels (47 images).
- Batch 8 + 8; λ schedule as P8; 20,000 steps; seeds 0–2.
- Hardware: cv02 RTX A6000, at most 2 runs per GPU.
- Evaluated weights: EMA teacher, identical for all arms.

## Arms
| Arm | Unlabelled loss | Pool |
|---|---|---|
| A (reference, no new runs) | none (P6 L3 10%) | – |
| Bx | `confidence_ce`, t_pos 0.95 | external |
| Cx (proposed) | `tolerant_pl`, R = 2 px | external |
| Dx (loss-off control) | Cx with λ_final = 0 | external |

Dx differs from P8's D only in what the unlabelled loader reads, which affects random-number consumption. It is run so that Cx − Dx is a clean paired contrast.

## Metrics
As P8:
- **Primary:** test crack IoU, test inactive IoU, test crack relaxed F1@2. All use argmax and revised labels.
- **Secondary:** AP with bin-0 share, val, relaxed precision@2.

## Decision rules
1. **Cx helps** if mean(Cx) − mean(Dx) on any primary metric is > 0.01 and > 2·√((sd_Cx² + sd_Dx²)/3), with no primary metric worse by the same rule. Bx vs Dx uses the same rule.
2. **Cx beats Bx** under the same rule.
3. **Width check:** if Cx's crack gain comes with crack relaxed precision@2 falling by > 0.05 against Dx, flag it as possible fattening.
4. **Gap closed:** (Cx − Dx) / (L3@100% − Dx), per primary metric.
5. **Pool-size effect (secondary):** (Cx − Dx) − (C − D) against P8. Same code and seeds, so this is the change caused by the pool.

## Required robustness reporting
- The image bootstrap and leave-top-3-cells-out check from P6 exploratory 5, on every rule-1 contrast.
- **Source split.** The pool is 77% CSIR and 23% ARTS, with no CFVS, BMRK or SDLE. Test is 18 CFVS, 13 ARTS, 10 BMRK, 8 CSIR and 1 SDLE. Report Cx − Dx crack IoU separately on the 21 CSIR+ARTS test cells and on the other 29. This is descriptive, not a rule.

## Not claimed
- Tuning of R, t_pos, λ or pool filtering.
- Results beyond this split and dataset.
- Any statement about the pool's label quality. The pool is unlabelled.
