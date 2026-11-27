"""cv5v2_f<k> sets: held-out lists of the cv5v2_v11 roots (md5 = cv5v2.json), v1.1 GT + ignore; bench_infer's queue token."""
import subprocess
import sys
from pathlib import Path

import pytest

from bench import sets

ROOT = Path(__file__).resolve().parent.parent
N = (107, 111, 104, 104, 106)


@pytest.mark.parametrize("k", range(5))
def test_cv5v2_sets(k):
    if not (sets.CV_ROOTS["cv5v2"] / f"cv5v2_v11_f{k}").exists():
        pytest.skip("cv5v2 roots not on this machine")
    S = sets.resolve(f"cv5v2_f{k}")
    assert S["kind"] == "open" and len(S["stems"]) == N[k] and S["list_md5"] == sets.CV_LIST_MD5["cv5v2"][k]
    assert S["masks"] == sets.MASKS_V11 / "masks" and S["ignore"] == sets.MASKS_V11 / "ignore"
    assert all((S["masks"] / f"{s}.png").is_file() and (S["ignore"] / f"{s}.png").is_file() for s in S["stems"])
    if k in (0, 4):   # folds 0 and 4 = B6 folds 0 and 4
        assert S["stems"] == sets.resolve(f"cv5v1_f{k}")["stems"]


def test_infer_prints_bench_start_first():
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "bench_infer.py"), "--run", "/nonexistent", "--set", "test50",
                        "--dumps", "/nonexistent", "--method", "x", "--bench-run", "dump_x"],
                       capture_output=True, text=True, cwd=ROOT)
    assert r.returncode != 0 and r.stdout.splitlines()[0] == "BENCH_START: run=dump_x"
