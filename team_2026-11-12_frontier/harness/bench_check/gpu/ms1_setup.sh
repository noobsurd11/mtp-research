#!/bin/bash
# Milestone 1, step 1: the 1,000-step smoke of upernet_convnext_t_in1k on b6_root_0 through bench_q (MAXC 1), to measure the
# peak for the card's gate. Run only on the lead's word. Creates /home/noob/work/bq/ms1 (refuses if it exists) and tmux
# bench_q_ms1 with windows gm (1 s gpumem log), guard (auto-stop), q (queue). The smoke exits rc 3 by design (--exit_after_step).
# Gate 16,000 MiB for the smoke (peak unknown; A8 hrstem ConvNeXt-T measured 9,254). After it: peak = max per-process MiB of
# the smoke in gpumem.log; card memory.peak_mib / gate_mib = peak / peak + 2048 (new card version), then the 20k run job.
set -u
Q=/home/noob/work/bq/ms1; R=/home/noob/work/el_bench; S="=bench_q_ms1"
[ ! -e $Q ] || { echo "$Q exists"; exit 1; }
tmux has-session -t "$S" 2>/dev/null && { echo "tmux $S exists"; exit 1; }
mkdir -p $Q; echo 1 > $Q/MAXC
echo "smoke_upernet_cnxt_f0|bench/methods/upernet_convnext_t_in1k.yaml|5|/home/noob/work/b6/b6_root_0|16000||--exit_after_step 1000" > $Q/jobs.txt
JM=$(md5sum < $Q/jobs.txt | cut -c1-32); DEP=$(git -C $R rev-parse HEAD)
tmux new-session -d -s bench_q_ms1 -n gm "Q=$Q nice -n 19 bash $R/bench/q/bench_gpumem.sh"
tmux new-window -t "$S:" -n guard "Q=$Q LIB=$R/bench/q/bench_lib.sh bash $R/bench/q/bench_guard.sh"
sleep 3
tmux new-window -t "$S:" -n q "CUDA_VISIBLE_DEVICES=0 Q=$Q JOBS_MD5=$JM DEPLOY=$DEP REPO=$R bash $R/bench/q/bench_q.sh"
sleep 5; echo "gpumem $(cat $Q/gpumem.pid) guard $(cat $Q/guard.pid) queue $(cat $Q/queue.pid 2>/dev/null)"; tail -3 $Q/launch.log
