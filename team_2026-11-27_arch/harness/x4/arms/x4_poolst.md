# Arm x4_poolst: handover (builder pool, 28 Nov 2026)

E = measured, S = judgement. Full step log: harness/x4/arms/BUILD_pool.md.

## What the arm changes
COMBO (hrnet_w18_unetpp_swad_const_pf_v11) plus offline self-training on teacher pseudo-labels of the unlabelled pool. Nothing else changes: PF schedule, SWAD 10k to 20k, ema_9998, BN re-estimate, readouts, weights_key swad_bn; the x4 comparison uses the swad readout.
- Per step: the COMBO labelled batch (8 x 512, stream 0, unchanged) plus a separate forward of 8 pool crops (stream 5).
- Loss = ce_dice(labelled) + 1.0 x ce_dice(pool crops, pseudo-labels, 255 ignored). The pool forward updates the BN running statistics (bn train, as in Noisy Student and CSST; state arm_bn = train).
- Pool crops are 384 x 384 at native scale, with no resize, so 1 to 2 px cracks keep their width. They then get the label-safe ops: flips, rot90, brightness/contrast p 0.4, normalise.
- CSST sampler (doi:10.1109/tpami.2021.3138337): half of the pool slots (p_rare 0.5) are centred on a pixel of a thresholded pseudo component. The class is drawn uniformly from crack and inactive, then a component uniformly; components are 8-connected, with at least 10 px for crack and 100 px for inactive. The other slots are uniformly placed crops of uniformly drawn cells.
- Pseudo-label target = teacher argmax where the teacher confidence (uint8) >= round(255 x thr[argmax]), else 255. thr = 0.9 for every class, except 0.5 for inactive (rule below).
- Teacher of fold k: the mean softmax of the 5 cv5v3 COMBO fold-k runs (c3x_hrnet_swad_v11_f<k>_s5..9, slim.pth, key swad) over the 8 D4 views. It runs in fp32 with TF32 off.
  - The script asserts that every teacher's own held-out list has the same md5 as fold k's, so no teacher trained on a fold-k held-out cell.
  - It also asserts that no teacher train list holds a pool stem.
- Papers: CSST doi:10.1109/tpami.2021.3138337 (sampler; scout unsup #4). Ledger pool-distillation family (gate opened): P005 Naive-Student arXiv:2005.10266, P051 Zoph arXiv:2006.06882, P157 Data Distillation doi:10.1109/cvpr.2018.00433, P180 Noisy Student doi:10.1109/cvpr42600.2020.01070 (all in the card); also P080, P022, P014 (same family, not in the card). P034 mic_halfcell is not used here (it needs the half-cells).

## Pool list: lead's ruling (recorded as asked)
- **The student trains on pool_t9_v2.txt ONLY**: 4,949 cells (ARTS 1,497, CSIR 3,452), md5 39877edec7b3a1b1211aa9fcd6c5e95b, repo copy bench/pool_st/sub_v2.txt, key data.pool_st.sublist.
- **Reason (lead):** cv5v3 cannot measure a half-cut effect (P532 has 0 half-cut cells). Using pool_half would also burn H36/U4, our only remaining labelled half-cut check and the seed of a new unseen half-cut set.
- E, what was found:
  - The ruled 4,949 list has 0 half-cut cells. All 1,152 half-cells on disk (CSIR_00297 to 00301 and 00333 to 00335, 144 each) were removed from it by the module rule. Each of those modules holds labelled _rf cells (H36, F-set) or ext11 cells; CSIR_00300 also holds an E1 cell.
  - The half-cell list used before is /home/noob/work/bench_udev/sets/lists/pool_half.txt (943 cells, md5 a4752dbabfecc24a604c5af62f683b74, 7 modules, without CSIR_00300).
- E, leak checks: scripts/pool_st_lists.py checked both lists against module_identity_v3.tsv (both module rules, crossed; 116 E1/test50 physical modules, 119 image ids), against forbidden_v1 (9bb4d919) and against the 532 labelled cells. Result: 0 hits.
  - Per fold, 0 pool cells share a physical module with a fold-k held-out cell, so nothing is dropped per fold.
  - The 5,892 cv02 pool images match their gaint md5s.
- The pseudo-label folders cover lists_v1 = v2 + pool_half (5,892, all.txt bdec32b66c89142a0b5f7cf1a45cc874). The teachers had started on this list before the ruling. Their output is written only at the end, so a v2-only restart would have saved nothing. Computing teacher predictions on pool_half trains nothing.
- **Later variant x4_poolst_half** = this card without the data.pool_st.sublist line. It needs no new pseudo-labels; it is not built.

## Confidence threshold (fixed before any student trains; no held-out data)
- The rule was written in BUILD_pool.md at 27 Nov 23:37:24 IST; the histogram was first read at 28 Nov 02:55 IST. Global 0.9. A rare class (crack, inactive) gets its own value only if fewer than 50% of its argmax pixels survive 0.9. Its value is then the largest of 0.8 / 0.7 / 0.6 / 0.5 that keeps at least 50% (0.5 if none does).
- E (v2 stems x folds 0 to 3, pooled, 5.19e9 px; cv02 thr_hist.py 63aaddbd; array thr_hist_f0_f1_f2_f3.npy 1d76a77f):

| t | all px kept | argmax-crack kept | argmax-inactive kept |
|---|---|---|---|
| 0.5 | 0.994 | 0.971 | 0.492 |
| 0.7 | 0.947 | 0.788 | 0.404 |
| 0.8 | 0.915 | 0.684 | 0.366 |
| 0.9 | 0.870 | 0.552 | 0.313 |
| 0.968 | 0.804 | 0.408 | 0.266 |

- Result: crack keeps 55.2% at 0.9, so it stays at 0.9. Inactive is under 50% at every candidate, so it gets 0.5. Card: conf_thresh=0.9, conf_thresh_class=[[11,0.5]].
- Teacher argmax on the pool: crack 0.035% of px (90.9 px per cell; the labelled train share is 0.19%), inactive 0.046%.

## Code
- Branch x4_pool, HEAD **c7bfeb279d11564f9c08c0741140cbb4f92db307**. It is bench_x4 41c931d (miro merge) plus 4 commits: 0ff9196, 8951b1c, 561d203, c7bfeb2.
- Files:
  - src/data/pool_st.py (new): threshold, components, PoolSTDataset, PoolSTSampler, fold location and md5 checks, build_pool_st_stream.
  - src/trainers/trainer.py: pst_* attributes, _pst_loss, the stream hook in fit and _train_step; its own log keys loss_pst, pst_valid, pst_crack_px, pst_inact_px, pst_rare.
  - scripts/train.py: opt-in data.pool_st hook after cp. It writes pool_st_stats.json and a "POOLST:" log line.
  - scripts/pool_st_teacher.py and scripts/pool_st_lists.py.
  - bench/pool_st/lists_v1 (MD5.txt 8590db2f) and bench/pool_st/sub_v2.txt.
  - Card bench/methods/x4_poolst.yaml (md5 673f7c319ae5a67e863c90325023a0de) and bench/methods_cv02/x4_poolst.yaml (ddd5d2cc35291fb39ccb3cfa6de1336b; weights path only).
  - tests/test_pool_st.py, tests/test_x4_poolst_card.py.
- Card = COMBO + 15 data.pool_st keys. bench.cards diff lists exactly these keys; validate OK on both cards; cvcard OK (weights md5 e6bb005d on cv02).
- The values are opts-safe: card opts are space-joined unquoted, and yaml reads {14:10} as sexagesimal. So min_px is a list aligned with rare_classes, conf_thresh_class is [[class,thr]], and the pin must be 32-char hex (all validated).
- The run fails closed if:
  - INDEX.md5 differs from the pin, or no fold folder (or more than one) has the root's held-out md5;
  - any pseudo-label file differs from its fold's MD5.txt, or any pool image differs from lists_v1/images.md5;
  - a sublist stem has no pseudo-labels, or a pool stem is a labelled cell of the root;
  - the folder is a --limit smoke output.
- Deployed: cv02 /tmp/noob_el/bench_c7bfeb2 (CODE.md5 31f723ee79128755784d1f8dc5877bdc, 807 files, CV02_CODE_OK).

## Tests (E)
- tests/test_pool_st.py, 7 passed:
  - hand values for the threshold and the opts forms (the sexagesimal trap is rejected);
  - 8-connected components and min_px;
  - component crops centred at native scale, deterministic under the stream seed;
  - sampler: rare share, class-uniform draw, exact resume at start_batch, seed dependence;
  - _pst_loss: shape, gradient, frozen versus train BN, equal to the criterion;
  - end-to-end stream: pin, wrong pin, wrong fold, tampered file, sublist.
- tests/test_x4_poolst_card.py, 2 passed.
- Together with test_x4_miro, test_f2_cp, test_rcs and test_bench_cards*: all pass except test_bench_cards_cv02::test_variants_exist. That one also fails on a clean archive of the base (pre-existing). Full suite at 642a70e: 771 passed, 2 failed, both pre-existing.

## Identity (E): IDENTICAL
- Strong form: scripts/thin/identity_cpu.py on clean archives of 41c931d vs 561d203 (c7bfeb2 adds only the card and its test). COMBO card opts, seed 5, cv5v3_v11_f0, 5 CPU steps, fp32.
  - 109 fields equal: exact loss repr, lrs, the sha256 of every parameter and buffer per step, and the eval logits sha256. Only the code path and seconds are excluded.
  - Records: /home/noob/work/builder_scratch/pool/idcpu_{base,new}.json.
- Stdout form: train.py with log_every 1, --exit_after_step 5, x4_idcheck.py. 25 values, 0 differ; PF encoder lines identical. Run on 399f963 vs 642a70e and again on 41c931d vs 561d203.

## Keys-on checks (E, CPU, not a GPU smoke)
- gaint, train.py, fold 0, the arm's values, real f0 pseudo-labels from the backup, 3 steps:
  - startup 26 s; components crack 2,258 in 541 cells, inactive 143 in 67 cells; valid px 0.876;
  - loss_pst 4.16 to 4.22; pst_rare 0.375 / 0.625 / 0.25;
  - labelled loss_sup at step 3 is 4.176 (keys-off 4.1768: the labelled stream is unchanged).
- cv02, the real cv02 card on every fold root, stream built and one batch drawn: STREAM_CHECK_OK.
  - Each fold is found by its held-out md5; 4,949 cells each (sublist md5 39877ede).
  - Components per fold: crack 2,189 to 2,281, inactive 143 to 177; valid px 0.844 to 0.882.
  - Batch (8, 1, 384, 384); build 39 to 52 s per root.

## Memory
- Not measured on a GPU, per the lead: the integrator runs the 200-step smoke in x4_w1. The arm adds a second forward on the pool batch, so the smoke is needed.
- S: COMBO peaks at 9,386 MiB. The pool forward (8 x 384 x 384 = 0.5625 x the labelled px) is held to the same backward, so I estimate about +4.5 to 5 GiB, giving about 14 to 14.5k MiB.
- The card has peak null and a provisional gate_mib of 17,000. Use @<measured peak> in x4_make_jobs (gate = max(17,000, peak + 2,048)), or lower the card gate after the smoke.
- S, step time: about 1.4 to 1.6x COMBO, from the extra forward and backward on 56% of the px.

## Precomputed input: pseudo-labels (E)
- cv02 /tmp/noob_el/pool_st/pl_v1/f0..f4: per cell lbl, conf, pcrack PNG, plus manifest.json, cells.tsv, hist_cls_conf.npy, MD5.txt. 17,679 files and about 255 MB per fold.
- **INDEX.md5 md5 bf24d7206072e98a36b12f05898db9e5** (the card pin). Per-fold MD5.txt md5s: f0 0cadc27e, f1 fa706b72, f2 b704b6de, f3 26e884da, f4 8d4b51f8.
- Every fold's manifest: n 5,892, fold k, held-out md5 = fold k (79816ba6 / 548af76f / ec7df8fd / b61a2d6f / 2f7c5a7c), teachers seeds 5 to 9 with checkpoint md5s, revision 642a70e, limit None, D4, fp32.
- Made by scripts/pool_st_teacher.py (at 642a70e; unchanged since) through cv02 /tmp/noob_el/pool_st/pl_launch.sh (lane rule; one teacher per GPU after the lead's update; PIDs in pids/). The teacher peak was 4,900 MiB, at 8,372 to 13,191 s per fold.
- **cv02 /tmp is wiped on reboot.** Backup on gaint: /home/noob/work/bench_x4pool_io/pl_v1 (1.4 GB, all 5 folds plus INDEX.md5, md5sum -c OK, INDEX md5 equal). After a reboot, copy it back to /tmp/noob_el/pool_st/pl_v1 and check `md5sum -c` per fold; the pin then holds. Also needed on cv02: /tmp/noob_el/el_p7/data/unlabeled/images_512 (the run checks the 4,949 image md5s at start).
- Logs and scripts: /home/noob/work/bench_x4pool_io/cv02_pool_st_meta.
- Incident (my error; no data effect): pl_launch.sh was rewritten in place while the wrappers of f0, f1 and f4 were running. After each teacher exited, the wrapper ran a stray line: a python relaunch that refused at once, or a "dir" error. This overwrote f0, f1 and f4 .log/.pid/.rc with rc 1 or 2. The teacher outputs are complete and verified (MD5.txt and manifests above).

## Jobs (x4_make_jobs.py; PEAK from the x4_w1 smoke)
Stage P (seed 5, 5 folds):

    python x4_make_jobs.py --out jobs/<qn>.tsv --repo /home/noob/work/bench_wt_x4_pool --seeds 5 --commit c7bfeb279d11564f9c08c0741140cbb4f92db307 bench/methods/x4_poolst.yaml=poolst@<PEAK>

Stage S (add seed 6): the same command with --seeds 6.
Memory smoke (x4_w1): the same command with --seeds 5 --folds 0 --extra "--exit_after_step 200" and @15000 (a gate guess, giving a gate of 17,048).
The card has a swad readout, so the 10th field is swad; the comparator is COMBO's swad readout.

## Open points (S)
- The teacher puts crack on only 0.035% of pool px, against 0.19% in labelled train. Most pool cells are crack-free under the teacher. The rare-class crops (crack components in about 530 of 4,949 cells per fold) carry the crack signal; the uniform crops mostly teach background on low-contrast CSIR/ARTS cells. Watch the crack width and the false-crack guards.
- The pool is 70% CSIR and holds no CFVS, BMRK or SDLE, so any gain should show mostly on CSIR and ARTS.
- The pool holds near-duplicate cells under different image ids (e.g. ARTS_00014 and ARTS_00027 rows give identical teacher stats). They share no module with an evaluation set; they only weight some cells twice.
