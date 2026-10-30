# Labelling plan after the SK1 null (agent 4, 22 Oct 2026)

**Why this plan.** `null_diagnosis.md` §2 and agent 2's pool probe point the same way:
- 34–38% of GT crack is truly missed, more than 2 px from any prediction;
- the misses sit in faint cracks, cracks on inactive edges, and the ARTS/BMRK sources;
- no SSL loss and no prior shift reaches them.

So the next lever is which cells are labelled and how cracks are labelled.

All counts below are measured on cv02 `el_p7/data` (`masks_escdd`, split seed 0) on 22 Oct.

## 1. What the 5% labelled set teaches today

| Source | Train cells | Train cells with crack | In the 5% labelled set (crack cells, crack px) | Test crack px (share) | Test relaxed crack recall, BsD5 |
|---|---|---|---|---|---|
| ARTS | 162 | 43 | 4 (1 cell, **47 px**) | 2,856 (3%) | 0.30 |
| BMRK | 42 | 24 | 3 (2 cells, 5,387 px) | 25,235 (27%) | 0.40 |
| CFVS | 146 | 88 | 6 (3 cells, 11,646 px) | 52,642 (57%) | 0.80 |
| CSIR | 111 | 52 | 7 (2 cells, **687 px**) | 11,146 (12%) | 0.67 |
| SDLE | 17 | 2 | 3 (1 cell, 208 px) | 195 (0.2%) | 0.24 |

**Reading.**
- At 5% the model has seen almost no ARTS crack (47 px) and little CSIR crack (687 px).
- Its labelled crack is dominated by CFVS (11,646 of 17,975 px), which is also the source it recalls best.
- BMRK carries 27% of test crack, with only 2 labelled crack cells.

## 2. Which cells to label next

**We already hold full labels for all 478 train cells.** So the question "which cells should be labelled" can be answered **retrospectively, with no human labelling**: move chosen cells from the unlabelled pool into the labelled set and train. This is the cheapest high-value experiment the diagnosis points to. It needs the user's approval and a protocol.

### 2a. Proposed retrospective budget test (sketch, not a protocol)
- **Question.** At a fixed budget of +12 labelled cells over 5% (23 → 35), does choosing them by source and crack type beat choosing at random?
- **Arms** (supervised, L3 recipe, 20,000 steps, 5 seeds each, final weights, cv02):

  | Arm | Added cells |
  |---|---|
  | R | +12 random train cells; 3 draws of the random set |
  | T | +12 targeted: 6 BMRK crack cells, 4 ARTS crack cells, 2 CSIR crack cells, preferring cells whose crack is faint or on an inactive edge |

  - Targeting may use train masks only; never test or val.
- **Primary:** test crack IoU and crack relaxed recall, all four cell sets, and **against R+LA τ = 1** (the S-a yardstick).
- **Expected effect.** Unknown. Falsifiable: T − R crack IoU > threshold, and ARTS/BMRK recall up by ≥ 0.1.
- **Cost.** About 20 supervised runs × 1.5 h, on cv02.
- The same design answers the split-seed weakness (handbook 13 A9).

### 2b. For new labelling (WattCycle or new modules)
- Prefer cells from module types and sources absent from the labelled set over more of the same source. CFVS-like cells are already recalled at 0.80.
- Within a source, prefer cells with faint or short cracks and cells with inactive regions. These are where recall is lowest: 0.42 for the faintest third and 0.44 for inactive-edge cracks.

## 3. Open label-convention questions (for the user)
These are user and annotator decisions, not training questions.

1. **Cracks drawn on the edge of an inactive region.**
   - 12% of test crack px lie within 2 px of GT inactive; relaxed recall there is 0.44 vs 0.69 elsewhere (0.37 vs 0.59 without the twins).
   - In the image these show as an intensity step, not a line (e.g. audit M28–M30).
   - Questions:
     - Should a crack that bounds an inactive area be labelled as crack, as inactive edge, or both?
     - Should scoring use a tolerance band there?
2. **Faint cracks.**
   - Labelled-crack contrast near zero: the faintest third of test crack px has recall 0.42.
   - Some are real but at noise level (CSIR_00057). Some may be wide-labelled thin cracks: the 20221008 revision widened labels (handbook 17 §5.9).
   - Question: label width for faint cracks. Keep the widened convention, or label the visible core only?
3. **Tiny fragments.**
   - 12 of the 40 always-missed components are under 50 px, the smallest 2–4 px.
   - Several are pieces of a larger crack split by an inactive region or busbar.
   - Question: merge fragments into their parent crack, or drop specks under N px from the masks?
4. **Old-mask remap pixels.**
   - The P6 remap pixels in `ARTS_00051_r3_c2` (4 audit components, M02–M05) exist only because P6 restored them from the old masks (handbook 17 §5.3). E-SCDD itself has no crack there.
   - Question: keep them in the test GT, or drop them? This changes test crack px by 236 (0.26%).

## 4. One-hour human audit of the 40 always-missed components
- **Definition.** A GT crack component (8-connected) whose seed-mean relaxed recall is below 0.1 in **all five arms** (A5c, AB5, BsD5, BsDB5, BsDBn5).
- **Size.** 40 components in 18 cells, 5,018 px (5.4% of test crack px).
- **By source:** BMRK 17, ARTS 10, CFVS 7, CSIR 6.

**Files**
- **Sheet:** `team_2026-10-21/skcdf/audit_sheet.csv`. One row per component: id, cell, component number, area, width, contrast, BsD5 relaxed recall, crop path. Empty columns to fill: `real_crack`, `label_artefact`, `unsure`, `note`; put an x in one of the three.
- **Crops:** `team_2026-10-21/skcdf/audit_crops/M01_…png` to `M40_…png`. Each has three panels:
  1. the image, contrast-stretched;
  2. the same with this GT crack in **red**, other crack GT in **yellow** and inactive edges in **blue**;
  3. the whole cell with a red box marking the crop.
- **Overview:** `audit_crops/grid_all40.png` (all 40 at half size). The older `verify_a4/missed_all.png` shows the 16 largest.

**How to use it**
- About 1.5 minutes per component.
- Mark "label artefact" when nothing crack-like is visible at the red pixels. Examples: an inactive-edge step, noise, a busbar edge, a remap speck.
- Mark "unsure" when it is faint.

**What the audit decides**
- **Mostly artefacts** (say ≥ 50% of px): part of the crack "deficit" is a label convention. Fix the masks or the metric first (§3) and report test numbers both ways.
- **Mostly real cracks:** the deficit is recognition. §2's budget test is the next experiment.

## 5. What is not proposed
More SSL variants aimed at crack: the SKCDF track is closed, and S-b's gate did not pass. Synthetic E-SCDD images are not proposed either (data decision D2).
