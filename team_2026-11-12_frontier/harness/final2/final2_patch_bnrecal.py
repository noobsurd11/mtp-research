"""Candidate second fix for F2 (NOT committed; for the smoke with PATCH=1): src/trainers/weight_avg.py train_fold_loader
refuses 'train.txt overlaps val / test'; on the full-pool root val = test = training cells (the in-sample monitor), so the
step-20000 finalize (BN re-estimate of the averaged readouts) raises after the validation fix. Allowed here only when EVERY
val and test cell is a training cell (the condition of F2's eval fix); any partial overlap still raises. The loader (stems,
order, transform) is unchanged. Usage: python final2_patch_bnrecal.py <path of weight_avg.py>"""
import sys
from pathlib import Path

p = Path(sys.argv[1])
t = p.read_text()
a = '    if set(stems) & held:\n        raise ValueError("training.bn_recal: train.txt overlaps val / test")\n'
b = ('    if set(stems) & held and not held <= set(stems):   # F2: the in-sample monitor (val / test all train cells) is allowed\n'
     '        raise ValueError("training.bn_recal: train.txt overlaps val / test")\n')
assert t.count(a) == 1, "anchor not found"
p.write_text(t.replace(a, b))
print(f"patched {p}")
