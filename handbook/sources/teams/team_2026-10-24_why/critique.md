# Critique log (C, critic and moderator), 24 Oct 2026

Tags: **E** evidence (file + number, recomputed or read), **R** reading (interpretation of evidence), **S** speculation (no direct evidence).
Verdicts on claims: **holds**, **holds with caveat**, **weakened**, **rejected**, **open**.

## 0. Independent checks by C (CPU only, before R1/R2 reported)
Script: scratchpad `chk.py` (reads `results/sk1/la_sa_test.json`, per-cell TP/FP/FN, final-step weights). Rule 1 = max(0.01, 2·sqrt((sdA²+sdB²)/3)), 5 v 5 seeds.

### C0.1 The "free logit bias" yardstick is one-sided (E)
Crack IoU, test. Reproduces `la_sa.md` §2 to 4 decimals.

| Contrast | all 50 | no twins | no twins + noisy cell |
|---|---|---|---|
| BsM5 − A5c (no LA either side) | +0.0289 (0.0156) passes | +0.0193 (0.0181) passes | +0.0193 (0.0182) passes |
| BsM5 − (A5c+LA) | +0.0135 (0.0159) n.d. | +0.0043 (0.0187) n.d. | +0.0038 (0.0189) n.d. |
| (BsM5+LA) − (A5c+LA) | **+0.0368 (0.0134) passes** | **+0.0350 (0.0153) passes** | **+0.0345 (0.0155) passes** |
| (BsD5+LA) − (A5c+LA) | +0.0235 (0.0112) passes | +0.0203 (0.0135) passes | +0.0204 (0.0136) passes |
| (CsM5+LA) − (A5c+LA) | +0.0182 (0.0173) passes | +0.0099 (0.0174) n.d. | +0.0141 (0.0165) n.d. |

- **Verdict on the team README framing** ("BsM5 helps crack only up to what a free logit bias gives supervised"): **weakened.** That is true only when the bias is applied to one side. With the bias on both sides, BsM5 and BsD5 still pass on crack IoU in every cell set, and the matched gain is larger than the unmatched one (+0.035 vs +0.019 without twins).
- **R:** SSL and the prior shift are additive on crack IoU, and LA gives BsM5 twice the gain it gives A5c (+0.031 vs +0.015 without twins). One reading: SSL improves the crack ranking (AP 0.367 vs 0.287, `alhvr/results.md` §1) more than the argmax shows, and LA converts ranking into recall.
- **Caveats (E):** τ = 1 was fixed after SK1's LA rows (`la_sa.md` limits); BsM5+LA loses 0.081 crack precision (0.635 → 0.554), beyond the 0.05 width flag; relF1@2 in reduced sets only from the critic's scorer. So "(SSL+LA) − (sup+LA)" is post hoc and flagged, not a verdict.

### C0.2 SSL's crack gain is confined to the source the labelled set covers (E, post hoc, descriptive)
Crack IoU by source, test without the 7 twins, tau 0, seed means; threshold computed per source from seed sds.

| Source | test crack px (no twins) | 5% labelled crack px (`labelling_plan.md` §1) | A5c | BsM5 | Δ (thr) | BsD5 |
|---|---|---|---|---|---|---|
| CFVS | 16,420 | 11,646 | 0.293 | 0.339 | **+0.047 (0.012)** | 0.329 |
| CSIR | 11,146 | 687 | 0.350 | 0.371 | +0.021 (0.024) | 0.346 |
| BMRK | 25,235 | 5,387 | 0.165 | 0.168 | +0.002 (0.030) | 0.186 |
| ARTS | 2,673 | 47 | 0.133 | 0.102 | −0.030 (0.035) | 0.108 |

- **R:** the hard-PL SSL gain on crack lands where the supervised model is already competent and the labelled set already has crack (CFVS 65% of labelled crack px). It does nothing for BMRK (27% of test crack, recall 0.19) or ARTS. Consistent with self-training amplifying what the labelled set teaches (confirmation bias), and with null_diagnosis §2.3. Per-source thresholds are post hoc and the source groups were not pre-declared, so this is descriptive.
- Same table with LA (all 50 incl. twins, recall): BsM5+LA lifts BMRK recall 0.191 → 0.279 and CFVS 0.522 → 0.614. So LA, not SSL, is what moves the under-represented source.

### C0.3 Inactive: SSL raises recall, not precision (E)
Test, all 50, seed means, IoU / precision / recall: A5c 0.253 / 0.771 / 0.276; BsM5 0.360 / 0.694 / 0.431; CsM5 0.370 / 0.700 / 0.441; BsD5 0.371 / 0.750 / 0.427. LA adds little on inactive (A5c 0.264). So the inactive gain is not a prior shift; it survives the yardstick (`la_sa.md` §2).

### C0.4 What labels buy vs what SSL buys (E, cross-experiment within cv02, descriptive)
From `handbook/11` (b): A5c 5% → L3 10% (+24 labelled cells): crack IoU 0.304 → 0.396 (+0.092), inactive 0.253 → 0.294 (+0.041), relF1@2 0.720 → 0.814 (+0.094). Best SSL at 5% (BsM5 − A5c): +0.029 / +0.107 / +0.045.
- **R:** for crack, +24 labelled cells buy about 3× the best SSL gain; for inactive, SSL at 5% buys more than doubling the labels. This asymmetry is the core fact any "why" story must explain. Caveats: L3 10% is 3 seeds from P6; the 10% labelled set contains 19 crack cells vs 9 at 5% (`handbook/13` A1), so "labels" here also means "more crack variety".

### C0.5 Crack probability is bimodal on GT crack (E)
`results/al1/hist_revised.npz`, test, seed means, share of GT crack px by p(crack):

| Arm | < 0.001 | 0.001-0.1 | 0.1-0.5 | 0.5-0.95 | ≥ 0.95 | middle total |
|---|---|---|---|---|---|---|
| A5 | 0.569 | 0.042 | 0.018 | 0.024 | 0.347 | 0.084 |
| BsM5 (D7) | 0.449 | 0.098 | 0.044 | 0.049 | 0.360 | 0.191 |
| CPS5 | 0.547 | 0.057 | 0.024 | 0.030 | 0.342 | 0.111 |
| AL5 | 0.596 | 0.043 | 0.019 | 0.025 | 0.317 | 0.087 |

GT-negative px in 0.001-0.95: A5 13.4k, BsM5 44.8k.
- **R:** for the supervised model, any threshold or prior rule can act on at most 8% of GT crack; the rest is confidently right or confidently wrong. BsM5 moves 12 points of GT crack out of bin 0 into the middle band, which is the ranking gain that LA converts into IoU (C0.1). This is class-conditional evidence for R2's "no dynamic range" claim, better than the global conf_frac.

### C0.6 Per-source SSL gain moves with the labelled draw (E, cross-protocol, descriptive)
Crack IoU per source, test without twins and noisy cell, seed means (`la_sa_test.json`, τ 0).

| Arm | ARTS | BMRK | CFVS | CSIR |
|---|---|---|---|---|
| A5c (5 seeds) | 0.133 | 0.165 | 0.293 | 0.374 |
| L3 10% (3) | 0.197 | 0.219 | 0.333 | 0.414 |
| BsM10 (3, P18 expl.) | 0.212 | 0.229 | 0.359 | 0.428 |
| L3 20% (3, P6) | 0.283 | 0.191 | 0.330 | 0.424 |
| BsM20 (5, P18 expl.) | 0.307 | 0.257 | 0.309 | 0.427 |
| A50 (5) | 0.375 | 0.327 | 0.369 | 0.452 |
| L3 100% (3, P6) | 0.435 | 0.378 | 0.397 | 0.479 |

- SSL − sup by source: 5% BMRK +0.002, ARTS −0.030; 10% all four +0.010 to +0.026; 20% BMRK +0.066, CFVS −0.021.
- Supervised BMRK is non-monotone (10% 0.219, 20% 0.191): which cells are drawn matters, not only how many.
- **R:** supports "SSL amplifies what the labelled draw covers" (R1) and shows the 5% source pattern is a property of one draw. Mixed protocols (P6 vs P18 seeds), 3-seed arms, exploratory.

## 1. Claims from R1 (data side), `r1_data_side.md` v1

| # | Claim | Tag check | Verdict |
|---|---|---|---|
| R1-1 | SSL crack gain is source-bound (CFVS/CSIR), zero/negative on BMRK/ARTS | E; reproduced by C (C0.2) | **holds** at 5%, one draw. Weakened as a general law by C0.6 (at 10-20% SSL reaches BMRK) |
| R1-1b | Labels lift BMRK/ARTS +0.21/+0.30 (5→100%) | E, 2-seed A20/A100 in R1's files; C's 3-5 seed version agrees in direction | holds as description. Confounded: random labels also add every source; does not show *targeted* beats random |
| R1-1c | 5% set has 0 ARTS crack px on E-SCDD masks (47 px are P6 remap) | E | plausible, matches `labelling_plan.md` diff; not rechecked by C |
| R1-2 | Strict IoU compressed by label jitter (1-px shift IoU 0.47-0.56) | E from `handbook/13` A5 | holds. Duplicate-mask IoU is one pair (0.257), not a range: R1 to fix |
| R1-3 | Scarcity is equal for crack and inactive (pool/labelled px 12.1 vs 11.5); error type differs (inactive under-extended regions, crack missing components) | E (ratios, P/R) + R (mechanism) | **holds**; best answer so far to the survivorship test. C0.3 agrees (inactive recall +0.16, precision flat) |
| R1-3b | Inactive gain reaches CSIR (0.002 → 0.109) without labelled CSIR inactive | E but 3 cells hold all CSIR/ARTS inactive | fragile; tag |
| R1-4 | Twins inflate scores but are not transductive (D7 pool: non-twin gain +0.0197 vs old pool +0.019) | E | **holds** |
| R1-5 | "Faint" is confounded with BMRK (62% of faint-tertile px) | E | **holds**; withdraws an earlier team claim. Good |
| R1-D3 | Tolerance-aware primary | – | reframe: relF1@2 is already primary; changing primaries post hoc is a method change |

Open challenge to R1 (round 1): coverage vs intrinsic difficulty (CSIR: 548 labelled px yet best A5c; BMRK: 5,387 px yet worst, blurriest, 4-px labels); D1 design must use draw-level variance.

## 2. Claims from R2 (method side), `r2_method_side.md` v1

| # | Claim | Tag check | Verdict |
|---|---|---|---|
| R2-1 | Saturated, confidently-wrong teacher; thresholds have no dynamic range | Evidence given was global conf_frac 0.965 (background-dominated), CW-BASS (Pascal, DINOv2; abstract checked, `arxiv:2608.12773`), P5 (old ALHVR nets, 20% split) | **holds with better evidence** (C0.5, class-conditional bimodality). The cited evidence was weak; P5 is not the P-series base |
| R2-2 | True misses are a recognition failure the PL loop cannot reach (12% recovered by BsDBn5) | E | holds as a measurement. "Upper bound for any threshold fix" too strong: BsDBn5 removes bg PLs and is confounded with head overwrite |
| R2-3 | Published gains come from weak/from-scratch baselines with 0-Dice classes | E (DINO-Mix Table 1 per R2; DINO-Mix exists, `arxiv:2602.07819`); SKCDF verified by earlier critics | holds for Synapse-type benchmarks; R2 does not show it for Cityscapes/Pascal, where UniMatch-type gains are on pretrained bases |
| R2-4 | Closest public regime (SemiCurv Gaps384 5%) shows the same null | C read Table III: TCSM 37.8 vs UNet 34.9 omitted; Gaps384 5→100% headroom only +4.1; CrackForest 5% MT +6.8, CutMix +5.9; single runs | **rejected as stated.** Public thin-crack evidence is mixed |
| R2-5 | We fail Oliver's conditions (labelled not i.i.d. with pool by source; val too small to tune) | E for our side; Oliver abstract checked | holds; converges with R1-1 |
| R2-C5 | Untuned recipe could hide ~0.01 crack IoU | S, conceded | open; cannot be separated with current data |
| R2-C4 | DTCT entropy-min suppresses inactive | R, one-change arm named | holds as reading |

## 3. Literature checks by C
Only papers returned by the Research MCP in this session.
- **CReST** (Wei et al., CVPR 2021, `doi:10.1109/cvpr46437.2021.01071`), abstract: SSL methods "perform poorly on minority classes" yet "still generate high precision pseudo-labels on minority classes". Our match (E): teacher confident crack PL share 0.0015 at 20k vs labelled-batch GT crack 0.0030 (`results/sk1/diag_trajectories.md`, sk1_BsD and sk1_BsDB rows); test crack precision 0.63 vs recall 0.37-0.41 (C0.1). So the minority PL is precise and under-covering, as CReST describes. CReST's fix (rebalanced self-training) is close to ABSH/LA, which we ran (SK1 n.d.; LA additive). Classification benchmarks only, so the transfer to 1-3 px structures is R.
- **Arazo et al.** (IJCNN 2020, `doi:10.1109/ijcnn48605.2020.9207304`): pseudo-labelling overfits to its own wrong predictions (confirmation bias). Fits C0.2 (gain only where the labelled source is) as R, not E: we have no direct measure of confirmation over training.
- **Oliver et al.** (2018, `arxiv:1804.09170`), abstract: simple baselines are "often underreported", SSL methods differ in sensitivity to labelled/unlabelled amounts, and performance "can degrade substantially when the unlabeled dataset contains out-of-distribution examples". Relevant twice: (i) our supervised L3 was laddered (P6) while most SOTA papers compare against weaker baselines (SKCDF Synapse baseline: no threshold, joint BN, `null_diagnosis.md` §1.5); (ii) our external pool (CSIR/ARTS) never helped (`handbook/11` row 5).

- **SemiCurv** (`doi:10.1109/tip.2022.3189823`), Table III read in full text: Gaps384 5% UNet 34.9, TCSM 37.8, MT 34.3, CutMix 33.5, cGAN 33.7, VAT 29.6, SemiCurv 38.0; UNet 100% 39.0. CrackForest 5% UNet 60.1, MT 66.9, CutMix 66.0. R2's v1 omitted TCSM and CrackForest; corrected in round 1.
- **Existence checks (get_paper):** CW-BASS v2 `arxiv:2608.12773` (abstract: 98% of Pascal pixels ≥ 0.95 with DINOv2; adaptive cutoffs flood retention); DINO-Mix `arxiv:2602.07819`; Chen et al. 2020 `doi:10.1609/aaai.v34i04.5763` (class mismatch; R1 later dropped it as the frame); Wei et al. 2020 `arxiv:2010.03622` (expansion assumption; also assumes minimal overlap between class neighbourhoods, which faint cracks on background violate: R). Table-level claims for DINO-Mix, UniMatch V2, Torpey and DARS were read by R2, not re-read by C.

## 4. Discussion rounds (SendMessage)
- **Round 0 (C to both):** evidence standards; five challenges each (asymmetric LA yardstick, survivorship, twins, untuned recipe, benchmark regimes).
- **Round 1:**
  - R1 conceded SSL recovers ~9% of true misses; withdrew "SSL helps least on faint" (faint is 62% BMRK); split competence into coverage + intrinsic difficulty after C's CSIR/BMRK counter-example; supplied labelled per-source counts by fraction (BMRK 2/5,387 px at 5% and 10%, 5/6,235 at 20%; ARTS 0 / 3 / 9 cells). ARTS tracks coverage; BMRK does not (+0.054 at 10% with no new BMRK labels, −0.028 at 20% with +3 cells). Redesigned D1 as R / Tc / Ts with draw-level variance.
  - R2 conceded SemiCurv was selective (now "mixed, single-run, no prior"), replaced global saturation with C's class-conditional histogram (re-derived, exact match), dropped BsDBn5 as a bound, downgraded copy-paste.
- **Round 2:**
  - R1 accepted: likeliest D1 outcome Ts ≈ Tc (still informative); 3 seeds per draw is a rule conflict for the user; audit before D1; R/Tc/Ts is a proposal replacing `labelling_plan.md` §2a. Split cause 2 into inactive-edge convention (cause) and IoU compression (measurement).
  - R2 pushed back and C accepted: (a) the 8% bound is for a fixed final model; training dynamics moved it to 19% in BsM5, but no training-time rule we ran moved pool true misses by more than 0.046; (b) BsM20 BMRK +0.066 is descriptive only. R2 moved MIM above copy-paste, gated by the frozen probe. IoU compression: R2 "measurement, changes no verdict" (ALHVR WORSE and SK1 null on relF1@2 too). R1 and R2 now agree on this.

## 5. Final verdicts and open disagreements
**Converged:**
- SSL's crack gain is real, small, and passes even with LA on both sides (C0.1); its argmax size equals a free bias, its ranking effect is larger (AP 0.287 → 0.367, mid-band 8% → 19%).
- The gain is bound to what the labelled draw covers (C0.2, C0.6, R1 §1); the teacher is confidently wrong where coverage is missing (R2 §1). One mechanism seen from two sides.
- Inactive vs crack: same scarcity, different error type (R1-3, C0.3).
- Failed methods failed for method-specific measured reasons (SK1: no prior collapse; AL1: Ω1 holds most rare pixels, DTCT suppresses inactive).
- Twins inflate absolute scores; not transductive (R1-4).
- IoU compression is a measurement effect; inactive-edge convention is a coverage cause.

**Open (go to SYNTHESIS):**
1. D1's primary contrast: R2 keeps source-targeted vs random (T − R, ~30 GPU-h); R1 wants Ts − Tc with a crack-count control (~40 GPU-h). C's view: R1's design answers the user's item and the confound; R2's is cheaper. User's call.
2. BMRK: intrinsically hard (blur, 4-px labels, downscaled ELPV) vs label artefact. Decided by the user's 40-component audit (17 of 40 are BMRK), not by argument.
3. Whether a training-time rule could reach true misses beyond 0.046: R2 says possible, unshown; nothing we ran did.
4. Untuned SSL recipe could hide ~0.01 crack IoU (R2-C5): cannot be separated with existing data.
5. DTCT-entropy one-change arm: explains the AL1 inactive harm; both R2 and C say not worth GPU. Open but unfunded.
6. R1's D5 (source-matched pool): R2 did not engage. Cost understated by R1 (BsM5 runs took ~5.5 h each on cv02 lanes, `results/al1/launch.log`, so 5 runs ≈ 25-30 GPU-h, not 8).

**Cost note (E):** `results/al1/launch.log`: A5 supervised runs ~2.5 h and BsM5 ~5.5 h on shared cv02 lanes (two runs per GPU). `labelling_plan.md`'s "1.5 h per supervised run" is optimistic for packed lanes.
