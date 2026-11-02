# Build: HC2, opt-in inactive handling on top of HC (deploy **0405151**; arm = (a2) `data.synth_halfcut_ignore_inactive=true`)

builder, 2 Nov 2026 (v1, ACCEPTED by coach; v1.1 = §9 addendum: REVISION, 255 collision check, resume check, full non-test diff; no code change, deploy still 0405151). Code only. No test or E1 read. Spec: protocol_SKR2_HC2 §2 (decision D1, team-lead 2 Nov 11:27; D1 refinement with a pre-set rule, 11:33). Parent build: `build_hc.md` (HC deploy c2e6973). Tags: E = measured (file named), S = judgement.

## 0. Summary
- **Code:** gaint worktree **`/home/noob/work/el_hc2`**, new branch **`hc2`** from c2e6973. Two commits:
  - **b28c284**: `data.synth_halfcut_exclude_inactive` (D1 as first decided: inactive-bearing sources ineligible);
  - **0405151 = deploy** (`0405151c2e24e1ddb6fb5fd5fa64a77c0823854e`, stamp `el_hc2/reports/hc2/DEPLOY`): `data.synth_halfcut_ignore_inactive`, the (a2) variant the pre-set rule selected (§1). Both keys default off and are mutually exclusive.
  - `/home/noob/work/el_hc` was not touched: HEAD c2e6973, 0 tracked changes, checked before and after each step. runner's queue and smokes use it. A new worktree and branch were needed because branch `hc` is checked out in el_hc; a commit on `hc` would have moved el_hc's HEAD under runner.
- **HC2 arm (a2) opts:** SUP100-PF opts + `data.synth_halfcut.p=0.35 data.synth_halfcut.pool=data/splits/synth_halfcut_pool_ap.tsv data.synth_halfcut_ignore_inactive=true` at el_hc2 0405151.
  - All 353 rule_p sources stay eligible. p 0.35 per eligible sample, simulator, pool, jitter and draws are HC's.
  - In a synthesized view, every inactive (class 11) px of the mask becomes **255**, which the loss ignores (CEDiceLoss ignore_index 255, in CE and in Dice).
  - Real views are unchanged, inactive labels included. Synthetic images are byte-identical to HC's.
- **Rule inputs (E, §1):** the exclude variant keeps only **0.399** of the rule_p sources' crack px (0.359 in synthetic views). That is < 0.60, and the ignore index is supported, so the rule gives (a2).
- **Counts (E, house masks):** 35 of the 353 rule_p sources hold inactive px (not 41; §2). Under (a2) they stay eligible. In the unit test's one view per cell (p 1), 33 of these 35 views carry ignored px; ignored px are **0.23%** of synthetic px.
- **Expected at p 0.35 (a2):**

  | Measure | Expected |
  |---|---|
  | synthetic share | 0.2585 (= HC; H1 measured 0.2564) |
  | eligible share | 0.7385 (H1 0.7386) |
  | p_eff | 0.35 |
  | excluded | 0 |
  | synthetic inactive px | **0** |
  | synthetic ignored px | ~0.2% of synthetic px |

- **Tests (E):** 15 new (8 exclude, 7 ignore); HC's 14 unchanged. Suite **314 passed, 3 skipped** (HC 299 + 15; same 3 skips), CPU only.
- **CPU identity (E, 5 real steps, at 0405151):** switch absent (house, PF), p 0 with the ignore key on, and p 0 with the exclude key on are **IDENTICAL** to e544133 and to c2e6973. p 0.35 with the keys off or false is **IDENTICAL** to c2e6973. p 0.35 with the ignore key on is IDENTICAL for 5 steps, as predicted (no ignored px before batch 7). A 9-step pair shows the effect starting exactly at step 8 (§5).

## 1. D1 rule inputs (team-lead 11:33: exclude if crack-px retention ≥ 60%, else ignore if the loss supports an ignore index)
- **Crack-px retention of the exclude variant** (E, `builder_scratch/hc2_retention.py` md5 cd81d945, out c2aac2c9; house masks; class 14):

  | Reading | All 353 sources | 318 kept | Retention |
  |---|---|---|---|
  | whole source masks | 232,346 px | 92,681 px | **0.399** |
  | synthetic views (jitter off, mean of both halves) | 224,856 px | 80,634 px | **0.359** |
  | crack sources (≥ 1 px; same at ≥ 20 px) | 168 | 133 | 0.79 |

  - All 35 inactive-bearing sources are crack cells, and they hold ~60% of the sources' crack px (judge W4: ~58% on the families' train cells).
- **Ignore support (E):**
  - the HC2 loss is `loss.supervised=ce_dice`. `loss_factory` builds `CEDiceLoss(dice_classes, dice_weight)` with the default `ignore_index=255`;
  - `ce_dice.py` uses `valid = targets != ignore_index` for CE (mean over valid px) and for both Dice terms (p and y multiplied by valid);
  - precedent: Track M R4 (commit 0642889) trained with 255 in labelled masks;
  - the class weights come from the real masks before any transform (`count_class_pixels` on the stem list), so they are unaffected;
  - unit test: the loss does not depend on the logits at 255 px and equals CE + Dice over the valid px.
- **Amount relabelled:** inactive px in HC's synthetic views = 0.21% of px (mean 552 px per view, jitter off, all 353). The deployed transform at p 1 (seeds as the test) gives 212,582 px = 0.23% of synthetic px (`builder_scratch/hc2_ignore_stats.py` a560bc2c). Per inactive-bearing view: min 0, median 3,841, max 33,938 px. 2 of the 35 views crop to a half without inactive.

## 2. Counts (E; `el_hc2/reports/hc2/source_count.txt` md5 b5979192, `excluded_sources.tsv` 12168461, `excluded_stems.txt` **8476d11d**, pinned in the test)
These define the exclude key (b28c284) and the retention above. Under (a2) all 353 remain sources.
- 478 train cells; 353 rule_p sources (= HC); 35 hold inactive px; 318 do not; 125 are not rule_p sources. 42 train cells hold inactive px.
- **Inactive-bearing sources by group:** CFVS 25, CSIR 9, ARTS 1. BMRK / SDLE have no rule_p sources.
- **Inactive px per source:** min 295, median 3,259, max 30,424. No source holds 1-294 px, so the "≥ 1 px" cut does not depend on specks.
- **Why not 41 (E, `builder_scratch/hc2_count_stages.py`):**

  | Stage | Cells | With inactive px |
  |---|---|---|
  | all train | 478 | 42 |
  | gaps found (226967c rule) | 466 | **41** |
  | + g ≤ 20 | 411 | **41** |
  | + rule_p padding < 0.4 (= HC sources) | 353 | **35** |

  - 41 is domain's pre-rule_p budget ("inactive in 36 / 41"), not a count of rule_p sources.
  - rule_p's padding cut already excludes 6 inactive BMRK single-cell crops: BMRK_00097_cell0277, 00222_cell0882, 00446_cell0206, 00601_cell0661, 00796_cell1630, 01660_cell0398.
  - CSIR_00092_r12_c5 has no gaps found.
  - On `masks_coded` the count would be 36. Training uses `masks_escdd`.
  - Class 17 (dead_cell) is not part of either key. Its 1 train cell is not a rule_p source.
- **The 35** (stem, inactive px):
  - ARTS_00024_r2_c1 381;
  - CFVS: 00013_r7_c4 13,551 · 00015_r7_c4 13,080 · 00015_r9_c3 3,670 · 00016_r7_c4 13,977 · 00020_r4_c4 2,771 · 00021_r5_c2 2,230 · 00022_r4_c4 3,951 · 00030_r6_c3 295 · 00031_r4_c4 6,064 · 00031_r5_c5 2,588 · 00037_r8_c4 3,131 · 00038_r8_c3 2,152 · 00045_r4_c3 1,695 · 00095_r7_c2 4,905 · 00103_r9_c3 11,176 · 00114_r8_c2 13,467 · 00125_r8_c5 19,821 · 00126_r5_c3 15,554 · 00130_r8_c2 22,342 · 00134_r6_c3 451 · 00139_r4_c3 15,774 · 00140_r4_c2 3,259 · 00146_r8_c3 30,424 · 00181_r9_c6 2,430 · 00184_r8_c2 2,979;
  - CSIR: 00055_r6_c3 3,956 · 00072_r7_c3 354 · 00090_r3_c5 2,891 · 00092_r11_c5 1,383 · 00092_r3_c2 2,109 · 00135_r9_c3 10,249 · 00179_r12_c4 6,034 · 00179_r2_c4 393 · 00203_r3_c3 2,404.

## 3. Diff (`git diff c2e6973 0405151`: 6 files, +632 / −9)
| File | md5 c2e6973 → 0405151 | Change |
|---|---|---|
| `src/data/synth_halfcut.py` | 66686cd0 → **65992532** | Constants `INACTIVE_CLASS = 11`, `IGNORE_VALUE = 255`, code `NOT_SOURCE_INACTIVE = 3`. `SynthHalfCut(..., exclude_inactive=False, ignore_inactive=False)`: bool only, exclusive. **exclude:** after `find_source`, an inactive-bearing source returns the unchanged objects with code 3, before any draw. **ignore:** after `synthesize()` (all draws done), `OM[OM == 11] = 255` on synthesize's own new array. Either on: a made view still holding class 11 raises `RuntimeError` |
| `scripts/train.py` | 64dbf938 → **c87de62e** | `check_synth_halfcut`, per key: bool only; true needs `data.synth_halfcut`; nested spelling `data.synth_halfcut.<key>` refused. Both on: refused. ignore needs `loss.supervised=ce_dice`. `build_benchmark_data` passes a key only when present, plus an own log line per key when on. The existing `synth_halfcut: p ...` line is unchanged |
| `src/trainers/trainer.py` | 46e4470f → **a4967640** | Code counters have length 4. The `synth window` line is unchanged in format; its `not_eligible` = code 2 + code 3, and code 3 occurs only under exclude. With either key on, an own line (§6) counts the px of the batch's synthetic views as trained (`batch["mask"][synth == 1]`, the CPU tensor, no draw): inactive, ignored (255), all |
| `tests/test_hc2_exclude_inactive.py` | new, **5bec64c5** | 8 tests (§4) |
| `tests/test_hc2_ignore_inactive.py` | new, **27936e11** | 7 tests (§4) |
| `scripts/hc/hc2_source_count.py` | new, 4b3ba05f | Count of §2 (deployed transform, p 0, exclude on); excluded TSV; expected shares |

- Unchanged (md5 equal at c2e6973 and 0405151): `src/data/benchmark_el.py` 41188cad, `src/losses/ce_dice.py` 13b1c6a7, `tests/test_hc_synth.py` 829bbe3f, pool a78a2d2a, `scripts/hc/smoke_hc.sh` 5a5c707b.
- **Which code runs with the keys off (judge's condition (b)):** every changed non-test line is behind one of the two keys, or inside HC's synth logging branch (`if self.synth_on`). That branch changes in two ways: counter lists of length 4, and `not_eligible` printed as code 2 + code 3, where code 3 is always 0 with exclude off.
  - Nothing touches the training step math, the data path with the keys off, `benchmark_el.py` or the loss.
  - The HC log line is byte-identical: HC's `test_trainer_synth_log_line` passes unchanged, and so does a key-off check in my tests.
  - The CPU identity (§5) covers house, PF, p 0 and p 0.35.

## 4. Tests (E; `el_hc2/reports/hc2/suite_0405151.txt` md5 836329ea, run at HEAD 0405151: 314 passed, 3 skipped; CPU only, `CUDA_VISIBLE_DEVICES=""`, nice 19, 8 threads, F1_IMAGENET=1)
**`tests/test_hc2_ignore_inactive.py`, (a2), the arm:**
1. **Real train list, p 1, seeds = cell index:** every cell's code, image bytes, dtypes and generator state equal the key-off transform.
   - A made view's mask = the key-off mask with 11 → 255, nothing else changed. Other codes return the same unchanged objects.
   - 353 made, 125 not sources. The 35 inactive-bearing views carry ignored px (≥ 30 of them; measured 33). The 318 others carry none. No synthetic view holds class 11.
2. **Toy cell** (inactive block), 4 seeds: the key-off view does hold inactive px; key on = the same image with 11 → 255 (same px count). Not drawn at p 0: the real view keeps its inactive labels.
3. **Stream:** p 0 + key on = the house stream bit for bit. At p 0.5 and p 1: codes, images and stems equal the key-off stream; masks are equal except 11 → 255 in made samples, which holds after the label-safe ops. No code 3.
4. **Key off = c2e6973** (`ignore_inactive=False`, toy stream at p 0.5): equal to c2e6973's `synth_halfcut.py` loaded from git.
5. **CEDiceLoss:** ignore_index 255; the loss is unchanged when the logits at the 255 px are perturbed; it equals CE (mean over valid px) + Dice (valid px) computed by hand.
6. **Switch checks:**
   - accepted: HC only, key true, key false, and ignore true with exclude false;
   - refused: ignore true without HC, `"true"`, both keys true, the nested spelling, ignore with `loss.supervised=weighted_ce`;
   - `--opts ...=true` parses to bool;
   - refused in `SynthHalfCut`: `"true"`, `1`, and both keys on.
7. **Trainer line:** made samples with 6 px of 255 each give `synthetic_ignored_px 24` per window and 48 in total, share 0.02344 of synthetic px. The HC line is as HC.

**`tests/test_hc2_exclude_inactive.py`, the exclude key (b28c284; off in the arm):**
1. Real list p 1: 318 made / 35 code 3 / 125 code 2; ineligible cells return the unchanged objects and leave the generator state untouched; no made view holds inactive; key off gives 353 / 125; groups 25 / 9 / 1; stem md5 8476d11d.
2. Toy inactive-bearing source: code 3 at p 1 / 0.35 / 0 with no draw. Key off: made with inactive. Without inactive: made.
3. The leak guard raises.
4. Stream with the key on: p 0 = house; at p 1, code-3 samples equal the house sample.
5. Key off = c2e6973, toy stream at p 0.35 and p 1 (absent and false).
6. Key off = c2e6973 on all 478 real cells at p 1: code, bytes, dtypes and generator state equal; 353 made.
7. Switch checks, including both keys on → refused.
8. Trainer lines: code 3 counts in `not_eligible`; the HC2 line counts; key absent or false gives no HC2 line.

HC's 14 tests (`tests/test_hc_synth.py`, md5 unchanged) pass at 0405151.

## 5. CPU identity (E; harness `builder_scratch/identity_cpu.py` md5 962379a6, as HC; CPU fp32, 8 threads, nice 19, `CUDA_VISIBLE_DEVICES=""`, 5 real steps)
Compared fields: loss / loss_sup / loss_con / lambda repr, lr of every group, sha of all params + buffers after every step, fixed-batch logits and shape, fixed-batch stems / image / mask sha, init state, class-count sha, loss class, n_params. Only `sec` is ignored. References: the e544133 export records (`builder_scratch/idchk/A_e544133_house.json`, `C_e544133_pf.json`) and el_hc c2e6973's records (`el_hc/reports/hc/idchk_c2e6973/`).

Run dir `el_hc2/reports/hc2/idchk_0405151/` (run.sh md5 7116c436; compare `builder_scratch/idchk_hc2a2_compare.py` 094603a0 → `compare.txt` f4a3d775: **ALL AS EXPECTED**; 7 runs rc 0, 0 Tracebacks; HEAD 0405151, 0 tracked changes).

| Run at 0405151 (5 steps) | vs e544133 export | vs c2e6973 record |
|---|---|---|
| house, switch absent | **IDENTICAL** 5/5 (A) | **IDENTICAL** (HC_house_off) |
| SUP100-PF, switch absent | **IDENTICAL** 5/5 (C) | **IDENTICAL** (HC_pf_off) |
| SUP100-PF, p 0 + **ignore key on** | **IDENTICAL** 5/5 (C) | **IDENTICAL** (HC_pf_p0) |
| SUP100-PF, p 0 + exclude key on | **IDENTICAL** 5/5 (C) | **IDENTICAL** (HC_pf_p0) |
| SUP100-PF, p 0.35, keys absent | | **IDENTICAL** (HC_pf_p035) |
| SUP100-PF, p 0.35, ignore key false | | **IDENTICAL** (HC_pf_p035) |
| SUP100-PF, p 0.35, ignore key on | | IDENTICAL over 5 steps (predicted below) |

- Fixed-batch key lists: `synth` is present iff `data.synth_halfcut` is set, as at c2e6973. The values (stems, image, mask sha) are equal.
- **Why p 0.35 + ignore on is identical over 5 steps (E, `stream_ign.txt`, `builder_scratch/hc2_stream_ign.py`):**
  - in the identity stream's batches 0-5, images and codes equal the key-off stream, and no synthetic view holds an ignored px;
  - the two inactive-bearing sources made in batch 2 (CSIR_00090_r3_c5, CFVS_00095_r7_c2) were cropped to the half without inactive;
  - the first synthetic view with ignored px is in **batch 7** (CFVS_00146_r8_c3, 34,651 px), then batches 16, 17, 20, 23, 31, 37, 38 (`hc2_stream_ign_n.py`, 40 batches).
- **(a2) end to end on CPU, 9 steps** (key absent vs ignore on, both at 0405151; `run9.sh` 56335cde, compare `builder_scratch/idchk_hc2a2_cmp9.py` 7ac4c51a → `compare9.txt` b169478c): **AS PREDICTED**.
  - steps 1-7 IDENTICAL (loss, lr, params + buffers sha, logits);
  - **step 8 differs** (loss 4.497069 off vs 4.498464 on), step 9 too;
  - losses finite; init state, class-count sha and fixed batch equal.
  - So 255 px reach the real training step through `train.py` → dataset → trainer → CEDiceLoss and change only the steps whose batch holds them.
- **b28c284 chain** (exclude key; `el_hc2/reports/hc2/idchk_b28c284/compare.txt`, ALL AS EXPECTED): house / PF off, p 0 + exclude on / false IDENTICAL to e544133 and c2e6973; p 0.35 key absent / false IDENTICAL to c2e6973; p 0.35 + exclude on first differs at step 3, as predicted (batch 2 holds 2 excluded sources that HC made).

## 6. Live readouts (for runner's GPU smoke, after coach's OK)
- **Log lines at 0405151 with (a2) on:**
  - `synth_halfcut: p 0.35 jitter 0.08 pool data/splits/synth_halfcut_pool_ap.tsv (1008 pairs, md5 a78a2d2a...)`, unchanged;
  - `synth_halfcut_ignore_inactive: on (inactive (class 11) px of synthetic views -> 255, ignored by the loss)`;
  - every log window: `synth window: made A eligible_not_drawn B not_eligible C | total: ... (share S, eligible E, p_eff P) at step N`, unchanged, so `s2_smoke_parse.py` 0d5c448a's regex still applies;
  - then `synth inactive: excluded 0 synthetic_inactive_px X synthetic_ignored_px Y | total: excluded 0 (share 0.0000) synthetic_inactive_px T synthetic_ignored_px U (share of synthetic px R) at step N`.
- **Expected:** share **0.2585**, eligible **0.7385**, p_eff **0.35** (all = HC's H1); synthetic_inactive_px total **0 exactly**; R ≈ 0.002 (S: ~±0.001 at 1,000 steps, since only ~200 of the ~2,070 synthetic views come from inactive-bearing sources).
- **Peak:** expected = HC's 6,826 MiB (the transform runs in the CPU workers; the loss is unchanged), so the gate stays 9,000.
- **Smoke opts:** SUP100-PF s0 + the three (a2) opts, 1,000 steps, el_hc2 0405151 with 0 tracked changes, run name e.g. `hc2_smk_HCig_s0`.
- **GPU H0:** not needed by the protocol's chain argument (c2e6973 = e544133 on GPU for 2,000 steps; 0405151 = c2e6973 on CPU with the keys off and at p 0 with the key on, §5). If coach / judge read condition (b) literally, a 1,000-step p 0 + key-on run vs `f3_SUPPF_100pct_s0` can ride with the smoke (~8 min).

## 7. Disclosures (S unless marked)
- **(a2) keeps HC's crack dose and half-cut geometry in full.** It only removes inactive supervision from the synthetic views. Inactive cells are seen with labels in their real views (~65% of their draws, as under HC). In their synthetic views (~35%), the inactive region is ignored rather than taught.
- **Ignored px are not "not inactive":** the loss neither rewards nor penalises any class there. Neighbouring non-inactive px in the same view are trained as usual.
- **Dice on inactive:** CEDiceLoss's inactive Dice term (dice_classes 14, 11) sees no inactive px from synthetic views. A batch made only of synthetic views of inactive sources would push predicted inactive mass down over its valid px, as for any batch without inactive (CEDiceLoss docstring). E: H1's mix has ~74% real views per batch.
- **CE class weights are unchanged** (computed from the real masks; ce_dice is unweighted anyway).
- **Totals restart after a resume** (logging only), as HC.
- **The exclude key stays in the code (off).** It is tested and identity-checked (b28c284 chain, records `el_hc2/reports/hc2/idchk_b28c284/`, all as expected), and is not part of the arm.
- **Not changed:** simulator, pool, jitter, p, rule_p, draw order, the house transforms and their seeds, `benchmark_el.py`, the loss.

## 8. Reproduce (gaint)
```
cd /home/noob/work/el_hc2   # HEAD 0405151, 0 tracked changes
export CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=8 MKL_NUM_THREADS=8 PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 F1_IMAGENET=1
nice -n 19 /home/noob/work/el-fault-detection/.venv/bin/python -m pytest -p no:cacheprovider tests -q
bash reports/hc2/idchk_0405151/run.sh && /home/noob/work/el-fault-detection/.venv/bin/python /home/noob/work/builder_scratch/idchk_hc2a2_compare.py reports/hc2/idchk_0405151
```

## 9. Addendum v1.1 (after coach's ACCEPT; no code change, deploy still 0405151)
- **REVISION:** `/home/noob/work/el_hc2/REVISION` = `0405151`. It is untracked, in the same format as el_hc's `c2e6973`. HEAD = DEPLOY = REVISION = 0405151, 0 tracked changes.
- **Arm opts / run names (coach):**
  - opts: pf2 SUPPF + `data.synth_halfcut.p=0.35 data.synth_halfcut.pool=data/splits/synth_halfcut_pool_ap.tsv data.synth_halfcut_ignore_inactive=true`;
  - run names: `hc2_HCig_100pct_s5..9`;
  - GPU checks (runner, coach's ruling on condition (b)): H0 at 0405151, p 0 + ignore on, 1,000 steps, step + PF lr lines vs `f3_SUPPF_100pct_s0.stdout`; then the HC2 smoke (§6).
- **255 collision check** (coach's question; E, code read at 0405151):
  - The label-safe pipeline (`get_labelsafe_augmentation`) is Resize 512 (a no-op on 512 inputs), HorizontalFlip, VerticalFlip, RandomRotate90, then RandomBrightnessContrast and Normalize (image only). There is no rotation by arbitrary angles, no affine, no padding, so no mask fill value exists.
  - Real masks cannot hold 255: `load_index_mask` raises on values ≥ 24 unless `data.mask_ignore_value` is set (Track M only; not in the pf2 SUPPF opts).
  - The synthetic pad label is class 7, not 255. So 255 in a training mask comes only from the (a2) relabel. This agrees with the 9-step check (§5): the run changes exactly at the first batch with a relabelled view.
- **Resume under (a2)** (E, one-off `builder_scratch/hc2_resume_ign.py` 885549a7 → `el_hc2/reports/hc2/resume_ign.txt` 341c7c1a; real labelled stream, pf2 SUPPF opts, p 0.35, ignore on): resumed at batch 7, batches 7 and 8 equal the uninterrupted stream (image, mask, codes, stems); batch 7 holds 34,651 ignored px. (HC's own resume test also passes at 0405151.)
- **What (a2) can and cannot tell (S, team-lead's note for v1.1):** inactive px are only ~0.21-0.23% of synthetic-view px (§1).
  - So (a2) mainly tests whether the inactive labels in synthetic views matter.
  - If HC2's inactive cost stays, the other explanation stays open: dilution, i.e. fewer real views of inactive cells. Under HC and (a2) alike, the 35 inactive-bearing sources are real in ~65% of their draws.
- **Full non-test diff** `git diff c2e6973 0405151 -- src/data/synth_halfcut.py scripts/train.py src/trainers/trainer.py scripts/hc/hc2_source_count.py` (260 lines, md5 768366b4). `scripts/hc/hc2_source_count.py` is a read-only build tool, not imported by training:

```diff
diff --git a/scripts/hc/hc2_source_count.py b/scripts/hc/hc2_source_count.py
new file mode 100644
index 0000000..989355b
--- /dev/null
+++ b/scripts/hc/hc2_source_count.py
@@ -0,0 +1,61 @@
+"""HC2 build check (CPU, read-only): classify every train cell (house masks) with the deployed transform at p = 0 and
+``exclude_inactive`` on, so nothing is drawn: eligible (code 0), not a rule_p source (2), rule_p source excluded because
+its mask holds inactive (class 11) px (3). Writes the excluded sources (stem, inactive px, group) as a TSV and prints the
+counts and the expected live shares at a given p.
+
+Usage: python scripts/hc/hc2_source_count.py --out excluded.tsv [--p 0.35] [--masks data/labeled/masks_escdd]
+"""
+from __future__ import annotations
+
+import argparse
+import collections
+import hashlib
+import sys
+from pathlib import Path
+
+import numpy as np
+from PIL import Image
+
+ROOT = Path(__file__).resolve().parents[2]
+sys.path.insert(0, str(ROOT))
+from src.data.benchmark_el import load_index_mask  # noqa: E402
+from src.data.splits import load_split  # noqa: E402
+from src.data.synth_halfcut import (INACTIVE_CLASS, NOT_DRAWN, NOT_SOURCE, NOT_SOURCE_INACTIVE,  # noqa: E402
+                                    SynthHalfCut)
+
+
+def main() -> None:
+    ap = argparse.ArgumentParser()
+    ap.add_argument("--out", required=True)
+    ap.add_argument("--p", type=float, default=0.35)
+    ap.add_argument("--masks", default="data/labeled/masks_escdd")
+    a = ap.parse_args()
+    stems = load_split(ROOT / "data/splits/train.txt")
+    s = SynthHalfCut(0.0, ROOT / "data/splits/synth_halfcut_pool_ap.tsv", exclude_inactive=True)
+    codes, rows, inact_cells = collections.Counter(), [], 0
+    for st in stems:
+        img = np.array(Image.open(ROOT / "data/labeled/images" / f"{st}.png").convert("L"))[:, :, None]
+        M = load_index_mask(ROOT / a.masks / f"{st}.png")
+        code = s.apply_pair(img, M)[2]
+        codes[code] += 1
+        k = int((M == INACTIVE_CLASS).sum())
+        inact_cells += k > 0
+        if code == NOT_SOURCE_INACTIVE:
+            rows.append((st, k, st.split("_")[0]))
+        if code == NOT_DRAWN:
+            assert k == 0, st
+    n, elig, excl, nsrc = len(stems), codes[NOT_DRAWN], codes[NOT_SOURCE_INACTIVE], codes[NOT_SOURCE]
+    body = "stem\tinactive_px\tgroup\n" + "".join(f"{st}\t{k}\t{g}\n" for st, k, g in sorted(rows))
+    Path(a.out).write_text(body)
+    print(f"train cells {n}; rule_p sources {elig + excl}; excluded (inactive) {excl}; eligible {elig}; "
+          f"not rule_p sources {nsrc}; train cells with inactive px {inact_cells}")
+    print("excluded by group", dict(sorted(collections.Counter(g for _, _, g in rows).items())))
+    ks = sorted(k for _, k, _ in rows)
+    print(f"inactive px per excluded source: min {ks[0]} median {ks[len(ks) // 2]} max {ks[-1]}")
+    print(f"expected at p {a.p}: eligible share {elig / n:.4f}, synthetic share {a.p * elig / n:.4f}, "
+          f"excluded share {excl / n:.4f}, synthetic views kept vs HC {elig / (elig + excl):.4f}")
+    print(f"{a.out}: md5 {hashlib.md5(body.encode()).hexdigest()}")
+
+
+if __name__ == "__main__":
+    main()
diff --git a/scripts/train.py b/scripts/train.py
index d4f0017..7be91f2 100644
--- a/scripts/train.py
+++ b/scripts/train.py
@@ -108,8 +108,26 @@ def frac_tag(frac: float) -> str:
 def check_synth_halfcut(cfg: dict, method: str) -> None:
     """HC switch (opt-in ``data.synth_halfcut`` = {p, pool, jitter}; not in base.yaml): synthetic half-cut cells in the
     labelled training stream (src/data/synth_halfcut.py, protocol_HC). Supervised BenchmarkEL runs with the label-safe
-    augmentation only, no cp / absh. Absent: nothing changes."""
+    augmentation only, no cp / absh. Absent: nothing changes.
+    HC2 (opt-in, true / false; absent or false = HC unchanged; at most one on; each needs ``data.synth_halfcut``):
+    ``data.synth_halfcut_exclude_inactive`` makes sources whose mask holds inactive px ineligible;
+    ``data.synth_halfcut_ignore_inactive`` (a2) labels the inactive px of synthetic views 255 (ignored; ce_dice only)."""
     sh = cfg.get("data", {}).get("synth_halfcut")
+    keys = ("exclude_inactive", "ignore_inactive")
+    on = {}
+    for k in keys:
+        v = cfg.get("data", {}).get(f"synth_halfcut_{k}")
+        if v is not None and not isinstance(v, bool):
+            raise ValueError(f"data.synth_halfcut_{k} must be true or false, got {v!r}")
+        if v and not sh:
+            raise ValueError(f"data.synth_halfcut_{k} needs data.synth_halfcut")
+        if isinstance(sh, dict) and k in sh:
+            raise ValueError(f"use data.synth_halfcut_{k} (not data.synth_halfcut.{k})")
+        on[k] = bool(v)
+    if all(on.values()):
+        raise ValueError("data.synth_halfcut_exclude_inactive and data.synth_halfcut_ignore_inactive are exclusive")
+    if on["ignore_inactive"] and cfg.get("loss", {}).get("supervised") != "ce_dice":
+        raise ValueError("data.synth_halfcut_ignore_inactive needs loss.supervised=ce_dice (ignore_index 255)")
     if not sh:
         return
     if method != "supervised" or cfg["data"].get("dataset", "benchmark_el") != "benchmark_el" or cfg.get("cp") \
@@ -461,9 +479,17 @@ def build_benchmark_data(cfg: dict, method: str, seed: int, frac: float, is_ssl:
         if d_cfg.get("synth_halfcut"):
             from src.data.synth_halfcut import SynthHalfCut
             sh = d_cfg["synth_halfcut"]
-            synth = SynthHalfCut(float(sh["p"]), sh["pool"], float(sh.get("jitter", 0.08)))
+            hc2 = {k: d_cfg[f"synth_halfcut_{k}"] for k in ("exclude_inactive", "ignore_inactive")
+                   if d_cfg.get(f"synth_halfcut_{k}") is not None}  # HC2 (opt-in): absent / false = HC unchanged
+            synth = SynthHalfCut(float(sh["p"]), sh["pool"], float(sh.get("jitter", 0.08)), **hc2)
             logger.info("synth_halfcut: p %s jitter %s pool %s (%d pairs, md5 %s)", synth.prob, synth.jitter,
                         sh["pool"], len(synth.pool), synth.pool_md5)
+            if synth.exclude_inactive:
+                logger.info("synth_halfcut_exclude_inactive: on (sources whose mask holds inactive (class 11) px are "
+                            "ineligible)")
+            if synth.ignore_inactive:
+                logger.info("synth_halfcut_ignore_inactive: on (inactive (class 11) px of synthetic views -> 255, "
+                            "ignored by the loss)")
         labeled_ds = BenchmarkELDataset(img_dir, msk_dir, labeled_stems, strong_aug, ignore_value=ign,
                                         **({"synth": synth} if synth is not None else {}))
         labeled_loader = BatchStream(labeled_ds, lbs, stream_id=0, **stream_kw)
diff --git a/src/data/synth_halfcut.py b/src/data/synth_halfcut.py
index 7e7fbb5..022fdc8 100644
--- a/src/data/synth_halfcut.py
+++ b/src/data/synth_halfcut.py
@@ -20,6 +20,18 @@ training jitter of dom_synth_halfcut.py). Per labelled training sample, before t
      from the 1,008 pool half-cell pairs (``pool`` file, CSIR_00300 excluded), rounded and clipped to uint8.
   Candidates that are not sources pass through unchanged. Output is always 512 x 512, labels stay 0-23.
 
+HC2 (protocol_SKR2_HC2 s2, decision D1, opt-in ``exclude_inactive``; ``data.synth_halfcut_exclude_inactive=true``):
+a source whose mask (the whole 512 x 512 crop) holds >= 1 inactive (class 11) px is ineligible too: it passes through
+unchanged as a real view (code ``NOT_SOURCE_INACTIVE``) and draws nothing. On the 478 train cells (house masks) 35 of the
+353 sources hold inactive px (CFVS 25, CSIR 9, ARTS 1), so 318 sources remain (tests/test_hc2_exclude_inactive.py).
+A synthesized view then holds no inactive px (checked: RuntimeError otherwise). Off (default): exactly the HC transform.
+
+HC2 (a2) (team-lead's pre-set D1 rule, 2 Nov: the exclude variant keeps only 0.40 of the sources' crack px, < 0.60, so
+inactive px are ignored instead; opt-in ``ignore_inactive``; ``data.synth_halfcut_ignore_inactive=true``): all rule_p
+sources stay eligible and the draws and images are HC's; in a synthesized view every inactive (class 11) px of the mask
+becomes ``IGNORE_VALUE`` = 255, which the supervised loss ignores (CEDiceLoss ignore_index 255). Real views are unchanged.
+At most one of ``exclude_inactive`` / ``ignore_inactive`` is on.
+
 Randomness: every draw comes from this object's own ``random_generator``. ``SynthHalfCut`` is an (empty) Albumentations
 Compose so that the batch stream's ``seed_pipeline`` gives it a per-sample seed (deterministic and resumable, independent
 of the worker count). The dataset stores it after its house transform, so the stream seeds the house transforms first;
@@ -43,8 +55,11 @@ PAD_CLASS = 7        # BenchmarkEL "padding"
 SIZE = 512
 MAX_GAP = 20         # widest inserted gap band (px)
 MAX_PAD_FRAC = 0.4   # largest padding (class 7) fraction of the band's px
+INACTIVE_CLASS = 11  # BenchmarkEL "inactive" (HC2: sources holding it are ineligible when exclude_inactive is on)
 # per-sample outcome codes (sample["synth"]): eligible but not drawn, synthesized, not eligible
 NOT_DRAWN, MADE, NOT_SOURCE = 0, 1, 2
+NOT_SOURCE_INACTIVE = 3  # HC2 only: a rule_p source excluded because its mask holds inactive px (not eligible)
+IGNORE_VALUE = 255  # HC2 (a2): label of inactive px in synthetic views (the supervised losses' ignore_index)
 
 
 def load_pool(path: str | Path) -> tuple[np.ndarray, str]:
@@ -151,23 +166,34 @@ class SynthHalfCut(A.Compose):
     An empty Compose: only its own seeded ``random_generator`` is used (the stream reseeds it per sample). Eligibility is a
     deterministic function of (image, mask) and is checked first; only an eligible sample draws, in this order: u (made if
     u < p), then for a made sample x jitter, y jitter, half, pool index. p = 0 draws nothing.
+    ``exclude_inactive`` (HC2, default False): a source whose mask holds inactive px is not eligible (code 3, no draw).
+    ``ignore_inactive`` (HC2 (a2), default False): inactive px of a synthesized view's mask become IGNORE_VALUE (no draw).
     """
 
-    def __init__(self, p: float, pool: str | Path, jitter: float = 0.08) -> None:
+    def __init__(self, p: float, pool: str | Path, jitter: float = 0.08, exclude_inactive: bool = False,
+                 ignore_inactive: bool = False) -> None:
         super().__init__([])
         if not 0.0 <= float(p) <= 1.0 or not 0.0 <= float(jitter) < 1.0:
             raise ValueError(f"synth_halfcut: p in [0, 1] and jitter in [0, 1) needed, got {p}, {jitter}")
+        if not isinstance(exclude_inactive, bool) or not isinstance(ignore_inactive, bool):
+            raise ValueError(f"synth_halfcut: exclude_inactive / ignore_inactive must be true or false, got "
+                             f"{exclude_inactive!r} / {ignore_inactive!r}")
+        if exclude_inactive and ignore_inactive:
+            raise ValueError("synth_halfcut: exclude_inactive and ignore_inactive are exclusive")
         self.prob, self.jitter = float(p), float(jitter)
+        self.exclude_inactive, self.ignore_inactive = exclude_inactive, ignore_inactive
         self.pool, self.pool_md5 = load_pool(pool)
         self.last_padded = False
 
     def apply_pair(self, image: np.ndarray, mask: np.ndarray) -> tuple[np.ndarray, np.ndarray, int]:
-        """(image, mask, outcome code). Unchanged objects are returned for NOT_DRAWN and NOT_SOURCE."""
+        """(image, mask, outcome code). The unchanged objects are returned for every code but MADE."""
         self.last_padded = False
         I = image[:, :, 0].astype(np.float64)
         geo = find_source(I, mask)
         if geo is None:
             return image, mask, NOT_SOURCE
+        if self.exclude_inactive and (mask == INACTIVE_CLASS).any():  # HC2: ineligible, draws nothing
+            return image, mask, NOT_SOURCE_INACTIVE
         rng = self.random_generator
         if self.prob <= 0.0 or rng.random() >= self.prob:
             return image, mask, NOT_DRAWN
@@ -176,4 +202,9 @@ class SynthHalfCut(A.Compose):
         half = int(rng.integers(2))
         mt, sdt = self.pool[int(rng.integers(len(self.pool)))]
         O, OM, self.last_padded = synthesize(I, mask, geo, sxj, syj, half, (mt, sdt))
+        if self.ignore_inactive:  # HC2 (a2): OM is synthesize()'s own new array
+            OM[OM == INACTIVE_CLASS] = IGNORE_VALUE
+        if (self.exclude_inactive or self.ignore_inactive) and (OM == INACTIVE_CLASS).any():
+            raise RuntimeError("synth_halfcut: exclude_inactive / ignore_inactive is on but a synthetic view holds "
+                               "inactive px")
         return np.clip(np.rint(O), 0, 255).astype(np.uint8)[:, :, None], OM, MADE
diff --git a/src/trainers/trainer.py b/src/trainers/trainer.py
index 918ab12..282f337 100644
--- a/src/trainers/trainer.py
+++ b/src/trainers/trainer.py
@@ -242,8 +242,16 @@ class Trainer:
         # HC (opt-in ``data.synth_halfcut``): per-sample outcome codes of the synthetic half-cut transform, counted per log
         # window and in total, on their own log line (the step line is unchanged).
         self.synth_on = bool(cfg.get("data", {}).get("synth_halfcut"))
-        self._synth_win = [0, 0, 0]
-        self._synth_tot = [0, 0, 0]
+        self._synth_win = [0, 0, 0, 0]  # code 3 (HC2 only): a source excluded because its mask holds inactive px
+        self._synth_tot = [0, 0, 0, 0]
+        # HC2 (opt-in ``data.synth_halfcut_exclude_inactive`` / ``_ignore_inactive``): px of the synthetic views as
+        # trained: inactive (must be 0), ignored (255; a2) and all; own line.
+        self.synth_hc2 = self.synth_on and any(cfg["data"].get(f"synth_halfcut_{k}") is True
+                                               for k in ("exclude_inactive", "ignore_inactive"))
+        if self.synth_hc2:
+            from src.data.synth_halfcut import IGNORE_VALUE, INACTIVE_CLASS
+            self._inactive_class, self._ignore_value = INACTIVE_CLASS, IGNORE_VALUE
+            self._synth_px_win, self._synth_px_tot = [0, 0, 0], [0, 0, 0]  # inactive, ignored, all
         self.exit_after_step: int | None = None  # test hook: hard-exit right after this step (simulated crash)
         # F2 CP (opt-in, set by train.py after construction): copy-paste stream and its weight; lambda 0 or no
         # stream = the plain step (no forward, no draw, no log keys).
@@ -541,10 +549,16 @@ class Trainer:
             self._pl_counts = c if self._pl_counts is None else self._pl_counts + c
             self._pl_pixels += self.con_criterion.last_num_pixels
         out = {"loss": loss.item(), "loss_sup": loss_sup.item(), "loss_con": loss_con.item(), "lambda": lam}
-        if self.synth_on and "synth" in batch:  # HC: 0 eligible not drawn, 1 synthetic, 2 not eligible
+        if self.synth_on and "synth" in batch:  # HC: 0 eligible not drawn, 1 synthetic, 2 not eligible (3: HC2)
             for c in batch["synth"].tolist():
                 self._synth_win[int(c)] += 1
                 self._synth_tot[int(c)] += 1
+            if self.synth_hc2:  # HC2: px of this batch's synthetic views, as trained
+                sm = batch["mask"][batch["synth"] == 1]
+                n = (int((sm == self._inactive_class).sum()), int((sm == self._ignore_value).sum()), sm.numel())
+                for i in range(3):
+                    self._synth_px_win[i] += n[i]
+                    self._synth_px_tot[i] += n[i]
         if self._cp_out is not None:
             out.update({k: float(v) for k, v in self._cp_out.items()})
             self._cp_out = None
@@ -825,9 +839,16 @@ class Trainer:
                     w, s = self._synth_win, self._synth_tot
                     logger.info("synth window: made %d eligible_not_drawn %d not_eligible %d | total: made %d "
                                 "eligible_not_drawn %d not_eligible %d (share %.4f, eligible %.4f, p_eff %.4f) at step %d",
-                                w[1], w[0], w[2], s[1], s[0], s[2], s[1] / max(sum(s), 1),
+                                w[1], w[0], w[2] + w[3], s[1], s[0], s[2] + s[3], s[1] / max(sum(s), 1),
                                 (s[0] + s[1]) / max(sum(s), 1), s[1] / max(s[0] + s[1], 1), done)
-                    self._synth_win = [0, 0, 0]
+                    if self.synth_hc2:  # HC2: own line (not_eligible above includes the excluded sources)
+                        pw, pt = self._synth_px_win, self._synth_px_tot
+                        logger.info("synth inactive: excluded %d synthetic_inactive_px %d synthetic_ignored_px %d | "
+                                    "total: excluded %d (share %.4f) synthetic_inactive_px %d synthetic_ignored_px %d "
+                                    "(share of synthetic px %.5f) at step %d", w[3], pw[0], pw[1], s[3],
+                                    s[3] / max(sum(s), 1), pt[0], pt[1], pt[1] / max(pt[2], 1), done)
+                        self._synth_px_win = [0, 0, 0]
+                    self._synth_win = [0, 0, 0, 0]
                 window = []
 
             if self.val_loader is not None and (done % self.val_every == 0 or done == self.total_steps):
```
