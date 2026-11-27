# Static prose of THESIS_TABLES.md (thesis_tables, 21 Nov 2026). No number in this file is used as a table value.

HEAD = r"""
# Thesis results tables (MTP, EL defect segmentation, 24 classes; 21 Nov 2026, revised 23 Nov 2026)

Scope: the results tables of the thesis chapter, filled by copying from result files. T = the project root; paths are relative to it.
Companion files in `T/thesis/`: `thesis_tables.tex` (the same tables as booktabs floats), `SOURCES.tsv` (each copied value with
file, line and md5), `GAPS.md` (missing numbers, disagreements between sources, wording that overstates). Generator and checker:
`build/make_tables.py` with the table content in `build/tables_data.py`.

## 0. Conventions
- **Tags.** E = measured (copied from a result file). S = judgement (only in quoted "Reading" notes, marked S). Decision words are kept
  as the sources print them: CONFIRMED, NOT CONFIRMED, PASS, FAIL, n.d., NO LOSS, NULL, "decides nothing".
- **Copy, not recompute.** No value is computed or rounded here, with one ruled exception: the E1 smallest detectable effect
  (2.80 x 0.0265 = 0.0742; T4, T8), flagged `derived = yes` in `SOURCES.tsv` with its command. Where two
  files print one quantity at different precision (for example 0.8463 in a verdict and 0.846 in a summary), the table copies one and
  cites that one. Brackets are 95% intervals unless the caption says "range over seeds" or "[min, max]".
- **Check.** `make_tables.py` stops unless (1) each anchor matches exactly one line of its file, (2) each value is a substring of that
  line, (3) each value is a substring of its own table row.
- **Machines.** Training machine = the RTX A6000 machine that trained every 5-seed CV5 row and the full-pool models and made the
  dumps of the final E1 opening; second machine = the other machine, used for part of the 2-seed screens and for some pre-protocol
  runs (T21). No read mixes models of the two machines.
- **Sealed data.** Only result text files were read (verdict.txt, read.txt, *.md). No E1 or test50 label, mask, image or dump was opened.
- **Abbreviations.** relF1@2 = crack F1 at 2 px tolerance (relP@2, relR@2 its precision and recall); mIoU-R13 = mean IoU over the 13
  robust classes; OP-A = argmax; OP-W = width-matched crack bias; M = decision margin (0.010 for relF1@2). PF = U-Net++ / ResNet-34 with
  the encoder-preserving fine-tune (the baseline); HOUSE = the same model with the plain fine-tune; HRNET = HRNet-W18 U-Net++ under the
  PF recipe; SWAD = swad_const weight averaging (readouts swad and swad_bn); D4 = 8-view flip and rotation TTA; CS / CB = HRNet + SWAD
  with readout swad / swad_bn (CB = COMBO, CS = COMBO_SWAD of the c3x read). C1 = full-pool PF; C2 = full-pool HRNet + SWAD (swad) + D4
  (the final model recipe); C3 = 5-seed ensemble of C2; E-PF = 5-seed ensemble of C1; C1-D4 = C1 with D4; S4 = C2S5 = C2 seed 5 alone.
- **Errata.** `results/FINAL_OPENING_READ_ERRATA.md` (af55915f) supersedes five readings of FINAL_OPENING_READ.md; tables and notes
  use the errata wording and cite it.
- **Scope of the headline.** The confirmed E1 claim is about the C2 recipe averaged over seeds 5 to 9, not about one checkpoint; it is
  carried by the full cells; the half-cut cells are n.d. test50 rows are context only (in-distribution, known leakage) and never a
  claim to beat Pratt 2023 or any published model.
"""

PLACEMENT = r"""
Placement (as ruled on 21 Nov, round 2):
- **Main chapter:** T4, T6, T7a, T8, T9, T10, T16b, T20.
- **Appendix:** every other table, including T21 (before the benchmark protocol).
"""

EXTRA = {}

TAIL = r"""
## 3. Considered and not tabulated
- `results/C3_S5_LOOK.md`: one seed per row, descriptive; superseded by `C3HRNET_READ.md`.
- `results/W1G_FIRST_READ.md`, `results/ROWS2_PRELIM.md`: provisional reads superseded by `W1C_READ.md`, `ROWS1_READ.md`, `ROWS2_READ.md`.
- `results/W2A_GATES.md`: gate verdicts only (ema hash PASS, swad pre-screen PASS, spd mechanism FAIL); enters T16a through W2A_READ.md.
- `results/stageA/`, `results/stageB/` (B1, B3, F2, SAMECELL), `results/stageC/` (CV5V3_BUILD, GAP_CENSUS, LABEL_VERSION_STRATA):
  protocol evidence; cited through `benchmark/PROTOCOL_v0.2.md` in T1, T2, T4 and through `benchmark/PROTOCOL_v1.0.md` in T4, T20.
- `results/stageB/U2U4_READ.md`: all descriptive; only the PF level on U2 enters T14.
- Per-source and per-class CV5 values of the final TTA read (`final_tta_read/read.txt`, `class_guard.txt`) and per-source values of
  the E1 read beyond T10: available, not tabulated.
- Pre-protocol results (P-series, Track M, PF2 to SKR2C): now T21 (appendix), traced to handbook doc 11 and, where they print the
  same string, to the cited session records.
- `thesis/RELATED_WORK.md` (f2a6adcd; gap G-N10): the related-work table (R rows read in full text, A rows abstract-level), with its
  own generator `build/related_work/gen.py`, `related_work.tex` and `RW_SOURCES.tsv`. Not repeated here; T13a keeps the published
  rows of the test50 public table.
- `thesis/INFERENCE_COST.md` (1e5a9002) sections 3.1, 3.2 and 4 (unit runs by thread count, additivity check, dump wall times
  on the training machine): available, not tabulated; T22 copies sections 3.3 and 3.4.
- `results/HOUSECS_READ.md` (9efd43ac) sections 4 to 6 (guard values, per-seed deltas, levels): available, not tabulated; T7a
  carries its contrasts and the guard items outside a bound.
- Pending, no numbers: the U2 TTA
  re-run, la_ce_full.

## 4. Regenerate
`cd T/thesis/build && python3 -I make_tables.py` rewrites THESIS_TABLES.md, thesis_tables.tex and SOURCES.tsv, and stops on any
anchor or value mismatch. If a source file changes, its md5 in SOURCES.tsv changes on the next run.
"""
