# Downloads verified (Om OK of 4 Nov 2026; picks 1 and 3)

Owner: datascout. Status: **all three sets complete and verified** (A3 added 4 Nov 13:4x; times in `../log.md`).
Plan: `download_plan.md` (frozen md5 409481f7 + disclosure edit, see `../log.md`); A1 selection `download_selection_A1.tsv` (md5 in log).
Root: `~/mtp/datasets/thermal_public/` (new empty dirs, created 4 Nov 12:43). Scripts: `../scripts/osf_list.py`, `osf_fetch.py`, `select_a2.py`, `select_a1.py`, `write_manifest.sh`. Nothing in the data dirs was executed; Python ran with `-I` from `../scripts/`.
Method: every file's size against the OSF listing, md5 and sha256 against OSF's published `extra.hashes`; per-file results in `<set>/<set short>_verify.tsv`; `MANIFEST.md5` per set (md5sum format, paths relative to the set dir; it also lists the verify TSV).

## Summary
| Set | Files | Bytes | Size match | md5 match (published) | sha256 match (published) | No published hash |
|---|---|---|---|---|---|---|
| A1 `A1_osf_csr6t` (OSF csr6t) | 209 | 286,886,436 | 209 | 209 | 209 | 0 |
| A2 `A2_osf_ar76v` (OSF ar76v) | 47 | 237,009,189 | 47 | 47 | 47 | 0 |
| A3 `A3_dtu` (figshare 29665346) | 2 downloaded (7z + README) | 642,610,942 + 1,161 | 2 | 2 (figshare supplied = computed md5: 7z 2ca8adbcf45639f6eefc668eceac3fe7, README 8dd0b5ce28cc856c14abb1d3d3f73fed) | not published (local sha256 of the 7z: 3af1c066...) | 0 |

Disk (`df -h ~`, free): 6.9 GB before A3 / A2 / A1 (12:43); 6.4 GB after A2; 6.1 GB after A1 images; 4.6 GB at 13:39 (other sessions' /tmp scratch, pruned after); 5.59 GB before A3 extraction (13:46, `df -B1`); 4.2 GB after A3 extraction. Floor 4.0 GB.

## A1 contents (OSF csr6t)
- `darkIV/`: all 159 items of `EL-Derived_Cell_Dark_I-V`: 158 `<serial>_EL-derived_cell-dark-I-V.txt` (13,958 B each) + `diode_fit_outputs.xls` (1,615,360 B). 3,820,724 B.
- 10 modules, chosen by the frozen rule (5 severity quintiles x 2, seed 20261104, bin 5 always takes the max). s = median minus minimum EL-derived cell voltage at about 3.393 A (mV).

| Serial | Bin | How | s (mV) | EL (NEF, 3.392-3.393 A) | IR raw (240 x 320 deg C) | IR cropped (jpg plot, txt = rot180 raw crop) | UVF | Dark I-V |
|---|---|---|---|---|---|---|---|---|
| 6330431031 | 1 | rand | 4.46 | `20220128_124740_SHELL_M55_6330431031_1s_3.393A_23.581V.NEF` | `20220124_140401_SHELL_M55_6330431031_180s_3.393A.txt` | `6330431031_cropped.jpg`, `6330431031_cropped.txt` | `20220124_151220_SHELL_M55_6330431031.jpg` | `6330431031_EL-derived_cell-dark-I-V.txt` |
| 6330431038 | 1 | rand | 4.55 | `20220127_152103_SHELL_M55_6330431038_1s_3.392A_23.850V.NEF` | `20220126_140157_SHELL_M55_6330431038_180s_3.392A.txt` | `6330431038_cropped.jpg`, `6330431038_cropped.txt` | `20220131_163838_SHELL_M55_6330431038.jpg` | `6330431038_EL-derived_cell-dark-I-V.txt` |
| 6330431484 | 2 | rand | 5.60 | `20220128_114453_SHELL_M55_6330431484_1s_3.393A_23.782V.NEF` | `20220114_151938_SHELL_M55_6330431484_180s_3.393A.txt` | `6330431484_cropped.jpg`, `6330431484_cropped.txt` | `20220126_115904_SHELL_M55_6330431484.jpg` | `6330431484_EL-derived_cell-dark-I-V.txt` |
| 6330431480 | 2 | rand | 5.04 | `20220127_150920_SHELL_M55_6330431480_1s_3.392A_24.342V.NEF` | `20220126_133702_SHELL_M55_6330431480_180s_3.392A.txt` | `6330431480_cropped.jpg`, `6330431480_cropped.txt` | `20220202_093932_SHELL_M55_6330431480.jpg` | `6330431480_EL-derived_cell-dark-I-V.txt` |
| 6320427398 | 3 | rand | 6.24 | `20220128_155358_SHELL_M55_6320427398_1s_3.392A_25.804V.NEF` | `20220121_090335_SHELL_M55_6320427398_180s_3.393A.txt` | `6320427398_cropped.jpg`, `6320427398_cropped.txt` | `20220126_101202_SHELL_M55_6320427398.jpg` | `6320427398_EL-derived_cell-dark-I-V.txt` |
| 6330431479 | 3 | rand | 6.18 | `20220128_173911_SHELL_M55_6330431479_1s_3.392A_23.802V.NEF` | `20220119_112237_SHELL_M55_6330431479_180s_3.393A.txt` | `6330431479_cropped.jpg`, `6330431479_cropped.txt` | `20220126_104235_SHELL_M55_6330431479.jpg` | `6330431479_EL-derived_cell-dark-I-V.txt` |
| 6320427793 | 4 | rand | 8.41 | `20220128_190748_SHELL_M55_6320427793_1s_3.392A_23.744V.NEF` | `20220114_095653_SHELL_M55_6320427793_180s_3.393A.txt` | `6320427793_cropped.jpg`, `6320427793_cropped.txt` | `20220126_121256_SHELL_M55_6320427793.jpg` | `6320427793_EL-derived_cell-dark-I-V.txt` |
| 6320427802 | 4 | rand | 8.14 | `20220128_151618_SHELL_M55_6320427802_1s_3.392A_24.567V.NEF` | `20220114_125108_SHELL_M55_6320427802_180s_3.393A.txt` | `6320427802_cropped.jpg`, `6320427802_cropped.txt` | `20220126_115737_SHELL_M55_6320427802.jpg` | `6320427802_EL-derived_cell-dark-I-V.txt` |
| 6320427439 | 5 | max | 19.32 | `20220128_173330_SHELL_M55_6320427439_1s_3.392A_26.174V.NEF` | `20220119_124308_SHELL_M55_6320427439_180s_3.393A.txt` | `6320427439_cropped.jpg`, `6320427439_cropped.txt` | `20220126_103656_SHELL_M55_6320427439.jpg` | `6320427439_EL-derived_cell-dark-I-V.txt` |
| 6320427227 | 5 | rand | 9.74 | `20220128_103728_SHELL_M55_6320427227_1s_3.392A_24.339V.NEF` | `20220117_130858_SHELL_M55_6320427227_180s_3.393A.txt` | `6320427227_cropped.jpg`, `6320427227_cropped.txt` | `20220126_111944_SHELL_M55_6320427227.jpg` | `6320427227_EL-derived_cell-dark-I-V.txt` |

Format notes (E, pick 1 discovery): Shell M55 = 3 x 12 cells; IR raw and A2 IR are tab-separated 240 x 320 deg C matrices; `<serial>_cropped.txt` is exactly the raw window rotated 180 deg (10/10); `_cropped.jpg` is a matplotlib plot (7200 x 4800); NEF preview 4928 x 3264 RGB 8-bit (no raw decoder installed); UVF jpg 6000 x 4000 RGB.

## A2 contents (OSF ar76v)
- `IR/`: all 32 files of `indoor_IR` (16 captures of 15 modules, jpg + txt; 5.289 A / 60 s, 408181737 at 5.089 A). 15,706,079 B.
- `EL/`: 15 NEF, one per IR module, at exactly the module's IR current (rule in `download_plan.md`). 221,303,110 B. Module 409001724 has two IR captures and one EL frame.

## A3 (DTU figshare 29665346)
- `archive/IRT DATASET.7z` (642,610,942 B) and `archive/README.md` (1,161 B): md5 equal to figshare's supplied and computed md5 for both.
- `7z l` before extraction: 1,414 files in 94 folders, 1,162,474,935 B unpacked; no absolute or `..` paths. Full extraction left >= 4.0 GB free (5.586 -> 4.423 GB by `df -B1`), so everything was extracted (team-lead rule), with the system `7z x` into `extracted/` (new dir); 7z verified every file CRC ("Everything is Ok"); 1,414 files on disk, same byte total.
- Contents by type: 640 `.raw` IR arrays (562.2 MB), 31 `.nef` EL (516.8 MB), 640 `.png` IR previews (78.0 MB), 33 `.csv` I-V, 12 `.jpg` (soiling visible images), 57 `.db` (Windows thumbnail caches), 1 `.md`.
- Defect folders (files): 01_Cell Cracks 279, 02_Cell Interconnects 283, 03_PID 214, 04_Glass Cracks 71, 05_Short-circuited Bypass Diode 250, 06_Soiling 1 158, 07_Soiling 2 157.
- `MANIFEST.md5`: md5 of all 1,416 files (2 archive + 1,414 extracted). Nothing in `extracted/` was executed or opened by any tool except 7z so far.
