"""First look: names, sessions, conditions, image/mask sizes and values, CSV coverage, Test_Images relation."""

from __future__ import annotations

import collections
import csv
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
from ucf_common import dump, pairs, parse_name  # noqa: E402

root, out = Path(sys.argv[1]), Path(sys.argv[2])
res = {}
rel = {s: pairs(root, s) for s in ("train", "test")}
names = {s: [p[0] for p in rel[s]] for s in rel}
res["n"] = {s: len(v) for s, v in names.items()}
res["overlap_train_test_names"] = len(set(names["train"]) & set(names["test"]))
res["unparsed"] = {s: [n for n in v if parse_name(n)["session"] is None][:5] for s, v in names.items()}

# conditions / sessions / cells
for s in names:
    p = [parse_name(n) for n in names[s]]
    res[f"{s}_conditions"] = collections.Counter(x["cond"] for x in p).most_common()
    res[f"{s}_n_sessions"] = len({x["session"] for x in p})
    res[f"{s}_cell_range"] = [min(x["cell"] for x in p if x["cell"] is not None), max(x["cell"] for x in p if x["cell"] is not None)]
sess = {s: {parse_name(n)["session"] for n in names[s]} for s in names}
res["sessions_in_both_splits"] = len(sess["train"] & sess["test"])
res["sessions_only_test"] = len(sess["test"] - sess["train"])
per_sess = collections.defaultdict(lambda: [0, 0])
for i, s in enumerate(("train", "test")):
    for n in names[s]:
        per_sess[parse_name(n)["session"]][i] += 1
res["test_share_per_session_quantiles"] = np.quantile([b / (a + b) for a, b in per_sess.values()], [0, .1, .5, .9, 1]).tolist()
res["cells_per_session_quantiles"] = np.quantile([a + b for a, b in per_sess.values()], [0, .1, .5, .9, 1]).tolist()

# sizes and mask values (all images; cheap)
sizes, mvals, msizes, mismatch = collections.Counter(), collections.Counter(), collections.Counter(), 0
for s in rel:
    for n, a in rel[s]:
        with Image.open(root / "training" / "data" / s / "images" / n) as im:
            isz = im.size
            imode = im.mode
        with Image.open(root / "training" / "data" / s / "annotations" / a) as m:
            msz = m.size
            mm = m.mode
        sizes[(s, isz[0] // 10 * 10, isz[1] // 10 * 10, imode)] += 1
        msizes[mm] += 1
        if isz != msz:
            mismatch += 1
res["image_size_buckets"] = [[list(k), v] for k, v in sizes.most_common(12)]
res["mask_modes"] = dict(msizes)
res["image_mask_size_mismatch"] = mismatch
vals = collections.Counter()
for s in rel:
    for n, a in rel[s][::7]:
        m = np.asarray(Image.open(root / "training" / "data" / s / "annotations" / a))
        u, c = np.unique(m, return_counts=True)
        for x, y in zip(u, c):
            vals[int(x)] += int(y)
res["mask_values_sample_every7"] = dict(sorted(vals.items()))

# CSV coverage
csv_files = collections.defaultdict(list)
with open(root / "AnnotationsCombined.csv", newline="") as f:
    for r in csv.DictReader(f):
        csv_files[r["filename"]].append(r)
rel_all = set(names["train"]) | set(names["test"])
res["csv_files"] = len(csv_files)
res["release_in_csv"] = len(rel_all & set(csv_files))
res["release_not_in_csv"] = sorted(rel_all - set(csv_files))[:5]
nonrel = set(csv_files) - rel_all
def has_regions(rows):
    return any(r["region_shape_attributes"] not in ("{}", "") for r in rows)
res["csv_not_in_release"] = len(nonrel)
res["csv_not_in_release_with_regions"] = sum(has_regions(csv_files[f]) for f in nonrel)
res["release_with_csv_regions"] = sum(has_regions(csv_files[f]) for f in rel_all & set(csv_files))
# duplicates rows for same file across sessions of annotation (multiple region_count groups?)
dup_files = 0
for f, rows in csv_files.items():
    rc = {r["region_count"] for r in rows}
    if len(rc) > 1:
        dup_files += 1
res["csv_files_with_inconsistent_region_count"] = dup_files
cls_nonrel = collections.Counter()
for f in nonrel:
    for r in csv_files[f]:
        a = json.loads(r["region_attributes"] or "{}")
        if a:
            cls_nonrel[a.get("Defect_Class")] += 1
res["csv_not_in_release_region_classes"] = cls_nonrel.most_common()

# Test_Images relation
ti = sorted(p.name for p in (root / "Test_Images").iterdir())
res["test_images_n"] = len(ti)
res["test_images_in_release"] = len(set(ti) & rel_all)
res["test_images_in_csv"] = len(set(ti) & set(csv_files))
res["release_not_in_test_images"] = len(rel_all - set(ti))
res["csv_not_in_test_images"] = len(set(csv_files) - set(ti))
# byte-identical? compare md5 for 300 release images
same = diff = 0
for s in rel:
    for n, _ in rel[s][::40]:
        p1, p2 = root / "training" / "data" / s / "images" / n, root / "Test_Images" / n
        if p2.exists():
            if hashlib.md5(p1.read_bytes()).hexdigest() == hashlib.md5(p2.read_bytes()).hexdigest():
                same += 1
            else:
                diff += 1
res["release_vs_test_images_md5_same_diff"] = [same, diff]
# defect_percentages
dp = sorted((root / "defect_percentages").iterdir())
res["defect_percentages_n"] = len(dp)
res["defect_percentages_example"] = json.loads(dp[0].read_text())
dump(res, out)
print(json.dumps(res, indent=1, default=str)[:6000])
