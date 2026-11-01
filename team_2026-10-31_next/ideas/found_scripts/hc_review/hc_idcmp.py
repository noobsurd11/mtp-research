"""found, 1 Nov 2026 (HC review): compare identity_cpu.py records (builder harness 962379a6).
IDENTICAL iff loss_class, n_params, init_state, class_counts_sha, fixed_batch stems/image/mask bytes and every
step out (loss repr), lr, state hash (all params + buffers), logits hash, logits shape are equal.
fixed_batch.keys is reported separately: el_hc adds the sample key 'synth' by design (benchmark_el.py +7)."""
import json
import sys

KEYS = ("loss_class", "n_params", "init_state", "class_counts_sha")
STEP_KEYS = ("out", "lr", "state", "logits", "logits_shape")
args = sys.argv[1:]
for a, b in zip(args[::2], args[1::2]):
    A, B = json.load(open(a)), json.load(open(b))
    d = [k for k in KEYS if A.get(k) != B.get(k)]
    fa, fb = A["fixed_batch"], B["fixed_batch"]
    d += ["fixed_batch." + k for k in ("stems", "image", "mask") if fa.get(k) != fb.get(k)]
    if len(A["steps"]) != len(B["steps"]):
        d.append("n_steps")
    nsame = 0
    for i, (x, y) in enumerate(zip(A["steps"], B["steps"])):
        bad = [k for k in STEP_KEYS if x.get(k) != y.get(k)]
        d += ["step%s.%s" % (x.get("step", i), k) for k in bad]
        nsame += not bad
    extra = sorted(set(fa.get("keys", [])) ^ set(fb.get("keys", [])))
    na, nb = a.rsplit("/", 1)[-1], b.rsplit("/", 1)[-1]
    verdict = "IDENTICAL" if not d else "DIFFER " + str(d[:8])
    print("%s vs %s: %s; steps equal %d/%d; batch keys sym-diff %s" % (na, nb, verdict, nsame, len(A["steps"]), extra))
