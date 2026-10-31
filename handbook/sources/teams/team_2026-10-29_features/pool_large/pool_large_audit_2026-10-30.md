# Large unlabelled EL pool: audit and download plan (30 Oct 2026)

Author: `poolscout` (team_2026-10-29_features), for `vetter` and the user. Tags: **E** measured here, **D** from a document, **R** reading.
Scope: metadata of the full HF dataset (all 159,332 rows, by ID, no pixels) plus a pixel sample of 599 rows. No full download. gaint: `df` and `ls` only. No model inference, no test scoring, no protocol_100 outputs opened.

## 0. Short answer
1. **HF `sasan/scdd-unlabeled` is Pratt's Dropbox pool** (E): same 9 leaf folders and file naming; all 11,993 files of our 6 Oct Dropbox download are in it under the same folder; PNG byte length equals our gaint raw file for 1,024 of 1,027 rows checked (3 differ, content not checked); 2,574 module IDs vs the README's 2,573 module images.
2. **No new cell types or sources** (E): only CSIR (22,931) and ARTS (136,401), the same 9 folders. Half-cells: 1,152, all already in our pool. No BMRK, CFVS or SDLE. No CSIR module between 400 and 2,362, so E1's later family (1095-1103, 1621-2328) is absent.
3. **What it adds** (E): 147,394 rows beyond our 11,938. 124,467 (84%) are ARTS mono 5-busbar cells, mostly native 512 px, bright and low-contrast (median mean 205, sd 24 vs our labelled ARTS 133, 41).
4. **Leakage, by ID** (E): 315 of our 582 labelled cells are in it, including **21 of 50 test** and 23 of 54 val; also all 17 `_rf` cells, 1 D7 twin, 0 of 106 E1 cells and 1 E1 module (CSIR_00300).
5. **Leakage, by content** (E): there are byte-identical copies under other module IDs. Measured: 27 such pairs within row groups. Extrapolated: about 2,400 pairs (95% bounds 1,400 to 9,500), mostly `multi/ribbons_3`, the folder holding 186 of our labelled IDs. ID-based exclusion alone is therefore not enough; a content dedupe on the full pool is required.
6. **Download** (R): it fits only on gaint (578 GB free; about 93 GB needed). The laptop has 13 GB free. Wait until protocol_100 is done (after ~10:00 IST 31 Oct). HF parquet is the only practical source.

## 1. Source facts
### 1.1 HF `sasan/scdd-unlabeled` (E: HF API, parquet footers, 30 Oct)
- **Repository:** head `7c4e73d8590a`, created 2025-05-23, last commit 2025-06-11. Public, not gated, 12 downloads.
- **Uploader:** `sasan`, profile name Sasan Jafarnejad, a co-author of Hanifi et al. (arxiv:2511.09604).
- **Card:** a `dataset_info` YAML only. No description, no licence (`license: ""`), no citation, no paper link.
- **Files:** 302 parquet shards, 76,302,557,765 bytes (156 to 1,099 MB, median 191 MB), split `train`, 159,332 rows. Per-shard sha256 is in the API (`out/hf_api.json`).
- **Columns:** `image` {bytes, path}, `label` (`<group>__<ribbons_N>`), `file_path` (`<group>/<ribbons_N>/<STEM>.png`). There is no module, supplier or date column; source and module are encoded in the stem (`SRC_<module>_r<row>_c<col>`). All 159,332 stems parse this way.
- **Parquet layout:**
  - 1,812 row groups of 100 rows (27 or 28 in a shard's last group);
  - images are stored as one snappy dictionary page per row group (8 to 220 MB, median 36 MB);
  - PNG payload 76.45 GB;
  - written by parquet-cpp-arrow 20.0.0.
- **History:** the 23 May upload (`b3eab47e`) had `image` and `label` only, with the same 159,332 rows. The 11 June re-upload added `file_path`.
- **Row order:** shuffled within folders, so a contiguous slice is not a fair sample. Consecutive rows share a module 0.4% of the time. Within row groups, Spearman(position, module id) has median 0.003, and first-half vs second-half composition gives chi2 p = 0.95.

### 1.2 Pratt's Dropbox pool (D)
- **Link** (`dataset_unlabelled/README.md`, GitHub `TheMakiran/BenchmarkELimages` @ `768b5e7`): `https://www.dropbox.com/scl/fo/05tusdgk1iip792c7a11c/h?rlkey=lwqhnniotq17ct3p5o9ovxhvv&dl=0`.
- **README text:** "over 150,000 cell-level EL images cropped from 2,573 module-level EL images. Over 2,000 of those images were sourced from one module supplier during the construction of a 911 kWp DC rooftop installation at the CSIR commissioned in 2018."
- **Supplier:** ARTS = ARTsolar (F04 census). 2,245 ARTS modules in HF fits "over 2,000 from one supplier" (R).
- **Size and tree:** not visible. The share page returns HTTP 200 but renders its listing client-side; the API needs a token.
- **Our earlier listing:** `_inventory.json` on gaint (15,388 entries). Per vetter, 4 folders stop at exactly 2,500 entries, so it was truncated. HF holds the full counts (§3.1).
- **Licence:** none. The GitHub repo has no licence file (GitHub API returns 404). The README asks users to cite Pratt, Mattheus, Klein 2023 (doi:10.1016/j.sasc.2023.200048) "for any other dataset on this repo or dropbox link".
- **Pratt 2023 §3.2** (full text read):
  - labelled cells were curated from "80,000+ images available from the five data sources";
  - module images were cropped to 512 px with "a full cell in the center surrounded by adjacent cells";
  - Future work cites "80,000+ unlabeled EL images", fewer than the later README's 150,000.

### 1.3 Hanifi et al. 2025 (D: local full text, `literature/notes/A09`)
- **Table I:** SCDD 695 labelled / **150,000** unlabelled; E-SCDD 1,000 / **151,700**.
- **151,700** = Pratt's 150,000 + their ~1,700 synthetic unlabelled images (1,768 in the text). It is not a separate count of the Dropbox pool.
- **New real cells:** the 110 described (117 released, `_rf`) came "from the original SCDD's unlabeled pool": 40 multi, 43 half-cut multi, 14 mono, 13 IBC "dogbone".
- **Cell types:** they report half-cut mono as absent from the pool.

## 2. Our pool's provenance (D, E)
| Number | What it is | Source |
|---|---|---|
| 11,993 | Dropbox files downloaded 6 Oct; 9.35 GB on gaint `sa-unetpp-ssl-el/data/unlabeled/images` | handbook 03 §6; gaint `ls` (E) |
| **11,938** | 11,993 minus 55 files whose ID is a labelled cell (48 train, 6 val, 1 test); converted to 512 px grey; `external_unlabeled.txt`. This is the "11,938-cell pool" in the suggestion | handbook 03 §6 |
| 11,219 | the "pool part" of `mim_pool_v11`: 11,938 − 463 (R1 module 413, R2 ext117 11, R3 r_hp ≥ 0.95 50, R4 0; union 463) − 256 monitor | protocol_mim5 v1.1; E: 11,219 + 256 + 463 = 11,938 |
| 11,690 | `mim_pool_v11.txt` (md5 f0a5d74a) = 11,219 + 471 train images (478 − 7 D7 twins) | protocol_mim5 v1.1 |

- **Download method** (old era, D): `download_unlabeled.py` walked the Dropbox tree depth-first with the API, capped each leaf folder at 2,500 entries, used `random.seed(42)`, round-robin over the 9 leaves, and stopped at 12,000; 7 downloads failed.
- **The cap explains the pool's skew** (R): CSIR mono 5-busbar cells make up 6.2% of their folder in HF but 0 of our 1,701 cells from that folder.
- **Is our pool a subset of the large pool?** Yes (E). All 11,993 IDs are in HF with the same folder, and byte lengths match for 1,024 of 1,027 rows checked.
- **Pool composition** (E): 353 modules (CSIR 183, ARTS 170); same CSIR rooftop source.
- **The 17 `_rf` cells:**
  - they are E-SCDD's 117 newly labelled real cells minus the 100 that are in our 11,938 (E);
  - all are CSIR, from 13 modules: `CSIR_00031_r12_c4`, `00034_r8_c3`, `00038_r11_c3`, `00038_r4_c1`, `00046_r4_c5`, `00046_r6_c1`, `00048_r10_c4`, `00051_r11_c5`, `00052_r3_c3`, `00065_r7_c7`, `00065_r8_c7`, `00115_r2_c1`, `00347_r7_c5`, `00351_r4_c6`, `00351_r5_c1`, `00361_r6_c4`, `00367_r7_c6`;
  - decision.md D4 excludes them from every unlabelled pool, and D5 makes them part of the Option A test extension.
  - All 17 are in HF. The 6 checked by content are the same images (r_hp 0.999+).

## 3. Profile
### 3.1 Full pool by ID (E: all 159,332 rows)
| Folder (busbars) | Source | HF rows | In our 11,938 | New |
|---|---|---|---|---|
| mono ribbons_0 | CSIR | 1,068 | 1,059 | 9 |
| mono ribbons_3 | ARTS / CSIR | 240 / 3,468 | 158 / 1,544 | 82 / 1,924 |
| mono ribbons_4 | CSIR | 1,920 | 1,701 | 219 |
| mono ribbons_5 | ARTS / CSIR | 126,168 / 8,340 | 1,701 / 0 | 124,467 / 8,340 |
| multi ribbons_2 | CSIR | 132 | 132 | 0 |
| multi ribbons_3 | ARTS / CSIR | 9,993 / 2,063 | 875 / 805 | 9,118 / 1,258 |
| multi ribbons_4 | CSIR | 1,116 | 1,107 | 9 |
| multi ribbons_5 | CSIR | 3,672 | 1,704 | 1,968 |
| multi_half_cells ribbons_9 | CSIR | 1,152 | 1,152 | 0 |
| **total** | | **159,332** | **11,938** | **147,394** |

- **Cell type:** 141,204 mono, 16,976 multi, 1,152 multi half-cells.
- **Busbars:** given by `ribbons_N`.
- **IBC:** `mono/ribbons_0` is probably the IBC "dogbone" set (R). 19 of the 117 `_rf` cells come from it, and Hanifi lists 13 IBC cells. Not checked visually.
- **Modules:** 2,574 (ARTS 2,245, CSIR 329).
  - Cells per module: 60 (2,251 modules), 72 (275), 144 (9; half-cell modules), others rare.
  - ARTS IDs run 1-2,246. CSIR IDs are 29-399 and 2,363-2,451.
- **Vetter's questions:**
  - No folder beyond the 9.
  - No half-cells beyond our 1,152.
  - No BMRK, CFVS or SDLE-like source.
  - No CSIR module in 400-2,362 (E1's 391-401 except 300, 1095-1103 and 1621-2328 are all absent).
- **ID collisions:** 192 stems (3 module IDs: CSIR_00029, 00053, 00056) appear in two folders. The 2 pairs checked are different images (r_hp 0.12, 0.27). So stems and module IDs are not unique keys.

### 3.2 Sample design (E)
- **Random part:** 2 rows per shard (stratified, seed 20261030), positions 0-49 of a row group. Position is random (§1.1), so this restriction does not bias the sample.
- **Targeted part:** 37 rows whose ID matches one of our labelled, `_rf`, duplicate-stem or CSIR_00300 cells. Used for verification only, never for rates.
- **Method:**
  - row-group footers were read with HTTP range requests;
  - each PNG was located by walking the snappy fragments, then decoded exactly;
  - every PNG chunk CRC was recomputed;
  - images were decoded with PIL/numpy under `python -I`.
- **Fetched:** 599 of 641 rows (566 random, 33 targeted). 42 rows could not be located (38 random, 4 targeted: val `ARTS_00152_r12_c5` and `ARTS_00160_r11_c1`, test `ARTS_00001_r6_c2`, D7 twin `ARTS_00081_r5_c1`). 33 of the failures are in `multi/ribbons_3`, whose pages snappy-compress about 0.8%, which defeated the walk.
  - Failure depends on row position, so the 13 `multi/ribbons_3` rows fetched are still random within their folder.
  - Rates are post-stratified by folder (folder sizes are known exactly) with a stratified bootstrap 95% CI. Zero counts use the Wilson upper bound (0.67%, ≤ 1,074 rows).
- **Check of the method:** the estimated share of rows in our 11,938 by ID is 6.99% [5.45, 8.69]; the true share is 7.49%.
- **Files:** rows and md5s (PNG bytes, decoded pixels, 512 px grey) in `out/sample_index.tsv`; images in `/home/yugma/mtp/datasets/scdd_unlabeled_sample/r<global_row>.png` (599 files, 293.6 MB).

### 3.3 Pixel profile (E, random 566, post-stratified; N = 159,332)
| Property | Estimate | 95% CI | Rows |
|---|---|---|---|
| Format | PNG, RGB, 8-bit (colour type 2), non-interlaced: 566 / 566 | ≥ 99.3% | all |
| Native 1200 x 1200 (rest 512 x 512; no other size) | 16.1% | 14.0-18.1% | 25.6k [22.4k, 28.8k] |
| Near-grey (channel max diff median 5); > 1% pixels with channel diff > 16 | 2.9% | 1.7-4.5% | 4.6k |
| Decode failure / CRC error | 0 / 566 | ≤ 0.67% | ≤ 1,074 |
| Near-blank (sd < 5 on 512 px grey) | 0 / 566 | ≤ 0.67% | ≤ 1,074 |
| Low contrast (sd < 10) | 3.3% | 2.0-4.7% | 5.2k |
| White padding (> 30% of pixels = 255; module-edge cells) | 5.2% | 3.4-6.9% | 8.2k |
| Dark border (black padding) | 0 / 566 | ≤ 0.67% | |

- **Crop style:** the cell is centred, with parts of the neighbouring cells around it. This is the same framing as the labelled 512 px images (Pratt 2023 §3.2). Edge cells are padded white. See `out/montage_random24.png`.
- **Size by folder (sample):** `mono/ribbons_5` 471 of 505 native 512 px; `multi/ribbons_3` 13 of 13 and `multi/ribbons_4` 3 of 3 native 1200 px.
- **Intensity, 512 px grey, median (mean / sd / mean |Laplacian|):**

| Group | mean | sd | lap |
|---|---|---|---|
| HF ARTS 512 px (n 461; most of the new data) | 205 | 24 | 5.5 |
| HF ARTS 1200 px (n 19) | 128 | 30 | 8.2 |
| HF CSIR 1200 px (n 44) | 145 | 50 | 5.4 |
| HF CSIR 512 px (n 42) | 147 | 35 | 3.3 |
| ours, train ARTS (162) | 133 | 41 | 9.3 |
| ours, train CSIR (111) | 141 | 45 | 5.7 |
| ours, train CFVS / BMRK / SDLE | 170 / 221 / 225 | 50 / 61 / 59 | 4.4 / 2.7 / 2.9 |
| E1 CSIR (101) | 190 | 55 | 3.0 |

- **Reading** (R):
  - HF CSIR 1200 px cells look like our labelled CSIR cells.
  - The bulk of the new data (ARTS 512 px) is brighter and has about 60% of the labelled ARTS contrast. This is the native-512 px mismatch already noted for our pool (handbook 03 §6).
  - Nothing in the pool resembles E1 (bright, high contrast, half-cut, scuffed).

## 4. Overlap and leakage
### 4.1 Exact, by ID, full pool (E)
| Our set | IDs in HF | Modules in HF | HF rows in those modules |
|---|---|---|---|
| train 478 | 271 | 169 / 322 | 11,750 |
| val 54 | 23 | 20 / 49 | 1,428 |
| **test 50** | **21** | 20 / 48 | 1,338 |
| E1 106 | **0** | 1 / 71 (CSIR_00300) | 144 |
| ext117 | 11 (the 11 already in our pool) | 9 | 1,168 |
| 17 `_rf` | **17** | 13 | 900 |
| D7 twins 7 | 1 (`ARTS_00081_r5_c1`) | 1 | 78 |
| val ∪ test ∪ E1 modules (159) | | 36 | 2,550 |

- **Test IDs in HF:**
  - ARTS: `00001_r6_c2`, `00020_r5_c1` (D7 twin cell), `00020_r7_c3`, `00023_r7_c4`, `00030_r8_c6`, `00047_r3_c1`, `00051_r3_c2`, `00073_r4_c2`, `00076_r6_c1`, `00078_r11_c6`, `00145_r5_c2`, `00152_r9_c3`, `00166_r4_c2`;
  - CSIR: `00055_r7_c4`, `00057_r8_c6`, `00070_r8_c4` (the noisy cell), `00092_r8_c4`, `00166_r2_c4`, `00173_r4_c4`, `00200_r4_c6`, `00201_r4_c6`.
  - Only 2 CSIR/ARTS labelled cells are absent from HF (`ARTS_00007_r12_c1`, `CSIR_00290_r11_c5`).
- **Same ID, content check** (targeted rows):
  - 26 of the 27 targeted rows that have a same-ID reference are the same capture as our labelled or `_rf` image: r_hp 0.998-0.9998. They are 5 test, 3 val, 6 train, 6 `_rf` 17 and 6 `_rf` in-pool rows. The other 6 targeted rows (duplicate stems, CSIR_00300) have no same-ID reference.
  - No md5 match: the labelled images were re-processed by Pratt (512 px RGBA).
  - Exception: val `CSIR_00127_r11_c5` scores r_hp 0.52, so it is a different image under the same ID. Its HF bytes equal our Dropbox file (2,477,079 B).
- **E1:** the only shared module is CSIR_00300 (144 half-cells; all are in our pool already, and R1 dropped them from `mim_pool_v11`). E1's cell `CSIR_00300_r25_c1` lies outside HF's r1-24 grid.
- **Module rule caveat:** module IDs collide across folders (§3.1). A module rule must be folder-qualified, or must drop both modules.

### 4.2 Exact, by content (E)
- **Within-row-group byte duplicates:** the image column is dictionary-encoded per row group. Over all 1,812 row groups there are 159,305 distinct PNGs for 159,332 rows, so 27 rows (23 row groups) are byte-identical to another row.
- **What the duplicates are:** every pair is the same cell position under two module IDs, e.g.:
  - `CSIR_00081` = `CSIR_00087` (8 pairs);
  - ARTS 00018/00019/00031/00032 (one cluster);
  - ARTS 00012/00025, 00120/00121, 00136/00137, 00111/00113, 00134/00135, 00147/00148;
  - `CSIR_00083` = `00091`; `CSIR_00029` = `00130`.
  - This is the same phenomenon as the known `CSIR_00107_r9_c3` = `CSIR_00117_r9_c3` (decision.md D4) and very likely the D7 twin `ARTS_00020_r5_c1` ~ `ARTS_00081_r5_c1` (r_hp 0.997).
- **Extrapolation:** rows are shuffled within folders, so P(a duplicate pair shares a row group) is known per folder.

| Folder | Observed pairs | Estimated pairs (95% CI) |
|---|---|---|
| multi ribbons_3 | 18 | 2,284 (1,354-3,610) |
| multi ribbons_4 | 9 | 108 (49-205) |
| others | 0 | 0 (upper bounds 6 to 5,213; mono ribbons_5 is uninformative) |

- **Reading** (R): about 38% of `multi/ribbons_3` rows (CI 22-60%) have a byte-identical twin under another module ID. That folder holds 186 of our labelled IDs, including ARTS test cells. **A test cell can sit in the pool under a different ID.** Only a full-pool content check (md5 + r_hp) closes this.

### 4.3 Near-duplicates (E, random sample)
- **Metric:** r_hp, the Track M variant (`trackM/data_addendum.md`):
  - our pool pipeline: grey, then area-resize to 512;
  - 4x4 mean to 128 px;
  - minus a Gaussian blur (σ 3), z-scored, Pearson.
- **Calibration on our split:**
  - the 7 D7 twins score 0.935-0.997 (Track M: 0.934-0.998);
  - the best non-twin same-source match for each test cell has median / max of 0.81 / 0.94 (ARTS), 0.88 / 0.95 (CSIR), 0.87 / 0.93 (CFVS), 0.94 / 0.98 (BMRK).
- **Thresholds:** ≥ 0.98 = copy; 0.95-0.98 = check visually.
- **Not the same as agent 4's metric:** agent 4's `neardup.py` (the r_hp behind `mim_pool_v11`) is on gaint only and was not read (ls-only rule). My values differ from its `lab_pairs` values by up to 0.17, so its thresholds do not transfer.

| Against | r_hp ≥ 0.95 | r_hp ≥ 0.98 | max |
|---|---|---|---|
| any labelled 582 | 4 / 566: 0.67% [0.17, 1.34] ≈ 1,065 rows [266, 2,131] | 1 / 566 | 0.985 |
| val, test, E1, 17 `_rf` | 1 / 566 (test `ARTS_00047_r3_c1` vs HF `ARTS_00044_r2_c1`, 0.960) | 0 | 0.960 |
| E1 106 | 0 (≤ 1,074 rows) | 0 | 0.81 |
| 17 `_rf` | 0 | 0 | 0.88 |
| exact md5 of 512 px grey, any of 816 references | 0 | | |

- **Visual check** (`out/montage_ge095_pairs.png`): none of the 4 pairs is a copy.
  - Same module, different row (CSIR_00227 r5 vs r2; CSIR_00059 r2 vs r6, where the train cell has a crack the pool cell lacks).
  - Same position in an ARTS module edge column. This is the D4 "shading family"; ARTS_00047_r3_c1 was already a D4 top candidate.
- **Within the sample:** 77 pairs ≥ 0.90, mostly ARTS at the same position, and 0 identical md5.
- **Reading** (R): random pool rows rarely look like our labelled cells, and never like E1. The leakage risk is the direct ID hits (§4.1) plus the duplicate-ID copies (§4.2), not chance near-duplicates.

## 5. Disk and time (E unless marked)
- **Free space:**
  - laptop `/`: 272 G, 13-15 G free (96%), so a full download cannot go there;
  - gaint `/` (home is on the same filesystem): 1.6 T, **578 G free**; 48 CPUs (`ls /sys`).
- **Size:**
  - parquet: 76.3 GB;
  - extracted PNGs: about 76.4 GB (the page payload);
  - 512 px grey PNG (our pipeline): 103 KB per row (post-stratified), about **16.5 GB**;
  - r_hp descriptors in fp16: 5.2 GB.
  - Total on gaint: about 93 GB, or about 170 GB if extracted native PNGs are also kept (not needed).
- **Download time:** the laptop measured 0.9-1.5 MB/s per stream from the HF Xet CDN, with 1-6 s request latency. gaint bandwidth was not measured (no processes allowed).
  - 76.3 GB at 1 MB/s takes 21 h; at 10 MB/s, 2.1 h; at 50 MB/s, 25 min (R).
  - A one-shard timed test (~190 MB) on gaint is the first step.
- **CPU:**
  - decode + 512 px grey + descriptor: median 30 ms (1200 px) and 7.6 ms (512 px) per image on the laptop, about 0.5 core-hour for all rows;
  - query matmul (≈ 12.8k reference cells × 159k × 16,384 × 2 FLOP ≈ 6.7e13): about 3 min at the laptop's measured 429 GFLOP/s;
  - optional all-pairs inside the pool (4.2e14 FLOP): about 16 min;
  - md5 of all PNGs: I/O-bound, about 76 GB of reads.
- **This audit's download:** about 0.43 GB of data:
  - manifest 9.0 MB;
  - sampling about 390 MB in 3 runs;
  - tests and debugging about 30 MB;
  - API, HTML and README under 1 MB.
  - A pip install (`pip install --no-cache-dir pyarrow numpy pillow`) into a throwaway venv `pool_large/.venv` completed, not aborted as first reported. It installed pyarrow 26.0.0, numpy 2.5.4 and pillow 13.0.0 (wheels 77.8 MB). The venv was deleted unused. All traffic was therefore about 0.51 GB, over the 0.5 GB cap if tooling counts; data alone is 0.43 GB.
  - Nothing else changed: no user-site or system packages, no pip cache, no `/tmp/pip-*` left, the research `.venv` has no file modified this session, and `pip check` there is clean.
  - The sample directory holds 293.6 MB and can be deleted when no longer needed.

## 6. Download plan (for approval; nothing started)
1. **Source: HF parquet.**
   - It is a verified mirror (§0.1) with per-shard sha256, ranged and resumable downloads, and a stable revision (`7c4e73d8`).
   - The Dropbox needs an API token, a full tree walk and per-file requests (about 159k); our last walk was capped and truncated.
2. **Target:** gaint, under the user's account, `/home/noob/work/datasets/scdd_unlabeled/7c4e73d8/` (raw shards) plus `.../cells512/` (converted).
   - Not before protocol_100 finishes (~10:00 IST 31 Oct) and the user confirms.
   - Run under `nice -n 19 ionice -c3` with a bandwidth cap (e.g. 20 MB/s), and never touch the f100 tmux session or root's `finllm_chat.py`.
3. **Checksums:**
   - sha256 of every shard against the HF LFS oid (`out/hf_api.json`);
   - row count 159,332;
   - footer schema;
   - store a `MANIFEST.sha256`.
4. **Matches the Dropbox pool:**
   - for the 11,993 rows whose IDs are in our gaint raw download, md5 of the PNG bytes must equal md5 of `sa-unetpp-ssl-el/data/unlabeled/images/*` (byte lengths already agree for 1,024 of 1,027);
   - optionally, one Dropbox API listing (token needed) to confirm no file outside the 9 folders.
5. **Dedupe** (pre-declared; drop the union):
   - **D0 ID:** any of our 582 labelled (including the 7 D7 twins), E1 106, ext117 and the 117 `_rf` (including the 17). That is 443 HF rows now (315 labelled + 117 `_rf` + 11 ext117).
   - **D1 module:** (folder, module) of every val, test and E1 cell: 36 modules, ≤ 2,550 rows. Or ID-wide if the user prefers caution.
   - **D2 byte or pixel copy:**
     - md5 of PNG bytes and of the decoded 512 px grey equal to any D0/D1 row or any labelled, E1 or `_rf` image;
     - then drop copies of those copies, as the transitive closure over md5 groups.
   - **D3 content:**
     - r_hp ≥ 0.95 to any val, test, E1 or 17 `_rf` cell (expected ≈ 0.2%, ≤ 800 rows);
     - r_hp ≥ 0.98 to any train cell (copies only);
     - re-check with agent 4's samepos full-res screen for ARTS.
   - **D4 within the pool:** keep one row per md5 group (≈ 2,400 pairs expected); optionally cluster at r_hp ≥ 0.98.
   - Report counts per rule, as `build_mim_pool.py` does, and keep a list of dropped rows with reasons.
6. **Profiling pass:** per row, native size, mode, mean, sd, p1, lap, white-padding share and low-contrast flag. Tables by folder, source and module; compare with the 582, E1 and our 11,938.
7. **Licence and usage:**
   - no licence on either the Dropbox or the HF mirror; the README asks for citation of Pratt et al. 2023;
   - use is research-only in the thesis, citing Pratt 2023 (and the HF mirror as the channel);
   - do not redistribute images or a derived pool.
8. **Use:**
   - keep the pool-size SSL arm separate from protocol_100 (handbook 03 §6 pool mismatch);
   - declare its source mix: the new data is 84% ARTS mono 5-busbar, mostly 512 px and low contrast.

## 7. Open questions (user or vetter)
1. **Approve the download to gaint after protocol_100?** At what bandwidth cap, and keep the raw shards or delete them after conversion?
2. **D1 module rule:** folder-qualified or ID-wide? ID-wide is more conservative given the ID collisions.
3. **Thresholds:** keep r_hp 0.95 for held-out sets, or adopt agent 4's `neardup.py` definition after reconciling? The two metrics differ by up to 0.17.
4. **Pretraining set:** all 159k, or a source-balanced subset? 124k of the new rows are ARTS mono 512 px, while E1 is CSIR half-cut and scuffed.
5. **Item 7 (targeted labelling search):** the pool adds no half-cells, no scuff-rich CSIR modules and no E1 modules, so a scuff or half-cut search has nothing new to mine. A crack search in ARTS mono 5-busbar cells is possible.
6. **Existing claims:** do any past "x" arms need a note? The old 11,938 pool held 0 test IDs after the 6 Oct filter, but byte copies under other IDs were never screened in that pool beyond R3.

## 8. References and files
- **Papers** (Research MCP ids):
  - doi:10.1016/j.sasc.2023.200048 (Pratt, Mattheus, Klein 2023; full text §3.2 and Future work);
  - arxiv:2511.09604 (Hanifi et al. 2025; local full text);
  - arxiv:2402.17611 (Torpey, Pratt, Klein 2024; abstract only; a 22k unlabelled set).
- **Web:**
  - HF API `api/datasets/sasan/scdd-unlabeled` (+ `/commits/main`, `/tree/b3eab47e3a`);
  - datasets-server `/info`, `/size`, `/rows`;
  - GitHub raw `dataset_unlabelled/README.md` @ 768b5e7;
  - Dropbox share page (HTML only).
- **Scripts** (`pool_large/scripts/`, stdlib + numpy/PIL/scipy, `python -I`):
  - `pq_lite.py` (Thrift, snappy, ranges), `manifest.py`, `analyze_manifest.py`, `build_refs.py`;
  - `select_targets.py`, `sampler.py`, `dict_probe.py`;
  - `calib_rhp.py`, `profile_overlap.py`, `estimate.py`, `poststrat.py`.
- **Outputs** (`pool_large/out/`):
  - `manifest.tsv` (159,332 rows, md5 25a553f1), `manifest_profile.json`, `id_overlap.tsv`, `rowgroups.json`, `dict_probe.json`;
  - `targets.tsv`, `sample_index.tsv` (rows and md5s, md5 85f138a7), `sample_profile.tsv`, `sample_matches.tsv`;
  - `estimates.json`, `poststrat.json`, `calib_rhp.json`, `ref_stats.tsv`;
  - `gaint_raw_ls.txt`, `montage_*.png`, `hf_api.json`, `refs.json`.
