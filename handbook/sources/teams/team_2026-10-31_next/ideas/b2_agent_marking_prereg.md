# B2 agent marking: pre-registration (marker1)

**Status:** v2.2, written 2026-11-02.
- It implements judge's 7 changes to v1.0 exactly.
- v2.2 = v2.1 (md5 cf37be4f) plus judge's bundle details: §4 views, §7 / §8 file names.
- It supersedes v1.0 (md5 9b0949e0: centre-cell unit, self-built stem lists) and v2.0 (md5 5b583564: written before judge's 7 changes arrived; own thresholds and views).
- No calibration or B2 image has been viewed, and no mark exists.
- v1 and v2 artefacts are kept for audit in `ideas/marker1/superseded_v1/` and `superseded_v2/`, and are not used.
- My stem-named scratch copies of the 32 Hanifi images, and the views made from them, were deleted unviewed.

**Rater:** `marker1` (Claude agent).

## 1. Purpose and the two-rater caveat
- **Purpose:** replace the user's 15-minute marking of the 100 B2 v2 panels with agent marks. This applies only if the calibration in §6 passes.
- **marker1 and marker2 are two runs of one model:** their agreement is consistency, not independent reliability. A shared blind spot would show in both. The checks against house and Hanifi labels (§5) are the only external checks.

## 2. Blinding and disclosures
**Bundles:**
- I mark only from judge's bundles: name-free random IDs. Calibration = 72 items, mixed and shuffled. B2 = 100 items, shuffled. Judge holds the key.
- **I do not match bundle images against any file on disk, by pixel or by md5.** I do not use my `calib_order` / `calib_boxes` / `calib_img_md5` files (superseded_v1), or any stem list, for marking.

**Labels:**
- I never see calibration labels.
- Judge computes agreement with judge's own code, after my marks file's md5 is in the log.
- I receive PASS / FAIL only: no per-cell feedback and no numbers.

**Files I do not open from now on:**
- in `b2_mining/v2/`: `b2v2_candidates.tsv`, `pool_v2_half.jsonl`, `b2v2_report.txt`, `b2v2_hanifi_panels.txt`, `b2v2_gate*`, `overlays/`, `b2v2_sheet*.png`, other raters' `b2v2_marks*.tsv`, `b2v2_list.txt`;
- Hanifi files: `calib/data/rf` masks, `ignore`, `rf_context.tsv`; `found/t9/rf_sets.tsv`;
- `judge/` (including `judge/out/rf_sets.tsv`);
- any model output (`m0`, dumps, records);
- `scuff_masks/`;
- review files on B2;
- log lines about B2 panels. I only append my own log lines.

**Other rules:**
- Any rater who must touch `rf_sets.tsv` reads columns 1-6 only (`cut -f1-6`). Column 7, `crack_px`, is a label.
- E1 / test: never.

**Disclosures** (no counts or labels repeated here):
- **D1.** `b2v2_report.txt` was required reading in my brief.
  - It describes the B2 v2 ranking as a list of crack-predicted half-cells (90 ranked plus 10 random).
  - It also gives the ranking's AUROC against the Hanifi labels and aggregate Hanifi label counts for the pool half-cells.
  - So I know the panels are enriched for model-predicted crack, and I know a rough Hanifi base rate.
  - Mitigation: no quota and no balancing; each item is marked on its own. The bundle hides part (A / B), and ranked vs random.
- **D2.** I read `review_suggestions_2026-10-30.md` §3. It names the 3 Hanifi cells that are also B2 panels, with their label px. They are not in the calibration set. In the name-free B2 bundle I cannot tell which items they are, and I have never viewed them. Judge may treat those 3 as descriptive, as `b2v2_report.txt` already does.
- **D3.** I read `judge/out/rf_sets.tsv`: the header line (it shows the column name `crack_px`, no values) and columns 1-6. `judge/` is off-limits from now on.
  - **I know the calibration part-B stems.** I built the 32-stem Hanifi list for v1 and saw it printed. A script read only the `stem` field of `pool_v2_half.jsonl` (key names printed, no score values).
  - Printed outputs also showed the 36 H36 `_rf` stems, the 3 B2-list stems of D2, and 3 `b2v2_list.txt` lines from `head`.
  - A script compared the 32 pool copies with their E-SCDD `_rf` image files (images only, no masks, no viewer): same pictures, aligned at shift (0, 0).
  - Knowing the stems gives no label information. The matching rule above stops me linking items to stems.
- **D4.** I viewed 2 random pool half-cells (seed 7) to check geometry and tools. They are outside the Hanifi set and outside the B2 list.
- **D5.** I read the last 40 lines of `log.md` at the start. They say the user may mark B2 and the protocol is changing; no panel is named.

## 3. Marking unit
**The whole 512 × 512 crop.** A crack or scuff visible anywhere in the crop counts: centre cell, neighbour strips, either side of a gap. This is the unit for raters and the user alike. Every reference label is counted on the whole crop. There is no centre box and no fork.

## 4. Marking guide
**Views.** These are judge's bundle images in `team_2026-10-31_next/b2_bundle/` (README.md; MANIFEST.md5 1751950d). Both are viewed for every item, one item at a time:
- **`<ID>_v1.png`:** the 512 × 512 greyscale crop at native resolution.
- **`<ID>_v2.png`:** the same crop with autocontrast (1 % cutoff) and a 2× Lanczos upscale to 1024 × 1024.
- IDs are C001-C072 (calibration, `cal/`) and P001-P100 (B2, `b2/`).
- No other processing: no own zoom, filters or ridge detection, no model, no other image.
- Reading hint (S): V2's stretch darkens grain blotches. Judge texture on V1, and use V2 to follow thin lines.

**Classes:**
- **crack:** a thin dark line.
  - About 1-3 px wide at native resolution (up to ~4 px with halo), at least ~15 px long.
  - It crosses the grain texture instead of tracing blotch outlines.
  - Its course is sharp and fairly straight or gently curved, often branching (Y, X, dendritic).
  - It may end at a busbar, ribbon or cell edge.
  - A dark area with sharp, crack-shaped borders (inactive) counts as crack when its bounding line is visible.
- **scuff:** a broad dark smear or rub streak.
  - About >= 5 px wide and at least ~40 px long.
  - Longer, smoother and more continuous than grain blotches, with soft edges.
  - Straight or gently curved; may cross busbars; may come as several parallel streaks.
- **both:** a scuff, plus a separate thin crack (for example branches leaving the streak).
- **neither:** none of the above anywhere in the crop.
- **unsure:** a candidate I cannot place between crack / scuff and normal texture at this resolution. Used honestly, never to fill the table.

**Not defects** (mark neither unless a real crack or scuff is also present):
- multi-crystalline grain blotches and grain boundaries: irregular, curvy, part of a patchwork of brightness changes;
- busbars and ribbons: straight, regular, often dashed;
- fingers: fine regular lines across the busbars;
- short finger-interruption dashes;
- the half-cut gap / black bar, cell spacing and the module frame or edge;
- white background outside the module;
- round dark spots and point-like blobs;
- uniformly dark (dead) cells with no line structure.

**Recording:**
- One line per item: `id  mark  note`. The note says what and where, e.g. `diagonal ~60 px line, upper-left neighbour, crosses grain`.
- Each line is appended right after that item is viewed.
- One pass, in the bundle's shuffled order.
- A written mark is never revised. A pure typo fix is logged as such.

## 5. Calibration set and references (judge builds the bundle and scores)
- **72 items, mixed and shuffled into one bundle.**
- **Part A, 40 house-labelled CSIR train cells**, drawn by judge with a seed.
  - 20 with crack >= 100 px and 20 with 0 crack px; house `masks_escdd`, whole crop.
  - Reference: crack+.
- **Part B, 32 Hanifi `_rf` half-cells.**
  - The set: in the 986 B2 pool half-cells, minus the `b2v2_list.txt` stems, hygiene applied (no CSIR_00300, no val/test-module cells).
  - References from E-SCDD `_rf` masks over the whole crop: crack+ = class 14 >= 20 px; scuff+ = class 25 >= 1 px; either+ = crack+ or scuff+.
- **My marks mapped:**
  - crack+ = `crack` or `both`;
  - scuff+ = `scuff` or `both`;
  - either+ = `crack`, `scuff` or `both`.
  - **`unsure` counts as negative.**
- **Scorer:** judge's own code. My `superseded_v1/m1_calib_score.py` (md5 022f0c49, centre-box version) stays as a stated reference only. It is not the scorer.
- **Label caveats for part B:**
  - Hanifi crack labels are speckle-heavy and SAM-made, so a crack+ label (>= 20 px) may be scattered specks with no visible line;
  - Hanifi chose which cells to label;
  - n = 32, so the CIs are wide;
  - all cells are CSIR 297-335, not E1's half-cut family.

## 6. Acceptance rule (thresholds fixed now; unsure = negative)
**PASS only if all three hold:**
1. **Primary gate, part A crack recognition:**
   - crack+ sensitivity >= 0.70, **and**
   - crack+ specificity >= 0.70, **and**
   - the bootstrap 95 % lower bound of balanced accuracy > 0.5 (2,000 cell resamples, seed 1).

   The bound beats the trivial all-negative and all-positive raters.
2. **Weak scuff gate, part B** (stated as weak: few positives, noisy labels):
   - scuff+ sensitivity >= 0.50, **and**
   - scuff+ specificity >= 0.70.

   Wilson 95 % CIs are reported.
3. **Unsure cap:** `unsure` on <= 14 of the 72 calibration items (20 %).

**Reported, not gated:** part-B crack and either agreement: κ, sensitivity / specificity with Wilson CIs, 2 × 2 tables.

**On FAIL:**
- I stop, report to team-lead, and do not mark B2.
- No re-marking.
- No change to the guide, views or rule after the verdict.

**Rationale (S):**
- The house labels in part A are clean, so they test whether I can see real cracks of moderate size on CSIR grain.
- Part B's crack labels are speckled, so crack agreement there is informative but not a fair gate.
- Scuff can only be checked on part B, hence a weak gate.

## 7. B2 marking (only on PASS)
- Judge's name-free B2 bundle: 100 items, shuffled. Same guide, views and one-pass rule.
- I mark by bundle ID in the shuffled order.
- I write `ideas/marker1/b2_marks.tsv` with columns `id  mark  note` (bundle README).
- I log its md5, then send it to judge and coach. Judge maps IDs back to panels and stems through the key.
- **Caveats (S):**
  - The B2 panels are mostly model-crack-predicted cells, a different mix from calibration, so agreement need not transfer exactly.
  - D2's 3 cells are descriptive only.

## 8. Practical
- CPU only, on the laptop, one item at a time.
- Calibration output: `ideas/marker1/cal_marks.tsv` (`id  mark  note`). Its md5 goes in `log.md` before I message judge and before judge opens any label.
- I view the bundle images in place. I make no copies.

## 9. Every file I read while writing this prereg (v1.0 to v2.1)
**Team and handbook files:**
- `team_2026-10-31_next/README.md`.
- `team_2026-10-29_features/b2_mining/v2/b2v2_report.txt`, in full (D1). Also directory listings of `b2_mining/` and `b2_mining/v2/` (file names only).
- `team_2026-10-27_unlabelled/ideas.md`: grep lines matching F11-F18.
- `handbook/02_domain_primer_EL_and_defects.md`, in full.
- `team_2026-10-31_next/log.md`: last 40 lines at the start (D5). Later, a grep for numpy (one judge line about the laptop python).

**B2 and Hanifi files:**
- `team_2026-10-31_next/judge/out/rf_sets.tsv`: header line; columns 1-6 via `cut`; counts of columns 2 / 3 / 6 (D3).
- `team_2026-10-29_features/b2_mining/v2/pool_v2_half.jsonl`: key names and the `stem` field only, by script (D3).
- `team_2026-10-29_features/b2_mining/v2/b2v2_list.txt`: `head -3`, and used in `comm` set operations (D3).
- `team_2026-10-29_features/review_suggestions_2026-10-30.md`: grep lines for Hanifi / `_rf` / 986, and lines 18-40 and 90-110 (D2).

**Greps:**
- Over the team folders for "35 of the 43" etc. (file names only).
- For "342 ... 163": matching lines in `protocol_HC.md`, `build_hc.md`, `idea03_neighbour_ref.md`, `idea05_synthetic_halfcut.md`, `domain_out/shv1_meta/README.md`, `dom_synth_*.py`, `hc_review_checks.py`, and `log.md` line 132.
- For `images_512` over `b2_mining/v2/*.log` (includes `b2v2_gate.log`): no hits, nothing printed.

**Other files:**
- `team_2026-10-31_next/ideas/idea05_synthetic_halfcut.md`, lines 40-60.
- `handbook/14_code_and_infrastructure.md`: grep lines for `images_512`, `gaint`, python.
- `team_2026-10-27_unlabelled/ideas_scripts/scuff_check.py`: grep lines, code only.
- `~/mtp/datasets/escdd_full/ListOfClassesAndColorCodes_20221008.csv`: the class list.

**Image data:**
- `team_2026-10-31_next/b2_bundle/README.md` and the bundle file listing (names only; no image viewed).
- `escdd_full` directory listings: the top level, and the file names of `<stem>_rf` in `el_images_*`.
  - 32 `_rf` image files were opened by the pixel-compare script only (D3).
  - No mask file was opened.
- gaint `images_512`:
  - a listing (head and count);
  - 2 D4 images viewed;
  - 32 v1 Hanifi pool copies processed by script, never viewed, now deleted.
