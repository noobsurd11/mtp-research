# P18 protocol (EXPLORATORY): the BsM recipe at 10% and 20% labels

Locked 13 Oct 2026, ~17:40 IST, before any P18 run. The user's go: "cool, youve got 3hrs to wrap up,, complete whateer left or experiment whatever you think useful then we ill move to the presentation part, analysis left ig, but check once and go" (13 Oct ~17:25 IST). Claude picked this experiment from the open decisions (doc 15 §3, decision 2).

## What I had seen when locking
Everything up to P17:
- P13: at 5%, BsM5 (hard pseudo-labels ≥ 0.95, separate BN, CutMix) was the best SSL arm on crack. On 5 seeds (Amendment 2) BsM5 − A5c is +0.029 / +0.107 / +0.045.
- P16: the Cs recipe (tolerant pseudo-labels, separate BN, CutMix off) is n.d. against supervised at 20%, 50% and 100%.
- P17: decoupling the decoder changes nothing detectable on BsM5.

**The arm choice is test-informed:** BsM was chosen because it did best on P13's test cells. So P18 is **exploratory**. Its rule-1 arithmetic is reported, but it gives no confirmatory verdict and no claim rests on it alone.

## Question
Does the recipe that worked best at 5% still beat supervised at 10% and 20% labels? Is P16's "no gain from 20% up" a property of the label fraction or of the Cs recipe?

## Code and runs
- Code: `bac5264` (cv02 deployment `el_p13`), as BsM5 and P16 Part A. No code change.
- Options: BsM5's verbatim (`scripts_cv02/p13a2_queue.spec`), with `data.labeled_fraction` and the seed changed. Unlabelled pool: in-domain (the train cells not labelled: 431 at 10%, 383 at 20%).
- 20,000 steps, batch 8 + 8, EMA teacher's final weights, re-score on revised labels; one run per GPU.

| Arm | Run names | Labels | Seeds | GPUs |
|---|---|---|---|---|
| **BsM20** | `p18_BsM_20pct_s<k>` | 20% (95 cells) | 0–4 | 0–4 |
| **BsM10** | `p18_BsM_10pct_s<k>` | 10% (47 cells) | 0–2 | 5–7 |

**References (existing, cv02):**
- A20 = P6 `p6_L3_20pct` s0–2 (`824fab0`) + P16 `p16_A_20pct` s3–4 (`bac5264`), as pooled in P16.
- A10 = P6 `p6_L3_10pct` s0–2 (`824fab0`).
- S20 = P16 `p16_S_20pct` s0–4 (Cs recipe, `d51b60f`).

**Seeds:** 5 at 20% (the standing rule for effects < 0.05), 3 at 10%. The 3 hours available allow 8 runs at one per GPU, so 10% stays a 3 vs 3 descriptive point.

## Pipeline check
λ = 0 until step 2,000. With the separate forward the student is then the supervised run (P13 audit). So `loss_sup` of BsM20 s3–4 should equal `loss` of `p16_A_20pct_s3–4` (same commit, same machine) at steps 50 to 2,000. A mismatch is reported and looked into; it does not change the arithmetic.

## Analysis (all exploratory)
Primaries as P13 (test crack IoU, inactive IoU, crack relF1@2; argmax, revised labels), with P8 rule-1 arithmetic Δ > max(0.01, 2·√((sd_A² + sd_B²)/3)).
1. **BsM20 − A20** (5 vs 5).
2. **BsM10 − A10** (3 vs 3).
3. Descriptive: BsM20 − S20, which changes two things (hard vs tolerant pseudo-labels, CutMix on vs off), so the difference cannot be attributed to either. Also gap closed, and the label-fraction curve with the BsM points (5, 10, 20%).
4. Width check: relP@2 drop > 0.05 flagged.

**Robustness:**
- image bootstrap (2,000) and leave-top-3-out;
- with and without test cell `CSIR_00070_r8_c4`;
- E1 per-cell metrics on test and the 106-cell extension;
- conf_frac at steps 4,000 and 20,000.

## Not claimed
- Any confirmatory verdict: the arm was picked after seeing test results.
- 50% or 100% labels; tuning of λ, t_pos or CutMix; gaint replication; other split seeds.
