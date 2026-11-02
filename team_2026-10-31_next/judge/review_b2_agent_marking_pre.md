# judge: B2 agent-rater plan, requirements before marker1's prereg (2 Nov 2026 11:30 IST)
**NOT FOR RATERS.** This file holds label statistics of the calibration cells. marker1 / marker2 must not read it, or anything under judge/.

Code: inline checks on names, rf masks and rf_context.tsv (gaint, CPU). No B2 panel name appears here or in any judge output.

## E: what the proposed calibration set is
- **Membership.** Hanifi `_rf` half-cells inside the 986 pool, minus b2v2_list, with hygiene = **32 cells, all from H36**.
  - The 35 Hanifi half-cells in the pool are 35 of H36's 36. Removing the 3 listed panels leaves 32.
  - The `_rf` -> pool name mapping is "strip _rf"; it reproduces the 35. Overlap of the 32 with the list: **0**.
  - All 32 are in B2-panel modules. **4 of them sit directly above or below a B2 panel cell**, so they are visible inside that panel's 512-px crop.
- **Crack reference (Hanifi, whole crop, keep).** H36's crack labels were already judged unusable for scoring (protocol_HC §2, A8 §2).
  - 14 cells >= 20 px.
  - 1,477 px in all, in 23 components: median 54 px, only 2 >= 100 px.
  - **49% of crack px lie within 10 px of a spacing / cut-line px.**
- **Target-cell vs whole crop.** Each 512-px crop shows the target half-cell plus parts of the half-cells above and below; Hanifi masks label the whole crop.
  - Only **33%** of the crack px fall in the centre half-cell (box from the gap rows).
  - Only **6 of the 14** "crack" cells have >= 20 px there.
  - Ignore (SAM scuff etc.) px fall in the centre cell for 2 of the 12 cells that have any.
  - B2's ranking score (`a`, `b_len`) was computed on the whole crop, and the user's sheet says only "mark each panel".
- **Scuff reference.** rf_context flags scuff in 8 of 32; ignore px in 12 of 32 (8,915 px). There is no scuff class in the `_rf` masks; scuff is Hanifi's SAM-made ignore region.
- **Clean crack reference available (house masks_escdd, train, no test / E1).** CSIR train cells: 47 with crack >= 100 px and 61 with 0 px. Same source family as the B2 modules, full cells.
- **Scuff masks in `scuff_masks/` are ext_scuff (E1) and test_scuff (test).** Both are forbidden for calibration.

## Requirements for the prereg (S)
1. **Fix the marking unit:** the whole 512-px crop, as B2's score and the masks use. Compute the reference on the same unit. If the user's marks are to be compared, team-lead must tell the user the same unit.
2. **Do not gate acceptance on Hanifi crack agreement.**
   - The reference is speck-level and half on cut / spacing edges.
   - A rater who marks only real cracks would "fail", and one who copies Hanifi's habits would "pass".
   - Report it descriptively.
   - Gate crack recognition on a clean house-labelled set instead: e.g. 20 CSIR train cells with crack >= 100 px + 20 with 0 px, random, seed fixed. Train only, so nothing on test / E1 is selected.
3. **Scuff gate:** Hanifi's 32 cells (scuff flag; SAM regions) are the only non-test, non-E1 scuff reference.
   - It has 8 positives, so a gate there can only reject a rater who misses most scuff (sensitivity CI ~ ±0.3).
   - State the CI. Acceptance must beat the trivial raters (all-neither, all-scuff).
4. **Rule form:** sensitivity and specificity per class with Wilson 95% CIs.
   - PASS needs the balanced-accuracy lower bound > 0.5 on the crack gate, plus pre-set point thresholds.
   - Fix how 'unsure' counts (negative) and cap the unsure share (e.g. <= 20%).
   - Fix everything before any mark exists.
5. **Blinding:**
   - Raters get name-free bundles (random IDs) of single crops at native resolution, for calibration and panels alike.
   - The ID key is held by judge / team-lead.
   - Forbidden reads for raters:
     - b2v2_candidates.tsv, pool_v2_half.jsonl, b2v2_report.txt, b2v2_hanifi_panels.txt, b2v2_gate*, overlays/, b2v2_sheet*.png (stem names in panel titles);
     - calib/data/rf masks / ignore / rf_context.tsv; rf_sets.tsv (crack_px column);
     - any m0 / dump / record / model output;
     - scuff_masks/; judge/; vetter's review (names the 3 cells); team log lines that give panel numbers.
   - Marks are md5-logged before any key or label is opened. A non-rater (judge) computes agreement, and raters get PASS / FAIL only. Without that, the 4 adjacent calibration cells leak labels into 4 B2 crops, and per-cell feedback trains the raters on Hanifi's habits.
6. **Independence:** marker1 and marker2 are two runs of one model. Their agreement measures run-to-run consistency, not inter-annotator reliability. Say so. The external anchors are the house-labelled crack gate, the Hanifi scuff check, and the user's marks if they still mark.
7. **Role conflict:** marker1 writes the guide and the rule and is also a rater.
   - It must not open any calibration label while writing.
   - The guide may not contain base rates or example labels from the calibration cells.
   - The judge computes and applies the rule.
