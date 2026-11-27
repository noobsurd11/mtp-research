#!/usr/bin/env bash
# Lead, 13 Nov 2026. Waits for the W1-G chain (training, then held-out dumps) to end, then runs the four
# wave 1 read tools of builder x3 (bench_x3 69a60f5) on the 10 out-of-fold dumps. CPU only, open folds only
# (the tools refuse sealed sets). Outputs are a first read from the pre-review tool version; the table read
# is redone from the merged, reviewed worktree. Stop the wait: touch /home/noob/work/bench_reads/STOP
set -u
Q=/home/noob/work/bq/w1g
R=/home/noob/work/bench_reads/w1g
W=/home/noob/work/bench_wt_x3
P=/home/noob/work/el-fault-detection/.venv/bin/python
L=/home/noob/work/bench_reads/w1g_read.log
D=/home/noob/work/bench_dumps/w1g/elbench1/house_r34_unetpp_pf_v11
lg(){ echo "[$(date '+%F %T')] $*" >> "$L"; }
mkdir -p "$R"
lg "waiter start pid $$; tools $(git -C $W rev-parse --short HEAD)"
while :; do
  grep -qE "chain done|dumps not started" "$Q/chain.log" 2>/dev/null && break
  [ -e /home/noob/work/bench_reads/STOP ] && { lg "STOP file; exit"; exit 0; }
  sleep 120
done
n=$(ls -d "$D"/w1g_pf_v11_f*_s*/cv5v2_f*/manifest.json 2>/dev/null | wc -l)
lg "chain ended: $(tail -1 "$Q/chain.log" | cut -c1-200); manifests $n"
[ "$n" = 10 ] || { lg "not 10 manifests; no read"; exit 1; }
cd "$W" || exit 1
[ "$(git rev-parse --short HEAD)" = 69a60f5 ] || { lg "worktree not at 69a60f5; no read"; exit 1; }
[ -z "$(git status --porcelain --untracked-files=no)" ] || { lg "worktree has tracked changes; no read"; exit 1; }
export CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
G=(--arm "PF=$D:w1g_pf_v11_f[0-4]_s[56]" --labels v11 --workers 8 --cache "$R")
run(){ # name script extra...
  local name=$1 script=$2; shift 2
  [ -e "$R/$name" ] && { lg "$name: output dir exists, skipped"; return 0; }
  lg "$name start"
  nice -n 19 "$P" "scripts/$script" "${G[@]}" "$@" --out "$R/$name" > "$R/$name.stdout" 2>&1
  local rc=$?
  lg "$name rc=$rc; Traceback lines $(grep -c Traceback "$R/$name.stdout"); files $(ls "$R/$name" 2>/dev/null | tr '\n' ' ')"
}
run read bench_read_w1.py --baseline PF
run src_calib bench_src_calib.py
run dti bench_dti.py
run d0 bench_d0.py
lg "W1G READ ALL DONE"
