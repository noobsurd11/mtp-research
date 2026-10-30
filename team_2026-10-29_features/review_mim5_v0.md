# coach review of `protocol_mim5.md` v0 (code `el_f1` fe31831)

coach, 29 Oct 2026. **Verdict: CHANGES.** v1 with C1-C6 applied as written is pre-approved: I reply APPROVED in one line once the new smoke (S1-S3) and the diff are in. No pretraining beyond the smoke before that.

## Smoke so far (E, gaint `reports/f1/smoke_mim_b16`)
- Loss 0.905 to 0.701 in 240 steps, finite.
- 8.0 GB at batch 16, about 38 samples/s on the shared GPU.
- Recon picture is aligned: busbars, fingers and corners land in the right patches; about 40% visible.
- The smoke unfroze the encoder at step 78, during the global warmup, so it did not exercise the protocol's 2-epoch freeze.

## Changes
- **C1. Pool exclusions are not applied.** Only `CSIR_00299_r8_c6` was dropped. Apply coach_mim5.md §B in `build_mim_pool.py`, reading the two neardup JSONs (copied with md5):
  - drop every cell whose (source, module) is a val, test or E1 module (196 / 88 / 144 by my count, overlapping);
  - drop the 11 ext117 stems in the pool;
  - drop every pool cell with r_hp >= 0.85 to a val, test or ext117 query;
  - drop pool copies (r_hp >= 0.95) of the 7 train twins.
  - Print the count per rule and the new list md5.
  - D4's "shading, not twins" verdict is beside the point here. The rule protects the E1 premise (unseen modules: A5c never saw them, so MIM must not) and test-module exposure. It costs about 3.5% of the images.
- **C2. Encoder lr and warmup.**
  - Decoder group 1e-3, encoder 2e-4 (`enc_lr_mult 0.2`).
  - fe31831 has no encoder warmup at unfreeze. With freeze = warmup = 2 epochs, the encoder starts at peak lr with an empty AdamW state: every weight moves by about lr on the first step (sign(g)).
  - Add `--enc_warmup_steps 1000`: enc_lr = lr_at(step) × mult × min(1, (step − freeze + 1)/1000). Add a unit test and log enc_lr.
- **C3. Batch, width, length.** Keep 100 epochs. The sample count (about 1.2M) is what matches HPT.
  - Batch: 64 if it fits on the launch machine; else 32 with the same lrs (AdamW is not linear-scaling in this range).
  - Decoder width 256 instead of 512 if a 50-step timing shows at least 1.6x throughput. My count is decoder about 36 GFLOPs fwd vs encoder about 19 at 512, so width 256 should roughly halve the cost. MAE found decoder width matters little for fine-tune (R, S here).
  - Record the choice and the measured samples/s in v1.
- **C4. Rule 1 divisor (reversed 29 Oct after team-lead's ruling; the README /n was an error, now fixed).** The verdict uses the house divisor 3 (`handbook/07` §5, `scripts/ssl_rules.py` `cmp`), even at 5 v 5. It is stricter and keeps verdicts comparable with BsM5, CsM5 and P16. /5 is reported as descriptive only. v1 must say /3.
- **C5. Verdict sets.** All 50 and without the noisy cell, as v0 has it: the clean set is the pre-registered co-primary (27 Oct SYNTHESIS §2). Twins and both are reported. My coach_mim5.md "without both" is superseded.
- **C6. I2 missing.** Save the ImageNet encoder through `encoder_state_dict()` at step 0 (`mim_step0.pth`). `encoder_init=mim_step0.pth` must reproduce A5c-f1 bit-identically for >= 300 steps on the launch machine. Item 3's "200 steps finite" with the MIM file stays as well.

## Small
- "The 24 labelled 5% cells": `labeled_5pct.txt` has 23.
- The m0_audit JSONs must carry `step` and `code_revision`; my verifier asserts both.

## Smoke v1 must show
- **S1.** Real schedule, run past the unfreeze: freeze + 200 steps (at most 1,000 steps). Show:
  - no loss spike at unfreeze;
  - encoder grad norm logged;
  - enc_lr ramping from 0.
- **S2.** Peak memory and samples/s at the chosen batch and width, next to whatever else is on the GPU.
- **S3.** Pool builder output: per-rule counts and list md5.

## Agreed as written
- Arms and one change.
- Re-run A5c-f1, with old A5c descriptive.
- Pre-stated expectation, including "below the free bias is not useful".
- Outcomes table and the kill.
- 6 tests disclosed.
- LA secondary.
- E1 secondary.
- Per-stage weight change.
- Machine rule (cv02 preferred; gaint only with team-lead's OK).
- Deployment and relay.
