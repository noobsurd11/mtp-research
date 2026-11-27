#!/bin/bash
# Code proof of commit K for T3b (gaint CPU; git archives in a scratch dir; nothing on cv02). Items (each OK or FAIL):
#   1 K's history: F2 and G are ancestors (merge), R's 3 read commits cherry-picked (-x), then the T3b commits; parents listed.
#   2 TRAINING PATH byte-equal to F2: scripts/train.py, src/, configs/, bench/methods/, bench/methods_cv02/, bench/cards.py,
#     bench/tta.py, bench/q/cv02/{cq_setup.sh, cq_gpumem.sh, slim_ckpt.py, cvcard.py, relay_w1c.sh}, bench/q/bench_lib.sh
#     (same file set, every file equal).
#   3 the set of paths where K differs from F2 = G's 4 + R's 9 + the T3b paths listed in LAUNCH_REQUEST_t3b.md (nothing else).
#   4 G's and R's paths in K equal G's / R's, except the T3b-edited ones: G scripts/bench_infer.py, cq.sh; R bench_score.py,
#     bench_open_read.py, bench/derived.py.
#   5 the T3b edits of bench_infer.py, bench_score.py, bench/derived.py only ADD lines (0 removed); sets.py removes 1 line
#     (SIZES, re-added with the T3b sizes); dumpfmt.py changes 1 line (set_kind's sealed test); cq.sh against merge(F2, G) and bench_open_read.py against R: the
#     removed / added line counts printed, each removed line shown.
#   6 dynamic: R's and K's bench_open_read.py on the same synthetic records WITHOUT --t3b: read.txt byte-equal; read.json equal
#     except the new model key cc_recany_20.
#   NEG=1: items 2 and 5 rerun on two tampered copies of K's tree (one byte in src/trainers/weight_avg.py; G's train-overlap guard line removed
#   from scripts/bench_infer.py): each must FAIL.
# Usage: [NEG=1] bash t3b_codeproof.sh <K commit> <out file>
set -u
KC=${1:?K}; OUT=${2:?out}; NEG=${NEG:-0}; HERE=$(cd "$(dirname "$(readlink -f "$0")")" && pwd)
REPO=/home/noob/work/bench_wt_t3b; P=/home/noob/work/el-fault-detection/.venv/bin/python
F2=9967d59abaab03cef83c1e3014840b2359ef45d7; G=8bd1c2761c85f4721e444a8bf7124d2e5804973a; R=0c72cf942a5cc89accfcd02e1d2b443a033549d9
F=821dfadf49116cc6d5fdbd6697e263dd7cf0f834; RB=89b9ea5
S=/home/noob/work/bench_int_io/t3b/codeproof_$$; [ -e $S ] && exit 1; mkdir -p $S
KC=$(git -C $REPO rev-parse "$KC^{commit}") || exit 1
for c in F2:$F2 G:$G R:$R K:$KC M:$(git -C $REPO rev-list --merges -1 $KC); do n=${c%%:*}; mkdir -p $S/$n && git -C $REPO archive ${c#*:} | tar -x -C $S/$n; done
TRAIN="scripts/train.py src configs bench/methods bench/methods_cv02 bench/cards.py bench/tta.py bench/q/cv02/cq_setup.sh bench/q/cv02/cq_gpumem.sh bench/q/cv02/slim_ckpt.py bench/q/cv02/cvcard.py bench/q/cv02/relay_w1c.sh bench/q/bench_lib.sh"
GP=$(git -C $REPO diff --name-only $F $G); RP=$(git -C $REPO diff --name-only $RB $R)
T3B="bench/derived.py bench/dumpfmt.py bench/q/cv02/cq.sh bench/sets.py bench/sets/e1_106_stems.txt bench/sets/e1t3b_f0.txt bench/sets/e1t3b_f1.txt bench/sets/e1t3b_f2.txt bench/sets/e1t3b_f3.txt bench/sets/e1t3b_f4.txt bench/t3b_labels.py scripts/bench_infer.py scripts/bench_make_t3b_roots.py scripts/bench_open_read.py scripts/bench_score.py scripts/bench_t3b_oof.py tests/test_bench_t3b.py"
nf=0; item(){ if [ "$2" = OK ]; then echo "OK    $1: $3"; else echo "FAIL  $1: $3"; nf=$((nf+1)); fi; }
c2(){ # tree: training path vs F2
  local d=$1 bad=""; for p in $TRAIN; do diff -rq $S/F2/$p $d/$p > /dev/null 2>&1 || bad="$bad $p"; done
  [ -z "$bad" ] && item 2 OK "training path byte-equal to F2 ($(cd $d && find $TRAIN -type f | wc -l) files)" || item 2 FAIL "differs from F2:$bad"; }
c5(){ # tree: add-only edits
  local d=$1 x bad="" t
  for x in scripts/bench_infer.py:G scripts/bench_score.py:R bench/derived.py:R; do
    p=${x%%:*}; b=${x#*:}; t=$(diff $S/$b/$p $d/$p | grep -c '^<'); [ "$t" = 0 ] || bad="$bad $p(-$t)"; done
  [ -z "$bad" ] && item 5a OK "bench_infer.py (vs G), bench_score.py, derived.py (vs R): T3b lines only added (0 removed; added $(for x in scripts/bench_infer.py:G scripts/bench_score.py:R bench/derived.py:R; do diff $S/${x#*:}/${x%%:*} $d/${x%%:*} | grep -c '^>'; done | paste -sd/))" || item 5a FAIL "lines removed:$bad"; }
{
echo "t3b code proof $(date '+%F %T'): K $KC (script $(md5sum < $0 | cut -c1-8))"
# 1 history
ok=OK; git -C $REPO merge-base --is-ancestor $F2 $KC && git -C $REPO merge-base --is-ancestor $G $KC || ok=FAIL
for c in 82ea81c 19764b2 0c72cf9; do git -C $REPO log --format=%B $F2..$KC | grep -q "cherry picked from commit $c" || ok=FAIL; done
item 1 $ok "F2 and G ancestors; R's 82ea81c, 19764b2, 0c72cf9 cherry-picked; history: $(git -C $REPO log --format='%h(%p)' $F2..$KC | tr '\n' ' ')"
# 2 training path
c2 $S/K
# 3 path set
WANT=$(printf '%s\n' $GP $RP $T3B | sort -u); GOT=$(git -C $REPO diff --name-only $F2 $KC | sort -u)
[ "$WANT" = "$GOT" ] && item 3 OK "K differs from F2 in exactly $(echo "$GOT" | wc -l) paths (G $(echo $GP | wc -w), R $(echo $RP | wc -w), T3b $(echo $T3B | wc -w), overlaps counted once)" \
  || item 3 FAIL "unexpected: $(comm -3 <(echo "$WANT") <(echo "$GOT") | tr '\n' ' ')"
# 4 G and R paths
bad=""; for p in $GP; do case " scripts/bench_infer.py bench/q/cv02/cq.sh " in *" $p "*) continue;; esac; cmp -s $S/G/$p $S/K/$p || bad="$bad $p"; done
for p in $RP; do case " scripts/bench_score.py scripts/bench_open_read.py bench/derived.py " in *" $p "*) continue;; esac; cmp -s $S/R/$p $S/K/$p || bad="$bad $p"; done
[ -z "$bad" ] && item 4 OK "G's other paths = G, R's other paths = R" || item 4 FAIL "differ:$bad"
# 5 edits
c5 $S/K
t=$(diff $S/F2/bench/sets.py $S/K/bench/sets.py | grep -c '^<'); [ "$t" = 1 ] && item 5b OK "sets.py: 1 line removed (the SIZES line, re-added with the e1t3b sizes), $(diff $S/F2/bench/sets.py $S/K/bench/sets.py | grep -c '^>') added" || item 5b FAIL "sets.py removed $t"
t=$(diff $S/F2/bench/dumpfmt.py $S/K/bench/dumpfmt.py | grep '^<'); [ "$t" = '<     if name in SEALED:' ] && item 5c OK "dumpfmt.py: 1 line changed (set_kind: 'if name in SEALED:' -> '... or name in SEALED_T3B:'), $(diff $S/F2/bench/dumpfmt.py $S/K/bench/dumpfmt.py | grep -c '^>') added" || item 5c FAIL "dumpfmt.py removed: $t"
echo "      cq.sh vs merge(F2, G): -$(diff $S/M/bench/q/cv02/cq.sh $S/K/bench/q/cv02/cq.sh | grep -c '^<') +$(diff $S/M/bench/q/cv02/cq.sh $S/K/bench/q/cv02/cq.sh | grep -c '^>'); removed lines:"
diff $S/M/bench/q/cv02/cq.sh $S/K/bench/q/cv02/cq.sh | grep '^<' | cut -c1-170 | sed 's/^/        /'
echo "      bench_open_read.py vs R: -$(diff $S/R/scripts/bench_open_read.py $S/K/scripts/bench_open_read.py | grep -c '^<') +$(diff $S/R/scripts/bench_open_read.py $S/K/scripts/bench_open_read.py | grep -c '^>'); removed lines:"
diff $S/R/scripts/bench_open_read.py $S/K/scripts/bench_open_read.py | grep '^<' | cut -c1-170 | sed 's/^/        /'
# 6 dynamic: the opening read without --t3b
(cd $S/K/tests && CUDA_VISIBLE_DEVICES= $P - "$S" <<'EOF'
import json, subprocess, sys
from pathlib import Path
S = Path(sys.argv[1]); sys.path.insert(0, str(S / "K" / "tests")); sys.path.insert(0, str(S / "K"))
from test_bench_opening_read import _synth_records
rd = S / "recs"; rd.mkdir()
a = _synth_records(rd, "C1", (5, 6, 7, 8), n_cells=24); b = _synth_records(rd, "C2", (5, 6, 7, 8), n_cells=24, shift=0.1, seed0=1)
for t in ("R", "K"):
    r = subprocess.run([sys.executable, str(S / t / "scripts" / "bench_open_read.py"), "--set", "e1_106", "--arm", "C1=" + ",".join(a),
                        "--arm", "C2=" + ",".join(b), "--pair", "C1=C2", "--aa", "C1:5,6:7,8", "--boot", "200", "--out", str(S / f"rd_{t}")],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
txt = (S / "rd_R" / "read.txt").read_bytes() == (S / "rd_K" / "read.txt").read_bytes()
jr, jk = (json.loads((S / f"rd_{t}" / "read.json").read_text()) for t in ("R", "K"))
def strip(x):
    if isinstance(x, dict):
        return {k: strip(v) for k, v in x.items() if k not in ("cc_recany_20", "seconds", "path")}
    if isinstance(x, list):
        return [strip(v) for v in x]
    return x
print(f"DYN read.txt equal {txt}; read.json equal except cc_recany_20 {strip(jr) == strip(jk)}; cc_recany_20 in K's models {'cc_recany_20' in jk['subsets']['all']['arms']['C1']['models']['5']}")
EOF
) > $S/dyn.out 2>&1
grep -q "DYN read.txt equal True; read.json equal except cc_recany_20 True; cc_recany_20 in K's models True" $S/dyn.out && item 6 OK "$(tail -1 $S/dyn.out)" || item 6 FAIL "$(tail -2 $S/dyn.out | tr '\n' ' ' | cut -c1-200)"
if [ "$NEG" = 1 ]; then
  echo "-- negatives (tampered copies of K's tree; each must FAIL)"
  cp -a $S/K $S/KN1; printf '#' >> $S/KN1/src/trainers/weight_avg.py; c2 $S/KN1
  cp -a $S/K $S/KN2; grep -v 'the set overlaps the run.s training cells' $S/K/scripts/bench_infer.py > $S/KN2/scripts/bench_infer.py; c5 $S/KN2
fi
echo "t3b code proof: $nf FAIL"
} 2>&1 | tee $OUT
rm -rf $S
