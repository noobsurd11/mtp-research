"""YAML configuration loader with optional override merging."""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import yaml


def load_config(path: str | Path) -> dict[str, Any]:
    """Load a YAML config file.

    If the config contains a ``defaults:`` key listing parent config names,
    those are loaded first from the same directory and the current file's
    values are merged on top (shallow merge at the section level).

    Args:
        path: Path to the YAML configuration file.

    Returns:
        Merged config dict.
    """
    path = Path(path)
    with open(path) as f:
        cfg = yaml.safe_load(f) or {}

    # Handle simple inheritance via ``defaults: [base]``
    defaults = cfg.pop("defaults", [])
    if isinstance(defaults, str):
        defaults = [defaults]

    base: dict[str, Any] = {}
    for parent_name in defaults:
        parent_path = path.parent / f"{parent_name}.yaml"
        if parent_path.exists():
            parent_cfg = load_config(parent_path)
            base = _deep_merge(base, parent_cfg)

    return _deep_merge(base, cfg)


def merge_config(
    base: dict[str, Any],
    overrides: dict[str, Any],
) -> dict[str, Any]:
    """Return a new config with ``overrides`` applied on top of ``base``.

    Args:
        base:      Base configuration dict.
        overrides: Dict of values to overlay (nested dicts are merged).

    Returns:
        Merged config dict (``base`` is not mutated).
    """
    return _deep_merge(copy.deepcopy(base), overrides)


def _deep_merge(
    base: dict[str, Any],
    override: dict[str, Any],
) -> dict[str, Any]:
    """Recursively merge ``override`` into ``base``."""
    result = copy.deepcopy(base)
    for key, val in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(val, dict):
            result[key] = _deep_merge(result[key], val)
        else:
            result[key] = copy.deepcopy(val)
    return result
