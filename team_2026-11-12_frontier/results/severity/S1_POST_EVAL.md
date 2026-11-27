# S1 t5_post_eval: per-cell severity outputs from our out-of-fold predictions

Severity track builder, 15 Nov 2026. Spec: `cards/T12_benchmark_protocol_spec.md` section 6, with the critic's fix (`cards/WAVE3_REVIEW.md` section 2, T12 row "t5_post_eval": reuse T8's `c_phys.py` rule; run the pre-check also with predicted crack and ribbons). Tags: E = measured (file given), R = paper or dataset page, S = judgement.
Nothing here trains or tunes a model. No sealed cell (legacy test, E1) is read: the dumps are the cv5v2 out-of-fold sets, read through `bench/w1read.discover` (refuses sealed sets); `cells.tsv` only through `udev.load_cells_safe`.

## 1. Rule (written 15 Nov 21:52 IST, before any number of this item existed; not changed after)

### 1.1 Inputs
- gaint: PF = `house_r34_unetpp_pf_v11`, W1-G + W1-G2 dumps, seeds 5 to 8 (`bench_dumps/w1g/...:w1g_pf_v11_f[0-4]_s[5-8]`).
- cv02 (relayed): PF seeds 5 to 9 (`w1c1_pf_v11`), HOUSE seeds 5, 6 (`w1c2_house_v11`), and the five tranche 1 rows, seeds 5, 6 (`r1_<row>`), through `bench_reads/w1c/links` and `bench_reads/rows1/links`.
- Ground truth: label set v1.1 (`bench_data/masks_v11`), ignore px not scored. 532 P532 cells, each scored once out of fold. A read never mixes machines.
- The 4 known duplicate cells (`benchmark/splits/dup_crossfold_v1.tsv`): every number is on 532 cells; the primary is also printed on 528 cells beside it (PROTOCOL_v0.2 s11 item 5).

### 1.2 Per-cell outputs (computed from a class map alone; GT only to score)
Class ids from `make_masks_v11.py` NAMES: inactive 11, crack 14, padding 7, ribbons 4, busbars 9.
- **Derived inactive region** R (PROTOCOL_DRAFT 4.4: "labelled inactive plus the crack pixels it encloses"), the same rule for GT and prediction: R = I or (C and (closing(I, 5 x 5 square) or fill_holes(I))), I = class 11, C = class 14. So a crack line running inside an inactive area (up to about 4 px wide) or fully surrounded by it counts as inactive; a crack on the border between inactive and active area does not.
- **Inactive area fraction** a = |R and keep| / |keep and map != padding|, in % (keep = not ignore; for the label-free output keep = all px). Error e = a_pred - a_gt (percentage points).
- **Bands** {0, (0, 1%), >= 1%}, by a == 0 exactly, 0 < a < 1, a >= 1. 3 x 3 confusion with counts; linear-weighted Cohen's kappa.
- **Cell-level inactive detection** at a >= 0.5%: sensitivity over cells with a_gt >= 0.5%; false-alarm rate over the cells with a_gt == 0 (the inactive-free cells; spec: 484). Cells with 0 < a_gt < 0.5% are in neither count.
- **Crack length** = skeleton px (`bench/skel.py`) of crack and keep; error pred - GT; printed as descriptive, labelled "not a power proxy (P617)".
- **Crack orientation**: for each crack component of at least 20 px (8-connected), the angle (0 to 90 degrees) between its principal axis and the ribbon direction. Ribbon direction = px-weighted axial mean (doubled-angle average) of the principal axes of the ribbon components of the same map. (S: one principal axis over all ribbon px of a cell is ill-posed, because 2 to 3 parallel ribbons spread across the cell give similar variance along and across; the per-component mean is the same quantity in substance.) No ribbon px: undefined, counted. Summary: share of crack skeleton px at 0 to 30, 30 to 60, 60 to 90 degrees, prediction and GT. Descriptive.
- **Isolation risk**: T8's `c_phys.py` rule, reimplemented as a function with its parameters unchanged (cell = map not in {1, 2, 3, 4, 5, 6, 7, 8, 9, 21, 22, 255}; crack dilated by 1 px (3 x 3); free = cell minus dilated crack; a component of free (4-connected, `ndi.label` default, as c_phys) is isolated if it touches the dilated crack's 1-px ring, does not touch ribbons or busbars (classes 4, 9) dilated by 2 px, and has >= 50 px). Evaluable only if crack >= 20 px and ribbon or busbar px exist (as c_phys); otherwise the score is 0 (the rule cannot fire) and the cell is counted as not evaluable. Score s = isolated px / cell px. The reimplementation must reproduce `cards/T8_precheck/c_phys.json` (iso px per cell on GT) exactly; if it does not, the isolation part is reported as blocked.
- **Module view**: per image id (`cells.tsv` image_id) among the 532 cells, the worst cell = the cell with the largest a; module value = that a, with its band. GT worst cell likewise; error and 3 x 3 band confusion at image level. The number of P532 cells per image id is printed (most image ids hold few cells, so this is a partial module view).
- **Error bar given to a user**: from the out-of-fold cells pooled over seeds, per predicted band, the 10th, 50th and 90th percentile of a_gt and of e. For the module view the same over image ids by the band of the predicted worst cell.

### 1.3 Statistics
- Point value of every pooled statistic = mean over seeds of the per-seed value (protocol convention). Intervals: two-stage group bootstrap (330 cv5v2 groups with replacement, then one seed per fold and arm), 2,000 draws, `random.Random(0)`, as `crossfit_op.boot_pair` / `gap_census.boot`. SE = sd of the bootstrap draws.
- **Primary (spec):** per-cell inactive area fraction MAE (% of non-padding px) over the 532 OOF cells, per machine. Descriptive: no pass mark.

### 1.4 Decision rules (fixed now)
- **D1, isolation risk pre-check (spec, word for word in substance):** on GT masks, over the P532 cells with GT crack (v1.1, keep; spec: 229): AUROC of s for "cell has GT inactive (a_gt > 0)" and Spearman of s with GT inactive area a_gt, over the same cells (average ranks for ties). GT pass: AUROC >= 0.75 and Spearman >= 0.5. **Critic's fix:** the same two statistics with s computed from the predicted map (predicted crack and ribbons, full map), same cells and same GT labels, mean over seeds of the per-seed value, per machine; predicted pass with the same two thresholds. Isolation risk enters T5 as a label-free risk score only if the GT pre-check passes AND the predicted version passes on both machines (gaint PF, cv02 PF). GT pass and predicted fail: dropped from the output ("supported on clean masks, not carried by our predictions"). GT fail: dropped (no power or label support). Spearman over the GT-inactive cells only is printed and decides nothing.
- **D2, value test (spec, word for word in substance):** T5 earns a place beside the headline only if, on the W1-C entries (cv02: HOUSE against PF), the per-cell inactive area MAE either (a) orders HOUSE vs PF differently from pooled inactive IoU (point estimates: HOUSE better by MAE iff delta MAE < 0; better by IoU iff delta IoU > 0; the orders differ iff these disagree), or (b) separates them with a larger |z|, z = delta / SE from the same two-stage bootstrap. Otherwise it is a one-table appendix. Pooled inactive IoU here = class 11 over keep px from one confusion over all cells (must reproduce W1C_READ: PF 0.503, HOUSE 0.522, else D2 is blocked).
- **D2 on the tranche 1 rows (task addition):** the same (a) and (b) for each of the five rows against PF (cv02). They do not change D2; if 3 or more of the 5 rows give the opposite placement to D2 (at least one of (a), (b) where D2 found none, or none where D2 found one), the result says "D2 contradicted by the rows" and the lead decides.
- **What the outcomes mean:** D2 pass = the per-cell inactive fraction separates methods in a way pooled IoU does not, so it is printed beside the headline (it still never ranks methods; spec). D2 fail = a one-table appendix with the per-cell outputs; the severity output for WattCycle is still the inactive fraction per cell and worst cell per module with its error bar, because that is the quantity with support in the literature (P263 R); it is not a validated power estimate in either case. No result here says anything about electrical power: none of the 532 cells has an electrical measurement.

## 2. Numbers (E)
Section 1 is unchanged since 21:53: with sections 2 to 5 put back to their placeholders the file hashes to md5 440734f5 again (checked 22:27).
Tool: bench_sev 637e2ce (`bench/post_eval.py` md5 b1c6d2f9, `scripts/bench_post_eval.py` e8f9dbc1; 17 unit tests pass). Run 15 Nov 21:56 to 21:59 by `bench_reads/severity/S1/run_s1.sh` (log `run_s1.log`). Outputs: `bench_reads/severity/S1/{gaint,cv02}/post_eval.{json,txt}` (md5 f5dbc7d2, 920aaf4a, 2aa01fbb, 31b2c522). Interval = two-stage group bootstrap, 2,000 draws.

**Checks.** The isolation function reproduces `c_phys.json` on GT: 532 cells compared, 0 mismatches. Pooled inactive IoU from this tool: PF 0.5025 (gaint), PF 0.5027 and HOUSE 0.5217 (cv02), equal to W1C_READ / ROWS1_READ (0.503, 0.503, 0.522), so D2 is not blocked. Label-free a (all px) differs from the scored a (keep px) by at most 0.02 pp.

**GT (derived region, v1.1, 532 cells):** bands 0 / (0, 1%) / >= 1% = 484 / 17 / 31 (spec: 484 / 10 + 7 / 31). Detection classes: 38 cells with a_gt >= 0.5%, 484 with a_gt = 0, 10 in between. 229 cells with GT crack, 48 of them with GT inactive.

### 2.1 Per-cell outputs, pooled (point = mean over seeds [95% interval])
| Machine, arm (seeds) | MAE of a, pp (primary) | bias, pp | inactive IoU | sens @0.5% | false alarm @0.5% | kappa, 3 bands | crack skeleton ratio pred / GT |
|---|---|---|---|---|---|---|---|
| gaint PF (5 to 8) | **0.121 [0.063, 0.189]** | -0.085 [-0.155, -0.028] | 0.503 [0.391, 0.599] | 0.730 [0.535, 0.885] | 0.0026 [0, 0.0086] | 0.792 [0.681, 0.873] | 0.817 [0.763, 0.870] |
| cv02 PF (5 to 9) | **0.122 [0.066, 0.188]** | -0.083 [-0.152, -0.024] | 0.503 [0.392, 0.594] | 0.732 [0.531, 0.881] | 0.0025 [0, 0.0084] | 0.782 [0.668, 0.869] | 0.821 [0.766, 0.872] |
| cv02 HOUSE (5, 6) | 0.115 [0.060, 0.178] | -0.068 | 0.522 | 0.737 | 0.0021 | 0.772 | 0.816 |
| cv02 unet_r34_pf | 0.113 [0.060, 0.176] | -0.079 | 0.522 | 0.711 | 0.0021 | 0.761 | 0.806 |
| cv02 dlv3p_r34_pf | 0.127 [0.067, 0.199] | -0.102 | 0.478 | 0.763 | 0.0000 | 0.801 | 0.746 |
| cv02 hanifi_vgg16_unet_pf | 0.137 [0.071, 0.212] | -0.100 | 0.498 | 0.737 | 0.0010 | 0.757 | 0.827 |
| cv02 ucf_dlv3_r50_pf | 0.121 [0.063, 0.189] | -0.093 | 0.497 | 0.737 | 0.0010 | 0.794 | 0.659 |
| cv02 pratt_dlv3p_wcec | 0.108 [0.054, 0.171] | -0.073 | 0.506 | 0.842 | 0.0010 | 0.748 | 0.897 |

- 528 cells (4 duplicate cells excluded): MAE PF 0.1216 (gaint), 0.1233 (cv02), HOUSE 0.1158; inactive IoU unchanged to 4 decimals.
- The MAE over 532 cells is mostly zeros: 484 cells have no inactive and the models put almost none there. Post hoc split (descriptive, decides nothing; computed from the same caches): PF MAE on the 48 GT-inactive cells 1.25 pp (gaint) / 1.28 pp (cv02), on the 31 cells with a_gt >= 1% 1.79 / 1.82 pp, on the 484 inactive-free cells 0.009 / 0.008 pp. HOUSE: 1.22 / 1.73 / 0.005 pp.
- Band confusion, PF cv02, summed over 5 seeds (rows GT 0 / (0, 1%) / >= 1%; columns predicted): [[2374, 42, 4], [35, 46, 4], [17, 28, 110]]. Large cells are found; the (0, 1%) band is unreliable both ways.
- Per source, PF cv02: MAE ARTS 0.003, BMRK 0.399, CFVS 0.185, CSIR 0.117 pp; sensitivity BMRK 0.72, CFVS 0.88, **CSIR 0.20** (CSIR inactive cells are mostly missed at the 0.5% level).
- Crack length (descriptive, **not a power proxy, P617**): predicted skeleton px are 0.82 of GT on PF (both machines); per-cell MAE 58 to 59 px.
- Crack orientation (descriptive): share of skeleton px at 0 to 30 / 30 to 60 / 60 to 90 degrees to the ribbons: GT 0.836 / 0.121 / 0.043; PF 0.832 / 0.140 / 0.028 (cv02), 0.833 / 0.141 / 0.027 (gaint). Most crack length runs near the ribbon direction in these labels; the model follows that. Cell maps without ribbon px (orientation undefined): GT 9, PF 6 to 8 per run set.

### 2.2 Module view (worst cell per image id)
354 image ids in P532; cells per image id: 1 cell 244, 2 cells 68, 3 cells 28, 4 to 10 cells 14. So 69% of "modules" are a single cell and this is a partial module view.
| Machine, arm | worst-cell MAE, pp | kappa, 3 bands | same worst cell as GT (multi-cell ids with GT inactive) |
|---|---|---|---|
| gaint PF | 0.174 | 0.806 | 0.750 |
| cv02 PF | 0.176 | 0.800 | 0.768 |
| cv02 HOUSE | 0.166 | 0.798 | 0.763 |

### 2.3 D1 isolation pre-check (229 GT crack cells, 48 with GT inactive)
| Map | AUROC (has inactive) | Spearman with a_gt | Pass (>= 0.75 and >= 0.5) |
|---|---|---|---|
| GT crack + GT ribbons | 0.829 | 0.577 | **PASS** |
| predicted, gaint PF (mean of 4 seeds) | 0.698 | 0.375 | FAIL |
| predicted, cv02 PF (mean of 5 seeds) | 0.708 | 0.394 | FAIL |
| predicted, cv02 HOUSE / unet / dlv3p / hanifi / ucf / pratt | 0.686 / 0.683 / 0.700 / 0.692 / 0.730 / 0.780 | 0.361 / 0.363 / 0.402 / 0.390 / 0.520 / 0.488 | FAIL (all) |
GT detail: evaluable 228 of 229; the rule isolates >= 0.5% of the cell in 30 of 48 inactive cells and 18 of 181 others; Spearman over the 48 inactive cells only 0.354 (printed, decides nothing).

### 2.4 D2 value test (cv02; arm minus PF; z = delta / bootstrap SE)
| Arm | delta MAE, pp [95%] | z MAE | delta inactive IoU [95%] | z IoU | (a) order differs | (b) larger abs z | place |
|---|---|---|---|---|---|---|---|
| **HOUSE (decides)** | -0.0075 [-0.0456, +0.0181] | -0.45 | +0.0190 [-0.0304, +0.0873] | +0.65 | no | no | **no** |
| unet_r34_pf | -0.0092 [-0.0436, +0.0161] | -0.61 | +0.0195 [-0.0293, +0.0790] | +0.72 | no | no | no |
| dlv3p_r34_pf | +0.0050 [-0.0359, +0.0467] | +0.24 | -0.0248 [-0.1079, +0.0567] | -0.60 | no | no | no |
| pratt_dlv3p_wcec | -0.0147 [-0.0542, +0.0137] | -0.85 | +0.0036 [-0.0558, +0.0819] | +0.10 | no | yes | yes |
| hanifi_vgg16_unet_pf | +0.0141 [-0.0149, +0.0471] | +0.88 | -0.0048 [-0.0581, +0.0538] | -0.17 | no | yes | yes |
| ucf_dlv3_r50_pf | -0.0011 [-0.0409, +0.0284] | -0.06 | -0.0055 [-0.0641, +0.0651] | -0.17 | yes | no | yes |
No interval excludes 0 for either metric in any contrast; the largest |z| is 0.88.

## 3. Outcome
- **Primary (descriptive):** per-cell inactive area fraction MAE = 0.121 pp [0.063, 0.189] on gaint PF and 0.122 pp [0.066, 0.188] on cv02 PF; on the 48 cells that have inactive area the error is about 1.25 to 1.28 pp (post hoc split). The model under-states inactive area on average (bias -0.08 pp; median error in the >= 1% band -0.3 pp).
- **D1: isolation risk is DROPPED** under the rule: the GT pre-check passes (AUROC 0.829, Spearman 0.577), but computed from our predicted crack and ribbons it fails on both machines (PF 0.698 / 0.375 on gaint, 0.708 / 0.394 on cv02; no arm passes). Reading: "supported on clean masks, not carried by our predictions". It does not enter T5.
- **D2 on the W1-C entries: FAIL.** HOUSE vs PF: MAE and pooled inactive IoU order the two the same way (both favour HOUSE) and MAE separates them less (|z| 0.45 against 0.65). Under the spec rule T5 is a **one-table appendix**, not a column beside the headline.
- **Rows check: "D2 contradicted by the rows", the lead decides.** 3 of the 5 rows give the opposite placement (pratt and hanifi by (b), ucf by (a)), which is the trigger I fixed. S: every one of these firings is inside noise (no interval excludes 0; all |z| <= 0.88; ucf's "order differs" rests on deltas of -0.001 pp and -0.006 IoU), so in my judgement the rows do not show that per-cell MAE separates methods better than pooled IoU; the appendix placement is the reading I would keep. This is the lead's call by my own rule.
- Nothing here is about electrical power: no P532 cell has an electrical measurement.

## 4. What a user would receive (S, built from the E numbers above; PF on cv02)
**One cell** (example, chosen by fixed rule: median predicted value among cells in the >= 1% band, seed 5): `CFVS_00143_r4_c3`. Output: "inactive (electrically isolated) area about 2.7% of the cell (5 models: 2.2 to 3.7%), band >= 1%. From the out-of-fold record of cells in this band, the true value lies between the prediction - 1.7 pp and + 3.8 pp for 80% of cells (here 1.0% to 6.5%); 93% of cells predicted >= 1% truly are >= 1%. Crack length 2,737 skeleton px (descriptive), mostly within 30 degrees of the ribbons." The labelled value is 1.66%, inside the interval.
For a cell predicted in band (0, 1%), only 40% truly are in that band, and the 80% range of the true value is 0 to 3.0%: the user is told "small or no inactive area, low confidence". Band 0 is right for 98% of cells.
**One module image** (chosen post hoc as the image id with the most cells whose predicted worst cell is >= 1%, cv02 PF): `CFVS_00146`, 3 labelled cells. Output: "worst cell r8_c3, inactive area about 11.4% (5 models: 10.8 to 12.2%), band >= 1%; the other two cells 0%." Labelled worst cell: 14.6%. Error bar for a module whose worst cell is predicted >= 1%: 80% of true worst-cell values lie between the prediction - 1.7 pp and + 3.8 pp; 96% are truly >= 1%. The predicted worst cell is the labelled worst cell in 77% of multi-cell image ids with inactive area.
**What it must not be read as:** not a power-loss estimate and not a power band (no electrical ground truth on any of these cells; the link from inactive area to power is a literature claim, P263 R, untested here); not a crack severity (crack length is not a power proxy, P617; the isolation score is dropped); not a module rating (69% of image ids hold one labelled cell; real modules have 60 to 144 cells and the worst cell of a crop set is not the worst cell of the module); not valid on unseen modules or half-cut cells (all numbers are cv5v2 pool cells "on cv5v2 as built", with the same-module twins of PROTOCOL_v0.2 s11 item 9; CSIR inactive cells are mostly missed, sensitivity 0.20).

## 5. Owed
- Lead: the D2 rows contradiction (section 3): keep T5 as a one-table appendix (my reading) or place it beside the headline.
- The external check of "inactive fraction tracks power" is T12 item 8 (`severity_external_elpvpower`), still gated: data downloaded under S0, but the 20-module cell-cutting pilot (gate b) and the embedding check against BMRK (gate c) are not done.
- Not run: the module view on real full modules (needs a set with whole modules), any inference on new images.
- Post hoc in this file, labelled as such, deciding nothing: the MAE split by GT stratum and the choice of the example module.
