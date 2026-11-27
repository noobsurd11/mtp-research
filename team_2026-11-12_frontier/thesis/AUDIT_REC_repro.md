# Audit of app_repro (27 Nov 2026, independent checker)

Files: `chapters/app_repro.tex`, `chapters/app_repro_NOTES.md`. Line numbers are those of the edited .tex. Short source keys follow the NOTES source key (HO, PH, D1, CV, PM, AA, P1, SE, SR, GIT); `R/` = `/home/yugma/mtp/research/`.

## Priority 1 settled: PV-S3 released code, 0.828 vs 0.791

The writer was right. The primary record is the detailed section of the training-machine report (CV = `R/handbook/sources/old_era_reports/cv02__el_results_cv02.md`):
- CV l.903–906: "PV-S3's own end-of-training validation … logged per-class IoU crack 0.9133, contact 0.7806, interconnect 0.5959, corrosion 0.8735 … These equal our **pvs3 / native** numbers to 4 decimals."
- CV l.944–948, the native table: pvs3 IoU 0.9133 / 0.7806 / 0.5959 / 0.8735, mean **0.7909**. This is identical to the log.
- CV l.924–928, the eval295 table: 0.9147 / 0.7392 / 0.7866 / 0.8731, mean **0.8284**. This does not match the log (contact 0.7392 vs 0.7806, interconnect 0.7866 vs 0.5959).

The value that matches the code's own validation log is therefore **0.791 at native resolution**. Five summary lines say "0.828, which matches their own validation log", and all five are loose wording: CV l.61, handoff 6.10 (`MTP_session_handoff_2026-10-07.md` l.475), PH l.101, handbook 05 §4.2 l.224 (laptop and server copies) and PM l.151. In each case 0.828 is the same predictions scored on our eval295 grid. The .tex now states the four log values and says the match is 0.791, not 0.828 (change 9). Tables keep 0.828 because every other row of those tables is on the eval295 grid, and the PV-S3 table caption now says so (change 8).

## CHANGES

| # | file:line | old | new | evidence (path:line, quoted) |
|---|---|---|---|---|
| 1 | app_repro.tex:10–11 | "They come from the first pipeline: … the final step of 20,000 steps" | "On BenchmarkEL, unless stated otherwise, they come from the first pipeline: …" | UCF runs used DeepLabV3+ R50 and 3,585 to 95,760 steps (D1 l.628–630). The pilots and Pratt set C 0.116 are best-validation values: D1 l.532 "| run (best val) |", D1 l.550 "best val (step 17,500)" |
| 2 | :49 | "…compared two under-trained runs and was withdrawn." | "…and is recorded as invalid." | PH l.224 "early claim "SSL doubles performance 10.83 to 21.19" is invalid (both runs undertrained)". No withdrawal is recorded |
| 3 | :56 | "the SA-UNet++ row, the crack-width wording and all numbers needed final-step values from the rebuilt pipeline" | "…and the move of all numbers to final-step values from the rebuilt pipeline were pending" | PH l.363 "(v) Gangopadhyay row; (vi) crack-width claim wording; (vii) numbers moved to final-step new-pipeline values". These are three separate items; the old text merged them |
| 4 | :71 (tab:repro-poster) | Note cell "5-class includes background" | adds "; 48.15 equals the IoU equivalent of the published F1 (our identification)" | Fioresi prints F1 only (PM l.84–87). PM l.90 gives the IoU-equivalent mean 0.481 = (0.681+0.408+0.198+0.639)/4 = 0.4815, and D1 l.618 uses 0.4815 as the reference. The "Published" column would otherwise read as a printed Fioresi IoU |
| 5 | :165 | "Runs of 3 to 6 Oct are old era" | "Runs before 7 Oct are old era" | The Pratt row uses the 2 Oct pilots: HO l.186 "All "pilot" runs of Oct 2 used the coupled augmentation" |
| 6 | :184 | "The analysis of 8 Oct showed…" | "The audit analysis of 7 and 8 Oct showed…" | GIT f9708c0 2026-10-07 23:59:58 already contains PM l.12 with the rule-B / rule-C exclusion (`git show f9708c0:analysis/papers_metrics.md` l.12) |
| 7 | :187–188 | "the U-Net++ pilot arms (coupled-augmentation code) at 0.280 to 0.295 …, and our crack medians 0.21 to 0.25" | "…(coupled-augmentation code, best-validation weights) … and the U-Net++ arms' crack medians 0.21 to 0.25 (the two Pratt U-Nets 0.149 and 0.176)" | D1 l.532 "run (best val)"; PM l.58 "our U-Net++ arms 0.21–0.25, Pratt-A 0.149, Pratt-C 0.176. Paper 0.13–0.26." |
| 8 | :234–236 (tab:repro-pvs3 caption) | "Old era: PV-S3 reproduction … test was the only readout)" | "Old era, first pipeline: … scored on our evaluation grid with the shorter side at 295; … 25 to 44\% of test cells have the same physical cell in train, as later found)" | Rule 4 needs the conditions in the caption. D1 l.607 "eval: the whole image with its shorter side at 295"; SR l.166 "25–44% of test cells have the same physical cell (other stress stage) in train" |
| 9 | :262–264 | "0.828 on our evaluation grid and 0.791 at native resolution, where the per-class values matched the code's own validation log to four decimals." | "…0.791 at native resolution, the code's own protocol. The code's own end-of-training validation log (crack 0.9133, contact 0.7806, interconnect 0.5959, corrosion 0.8735) equals our native-resolution per-class values to four decimals, so the value that matches the log is 0.791, not 0.828." | CV l.903–906 and l.944–948 (quoted above); CV l.940 "native full resolution (PV-S3 protocol)" |
| 10 | :270–272 | "Our ``SemiCE'' was not PV-S3's: … (about 0.001 for crack)." | "The ``SemiCE'' of our Mean Teacher arms was not PV-S3's: … (about 0.001 for crack); our PV-S3 reimplementation (v1, v2) used the softmax form." | AA l.88–89 "Our `ConfidenceCELoss` (PV-S3 reimplementation) is the softmax version. The MT arm's `semi_ce` is not."; D1 l.663 "SemiCE = CE towards the teacher's argmax where the teacher's max softmax ≥ t_pos = 0.6". The old wording sat inside the PV-S3 section and implied that v1 and v2 used the per-class BCE |
| 11 | :289 | "The audit of 8 Oct found…" | "The audit of 7 and 8 Oct found…" | GIT f9708c0 (7 Oct 23:59:58) contains `analysis/alhvr_audit.md` l.46 "Ours (cosine to 0) \| 0.0156 \| 8.1%" and l.60 (89.4%) |
| 12 | :342 | "In our reading (descriptive; their rule is not confirmed)" | "…; the 50 cells overlap our training pool)" | Claim strength for a test50 re-score. ch03_related.tex l.106 "8 of its cells are the same physical cell as a cell of the training pool"; ch05 conditions "test50 values are in-distribution, known leakage, context only" |
| 13 | :348 (tab:repro-summary caption) | "Rows of 3 to 6 Oct are old era" | "Rows from before 7 Oct are old era" | same as change 5 |
| 14 | :400–401 | "Blur and $\pm 5^\circ$ rotation on crack labels a median 1.75~px wide, not a code or data bug, explained…" | "The training recipe, mainly blur and $\pm 5^\circ$ rotation on crack labels a median 1.75~px wide and secondly the loss, not a code or data bug, explained…" | P1 l.44–46 "It is the training recipe."; "Augmentation (biggest factor): blur kernels of 3–7 px and ±5° rotations…"; "Loss: plain or weighted CE learns a 0.2%-pixel thin class slowly". The old text gave augmentation as the whole cause |

NOTES: the PV-S3 log row and CONFLICTS 1 are rewritten as settled, and an "AUDIT 27 Nov" table at the end gives the source of every edited fact.

## REMOVED
None. No claim lacked a source.

## CONFLICTS
1. **PV-S3 0.828 vs 0.791 (settled, see above).** The handbook (05 §4.2 l.224 and l.227; server copy identical), handoff 6.10 (l.475), CV l.61, PH l.101 and PM l.151 all say that 0.828 matches the validation log. The detailed primary section (CV l.903–906, l.944–948) shows that 0.791 is the match. The appendix is now exact. I left the handbook and handoff alone (outside scope); they should be corrected at the next handbook refresh.
2. **Deck slide 4 (`to_human/ee511_deck/mtp/deck2_src.html` l.117–121) against the files.** No row contradicts the appendix. Notes:
   - Pratt "0.28 vs 0.28 to 0.30" is consistent at two decimals with the pilots' 0.280 to 0.295 (best-validation weights, coupled-augmentation code) and set A's 0.303 (final step). It mixes checkpoints and models (U-Net / U-Net++ against the DeepLabv3+ 4c row), and the absent-class rule is inferred, so "Ours, same scoring" is slightly stronger than the files.
   - Fioresi "crack F1 0.81 vs 0.81": ours is 0.806 (PM l.93), which rounds correctly.
   - PV-S3 "supervised 0.088 vs 0.23, same recipe": 8.76% = 0.0876, which rounds to 0.088. Ours is 0.230 in the PV-S3 convention at the paper's budget (D1 l.628). Consistent.
   - Hanifi "0.335 vs 0.352": consistent (P19 README l.42).
   - SEiPV "0.86 vs 0.84 or 0.46 to 0.51": consistent with SE l.13 and l.22 (13 Oct P-series, 5 seeds). Thesis T13b gives 0.855 for the final models, so the deck's "ours" is the older P-series value, not the T13b one. This is not an error, but the deck and T13b give different "ours" values for the same published number.
   - The deck caption says "Pratt, Fioresi, PV-S3: reproduced in our first pipeline". This matches the appendix's use of "first pipeline" for all work before 7 Oct.
3. NOTES CONFLICTS 2 to 9 (the writer's) were checked and stand as the writer resolved them. Examples: 23,750,424 parameters for the 1-channel model (D1 l.489–490); set C 0.116 stated as the best-validation value; the SemiCE crack threshold 0.0009 / 0.0013 written as "about 0.001".

## OPEN
1. `\CITE{Gangopadhyay et al. 2025, SA-UNet++ …}` is used twice (l.34, l.277). The paper is not in `references.bib` (also not in refs_extra.bib or chapters/*.bib) and must be added before submission. It is listed under MISSING_CITES in NOTES.
2. tab:repro-phase1, row ALHVR-20: the Welch interval +0.0289 [+0.0007, +0.0570] excludes 0 but carries no verdict word. The caption says "no rule was fixed before them" and "uncorrected", the audit item says one of 38 tests survives Bonferroni, and Section repro-alhvr shows the loss was barely applied. I left it as is. If the lead wants it explicit, add "(uncorrected; p 0.045, ST l.11)".
3. "flat from 10% to 100% labels (0.357, 0.354 and 0.346)" is a reading without a test, worded as the handoff words it (HO l.26). I left it.
4. The SA-MT-20 value 0.3384 has a single source (HO l.281). On 6 Oct the phase-1 notes still called it unverified (PH l.258).

## Checks done
- Every \ref target exists (ch:data, ch:deployment, ch:legacy, ch:protocol, ch:related, ch:t3b, sec:data-split, tab:T13a, tab:T13b, tab:T21, plus 13 internal labels).
- All 17 labels are unique across `chapters/*.tex` and `thesis_tables.tex`.
- All 10 cite keys exist in `references.bib`.
- The source has no unicode, no unescaped `%`, `_` or `#`, balanced `$` and 11 begin/end pairs.
- Rule 6: no host, user or path names; the industry partner is unnamed; no person is named except published authors.
- Consistency with the main text holds: ch03 (8 physical-cell twins, Jha's 1,769 of 2,289 test images in training lists, the pooled vs per-image contrast), ch05 (P-series from 10 Oct, test50 scored in every run), T13a and T13b (cited as the final-model versions; no shared value conflicts) and T21 (row AL1, 23 Oct).

**Numbers checked against the primary file:** about 210 of about 215. The rest were checked only against NOTES or a secondary record:
- the phase-0 numbers whose only surviving record is the phase-0/1 handoff (PH) itself (the code is lost);
- the 8-cell overlap, taken from the main text ch03;
- the A04 claim wording.
