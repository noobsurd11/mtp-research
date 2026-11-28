# Handover: x4_fade (builder res)

Builder res, 27 Nov 2026. E = measured, S = judgement. Code branch x4_res, worktree /home/noob/work/bench_wt_x4_res:
085b0d9 (code, tests, cards) + f2df856 (card memory fields only). Base bench_x4 399f963. Code: src/models/x4_res.py, 3-line hook
in src/models/bench_models.build_bench_smp (only when a model.x4_* key is present); tests/test_x4_res.py.

## Arm
- Card: bench/methods/x4_fade.yaml (md5 5aceff224def1c957f9133c5afd1a3d6), cv02 variant bench/methods_cv02/x4_fade.yaml (md5 b3693251ce20df54f3c6a9e0c0393ac4).
  = COMBO (hrnet_w18_unetpp_swad_const_pf_v11) + exactly `model.x4_upsampler=fade`; readouts as COMBO; compare its swad readout with COMBO's.
- Paper: FADE, Lu et al., IJCV 2024, doi:10.1007/s11263-024-02191-8 (ECCV 2022 arXiv:2207.10392); NEW per scouts/general (fit 4). Code: github.com/poppinace/fade e4de4db, pytorch_implementation/FADE_L2H.py (MIT).
- What changes:
  Every one of the 11 U-Net++ DecoderBlocks upsamples with FADE instead of nearest x2:
  out = gate * Aligner(en) + (1 - gate) * CARAFE(de, softmax(SemiShift(en, de))), gate = sigmoid(nearest-up(conv1x1(de))),
  up_kernel_size 5, embedding 64, content-encoder 3x3, xavier init (as upstream). de = the block's input, en = the guide:
  block x_<d>_<l> uses the encoder feature at its output resolution (stride 16/8/4/2: 512/256/128/64 ch); the last block x_0_4
  (stride 2 -> 1) uses the network input (1 channel, normalised), the only stride-1 signal. Then the block concatenates its skip
  as before. New params under decoder.blocks.*.up.* (full lr from step 0; PF unchanged).
  Deviations (S): (1) a 1x1 Aligner (the official Aligner class, commented out upstream because its hosts have equal widths) maps
  en to de's width for the gate term; (2) CARAFE is evaluated in the low-res sub-pixel layout (same sum; test: equal to the
  official CARAFE, float64, 1e-12); (3) FADE-lite not used.

## Numbers
- Training peak (E, cv02 smoke, GPU 2): 16,916 MiB (COMBO in the same queue 8,638). Card peak_mib 17,664 (= smoke + 748, S);
  **gate 19,712 MiB**.
- Step speed (E, same GPU, interleaved, pure train step): best 1.591 steps/s = **0.48 x COMBO** (3.285).
  Smoke steps/s: 0.755 / 0.826 / 0.820 / 0.824 at steps 50 / 100 / 150 / 200 (GPU 2; COMBO on the same GPU 1.571 / 1.61 / 1.502 / 1.484).
- Wall time per run (S): about 320 min (COMBO 155).
- Params / GFLOPs at 1x1x512x512: 21,998,890 (+1,203,198); 254.2 GFLOPs (+36.1) (COMBO 20,795,692 / 218.1).
- Dump (E): fp32 b8 max_reserved 6,752 MiB -> projected dump peak 7,708 MiB (S); dump gate 9,800.

## Jobs (5 folds x seeds 5, 6; 10 lines; nothing launched)
In /home/yugma/mtp/research/team_2026-11-27_arch/harness/x4 (gaint):
    python x4_make_jobs.py --out jobs/<qn>.tsv --repo <tree at x4_res f2df856 or merged> --dump-gate 9800 bench/methods/x4_fade.yaml=fade
(the card carries peak_mib 17664, so no @PEAK is needed; gate = max(card gate, peak + 2,048) = 19712). Preview written by me with
--repo /home/noob/work/bench_wt_x4_res: /home/noob/work/bench_x4_res_io/jobs_preview/x4_fade.tsv md5 16df9dd9 (10 lines; first: x4_fade_f0_s5|bench/methods/x4_fade.yaml|5|/tmp/noob_el/bench_data_v3b/roots/cv5v3_v11_f0|0|19712|9800|0||swad).

## Note
Heaviest training memory after SAPA; a dump gate above the default (6,200) is needed. Guard to watch (S): guided upsamplers can widen cracks or add false lines (width 0.85 to 1.15, false crack px on crack-free cells).

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
