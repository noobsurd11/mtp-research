# coach verify: protocol_PF2E (E-PF vs E-g, 5-member mean-softmax ensembles of PF2's seeds 5-9; inference only, gaint CPU fp32)

coach, 1 Nov 2026 19:18 IST. Independent recompute. Tags: E (file), S (judgement).
- **Inputs:** runner's pull `results/pf2e/raw/` (MANIFEST 532305e0, `md5sum -c` OK; = gaint `el_f3/reports/pf2e/out`). Run 19:02:04-19:13:10, rc 0 (`run.log`), `pf2e_infer.py` 272463d3 (as APPROVED). Members: latest.pth md5s re-read by coach on gaint, equal to `member_latest_md5.txt`: SUP s5-9 02f70aa3 / 25ae6cbf / 59de8607 / 7558407c / d24bbdc0; SUPPF s5-9 79802bb7 / cffdc5dc / 17bb85ca / 89521560 / 4dc95532 (step 20000, REVISION e544133 asserted by the script).
- **Code:** my own `scripts/coach/coach_pf2e.py` dc0d484f (own metrics; paired image bootstrap and 71-cluster module bootstrap with my own RNG, so CIs differ from runner's in the 3rd decimal by design). Output `results/pf2e/coach_v/pf2e_coach.txt`.
- **vs runner's `results/pf2e/pf2e_boot_runner.txt` (b1417347; pf2e_boot bee9e182): CONFIRMED.** All point estimates equal to 4 dp; the val decisions re-derived; every verdict the same.

## Order of events (the verdict b)
- protocol_PF2E §2 said "the verdict uses the chosen b"; the approved scorer said "headline b". judge flagged it. **Clarified 19:04:56 IST** (headline b = D2-chosen b, or 0 if it trips the val width flag), while `out/` was empty (checked 19:04:45 and after writing). **`pf2e_val_decisions.json` was written 19:05:49** (gaint mtime), test / E1 files 19:13:09. No PF2E number existed when the rule was fixed.

## Val decisions (E; re-derived by coach from the stored sweep; sweep entries at the scored b recomputed from the val cells: equal)
- E-g: D2 b **1.25** (val relR@2 0.9018, relP@2 0.9003); val crack precision drop +0.0543 > 0.05 → **headline b 0**.
- E-PF: D2 b **1.5** (val relR@2 0.9089, relP@2 0.9011); drop +0.0753 → **headline b 0**.
- So the **verdict is at b 0 for both** (argmax ensembles). Gate repeated in the real run: s5 alone within 0.0004 of the PF2 opening (CPU fp32 vs GPU bf16).

## Verdict (protocol_PF2E §3)
1. **Test (all 50 / clean 49), paired image bootstrap: n.d.** No primary's CI excludes 0; none lies below 0.
   | primary | E-g | E-PF | Δ all 50 [runner CI] [coach CI] | Δ clean 49 |
   |---|---|---|---|---|
   | crack IoU | 0.4788 | 0.4815 | +0.0027 [−0.0146, +0.0159] [−0.0138, +0.0148] | +0.0027 |
   | crack relF1@2 | 0.8821 | 0.8942 | **+0.0121** [−0.0048, +0.0309] [−0.0037, +0.0296], P>0 0.92 | +0.0121 |
   | inactive IoU | 0.4376 | 0.4613 | +0.0237 [−0.0310, +0.0971] [−0.0317, +0.0995] | +0.0245 |
2. **E1 co-primaries (106 cells, 71 module clusters), module-cluster bootstrap: PASS on E1 inactive IoU.**
   | co-primary | E-g | E-PF | Δ [runner CI] [coach CI] |
   |---|---|---|---|
   | E1 crack relF1@2 | 0.3990 | 0.4345 | +0.0355 [−0.0232, +0.0912] [−0.0270, +0.0897] n.d. |
   | **E1 inactive IoU** | 0.0665 | 0.2807 | **+0.2141 [+0.0303, +0.3820] [+0.0357, +0.3893]**, P>0 0.99 |
3. **PF2E: PASS (E1 inactive IoU co-primary); test n.d.; no primary FAIL.** Wording (S, revised with judge's qualifications, below): "As the deployable 5-member ensemble at argmax, PF makes far fewer false inactive calls on module-edge pixels of E1 edge cells and doubles E1 inactive recall (IoU 0.067 → 0.281; module-cluster CI above 0, borderline under a Bonferroni correction); on test it repeats the singles' relF1@2 gain (+0.012), CI includes 0." Not "a broad unseen-panel inactive capability": E1 inactive GT is 10 cells in 7 source images.

## Robustness and caveats (E / S)
- **E1 is not an independent replication:** the members are PF2's seeds 5-9, whose single-model E1 numbers were opened at E1 opening #1 (inactive +0.189). The ensemble result restates that gain for the deployable object; it adds a cluster-level CI (cell selection) to PF2's seed-level rule. The E1 cluster key (stem minus `_rN_cM` / `_cellN` = source image, 71) is an assumption: judge's b6_audit found cross-image twins only in CFVS, none in CSIR (train / val); not checked on E1 (no E1 image read for it).
- **E1 crack precision falls under PF:** crack P 0.547 → 0.495, relP@2 0.626 → 0.588; recall 0.160 → 0.189, relR@2 0.293 → 0.345; component recall 0.159 → 0.209. Crack px on the 74 crack-free E1 cells 2,138 → 2,528. Val crack-free px 87 → 0; test crack-free 0 / 0.
- **E1 strata (runner's readout, descriptive):** scuff + half-cut 29: inactive 0.360 → 0.637, crack R 0.088 → 0.127; other 77: inactive 0.023 → 0.131, crack R 0.376 → 0.376; half-cut 58 inactive 0.326 → 0.593; full 48 inactive 0.024 → 0.130.
- **Ensemble vs singles (descriptive):** E-g test crack IoU 0.4788 vs single mean 0.4662; relF1@2 0.8821 vs 0.8730. E-PF test relF1@2 0.8942.
- **Test without the 7 D6 twins (reported):** crack IoU −0.0060, relF1@2 +0.0170, inactive +0.0212 (all n.d.).
- **At the D2-chosen b (reported, not the verdict b; width flag tripped):** E-g b 1.25 / E-PF b 1.5: test crack IoU 0.4849 / 0.4888 (clean 0.4880 / 0.4920), relF1@2 0.8917 / 0.9078, inactive 0.4427 / 0.4680; E1 crack IoU 0.1839 / 0.2020, relF1@2 0.4442 / 0.4733, inactive 0.0672 / 0.2874; test crack precision 0.602 / 0.584 (vs 0.666 / 0.670 at b 0), the cost the width flag guards against.
- **FINAL (cv02, R34 5-seed, b +0.75) clean-test crack IoU 0.492:** descriptive only (other machine, commits, bias). E-PF at the verdict b 0: 0.4846; at its D2 b 1.5: 0.4920.
- **Scuff-ignored test (descriptive):** same pattern (relF1@2 +0.0121 / +0.0122, n.d.).
- **B5 operating points + cell-level (reported):** frozen extra pass `pf2e_b5.sh` 4e7bd28e (APPROVED 19:17), pending; addendum when pulled.

## Qualifications (judge, appended below; coach re-checked the main ones from the per-cell files, E)
- E1 inactive GT: **9,158 px in 10 cells, 7 source images, n_eff 3.3** (coach: same).
- E-g false inactive px on E1: **32,654**, mostly on GT class 5 (15,993), 0, 4 and 21, in CSIR_00394 / 00391 / 00395 (16,670 / 8,390 / 6,555); E-PF **11,315** (CSIR_00394 5,644, 00395 3,417). Inactive TP 2,782 → 5,746 (**recall 0.304 → 0.627**). So about half of the IoU gain is fewer false inactive calls on module-edge px of edge cells, half is recall (coach: same).
- judge (not re-run by coach): leave-one-cluster-out Δ range [+0.138, +0.277]; with consecutive-id CSIR families as clusters (37 or 16) the lower bound stays > 0 (+0.023 / +0.024); a Bonferroni-99% lower bound is ~0.000 (borderline under correction).
- These qualifications go with the result into anything for the user or the handbook.

## What this decides (S)
- On test the PF ensemble is worse on no primary (all three point estimates positive, none significant); on E1 inactive it is clearly better. **Recommendation (S) for the deployable model: E-PF (PF recipe) is the better candidate than the house recipe; its operating point by the D2 rule on val is argmax here.** The width flag tripped for both arms at the D2 b, so the headline stays at argmax; whether the D2 grid or the width threshold should change is a separate, pre-registered question, not a re-pick here.

## judge: adversarial check (2026-11-01 19:20 IST; verify_pf2e as of md5 60ff1f85; raw MANIFEST 532305e0, md5sum -c OK)
**Verdict: CONFIRMED, with qualifications.** PF2E PASSes on the E1 inactive IoU co-primary; test is n.d.; no FAIL.

Code: `judge/pf2e_check.py` 83401571. It is my own code: it imports nothing from Track M and has its own counts, primaries and resamplers. Output: `judge/out/pf2e_check_out.txt`. Laptop only.

**The four points team-lead asked for (E):**
1. **The D2 bias was chosen on val only.**
   - I re-derived D2 from the stored val sweep: E-g b 1.25 (relR@2 0.902 / relP@2 0.900), precision drop +0.0543. E-PF b 1.5 (0.909 / 0.901), drop +0.0753. Both are flagged, so headline b = 0 for both. This equals the decisions file (md5 40538419).
   - The sweep entries at every stored b, re-summed from the val cells, match with |Δ| = 0.
   - The val loop finished before the test / E1 loops in one process (`run_full.log`: "val decisions written" before "test done").
2. **Members are exactly seeds 5-9.**
   - All four E-*.json files list `pf2_{SUP,SUPPF}_100pct_s5..9`, step 20000, e544133.
   - The decisions meta carries script 272463d3 and m_common 10f0d37c.
   - The latest.pth md5s are as recorded by coach. I did not re-read them on gaint.
3. **No number was chosen after seeing test or E1.**
   - Order: the "headline b" clarification at 19:04:56 (out/ empty); `pf2e_val_decisions.json` mtime 19:05:49; test / E1 files 19:13:09.
   - The verdict b follows from the val file alone. The script refuses a second pass.
   - Nothing was re-picked after the flag tripped. The D2-b rows are reported only.
4. **E1 module-cluster bootstrap.**
   - My own resampler (2,000, seed 0, cluster draws via `default_rng(0).integers`) gives the same CIs as runner's to 4 dp: test relF1@2 +0.0121 [−0.0048, +0.0309]; E1 inactive +0.2141 [+0.0303, +0.3820]; E1 relF1@2 +0.0355 [−0.0232, +0.0912].
   - Identical arms give 0.
   - There are 71 clusters.

**What the E1 inactive pass rests on (E; this changes the wording, not the verdict):**
- **Tiny ground truth.** E1 inactive GT is 9,158 px in 10 cells across 7 clusters. The top-3 clusters hold 87%; effective n = 3.3.
- **The gain has two parts, about half and half:**
  - Detection: TP 2,782 → 5,746 (recall 0.304 → 0.627; half-cut 1,928 → 3,946 of 5,494; full 854 → 1,800 of 3,664).
  - False alarms removed: E-g calls 32,326 inactive px on 9 cells with no inactive GT. About 31k of these sit in three consecutive CSIR images (00391, 00394, 00395), on module-border / frame-edge / ribbon GT px of edge cells. E-PF calls 9,998.
  - Giving E-g E-PF's false-alarm count alone lifts its IoU 0.067 → 0.143.
  - So "PF lifts E1 inactive IoU +0.21" = PF finds twice the (little) inactive, **and** stops the house ensemble calling dark module edges inactive.
- **Robustness:**
  - Leave-one-cluster-out keeps Δ inactive in [+0.138, +0.277].
  - Merging consecutive-id CSIR images into families (the cluster key's main weakness: 37 or 16 clusters instead of 71) keeps the LB > 0: [+0.023, +0.296] and [+0.024, +0.287].
  - **Multiplicity:** the 5 co-primaries are uncorrected, as pre-registered. With a Bonferroni 99% CI the LB is ≈ 0.000 (0.55% of resamples ≤ 0), so the pass is borderline under correction. Disclose it.

**Other (E, coach's numbers re-computed, all equal):**
- E1 crack P 0.547 → 0.495, relP@2 0.626 → 0.588, relR@2 0.293 → 0.345, comp R 0.159 → 0.209.
- E1 crack-free px 2,138 → 2,528 (+18%); val 87 → 0.
- Test without the 7 D6 twins: −0.0060 / +0.0170 / +0.0212.
- D2-b rows: E-PF clean test crack IoU 0.4920 at b 1.5 (flagged), 0.4846 at b 0.

**Reading (S):**
- The pass is real but narrow in what it rests on. Call it "fewer false inactive calls on module edges plus twice the inactive recall, on 10 E1 cells / 7 images". It is not a broad unseen-panel inactive capability.
- It is also not an independent replication: the same models and E1 cells as opening #1.
- I agree with coach's recommendation that E-PF is the better deployable candidate than E-g, on the evidence of no test loss, the relF1@2 sign repeated, and the E1 inactive effect. Put next to it, for the user:
  - on E1 the PF ensemble buys crack recall with crack precision (P −0.05, relP@2 −0.04, crack-free px +18%);
  - test gives no significant gain on any primary;
  - E-PF's 0.4920 "matching FINAL" appears only at a b the pre-registered width flag rejected, so it is not a claim.

## Addendum: B5 operating points + cell-level (protocol_PF2E §4, reported only; coach 2026-11-01 19:39 IST)
- Frozen extra pass `pf2e_b5.sh` 4e7bd28e (calib_dump c172717e group ensembles, el_metrics 6e73ff11), gaint CPU fp32, 19:27-19:36:49, rc 0; **b = 0 self-check vs PF2E's own E-*.b0.json PASS at tol EXACT for all 6** (no cpu fallback). Pull `results/pf2e/b5/` (MANIFEST 03e8fc82, md5sum -c OK). Disclosed: the out_b5 copy kept the rec files and lost the test / ext summaries (same file names as the records; cp refused to overwrite), so those summaries are on gaint only (`el_f3/reports/pf2e/b5_work/sum/`); test_clean summaries are local.
- **Recomputed by coach from the raw records (own code, `scripts/coach/coach_thin.py` curves / OP rule; = calib's test_clean summaries exactly: b 1.1 / 1.2 and 1.5 / 1.5, compR 0.8396 / 0.8717, relR 0.8729 / 0.9107):**

  | | E-g | E-PF | Δ |
  |---|---|---|---|
  | val OP b_comp / b_rel | 1.1 / 1.2 | 1.5 / 1.5 | |
  | test comp recall @ comp P ≥ 0.90 (compP) | 0.8307 (0.914) | 0.8624 (0.915) | +0.032 |
  | test relR@2 @ relP@2 ≥ 0.90 (relP) | 0.8655 (0.919) | 0.9035 (0.912) | +0.038 |
  | clean comp recall / relR@2 | 0.8396 / 0.8729 | 0.8717 / 0.9107 | +0.032 / +0.038 |
  | E1 comp recall / relR@2 at the val OP (descriptive) | 0.253 / 0.400 | 0.378 / 0.498 | +0.125 / +0.098 |
  | E1 comp P / relP@2 at the val OP | 0.495 / 0.498 | 0.397 / 0.451 | |
- Speck guard at OP-comp (test): all-size comp precision 0.757 → 0.678, speck share 0.0080 → 0.0069. Cell-level at b 0 (test_clean, calib): recall 0.936 both, FA rate 0 both, AUROC 0.968 → 1.000.
- Reading (S): at matched val precision (0.90), the PF ensemble recovers more crack on test (+0.03 to +0.04), the same direction as PF2's singles (relR@2 at relP ≥ 0.90 +0.034); one ensemble per arm, so no rule-1 test here. On E1 precision at the val OP is far below 0.90 for both (domain shift).
