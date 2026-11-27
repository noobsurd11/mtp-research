# Re-review of the stage B fix round (F1, F2), 15 Nov 2026, 17:40 to 17:58 IST

Reviewer: independent agent (built none of it). Object: branch `bench_b` at **b5bf0ae** (worktree /home/noob/work/bench_wt_b; F1 c7ba76f, bea6a47; F2 fdb6a5c, 8f9178b, 4920802, b5bf0ae over 60fcf70); products /home/noob/work/bench_udev/{build_shvoof_v2, jobs_v2, opc2}; tool outputs /home/noob/work/bench_reads/stageBfix/{F1,F2}; result files results/stageB/{B3 s1b + s8, B1_classbias_xfit s5 + 5a, F2_read_options, SAMECELL_AUDIT}.md.
Read: BRIEF 1 to 3, 5, 7; LEAD_INSTRUCTIONS; REVIEW_STAGEB (full); BUILD_LOG Stage B and fix round; log.md 13:51 (duplicates), 16:01 (protocol), 16:07 (stage B rulings) to 17:11; PROTOCOL_v0.2 s3, s5, s10, s11.
Own check files: /home/noob/work/bench_reads/stageBfix/review/ (rv_u2_build, rv_fake_u2b, rv_jobs, rv_dnt, rv_u4sheet, rv_identity, rv_x528, rv_cb_v2, rv_samecell, rv_shv_v2, rv_v2_edge, rv_opc2_manifests, rv_sets_refuse: .py and .out; pytest_full.log). My scripts share no code with `bench/` except on purpose: the synthetic-dump writer and read tool (U2), the root writer (guard test), the sheet tool, `classbias.crossfit_biases` (planted leak). CPU only, nice 19, at most 8 workers; tmux `bench_bfix_review` (panes 1864360, 1886853, 1908739 / python 1909648, 1922476; all ended by themselves; session gone). Synthetic dumps (fake_u2b, 83 MB) deleted after use.
Tags: E = measured by my own command; S = judgement. No sealed label or prediction read; no sealed image read.

## Verdict
| Item | Verdict |
|---|---|
| 1. U2 rebuild, read path, job lists | **PASS WITH NOTE** |
| 2. U1 rule text | **PASS WITH NOTE** |
| 3. Pack guard and sheet-to-masks script | **PASS WITH NOTE** |
| 4. Read-tool options (score-exclude, crack-free n, OP-C class lines) | **PASS WITH NOTE** |
| 5. Class-bias variant 2 | **PASS** (the check; the variant itself FAILS its rule, correctly) |
| 6. Same-cell audit | **PASS WITH NOTE** |
| 7. Hygiene | **PASS** |
No item fails. The REVIEW_STAGEB item 1 FAIL is closed: every shvoof line may be armed from jobs_v2 after the merge and identity check.

## 1. U2: PASS WITH NOTE
E (rv_u2_build.out, rv_fake_u2b, rv_jobs.out):
- build_shvoof_v2: `md5sum -c` of its MANIFEST.md5 OK, md5 of MANIFEST.md5 **8dda906e** = `SHVOOF_MANIFEST_MD5` in bench/sets.py, 3,202 entries. **0 of 1,064 views** (image, mask, ignore) are not 512 x 512.
- Spec: every shvoof_f<k> view's source cell is in cv5v2 fold k's held-out list and the sources cover that fold exactly (2 halves each); union 1,064 views = stems_eval.txt, 532 source cells, no duplicate. View lists byte-equal to the B3 lists (fd21d9ad, a9c7e50e, d9d1d68a, 2c36e373, fe3ebc2b = the UDEV_LIST_MD5 pins). Against the B3 build: masks and ignore differ in exactly the 4 views of ARTS_00100_r1_c2 and CFVS_00177_r1_c4; images differ in 1,062 of 1,064 (per-stem seeds). context.tsv: gap rule found 518, none 12, wide_fallback 2; the fallback cells carry g 9 and sy 1.1898, the values of the 12 no-gap cells; their views are real cells (grey mean 124 to 169, sd 22 to 53, mask classes present; CFVS_00177 keeps its crack).
- Code (udev_shv.py diff): fallback when `zoomed_rows(g) < 512`, assert 512 x 512 on every view before it is yielded, stem-seeded rng in mode 'stem'; stream mode kept for the SHV1 check.
- Synthetic read in the reviewer's pattern, made stronger: two DIFFERENT arms (PF: pred = GT of every view; B: pred = GT with crack removed in folds 0 and 1), seeds 5, 6, written by sets.resolve on the new build. `--labels v11`: refused, rc 1. `--labels set`: **rc 0**; 1,064 cells (532 source cells, folds 0 to 4), 330 groups, effective n crack 20.6, inactive 12.2 (= B3 values); B relR@2 **0.6646** = my own count of GT crack px (non-ignore) in folds 2 to 4 over all, 434,074 / 653,168 = 0.6646; PF 1.000; B - PF frontier -0.335 [-0.584, -0.175] "below 0". So groups by source cell, fold k and the label path all work.
- Roots, U4, U5 unchanged: B3 MANIFEST.md5 still 41a0c35c and `md5sum -c` OK; ROOTS_cvloso2_v11.md5 c82ebe1c, cvloso2.json 16b0f1bd, u5_csir_multi 14bf0cb3, h36cf 68218088, pool_half a4752dba; no file in bench_udev newer than 16:07 outside build_shvoof_v2, jobs_v2, opc2 except the two PREP.md files (asked by the fix).
- jobs_v2: JOBS.md5 OK (7c971ea6); udev_infer 174 lines, equal to the B3 list with the `--dumps` root masked; 6 dump roots, **each holds one set family**, 0 (dump root, run id) pairs with more than one set; every `--run` checkpoint exists; no sealed set name. loso2 lists unchanged (6c07b4db, 33c2af8a). jobs/ and jobs_tta/ JOBS.md5 still OK.
- PREP.md read lines: jobs_v2/PREP.md U2 read uses dumps_shvoof, the rebuild's stems_eval.txt and `--labels set`; jobs/PREP.md (superseded note, "do not arm udev_infer of this folder") and jobs_tta/PREP.md corrected; the diffs against the saved originals (36b2892e, 7f26a4bf) touch only those lines.
- Nothing armed: no bq queue other than dry_t1/2, w1g, w1g2, w1g_smoke, w2a, w2a2, w2a_smoke; no bench_wt_udev, no bench_udev/dumps*, no tmux session for udev, loso or tta.
Note (wording, no fix needed for use): B3.md 2 keeps "max grey difference 81" from the B3 build; for build_shvoof_v2 the val views differ from SHV1 by at most **98** grey levels, masks equal (rv_shv_v2.out). The bracket already says it is a different draw; add the 98 if the sentence is edited again.

## 2. U1 rule: PASS WITH NOTE
- E: B3.md 1b rule 6 carries the lead's ruling (log.md 16:07): pooled 164 held-out cells (CSIR 114 + BMRK 50) decide, frontier read with width ratio and two-stage interval; per-source reads (eff n 8.3, 16.2) printed, cannot decide alone; opposite signs of at least M in the two sources = "inconsistent", U1 then not a primary. Every element of the lead's sentence is there; wording equal in substance. Dated 16:14 (BUILD_LOG line 16:14).
- E: no LOSO-2 experiment, dump or queue exists now (17:45): no directory named *loso* under /home/noob/work beyond the root, split and job folders; no bench_udev/dumps; no bq/udev*; on cv02 (read-only listing) no *loso* run dir and no queue other than rows1, rows2, w1c and their smokes. So the rule precedes any number, whatever the exact minute.
- jobs_v2/PREP.md has the pooled and both per-source commands.
**Note (open rule gap, lead):** the clause "opposite signs, each of at least M" does not say which M: the pooled M_U1 or each source's own A/A M (both get printed). It must be fixed in writing in rule 6 before any LOSO-2 number exists. Not a builder defect.

## 3. Pack guard and sheet script: PASS WITH NOTE
E (rv_dnt.out, rv_u4sheet.out, rv_sets_refuse.out):
- do_not_train.txt (5a22e8cc) = the 24 stems of label_pack_U4/stems.txt (313797b2) plus their _rf forms, 48 entries. A stem, its _rf form, a view of it (`__h1`) and `_rf__h0` all hit; an unrelated stem does not.
- `udev.write_roots` on a toy split with one real pack stem in train: refused with the do-not-train message, **0 files and 0 dirs written**; the same split without it gets past the guard (fails later on my dummy group map, as expected). 0 hits in the train / val / test lists of the 10 wave 1 roots and 2 LOSO-2 roots. bench_make_roots calls the guard on the pool and on every re-read list (code read).
- Sheet script, my own synthetic fills (copies under review/u4sheet/): full sheet (cell 1 model mark A, cell 2 all D, cell 3 one '?', cell 4 one S, cell 5 one miss M C4 D4) and short sheet (cell 1 crack y + mark A; cell 3 crack '?', scuff y with E5). Both rc 0, SOURCE.json synthetic true. My pixel check: crack px of cell 1 = the label-map component px exactly (7 px) in both formats; D-only cells crack 'no', use_false_alarm yes, no ignore; '?' and S marks go to ignore only (S also scuff); miss M = 2 squares (8,192 px) ignore, crack 'yes', 0 crack px; short '?' cell wholly ignored; no crack px under ignore anywhere.
- Refusals (rc 1, output folder not created): the user's unfilled results.csv (213 of 285 rows empty) and results_short.csv (67 of 67); a short sheet with crack 'n' and an A mark; a full sheet with one row deleted.
- The user's files are untouched: results.csv 1286a270, results_short.csv a87b27f6 before and after my run, equal to SHEETS_unfilled.md5 (written by the lead 16:08:23, before the round) and file mtimes 14:06 / 16:06.
- `sets.resolve('u4lab')` refused (no pin); test50 and e1_106 still raise SealedSetError.
Notes (S):
1. As the builder says, the guard is only in the two root builders; train.py and bench_q do not call it. Any future builder of a pool training list (SSL, distillation, pool pseudo-labels) must call `bench.donottrain.assert_clean`; put that sentence into the spec of any such arm.
2. On a u4lab read, crack recall is measured only on located cracks: a missed crack enters as ignore squares, and on the short sheet a cell answered 'y' with one A mark scores any other unmarked crack in it as background. State this beside any u4lab recall number.

## 4. Read-tool options: PASS WITH NOTE
E (rv_identity.out, rv_x528.out, rv_cb_v2_part1.out):
- Option off: my own rerun of the W1-G four-seed read at b5bf0ae (fresh cache, 8 workers) against the stored bench_reads/w1g4/read: read.txt 98 lines, 1 differs (the header's tool md5); read.json 9,450 leaves, NaN-aware compare: only `tool_md5` and `seconds` differ. Byte-identical apart from those.
- 528 values, my own code from the dumps and masks (no bench code): PF seeds 5 to 8, pooled at argmax, crack IoU **0.3646 (532) / 0.3643 (528)**, per seed 0.3599 / 0.3649 / 0.3697 / 0.3640 and 0.3597 / 0.3646 / 0.3694 / 0.3636; inactive IoU 0.5025 / 0.5025. Equal to F2_read_options 3c.
- Crack-free n, own count: v1.1 (non-ignore crack px == 0) **303 of 532, 301 of 528**; v1 (masks_escdd) **300**; the three cells with v1 crack and none in v1.1 are ARTS_00051_r6_c2, CSIR_00117_r8_c4, CSIR_00176_r5_c2; none the other way. So the builder's explanation is right: 303 is the v1.1 count, and the definition in crossfit_op.guards / w1read.crackfree (GT crack px over scored px == 0 in the record) is the scoring label set. The x528 and OP-C reads print the definition and "303 of 532 | 301 of 528".
- OP-C class lines: printed in opc_demo/read/read.txt. My own recompute (mean over seeds 5 to 8, 532 cells): OP-C gridline IoU 0.3623, precision 0.4885, recall 0.5840, 46,389 px on 174 gridline-free cells, share 0.046; splice 0.1126 / 0.1988 / 0.2068 / 12,710 px on 472 cells / 0.183; S1 gridline 0.3021 / 0.6331 / 0.3663 / 15,648 / 0.032; splice 0.0210 / 0.3362 / 0.0220 / 194 / 0.095. Equal to the file line for line.
- `--score-exclude` loader fails closed on sealed or forbidden stems and on a stem not in the read (code read of w1read.load_exclude / apply_exclude).
Notes:
1. PROTOCOL_v0.2 s10 item 6 and s11 item 5 still say the 303 comes "from the v1 metadata": wrong; fix text (lead): "303 is the v1.1 crack-free count (v1 gives 300); every read already defined crack-free by the scoring label set; 301 on 528 cells." No number changes.
2. bench_udev_read, bench_aa, bench_headres, bench_ens_edge, bench_labelfree lack the option (S: correct for the U-dev reads, which take an explicit stem list and whose sets other than U2 hold none of the 4 cells; U2 does hold their views: a U2 read for a final table should pass a stems_eval list without the 8 views of the 4 cells, and list that in jobs_v2/PREP.md when a 528 U2 table is wanted).

## 5. Class-bias variant 2: PASS
- Rule before run (E): B1 s5 says written 16:34; BUILD_LOG 16:45 records it. Independent evidence: commit **fdb6a5c at 16:44:48** already holds `verdict_v2` with the rule's constants (V2_MIOU_SLACK 0.002, V2_PREC_SLACK 0.02, rules 2, 3a, 3b) and run_f2.sh holds the edge rule; the first variant 2 number exists at 17:22 (classbias_b.tsv mtime; chain log fit 17:16 to 17:23). bench/classbias.py is unchanged from fdb6a5c to b5bf0ae; the only later read change (b5bf0ae) restricts the 528 guard tables to kept stems (3 lines), not a threshold. The fit manifest's commit 8f9178b changed only samecell files and tests (`git diff --stat fdb6a5c 8f9178b`), and bench_classbias.py md5 7af85609 is the same at both.
- Cross-fitting (E, rv_cb_v2_part2.out; own superset cache for the v2 box: px with top - runner-up <= 5.5 or top - z11 <= 9.5, seed 5): the library fit with `grids('v2')` (class 11: -1.5 to +8.0, 39 values; others 23) on my cache gives b_0 = the v2 tsv row (5, 0) exactly (b11 = 5.0). **Planted leak** (fold 0 replaced by poison: all GT splice, random logits, 1e9 splice px): b_0 **unchanged**. Control, same poison in fold 1: b_0 moves (b16 4.0, b11 8.0, b13 -0.75, ...). All 20 OP-C2 manifests name fit_folds = the other four folds, carry their tsv row, variant v2, open set (rv_opc2_manifests.out).
- Numbers recomputed (E, own code, rv_cb_v2_part1.out): seed 5 OP-C2 dump pred = argmax(float32(logp) + b_v2(5, k)) at **every px of all 532 cells** (0 differ); S1 = argmax(logp), 0 differ. Seeds 5 to 8 (per seed printed): mIoU-R13 S1 0.6129, OP-C 0.6266, OP-C2 0.6267; crack IoU 0.3646 / 0.3635 / 0.3609; inactive IoU 0.5025 / 0.5129 / 0.5166; pooled inactive precision 0.7694 / 0.7493 / 0.7274; cell precision 0.9542 / 0.9516 / 0.9499. Rule 1 points hold (+0.0138, crack -0.0037, inactive +0.0141), rule 2 holds, **rule 3a fails** (-0.0419 against -0.0401; the file's -0.0420 is the same number rounded from unrounded means), 3b holds. Edge count own: b11 = +8.0 in **14 of 20** fits (mean 7.60, min 5.00).
- Variant 1 untouched (E): bench_udev/opc MANIFEST.md5 e1cabf4c, `md5sum -c` OK; B1 fit tsvs d6a2bf00 / 2b9f5691; nothing in bench_udev/opc or bench_reads/stageB newer than 16:07; OP-C - S1 recomputed +0.0137 (= first review).
- (S) The FAIL does not hang on the lead's open question (3a pooled precision or 3b cell precision): the edge rule fired in 14 of 20 fits, so no cv02 confirmation exists and variant 2 cannot pass under either reading. Variant 1 stays OP-C; ledger count 2.
Wording slip (no effect): B1 5a "the other 10 classes got the variant 1 value in 217 of 220 (seed, fold, class) cells" should read **197 of 200** (10 classes x 20 fits; 3 differ, as listed; rv_v2_edge.out).

## 6. Same-cell audit: PASS WITH NOTE
E (rv_samecell.out):
- Coverage: my own enumeration of same-source pool pairs with different cv5v2 folds gives **30,974** (ARTS 13,243, CFVS 11,418, CSIR 5,198, BMRK 1,000, SDLE 115) = the set of pairs in run2 pairs.tsv exactly; fold columns right; ranked by inliers; counts at >= 5 / 10 / 15 / 20 / 30 / 50 = 397 / 92 / 47 / 30 / 23 / 19 as reported; run 1 and run 2 give identical inliers for every pair.
- Calibration (calibration.tsv): lead's confirmed pairs 216 and 37 inliers (ranks 9 and 22 of the full list); lead's 5 rejected pairs 0, 4, 0, 0, 0; 35 known same-cell pairs: 6 below 10 (0, 0, 0, 0, 3, 5), 29 at 33 to 1,527. It is honest about being in-sample (parameters set on these 42 pairs; stated in s2 and s5).
- Sheets: 532 stems in pairs.tsv, all pool, 0 legacy test, 0 forbidden; the script reads images only for the 532 pool stems (code: fold_of from cv5v2 held-outs, assert_open); sheet_1 viewed: pool cell images with stem / fold headers, emission contour and inlier points, no label.
- No split or list changed: cv5v2.json 441d118f (both copies, mtimes 12 and 13 Nov), cv5v2_groups.tsv e44f0668, dup_crossfold_v1.tsv fc89e708 (mtime 13:51, the lead's).
Notes (for the lead's ruling, S):
1. The finding is real and larger than the 4 cells: 17 of the 19 pairs with >= 50 inliers are neighbouring crops of one physical module under two image ids in different folds (16 image-id pairs, 60 pool cells), and sheet_1 shows the same serial text on both images of pairs #3 and #4. cv5v2's module groups therefore miss image-id links. The ruling options are as SAMECELL_AUDIT 4 lists (v2 exclude list read beside 532 at once; regrouping needs new runs).
2. The matcher misses featureless mono pairs (6 of 35 known pairs below 10 inliers), so the list is a lower bound, as the file says.

## 7. Hygiene: PASS
- E: full pytest at b5bf0ae: **614 passed, 4 skipped**, rc 0 (pytest_full.log); tracked changes 0 before and after, 0 untracked non-ignored files. 6 commits since 60fcf70, each message ends with the Co-Authored-By line; no remote ref for bench_b (nothing pushed).
- E: since 16:07 the only changed git refs are refs/heads/bench_b and its worktree files; el_bench 31c0c36, bench_wt_w2 c57508e (the running w2a2 tree), bench_wt_a 81b4505, bench_wt_rows1 52e3f14, bench_wt_rows2 b12fca8: 0 tracked changes. Files newer than 16:07 outside bench_wt_b, bench_udev, bench_reads/stageBfix and the team folder: only bq/w2a2 and gpu_gate (the running queue), bench_relay (rows2 relay) and bench_rows2_io/review (the rows2 reviewer, 16:20 to 16:30): none from F1 or F2.
- Info: tmux session `bench_b_B3` (an idle bash, pane 4177041, from the B3 builder at 13:10) is still open; not from this round, harmless; whoever owns it may close it by that PID.

## Exact fixes (none blocking)
1. Lead: write into B3.md 1b rule 6 which M decides "inconsistent" (pooled M_U1, or each source's own A/A M), before any LOSO-2 number.
2. Lead: PROTOCOL_v0.2 s10 item 6 and s11 item 5: replace "303 from the v1 metadata" by "303 is the v1.1 crack-free count (v1: 300); reads define crack-free by the scoring label set; 301 on 528 cells".
3. Lead: rule on the same-cell audit (v2 exclude list or regrouping); if a 528 U2 table is wanted, pass a U2 stems list without the 8 views of the 4 cells.
4. Text only, any time: B1 5a "217 of 220" -> "197 of 200"; B3.md 2 add "build_shvoof_v2: max grey difference 98".
5. Spec rule for future pool-training arms: call bench.donottrain.assert_clean on the training list.

## Final table: product or number, rule, outcome, may the lead rely on it
| Product or number (E) | Rule | Outcome | Rely? |
|---|---|---|---|
| U2 build_shvoof_v2 (MANIFEST 8dda906e, 1,064 views) | REVIEW_STAGEB 1 fix, T7 0.2 | all views 512 x 512; fold guard, coverage, lists unchanged; only the 4 fallback views' masks changed | **yes** |
| bench_udev_read on shvoof (--labels set, groups by source cell, fold k) | REVIEW_STAGEB 1 fix | own two-arm synthetic read rc 0, B relR@2 = own count 0.6646; v11 refused | **yes** |
| jobs_v2 (JOBS.md5 7c971ea6; udev_infer 1bcb077e) and corrected PREP.md files | one dump root per set family | holds; nothing armed | **yes**: arm from jobs_v2 after the merge and identity check, never jobs/udev_infer |
| LOSO-2 roots, U4 / U5 lists, B3 MANIFEST 41a0c35c | unchanged | md5sum -c OK | yes |
| U1 deciding read (B3 1b rule 6) | lead's ruling 16:07, before any LOSO number | written; no LOSO run exists | yes, after the M of the "inconsistent" clause is fixed |
| Do-not-train guard (5a22e8cc) | REVIEW_STAGEB 3 note 3 | refuses a pack stem before writing; 12 roots clean | yes (root builders only) |
| Sheet-to-masks script, set u4lab | both formats, refuse unfilled / contradictory / altered | own fills match own pixel check; refusals hold; user's sheets untouched | **yes**; pin the real build's MANIFEST md5 after the user fills a sheet |
| --score-exclude in 5 read tools | off = identical; on = 528 beside 532 | W1-G identical (tool md5, seconds only); crack IoU 0.3646 / 0.3643 recomputed | **yes** |
| 528 v 532: no PASS* flag, sign or verdict changes; shifts <= 0.0004 | ruling 13:51 | one headline recomputed equal | yes |
| Crack-free n 303 (v1.1) / 301 (528) / 300 (v1) | scoring label set | own count equal; protocol text wrong about v1 | yes; fix the protocol text |
| OP-C gridline / splice lines | ruling 16:07 | printed; recomputed equal | yes |
| classbias variant 2 = FAIL (rule 3a -0.0419 v -0.0401; edge 14 of 20) | B1 s5, written before code and numbers | rule pre-dates numbers (commit 16:44:48); leak test clean; numbers recomputed | **yes**: variant 1 stays OP-C, ledger count 2, no third grid |
| OP-C2 dumps (opc2 MANIFEST 415a523d) | cross-fit | 20 manifests clean; pred = argmax(logp + b) at every px (seed 5) | yes (descriptive only) |
| Same-cell audit: 2 known duplicates confirmed, 5 rejected pairs 0 to 4, 16 cross-fold image-id pairs of one module, 4 same-cell candidates | masked matcher, in-sample calibration | coverage exact (30,974); deterministic; pool images only; no list changed | **yes** as a candidate list for the lead's eye; a lower bound |
| Full pytest 614 passed, 4 skipped at b5bf0ae | suite passes | holds | yes |
