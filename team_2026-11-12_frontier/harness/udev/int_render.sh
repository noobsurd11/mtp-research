#!/bin/bash
# integrator udev: every reviewed card renders to the same config on bench_udev as on the tree it was reviewed on.
# `python -m bench.cards render <card> --seed s --run-name n --data-root r` at the reference archive and at bench_wt_udev,
# md5 of the output compared. One process at a time. Output lines go to stdout (int_check.sh appends them to run.log);
# per-tuple table $IO/check/render/render.tsv (set, tree, card, seed, name, root, md5 ref, md5 new, same).
set -u
IO=/home/noob/work/bench_int_io; O=$IO/check/render; mkdir -p $O; T=$O/render.tsv; : > $T
P=/home/noob/work/el-fault-detection/.venv/bin/python; NEW=/home/noob/work/bench_wt_udev
export CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1
G=/home/noob/work/bench_data/roots; C=/tmp/noob_el/bench_data/roots; U=/home/noob/work/bench_udev/roots
rmd5() { (cd $1 && nice -n 19 $P -m bench.cards render $2 --seed $3 --run-name $4 --data-root $5 2>/dev/null | md5sum | cut -c1-32); }
one() {  # set tree card seed name root
  local a b; a=$(rmd5 $IO/arch_$2 $3 $4 $5 $6); b=$(rmd5 $NEW $3 $4 $5 $6)
  local s=no; [ "$a" = "$b" ] && [ "$a" != d41d8cd98f00b204e9800998ecf8427e ] && s=yes
  echo -e "$1\t$2\t$3\t$4\t$5\t$6\t$a\t$b\t$s" >> $T; }
# wave 1 cards (31c0c36): the 5 cards of bench/methods at 31c0c36, folds 0-4 x seeds 5-9 on the gaint roots; the PF v11
# card also on the two LOSO-2 roots (the udev_loso2 PF lines)
for card in house_r34_unetpp house_r34_unetpp_pf house_r34_unetpp_pf_v11 house_r34_unetpp_v11 upernet_convnext_t_in1k; do
  for k in 0 1 2 3 4; do for s in 5 6 7 8 9; do one W1 31c0c36 bench/methods/$card.yaml $s chk_${card}_f${k}_s$s $G/cv5v2_v11_f$k; done; done; done
for k in 0 1; do for s in 5 6 7 8; do one W1-LOSO 31c0c36 bench/methods/house_r34_unetpp_pf_v11.yaml $s udev_pf_loso_f${k}_s$s $U/cvloso2_v11_f$k; done; done
# wave 2a cards (c57508e): the exact (name, card, seed, root) of the 61 reviewed bq/w2a lines (bq/w2a2 = its last 36)
while IFS='|' read -r name card seed root gate cmd extra; do one W2A c57508e $card $seed $name $root; done < /home/noob/work/bq/w2a/jobs.txt
# tranche 1 rows (52e3f14): bench/methods (gaint roots) and bench/methods_cv02 (cv02 roots), folds 0-4 x seeds 5, 6
for card in dlv3p_r34_pf_v11 unet_r34_pf_v11 pratt_dlv3p_wcec_v11 hanifi_vgg16_unet_pf_v11 ucf_dlv3_r50_pf_v11; do
  for k in 0 1 2 3 4; do for s in 5 6; do
    one R1 52e3f14 bench/methods/$card.yaml $s r1_${card}_f${k}_s$s $G/cv5v2_v11_f$k
    one R1-cv02 52e3f14 bench/methods_cv02/$card.yaml $s r1_${card}_f${k}_s$s $C/cv5v2_v11_f$k; done; done; done
# W1 cards in bench/methods_cv02 (deployed on cv02 since d3a3280; reviewed in rows1 / rows2 trees)
for card in house_r34_unetpp house_r34_unetpp_pf house_r34_unetpp_pf_v11 house_r34_unetpp_v11; do
  for k in 0 1 2 3 4; do for s in 5 6; do one W1-cv02 b12fca8 bench/methods_cv02/$card.yaml $s w1c_${card}_f${k}_s$s $C/cv5v2_v11_f$k; done; done; done
# tranche 2 rows (b12fca8): bench/methods and bench/methods_cv02; skr01 also on the LOSO-2 roots (the udev_loso2 skr01 lines)
for card in segformer_mitb2_pf_v11 hrnet_w18_unetpp_pf_v11 skr01_pf_v11; do
  for k in 0 1 2 3 4; do for s in 5 6; do
    one R2 b12fca8 bench/methods/$card.yaml $s r2_${card}_f${k}_s$s $G/cv5v2_v11_f$k
    one R2-cv02 b12fca8 bench/methods_cv02/$card.yaml $s r2_${card}_f${k}_s$s $C/cv5v2_v11_f$k; done; done; done
for k in 0 1; do for s in 5 6; do one R2-LOSO b12fca8 bench/methods/skr01_pf_v11.yaml $s udev_skr01_loso_f${k}_s$s $U/cvloso2_v11_f$k; done; done
# card files byte-equal to their reviewed tree
nf=0; ns=0
for f in $(cd $NEW && ls bench/methods/*.yaml bench/methods_cv02/*.yaml); do
  for c in b12fca8 c57508e 31c0c36; do if [ -e $IO/arch_$c/$f ]; then nf=$((nf+1)); cmp -s $IO/arch_$c/$f $NEW/$f && ns=$((ns+1)); break; fi; done; done
echo "[$(date '+%F %T')] render: $(awk -F'\t' '{n[$1]++; if ($9=="yes") y[$1]++} END {for (k in n) printf "%s %d of %d; ", k, y[k], n[k]}' $T)total $(awk -F'\t' '$9=="yes"' $T | wc -l) of $(wc -l < $T) equal (empty renders count as not equal); card files byte-equal to their reviewed tree: $ns of $nf; bench/cards.py = c57508e: $(cmp -s $IO/arch_c57508e/bench/cards.py $NEW/bench/cards.py && echo yes || echo no); table $T"
