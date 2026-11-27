#!/usr/bin/env python3
"""bench_release, 22 Nov 2026. files/results/BASELINES.md: verbatim copies of thesis tables T5, T6, T7a, T15 (CV5, pool
cells) and T8, T10, T11a (E1 opening #8, aggregates only) from thesis/THESIS_TABLES.md, through stage.py's sanitize rules.
test50 tables (T13a to T13c) are not copied: context only, known leakage. Appends to substitutions.tsv and sources.json.
Run after stage.py: python3 -I stage_results.py"""
import hashlib, json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import stage  # noqa: E402

SRC = stage.TEAM / "thesis" / "THESIS_TABLES.md"
WANT = ["T5.", "T6.", "T7a.", "T15.", "T8.", "T10.", "T11a."]
raw = SRC.read_bytes()
lines = raw.decode().split("\n")
heads = [i for i, l in enumerate(lines) if l.startswith("### ")]
sec = {}
for j, i in enumerate(heads):
    end = heads[j + 1] if j + 1 < len(heads) else next(k for k in range(i + 1, len(lines)) if lines[k].startswith("## "))
    sec[lines[i][4:].split(" ")[0]] = "\n".join(lines[i:end]).rstrip() + "\n"
md5 = hashlib.md5(raw).hexdigest()
out = [
    "# Baseline and final-model results (copied from the thesis tables)",
    "",
    f"Verbatim copies of thesis tables {', '.join(w.rstrip('.') for w in WANT)} from `THESIS_TABLES.md` (md5 {md5[:8]}, 21 Nov 2026).",
    "Every value there is traced to a result file by the thesis-table checker; nothing here is recomputed.",
    "Machine names are replaced: machA = 1 x RTX PRO 4500 (32 GB), machB = 8 x RTX A6000 (48 GB). A read never mixes machines.",
    "Tags: E = measured, S = judgement. Internal file names in the notes (verdict.txt, *_READ.md) refer to the project's result",
    "files; they are not part of this release.",
    "",
    "CV5 tables (T5, T6, T7a, T15) are out-of-fold reads on the 532 pool cells. E1 tables (T8, T10, T11a) are aggregates of the",
    "one registered final opening on the 106 unseen-module cells; no per-cell value, label or prediction is released.",
    "test50 tables are not included: test50 overlaps the training pool (known leakage) and decides nothing.",
    "",
]
for w in WANT:
    out.append(sec[w])
text = "\n".join(out)
dest = "results/BASELINES.md"
p = stage.OUT / dest
p.parent.mkdir(parents=True, exist_ok=True)
p.write_text(stage.sanitize(text, dest), encoding="utf-8")
with open(stage.HERE / "substitutions.tsv", "a") as f:
    for t in stage.SUBS:
        f.write("\t".join(map(str, t)) + "\n")
sj = stage.HERE / "sources.json"
d = json.load(open(sj)); d[dest] = ["thesis/THESIS_TABLES.md (sections " + " ".join(WANT) + ")", md5]
json.dump(dict(sorted(d.items())), open(sj, "w"), indent=1)
print(f"wrote {dest}: {len(WANT)} tables, {len(stage.SUBS)} substituted lines, {sum(t[3] for t in stage.SUBS)} substitutions")
