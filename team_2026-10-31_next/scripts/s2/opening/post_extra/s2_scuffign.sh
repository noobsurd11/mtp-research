#!/bin/bash
# SKR2 + HC2 opening, pass 10c (s2_post.sh runs it with GS set; reported only, non-fatal): scuff-ignored test pass, descriptive
# (protocol_SKR2_HC2 §4 = protocol_PF2 §4.3, Om B2). DRAFT (runner's helper, 2 Nov 2026) for coach's FREEZE. From hc_scuffign.sh
# (cf516c62): PF2's frozen pf2_scuffign.py (e3615fdb, copy in open/post_extra/) once PER ARM with --code = the arm's worktree, m0 from
# post/m0/<arm>, out post/m0_scuffign/<arm>; ONE shared-gate wait per python process (the HC hook was gated by hc_post.sh instead).
# Self-check inside pf2_scuffign.py first: the 2 cells' stats must equal this opening's m0 JSONs, else it writes nothing for that arm.
set -u
. /home/noob/work/s2q/open/s2_settings.sh || exit 2
. $GATE_SH
GS=${GS:?}; F=0
m=$(settings_check) || { echo "settings: $m"; exit 2; }
for a in SKR01 HC2; do
  w=$(wt_of $a)
  gate_wait $GS "s2 post scuffign $a"
  HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 $P $OPEN/post_extra/pf2_scuffign.py --code $w --m0 $S2_OUT/m0/$a --out $S2_OUT/m0_scuffign/$a \
    --runs $(for r in $(runs_of $a); do echo $w/experiments/$r; done)
  rc=$?; echo "[$(date)] scuffign $a rc=$rc"; [ $rc = 0 ] || F=$((F + 1))
done
[ $F = 0 ]
