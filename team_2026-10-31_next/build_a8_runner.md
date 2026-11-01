# build_a8_runner: A8 screen scoring build (DRAFT for coach's review)

runner's helper agent, 1 Nov 2026 ~19:50 IST. Protocol: `protocol_A8screen.md` v1.1 (§3 GO rule, §9 lock record, §10 data.root, nq APPROVED 19:43; on-disk md5 64f430a5 when read). Tags: E measured (file / command), S judgement.
- Draft only: no job started anywhere. gaint use was read-only (ls, md5sum, git log / diff, sed / grep on code and scripts, head of the nq exp files). No training .stdout or train.log, no test or E1 file, no per-cell JSON was opened.
- a8_score.sh refuses to run until coach writes `FROZEN.md5` in its gaint script dir (protocol §10: "No scoring trigger arms before coach FREEZES the scoring files").

## 1. Files (local `scripts/a8/`; runner copies the first three to gaint `/home/noob/work/a8_score/scripts/`)
| File | md5 | What |
|---|---|---|
| `a8_score.sh` | 73226de51e1ae93cc00b771be79eb1a1 | the scoring driver (passes 0-6, §4) |
| `a8_calib_dump_4k.py` | 12e4818ea6e172e4332fa34f3fc3446b | calib_dump c172717e with ONE line changed (l.54 step assert 20000 → 4000). **Needs coach's review** |
| `a8_init_dump.py` | 87923f8e395856cdf2eb4abe13145051 | new: step-0 encoder reference for enc_cosine_hr. **Needs coach's review** |
| `a8_calib_dump_4k.diff` | c50a916ad3f9f43b648bf7fee32156f4 | unified diff vs c172717e (1 line) for review; not deployed |
- a8_score.sh hard-codes the md5s of the two .py files and of every external file below; coach's FROZEN.md5 must list a8_score.sh (checked).

## 2. External paths, md5 as found on gaint (E, 19:35-19:47)
| Path | md5 | Use |
|---|---|---|
| `/home/noob/work/el_f8` HEAD = `REVISION_f8` | c280e8c2f5cec2fd3ed38eb4ea010da7e6966dde | code; `git diff --stat HEAD` empty. e544133..c280e8c2 touches 4 files only (hrstem_unetpp, model_factory, enc_cosine_hr, tests): data / utils code = house |
| `el_f8/src/models/hrstem_unetpp.py` | 42c3980d9ea6bdc27cda818c1f554b9d | model build in the dumper and init ref |
| `el_f8/src/models/model_factory.py` | 9cd345b80a1e15d371e03ea30d12b0bd | same |
| `el_f8/reports/enc_cosine_hr.py` | d72f4324cb0417a211025cf0f18b2465 | 4k cosine (run in place) |
| `el_f8/data/splits/val.txt` (54) | 9dcccf00662dfca750f0b46628f8d5bb | val stems (dumper via --code el_f8) |
| `el_f8/data/splits/test.txt` (50) | a31fad14fa27ee28e2a2319b8976aba3 | NEVER read (named here for the record only) |
| `/home/noob/work/a8_root/SPLITS.md5` | 0880d3e0257bced258e3102f0e6b3348 | train 842f27c4, val 9dcccf00, test 9dcccf00 (= val); labeled → el_f8/data/labeled |
| `el_f3/reports/pf2/post_extra/calib/calib_dump.py` | c172717e5989edb8e0b7b312096f9180 | base of the 4k copy (= calib/frozen_candidate) |
| `el_f3/reports/pf2/post_extra/calib/el_metrics.py` | 6e73ff11aaa6171a52b5a5404877ab46 | records + the GO scorer's import |
| `/home/noob/work/found/p8/a8_screen_score.py` | 8eba76e5bb0783e9d4ecc432dea4a785 | GO rule |
| `/home/noob/work/found/t9/rf_sets.tsv` | 14771356ef7c99f567c5f80dad2e48dd | F51 51 / H36 36 / F19 19, module per stem (local copy `ideas/found_scripts/t9_rf_sets.tsv`, same md5) |
| `/home/noob/work/found/t9/el_metrics.py` | 46b682ccbdc35b1c3c593a72cc75401b | NOT used (a8_screen_score's default import; §5 item 4) |
| `/home/noob/work/calib/data/rf/stems_eval.txt` (106) | 3a65c2fb0ecaf32e91377d4ad249029a | rf stems; images / masks / ignore 106 each (ls count) |
| `/home/noob/work/weights/dinov3_convnext_tiny_lvd1689m_timm.safetensors` | abf904631bf1ba23642e60c46b20dc5e | A8 backbone (reloaded at every model build) |
| `/home/noob/.cache/torch/hub/checkpoints/convnext_tiny-983f1562.pth` | fcc1480a11e933010f4d7e0ccb7e33b1 | A8c backbone |
| `/home/noob/work/nq/launch.log` | (live) | start condition: "trained <run> rc=0", "config OK <run> vs" |
| `/home/noob/work/nq/exp_A8.txt` / `exp_A8c.txt` | 4643e1fd / ff3cb9c7 | read once (head) to match the config_used.yaml key format |
| python | `/home/noob/work/el-fault-detection/.venv/bin/python` → python3.12 | as training |
| `el_f3/reports/pf2/scripts/gpu_gate.sh` | 00fabfddaf7d7dfd11e25008f94f744d | not used (CPU choice) |

## 3. Device: CPU fp32 for all 4 runs (S, on E)
- E: found's run spec (`ideas/idea08_runspec.md` §2) requests no GPU scoring pass ("Final weights only are scored, on CPU after training"); protocol §9 fixes no device.
- E: no m0 JSON exists for screen runs, so PF2's reason for cuda (bf16 reproduced m0 at tol exact) does not apply. CPU fp32 is calib_dump's default numerics; PF2E's B5 pass used it (coach APPROVED).
- E: nq order puts A8 s0 / A8c s0 first and s1s 4th / 5th beside HC (protocol §10, 19:43). So scoring will overlap HC training. A GPU pass would need gate_wait at GS ≥ 9,900 next to HC lanes and finllm's 2 GB floor; the hrstem dump peak is also unmeasured. CPU uses no GPU memory.
- S: cost is small (§7). Env: CUDA_VISIBLE_DEVICES="", nice 19, OMP / MKL / OPENBLAS 8; records run 8 procs × 1 thread; HF_HUB_OFFLINE=1.
- GPU variant (not drafted): `--device cuda` behind `gate_wait $GS` (GS ≥ 9,900 beside training), after a dump smoke for the peak; all 4 runs on the same device.

## 4. Passes, what each reads (E, from the code; no test, no E1)
| Pass | Reads | Writes (`O=/home/noob/work/a8_score/v1`) |
|---|---|---|
| 0 static + start | FROZEN.md5, 15 md5s (§2), git HEAD, a8_root, launch.log, 4 × config_used.yaml (awk on 8 keys), md5 of 4 × latest.pth | `expected_md5.txt`, `out/inputs_md5.txt`, `frozen/` copies (el_metrics, calib_dump, a8_screen_score, rf_sets) |
| 1 selftest | nothing (synthetic) | log |
| 2 dump ×4 | latest.pth (step 4000 asserted), config_used.yaml, weights file, val 54 images (el_f8 val.txt), rf 106 images | `work/dump/<run>.{val,rf}.npz` (stems, margin, oth, pc) |
| 3 records ×8 | dumps, val masks_escdd (54), rf masks + ignore (106) | `out/rec/<run>.{val,rf}.json` (+ `.selfcheck.txt` UNCHECKED) |
| 4 cosine | config_used.yaml + weights file (init ref), latest.pth | `work/init/<run>.init.pth`, `out/enc_cosine_4k_{A8,A8c}.{json,txt}`, `out/a8_validity.txt` |
| 5 GO rule | dumps (pc), records, val masks, rf masks + ignore, rf_sets.tsv | `out/a8_screen_score.{json,stdout}` |
| 6 summary | pass 4 + 5 outputs | `out/a8_summary.txt`, md5 lists, `out/MANIFEST.md5`; log `O/a8_score.log` end line "a8 scoring done: rc=N" |
- **No test:** dumps get `--sets val rf` and no `--opening`, so calib_dump's own assert would refuse `test`; val stems come from el_f8's val.txt; no command names a test list or test mask. a8_root's test.txt (= val) is not read by scoring.
- **No E1:** no `ext` set, no ext117 path; el_metrics `--ext` default stays unused (sets val / rf only).
- **No training log:** completeness comes from launch.log rc lines + the step assert + latest.pth md5s; no .stdout / train.log is read.

## 5. 4k checkpoints and el_f8's model in the frozen scorers (E)
1. **calib_dump c172717e cannot load the screen checkpoints:** l.54 `assert int(st.get("step", -1)) == 20000`. The trainer writes latest.pth at `done == total_steps` with `"step": done` (trainer.py l.694, l.841), so step = 4000. Fix: `a8_calib_dump_4k.py`, the same file with `== 4000` on l.54 (diff 1 line; a8_score.sh re-checks the diff at run time). **Needs coach's review + freeze.**
2. **el_f8's model loads with no change:** calib_dump drops encoder_init / decoder_init and sets encoder_weights None. build_hrstem_unetpp ignores that key and reloads `backbone_weights` from the file (A8 via timm's pretrained path with the file overlay; A8c via torch.load + remap). The file must stay in place (builder's minor 4); both md5s are checked. forward returns (B, 24, 512, 512) logits. Input = calib_dump's (x/255 − 0.5)/0.25, the house normalisation (data code unchanged). load_state_dict is strict on `st["models"]["model"]`.
3. **enc_cosine_hr needs an init (A) file; none exists for el_f8 runs** (PF2 used `rn50_imagenet_step0.pth`). `a8_init_dump.py` builds the model from each run's own config_used.yaml through el_f8's build_model (the training init path). It asserts every encoder tensor equals the weights file (stem = RGB sum, max|d| ≤ 1e-6; others exact) and saves `{"models": {"model": sd}, "step": 0}`. **Needs coach's review.** `--backbone` = each arm's own timm name (A8 `convnext_tiny.dinov3_lvd1689m`, A8c `convnext_tiny`).
4. **a8_screen_score's default import is the wrong el_metrics:** `--el-metrics` defaults to found/t9 (46b682cc). Its choose_op scans the full GRID including b = 0.75; 6e73ff11 (calib's OP rule, protocol_PF2 §4.1, also the records writer) limits it to −4.0..+12.0 step 0.1. Both grids have 162 points, so the wrong import runs silently; b_rel differs only if 0.75 wins. The draft passes `--el-metrics $O/frozen` (the 6e73ff11 copy).
5. a8_screen_score's comment says it records the el_metrics md5 in its output; it does not (argv only). a8_score.sh records it in `out/scripts_md5.txt`.

## 6. GO-rule computation path (E, a8_screen_score 8eba76e5 + el_metrics 6e73ff11)
1. Per run and cell: 1,000-bin p(crack) histograms of the dump's `pc` on GT-crack / non-crack keep px (val: all px; rf: not ignore).
2. Crack AP per run and set = binned AP of the pooled histograms; arm value = mean of 2 seeds. Sets: F51 / H36 / F19 from rf_sets.tsv; val = the 54 dump stems.
3. **Term 1a:** A8 − A8c F51 AP > 0.
4. **Term 1b:** the 36 F51 modules are resampled with replacement, 2,000 times, rng seed 0 (a multiset of stems). Per resample the AP is recomputed per run, then the arm-mean difference is taken. The 2.5th percentile must be > 0.
5. **Term 2:** val AP A8 − A8c ≥ −0.02.
6. **Term 3:** per run, b_rel = choose_op(curves(val records), relR, relP): max relR@2 s.t. relP@2 ≥ 0.90 on the OP grid; ties go to the smaller b; if unreachable, the max-precision b, flagged. FA = Σ `pred[j]` over the cells of the set with n_gt = 0 in the rf records. Arm = seed mean. A8 ≤ max(1.5 × A8c, A8c + 200), checked for H36 and F51 separately.
7. GO = all 5 true. Reported: per-run values, cell AUROC, F51 sign count, boot hi, F19, inactive IoU at b_rel.
8. Validity (pass 4): stage2 and stage3 `cos_w` ≥ 0.5 per run; an arm is VALID only if both runs pass. `a8_summary.txt` prints GO / KILL, or NO VERDICT if an arm is invalid (§3). This is mechanical: coach recomputes before any verdict.

## 7. Cost (S)
- Dumps: 640 CPU fp32 forwards (4 × 160 cells). builder E: ~8 s per 2 × 512 fwd + bwd on CPU (`review_f8_wrapper.md`), so ~0.5-1.3 s per forward at 8 threads, ~5-14 min.
- Records: 8 calls × 8 procs, ~4-8 min. Init + cosine: ~2-3 min. GO scorer: ~1-3 min. Its loader re-reads each full `pc` array per cell, ~7 GB of page-cache reads per run.
- **Total ~15-30 min wall, 0 GPU-h.**
- RAM peak ~9 GB, during rf records. Frozen make_records re-reads `z["margin"]` / `z["oth"]` per cell and keeps 106 views: 106 × 83 MB. Val records ~2.3 GB, dumper ~2-3 GB, passes sequential.
- gaint disk: dumps 0.84 GB, init refs 0.56 GB. Laptop pull: `out/` ~10 MB (records ~8 MB) + the log.

## 8. Runner steps after coach's FREEZE
1. Copy the three files to `/home/noob/work/a8_score/scripts/` and check their md5s. Coach writes `FROZEN.md5` there (a8_score.sh, a8_calib_dump_4k.py, a8_init_dump.py).
2. Optional `MODE=check bash .../a8_score.sh`: static checks only, log `a8_score/check/a8_score.log`, end line "a8 check done: rc=N".
3. Arm in tmux (MODE=wait polls launch.log every 60 s, MAXH 72). Script PID in `v1/a8_score.pid`; python PIDs in `v1/pids.txt`. `v1/HOLD` pauses before the next pass.
4. Pull `v1/out/` + `v1/a8_score.log`; dumps and init refs stay on gaint (md5 lists in out/). Coach recomputes.

## 9. Open questions
1. coach: approve `a8_calib_dump_4k.py` as the 4k path (one-line copy), or prefer a runtime patch of c172717e?
2. coach: approve `a8_init_dump.py` (init ref via build_model; init == file asserted)?
3. coach: confirm `--el-metrics` = frozen 6e73ff11, not the found/t9 46b682cc default (§5 item 4).
4. coach: validity rule as drafted: cos_w only, per run, both seeds; cos_ln / gamma / norm ratio reported only. Or arm mean, or cos_ln in the rule?
5. coach: records are UNCHECKED (no m0 for screen runs). An optional sanity check against metrics.json `val_history` at step 4000 is not drafted. metrics.json also holds a `test_final` block (= the val duplicate under a8_root), so reading it needs a ruling.
6. runner: gaint has no file-based CPU critical-window flag. The draft pauses on `v1/HOLD`; confirm, or name the flag.
7. runner: ~9 GB RAM during rf records beside HC training: OK?
8. runner: the trigger is launch.log "trained <run> rc=0" ×4 + "config OK <run> vs" ×4. Scoring writes nothing to nq/post.log, so nq_gpumem's "nq scoring done" stop is unaffected.
