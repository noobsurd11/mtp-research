"""bench/m0core.py = m0_audit d36f7438 (comps, cell_stats, BANDS, NC, S8) and m0_analyze d5adbe6b (src, agg, DEFECT), by AST."""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_ast_identity():
    spec = importlib.util.spec_from_file_location("bench_score", ROOT / "scripts" / "bench_score.py")
    import sys
    argv = sys.argv
    sys.argv = ["bench_score.py", "ast-check"]
    try:
        mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    finally:
        sys.argv = argv
    assert mod.ast_check(ROOT / "tests/ref/m0_audit_d36f7438.py", ROOT / "tests/ref/m0_analyze_d5adbe6b.py") == []
