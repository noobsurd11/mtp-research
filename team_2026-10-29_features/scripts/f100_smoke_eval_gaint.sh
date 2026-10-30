#!/bin/bash
# Evaluate the protocol_100 smokes (reports/f100/smoke, el_f3 e544133) into reports/f100/smoke/GATES.txt.
set -u
cd /home/noob/work/el_f3
P=/home/noob/work/el-fault-detection/.venv/bin/python
O=reports/f100/smoke; G=$O/GATES.txt
REF=/home/noob/work/el_f2/reports/f100/idchk/i1_elm.lines
S0=/home/noob/work/el_f1/reports/f1/smoke_v1/mim_step0.pth
ENC=/home/noob/work/el_f1/experiments/f1_mim_pre_s0/encoder_final.pth
ext(){ grep -E "src.trainers.trainer — (step|val @)" $1 | sed -E "s/^[0-9-]+ [0-9:,]+ //; s/ +steps_per_sec=[0-9.]+//"; }
for n in a1_nosw_v500 a2_pfneutral_step0 a3_cp_l0 b1_nosw_voff b2_cp_v500 b3_cp_voff c1_suppf c2_mimpf d1_nosw_expseg; do
  ext $O/$n.stdout > $O/$n.lines; grep -v "val @" $O/$n.lines > $O/$n.steplines; done
same(){ cmp -s $1 $2 && echo "IDENTICAL ($(wc -l < $1) lines)" || echo "DIFFER ($(wc -l < $1) vs $(wc -l < $2) lines; first diff: $(diff $1 $2 | head -3 | tr '\n' ' ' | cut -c1-200))"; }
{
echo "== protocol_100 smoke gates, code $(cat REVISION), $(date)"
cat $O/status.txt | sed 's/^/   /'
echo "-- identity (loss/lr/val lines, timestamps and speed stripped)"
head -22 $O/a1_nosw_v500.lines > $O/a1_1k.lines
echo "I1-100 at f3: a1 (no switch) first 1,000 steps vs el_m 1be64e1 i1_elm: $(same $O/a1_1k.lines $REF)"
echo "PF neutral + mim_step0 (a2) vs a1 1k: $(same $O/a2_pfneutral_step0.lines $O/a1_1k.lines)"
echo "CP lambda 0 (a3) vs a1 1k: $(same $O/a3_cp_l0.lines $O/a1_1k.lines)"
echo "expandable_segments (d1) vs a1 1k: $(same $O/d1_nosw_expseg.lines $O/a1_1k.lines)"
echo "-- val off (step lines only, 2,000 steps)"
echo "house: b1 (val off) vs a1 (val 500): $(same $O/b1_nosw_voff.steplines $O/a1_nosw_v500.steplines)"
echo "CP:    b3 (val off) vs b2 (val 500): $(same $O/b3_cp_voff.steplines $O/b2_cp_v500.steplines)"
echo "val lines in b1 / b3: $(grep -c 'val @' $O/b1_nosw_voff.lines) / $(grep -c 'val @' $O/b3_cp_voff.lines)"
echo "-- step 2000 lines"
for n in a1_nosw_v500 c1_suppf c2_mimpf b2_cp_v500; do echo "$n: $(grep 'step 2000/20000' $O/$n.lines | cut -c1-330)"; done
echo "PF encoder lr (c1) at steps 1000/1500/2000: $(grep -h 'PF encoder lr' $O/c1_suppf.stdout | grep -E 'step (1000|1500|2000)$' | sed -E 's/.*lr=//' | tr '\n' ' ')"
echo "F2-100 (c2): $(grep -h 'Encoder initialised' $O/c2_mimpf.stdout | grep -oE '\([0-9]+ tensors, md5 [0-9a-f]+\)') expected md5 $(cut -c1-32 /home/noob/work/el_f1/experiments/f1_mim_pre_s0/encoder_final.md5)"
echo "-- PF gate: per-stage mean cosine / norm ratio to init at step 2,000 (gate: layer3 and layer4 cos >= 0.5)"
OMP_NUM_THREADS=4 CUDA_VISIBLE_DEVICES="" $P reports/enc_cosine.py --out $O/enc_cosine_2k.json \
  --pair "SUP100-g s0 2k (a1) vs ImageNet" $S0 $O/a1_nosw_v500/checkpoints/latest.pth \
  --pair "SUP100-PF s0 2k (c1) vs ImageNet" $S0 $O/c1_suppf/checkpoints/latest_2k.pth \
  --pair "MIM100-PF s0 2k (c2) vs encoder_final" $ENC $O/c2_mimpf/checkpoints/latest_2k.pth 2>&1 | grep -v Warning
echo "-- G5 (coach review_100_v1): PF smokes resumed to 4,000 steps; gate layer3 and layer4 cos >= 0.8 at 4k in both arms"
for n in c1_suppf c2_mimpf; do echo "$n: $(grep -E 'step (2050|4000)/20000' $O/${n}_4k.stdout | sed -E 's/^[0-9-]+ [0-9:,]+ //; s/ +steps_per_sec=[0-9.]+//' | tr '\n' ' ' | cut -c1-400)"; done
OMP_NUM_THREADS=4 CUDA_VISIBLE_DEVICES="" $P reports/enc_cosine.py --out $O/enc_cosine_4k.json \
  --pair "SUP100-PF s0 4k (c1) vs ImageNet" $S0 $O/c1_suppf/checkpoints/latest.pth \
  --pair "MIM100-PF s0 4k (c2) vs encoder_final" $ENC $O/c2_mimpf/checkpoints/latest.pth 2>&1 | grep -v Warning
$P - <<'PY2'
import json
for f, thr in (("reports/f100/smoke/enc_cosine_2k.json", 0.5), ("reports/f100/smoke/enc_cosine_4k.json", 0.8)):
    r = json.load(open(f))
    for lab, v in r.items():
        if "vs ImageNet" in lab and "SUP100-g" in lab:
            continue
        ok = v["layer3"]["cos"] >= thr and v["layer4"]["cos"] >= thr
        print(f"{lab}: steps {v['steps'][1]}, layer3 {v['layer3']['cos']:.3f} layer4 {v['layer4']['cos']:.3f} -> {'PASS' if ok else 'FAIL'} (>= {thr})")
PY2
echo "-- CP100 smoke (b2)"
$P - <<'PY'
import hashlib, json, re
import numpy as np
O = "reports/f100/smoke"
lib = json.load(open(f"{O}/b2_cp_v500/cp_library.json"))
kept = sorted((c["stem"], c["cid"], c["area"]) for c in lib["components"] if c.get("kept"))
tsv = "".join(f"{s}\t{c}\t{a}\n" for s, c, a in kept)
open(f"{O}/cp100_library_kept.tsv", "w").write(tsv)
src = {}
for s, _, _ in kept:
    src[s.split("_")[0]] = src.get(s.split("_")[0], 0) + 1
print("library summary:", lib["summary"])
print(f"kept {len(kept)} comps, {sum(a for _, _, a in kept)} px, sources {src}, kept-list md5 {hashlib.md5(tsv.encode()).hexdigest()}")
v = {k: [] for k in ("cp_crack_px", "cp_ring_px", "cp_fails", "cp_p14_crack", "cp_p14_ring", "loss_cp")}
for ln in open(f"{O}/b2_cp_v500.lines"):
    for k in v:
        m = re.search(rf"{k}=([0-9.e+-]+)", ln)
        if m: v[k].append(float(m.group(1)))
print("pasted crack px/step mean %.0f (labelled 4,549 from masks; ratio %.2f); ring px/step %.0f; fails/step %.2f; p14 crack/ring at 2k %.3f / %.3f; loss_cp at 2k %.4f" % (
    np.mean(v["cp_crack_px"]), np.mean(v["cp_crack_px"]) / 4549, np.mean(v["cp_ring_px"]), np.mean(v["cp_fails"]),
    v["cp_p14_crack"][-1], v["cp_p14_ring"][-1], v["loss_cp"][-1]))
PY
echo "-- decoy go/no-go at 2k (CP b2 vs SUP a1, CP100 library and held-out cells)"
comm -23 <(sort data/splits/train.txt) <(sort reports/f100/cp100_library_exclude.txt) > reports/f100/train_minus_cpexcl.txt
echo "library list: $(wc -l < reports/f100/train_minus_cpexcl.txt) cells (train minus cp100_library_exclude: 7 D7 twins + 6 scuff-as-crack stems; md5 $(md5sum < reports/f100/cp100_library_exclude.txt | cut -c1-8))"
HF_HUB_OFFLINE=1 $P scripts/cp_decoy.py --runs $O/a1_nosw_v500 $O/b2_cp_v500 --labeled reports/f100/train_minus_cpexcl.txt \
  --out $O/decoy_2k.json > $O/decoy_2k.log 2>&1; echo "cp_decoy rc=$?"
$P - <<'PY'
import json
r = json.load(open("reports/f100/smoke/decoy_2k.json"))
a, c = r["runs"]["a1_nosw_v500"], r["runs"]["b2_cp_v500"]
flag = c["decoy"] > 2 * a["decoy"] or c["decoy"] > 0.05
print(f"steps {a['step']} / {c['step']}; SUP 2k real {a['real']:.4f} decoy {a['decoy']:.4f} bg {a['background']:.4f} | CP 2k real {c['real']:.4f} decoy {c['decoy']:.4f} bg {c['background']:.4f} | cells {r['n_cells']} comps {r['n_components']} (no decoy spot {r['n_no_decoy_spot']}) -> {'FAIL (shortcut flag)' if flag else 'PASS'}")
PY
echo "-- memory (nvidia-smi per process, MiB; max over the smoke): see mem.log"
awk '{for (i = 2; i <= NF; i++) if ($i ~ /,$/) {pid = $i; sub(",", "", pid); m = $(i + 1); if (m + 0 > mx[pid]) mx[pid] = m + 0}} END {for (p in mx) print p, mx[p]}' $O/mem.log | sort -n -k2 > $O/mem_max.txt
while read pid mib; do echo "  $pid $(awk -v p=$pid '$1 == p {print $2; exit}' $O/pids.log) max $mib MiB"; done < $O/mem_max.txt
echo
} > $G 2>&1
cat $G
