# A6 duplicate tool (shared piece S3): md5, NCC and embedding searches (stage A, builder A5+A6, 14 Nov 2026)

Specs: `cards/T12_benchmark_protocol_spec.md` section 5 (leakage_audit_v02), `cards/T8_more_data_spec.md` check C0, `cards/T9_pool_teachers_spec.md` section 1.1 (`pool_t9.txt`); merged by `cards/WAVE3_REVIEW.md` Y5 and S3. Lead's ruling L2: the tool may read sealed images (legacy test 50, E1 106) as pixels only; it writes pair lists; it reads no label and no prediction of a sealed cell. Tags: E = measured here, S = judgement.

## 1. Reading rule (fixed before any search was run)

### Sets (images only)
- Labelled and evaluation sets, the 816 stems of `bench_data/meta/cells.tsv`: P532 (cv5v2 folds 0 to 4), legacy test 50 (sealed), E1 106 (sealed), the 117 `_rf` cells (F51, H36, F19, 11 "excluded"), the 11 `aux_ext11` cells. From cells.tsv only the columns stem, source, image_id, module_group, cell_id, role, bench_set, rf_set are read.
- Unlabelled pool: the 11,938 stems of `data/splits/external_unlabeled.txt` (images_512).
- External: UCF-EL, every image on disk (training/data/train, training/data/test, and the `Test_Images` files not already in those two).

### Three scores
1. **md5**: md5 of the file bytes and md5 of the decoded 8-bit grey pixels (PIL `convert("L")`). A hit = equal md5 (either kind) across two different stems.
2. **NCC** (T8 C0 descriptor, = `data_analysis/scripts/ucf_twins.py` `refined`): grey image resized to 128 px (BOX), DoG (sigma 1 minus sigma 6), row and column means removed, L2-normalised; score = dot product, max over the 8 dihedral views of the query image. BenchmarkEL-family pairs use the whole 512 px image. UCF pairs use our central cell crop (rows and columns 128 to 384) against the whole UCF image (UCF images are single cells).
3. **Embedding** (T12): DINOv2 ViT-S/14 (public weights, md5 2e405cee, Apache 2.0, timm `vit_small_patch14_dinov2`, strict load, position embedding resampled to 224 px by timm), grey copied to 3 channels, 224 px bilinear, ImageNet mean and std, CLS token after the final norm, L2-normalised; cosine, max over the 8 dihedral views of the query. Same crops as NCC for UCF.

### Thresholds
- NCC: **>= 0.80** (T8 C0).
- Embedding: **tau = 5th percentile of the cosine over known same-cell pairs** (every pair of images that share a `cell_id` in cells.tsv: the re-imaged and multi-stage cells, which include the 7 legacy test twins and CFVS_00015 / 16). Its false-alarm rate is estimated on pairs from different sources among the 816 (which cannot be the same cell).
- Pre-check (T12): AUROC of the embedding cosine, known same-cell pairs against different-source pairs, **>= 0.95**. If it fails, the embedding is used for no decision and the decisions below fall back to md5 + NCC >= 0.80 ("no new claim"). The same AUROC is printed for NCC (descriptive).

### Decisions (what each outcome does)
- **(a) labelled sets.** A pair of labelled stems is flagged if md5 matches, NCC >= 0.80, or cosine >= tau (embedding only if the pre-check passed), and the two stems are not already in the same `module_group`.
  - both in P532, different cv5v2 folds: a **new group link** (`new_group_links.tsv`). T12 rule: each link enters a `cv5v2b` split with a new md5 before the 5-seed table; screens already run on cv5v2 carry a one-line caveat. Building cv5v2b is the lead's step, not this tool's.
  - P532 with a legacy test cell: a candidate for the L-test "twins" subset (listed by id).
  - any labelled stem with an E1 cell: listed by id (E1 claims unseen modules).
  - F51, H36, F19, other `_rf` or aux_ext11 with P532: listed.
  - If the different-source false-alarm rate at tau is not small (S: the spec gives no number), the lists are printed as candidates for a visual check and the lead decides whether to apply them.
- **(b) pool.** `pool_t9.txt` = the 11,938 pool stems minus every stem that (1) shares an image id (module) with any of the 816 labelled stems (an `_rf` stem's image id is its stem without `_rf` and position), (2) has an md5 equal to any of the 816, or (3) has cosine >= tau with any of the 816 (if the pre-check passed; else NCC >= 0.80 takes its place). NCC >= 0.80 hits that are not excluded by (1) to (3) are listed separately (`pool_ncc_only.tsv`) for the lead; they are not removed. `pool_t9.meta.tsv`: stem, source, cell type, native size, sd of content px (px not equal to 0 or 255). Asserts fail closed: zero image-id overlap with every excluded set; count and md5 printed.
- **(c) UCF-EL** (exclusion lists only; nothing is trained). C0 rule: any UCF image with an md5 match or NCC >= 0.80 against any of the 816 is excluded (`ucf_exclusions.tsv`). Pass = no such pair (expected 0, different labs, T8). Embedding hits at tau are listed separately for a visual check (no spec applies the embedding rule to UCF).
- Contact sheets: the top 40 pairs per search (labelled, pool, UCF) and score (NCC, embedding), only pairs without a sealed member, to `results/stageA/dup_sheets/`. Pairs with a sealed member are listed by cell id and score only.

## 2. Numbers (all E unless marked S)

Code: `/home/noob/work/bench_wt_a` branch bench_a, commit c267c8d for the run (`bench/dup.py` ee9d46cd, `scripts/bench_dupsearch.py` 4c234b27, `tests/test_bench_dup.py` c2b57cbb, 17 tests); 81b4505 adds only a `--tau` option for the lead (script 4840914b; default unchanged). Full pytest 534 passed, 4 skipped. Weights `/home/noob/work/bench_a_io/weights/dinov2_vits14_pretrain.pth` md5 2e405cee (fetched once from dl.fbaipublicfiles.com, equal to the torch-hub copy; `SOURCE.txt`, `LICENSE_dinov2.txt` beside it).
Run: tmux `bench_a_dup`, python PID 4160106, 06:02:08 to 06:15:48 (820 s, 8 workers, CPU). Inputs: cells.tsv a50521b4, cv5v2_groups e44f0668, forbidden 9bb4d919, pool list 34d191cb, pool meta 7f3aea18. Outputs `/home/noob/work/bench_reads/stageA/dup/run1/`: summary.txt 68f269ca, summary.json f70c15cb, pairs_labelled.tsv 0fb4c040 (76,054 pairs: every pair with NCC >= 0.5, cos >= tau - 0.05, an md5 match or a known same cell), new_group_links.tsv c2a6bfc6, flagged_sealed_pairs.tsv 23fac77e (ids and scores only), pool_best.tsv 0dcf9c2e (per pool cell: module hit, md5 hit, best NCC and cosine partner over the 816), pool_t9.txt 99b47f7d, pool_t9.meta.tsv e52fc7be, pool_ncc_only.tsv bd6e9cb3, ucf_best.tsv 31542d1c, ucf_exclusions.tsv ab9d5c46, ucf_emb_hits.tsv f79b281d; features in `run1/feats/`. Contact sheets (no sealed or aux_ext11 image drawn; asserted): `results/stageA/dup_sheets/{labelled,pool,ucf}_{ncc,cos}.png`.
Sets read: 814 of the 816 labelled stems (no image on disk for `CSIR_00046_r4_c5_rf`, `CSIR_00046_r6_c1_rf`, two "excluded" rf cells not in the pool; their image id is still used by the module rule); 9 rf cells without an rf image were read from their pool copy. Pool 11,938. UCF-EL 17,064 (`Test_Images`, which holds all 11,851 train and test images).

### 2.1 Calibration (known same-cell pairs: 60 pairs of 16 physical cells; different-source pairs: 232,079)
| score | AUROC known vs different-source | known pairs min / median | different-source p99 / max | threshold | different-source FA at threshold | known pairs at threshold |
|---|---|---|---|---|---|---|
| embedding | **0.991** (pre-check >= 0.95: pass) | 0.822 / 0.941 | 0.887 / 0.957 | tau = **0.830** (T12 rule) | **6.6%** | 95% (by construction) |
| NCC | 0.994 | 0.146 / 0.817 | 0.429 / 0.849 | 0.80 (C0) | 0.04% | 53% |

### 2.2 (a) Labelled sets: flagged pairs not already in one module group (md5 / NCC >= 0.80 / cos >= tau)
| category | flagged pairs | md5 | NCC >= 0.80 | cos >= tau |
|---|---|---|---|---|
| P532 across folds (new group links) | **17,863** | 0 | 894 | 17,349 |
| P532 same fold | 4,058 | 0 | 192 | 3,937 |
| legacy test with P532 | 3,797 | 0 | 325 | 3,583 |
| any with E1 | 5,740 | 0 | 259 | 5,517 |
| P532 with F51 / H36 / F19 / rf excluded / aux_ext11 | 2,650 / 424 / 733 / 119 / 100 | 0 | 0 | all |
Descriptive (S, not a rule): no pair of labelled stems from different module groups reaches cos >= 0.99 or NCC >= 0.99 except four pairs of E1 BMRK cells among themselves. At cos >= 0.97 and NCC >= 0.80 together: 5 cross-fold P532 pairs (ARTS r1_c6 and r12_c5 cells of different modules, CFVS_00076 / 00082 r1_c1; the ARTS ones are the same pairs benchdesign's fine-texture check left as "possible same cell"), 0 test with P532, 2 E1 pairs (E1-internal BMRK).

### 2.3 (b) Pool
- Module rule: 5,091 of 11,938 pool cells share an image id with the 816 (left 6,847). md5: 10 hits, all also module hits (the pool copies of 9 rf cells and of `CSIR_00066_r11_c2`, an aux_ext11 cell).
- Embedding at tau 0.830: 11,599 hits (6,581 of them only by the embedding).
- **Rule output: `pool_t9.txt` = 266 stems** (254 multi, 12 mono), md5 99b47f7d. Asserts held: no image id of the 816, no forbidden stem, no labelled stem.
- NCC >= 0.80 not excluded by (1) to (3): 8 cells (`pool_ncc_only.tsv`).
- Descriptive (S): among the 6,847 cells left by the module rule, best cosine >= 0.99: 10 cells (6 with a P532 partner, 4 with F51); best NCC >= 0.999: 5 cells, and the sheet shows them as the same image as a labelled cell under another image id: ARTS_00012_r8_c1 = ARTS_00025_r8_c1, ARTS_00121_r1_c3 = ARTS_00120_r1_c3, ARTS_00122_r1_c6 = ARTS_00026_r1_c6 (P532), CSIR_00091_r7_c3 / r7_c6 = CSIR_00083_r7_c3_rf / r7_c6_rf (F51). At NCC 0.99 the sheet also shows a same-layout pair from two modules with different serial labels (ARTS_00046_r1_c6 vs ARTS_00040_r1_c6, 0.993), so high NCC alone is not proof. Pool cells with NCC >= 0.80 to an E1 cell: 21 (by id in `pool_best.tsv`).

### 2.4 (c) UCF-EL (C0)
md5 hits 0. NCC >= 0.80: **227 UCF images** (max 0.912; 211 of them have the same partner, `CSIR_00112_r9_c4`, a plain mono cell with 4 busbars). Embedding hits at tau: 13,475 of 17,064 (cos max 0.974). The top 40 NCC pairs on `ucf_ncc.png` are same-layout mono cells with different texture (S: no true duplicate seen).

## 3. Outcome under the rule

- **Pre-check passes** (AUROC 0.991), so by the rule the embedding is used for decisions at tau = 0.830.
- **The tau rule is unusable (said so; the decision is the lead's).** It flags 6.6% of pairs that cannot be the same cell, 17,863 cross-fold pairs (linking them would merge almost every module into one group), and leaves 266 of 11,938 pool cells (T9 expected about 9,600). By the clause fixed in section 1, the labelled lists are printed as candidates for a visual check, not applied. For the pool the rule has no such clause: its literal output is the 266-stem `pool_t9.txt`, which no pool arm can use. No threshold was changed. The cause (S): the 5th percentile of known pairs sits low because 56 of the 60 known pairs are CFVS cells re-imaged at several stress stages (cracks grow, contrast changes), and a ViT-S CLS token mostly codes cell layout (busbars, grid, source), which same-layout cells of different modules share.
- **NCC >= 0.80** is specific against other sources (0.04%) but flags many same-source same-layout pairs (894 cross-fold), and finds only 53% of known pairs. It is not a clean rule either.
- **New group links:** none applied. Candidates for a visual check: the 5 cross-fold pairs listed in 2.2 (cos >= 0.97 and NCC >= 0.80; S) and the top of `labelled_{ncc,cos}.png`. Legacy test with P532: no near-exact pair; E1: no near-exact pair with any other set.
- **Pool:** a real leak exists that the module rule misses: at least 5 pool cells are the same image as a P532 or F51 cell under another image id (NCC and cos >= 0.999). Whatever list the lead picks must drop them.
- **UCF-EL (C0):** formally the C0 pass ("no pair with NCC >= 0.80") fails with 227 hits; per the rule these 227 images are excluded and logged (`ucf_exclusions.tsv`, 1.3% of UCF). The sheet suggests they are layout matches, not duplicates (S).

Options for the lead (S; each is one command on the cached features, about 1 minute, new output folder):
1. Pool by module + md5 only (6,847 cells; keeps the 5 near-exact copies): `--tau 1.01`. Then drop the near-exact copies by hand from `pool_best.tsv`, or
2. Pool by module + md5 + embedding at a high tau, e.g. 0.99 (drops the 10 non-module cells with cos >= 0.99, which include the 5 copies; 6,837 left), or 0.98 (153 dropped; 6,694 left). Different-source pairs at cos >= 0.97: 0 of 232,079 (E); at >= 0.95: 4. Same-source same-layout false alarms are not measured by this; the sheets are the check.
3. Keep the T12 rule (266 cells): blocks every pool arm.
Command (option 2 shown):
`cd /home/noob/work/bench_wt_a && CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=1 nice -n 19 /home/noob/work/el-fault-detection/.venv/bin/python scripts/bench_dupsearch.py --out /home/noob/work/bench_reads/stageA/dup/run_tau099 --feats /home/noob/work/bench_reads/stageA/dup/run1/feats --sheets /home/noob/work/bench_reads/stageA/dup/run_tau099/sheets --workers 8 --tau 0.99`
The chosen `pool_t9.txt` then goes to `benchmark/splits/` with its md5 (T9 1.1); that copy is the lead's step.

## 4. Not run yet / not checkable
- Two rf images are not on disk (`CSIR_00046_r4_c5_rf`, `CSIR_00046_r6_c1_rf`): only the module rule covers them.
- The 159k full pool (HF `sasan/scdd-unlabeled`) is not on disk; not searched.
- No external set other than UCF-EL is on disk (ELPV, MultiSolSegment, PVEL-S not present): not searched.
- `cv5v2b` is not built (it waits for the lead's choice of links).
- Visual check of the candidate pairs is for a human; the sheets show 40 pairs per search.
