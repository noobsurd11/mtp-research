# Corrected split cv5v3: build (stage C, 15 to 16 Nov 2026)

Task: lead's ruling of 15 Nov 22:14 (log.md; PROTOCOL_v0.2 s11 item 10 (d)): the final 5-seed table is trained on a corrected split cv5v3, built and reviewed before any 5-seed run. Builder: cv5v3 builder. Code: /home/noob/work/bench_wt_cv5v3, branch bench_cv5v3 from bench_split f966127.
Tags: E = measured here (file named), S = judgement. Nothing trained, no GPU. No label, mask, prediction or label summary of a sealed (legacy test, E1) cell read; cells.tsv only through `udev.load_cells_safe`; v1.1 masks read for the 532 pool cells only.

## 1. Rule (written before the build script was run; not changed after)

### 1a. Groups
Unit: a pool cell (one of the 532 stems of cv5v2). Two pool cells are in one cv5v3 group if they are joined by a chain of these links (connected components):
- L1 the same cv5v2 group (`cv5v2_groups.tsv` column `group`; an existing group is never split);
- L2 the same image id;
- L3 the same physical module under rule B (`module_identity_v3.tsv` column `physical_module`, keyed by image id; the doubted links CSIR_00034 / CSIR_02431 and ARTS_00150 / ARTS_00151 stay in, as the file has them);
- L4 the four open image-id pairs named in the header of `score_exclude_v2c.txt` (ARTS_00007 | ARTS_00063, CFVS_00098 | CFVS_00102, CFVS_00106 | CFVS_00109, CFVS_00150 | CFVS_00151), taken as linked; the script parses them from the header and asserts that exactly these four are found;
- L5 the same `module_group` in cells.tsv (the earlier module links, kept also where the audit found no pixel support or dropped the link, e.g. ARTS_00040 / ARTS_00061).
Group name: the smallest cv5v2 group name inside the component.
The pre-set rule's module column (`physical_module_fixed_rule`) is not a link; the script reports whether adding it would change any group.

### 1b. Folds
- R1 A group whose cells all sit in one cv5v2 fold keeps that fold.
- R2 A group that spans cv5v2 folds goes to the fold that holds most of its cells (count of pool cells).
- R3 Ties under R2 (two or more folds hold the same largest count): the tied fold that gives the smallest balance cost B, then the lowest fold number. B = sum over the 5 folds of (crack cells in fold - mean)^2 + sum over the 5 folds of (inactive cells in fold - mean)^2, computed on the held-out fold counts after the group is placed. Crack cell = at least one class-14 px, inactive cell = at least one class-11 px, both in the v1.1 training masks (`bench_data/masks_v11/masks`, 255 = ignore, not counted).
- Order: first every R1 group keeps its fold and every R2 group without a tie is placed; then the tied groups are placed one at a time in ascending group name, each seeing the counts left by the groups placed before it.
- No model result, read or score of any kind is an input. The rule uses only the files of 1a, cells.tsv non-label columns plus the v1.1 masks of pool cells.
- Output order: every list in pool order (legacy train.txt then val.txt), list md5 = md5 of '\n'.join(stems) + '\n' (the cv5v2 format rules).

### 1c. Checks (each printed with PASS / FAIL in `cv5v3_check.txt`; the split is accepted only if all pass)
- C1 no cv5v3 group spans folds; and separately none of: cv5v2 group, image id, rule-B physical module, cells.tsv module_group, open pair spans folds.
- C2 no forbidden (`forbidden_v1.txt`) or sealed (cells.tsv role test / E1) stem, base stem or _rf form in the pool or in any list; do-not-train guard (`bench.donottrain.assert_clean`, list md5 5a22e8cc) on every list.
- C3 every pool cell in exactly one held-out list; per fold train and held-out disjoint, union = pool, both in pool order, md5s as written into the JSON.
- C4 per fold, cv5v2 beside cv5v3: cells, groups, crack cells, inactive cells, crack px, inactive px, cells per source, cells per cell type (cells.tsv `cell_type`). Pass rule: (a) for cells, crack cells and inactive cells the spread over folds (max - min) is not larger than in cv5v2 by more than 2; (b) per source and per cell type the spread is not larger than in cv5v2 by more than 2; (c) no fold has a source or cell type in its held-out list that is absent from its training list unless cv5v2 already had that (source or type, fold) case. Every increase of a spread, also within the tolerance, is printed as "worse by n".
- C5 classes with held-out px and 0 training px in some fold (v1.1 training masks, classes 0 to 23): the set of (class, fold) cases of cv5v3 must be a subset of cv5v2's, or each new case must replace a cv5v2 case of the same class (same number of such cases per class or fewer).
- C6 determinism: a second run writes byte-identical files (`--check` mode recomputes and compares bytes).

### 1d. Moved cells
Every cell whose cv5v3 fold differs from its cv5v2 fold is listed with its group, the folds of the group before, the fold kept and the reason (R2 majority, or R3 tie with the cost of each tied fold). The list is compared with the audit's proposal (`cv5v3_proposal.tsv`, 31 moves); every difference is explained.

(Record: section 1 stood in this file at 15 Nov 23:4x before any script existed; md5 of the file then f9429895, frozen copy /home/noob/work/bench_reads/stageC/cv5v3/CV5V3_BUILD_rule_frozen.md. Nothing in section 1 was changed after.)

## 0. Outcome in short
1. Split files written and reproducible: `benchmark/splits/cv5v3.json` (f116d37d), `cv5v3_groups.tsv` (d8679d4b), `cv5v3_check.txt` (34f6ac6d), `cv5v3.md5` (de1d061e). A second run (`--check`) and a third run into the scratchpad give byte-identical files.
2. 299 groups (cv5v2 330). 26 groups spanned cv5v2 folds: exactly the 99 cells of `score_exclude_v2c.txt`. **35 cells move** (ARTS 19, CFVS 12, CSIR 4), 497 keep their fold.
3. Checks C1, C2, C3, C5 pass; C6 passes. **C4 fails**: held-out fold sizes 104 / 124 / 102 / 98 / 104 (cv5v2 107 / 111 / 104 / 104 / 106), and the ARTS, CFVS and multi spreads grow. Crack-cell and inactive-cell balance improve. E: no split that keeps R1 and R2 can pass "not worse" on cells or CFVS (fold 1 holds at least 112 cells under R1 + R2). **The lead's fold rule and the lead's balance check conflict; the lead decides (section 7).**
4. Roots `/home/noob/work/bench_data_v3/roots/cv5v3_v11_f0..f4` built by the reviewed root builder (every assert OK, `--check` OK), and they pass the LOSO-2 root checks carried over (96 PASS, 0 FAIL). Sets `cv5v3_f0..f4` registered in bench/sets.py with md5 pins; full pytest 658 passed, 4 skipped.
5. New fact for the lead: **SDLE stems name their module** (A1, A10, A11). The 17 SDLE pool cells come from 3 modules spread over all 5 folds. The audit called SDLE undecidable; the rule has no SDLE link (section 6).
6. Nothing trained, no GPU, no existing split / list / root / queue changed (md5 check of all 20 earlier files in benchmark/splits).
7. **Review (harness/REVIEW_CV5V3.md): FAIL on item 4 only (C4), groups / folds / lists / roots / nothing-else-changed PASS.** The reviewer's fixes F1 (C4) and F2 (SDLE links) are rulings for the lead. Fix round 1 (section 11, 16 Nov) does not choose for the lead: it makes every ruling a one-command rebuild (builder options, defaults = frozen rule, published files unchanged), builds the four candidates outside benchmark/splits, does the in-branch part of F3, fixes the F4 wording and corrects one fact (the clamp cell is ARTS_00008_r4_c1). **The split stays not accepted until the lead rules on F1 and F2.**
8. **Review round 2 (REVIEW_CV5V3.md): FAIL on item 4 only again, no builder error; items 1 to 3 PASS for the published split and candidates a to d.** Fix round 2 (section 12) does the two builder items: F5 states that tied groups not yet placed count in their cv5v2 fold while a tie is costed (as the code always did; candidate c depends on it), F6 fixes the stale docstring. No split file, candidate, root or pin changed. F1 and F2 are still the lead's.
9. **Lead's ruling 16 Nov 00:39: cv5v3 = candidate d** (`--sdle-links --tie-break fewer --c4-scope scoring`). Applied in section 13: benchmark/splits files of a replaced by d (cv5v3.json 7a700b00, cv5v3_groups.tsv d880a769, cv5v3_check.txt 2afc4cc6, cv5v3.md5 400c1353; copies of a in results/stageC/cv5v3/replaced_a/), pins and sets re-pinned (bench_cv5v3 c417732), meta and roots in /home/noob/work/bench_data_v3b (ROOTS_cv5v3_v11.md5 79e8aee8), every check PASS, full pytest 667 passed. Sections 2 to 8 describe candidate a as first built; section 13 holds d's numbers. Waits for the delta review; bench_data_v3 (a's roots) stays until it passes.

## 2. Groups (E: cv5v3_check.txt)
| links used | groups | groups spanning cv5v2 folds |
|---|---|---|
| L1 cv5v2 groups | 330 | 0 |
| + L2 image id | 330 | 0 |
| + L3 rule-B physical module | 303 | 24 |
| + L4 four open pairs | 299 | 26 |
| + L5 cells.tsv module_group | 299 | 26 |
- L5 adds nothing on pool cells: every cells.tsv module link between pool image ids is already in L1 (cv5v2 groups were built from the same table). The prior link the audit dropped (ARTS_00040 / ARTS_00061, different serials) stays linked: both image ids hold pool cells in fold 4, already one cv5v2 group.
- Adding the pre-set rule's module column changes no group (E: `adding the pre-set rule's module column ... changes no group: True`), as the audit said.
- The doubted links CSIR_00034 / CSIR_02431 and ARTS_00150 / ARTS_00151 are inside rule B and stay in; they touch no second fold (CSIR_00034, CSIR_02431 and ARTS_00151 hold no pool cells).
- Crack cell from the v1.1 masks agrees with cells.tsv crack_px_v11 > 0 on 532 of 532 cells.

## 3. Moved cells (E: results/stageC/cv5v3/cv5v3_moves.tsv; reason per cell there)
26 groups spanned folds: 17 placed by R2 (majority), 9 ties placed by R3. 35 cells move.

| group (cv5v2 folds: cells) | fold kept | reason | moved cells |
|---|---|---|---|
| ARTS_00002 (f1:7, f2:3) | 1 | R2 | ARTS_00002_r3_c2, _r4_c2, _r6_c1 |
| ARTS_00006 (f2:2, f3:1) | 2 | R2 | ARTS_00006_r10_c3 |
| ARTS_00007 (f0:1, f3:2; open pair) | 3 | R2 | ARTS_00063_r5_c3 |
| ARTS_00008 (f1:3, f3:3) | 1 | R3, cost 86 = 86, lower fold | ARTS_00008_r3_c6, _r4_c1, _r6_c4 |
| ARTS_00011 (f0:3, f4:2) | 0 | R2 | ARTS_00024_r11_c6, _r2_c1 |
| ARTS_00013 (f3:1, f4:2) | 4 | R2 | ARTS_00026_r1_c6 |
| ARTS_00019 (f2:2, f4:1) | 2 | R2 | ARTS_00032_r12_c3 |
| ARTS_00025 (f0:1, f4:2) | 4 | R2 | ARTS_00025_r8_c1 |
| ARTS_00029 (f0:2, f2:3) | 2 | R2 | ARTS_00029_r2_c5, _r4_c3 |
| ARTS_00106 (f2:1, f4:3) | 4 | R2 | ARTS_00106_r1_c5 |
| ARTS_00111 (f0:1, f3:1) | 0 | R3, 86 = 86, lower fold | ARTS_00114_r1_c6 |
| ARTS_00118 (f1:1, f2:1) | 1 | R3, 86 = 86, lower fold | ARTS_00119_r1_c4 |
| ARTS_00165 (f1:1, f3:1) | 3 | R3, f3 84 < f1 92 | ARTS_00166_r12_c5 |
| CFVS_00017 (f3:7, f4:1) | 3 | R2 | CFVS_00019_r1_c4 |
| CFVS_00065 (f2:2, f3:1) | 2 | R2 | CFVS_00070_r1_c4 |
| CFVS_00076 (f2:1, f4:1) | 2 | R3, 84 = 84, lower fold | CFVS_00082_r1_c1 |
| CFVS_00088 (f1:3, f2:1, f4:2; open pair 00106 / 00109) | 1 | R2 | CFVS_00106_r12_c1, CFVS_00109_r11_c1, _r1_c2 |
| CFVS_00098 (f0:1, f3:1, f4:6; open pair 00098 / 00102) | 4 | R2 | CFVS_00098_r1_c6, CFVS_00101_r5_c1 |
| CFVS_00132 (f0:2, f3:1) | 0 | R2 | CFVS_00134_r6_c3 |
| CFVS_00150 (f1:2, f2:1; open pair) | 1 | R2 | CFVS_00151_r3_c1 |
| CFVS_00156 (f1:1, f4:1) | 1 | R3, 84 = 84, lower fold | CFVS_00156_r5_c6 |
| CFVS_00168 (f0:1, f4:1) | 4 | R3, f4 70 < f0 84 | CFVS_00170_r2_c4 |
| CSIR_00104 (f0:1, f3:3) | 3 | R2 | CSIR_00104_r4_c5 |
| CSIR_00106 (f0:1, f2:1) | 0 | R3, 70 = 70, lower fold | CSIR_00106_r6_c1 |
| CSIR_00107 (f1:2, f3:1) | 1 | R2 | CSIR_00107_r9_c3 |
| CSIR_00178 (f0:1, f1:1) | 1 | R3, f1 68 < f0 76 | CSIR_00207_r7_c5 |
Group names are the smallest cv5v2 group inside (so ARTS_00019 is the audit's module ARTS_00018, ARTS_00025 its ARTS_00012, ARTS_00029 its ARTS_00016, CFVS_00098 its CFVS_00101 joined with CFVS_00098).

### 3a. Against the audit's proposal (E: cv5v3_vs_proposal.tsv, 24 cells end in a different fold)
Proposal 31 moves, cv5v3 35; 21 moves in both, 14 only in cv5v3, 10 only in the proposal. Every difference has one of two causes:
- **Open pairs taken as linked (L4; the proposal did not link them): 4 cells.** ARTS_00063_r5_c3 (f0 -> f3, joins ARTS_00007's two f3 cells); CFVS_00098_r1_c6 (f0 -> f4, joins the CFVS_00101 module, 6 cells in f4); CFVS_00106_r12_c1 (f2 -> f1, joins the CFVS_00088 group, 3 cells in f1); CFVS_00151_r3_c1 (f2 -> f1, joins CFVS_00150's two f1 cells).
- **Tie rule (lead's R3 against the proposal's "smaller fold"): 20 cells in 9 groups.** Equal cost, lower fold wins in cv5v3: ARTS_00008 (kept f1, proposal f3: 6 cells differ), ARTS_00111 (f0 v f3), ARTS_00118 (f1 v f2), CFVS_00076 (f2 v f4), CFVS_00156 (f1 v f4), CSIR_00106 (f0 v f2): 2 cells each. Lower cost wins in cv5v3: CFVS_00168 (f4, cost 70 v 84; proposal f0), CSIR_00178 (f1, 68 v 76; proposal f0): 2 cells each. ARTS_00165 ends in f3 under both rules.
- Count: 4 + 6 + 5 x 2 + 2 x 2 = 24.

## 4. Balance (E: results/stageC/cv5v3/cv5v3_balance.md, cv5v3_class_cells.tsv; held-out cells per fold, cv5v2 / cv5v3; crack and inactive from the v1.1 training masks)
| fold | cells | groups | crack cells | inactive cells | crack px | inactive px | ARTS | BMRK | CFVS | CSIR | SDLE | dogbone | mono | multi | no_spacing |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 107 / 104 | 66 / 59 | 51 / 48 | 10 / 12 | 49,311 / 56,251 | 56,753 / 57,585 | 36 / 35 | 10 / 10 | 34 / 33 | 23 / 22 | 4 / 4 | 2 / 2 | 47 / 45 | 47 / 46 | 11 / 11 |
| 1 | 111 / **124** | 67 / 66 | 44 / 48 | 8 / 8 | 60,467 / 60,972 | 57,565 / 57,565 | 39 / 45 | 10 / 10 | 36 / 41 | 22 / 24 | 4 / 4 | 1 / 1 | 49 / 55 | 48 / 55 | 13 / 13 |
| 2 | 104 / 102 | 63 / 56 | 46 / 43 | 7 / 7 | 57,196 / 56,738 | 57,142 / 57,142 | 37 / 36 | 10 / 10 | 31 / 31 | 23 / 22 | 3 / 3 | 0 / 0 | 36 / 36 | 56 / 54 | 12 / 12 |
| 3 | 104 / **98** | 67 / 57 | 46 / 47 | 15 / 14 | 99,932 / 92,831 | 56,785 / 56,334 | 34 / 30 | 10 / 10 | 34 / 32 | 23 / 23 | 3 / 3 | 0 / 0 | 53 / 51 | 39 / 35 | 12 / 12 |
| 4 | 106 / 104 | 67 / 61 | 42 / 43 | 8 / 7 | 40,640 / 40,754 | 56,775 / 56,394 | 36 / 36 | 10 / 10 | 34 / 32 | 23 / 23 | 3 / 3 | 0 / 0 | 56 / 54 | 39 / 39 | 11 / 11 |
| spread | 7 / 26 | 4 / 10 | 9 / 5 | 8 / 7 | | | 5 / 15 | 0 / 0 | 5 / 10 | 1 / 2 | 1 / 1 | 2 / 2 | 20 / 19 | 17 / 20 | 2 / 2 |
- Training set sizes: 428 / 408 / 430 / 434 / 428 (cv5v2 425 / 421 / 428 / 428 / 426).
- Classes with held-out px and 0 training px: cv5v2 belt_mark f0, rings f2, clamp f3; cv5v3 belt_mark f0, rings f2, **clamp f1**. Same 3 classes, one case each: C5 pass. (Corrected 16 Nov, fix round 1, E: the one pool cell with clamp px is **ARTS_00008_r4_c1** (1,238 px), not CSIR_00107_r9_c3 as written here before and in the review. It sits in the tied group ARTS_00008 (f1:3, f3:3), which the frozen tie rule sends to f1; under I3 it stays in f3 and the clamp case is the cv5v2 one.)
- No fold holds out a source or cell type that its training list lacks (both splits).

## 5. Checks (E: benchmark/splits/cv5v3_check.txt; roots: /home/noob/work/bench_reads/stageC/cv5v3/check_roots.out)
| Check | Outcome |
|---|---|
| C1 no group spans folds; nor cv5v2 group, image id, rule-B module (cv5v2: 24 span), pre-set-rule module, module_group, any open pair | PASS (0 each) |
| C2 forbidden / sealed / do-not-train stems in the pool and every list | PASS (0; udev.assert_open and donottrain.assert_clean on every list) |
| C3 held-outs partition the pool; per fold disjoint, union = pool, pool order, md5 rule | PASS |
| C4a spread of cells / crack cells / inactive cells not worse than cv5v2 by more than 2 | **FAIL** cells 7 -> 26; crack 9 -> 5, inactive 8 -> 7 pass |
| C4b spread per source / cell type | **FAIL** ARTS 5 -> 15, CFVS 5 -> 10, multi 17 -> 20; BMRK, CSIR, SDLE, dogbone, mono, no_spacing pass |
| C4c source / type held out but absent from training | PASS (none, both splits) |
| C5 classes with no training px | PASS (3 cases in both; clamp f3 -> f1) |
| C6 determinism | PASS (--check 9 of 9 files byte-identical; third run cmp-identical) |
| Roots: every bench_make_roots assert, --check | PASS (`0 of 299 groups split; held-outs partition 532; lists = cv5v3.json`; ROOTS_cv5v3_v11.md5 9c148c7e) |
| Roots: LOSO-2 checks carried over | PASS (96 / 96): lists = groups file = JSON, test == val, 0 duplicates, 0 forbidden / sealed / do-not-train, 0 shared cv5v3 group / cv5v2 group / module_group / image id / rule-B module / open pair, 532 mask links per root (train -> masks, held-out -> masks_strict, 0 wrong, 0 dangling), labeled -> house dir, layout and MASKLINKS header = wave 1, SPLITS / DATA_MANIFEST / ROOTS md5sum -c OK, held md5 = JSON = sets.py pin, held-outs partition the pool |
- Why C4 cannot pass under R1 + R2 (E, information lines I1 to I3 of cv5v3_check.txt): R2 moves alone (ties left in place) put 119 cells in fold 1 (ARTS_00002 +3, CFVS_00088 +3, CFVS_00150 +1, CSIR_00107 +1). The tied groups can take at most 7 cells out of fold 1, so **fold 1 holds at least 112 cells under R1 + R2** (cv5v2's largest fold 111); the CFVS spread is at least 8 (cv5v2 5). The tie rule adds the rest: 6 of the 9 ties have equal balance cost (no crack or inactive difference) and go to the lower fold, 3 of them into fold 1 (ARTS_00008, ARTS_00118, CFVS_00156); CSIR_00178 goes to fold 1 by cost. Variant I3 (equal cost -> fewer cells) gives 104 / 114 / 104 / 104 / 106, ARTS spread 3, CFVS 8, still a C4 fail on cells (7 -> 10) and CFVS.
- One root check was adapted after its first run (disclosed): LOSO-2 required "no near-duplicate pair at NCC >= 0.85 across train and held-out". No within-source 5-fold split meets that (cv5v2 roots: 1,160 such pairs summed over folds; BMRK / SDLE smooth cells and ARTS look-alike edge cells, ungrouped by decision, splits/README). Carried over as: 0 md5-identical or known same-cell pairs across (cv5v2: the two dup_crossfold_v1 pairs, each in both of its folds and listed twice in the inputs: 8 entries) and a total at >= 0.85 not above cv5v2 (cv5v3 1,152, cv5v2 1,160). 3 pairs at >= 0.85 cross in cv5v3 and not in cv5v2: ARTS_00026 / ARTS_00102 / ARTS_00114 r1_c6 (NCC 0.945 to 0.953), corner crops with the printed serial band; ARTS_00026 and ARTS_00114 moved with their modules (ARTS_00013, ARTS_00111), and serial evidence puts the three in different modules (S: look-alikes of the kind cv5v2 left ungrouped). 5 pairs crossing in cv5v2 no longer cross.
- DATA_MANIFEST.md5 of each cv5v3 root equals the cv5v2 root of the same fold (E): it lists every pool image and the mask each root links, and masks and masks_strict differ only on 15 pool cells (the v1.1 ignore edits), none of which moved.

## 6. What remains uncertain
1. **SDLE module names (new, E).** Stems read SDLE_<n>_<module>-<test>-<hours>-PT-cell<k>. Pool cells: A1 7 cells (cv5v2 folds 0:2, 1:2, 2:1, 3:1, 4:1), A10 2 (folds 2, 3; A10 also holds one legacy-test cell), A11 8 cells at 500 h, 2500 h, 3000 h (folds 0:2, 1:2, 2:1, 3:1, 4:2). Cell numbers differ, so these are different cells of one module, at most the same cell at another stress stage for A11 (not checked). The audit treated SDLE as one undecidable image id per cell and the frozen rule has no SDLE link, so cv5v3 keeps SDLE as cv5v2 did. If the lead adds these as links (information I4): 47 moves, SDLE held out 7 / 0 / 2 / 0 / 8, fold sizes 107 / 120 / 101 / 95 / 109. S: same kind of defect as the CFVS / ARTS links; 17 cells, about 3% of the pool.
2. **BMRK** (50 pool cells): no module id; if ELPV's numbering follows modules, neighbouring numbers share a module (not on disk; not checked).
3. **CFVS** twins without overlapping labelled crops are invisible to the audit; 6 cells.tsv-only links are kept without pixel support; more may exist.
4. Rule B is post hoc (audit 3c); for pool cells it equals the pre-set rule (E here: adding the pre-set column changes no group).
5. Sister cells and look-alikes: links below 320 inliers between multi cells rest on the serial calibration and the eye (audit 9.5); unlinked look-alike pairs stay across folds as in cv5v2 (section 5).
6. C4: see section 7.

## 7. For the lead: the C4 conflict (decision needed before review)
The frozen rule (R1 keep, R2 majority, R3 balance cost then lower fold) gives fold sizes 104 / 124 / 102 / 98 / 104. The lead's check "must not get worse" fails on cells, ARTS, CFVS and multi spreads, and E shows that every split keeping R1 + R2 fails on cells and CFVS. Options (S):
- (a) **Accept cv5v3 as built** and narrow the check to what scoring depends on: crack-cell spread (9 -> 5), inactive-cell spread (8 -> 7), class coverage (same 3 cases), no missing source or type in training (none). Fold 1 trains on 408 cells (cv5v2 421), fold 3 on 434. All arms share the split, so contrasts are unaffected; per-fold levels are not comparable across folds anyway. Nothing to rebuild; the check file would be re-rendered with the narrowed verdict (json, groups, roots, set pins unchanged).
- (b) Variant I3 (equal cost -> fewer cells): 104 / 114 / 104 / 104 / 106; still fails "not worse" on cells and CFVS. Changes 10 cells' folds against (a); script option, json, roots, pins all rebuilt (about 10 min CPU).
- (c) Allow extra moves of whole clean groups out of fold 1 (breaks R1 and the "minimal moves" idea; shrinks the unmoved set used in section 8).
- Separately: SDLE links yes / no (section 6.1). If yes, rerun with the links added; (a) / (b) / (c) still apply.
My reading (S): (a). The imbalance is 26 cells of 532 and touches no balance that the metrics use.

## 8. Plan for the baseline on cv5v3 (not executed)
Arms: PF v1.1 (`bench/methods/house_r34_unetpp_pf_v11.yaml`) and HOUSE v1.1 (`house_r34_unetpp_v11.yaml`), 5 seeds x 5 folds each = 50 training runs + 50 held-out dumps. Seeds 5 to 9, the seeds of the existing cv5v2 runs.

**Code to deploy.** Training needs no code change (train.py reads only the root). The dump needs `bench/sets.py` with the cv5v3 pins (bench_cv5v3, or a merge of it). Read tools (fix round 1, bench_cv5v3 760ef24): `bench/w1read.py` accepts cv5v2_f or cv5v3_f sets, one split per read; `w1read.check_groups` (run by `assemble`, so by every read tool: bench_read_w1, bench_aa, ensread, classbias, classbias_read, src_calib, atlas) refuses cv5v3 runs unless the groups passed partition the stems as `bench_data_v3/meta/cv5v3_groups.tsv` does, so a cv5v3 read must pass `--groups /home/noob/work/bench_data_v3/meta/cv5v3_groups.tsv`; label-set mode `manifest` already maps cv5v3_v11_f<k> roots to v11 (test added). `bench/q/cv02/cq.sh` is not on bench_cv5v3 (it came with bench_rows2, merged into ae4dd10): patch written, not applied, `/home/noob/work/bench_reads/stageC/cv5v3/fix1/cq_cv5v3.patch` (DATA_V3, BENCH_CV5V3_ROOTS, ROOTS_cv5v3_v11.md5 check when a job uses a cv5v3 root, set token cv5v3_f<k> taken from the root); it applies at the deploy merge of bench_cv5v3 with ae4dd10, the lead's call. If the lead's ruling rebuilds the meta folder somewhere else, `BENCH_META_V3` and `BENCH_CV5V3_ROOTS` point there.

**gaint.** Data: `/home/noob/work/bench_data_v3` (built). Queue dir e.g. `/home/noob/work/bq/c3base`, armed by bench_setup.sh pinned to the deploy commit, as W1-G. Job lines, train (as bq/w1g/jobs.txt):
`c3_pf_v11_f0_s5|bench/methods/house_r34_unetpp_pf_v11.yaml|5|/home/noob/work/bench_data_v3/roots/cv5v3_v11_f0|9000||`
dump (as bq/w1g/dump/jobs.txt, set token `cv5v3_f<k>`):
`dump_c3_pf_v11_f0_s5|-|5|/home/noob/work/bench_data_v3/roots/cv5v3_v11_f0|6200|<python> -u scripts/bench_infer.py --run <repo>/experiments/c3_pf_v11_f0_s5 --set cv5v3_f0 --dumps /home/noob/work/bench_dumps/c3base --method house_r34_unetpp_pf_v11 --card bench/methods/house_r34_unetpp_pf_v11.yaml --run-id c3_pf_v11_f0_s5 --device cuda --precision fp32 --threads 4 --workers 4 --batch 8 --logp --bench-run dump_c3_pf_v11_f0_s5|`

**cv02.** New code archive `/tmp/noob_el/bench_<sha>` with CODE.md5 (as W1-C); copy `bench_data_v3/meta` and rebuild the roots on cv02 with the deployed `scripts/bench_make_roots.py` into `/tmp/noob_el/bench_data_v3/roots` (labeled `/tmp/noob_el/bench_data/labeled`, masks `/tmp/noob_el/bench_data/masks_v11/{masks,masks_strict}`, both already there); compare `ROOTS_cv5v3_v11.md5` with gaint's except MASKLINKS lines. **`bench/q/cv02/cq.sh` hardcodes `--set cv5v2_f$fold` and exports only `BENCH_CV5V2_ROOTS`**: it needs the set token from the job (or the root name) and `BENCH_CV5V3_ROOTS=$DATA_V3/roots`. Job line (as w1c): `c3_pf_v11_f0_s5|bench/methods/house_r34_unetpp_pf_v11.yaml|5|/tmp/noob_el/bench_data_v3/roots/cv5v3_v11_f0|<gpu>|9000|6200|1|`. /tmp is wiped on reboot. Relay dumps to gaint as for W1-C.

**GPU-hours** (20,000 steps per run): gaint about 1 h per run (task figure); cv02 0.18 s per step when its GPUs are free = 1.0 h per run; dump and slim about 2 min. 50 runs = **about 50 GPU-h training + about 2 h dumps**, matching the lead's 50 GPU-h. Wall time: cv02 with 8 free GPUs, one run per GPU, about 7 h; with 2 lanes per GPU the step time rises (W1-C measured 3.5 to 4 h per run with shared GPUs). gaint alone: about 52 h on its one shared GPU. Suggested split (S): all 50 on one machine so every arm and seed is paired; cv02 is the faster choice when free, and the cv5v2 references with the most seeds are there (PF s5 to s9, w1c1; HOUSE only s5, s6, w1c2; gaint PF s5 to s8). For a 5-seed HOUSE leakage comparison either add HOUSE cv5v2 s7 to s9 on cv02 (15 runs, about 15 GPU-h) or compare HOUSE on s5, s6 only.

**Cells for the cv5v2 against cv5v3 comparison** (E: results/stageC/cv5v3/cv5v3_compare_cells.tsv; every cell is held out exactly once in each split):
| set | cells | crack cells | inactive cells | what changes between the two splits for these cells |
|---|---|---|---|---|
| clean_unmoved | 433 (all clean cells keep their fold) | 192 | 40 | only the 35 moved cells in their training set; no module-mate across folds in either split, except the 17 SDLE cells (modules A1, A10, A11 span folds in both splits, section 6.1; corrected 16 Nov, review F4) |
| affected_unmoved | 64 (ARTS 32, CFVS 25, CSIR 7) | 23 | 6 | same fold; their module-mates leave the training set (moved into this fold) |
| affected_moved | 35 (ARTS 19, CFVS 12, CSIR 4) | 14 | 2 | fold changes; module-mates leave training |
- Leakage estimate (S, to be pre-registered with the runs): per seed, (score on cv5v3 minus score on cv5v2) on affected_unmoved, minus the same difference on clean_unmoved (the control for the changed training sets), group bootstrap over cv5v3 groups. affected_moved adds 35 cells with a fold change as a second stratum. By the audit's closest relation (cv5v2): affected_unmoved = 2 same cell, 20 neighbouring crop, 38 same module only, 4 open pair; affected_moved = 2, 18, 11, 4.
- Power (S): 23 crack cells in affected_unmoved; the audit's upper bound for the whole effect is about +0.07 crack IoU on affected cells, so a 5-seed difference-in-differences should see an effect of that size and cannot see one of 0.01.

## 9. Record
- Code: /home/noob/work/bench_wt_cv5v3, branch bench_cv5v3 from f966127: 3103270 (bench/cv5v3.py, scripts/bench_make_cv5v3.py, tests/test_bench_cv5v3.py, 11 tests), ccfd538 (cv5v3 pins in scripts/bench_make_roots.py, sets cv5v3_f0..f4 in bench/sets.py, scripts/bench_check_cv5v3_roots.py, tests/test_bench_sets_cv5v3.py), 5591820 (comparison-cell table, --tables-only). Existing names and pins in bench/sets.py and the root builder unchanged (tested). Full pytest 658 passed, 4 skipped. No push. Git-ignored data links data/labeled, data/unlabeled, data/escdd_masks as in bench_wt_split.
- Files: benchmark/splits/cv5v3.json, cv5v3_groups.tsv, cv5v3_check.txt, cv5v3.md5 (new); results/stageC/cv5v3/{cv5v3_balance.md, cv5v3_moves.tsv, cv5v3_vs_proposal.tsv, cv5v3_class_cells.tsv, cv5v3_compare_cells.tsv}; /home/noob/work/bench_data_v3/{meta (read-only copies + META.md5), roots/cv5v3_v11_f0..f4, roots/ROOTS_cv5v3_v11.md5, roots/build_v11.log}; logs /home/noob/work/bench_reads/stageC/cv5v3/.
- Inputs unchanged: all 20 earlier files of benchmark/splits (md5 snapshot before run 1, md5sum -c after); bench_data, bench_udev and every other worktree, queue and session untouched. tmux bench_v3_pytest (pane 285214) ended by itself. CPU only, nice 19, one worker.
- Sealed sets: no label, mask, prediction or label summary of a sealed cell used; cells.tsv only through load_cells_safe; masks of the 532 pool cells only. Disclosed in BUILD_LOG: masks_v11/SUMMARY.txt and a MANIFEST.tsv filter printed on screen show ignore-px counts / mask hashes of 2 legacy-test cells; used and written nowhere. No sealed stem in any file written.

## 10. Reviewer commands (gaint, as noob; all CPU; fix round 1 commands in section 11)
```
P=/home/noob/work/el-fault-detection/.venv/bin/python; W=/home/noob/work/bench_wt_cv5v3; S=/home/yugma/mtp/research/team_2026-11-12_frontier/benchmark/splits
git -C $W log --oneline f966127..HEAD; git -C $W status --short --untracked-files=no | wc -l      # 3 commits; 0
cd $W && CUDA_VISIBLE_DEVICES= $P -m pytest -q -p no:cacheprovider tests/test_bench_cv5v3.py tests/test_bench_sets_cv5v3.py tests/test_bench_sets_cv5v2.py   # 25 passed
cd $W && CUDA_VISIBLE_DEVICES= nice -n 19 $P scripts/bench_make_cv5v3.py --check      # CHECK OK: 9 of 9 files byte-identical / SOME CHECK FAILED (C4)
cd $S && md5sum -c cv5v3.md5 && md5sum -c SPLITS.md5 && md5sum -c SPLIT_INTEGRITY.MD5.txt   # all OK (earlier files unchanged)
grep -E "^\[C[0-9]\]" $S/cv5v3_check.txt | cut -c1-120                                          # 4 FAIL lines, all C4
cd $W && CUDA_VISIBLE_DEVICES= nice -n 19 $P scripts/bench_make_roots.py --split /home/noob/work/bench_data_v3/meta/cv5v3.json --groups /home/noob/work/bench_data_v3/meta/cv5v3_groups.tsv --forbidden /home/noob/work/bench_data_v3/meta/forbidden_v1.txt --legacy-splits data/splits --labeled /home/noob/work/el-fault-detection/data/labeled --out /home/noob/work/bench_data_v3/roots --tag v11 --train-masks /home/noob/work/bench_data/masks_v11/masks --heldout-masks /home/noob/work/bench_data/masks_v11/masks_strict --link-dir masks_v11 --check   # CHECK OK ROOTS_cv5v3_v11.md5 9c148c7e...
cd $W && CUDA_VISIBLE_DEVICES= nice -n 19 $P scripts/bench_check_cv5v3_roots.py | tail -1    # ALL PASS
cd /home/noob/work/bench_data_v3/meta && md5sum -c META.md5
```
An independent recompute of the groups (own union-find over cv5v2 groups, module_identity_v3 by image id, the 4 pairs, cells.tsv module_group) and of R2 / R3 from cv5v3_groups.tsv is the strongest check; the builder's functions are in bench/cv5v3.py.

## 11. Fix round 1 (16 Nov; dated amendment; section 1 unchanged)
Review: harness/REVIEW_CV5V3.md, FAIL on item 4 (C4) only. The reviewer recomputed the split cell for cell and found no builder error; F1 (rule on C4) and F2 (SDLE links yes / no) are for the lead, F3 deploy items for the builder before the first cv5v3 run, F4 wording. log.md holds no ruling on F1 / F2 at the time of this round. S: choosing between them is the lead's call, so this round does not change the published split; it makes each ruling a one-command rebuild and shows what each gives.

### 11a. Done
- Builder options (bench_cv5v3 760ef24, 7aaf0a4; tests/test_bench_cv5v3_read.py): `--tie-break fewer` (R3: equal cost -> fewer cells after the placement, then lowest fold; the review's I3), `--sdle-links` (L6: SDLE pool cells whose stem names the same module are one group), `--c4-scope scoring` (C4 pass condition only on the crack-cell and inactive-cell spreads, not worse by more than 2, and on C4c; every other spread printed as `[C4-info]`; C5 unchanged), `--out DIR`. Defaults are the frozen rule: `--check` still gives 9 of 9 files byte-identical to the published ones. A non-default option is printed as a VARIANT line in the check file and the balance table; L6 and R3 are also written into cv5v3.json (`groups.amendments`); the C4 scope is not (it changes no list).
- F3, in-branch part (760ef24): read tools accept cv5v3 runs; `w1read.check_groups` in `assemble` refuses a cv5v3 read whose groups are not the cv5v3 partition (the cv5v2 groups are finer and would understate the variance); test that the real cv5v3_groups.tsv passes and cv5v2_groups.tsv is refused. cq.sh: patch only (section 8).
- Full pytest on bench_cv5v3 at 7aaf0a4 (tmux bench_v3_fix1pytest2, pane 473481, ended by itself): 665 passed, 4 skipped, rc 0 (/home/noob/work/bench_reads/stageC/cv5v3/fix1/pytest_full.log; 658 before + the 7 tests of tests/test_bench_cv5v3_read.py).
- F4: section 8 table corrected (17 SDLE cells in clean_unmoved have module-mates across folds in both splits). Settled by L6 if the lead says yes: then clean_unmoved = 416 cells (190 crack, 40 inactive) with no SDLE cell.
- Correction (E): the clamp cell is ARTS_00008_r4_c1, not CSIR_00107_r9_c3 (section 4). The review's sentence "unavoidable wherever that module sits" does not hold: the clamp case follows the tie of ARTS_00008.

### 11b. Candidates for the lead (E: /home/noob/work/bench_reads/stageC/cv5v3/candidates/<name>/{splits,tables}, CANDIDATES.md5; each built twice, `--check` 9 of 9 byte-identical)
Held-out cells per fold; spreads (max - min over folds); cv5v2 for reference.
| candidate (options) | held-out sizes | cells | crack | inactive | ARTS | CFVS | CSIR | SDLE | multi | no_spacing | moves | clamp case | C4 as written | C4 narrowed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| cv5v2 | 107 / 111 / 104 / 104 / 106 | 7 | 9 | 8 | 5 | 5 | 1 | 1 | 17 | 2 | - | f3 | - | - |
| a frozen rule (`--c4-scope scoring`) = published split | 104 / 124 / 102 / 98 / 104 | 26 | 5 | 7 | 15 | 10 | 2 | 1 | 20 | 2 | 35 | f1 | FAIL | PASS |
| b I3 (`--tie-break fewer --c4-scope scoring`) | 104 / 114 / 104 / 104 / 106 | 10 | 5 | 7 | 3 | 8 | 2 | 1 | 17 | 2 | 35 | f3 | FAIL | PASS |
| c L6 + frozen tie (`--sdle-links --c4-scope scoring`) | 107 / 120 / 101 / 95 / 109 | 25 | 4 | 7 | 15 | 10 | 2 | 8 | 20 | 7 | 47 | f1 | FAIL | PASS |
| d L6 + I3 (`--sdle-links --tie-break fewer --c4-scope scoring`) | 107 / 110 / 103 / 101 / 111 | 10 | 4 | 7 | 3 | 8 | 2 | 8 | 17 | 7 | 47 | f3 | FAIL | PASS |
- Every candidate passes C1 (also the SDLE module under L6), C2, C3, C5 and C6. No candidate passes C4 as written; the review showed that none of the 512 tie placements under R1 + R2 can (E, RV/rv_ties.out).
- b against the published split: 10 cells change fold (ARTS_00008 group 6 cells f1 -> f3; ARTS_00118 group 2 cells f1 -> f2; CFVS_00156 group 2 cells f1 -> f4); the 35 moved stems differ, the count does not. Same crack and inactive spreads.
- d adds the 3 SDLE modules: A1 (7 cells) to f0, A10 (2) to f2, A11 (8) to f4, all by R3 (A11 by cost, f4 54 against 70; A1, A10 equal cost, fewer cells); 12 SDLE cells move. SDLE held out 7 / 0 / 2 / 0 / 8; every fold's training list keeps SDLE cells (C4c pass), folds 1 and 3 score no SDLE cell. no_spacing spread 2 -> 7 follows (SDLE cells are no_spacing).
- Smallest training list: a 408, b 418, c 412, d 421 cells (cv5v2 421).
- My reading (S; replaces the "(a)" of section 7): **d**, i.e. F2 yes and F1 (b) with the narrowed C4. L6 is the kind of link rule 1 closes for the other sources, and I3 removes most of the size imbalance at the same crack and inactive balance. The reviewer chose the same (F1 (b), F2 yes).

### 11c. Rebuild after the ruling (about 10 min CPU, then a delta review)
1. The lead writes the ruling (options) into log.md. Builder: `scripts/bench_make_cv5v3.py <options> --out <staging> --tables <staging_tables>` and cmp against the candidate of section 11b (must be byte-identical).
2. (a) only: cv5v3.json, cv5v3_groups.tsv, roots and set pins stay; cv5v3_check.txt and cv5v3.md5 are replaced in benchmark/splits and in bench_data_v3/meta (META.md5 renewed). Needs the lead's yes to replace those two published files (the builder refuses to overwrite).
3. b, c or d: new cv5v3.json and cv5v3_groups.tsv. Re-pin `PINNED` in scripts/bench_make_roots.py and `CV_LIST_MD5` / `SIZES` of cv5v3 in bench/sets.py (tests updated, full pytest); meta and roots built into a fresh folder (suggested `/home/noob/work/bench_data_v3b`, with `BENCH_META_V3` / `BENCH_CV5V3_ROOTS` pointed there), or into bench_data_v3 after the lead approves removing the current one; the root checks of section 5 rerun; benchmark/splits files replaced only with the lead's yes (or published under a new name, e.g. cv5v3b, if the lead prefers to keep the reviewed files). Then the delta review the reviewer listed (rv_split.py, rv_roots.py, the set / builder tests).
4. The baseline plan of section 8 is unchanged except the comparison sets (d: clean_unmoved 416, affected_unmoved 69, affected_moved 47; crack cells 190 / 23 / 16; inactive 40 / 6 / 2).

### 11d. Not done (and why)
- No split file, root, pin or set registration changed: each depends on F1 / F2.
- cq.sh not changed on any branch: it is not on bench_cv5v3, and the deploy merge base is the lead's call.
- ready = false: C4 as written still fails for every reachable split; the split passes only under a narrowed C4 that the lead has not ruled.

### 11e. Reviewer commands for this round
```
P=/home/noob/work/el-fault-detection/.venv/bin/python; W=/home/noob/work/bench_wt_cv5v3; C=/home/noob/work/bench_reads/stageC/cv5v3/candidates
git -C $W log --oneline 5591820..HEAD; git -C $W diff --stat 5591820..HEAD                      # 760ef24, 7aaf0a4; 4 files
cd $W && CUDA_VISIBLE_DEVICES= nice -n 19 $P scripts/bench_make_cv5v3.py --check                  # CHECK OK: 9 of 9 (published files unchanged)
cd $W && CUDA_VISIBLE_DEVICES= nice -n 19 $P -m pytest -q -p no:cacheprovider tests/test_bench_cv5v3_read.py tests/test_bench_cv5v3.py tests/test_bench_sets_cv5v3.py   # all pass
cd $C && md5sum -c --quiet CANDIDATES.md5 && echo candidates OK
for n in "a_frozen_narrow --c4-scope scoring" "b_fewer_narrow --tie-break fewer --c4-scope scoring" "c_sdle_frozen_narrow --sdle-links --c4-scope scoring" "d_sdle_fewer_narrow --sdle-links --tie-break fewer --c4-scope scoring"; do set -- $n; d=$1; shift; (cd $W && CUDA_VISIBLE_DEVICES= nice -n 19 $P scripts/bench_make_cv5v3.py --out $C/$d/splits --tables $C/$d/tables "$@" --check | head -1); done   # 4 x CHECK OK
cmp $C/a_frozen_narrow/splits/cv5v3.json /home/yugma/mtp/research/team_2026-11-12_frontier/benchmark/splits/cv5v3.json && echo a keeps the json
grep -c "ARTS_00008_r4_c1" $C/b_fewer_narrow/splits/cv5v3_groups.tsv                              # 1 (clamp cell; fold column 3)
cd /home/noob/work/bench_reads/stageC/cv5v3/fix1 && bash -n cq_b/cq.sh && cat cq_cv5v3.patch | head -60
```

## 12. Fix round 2 (16 Nov; dated amendment; section 1 unchanged)
Review: harness/REVIEW_CV5V3.md round 2, FAIL on item 4 only, for the same reason as round 1 (rule 3 as written cannot hold under R1 + R2). No builder error found. Builder items: F5 and F6. F1 and F2 are the lead's; F3 (cq.sh) waits for the deploy merge. log.md holds no ruling on F1 / F2 at the time of this round, so the published split, the candidates, the roots and the pins stay as reviewed.

### 12a. F5: the count reading of R3 (clarification, applies to the published split and to every candidate)
Section 1b says the tied groups are placed "one at a time in ascending group name, each seeing the counts left by the groups placed before it". Stated exactly: **while a tied group is costed, every pool cell counts in one fold: cells of R1 groups in their fold, cells of R2 groups in their majority fold, cells of tied groups already placed in their kept fold, and cells of tied groups not yet placed in their cv5v2 fold.** This is what the build has always done (bench/cv5v3.py assign_folds starts from `new = dict(fold_v2)`) and what the reviewer recomputed as the main reading. It holds under both tie-breaks (frozen and I3) and with or without L6.
- E (reviewer, RV/r2/rv2_candidates.out): the other reading (unplaced ties left out of the counts) gives the same folds for the published split and for candidates a, b and d; **candidate c changes 4 cells** (ARTS_00165 / ARTS_00166 r12_c5 to f1, CSIR_00178_r7_c1 / CSIR_00207_r7_c5 to f0). So if the lead picks c, this sentence is part of its rule.
- Where it is written now: this section; the module docstring and the assign_folds docstring of bench/cv5v3.py; the `--tie-break` help of scripts/bench_make_cv5v3.py. The split files are not changed: the JSON `groups.amendments` and the check file are output bytes of the reviewed split and candidates, and the reading changes no fold of the published split.
- Test: tests/test_bench_cv5v3.py `test_unplaced_tied_groups_count_in_their_cv5v2_folds` (a toy where the two readings give f0 against f1; both tie-breaks give f0, the stated reading).

### 12b. F6: docstring
bench/cv5v3.py assign_folds no longer says "tie_size=True is NOT the rule: a variant for information only". It now says: tie_size=False is the frozen rule of section 1; tie_size=True is amendment I3 (`--tie-break fewer`, candidates b and d of section 11b) and becomes the rule only if the lead rules F1 (b). This wording is right under either ruling; if the lead picks b or d, the rebuild commit names the ruling's log.md entry in the same place.

### 12c. Checks after this round
E (/home/noob/work/bench_reads/stageC/cv5v3/fix2/run_checks.out; script run_checks.sh beside it; tmux bench_v3_fix2check, pane 551495, 00:31:51 to 00:34:41, ended by itself; CPU, nice 19):
- Commit bench_cv5v3 616da42 (3 files: bench/cv5v3.py docstrings, one help line in scripts/bench_make_cv5v3.py, one test). No code path changed.
- cv5v3 tests (test_bench_cv5v3.py, _read.py, test_bench_sets_cv5v3.py): 27 passed. Full pytest: **666 passed, 4 skipped, rc 0** (665 before + the new test; fix2/pytest_full.log).
- Published split: `--check` CHECK OK, 9 of 9 files byte-identical (rc 1 from C4 as written, as before). cv5v3.md5, SPLITS.md5, SPLIT_INTEGRITY.MD5.txt check OK.
- Candidates a to d: each `--check` against its folder 9 of 9 byte-identical, rc 0 (narrowed C4); CANDIDATES.md5 OK before and after.
- Roots: bench_data_v3 has 0 files newer than the root build (last file 15 Nov 23:52); meta/META.md5 OK.
- Other worktrees at the same HEADs as the review, 0 tracked changes (el_bench and bench_wt_w2 hold only untracked run folders of their queues).

### 12d. Still open (unchanged from 11c and 11d)
- F1 (lead): narrow rule 3 (`--c4-scope scoring`) with the frozen tie-break (a) or with I3 (b). F2 (lead): SDLE links (L6) yes or no. Builder's and reviewer's reading (S): d.
- After the ruling: the rebuild of section 11c (cmp against the reviewed candidate; new pins and roots in a fresh folder for b, c or d; full pytest), then the reviewer's delta review.
- ready = false: rule 3 as written still fails for every reachable split.

### 12e. Reviewer commands for this round
```
P=/home/noob/work/el-fault-detection/.venv/bin/python; W=/home/noob/work/bench_wt_cv5v3; C=/home/noob/work/bench_reads/stageC/cv5v3/candidates
git -C $W log --oneline 7aaf0a4..HEAD; git -C $W diff 7aaf0a4..HEAD                       # docstrings, one help line, one test
cd $W && CUDA_VISIBLE_DEVICES= nice -n 19 $P -m pytest -q -p no:cacheprovider tests/test_bench_cv5v3.py -k unplaced
cd $W && CUDA_VISIBLE_DEVICES= nice -n 19 $P scripts/bench_make_cv5v3.py --check | head -1      # CHECK OK: 9 of 9
cd $C && md5sum -c --quiet CANDIDATES.md5 && echo candidates OK
cat /home/noob/work/bench_reads/stageC/cv5v3/fix2/run_checks.out
```

## 13. After the lead's ruling (16 Nov; dated amendment; section 1 unchanged)
Ruling: log.md 16 Nov 00:39 "RULING on the corrected split cv5v3": **cv5v3 = candidate d, options `--sdle-links --tie-break fewer --c4-scope scoring`** (F1 option (b): rule 3 narrowed to crack cells, inactive cells, classes without training px and no source or cell type missing from training; ties to the fold with fewer cells; F2 yes: SDLE module links L6; F5 reading as coded). Published candidate a files may be replaced (copies kept); meta and roots into the fresh folder /home/noob/work/bench_data_v3b; bench_data_v3 may be removed only after the delta review passes (not done here). Logs and snapshots: /home/noob/work/bench_reads/stageC/cv5v3/ruling/.

### 13a. Applied (E)
1. **Rebuild into staging** (`scripts/bench_make_cv5v3.py --sdle-links --tie-break fewer --c4-scope scoring --out ruling/staging/splits --tables ruling/staging/tables`, rc 0, ALL CHECKS PASS): all 9 files cmp-identical to the reviewed candidate d (ruling/staging_cmp.txt); CANDIDATES.md5 OK.
2. **Copies of candidate a** (published 15 Nov): results/stageC/cv5v3/replaced_a/splits/{cv5v3.json f116d37d, cv5v3_groups.tsv d8679d4b, cv5v3_check.txt 34f6ac6d, cv5v3.md5 de1d061e} and replaced_a/tables/ (the 5 tables of a), md5s in replaced_a/REPLACED_A.md5. The frozen rule (defaults) still rebuilds them: `--out replaced_a/splits --tables replaced_a/tables --check` gives 9 of 9 byte-identical (rc 1 from C4 as written).
3. **Replaced in benchmark/splits** (candidate d): cv5v3.json **7a700b00**32a6305ab2c2c570453283af, cv5v3_groups.tsv **d880a769**e3672b7dbc3614a33738a326, cv5v3_check.txt **2afc4cc6**41c7d81f61000408a1253188, cv5v3.md5 **400c1353**21766c1bfff8c5544cf98d1e. The tables in results/stageC/cv5v3 replaced the same way: cv5v3_balance.md cb1d82b7, cv5v3_moves.tsv b77a6370, cv5v3_vs_proposal.tsv 52b4608b, cv5v3_class_cells.tsv 1ef0d183, cv5v3_compare_cells.tsv 4d381878. md5 of all 25 files of benchmark/splits before and after: only these 4 lines differ (ruling/splits_md5_before.txt, splits_md5_after_replace.txt); cv5v3.md5, SPLITS.md5, SPLIT_INTEGRITY.MD5.txt check OK. cv5v3_proposal.tsv, cv5v2 files and score_exclude lists unchanged. `--sdle-links --tie-break fewer --c4-scope scoring --check`: 9 of 9 byte-identical, ALL CHECKS PASS, rc 0.
4. **Code** (bench_cv5v3, 2 commits, no push): 6a3876a: F5 / F6 wording now names the ruling (bench/cv5v3.py module docstring: the published cv5v3 = rule of s1 + L6 + I3, F5 reading holds; assign_folds docstring: "The lead ruled F1 (b) on 16 Nov 00:39: I3 is the rule of the published cv5v3"; sdle_module docstring: L6 is a link of the published cv5v3; script docstring and `--tie-break` / `--sdle-links` / `--c4-scope` help name the ruling; constant `RULED`); the disk test builds with `RULED`, checks sizes 107 / 110 / 103 / 101 / 111 and that the json / groups md5 equal the root-builder pins. Defaults stay the frozen rule (test unchanged). No output byte changed (step 3 check after the commit). c417732: re-pins.
5. **Re-pins** (c417732): scripts/bench_make_roots.py `PINNED` cv5v3.json 7a700b00..., cv5v3_groups.tsv d880a769... (a's pins retired). bench/sets.py `CV_LIST_MD5["cv5v3"]` = 79816ba63cca96e10265197eb4cfa905, 548af76f51f938d5a73c2da580085483, ec7df8fded6159f9b1fac7481bce7402, b61a2d6f14f2a84993b83a00dabae7bf, 2f7c5a7ccc19b292629d3b00a7f62214; `SIZES` cv5v3_f0..f4 = 107 / 110 / 103 / 101 / 111. Defaults `BENCH_CV5V3_ROOTS` = /home/noob/work/bench_data_v3b/roots (bench/sets.py), `BENCH_META_V3` = /home/noob/work/bench_data_v3b/meta (bench/cellmeta.py), so `w1read.check_groups` now compares with the 285-group partition of d (docstring 299 -> 285). scripts/bench_check_cv5v3_roots.py: default `--data /home/noob/work/bench_data_v3b`, one new check per fold "SDLE module named in the stem (L6) shared by train and held-out: 0" (own regex), and the DATA_MANIFEST info line no longer claims that no ignore-px cell moved. Tests: test_bench_sets_cv5v3.py sizes, new test that the two folder defaults are bench_data_v3b; test_bench_cv5v3_read.py paths.
6. **Meta** /home/noob/work/bench_data_v3b/meta: cv5v3.json, cv5v3_groups.tsv, cv5v3_check.txt, forbidden_v1.txt (copies of benchmark/splits, read-only), META.md5 (md5 ade72e13), `md5sum -c` OK.
7. **Roots** /home/noob/work/bench_data_v3b/roots/cv5v3_v11_f0..f4 by scripts/bench_make_roots.py at c417732 (masks_v11 links: train -> bench_data/masks_v11/masks, held-out -> masks_strict; labeled -> house dir). Every builder assert OK: "0 forbidden of 167; 0 of 285 groups split; held-outs partition 532; lists = cv5v3.json". **ROOTS_cv5v3_v11.md5 79e8aee81f4aeeb4bd45034360dad1c5**; `--check`: CHECK OK, same md5; `md5sum -c` OK. build_v11.log beside the roots (= ruling/make_roots.out).

| root | train | held-out | groups | SPLITS.md5 | train.txt | test.txt (= val.txt) | DATA_MANIFEST.md5 |
|---|---|---|---|---|---|---|---|
| cv5v3_v11_f0 | 425 | 107 | 56 | 9553a80b | d7069b34 | 79816ba6 | df7f4924 |
| cv5v3_v11_f1 | 422 | 110 | 59 | 50df3e60 | af008fb0 | 548af76f | d9986a61 |
| cv5v3_v11_f2 | 429 | 103 | 55 | 5496f149 | aed692ad | ec7df8fd | 33e65b3f |
| cv5v3_v11_f3 | 431 | 101 | 55 | 21005e17 | b778eaba | b61a2d6f | bc882df0 |
| cv5v3_v11_f4 | 421 | 111 | 60 | 95441468 | a0211569 | 2f7c5a7c | 908e9704 |

8. **Root checks** (scripts/bench_check_cv5v3_roots.py, ruling/check_roots.out, rc 0): **ALL PASS, 101 PASS, 0 FAIL** (96 as in s5 + the 5 new SDLE-module lines). Lists = groups file = JSON, test == val, 0 duplicate / forbidden / sealed / do-not-train, 0 shared cv5v3 group / cv5v2 group / module_group / image id / rule-B module / open pair / SDLE stem module, 532 mask links per root (0 wrong, 0 dangling), labeled link, wave 1 layout and MASKLINKS header, SPLITS / DATA_MANIFEST / ROOTS / META md5sum -c OK, held md5 = JSON = sets.py pin, held-outs partition the pool, 0 md5-identical or known same-cell pair across. Near-duplicates at NCC >= 0.85 across train and held-out, summed over folds: **1,130** (cv5v2 1,160; a 1,152). 12 pairs cross in d and not in cv5v2: 4 ARTS r1_c6 corner crops with the printed serial band (the 3 pairs among ARTS_00026 / 00102 / 00114 named in s5, plus ARTS_00021 / ARTS_00118, whose groups ARTS_00008 and ARTS_00118 now sit in f3 and f2; NCC 0.943 to 0.953), and 8 SDLE pairs between different stem modules (A1 / A10 / A11, NCC 0.857 to 0.927), split apart because L6 sends each module to one fold (S: smooth SDLE look-alikes of the kind cv5v2 left ungrouped; their stems name different modules). 25 pairs crossing in cv5v2 no longer cross. DATA_MANIFEST.md5 of each root equals cv5v2's of the same fold (info).
9. **Tests**: cv5v3 + cv5v2 set tests 34 passed, 0 skipped (roots present). **Full pytest at c417732: 667 passed, 4 skipped, rc 0** (ruling/pytest_full.log; 666 + the new folder-default test).
10. **cq.sh** (F3, deploy, still the lead's merge): ruling/cq_cv5v3b.patch (md5 330ac850) = fix1/cq_cv5v3.patch with the one default changed, `DATA_V3=${DATA_V3:-/tmp/noob_el/bench_data_v3b}`; `patch --dry-run` on the fix1/cq_a copy OK. Not applied anywhere.
11. Not done, by the ruling: /home/noob/work/bench_data_v3 (candidate a roots) not removed; 0 files changed there. It goes once the delta review of bench_data_v3b passes.

### 13b. Candidate d in short (E: cv5v3_check.txt, cv5v3_balance.md)
- 285 groups; C1 to C5 PASS under the narrowed C4; C6 (--check) PASS. 47 cells move (ARTS 19, CFVS 12, SDLE 12, CSIR 4).
- Held-out 107 / 110 / 103 / 101 / 111 (cv5v2 107 / 111 / 104 / 104 / 106); training lists 425 / 422 / 429 / 431 / 421 (smallest 421 = cv5v2). Spreads cv5v2 -> d: crack cells 9 -> 4, inactive 8 -> 7 (pass); cells 7 -> 10, CFVS 5 -> 8, CSIR 1 -> 2, SDLE 1 -> 8, no_spacing 2 -> 7, ARTS 5 -> 3 (info, costs accepted by the ruling). SDLE held out 7 / 0 / 2 / 0 / 8.
- Classes with held-out px and 0 training px: belt_mark f0, rings f2, clamp f3: cv5v2's exact cases.
- Wording note (S): the information line I4 of cv5v3_check.txt still reads "Not a link of the rule ... If added as links" although L6 is used; it is output text of the reviewed candidate, so it stays (changing it breaks the byte cmp). The VARIANT lines, the JSON `groups.amendments` and the `[C1] PASS SDLE module named in the stem` line record that L6 is in.

### 13c. Comparison sets of candidate d (E: results/stageC/cv5v3/cv5v3_compare_cells.tsv)
| set | cells | crack cells | inactive cells | sources |
|---|---|---|---|---|
| clean_unmoved | **416** | 190 | 40 | no SDLE cell; = pool minus benchmark/splits/score_exclude_v3.txt (116 cells; E: sets equal) |
| affected_unmoved | **69** | 23 | 6 | ARTS 32, CFVS 25, CSIR 7, SDLE 5 |
| affected_moved | **47** | 16 | 2 | ARTS 19, CFVS 12, SDLE 12, CSIR 4 |
Relations (audit's closest, cv5v2): affected_unmoved 2 same cell, 20 neighbouring crop, 38 same module only, 4 open pair, 5 SDLE module; affected_moved 2, 18, 11, 4, 12. Leakage estimate and power as in s8 (difference-in-differences against clean_unmoved, group bootstrap over the 285 cv5v3 groups; 23 crack cells in affected_unmoved).

### 13d. Baseline plan of s8 with the new folder names (not executed; GPU-hours unchanged: about 50 GPU-h + 2 h dumps)
- **Code to deploy**: bench_cv5v3 at c417732 (or the deploy merge of it with ae4dd10, the lead's call); cq.sh with ruling/cq_cv5v3b.patch. Training needs no code change.
- **gaint**: data /home/noob/work/bench_data_v3b (built). Environment defaults already point there; set them explicitly in the queue anyway: `BENCH_CV5V3_ROOTS=/home/noob/work/bench_data_v3b/roots BENCH_META_V3=/home/noob/work/bench_data_v3b/meta`. Queue dir e.g. /home/noob/work/bq/c3base. Train job (as bq/w1g/jobs.txt):
  `c3_pf_v11_f0_s5|bench/methods/house_r34_unetpp_pf_v11.yaml|5|/home/noob/work/bench_data_v3b/roots/cv5v3_v11_f0|9000||`
  Dump job (set token `cv5v3_f<k>`):
  `dump_c3_pf_v11_f0_s5|-|5|/home/noob/work/bench_data_v3b/roots/cv5v3_v11_f0|6200|<python> -u scripts/bench_infer.py --run <repo>/experiments/c3_pf_v11_f0_s5 --set cv5v3_f0 --dumps /home/noob/work/bench_dumps/c3base --method house_r34_unetpp_pf_v11 --card bench/methods/house_r34_unetpp_pf_v11.yaml --run-id c3_pf_v11_f0_s5 --device cuda --precision fp32 --threads 4 --workers 4 --batch 8 --logp --bench-run dump_c3_pf_v11_f0_s5|`
- **Reads**: every cv5v3 read passes `--groups /home/noob/work/bench_data_v3b/meta/cv5v3_groups.tsv` (285 groups; w1read.check_groups refuses any other partition, including a's 299 groups).
- **cv02**: code archive /tmp/noob_el/bench_<sha> with CODE.md5; copy bench_data_v3b/meta to /tmp/noob_el/bench_data_v3b/meta, rebuild the roots there with the deployed scripts/bench_make_roots.py (`--out /tmp/noob_el/bench_data_v3b/roots`, labeled /tmp/noob_el/bench_data/labeled, masks /tmp/noob_el/bench_data/masks_v11/{masks,masks_strict}); compare ROOTS_cv5v3_v11.md5 with gaint's (79e8aee8) except the MASKLINKS lines; `DATA_V3=/tmp/noob_el/bench_data_v3b` (the patch default). Job line: `c3_pf_v11_f0_s5|bench/methods/house_r34_unetpp_pf_v11.yaml|5|/tmp/noob_el/bench_data_v3b/roots/cv5v3_v11_f0|<gpu>|9000|6200|1|`. /tmp is wiped on reboot.
- Arms, seeds (5 to 9), the HOUSE cv5v2 s7 to s9 option and the machine choice: as s8.

### 13e. Delta-review commands (gaint, as noob; CPU, nice 19)
```
P=/home/noob/work/el-fault-detection/.venv/bin/python; W=/home/noob/work/bench_wt_cv5v3; S=/home/yugma/mtp/research/team_2026-11-12_frontier/benchmark/splits
A=/home/yugma/mtp/research/team_2026-11-12_frontier/results/stageC/cv5v3/replaced_a; C=/home/noob/work/bench_reads/stageC/cv5v3/candidates/d_sdle_fewer_narrow
D=/home/noob/work/bench_data_v3b; R=/home/noob/work/bench_reads/stageC/cv5v3/ruling; export CUDA_VISIBLE_DEVICES=
git -C $W log --oneline 616da42..HEAD; git -C $W diff --stat 616da42..HEAD; git -C $W status --short --untracked-files=no | wc -l   # 6a3876a, c417732; 0
for f in cv5v3.json cv5v3_groups.tsv cv5v3_check.txt cv5v3.md5; do cmp $S/$f $C/splits/$f && echo "published = d: $f"; done
cd $S && md5sum -c cv5v3.md5 && md5sum -c --quiet SPLITS.md5 && md5sum -c --quiet SPLIT_INTEGRITY.MD5.txt && echo splits OK
md5sum $S/* | sed "s#$S/##" | diff $R/splits_md5_before.txt - ; echo "(only the 4 cv5v3 lines differ)"
cd $A && md5sum -c REPLACED_A.md5 && cmp splits/cv5v3.json /home/noob/work/bench_data_v3/meta/cv5v3.json && echo "copies of a OK"
cd $W && nice -n 19 $P scripts/bench_make_cv5v3.py --sdle-links --tie-break fewer --c4-scope scoring --check      # CHECK OK: 9 of 9; ALL CHECKS PASS; rc 0
cd $W && nice -n 19 $P scripts/bench_make_cv5v3.py --out $A/splits --tables $A/tables --check | head -1           # CHECK OK: 9 of 9 (frozen rule still rebuilds a)
cd $D/meta && md5sum -c META.md5 && for f in cv5v3.json cv5v3_groups.tsv cv5v3_check.txt forbidden_v1.txt; do cmp $f $S/$f; done && echo meta = splits
cd $W && nice -n 19 $P scripts/bench_make_roots.py --split $D/meta/cv5v3.json --groups $D/meta/cv5v3_groups.tsv --forbidden $D/meta/forbidden_v1.txt --legacy-splits data/splits --labeled /home/noob/work/el-fault-detection/data/labeled --out $D/roots --tag v11 --train-masks /home/noob/work/bench_data/masks_v11/masks --heldout-masks /home/noob/work/bench_data/masks_v11/masks_strict --link-dir masks_v11 --check | head -1   # CHECK OK ROOTS_cv5v3_v11.md5 79e8aee8...
cd $D/roots && md5sum -c --quiet ROOTS_cv5v3_v11.md5 && md5sum ROOTS_cv5v3_v11.md5                               # 79e8aee81f4aeeb4bd45034360dad1c5
cd $W && nice -n 19 $P scripts/bench_check_cv5v3_roots.py | tail -1                                               # ALL PASS
cd $W && nice -n 19 $P -m pytest -q -p no:cacheprovider tests/test_bench_cv5v3.py tests/test_bench_cv5v3_read.py tests/test_bench_sets_cv5v3.py tests/test_bench_sets_cv5v2.py   # 34 passed
cd $W && nice -n 19 $P -m pytest -q -p no:cacheprovider | tail -1                                                  # 667 passed, 4 skipped
find /home/noob/work/bench_data_v3 -newermt "2026-11-15 23:56" | wc -l                                              # 0 (a's roots untouched)
```
Reviewer's own checks on the new roots and JSON: rv_split.py / rv3_candidates.py on benchmark/splits (expected = candidate d), rv_roots.py with the data folder set to /home/noob/work/bench_data_v3b and the pins of c417732.
