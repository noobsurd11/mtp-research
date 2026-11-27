"""Label set v1.1 cards and roots: the _v11 cards = the house cards plus two config keys; on gaint, every cv5v2_v11 root
loads as scripts/train.py would (train masks with ignore 255, held-out masks strict) and every v1 root reads masks_escdd."""
import os
from pathlib import Path

import pytest

from bench import cards

ROOT = Path(__file__).resolve().parent.parent
M = ROOT / "bench" / "methods"
ROOTS = Path(os.environ.get("BENCH_ROOTS", "/home/noob/work/bench_data/roots"))
V11 = Path(os.environ.get("BENCH_MASKS_V11", "/home/noob/work/bench_data/masks_v11"))
PAIRS = [("house_r34_unetpp", "house_r34_unetpp_v11"), ("house_r34_unetpp_pf", "house_r34_unetpp_pf_v11")]
SAME = ("version", "family", "papers", "kind", "config", "weights", "weights_key", "decision_rule", "memory", "external")


@pytest.mark.parametrize("base,v11", PAIRS)
def test_v11_card_is_house_plus_two_keys(base, v11):
    a, b = cards.load_card(M / f"{base}.yaml"), cards.load_card(M / f"{v11}.yaml")
    assert b["name"] == v11 and b["diff_ref"] == base
    assert {k: a[k] for k in SAME} == {k: b[k] for k in SAME}
    d = cards.config_diff(cards.expected_config(a, 5, "x", "/r"), cards.expected_config(b, 5, "x", "/r"))
    assert d == ["data.mask_ignore_value: '<absent>' -> 255", "data.mask_subdir: 'labeled/masks_escdd' -> 'masks_v11'"]


def _roots(tag):
    rs = sorted(ROOTS.glob(f"cv5v2_{tag}_f*"))
    if len(rs) != 5:
        pytest.skip(f"cv5v2_{tag} roots not on this machine")
    return rs


def _lines(p):
    return [l.strip() for l in open(p) if l.strip()]


def test_v11_roots_load_like_the_trainer():
    from src.data.benchmark_el import load_index_mask
    rs = _roots("v11")
    c = cards.load_card(M / "house_r34_unetpp_pf_v11.yaml")
    sub = cards.expected_config(c, 5, "x", str(rs[0]))["data"]["mask_subdir"]
    ign_train = 0
    for r in rs:
        msk = r / sub                                  # = scripts/train.py: root / data.mask_subdir
        tr, va, te = (_lines(r / "splits" / f"{n}.txt") for n in ("train", "val", "test"))
        assert va == te and not set(tr) & set(va)
        for s in tr:
            assert os.readlink(msk / f"{s}.png") == str(V11 / "masks" / f"{s}.png")
            ign_train += int((load_index_mask(msk / f"{s}.png", 255) == 255).sum())
        for s in va:
            assert os.readlink(msk / f"{s}.png") == str(V11 / "masks_strict" / f"{s}.png")
            load_index_mask(msk / f"{s}.png")         # strict: raises on 255 (the trainer's val / test datasets)
    assert ign_train == 4 * 3484                       # each train cell is in 4 of the 5 train lists (LABELS_V11 s2)


def test_v1_roots_read_masks_escdd():
    rs = _roots("v1")
    c = cards.load_card(M / "house_r34_unetpp_pf.yaml")
    sub = cards.expected_config(c, 5, "x", str(rs[0]))["data"]["mask_subdir"]
    for r in rs:
        assert sub == "labeled/masks_escdd" and not (r / "masks_v11").exists()
        assert (r / sub).resolve() == Path("/home/noob/work/el-fault-detection/data/labeled/masks_escdd").resolve()
