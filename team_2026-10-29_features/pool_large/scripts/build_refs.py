"""Build reference stem lists for the large-pool audit (local files only, read-only inputs).

Writes <out>/refs.json with: labelled stems per split (582), E1 106, ext117, the 117 E-SCDD _rf stems,
the 17 _rf stems not in our pool, current external pool (11,938), mim_pool_v11 pool part (11,219), monitor (256),
D7 twins, and module sets. Module id = first two '_' fields of the stem.
Usage: python -I build_refs.py <out_dir>
"""
import csv
import json
import sys
from pathlib import Path

R = Path("/home/yugma/mtp/research")
DS = Path("/home/yugma/mtp/datasets")
out = Path(sys.argv[1])


def rd(p):
    return [x.strip() for x in open(p) if x.strip()]


def mod(s):
    return "_".join(s.split("_")[:2])


sp = DS / "splits_benchmark"
lab = {k: rd(sp / f"{k}.txt") for k in ("train", "val", "test")}
ext = rd(sp / "external_unlabeled.txt")
meta = {r["stem"]: r for r in csv.DictReader(open(sp / "external_unlabeled_meta.csv"))}
rows = list(csv.DictReader(open(R / "results/e1/ext117_manifest.csv")))
ext117 = sorted(r["stem"] for r in rows)
e1 = sorted(r["stem"] for r in rows if r["in_external_pool"] == "0")
rf = sorted({p.name[:-len("_rf.png")] for p in (DS / "escdd_full").glob("el_images_*/*_rf.png")
             if not p.name[0].isdigit()})
ext_set = set(ext)
rf17 = sorted(s for s in rf if s not in ext_set)
cp = R / "team_2026-10-29_features/results/b2/coach_pull"
mim = rd(cp / "mim_pool_v11.txt")
mim_pool = sorted(Path(x).stem for x in mim if x.startswith("unlabeled/"))
mim_train = sorted(Path(x).stem for x in mim if x.startswith("labeled/"))
mon = sorted(Path(x).stem for x in rd(cp / "mim_monitor_v11.txt"))
twins = ["CFVS_00003_r5_c5", "CFVS_00037_r8_c4", "CFVS_00032_r8_c4", "CFVS_00020_r4_c4", "CFVS_00022_r4_c4",
         "CFVS_00031_r4_c4", "ARTS_00081_r5_c1"]
refs = dict(
    train=lab["train"], val=lab["val"], test=lab["test"], e1=e1, ext117=ext117, rf117=rf, rf17=rf17,
    pool11938=sorted(ext), mim_pool11219=mim_pool, mim_train471=mim_train, monitor256=mon, d7_twins=twins,
    pool_meta={s: meta[s]["source_file"] for s in ext},
)
mods = {k: sorted({mod(s) for s in v}) for k, v in refs.items() if isinstance(v, list)}
refs["modules"] = mods
out.mkdir(parents=True, exist_ok=True)
json.dump(refs, open(out / "refs.json", "w"), indent=0)
for k, v in refs.items():
    if isinstance(v, list):
        print(f"{k}: {len(v)} stems, {len(mods[k])} modules")
print("rf in pool:", len(set(rf) & ext_set), "rf17:", rf17)
print("mim_pool subset of pool:", set(mim_pool) <= ext_set, "monitor subset:", set(mon) <= ext_set,
      "pool - mim - monitor:", len(ext_set - set(mim_pool) - set(mon)))
