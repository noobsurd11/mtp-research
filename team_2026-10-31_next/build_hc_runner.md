# build_hc_runner: HC opening build (protocol_HC v1.1 §9.3), DRAFT for coach's review and FREEZE

runner's helper agent, 2026-11-01 20:16 IST. Tags: E measured (file / command), S judgement.
- Draft only: no job started anywhere. gaint use was read-only (ls, md5sum, wc -l, git log / diff, grep -n / sed -n on code and scripts). No training .stdout / train.log, no test or E1 mask, no m0 / per-cell JSON, nothing under reports/*/post/ was opened (paths and md5s only). el_thin not touched.
- Nothing arms until coach writes `FROZEN.md5` in gaint `/home/noob/work/nq/hc/` (hc_postwatch.sh refuses otherwise; protocol_HC §11 ruling 19:27).

## 1. Files (local `scripts/hc/`; runner copies the tree to gaint `/home/noob/work/nq/hc/`)
| File | md5 | What |
|---|---|---|
| `hc_postwatch.sh` | e968f7b46cb9880a61cb6ccc61cb4930 | trigger: arm checks, waits for 5 × `trained hc_HC_100pct_sK rc=0` + 5 × `config OK hc_HC_100pct_sK vs` in nq/launch.log, runs hc_post.sh |
| `hc_post.sh` | 088145323636dbf21968e297b60d7de3 | the ONE HC opening (passes 0-12, §3); end line in nq/post.log |
| `hc_e1_coprim.py` | 5a8fbe89631833a3adf1a41866c0153b | E1 co-primaries (relF1@2, inactive IoU), rule 1 vs SUPPF, strata reported; `--selftest` |
| `hc_shv1.sh` | ba4c6c51552b4b15d6fd74333af69d7b | CPU dumps val / rf / SHV1 for HC s5-9 + SUPPF s5-9, records, val self-check, SHV1 readout |
| `hc_shv1_read.py` | c502b23c6c36ae5b38379f1208cab9bf | SHV1 / SHV1-p readout and mechanism kill; `--selftest` on calib's pre-check records |
| `hc_f51.py` | c9b4bdec6c83db8d41a3af5c1ecf7574 | F51 harm guard via a8_screen_score's AP + bootstrap (imported, unmodified); `--selftest` |
| `hc_copies.md5` | 5bd0f3012df546c976047c7bdd773a54 | md5 list of the 10 third-party copies below (checked at arming and at the opening) |
| `post_extra/hc_b5.sh` | 9167911e171b1fbb2ee4064ff2aeaf98 | B5 + cell-level hook (thin_b5.sh 2dfaf915 with paths / protocol / arm changed) |
| `post_extra/hc_scuffign.sh` | cf516c628af103a99fb5e38068713109 | scuff-ignored test hook (pf2_scuffign.sh 2abfae02 with --code el_hc) |
| `calib_syn/calib_dump.py` | 9694ad7d9e8528e7fc4542acaaf5b5b3 | copy: calib's synval-capable dumper (**unfrozen superset**, §5) |
| `calib_syn/el_metrics.py` | f40a0efe0baa8f3ce419f0c55a70442e | copy: calib's synval-capable scorer (**unfrozen superset**, §5) |
| `found/a8_screen_score.py` | 8eba76e5bb0783e9d4ecc432dea4a785 | copy: found's AP / module bootstrap (= A8 screen scorer) |
| `trackM/m0_analyze.py` | d5adbe6bfb84ce251f56ec7494a69663 | copy: Track M agg (not on gaint; E: ls of /home/noob/work/*/m0_analyze.py to depth 4: none) |
| `thin/thin_e1_relf1.py` | 98bcb979cd49bc87e4b2f076961f4074 | copy: relf1() reference for the E1 self-test |
| `post_extra/pf2_scuffign.py` | e3615fdb17475c9b60307b3a278797b6 | copy: PF2's frozen scuff-ignored pass |
| `post_extra/calib/{calib_dump.py, el_metrics.py, pf2_b5_hook.sh, pf2_b5_pooled.sh}` | c172717e / 6e73ff11 / e06dfc5f / 873591ff | copies: calib's FROZEN B5 files (= PF2 / THIN) |

Proposed `FROZEN.md5` (coach writes it after review; hc_postwatch / hc_post require every line below, by path):
```
e968f7b46cb9880a61cb6ccc61cb4930  hc_postwatch.sh
088145323636dbf21968e297b60d7de3  hc_post.sh
5a8fbe89631833a3adf1a41866c0153b  hc_e1_coprim.py
ba4c6c51552b4b15d6fd74333af69d7b  hc_shv1.sh
c502b23c6c36ae5b38379f1208cab9bf  hc_shv1_read.py
c9b4bdec6c83db8d41a3af5c1ecf7574  hc_f51.py
5bd0f3012df546c976047c7bdd773a54  hc_copies.md5
9694ad7d9e8528e7fc4542acaaf5b5b3  calib_syn/calib_dump.py
f40a0efe0baa8f3ce419f0c55a70442e  calib_syn/el_metrics.py
8eba76e5bb0783e9d4ecc432dea4a785  found/a8_screen_score.py
d5adbe6bfb84ce251f56ec7494a69663  trackM/m0_analyze.py
98bcb979cd49bc87e4b2f076961f4074  thin/thin_e1_relf1.py
9167911e171b1fbb2ee4064ff2aeaf98  post_extra/hc_b5.sh
cf516c628af103a99fb5e38068713109  post_extra/hc_scuffign.sh
e3615fdb17475c9b60307b3a278797b6  post_extra/pf2_scuffign.py
c172717e5989edb8e0b7b312096f9180  post_extra/calib/calib_dump.py
6e73ff11aaa6171a52b5a5404877ab46  post_extra/calib/el_metrics.py
e06dfc5fd8946987f38a0cb82056649b  post_extra/calib/pf2_b5_hook.sh
873591ff9f28371e21e37e6878af274c  post_extra/calib/pf2_b5_pooled.sh
```

## 2. External paths, md5 as found on gaint (E, 1 Nov 19:55-20:10)
| Path | md5 | Use |
|---|---|---|
| `/home/noob/work/el_hc` HEAD | c2e697324d391e05a3fbdb6c3ba2f607c5152e5d | deploy; `git diff --stat HEAD` empty; `reports/hc/DEPLOY` e214c393 (= "c2e6973\n") |
| `el_hc/REVISION` | **absent** | hc_postwatch writes `c2e6973` at arming (untracked, as el_f3 / el_thin; m0_audit reads it, l.158) |
| `el_hc/scripts/rescore_label_versions.py` | 1e41202b99611169030abc5d2524f72c | pass 3 (= PF2 / THIN) |
| `el_hc/scripts/rescore_logit_adjust.py` | ec315d2e8c3e3015cb31a1fc3675ddd5 | pass 6 (= el_f3, PF2's comparator LA) |
| `el_hc/data/splits/val.txt` / `test.txt` | 9dcccf00 / a31fad14 | = el_f3; data/escdd_masks and labeled point to the same targets as el_f3 (el_f1/data/escdd_masks; el-fault-detection/data/labeled) |
| `el_f1/reports/f1/m0_audit.py` / `m0_audit_tau.py` | d36f7438d0fefb0ffc926c69f6c6af2d / d77241bbe2845cabc2779adc827eb838 | pass 4 |
| `el_f1/reports/f1/ext117/stems_eval.txt` (106) | 5266806b559f74bcf9eae167bb076b95 | E1 list (md5 only) |
| `el_f1/reports/f1/smoke_v1/mim_step0.pth` | 178b872d35d15689f6ab38bf57789327 | ImageNet R34 step 0 (cosines) |
| `el_f3/reports/enc_cosine.py` | d3bc7a708d3630de7322fc6dd2ff403e | pass 8 (el_hc has none) |
| `el_f3/reports/pf2/scripts/gpu_gate.sh` | 00fabfddaf7d7dfd11e25008f94f744d | shared gate |
| `el_f3/reports/pf2/post/MANIFEST.md5` (290 lines) | 3827f7c08e653ae5a2164093b242b3b6 | comparator check; m0 SUPPF s5-9 (+ tau0 / tau1) present by name |
| `el_f3/reports/pf2/post_extra/B5_DEVICE` | 4e7ff5667feec6c8ca239343833c224b (= "cuda") | B5 device (as PF2 / THIN) |
| `el_f3/reports/pf2/post_extra/{calib/*, pf2_scuffign.py}` | c172717e, 6e73ff11, e06dfc5f, 873591ff, e3615fdb | = local copies |
| `el_f3/reports/pf2/b5_work/dump/` | names only | SUPPF s5-9: val / test / ext npz only: **no rf, no synval** dump exists |
| `el_f3/reports/d/e1_context.tsv` | 12bd138523fccfc6be5b41df35d19147 | E1 strata (= local team_2026-10-29_features copy) |
| `/home/noob/work/nq/exp_HC.txt` | 01008fdfd25c3e0a70b0102d2f72b2bc | config re-check at the opening |
| `nq/scripts/nq_queue.sh` / `nq_gpumem.sh` / `nq_jobs.txt` | 156c6936 / 1c3671a3 / 5cb4bad9 | = APPROVED versions |
| `/home/noob/work/calib/scripts/v5/calib_dump.py` / `el_metrics.py` | 9694ad7d / f40a0efe | the synval superset (calib's routing pre-check, `ideas/routing_precheck.md`); local `ideas/scripts/` same md5 |
| `/home/noob/work/calib/scripts/calib_dump.py` / `el_metrics.py` | 1d35360e / 7936084e | intermediate versions (log 17:39): NOT used |
| `/home/noob/work/calib/frozen_candidate/` | c172717e / 6e73ff11 / e06dfc5f / 873591ff | calib's frozen B5 set |
| `/home/noob/work/domain_scratch/shv1/MANIFEST.md5` / `stems_eval.txt` (108) | 63dd5469cc4eeaf21025e98669d635e3 / f809683f | SHV1 |
| `/home/noob/work/domain_scratch/out/shv1p_stems_eval.txt` (80) | 7f651fc7348f4dcaa06d404645fa1951 | SHV1-p; `shv1c_subset.tsv` a9afc2df |
| `/home/noob/work/calib/data/rf/stems_eval.txt` (106) | 3a65c2fb0ecaf32e91377d4ad249029a | Hanifi _rf (images 106) |
| `/home/noob/work/found/t9/rf_sets.tsv` | 14771356ef7c99f567c5f80dad2e48dd | F51 51 cells / 36 modules (E, local copy same md5), H36, F19 |
| `/home/noob/work/found/p8/a8_screen_score.py` | 8eba76e5 | = local copy |
| `calib/out/rec/FINAL.val.json`, `rec_shv1/FINAL.synval.json`, `rec_shv1/MANIFEST.md5` | 6d038462 / ed5365dd / f089abce | FINAL reference rows (reused, §8 q2) |
| `calib/out/rec/SUPPF5_m{0..4}.val.json`, `rec_shv1/SUPPF5_m{0..4}.synval.json` | e23b33ac fc2a9bf7 29658f17 cabccfe9 ebae273b / 020c8023 8ecc1a1f ece0559d 307de5cf 17beb574 | readout self-test (routing pre-check values) |
| FINAL members | latest.pth present | `/home/noob/work/cv02_noob_el/el_p6/experiments/p6_L3_100pct_s{0,1,2}`, `el_p13/experiments/p16_A_100pct_s{3,4}` (calib's run_shv1.sh) |
| python | `/home/noob/work/el-fault-detection/.venv/bin/python` → python3.12 | all passes |

## 3. Passes (hc_post.sh): reads, device, cost
Outputs `el_hc/reports/hc/post/` (+ `post.log`); work dirs outside post/: `reports/hc/b5_work`, `reports/hc/syn_work`; PIDs `reports/hc/post_pids.txt`.
| # | Pass | Reads | Device | Cost (S) |
|---|---|---|---|---|
| 0 | integrity: HEAD = DEPLOY = REVISION = c2e6973, 0 tracked; FROZEN.md5 (all REQ listed + `md5sum -c`); hc_copies.md5; PF2 MANIFEST `md5sum -c`; 16 external md5s; escdd_masks link = el_f3's | files above | - | s |
| 1 | completeness: `grep -q "step 20000/20000"` per HC stdout (the one stdout grep) | 5 stdouts (grep -q only) | - | s |
| 2 | config re-check: diff vs pf2_SUPPF_100pct_s5 = exp_HC.txt, seed K; latest.pth md5 | config_used.yaml, latest.pth | - | ~10 s |
| 3 | rescore_label_versions per run | ckpt, test / val | GPU, gate × 5 | ~5-10 min |
| 4 | m0_audit default + tau 0 / 1 (val, test, ext117), `--code el_hc` | ckpt, val / test / E1 | GPU, gate × 3 | ~10-15 min |
| 5 | tau0 check (cells equal, step 20000, code_revision, 54 / 50 / 106) | m0 JSONs | CPU | s |
| 6 | LA tau 0 / 1 (test, val) `--check` | ckpt, rescore JSONs | GPU, gate | ~5 min |
| 7 | E1 co-primaries (decision): self-test on the 10 m0 files, then scorer | m0 JSONs (HC + PF2's SUPPF), e1_context | CPU | ~1 min |
| 8 | 20k cosines vs ImageNet R34 (reported) | ckpts, mim_step0 | CPU, 4 thr | ~2 min |
| 9 | frozen extras (reported): hc_b5.sh (per-run B5 dump val / test / ext, records + self-check exact, summaries; HC pooled OP) and hc_scuffign.sh | ckpt, val / test / E1, m0 | GPU (B5_DEVICE cuda), gate per hook + per B5 run | ~15-20 min |
| 10 | SHV1 (decision): hc_shv1.sh | ckpts of 10 runs, val 54, rf 106, SHV1 108, m0 val cells, calib records | CPU fp32, 8 thr | dumps ~30 min (2,680 forwards at ~0.67 s, from calib's 17:47-17:59 SHV1 dump); records 30 calls ~15-30 min; RAM peak ~9 GB (rf / SHV1 records, as build_a8_runner §7) |
| 11 | F51 guard (decision): self-test, then hc_f51.py | val / rf dumps + records, rf masks / ignore, rf_sets | CPU | ~2-5 min |
| 12 | MANIFEST.md5 | post/ | - | s |
- Total S: ~1.5-2 h wall; GPU ~40-50 min (16 gated starts, ≥ 120 s apart); disk on gaint ~3.5 GB syn_work + ~1.4 GB b5_work; pull ~100-150 MB (m0, B5 rec, SHV1 / rf records).
- Decision passes (7, 10, 11) do not abort: rc in `decision_rc.txt`, MANIFEST still written, opening rc 1 if any failed. Core passes 0-6 abort (rc 1). Refusal before any pass (GS < 9,900 or post/ exists): rc 2. End line always: `[<date>] nq scoring done: post rc=<rc>` in nq/post.log, rc captured before `$(date)`.
- Trigger failures (HC rc ≠ 0, `CONFIG FAIL hc_...`, MAXH 96 h, FROZEN changed): `nq NOT scored (FAIL): ...`, deferred until no nq training PID is alive (§8 q7). Arming refusals never write an nq end line.

## 4. Device for SHV1 + F51: CPU fp32 (S, on E)
- E: SUPPF s5-9 have no rf / synval dumps (PF2's b5_work holds val / test / ext only), so both arms must be dumped at HC's opening; one device for all 10 runs keeps the contrast paired (coach's THIN rule: same device on both sides).
- E: the pre-registered baselines (SHV1 matched relR@2 0.694 / 0.876, FINAL 0.730 / 0.892, Δb +0.9 / +0.4) are calib's CPU fp32 numbers (routing_precheck.md); the self-test reproduces them on the same code path.
- S: no GPU memory used, so no gate wait and no risk to finllm's 2 GB floor if anything else trains; cost (~1 h CPU) is acceptable after the GPU passes. No m0 exists for rf / SHV1, so the cuda "exact" self-check reason (PF2 B5) does not apply; val records get a cpu-profile self-check vs m0 (reported).
- GPU variant (not drafted): calib_dump `--device cuda --batch 8` behind `gate_wait $GS`, both arms.

## 5. Definitions as coded (E, from the code)
- **E1 (hc_e1_coprim.py):** per run, all 106 ext cells pooled from the default (argmax) m0 JSON; relF1@2 = thin's relf1 (copied verbatim); inactive IoU = `m0_analyze.agg(...)["iou"][11]`; asserts step 20000, 106 identical stems, code_revision SUPPF e544133 / HC c2e6973. Rule 1 /3, sd ddof 1. Strata (reported): 29 scuff + half-cut, 29 half-cut without scuff, 48 full, 58 half-cut, 77 other (sizes asserted). Self-test: = ast-extracted relf1 of the frozen thin file, = agg relF1 (exact), agg inactive = pf2_e1_extra.py formula (≤ 1e-12); prints booleans only.
- **SHV1 (hc_shv1_read.py, el_metrics f40a0efe imported):** per arm, counts pooled over 5 seeds (pool_cells). Oracle b = `oracle_b_relf1` (OPGRID, ties smaller b). **Mechanism = max relR@2 over GRID with relP@2 ≥ 0.90 on SHV1 (routing_precheck.matched, unchanged); HC − SUPPF < +0.05 → "mechanism FAILED".** Reported: oracle b V0 / SHV1 / SHV1-p and gaps, matched relR@2 on V0 and SHV1-p, relR / relP / pixel R at b 0, per-seed rows, FINAL (b_dep 0.75). Self-test: FINAL +1.1 / +1.5 / 0.892 / 0.730 and SUPPF s0-4 pooled +2.9 / +3.8 / 0.876 / 0.694 from calib's records.
- **F51 (hc_f51.py):** a8_screen_score.rule() with A8 := HC, A8c := SUPPF: 1,000-bin AP per run, arm mean, paired bootstrap over the 36 F51 modules (asserted; 51 cells), 2,000 resamples, rng seed 0. **FAIL iff boot_hi < 0** (97.5th percentile). Its GO terms are stored as "not used". Loader = a8's main() with two speed-only changes (pc read once per set, GT read once per stem). b_rel / FA from el_metrics f40a0efe choose_op (OPGRID; not found/t9 46b682cc, build_a8_runner §5.4).
- **Data scope:** SHV1 / F51 passes read val, rf and SHV1 only (calib_dump without `--opening`, no ext set). Test and E1 are read only by passes 3, 4, 6, 7, 9 (the opening).

## 6. Local checks (E, laptop, light)
- `bash -n` OK on the 5 shell files; in-memory `compile()` OK on the 3 new .py (no bytecode written).
- `hc_f51.py --selftest`: a8's own selftest OK; HC better → guard passed, worse → FAIL, identical → passed; d = direct AP difference; bootstrap reproducible. PASS.
- `hc_e1_coprim.py`: `--selftest` PASS on 10 synthetic m0-format files; main run on them OK (rule-1 lines).
- `hc_shv1_read.py`: main run OK on synthetic records (el_metrics.cell_record on 64 × 64 toys, real SHV1 / SHV1-p stem lists); swapping arms gives "mechanism FAILED". `--selftest` needs calib's records: not run locally (per-cell JSONs), runner runs it (pass 10a).
- Trigger regexes checked on a fake launch.log (5 / 5 counts; rc=137 caught; interim lines do not match nq_gpumem's stop regex).

## 7. Runner steps after coach's FREEZE
1. Copy `scripts/hc/` to gaint `/home/noob/work/nq/hc/` (keep subdirs); `md5sum -c` against the §1 list there. Coach writes `FROZEN.md5`.
2. Arm in tmux: `GS=<coach's ruling, ≥ 9900> bash /home/noob/work/nq/hc/hc_postwatch.sh` (PID in nq/hc_postwatch.pid; writes el_hc/REVISION if absent).
3. To pause CPU passes of hc_shv1.sh: touch `el_hc/reports/hc/CPU_HOLD`. To stop: python PID from `post_pids.txt` / `syn_work/pids.txt` first, then the script.
4. Pull `reports/hc/post/` + `post.log` + nq/gpumem.log; verdicts only after coach's recompute (test two-set rule via m2_rung locally, as pf2_post_local.sh: not drafted here).

## 8. Open questions
1. coach: **freeze calib's synval superset** calib_dump 9694ad7d / el_metrics f40a0efe for HC. They are calib's UNFROZEN superset (frozen_pf2/README; log 18:03); calib reported B5 outputs byte-identical to 6e73ff11 (log 17:42). Needs coach's freeze.
2. coach: FINAL reference reuses calib's existing CPU records (FINAL.val.json 6d038462, FINAL.synval.json ed5365dd) instead of a fresh dump; members are reachable on gaint (~10 min CPU) if a recompute at the opening is wanted.
3. coach: SUPPF s5-9 SHV1 / F51 readouts do not exist; the draft produces them at HC's opening (CPU, val / rf / SHV1 only; not a new test or E1 read of SUPPF). Confirm.
4. coach: F51 "upper 95% bound" = 97.5th percentile (two-sided, mirror of a8's lower bound), not a one-sided 95th.
5. coach: matched relR@2 scans GRID incl. b +0.75, as the pre-check baseline; OPGRID-only would differ only if +0.75 wins.
6. coach: GS value (≥ 9,900 in §9.3; likely no HC lane trains at opening time).
7. runner / coach: on an early HC failure the `nq NOT scored` line is deferred until no nq PID is alive, so nq_gpumem keeps logging the other lanes. If the queue is under HOLD and later resumes, nq_gpumem must be restarted (the queue checks it only at arming).
8. runner: ~9 GB RAM peak during rf / SHV1 records (free not checked: not in the allowed commands). A8 scoring (CPU, 8 threads) should be finished before pass 10; if not, 16 threads: confirm or use CPU_HOLD.
9. coach (S, from bash semantics; not tested on gaint): in thin_post.sh / pf2_post.sh, `[ a ] && [ b ] && [ c ]` and `(cd $PF && md5sum -c ...) && echo ...` under `set -e` do not abort when an earlier term fails (bash exempts all but the last command of an && list). THIN's integrity and comparator checks could pass silently. hc_post.sh uses explicit `|| fail`. el_thin not touched.
10. Not drafted (reported items done after the pull, as PF2): test m2_rung two-set verdict, E1 width-robust table, crack-free px, E1 oracle relF1@2 (in B5 ext summaries).
