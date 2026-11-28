# x4 two-stage screening rule (lead, written 27 Nov 2026 23:12:59 IST before any x4 arm has trained)

Reason: 5 free A6000s give about 2.2 runs per hour; a full 2-seed screen (10 runs) costs about 4 h. To screen more arms by the 28 Nov noon deadline, each arm runs in two stages. This rule is fixed now and is not changed after any arm result is seen.

## Stage P (pathfinder, descriptive, decides nothing about the method)
- Arm trained at seed 5 on all 5 cv5v3 folds (5 runs), COMBO recipe plus the arm change, 20k steps, swad readout, OP-A.
- Read with read_x4 against COMBO seed 5 (same seed, same folds), 532 cells, plus the 416 clean cells and all guards printed.
- PROMOTE to stage S if ANY of:
  (a) crack relF1@2 delta >= +0.005;
  (b) crack relR@2 delta >= +0.010 and crack relP@2 delta >= -0.005;
  (c) inactive IoU delta >= +0.030.
- Otherwise the arm is recorded as "pathfinder: not promoted" with its numbers. That is not a verdict on the method; it means this setting did not justify the GPU time.

## Stage S (screen, the protocol rule)
- Add seed 6 (5 runs). Read arm seeds 5, 6 against COMBO seeds 5, 6 with read_x4 (seed-aware two-stage group bootstrap, 285 cv5v3 groups, 2,000 draws).
- SCREEN PASS iff crack relF1@2 delta >= M (= 0.0100, recomputed from the PF A/A in the read) with the 95% interval lower end > 0 at OP-A on 532 cells, and the guards pass (width ratio pooled and per source within 0.85 to 1.15 of COMBO; false crack px on crack-free cells <= 1.5x COMBO; mIoU-R13 change >= -0.010). OP-W and the 416 clean cells are printed beside as robustness checks.
- A gain with a failing guard is "GAIN, FAILING GUARDS NAMED"; otherwise NOT CONFIRMED (worded WORSE, "interval holds 0" or "below M").

## Stage C (confirmation, later)
- Only a screen PASS arm gets seeds 7 to 9 and a 5-seed read under the same rule. Combinations of passing arms come after that.

## Inference-only and post-hoc items
- Read against COMBO with the same tool, labelled post-hoc; cross-fitted where a parameter is chosen.
