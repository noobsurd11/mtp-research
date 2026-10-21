"""SK1 protocol_v2 §7: compare a new-code absh-off run's log with the reference run's log up to a step.

Compares, line by line, every training log line ("step N/T  k=v ...") and every val line ("val @ step N ...") with
N <= --upto. Timestamps and timing fields (steps_per_sec) are dropped; every other field must be equal as text.
Usage: python sk1_identity_diff.py <new.stdout> <reference.stdout> [--upto 2500]
"""
import re
import sys

TIMING = {"steps_per_sec"}


def lines(path, upto):
    out = []
    for ln in open(path, errors="replace"):
        m = re.search(r"(step (\d+)/\d+\s+.*|val @ step (\d+)\s+.*)$", ln.rstrip("\n"))
        if not m:
            continue
        n = int(m.group(2) or m.group(3))
        if n > upto:
            continue
        body = m.group(1)
        if body.startswith("step"):
            head, _, rest = body.partition("  ")
            kv = [f for f in rest.split() if f.split("=")[0] not in TIMING]
            body = head + "  " + " ".join(kv)
        out.append(body)
    return out


def main():
    new, ref = sys.argv[1], sys.argv[2]
    upto = int(sys.argv[sys.argv.index("--upto") + 1]) if "--upto" in sys.argv else 2500
    a, b = lines(new, upto), lines(ref, upto)
    n = min(len(a), len(b))
    diffs = [(i, x, y) for i, (x, y) in enumerate(zip(a, b)) if x != y]
    print(f"new {len(a)} lines, ref {len(b)} lines (<= step {upto}); differing: {len(diffs)}")
    for i, x, y in diffs[:5]:
        print(f"  #{i}\n    new: {x}\n    ref: {y}")
    ok = not diffs and len(a) == len(b) and n > 0
    print("IDENTICAL" if ok else "DIFFERENT")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
