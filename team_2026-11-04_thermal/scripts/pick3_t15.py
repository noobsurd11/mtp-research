#!/usr/bin/env python3
"""pick3_t15.py: T15 readout on the A1 EL-derived cell dark I-V files (plan_pick3.md section 3.1).

Run (after plan v1 is frozen):
  ~/mtp/research/.venv/bin/python -I scripts/pick3_t15.py --dir <darkIV folder> --out pick3/out --discover
  ~/mtp/research/.venv/bin/python -I scripts/pick3_t15.py --dir <darkIV folder> --out pick3/out --run

--discover prints format facts only (shape, header tokens, which axis is current, current levels);
it prints no cell voltage statistics.
--run applies the frozen rules: P = cell voltage at the highest current; d = module median P - P;
valid 0.3 < P < 0.8 V; coverage; spread (robust SD of d, share d >= 1 V_t); kill; labels D90, DVt.
"""
import argparse
import glob
import json
import os
import re
import sys

import numpy as np

VT = 0.0257  # thermal voltage at 25 C, volts (plan 3.1)
_SPLIT = re.compile(r"[\s,;]+")


def parse(path):
    header, rows = [], []
    for line in open(path, "r", errors="replace"):
        toks = [t for t in _SPLIT.split(line.strip()) if t]
        if not toks:
            continue
        try:
            rows.append([float(t) for t in toks])
        except ValueError:
            header.append(toks)
    lens = np.array([len(r) for r in rows])
    mode = int(np.bincount(lens).argmax())
    M = np.array([r for r in rows if len(r) == mode], dtype=np.float64)
    return header, M, int((lens != mode).sum())


def orient(M):
    """Return (currents[n_levels], V[n_levels, n_cells], description).
    Heuristic: one column (or row) is the current axis: non-negative, monotone, max well above 0.8
    or not inside the voltage band; the other entries are cell voltages."""
    def is_current(v):
        v = np.asarray(v)
        mono = np.all(np.diff(v) >= 0) or np.all(np.diff(v) <= 0)
        return mono and np.nanmax(v) > 1.0 and np.nanmin(v) >= 0
    # rows = levels, first column = current
    if M.shape[1] >= 2 and is_current(M[:, 0]):
        return M[:, 0], M[:, 1:], "rows=current levels, col0=current, cols1..=cells"
    if M.shape[0] >= 2 and is_current(M[0, :]):
        return M[0, :], M[1:, :].T, "row0=current levels, rows1..=cells"
    # cells in rows with a leading cell index column?
    if M.shape[1] >= 3 and np.allclose(M[:, 0], np.arange(1, M.shape[0] + 1)):
        return None, M[:, 1:].T, "col0=cell index; no current axis found"
    return None, None, "unrecognised"


def serial_of(path):
    m = re.match(r"(\d+)_", os.path.basename(path))
    return m.group(1) if m else os.path.basename(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    ap.add_argument("--out", required=True)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--discover", action="store_true")
    g.add_argument("--run", action="store_true")
    a = ap.parse_args()
    files = sorted(glob.glob(os.path.join(a.dir, "*EL-derived*cell*dark*I-V*.txt")))
    os.makedirs(a.out, exist_ok=True)
    if a.discover:
        facts = []
        for p in files[:3]:
            h, M, dropped = parse(p)
            cur, V, desc = orient(M)
            facts.append({"file": os.path.basename(p), "header_tokens": [t[:8] for t in h[:3]],
                          "matrix_shape": list(M.shape), "rows_dropped": dropped, "orientation": desc,
                          "n_levels": None if cur is None else int(len(cur)),
                          "n_cells": None if V is None else int(V.shape[1]),
                          "current_levels_A": None if cur is None else [round(float(c), 4) for c in cur]})
        shapes = {}
        for p in files:
            _, M, _ = parse(p)
            shapes[str(M.shape)] = shapes.get(str(M.shape), 0) + 1
        out = {"n_files": len(files), "shape_counts": shapes, "first_files": facts}
        json.dump(out, open(os.path.join(a.out, "t15_discover.json"), "w"), indent=1)
        print(json.dumps(out, indent=1))
        return
    # --run
    per_cell = []
    fmt = {}
    for p in files:
        s = serial_of(p)
        h, M, _ = parse(p)
        names = h[0] if h else []
        paired = (M.shape[1] == 72 and len(names) == 72 and
                  all(names[2 * c].startswith("voltage_(V)_Cell") and names[2 * c + 1].startswith("current_(A)_Cell")
                      for c in range(36)))
        if paired:
            # layout found at discovery: 36 (voltage, current) column pairs, one row per current level
            Vm, Im = M[:, 0::2], M[:, 1::2]
            desc = "paired: 36 x (voltage_(V)_CellN, current_(A)_CellN), rows = current levels"
            P = np.array([Vm[int(np.nanargmax(Im[:, c])), c] for c in range(36)])
            kmax = [float(np.nanmax(Im[:, c])) for c in range(36)]
            fmt[desc] = fmt.get(desc, 0) + 1
            fmt.setdefault("max_current_per_file_A", []).append(round(float(np.median(kmax)), 4))
        else:
            cur, V, desc = orient(M)
            fmt[desc] = fmt.get(desc, 0) + 1
            if V is None or cur is None:
                for c in range(36):
                    per_cell.append((s, c + 1, np.nan, False))
                continue
            k = int(np.nanargmax(cur))
            P = V[k, :]
        for c, v in enumerate(P[:36]):
            valid = bool(np.isfinite(v) and 0.3 < v < 0.8)
            per_cell.append((s, c + 1, float(v), valid))
        for c in range(len(P), 36):
            per_cell.append((s, c + 1, np.nan, False))
    serials = sorted({r[0] for r in per_cell})
    # deficit d = module median P - P over valid cells
    d = {}
    for s in serials:
        vals = np.array([r[2] for r in per_cell if r[0] == s and r[3]])
        med = np.median(vals) if len(vals) else np.nan
        for r in per_cell:
            if r[0] == s:
                d[(s, r[1])] = (med - r[2]) if r[3] else np.nan
    dv = np.array([v for v in d.values() if np.isfinite(v)])
    n_total = len(files) * 36
    coverage = len(dv) / n_total if n_total else float("nan")
    mad = np.median(np.abs(dv - np.median(dv)))
    rsd = 1.4826 * mad
    share_vt = float(np.mean(dv >= VT))
    no_spread = (rsd < 0.1 * VT) and (share_vt < 0.01)
    kill = (coverage < 0.5) or no_spread
    p90 = float(np.percentile(dv, 90))
    with open(os.path.join(a.out, "t15_cells.tsv"), "w") as f:
        f.write("serial\tcell\tP_V\tvalid\td_V\tD90\tDVt\n")
        for r in per_cell:
            dd = d[(r[0], r[1])]
            f.write(f"{r[0]}\t{r[1]}\t{r[2]}\t{int(r[3])}\t{dd}\t"
                    f"{int(np.isfinite(dd) and dd >= p90)}\t{int(np.isfinite(dd) and dd >= VT)}\n")
    mc = fmt.pop("max_current_per_file_A", [])
    if mc:
        fmt["max_current_A_min_median_max"] = [min(mc), float(np.median(mc)), max(mc)]
    summ = {"rule": "plan_pick3.md v1.2 (md5 2893a817) section 3.1", "formats": fmt, "n_files": len(files),
            "n_cells_total": n_total, "n_valid": int(len(dv)), "coverage": coverage,
            "robust_sd_d_V": float(rsd), "robust_sd_d_in_Vt": float(rsd / VT),
            "share_d_ge_1Vt": share_vt, "no_spread": bool(no_spread),
            "kill_T15": bool(kill), "d_p90_V": p90,
            "n_D90": int(np.sum(dv >= p90)), "n_DVt": int(np.sum(dv >= VT))}
    json.dump(summ, open(os.path.join(a.out, "t15_summary.json"), "w"), indent=1)
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
