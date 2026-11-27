"""T5 CPU pre-checks on the 532 cv5v2 pool cells (train + val; no test50, no e1).
A) stride quantisation ceiling for crack: best block-wise (2x2 / 4x4 aligned) reconstruction IoU of the GT.
B) single-channel cue separability: pixel AUROC crack vs negatives, overall, vs line-like structures, and on
   low-contrast crack px; per source for raw and the best cues.
"""
import sys, os, numpy as np
from PIL import Image
from scipy import ndimage as ndi
from skimage.filters import frangi

BENCH = os.path.expanduser("~/mtp/research/team_2026-11-12_frontier/benchmark")
IMG = os.path.expanduser("~/mtp/datasets/BenchmarkELimages/dataset_20211104")
rows = [l.rstrip("\n").split("\t") for l in open(f"{BENCH}/cells.tsv")]
hdr = rows[0]; rows = [dict(zip(hdr, r)) for r in rows[1:]]
pool = [r for r in rows if r["bench_set"].startswith("cv5v2:")]
assert len(pool) == 532, len(pool)
assert not any(r["bench_set"] in ("test50", "e1_106") for r in pool)

def img_path(stem):
    for d in ("images_train_original", "images_val"):
        p = f"{IMG}/{d}/{stem}.png"
        if os.path.exists(p):
            return p
    raise FileNotFoundError(stem)

CRACK, PAD, IGN = 14, 7, 255
LINES = (4, 5, 9, 15)  # ribbons, border, busbars, gridline

# ---------- A) quantisation ceiling ----------
qa = {}
for f in (2, 4):
    for k in range(1, f * f + 1):
        qa[(f, k)] = [0, 0, 0]  # inter, union parts
gt_total = 0
for r in pool:
    m = np.array(Image.open(f"{BENCH}/out/masks_v11/masks/{r['stem']}.png"))
    c = (m == CRACK)
    if not c.any():
        continue
    valid = m != IGN
    gt_total += c.sum()
    for f in (2, 4):
        s = c.reshape(512 // f, f, 512 // f, f).sum((1, 3))
        for k in range(1, f * f + 1):
            b = np.kron(s >= k, np.ones((f, f), bool)) & valid
            i = (b & c).sum(); u = (b | c).sum()
            qa[(f, k)][0] += i; qa[(f, k)][1] += u; qa[(f, k)][2] += b.sum()
print("A) crack GT px in pool:", gt_total)
for (f, k), (i, u, p) in qa.items():
    print(f"   stride {f}, block on if >= {k} of {f*f} px: IoU {i/u:.3f}  pred/GT px {p/gt_total:.2f}")

# ---------- B) cue separability ----------
def liot_dark(I):
    """LIOT-style contrast-invariant count: number of the 32 (4 dirs x d=1..8) neighbours brighter than p."""
    P = np.pad(I, 8, mode="edge"); n = np.zeros(I.shape, np.int16)
    for d in range(1, 9):
        for dy, dx in ((0, -d), (0, d), (-d, 0), (d, 0)):
            n += (P[8 + dy:8 + dy + 512, 8 + dx:8 + dx + 512] > I)
    return n.astype(np.float32)

def hessian_ridge(I):
    out = np.zeros(I.shape, np.float32)
    for s in (1.0, 1.5, 2.0, 3.0):
        hxx = ndi.gaussian_filter(I, s, order=(0, 2)); hyy = ndi.gaussian_filter(I, s, order=(2, 0))
        hxy = ndi.gaussian_filter(I, s, order=(1, 1))
        tr = hxx + hyy; det = np.sqrt((hxx - hyy) ** 2 + 4 * hxy ** 2)
        l_hi = 0.5 * (tr + det)  # largest eigenvalue: positive across a dark line
        out = np.maximum(out, s * s * np.clip(l_hi, 0, None))
    return out

def notch(I):
    """Zero strong periodic peaks on the two frequency axes (finger / busbar periodicity), keep DC band."""
    F = np.fft.fft2(I); A = np.abs(F); M = np.ones_like(A)
    for axis in (0, 1):
        line = A[:, 0] if axis == 0 else A[0, :]
        med = np.median(line[4:-4]) + 1e-6
        idx = np.where(line > 5 * med)[0]
        idx = idx[(idx >= 4) & (idx <= 512 - 4)]
        for j in idx:
            if axis == 0:
                M[j, :] = 0
            else:
                M[:, j] = 0
    M[:4, :4] = M[:4, -4:] = M[-4:, :4] = M[-4:, -4:] = 1
    return np.real(np.fft.ifft2(F * M)).astype(np.float32)

def cues(I):
    I = I.astype(np.float32)
    med = ndi.median_filter(I, 15) + 1.0
    clos = ndi.grey_closing(I, size=(9, 9))
    bc = ndi.zoom(ndi.maximum_filter(I, 8)[4::8, 4::8], 8, order=1)[:512, :512]
    J = notch(I)
    return {
        "raw_dark": -I,
        "rel_dark15": (med - I) / med,
        "blackhat9": clos - I,
        "blackhat9_rel": (clos - I) / (clos + 1.0),
        "hessian_ridge": hessian_ridge(I / med.mean()),
        "frangi": frangi(I, sigmas=(1, 1.5, 2, 2.5), black_ridges=True).astype(np.float32),
        "liot_count": liot_dark(I),
        "crackcue_coarse": (bc - I) / (bc + 1.0),
        "notch_blackhat9": ndi.grey_closing(J, size=(9, 9)) - J,
    }

rng = np.random.default_rng(0)
store = {}  # cue -> lists
def add(key, arr):
    store.setdefault(key, []).append(arr)

n_cells = 0
for r in pool:
    m = np.array(Image.open(f"{BENCH}/out/masks_v11/masks/{r['stem']}.png"))
    c = m == CRACK
    if c.sum() < 20:
        continue
    I = np.array(Image.open(img_path(r["stem"])).convert("L"))
    assert I.shape == (512, 512)
    n_cells += 1
    neg = (m != CRACK) & (m != PAD) & (m != IGN) & ~ndi.binary_dilation(c, iterations=2)
    lines = np.isin(m, LINES) & neg
    med = ndi.median_filter(I.astype(np.float32), 15) + 1.0
    lowc = c & (((med - I) / med) < 0.02)
    ni = np.flatnonzero(neg); ni = rng.choice(ni, min(4000, ni.size), replace=False)
    li = np.flatnonzero(lines); li = rng.choice(li, min(1000, li.size), replace=False) if li.size else li
    ci = np.flatnonzero(c); lo = np.flatnonzero(lowc)
    for name, v in cues(I).items():
        v = v.ravel()
        add((name, "pos", r["source"]), v[ci]); add((name, "neg", r["source"]), v[ni])
        add((name, "lines", r["source"]), v[li]); add((name, "lowc", r["source"]), v[lo])

def auroc(p, n):
    if p.size == 0 or n.size == 0:
        return float("nan")
    x = np.concatenate([p, n]); rk = ndi.rank_filter if False else None
    from scipy.stats import rankdata
    R = rankdata(x)[: p.size].sum()
    return (R - p.size * (p.size + 1) / 2) / (p.size * n.size)

def cat(name, kind, src=None):
    ks = [k for k in store if k[0] == name and k[1] == kind and (src is None or k[2] == src)]
    return np.concatenate([np.concatenate(store[k]) for k in ks]) if ks else np.array([])

names = sorted({k[0] for k in store})
srcs = sorted({k[2] for k in store})
print(f"B) cells with >= 20 crack px: {n_cells}; crack px {cat('raw_dark','pos').size}, low-contrast crack px {cat('raw_dark','lowc').size}")
print(f"   {'cue':18s} AUROC_all  AUROC_vs_lines  AUROC_lowcontrast  per-source AUROC_all ({' '.join(srcs)})  spread")
for nm in names:
    p, n, l, lc = cat(nm, "pos"), cat(nm, "neg"), cat(nm, "lines"), cat(nm, "lowc")
    per = [auroc(cat(nm, "pos", s), cat(nm, "neg", s)) for s in srcs]
    print(f"   {nm:18s} {auroc(p,n):.3f}      {auroc(p,l):.3f}           {auroc(lc,n):.3f}             "
          + " ".join(f"{a:.3f}" for a in per) + f"   {np.nanmax(per)-np.nanmin(per):.3f}")
