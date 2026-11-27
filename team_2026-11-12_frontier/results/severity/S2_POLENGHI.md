# S2 Polenghi staged damage: does predicted inactive area or isolation risk track measured power loss?

Severity track builder, 15 Nov 2026, on gaint. Data: Polenghi et al. 2026, PV_EL_HDR_BW_Test_DB, Mendeley Data doi 10.17632/pxyzzkbs4b.1 (P564), CC BY 4.0 (S0). Local copy `~/mtp/datasets/severity_public/polenghi/raw/` (260 files, sha256 checked in S0). Use: inference and analysis only; nothing trains or tunes a model; nothing redistributed. Tags: E = measured (file given), R = paper or dataset page, S = judgement.

## 0. The set, from its files (E unless marked)
- **Units.** Two physical devices, CellID 0.1 and 0.2 (`EXPERIMENTAL PARAMETERS.txt`: polycrystalline, 4.5 Wp, 5 V, 0.9 A, 130 x 150 mm, DAUERHAFT AP130X150MM). From the EL images (S, by eye): each device is a mini-panel of 10 vertical cell strips (about 13 x 150 mm each) with dark gaps between strips and two dark horizontal interconnect bands; it is not one wafer cell.
- **Stages.** 84 rows in `ELPV_DATA_FULL.CSV` (`;`-separated): 0.1 has D01 to D35 and S1 to S3 (38), 0.2 has D00 to D42 and S1 to S3 (46). D## = damage stage, S# = soiling stage. Damage is added step by step (`progressive_damage` = 1 on 71 rows: the EL damage is cumulative); the soot stages 0.2_D01 to D07 and all soiling stages have `progressive_damage` = 0 (the soot or sand was removed afterwards).
- **Images per stage.** One EL, one BN (near-IR black / white, same camera as EL, pixel-aligned with it) and one HDR (visible) image, file `<CellID>_<DamageID>_<EL|BN|HDR>_rt_cr.png` ("rectified and cropped"); the CSV column `EL_file_name` names the EL file of each row, so a stage maps to its images by name. Sizes 2,943 to 2,997 x 2,542 to 2,594 px (500 DPI, about 23 px per mm), EL and BN of a stage of equal size. Modes: EL 74 L + 10 RGBA (0.1_D06 to D09, D33 to D35, 0.2_D40 to D42; alpha 255 everywhere and R = G = B, so they are grey images in an RGBA container), BN likewise, HDR 74 RGB + 10 RGBA. EL images are dark: grey median 7 to 29, 99th percentile 55 to 111 on the four stages checked (0.1_D01, D20, 0.2_D00, D34).
- **Electrical series.** Per stage one operating point under a halogen lamp (irradiance estimated 50 W/m2, multimeter): `V_alo_light` [V], `A_alo_light` [mA], `P_alo_light` = V x I [mW], and `Power_output_loss [%] [V*I]` against the device's first stage. First stages: 0.1_D01 P = 209.72 mW, 0.2_D00 P = 186.111 mW (both loss 0, degradation "none"). There is **no I-V curve, no Pmpp, no Isc / Voc**. Also per stage: EL drive `V_EL`, `A_EL` (6.8 V, about 640 to 1,000 mA on most stages; 0 mA on 0.1_D33 to D35 and 3 mA on 0.2_D42, the "fatal" stages; 1,360 to 5,100 mA on the over-current stages 0.2_D35 to D41), degradation level (none ... Catastrophic), damage kind (mechanical, thermal, dirt, electric), visible type per image kind, cause, new-damage bounding box `[Xmin,Xmax,Ymin,Ymax]` in image px, free text.
- **Masks:** none. No pixel labels exist, so nothing here scores segmentation.

## 1. Rule (written 15 Nov 2026, 22:33 to 22:34 IST (file time), before any inference on this set; not changed after)

### 1.1 Deviation from the task wording, fixed now
The task asks for the relative loss of measured **maximum** power. The set has no maximum power. The only electrical output is P = V x I at one operating point under about 50 W/m2. I use it: **L = 100 x (1 - P / P_first)** per stage, P_first = P of the device's first stage (0.1_D01, 0.2_D00). L must equal the dataset's `Power_output_loss` column within 0.15 pp (its rounding); mismatches are listed. Every result below is "loss of V x I at one low-light operating point", not Pmpp loss. The lead may reject this substitution; then the item is blocked for want of an electrical quantity.

### 1.2 Analysis set (primary)
Stages with `progressive_damage` = 1 **and** `A_EL` >= 100 mA. Expected 67 stages: 0.1 D01 to D32 (32), 0.2 D00 and D08 to D41 (35). Reasons: `progressive_damage` = 0 marks soot and sand that were removed (optical shading, not damage; the authors' own flag for "EL damage usable cumulatively"); `A_EL` < 100 mA means the EL image was taken with almost no drive current (0.1_D33 to D35, 0.2_D42), so it does not show the device's state.

### 1.3 Image preparation (as our cells: one grey 512 x 512 image per cell, unit filling most of the frame, white padding outside)
- Grey exactly as `BenchmarkELDataset` reads our images: PIL `convert("L")`.
- Intensity: one fixed linear map per device, from its first stage (0.1_D01, 0.2_D00): lo, hi = 1st and 99th percentile of that image's grey px; every stage of the device: out = clip(round((x - lo) x 230 / (hi - lo)), 0, 255). (S: our cells' active area is about 150 to 230 grey; the raw EL here is 7 to 29; a per-stage stretch would hide global darkening, a per-device fixed map keeps it.)
- **P1 (primary): device as one cell.** The whole image resized with `cv2.INTER_AREA` so that its longer side (the width) is 512 px, height in proportion (about 440), centred vertically on a 512 x 512 canvas of value 255 (padding in our images is white). Device mask = the placed region. Scale about 3.9 px per mm (S: our 156 mm cells are about 1.6 to 1.9 px per mm; the device is 130 x 150 mm, close to one cell's size).
- **P2 (sensitivity): 2 x 2 tiles.** The image cut at its mid column and mid row into 4 tiles; each tile prepared like P1 (same intensity map; longer side 512, centred on a white canvas).
- Inference: the 20 PF models `w1g_pf_v11_f{0..4}_s{5..8}` (`el_bench/experiments/<run>/checkpoints/latest.pth`, step 20,000; no fold saw these images), the eval transform of the training config (resize no-op, normalise mean 0.5, sd 0.25 on /255), fp32 on CPU, softmax per model, **mean softmax over the 20 models**, pred = argmax (as the derived-dump ensemble). Per-model argmax maps are kept for the spread.

### 1.4 Severity outputs per stage (S1's code, `bench/post_eval.py` at bench_sev 637e2ce, unchanged)
`map_record(pred, keep = device mask)`: **a** = derived inactive region (class 11 plus enclosed crack px) in % of device px predicted non-padding; **crack** = crack skeleton px (512 canvas px); **s** = isolation score of the c_phys rule (isolated px / cell px; 0 when not evaluable). P2: a = 100 x sum nR / sum den over the 4 tiles, crack = sum of skeleton px, s = sum iso / sum cellpx.

### 1.5 Transfer gate (computed and judged BEFORE any correlation with power is computed)
- **TC1:** a stage is "seen as a cell" if at least 50% of its device px are predicted as a cell-surface class (background 0, gridline 15, the defect classes 10 to 20 and 23). TC1 passes if at least 90% of the 67 analysis stages are seen as a cell.
- **TC2:** on the two undamaged first stages (0.1_D01, 0.2_D00; the authors list snail trails / micro cracks there, loss 0), predicted a < 10% on both.
- **TC3 (S):** a contact sheet of both first stages and at least 6 other stages with the ensemble prediction overlaid; I write "usable" or "unusable, because ..." into section 2 before the power join is run.
- P1 passes the gate if TC1, TC2 and TC3 all pass. If P1 fails and P2 passes (same three checks), P2 is read instead of P1. If both fail: **"transfer too poor to tell"**; correlations are then printed as descriptive only.

### 1.6 Statistics and decision
- rho_pooled(x) = Spearman (average ranks) between x and L over the analysis stages of both devices; rho_within(x, device) the same per device.
- Interval: two-stage group bootstrap, 2,000 draws, `numpy.random.default_rng(0)`: draw 2 devices with replacement from {0.1, 0.2}, then within each drawn device draw its stages with replacement; pooled rho of a, s and crack on the same draw (paired). Draws where x or L is constant are dropped and counted. 95% interval = 2.5 / 97.5 percentiles; SE = sd of the draws; SE of a difference = sd of the paired draws of rho_x - rho_crack.
- **Pass (task rule):** for x in {a, s}: rho_pooled(x) >= 0.6, the lower 95% bound of rho_pooled(x) > 0, and rho_pooled(x) - rho_pooled(crack) > SE of that paired difference. **PASS if a or s passes.** Anything else: null.
- **What the outcomes mean.** PASS: on this staged-damage record the predicted quantity tracks the measured loss and does so better than crack length; it is a worked example on 2 devices at one low-light operating point, not a validation of power bands and not STC Pmpp. Null: the predicted quantity does not track measured loss on this record by this rule (rho values reported plainly). Gate failed: "transfer too poor to tell" (the model does not read these images well enough for the question to be asked).
- Known limits, fixed now (S): n = 2 independent devices; stages of one device are a dependent series and the bootstrap ignores that, so intervals are optimistic; with 2 devices the device stage of the bootstrap has only 3 distinct compositions; two candidates (a, s) give two chances to pass; S1 dropped s on our own data (D1 failed on predicted maps), so a pass on s alone carries that caveat.

### 1.7 Descriptive, decides nothing
- Stage-order baseline: rho between L and the stage number (D##) within and pooled (a predictor that only knows time).
- EL dark share (no model): share of raw grey px of the stage below 0.5 x the median grey of the device's first stage; its rho with L.
- The same statistics on all 84 stages, on the analysis set without the over-current stages 0.2_D35 to D41, and for the preparation not read (P2 or P1).
- Per stage the min and max of a over the 20 single models.
- **Scuff probe:** stages whose cause or any visible-type field contains "abrasion", "scratch" or "abraded" (case-insensitive). Per stage: ensemble crack skeleton px (P1) inside the new-damage box mapped to the canvas, at that stage and at the device's previous stage (DamageID order), and the difference; the authors' EL visible type beside it. New skeleton px in the box at a stage whose EL visible type names no crack are counted as "probable false crack px" (S: the box may hold real cracks the authors did not name). Box crops on a contact sheet.

## 2. Transfer gate (filled after inference, before the power join)
**P1, written 15 Nov 22:49 IST, before any correlation with power was computed** (preview of the gate step on P1 only; inference P1 done 22:47, 84 stages, 596 s, rc 0):
- TC1 (E): 67 of 67 analysis stages seen as a cell (share 1.00; lowest per-stage share of cell-surface px 0.61). Pass.
- TC2 (E): predicted a on the first stages 0.51% (0.1_D01) and 0.00% (0.2_D00), both < 10%. Pass.
- TC3 (S), contact sheet of 0.1_D01, 0.2_D00, 0.1_D11, D22, D32, 0.2_D18, D30, D41 (stages fixed by the thirds rule in `sev_polenghi_read.py`, not by power): **usable.** The model reads the device as a cell: strip gaps mostly as ribbons, the frame as border, the bright strips as background; the snail-trail networks of the undamaged stages are mostly left alone (a few short crack strokes); the new radial and diagonal cracks of the damaged stages are drawn as crack. Weakness seen before any power number: inactive is under-called. Several large dark regions (a whole dark strip at the right of 0.1_D11 and D22, the dark centre of 0.1_D32) get no inactive label; only some dark blobs at the device edge (0.2_D18, D30) and the over-current stage 0.2_D41 get large inactive areas. So a may track only part of the dark area. This is a weakness of transfer, not an unusable map.
- P1 passes the gate, so P1 is read (rule 1.5). P2 is computed and printed as descriptive.

**P2 and the full gate step, written 15 Nov 23:24 IST, after `power.json` existed (mtime 23:23:17); P2 is descriptive and decides nothing** [wording fixed 16 Nov, review F2.1] (P2 inference done 23:21, 336 tiles, 2,038 s, rc 0; gate step `bench_reads/severity/S2/gate.json`, `per_stage_gate.tsv`, sheets `gate_sheet_P1.png`, `gate_sheet_P2.png`): the full step repeats the P1 preview exactly (TC1 1.00, TC2 0.512 / 0.000). P2: TC1 67 of 67 (1.00), TC2 0.37% / 0.004%, TC3 (S) usable: at about 2x the scale the model draws more of the radial cracks and labels more of the dark regions as inactive (the dark right strip of 0.1_D11, edge blobs of 0.1_D32), still missing the dark centre of 0.1_D32; tile borders cut some regions. Decision under 1.5 unchanged: **P1 is read.**

## 3. Numbers (E)
Tools: bench_sev f1eb157 (prep, inference), 5c1534e (`scripts/sev_polenghi_read.py`, md5 90062448, the same file that ran both steps), tests c4a85c7 (13 pass; with S1's 17, 30 pass). Inference 22:37 to 23:21 in tmux `bench_sev_s2` (`bench_reads/severity/S2/run_s2.sh`, log `run_s2.log`), 8 workers, CPU, fp32, 20 models x (84 + 336) images. Outputs in `bench_reads/severity/S2/`: `gate.json` (md5 3789aacc), `power.json` (af3adaf2), `per_stage_power.tsv` (e1ef2113; every stage with L, a, s, crack for P1 and P2, model min / max), `per_stage_gate.tsv` (ca112b28), `scatter_primary.png` (e40ee71e).

**Checks.** Recomputed L equals the dataset's loss column on all 84 stages (0 mismatches over 0.15 pp). Analysis set = 67 stages (32 + 35) as expected. No bootstrap draw dropped. Data note found while reading: the EL images of **0.2_D27 and 0.2_D28 are pixel-identical** (different PNG files, same grey array) while their losses are 23.7% and 40.5%; both stay in the set (rule 1.2 has no clause for it), so one pair of points has the same predictor value and two losses. No other EL pair is identical.

### 3.1 Primary (P1, 67 stages; rho = Spearman with L; interval = two-stage bootstrap, 2,000 draws)
| Predictor | rho pooled [95%] | SE | within 0.1 (32) | within 0.2 (35) | rho - rho(crack) [95%], SE | rho >= 0.6 | low > 0 | beats crack by > SE | pass |
|---|---|---|---|---|---|---|---|---|---|
| (a) inactive area a | **0.557 [0.152, 0.795]** | 0.167 | 0.306 | 0.715 | -0.090 [-0.758, +0.301], 0.307 | no | yes | no | **no** |
| (b) isolation score s | **-0.253 [-0.571, +0.111]** | 0.178 | -0.450 | -0.053 | -0.900 [-1.484, -0.377], 0.304 | no | no | no | **no** |
| crack skeleton px (comparison) | 0.647 [0.355, 0.941] | 0.166 | 0.913 | 0.510 | | | | | |
| stage number (descriptive) | 0.910 | | 0.949 | 0.956 | | | | | |
| EL dark share, no model (descriptive) | 0.848 | | 0.919 | 0.841 | | | | | |

### 3.2 Descriptive blocks (decide nothing)
| Block | n | rho a [95%] | rho s | rho crack [95%] |
|---|---|---|---|---|
| P2 tiles, same 67 stages | 67 | 0.609 [0.376, 0.776] (within 0.525 / 0.672) | -0.351 | 0.684 [0.449, 0.931] (within 0.901 / 0.584) |
| P1, all 84 stages | 84 | 0.466 [-0.197, 0.784] (within -0.028 / 0.719) | -0.118 | 0.516 [0.260, 0.738] |
| P1, without the over-current stages 0.2_D35 to D41 | 60 | 0.494 [0.155, 0.879] (within 0.306 / 0.838) | -0.131 | 0.835 [0.683, 0.941] |
EL dark share on all 84 stages: 0.892. P2 would not pass either: rho 0.609 >= 0.6 and low bound > 0, but it is below crack length (difference -0.075, SE 0.188).

### 3.3 What the values look like (from `per_stage_power.tsv`)
- Predicted a is small: P1 0 to 9.2% of the device; device 0.1 stays under 1% on 28 of its 32 analysis stages although its loss reaches 40 to 55% (the dark strips that I flagged in section 2 are not called inactive). Device 0.2: a = 0 on D00 to D14 (loss up to 16%), 2.3 to 5.5% on D18 to D40 except D33 (loss 20 to 57%), 9.2% at D33 (55%) and 8.7% at D41 (100%). So on 0.2 a rises in steps with the loss; on 0.1 it does not.
- The 20 single models disagree widely on a: e.g. 0.2_D41 2.7 to 22.1%, 0.1_D27 1.7 to 7.1%, 0.2_D33 1.5 to 14.1% (min to max over models).
- The isolation score fires mostly on the early stages of 0.1 (s 0.017 to 0.037 on D01 to D05, loss 0 to 14%) and is 0 or near 0 on most heavily damaged stages: the c_phys rule here reacts to the predicted ribbons on the strip gaps, not to the damage. Its negative rho is an artefact of that, not a physical signal (S).
- Crack length grows with the cumulative damage on device 0.1 (127 px at D01 to 2,000 to 2,700 px at D25 to D32), hence its within-0.1 rho of 0.91; on 0.2 it falls again on the over-current stages (EL driven at 1.4 to 5.1 A, saturated images), which lowers its pooled rho.

## 4. Outcome
- **Gate: passed** (P1 and P2; section 2). The model reads these images as cells; the result is not "transfer too poor to tell".
- **Primary: NULL.** Neither predicted inactive area (rho 0.557 [0.152, 0.795]) nor isolation score (rho -0.253) meets the rule. Inactive area misses rho >= 0.6 narrowly and does not beat crack length (difference -0.09, SE 0.31); isolation score is unrelated or negative. Plainly: on this staged-damage record, predicted inactive area does not track the measured loss better than predicted crack length, and the isolation score does not track it at all.
- **Reading (S).** The record cannot separate damage measures. The damage only accumulates, so anything that grows with it tracks the loss: stage number alone gives rho 0.91 and a model-free count of dark EL pixels 0.85, both above every model output. A real test of "power follows inactive area, not crack length" needs units where cracks and inactive area vary independently (many cells or modules, as in ELPVPower), not one damage series per device. Two transfer weaknesses also blunt a: the model calls few of the dark strips inactive (device 0.1), and the 20 models disagree several-fold on a. The literature claim (P263, R) is neither supported nor contradicted here. Three caveats: n = 2 devices, the loss is V x I at one ~50 W/m2 operating point and not Pmpp, and two stages share one image.
- For WattCycle: this set gives no support for turning predicted inactive area into a power band. S1's reading stands: inactive fraction per cell is the descriptive output, with no validated link to power.

## 5. Scuff probe (descriptive; P1 ensemble; `bench_reads/severity/S2/scuff_sheet.png`, md5 b58f6efd, crops of the new-damage box, previous stage | this stage, image | prediction)
The rule's word match (cause or any of the HDR / BN / EL visible-type fields contains abrasion, scratch or abraded) picked 33 stages. Most were picked by the HDR or BN field only (for example dents and hammer hits that also scratch the surface). The 8 stages whose cause or EL type names abrasion, scratch or cut are the probe proper:
| Stage | Authors' EL visible type / cause | crack skeleton px in box, previous -> now | new | EL names a crack |
|---|---|---|---|---|
| 0.1_D06 | abrasion / knife side slide | 0 -> 57 | **+57** | no |
| 0.1_D14 | heavy coating abrasion; cut / knife repeated slide | 0 -> 97 | **+97** | no |
| 0.1_D17 | heavy coating abrasion; cut / knife repeated slide | 0 -> 9 | +9 | no |
| 0.1_D26 | abrasion; coating removal / knife transversal deep cut | 2 -> 73 | **+71** | no |
| 0.2_D15 | cut / deep knife scratch | 0 -> 10 | +10 | no |
| 0.2_D25 | light multiple cuts / knife scratches | 0 -> 0 | 0 | no |
| 0.2_D26 | superficial scratch / knife scratch | 0 -> 0 | 0 | no |
| 0.2_D27 | light scratch / superficial fire | 0 -> 0 | 0 | no |
- 5 of these 8 stages gain new predicted crack inside the box; 4 of the 5 are the knife abrasions and cuts of device 0.1 (+57, +97, +9, +71 skeleton px; box areas 3,300 to 4,100 canvas px). The crops show why: the knife leaves sharp dark straight lines in the EL, and the model draws them as crack. The light scratches of 0.2 (D25 to D27) get none. Under the rule, these new px count as "probable false crack px" because the authors' EL description names no crack. S: some knife cuts may well break the silicon beneath; without masks this cannot be settled.
- Across all 33 matched stages: the stages with new crack px where the EL type names no crack are 0.1_D05 (+2), D06, D14, D17, D26, 0.2_D15 and D20 (+9).
- This is the same failure as on our unseen-module set: straight dark surface lines read as crack. It is a public example of it, small and not a rate.

## 6. Owed
- Lead: accept or reject the electrical substitution of rule 1.1 (V x I at one low-light operating point instead of maximum power). If rejected, the item is blocked: the set holds no other electrical quantity.
- The test this set cannot give (inactive area against crack length on independent units with measured Pmpp) is T12 item 8 on ELPVPower (S3): its gates (b) cell cutting and (c) BMRK overlap are still open, and its licence version is unverified.
- Data note for any later user of the set: the EL images of 0.2_D27 and 0.2_D28 are pixel-identical while their losses differ (23.7 / 40.5%). Worth reporting to the authors.
- Deliverables: contact sheets `bench_reads/severity/S2/gate_sheet_P1.png` (8 stages, image over prediction; crack red, derived inactive blue, ribbons green, busbars yellow), `gate_sheet_P2.png`, `scuff_sheet.png`, `scatter_primary.png`. External images stay outside the project tree (rule of the track), so none are copied in.
- Not done: no thermal or BN / HDR image used; no cell-level split of the 10 strips (the device is the unit, per rule 1.3).
