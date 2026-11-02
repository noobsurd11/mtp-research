"""judge b6_root_check (2 Nov 2026): builder's 5 B6 fold roots vs coach's frozen folds (b6_folds.tsv e2cafce1) and judge's groups
(b6_groups.tsv 5ff33e20). Names only (split lists, manifests); no image, mask or prediction.
Usage: python3 b6_root_check.py ROOTS_DIR (r0..r4 with train/val/test.txt + SPLITS.md5; el_{train,val,test}.txt; e1_{stems,eval}.txt;
       DATA_MANIFEST.md5) FOLDS.tsv GROUPS.tsv
"""
import hashlib
import sys
from collections import defaultdict
from pathlib import Path

D, FOLDS, GROUPS = Path(sys.argv[1]), sys.argv[2], sys.argv[3]
rd = lambda p: [l.strip() for l in open(p) if l.strip()]
tr, va, te = rd(D / "el_train.txt"), rd(D / "el_val.txt"), rd(D / "el_test.txt")
e1 = set(rd(D / "e1_stems.txt")) | set(rd(D / "e1_eval.txt"))
forb = set(te) | e1
fold = {}; fgrp = {}
for r in [l.rstrip("\n").split("\t") for l in open(FOLDS)][1:]:
    fold[r[0]] = int(r[3]); fgrp[r[0]] = r[2]
grp = {r[0]: r[3] for r in [l.rstrip("\n").split("\t") for l in open(GROUPS)][1:]}
bad = []
ok = lambda c, msg: c or bad.append(msg)
ok(len(fold) == 532 and set(fold) == set(tr) | set(va), "folds != train u val")
ok(set(grp) == set(fold), "groups stems != folds stems")
ok(all(fgrp[s] == grp[s] for s in fold), "phys_group column != judge groups")
gf = defaultdict(set)
for s in fold:
    gf[grp[s]].add(fold[s])
ok(all(len(v) == 1 for v in gf.values()), f"groups split across folds: {[g for g, v in gf.items() if len(v) > 1][:5]}")
held = []
for k in range(5):
    R = D / f"r{k}"
    t, v, x = rd(R / "train.txt"), rd(R / "val.txt"), rd(R / "test.txt")
    fk = {s for s in fold if fold[s] == k}
    ok(v == x, f"root {k}: val.txt != test.txt")
    ok(set(v) == fk and len(v) == len(fk), f"root {k}: held-out != fold {k}")
    ok(set(t) == set(fold) - fk and len(t) == len(set(t)), f"root {k}: train != other 4 folds")
    ok(not (set(t) & set(v)), f"root {k}: train / held-out overlap")
    ok(not ((set(t) | set(v)) & forb), f"root {k}: TEST or E1 stem present")
    order = [s for s in tr if s in set(t)] + [s for s in va if s in set(t)]
    ok(t == order, f"root {k}: train order != train.txt then val.txt order")
    md = {l.split()[1]: l.split()[0] for l in open(R / "SPLITS.md5") if l.strip()}
    for n in ("train.txt", "val.txt", "test.txt"):
        h = hashlib.md5(open(R / n, "rb").read()).hexdigest()
        key = [kk for kk in md if kk.endswith(n)]
        ok(key and md[key[0]] == h, f"root {k}: SPLITS.md5 mismatch {n}")
    held += v
    grps_k = {grp[s] for s in v}
    print(f"root {k}: train {len(t)} held-out {len(v)} (= fold {k}: {len(fk)}) groups {len(grps_k)} test/E1 0 val==test {v == x}")
ok(sorted(held) == sorted(fold), "union of held-out != 532 / duplicates")
man = [l.split()[1] for l in open(D / "DATA_MANIFEST.md5") if l.strip()]
stems_m = {Path(p).stem for p in man}
ok(len(man) == 1064 and stems_m == set(fold), "DATA_MANIFEST != 532 stems x (image, mask)")
ok(not (stems_m & forb), "DATA_MANIFEST has a TEST or E1 stem")
ok({str(Path(p).parent) for p in man} == {"labeled/images", "labeled/masks_escdd"}, "DATA_MANIFEST dirs")
print(f"held-out union {len(held)} unique {len(set(held))}; groups {len(gf)} split 0; DATA_MANIFEST {len(man)} lines, stems {len(stems_m)}, forbidden 0")
print("FAIL:", bad) if bad else print("ALL CHECKS PASS")
