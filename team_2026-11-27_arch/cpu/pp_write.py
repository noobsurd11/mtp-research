"""Task 1, step 2: write the post-processed COMBO dumps (arm PPCC, POST-HOC) with the cross-fitted L and A of
OUT/pp/choices.json: fold k of seed s gets the (L, A) chosen on the other four folds of seed s (pp_sweep.py).
Each derived dump = the source dump with pp_sweep.apply_pp applied, written by dumpfmt.write_cell (validated, refuses to
overwrite); manifest = the source manifest with run_id '<source run_id>.ppcc', plus 'derivation' and 'derived_from'.
Writer / device / checkpoint fields are the source's (the read must see one GPU model and one writer; the derivation key
records the change). Output: OUT/pp_dumps/elbench1/<method>/<run_id>.ppcc/cv5v3_f<k>/.

  PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES= nice -n 19 <venv python> pp_write.py --seeds 5,6 --workers 8
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from multiprocessing import get_context
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cpu_common as C  # noqa: E402
import pp_sweep as PP  # noqa: E402
from bench import dumpfmt  # noqa: E402


def _w(a):
    src, dst, stem, L, A = a
    d = dumpfmt.read_cell(Path(src) / f"{stem}.npz", check=True)
    q = PP.apply_pp(d, L, A)
    return stem, dumpfmt.write_cell(Path(dst) / f"{stem}.npz", **q)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", default="5,6")
    ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()
    C.check_tree()
    ch = json.loads((C.OUT / "pp" / "choices.json").read_text())
    pp_md5 = hashlib.md5((Path(__file__).resolve().parent / "pp_sweep.py").read_bytes()).hexdigest()
    pool = get_context("fork").Pool(a.workers)
    for r in C.combo_runs([int(x) for x in a.seeds.split(",")]):
        c = ch[f"s{r.seed}_f{r.fold}"]
        rid = f"{r.run_id}.ppcc"
        dst = C.OUT / "pp_dumps" / "elbench1" / C.MX / rid / r.set_name
        assert not dst.exists(), f"refuse: {dst} exists"
        dst.mkdir(parents=True)
        res = dict(pool.map(_w, [(str(r.set_dir), str(dst), s, c["L"], c["A"]) for s in r.stems], chunksize=2))
        meta = {k: v for k, v in r.manifest.items()
                if k not in ("format", "n_cells", "cells", "ties_total", "bytes_total", "written")}
        meta["run_id"] = rid
        meta["derivation"] = (f"ppcc: crack comps (8-conn) with skeleton length < {c['L']} px -> oth; inactive comps < "
                              f"{c['A']} px -> 0; L, A cross-fitted on the other 4 folds of seed {r.seed} (post-hoc arm)")
        meta["derived_from"] = {"set_dir": str(r.set_dir), "manifest_md5": r.manifest_md5, "pp_sweep_md5": pp_md5,
                                "L": c["L"], "A": c["A"]}
        dumpfmt.write_manifest(dst, meta, {s: res[s] for s in r.stems})
        print(f"wrote {dst} ({len(res)} cells; L={c['L']} A={c['A']})", flush=True)
    pool.close(); pool.join()
    return 0


if __name__ == "__main__":
    sys.exit(main())
