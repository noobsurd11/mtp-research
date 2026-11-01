"""p8_merge (found, 1 Nov 2026): final P8 pick from run1 (references, cached encoders, SAM2) + run2 (DINOv3 rows), the
pick rule of protocol_A8screen §2 applied to the union: candidate enters if F51 crack AP (2-seed mean) >= best cached CNN
reference - 0.02; DINOv3 ConvNeXt-T enters regardless (Om's named encoder). Descriptive table of all rows.
Usage: python p8_merge.py RUN1/p8_summary.json RUN2/p8_summary.json OUT.json"""
import json
import sys

import numpy as np

CNN_REFS = ("rn34_imagenet", "rn50_imagenet", "convnext_t_in1k")
summ, means = {}, {}
for f in sys.argv[1:3]:
    d = json.load(open(f))
    summ.update(d["summary"])
for tag, v in summ.items():
    if "F51" in v:
        means.setdefault(tag.split("/")[0], []).append(v["F51"]["crack_ap"])
means = {k: float(np.mean(v)) for k, v in means.items()}
ref = max(means[n] for n in CNN_REFS)
cands = [n for n in ("dinov3_cnx_t", "sam2_hiera_t") if n in means]
pick = sorted(set([n for n in cands if means[n] >= ref - 0.02] + ["dinov3_cnx_t"]))
rows = {tag: {k: {m: v[k].get(m) for m in ("crack_ap", "cell_auroc", "recall_at_pstar", "fa_px_crackfree_argmax", "inactive_ap")}
              for k in ("val", "F51", "H36", "F19") if k in v} for tag, v in summ.items()}
out = {"f51_crack_ap_mean": means, "best_cached_cnn_ref": ref, "bar": ref - 0.02, "pick": pick, "rows": rows}
json.dump(out, open(sys.argv[3], "w"), indent=1)
print(json.dumps({"f51_crack_ap_mean": {k: round(x, 3) for k, x in means.items()}, "ref": round(ref, 3), "pick": pick}, indent=1))
