# coach verify: protocol_SKR2C v1 opening (SKR01 vs SUPPF, fresh seeds 10-14; singles R and 5-member ensembles D at a shared b 0; gaint); E1 opening #7

coach, 14 Nov 2026, written 05:05-05:11 IST (`date`). Independent recompute, done on gaint. This is the first verdict of this opening: the lead read no number and gave me none. judge's check is the last section (CONFIRMED WITH FIXES). Tags: E (measured, with the file), S (judgement). "Same cells" below always means the same 50 test and 106 E1 cells as #5 / #6: this is the 3rd look for this contrast.

## Verdicts
- **R (recipe, singles s10-14, rule 1): FAIL, by guards G1 and G2** (E, `results/s2c/coach_v/coach_s2c_R.txt`; same cells).
  - G1: test inactive IoU Δ −0.0198 (all 50) / −0.0207 (clean 49); bar ≤ −0.015 in both sets.
  - G2: test crack relP@2 Δ −0.0780 (all 50); bar < −0.03. G2's E1 arm did not trip: 3,931 vs 4,211 px on the 74 crack-free cells, ×0.93; bar ×1.5 = 6,316 px (ruling 1).
  - Co-primaries: 1 BETTER (E1 crack relF1@2 +0.0289, thr 0.0281), 0 WORSE, 6 n.d. Protocol §3a: "FAIL: any WORSE, or any guard tripped". The BETTER label does not change that.
- **D (deployable, E-SKR2' vs E-SUPPF', both at b 0): FAIL, by guard G1t alone** (E, `coach_v/coach_s2c_D.txt`; same cells).
  - G1t: test inactive IoU Δ −0.0269 (all 50) / −0.0283 (clean 49); bar ≤ −0.015 in both sets.
  - Primaries: 1 passes (E1 crack relF1@2 +0.0342, CI [+0.0115, +0.0544]), 0 fail, 4 n.d. Guards G2a, G2b, G1e not tripped.
  - Fixed wording (§3b / §3c): "inactive guard alone: D's G1t null false-FAIL ~8%; with R's G1 ~9-15%, ~15% combined that a true null keeps SUP100-PF through an inactive guard alone."
- **Combination (§3c): "R FAIL or D FAIL → the SUP100-PF ensemble stays (#6's E-PF at b 0)."** Both are FAIL.
  - R's FAIL is caused by G1 and G2. It is not "G1 alone", so §7's G1-alone sentence does not attach to R's line by the letter.
  - D's FAIL is caused by an inactive guard alone, so D's line carries the false-FAIL sentence above.
- **Named claim (§3a): REPLICATED does not hold** (E).
  - Condition 1 (seed-aware two-stage bootstrap of E1 relF1@2, 10 fresh singles, seed 0): CI [−0.0015, +0.0590], estimate +0.0289. Not wholly above 0: **fails**, by 0.0015.
  - Condition 2 (D's E1 relF1@2 primary passes): **holds** ([+0.0115, +0.0544]).
  - Condition 3 (neither R nor D is FAIL): **fails**.
  - Lower tier, fixed wording: **"the fresh-seed ensemble pair differs on E1 relF1@2 (fixed-model CI; seed noise not included); replication at recipe level not shown"**.
  - R's rule-1 label for E1 relF1@2, reported next to it as §3a requires: **BETTER** (+0.0289, thr 0.0281; margin 0.0008).
  - Reading note (S): "If only D's ensemble CI passes" can be read as (i) condition 2 holds and condition 1 does not, or (ii) that plus condition 3. Under (i) the lower-tier sentence is stated, as above. Under (ii) no fixed sentence exists for this case. Both readings give "REPLICATED does not hold" and "replication at recipe level not shown". Judge rules (i): the lower-tier sentence is stated. It is not a pass and is always quoted next to 'D FAIL by G1t'.
- **Handbook line (§7, fixed wording filled in):**
  > SKR2C (E1 #7; same 50 test and 106 E1 cells as #5 / #6, 3rd look). **R FAIL** by G1 (test inactive IoU −0.0198 / −0.0207) and G2 (test crack relP@2 −0.0780, all 50): the Skeleton Recall route closes for the deployable at w 0.1. **D FAIL** by G1t (test inactive −0.0269 / −0.0283), an inactive guard alone: D's G1t null false-FAIL ~8%; with R's G1 ~9-15%, ~15% combined that a true null keeps SUP100-PF through an inactive guard alone. The SUP100-PF ensemble stays (#6's E-PF at b 0). E1 relF1@2: the named claim REPLICATED does not hold (seed-aware CI [−0.0015, +0.0590]; R and D both FAIL); R's rule-1 label BETTER (+0.0289, thr 0.0281; margin 0.0008); "the fresh-seed ensemble pair differs on E1 relF1@2 (fixed-model CI; seed noise not included); replication at recipe level not shown".
- **Where the two R trips sit** (E, `coach_v/coach_s2c_extra.txt`; leave-outs, no bar or set changed):
  - **G2 is one run on one cell.** SKR01 s13 predicts 49,713 crack px on the noisy test cell CSIR_00070_r8_c4 (GT 787 px), 34% of that run's predicted crack px on test. The other 4 SKR01 runs predict 0 to 926 px there; the 5 SUPPF runs 0 to 2 px.
    - s13's test relP@2 is 0.6147 on all 50 and 0.9361 on the clean 49.
    - Δ on the clean 49: −0.0119. Δ without SKR01 s13: −0.0151. Δ without module CSIR_00070: −0.0119. None of these would trip.
    - The guard is registered on all 50, so the trip stands.
    - Five separate inference passes of the opening agree: 49,713 px in the m0 default pass, the scuff-ignored pass and the B5 record at b 0; test crack IoU 0.3427 in the rescore pass and the LA tau 0 pass, as in m0. So it repeats under the opening's GPU bf16 scoring; it is not one bad pass. The five passes share the weights and bf16, and fp32 on test was not run, so it is not shown at another precision (on val, D gate (a) has s13 at CPU fp32 within 0.0013 of bf16).
  - **G1 trips in 9 of 10 seed drops and 47 of 48 module drops.** Not tripped only without SUPPF s13 (−0.0133 / −0.0139) or without module CFVS_00114 (−0.0142 / −0.0149).
  - **Verdict R is FAIL in all 10 seed drops.** No single module drop removes both trips.
  - Without G2, R would still be FAIL, by G1 alone, and §7's sentence would attach: "G1 null false-FAIL ~9-15% (S2 W1); with D's G1t ~8%, ~15% combined that a true null closes the route through an inactive guard alone". I give it for that reason; it is not part of R's line by the letter (S).
- **Runner's readout: CONFIRMED** (E, section 4). Every estimate, threshold, label and guard value equals mine to 4 dp; D's CIs are equal to full float precision. The runner's files hold no R verdict (review note N4): the R verdict above is assembled here for the first time.
- **Integrity: no problem found** (E, section "Integrity"; `coach_v/integrity.txt`, 73 checks).

## Inputs, order and code (E)
- **Opening:** gaint, driver `s2c_opening.sh`, FROZEN.md5 836be7e5 (27 files), 14 Nov 00:22:45 to 03:54:57 IST.
  - The driver waited at the shared GPU gate until 02:23. R's GPU passes ran 02:23:28 to 03:36:26 (`post_pids.txt`). D ran 03:36:26 to 03:54:53, CPU fp32.
  - End line `s2c opening done: R rc=0 D rc=0` (`/home/noob/work/s2c/opening.log`).
- **Files I used:** the project copies `results/s2c/raw_r` (MANIFEST bb6dffea, 354 files) and `results/s2c/raw_d` (MANIFEST 648ff42b, 15 files). `md5sum -c` passes at the source and at the copy; file lists are equal.
- **My code** (own; it calls neither the runner's readout nor the opening's scorers):
  - `scripts/coach/coach_s2c.py` **8adaef8e**: verdict R, verdict D, the named-claim bootstrap, the §3c combination, fragility, reported items.
    - It reuses my earlier coach functions: `coach_thin` (rule1, twoset, e1_agg, load_m0), `coach_s2` (e1_vals, test_vals, g1, g2, b5_arm_w), `coach_verify` (counts, metrics), `coach_skr2e` (feats, metr, boot, cfree_px), and the feats / metr / boot of my `coach_s2_boot.py` 7ea26cfb (copied verbatim).
  - `scripts/coach/coach_s2c_integrity.py` b13a2461; `scripts/coach/coach_s2c_extra.py` 4be6328f (written after the verdict outputs; reported lines only).
- **Self-test before any SKR2C number was read** (`coach_v/coach_s2c_selftest.txt` 729d649e, 04:55:47 IST): SELFTEST PASS, 92 lines, on opened files only.
  - #5 (SUPPF s5-9, SKR01 s5-9): every co-primary, threshold, guard and the PASS of `verify_skr2_hc2.md` to 4 dp; B5 OPs 3.9 / 3.9 and 4.8 / 2.7; the seed-aware CI [+0.0038, +0.0756] of `boot.txt`; leave-one-seed-out 5 / 10; leave-one-image-out 65 / 71.
  - #6 (E-PF vs E-SKR2 at b 0): the runner's seed-0 CIs of `verify_skr2e.md` to 4 dp (so my "seed 0" draws are the registered ones), and my own #6 CIs with the second stream.
- **Order** (file times in `results/s2c/coach_v/`):
  - integrity 04:45 to 04:47 (rerun about 05:03 after a comment-only edit of the script; the same 73 ok lines); self-test 04:55:47; R 04:56:19; D 04:56:53; md5 list `MD5_first` 04:56:53.
  - Only after that did I open `results/s2c/local/`, `local_extra/` and the opening's own text outputs (e1_coprim, guards, named_boot, b5w_table, D gate, D checks).
  - R / D / combine outputs are unchanged since `MD5_first` (bb7f3fc4, aa2c73f4, bc5939f2). Final list: `coach_v/MD5`.
- **CIs.**
  - "Seed 0" means a fresh numpy `default_rng(0)` per bootstrap, stems and clusters sorted, one `rng.integers(0, n, n)` per resample. These are the draws of Track M `m1_analyze.boot` and of the pf2e cluster bootstrap, fed into my own metric code.
  - A second stream (`default_rng(12345)`, shared across sets) is printed beside every D interval. No pass, fail or trip differs between the two streams.
- **Limits of the independence** (E):
  - The per-cell files (m0 JSONs, B5 records, E-*.json) are the opening's inference outputs. I ran no model.
  - B5 starts from the opening's per-b count records (`rec_w`), as at #5; the dump-to-record step is not recomputed.
  - The runner's readout and mine ran on the same interpreter (gaint venv, python 3.12.3, numpy 2.5.2). The independence is in the code.

## Integrity (E, own commands; `coach_v/integrity.txt` 5d6b8b2f)
| item | result |
|---|---|
| FROZEN.md5 | 836be7e5 on gaint `open/`, in the project, and the copy in `post/`. `md5sum -c` OK at both ends (27 files). `open/` holds exactly the listed files, none writable, no `__pycache__`; newest file 00:00:11, before the 00:22:45 start. The 27 md5s equal `build_s2c_stage2.md` §4. |
| MANIFESTs | post bb6dffea (353 lines), d_out 648ff42b (14 lines); `-c` OK at source and copy; every file but the MANIFEST itself is covered. |
| End lines | `opening.log`: "s2c opening done: R rc=0 D rc=0". `post.log`: "decision passes failed: 0", "s2c scoring done: post rc=0". `d_run.log`: "s2c D full end rc=0". No HOLD, no refusal log. |
| rc files | `decision_rc.txt`: e1_coprim, b5w, realsplits_b5, guards, named_boot all rc=0. `extra_rc.txt`: enc_cosine, cellgate, scuffign, realsplits_scuffign all rc=0. |
| Real splits, the opening's asserts | `realsplits.txt`: 11 calls, 11 PASS, 116 "-> True", 0 False. `d_realsplits.txt`: PASS (3 E-*.json files). |
| Real splits, my own check | 115 per-cell / per-run files (m0 default / tau0 / tau1, scuff-ignored, B5 rec / rec_w, LA, rescore, the 3 D files): test stems = the 50 of el_f3 `data/splits/test.txt` (a31fad14); E1 stems = the 106 of `ext117/stems_eval.txt` (5266806b); val stems = the 54 of val.txt (9dcccf00). The training root's `test.txt` is the val list (9dcccf00; SPLITS.md5 24568cdb) and shares 0 stems with the real test list. No file holds it as "test". |
| The 10 fresh runs | m0: 15 JSONs per arm = s10..s14 × (default, tau0, tau1); run names inside equal the file names. D members: s2c_SUPPF_100pct_s10..14 and s2c_SKR01_100pct_s10..14, step 20000, model code e544133. `latest.pth` md5s agree three ways (R `init_check.txt`, D `member_latest_md5.txt`, the files now). No other s2c_* run dir, no *_STOPPED_* dir: no stop or rerun happened. |
| Training | per run: 1 header, 1 "step 20000/20000", 0 Traceback, 1 "val: 54  test: 54" (counts only); launch.log 5d2544a7 "config OK" and "trained rc=0" once each; ALL TRAINED line; autostop log without a trigger. Config diff vs pf2_SUPPF_100pct_s5 = seed + run_name + `data.root` (+ `skel_recall.weight 0.1` for SKR01). Worktrees: el_thin c9bbb02, el_f3 e544133, 0 tracked changes. |
| Scorer md5s | `md5sum -c scorer_md5_expected.txt` passes now (22 files); the opening's own check shows 22 OK. 18 of the 22 are named in the review / build and match (m0_audit d36f7438, m0_audit_tau d77241bb, m0_audit_b3 7aa7d6d8, rescore 1e41202b, LA ec315d2e / 419486b1, gate 00fabfdd, e1_context 12bd1385, the split lists, the exp files, launch.log). The other 4 are pinned by the frozen driver only (enc_cosine d3bc7a70, mim_step0 178b872d, B5_DEVICE 4e7ff566, the reference config 6aba106a). |
| tau 0 | my comparison: tau0 cells = default cells for all 10 runs; tau1 differs in 10 of 10; step 20000; code_revision c9bbb02 / e544133; conf 24×24. Equal to the opening's `tau0_check_*.txt`. |
| D order | val decisions and gate written 03:42:47; test / E1 per-cell files 03:54:52 (`d_out` file times; `d_full.log` prints "val decisions written" before "test done"). |
| D gate (a) | all 10 members within tolerance, CPU fp32 vs their R m0 (GPU bf16): largest \|Δ\| crack IoU 0.0004, relF1@2 0.0013 (SKR01 s13); val any-hit equal for all. Val GT comps 125, E1 296 (`s2c_d_gate.txt`). |
| gaint readout script | the stored diff equals my `diff -u` of `s2c_post_local_gaint.sh` 1f43dc6f against the frozen `s2c_post_local.sh` 1da9a692. From the first m2_rung call to the end of the file (3 m2_rung calls, the collected-outputs block, the `s2c_d_boot.py` call) the two files are equal once the stderr redirect is dropped. The changes are: local copy instead of ssh, gaint's Python, two more md5 pins plus the D self-test, stderr kept. No scoring command changed. |
| gaint Python | `env_check.txt`: `s2c_d_boot.py --selftest` SELFTEST PASS. My own check: m2_rung on opening #5's files under gaint's Python gives md5 e0de918a (tau 0) and f7c5bc23 (tau 1), the md5s of the 3 Nov laptop outputs. |
| Registry before the opening | `e1_openings.md` #7 and `test_openings.md` row 18 carry "registered, NOT opened" lines dated 14 Nov 00:13 with 836be7e5. |

- **My own script first** (disclosed): its first three runs flagged 4 lines or stopped on a KeyError. All were wrong expectations in my file, none a fault of the opening: 13 real-splits calls expected (the driver makes 11); the B5 records' `runs` field expected as a bare name (it is the run path); the LA JSON expected with 20 keys (it has 40, each tau also with `_maskabsent`); a line-picking heuristic for the scoring commands. Corrected; the kept file is a later run with every line ok.

## 1. Verdict R: 7 co-primaries and 2 guards (E, `coach_v/coach_s2c_R.txt`)
Rule 1, /3, 5 v 5, seed means ± sd. Test and B5 co-primaries by the two-set rule (all 50; clean 49 without CSIR_00070_r8_c4). The threshold is rule 1's. The interval column is the seed-aware two-stage bootstrap (seed 0); it is reported and enters no label of verdict R.

| co-primary | SUPPF | SKR01 | Δ (thr) all 50 | Δ (thr) clean 49 | seed-aware 95% interval, all 50 / clean 49 (reported) | outcome |
|---|---|---|---|---|---|---|
| test crack IoU | 0.4692 ± 0.0030 | 0.4438 ± 0.0568 | −0.0254 (0.0656) | +0.0021 (0.0100) | [−0.1068, +0.0079] / [−0.0055, +0.0096] | n.d. |
| test crack relF1@2 | 0.8902 ± 0.0018 | 0.8551 ± 0.0777 | −0.0351 (0.0898) | +0.0012 (0.0100) | [−0.1633, +0.0068] / [−0.0056, +0.0089] | n.d. |
| test inactive IoU | 0.4681 ± 0.0205 | 0.4483 ± 0.0091 | −0.0198 (0.0259) | −0.0207 (0.0269) | [−0.0486, +0.0153] / [−0.0512, +0.0163] | n.d. |
| B5 comp recall @ comp P ≥ 0.90, arm-pooled OP (b 4.6 vs 3.0) | 0.8455 ± 0.0213 | 0.8392 ± 0.0071 | −0.0063 (0.0259) | −0.0064 (0.0262) | not computed | n.d. |
| B5 relR@2 @ relP@2 ≥ 0.90, arm-pooled OP (b 3.8 vs 2.2) | 0.8789 ± 0.0049 | 0.8737 ± 0.0101 | −0.0052 (0.0129) | −0.0062 (0.0130) | not computed | n.d. |
| E1 crack relF1@2 (106, one set) | 0.4279 ± 0.0163 | 0.4568 ± 0.0181 | **+0.0289 (0.0281)** | | [−0.0015, +0.0590] | **BETTER** |
| E1 any-hit comp recall (296 comps ≥ 20 px) | 0.4223 ± 0.0265 | 0.4358 ± 0.0598 | +0.0135 (0.0755) | | [−0.0489, +0.0795] | n.d. |

| guard | value (5-seed means) | seed-aware 95% interval (reported) | trip if | outcome |
|---|---|---|---|---|
| G1 inactive | test inactive IoU Δ −0.0198 (all 50) / −0.0207 (clean 49) | [−0.0486, +0.0153] / [−0.0510, +0.0154] | ≤ −0.015 in both sets | **TRIP** |
| G2 precision, test arm | test crack relP@2 Δ −0.0780 (all 50): 0.9441 → 0.8661 | [−0.2651, −0.0065], median −0.0204 | < −0.03 | **TRIP** |
| G2 precision, E1 arm | E1 crack px on the 74 crack-free cells 3,931 vs fresh SUPPF 4,211 = ×0.934; bar 6,316 px | not computed; ×0.89 … ×1.05 over the 71 cluster drops | > 1.5 × fresh SUPPF mean (ruling 1) | ok |
| **Verdict R** | 1 BETTER, 0 WORSE, G1 and G2 tripped | | | **FAIL** |

- **Reference line of ruling 1 (decides nothing):** the fixed s5-9 bar is 5,896 px; SKR01's 3,931 is below it too. (SKR01's fresh mean and the old s5-9 SUPPF mean both print as 3,931; a coincidence of rounding, different runs.)
- **Per seed (s10..s14):**
  - E1 relF1@2: SUPPF 0.4310 / 0.4136 / 0.4280 / 0.4531 / 0.4135; SKR01 0.4703 / 0.4312 / 0.4445 / 0.4728 / 0.4652.
  - E1 any-hit: SUPPF 0.4088 / 0.4595 / 0.3885 / 0.4223 / 0.4324; SKR01 0.5304 / 0.3919 / 0.3919 / 0.4054 / 0.4595.
  - test inactive IoU (all 50): SUPPF 0.4418 / 0.4831 / 0.4626 / 0.4938 / 0.4592; SKR01 0.4373 / 0.4413 / 0.4567 / 0.4578 / 0.4485.
  - test relP@2 (all 50): SUPPF 0.9464 / 0.9482 / 0.9401 / 0.9387 / 0.9470; SKR01 0.9252 / 0.9323 / 0.9272 / **0.6147** / 0.9310.
  - test crack IoU (all 50): SUPPF 0.4681 / 0.4711 / 0.4704 / 0.4718 / 0.4645; SKR01 0.4666 / 0.4715 / 0.4758 / **0.3427** / 0.4625. On the clean 49 SKR01 s13 is 0.4800.
  - E1 crack-free px: SUPPF 3,813 / 4,370 / 3,890 / 3,235 / 5,745; SKR01 4,539 / 6,076 / 3,359 / 2,465 / 3,216.
- **B5:** both arms reach the val OP on the wide grid (−8 … +12); the OPs equal those on the −4 … +12 sub-grid (the opening's `b5w_table.txt`).
- **The all-50 test crack rows are dominated by SKR01 s13 on the noisy cell.** That is why the all-50 thresholds are 0.066 and 0.090. On the clean 49 both test crack co-primaries are near 0 (+0.0021, +0.0012).

## 2. Verdict D: 5 primaries and 4 guards at the b 0 pair (E, `coach_v/coach_s2c_D.txt`)
E-SUPPF' = s2c_SUPPF_100pct_s10..14, E-SKR2' = s2c_SKR01_100pct_s10..14; mean softmax, both at b 0. 95% CIs, 2,000 resamples, seed 0. Test: paired image bootstrap. E1: 71-cluster bootstrap. Threshold for a primary: CI wholly above 0 (pass) or wholly below 0 (fail).

| primary | E-SUPPF' | E-SKR2' | Δ [CI] all 50 | Δ [CI] clean 49 | outcome |
|---|---|---|---|---|---|
| test crack IoU | 0.4872 | 0.4876 | +0.0004 [−0.0050, +0.0052] | +0.0016 [−0.0028, +0.0062] | n.d. |
| test crack relF1@2 | 0.9004 | 0.9012 | +0.0008 [−0.0035, +0.0047] | +0.0020 [−0.0013, +0.0055] | n.d. |
| test inactive IoU | 0.4746 | 0.4477 | −0.0269 [−0.0592, +0.0007] | −0.0283 [−0.0656, +0.0025] | n.d. |
| E1 crack relF1@2 (106 cells, 71 clusters) | 0.4385 | 0.4727 | **+0.0342 [+0.0115, +0.0544]** | | **pass** |
| E1 any-hit (114 → 124 of 296) | 0.3851 | 0.4189 | +0.0338 [0.0000, +0.0586] | | n.d. |

| guard | value at the b 0 pair | trip if | outcome |
|---|---|---|---|
| G2a | test relP@2 Δ −0.0133 (all 50): 0.9566 → 0.9434 | < −0.03 | ok |
| G2b | E1 crack px on the 74 crack-free cells 2,539 vs 2,925 = ×0.868; bar 4,388 px | > 1.5 × E-SUPPF' | ok |
| G1t | test inactive IoU Δ −0.0269 (all 50) / −0.0283 (clean 49) | ≤ −0.015 in both sets | **TRIP** |
| G1e | E1 inactive IoU Δ +0.0973, cluster CI [−0.0681, +0.2054] | CI wholly below 0 | ok |
| **Verdict D** | 1 primary passes, 0 fail, G1t tripped | | **FAIL** |

- **Three bounds sit within 0.002 of 0** (flagged; none changes the verdict):
  - **E1 any-hit lower bound is exactly 0.** Of the 2,000 draws 44 are below 0, 48 are exactly 0 and 1,908 are above; the 2.5th percentile falls on a 0. "Wholly above 0" needs a bound above 0, so it is not a pass; the frozen scorer reads it the same way. If a bound at 0 were counted as above, E1 any-hit would be a second passing primary; D would still be FAIL by G1t.
  - **Test inactive upper bound is +0.0007 on all 50** (+0.0025 on the clean 49). It is not wholly below 0, so the inactive primary does not fail. Had it failed, D would be FAIL by a primary and a guard, and the "inactive guard alone" wording would not apply.
  - Test relF1@2 lower bound on the clean 49 is −0.0013.
- **Second RNG stream:** the same outcome on every row (for example test inactive [−0.0586, +0.0038], E1 relF1@2 [+0.0109, +0.0554], E1 any-hit [0.0000, +0.0604]).
- **Fixed wording of §3b that would apply to a PASS** (volume line, "not replicated at ensemble level"): not triggered, D is FAIL. Per-image concentration line for the any-hit lines of D (§3b): the net +10 hits are 4 images up and 1 down, n_eff of the gain 2.6 images, all in scuff + half-cut cells; details in section 5.

## 3. Named claim, condition 1 (E, `coach_s2c_R.txt` R.5)
- **Registered form:** seed-aware two-stage bootstrap (71 E1 clusters, same draw for both arms; 5 runs drawn with replacement per arm), 2,000 draws, seed 0, the `coach_s2_boot.py` pattern.
  - E1 relF1@2 +0.0289, CI **[−0.0015, +0.0590]**, P(Δ > 0) 0.971.
  - Also from the same draws (reported): E1 relR@2 +0.0310 [+0.0027, +0.0586]; relP@2 +0.0236 [−0.0399, +0.0939]; any-hit +0.0135 [−0.0489, +0.0795]; inactive +0.0675 [−0.0827, +0.1763].
- **It is not a stream accident** (not the registered CI): with seeds 1 to 20 and 20261102 the lower bound runs from −0.0042 to −0.0005, above 0 in 0 of 21 streams. With 20,000 draws: [−0.0019, +0.0608].
- **Rule 1 and the seed-aware CI disagree here, both by a hair.** Rule 1 says BETTER by 0.0008; the seed-aware CI misses 0 by 0.0015.
  - §7 expected the seed-aware CI to be the easier test of the two (~1.96 SE against rule 1's ~2.58 SE). Here it was the harder one.
  - Reason: rule 1's threshold (0.0281) uses the seed spread only (sds 0.016 / 0.018); the CI also carries the cell noise from resampling the 71 clusters, and its half-width is about 0.030.

## 4. Comparison with the runner's readout and the opening's own outputs (E)
Runner's files: `results/s2c/local/` (md5 list OK) and `results/s2c/local_extra/`. Every difference found is listed; none changes a number that enters a verdict.

| item | runner / opening | mine | difference |
|---|---|---|---|
| Test co-primaries at tau 0 (`m2_rung_SKR01.txt` 1af55f6e) | means, sds, Δ, thr, labels, both sets | the same | none to 4 dp |
| E1 co-primaries (`e1_coprim.txt` 5662f36c) | +0.0289 (0.0281) BETTER; +0.0135 (0.0755) n.d.; per-seed values; strata | the same | none to 4 dp |
| B5 (`b5w_table.txt` ea62c4e6) | OPs 4.6 / 3.8 and 3.0 / 2.2; −0.0063 (0.0259), −0.0064 (0.0262), −0.0052 (0.0129), −0.0062 (0.0130); per-run OP −0.0042 / −0.0044 | the same | none to 4 dp |
| Guards (`guards.txt` 3f400c8d) | G1 −0.0198 / −0.0207 TRIP; G2 −0.0780, 3,931 vs 4,211 ×0.93 TRIP; reference bar 5,896 | the same | none; I print ×0.934 and the two G2 arms on separate lines |
| Named bootstrap (`named_boot.txt` d5ff89b8) | [−0.0015, +0.0590], condition 1 False; test rows | the same | none to 4 dp; P>0 printed with 2 dp there, 3 dp here |
| Verdict D (`d_boot.txt` e1241b78, `d_verdict.json` 4f27ff27) | FAIL, carrier E1 crack relF1@2, trip G1t; all estimates and CIs | the same | **0 to full float precision** (verdict pair and b_mv pair); guard names worded "delta" there, "d" here |
| D reported (concentration, strata, leave-one-out ranges, sweep, matched volume, singles vs ensemble) | | the same | none to the printed digits |
| LA tau 1 (`m2_rung_SKR01_tau1.txt` a834e424) | test rows | the same | none to 4 dp |
| Scuff-ignored test | `local/m2_rung_SKR01_scuffign.txt` is **empty** (0 bytes): the frozen script's `sed` built a wrong path and m2_rung stopped; the script marks that call "reported only" and went on. Redone with the ten paths written out: `local_extra/m2_rung_SKR01_scuffign.txt` 4fd12a6f | equal to `local_extra` | none to 4 dp. Reported-only item; the frozen script has a path bug |
| Paired image bootstrap of the 5-seed means (reported) | all 50: crack [−0.0557, +0.0047], relF1 [−0.0842, +0.0034], inactive [−0.0360, +0.0029]. Clean 49: crack [−0.0011, +0.0060], relF1 [−0.0014, +0.0042], inactive [−0.0384, +0.0029] | all 50 equal. Clean 49: crack [−0.0014, +0.0063], relF1 [−0.0014, +0.0043], inactive [−0.0384, +0.0064] | clean 49 differs in the 3rd to 4th decimal. Cause: my function carries one RNG across the two sets; m2_rung restarts seed 0 per set. With m2_rung's stream my intervals equal the runner's exactly (`coach_s2c_extra.txt` §7) |
| `opening_outputs.txt` 6495d0b7 | 19 collected files | each md5 tag and text equals the raw file | none |
| m2_rung "RUNG VERDICT: n.d." | Track M's test-only line | | **not verdict R**: it knows neither B5, E1 nor the guards. Verdict R is FAIL |
| `*.err` files | m2_rung: one numpy warning ("Mean of empty slice", the SDLE source row has 1 cell and no inactive); `d_boot.err`, `env_check.err` empty | | harmless |

- **What the runner did not compute:** verdict R, the named-claim tier, the §3c combination (note N4). The opening's E1 / B5 / guards / named-bootstrap passes are collected verbatim, not recomputed by the runner. The second computation of those is mine.

## 5. Reported items of §4 (never change a verdict)
### R (E, `coach_s2c_R.txt`, `coach_s2c_extra.txt`; the last three bullets from the opening's files)
- **B5 per run** (per-run val OP, all 50): comp recall −0.0042 (thr 0.0337), relR@2 −0.0044 (thr 0.0130); both n.d. At the val OP on E1 (descriptive): +0.0081 / +0.0051.
- **LA tau 1:** crack IoU −0.0414 / −0.0019, relF1@2 −0.0531 / +0.0003, inactive −0.0191 / −0.0201; all n.d. (thr 0.0966 / 0.0100, 0.1340 / 0.0100, 0.0249 / 0.0258).
- **Scuff-ignored test:** same as the verdict sets (crack −0.0255 / +0.0020; relF1@2 −0.0353 / +0.0012; inactive −0.0198 / −0.0207). 2 cells have px set to ignore (34 and 202 px); every other test cell is identical to the default m0.
- **Width, seed means (SUPPF → SKR01):**
  | | pred / GT crack px | relP@2 | relR@2 | pixel P | pixel R | any-hit | crack-free px |
  |---|---|---|---|---|---|---|---|
  | test (50) | 0.947 → 1.152 | 0.9441 → 0.8661 | 0.8422 → 0.8548 | 0.657 → 0.583 | 0.622 → 0.654 | 0.8974 → 0.9037 (189 comps) | 0 → 1 (2 cells) |
  | E1 (106) | 0.479 → 0.527 | 0.5126 → 0.5362 | 0.3686 → 0.3996 | 0.421 → 0.439 | 0.200 → 0.229 | 0.4223 → 0.4358 | 4,211 → 3,931 (74 cells) |
  - On the clean 49: test relP@2 0.9441 → 0.9322.
- **E1 strata (relF1@2; any-hit):**
  - scuff + half-cut (29): 0.368 → 0.392; 0.389 → 0.403 (274 comps);
  - half-cut without scuff (29): 0.811 → 0.815; 0.800 → 0.818 (11 comps);
  - full (48): 0.430 → 0.498; 0.873 → 0.873 (11 comps);
  - half-cut (58): 0.422 → 0.440; other (77): 0.517 → 0.565.
- **E1 inactive IoU** (not a co-primary here): 0.2255 → 0.2930, +0.0675 (rule-1 thr 0.1399).
- **Per source, test crack IoU (descriptive):** ARTS +0.027, BMRK +0.003, CFVS +0.002, CSIR −0.067 (the noisy cell; without it −0.003, from the runner's m2_rung table). Inactive: ARTS +0.036, BMRK −0.012, CFVS −0.033, CSIR −0.036.
- **Four test cell sets:** without twins crack −0.0287 / relF1@2 −0.0503 / inactive −0.0189; without both +0.0038 / +0.0025 / −0.0199; all n.d.
- **Seed-aware two-stage bootstrap of each test co-primary** (48 / 47 modules × seeds, seed 0):
  | readout | Δ | 95% interval | P(Δ > 0) |
  |---|---|---|---|
  | test crack IoU, all 50 | −0.0254 | [−0.1068, +0.0079] | 0.34 |
  | test crack IoU, clean 49 | +0.0021 | [−0.0055, +0.0096] | 0.72 |
  | test relF1@2, all 50 | −0.0351 | [−0.1633, +0.0068] | 0.31 |
  | test relF1@2, clean 49 | +0.0012 | [−0.0056, +0.0089] | 0.66 |
  | test inactive IoU, all 50 | −0.0198 | [−0.0486, +0.0153] | 0.10 |
  | test inactive IoU, clean 49 | −0.0207 | [−0.0512, +0.0163] | 0.12 |
- **10-seed view, single means s5-14 ("5 of 10 seeds opened before"; descriptive):**
  | readout | s5-9 Δ | s10-14 Δ | s5-14 Δ |
  |---|---|---|---|
  | test crack IoU, all 50 | +0.0091 | −0.0254 | −0.0082 |
  | test crack IoU, clean 49 | +0.0088 | +0.0021 | +0.0055 |
  | test relF1@2, all 50 | +0.0089 | −0.0351 | −0.0131 |
  | test inactive IoU, all 50 | +0.0099 | −0.0198 | −0.0049 |
  | E1 relF1@2 | +0.0364 | +0.0289 | +0.0327 |
  | E1 any-hit | +0.0439 | +0.0135 | +0.0287 |
  | E1 crack-free px | −112 | −280 | −196 |
  | E1 inactive IoU | +0.0022 | +0.0675 | +0.0349 |
- **Cell-level** = the opening's cell-gate line (`cellgate/s2_cellgate.txt` a93078b6; **not recomputed by me**). UNSTABLE THRESHOLD, reported only, never evidence for or against a gate: the val-chosen t per run is SUPPF 7.44 / −6.88 / 8.69 / 7.34 / 4.81, SKR01 7.22 / −0.84 / 7.66 / 7.75 / 8.16. Ungated → gated at b 0: SKR01 E1 crack-free px 3,931 → 3,506 (SUPPF 4,211 → 3,604); E1 any-hit 0.4358 → 0.4196; test relP@2 0.8661 → 0.8678.
- **20k encoder cosines** (`enc_cosine_20k.txt` b5336e4f; not recomputed by me): layer3 0.927 to 0.930 in both arms; layer4 SKR01 0.930 to 0.951, SUPPF 0.933 to 0.944.
- **Thin-term magnitudes: missing.** "Reported-only item of section 4 not produced: no frozen grep pattern existed; no verdict depends on it" (ruling 3). No training stdout was opened for it.

### D (E, `coach_s2c_D.txt`)
- **Val decisions (val only, reported):**
  - E-SUPPF' D2 b 1.25 (the max-relF1@2 branch; val relR@2 there 0.8971); crack-precision drop +0.0615; width flag ON.
  - E-SKR2' D2 b 0.75 (relR@2 0.9007, relP@2 0.9100); drop +0.0381; flag off.
  - b_mv **−0.45**: val crack pred / GT of E-SKR2' 0.9909 against E-SUPPF' 0.9865 at b 0 (E-SKR2' at b 0 has 1.1070; the next nearest b is −0.50 with 0.9779).
  - Re-derived by me from the stored sweep and grid, and re-summed from the val cells of the three files: equal.
- **Matched val volume: E-SKR2' at b_mv −0.45 vs E-SUPPF' at b 0** (reported, not a verdict):
  | readout | Δ [CI] all 50 | Δ [CI] clean 49 |
  |---|---|---|
  | test crack IoU | −0.0077 [−0.0137, −0.0029] | −0.0075 [−0.0134, −0.0030] |
  | test relF1@2 | −0.0056 [−0.0133, −0.0002] | −0.0055 [−0.0130, −0.0001] |
  | test inactive IoU | −0.0290 [−0.0611, −0.0007] | −0.0307 [−0.0672, +0.0001] |
  | E1 relF1@2 | +0.0133 [−0.0106, +0.0463] | |
  | E1 any-hit (114 → 110) | −0.0135 [−0.0459, +0.0088] | |
  - Test relP@2 −0.0012; E1 crack-free px 1,638 vs 2,925 (×0.56); E1 inactive +0.0957 [−0.0717, +0.2032].
  - At matched val volume E-SKR2' is below E-SUPPF' on both test crack readouts, with CIs below 0, and not above it on E1.
- **E1 aggregate sweep (−1.5 … 3; E1-oracle, chooses nothing):** E-SKR2' has the higher relF1@2 at every equal b (+0.016 … +0.042; +0.034 at b 0) and fewer crack-free px at every b ≤ 0.75 (from b 1.0 to 1.75 it has slightly more).
- **E1 matched volume:** E-SUPPF' reaches E-SKR2''s b 0 pred / GT (0.440) at b 0.215. There relF1@2 Δ is +0.0342 → **+0.0290** (bias share 15%); any-hit Δ is +0.0338 → **+0.0135** (bias share 60%); crack-free px 2,539 vs 3,383.
- **any-hit concentration (the per-image line):**
  - GT: 296 comps in 21 of 71 images; top 3 images 57%, top 10 94%, n_eff 7.1; 274 comps in the 29 scuff + half-cut cells.
  - The net +10 hits: 4 images up (CSIR_01717 +6, CSIR_01679 +3, CSIR_02222 +1, CSIR_01637 +1), 1 down (CSIR_01647 −1); n_eff of the gain 2.6 images.
  - All of it is in scuff + half-cut cells (95 → 105 of 274); the other 77 cells score 19 / 22 in both.
  - Without the top-3 comp images: any-hit +0.0000, relF1@2 +0.0318.
- **Leave-one-cluster-out (71), point estimates:** relF1@2 [+0.0281, +0.0373]; any-hit [+0.0177, +0.0386]; E1 inactive [+0.0582, +0.1333].
- **E1 inactive:** 9,158 GT px in 7 images, top 3 hold 87%, n_eff 3.3. Without them the Δ is +0.0525.
- **E1 strata (relF1@2):** scuff + half-cut 0.351 → 0.388; half-cut without scuff 0.875 → 0.842; full 0.485 → 0.560; other 77 0.577 → 0.623.
- **Width:**
  | | test pred / GT | test P / R | test relP / relR | E1 pred / GT | E1 relP / relR | crack-free px test / E1 / val |
  |---|---|---|---|---|---|---|
  | E-SUPPF' b 0 | 0.939 | 0.677 / 0.635 | 0.957 / 0.850 | 0.398 | 0.560 / 0.361 | 0 / 2,925 / 0 |
  | E-SKR2' b 0 | 1.032 | 0.645 / 0.666 | 0.943 / 0.863 | 0.440 | 0.594 / 0.393 | 0 / 2,539 / 26 |
  | E-SKR2' b −0.45 | 0.931 | 0.672 / 0.626 | 0.955 / 0.841 | 0.342 | 0.632 / 0.352 | 0 / 1,638 / 4 |
- **Four test sets (b 0 pair):** without twins crack +0.0011 [−0.0052, +0.0074], inactive −0.0193 [−0.0357, +0.0086]; without both +0.0028 [−0.0022, +0.0088], −0.0204 [−0.0375, +0.0092]. **test_noscuff:** same as test (+0.0003 / +0.0008 / −0.0269).
- **Per source, test crack IoU:** ARTS 0.449 → 0.477, BMRK 0.398 → 0.401, CFVS 0.547 → 0.550, CSIR 0.426 → 0.412. Inactive: CFVS 0.582 → 0.537, BMRK 0.383 → 0.361.
- **Singles vs ensemble (descriptive):**
  - test crack IoU: E-SUPPF' 0.4872 vs singles 0.4692 ± 0.0030; E-SKR2' 0.4876 vs 0.4438 ± 0.0568 (clean 49: 0.4920 vs 0.4744 ± 0.0058).
  - E1 relF1@2: 0.4385 vs 0.4279; 0.4727 vs 0.4568.
  - E1 any-hit: both ensembles are below their single means (0.3851 vs 0.4223; 0.4189 vs 0.4358).
  - The ensemble averages out s13's flood of the noisy cell: E-SKR2' predicts 348 crack px there, E-SUPPF' 0.
- **#6 row for reference (s5-9 ensembles at b 0, opened):** test crack IoU +0.0102, relF1@2 +0.0104, inactive +0.0050; E1 relF1@2 +0.0353, any-hit +0.0676, E1 inactive −0.0418; G2a −0.0110; G2b ×1.06.
- **FINAL** (cv02, R34 5-seed ensemble, b +0.75) clean-test crack IoU 0.492, descriptive only: E-SKR2' clean 0.4920, E-SUPPF' 0.4904.
- **Missing D items:** none.

## 6. Fragility (E, `coach_s2c_R.txt`, `coach_s2c_D.txt`, `coach_s2c_extra.txt`)
- **Verdict R:**
  | check | result |
  |---|---|
  | leave-one-seed-out (10 drops, rule 1 /3 on 4 v 5) | FAIL in 10 of 10 |
  | G1 over the seed drops | trips in 9 of 10; Δ all 50 from −0.0263 to −0.0133 |
  | G2 over the seed drops | trips in 9 of 10; relP@2 Δ −0.0946 … −0.0151; not without SKR01 s13 |
  | G1 over the 48 module drops | trips in 47; not without CFVS_00114 |
  | G2 over the 48 module drops | trips in 47; not without CSIR_00070 |
  | seed-aware two-stage bootstrap (seed 0) | G1 trips in 62% of draws, G2's relP arm in 46%, either in 81% |
  | test inactive co-primary | WORSE in 1 of 10 seed drops (without SUPPF s10); n.d. in the other 9 and in all 48 module drops |
- **R's BETTER label on E1 relF1@2** is as fragile as at #5:
  - margin 0.0008;
  - leave-one-seed-out keeps BETTER in **3 of 10** drops (Δ stays +0.025 … +0.035 in all 10);
  - leave-one-cluster-out keeps it in **63 of 71** (n.d. without CSIR_00303, 00341, 00345, 00394, 01637, 01647, 01717 or 02222).
  - It does not carry verdict R, which is FAIL.
- **Named-claim condition 1:**
  - CI above 0 in 2 of 10 seed drops (without SUPPF s13 or SKR01 s11);
  - CI above 0 in 1 of 71 cluster drops (without CSIR_00305: [+0.0005, +0.0612]).
  - The miss is as close as the label's hit.
- **Verdict D:**
  | check | result |
  |---|---|
  | G1t over the 50 image drops | trips in 50 of 50; Δ all 50 from −0.0321 to −0.0165 |
  | G1t in the image bootstrap (seed 0) | trips in 83% of draws |
  | test inactive primary over the image drops | turns to "fail" (CI wholly below 0) in 2 of 50 (without BMRK_00788_cell1622 or CFVS_00027_r4_c4) |
  | E1 relF1@2 pass over the 71 cluster drops | CI above 0 in 71 of 71; lower bound +0.0046 … +0.0161 |
  | E1 any-hit over the 71 cluster drops | CI above 0 in 1 of 71 (without CSIR_01647) |
  | G2a, G2b under leave-one-out | no trip in any drop (−0.0149 … −0.0101; ×0.79 … ×1.02) |
- **Where the test inactive loss sits:**
  - 92,125 GT inactive px in 16 of 50 cells; top 3 cells 59%, n_eff 7.2 cells.
  - Singles: per-cell IoU down in 8 of 16, median change −0.0001. True positives 56,111 → 55,236 px; inactive predicted on other GT 27,793 → 31,053 px. So it is mostly extra false inactive, not lost inactive.
  - Without the top-3 inactive cells: singles −0.0103 / −0.0117; ensembles −0.0309 / −0.0361.
  - Ensembles: down in 6 of 16 cells; the largest single drop is CFVS_00042_r8_c4, 0.716 → 0.420.
- **The same readout on the two other sets leans the other way:**
  - val (not sealed): singles inactive +0.0123 (thr 0.0949), ensembles +0.0440;
  - E1: singles +0.0675, ensembles +0.0973 [−0.068, +0.205].

## 7. What this opening shows and does not show
### Shows (E)
- **With fresh seeds neither reading passes.** R and D both FAIL on guards that were registered before any SKR2C number existed. By §3c and §7 the SUP100-PF ensemble stays and the Skeleton Recall route closes for the deployable at w 0.1.
- **The test crack leans of #5 (n.d. by rule 1) and passes of #6 (fixed-model CIs) did not repeat.**
  - Singles, clean 49: +0.0021 (was +0.0088). Ensembles: +0.0004 / +0.0016 with CIs across 0 (was +0.0102 / +0.0101 with CIs above 0).
  - At matched val volume E-SKR2' is below E-SUPPF' on test crack IoU (−0.0077, CI below 0; a reported item, fixed-model CI, seed noise not included).
  - §5 expected a test-crack pass at b 0 as "likely, and likely mostly volume". It did not come.
- **The test inactive sign flipped between seed sets.** s5-9: singles +0.0099, ensembles +0.0050. s10-14: singles −0.0198, ensembles −0.0269. Both fresh readings fall on the wrong side of the −0.015 bar.
- **On the same 106 E1 cells the E1 relF1@2 difference came back at about the same size (seed-level only; not new-panel evidence).**
  - Singles +0.0289 (s5-9: +0.0364); ensembles +0.0342 (s5-9: +0.0353).
  - For this ensemble pair it is a curve shift, not volume (E1-oracle sweep, descriptive): +0.0290 at matched E1 volume, above E-SUPPF' at every b of the sweep, with fewer false-alarm px on crack-free cells (×0.93 singles, ×0.87 ensembles).
  - The registered claim fails two of its three conditions: the seed-aware CI misses 0 by 0.0015, and R and D are both FAIL. A CI above 0 would not have made it hold. The fixed wording is "replication at recipe level not shown".
- **E1 any-hit shrank:** singles +0.0135 n.d. (s5-9 +0.0439); ensembles +0.0338 with the lower bound at 0 (s5-9 +0.0676). It is 10 components in about 3 effective images, 60% of it volume.
- **One of five fresh SKR01 models fails badly on one odd cell** (49,713 false crack px on the noisy cell). No s5-9 run of either arm did (0 to 303 px, opened files). The ensemble averages it out. That is 1 of 10 SKR01 runs against 0 of 10 SUPPF runs over s5-14; it does not separate the recipe from run-to-run chance.

### Does not show (S)
- **Not new-panel evidence, in either direction.** These are the same 50 test and 106 E1 cells for the 3rd time. Fresh seeds remove seed luck, not cell luck (§1). The failures are as cell-bound as the earlier passes.
- **Not that Skeleton Recall harms inactive in general.**
  - The loss is on test only; val and E1 lean positive.
  - It sits in 16 cells (n_eff 7.2). The seed-aware interval is [−0.049, +0.015], P(Δ < 0) 0.90.
  - Two seed sets give opposite signs; 10 seeds pooled give −0.0049.
  - G1's registered null false-FAIL rate is 9 to 15%, D's G1t 8%, about 15% combined. Both inactive guards tripped; they share the 10 models and the test cells, so under a true null the chance of both is no more than D's ~8%. Against that, the route has now met an inactive guard at three openings (#5, #6, #7), so the chance of at least one trip under a true null is above one opening's ~15%. This outcome is what such a false FAIL would look like. It is also what a small real cost would look like. The data cannot tell them apart, and the consequence was fixed in advance for exactly this case.
- **Not a general precision loss from G2's trip.** It is one run on one cell; on the clean 49 the relP@2 Δ is −0.0119; on E1 relP@2 rises (+0.024) and false-alarm px fall. What it does show: a single model can fail badly on one odd cell. That this is specific to Skeleton Recall is not shown (1 of 10 runs against 0 of 10). A small test relP@2 lean of about −0.012 is there on the clean 49 and in the ensemble pair (G2a −0.0133), as at #5 (−0.0121) and #6 (−0.0110): inside the −0.03 bar, same cells. G2 has no usable stated null rate for a one-run event: S2 §3c's 'null trip ~0' assumed a relP@2 seed sd of 0.0015.
- **Not that the E1 relF1@2 effect is refuted.** "Not shown" is the registered wording. §5 put the chance of the named claim holding at 25 to 45% even if the effect is real, and called "replication not shown" the likeliest honest outcome.
- **Multiplicity (S):** the single BETTER label sits among 7 co-primaries at a margin of 0.0008; §3a puts the family-wise false-BETTER rate at ≤ ~10%. It supports no claim on its own.
- **Not claimable:** "SKR2 replicated", "E1 gain confirmed", "SKR2 hurts inactive", "SKR2 loses precision".
- **Claimable:** "On fresh seeds, on the same 50 test and 106 E1 cells as #5 / #6 (3rd look), SKR w 0.1 failed protocol_SKR2C on the test inactive guards (singles and ensembles) and on the test relP@2 guard (one run, one cell). The E1 relF1@2 difference appeared again in the ensemble pair (+0.034, fixed-model CI above 0); replication at recipe level was not shown. SUP100-PF stays."
- **Next step is the user's.** No unopened test-like set exists for these models. A fourth look at the same cells cannot settle either open point.

## 8. Disclosures
1. **Val-only values seen early.** While listing JSON keys before my recompute I saw two val-only values of D: E-SKR2''s reported D2 b (0.75) and b_mv (−0.45, also in a file name). No test or E1 number of this opening was read before my R and D outputs were on disk (`MD5_first`, 04:56:53).
2. **`coach_s2c_extra.py` was written after I saw the verdicts.** It holds reported and fragility lines only (per-seed guard values, the noisy cell, leave-outs, bootstrap shares, comparison aids). Nothing in it feeds a verdict.
3. **Four wrong expectations in my integrity script** (section "Integrity"); corrected before the kept run.
4. **A cosmetic slip in my output:** the last line of `coach_s2c_combine.txt` prints "carried by" next to FAIL. Read it as "BETTER co-primary / passing primary". The script is left at the md5 that produced the first outputs.
5. **Same interpreter** for the runner's readout and my recompute (section "Inputs").
6. **Reported items taken from the opening's files, not recomputed by me:** the cell-gate line and the encoder cosines.
7. **No GPU, no inference, no write outside** `verify_skr2c.md`, `scripts/coach/coach_s2c*.py`, `results/s2c/coach_v/` and one line in `log.md`. No process of mine is left running; no tmux session was started.
8. **m2_rung run by me once**, on opened #5 files only, piped to `md5sum`, to check the gaint-Python claim. It is not part of my recompute.

## 9. Checks requested of judge
- Verdicts R and D from the per-cell files, and the two wording readings (the lower tier of the named claim; the G1-alone sentence).
- E1 any-hit's lower bound of exactly 0: is "not a pass" the right reading of "wholly above 0"?
- The G2 trip: is "one run, one cell; stands as registered" stated fairly?
- Section 7's "does not show" list.

## 10. Proposed registry lines (for the lead; I did not edit either file)
**`e1_openings.md`, row 7** (cells "registered", "opened", "result file"; the first four cells stay):
> | 7 | protocol_SKR2C (v1 LOCKED 3 Nov 02:37, md5 91b76abd) | s2c_SKR01_100pct_s10..14 (el_thin c9bbb02) vs s2c_SUPPF_100pct_s10..14 (el_f3 e544133); singles (R, rule 1) and 5-member ensembles at a shared b 0 (D) | R: E1 crack relF1@2 + any-hit (rule 1, S2 set); D: E1 crack relF1@2 + any-hit (71-cluster bootstrap), G2b / G1e at b 0; named claim: seed-aware two-stage bootstrap of E1 relF1@2 (10 fresh singles) + D pass + no FAIL; reported: strata, width, E1 sweep, b_mv | v1 LOCKED 3 Nov 02:37 (judge SIGNED 5995fcd5, 47f8e6f0); opening set FROZEN 14 Nov 00:13 (836be7e5, 27 files) | **opened 14 Nov 2026 00:22:45-03:54:57** (gaint, `s2c_opening.sh`, 's2c opening done: R rc=0 D rc=0'; R scoring 02:23-03:36 after the GPU gate wait, D 03:36-03:54 CPU fp32; post MANIFEST bb6dffea, d_out MANIFEST 648ff42b) | `verify_skr2c.md` (coach, 14 Nov; judge pending). Same 106 E1 cells as #5 / #6, 3rd look. **R FAIL** by G1 (test inactive IoU −0.0198 / −0.0207) and G2 (test relP@2 −0.0780 on all 50: one run on the noisy cell); E1 crack relF1@2 +0.0289 (thr 0.0281) BETTER by rule 1, any-hit +0.0135 n.d., G2's E1 arm ×0.93 ok. **D FAIL** by G1t alone (test inactive −0.0269 / −0.0283; null false-FAIL ~8%); E1 crack relF1@2 +0.0342 [+0.0115, +0.0544] passes, any-hit +0.0338 [0.0000, +0.0586] does not (net +10 hits, n_eff 2.6 images, all in scuff + half-cut cells), G2b ×0.87 ok, G1e ok (+0.097 [−0.068, +0.205]). Named claim: REPLICATED does not hold (seed-aware CI [−0.0015, +0.0590]); "the fresh-seed ensemble pair differs on E1 relF1@2 (fixed-model CI; seed noise not included); replication at recipe level not shown". The SUP100-PF ensemble stays |

**`team_2026-11-12_frontier/benchmark/test_openings.md`, row 18** (moves from section D to the counted openings, which become 18):
> | 18 | SKR2C (= E1 opening 7) | SKR01 v SUPPF, fresh seeds 10 to 14, gaint; singles (R) and two 5-member ensembles at a shared b 0 (D) | R: the SKR2_HC2 set at argmax (three + two operating-point readouts; guards on test inactive and relP@2). D: the SKR2E set at b 0 (three; guards on relP@2 and test inactive) | 14 Nov 00:22 to 03:54 | Third look at the same 50 cells for this contrast. R: all five test co-primaries n.d. (crack IoU −0.0254 on all 50, +0.0021 on the clean 49; inactive −0.0198 / −0.0207); guards on test inactive and relP@2 (−0.0780, one run on the noisy cell) trip: R FAIL. D: crack IoU +0.0004 [−0.0050, +0.0052], relF1@2 +0.0008 [−0.0035, +0.0047], inactive −0.0269 [−0.0592, +0.0007], no primary passes or fails; guard on test inactive trips (−0.0269 / −0.0283): D FAIL (`team_2026-10-31_next/verify_skr2c.md`) |

## Judge (14 Nov 2026, 05:28 IST)
judge, adversarial check of everything above, read at md5 **79c226e31bc2d26f46f6a3ec498fe580** (344 lines; `md5sum` at 05:12, 05:23 and again just before this append). Nothing above this heading was edited by me. Tags: E (measured, with the file), S (judgement). "Same cells" as above: the 3rd look at the same 50 test and 106 E1 cells.

### Finding
| item | coach | judge |
|---|---|---|
| Verdict R | FAIL, by G1 and G2 | **CONFIRMED WITH FIXES** (fixes 1, 2, 9, 11, 13; wording only) |
| Verdict D | FAIL, by G1t alone | **CONFIRMED WITH FIXES** (fix 5; wording only) |
| Combination (§3c) | the SUP100-PF ensemble stays | **CONFIRMED** |
| Named claim (§3a) | REPLICATED does not hold; lower-tier sentence | **CONFIRMED WITH FIXES** (fixes 3, 4, 8; wording only) |

- Every deciding number equals mine to 4 dp (E, table below).
- I found no reading of the protocol text under which a verdict, the combination or the named claim changes (E, "Other readings").
- 14 wording fixes at the end. None changes a number.

### How I checked (E)
- **Own code**, numpy only; it imports nothing from the coach, the runner, the frozen set or Track M:
  - `scripts/judge/judge_s2c.py` 79766f9b: inputs, the 5 co-primaries that come from the m0 files, R's guards, the named-claim bootstrap, verdict D, the leave-outs behind ruling (d), the guards under other readings.
  - `scripts/judge/judge_s2c_b5.py` de47549e: the 2 B5 co-primaries from `rec_w`. Its OP and rule-1 functions are copied from the judge's own `judge/s2_b5w.py` 67f03055 (opening #5); that file's descriptive E1 width part is left out.
  - Outputs: `results/s2c/judge_v/judge_s2c_out.txt` 51af7ec0, `judge_s2c_b5_out.txt` 8ae0804f; both `.err` files are empty. Two runs of `judge_s2c.py` gave sections 0 to 4 byte for byte.
- **Not blind.** The task order had me read this verify first. My scripts were written afterwards (05:15 to 05:24), knowing the coach's numbers. They check stated numbers. They are not a third blind recompute.
- **Draw order of the named-claim bootstrap:** read (not imported) from `results/s2/coach_v/diag/coach_s2_boot.py` 7ea26cfb, the pattern §3a names: one `default_rng(0)`; per draw the 71 clusters, then 5 SUPPF runs, then 5 SKR01 runs.
- **Same limits as the coach:** the per-cell files are the opening's inference outputs; B5 starts from `rec_w`; same interpreter (gaint venv). No GPU, no inference. Of sections 5 and 6 I recomputed only the lines named below.

### Recomputed numbers (E, `judge_v/judge_s2c_out.txt`, `judge_s2c_b5_out.txt`)
| quantity | judge | coach | equal to 4 dp |
|---|---|---|---|
| R, G1: test inactive IoU Δ, all 50 / clean 49 | −0.019765 / −0.020695 | −0.0198 / −0.0207 | yes |
| R, G2: test relP@2 Δ, all 50 | −0.077998 (0.9441 → 0.8661) | −0.0780 | yes |
| R, G2: E1 crack-free px, SKR01 vs fresh SUPPF | 3,931.0 vs 4,210.6 = ×0.9336; bar 6,315.9 px | 3,931 vs 4,211, ×0.934; bar 6,316 px | yes |
| R, E1 relF1@2 Δ and rule-1 threshold | +0.028949, thr 0.028121, BETTER; margin +0.000828 | +0.0289 (0.0281) BETTER; margin 0.0008 | yes |
| R, E1 any-hit | +0.0135 (0.0755) n.d. | the same | yes |
| R, test crack IoU, all 50 / clean 49 | −0.0254 (0.0656) / +0.0021 (0.0100) n.d. | the same | yes |
| R, test relF1@2 | −0.0351 (0.0898) / +0.0012 (0.0100) n.d. | the same | yes |
| R, test inactive IoU | −0.0198 (0.0259) / −0.0207 (0.0269) n.d. | the same | yes |
| R, B5 comp recall, arm-pooled OP b 4.6 vs 3.0 | −0.0063 (0.0259) / −0.0064 (0.0262) n.d. | the same | yes |
| R, B5 relR@2, arm-pooled OP b 3.8 vs 2.2 | −0.0052 (0.0129) / −0.0062 (0.0130) n.d. | the same | yes |
| Named claim, condition 1 (seed 0) | +0.0289 [−0.001467, +0.059028], P(Δ > 0) 0.9705 | [−0.0015, +0.0590], 0.971 | yes |
| the same, seeds 1 to 20 and 20261102 | lower bound −0.0042 … −0.0005; above 0 in 0 of 21 | the same | yes |
| D, G1t: test inactive IoU Δ, all 50 / clean 49 | −0.026877 / −0.028322 | −0.0269 / −0.0283 | yes |
| D, E1 relF1@2 Δ, 71-cluster CI | +0.0342 [+0.011509, +0.054423] pass | +0.0342 [+0.0115, +0.0544] pass | yes |
| D, E1 any-hit Δ, 71-cluster CI | +0.0338 [0.000000, +0.058565]; draws 44 below 0, 48 exactly 0, 1,908 above | [0.0000, +0.0586]; 44 / 48 / 1,908 | yes |
| D, test inactive IoU Δ, CI, all 50 / clean 49 | −0.0269 [−0.0592, +0.0007] / −0.0283 [−0.0656, +0.0025] n.d. | the same | yes |
| D, test crack IoU | +0.0004 [−0.0050, +0.0052] / +0.0016 [−0.0028, +0.0062] n.d. | the same | yes |
| D, test relF1@2 | +0.0008 [−0.0035, +0.0047] / +0.0020 [−0.0013, +0.0055] n.d. | the same | yes |
| D, G2a | −0.0133 (0.9566 → 0.9434) ok | the same | yes |
| D, G2b | 2,539 vs 2,925 = ×0.8680; bar 4,387.5 px ok | ×0.868; bar 4,388 px | yes |
| D, G1e | +0.0973 [−0.0681, +0.2054] ok | the same | yes |

- **Verdicts from these numbers:** R = 1 BETTER, 0 WORSE, 6 n.d., G1 and G2 tripped: FAIL. D = 1 primary passes, 0 fail, G1t tripped: FAIL.
- **Lines behind ruling (d)** (E, section 4 of my output; equal to the coach's):
  - noisy cell, predicted crack px per run: SUPPF 2 / 0 / 0 / 0 / 2; SKR01 926 / 203 / 0 / 49,713 / 0; GT 787; E-SUPPF' 0, E-SKR2' 348.
  - SKR01 s13: 34.4% of its test crack px on that cell; relP@2 0.6147 (all 50), 0.9361 (clean 49).
  - relP@2 Δ: clean 49 −0.0119; all 50 without SKR01 s13 −0.0151.
  - Seed drops: G1 trips in 9 of 10 (not without SUPPF s13: −0.0133 / −0.0139); G2 in 9 of 10 (not without SKR01 s13); at least one guard trips in 10 of 10.
  - Opened s5-9 files, same cell: SUPPF 220 / 227 / 2 / 29 / 0; SKR01 0 / 167 / 303 / 0 / 0. So "0 to 303 px" holds.
- **A rounding coincidence, not a mix-up:** SKR01's fresh E1 crack-free mean (19,655 / 5 = 3,931.0) and the old SUPPF s5-9 mean of ruling 1 (19,653 / 5 = 3,930.6) both print as 3,931.

### Other readings of the text (E for the numbers, S for which reading is registered)
| rule | protocol text | other reading | outcome under it |
|---|---|---|---|
| rule-1 labels | §3a "5 v 5, rule 1 /3" | none in the text | R is FAIL by guards whatever the labels are |
| two-set rule | §3a names the two sets only. House form (`team_2026-10-29_features/review_spec_cp5_v1.md` l.7): "pass on both, or on one with a same-sign n.d. on the other; worse on either fails" | a label from one set alone | all 5 test co-primaries are n.d. in each set on its own; no label under any form |
| G1 | "test inactive IoU Δ ≤ −0.015 in both sets"; "seed means" (S2 §3c: "5-seed means") | counts pooled over the seeds | −0.0195 / −0.0204: trips |
| G2, test arm | "test crack relP@2 Δ < −0.03 (all 50)" | counts pooled over the seeds: −0.1007. Clean 49 or 4 seeds is not a reading: the set is named | trips |
| G2, E1 arm | "> 1.5 × SUPPF's"; ruling 1: the fresh mean | fixed s5-9 bar 5,896 px | ok under both |
| verdict R | "FAIL: any WORSE, or any guard tripped" | none | FAIL |
| D pass rule | "the CI is wholly above 0" | a bound of exactly 0 counts as above | E1 any-hit becomes a 2nd passing primary; D stays FAIL |
| D "seed 0" | "2,000, seed 0" | another stream | the coach's second stream moves no label. The one bound a stream could move is test inactive's upper end (+0.0007; 55 of 2,000 draws above 0). Below 0, D would be FAIL by a primary and a guard, and the "inactive guard alone" sentence would go. Verdict the same |
| G2a | §3b "test relP@2 Δ < −0.03" (no set named; frozen scorer and SKR2E: all 50) | clean 49: −0.0101 | ok under both |
| G1t, G2b, G1e | point estimates as written | none | G1t trips; the others do not |
| §3c | "R FAIL or D FAIL → the SUP100-PF ensemble stays" | every branch except "R PASS and D PASS" keeps SUP100-PF | stays |
| §3c false-FAIL sentence | "If an inactive guard alone caused it, the line carries its null false-FAIL" | per verdict (the frozen D scorer; §7 for R), or for the combined outcome | per verdict: D's line carries it, R's does not. Combined: G2 is also a cause, so no line carries it. Wording only |
| named-claim lower tier | ruling (a) | | wording only |
| §7 "G1 alone" | ruling (b) | | wording only |

### Rulings on the coach's four points
- **(a) "If only D's ensemble CI passes": reading (i) is the registered one. The lower-tier sentence is stated.** (S)
  - Text: §3a lists three conditions for REPLICATED, then "**If only D's ensemble CI passes:** ...". §3a Multiplicity: "A D-only E1 pass, read as a recipe claim, would be ~8-9% (judge M3). That is why it gets the lower-tier wording."
  - Origin (`judge/review_SKR2C_v09.md` M3, l.46-51): the upper tier "needs all of" the seed-aware CI, the D primary and "the verdict is not FAIL"; then "If only the ensemble CI passes". The contrast is between the two CIs. The not-FAIL condition belongs to the upper tier only.
  - So "only" ranges over the two CIs: D's fixed-model CI passes and the seed-aware CI does not. That is this case.
  - Under (ii) no fixed sentence exists; the sentence is still true as a statement (E). Under both, REPLICATED does not hold.
  - Condition: the sentence is not a pass. It is always quoted next to "D FAIL by G1t" (fix 3, fix 4).
- **(b) §7's "G1 alone" sentence does not attach to R's line.** (S)
  - Text: §7 "**If G1 alone caused it:** the line carries 'G1 null false-FAIL ~9-15% (S2 W1); with D's G1t ~8%, ~15% combined that a true null closes the route through an inactive guard alone'."
  - G2 also tripped, so the condition is not met. The quoted sentence would also be false of this FAIL: the route did not close through an inactive guard alone.
  - §3c's sentence is applied per verdict (the frozen `s2c_d_boot.py` prints it iff only G1t / G1e tripped and no primary failed), so D's line carries it. Correct as written.
  - The coach's counterfactual ("Without G2, R would still be FAIL, by G1 alone ...") may stay: it is marked S and kept out of R's line and the handbook line.
- **(c) E1 any-hit with a lower bound of exactly 0 is not a pass.** (E / S)
  - Text: §3b "**Pass:** the CI is wholly above 0." An interval whose lower end is 0 contains 0.
  - The frozen scorer, fixed before any number, reads it strictly: `s2c_d_boot.py` 164ef377 l.203, `lo[i] > 0`; the runner's `d_verdict.json` names E1 crack relF1@2 as the only carrier. The fail side is the mirror (`hi < 0`).
  - In substance: 92 of 2,000 draws (4.6%) are at or below 0, more than the 2.5% tail.
  - Under the other reading D stays FAIL by G1t, and no fixed wording changes.
- **(d) "G2 is one run on one cell; the trip stands as registered" is fair. The trip stands. One sentence overstates (fix 1).** (E / S)
  - The facts hold (lines above).
  - **The protocol gives no ground to set the run or the cell aside:**
    - §3a: "**G2:** test crack relP@2 Δ < −0.03 (all 50)". The set is named. G1 beside it says "in both sets"; G2 does not.
    - S2 §3c, which §3a cites for the guards: "pre-registered FAIL rules; any trip FAILS that arm, whatever else passes", on seed means.
    - The only rule on replacing a run is §2b (a stopped run is rerun). s13 was not stopped: step 20000, rc 0, no autostop trigger.
  - **Overstated:** "So it is the model, not one bad pass." The five passes share the weights, the code path and GPU bf16. They show that the result repeats under the registered scoring, not that it holds at another precision. D gate (a) has s13 at CPU fp32 within 0.0013 of bf16, on val only.
  - **G2 has no usable stated null rate for this event (S).** S2 §3c calibrated "Null trip ~0" on a test relP@2 seed sd of 0.0015. Here the sd is 0.1406 for SKR01 (0.0043 for SUPPF). So the trip is neither "impossible under a null, hence a recipe effect" nor something to discount.
  - One flood in 10 SKR01 runs (s5-14) against 0 in 10 SUPPF runs does not separate the recipe from chance (fix 9).

### Integrity (E, own commands)
- **The real lists were scored.**
  - `el_f3/data/splits/test.txt` a31fad14 (50), `val.txt` 9dcccf00 (54), `ext117/stems_eval.txt` 5266806b (106).
  - The stems of the 10 m0 JSONs, the 20 B5 `rec_w` val / test files and the 2 D b 0 files equal these lists (asserted in my scripts).
  - The training root's `test.txt` is the val list (9dcccf00) and shares 0 stems with the real test list.
  - The opening's own asserts: 11 PASS, 116 "-> True", 0 False; D PASS.
- **Exactly the 10 fresh runs.**
  - Run names inside the m0 JSONs are s2c_SUPPF / s2c_SKR01 _100pct_s10..14, step 20000, revisions e544133 / c9bbb02; `m0/` holds no other run. tau 0 cells equal the default cells in all 10.
  - D members are the same 10. `latest.pth` md5s now equal `member_latest_md5.txt` and `init_check.txt`, 10 of 10; file times 3 Nov 04:45 to 11:24.
  - Exactly 10 `s2c_*` run dirs over both trees, no `*_STOPPED_*`. `launch.log`: "S2C ALL TRAINED (10 rc 0 of 10)". `autostop.log`: start and end lines only.
- **No threshold or set changed after the numbers existed.**
  - gaint `open/FROZEN.md5` 836be7e5; `md5sum -c` 27 OK now; every file read-only; newest file time 14 Nov 00:00, before the 00:22:45 start; `opening.log` records the same check at the start.
  - Bars in the frozen code equal the protocol: `s2c_guards.py` l.38 (−0.015, −0.03, 1.5); `s2c_d_boot.py` l.203 and l.212-215.
  - `protocol_SKR2C.md` sections 0 to 8 equal the judge's lock copy 91b76abd (empty diff). Rulings file time 13 Nov 17:12. Registry lines 14 Nov 00:13.
  - MANIFESTs bb6dffea (353 OK) and 648ff42b (14 OK), at the source and at the copy.
- **Code written after the numbers existed** (all disclosed above; none sets a bar or a set):
  - the gaint readout wrapper 1f43dc6f (04:37:48). Diff read: transport, Python, two md5 pins, stderr. The D scorer it calls is the frozen 164ef377. It holds no R verdict.
  - `coach_s2c_extra.py` (05:03:40). It reads `coach_s2c_R.json`; `coach_s2c.py` (04:55:32) does not import or read it; `coach_s2c_R.txt`, `_D.txt`, `_combine.txt` still have the md5s of `MD5_first` (bb7f3fc4, aa2c73f4, bc5939f2; file times 04:56). **It feeds no verdict.**
  - `coach_s2c_integrity.py` has the same file time 05:03:40. I did not diff the coach's "comment-only" edit. It feeds no verdict.
  - my own two scripts (see "Not blind").
- **Not checked by me:** the 73 lines of `coach_v/integrity.txt` one by one; the module and cluster leave-outs; the b_mv and sweep items; the cell-gate and cosine lines.

### Section 7, "shows and does not show" (S)
- **Balanced on the main points.** It claims no replication, no inactive harm and no precision loss, and it says the result is cell-bound.
- **Overstated, three places:**
  - "The E1 relF1@2 gain came back": a seed-level statement on the same 106 cells. The cell luck is shared by all three looks. Say so in the sentence (fix 8).
  - "The registered seed-aware claim missed by 0.0015" reads as a near miss. The claim also fails condition 3 outright (fix 8).
  - "it is the model" (fix 1); "a single SKR01 model can fail badly" (fix 9).
- **Understated, two places:**
  - Both inactive guards tripped. Under a true null the chance of both is no more than D's ~8%; "~15%" is the chance of either (fix 10).
  - A small test relP@2 lean of about −0.012 has shown at every look (#5 −0.0121, #6 −0.0110, now −0.0119 on the clean 49 and −0.0133 for the ensembles): inside the bar, same cells (fix 11).
- **Third look and the point-estimate guards (S, rough; my number, not for the tables):** the route has met an inactive guard at three openings: #5 (G1, ok at +0.0099), #6 (G1t, ok at +0.0050), #7 (both trip). With the stated null rates, and #5 / #6 sharing their models, the chance that a true null trips at least once over them is roughly 25 to 30%, not 15%. This bears on how to read the trip, not on the verdict: each opening's rule was fixed before its numbers.
- **§1's rule "Every result line says 'same cells as #5 / #6'":** the "Claimable" sentence, the one most likely to be copied out, lacks it (fix 12).
- **§3b's rule "Every any-hit line carries the per-image concentration line":** the any-hit lines of sections 2 and 10 point to section 5 instead of carrying it (fix 5).

### Wording fixes (none changes a number)
1. Verdicts, G2 bullet. Replace "So it is the model, not one bad pass. All five are GPU bf16; fp32 on test was not run." with "So it repeats under the opening's GPU bf16 scoring; it is not one bad pass. The five passes share the weights and bf16, and fp32 on test was not run, so it is not shown at another precision (on val, D gate (a) has s13 at CPU fp32 within 0.0013 of bf16)."
2. Verdicts. Replace "**G1 holds in 9 of 10 seed drops and 47 of 48 module drops.**" with "**G1 trips in 9 of 10 seed drops and 47 of 48 module drops.**" ("holds" can be read as "is ok").
3. Named claim, reading note. Replace "I do not pick one." with "Judge rules (i): the lower-tier sentence is stated. It is not a pass and is always quoted next to 'D FAIL by G1t'."
4. Handbook line. Replace "E1 relF1@2: R's rule-1 label BETTER (+0.0289, thr 0.0281);" with "E1 relF1@2: the named claim REPLICATED does not hold (seed-aware CI [−0.0015, +0.0590]; R and D both FAIL); R's rule-1 label BETTER (+0.0289, thr 0.0281; margin 0.0008);".
5. Section 2. Replace "Every any-hit line carries the per-image concentration line: section 5." with "Per-image concentration line for the any-hit lines of D (§3b): the net +10 hits are 4 images up and 1 down, n_eff of the gain 2.6 images, all in scuff + half-cut cells; details in section 5." In section 10, `e1_openings.md` line, replace "any-hit +0.0338 [0.0000, +0.0586] does not" with "any-hit +0.0338 [0.0000, +0.0586] does not (net +10 hits, n_eff 2.6 images, all in scuff + half-cut cells)".
6. Section 7, Shows. Replace "**The test crack gains of #5 / #6 did not repeat.**" with "**The test crack leans of #5 (n.d. by rule 1) and passes of #6 (fixed-model CIs) did not repeat.**"
7. Section 7, Shows. Replace "(−0.0077, CI below 0)." with "(−0.0077, CI below 0; a reported item, fixed-model CI, seed noise not included)."
8. Section 7, Shows, E1 bullet. Three replacements:
   - "**The E1 relF1@2 gain came back at about the same size.**" becomes "**On the same 106 E1 cells the E1 relF1@2 difference came back at about the same size (seed-level only; not new-panel evidence).**"
   - "It is a curve shift, not volume:" becomes "For this ensemble pair it is a curve shift, not volume (E1-oracle sweep, descriptive):"
   - "The registered seed-aware claim missed by 0.0015, so the fixed wording is" becomes "The registered claim fails two of its three conditions: the seed-aware CI misses 0 by 0.0015, and R and D are both FAIL. A CI above 0 would not have made it hold. The fixed wording is"
9. Section 7. After "No s5-9 run of either arm did (0 to 303 px, opened files). The ensemble averages it out." add "That is 1 of 10 SKR01 runs against 0 of 10 SUPPF runs over s5-14; it does not separate the recipe from run-to-run chance." Replace "What it does show: a single SKR01 model can fail badly on one odd cell." with "What it does show: a single model can fail badly on one odd cell. That this is specific to Skeleton Recall is not shown (1 of 10 runs against 0 of 10)."
10. Section 7, Does not show, inactive bullet. After "about 15% combined." add "Both inactive guards tripped; they share the 10 models and the test cells, so under a true null the chance of both is no more than D's ~8%. Against that, the route has now met an inactive guard at three openings (#5, #6, #7), so the chance of at least one trip under a true null is above one opening's ~15%."
11. Section 7, Does not show, G2 bullet. Add at its end "A small test relP@2 lean of about −0.012 is there on the clean 49 and in the ensemble pair (G2a −0.0133), as at #5 (−0.0121) and #6 (−0.0110): inside the −0.03 bar, same cells. G2 has no usable stated null rate for a one-run event: S2 §3c's 'null trip ~0' assumed a relP@2 seed sd of 0.0015."
12. Section 7, Claimable. Replace "On fresh seeds SKR w 0.1 failed protocol_SKR2C" with "On fresh seeds, on the same 50 test and 106 E1 cells as #5 / #6 (3rd look), SKR w 0.1 failed protocol_SKR2C".
13. Section 1, reference line. After "SKR01's 3,931 is below it too." add "(SKR01's fresh mean and the old s5-9 SUPPF mean both print as 3,931; a coincidence of rounding, different runs.)"
14. Header. Replace "judge has not checked it yet." with "judge's check is the last section (CONFIRMED WITH FIXES)."

### What would change a verdict
- **Nothing found.** R is FAIL by G1 alone and by G2 alone; D is FAIL by G1t; every branch of §3c except a double PASS keeps SUP100-PF; the named claim fails condition 3 whatever the seed-aware CI does.
- **Nearest edges, none of which moves a verdict** (E):
  - D's test inactive upper bound +0.0007: below 0 it would add a failing primary and remove the "inactive guard alone" sentence.
  - E1 any-hit lower bound exactly 0: above 0 it would add a passing primary.
  - Named-claim condition 1 lower bound −0.0015; R's BETTER margin +0.0008.
  - G1 without SUPPF s13 (−0.0133 / −0.0139): G2 still trips in that drop.
- **Not settled by this check:** whether SKR01 s13 floods the noisy cell at fp32. No inference was allowed here. The registered R scoring is GPU bf16, so the verdict does not depend on it.
- No GPU, no inference, nothing written under `/home/noob/work`. No process of mine is left running. I did not edit `e1_openings.md` or the benchmark registry.

## Fixes applied (team-lead, 14 Nov 2026, 05:50 IST)
The judge's 14 wording fixes (list above) were applied to the coach's sections by the lead with exact string replacement, each old string found exactly once. No number, threshold or verdict changed. File as the judge left it: md5 757a3b1e (copy `results/s2c/judge_v/verify_skr2c_before_fixes_757a3b1e.md`). The judge's section is unchanged.
