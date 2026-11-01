# PF2 build note (runner, 31 Oct 2026; for coach's §9 review)

Deploy: gaint `el_f3`, commit **e544133** (no code change; `REVISION` e544133, 0 tracked changes, checked by every script). Protocol: `protocol_PF2.md`. Scripts: gaint `el_f3/reports/pf2/scripts/`, local copies `team_2026-10-31_next/scripts/pf2/` (md5s at the end). Smoke evaluation: gaint `el_f3/reports/pf2/smoke/GATES.txt`. Tags: E measured (file), S judgement.

## Gate 1. Identity at e544133 today (E, `smoke/GATES.txt`)
- `REVISION` e544133, HEAD e544133, 0 tracked changes (smoke deploy check).
- **SUP100-g** smoke `pf2s_sup_s0` (s0, val off, 1,000 steps) vs the real run `f3_SUP_100pct_s0.stdout`: **IDENTICAL (20 step lines**, timestamps and speed stripped). Also IDENTICAL vs protocol_100 smoke b1.
- **SUP100-PF** smoke `pf2s_suppf_s0` vs the real run `f3_SUPPF_100pct_s0.stdout`: **IDENTICAL (20)**, PF encoder lr lines **IDENTICAL (20)**; also IDENTICAL vs smoke c1 (steps and PF lr).

## Gate 2. Opts strings and configs (E)
- Run names `pf2_{SUP,SUPPF,RN50PF}_100pct_s{5..9}`; the 15 opts strings in `el_f3/reports/pf2/pf2_jobs.txt`, **md5 210d0d6fcc54c3effcc36893e0d51ad5** (`pf2_make_jobs.sh` 9573d968). The queue refuses any other md5.
- Opts = protocol_100's (`f100_queue.sh`) + `training.val_every=20000`; RN50-PF = SUP100-PF + `model.encoder_name=resnet50`.
- Smoke configs vs protocol_100's arm configs (run_name / experiments_dir ignored): SUP100-g vs `f3_SUP_100pct_s0`: none; SUP100-PF vs `f3_SUPPF_100pct_s0`: none; **RN50-PF vs `f3_SUPPF_100pct_s0`: only `encoder_name: resnet50`**. (Smokes are seed 0; the real runs add seed 5-9, checked by the queue.) RN50-PF vs Track M `m_r3_rn50_s1` (house RN50): seed, val_every and the `encoder_pf` block only.
- After each start the queue diffs the run's `config_used.yaml` against protocol_100's s0 config of its arm: allowed seed only (SUP vs `f3_SUP_100pct_s0`, SUPPF vs `f3_SUPPF_100pct_s0`), seed + `encoder_name: resnet50` (RN50-PF vs `f3_SUPPF_100pct_s0`). Anything else: `reports/pf2/HOLD` + a `CONFIG FAIL` line (running runs continue).

## Gate 3. Data (E, `el_f3/reports/pf2/data_check/data_check.txt`)
- Splits train 842f27c4 / val 9dcccf00 / test a31fad14 and ext117 `stems_eval.txt` 5266806b: equal to protocol_100's records (`team_2026-10-29_features/log.md` 30 Oct 16:35; `protocol_mim5.md`).
- `masks_escdd` 583, labelled images 582, ext117 354 files: newest mtimes 10 Oct / 2 Oct / 29 Oct 13:00, all before protocol_100's launch (30 Oct 12:05), so the bytes protocol_100 read are unchanged. No aggregate md5 of these folders was on record; full per-file listings are now saved (aggregates labeled 766bab95, escdd_masks 53c5b631, ext117 c06fd2e9) for any later comparison.

## Gate 4. RN50 build (E, `el_f3/reports/pf2/cpucheck/rn50_cpucheck.json`, script f451eebc; CPU)
- Weights: smp 0.5.0 loads `smp-hub/resnet50.imagenet` from the offline HF cache (snapshot 00cb74e3, `model.safetensors`, sha256 **df1aad85e18536504a4c8597118364e291ff3a9c4b56dd9b3a4900642e4c3a7c** = the blob name, md5 646f731d; cached 3 Oct, no download). Same smp key as Track M R3 (`encoder_name: resnet50`, encoder_weights imagenet).
- 48,982,808 params (= Track M R3). Stem (64, 1, 7, 7) **equals the RGB sum** of the 3-channel ImageNet stem. Rebuild identical.
- PF groups: group 0 (house) 25,481,048 params, lr 1e-3, wd 1e-4; group 1 (`encoder.*`) 23,501,760 params, **53 conv tensors** (R34: 36), lr 1e-4, wd 0.
- "PF encoder lr=" lines in the RN50-PF smoke: at steps 1,000 / 1,500 / 2,000: 9.96e-08 / 4.957e-05 / 9.797e-05 (freeze, ramp, 0.1 × house), as R34 SUP100-PF (1.0e-7 / 5.0e-5 / 9.8e-5). Losses finite (2k 0.6951, 4k 0.5049); 0 Tracebacks.
- ImageNet RN50 step-0 reference for the cosine table: `reports/pf2/cpucheck/rn50_imagenet_step0.pth`.

## Gate 5. RN50-PF smoke and lanes (E, `gpumem.log` 1 s samples, `smoke/GATES.txt`)
- **Peaks, per process (nvidia-smi):** RN50-PF **11,186 MiB** (first process, constant from step ~100 to 2,000; the resumed 2k→4k process 10,098); SUP100-g 6,830; SUP100-PF 6,826; finllm 5,876; idle GPU with finllm alone: 25,525 free. `torch.cuda.max_memory_reserved` is only stored in metrics.json at a normal end, which the `exit_after_step` smoke does not reach; nvidia-smi per-process (which includes the CUDA context) is the gating figure, as in protocol_100.
- **RN50 gate GRN = 11,186 + 2,048 = 13,234 MiB.**
- **Lanes (E where measured):** 1 RN50 + 1 R34 + finllm: **7,241-7,500 MiB free measured** (7,241 includes 254 MiB of builder's pytest CUDA context, now asked to use CUDA_VISIBLE_DEVICES=""). 3 R34: ~5.0 GB (protocol_100). 2 RN50: 25,525 − 2 × 11,186 = ~3.2 GB (S). **1 RN50 + 2 R34: ~0.7 GB, NOT allowed**: MAXRN 1 and the R34 gate (9,000) both block it.
- **Speeds (steps/s, from step-line timestamps):** RN50-PF alone 3.6-3.85 (mean ~3.7); RN50-PF beside one R34 1.79 with the R34 at 3.33; R34 alone ~5.6-7.1 (the SUPPF smoke's last lines after RN50 exited); 3 R34 at once 2.25 each (protocol_100). The GPU is compute-bound at about 6.7-7 R34-equivalent steps/s in every mix; one RN50 step ≈ 1.9 R34 steps.
- **Scoring peak (coach ruling 14:20, before any number):** RN50 LA val pass (`rescore_logit_adjust --splits val`, 54 cells, 2k copy) **5,824 MiB** (1 s samples). The smoke's m0_audit val pass stopped at the frozen scorer's `assert step == 20000` (designed; m0_audit d36f7438 not edited; my slip in the smoke design), so **LA stands in for the unmeasured RN50 m0 pass** (LA was the largest R34 pass: 5,106 vs m0 4,002, rescore 4,398; disclosed). **GS = max(7,154, 5,824 + 2,048) rounded up to 100 MiB = 7,900 MiB.** The 1 s logger measures every pass at the opening.

## Gate 6. PF preservation on RN50 (E for seed 0; s5 during the run)
- **Launch gate (coach: the smoke's seed-0 4k cosine, as protocol_100 G5):** RN50-PF s0 vs ImageNet RN50, per-stage mean conv cosine / norm ratio: **2k layer3 0.996, layer4 0.997; 4k layer3 0.975, layer4 0.983 (≥ 0.8: PASS)**; conv1 1.000, layer1 0.992, layer2 0.983 at 4k. Reference, house RN50 (Track M `m_r3_rn50_s1`, 20k): layer3 0.007, layer4 0.001. R34 SUP100-PF s0 (protocol_100 c1): 4k 0.975 / 0.985.
- Confirmation on RN50-PF s5 (`pf2_g6.sh` 0c19e718): a checkpoint is written every 2,000 steps (`checkpoint_every: 2000`, atomic `latest.pth`), so step 4,000 is saved. The script waits for the "step 4050/20000" line (the 4k save is complete), copies `latest.pth` to `latest_4k.pth`, asserts step 4000, runs `enc_cosine.py` on CPU vs the ImageNet RN50 step 0. PASS if layer3 and layer4 ≥ 0.8. FAIL: `RN_STOP` (the queue skips the RN50 jobs), every running RN50-PF python process stopped by its recorded PID (`reports/pf2/pids/`, command line printed and checked first), the trigger then waits for the 10 R34 runs. With the R34-first policy, s5 reaches 4k about 9 h after launch.

## Gate 7. Queue, trigger, opening
- `pf2_queue.sh` 48e32d54: `POLICY=twohead` (coach ruling), MAXC 3, MAXRN 1, R34 gate 9,000, RN50 gate 13,234 MiB; shared gate `gpu_gate.sh` (one flock for every runner-started GPU job, free ≥ need, ≥ 120 s since any start, global HOLD); queue HOLD `reports/pf2/HOLD`; rc captured before `$(date)`; refuses to start without the gpumem logger alive.
- gpumem logger `pf2_gpumem.sh` 542adcf1, PID 1500647 since 14:03:24 (10 s; 1 s while a scoring process is on the GPU or during smokes), stops 60 s after the opening's end line.
- Trigger `pf2_postwatch.sh` a3db163e: all 15 "trained ... rc=0" (10 if RN_STOP); any needed rc ≠ 0 → "pf2 NOT scored (FAIL)".
- Opening `pf2_post.sh` d4905727: completeness, init record, rescore, m0 default / tau 0 / tau 1 (val, test, ext117), tau0 check, LA tau 0 / 1, 20k cosine table; every GPU pass behind **GS = 7,900 MiB**; extra passes only if listed in `post_extra/FROZEN.md5` and `md5sum -c` passes before the opening; MANIFEST; one end line.
- Extra pass ready: scuff-ignored test (`post_extra/pf2_scuffign.py` e3615fdb + `pf2_scuffign.sh` 2abfae02): re-infers test exactly as m0_audit (its `comps` / `cell_stats` code lines identical to d36f7438, checked; `predict` minus the TTA branch); self-check first (the 2 cells' stats with the original keep must equal the opening's m0 JSON, else exit 1 and nothing written); then the 236 raw E-SCDD class-25 px ignored (asserts 34 / 202 px, all crack in our GT). Output: m0-format JSONs, so m2_rung runs unchanged. **Self-check-only run 14:27 on two already-opened protocol_100 runs (f3_SUP_100pct_s0, f3_SUPPF_100pct_s0): both "2 cells equal the m0 JSON"; nothing written** (`reports/pf2/scuffign_selfcheck.log`). Frozen: `post_extra/FROZEN.md5` **md5 1ae6d4f561e4b9436fa6d1ce53c9f7af** (lists pf2_scuffign.py e3615fdb, pf2_scuffign.sh 2abfae02). calib's B5 / cell-level pass can be added to it before the opening (new md5 to coach).
- E1 scorer successor `pf2_e1_extra.py` d404dd25 (frozen by coach). Local analysis `pf2_post_local.sh` 3d4bd4ed. Launch wrapper `pf2_launch.sh` 1ed586de. Local watcher `watch_pf2.sh` c918d27b (tracked).

## ETA (S, from the measured speeds)
- R34 phase: 10 runs in 3-lane seed waves at 2.25 steps/s each (~2.5 h per wave): about 7.4 h for 9 runs; the 10th (SUPPF s9) then runs beside RN50-PF s5 (3.33 / 1.79) for ~1.7 h.
- RN50 phase: s5 finishes alone (~0.7 h), then s6-s9 alone at ~3.7 steps/s, ~1.5 h each: ~6 h.
- **Total about 15.8 h + gate spacing: launch ~14:45 → all trained ~06:30-07:00 on 1 Nov; opening (15 runs incl. RN50, ~45 min) → ~07:30.** Gate 6 confirmation (s5 at step 4,000) about 8 h after launch (~22:50).
- Cross-check: total work ≈ 200k R34 steps + 100k RN50 steps × 1.9 ≈ 390k R34-equivalent / ~6.8 per s ≈ 16 h.

## Script md5s
gaint `el_f3/reports/pf2/scripts/` = local `scripts/pf2/`: gpu_gate.sh 00fabfdd, pf2_gpumem.sh 542adcf1, pf2_smoke.sh 9d5b1e36, pf2_smoke_eval.sh c4de2a3e, pf2_rn50_cpucheck.py f451eebc, pf2_make_jobs.sh 9573d968, pf2_queue.sh 48e32d54, pf2_g6.sh 0c19e718, pf2_postwatch.sh a3db163e, pf2_post.sh d4905727, pf2_launch.sh 1ed586de, post_extra pf2_scuffign.py e3615fdb / pf2_scuffign.sh 2abfae02 (FROZEN.md5 1ae6d4f5). Local only: pf2_e1_extra.py d404dd25 (frozen), pf2_e1_width.py 241260db, pf2_post_local.sh b9fe78a6, watch_pf2.sh c918d27b. Jobs file 210d0d6f. Smoke GATES.txt 5bd44a20.
