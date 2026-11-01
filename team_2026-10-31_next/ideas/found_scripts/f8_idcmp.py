"""found, 31 Oct 2026: compare two identity_cpu.py records (builder's harness): IDENTICAL iff loss_class, n_params,
init_state, class_counts_sha, fixed_batch and every step's out (loss repr), lr, state hash and logits hash are equal.
Usage: python f8_idcmp.py A.json B.json [C.json D.json ...] (pairs)"""
import json
import sys

KEYS = ("loss_class", "n_params", "init_state", "class_counts_sha", "fixed_batch")
args = sys.argv[1:]
for a, b in zip(args[::2], args[1::2]):
    A, B = json.load(open(a)), json.load(open(b))
    diffs = [k for k in KEYS if A.get(k) != B.get(k)]
    if len(A["steps"]) != len(B["steps"]):
        diffs.append("n_steps")
    for i, (x, y) in enumerate(zip(A["steps"], B["steps"])):
        for k in ("out", "lr", "state", "logits", "logits_shape"):
            if x.get(k) != y.get(k):
                diffs.append(f"step{x.get('step', i)}.{k}")
    print(f"{a.rsplit('/', 1)[-1]} vs {b.rsplit('/', 1)[-1]}: {'IDENTICAL' if not diffs else 'DIFFER ' + str(diffs[:6])} "
          f"({len(A['steps'])} steps; losses {[s['out'] for s in A['steps']][:5]})")
