"""Split-file loading.  A missing or empty split file is always an error."""

from __future__ import annotations

from pathlib import Path

import numpy as np


def load_split(path: str | Path) -> list[str]:
    """Read image stems (one per line) from a split file.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError:        If the file contains no stems.
    """
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"Split file not found: {path}")
    stems = [l.strip() for l in path.read_text().splitlines() if l.strip()]
    if not stems:
        raise ValueError(f"Split file is empty: {path}")
    return stems


def stratified_sample(names: list[str], strata: list, k: int, seed: int) -> list[str]:
    """Draw ``k`` of ``names`` so every stratum keeps its share (largest-remainder allocation).

    Per stratum the quota is ``k * n_s / N``; floors are taken and the remaining
    slots go to the largest fractional parts (ties broken by a seeded shuffle).
    Within a stratum the members are a seeded random choice.  Returned in the
    input order.  Deterministic for a given (names, strata, k, seed).
    """
    if len(names) != len(strata):
        raise ValueError("names and strata differ in length")
    if not 0 < k <= len(names):
        raise ValueError(f"k={k} out of range for {len(names)} names")
    rng = np.random.RandomState(seed)
    groups: dict = {}
    for i, s in enumerate(strata):
        groups.setdefault(s, []).append(i)
    keys = sorted(groups, key=str)
    n = len(names)
    quota = {s: k * len(groups[s]) / n for s in keys}
    take = {s: int(np.floor(quota[s])) for s in keys}
    rest = k - sum(take.values())
    order = list(rng.permutation(len(keys)))
    by_frac = sorted(range(len(keys)), key=lambda j: (-(quota[keys[j]] - take[keys[j]]), order[j]))
    for j in by_frac[:rest]:
        take[keys[j]] += 1
    chosen = []
    for s in keys:
        idx = groups[s]
        chosen += [idx[i] for i in rng.permutation(len(idx))[: take[s]]]
    chosen_set = set(chosen)
    return [names[i] for i in range(n) if i in chosen_set]
