"""Quick look: image + colour-coded mask for a few stems. usage: python -I peek.py <root> <out.png> split:stem ..."""

from __future__ import annotations

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from common import class_names, load_image, load_mask  # noqa: E402


def main() -> None:
    root, out = Path(sys.argv[1]), Path(sys.argv[2])
    items = [a.split(":") for a in sys.argv[3:]]
    rows = list(csv.DictReader(open(root / "ListOfClassesAndColorCodes_20211104.csv")))
    lut = np.zeros((24, 3), np.uint8)
    for r in rows:
        lut[int(r["Label"])] = [int(r["Red"]), int(r["Green"]), int(r["Blue"])]
    names = class_names(root)
    fig, axes = plt.subplots(len(items), 2, figsize=(10, 5 * len(items)))
    axes = np.atleast_2d(axes)
    for i, (split, stem) in enumerate(items):
        im, m = load_image(root, split, stem), load_mask(root, split, stem)
        axes[i, 0].imshow(im, cmap="gray", vmin=0, vmax=255)
        axes[i, 0].set_title(f"{split}/{stem}")
        axes[i, 1].imshow(lut[m])
        present = [f"{c}:{names[c]}" for c in np.unique(m)]
        axes[i, 1].set_title(", ".join(present), fontsize=7)
        for a in axes[i]:
            a.axis("off")
    plt.tight_layout()
    plt.savefig(out, dpi=70)


if __name__ == "__main__":
    main()
