# coach review of `protocol_mim5.md` v1 (code `el_f1` 603e0d5)

coach, 29 Oct 2026. **Verdict: APPROVED for the MIM pretraining launch**, after one change (A1) recorded as v1.1. Fine-tune launch is approved once F1-F2 are logged; no further review needed for them.

## A1. R3 threshold 0.95, not 0.85 (my error)
- I set 0.85 without counting. Counts from the neardup and samepos JSONs, against val, test and ext117 queries (E, gaint `critic4_skcdf/neardup`):

  | r_hp threshold | pool cells dropped | ARTS | CSIR |
  |---|---|---|---|
  | 0.85 | 780 | 624 | 156 |
  | 0.90 | 389 | 341 | 48 |
  | 0.93 | 167 | 149 | 18 |
  | 0.95 | 50 | 36 | 14 |

- At 0.85 the rule removes 23% of the pool's 2,734 ARTS cells. That is the same-position shading family, which D4 checked at full resolution and found to be different cells (0.89-0.93). It would bias the pool away from ARTS, the source with no labelled crack at 5%.
- 0.95 still drops every exact or near copy (train-pool twins sit at 0.9997-1.0) and the top three test candidates (0.953-0.959). R1 (modules) and R2 are unchanged.
- Rebuild the list, put the counts and the new md5 into v1.1, then launch.

## Smoke (E, runner's report; `reports/f1/smoke_v1`)
- **Loss:**
  - 0.917 at step 20, 0.501 at 340 while frozen;
  - 0.499, 0.497 and 0.478 at 360-400 across the unfreeze, so no spike;
  - 0.427 at 560.
- **Encoder:**
  - grad norm 0 while frozen, then 0.37-0.46;
  - enc_lr ramps from 3.4e-6;
  - clip rate 0.
- **Held-out monitor:** 0.916, 0.499, 0.404.
- **Memory and speed:** 8.0 GB at batch 16; about 30 GB at batch 64. So batch 64 on an A6000 and batch 32 on gaint, per C3.
- **Width:** 512 kept. w256 gave only 1.16x; my FLOP estimate overstated the decoder share.
- **Code:** enc_lr_factor, the monitor disjointness check and the `{models: {model}}` save format are as required; 264 tests pass.

## Fine-tune gate (no new review)
- **F1.** `identity_f1.txt` shows I1 (el_m vs 603e0d5) and I2 (`encoder_init=mim_step0.pth`) bit-identical for 1,000 steps, on the machine the fine-tunes run on. If that machine is not gaint, repeat I1/I2 there.
- **F2.** A 200-step fine-tune smoke with `encoder_final.pth`:
  - the log has "Encoder initialised from ... (N tensors, md5 ...)" with the md5 matching `encoder_final.md5`;
  - the loss is finite.

## Machine
- Pretraining may run on gaint now. The rule binds the fine-tunes only; the encoder file travels with its md5.
- Both fine-tune arms run on one machine type. gaint is team-lead's call because of the user's jobs.
