# Handover: x4_fullres_skip (builder res)

Builder res, 27 Nov 2026. E = measured, S = judgement. Code branch x4_res, worktree /home/noob/work/bench_wt_x4_res:
085b0d9 (code, tests, cards) + f2df856 (card memory fields only). Base bench_x4 399f963. Code: src/models/x4_res.py, 3-line hook
in src/models/bench_models.build_bench_smp (only when a model.x4_* key is present); tests/test_x4_res.py.

## Arm
- Card: bench/methods/x4_fullres_skip.yaml (md5 85b941e990967febe0cd320e5ec40e91), cv02 variant bench/methods_cv02/x4_fullres_skip.yaml (md5 7db5e1ff13fa2b9bde5bd1ad4a953c53).
  = COMBO (hrnet_w18_unetpp_swad_const_pf_v11) + exactly `model.x4_fullres_skip=16`; readouts as COMBO; compare its swad readout with COMBO's.
- Paper: FACS-net, Automation in Construction 2026, doi:10.1016/j.autcon.2025.106719; NEW per scouts/general and scouts/thin (fit 4), full text read by the scouts. No code used.
- What changes:
  What COMBO does now (E): smp's UnetPlusPlusDecoder drops features[0] (the input image); the stride-2 skip is the HRNet
  stem conv1-BN-ReLU output (64 ch); the last block x_0_4 (stride 2 -> 1, 32 -> 16 ch) nearest-upsamples with NO skip. So no
  full-resolution information reaches the output after the stem.
  Arm: a stride-1 stem on the input, 2 x (Conv3x3-BN-ReLU), 16 channels (decoder.fullres_stem, smp init, full lr from step 0),
  is concatenated as the skip of x_0_4 (its conv1 input 32 -> 48 channels; the block is rebuilt with smp's init). Everything else
  is COMBO's. FACS-net's other decoder parts (FPCM FFT band split, CBAM) are not included (S: one change per arm).

## Numbers
- Training peak (E, cv02 smoke, GPU 5): 8,984 MiB (COMBO in the same queue 8,638). Card peak_mib 9,732 (= smoke + 748, S);
  **gate 11,780 MiB**.
- Step speed (E, same GPU, interleaved, pure train step): best 3.082 steps/s = **0.94 x COMBO** (3.285).
  Smoke steps/s: 2.359 / 2.529 / 2.579 / 2.613 (GPU 5, different GPU; not comparable).
- Wall time per run (S): about 165 min (COMBO 155).
- Params / GFLOPs at 1x1x512x512: 20,800,508 (+4,816); 220.6 GFLOPs (+2.5) (COMBO 20,795,692 / 218.1).
- Dump (E): fp32 b8 max_reserved 3,116 MiB -> projected dump peak 4,072 MiB (S); dump gate 6,200 (default).

## Jobs (5 folds x seeds 5, 6; 10 lines; nothing launched)
In /home/yugma/mtp/research/team_2026-11-27_arch/harness/x4 (gaint):
    python x4_make_jobs.py --out jobs/<qn>.tsv --repo <tree at x4_res f2df856 or merged> bench/methods/x4_fullres_skip.yaml=fullres
(the card carries peak_mib 9732, so no @PEAK is needed; gate = max(card gate, peak + 2,048) = 11780). Preview written by me with
--repo /home/noob/work/bench_wt_x4_res: /home/noob/work/bench_x4_res_io/jobs_preview/x4_fullres_skip.tsv md5 d7a48987 (10 lines; first: x4_fullres_f0_s5|bench/methods/x4_fullres_skip.yaml|5|/tmp/noob_el/bench_data_v3b/roots/cv5v3_v11_f0|0|11780|6200|0||swad).

## Note
Cheapest arm (+4.8k params). Composes with the upsampler keys (with both set, FADE / SAPA in x_0_4 use the stem output as guide); not carded.

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
