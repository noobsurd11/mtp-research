#!/bin/bash
# runner (1 Nov 2026): jobs for the HC + A8 queue -> /home/noob/work/nq/nq_jobs.txt, lines "name|seed|arm|opts", in ORDER.
# HC (protocol_HC §3, §9.3): the pf2_SUPPF_100pct_sK opts of el_f3/reports/pf2/pf2_jobs.txt (md5 210d0d6f), run_name replaced,
#   + data.synth_halfcut.p=0.35 data.synth_halfcut.pool=data/splits/synth_halfcut_pool_ap.tsv; names hc_HC_100pct_s5..9.
# A8 / A8c (protocol_A8screen §9, idea08_runspec §2c): the opts of runner's smoke_a8.sh (3171fef8) without the smoke-only
#   training.checkpoint_every=300, + data.root=/home/noob/work/a8_root (coach, protocol_A8screen v1.1 §10: test.txt = val.txt, so the
#   trainer's unconditional end-of-run TEST reads no test cell); seeds 0, 1; names f8_A8_4k_s{0,1} / f8_A8c_4k_s{0,1}.
# ORDER (env, space-separated names) = the dispatch order (coach's plan); every name must be one of the 9.
set -eu
J=/home/noob/work/el_f3/reports/pf2/pf2_jobs.txt; O=/home/noob/work/nq; mkdir -p $O
[ "$(md5sum < $J | cut -c1-32)" = 210d0d6fcc54c3effcc36893e0d51ad5 ]
(cd /home/noob/work/a8_root && md5sum -c --quiet SPLITS.md5) && cmp -s /home/noob/work/a8_root/splits/test.txt /home/noob/work/a8_root/splits/val.txt
declare -A L
for k in 5 6 7 8 9; do
  base=$(grep "^pf2_SUPPF_100pct_s$k|" $J | cut -d'|' -f4 | sed "s/ run_name=pf2_SUPPF_100pct_s$k\$//"); [ -n "$base" ]
  L[hc_HC_100pct_s$k]="hc_HC_100pct_s$k|$k|HC|$base data.synth_halfcut.p=0.35 data.synth_halfcut.pool=data/splits/synth_halfcut_pool_ap.tsv run_name=hc_HC_100pct_s$k"
done
B="data.labeled_fraction=1.0 data.split_seed=0 training.labeled_batch_size=8 data.mask_subdir=labeled/masks_escdd data.augmentation=labelsafe loss.supervised=ce_dice"
S4="training.total_steps=4000 training.warmup_steps=200 training.encoder_pf.freeze=200 training.encoder_pf.ramp=200 training.encoder_pf.lr_mult=0.1 training.encoder_pf.wd=0 training.val_every=4000"
A8="model.name=hrstem_unetpp model.backbone=convnext_tiny.dinov3_lvd1689m model.backbone_weights=/home/noob/work/weights/dinov3_convnext_tiny_lvd1689m_timm.safetensors model.backbone_weights_format=timm model.backbone_drop_path=0.0"
A8C="model.name=hrstem_unetpp model.backbone=convnext_tiny model.backbone_weights=/home/noob/.cache/torch/hub/checkpoints/convnext_tiny-983f1562.pth model.backbone_weights_format=torchvision_convnext model.backbone_drop_path=0.0"
for k in 0 1; do
  L[f8_A8_4k_s$k]="f8_A8_4k_s$k|$k|A8|seed=$k $B $S4 $A8 data.root=/home/noob/work/a8_root run_name=f8_A8_4k_s$k"
  L[f8_A8c_4k_s$k]="f8_A8c_4k_s$k|$k|A8c|seed=$k $B $S4 $A8C data.root=/home/noob/work/a8_root run_name=f8_A8c_4k_s$k"
done
ORDER=${ORDER:?space-separated job names}
[ "$(echo $ORDER | wc -w)" = 9 ] && [ "$(echo $ORDER | tr ' ' '\n' | sort -u | wc -l)" = 9 ]
for n in $ORDER; do [ -n "${L[$n]:-}" ]; echo "${L[$n]}"; done > $O/nq_jobs.txt
md5sum $O/nq_jobs.txt
