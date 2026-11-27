"""T3b build pre-check (review round 1 N8): decode and check all 106 E1 training labels IN MEMORY before anything is written
to IO/data. Run by t3b_queue.sh build only, after the registration (it decodes E1 masks and ignore maps).
For every E1 stem of the registered list: md5 of images/, masks/, ignore/<s>.png = the line of reg/e1_files.md5 (the
registration's hashes) before the file is opened; then K's bench/t3b_labels.map_e1 (the function K's builder uses) on the
decoded mask and ignore map. Writes nothing; prints one line; rc 0 only if all 106 pass.
Usage: python t3b_label_precheck.py <K worktree> <E1 dir> <reg/e1_files.md5> <reg/lists/e1_106_stems.txt>
"""
import hashlib
import sys
from pathlib import Path

import numpy as np
from PIL import Image


def main(argv):
    repo, e1d, man_p, lst = Path(argv[0]), Path(argv[1]), Path(argv[2]), Path(argv[3])
    sys.path.insert(0, str(repo))
    from bench import t3b_labels
    man = {}
    for l in open(man_p):
        if l.strip():
            h, p = l.split(None, 1)
            man[p.strip()] = h
    stems = [l.strip() for l in open(lst) if l.strip()]
    assert len(stems) == 106 and set(man) == {f"{d}/{s}.png" for s in stems for d in ("images", "masks", "ignore")}, "manifest / list"
    bad, n255 = [], 0
    for s in stems:
        for d in ("images", "masks", "ignore"):
            if hashlib.md5((e1d / d / f"{s}.png").read_bytes()).hexdigest() != man[f"{d}/{s}.png"]:
                sys.exit(f"label precheck: {d}/{s}.png differs from the registration (nothing written)")
        try:
            t, c = t3b_labels.map_e1(np.array(Image.open(e1d / "masks" / f"{s}.png")), np.array(Image.open(e1d / "ignore" / f"{s}.png")))
            n255 += int(c["ignore_px"] > 0)
        except ValueError as e:
            bad.append(f"{s}: {e}")
    if bad:
        sys.exit(f"label precheck: {len(bad)} of 106 cells refused (nothing written), e.g. {bad[:2]}")
    print(f"label precheck: 106 of 106 E1 cells map to training labels = the scoring view (in memory; nothing written); "
          f"cells with ignore px {n255}")


if __name__ == "__main__":
    main(sys.argv[1:])
