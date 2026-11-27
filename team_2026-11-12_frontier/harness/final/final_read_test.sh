#!/bin/bash
# Final package: test of run_read_final.sh on a FAKE relay root (synthetic manifests only, no dump data, no read tool run:
# STUB). Pattern: harness/c3x/c3x_read_test.sh. The F checks run against the real worktree bench_wt_fin (read-only git
# commands); the read-tree checks against the real bench_wt_final (read-only).
# Checks: SHOW; refusals with nothing written (a missing relay unit; a missing 'relayed' log line; one wrong manifest field
# each: CS_D4 weights key, PF_D4 tta false, PF_D4 revision 03375d4, CB_D4 step 600, a plain arm with the D4 writer, a third
# writer, two devices; review N1: a D4 dump from another checkpoint, a plain dump without checkpoint_md5; wrong F commit;
# F_REPO without F; output folder exists); the positive path (folder, 150 live links,
# expected_dumps.tsv, the stub gets the six arms and the seven pairs, each arm's regex fullmatches exactly its 25 link names
# in its method dir); a TAG repeat writes its own folder; RELAY_FIN outside RELAY_ROOT passes the positive path (and without it
# the moved fin relay is refused).
# Usage: bash final_read_test.sh <new work dir>      (CPU, about a minute; writes only into the work dir)
set -u
W=${1:?work dir}; H=$(cd "$(dirname "$(readlink -f "$0")")" && pwd)
[ -e $W ] && { echo "REFUSED: $W exists"; exit 1; }
mkdir -p $W; RR=$W/relay; RD=$W/reads; PY=/home/noob/work/el-fault-detection/.venv/bin/python
OLD=89b9ea5a12a37a87c16c4868cc4adf00794a7610; C3X=03375d4c5e9ddde040603230eaca2b1c1139e14c
WO="bench_infer.py afd9164264de4d91e43e258e6f8b1836"; WF="bench_infer.py 32e0b67c2ad8073c33440b8347d77f57"
MP=house_r34_unetpp_pf_v11; MX=hrnet_w18_unetpp_swad_const_pf_v11
D4='{"mode": "d4", "scales": [1.0], "d4": true, "views": 8}'
n=0; f=0; ok(){ n=$((n+1)); echo "PASS $*"; }; bad(){ n=$((n+1)); f=$((f+1)); echo "FAIL $*"; }
mk(){ # relay unit method dumpdir fold seed key rev tta writer
  local d=$RR/$1/$2/dumps/elbench1/$3/$4/cv5v3_f$5 ck=$(echo -n ${4%%.*} | md5sum | cut -c1-32); mkdir -p $d $RR/$1/.ok
  echo "{\"run_id\": \"$4\", \"fold\": $5, \"seed\": $6, \"weights_key\": \"$7\", \"step\": 20000, \"set\": \"cv5v3_f$5\", \"precision\": \"fp32\", \"set_kind\": \"open\", \"train_code_revision\": \"$8\", \"tta\": $9, \"device\": \"NVIDIA RTX A6000\", \"writer\": \"${10}\", \"checkpoint_md5\": \"$ck\"}" > $d/manifest.json
  touch $RR/$1/.ok/$2; grep -qF "relayed $2:" $RR/$1/relay.log 2>/dev/null || echo "[x] relayed $2: 9 files" >> $RR/$1/relay.log; }
build(){ rm -rf $RR; for s in 5 6 7 8 9; do for k in 0 1 2 3 4; do
  r=c3_pf_v11_f${k}_s$s; mk c3base $r $MP $r $k $s model $OLD false "$WO"; mk fin $r.tta_d4 $MP $r.tta_d4 $k $s model $OLD "$D4" "$WF"
  r=c3x_hrnet_swad_v11_f${k}_s$s; mk c3x $r $MX $r.swad $k $s swad $C3X false "$WO"; mk c3x $r $MX $r $k $s swad_bn $C3X false "$WO"
  mk fin $r.swad.tta_d4 $MX $r.swad.tta_d4 $k $s swad $C3X "$D4" "$WF"; mk fin $r.swad_bn.tta_d4 $MX $r.swad_bn.tta_d4 $k $s swad_bn $C3X "$D4" "$WF"
  done; done; }
RUN(){ RELAY_ROOT=$RR READ_ROOT=$RD STUB=${STUB-true} bash $H/run_read_final.sh 2>&1; }
S=$(SHOW=1 bash $H/run_read_final.sh); case "$S" in *"--pair PF=PF_D4 --pair CS=CS_D4 --pair PF=CS_D4"*"--pair PF_D4=CS_D4"*"--aa PF:5,6:7,8"*"--score-exclude"*) ok "SHOW prints the command";; *) bad "SHOW";; esac
build; [ "$(find $RR -name manifest.json | wc -l)" = 150 ] && ok "fake relay root: 150 manifests" || bad "fake relay build"
U=c3x_hrnet_swad_v11_f2_s7.swad.tta_d4; rm -rf $RR/fin/$U $RR/fin/.ok/$U
o=$(RUN); [[ "$o" == *"REFUSED: 1 of 150 dump folders not relayed"*"$U"* ]] && [ ! -e $RD/final_tta ] && ok "missing relay unit refused, no folder" || bad "missing unit: $o"
build; sed -i "/relayed c3_pf_v11_f3_s9.tta_d4:/d" $RR/fin/relay.log
o=$(RUN); [[ "$o" == *"REFUSED: 1 of 150"*"c3_pf_v11_f3_s9.tta_d4"* ]] && [ ! -e $RD/final_tta ] && ok "missing 'relayed' log line refused" || bad "log line: $o"
case1(){ # name, sed expression on one manifest, path of that manifest, expected text
  build; sed -i "$2" $3; o=$(RUN); [[ "$o" == *"$4"* ]] && [[ "$o" == *"REFUSED: manifest check failed"* ]] && [ ! -e $RD/final_tta ] && ok "$1 refused, no folder" || bad "$1: $(echo "$o" | tail -4)"; }
FX=$RR/fin/c3x_hrnet_swad_v11_f1_s6.swad.tta_d4/dumps/elbench1/$MX/c3x_hrnet_swad_v11_f1_s6.swad.tta_d4/cv5v3_f1/manifest.json
FP=$RR/fin/c3_pf_v11_f4_s9.tta_d4/dumps/elbench1/$MP/c3_pf_v11_f4_s9.tta_d4/cv5v3_f4/manifest.json
FB=$RR/fin/c3x_hrnet_swad_v11_f0_s5.swad_bn.tta_d4/dumps/elbench1/$MX/c3x_hrnet_swad_v11_f0_s5.swad_bn.tta_d4/cv5v3_f0/manifest.json
PP=$RR/c3base/c3_pf_v11_f2_s8/dumps/elbench1/$MP/c3_pf_v11_f2_s8/cv5v3_f2/manifest.json
CX=$RR/c3x/c3x_hrnet_swad_v11_f3_s7/dumps/elbench1/$MX/c3x_hrnet_swad_v11_f3_s7.swad/cv5v3_f3/manifest.json
case1 "CS_D4 weights key swad_bn" 's/"weights_key": "swad"/"weights_key": "swad_bn"/' $FX "weights_key = 'swad_bn', expected 'swad'"
case1 "PF_D4 tta false" "s/\"tta\": {[^}]*}/\"tta\": false/" $FP "tta = False, expected {'mode': 'd4'"
case1 "PF_D4 revision 03375d4" "s/$OLD/$C3X/" $FP "train_code_revision = '$C3X', expected '$OLD'"
case1 "CB_D4 step 600" 's/"step": 20000/"step": 600/' $FB "step = 600, expected 20000"
case1 "plain PF with the D4 writer" "s/${WO#* }/${WF#* }/" $PP "writer = '$WF', expected '$WO'"
case1 "a third writer" "s/${WF#* }/99999999999999999999999999999999/" $FB "writers over the 150 dumps"
case1 "two devices" "s/RTX A6000/RTX PRO 4500/" $CX "devices over the 150 dumps"
case1 "plain CS tta d4" "s/\"tta\": false/\"tta\": $D4/" $CX "tta = {'mode': 'd4'"
case1 "CS_D4 from another checkpoint (review N1)" "s/\"checkpoint_md5\": \"[0-9a-f]*\"/\"checkpoint_md5\": \"$(echo -n x | md5sum | cut -c1-32)\"/" $FX "c3x_hrnet_swad_v11_f1_s6 key swad: checkpoint_md5 of the D4 dump"
case1 "plain CB without checkpoint_md5 (review N1)" "s/, \"checkpoint_md5\": \"[0-9a-f]*\"//" $RR/c3x/c3x_hrnet_swad_v11_f3_s7/dumps/elbench1/$MX/c3x_hrnet_swad_v11_f3_s7/cv5v3_f3/manifest.json "c3x_hrnet_swad_v11_f3_s7 key swad_bn: checkpoint_md5 of the D4 dump"
build; o=$(F=491e4605e11e4e8858b93f0c2cc2e259376c4b5e RUN); [[ "$o" == *"F is not the final-package commit"* ]] && [ ! -e $RD/final_tta ] && ok "wrong F commit refused" || bad "F: $o"
mkdir -p $W/emptyrepo && git -C $W/emptyrepo init -q 2>/dev/null
o=$(F_REPO=$W/emptyrepo RUN); [[ "$o" == *"F is not the final-package commit"* ]] && [ ! -e $RD/final_tta ] && ok "F_REPO without F refused" || bad "F_REPO: $o"
build; o=$(STUB="echo STUBARGS" RUN)
nl=$(find $RD/final_tta/links -type l 2>/dev/null | wc -l); bl=$(find -L $RD/final_tta/links -type l 2>/dev/null | wc -l)
[[ "$o" == *"manifest check: 150 dumps, device ['NVIDIA RTX A6000'], writers [('$WF', 75), ('$WO', 75)]: OK"* ]] \
  && [[ "$o" == *"STUBARGS --arm PF="*"--arm CB_D4="*"--pair PF_D4=CS_D4"* ]] && [ "$nl" = 150 ] && [ "$bl" = 0 ] \
  && [ "$(grep -c . $RD/final_tta/expected_dumps.tsv)" = 150 ] && [[ "$o" == *"FINAL TTA READ ALL DONE (rc 0)"* ]] \
  && ok "complete set: folder, 150 live links, expected_dumps.tsv, stub got 6 arms and 7 pairs" || bad "positive: nl $nl bl $bl $(echo "$o" | tail -4)"
echo "$o" | grep '^STUBARGS' > $W/stubargs.txt
R=$($PY - $W/stubargs.txt $RD/final_tta/links/elbench1 <<'EOF'
import re, shlex, sys
from pathlib import Path
args = shlex.split(open(sys.argv[1]).read())[1:]
arms = [args[i + 1] for i, x in enumerate(args) if x == "--arm"]
pairs = [args[i + 1] for i, x in enumerate(args) if x == "--pair"]
seen, msg = {}, []
for spec in arms:
    name, rest = spec.split("=", 1); mdir, rx = rest.rsplit(":", 1)
    hit = [p.name for p in sorted(Path(mdir).iterdir()) if re.fullmatch(rx, p.name)]
    msg.append(f"{name} {len(hit)}")
    for h in hit:
        seen.setdefault(h, []).append(name)
both = [h for h, v in seen.items() if len(v) > 1]
ok = len(arms) == 6 and len(pairs) == 7 and all(m.endswith(" 25") for m in msg) and len(seen) == 150 and not both
print(("OK " if ok else "BAD ") + ", ".join(msg) + f"; {len(seen)} names; {len(both)} in two arms; {len(pairs)} pairs")
EOF
); [[ "$R" == OK* ]] && ok "each arm regex fullmatches exactly its 25 link names ($R)" || bad "regex partition: $R"
o=$(RUN); [[ "$o" == *"output folder exists"* ]] && ok "second run refused (output folder exists)" || bad "exists: $o"
mv $RR/fin $W/nas_fin; o=$(RELAY_FIN=$W/nas_fin TAG=nas STUB=true RUN); nl=$(find $RD/final_tta_nas/links -type l 2>/dev/null | wc -l)
[[ "$o" == *"FINAL TTA READ ALL DONE (rc 0)"* ]] && [ "$nl" = 150 ] && [ "$(grep -c "|$W/nas_fin/" $RD/final_tta_nas/expected_dumps.tsv)" = 75 ] \
  && ok "RELAY_FIN outside RELAY_ROOT: positive path, the 75 D4 dumps linked from it" || bad "RELAY_FIN: nl $nl $(echo "$o" | tail -2)"
o=$(TAG=nas2 STUB=true RUN); [[ "$o" == *"REFUSED: 75 of 150 dump folders not relayed"* ]] && [ ! -e $RD/final_tta_nas2 ] && ok "without RELAY_FIN the moved fin relay is missing: refused" || bad "no RELAY_FIN: $(echo "$o" | tail -1)"
mv $W/nas_fin $RR/fin
o=$(TAG=t2 STUB=true RUN); [ -d $RD/final_tta_t2/links ] && [[ "$o" == *"FINAL TTA READ ALL DONE (rc 0)"* ]] && ok "TAG repeat writes its own folder final_tta_t2" || bad "TAG: $(echo "$o" | tail -2)"
echo "final read test: $((n-f)) of $n PASS"
