# Review of benchmark protocol v1.0 and the info sheet template (protocol_reviewer, 22 Nov 2026)

Independent reviewer; I did not write either file. Files and sources only: no GPU, nothing on cv02, no sealed label or prediction
read (result and verdict files only). Tags: E = stated in the cited file (file:line), S = my judgement, "derived" = computed here
with the formula given. Short paths as in the v1.0 header (T = `/home/yugma/mtp/research/team_2026-11-12_frontier`).

## Pins
- Reviewed: `benchmark/PROTOCOL_v1.0.md` **0d18b4f136d2db522b3ae6a7b8a6a91d** (505 lines); `benchmark/INFO_SHEET_TEMPLATE.md`
  **29d63f257142f16ec11eb44dcdc77ef2** (118 lines). Both checked at the start of the review.
- Every md5 prefix in the v1.0 header equals the file on disk at the start of the review (40 files checked, 0 differ).
- Extra sources read: `log.md` 83175f3d, `BRIEF.md` bc06edd2, `log/brief_protocol_v02.md` de20794e,
  `harness/REVIEW_OPENING.md` f81cb703, `harness/final/opening/OPENING_REQUEST.md`, `benchmark/release_v1/LICENCE_AUDIT.md`
  f267ea23, `benchmark/release_v1/files/README.md` 690dac25, `results/final_tta_read/read.txt` 54214525, `results/W2A_READ.md`
  90c781a8, `results/stageB/B1_classbias_xfit.md`, `benchmark/README.md` 6aae7374, `benchmark/splits/README.md` 6e3c03a7,
  `benchmark/LABELS_V11.md` 70872c46.
- Moved while I reviewed (E, log 22 Nov 12:08 and 12:14): `results/HOUSEPF_READ.md` now exists (71e5a382) and
  `thesis/INFERENCE_COST.md` is now 81b3a953 (CPU latency written; GPU run still not run). v1.0 cites the older state; see N1.

## Verdict: **FIX**
No number in v1.0 or the C2 sheet differs from its cited source (111 checked, list at the end). The fixes are about rules
stated differently from the record, one claim placed under the wrong verdict word, missing rulings, silent drops from v0.2, and
what a third party needs to score a model.

## Blocking items

### B1. Entry class (a) is redefined without a record, and the G16 comparator of C2 is misdescribed (6.1, 6.4, IST A2, E6, J)
E:
- v1.0 l213 defines class (a) as "one set of weights, one forward pass, **or a fixed TTA stated in the card**" with "the
  same-model plain comparator", and cites "D brief 7, via `v0.2` 6.1". Brief 7 (`log/brief_protocol_v02.md` l12) says only
  "(a) trained single model; ... (c) ensemble, always printed beside the equal-cost comparator". v0.2 l128, l130: (a) "one set
  of weights, one forward pass"; (c) "several models or **views**". No log entry, rule or review moves a fixed-view TTA into (a).
- The opening's own review says the opposite: `REVIEW_OPENING.md` l100 "N4. **C2 is entry class (c)** by protocol 6.1 ('several
  models or views'; D4 = 8 views)", with the claim wording "C2 (HRNet-W18 U-Net++ + SWAD, D4: 8 views) against C1 (PF, one view)"
  (l104).
- G16 (`W3` l272): "Above 2x house training or inference cost, the PF 2-seed ensemble is printed as the equal-cost comparator.
  TTA rows print the view count." C2 costs 1,744 GFLOPs per cell, 11.8 x C1 (`IC` l23, l24).
- What was printed for C2: no PF 2-seed ensemble on any set. On CV5, PF_D4; on E1, C1-D4. ORULE introduced C1-D4 as "the
  candidate against the baseline with the same views" (l117), conditional on read (a) (l54 to l55), to separate the TTA part; it
  never names it as G16's comparator. ORULE and FOR never mention G16.
- C1-D4 is not equal cost: 1,184 against 1,744 GFLOPs per cell (0.68 x; `IC` l23).
- On E1 a PF ensemble does exist: E-PF (5 seeds, 740 GFLOPs). It was contrasted with C3 (S2) and C1 (S5), never with C2 (FOR
  l40 to l44). C2 - E-PF is only a point difference: 0.4897 - 0.4489 = +0.0408 (derived from `TT` l326, l328; no interval).
- No FLOP-matched PF comparator can be built from existing dumps: the C1-D4 E1 jobs wrote no logp (`IC` 4b57f062 l38), and no
  CV5 ensemble read exists (FRULE l42).
- The "model part" is read at unequal crack width. E1 width ratio C2 0.463, C1-D4 0.345, C1 0.458 (`TT` l326, l330, l325). So
  C2 / C1-D4 = 1.34 (derived), outside 0.85 to 1.15. FOR printed no guard for C2 - C1-D4 (l38). T3R l152 to l153: relF1@2 is
  "less width-sensitive than strict IoU but not immune".

S, answer to item 7 of the brief: the author is right that the comparator printed was PF at the same 8 views, not a PF 2-seed
ensemble. v1.0 must still say it differently:
- equal views is not equal cost;
- the deviation was not "stated" before v1.0;
- C2 is class (c) under the recorded rule;
- E-PF existed on E1 but was never set against C2;
- no equal-cost comparator for C2 exists in any read.

Fix:
1. 6.1 (a): restore "one set of weights, one forward pass" and the record "D brief 7, via `v0.2` 6.1". 6.1 (c): "several
   models or views; printed beside the equal-cost comparator". Example for (c): "C2 (one weight set per seed, 8 D4 views;
   scored per seed as a single model, FRULE s1; class (c) by views, `REVIEW_OPENING` N4) and C3 (5 models x 8 views)". If the
   writer wants TTA in (a), put it in section 11 as R7 (below), marked "proposed, not in force".
2. 6.4, replace the last two sentences of the G16 bullet with:
   > C2 with D4 is above the G16 line at inference (1,744 GFLOPs per cell, 11.8 x C1). G16's comparator, a PF 2-seed
   > ensemble, was not printed for C2 on CV5 or E1, and no FLOP-matched PF comparator exists in any read. Printed instead:
   > - same-view controls PF_D4 (CV5) and C1-D4 (E1), 1,184 GFLOPs, 0.68 x C2. They isolate the model part (C2 - C1-D4
   >   +0.0451 [+0.0173, +0.0699]) but are not equal cost, and on E1 they draw cracks thinner (width ratio C2 / C1-D4 =
   >   0.463 / 0.345 = 1.34, derived from TT T11a; no guard was printed for that contrast);
   > - on E1 only, E-PF (5-seed PF ensemble, 740 GFLOPs), contrasted with C3 and C1, not with C2. C2 - E-PF = +0.0408 at
   >   point level (derived, no interval).
   >
   > This deviation from G16 was not ruled before the opening and is disclosed here first (S). Ruling R7.
3. 6.1 (c) example: after "C3 beside E-PF" add "not equal cost (C3 = 11.8 x E-PF in FLOPs); no equal-cost comparator exists for
   C3 either".
4. IST A2: "(c) by views under v0.2 6.1 (`REVIEW_OPENING` N4): one weight set per seed, 8 views; each seed scored as a single
   model (FRULE s1); C3 is (c) as an ensemble. Class wording pending R7."
5. IST E6: "above the G16 line (11.8 x C1 in FLOPs). No equal-cost comparator printed. Same-view controls: PF_D4 on CV5, C1-D4
   on E1 (0.68 x C2 FLOPs; C2 / C1-D4 width 1.34, derived). E-PF (0.42 x C2) on E1, set against C3 only. Deviation from G16
   not ruled before the opening (R7)."
6. IST J(2): the same wording as E6, in short.

### B2. Licence and track: v1.0 understates what the records say about ELPV and SegFormer, and IST A5 puts C2 in the main track
E:
- v1.0 l85: ELPV is "reported as CC BY-NC-SA 4.0, unverified".
- v1.0 l86: SegFormer `mit_b2` has "licence field 'other' (`RR2` l85 to l93)". The same file records more: RR2 l11 "NVIDIA
  SegFormer licence, non-commercial"; l15 and l92 "research-only weights, benchmark row only".
- v1.0 6.2 (l220) requires such a row to say so. The segformer row of 7.2 (l320) does not.
- `benchmark/release_v1/LICENCE_AUDIT.md` (f267ea23, 22 Nov, written just after v1.0's 12:00 state) verifies the ELPV images as
  CC BY-NC-SA 4.0 (s2). Its decision D4 (s7) says: "The final model C2 uses HRNet-W18 (MIT) and trains on BMRK cells, so it is
  research-only as it stands". It also lists user decisions D1 to D6, which v1.0 does not mention.
- The user's own rule (log 15 Nov 12:40 (3)): "main model and benchmark only on data and weights with clear terms".
- IST A5 says C2 is "main".

Fix:
1. 2.4: "ELPV (BMRK cells): CC BY-NC-SA 4.0, verified 22 Nov (`benchmark/release_v1/LICENCE_AUDIT.md` s2); SDLE: CC BY 4.0
   (same file). SegFormer MiT-B2: NVIDIA SegFormer licence, non-commercial: research-only weights, benchmark row only (`RR2`
   l11, l15, l92; HF field 'other', l90)."
2. 7.2 segformer row, verdict cell: add "research-only weights, benchmark row only".
3. Rewrite R2 with options (see B3). State the fact first: every pool-trained row, C1 and C2 included, trains on the 50 BMRK
   (ELPV) cells, and BenchmarkEL states no licence. Cite LICENCE_AUDIT s7 D1 to D6.
4. IST A5: "track pending R2; research-only as trained (50 BMRK = ELPV cells, CC BY-NC-SA 4.0; LICENCE_AUDIT D4)".
5. 10 #8: cite LICENCE_AUDIT as the "list of cleared data and weights" that v0.2 Open 8 asked for (v0.2 l235).

### B3. Section 11: options are not separated from the recommendation, and needed rulings are missing
E: the table has only Question / Recommendation / Reason (l444). No ruling lists its options.

Fix (a). Add an "Options" column ahead of the recommendation, at least two options each:

| # | Options |
|---|---|
| R1 | (a) separate 2-seed screen tier (the current recommendation); (b) run the 5 rows to 5 seeds on cv5v3 (new runs, against D user 22 Nov 11:40); (c) drop the 5 rows from the tables |
| R2 | (a) "clear" = terms that allow research use as found, citation-request sources accepted, plus a commercial-use column (LICENCE_AUDIT s2 columns); (b) "clear" = an explicit licence that grants use: BenchmarkEL has none, so no current row qualifies; (c) main track without ELPV-derived cells (retrain without the 50 BMRK cells: new runs) |
| R3 | (a) keep 1.5 x PF, frozen; (b) an absolute bound per crack-free cell; (c) HOUSE as the reference. HRN l32 names option (c); v1.0 leaves it out |
| R4 | (a) window; (b) centre cell (re-scores every read; the centre-cell geometry is post hoc, AUD l61, and BMRK / SDLE have none, AUD l62) |
| R5 | (a) no ranks; (b) rank intervals from rank_stability on CPU; (c) point ranks |
| R6 | (a) freeze after the listed items; (b) freeze now with PENDING marked, then v1.1 |

Fix (b). Add the missing rulings:
- **R7**, entry class of a fixed-view TTA and the G16 comparator (B1). Options:
  - (a) keep v0.2: TTA is class (c); disclose that C2 has no equal-cost comparator (my recommendation, S);
  - (b) adopt v1.0's class (a) wording from a dated ruling, for future entries only;
  - (c) define equal cost in FLOPs per cell and require a FLOP-matched PF comparator for future entries above 2 x.
- **R8**, LICENCE_AUDIT s7 D1 to D6 (release licence, who approves publication, commercial use of BMRK cells and MiT-B2). D4
  decides whether C2 can be called the main-track final model.
- **R9**, AUD s5 question 3: report the 18 spurious-inactive cells with and without? AUD l190 to l191 addresses it to the user.
  v1.0 l453 answers it by S as "not a user ruling". Put it to the user with that recommendation, or log the user's answer.
- **R10**, E1 for outside entries. v1.0 3.5 says E1 stays zero-shot for an outsider (S). But:
  - the E1 masks are public (release 20221008);
  - there is no registration path for outsiders (TL section E is empty; EL holds team rows only);
  - C1's per-cell E1 records, needed for a seed-aware contrast, are not released (LICENCE_AUDIT s5).

  Options: (a) outsiders report E1 levels only, with a self-declared opening line in a public ledger; (b) outsiders send dumps
  and the team runs the contrast; (c) E1 is not offered to outside entries.

Fix (c). Add lead-level items to the note under the table:
- latency scope: v0.2 s11 item 4 says "measured once per row"; IC covers the E1 candidates only (lead's brief, log 22 Nov
  11:30);
- the HOUSE rule (B5);
- the duties that v1.0 marks "adopted as protocol (S)": l81, the 5.5 robustness duty (l201), and checklist item 9's new
  "carrying groups" clause (l467). An S tag cannot make protocol text; they need the lead's word.

Fix (d). R6 freeze conditions: add "this review PASS", "the lead's word on G17, G19, G20" and "R7 to R10 ruled".

### B4. 7.5 lists a non-inferiority claim under "CONFIRMED on CV5" (l364)
E: B5's rule (B5 l12 to l15) tests D4MS - PLAIN >= -M (non-inferiority). Its verdict is "msc_tta (D4MS) counts as a
non-inferior score arm" (B5 l3; log 19 Nov 01:24). It is a 2-seed read on cv5v2 (gaint) with no A/A in the read (B5 l7). v1.0
l29 says "On CV5 only D4 TTA on PF is CONFIRMED", so l364 also contradicts the file itself.

Fix. Move the sentence out of the CONFIRMED bullet into its own bullet:
> Passed a registered non-inferiority score claim (gaint, cv5v2, W1-G PF, 2 seeds, M from ROWS1): D4MS "counts as a
> non-inferior score arm", the first method to pass its full registered claim (19 Nov); D4MS - PLAIN relF1@2 +0.0142
> [+0.0079, +0.0202] (`B5` l3, l12; `log` 19 Nov 01:24).

### B5. Items of v0.2 dropped without a word (check 8)
E: none of these appears in v1.0 (grep), and section 14 does not drop them:
1. **HOUSE rule** (lead's ruling, W1C l56; v0.2 l172): "any arm that claims an in-distribution crack gain is also printed
   against HOUSE". C2's CV5 check was never printed against HOUSE: no CS_D4 - HOUSE exists, only HRNET - HOUSE (HRN l25).
2. relF1@1, @2 and @3 printed together (v0.2 l77; D HO5 L7). v1.0 5.1 (l137) keeps @1 only.
3. test50 "clean 42 without twins" (v0.2 l57). Opening #19 prints no clean-42 row (GAPS G-N9, open).
4. The 156 sealed rows of the cell tables carry label summaries that no reader uses or prints (v0.2 l63; a sealing rule).
5. "The ceiling bars nothing: a stride-4 row that passes the standard rule is a candidate like any other" (v0.2 l143).
6. The labelling pack: the user said yes on 15 Nov 12:40 (4), then "Q3 later" on 17 Nov 13:24 (v0.2 l190). Its state is not
   given.
7. "Label issues 3 to 8 of `draft` 2.5 ... are unchanged" (v0.2 l43). This covers the `_rf` crack-label issue (H36
   speck-level) and dotted labels, which AUD does not cover.
8. The screen's error rate, "0 of 15 A/A splits would be promoted" (v0.2 l116), and the MDEs for strict IoU, mIoU-R13 and
   inactive (v0.2 l121).

Fix: carry each item into its v1.0 section, or add a section 14 row that drops it with a reason. For item 1, either:
- carry the rule and add "not applied to CS_D4: no CS_D4 - HOUSE read exists; HOUSE - PF is in `results/HOUSEPF_READ.md`
  71e5a382"; or
- drop it with a dated ruling.

### B6. A third party cannot score a new model from v1.0 alone (check 9)
E: `benchmark/release_v1/files/README.md` (690dac25) s3 to s6 covers most of the steps: data layout, the v1.1 rebuild, folds,
the dump format, `bench_score.py` and `bench_read_w1.py`. v1.0 never cites it. Still missing from both:
1. **Release README not cited.** v1.0 6.6 or 12 should cite it with its md5 as the procedure.
2. **Class map.** The 24 class ids and names, and the 13 ids of mIoU-R13. v1.0 4 gives the 13 names only (l125). m0core and
   cellmeta use ids (crack 14, inactive 11).
3. **v1 definition.** l60 calls v1 "`masks_escdd`", an internal name. Give the LABELS_V11 s1 definition, or point to README s4.
4. **Distance and components.** Write out: Euclidean distance <= 2.0 px, inclusive (m0core l49); components 8-connected; a
   crack component "found" if >= 50% of its px are within 2 px; any-hit = at least 1 px; sizes >= 20 px for crack, >= 100 px
   for inactive (m0core l93 to l107); crack-free = no GT crack px under the scoring label set.
5. **Clusters for the sealed bootstrap.** "the stem without its cell suffix; SDLE stems end in `-cell<n>`" (ORULE l29 to l30).
6. **Comparator records.** A contrast needs the PF baseline's per-fold dumps and PF's own A/A (4 seeds) for M. Neither PF
   dumps nor the training code is released (LICENCE_AUDIT s7 D5 recommends not shipping training code). v1.0 must say which:
   - the entrant retrains PF from a published card on their own machine (then M comes from their own A/A, and "a read never
     mixes machines" applies); or
   - PF's pool out-of-fold per-cell records are released.
7. **E1 label view.** v1.0 2.2 states the rule, but `ext117/ignore` is a project file. Release README s7 says "no builder
   script in this release" (D6). Without it no outsider can rebuild the E1 scoring labels.
8. **E1 contrasts.** An outsider cannot compute the seed-aware contrast against C1 (C1's E1 records are not released), so only
   levels are comparable (R10).
9. **Rules for an entrant's own runs.** Final-step weights; unlabelled data only from `pool_t9_v2.txt`; no stem of
   `forbidden_v1.txt`; seed count; what to declare when the budget differs (G16). These are spread over 5.3, 6.4 and 6.5. Put
   them in one numbered list, or point to README s5.1.

Fix: add a short section "12.3 How to score a new entry", citing the release README by md5 and covering items 2 to 9.

## Non-blocking notes
- **N1. PENDING count.** l4 says "Two parts are PENDING", but l298 and section 13 also list HOUSE - PF. Since v1.0 was written:
  - `results/HOUSEPF_READ.md` (71e5a382) gives HOUSE - PF relF1@2 +0.0059 [-0.0043, +0.0152] and strict +0.0179 [+0.0093,
    +0.0266] (l12 to l13). The point values equal v1.0 l298;
  - `IC` 81b3a953 has CPU latency.

  Update l4, l298 and section 13. Section 13 should also list IST E5 as a place to fill.
- **N2. HRNet's failing guards.** l366 lists HRNet-W18's failing guard as "false crack px" only. HRN l3 and l18 (and v1.0 l287)
  also name ARTS width 1.162 (416, OP-W).
- **N3. Largest gain is stale.** l36 "the largest method gain (+0.015 relF1@2) is 0.6 of the relF1@2 shift" is AUD's value of
  19 Nov (AUD l104). Since 21 Nov, CS_D4 - PF is +0.0222 (selection-biased), which is 0.89 of the shift (derived: 0.0222 /
  0.025). Date the statement or update it.
- **N4. U2 / U4 date.** l378 and l380 say the U2 / U4 reads ran 21 Nov. They ran 19 Nov 01:23 to 01:28; the file was written
  21 Nov (U2U4 l5; log 21 Nov 00:24).
- **N5. Pool-list count rule.** l249: 1,475 is the pre-set rule's count; under rule B it is 1,003 (SPI l124). 3.1 uses rule B
  (561 modules). Add "(pre-set rule; 1,003 under rule B)".
- **N6. "Label-noise band".** l145 calls inactive's +-0.05 to 0.07 a "label-noise band". RAT l47 to l50 says the +0.069 from
  ignoring candidates "must not be read as label noise". Say "inactive band +-0.05 to 0.07 (interval size; AUD s2; RAT: mostly
  not label noise)".
- **N7. "Modules not in the pool".** l18 states "106 cells of modules not in the pool" as fact. Per GAPS G-W7, write "106 cells
  with no module link to the pool found (supported, not proven)".
- **N8. Guards "with every contrast".** l21 says so, but on E1 inactive is reported only, and on T3b width is not a guard. Add
  "(per set: 5.2)".
- **N9. Mis-cited record.** l22 cites `v0.2` s11 item 8 for "Sealed sets: OP-A only"; that item is about OP-C. Cite ORULE s2
  (and `REVIEW_OPENING` N5, which calls OP-A only on sealed sets a deviation from v0.2 5.4).
- **N10. Screen rule stated more strongly than applied.** l195 requires "width band held" for a screen pass. swad_const passed
  its screen with ARTS width 1.20 at argmax, treated as a flag (W2A l48, l54). Say: "pooled width held; per-source failures are
  flagged and re-checked at 5 seeds".
- **N11. OP-W missing from 7.1.** The 7.1 contrast table shows OP-A only, but the confirmation rule needs all four values (l196).
  Add OP-W columns (TT T6 and T7a hold them) or cite them.
- **N12. E1 summary without scope.** l28 gives the E1 result without its scope. GAPS D2 asks the summary to carry: mean over
  seeds 5 to 9; full cells carry it, half-cut n.d.; 101 of 106 cells CSIR; OP-A only; MDE about 0.074. Add "(scope: 7.4)" at
  least.
- **N13. IST H1 verdict words.** IST H1 prints only verdict.txt l170. GAPS G-D2 prints both l126 and l170 (as v1.0 l300 does).
- **N14. v0.2 contradiction 9.** Resolved by the cited record (E). Time: log 15 Nov 16:07; v0.2 s11 item 8 says 16:08. No
  change needed.
- **N15. Sections 9 and 10.** Contradictions 1 to 10 are resolved, superseded or partly resolved as stated; I checked each
  cited record (E). Open items: status right except #7 (latency scope narrowed without a ruling; B3) and #8 (now has
  LICENCE_AUDIT; B2).

## Numbers checked (111; "equal" = same string or same value at the stated rounding)
Source paths are the v1.0 short paths. `rd` = `results/final_tta_read/read.txt`. Line numbers are of the files as pinned.

| # | v1.0 line | Value | Source file:line | Result |
|---|---|---|---|---|
| 1 | 17 | 582 = 478 / 54 / 50, 24 classes | BRIEF:20 | equal |
| 2 | 18, 53 | E1 106 cells; CSIR 101, BMRK 5; 62 half-cut, 44 full; 71 clusters | ORULE:29 | equal |
| 3 | 19, 93 | 285 groups; 0 of 304 modules span | log:80 | equal |
| 4 | 20, 142 | convention band +-0.019 | FRULE:90; AUD:29 to 31 (max shift 0.0188, derived) | equal |
| 5 | 21, 150 | width band 0.85 to 1.15 | FRULE:78; ORULE:96 | equal |
| 6 | 21, 152 | false crack px <= 1.5 x reference | FRULE:80; ORULE:98 | equal |
| 7 | 23, 174 | M = max(0.01, 2 x SE of PF A/A) | FRULE:70 | equal |
| 8 | 23, 183 | sealed M 0.010 fixed | ORULE:87 | equal |
| 9 | 27, 111 | 19 counted openings, 24 Oct to 21 Nov | TL:26 | equal |
| 10 | 28, 349 | P +0.0430 [+0.0013, +0.1043] | FOR:23 | equal |
| 11 | 34 | 582 / 642 / 695 cells; 186 of 582 change split | v0.2:22 | equal |
| 12 | 36 | 0.320 vs 0.365; 0.822 vs 0.846; +0.015 = 0.6 of shift | AUD:101, 104 | equal (stale, N3) |
| 13 | 37, 72 | 0.233 / 0.365 / 0.414; relF1@2 0.824 / 0.846 / 0.849 | AUD:24 to 25 | equal |
| 14 | 38 | E-SCDD 44 of 82 test cells share a module | AUD:143 | equal |
| 15 | 38 | test50 8 same cell (7 pixels, 1 link), 7 neighbouring, 19 module | SPI:208 to 210; ERR:19 to 21 | equal |
| 16 | 39 | source balanced accuracy 0.94, chance 0.20 | AUD:119 | equal |
| 17 | 40 | ucf -0.0773 [-0.0892, -0.0594] | R1:22 | equal |
| 18 | 40 | pratt -0.0932 [-0.1113, -0.0774] | R1:23 | equal |
| 19 | 40 | hanifi -0.0064 [-0.0189, +0.0042] | R1:20 | equal |
| 20 | 43 | 22 full text, 7 abstract-level, 2018 to 2026 | RW:11 | equal |
| 21 | 43 | no interval 18; module-disjoint 0; overlap / selection 7 | RW:88, 92, 95 | equal |
| 22 | 43 | metric undefined 15; background 10; tolerant metric 0; unseen 0; all stated 2 | RW:97 to 101 | equal |
| 23 | 47 | 816 cells, 787 physical, 463 groups, 93 synthetic | v0.2:29 | equal |
| 24 | 51 | ARTS 182, BMRK 50, CFVS 169, CSIR 114, SDLE 17 | v0.2:33 | equal |
| 25 | 52 | test50 50 cells, 48 image ids | ORULE:30 | equal |
| 26 | 53 | crack in 32 cells, inactive in 10 | ORULE:194 | equal |
| 27 | 53, 152 | 74 crack-free E1 cells | FOR:26 | equal |
| 28 | 61 | masks_v11 MANIFEST 9c0e0687 | ORULE:77 | equal |
| 29 | 65 | train 16 cells 3,484 px; test 2 cells 236 px | v0.2:40 | equal |
| 30 | 65 | PFV1 - PF relF1@2 -0.0014 [-0.0099, +0.0064] | v0.2:42 | equal |
| 31 | 66 | relF1@2 contrasts move <= 0.0031 | AUD:32 | equal |
| 32 | 67 | E1 labels about 1.5 x wider | T3R:110 to 111 | equal |
| 33 | 72 | label shifted 1 px: IoU 0.483 | AUD:26 | equal |
| 34 | 73 | double annotation 0.259 / 0.829; vote 0.398 / 0.868 | AUD:40 to 41 | equal |
| 35 | 74 | 57% crack, 71% inactive outside centre; 117 of 229 | AUD:54 to 55 | equal |
| 36 | 75 | 31,039 px = 10.9%; 33 of 285 groups, n_eff 12.9 | AUD:68, 74 | equal |
| 37 | 75 | spurious inactive 30 of 40 model error | RAT:39 | equal |
| 38 | 76 | missed 1.8%, spurious 2.5%; no contrast > 0.003 | AUD:85, 87, 93 | equal |
| 39 | 76 | rater share 0.244 [0.105, 0.436] | RAT:32 | equal |
| 40 | 77 | widths 1.59 / 2.06 / 2.25 / 3.09; 10 of 24 classes | AUD:107, 111 | equal |
| 41 | 78 | 125 of 285 groups, n_eff 24.1; HRNET under M after 1; HOUSE 0 after 4 | AUD:128 to 130 | equal |
| 42 | 79 | 2 images sigma > 10; 41 look-alike pairs | AUD:137, 147 | equal |
| 43 | 82 | raters 29/30, 30/30, 60 items | RAT:23 | equal |
| 44 | 86 | HRNet weights e6bb005d, MIT | RR2:12, 85 | equal |
| 45 | 86 | mit_b2 licence field "other" | RR2:90 | equal (selective: RR2:11, 92 non-commercial; B2) |
| 46 | 92 | cv5v3.json 7a700b00, groups d880a769 | v0.2:263 | equal |
| 47 | 94 | held-out 107 / 110 / 103 / 101 / 111; 47 moved; spread 4 (9), 7 (8) | log:77 | equal |
| 48 | 95 | 700 image ids = 561 modules (rule B); 527 pre-set | SPI:301 | equal |
| 49 | 96 | score_exclude_v3 6d48dfbd; 116 excluded, 416 left | FRULE:99; log:77 | equal |
| 50 | 100 | cv5v2.json 441d118f, 330 groups | v0.2:48 to 49 | equal |
| 51 | 100 | 24 modules; 91 cells ARTS 48, CFVS 32, CSIR 11; 22.7% | SPI:302, 144 | equal |
| 52 | 101 | leakage DiD strict -0.0041 [-0.0136, +0.0069] (69 cells) | LEAK:11 | equal |
| 53 | 101 | leakage DiD relF1@2 +0.0026 [-0.0092, +0.0174] | LEAK:12 | equal |
| 54 | 102 | M 0.010, inactive 0.055 to 0.061 | SPI:305 | equal |
| 55 | 106 | DATA_MANIFEST 33e65b3f | log:227 | equal |
| 56 | 107 | F 821dfad steps 1 to 18,000; F2 9967d59 | ADD1:16 to 17 | equal |
| 57 | 118 | forbidden_v1 167 stems | v0.2:62 | equal |
| 58 | 119 | #8 4c783a77, 11:22:35; opened 11:25:30 to 12:06:09 | EL:31 to 32 | equal |
| 59 | 119 | #9 fb2c424c; registration 2 03:13, 5f18a820 | EL:33 to 35 | equal |
| 60 | 121 | largest inlier count 7; about a third testable | SPI:193, 194 (32%) | equal |
| 61 | 129 | gridline 0.302, splice 0.021; OP-C 0.362, 0.113, precision 0.20 | log:69 | equal |
| 62 | 129 | sp mono 0.243 to 0.166 | FOR:51 | equal |
| 63 | 143 | level band 0.48 to 0.60 | v0.2:85 | equal |
| 64 | 144 | annotator 95th percentile 2.000 px | v0.2:82 | equal |
| 65 | 145 | inactive band +-0.05 to 0.07 | ORULE:100; AUD:163 | equal (wording, N6) |
| 66 | 152 | crack-free 303 of 532, 226 of 416 | HRN:19 | equal |
| 67 | 156 | PF false px 212, share 0.13%, any-hit 0.884 | HRN:27; C3X:10; rd:5 | equal |
| 68 | 158 | HOUSE 3.7 x | HRN:27 | equal |
| 69 | 165 | OP-F A/A -0.0118 [-0.0357, -0.0005] | v0.2:100 | equal |
| 70 | 166 | OP-C 11 of 13 classes; variant 2 grid +8.0 | v0.2:101; log:69 | equal |
| 71 | 168 | OP-C +0.0137 [+0.0107, +0.0169]; +0.0126 [+0.0077, +0.0167] | v0.2:260 | equal |
| 72 | 173 | 2,000 draws; 285 / 330 groups; 95% percentile | FRULE:73; v0.2:108 | equal |
| 73 | 178 | cv02 cv5v2: 0.010 x 3; inactive 0.049 (15 splits) | v0.2:113 | equal |
| 74 | 179 | gaint: 0.010 x 3; inactive 0.054 | R1:36 | equal |
| 75 | 180 | cv02 cv5v2 416: 0.0111 | R2:28 | equal |
| 76 | 181 | cv5v3 532: 0.0100, A/A -0.0002, SE 0.0037 | C3X:28 | equal |
| 77 | 181 | inactive allowed drop 0.0462 | TT:167 | equal |
| 78 | 183 | E1 A/A +0.0022 [-0.0425, +0.0507], SE 0.0225 | FOR:45 | equal |
| 79 | 184 | U1 0.044 (frontier 0.064), strict 0.032 | U1:17 | equal |
| 80 | 188 | MDE 0.0087 / 0.0071 / 0.0055 | v0.2:121 | equal |
| 81 | 188 | E1 MDE 2.80 x 0.0265 = 0.0742 | TT:169; GAPS:13 | equal |
| 82 | 188 | T3b about +0.085 at SE about 0.030 | T3R:144 to 145 | equal |
| 83 | 215 | C3 8 x E-PF in forwards, 11.8 x in FLOPs | FOR:42; IC:24 | equal |
| 84 | 238 | PF 26,075,672 (21,278,400); 148.0; 5,736; 0.18 | RR2:67 | equal |
| 85 | 239 | HRNet 20,795,692 (10,947,028); 218.0; 8,430; 0.32 | RR2:69 | equal |
| 86 | 240 | C2 card 9,462 MiB; cv02 8,634 to 8,740 | log:180 | equal |
| 87 | 241 | SegFormer 24,722,008 (24,190,016); 50.0; 4; 7,444; 0.19 | RR2:68 | equal |
| 88 | 243 | per cell 148 / 740 / 1,184 / 1,744 / 8,722 GFLOPs | IC:23 | equal |
| 89 | 244 | HRNet 1.47 x FLOPs, 1.8 x step time | RR2:76 | equal |
| 90 | 245 | stride 4 about 0.02 / 0.02; stride 8 0.08 to 0.10 | R1:28 | equal |
| 91 | 246 | C2 E1 100 s per job, 0.94 s per cell | IC:36 (4b57f062) | equal |
| 92 | 249 | pool_t9_v2 4,949 (39877ede); pool_t9 6,424; 1,475 | v0.2:262; wc and md5 of the file | equal (rule mix, N5) |
| 93 | 254 | UCF-EL 227 images excluded | v0.2:137 | equal |
| 94 | 272 to 281 | T5 levels, 10 arms x 7 columns | TT:180 to 189; rd:5, 8, 11, 14, 17, 20 (PF, PF_D4, CS, CS_D4, CB, CB_D4) | equal |
| 95 | 287 | HRNET - PF +0.0104 [+0.0012, +0.0203]; +0.0115 [+0.00001, +0.0259]; strict +0.0008 [-0.0105, +0.0111] | HRN:10; HRNr:213 | equal |
| 96 | 288, 289 | SWADBN / SWAD - PF values and items | SWD:10 to 11, 15 to 16, 22, 24 | equal |
| 97 | 290 | COMBO - PF +0.0154 [+0.0065, +0.0260]; +0.0167 [+0.0055, +0.0298]; strict +0.0099 [-0.0007, +0.0207] | C3X:20 to 21; C3Xr:327 | equal |
| 98 | 291 | CS - PF +0.0166 [+0.0082, +0.0263]; +0.0176 [+0.0071, +0.0300]; strict +0.0161 | TTA:18; TT:206 | equal |
| 99 | 292 to 294 | (a), (b), (c) relF1@2 and strict intervals; ARTS 1.159 | TTA:15 to 17; TT:223 to 225 | equal |
| 100 | 295 to 297 | CS_D4 - PF_D4; HRNET - HOUSE; COMBO - HRNET / SWADBN | TT:227; HRNr:237 to 238; C3X:29 | equal |
| 101 | 298 | HOUSE - PF +0.0059; strict +0.0179 | AUD:155; HOUSEPF:12 to 13 | equal (now has intervals, N1) |
| 102 | 302, 304 | +0.0073, k_0 17 and 31; +0.0047, +0.0015; screen +0.0135 vs +0.0070 | AUD:155 to 158; SWD:29 | equal |
| 103 | 311 to 329 | T15 levels and T16a contrasts, 19 rows | TT:503 to 520, 532 to 545; R1:8 to 14, 19 to 23; R2:12 to 14, 21, 39, 53 | equal |
| 104 | 337, 338 | cards a4a46a52, 98f152de, commit 03375d4; SWAD 10,000 to 20,000 | FRULE:36, 43 | equal |
| 105 | 350 to 354 | G1 / G2 1.013; G3 2421 vs 3218 (0.75 x); G4 +0.0249; inactive +0.0996 [-0.0310, +0.2162]; strict +0.0263 [+0.0022, +0.0651]; fixed-model [+0.0067, +0.1007]; SE 0.0265 | FOR:23 to 29 | equal |
| 106 | 356 | levels C1 0.447 (0.439 to 0.457), C2 0.490 (0.466 to 0.507), C3 0.487, E-PF 0.449, C1-D4 0.445 | FOR:33; TT:325 to 330 | equal |
| 107 | 357 | beside: +0.0451, -0.0021, -0.0025, +0.0405, +0.0383, +0.0189, +0.0023 with intervals | FOR:38 to 44 | equal |
| 108 | 358 | strata CSIR, BMRK (with ERR levels), full, half-cut, crack cells | FOR:47 to 48; ERR:23 to 25 | equal |
| 109 | 359, 361 | errata wording; test50 v0 0.383 / 0.337, 0.588 / 0.570, 0.424 / 0.405; Pratt 0.25 / 0.38 / 0.28; PV-S3 0.441 / 0.418 vs 0.58; SEiPV 0.896, 0.903 vs 0.7447, 0.8604; v1.1 +0.0102 [-0.0094, +0.0291], +0.0322 [+0.0036, +0.0584], levels 0.891 / 0.901 / 0.901 | ERR:11 to 17, 28 to 29; FOR:54 to 60 | equal |
| 110 | 364 | (a) +0.0134; D4MS - PLAIN +0.0142 [+0.0079, +0.0202] | TTA:15; B5:12 | equal (verdict word wrong, B4) |
| 111 | 372, 377, 387, 390, 394 | T14 levels; U1 +0.0206 [-0.0518, +0.0744], 164 cells, n 17.7; folds 49e70413, 22 / 22 / 20 / 21 / 21, LISTS 5c86318a; jobs d77f3a94 / 9423cb91; severity MAE 0.12, kappa 0.78, CSIR 0.20, rho 0.56 / 0.91, 0.87 [0.80, 0.91] / 0.89 | TT:482 to 490; U1:6, 19; T3R:25 to 28; EL:35; SEV:12, 14, 20, 25 | equal |

### Info sheet, C2 column (every number)
| IST line | Value | Source file:line | Result |
|---|---|---|---|
| 72 | card 98f152de, commit 03375d4, SWAD 10,000 to 20,000 | FRULE:36 | equal |
| 73 | row card c89314d8; timm offline cache deviation | RR2:12, 41 | equal |
| 75 | rule 21 Nov 00:45 IST | FRULE:1 | equal |
| 76 | masks_v11 MANIFEST 9c0e0687 | ORULE:77 | equal |
| 77 | DATA_MANIFEST 33e65b3f | log:227 | equal |
| 78 | 7a700b00; d880a769 (285); 6d48dfbd (116 / 416) | v0.2:263; FRULE:99 | equal |
| 82 | E1 opening #8 | EL:27 | equal |
| 84 | 20,000 x 8, 512 px | FRULE:36; T3R:49 | equal |
| 85 | weights e6bb005d, MIT | RR2:12, 85 | equal |
| 86 | seeds 5 to 9 | FRULE:38 | equal |
| 88 | 03375d4; bench_infer 32e0b67c at F; F 821dfad; F2 9967d59; G 8bd1c27 | FRULE:54; ADD1:16 to 17; FOR:10 | equal |
| 89 | step 20000, key swad | ORULE:35, 42 | equal |
| 90 | about 1.9 h per training; about 107 min per screen run | log:299; R2:32 | equal |
| 91 | 9,462 MiB; 8,634 to 8,740; gate 11,510 | log:180 | equal |
| 93 | 8 views; softmax per view in fp32 | ORULE:42 | equal |
| 94 | log(p + 1e-12) | ORULE:42 | equal |
| 95 | batch 8, fp32, TF32 off | ORULE:66 | equal |
| 96 | seed 5 | FRULE:41 | equal |
| 97 | 20,795,692; encoder 10,947,028 | RR2:69; IC:20 | equal |
| 98 | 218.0 per view; 1,744 per cell | RR2:69; IC:23 | equal |
| 99 | stride 1 | RR2:69 | equal |
| 100 | 0.32 s per step (row card) | RR2:69 | equal |
| 101 | 0.94 s and 0.45 s per cell | IC:36, 47 (4b57f062) | equal |
| 111 | REGISTERED 4c783a77; rule 065a7ddd; test50 after 18 openings | FOR:8, 3; TL:49 | equal |
| 113 | user 21 Nov about 11:21 IST | log:282 | equal |
| 114 | CS_D4 0.3942 / 0.8684 / 0.5370 / 0.6232 / 98 / 1.0118; 416 0.8494; (c) +0.0222 [+0.0138, +0.0308], +0.0230 [+0.0127, +0.0341]; ARTS 1.159; (b) +0.0055 [-0.0002, +0.0115] | TT:188; rd:14; TTA:16 to 17 | equal |
| 115 | C2 0.4897 [0.4656, 0.5067]; P and intervals; G1 to G4; inactive; strict; full; half-cut; seed 5; test50 0.901 / 0.891, +0.0102 [-0.0094, +0.0291]; v0 0.383, 0.588, 0.424 | TT:491; FOR:23 to 29, 43, 48, 55, 58 to 60 | equal |
| 116 | COMBO k_0 31 | AUD:158 | equal |
| 117 | a95f89e8, 54214525, fdb56b78; 3a308b9c, 2b838801, d9a250a2, 2525575e, bbb5f3b4, e9169514 | TTA:5 to 6; FOR:5, 8 to 16 | equal |

## Round 2 (protocol_reviewer, 22 Nov 2026, about 12:55 IST)
Round 1 above is unchanged. Same rules: files and sources only, no GPU, nothing on cv02, no sealed label or prediction read.

### Pins, round 2
- Reviewed: `benchmark/PROTOCOL_v1.0.md` **09b8f12f5e72a6a06d7ffea518e1689a** (555 lines); `benchmark/INFO_SHEET_TEMPLATE.md`
  **c804163fbf04282961717b1861d7fed2** (118 lines). `v0.2` still b8b7f66a.
- New sources, md5 checked: `HPF` 71e5a382, `IC` 81b3a953, `LIC` f267ea23, `REL` 690dac25.
- Also read: `benchmark/release_v1/staging/e2e/E2E_RESULT.md` 29f4fb4f; release code `bench/cv5v3.py` 14b71c95 and
  `bench/classbias.py` 5e0dc317; `results/final_tta_read/read.txt` 54214525; `log.md` daf05087 (entries to 22 Nov 12:31).
- Method: I rebuilt the round-1 v1.0 text from my saved reads (md5 equal to 0d18b4f1) and diffed it with the new file. I
  checked every round-1 item against my own round-1 text above, not against the author's change table.

### Verdict, round 2: **FIX**
- All six round-1 blocking items and N1 to N15 are fixed as asked.
- Three new problems remain, each a one-sentence edit (R2-B1 to R2-B3).
- Once they are made, a diff check by the lead is enough. I see no need for a round 3.

### Blocking items, round 2

**R2-B1. R8 presents D3 as open and recommends against the user's 12:08 words without quoting them.**
E:
- `log` l355 quotes the user, 22 Nov 12:08: "dont worry about any permissions atleast for now, publish them all".
- R8 (l471) counts as ruled only D2 and, by the writer's reading, D1.
- For D3 (`LIC` s7: "Who must approve publication besides you"), R8 recommends (a) "ask the mentor and WattCycle in writing
  before the push". The user's words may already answer D3: publish without asking, "for now".

Fix in R8:
1. Quote the user's words.
2. Write: "The writer reads them as covering D1; they may also answer D3, publishing without asking, for now."
3. D3 options: (a) the user confirms that reading; (b) the user asks the mentor and WattCycle before the push.
   Recommendation (S): ask the user which reading holds.

**R2-B2. Section 1 (l36) "Since 21 Nov the largest CV5 contrast is CS_D4 - PF +0.0222" is not true.**
E:
- `results/final_tta_read/read.txt` l481: CB_D4 - PF, OP-A, relF1@2 +0.0243 [+0.0160, +0.0338] on 532 cells. It is a
  declared descriptive contrast (FRULE l94).
- On the 416 clean cells it is +0.0259 (l839).
- 0.0243 / 0.025 = 0.97 of the release shift (derived). Round-1 N3 asked only to date or update the line; the word "largest" is
  new.

Fix, replace the second sentence with:
> Since 21 Nov the C2 recipe on CV5 (CS_D4 - PF) is +0.0222 (selection-biased; `TTA`), 0.89 of the shift (derived: 0.0222 /
> 0.025). The largest CV5 contrast printed against PF is CB_D4 - PF +0.0243 [+0.0160, +0.0338] (information only;
> final_tta_read/read.txt l481), 0.97 of the shift (derived).

The section's point, that the label release moves levels more than any method, still holds, but only just (0.97 < 1).

**R2-B3. The "disagreement" 0.370 against 0.449 (s9 l441; s11 note l480) is a set difference, not a conflict.**
This settles the lead's question. E, `benchmark/release_v1/staging/e2e/E2E_RESULT.md` (29f4fb4f):
- Item 3 (l10 to l15): `bench_score.py summary` on cv5v3_f0 (107 cells). The oracle shifted 1 px scores strict crack IoU
  **0.3696** and relF1@2 0.9992.
- Item 5 (l20 to l25): `bench_read_w1.py` on all 532 out-of-fold cells (oracle dumps for all 5 folds). The shifted arm scores
  strict crack IoU **0.4492** and relF1@2 0.9990.
- `REL` l95 to l96 gives 0.370 and names the set ("oracle dumps of fold 0"). `log` l354 gives 0.449 without naming the set; it
  is the 532-cell value.
- Both values are right for their sets. The two also come from two different tools.

Fix:
1. s9 l441: replace the sentence with:
   > The release README's oracle check (strict crack IoU 0.370 for a 1-px shift, `REL` s5.4) is on fold 0 (107 cells);
   > `log` 22 Nov 12:01's 0.449 is on all 532 cells; both are in benchmark/release_v1/staging/e2e/E2E_RESULT.md (29f4fb4f)
   > items 3 and 5: a set difference, not a conflict.
2. s11 note (l480): drop "and the oracle-check value in `REL` s5.4 (s9)".

### Round-1 items: what I asked, and where the fix is now
| Item | Asked in round 1 | Now (v1.0 line) | Status |
|---|---|---|---|
| B1 (1) | 6.1 (a) back to "one set of weights, one forward pass"; (c) "several models or views"; C2 and C3 as (c) examples | l219, l221, l224 | fixed |
| B1 (2) | 6.4 G16 bullet replaced (no equal-cost comparator; same-view controls 0.68 x; width 1.34; E-PF only against C3 and C1; C2 - E-PF +0.0408; not ruled before the opening; R7) | l252 to l256 | fixed; derived values checked below |
| B1 (3) | 6.1 (c) example: C3 not equal cost (11.8 x) | l221 | fixed |
| B1 (4) to (6) | IST A2, E6, J(2) | IST l71, l102, l118 | fixed |
| B2 (1) | 2.4: ELPV verified, SDLE, SegFormer non-commercial | l86 to l88 | fixed |
| B2 (2) | segformer row flagged research-only | l333 | fixed |
| B2 (3) | R2 rewritten with the fact and options, citing `LIC` s7 | l465 | fixed |
| B2 (4) | IST A5 | IST l74 | fixed |
| B2 (5) | 10 #8 cites `LIC` as the cleared list | l453 | fixed |
| B3 (a) | Options column for R1 to R6 | l462 to l469 | fixed |
| B3 (b) | R7 to R10 | l470 to l473 | fixed (R8 fairness: R2-B1) |
| B3 (c) | lead-level note: latency scope, HOUSE rule, proposed duties | l475 to l480; marked "proposed" at l82, l207, l494 | fixed |
| B3 (d) | R6 conditions: review PASS, G17 / G19 / G20, R7 to R10 | l469 | fixed |
| B4 | B5's D4MS claim moved out of CONFIRMED | l377 to l378 | fixed |
| B5 1 | HOUSE rule carried, with "not applied to CS_D4" | l312, s14 row 25, s11 note | fixed |
| B5 2 | relF1@3: carry or drop with a reason | l142, s14 row 24 (dropped; S) | fixed (N21) |
| B5 3 | clean 42 | l117 | fixed |
| B5 4 | sealed-row label columns | l122 | fixed (`REL` l33 to l34 confirms identity columns only) |
| B5 5 | stride ceiling "bars nothing" | l257 | fixed |
| B5 6 | labelling pack state | l416 | fixed (N20 confirms "not filled") |
| B5 7 | label issues 3 to 8 | l67 | fixed |
| B5 8 | screen error rate; MDEs of all four metrics | l193, l194 | fixed |
| B6 1 | cite `REL` with md5 | l14, l271, l502 | fixed |
| B6 2 | class-id map and R13 ids | l504 | fixed; ids equal to release code (below) |
| B6 3 | v1 definition | l60 | fixed (`LAB` l7) |
| B6 4 | distance and component rules | l506 to l510 | fixed; equal to m0core l12, l47 to l49, l93 to l107 |
| B6 5 | sealed clusters | l511 | fixed |
| B6 6 | comparator records | l512; R8 | fixed |
| B6 7 | E1 label view | l513, s13 | PENDING, stated |
| B6 8 | E1 contrasts for outsiders | l514; R10 | fixed |
| B6 9 | entrant's own rules in one list | l503 | fixed |
| N1 | PENDING count; HOUSE - PF; IC; IST E5 in s13 | l4, l310, l521, l524 | fixed |
| N2 | HRNet's ARTS width in 7.5 | l380 | fixed |
| N3 | date or update the "largest gain" line | l36 | dated, but the new "largest" claim is wrong: R2-B2 |
| N4 | U2 / U4 read dates | l392, l394 | fixed |
| N5 | pre-set rule against rule B | l261 | fixed |
| N6 | "label-noise band" | l150 | fixed |
| N7 | "modules not in the pool" | l18 | fixed |
| N8 | guards "with every contrast" | l21 | fixed |
| N9 | mis-cited record for OP-A only | l22 | fixed |
| N10 | screen width rule as applied | l201 | fixed |
| N11 | OP-W columns in 7.1 | l297 to l310 | fixed; values checked below |
| N12 | E1 scope in section 0 | l28 | fixed |
| N13 | IST H1 both verdict words | IST l114 | fixed |
| N14 | none needed | | no change, right |
| N15 | Open #7 and #8 | l452, l453 | fixed |

### Section 11 rulings: are the options fair?
- Every ruling now lists its options apart from the recommendation, and each recommendation is marked S (l460, l462).
- R1 to R7, R9 and R10: fair. Each has two or three real options, including the costly one where it exists (R1 (b), R2 (c)).
- R3 now includes HOUSE as option (c), which `HRN` s4 names.
- R7 says the reviewer's recommendation and the writer's apart.
- R8: not fair as written (R2-B1). Also N19 below.
- No needed ruling is missing beyond R1 to R10 and the lead-level note.

### Equal-cost comparator, round 2
- 6.4 (l253 to l256), IST E6 and IST J(2) now say what the record supports:
  - no equal-cost comparator for C2 exists;
  - C1-D4 and PF_D4 are same-view controls at 0.68 x C2's FLOPs, with C2 / C1-D4 crack width 1.34;
  - E-PF was set against C3 and C1 only, and C2 - E-PF exists only as a derived point value;
  - the deviation was not ruled before the opening (R7).
- 6.1 is back to the v0.2 classes, with C2 in class (c) (`RVO` N4). Nothing more is needed here.

### Non-blocking notes, round 2
- **N16. Header time.** l3 still says "state of the files at about 12:00 IST". The file now cites records from 12:08 to 12:31,
  and s13 says "about 12:40". Update l3.
- **N17. RVP pin.** The header pins `RVP` at 7bfecedd, the round-1 state. This round-2 append changes the file's md5. Write
  "`RVP` round 1 7bfecedd; round 2 appended (md5 as sent by the reviewer)".
- **N18. IST template A5.** It says "research-only weights flagged". Write "research-only data or weights flagged": C2's limit
  comes from data (ELPV).
- **N19. R8 PF-records option (a).** Pool per-cell records are statistics derived from BenchmarkEL labels, the "unclear"
  class of `LIC` s1 and s4. Say so beside the option; the user's "publish them all" may cover it.
- **N20. Labelling pack, confirmed (E).** 8.5's "not filled" holds: `label_pack_U4/results.csv` and `results_short.csv`
  still equal `SHEETS_unfilled.md5` (1286a270, a87b27f6). It could be cited.
- **N21. relF1@3.** The drop is the writer's S against a lead's rule (HO5 L7, via `v0.2` l77). It is now explicit (s14 row
  24), as round 1 asked; the lead may confirm it in the s11 note.

### Numbers checked in round 2 (new or changed; 52 rows)
| # | v1.0 line | Value | Source file:line | Result |
|---|---|---|---|---|
| 1 | 28 | E1 MDE about 0.074 | TT:169 | equal |
| 2 | 31, 90 | MIT code, CC BY 4.0 lists and results; push blocked at 12:08 by a token | log:355 | equal |
| 3 | 36 | CS_D4 - PF +0.0222 | TTA:17 | equal |
| 4 | 36 | 0.89 of the shift (0.0222 / 0.025 = 0.888) | AUD:101 (+0.025) | equal (derived); "largest" wrong, R2-B2 |
| 5 | 60 | v1: E-SCDD 577 cells; 5 cells from 20211104 | LAB:7 | equal |
| 6 | 87 | 50 pool and 5 E1 BMRK cells | v0.2:33; ORULE:29 | equal |
| 7 | 87 | SegFormer non-commercial; HF field "other" | RR2:11, 15, 90, 92 | equal |
| 8 | 142 | read tool prints relF1@1 and @2 only | rd:4 (columns relF1_2, relF1_1) | equal |
| 9 | 150 | spurious inactive mostly model error | RAT:47 to 50 | equal |
| 10 | 193 | 0 of 15 A/A splits promoted | v0.2:116 | equal |
| 11 | 194 | strict 0.0083 / 0.0067 / 0.0052 | v0.2:121 | equal |
| 12 | 194 | mIoU-R13 0.0067 / 0.0055 / 0.0042 | v0.2:121 | equal |
| 13 | 194 | inactive 0.0518 / 0.0423 / 0.0328 | v0.2:121 | equal |
| 14 | 221, 253 | 11.8 x; 1,744 GFLOPs per cell | IC:23 to 24 | equal |
| 15 | 254 | 1,184 / 1,744 = 0.68 (0.6789) | IC:23 | equal (derived) |
| 16 | 254 | C2 - C1-D4 +0.0451 [+0.0173, +0.0699] | FOR:38 | equal |
| 17 | 254 | width 0.463 / 0.345 = 1.34 (1.342) | TT:326, 330 | equal (derived) |
| 18 | 255 | 740 / 1,744 = 0.42 (0.4243) | IC:23 | equal (derived) |
| 19 | 255 | 0.4897 - 0.4489 = +0.0408 | TT:326, 328 | equal (derived) |
| 20 | 257 | 0.159 / 0.533; 0.279 / 0.717; 0.521 / 0.955 at 1.365 | v0.2:143 | equal |
| 21 | 258 | C1 0.216 (0.233), E-PF 1.40 (1.48), C1-D4 2.23 (2.37) | IC:61 to 63 | equal |
| 22 | 258 | C2 3.88 (4.38), C3 16.6 (19.2); C2 18.0 x C1 | IC:64, 65 | equal (3.88 / 0.216 = 17.96) |
| 23 | 258 | RSS 1,376 MiB (batch 1), 4,382 MiB (batch 8) | IC:33 (column "RSS b1 / b8, 16 thr") | equal |
| 24 | 258 | C2 on E1 100 s per job, 0.94 s per cell | IC:81 | equal |
| 25 | 261 | 1,003 under rule B | SPI:124 | equal |
| 26 | 299 | HRNET - PF OP-W +0.0117 [+0.0019, +0.0220]; 416 OP-W +0.0126 [+0.0006, +0.0273] | HRN:10 | equal |
| 27 | 300 | SWADBN OP-W +0.0048 [-0.0036, +0.0141]; +0.0071 [-0.0025, +0.0176] | SWD:10 | equal |
| 28 | 301 | SWAD OP-W +0.0053 [-0.0022, +0.0128]; +0.0058 [-0.0030, +0.0150] | SWD:11 | equal |
| 29 | 302 | COMBO OP-W +0.0158 [+0.0069, +0.0264]; 416 OP-W +0.0166 [+0.0054, +0.0298] | C3Xr:344; c3x_read/read_x416.txt:335; HPF:39 | equal |
| 30 | 303 | CS - PF OP-W +0.0173 [+0.0087, +0.0272]; +0.0180 [+0.0076, +0.0305] | TT:206 | equal |
| 31 | 304 | (a) OP-W +0.0132 [+0.0062, +0.0205]; +0.0132 [+0.0047, +0.0223] | TT:223 | equal |
| 32 | 305 | (b) OP-W +0.0055 [-0.0009, +0.0118]; +0.0049 [-0.0033, +0.0125] | TT:224 | equal |
| 33 | 306 | (c) OP-W +0.0228 [+0.0141, +0.0320]; +0.0229 [+0.0124, +0.0340] | TT:225 | equal |
| 34 | 307 | CS_D4 - PF_D4 OP-W +0.0096 [+0.0022, +0.0172]; +0.0097 [+0.0013, +0.0192] | TT:227 | equal |
| 35 | 308 | HRNET - HOUSE OP-W +0.0083 [-0.0041, +0.0209] | HRNr:254 | equal |
| 36 | 310 | HOUSE - PF relF1@2, four values with intervals | HPF:12 | equal |
| 37 | 310 | HOUSE - PF strict +0.0179 [+0.0093, +0.0266] | HPF:13 | equal |
| 38 | 310 | ARTS width 1.307 / 1.167 / 1.370 / 1.190; CFVS 1.164 | HPF:26 | equal |
| 39 | 310 | false crack px 2.55 to 3.66 x PF; 9 items | HPF:27, 30 | equal |
| 40 | 377 | (a) +0.0134 [+0.0066, +0.0207] | TTA:15 | equal |
| 41 | 378 | D4MS - PLAIN +0.0142 [+0.0079, +0.0202]; 2 seeds; no A/A | B5:3, 7, 12 | equal |
| 42 | 380 | HRNet ARTS width 1.162 (416, OP-W) | HRN:18 | equal |
| 43 | 392, 394 | reads 19 Nov 01:23 to 01:28 | U2U4:5 | equal |
| 44 | 416 | pack: yes 15 Nov 12:40; "Q3 later" 17 Nov 13:24; 24 cells | log:51, 135; v0.2:190 | equal |
| 45 | 441 | 0.370 against 0.449 | REL:96; log:354; E2E_RESULT:15, 24 | values equal; "disagreement" wrong, R2-B3 |
| 46 | 503 | 167 stems = test50 + 106 E1 + 11 | REL s5.1 | equal |
| 47 | 504 | 24 class ids, 0 background to 23 meas_artifact | release `bench/cv5v3.py` l23 to l25 (14b71c95) | equal |
| 48 | 504 | mIoU-R13 ids 0, 1, 2, 4, 5, 7, 11, 13, 14, 15, 16, 20, 21 | release `bench/classbias.py` l35 (5e0dc317); names in v1.0 l129 | equal |
| 49 | 507 to 509 | <= 2.0 px; 8-connected; >= 20 px, >= 50%, any-hit; inactive >= 100 px by overlap | m0core:12, 47 to 49, 93 to 107 | equal |
| 50 | 511 | 71 and 48 clusters | ORULE:29 to 30 | equal |
| 51 | 520 | 8 of 33 trained and relayed (12:09) | log:357 | equal |
| 52 | IST 101 | C2 CPU 3.88 (4.38), 18.0 x, 1,376 MiB; wall 0.94 and 0.45 s per cell | IC:64, 33, 81, 92 | equal |
