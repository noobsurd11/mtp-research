# marker2 disclosures (B2 agent marking), written before viewing any bundle image

Rater: `marker2` (Claude agent; second run of the same model as marker1, see prereg §1).
Prereg used as approved: `ideas/b2_agent_marking_prereg.md` v2.2, md5 db787d03079b0a831c97fde330a69235. judge's message quoted dc84975b; judge's log line 583 (11:39) approves "as on disk md5 db787d03", which is the file I read.

No counts or labels are repeated here beyond what is needed to say what I know.

## D1. b2v2_report.txt (read in full; required by team-lead's brief)
- It describes B2 v2 as a list of crack-predicted half-cells: 90 ranked plus 10 random, with module counts, the power table and the validation AUROCs. It also gives the train-positive stems, which are train cells, not pool cells.
- The 30 Oct addendum gives aggregate Hanifi `_rf` label counts for the 35 pool half-cells (crack >= 20 px, scuff, either) and the ranking's AUROC against them. So I know a rough Hanifi base rate for part B.
- The report names no B2 panel cell.
- Mitigation: no quota, no balancing; each item is marked on its own.

## D2. Design composition known from the prereg (§5)
Part A has 40 house-labelled CSIR train cells (20 with crack >= 100 px, 20 with 0 crack px). Part B has 32 Hanifi `_rf` pool half-cells. The bundle mixes them. Both raters know this. No quota is used.

## D3. ideas.md (team_2026-10-27_unlabelled)
Lines 1-60 and the F11-F18 table rows. These contain scuff facts and the statement that 5 of 43 `_rf` half-cuts carry scuff, 4 of them with crack.

## D4. B2 / Hanifi files touched (no labels beyond what is listed)
- `b2_mining/v2/b2v2_list.txt`: `head -3` (3 stems) and `wc -l`. I don't know whether those stems are ranked or random, or which bundle IDs they map to.
- `b2_mining/v2/b2v2_marks.tsv`: `head -3`, the blank template (header plus rows "1", "2"; no marks).
- `b2_mining/v2/MANIFEST_v2.md5`: grep "png", 5 lines of md5s for gate_top20 / sheet PNGs. Files not opened.
- gaint `/home/noob/work/found/t9/rf_sets.tsv`: header plus 1 data row (`ARTS_00062_r6_c2_rf`, F19, eligible 1, module ARTS_00062, n_pool_module 41, has_pool_copy 1, crack_px 28) and `wc -l`. ARTS, outside the CSIR 297-335 pool, so not a part-B cell.
- Directory listings only: `b2_mining/`, `b2_mining/v2/`, `pool_large/`, `~/mtp/datasets/` (top level), `scdd_unlabeled_sample/` (head), `escdd_mirror_shivahanifi/` (top level), and a file count of gaint `images_512`.

## D5. Not read
- `review_suggestions_2026-10-30.md` (vetter) was never opened or grepped. I don't know which 3 Hanifi cells are B2 panels.
- I have not opened or viewed any of these: b2v2_candidates.tsv, pool_v2_half.jsonl, b2v2_hanifi_panels.txt, b2v2_gate*, overlays/, any B2 sheet PNG, any mask (house, E-SCDD, rf), rf_context, scuff_masks/, judge/, any model output, E1, test.
- I have viewed no pool or calibration image, apart from the bundle after this file's md5 is logged.

## D6. Log lines read
- `team_2026-10-31_next/log.md`:
  - the last 30 lines at 11:27. They covered B2 process lines only (team-lead 11:18 / 11:26, coach 11:22), with no panel numbers or contents, plus HC / arch / SKR2 lines with set-level F51 / H36 / F19 aggregates;
  - a grep for "prereg", printing prereg md5 and approval lines, T9 / S10 lines, and marker1's process lines (no marks).
- `team_2026-10-29_features/log.md`: `grep -o` for pool path tokens only. Output was words like "pool"; no B2 lines.

## D7. Other
- handbook 02 in full; team README; `b2_bundle/README.md`; the prereg.
- My scratch viewer script (`view.py`) was written before the rule "no own zoom". It was never run on any image and is not used.
