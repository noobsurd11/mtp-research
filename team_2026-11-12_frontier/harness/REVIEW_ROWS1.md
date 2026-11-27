# Review of LAUNCH_REQUEST_rows1.md (reviewer rows1, 14 Nov 2026, 04:44 to 04:56 IST)

Independent reviewer, did not build. Every item checked by my own commands; outputs on gaint in `/home/noob/work/bench_rows1_io/review/rvw/` (run.log, pg.txt, item2_diffs.txt, item34_roots.txt, item5_cards_cv02.txt, item6_jobs.txt, item7_lane_test.txt, item7_live_lanes.txt, item8_smoke.txt, id_*_cmp.txt). cv02 only read (scripts piped by stdin, `ssh -a`). Nothing armed or launched. E = measured, S = judgement.

## Verdict

**All 5 rows PASS. Overall PASS: the lead may launch with the section "Launch commands" below.**

| Row | Card (md5) | Verdict |
|---|---|---|
| dlv3p_r34_pf | dlv3p_r34_pf_v11 (58d467e2) | PASS |
| unet_r34_pf | unet_r34_pf_v11 (384a5cef) | PASS |
| pratt_dlv3p_wcec | pratt_dlv3p_wcec_v11 (640bcf9d) | PASS |
| hanifi_vgg16_unet_pf | hanifi_vgg16_unet_pf_v11 (3d58654a) | PASS |
| ucf_dlv3_r50_pf | ucf_dlv3_r50_pf_v11 (90edf734) | PASS |

No blocking finding. Notes for the lead at the end (none needs a fix before launch).

## Evidence per checklist item

### 1. Code (PASS)
- E: worktree /home/noob/work/bench_wt_rows1, branch bench_rows1, HEAD 52e3f149f8244e6399c0a01dcf8c6b36874d219d, 0 tracked changes (also clean after my pytest). d3a3280 is an ancestor. 3 commits: 4214880, b2ea066, 52e3f14, each message carries the Co-Authored-By line. el_bench HEAD 31c0c368ee65742893a36523bcf48e366ea948ed, 0 tracked changes.
- E: diff d3a3280..52e3f14 = 11 A (5 cards, 5 cv02 variants, tests/test_bench_rows1.py) + 2 M (src/models/bench_models.py, tests/test_bench_cards_cv02.py). Against 31c0c36 the only modified file is src/models/bench_models.py. bench/q diff d3a3280..52e3f14: 0 lines. No change to trainer, train.py, data, augmentation, losses, optimiser or configs.
- E: the bench_models.py change (read in full) runs only inside `build_bench_smp` for decoder deeplabv3 / deeplabv3plus: it replaces `nn.AdaptiveAvgPool2d(1)` by `GlobalAvgPool` (no parameter or buffer change). No card before this tranche uses bench_smp with those decoders (grep of bench/methods, configs: only the 3 new row cards; configs/ucf_deeplab.yaml uses the old `deeplabv3plus` wrapper name). On CPU: 0 AdaptiveAvgPool2d left, 1 GlobalAvgPool, for both DLV3+ R34 and DLV3 R50.
- E: own flag-off identity, own git archive of 31c0c36 (review/rvw/ref_31c0c36) vs bench_wt_rows1 52e3f14, identity_cpu.py 962379a6, 5 CPU steps: **PFV11 IDENTICAL, SUP IDENTICAL** (all fields except code / sec). The builder's SUPPF IDENTICAL not re-run (S: SUPPF lies between the two arms I ran; same code path).
- E: own full pytest of bench_wt_rows1: **399 passed, 4 skipped**.

### 2. Cards (PASS)
- E: own `bench.cards diff house_r34_unetpp_pf_v11 <row>` on gaint and (builder's rv5 script, run by me with PYTHONDONTWRITEBYTECODE) on cv02 deploy, same result:
  - dlv3p: model.name smp_unetpp -> bench_smp, model.decoder deeplabv3plus, model.encoder_name resnet34, model.encoder_weights imagenet.
  - unet: same 4 keys with decoder unet.
  - pratt: dlv3p's 4 keys + loss.supervised ce_dice -> weighted_ce, loss.weight_set C.
  - hanifi: model.name smp_unetpp -> smp_unet only (factory default vgg16 / imagenet; built model is Unet with VGGEncoder).
  - ucf: 4 keys with decoder deeplabv3, encoder resnet50.
  These are exactly the T11 lists. All 7 _v11 cards validate.
- E: rendered config of every row: total_steps 20000, labeled_batch_size 8, input_size 512, mask_subdir masks_v11, mask_ignore_value 255, augmentation labelsafe, adam lr 1e-3, wd 1e-4, bf16, encoder_pf freeze 1000 / ramp 1000 / lr_mult 0.1 / wd 0. The 4 house cards are byte-equal to d3a3280 on cv02.
- E: PF actually applied (review/rvw/pg.txt, CPU build from the rendered card config, HF offline, the trainer's own `build_optimizer` and `build_lr_lambdas`): for every row 2 groups, group 1 == exactly the `encoder.*` parameters, groups disjoint and covering all parameters; group 0 lr 1e-3 wd 1e-4, group 1 lr 1e-4 wd 0; PF multiplier 0.0 at steps 0 and 999, 0.001 at 1000, 0.49 at 1499, 0.98 at 1999 (house PF card gives the same numbers). Encoder tensors equal the card's weights file (R34 179 of 179, VGG16 25 of 25, R50 264 of 264 shared tensors; first conv = RGB sum). Output (1, 24, 512, 512) for all.
- E (pratt): `loss_factory` weighted_ce branch builds `WeightedCrossEntropyLoss(weight=pratt_weights("C"))`; class default `ignore_index=255`; forward computes CE with ignore_index and weights `w * (targets != 255)`, so ignore px get weight 0 in numerator and denominator. Set C = background 0.2, ribbons 3, gridline 10, inactive 10, crack 20, others 1, as T11 row 6. Unit test in tests/test_bench_rows1.py, passed. WAVE3_REVIEW's "ignore_index fix" needs no code change.

### 3. Fairness record, G16 (PASS, one column added here)
| Row | Params total = trainable | encoder.* | GFLOPs 512 (request) | Output stride (E, CPU build) | Peak MiB | s/step | Steps x batch |
|---|---|---|---|---|---|---|---|
| house PF | 26,075,672 | 21,278,400 | 148.0 | 1 (encoder 32) | 5,736 cv02 | 0.18 | 20k x 8 |
| dlv3p | 22,437,096 | 21,278,400 | 62.4 | 4 (encoder 16, x4 bilinear head) | 3,396 | 0.070 | 20k x 8 |
| unet | 24,433,432 | 21,278,400 | 63.4 | 1 (encoder 32) | 3,468 | 0.100 | 20k x 8 |
| pratt | 22,437,096 | 21,278,400 | 62.4 | 4 (encoder 16) | 3,012 | 0.060 | 20k x 8 |
| hanifi | 23,750,424 | 14,713,536 | 199.0 | 1 (encoder 32) | 4,766 | 0.145 | 20k x 8 |
| ucf | 39,633,368 | 23,501,760 | 326.4 | 8 (encoder 8, x8 bilinear head) | 6,322 | 0.215 | 20k x 8 |
- E: parameter counts match the request exactly. Output stride is in the card headers but not in the request table; given above. Every row trains 20,000 steps of 8 images (160k images), = baseline; no row flagged for steps or images. Pretraining: ImageNet for all. Recipe: house PF; pratt carries the paper's loss (stated). ucf is 2.2x house GFLOPs (1.2x step time): the request prints the PF 2-seed ensemble rule (G16). GFLOPs not re-measured by me.

### 4. Weights (PASS)
- E: md5 on gaint HF cache = cv02 /tmp/noob_el/cache/hf cache = fresh download in bench_rows1_io/weights/dl: R34 f57b430554b18e1238c4f92eac566544, R50 646f731d7a6946d93ac9f84d6ba4f038, VGG16 b699ccbfbb18925f697dd13013b7dcc9. cvcard.py on cv02: each variant's card md5 = the cv02 file md5. HF API records: gated false, licence "other" (3 of 3). WEIGHTS.tsv records source URL, md5, licence, torchvision origin.
- E: offline load: cq.sh exports HF_HUB_OFFLINE=1 and env.sh sets HF_HOME=/tmp/noob_el/cache/hf; the 5 cv02 smokes started and trained under that; my gaint CPU builds loaded with HF_HUB_OFFLINE=1.

### 5. Deploy and data (PASS)
- E: fresh `git archive 52e3f14` (review/rvw/arch_52e3f14) checked against cv02's CODE.md5: ARCHIVE_OK 640 files, file lists equal; CODE.md5 641 lines, md5 daa2c5a771dce6d5e6f9d8a1881e67eb. On cv02: REVISION 52e3f149..., CV02_CODE_OK. Extra files there are only __pycache__ from the smokes; no runs/ or dumps/ dir; 0 r1_* in experiments.
- E: data: DEPLOY.md5 d6063fd83d20e656612540edda702cbe (cv02 = gaint stage), md5sum -c OK; ROOTS_OK; roots line diff vs gaint 0 and 0; both `asserts: OK (0 forbidden of 167; 0 of 330 groups split; held-outs partition 532; lists = cv5v2.json)`; masks CV02_MASKS_OK, 1,596 lines, 0 not in gaint MANIFEST (9c0e0687); review_w1g.py on cv02: ALL PASS, 57 PASS, 0 FAIL (532 mask links, wrong 0, dangling 0; ignore px strict 0, masks 3,484). labeled, masks_v11, meta, roots, roots/cv5v2_v11_f0 are dr-xr-xr-x.

### 6. Jobs (PASS)
- E: /tmp/noob_el/bench_q/rows1/jobs.txt md5 0069cb429328f5590d9e892420a12a04 (= gaint realq copy), r--r--r--. My script rebuilt the expected 50 lines (seed 5 block: dlv3p, unet, pratt, hanifi, ucf, folds 0-4 each; then seed 6 the same; root cv5v2_v11_f<k>, gate = card gate, dump gate 6200, logp 1, extra empty) and compared: **exact equal, order included**; names unique; 10 per row; each card gate = peak + 2,048. 0 r1_* names in B/experiments; no runs/ or dumps/; Q holds only jobs.txt, LPG (1), MAXC (8); no bench_q_rows1 session. Dump command = W1 keys (bench_infer fp32, `--logp`, forbidden list), the same DCMD code as W1-C.
- E: gaint /home/noob/work/bench_relay/rows1 does not exist.

### 7. Safety on cv02 (PASS)
- E: lane test (test_other_on.sh 715166a0) on cq.sh of 52e3f14: 13 of 13 PASS, 0 FAIL. cq.sh 5f13e5ac = d3a3280 (bench/q diff 0 lines); read in full: lane rule sums other users' MiB per GPU, our runs only from live Q/pids PIDs, so the finished W1-C queue (and any other queue dir) counts as another user; LPG 1 enforced; stop only via stop_verified on a recorded PID.
- E: live lanes, read-only, 23:19 UTC: GPUs 0-6 qualify, GPU 7 excluded (t25089 7,776 MiB); awk sums agree; 0 bench_* tmux sessions on cv02; load 1.3 of 64 cores.
- E: `git grep -nE "pkill|killall|pgrep|xargs.*kill"` over 52e3f14 bench/q: 0. All `kill` uses are `kill -0` probes or SIGTERM / SIGKILL to a verified PID (bench_lib.sh).
- E: PID files: smoke 2 pid file 3364836 and its cmdline file starts `/tmp/noob_el/el-fault-detection/.venv/bin/python -u scripts/train.py --exit_after_step 50`; 12 `pid <job> <pid> (python; parent <pid>)` lines in the two smoke logs.
- E: relay_w1c.sh 74a2ec3d (read in full): ssh -n -a -o ForwardAgent=no BatchMode, only read commands on cv02, refuses overwrite. Stage /home/noob/work/bench_rows1_io/stage/bench_52e3f14: md5sum -c OK, REVISION 52e3f149..., CODE.md5 daa2c5a7.

### 8. Smokes (PASS)
- E (rows1_smoke launch.log, deploy b2ea066, same model code as 52e3f14): all 5 rows `config OK (= card)`, `startup line OK: Labelled: 425 (.../cv5v2_v11_f0/splits/train.txt)  unlabelled: 0 (-)  val: 107  test: 107`, `trained ... rc=3` (by design), `Traceback lines 0`. NaN: stdouts already removed, so I could not re-count; the builder's count 0 (BUILD_LOG 04:04:38) stands.
- E (rows1_smoke2, deploy 52e3f14): ucf smoke armed line with deploy 52e3f149 (CODE.md5 OK), config OK, startup line OK, rc 3; dump dry test of the 300-step dlv3p fixture rc 0, RUN.md5 111 files, end line `(0 trained rc 0, 1 dumped rc 0, 1 RUN.md5 of 2 jobs)`.
- E: peaks recomputed by me from both gpumem.log files: smokes 3,396 / 3,468 / 3,012 / 4,766 / 6,322; dumps 1,660 / 1,970 / 1,660 / 2,916 / 2,274; = request.
- E: outputs removed (0 smoke/dumptest r1 dirs in B/experiments; no runs/, dumps/). Nothing of this tranche runs: no python under bench_52e3f14 / bench_b2ea066 on cv02, no rows1 or relay session on gaint except my finished check session.

## Launch commands checked (unchanged from the request section 4)
Queue (G):
`ssh -n -a -o BatchMode=yes cv02@10.8.1.106 'B=/tmp/noob_el/bench_52e3f14 Q=/tmp/noob_el/bench_q/rows1 SES=bench_q_rows1 DEPLOY=52e3f149f8244e6399c0a01dcf8c6b36874d219d JOBS_MD5=0069cb429328f5590d9e892420a12a04 DATA_MD5=d6063fd83d20e656612540edda702cbe bash /tmp/noob_el/bench_52e3f14/bench/q/cv02/cq_setup.sh'`
Must print `cq_setup: bench_q_rows1 armed: gpumem <pid> queue <pid>` and `cv02 q armed: 50 jobs (md5 0069cb42...) ... deploy 52e3f149... (CODE.md5 OK) ... LPG 1, MAXC 8 ... cq 5f13e5ac`; within about 6 min `r1_dlv3p_r34_pf_f0_s5 config OK (= card)` and `startup line OK: Labelled: 425 ...` (C `tail -20 /tmp/noob_el/bench_q/rows1/launch.log`).
Relay (G), first `cd /home/noob/work/bench_rows1_io/stage/bench_52e3f14 && md5sum -c --quiet CODE.md5 && echo OK && md5sum bench/q/cv02/relay_w1c.sh` (OK, 74a2ec3d...), then
`tmux has-session -t "=bench_relay_rows1" 2>/dev/null || { test ! -e /home/noob/work/bench_relay/rows1 && mkdir -p /home/noob/work/bench_relay/rows1 && tmux new-session -d -s bench_relay_rows1 "B=/tmp/noob_el/bench_52e3f14 Q=/tmp/noob_el/bench_q/rows1 RD=/home/noob/work/bench_relay/rows1 N=50 NAMES_RX=^r1_ POLL=300 bash /home/noob/work/bench_rows1_io/stage/bench_52e3f14/bench/q/cv02/relay_w1c.sh"; }`
Stop: C `touch /tmp/noob_el/bench_q/rows1/HOLD`; a run only by its PID in Q/pids/<name>.pid after printing its cmdline. Relay: G `touch /home/noob/work/bench_relay/rows1/STOP`.
S: all preconditions of cq_setup hold now (session absent, Q unarmed, jobs md5, REVISION, CODE.md5, LPG 1, no existing experiments). Nothing starts on gaint's GPU.

## Notes for the lead (S, none blocks the launch)
1. Dump near-ties: dumpfmt.check_cell fails a cell when two non-crack logits round to equal log-probabilities and |m| is large. Monotone float subtraction can only create a tie, not reverse the order, so this needs a difference within float rounding; the 300-step dlv3p fixture had 0 such px on 107 cells and 45 W1-C dumps passed. Watch for `dumped dump_r1_... rc=1`: that run gets no RUN.md5 and is not relayed; latest.pth stays on cv02 (lost on a cv02 reboot) and can be re-dumped. Any change to the dump checker needs its own review.
2. F51 dumps (T11 frame) are not in this job list. F51 is not on cv02 (pool cells only); they can be made on gaint later from the relayed slim.pth (bench_infer reads only step and models).
3. gaint disk: 174 GB free on /home/noob/work now. The rows1 relay brings about 56 GB and W2a plans about 59 GB: about 115 GB in all, about 59 GB margin. Check `df` once both are running.
4. The request table lacks output stride (given in item 3 above). Weight licence "other" / torchvision weight terms remain a user question before a public release (request 7).
5. With LPG 1 and GPU 7 taken, at most 7 runs run at once; MAXC 8 does not bind.
