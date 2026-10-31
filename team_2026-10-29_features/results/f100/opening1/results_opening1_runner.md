# protocol_100 opening 1: runner's analysis (CONFIRMED by coach, verify_100_o1.md §6)

runner, 31 Oct 2026 01:39 IST; coach CONFIRMED by 01:42 (byte-identical raw, every number matches to 4 dp); rung-file notes added. The 15 fine-tunes (SUP100-g, SUP100-PF, MIM100-PF; seeds 0-4; gaint, e544133, val off, 20,000 steps, final weights). CP100 (contrast 3) is opening 2.

## Inputs
- gaint `el_f3/reports/f100/post_opening1/` pulled to `results/f100/opening1/raw/`; `MANIFEST.md5` (md5 6b801fdd) checks OK, 87 files.
- All 15: step 20000, code_revision e544133; tau 0 == default per cell for all runs (`raw/tau0_check.txt`); MIM100-PF logs "Encoder initialised ... md5 1c3df959" (`raw/init_check.txt`).
- Per-cell files for the recompute: `raw/m0/f3_{SUP,SUPPF,MIMPF}_100pct_s{0..4}.json` (default argmax), `.tau0.json`, `.tau1.json` (LA); `raw/rescore/` (rescore JSONs + logs); `raw/la.json`; `raw/enc_cosine_20k.{json,txt}`.
- My outputs: `m2_rung_{recipe,pool,bottom}.txt` (md5 614a32d9 / ea39d24b / da010dac; before the first-line notes 3d5fc524 / - / 6ced66ab), `_tau1.txt` (4a6b8e0a / 9542daa1 / 4ab6b037; before the notes c116a753 / - / aa0544b4), `ssl_rules_opening1.txt` (f59e6f23, rescore path, f3_ mapped to p93_), `o1_extra.txt` (120f2cf9, `scripts/f100_o1_extra.py` bfef0502: E1 split, crack px on crack-free cells). Driver `scripts/f100_post_local.sh`.

## Verdicts (protocol_100 rule: rule 1, divisor 3, primaries test crack IoU / crack relF1@2 / inactive IoU, sets all 50 and −noisy)
| Contrast | Set | crack IoU d (thr) | relF1@2 d (thr) | inactive IoU d (thr) | Result |
|---|---|---|---|---|---|
| Recipe SUP100-PF − SUP100-g | all 50 | −0.0012 (0.0316) n.d. | +0.0117 (0.0395) n.d. | +0.0150 (0.0306) n.d. | |
| | −noisy | −0.0061 (0.0100) n.d. | +0.0050 (0.0100) n.d. | +0.0143 (0.0321) n.d. | **n.d. everywhere: closed** |
| Pool MIM100-PF − SUP100-PF | all 50 | +0.0048 (0.0113) n.d. | +0.0035 (0.0162) n.d. | −0.0118 (0.0390) n.d. | |
| | −noisy | −0.0017 (0.0100) n.d. | −0.0039 (0.0100) n.d. | −0.0112 (0.0409) n.d. | **n.d. everywhere: closed** |
| Bottom line MIM100-PF − SUP100-g (reported) | all 50 | +0.0036 (0.0299) n.d. | +0.0152 (0.0366) n.d. | +0.0032 (0.0398) n.d. | |
| | −noisy | −0.0078 (0.0100) n.d. | +0.0012 (0.0100) n.d. | +0.0031 (0.0415) n.d. | n.d. everywhere |

- Per the Kill line ("n.d. on all three primaries in both sets ... that contrast is closed at 100%"): **recipe and pool are closed at 100%.** No ensemble step, no further test opening for them.
- ssl_rules cross-check (rescore path, all 50): same deltas and thresholds to 4 dp for all three pairs; width check crack relP@2 ok (+0.0131 / +0.0203 / +0.0334).
- **Not a verdict:** m2_rung prints "RUNG VERDICT: PASS" for recipe and bottom (tau 0 and tau 1). That is Track M's rung rule with mIoU_rob as a primary (all 50 only; n.d. without noisy, a noisy-cell robustness effect; at tau 1 recipe's mIoU_rob is BETTER in both sets, +0.0319 / +0.0264). Under protocol_100 mIoU_rob is reported only; these contrasts are n.d. Each of the four rung files carries this as a first-line note. Recipe mIoU_rob all 50 +0.0303 (thr 0.0199) BETTER, −noisy +0.0058 (0.0129) n.d.; bottom all 50 +0.0227 (0.0168) BETTER, −noisy +0.0032 (0.0138) n.d.; pool all 50 −0.0076, −noisy −0.0026 n.d.
- Against the pre-stated expectations: recipe crack −0.01 to +0.02 (S): observed −0.0012 / −0.0061, inside. Pool (unknown under PF): crack +0.0048 / −0.0017, about 0.4× / 0.2× the clean MDE (0.012).

## Spread and the noisy cell
- Per-seed test crack IoU all 50 / −noisy: SUP100-g s0 **0.4143** / 0.4748, s1-s4 0.469-0.478 / 0.472-0.481 (one seed in five fails on CSIR_00070, as the protocol's power line said; CSIR FP-absent px SUP 43,120 vs SUP100-PF 14,753 vs MIM100-PF 36,525). SUP100-PF 0.444-0.468 / 0.461-0.474; MIM100-PF 0.459-0.468 / 0.462-0.471.
- −noisy sd: SUP 0.0038, SUPPF 0.0053, MIMPF 0.0032 (all thresholds at the 0.01 floor for crack).
- Paired image bootstrap (B−A, 95%): recipe −noisy crack [−0.0208, +0.0045]; pool −noisy crack [−0.0066, +0.0047]; bottom −noisy crack [−0.0192, +0.0008] (P>0 0.04).
- Leave-top-3-out crack IoU d: recipe −0.0093 / −0.0158; pool +0.0100 / +0.0016; bottom +0.0007 / −0.0142 (all 50 / −noisy).

## Reported sets and secondaries (never change a verdict)
- **−both (n 42) crack IoU WORSE** for recipe (−0.0190, thr 0.0107) and bottom (−0.0161, thr 0.0100): without the noisy cell and the 7 twins, SUP100-g has the higher crack IoU (0.4071 vs 0.3882 / 0.3910). −twins: all n.d. on primaries (mIoU_rob BETTER for recipe and bottom). Pool: n.d. on all four sets.
- Named per-source secondaries (rule-1 arithmetic, descriptive): BMRK crack AP WORSE for recipe (−0.0198) and bottom (−0.0139); −noisy CSIR crack IoU WORSE for recipe (−0.0570) and bottom (−0.0396), BETTER for pool (+0.0174); CSIR inactive IoU BETTER for bottom (+0.0771 all, +0.1352 −noisy). ARTS inactive IoU (13 cells, small inactive area): SUP 0.000, SUPPF 0.689, MIMPF 0.000 (one-arm swing; per-source table in m2_rung).
- **LA (tau 1):** every primary n.d. in both sets for all three pairs (recipe crack +0.0004 / +0.0005; pool +0.0094 / −0.0019; bottom +0.0097 / −0.0013). mIoU_rob BETTER under tau 1 for recipe (both sets) and bottom (all 50).
- **E1 (ext 106; `o1_extra.txt`), mean±sd of 5:**

| Group | n | Arm | crack recall | crack IoU | inactive IoU |
|---|---|---|---|---|---|
| all | 106 | SUP / SUPPF / MIMPF | 0.169 / 0.213 / 0.189 | 0.141 / 0.167 / 0.150 | 0.041 / 0.245 / 0.125 |
| scuff + half-cut | 29 | SUP / SUPPF / MIMPF | 0.094 / 0.152 / 0.131 | 0.086 / 0.132 / 0.115 | 0.088 / 0.566 / 0.423 |
| other | 77 | SUP / SUPPF / MIMPF | 0.393 / 0.397 / 0.363 | 0.261 / 0.238 / 0.224 | 0.028 / 0.104 / 0.044 |

  The E1 gains of the PF arms sit in the scuff + half-cut group (crack recall +0.058 SUPPF, +0.037 MIMPF; inactive IoU 0.09 → 0.57 / 0.42); on the 77 other cells crack IoU is lower for both PF arms (−0.023 / −0.037).
- **Crack px on crack-free cells** (sum, mean of 5): test (2 cells) 0 / 0 / 0; val (31) 178 / 17 / 71; ext (74) 3,181 / 3,846 / 3,849 (cells with any crack px 34.6 / 27.0 / 37.6).
- **Encoder cosine at 20k** (mean of 5; layer3 / layer4, to init): SUP100-g 0.015 / 0.001 (ImageNet); SUP100-PF 0.928 / 0.936 (ImageNet); MIM100-PF 0.959 / 0.961 (encoder_final). PF keeps the encoder; the house recipe erases layer3/4 at 100% as at 5%.
- Val (inclusion rule, Track M): no contrast passes on val; recipe inactive +0.043 n.d., bottom mIoU_rob −0.0104 WORSE (val only).

## Reading (mine, for coach to check)
At 100% labels, on the three primaries: keeping the ImageNet encoder (PF) does not change test crack or inactive segmentation measurably, and the MIM encoder on top of PF does not either. Both questions close n.d. The PF arms do keep their encoders (cosine ≥ 0.93), so the null is not an erasure artefact. Signals outside the verdict: on all 50 no PF seed fails on the noisy cell the way SUP100-g s0 does (crack sd 0.026 vs 0.009 / 0.003; −noisy sds similar, 0.004 / 0.005 / 0.003); mIoU_rob is higher for the PF arms on all 50 only (−noisy n.d.); on E1 PF raises scuff/half-cut crack recall and inactive IoU while lowering crack IoU on the other 77 cells; on −both SUP100-g's crack IoU is higher. Multiplicity: 3 contrasts × 3 primaries × 2 sets, no correction (protocol).
