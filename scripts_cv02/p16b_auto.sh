#!/bin/bash
# P16 Part B (protocols/P16_label_fraction_curve.md, Amendment 1), cv02 worktree el_p16 (d51b60f).
# Waits for P13's CsM5 s0-4 and Cs5 s0-2 to be rescored (rc=0) and for the Part A queue to be empty, picks CutMix from
# P13's *val* numbers only, then queues the 15 SSL runs (session/report dir p16b).
cd /tmp/noob_el/el_p16; R=reports/p16b; P13=/tmp/noob_el/el_p13/reports/p13; mkdir -p $R
need="p13_CsM_5pct_s0 p13_CsM_5pct_s1 p13_CsM_5pct_s2 p13_CsM_5pct_s3 p13_CsM_5pct_s4 p13_Cs_5pct_s0 p13_Cs_5pct_s1 p13_Cs_5pct_s2"
while true; do
  for r in $need; do grep -qE "(trained|rescored) $r rc=[1-9]" $P13/launch.log && { echo "[$(date)] $r failed; stop"; exit 1; }; done
  ok=1; for r in $need; do grep -q "rescored $r rc=0" $P13/launch.log || ok=0; done
  grep -q "queue empty" /tmp/noob_el/el_p13/reports/p16/queue.log || ok=0
  [ $ok = 1 ] && break
  sleep 120
done
/tmp/noob_el/el-fault-detection/.venv/bin/python - > $R/selection.txt <<'EOF'
import json, statistics as st
P = "/tmp/noob_el/el_p13/reports/p13"
def score(arm, seeds):
    ms = [st.mean(json.load(open(f"{P}/{arm}_s{s}.json"))[f"val/{arm}_s{s}"]["new_escdd"][c][m] for s in seeds)
          for c, m in (("crack", "iou"), ("inactive", "iou"), ("crack", "rel_f1_2"))]
    return st.mean(ms), ms
a, am = score("p13_CsM_5pct", range(5))
b, bm = score("p13_Cs_5pct", range(3))
print("P13 val seed means (crack IoU, inactive IoU, crack relF1@2), revised labels, final weights")
print(f"CsM5 (5 seeds): {[round(x, 4) for x in am]} -> score {a:.4f}")
print(f"Cs5  (3 seeds): {[round(x, 4) for x in bm]} -> score {b:.4f}")
print("CUTMIX=" + ("0.5" if a > b else "0"))
EOF
CM=$(grep -oP 'CUTMIX=\K\S+' $R/selection.txt) || { echo "[$(date)] selection failed"; exit 1; }
X=""; [ "$CM" = "0.5" ] && X=" ssl.cutmix_p=0.5"
B="training.total_steps=20000 data.split_seed=0 training.labeled_batch_size=8 training.unlabeled_batch_size=8 data.mask_subdir=labeled/masks_escdd data.augmentation=labelsafe loss.t_pos=0.95 ssl.lambda_final=1.0 ssl.warmup_steps=2000 ssl.ramp_steps=2000 model.name=smp_unetpp loss.supervised=ce_dice ssl.labeled_aug=supervised ssl.student_forward=separate loss.consistency=tolerant_pl loss.tolerance_radius=2$X"
{ echo "# P16 Part B, generated $(date) from $R/selection.txt (CUTMIX=$CM)"
  for s in 0 1 2 3 4; do echo "p16_S_20pct_s$s - ssl_mean_teacher.yaml seed=$s data.labeled_fraction=0.2 $B"; done
  for s in 0 1 2 3 4; do echo "p16_S_50pct_s$s - ssl_mean_teacher.yaml seed=$s data.labeled_fraction=0.5 $B"; done
  for s in 0 1 2 3 4; do echo "p16_Sx_100pct_s$s - ssl_mean_teacher.yaml seed=$s data.labeled_fraction=1.0 data.unlabeled_pool=external $B"; done
} > $R/p16B_queue.spec
echo "[$(date)] CUTMIX=$CM; queueing $(grep -vc '^#' $R/p16B_queue.spec) runs"
bash gpu_queue_p16.sh p16b $R/p16B_queue.spec 3 0 5 1 2 3 4 6 7
