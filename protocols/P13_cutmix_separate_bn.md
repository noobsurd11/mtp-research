# P13 protocol: Mean Teacher with the two literature ingredients our pipeline lacked (CutMix on unlabelled images, BatchNorm kept clean of unlabelled images), at 5% and 10% labels

Locked 11 Oct 2026, ~11:55 IST, before any P13 training run (only the 100-step GPU smoke runs, `smoke_*`, had run). The user asked on 11 Oct whether the SSL setup is doing something wrong ("be skeptical ... look if anything wrong with our experiment"). This protocol tests the two concrete deviations the audit found. It falls under the SSL work on all machines that the user approved on 10 Oct.

What I had seen when locking:
- All P8, P9 and P10 results (`results/p8–p10`).
- P12 gaint seeds: gCm5 s3 0.337 / 0.400 / 0.779; gDm5 s3 0.270 / 0.249 / 0.670; gDm5 s4 0.283 / 0.254 / 0.688 (crack IoU / inactive IoU / crack relF1@2).
- The BN-recalibration diagnostic on P10 and P6-10% checkpoints (`results/p13_audit/bn_diag.*`). Crack / inactive IoU, mean of 3 seeds, as trained → BN recomputed on all 478 train images:
  - A5 0.298/0.277 → 0.310/0.302;
  - D5 0.243/0.243 → 0.250/0.268;
  - Dx5 0.275/0.198 → 0.285/0.282.

  Recalibration lifts every arm by about +0.01 crack, but the D5 − A5 gap stays at −0.06. So the handicap is in the trained weights, not in the evaluation statistics.
- No P11 result, no cv02 P12 result.

## Why this exists (audit, 11 Oct)
No implementation bug was found in the Mean Teacher step. Checked:
- teacher and student views share geometry;
- the EMA covers BN buffers;
- the teacher is detached and in eval mode;
- the evaluated weights are the teacher's;
- no unlabelled/test overlap.

Two design choices separate our pipeline from the semi-supervised segmentation methods that report gains.

1. **The perturbation is weak.**
   - The student's strong view is ±0.25 brightness/contrast jitter plus mild noise.
   - Through training, the unlabelled loss stays about 10× below the supervised loss, e.g. 0.004 vs 0.038 at step 20,000 in P10 C5 s0.
   - The teacher is confident on 94–97% of unlabelled pixels, and the student already agrees with it there.
   - French et al. (BMVC 2020) show that segmentation consistency needs mask-based mixing (CutMix); standard augmentation consistency gives little. CutMix copies pixels and never resamples them, so it is label-safe for 1–2 px cracks.
2. **Unlabelled images share the student's BatchNorm batch with labelled images.**
   - With the loss off, this alone costs the matched pipeline at 5% −0.015 to −0.028 crack IoU against supervised (gaint gDm5 s3/s4 vs A5).
   - Swapping the unlabelled pool moves the loss-off control by up to 0.09 IoU (P9, P10).
   - Recomputing BN statistics after training does not remove it.
   - So: forward the unlabelled images separately, and keep them out of the BN running statistics. At λ = 0 the student then *is* the supervised run (tested bit for bit).

## Code
- Commit `bac5264` (branch `p13` on gaint; deployed to cv02 `/tmp/noob_el/el_p13`). The P12 code `24590fb` plus two opt-in switches; defaults are unchanged bit for bit:
  - `ssl.student_forward=separate`: labelled forward, then unlabelled forward inside `frozen_bn_stats`.
  - `ssl.cutmix_p=0.5`: per unlabelled image, a box from the next image of the batch is pasted into the strong view. The teacher's logits (weak view) get the same box.
    - Box area U(0.02, 0.4) of the image, aspect U(0.3, 3.33), as UniMatch.
    - The draws are a pure function of (seed, step).
- Tests: `tests/test_ssl_split.py`; 197 pass.
- GPU smoke on cv02: 100 steps; the separate-forward λ = 0 student equals the supervised run bitwise.

## Fixed for all arms
P12's options verbatim:
- **Data:** in-domain pool only; revised masks; split seed 0.
- **Labelled images:** `ssl.labeled_aug=supervised`.
- **Model and losses:** L3 base (`smp_unetpp`, `ce_dice`); `tolerant_pl` with R = 2, or `confidence_ce` (t_pos 0.95).
- **Training:**
  - batch 8 + 8;
  - λ 0 for 2,000 steps, then a ramp over 2,000 steps to 1.0;
  - 20,000 steps;
  - the EMA teacher's final weights are evaluated;
  - `OMP_NUM_THREADS=4`.
- **Added:** `ssl.student_forward=separate` in every P13 arm.

No tuning: `cutmix_p`, the box law and every other value are fixed here.

## Arms
| Arm | Run names | Unlabelled loss | CutMix | Labels | Seeds | Hardware |
|---|---|---|---|---|---|---|
| Ds5 | `p13_Ds_5pct` | `tolerant_pl`, λ_final = 0 | – | 5% (23) | 0–2 | cv02 |
| Cs5 | `p13_Cs_5pct` | `tolerant_pl` | no | 5% | 0–2 | cv02 |
| CsM5 | `p13_CsM_5pct` | `tolerant_pl` | 0.5 | 5% | 0–2 | cv02 |
| BsM5 | `p13_BsM_5pct` | `confidence_ce` (hard PL, ≥ 0.95) | 0.5 | 5% | 0–2 | cv02 |
| Ds10, Cs10, CsM10, BsM10 | `p13_*_10pct` | as the 5% arms | as above | 10% (47) | 0–2 | cv02 |
| gDs5 | `p13_gDs_5pct` | as Ds5 | – | 5% | 3–5 | gaint |
| gCsM5 | `p13_gCsM_5pct` | as CsM5 | 0.5 | 5% | 3–5 | gaint |

**Supervised references:**
- 5%: P12 `p12_A_5pct` (A5c, cv02, seeds 0–2).
- 10%: P6 `p6_L3_10pct` (A10, cv02).
- gaint: P10 `p10_A_5pct` (seeds 0–2).

**Scheduling**
- **cv02:**
  - One queue, chained after P12's supervised queue has launched, plus 5 minutes.
  - At most 3 runs per GPU, and only on a GPU with < 1,000 MiB used.
  - Order: CsM5, BsM5, Ds5, Cs5, then CsM10, BsM10, Ds10, Cs10.
- **gaint:**
  - Two sequential lanes after the P12 lanes finish, each run waiting for < 20,000 MiB used.
  - Lane 1: gCsM5 s3–5. Lane 2: gDs5 s3–5.
- Training is deterministic per machine; co-location affects speed only.

## Metrics
As P8–P12:
- **Primary:** test crack IoU, inactive IoU, crack relF1@2 (argmax, revised labels).
- **Secondary:** AP, bin-0 share, relaxed precision@2.

## Decision rules (cv02; each label fraction separately)
1. **Pipeline check (descriptive):**
   - Ds student vs A (P12 A5c, or P6 A10): are the final student weights bitwise equal? Expected yes at 5%. At 10% A10 ran with P6 code `824fab0`; equality is checked, not assumed.
   - Ds (teacher) − A: the EMA effect alone.
2. **The loss helps:** CsM − Ds, BsM − Ds and Cs − Ds, under P8 rule 1 (Δ > max(0.01, 2·√((sd_A² + sd_B²)/3)) on any primary, no primary worse).
3. **SSL beats supervised:** CsM − A, BsM − A and Cs − A under the same rule. Credited only if that arm passes rule 2.
4. **CutMix effect:** CsM − Cs, rule-1 arithmetic.
5. **Tolerant vs hard under CutMix:** CsM − BsM, rule-1 arithmetic.
6. **Separate-forward effect (descriptive; P12 ran at `24590fb`, whose joint path is unchanged in `bac5264`):** Cs5 − Cm5 and Ds5 − Dm5 (P12, cv02).
7. **Width check:** relP@2 drop > 0.05 against Ds is flagged.
8. **Gap closed:** (X − A) / (L3@100% − A).
9. **gaint replication (descriptive):** gCsM5 − gDs5, and gCsM5 − A5 (P10 gaint). "Replicated" if each passing metric has the same sign and at least half the size. gaint never rescues a failed cv02 rule.

**Primary claims:** rules 2 and 3 for CsM5. Everything else is secondary; the number of contrasts is disclosed.

## Required robustness reporting
- Image bootstrap (2,000 resamples) and leave-top-3-out on every rule-2/3 contrast.
- Per-seed table with `rare_frac` from the training log at steps 4,000 and 20,000, as the collapse watch.

## Not claimed
- Tuning of CutMix, λ, t_pos, R.
- Feature-level perturbation.
- External pool.
- Pooling cv02 and gaint seeds.
- Results beyond this split.

## Amendment 1 (11 Oct 2026, ~13:00 IST, before any P13 run)

**Why:**
- The user set a one-day deadline for results.
- Their earlier standing rule asks for ≥ 5 seeds for effects < 0.05.
- GPU time is shared with two new experiments: P14 (tolerant supervision) and P15 (UCF-EL encoder transfer).

**Nothing new seen:** no P13 run had started; P11/P12 results unchanged since locking.

**Changes:**
- **5% only.** The 10% arms are dropped: supervised crack gains +0.002 from 10% to 20% (P6), so 10% has little crack headroom.
- **cv02 runs, 13 in all, in queue order:**
  - CsM5 seeds 0–4;
  - A5c seeds 3–4 (`p13_A_5pct`, supervised, same options as P12 A5c; the supervised path in `bac5264` equals `24590fb`);
  - BsM5 seeds 0–2;
  - Cs5 seeds 0–2.
- **Ds5 dropped.** With `student_forward=separate` and λ = 0, the student is bit-identical to the supervised run. This was verified on the GPU for 100 steps (`results/p13_audit/smoke_gpu.log`). Ds5 therefore equals A5c plus EMA evaluation.
- **Loss-off control:** rule 2 uses A5c (P12 seeds 0–2 plus P13 seeds 3–4) instead of Ds5. The EMA-only effect is not measured and is disclosed.
- **No gaint replication:** gaint runs P15 instead.

**Primary claim:** CsM5 − A5c on 5 vs 5 seeds, rule 1 arithmetic.
- Rule 3 (SSL beats supervised) and rule 2 (the loss helps) are now the same contrast.
- BsM5 − A5c, Cs5 − A5c, CsM5 − Cs5 and CsM5 − BsM5 are secondary.

**Added reporting:** the per-cell task metrics of the E1 evaluation (`to_human/proposal_reframe_2026-10-11.md`), labelled secondary.
