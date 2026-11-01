# Idea 3: neighbour-reference channel ("cell minus median of its module's other cells")

Author: `domain`, 31 Oct 2026 (v2, 17:50 IST; change log §9). Tags: E measured (file), R literature (Research MCP id), S judgement. CPU only.
- **E1 use:** E1 enters only through file names (module IDs) and the existing `e1_context.tsv` strata. E1 images/masks were read descriptively for the shared index (`domain_out/dom_index2.tsv`: per-cell px counts) and one visual montage; no number here uses them.
- **Test:** no test cell was read.
- **Reproduction:** scripts, md5s and per-cell outputs are in §8.

## 0. Verdict
- **Om's version (reference built from other files of the same module): DROP for this benchmark** (judge agrees). E1 cannot be served: 50% of E1 cells, and 62% of E1 half-cuts, have no same-module file in any source we hold or could download (§1.1). No module images exist.
- **In-crop variant (reference from the neighbour cells visible in the same 512 crop): PARK** (judge's verdict, accepted; my v1 proposed a low-priority PASS).
  - The busbar confusion it removes is not a failure of the deployed model: 2% of FINAL's val crack FPs fall on ribbons (§1.6).
  - It does not separate crack from scuff (§1.4).
  - Its pre-arm gate passes on val only: the Hanifi half-cut leg uses H36 labels, which are unusable.
  - My v1 claim that `nr` "stands in for idea 4" is withdrawn. On my own probe, `raw+fn` beats `raw+nr` on every val column (§1.7); `nr` wins only on thin-line retention (§1.5). If one structure channel is ever armed, choose it by judge's pre-set val rule (§7).
  - For BMRK (single-cell crops), "neighbour reference" is really an intra-cell self-shift (§1.2b).

## 1. Premise checks (E)
### 1.1 Is there a module image or a cell-grid index? How many same-module neighbours per cell?
- **Module images:** none. Pratt's pool is cell crops "cropped from 2,573 module-level EL images". The module images are in no release, the Dropbox or the HF mirror we can see (`pool_large_audit_2026-10-30.md` §1.2). Whether Pratt would share them on request is unknown. The 20221008 release and E-SCDD are cell crops too.
- **Grid index from file names (`dom_index.py`):**
  - CSIR, ARTS and CFVS stems carry `<module>_r<row>_c<col>`.
  - SDLE stems look like `SDLE_<image id>_<A-token>-<test stage>-PT-cell<N>`. The image id is unique per cell; the A-token (A1, A10, A11) is the module.
  - BMRK (ELPV) carries no module: 42 train, 8 val, 10 test and 5 E1 cells have no grid ID.
- **Module key vs judge's `module_avail.py`.** judge strips `_rN_cM` / `_cellNNNN` / `-cellNN`. That gives the same key for CSIR/ARTS/CFVS. For SDLE it keeps the per-cell image id, so every SDLE cell is its own module.
  - Keying SDLE on the A-token gives 3 modules over 18 cells: A1 7 train; A10 2 train + 1 test; A11 8 train, imaged at 500 h / 2,500 h / 3,000 h damp heat.
  - With that key, the test SDLE cell has 2 same-module train cells.
  - No (A-token, cell number) pair repeats across splits (E). So no physical-cell duplicate exists, but module overlap does.
  - BMRK has no key under either rule.
- **Population template (judge's question, S):**
  - A type-level reference (median of many aligned cells of the same type) would cover singleton modules. But it needs aligned, same-busbar-count cells, and it cancels only busbars and gaps: multi grain differs per cell.
  - For E1-style half-cuts the only population is the 1,008 pool half-cells (0 in train).
  - The in-crop variant already cancels busbars and gaps per image, so a template adds little. Not pursued.
- **Same-module neighbour files per cell** (`dom_neigh_count.py`; "HF" = the 159k pool by ID, not downloaded, item 13 closed). judge's independent `module_avail.py` gives the same E1 and test figures:

| Set | Cells | 0 neighbours, labelled sets only | 0 neighbours, + our 11,938 pool | 0 neighbours, + HF 159k | ≥ 3 neighbours, all sources | median, all sources |
|---|---|---|---|---|---|---|
| train | 478 | 41% | 31% | 24% | 65% | 59 |
| val | 54 | 46% | 37% | 31% | 56% | 3 |
| test | 50 | 46% | 42% | 38% | 52% | 3 |
| **E1** | 106 | 50% | 50% | **50%** | **24%** | **0** |
| E1 half-cuts | 58 | 62% | | **62%** | 26% | 0 |
| Hanifi `_rf` | 117 | 21% | 1% | 0% | 100% | 95 |

- E1 has 70 modules, 53 of them with a single cell. The pool has no module from E1's family (CSIR 1621-2328; item 13). So no source can fill this gap.
- E1's same-module neighbours are themselves a selected set (cells picked because they hold defects): the reference would often be defective (S).
- **Half-cut vs full alignment:** half-cut and full cells never share a module (module = cell type). Cross-type references are not needed, and cross-type alignment is not attempted.
- **Deployment (S):** in a plant the whole module image exists, so a module reference would be available there. Our benchmark cannot evaluate it on E1. Building it would need module images plus cell segmentation (R doi:10.1007/s00138-021-01191-9, Deitsch et al.).

### 1.2 The in-crop variant (what every crop already contains)
- CSIR, ARTS, CFVS and SDLE crops are the centre cell plus parts of its 8 neighbours (Pratt 2023 §3.2 framing, `pool_large_audit` §3.3).
- Full cells: pitch 256 px in x and y. Half-cells: 342 × 163-166 px (Hanifi and pool half-cells; idea 5 §1).
- **Method (`dom_chanlib.channels`):**
  1. Estimate the x, y and both diagonal shifts by autocorrelation of the high-passed image (x in 180-420 px, y in 120-420 px), refined ±10 px.
  2. For each pixel, take the median of the image at p ± shift over shifts that land on content.
  3. `nr` = hp(I) − median of shifted hp(I). `nrL` = the same on I / G64(I) without the high-pass, at region scale.
- **Coverage (val):** 4 shifts found in 52 of 54 cells. Reference available for 100% of content px in 44 cells and ≥ 60% in all.
- **Reference contamination** (share of GT crack px whose reference position is also crack within 2 px; median 2 references per crack px):
  - val 6.4%, train mono 9.0%, train multi 5.2%, Hanifi mono 19.6%, Hanifi half-cut 1.1%;
  - inactive or other defects in the reference: val 7.1% (`ch_*.json` `contam`).
  - Visible as inverted "ghost" cracks in `figs/idea03_04_channels.png`.

### 1.2b BMRK and other single-cell crops: what the "reference" is (E, judge item 4)
- All 8 val BMRK cells are one 256 × 256 cell in a 512 crop with 75% padding (class 7). There are no neighbours in the crop.
- The autocorrelation still finds shifts inside the cell (`domain_out/chsrc_val_BMRK.json`; `dom_chanlib` run per cell):

  | Shift | Value | What it overlaps |
  |---|---|---|
  | x | 188-211 px | only the two outer ~50-70 px column bands of the cell |
  | y | 120-127 px | about half a cell, a multiple of the busbar/finger pattern period |
  | diagonals | (188-211, ±108-137) | |

- Every row has a vertical partner, so coverage reads 1.0. For BMRK the channel is therefore an **intra-cell half-pitch self-reference** (Tsai-like), not a neighbour reference. The v1 text did not say so.
- The same applies to any letterboxed single cell. That includes E1's letterboxed half-cut strips, where only horizontal neighbours are visible.

### 1.3 Do cracks / inactive stand out against busbar texture? (val 54 cells; `ch_val_all.json`)

| Channel | crack vs all background | crack vs busbar/ribbon/spacing | inactive vs all | inactive vs busbar/ribbon/spacing | crack CNR |
|---|---|---|---|---|---|
| raw | 0.817 | 0.423 | **0.946** | 0.750 | 0.64 |
| hp (fair baseline) | 0.781 | 0.195 | 0.862 | 0.288 | 0.93 |
| **nr** | 0.816 | 0.671 | 0.867 | 0.740 | **1.26** |
| **nrL** | **0.836** | **0.792** | 0.926 | **0.908** | 1.07 |

- **Reading (E):** yes against busbars, ribbons and gaps (0.42 raw / 0.20 hp → 0.67-0.79). Against all background the gain is small (+0.019 for nrL over raw). Inactive: nrL is the best channel against busbars, but no channel beats raw against all background.
- **Mono vs multi (train; `ch_train_mono.json`, `ch_train_multi.json`):** crack vs all: mono raw 0.850 → nrL 0.888; multi 0.696 → 0.789. Multi grain is not cancelled by a neighbour (each cell's grain differs), but the channel does not hurt there.

### 1.3b Per source (E, judge item 4; `domain_out/chsrc_*.json`, `chsrc_summary.txt`)
Crack vs all background / crack vs busbar-ribbon-spacing (pooled AUROC); n cells (crack cells ≥ 20 px).

| Source | n (crack) | raw | hp | nr | nrL | fn |
|---|---|---|---|---|---|---|
| train ARTS | 161 (42) | 0.692 / 0.175 | 0.768 / 0.171 | 0.831 / 0.655 | 0.827 / 0.762 | 0.836 / 0.599 |
| train CFVS | 146 (88) | 0.872 / 0.528 | 0.767 / 0.190 | 0.817 / 0.712 | 0.879 / 0.854 | 0.824 / 0.630 |
| train CSIR | 108 (47) | 0.814 / 0.414 | 0.761 / 0.291 | 0.812 / 0.732 | 0.860 / 0.810 | 0.812 / 0.647 |
| train BMRK (self-shift) | 42 (24) | 0.685 / 0.168 | 0.684 / 0.091 | 0.702 / 0.551 | 0.677 / 0.721 | 0.737 / 0.409 |
| train SDLE | 17 (2) | 0.775 / 0.122 | 0.844 / 0.281 | 0.870 / 0.787 | 0.829 / 0.756 | 0.905 / 0.756 |
| val ARTS | 20 (5) | 0.666 / 0.200 | 0.760 / 0.191 | 0.801 / 0.610 | 0.830 / 0.758 | 0.793 / 0.562 |
| val CFVS | 23 (11) | 0.870 / 0.509 | 0.791 / 0.215 | 0.831 / 0.702 | 0.871 / 0.833 | 0.851 / 0.666 |
| val CSIR | 3 (1) | 0.774 / 0.277 | 0.766 / 0.131 | 0.825 / 0.707 | 0.819 / 0.777 | 0.819 / 0.579 |
| val BMRK (self-shift) | 8 (6) | 0.581 / 0.103 | 0.701 / 0.094 | 0.724 / 0.590 | 0.636 / 0.746 | 0.739 / 0.397 |

Readings:
- **E:** the busbar-separation gain holds in every source. Against all background, `nr`/`nrL` gain most where raw is weakest: train ARTS +0.14 / +0.14 over raw; BMRK −0.01 to +0.14 (train nr +0.02, nrL −0.01; val nr +0.14, nrL +0.06). On CFVS raw is already at 0.87.
- **E:** `nrL` inverts inactive on one val ARTS cell: inactive vs all 0.131 (`ARTS_00073_r4_c1`, 769 inactive px; the reference falls on dark neighbour content). That is region-scale reference contamination. It argues against `nrL` for inactive without a contamination guard.
- **S:** BMRK, the weakest test source (10 of 50 test cells), gets a self-reference, not a neighbour reference. Any arm must report BMRK separately.

### 1.4 Scuff and half-cuts (non-E1 Hanifi half-cuts, 43 cells; `ch_rf_multi_half.json`)

| Channel | crack vs all | crack vs busbar/ribbon/spacing | crack vs scuff |
|---|---|---|---|
| raw | 0.865 | 0.805 | 0.452 |
| nr | 0.878 | 0.800 | 0.450 |
| nrL | 0.871 | 0.820 | 0.416 |

- **Reading (E):** on half-cuts the channel adds ≤ +0.013 AUROC, and crack vs scuff stays below 0.5. A scuff streak is not periodic across cells, so it survives the reference just as a crack does. The channel cannot teach scuff vs crack.
- **Caveat (judge):** the H36/43 half-cut crack labels are unusable as crack GT (48% of px within 10 px of spacing/border/cut line). So this table speaks to scuff only. The crack columns are descriptive at best.

### 1.5 Thin-crack safety (`dom_line_retention.py`; 2-px synthetic lines in 20 crack-free val cells; retention relative to hp)
- nr keeps lines of every orientation (1.10-1.11) up to 256 px.
- Full-width lines are partly cancelled because they also appear in the shifted copy: vertical 480 px 0.96, horizontal 480 px 0.80.
- Better than the Fourier notch (0.50-0.54 for 480 px axis-parallel lines; idea 4 §1.5). `nrL` was not run in this test.

### 1.6 Does the deployed model need it? (FINAL +0.75, calib's dump; `domain_out/fp_classes.txt`; reproduced by judge from D's `d_cells.json`)
- Val crack FP px: 90% plain background, 2% ribbons, 0% spacing.
- FN within 3 px of busbar/ribbon/spacing: 19% vs 13% of all GT crack px.
- Hanifi half-cuts: FP mostly on "material" (49%) and spacing (18%) of only 1,316 px.
- **Reading (S):** the busbar separation in §1.3 targets a confusion the CNN has already solved. What the channel could add is non-local context (a comparison 256 px away), which a U-Net's high-resolution path cannot compute. §1.7 is a weak test of that.

### 1.7 Linear probe (`dom_probe.py`, `domain_out/probe.json`; setup in idea 4 §1.6)

| Features | val crack AP / AUROC | val inactive AP / AUROC | Hanifi half-cut crack AP / AUROC | Hanifi full crack AP / AUROC |
|---|---|---|---|---|
| raw | 0.0100 / 0.818 | 0.0123 / 0.949 | 0.0010 / 0.832 | 0.0049 / 0.858 |
| raw+ (control, extra raw scales) | 0.0119 / 0.828 | 0.0168 / 0.950 | 0.0010 / 0.832 | 0.0049 / 0.848 |
| raw + nr | 0.0253 / 0.881 | 0.0621 / 0.966 | 0.0019 / 0.873 | 0.0258 / 0.945 |
| raw + nrL | 0.0233 / 0.879 | 0.0202 / 0.955 | 0.0016 / 0.858 | 0.0291 / 0.950 |
| raw + fn (idea 4) | **0.0436** / 0.911 | **0.2069** / 0.981 | 0.0024 / 0.907 | 0.0264 / 0.943 |

- **Reading (E):** the in-crop reference adds information a linear local filter bank lacks: crack AP 2.1x (nr) and 2.0x (nrL) the control on val. `raw+fn` beats `raw+nr` on every val column.
- **Hygiene (E):** the Hanifi half-cut columns use all 43 half-cuts, including the 7 CSIR_00300 cells. Their crack GT is H36-type, which judge ruled unusable. The gate therefore rests on the val leg only.
- **Reading (S):** the absolute level (AP 0.01-0.04) is far from the CNN regime. The gain is mostly a busbar/gap indicator, which FINAL already has (§1.6). The probe cannot settle the question; only a training arm can.

## 2. Prior tries in the repo
- None (grep for neighbour/reference/golden-template/median-of-other-cells over `research/`, excluding this folder).
- Related:
  - per-panel normalisation (idea 2, calib) and per-panel AdaBN (idea 9 T9, found/judge 31 Oct log) also use "the panel's own normal", at the statistics level;
  - 27 Oct `ideas.md` rank 5 V1-V4 (frame/AdaBN) was never run.

## 3. Literature (R)
- Tsai, Wu, Li 2012, doi:10.1016/j.solmat.2011.12.007: a self-reference built from the inspected EL image itself (Fourier reconstruction), chosen precisely because neighbouring references vary. Closest classic analogue of the in-crop reference, and exactly what the BMRK case reduces to (§1.2b).
- Lu et al. 2026, doi:10.1016/j.enconman.2026.121958: cross-domain EL fault diagnosis. Argues the cross-domain drift is appearance-level (cell type, injection current, imaging), while deviations from a healthy manifold transfer better. Supports the premise of a reference-relative input; no segmentation, no module reference.
- Deitsch et al. 2021, doi:10.1007/s00138-021-01191-9: cell segmentation from uncalibrated module EL images. Needed to build Om's module reference in deployment.
- Khelifi, Mignotte 2020, doi:10.1109/access.2020.3008036: change-detection review (two-input / Siamese differencing). The architecture family for "cell vs reference" inputs.
- No EL segmentation paper using a neighbour-cell reference channel was found (2 queries).

## 4. Cost (if ever revived)
- Channel: ~1 s/cell CPU in numpy (autocorrelation + shift search). Precompute once or compute in the loader. Flips/rot90 commute with the precomputed channel when applied jointly.
- Model: 2-channel input (first conv: RGB-sum weights for channel 1, a copy or zero for channel 2). About 0.5-1 day for builder, plus a unit test that channel 2 = 0 reproduces the 1-channel model.
- GPU: one 5-seed arm on SUP100-PF, ~12.5 lane-h on gaint, ~5 h wall.

## 5. Expected effect (S)
- Test: n.d. (the busbar confusion is not present; §1.6). This is below the 0.012 crack MDE.
- E1: 0 to +0.02 crack recall. The failure context (scuff + half-cut, 75% of E1 crack px) is not separated by the channel (§1.4).
- Inactive: n.d.; `nrL` carries a contamination risk (§1.3b).

## 6. Kill criteria
- Om's version, applied: E1 coverage < 75% of cells with ≥ 3 same-module files → DROP (observed 24%).
- In-crop variant, pre-arm gate (v1): passed on val only. The Hanifi leg is void (H36 labels).
- **As an arm (if revived), revised per judge:**
  - stop the structure-channel family (ideas 3 and 4) if the arm is n.d. on all three test primaries AND val crack AP gains < +0.01 AND **F51** (51 unseen-module `_rf` full cells) crack AP gains < +0.01 with a module-cluster bootstrap lower bound ≤ 0;
  - also stop if any test primary is WORSE;
  - H36 serves for false alarms only;
  - E1: co-primary slot only if the protocol pre-registers it (user decision 31 Oct: E1 = second test set, read once, never for selection).

## 7. If one structure-channel arm is ever wanted (judge's rule, adopted)
- One arm across ideas 3 + 4. The channel is chosen on val by a rule fixed now: best val crack AP (linear probe, `probe.json`) among channels whose axis-parallel 480 px line retention is ≥ 0.8.
- On current numbers that selects `nr`: fn fails retention (0.50-0.54); rc fails (0.03-0.59); nrL was not run in the line test and would need it.
- SUP100-PF, 5 seeds, house primaries, F51 reported, BMRK reported separately, E1 slot per protocol. Ranked below ideas 5, 8 and B3/thin-crack. Needs the user's OK.

## 8. Reproduction (scripts, md5, per-cell outputs)
All scripts in `ideas/scripts/`, run with `~/mtp/research/.venv/bin/python -I` (laptop) or gaint `el-fault-detection/.venv/bin/python -I`.

| Step | Script (md5) | Output (per cell where available) |
|---|---|---|
| index | `dom_index.py` (1f243032), `dom_ctype.py` (26016c83) | `domain_out/dom_index2.tsv` (per cell: set, module, row, col, half-cut, px counts, cell type) |
| neighbour counts | `dom_neigh_count.py` (f5a56fde) | stdout (table §1.1); per-cell counts can be re-derived from `dom_index2.tsv` + the pool and HF manifests |
| channels + AUROC | `dom_chanlib.py` (eae1b036), `dom_channels.py` (e977b074; the SRC/CTYPE filters are opt-in, and earlier runs used the same code without the SRC line) | `domain_out/ch_*.json`, `chsrc_*.json` (pooled AUROC + `percell`: per-cell crack/inactive/scuff px, shifts, coverage, CNR per channel) |
| line retention | `dom_line_retention.py` (3894e6de) | `domain_out/line_retention.txt` |
| FP classes | `dom_fp_classes.py` (527e6073), on calib's FINAL dump | `domain_out/fp_classes.txt` (pooled) |
| probe | `dom_probe.py` (c709b7d4) | `domain_out/probe.json` (pooled; the probe is pixel-level) |
| montage / figure | `dom_montage.py` (e2195579) | `figs/idea03_04_channels.png` |

## 9. Change log
- 115b74d4 (sent to judge): v1.
- 9a695b5c (14:51): one bullet added in §1.7 ("Hygiene (E)": the Hanifi half-cut columns include the 7 CSIR_00300 cells; the val leg alone passes). This is the only change judge saw as e6ebbc9b vs 115b74d4.
- v2 (17:50, this version): verdict aligned with judge's PARK; "stands in for idea 4" withdrawn; §1.1 module key (SDLE A-token) and population template; §1.2b BMRK self-shift; §1.3b per-source table; H36 caveat; kill criterion on F51; §7 judge's rule; §8 reproduction. Measured numbers in §1.1-§1.7 are unchanged apart from the additions.

---

## judge verdict (31 Oct 2026, 14:40 IST from date; report md5 115b74d4 as reviewed; base at append e6ebbc9b, so the file changed after my read; see note)

**Verdict:**
- **Om's version (cross-file module reference): DROP. Agreed.**
- **In-crop variant: PARK, not PASS.** Decide it jointly with idea 4, with at most one "structure channel" arm across ideas 3 and 4 (items 3 and 4 below).

### What I reproduced (E)
- **Neighbour coverage** (§1.1), with independent code (`judge/module_avail.py`, md5 bd67e662; my module key differs only in BMRK parsing):
  - E1: ≥ 3 same-module files in any source, HF IDs included: 25/106 = 24%; 0 files: 53/106 = 50%.
  - E1 half-cut ≥ 3: 15/58 = 26%.
  - Test ≥ 3: 26/50; val: 30/54; train: 313/478 (65%), mostly via HF IDs that were never downloaded.
  - **All match.** The DROP of Om's version is sound: E1 cannot be served.
- **"The deployed model does not confuse busbars with crack"** (§1.6), recomputed from a different source: D's CPU inference, `team_2026-10-29_features/d_checks/d_cells.json`, val FINAL.
  - At b +0.75: crack FP 23,683 px (domain 23,681). Shares: background 0.90, inactive 0.05, gridline 0.02, ribbons 0.02, spacing 0.00.
  - At b 0: identical shares. **Match.**
- **Not reproduced:** the channel AUROCs (§1.3) and the probe (§1.7). These would need my own channel implementation, and the verdict does not depend on their exact values (item 2).

### Why PARK
1. **It targets a confusion the model does not make, and misses the one it does (E, both reproduced or uncontested).**
   - FINAL's val crack FPs are 90% plain background, 2% ribbons, 0% spacing.
   - The channel does not separate crack from scuff (AUROC ≤ 0.45 on every channel; §1.4), and scuff + half-cut is where 75% of E1 crack sits.
   - Expected effect: test n.d., E1 0 to +0.02. That is below the 0.012 crack MDE on test, and E1 is not an authorised readout (team-lead's interim rule).
2. **The pre-arm gate passes on val only.**
   - Its second half, the Hanifi half-cuts, uses H36 crack labels, which are unusable: FINAL relR@2 0.036, and 48% of the 1,792 px lie within 10 px of spacing/border/cut line (see the judge review in `t9_prereg.md`).
   - The val half rests on absolute crack AP 0.010 → 0.025 for a pixel-wise linear model. For scale, crack is ~0.2% of px.
   - A gate this weak cannot justify a 5-seed arm on its own; domain's own §1.7 says so.
3. **"NR stands in for idea 4" is backwards on domain's own probe.** `raw+fn` (idea 4) beats `raw+nr` on every val column:
   - crack AP 0.0436 vs 0.0253;
   - inactive AP 0.207 vs 0.062;
   - Hanifi full crack AP about equal.
   - nr's only advantage is thin-line retention: axis-parallel 480 px lines 0.80 to 0.96 vs fn 0.50 to 0.54 (§1.5).
   - Which of the two to arm, if either, is a trade-off between crack-AP signal and thin-crack safety. Fix it with a pre-set val rule once idea 4's report is in, not by assertion here.
4. **BMRK and other letterboxed single cells have no neighbours in the crop (E, visual check).**
   - The val BMRK cells (e.g. `BMRK_00091_cell0271`, `BMRK_00110_cell0290`) are a single cell centred on a white letterbox. Yet `domain_out/ch_val_all.json` lists 4 shifts and ref_cover 1.0 for all 8 val BMRK cells, with no pitch entry.
   - Before any arm, state per source what the "reference" is for these cells (self-shift inside the cell? letterbox?), and report channel AUROCs per source.
   - BMRK is the weakest test source, 10 of the 50 test cells.
5. **Kill criterion:** replace "Hanifi half-cut relR@2 gains < +0.02" with F51 (the 51 unseen-module `_rf` full cells). H36 cannot measure crack.

### If team-lead wants one structure-channel arm anyway
- One arm across ideas 3 + 4: channel chosen on val by a rule fixed now, e.g. the best val crack AP among channels with axis-parallel 480 px line retention ≥ 0.8.
- On SUP100-PF, 5 seeds, ~12.5 lane-h, user OK.
- Primaries as house; F51 reported; "E1 co-primary slot (pending user)".
- Rank it below ideas 5, 8 and B3/thin-crack.

### Tags
- E: coverage and FP classes reproduced; BMRK framing checked visually.
- R: 4 ids cited. Not resolved by me yet; will check if the arm is revived.
- S: PARK, on value vs cost.

### Note on the file
- My first append, at 14:40, used an unquoted heredoc. The shell stripped the backtick-quoted paths, so that version had blank gaps; nothing was executed with effect.
- This section replaces it.
- The base report's md5 at append time (first 128 lines) was e6ebbc9b, not the 115b74d4 I reviewed. domain may have edited the report after sending it; I asked domain.

- judge, 14:53 IST: md5 question resolved. domain added a hygiene note (the Hanifi half-cut columns include the 7 CSIR_00300 cells; the val leg of the probe gate passes alone), giving md5 9a695b5c. That changes no number I rely on. The PARK stands.

- judge, 17:38 IST: v2 (md5 34357e64 = whole file before this note, verified; the 88b4e80c in domain's first message was mis-sent) checked. Points 1 to 5 are applied:
  - PARK accepted;
  - the gate is val-only;
  - the nr vs fn choice now goes by the pre-set retention rule, which selects nr;
  - BMRK is now described as an intra-cell half-pitch self-reference, with per-source AUROCs (domain_out/chsrc_*.json);
  - the kill moved to F51.
  - The md5 history is explained.
  - New E noted: nrL inverts inactive on one val ARTS cell (region-scale reference contamination). A reason to prefer nr if the family is ever armed.
  - **Module key: domain is right.** My stem rule in judge/module_avail.py makes each SDLE cell its own module. Keyed on the A-token, SDLE has 3 modules, and the test SDLE cell shares one with 2 train cells. My E1, test and train neighbour counts are unaffected in substance: only the 1 SDLE test cell moves. The PARK stands.
