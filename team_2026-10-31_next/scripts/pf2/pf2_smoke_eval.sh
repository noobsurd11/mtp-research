#!/bin/bash
# Evaluate the PF2 smoke (reports/pf2/smoke, el_f3 e544133) into reports/pf2/smoke/GATES.txt. CPU only.
set -u
cd /home/noob/work/el_f3
P=/home/noob/work/el-fault-detection/.venv/bin/python
O=reports/pf2/smoke; G=$O/GATES.txt; F=reports/f100/smoke; E=experiments
S0=/home/noob/work/el_f1/reports/f1/smoke_v1/mim_step0.pth; R0=reports/pf2/cpucheck/rn50_imagenet_step0.pth
TM=/home/noob/work/cv02_noob_el/el_mt/experiments
ext(){ grep -E "src.trainers.trainer — (step|val @)" $1 | sed -E "s/^[0-9-]+ [0-9:,]+ //; s/ +steps_per_sec=[0-9.]+//"; }
pfl(){ grep -h "PF encoder lr" $1 | sed -E "s/^[0-9-]+ [0-9:,]+ //"; }
same(){ cmp -s $1 $2 && echo "IDENTICAL ($(wc -l < $1) lines)" || echo "DIFFER ($(wc -l < $1) vs $(wc -l < $2) lines; first diff: $(diff $1 $2 | head -3 | tr '\n' ' ' | cut -c1-200))"; }
for n in pf2s_sup_s0 pf2s_suppf_s0 pf2s_rn50pf_s0; do ext $O/$n.stdout | grep -v "val @" > $O/$n.steplines; pfl $O/$n.stdout > $O/$n.pflines; done
head -20 $F/b1_nosw_voff.steplines > $O/ref_b1_1k.steplines; head -20 $F/c1_suppf.steplines > $O/ref_c1_1k.steplines
pfl $F/c1_suppf.stdout | awk '{for(i=1;i<=NF;i++) if($i=="step"){s=$(i+1)}} s+0<=1000' > $O/ref_c1_1k.pflines
ext $E/f3_SUP_100pct_s0.stdout | grep -v "val @" | head -20 > $O/ref_f3sup_1k.steplines
ext $E/f3_SUPPF_100pct_s0.stdout | grep -v "val @" | head -20 > $O/ref_f3suppf_1k.steplines
pfl $E/f3_SUPPF_100pct_s0.stdout | awk '{for(i=1;i<=NF;i++) if($i=="step"){s=$(i+1)}} s+0<=1000' > $O/ref_f3suppf_1k.pflines
cfgd(){ diff <(grep -v -E "^run_name:|^  experiments_dir:" $1) <(grep -v -E "^run_name:|^  experiments_dir:" $2) | grep -E "^[<>]" | tr '\n' ' '; }
{
echo "== PF2 smoke, code $(cat REVISION), $(date)"
sed 's/^/   /' $O/status.txt
echo "-- config_used.yaml vs protocol_100's arm configs (run_name and experiments_dir ignored; expected: none, or encoder_name only)"
echo "SUP100-g   pf2s_sup_s0 vs f3_SUP_100pct_s0:     [$(cfgd $O/pf2s_sup_s0/config_used.yaml $E/f3_SUP_100pct_s0/config_used.yaml)]"
echo "SUP100-PF  pf2s_suppf_s0 vs f3_SUPPF_100pct_s0: [$(cfgd $O/pf2s_suppf_s0/config_used.yaml $E/f3_SUPPF_100pct_s0/config_used.yaml)]"
echo "RN50-PF    pf2s_rn50pf_s0 vs f3_SUPPF_100pct_s0: [$(cfgd $O/pf2s_rn50pf_s0/config_used.yaml $E/f3_SUPPF_100pct_s0/config_used.yaml)]"
echo "RN50-PF    pf2s_rn50pf_s0 vs Track M m_r3_rn50_s1 (house RN50): [$(cfgd $O/pf2s_rn50pf_s0/config_used.yaml $TM/m_r3_rn50_s1/config_used.yaml)]"
echo "-- identity after the 30 Oct reboot (step lines, timestamps and speed stripped; protocol_100 smokes, same commit / opts / seed)"
echo "GATE 1 SUP100-g  pf2s_sup_s0 vs the real run f3_SUP_100pct_s0.stdout, 1,000 steps: $(same $O/pf2s_sup_s0.steplines $O/ref_f3sup_1k.steplines)"
echo "SUP100-PF pf2s_suppf_s0 vs the real run f3_SUPPF_100pct_s0.stdout, 1,000 steps: $(same $O/pf2s_suppf_s0.steplines $O/ref_f3suppf_1k.steplines); PF lr lines: $(same $O/pf2s_suppf_s0.pflines $O/ref_f3suppf_1k.pflines)"
echo "SUP100-g  pf2s_sup_s0 vs b1_nosw_voff, 1,000 steps: $(same $O/pf2s_sup_s0.steplines $O/ref_b1_1k.steplines)"
echo "SUP100-PF pf2s_suppf_s0 vs c1_suppf, 1,000 steps: $(same $O/pf2s_suppf_s0.steplines $O/ref_c1_1k.steplines)"
echo "SUP100-PF PF encoder lr lines vs c1_suppf, 1,000 steps: $(same $O/pf2s_suppf_s0.pflines $O/ref_c1_1k.pflines)"
echo "-- RN50-PF lines"
echo "params: $(grep -m1 -oE 'Model smp_unetpp: [0-9,]+ parameters' $O/pf2s_rn50pf_s0.stdout) (Track M RN50: 48,982,808)"
echo "step 1000 / 2000: $(grep -E 'step (1000|2000)/20000' $O/pf2s_rn50pf_s0.steplines | cut -c1-200 | tr '\n' ' ')"
echo "4k: $(ext $O/pf2s_rn50pf_s0_4k.stdout | grep -E 'step (2050|4000)/20000' | cut -c1-200 | tr '\n' ' ')"
echo "PF encoder lr at 1000/1500/2000: $(grep -E 'step (1000|1500|2000)$' $O/pf2s_rn50pf_s0.pflines | sed -E 's/.*lr=//; s/ .*//' | tr '\n' ' ')"
echo "Tracebacks: $(cat $O/*.stdout | grep -c Traceback)"
echo "-- PF cosine to ImageNet (per-stage mean cosine / norm ratio); protocol_100 gate 5 / G5: layer3 and layer4 >= 0.5 at 2k, >= 0.8 at 4k"
OMP_NUM_THREADS=4 CUDA_VISIBLE_DEVICES="" $P reports/enc_cosine.py --out $O/enc_cosine.json \
  --pair "RN50-PF s0 2k vs ImageNet RN50" $R0 $O/pf2s_rn50pf_s0/checkpoints/latest_2k.pth \
  --pair "RN50-PF s0 4k vs ImageNet RN50" $R0 $O/pf2s_rn50pf_s0/checkpoints/latest.pth \
  --pair "house RN50 m_r3_rn50_s1 20k vs ImageNet RN50 (ref)" $R0 $TM/m_r3_rn50_s1/checkpoints/latest.pth 2>&1 | grep -v Warning
echo "protocol_100 SUP100-PF s0 (c1): 2k layer3/4 0.996/0.997, 4k 0.975/0.985"
echo "-- memory (gpumem.log, 1 s samples during the smoke; per-process nvidia-smi MiB): max per label"
awk '/^#/ {next} {for(i=5;i<=NF;i++){split($i,a,":"); k=a[2]; if(k=="other"){k="other_pid" a[1]}; if(a[3]+0>m[k]) m[k]=a[3]+0}; if(mf==""||$2+0<mf) mf=$2+0} END{for(k in m) print "  " k, m[k]; print "  min free", mf}' \
  <(awk -v t0="$(head -1 $O/status.txt | grep -oE '^\[[0-9:]+' | tr -d '[')" -v t1="$(grep ALLDONE $O/status.txt | grep -oE '^\[[0-9:]+' | tr -d '[')" '/^#/ {next} $1>=t0 && $1<=t1' reports/pf2/gpumem.log) | sort
echo "-- speed: instantaneous steps/s from step-line timestamps (time of line: rate over the previous 50 steps)"
rate(){ grep -E "src.trainers.trainer — step [0-9]+/20000" $1 | awk '{split($2,t,/[:,]/); s=t[1]*3600+t[2]*60+t[3]; match($0,/step [0-9]+/); n=substr($0,RSTART+5,RLENGTH-5)+0; if(ps!="" && s>ps) printf "%s %.2f; ", substr($2,1,8), (n-pn)/(s-ps); ps=s; pn=n}'; }
for n in pf2s_rn50pf_s0 pf2s_sup_s0 pf2s_suppf_s0 pf2s_rn50pf_s0_4k; do echo "$n: $(rate $O/$n.stdout | cut -c1-1500)"; done
echo "-- scoring passes on the RN50 2k copy (val only): logs"
tail -3 $O/m0val.log; tail -4 $O/la_val.log
} > $G 2>&1
echo "GATES written: $G"
