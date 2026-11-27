"""layered_ci pathfinder check (w2b builder, 17 Nov 2026). CPU only, reads logs, one dump folder and the fold-0
held-out masks (open: val = test = cv5v2 fold 0). Prints PASS / FAIL per criterion and one overall line; writes nothing
unless --out is given (then the same text to that file).

Criteria (cards/T10_rare_classes_spec.md arm 3, "Pathfinder: fold 0, seed 5, 20k steps on gaint. Pass: finite loss;
step time <= 1.15x and peak memory <= +1 GB vs the baseline smoke; the layer's held-out fold-0 region Dice >= 0.3 at
20k. Not used to rank."):
  C1 finite loss: every 'step N/20000  loss=X ...' line of the pathfinder's train.log has finite loss, loss_sup and loss_aux,
     the last line is step 20000, and checkpoints/latest.pth holds step 20000.
  C2 step time: steps_per_sec of the layered_ci smoke >= PF smoke / 1.15 (same smoke queue w2b_smoke, run one after the
     other at MAXC 1, value of the step-200 line = mean over steps 1 to 200). Beside it (descriptive, not the criterion):
     the pathfinder's step-20000 steps_per_sec against W1-G w1g_pf_v11_f0_s5 (other load on the GPU differs).
  C3 peak memory: gpumem.log peak of smoke_w2b_lci_f0_s5 <= peak of smoke_w2b_pf_f0_s5 + 1024 MiB.
  C4 region Dice: from the pathfinder's layered dump (p_inact = sigmoid of the layer, float16): L = p_inact > 0.5 on the
     107 fold-0 held-out cells; T = inact_region_fill(strict held-out mask) (the training target rule); pooled Dice
     2 |L & T| / (|L| + |T|) >= 0.3.
Usage: python lci_pathfinder_check.py [--repo R] [--smoke-q Q] [--path-q Q] [--dumps D] [--out FILE]
"""
from __future__ import annotations

import argparse
import math
import re
import sys
from pathlib import Path

import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("--repo", default="/home/noob/work/bench_wt_w2b")
ap.add_argument("--smoke-q", default="/home/noob/work/bq/w2b_smoke")
ap.add_argument("--dumps", default="/home/noob/work/bench_dumps/w2b/elbench1/layered_ci_pf_v11")
ap.add_argument("--w1g", default="/home/noob/work/el_bench/experiments/w1g_pf_v11_f0_s5")
ap.add_argument("--root", default="/home/noob/work/bench_data/roots/cv5v2_v11_f0")
ap.add_argument("--run", default="w2b_lcipath_f0_s5")
ap.add_argument("--out", default=None)
a = ap.parse_args()
sys.path.insert(0, a.repo)
from bench import dumpfmt  # noqa: E402
from src.data.aux_targets import inact_region_fill  # noqa: E402
from src.data.benchmark_el import load_index_mask  # noqa: E402

L: list[str] = []
ok_all = True


def say(s: str) -> None:
    L.append(s)
    print(s, flush=True)


def verdict(name: str, ok: bool | None, detail: str) -> None:
    global ok_all
    if ok is None:
        say(f"{name} OPEN: {detail}")
        ok_all = False
        return
    ok_all &= ok
    say(f"{name} {'PASS' if ok else 'FAIL'}: {detail}")


STEP = re.compile(r"step (\d+)/(\d+)\s+(.*)$")


def step_lines(log: Path) -> list[tuple[int, dict]]:
    out = []
    for ln in log.read_text().splitlines():
        m = STEP.search(ln)
        if m:
            kv = dict(x.split("=", 1) for x in m.group(3).split() if "=" in x)
            out.append((int(m.group(1)), {k: float(v) for k, v in kv.items()}))
    return out


repo = Path(a.repo)
run = repo / "experiments" / a.run
# C1
log = run / "train.log"
if not log.exists():
    verdict("C1 finite loss", None, f"{log} missing")
else:
    rows = step_lines(log)
    bad = [s for s, d in rows if not all(math.isfinite(d.get(k, float("nan"))) for k in ("loss", "loss_sup", "loss_aux"))]
    last = rows[-1][0] if rows else None
    step_ck = None
    ck = run / "checkpoints" / "latest.pth"
    if ck.exists():
        import torch
        step_ck = int(torch.load(ck, map_location="cpu", weights_only=False).get("step", -1))
    verdict("C1 finite loss", not bad and last == 20000 and step_ck == 20000,
            f"{len(rows)} step lines, non-finite at {bad[:5]}, last line step {last}, latest.pth step {step_ck}")
    if rows:
        say(f"   pathfinder step 20000: {' '.join(f'{k}={v:.4g}' for k, v in rows[-1][1].items())}")


# C2, C3 from the smoke queue
def smoke_sps(name: str) -> float | None:
    p = repo / "experiments" / name / "train.log"
    if not p.exists():
        return None
    r = [d for s, d in step_lines(p) if s == 200]
    return r[-1].get("steps_per_sec") if r else None


def smoke_peak(name: str) -> int | None:
    g = Path(a.smoke_q) / "gpumem.log"
    if not g.exists():
        return None
    v = [int(x) for x in re.findall(rf"run_name={re.escape(name)}:(\d+)", g.read_text())]
    return max(v) if v else None


sp, sl = smoke_sps("smoke_w2b_pf_f0_s5"), smoke_sps("smoke_w2b_lci_f0_s5")
verdict("C2 step time", None if sp is None or sl is None else sl >= sp / 1.15,
        f"smoke steps/s PF {sp}, layered_ci {sl} (need >= PF / 1.15 = {None if sp is None else round(sp / 1.15, 4)})")
w1 = step_lines(Path(a.w1g) / "train.log") if (Path(a.w1g) / "train.log").exists() else []
pr = step_lines(log) if log.exists() else []
if w1 and pr:
    say(f"   descriptive: steps/s at step 20000, pathfinder {pr[-1][1].get('steps_per_sec')} vs W1-G f0 s5 "
        f"{w1[-1][1].get('steps_per_sec')} (GPU load differs between the two)")
pp, pl = smoke_peak("smoke_w2b_pf_f0_s5"), smoke_peak("smoke_w2b_lci_f0_s5")
verdict("C3 peak memory", None if pp is None or pl is None else pl <= pp + 1024,
        f"gpumem peak MiB PF smoke {pp}, layered_ci smoke {pl} (limit PF + 1024)")

# C4
dd = Path(a.dumps) / a.run / "cv5v2_f0"
stems = (Path(a.root) / "splits" / "val.txt").read_text().split()
assert stems == (Path(a.root) / "splits" / "test.txt").read_text().split() and len(stems) == 107
if not (dd / "manifest.json").exists():
    verdict("C4 region Dice", None, f"{dd} has no manifest")
else:
    import json
    man = json.loads((dd / "manifest.json").read_text())
    assert man["decision_rule"] == "layered_ci_replace" and man["step"] == 20000 and man["fold"] == 0, man
    inter = sl_ = st_ = 0
    for s in stems:
        c = dumpfmt.read_cell(dd / f"{s}.npz")
        assert "p_inact_softmax" in c, s
        g = load_index_mask(Path(a.root) / "masks_v11" / f"{s}.png")   # held-out link = strict v1.1 mask
        t = inact_region_fill(g) == 1
        lay = c["p_inact"].astype(np.float32) > 0.5
        inter += int((lay & t).sum()); sl_ += int(lay.sum()); st_ += int(t.sum())
    dice = 2 * inter / (sl_ + st_) if sl_ + st_ else float("nan")
    verdict("C4 region Dice", dice >= 0.3, f"pooled over 107 fold-0 cells: {dice:.4f} (layer px {sl_}, target px {st_}, "
            f"both {inter}); need >= 0.3")
say(f"PATHFINDER {'PASS' if ok_all else 'NOT PASSED'} ({a.run}; criteria C1 to C4; not used to rank)")
if a.out:
    Path(a.out).write_text("\n".join(L) + "\n")
