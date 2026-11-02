# A3: geometry-aware input / conditioning (busbar map, cut-line mask, cell type) (Om, 1 Nov)

arch, 2 Nov 2026. Tags: E measured (file), R literature (Research MCP id), S judgement. CPU only (one gaint CPU pass, nice 19, 1 thread, CUDA hidden). New numbers are Hanifi `_rf` only (H36 / F51); no test or E1 file opened.

## 0. Verdict (proposed): DROP. HC already removes the cut-line confusion on real half-cuts; what is left is not geometry.
1. **Can the maps be derived automatically?** Yes for most of it (§1.1): cell type by domain's frozen half-cut detector (pool recall 98.1%, labelled FP 0.86%, Hanifi half 35/36, full 0/70); cut-line position by the HC simulator's own row-profile gap finder (gap found 158/162 train multi cells; 54/54 val for SHV1); busbar columns by column profiles (idea 5 measured busbar period this way). Synthetic HC cells: exact by construction. E1: only at an opening (the detector was never run on E1; under the E1 policy it may run only inside a registered opening).
2. **Is geometry what the model gets wrong on real unseen half-cuts?** Not any more (§1.2). On H36 (36 real half-cuts, non-E1), SUP100-PF puts 123 px/run of crack FP on the cut-line / spacing class at val b_rel; **HC puts 3** (and ribbons 33 → 4). Missed crack px are not enriched near busbars / ribbons / spacing on H36 (11-12% within 3 px vs 12% of all GT crack px).
3. **On unseen full cells (F51)** structure classes hold ≤ 3% of crack FP in both arms; FP is plain background (69-85%) and inactive (13-17%).
4. **The model already segments geometry as output classes** (busbars, ribbons, spacing, border are E-SCDD target classes), and the deployed model's val crack FP on them is 2% (idea 4 §1.4). An input map repeats information the network predicts.
5. **The E1 failure is scuff + half-cut** (already-opened numbers: crack recall SUPPF s0-4 0.152, E-PF ensemble 0.127 on those 29 cells vs E-PF 0.376 on the other 77; `idea07_metrics.md` §2, `verify_pf2e.md`); scuff is not geometry, and HC on E1 moved the half-cut-without-scuff stratum by volume, not detection (+0.6 component / seed, n.d.).
- The one geometry gap nothing covers is the **9-busbar layout** (E1 / pool half-cells, period 36-39 px vs 2-5 busbars in train). Evidence it matters: none (H36 FN not enriched near busbars). idea 11 §7 already holds the revival rule (after HC, if half-cut errors cluster on busbars).

## 1. Premise check (E)
### 1.1 Automatic geometry (existing tools; E from their reports)
| map | tool | measured quality (non-E1) | source |
|---|---|---|---|
| cell type half / full | `halfcut_detector_v1` (gaint `domain_scratch`, MANIFEST b8badda4; R2b: max F(240-272) < 0.14 AND max S(140-190) ≥ 0.14) | pool half recall 989/1,008 = 98.1%; labelled FP 5/582 = 0.86%; val FP 3/54; pool full multi 3.5% (3 ARTS modules at ~1.5× crop scale); Hanifi half 35/36, full 0/70 | log 31 Oct 18:25; `idea05_synthetic_halfcut.md` §1.10 |
| cut line (gap rows) | HC row-profile gap finder (`dom_synth_val.py` 6e702c36 / `dom_synth_halfcut.py` a380a208) | gap found 158/162 train multi cells; 54/54 val (SHV1); real half-cut gap 9-11 px at 163 px pitch | idea 5 §1.2-1.3, §1.8 |
| busbar columns | column dark-line profile (calib `calib_intensity.py` dark-column counts; idea 5 busbar period) | counts / periods per cell; busbar is also a GT class on labelled cells | idea 2 §2.1; idea 5 §1.2 |
| synthetic HC cells | simulator | exact (it inserts the gap) | idea 5 §4.1 |
- Hygiene note carried over (coach, 31 Oct): the detector's R1 / R2b were computed on test images (structure only); any future use excludes test from its DEV set.

### 1.2 Where SUPPF and HC put crack FP on real unseen cells, by GT structure class (E, new)
`scripts/arch/a3_fp_struct.py` 142ac52f (adapted from domain's `dom_fp_classes.py` 527e6073; rule logged before running), gaint CPU 11:28, rc 0, reading the HC opening's syn_work rf dumps in place; output `ideas/arch_out/a3_fp_struct.txt` 64a164a7. Crack-free FA px reproduce the records' values to 0.1 px (cross-check with `arch_A6.md`).
| arm | set | b | FP px / run | on cut-line / spacing (sp multi) | ribbons | material | background | inactive | border | FN within 3 px of busbar / ribbon / spacing (all GT crack px) |
|---|---|---|---|---|---|---|---|---|---|---|
| SUPPF s5-9 | H36 | b_rel | 476 | **123 (26%)** | 33 | 110 | 211 | 0 | 0 | 11% (12%) |
| HC s5-9 | H36 | b_rel | 93 | **3 (3%)** | 4 | 30 | 56 | 0 | 0 | 12% (12%) |
| SUPPF s5-9 | H36 | b 0 | 263 | 51 (19%) | 20 | 66 | 126 | 0 | 0 | 12% (12%) |
| HC s5-9 | H36 | b 0 | 48 | 1 (2%) | 2 | 12 | 34 | 0 | 0 | 12% (12%) |
| SUPPF s5-9 | F51 | b_rel | 8,528 | sp mono 125 (1%) | 127 | 56 | 5,857 (69%) | 1,228 (14%) | 1,090 (13%) | 15% (12%) |
| HC s5-9 | F51 | b_rel | 10,117 | sp mono 75 (1%) | 177 | 50 | 8,460 (84%) | 1,271 (13%) | 53 (1%) | 16% (12%) |
- H36 crack GT is speck-level (1,792 px, judge ruling), so its FN rows are weak; its FP rows are the usable readout (as in protocol_HC).
- F51 FN near structure 15-16% vs 12% base is a mild enrichment of ~150-200 px/run out of ~4-5k FN px.
- HC's larger F51 background FP (8,460 vs 5,857 px/run at b_rel) is extra predicted volume near GT on the 12 crack cells (F51 crack-cell pred / GT 0.90 → 1.13, relP@2 unchanged; verify_hc §5), not new false alarms: its crack-free FA is 122 vs 1,231 px/run (judge).
- **Reading (S):** HC (synthetic half-cuts in training) has already taken the cut-line / ribbon confusion on real half-cuts to ~0. A geometry input would target what is left: background and inactive FP on full cells, which are not geometry.

## 2. Prior tries in the repo
- idea 4 (periodic removal; DROP / PARKED with idea 3): busbar / ribbon / spacing are 2% of FINAL's val crack FP; crack vs scuff ≤ 0.45 AUROC on every structure channel (`idea04_periodic.md` §1.3-1.4).
- idea 3 (neighbour reference channel; PARKED): extra input channel route costed (0.5-1 day, 2-channel first conv).
- idea 5 / HC (protocol_HC, n.d., mechanism passed; H36 FA 278 → 11): the half-cut geometry route as training data. HC2 (p 0.175) approved next.
- idea 11 §7: busbar-count overlay revival rule after HC.
- No CoordConv / FiLM / geometry conditioning run in this repo (grep: none).

## 3. Literature (R)
- Deitsch et al. 2021, doi:10.1007/s00138-021-01191-9: automatic EL cell / busbar structure extraction from uncalibrated module images (the projection-profile family our detector uses).
- Otamendi et al. 2021, doi:10.1016/j.solener.2021.03.058: cell-level pipeline (detect cells, then segment anomalies).
- Pratt et al. 2023, doi:10.1016/j.sasc.2023.200048: the multi-class EL segmentation benchmark (SCDD) that E-SCDD extends; its label set includes cell-structure classes, i.e. geometry as an output, as here.
- S: I found no EL paper that feeds geometry as an input channel or FiLM condition and tests unseen panels. Full text not fetched.

## 4. Cost (if run anyway)
- Dev: geometry extractor (detector + gap finder + busbar profile, jointly augmented with flips / rot90) ~1 day; 2-channel or FiLM input ~0.5 day + CPU identity (channel off = house); a frozen per-cell geometry cache for train / val / rf / HC synth; E1 / test geometry computed only at the opening.
- GPU: one 5-seed arm ≈ 12.5 lane-h (R34 peak ~6.4 GB), plus HC interplay (it would have to run on top of HC2 to be useful, i.e. two changes or a second arm).

## 5. Expected effect (S)
- On top of SUP100-PF: H36 FA down (as HC already does); E1 crack 0 to +0.01; test n.d.
- On top of HC / HC2: ≈ 0 (the cut-line FP is already ~3 px/run on H36).

## 6. Kill criterion (Om's, applied non-E1)
- "No gain on E1 half-cut stratum and Hanifi half-cells (non-E1 check first)." Non-E1 check done: on Hanifi half-cells (H36) the geometry-located FP that A3 targets is already 3 px/run under HC, and FN shows no structure enrichment. There is nothing left on the non-E1 half-cells for A3 to win. → DROP.

## 7. Protocol sketch
- None. Revival (S): only via idea 11 §7, i.e. if HC2 reports half-cut errors clustered on busbars (9-busbar layout), test a 9-busbar overlay augmentation, not an input map.

## 8. Files
| file | md5 |
|---|---|
| `scripts/arch/a3_fp_struct.py` (copy on gaint `/home/noob/work/arch/`) | 142ac52f |
| `ideas/arch_out/a3_fp_struct.txt` | 64a164a7 |

## judge verdict (2026-11-02 11:43 IST; report md5 3f4d4c57 as reviewed)
**Verdict: DROP. Agreed.**

### What I reproduced (E)
Own code on the HC opening's rf dumps + rf masks, with my own val OP: `judge/arch_a3_check.py` e4efed6c; output `judge/out/arch_a3_check_out.txt`.
- **H36 at val b_rel, crack FP on the cut-line / spacing class (class 1):** SUPPF 122.8 px/run vs HC 3.0. Total FP 475.8 vs 92.8. **Match.**
- **H36 at b 0:** 51 vs 1. **Match.**
- **F51 at b_rel, crack FP by class:** SUPPF background 5,857 / inactive 1,228 / border 1,090; HC 8,460 / 1,271 / 53. **Match.**

### Notes (S)
- **HC's F51 FP total is higher** (10,117 vs 8,528 px/run), almost all background. It sits on crack cells (crack-free FA 122 vs 1,231). This is the +25% predicted volume near GT found in verify_hc §5. It does not change A3, but don't read "FP plain background" as HC adding false alarms on clean cells.
- **The DROP rests on H36:**
  - SUPPF's cut-line confusion on real half-cuts is gone under HC (123 → 3 px/run, every seed per verify_hc);
  - missed crack px show no structure enrichment, but H36 crack GT is speck-level, so this is the weaker half;
  - F51 shows 15-16% near structure vs a 12% base, a mild enrichment of ~150-200 px/run.
- The 9-busbar revival route via idea 11 §7 is the right place for what remains.
