#!/bin/bash
# coach (1 Nov, respawned): A8 screen verification ON GAINT CPU, reading a8_score/v1 in place (read-only) after md5sum -c of its
# MANIFEST and the dump md5 list. Own code: coach_a8.py 2da944cd (GO-rule terms, own AP / OP / FA / module bootstrap) and
# coach_a8_extra.py (validity vs the weights files, val dump integrity, stems). nice 19, 8 threads, CUDA hidden. No test, no E1, no stdout.
set -u
B=/home/noob/work/coach_v/bin; OUT=/home/noob/work/coach_v/a8/out; mkdir -p $OUT
V=/home/noob/work/a8_score/v1; C=/home/noob/work/el_f8; RF=/home/noob/work/calib/data/rf; RFS=/home/noob/work/found/t9/rf_sets.tsv
PY=/home/noob/work/el-fault-detection/.venv/bin/python
export CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=8 MKL_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8
grep -qE 'a8 scoring done: rc=0$' $V/a8_score.log || { echo "A8 scoring not done rc=0: abort"; exit 1; }
{ (cd $V/out && md5sum -c --quiet MANIFEST.md5 && echo "a8 out md5sum -c OK $(md5sum < MANIFEST.md5 | cut -c1-8) $(wc -l < MANIFEST.md5) files")
  (cd $V/work/dump && md5sum -c --quiet $V/out/dump_md5_on_gaint.txt && echo "dumps md5sum -c OK (8)")
  (cd $V/work/init && md5sum -c --quiet $V/out/init_md5_on_gaint.txt && echo "init refs md5sum -c OK (4)")
  echo "coach code: $(cd $B && md5sum coach_a8.py coach_a8_extra.py | cut -c1-8 | tr '\n' ' ')"
  echo "rf_sets $(md5sum < $RFS | cut -c1-8); a8_root test.txt $(md5sum < /home/noob/work/a8_root/splits/test.txt | cut -c1-8) val.txt $(md5sum < /home/noob/work/a8_root/splits/val.txt | cut -c1-8) train.txt $(md5sum < /home/noob/work/a8_root/splits/train.txt | cut -c1-8)"
  echo "el_f8 HEAD $(cd $C && git rev-parse --short HEAD) tracked-modified $(cd $C && git status --short --untracked-files=no | wc -l)"
  grep -E 'f8_A8c?_4k_s[01]( |$)' /home/noob/work/nq/launch.log | grep -E 'trained|config OK|CONFIG FAIL|HOLD'
  for r in f8_A8c_4k_s0 f8_A8_4k_s1 f8_A8c_4k_s1; do echo "== config diff f8_A8_4k_s0 vs $r"; diff $C/experiments/f8_A8_4k_s0/config_used.yaml $C/experiments/$r/config_used.yaml; done
  for r in f8_A8_4k_s0 f8_A8c_4k_s0; do echo "== $r data / schedule keys"; grep -E '^\s*(root|total_steps|warmup_steps|val_every|seed|freeze_steps|ramp_steps|lr_mult|backbone[a-z_]*|name):' $C/experiments/$r/config_used.yaml | tr -s ' ' | tr '\n' ' '; echo; done
} > $OUT/integrity.txt 2>&1
nice -n 19 $PY -I $B/coach_a8.py $V $RF $RFS $C > $OUT/coach_a8.txt 2>&1; echo "coach_a8 rc=$?" >> $OUT/integrity.txt
nice -n 19 $PY -I $B/coach_a8_extra.py $V $C $RF $RFS /home/noob/work/weights/dinov3_convnext_tiny_lvd1689m_timm.safetensors \
  /home/noob/.cache/torch/hub/checkpoints/convnext_tiny-983f1562.pth > $OUT/coach_a8_extra.txt 2>&1; echo "coach_a8_extra rc=$?" >> $OUT/integrity.txt
echo "coach a8 verify done $(date '+%H:%M:%S')" >> $OUT/integrity.txt
(cd $OUT && md5sum integrity.txt coach_a8.txt coach_a8_extra.txt > MD5)
