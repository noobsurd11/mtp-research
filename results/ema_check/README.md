# EMA teacher vs student at the final step (descriptive, 13 Oct 2026)

**Why:** from P13 on, the supervised arm (A) is the loss-off control, but SSL arms are scored on the EMA teacher while A has no EMA. So SSL − A could contain an "EMA-only" effect, which was never measured (Ds5 dropped in P13 Amendment 1; handbook doc 13 C11). The P17 reading ("the gain reaches the teacher through the shared encoder") also leaned on this.

**What was done:** read-only re-scoring of `latest.pth` (step 20,000) for 15 runs:
- weights: once the student (`models.model`), once the EMA teacher (`models.teacher`);
- runs: BsM5 s0–4, CsM5 s0–4 (P13, `el_p13`), BsD5 s0–4 (P17, `el_p17`);
- data: test, revised labels.

The script is `scripts_cv02/rescore_weights.py`: the standard re-scorer plus `--key` and `--root`, run from cv02 `diag/student/`. No deployment dir was changed. Done after P13 and P17 results were known, and not in any protocol.

**Sanity:** the teacher scores reproduce the official re-score JSONs exactly (max |diff| 0 over 15 runs and 5 metrics).

## Result (`summary.txt`)
EMA teacher − student, mean [min, max] over 5 seeds:

| Arm | crack IoU | inactive IoU | crack relF1@2 | crack AP | inactive AP |
|---|---|---|---|---|---|
| BsM5 | −0.0010 [−0.0023, +0.0004] | −0.0014 [−0.0037, +0.0024] | −0.0017 [−0.0030, +0.0001] | +0.0010 [−0.0011, +0.0020] | +0.0019 [−0.0002, +0.0042] |
| CsM5 | −0.0008 [−0.0030, +0.0019] | −0.0000 [−0.0028, +0.0017] | −0.0006 [−0.0043, +0.0035] | +0.0010 [−0.0008, +0.0038] | +0.0013 [−0.0020, +0.0030] |
| BsD5 | −0.0008 [−0.0023, +0.0002] | −0.0008 [−0.0033, +0.0022] | −0.0015 [−0.0041, −0.0004] | +0.0002 [−0.0009, +0.0016] | −0.0014 [−0.0035, +0.0009] |

## Reading
- At step 20,000 the EMA teacher and the student score the same: every difference is within ±0.005. The cosine schedule ends at learning rate 0, so the student barely moves at the end and the EMA catches up with it.
- So the SSL gains over A5c (P13, P17) are carried by the trained student itself, not by scoring an EMA average.
- By the same mechanism, a λ = 0 run's teacher would match its student, which is bit-identical to A. That makes the EMA-only effect very likely about 0 at this schedule. This is an inference, not a measurement of Ds5. Phase 1 (teacher − student +0.000 ± 0.002) and P8 (student = teacher) agree.
- For P17: BsD5's student (encoder trained with pseudo-labels + labelled decoder trained on labelled data only) scores like its teacher. The gain over supervised therefore sits in the encoder, not in the EMA.

Files: `p13_model.json`, `p13_teacher.json`, `p17_model.json`, `p17_teacher.json` (+ logs), `summary.txt`.
