# NOTES for app_pseries.tex (Appendix "The P-series: diagnostics and semi-supervised learning (7 to 23 Oct)")

Writer id `pseries`, 27 Nov 2026. Every number and dated fact in the .tex, with its source (path:line) and the quoted text.
All paths are on the laptop research repo `/home/yugma/mtp/research/` (snapshot to 4 Nov; these files predate it). Server not needed.

## Abbreviations and md5 (first 8 hex of `md5sum`)
| Key | Path | md5 |
|---|---|---|
| H07 | handbook/07_methodology_rules_and_statistics.md | b18b3451 |
| H08 | handbook/08_experiments_P1_P7_diagnostics.md | 88927802 |
| H09 | handbook/09_experiments_P8_P12_ssl_series.md | b26c0c0a |
| H10 | handbook/10_experiments_P13_P16_E1.md | a1c57c87 |
| H12 | handbook/12_decisions_log.md | b4c463a5 |
| P11R | results/p11/README.md | 28209882 |
| P13R | results/p13/README.md | aafd4f1e |
| P14R | results/p14/README.md | 443b170d |
| P15R | results/p15/README.md | c0fc59ed |
| P16R | results/p16/README.md | 22eceb33 |
| P17R | results/p17/README.md | 0de2f6b3 |
| E1R | results/e1/README.md | 904fce1b |
| ALR | team_2026-10-21/alhvr/results.md | 2a335c42 |
| ALP | team_2026-10-21/alhvr/protocol_v2.md | 46ef0543 |
| ALLOG | team_2026-10-21/alhvr/log.md | 7bcb1b70 |
| ALL | results/al1/launch.log | 41052fec |
| DD | team_2026-10-21/data/decision.md | 622a5c13 |
| CH05 | thesis working copy chapters/ch05_legacy.tex | (read 27 Nov) |
| TT | thesis working copy THESIS_TABLES.md | (read 27 Nov) |

Handbook docs are the project's own synthesis; each line quoted below names its primary file (results/*/README.md, protocols/*.md),
and the key P11, P13 to P17 and AL1 numbers were also checked in the primary README (P11R, P13R, ..., ALR).

Machine names: "training machine" = cv02 (RTX A6000), "second machine" = gaint (RTX PRO 4500), as in TT l17 to l19 ("Training
machine = the RTX A6000 machine ... second machine = the other machine, used ... for some pre-protocol runs (T21)") and H09 l56
("g prefix | the run is on gaint (RTX PRO 4500), not cv02 (RTX A6000)"). T21 itself labels AL1 "training machine" and P15 "second
machine", consistent with this mapping.

## Intro
| Fact | Source |
|---|---|
| period 7 to 23 Oct; P1 to P7, P8 to P17, audit, P18, E1, AL1 | H08 l4 "first seven experiments of the P-series (7 to 10 Oct 2026)"; H10 l1 "P13 to P17, the P13 audit, and E1 (11 to 13 Oct 2026)"; ALR l1 "AL1 v2 results ... (23 Oct 2026)" |

## Section: Conditions
| Number / fact | Source (quote) |
|---|---|
| legacy split 478 / 54 / 50, release 20211104 | DD l8 "Keep BenchmarkEL `20211104`, 478 / 54 / 50, with `masks_escdd`" |
| split seed 0 | H09 l97 "revised masks; seed-0 split" |
| P1 to P5 on 20211104 masks (v0) | H08 l15 "Old era: original 20211104 masks ... These appear in P1, P2, P3 and P4 only"; P5 scored against revised and old (H08 l358), models trained on old masks (H08 l344 old-era ALHVR runs) |
| from P6 revised masks = v1 | H08 l281 "From P6 on, every experiment trains and scores on the revised masks"; H08 l409 (E-SCDD masks, classes 24 to 29 mapped back, old mask for 5 stems) = v1 definition in ch04_data.tex l66 |
| 5/10/20/50/100% = 23/47/95/239/478 cells; inactive in 2, 4, 9, 20 | H10 l660 to l664 "| 5% | 23 | 2 | 455 |", "| 10% | 47 | 4 | 431 |", "| 20% | 95 | 9 | 383 |", "| 50% | 239 | 20 | 239 |", "| 100% | 478 | – | 0 |" |
| in-domain pool 455, 431, 383, 239 | same lines |
| external pool 11,938, 77% CSIR 23% ARTS | H09 l248 "The pool is 77% CSIR and 23% ARTS, with no CFVS, BMRK or SDLE" ; H09 l53 "external unlabelled pool (11,938 cells)" |
| IoU pooled over all cells of the split, per class | H08 l68 "IoU: intersection over union of predicted and true pixels of a class, pooled over all cells of the split" |
| argmax, final weights | H10 l95 "argmax prediction, final weights" |
| AP from histograms with 1,000 bins | H08 l69 "AP: pixel average precision from score histograms with 1,000 bins" |
| P6/P7 primaries AP; from P8 IoU / IoU / relF1@2 | H08 l424 "Primary metrics: crack AP and inactive AP"; H09 l64 "From P8 on, the primary metrics are test crack IoU, test inactive IoU and test crack relaxed F1@2" |
| rule formula, any primary passes none worse | H07 l96 "Δ = mean(B) − mean(A) > max(0.01, 2 · √((sd_A² + sd_B²) / 3))"; H07 l97 "and no primary metric is worse by the same threshold" |
| 3 v 3 about 2 SE, one-sided p about 0.06; 5 v 5 about 2.58 SE | H07 l111 "3 vs 3 seeds: 2 SE is roughly a one-sided t-test at p ≈ 0.06"; H07 l112 "5 vs 5 seeds: the divisor stays 3 ... The threshold is then about 2.58 SE" |
| bootstrap 2,000 resamples, top-3 out, source split 21 / 29 | H10 l106 "resample the 50 test cells with replacement 2,000 times, paired"; l107 "Leave-top-3-out"; l109 "CSIR/ARTS (21 cells) vs CFVS/BMRK/SDLE (29 cells)" |
| robustness never changes verdict | H07 l142 "R7 ... they never change the verdict" |
| L3 recipe: smp U-Net++ ImageNet ResNet-34, CE + soft Dice, label-safe, 20,000 steps, batch 8, Adam 1e-3, wd 1e-4, 200 warm-up, cosine | H08 l410 "20,000 steps; batch 8 labelled; Adam 1e-3 with weight decay 1e-4; 200-step warm-up then cosine to 0; grad clip 1"; H08 l420 "L3 | smp_unetpp | labelsafe | CE + soft Dice (crack, inactive)"; H08 l418 label-safe = "flips/rot90 + brightness/contrast only" |
| Mean Teacher: unlabelled batch 8, EMA 0.999, teacher scored; λ 0 for 2,000 then ramp over 2,000 to 1 | H09 l97 "batch 8 + 8"; l99 "EMA 0.999"; l102 "λ schedule: 0 for 2,000 steps, ramp over 2,000 steps to 1.0"; l103 "EMA teacher evaluated" |
| P1 to P5 on gaint; P6, P7 on cv02 | H08 l48 to l54 (Machine column: gaint for P1 to P5, cv02 for P6, P7) |
| P10 references, P12 g-arms on gaint; P15 on gaint | H09 l357 "6 supervised references on gaint"; H09 l649 to l651 (gDm5, gCm5, gA10 gaint); H10 l568 "Arms: gaint" |
| never pooled, never across machines | H07 l171 "Never compare arms across machines"; H09 l653 "never pooled with cv02 seeds" |
| test50 caveats; 59% in 3 cells; no model selected on test | CH05 l30 to l35; CH05 l138 "3 of its cells hold 59\% of its inactive pixels"; H08 l512 "test | 16 of 50 | 59%" |
| E1 read without registration | CH05 l19 "E1 was read without registration during the P-series" |

## Section: Restart and P1 to P5
| Number / fact | Source (quote) |
|---|---|
| restart 7 Oct; three doubts | H08 l37 to l40; H12 l121 "D1. Restart with analysis first (7 Oct, 23:37)" |
| first protocol commit 23:59 on 7 Oct | H12 l150 "first commit `f9708c0` (7 Oct 23:59)" |
| exploratory label outside protocols | H12 l145 "Anything outside the rules is labelled EXPLORATORY"; l143 "Every experiment gets a protocol in `protocols/`, committed before any run" |
| old-pipeline description | H08 l15 "original 20211104 masks, from-scratch 5M U-Net++, weighted CE, strong augmentation, SemiCE Mean Teacher" |
| P1 date 8 Oct | H08 l92 "gaint, 8 Oct 2026, 00:46 to 01:52 IST" |
| 0.325 crack IoU on own 47 images, inactive 0.88 | H08 l80 "still score only 0.325 crack IoU on those same 47 images, while inactive reaches 0.88" |
| ten images, 3,000 steps | H08 l93 "10 train images that contain crack"; l94 "3,000 steps" |
| one run per arm, 3 seeds for B and D | H08 l107 "one run per arm, except B and D, which got 3 seeds" |
| A 0.612 (AP 0.929), B 0.677, C 0.861, E 0.381 (AP 0.587) | H08 l121 to l125 (rows A, B, C, E) |
| H2 met; H1 not met as written, partial; precision 0.62 vs 0.81; H3 refuted; H4 refuted | H08 l141 to l145 |
| 10/10 masks identical | H08 l141 "loader mask identical to the raw PNG in 10/10 images" |
| fp32 0.656 ± 0.048 vs bf16 0.668 ± 0.031 | H08 l142 "over 3 seeds B 0.668 ± 0.031 vs D 0.656 ± 0.048" |
| led to label-safe aug (L1), Dice (L3) | H08 l158, l159 |
| P2 date 8 Oct; λ = 1.5; 40 batches; no optimiser step | H08 l166 "Mean Teacher on BenchmarkEL with λ = 1.5 scored the same as its λ = 0 control"; l180 "40 training batches"; l181 "Forward and backward only, no optimiser step"; l182 "8 Oct 2026, 00:44 IST" |
| 100% of pixels ≥ 2 positives (threshold 20%), rule fires | H08 l196 "> 20% of unlabelled pixels with ≥ 2 positive classes | 100% of pixels | Met, strongly. The rule fires" |
| offset share 0.041 ± 0.009 (against 0.5); 0.25 ± 0.35 | H08 l194, l195 |
| pushes background, padding and crack up together | H08 l224 "its target pushes background, padding and crack up at the same time" |
| old MT results invalid | H08 l225 "every old Mean Teacher result is a test of this loss, not of Mean Teacher" |
| 77% coverage, crack 0.024%, about 8x under | H08 l211 "A standard pseudo-label rule (teacher max-prob ≥ 0.95) covers 77% of unlabelled pixels"; l217 "crack | 0.024% (about 8× under its labelled share of about 0.19%)" |
| confidence_ce replaced it; queue held | H08 l230 "A correct hard pseudo-label loss (`confidence_ce`, used as arm B from P7 on)"; l232 "The external-pool queue on gaint was held by the user (7 to 8 Oct) and stays held"; H12 l159 "The queue has stayed held and untouched since" |
| P3 10 Oct, no protocol, exploratory | H08 l244 "There was no protocol, so every statement here is exploratory"; l247 "gaint, 10 Oct 2026" |
| +0.05 to +0.07 every model | H08 l270 "The label version alone moves crack IoU by +0.05 to +0.07 for every model" |
| 0.304 → 0.355 (SL-10%, 3 seeds) | H08 l262 "| test | SL-10% b8 | 0.304±0.005 → 0.355±0.005"; l258 "mean ± sd over 3 seeds" |
| 129 of 281, 34 of 50 test | H08 l254 "129 of the 281 crack images have a changed crack mask, including 34 of the 50 test images" |
| within 2 px; cleaning | H08 l255 "almost entirely within 2 px of the old labels ... So this is a cleaning (dotted labels joined, widened)" |
| P4 numbers: 0.029 / 0.321 / 0.331 / 0.183; inactive 0.097 / 0.423 / 0.383 / 0.384 | H08 l308 to l311 |
| 47 cells, 2,000 steps, 2 probe seeds, pooled val+test, revised | H08 l296 "47 images ... 2,000 steps; batch 8; no augmentation; 2 probe seeds"; l297 "val (54) + test (50), pooled (104)"; l299 "decision metric: pooled val+test AP, revised labels" |
| rule 1 fires (+0.30), rows 3 and 6 stay (MIM, foundation distillation); rule 2 fires | H08 l288, l289 (row 3 MIM, row 6 foundation-teacher distillation); l316 "Rule 1 fires: best pretrained beats random by +0.30 crack AP"; l317 "Rule 2 fires" |
| led to L2 | H08 l327 |
| P5: two old ALHVR runs, 378 cells | H08 l344 "old-era runs `alhvr_20pct_s0` and `s1`"; l345 "378 unlabelled train images" |
| strict 0.27, relaxed 0.64 (r3, global) | H08 l364 "| global γ | r3 (both unsure) | 0.72 | 0.27 (0.23) | 0.64 | 0.62 |" |
| confident 0.59 / 0.96; 8% recall | H08 l368 "| reference: ensemble prob ≥ 0.95 | – | recall of all GT crack 0.08 | 0.59 (0.50) | 0.96 |"; l392 "covers only 8% of GT crack" |
| per-class r3 relaxed 0.48, recall 0.29; rule 1 fires borderline | H08 l383 "Ω3 relaxed P under γ_c = 0.48 (recall 0.29) | Fires (borderline)" |
| rule 2 inactive 0.43 fires; rule 3: 40 points, not met | H08 l384, l385 |
| tolerant loss definition | H08 l395 "rare-class pixels are credited if the student predicts the class anywhere within R = 2 px; confident head-class pixels away from rare targets get ordinary CE; everything else gets no loss" |

## Section: P6 and P7
| Number / fact | Source (quote) |
|---|---|
| P6 locked 11:42, 10 Oct | H12 l254 "D13. P6 design: revised masks and a one-change ladder (10 Oct, locked 11:42)" |
| 21 runs, seeds 0 to 2, cv02 | H08 l410 "seeds 0, 1, 2"; l413 "21 runs, 10 Oct 11:46 to 15:32 IST, all rc = 0" |
| arms L0 to L3 and fractions | H08 l417 to l420 |
| L0 → L1 crack AP +0.020 (0.019), inactive +0.028 (0.020) helps; L1→L2, L2→L3 hurt; L0 10→100 n.d.; L3 10→100 helps | H08 l449 to l453 |
| rule 2 picks L0, 0.480 | H08 l460, l464 |
| headroom −0.001; interim +0.026 | H08 l472 "the headroom is −0.001 < 0.02"; l475 "An interim figure of +0.026 averaged the per-split APs" |
| bin-0: L0 3%, L2 19%, L3 42% | H08 l485, l487, l488 |
| crack IoU rises L1→L2, flat L2→L3 | H08 l492 |
| primaries switched from P8 | H08 l497 |
| L3 10→100 crack +0.075 [+0.029, +0.128]; inactive +0.135 [+0.049, +0.205] | H08 l527, l528 |
| L0 does not convert labels | H08 l506 |
| L3 = reference A | H08 l566 |
| correction: 71,376 FP px; +0.048; about +0.010 | H08 l533 "`p6_L0_10pct_s1` put 71,376 false-positive crack px on the very noisy test cell"; l534 "Without that cell L1 − L0 crack IoU is about +0.010" |
| Table P6 rows | H08 l435 to l441 (crack AP, inactive AP, crack IoU, inactive IoU, crack relF1@2 columns) |
| P7 arms B, C, D; seeds 0 to 2; labelled images take strong view | H08 l593 to l598; l587 "the labelled images take the same strong view"; l590 "seeds 0 to 2" |
| C − D +0.000 n.d., −0.032 worse; B − D worse; C − B +0.024, +0.064 better | H08 l625 to l627 |
| width +0.031 thinner | H08 l629 "crack relP@2 C − D = +0.031. C predicts thinner cracks" |
| pilot | H08 l630 |
| C − B inactive +0.056 [+0.022, +0.086], only robust | H08 l639; l642 "The only robust contrast is C over B on inactive" |

## Section: P8 to P12
| Number / fact | Source (quote) |
|---|---|
| base choice post hoc | H09 l89 to l92 |
| P8 locked 15:43 | H12 l281 "D15. ... (10 Oct, locked 15:43, before any P8 run)" |
| C − D +0.009 (0.010), +0.059 (0.132), +0.015 (0.017); B − D, C − B n.d. | H09 l139 to l141 |
| D − A crack −0.013 [−0.028, −0.001], inactive −0.101 [−0.171, −0.031] | H09 l154, l155 |
| student = teacher | H09 l165 to l172 |
| three remaining differences | H09 l174 to l177 |
| P9: Cx − Dx +0.056 (0.046); Bx no; Cx not beat Bx | H09 l266 to l268 |
| same size as P8 +0.059; passes for lower spread | H09 l274 |
| CI [−0.013, +0.117]; +0.026 without top 3 | H09 l281; l287 "without the 3 largest inactive cells the gain halves to +0.026" |
| pool-size effect −0.005, −0.003, −0.007 | H09 l272 |
| Dx − D inactive +0.094 [+0.003, +0.179] | H09 l295 |
| Cx − C CSIR+ARTS −0.019 [−0.041, −0.003] | H09 l300 |
| P10: none pass; B5 amendment before any B5 run | H09 l369 "before any B5 run"; l406 to l409 |
| seed 2: C5 0.142, B5 0.128 | H09 l442 "| 2 | 0.244 / 0.249 | 0.128 / 0.003 | 0.142 / 0.027 |" |
| rare_frac 0.001 to 0.002 from step 4,000 | H09 l445 |
| Cx5 − Dx5 relF1@2 −0.027 (0.024) worse | H09 l407 |
| relP −0.065 | H09 l411 |
| crack −0.012 [−0.026, −0.001] | H09 l426 |
| CSIR+ARTS −0.065 [−0.092, −0.026] | H09 l431 |
| A5 on gaint, reference only; D5 − A5 −0.055 | H09 l362; l450 "D5 − A5: crack IoU −0.055" |
| P11 locked 00:11, 11 Oct | H09 l517 "Locked 11 Oct 00:11 IST" |
| Dm − D inactive +0.101 | P11R l35 area; H09 l570 "Dm − D (P8), inactive | +0.101" |
| Dm − A −0.007 [−0.016, −0.001], n.d. by seed rule | P11R l35 "| Dm − A (rule 1, pipeline check) | −0.007 (0.010) | ... | no detectable handicap"; P11R l49 "[−0.016, −0.001]" |
| Cm − Dm +0.071 (0.069), +0.018 (0.013) | P11R l36 |
| robust: inactive +0.071 [+0.020, +0.121]; crack +0.009 [+0.003, +0.016] | H09 l565, l566 |
| Cm − A +0.071 (0.067), +0.013 (0.012), credited | P11R l38 "**Cm beats supervised** (credited: rule 2 holds)" |
| relF1@2 robust +0.013 [+0.005, +0.024]; inactive [−0.009, +0.158] | P11R l90; P11R l55 |
| Cmx − A not credited | P11R l39 |
| P12 locked 01:37 | H09 l633 "11 Oct 01:37 IST, commit `7320bd4`" |
| Cm5 − Dm5 +0.023 (0.022), +0.040 (0.027) | H09 l701 |
| replicates on gaint +0.047, +0.078; seeds 3 to 5 | H09 l705; l653 |
| Cm5 − A5c +0.006 (0.014), +0.003 (0.161), +0.015 (0.022) fails | H09 l703 |
| Dm5 − A5c −0.017 [−0.024, −0.010], n.d. by seed rule | H09 l699 "n.d. by the seed rule"; l719 "[−0.024, −0.010]" |
| Dm5 − D5 +0.045 | H09 l700 |
| BN mixing reading | H09 l766 |
| gaint cannot rescue | H09 l675 "gaint never rescues a cv02 rule that failed" |
| calibration gA10 − L3 10% crack +0.004 (n.d.) | H09 l707 "| gA10 − L3 10% (rule 7, calibration) | +0.004 (0.010) | ... | n.d." |

## Section: audit and P13
| Number / fact | Source (quote) |
|---|---|
| 11 Oct 11:24 | H10 l150 "At 05:54 UTC (11:24 IST) on 11 Oct" |
| code checks, no bug | H10 l170 to l175 |
| 0.004 vs 0.038 at step 20,000; 94 to 97% | H10 l181, l182 |
| French et al. on CutMix | H10 l183 |
| BN recalibration +0.01, gap about −0.06; weights | H10 l210, l211 |
| 0 of 350 tensors | H10 l216 "tensors differing: 0 of 350" |
| P13 locked 11:51; Amendment 1 12:51 before any run | H10 l233, l234 |
| Amendment 1 contents, 5 seeds rule, one-day deadline | H10 l248 to l251; H12 l426 to l436 |
| arms and seeds | H10 l255 to l260 |
| no tuning | H10 l246 |
| 13 runs 13:30 to 21:04 | H10 l263 |
| CsM5 − A5c +0.014 (0.016), +0.117 (0.052), +0.033 (0.025) passes | P13R l59; H10 l303 |
| CIs [+0.042, +0.189], [+0.006, +0.055]; top-3 +0.103, +0.020 | P13R l98 |
| BsM5 − A5c +0.036, +0.113, +0.052; crack [+0.021, +0.048] | H10 l304, l330 |
| Cs5 − A5c inactive +0.105 | H10 l305 |
| CsM5 − Cs5 +0.010 n.d.; [+0.004, +0.017] | H10 l306, l332 |
| CsM5 − BsM5 −0.022 (0.014) worse | H10 l307 |
| Cs5 − Cm5 n.d., Cm5 sd 0.139; inactive +0.084 [+0.030, +0.143] | H10 l308, l334 |
| SSL seeds 0.318 to 0.403 vs A5c 0.192 to 0.284 | H10 l296 |
| val 6 inactive cells | H10 l385 |
| no collapse | H10 l353 |
| ratio 0.46, 0.77, 0.98 | H10 l358 to l360; P13R l129 |
| Amendment 2: reason, stopping rule | H07 l46 "because BsM5 − A5c crack IoU (+0.036) was below 0.05 on 3 seeds ... a stopping rule fixed in advance (5 seeds total, reported whatever they show)" |
| s3, s4 0.317, 0.327 | P13R l73 "| BsM5 s3 / s4 | 0.317 / 0.327 |" |
| BsM5 − A5c +0.029 (0.016), +0.107 (0.044), +0.045 (0.023); crack [+0.014, +0.041] | P13R l78, l81 |
| CsM5 − BsM5 −0.015 (0.018) n.d., still negative over cells | P13R l79, l81 |
| without noisy cell CsM5 − A5c crack +0.016 (0.014) | P13R l82 |

## Section: P14, P15
| Number / fact | Source (quote) |
|---|---|
| P14 locked 12:55; 9 runs; 10%; seeds 0 to 2 | H10 l450; l459 "cv02, 10% labels (47 cells), split seed 0, seeds 0–2"; l468 "9, 11 Oct 14:42 to 19:34 IST" |
| tolerant rule on human labels, Dice exact | H10 l453 to l456 |
| scored on revised test labels | H10 l468 "Scored on the revised test labels" |
| L3 − L3o +0.082 (0.011), +0.081 (0.011) | P14R l34 |
| [+0.046, +0.129]; both source groups | P14R l43; H10 l507 |
| L3To − L3o −0.004, +0.041 needed, fails | P14R l35 |
| L3T − L3 inactive +0.037 (0.028) passes | P14R l36 |
| [−0.016, +0.093] | H10 l505 |
| crack AP 0.400 → 0.380 | H10 l515 |
| old-label scoring 0.351 vs 0.332 | H10 l519 |
| reading "change in what is labelled" | H10 l526 |
| P15 locked 12:55 | H10 l548 |
| DeepLabV3+ ResNet-34, 9,562 UCF train cells, 59,760 steps (100 epochs) | H10 l553, l555 |
| 216 encoder tensors, fresh decoder | H10 l556, l562, l564 |
| max 0.79, none ≥ 0.90 | H10 l559 |
| 6 runs gaint, seeds 0 to 2 | H10 l568, l577 |
| gU5 − A5 +0.0096 (0.0100) n.d. | P15R l44 |
| gU10 − gA10 −0.012 (0.011), −0.086 (0.059), −0.014 (0.013) worse; robust | P15R l45; H10 l626 |
| 30 Oct qualification | H10 l632 "So P15 likely tested little more than conv1/layer1 transfer (S; not measured on the P15 encoder)" |

## Section: P16
| Number / fact | Source (quote) |
|---|---|
| our question of 11 Oct | H10 l649 "okay why we using 5 or 10% for ssl?" |
| Part A locked 17:28; Part B 17:35 | H10 l674, l690 |
| CutMix by P13 val rule | H10 l693, l701, l702 |
| CsM5 0.3507, Cs5 0.3652 → CUTMIX=0 | H10 l708, l709, l711 |
| Cs recipe weakest on P13 test crack; test not used | H10 l717 |
| arms, pools 383 / 239 / external, 5 seeds | H10 l723 to l725, l721 |
| pooled P6 seeds after pooling check | H10 l680, l682, l772 |
| verdicts S20, S50, Sx100 with thresholds; width flag | P16R l72 to l74 |
| every CI includes 0 | H10 l775 |
| 4 of 24 runs; 2 of 15 supervised, 2 of 15 SSL | H10 l780, l786 |
| 15 to 31%, 39k to 80k, 787 px, 0.11 to 0.18 | H10 l780 to l782 |
| noisiest of all 582 | H10 l785 |
| post hoc crack +0.002, +0.002, −0.002; verdict unchanged | H10 l789 to l792 |
| 2 to 7% vs 46% | H10 l796 |
| reading | H10 l813, l814 |

## Section: E1
| Number / fact | Source (quote) |
|---|---|
| definitions fixed 12:59, 11 Oct | H10 l1133 "definitions fixed 11 Oct 12:59 IST, commit `21b5a8f`, before any E1 number" |
| metric definitions (20 px, 50 px, 0.5%) | H10 l1149 to l1154 |
| 106 cells of 20221008, not in our 582 nor external pool; 101 CSIR, 5 BMRK; 32 crack, 10 inactive; 67 modules, 1 shared | H10 l1137 to l1140 |
| amendment 13:16 after first pass; four types ignore | H10 l1141 "25 to 28 (scuff, corrosion cell, brightening, star) are marked ignore"; l1165 to l1169 |
| criterion "adopt as primary if narrower" | H10 l1193 |
| tolF1 8 vs crack IoU 13 (test) | H10 l1176, l1178 |
| inactive cell IoU 9 vs 7, 17 vs 10 | H10 l1181, l1182, l1195 |
| L3 100% 0.471 → 0.152; 0.80 → 0.41; L3 10% 0.396 → 0.080 | H10 l1190, l1191; E1R l74 |
| Table rows: P11 Cm − A false alarm +0.113 [+0.049, +0.186]; inactive cell IoU +0.071 [+0.001, +0.166] | P11R l92 |
| P12 Cm5 − A5c false alarm +0.095 [+0.035, +0.162]; inactive cell IoU +0.212 [+0.065, +0.351] | H09 l750 |
| P13 CsM5 − A5c inactive cell IoU +0.467 (0.033 → 0.500) [+0.322, +0.592]; crack IoU +0.001 [−0.011, +0.012]; BsM5 relF1@2 +0.046 [+0.018, +0.072]; Cs5 − Cm5 FA −0.095 [−0.141, −0.050] | H10 l408 to l413; P13R l168 |
| P14 L3 − L3o +0.030 [+0.012, +0.048]; L3T − L3 inactive cell IoU +0.088 [+0.005, +0.193] | H10 l522, l523 |
| P15 gU5 − A5 tolF1 −0.034 [−0.068, −0.004]; gU10 n.d. | H10 l628 |
| P16 S20 inactive cell IoU +0.179 [+0.011, +0.385]; S50 relF1@2 +0.047 [+0.019, +0.077]; Sx100 n.d. | H10 l800 to l802 |
| P17 BsD5 − BsM5 FA +0.049 [+0.011, +0.089] | H10 l898 |
| AL1 AL5 − A5 ext every CI includes 0 | ALR l100 "AL5 − A5, extension (106 cells): every CI includes 0" |
| reading: false alarms about 0.10; separate BN removes; inactive lift | H10 l1200, l1202, l1203 |
| repeated reads | CH05 l141 (E1 read too often) |

## Section: P17, P18, checks
| Number / fact | Source (quote) |
|---|---|
| two methods considered; DCA 3D, three expert decoders, not run | H12 l564 "Skip DCA: a 3D method built on three expert decoders" |
| SKCDF data-flow decoupling, largest ablation credit | H12 l565 "Take SKCDF's one component with the largest ablation credit (data-flow decoupling, +12.74 of +19.61 Dice)" |
| locked 01:51, 13 Oct; seeds 0 to 4 | H10 l843, l850 |
| decoder copy, 0.99 average, loss reaches encoder and copy only; teacher scored | H10 l845 to l848 |
| pipeline check passed (44 lines, 5 seeds) | H10 l853 |
| BsD5 − BsM5 −0.006 (0.013), +0.011 (0.043), −0.008 (0.017) n.d. | P17R l51 |
| 44%, 41%, 39%; about 40% | P17R l54 |
| BsD5 − A5c +0.023, +0.117, +0.037 | H10 l876 |
| crack [−0.011, +0.002], lean in CSIR/ARTS | P17R l71, l78 |
| AP 0.310 vs 0.367 | H10 l897 |
| EMA teacher − student ±0.005 | H10 l1103 "teacher − student is within ±0.005 on every metric for every run" |
| P18 exploratory, BsM chosen after P13 test; locked 17:31 | H10 l915 |
| BsM10 (3) − A10 +0.132 (0.032), [+0.043, +0.235] | H10 l922, l929, l948 |
| BsM20 (5) − A20 +0.060 (0.051), [−0.018, +0.119]; s4 fails on noisy cell | H10 l925, l930, l947, l948 |
| reading: depends on recipe; differences not identified; no locked change | H10 l955, l956 |
| P19 14 Oct, released code | H12 l600 "D40. Reproduce Hanifi 2025 (14 Oct, ~08:33–09:00 IST)"; handbook/15_status_remaining_work.md l42 "Their code, release split, no augmentation" |

## Section: 21 to 23 Oct
| Number / fact | Source (quote) |
|---|---|
| reviewer approval and independent recompute | team_2026-10-21/README.md l28 to l32 ("No launch ... without `APPROVED`"; "the critic verifies it independently, recomputing from the raw per-run files") |
| no newer release; keep split | DD l7, l8 |
| 7 twin test cells; criteria (same source and position, r 0.80 to 0.94, identical crack geometry) | DD l9; DD l76 "same source and module position, high-pass image correlation 0.80–0.94, and identical crack geometry checked visually" |
| 36,405 of 92,074 (39.5%); 12.1% inactive | DD l88 |
| 5%: every twin in unlabelled set | DD l103 |
| reported with and without, post hoc | DD l71 "The lists are post hoc relative to the P-series" |
| BsM5 − A5c without twins +0.019 (0.018), passes; CsM5 inactive only; BsD5 − BsM5 n.d. | DD l112, l114, l115; H10 l312 "Passes on all three, crack only just" |
| D7 = yes, pool 455 → 448, references re-run; old claims kept with lines beside | DD l145, l146; ALP l52 "Pool 455 → 448 cells" |
| later fuller count of shared cells | CH05 l30 "8 test cells are the same physical cell as a training cell and 7 more are neighbouring crops" (text cites Section data-split) |
| SK1 21 to 22 Oct, ABSH on decoupled recipe, 5 seeds, 448 pool | H10 l960, l971, l972 |
| BsDB5 − BsD5 −0.0044 (0.0100) / −0.0113 (0.0282) / +0.0044 (0.0100) n.d. all four sets | H10 l982, l986 |
| closed 22 Oct | H10 l996 "Closed 22 Oct" |
| S-a: τ = 1 fixed before any number; prior from labelled cells | H10 l999 "z_c − log π_c, with π from each run's own labelled cells and τ = 1 fixed before any S-a number" |
| +0.015 to +0.023 at 5% | H10 l1003 |
| symmetric BsM5 +0.037 | H10 l1005 |
| yardstick BsM5 +0.0135 (0.0159) n.d.; "a yardstick, not a verdict against SSL" | H10 l1006, l1010 |
| inactive gains survive | H10 l1016 |
| AL1 question | ALP l9 "At 5% labels ... does ALHVR, adapted to 2-D EL cells and run on today's supervised base with a schedule under which its unlabelled loss is actually applied, beat the step-matched supervised baseline?" |
| protocol 21 Oct; results 23 Oct | ALP l1 "(agent 1, 21 Oct 2026)"; ALR l1 "(23 Oct 2026)" |
| adaptation steps: base, schedule, separate BN, FeatureNoise only (dropout zeroed 96 to 99.7%), full-res prototypes (orthogonal at 1/8, explains 4.6%), class-normalised sharpening, detached target | H10 l1035 to l1041 |
| λ_max 0.1 (paper's value) and 1.0 CPS, matched to BsM5 gradient share | H10 l1037 "λ_max. Matched to BsM5's unlabelled gradient share (D0c): 0.1 for full ALHVR (the paper's value), 1.0 for CPS" |
| arms A5, AL5, ALd5, ALdh5 (λ 0.3), CPS5, CPSm5, BsM5 re-run; 5 seeds | H10 l1047 to l1053; l1043 "5 seeds each, 20,000 steps, network A at the final step" |
| training machine (cv02) | ALR l6 "Code `3a94457`, cv02" |
| SSL arms on 448 pool | ALR l7 |
| checks C1 tensor identity, A5 identical to A5c, 35 runs step 20,000 | H10 l1056, l1058, l1060 |
| launched 21 Oct 15:20 | ALLOG l43 "21 Oct 15:20 trainer: **AL1 v2 LAUNCHED** on cv02 GPUs 0-3" |
| last rescore 23 Oct | ALL last lines "[2026-10-23 01:07:29] big1 g1 rescored al1_ALdh5_s4 rc=0" (log clock; 21 Oct start line 09:49:49 matches 15:19 IST, so the log is UTC) |
| AL1 table values | ALR l36 to l46 (P, S1, S2, S3 ALd5, S3 ALdh5, S3 CPS5, S4, ref BsM5) |
| CIs [−0.0287, −0.0065], [−0.1906, −0.0750], [−0.0536, −0.0118] | ALR l48 |
| WORSE in all four cell sets | ALR l64 |
| ALHVR-family WORSE on inactive | ALR l56 |
| CPS level with supervised, below BsM5 | H10 l1096; ALR l45 |
| inactive recall A5 0.276, AL5 0.124, CPS5 0.400 (post hoc) | H10 l1081 to l1083 |
| four predictions held; inactive damage not predicted | H10 l1086 to l1091 |
| reading | H10 l1092 to l1096 |
| ALHVR question since before 7 Oct | H10 l1093 "The old-era question 'does ALHVR help with a fair schedule?' (doc 13 E11) is answered: no" |
| from 24 Oct all labels | CH05 l73 "The work then turned to models trained on all labels (from 24 Oct)" |

## Section: Summary tables and final section
All cells repeat values given above (same sources). "label quality as the larger lever" (P14 row, Led to) is our reading, from H10
l531 "P14 strengthens claim 1 of the evidence table (label version matters more than any SSL effect)". "closed for this fine-tune"
(P15) from H10 l632. "nothing launched" (P17) from H10 l907 "Nothing launched." "no locked change" (P18) from H10 l956.
Final section: +0.082 (P14R l34), +0.101 (H09 l570), CsM5 − BsM5 n.d. at 5 v 5 (P13R l79); "only P11 passed both under the shared
forward" from H09 l787, l788 (summary table: P11 Cm − Dm passes and Cm − A passes; P12 Cm5 − A5c fails; P8 to P10 none).

## Derived values
None. Every number is copied. Counts of machine assignment are copied from the Machine columns cited above.

## MISSING_CITES (plain text; used as \CITE{} in the .tex)
- Sohn, K., Berthelot, D., Li, C.-L., et al. (2020). FixMatch: Simplifying semi-supervised learning with consistency and confidence. NeurIPS 2020.
- Oquab, M., Darcet, T., Moutakanni, T., et al. (2024). DINOv2: Learning robust visual features without supervision. TMLR 2024.
- French, G., Laine, S., Aila, T., Mackiewicz, M., Finlayson, G. (2020). Semi-supervised semantic segmentation needs strong, varied perturbations. BMVC 2020 (cited in H10 l183 as "French et al. (BMVC 2020)").
- SKCDF (CVPR 2025): the decoupled-data-flow semi-supervised medical segmentation paper named in H10 l839 and H12 l565; full reference to be taken from literature/notes before citing.
- Chen, X., Yuan, Y., Zeng, G., Wang, J. (2021). Semi-supervised semantic segmentation with cross pseudo supervision. CVPR 2021 (ALP l40 "From CPS (Chen 2021)").

## UNSOURCED
None left in the text. Removed while drafting: a claim that the separate forward moved a primary by more than the tolerant/hard choice
(the separate-minus-joint contrast Cs5 − Cm5 is n.d. by the seed rule, H10 l308), replaced by sourced values.

## CONFLICTS (found, not resolved in the sources)
1. Twin test cells: the 21 Oct data decision lists 7 (DD l9, l79 to l88); CH05 l30 says "8 test cells are the same physical cell as a
   training cell and 7 more are neighbouring crops" (later audit). The .tex gives the 21 Oct list of 7 as such and points to
   Section data-split for the later count; it does not state 8 itself.
2. P12 calibration: H09 l707 gives gA10 − L3 10% crack IoU +0.004 but its verdict text says "agree on crack within 0.006"; H10 l596
   says "within 0.004 to 0.006". The .tex copies the difference, +0.004.
3. P6 headroom: README value −0.001 (pooled) vs `results/p6/p6_rules.txt` still printing the interim "+0.0256" (H08 l475 to l477).
   The .tex uses −0.001, as the later protocols did, and mentions the replaced interim +0.026.
4. Protocol header clock times disagree with git commit times for several protocols (H09 l28, H10 l51, H12 l163); the .tex uses the
   git times, as the handbook does.
5. AL1 contrast count: ALP l57 says 1 primary + 9 secondary, while the table lists 8 secondary contrasts (ALR l57 notes this). Not
   used in the .tex.
6. Launcher return codes of P13 Amendment 2, P17 and P18 were always 0 because of a logging bug (H10 l25, l854); completion was
   confirmed by step-20,000 logs and checkpoints instead. The .tex says P17's pipeline check passed and does not rely on rc.

## AUDIT 27 Nov (independent checker; see AUDIT_REC_pseries.md)
Every value above was re-checked against the primary file (results/*/README.md, *_rules.txt, team_2026-10-21/alhvr/results.md,
team_2026-10-21/data/decision.md, results/ema_check/README.md, results/sk1/sk1_rules.txt, results/sk1/la_sa.md); 27 of these files
have the same md5 on the server (canonical) as in the laptop repo. Edits made to the .tex, with their sources:
- l16: P1 to P5 "examined models or probes trained on the 20211104 masks": P3, P4 and P5 scored on revised labels
  (results/p3_label_versions/README.md l6; results/p4_feature_probe/README.md l4 "47 images (`labeled_10pct`, seed 0), old labels";
  results/p5_region_pl/README.md l8 "Crack (14), revised labels").
- l31: thresholds are printed in parentheses, not brackets (brackets are the 95% intervals throughout the .tex).
- l41 to l44: P15 pretraining ran on the training machine: results/p15/README.md l6 "Pretraining (cv02, one run ...)", l10 "Fine-tuning
  (gaint, RTX PRO 4500): 6 runs". P12 calibration arm gA10 on gaint: results/p12/README.md l8; it is a cross-machine contrast (rule 7,
  l49 "gA10 − L3 10% (rule 7, calibration) ... n.d."), so "a rule never compared arms across machines" was replaced.
- l90 to l91: P4 probes trained on old masks, scored on revised (results/p4_feature_probe/README.md l4, H08 l296 to l299).
- l100: "8% of ground-truth crack": results/p5_region_pl/README.md l18 "recall of all GT crack 0.08", l40 "covers only 8% of GT crack".
- l176: the rare_frac 0.001 to 0.002 is seed 2 only: results/p10/README.md l95 "stays at 0.001–0.002 from step 4,000 in seed 2, against
  0.007–0.009 in seeds 0–1".
- l231: loss ratios are seed 0: results/p13/README.md l124 "At step 20,000, s0, the unlabelled / supervised loss ratio is".
- l247: "scored higher" (no rule was applied to the old-label scoring): results/p14/README.md l65 to l70.
- l262 to l263: Part B was locked before any P16 SSL run, not before any P16 run (Part A runs started 17:28): results/p16/README.md l3
  "Part B (Amendment 1) was locked before any SSL run", l7 "11 Oct 17:28–22:06 IST"; H10 l674, l690.
- l301 to l302: extension cells use the E1 label set (release 20221008 masks), not v1: results/e1/README.md l10 "masks are the
  release's own"; ch04_data.tex sec:data-labels "The E1 set is the release 20221008 masks ...".
- l331: "most of all" (an unsourced superlative) replaced by the sourced value: results/p13/README.md l168 "+0.467 (0.033 → 0.500)".
- l359 to l360: the 21 Oct team were AI agents (team_2026-10-21/README.md l3 "orchestrates four agents", l27 to l31); wording as in
  app_build.tex l309 to l311.
- l406: BsM5 is scored on its EMA teacher: team_2026-10-21/alhvr/results.md l9 "Network A (`model`) for two-network arms and A5, EMA
  teacher for BsM5".
- l448: P10 supervised references on the second machine: results/p10/README.md l7.
- l485: "the seven test cells of the 21 Oct list": the later audit counts 8 same-cell test cells (ch05_legacy.tex l30), so the count
  is tied to its list (team_2026-10-21/data/decision.md l75 to l88, l103).
