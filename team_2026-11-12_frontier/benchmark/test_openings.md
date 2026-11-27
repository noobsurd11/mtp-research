# Test openings ledger (for the paper)

benchdesign, started 2026-11-12 at team-lead's request (lead decision D11). Same format as `team_2026-10-31_next/e1_openings.md`.
Test = the 50 legacy test cells of BenchmarkEL `dataset_20211104` (`splits/legacy.json`, `sealed_sets.test50`, list md5 a31fad14).
Back-filled from the handbook and the team files; no result file was opened to write it. Tags: E = stated in the cited file; S = judgement.

**Policy (standing rules, `H07` §7, `H18` terms; lead decision 12 Nov):** the test set is never used for training, tuning, checkpoint or operating-point choice. A **test opening** is one scoring of the 50 cells for one locked protocol, registered before the scoring, counted and disclosed. From 12 Nov every opening gets a row here before it happens; the paper reports every row. Training runs must not compute test numbers: development roots set `splits/test.txt` to the val list or the held-out fold (`H13` C18).

## A. Before counting started (to 24 Oct 2026): test was scored in every experiment, uncounted
The count cannot be reconstructed as "openings": scoring test at the end of each run was the normal procedure, and the trainer itself evaluates `splits/test.txt` at the end of every run (`H13` C18). What is known (E):

| Period | What read test | Source |
|---|---|---|
| Old era, to 7 Oct | every run; best-val and test-time choices were made in places; class weights were computed over train + val + test (a leak, later removed) | `H13` B5, B10; `H06` |
| 8 to 10 Oct | P3 (old-era checkpoints re-scored on old and revised masks); P1, P2, P4, P5 diagnostics | `H08` |
| 10 to 13 Oct | P6 to P18: every arm of every experiment scored on test at final weights under a locked rule (P6, P7, P8, P9, P10, P11, P12, P13, P14, P15, P16, P17; P18 exploratory). Protocol lock dates: P6 to P10 10 Oct, P11 to P16 11 Oct, P17 and P18 13 Oct | `H08`, `H09`, `H10`; `protocols/P*.md` |
| 11 to 13 Oct | E1 per-cell re-scoring of the P6 to P12 checkpoints on test and the extension (73 + 33 runs); EMA check; qualitative panel; Pratt-convention re-score (23 runs); SEiPV-convention re-score (18 checkpoints) | `H10` §E1 and follow-ups; `results/seipv_compare/README.md` |
| 14 Oct | P19: Hanifi 2025 reproduction, on the `20221008` release split (553 / 70 / 72), not on test50. Its train split holds 38 of our 50 test cells and most E1 cells; those models (the authors' code) are used nowhere else | `results/p19/README.md`; `H05` §16 |
| 21 to 23 Oct | SK1 (SKCDF head), S-a (logit adjustment on existing checkpoints, post hoc), AL1 (ALHVR port); the null diagnosis of test crack misses (post hoc) | `H10`; `H13` A12 |
| 24 Oct | Track D: frozen-encoder probe (BMRK test crack AP under a locked rule), inactive-edge re-score (post hoc), labelled-set experiment (27 runs) | `H18` §D1 to D3 |
| 24 Oct | Track M M0: audit re-score of the five 100% checkpoints; nothing tuned; stated as not counted | `H18` §M0, §M7 |
| 27 Oct | measurement study on existing per-cell counts (power, label-noise split, component metrics); no new model scored | `eval.md` |

Consequences (S): the house recipe at 100% labels (cv02 seeds 0 to 4) has been scored on test in P6, P16, M0, Track M and the 27 Oct study; its test numbers are a well-read reference, not a blind result. No model was ever selected on test in the P-series (final weights, val-based choices only).

## B. Counted openings (24 Oct to 21 Nov 2026): 19 (row 19 = the final opening, public table only)
| # | Protocol (team) | Models | Test primaries (pre-registered) | Opened | Result (E) |
|---|---|---|---|---|---|
| 1 | Track M R1 (TTA, 5-seed ensemble, crack bias) | SUP100 seeds 0 to 4, cv02; inference only | crack IoU, relF1@2, inactive IoU, mIoU_rob; all 50 and clean | 24 Oct | TTA - plain: crack IoU +0.0104 clean, PASS on the 0.01 floor; ensemble - single: crack IoU +0.0144 [+0.0118, +0.0167] PASS; bias +0.75 descriptive (`H18` §M1) |
| 2 | Track M R2 (Dice on 12 classes) | 5 v 5, cv02 | same four | 24 to 25 Oct | crack IoU -0.0106, relF1@2 -0.0130: WORSE (`H18` §M2) |
| 3 | Track M R4 (+107 E-SCDD cells) | 5 v 5, cv02 | same four | 24 Oct | n.d. on all four (`H18` §M3) |
| 4 | Track M R2c (Dice on 3 classes) | 5 v 5, cv02 | same four | 24 to 25 Oct | n.d. on all four (`H18` §M2) |
| 5 | Track M R3 Part B (ResNet-50) | seeds 1 to 5 v SUP100, cv02 | same four | 24 to 25 Oct | inactive IoU -0.0251 clean: WORSE (`H18` §M4) |
| 6 | Track M R5 (2x resolution) | 5 v 5, cv02 | same four | 24 to 25 Oct | n.d. on all four (`H18` §M5) |
| 7 | Track M FINAL | 5-seed SUP100 ensemble, bias +0.75 and 0 | same four | 25 Oct | PASS: crack IoU +0.018 [+0.013, +0.025] clean (0.492), relF1@2 +0.016 (0.897) (`H18` §M7) |
| 8 | MIM5 (features team) | MIM5 v A5c-f1, 5 v 5, gaint, 5% labels | crack IoU, relF1@2, inactive IoU | 29 to 30 Oct | n.d. on all three, all estimates negative (`H19` §2) |
| 9 | DDeP5 (features team) | DDeP5 v A5c-f1, 5 v 5, 5% labels | same three | 29 to 30 Oct | n.d. on all three (`H19` §3.2) |
| 10 | protocol_100 opening 1 | SUP100-g, SUP100-PF, MIM100-PF, seeds 0 to 4, gaint | same three, all 50 and clean | 31 Oct 00:57 to 01:33 | all contrasts n.d. (`H19` §10.2) |
| 11 | protocol_100 opening 2 | CP100 seeds 0 to 4 (SUP100-g files reused) | same three | 31 Oct 06:53 to 07:07 | n.d. (`H19` §10.3) |
| 12 | PF2 (= E1 opening 1) | SUP100-g, SUP100-PF, RN50-PF, seeds 5 to 9, gaint | same three | 1 Nov 06:33 to 08:26 | PF - house: relF1@2 +0.0117 / +0.0120 BETTER, narrow; crack and inactive n.d. RN50-PF: inactive -0.0289 WORSE (`H20` §4) |
| 13 | PF2E (= E1 opening 4) | ensembles of PF2's members; inference only | same three, at b 0 | 1 Nov 19:02 to 19:13 | test n.d. on all three (crack IoU 0.4788 v 0.4815) (`H20` §5) |
| 14 | THIN-B3 (= E1 opening 2) | SKR, CLD, B3 seeds 5 to 9 v PF2's SUPPF | same three + two operating-point readouts | 1 Nov 19:40 to 21:13 | SKR crack IoU -0.0136 WORSE; CLD and B3 n.d. on the three; no arm passes (`H20` §6.0) |
| 15 | HC (= E1 opening 3) | HC seeds 5 to 9 v SUPPF | same three | 2 Nov 02:18 to 03:10 | n.d. on all three (`H21` §2) |
| 16 | SKR2_HC2 (= E1 opening 5) | SKR2 (w 0.1), HC2, seeds 5 to 9 v SUPPF | same three + two operating-point readouts; guards on test inactive and relP@2 | 2 Nov 20:01 to 21:23 | SKR2 test n.d.; HC2 test inactive -0.0256: guard trip (`H21` §4) |
| 17 | SKR2E (= E1 opening 6) | E-SKR2 v E-PF ensembles; inference only | same three at a shared b 0; guards at the headline pair | 2 Nov 22:24 to 22:36 | at b 0 crack IoU +0.0102 and relF1@2 +0.0104 pass; FAIL by the guards at the headline pair (`H21` §5) |
| 18 | SKR2C (= E1 opening 7) | SKR01 v SUPPF, fresh seeds 10 to 14, gaint; singles (R) and two 5-member ensembles at a shared b 0 (D) | R: the SKR2_HC2 set at argmax (three + two operating-point readouts; guards on test inactive and relP@2). D: the SKR2E set at b 0 (three; guards on relP@2 and test inactive) | 14 Nov 00:22 to 03:54 | Third look at the same 50 cells for this contrast. R: all five test co-primaries n.d. (crack IoU −0.0254 on all 50, +0.0021 on the clean 49; inactive −0.0198 / −0.0207); guards on test inactive and relP@2 (−0.0780, one run on the noisy cell) trip: R FAIL. D: crack IoU +0.0004 [−0.0050, +0.0052], relF1@2 +0.0008 [−0.0035, +0.0047], inactive −0.0269 [−0.0592, +0.0007], no primary passes or fails; guard on test inactive trips (−0.0269 / −0.0283): D FAIL (`team_2026-10-31_next/verify_skr2c.md`) |
| 19 | final opening, test50 public table (harness/final/opening, rule 065a7dddfff2efd4897503561955093f; REGISTERED.txt 4c783a779208979ccbed8c13802950b2) | C1 fin_pf_v11_pool_s5..9 (plain), C2 fin_hrnet_swad_v11_pool_s5..9 (swad, D4), C1-D4 | public table only, decides nothing: Pratt median IoU rules A/B/C, PV-S3 both background rules, SEiPV family on v0; protocol card on v1.1 (all 50, clean 49, 16 without module link); C2 - C1 relF1@2 secondary | registered 21 Nov 2026 11:22; **opened 11:25:30 to 12:06:09** (dumps cv02 to 11:58:14; read once 12:02:30 to 12:06:09, rc 0) | public table only, decides nothing: v0 Pratt A median IoU crack C2 0.383 / C1 0.337, inactive 0.588 / 0.570, mean of 3 0.424 / 0.405; PV-S3 crack IoU 0.441 / 0.418; v1.1 C2 - C1 relF1@2 +0.0102 [-0.0094, +0.0291] n.d., strict crack IoU +0.0229 (outside band); in-distribution with known leakage (`results/FINAL_OPENING_READ.md`) |

Multiplicity (S): 18 openings, each with 3 to 7 uncorrected test readouts. Openings 13 and 17 re-measure the members of 12 and 16. The SUPPF seeds 5 to 9 files of opening 12 were reused as the comparator in 14, 15 and 16 (a reuse, not a new read). Opening 18 (SKR2C, 14 Nov) is the third look at the same 50 test cells for the SKR01 v SUPPF contrast (after 16 and 17), on fresh seeds.

Disclosed slips (E): before opening 8, one supervised run's test crack IoU (0.301) was seen in a stdout (`H19` §3.4). Further incidents (a stdout tail during THIN-B3, a quarantined CPU batch, test images touched for structure) are listed in `H13` D34 to D45; not re-read here.

## C. Trained or run without a test read (E)
| What | Why no read |
|---|---|
| AM (MIM reconstruction error), 29 Oct | val only (`H19` §3.1) |
| CP5, 30 Oct | stopped unscored; the automatic re-score files of two seeds exist, unopened (`H19` §3.3) |
| D (inference-only checks), 30 Oct | val and E1 only (`H19` §10.5) |
| A8 screen (DINOv3 ConvNeXt-T), 1 to 2 Nov | F51 and val only; per-run data root with test.txt = val (`H21` §1) |
| B6 (module-grouped CV), 2 Nov | per-fold roots; test.txt = the held-out fold (`H21` §3) |

## D. Registered, not opened
| # | Protocol | Models | Test primaries | Registered | Status |
|---|---|---|---|---|---|
| (18) | SKR2C | moved to section B on 14 Nov 2026 | | | **opened 14 Nov 00:22 to 03:54** (row 18 of section B) |
- Row 18 (SKR2C = E1 opening 7): **registered, NOT opened**; opening set FROZEN 14 Nov 2026 00:13 IST, FROZEN.md5 836be7e50c509339266097f4ba712f67 (27 files; `team_2026-10-31_next/build_s2c_stage2.md` §4, §7). Same 50 test and 106 E1 cells, 3rd look for this contrast.
- Row 18 **OPENED 14 Nov 2026 00:22:45 to 03:54:57 IST** (lead's driver run on the user's OK of 12 Nov; R rc=0, D rc=0). Coach's recompute and judge's check: `team_2026-10-31_next/verify_skr2c.md` (judge CONFIRMED WITH FIXES 05:28). R FAIL, D FAIL; the SUP100-PF ensemble stays. Nothing is registered and unopened now.
- Row 19 (final opening, test50 public table = E1 opening 8): **registered, NOT opened** 21 Nov 2026 11:22:35 IST, REGISTERED.txt 4c783a779208979ccbed8c13802950b2 (`harness/final/opening`, rule 065a7ddd); row in section B. Public table only; decides nothing.
- Row 19 **OPENED 21 Nov 2026 11:25:30 to 12:06:09 IST** (with E1 opening #8; one queue on cv02, read once on gaint, rc 0). Public table only; E1 decides: CONFIRMED (C2 - C1 relF1@2 +0.0430 [+0.0013, +0.1043]). `results/FINAL_OPENING_READ.md`, `results/final_opening_read/`.

## E. Benchmark openings (from 12 Nov; none yet)
Rows are added before the scoring starts.

| # | Protocol | Models | Sets and primaries | Registered | Opened | Result file |
|---|---|---|---|---|---|---|
| | | | | | | |
