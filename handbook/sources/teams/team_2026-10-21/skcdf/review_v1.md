# Review of SK1 protocol_v1 (agent 4, 21 Oct 2026)

## Verdict: CHANGES (minor)

**Allowed now:** the §12 smoke runs (300 steps) and the §7 identity checks (2,500 steps, cv02).
**Not allowed:** the real launch. It waits for protocol_v2 with the changes below, and for the user's answer to `data/decision.md` D7.

## What I checked
- **Paper.** Read in full (`literature/pdfs/skcdf_cvpr2025`).
- **Official code.** `yinguanchun/SKCDF @ 12f807d`, `SKCDF/code/train_skcdf.py:185-280`, read independently. Design §1 matches it on every point:
  - `ir2 = min(class_size)/class_size` from the first 4 labelled volumes (`:191-206`);
  - masked logits and label × 0 (`:254-259`);
  - linear anneal `ir22` (`:265`);
  - head/decoder EMA at the top of each iteration, H→D→H (`:215-238`);
  - λ = 10 with a sigmoid ramp over all epochs;
  - inference through `decoder_u` main head.
  - Table 3: ABSH adds +6.17 over DF (63.57 − 57.40). The text's 7.17 is wrong.
- **Diff** `f2f20d3..b90008e`, read line by line:
  - **Transfer order.** H runs after the optimizer step and before the teacher EMA. D runs in `_decouple_transfer`; it carries both heads, then aux_u ← aux_l, then main_u ← aux_u. This is the same sequence as SKCDF, shifted by half a step.
  - **Gradient paths.** The aux losses reach encoder and decoder, as in SKCDF.
  - **Teacher aux PL.** It uses the same CutMix box and the same 0.95 rule.
  - **Bernoulli streams.** Streams 3 and 4 do not collide: CutMix uses 2, the data stream uses its own.
  - **Evaluation.** `test_final_absh` is computed before `best.pth` loads. The primary stays the final-step teacher main head.
  - No bug found.
- **Tests on gaint.** `pytest tests/test_absh.py` gave **14 passed**. The file has 14 `def test_` functions and no parametrize. Protocol and log say 16; correct the count in v2.

## Answers to my five questions: satisfactory
- **Why this can work where P17 did not.** Credible. DF guarded against a harm that BsM5 already guarded against. ABSH targets the measured failure: bin-0 share 0.53 / 0.54 means confident misses on rare pixels.
- **One change per arm.** BsDB5 − BsD5 changes only `absh.enabled`. AB5 − A5c and BsDB5 − BsDBn5 are also single changes.
- **Design.** 5 v 5 seeds, 20k steps, final weights, one machine, no selection.
- **Adaptations are justified and fixed a priori.** The reference clip on crack/inactive avoids the splice scale; the 2-px band protects width; normalisation is CE/all-pixels.

## Required changes for v2
1. **Twin cells** (`data/decision.md` D6, D7).
   - Add "with and without the 7 twin test cells" to §9 for every contrast, next to the noisy cell. Report all four combinations.
   - State both branches of D7:
     - "no": pools unchanged, references reused after §7;
     - "yes": the 7 train twins are removed from the 5% unlabelled pool for all SSL arms. BsD5 s0–4 is re-run on the reduced pool with the new code (`absh.enabled=false`), on the same machine as BsDB5/BsDBn5, and the reused BsD5 is dropped. A5c and AB5 are unaffected (no pool).
2. **Prior-shift control** (descriptive, required).
   - **Why.** ABSH mainly moves the evaluated head's class prior. A reviewer will ask whether a free logit bias gives the same gain (handbook 05 §10 row 9: separate any gain from a threshold shift).
   - **What to add.** On the final BsD5 and A5c teacher checkpoints (no training), score test with logit adjustment `z_c − τ·log π_c`:
     - π is the class frequency in the 23 labelled cells (the same counts as `absh_p`);
     - **τ = 1 fixed now**, never tuned on test;
     - optionally a τ grid on **val only**, reported as such.
   - **Report** BsD5+LA next to BsDB5, and A5c+LA next to AB5, with AP and bin-0 share.
   - **Reading map.** If BsDB5 ≈ BsD5+LA on IoU and AP is unchanged, ABSH acts as a prior shift and should be described so.
3. **Mechanism logging.** Every 500 steps, log ‖main_l − aux_l‖ and the main head's mean predicted crack/inactive share on the labelled batch. This shows whether the H transfer actually moves the evaluated head. Check it in the smoke run.
4. **Deviations table.** Add a short table in §4 listing every deviation from the official code:
   - keep-prob reference and clip;
   - band;
   - aux Dice over kept pixels (the official code keeps masked pixels as zero-logit background inside Dice, which changes the Dice denominator);
   - PL source (EMA teacher aux head, ≥ 0.95);
   - transfer after the step rather than before;
   - λ = 1 vs 10;
   - Adam vs SGD;
   - inference head;
   - no SKCM.
5. **Test count:** 14, not 16 (or add the 2 missing tests and say which).
6. **Reference provenance.** A5c s0–2 come from P12 at a different commit than s3–4 (`bac5264`). Your §7 checks only s3.
   - Either add a check against `p12_A_5pct_s0`'s log, or state that s0–2 are reused as already pooled in P13 (handbook 13 C12) and disclosed.
7. **Machine.** I support **cv02**. gaint has 1 GPU shared with ALHVR; 25 runs there would take about 2 days; the references exist on cv02. This is the leader's call, and the README says gaint first. Record the leader's decision in v2.
   - Keep the cv02 rule: no GPU where another user holds > 4 GB.
   - Relay to gaint after the runs, with MD5.

## Not required, noted
- **Expected effect size.** P17's thresholds are about 0.013 crack / 0.043 inactive / 0.017 relF1@2, so a crack gain below about 0.013 will be n.d. at 5 seeds. That is fine as long as the n.d. reading is pre-written; §8 does this.
- **Flood flag on test (> 5× GT).** Acceptable because it never excludes a run.
- **`decoder_u` as SKCDF's own inference path.** Correctly secondary.

## What I will do on the results
I will recompute every primary and secondary number from the raw re-score JSONs and per-cell counts, with my own script, before anything reaches the leader.
