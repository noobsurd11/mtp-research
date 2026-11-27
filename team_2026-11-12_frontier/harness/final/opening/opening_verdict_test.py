"""Tests of opening_verdict.py (the registered rule, OPENING_RULE.md section 4): every outcome, every guard and its edges,
inactive and strict-IoU wording, and an end-to-end run of main() on reads made by scripts/bench_open_read.py (R) from
synthetic records. Round 1 (REVIEW_OPENING.md 3f7d6d4e): B1 (every strict-IoU delta line carries the convention band), N2
(inactive fixed-model interval, per-class and component tables), N3 (fin decisions quoted; md5, mechanics and count refusals),
N15 (hi = 0 is not WORSE). Run: python -m pytest -q opening_verdict_test.py (CPU, about a minute). No sealed data."""
import copy
import hashlib
import json
import re
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import opening_verdict as V  # noqa: E402

R_TREE = Path(V.R_TREE)


def _m(d, lo, hi, se=0.01):
    return {"delta": d, "lo": lo, "hi": hi, "se": se}


def base(delta=0.03, lo=0.005, hi=0.06, width=(1.00, 1.02), csir=(1.0, 1.03), fa=(300.0, 330.0), miou=0.0,
         inact=(-0.02, -0.08, 0.04), siou=(0.01, -0.01, 0.03)):
    sa = {"relF1_2": _m(delta, lo, hi, 0.019), "miou_rob": _m(miou, miou - 0.01, miou + 0.01),
          "inact_iou": _m(*inact), "crack_iou": _m(*siou), "relP2": _m(0.01, -0.01, 0.03), "relR2": _m(0.02, 0.0, 0.04),
          "relF1_1": _m(0.02, 0.0, 0.04)}
    gr = {"width_ratio": {"A": width[0], "B": width[1], "B_over_A": width[1] / width[0]},
          "fa_px": {"A": fa[0], "B": fa[1], "B_over_A": fa[1] / fa[0]}}
    grc = {"width_ratio": {"A": csir[0], "B": csir[1], "B_over_A": csir[1] / csir[0]}, "fa_px": gr["fa_px"]}
    con = {"seed_aware": {"metrics": sa}, "fixed": {"metrics": {"relF1_2": _m(delta, delta - 0.02, delta + 0.02)}}}
    arms = {"C1": {"models": {"5": {"fa_cells": 74}}, "summary": {}}}
    return {"subset_n": {"all": 106, "src:CSIR": 101, "src:BMRK": 5},
            "subsets": {"all": {"contrasts": {"C2 - C1": con}, "guard_ratios": {"C2 - C1": gr}, "arms": arms},
                        "src:CSIR": {"guard_ratios": {"C2 - C1": grc}},
                        "src:BMRK": {"guard_ratios": {"C2 - C1": {"width_ratio": {"A": 1, "B": 3, "B_over_A": 3.0}}}}}}


def test_confirmed():
    r = V.decide(base())
    assert r["outcome"] == "CONFIRMED" and r["fails"] == [] and r["headline"]
    assert [g[1] for g in r["guards"]] == ["G1 width pooled", "G2 width CSIR", "G3 false crack px", "G4 mIoU-R13"]


def test_bmrk_with_5_cells_is_not_a_guard_item():
    r = V.decide(base())        # BMRK width ratio 3.0 would fail, but BMRK has 5 cells < 40
    assert all("BMRK" not in g[1] for g in r["guards"]) and r["outcome"] == "CONFIRMED"


@pytest.mark.parametrize("kw,item", [
    ({"width": (1.0, 1.16)}, "G1 width pooled"), ({"width": (1.0, 0.84)}, "G1 width pooled"),
    ({"csir": (1.0, 1.151)}, "G2 width CSIR"), ({"fa": (100.0, 150.1)}, "G3 false crack px"),
    ({"miou": -0.0101}, "G4 mIoU-R13")])
def test_each_guard_fails_alone(kw, item):
    r = V.decide(base(**kw))
    assert r["outcome"] == "GAIN, FAILING GUARDS NAMED" and r["fails"] == [item]


@pytest.mark.parametrize("kw", [{"width": (1.0, 1.15)}, {"width": (1.0, 0.85)}, {"csir": (2.0, 2.3)},
                                {"fa": (100.0, 150.0)}, {"miou": -0.010}, {"delta": 0.010}])
def test_inclusive_edges_pass(kw):
    assert V.decide(base(**kw))["outcome"] == "CONFIRMED"


def test_hi_zero_is_not_worse():     # N15: WORSE needs the upper end strictly below 0
    assert V.decide(base(delta=-0.03, lo=-0.06, hi=0.0))["outcome"] == "NOT CONFIRMED (the interval holds 0; Delta <= 0)"
    assert V.decide(base(delta=-0.03, lo=-0.06, hi=-1e-9))["outcome"].startswith("NOT CONFIRMED (WORSE")


def test_band_helper():
    assert V.band(0.019) == "inside the convention band +-0.019; decides nothing"
    assert V.band(-0.0191) == "outside the convention band +-0.019; decides nothing"
    assert V.band(None).startswith("outside")
    assert V.BAND == 0.019


def test_strict_edges_of_the_headline():
    assert V.decide(base(lo=0.0))["outcome"].startswith("NOT CONFIRMED (the interval holds 0")
    assert V.decide(base(delta=0.0099, lo=0.001))["outcome"].startswith("NOT CONFIRMED (below M")
    assert V.decide(base(delta=-0.03, lo=-0.06, hi=-0.001))["outcome"].startswith("NOT CONFIRMED (WORSE")
    r = V.decide(base(delta=0.02, lo=-0.017, hi=0.057))
    assert r["outcome"] == "NOT CONFIRMED (the interval holds 0; Delta > 0)" and not r["headline"]


def test_guards_do_not_rescue_a_failed_headline():
    r = V.decide(base(lo=-0.01, width=(1.0, 2.0)))
    assert r["outcome"].startswith("NOT CONFIRMED") and "G1 width pooled" in r["fails"]


def test_inactive_never_decides_but_is_named():
    r = V.decide(base(inact=(-0.2, -0.3, -0.1)))
    assert r["outcome"] == "CONFIRMED" and r["inactive_lower"]
    assert not V.decide(base())["inactive_lower"]


def test_strict_iou_band_label():
    assert V.decide(base(siou=(0.019, 0.0, 0.03)))["strict_band"] == "inside the convention band"
    assert V.decide(base(siou=(-0.0191, -0.03, 0.0)))["strict_band"] == "outside the convention band"


def test_missing_values_fail_closed():
    d = base()
    d["subsets"]["all"]["contrasts"]["C2 - C1"]["seed_aware"]["metrics"]["relF1_2"]["lo"] = None
    assert V.decide(d)["outcome"].startswith("NOT CONFIRMED")
    d = base()
    d["subsets"]["all"]["guard_ratios"]["C2 - C1"]["width_ratio"]["B_over_A"] = None
    assert V.decide(d)["outcome"] == "GAIN, FAILING GUARDS NAMED"


def test_a_tampered_rule_is_caught():
    """Mutants of the rule constants change at least one outcome of these tests' fixtures."""
    for name, val in (("M", 0.0), ("FA_X", 2.0), ("MIOU_MIN", -0.05), ("WIDTH", (0.8, 1.2)), ("MIN_SRC_CELLS", 5)):
        old = getattr(V, name)
        setattr(V, name, val)
        try:
            outs = [V.decide(base(delta=0.009, lo=0.001))["outcome"], V.decide(base(fa=(100.0, 160.0)))["outcome"],
                    V.decide(base(miou=-0.02))["outcome"], V.decide(base(width=(1.0, 1.18)))["outcome"],
                    V.decide(base())["outcome"]]
        finally:
            setattr(V, name, old)
        ref = [V.decide(base(delta=0.009, lo=0.001))["outcome"], V.decide(base(fa=(100.0, 160.0)))["outcome"],
               V.decide(base(miou=-0.02))["outcome"], V.decide(base(width=(1.0, 1.18)))["outcome"], V.decide(base())["outcome"]]
        assert outs != ref, name


# ---------------------------------------------------------------- end to end through main() on real read.json files
@pytest.fixture(scope="module")
def reads(tmp_path_factory):
    if not (R_TREE / "scripts" / "bench_open_read.py").exists():
        pytest.skip("read tree R not on this machine")
    sys.path.insert(0, str(R_TREE / "tests"))
    sys.path.insert(0, str(R_TREE / "scripts"))
    import bench_open_read as bor
    from test_bench_opening_read import _synth_records
    t = tmp_path_factory.mktemp("verdict")
    out = {}
    for tag, set_name, labels, arms, pairs, extra in (
            ("e1", "e1_106", "set", ("C1", "C2", "C3", "EPF"), ["C1=C2", "C1=C3", "EPF=C3", "C2=C3", "C1=C2S5", "C1=EPF"],
             ["--aa", "C1:5,6:7,8"]),
            ("t50", "test50", "v11", ("C1", "C2"), ["C1=C2", "C1=C2S5"], []),
            ("t50v0", "test50", "v0", ("C1", "C2"), ["C1=C2"], ["--public"])):
        d = t / tag
        d.mkdir()
        recs = {}
        for i, a in enumerate(arms):
            seeds = [56789] if a in ("C3", "EPF") else [5, 6, 7, 8, 9]
            recs[a] = _synth_records(d, a, seeds, shift=0.05 if a in ("C2", "C3") else 0.0, seed0=i,
                                     labels=labels)
        recs["C2S5"] = [recs["C2"][0]]
        for p in recs.values():
            for f in p:
                r = json.loads(Path(f).read_text())
                r["set"] = set_name
                Path(f).write_text(json.dumps(r))
        args = ["--set", set_name, "--out", str(d / "read"), "--boot", "2000"]
        for a, fs in recs.items():
            args += ["--arm", f"{a}={','.join(fs)}"]
        for p in pairs:
            args += ["--pair", p]
        bor.main(args + extra)
        out[tag] = d / "read" / "read.json"
    fin = t / "fin_verdict.txt"
    fin.write_text("x\n(a) B5 TTA RESULT NOT REPLICATED ON CV5V3 / CV02: (a) is NOT CONFIRMED (test).\n"
                   "(b) D4 IN C2 / C3 SUPPORTED ON CV5: (b) CS_D4 - CS is CONFIRMED.\n(c) C2 PASSES ITS CV5 CHECK (test)\n")
    fmd5 = hashlib.md5(fin.read_bytes()).hexdigest()
    reg = t / "REGISTERED.txt"
    reg.write_text(f"registered x\nrule OPENING_RULE.md abc\njobs j 20 lines\nc1d4 no (fin verdict {fmd5})\n"
                   "flags none | ruled: not needed\nruns F2 9967d59abaab03cef83c1e3014840b2359ef45d7 (deploy /tmp/noob_el/bench_9967d59: test)\n")
    out["reg"] = reg
    out["fin"] = fin
    out["t"] = t
    return out


def _main(reads, out, *extra, fin=None, reg=None):
    V.main(["--e1", str(reads["e1"]), "--t50", str(reads["t50"]), "--t50v0", str(reads["t50v0"]), "--reg",
            str(reg or reads["reg"]), "--fin-verdict", str(fin or reads["fin"]), "--out", str(out), *extra])


def test_main_end_to_end_mechanics(reads):
    o = reads["t"] / "verdict.txt"
    _main(reads, o, "--mechanics")
    txt = o.read_text()
    assert "## E1 opening #8: the primary contrast P = C2 - C1" in txt and "FINAL OPENING VERDICT: E1 P" in txt
    assert "## test50 opening #19: the public table" in txt and "| Pratt A crack |" in txt and "S2 C3 - E-PF" in txt
    assert "test50 leakage" in txt
    js = json.loads(o.with_suffix(".json").read_text())
    assert js["outcome"] in ("CONFIRMED", "GAIN, FAILING GUARDS NAMED") or js["outcome"].startswith("NOT CONFIRMED")
    with pytest.raises(SystemExit):
        _main(reads, o, "--mechanics")


SIGNED = re.compile(r"[+-]\d+\.\d")


def test_every_strict_iou_delta_line_carries_the_band(reads):       # B1
    o = reads["t"] / "verdict_b1.txt"
    _main(reads, o, "--mechanics")
    lines = [l for l in o.read_text().splitlines() if "strict" in l.lower() and SIGNED.search(l)]
    assert len(lines) >= 8, len(lines)        # P, S1 to S5 (+ C1-D4 lines when present), strata, test50 contrasts
    missing = [l for l in lines if "convention band +-0.019; decides nothing" not in l]
    assert not missing, missing
    # every strict-IoU number in such a line is followed by its band within the same clause
    for l in lines:
        for part in l.split(";"):
            if "strict crack IoU" in part and SIGNED.search(part):
                assert "convention band" in part or "convention band" in l[l.index(part):], l


def test_band_test_catches_a_line_without_the_band(reads, monkeypatch):
    o = reads["t"] / "verdict_b1_mutant.txt"
    monkeypatch.setattr(V, "siou", lambda m: f"strict crack IoU {V.ci(m, 'crack_iou')}")
    _main(reads, o, "--mechanics")
    lines = [l for l in o.read_text().splitlines() if "strict" in l.lower() and SIGNED.search(l)]
    assert any("convention band" not in l for l in lines)


def test_n2_n3_items_are_printed(reads):
    o = reads["t"] / "verdict_n2.txt"
    _main(reads, o, "--mechanics")
    txt = o.read_text()
    assert re.search(r"inactive IoU \(reported, never decides; 10 inactive cells\): .* seed-aware \[.*\], fixed-model \[", txt)
    assert "## E1 per-class IoU of the 13 robust classes" in txt and "| 14 crack |" in txt and "| 21 frame edge |" in txt
    assert "## E1 components" in txt and "| C1 |" in txt
    assert "(a) B5 TTA RESULT NOT REPLICATED" in txt and "(b) D4 IN C2 / C3 SUPPORTED" in txt and "(c) C2 PASSES" in txt
    assert "entry class (c)" in txt and "deviation from protocol 5.4" in txt
    assert ("- fin2 resume of the full-pool runs (registration line, quoted): runs F2 9967d59abaab03cef83c1e3014840b2359ef45d7 "
            "(deploy /tmp/noob_el/bench_9967d59: test)") in txt


def test_runs_f2_line_required(reads):      # round 3 (i): outside mechanics a registration without it is refused
    t = reads["t"]
    reg = t / "reg_nof2.txt"
    reg.write_text("\n".join(l for l in reads["reg"].read_text().splitlines() if not l.startswith("runs F2")) + "\n")
    with pytest.raises(SystemExit, match="'runs F2' lines"):
        _main(reads, t / "v_nof2.txt", reg=reg)
    _main(reads, t / "v_nof2_mech.txt", "--mechanics", reg=reg)
    assert "quoted): MISSING (mechanics run only)" in (t / "v_nof2_mech.txt").read_text()


def test_fin_verdict_refusals(reads):
    t = reads["t"]
    bad = t / "fin_bad.txt"
    bad.write_text(reads["fin"].read_text() + "extra\n")            # md5 differs from the registered one
    _, why = V.fin_lines(str(bad), reads["reg"].read_text())
    assert any("!= the registered" in w for w in why)
    for body, msg in (("(a) x\n(b) y\n", "decision (c) found 0 times"), ("(a) x\n(a) z\n(b) y\n(c) w\n", "decision (a) found 2"),
                      ("[MECHANICS TEST, NOT A VERDICT] (a) x\n(a) x\n(b) y\n(c) w\n", "MECHANICS")):
        f = t / "fin_case.txt"
        f.write_text(body)
        reg = t / "reg_case.txt"
        reg.write_text(f"c1d4 no (fin verdict {hashlib.md5(f.read_bytes()).hexdigest()})\n")
        _, why = V.fin_lines(str(f), reg.read_text())
        assert any(msg in w for w in why), (body, why)
    ok_lines, why = V.fin_lines(str(reads["fin"]), reads["reg"].read_text())
    assert why == [] and len(ok_lines) == 4


def test_main_refuses_reads_that_are_not_the_registered_shape(reads):
    with pytest.raises(SystemExit, match="refuse"):     # synthetic reads have 30 cells / 15 clusters, not 106 / 71
        _main(reads, reads["t"] / "v2.txt")
    e1 = json.loads(reads["e1"].read_text())
    bad = V.check_read(e1, "e1_106", 30, 15, "set", ("C1", "C2", "C3", "EPF", "C2S5"))
    assert bad == []
    e2 = copy.deepcopy(e1)
    e2["boot"] = 500
    assert any("bootstrap" in b for b in V.check_read(e2, "e1_106", 30, 15, "set", ("C1",)))
    e2 = copy.deepcopy(e1)
    e2["arms"]["C2"]["runs"] = e2["arms"]["C2"]["runs"][:4]
    assert any("seeds" in b for b in V.check_read(e2, "e1_106", 30, 15, "set", ("C1",)))
    assert any("labels" in b for b in V.check_read(e1, "e1_106", 30, 15, "v0", ("C1",)))
