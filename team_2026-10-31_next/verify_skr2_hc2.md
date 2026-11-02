# coach verify: protocol_SKR2_HC2 v1.1 opening (SKR2 and HC2 vs SUP100-PF, seeds 5-9; 100% labels, gaint); E1 opening #5

coach (respawned session), 2 Nov 2026, first written ~21:38 IST (header first typed as 22:05 by hand; corrected 21:49 from `date`). Independent recompute. Tags: E (file), S (judgement).

## Verdicts
- **SKR2 (Skeleton Recall w 0.1): PASS.** One co-primary BETTER (E1 crack relF1@2 +0.0364, thr 0.0351), none WORSE, G1 and G2 not tripped. Every test co-primary and both B5 co-primaries are n.d.
  - **The BETTER label is fragile** (judge, E): margin 0.0013; leave-one-seed-out keeps BETTER in 5 of 10 drops (own check: 5 / 10), leave-one-E1-image-out in 65 of 71.
  - **The effect is robust:** seed-aware P(Δ > 0) 0.985; Δ stays +0.025 … +0.042 in every seed drop; it is not a bias shift (Reading).
- **HC2 (synthetic half-cuts p 0.35, inactive → ignore in synthetic views): FAIL**, by **G1** (test inactive IoU −0.0256 / −0.0259; bar ≤ −0.015 in both sets). No co-primary BETTER or WORSE. G3 passed. **Mechanism FAILED** (relP@2 ≥ 0.90 unreachable on SHV1, so no matched recall exists). The cause is the ignore label, not a loss of crack recall (see Mechanism).

## Inputs and code
- **Runs (E, `results/s2/coach_v/integrity.txt`):** 10 runs trained rc 0 (SKR2 14:03-16:39, HC2 17:00-19:59), each with `config OK ... seed K + <arm> change only`. My own config diff vs pf2_SUPPF_100pct_s5 is seed plus:
  - SKR2: `skel_recall.weight 0.1`;
  - HC2: `synth_halfcut {p 0.35, pool synth_halfcut_pool_ap.tsv}` + `synth_halfcut_ignore_inactive: true`.
- **Per stdout (grep -c only):** 1 header, step 20000/20000, 0 Tracebacks, 400 PF lr lines.
- **Deploys:** HEAD = REVISION, 0 tracked changes (el_thin c9bbb02, el_hc2 0405151).
- **GPU:** gpumem min free 2,078 MiB at 12:18:28 (the near-miss runner already disclosed; the floor held).
- **Opening:**
  - s2_post with **FROZEN fb5becd2**, the v1.1 stage-2 freeze (= local `results/s2_FROZEN_v11.md5`). Started 20:01:46 (post_settings.txt); `s2q scoring done: post rc=0` at 21:23:18.
  - Decision passes rc 0: hc2_synth_inactive, e1_coprim, b5w, shv1, f51, guards. Extras rc 0: enc_cosine, cellgate, scuffign.
  - tau0 == default cells; step 20000 and the arm's code_revision for all 10.
  - Comparator MANIFESTs unchanged: PF2 3827f7c0, HC d5c39e0d, THIN 5d3f5b31.
- **Where I recomputed (disclosed):**
  - gaint CPU (nice 19, 8 threads, CUDA hidden). My predecessor armed it at 14:36; it fired at 21:24 on 's2q scoring done'.
  - It read the opening in place after `md5sum -c` of the S2 post MANIFEST **bd671e26** (490 files), PF2 3827f7c0, HC d5c39e0d, and the HC and S2 syn dumps (30 + 30).
  - Text outputs: `results/s2/coach_v/` and `results/s2/coach_v/diag/`, each with an MD5 file.
- **Code (coach's own):**
  - wrapper `coach_verify_s2_gaint.sh` 8073d957;
  - test co-primaries: `coach_verify.py` b0456b28 (two sets, tau 0 / 1, paired image bootstrap);
  - `scripts/coach/coach_s2.py` **a95649de**: E1 co-primaries; B5 on the wide grid (own curves and OP); G1-G3; F51 (own AP and RNG); SHV1 pooled.
  - Self-test PASS before any S2 number was read. It reproduces:
    - SUPPF 0.4202 / 0.3811 / 0.2371 and HC 0.4338 / 0.377 / 0.2369;
    - SKR w 1.0 any-hit 0.523; crack-free px 3,931;
    - G1 / G2 for HC / SKR / CLD (= judge's);
    - B5 for SKR / CLD (= verify_thin_b3);
    - F51 HC +0.0669.
  - Extras after the opening (reported only; `results/s2/coach_v/diag/`):
    - `coach_s2_boot.py` 7ea26cfb: seed-aware two-stage bootstrap (48 test modules / 71 E1 images, plus seeds; 2,000 draws; RNG 20261102);
    - `coach_s2_shv1diag.py` e3cf58fc;
    - `coach_s2_inact.py` 3c9874e3;
    - scuff-ignored test through coach_verify.
- **Cross-checks:**
  - **vs the opening's own decision outputs** (gaint `s2q/post`, read-only): e1_coprim, guards, b5w_table, shv1_readout and f51 all equal mine to 4 dp. Only the F51 bootstrap bounds differ, by RNG.
  - **vs runner's pull and local readout: CONFIRMED** (2 Nov ~21:43; first typed as 22:2x, corrected).
    - Pull `results/s2/raw/`: MANIFEST bd671e26 (490 files), md5sum -c OK on the laptop. The decision files I cross-checked (e1_coprim, guards, shv1_readout, f51, b5w_table) are byte-identical to gaint's.
    - Readout: `s2_post_local.sh` 0ec30d37 → `results/s2/local/` (local_md5.txt OK). The m2_rung test rows equal my coach_verify to 4 dp: means, sds, Δ, thresholds and verdicts in both sets, plus the paired image-bootstrap intervals. Files: SKR01 e0de918a / tau 1 f7c5bc23, HC2 38a7cb4b / tau 1 de00917f, HC2 vs HC 8018b54c (descriptive).
    - runner did not recompute the opening's E1 / B5 / guards / SHV1 / F51 passes (opening_outputs.txt 11ebe685 collects them verbatim). The second computation of those is mine; judge's is the third.

## Co-primaries (§3: rule 1 /3, 5 v 5; test co-primaries by the two-set rule)
### SKR2 (7 co-primaries)
| co-primary | SUPPF | SKR2 | Δ (thr) all 50 | Δ (thr) clean 49 | result |
|---|---|---|---|---|---|
| test crack IoU | 0.4651 | 0.4741 | +0.0091 (0.0100) | +0.0088 (0.0100) | n.d. |
| test crack relF1@2 | 0.8847 | 0.8936 | +0.0089 (0.0100) | +0.0085 (0.0100) | n.d. |
| test inactive IoU | 0.4557 | 0.4656 | +0.0099 (0.0272) | +0.0102 (0.0285) | n.d. |
| B5 comp recall @ comp P ≥ 0.90, arm-pooled OP (b 4.8 vs 3.9) | 0.8212 | 0.8381 | +0.0169 (0.0290) | +0.0171 (0.0293) | n.d. |
| B5 relR@2 @ relP@2 ≥ 0.90, arm-pooled OP (b 2.7 vs 3.9) | 0.8723 | 0.8818 | +0.0094 (0.0177) | +0.0094 (0.0177) | n.d. |
| E1 crack relF1@2 (106, one set) | 0.4202 ± 0.0272 | 0.4567 ± 0.0135 | **+0.0364 (0.0351)** | | **BETTER** |
| E1 any-hit comp recall (296 comps ≥ 20 px) | 0.3811 ± 0.0320 | 0.4250 ± 0.0318 | +0.0439 (0.0521) | | n.d. |
| **Verdict** | | | | | **PASS** |
- **B5:** both arms reach the val OP on the wide grid (−8 … +12). The OPs equal those on the −4 … +12 sub-grid (self-check). SUPPF's wide-grid OPs equal its frozen ones (b_comp 3.9, b_rel 3.9).
- **E1 per seed:**
  - relF1@2: SUPPF 0.443 / 0.428 / 0.440 / 0.414 / 0.376; SKR2 0.465 / 0.459 / 0.435 / 0.469 / 0.456.
  - any-hit: SUPPF 0.399 / 0.355 / 0.429 / 0.365 / 0.358; SKR2 0.466 / 0.429 / 0.409 / 0.439 / 0.382.

### HC2 (5 co-primaries)
| co-primary | SUPPF | HC2 | Δ (thr) all 50 | Δ (thr) clean 49 | result |
|---|---|---|---|---|---|
| test crack IoU | 0.4651 | 0.4684 | +0.0033 (0.0100) | +0.0064 (0.0100) | n.d. |
| test crack relF1@2 | 0.8847 | 0.8816 | −0.0032 (0.0119) | +0.0006 (0.0100) | n.d. |
| test inactive IoU | 0.4557 | 0.4301 | −0.0256 (0.0277) | −0.0259 (0.0279) | n.d. |
| E1 crack relF1@2 (106, one set) | 0.4202 ± 0.0272 | 0.4276 ± 0.0317 | +0.0074 (0.0483) | | n.d. |
| E1 inactive IoU (106, one set) | 0.2371 ± 0.0271 | 0.1575 ± 0.0666 | −0.0795 (0.0830) | | n.d. |
| **Verdict** | | | | | **FAIL (G1)** |
- E1 inactive per seed, HC2: 0.179 / 0.184 / 0.043 / 0.216 / 0.165.

### Guards (§3c; any trip fails the arm)
| guard | arm | value (5-seed means) | trip if | result |
|---|---|---|---|---|
| G1 inactive | SKR2 | test inactive IoU Δ +0.0099 / +0.0102 | ≤ −0.015 in both sets | ok |
| G1 inactive | HC2 | test inactive IoU Δ −0.0256 / −0.0259 | ≤ −0.015 in both sets | **TRIP** |
| G2 precision | SKR2 | test relP@2 Δ −0.0121 (all 50); E1 crack px on 74 crack-free cells 3,819 vs 3,931 = ×0.97 | < −0.03, or > ×1.5 | ok (both) |
| G3 F51 harm | HC2 | F51 crack AP 0.5078 vs 0.4702, Δ +0.0376; 36-module bootstrap: opening [+0.0022, +0.0869], mine [+0.0027, +0.0866] | upper bound < 0 | ok |
- **Next to any-hit (§3c), seed means (E):**
  | readout | SUPPF | SKR2 | HC2 |
  |---|---|---|---|
  | E1 pred / GT crack px | 0.466 | 0.546 | 0.473 |
  | E1 relP@2 | 0.5245 | 0.5393 | 0.5532 |
  | E1 relR@2 | 0.3515 | 0.3962 | 0.3498 |
- **Cell-gate line (v1.0.1). UNSTABLE THRESHOLD: reported only, never evidence for or against a gate.**
  - Why unstable: the val-chosen t swings across seeds. t per run: SKR2 9.39 / 0.31 / 7.84 / 2.16 / 8.37; SUPPF +5.72 … −10.81; HC2 +7.84 … −12.25.
  - Ungated → gated at b 0, SKR2:
    - E1 crack-free px 3,819 → 3,312 (vs SUPPF ×0.97 → ×0.85);
    - E1 any-hit 0.425 → 0.403 (Δ vs SUPPF +0.044 → +0.022);
    - test relP@2 0.9296 → 0.9314 (Δ −0.0121 → −0.0108).
  - Ungated → gated at b 0, HC2: crack-free px 3,125 → 2,794; any-hit 0.363 → 0.349; test relP@2 0.9225 → 0.9307.
  - For SKR2 the gate empties 57.6 of 74 E1 crack-free cells, and also 5.4 of 32 crack-positive cells.

## HC2 mechanism (§3b; SHV1, val-derived, non-E1)
| arm (5 seeds pooled) | matched relR@2 at relP@2 ≥ 0.90: V0 / SHV1 / SHV1-p | max SHV1 relP@2 (b) | SHV1 at b 0: relR@2 / relP@2 | SHV1 inactive IoU at b 0 |
|---|---|---|---|---|
| SUPPF | 0.876 / 0.696 / 0.706 | 0.936 (−4.0) | 0.697 / 0.900 | 0.471 |
| **HC2** | 0.887 / **undefined** / **undefined** | **0.776** (−4.0, grid floor) | 0.846 / **0.732** | **0.002** |
| HC (reference, opened) | 0.889 / 0.819 / 0.836 | 0.939 (−4.0) | 0.823 / 0.897 | 0.383 |
| SKR2 (context) | 0.877 / 0.716 / 0.732 | 0.923 (−4.0) | 0.734 / 0.888 | 0.433 |
- **Decision: mechanism FAILED.** (The frozen readout prints UNDEFINED and leaves an unreachable case to coach.)
  - The registered quantity is recall at relP@2 ≥ 0.90. HC2 never reaches 0.90 on pooled SHV1 (max 0.776), and no single seed does either, so the +0.05 gain is not shown.
  - I read it as recall-at-precision = 0 (the usual R@P convention). I do not use the max-precision b: calib's fallback exists to choose a val OP. Here it would compare HC2 at relP 0.78 with SUPPF at 0.90. For the record, HC2's relR@2 there is 0.789 (flagged, not used).
- **Where it fails (E, `diag/shv1diag.txt`; a descriptive post-hoc split with no verdict role):**
  - **11 of 108 SHV1 views per run carry GT inactive** (from val's inactive cells; 55 pooled over 5 seeds). Pooled over 5 seeds:
    - HC2 predicts **340 inactive px vs HC's 231,221** (IoU 0.002 vs 0.386);
    - it predicts 417,601 crack px vs HC's 226,137;
    - its **off-GT (2 px) crack px are 161,569 vs 31,643 (×5.1)**;
    - relP@2 at b 0 is 0.61.
  - **The other 97 views per run (485 pooled), without GT inactive:** HC2 ≈ HC.
    - matched relR@2: HC2 0.845, HC 0.858, SUPPF 0.784 (HC2 − SUPPF +0.060);
    - max relP@2: 0.954 vs HC's 0.955.
  - **Real val (V0) is unaffected:**
    - inactive IoU at b 0 (seed means): HC2 0.484, SUPPF 0.508, HC 0.468;
    - relP@2 on val's inactive cells: HC2 0.882, HC 0.900.
- **Reading (S):**
  - The ignore label taught the network that synthetic half-cut views hold no inactive. In those views every labelled px lowers the inactive logit and none raises it. Whatever the inactive area is called there costs nothing, so it comes out as crack.
  - The crack mechanism itself survives (the views without inactive).
  - **§7 (a2) is formally triggered:** "mechanism failed at full crack dose → the HC route closes"; HC2 ran at full crack dose and its registered mechanism failed. **coach and judge recommend not applying it.** The failing quantity is precision on the 11 inactive-bearing SHV1 views per run, an artefact of the ignore label, while the other 97 views pass (+0.060 vs SUPPF). That reason is a post-hoc reinterpretation, disclosed as such. **The call is the user's.**
  - I did not foresee this effect at v1.1 (the v1.1 note (i) covered only the lost inactive gradient). Disclosed.
- **Live synthetic readouts (E, `hc2_synth_readout.txt`), as expected:**
  - synthetic share 0.2578-0.2606; eligible 0.7383-0.7387; p_eff 0.349-0.353 (expected 0.2585 / 0.7385 / 0.35);
  - **synthetic_inactive_px 0 in all 5 runs**;
  - ignored share of synthetic px 0.00206-0.00212.

## Reported (§4; never change a verdict)
### SKR2
- **Seed-aware two-stage bootstrap (E, `diag/boot.txt`; modules or E1 images, plus seeds):**
  | readout | Δ | 95% interval | P(Δ > 0) |
  |---|---|---|---|
  | E1 relF1@2 | +0.0364 | [+0.004, +0.076] | 0.99 |
  | E1 relR@2 | +0.045 | [+0.012, +0.084] | 0.99 |
  | E1 relP@2 | +0.015 | [−0.032, +0.074] | 0.69 |
  | E1 any-hit | +0.044 | [−0.006, +0.103] | 0.96 |
  | test crack IoU | +0.009 | [+0.001, +0.019] | 0.98 |
  | test relF1@2 | +0.009 | [−0.001, +0.024] | 0.96 |
  | test inactive IoU | +0.010 | [−0.017, +0.041] | 0.77 |
  - The clean set gives the same picture.
- **Width (E):**
  - test pred / GT 0.954 → 1.062 (+11%; SKR w 1.0 went to 1.545);
  - test relP@2 −0.012 (w 1.0: −0.070); pixel precision −0.026, pixel recall +0.043; test any-hit 0.875 → 0.886;
  - on E1, pred / GT is +17% while relP@2 rises and crack-free px stay flat (×0.97; w 1.0: ×2.4).
  - E1 crack IoU and pixel recall are not quoted: E1 GT is ~1.5× wider than train, so both are width-inflated (judge, THIN).
- **E1 strata (relF1@2; any-hit where shown):**
  - scuff + half-cut (29): relF1@2 0.359 → 0.400; any-hit 0.348 → 0.393;
  - half-cut without scuff (29): 0.780 → 0.786;
  - full (48): 0.452 → 0.487;
  - other (77): 0.521 → 0.551.
  - SKR2's seed sd is smaller in every stratum.
- **LA tau 1:** crack IoU +0.0043 / +0.0042, relF1@2 +0.0078 / +0.0076, inactive +0.0112 / +0.0116; all n.d.
- **Scuff-ignored test:** same as the verdict sets (crack +0.0090 / +0.0088).
- **Per source, test crack IoU (descriptive, no labels):** ARTS +0.029, BMRK +0.010, CFVS +0.008, CSIR +0.009. Without the 7 D6 twins: +0.015 (unregistered subset, no label).
- **F51 and SHV1:**
  - F51 crack AP −0.0046 [−0.0098, +0.0157];
  - false alarms at val b_rel: H36 182 vs 278 px, F51 770 vs 1,231 px;
  - SHV1 matched relR@2 +0.020 (context only).
- **Training and encoder:**
  - thin term (raw value, 5k-block means): 0.39 → 0.21, all seeds alike;
  - 20k encoder cosine: layer3 0.925-0.928, layer4 0.930-0.940 (PF held).
- **Reference row, SKR w 1.0 (opened, not a contrast):** E1 relF1@2 0.479, any-hit 0.523, pred / GT 1.096, crack-free px 9,428.

### HC2
- **Test inactive (G1):**
  - seed-aware [−0.078, +0.015], P(Δ < 0) 0.89;
  - 10 of 16 test inactive cells drop (median −0.030);
  - **HC2 − HC (descriptive, both opened): −0.003; 8 of 16 cells down, median −0.004.** Removing the synthetic inactive labels did not recover HC's test inactive cost.
- **E1 inactive** −0.0795, n.d.:
  - seed-aware [−0.263, +0.089];
  - 5 of the 7 E1 inactive images drop (median −0.18), with less predicted inactive volume. Example: CSIR_01101, a full cell without a half-cut, 1,487 → 327 px (seed mean);
  - HC2 − HC −0.079;
  - **concentration** (judge, E): 9,158 GT inactive px per run in 7 images; the top 3 (CSIR_01637 / 01101 / 01647) hold 87.0%, effective n 3.3 images. Leaving the top 3 out: HC2 −0.023, SKR2 +0.006, HC −0.011. The E1 inactive co-primary is a 3-image readout;
  - strata: half-cut (58) 0.537 → 0.381; scuff + half-cut 0.572 → 0.415; half-cut without scuff 0.150 → 0.026; full 0.097 → 0.018.
- **Crack:**
  - E1 relF1@2 +0.007 (n.d.) comes from precision: relP@2 +0.029, relR@2 −0.002, crack-free px ×0.80; any-hit −0.018;
  - test crack IoU +0.003 / +0.006; HC2 − HC −0.006 / −0.002;
  - B5 (reported; not a co-primary for HC2): comp recall +0.0392 / +0.0396, BETTER by rule-1 arithmetic (b_comp 5.1 vs 3.9; HC was +0.037), **with test comp precision at that OP 0.728 vs SUPPF 0.846 on all 50** (0.889 vs 0.890 on the clean 49; judge, `judge/out/s2_b5w_out.txt`); relR@2 −0.004, n.d.
- **F51 and H36:** F51 crack AP +0.038 (HC +0.067). False alarms at val b_rel: H36 38 vs 278 px (HC 11); F51 41 vs 1,231 px.
- **Per source, test (descriptive):**
  - inactive: ARTS −0.41 (few px), BMRK −0.039, CSIR −0.032, CFVS −0.005;
  - crack: ARTS +0.060, BMRK +0.024, CFVS −0.007, CSIR +0.004.
- **LA tau 1:** crack −0.0015 / −0.0002, relF1@2 −0.0026 / −0.0011, inactive −0.0251 / −0.0251; all n.d.
- **Scuff-ignored test:** same as the verdict sets.
- **Encoder cosines:** layer3 0.927-0.929, layer4 0.928-0.940.

## Reading (S, with E)
- **SKR2: the dose cut did what §2 aimed for.**
  - w 0.1 keeps a recall push: E1 relR@2 +0.045 (P 0.99); test pixel recall +0.043.
  - The width cost is small: test pred / GT +11%, relP@2 −0.012. On E1, relP@2 rises and crack-free px are flat.
  - There is no test crack IoU loss: +0.009 (P 0.98), n.d. by 0.0009.
- **How much the SKR2 PASS carries:**
  - It rests on one E1 co-primary, 0.0013 over its bar. §3d puts the family-wise false-BETTER rate at about 10% or less over the 7 co-primaries. The label is fragile (5 / 10 seed drops, 65 / 71 image drops keep it); the effect is not (seed-aware P 0.985).
  - **Not a bias shift** (judge, E1-oracle, descriptive, chooses nothing): SUPPF's best constant b on E1 reaches 0.4289 (b +4.0), below SKR2's 0.4567 at b 0. At equal E1 predicted volume (SUPPF at b +1.4, pred / GT 0.547) SKR2 still leads: relF1@2 +0.031, any-hit +0.024, relP@2 0.539 vs 0.501, crack-free px 3,819 vs 4,858. So SKR2 sits above SUPPF's own E1 operating curve.
  - **w 0.1 vs w 1.0** (THIN, opened reference): about a third of the detection gain kept (any-hit +0.044 vs +0.142; relR@2 +0.045 vs +0.142), none of the false alarms (E1 crack-free px ×0.97 vs ×2.40; test relP@2 −0.012 vs −0.070).
  - Width-insensitive detection (any-hit) is +0.044, n.d.
  - **Claimable:** "SKR w 0.1 passes protocol_SKR2_HC2: E1 crack relF1@2 BETTER (+0.036), with no test cost and no precision-guard trip."
  - **Not claimable:** "E1 detection BETTER" (any-hit n.d.); "test BETTER".
  - §7: SKR2 PASS → it becomes a candidate for the deploy recipe (the FINAL-style ensemble question), under its own protocol.
- **HC2: FAIL by G1.** On the label-vs-dilution question:
  - **HC2 gives no support to the label cause** (HC2 − HC −0.003 vs +0.023 for full recovery; seed-aware P(full recovery) 0.12, judge), **but cannot exclude it**: (a2) also lowers predicted inactive on test (share of GT inactive px predicted inactive 0.557 vs HC 0.595; inactive px on non-inactive GT 27.3k vs 34.6k per run; judge, `judge/out/s2_inact_conf_out.txt`, `s2_hc2hc_out.txt`). **Dilution is not shown either.**
  - (a2) added a harm of its own: inactive is suppressed in synthetic views (SHV1 IoU 0.002), and predicted inactive is lower on E1 (−0.08, n.d.; 5 of 7 images; E1 share predicted inactive 0.284 vs HC 0.562). Ignore-in-synthetic is not a fix.
- **Recommendation (S): close the (a2) design.**
  - §7 (a2) formally closes the HC route (see Mechanism). coach and judge recommend not applying it: in views without inactive the crack mechanism is intact, and HC's own result stands. The call is the user's.
  - The cause question (label vs dilution) stays open. A dilution-targeted variant (for example, fewer synthetic views of inactive cells) would keep G1 and needs the user's OK.
- **BEST:** no change from this opening. A deploy-recipe change needs its own protocol.
- **User decision (relayed by team-lead after judge's check):** §7 (a2) formally triggered; **not applied by user decision**. The HC route stays open; the (a2) ignore design is closed. Next: protocol_SKR2E (SKR2 as a deployable ensemble).

## judge: adversarial check (2026-11-02 21:44 IST (header first written as 22:40, a typing error, corrected 21:49); verify_skr2_hc2 as of md5 1ae9ef8f; S2 post MANIFEST bd671e26, md5sum -c OK (my read-only pull = runner's results/s2/raw); comparators PF2 3827f7c0, HC d5c39e0d, THIN 5d3f5b31 md5sum -c OK)
**Verdicts CONFIRMED: SKR2 PASS; HC2 FAIL (G1).** HC2 mechanism FAILED (registered readout undefined, so the +0.05 gain is not shown). G3 passed. The SKR2 BETTER label is knife-edge, but the effect behind it is robust and is not a bias shift. Coach's HC2 label-vs-dilution reading overstates (fix 3). The §7 (a2) line is formally triggered; it is not "not triggered" (fix 4).

Code (own; imports no s2_* / el_metrics / coach code; laptop CPU, research/.venv numpy, except the gaint pass):
- `judge/s2_recompute.py` e67795ab: m0 per-cell files. It covers the test two sets, the E1 co-primaries, G1 / G2, width, strata, a seed-aware two-stage bootstrap (clusters + 5 seeds per arm, rng 20261102), HC2 vs HC vs SUPPF, and E1 inactive by source image. Self-test SUPPF vs HC = verify_hc to 4 dp.
- `judge/s2_b5w.py` 67f03055: wide-grid B5 with my own OP code on rec_w, plus a matched-volume E1 check on SUPPF's bias curve.
- `judge/s2_extra.py` f0d2e12e: leave-one-image-out / leave-one-seed-out, E1 relF1@2 vs constant b, and the SHV1 split from records.
- `judge/s2_inact_conf.py` 1ad9caec; `judge/s2_hc2hc.py` fc1bc5cb.
- gaint CPU (nice 19, CUDA hidden; tmux jdgs2, run_s2.sh c7f9490c): `hc_gaint_recompute.py` 53d7e0ea on the dumps (F51 AP + module bootstrap; SHV1 with own EDT code).

Outputs: `judge/out/s2_{recompute,b5w,extra,inact_conf,hc2hc}_out.txt`, `judge/out/s2_f51_gaint.txt`, `judge/out/s2_shv1_gaint.txt`.

### 1. Recompute (E)
- Every co-primary, threshold and guard value in coach's tables equals mine to 4 dp, in both test sets.
  - SKR2: E1 relF1@2 +0.0364 (thr 0.0351) BETTER; any-hit +0.0439 (0.0521); test crack IoU +0.0091 / +0.0088.
  - HC2: test inactive −0.0256 / −0.0259; E1 inactive −0.0795 (0.0830).
  - G2: relP@2 −0.0121; E1 crack-free px 3,819 vs 3,931 (×0.972).
- **B5 wide grid:** OPs (b_comp / b_rel) SUPPF 3.9 / 3.9 (= frozen), SKR2 4.8 / 2.7, HC2 5.1 / 2.6, all reachable.
  - SKR2 comp recall +0.0169 (0.0290) / +0.0171; relR@2 +0.0094 (0.0177) in both sets. n.d., no WORSE.
- **G3:** F51 AP 0.5078 vs 0.4702 (+0.0376). Module bootstrap with seed 0 (the a8 stream): [+0.0022, +0.0869], equal to the opening exactly.
- **Mechanism (own EDT code from the dumps):** HC2's matched SHV1 relR@2 is undefined pooled and in all 5 seeds; V0 0.8874. SUPPF 0.6959 and HC 0.8192 equal the opening.
- **Tool note:** my inherited tool's last line prints "held" when the delta is NaN, because NaN < 0.05 is False. The frozen opening printed UNDEFINED correctly. I do not use that line.

### 2. SKR2 PASS: the BETTER label is fragile; the gain is not (E)
- **The label is fragile:**
  - The margin is 0.0013, 3.7% of the threshold.
  - Leave-one-seed-out keeps BETTER in **5 of 10** drops (3 / 5 SUPPF seeds, 2 / 5 SKR2 seeds), although d stays +0.025 … +0.042 in all 10.
  - Leave-one-E1-image-out keeps BETTER in **65 of 71**. Dropping CSIR_01637, 01101, 01647, 01774, 02026 or 00308 gives n.d.; the worst d − thr is −0.0031.
  - The gain is diffuse: 27 images add to it and 28 subtract; the top 3 hold 49% of the positive part.
- **The effect is not fragile:**
  - Seed-aware two-stage: [+0.0038, +0.0759], P(d < 0) 0.015 (coach [+0.004, +0.076]).
  - It has the same sign in every stratum: scuff + half-cut +0.041, full +0.035, half-cut without scuff +0.006 (each n.d. alone).
- **Not a bias shift.**
  - SUPPF's best constant b on E1 (E1-oracle, descriptive, chooses nothing) reaches 0.4289 at b +4.0. SKR2 at b 0 is 0.4567, +0.028 above it.
  - **At equal E1 predicted volume** (SUPPF at b +1.4, pred/GT 0.547 = SKR2's at b 0), SKR2 is ahead on every readout:

    | readout | SUPPF | SKR2 |
    |---|---|---|
    | relF1@2 | 0.425 | 0.457 (+0.031) |
    | any-hit | 0.401 | 0.425 (+0.024; 19 of 25 seed pairs > 0) |
    | relP@2 | 0.501 | 0.539 |
    | crack-free px | 4,858 | 3,819 |

  - So SKR2 sits above SUPPF's own E1 operating curve: more detection at equal volume, with fewer false alarms. About half of the raw any-hit gain (+0.044) is volume-equivalent.
- **w 0.1 vs w 1.0** (THIN, opened reference): it kept about a third of the detection gain and none of the false alarms.

  | readout | w 0.1 (SKR2) | w 1.0 (THIN) |
  |---|---|---|
  | any-hit | +0.044 | +0.142 |
  | E1 relR@2 | +0.045 | +0.142 |
  | E1 relF1@2 | +0.036 | +0.059 |
  | E1 crack-free px | ×0.97 | ×2.40 |
  | E1 relP@2 | +0.015 | −0.059 |
  | test relP@2 | −0.012 | −0.070 |
  | test pred/GT | 1.06 | 1.54 |

  - Answer to the protocol's question: yes on false alarms. On detection, only partly, and any-hit is n.d. on its own.
- **Test:** crack IoU +0.0091, seed-aware P(d > 0) 0.98, n.d. by 0.0009. relF1@2 +0.0089, P 0.97. Inactive +0.010, P 0.75. "No test cost" is right; "leans better on crack" is the full statement.
- E1 inactive is flat: +0.002; leave-top-3-images-out +0.006.

### 3. HC2 vs HC: the inactive lean stayed; the test cannot say why (E / S)
- **It stayed:**
  - test inactive HC2 −0.0256 vs HC −0.0228; HC2 − HC −0.0028 (clean −0.0029). Full recovery would be +0.0228.
  - The recovered share is −0.12 (seed-aware median −0.10, IQR [−0.87, +0.49]).
  - Seed-aware HC2 − HC: [−0.050, +0.044]. **P(≥ full recovery) 0.12**, P(≥ half) 0.24, P(> 0) 0.43.
  - HC2 is not a paired replicate of HC: the per-seed correlation is −0.34 on test inactive, so "same draws" buys no pairing. Treat it as an independent 5 v 5.
- **Confound (E):** the ignore label suppresses inactive outside synthetic views too.

  | set | readout | SUPPF | HC | HC2 |
  |---|---|---|---|---|
  | test | share of GT inactive px predicted inactive | 0.610 | 0.595 | **0.557** |
  | test | inactive predicted on non-inactive px, per run | 31.2k | 34.6k | **27.3k** |
  | val | share of GT inactive px predicted inactive | | 0.722 | **0.653** |
  | E1 | share of GT inactive px predicted inactive | 0.555 | 0.562 | **0.284** |
  | E1 | share of GT inactive px predicted background | | 0.214 | **0.433** |

  - So any recovery from removing the synthetic labels is mixed with a new suppression that pushes the same readout down.
- **Fix 3:**
  - Replace "What holds: synthetic inactive labels are not the main source of HC's test inactive cost" with: "HC2 gives no support to the label cause (HC2 − HC −0.003 vs +0.023 for full recovery; seed-aware P(full) 0.12), but cannot exclude it, because (a2) also lowers predicted inactive on test (TP share 0.557 vs 0.595). Dilution is not shown either."
  - The (a2) design is closed; the cause question stays open.
- **Post-hoc pool (descriptive):** HC + HC2 (10 seeds) − SUPPF on test inactive is −0.024 [−0.063, +0.007], P 0.94.
  - The synthetic-half-cut lean repeats in a second seed set.
  - SUPPF's 5 seeds bound the interval; still n.d.
- **E1 inactive concentration:**
  - 9,158 GT px per run sit in 7 source images (10 cells). The top 3 hold **87.0%**: CSIR_01637 40.4% (4 scuff + half-cut cells), CSIR_01101 35.2% (full cell), CSIR_01647 11.3%. Effective n is **3.3 images**.
  - HC2 per image (vs SUPPF): CSIR_01637 0.626 → 0.451, CSIR_01101 0.327 → 0.054, CSIR_01647 0.704 → 0.455, CSIR_00400 (full) 0.555 → 0.011.
  - Leave-top-3-images-out: HC2 −0.023 on the 1,195 px left, where 2 of the 4 images are 0 for every arm. SKR2 +0.006; HC −0.011.
  - The E1 inactive co-primary is a 3-image readout; its threshold (0.083) reflects that. The HC2 drop reaches full cells too, so it is not a half-cut-geometry effect alone.

### 4. HC2 mechanism and §7 (S, with E)
- **FAILED is the right reading of the registered rule.**
  - Pooled SHV1 relP@2 peaks at 0.776, at the grid floor b −4.0. Recall at P ≥ 0.90 does not exist, so the required ≥ +0.05 is not shown.
  - The frozen readout left UNDEFINED to coach; this ruling is coach's, made after the numbers, and it is disclosed. I agree with it.
- **The split matches coach's diag** (post hoc; my records code):
  - 11 SHV1 views with GT inactive: HC2 inactive IoU 0.002 (HC 0.386); relP@2 at b 0 0.613; off-GT crack px 32.3k vs 6.3k per run (×5.1).
  - 97 views without: matched relR@2 HC2 0.845, SUPPF 0.784 (+0.060), HC 0.858.
- **Fix 4:**
  - §7 (a2) reads "mechanism failed at full crack dose → the HC route closes". HC2 ran at full crack dose and its registered mechanism failed, so the line **is triggered by its letter**.
  - Not applying it is defensible: the failing quantity is precision on 11 inactive-bearing views, an artefact of the ignore label, and the other 97 views pass. But that is a post-hoc reinterpretation.
  - Write: "§7 (a2) is formally triggered. coach and judge recommend not applying it (reason: ...). The call is the user's." Do not write "not triggered".
- **G3:** F51 AP +0.0376. Seed-aware two-stage [−0.008, +0.100].
  - CSIR_00073 carries it: without its module, d is +0.017.
  - Half of HC's +0.067. Seeds s8 / s9 (0.475 / 0.469) sit at SUPPF's level.
- **Fix 5:** HC2's B5 comp recall "BETTER by rule-1 arithmetic" (+0.039) comes, on all 50 cells, with test comp precision at the OP of **0.728 vs SUPPF's 0.846**. On the clean 49 it is 0.889 vs 0.890. State the precision next to it.

### 5. Fixes for coach (no verdict changes)
1. SKR2: put the fragility line next to PASS: margin 0.0013; leave-one-seed-out 5 / 10; leave-one-image-out 65 / 71; effect seed-aware P 0.985.
2. SKR2: add "not a bias shift" (SUPPF's E1-best constant b 0.4289 < 0.4567; at matched volume relF1@2 +0.031, any-hit +0.024, fewer false-alarm px) and the w 0.1 / w 1.0 fractions.
3. HC2 label vs dilution: as in §3 above.
4. §7 (a2): "formally triggered; recommend not applying; user's call".
5. HC2 B5 comp recall: show test comp P 0.728 vs 0.846 on all 50.
6. Add the E1 inactive concentration line (top 3 = 87%, effective n 3.3; leave-top-3-out HC2 −0.023).

### 6. What this decides (S)
- **SKR2 PASS** → a deploy-recipe candidate under its own protocol (§7). BEST is unchanged until then.
- For the user: "Skeleton Recall at w 0.1 raises E1 crack relF1@2 by +0.036 (PASS by 0.0013). The gain itself is robust (seed-aware P 0.985) and is not a bias shift. It costs nothing measurable on test or in false alarms. Its E1 detection gain (any-hit +0.044) is a third of w 1.0's and n.d."
- **HC2 FAIL (G1).** The ignore-in-synthetic design is closed.
  - It created its own inactive suppression: SHV1 inactive views go to crack, and E1 inactive goes to background.
  - Whether HC's test inactive cost is label or dilution is still open. A dilution-targeted variant would need the user's OK and G1.

## coach: judge's fixes applied (2 Nov ~21:47 IST; first typed as 22:5x, corrected)
- All 6 applied in coach's sections, no verdict change: (1) fragility line next to SKR2 PASS (leave-one-seed-out 5 / 10 re-derived by coach from the per-seed values); (2) not-a-bias-shift and w 0.1 / w 1.0 lines in Reading; (3) HC2 label vs dilution replaced with judge's wording; (4) §7 (a2) "formally triggered; coach and judge recommend not applying; the user's call", in Mechanism and Recommendation; (5) HC2 B5 comp precision 0.728 vs 0.846 (all 50) / 0.889 vs 0.890 (clean 49); (6) E1 inactive concentration (top 3 = 87.0%, effective n 3.3; leave-top-3-out HC2 −0.023). Also corrected: the SHV1 split counts are per run 11 / 97 of 108 views (55 / 485 were pooled over 5 seeds).
- E1 concentration totals re-derived from my `diag/inact.txt` (9,158 px; top 3 7,963 = 87.0%; 1/Σw² 3.26).
