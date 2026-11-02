#!/bin/bash
# SKR2 + HC2 opening trigger (protocol_SKR2_HC2 v1.0.1 §6; HC2 under v1.1). DRAFT (runner's helper, 2 Nov 2026) for coach's FREEZE.
# From hc_postwatch.sh (e968f7b4, frozen HC trigger): paths nq -> s2q; 5 HC runs -> the 10 runs of s2_settings.sh; both worktrees
# checked; comparator MANIFESTs PF2 + HC (+ THIN: reference rows); every check is its own statement with '|| refuse' (no && chain).
# Lives in /home/noob/work/s2q/open/. Run in tmux by runner AFTER coach's FROZEN.md5 exists there.  Usage: GS=<MiB, >= 9900> bash s2_postwatch.sh
# Arming (refuses, exit 2, with ONE non-end line "s2 opening trigger REFUSED: ..." in s2q/post.log; never an s2q end line, so
# s2q_gpumem keeps logging the training lanes):
#   settings complete (settings_check: no TBD); FROZEN.md5 lists every REQ file and md5sum -c passes; s2_copies.md5 passes; GS >= 9,900;
#   per arm: worktree HEAD = DEPLOY file = deploy commit, 0 tracked changes, REVISION written if absent (untracked, as el_f3 / el_thin /
#   el_hc; m0_audit records it as code_revision) else = deploy; comparator / reference MANIFESTs (PF2 3827f7c0, HC d5c39e0d, THIN
#   5d3f5b31) have the expected md5 and md5sum -c passes; s2q/post/ and s2q/post_work/ absent; no other s2_postwatch alive.
# Fires s2_post.sh when s2q/launch.log shows "trained RUN rc=0" AND "config OK RUN vs" for all 10 runs (FROZEN re-checked first).
# s2_post.sh writes the ONE end line "[<date>] s2q scoring done: post rc=N".
# Failure (a run trained rc != 0, a "CONFIG FAIL RUN:" line, not all 10 within MAXH h, or FROZEN changed): one line
# "s2 trigger: FAIL seen (...); no scoring; end line deferred while s2q training processes are alive", then, once no PID in
# s2q/pids/*.pid is alive (2 polls 60 s apart), the end line "[<date>] s2q NOT scored (FAIL): <reason>" (s2q_gpumem stops 60 s later).
# Poll 120 s. PID in s2q/s2_postwatch.pid.
set -u
. /home/noob/work/s2q/open/s2_settings.sh || { echo "s2_postwatch: cannot source s2_settings.sh" >&2; exit 2; }
H=$OPEN; MAXH=${MAXH:-96}; PW=$S2/s2_postwatch.pid
ALL="$SKR_RUNS $HC2_RUNS"
refuse(){ echo "s2_postwatch refused: $*" >&2; echo "[$(date)] s2 opening trigger REFUSED: $*" >> $NL; exit 2; }
frozen_ok(){
  local f; [ -s $H/FROZEN.md5 ] || return 1
  for f in $REQ; do grep -qE "^[0-9a-f]{32}  (\./)?$f\$" $H/FROZEN.md5 || return 1; done
  (cd $H && md5sum -c --quiet FROZEN.md5) > /dev/null 2>&1 || return 1
  (cd $H && md5sum -c --quiet s2_copies.md5) > /dev/null 2>&1 || return 1
}
alive(){ local n=0 f; for f in $S2/pids/*.pid; do [ -e "$f" ] || continue; kill -0 "$(cat $f)" 2>/dev/null && n=$((n + 1)); done; echo $n; }
endfail(){
  echo "[$(date)] s2 trigger: FAIL seen ($1); no scoring; end line deferred while s2q training processes are alive" >> $NL
  local quiet=0; while [ $quiet -lt 2 ]; do if [ "$(alive)" = 0 ]; then quiet=$((quiet + 1)); else quiet=0; fi; sleep 60; done
  echo "[$(date)] s2q NOT scored (FAIL): $1" >> $NL; rm -f $PW; exit 1; }
man_ok(){ local d=$1 m=$2; [ "$(md5sum < $d/MANIFEST.md5 | cut -c1-32)" = $m ] || return 1; (cd $d && md5sum -c --quiet MANIFEST.md5) > /dev/null 2>&1; }

# ---- arming checks ----
m=$(settings_check) || refuse "$m"
GS=${GS:-}; [ "$GS" -ge 9900 ] 2>/dev/null || refuse "GS '$GS' < 9900 (scoring gate >= 9,900 beside training, as HC)"
frozen_ok || refuse "coach's $H/FROZEN.md5 missing, not listing every scorer file, or md5sum -c failed (or s2_copies.md5 failed)"
for a in SKR01 HC2; do
  wt=$(wt_of $a); dep=$(dep_of $a); case $a in SKR01) df=$SKR_DEPLOY_FILE;; HC2) df=$HC2_DEPLOY_FILE;; esac
  [ "$(git -C $wt rev-parse --short=7 HEAD)" = $dep ] || refuse "$a: $wt HEAD != $dep"
  [ "$(cat $df 2>/dev/null)" = $dep ] || refuse "$a: $df != $dep"
  [ -z "$(git -C $wt status --short --untracked-files=no)" ] || refuse "$a: tracked changes in $wt"
  [ -e $wt/REVISION ] || echo $dep > $wt/REVISION
  [ "$(cat $wt/REVISION)" = $dep ] || refuse "$a: $wt/REVISION != $dep"
done
man_ok $PF $MAN_PF2 || refuse "PF2 comparator MANIFEST (expected $MAN_PF2) check failed"
man_ok $HCP $MAN_HC || refuse "HC opening MANIFEST (expected $MAN_HC) check failed"
man_ok $THP $MAN_THIN || refuse "THIN opening MANIFEST (expected $MAN_THIN) check failed"
[ ! -e $S2_OUT ] || refuse "$S2_OUT exists (opening already ran?)"
[ ! -e $WK ] || refuse "$WK exists (opening already ran?)"
if [ -e $PW ] && kill -0 "$(cat $PW)" 2>/dev/null; then refuse "another s2_postwatch is alive"; fi
echo $$ > $PW
echo "[$(date)] s2 opening trigger armed (pid $$; FROZEN.md5 $(md5sum < $H/FROZEN.md5 | cut -c1-8); settings $(md5sum < $H/s2_settings.sh | cut -c1-8); GS $GS; MAXH $MAXH; runs $(echo $ALL | wc -w))" >> $NL

# ---- wait ----
cnt(){ local r n=0; for r in $ALL; do grep -qE "trained $r rc=0\$" $LL && n=$((n + 1)); done; echo $n; }
cok(){ local r n=0; for r in $ALL; do grep -qF "config OK $r vs " $LL && n=$((n + 1)); done; echo $n; }
ALT=$(echo $ALL | tr ' ' '|')
bad(){ grep -E "trained ($ALT) rc=[1-9][0-9]*\$|CONFIG FAIL ($ALT):" $LL | head -1; }
T0=$(date +%s)
while :; do
  [ -e $LL ] && [ "$(cnt)" = 10 ] && [ "$(cok)" = 10 ] && break
  b=$(bad 2>/dev/null); [ -n "$b" ] && endfail "$(echo "$b" | cut -c1-200)"
  [ $(( $(date +%s) - T0 )) -ge $(( MAXH * 3600 )) ] && endfail "not all 10 runs trained rc 0 + config OK within $MAXH h ($(cnt) trained, $(cok) config OK)"
  sleep 120
done
frozen_ok || endfail "FROZEN.md5 / scorer files changed after arming"
echo "[$(date)] s2 scoring start (10 runs trained rc 0, 10 config OK; GS $GS)" >> $NL
GS=$GS bash $H/s2_post.sh
rc=$?
rm -f $PW
exit $rc
