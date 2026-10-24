# MC review of `protocol_r1.md` (R1: TTA, 5-seed ensemble, crack operating point; inference only)

MC, 24 Oct 2026. **Verdict: APPROVED once one line is fixed (F1).** MD makes the edit, logs it, and may launch without another review.

## F1 (required before launch). The R1a pass rule contradicts design §1 and C6
- **As written:** "better if better on at least one primary on at least one cell set".
- **Design §1:** pass on both cell sets, or pass on one and n.d. with the same sign on the other (reported as such). C6 adds that "worse" on either set fails.
- **Fix:** replace the R1a sentence with the design §1 rule plus C6. Apply the same wording to R1b with bootstrap CIs: CI above 0 on one set and Δ of the same sign on the other; no primary CI wholly below 0 on either set.

## Checks (E: read the code, `scripts/m1_r1.py`, `scripts/m_common.py`)
| Item | Finding |
|---|---|
| Val decisions before test | Yes. The val loop writes `r1_val_decisions.json` before the test loop starts any inference. The test pass applies `dec` only |
| Test variants | Only per-seed plain/TTA, ensemble plain/TTA, LOO plain and the chosen R1 model. Matches the protocol |
| D1 / D2 implementation | Matches the text. Grid 0 to 3 in steps of 0.25. The val score has no inactive. Val list fixed |
| TTA inversion | `dihedral(inv=True)` undoes flip, then rotation, in the right order. Exact on square inputs |
| Ensemble | Mean of softmax, then log and argmax. LOO = (5·mean − member)/4: correct |
| Bias | Added to log p(crack) only; every class is scored. The p-bands for biased outputs use the re-normalised softmax: correct |
| Scoring helpers | `m_common.cell_stats` is M0's function with the asserts. The identity check (single_plain = M0 per-cell confusion, max diff 0) guards argmax-of-softmax vs argmax-of-logits ties |
| Step and cell asserts | Present (step 20000; 54/50 cells) |
| Code base | `el_m` @ `86197f3`; identity check to 1,000 steps (stdout losses, lr, val line) recorded in `identity_check.txt` |

## Notes (not blocking)
1. **CPU memory.** 5 models × (plain + TTA) × 54 × 24 × 512² float32 is about 13.6 GB, plus the ensembles. Check the free RAM on cv02 first, or keep the probs in fp16.
2. **R1a×b** (TTA ensemble − plain ensemble) is descriptive, because D1 already used val. Agreed.
3. **Noisy cell.** Report crack and border px on `CSIR_00070_r8_c4` for every variant (already listed). That is where the ensemble's all-50 gain will come from.
4. **R1c is descriptive.** If D2 lands on the max-relF1 branch, say plainly that the recall target is not reachable at relP@2 ≥ 0.90 on val.
5. **Disclosure is correct.** The choices are val-informed from M0's val numbers; no test number of a tuned variant exists.

## My verification plan for the results
- Recompute every contrast from `r1/r1_cells.json`: rule 1 per primary and set, a paired bootstrap with my own code (`mc_verify/mc_agg.py`, seed 0, 2,000 resamples), and the LOO spread.
- Check that `single_plain` equals M0.
- Re-derive the D1/D2 decisions from the val sweep.
