"""elbench method cards: one YAML per method, bench/methods/<name>.yaml. Read by the registry user (train opts), the queue's
cfgcheck and the dump manifest. Needs PyYAML only (no torch).

Schema (all keys required unless marked optional; bench/methods/SCHEMA.md has the prose):
  name            str, = file stem
  version         int
  family          str (free tag, e.g. "cnn-unetpp", "vit-dpt", "external-nnunet")
  papers          list of paper ids (doi:..., arXiv:...); [] for house methods
  kind            harness | external
  config          harness only: the base YAML passed to scripts/train.py --config (repo-relative)
  opts            harness only: list of --opts tokens WITHOUT seed, run_name, data.root (the queue adds those three)
  weights         list of {path, md5} files the build reads at training time ([] if none); md5 = full 32 hex
  weights_key     model | ema | teacher   (which state dict the dump reads)
  decision_rule   argmax24 (softmax heads) or a named rule implemented in bench_infer / the adapter
  memory          {peak_mib: int or null, gate_mib: int or null, source: str}; gate = peak + 2048 (rule), null = smoke first
  external        external only: {venv, train_cmd, infer_cmd, export}; null for harness
  diff_ref        optional: name of another card; cfgcheck also prints this card's config diff against it
  notes           optional str
"""
from __future__ import annotations

import copy
import hashlib
import json
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
REQUIRED = ("name", "version", "family", "papers", "kind", "weights", "weights_key", "decision_rule", "memory")
RESERVED = ("seed=", "run_name=", "data.root=")
WEIGHTS_KEYS = ("model", "ema", "teacher")
RULES = ("argmax24",)


def md5_file(p) -> str:
    return hashlib.md5(Path(p).read_bytes()).hexdigest()


def load_card(path) -> dict:
    path = Path(path)
    c = yaml.safe_load(path.read_text())
    errs = validate(c, path.stem)
    if errs:
        raise ValueError(f"card {path}: " + "; ".join(errs))
    return c


def validate(c: dict, stem: str | None = None) -> list[str]:
    e = [f"missing {k}" for k in REQUIRED if k not in c]
    if e:
        return e
    if stem is not None and c["name"] != stem:
        e.append(f"name {c['name']} != file stem {stem}")
    if c["kind"] not in ("harness", "external"):
        e.append("kind must be harness | external")
    if c["weights_key"] not in WEIGHTS_KEYS:
        e.append(f"weights_key must be one of {WEIGHTS_KEYS}")
    if c["decision_rule"] not in RULES:
        e.append(f"decision_rule must be one of {RULES}")
    if not isinstance(c["papers"], list):
        e.append("papers must be a list")
    for w in c["weights"] or []:
        if set(w) != {"path", "md5"} or len(str(w["md5"])) != 32:
            e.append(f"weights entry {w} needs path and a 32-hex md5")
    m = c["memory"] or {}
    if set(m) != {"peak_mib", "gate_mib", "source"}:
        e.append("memory needs peak_mib, gate_mib, source")
    elif m["peak_mib"] is not None and m["gate_mib"] is not None and m["gate_mib"] < m["peak_mib"] + 2048:
        e.append("memory.gate_mib < peak_mib + 2048")
    if c["kind"] == "harness":
        if "config" not in c or "opts" not in c:
            e.append("harness card needs config and opts")
        else:
            bad = [t for t in c["opts"] if any(t.startswith(r) for r in RESERVED) or "=" not in t]
            if bad:
                e.append(f"opts must not set seed / run_name / data.root and must be k=v: {bad}")
        if c.get("external") not in (None, {}):
            e.append("harness card: external must be null")
    else:
        x = c.get("external") or {}
        miss = [k for k in ("venv", "train_cmd", "infer_cmd", "export") if k not in x]
        if miss:
            e.append(f"external card needs external.{miss}")
    return e


def apply_opts(cfg: dict, opts: list[str]) -> dict:
    """Same as scripts/train.py apply_opts (e544133 l.92-101); tests assert equality on the house opts."""
    for kv in opts:
        k, _, v = kv.partition("=")
        keys = k.strip().split(".")
        node = cfg
        for part in keys[:-1]:
            node = node.setdefault(part, {})
        node[keys[-1]] = yaml.safe_load(v)
    return cfg


def run_opts(card: dict, seed: int, run_name: str, data_root: str) -> list[str]:
    assert card["kind"] == "harness"
    return [f"seed={int(seed)}", *card["opts"], f"data.root={data_root}", f"run_name={run_name}"]


def expected_config(card: dict, seed: int, run_name: str, data_root: str) -> dict:
    """The config_used.yaml scripts/train.py writes for this card's run (load_config + apply_opts + run_name)."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("elbench_config", REPO / "src" / "utils" / "config.py")
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)   # yaml only; avoids src.utils' torch import
    cfg = apply_opts(mod.load_config(REPO / card["config"]), run_opts(card, seed, run_name, data_root))
    cfg["run_name"] = run_name
    return cfg


def _flat(d, pre=""):
    out = {}
    for k, v in d.items():
        if isinstance(v, dict):
            out.update(_flat(v, f"{pre}{k}."))
        else:
            out[f"{pre}{k}"] = v
    return out


def config_diff(a: dict, b: dict) -> list[str]:
    fa, fb = _flat(a), _flat(b)
    return [f"{k}: {fa.get(k, '<absent>')!r} -> {fb.get(k, '<absent>')!r}" for k in sorted(set(fa) | set(fb))
            if fa.get(k, "<absent>") != fb.get(k, "<absent>")]


def cfgcheck(card: dict, config_used: Path, seed: int, run_name: str, data_root: str) -> list[str]:
    """[] if the run's config_used.yaml equals the card's expected config exactly (ignores logging.experiments_dir)."""
    got = yaml.safe_load(Path(config_used).read_text())
    want = expected_config(card, seed, run_name, data_root)
    for c in (got, want):
        c.get("logging", {}).pop("experiments_dir", None)
    return config_diff(want, got)


def main(argv=None) -> None:
    import argparse
    ap = argparse.ArgumentParser(prog="python -m bench.cards")
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("validate"); p.add_argument("cards", nargs="+")
    p = sp.add_parser("opts"); p.add_argument("card"); p.add_argument("--seed", type=int, required=True)
    p.add_argument("--run-name", required=True); p.add_argument("--data-root", required=True)
    p = sp.add_parser("cfgcheck"); p.add_argument("card"); p.add_argument("--config", required=True)
    p.add_argument("--seed", type=int, required=True); p.add_argument("--run-name", required=True)
    p.add_argument("--data-root", required=True)
    p = sp.add_parser("diff"); p.add_argument("card_a"); p.add_argument("card_b")
    p = sp.add_parser("render"); p.add_argument("card"); p.add_argument("--seed", type=int, required=True)
    p.add_argument("--run-name", required=True); p.add_argument("--data-root", required=True)
    a = ap.parse_args(argv)
    if a.cmd == "validate":
        bad = 0
        for f in a.cards:
            try:
                load_card(f); print(f"OK {f} md5 {md5_file(f)}")
            except ValueError as ex:
                bad += 1; print(f"INVALID {ex}")
        sys.exit(1 if bad else 0)
    if a.cmd == "opts":
        print(" ".join(run_opts(load_card(a.card), a.seed, a.run_name, a.data_root)))
    elif a.cmd == "cfgcheck":
        d = cfgcheck(load_card(a.card), Path(a.config), a.seed, a.run_name, a.data_root)
        print("config OK (= card)" if not d else f"CONFIG FAIL {len(d)}: {d}")
        sys.exit(1 if d else 0)
    elif a.cmd == "render":   # the config_used.yaml train.py would write (yaml.safe_dump, sort_keys=False, as train.py l.236)
        sys.stdout.write(yaml.safe_dump(expected_config(load_card(a.card), a.seed, a.run_name, a.data_root), sort_keys=False))
    elif a.cmd == "diff":
        ca, cb = load_card(a.card_a), load_card(a.card_b)
        print(json.dumps(config_diff(expected_config(ca, 0, "x", "R"), expected_config(cb, 0, "x", "R")), indent=1))


if __name__ == "__main__":
    main()
