"""Wave 2a gates: shared paths and helpers (builder, 17 Nov 2026). CPU only. Reads checkpoints, logs and dumps; writes
only into the --out folder of the calling gate (a new folder; refuses if it exists). No file of any worktree is changed.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from pathlib import Path

W = Path("/home/noob/work")
W2 = W / "bench_wt_w2"                      # training tree of wave 2a, c57508e
ELB = W / "el_bench"                        # training tree of W1-G, 31c0c36
RB = W / "bench_wt_b"                       # reviewed read tools, b5bf0ae
EXP_W2A = W2 / "experiments"
EXP_PF = ELB / "experiments"
DUMPS_W2A = W / "bench_dumps/w2a/elbench1"
DUMPS_PF = W / "bench_dumps/w1g/elbench1/house_r34_unetpp_pf_v11"
FOLDS = (0, 1, 2, 3, 4)
SEEDS = (5, 6)
STEP_RX = re.compile(r"step (\d+)/(\d+)\s+loss=([0-9.eE+-]+)\s")
PROBE_RX = re.compile(r"ENC probe step (\d+)\s+(.*)$")
PROBE_ST = re.compile(r"(\w+): cos=([0-9.eE+-]+) nr=([0-9.eE+-]+) dev=([0-9.eE+-]+)")


def guard_env() -> None:
    """Refuse to run with a visible GPU or with bytecode writing on (the worktrees must stay clean)."""
    if os.environ.get("CUDA_VISIBLE_DEVICES", None) != "":
        sys.exit('refuse: run with CUDA_VISIBLE_DEVICES="" (CPU only)')
    if os.environ.get("PYTHONDONTWRITEBYTECODE") != "1":
        sys.exit("refuse: run with PYTHONDONTWRITEBYTECODE=1")


def new_out(path: str) -> Path:
    out = Path(path)
    if out.exists():
        sys.exit(f"refuse: output folder exists: {out}")
    out.mkdir(parents=True)
    return out


class Report:
    """Lines go to stdout and, at close, to <out>/<name>.txt; numbers to <out>/<name>.json; the verdict to <out>/VERDICT."""

    def __init__(self, out: Path, name: str) -> None:
        self.out, self.name, self.lines = out, name, []

    def p(self, s: str = "") -> None:
        print(s, flush=True)
        self.lines.append(s)

    def close(self, doc: dict, verdict: str) -> None:
        assert verdict in ("PASS", "FAIL", "OPEN"), verdict
        for f, text in ((f"{self.name}.txt", "\n".join(self.lines) + "\n"),
                        (f"{self.name}.json", json.dumps(doc, indent=1)), ("VERDICT", f"{self.name} {verdict}\n")):
            p = self.out / f
            if p.exists():
                sys.exit(f"refuse: {p} exists")
            p.write_text(text)


def md5_file(p: Path) -> str:
    h = hashlib.md5()
    with open(p, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def pf_run(k: int, s: int) -> Path:
    return EXP_PF / f"w1g_pf_v11_f{k}_s{s}"


def w2a_run(arm: str, k: int, s: int) -> Path:
    return EXP_W2A / f"w2a_{arm}_f{k}_s{s}"


def load_ckpt(run: Path) -> dict:
    """latest.pth of a run (the file scripts/bench_infer.py dumps from), on the CPU. Asserts step = total_steps."""
    import torch
    st = torch.load(run / "checkpoints" / "latest.pth", map_location="cpu", weights_only=False)
    assert int(st["step"]) == int(st["cfg"]["training"]["total_steps"]) == 20000, (run, st["step"])
    return st


def loss_lines(run: Path) -> dict[int, float]:
    """{step: loss} from the trainer's 'step N/20000  loss=...' lines of train.log (one line per log_every = 50 steps;
    the value is the mean loss of the 50 steps ending at N, printed with 4 significant digits). Last line per step."""
    out = {}
    for line in open(run / "train.log", errors="replace"):
        m = STEP_RX.search(line)
        if m:
            assert int(m.group(2)) == 20000, (run, line)
            out[int(m.group(1))] = float(m.group(3))
    return out


def curve(run: Path) -> dict[int, float]:
    """{step: loss} from metrics.json train_curve (the same windows at full precision)."""
    d = json.loads((run / "metrics.json").read_text())
    return {int(r["step"]): float(r["loss"]) for r in d["train_curve"]}, int(d.get("resumes") or 0)


def probe_rows(run: Path) -> dict[int, dict]:
    """{step: stages} from <run>/enc_probe.jsonl (last row per step, as the probe's module doc says)."""
    out = {}
    for line in open(run / "enc_probe.jsonl"):
        if line.strip():
            r = json.loads(line)
            out[int(r["step"])] = r["stages"]
    return out


def probe_log(run: Path) -> dict[int, dict]:
    """{step: {stage: {cos, nr, dev}}} from the 'ENC probe step' lines of train.log (4 decimals). Last line per step."""
    out = {}
    for line in open(run / "train.log", errors="replace"):
        m = PROBE_RX.search(line)
        if m:
            out[int(m.group(1))] = {s: {"cos": float(c), "nr": float(n), "dev": float(d)}
                                    for s, c, n, d in PROBE_ST.findall(m.group(2))}
    return out


def manifest_ckpt_md5(run_dump: Path) -> str | None:
    """checkpoint_md5 of a dump's manifest (<method>/<run id>/<set>/manifest.json), None if the dump does not exist."""
    ms = sorted(run_dump.glob("*/manifest.json")) if run_dump.is_dir() else []
    return json.loads(ms[0].read_text())["checkpoint_md5"] if len(ms) == 1 else None
