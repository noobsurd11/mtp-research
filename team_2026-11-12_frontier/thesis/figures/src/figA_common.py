"""fig_maker_A shared helpers: style, source-line lookup, saving, data CSVs.

Rules kept here:
- Every plotted number is parsed from a result text / json file or a table. find() returns the matching line and its number,
  and it fails unless the pattern matches exactly one line (inside the named section when one is given).
- Only result text / json files and tables are opened (no E1 or test50 dump, label, prediction or image).
- Output goes to thesis/figures/ only: F<n>.pdf, F<n>.png (200 dpi), F<n>_data.csv.
Style: Okabe-Ito colours (the palette fig_maker_B also uses), PF / reference in grey, sans 9 pt, 15 cm wide, no titles.
"""
from __future__ import annotations

import csv
import json
import os
import re
from dataclasses import dataclass

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

T = "/home/yugma/mtp/research/team_2026-11-12_frontier"
FIG = os.path.join(T, "thesis", "figures")
CM = 1 / 2.54
WIDTH = 15 * CM  # 15 cm text width

# Okabe-Ito (colour-blind safe); grey = PF / reference
GREY = "#999999"
DARK = "#222222"
MUTED = "#555555"
GRID = "#e5e5e5"
BLUE = "#0072B2"
VERM = "#D55E00"
GREEN = "#009E73"
PURPLE = "#CC79A7"
ORANGE = "#E69F00"
BAND = "#eeeeee"

ARM_COLOR = {"C1": GREY, "PF": GREY, "C2": BLUE, "CS_D4": BLUE, "C1-D4": VERM, "PF_D4": VERM,
             "C3": GREEN, "CS": GREEN, "E-PF": PURPLE}
ARM_MARK = {"C1": "o", "PF": "o", "C2": "s", "CS_D4": "s", "C1-D4": "D", "PF_D4": "D", "C3": "^", "CS": "^", "E-PF": "v"}

NUM = r"[+-]?\d+\.\d+"
IV = rf"({NUM}) \[({NUM}), ({NUM})\]"  # value [lo, hi]


def setup() -> None:
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["DejaVu Sans"],
        "font.size": 9, "axes.labelsize": 9, "xtick.labelsize": 9, "ytick.labelsize": 9,
        "legend.fontsize": 8, "legend.frameon": False, "legend.handlelength": 1.6,
        "axes.spines.top": False, "axes.spines.right": False, "axes.linewidth": 0.6,
        "axes.edgecolor": DARK, "axes.labelcolor": DARK, "text.color": DARK,
        "xtick.color": DARK, "ytick.color": DARK, "xtick.major.width": 0.6, "ytick.major.width": 0.6,
        "xtick.major.size": 3, "ytick.major.size": 3,
        "axes.axisbelow": True, "grid.color": GRID, "grid.linewidth": 0.6,
        "lines.linewidth": 1.0, "lines.markersize": 4.5, "errorbar.capsize": 0,
        "pdf.fonttype": 42, "ps.fonttype": 42, "savefig.dpi": 200,
        "figure.dpi": 100,
    })


_LINES: dict[str, list[str]] = {}


def lines(rel: str) -> list[str]:
    if rel not in _LINES:
        with open(os.path.join(T, rel), encoding="utf-8") as f:
            _LINES[rel] = f.read().split("\n")
    return _LINES[rel]


@dataclass
class Hit:
    path: str   # relative to T
    line: int   # 1-based
    text: str
    groups: tuple

    @property
    def src(self) -> str:
        return f"{self.path}:{self.line}"

    def f(self, i: int) -> float:
        return num(self.groups[i])


def _section_range(ls: list[str], section: str | None) -> tuple[int, int]:
    if section is None:
        return 0, len(ls)
    hs = [i for i, l in enumerate(ls) if re.search(section, l)]
    if len(hs) != 1:
        raise RuntimeError(f"section {section!r}: {len(hs)} header matches")
    s = hs[0]
    e = len(ls)
    for j in range(s + 1, len(ls)):
        if ls[j].startswith("## ") or ls[j].startswith("### "):
            e = j
            break
    return s, e


def find(rel: str, pattern: str, section: str | None = None) -> Hit:
    """The one line of file rel (inside section, if given) that matches pattern; groups parsed by the caller."""
    ls = lines(rel)
    s, e = _section_range(ls, section)
    hits = [(i, re.search(pattern, ls[i])) for i in range(s, e)]
    hits = [(i, m) for i, m in hits if m]
    if len(hits) != 1:
        raise RuntimeError(f"{rel}: pattern {pattern!r} (section {section!r}) matched {len(hits)} lines")
    i, m = hits[0]
    return Hit(rel, i + 1, ls[i], m.groups())


def num(s: str) -> float:
    return float(s.replace("+", ""))


def load_json(rel: str):
    with open(os.path.join(T, rel), encoding="utf-8") as f:
        return json.load(f)


def save(fig, n: str) -> None:
    pdf = os.path.join(FIG, f"{n}.pdf")
    png = os.path.join(FIG, f"{n}.png")
    # bbox tight + 0.03 in pad: text placed outside the axes (value columns, labels at the edge) can never be clipped,
    # in the PDF as well as in the PNG (their text metrics differ slightly).
    fig.savefig(pdf, bbox_inches="tight", pad_inches=0.03,
                metadata={"CreationDate": None, "ModDate": None, "Creator": f"fig_maker_A make_{n}.py"})
    fig.savefig(png, dpi=200, bbox_inches="tight", pad_inches=0.03, metadata={"Software": None})
    plt.close(fig)


def write_csv(n: str, header: list[str], rows: list[list]) -> None:
    with open(os.path.join(FIG, f"{n}_data.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(header)
        for r in rows:
            w.writerow(r)


def zero_line(ax, axis: str = "x") -> None:
    (ax.axvline if axis == "x" else ax.axhline)(0, color=DARK, lw=0.7, zorder=1)


def m_line(ax, m: float, axis: str = "x", label: bool = True) -> None:
    (ax.axvline if axis == "x" else ax.axhline)(m, color=DARK, lw=0.8, ls=(0, (4, 2.5)), zorder=1)


def fmt_signed(v: float, nd: int = 4) -> str:
    return f"{v:+.{nd}f}"
