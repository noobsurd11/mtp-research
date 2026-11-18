# Review of stage A (CPU analyses), 14 Nov 2026, 06:20 to 06:35 IST

Reviewer: independent agent (built none of it). Object: branch `bench_a` at **81b4505** (worktree `/home/noob/work/bench_wt_a`), result files `results/stageA/{A1,A2_P1_G5,A2_metric_probe,A3_ci_error_atlas,A4,A5_head_res_ceiling,A6_duplicates}.md`, tool outputs under `/home/noob/work/bench_reads/stageA/`. Read: BRIEF 1 to 3 and 7, LEAD_INSTRUCTIONS, W1G_FIRST_READ, W1_READ, WAVE3_REVIEW sections 1, 2 (verdict lines), 4, 6, HANDOVER 5, specs T12 sections 1, 2, 4, 5, T9 1.4, T2 G5, T10 A0, T11 A0.
Own check files: `/home/noob/work/bench_reads/stageA/review/` (scripts `rv_dumps.py` 2e9dc61d, `rv_analyse.py` e64b1901, `rv_ncc.py` 5df80014, `rv_tau95.py` 2bf55ccc, `rv_tau.py` 35ec658f; outputs `rv_analyse.out` 25d8cd0d, `rv_ncc.out` 8c8434fd, `rv_tau95.out` c3a39524, `rv_tau.out` dc5881ee, `a1_r_sd.out` 9f83b277, `sealed_runtime.out` dbf14f07, `overwrite_refusal.out` 4203f223, `pytest_full.log`). My scripts share no code with `bench/`; they read the npz files with numpy and the v1.1 masks with PIL. CPU only, nice 19, 8 workers, tmux `bench_a_review` (pytest, pane 110990) and `bench_a_review2` (recompute, pane 131936); both ended by themselves.
Tags: E = measured by my own command; S = judgement.

## Verdict
| Item | Verdict |
|---|---|
| A1 aa_calibration | **PASS WITH NOTE** |
| A2 S1 derived dumps + metric_validity_probe + P1 / G5 | **PASS WITH NOTE** |
| A3 ci_error_atlas | **PASS WITH NOTE** |
| A4 tau_from_annotators | **PASS** |
| A5 head_res_ceiling | **PASS WITH NOTE** |
| A6 duplicate tool | **PASS WITH NOTE** |
No item fails. The notes are wording fixes in the result files and one unsafe owed command; no number changes.

## Hygiene (all items, E)
- `git status` clean at 81b4505; 7 commits since c57508e, all only ADD new files (22 files, 5,423 lines; no existing file edited); all 7 messages end with the Co-Authored-By line; nothing pushed.
- Full pytest on bench_a: **534 passed, 4 skipped**, rc 0 (446 at c57508e + 88 new).
- Other trees untouched: el_bench 31c0c36, bench_wt_w2 c57508e, bench_wt_rows1 52e3f14, all with 0 tracked changes. No file under bench_data, bench_relay/w1c, bench_reads/w1g, s2c newer than 04:41 (stage A start); files newer than 04:41 in bq are the w1g2 queue's own, in bench_relay the rows1 relay's own.
- Refusal to overwrite, tested on real outputs: bench_aa.py, bench_atlas.py, bench_tau_pairs.py all refuse before reading anything. Determinism: my rerun of bench_tau_pairs.py into a new folder gives byte-identical tau.json 20ca3890, tau.txt 8d980181, tau_pairs.tsv ee0e9550.
- Manifest md5s of inputs are printed by every tool (aa.json runs, atlas summary, probe / edge logs, ens-dump and headres derived manifests with `derived_from`, dup inputs block).
- No tmux session or process of stage A is left running.

## Sealed sets (all items, E)
- Grep of the 16 new files: only bench_dupsearch.py names test50 / e1_106 image paths (images only; no mask path, no dump path); tau.py loads the sealed list to refuse it; no new tool uses a label column of cells.tsv (atlas loads cells.tsv only to list the 532 pool stems).
- Run-time: `derived.assert_open` (sealed set and sealed stem in an open set), `tau.open_check`, `tau.load_class`, `dumpfmt.check_set("test50"/"e1_106")`, `sets.resolve("test50")` all raise. The tau sealed list (156) is contained in forbidden_v1 (167).
- Dup tool: contact sheets assert no forbidden or sealed stem per drawn image; the 6 PNGs in `results/stageA/dup_sheets/` are the only images written into the project tree. Outside the tree, `dup/run1/feats/feat_lab.npz` holds 128 x 128 band-pass (DoG) descriptors of all 814 labelled images, the 156 sealed ones included (pixel derivatives, allowed by L2, not labels).
- Observation for the lead (not a tool fault): `bench_data/meta/cells.tsv` carries label-derived columns (has_crack, crack_px, ...) for the 156 sealed rows. Any reader of whole rows touches sealed label summaries. My own awk check printed those columns for 2 test50 rows (logged in BUILD_LOG at once; nothing computed or written from them).

## A1 aa_calibration: PASS WITH NOTE
Spec fidelity (E, code read): splits, the 'fold' stage (= boot_pair call order, unit-tested), the 'set' stage (k seeds per fold drawn with replacement, the spec's replacement), M = max(0.01, 2 SE_AA), MDE table, part (d) DEFF, as spec section 1. Promotion counted in both orientations (stricter than the spec's one-sided rule). Reading rule thresholds equal the spec and Y1.
Independent recompute (E, `rv_analyse.out`): per-seed pooled W1-C1 metrics equal the A1 table to 4 decimals (crack IoU s5..s9 0.3671 / 0.3649 / 0.3654 / 0.3609 / 0.3658; inactive 0.4904 / 0.4958 / 0.5204 / 0.5087 / 0.4983). Over the 15 k = 2 splits: RMS of deltas crack IoU 0.0023, relF1@2 0.0021, inactive 0.0119 (= tool); canonical {7,8} - {5,6} inactive +0.0214 (= tool's +0.021).
Part (e) (S, algebra checked): with V(k) averaged over all disjoint splits of one seed set, the average of (sum of k values - sum of k values)^2 / k^2 equals 2(m2 - p)/k for every quadratic form, so V(1) = 2 V(2) and a = 0 identically, for the seed part and for the group-bootstrap part alike. The builder's claim is right: the Y1 test 2 sqrt(a) > 0.05 can never fire from an A/A. L4 (count-based inactive policy) does not depend on it.
Statistics: 330 groups, 2,000 draws, seed 0; no selection on scored cells (OP-F / OP-W from the reviewed crossfit_op).
Notes and exact fixes:
1. **r uses RMS, the spec says sd.** RMS is the better estimator (orientation of an A/A split is arbitrary) and was stated in the reading rule, but it changes one branch. E (`a1_r_sd.out`): with the spec's sd, crack IoU has r = 0.649 (fold) and 0.798 (set), so under spec rule 3 the 'set' stage would pass its adoption check for crack IoU while relF1@2 (0.506 / 0.615), inactive (0.391 / 0.478) and mIoU-R13 (0.467 / 0.568) would not. M is unchanged in every case (crack IoU stays at the 0.01 floor). Fix: add to A1.md section 3 item 2: "Under the spec's literal r = sd(delta) / mean SE, crack IoU would adopt the 'set' stage (r 0.65 to 0.80) and the other three would not; the metrics then point to different branches, so whether to replace the seed stage is the lead's decision. M is the same under both."
2. Time stamp: the rule says "written 04:50, while the W1-C1 run was computing", but BUILD_LOG and aa.json mtime put the end of that run at 04:49. Write-before-read cannot be checked from file times. Fix: correct the time or the phrase in A1.md section 1.
3. gaint M is still owed (W1-G2 seeds 7, 8: 0 of 10 dumps at 06:29). The command in A1.md section 4 is correct as written.

## A2 S1 + metric_validity_probe + P1 / G5: PASS WITH NOTE
Spec fidelity (E, code and outputs read): ensemble = mean softmax from `logp`, argmax; `derived_from` holds the members' manifest md5s; probes P-wide / P-thin / P-drop / P-shift as spec section 2; eligibility E1 to E3 and the headline rule as written; centreline F1@2 follows the spec formula (Ts against the predicted MASK), which is why it rewards dilation; the Y13 limits and Y8 confirmation are applied. P1 uses the critic's fix (edge at OP-W >= M, strict crack IoU); G5 (b) as T2.
Independent recompute (E): ensemble minus single-seed mean, strict crack IoU, argmax: **+0.0116** on W1-G (ens 0.3740, singles 0.3599 / 0.3649) and **+0.0116** on W1-C1 (0.3776; 0.3671 / 0.3649); relF1@2 +0.0108 / +0.0106; inactive +0.019 / +0.015. All equal the tool.
Statistics (E): my group bootstrap of the same edge with the seeds held fixed gives SE 0.0008 / 0.0009 (cells flat 0.0007); the tool's SE 0.0026 / 0.0019 is wider, as expected from the one-seed-per-fold stage that A1 shows to overstate SE. Not narrower than a naive check. OP-W is cross-fitted on other folds.
Notes and exact fixes:
1. P1 (b): the spec reads P(missed by seed 6 | missed by seed 5); the file decides on the mean of both orders (0.814 / 0.804). The spec's order gives 0.765 (W1-G) and 0.848 (W1-C1): same outcome (below 0.9). Fix: print the spec's order as the rule value in A2_P1_G5.md section 3 item 2.
2. P1 opens on its point estimate (0.0116 >= 0.010) while its interval low (0.0068 / 0.0080) is below M; the critic's text ("beat ... by at least M") does not say point or interval. The file states both; the lead should know the opening rests on the point.
3. Derived manifests write `precision: fp32` and `seed: 56` for an ensemble built from float16 `logp` of seeds 5 and 6. Fix (next commit, no rerun needed): `precision: "fp32 from fp16 logp"` or a separate `source_precision` key. Not a number change.
4. G5 (c) is not run; it needs in-sample teacher maps and the lead's OK (stated correctly in the file).
5. Metric probe: the headline does not reproduce (W1-G relF1@2, W1-C1 strict IoU), so no v0.2 change; the stable parts (relF1@2 passes E2, centreline F1@2 as specified fails E2) are results. Correct under the pre-set rules.

## A3 ci_error_atlas: PASS WITH NOTE
Spec fidelity (E, code read): buckets, first-applicable order, 8-connected components, coverage thresholds (T10 0.10, T6 0.20, T8 0.50), oracles, (d) rule statistics, (e) softmin control and FL / ML candidates as T10 A0; every gate carries the group interval, the leave-top-3 value and region counts (Y4); BMRK and per-fold rows (G20). The P-GIN (d) deficit threshold was set by the builder (the critic gave none) and is declared as such.
Independent recompute (E): T6 region-miss share of inactive FN (seed-mean pooled counts) **0.496 (W1-G) and 0.528 (W1-C1)** = tool; G-rules: 284 of 285 GT inactive regions >= 100 px have GT crack within 5 px (0.9965) = tool.
Statistics: two-stage group bootstrap; the G-bias oracle and the P-GIN decile cut are in-sample by the spec's own design and are labelled optimistic / descriptive; no gate decision uses a fitted parameter.
Notes and exact fixes:
1. **Owed command is unsafe.** A3 section 6 runs `git checkout -q 8e0c17e -- bench/atlas.py scripts/bench_atlas.py` inside the shared worktree; if a later builder changes those files, this silently reverts them and leaves bench_a dirty. Fix: drop the checkout (bench_a HEAD 81b4505 holds the 8e0c17e versions; verified, no later commit touches them), or run from `git -C /home/noob/work/el_bench archive 8e0c17e` unpacked into a scratch folder.
2. G-paste is closed only by its FL clause, and the FL score belongs to the part (e) scorer whose positive control failed (4 of 7). The file says so and leaves it to the lead: correct; the lead should treat G-paste as "condition 1 holds, condition 2 untrusted".
3. T6 gate 1: W1-G 0.496 in band, W1-C1 0.528 BUILD; not reproduced under Y8, so LEAD DECIDES. Correct; seed noise exceeds the distance to 0.5.

## A4 tau_from_annotators: PASS
Spec fidelity (E, code read): mutually nearest skeleton points (critic fix 1), growth rule fixed in the reading rule, leave-@2 only if CI low > 2.5 on NG AND DA (critic fix 2), spec's statistic kept as secondary; pairs with a legacy test cell are refused before any read (25 pairs).
Independent recompute (E, `rv_tau95.out`; own NCC alignment, own Zhang-Suen thinning, own mutual-NN): alignment shifts equal the tool's for all 7 pairs; pooled NG **tau95 2.000** over 4,927 distances (tool 4,926), shares <= 1 / 2 / 3 px 0.865 / 0.969 / 0.995 (= tool); DA tau95 2.000, 835 distances, 0.902 / 0.993 / 1.000 (= tool). Per pair only CFVS_00102 / 00103 differs (2.295 vs 2.325, skeleton detail).
Outcome holds: CI lows at or below 2.5, so the headline tolerance stays @2; the spec's citable condition holds. The evidence is thin (6 NG pairs, 1 DA), as the file says.

## A5 head_res_ceiling: PASS WITH NOTE
Spec fidelity (E): model side as T11 A0 (avg-pool of `logp`, bilinear, align_corners False, dumpfmt writer, read with the reviewed bench_read_w1); GT side added as the critic's lower bound; the band is printed and bars nothing (critic's fix).
Independent recompute (E, own torch avg_pool2d + interpolate on v1.1 GT, ignore px excluded, pooled IoU over 532 cells): **stride 4, best t 0.30, crack IoU 0.5214, width ratio 1.365** = tool (0.521, 1.365).
Statistics: the threshold sweep is in-sample by construction (a ceiling, not a model result); the model-side OP-W is cross-fitted.
Note and exact fix: the spec's assert "s = 1 reproduces the PF dump byte for byte" does not hold (S1 = argmax of float16 `logp` differs from fp32 `pred` at 1,698 of 278.9 M px, 11 crack px); the builder used S1 as the paired baseline and printed the difference, which is the right comparison, and S1 reproduces the first-read metrics to 4 decimals. Fix: add one line to A5.md section 1: "Deviation from the spec: the s = 1 byte-for-byte assert is replaced by S1 = argmax(logp) as baseline; difference printed in section 2." The owed command passes two `--arm S1=` and two `--arm S4=` specs with one name each; that use is untested, so check that bench_read_w1 merges them into one arm (4 seeds) before reading the output.

## A6 duplicate tool: PASS WITH NOTE
Spec fidelity (E): md5, NCC (T8 C0 descriptor) and DINOv2 ViT-S/14 cosine with 8 dihedral views; tau = 5th percentile of known same-cell pairs and the AUROC pre-check as T12 section 5; pool list rule as T9; images only (L2).
Independent recompute (E): (a) my own NCC descriptor on 11 open pairs (`rv_ncc.out`) agrees with the tool within 0.0005 on every pair: the 5 near-exact pool copies (0.9996 to 0.9999), ARTS_00046 / 00040 0.9926, 3 cross-fold candidates 0.8808 to 0.9511, 2 low pairs 0.5097 and 0.5449. (b) From the tool's stored embeddings, my own calibration: 60 known pairs of 16 cells, **tau 0.830, different-source false alarm 6.6% of 232,079 pairs, AUROC 0.991** = tool.
Outcome: the T12 tau rule passes its pre-check but flags 17,863 cross-fold links and leaves 266 pool cells; the builder applied nothing and left the choice to the lead. Correct handling of an unusable rule.
Notes and exact fixes:
1. `dup/run1/pool_t9.txt` (266 stems) carries the official list name although nobody may use it. Fix: in the next run (or by the lead), write the literal rule output as `pool_t9_T12literal.txt`, or add `dup/run1/README` saying "literal T12 output, unusable, do not copy". The chosen list must drop the 5 near-exact copies (confirmed by my NCC).
2. The labelled-set clause "if the different-source false-alarm rate is not small, the lists are printed as candidates and the lead decides" has no number and was set by the builder; the dry run on the full labelled set (05:57 to 06:01) already showed tau and the 6.6% rate, and the file times cannot show which came first. Its outcome is "lead decides", so nothing was bent toward a number; state the order in A6.md section 1.
3. `feat_lab.npz` holds DoG descriptors of the 156 sealed images (see the sealed section). Keep it outside the project tree; delete `run1/feats` and `dry/feats` once the lead has chosen a list.
4. UCF C0 formally fails (227 NCC hits); per rule they are excluded. Correct.

## Final table: number, rule, outcome, may the lead rely on it
| Item | Number (E) | Rule | Outcome | Rely? |
|---|---|---|---|---|
| A1 | 0 of 15 A/A splits promoted, relF1@2 OP-A (and 0/15 on all headline metrics) | <= 1 of 15 | screen rule holds its error rate | yes |
| A1 | r (RMS) 0.74 / 0.55 / 0.49 / 0.48; set stage 0.91 / 0.66 / 0.59 / 0.58 | r in [0.7, 1.5]; set adopted only if its r is in band | no stage change; under the spec's sd, crack IoU would adopt 'set' (0.65 to 0.80) | yes for M; the seed-stage choice is the lead's |
| A1 | M cv02 OP-A: 0.010 crack IoU, 0.010 relF1@2, 0.010 mIoU-R13, 0.049 inactive | M = max(0.01, 2 SE_AA) | these are the cv02 margins | yes (recomputed spreads equal) |
| A1 | inactive MDE(2) 0.052 | > 0.08 bars inactive | does not fire | yes |
| A1 | a = 0 (identity) | 2 sqrt(a) > 0.05 | rule cannot fire from an A/A; L4 stands on its own | yes, as "unusable" |
| A1 | M gaint | same | owed (W1-G2) | not yet |
| A2 | ens2 edge strict crack IoU +0.0116 (both machines), CI low 0.0068 / 0.0080 | P1: edge at OP-W >= M | opens on cv02 at M 0.010 (point; CI low below M) | yes, with that caveat |
| A2 | edge +0.0116 and relF1@2 +0.0108 / +0.0106 | G5 (b): >= 0.005 | passes; G5 (c) not run | yes for (b) |
| A2 | P(s6 miss given s5 miss) 0.765 / 0.848 | > 0.9 lowers the expectation | does not fire | yes |
| A2 | headline z: W1-G relF1@2, W1-C1 strict IoU | eligible max z, 10% band, S_j; Y8 | not reproduced: no v0.2 headline change | yes |
| A2 | centreline F1@2 P-wide +0.0137 / +0.0136; relF1@2 -0.004 (CI holds 0) | E2 | centreline F1@2 not eligible; relF1@2 keeps its place | yes |
| A3 | G-rules 0.996 | < 0.97 -> d = 10 | d = 5 | yes (recomputed) |
| A3 | R-a 0.1% / 0.6% deleted; R-b 0.6% / 0.5% added | >= 3% | ci_rules_posthoc not built | yes |
| A3 | G-layer 0.370 / 0.366, O1 + O5 +0.153 | >= 0.25 or >= 0.04, lt3 holds | OPEN (layered_ci is the D2 arm) | yes |
| A3 | FN-missed 0.378 / 0.393; FL share 0.660 / 0.627 | >= 0.35 and < 0.50 | CLOSED by the FL clause, whose scorer failed its control | as written yes; the lead may set the FL clause aside |
| A3 | T6 region-miss 0.496 / 0.528 | >= 0.5 BUILD, band 0.3 to 0.5 | LEAD DECIDES (not reproduced) | yes (recomputed) |
| A3 | P-GIN (d) +0.092 / +0.099, CI holds 0 | deficit = point < 0, CI < 0, lt3 < 0 | NO DEFICIT | yes, for P532 only |
| A4 | tau95 NG 2.000 [2.000, 2.000], DA 2.000 [1.414, 2.000] | leave @2 only if CI low > 2.5 on both | stays @2; spec's citable condition holds | yes (recomputed), thin evidence |
| A5 | s4 - s1 OP-A crack IoU -0.203 / -0.206, relF1@2 -0.309 / -0.306 | >= 0.05 or >= 0.02: "head binds" | head binds; printed beside stride-4 rows, bars nothing | yes |
| A5 | GT lower bound s4: IoU 0.521, relF1@2 0.955, width 1.365 | printed | ceiling above PF's level | yes (recomputed) |
| A6 | AUROC 0.991; tau 0.830; FA 6.6%; 17,863 links; pool 266 | T12 rule | rule unusable; nothing applied; lead decides | yes (recomputed calibration) |
| A6 | 5 pool cells are the same image as P532 / F51 cells (NCC >= 0.9996) | any chosen pool list drops them | must be removed | yes (recomputed NCC) |
| A6 | UCF 227 NCC >= 0.80, 0 md5 | C0 | excluded per rule; layout matches (S) | yes |
