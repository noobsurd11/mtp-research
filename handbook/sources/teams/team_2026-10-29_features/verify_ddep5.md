# coach verify: DDeP5 vs A5c-f1 (5%, gaint, 2751aa8 vs 603e0d5)

coach, 30 Oct 2026 09:34 IST. Independent recompute with `scripts/coach_verify_f2.sh` (md5 f2c6c7ec), `scripts/coach_f2_checks.py` (b7eacb14) and `scripts/coach_verify.py` (b0456b28).
- DDeP5 arm: my own pull of gaint `el_f2/reports/f2/post_ddep5/` into `results/ddep5/coach_raw/`.
- A5c-f1 arm: the per-cell files already verified for MIM5 (`results/mim5/coach_raw/`).
- Outputs: `results/ddep5/coach/` (MD5 file there).

**Verdict: n.d. on all three primaries in both verdict sets (rule 1, house /3). DDeP5 is CLOSED per protocol_ddep5 v1: "a denoising-pretrained decoder does not beat a random decoder at 5% on EL". No 100% arm.**
- Every primary delta is small and positive.
- The crack gain (+0.007) is below both the 0.01 floor and the free logit bias (+0.016).

**vs runner's analysis: CONFIRMED** (section 5).

## 1. Integrity (E)
- All 5 DDeP5 runs: trained and rescored rc 0; one header per stdout; `step 20000/20000`.
- Each log has one `Decoder initialised ... (132 tensors, md5 dd786ff4...)` and no encoder_init.
  - dd786ff4 = `decoder_final.md5` on gaint = the cv02 file (checked 02:30).
  - `decoder_init` is in each config; no `loss_cp` keys.
- JSONs: step 20000, weights `model`, code_revision 2751aa8. Cells val 54 / test 50 / ext 106, same stems as the A5c-f1 files.
- el_f2: REVISION 2751aa8 = HEAD, 0 tracked files modified.
  - REVISION was written after the runs (runner, 08:46). Disclosed.
- Manifest: gaint and local `MANIFEST.md5` md5 ad967204 (30 files); `md5sum -c` OK. Runner's `results/ddep5/raw` is byte-identical to mine.
- Own checks:
  - tau0 cells == default (5/5);
  - pooled test primaries from the m0 cells == runner's rescore JSONs (max diff 0);
  - tau1 cells == `la.json` tau 1 (max diff 0).
- Cross-commit scoring (E, diff): between 603e0d5 and 2751aa8, `src` changes only `copy_paste.py`, `trainer.py` and `encoder_init.py`.
  - The scorer (`m0_audit.py` d36f7438, `m0_audit_tau.py` d77241bb, same files) imports none of them.
  - So A5c-f1 (scored at 603e0d5) and DDeP5 (at 2751aa8) go through identical inference code.

## 2. C1 primaries, test (tau 0), A5c-f1 → DDeP5, Δ (threshold /3) verdict
| Set | crack IoU | crack relF1@2 | inactive IoU |
|---|---|---|---|
| all 50 | 0.3002 → 0.3071, +0.0070 (0.0100) n.d. | 0.7136 → 0.7222, +0.0086 (0.0170) n.d. | 0.2791 → 0.2872, +0.0081 (0.0591) n.d. |
| without CSIR_00070_r8_c4 | 0.3024 → 0.3098, +0.0073 (0.0100) n.d. | 0.7175 → 0.7268, +0.0092 (0.0171) n.d. | 0.2901 → 0.2985, +0.0084 (0.0612) n.d. |
| without twins (reported) | +0.0094 (0.0109) n.d. | +0.0149 (0.0251) n.d. | +0.0018 (0.0659) n.d. |
| without both (reported) | +0.0099 (0.0111) n.d. | +0.0158 (0.0252) n.d. | +0.0019 (0.0687) n.d. |

- /5 thresholds (descriptive): crack 0.0100, relF1 0.0132, inactive 0.0457 on all 50; all n.d.
- Per seed, crack / relF1 / inactive:
  - DDeP5 s0-4: 0.309/0.721/0.329, 0.314/0.736/0.267, 0.304/0.718/0.316, 0.306/0.720/0.257, 0.304/0.717/0.266.
  - sd 0.004/0.008/0.033, slightly below A5c-f1's 0.005/0.013/0.039.
  - The crack threshold therefore sits at the 0.01 floor.
- Descriptive:
  - Paired image bootstrap, all 50: crack +0.0070 [+0.0014, +0.0125], relF1 +0.0086 [+0.0015, +0.0175], inactive +0.0081 [−0.0241, +0.0547]. It resamples cells, not seeds.
  - Leave-top-3-out: crack +0.0068, relF1 +0.0077, inactive +0.0279.
- How the crack gain arises (all 50, descriptive):
  - Crack recall 0.365 → 0.384 (+0.019, past its rule-1 threshold of 0.017); precision 0.628 → 0.606 (−0.022).
  - relR@2 +0.024, relP@2 −0.024 (width flag ok, threshold 0.05).
  - mIoU_rob 0.424 → 0.420 (−0.005).
  - The pretrained decoder acts mostly as a shift toward crack, which is what the free bias does.
- Per source crack IoU: ARTS +0.001, BMRK +0.007, CFVS +0.006, CSIR +0.010. All n.d.

## 3. LA contrasts
| Contrast | crack IoU | relF1@2 | inactive IoU |
|---|---|---|---|
| C2 (both tau 1), all 50 | 0.3157 → 0.3202, +0.0045 (0.0100) n.d. | +0.0046 (0.0164) n.d. | +0.0086 (0.0599) n.d. |
| C2, without noisy | +0.0047 (0.0100) n.d. | +0.0049 (0.0154) n.d. | +0.0090 (0.0620) n.d. |
| C3 (DDeP5 tau 0 vs A5c-f1+LA), all 50 | 0.3157 → 0.3071, −0.0086 (0.0100) n.d. | −0.0010 (0.0141) n.d. | −0.0017 (0.0591) n.d. |

- With the bias on both arms, about two thirds of the crack gain disappears (+0.0070 → +0.0045).
- DDeP5 alone does not reach A5c-f1+LA.

## 4. E1 (106 cells, descriptive only), crack recall A5c-f1 → DDeP5
| Group | tau 0 | tau 1 |
|---|---|---|
| all 106 | 0.0473 → 0.0465 | 0.0578 → 0.0574 |
| scuff + half-cut (29) | 0.0295 → 0.0309 | 0.0374 → 0.0392 |
| other (77) | 0.1009 → 0.0935 | 0.1192 → 0.1122 |

E1 crack is unchanged; the scuff + half-cut gap is untouched.

## 5. vs runner's analysis: CONFIRMED
- Runner's files are `results/ddep5/{results_ddep5_runner.md, m2_rung_ddep5.txt, m2_rung_ddep5_tau1.txt, m2_rung_ddep5_C3.txt, ssl_rules_ddep5.txt}`.
- They match mine to 4 decimals on all of these:
  - C1, both sets: means, sds, deltas, /3 and /5 thresholds, verdicts;
  - C2 and C3;
  - bootstrap and leave-top-3-out;
  - precision and recall;
  - the ssl_rules cross-check.
- Note on `m2_rung_ddep5_C3.txt`: it prints "RUNG VERDICT: WORSE".
  - That comes from the Track M rung rule's mIoU_rob guard (C3 mIoU_rob −0.0118, threshold 0.0100). It is not part of protocol_ddep5.
  - C3 is a yardstick with no verdict, and mIoU_rob compares a tau 0 arm with a tau 1 base, which is not a like-for-like contrast.
  - Runner's md does not cite the WORSE label (correct).
- Decoder-change diagnostic (runner, descriptive; `results/ddep5/ddep5_decoder_change.json` md5 0ebb86cb, `scripts/f2_decoder_change.py` b35edd53). Read, not recomputed.
  - Relative L2 change is about 0.97 in both arms, but that is mostly weight-decay shrinkage: decoder conv norm falls from 61.5/71.1 to 15.8.
  - Cosine to init, seed 0:
    - DDeP5 final vs the DDeP init 0.090, vs a random init 0.072;
    - A5c-f1 final vs its own init 0.102, vs the DDeP init 0.066.
  - Per block, x_0_4 (the full-resolution block) changes least (rel. about 0.60).
  - Fine-tuning at lr 1e-3 for 20k steps overwrites most of the pretrained decoder, as protocol_ddep5's expectation said. This is consistent with the n.d.

## Notes
- Test openings: one DDeP5 test opening (the post scored val, test and ext together). A5c-f1 was already open.
- Multiplicity (protocol): MIM5 and DDeP5 so far share A5c-f1, with CP5 still to come. Nothing passed, so no correction question arises.
