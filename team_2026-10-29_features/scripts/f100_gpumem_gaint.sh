#!/bin/bash
# GPU memory log for gaint (team-lead rule, 31 Oct 2026): whenever our GPU jobs share the GPU, free memory is logged every 10 s
# for the whole overlap; here from now through CP100 and opening 2. While one of our scoring processes is on the GPU the
# interval is 1 s, so the m0 pass peak in opening 2 (finllm alone) is measured, not assumed.
# Line: "HH:MM:SS free_MiB used_MiB | pid:label:MiB ..." (per-process used memory from nvidia-smi --query-compute-apps).
# Stops 60 s after the opening-2 end line (only lines written after start count) (scoring done / NOT scored / FAIL) or CP_STOP, or after MAXH hours.
# PID in reports/f100/gpumem.pid (stop only by that exact PID); log reports/f100/gpumem.log. Writes nothing else.
cd /home/noob/work/el_f3 || exit 1
L=reports/f100/gpumem.log; LL=reports/f100/launch.log; MAXH=${MAXH:-14}; T0=$(date +%s); END=0; N0=$(wc -l < $LL)
echo $$ > reports/f100/gpumem.pid
echo "# start $(date '+%F %T') pid $$ (10 s; 1 s while a scoring process is on the GPU); cols: time free_MiB used_MiB | pid:label:MiB" >> $L
RX='run_name=[A-Za-z0-9_]+|rescore_label_versions|m0_audit_tau|m0_audit|rescore_logit_adjust|cp_decoy|f2_crackfree_fp|enc_cosine|finllm_chat|d_infer'
while :; do
  g=$(nvidia-smi --query-gpu=memory.free,memory.used --format=csv,noheader,nounits -i 0 | tr -d ' ' | tr ',' ' ')
  a=$(nvidia-smi --query-compute-apps=pid,used_memory --format=csv,noheader,nounits | tr -d ' ' | while IFS=, read -r p m; do
        lab=$(ps -o args= -p "$p" 2>/dev/null | grep -oE "$RX" | head -1); echo -n "$p:${lab:-other}:$m "; done)
  echo "$(date +%T) $g | $a" >> $L
  if [ $END = 0 ] && tail -n +$((N0+1)) $LL | grep -qE "f3 opening2 scoring done|f3 opening2 NOT scored|f3 opening2 .*FAIL|CP_STOP"; then
    END=$(date +%s); echo "# end line seen $(date '+%F %T'); stopping in 60 s" >> $L; fi
  [ $END != 0 ] && [ $(( $(date +%s) - END )) -ge 60 ] && { echo "# stop $(date '+%F %T')" >> $L; rm -f reports/f100/gpumem.pid; exit 0; }
  [ $(( $(date +%s) - T0 )) -ge $(( MAXH * 3600 )) ] && { echo "# stop $(date '+%F %T') (MAXH ${MAXH} h)" >> $L; rm -f reports/f100/gpumem.pid; exit 0; }
  if echo "$a" | grep -qE ':(rescore_label_versions|m0_audit_tau|m0_audit|rescore_logit_adjust|cp_decoy|f2_crackfree_fp|enc_cosine):'; then sleep 1; else sleep 10; fi
done
