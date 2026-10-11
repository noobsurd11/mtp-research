# P16 protocol: SSL at 20%, 50% and 100% labels (cv02)

Part A locked 11 Oct 2026, ~16:50 IST, before any P16 run. Part B (the SSL arms) is locked by amendment once the user picks the SSL recipe, and before any SSL arm starts.

**Prompted by** the user (11 Oct, ~16:35 IST): "why we using 5 or 10% for ssl? ... try 20, 50 and 100".

What I had seen when locking:
- P11 (10%) and P12 (5%) results; P13 and P14 still training.
- The supervised label curve (P6 on cv02; P10 A5/A50 on gaint): crack IoU 0.298 / 0.396 / 0.398 / 0.437 / 0.471 and inactive IoU 0.277 / 0.294 / 0.347 / 0.427 / 0.429 at 5 / 10 / 20 / 50 / 100%.
- Labelled cells containing inactive: 2 (5%), 4 (10%), 9 (20%), 20 (50%). In-domain unlabelled pool: 455, 431, 383, 239, 0.

## Why this exists
- P8–P13 tested SSL only at 5% and 10%. There inactive is in 2–4 labelled cells and the teacher is weakest, so inactive was unmeasurable there by construction.
- Segmentation SSL benchmarks report 1/16 to 1/2 of the labels. We have no point above 10%.
- At 100% there is no in-domain unlabelled data. SSL there can only use the external pool (11,938 CSIR/ARTS cells), so it asks whether extra unlabelled data helps a fully supervised model.

## Part A: supervised references (cv02, worktree `el_p13` at `bac5264`)
P6's L3 options verbatim (`configs/supervised.yaml`, `smp_unetpp`, `ce_dice`, label-safe, revised masks, batch 8, 20,000 steps, split seed 0). P6's `config_used.yaml` for L3 20% equals P13's A5 config except seed and fraction (checked by diff), and the supervised path is unchanged from `824fab0` to `bac5264`. So P6 seeds 0–2 are pooled with the new seeds.

| Arm | Run names | Labels | Seeds (new) | Pooled with |
|---|---|---|---|---|
| A20 | `p16_A_20pct` | 20% (95 cells) | 3–4 | P6 `p6_L3_20pct` s0–2 |
| A50 | `p16_A_50pct` | 50% (239) | 0–4 | – (P10's A50 ran on gaint) |
| A100 | `p16_A_100pct` | 100% (478) | 3–4 | P6 `p6_L3_100pct` s0–2 |

Scheduling: one queue; 3 runs per GPU; only on a GPU with < 1,000 MiB used. GPU 5 now, then GPUs 0–2 when P14 frees them.

## Part B: SSL arms (to be locked by amendment)
Planned: 5 seeds each, separate-BN forward (so the supervised arm is the exact loss-off control), tolerant pseudo-labels.
- S20: 20%, in-domain pool (383).
- S50: 50%, in-domain pool (239).
- Sx100: 100%, external pool (11,938).
- Open: whether CutMix is on. That is the user's call (asked 11 Oct ~16:50).

## Rules (as P13)
- **Primary:** S − A at each fraction under P8 rule 1: Δ > max(0.01, 2·√((sd_A² + sd_B²)/3)) on any of test crack IoU, inactive IoU, crack relF1@2, and none worse. 5 vs 5 seeds.
- **Width check:** relP@2 drop > 0.05 flagged.
- **Gap closed:** (S − A) / (A100 − A).
- **Robustness:** image bootstrap (2,000 resamples) and leave-top-3-out on every primary contrast; E1 per-cell metrics and the 106-cell extension as labelled secondary.
- **Descriptive:** the SSL gain against label fraction, together with P11 (10%), P12 (5%) and P13 (5%), within cv02 only.

## Not claimed
- Tuning at any fraction.
- Other splits.
- Pooling with gaint.

## Amendment 1: Part B locked (11 Oct 2026, ~17:40 IST, before any P16 SSL run)

**User's choice (11 Oct ~17:00 IST):** "Pick on P13 val". CutMix on or off is decided by P13's validation numbers, never its test numbers.

**Seen at locking:**
- P16 Part A (supervised) runs had started; no P16 result exists.
- 3 of 13 P13 runs had finished (`p13_A_5pct_s3`, `s4`, `p13_Cs_5pct_s2`). None of their numbers was opened.

**Code:** branch `p16` at `d51b60f` = `bac5264` (P13) plus one change: SSL at `labeled_fraction` 1.0 is allowed when `data.unlabeled_pool=external` (it was refused). Partial-label paths are unchanged (`tests/test_p16_full_label_ssl.py`; full suite 204 passed). cv02 worktree `/tmp/noob_el/el_p16`.

**Recipe selection (automatic, `p16b_auto.sh` on cv02):**
- It waits until P13's CsM5 (seeds 0–4) and Cs5 (seeds 0–2) are all rescored with rc = 0, and until the Part A queue has launched everything.
- It reads only the `val/` entries of their re-score JSONs (revised labels, final weights).
- Score of an arm = mean over the three primaries (val crack IoU, val inactive IoU, val crack relF1@2) of the seed means.
- CutMix on (`ssl.cutmix_p=0.5`) if score(CsM5) > score(Cs5); otherwise off.
- It writes `reports/p16/selection.txt`, then queues the 15 SSL runs.

**SSL arms** (P13's Cs/CsM options verbatim, except fraction, pool and the selected CutMix setting; seeds 0–4):

| Arm | Run names | Labels | Unlabelled pool | Supervised reference |
|---|---|---|---|---|
| S20 | `p16_S_20pct` | 20% (95) | in-domain (383) | A20: `p6_L3_20pct` s0–2 + `p16_A_20pct` s3–4 |
| S50 | `p16_S_50pct` | 50% (239) | in-domain (239) | A50: `p16_A_50pct` s0–4 |
| Sx100 | `p16_Sx_100pct` | 100% (478) | external (11,938) | A100: `p6_L3_100pct` s0–2 + `p16_A_100pct` s3–4 |

- With the separate forward and λ = 0 the student is bit-identical to supervised (P13 Amendment 1), so A is also each arm's loss-off control. Rule 2 and rule 3 are therefore the same contrast, S − A.
- **Primary claims:** S20 − A20, S50 − A50 and Sx100 − A100, each under P8 rule 1, 5 vs 5 seeds. Three contrasts, all reported.
- Scheduling: one queue, 3 runs per GPU, only on a GPU with < 1,000 MiB used.
