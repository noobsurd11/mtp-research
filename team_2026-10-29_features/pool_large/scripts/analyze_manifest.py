"""Profile the HF manifest by ID only (no pixels) and check exact-ID overlap with our sets.

Usage: python -I analyze_manifest.py <out_dir>   (reads manifest.tsv, rowgroups.json, refs.json; writes
manifest_profile.json and id_overlap.tsv, prints a summary)
"""
import collections
import csv
import json
import re
import sys
from pathlib import Path

out = Path(sys.argv[1])
refs = json.load(open(out / "refs.json"))
rows = list(csv.DictReader(open(out / "manifest.tsv"), delimiter="\t"))
rgm = json.load(open(out / "rowgroups.json"))
PAT = re.compile(r"^([A-Z]+)_(\d+)_r(\d+)_c(\d+)$")


def stem(fp):
    return Path(fp).stem


def mod(s):
    return "_".join(s.split("_")[:2])


N = len(rows)
st = [stem(r["file_path"]) for r in rows]
lab = collections.Counter(r["label"] for r in rows)
fp_dup = collections.Counter(r["file_path"] for r in rows)
stem_dup = collections.Counter(st)
pat_ok = [bool(PAT.match(s)) for s in st]
src = collections.Counter(s.split("_")[0] for s in st)
mods = collections.Counter(mod(s) for s in st)
lab_src = collections.Counter((r["label"], s.split("_")[0]) for r, s in zip(rows, st))
ip_mismatch = sum(Path(r["file_path"]).name != r["image_path"] for r in rows)
lab_mismatch = sum(r["label"] != "__".join(r["file_path"].split("/")[:-1]) for r in rows)
# per-label mean bytes from row groups that are single-label
rg_bytes = collections.defaultdict(list)
for name, m in rgm.items():
    g0 = m["first_global_row"]
    for rg in m["rowgroups"]:
        labs = {rows[g]["label"] for g in range(g0, g0 + rg["rows"])}
        if len(labs) == 1:
            rg_bytes[labs.pop()].append((rg["img_unc"], rg["rows"]))
        g0 += rg["rows"]
lab_bytes = {k: sum(b for b, _ in v) / sum(n for _, n in v) for k, v in rg_bytes.items()}
shard_labels = {name: sorted({rows[g]["label"] for g in range(m["first_global_row"], m["first_global_row"] + m["rows"])})
                for name, m in rgm.items()}
mixed = sum(len(v) > 1 for v in shard_labels.values())
# module ids by source: count, cells per module
cells_per_mod = collections.Counter(mods.values())
mod_by_src = collections.Counter(m.split("_")[0] for m in mods)
# rows and cols per source
rc = collections.defaultdict(collections.Counter)
for s in st:
    m = PAT.match(s)
    if m:
        rc[m.group(1)][(int(m.group(3)), int(m.group(4)))] += 1
maxrc = {k: (max(r for r, _ in v), max(c for _, c in v)) for k, v in rc.items()}

hf_stems = set(st)
hf_mods = set(mods)
stem_rows = collections.defaultdict(list)
for g, s in enumerate(st):
    stem_rows[s].append(g)
sets = ["train", "val", "test", "e1", "ext117", "rf117", "rf17", "pool11938", "mim_pool11219", "monitor256",
        "d7_twins"]
ov = {}
lines = []
for k in sets:
    S = set(refs[k])
    inter = sorted(S & hf_stems)
    M = set(refs["modules"][k])
    mi = sorted(M & hf_mods)
    rows_in_mods = sum(mods[m] for m in mi)
    ov[k] = dict(n=len(S), id_in_hf=len(inter), modules=len(M), modules_in_hf=len(mi), hf_rows_in_those_modules=rows_in_mods)
    for s in inter:
        for g in stem_rows[s]:
            lines.append((k, s, g, rows[g]["label"], rows[g]["shard"], rows[g]["rg"], rows[g]["row_in_rg"]))
# folder agreement for our pool
pm = refs["pool_meta"]
agree = disagree = 0
dis = []
for s, sf in pm.items():
    grp, fold = sf.split("__")[:2]
    hl = {rows[g]["label"] for g in stem_rows.get(s, [])}
    if not hl:
        continue
    if f"{grp}__{fold}" in hl:
        agree += 1
    else:
        disagree += 1
        dis.append((s, sf, sorted(hl)))
pool_missing = sorted(set(pm) - hf_stems)
# 55 labelled cells that were in our 11,993 download: all labelled stems in HF by split, by source
lab_in = {k: collections.Counter(s.split("_")[0] for s in set(refs[k]) & hf_stems) for k in ("train", "val", "test", "e1")}
lab_src_all = {k: collections.Counter(s.split("_")[0] for s in refs[k]) for k in ("train", "val", "test", "e1")}
# held-out module exposure: HF rows in modules of val/test/E1 cells
held = set(refs["modules"]["val"]) | set(refs["modules"]["test"]) | set(refs["modules"]["e1"])
held_rows = sum(mods[m] for m in held & hf_mods)
prof = dict(rows=N, labels=dict(lab), sources=dict(src), label_x_source={f"{a}|{b}": v for (a, b), v in lab_src.items()},
            modules=len(mods), modules_by_source=dict(mod_by_src), cells_per_module_hist=dict(sorted(cells_per_mod.items())),
            max_row_col=maxrc, stem_pattern_ok=sum(pat_ok), dup_file_path=sum(v > 1 for v in fp_dup.values()),
            dup_stem=sum(v > 1 for v in stem_dup.values()), dup_stem_rows=sum(v for v in stem_dup.values() if v > 1),
            image_path_mismatch=ip_mismatch, label_vs_path_mismatch=lab_mismatch, mean_png_bytes_by_label=lab_bytes,
            shards_with_mixed_labels=mixed, overlap=ov, pool_folder_agree=agree, pool_folder_disagree=disagree,
            pool_folder_disagree_examples=dis[:10], pool_missing_from_hf=len(pool_missing),
            pool_missing_examples=pool_missing[:20], labelled_in_hf_by_source={k: dict(v) for k, v in lab_in.items()},
            labelled_by_source={k: dict(v) for k, v in lab_src_all.items()}, held_out_modules=len(held),
            held_out_modules_in_hf=len(held & hf_mods), hf_rows_in_held_out_modules=held_rows,
            dup_stem_examples=[(s, [rows[g]["file_path"] for g in stem_rows[s]]) for s, v in stem_dup.items() if v > 1][:10],
            non_pattern_examples=[s for s, ok in zip(st, pat_ok) if not ok][:20])
json.dump(prof, open(out / "manifest_profile.json", "w"), indent=1)
with open(out / "id_overlap.tsv", "w") as f:
    f.write("set\tstem\tglobal_row\tlabel\tshard\trg\trow_in_rg\n")
    for x in lines:
        f.write("\t".join(map(str, x)) + "\n")
print(json.dumps({k: v for k, v in prof.items() if k not in ("label_x_source",)}, indent=1)[:9000])
