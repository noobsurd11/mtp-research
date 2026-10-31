# coach verify: protocol_100 opening 2 (CP100 vs SUP100-g; 100% labels, gaint, e544133)

coach, 31 Oct 2026 ~07:30 IST. Independent recompute.
- **CP100 files:** my own pull of gaint `el_f3/reports/f100/post_opening2/` into `results/f100/coach_raw_o2/` (MANIFEST 1f307099, 42 files). Byte-identical to runner's `results/f100/opening2/raw/`.
- **SUP100-g comparator:** the opening-1 per-cell files. Manifest 6b801fdd, unchanged on gaint and locally, as pre-registered.
- **Outputs:** `results/f100/coach_o2/`.

**Verdict: CP100 is n.d. on all three primaries in both verdict sets, for C1 (tau 0) and for C2 (both arms at tau 1). There is no crack claim. CP100 is CLOSED at 100% labels per the protocol's kill line.**
**vs runner's analysis: CONFIRMED.** Every number below matches runner's `results_opening2_runner.md` to 4 decimals.

## 1. Integrity (E)
- **Runs:** 5/5 CP runs, step 20000, code_revision e544133, tau0 == default.
- **Score match:** my pooled test primaries equal runner's rescore JSONs, and tau1 cells equal `la.json` (max diff 0). Stems are the same as every other arm.
- **Encoder:** CP100 trained with the house optimizer, and its layer3/4 cosine to init is 0.011 / 0.001 (erased, as for SUP100-g).

## 2. Primaries (Δ CP100 − SUP100-g, threshold /3)
| Contrast | Set | crack IoU | crack relF1@2 | inactive IoU |
|---|---|---|---|---|
| C1, tau 0 | all 50 | 0.4598 → 0.4674, +0.0076 (0.0307) n.d. | +0.0102 (0.0379) n.d. | +0.0020 (0.0277) n.d. |
| | noNoisy | 0.4743 → 0.4747, +0.0003 (0.0100) n.d. | +0.0012 (0.0100) n.d. | +0.0007 (0.0299) n.d. |
| C2, tau 1 both | all 50 | +0.0086 (0.0311) n.d. | +0.0101 (0.0354) n.d. | +0.0016 (0.0274) n.d. |
| | noNoisy | +0.0004 (0.0100) n.d. | +0.0002 (0.0101) n.d. | +0.0005 (0.0297) n.d. |
| C3, CP tau 0 vs SUP+LA (yardstick) | all 50 | +0.0090 n.d. | +0.0096 n.d. | +0.0008 n.d. |
| | noNoisy | +0.0023 n.d. | +0.0015 n.d. | −0.0004 n.d. |

- **Width flag:** C1 relP@2 +0.0188 (all 50), ok.
- **Crack precision:** +0.019 (all 50) / +0.006 (noNoisy), against the pre-stated −0.01 to −0.03.
- **C3 rung flag:** runner's note on `m2_rung_C3.txt` is correct. Its PASS is mIoU_rob compared across tau 0 and tau 1, a tau effect (SUP100-g 0.5405 at tau 0 vs 0.4716 at tau 1), not a CP effect.

## 3. E3b decoy at 20k (pre-registered, original thresholds; reported, not a verdict)
| 20k, 248 held-out cells, 553 comps | real | decoy | background | decoy / real |
|---|---|---|---|---|
| SUP100-g (5 seeds, mean) | 0.2943 | 0.0028 | 0.0008 | 0.95% |
| CP100 (5 seeds, mean) | 0.4025 | 0.0125 | 0.0008 | 3.1% |

- **Original gate-6 rule: FLAG.** CP decoy is 4.41x SUP's, well under 0.05.
- **Gate 6b conditions:** (1) yes; (2) **no**, 0.0125 > 0.0094; (3) yes, 3.1% ≤ 3.6%.
- **What this means for gate 6b, disclosed plainly:** its GO (30 Oct) rested on the decoy rate falling from 2k to 4k (0.0076 → 0.0039). By 20k it had tripled to 0.0125. So a seam sensitivity did develop late in training, and my "not growing" reading at 4k did not hold.
- As pre-registered, the CP100 result carries a **seam-sensitivity caveat**. With a null verdict, the caveat changes no conclusion.
- Real pasted cracks are found far better (0.40 vs 0.29), as expected for a model trained on pastes.

## 4. Secondaries (descriptive)
- **Crack px predicted on crack-free cells (seed means):**
  - test (2 cells): 0 vs 0;
  - val (31 cells): 178 → 389 (tau 1: 245 → 558);
  - E1 (74 cells): 3,181 → 3,408.
  - CP doubles false crack on clean val cells, consistent with the late seam sensitivity.
- **E1, C1:**
  - crack recall 0.169 → 0.193 (n.d.);
  - crack IoU 0.141 → 0.158 (by arithmetic above its 0.0167 threshold; E1 is never for selection);
  - scuff + half-cut recall 0.094 → 0.115.
- **The noisy cell:** CP seeds 0.458-0.475 on all-50 crack (no seed fails like SUP s0). Crack px on CSIR_00070 per CP seed: 2,357 / 0 / 0 / 496 / 2,807.

## 5. Infrastructure note (runner, E)
- The measured LA scoring-pass peak (5,106 MiB) means opening 1's LA pass most likely took gaint's free memory to about 1.5 GB, below the 2 GB floor kept for finllm.
- Runner reported it to team-lead, and it is in protocol_100. It has no effect on any number.

## 6. protocol_100 closing summary (both openings)
- **Pool via MIM (MIM100-PF − SUP100-PF):** n.d., closed.
- **Pool via copy-paste (CP100 − SUP100-g):** n.d. at tau 0 and tau 1, closed, with the E3b seam caveat.
- **Recipe (SUP100-PF − SUP100-g):** n.d. on test. Large descriptive E1 gains (`verify_100_o1.md` §4) and a noisy-cell robustness signal.
- **Conclusion for the user's question:** neither way of using the unlabelled pool (learned encoder features, pasted cracks on pool backgrounds) improves the model trained on all 478 labels, in this design and at this power (clean MDE crack 0.012).
- **The open lead is the fine-tune recipe,** not the pool: the PF E1 replication and RN50-PF.
