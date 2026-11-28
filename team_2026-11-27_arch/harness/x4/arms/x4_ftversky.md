# x4_ftversky: focal Tversky loss on crack (builder loss)

## What it changes
The crack Dice term of the house CE + Dice is replaced by the focal Tversky loss (Abraham and Khan, ISBI 2019, doi:10.1109/isbi.2019.8759329): TI = (TP + s) / (TP + 0.7 FN + 0.3 FP + s), FTL = (1 - TI) ** 0.75 (their 1 / gamma with gamma 4/3); TP, FN, FP are sums over the whole batch of soft crack probabilities (as the house Dice), ignore px excluded, s = 0.5. CE and the inactive Dice term unchanged, mean of the Dice-type terms and dice_weight as the house.
- s = 0.5 makes FN = FP = 0.5 with exponent 1 equal the house Dice term exactly (unit test), so the arm changes only the recall weighting and the focal exponent.
- Not used (S): their deep supervision with FTL on intermediate outputs and TL on the last (architecture-specific, not in COMBO).
- Keys: loss.ftversky.{enabled=true, cls=14, fn_weight=0.7, fp_weight=0.3, gamma=0.75, smooth=0.5}. Log: 'thin loss_ftversky=...' lines.
- Code: src/losses/x4_losses.py (CEFocalTverskyLoss), src/losses/loss_factory.py.
- Precomputed inputs: none. Run time (S): as COMBO.

## Common
- Branch x4_loss, worktree /home/noob/work/bench_wt_x4_loss, commit c9b93d8320504394a2d5418719f3a4a1bc85099d (arms 1 to 3 in 092026f, arm 4 in c9b93d8; both on bench_x4 41c931d, miro merged; merge is a fast-forward of bench_x4). cv02 deploy /tmp/noob_el/bench_c9b93d8 (CODE.md5 checked, CV02_CODE_OK). Queue calls need X4=c9b93d8320504394a2d5418719f3a4a1bc85099d and --repo /home/noob/work/bench_wt_x4_loss for x4_make_jobs.py (the card lives only on this branch).
- Comparator: COMBO card hrnet_w18_unetpp_swad_const_pf_v11; this arm = COMBO + exactly the keys listed (bench.cards diff and tests/test_x4_loss_cards.py). Readouts as COMBO; compare the swad readout with COMBO's swad readout.
- Identity (keys off), E: 5 CPU steps (identity_cpu.py 962379a6 / compare_id.py 3b83b364), seed 5, cv5v3_v11_f0, fresh git archive of bench_x4 41c931d vs c9b93d8: COMBO card opts IDENTICAL; x4_miro card opts IDENTICAL (the merged arm is unchanged by this branch). Earlier rounds: 23717a7 vs 34cca2f (arms 1-3) IDENTICAL; 399f963 vs ec3562e (arms 1-4) IDENTICAL. Logs: /home/noob/work/bench_x4loss_io/check{,2,3}/run.log.
- Unit tests, E: tests/test_x4_loss.py (shape, gradient, hand-computed values; factory and trainer with keys off unchanged), tests/test_x4_loss_cards.py. Full pytest at c9b93d8: 804 passed, 12 skipped, 2 failed (test_variants_exist and test_shv_reproduces_shv1_on_real_val_cells; both fail identically on 41c931d: pre-existing / data links of a fresh worktree).
- Peak and gate, E: no model or batch change: COMBO training peak 9,386 MiB on cv02, job gate 11,434 MiB (lead ruling: no smoke).
- Jobs (5 folds x seeds 5, 6), on gaint in harness/x4:
  `python x4_make_jobs.py --repo /home/noob/work/bench_wt_x4_loss --commit c9b93d8320504394a2d5418719f3a4a1bc85099d --out jobs/<file>.tsv bench/methods/x4_ftversky.yaml=ftv@9386`
  (10 lines x4_ftv_f0..4_s5,6, 11th field = deploy c9b93d8; gate = max(card gate 11,000, peak + 2,048)); then append to the shared cq_x4.sh queue (`X4=c9b93d8320504394a2d5418719f3a4a1bc85099d bash x4_queue.sh append <qn> jobs/<file>.tsv`) or place / arm a queue of its own as RUNBOOK section 2; relay and score as usual.
- Installs: none (house venv; scipy already present). Weights: the COMBO encoder file only (md5 e6bb005ddbe1b52bde05618fc6b4b8e3).
