#!/bin/bash
# w2b builder CPU checks on gaint (CPU only: CUDA_VISIBLE_DEVICES="", nice 19, two lanes of 4 threads = 8 in total).
# Base = c57508e (bench_w2, the wave 2a deploy). NEW = a git archive of the bench_w2b commit TAG under IO (frozen: edits
# in the worktree during the run cannot reach it). Nothing is written inside el_bench, bench_wt_w2 or the worktree.
# Usage: bash run_w2b_check.sh <lane A|B> <TAG>   (TAG = short commit of NEW; the output goes to IO/check_<TAG>)
#   Lane A: flag-off 5-step identity (identity_cpu.py 962379a6) ref c57508e vs NEW for the house and PF cards on fold
#     roots (PFV11 = house_r34_unetpp_pf_v11 and HV11 = house_r34_unetpp_v11 on cv5v2_v11_f0; PFV1 = house_r34_unetpp_pf
#     and HV1 = house_r34_unetpp on cv5v2_v1_f0) and RCS; then the render check (every card of c57508e rendered at ref and
#     at NEW for seeds 5 and 6 on the five cv5v2_v11 roots, md5 equal), cfgcheck at NEW of the 10 W1-G and the wave 2a
#     config_used.yaml, the full pytest of NEW, and the 5-step train.py smokes of the new cards (+ PF at ref and at NEW).
#   Lane B: identity for the other wave 2a cards: SBJ (soft_band_jml), JMLH (jml_hard), EMA, SWAD, SPD.
# Only IDENTICAL / DIFF and counts are printed for the identity; no metric of any held-out cell is read.
set -u
LANE=${1:?lane A or B}; TAG=${2:?tag}
IO=/home/noob/work/bench_w2b_io; OUT=$IO/check_$TAG; mkdir -p $OUT; L=$OUT/run.log
P=/home/noob/work/el-fault-detection/.venv/bin/python
ID=/home/noob/work/bench_check/identity_cpu.py; CMP=/home/noob/work/bench_check/compare_id.py
REF=$IO/ref_c57508e; WT=/home/noob/work/bench_wt_w2b; NEW=$IO/new_$TAG
RV11=/home/noob/work/bench_data/roots/cv5v2_v11_f0; RV1=/home/noob/work/bench_data/roots/cv5v2_v1_f0
export CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1
log() { echo "[$(date '+%F %T')] $LANE: $*" >> $L; }
log "start; TAG $TAG = $(git -C $WT rev-parse $TAG); worktree HEAD $(git -C $WT rev-parse --short HEAD); bench_wt_w2 $(git -C /home/noob/work/bench_wt_w2 rev-parse --short HEAD) changes $(git -C /home/noob/work/bench_wt_w2 status --porcelain -uno | wc -l); el_bench $(git -C /home/noob/work/el_bench rev-parse --short HEAD) changes $(git -C /home/noob/work/el_bench status --porcelain -uno | wc -l); identity_cpu $(md5sum < $ID | cut -c1-8) compare_id $(md5sum < $CMP | cut -c1-8)"
git -C $WT merge-base --is-ancestor c57508ec458b54d935a8c3ffcfe722ff2acadb38 $TAG || { log "REFUSED: $TAG is not on c57508e"; exit 1; }
if [ "$LANE" = A ]; then
  if [ ! -d $NEW ]; then
    mkdir -p $NEW && git -C $WT archive $TAG | tar -x -C $NEW && echo $TAG > $NEW/REVISION
    for d in labeled escdd_masks unlabeled; do ln -s "$(readlink /home/noob/work/bench_wt_w2/data/$d)" $NEW/data/$d; done
    log "new made: git archive $TAG -> $NEW (+ data symlinks)"
  fi
  if [ ! -d $REF ]; then
    mkdir -p $REF && git -C /home/noob/work/el_bench archive c57508ec458b54d935a8c3ffcfe722ff2acadb38 | tar -x -C $REF && echo c57508e > $REF/REVISION
    for d in labeled escdd_masks unlabeled; do ln -s "$(readlink /home/noob/work/bench_wt_w2/data/$d)" $REF/data/$d; done
    log "ref made: git archive c57508e -> $REF (+ data symlinks)"
  fi
  touch $OUT/ref.ready
else
  t=0; while [ ! -e $OUT/ref.ready ] && [ $t -lt 600 ]; do sleep 5; t=$((t+5)); done
fi
card_opts() { (cd $NEW && $P -m bench.cards opts bench/methods/$1.yaml --seed 5 --run-name idw2b_$1 --data-root $2 | tr '\n' ' '); }
ident() {  # arm card root
  local arm=$1 o; o=$(card_opts $2 $3) || { log "id $arm: opts FAIL"; return; }
  mkdir -p $OUT/id
  for side in ref new; do
    local code=$REF; [ $side = new ] && code=$NEW
    nice -n 19 $P $ID --code $code --out $OUT/id/${arm}_$side.json --steps 5 --threads 4 --opts $o > $OUT/id/${arm}_$side.log 2>&1
    log "id $arm $side rc=$?"
  done
  $P $CMP $OUT/id/${arm}_ref.json $OUT/id/${arm}_new.json > $OUT/id/${arm}_cmp.txt 2>&1
  log "id $arm ($2 on $(basename $3)) compare rc=$?: $(cat $OUT/id/${arm}_cmp.txt)"
}

if [ "$LANE" = A ]; then
  ident PFV11 house_r34_unetpp_pf_v11 $RV11
  ident HV11 house_r34_unetpp_v11 $RV11
  ident PFV1 house_r34_unetpp_pf $RV1
  ident HV1 house_r34_unetpp $RV1
  ident RCS rcs_pf_v11 $RV11
  # render check: every card that exists at c57508e, seeds 5 and 6, five cv5v2_v11 roots: md5 of the rendered config
  nr=0; ns=0; bad=""
  for cf in $REF/bench/methods/*.yaml; do c=$(basename $cf .yaml)
    for k in 0 1 2 3 4; do for s in 5 6; do r=/home/noob/work/bench_data/roots/cv5v2_v11_f$k
      a=$(cd $REF && $P -m bench.cards render bench/methods/$c.yaml --seed $s --run-name x_$c --data-root $r 2>&1 | md5sum | cut -c1-32)
      b=$(cd $NEW && $P -m bench.cards render bench/methods/$c.yaml --seed $s --run-name x_$c --data-root $r 2>&1 | md5sum | cut -c1-32)
      nr=$((nr+1)); [ "$a" = "$b" ] && ns=$((ns+1)) || bad="$bad $c/f$k/s$s"
    done; done
    [ "$(md5sum < $cf)" = "$(md5sum < $NEW/bench/methods/$c.yaml)" ] || bad="$bad $c(card file differs)"
  done
  log "render check: $ns of $nr rendered configs equal at c57508e and at NEW (cards of c57508e: $(ls $REF/bench/methods/*.yaml | wc -l)); differing:${bad:- none}"
  nc=0; nt=0
  for k in 0 1 2 3 4; do for s in 5 6; do n=w1g_pf_v11_f${k}_s$s; c=/home/noob/work/el_bench/experiments/$n/config_used.yaml
    [ -s $c ] || continue; nt=$((nt+1))
    m=$(cd $NEW && $P -m bench.cards cfgcheck bench/methods/house_r34_unetpp_pf_v11.yaml --config $c --seed $s --run-name $n --data-root /home/noob/work/bench_data/roots/cv5v2_v11_f$k)
    [ "$m" = "config OK (= card)" ] && nc=$((nc+1))
  done; done
  log "W1-G config_used.yaml cfgcheck OK at NEW: $nc of $nt"
  nc=0; nt=0; J=/home/noob/work/bq/w2a/jobs.txt
  while IFS='|' read -r n card s root rest; do c=/home/noob/work/bench_wt_w2/experiments/$n/config_used.yaml
    [ -s $c ] || continue; nt=$((nt+1))
    m=$(cd $NEW && $P -m bench.cards cfgcheck $card --config $c --seed $s --run-name $n --data-root $root)
    [ "$m" = "config OK (= card)" ] && nc=$((nc+1)) || log "w2a cfgcheck $n: $m"
  done < $J
  log "wave 2a config_used.yaml (bq/w2a/jobs.txt $(md5sum < $J | cut -c1-8)) cfgcheck OK at NEW: $nc of $nt"
  (cd $NEW && nice -n 19 $P -m pytest -q -p no:cacheprovider tests > $OUT/pytest_all.log 2>&1)
  log "pytest full suite NEW rc=$?: $(tail -1 $OUT/pytest_all.log)"
  # 5-step train.py smokes (real path: card opts + 5-step overrides; experiments under IO; checkpoints removed after)
  E=$OUT/exp; mkdir -p $E
  S="training.total_steps=5 training.val_every=5 training.checkpoint_every=5 training.num_workers=2 training.log_every=1 logging.experiments_dir=$E"
  smoke() {  # name code card root extra...
    local name=$1 code=$2 card=$3 root=$4; shift 4
    local o; o=$(cd $NEW && $P -m bench.cards opts bench/methods/$card.yaml --seed 5 --run-name $name --data-root $root) || { log "smoke $name: opts FAIL"; return; }
    (cd $code && nice -n 19 $P scripts/train.py --config configs/supervised.yaml --device cpu --opts $o $S "$@" > $E/$name.stdout 2>&1)
    local rc=$?
    local cc; cc=$(cd $NEW && $P -m bench.cards cfgcheck bench/methods/$card.yaml --config $E/$name/config_used.yaml --seed 5 --run-name $name --data-root $root | grep -o "^[A-Za-z ]*[0-9]*" | head -1)
    log "smoke $name ($card, code $(basename $code), root $(basename $root)) rc=$rc tracebacks $(grep -c Traceback $E/$name.stdout) nan $(grep -ci 'loss.*nan' $E/$name/train.log) $(grep -o 'Labelled: [0-9]*' $E/$name/train.log | head -1) | cfgcheck vs card (5-step overrides expected): $cc | $(grep -o 'LA_CE: .*' $E/$name/train.log | head -1) $(grep -o 'LAYERED_CI: .*' $E/$name/train.log | head -1) | step1 $(grep -o 'step 1/5 .*' $E/$name/train.log | head -1)"
    [ "${KEEP_CK:-0}" = 1 ] || rm -rf $E/$name/checkpoints
  }
  smoke w2bs_pf_ref $REF house_r34_unetpp_pf_v11 $RV11
  smoke w2bs_pf_new $NEW house_r34_unetpp_pf_v11 $RV11
  # flag-off train.py path end to end: metrics.json of the two PF smokes equal except timing (losses, lr, val, test tables)
  $P - $E/w2bs_pf_ref/metrics.json $E/w2bs_pf_new/metrics.json > $OUT/pf_smoke_metrics_cmp.txt 2>&1 <<'PYEOF'
import json, sys
a, b = (json.load(open(f)) for f in sys.argv[1:3])
def strip(d):
    d = dict(d); d.pop("timing", None); d.pop("run_name", None)
    d["train_curve"] = [{k: v for k, v in r.items() if k != "steps_per_sec"} for r in d.get("train_curve", [])]
    return d
sa, sb = strip(a), strip(b)
diff = sorted(k for k in set(sa) | set(sb) if sa.get(k) != sb.get(k))
print(("IDENTICAL (metrics.json without timing / run_name / steps_per_sec; keys %d)" % len(sa)) if not diff else f"DIFF in {diff}")
sys.exit(1 if diff else 0)
PYEOF
  log "PF smoke ref vs new metrics.json rc=$?: $(cat $OUT/pf_smoke_metrics_cmp.txt)"
  for c in $(cd $NEW && ls bench/methods/*.yaml | xargs -n1 basename | sed 's/\.yaml$//'); do
    [ -e $REF/bench/methods/$c.yaml ] && continue
    KEEP_CK=1 smoke w2bs_${c}_f0 $NEW $c $RV11
    smoke w2bs_${c}_f3 $NEW $c /home/noob/work/bench_data/roots/cv5v2_v11_f3
    # dumps of the 5-step fold-0 checkpoint (CPU fp32) with every decision the card allows; writer check on read
    DD=$OUT/dumps; decs="card"; [ "$(grep -c '^decision_rule: layered_ci_replace' $NEW/bench/methods/$c.yaml)" = 1 ] && decs="card argmax24 layered_ci_union"
    for dec in $decs; do
      (cd $NEW && nice -n 19 $P scripts/bench_infer.py --run $E/w2bs_${c}_f0 --set cv5v2_f0 --dumps $DD --method $c --card bench/methods/$c.yaml --decision $dec --expect-step 5 --device cpu --precision fp32 --threads 4 --workers 2 > $OUT/dump_${c}_$dec.log 2>&1)
      log "dump $c decision $dec rc=$?: $(grep -o 'dumped .*cells.*s ->' $OUT/dump_${c}_$dec.log | head -1) tracebacks $(grep -c Traceback $OUT/dump_${c}_$dec.log)"
    done
    (cd $NEW && $P - $DD/elbench1/$c > $OUT/dump_${c}_check.txt 2>&1 <<'PYEOF'
import json, sys
from pathlib import Path
import numpy as np
from bench import dumpfmt
root = Path(sys.argv[1]); out = []
crack = {}
for d in sorted(root.glob("*/cv5v2_f0")):
    m = json.loads((d / "manifest.json").read_text())
    n = 0; extra = set(); sig = 0
    for f in sorted(d.glob("*.npz")):
        c = dumpfmt.read_cell(f)          # check_cell: pred == where(m_crack > 0, 14, oth) outside ties, ranges, dtypes
        n += 1; extra |= set(c) - {"pred", "oth", "m_crack", "p_crack", "p_inact"}
        crack[(d.parent.name, f.stem)] = int((c["pred"] == 14).sum())
    out.append(f"{d.parent.name}: rule {m['decision_rule']} t_I {m.get('decision_t_I')} cells {n} extra keys {sorted(extra)} writer check OK")
runs = sorted({r for r, _ in crack}); stems = sorted({s for _, s in crack})
same = all(len({crack[(r, s)] for r in runs}) == 1 for s in stems)
out.append(f"crack px per cell equal across the {len(runs)} decision dumps: {same}")
print("; ".join(out))
PYEOF
)
    log "dump check $c rc=$?: $(cat $OUT/dump_${c}_check.txt | tr '\n' ' ' | cut -c1-900)"
    rm -rf $DD $E/w2bs_${c}_f0/checkpoints
  done
  log "lane A done"
fi

if [ "$LANE" = B ]; then
  ident SBJ soft_band_jml $RV11
  ident JMLH jml_hard $RV11
  ident EMA ema_wise_posthoc_pf_v11 $RV11
  ident SWAD swad_const_pf_v11 $RV11
  ident SPD encoder_spd_pf_v11 $RV11
  # flag-off dump identity: the W1-G PF checkpoint of fold 0 seed 5 dumped on CPU (fp32) by the ref and the NEW writer
  W1=/home/noob/work/el_bench/experiments/w1g_pf_v11_f0_s5
  for side in ref new; do code=$REF; [ $side = new ] && code=$NEW
    (cd $code && nice -n 19 $P scripts/bench_infer.py --run $W1 --set cv5v2_f0 --dumps $OUT/dumpid_$side --method house_r34_unetpp_pf_v11 --card bench/methods/house_r34_unetpp_pf_v11.yaml --device cpu --precision fp32 --threads 4 --workers 2 > $OUT/dumpid_$side.log 2>&1)
    log "dump identity $side rc=$?: $(grep -o 'dumped .*cells' $OUT/dumpid_$side.log | head -1)"
  done
  $P /home/noob/work/bench_w2b_io/dump_compare.py $OUT/dumpid_ref/elbench1/house_r34_unetpp_pf_v11/w1g_pf_v11_f0_s5/cv5v2_f0 $OUT/dumpid_new/elbench1/house_r34_unetpp_pf_v11/w1g_pf_v11_f0_s5/cv5v2_f0 $NEW > $OUT/dumpid_cmp.txt 2>&1
  log "dump identity compare rc=$?: $(cat $OUT/dumpid_cmp.txt)"
  rm -rf $OUT/dumpid_ref $OUT/dumpid_new
  log "lane B done"
fi
