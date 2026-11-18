# Review of LAUNCH_REQUEST_rows2.md (reviewer rows2, 15 Nov 2026, 16:20 to 16:35 IST)

Independent reviewer; I did not build this tranche. I checked every item with my own commands. Outputs are on gaint in `/home/noob/work/bench_rows2_io/review/rvw/`: run.log, pg.txt, stride.txt, skel_*.txt, id/*_cmp.txt, pytest_all.log, item1_git.txt, item2_render_diff.txt, item3_peaks.txt, item4_cv02_cache.txt, item5_deploy.txt, item5_data.txt, item34_roots.txt, item5_cards_cv02.txt, item6_rv6.txt, item6_jobs_cv02.txt, item7_safety.txt, item7_live_lanes.txt, item8_smoke.txt. On cv02 I only read: scripts went in by stdin, always with `ssh -a`. Nothing was armed or launched. Request checked: md5 d6ef49bd, 63 lines. E = measured, S = judgement.

## Verdict

**All 3 rows PASS. Overall PASS: the lead may launch with the commands in "Launch commands checked" below.**

| Row | Card (md5) | Weights (md5), licence | Verdict |
|---|---|---|---|
| segformer_mitb2_pf | segformer_mitb2_pf_v11 (fcaa08cc) | mit_b2 (e4dacbe5), NVIDIA SegFormer licence, non-commercial | PASS |
| hrnet_w18_unetpp_pf | hrnet_w18_unetpp_pf_v11 (c89314d8) | hrnet_w18 (e6bb005d), MIT | PASS |
| skr01_pf_v11 | skr01_pf_v11 (c01c6e78) | R34 (f57b4305), = house, terms unverified | PASS |

segformer_mitb2_pf: licence: research-only weights, benchmark row only

Nothing blocks the launch. Notes for the lead are at the end; none needs a fix before launch.

## Evidence per checklist item

### 1. Code (PASS)
- E: worktree /home/noob/work/bench_wt_rows2, branch bench_rows2, HEAD b12fca8a52e1aaae4590b8267e2a1d015128dac6. 0 changes (tracked or untracked), also after my checks. 52e3f14 is an ancestor.
- E: 3 commits: 0122c5c, 75d38b9, b12fca8. Each carries `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- E: el_bench HEAD 31c0c368ee65742893a36523bcf48e366ea948ed, 0 tracked changes.
- E: diff 52e3f14..b12fca8 = 6 A (3 cards in bench/methods, 3 in bench/methods_cv02), 1 A (tests/test_bench_rows2.py), 1 M (tests/test_bench_cards_cv02.py). The M only widens the variant set with ROWS2.
- E: diff 52e3f14..b12fca8 over src, scripts, configs, bench/q, bench/cards.py and bench/dumpfmt.py: 0 files. The trainer, train.py, data, augmentation, losses, optimiser and steps are unchanged.
- E: against 31c0c36 the only modified file is src/models/bench_models.py: the rows1 deeplab pooling swap, already reviewed in REVIEW_ROWS1. Only decoder deeplabv3 / deeplabv3plus reaches it, and no rows2 card does. Against d3a3280: 18 A, 2 M.
- E: own flag-off identity, 5 CPU steps, identity_cpu.py 962379a6. I made my own git archives of 31c0c36 (review/rvw/ref_31c0c36) and of b12fca8 (review/rvw/arch_b12fca8):
  - **PFV11 IDENTICAL**
  - **SUP IDENTICAL**
  - both on all fields except code / sec.
  - S: the builder's SUPPF IDENTICAL was not re-run. It lies between the two arms I ran and uses the same code path.
- E: W1 cards (pf_v11, v11, pf): config rendered at 31c0c36 == rendered at b12fca8, 30 of 30.
- E: own full pytest of the b12fca8 archive: **415 passed, 4 skipped**.

### 2. Cards (PASS)
- E: own flattened diff of the fully rendered config, each row against house_r34_unetpp_pf_v11 (seed 6, fold 2 root; item2_render_diff.txt), and the builder's `bench.cards diff` on the cv02 deploy give the same result:
  - segformer: model.name smp_unetpp -> bench_smp, model.decoder segformer, model.encoder_name mit_b2, model.encoder_weights imagenet. These are exactly T11 row 3's 4 keys.
  - hrnet: the same 4 keys with unetplusplus and tu-hrnet_w18. That is 3 of T11 row 5's 4 keys; `model.encoder_weights_file` is left out (see below).
  - skr01: only `loss.skel_recall.weight: <absent> -> 0.1`. So skr01 = PF v1.1 card + the Skeleton Recall key.
- hrnet deviation, judged acceptable (S): T11 names `encoder_weights_file=<local timm file>`, which would put a gaint path into a config that cv02 renders. Instead timm loads the same file from the offline HF cache. E on cv02: refs/main = 7e2c5583, the only snapshot, file md5 e6bb005d. cq.sh md5-checks the card's path before every start. On gaint the built encoder equals the file: 1,925 of 1,925 shared tensors equal, stem `model.conv1.weight` = RGB sum. The rendered config still differs from house only in keys T11 names. Same smp UnetPlusPlus defaults as the house `smp_unetpp` factory (read both).
- E, rendered config of every row: total_steps 20000, labeled_batch_size 8, input_size 512, mask_subdir masks_v11, mask_ignore_value 255, augmentation labelsafe, adam lr 1e-3, wd 1e-4, bf16. encoder_pf: freeze 1000, ramp 1000, lr_mult 0.1, wd 0.
- E, PF actually applied (pg.txt). For each card I built the model on CPU (HF offline) and ran the trainer's own `build_optimizer` and `build_lr_lambdas`:

  | Card | Groups | g1 == encoder.* | g0 / g1 tensors | lr g0 / g1 | wd g0 / g1 |
  |---|---|---|---|---|---|
  | segformer | 2 | yes | 13 / 332 | 1e-3 / 1e-4 | 1e-4 / 0 |
  | hrnet | 2 | yes | 68 / 963 | 1e-3 / 1e-4 | 1e-4 / 0 |
  | skr01 | 2 | yes | 68 / 108 | 1e-3 / 1e-4 | 1e-4 / 0 |
  | house PF | 2 | yes | 68 / 108 | 1e-3 / 1e-4 | 1e-4 / 0 |

  - Groups are disjoint and cover all parameters.
  - PF multiplier at steps 0, 999, 1000, 1500, 2000 = 0, 0, 0.001, 0.4957, 0.9797, the same for all 4.
  - Encoder tensors equal the card file: mit_b2 331 of 331, hrnet 1,925 of 1,925, R34 179 of 179.
  - Stems = RGB sum: `patch_embed1.proj.weight`, `model.conv1.weight`, `conv1.weight`.
  - Output (1, 24, 512, 512) for all.
- E, skr01 loss really active (skel_skr01_pf_v11.txt). I ran the trainer's real `_train_step` on CPU for 3 steps (fold 0 root, seed 5):
  - loss class ThinCrackLoss, srec_weight 0.1, trainer thin_on True;
  - each step: crack in batch, tube px > 0, Skeleton Recall term present, finite and **> 0**;
  - tube px on ignore (255) px: 0.
  - Controls (house PF v11, segformer): CEDiceLoss, no term, no tube.
  - I printed no loss value.

### 3. Fairness record, G16 (PASS)
| Row | Params total = trainable | encoder.* | GFLOPs 512 (request) | Output stride (E, mine) | Peak MiB (E, recomputed) | Gate | s/step (request) | Steps x batch |
|---|---|---|---|---|---|---|---|---|
| house PF | 26,075,672 | 21,278,400 | 148.0 | 1 | 5,736 (W1-C) | 9,000 | 0.18 | 20k x 8 |
| segformer | 24,722,008 | 24,190,016 | 50.0 | 4 (decoder 128 px, x4 head) | 7,444 | 9,492 | 0.19 | 20k x 8 |
| hrnet | 20,795,692 | 10,947,028 | 218.0 | 1 | 8,430 | 10,478 | 0.32 | 20k x 8 |
| skr01 | 26,075,672 | 21,278,400 | 148.0 | 1 | 5,574 | 7,622 | 0.18 | 20k x 8 |
- E: parameter counts and output strides match the request table. Each gate = peak + 2,048.
- E: peaks recomputed from both memory logs (mem1s 1 s, gpumem 2 s) of rows2_smoke, rows2_smoke2 and rows2_smoke3: smokes 7,444 / 8,430 / 5,574; dumps 2,502 / 3,944. Both logs agree with the request.
- E: every row trains 20,000 steps of 8 images (160k images), ImageNet pretraining, house PF recipe. No row trains more or fewer steps or images than the baseline; none is flagged.
- Step time: the stdouts are removed, so I could not recompute s/step.
  - E: the smoke wall windows in launch.log (python start to `trained ... rc=3`, 300 steps plus startup) are 91 s, 121 s and 91 s. These fit 0.19, 0.32 and 0.18 s/step.
  - hrnet: 1.47x house FLOPs, 1.8x step time. Both are below G16's 2x line, so no equal-cost ensemble comparator is needed.
  - GFLOPs were not re-measured by me.

### 4. Weights (PASS)
- E, md5 equal at all ends:

  | Weights | md5 | gaint HF cache | download copy (bench_rows2_io/weights/hf) | cv02 /tmp/noob_el/cache/hf/hub |
  |---|---|---|---|---|
  | mit_b2 | e4dacbe55332270c75f47be8b8f04b75 | yes | yes | yes |
  | hrnet_w18 | e6bb005ddbe1b52bde05618fc6b4b8e3 | yes | yes | yes |
  | R34 | f57b430554b18e1238c4f92eac566544 | yes | - | yes |

  - cvcard.py on cv02: each card md5 = the cv02 file md5.
  - mit_b2 sits at snapshot 868ab6f1, the revision smp 0.5.0 pins.
- E: HF API records: mit_b2 gated False, license:other; hrnet gated False, license:mit, sha 7e2c5583.
- E: WEIGHTS.tsv records source URL, revision, md5, bytes, both cache paths, licence and commercial use:
  - mit_b2 **NO** (research-only weights, benchmark row only). Licence text lic/NVlabs_SegFormer_LICENSE, l.38-39: "non-commercially ... research or evaluation purposes only".
  - hrnet **YES** by the MIT text (lic/HRNet_Image_Classification_LICENSE, Microsoft 2019).
  - R34 unverified, as in rows1.
  - The segformer card carries the exact line `# licence: research-only weights, benchmark row only` (grep count 1; 0 in the others).
- E: offline load:
  - cq.sh exports HF_HUB_OFFLINE=1 and env.sh sets HF_HOME=/tmp/noob_el/cache/hf.
  - The 4 cv02 smokes (segformer, hrnet x2, skr01) started and trained under that.
  - My gaint CPU builds ran with HF_HUB_OFFLINE=1 and loaded the file tensors (item 2).

### 5. Deploy and data (PASS)
- E, deployed code:
  - My fresh `git archive b12fca8` checked against cv02's CODE.md5: ARCHIVE_OK, file lists equal (647 tracked files).
  - CODE.md5: 648 lines, md5 9f42e15ad216f7fe5f4791eab68c90b4. This equals the gaint stage copy.
  - On cv02: REVISION b12fca8a..., CV02_CODE_OK. No file newer than CODE.md5 except __pycache__.
  - No runs/ or dumps/ dir and 0 r2_* entries in experiments.
- E, data:
  - DEPLOY.md5 d6063fd83d20e656612540edda702cbe on cv02 = the gaint stage copy, md5sum -c OK; ROOTS_OK.
  - Roots line diff against gaint: 0 and 0.
  - Two `asserts: OK (0 forbidden of 167; 0 of 330 groups split; held-outs partition 532; lists = cv5v2.json)`.
  - Masks: CV02_MASKS_OK, 1,596 lines, 0 not in the gaint MANIFEST (9c0e0687). BUILD_LOG base-mask line `582 of 582 IDENTICAL, 0 DIFF`: count 1.
  - review_w1g.py (7ab965f2) on cv02: ALL PASS, 57 PASS, 0 FAIL (532 mask links, wrong 0, dangling 0; ignore px strict 0, masks 3,484).
- E: labeled, masks_v11, roots and roots/cv5v2_v11_f* are dr-xr-xr-x (read-only).

### 6. Jobs (PASS)
- E: /tmp/noob_el/bench_q/rows2/jobs.txt:
  - md5 87e0b6089fece20e986553baac684626 (= gaint realq copy), r--r--r--, 30 lines.
  - My script rebuilt the expected 30 lines and they are **exactly equal, order included**. The expected lines are: seed 5 block (segformer f0-f4, hrnet f0-f4, skr01 f0-f4), then seed 6 the same; root cv5v2_v11_f<k>; card gate; dump gate 6200; logp 1; extra empty.
  - Names unique, 10 per row, mismatches 0, `15 5; 15 6`.
- E: 0 r2_* in B/experiments. Q holds only jobs.txt, LPG (1) and MAXC (8). No bench_q_rows2 session.
- E: the dump command is the same DCMD code as W1-C (bench/q diff 0): bench_infer fp32, `--logp`, forbidden list. The dump tests wrote npz keys pred, oth, m_crack, p_crack, p_inact and logp (builder; dump code unchanged).
- E: gaint /home/noob/work/bench_relay/rows2 does not exist.

### 7. Safety on cv02 (PASS)
- E: lane test (test_other_on.sh 715166a0) on cq.sh of b12fca8: 13 of 13 PASS.
- E: cq.sh 5f13e5ac = d3a3280 (bench/q diff 0 lines), read in full again:
  - The lane rule sums other users' MiB per GPU, and only live PIDs in Q/pids count as ours. So any other queue dir counts as another user.
  - LPG 1 is enforced. Arming fails unless LPG is 1 or 2, and Q/LPG = 1.
  - A stop only goes through stop_verified on a recorded PID.
- E: live lanes, read-only, 10:53 UTC: only GPU 5 qualifies (ds404_user13 3,638 MiB). Every other GPU has a user above 4,096 MiB. The awk sums agree. 0 bench_* sessions on cv02.
- E: `git grep -nE "pkill|killall|pgrep|xargs.*kill"` over b12fca8 bench/q and scripts/bench_infer.py: 0. All `kill` uses are `kill -0` probes, or TERM / KILL to a verified PID (bench_lib.sh), or test-only code.
- E, PID files: all 6 smoke and dump jobs have `pid <n>` = their `pid <job> <n> (python; parent ...)` log line. Cmdlines start `/tmp/noob_el/el-fault-detection/.venv/bin/python -u scripts/train.py --exit_after_step` (smokes) or `... scripts/bench_infer.py --run` (dumps).
- E, relay:
  - relay_w1c.sh 74a2ec3d is unchanged. It uses `ssh -n -a -o ForwardAgent=no -o BatchMode=yes` and only read commands on cv02.
  - Stage /home/noob/work/bench_rows2_io/stage/bench_b12fca8: md5sum -c OK, REVISION b12fca8a.
  - No bench_relay_rows2 or bench_relay_rows2_dry session on gaint.

### 8. Smokes (PASS)
- E (rows2_smoke launch.log, deploy 75d38b9; it differs from b12fca8 only in the 6 card memory blocks): all 3 rows print:
  - `config OK (= card)`;
  - `startup line OK: Labelled: 425 (/tmp/noob_el/bench_data/roots/cv5v2_v11_f0/splits/train.txt)  unlabelled: 0 (-)  val: 107  test: 107`;
  - `trained ... rc=3` (by design).
- E (rows2_smoke2, deploy b12fca8):
  - armed line with deploy b12fca8a... (CODE.md5 OK);
  - hrnet 50-step smoke with the real gate: config OK, startup OK, rc 3;
  - segformer dump test `dumped ... rc=0`, `Traceback lines 0`, `RUN.md5 ... rc=0: 111 files, md5 129b1109`.
- E (rows2_smoke3): hrnet dump test rc 0, Traceback 0, RUN.md5 111 files, md5 25e43837.
- NaN / Traceback in training: the smoke stdouts are already removed, so I could not re-count. The builder's counts stand (BUILD_LOG 13:31:51: Traceback 0, nan 0).
- E: outputs removed. Both deploys: smoke/dumptest dirs 0, runs/ and dumps/ absent, CODE_OK.
- E: nothing of this tranche is running: 0 cv02 processes matching the rows2 deploys, queue or r2_ names; 0 bench_* sessions on cv02; no rows2 session on gaint. My own check session bench_rows2_rvw ended by itself.

## Launch commands checked (unchanged from the request section 4)
I checked every precondition of cq_setup.sh, which I read in full:
- session absent;
- Q has no queue.pid, gpumem.pid, HOLD, pids/ or launch.log;
- jobs md5 equal;
- REVISION = DEPLOY;
- CODE.md5 OK;
- LPG 1;
- no job's experiments/<name> exists.

Queue (G):
`ssh -n -a -o BatchMode=yes cv02@10.8.1.106 'B=/tmp/noob_el/bench_b12fca8 Q=/tmp/noob_el/bench_q/rows2 SES=bench_q_rows2 DEPLOY=b12fca8a52e1aaae4590b8267e2a1d015128dac6 JOBS_MD5=87e0b6089fece20e986553baac684626 DATA_MD5=d6063fd83d20e656612540edda702cbe bash /tmp/noob_el/bench_b12fca8/bench/q/cv02/cq_setup.sh'`

It must print `cq_setup: bench_q_rows2 armed: gpumem <pid> queue <pid>` and `cv02 q armed: 30 jobs (md5 87e0b608...) ... deploy b12fca8a... (CODE.md5 OK) ... LPG 1, MAXC 8 ... cq 5f13e5ac`. Then either:
- at the first start: `r2_segformer_mitb2_pf_f0_s5 config OK (= card)` and `startup line OK: Labelled: 425 ...` (C `tail -20 /tmp/noob_el/bench_q/rows2/launch.log`); or
- with no lane: a `lane GPU <g>: another user > 4096 MiB` line per GPU. The job starts by itself when a GPU qualifies.

Relay (G). First run `cd /home/noob/work/bench_rows2_io/stage/bench_b12fca8 && md5sum -c --quiet CODE.md5 && echo OK && md5sum bench/q/cv02/relay_w1c.sh` (OK, 74a2ec3d...), then:
`tmux has-session -t "=bench_relay_rows2" 2>/dev/null || { test ! -e /home/noob/work/bench_relay/rows2 && mkdir -p /home/noob/work/bench_relay/rows2 && tmux new-session -d -s bench_relay_rows2 "B=/tmp/noob_el/bench_b12fca8 Q=/tmp/noob_el/bench_q/rows2 RD=/home/noob/work/bench_relay/rows2 N=30 NAMES_RX=^r2_ POLL=300 bash /home/noob/work/bench_rows2_io/stage/bench_b12fca8/bench/q/cv02/relay_w1c.sh"; }`

Confirm the relay with: G `tmux has-session -t "=bench_relay_rows2" && cat /home/noob/work/bench_relay/rows2/relay.pid && head -1 /home/noob/work/bench_relay/rows2/relay.log`.

Stop:
- queue: C `touch /tmp/noob_el/bench_q/rows2/HOLD`;
- a running run: only by its PID in Q/pids/<name>.pid, after printing its cmdline;
- relay: G `touch /home/noob/work/bench_relay/rows2/STOP`.

Nothing starts on gaint's GPU.

## Notes for the lead (S, none blocks the launch)
1. **Request licence line.** The request writes `licence: segformer_mitb2_pf: research-only weights, benchmark row only`. The row name sits inside the user's phrase, so a grep for the exact line finds 0 in the request. The card has the exact line, and this review states it above (Verdict). If the lead wants the request to match the rule word for word, add the line `licence: research-only weights, benchmark row only` under the segformer row. It is a text-only change and does not touch any pinned file.
2. **cv02 disk.** /tmp on cv02 has 106 GB free and is 94% used on the shared disk. The tranche writes about 45 GB, and cq.sh has no disk guard. Check `df -h /tmp` on cv02 once a day. If it falls below about 20 GB, `touch Q/HOLD`. gaint has 213 GB free, so the relay's 33 GB fits beside W2a.
3. **Lanes.** At 10:53 UTC only GPU 5 qualifies, so the queue may take 1 to 2 days, as the request says. Under LPG 1, MAXC 8 does not bind.
4. **segformer under PF.** PF freezes the encoder for 1k steps, and the encoder is 98% of segformer's parameters (24.19M of 24.72M). T11's one retry (`training.encoder_pf.lr_mult=0.3`) applies only if the failure gate trips on fold 0 seed 5; read that run first. Its stride-4 head should be printed beside the A0 GT-side bound.
5. **hrnet.** T11 expected about 21M encoder parameters. timm `features_only` builds 10.95M (encoder.*), 20.8M total; the request prints the real numbers. Apply the inactive guard (WAVE3_REVIEW) at read time. Its step time is 1.8x house without contention. If CPU contention pushes the measured ratio above 2x, G16's equal-cost ensemble comparator applies.
6. **Dump near-ties.** This is unchanged from REVIEW_ROWS1 note 1. If a run logs `dumped dump_r2_... rc=1`, it gets no RUN.md5 and is not relayed. Its latest.pth stays on cv02 and can be re-dumped.
7. **Not in this job list.** F51 dumps are not here (later, on gaint from slim.pth). skr01's LOSO-2 part (4 runs) is also not here; it needs its own job list once the LOSO-2 roots are built and placed (stage B3).
8. **Builder slip.** The builder printed 3 training-loss values from a gaint CPU fixture log (logged). No held-out or metrics number was involved, and nothing was selected from them.
