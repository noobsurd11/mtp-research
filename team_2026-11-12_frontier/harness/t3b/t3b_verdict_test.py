"""Tests of t3b_verdict.py (synthetic read documents only). Run: python -m pytest -q t3b_verdict_test.py"""
import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import t3b_verdict as V  # noqa: E402

REG = "registered x\nopening_e1 E1 opening #9 e1_open9_t3b (T3b)\nrule T3B_RULE.md abc\n"


def met(d, lo, hi):
    return {"delta": d, "lo": lo, "hi": hi, "se": 0.01}


def contrast(d=0.05, lo=0.01, hi=0.09, miou=0.0, ina=(0.0, -0.1, 0.1)):
    m = {k: met(0.0, -0.01, 0.01) for k in V.OVM.BOOT_KEYS} if hasattr(V.OVM, "BOOT_KEYS") else {}
    for k in ("relF1_2", "relP2", "relR2", "relF1_1", "crack_iou", "inact_iou", "miou_rob", "width_ratio", "fa_px", "fa_share50"):
        m[k] = met(0.0, -0.01, 0.01)
    m["relF1_2"] = met(d, lo, hi)
    m["miou_rob"] = met(miou, miou - 0.01, miou + 0.01)
    m["inact_iou"] = met(*ina)
    return {"seed_aware": {"metrics": m}, "fixed": {"metrics": copy.deepcopy(m)}}


def model(fa=1000.0):
    return {"relF1_2": 0.5, "crack_iou": 0.3, "inact_iou": 0.4, "miou_rob": 0.6, "width_ratio": 1.2, "fa_px": fa, "fa_cells": 74,
            "cc_recany_20": 0.5, "cc_rec50_20": 0.3, "cc_prec_20": 0.4, "per_class_iou": {str(c): 0.5 for c in V.ROB13}}


def arm(fa=1000.0, seeds=(5, 6, 7)):
    ms = {str(s): model(fa) for s in seeds}
    sm = {k: {"mean": v, "min": v, "max": v} for k, v in model(fa).items() if isinstance(v, float)}
    return {"models": ms, "summary": sm}


def rid(a, s):
    return {"ALL": f"t3b_all_s{s}.oof", "HALF": f"t3b_half_s{s}.oof", "ZS": f"fin_hrnet_swad_v11_pool_s{s}.swad.tta_d4.e1_106"}[a]


def doc(d=0.05, lo=0.01, hi=0.09, fa_all=1000.0, fa_zs=1000.0, miou=0.0, w_all=1.5, w_zs=1.0, seeds=(5, 6, 7)):
    sub = {"n": 106, "n_clusters": 71, "arms": {"ALL": arm(fa_all, seeds), "HALF": arm(1000.0, seeds), "ZS": arm(fa_zs, seeds)},
           "contrasts": {"ALL - ZS": contrast(d, lo, hi, miou), "HALF - ZS": contrast(), "ALL - HALF": contrast()},
           "guard_ratios": {"ALL - ZS": {"width_ratio": {"A": w_zs, "B": w_all, "B_over_A": w_all / w_zs},
                                         "fa_px": {"A": fa_zs, "B": fa_all, "B_over_A": fa_all / fa_zs}},
                            "HALF - ZS": {"width_ratio": {"A": 1, "B": 1, "B_over_A": 1}, "fa_px": {"A": 1, "B": 1, "B_over_A": 1}},
                            "ALL - HALF": {"width_ratio": {"A": 1, "B": 1, "B_over_A": 1}, "fa_px": {"A": 1, "B": 1, "B_over_A": 1}}}}
    strat = copy.deepcopy(sub)
    strat["n"], strat["n_clusters"] = 29, 10
    return {"set": "e1_106", "n_cells": 106, "n_clusters": 71, "labels": "set", "boot": 2000, "boot_seed": 0,
            "t3b": {"comparator": "ZS", "trained_on_e1_arms": ["ALL", "HALF"]},
            "arms": {a: {"runs": [{"seed": s, "run_id": rid(a, s)} for s in seeds]} for a in ("ALL", "HALF", "ZS")},
            "subsets": {"all": sub, "strat_hard": strat}}


def test_confirmed():
    r = V.decide(doc())
    assert r["outcome"] == "CONFIRMED" and not r["fails"]


@pytest.mark.parametrize("kw,item", [({"fa_all": 1501.0}, "G1 false crack px"), ({"miou": -0.0101}, "G2 mIoU-R13")])
def test_each_guard_alone_fails(kw, item):
    r = V.decide(doc(**kw))
    assert r["outcome"] == "GAIN, FAILING GUARDS NAMED" and r["fails"] == [item]


def test_inclusive_edges():
    assert V.decide(doc(fa_all=1500.0))["outcome"] == "CONFIRMED"
    assert V.decide(doc(miou=-0.010))["outcome"] == "CONFIRMED"
    assert V.decide(doc(d=0.010))["outcome"] == "CONFIRMED"


@pytest.mark.parametrize("kw,want", [({"lo": 0.0}, "the interval holds 0; Delta > 0"), ({"d": 0.0099}, "below M"),
                                     ({"d": -0.05, "lo": -0.09, "hi": -0.01}, "WORSE"), ({"d": -0.01, "lo": -0.05, "hi": 0.0}, "Delta <= 0")])
def test_not_confirmed_wording(kw, want):
    r = V.decide(doc(**kw))
    assert r["outcome"].startswith("NOT CONFIRMED") and want in r["outcome"]


def test_guards_never_rescue_and_width_never_decides():
    assert V.decide(doc(lo=-0.001, fa_all=1.0))["outcome"].startswith("NOT CONFIRMED")
    for w in (0.2, 1.0, 3.0):
        assert V.decide(doc(w_all=w))["outcome"] == "CONFIRMED"


def test_missing_values_fail_closed():
    assert V.decide(doc(d=None))["outcome"].startswith("NOT CONFIRMED")
    assert V.decide(doc(fa_zs=float("nan")))["outcome"] == "GAIN, FAILING GUARDS NAMED"


@pytest.mark.parametrize("change,why", [("seeds", "seeds"), ("arm", "arm HALF missing"), ("t3b", "T3b card"), ("boot", "bootstrap"),
                                        ("cells", "set / cells / clusters")])
def test_check_read_refusals(change, why):
    d = doc()
    if change == "seeds":
        d["arms"]["ALL"]["runs"] = [{"seed": 5}, {"seed": 6}]
    if change == "arm":
        del d["arms"]["HALF"]
    if change == "t3b":
        d["t3b"]["comparator"] = "ALL"
    if change == "boot":
        d["boot"] = 1000
    if change == "cells":
        d["n_clusters"] = 70
    assert any(why in b for b in V.check_read(d))


def test_main_end_to_end_and_refusals(tmp_path):
    rd = tmp_path / "read.json"; rd.write_text(json.dumps(doc()))
    reg = tmp_path / "REG.txt"; reg.write_text(REG)
    out = tmp_path / "v" / "verdict.txt"
    r = subprocess.run([sys.executable, str(HERE / "t3b_verdict.py"), "--read", str(rd), "--reg", str(reg), "--out", str(out)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    t = out.read_text()
    assert "T3B VERDICT: P (ALL - ZS pooled out-of-fold crack relF1@2) CONFIRMED" in t
    assert "ZS (zero-shot comparator, never trained on E1)" in t and "reported, not a guard" in t
    assert all("convention band" in l for l in t.splitlines() if "strict crack IoU" in l and ("+" in l or "-0" in l))
    assert json.loads(out.with_suffix(".json").read_text())["outcome"] == "CONFIRMED"
    r = subprocess.run([sys.executable, str(HERE / "t3b_verdict.py"), "--read", str(rd), "--reg", str(reg), "--out", str(out)],
                       capture_output=True, text=True)
    assert r.returncode != 0 and "exists" in r.stderr
    reg.write_text("registered x\n")
    r = subprocess.run([sys.executable, str(HERE / "t3b_verdict.py"), "--read", str(rd), "--reg", str(reg), "--out", str(tmp_path / "v2.txt")],
                       capture_output=True, text=True)
    assert r.returncode != 0 and "opening #9" in r.stderr


def test_rule_constants():
    assert (V.M, V.FA_X, V.MIOU_MIN, V.N_CELLS, V.N_CLUSTERS, V.SEEDS, V.BAND) == (0.010, 1.5, -0.010, 106, 71, [5, 6, 7], 0.019)


@pytest.mark.parametrize("attr,val", [("M", 0.02), ("FA_X", 2.0), ("MIOU_MIN", -0.02)])
def test_tampered_constants_change_an_outcome(monkeypatch, attr, val):
    case = {"M": doc(d=0.015), "FA_X": doc(fa_all=1800.0), "MIOU_MIN": doc(miou=-0.015)}[attr]
    before = V.decide(case)["outcome"]
    monkeypatch.setattr(V, attr, val)
    assert V.decide(case)["outcome"] != before


def test_primary_is_the_seed_aware_interval_not_the_fixed_model_one():
    """round 1 N2: fixed-model and seed-aware intervals differ; only the seed-aware one decides (mutant M9 fails here)."""
    d = doc(d=0.05, lo=-0.002, hi=0.10)
    d["subsets"]["all"]["contrasts"]["ALL - ZS"]["fixed"]["metrics"]["relF1_2"] = met(0.05, 0.02, 0.08)
    assert V.decide(d)["outcome"].startswith("NOT CONFIRMED")
    d2 = doc(d=0.05, lo=0.01, hi=0.09)
    d2["subsets"]["all"]["contrasts"]["ALL - ZS"]["fixed"]["metrics"]["relF1_2"] = met(0.05, -0.03, 0.12)
    r = V.decide(d2)
    assert r["outcome"] == "CONFIRMED" and r["fixed"]["lo"] == -0.03 and r["lo"] == 0.01


@pytest.mark.parametrize("arm,bad", [("ALL", "t3b_half_s5.oof"), ("HALF", "t3b_all_s6.oof"), ("ZS", "fin_hrnet_swad_v11_pool_s8.swad.tta_d4.e1_106")])
def test_run_ids_must_be_the_registered_ones(arm, bad):
    """round 1 B2: a read with swapped or foreign records is refused."""
    d = doc()
    d["arms"][arm]["runs"][0]["run_id"] = bad
    assert any(f"arm {arm} run ids" in b for b in V.check_read(d))


def test_swapped_all_and_half_is_refused():
    d = doc()
    d["arms"]["ALL"]["runs"], d["arms"]["HALF"]["runs"] = d["arms"]["HALF"]["runs"], d["arms"]["ALL"]["runs"]
    b = V.check_read(d)
    assert any("arm ALL run ids" in x for x in b) and any("arm HALF run ids" in x for x in b)


def test_crack_free_count_must_be_74():
    """round 1 N3"""
    d = doc()
    d["subsets"]["all"]["arms"]["ZS"]["models"]["6"]["fa_cells"] = 73
    assert any("73 crack-free cells (74 registered)" in b for b in V.check_read(d))
    assert not V.check_read(doc())


def test_repeat_header(tmp_path):
    """round 1 N5"""
    rd = tmp_path / "read.json"; rd.write_text(json.dumps(doc()))
    reg = tmp_path / "REG.txt"; reg.write_text(REG)
    out = tmp_path / "verdict.txt"
    r = subprocess.run([sys.executable, str(HERE / "t3b_verdict.py"), "--read", str(rd), "--reg", str(reg), "--repeat", "x1", "--out", str(out)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert "# REPEAT (TAG x1), not the registered read" in out.read_text().splitlines()[2]
