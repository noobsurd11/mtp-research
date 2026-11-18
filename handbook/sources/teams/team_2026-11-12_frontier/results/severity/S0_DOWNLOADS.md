# S0 downloads: Polenghi et al. 2026 and ELPVPower

Severity track builder, 15 Nov 2026, 21:47 to 22:27 IST, on gaint. Tags: E = measured (file given), R = dataset page or paper, S = judgement. Both downloads approved by the user on 15 Nov (as relayed in the lead's task); use is inference and analysis only, nothing trains a model, nothing is redistributed.
Full READMEs (source, DOI, licence text as found, date, file list with md5): `~/mtp/datasets/severity_public/polenghi/README.md` and `~/mtp/datasets/severity_public/elpvpower/README.md`. Fetch log: `bench_reads/severity/S0/fetch*.log`.

## 1. Rule for this item (the task's criteria as applied; written down at 22:26, after the fetch)
Fetched = every file of the repository's file list present and passing the publisher's own checksum. Licence = quoted from the repository record and from any licence file in the set; a version not stated is reported as unverified. Contents = counted from the files, not from the papers. A set behind a form, a login or a bot check is not forced.

## 2. Outcome
| | Polenghi et al. (P564) | ELPVPower (P263) |
|---|---|---|
| Repository, DOI | Mendeley Data pxyzzkbs4b v1, 10.17632/pxyzzkbs4b.1 | Juelich DATA, 10.26165/JUELICH-DATA/TVWUUP v1.3 |
| Fetched | **yes**: 260 of 260 files, 1,375,487,839 B, all sha256 OK | **yes**: 721 of 721 files, 337,749,355 B, all sha256 OK |
| Licence as found | **CC BY 4.0**: repository field "Creative Commons Attribution 4.0 International" and `LICENSE.txt` ("licensed under the Creative Commons Attribution 4.0 International License (CC BY 4.0)") | **CC BY, version not stated**: Dataverse record `"license": "CCBY"`, no terms of use; no licence in the release README; landing page behind a bot check (not passed). Version unverified |
| What it is | 2 small poly devices (CellID 0.1, 0.2; 4.5 Wp, 130 x 150 mm; by eye a 10-strip mini-panel), 84 cumulative damage stages (38 + 46) | 719 EL images of whole modules (6 x 10 multi cells), 137 module instances, 3 module types |
| Images | per stage EL + near-IR BW + visible HDR, rectified, EL and BW pixel-aligned; about 2,950 x 2,560 px at 500 DPI | 900 x 1,500 px per module (about 148 px per cell), globally rescaled to [0, 255] |
| Electrical quantity | one operating point per stage under a halogen lamp (about 50 W/m2): V, I (mA), P = V x I (mW), "Power_output_loss [%]" 0 to 100; no I-V curve, no Isc, Voc, Pmpp | measured Pmpp (`peak_power`, W) and nominal power (175 / 230 / 240 W) per image |
| Organisation | two dependent series (damage added step by step); per stage: degradation level, damage kind (mechanical 47, thermal 16, dirt 13, electric 6), damage cause, new-damage bounding box, free text | repeated measurements: 21 instances x 1, 98 x 2, 8 x 3, 10 instances with 33 to 51 (mechanical load series, pressure 26 levels); excitation high 646 / low 73; the paper's 5 folds as columns |
| Masks | none | none |
| Code | none in the set | github ma0ho/elpvpower @4066805: 11 source files fetched (no checkpoints); no licence file; **no cell cutting** (whole-module regression; pvinspect used only for a visualisation with rows=6, cols=10) |

## 3. Reading (S)
- **Polenghi** is a damage-progression record of two devices, not a cell population: any severity statistic on it has n = 2 independent units. Its value here is as a worked example (does predicted inactive area rise stage by stage as P falls on one device?), and its abrasion / scrape stages as a public look at surface damage; it cannot validate a power band. The power is a single operating point at about 50 W/m2, not STC Pmpp. Our models never saw 10-strip mini-panels or 3k px images, so inference needs cell-strip cropping and resizing first.
- **ELPVPower** is the only one of the two with measured Pmpp on full-size modules. Its cells are about 148 px, so using our 512 px models means upsampling about 3.5x, against BMRK cells that are ELPV cells downscaled and padded; crack labels of 1 to 2 px at 512 would be sub-pixel at 148 px. T12 item 8's gate (b) (automatic cell cutting with >= 95% usable cells on a 20-module pilot) and gate (c) (no ELPVPower module among BMRK training cells) are still open; the rectified 6 x 10 layout makes (b) look easy (S), (c) is untested.
- Results on ELPVPower must carry "licence version unverified" until the CC BY version is confirmed from the landing page or the authors' paper (the paper says the data are public, R P263, per the T12 spec).

## 4. Owed
- ELPVPower licence version: read the landing page from a normal browser (the bot check needs JavaScript), or the paper's data statement. Until then: "analysis only, terms unverified (CC BY, version not stated)".
- T12 item 8 is not run: gates (b) and (c) first; inference on about 43k cells is a CPU job of hours (S) or a GPU job to be prepared for the lead.
- Not fetched by choice: the 6 ELPVPower model checkpoints (535 MB; not needed for our analysis).
