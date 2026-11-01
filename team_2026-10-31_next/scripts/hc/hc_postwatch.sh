#!/bin/bash
# HC opening trigger (protocol_HC v1.1 §9.3, §11 launch-order ruling). DRAFT (runner's helper, 1 Nov 2026) for coach's FREEZE; lives in
# /home/noob/work/nq/hc/. Run in tmux by runner, AFTER coach's FROZEN.md5 exists there. Usage: GS=<MiB, >= 9900> bash hc_postwatch.sh
# Arming (refuses, exit 2, with ONE non-end line "hc opening trigger REFUSED: ..." in nq/post.log, if any check fails; it never writes an
# nq end line, so nq_gpumem keeps logging the training lanes):
#   coach's FROZEN.md5 lists every scorer file (REQ below) and md5sum -c passes; hc_copies.md5 passes (third-party copies = originals);
#   GS >= 9,900; el_hc HEAD = reports/hc/DEPLOY = c2e6973, 0 tracked changes; el_hc/REVISION written if absent (untracked, as el_f3 /
#   el_thin; m0_audit records it as code_revision), else must equal c2e6973; PF2 comparator MANIFEST passes; post/ does not exist yet.
# Fires hc_post.sh when /home/noob/work/nq/launch.log shows "trained hc_HC_100pct_sK rc=0" AND "config OK hc_HC_100pct_sK vs" for all
# K in 5..9 (FROZEN.md5 re-checked just before). hc_post.sh writes the ONE end line "nq scoring done: post rc=N".
# Failure (an HC run trained rc != 0, a "CONFIG FAIL hc_HC_100pct_sK" line, or not all 5 within MAXH h, or FROZEN changed): one line
# "hc trigger: FAIL seen (...); no scoring; end line deferred while nq training processes are alive", then, once no PID in
# /home/noob/work/nq/pids/*.pid is alive (2 polls 60 s apart), the end line "[<date>] nq NOT scored (FAIL): <reason>" (stops nq_gpumem 60 s
# later; deferring it keeps the 10 s memory log while other nq lanes still train). Poll 120 s. PID in /home/noob/work/nq/hc_postwatch.pid.
set -u
H=/home/noob/work/nq/hc; L=/home/noob/work/nq/launch.log; NL=/home/noob/work/nq/post.log; WT=/home/noob/work/el_hc; DEPLOY=c2e6973
PF=/home/noob/work/el_f3/reports/pf2/post; MAXH=${MAXH:-96}
REQ="hc_postwatch.sh hc_post.sh hc_e1_coprim.py hc_shv1.sh hc_shv1_read.py hc_f51.py hc_copies.md5 calib_syn/calib_dump.py calib_syn/el_metrics.py
     found/a8_screen_score.py trackM/m0_analyze.py thin/thin_e1_relf1.py post_extra/hc_b5.sh post_extra/hc_scuffign.sh post_extra/pf2_scuffign.py
     post_extra/calib/calib_dump.py post_extra/calib/el_metrics.py post_extra/calib/pf2_b5_hook.sh post_extra/calib/pf2_b5_pooled.sh"
refuse(){ echo "hc_postwatch refused: $*" >&2; echo "[$(date)] hc opening trigger REFUSED: $*" >> $NL; exit 2; }
frozen_ok(){
  local f; [ -s $H/FROZEN.md5 ] || return 1
  for f in $REQ; do grep -qE "^[0-9a-f]{32}  (\./)?$f\$" $H/FROZEN.md5 || return 1; done
  (cd $H && md5sum -c --quiet FROZEN.md5 && md5sum -c --quiet hc_copies.md5) > /dev/null 2>&1
}
alive(){ local n=0 f; for f in /home/noob/work/nq/pids/*.pid; do [ -e "$f" ] || continue; kill -0 "$(cat $f)" 2>/dev/null && n=$((n + 1)); done; echo $n; }
endfail(){
  echo "[$(date)] hc trigger: FAIL seen ($1); no scoring; end line deferred while nq training processes are alive" >> $NL
  local quiet=0; while [ $quiet -lt 2 ]; do if [ "$(alive)" = 0 ]; then quiet=$((quiet + 1)); else quiet=0; fi; sleep 60; done
  echo "[$(date)] nq NOT scored (FAIL): $1" >> $NL; rm -f /home/noob/work/nq/hc_postwatch.pid; exit 1; }

# ---- arming checks ----
GS=${GS:-}; [ "$GS" -ge 9900 ] 2>/dev/null || refuse "GS '$GS' < 9900 (protocol_HC §9.3: scoring gate >= 9,900 beside training)"
frozen_ok || refuse "coach's $H/FROZEN.md5 missing, not listing every scorer file, or md5sum -c failed (or hc_copies.md5 failed)"
[ "$(git -C $WT rev-parse --short=7 HEAD)" = $DEPLOY ] && [ "$(cat $WT/reports/hc/DEPLOY)" = $DEPLOY ] \
  && [ -z "$(git -C $WT status --short --untracked-files=no)" ] || refuse "el_hc HEAD / DEPLOY != $DEPLOY or tracked changes"
[ -e $WT/REVISION ] || echo $DEPLOY > $WT/REVISION
[ "$(cat $WT/REVISION)" = $DEPLOY ] || refuse "el_hc/REVISION != $DEPLOY"
(cd $PF && md5sum -c --quiet MANIFEST.md5) > /dev/null 2>&1 || refuse "PF2 comparator MANIFEST check failed"
[ ! -e $WT/reports/hc/post ] || refuse "el_hc/reports/hc/post exists (opening already ran?)"
[ -e /home/noob/work/nq/hc_postwatch.pid ] && kill -0 "$(cat /home/noob/work/nq/hc_postwatch.pid)" 2>/dev/null && refuse "another hc_postwatch is alive"
echo $$ > /home/noob/work/nq/hc_postwatch.pid
echo "[$(date)] hc opening trigger armed (pid $$; FROZEN.md5 $(md5sum < $H/FROZEN.md5 | cut -c1-8); GS $GS; MAXH $MAXH)" >> $NL

# ---- wait ----
cnt(){ grep -oE "trained hc_HC_100pct_s[5-9] rc=0\$" $L | sort -u | wc -l; }
cok(){ grep -oE "config OK hc_HC_100pct_s[5-9] vs " $L | sort -u | wc -l; }
bad(){ grep -E "trained hc_HC_100pct_s[5-9] rc=[1-9]|CONFIG FAIL hc_HC_100pct_s[5-9]" $L | head -1; }
T0=$(date +%s)
until [ "$(cnt)" = 5 ] && [ "$(cok)" = 5 ]; do
  b=$(bad); [ -n "$b" ] && endfail "$(echo "$b" | cut -c1-200)"
  [ $(( $(date +%s) - T0 )) -ge $(( MAXH * 3600 )) ] && endfail "not all 5 HC runs trained rc 0 + config OK within $MAXH h ($(cnt) trained, $(cok) config OK)"
  sleep 120
done
frozen_ok || endfail "FROZEN.md5 / scorer files changed after arming"
echo "[$(date)] hc scoring start (5 HC runs trained rc 0, 5 config OK; GS $GS)" >> $NL
GS=$GS bash $H/hc_post.sh
rc=$?
rm -f /home/noob/work/nq/hc_postwatch.pid
exit $rc
