# AI-rater check of the audit's label-error candidates: result (lead, 21 Nov 2026)

Rule: PREREG.md (bf7226e4, frozen before rating; no amendments). Scorer scripts/score.py (cfe5b91d). Full output: out/score_report.txt,
out/candidate_verdicts.tsv, out/calibration_items.tsv. E = measured by the scorer, S = judgement.

## Run record
- Raters: 3 fresh agents, model claude-opus-5-5, in-process subagents of the lead session, each split into 3 sessions (cap 62 panels
  per session), bundle /home/noob/work/bench_int_io/rater/bundle/ only, launch prompt = the designer's, no audit numbers.
- Files (184 of 184 IDs each, 4 fields, no duplicate, order kept; md5 logged before unsealing): r1 f163b9bb, r2 0c556a53,
  r3 8f4d6886 (ratings/RATINGS_MD5.txt). Key unsealed 21 Nov 05:20 (chmod 700); tripwire `stat -c %X key/key.tsv` = 1795212939 as
  recorded (key not read before scoring); key md5 fe33e960 as recorded.
- Deviations (none changes a rating rule; no rater replaced):
  1. Session cap overshoot: r1 session 2 rated 74 panels (12 over), r2 session 2 rated 68 (6 over; its 69th append was then refused
     by the session's permission check, nothing written). The cap is a session-length control, not a reading rule; the extra lines
     were rated the same way and kept (the brief forbids edits). Ruled and logged before unsealing.
  2. Scratch writes outside the bundle: r1 (done.txt, a list of its own rated IDs, to find its resume point) and r3 (ids.txt, its
     own IDs, after rating, for a final check). Neither holds key or audit information; neither is a read of forbidden material.
     r1's was ruled before unsealing; r3's was reported in its final report, read before unsealing, and judged the same way (S),
     but its log line was written after scoring.
  3. r2 session 2 viewed two panels (ERXLC, KCELN) without rating them; session 3 rated them after a second look.

## Calibration (60 blind items with known answers; E)
- Every rater alone: sensitivity 29/30, specificity 30/30. Majority: sens 0.967 [0.833, 0.994], spec 1.000 [0.886, 1.000],
  Youden J bootstrap lower bound 0.900; Fleiss kappa 1.000 on these items. Per plant type: all majority-correct except one crack FAKE
  in the label (rated ambiguous).
- Caveat (PREREG section 8, S): planted items are cleaner than real candidates, so these numbers are probably optimistic for the
  candidates; the three raters are runs of one model (consistency, not independent reliability).

## Pre-registered decision (E)
| Class | Gates G1 to G4 | Majority label-error share | Corrected for rater sens/spec | Pre-registered reading |
|---|---|---|---|---|
| crack (F5), 78 candidates in 39 cells | all pass (sens 0.944, spec 1.000; J lb 0.833; 3 of 3 alone; kappa 0.674) | 18/78 = 0.231, cell-bootstrap [0.099, 0.405] | 0.244 [0.105, 0.436] | **MEASURED: label errors exist but are a minority of the image-supported candidates** |
| inactive (F4), 46 candidates in 14 cells | all pass (sens 1.000, spec 1.000; J lb 1.000; 3 of 3; kappa 0.844) | 10/46 = 0.217, [0.081, 0.526] | 0.217 [0.081, 0.526] | **MEASURED: label errors exist; whether they are most is undetermined** |

Uncalibrated shares (S; only the label-error call is calibrated):
- crack: ambiguous 46, model error 11, convention 1, no majority 2. By type: missed crack 9/46 label error (32 ambiguous); spurious
  crack 9/32. By source: CSIR 13/41, CFVS 1/26 (20 ambiguous), BMRK 2/7, ARTS 2/4.
- inactive: model error 30, ambiguous 5, no majority 1. By type: **missed inactive 5/6 label error**; **spurious inactive 5/40
  label error, 30/40 model error**.
- px-weighted label-error share: crack 0.425, inactive 0.300 (descriptive).

## What this changes in REPORT.md (S)
- F5 (crack label errors) goes from suggestive to measured, in this form only: of the 78 image-supported crack candidates, about a
  quarter (corrected 0.24 [0.11, 0.44]) are label errors by 3 calibrated AI raters; most of the rest are ambiguous at this
  resolution. It is not a count of all label errors in the pool. F5's earlier result (crack label errors move no contrast by more
  than 0.003) stands.
- F4 (inactive): the raters call 30 of 40 spurious-inactive candidates model errors, i.e. the label is right there. So F4's
  "about 10.9% of inactive px are spurious candidates" and the +0.069 inactive IoU from ignoring them must not be read as label noise:
  only about 0.22 [0.08, 0.53] of the image-supported inactive candidates (0.30 px-weighted) are label errors, and the missed-inactive
  type (5 of 6) is where they concentrate.
- The auditor's earlier one-look check agrees with the raters on 7 of 10 matched "label error likely" rows (descriptive).
