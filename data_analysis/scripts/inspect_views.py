"""Close-up views for manual inspection.

usage: python -I inspect_views.py <root> <out.png> <ncols> split:stem[:y0:y1:x0:x1] ...
Each item: raw crop and crop with crack label (red) / inactive outline (yellow), nearest-neighbour upscaled.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from common import load_image, load_mask  # noqa: E402
from figures import overlay_rgb  # noqa: E402


def main() -> None:
    root, out, ncols = Path(sys.argv[1]), Path(sys.argv[2]), int(sys.argv[3])
    items = sys.argv[4:]
    n = len(items)
    nrows = int(np.ceil(n / ncols))
    fig, ax = plt.subplots(nrows, 2 * ncols, figsize=(5 * ncols, 2.6 * nrows))
    ax = np.atleast_2d(ax)
    for i, it in enumerate(items):
        p = it.split(":")
        split, stem = p[0], p[1]
        img, m = load_image(root, split, stem), load_mask(root, split, stem)
        if len(p) == 6:
            y0, y1, x0, x1 = map(int, p[2:])
        else:
            y0, y1, x0, x1 = 0, 512, 0, 512
        sl = (slice(y0, y1), slice(x0, x1))
        a, b = ax[i // ncols, (i % ncols) * 2], ax[i // ncols, (i % ncols) * 2 + 1]
        a.imshow(img[sl], cmap="gray", interpolation="nearest")
        a.set_title(f"{split}/{stem} [{y0}:{y1},{x0}:{x1}]", fontsize=6)
        b.imshow(overlay_rgb(img[sl], m[sl]), interpolation="nearest")
        a.axis("off")
        b.axis("off")
    for j in range(n, nrows * ncols):
        ax[j // ncols, (j % ncols) * 2].axis("off")
        ax[j // ncols, (j % ncols) * 2 + 1].axis("off")
    plt.tight_layout()
    plt.savefig(out, dpi=90)


if __name__ == "__main__":
    main()
