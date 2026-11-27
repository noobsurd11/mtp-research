"""elbench x3: post-processing arms on prediction dumps (CPU). A method card opts in with the optional key
`postproc: {name: <one of POSTPROC>, script: <repo path>, uses_source_metadata: bool}`; cards without it are unchanged.
bench/cards.py does not read the key; validate_postproc() checks it (tests/test_bench_x3.py runs it on every card)."""
from __future__ import annotations

POSTPROC = {"src_calib": "scripts/bench_src_calib.py", "dti_hysteresis": "scripts/bench_dti.py"}


def validate_postproc(card: dict) -> list[str]:
    p = card.get("postproc")
    if p is None:
        return []
    e = []
    if set(p) != {"name", "script", "uses_source_metadata"}:
        e.append("postproc needs exactly name, script, uses_source_metadata")
        return e
    if p["name"] not in POSTPROC:
        e.append(f"postproc.name must be one of {sorted(POSTPROC)}")
    elif p["script"] != POSTPROC[p["name"]]:
        e.append(f"postproc.script for {p['name']} must be {POSTPROC[p['name']]}")
    if not isinstance(p["uses_source_metadata"], bool):
        e.append("postproc.uses_source_metadata must be true / false")
    if card.get("kind") != "harness" or card.get("decision_rule") != "argmax24":
        e.append("postproc cards: harness kind, decision_rule argmax24 (the dump stays the raw model output)")
    return e
