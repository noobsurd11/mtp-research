Verdict, round 1 (la_ce at 73540e7): PASS
Verdict, round 2 (code, cards, queues, smoke, pathfinder at f678381; reads excluded): PASS (no blocking finding; notes R2-N1 to R2-N7)
Verdict, round 3 (the reads: READ_PLAN 3f38d910, run_read_w2b.sh 8d644288, w2b_verdict.py 1ace40f7, w2b_counts.py a23dd544, tests 23b16576 / 56ad06a1 / e60c4695 / 78f16810; step-0 re-checked 19:37): PASS (no blocking finding; R3-N1 for the lead, R3-N4 = R2-N4 on p_inact)
Verdict, whole w2b set (rounds 2 + 3: code f678381, queues, smoke, pathfinder, reads; request 8c2f841d, harness MD5.txt 79e78e11): PASS (no blocking finding; one launch-step change advised, R2-N2; notes R3-N1 to R3-N5)

# Review of wave 2b, round 1: la_ce (logit-adjusted CE) at commit 73540e7, 17 Nov 2026

Reviewer: w2b_reviewer (independent, built none of it). Round 1 from 17:47 to 17:59 IST (clock from `date`).
Object: branch bench_w2b, commit 73540e7 (parent c57508e = wave 2a code). Reviewed from my own `git archive` of 73540e7 and of c57508e (scratch dir, removed), never the builder's worktree. The worktree is NOT at 73540e7 in content: it has 8 modified tracked files and 2 untracked ones (layered_ci work in progress, E `git status --short`), so nothing may be deployed from the live worktree; deploy only from the commit.
E = my own command; S = judgement. No sealed cell (legacy test 50, E1 106) read; no held-out metric read. CPU only, nice 19, at most 8 threads; nothing started on a GPU; no process of mine is left (5 recorded PIDs, all gone, E).
Own evidence (scripts, logs, config_used.yaml, no checkpoints): /home/noob/work/bench_reads/w2b_review/r1/.

## md5s reviewed (first 8; `git show 73540e7:<file> | md5sum`, E)
| File | md5 |
|---|---|
| src/losses/ce_dice.py | 7f6cf1f9 |
| src/losses/loss_factory.py | 64f66a99 |
| scripts/train.py | badf231a |
| tests/test_w2b_la_ce.py | c508a620 |
| bench/methods/la_ce_pf_v11.yaml | 8bcd481a |
| T/harness/w2b/make_la_ce_card.py | d671b90d (on disk, unchanged) |
| T/harness/w2b/run_w2b_check.sh | 56dd3d20 as handed to me; **changed on disk since** (a610df71 at 17:53, 2407c83b at 17:59, E). Round 2 must review the current file. |
| Inputs | classbias_b.tsv d6a2bf00 (bench_reads/stageB/B1/fit_gaint_pf), house_r34_unetpp_pf_v11.yaml a4a46a52 (= W1-G dump manifests' card_md5), weights f57b4305 (= card) |

## Blocking findings
None.

## 1. Leakage: PASS (one note)
- E: I recomputed the 5 rows from classbias_b.tsv with exact fractions (o_c = -mean over seeds 5..8 of b_{s,k,c} for FREE = {1,2,4,5,7,11,13,15,16,20,21}, 0 elsewhere; non-FREE b are 0 in all 20 rows). All 5 rows of the rendered card equal mine exactly (float lists, no -0.0). Inactive = -4.0 in every row (b_11 = +4.0 in all 20 fits, the grid edge, as ruled Q4). Max |per-fold - pooled| = 0.20 nats (builder said <= 0.25).
- E: what "fold k" means in the tsv. Fit code at bench_b 43ebf79: `w1read.assemble` sets fold_of[stem] = r.fold of the run that dumped it; `crossfit_biases` fits fold k on `[f for f in cache if f != k]`. fit.json inputs: row (s, k) <- run w1g_pf_v11_f{k}_s{s}, dump manifest split_def = roots/cv5v2_v11_f{k}, split_md5 = md5 of that root's train.txt.
- E: per fold, from the 20 dump manifests and the root lists: cells held out by the fold-k runs == cv5v2_v11_fk/splits/test.txt; cells used to fit b_k (held out by folds != k) intersect test_k in **0** cells and are a subset of train_k; train_k and test_k disjoint. So no fold-k label enters o^(k) directly.
- E: key -> fold. md5 of cv5v2_v11_f{0..4}/splits/train.txt = 96d3154c, 19e4a606, 56d43036, b65ff0f2, c57b0b94 = the card's keys in fold order, = ROOTS_cv5v2_v11.md5, = the W1-G config roots and the 61 bq/w2a jobs' roots. The loader trains on exactly root/splits/train.txt when labeled_fraction = 1.0 (train.py l.414-415), the file whose md5 is taken (l.145).
- E: real path (scripts/train.py, CPU, 3 steps): fold 0 run logged `LA_CE ... row train.txt md5 96d3154c...` with the fold-0 row; fold 3 run the fold-3 row (both equal to my recomputation).
- E: fail closed. Resolver over all 100 splits/train.txt under /home/noob (depth 6) plus the LOSO-2 and cv5v3 roots: cv5v3_v11_f0..4 (bench_data_v3b and both review copies) and cvloso2_v11_f0/f1 all raise; the real train.py run on cv5v3_v11_f0 died with `ValueError: ... no row ... (md5 d7069b34...)` before step 1. Missing root -> FileNotFoundError.
- Note N1 (S, not blocking, the lead's Q1 ruling covers it): b_k is fitted on fold-j predictions (j != k) of models f_j that were trained with fold-k labels, so fold-k labels reach o^(k) at second order, through 11 scalars on a 0.25 grid averaged over 4 seeds. OP-C (the comparator) has the same dependence, so the contrast is symmetric. A leak-free version would need nested fits; not available and not needed under the ruling.
- Note N2 (E): the key is the split, not the root. cv5v2_v1_f0..4, b6/b6_root_0 and _4 and runner_b6deploy/el_b6/b6_roots/b6_root_0 and _4 have the same train.txt md5 as cv5v2_v11 folds and resolve. None of them has masks_v11 (E), so the card's data.mask_subdir=masks_v11 cannot train on them (S: the loader fails), and any of them would train on the same cell list anyway, so no leak.

## 2. Flag-off identity: PASS
- E, my own real-path check (not identity_cpu.py, which calls build_losses directly and so skips train.py main, where resolve_logit_offset now sits): scripts/train.py --device cpu on cv5v2_v11_f0, house_r34_unetpp_pf_v11, seed 5, 3 steps, checkpoint at step 3, fresh archives c57508e vs 73540e7. latest.pth: model, optimizer, scheduler and every other key equal by sha256 except cfg.run_name and trainer.train_time / train_curve.steps_per_sec (timing); per-step loss lines equal (4.204, 4.172, 4.126); train.log equal apart from time stamps, run name and speed; config_used.yaml equal; no LA_CE line.
- E, builder's identity_cpu lanes (run.log, 5 steps, ref c57508e vs a git archive of 73540e7) at 17:59: IDENTICAL for PFV11, HV11, PFV1, HV1, SBJ, JMLH, EMA, SWAD; RCS and SPD still running; render check, cfgcheck of W1-G / wave 2a configs, full pytest and smokes not yet logged. encoder_spd_ctrl_pf_v11 (1 job in w2a, w2a2) is not in the list (S: identical by construction, below).
- S, by construction: with no key, CEDiceLoss gets no buffer (a plain None attribute), forward takes the original line unchanged, the factory passes no kwarg and the two new checks are false, resolve_logit_offset returns the same dict object without reading any file; no random draw added. This holds for every card, not only ce_dice ones.

## 3. Loss correctness: PASS (two notes)
- E (read + tests): CE(z + o, y) with o broadcast (1, C, 1, 1) on CE only; Dice and prob use softmax(z); ignore 255: valid mask unchanged, CE ignore_index=255; fp32 (logits.float() + fp32 buffer, fine under bf16 autocast); buffer non-persistent (state_dict and checkpoints unchanged) and moved by train.py's `.to(device)`; numel checked against the class dim; finite check.
- Sign (S, checked by test 7 which I ran and mutated): post-hoc OP-C is argmax(z_PF + b); training on CE(z + o) drives z + o towards calibrated logits, so z = calibrated - o = calibrated + b with o = -b. A sign-flipped mutant fails 3 of 9 tests (E).
- E: other consumers. bench_infer.py builds only cfg["model"]; EMA / SWAD / BN readouts (wavg) use weights only; best.pth selection uses val defect_miou of argmax(z). Nothing reads the buffer or the key except the loss.
- E: real path, flag on: step-1 loss 4.057 (f0) and 4.050 (f3) vs PF 4.204, finite, 3 steps each, no traceback.
- Note N3 (E): val loss logged at val_every (evaluator criterion = sup_criterion) includes the offset; logged only, it decides nothing.
- Note N4 (S, for reading the result, not a defect): the inactive Dice term (dice_classes 14, 11, weight 1) works on softmax(z); where CE(z + o) inflates p_11 by up to e^4 on non-inactive px, the batch Dice pushes it back down, and per px its gradient is much larger than the CE term's. The learned inactive shift may be far below 4 nats. An inactive null of la_ce may come from this design (the spec's "CE term only"), not from the idea.
- S: memory: one extra transient (8, 24, 512, 512) fp32 tensor, about 200 MB; the 11,000 MiB default gate is ample (PF peak 6,830).

## 4. Card and cfgcheck: PASS
- E: `diff` (comments dropped) of la_ce_pf_v11.yaml vs house_r34_unetpp_pf_v11.yaml: name, papers, the 5 table opts, memory block (peak null, gate 11000), diff_ref, notes. Training opts otherwise identical. `cards.validate` = []. Opts render with no spaces inside the lists (bench_q word-splits).
- E: the table survives cfgcheck: config_used.yaml of my real fold-0 flag-on run, `bench.cards cfgcheck` vs the card: only my 5 smoke overrides differ (checkpoint_every, log_every, num_workers, total_steps, val_every); the 5 md5 keys load back as strings with the same lists. config_used.yaml is written before the row is picked and cfg["loss"] is not changed by the resolver (E, test 6 and code).
- Note N5 (S): on a root with no row, bench_q's live check (cfgcheck + 'Labelled:' line) passes and the run then dies at the loss build; the queue records rc != 0 for that job. No wrong training can happen. Round 2 queue: check the roots anyway.

## 5. Tests: PASS (one gap)
- E: tests/test_w2b_la_ce.py 9 passed on my archive. Full suite at 73540e7: 456 passed, 4 skipped; at c57508e: 446 passed, 4 skipped; the 10 extra = the 9 new tests + test_card_model_builds_on_cpu[la_ce_pf_v11.yaml] (collect-only diff).
- E, mutation: Dice on z + o -> 1 failure; sign flip -> 3 failures; **resolver that ignores the md5 and returns the first row (after the fail-closed check) -> 9 of 9 pass**. Gap N6: test_resolver_picks_the_fold_row puts the matching row first in the dict. The code itself is right (`table[h]`, and E above on folds 0 and 3), so not blocking; a one-line fix is to put the matching row second (or test two roots).

## Not verified
- Any GPU run (bf16 autocast on CUDA, memory peak); a full 20,000-step run.
- The builder's remaining lanes (RCS, SPD identity; render check; cfgcheck of W1-G and wave 2a configs; full pytest; smokes) were not finished at 17:59.
- The classbias fit itself beyond its fold bookkeeping (reviewed in REVIEW_STAGEB.md).
- Round 2 items: layered_ci, the gaint queue files, the pre-registered reads, LAUNCH_REQUEST_w2b.md, the current run_w2b_check.sh (2407c83b) and the new harness/w2b files (dump_compare.py, lci_pathfinder_check.py, make_w2b.py).

---

# Round 2: layered_ci code, the la_ce changes since 73540e7, cards, queues, smoke and pathfinder (17 Nov 2026, 19:06 to 19:28 IST)

Scope (lead 19:06): everything except the pre-registered reads (READ_PLAN_w2b.md, run_read_w2b.sh, w2b_verdict*.py, w2b_counts.py, test_run_read_w2b.sh: round 3). Same limits as round 1: CPU only, nice 19, at most 8 threads; nothing started on a GPU; nothing changed in the builder's worktree or harness files; my archives and dumps lived in the scratch dir and are removed; no process of mine is left (9 recorded PIDs over both rounds, all gone, E). Own evidence (scripts, logs, outputs; no checkpoints): /home/noob/work/bench_reads/w2b_review/r2/.

## Object and pins (E, 19:27)
- **Branch HEAD moved during the review.** At 19:06 the lead's message and the request named 5995379. At 19:07 the builder committed **f678381** (my N6 test, `git diff --stat 5995379 f678381` = tests/test_w2b_la_ce.py only, +17). Between 19:07 and 19:09 he re-cut the 4 launch.sh files, REPO_MD5.txt and the request. I sent you a heads-up at 19:07. This verdict is for **f678381** (`git status --porcelain -uno` = 0 lines).
- REPO_MD5.txt **647b6245** (17 files; `md5sum -c` OK on the worktree and on my own git archive of f678381). The 17 file md5s are as in the lead's list, except tests/test_w2b_la_ce.py **c4feb0c6** (was c508a620).
- Queue copies in harness/w2b/bq_local, as reviewed:
  - jobs.txt: smoke 973308a9, lcipath 06752167, lace f89627eb, lci cd7d1c9d.
  - dump/jobs.txt: lcipath b798b2a6, lace 3759e824, lci 135778ff.
  - launch.sh (DEPLOY f678381b...): smoke **cf438b5a**, lcipath **66fbf7f7**, lace **34b4e0de**, lci **3b63508b**. These equal the PINs in the request's steps 2 to 5.
  - MAXC: 1, 1, 2, 2; dump MAXC 1.
- Harness scripts in scope: lci_pathfinder_check.py ec96c6e8, w2b_armcheck.sh ec809a7b, make_w2b.py d73386e3, run_w2b_check.sh 2407c83b, dump_compare.py eb515ae4, layered_dump_shim_test.sh 579e01a4.
- Request: content reviewed at 026f6f8e / **8c2f841d** (19:27). harness MD5.txt **79e78e11** (33 lines; `md5sum -c` OK at 19:26). Both still change as round-3 files are added. Re-run step 0 at launch.

## Blocking findings
None.

## 1. Flag-off identity: PASS
All checks below are E, on fresh git archives of c57508e and f678381.
- **Real-path train.py**, CPU, cv5v2_v11_f0, seed 5, 3 steps, checkpoint at 3, exit:
  - **PF v1.1** and **soft_band_jml** (an x2 card, whose aux-target code path in train.py changed): every model, optimizer and scheduler tensor in latest.pth is sha256-equal between c57508e and f678381. Only cfg.run_name, train_time and train_curve.steps_per_sec differ.
  - Loss lines equal (PF 4.204 / 4.172 / 4.126; SBJ 4.205 / 4.172 / 4.131); train.log equal apart from stamps; config_used.yaml equal.
- **Dump writer, flag off.** I dumped W1-G w1g_pf_v11_f0_s5 (trained) with the c57508e and the f678381 bench_infer, PF card, CPU fp32, cv5v2_f0:
  - **642 of 642 arrays equal** (107 cells x pred, oth, m_crack, p_crack, p_inact, format) and every cell md5 equal.
  - The manifests differ only in code_repo, writer and written; decision_rule is argmax24 on both and there is no decision_t_I.
- **Render**: all 14 cards of c57508e, seeds 5 and 6, five cv5v2_v11 roots: **140 of 140** rendered configs md5-equal at ref and new; card files equal.
- **cfgcheck at f678381** of existing run configs: W1-G + W1-G2 **20 of 20**, wave 2a (bq/w2a/jobs.txt) **61 of 61**.
- **Full pytest at f678381**: **471 passed, 4 skipped** (c57508e: 446). The two w2b test files: 23 passed.
- S, by construction: with none of the keys `model.aux_heads`, `data.aux_targets`, `loss.aux`, `eval.decision`, `--decision`, `extra=`:
  - build_model returns the bare core and build_losses adds no "aux";
  - train.py adds no builder, the trainer's aux branch and test rule are skipped, and check_layered_cfg is not called;
  - bench_infer takes the card's rule (argmax24) and the old run id;
  - write_cell writes the same keys.

## 2. layered_ci correctness against the spec (T10 Arm 3, WAVE3_REVIEW row, rulings): PASS
- **Target, own implementation (E).** I wrote my own version of the target: Euclidean disk r = 2, crack within reach of inactive, holes = 4-connected background components not touching the border, ignore re-applied. On all 532 P532 masks it gives **0 cells differing** from src inact_region_fill.
  - Crack px inside the target: 48,934 of 307,593 = **15.91%** (spec band 15 to 25%).
  - Only 48 of the 532 cells contain inactive; 12 contain ignore px.
- **Target placement (E, code).** The target is built in AuxTargetDataset on the mask after augmentation and the ignore mapping, and wraps only the labelled train dataset (train.py l.515-534). Val and test loaders are built without it (l.567-568).
- **Aux head (E).** In smp 0.5.0, SegmentationModel.forward is check_input_shape -> encoder -> decoder -> segmentation_head (classification_head None). AuxHeadModel repeats that and adds the head on the same d. The head is built inside fork_rng.
  - Unit test: core init, global RNG and z24 are bit-equal to the bare PF model at seed 5.
  - My real-path layered_ci run (f0, 3 steps): loss = loss_sup + loss_aux on every step line; the checkpoint holds the 350 core keys + aux_heads.inact_region.0.{weight,bias}; cfgcheck vs the card differs only in my 5 smoke overrides.
  - Against PF with the same seed and data after 3 steps: encoder 216/216 tensors equal (PF freeze = lr multiplier 0), decoder 110 tensors differ, head differs. So the aux loss trains the shared decoder, as the spec says (risk 4 of the spec, guarded by the crack guards).
- **Loss (E, tests + mutation).** BCE-with-logits mean over px != 255, plus batch soft Dice with +1 smoothing, in fp32 with autocast off, weight 1.0. A mutant that drops the ignore mask fails a test.
- **Decision (E, independent).** I built my own shim: W1-G f0 s5 weights + an aux head set to w11 - w0 with bias -1, so the layer is not trivial. I ran the 3 dumps with the f678381 bench_infer (card = replace, argmax24, union; CPU fp32).
  - I re-ran the forward myself and computed the spec's pseudo-code in numpy: **0 px mismatches** in pred for argmax24, replace and union, and 0 in oth (same rule on the 23 non-crack classes) over 107 x 262,144 px.
  - Crack px equal to argmax in 107/107 cells; p_inact = sigmoid(zI) in 107/107; p_inact_softmax = the argmax readout's p_inact in 107/107; every cell passes the writer check on read.
  - Manifests: decision_rule layered_ci_replace / argmax24 / layered_ci_union, decision_t_I 0.5 (absent on argmax24), run ids `<run>`, `<run>.argmax24`, `<run>.layered_ci_union`.
  - My shim's layer moved only 239 px, so I also ran decide() against my spec version in memory on the 107 real z24 with 2 random layers: A (replace) 31,923 px, B (write) 18.4 M px, **0 mismatches** in pred and oth for both rules, crack never changed.
- **Unit tests (E).** test_w2b_layered_ci.py: 13 pass. Mutants that the tests kill:
  - layer overwrites crack;
  - alt may pick crack;
  - replace step missing;
  - no hole fill;
  - reach radius 3;
  - head init from the global RNG;
  - ignore not masked.
  One mutant survived, but it adds 0 x head to z24 and is value-equivalent, so it is no gap.
- WAVE3_REVIEW row (FIX then GO): (1) within-model contrast = mechanism only, (2) comparator = PF at OP-C (K2), (3) proxy gate: these are read-plan items for round 3. (4) Shared head and decision module: built once (bench/decision.py, src/models/aux_heads.py).

## 3. Leakage: PASS
- E: only the labelled train dataset gets the target (above). bench_infer reads no mask. The decision uses model outputs only.
- lci_pathfinder_check C4 reads the strict fold-0 held-out masks, which is open data and not used to rank, as the spec says.
- No sealed list is touched: bench_infer's forbidden-list guard is unchanged.

## 4. Queues and gates on gaint: PASS (two notes)
- **Arm check (E, 19:13).** `w2b_armcheck.sh` on the 4 prepared copies gives 4 x `ARMCHECK PASS`. It covers: DEPLOY = HEAD f678381, 0 tracked changes, md5s of jobs and dump jobs, no experiments/<job>, card validate, weights md5, gates >= card gates, splits and SPLITS.md5, extra only on smoke_*, --bench-run on dumps.
- **My own cross-check of the job lines (E): all OK.**
  - Training jobs: 10 + 10 + 1; card, seed and fold root match the name; gate 11000; no extra except the 3 smoke lines (`--exit_after_step 200`).
  - Dump jobs: 10 la_ce (one per run); 30 + 3 layered (card, argmax24, union per run). Each one: --run = REPO/experiments/<run>, --set = the run's fold, method = card = the arm, run id per rule, `--weights-key model`, cuda fp32, gate 6200, no --logp, its own `--bench-run`.
- **Chain semantics (E).** bench_chain.sh writes `chain done` after phase 1 ends with `BENCH Q ALL DONE` even when smokes end with rc 3. Precedent: bq/w1g_smoke "0 rc 0 of 1 ... chain done". w2b_smoke has no dump dir, so it reaches "no jobs; chain done". So the pathfinder waiter fires.
  - The layered_ci screen's waiter is started by hand only after `PATHFINDER PASS` (request step 5).
- **Memory basis (E + S).**
  - GPU at 19:26: 32,623 MiB total; finllm 6206 at 5,876 MiB; it is in PROTECT (bench_lib.sh: never verified, stopped or counted as "outside").
  - The highest wave 2a peak is 7,154 MiB, run at MAXC 2 on gaint (w2a, w2a2 MAXC 2).
  - The 200-step smoke peak is representative: PF freeze is an lr multiplier, not requires_grad (trainer l.110), and the W1-G smoke 6,826 equals the real runs' 6,830.
  - S: two layered or la_ce runs (about 7.2 GB each) + the layered final-test transient (about 0.6 to 0.8 GB) + finllm ≈ 21 GB of 32.6. The 11,000 MiB start gate holds a second start until about 19.7 GB is free.
- **Pathfinder criteria C1 to C4 (READ_PLAN s3) are implemented as written (E, read + dry run).**
  - C1: every step line finite in loss, loss_sup and loss_aux; last line 20000; latest.pth step 20000. The parser works on a real layered train.log, and W1-G logs have no other `step N/M` lines.
  - C2: steps/s at step 200, layered smoke >= PF smoke / 1.15.
  - C3: gpumem peak, layered smoke <= PF smoke + 1,024 MiB. The run_name=<name>:<MiB> format matches bq gpumem.log.
  - C4: pooled Dice of p_inact > 0.5 vs the target from the strict mask, >= 0.3. It asserts decision_rule, step 20000 and fold 0.
  - Dry run on my shim dump: C1 to C3 OPEN (inputs absent), so `PATHFINDER NOT PASSED`. It fails closed.
- **Stop paths (S).** Unchanged mechanisms reviewed in wave 2a: NOSTART for a waiter, HOLD for a queue, a running job only via pids/<name>.pid with owner and cmdline verification. Disk 100 GB free (E, 19:26) against about 17 GB needed (S, builder).

## Notes (not blocking)
- **R2-N1 (E):** HEAD and pins moved mid-review (above). The request and harness MD5.txt are still changing (round-3 files). At launch, do step 0 against the then-current md5s; my verdict holds for the md5s pinned above.
- **R2-N2 (S, procedural; it affects C2):** request step 2 arms the w2b smoke with `PREV=$B/w2a3`, but your 19:06 order puts the c3x smoke (bq/c3x_smoke, a bench_q queue with chain.log) in between. With PREV=w2a3 both arm when w2a3 ends. The outside-process rule serializes job starts, but if a c3x job runs during one of the two w2b smokes and not the other, the C2 step-time ratio is confounded. C3 is per-process and is not affected. Use `PREV=$B/c3x_smoke`, and check in launch.log that no outside process overlapped the PF and layered smokes.
- **R2-N3 (E/S):** C4 is a low floor. My shim layer, which only restates the softmax inactive decision (z11 - z0 - 1), scores 0.5245 on fold 0. A C4 PASS shows the layer learned the region, not that it adds anything over the softmax. That is what the between-model reads must show.
- **R2-N4 (S, for round 3):** in the replace and union dumps p_inact = sigmoid(layer); the softmax score is in p_inact_softmax and in the argmax24 readout. Any read tool that uses p_inact from those dumps (thresholds, score-based region readouts, OP-C fits) reads the layer. I will check the read path in round 3.
- **R2-N5 (S):** the aux target is positive in few batches (48 of 532 cells have inactive). In the other batches the batch Dice term pulls the layer to 0. This is a design property, not a defect.
- **R2-N6 (S):** the trainer's final-test layered rule (metrics.json only) clones the 24 logits about 3 times at eval batch 8. The 200-step smoke does not see this (no test), so C3 does not cover it. It is far from the limit (R2-N2 arithmetic in section 4).
- **R2-N7 (S, minor):** check_layered_cfg does not refuse EMA or SWAD with aux heads; a deepcopy of AuxHeadModel after a forward would hit non-leaf tensors in aux_out. This card cannot reach it; refuse it if a later card combines them.

## Not verified (round 2)
- No GPU run: peaks, step time and the pathfinder itself are measured only by the smoke and the pathfinder.
- The trainer's final-test path with the layered rule: my CPU runs exited at step 3, before val and test. The builder's 5-step smokes ran it (his E). It writes metrics.json only.
- The pre-existing c57508e writer tie on untrained models (builder's finding): not reproduced by me.
- bench_setup.sh, bench_q.sh and bench_chain.sh themselves: unchanged since c57508e; I relied on the builder's arm-check replica plus my own job-line checks.
- Everything in round 3 (READ_PLAN_w2b.md 3f38d910, run_read_w2b.sh 8d644288, w2b_counts.py a23dd544, w2b_verdict*.py, test_run_read_w2b.sh).

---

# Round 3 (folded into round 2; one verdict for the whole set): the pre-registered reads (17 Nov 2026, 19:29 to 19:36 IST)

Scope (lead 19:18): READ_PLAN_w2b.md and the read tools, checked against the rulings in log.md "17 Nov 17:33" (Q1 to Q7), "18:00" (la_ce_full follow-up) and "19:06" (K0 to K4, Q6 restated). Same limits as before. Builder tests were re-run on a scratch copy of harness/w2b, with the test temp dir moved to my scratch. One shim layered dump was made in scratch and read with the old read tree. All of it is removed now. Evidence: /home/noob/work/bench_reads/w2b_review/r3/.

## Pins (E, 19:36; unchanged since the lead's 19:18 check)
- **Harness:** LAUNCH_REQUEST_w2b.md **8c2f841d**, w2b/MD5.txt **79e78e11** (`md5sum -c` OK), REPO_MD5.txt **647b6245**.
- **Read tools:** READ_PLAN_w2b.md **3f38d910**, run_read_w2b.sh **8d644288**, w2b_verdict.py **1ace40f7**, w2b_counts.py **a23dd544**.
- **Tests:** w2b_verdict_test.py **23b16576**, w2b_verdict_shape_test.py **56ad06a1**, test_run_read_w2b.sh **e60c4695**, test_w2b_counts.py **78f16810**.
- **State:** bench_wt_w2b HEAD f678381, 0 tracked changes, no bq/w2b* placed. The read tree bench_wt_b is at b5bf0ae, clean, bench_read_w1.py fdb56b78.
- **Queue launch.sh re-pinned to DEPLOY f678381:** cf438b5a, 66fbf7f7, 34b4e0de, 3b63508b (= the request's PINs); my arm check at 19:13 gave 4 of 4 PASS (round 2).

## Blocking findings
None.

## 1. Verdict rules against the rulings: PASS
I read w2b_verdict.py line by line against the rulings.

**la_ce**
- **P1 / P2:** `delta >= M and lo > 0`. They take the 532 margin from read.json "M" and the 416 margin from "x416"."M". M = max(0.01, 2 SE of the A/A) of bench_read_w1.
- **G1:** LACE - PF strict crack IoU and relF1@2 >= -M, at OP-A and OP-W, on the 532 cells; the 416 values are printed only.
- **G2:** inactive IoU LACE - PFC >= -M_inact.
- **G3:** every R13 class (crack and background included) >= -0.03.
- **G4:** each FREE class's pred/GT area within [0.85, 1.15] x PFC's. PFC 0 gives inf, so the line fails.
- **G5:** each FREE class's px on cells without it <= 1.5 x PFC's. PFC 0 means LACE must be 0.
- **Outcomes:** DROP if the P1 point <= 0 on either cell set or any G1 line fails. Otherwise PROMOTE if P1, P2 (both sets) and every G line pass. Otherwise PARK. Precedence: DROP before PROMOTE.

**layered_ci**
- **L1:** R1 LCI - PFC `delta > 0 and lo > 0` on 532 and 416.
- **L2:** R2 <= 1.15 x PFC.
- **L3:** R3 delta >= -0.02.
- **L4:** R4 ratio in [0.85, 1.15].
- **L5:** R5 delta > 0.
- **L6:** paired R5 LCI - LCIARG > 0.
- **L7:** crack IoU and relF1@2 vs PF at OP-A and OP-W; width pooled and for ARTS, BMRK, CFVS, CSIR; false crack px <= 1.5 x PF.
- **Outcomes:** DROP on L6, R5 < 0 or any L7 line. PROMOTE on L1 (both sets) plus L2 to L7. Otherwise PARK.

All of this equals READ_PLAN sections 1 and 2 and the restated Q6, including G5's 1.5 x PFC (not 1.15) and the 532 AND 416 condition for P1, P2 and L1.

Further checks:
- **Tests (E):** w2b_verdict_test.py 43 of 43. The cases cover every element at and beside its boundary (M, -M, 1.15, 0.85, 1.5, -0.03, -0.02, point 0), the precedence (drop wins), guards judged on 532 only, and the 416 condition.
- **Shape test (E):** w2b_verdict_shape_test.py PASS on the real w2a read.json and counts JSON. The keys used exist: contrasts "B - A", metrics miou_rob / crack_iou / relF1_2 / inact_iou, M and x416.M, and summary per source with width_ratio and fa_px.
- **miou_rob is mIoU-R13 (E):** crossfit_op.fmetrics takes the mean IoU over ROB13 = R13.
- **Margins per cell set (E, from the finished w2a read, which uses the same PFAA arms, cells, groups and bootstrap seed 0, so the w2b read reproduces them):** M mIoU-R13 = 0.010 on both 532 and 416 (A/A SE 0.0032 / 0.0034); M_inact = 0.0543 on 532 (the 0.054 of the rulings), 0.0597 on 416 (no element uses it); crack 0.010 / 0.010. So the read's M equals the rulings' fixed 0.010 on both sets, and the guards use the 532 margins as ruled.

## 2. Count tool: PASS
- w2b_counts.py reads only the finished read's argmax records (cache) and read.json. No dump and no label is read.
- **R1 to R5:** R1 = GT components >= 100 px with >= 50% predicted inactive; R2 = predicted inactive px on cells without GT inactive; R3 / R4 / R5 pooled. Per-class columns: IoU, pred/GT, and px on cells without the class.
- **Bootstrap:** two-stage group bootstrap as crossfit_op.boot_pair (330 groups with replacement, then one seed per fold; `:paired` uses the same seed for both readouts), 2,000 draws, seed 0.
- **Fail-loud checks:** the 416 set via --exclude; the groups md5 is checked against the read's; every arm and seed must hold every stem.
- test_w2b_counts.py PASS (E, re-run): PF and RCS R5, R3, R1 equal bench_read_w1 to 6 dp, and the RCS - PF R5 delta and bounds to 4 dp.

## 3. run_read_w2b.sh: PASS (cannot mix machines, cannot read an incomplete arm)
- **Pins:** read tree b5bf0ae, clean, fdb56b78; score_exclude_v3 6d48dfbd; full md5 of w2b_counts.py and w2b_verdict.py; the arm's dump jobs.txt md5 (lace 3759e824, lci 135778ff = the queue files).
- **Completeness:** each of the 10 or 30 expected dump jobs must appear exactly once in dump/jobs.txt, its last `] trained <job> rc=` line in dump/launch.log must be rc=0 (format E: bench_lib.sh l.67, real w2a lines), and a real, not symlinked, folder with a manifest must exist. Then bench_read_w1 itself checks the manifest (verify), that the dumped cells equal the set's stems, the stems md5, all 5 folds per seed and the same stems in every arm.
- **Manifests:** run id, fold, seed, weights key, step 20000, set, fp32, open set, code_commit f678381, decision rule (t_I 0.5 on layered readouts). PF: 31c0c36, fp32, seed and fold. PFC: derivation classbias_xfit (so OP-C2's classbias_xfit_v2 is refused), fit_folds without its own fold, rule argmax24_logp_plus_classbias_xfit.
- **One device over all dumps (E):** gaint dumps say "NVIDIA RTX PRO 4500 Blackwell" (W1-G, PFC, w2a), cv02's say "NVIDIA RTX A6000". Together with the fixed gaint paths (w1g, dumps_gaint, bench_dumps/w2b), a cv02 dump cannot enter.
- **No readout mixing (E):** discover uses `re.fullmatch` on run ids, so the LCI arm `w2b_lci_f[0-4]_s[56]` never picks up `<run>.argmax24` or `.layered_ci_union`. The pathfinder run (`w2b_lcipath_...`) cannot match either.
- **Fails closed:** an existing output folder is refused, and a refusal writes no folder. test_run_read_w2b.sh 20 of 20 (E, re-run): wrong ARM, existing output, changed tool, missing queue, missing or failed trained line, wrong commit, wrong rule, missing t_I, symlinked folder, changed jobs.txt; complete fixtures pass.
- **The old read tree on a real layered dump (E):** nobody had tested this. I made a shim layered_ci_replace dump with the f678381 bench_infer and loaded it with b5bf0ae code: w1read._load_run passed (manifest verify, stems, v11 GT). The 107 records from `_job("rec", argmax)` hold 24,762 inactive pred px, equal to the pred == 11 px of the dump files. The old check_cell requires the 5 keys and ignores the extra p_inact_softmax; bench_read_w1, w1read and crossfit_op never read p_inact.

## Notes (not blocking)
- **R2-N2 (still open):** request step 2 still arms the w2b smoke with `PREV=$B/w2a3` (line 108). Use `PREV=$B/c3x_smoke` per your 19:06 order, so that no outside job overlaps the two smokes whose step times C2 compares.
- **R3-N1 (S; needs your yes or no): the "either cell set" DROP clause.**
  - It is consistent with P1 having to hold on both sets, and it keeps a gain seen only on the leak-prone 532 cells from surviving as PARK.
  - Its cost: the mIoU-R13 contrast SE is about 0.0035 on either set (E, w2a), so a true effect of +0.005 gives a 416 point <= 0 about 8% of the time (S) and is then DROP instead of PARK.
  - It changes nothing about promotion. Since la_ce_full follows a null anyway (18:00), the stakes are low. If you keep it, it is fine as built.
- **R3-N2 (S):** verdict.txt does not mention la_ce_full. When la_ce ends DROP or PARK on a null primary, the ledger line should cite the 18:00 follow-up so the hypothesis is not closed on la_ce alone.
- **R3-N3 (S):** the PF4 sensitivity folder gets a verdict.txt with an ordinary "VERDICT ...: PROMOTE / DROP / PARK" line. The sensitivity marker is only in run.log and SENSITIVITY_PF4.txt. Read only w2b_<arm>/verdict.txt as the verdict, or have a later script prefix the PF4 verdict line.
- **R3-N4 (E):** the owed atlas read for FP-on-crack (READ_PLAN 2) uses p_inact (bench_wt_b atlas.py l.286, l.372). On LCI dumps that is the layer's sigmoid, not the softmax score. Point the atlas at the `.argmax24` readout, or map p_inact_softmax, depending on which question it answers.
- **R3-N5 (S):** NaN or null edges (a class with no GT and no prediction in a cell set) make the verdict crash or fail a line, never pass it. Realistic data cannot hit them on R13 over 532 or 416 cells.

## Not verified (round 3)
- No real w2b read exists yet: the verdict and count tools were exercised on synthetic cases and on the w2a read with renamed arms.
- bench_read_w1's internals (operating points, OP-W fit, bootstrap): reviewed in earlier waves, not re-derived here.
- The atlas FP-on-crack read: owed and not built.
