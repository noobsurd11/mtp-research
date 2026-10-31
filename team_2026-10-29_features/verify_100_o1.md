# coach verify: protocol_100 opening 1 (SUP100-g, SUP100-PF, MIM100-PF; 100% labels, gaint, e544133)

coach, 31 Oct 2026 ~01:37 IST. Independent recompute with `scripts/coach_verify_f100.sh`, `scripts/coach_f2_checks.py` and `scripts/coach_verify.py`.
- Inputs: my own pull of gaint `el_f3/reports/f100/post_opening1/` into `results/f100/coach_raw_o1/` (MANIFEST 6b801fdd, 87 files, identical on gaint and locally).
- Outputs: `results/f100/coach_o1/`.
- vs runner's analysis: pending (section 6).

**Verdicts (rule 1, house /3, two-set rule; protocol_100 v1.2):**
1. **Pool via the encoder, MIM100-PF − SUP100-PF: n.d. on all three primaries in both sets. CLOSED.** Continued MIM on the pool does not beat ImageNet init at 100% labels, even under a fine-tune that keeps the encoder (layer3/4 cosine to the MIM init 0.96 at 20k). This answers the user's question: **no**.
2. **Recipe, SUP100-PF − SUP100-g: n.d. on all three primaries in both sets. Closed as a test-score change.** Strong E1 gains are descriptive only (section 4).
3. **Bottom line, MIM100-PF − SUP100-g (reported): n.d.**
- Same verdicts at tau 1 (LA-matched) for all three.

## 1. Integrity (E)
- 15/15 runs trained rc 0, step 20000/20000, 0 tracebacks.
- The three s1 runs: 2 headers + 1 resume marker. The resume was bit-identical (`review_100_v1.md`).
- PF lines only in the PF arms (about 400 each); encoder md5 1c3df959 (216 tensors) only in MIM100-PF; `encoder_pf` freeze 1000 / lr_mult 0.1 in the PF configs; val_every 20000 everywhere.
- REVISION e544133 = HEAD, 0 tracked files modified.
- File checks: all JSONs step 20000, weights `model`, code_revision e544133, same stems as A5c-f1; tau0 == default.
- My pooled test primaries equal runner's rescore JSONs, and tau1 cells equal `la.json` (max diff 0).

## 2. Mechanism: PF kept the encoder (E, `enc_cosine_20k.txt`)
| Arm (5 seeds) | layer1 | layer2 | layer3 | layer4 | layer3/4 norm ratio |
|---|---|---|---|---|---|
| SUP100-g vs ImageNet | 0.40 | 0.14-0.15 | 0.008-0.022 | −0.000-0.001 | 0.09-0.13 / 0.00-0.06 |
| SUP100-PF vs ImageNet | 0.98 | 0.96 | 0.93 | 0.93-0.94 | 1.09 / 1.07-1.09 |
| MIM100-PF vs encoder_final | 0.98 | 0.96 | 0.96 | 0.96 | 1.05 / 1.04 |

So the PF contrasts test a preserved encoder, as designed. The erasure finding is reproduced on 5 fresh SUP100 seeds.

## 3. Primaries, test, tau 0 (Δ, threshold /3)
| Contrast | Set | crack IoU | crack relF1@2 | inactive IoU |
|---|---|---|---|---|
| pool MIM100-PF − SUP100-PF | all 50 | 0.4586 → 0.4635, +0.0048 (0.0113) n.d. | +0.0035 (0.0162) n.d. | 0.4545 → 0.4427, −0.0118 (0.0390) n.d. |
| | noNoisy | −0.0017 (0.0100) n.d. | −0.0039 (0.0100) n.d. | −0.0112 (0.0409) n.d. |
| recipe SUP100-PF − SUP100-g | all 50 | 0.4598 → 0.4586, −0.0012 (0.0316) n.d. | +0.0117 (0.0395) n.d. | 0.4395 → 0.4545, +0.0150 (0.0306) n.d. |
| | noNoisy | 0.4743 → 0.4682, −0.0061 (0.0100) n.d. | +0.0050 (0.0100) n.d. | +0.0143 (0.0321) n.d. |
| bottom MIM100-PF − SUP100-g | all 50 | +0.0036 (0.0299) n.d. | +0.0152 (0.0366) n.d. | +0.0032 (0.0398) n.d. |
| | noNoisy | −0.0078 (0.0100) n.d. | +0.0012 (0.0100) n.d. | +0.0031 (0.0415) n.d. |

- /5 descriptive: all n.d. Width flags: ok.
- **Reported sets (not in the verdict):** without both (twins and noisy), recipe crack −0.0190 (thr 0.0107) and bottom −0.0161 (0.0100) are WORSE by the arithmetic. PF trades crack recall for precision on test: crack R 0.638 → 0.618, P 0.623 → 0.640 (all 50).
- **The noisy cell:** SUP100-g s0 fails on CSIR_00070 (crack 0.414 on all 50 vs 0.475 without it). That inflates SUP100-g's all-50 thresholds (0.03). The PF arms' worst seed is milder (SUP100-PF s0 0.444).
  - mIoU_rob, recipe: +0.030 on all 50 (above its 0.020 threshold), +0.006 without noisy. A noisy-cell robustness effect; descriptive.
- **Tau 1 (LA-matched):** all three contrasts n.d. on all primaries in both sets.

## 4. E1 (106 unseen-module cells), descriptive only, never for selection
| Contrast | E1 crack recall | E1 crack IoU | E1 relR@2 | E1 inactive IoU | scuff + half-cut (29): crack recall / inactive IoU |
|---|---|---|---|---|---|
| recipe SUP100-PF − SUP100-g | 0.169 → 0.213 (+0.045) | 0.141 → 0.167 (+0.026) | +0.086 | 0.041 → 0.245 (+0.205) | 0.094 → 0.152 / 0.088 → 0.566 |
| pool MIM100-PF − SUP100-PF | −0.024 | −0.017 | −0.025 | −0.121 | −0.021 / −0.144 |
| bottom MIM100-PF − SUP100-g | +0.021 | +0.008 | +0.062 | +0.084 | +0.037 / +0.335 |

- **Reading (S):**
  - PF's E1 gain (crack recall +0.045, inactive IoU +0.20, scuff + half-cut inactive 0.09 → 0.57) is the largest E1 change any arm has produced. It fits the literature on full fine-tuning distorting pretrained features out of distribution (R arxiv:2202.10054).
  - But E1 has been read many times. A claim needs a pre-registered replication: new seeds with E1 crack recall and E1 inactive IoU as co-primaries stated before the runs, or an independent unseen-module set.
  - MIM-PF is worse than SUP100-PF on E1, so the pool's features do not help unseen modules either.

## 5. What this decides (S, for team-lead)
- **The user's question:** pool feature learning (MIM) does not help at 100% labels, now tested fairly with the encoder kept. Together with MIM5, DDeP5 and AM, the pool-representation line is closed.
- **BEST for B3 / RN50:**
  - Test cannot separate SUP100-g and SUP100-PF (n.d.). On test, PF trades a little crack recall for precision; on the noisy cell and on E1 it is clearly more robust (descriptive).
  - Recommendation: **BEST = SUP100-PF** for the follow-ups (B3, RN50-PF). Reason: equal on test by the rule, and more robust out of distribution. Pre-register a replication of the PF E1 effect as part of the next protocol.
- **CP100 (opening 2)** continues unchanged, against SUP100-g, as pre-registered.

## 6. vs runner's analysis: CONFIRMED (31 Oct ~01:55)
- Runner's files: `results/f100/opening1/` (`results_opening1_runner.md` md5 73236437, `m2_rung_{recipe,pool,bottom}[_tau1].txt`, `ssl_rules_opening1.txt`, `o1_extra.txt`).
- Runner's `raw/` is byte-identical to my `coach_raw_o1/` (87 files).
- These match mine to 4 decimals:
  - every primary delta and threshold, both sets, all three contrasts;
  - tau 1;
  - the E1 split (crack recall 0.169 / 0.213 / 0.189; scuff + half-cut 0.094 / 0.152 / 0.131);
  - the 20k cosines.
- **Flag, not a verdict:** `m2_rung_recipe.txt` and `m2_rung_bottom.txt` print "RUNG VERDICT: PASS". That is Track M's rung rule, which counts mIoU_rob as a primary: all 50, recipe +0.0303 (thr 0.0199), bottom +0.0227 (0.0168); without noisy, both n.d.
  - Under protocol_100, mIoU_rob is reported only, so the recipe and bottom contrasts are **n.d.**, not PASS.
  - The all-50 mIoU_rob gain is the noisy-cell robustness effect (§3). Any file quoting these rung outputs must carry that note, as with DDeP5's C3.
