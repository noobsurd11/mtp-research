# Idea 8 run spec for runner's intake (found, 31 Oct 2026)

Design: `idea08_foundation.md` v3.x (md5 193435fc), §4a probe, §4a' screen. The user approved the weights and the 2-seed 4k PF screen **after PF2** (team-lead, log.md).
- **Status: NOT ready to queue.** Open items are in §3.
- No test cell in any step.
- **E1 is not read in the probe or the screen** (user's E1 policy: second test set, read only at 4b's opening).

## 1. Step 4a, P8-probe (frozen encoders, linear heads): **CPU by default; no GPU slot requested**
- **Where:** gaint CPU, `CUDA_VISIBLE_DEVICES=""`, nice 19, ≤ 8 threads.
- **Code:** `ideas/scripts/p8_probe.py` (**md5 f2033a3e**, frozen; gaint copy `/home/noob/work/found/p8/`), built on D1's `scripts_cv02/trackD_probe.py`. CPU smoke on 4 train cells (no val / rf read): all cached encoders + SAM2 Hiera-T run; DINOv3 skipped until its file exists; DINOv3 ViT feature path checked at 512 and 1024 with random weights.
  - It imports `el_f3` (e544133) read-only, for data lists and loaders only.
  - No worktree is needed: no training code changes.
- **Command (template):**
  - `CUDA_VISIBLE_DEVICES="" nice -n 19 /home/noob/work/el-fault-detection/.venv/bin/python -I p8_probe.py --code /home/noob/work/el_f3 --rf /home/noob/work/calib/data/rf --sets-file /home/noob/work/found/t9/rf_sets.tsv --encoders <list> --seeds 0 1 --steps 2000 --out /home/noob/work/found/p8/`
- **Writes:** probe heads (≈ 2-5 MB each) and per-set histograms / JSON. **No model checkpoints.**
- **Steps:** per encoder and seed, one feature-extraction pass over 532 + 106 cells, then 2,000 linear-head steps (batch 8).
- **Memory:** CPU only. S: RAM ≤ 20 GB with stride-4 features cached for 478 cells at fp16.
- **Time:** S, revised after the smoke: ~4-6 h CPU for 10 encoders × 2 seeds (2,000 head steps at 512² on CPU dominate). If team-lead prefers the GPU: ~1 GPU-h as a scoring-class pass, peak **unknown**, so runner smokes it first.
- **Data read:**
  - el_f3 `data/labeled/images` + `labeled/masks_escdd` (train 478, val 54);
  - `/home/noob/work/calib/data/rf` (106 cells: F51 / H36 / F19 per `rf_sets.tsv` md5 14771356).
- **Weights read (md5 on gaint):**

| Encoder | File | md5 |
|---|---|---|
| IN ConvNeXt-T (torchvision) | `~/.cache/torch/hub/checkpoints/convnext_tiny-983f1562.pth` | fcc1480a11e933010f4d7e0ccb7e33b1 |
| IN R50 / R34, DINOv2-S/14 | `~/.cache/torch/hub/checkpoints/` + HF smp-hub cache | recorded by the script at run time |
| SAM2 Hiera-T (timm, encoder only) | `/home/noob/work/weights/timm_sam2_hiera_tiny_fb_r896.safetensors` | c453c0749746456916fdd110ae8aa724 |
| DINOv3 ConvNeXt-T, ViT-S/16 | **pending the user's route A or B** (`idea08_download.md`) | sha256 given there |
| SUP100-PF s0 / SUP100-g s0 (sanity rows) | `el_f3/experiments/f3_SUPPF_100pct_s0`, `f3_SUP_100pct_s0` | step 20,000 asserted |

- **Approval:** this is a CPU descriptive step that picks candidates and never kills (judge, idea 8 v2 re-review). It needs judge's OK on the script's pre-registered pick rule (§4a), not coach's APPROVED.

## 2. Step 4a', PF fine-tune screen (the kill gate): **GPU, via runner's queue only**
- **Worktree / commit:** new gaint worktree `el_f8` from `e544133` + the ConvNeXt wrapper commit. **TBD:** coach is deciding whether builder or found builds it.
  - Opt-in switch, default off, so the build is bit-identical to e544133 with the switch off (identity test).
- **Runs:** 4 = {A8: DINOv3 ConvNeXt-T-PF, A8c: IN-1k ConvNeXt-T-PF} × seeds {0, 1}.
  - Optional descriptive reference: SUP100-PF R34 on the same short schedule × 2.
- **Command (template; final switch names from the wrapper commit):**
  ```
  python scripts/train.py --config configs/supervised.yaml --opts <SUP100-PF opts as f3_SUPPF_100pct> \
    model.name=hrstem_unetpp model.backbone=convnext_tiny model.backbone_weights=<file per arm> model.backbone_weights_format=<timm|torchvision_convnext> model.backbone_drop_path=0.0 \
    training.total_steps=4000 training.warmup_steps=200 \
    training.encoder_pf={freeze:200,ramp:200,lr_mult:0.1,wd:0} training.val_every=4000 \
    seed=<0|1> run_name=f8_<A8|A8c>_4k_s<0|1>
  ```
  - Cosine to 0 at step 4,000: the house schedule with total_steps = 4,000.
- **Steps:** 4,000 per run.
- **Writes:** checkpoints `latest.pth` at 2,000 and 4,000 (S: ~0.4 GB each with optimizer state) and the stdout.
  - Final weights only are scored, on CPU after training: a calib-format dump on val + rf, plus el_metrics records. So **no GPU scoring pass** is requested.
  - Rule: `ideas/scripts/a8_screen_score.py` (**md5 8eba76e5**, frozen). Synthetic self-test OK. I/O test on calib's existing dumps with identical arms gives Δ 0 and GO false, as designed.
- **GPU memory peak: unknown.** Runner smokes 300 steps first. S estimate 8-11 GB, between R34-PF (6.4 GB) and RN50-PF (11,186 MiB measured).
- **Time:** S: ~0.3-0.5 GPU-h per run, ~1.5-2 GPU-h total.
- **Data read:** el_f3 `data/` (train 478, masks_escdd; val 54). No test, no E1, no pool.
- **Weights (md5):** IN-1k ConvNeXt-T fcc1480a…; DINOv3 ConvNeXt-T pending route A or B.
- **Approval:** user OK given (after PF2). **coach APPROVED: pending.** The protocol is not written yet; the rule is fixed in `idea08_foundation.md` §4a'.

## 2b. Wrapper status and smoke requirements (builder's review, `review_f8_wrapper.md`)
- **Commits** (el_f8, branch f8):
  - 063f74f0, the wrapper;
  - 920c6695, review fixes: enc_cosine_hr classifies 1-D tensors by module type (22 LN + 18 gamma on ConvNeXt-T); Hiera 512 grad test;
  - **c280e8c2 (deploy candidate):** explicit `model.backbone_drop_path` (code default 0.0, timm's default; screen opts set `model.backbone_drop_path=0.0`). Suite 296 passed, 3 skipped.
    - CPU identity re-run at c280e8c2: house and PF IDENTICAL to the e544133 export (B2 20997fe1, D2 8029d6a3).
    - File md5s: hrstem_unetpp.py 42c3980d, model_factory.py 9cd345b8, test_f8_hrstem.py 00888cf0, enc_cosine_hr.py d72f4324.
  - Suite 295 passed, 3 skipped.
- Builder re-ran the house / PF CPU identity independently: IDENTICAL.
- **Smoke items for runner (after PF2):**
  - (a) Hiera uses SDPA, whose CUDA backward can be non-deterministic. Run two identical 200-step A8h runs and compare loss lines before relying on resume identity for Hiera.
  - (b) DINOv3 ConvNeXt file: once it exists, an output-equivalence check (timm-built model vs a reference forward) before any run.
    - Route B (timm mirror) loads through the timm path.
    - Route A (Meta format: downsample_layers / dwconv / pwconv1 keys) needs a new tested remap format first; the timm path would fail loudly on it.
- Scorers that rebuild the model reload `backbone_weights` from the file path (harmless; the file must stay in place).

## 2c. A8 / A8c exact model opts (1 Nov; DINOv3 route B fetched and checked)
- **A8:** `model.name=hrstem_unetpp model.backbone=convnext_tiny.dinov3_lvd1689m model.backbone_weights=/home/noob/work/weights/dinov3_convnext_tiny_lvd1689m_timm.safetensors model.backbone_weights_format=timm model.backbone_drop_path=0.0`. File md5 abf90463, sha256 = LFS oid. Equivalence check passed (`found_scripts/dinov3_equiv.txt`).
- **A8c:** `model.name=hrstem_unetpp model.backbone=convnext_tiny model.backbone_weights=/home/noob/.cache/torch/hub/checkpoints/convnext_tiny-983f1562.pth model.backbone_weights_format=torchvision_convnext model.backbone_drop_path=0.0`. File md5 fcc1480a; the remap is unit-tested equal to torchvision.
- **Both:** + SUP100-PF opts + `training.total_steps=4000 training.warmup_steps=200 training.encoder_pf.freeze=200 training.encoder_pf.ramp=200 training.encoder_pf.lr_mult=0.1 training.encoder_pf.wd=0 training.val_every=4000`, seeds 0 and 1, run names `f8_A8_4k_s{0,1}` / `f8_A8c_4k_s{0,1}`. Code el_f8 **c280e8c2**.
- **A8h (SAM2 Hiera-T) is not in the screen** (P8 run 1 pick). So builder's Hiera determinism smoke item (a) is moot unless Hiera re-enters.

## 3. Open before runner can queue anything for idea 8
1. ~~The user's DINOv3 route~~: **done**. Route B, user's words "B: I accept, fetch timm"; files fetched 1 Nov 14:28, sha256 MATCH, md5 in MD5SUMS, equivalence check passed.
2. Wrapper owner (coach), wrapper commit, identity test, a PF cosine table that includes LayerNorm stages.
3. `p8_probe.py` written and its pick rule OK'd by judge.
4. coach's protocol and APPROVED line for 4a'.
5. PF2 finished (the user's condition).
