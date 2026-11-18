
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
