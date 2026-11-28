# Handover: x4_dysample (builder res)

Builder res, 27 Nov 2026. E = measured, S = judgement. Code branch x4_res, worktree /home/noob/work/bench_wt_x4_res:
085b0d9 (code, tests, cards) + f2df856 (card memory fields only). Base bench_x4 399f963. Code: src/models/x4_res.py, 3-line hook
in src/models/bench_models.build_bench_smp (only when a model.x4_* key is present); tests/test_x4_res.py.

## Arm
- Card: bench/methods/x4_dysample.yaml (md5 dbb928200158fdb26029dadaae1dbb59), cv02 variant bench/methods_cv02/x4_dysample.yaml (md5 65e04368d53a8896eb1a420c04a5615e).
  = COMBO (hrnet_w18_unetpp_swad_const_pf_v11) + exactly `model.x4_upsampler=dysample`; readouts as COMBO; compare its swad readout with COMBO's.
- Paper: DySample, Liu et al., ICCV 2023, doi:10.1109/iccv51070.2023.00554; NEW per scouts/general (kept there as a control arm: unguided). Code: github.com/tiny-smart/dysample 81a1de5, dysample.py (MIT).
- What changes:
  Every one of the 11 U-Net++ DecoderBlocks upsamples with DySample+ (style lp, groups 4, dynamic scope: offset =
  conv1x1(x) * sigmoid(scope(x)) * 0.5 + init_pos, then grid_sample bilinear, border padding) instead of nearest x2. Unguided.
  Official init (offset std 0.001, scope 0): at step 0 the upsampler is bilinear (unit test: zero offset == F.interpolate bilinear).
  New params under decoder.blocks.*.up.*; init_pos is a non-persistent buffer.
  Deviation (S, numerics only): sampling grid and grid_sample run in fp32 with autocast off; in bf16 the normalised coordinate
  step near the border is about 1 px at 512 px. Variant choice (S): dynamic scope (DySample+) over the static 0.25 scope.

## Numbers
- Training peak (E, cv02 smoke, GPU 3): 8,972 MiB (COMBO in the same queue 8,638). Card peak_mib 9,720 (= smoke + 748, S);
  **gate 11,768 MiB**.
- Step speed (E, same GPU, interleaved, pure train step): best 3.022 steps/s = **0.92 x COMBO** (3.285).
  Smoke steps/s: 1.041 / 1.121 / 1.226 / 1.283 (GPU 3, different GPU from COMBO's; not comparable).
- Wall time per run (S): about 170 min (COMBO 155).
- Params / GFLOPs at 1x1x512x512: 20,982,412 (+186,720); 219.7 GFLOPs (grid_sample not counted) (COMBO 20,795,692 / 218.1).
- Dump (E): fp32 b8 max_reserved 2,990 MiB -> projected dump peak 3,946 MiB (S); dump gate 6,200 (default).

## Jobs (5 folds x seeds 5, 6; 10 lines; nothing launched)
In /home/yugma/mtp/research/team_2026-11-27_arch/harness/x4 (gaint):
    python x4_make_jobs.py --out jobs/<qn>.tsv --repo <tree at x4_res f2df856 or merged> bench/methods/x4_dysample.yaml=dysample
(the card carries peak_mib 9720, so no @PEAK is needed; gate = max(card gate, peak + 2,048) = 11768). Preview written by me with
--repo /home/noob/work/bench_wt_x4_res: /home/noob/work/bench_x4_res_io/jobs_preview/x4_dysample.tsv md5 274e57f5 (10 lines; first: x4_dysample_f0_s5|bench/methods/x4_dysample.yaml|5|/tmp/noob_el/bench_data_v3b/roots/cv5v3_v11_f0|0|11768|6200|0||swad).

## Note
Cheap. scouts/general expects gains mostly in region interiors (its own ADE20K table), so S: a control for the guided upsamplers rather than the main thin-line arm.

## Checks (common to the 5 res arms)
- Identity, keys off (E): IDENTICAL. COMBO card opts on gaint cv5v3_v11_f0, 5 CPU steps, ref = git archive 399f963 vs x4_res
  (identity_cpu.py 962379a6, compare_id.py 3b83b364; all fields except code / sec: losses, lr, sha256 of every param and buffer
  after each step, eval logits). Records /home/noob/work/bench_x4_res_io/check/COMBO_{ref,new}.json.
- Unit tests (E): tests/test_x4_res.py 16 passed; with tests/test_bench_cards.py 50 passed (CPU).
- 5-step CPU run of this card on cv5v3_v11_f0 (E): rc 0, Traceback 0, nan 0 (/home/noob/work/bench_x4_res_io/check/run.log).
- Card checks (E): bench.cards validate OK; cvcard.py OK (weights md5 e6bb005d on cv02 path); bench.cards diff vs COMBO = only
  the arm key. No install, no new weights (pretrained = COMBO's timm hrnet_w18.ms_aug_in1k, md5 e6bb005ddbe1b52bde05618fc6b4b8e3).
- No precomputed input.
- cv02 smoke (E): queue x4_ressmoke (harness/x4/jobs/ressmoke.tsv md5 d056f486), deploy /tmp/noob_el/bench_085b0d9 (CODE.md5
  af38e9e0), 200 steps each, lane rule live, LPG 1, python PIDs in the queue's pids/; COMBO card run in the same queue as the
  reference. All 6 rc 3 by design, 0 Tracebacks. Run dirs and .stdout removed after (gaint/cv02 logs kept: queue launch.log,
  gpumem.log). COMBO smoke peak 8,638 MiB vs its 25-run full-training peak 9,386 (+748): peak_mib in the card = smoke + 748 (S).
- Same-GPU speed (E): one process on cv02 GPU 5, 5 interleaved rounds x 15 timed steps per model, bf16, batch 8 x 512 px,
  Adam, cudnn deterministic, random input (pure train step, no data loading): COMBO best 3.285 steps/s. Ratio = arm / COMBO.
  Log /home/noob/work/bench_x4_res_io/speed_run2_out.txt. (A first non-interleaved run was disturbed by another user: 3.08 ->
  0.98 steps/s for COMBO within the run; discarded, kept as speed_run1_out.txt.)
- Dump memory (E): eval fp32, TF32 off, batch 8, no_grad on cv02 GPU 3: torch max_reserved; COMBO 2,988 MiB vs its measured
  dump peak 3,944 (+956 context). Projected dump peak = reserved + 956 (S).
- Wall time per 20k-step run (S): COMBO median 155 min on cv02; scaled by 1 / ratio as an upper bound (data loading, SWAD and
  BN re-estimation do not slow down with the model).
- Queue: the jobs below need a deploy of a commit that holds this card and src/models/x4_res.py (x4_res f2df856, or bench_x4
  after merging x4_res); run x4_make_jobs.py with --repo at that tree (default bench_wt_x4 only after the merge).
