#!/bin/bash
# GPU memory log on gaint for PF2 (team-lead standing rule: whenever our GPU jobs share the GPU, free memory every 10 s for the
# whole overlap). Runs from the PF2 smoke through the PF2 scoring. 1 s samples while a scoring process is on the GPU or while
# /home/noob/work/gpu_gate/FAST exists (smokes: peaks are measured, not assumed); 10 s otherwise.
# Line: "HH:MM:SS free_MiB used_MiB | pid:label:MiB ..." (per-process used memory, nvidia-smi --query-compute-apps).
# Stops 60 s after a PF2 end line in reports/pf2/launch.log (only lines written after start), or STOP file, or MAXH hours.
# PID in reports/pf2/gpumem.pid (stop only by that exact PID). Writes nothing else.
cd /home/noob/work/el_f3 || exit 1
mkdir -p reports/pf2; L=reports/pf2/gpumem.log; LL=reports/pf2/launch.log; touch $LL
MAXH=${MAXH:-48}; T0=$(date +%s); END=0; N0=$(wc -l < $LL); GG=/home/noob/work/gpu_gate
echo $$ > reports/pf2/gpumem.pid
echo "# start $(date '+%F %T') pid $$ (10 s; 1 s while scoring or FAST); cols: time free_MiB used_MiB | pid:label:MiB" >> $L
RX='run_name=[A-Za-z0-9_]+|rescore_label_versions|m0_audit_tau|m0_audit|rescore_logit_adjust|cp_decoy|f2_crackfree_fp|enc_cosine|finllm_chat|d_infer'
SC=':(rescore_label_versions|m0_audit_tau|m0_audit|rescore_logit_adjust|cp_decoy|f2_crackfree_fp|enc_cosine):'
while :; do
  g=$(nvidia-smi --query-gpu=memory.free,memory.used --format=csv,noheader,nounits -i 0 | tr -d ' ' | tr ',' ' ')
  a=$(nvidia-smi --query-compute-apps=pid,used_memory --format=csv,noheader,nounits | tr -d ' ' | while IFS=, read -r p m; do
        lab=$(ps -o args= -p "$p" 2>/dev/null | grep -oE "$RX" | head -1); echo -n "$p:${lab:-other}:$m "; done)
  echo "$(date +%T) $g | $a" >> $L
  if [ $END = 0 ] && tail -n +$((N0+1)) $LL | grep -qE "pf2 scoring done|pf2 NOT scored|pf2 post FAIL"; then
    END=$(date +%s); echo "# end line seen $(date '+%F %T'); stopping in 60 s" >> $L; fi
  [ $END != 0 ] && [ $(( $(date +%s) - END )) -ge 60 ] && { echo "# stop $(date '+%F %T')" >> $L; rm -f reports/pf2/gpumem.pid; exit 0; }
  [ -e reports/pf2/GPUMEM_STOP ] && { echo "# stop $(date '+%F %T') (GPUMEM_STOP)" >> $L; rm -f reports/pf2/gpumem.pid reports/pf2/GPUMEM_STOP; exit 0; }
  [ $(( $(date +%s) - T0 )) -ge $(( MAXH * 3600 )) ] && { echo "# stop $(date '+%F %T') (MAXH ${MAXH} h)" >> $L; rm -f reports/pf2/gpumem.pid; exit 0; }
  if [ -e $GG/FAST ] || echo "$a" | grep -qE "$SC"; then sleep 1; else sleep 10; fi
done
