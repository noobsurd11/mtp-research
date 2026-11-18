# Review of the corrected split cv5v3 (independent reviewer; round 3, after builder fix round 2; 16 Nov 2026)

Scope: the published cv5v3 split (benchmark/splits cv5v3.json f116d37d, cv5v3_groups.tsv d8679d4b, cv5v3_check.txt 34f6ac6d; roots /home/noob/work/bench_data_v3), the four candidates a to d (/home/noob/work/bench_reads/stageC/cv5v3/candidates, CANDIDATES.md5), and the fix-round-2 commit bench_cv5v3 616da42. Results file: results/stageC/CV5V3_BUILD.md (cccc6ec1), section 12. I built none of it. My checks use my own code; the only shared code is the reviewed cells loader `udev.load_cells_safe`, imported from bench_wt_split (f966127).
Check files: /home/noob/work/bench_reads/stageC/review_cv5v3/ (RV/; round 1), RV/r2/ (round 2), RV/r3/ (this round): run_r3.sh / run_r3.out (all commands of this round), rv3_candidates.py / .out (my items 1 to 4 for the published split and a to d), rv3_vs_rv2.diff (empty), rv3_balance.md, rv_roots_r3.out, rebuild/ (fresh builds of a to d), check_published.out, pytest_full.log, worktrees_r3.txt, splits_r3_before/after.md5, tables_r3_before/after.md5.
Tags: E = measured here, S = judgement. CPU only (CUDA_VISIBLE_DEVICES empty, nice 19, one process at a time; tmux bench_v3_rv3, pane pid 588009, 00:37:00 to 00:39:54, ended by itself). Nothing trained. No sealed label, mask, prediction or label summary read (masks opened only for the 532 pool stems, asserted before each open).

## Delta review after the ruling (16 Nov 2026, round 4; 00:57 to 01:02)

Scope: the lead's ruling of 16 Nov 00:39 (log.md, read word for word): cv5v3 = candidate d, `--sdle-links --tie-break fewer --c4-scope scoring`; a's published files replaced (copies in results/stageC/cv5v3/replaced_a/); meta and roots in /home/noob/work/bench_data_v3b. Builder's work: bench_cv5v3 6a3876a, c417732; CV5V3_BUILD.md s0 item 9 and s13 (4ad5acae).
Check files: /home/noob/work/bench_reads/stageC/review_cv5v3/r4/ (RV/r4): run_r4.sh / run_r4.out (all commands), rv4_split.py / .out (my items 1 to 4; r3 script with new pins, run on the published split, candidate d and the copies of a), rv4_balance.md, rv_roots4.py / .out (my root checks on bench_data_v3b, groups with L6), rebuild/ (fresh builds: ruled options and frozen rule), roots_fresh/ (fresh root build), roots_builder_check.out, builder_root_check.out, check_published.out, pytest_full.log, splits_r4_before/after.md5, tables_r4_before/after.md5, worktrees_r4.txt. Own code only, except the reviewed safe loader `udev.load_cells_safe` (bench_wt_split f966127). CPU only, nice 19, one process at a time, foreground. Nothing trained; no sealed label, mask or prediction read (masks of the 532 pool stems only, asserted).

### Verdict: PASS. The builder may now remove /home/noob/work/bench_data_v3 (the unused roots and meta of candidate a).

| Item | Verdict |
|---|---|
| Published = reviewed candidate d, reproduces from the script with the ruled options | PASS |
| 1 Groups (with the SDLE modules) | PASS |
| 2 Folds | PASS |
| 3 Lists | PASS |
| 4 Balance (rule 3 narrowed as the lead ruled) | PASS |
| Set pins = published lists | PASS |
| 5 Roots in bench_data_v3b | PASS |
| Full pytest | PASS |
| 6 Nothing else changed, nothing trained | PASS |

### Published files = candidate d (E: run_r4.out)
- benchmark/splits cv5v3.json 7a700b00, cv5v3_groups.tsv d880a769, cv5v3_check.txt 2afc4cc6, cv5v3.md5 400c1353: each cmp-identical to candidates/d_sdle_fewer_narrow (the candidate reviewed in rounds 2 and 3); the 5 tables in results/stageC/cv5v3 too. CANDIDATES.md5 OK before and after.
- Fresh build at c417732 with the ruled options into RV/r4/rebuild/d: rc 0, ALL CHECKS PASS, all 9 files cmp-identical to the published ones. `--check` with the ruled options: "CHECK OK: 9 of 9 files byte-identical", ALL CHECKS PASS, rc 0.
- Against my round-3 snapshot of benchmark/splits only the 4 cv5v3 lines differ, plus one new file score_exclude_v3.txt (6d48dfbd, written 00:39:27 with the lead's ruling, before the builder started at 00:43; it is in the builder's "before" snapshot too). cv5v2 files, score_exclude_v2c, cv5v3_proposal unchanged. cv5v3.md5, SPLITS.md5, SPLIT_INTEGRITY.MD5.txt check OK.
- Copies of a: REPLACED_A.md5 OK; the 4 split files and 5 tables equal my round-3 md5s of a (f116d37d, d8679d4b, 34f6ac6d, de1d061e; tables 81a6ae5c ...); the json equals bench_data_v3/meta/cv5v3.json. A fresh frozen-rule build into RV/r4/rebuild/a is cmp-identical to all 9 copies (rc 1 from C4 as written, as expected). Held-out md5s of the copy = the retired pins 457fbcf3 ...

### 1 to 4 on the published split (E: rv4_split.out, 0 FAIL lines; output for the published split = output for candidate d)
- 1 Groups: my union-find over L1 to L6 gives 285 groups = the groups file (partition and names). No cv5v2 group split. 0 folds spanned by any cv5v3 group, cv5v2 group, image id, rule-B module, pre-set module, module_group, cell_id, open pair or SDLE stem module (A1 7 cells, A10 2, A11 8, each in one fold). Without L6 (copy of a) the 3 SDLE modules span folds, as reported before.
- 2 Folds: my recompute (R1, R2, R3 exact cost, then fewer cells, then lower fold; unplaced ties in their cv5v2 fold) = JSON on 532 of 532 cells; the other count reading also changes 0 cells. 12 ties: ARTS_00008 -> f3, ARTS_00111 -> f0, ARTS_00118 -> f2, ARTS_00165 -> f3, CFVS_00076 -> f2, CFVS_00156 -> f4, CFVS_00168 -> f4, CSIR_00106 -> f0, CSIR_00178 -> f1, SDLE A1 -> f0, A10 -> f2, A11 -> f4 (cost 54 against 70). 47 moves (ARTS 19, CFVS 12, SDLE 12, CSIR 4). Against the proposal: 16 group joins (4 open pair + 12 SDLE) and 10 tie cells, 0 unexplained. JSON `groups.amendments` records L6 and I3.
- 3 Lists: per fold disjoint, union = pool, pool order, md5 and n fields right; each pool cell held out once; no forbidden, sealed or do-not-train stem (all forms) in any list; no sealed or forbidden stem as text in any cv5v3* file.
- 4 Balance, as ruled: held-out 107 / 110 / 103 / 101 / 111; crack-cell spread 9 -> 4, inactive 8 -> 7 (not worse, not even within the tolerance); classes without training px belt_mark f0, rings f2, clamp f3 = cv5v2's exact cases (clamp cell ARTS_00008_r4_c1 in f3); no source or cell type held out but absent from training; smallest training list 421 = cv5v2. Accepted costs as the ruling states: cells 7 -> 10, CFVS 5 -> 8, CSIR 1 -> 2, SDLE 1 -> 8 (held out 7 / 0 / 2 / 0 / 8), no_spacing 2 -> 7. check.txt: C1 to C5 PASS, C4-info lines print the costs.
- Comparison sets (own definition: cell of a group that spans cv5v2 folds = affected; moved or not): clean_unmoved 416 (crack 190, inactive 40, no SDLE), affected_unmoved 69 (23, 6), affected_moved 47 (16, 2) = cv5v3_compare_cells.tsv cell for cell. score_exclude_v3.txt (116) = my affected set = v2c + the 17 SDLE cells; clean_unmoved = pool minus it.

### Set pins (E: rv4_split.out, rv_roots4.out)
- bench/sets.py at c417732: CV_LIST_MD5 cv5v3 = 79816ba6 / 548af76f / ec7df8fd / b61a2d6f / 2f7c5a7c = held-out md5s of the published JSON = test.txt of each root; SIZES 107 / 110 / 103 / 101 / 111. Root builder PINNED cv5v3.json 7a700b00..., cv5v3_groups.tsv d880a769... (full md5s match). BENCH_CV5V3_ROOTS and BENCH_META_V3 default to bench_data_v3b; `git grep` finds no remaining path to bench_data_v3 in code (only a comment in a test).

### 5 Roots in bench_data_v3b (E: rv_roots4.out ALL PASS, 125 PASS, 0 FAIL; run_r4.out)
- meta: 4 read-only files, each = benchmark/splits bytes; META.md5 ade72e13, -c OK.
- ROOTS_cv5v3_v11.md5 79e8aee8, -c OK. Root builder `--check` at c417732: rc 0, asserts OK (0 forbidden of 167; 0 of 285 groups split; held-outs partition 532; lists = cv5v3.json). A fresh root build into RV/r4/roots_fresh gives the same ROOTS md5 file (0 diff lines), the same splits and the same 532 mask link targets per fold.
- Per fold (my code): train / val / test = JSON (test = val); 0 duplicates; 0 forbidden, sealed or do-not-train; 0 cv5v3 group, cv5v2 group, image id, rule-B module, module_group, SDLE stem module or open pair shared across train and held-out; 532 mask links (train -> masks, held-out -> masks_strict, 0 wrong, 0 dangling); MASKLINKS header = wave 1; labeled -> house dir; layout = cv5v2_v11_f0; SPLITS.md5 and DATA_MANIFEST.md5 -c OK; held md5 = JSON = sets.py pin; SIZES pin right; 0 md5-identical, identical-file or dup_crossfold pair across.
- Near-duplicates at NCC >= 0.85 across train and held-out, summed over folds: 1,130 (cv5v2 1,156 by my count; the builder's 1,160 counts the 4 dup_crossfold entries twice, as in round 1). 12 pairs cross that did not in cv5v2: 4 ARTS r1_c6 serial-band corner crops (ARTS_00021 / 00118, and the 3 pairs among 00026 / 00102 / 00114) and 8 SDLE pairs between different stem modules. Matches the builder.
- Builder's own root check script: rc 0, 101 PASS, 0 FAIL, ALL PASS.

### Code, tests (E)
- 6a3876a, c417732: 10 files, +69 / -26; docstrings, help, RULED constant, pins, folder defaults, one new root check (SDLE module), tests. Both messages end with the Opus 5.5 co-author line. No upstream, no remote branch holds c417732 (not pushed). Worktree clean.
- cv5v3 + cv5v2 set tests: 34 passed. Full pytest at c417732: **667 passed, 4 skipped, rc 0** (RV/r4/pytest_full.log).

### 6 Nothing else changed, nothing trained (E: run_r4.out)
- Worktrees: el_bench 31c0c36, bench_wt_w2 c57508e, bench_wt_udev ae4dd10, bench_wt_a 81b4505, bench_wt_b b5bf0ae, bench_wt_split f966127, bench_wt_sev c2fed43, bench_wt_rows1 52e3f14, bench_wt_rows2 b12fca8: same HEADs as round 3, 0 tracked changes. Only bench_wt_cv5v3 moved (616da42 -> c417732), clean.
- bench_data, bench_udev, bench_data_v3, bench_dumps: 0 files newer than my round-3 end (00:39:54); bench_data_v3 0 files newer than 15 Nov 23:56 and its ROOTS md5 still checks. bq and bench_relay: no new top-level entry. ROOTS_cv5v2_v11 and ROOTS_cvloso2_v11 check OK. My runs left splits, tables, CANDIDATES.md5 and REPLACED_A.md5 unchanged (md5 before = after).
- Nothing trained: the GPU holds two wave 2a runs (seed 6, cwd bench_wt_w2, roots bench_data/roots/cv5v2_v11_f3 and f4) and another user's process; no cv5v3 run, dump, queue dir or c3_* experiment exists.

### Remaining notes (none blocks)
- S (wording): cv5v3_check.txt line I4 still says SDLE is "not a link of the rule". It is an information line and output bytes of the reviewed candidate; the VARIANT lines, `[C1] PASS SDLE module named in the stem` and the JSON amendments say L6 is in. Accept as is.
- E (typo, builder, text only): CV5V3_BUILD.md s13a item 5 writes the f0 pin as `79816ba6cca96e10265197eb4cfa905` (31 hex chars); sets.py and the JSON hold `79816ba63cca96e10265197eb4cfa905`. Fix the text; no file or pin is wrong.

### For the lead before the cv5v3 baseline runs are prepared
1. Deploy: bench_cv5v3 is not merged anywhere. The runs need its bench/sets.py (cv5v3 pins) for the dumps and its read tools; the deploy commit (c417732 or a merge with ae4dd10) is your call. bench_wt_udev has queues pinned: the merge must not happen in that worktree.
2. cv02: cq.sh needs ruling/cq_cv5v3b.patch (DATA_V3 default /tmp/noob_el/bench_data_v3b; the fix1 patch points at bench_data_v3 and must not be used). Rebuild the roots on cv02 from bench_data_v3b/meta and compare ROOTS_cv5v3_v11.md5 with 79e8aee8 except the MASKLINKS lines; /tmp is wiped on reboot.
3. Reads: every cv5v3 read must pass `--groups /home/noob/work/bench_data_v3b/meta/cv5v3_groups.tsv` (285 groups); a's 299-group file is refused by w1read.check_groups. cv5v2 reads use score_exclude_v3.txt (116), whose clean set equals cv5v3's clean_unmoved (416) (E).
4. Costs you accepted, to state in the protocol: SDLE is scored only in folds 0, 2 and 4 (7 / 0 / 2 / 0 / 8), so per-source SDLE numbers come from 17 cells in 3 folds; fold sizes 101 to 111. 12 near-duplicate look-alike pairs (NCC >= 0.85) newly cross train and held-out, with 25 crossing pairs gone (net 1,130 against 1,156).
5. Open from s8 / s13d: HOUSE cv5v2 seeds 7 to 9 (15 runs) or a HOUSE comparison on seeds 5 and 6 only; machine choice for the 50 runs.
6. After the builder removes bench_data_v3, the only copies of a are results/stageC/cv5v3/replaced_a/ (REPLACED_A.md5), which the frozen rule rebuilds byte for byte (E).

(The round-3 text below is kept as written; its item-4 FAIL is resolved by the ruling and this delta review.)

## Verdict: FAIL (item 4 only; still waits on the lead's rulings F1 and F2; no builder error found)

| Item | Verdict |
|---|---|
| 1 Groups | PASS (published split and candidates a to d; SDLE note settled only by F2) |
| 2 Folds | PASS (each split follows its declared rule, cell for cell; F5 reading now written) |
| 3 Lists | PASS (all reproduce byte for byte; no forbidden, sealed or do-not-train stem) |
| 4 Balance | **FAIL** against the lead's rule 3 as written, for the published split and for every candidate. Crack cells, inactive cells and classes without training px are not worse in any of them. log.md still has no ruling that narrows rule 3 (last entry 15 Nov 23:42). |
| 5 Roots | PASS (published roots unchanged and pass again; b to d have no roots yet, which is right before a ruling) |
| 6 Nothing else changed | PASS |

Fix round 2 changed no output byte and no code path (E). F5 and F6 are done and right. Item 4 fails for the same reason as in rounds 1 and 2: R1 + R2 and "must not get worse" on every rule-3 count cannot both hold (none of the 512 tie placements does, RV/rv_ties.out). Only the lead can unblock it.

## Fix round 2 (616da42): checked
E (git diff 7aaf0a4..616da42; RV/r3/run_r3.out):
- 3 files, +24 / -3: the module and assign_folds docstrings of bench/cv5v3.py, one help line in scripts/bench_make_cv5v3.py, one new test. No executable line changed. The commit message ends with the Opus 5.5 co-author line. bench_cv5v3 has no upstream and no remote branch holds 616da42 (not pushed). Worktree clean.
- F5: the docstrings and the help line state that while a tied group is costed, tied groups not yet placed count in their cv5v2 folds. This is the reading I recomputed as the main one, and it matches the code (`new = dict(fold_v2)`).
- The new test `test_unplaced_tied_groups_count_in_their_cv5v2_folds`: I checked the toy by hand. With B in its cv5v2 folds, A -> f0 gives [3,1,1,0,0] and A -> f1 gives [1,3,1,0,0], cost 6 = 6, so f0 under both tie-breaks (fold sizes also tie). With B left out, [3,0,0,0,0] costs 7.2 and [1,2,0,0,0] costs 3.2, so f1. The test separates the two readings and pins the stated one.
- F6: the assign_folds docstring no longer calls tie_size=True "information only". It names it amendment I3, the rule only if the lead rules F1 (b). That is right under either ruling.
- CV5V3_BUILD.md section 12 states the facts above correctly, including that only candidate c depends on the reading (4 cells).

## 1. Groups: PASS
E (RV/r3/rv3_candidates.out, byte-identical to RV/r2/rv2_candidates.out; own union-find over L1 cv5v2 group, L2 image id, L3 rule-B module from module_identity_v3 94a357a8, L4 the 4 open pairs from the score_exclude_v2c header 28acb0ff, L5 cells.tsv module_group, and for c and d also L6, the SDLE module token in the stem):
- Published and a: 299 groups; b: 299; c and d: 285. In each my partition equals the `group` column of that split's cv5v3_groups.tsv.
- No cv5v2 group is split in any split.
- 0 folds spanned by any cv5v3 group, cv5v2 group, image id, rule-B module, pre-set-rule module, cells.tsv module_group, cell_id or open pair, in all five. Under L6 (c, d), 0 SDLE stem modules span folds.
- SDLE (S, F2): without L6 (published, a, b), modules A1 (7 pool cells) and A11 (8) span all 5 folds and A10 (2) spans f2 and f3. Not a rule-1 input, so not an item-1 fail; only F2 settles it.

## 2. Folds: PASS
E (RV/r3/rv3_candidates.out):
- My recompute (R1, R2, R3 exact integer balance cost, then lower fold or, for I3, fewer cells then lower fold; unplaced ties in their cv5v2 fold) equals the JSON folds on 532 of 532 cells for the published split and each of a to d. R1 holds in all five.
- The other count reading (unplaced ties left out) changes 0 cells for the published split, a, b and d, and 4 for c (ARTS_00165 / 00166 r12_c5 f3 -> f1, CSIR_00178_r7_c1 / CSIR_00207_r7_c5 f1 -> f0). Since 616da42 the stated reading is written in the code, help and results file, so c is no longer ambiguous.
- Against the audit's proposal (31 moves): published and a: 4 open-pair joins + 20 tie cells; b: 4 + 10; c: 16 group joins (4 open pair + 12 SDLE) + 20 ties; d: 16 + 10. 0 unexplained.

## 3. Lists: PASS
E (RV/r3/rv3_candidates.out, run_r3.out, rebuild/):
- In all five splits: 5 folds; per fold, train and held-out disjoint, union = pool, pool order, md5 and n fields right; each pool cell held out exactly once.
- No stem, base stem or _rf form in any list is forbidden (9bb4d919), sealed (role test / E1) or do-not-train (5a22e8cc); no sealed or forbidden stem appears as text in any cv5v3* file.
- Published `--check` at 616da42: "CHECK OK: 9 of 9 files byte-identical" (rc 1 from C4 as written, as before).
- Fresh builds of a to d at 616da42 into RV/r3/rebuild: each is cmp-identical to its candidate on all 9 files (4 split, 5 table files). CANDIDATES.md5 OK before and after.
- benchmark/splits and results/stageC/cv5v3 unchanged by these builds (md5 before = after).

## 4. Balance: FAIL (lead's rule 3 as written)
E (RV/r3/rv3_balance.md, identical to round 2; v1.1 training masks, pool cells only; equal to the builder's 11b table). Spreads = max minus min over the 5 folds:

| split | held-out per fold | cells | crack | inactive | ARTS | CFVS | CSIR | SDLE | multi | no_spacing | moves | clamp fold | smallest train |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| cv5v2 | 107 / 111 / 104 / 104 / 106 | 7 | 9 | 8 | 5 | 5 | 1 | 1 | 17 | 2 | - | 3 | 421 |
| published = a | 104 / 124 / 102 / 98 / 104 | **26** | 5 | 7 | **15** | **10** | **2** | 1 | **20** | 2 | 35 | 1 | 408 |
| b (I3) | 104 / 114 / 104 / 104 / 106 | **10** | 5 | 7 | 3 | **8** | **2** | 1 | 17 | 2 | 35 | 3 | 418 |
| c (L6) | 107 / 120 / 101 / 95 / 109 | **25** | 4 | 7 | **15** | **10** | **2** | **8** | **20** | **7** | 47 | 1 | 412 |
| d (L6 + I3) | 107 / 110 / 103 / 101 / 111 | **10** | 4 | 7 | 3 | **8** | **2** | **8** | 17 | **7** | 47 | 3 | 421 |

Bold = larger than in cv5v2. Said plainly:
- **Crack cells:** not worse in any split (9 -> 5 or 4).
- **Inactive cells:** not worse in any split (8 -> 7).
- **Classes without training px:** not worse in any split: 3 cases each (belt_mark f0, rings f2, clamp f1 or f3), the same 3 classes as cv5v2; b and d keep cv5v2's exact cases. The only pool cell with clamp px is ARTS_00008_r4_c1.
- No fold holds out a source or cell type its training list lacks, in any split.
- **Worse than cv5v2 on counts rule 3 also names:** fold size (best 10 against 7), CFVS (8 at best against 5), CSIR (2 against 1); with L6 also SDLE (1 -> 8) and no_spacing (2 -> 7). No split under R1 + R2 avoids this. The candidates pass only under the narrowed C4 (`--c4-scope scoring`), which the lead has not ruled.
- S: d remains the best candidate on what scoring uses (crack spread 4, cv5v2's clamp case, smallest training list 421 = cv5v2), and it closes the SDLE links.

## 5. Roots: PASS
E (RV/r3/rv_roots_r3.out, equal line for line to rounds 1 and 2, ALL PASS, 0 FAIL lines):
- bench_data_v3/roots/cv5v3_v11_f0..f4: train / val / test lists equal the published JSON; 0 duplicate, forbidden, sealed or do-not-train stems; 0 groups, modules, image ids or open pairs shared across train and held-out; 532 mask links per root (train -> masks, held-out -> masks_strict, 0 wrong, 0 dangling); labeled links right; wave 1 layout and MASKLINKS header.
- `md5sum -c` OK for roots/ROOTS_cv5v3_v11.md5 (pin 9c148c7e) and meta/META.md5; meta files equal benchmark/splits bytes and are read-only. 0 files under bench_data_v3 newer than 15 Nov 23:56.
- b, c and d have no roots: right before a ruling.

## 6. Nothing else changed: PASS
E (RV/r3/run_r3.out):
- benchmark/splits: all files equal my round-1 start snapshot; cv5v3.md5, SPLITS.md5 and SPLIT_INTEGRITY.MD5.txt check OK. results/stageC/cv5v3 tables unchanged.
- bench_data, bench_udev, bench_data_v3, bench_dumps: 0 files newer than 15 Nov 23:56. ROOTS_cv5v2_v11.md5 and ROOTS_cvloso2_v11.md5 check OK. bench_relay: only rows2 is newer (the cv02 rows queue). bq: no new top-level entry.
- Worktrees (RV/r3/worktrees_r3.txt): el_bench 31c0c36, bench_wt_w2 c57508e, bench_wt_udev ae4dd10, bench_wt_a 81b4505, bench_wt_b b5bf0ae, bench_wt_split f966127, bench_wt_sev c2fed43, bench_wt_rows1 52e3f14, bench_wt_rows2 b12fca8: same HEADs as round 2, 0 tracked changes. bench_wt_cv5v3 moved 7aaf0a4 -> 616da42 (the fix commit only), clean.
- Full pytest on bench_cv5v3 at 616da42: **666 passed, 4 skipped, rc 0** (RV/r3/pytest_full.log; 665 + the new test). cv5v3 tests: 27 passed.
- Nothing trained: the GPU holds two w2a2 runs (seed 6) from the running wave 2a queue and another user's process; no cv5v3 run, dump or queue dir exists.

## Exact fixes
- **F1 (lead, blocking; unchanged): rule on rule 3 / C4 and the tie-break.** Rule 3 as written cannot pass under R1 + R2 (E). Choose (a) the frozen tie-break with rule 3 narrowed to crack cells, inactive cells, classes without training px, and no source or type missing from training (`--c4-scope scoring`), or (b) **my choice (S):** I3 (`--tie-break fewer`) with the same narrowing. Write the ruling, with the exact options, into log.md.
- **F2 (lead, blocking; unchanged): SDLE links (L6) yes or no.** S: yes, so candidate d. If no, write into PROTOCOL section 3.1 that A1 and A11 (15 pool cells) span all folds in cv5v3.
- **After the ruling (builder), then my delta review:** as in CV5V3_BUILD.md 11c. (a): replace only cv5v3_check.txt and cv5v3.md5 in benchmark/splits and bench_data_v3/meta, renew META.md5, with the lead's yes. b, c or d: rebuild with the 11c command and cmp against the candidate reviewed here (must be byte-identical); re-pin PINNED in scripts/bench_make_roots.py and CV_LIST_MD5 / SIZES of cv5v3 in bench/sets.py; build meta and roots in a fresh folder (bench_data_v3b) and point BENCH_META_V3 / BENCH_CV5V3_ROOTS, and DATA_V3 on cv02, there; rerun the full pytest. My delta review then: rv_roots.py on the new roots and JSON, the root builder `--check`, the set tests.
- **F3 (lead, deploy):** the cq.sh patch goes in at the deploy merge and must point DATA_V3 at the folder the chosen roots are built in.
- F5 and F6: done (616da42), nothing more needed.
