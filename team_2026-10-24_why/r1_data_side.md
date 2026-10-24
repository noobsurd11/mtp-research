# R1: data/problem side. What about our data, labels and metric breaks SOTA SSL assumptions

R1, 24 Oct 2026. Tags: **[E]** evidence (file + number), **[R]** reading, **[S]** speculation.
All results: one split (seed 0), 50 test cells, 5 seeds unless stated. "n.d." means not detected at the rule-1 threshold, not "no effect".

New CPU analyses (this session; scripts in the scratchpad, outputs quoted below):
- `shift.py`: crack/inactive composition, contrast tertiles, crack near inactive, by source, for labelled 5% / D7 pool (448) / train / test. Masks: E-SCDD files (`~/mtp/datasets/escdd_full`), old mask for the 5 cells E-SCDD lacks. Contrast tertile edges −0.39 / −0.06 as in `skcdf/null_diagnosis.md` §2.3. Sanity: test tertile shares 0.48 / 0.29 / 0.23 vs the probe's 0.48 / 0.28 / 0.24.
- `src.py`, `d7.py`, `frac.py`: per-source pooled crack and inactive IoU / recall / precision from `results/al1/per_image.json`, `p12`, `p13`, `p16/per_image_{A,S}.json`, `p18/per_image.json` (per cell [TP, FP, FN] crack, then inactive).
- `comp.py`: source × contrast cross-tab of relaxed recall from `skcdf/verify_a4/c4_probe.json` (211 components).
- `sharp.py`: image sharpness and crack label width per source.

## 0. Verdict (reading, ranked)
SSL is not failing everywhere on crack. Its crack gain is real but source-bound: it lands on the sources the 23 labelled cells already teach (CFVS, CSIR) and is zero or negative on the sources labels would fix (BMRK, ARTS). The benchmarks SOTA methods win on do not have this structure. Ranked data-side causes:

1. **Source coverage of the labelled set, plus intrinsic source difficulty** (strongest; new numbers, §1). SSL cannot create recognition of a source or crack type the labelled set does not teach. Labels can: BMRK and ARTS crack IoU rise +0.21 to +0.30 from 5% to 100% labels, while BsM5 at 5% gives them +0.002 and −0.022. Revised after C's round 1 (§1.5): coverage explains ARTS cleanly (3% of crack). BMRK (27.5%) is also intrinsically hard (blurriest, 4-px labels) and does not track labelled px from 5% to 20%.
2. **Split after C's last point:** (a) **cause:** the inactive-edge convention is under-taught (15.0% of test crack vs 6.2% of labelled crack); (b) **measurement, not cause:** jitter and IoU compression hit both arms and shrink the visible SSL gain (gap to L3 100% closed: 17% on IoU vs 29% on relF1@2, C). Original text: **Label convention and metric** (§3). 1-px label jitter caps strict IoU (a perfect mask shifted 1 px scores 0.47 to 0.56). IoU sits at 0.30 while relF1@2 sits at 0.72, and a free prior shift moves IoU by +0.015 to +0.023. Small SSL gains on crack are measured on a compressed, operating-point-sensitive scale.
3. **Crack vs inactive signal geometry** (§2, answers C's survivorship test). The data scarcity is the same for both classes (pool-to-labelled pixel ratio 12.1 for crack, 11.5 for inactive), so scarcity alone cannot be the cause. What differs is the error type: supervised inactive is under-extended regions (precision 0.77, recall 0.28), which confident self-training extends. Supervised crack is missing recognition on whole components.
4. **Twins / CFVS time series** (§4). They inflate absolute scores and 44% of SSL's relaxed-recall gain sits on them, but the gain is not transductive: removing the twins from the pool leaves the non-twin gain unchanged.
5. Weak or unsupported: small unlabelled pool, the noisy cell, faint cracks as a separate cause (§5).

## 1. Source coverage: SSL amplifies what labels teach; it does not add sources

### 1.1 What the 23 labelled cells contain [E, `shift.py`]
| Source | Labelled 5%: crack cells, crack px | D7 pool crack px (share) | Test crack px (share) |
|---|---|---|---|
| ARTS | **0 cells, 0 px** | 10,458 (0.048) | 2,620 (0.029) |
| BMRK | 2, 5,387 | 25,811 (0.120) | 25,235 (0.275) |
| CFVS | 3, 11,646 | 122,742 (0.569) | 52,642 (0.573) |
| CSIR | 2, 548 | 56,628 (0.262) | 11,146 (0.121) |
| SDLE | 1, 208 | 197 | 195 |
| total | 8 cells, 17,789 px | 215,836 | 91,838 |

- [E] On E-SCDD's own masks the 5% set has **no ARTS crack**. `skcdf/labelling_plan.md` §1 counts 47 ARTS px and 687 CSIR px; the difference (47 + 139 = 186 px) matches P6's old-mask remap pixels (handbook 03 §3.1). So the only ARTS "crack" the model is taught at 5% is remap pixels.
- [E] Inactive: 2 labelled cells (BMRK 1, CFVS 1), 20,517 px; pool 36 cells, 236,309 px.

### 1.2 Per-source crack IoU, 5% arms (pooled over cells, seed mean, noisy cell excluded) [E, `frac.py`, `src.py`; AL1 runs = D7 pool]
| Arm | ARTS | BMRK | CFVS | CFVS non-twin | CSIR |
|---|---|---|---|---|---|
| A5 (al1) | 0.164 | 0.165 | 0.360 | 0.293 | 0.374 |
| BsM5 (al1, D7) | 0.142 | 0.167 | 0.402 | 0.343 | 0.389 |
| CPS5 | 0.154 | 0.175 | 0.364 | 0.293 | 0.374 |
| AL5 | 0.146 | 0.151 | 0.347 | 0.279 | 0.332 |
| CsM5 (p13) | 0.120 | 0.160 | 0.390 | 0.319 | 0.367 |
| BsD5 (p17, old pool) | 0.144 | 0.186 | 0.392 | 0.329 | 0.369 |

- [E] BsD5 is the one arm with a visible BMRK lean (+0.021); still far below the +0.215 labels give.

- [E] BsM5 − A5: ARTS −0.022, BMRK +0.002, CFVS +0.042 (non-twin +0.050), CSIR +0.015. BMRK + ARTS are 30% of test crack px.
- [E] Relaxed recall (component probe, BsD5 − A5c): CFVS holds 57% of test crack px but 73% of the relaxed-recall gain; BMRK 27% of px, 23% of gain; ARTS 3%, 0% (`comp.py`).

### 1.3 The same sources respond strongly to labels [E, `frac.py`; P16 A arms, cv02; A20 and A100 have 2 seeds in these files: descriptive only]
| Supervised | ARTS | BMRK | CFVS | CSIR |
|---|---|---|---|---|
| 5% (A5) | 0.164 | 0.165 | 0.360 | 0.374 |
| 20% (A20) | 0.292 | 0.198 | 0.492 | 0.421 |
| 50% (A50) | 0.388 | 0.327 | 0.509 | 0.452 |
| 100% (A100) | 0.464 | 0.380 | 0.522 | 0.469 |
| 5→100% gain | **+0.300** | **+0.215** | +0.162 | +0.095 |

- [R] BMRK is not a fixed convention ceiling, which I first suspected from its 4-px labels (§3). More labelled cells raise it by +0.215. CFVS and CSIR, where SSL helps, saturate first.
- [R] So the crack deficit at 5% is largely missing source coverage. SSL's pseudo-labels come from a teacher that does not fire on the uncovered sources (pool true-miss share CSIR/ARTS 0.461 vs CFVS/BMRK/SDLE 0.341, `skcdf/second_opinion_a2.md`), so SSL cannot transfer coverage it never had.
- [R] Withdrawn after R2's challenge: I first called this Chen et al.'s class-distribution mismatch (`doi:10.1609/aaai.v34i04.5763`). That paper is about OOD *classes* in the unlabelled set, which we do not have. R2's framing fits better: self-training expands labels only through augmentation neighbourhoods (Wei et al., `arxiv:2010.03622`), and label-safe augmentation never maps a CFVS crack onto BMRK/ARTS appearance.
- [E] Weight: BMRK is the load-bearing contrast (27.5% of test crack, 10 cells, +0.002). ARTS is 2,620 px (2.9%) over 10 cells, so its −0.022 is a small-pixel number.
- [E] BMRK is under-scored rather than unseen: LA lifts BsM5's BMRK recall 0.191 → 0.279 (C, `critique.md` C0.2), and the 5% set has 5,387 BMRK crack px. So BMRK cracks get some crack logit mass, but not enough to cross the argmax.
- [S] Caveat: one split. The 5% draw decides source coverage (handbook 13 A9). Split seeds 1 and 2 would have different source mixes, and the effect could change.

### 1.4 How far this is from the benchmark regimes [E for the cited numbers, R for the comparison]
| | Ours (5%) | ACDC 10% (ALHVR) | Synapse 20% (SKCDF) | Cityscapes / Pascal 1/16 |
|---|---|---|---|---|
| Labelled units | 23 cells, crack in 8, inactive in 2 | 7 patients (handbook 05, ALHVR) | 4 volumes (`null_diagnosis.md` §1.5) | per-image, many instances per class |
| Target geometry | 1–3 px lines, median label width 1.75 px (handbook 13 A5) | compact organs | organs, failure = class at 0 Dice | objects and regions |
| Target share | crack 0.19% of train px | – | – | – |
| Label agreement | two duplicate pairs with independent masks: crack IoU 0.257 (handbook 13 A5) and 0.21 (`ARTS_00081_r5_c1` vs `ARTS_00020_r5_c1`, handbook 03 §2.2); 1-px shift IoU 0.47–0.56 (handbook 13 A5) | not measured here | not measured here | not measured here |
| Sources | 5 sources; per-source coverage in the 5% set: 0 to 3 crack cells | one dataset protocol | one | one city / one dataset |
| SSL gain reported | crack +0.02 to +0.03 IoU (P13, P17) | +9 Dice (ALHVR headline, handbook 05) | +6 to +19 Dice, gains = rescue of 0-Dice classes (`second_opinion_a2.md` §2) | Pascal 1/16 +9 to +12; Cityscapes +3 with strong encoders (UniMatch V2, `doi:10.1109/tpami.2025.3528453`, handbook 05) |

- [R] The SOTA gains are mostly rescues of classes or structures the supervised model gets badly wrong but that are visually unambiguous (organs, objects). Our crack is never collapsed (IoU 0.30, `second_opinion_a2.md` §2). Its errors are missing source coverage plus label jitter, neither of which a confident-teacher loss reaches.
- [S] "Organ labels are much more consistent than crack labels" is plausible but I have no measurement of benchmark label agreement. Speculation.

### 1.5 Coverage vs intrinsic difficulty, across fractions (C's round-1 challenges 1–2)
Labelled crack per source, split seed 0, nested subsets (`cov.py`, E-SCDD masks) [E]; supervised and SSL−sup per-source crack IoU from C's recompute (no twins, no noisy cell) [E, C]:

| Fraction | BMRK labelled (cells, px) | ARTS labelled | CSIR labelled | sup BMRK | sup ARTS | SSL−sup BMRK | SSL−sup ARTS | SSL−sup CFVS |
|---|---|---|---|---|---|---|---|---|
| 5% | 2, 5,387 | 0, 0 | 2, 548 | 0.165 | 0.133 | +0.002 | −0.030 | +0.047 |
| 10% | 2, 5,387 | 3, 614 | 4, 4,739 | 0.219 | 0.197 | +0.010 | +0.015 | +0.026 |
| 20% | 5, 6,235 | 9, 2,916 | 11, 8,620 | 0.191 | 0.283 | **+0.066** | +0.024 | −0.021 |
| 50% | 12, 17,026 | 19, 5,627 | 29, 31,717 | 0.327 | 0.375 | – | – | – |
| 100% | 24 (all) | 42 | 50 | 0.378 | 0.435 | – | – | – |

- [E] ARTS supervised IoU rises monotonically with labelled ARTS crack (0 → 614 → 2,916 → 5,627 px). That supports coverage.
- [E] BMRK does not track labelled px: 5% → 10% gains +0.054 with no new BMRK labels; 10% → 20% adds 3 BMRK cells and drops −0.028. Only 20% → 50% (+7 cells, +10.8k px) gives +0.136. Even at 50%, BMRK (0.327) is below CFVS at 5% (0.360).
- [E] CSIR has the least labelled crack among covered sources (548 px) yet the best A5 IoU (0.374): its test cracks are dark (dark tertile 0.42) and sharp.
- **Conceded [R]:** per-source competence is coverage **plus** intrinsic difficulty. BMRK is a hard source (downscaled ELPV, blurriest, 4-px labels, 38% placement within 1 px). Targeted BMRK labels may underperform the label-scaling curve. Cause 1 is strongest for ARTS (3% of test crack) and partial for BMRK (27.5%).
- [E, R] SSL's per-source gain loosely follows coverage: it is ≤ 0 on a source with 0 labelled crack cells (ARTS 5%), small with 2 cells (BMRK 5–10%), and largest on BMRK only at 20% (5 cells, +0.066), while CFVS saturates (−0.021 at 20%). This is consistent with "SSL expands only what labels cover", but it rests on one nested draw, and BsM20 is exploratory (P18). A threshold of about 3–5 labelled crack cells per source is a reading, not a measured rule.

## 2. Why inactive benefits and crack does not (C's survivorship challenge)
- [E] Scarcity is not the differentiator. Pool/labelled pixel ratio: crack 215,836 / 17,789 = 12.1; inactive 236,309 / 20,517 = 11.5 (`shift.py`). Inactive is even rarer by cells (2 vs 8 labelled).
- [E] Error type differs (al1 test, pooled, seed mean, `src.py`):
  - inactive A5 precision 0.771, recall 0.276 → BsM5 0.746 / 0.444 (+0.17 recall);
  - crack A5 0.626 / 0.371 → BsM5 0.636 / 0.409 (+0.04 recall).
- [E] Inactive gains reach a source with no labelled inactive: CSIR inactive IoU A5 0.002 → BsM5 0.109, CPS5 0.258. **Fragile:** all CSIR/ARTS test inactive sits in 3 cells (handbook 07 §8, per C). Crack gains do not reach ARTS, which has no labelled crack (−0.022).
- [R] Inactive is a large, dark, region-scale class. A teacher that finds part of a region confidently can extend it, and pixel-level jitter at its boundary costs little IoU. Crack errors are whole components the teacher never fires on (40 components missed by every arm; `null_diagnosis.md` §2.3), and IoU on 2-px lines is dominated by placement. Same scarcity, different failure mode: this is what separates the classes.
- [S] Why inactive transfers to CSIR and crack does not to ARTS: dark-region appearance is source-invariant, thin-line appearance depends on resolution and sharpness (§3). Not tested.

## 3. Labels, conventions and metric
- [E] Label width by source (`sharp.py`, median over cells): BMRK 4.0 px, CFVS 2.0–2.83, CSIR/ARTS 2.0. BMRK is also the blurriest (mean |Laplacian| 1.9–2.2 vs 3.5 CFVS, 6.3–6.6 ARTS). BMRK cells are ELPV cells downscaled 300 → 256 px in a padded 512 canvas, with the worst label placement: 38% within 1 px of the darkest line vs ARTS 75% (`data_analysis/benchmark_el_report.md`, handbook 02 §8).
- [E] Strict-IoU compression: A5 crack IoU 0.304 vs relF1@2 0.720; BsM5 0.331 vs 0.761 (`alhvr/results.md` §1). LA τ=1 adds +0.015 to +0.023 IoU at 5% but only +0.008 to +0.015 relF1@2, with a precision drop up to −0.081 (`results/sk1/la_sa.md` §1).
- [R] On relF1@2, SSL's gain over supervised (+0.036 to +0.045) is about 3× its IoU gain and survives against A5c+LA for BsM5 (+0.036, passes) on all 50 cells (`la_sa.md` §2). The IoU yardstick understates SSL on crack. relF1@2 without the twins is n.d. for BsM5 (+0.028 vs 0.029), so this is marginal.
- [E] Label noise is large relative to SSL effects: old vs revised labels move crack IoU by +0.05 to +0.07 on re-scoring and +0.082 on training (P3, P14; handbook 13 A5). Rill-García et al. (`doi:10.1016/j.neucom.2022.01.051`) report that inaccurate crack annotations cut F-measure by up to 20% on a synthetic benchmark. Li et al. (`doi:10.1109/iccv51070.2023.00119`) treat SSL segmentation under label noise as a separate problem. Neither is EL.
- [R] Inactive-edge cracks: 15.0% of test crack px lie within 2 px of inactive, but only 6.2% (1,104 px) of labelled crack does (pool 21.5%) (`shift.py`). The convention the test scores (crack drawn along an inactive edge) is barely taught. Its relaxed recall is 0.44 vs 0.69 elsewhere (`null_diagnosis.md` §2.3).

## 4. Twins and the CFVS time series (C's challenge 4)
- [E] Old pool (twins unlabelled in pool), scored without the twins: BsM5 − A5c crack +0.019 (thr 0.018) (`data/decision.md` D6).
- [E] D7 pool (twins removed from the pool), scored without the twins: BsM5 − A5 crack **+0.0197 (thr 0.0181)**, inactive +0.115 (0.057); without twins and the noisy cell +0.0199 (0.0181) (`d7.py` on `results/al1/per_image.json`).
- [R] Removing the twins from the pool changes the non-twin crack gain by < 0.001. The twins' share of the gain is not transductive leakage. The twin cells are large, dark CFVS cracks where every arm is better, and SSL gains more there (+0.037 IoU) because CFVS is the source it already covers.
- [E] Against the LA yardstick, without the twins BsM5 − (A5c+LA) crack is in [−0.014, +0.004], n.d. (`la_sa.md` §2).
- [S] CFVS is a time series of the same modules. Non-twin pool cells from the same modules (earlier or later stages) may still give a module-level transductive advantage. I have not measured module overlap beyond the 7 twin pairs.

## 5. Factors checked and how much they explain
| Factor | Supported? | Evidence / note |
|---|---|---|
| Crack thin and rare; pred/GT 0.59–0.74 | [E] yes, but SSL moves it little | `null_diagnosis.md` §2.1: A5c 0.593, BsD5 0.667 |
| ~half of GT crack confident miss | [E] yes | bin-0 0.42–0.57 (`null_diagnosis.md` §2.2) |
| 38% true miss, not offset | [E] yes (pool) | BsD5 0.378 vs offset 0.180 (`second_opinion_a2.md`); SSL recovers 0.037 of A5c's 0.415 (≈9%): SSL does reach some misses (conceded to C) |
| Misses concentrate on faint cracks | [E] partly; **confounded by source** | BMRK holds 13,011 of ~21,000 faint-tertile test px (62%) (`comp.py`). Outside BMRK the faint tertile has recall 0.42 (A5c) → 0.48 (BsD5), n43. CSIR faint 0.11–0.17 (1,917 px). The faint gain share (0.26) ≈ its pixel share (0.23): SSL does not help faint cracks less than others in relaxed recall. I withdraw "SSL helps least on faint" |
| Inactive-edge cracks | [E] yes | §3; recall 0.44 vs 0.69; under-taught 6.2% vs 15.0% |
| ARTS/BMRK sources | [E] yes, strongest | §1 |
| 40 always-missed components | [E] exist, 5.4% of crack px; **unaudited** | `skcdf/audit_sheet.csv` 0 of 40 rows filled; real vs artefact unknown |
| Twins | [E] inflate scores, not transductive | §4 |
| Label noise / convention | [E] large vs SSL effects | §3 |
| Small unlabelled pool | [E] **not supported** | pool/labelled ratio 19.5 (448/23) is similar to Cityscapes 1/16 [R]; P9 pool-size effect ≈ 0; external 11,938 pool gave no gain (handbook 13 A7), but it is mismatched, so this is not a clean test |
| 23 cells, inactive in 2 | [E] yes for variance, not as the differential cause | inactive sd up to 0.14 (handbook 13 A1); inactive still gains most (§2) |
| Noisy cell | [E] a measurement hazard, not a mechanism | AL1 BsM5 FP on it ≤ 206 px (`alhvr/results.md` §4); P16 runs up to 80k px |
| IoU vs tolerant F1, LA | [E] yes | §3 |
| Labelled→test shift | [E] mixed | test crack darker (dark tertile 0.48 vs 0.17 in labelled 5%); inactive-edge 0.150 vs 0.062; image noise median equal (0.99) in all sets (`shift.py`) |

## 6. Directions from the data side (each needs team-lead / user approval)
| # | Hypothesis (falsifiable) | Evidence | Cheapest test | Cost | Expected effect | Kill |
|---|---|---|---|---|---|---|
| D1 | **Source coverage, not crack count, drives crack at 5%.** Adding 12 crack cells from the weak sources (BMRK/ARTS/CSIR) beats adding 12 crack cells drawn from all sources (CFVS-heavy) | §1.3, §1.5 | Retrospective, supervised L3, final weights. Arms: R = +12 random train cells; Tc = +12 random crack cells, any source; Ts = +12 crack cells, 6 BMRK / 4 ARTS / 2 CSIR, random within source. 3 draws × 3 seeds each = 27 runs. **Key contrast Ts − Tc** (source at equal crack count); Tc − R = crack-count effect. Threshold on **draw-level** variance: per-draw seed mean, then 2·sqrt(var_draw_Ts/3 + var_draw_Tc/3), floor 0.01. Also vs Tc+LA, per source, four cell sets | ~27 × 1.5 h ≈ 40 GPU-h | [S] Ts − Tc overall crack IoU +0.01 to +0.02 (BMRK is 27.5% of test crack; a +0.05 to +0.10 BMRK gain gives +0.014 to +0.028 pooled); BMRK relaxed recall +0.1. Random +12 ≈ +0.04 over A5c (C's scaling from +24 → +0.092). Near-threshold: may be n.d. | Ts − Tc n.d. at draw-level variance **and** BMRK/ARTS recall moves < 0.05 |
| D2 | **Per-source analysis is free.** SSL gain in all existing arms is concentrated in CFVS/CSIR | §1.2 | CPU only, done here for AL1/P12/P13 | 0 | – | already shown; extend to P17/P18 |
| D3 | **Report relF1@2 against sup+LA** (already a primary; no change of primary) in all four cell sets with relaxed counts | §3 | CPU, critic's scorer (`verify_a4/sa_verify_a4.txt`) | 0 GPU | all 50: BsM5 − (A5c+LA) +0.036, passes; without twins +0.028 (thr 0.029), n.d. | – (reporting) |
| D4 | **Inactive-edge convention.** Excluding or tolerance-banding cracks within 2 px of inactive raises every arm's crack IoU, not the gap | §3 | CPU re-score with a band mask on existing predictions (needs prediction maps → GPU inference, ~1 h) | ~1 GPU-h inference | all arms +0.01 to +0.03, gap unchanged | gap changes sign |
| D5 | **Source-matched pool.** SSL with pool restricted to sources present in the labelled set does no worse on crack, i.e. the uncovered-source pool cells contribute nothing | §1 | training: 5 runs | ~8 GPU-h | crack Δ vs BsM5 within ±0.01 | restricted pool clearly worse on CFVS/CSIR |
| D6 | **Stop SSL for crack; keep SSL for inactive.** Thesis claim: SSL adds region-scale classes; crack needs labels and coverage | §1–2 | none (claim from existing results) | 0 | – | D1 shows targeted labels do no better than random **and** SSL+LA on more seeds passes vs sup+LA |

Rank: D2 (done) > D1 > D3 > D6 (as framing) > D4 > D5.

**D1 caveats (agreed with C, round 2):**
- **Likeliest outcome: Ts ≈ Tc.** BMRK gained +0.054 from 5% to 10% with no new BMRK labels, so crack variety from any source transfers, and Tc is a strong rival. Ts ≈ Tc is still informative: crack count, not source, would then be the lever. Tc − R is reported as the cleaner answer to the user's pending "12 targeted vs 12 random" item.
- **Rule conflict for the user.** 3 seeds per draw breaks the standing rule of ≥ 5 seeds for effects < 0.05. Draw variance dominates here, but the user must approve the deviation explicitly. Not decided by us.
- **Audit first.** 17 of the 40 always-missed components are BMRK (`skcdf/labelling_plan.md` §4). If the user's audit marks many as label artefacts, part of BMRK's "intrinsic difficulty" is convention (4-px labels, 38% placement within 1 px), and Ts's BMRK quota should change. Order: audit, then D1.
- **Status.** The R / Tc / Ts design is a proposal to replace `labelling_plan.md` §2a (T vs R). It is not decided.
