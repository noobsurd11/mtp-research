# 14. Code and infrastructure: where everything lives and how a run is made

## What this covers
This is the map of the machinery behind every number in this project:
- where the code, data, runs and results sit, on the local laptop and on the two GPU servers (gaint and cv02);
- how the training code is organised and what each important config option does, with the code location;
- how runs are launched, queued and re-scored;
- how a local `results/pN/` folder is produced from server outputs;
- which commit, machine and folder belong to each experiment;
- recipes for finding a specific thing (a run's config, log, scores).

Read 07_methodology_rules_and_statistics.md for *why* runs are set up this way (step matching, final weights, one machine per comparison). This file covers *how*.

**Update 30 Oct 2026 (additive):** §1.2b (gaint worktrees `el_f1`, `el_f2`, `el_f3`, the memory rule, `run_one.sh` locks and spacing, two-opening scoring), §1.3b (Track D/M deployments), a dated note in §3.1 (the rc bug recurred), throughput rows in §3.3 and §5b (experiment map for 24 to 30 Oct). Taken from the team files, not from a fresh server listing; sources are named in each part.

**Update 1 Nov 2026, ~21:00 IST (additive):** §1.2d (worktrees `el_thin`, `el_hc`, `el_f8`; the shared GPU gate; the PF2, THIN, nq and A8-scoring queues; gates from measured peaks, GS 9,900; frozen scorer sets; the data-root trick against the trainer's end-of-run test pass; the gaint event watcher; weights and the sam2 venv) and §5c (experiments of 31 Oct to 1 Nov). Sources: `team_2026-10-31_next/`, doc 20.

Everything below was checked on 11 Oct 2026, about 22:00 IST, by listing files, reading code and running `git log` / `nvidia-smi`. Status then: P13 and P14 done; P15 (gaint) running, 5 of 6 runs re-scored; P16 SSL arms running on cv02 (ETA about 03:00 to 04:30 IST on 12 Oct). Later: both finished and were analysed by 12 Oct 05:30 IST; server state at the 13 Oct close is in doc 15 §1b. Updated 13 Oct ~16:30 IST for P17 and P13 Amendment 2 (worktree `el_p17`, deployment, `ssl.decouple_decoder`, scripts) and the cv02 backup on gaint; state after P17 is in doc 15 §1c.

## Sources
- gaint training repo `/home/noob/work/el-fault-detection` (README.md, `src/`, `configs/`, `scripts/`, `tests/`) and worktrees `/home/noob/work/el_p13`, `el_p14`, `el_p16`, `el_p17`; the cv02 backup `/home/noob/work/cv02_noob_el`.
- cv02 deployments under `/tmp/noob_el/` (`el_p6`, `el_p7`, `el_p11`, `el_p13`, `el_p14`, `el_p16`, `el_p17`, `diag/`, `ext117/`), their `REVISION` files, `gpu_queue_p16.sh`, `launch_set_p16.sh`.
- Local research repo `~/mtp/research`: `scripts/`, `scripts_cv02/`, `scripts_gaint/`, `protocols/`, `results/*/README.md`.
- Memory notes `~/.claude/projects/-home-yugma/memory/server-runs-tmux-parallel.md` and `mtp-el-ssl-project.md`.
- Commands run: `git worktree list`, `git log --oneline`, `cat REVISION`, `nvidia-smi --query-gpu=name,memory.total`, `ls`, `tmux ls` (read-only).

---

## 1. Where everything lives

### 1.1 Local machine (the user's laptop, `~/mtp`)
| Path | What it is |
|---|---|
| `~/mtp/research/` | The research notes repo (local git, **no remote**; `git remote -v` is empty; 64 commits in total as of 11 Oct 21:13 IST, 34 of them dated 11 Oct). This is where protocols, results, reports and analysis scripts live. Commits here are made by the assistant with the session trailer. |
| `~/mtp/research/protocols/` | One locked protocol per experiment: `P1_overfit_check.md` ... `P16_label_fraction_curve.md` (no P3 file; P3 was a read-only re-score, see `results/p3_label_versions/README.md`). A protocol is committed before its runs start. |
| `~/mtp/research/results/` | One folder per experiment (`p1`, `p2`, `p3_label_versions`, `p4_feature_probe`, `p5_region_pl`, `p6` ... `p14`, `p13_audit`, `e1`, `figures`, `p15`). `p15/` so far holds only `dedup.py` (the UCF-EL vs BenchmarkEL leakage check, commit `c9f5562`); its results and `p16/` are created by the post-processing scripts when the runs finish. |
| `~/mtp/research/to_human/` | Reports written for the user: `situation_report_2026-10-08.md`, `directions_2026-10-10.md`, `proposal_reframe_2026-10-11.md`, `midterm_deck_outline.md`, `results_2026-10-12.md` (the morning summary, being filled as results land). |
| `~/mtp/research/scripts/` | Local analysis scripts (rules, bootstrap, figures, post-processing). See section 4. |
| `~/mtp/research/scripts_cv02/` | Copies of what was run on cv02: queue/launch scripts, queue spec files, E1 scorer and aggregator, the P16 auto-launcher. |
| `~/mtp/research/scripts_gaint/` | Copies of gaint-side scripts used for probes and scoring (P1, P2, P4, P5 scripts; `rescore_label_versions.py`, `per_image_scores.py`, `score_histograms.py`, `overlay_figure.py`). |
| `~/mtp/research/analysis/` | `alhvr_audit.md` (audit of the earlier ALHVR work), `papers_metrics.md` (how papers define their metrics). |
| `~/mtp/research/data_analysis/` | `benchmark_el_report.md`, `ucf_el_report.md` (first-hand dataset analyses). |
| `~/mtp/research/literature/` | `survey.md`, `papers_index.md`, `reading_list.md`, `notes/` (26 per-paper and per-topic notes), `pdfs/`, `pdfs_inst/` (local PDFs; never redistribute). |
| `~/mtp/research/papers/` | PDFs obtained through institute access. **Local only; never redistribute or upload.** |
| `~/mtp/research/handbook/` | This handbook. |
| `~/mtp/research/results/escdd_audit/` | The E-SCDD audit (12 Oct):<br>• `README.md`;<br>• `scripts/`: download, inventory, crossref, analysis, dups_mad, ours_vs_escdd, montage. Run with `.venv/bin/python -I`;<br>• `out/*.json`;<br>• `escdd_samples.png`. |
| `~/mtp/research/.venv/` | Python env used for the local analysis scripts (`.venv/bin/python scripts/...`). |
| `~/mtp/datasets/` | Local dataset copies:<br>• `BenchmarkELimages/dataset_20211104/` (images/masks per split, class list CSV);<br>• `UCF-EL-Defect/`;<br>• `splits_benchmark/` (train/val/test, seed folders, external pool manifest);<br>• `splits_ucf_cv02/`.<br>Added 12 Oct (doc 17), all hash-verified:<br>• `escdd_full/` (HF `snt-ubix/escdd`, 903 image/mask pairs + CSV, JSON, README);<br>• `escdd_mirror_shivahanifi/` (HF mirror with no-padding variants);<br>• `BenchmarkEL_releases/dataset_{20221008,20220723}/` (originals only, GitHub tree `768b5e7`);<br>• the HF API listings `escdd_full_hf_api.json` and `escdd_mirror_shivahanifi_hf_api.json`. |
| `~/mtp/MTP_session_handoff_2026-10-07.md` | The handoff document from before this work started (old-era context). |

### 1.2 gaint (`ssh noob@172.18.22.20`)
- **GPU:** 1x NVIDIA RTX PRO 4500 Blackwell, 32,623 MiB (`nvidia-smi`, 11 Oct).
- **Main repo:** `/home/noob/work/el-fault-detection`, branch `main` at `24590fb` (P11 switch). GitHub remote `origin = github.com/noobsurd11/el-fault-detection` (pushing needs the user's OK). 82 commits.
- **Worktrees** (`git worktree list`): one per experiment that needed new code, so running lanes never see code change under them.

| Worktree | Branch | Commit | Adds |
|---|---|---|---|
| `/home/noob/work/el-fault-detection` | main | `24590fb` | P11 `ssl.labeled_aug=supervised` |
| `/home/noob/work/el_p13` | p13 | `bac5264` | P13 `ssl.student_forward=separate`, `ssl.cutmix_p` |
| `/home/noob/work/el_p14` | p14 | `be67787` | P14 `loss.supervised=tol_dice`, P15 `model.encoder_init` (on top of `bac5264`) |
| `/home/noob/work/el_p16` | p16 | `d51b60f` | P16: SSL allowed at `labeled_fraction` 1.0 with `data.unlabeled_pool=external` (on top of `bac5264`; it does **not** contain `be67787`) |
| `/home/noob/work/el_p17` | p17 | `f2f20d3` | P17 `ssl.decouple_decoder`, `ssl.decouple_ema` (on top of `bac5264` only); +6 tests in `tests/test_ssl_split.py` |

- **(Added 30 Oct)** Worktrees added 29 to 30 Oct (`el_f1`, `el_f2`, `el_f3`) and the Track M base `el_m`: §1.2b.
- **Backup of cv02 (13 Oct):** `/home/noob/work/cv02_noob_el/` holds copies of cv02 `/tmp/noob_el` (`el_p6`, `el_p7`, `el_p11`, `el_p13`, `el_p14`, `el_p16`, `el_p17`, `el-fault-detection` without `.venv`, `diag` without `g_import`/`pylib`, `ext117`, `results_to_sync`; no data). Every file was checked by manifest and every checkpoint by MD5 against cv02. Copied through the user's laptop, because cv02 and gaint cannot log into each other and cv02's login is shared (no ssh agent forwarding or keys there). Runs after 13 Oct need another pass.

- **Commit history of the training code** (main, newest first, from `git log`): `24590fb` P11 switch; `0367079` P7 label-safe SSL views + `tolerant_pl` + `rare_frac` logging; `824fab0` P6 switches (`data.mask_subdir`, `data.augmentation=labelsafe`, `smp_unetpp`, `ce_dice`) and P3-P5 probe scripts; `4474d04` and `28686c0` P1/P2 scripts; earlier commits are the old-era low-label queue (`sl_*pct_b8`), BN recalibration, external pool preparation (`0136855`, `46dfe92`).
- **Inside each repo/worktree:** `experiments/<run>/` (run outputs), `experiments/<run>.stdout` and `<run>.rescore.log`, `reports/` (re-score JSONs per experiment, e.g. `reports/p12/`, `el_p14/reports/p15/`), `data/` (`labeled/images`, `labeled/masks_coded` = old labels, `labeled/masks_escdd` = revised labels, `escdd_masks/{train,val,test}`, `splits/`, `unlabeled/`, `ucf_el` symlink to `/home/noob/work/datasets/UCF-EL-Defect/training`).
- **Old-era runs** still in `el-fault-detection/experiments/`: `sl_*pct_b8`, `sl_20pct`, `mt_20pct*`, `alhvr_20pct*`, `sa_*`, `pratt_unet_set*`, `ucf_*`, `pilot_*` (see 06_history_phase0_phase1.md; their Mean Teacher results are invalid, see 13_problems_pitfalls_open_issues.md).
- **tmux sessions** (`tmux ls`, 11 Oct): `p10g`, `p12g` (finished lanes), `p15g` (P15 lanes, running), `noob-0`.
- **The held extpool queue: leave untouched.** On 8 Oct the old `extpool_20261007` queue (SemiCE Mean Teacher on the external pool) was held by hand while SemiCE was under audit. The log `experiments/repro/night_queue_extpool_20261007.log` ends with "HELD by hand: semi_ce under audit. Relaunch: bash scripts/resume_queues.sh extpool_20261007". The crontab only has an `@reboot` line for the `lowlabel_20261006` queue. Standing instruction: do not relaunch, edit or kill it.
- `REVISION` in the main repo reads `dfa4fd6...` (an old deploy marker); `REVISION_P6` reads `824fab0...`. Trust `git log` / the worktree commit rather than this file on gaint.

### 1.2b gaint, 29 to 30 Oct: worktrees, memory rule, run locks, scoring (added 30 Oct)
Sources: `team_2026-10-29_features/log.md` (29 Oct 12:40 to 30 Oct 11:18), `protocol_100.md` "Code" and "Lanes", `coach_100.md`, `SESSION_RECORD_2026-10-28_to_30.md` §2, §9, §11.

**Worktrees**

| Worktree | Branch, base | Deploy commit | Adds |
|---|---|---|---|
| `el_m` | Track M base | `1be64e1` | the Track M SUP100 code (= cv02 `el_mt5`); identity reference for all f-worktrees |
| `/home/noob/work/el_f1` | f1, from `1be64e1` | **`603e0d5`** | `model.encoder_init` (load an encoder from a file); MIM pretraining: `pretrain_mim.py`, `spark.py` (SparK sparse MIM), `build_mim_pool.py` (pool rules R1 to R4 + 256 monitor cells), encoder lr 0.2× with a 1,000-step ramp after unfreeze, clip 5, `mim_step0.pth`, monitor loss (commits `fe31831`, then `603e0d5`; suite 264 passed, 3 skipped). `REVISION` = 603e0d5. Used by MIM pretraining, A5c-f1 and MIM5 |
| `/home/noob/work/el_f2` | f2, from `603e0d5` | **`2751aa8`** | `model.decoder_init` + DDeP pretraining (`pretrain_ddep.py`, `c33ed65`); the CP stream (`copy_paste.py` stream id 3, trainer cp hook, `cp_preview.py`, `42bf7d1`); `cp_decoy.py` (`c60d6e8`); `am_map.py` (val-only AM check, `9d37026`); the P3 residual fix (`2751aa8`; suite 278 passed). `REVISION` written after the runs (= HEAD, 0 tracked files modified). Used by DDeP pretraining (cv02 deploy), DDeP5 and CP5 |
| `/home/noob/work/el_f3` | f3, from `2751aa8` | **`e544133`** | CP at 100% (`20aad52`: no unlabelled-train list at `labeled_fraction` ≥ 1, pool backgrounds only, optional `cp.library_exclude`); the PF switch `training.encoder_pf` {freeze, ramp, lr_mult, wd}: two param groups (group 1 = `encoder.*` with lr × lr_mult and its own wd, multiplier 0 before `freeze` then a linear ramp), BN in train mode, RNG unchanged, encoder lr on its own "PF encoder lr=" log line. Suite 285 passed, 3 skipped. Used by protocol_100 |

- Identity checks (E, `log.md`; `team_2026-10-29_features/identity_f1.txt`): `el_f1` with the switch off equals `el_m` to step 1,000 incl. val; `el_f2` with no switch equals `f1_A_5pct_s0` for 2,000 steps; CP λ 0 equals no switch for 1,000 steps; at 100% opts, `el_m` vs `el_f2`, `el_m` vs `el_f1` and `el_f2` + `encoder_init=mim_step0` are all identical for 1,000 steps. protocol_100 adds its own gates at e544133 (doc 19 §7).
- Masks: `el_f1/data/escdd_masks` are per-stem symlinks to `labeled/masks_escdd` (pixel md5 8bcd3691 = cv02), because gaint's own `data/escdd_masks/test` holds scuff at 2 cells (doc 13 A15). `el_f2` and `el_f3` link to the same.
- Run names: `f1_A_5pct_sK`, `f1_MIM_5pct_sK`, `f1_mim_pre_s0`; `f2_DDeP_5pct_sK`, `f2_CP_5pct_sK`, `f2_ddep_pre_s0` (cv02); `f3_SUP_100pct_sK`, `f3_SUPPF_100pct_sK`, `f3_MIMPF_100pct_sK`, `f3_CP_100pct_sK`.
- tmux sessions (from the log): `f1g` (MIM pretraining and MIM5 lanes), `f2chk` / `f2chk2` (f2 identity and smokes), `f2g` (f2 lanes), `f100` (100% identity, smokes, then the protocol_100 queue), `b1` (B1 audit, CPU), `b2` (B2 pool mining, CPU, from 12:09 IST 30 Oct). On cv02: `f2ddep`.

**Memory rule (team-lead, 29 Oct 13:31; session record §2)**
- gaint has one RTX PRO 4500 (32.6 GB). Root's `finllm_chat.py` holds 5.9 GB and must never run out of memory, so **≥ 2 GB stays free at all times.**
- **Start gate per run = own measured peak + 2 GB:** fine-tune 6.8 GB → gate 9,000 MiB; CP 9.5 GB (measured 9,526 MiB) → gate 11,600 MiB (lowered from a 12,000 MiB estimate, `run_one.sh` v5). End-of-run rescoring (batch 8, bf16, no grad, about 3 GB) waits for 6,000 MiB.
- Packing at 100% (`protocol_100.md`): 3 fine-tunes leave 4.9 GB; 2 CP + 0 fine-tunes about 6.4 GB; 1 CP + 2 fine-tunes 2.2 GB.

**`run_one.sh` locks and spacing (doc 13 D22, D25, D27)**
- f1g `run_one.sh` v3 (md5 969f7676): an atomic claim dir per run, so two lanes can never start the same run.
- A HOLD file pauses a lane before its next run. The first, shared HOLD also blocked the MIM5 lanes; replaced by an A-lane-only `HOLD_A` (md5 6f6fe611).
- f2g `run_one.sh` v3 (md5 8453c0e5): an atomic start gate (flock check-and-stamp) and ≥ 120 s since the last start, after three runs started on one free-memory reading. v4 (md5 176ea9c9) uses the same gate before end-of-run rescoring; v5 (md5 02287430) sets the CP gate from the measured peak. Older versions are kept beside each new one.
- The protocol_100 smokes used a 90 s spacing (`scripts/f100_smokes_gaint.sh`).
- `run_one.sh` captures the training rc before any `$(date)` (all versions). The status lines of several other scripts did not (§3.1 note of 30 Oct).

**Two-opening scoring for protocol_100 (log 30 Oct 11:18)**
- Script `scripts/f100_post_gaint.sh` (md5 a39362b2), triggered by `scripts/f100_postwatch_gaint.sh` (md5 71c24ea2).
- **Opening 1:** the 15 fine-tunes (SUP100-g, SUP100-PF, MIM100-PF) → `el_f3/reports/f100/post_opening1/`.
- **Opening 2:** CP100, plus the E3b decoy and crack px on crack-free cells → `post_opening2/`. SUP100-g's opening-1 files are reused unchanged (manifest re-checked).
- Each pass: rescore, m0 default / τ 0 / τ 1, the τ 0 check, LA, the encoder cosine table at 20k, a manifest. Final line `[date] f3 opening<N> scoring done: post rc=<rc>` in `el_f3/reports/f100/launch.log`, with rc captured before `date`.
- Conditions (doc 12 D49): CP100 runs to the end whatever opening 1 shows; no protocol change after opening 1.

**Speed rules for protocol_100 (coach_100.md).** bf16 autocast is already on (`configs/base.yaml`: `amp: true, amp_dtype: bfloat16`). Val only at steps 0 and 20,000 if a 2,000-step bit-identity check passes. An optional 4th lane via `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True` only after a 1,000-step identity and ≤ 5.5 GB reserved per fine-tune. No TF32, channels_last, `cudnn.benchmark` or torch.compile.

**As launched (v1.1, 30 Oct 12:05:34 IST; `protocol_100.md` v1.1, `log.md` 12:05):** queue `el_f3/reports/f100_queue.sh` (md5 e4cb4ad3), `training.val_every=20000` (gate 4 passed), at most 3 concurrent runs, no expandable_segments (gate 7: 6,442 MiB reserved per fine-tune, 4 × 6.44 + 5.9 = 31.7 GB > 30.1 GB allowed), postwatch `f100_postwatch.sh` (md5 f046bb5f). CP100 jobs wait at the queue's first CP job for `el_f3/reports/f100/CP_GO` or `CP_STOP`, written by the gate-6b script `f100_gate6b2.sh` (md5 80211978) with coach's three conditions (doc 12 D50).

### 1.2c gaint, 30 to 31 Oct: protocol_100 operations, memory logging (added 31 Oct)
Sources: `team_2026-10-29_features/log.md`, `protocol_100.md`, `scripts/`.
- **Queue and openings (`el_f3/reports/`):** `f100_queue.sh` (strict order; waits at the first CP job for `f100/CP_GO` or `CP_STOP`; pauses while `f100/HOLD` exists); `f100_postwatch.sh` fires `f100_post.sh opening1|opening2`; each start or scoring pass takes the flock gate `f100/gate.lock` with ≥ 120 s spacing. End lines in `f100/launch.log`: `f3 opening<N> scoring done: post rc=N`.
- **`f100_resume.sh`:** the post-reboot resume (`train.py --resume`, stdout appended after a marker line, "trained <run> rc=N (resumed)").
- **`f100_unhold.sh`** (md5 f64cd600, tmux `f100r:unhold`): lifts HOLD on the opening-1 done or NOT-scored line; if the post process is gone for 2 min it first writes "f3 opening1 post FAIL: ...".
- **`f100_gpumem.sh`** (local `scripts/f100_gpumem_gaint.sh`, md5 5c6b8c6a; tmux `f100r:gpumem`): writes "time free used | pid:label:MiB" to `f100/gpumem.log` every 10 s, every 1 s while a scoring process is on the GPU; PID in `f100/gpumem.pid` (stop only by that PID); stops 60 s after the opening-2 end line. Ran 01:45:40 to 07:08:34 31 Oct.
- **Measured GPU peaks (MiB, nvidia-smi per process; scoring measured in opening 2 with finllm alone):** rescore_label_versions 4,398; m0_audit and m0_audit_tau 4,002; rescore_logit_adjust (LA) 5,106; cp_decoy 3,292; CP100 run 9,524; root's finllm 5,876.
- **Gates now:** start gates = measured peak + 2 GB (fine-tune 9,000, CP 11,600 MiB). **Concurrent scoring passes: 7,154 MiB** (LA peak + 2,048). The 6,000 MiB gate inside `f100_post.sh` assumed ~3 GB passes; it is safe only with finllm alone on the GPU.
- **Local analysis (team folder `scripts/`):** `f100_post_local.sh` (opening 1), `f100_post_local_o2.sh` (opening 2), `f100_o1_extra.py` (E1 split and crack px on crack-free cells; takes ARM=DIR pairs), `watch_f100.sh` (local watcher, run as a tracked job; prints its PID).
- **D:** `el_f3/reports/d/` (`d_infer.py` md5 129edac4, `--only-r34-10` mode; CPU fp32; outputs in `reports/d/out/`, pulled to `d_checks/`).

### 1.2d gaint, 31 Oct to 1 Nov: new worktrees, shared gate, queues, data roots, frozen scorers (added 1 Nov)
Sources: `team_2026-10-31_next/log.md`, `build_*.md`, the protocols' build records.
- **Worktrees (all branched from e544133; each deploy frozen until its opening ends):**
  - `el_f3` (e544133, unchanged): PF2 (`reports/pf2/`), PF2E (`reports/pf2e/`), the RN ensemble secondary (`reports/d_pf2rn/`).
  - `el_thin` (branch thin): Skeleton Recall, clDice, B3 scuff class (opt-in, default off). Code 9461ecc, smoked d93d9a1, **run deploy c9bbb02**; `reports/thin/` (q, post, post_extra, smoke). CPU identity with flags off = e544133 (house and PF).
  - `el_hc` (branch hc): `data.synth_halfcut` loader transform. **Deploy c2e6973** (`smoke_hc.sh` 5a5c707b); p = 0 bit-identical to SUP100-PF over 2,000 GPU steps (H0).
  - `el_f8` (branch f8): `model.name=hrstem_unetpp` (timm ConvNeXt-T / Hiera-T + a stride-2 stem + the house U-Net++ decoder), `model.backbone_drop_path`, `reports/enc_cosine_hr.py` d72f4324. **Deploy c280e8c2**; house and PF IDENTICAL to e544133 on CPU.
- **Shared GPU gate** `/home/noob/work/gpu_gate` (runner, `gpu_gate.sh`): flock `gate.lock`, start only if free ≥ the job's gate, ≥ 120 s spacing, a HOLD file, `gate.log`; a `FAST` file makes the gpumem loggers sample every 1 s (set for whole openings and smokes).
- **Queues:** PF2 `el_f3/reports/pf2/scripts/pf2_queue.sh` (twohead, 3 lanes, at most 1 RN50); THIN `el_thin/reports/thin/q/thin_queue.sh` 46b871c1; **nq** `/home/noob/work/nq/` (`nq_queue.sh` 156c6936, jobs 5cb4bad9: A8 / A8c s0-1 and HC s5-9, 3 lanes) with the HC opening in `nq/hc/` (FROZEN a23994c4, trigger `hc_postwatch.sh`); A8 scoring `/home/noob/work/a8_score/` (`a8_score.sh` 75a57c9c, MODE=check / wait, HOLD for CPU windows). Every queue re-diffs each run's `config_used.yaml` against its expected one-change diff and HOLDs on a mismatch.
- **Gates now (MiB; measured peak + 2,048):** training R34 9,000, RN50 13,234, SKR 9,100, CLD 10,500, B3 9,000, HC 9,000, A8 / A8c 11,400. **Scoring beside other jobs: GS 9,900** (PF2's LA pass over 15 runs, 7,758 measured on 1 Nov). Measured peaks: RN50-PF train 11,186; SKR 7,020; CLD 8,374; B3 5,738; HC 6,826; A8 / A8c 9,254; PF2 opening rescore_label_versions 6,020, m0_audit 5,254, LA 7,758; RN50 B5 dump 5,252. Rule: max(smoke peak, last real peak) + 2 GB.
- **Frozen scorer sets (coach writes FROZEN.md5; nothing listed changes before the opening):** PF2 `el_f3/reports/pf2/post_extra/FROZEN.md5` 475d78fb + `B5_DEVICE` cuda; THIN `el_thin/reports/thin/post_extra/FROZEN.md5` 584cabea; A8 `a8_score/scripts/FROZEN.md5`; HC `nq/hc/FROZEN.md5` a23994c4. calib's B5 scorer inside them: `el_metrics.py` 6e73ff11, `calib_dump.py` c172717e, `pf2_b5_hook.sh` e06dfc5f, `pf2_b5_pooled.sh` 873591ff (local copy `team_2026-10-31_next/ideas/scripts/frozen_pf2/`). The opening dump runs on GPU bf16, which reproduces m0 exactly; CPU fp32 differs by up to 0.0046 on pixel metrics, 0.0069 on inactive IoU and 0.0214 on component metrics (calib's 20-run check; coach, log 31 Oct 14:42).
- **Data-root trick (no code change):** the trainer evaluates the test split at the end of every run (doc 13 C18). A run that must read no test cell gets `data.root=<root>` with `labeled/` (symlink), `splits/train.txt` and `splits/val.txt` byte copies, and `splits/test.txt` = the held-out list. A8: `/home/noob/work/a8_root` (train 842f27c4, val 9dcccf00, test = val). B6 (planned): `b6_root_{0..4}` (folds 0-4 as in `b6_folds.tsv`) with val = test = fold k; on cv02 a fresh `labeled/` holding only the 532 train + val stems. Checks: split md5s, 0 real test / E1 stems, the CPU data-build line ("Labelled: N ... val: n test: n").
- **Event watcher (since 1 Nov 19:28):** one gaint watcher `/home/noob/work/runner_events/` (`rwatch.sh` f266e5cc, now `rwatch_v2.sh` a07d7490, tmux rwatch2) appends events from the queue / opening / smoke logs, Traceback counts (`grep -ho | wc -l`, never the stdout itself) and free < 2,048 MiB twice to `events.log`; stopped via its STOP file. Laptop side: one tracked waiter `lwait.sh` (d05cb68a) reads new events every 5 min and polls cv02 read-only every 15 min (gaint cannot reach cv02: no key there, by design).
- **Weights and venv:** `/home/noob/work/weights/` (`MD5SUMS`): SAM2 `sam2.1_hiera_tiny.pt` 6aa6761c, timm `sam2_hiera_tiny` c453c074, DINOv3 ConvNeXt-T `dinov3_convnext_tiny_lvd1689m_timm.safetensors` abf90463, DINOv3 ViT-S/16 d6f2118f. `/home/noob/work/venv_sam2` (SAM2 code from Meta's repo at a pinned commit; torch reused read-only from the house venv).
- **Recompute on gaint CPU (coach, since the laptop ran short of memory):** `/home/noob/work/coach_v/bin` (reads an opening's `post/` in place after `md5sum -c`; only text comes back).
- **CPU windows:** runner declares a critical window around each opening; other agents start no gaint CPU job inside it.

### 1.3 cv02 (`ssh cv02@10.8.1.106`)
- **GPUs:** 8x NVIDIA RTX A6000, 49,140 MiB each (`nvidia-smi`, 11 Oct). Shared with other users.
- **Everything of ours is under `/tmp/noob_el/`.** Note it is under `/tmp`: a reboot or cleanup could remove it. The local `results/` folders hold copies of everything needed for the reported numbers (re-score JSONs, per-image JSONs, histograms, E1 JSONs). Checkpoints are on cv02 and, since 13 Oct, copied to gaint `cv02_noob_el` (§1.2).

| Path | Contents |
|---|---|
| `el-fault-detection/` | Older code copy (`REVISION` `fe79e19`) whose `.venv` is the Python used by every cv02 run: `/tmp/noob_el/el-fault-detection/.venv/bin/python`. |
| `el_p6/` | P6 deployment, `REVISION` `824fab0`, own `data/`. |
| `el_p7/` | P7-P10 deployment, `REVISION` `0367079`. Its `data/` is the real data dir that later deployments symlink to. Reports `reports/p7`, `p8`, `p9`, `p10`. |
| `el_p11/` | P11 and P12 deployment, `REVISION` `24590fb`, `data -> /tmp/noob_el/el_p7/data`. Reports `reports/p11`, `reports/p12`. |
| `el_p13/` | P13 deployment, `REVISION` `bac5264`. Also hosts P13 Amendment 2 (BsM5 s3-4, session and reports `p13a2`), P16 Part A (`reports/p16/`, supervised references) and the P15 pretraining run (`experiments/p15_ucf_pre_dlv3p_r34`, log `reports/p15_pre.log`). |
| `el_p14/` | P14 deployment, `REVISION` `be67787`. Reports `reports/p14`. |
| `el_p16/` | P16 Part B (SSL arms), code `d51b60f` per `protocols/P16_label_fraction_curve.md` Amendment 1. **This dir has no `REVISION` file** (it was deployed from a tar export); the commit is recorded in the protocol and in `scripts_cv02/p16b_auto.sh`'s header. Reports `reports/p16b/`, auto-launcher log `reports/p16b_auto.log`, CutMix choice `reports/p16b/selection.txt`. |
| `el_p17/` | P17 deployment, `REVISION` `f2f20d3`, `data -> /tmp/noob_el/el_p7/data`. Runs `p17_BsD_5pct_s0..4` (session `p17run`; `reports/p17` is a symlink to `reports/p17run`), smoke runs `smoke_BsD`, `smoke_BsD_lowthr` (session `p17smoke`). `scripts/per_image_scores.py` and `score_histograms.py` copied from `el_p13`. |
| `diag/` | E1 and diagnostics: `e1_task_metrics_v2.py` (byte-identical to local `scripts_cv02/e1_task_metrics.py`), outputs in `diag/e1v2/` (124 JSONs on 11 Oct), logs `e1p11.log` ... `e1p14.log`, `e1p13.log`, `e1p17.log`, `e1p13a2.log`; `g_import/` (slim copies of gaint runs for E1); `bn_diag.py` (P13 audit); `p15_ucf_pre_dlv3p_r34.pth` (P15's pretrained UCF-EL encoder source). |
| `ext117/` | The unseen-module extension set: `images/`, `masks/`, `ignore/`, `manifest.csv`, `stems_eval.txt` (106 evaluated cells). See 03_datasets_and_splits.md and `results/e1/README.md`. |
| `env.sh` | Sourced before every run. It only sets cache and path variables (`XDG_CACHE_HOME`, `UV_CACHE_DIR`, `TORCH_HOME`, `MPLCONFIGDIR`, `PATH`). Do not copy its values anywhere. |
| `pvs3/`, `pvs3_env`, `results_to_sync/`, `state/`, `tools/`, `bin/`, `*.tgz` | Old-era material (UCF-EL PV-S3 runs, old ALHVR cv02 runs, old GPU-claim scripts, code tarballs). Not used by P6-P16. |

- **Data on cv02:** `el_p7/data/labeled/images` (582 PNG), `labeled/masks_coded` (old labels), `labeled/masks_escdd` (revised labels, used for training when `data.mask_subdir=labeled/masks_escdd`), `escdd_masks/{val,test}` (revised labels used by the re-scorer), `splits/`, `unlabeled/images_512` (11,938 external-pool images). The two revised-mask copies agree: on 11 Oct all 104 val+test masks in `escdd_masks/` were byte-identical (`cmp`) to `labeled/masks_escdd/`.

### 1.3b cv02, 24 to 29 Oct: Track D, Track M and DDeP deployments (added 30 Oct)
Sources: `team_2026-10-24_go/trackM/results_r*.md`, `results_final.md`, `SESSION_RECORD_2026-10-21_to_27.md` §11, `team_2026-10-29_features/log.md`.
- **Track M:** `el_mt` (`3c1b72b`; R2, R2c, R3 Part B), `el_mt4` (`0642889`; R4, data root `/tmp/noob_el/data_r4`), `el_mt5` (`1be64e1`; R5 and the FINAL scoring, `scripts/m9_final.py`). The M0 audit and R1 re-scored the existing SUP100 checkpoints (`el_p6` 824fab0, `el_p13` bac5264).
- **Track D:** probe, edge and labelled-set outputs are local in `results/trackD_probe/`, `results/trackD_edge/`, `results/trackD_labelset/`.
- **Copies on gaint:** `/home/noob/work/cv02_noob_el/` holds `el_trackD`, `el_mt*` and `trackM`, relayed through the laptop with MD5 on both hops (session record 21 to 27 Oct §11).
- **DDeP pretraining (29 Oct):** cv02 `/tmp/noob_el/el_f2` (`REVISION` 2751aa8, checked by the queue's data gate with the pool image-bytes manifest 855daabd = gaint), tmux `f2ddep`, A6000 GPU 0. Backup on gaint `cv02_noob_el/el_f2/experiments/f2_ddep_pre_s0/`.
- **cv02 at 10:51 IST 30 Oct:** 0 of 8 GPUs usable (each had other users' processes of 9 to 42 GB), so protocol_100 runs on gaint.

---

## 2. The training code (gaint repo; `el_p16` and `el_p14` are the newest variants)

### 2.1 Layout
| Folder | Files and role |
|---|---|
| `scripts/train.py` | Entry point. Loads a YAML config, applies `--opts` overrides, builds data streams, model, losses, and the `Trainer`; writes `experiments/<run>/`. |
| `src/data/` | `benchmark_el.py` (Dataset reading 512x512 grayscale images and index masks, class id 0-23 per pixel); `augmentations.py` (all augmentation pipelines); `stream.py` (deterministic batch streams); `splits.py` (`load_split`); `class_info.py` (24 class names; crack = 14, inactive = 11, padding = 7); `class_stats.py`; `ucf_el.py` (UCF-EL dataset). |
| `src/models/` | `model_factory.py` (`build_model`), `sa_unetpp.py` (from-scratch U-Net++, optional SA gate), `deeplabv3plus.py`, `self_attention.py`, `perturbations.py`. |
| `src/losses/` | `ce_dice.py`, `weighted_ce.py`, `semi_ce.py`, `confidence_ce.py`, `tolerant_pl.py`, `class_threshold_ce.py`, `alhvr.py`, `loss_factory.py`. |
| `src/trainers/` | `trainer.py` (supervised and Mean Teacher in one iteration-based trainer), `ssl_ops.py` (CutMix and `frozen_bn_stats`, P13), `ema.py`, `alhvr_trainer.py`, `alhvr_diagnostics.py`. |
| `src/evaluation/` | `metrics.py` (confusion-matrix metrics, relaxed crack recall), `evaluator.py`, `threshold_free.py` (binned AP), `runs.py`, `visualize.py`. |
| `src/utils/` | `config.py` (YAML with `defaults:` inheritance), `checkpoint.py`, `seed.py`, `jobs.py`. |
| `tests/` | 20 test files on main (`git ls-files tests`; `ls` also shows `__pycache__`), plus `test_ssl_split.py` (P13), `test_p14_p15.py` (P14/P15), `test_p16_full_label_ssl.py` (P16) on their branches. Protocols record the counts that passed (197 for P13, 205 for P14, 204 for P16). |

### 2.2 Configs and the `--opts` override
- `configs/base.yaml` holds the YAML defaults. Some keys default in code instead (`scripts/train.py` fallbacks): `data.mask_subdir` (`labeled/masks_coded`), `data.split_seed`, `data.augmentation`, `data.unlabeled_pool`, `ssl.labeled_aug`. `supervised.yaml`, `ssl_mean_teacher.yaml` and `alhvr.yaml` inherit it through `defaults: [base]` (`src/utils/config.py`, deep merge).
- `--opts a.b=c ...` overrides any key with dot notation; values are parsed as YAML (`apply_opts` in `scripts/train.py`). Example from `scripts_cv02/p13_queue.spec`:
  `ssl_mean_teacher.yaml seed=0 training.total_steps=20000 data.split_seed=0 data.labeled_fraction=0.05 training.labeled_batch_size=8 training.unlabeled_batch_size=8 data.mask_subdir=labeled/masks_escdd data.augmentation=labelsafe loss.t_pos=0.95 ssl.lambda_final=1.0 ssl.warmup_steps=2000 ssl.ramp_steps=2000 model.name=smp_unetpp loss.supervised=ce_dice ssl.labeled_aug=supervised ssl.student_forward=separate loss.consistency=tolerant_pl loss.tolerance_radius=2 ssl.cutmix_p=0.5`
- **The base defaults are old-era settings**, not the P-series recipe: `model.name: unetpp` (from scratch), `loss.supervised: weighted_ce`, `loss.consistency: semi_ce`, batch 4+4, `ssl.lambda_final: 1.5`; and the code fallback for masks is `labeled/masks_coded` (old labels). Every P6+ run overrides these on the command line. The exact option strings per experiment are in each protocol and in `scripts_cv02/*.spec` (and, for P16 Part B, in cv02 `el_p16/reports/p16b/p16B_queue.spec`). The config a run actually used is saved in `experiments/<run>/config_used.yaml`.
- New switches are added opt-in, with defaults that keep earlier runs bit-identical, and they are not written into `base.yaml` so older run configs stay resumable (comments in `scripts/train.py`).

**Base defaults that stay in force in the P-series** (`configs/base.yaml`): 20,000 optimizer steps; Adam, lr 1e-3, weight decay 1e-4, 200-step linear warmup then cosine to 0; gradient clip 1.0; bf16 autocast; `deterministic: true`; val every 500 steps; `latest.pth` every 2,000 steps; EMA alpha 0.999; input 512, normalisation mean 0.5, std 0.25.

### 2.3 Data and splits (`build_benchmark_data` in `scripts/train.py`)
- `data.labeled_fraction` f: 1.0 uses `data/splits/train.txt` (478 cells); f < 1 uses `data/splits/seed<k>/labeled_<P>pct.txt` with its complement `unlabeled_<P>pct.txt` as the in-domain unlabelled pool. Files exist for 2, 5, 10, 20, 50 pct (`ls data/splits/seed0`). `<P>` is `round(f*100)`, so 0.05 maps to `5pct`.
- `data.split_seed` k picks the subset. It defaults to the training seed, so the P-series always passes `data.split_seed=0`: the labelled cells stay fixed while `seed=` varies the training seed.
- `data.mask_subdir`: default `labeled/masks_coded` (old 20211104 labels); `labeled/masks_escdd` = revised E-SCDD labels (P6 onward). Train, val, test and class weights use the same mask set during training.
- `data.unlabeled_pool`: `split` (default; rest of train) or `external` (manifest `data/splits/external_unlabeled.txt`, images `data/unlabeled/images_512`, 11,938 cells). The code refuses external stems that clash with train/val/test. At f = 1.0 SSL is refused unless the pool is external (P16 patch, `d51b60f`).
- **Determinism** (`src/data/stream.py`): every training batch is a pure function of (seed, stream id, batch index). Epoch order comes from `randperm` seeded by (seed, stream, epoch); every sample carries its own augmentation seed, and each Albumentations transform gets its own seed (this fixed a bug where flips always fired together). One batch is drawn per stream per step. A resumed run therefore sees exactly the batches of an uninterrupted run, regardless of worker count. With `training.deterministic: true`, cuDNN runs deterministically. Protocols state that training is deterministic per machine and that co-locating runs on a GPU changes speed only (`protocols/P13_cutmix_separate_bn.md`).

### 2.4 Augmentation (`src/data/augmentations.py`)
| Pipeline | Ops | Used by |
|---|---|---|
| `get_strong_augmentation` (old default) | resize; h/v flips; 90 degree rotations; +/-5 degree rotation (border image 0, mask class 7 padding); Gaussian blur; brightness/contrast +/-0.2; Gaussian noise | old-era supervised runs |
| `get_labelsafe_augmentation` (`data.augmentation=labelsafe`, P6) | resize; h/v flips; 90 degree rotations; brightness/contrast +/-0.2 (p 0.4). No small rotation, no blur, no noise | P-series supervised arms; also SSL labelled images under `ssl.labeled_aug=supervised` |
| `get_labelsafe_geometric` + `get_labelsafe_strong_photometric` (P7) | shared geometry (flips, 90 degree rotations), then for the student: brightness/contrast +/-0.25 (p 0.8), Gaussian noise (p 0.3) | SSL unlabelled images (student strong view) |
| `get_weak_photometric` / `get_weak_augmentation` | normalise only (resize for eval) | teacher view; val/test/re-scoring |

"Label-safe" means geometry is restricted to exact pixel permutations, so a 1-2 px crack label is never resampled or shifted against its crack, and blur (which erases thin cracks) is dropped. The SSL two-view dataset (`TwoViewDataset`) applies the geometry once, then two photometric stages, so the student and teacher views are pixel-aligned.

### 2.5 Models (`src/models/model_factory.py`)
| `model.name` | Model | Notes |
|---|---|---|
| `unetpp` | From-scratch U-Net++ (`SAUNetPlusPlus`), 4.98M params; `sa_gating: true` adds the old SA gate (5.44M) | old era (README) |
| `smp_unetpp` | `segmentation_models_pytorch.UnetPlusPlus`, ResNet34 encoder, ImageNet weights; first conv adapted to 1 channel by summing RGB filters | **P6 arm L2/L3 onward: the "L3 base" of every P-series run** |
| `smp_unet` | smp U-Net, VGG16 ImageNet encoder | Pratt et al. replication (`configs/pratt_unet.yaml`) |
| `deeplabv3plus` | DeepLabV3+ wrapper (ResNet50 default) | UCF-EL recipe; P15 pretraining used DeepLabV3+ with ResNet34 (`p15_ucf_pre_dlv3p_r34`) |

`model.encoder_init=<path>` (P15, `be67787`, `load_encoder_init` in `el_p14/scripts/train.py`) copies `encoder.*` weights from another run's `latest.pth`; 3-channel first conv weights are summed to 1 channel; strict matching.

### 2.6 Losses (`src/losses/`, built in `loss_factory.py`)
**Supervised (`loss.supervised`)**
- `weighted_ce` (old default): CE with class weights from the labelled subset, sqrt-inverse-frequency, capped at 10x the median, classes absent get weight 0.
- `ce` : plain CE.
- `ce_dice` (P6 L3 onward): plain CE + batch soft Dice on crack and inactive, `CE + 1.0 * mean(1 - Dice_c)` (`ce_dice.py`).
- `tol_dice` (P14, `el_p14` only): `ce_dice` with the CE replaced by the tolerant rule applied to the human labels (`TolerantCEDiceLoss` in `el_p14/src/losses/tolerant_pl.py`); radius 0 equals `ce_dice` (tested).

**Unlabelled / consistency (`loss.consistency`)**
- `semi_ce` (old default): the SemiCE loss of the old Mean Teacher runs. P2 showed it is not a valid consistency loss; every result using it is invalid (09/06 docs).
- `confidence_ce` (`confidence_ce.py`): FixMatch-style hard pseudo-labels: CE to the teacher's argmax where teacher max-probability >= `loss.t_pos` (P-series uses 0.95), nothing elsewhere; sum divided by all unlabelled pixels. Used by P13's BsM5 arm ("B" arms = hard PL).
- `tolerant_pl` (`tolerant_pl.py`, `TolerantPLLoss`, P7): the project's proposed loss ("C" arms). Per unlabelled pixel, from the teacher's softmax on the weak view:
  - teacher argmax is a rare class r (crack 14 or inactive 11), confident or not: tolerant term `-p_t[r] * log(maxpool_{(2R+1)x(2R+1)}(p_s[r]))`. The student is credited for predicting r anywhere within R px; the term is weighted by the teacher's probability, so unsure targets count less;
  - confident (>= `t_pos`, 0.95) head-class pixel outside an R-px band around rare targets: plain CE to the teacher's argmax;
  - everything else (unconfident head pixels, and the band): no loss. The band is a "don't care" zone so a student crack 1-2 px off is not punished;
  - normalised by the number of unlabelled pixels. R = `loss.tolerance_radius` (2 in all P-series runs). It logs `conf_frac` (share of confident head pixels used) and `rare_frac` (share of pixels with a rare target), which appear in `experiments/<run>.stdout` every 50 steps.
- `class_threshold_ce`, `none`: other options (old UCF PV-S3 work; loss off).

A "D" arm (loss-off control) uses `tolerant_pl` with `ssl.lambda_final=0`, so the loss is never applied.

### 2.7 The Mean Teacher step (`src/trainers/trainer.py`)
- **Same budget for every method:** `training.total_steps` optimizer steps; each step draws one labelled batch (and, in SSL, one unlabelled batch). This is the "step matching" rule built into the trainer.
- **Teacher and EMA** (`ema.py`): the teacher starts as a copy of the student; after every optimizer step its weights and float buffers (BatchNorm statistics) become `0.999 * teacher + 0.001 * student`. The teacher runs in eval mode with no gradient. **Validation, test and all re-scoring use the teacher** for Mean Teacher runs.
- **lambda schedule** (`consistency_weight`): 0 for `ssl.warmup_steps` (2,000 in the P-series), then a linear ramp over `ssl.ramp_steps` (2,000) to `ssl.lambda_final` (1.0 in the P-series; old default 1.5). Total loss = supervised + lambda * consistency.
- **Joint forward (default, P8-P12):** labelled and unlabelled images go through the student in one batch, so BatchNorm normalises them together and the running statistics mix both. P12 measured this as a handicap ("joint-BN").
- **`ssl.labeled_view`** (`strong` in `ssl_mean_teacher.yaml`): which two-view image the labelled loss sees, in the default two-view pipeline.
- **`ssl.labeled_aug=supervised`** (P11, `24590fb`): the labelled images instead get exactly the supervised arm's label-safe pipeline (`SupervisedViewDataset` in `scripts/train.py`). Then a loss-off SSL run differs from supervised only in batch composition and data streams.
- **`ssl.student_forward=separate`** (P13, `bac5264`, `_ssl_losses_split`): two student forwards per step. The labelled forward updates BatchNorm as in a supervised run; the unlabelled forward runs inside `frozen_bn_stats` (`ssl_ops.py`), which uses batch statistics for that pass but restores every running mean/var afterwards. At lambda = 0 the unlabelled pass is skipped entirely, so the student is bit-identical to the supervised run (verified on GPU for 100 steps, `results/p13_audit/smoke_gpu.log`). This is why, from P13 on, the supervised arm is also the exact loss-off control.
- **`ssl.decouple_decoder=true`** (P17, `f2f20d3`; needs `student_forward=separate`): SKCDF-style decoupling. At step 0 the trainer deep-copies the model's decoder and segmentation head into `dec_u` (`decoder_u`, `head_u`). The student's unlabelled forward (strong view, CutMix, inside `frozen_bn_stats`) goes encoder → `decoder_u` → `head_u`, so the unlabelled loss reaches the encoder and `decoder_u` only. `decoder_u` has its own optimizer, scheduler and gradient clip (same settings). After every step `decoder_u ← ω · decoder_u + (1 − ω) · decoder` on parameters (not BN buffers), ω = `ssl.decouple_ema` (0.99). Pseudo-labels still come from the EMA teacher (encoder + labelled decoder), and the teacher is what is evaluated. `decoder_u` is checkpointed (`models.decoder_u`) and scored as `test_final_secondary` in `metrics.json` (student encoder + `decoder_u`). Default off: the P13 step is unchanged. At λ = 0 the decoupled run equals the supervised run bit for bit (tested), and P17's logs matched BsM5 to step 2,000.
- **`ssl.cutmix_p`** (P13): per unlabelled image, with probability p, one box (area 2-40% of the image, aspect 0.3 to 3.33, as UniMatch) is pasted from the next image in the batch into the student's strong view, and the same box is applied to the teacher's logits, so pseudo-labels stay on the pixels they were predicted for. Boxes are a pure function of (seed, step) (`mix_seed(seed, 2, step)`).
- **Logged per 50 steps** (`log_every`): `loss`, `loss_sup`, `loss_con`, `lambda`, `conf_frac`, `rare_frac`, `lr`, `steps_per_sec`.
- **Checkpoints:** `checkpoints/latest.pth` (full training state: student `models.model`, teacher `models.teacher`, optimizer, scheduler, RNG, history; every 2,000 steps and at the end) and `checkpoints/best.pth` (best-val weights). `--resume` continues bitwise. **The P-series uses `latest.pth` at step 20,000 (final weights) for every reported number**; best-val selection is not used because it flips signs on 54 val cells.
- `metrics.json` from training contains val/test at the best-val step and the final step, scored on the training mask set. The **reported** numbers come from the separate re-score (next section), not from `metrics.json`.

### 2.8 Evaluation and re-scoring
- **`scripts/rescore_label_versions.py`** (gaint repo; local copy `scripts_gaint/`): read-only. For each run and split (test, val) it loads `latest.pth` (teacher for Mean Teacher), predicts with the weak view under bf16, and scores the **same predictions** against both label versions: `old_20211104` (`data/labeled/masks_coded`) and `new_escdd` (`data/escdd_masks/<split>/`). Per class (crack, inactive): dataset-level (pooled over all cells) `iou`, `precision`, `recall`; `ap` (binned pixel AP, 1,000 bins); `gt_px`; relaxed scores at 1 and 2 px: `rel_p{r}` (share of predicted crack px within r px of GT crack), `rel_r{r}` (share of GT px within r px of a prediction), `rel_f1_{r}`. Prediction = argmax. Every launch script runs it automatically after training ("rescored <run> rc=" line).
- **`per_image_scores.py`** (local copy `scripts_gaint/`; deployed into cv02 code dirs' `scripts/`, not in the gaint main repo): same inference, writes per cell `[crack tp, fp, fn, inactive tp, fp, fn]`. Summing over cells reproduces the re-score IoU exactly (every analysis prints this sanity check).
- **`score_histograms.py`** (same locations): per-bin positive/negative pixel counts of crack/inactive scores, used for pooled AP and the "bin-0 share" (share of GT pixels scored < 0.001).
- **`src/evaluation/metrics.py`**: the in-training metrics (`defect_miou` = mean IoU of crack and inactive; `crack_recall_relaxed` with a 2 px disk). Conventions `standard`, `pvs3`, `pratt_median` exist because papers define metrics differently (see 05_literature_and_baselines.md).
- **E1 per-cell scorer** (`/tmp/noob_el/diag/e1_task_metrics_v2.py` = local `scripts_cv02/e1_task_metrics.py`): argmax, final weights, teacher for MT, on the 50 test cells (revised masks) and the 106-cell `ext117` set. Per cell it stores crack counts, relaxed P/R, skeleton lengths, inactive areas. Definitions: `results/e1/README.md`.

---

## 3. Running experiments: queues, logs, rules of the machines

### 3.1 How a cv02 experiment is launched
1. A protocol is committed in `~/mtp/research/protocols/` before any run.
2. The code commit is deployed to a fresh cv02 dir (`git archive` from gaint, recorded in `REVISION`; `el_p16` used a tar export and has no `REVISION`). `data` is symlinked to `el_p7/data`.
3. A **spec file** lists one run per line: `<run name> <gpu or -> <config yaml> <opts...>` (copies in `scripts_cv02/*.spec`).
4. **`gpu_queue_pNN.sh <session> <spec> <per-gpu> <gpu list>`** (e.g. `/tmp/noob_el/el_p16/gpu_queue_p16.sh`): loops over the listed GPUs; a GPU takes runs only when its used memory is < 1,000 MiB (so never a GPU another user has taken); it then gets `<per-gpu>` runs (3 in the P-series) at once; it polls every 60 s and prints "queue empty" when all are launched. It writes per-GPU `reports/<session>/queue_g<g>.spec`; its status lines go to stdout, which the callers redirected to `reports/<session>/queue.log` for P10 to P14 and P16 Part A. P16 Part B has no `queue.log`: the queue ran inside `p16b_auto.sh`, so its output is in `el_p16/reports/p16b_auto.log`.
5. **`launch_set_pNN.sh <session> <spec>`**: one tmux window per run in session `<session>`. Each window: `source /tmp/noob_el/env.sh`, set `CUDA_VISIBLE_DEVICES` and `OMP_NUM_THREADS=4`, run `scripts/train.py --overwrite ... run_name=<name>` (stdout to `experiments/<name>.stdout`), then `rescore_label_versions.py --runs <name> --out reports/<session>/<name>.json`. It appends to `reports/<session>/launch.log`:
   - `[date] start <name> gpu <g>`
   - `[date] trained <name> rc=<exit code>`
   - `[date] rescored <name> rc=<exit code>`
   A run whose `experiments/<name>` exists is skipped, never overwritten. "rc=0" on both lines means the run is complete.

   **Launcher rc bug (found 21 Oct 2026 by the SK1 trainer, confirmed by the SKCDF critic; additive note).** In `launch_set.sh`, `launch_set_p11.sh`, `launch_set_p17.sh`, `launch_gaint_p10.sh` and `launch_gaint_p13.sh` the line `echo "[$(date)] trained <name> rc=$?"` expands `$?` after the `$(date)` command substitution, so it records date's exit code: **the logged rc is always 0**, whatever training or re-scoring returned (`bash -c 'false; echo "[$(date)] rc=$?"'` prints rc=0). So "rc = 0" statements for runs launched with these scripts are not evidence of completion. Use instead: the log reaches `step N/N` and prints `TEST (final weights, step N)`; `checkpoints/latest.pth` step = N; `metrics.json` `test_final.step` = N; the re-score JSON's `step` = N. Checked on 21 Oct for all P13 (15), P17 (5) and P18 (8) runs, on both the gaint `cv02_noob_el` copies and the cv02 originals: all complete (`results/rc_check/p13_p17_p18_completion.txt`, script `results/rc_check/runcheck.py`). Other experiments launched with these scripts have not been re-checked this way. `launch_set_sk1.sh` (SK1) captures rc first and re-scores only on rc = 0.

   **[Note 30 Oct: the bug recurred on 29 to 30 Oct, despite this note (commit 16128f7).** New gaint and cv02 scripts wrote five status lines with `rc=$?` after `$(date)`: MIM pretrain ("pretrain rc"), MIM5 post, DDeP5 post, cv02 DDeP ("ddep rc") and the f100 smoke status lines. The training-run lines of `run_one.sh` (all versions) and `f2_postC` captured rc first and were correct. Each affected run was confirmed complete otherwise: DONE lines (36500/36500, 40000/40000), POST DONE with md5 manifests, `md5sum -c` on the encoder and decoder files, step-20000 lines and 0 Tracebacks in all 15 MIM5/A5c-f1/DDeP5 runs. No verdict is affected. The smoke lines and the staged f100 queue were fixed (rc captured before `date`, md5 60499c90). Sources: `team_2026-10-29_features/log.md` 30 Oct 11:16 and 11:21; `SESSION_RECORD_2026-10-28_to_30.md` §9; doc 13 D20.]
6. Queues that must follow each other are chained (wait for the previous "queue empty", then about 5 minutes), never run concurrently: two queues polling "GPU free" raced on 10 Oct (memory note).
7. **P16 Part B auto-launcher** (`scripts_cv02/p16b_auto.sh`, running in cv02 tmux `p16auto`): waited until P13's CsM5 s0-4 and Cs5 s0-2 were re-scored with rc = 0 and P16 Part A's queue was empty, wrote `reports/p16b/selection.txt` from P13 **val** numbers only (CutMix on if the mean of the three val primaries was higher for CsM5 than Cs5; it chose `CUTMIX=0`), generated `reports/p16b/p16B_queue.spec`, then ran `gpu_queue_p16.sh p16b ... 3 0 5 1 2 3 4 6 7`. All 15 runs launched at 21:05 IST on 11 Oct (launch.log, in UTC: 15:34:54 to 15:35:38); only GPUs 0, 3, 4, 5 and 6 received runs.

**gaint** uses sequential "lanes" instead (`lane.sh` in the report dir, e.g. `el_p14/reports/p15/lane.sh`; template in `scripts_cv02/launch_gaint_p13.sh`): each lane waits for a trigger line in an earlier log, waits for < 20,000 MiB used on GPU 0, trains and re-scores runs one after another, logging to `reports/<exp>/launch_gaint.log`. gaint never runs more than two jobs at once.

### 3.2 Machine rules (standing; memory note `server-runs-tmux-parallel.md`)
- Long runs go in tmux, one window per run. Use `tmux has-session -t "=name"` (exact match): plain `-t name` prefix-matches (it found `p13smoke` once and nothing launched). The current launch scripts use plain `-t $S`, which is safe only while session names are unique prefixes.
- On cv02, never start on a GPU where another user holds > 4 GB. The queue's < 1,000 MiB rule is stricter.
- All arms and seeds of one experiment run on one hardware type; numbers from gaint and cv02 are never compared inside a rule.
- Same commit and byte-identical data/splits across machines (md5 check required by the memory note; no written md5 record was found in `~/mtp/research`, so check with `md5sum` if needed).
- Code changes go in a new worktree on gaint (`git worktree add ../el_pNN -b pNN`), never in the tree a running lane launches from.
- Do not kill queues or processes without the user's say-so. Fill idle machines overnight with the next locked experiment.

### 3.3 Throughput (observed, for planning)
| What | Where | Time |
|---|---|---|
| SSL run, 20,000 steps, 3 per GPU | cv02 A6000 | about 6-7.5 h (P13: 13:30 to 21:04 IST for the last runs; BsM5 logged ~0.93 steps/s) |
| SSL run, 20,000 steps, 1 per GPU | cv02 A6000 | about 2 h 10 min (P17 and BsM5 s3-4, 13 Oct: ~4.2 steps/s at λ = 0, ~3.6 after; separate BN + CutMix, about 10 GB per run) |
| Supervised run, 20,000 steps, 3 per GPU | cv02 | about 3-3.5 h (P14 L3o: 14:42 to 18:14 IST) |
| Supervised run (P15 arms) | gaint, one GPU, two lanes | about 1 h 40 min each (`el_p14/reports/p15/launch_gaint.log`) |
| Re-score of one run | either | seconds |
| E1 scoring | cv02 | about 4-6 s per run (`diag/e1p13.log`) |

Added 30 Oct (sources: `team_2026-10-24_go/trackM/results_r3.md`, `results_r5.md`; `team_2026-10-29_features/protocol_100.md`, `log.md`):

| What | Where | Time |
|---|---|---|
| Supervised R34 run, 100% (Track M) | cv02 | about 1.1 GPU-h per run; ResNet-50 (R3) about 2 GPU-h; 2× resolution (R5) about 4.2 GPU-h |
| Fine-tune, 3 at once (5%; same step cost at 100%) | gaint | 2.25 steps/s each, about 2.5 h per 20k-step run |
| CP run, 2 at once | gaint | about 2.2 steps/s each, about 2.5 h |
| MIM pretraining alone, batch 32 | gaint | 71 samples/s; 36,500 steps 13:08 to 18:34 IST |
| DDeP pretraining alone | cv02 A6000 | 245 samples/s; 40,000 steps, done 22:42 IST |
| protocol_100, 20 runs | gaint | about 19 h (fine-tune waves about 12.3 h, then CP about 6.8 h) |

Memory per run: about 5.7 GB (supervised) and 6.2 GB (SSL) on cv02 (`nvidia-smi --query-compute-apps`, 11 Oct, earlier runs). The P16 Part B SSL runs (separate-BN forward) use about 9.7 GB each, about 29 GB per GPU at 3 per GPU (`nvidia-smi --query-compute-apps`, ~22:30 IST 11 Oct).

---

## 4. Research-side scripts (`~/mtp/research`)

| Script | What it does |
|---|---|
| `scripts/ssl_rules.py` | The locked rule-1 arithmetic for any contrast. Loads re-score JSONs from `--dirs` (arm key `pN:<arm>`, seeds parsed from `_s<k>`), optional `--merge NEW=ARM1+ARM2` (pool disjoint seeds, e.g. A5c = P12 s0-2 + P13 s3-4). Prints a table (test crack IoU, inactive IoU, crack relF1@2, crack relP@2, AP, val IoU; mean +/- sd), then for each `--pairs A=B`: delta, threshold `max(0.01, 2*sqrt((sd_A^2 + sd_B^2)/3))`, BETTER / WORSE / n.d. per primary, the rule-1 verdict, the width check (crack relP@2 drop > 0.05) and "gap closed" against `--ref`. Uses `new_escdd` (revised labels), test split. |
| `scripts/per_image_analysis.py` | Robustness over test cells from per-image JSONs: Delta IoU with all cells, Delta without the top-3 cells (by GT area of that class), 95% paired image-bootstrap CI (2,000 resamples), P(Delta > 0). `--keep <regex>` restricts to a source group (e.g. `^(CSIR|ARTS)_`); `--merge` as above; `--check <raw dir>` verifies summed per-image IoU equals the re-score IoU. |
| `scripts/ssl_figure.py` | Bar figure (mean +/- sd with seed dots) for chosen arms; with `--hist` prints the bin-0 share. |
| `scripts/post_ssl.sh pN <cv02 gpu> <expected runs>` | One-command post-processing for P9-P14 and P17 (the p17 branch also pulls BsM5 s3-4 from `el_p13/reports/p13a2`, scores them per image into `results/p13/per_image_a2.json`, writes `results/p17/decoder_u_secondary.txt`, and adds a without-`CSIR_00070_r8_c4` source split): pull re-score JSONs and `launch.log` from cv02 (`CODE` dir per experiment), run per-image and histogram scoring on cv02, apply `ssl_rules.py` with the experiment's arms/pairs, bootstrap (all cells and both source groups), figure. Writes `results/pN/{raw/, pN_rules.txt, per_image.json, per_image_test.txt, hist_revised.npz, fig_pN_bars.png}`. |
| `scripts/post_p78.sh p7|p8 <gpu>` | Same for P7/P8 using `p78_rules.py` and `p78_figure.py`. |
| `scripts/post_p15.sh <cv02 gpu>` | P15: pull gaint JSONs (`el_p14/reports/p15`) and P12's gaint JSONs, apply rules, copy slim checkpoints (config + `latest.pth`) of the gaint runs to cv02 `diag/g_import` via the scratchpad, run E1 on cv02, aggregate to `results/e1/e1_p15.md`. |
| `scripts/post_p16.sh <cv02 gpu>` | P16: pull Part A (`el_p13/reports/p16`) and Part B (`el_p16/reports/p16b`) JSONs plus `selection.txt`, per-image and histogram scoring for both code dirs, rules with A20 = P6 L3 20% s0-2 + P16 A20 s3-4 and A100 = P6 L3 100% s0-2 + P16 A100 s3-4, bootstrap, bars, `p16_curve.py`, E1, aggregate to `results/e1/e1_p16.md`. Committed `f9f2783`; ran 12 Oct ~04:30 IST on cv02 GPU 0 (rc = 0). |
| `scripts/p16_curve.py` | Supervised vs SSL against label fraction (cv02 only); 5% point = P13 Cs5 or CsM5 depending on `selection.txt`. |
| `scripts/p16_excell.py` | Post hoc (12 Oct): P16's rule arithmetic and curve with one test cell (default `CSIR_00070_r8_c4`) removed, from E1 per-cell counts; checks the all-cell values against the re-score JSONs first. Writes `results/p16/sensitivity_excell.txt` and `fig_p16_curve_excell.png`. |
| `scripts/p17_excell.py` | Post hoc (13 Oct, as `p16_excell.py`): rule-1 arithmetic for the P17 and P13 5% contrasts (A5c, BsM5, BsD5, CsM5; 5 seeds each) with and without one test cell, from E1 per-cell counts; checks the all-cell values against the re-score JSONs first. Writes `results/p17/sensitivity_excell.txt`. |
| `scripts/p19_compare.py` | P19: our Hanifi 2025 runs vs the paper's Table 2, Table 3 and Fig. 3 (transcribed, checked against Table 3); per-class table and `results/p19/fig_p19_classiou.png`. |
| `scripts/p18_curve.py` | P18 (exploratory): rule-1 arithmetic for BsM20 − A20, BsM10 − A10, BsM20 − S20 (and BsM5 − A5c, S20 − A20) with and without the noisy cell, from E1 counts; label-fraction curve with supervised, the tolerant recipe and the BsM recipe (`results/p18/fig_p18_curve.png`). Called by `post_ssl.sh p18`. |
| `scripts/qualitative_panel.py` | Qualitative figure from a `pred_dump.py` npz (`results/qualitative/fig_qualitative_5pct.png`). |
| `scripts_cv02/rescore_weights.py` | The re-scorer with `--key model|teacher|auto` and `--root`; used for the EMA check (`results/ema_check/`). Runs from cv02 `diag/student/`. |
| `scripts_cv02/pred_dump.py` | Read-only argmax predictions of given runs on given test cells, with image and revised mask, to an npz. Run from a cv02 code root. |
| `scripts_cv02/pratt_scores.py` | Read-only per-image TP/FP/FN for crack, gridline and inactive on old and revised labels (`results/pratt_compare/`). |
| `scripts/diag_csir70.py` | Post hoc (12 Oct): loads `experiments/<run>/checkpoints/latest.pth` (teacher for Mean Teacher runs) and predicts one test cell in bf16 and fp32; prints crack predicted/FP pixels and p(crack) quantiles and saves a p(crack) PNG. Run on cv02 from the code worktree root (`el_p13` for A runs, `el_p16` for S runs). Output: `results/p16/diag_csir70.txt` and `diag_csir70/`. |
| `scripts/cell_noise_rank.py` | Ranks the 582 labelled cells by robust pixel-noise sigma (1.4826 × median absolute residual from a 5×5 median filter). Output `results/p16/cell_noise_rank.txt`. |
| `scripts/p6_rules.py`, `p6_figures.py`, `p6_hist_analysis.py` | P6 rules, figures, histogram/saturation analysis. |
| `scripts/p78_rules.py`, `p78_figure.py` | P7/P8 rules and figure. |
| `scripts/aggregate_runs.py` | Per-arm tables and a ladder figure from re-score JSONs (used for P6/P7). |
| `scripts/midterm_figures.py` | P5 offset figure and the tolerant-routing schematic. |
| `scripts_cv02/e1_task_metrics.py` | E1 per-cell scorer (run on cv02 as `diag/e1_task_metrics_v2.py`). |
| `scripts_cv02/e1_aggregate.py` | E1 tables: per-arm means with bootstrap half-widths, paired contrasts with CIs, leave-top-3-out; `--merge`, `--sets test ext`. |
| `scripts_cv02/gpu_queue*.sh`, `launch_set*.sh`, `launch_gaint_p1{0,2,3}.sh`, `*.spec`, `p16b_auto.sh` | Copies of the launch machinery and the exact run lists. |
| `scripts_gaint/*` | Copies of gaint probe scripts (P1 `overfit_check.py`, P2 `probe_semice_gradient.py`, P4 `p4_feature_probe.py`, P5 `p5_region_pl_precision.py`) and the scoring scripts. |

To reproduce a results folder: run its post-processing command (table in section 5) from `~/mtp/research`. The scripts need the run checkpoints on the servers for the per-image, histogram and E1 steps; the rules step needs only the JSONs in `results/pN/raw/`.

---

## 5. Experiment to code, machine and folders

| Exp | Code (commit / branch) | Machine | Run dir / deployment | Reports dir (server) | Local results | Post-processing |
|---|---|---|---|---|---|---|
| P1 overfit check | `28686c0`, `4474d04` (main) | gaint | `el-fault-detection` | `reports/overfit_check` | `results/p1` | `scripts/overfit_check.py --arm A..E` (copy `scripts_gaint/`) |
| P2 SemiCE probe | `28686c0` (main) | gaint | `el-fault-detection`, checkpoint `experiments/mt_20pct_s0` | `reports/probes/` | `results/p2` | `scripts/probe_semice_gradient.py --run experiments/mt_20pct_s0 --batches 40` |
| P3 label versions | `rescore_label_versions.py` (added with `824fab0`) | gaint | existing old-era runs | `reports/probes/rescore_label_versions.json` | `results/p3_label_versions` | `compare.py` in that folder |
| P4 feature probe | `p4_feature_probe.py` | gaint | `el-fault-detection` | n/a | `results/p4_feature_probe` | script itself |
| P5 region PL precision | `p5_region_pl_precision.py` | gaint | on `alhvr_20pct_s0/s1` | n/a | `results/p5_region_pl` | script itself; `scripts/midterm_figures.py` |
| P6 corrected baseline | `824fab0` | cv02 | `/tmp/noob_el/el_p6` | `el_p6/reports/p6` | `results/p6` | `p6_rules.py`, `p6_figures.py`, `p6_hist_analysis.py` |
| P7 tolerant PL pilot | `0367079` | cv02 | `el_p7` | `el_p7/reports/p7` | `results/p7` | `bash scripts/post_p78.sh p7 <gpu>` |
| P8 tolerant PL on L3 | `0367079` | cv02 | `el_p7` | `el_p7/reports/p8` | `results/p8` | `bash scripts/post_p78.sh p8 <gpu>` |
| P9 external pool | `0367079` | cv02 | `el_p7` | `el_p7/reports/p9` | `results/p9` | `bash scripts/post_ssl.sh p9 <gpu> 9` |
| P10 SSL at 5% | `0367079` | cv02 (SSL arms); gaint (A5, A50 references) | `el_p7`; gaint `el-fault-detection` | `el_p7/reports/p10`; gaint `reports/p10` | `results/p10` | `bash scripts/post_ssl.sh p10 <gpu> 15` |
| P11 matched pipeline, 10% | `24590fb` | cv02 | `el_p11` | `el_p11/reports/p11` | `results/p11` | `bash scripts/post_ssl.sh p11 <gpu> 12` |
| P12 matched, 5% | `24590fb` | cv02; gaint replication (gDm5, gCm5 s3-5; gA10 s0-2) | `el_p11`; gaint `el-fault-detection` | `el_p11/reports/p12`; gaint `reports/p12` | `results/p12` | `bash scripts/post_ssl.sh p12 <gpu> 15` |
| P13 separate BN + CutMix | `bac5264` (p13) | cv02 (gaint arms dropped by Amendment 1) | `el_p13` | `el_p13/reports/p13` | `results/p13` | `bash scripts/post_ssl.sh p13 <gpu> 13` |
| P14 tolerant supervision | `be67787` (p14) | cv02 | `el_p14` | `el_p14/reports/p14` | `results/p14` | `bash scripts/post_ssl.sh p14 <gpu> 9` |
| P15 UCF-EL encoder | pretrain `bac5264` on cv02 (`el_p13/experiments/p15_ucf_pre_dlv3p_r34`); arms `be67787` on gaint | cv02 + gaint | gaint worktree `el_p14`, tmux `p15g` | gaint `el_p14/reports/p15` | `results/p15` (only `dedup.py` until the post-processing runs) | `bash scripts/post_p15.sh <cv02 gpu>` |
| P13 Amendment 2 (BsM5 s3-4) | `bac5264` (p13) | cv02 | `el_p13` (tmux `p13a2`) | `el_p13/reports/p13a2` | `results/p13/raw/` (`launch_a2.log`), `results/p13/per_image_a2.json` | via `bash scripts/post_ssl.sh p17 <gpu> 5` |
| P17 decoupled decoder | `f2f20d3` (p17) | cv02 | `el_p17` (tmux `p17run`) | `el_p17/reports/p17` (= `p17run`) | `results/p17` | `bash scripts/post_ssl.sh p17 <gpu> 5`, then `.venv/bin/python scripts/p17_excell.py`; E1 via `diag/e1_task_metrics_v2.py --code /tmp/noob_el/el_p17`, aggregate `results/e1/e1_p17.md` |
| P19 Hanifi 2025 reproduction | their repo `506aa0b` (TF 2.18 / Keras 3.8) | cv02 | `/tmp/noob_el/hanifi` (venv via `uv`, Python 3.10; tmux `p19`; `env_p19.sh` sets `KERAS_HOME`, wandb off) | `/tmp/noob_el/hanifi/runs` | `results/p19` | `scripts_cv02/hanifi_run.py` via `scripts_cv02/p19_launch.sh`; `.venv/bin/python scripts/p19_compare.py --out results/p19/fig_p19_classiou.png` |
| P18 BsM at 10/20% (exploratory) | `bac5264` | cv02 | `el_p13` (tmux `p18`, spec `reports/p18_queue.spec`) | `el_p13/reports/p18` | `results/p18` | `bash scripts/post_ssl.sh p18 <gpu> 8` (also runs E1 and `scripts/p18_curve.py`) |
| P16 label-fraction curve | Part A `bac5264`; Part B `d51b60f` (p16) | cv02 | Part A `el_p13` (tmux `p16`); Part B `el_p16` (tmux `p16b`, launcher `p16auto`) | `el_p13/reports/p16`; `el_p16/reports/p16b` | `results/p16` | `bash scripts/post_p16.sh <cv02 gpu>` |
| E1 per-cell metrics | `diag/e1_task_metrics_v2.py` (`--code <deployment>`) | cv02 | `/tmp/noob_el/diag`, set `ext117` | `diag/e1v2/<run>.json` | `results/e1` (`raw/`, `raw_v2/`, `e1_pNN.md`) | `scripts_cv02/e1_aggregate.py results/e1/raw_v2 --sets test ext --arms ... --pairs ...` (exact calls in the post scripts and in `results/e1/README.md`) |

Run names follow `p<NN>_<arm>_<frac>pct_s<seed>` (e.g. `p13_CsM_5pct_s3`); gaint runs in P12/P15 carry a `g` prefix in the arm (`p12_gCm_5pct_s3`, `p15_gU_5pct_s0`). Arm letters are explained in 04_glossary_and_naming.md.

### 5b. Experiments of 24 to 30 Oct (added 30 Oct)

| Exp | Code | Machine | Team folder (protocols, results, verification) | Local raw outputs |
|---|---|---|---|---|
| Track D probe, edge, labelled set | see `trackD/d1chk/` | cv02 | `team_2026-10-24_go/trackD/` | `results/trackD_probe/`, `trackD_edge/`, `trackD_labelset/` |
| Track M M0, R1 | existing SUP100 checkpoints; scripts `trackM/scripts/m0_audit.py`, `m1_r1.py` (FINAL: `m9_final.py`) | cv02 | `team_2026-10-24_go/trackM/` | `trackM/m0/`, `m0b/`, `r1/` |
| Track M R2, R2c, R3 | `el_mt` `3c1b72b` | cv02 | `trackM/` | `trackM/r2/`, `r2c/`, `r3b/`, `pilots/` |
| Track M R4 | `el_mt4` `0642889` | cv02 | `trackM/` | `trackM/r4/` |
| Track M R5, FINAL | `el_mt5` `1be64e1` | cv02 | `trackM/` | `trackM/r5/`, `final/` |
| MIM pretraining, A5c-f1, MIM5, AM | `el_f1` `603e0d5` | gaint | `team_2026-10-29_features/` (`protocol_mim5.md`, `protocol_am.md`, `verify_mim5.md`) | `team_2026-10-29_features/results/mim5/` |
| DDeP pretraining | `el_f2` `2751aa8` | cv02 | `protocol_ddep5.md` | backup gaint `cv02_noob_el/el_f2/` |
| DDeP5, CP5 | `el_f2` `2751aa8` | gaint | `protocol_ddep5.md`, `protocol_cp5.md`, `verify_ddep5.md` | `results/ddep5/`, `results/cp5/` |
| B1 label audit | `team_2026-10-29_features/scripts/b1/b1_audit.py`, `b1_report.py` (CPU) | gaint | `coach_strategy.md` appendix | `team_2026-10-29_features/b1_audit/` |
| protocol_100 | `el_f3` `e544133` | gaint | `protocol_100.md` (v1.1, md5 8dcb231b), `review_100_v1.md`, `coach_100.md` | (running since 12:05 IST 30 Oct; reports to `el_f3/reports/f100/`) |

Per-cell raw JSONs of MIM5, DDeP5 and CP5 (about 240 MB) are kept locally and on gaint with `MANIFEST.md5`, not in git (`SESSION_RECORD_2026-10-28_to_30.md` §11). Script paths in the 29 to 30 Oct team files (`scripts/...`) are relative to `team_2026-10-29_features/` (e.g. `scripts/f3/enc_cosine.py`, `scripts/f100_post_gaint.sh`, `scripts/coach_verify.py`); Track M's are in `team_2026-10-24_go/trackM/scripts/`; Track D's analysis scripts are in the repo's `scripts/trackD_*_analysis.py`.

### 5c. Experiments of 31 Oct to 1 Nov (added 1 Nov)

| Exp | Code | Machine | Team folder (protocols, results, verification) | Local raw outputs |
|---|---|---|---|---|
| PF2 | `el_f3` e544133 | gaint | `team_2026-10-31_next/protocol_PF2.md`, `build_pf2.md`, `verify_pf2.md` | `results/pf2/` |
| PF2E | `el_f3` e544133 (`pf2e_infer.py` 272463d3), CPU fp32 | gaint | `protocol_PF2E.md`, `build_pf2e.md`, `verify_pf2e.md` | `results/pf2e/` |
| THIN-B3 | `el_thin` c9bbb02 | gaint | `protocol_thin_b3.md`, `build_thin_b3.md`, `build_thin_runner.md` | `results/thin/` (after the opening) |
| HC | `el_hc` c2e6973 | gaint | `protocol_HC.md`, `build_hc.md`, `build_hc_runner.md`, `review_hc.md` | (queued) |
| A8 screen | `el_f8` c280e8c2 | gaint | `protocol_A8screen.md`, `ideas/idea08_runspec.md`, `build_a8_runner.md`, `review_f8_wrapper.md` | (queued) |
| B6 | e544133 + per-fold data roots | cv02 (planned) | `protocol_B6.md`, `judge/review_B6_v0.md` | `results/b6/` (folds, counts, cv02 polls) |
| Idea checks (1, 2, 7; routing pre-check) | `ideas/scripts/` (calib) | gaint CPU | `ideas/idea01`, `idea02`, `idea07`, `routing_precheck.md` | `ideas/calib_out/` |
| Idea checks (3, 4, 5, 11; SHV1; detector) | domain scripts on gaint `/home/noob/work/domain_scratch` | gaint CPU | `ideas/idea03`, `idea04`, `idea05`, `idea11` | `ideas/domain_out/` |
| T9, S10, P8 probe | `ideas/scripts/`, gaint `/home/noob/work/found/` | gaint CPU | `t9_prereg.md`, `s10_prereg.md`, `idea08_foundation.md` §4c-4d | `ideas/found_scripts/` |

Per-cell raw pulls (`results/*/raw`, `coach_raw`), the protocol_100 per-cell copies in `results/pf2/pooled10_m0`, `rules_in` copies, PF2E's B5 record JSONs and calib's per-cell records (`ideas/calib_out/rec*`) are kept locally and on gaint with `MANIFEST.md5`, not in git (`team_2026-10-31_next/.gitignore`).

---

## 6. How to find X (recipes for the guide agent)

All commands are read-only. Prefix with `ssh -o BatchMode=yes cv02@10.8.1.106 '...'` or `ssh -o BatchMode=yes noob@172.18.22.20 '...'`.

| I want | Where / command |
|---|---|
| The exact config a run used | `<deployment>/experiments/<run>/config_used.yaml` (e.g. cv02 `/tmp/noob_el/el_p13/experiments/p13_CsM_5pct_s0/config_used.yaml`) |
| The option string a run was launched with | the queue spec: local `scripts_cv02/pNN_queue.spec`, or server `reports/<session>/queue_g<g>.spec`; P16 Part B: cv02 `el_p16/reports/p16b/p16B_queue.spec` |
| The training log (loss, lambda, conf_frac, rare_frac per 50 steps) | `<deployment>/experiments/<run>.stdout` (also `experiments/<run>/train.log`). Example: `grep "step 20000/20000" .../p13_Cs_5pct_s0.stdout` |
| Did a run finish cleanly? | `grep <run> <deployment>/reports/<session>/launch.log`: need `trained ... rc=0` and `rescored ... rc=0` (not sufficient for runs from the P-series launchers: their rc is always logged as 0; see §3.1 note and check step 20,000 in the log, `latest.pth` and the re-score JSON) |
| The reported scores of a run | local `results/pN/raw/<run>.json` (copy of server `reports/<session>/<run>.json`) |
| How to read a re-score JSON | keys `test/<run>` and `val/<run>`; inside: `n` (cells), `weights` (`teacher` or `model`), `step` (20000), then `old_20211104` and `new_escdd`, each with `crack` and `inactive`, each with `iou, precision, recall, ap, gt_px, rel_f1_1, rel_p1, rel_r1, rel_f1_2, rel_p2, rel_r2`. The P-series headline numbers are `test/<run>` -> `new_escdd` -> class -> metric. Python: `json.load(open(f))["test/p13_CsM_5pct_s0"]["new_escdd"]["crack"]["iou"]` |
| Per-cell confusion counts | `results/pN/per_image.json`: `{"test/<run>": {"<cell stem>": [crack tp, fp, fn, inactive tp, fp, fn]}}` |
| Score histograms / bin-0 share | `results/pN/hist_revised.npz`, keys `test/<run>`, arrays (2 classes, pos/neg, 1000 bins); `ssl_figure.py --hist` prints the bin-0 share |
| E1 per-cell metrics of a run | `results/e1/raw_v2/<run>.json` (`cells` -> `test` / `ext` -> stem -> values); aggregated tables `results/e1/e1_pNN.md` |
| The locked rule verdicts | `results/pN/pN_rules.txt` and the "Locked rules" table in `results/pN/README.md` |
| Bootstrap and source split | `results/pN/per_image_test.txt` |
| A checkpoint | `<deployment>/experiments/<run>/checkpoints/latest.pth` on cv02, or the same path under gaint `/home/noob/work/cv02_noob_el/` (keys `models.model` = student, `models.teacher` = EMA teacher; P17 runs also `models.decoder_u`) |
| Which code produced a run | `cat <deployment>/REVISION` on cv02 (none for `el_p16`; see protocol), or the worktree commit on gaint (`git -C /home/noob/work/el_p14 log -1`) |
| What runs are going now | `tmux ls`; `tail <deployment>/reports/<session>/launch.log`; `nvidia-smi` (look, never attach or kill) |
| The P16 CutMix decision | cv02 `/tmp/noob_el/el_p16/reports/p16b/selection.txt` (P13 val seed means, `CUTMIX=0`) |
| Split membership | `data/splits/{train,val,test}.txt`, `data/splits/seed0/labeled_<P>pct.txt`, `unlabeled_<P>pct.txt`, `external_unlabeled.txt` (also local `~/mtp/datasets/splits_benchmark/`) |
| Old-era results | gaint `el-fault-detection/reports/results_consolidated.md`, `reports/summary.md`; context in 06_history_phase0_phase1.md |

## Known gaps in this map
- `el_p16` on cv02 has no `REVISION` file; its commit (`d51b60f`) is taken from the protocol and the deploy notes.
- No written md5 record of cross-machine data equality was found in the research repo.
- gaint's `REVISION` (`dfa4fd6`) is stale; use `git log`.
- `/tmp/noob_el` on cv02 is in `/tmp`. Since 13 Oct its run dirs and checkpoints are copied to gaint `cv02_noob_el` (MD5-checked), so one server can fail without losing them; there is still no copy off both servers.
- (Resolved 12 Oct) P15 and P16 results are local: `results/p15/`, `results/p16/`. The noisy-cell p(crack) maps were copied from cv02 `/tmp` to `results/p16/diag_csir70/` on 13 Oct.

## Related docs
00_START_HERE.md, 01_project_overview_and_scope.md, 02_domain_primer_EL_and_defects.md, 03_datasets_and_splits.md, 04_glossary_and_naming.md, 05_literature_and_baselines.md, 06_history_phase0_phase1.md, 07_methodology_rules_and_statistics.md, 08_experiments_P1_P7_diagnostics.md, 09_experiments_P8_P12_ssl_series.md, 10_experiments_P13_P16_E1.md, 11_results_synthesis_and_claims.md, 12_decisions_log.md, 13_problems_pitfalls_open_issues.md, 15_status_remaining_work.md, 16_faq_for_the_guide.md
