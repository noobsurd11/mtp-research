# harness survey notes (running log; E = measured in files, S = judgement)

## 12 Nov, local context read
- BRIEF, README, handbook 14 (all), 07 s4-7, 18 M0, trackM/baseline.md, build_s2c, build_b6, build_pf2 read.
- Key facts (E, handbook 14):
  - trainer scripts/train.py; YAML defaults: inheritance; --opts a.b=c parsed as YAML (apply_opts).
  - model.name: unetpp, smp_unetpp (house), smp_unet, deeplabv3plus; el_f8 adds hrstem_unetpp (timm ConvNeXt-T/Hiera-T).
  - losses: weighted_ce, ce, ce_dice (house), tol_dice (el_p14); el_thin adds skel recall + clDice.
  - checkpoint latest.pth every 2000 steps, keys models.model / models.teacher.
  - data-root trick: data.root=<root> with labeled symlink + splits/{train,val,test}.txt; trainer evals test split at end.
  - b6 roots /home/noob/work/b6/b6_root_{0..4}: val=test=fold k; 425/107 etc.
  - scorers: rescore_label_versions.py (crack/inactive iou/P/R/AP/rel@1,2), m0_audit.py (Track M; 24x24 conf per cell, crack_rel2, crack_cc, inact_cc, p-bands, h1000), m0_audit_tau.py (el_f1 reports), b6_score.py 981b5f29 (= m0 functions line-identical; bf16 GPU exact vs m0), el_metrics.py 6e73ff11 (B5, calib), e1_task_metrics.py (cv02).
  - gates: peak + 2048 MiB; >=120 s spacing; flock gate /home/noob/work/gpu_gate; s2c_lib verify-by-cmdline PID stop.

## gaint code survey (E, read-only, snapshots in harness/src_snap/)
- Branch graph: main 24590fb -> p13 -> p17 -> sk1 -> m(1be64e1) -> f1 -> f2 -> f3 e544133 (linear). thin c9bbb02, f8 c280e8c, hc c2e6973, hc2 0405151 are siblings off e544133; nothing merges them. p14 (tol_dice) and p16 are NOT in f3.
- main..f3 diffstat: 33 files, +3749/-26. f3..thin 19 files +1639. f3..f8 4 files +386. f3..hc2 11 files +2389.
- train.py (el_f3, 553 l.): apply_opts l.92-101 (dot keys, yaml.safe_load value, creates missing dicts); build_optimizer l.108-131 (adam/adamw/sgd; PF 2 groups l.113-123); main l.203-322; build_benchmark_data l.325-476 (root/splits/{train,val,test}.txt, img root/labeled/images, masks root/<mask_subdir>; labelsafe aug l.431-434; eval loaders val+test l.456-464).
- config.py: defaults: inheritance with deep merge (docstring says shallow; code is deep).
- model_factory.py (f3, 100 l.): unetpp/sa_unetpp, smp_unet (vgg16), smp_unetpp (encoder_name, encoder_weights; l.77-87), deeplabv3plus; upsample_input wrapper l.13-32. f8 adds hrstem_unetpp l.89-93 -> hrstem_unetpp.py (timm forward_intermediates, prune_intermediate_layers, smp UnetPlusPlusDecoder, stride-2 HRStem).
- loss_factory.py (f3): ce, ce_dice (dice_classes, dice_weight), weighted_ce; consistency none/confidence_ce/tolerant_pl/class_threshold_ce/semi_ce. thin adds ThinCrackLoss wrapper (skel_recall, cldice) l.66-78, only on ce_dice.
- Loss signature: sup_criterion(logits, masks) only (trainer l.466). No extra targets path in f3.
- trainer.py (939 l.): LR lambdas cosine/constant/poly l.85-107; PF l.109-127; LambdaLR l.240; amp bf16 autocast l.395; clip l.506; EMA teacher ONLY for SSL (l.262-265; eval_model = teacher if ssl l.383); latest.pth payload l.691-715 (models dict: model, teacher...); fit l.767; end-of-run TEST on test_loader l.858-865 (+ best.pth test l.868-877); metrics.json l.882-911.

## scorers (E, local copies)
- rescore_label_versions.py 1e41202b (104 l.): ROOT=code dir; data/splits/<split>.txt sorted, GT data/escdd_masks/<split>; latest.pth, teacher if MT; bf16 autocast batch 8; crack+inactive only: iou/P/R/AP(1000 bins)/rel@1,2 pooled. Hard-wired cuda and data/ paths (l.32-33, 68).
- m0_audit.py d36f7438 (Track M, 181 l.): per cell 24x24 conf, crack_rel2 [TPp, P, TPr, G], crack_cc (gt/pr [size, hit] within 2 px), inact_cc (overlap), crack_pband 5 bands, crack_h1000 pos/neg. Sets val/test/ext (ext ignore mask). Asserts step 20000. encoder_init dropped, encoder_weights None at build.
- m0_analyze.py d5adbe6b: agg() pooled conf -> per-class IoU/P/R; miou24, miou_gt, miou_fix, miou_rob (list from >=3 GT cells), _no07; relP2/relR2/relF1; cc_rec50_20, cc_recany_20, cc_prec_20; in_cc_rec50 (>=100 px), in_cc_prec; subsets all/-noisy/-twins; per source = stem prefix.
- b6_score.py 981b5f29: comps/BANDS/cell_stats/dihedral/predict line-identical to m0_audit_tau d77241bb; GT from run's own data.root; held-out asserts; --device; output <run>.b6.json m0 schema. GPU bf16 EXACT vs m0 (54/54 cells).
- calib_dump.py c172717e: npz per model x set: stems, margin f16 (log pc - max other log p), oth u8 (argmax of 23 non-crack), pc f16. Ensembles = mean softmax. test only with --opening.
- el_metrics.py 6e73ff11 (B5): records from dump at every crack bias b in grid -4..12; OP chosen on val only; cell-level AUROC (s20), inactive area error; selfcheck vs m0 tol 0.0005 (cuda bf16), cpu profile 0.01/0.025.

## gaint state 12 Nov (E, read-only)
- GPU: 32,623 MiB total, 2,787 free: root finllm 6206 5,876 MiB + llama-server (noob, /home/noob/.local/src/llama.cpp) 22,382 MiB. No training can start.
- disk / : 1.6T, 250 G free.
- venv: py 3.12.3, torch 2.14.1+cu130, tv 0.29.1, timm 1.0.30, smp 0.5.0, albumentations 2.0.8, numpy 2.5.2, scipy 1.18.1, sklearn 1.9.1, opencv-headless 5.0, hf_hub 2.1.1, safetensors 0.8.0, einops 0.8.2, triton 3.8.0. NOT present: scikit-image, monai, transformers, nnunetv2, mmseg/mmcv, kornia.
- smp 0.5.0 decoders: deeplabv3 dpt fpn linknet manet pan pspnet segformer unet unetplusplus upernet; encoders incl. timm_universal (tu-*), timm_vit, mix_transformer; losses: dice focal jaccard lovasz mcc soft_bce soft_ce tversky.
- timm 1.0.30: DINOv3 ViT S/B/L/H+/7B (eva.py), DINOv3 ConvNeXt T/S/B/L (convnext.py), hieradet_sam2, swin v1/v2, mambaout; optim param_groups_layer_decay; utils model_ema.
- weights /home/noob/work/weights (MD5SUMS): sam2.1_hiera_tiny.pt, timm_sam2_hiera_tiny_fb_r896, dinov3_convnext_tiny_lvd1689m_timm, dinov3_vits16_lvd1689m_timm. HF cache: smp-hub resnet34/resnet50/vgg16 imagenet. torch hub: convnext_tiny-983f1562 (torchvision), dinov2_vits14_pretrain, resnet50-11ad3fa6.
- venv_sam2: own venv + zz_reuse_el_venv_readonly.pth (adds house site-packages) + found_sam2_src.pth (sam2 src 2b90b9f). Pattern for new venvs that share torch.
- data: el-fault-detection/data/labeled/{images 582, masks_escdd 583 files, masks_coded}; el_f3/data = symlinks labeled, escdd_masks -> el_f1/data/escdd_masks, unlabeled; splits/{train,val,test}.txt, seed0-2, external_unlabeled.txt.
- b6/b6_root_{0..4}: labeled symlink, splits/{train,val,test}.txt (425/107/107 f0), SPLITS.md5, DATA_MANIFEST.md5; b6/ROOTS.md5, b6_forbidden.txt.
- E1: el_f1/reports/f1/ext117 (images, masks, ignore, stems_eval.txt, stems.txt, manifest.csv); /home/noob/work/ext117 lacks stems_eval.txt. rf: calib/data/rf (images, masks, ignore, stems_eval.txt, rf_context.tsv).
- B6 relayed runs: cv02_noob_el/el_b6/experiments/b6_{SUP,SUPPF}_f{0..4}_s{5,6} (config_used.yaml, checkpoints/{latest,best}.pth, metrics.json, train.log); one run dir 499 MB.
- 12 Nov: DESIGN.md written (238 l.); b6 check paths confirmed: b6_build/check/out_cpu|out_gpu, b6_score/out/<run>.b6.json
