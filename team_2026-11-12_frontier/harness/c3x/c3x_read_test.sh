#!/bin/bash
# c3x: test of run_read_c3x.sh on a FAKE relay root (synthetic manifests only, no dump data, no read tool run: STUB=true).
# Checks: SHOW; refusals with nothing written (missing relays; one wrong manifest field each: COMBO revision, writer, device,
# weights key of COMBO_SWAD, step; missing enc_probe.jsonl; wrong C3X; output folder exists); the positive path (folder,
# 125 links, expected_dumps.tsv, the stub gets the five arms and the six pairs).
# Usage: CLONE=<scratch clone holding the c3x commit> C3X=<that commit> bash c3x_read_test.sh <new work dir>
set -u
W=${1:?work dir}; CLONE=${CLONE:?}; C3X=${C3X:?}; H=$(cd "$(dirname "$(readlink -f "$0")")" && pwd)
[ -e $W ] && { echo "REFUSED: $W exists"; exit 1; }
mkdir -p $W; RR=$W/relay; RD=$W/reads; OLD=89b9ea5a12a37a87c16c4868cc4adf00794a7610
n=0; f=0; ok(){ n=$((n+1)); echo "PASS $*"; }; bad(){ n=$((n+1)); f=$((f+1)); echo "FAIL $*"; }
mk(){ # relay rid run_for_dir method key rev [dumpdirname]
  local rl=$1 run=$2 meth=$3 key=$4 rev=$5 dn=${6:-$2} k=${2#*_f}; k=${k:0:1}; local s=${2##*_s}; s=${s:0:1}
  local d=$RR/$rl/$run/dumps/elbench1/$meth/$dn/cv5v3_f$k; mkdir -p $d $RR/$rl/.ok
  echo "{\"run_id\": \"$dn\", \"fold\": $k, \"seed\": $s, \"weights_key\": \"$key\", \"step\": 20000, \"set\": \"cv5v3_f$k\", \"precision\": \"fp32\", \"set_kind\": \"open\", \"train_code_revision\": \"$rev\", \"device\": \"NVIDIA RTX A6000\", \"writer\": \"bench_infer.py 1111\"}" > $d/manifest.json
  touch $RR/$rl/.ok/$run; grep -q "relayed $run:" $RR/$rl/relay.log 2>/dev/null || echo "[x] relayed $run: 9 files" >> $RR/$rl/relay.log; }
build(){ rm -rf $RR; for s in 5 6 7 8 9; do for k in 0 1 2 3 4; do
  mk c3base c3_pf_v11_f${k}_s$s house_r34_unetpp_pf_v11 model $OLD
  mk c3hrnet c3h_hrnet_w18_unetpp_pf_f${k}_s$s hrnet_w18_unetpp_pf_v11 model $OLD
  mk c3swad c3s_swad_v11_f${k}_s$s swad_const_pf_v11 swad_bn $OLD
  r=c3x_hrnet_swad_v11_f${k}_s$s; mk c3x $r hrnet_w18_unetpp_swad_const_pf_v11 swad_bn $C3X; mk c3x $r hrnet_w18_unetpp_swad_const_pf_v11 swad $C3X $r.swad
  mkdir -p $RR/c3x/$r/experiments/$r; echo '{"step": 20000, "stages": {"model": {"cos": 0.9}}}' > $RR/c3x/$r/experiments/$r/enc_probe.jsonl
  done; done; }
RUN(){ RELAY_ROOT=$RR READ_ROOT=$RD C3X_REPO=$CLONE C3X=${XX:-$C3X} STUB=${STUB-true} bash $H/run_read_c3x.sh 2>&1; }
S=$(SHOW=1 bash $H/run_read_c3x.sh); case "$S" in *"--pair SWADBN=COMBO_SWAD"*"--aa PF:5,6:7,8"*) ok "SHOW prints the command";; *) bad "SHOW";; esac
build; rm -rf $RR/c3x/c3x_hrnet_swad_v11_f2_s7 $RR/c3x/.ok/c3x_hrnet_swad_v11_f2_s7
o=$(RUN); [[ "$o" == *"REFUSED: 1 of 100 runs not relayed"*"c3x_hrnet_swad_v11_f2_s7"* ]] && [ ! -e $RD/c3x ] && ok "missing relayed run refused, no folder" || bad "missing run: $o"
case1(){ # name, sed expression on one manifest, path of that manifest, expected text
  build; sed -i "$2" $3; o=$(RUN); [[ "$o" == *"$4"* ]] && [[ "$o" == *"REFUSED: manifest check failed"* ]] && [ ! -e $RD/c3x ] && ok "$1 refused, no folder" || bad "$1: $(echo "$o" | tail -3)"; }
MX=$RR/c3x/c3x_hrnet_swad_v11_f1_s6/dumps/elbench1/hrnet_w18_unetpp_swad_const_pf_v11
case1 "COMBO revision 89b9ea5" "s/$C3X/$OLD/" $MX/c3x_hrnet_swad_v11_f1_s6/cv5v3_f1/manifest.json "train_code_revision = '$OLD', expected '$C3X'"
case1 "PF revision C3X" "s/$OLD/$C3X/" $RR/c3base/c3_pf_v11_f4_s9/dumps/elbench1/house_r34_unetpp_pf_v11/c3_pf_v11_f4_s9/cv5v3_f4/manifest.json "expected '$OLD'"
case1 "two writers" "s/bench_infer.py 1111/bench_infer.py 2222/" $RR/c3hrnet/c3h_hrnet_w18_unetpp_pf_f0_s5/dumps/elbench1/hrnet_w18_unetpp_pf_v11/c3h_hrnet_w18_unetpp_pf_f0_s5/cv5v3_f0/manifest.json "writers over the 125 dumps"
case1 "two devices" "s/RTX A6000/RTX PRO 4500/" $RR/c3swad/c3s_swad_v11_f3_s8/dumps/elbench1/swad_const_pf_v11/c3s_swad_v11_f3_s8/cv5v3_f3/manifest.json "devices over the 125 dumps"
case1 "COMBO_SWAD key swad_bn" 's/"weights_key": "swad"/"weights_key": "swad_bn"/' $MX/c3x_hrnet_swad_v11_f1_s6.swad/cv5v3_f1/manifest.json "weights_key = 'swad_bn', expected 'swad'"
case1 "step 600" 's/"step": 20000/"step": 600/' $MX/c3x_hrnet_swad_v11_f1_s6/cv5v3_f1/manifest.json "step = 600, expected 20000"
build; rm $RR/c3x/c3x_hrnet_swad_v11_f0_s9/experiments/c3x_hrnet_swad_v11_f0_s9/enc_probe.jsonl
o=$(RUN); [[ "$o" == *"1 of 100 runs not relayed (or a dump folder or enc_probe.jsonl is missing): c3x_hrnet_swad_v11_f0_s9"* ]] && [ ! -e $RD/c3x ] && ok "missing enc_probe.jsonl refused" || bad "enc_probe: $o"
build; o=$(XX=852ed5c411b967d7ea758ef2cd5dbe70ae4e50a1 RUN); [[ "$o" == *"C3X is not the c3x commit"* ]] && [ ! -e $RD/c3x ] && ok "wrong C3X refused" || bad "C3X: $o"
build; o=$(STUB="echo STUBARGS" RUN)
nl=$(find $RD/c3x/links -type l 2>/dev/null | wc -l); bl=$(find -L $RD/c3x/links -type l 2>/dev/null | wc -l)
[[ "$o" == *"manifest check: 125 dumps, device ['NVIDIA RTX A6000'], writer ['bench_infer.py 1111']: OK"* ]] && [[ "$o" == *"STUBARGS --arm PF="*"--arm COMBO_SWAD="*"--pair SWADBN=COMBO_SWAD"* ]] \
  && [ "$nl" = 125 ] && [ "$bl" = 0 ] && [ "$(grep -c . $RD/c3x/expected_dumps.tsv)" = 125 ] && [[ "$o" == *"C3X READ ALL DONE (rc 0)"* ]] && ok "complete set: folder, 125 live links, stub got 5 arms and 6 pairs" || bad "positive: nl $nl bl $bl $(echo "$o" | tail -4)"
o=$(RUN); [[ "$o" == *"output folder exists"* ]] && ok "second run refused (output folder exists)" || bad "exists: $o"
echo "c3x read test: $((n-f)) of $n PASS"
