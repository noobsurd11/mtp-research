#!/bin/bash
# c3base fix round 1: dry tests of the s6 launch pre-checks (F8.1 disk, F8.2 cross-machine). READ ONLY on both machines:
# every arm step is replaced by echo; the only write is a temp dir (mktemp) on gaint, removed at the end. Usage (G): bash c3_f82_dry.sh
set -u
pre_gaint() { local G=$1; test ! -e $G/queue.pid && test ! -e $G/gpumem.pid && test ! -e $G/pids && test ! -s $G/launch.log && ! tmux has-session -t "=bench_q_c3base" 2>/dev/null; }
cvchk() { ssh -n -a -o BatchMode=yes -o ConnectTimeout=10 ${2:-} cv02@10.8.1.106 "Q=$1; "'test ! -e $Q/queue.pid && test ! -e $Q/gpumem.pid && test ! -e $Q/pids && test ! -s $Q/launch.log && ! tmux has-session -t "=bench_q_c3base" 2>/dev/null && echo CV02_C3BASE_NEVER_ARMED' 2>/dev/null | grep -qx CV02_C3BASE_NEVER_ARMED; }
arm_cv02() { if pre_gaint $1; then ssh -n -a -o BatchMode=yes cv02@10.8.1.106 'a=$(df --output=avail -BG /tmp | tail -1 | tr -dc 0-9); [ "$a" -ge '$2' ] || { echo "REFUSED: cv02 /tmp free ${a} GB < '$2'"; exit 1; }; echo WOULD_ARM_CV02 free $a'; else echo "REFUSED: gaint bq/c3base armed or used (F8.2)"; fi; }
fb() { if cvchk "$@"; then echo WOULD_RUN_LAUNCH_SH; else echo "REFUSED: cv02 c3base armed or used, or cv02 unreachable (F8.2)"; fi; }
T=$(mktemp -d); touch $T/queue.pid
echo "T1 cv02 arm, real gaint dir, 108:  $(arm_cv02 /home/noob/work/bq/c3base 108)"
echo "T2 cv02 arm, real gaint dir, 80:   $(arm_cv02 /home/noob/work/bq/c3base 80)"
echo "T3 cv02 arm, gaint dir armed:      $(arm_cv02 $T 80)"
echo "T4 fallback, real cv02 dir:        $(fb /tmp/noob_el/bench_q/c3base)"
echo "T5 fallback, used cv02 dir:        $(fb /tmp/noob_el/bench_q/c3base_smoke)"
echo "T6 fallback, cv02 unreachable:     $(fb /tmp/noob_el/bench_q/c3base '-p 1')"
rm -r $T
echo "gaint Q: $(ls /home/noob/work/bq/c3base | tr '\n' ' ')| cv02 Q: $(ssh -n -a -o BatchMode=yes cv02@10.8.1.106 'ls /tmp/noob_el/bench_q/c3base' | tr '\n' ' ')| c3base sessions gaint $(tmux ls 2>/dev/null | grep -c c3base) cv02 $(ssh -n -a -o BatchMode=yes cv02@10.8.1.106 'tmux ls 2>/dev/null | grep -c c3base')"
