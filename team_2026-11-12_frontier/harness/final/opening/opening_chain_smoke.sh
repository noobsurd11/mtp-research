#!/bin/bash
# Builder's dry run of the whole opening chain on gaint CPU with SYNTHETIC data (no sealed image, mask or prediction is read):
#   synthetic images and masks named by the real E1 / test50 stem lists (the lists are allowed), 10 tiny random U-Net++ runs
#   laid out like the full-pool runs after the fin2 resume (deploy bench_9967d59, REVISION = F2, latest.pth step 20000 with keys
#   model and swad, relayed LATEST.md5),
#   -> opening_register.sh (IO in scratch; synthetic label dirs; a synthetic fin verdict 'B5 TTA RESULT REPLICATED')
#   -> every line of the registered job list run by G's bench_infer.py exactly as cq.sh renders it, but --device cpu and
#      the paths mapped into the scratch dir; output laid out as relayed units (.ok + 'relayed' log line)
#   -> run_opening_read.sh (R's records, bench_ens_dump --opening, bench_open_read, opening_verdict.py) with test overrides
#   -> negatives: a tampered manifest, a wrong REG_MD5 and an existing output are refused with nothing written.
# Usage: bash opening_chain_smoke.sh <G commit> <R commit> <out dir>   (about 30 to 50 CPU-min, nice 19, 2 x 4 threads)
set -u
G=${1:?G}; RC=${2:?R}; OUT=${3:?out}; HERE=$(cd "$(dirname "$(readlink -f "$0")")" && pwd)
P=/home/noob/work/el-fault-detection/.venv/bin/python; GT=/home/noob/work/bench_wt_openg; RT=/home/noob/work/bench_wt_open
F=9967d59abaab03cef83c1e3014840b2359ef45d7   # F2: the REVISION of the full-pool runs' deploy (fin2 resume)
S=/home/noob/work/bench_int_io/opening/chain_$$; [ -e $S ] && exit 1; mkdir -p $S $OUT || exit 1
export CUDA_VISIBLE_DEVICES="" PYTHONDONTWRITEBYTECODE=1
[ "$(git -C $GT rev-parse HEAD)" = "$G" ] && [ "$(git -C $RT rev-parse HEAD)" = "$RC" ] || { echo "worktrees not at G / R"; exit 1; }
echo "[$(date '+%F %T')] chain smoke in $S (G $G, R $RC)" | tee $OUT/chain_smoke.out
# ---- synthetic data and runs
nice -n 19 $P - "$S" "$RT" "$F" <<'EOF' || exit 1
import hashlib, sys, yaml, numpy as np, torch
from pathlib import Path
from PIL import Image
S, RT, F = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
sys.path.insert(0, str(RT))
from src.models.model_factory import build_model
rng = np.random.default_rng(7)
e1 = [l.strip() for l in open("/home/noob/work/el_f1/reports/f1/ext117/stems_eval.txt") if l.strip()]
t50 = sorted(l.strip() for l in open(RT / "data/splits/test.txt") if l.strip())
def img(p): Image.fromarray(rng.integers(0, 256, (512, 512), dtype=np.uint8)).save(p)
def mask(p, ign=None):
    m = np.zeros((512, 512), np.uint8); m[:, :40] = 7; m[200:210, :] = 4
    if rng.random() < 0.6: m[rng.integers(50, 450), 60:400] = 14
    if rng.random() < 0.3: m[300:400, 300:400] = 11
    if rng.random() < 0.5: m[100:103, :] = 15
    if ign is not None: m[ign] = 255
    Image.fromarray(m).save(p)
ext = S / "ext117"
for d in ("images", "masks", "ignore"): (ext / d).mkdir(parents=True)
(ext / "stems_eval.txt").write_bytes(Path("/home/noob/work/el_f1/reports/f1/ext117/stems_eval.txt").read_bytes())
for s in e1:
    img(ext / "images" / f"{s}.png"); mask(ext / "masks" / f"{s}.png")
    ig = np.zeros((512, 512), np.uint8); ig[0:5, 0:5] = 255; Image.fromarray(ig).save(ext / "ignore" / f"{s}.png")
lab = S / "labeled"
for d in ("images", "masks_coded"): (lab / d).mkdir(parents=True)
v11 = S / "masks_v11"
for d in ("masks", "ignore"): (v11 / d).mkdir(parents=True)
(v11 / "MANIFEST.md5").write_bytes(Path("/home/noob/work/bench_data/masks_v11/MANIFEST.md5").read_bytes())  # hash list only
for s in t50:
    img(lab / "images" / f"{s}.png"); mask(lab / "masks_coded" / f"{s}.png")
    ig = np.zeros((512, 512), bool); ig[10:12, 10:12] = True
    mask(v11 / "masks" / f"{s}.png", ig); Image.fromarray((ig * 255).astype(np.uint8)).save(v11 / "ignore" / f"{s}.png")
types = ["halfcut_multi", "multi", "mono", "no_spacing"]
(S / "cells.tsv").write_text("stem\tsource\tcell_type\n" + "".join(f"{s}\t{s.split('_')[0]}\t{types[i % 4]}\n" for i, s in enumerate(e1 + t50)))
root = S / "noob_el" / "bench_data_fin" / "roots" / "pool532_v11"
(root / "splits").mkdir(parents=True); (root / "splits" / "train.txt").write_text("ARTS_pool_only_r1_c1\n")
dep = S / "noob_el" / "bench_9967d59"; (dep / "experiments").mkdir(parents=True); (dep / "REVISION").write_text(F + "\n")
model = {"name": "unetpp", "in_channels": 1, "num_classes": 24, "start_filters": 2, "dropout_rate": 0.0, "input_size": 512}
for kind in ("fin_hrnet_swad_v11_pool", "fin_pf_v11_pool"):
    for sd in (5, 6, 7, 8, 9):
        run = dep / "experiments" / f"{kind}_s{sd}"; (run / "checkpoints").mkdir(parents=True)
        cfg = {"seed": sd, "method": "supervised", "model": model, "training": {"total_steps": 20000},
               "data": {"root": str(root), "input_size": 512, "mean": [0.5], "std": [0.25]}}
        (run / "config_used.yaml").write_text(yaml.safe_dump(cfg))
        torch.manual_seed(sd * 7 + len(kind)); m = build_model(model)
        with torch.no_grad():   # a 2-channel random head makes float32 near-ties common (attempt 1: a plain dump failed
            m.output_conv.weight.mul_(1000.0)   # dumpfmt.check_cell at 1 px); spreading the logits removes them
            m.output_conv.bias.copy_(torch.randn(24) * 50.0)
        torch.save({"step": 20000, "models": {"model": m.state_dict(), "swad": m.state_dict()}}, run / "checkpoints" / "latest.pth")
        h = hashlib.md5((run / "checkpoints" / "latest.pth").read_bytes()).hexdigest()
        rl = S / "relay_fin" / run.name / "runs" / run.name; rl.mkdir(parents=True)
        (rl / "LATEST.md5").write_text(f"{h}  experiments/{run.name}/checkpoints/latest.pth\n")
print("synthetic data and 10 tiny runs made")
EOF
printf 'x\n=> (a) PF_D4 - PF: CONFIRMED; failing guard items 0\n## decisions (FINAL_RULE section 4)\n(a) B5 TTA RESULT REPLICATED ON CV5V3 / CV02: (a) PF_D4 - PF is CONFIRMED. C1 (PF) is also shown with D4 in the opening (descriptive).\n(b) D4 IN C2 / C3 SUPPORTED ON CV5: (b) CS_D4 - CS is CONFIRMED.\n(c) C2 PASSES ITS CV5 CHECK (selection-biased; the E1 opening is the test): synthetic smoke line\n' > $S/fin_verdict.txt
RULE_MD5=$(md5sum < $HERE/OPENING_RULE.md | cut -c1-32)
# ---- registration (scratch IO)
TEST_MODE=1 IO=$S/io RULE_MD5=$RULE_MD5 G=$G R=$RC SKIP_GIT=1 FIN_VERDICT=$S/fin_verdict.txt EXT_DIR=$S/ext117 LABELED_DIR=$S/labeled \
  MASKS_V11_DIR=$S/masks_v11 REPO_G=$GT bash $HERE/opening_register.sh > $OUT/register.out 2>&1; echo "register rc $?" | tee -a $OUT/chain_smoke.out
tail -3 $OUT/register.out | cut -c1-200 | tee -a $OUT/chain_smoke.out
REG=$(cat $S/io/REGISTERED.md5) || exit 1
# ---- the dumps, as cq.sh renders them (cpu; paths mapped), laid out as relayed units
RD=$S/relay_open; mkdir -p $RD/.ok; : > $RD/relay.log
WINF="bench_infer.py $(md5sum < $GT/scripts/bench_infer.py | cut -c1-32)"
run_job(){ local line=$1; IFS='|' read -r name card seed root fold gate dgate logp extra <<< "$line"; set -- $extra
  local run=${2/\/tmp\/noob_el\//$S/noob_el/} key=$4 tta=$6 st=$8 op meth
  [ $st = e1_106 ] && op=e1_open8_final || op=t50_open19_final
  meth=$(basename $card .yaml)
  (cd $GT && BENCH_EXT=$S/ext117 BENCH_LABELED=$S/labeled OMP_NUM_THREADS=4 nice -n 19 $P -u scripts/bench_infer.py --run $run --set $st \
    --opening $op --dumps $RD/$name/dumps --method $meth --card $card --run-id $name --weights-key $key --tta $tta --device cpu \
    --precision fp32 --threads 4 --workers 0 --batch 8 $([ $logp = 1 ] && echo --logp --ens-member) --forbidden /nonexistent \
    --bench-run dump_$name > $S/dlog_$name.txt 2>&1) || { echo "DUMP FAILED $name"; return 1; }
  touch $RD/.ok/$name; echo "[$(date '+%F %T')] relayed $name: smoke" >> $RD/relay.log; }
export -f run_job; export S GT P RD
t0=$(date +%s)
grep . $S/io/jobs.txt | xargs -P ${PAR:-2} -d '\n' -I{} bash -c 'run_job "$@"' _ {} | tee -a $OUT/chain_smoke.out
echo "dumps: $(ls $RD/.ok | wc -l) of $(grep -c . $S/io/jobs.txt) in $(( $(date +%s) - t0 )) s" | tee -a $OUT/chain_smoke.out
# ---- the read (test overrides; pins of this build)
printf 'G=%s\nR=%s\nW_G="%s"\n' $G $RC "$WINF" > $S/pins.sh
(cd $S/masks_v11 && for s in $(grep . $RT/data/splits/test.txt); do md5sum masks/$s.png ignore/$s.png; done) > $S/v11_filecheck.md5   # synthetic per-file list (N9; the real one is MANIFEST.md5)
RENV="TEST_MODE=1 FIN_VERDICT=$S/fin_verdict.txt V11_FILECHECK_MANIFEST=$S/v11_filecheck.md5 IO=$S/io RD=$RD RF=$S/relay_fin READ_ROOT=$S/reads RT=$RT BENCH_EXT=$S/ext117 BENCH_LABELED=$S/labeled BENCH_MASKS_V11=$S/masks_v11 CELLS_TSV=$S/cells.tsv PINS_FILE=$S/pins.sh DEVICE_OK=cpu"
env $RENV REG_MD5=0000 bash $HERE/run_opening_read.sh > $OUT/neg_regmd5.out 2>&1; echo "negative wrong REG_MD5: rc $? ($(tail -1 $OUT/neg_regmd5.out)); out dir created: $([ -e $S/reads/open_final ] && echo yes || echo no)" | tee -a $OUT/chain_smoke.out
m=$(ls $RD/fin_pf_v11_pool_s7.test50/dumps/elbench1/*/*/test50/manifest.json); cp $m $S/m.bak; chmod u+w $m
sed -i 's/"weights_key": "model"/"weights_key": "swad"/' $m
env $RENV REG_MD5=$REG bash $HERE/run_opening_read.sh > $OUT/neg_manifest.out 2>&1; echo "negative tampered manifest: rc $? ($(grep -m1 'weights_key' $OUT/neg_manifest.out | cut -c1-120)); out dir created: $([ -e $S/reads/open_final ] && echo yes || echo no)" | tee -a $OUT/chain_smoke.out
cp $S/m.bak $m
env $(echo $RENV | sed 's/TEST_MODE=1 //') REG_MD5=$REG bash $HERE/run_opening_read.sh > $OUT/neg_notest.out 2>&1; echo "negative overrides without TEST_MODE: rc $? ($(tail -1 $OUT/neg_notest.out | cut -c1-90)); out dir created: $([ -e $S/reads/open_final ] && echo yes || echo no)" | tee -a $OUT/chain_smoke.out
v=$S/masks_v11/ignore/$(head -1 $RT/data/splits/test.txt).png; cp $v $S/v.bak; chmod u+w $v; printf x >> $v
env $RENV REG_MD5=$REG bash $HERE/run_opening_read.sh > $OUT/neg_v11.out 2>&1; echo "negative v1.1 file changed after registration: rc $? ($(tail -1 $OUT/neg_v11.out | cut -c1-110)); out dir created: $([ -e $S/reads/open_final ] && echo yes || echo no)" | tee -a $OUT/chain_smoke.out
cp $S/v.bak $v
env $RENV REG_MD5=$REG bash $HERE/run_opening_read.sh > $OUT/read.out 2>&1; rc=$?
echo "read rc $rc" | tee -a $OUT/chain_smoke.out
grep -E "manifest check|records:|arms:|f[0-9]+: |FINAL OPENING|ALL DONE" $OUT/read.out | cut -c1-220 | tee -a $OUT/chain_smoke.out
cp $S/reads/open_final/verdict.txt $OUT/verdict_synthetic.txt 2>/dev/null; cp $S/reads/open_final/MD5.txt $OUT/MD5_synthetic.txt 2>/dev/null
for r in read_e1 read_t50_v11 read_t50_v0; do cp $S/reads/open_final/$r/read.txt $OUT/${r}_synthetic.txt 2>/dev/null; done
env $RENV REG_MD5=$REG bash $HERE/run_opening_read.sh > $OUT/neg_exists.out 2>&1; echo "negative existing output: rc $? ($(tail -1 $OUT/neg_exists.out))" | tee -a $OUT/chain_smoke.out
echo "[$(date '+%F %T')] chain smoke done (read rc $rc); scratch removed" | tee -a $OUT/chain_smoke.out
chmod -R u+w $S; rm -rf $S
exit $rc
