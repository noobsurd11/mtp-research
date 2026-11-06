# Download plan: public sets for picks 1 and 3 (Om OK, 4 Nov 2026)

Owner: datascout. Written before any A1 / A2 image download. The md5 of this file is frozen in `../log.md`.
Authority: `../om_2026-11-04_decisions.md` (1); team-lead message of 4 Nov; `../synth/top3.md` l.29-42.
Not approved: the A1 0.55 GB extension. No other downloads, no installs.

## Sets and targets
| Set | What | Target dir (new, empty) | Expected size |
|---|---|---|---|
| A3 | DTU figshare article 29665346: `IRT DATASET.7z` (642,610,942 B) + `README.md` (1,161 B) | `~/mtp/datasets/thermal_public/A3_dtu/archive/`, extracted with system 7z into `A3_dtu/extracted/` | 0.64 GB + extracted size (read with `7z l` first) |
| A2 | OSF ar76v `indoor_IR` folder (all 32 files) + one EL NEF per IR module (15 modules) | `.../A2_osf_ar76v/{IR,EL}/` | about 0.23 GB |
| A1 | OSF csr6t `EL-Derived_Cell_Dark_I-V` folder (all 159 files incl. `diode_fit_outputs.xls`) + 10 modules: one EL NEF, IR `<serial>_cropped.jpg`, `<serial>_cropped.txt`, raw `<date>_SHELL_M55_<serial>_180s_<A>.txt`, UVF jpg | `.../A1_osf_csr6t/{darkIV,EL,IR,UVF}/` | 3.8 MB + about 0.28 GB |

Disk rule: `df -h ~` before each set; stop and report if free space would fall below 4.0 GB (6.9 GB free at 12:43 IST).
Safety: every file is untrusted data; no code is run from inside these dirs; scripts live in `team_2026-11-04_thermal/scripts/`; Python is `~/mtp/research/.venv/bin/python -I`; A3 is extracted with the system `7z` only after its md5 matches; nothing inside the archive is executed.
Verification: size against the listing, plus md5 and sha256 against OSF's published hashes (`attributes.extra.hashes`), and md5 against figshare's `supplied_md5` / `computed_md5`. One `MANIFEST.md5` per set; summary in `download_verified.md`.

## A2: which EL file per IR module (rule fixed before download)
- IR modules = the distinct serials in `indoor_IR` (15, R: listing).
- For each, take the EL NEF whose current is closest to the IR current (IR is at 5.289 A, one module at 5.089 A). Ties: the earliest timestamp. So for most modules this is the 5.289 A NEF, the bias-matched frame.
- If a module has no EL file at all, record it and skip.

## A1: the 10 modules (rule fixed before any A1 image download and before computing any severity score)
Disclosure: to learn the layout I looked at the header and the first 3 values (cells 1 to 3 at 3.393 A, all about 0.654 to 0.656 V) of one file, `6320427218_EL-derived_cell-dark-I-V.txt`. No other values were seen.
1. **Eligible** = serials that have all of: an EL-derived dark I-V txt; an IR raw txt named `..._180s_3.39xA.txt` (current 3.392 or 3.393 A); `<serial>_cropped.jpg` and `<serial>_cropped.txt`; a UVF jpg; and an EL `.NEF` at 3.392 to 3.393 A. Serial matching uses the 9 to 10 digit number in each name.
2. **Severity score per module** (from the dark I-V txt only): each file holds, per cell (36), the EL-derived cell voltage at a set of injected currents. Take the highest current row (about 3.393 A). s = median over the 36 cells of V_cell minus the minimum over cells of V_cell, in mV. This is the voltage deficit of the worst cell at about Isc: high s = at least one cell with low EL-derived voltage (dark / inactive-like or high-Rs) [S: physics reading]. If the file layout differs from this description, I stop, describe it in the log, and amend this section before selecting (amendment logged with a new md5).
3. **Strata:** sort eligible modules by s; cut into 5 equal-count bins (quintiles; ties by serial).
4. **Pick 2 per bin** with `numpy.random.default_rng(20261104)`, drawing bins in order 1 (lowest s) to 5, `rng.choice(bin, 2, replace=False)` on the serials sorted ascending. Exception: in bin 5 the module with the maximum s is always taken, and 1 more is drawn at random from the rest of bin 5. This guarantees the most inactive-like module is in the set.
5. **Files per module:** the EL NEF at 3.393 A (if two, the earliest); the IR raw txt; the IR cropped jpg and txt; the UVF jpg (if two, the earliest).
6. The selected serials, their s and bin are written to `download_selection_A1.tsv` before the image downloads start; that file's md5 goes to the log.

## Out of scope here
- The A1 0.55 GB extension (needs Om's OK).
- Decoding NEF: pick 1 work, not part of the download. No raw decoder is installed (no rawpy / dcraw); ImageMagick and tifffile are present. Options go in `../pick1/plan_pick1.md`.
