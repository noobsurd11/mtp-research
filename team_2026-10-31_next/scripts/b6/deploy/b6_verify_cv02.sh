#!/bin/bash
# runner DRAFT (1 Nov 2026): B6 cv02 deploy, step "verify on cv02" (called by b6_deploy.sh over ssh -a; read-only except the 5
# labeled symlinks). Prints "OK <DEPLOY.md5 md5>" only if every check passes; else "FAIL <what>" and exit 1.
set -u
. /tmp/noob_el/env.sh
B=/tmp/noob_el/el_b6; cd $B || { echo "FAIL no $B"; exit 1; }
fail(){ echo "FAIL $*"; exit 1; }
m8(){ md5sum < "$1" | cut -c1-8; }
md5sum -c --quiet DEPLOY.md5 >/dev/null 2>&1 || fail "DEPLOY.md5 -c"
md5sum -c --quiet CODE.md5 >/dev/null 2>&1 || fail "CODE.md5 -c"
[ "$(cut -c1-7 REVISION)" = e544133 ] || fail "REVISION"
[ "$(m8 frozen/results/b6/FROZEN_B6.md5)" = 807d4d03 ] && (cd frozen && md5sum -c --quiet results/b6/FROZEN_B6.md5 >/dev/null 2>&1) || fail "FROZEN_B6 807d4d03 -c"
(cd q && md5sum -c --quiet exp/EXP.md5 >/dev/null 2>&1) || fail "q/exp EXP.md5 -c"
[ "$(m8 q/b6_jobs.txt)" = 1fea91f5 ] && [ "$(m8 q/ref_SUP.yaml)" = ba0b243d ] && [ "$(m8 q/ref_SUPPF.yaml)" = 6aba106a ] || fail "jobs / ref md5"
[ "$(m8 bin/b6_cv02_queue.sh)" = a0374e91 ] && [ "$(m8 bin/b6_cv02_gpumem.sh)" = 330b1162 ] && [ "$(m8 bin/b6_cv02_identity.sh)" = bd1ba77d ] || fail "bin md5"
[ "$(m8 b6s/b6_score.py)" = 981b5f29 ] && [ "$(m8 b6s/b6_valcmp.py)" = 1ad95d68 ] && [ "$(m8 b6s/b6_forbidden.txt)" = 9bb4d919 ] && [ "$(m8 b6s/b6_folds.tsv)" = e2cafce1 ] || fail "b6s md5"
(cd b6_roots && md5sum -c --quiet ROOTS.md5 >/dev/null 2>&1) || fail "ROOTS.md5 -c"
for k in 0 1 2 3 4; do r=b6_roots/b6_root_$k
  [ -L $r/labeled ] || ln -s $B/b6_data/labeled $r/labeled
  [ "$(readlink $r/labeled)" = $B/b6_data/labeled ] || fail "$r/labeled -> $(readlink $r/labeled)"
  (cd $r && md5sum -c --quiet SPLITS.md5 >/dev/null 2>&1 && md5sum -c --quiet DATA_MANIFEST.md5 >/dev/null 2>&1) || fail "root $k SPLITS / DATA_MANIFEST -c"; done
[ "$(find b6_data -type f | wc -l)" = 1064 ] || fail "b6_data file count"
n=$(find b6_data/labeled/images -name '*.png' -printf '%f\n' | sed 's/\.png$//' | sort | comm -12 - <(sort b6s/b6_forbidden.txt) | wc -l); [ "$n" = 0 ] || fail "$n forbidden stems in b6_data"
W=$HF_HOME/hub/models--smp-hub--resnet34.imagenet/snapshots/7a57b34f723329ff020b3f8bc41771163c519d0c
[ "$(m8 $W/model.safetensors)" = f57b4305 ] && [ "$(m8 $W/config.json)" = edb5bacf ] || fail "R34 ImageNet weights md5"
[ -x /tmp/noob_el/el-fault-detection/.venv/bin/python ] || fail "venv python"
echo "OK $(md5sum < DEPLOY.md5 | cut -c1-32)"
