"""Method cards: schema, opts rendering = train.py apply_opts, and the house card reproduces a real run's config."""
import importlib.util
from pathlib import Path

import pytest

from bench import cards

ROOT = Path(__file__).resolve().parent.parent
REAL = {"house_r34_unetpp": ("/home/noob/work/el_f3/experiments/pf2_SUP_100pct_s5/config_used.yaml", "pf2_SUP_100pct_s5"),
        "house_r34_unetpp_pf": ("/home/noob/work/el_f3/experiments/pf2_SUPPF_100pct_s5/config_used.yaml", "pf2_SUPPF_100pct_s5")}


def test_cards_valid():
    for f in sorted((ROOT / "bench" / "methods").glob("*.yaml")):
        cards.load_card(f)


def test_reserved_opts_refused():
    c = cards.load_card(ROOT / "bench/methods/house_r34_unetpp.yaml")
    c["opts"] = c["opts"] + ["seed=3"]
    assert any("must not set" in e for e in cards.validate(c, "house_r34_unetpp"))


def test_apply_opts_equals_train():
    spec = importlib.util.spec_from_file_location("train_mod", ROOT / "scripts" / "train.py")
    tr = importlib.util.module_from_spec(spec); spec.loader.exec_module(tr)
    from src.utils.config import load_config
    c = cards.load_card(ROOT / "bench/methods/house_r34_unetpp_pf.yaml")
    ops = cards.run_opts(c, 5, "x", "data")
    assert tr.apply_opts(load_config(ROOT / c["config"]), ops) == cards.apply_opts(load_config(ROOT / c["config"]), ops)


@pytest.mark.parametrize("name", sorted(REAL))
def test_card_reproduces_real_config(name):
    path, run = REAL[name]
    if not Path(path).exists():
        pytest.skip("real run config not on this machine")
    c = cards.load_card(ROOT / f"bench/methods/{name}.yaml")
    assert cards.cfgcheck(c, Path(path), 5, run, "data") == []


@pytest.mark.parametrize("card", sorted(p.name for p in (ROOT / "bench" / "methods").glob("*.yaml")))
def test_card_model_builds_on_cpu(card):
    """Every harness card's rendered model section builds on CPU (local weight files only)."""
    import os
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    c = cards.load_card(ROOT / "bench/methods" / card)
    if c["kind"] != "harness":
        pytest.skip("external card")
    for w in c["weights"]:
        if not Path(w["path"]).exists():
            pytest.skip(f"missing {w['path']}")
        assert cards.md5_file(w["path"]) == w["md5"], w["path"]
    from src.models.model_factory import build_model
    m = build_model(cards.expected_config(c, 0, "x", "/r")["model"])
    assert sum(p.numel() for p in m.parameters()) > 0
