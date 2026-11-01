import json, numpy as np
from pathlib import Path
from PIL import Image
O = Path("/home/noob/work/found/s10"); D = Path("/home/noob/work/el_f3/data")
J = json.load(open(O / "prompts.json")); M = np.load(O / "model.npz"); S = np.load(O / "sam.npz")
un = lambda z, s: np.unpackbits(z[s])[: 512 * 512].reshape(512, 512).astype(bool)
for sp in ("oof", "val"):
    t = {"a": [0, 0], "b": [0, 0]}; g_all = 0
    for s in J["cells"][sp]:
        g = np.array(Image.open(D / "labeled" / "masks_escdd" / f"{s}.png")) == 11; g_all += int(g.sum())
        for v, z in (("a", M), ("b", S)):
            m = un(z, s); t[v][0] += int((m & g).sum()); t[v][1] += int(m.sum())
    print(sp, {v: {"P": round(tp / max(p, 1), 3), "R": round(tp / max(g_all, 1), 3), "pred_px": p} for v, (tp, p) in t.items()})
