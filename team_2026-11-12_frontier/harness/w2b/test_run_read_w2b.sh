#!/bin/bash
# Tests of run_read_w2b.sh (w2b builder, 17 Nov 2026). CPU, no real dump read beyond the existing PF and PF-at-OP-C
# manifests (json only); fixtures in a temp dir under /home/noob/work/bench_w2b_io, removed at the end.
# Cases: SHOW output for both arms and PF4 (arms, pairs, seeds, A/A, 416 set, counts pairs, verdict call); refusals:
# bad ARM, output folder exists, tool md5 not pinned, real state (no w2b dumps yet), fixture with every dump complete
# (STOP=checks: OK), a missing 'trained' line, a non-zero rc, a wrong code commit, a wrong decision rule, a missing t_I
# on a layered readout, a symlinked dump folder, a dump jobs.txt with another md5.
# Usage: bash test_run_read_w2b.sh   (prints one line per case and 'N of N passed')
set -u
H=$(cd "$(dirname "$0")" && pwd); S=$H/run_read_w2b.sh
TMP=$(mktemp -d /home/noob/work/bench_w2b_io/rrtest.XXXXXX); n=0; ok=0
chk(){ n=$((n+1)); if eval "$2"; then ok=$((ok+1)); echo "OK   $1"; else echo "FAIL $1"; fi; }
out(){ env "$@" bash $S 2>&1; }
# ---- SHOW
o=$(out ARM=lace SHOW=1)
chk "show lace: arms PF s[56], PFAA s[5-8], PFC s[56], LACE" '[[ "$o" == *"PF=/home/noob/work/bench_dumps/w1g/elbench1/house_r34_unetpp_pf_v11:w1g_pf_v11_f[0-4]_s[56]"* && "$o" == *"PFAA=/home/noob/work/bench_dumps/w1g/elbench1/house_r34_unetpp_pf_v11:w1g_pf_v11_f[0-4]_s[5-8]"* && "$o" == *"PFC=/home/noob/work/bench_udev/opc/dumps_gaint/elbench1/pf_v11_opc:w1g_pf_v11_f[0-4]_s[56]"* && "$o" == *"LACE=/home/noob/work/bench_dumps/w2b/elbench1/la_ce_pf_v11:w2b_lace_f[0-4]_s[56] "* ]]'
chk "show lace: pairs, A/A, baseline, 416 set" '[[ "$o" == *"--pair PFC=LACE --pair PF=LACE --labels v11"* && "$o" == *"--aa PFAA:5,6:7,8"* && "$o" == *"--baseline PF"* && "$o" == *"--score-exclude /home/yugma/mtp/research/team_2026-11-12_frontier/benchmark/splits/score_exclude_v3.txt"* ]]'
chk "show lace: counts 532 / 416 with R13 classes, verdict" '[[ "$o" == *"counts 532:"*"--pair PFC=LACE --pair PF=LACE --classes 0,1,2,4,5,7,11,13,14,15,16,20,21 --out /home/noob/work/bench_reads/w2b_lace/counts_532.txt"* && "$o" == *"--exclude /home/yugma/mtp/research/team_2026-11-12_frontier/benchmark/splits/score_exclude_v3.txt --out /home/noob/work/bench_reads/w2b_lace/counts_416.txt"* && "$o" == *"w2b_verdict.py --arm lace --read /home/noob/work/bench_reads/w2b_lace --c532"* ]]'
o=$(out ARM=lci SHOW=1)
chk "show lci: 3 readout arms, 5 read pairs, paired count pairs" '[[ "$o" == *"LCI=/home/noob/work/bench_dumps/w2b/elbench1/layered_ci_pf_v11:w2b_lci_f[0-4]_s[56] "* && "$o" == *"LCIARG=/home/noob/work/bench_dumps/w2b/elbench1/layered_ci_pf_v11:w2b_lci_f[0-4]_s[56]\.argmax24"* && "$o" == *"LCIUNI="*"\.layered_ci_union"* && "$o" == *"--pair PFC=LCI --pair PF=LCI --pair LCIARG=LCI --pair LCIARG=LCIUNI --pair PF=LCIARG"* && "$o" == *"--pair PFC=LCI --pair LCIARG=LCI:paired --pair LCIARG=LCIUNI:paired --pair PF=LCI --classes"* ]]'
o=$(out ARM=lci PF4=1 SHOW=1)
chk "show PF4: seeds 5-8 for PF and PFC, A/A on PF, own folder" '[[ "$o" == *"PF=/home/noob/work/bench_dumps/w1g/elbench1/house_r34_unetpp_pf_v11:w1g_pf_v11_f[0-4]_s[5-8]"* && "$o" == *"pf_v11_opc:w1g_pf_v11_f[0-4]_s[5-8]"* && "$o" == *"--aa PF:5,6:7,8"* && "$o" != *"PFAA="* && "$o" == *"/w2b_pf4_lci"* ]]'
# ---- refusals without fixtures
o=$(out ARM=xyz); chk "bad ARM refused" '[[ "$o" == REFUSED*"ARM must be lace or lci"* ]]'
mkdir -p $TMP/out/w2b_lace; o=$(out ARM=lace OUTROOT=$TMP/out); chk "existing output folder refused" '[[ "$o" == *"REFUSED: output folder exists"* ]]'
o=$(out ARM=lace OUTROOT=$TMP/out2 QROOT=$TMP/noq STOP=checks)
chk "real state: no dump jobs in the queue dir -> refused, no output folder" '[[ "$o" == *REFUSED*"jobs.txt missing or md5"* && ! -e $TMP/out2/w2b_lace ]]'
cp -r $H $TMP/hw && echo '# changed after the pin' >> $TMP/hw/w2b_verdict.py
o=$(OUTROOT=$TMP/out3 ARM=lace bash $TMP/hw/run_read_w2b.sh 2>&1); chk "changed w2b_verdict.py refused by its pin" '[[ "$o" == *"REFUSED: w2b_verdict.py md5"* ]]'
# ---- fixture: complete dumps (manifests only) for both arms
DEV=$(python3 -c "import json;print(json.load(open('/home/noob/work/bench_dumps/w1g/elbench1/house_r34_unetpp_pf_v11/w1g_pf_v11_f0_s5/cv5v2_f0/manifest.json'))['device'])")
mkfix(){  # arm queue card pre decs
  local arm=$1 q=$2 card=$3 pre=$4; shift 4
  mkdir -p $TMP/q/$q/dump && cp $H/bq_local/$q/dump/jobs.txt $TMP/q/$q/dump/jobs.txt && : > $TMP/q/$q/dump/launch.log
  for k in 0 1 2 3 4; do for s in 5 6; do for dec in "$@"; do
    job=dump_${pre}_f${k}_s${s}; rid=${pre}_f${k}_s${s}
    if [ $dec = card ]; then [ $arm = lace ] && rule=argmax24 || rule=layered_ci_replace; else job=${job}_$dec; rid=$rid.$dec; rule=$dec; fi
    echo "[2026-11-18 10:00:00] trained $job rc=0" >> $TMP/q/$q/dump/launch.log
    d=$TMP/d/elbench1/$card/$rid/cv5v2_f$k; mkdir -p $d
    python3 - $d $rid $k $s $rule "$DEV" <<'PYEOF'
import json, sys
d, rid, k, s, rule, dev = sys.argv[1:7]
m = {"run_id": rid, "fold": int(k), "seed": int(s), "weights_key": "model", "step": 20000, "set": f"cv5v2_f{k}",
     "precision": "fp32", "set_kind": "open", "decision_rule": rule, "code_commit": "f678381b1906575a69403e54f9c823f5f02bee28",
     "device": dev}
if rule.startswith("layered_ci"):
    m["decision_t_I"] = 0.5
open(f"{d}/manifest.json", "w").write(json.dumps(m))
PYEOF
  done; done; done
}
mkfix lace w2b_lace la_ce_pf_v11 w2b_lace card
mkfix lci w2b_lci layered_ci_pf_v11 w2b_lci card argmax24 layered_ci_union
F="OUTROOT=$TMP/o QROOT=$TMP/q DUMPROOT=$TMP/d STOP=checks"
o=$(out $F ARM=lace); chk "fixture lace complete: checks OK (10 dumps)" '[[ "$o" == *"manifest check: 10 arm dumps"*"OK"* && "$o" == *"STOP=checks: pins, completeness and manifests OK"* ]]'
o=$(out $F ARM=lci); chk "fixture lci complete: checks OK (30 dumps)" '[[ "$o" == *"manifest check: 30 arm dumps"*"OK"* && "$o" == *"STOP=checks"* ]]'
o=$(out $F ARM=lci PF4=1); chk "fixture lci PF4: PF / PFC seeds 5-8 found" '[[ "$o" == *"seeds [5, 6, 7, 8]"*"OK"* ]]'
L=$TMP/q/w2b_lace/dump/launch.log; cp $L $L.bak
grep -v "trained dump_w2b_lace_f3_s6 rc" $L.bak > $L; o=$(out $F ARM=lace); chk "missing trained line refused" '[[ "$o" == *"REFUSED: incomplete: dump_w2b_lace_f3_s6"* ]]'
cp $L.bak $L; echo "[2026-11-18 11:00:00] trained dump_w2b_lace_f1_s5 rc=1" >> $L; o=$(out $F ARM=lace); chk "last trained line rc 1 refused" '[[ "$o" == *"REFUSED: dump_w2b_lace_f1_s5 last line: trained dump_w2b_lace_f1_s5 rc=1"* ]]'
cp $L.bak $L
M0=$TMP/d/elbench1/la_ce_pf_v11/w2b_lace_f2_s5/cv5v2_f2/manifest.json; cp $M0 $M0.bak
python3 -c "import json,sys;p=sys.argv[1];m=json.load(open(p));m['code_commit']='5995379';open(p,'w').write(json.dumps(m))" $M0
o=$(out $F ARM=lace); chk "wrong code commit refused" '[[ "$o" == *"code_commit 5995379"* && "$o" == *"REFUSED: manifest check failed"* ]]'
cp $M0.bak $M0
python3 -c "import json,sys;p=sys.argv[1];m=json.load(open(p));m['decision_rule']='layered_ci_replace';open(p,'w').write(json.dumps(m))" $M0
o=$(out $F ARM=lace); chk "wrong decision rule refused" '[[ "$o" == *"decision_rule"*"expected '"'"'argmax24'"'"'"* && "$o" == *REFUSED* ]]'
cp $M0.bak $M0; rm $M0.bak
M1=$TMP/d/elbench1/layered_ci_pf_v11/w2b_lci_f4_s6.layered_ci_union/cv5v2_f4/manifest.json
python3 -c "import json,sys;p=sys.argv[1];m=json.load(open(p));m.pop('decision_t_I');open(p,'w').write(json.dumps(m))" $M1
o=$(out $F ARM=lci); chk "layered readout without t_I refused" '[[ "$o" == *"decision_t_I = None"* && "$o" == *REFUSED* ]]'
python3 -c "import json,sys;p=sys.argv[1];m=json.load(open(p));m['decision_t_I']=0.5;open(p,'w').write(json.dumps(m))" $M1
D2=$TMP/d/elbench1/la_ce_pf_v11/w2b_lace_f0_s6; mv $D2 $D2.real; ln -s $D2.real $D2
o=$(out $F ARM=lace); chk "symlinked dump folder refused" '[[ "$o" == *"REFUSED: no real dump folder"*"w2b_lace_f0_s6"* ]]'
rm $D2; mv $D2.real $D2
echo "x" >> $TMP/q/w2b_lace/dump/jobs.txt; o=$(out $F ARM=lace); chk "dump jobs.txt with another md5 refused" '[[ "$o" == *"jobs.txt missing or md5"* ]]'
chk "no output folder written by any refused or STOP=checks call" '[ ! -e $TMP/o/w2b_lace ] && [ ! -e $TMP/o/w2b_lci ] && [ ! -e $TMP/o/w2b_pf4_lci ]'
rm -rf $TMP
echo "$ok of $n passed"
[ $ok = $n ]
