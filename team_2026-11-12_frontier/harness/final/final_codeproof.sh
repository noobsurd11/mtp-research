#!/bin/bash
# Final package code proof (harness/final, item 1 of the lead's brief of 21 Nov 2026): commit F (default 821dfad, the deploy of
# the final package) against the c3x commit 03375d4 (the training, dump and read code of the 25 c3x runs; it also holds the
# gaint TTA deploy's code, pre-ttafix). Read only on every repo; CPU; nice 19; writes only into the scratch dir SCR (new or
# empty; default mktemp under /tmp; removed at the end unless KEEP=1).
#   (1) paths: git diff --name-status 03375d4 F = exactly the 10 expected paths (the two queue scripts, bench/tta.py and
#       scripts/bench_infer.py of the ttafix, the new full-pool root builder, five tests). Nothing under src/ configs/ data/,
#       scripts/train.py, bench/methods/ or bench/methods_cv02/ differs. Runtime trace (python -X importtime, CPU) of
#       scripts/train.py --help in archives of both commits: every repo module it loads is byte-equal, and none is bench.tta
#       or a changed path. The TTA code of 03375d4 = that of ae4dd10 (gaint udev_tta deploy); F's TTA code and its test =
#       2933146 (the reviewed ttafix). Old-style queue lines render byte-equal to 03375d4's cq.sh (the sandbox test
#       tests/test_bench_cq_final.py::test_old_style_lines_render_byte_equal_to_the_prepatch_script, run in an archive of F with
#       GIT_DIR = the repo's git dir, so `git show 03375d4:...` resolves; it must pass, not skip).
#   (2) deploy archive: CODE.md5 of an archive of F built as harness/c3base/c3_deploy.sh builds a stage copy (git archive +
#       REVISION + md5 of every file but CODE.md5, sorted) against the 03375d4 stage copy's CODE.md5: the differing paths are
#       the 10 of (1) plus REVISION. CV02=1 also checks that cv02 /tmp/noob_el/bench_03375d4/CODE.md5 = the stage copy's
#       (ssh -n -a -o BatchMode=yes, read only); otherwise that line is a SKIP. Prints the md5 of F's CODE.md5 (the deploy step
#       c3_deploy.sh F must print the same value).
#   (3) real cells, gaint CPU (DUMPS=1, default; about 80 min): bench_infer.py of an archive of 03375d4 ("old") and of F ("new")
#       on identical inputs: scratch run dirs = the relayed config_used.yaml with data.root moved to the gaint cv5v3 root of the
#       fold (split files equal to cv02's: train.txt md5 = the relayed manifest's split_md5) and checkpoints/latest.pth -> the
#       relayed slim.pth (step 20000); set = the run's own open cv5v3_f0 (107 cells); --device cpu --precision fp32
#       --threads 6 --workers 1 --batch 8.
#       (i)  --tta none, PF run (key model) and c3x run (key swad_bn): every npz byte-identical old vs new; manifests differ
#            only in code_repo, writer, written.
#       (ii) --tta d4, PF run (key model) and c3x run (key swad): oth, m_crack, p_crack, p_inact bit-equal per cell; pred
#            differs only where the old rule argmax p and the new rule argmax log(p + 1e-12) can differ, i.e. every px with a
#            different pred has new pred = where(m_crack > 0, 14, oth) (the log-argmax) and old pred != it; the count is printed
#            (expected 0); an old-code AssertionError (the ttafix failure) is recorded, not hidden.
#       (iii) at F: --tta d4 with key swad_bn on the c3x run loads and dumps (rc 0, 'dumped' line, manifest tta = mode_spec('d4')
#            = {mode d4, scales [1.0], d4 true, views 8}, weights_key swad_bn, step 20000); the PF model key and the c3x swad
#            key under d4 at F are the 'new' dumps of (ii).
#       FAST=1: only the PF run, (i) and (ii) (about 16 min; the negative test uses it). DUMPS=0 skips (3) with a SKIP line.
# Usage: bash final_codeproof.sh [<commit F>]    env: SCR, KEEP=1, CV02=1, DUMPS=0|1, FAST=1, REPO (a scratch clone: tests)
set -u
RP=${REPO:-/home/noob/work/bench_wt_fin}
F=$(git -C $RP rev-parse --verify "${1:-821dfadf49116cc6d5fdbd6697e263dd7cf0f834}^{commit}") || exit 1
OLD=03375d4c5e9ddde040603230eaca2b1c1139e14c; GTTA=ae4dd1094972d00bb55000d76f94598b946a1b68; TFIX=293314633bdf9f86dbea398f044040c20fe8683f
ST=/home/noob/work/bench_c3_io/stage/bench_03375d4
P=/home/noob/work/el-fault-detection/.venv/bin/python
RL=/home/noob/work/bench_relay; V3=/home/noob/work/bench_data_v3b
FORB=$V3/meta/forbidden_v1.txt
DUMPS=${DUMPS:-1}; FAST=${FAST:-0}; CV02=${CV02:-0}
SCR=${SCR:-$(mktemp -d /tmp/final_codeproof.XXXXXX)}; mkdir -p $SCR; [ -z "$(ls -A $SCR 2>/dev/null)" ] || { echo "REFUSED: $SCR not empty"; exit 1; }
fails=0; ok(){ echo "OK   $*"; }; bad(){ echo "FAIL $*"; fails=$((fails+1)); }; skip(){ echo "SKIP $*"; }
export CUDA_VISIBLE_DEVICES="" PYTHONDONTWRITEBYTECODE=1
echo "final code proof: 03375d4 -> $F ($(date '+%F %T'); script $(md5sum < $0 | cut -c1-8); scratch $SCR)"
WANT="M	bench/q/cv02/cq.sh
M	bench/q/cv02/cq_setup.sh
M	bench/tta.py
M	scripts/bench_infer.py
A	scripts/bench_make_pool_root.py
M	tests/test_bench_cards_cv02.py
M	tests/test_bench_cq_cv5v3.py
A	tests/test_bench_cq_final.py
A	tests/test_bench_pool_root.py
A	tests/test_bench_tta_pred.py"

# ---- (1) paths
GOT=$(git -C $RP diff --name-status $OLD $F)
[ "$GOT" = "$WANT" ] && ok "(1) git diff 03375d4 F: exactly the 10 expected paths" || { bad "(1) git diff 03375d4 F differs from the expected 10 paths:"; echo "$GOT" | sed 's/^/     /'; }
h=$(git -C $RP diff --name-only $OLD $F -- src configs data scripts/train.py bench/methods bench/methods_cv02 bench/cards.py \
    bench/dumpfmt.py bench/sets.py bench/q/bench_lib.sh bench/q/cv02/slim_ckpt.py bench/q/cv02/cvcard.py bench/q/cv02/cq_gpumem.sh \
    bench/q/cv02/cq_rescue.sh | tr '\n' ' ')
[ -z "$h" ] && ok "(1) src/ configs/ data/ scripts/train.py bench/methods/ bench/methods_cv02/ bench/cards.py dumpfmt.py sets.py bench_lib.sh slim_ckpt.py cvcard.py cq_gpumem.sh cq_rescue.sh: byte-equal" || bad "(1) changed: $h"
d=$(git -C $RP diff --name-only $GTTA $OLD -- bench/tta.py scripts/bench_infer.py | tr '\n' ' ')
[ -z "$d" ] && ok "(1) 03375d4's bench/tta.py and scripts/bench_infer.py = ae4dd10's (gaint udev_tta deploy, pre-ttafix)" || bad "(1) 03375d4 TTA code differs from ae4dd10: $d"
d=$(git -C $RP diff --name-only $TFIX $F -- bench/tta.py scripts/bench_infer.py tests/test_bench_tta_pred.py | tr '\n' ' ')
[ -z "$d" ] && ok "(1) F's bench/tta.py, scripts/bench_infer.py, tests/test_bench_tta_pred.py = 2933146's (the reviewed ttafix)" || bad "(1) F TTA code differs from 2933146: $d"
mkdir -p $SCR/old $SCR/new && git -C $RP archive $OLD | tar -x -C $SCR/old && git -C $RP archive $F | tar -x -C $SCR/new || { bad "(1) archive failed"; exit 1; }
for t in old new; do (cd $SCR/$t && OMP_NUM_THREADS=1 nice -n 19 $P -X importtime scripts/train.py --help > /dev/null 2> $SCR/train_$t.imp); done
mods=$(grep -ohE '\| +(src|bench|scripts)(\.[A-Za-z0-9_]+)*$' $SCR/train_old.imp $SCR/train_new.imp | awk '{print $2}' | sort -u)
n=$(echo "$mods" | grep -c .); ne=0; diffm=""
for m in $mods; do f=${m//.//}; [ -f $SCR/new/$f.py ] && f=$f.py || f=$f/__init__.py
  cmp -s $SCR/old/$f $SCR/new/$f && ne=$((ne+1)) || diffm="$diffm $m"; done
hit=$(echo "$mods" | grep -E '^bench\.tta$|bench_infer|bench_make_pool_root' | tr '\n' ' ')
[ "$n" -gt 10 ] && [ -z "$diffm" ] && [ -z "$hit" ] && ok "(1) runtime trace of train.py --help: $n repo modules loaded (both commits), $ne byte-equal, none is bench.tta / bench_infer / the pool-root builder" \
  || bad "(1) train.py trace: $n modules, differing:$diffm; hits '$hit'"
echo "$mods" > $SCR/train_modules.txt
r=$(cd $SCR/new && GIT_DIR=$(cd $RP && readlink -f "$(git rev-parse --git-common-dir)") OMP_NUM_THREADS=1 nice -n 19 $P -m pytest -q -p no:cacheprovider -rs \
    "tests/test_bench_cq_final.py::test_old_style_lines_render_byte_equal_to_the_prepatch_script" 2>&1 | tail -1)
case "$r" in "1 passed"*) ok "(1) old-style queue lines render byte-equal to 03375d4's cq.sh (sandbox test in the archive of F: $r)";; *) bad "(1) old-style render test: $r";; esac

# ---- (2) deploy archive (as c3_deploy.sh: git archive + REVISION + CODE.md5)
echo $F > $SCR/new/REVISION
(cd $SCR/new && find . -type f -printf '%P\n' | grep -vx CODE.md5 | sort | xargs -d '\n' md5sum > CODE.md5 && md5sum -c --quiet CODE.md5) || bad "(2) CODE.md5 of the F archive does not check"
(cd $ST && md5sum -c --quiet CODE.md5 > /dev/null 2>&1) && [ "$(cat $ST/REVISION)" = $OLD ] || bad "(2) stage copy $ST: CODE.md5 check failed or REVISION != 03375d4"
D=$(diff <(grep -v '  REVISION$' $ST/CODE.md5) <(grep -v '  REVISION$' $SCR/new/CODE.md5) | grep '^[<>]' | awk '{print $1 $3}' | LC_ALL=C sort | tr '\n' ' ')
DW="<bench/q/cv02/cq.sh <bench/q/cv02/cq_setup.sh <bench/tta.py <scripts/bench_infer.py <tests/test_bench_cards_cv02.py <tests/test_bench_cq_cv5v3.py >bench/q/cv02/cq.sh >bench/q/cv02/cq_setup.sh >bench/tta.py >scripts/bench_infer.py >scripts/bench_make_pool_root.py >tests/test_bench_cards_cv02.py >tests/test_bench_cq_cv5v3.py >tests/test_bench_cq_final.py >tests/test_bench_pool_root.py >tests/test_bench_tta_pred.py "
[ "$D" = "$DW" ] && ok "(2) CODE.md5 of F against the 03375d4 deploy: only the 10 paths differ (+ REVISION); $(grep -c . $SCR/new/CODE.md5) against $(grep -c . $ST/CODE.md5) lines" || bad "(2) CODE.md5 differs in: $D"
echo "     F deploy CODE.md5 md5 $(md5sum < $SCR/new/CODE.md5 | cut -c1-32) ($(grep -c . $SCR/new/CODE.md5) lines; c3_deploy.sh F must print the same)"
if [ "$CV02" = 1 ]; then
  m=$(ssh -n -a -o BatchMode=yes -o ConnectTimeout=20 cv02@10.8.1.106 "md5sum < /tmp/noob_el/bench_03375d4/CODE.md5 | cut -c1-32; cat /tmp/noob_el/bench_03375d4/REVISION" | tr '\n' ' ')
  [ "$m" = "$(md5sum < $ST/CODE.md5 | cut -c1-32) $OLD " ] && ok "(2) cv02 /tmp/noob_el/bench_03375d4: CODE.md5 = the stage copy's, REVISION 03375d4 ($m)" || bad "(2) cv02 bench_03375d4: '$m'"
else skip "(2) cv02 CODE.md5 of bench_03375d4 (set CV02=1)"; fi

# ---- (3) real cells, CPU
CMP=$SCR/cmp.py
cat > $CMP <<'EOF'
"""compare two dump set dirs: plain (every npz byte-identical) or d4 (fields bit-equal; pred differs only where intended)"""
import json, sys
from pathlib import Path
import numpy as np
mode, a, b = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
na, nb = sorted(p.name for p in a.glob("*.npz")), sorted(p.name for p in b.glob("*.npz"))
assert na == nb and na, f"cell files differ: {len(na)} / {len(nb)}"
ident = sum(p.read_bytes() == (b / p.name).read_bytes() for p in a.glob("*.npz"))
ma, mb = json.loads((a / "manifest.json").read_text()), json.loads((b / "manifest.json").read_text())
keys = sorted(k for k in set(ma) | set(mb) if ma.get(k) != mb.get(k))
out = {"cells": len(na), "npz_identical": ident, "bytes": int(sum((a / n).stat().st_size for n in na)), "manifest_keys_differ": keys}
if mode == "d4":
    eq = {k: 0 for k in ("oth", "m_crack", "p_crack", "p_inact")}; dp = intended = ties_new = 0
    for n in na:
        A, B = np.load(a / n), np.load(b / n)
        for k in eq:
            eq[k] += A[k].dtype == B[k].dtype and A[k].tobytes() == B[k].tobytes()
        d = A["pred"] != B["pred"]; dp += int(d.sum())
        m = B["m_crack"].astype(np.float32); want = np.where(m > 0, 14, B["oth"]).astype(np.uint8)
        intended += int((d & (B["pred"] == want) & (A["pred"] != want)).sum())
        ties_new += int((B["pred"] != want).sum())
    out.update({f"{k}_bit_equal": v for k, v in eq.items()}, pred_px_differ=dp, pred_px_differ_intended=intended,
               new_pred_vs_logargmax_px=ties_new, tta_old=ma.get("tta"), tta_new=mb.get("tta"))
print(json.dumps(out))
EOF
dump(){   # TREE TAG RUN METHOD KEY TTA -> dumps under $SCR/dumps/TAG; log $SCR/logs/TAG_RUN_KEY_TTA.log; sets DT (s), DRC
  local t0=$(date +%s) lg=$SCR/logs/$2_$3_$5_$6.log
  (cd $SCR/$1 && OMP_NUM_THREADS=6 nice -n 19 $P -u scripts/bench_infer.py --run $SCR/runs/$3 --set cv5v3_f0 --dumps $SCR/dumps/$2 \
     --method $4 --card bench/methods/$4.yaml --weights-key $5 --tta $6 --device cpu --precision fp32 --threads 6 --workers 1 --batch 8 \
     --forbidden $FORB > $lg 2>&1); DRC=$?; DT=$(( $(date +%s) - t0 ))
  echo "     dump $1 $3 key $5 tta $6: rc $DRC, ${DT} s wall: $(grep -E '^dumped |Error' $lg | tail -1 | cut -c1-150)"; }
setdir(){ local rid=$2; [ "$3" = model ] || rid=$rid.$3; [ "$4" = none ] || rid=$rid.tta_$4; echo $SCR/dumps/$1/elbench1/$5/$rid/cv5v3_f0; }
if [ "$DUMPS" = 0 ]; then skip "(3) real-cell dumps (DUMPS=0)"; else
  PFR=c3_pf_v11_f0_s5; CXR=c3x_hrnet_swad_v11_f0_s5; MP=house_r34_unetpp_pf_v11; MX=hrnet_w18_unetpp_swad_const_pf_v11
  mkdir -p $SCR/runs $SCR/logs $SCR/dumps
  for spec in c3base:$PFR:model c3x:$CXR:swad_bn,swad; do IFS=: read -r rl r keys <<< "$spec"; d=$SCR/runs/$r; mkdir -p $d/checkpoints
    sed 's#/tmp/noob_el/bench_data_v3b/roots/#'$V3'/roots/#' $RL/$rl/$r/experiments/$r/config_used.yaml > $d/config_used.yaml
    ln -s $RL/$rl/$r/experiments/$r/checkpoints/slim.pth $d/checkpoints/latest.pth
    nd=$(diff $RL/$rl/$r/experiments/$r/config_used.yaml $d/config_used.yaml | grep -c '^[<>]')
    sm=$(python3 -c "import json,glob; print(json.load(open(glob.glob('$RL/$rl/$r/dumps/elbench1/*/$r/cv5v3_f0/manifest.json')[0]))['split_md5'])")
    st=$(OMP_NUM_THREADS=1 nice -n 19 $P -c "import torch; s = torch.load('$d/checkpoints/latest.pth', map_location='cpu', weights_only=False); print(s['step'], ','.join(sorted(s['models'])))")
    [ $nd = 2 ] && [ "$sm" = "$(md5sum < $V3/roots/cv5v3_v11_f0/splits/train.txt | cut -c1-32)" ] && case "$st" in "20000 "*) true;; *) false;; esac \
      && ok "(3) run dir $r: config = relayed one with data.root moved to the gaint root (1 line), gaint train.txt md5 = the cv02 dump's split_md5 $sm, slim step/keys '$st'" \
      || bad "(3) run dir $r: diff lines $nd, split_md5 $sm, slim '$st'"
  done
  (cd $V3/roots && md5sum -c --quiet ROOTS_cv5v3_v11.md5 > /dev/null 2>&1) && ok "(3) gaint cv5v3 roots: ROOTS_cv5v3_v11.md5 checks (vs cv02 only MASKLINKS.tsv differ: absolute link paths)" || bad "(3) gaint cv5v3 roots do not check"
  if [ "$FAST" = 1 ]; then PLAIN="$PFR:$MP:model"; D4="$PFR:$MP:model"; NEWONLY=""; else
    PLAIN="$PFR:$MP:model $CXR:$MX:swad_bn"; D4="$PFR:$MP:model $CXR:$MX:swad"; NEWONLY="$CXR:$MX:swad_bn"; fi
  for spec in $PLAIN; do IFS=: read -r r m k <<< "$spec"
    dump old old $r $m $k none; r1=$DRC; dump new new $r $m $k none; r2=$DRC
    c=$( [ $r1$r2 = 00 ] && OMP_NUM_THREADS=1 nice -n 19 $P $CMP plain $(setdir old $r $k none $m) $(setdir new $r $k none $m) 2>&1)
    echo "     $c"
    echo "$c" | python3 -c "import json,sys; d=json.loads(sys.stdin.read()); sys.exit(0 if d['npz_identical']==d['cells'] and set(d['manifest_keys_differ'])<=set(['code_repo','writer','written']) else 1)" 2>/dev/null \
      && ok "(3i) --tta none $r key $k: $(echo "$c" | python3 -c "import json,sys; d=json.loads(sys.stdin.read()); print(f\"{d['npz_identical']} of {d['cells']} npz byte-identical ({d['bytes']} bytes); manifest keys that differ: {d['manifest_keys_differ']}\")")" \
      || bad "(3i) --tta none $r key $k: not byte-identical (rc $r1 / $r2): $c"
  done
  for spec in $D4; do IFS=: read -r r m k <<< "$spec"
    dump old old $r $m $k d4; r1=$DRC; dump new new $r $m $k d4; r2=$DRC
    if [ $r1 != 0 ]; then grep -q "pred disagrees with where" $SCR/logs/old_${r}_${k}_d4.log && echo "     old code raised the ttafix AssertionError (recorded; the fix's target)"; fi
    c=$( [ $r1$r2 = 00 ] && OMP_NUM_THREADS=1 nice -n 19 $P $CMP d4 $(setdir old $r $k d4 $m) $(setdir new $r $k d4 $m) 2>&1)
    echo "     $c"
    echo "$c" | python3 -c "
import json,sys; d=json.loads(sys.stdin.read()); n=d['cells']
ok = all(d[k+'_bit_equal']==n for k in ('oth','m_crack','p_crack','p_inact')) and d['pred_px_differ']==d['pred_px_differ_intended'] \
     and d['tta_new']=={'mode':'d4','scales':[1.0],'d4':True,'views':8} and d['tta_old']==d['tta_new'] \
     and set(d['manifest_keys_differ'])<=set(['code_repo','writer','written','cells','ties_total','bytes_total'])
sys.exit(0 if ok else 1)" 2>/dev/null \
      && ok "(3ii) --tta d4 $r key $k: $(echo "$c" | python3 -c "import json,sys; d=json.loads(sys.stdin.read()); print(f\"oth/m_crack/p_crack/p_inact bit-equal in {d['oth_bit_equal']}/{d['m_crack_bit_equal']}/{d['p_crack_bit_equal']}/{d['p_inact_bit_equal']} of {d['cells']} cells; pred differs at {d['pred_px_differ']} px, all of the ttafix kind ({d['pred_px_differ_intended']}); npz byte-identical {d['npz_identical']}; manifest keys that differ {d['manifest_keys_differ']}\")")" \
      || bad "(3ii) --tta d4 $r key $k (rc $r1 / $r2): $c"
  done
  for spec in $NEWONLY; do IFS=: read -r r m k <<< "$spec"
    dump new new $r $m $k d4
    sd=$(setdir new $r $k d4 $m)
    v=$( [ $DRC = 0 ] && grep -q '^dumped ' $SCR/logs/new_${r}_${k}_d4.log && python3 -c "
import json; d=json.load(open('$sd/manifest.json')); print(d['tta']=={'mode':'d4','scales':[1.0],'d4':True,'views':8} and d['weights_key']=='$k' and d['step']==20000 and d['n_cells']==107, d['tta'], d['weights_key'], d['step'], d['n_cells'], d['ties_total'])")
    case "$v" in True*) ok "(3iii) at F, --tta d4 key $k on $r: rc 0, dumped; manifest tta/key/step/cells: $v";; *) bad "(3iii) --tta d4 key $k on $r: rc $DRC, '$v'";; esac
  done
  [ "$FAST" = 1 ] && skip "(3) FAST=1: the c3x run (swad_bn plain, swad d4, swad_bn d4) not dumped"
fi
cd / ; [ "${KEEP:-0}" = 1 ] && echo "kept $SCR" || rm -rf $SCR
echo "final code proof: $fails FAIL"
exit $([ $fails = 0 ] && echo 0 || echo 1)
