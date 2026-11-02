#!/bin/bash
# runner (2 Nov 2026): pre-freeze self-tests of the SKR2 + HC2 opening set in /home/noob/work/s2q/open/ (coach: CPU, CUDA hidden, nice 19,
# <= 8 threads). Reads only already-opened comparator / reference files (PF2 SUPPF, HC, THIN, calib pre-check records); prints only the
# self-tests' own flags. Not part of the frozen set. Outputs + MD5.txt in /home/noob/work/s2q/pre_freeze/.
#   e1_selftest       s2_e1_coprim --selftest (SUPPF 0.4202 / 0.3811 / 0.2371, any-hit per seed, HC per run = HC e1_coprim.json)
#   guards_selftest   s2_guards --selftest (judge's HC / SKR w1.0 / CLD deltas, SUPPF 3,931, G3 wiring)
#   f51_selftest      s2_f51 --selftest (a8's own + verdict wiring)
#   shv1_selftest     s2_shv1_read --selftest (calib pre-check records + HC opening SHV1 records)
#   b5w_*_s5val       el_metrics_w records of pf2_SUPPF_100pct_s5 val from PF2's b5_work dump (self-check vs PF2 m0, tol exact), then
#                     s2_b5w_check records: equal to PF2's frozen 6e73ff11 record on -4..+12 (+0.75)
set -u
H=/home/noob/work/s2q/open; O=/home/noob/work/s2q/pre_freeze; P=/home/noob/work/el-fault-detection/.venv/bin/python
PF=/home/noob/work/el_f3/reports/pf2/post; HCP=/home/noob/work/el_hc/reports/hc/post; THP=/home/noob/work/el_thin/reports/thin/post
CAL=/home/noob/work/calib/out; PF2B5=/home/noob/work/el_f3/reports/pf2/b5_work
[ ! -e $O ] || { echo "$O exists"; exit 2; }; mkdir -p $O
CPU=(env CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=8 MKL_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8 HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 nice -n 19)
CPU1=(env CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 nice -n 19)
r(){ local n=$1 rc; shift; "$@" > $O/$n.txt 2>&1; rc=$?; echo "$n rc=$rc" >> $O/rc.txt; }
r e1_selftest "${CPU[@]}" $P $H/s2_e1_coprim.py --selftest --pf2-m0 $PF/m0 --hc-m0 $HCP/m0 --hc-json $HCP/e1_coprim.json --trackm $H/trackM --thin $H/thin/thin_e1_relf1.py
r guards_selftest "${CPU[@]}" $P $H/s2_guards.py --selftest --trackm $H/trackM --pf2-m0 $PF/m0 --hc-m0 $HCP/m0 --thin-m0 $THP/m0
r f51_selftest "${CPU[@]}" $P $H/s2_f51.py --selftest --a8 $H/found/a8_screen_score.py --el-metrics $H/calib_syn
r shv1_selftest "${CPU[@]}" $P -B $H/s2_shv1_read.py --selftest --el-metrics $H/calib_syn --st-val $CAL/rec --st-syn $CAL/rec_shv1 --st-hc $HCP/shv1/rec
r b5w_records_s5val "${CPU1[@]}" $P $H/calib_w/el_metrics_w.py records --dump $PF2B5/dump/pf2_SUPPF_100pct_s5.val.npz --set val --code /home/noob/work/el_f3 \
  --out $O/pf2_SUPPF_100pct_s5.val.wide.json --m0 $PF/m0/pf2_SUPPF_100pct_s5.json --m0-set val --tol-profile exact --procs 8
r b5w_subgrid_s5val "${CPU[@]}" $P $H/s2_b5w_check.py records --pair $O/pf2_SUPPF_100pct_s5.val.wide.json $PF/b5/rec/pf2_SUPPF_100pct_s5.val.json
(cd $O && md5sum *.txt *.json > MD5.txt)
cat $O/rc.txt
