# Builder brief: crack-to-region architecture (x4_cra), 28 Nov 2026

Read `BUILDER_BRIEF.md` (same folder) first. All of its rules, deliverables and identity requirements apply. This file adds the design. The user asked for a new architecture that the supervisor can see as one network. It is judged on crack relF1@2 and on inactive IoU.

## Why (E, from files)
- COMBO misses are crack ends (0.52 of missed crack px) and interior gaps of long cracks (0.28), with confidently negative margins (gaint `team_2026-11-27_arch/cpu/REPORT.md`). A hand-written endpoint extension gave +0.0045 [+0.0002, +0.0092] cross-fitted, so there is something to bridge.
- Inactive (class "inactive", check the index in the class map) is rare: 42 of 478 train cells. COMBO inactive IoU 0.5297 (532 cells). A separate inactive aux head with a layered decision was parked (-0.0140 [-0.0767, +0.0556]). Physically an inactive region is a piece of the cell cut off by a crack and the busbars/cell edge, and it is dark in EL.
- `x4_geomaux` (gaint `harness/x4/arms/x4_geomaux.md`, code `src/trainers/geomaux.py`, merged in bench_x4 0d4e431) already trains distance, direction (cos, sin) and width heads on the last decoder features, dropped at inference. Reuse it; do not duplicate it.

## Base
gaint worktree `/home/noob/work/bench_wt_x4_cra`, branch `x4_cra` from bench_x4 HEAD (8da53f6, includes geomaux 0d4e431 and poolst). Never edit other worktrees.

## What to build (opt-in keys, default off; keys off = bit-identical to COMBO)

### Part R: crack-to-region head (card `x4_cra_region`)
A second-stage module after the U-Net++ decoder that produces the inactive logit with region-level reasoning:
- inputs: the final decoder features, the model's own crack probability map (softmax channel of class crack; decide and document whether it is detached, default detached so the region head cannot distort the crack channel), and a context signal with a large receptive field (for example a downsampled pyramid pooling or a few dilated/strided conv blocks on the decoder features at 1/8 or 1/16 resolution, upsampled back). Keep it light (aim for < 1.5M params, < 1.3x step time).
- output: an inactive logit that is added as a residual to the base inactive logit (zero-initialised last layer, so at step 0 the arm equals COMBO's forward), the 24-class softmax and the house loss stay as they are.
- optional key (off by default in this card, own card if you build it): a region auxiliary loss on the inactive channel (for example Dice on inactive only, or boundary-aware), weight 0.1 to 0.3.
- unit test: shapes, gradient flows to the region head and (if not detached) not to the crack channel, zero-init equality to COMBO forward, hand-computed value of any new loss.

### Part D: direction-guided gap bridging (card `x4_cra_dir`, and the combined card `x4_cra`)
- training: geomaux heads on (same keys as `x4_geomaux`), kept at inference.
- inference: a deterministic bridging step that uses the predicted direction and distance to (1) extend crack ends along the predicted direction while the distance head says a crack is near, and (2) link two crack ends that face each other within a short gap. Every threshold is FIXED IN THE CARD before any run (choose them from the endpoint-extension study in cpu/REPORT.md and from training-fold reasoning only, never from held-out folds, test50 or E1). Document the values and why.
- the plain `swad` readout must stay exactly what COMBO's writer produces (the read checks the writer md5 `bench_infer.py afd9164264de4d91e43e258e6f8b1836`; do not change that file's behaviour for existing readouts). The bridged output is a SECOND readout (for example `swad_bridge`) written in the same dump format, so one training run gives both, and the read compares each against COMBO swad. If adding a readout needs a writer change, make it a new code path selected only by the new readout key, re-verify that the old readouts are byte-identical, and record the new writer md5.
- CPU check: run the bridging on existing COMBO out-of-fold dumps on gaint (COMBO has no direction head, so use this only to test that the code runs and is deterministic; report its numbers as a smoke, decides nothing).

### Combined card `x4_cra` = Part R + Part D (+ geomaux heads). This is the architecture. `x4_cra_region` and `x4_cra_dir` are its ablations.

## Hand-over
- One handover note per card in `harness/x4/arms/` on gaint, `BUILD_cra.md` progress log, unit tests, CPU identity IDENTICAL (keys off) vs 8da53f6, arm-on 5-step CPU smoke, params and CPU step-time ratio.
- Do NOT run GPU smokes or append to any queue. The lead (me) runs the 200-step memory smokes and the integration into bench_x4. Give me the exact x4_make_jobs.py lines (smoke and stage P, seeds 5 and 6) and say which readout key the read must use for each card.
- Do not touch cv02 at all. Do not stop, kill or change anything running.
- Final message: commit, cards with md5, identity result, tests passed, params, step-time ratio, readout keys, anything you could not do.
