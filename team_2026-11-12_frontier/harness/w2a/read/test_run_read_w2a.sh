#!/bin/bash
# Logic test of run_read_w2a.sh on a synthetic fixture (builder, 17 Nov 2026). No dump is read, no metric is computed, the
# read tool is never called: the test runs a copy of the script in which only five lines are replaced (the dump folder, the
# dump logs, the gate folder, the output folder, and the call of bench_read_w1.py, which becomes one printed line).
# The fixture holds a fake dump log (every job rc=0 except dump_w2a_softband_f1_s6 rc=1), fake manifests for every run id
# of bq/w2a2/dump/jobs.txt except that one, and fake gate verdicts (ema PASS, swad OPEN, spd FAIL).
#   bash test_run_read_w2a.sh <work dir that does not exist yet>
# Reads: run_read_w2a.sh, bq/w2a2/dump/jobs.txt, the real PF manifests (device string). Writes only under the work dir.
set -u
S=${1:?usage: test_run_read_w2a.sh <new work dir>}
[ -e $S ] && { echo "exists: $S"; exit 1; }
H=$(dirname $(readlink -f $0))
P=/home/noob/work/el-fault-detection/.venv/bin/python
export PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES=""
mkdir -p $S/fx/dumps $S/fx/gates $S/fx/out || exit 1
C=$S/run_copy.sh
sed -e "s#^WD=.*#WD=$S/fx/dumps#" -e "s#^DLOGS=.*#DLOGS=\"$S/fx/d1.log $S/fx/d2.log\"#" -e "s#^GD=.*#GD=$S/fx/gates#" \
    -e "s#else O=/home/noob/work/bench_reads/w2a#else O=$S/fx/out/w2a#" \
    -e 's#^  nice -n 19 \$P scripts/bench_read_w1.py .*#  echo "WOULD RUN THE READ"; : \\#' $H/run_read_w2a.sh > $C
nd=$(diff $H/run_read_w2a.sh $C | grep -c '^>')
echo "test copy differs from run_read_w2a.sh ($(md5sum < $H/run_read_w2a.sh | cut -c1-8)) in $nd lines (expected 5):"
diff $H/run_read_w2a.sh $C | grep '^>' | cut -c1-150
[ "$nd" = 5 ] || { echo "TEST SETUP FAIL"; exit 1; }
$P - $S/fx <<'EOF' || exit 1
import json, re, sys
from pathlib import Path
fx = Path(sys.argv[1])
dev = json.loads(Path("/home/noob/work/bench_dumps/w1g/elbench1/house_r34_unetpp_pf_v11/w1g_pf_v11_f0_s5/cv5v2_f0/manifest.json").read_text())["device"]
log = []
for l in open("/home/noob/work/bq/w2a2/dump/jobs.txt"):
    job, c = l.split("|")[0], l.split("|")[5]
    g = lambda k: re.search(rf"--{k} (\S+)", c).group(1)
    bad = job == "dump_w2a_softband_f1_s6"
    log.append(f"[2026-11-17 00:00:00] trained {job} rc={1 if bad else 0}")
    if bad:
        continue
    k = int(g("set").rsplit("_f", 1)[1])
    d = fx / "dumps" / g("method") / g("run-id") / g("set")
    d.mkdir(parents=True)
    (d / "manifest.json").write_text(json.dumps({
        "run_id": g("run-id"), "fold": k, "seed": int(l.split("|")[2]), "weights_key": g("weights-key"), "step": 20000,
        "set": g("set"), "precision": "fp32", "set_kind": "open", "code_commit": "c57508ec458b54d935a8c3ffcfe722ff2acadb38",
        "device": dev}))
(fx / "d1.log").write_text("\n".join(log) + "\n")
for gname, v in (("gate_ema_hash_r1", "PASS"), ("gate_swad_prescreen_r1", "OPEN"), ("gate_spd_mech_r1", "FAIL"), ("gate_spd_mech_r2", "FAIL")):
    (fx / "gates" / gname).mkdir()
    (fx / "gates" / gname / "VERDICT").write_text(f"{gname.rsplit('_r', 1)[0]} {v}\n")
print(f"fixture: {len(log)} log lines, {sum(1 for _ in (fx / 'dumps').glob('*/*/*/manifest.json'))} manifests")
EOF
nt=0; nf=0
# t <name> <expected rc> <text that must be in the output> [<text that must not be in the output>] -- VAR=... ...
t(){
  local name=$1 erc=$2 must=$3 mustnot=$4; shift 5
  local out rc
  out=$(env "$@" bash $C 2>&1); rc=$?
  nt=$((nt+1))
  if [ $rc = $erc ] && echo "$out" | grep -qF -- "$must" && { [ -z "$mustnot" ] || ! echo "$out" | grep -qF -- "$mustnot"; }; then
    echo "ok    $name"
  else nf=$((nf+1)); echo "FAIL  $name (rc $rc, expected $erc; must hold '$must'; must not hold '$mustnot')"; echo "$out" | cut -c1-300 | sed 's/^/      /'; fi
}
t "1 auto: complete arms with a passed gate only"           0 "ARMS=auto -> rcs ema jmlhard;" "" -- TAG=t1
t "1b auto: the read would run"                             0 "WOULD RUN THE READ" "" -- TAG=t1b
t "1c auto: softband skipped as incomplete (rc=1)"          0 "skipped (incomplete): softband: dump_w2a_softband_f1_s6 last line: trained dump_w2a_softband_f1_s6 rc=1" "" -- TAG=t1c
t "1d auto: swad skipped, gate OPEN"                        0 "skipped (gate not passed; GATE_ACK=\"swad\" reads it anyway): swad: gate gate_swad_prescreen OPEN" "" -- TAG=t1d
t "1e auto: spd skipped, newest verdict r2 FAIL"            0 "spd: gate gate_spd_mech FAIL ($S/fx/gates/gate_spd_mech_r2/VERDICT)" "" -- TAG=t1e
t "1f auto: pairs of the three arms, no others"             0 "--pair PF=RCS --pair RAWBN=EMA --pair PF=JMLHARD --labels" "SWAD" -- TAG=t1f
t "1g comparator PF seeds 5, 6 and A/A arm PFAA"            0 "_s[56] --arm PFAA=/home/noob/work/bench_dumps/w1g/elbench1/house_r34_unetpp_pf_v11:w1g_pf_v11_f[0-4]_s[5-8]" "" -- TAG=t1g
t "1h A/A option"                                           0 "--baseline PF --aa PFAA:5,6:7,8 --score-exclude" "" -- TAG=t1h
t "2 GATE_ACK reads swad and spd, and says so"              0 "ARMS=auto -> rcs ema jmlhard swad spd;" "" -- TAG=t2 "GATE_ACK=swad spd"
t "2b the acknowledgement is in the log"                    0 "GATE NOT PASSED BUT ACKNOWLEDGED (GATE_ACK): spd: gate gate_spd_mech FAIL" "" -- TAG=t2b "GATE_ACK=swad spd"
# c <name> <shell test>: a check on the files left by the runs above
c(){ nt=$((nt+1)); if eval "$2"; then echo "ok    $1"; else nf=$((nf+1)); echo "FAIL  $1 ($2)"; fi; }
t "2c the read is marked descriptive at start and end"      0 "DESCRIPTIVE ONLY, NOT A SCREEN VERDICT" "" -- TAG=t2c "GATE_ACK=swad spd"
c "2d GATE_ACK.txt names both arms, gates and verdict files" "grep -q 'spd: gate gate_spd_mech FAIL ($S/fx/gates/gate_spd_mech_r2/VERDICT)' $S/fx/out/w2a_t2/GATE_ACK.txt && grep -q 'swad: gate gate_swad_prescreen OPEN' $S/fx/out/w2a_t2/GATE_ACK.txt && grep -q 'NOT A SCREEN VERDICT' $S/fx/out/w2a_t2/GATE_ACK.txt"
c "2e the mark is twice in run.log (start, end)"            "[ \$(grep -c 'DESCRIPTIVE ONLY, NOT A SCREEN VERDICT' $S/fx/out/w2a_t2/run.log) = 2 ]"
c "2f no GATE_ACK.txt in a read without acknowledged arms"  "[ -d $S/fx/out/w2a_t1 ] && [ ! -e $S/fx/out/w2a_t1/GATE_ACK.txt ] && ! grep -q 'DESCRIPTIVE ONLY' $S/fx/out/w2a_t1/run.log"
t "2g GATE_ACK for an arm whose gate passed marks nothing"  0 "ARMS=ema -> ema;" "DESCRIPTIVE ONLY" -- TAG=t2g ARMS=ema GATE_ACK=ema
c "2h and leaves no GATE_ACK.txt"                           "[ ! -e $S/fx/out/w2a_t2g/GATE_ACK.txt ]"
t "3 named arm with a failed gate is refused"             1 "REFUSED, gate not passed: spd: gate gate_spd_mech FAIL" "WOULD RUN" -- TAG=t3 ARMS=spd
# review item 1 (REVIEW_W2A_READ.md): only folders <gate>_r<number> count, and only a file that is exactly "<gate> PASS"
for d in gate_spd_mech_rv gate_spd_mech_r2_rv gate_spd_mech_rerun; do mkdir $S/fx/gates/$d; echo "gate_spd_mech PASS" > $S/fx/gates/$d/VERDICT; done
t "3b folders _rv, _r2_rv, _rerun holding PASS do not count"  1 "REFUSED, gate not passed: spd: gate gate_spd_mech FAIL ($S/fx/gates/gate_spd_mech_r2/VERDICT)" "WOULD RUN" -- TAG=t3b ARMS=spd
t "3c auto mode still skips spd on r2 FAIL"                  0 "spd: gate gate_spd_mech FAIL ($S/fx/gates/gate_spd_mech_r2/VERDICT)" "-> rcs ema jmlhard spd" -- TAG=t3c
mkdir $S/fx/gates/gate_spd_mech_r3; echo "PASS" > $S/fx/gates/gate_spd_mech_r3/VERDICT
t "3d a file holding only PASS does not pass"                1 "REFUSED, gate not passed: spd: gate gate_spd_mech" "WOULD RUN" -- TAG=t3d ARMS=spd
mkdir $S/fx/gates/gate_spd_mech_r4; echo "gate_ema_hash PASS" > $S/fx/gates/gate_spd_mech_r4/VERDICT
t "3e a file naming another gate does not pass"              1 "($S/fx/gates/gate_spd_mech_r4/VERDICT)" "WOULD RUN" -- TAG=t3e ARMS=spd
mkdir $S/fx/gates/gate_spd_mech_r5; printf 'gate_spd_mech PASS\nsecond line\n' > $S/fx/gates/gate_spd_mech_r5/VERDICT
t "3f a file with a second line does not pass"               1 "REFUSED, gate not passed: spd: gate gate_spd_mech" "WOULD RUN" -- TAG=t3f ARMS=spd
c "3g none of these refused runs left an output folder"      "[ ! -e $S/fx/out/w2a_t3b ] && [ ! -e $S/fx/out/w2a_t3d ] && [ ! -e $S/fx/out/w2a_t3e ] && [ ! -e $S/fx/out/w2a_t3f ]"
t "4 named incomplete arm is refused"                     1 "REFUSED, incomplete: softband: dump_w2a_softband_f1_s6 last line" "WOULD RUN" -- TAG=t4 "ARMS=jmlhard softband"
t "5 existing output folder is refused"                     1 "output folder exists: $S/fx/out/w2a_t2" "WOULD RUN" -- TAG=t2
t "6 unknown arm is refused"                                1 "unknown arm: spdctrl" "WOULD RUN" -- TAG=t6 ARMS=spdctrl
# the retrained run arrives: rc=0 in the second dump log and its manifest
echo "[2026-11-17 23:00:00] trained dump_w2a_softband_f1_s6 rc=0" > $S/fx/d2.log
mkdir -p $S/fx/dumps/soft_band_jml/w2a_softband_f1_s6/cv5v2_f1
sed -e 's/w2a_softband_f1_s5/w2a_softband_f1_s6/' -e 's/"seed": 5/"seed": 6/' $S/fx/dumps/soft_band_jml/w2a_softband_f1_s5/cv5v2_f1/manifest.json \
  > $S/fx/dumps/soft_band_jml/w2a_softband_f1_s6/cv5v2_f1/manifest.json
t "7 softband alone is refused (needs jmlhard)"             1 "REFUSED: softband is read only against jmlhard" "WOULD RUN" -- TAG=t7 ARMS=softband
t "8 softband with jmlhard after the retrain"               0 "--pair PF=JMLHARD --pair JMLHARD=SOFTBAND --labels" "" -- TAG=softband "ARMS=jmlhard softband"
t "8b its output folder carries the tag"                    0 "out $S/fx/out/w2a_softband2;" "" -- TAG=softband2 "ARMS=jmlhard softband"
# newest verdict = highest run number, counted as a number: r1 OPEN, r2 FAIL, r9 FAIL, r10 PASS
for v in "r2 FAIL" "r9 FAIL" "r10 PASS"; do set -- $v; mkdir $S/fx/gates/gate_swad_prescreen_$1; echo "gate_swad_prescreen $2" > $S/fx/gates/gate_swad_prescreen_$1/VERDICT; done
t "9 newest gate verdict is r10, not r9 or r2"                  0 "swad: gate gate_swad_prescreen PASS ($S/fx/gates/gate_swad_prescreen_r10/VERDICT)" "" -- TAG=t9 ARMS=swad
t "9b swad arms and pairs"                                  0 "--pair PF=SWADBN --pair SWADRAWBN=SWADBN --pair PF=SWADRAW --pair PF=SWADRAWBN --pair PF=SWAD --pair PF=SWADEMABN --pair PF=SWADEMA --labels" "" -- TAG=t9b ARMS=swad
t "10 auto with everything complete: spd still skipped"     0 "ARMS=auto -> rcs ema jmlhard softband swad;" "" -- TAG=t10
t "10b manifest check counts 150 dumps"                     0 "manifest check: 150 wave 2a dumps" "" -- TAG=t10b
# a manifest with the wrong weights key
M=$S/fx/dumps/ema_wise_posthoc_pf_v11/w2a_ema_f2_s6.raw_bn/cv5v2_f2/manifest.json
cp $M $M.keep; sed -i 's/"weights_key": "raw_bn"/"weights_key": "model"/' $M
t "11 wrong weights key in a manifest is refused"           1 "REFUSED: manifest check failed" "WOULD RUN" -- TAG=t11 ARMS=ema
cp $M.keep $M
# a symlinked run folder
D=$S/fx/dumps/rcs_pf_v11/w2a_rcs_f3_s5; mv $D $D.real; ln -s $D.real $D
t "12 symlinked run folder is refused"                      1 "REFUSED, incomplete: rcs: no dump folder with a manifest" "WOULD RUN" -- TAG=t12 ARMS=rcs
rm $D; mv $D.real $D
t "13 PF4=1: four-seed PF arm, no PFAA"                     0 "_s[5-8] --arm RCS=" "PFAA" -- TAG=t13 ARMS=rcs PF4=1
t "13b PF4=1: A/A on PF"                                    0 "--aa PF:5,6:7,8" "" -- TAG=t13b ARMS=rcs PF4=1
t "13c PF4=1 is marked a sensitivity read"                  0 "SENSITIVITY READ (PF4=1), NEVER THE VERDICT" "" -- TAG=t13c ARMS=rcs PF4=1
c "13d PF4=1 has its own folder and a marker file"          "[ -f $S/fx/out/w2a_pf4_t13/SENSITIVITY_PF4.txt ] && [ ! -e $S/fx/out/w2a_t13 ] && [ \$(grep -c 'SENSITIVITY READ' $S/fx/out/w2a_pf4_t13/run.log) = 2 ]"
t "13e PF4=1 without TAG goes to w2a_pf4, not w2a"          0 "out $S/fx/out/w2a_pf4;" "" -- ARMS=rcs PF4=1
c "13f the default read has no sensitivity marker"          "[ ! -e $S/fx/out/w2a_t1/SENSITIVITY_PF4.txt ] && ! grep -q 'SENSITIVITY READ' $S/fx/out/w2a_t1/run.log"
t "14 SHOW=1 writes nothing"                                0 "SHOW=1 (no check of dumps or gates, nothing run, nothing written); arms: rcs ema jmlhard softband swad spd" "WOULD RUN" -- TAG=t14 SHOW=1
[ ! -e $S/fx/out/w2a_t14 ] && [ ! -e $S/fx/out/w2a_t3 ] && [ ! -e $S/fx/out/w2a_t4 ] && echo "ok    15 refused and SHOW runs left no output folder" || { nf=$((nf+1)); echo "FAIL  15 a refused run left an output folder"; }
nt=$((nt+1))
# a proper later verdict is accepted: <gate>_r<number> with exactly "<gate> PASS"
mkdir $S/fx/gates/gate_spd_mech_r6; echo "gate_spd_mech PASS" > $S/fx/gates/gate_spd_mech_r6/VERDICT
t "16 a proper gate_spd_mech_r6 PASS is accepted"           0 "spd: gate gate_spd_mech PASS ($S/fx/gates/gate_spd_mech_r6/VERDICT)" "DESCRIPTIVE ONLY" -- TAG=t16 ARMS=spd
c "16b and that read carries no GATE_ACK.txt"               "[ -d $S/fx/out/w2a_t16 ] && [ ! -e $S/fx/out/w2a_t16/GATE_ACK.txt ]"
echo "tests: $nt, failed: $nf; real read folder /home/noob/work/bench_reads/w2a exists: $([ -e /home/noob/work/bench_reads/w2a ] && echo yes || echo no)"
[ $nf = 0 ]
