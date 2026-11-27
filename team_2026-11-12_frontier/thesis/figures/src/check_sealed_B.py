"""Sealed-path check over fig_maker_B's read logs (logs_B/readlog_F*.tsv): every logged path must be free of the tokens
test50, e1_106, /e1/, _e1, and every per-cell file (image, mask, npz, cons) must name a P532 pool stem that is in no
sealed list (forbidden_v1.txt, legacy.json sealed sets) and whose cells.tsv bench_set is not test50 / e1_106."""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import figB_common as C  # noqa: E402


def main():
    P = C.pool()
    sealed = C._sealed()
    bs = {r["stem"]: r["bench_set"] for r in C.cells_rows()}
    tot, bad, per = 0, [], {}
    stems = set()
    for f in sorted(C.LOGS.glob("readlog_F*.tsv")):
        rows = list(csv.DictReader(open(f), delimiter="\t"))
        per[f.name] = len(rows)
        for r in rows:
            tot += 1
            p = r["path"]
            if any(t in p.lower() for t in C.SEALED_TOKENS):
                bad.append(("token", f.name, p))
            if r["kind"] in ("image", "mask_v11", "npz", "cons_npz"):
                st = Path(p).stem
                stems.add(st)
                if st not in P or st in sealed or bs.get(st) in ("test50", "e1_106"):
                    bad.append(("stem", f.name, p))
    print("read-log lines per figure:", per)
    print(f"total reads {tot}; distinct cell stems read {len(stems)}; all in P532: {stems <= P}; "
          f"overlap with sealed lists: {len(stems & sealed)}; violations: {len(bad)}")
    for b in bad[:20]:
        print("VIOLATION", b)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
