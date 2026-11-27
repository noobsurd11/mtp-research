"""GPU job launching: memory guard, job limit and a resume-once watchdog.

Rules (shared GPU):
  * before every launch, ``torch.cuda.mem_get_info`` (in a short-lived
    subprocess, so this process never holds a CUDA context) must show at least
    ``expected peak + margin`` (2 GiB) free;
  * at most ``max_jobs`` (2) of our training processes at once;
  * launches are serialised by a file lock and each launch waits until the new
    run has logged its first training step, so the next memory check sees the
    new job's memory;
  * waiting launchers are served first come, first served among the jobs
    that fit (ticket files in ``experiments/.queue`` hold each job's peak).

``run_job`` blocks: it waits for a slot, starts ``scripts/train.py``, and if the
process dies (non-zero exit) it waits for a slot again and relaunches once
with ``--resume`` (from ``checkpoints/latest.pth``), or from scratch with
``--overwrite`` if the run died before its first checkpoint.  Every decision
goes to ``experiments/<run>/launch.log``.
"""

from __future__ import annotations

import fcntl
import os
import signal
import subprocess
import sys
import time
from contextlib import contextmanager
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
EXPERIMENTS = ROOT / "experiments"
LOCK = EXPERIMENTS / ".gpu_launch.lock"
QUEUE = EXPERIMENTS / ".queue"
MARGIN_GIB = 2.0
MAX_JOBS = 2


def gpu_free_gib() -> tuple[float, float]:
    """(free, total) GiB on cuda:0 via ``torch.cuda.mem_get_info`` in a subprocess."""
    out = subprocess.run(
        [sys.executable, "-c", "import torch; f, t = torch.cuda.mem_get_info(0); print(f, t)"],
        capture_output=True, text=True, check=True,
    ).stdout.split()
    return int(out[0]) / 2**30, int(out[1]) / 2**30


GPU_SCRIPTS = ("scripts/train.py", "scripts/probes.py", "scripts/evaluate.py")


def our_training_jobs() -> list[tuple[int, str]]:
    """(pid, name) of our running GPU jobs: ``scripts/{train,probes,evaluate}.py`` main processes
    (DataLoader workers and ``--device cpu`` runs excluded)."""
    ps = subprocess.run(["ps", "-u", str(os.getuid()), "-o", "pid=,ppid=,args="],
                        capture_output=True, text=True, check=True).stdout
    procs = {}
    for line in ps.splitlines():
        parts = line.split(None, 2)
        if len(parts) == 3 and "python" in parts[2] and any(g in parts[2] for g in GPU_SCRIPTS) \
                and "--device cpu" not in parts[2]:  # CPU-only test runs do not use the GPU
            procs[int(parts[0])] = (int(parts[1]), parts[2])
    jobs = []
    for pid, (ppid, args) in procs.items():
        if ppid in procs:  # a DataLoader worker of one of these processes
            continue
        words = args.split()
        name = next((w.split("=", 1)[1] for w in words if w.startswith("run_name=")), None)
        if name is None and "--run" in words:
            name = "eval:" + Path(words[words.index("--run") + 1]).name
        jobs.append((pid, name or "?"))
    return jobs


@contextmanager
def launch_lock():
    LOCK.parent.mkdir(parents=True, exist_ok=True)
    with open(LOCK, "w") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)


class JobLog:
    def __init__(self, path: Path) -> None:
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)

    def __call__(self, msg: str) -> None:
        line = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
        with open(self.path, "a") as f:
            f.write(line + "\n")
        print(line, flush=True)


def slot_check(peak_gib: float) -> tuple[bool, str]:
    """(ok, reason): fewer than MAX_JOBS of our jobs and free >= peak + margin."""
    jobs = our_training_jobs()
    if len(jobs) >= MAX_JOBS:
        return False, f"wait: {len(jobs)} of our jobs running {sorted(n for _, n in jobs)}"
    free, total = gpu_free_gib()
    if free < peak_gib + MARGIN_GIB:
        return False, f"wait: free {free:.1f} GiB < expected peak {peak_gib:.1f} + {MARGIN_GIB:.0f} GiB"
    return True, f"slot ok: {len(jobs)} job(s) running, free {free:.1f}/{total:.1f} GiB >= {peak_gib:.1f} + {MARGIN_GIB:.0f}"


def _wait_first_step(proc: subprocess.Popen, train_log: Path, offset: int, timeout: float = 900) -> None:
    """Block until the run logs a training step after ``offset`` bytes, exits, or ``timeout`` passes."""
    t0 = time.time()
    while time.time() - t0 < timeout and proc.poll() is None:
        if train_log.exists():
            if train_log.stat().st_size < offset:  # a fresh start truncated the log
                offset = 0
            with open(train_log, "rb") as f:
                f.seek(offset)
                if b" loss=" in f.read():
                    return
        time.sleep(5)


def _pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def _is_launcher(pid: int) -> bool:
    """True if ``pid`` is alive and is one of our launchers (night_queue.py / launch.py).

    A ticket names the launcher's pid; after a reboot that pid can belong to an unrelated process, which must
    not count as a waiting launcher (it would block the queue forever).
    """
    if not _pid_alive(pid):
        return False
    try:
        cmd = Path(f"/proc/{pid}/cmdline").read_bytes().replace(b"\0", b" ").decode(errors="replace")
    except OSError:
        return False
    return "scripts/night_queue.py" in cmd or "scripts/launch.py" in cmd


def _live_tickets() -> list[Path]:
    """Waiting launchers' tickets, oldest first (tickets of dead launchers are removed)."""
    alive = []
    for t in sorted(QUEUE.iterdir()):
        try:
            pid = int(t.name.split("_")[1])
        except (IndexError, ValueError):
            continue
        if _is_launcher(pid):
            alive.append(t)
        else:
            t.unlink(missing_ok=True)
    return alive


def queue_pick() -> tuple[Path | None, str]:
    """The ticket allowed to launch now, and why.

    Backfilling FIFO: the oldest waiting job whose expected peak + margin fits
    in the free memory (with fewer than MAX_JOBS of our jobs running).  A big
    job that does not fit yet does not block a smaller one behind it.
    """
    jobs = our_training_jobs()
    if len(jobs) >= MAX_JOBS:
        return None, f"wait: {len(jobs)} of our jobs running {sorted(n for _, n in jobs)}"
    free, total = gpu_free_gib()
    tickets = _live_tickets()
    for t in tickets:
        try:
            peak = float(t.read_text())
        except (OSError, ValueError):
            continue
        if free >= peak + MARGIN_GIB:
            return t, (f"slot ok: {len(jobs)} job(s) running, free {free:.1f}/{total:.1f} GiB >= "
                       f"{peak:.1f} + {MARGIN_GIB:.0f} for {t.name.split('_', 2)[2]}")
    return None, f"wait: free {free:.1f} GiB fits none of {len(tickets)} queued job(s)"


def start_when_free(run_name: str, peak_gib: float, cmd: list[str], log: JobLog, poll: float = 60,
                    ticket_ns: int | None = None, settle: float | None = None) -> subprocess.Popen:
    """Wait for a slot (job limit + memory guard), start ``cmd``, wait for its first step.

    Launchers are served first come, first served: each takes a ticket in
    ``experiments/.queue`` and only the oldest live ticket may launch.
    ``ticket_ns`` keeps an earlier place in the queue (watchdog restarts).
    ``settle``: seconds to hold the launch lock after starting a non-training
    command (instead of waiting for the first logged training step).
    """
    train_log = EXPERIMENTS / run_name / "train.log"
    QUEUE.mkdir(parents=True, exist_ok=True)
    ticket = QUEUE / f"{ticket_ns or time.time_ns():020d}_{os.getpid()}_{run_name}"
    ticket.write_text(f"{peak_gib}")
    last_reason = ""
    try:
        while True:
            with launch_lock():
                pick, reason = queue_pick()
                ok = pick == ticket
                if pick is not None and not ok:
                    reason = f"wait: {pick.name.split('_', 2)[2]} goes first"
                if ok:
                    ticket.unlink(missing_ok=True)
                    log(reason)
                    offset = train_log.stat().st_size if train_log.exists() else 0
                    stdout = open(EXPERIMENTS / f"{run_name}.stdout", "a")
                    log("launch: " + " ".join(cmd))
                    proc = subprocess.Popen(cmd, cwd=ROOT, stdout=stdout, stderr=subprocess.STDOUT)
                    if settle is None:
                        _wait_first_step(proc, train_log, offset)
                    else:
                        t0 = time.time()
                        while time.time() - t0 < settle and proc.poll() is None:
                            time.sleep(2)
                    log(f"pid {proc.pid} " + ("running" if proc.poll() is None else f"exited rc={proc.returncode}"))
                    return proc
            if reason != last_reason:
                log(reason + f" (polling every {poll:.0f} s)")
                last_reason = reason
            time.sleep(poll)
    finally:
        ticket.unlink(missing_ok=True)


def run_job(run_name: str, peak_gib: float, train_args: list[str], max_restarts: int = 1,
            fresh: bool = True, front: bool = False) -> int:
    """Run one training job to completion with the guard and the watchdog.  Returns the exit code.

    ``train_args``: arguments for ``scripts/train.py`` (must include ``run_name=<run_name>`` in ``--opts``).
    ``fresh``: first launch uses ``--overwrite`` (start from scratch); otherwise ``--resume``.
    ``front``: take a place ahead of every waiting job (short smoke tests).
    """
    if f"run_name={run_name}" not in train_args:
        raise ValueError(f"train_args must set run_name={run_name}")
    log = JobLog(EXPERIMENTS / run_name / "launch.log")
    base = [sys.executable, "-u", "scripts/train.py"]
    latest = EXPERIMENTS / run_name / "checkpoints" / "latest.pth"
    stop = {"flag": False, "proc": None}

    def on_term(signum, frame):  # forward and do not restart
        stop["flag"] = True
        log(f"launcher got signal {signum}; forwarding to the run, no restart")
        if stop["proc"] is not None and stop["proc"].poll() is None:
            stop["proc"].send_signal(signal.SIGTERM)
        else:  # still queued: nothing to forward, just leave
            raise SystemExit(128 + signum)

    try:
        signal.signal(signal.SIGTERM, on_term)
    except ValueError:  # not in the main thread (night queue lanes)
        pass

    mode = "--overwrite" if fresh else "--resume"
    restarts = 0
    first_ticket = time.time_ns() if not front else time.time_ns() % 10**9  # front: a tiny ticket number
    while True:
        proc = start_when_free(run_name, peak_gib, base + [mode] + train_args, log, ticket_ns=first_ticket)
        stop["proc"] = proc
        rc = proc.wait()
        if rc == 0:
            log("finished rc=0")
            return 0
        log(f"run died rc={rc}")
        if stop["flag"] or restarts >= max_restarts:
            log(f"giving up (restarts used {restarts}/{max_restarts})")
            return rc
        restarts += 1
        mode = "--resume" if latest.exists() else "--overwrite"
        log(f"watchdog restart {restarts}/{max_restarts} with {mode}")
        time.sleep(30)


def run_task(name: str, peak_gib: float, cmd: list[str], settle: float = 45) -> int:
    """Run a short GPU command (evaluation, probes) under the same guard; no restart.  Returns the exit code."""
    log = JobLog(EXPERIMENTS / "repro" / f"{name}.launch.log")
    proc = start_when_free(name, peak_gib, cmd, log, settle=settle)
    rc = proc.wait()
    log(f"finished rc={rc}")
    return rc
