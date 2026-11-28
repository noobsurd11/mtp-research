# Handover: arm x4_vfmctx (builder vfm, 27 Nov 2026)

E = measured, S = judgement. Progress log: harness/x4/arms/BUILD_vfm.md.

## What the arm changes
COMBO (hrnet_w18_unetpp_swad_const_pf_v11: HRNet-W18 + U-Net++ + PF + SWAD 10k to 20k, swad readout, v1.1, cv5v3) plus exactly
one opt: `model.vfm_ctx.name=vit_small_patch16_dinov3.lvd1689m` (bench.cards diff vs COMBO = that key only).
- A frozen DINOv3 ViT-S/16 (timm 1.0.30, 21,586,944 params, eval mode, torch.no_grad) embeds each cell: house-normalised
  grey is mapped back to [0, 1] grey, replicated to 3 channels, ImageNet mean / std; 512 px -> 32x32 patch grid.
- Its last-block normed patch features (384 ch) are bilinearly resized (no grad) to the stride-16 and stride-32 HRNet features
  (encoder levels 4 and 5 = inputs of the deepest U-Net++ decoder nodes) and added through a 1x1 conv (no bias) + BatchNorm2d
  with gamma = beta = 0 (vfm_proj.*, 592,896 trainable params, decoder lr group). nnSAM pattern (concat into the decoder);
  S: add with zero gamma is the same function class and makes step 0 equal COMBO (E: step-1 loss equals COMBO's on CPU).
- The pixel path is not replaced or downsampled. The ViT is outside the module registry: not in parameters, state_dict,
  optimizer, SWAD / EMA, BN re-estimate, encoder probe or checkpoints; bench_infer rebuilds it from the same pinned file.
- Code: src/models/vfm_ctx.py (new), src/models/bench_models.py (branch on model.vfm_ctx; absent = old path), tests/test_vfm_ctx.py.

## Papers
doi:10.1002/mp.17481 (nnSAM); arXiv:2611.14519 (FM adaptation vs task-specific U-Nets); arXiv:2603.01115 (LUMOS);
arXiv:2508.10104 (DINOv3). SHORTLIST_1127 A09; MASTER P030 / P043 (`vfm_ctx_r34_pf`, ledger gate BUILD).

## Commit, deploy, weights
- Branch x4_vfm (worktree /home/noob/work/bench_wt_x4_vfm) on bench_x4 b3ec7a5: 482a68c (code, card, tests), **7c26d0d4202f0cf7571e19b10c619528de366a8a** (card memory). cv02 deploy /tmp/noob_el/bench_7c26d0d (CODE.md5 md5 d8d9c1ad6ca3f1a9832c0b92c049bec1, CV02_CODE_OK).
- Card bench/methods/x4_vfmctx.yaml md5 e9fe4c06c8ad8f7dd08ae04b21b2cb07 (+ methods_cv02 variant, cvcard OK).
- ViT weights: timm/vit_small_patch16_dinov3.lvd1689m @ 3bf4720a82ec2066db88137180ff1f83a675cef0, model.safetensors md5 d6f2118f2b32975eb1eb2514d2612f31, sha256 2a1ec16a...a906b040 (= /home/noob/work/weights/dinov3_vits16_lvd1689m_timm.safetensors; DINOv3 License, user accepted 31 Oct). Placed as HF cache entries on gaint (~/.cache/huggingface/hub) and cv02 (/tmp/noob_el/cache/hf/hub), same layout as HRNet; listed in the card weights, so cq md5-checks it before every start. NOTE: cv02 /tmp is wiped on reboot (as for HRNet).
- No new venv: the house venv timm builds the ViT.

## Checks
- Unit tests (CPU, gaint): tests/test_vfm_ctx.py 9 passed: shapes; ViT gets no gradient and is not in parameters / state_dict / PF groups; init equals plain HRNet U-Net++ (tensors, RNG, output); hand-computed injection value; dtype follow + strict load; DINOv2 ViT-S/14 variant; bad keys. Existing model/card tests: 67 passed, 1 pre-existing failure (test_variants_exist).
- **Identity (keys off): IDENTICAL**, 5 CPU steps, COMBO card opts, ref bench_x4 b3ec7a5 vs this branch (identity_cpu.py 962379a6 / compare_id.py 3b83b364; /home/noob/work/bench_x4_vfm_io/check/run.log).
- Arm 5 CPU steps: rc 0, no Traceback, no nan. bench_infer model path: rebuild + strict load gives IDENTICAL logits (CPU). The GPU dump path is not yet exercised (S: first real job's dump does it; dump gate 6,200 vs COMBO dump peak 3,944 + ViT about 0.1 to 0.4 GB).

## Memory (cv02, queue x4_vfmsmoke, 200 steps, seed 5, fold 0, GPU 5, lane rule held, PIDs 1891724 / 2372300, outputs removed; logs in harness/x4/evidence/cv02_q/x4_vfmsmoke)
- E: arm peak 8,444 MiB; COMBO control 8,638 MiB (same GPU, one after the other). Steps/s at 200: 2.535 vs 2.575 (-1.6%).
- S: projected full-run peak 9,600 MiB (max smoke + 748 COMBO smoke-to-run + 2 x 83 MiB ViT copies); **gate 11,648 MiB**.

## Precomputed inputs
None (the ViT runs online; frozen, so nothing fold-dependent).

## Jobs lines (x4_make_jobs.py, in harness/x4)
Stage P (seed 5):
`python x4_make_jobs.py --out jobs/vfmctx_p.tsv --repo /home/noob/work/bench_wt_x4_vfm --commit 7c26d0d4202f0cf7571e19b10c619528de366a8a --seeds 5 bench/methods/x4_vfmctx.yaml=vfmctx@9600`
Stage S (seed 6): same with `--out jobs/vfmctx_s.tsv --seeds 6`. Both seeds at once: `--seeds 5,6` (checked: 10 lines, gate 11648, dump gate 6200, readouts swad, 11th field 7c26d0d...; first line `x4_vfmctx_f0_s5|bench/methods/x4_vfmctx.yaml|5|/tmp/noob_el/bench_data_v3b/roots/cv5v3_v11_f0|0|11648|6200|0||swad|7c26d0d4202f0cf7571e19b10c619528de366a8a`).
Read: `x4_read.sh <tag> VFMCTX=<qn>:vfmctx:x4_vfmctx:swad`.

## Judgement notes (S)
- Purpose is unseen-module recall (UR) and inactive; cv5v3 can mainly show non-inferiority on crack (SHORTLIST A09).
- Variants kept behind the same key, not in this card: `layers` (e.g. [2,5,8,11]), `inject` (add stride 8), `img_size` (1024 for a 64x64 grid), DINOv2 ViT-S/14 (Apache-2.0, needs a cache entry on cv02 first).

## Addendum (2026-11-27 23:44:31): expected extra memory and the smoke already run
- Process note: my own smoke queue x4_vfmsmoke ran before the lead's update ("no own cv02 queues; arch_harness smokes in x4_w1") reached me. It is closed and finished (2 jobs, 18:03 to 18:12 UTC). It no longer blocks other queues, and I will not run another. The integrator may re-smoke in x4_w1 if a same-queue number is wanted.
- Expected extra memory of the frozen ViT (S, from sizes): fp32 weights 83 MiB (86,362,376 B) per model copy; 2 copies at most at once (the model, plus the BN re-estimate scratch deepcopy at the end) = 166 MiB. Activations: no grad, bf16 autocast, batch 8 x 1,029 tokens x 384 dim, freed layer by layer: under 100 MiB. Projection convs + BN + Adam state: 592,896 params x 4 tensors x 4 B = 9 MiB; the features kept for backward are small. Total expected about +200 to +300 MiB over COMBO. E: the smoke peak was 8,444 MiB vs 8,638 for COMBO (allocator noise is bigger than the ViT). Gate 11,648 = 9,600 + 2,048 already includes +214 MiB over the COMBO full-run peak 9,386.
