"""Shared helpers for the 27 Nov CPU analyses (team_2026-11-27_arch/cpu). gaint CPU only, nice 19.
Imports the reviewed read tree bench_wt_final (89b9ea5) read-only; run with PYTHONDONTWRITEBYTECODE=1 so nothing is
written there. Inputs: the relayed cv02 dumps of the cv5v3 held-out folds only (open sets; sealed sets are refused by
bench/w1read._load_run and dumpfmt). No training, no GPU.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

RT = Path("/home/noob/work/bench_wt_final")
REV = "89b9ea5a12a37a87c16c4868cc4adf00794a7610"
sys.path.insert(0, str(RT))
os.environ.setdefault("OMP_NUM_THREADS", "1")

from bench import cellmeta, w1read  # noqa: E402

RLY = Path("/home/noob/work/bench_relay")
MX = "hrnet_w18_unetpp_swad_const_pf_v11"
G3 = Path("/home/noob/work/bench_data_v3b/meta/cv5v3_groups.tsv")
OUT = Path("/home/noob/work/bench_reads/x4_cpu")


def check_tree() -> None:
    h = subprocess.run(["git", "-C", str(RT), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    d = subprocess.run(["git", "-C", str(RT), "status", "--porcelain", "-uno"], capture_output=True, text=True).stdout
    assert h == REV and not d.strip(), f"{RT} not at {REV[:7]} or has tracked changes"


def combo_set_dir(k: int, s: int) -> Path:
    """COMBO = c3x HRNet-W18 U-Net++ PF + SWAD, swad readout (the x4 comparator), held-out fold k, seed s."""
    run = f"c3x_hrnet_swad_v11_f{k}_s{s}"
    assert (RLY / "c3x" / ".ok" / run).exists(), f"{run} not relayed"
    return RLY / "c3x" / run / "dumps" / "elbench1" / MX / f"{run}.swad" / f"cv5v3_f{k}"


def combo_runs(seeds) -> list:
    """w1read.Run objects (manifest md5s verified, set = cv5v3_f<k>, labels v1.1) for the given seeds, folds 0 to 4."""
    runs = []
    for s in seeds:
        for k in range(5):
            r = w1read._load_run("COMBO", combo_set_dir(k, s), "v11")
            assert r.set_name == f"cv5v3_f{k}" and r.seed == s and r.manifest["weights_key"] == "swad"
            assert r.manifest["set_kind"] == "open" and r.manifest["precision"] == "fp32" and r.manifest["step"] == 20000
            runs.append(r)
    return runs


def groups() -> dict:
    return cellmeta.load_groups(G3)
