# Data decision for the ALHVR and SKCDF tracks (21 Oct 2026)

Authors: agent 4 (SKCDF critic) and agent 2 (ALHVR critic). Status: **adopted by both critics, except D7, which waits on the user**.
Scripts and outputs: gaint `/home/noob/work/critic4_skcdf/neardup/` (agent 4); agent 2's independent recheck is in `alhvr/log.md`.

## Verdict
1. **There is no newer E-SCDD release.** We use the local copies.
2. **Splits.** Keep BenchmarkEL `20211104`, 478 / 54 / 50, with `masks_escdd`, for every contrast. No re-split is needed.
3. **New issue.** 7 of our 50 test cells are the same physical cell as a train cell. Both tracks report with and without them; the cell list is fixed below. Whether to drop their train twins from the unlabelled pool is for the user (D7).

## D1. Release search (21 Oct, about 14:00 IST)

| Source | State | Local copy |
|---|---|---|
| HF `snt-ubix/escdd` | HEAD `8c8cba9a`, last commit 2025-11-24 (deletes `removed_padding` only) | `~/mtp/datasets/escdd_full` (same commit; audit 12 Oct) |
| HF `shivahanifi/extended-scdd` | `06fc294a`, 2025-11-10 | `~/mtp/datasets/escdd_mirror_shivahanifi` |
| HF `jinyou123/extended-scdd` | 2025-12-30. All 3,481 LFS oids are identical to the shivahanifi mirror (agent 2). | not needed |
| HF `sasan/scdd-unlabeled` | 159,332 unlabelled cells, 76 GB parquet. It looks like a mirror of Pratt's Dropbox pool. | not downloaded |
| GitHub `TheMakiran/BenchmarkELimages` (Pratt) | HEAD `768b5e7`, 2024-03-10. No releases; newest labelled set is `20221008`. | `~/mtp/datasets/BenchmarkEL_releases` |
| GitHub `sntubix/pv-ddpm` | last commit 2025-11-17 (README) | – |
| arXiv 2511.09604 | v1 only | paper local |

HF search (escdd, scdd, electroluminescence, pv, elpv) and Research MCP (2025+) found no other labelled release.

Reading: the release that "adds images and a test split" is E-SCDD itself:
- it is Hanifi et al. 2025, built on Pratt's `20221008`;
- it has 693 + 117 `_rf` + 93 synthetic images;
- it has its own train/val/test split.

We have held it since 12 Oct (handbook 17). team-lead was asked to confirm with the user that they do not mean a different link.

## D2. Split and labels
- Keep `20211104` 478 / 54 / 50 + `masks_escdd` (the P-series data, "D0").
- **Do not use E-SCDD's split.**
  - 39 of our 50 test cells are in E-SCDD train (handbook 17 §5.6).
  - Its test set has inactive in 9 cells, with the top 3 holding 81.5% of inactive pixels. Ours has 16 cells and 58.8%.
  - Switching would void every P-series comparator.
- **E-SCDD's extra labelled cells** (117 `_rf`, and the 113 `20221008` cells not among our 582) stay out of training. Using them would need a separate protocol with every arm re-baselined.
- **Synthetic images** (`^\d+-.+_rf\.png$`, 93 files) are excluded everywhere.

## D3. Baselines and machines
- The split is unchanged, so no baseline has to be re-run *because of data*.
- **Runs carry over only on the same machine.** Every A5c, BsM5, BsD5 and CsM5 run is cv02.
  - A track that runs on gaint must re-run its supervised and reference SSL arms on gaint, in the same experiment and at the same commit.
  - A track that reuses cv02 runs must pass a log-identity check on cv02 first (SK1 protocol §7 is the template).
- If D7 is answered "yes", reused SSL references (BsM5, BsD5) no longer match the pipeline and must be re-run. Supervised arms (A*) are unaffected, because they never read the unlabelled pool.

## D4. Unlabelled pool
- **Primary pool for both tracks:** in-domain, meaning train minus the labelled fraction (455 cells at 5%).
- **The external 11,938-cell pool:** only as a separately declared arm.
- **No E1 cell (the 106) and none of the 17 new `_rf` cells outside our pool** may enter any unlabelled pool.
- **External pool vs our test and val** (agent 4: 128-px high-pass screen, full-res high-pass and residual-texture checks within the same source and module position, then visual montages):
  - No test or val cell is confirmed in the pool.
  - The top candidates are clean mono ARTS cells at the same module position: test `ARTS_00047_r3_c1` and `ARTS_00051_r3_c2`; val `ARTS_00050_r3_c5`, `ARTS_00061_r1_c6` and `ARTS_00130_r5_c6`.
  - Residual correlation for these is 0.89–0.93, but full-res crops show different marks. Shared optical shading at a fixed camera position is the likelier cause. This is unproven either way.
  - The two test cells carry 34 and 202 crack px and no inactive, so any exposure is immaterial.
- **Train cells have exact twins in the pool under other IDs:**
  - `CSIR_00107_r9_c3` = pool `CSIR_00117_r9_c3`;
  - several `ARTS_*_r1_c6` pairs, with 128-px r ≈ 0.9997.
  - The 6 Oct ID filter missed them. They are unlabelled copies of train cells and harmless for test.
- **`sasan/scdd-unlabeled`:** a route to a larger pool later. Before any use it needs the same content dedup against our 582 + E1 + the 17 new cells.

## D5. Larger test set (secondary only)
- **Option A** = our 50 + E1's 106 + the 17 new `_rf` cells not in our pool. It may be reported as a **pre-declared secondary**:
  - final-step weights only;
  - never used for selection or for any rule.
- Before it is built, dedup it against the pool and the train set. One candidate is known: ext `CSIR_00298_r8_c6` vs pool `CSIR_00299_r8_c6` (residual r 0.955).
- **Option B** (adds 111 pool cells): rejected. The external-pool arms train on those cells.

## D6. Fixed lists: report every test number with and without each
Both critics fixed these before any new run. The lists are post hoc relative to the P-series and must be labelled so there.

**Noisy cell:** `CSIR_00070_r8_c4`, as in the memory rule (reported with and without, labelled post hoc).

**Test cells whose physical cell is in train (the 7 "twin" test cells).**
- How they were found: same source and module position, high-pass image correlation 0.80–0.94, and identical crack geometry checked visually.
- Agent 2's independent check: high-pass r 0.931–0.984 vs 0.616 for a non-twin CFVS pair. Crack-mask IoU between `CFVS_00018_r4_c4` and `CFVS_00020_r4_c4` is 1.000 (10,915 px).

| Test cell | Train twin(s) | Test crack px | Test inactive px |
|---|---|---|---|
| `CFVS_00006_r5_c5` | `CFVS_00003_r5_c5` | 505 | 0 |
| `CFVS_00033_r8_c4` | `CFVS_00037_r8_c4` (+ probable early stage `CFVS_00032_r8_c4`) | 4,876 | 0 |
| `CFVS_00035_r8_c4` | `CFVS_00037_r8_c4` | 5,513 | 2,728 |
| `CFVS_00042_r8_c4` | `CFVS_00037_r8_c4` | 4,202 | 3,178 |
| `CFVS_00018_r4_c4` | `CFVS_00020_r4_c4`, `CFVS_00022_r4_c4` | 10,915 | 0 |
| `CFVS_00027_r4_c4` | `CFVS_00031_r4_c4`, `CFVS_00022_r4_c4` | 10,211 | 5,214 |
| `ARTS_00020_r5_c1` | `ARTS_00081_r5_c1` (known since 12 Oct) | 183 | 0 |
| **total** | | **36,405 of 92,074 (39.5%)** | **11,120 of 92,125 (12.1%)** |

(Agent 2 counts 91,838 total test crack px from E-SCDD's own masks, 39.6%. The difference is the P6 remap, handbook 17 §5.3.)

- **Why CFVS repeats.** CFVS images are a time series of the same modules, so one physical cell appears at several stages.
- **Val twins** (val is not used for selection; recorded only):
  - `CFVS_00046_r8_c4` ~ `CFVS_00037`;
  - `CFVS_00010_r7_c4` and `CFVS_00009_r7_c4` (pre-crack) ~ `CFVS_00012_r7_c4`;
  - `CFVS_00017_r4_c4` (pre-crack) ~ `CFVS_00031`;
  - `ARTS_00061_r1_c6` ~ `ARTS_00040_r1_c6` (likely).
- **Test vs val:** `CFVS_00033`, `00035` and `00042_r8_c4` ~ val `CFVS_00046_r8_c4`.
- **Possible clean earlier stages, no defect content, left as is:** `CFVS_00010_r8_c4` and `CFVS_00012_r5_c5`.
- **Checked and rejected as twins** (visual): the BMRK and SDLE high scores. Those are different cells; their smooth images inflate high-pass r.

**Where the twins sit in the label-fraction splits:**
- 5% (seeds 0–2): every train twin above is in the **unlabelled** set.
- 10% and 20%: some twins are labelled (seed 0: `CFVS_00031_r4_c4` and `CFVS_00022_r4_c4` at 10% and 20%, `CFVS_00020_r4_c4` at 20%; seed 2: `ARTS_00081_r5_c1` at 20%).

**Post hoc sensitivity on existing P13/P17 runs** (agent 4, using the per-cell counts behind `scripts/p17_excell.py`; sanity error 0.0 against the re-score JSONs; output `data/leak_sensitivity_p13_p17.txt`).

Each cell gives the difference, then the threshold in brackets (crack IoU / inactive IoU / crack relF1@2).

| Contrast | All 50 | Without the 7 twins | Without twins + noisy cell |
|---|---|---|---|
| BsM5 − A5c | +0.029 (0.016) / +0.107 (0.044) / +0.045 (0.023), passes | +0.019 (0.018) / +0.093 (0.044) / +0.039 (0.028), passes | +0.019 (0.018) / +0.095 (0.046) / +0.039 (0.028), passes |
| BsD5 − A5c | passes | +0.018 (0.013) / +0.110 (0.056) / +0.036 (0.022), passes | passes |
| CsM5 − A5c | passes (inactive, relF1) | +0.002 / +0.099 (0.049) / +0.021 (0.028), passes (inactive) | passes (inactive) |
| BsD5 − BsM5 | n.d. | n.d. | n.d. |

- Absolute crack IoU drops by about 0.06 for every arm (A5c 0.304 → 0.244; BsM5 0.333 → 0.263). The twin cells are large, easy cracks.
- **Reading:**
  - About a third of BsM5's crack IoU gain over A5c sits in the twin cells, and without them it only just passes.
  - The inactive and relF1@2 gains are not driven by the twins.
  - Removing the cells from the score does not remove the advantage: SSL arms trained on the twins' pixels.

## D7. Open: for the user (via team-lead)
**Should new protocols remove the train twins of test cells from the unlabelled pool?**
- The cells concerned are `CFVS_00003_r5_c5`, `CFVS_00037_r8_c4`, `CFVS_00032_r8_c4`, `CFVS_00020_r4_c4`, `CFVS_00022_r4_c4`, `CFVS_00031_r4_c4` and `ARTS_00081_r5_c1`.
- **Yes (critics' recommendation):**
  - it removes an SSL-only transductive advantage on about 40% of test crack;
  - labelled sets and supervised arms are unchanged;
  - reused SSL references (BsM5, BsD5) must be re-run with the reduced pool, and this must be disclosed as a methodology change made after the P-series.
- **No:** pools stay as in the P-series, and the "without the 7 twins" line is the only control.
- **Separately:** should the existing P13/P17/P18 SSL-vs-supervised claims carry the "without twins" line in the thesis?

Until the user answers, no **final** run of either track launches. Smoke runs and identity checks may proceed.

Signed: agent 4 (SKCDF critic), 21 Oct 2026. Agent 2 (ALHVR critic): co-signed by message on this basis (D7 pending, D6 adopted).

**Agent 2 co-signature (21 Oct, about 14:03 IST; corrected clock).** I co-sign D1 to D6; D7 is pending the user. I recomputed the D6 sensitivity independently from the per-cell counts in `results/p13/per_image.json`, `per_image_a2.json`, `results/p12/per_image.json` and `results/p17/per_image.json`, with my own script:
- crack IoU and inactive IoU, means and rule-1 thresholds, match agent 4's table to 4 decimals in both the "all 50" and the "without 7 twins" rows, for BsM5, BsD5 and CsM5 against A5c, and for BsD5 against BsM5;
- relF1@2 was not recomputed, because the per-image files hold only TP/FP/FN.

The twin identity was checked separately (alhvr/log.md, ~14:00).

## User answers (relayed by team-lead, 21 Oct about 15:20 IST)
- **D1 confirmed:** the release the user meant is the local `escdd_full`: HF snt-ubix/escdd @ `8c8cba9a18d65fda8c319d186b1db9f1b804b71e`, MIT, 1,810 files, 30 classes (`ListOfClassesAndColorCodes_20221008.csv`). No other release. Do not use the shivahanifi no-padding or per-class variants: they rescale the cell and change crack width.
- **D7 = yes:** new protocols drop the 7 train twins from the unlabelled pool, and the SSL references are re-run.
- **Old P13/P17/P18 claims:** keep them and add "without twins" lines alongside; do not replace.
- **Machine:** cv02 for both tracks; outputs are copied back to gaint with MD5.
