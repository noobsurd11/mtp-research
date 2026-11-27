#!/bin/bash
# push changed/new files of the local x2 mirror (vs its base commit) into /home/noob/work/bench_wt_x2 (md5-checked).
cd /home/yugma/mtp/research/team_2026-11-12_frontier/harness/x2_src || exit 1
S=/home/yugma/mtp/research/team_2026-11-12_frontier/scripts
for f in $(git status --porcelain --untracked-files=all | awk '{print $2}'); do
  [ -f "$f" ] && $S/gput.sh "$f" "/home/noob/work/bench_wt_x2/$f" | sed 's/^/  /'
done
