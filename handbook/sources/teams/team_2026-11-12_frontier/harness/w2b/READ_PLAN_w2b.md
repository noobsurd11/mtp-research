# Wave 2b: pre-registered reads of la_ce and layered_ci (w2b builder, 17 Nov 2026, written before any w2b run)

E = measured by my own command, S = my judgement, D = a ruling with its source. All earlier ASK items are ruled (K0 to K4, Q1 to Q7).
Revision 2 (19:09): section 1 rewritten to the lead's la_ce rulings Q1 to Q7 (log.md "17 Nov 17:33", line 155).
Revision 3 (19:16): the lead's rulings on K0 to K4 and the Q6 corrections (a) and (b) and the la_ce_full follow-up
(log 18:00) applied; the read script, count step and verdict step are built (section 5). Nothing is open. Line numbers below are of the files as they stood at 19:10.
Sources: `cards/T10_rare_classes_spec.md` (arm 2 last bullet = la_ce; arm 3 = layered_ci), `cards/WAVE3_REVIEW.md` (Y1, Y6,
row layered_ci FIX then GO, "Gated follow-up la_ce: as specified, read against OP-C", G18, G20), `log.md` 15 Nov 12:50
(stage A rulings: M per machine; L4 count-based inactive policy; ci_rules_posthoc dropped; layered_ci the one trained
inactive arm), 15 Nov 16:07 (classbias_xfit passes, OP-C = comparator, la_ce opens, wider grid variant), 17 Nov 17:11
(la_ce and layered_ci on gaint against W1-G PF), `benchmark/PROTOCOL_v0.2.md` 5.3, 5.4, 11, `results/stageB/B1_classbias_xfit.md`,
`results/W2A_READ.md` and `harness/w2a/read/run_read_w2a.sh` (template; lead's ruling: PF seeds 5, 6 registered, PF4 =
sensitivity only).

## 0. Common to both reads
- Machine gaint only (D 17:11): arm dumps `/home/noob/work/bench_dumps/w2b/elbench1/<card>/<run>`, PF dumps
  `/home/noob/work/bench_dumps/w1g/elbench1/house_r34_unetpp_pf_v11` (W1-G seeds 5, 6; W1-G2 seeds 7, 8 for the A/A),
  PF at OP-C `/home/noob/work/bench_udev/opc/dumps_gaint/elbench1/pf_v11_opc` (classbias_xfit variant 1, registered OP-C;
  manifests: device RTX PRO 4500, fp32, decision `argmax24_logp_plus_classbias_xfit`; E 17:5x).
- Split cv5v2, 532 out-of-fold pool cells, label set v1.1, 330 groups (`cv5v2_groups.tsv`). Clean cells:
  `benchmark/splits/score_exclude_v3.txt` (md5 6d48dfbd, 116 excluded, 416 left; PROTOCOL_v0.2 l.262 to 263). For la_ce
  both cell sets decide (D 17:33, Q6); for layered_ci the 532-cell values decide and the 416 are printed beside (as W2A_READ).
- Tool: the reviewed read tree `bench_wt_b` b5bf0ae, `scripts/bench_read_w1.py` fdb56b78 (two-stage group bootstrap,
  2,000 draws, OP-A and cross-fitted OP-W, `--aa`), as `run_read_w2a.sh`.
- Arms common to both: `PF` = W1-G `w1g_pf_v11_f[0-4]_s[56]`; `PFAA` = `s[5-8]` (A/A only, `--aa PFAA:5,6:7,8`);
  `PFC` = PF at OP-C, `pf_v11_opc:w1g_pf_v11_f[0-4]_s[56]`. `--baseline PF` (OP-W matches PF's crack width).
- Margins (D 15 Nov 12:50; PROTOCOL 5.4; recomputed in the read from the same A/A): M = 0.010 for strict crack IoU,
  relF1@2 and mIoU-R13; M_inact = 0.054 (gaint). M covers seed noise, not the choice of folds.
- A screen pass is a promotion to a 5-seed confirmation (on cv5v3, as swad_const), never a result. One read per arm;
  the ledger records the contrasts read. A PF4 read (PF = seeds 5 to 8) is a sensitivity read in its own folder.
- K0 answered (D 17:33, Q5): PF seeds 5, 6 registered, at OP-A and at OP-C (`pf_v11_opc` seeds 5, 6); M from the A/A
  {5,6} v {7,8}; PF seeds 5 to 8 only as a printed sensitivity read in its own folder (w2b_pf4_<arm>). The brief's
  "seeds 5 to 8" is replaced. K1 answered: the G18 baseline is PFC. K2: the layered_ci comparator is PFC. K3: L1 to L5
  as proposed, L1 with its CI low > 0. K4: gaint against W1-G; L1 to L7 replace the spec's promotion (lead's K ruling, received between 19:10 and 19:16).
- Cell sets (lead, Q6 correction (a)): P1, P2 (la_ce) and L1 (layered_ci) must hold on the 532 cells AND on the 416
  clean cells; every guard is judged on the 532 cells and printed for both (cv5v2 has the module leak; the 416 condition
  keeps a leak-driven pass out).

## 1. la_ce (card `la_ce_pf_v11`, runs `w2b_lace_f[0-4]_s[56]`, dumps with the card's argmax24; rule = D 17:33 Q6)
Arm `LACE` = `la_ce_pf_v11:w2b_lace_f[0-4]_s[56]`, read at plain argmax; no post-hoc bias on la_ce and no logp in its
dumps (T10 spec l.156 "plain argmax at test, with no post-hoc bias on top (P045 5.3)"; D Q7).
Pairs (B - A): `PFC=LACE` (primary), `PF=LACE` (Y6). P1 and P2 must hold on the 532 cells AND on the 416 clean cells
(`--score-exclude`; D Q6 (a); the rule of rows 2 and c3swad, log.md l.152 Q2); the guards G1 to G5 are judged on the
532 cells and printed for both.
Offsets (D Q1 to Q4; card `la_ce_pf_v11`, harness/w2b/make_la_ce_card.py): per fold k, o^(k)_c = -mean over seeds 5 to 8
of b_{s,k,c} for the 11 FREE classes, 0 for the others (T10 spec l.132 to 134 for FREE, b[0] = b[14] = 0). **Deviation
from the spec text (l.156 "mean over folds and seeds"), ruled Q1:** the pooled vector would use the fits b_j (j != k),
whose fit cells include fold k, so fold-k labels would set training scalars of the fold-k run; b_k is fitted on folds
!= k only (the status of OP-C itself). Inactive o_11 = -4.0 in every row, the edge of the fit grid (-1.5 to +4.0;
B1_classbias_xfit.md 2d: b_11 = +4.0 in all 45 PF fits); the wider-grid variant failed its rule (B1 section 5), so the
registered value stays (D Q4). The unstable classes border 5, padding 7, frame_edge 21 keep their means (D Q3).

| # | Element | Rule (point = mean over 2 seeds; CI = two-stage group bootstrap 95%) | Source |
|---|---|---|---|
| P1 | primary | mIoU-R13(LACE) - mIoU-R13(PFC) >= M (0.010) and CI low > 0, on 532 and on 416 cells | T10 spec l.156 "primary mIoU-R13 against baseline + classbias_xfit"; WAVE3 l.104; M: PROTOCOL l.109 to 116, log l.54; D Q6 |
| P2 | Y6, present at OP-A | mIoU-R13(LACE) - mIoU-R13(PF) >= M and CI low > 0, on 532 and on 416 cells | WAVE3 l.37 (Y6) "counts only if it is present at OP-A and against baseline at OP-C"; l.274 (G18); D Q6 |
| G1 | crack guard (drop) | LACE - PF strict crack IoU >= -M and relF1@2 >= -M (points), at OP-A and at OP-W, against PF at the same operating point (532; 416 printed) | D Q6; OP-A / OP-W decide: PROTOCOL l.98 to 99, l.118 |
| G2 | inactive | inactive IoU(LACE) - inactive IoU(PFC) >= -M_inact (point; M_inact = 0.054 on gaint, from the read's A/A) | D Q6; M_inact: PROTOCOL l.114, log l.54 |
| G3 | per class | no R13 class with IoU(LACE) - IoU(PFC) < -0.03 (point) | **S**: the spec states this rule for classbias_xfit (T10 spec l.150 "no R13 class down by more than 0.03"), not for la_ce (l.156); kept, D Q6 |
| G4 | prior shift (G18) area, each FREE class 1, 2, 4, 5, 7, 11, 13, 15, 16, 20, 21 | pred / GT px of LACE within 0.85 to 1.15 x PFC's (points) | WAVE3 l.274 (G18) "... the predicted to GT area ratio (0.85 to 1.15 x baseline), are pass conditions"; baseline = PFC (D K1) |
| G5 | prior shift (G18) false px, each FREE class | LACE pred px on the cells without that class <= 1.5 x PFC's (points; PFC 0 means LACE must be 0, S) | WAVE3 l.274 (G18) "Predicted px of the class on cells without it"; factor 1.5 = the protocol's crack false-alarm factor, LAUNCH_REQUEST_w2a.md l.74 (D Q6 (b)) |

- **Promote** (to the 5-seed confirmation; a screen pass is only a promotion, PROTOCOL l.117) if P1 and P2 hold on both
  cell sets and G1 to G5 hold on the 532 cells. **Drop** if the primary delta (P1 point) <= 0 (S: on either cell set),
  or any crack guard (G1) fails (D Q6). Otherwise **park**: no promotion at 2 seeds (S: the ruling names no third outcome).
- **Pre-declared follow-up (lead, log 18:00):** if la_ce comes out null on mIoU-R13 or on inactive, it is not closed on
  that alone; the follow-up is **la_ce_full** (the offset in both the CE and the Dice term), screened the same way (same
  folds, seeds, comparators and rule). Reason on record: reviewer note N4 (REVIEW_W2B r1): the inactive Dice on
  softmax(z) can pull back much of the -4.0 CE offset, so a null may come from the "CE term only" design.
- Printed beside, deciding nothing: gridline 15 and splice 16 IoU, precision and px on the cells without them (log
  l.61, lead 15 Nov 16:07; D Q6); every guard's CI beside its point (D Q6); per-class IoU / P / R for the 13 classes; per
  source (BMRK row); crack width ratio (pooled and per source with >= 40 cells, PROTOCOL l.89) and false crack px on the
  303 crack-free cells (PROTOCOL l.90), as flags; LACE - PFC and LACE - PF for relP@2, relR@2; the inactive count
  readouts R1 to R5 of section 2; the PF4 sensitivity read (D Q5); each run's `LA_CE:` log line (its fold row).
- Tools: P1, P2, G1, G2 from bench_read_w1 (bench_wt_b b5bf0ae, fdb56b78): `--arm PF=...:w1g_pf_v11_f[0-4]_s[56]
  --arm PFAA=...:s[5-8] --arm PFC=<pf_v11_opc>:w1g_pf_v11_f[0-4]_s[56] --arm LACE=<w2b dumps>/la_ce_pf_v11:w2b_lace_f[0-4]_s[56]
  --pair PFC=LACE --pair PF=LACE --baseline PF --aa PFAA:5,6:7,8 --score-exclude score_exclude_v3.txt --labels v11`.
  G3 to G5 from `harness/w2b/w2b_counts.py` on the finished read folder (`--classes 0,1,2,4,5,7,11,13,14,15,16,20,21`,
  once without and once with `--exclude score_exclude_v3.txt`). All of it, with the verdict, by `run_read_w2b.sh ARM=lace`
  (section 5).

## 2. layered_ci (card `layered_ci_pf_v11`, runs `w2b_lci_f[0-4]_s[56]`)
Readouts of each run (3 dumps from one checkpoint, `bench_infer --decision`): `LCI` = layered_ci_replace at t_I 0.5
(card's rule, primary), `LCIARG` = argmax of the 24 logits (`<run>.argmax24`), `LCIUNI` = union rule (`<run>.layered_ci_union`).
Gate before the screen: the pathfinder passes (section 3). G-layer is open (D 15 Nov 12:50; its union-proxy clause met
by O1 + O5 = +0.15 >= 0.04, results/stageA/A3).

Corrections in force over the spec (D WAVE3 row layered_ci; D stage A L4): the within-model contrast is mechanism
evidence only; the comparator for promotion is PF with the best post-hoc inactive layer; promotion by the count-based
readouts of Y1; pooled inactive IoU promotes no trained arm at 2 seeds.
- K2 ruled (lead's K ruling, received between 19:10 and 19:16): the comparator is PFC (OP-C variant 1, inactive bias +4.0 in every gaint fit), the best
  post-hoc inactive layer that passed. Reason: WAVE3 names "rule b, OP-C inactive bias", but rule b (ci_rules_posthoc)
  was dropped at stage A (rules change under 1% of px) and the wider inactive grid (OP-C2) failed its rule.

Count-based readouts (definitions = the reviewed scorer `bench_wt_b` bench/m0core.py and B1 2e):
- R1 inactive region recall: share of GT inactive components >= 100 px (8-connected) with >= 50% of their px predicted
  inactive (`in_cc_rec50`), pooled over cells.
- R2 inactive false-alarm px: predicted inactive px summed over the cells without GT inactive (484 of 532 on v1.1; the
  read prints n).
- R3 inactive precision (pooled TP / predicted inactive px); R4 predicted / GT inactive px; R5 inactive IoU (direction).
- Intervals: two-stage group bootstrap as `crossfit_op.boot_pair` (330 groups, then one seed per fold; arms drawn
  independently for between-model contrasts, the same seed for both readouts of one run for within-model contrasts),
  2,000 draws, seed 0. The reviewed tool bootstraps inact_iou only (R1, R3 are point values in its guard table), so
  R1 to R5 come from `harness/w2b/w2b_counts.py` (built 17 Nov; round 2 review): `--pair PFC=LCI --pair LCIARG=LCI:paired
  --pair LCIARG=LCIUNI:paired --pair PF=LCI`. E (`harness/w2b/test_w2b_counts.py`, 18:00): on the finished wave 2a read it
  reproduces bench_read_w1's PF and RCS inactive IoU, precision and region recall (to 6 dp) and its RCS - PF inactive
  IoU delta and 95% bounds (to 4 dp), so its draws are the tool's draws.

| # | Read | Rule (mean over 2 seeds; 532 cells decide, except L1: 532 AND 416) |
|---|---|---|
| L1 | promotion (count-based, against PFC) | R1(LCI) - R1(PFC) > 0 with 95% CI low > 0, on the 532 AND on the 416 clean cells (D Q6 (a), K3) |
| L2 | false alarms | R2(LCI) <= 1.15 x R2(PFC) (point) |
| L3 | precision | R3(LCI) - R3(PFC) >= -0.02 (point) |
| L4 | area (spec risk 1, G18) | R4(LCI) within 0.85 to 1.15 x R4(PFC) |
| L5 | direction (Y1) | R5(LCI) - R5(PFC) > 0 (point) |
| L6 | mechanism (within model, drop guard) | R5(LCI) - R5(LCIARG) > 0 (point), paired seeds; printed with CI; promotes nothing |
| L7 | crack (spec drop rule) | LCI - PF strict crack IoU and relF1@2 >= -M (0.010; point) at OP-A and at OP-W; crack width ratio 0.85 to 1.15 x PF's at OP-A, pooled and per source with >= 40 cells (ARTS, BMRK, CFVS, CSIR); false crack px on the crack-free cells <= 1.5 x PF |

- **Promote** to the 5-seed confirmation if L1 holds on both cell sets and L2 to L7 hold (532). **Drop** if L6 fails
  (the layer does not beat its own model's argmax), or R5(LCI) - R5(PFC) < 0 (point, 532; the spec's "between-model
  delta < 0", comparator updated), or any L7 line fails. Otherwise **park**: "no promotion at 2 seeds".
- Thresholds of L1 to L5 are mine (S; Y1 names the readouts but no thresholds), ruled as proposed with L1's CI low > 0
  (K3, lead's K ruling). Every count readout is printed for the 416 cells as well.
- Printed beside, deciding nothing: R1 to R5 for LCI, LCIARG, LCIUNI, PF, PFC; LCI - PF inactive IoU (the spec's
  original primary, now descriptive); LCIARG - PF (does the aux loss move the softmax inactive, WAVE3 fix (1));
  LCIUNI - LCIARG; inactive region precision (`in_cc_prec`); mIoU-R13 and per-class IoU; G20: leave-top-3-groups-out,
  the BMRK row, fold-level values; the 416 clean cells; the A0 bucket FP-on-crack on LCI's dumps (spec risk 2; needs
  the atlas tool `t10_atlas.py` on the arm's dumps, owed).
- K4 ruled (lead's K ruling, received between 19:10 and 19:16): the spec screens on cv02 against W1-C1; the 17:11 ruling moves it to gaint against W1-G. The
  spec's promotion "(between-model delta >= M_inact with CI above 0) or (within-model delta >= 0.02 ...)" is replaced
  by L1 to L7 under the WAVE3 and stage A rulings.

## 3. layered_ci pathfinder (run `w2b_lcipath_f0_s5`, queue w2b_lcipath; check `harness/w2b/lci_pathfinder_check.py`)
Spec: fold 0, seed 5, 20k steps on gaint; "pass: finite loss; step time <= 1.15x and peak memory <= +1 GB vs the
baseline smoke; the layer's held-out fold-0 region Dice >= 0.3 at 20k. Not used to rank."
- C1 finite loss: every step line finite (loss, loss_sup, loss_aux), last line step 20000, latest.pth step 20000.
- C2 step time: steps/s at step 200 of `smoke_w2b_lci_f0_s5` >= that of `smoke_w2b_pf_f0_s5` / 1.15 (both in queue
  w2b_smoke, MAXC 1, one after the other; S: the same-conditions PF smoke is the "baseline smoke").
- C3 peak memory: gpumem.log peak of `smoke_w2b_lci_f0_s5` <= `smoke_w2b_pf_f0_s5` + 1,024 MiB.
- C4 region Dice: pooled over the 107 fold-0 held-out cells, L = p_inact (sigmoid of the layer) > 0.5 against
  T = inact_region_fill(strict held-out mask); 2 |L & T| / (|L| + |T|) >= 0.3.
- PASS = C1 to C4. The pathfinder run is not a screen run (separate name; the screen has its own 10 runs).

## 4. What each arm's gain could fake (S, printed with the verdict)
- la_ce: a prior shift (Y6) is controlled by reading against PFC; the per-fold offsets come from the fits on folds
  != k (ruled Q1; reviewer N1: second-order dependence as for OP-C). Splice and gridline carry most of OP-C's gain
  (B1: splice predicted 39 to 65 x more often on splice-free cells), so G4 and G5 can bind on splice.
- layered_ci: a sigmoid at 0.5 can predict more area (L2 to L4); the aux loss can lower the softmax's inactive (LCIARG
  - PF printed); writes inactive on GT crack where the softmax misses a crack (FP-on-crack, owed atlas read).

## 5. Read tools (built 17 Nov; round 2 review), all CPU, on gaint, after an arm's dumps are complete
- `run_read_w2b.sh` (ARM=lace or ARM=lci; PF4=1 for the sensitivity read in its own folder; SHOW=1 prints the
  commands): (1) pins: bench_wt_b at b5bf0ae and clean, bench_read_w1.py fdb56b78, score_exclude_v3.txt 6d48dfbd, the
  arm's dump jobs.txt (lace 3759e824, lci 135778ff), w2b_counts.py and w2b_verdict.py (full md5 in the script);
  (2) completeness: every expected dump (10 for la_ce; 30 for layered_ci) has 'trained <job> rc=0' as its last trained
  line in bq/<q>/dump/launch.log and a real folder with a manifest; (3) manifests: run id, fold, seed, weights key,
  step 20000, set, fp32, open set, code f678381, decision rule (and t_I 0.5 on layered readouts); PF fp32 at 31c0c36;
  PF at OP-C derivation classbias_xfit with fit_folds without its own fold; one device; (4) bench_read_w1 with the arms
  and pairs of sections 1 and 2 and --score-exclude (532 and 416 cells in one run); (5) w2b_counts.py on 532 and on 416
  cells (R13 classes; count pairs PFC=LACE, PF=LACE or PFC=LCI, LCIARG=LCI:paired, LCIARG=LCIUNI:paired, PF=LCI);
  (6) w2b_verdict.py: one PASS / FAIL line per element (P1, P2 per cell set, G1 to G5; L1 per cell set, L2 to L7) and
  one "VERDICT <arm>: PROMOTE / DROP / PARK" line. Output /home/noob/work/bench_reads/w2b_<arm> (must not exist), with
  run.log, verdict.txt and MD5.txt.
- Commands: `ARM=lace bash /home/yugma/mtp/research/team_2026-11-12_frontier/harness/w2b/run_read_w2b.sh` once bq/w2b_lace's dump chain is done; `ARM=lci bash /home/yugma/mtp/research/team_2026-11-12_frontier/harness/w2b/run_read_w2b.sh`
  once bq/w2b_lci's is; optionally `PF4=1 ARM=<arm> bash ...` (sensitivity, never the verdict).
- Tests (E): `w2b_verdict_test.py` 43 of 43 synthetic cases (every PASS / FAIL branch, the boundaries M, -M, 1.15, 1.5,
  0.85, the DROP / PARK / PROMOTE precedence, guards judged on 532 only, the 416 condition); `w2b_verdict_shape_test.py`
  PASS (the verdict reads the real read.json and w2b_counts JSON of the wave 2a read, arms renamed; no number printed);
  `test_run_read_w2b.sh` 20 of 20 (SHOW output for both arms and PF4; refusals: bad ARM, existing output, changed tool,
  no queue, missing / failed trained line, wrong commit, wrong rule, missing t_I, symlinked folder, changed jobs.txt;
  complete fixtures pass the checks); `test_w2b_counts.py` PASS (reproduces bench_read_w1). Outputs in evidence/.

