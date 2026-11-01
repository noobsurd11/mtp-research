# Idea 4: periodic-structure removal channel (Fourier notch / grid removal)

Author: `domain`, 31 Oct 2026. Tags: E measured (file), R literature (Research MCP id), S judgement. CPU only. No E1 data entered any number in this report. E1 images/masks were read only descriptively elsewhere: per-cell counts in `domain_out/dom_index2.tsv`, one visual montage, and idea 11's appearance table. No test cell was read.
Scripts: `ideas/scripts/` (`dom_chanlib.py`, `dom_channels.py`, `dom_line_retention.py`, `dom_crack_orient.py`, `dom_fp_classes.py`, `dom_probe.py`). Outputs: `ideas/domain_out/` (small JSON/TSV) and gaint `/home/noob/work/domain_scratch/out/`.

## 0. Verdict: DROP as a standalone arm; ideas 3 and 4 jointly PARKED (judge, accepted)
- **What works:** the channel does what Om predicted at the pixel level. It suppresses busbars, ribbons and gaps and keeps short or oblique cracks (§1.2). In a linear probe it adds the most crack and inactive information of all channels (§1.6).
- **Against it (1):** the deployed model already ignores busbars. Of FINAL's val crack false-positive px, 2% fall on ribbons, 0% on spacing and 90% on plain background (§1.4).
- **Against it (2):** it does not help scuff, the E1 failure context. Crack vs scuff stays ≤ 0.5 AUROC on the non-E1 Hanifi half-cuts (§1.3).
- **Against it (3):** it fades long cracks parallel to the axes. 480 px lines keep 32-34% of their visibility relative to oblique lines (§1.5). Idea 3's in-crop reference keeps them (0.80-0.96 vs 1.10).
- **Decision (v2):** §6's busbar/scuff kill criterion is met. The probe gate passes on its val leg only (the Hanifi leg uses unusable H36 labels). Ideas 3 and 4 are jointly PARKED.
  - nr vs fn is a trade-off, not a dominance: fn carries more probe information (val crack AP 0.0436 vs 0.0253; inactive 0.207 vs 0.062), and its axis-parallel loss touches 2.6-3.1% of crack px.
  - If one structure-channel arm is ever run, its channel is chosen by the rule written in idea 3 §7: best val probe crack AP among channels with axis-parallel 480 px retention ≥ 0.8. On current numbers fn fails (0.50-0.54) and nr qualifies.

## 1. Premise checks (E)
### 1.1 Channels tested (all label-free, per image, z-scored by median/MAD over content px)
- `raw`: −I.
- `hp`: −(I − G8(I)), masked Gaussian σ 8. This is the fair baseline: every residual channel also removes low frequencies.
- `fn`, Fourier notch: 2D FFT of `hp`. Peaks are bins where log-magnitude exceeds a 9×9 median of the spectrum by log 4, radius > 4, within 2 bins of an axis (grid structure is axis-aligned), dilated by 1. Their magnitude is set to the local median, keeping phase (Tsai et al. use a related self-reference by Fourier reconstruction, R doi:10.1016/j.solmat.2011.12.007).
- `rc`, row/column median removal: `hp` minus its column medians, then minus row medians. This removes full-length straight lines.
- `nr` / `nrL`, the in-crop neighbour reference from idea 3, shown for comparison.

### 1.2 Pixel separability (pooled AUROC, darker = higher; val 54 cells, 23 with crack ≥ 20 px; `ch_val_all.json`)

| Channel | crack vs all background | crack vs busbar/ribbon/spacing | inactive vs all | inactive vs busbar/ribbon/spacing | crack CNR (median, 23 cells) |
|---|---|---|---|---|---|
| raw | 0.817 | 0.423 | **0.946** | 0.750 | 0.64 |
| hp | 0.781 | 0.195 | 0.862 | 0.288 | 0.93 |
| fn | 0.834 | 0.632 | 0.883 | 0.713 | 1.26 |
| rc | 0.778 | 0.663 | 0.894 | 0.787 | 0.96 |
| nr (idea 3) | 0.816 | 0.671 | 0.867 | 0.740 | 1.26 |
| nrL (idea 3) | **0.836** | **0.792** | 0.926 | **0.908** | 1.07 |

- CNR = (median ring − median crack) / (1.4826 MAD ring); ring = dilate 6 − dilate 2 around the crack, non-defect px only.
- **Reading (E):** after a plain high-pass, busbars, ribbons and gaps are far darker than cracks (AUROC 0.195). The notch recovers this (0.632), and crack CNR rises 0.93 → 1.26. Against all background, the gain over raw is +0.017 AUROC.
- **Inactive:** the notch loses separability against all background (0.946 raw → 0.883). Large dark regions are low-frequency content.
- **By cell type (train, E):** multi 0.718 hp → 0.765 fn (crack vs all); mono 0.783 → 0.841; CFVS/BMRK/SDLE 0.756 → 0.812 (`ch_train_*.json`).

### 1.3 Half-cuts and scuff (non-E1 Hanifi `_rf`, 43 half-cut cells, 24 with crack, 6,523 scuff px; `ch_rf_multi_half.json`)

| Channel | crack vs all | crack vs busbar/ribbon/spacing | crack vs scuff | scuff vs all |
|---|---|---|---|---|
| raw | 0.865 | 0.805 | 0.452 | 0.861 |
| hp | 0.837 | 0.571 | 0.351 | 0.874 |
| fn | **0.904** | 0.763 | 0.435 | 0.887 |
| rc | 0.820 | 0.661 | 0.335 | 0.885 |

- **Reading (E):** on half-cuts, busbars are not the confounder (raw already 0.805 vs busbars; 9 thin busbars). Scuff is darker than crack in every channel (all ≤ 0.452). A periodic filter cannot separate a broad, non-periodic dark streak from a thin crack. Om's "should also help scuff" fails for the property that matters, telling scuff from crack.

### 1.4 Does the deployed model confuse busbars with cracks? (FINAL +0.75, calib's read-only dump; `gaint out/fp_classes.txt`)

| Set | Crack FP px | FP on plain background | FP on ribbons | FP on spacing | FN within 3 px of busbar/ribbon/spacing | All GT crack px within 3 px |
|---|---|---|---|---|---|---|
| val | 23,681 | 90% | 2% | 0% | 19% | 13% |
| Hanifi full | 14,552 | 88% | 1% | 1% | 16% | 11% |
| Hanifi half-cut | 1,316 | 26% (material 49%) | 4% | 18% | 11% | 12% |

- **Reading (E/S):** the trained CNN has already learned busbars, ribbons and gaps. Missed cracks are mildly enriched near them (19% vs 13% on val), about 700 px of 11,140 FN px. That is the upper bound of what busbar removal could recover on val. On half-cuts, 18% of the (few) FP px sit on gaps; that is 237 px over 36 cells.

### 1.5 Risk: cracks parallel to busbars or fingers (`dom_line_retention.py`, 20 crack-free val cells)
Method: a 2-px line 15 grey levels deep is inserted at the centre. Retention = line visibility in the channel relative to `hp`, median over cells.

| Channel | vertical, 64 / 128 / 256 / 480 px | horizontal, 64 / 128 / 256 / 480 px | 30° and 60°, all lengths |
|---|---|---|---|
| fn | 1.28 / 1.00 / 0.71 / 0.54 | 1.37 / 1.22 / 0.96 / 0.50 | 1.58 |
| rc | 1.74 / 1.55 / 0.91 / 0.59 | 1.81 / 1.65 / 0.65 / **0.03** | 1.90 |
| nr (idea 3) | 1.11 / 1.11 / 1.11 / 0.96 | 1.11 / 1.10 / 1.04 / 0.80 | 1.10 |

- **Reading (E):** relative to oblique lines, a 256-px axis-parallel line keeps 45-61% of its visibility under the notch, and a 480-px line keeps 32-34%. Row/column removal erases full-width horizontal lines.
- **Exposure (E, `dom_crack_orient.py`):** 40% of crack px are locally within 15° of an axis (val). Only 2.6-3.1% of crack px lie in long straight axis-parallel components (bounding box ≥ 200 px by ≤ 30 px): 17 train cells, 2 val cells, 0 Hanifi half-cuts. Pixel-level AUROC for axis-aligned vs oblique crack px moves alike under the notch (+0.050 vs +0.054 over hp, val). So the risk is real but small in this data.
- **Fingers:** at 512 px a full cell is 256 px for ~156 mm, so finger pitch (~1.5-2 mm) is ~2.5-3.3 px. Fingers are at or below the resolution limit and are not a separate periodic structure to remove (S).

### 1.6 Linear probe: information beyond a local filter bank (`dom_probe.py`, `domain_out/probe.json`)
Setup:
- Features per channel: the z-scored image, plus G_σ, Hessian eigenvalues and gradient magnitude at σ 1, 2, 4, 8 (17 features).
- Control `raw+` adds raw scales 16 and 32 (25 features), to separate "more features" from "new channel".
- L2 logistic regression trained on train px (≤ 400 positives + 600 random content px per cell), scored on all content px of val and Hanifi (scuff/star/etc. ignored). Pooled AP / AUROC.

| Features | val crack AP / AUROC | val inactive AP / AUROC | Hanifi half-cut crack AP / AUROC | Hanifi full crack AP / AUROC |
|---|---|---|---|---|
| raw | 0.0100 / 0.818 | 0.0123 / 0.949 | 0.0010 / 0.832 | 0.0049 / 0.858 |
| raw+ (control) | 0.0119 / 0.828 | 0.0168 / 0.950 | 0.0010 / 0.832 | 0.0049 / 0.848 |
| raw + fn | **0.0436** / 0.911 | **0.2069** / 0.981 | 0.0024 / 0.907 | 0.0264 / 0.943 |
| raw + rc | 0.0284 / 0.899 | 0.1419 / 0.976 | 0.0024 / 0.906 | 0.0170 / 0.937 |
| raw + nr (idea 3) | 0.0253 / 0.881 | 0.0621 / 0.966 | 0.0019 / 0.873 | 0.0258 / 0.945 |
| raw + all four | 0.0660 / 0.923 | 0.2181 / 0.979 | 0.0020 / 0.888 | 0.0511 / 0.961 |

- **Reading (E):** relative to the raw+ control, the notch multiplies linear crack AP by 3.7 on val and 2.4 on Hanifi half-cuts, so it passes the ≥ 10% gate.
- **Hygiene (E):** the Hanifi half-cut columns here and in §1.3/§1.4 use all 43 half-cuts, including the 7 CSIR_00300 cells (E1's shared module, 0 E1 crack in that module). They are descriptive filter evaluations. The gate decision does not depend on them: the val leg alone passes.
- **Reading (S):** absolute APs (0.01-0.07) are an order of magnitude below the CNN regime (FINAL val crack IoU ~0.44). A linear model cannot build "dark thin line that is not a straight full-length busbar"; a CNN can, and FINAL does (§1.4). So the probe shows the channel carries a busbar/gap indicator that local linear filters lack. It does not show a CNN lacks it. Hanifi half-cut APs (0.001-0.002) rest on tiny, speckled labels (1,792-2,855 px) and are near noise.

## 2. Prior tries in the repo
- None for Fourier or grid removal (grep for notch / Fourier / FFT / periodic over `research/`, excluding this folder). The only mention is a hypothesis about periodic structure easing MIM (`literature/notes/E01_pretraining_no_pseudolabels.md` l.5; `team_2026-10-29_features/directions.md` row 3).
- Closest tested lever: the input pipeline. P6 dropped blur and noise as crack-erasing (`protocols/P6_corrected_baseline.md`; handbook 03 §10). Track M R5 (2× resolution) addressed thin cracks by resolution (handbook 14 §3.3), not by filtering.

## 3. Literature (R)
- Tsai, Wu, Li 2012, doi:10.1016/j.solmat.2011.12.007: self-reference by Fourier image reconstruction for EL multi cells. Line/bar defect frequencies are zeroed and the difference image flags small cracks, breaks and finger interruptions. Classic, no learning, small private set.
- Li, Tsai 2011, doi:10.1016/j.solmat.2011.03.025: Fourier-domain saw-mark detection on multicrystalline wafers. Shows the method family targets line-like periodic artefacts.
- Chen et al. 2019, doi:10.1016/j.optlaseng.2019.01.016: steerable evidence filtering for EL crack detection. Hand-crafted orientation filters, the kind of local operator a CNN learns.
- Anwar, Abdullah 2014, doi:10.1186/1687-5281-2014-15: micro-crack detection in multi cells. Grain boundaries and dislocation clusters, not busbars, are named as the main confounders.
- None of these test a filtered channel as an extra CNN input against a CNN on raw pixels. That is the comparison that matters here (S).

## 4. Cost (if run anyway)
- Code: a 2-channel input (first conv summed for channel 1, channel 2 initialised as a copy or zero), a per-image notch in the loader (~30 ms/cell CPU) or precomputed channels; flips/rot90 applied jointly. About 0.5 day for builder.
- GPU: one 5-seed arm on SUP100-PF, about 12.5 lane-h on gaint (5 runs × ~2.5 h), ~5 h wall with 3 lanes.

## 5. Expected effect (S)
- Test: n.d. The model's crack FPs are not on busbars (§1.4). The FN surplus near busbars is ≤ ~6% of val FN px.
- E1: ~0. 75% of E1 crack px are in scuff + half-cut cells, where busbars are not the confounder (§1.3) and scuff is not separated.
- Inactive: risk of a small loss (§1.2).

## 6. Kill criteria
- **Model-side criterion: met (drop signal).** DROP if, on non-E1 data, (a) the deployed model's crack FP share on busbar/ribbon/spacing px is < 10%, or (b) the channel does not separate crack from scuff (AUROC ≤ 0.55). Observed: (a) 2% on val, (b) 0.435.
- **Information gate: passed (keep signal).** raw+fn must beat the raw+ control by ≥ 10% relative crack AP on val and on the Hanifi half-cuts. Observed: +266% and +140%.
- **Resolution (v2):** no standalone notch arm. Ideas 3 + 4 are jointly PARKED. The revival rule and kill (F51-based) are in idea 3 §6-7.

## 7. What would change the verdict
- A future base model whose crack FPs concentrate on gaps or busbars (for example a new cell type with 9+ busbars at a different scale). The half-cut FP split (18% on gaps) hints at this, but on 1,316 px only.
- A deployment where cells are imaged at higher resolution, so that fingers become a resolved periodic texture.

## 8. Reproduction (scripts, md5, per-cell outputs)
Scripts in `ideas/scripts/`, laptop `~/mtp/research/.venv/bin/python -I`; gaint `el-fault-detection/.venv/bin/python -I` at nice 19.

| Step | Script (md5) | Output |
|---|---|---|
| channels incl. `fn`, `rc` + AUROC | `dom_chanlib.py` (eae1b036), `dom_channels.py` (e977b074; SRC/CTYPE filters opt-in) | `domain_out/ch_*.json`, `chsrc_*.json` (pooled AUROC + `percell`: shifts, coverage, notch bins, CNR per channel, px counts) |
| line retention | `dom_line_retention.py` (3894e6de) | `domain_out/line_retention.txt` (medians over 20 cells) |
| crack orientation exposure | `dom_crack_orient.py` (426d1c1b) | stdout (§1.5) |
| FP classes | `dom_fp_classes.py` (527e6073), on calib's read-only FINAL dump | `domain_out/fp_classes.txt` (pooled; judge reproduced it from D's `d_cells.json`) |
| linear probe | `dom_probe.py` (c709b7d4) | `domain_out/probe.json` (pixel-pooled) |
| figure | inline script in the session log; uses `dom_chanlib.channels` | `figs/idea03_04_channels.png` |

Per source (raw / hp / nr / nrL / fn), see idea 3 §1.3b and `domain_out/chsrc_summary.txt`. The notch keeps its busbar gain in every source; for BMRK it acts on a single-cell crop.

---

## judge verdict (31 Oct 2026, 14:53 IST from date; report md5 67ceae9b as reviewed)

**Verdict: DROP as a standalone arm. Agreed.**
- The pre-stated model-side kill is met (E): busbar/ribbon/spacing are 2% of FINAL's val crack FP px, and crack vs scuff ≤ 0.452 on every channel.
- I reproduced the FP shares independently from D's `d_cells.json`: val FINAL b +0.75, 23,683 FP px; background 0.90, inactive 0.05, gridline 0.02, ribbons 0.02, spacing 0.00 (idea03 verdict).

**One correction to the "carried by idea 3's nr arm" resolution.**
- On domain's own data, the choice of nr over fn is not settled:
  - fn carries more probe information (val crack AP 0.0436 vs 0.0253; inactive 0.207 vs 0.062);
  - its axis-parallel loss touches only 2.6 to 3.1% of crack px in long straight components (§1.5, E).
- So nr vs fn is a trade-off, not a dominance.
- Ideas 3 and 4 are **jointly PARKED** (idea03 verdict). If a structure-channel arm is ever run, choose its channel by a val rule fixed beforehand, e.g. best val crack AP among channels with 480 px axis-parallel retention ≥ 0.8. Under that rule fn fails as computed (0.50 to 0.54) and nr qualifies. Write the rule down rather than assert it.
- The probe gate's Hanifi half-cut leg (1,792 px, H36) is uninformative, so the gate passes on its val leg alone, as domain notes.

**Tags:** E (FP shares reproduced); R (4 ids not re-resolved, no arm depends on them); S.
