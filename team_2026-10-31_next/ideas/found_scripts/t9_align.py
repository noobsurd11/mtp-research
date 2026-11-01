"""T9 gate 2 (found, 31 Oct): integer shift between each _rf image and its pool copy (phase correlation), so _rf masks can score pool copies."""
from pathlib import Path
import numpy as np
from PIL import Image
RF = Path("/home/noob/work/calib/data/rf"); POOL = Path("/home/noob/work/el-fault-detection/data/unlabeled/images_512")
pool = {p.stem for p in POOL.glob("*.png")}
shifts = {}
for s in (l.strip() for l in open(RF / "stems_eval.txt") if l.strip()):
    b = s[:-3]
    if b not in pool:
        continue
    x = np.array(Image.open(RF / "images" / f"{s}.png").convert("L"), np.float64); y = np.array(Image.open(POOL / f"{b}.png").convert("L"), np.float64)
    X, Y = np.fft.fft2(x - x.mean()), np.fft.fft2(y - y.mean())
    R = X * np.conj(Y); R /= np.abs(R) + 1e-9
    c = np.abs(np.fft.ifft2(R)); i, j = np.unravel_index(c.argmax(), c.shape)
    di, dj = (i if i < 256 else i - 512), (j if j < 256 else j - 512)
    shifts[s] = (di, dj, c.max())
nz = {k: v for k, v in shifts.items() if v[:2] != (0, 0)}
print(f"cells {len(shifts)}; zero integer shift {len(shifts) - len(nz)}; nonzero {len(nz)}: {list(nz.items())[:10]}")
print("phase-corr peak min/median", min(v[2] for v in shifts.values()), np.median([v[2] for v in shifts.values()]))
