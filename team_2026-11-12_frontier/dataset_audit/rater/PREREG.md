# AI-rater check of the dataset-audit label-error candidates: pre-registration

**Status:** v1.0, 21 Nov 2026 (IST), written by the rater designer (a subagent of the lead) **before any rating**. No rater agent
exists yet, no panel has been rated, and the key is sealed. This file, `RATER_BRIEF.md`, the panels, the key and the scorer are
frozen by the md5s in `MD5.txt`. Any later change is added as a dated amendment at the end; the text above it is never edited.
Tags as in the audit: **E** measured, **S** judgement, **P** an earlier record (file named).

## 0. Why, and what is reused
- `../REPORT.md` F4 and F5: the candidate **counts** are measured (E); that the candidates **are label errors** is suggestive (one
  non-expert look at 30 panels: 10 label error likely, 7 convention, 11 ambiguous, 1 model error, 1 unverifiable).
- The user (21 Nov) chose **"Use an AI rater"** for the 49 cells with an image-supported candidate, under a pre-registered rule,
  instead of the 2 to 3 h expert pass of REPORT section 5 (4).
- Earlier agent-rater test (P: handbook `11_results_synthesis_and_claims.md` row 50; `team_2026-10-31_next/ideas/b2_agent_marking_prereg.md`
  v2.2): crack recognition **passed** on 40 house-labelled CSIR cells (sensitivity 20/20, specificity 17/20); scuff **failed**.
  Reused here: native-resolution view plus a contrast-stretched enlarged view; one pass in a shuffled order; one line written right
  after each item, never revised; non-committal answers count against sensitivity; name-free random IDs with a sealed key;
  acceptance thresholds fixed before marking; calibration items with known answers mixed in blind; "two runs of one model measure
  consistency, not independent reliability".
- Not reused: scuff (failed there, not needed here); a centre-cell unit (the disputed region is marked instead).

## 1. Scope and data
- **Rated items: all 124 image-supported candidates** (`supported == 1` in `../out/a_candidates.tsv`, md5 7df4e6ff), in **49 pool
  cells** (39 cv5v3 groups):

  | Class (finding) | Type | n | Sources |
  |---|---|---|---|
  | crack (F5) | MC missed crack | 46 | CFVS 22, CSIR 18, BMRK 5, ARTS 1 |
  | crack (F5) | SC spurious crack | 32 | CSIR 23, CFVS 4, ARTS 3, BMRK 2 |
  | inactive (F4) | MI missed inactive | 6 | CFVS 6 |
  | inactive (F4) | SI spurious inactive | 40 | CSIR 24, CFVS 14, ARTS 1, BMRK 1 |

- The 129 candidates without image support are not rated; the result covers the image-supported ones only.
- Pool P532 only, through the audit's guarded loaders (`../scripts/common.py`, `pool_stems()` fails closed on sealed stems).
  Labels v1.1; consensus = the 25 cv5v3 out-of-fold models of the audit (`../cache/cons/`, vote >= 13 of 25 for the overlay).
  No label, prediction or label summary of the legacy test (50) or E1 (106) is read. CPU only, `nice -n 19`, at most 4 workers.

## 2. The question per candidate, and how answers map to the audit's categories
The rater sees two annotations, A and B, of a window, and green brackets around the candidate. It answers: **which annotation fits
the image inside the brackets?** One of `A`, `B`, `CONVENTION`, `AMBIGUOUS`, `UNREADABLE`, plus `high` / `low` confidence and a
short note (`RATER_BRIEF.md` section 4 has the decision rules). Through the key:

| Rater answer | Audit category |
|---|---|
| the consensus overlay (A or B) | **label error** |
| the label overlay (A or B) | **model error** (label judged correct) |
| `CONVENTION` | annotation-convention difference |
| `AMBIGUOUS` | ambiguous |
| `UNREADABLE` | unverifiable |
| no line for the ID | ambiguous (counted and reported) |

## 3. What the rater sees, and why
**Panel** (1112 x 712 px, one per item, `scripts/rcommon.py: render_panel`):
- top row: the whole image at 0.5x with an orange box on the window (context); the window at native 1:1, unprocessed; a legend;
- bottom row, enlarged to 360 px (Lanczos): the window with no overlay; the same with overlay A; the same with overlay B;
- green corner brackets around the disputed region (the candidate's bounding box, or the plant's for calibration items);
- window side = clip(region extent + 48, 96, 288) px; it is 96 px for most items (candidates 96 to 226, calibration 96 to 174).

**Decisions:**
- **Overlays are shown.** A candidate is a disagreement between the label and the models; without the two annotations the rater
  cannot know what is disputed, and a convention difference is by definition about how something is drawn. To limit anchoring, the
  enlarged tile **without** overlay comes first and the brief tells the rater to read it first.
- **Raters are blind to which overlay is the label.** A and B are assigned at random per item, balanced within each stratum
  (candidate type; calibration plant x side): 39 / 39 crack and 23 / 23 inactive candidates have the label as A / B. The legend says
  only that "which one is the dataset label is hidden". This removes the pull towards "the human label is right" (or "the models
  are right") and lets missed and spurious candidates share one question.
- **Both overlays are drawn identically.** Crack = the centreline (frozen `bench/skel.py` skeleton) dilated to a 3-px band, drawn as
  a red outline; this removes the line-width convention (F1, F7) that would otherwise identify the label. Inactive = blue outline
  plus a light tint. Residual cues cannot be removed (hand-drawn label polygons vs smoother model regions); disclosed in section 8.
- **Contrast stretch per image, not per window:** grey 1st to 99th percentile of the image's non-padding px, with a range of at least
  64 grey levels. A per-window autocontrast (B2's view) turned a uniform bright window into dark noise in a test render, which would
  mislead inactive judgements.
- **No information in the files:** random 5-character IDs, no text chunk in the PNGs, all panels the same size and the same mtime,
  written in random order. Each rater has its own random order (`orders/ORDER_R1..3.txt`).
- **Raters are not told that calibration items exist** (the brief does not mention them).

## 4. Raters
- **Three raters**, each a **fresh Claude agent** launched by the lead with the same model; the model id is logged. They are three
  runs of one model: their agreement is consistency, not independent reliability; a shared blind spot would show in all three. The
  calibration set (section 5) is the external check.
- **Each rater reads only the rater bundle** (`/home/noob/work/bench_int_io/rater/bundle/`: `RATER_BRIEF.md`, `examples/EX1..5.png`,
  its own `ORDER_R<N>.txt`, `panels/`) and writes only its own `out_r<N>/ratings_r<N>.tsv`. It never reads this file, the key, the
  scripts, the audit folder or its numbers, the handbook, or another rater's output. The launch prompt contains no audit number.
- A rater may be split into **sessions** (fresh agents with the same prompt and a cap of panels per session); a later session resumes
  at the first unrated ID of the same order and never re-rates. The three raters may run in parallel.
- **Validity and replacement:** a rater whose file lacks more than 5% of the IDs (more than 9 of 184), or who breaks the reading
  rules, is replaced once by a fresh rater with the same brief and order, starting a new file. This is decided and logged **before
  the key is unsealed**; no rater is replaced or re-run after the key is opened.
- **Freeze before scoring:** the three files' md5s are logged by the lead before `chmod 700 key`.
- Panels are viewed by the rater agents through their image viewer (the model's own input path, as in B2). No panel is uploaded,
  published or sent to any other service.

## 5. Calibration set: 60 items with known answers, mixed in blind
**Base (the "clean controls"):** regions of pool cells where the v1.1 label and the 25 models agree:
- crack: a v1.1 crack component >= 40 px with **all 25 models** within 2 px on >= 95% of its px (22 items; 2 items needed the
  fallback >= 23 of 25), visibly dark (contrast z <= -1.0 as in the audit, `common.contrast_z`);
- inactive: a v1.1 inactive component of 200 to 6,000 px, extent <= 200 px, with >= 20 of 25 models voting inactive on >= 80% of
  its px, z <= -1.0 (rare: before the size and window rules, only 29 regions >= 200 px in 13 non-rated cells meet the vote and
  darkness rules);
- bright clean material for the fakes: v1.1 background or busbar, >= 8 px (crack) / 6 px (inactive) from any crack or inactive
  label and from any px with >= 2 model votes, not darker than its ring (z > -0.3);
- every window free of candidate px (audit `ign` map).

**Plants.** Each plant is applied **either to the label overlay** (truth **label_error**: the consensus overlay is right) **or to the
consensus overlay** (truth **label_correct**: the label is shown unchanged and is right). This is how the clean controls enter: a
control is a clean region whose label is shown as is, while the other overlay carries the plant, so a control panel looks exactly
like a candidate panel. (An unchanged agreement panel would reveal itself and give a trivial specificity.)

| Class | Plant | What is done | Looks like | n label / n consensus |
|---|---|---|---|---|
| crack | SHIFT | the component (<= 90 px extent) or a 20 to 35 px-radius stretch of it moved 8 px along its normal, onto clean material (>= 90% background / busbar, none on a ribbon, not dark there) | displaced line | 6 / 6 |
| crack | DEL | the px within 4 px of a 10 to 20 px-radius stretch (26 to 99 px) removed | MC (label side), SC (consensus side) | 6 / 6 |
| crack | FAKE | a 3-segment polyline (12 to 28 px per segment, 2 px wide) added on clean bright material | SC (label side), MC (consensus side) | 6 / 6 |
| inactive | DEL | the region removed (consensus side: consensus inactive within 6 px of it) | MI (label side), SI (consensus side) | 6 / 6 |
| inactive | FAKE | a 4- to 6-vertex polygon (290 to 550 px) added on clean bright material | SI (label side), MI (consensus side) | 6 / 6 |

- **Totals:** crack 36 (18 label_error, 18 label_correct), inactive 24 (12 / 12); **184 panels in all** (124 candidates + 60).
- Cells: 58 cells (49 groups), none of the 49 rated cells; at most one item per cell (inactive DEL: up to 2). Crack and fake items
  also avoid the 39 modules (cv5v3 groups) of the rated cells; inactive DEL could not (9 of its 12 cells share a module with a rated
  cell; disclosed).
- Sources: crack CFVS 18, CSIR 12, ARTS 3, BMRK 3 (CSIR cells were taken first for SHIFT / DEL; fakes follow the candidates' sources);
  inactive CFVS 15, CSIR 7, BMRK 2.
- Selection is deterministic (`scripts/build.py`, public seed 20261121; the key records it). IDs, A / B and orders come from a secret
  seed drawn from `os.urandom`, stored only in the sealed key.
- **Non-scored examples** for the brief (`brief_examples/EX1..5.png`) come from cells outside the rated cells, their modules and the
  calibration cells: EX1 crack segment deleted (synthetic), EX2 fake inactive on bright material (synthetic), EX3 a real unsupported
  candidate read as a convention, EX4 a real unsupported candidate read as ambiguous, EX5 a dark crack-bounded region deleted from
  one overlay (synthetic). Answers and reasons are in the brief (S, the designer's reading).

## 6. Scoring (`scripts/score.py`; tested on synthetic data by `scripts/test_score.py`)
- Each answer is mapped through the key (section 2). **Majority** = the category given by >= 2 of 3 raters, else `no_majority`.
- **Calibration**, per class (crack, inactive) and pooled, per rater and for the majority:
  - **sensitivity** = share of label_error items called label_error; **specificity** = share of label_correct items **not** called
    label_error. Every non-label-error answer (model error, convention, ambiguous, unverifiable, missing) counts as a miss on a
    label_error item and as correct on a label_correct item;
  - Wilson 95% intervals; Youden J = sens + spec - 1 with a bootstrap 95% lower bound (2,000 resamples of the items, positives and
    negatives resampled separately, seed 1); results per plant type and side (descriptive).
- **Agreement:** Fleiss kappa among the 3 raters, on the binary label-error call and on the 5 categories, over the candidates of
  each class and over the calibration items.
- **Candidates:** majority verdict counts by class, type (MC, SC, MI, SI) and source; label-error share (>= 2 of 3) with a Wilson
  interval and a **cell-cluster bootstrap** interval (cells resampled; one cell holds 20 SI candidates); px-weighted share;
  **share corrected for rater error** (Rogan-Gladen: (p + spec - 1) / (sens + spec - 1), clipped to [0, 1]) with a joint bootstrap
  over candidate cells and calibration items (2,000 draws, seed 1).
- Descriptive only: the rater majority against the auditor's one look (`../out/a_visual_check.tsv`) where the candidates match.
- Outputs: `out/score_report.txt`, `out/candidate_verdicts.tsv`, `out/calibration_items.tsv`.

## 7. Decision rules (fixed now; applied per class: crack -> F5, inactive -> F4)
**Run validity:** each rater file holds >= 95% of the IDs (else section 4's replacement, before unsealing).

**The raters are trusted for a class only if all four hold:**
- **G1** majority sensitivity >= 0.70 **and** majority specificity >= 0.80 on that class's calibration items (crack 18 + 18,
  inactive 12 + 12);
- **G2** bootstrap 95% lower bound of the majority's Youden J >= 0.30 (so the error correction is not divided by a near-zero J);
- **G3** at least 2 of the 3 raters pass alone: sensitivity >= 0.60 and specificity >= 0.70 (the majority is not carried by one rater);
- **G4** Fleiss kappa of the binary label-error call over that class's candidates >= 0.40 (the verdicts on real candidates are
  reproducible across raters, not only on the planted items).

**If all four pass, the finding becomes "measured"** (E, rater-based) in this form: "of the N image-supported crack (inactive)
candidates, k are label errors by the majority of 3 calibrated AI raters (share, cell-bootstrap CI); corrected for the raters'
measured sensitivity and specificity: c [CI]". The reading of the corrected share's 95% interval is fixed now:
- lower bound > 0.5: **most** image-supported candidates are label errors;
- lower bound > 0 and upper bound < 0.5: label errors **exist but are a minority** of them;
- lower bound > 0 otherwise: label errors **exist**; whether they are most is undetermined;
- lower bound <= 0: **no measurable excess** of label-error calls over the raters' false-positive rate (the candidates are not shown
  to be label errors).

Convention, ambiguous and model-error shares are reported alongside, as uncalibrated (S): only the label-error call is calibrated.
The px share in REPORT F4 / F5 may then be restated as "about <corrected share> of the image-supported candidate px", never as a
count of all label errors in the dataset (section 8).

**If any gate fails for a class, the raters cannot be trusted for it and the finding stays "suggestive".** Their verdicts are reported
only as uncalibrated rater opinion (S) in an appendix, never in a headline. There is no re-rating, no change of brief, panels or
thresholds for this candidate set after the key is opened. The remaining route is the human pass the audit proposed (REPORT section
5 (4)), which is the user's decision.

## 8. What this cannot show
- **Truth.** A rater majority is not an expert annotator; it is a calibrated, reproducible reading of the image. Three runs of one
  model can share a blind spot.
- **Transfer from calibration to candidates.** Planted errors sit on clean, clearly visible structure and may carry shape cues
  (straight-edged polygons, 3-segment polylines, jogs at the ends of a shifted stretch) that real errors lack; real candidates are
  fainter and messier. Sensitivity and specificity measured here are likely optimistic for the candidates; G4 and the per-plant
  results partly guard against this, and DEL plants (no shape cue) are reported separately.
- **Conventions are not calibrated:** no planted item has CONVENTION as its truth.
- **Recall of the audit's detector:** unrated; only the 124 image-supported candidates are judged, so a corrected share is a share of
  these candidates, not of all label errors in the pool.
- **Calibration mix:** clean inactive regions are rare and CFVS-heavy (15 of 24 inactive items), while SI candidates are CSIR-heavy
  (24 of 40); 9 inactive DEL cells share a module with a rated cell (their windows are free of candidate px, but a neighbouring image
  may show the same physical area).
- **Overlay identity** cannot be fully hidden (residual style cues; section 3).
- **Calibration panels are cleaner:** their A and B differ only at the plant (median 2,530 differing display px between the A and B
  tiles, against 12,500 for candidates, whose windows hold other small disagreements). A rater could guess which panels are cleaner;
  this reveals no answer (A / B is random within each plant x side) and the raters are not told that planted items exist.

## 9. Procedure
1. (Done, designer) Build panels, key, orders, examples (`scripts/build.py`); write this file and the brief; test the scorer;
   copy the rater bundle; write `MD5.txt`; seal the key (`chmod 000 key`, access-time tripwire recorded in `MD5.txt`).
2. (Lead) Log `MD5.txt`. Launch the 3 raters as in the designer's report (bundle only, own order, own output, no audit numbers).
3. (Lead) When the three files are complete, log their md5s; check validity (section 4); replace a rater if needed.
4. (Lead) Check the key's access time against `MD5.txt` (`stat -c %x key/key.tsv`, after `chmod 700 key`), then score:
   `nice -n 19 /home/noob/work/el-fault-detection/.venv/bin/python -I scripts/score.py --key key/key.tsv --ratings <r1> <r2> <r3>
   --out out --visual ../out/a_visual_check.tsv`.
5. Report per class with the section 7 wording, both when the raters are trusted and when they are not.

## 10. Disclosures (what the designer read or viewed)
- Read: `../REPORT.md`, `../PLAN.md`, `../out/a_summary.txt`, `../out/a_visual_check.tsv`, `../out/a_candidates.tsv`, `../out/MD5.txt`,
  `../scripts/{common,candidates,consensus_pass,gallery}.py`, the B2 prereg (above), handbook doc 11 row 50 and doc 02 sections 1 to 8.
- Viewed (images), to set colours and the stretch and to choose the examples: 12 test renders (8 views of 6 calibration-type plants
  from an earlier selection run, some of whose cells may be in the final calibration set; 4 real unsupported candidates outside the
  rated modules) and the 5 examples. **No panel of the 124 rated candidates was viewed**, and no candidate verdict was formed.
- A scratch area of the designer that names calibration cells is kept inside the sealed `key/` folder (`key/designer_scratch/`).

## Amendments
(none)
