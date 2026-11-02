# B2 agent-marking bundles (judge, 2 Nov 2026)

These are name-free images for the blind B2 agent raters (`marker1`, `marker2`). The judge holds the ID key. Raters never see it.

## Contents (`MANIFEST.md5` lists every file)

| Folder | Items | IDs | What it is |
|---|---|---|---|
| `cal/` | 72 | C001-C072 | Calibration: a mix of EL cell crops in random order |
| `b2/` | 100 | P001-P100 | The B2 panels, in random order. The ID order says nothing about the panel list or the ranking |

Each item has two images, the same for every item:
- **`<ID>_v1.png`:** the 512 x 512 crop, greyscale, at native resolution.
- **`<ID>_v2.png`:** the same crop with autocontrast (1% cutoff) and a 2x Lanczos upscale to 1024 x 1024.

There is no other processing and no model output of any kind.

## How to mark (per the approved prereg, `ideas/b2_agent_marking_prereg.md`)
- **Unit:** the whole 512 px crop. Mark any crack or scuff visible anywhere in it, including in the neighbouring cells at the top and bottom edges.
- **Marks:** `scuff` / `crack` / `both` / `neither` / `unsure`, with a short note. Use the guide in the prereg.
- **Order:** calibration first, all 72, one pass, no revisions. Write `id<TAB>mark<TAB>note` lines to your own file:
  - marker1: `ideas/marker1/cal_marks.tsv`
  - marker2: `ideas/marker2/cal_marks.tsv`
- **Before telling anyone you are done:** log the marks file's md5 in `log.md`. Then message the judge.
- **Feedback:** the judge returns PASS or FAIL only. No per-item feedback, no numbers.
- **On PASS only:** mark `b2/` the same way, to `ideas/<you>/b2_marks.tsv`. md5 it in the log, then message the judge.

## Do not
- Open any file that could reveal labels, scores or names. This includes:
  - in `team_2026-10-29_features/b2_mining/v2/`: `b2v2_candidates.tsv`, `pool_v2_half.jsonl`, `b2v2_report.txt`, `b2v2_hanifi_panels.txt`, `b2v2_gate*`, `overlays/`, `b2v2_sheet*.png`, `b2v2_marks*.tsv`;
  - `calib/data/rf` masks, ignore or `rf_context.tsv`; `found/t9/rf_sets.tsv`;
  - the E-SCDD masks;
  - any m0 file, dump, record or other model output;
  - `scuff_masks/`;
  - `judge/`;
  - review files about B2;
  - log lines about B2 panels.
- Match bundle images against any other file on disk, by pixels or by md5.
- Talk to the other rater about marks.
