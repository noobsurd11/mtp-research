"""AI-rater check of the dataset-audit label-error candidates: shared code (data access, crop rule, panel renderer).
Reads only pool cells, through the audit's guarded loaders (dataset_audit/scripts/common.py, imported read-only).
CPU only. Run with: nice -n 19 /home/noob/work/el-fault-detection/.venv/bin/python -I <script>."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage as ndi

AUDIT_SCRIPTS = "/home/yugma/mtp/research/team_2026-11-12_frontier/dataset_audit/scripts"
sys.path.insert(0, AUDIT_SCRIPTS)
import common as C  # noqa: E402  (audit loaders; pool_stems() fails closed on sealed stems)

RATER = C.AUDIT / "rater"
PANELS = RATER / "panels"
KEYDIR = RATER / "key"
EXAMPLES = RATER / "brief_examples"
CONS_T = 13                     # consensus overlay = majority of the 25 models (as in the audit gallery)
TILE = 360                      # enlarged tile side (display px)
CTX = 256                       # context tile side (whole 512 image at 0.5x)
CROP_MIN, CROP_MAX, CROP_PAD = 96, 288, 48
COL_CRACK = (255, 40, 40)       # red outline: crack (3-px band around the centreline)
COL_INACT = (40, 120, 255)      # blue outline + light blue tint: inactive area
COL_BRACKET = (0, 210, 0)       # green corner brackets: the disputed region
COL_BOX = (255, 150, 0)         # orange box on the context tile: the window
TINT = 0.22                     # strength of the inactive tint
MIN_RANGE = 64                  # contrast stretch never amplifies more than 255 / 64
BG = (24, 24, 24)
ALLOWED_PLACE = (0, 9)          # v1.1 classes a planted fake may sit on: background (cell area), busbars


def font(size=14):
    try:
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size)
    except OSError:
        return ImageFont.load_default(size=size)


def load_cell(stem: str, pool: set) -> dict:
    """grey image, v1.1 label, label crack / inactive masks, 25-model consensus masks and vote maps (pool cells only)."""
    C.guard(stem, pool)
    gt = C.mask_v11(stem)
    z = np.load(C.CACHE / "cons" / f"{stem}.npz")
    keep = gt != C.IGN
    d = {"stem": stem, "grey": C.grey(stem), "gt": gt, "keep": keep, "valid": keep & (gt != 7),
         "vc": z["vc"], "vi": z["vi"], "ncov": z["ncov"], "ign": z["ign"]}
    d["lab_crack"] = (gt == C.CRACK) & keep
    d["lab_inact"] = (gt == C.INACT) & keep
    d["con_crack"] = (z["vc"] >= CONS_T) & keep
    d["con_inact"] = (z["vi"] >= CONS_T) & keep
    return d


def crop_window(bbox, size=512):
    """Square window around bbox [y0, x0, y1, x1] (inclusive): side = clip(extent + 48, 96, 288); shifted, never shrunk, at the edge."""
    y0, x0, y1, x1 = bbox
    ext = max(y1 - y0 + 1, x1 - x0 + 1)
    side = int(np.clip(ext + CROP_PAD, CROP_MIN, CROP_MAX))
    cy, cx = (y0 + y1 + 1) / 2.0, (x0 + x1 + 1) / 2.0
    wy0 = int(round(cy - side / 2.0))
    wx0 = int(round(cx - side / 2.0))
    wy0 = min(max(wy0, 0), size - side)
    wx0 = min(max(wx0, 0), size - side)
    return wy0, wx0, side


def disp_crack(m: np.ndarray) -> np.ndarray:
    """Crack drawn identically for label and model: the centreline (frozen bench skeleton), dilated to a 3-px band."""
    if not m.any():
        return m.copy()
    sk = C.skeletonize(m)
    return ndi.binary_dilation(sk, structure=np.ones((3, 3), bool))


def _up(m: np.ndarray) -> np.ndarray:
    return np.array(Image.fromarray(m.astype(np.uint8) * 255).resize((TILE, TILE), Image.NEAREST)) > 0


def _outline(m: np.ndarray, it=2) -> np.ndarray:
    if not m.any():
        return m
    return m & ~ndi.binary_erosion(m, iterations=it, border_value=1)


def _brackets(dr: ImageDraw.ImageDraw, box, col=COL_BRACKET, w=3):
    y0, x0, y1, x1 = box
    arm = max(8, int(0.25 * min(y1 - y0, x1 - x0)))
    arm = min(arm, 22)
    for (x, y, dx, dy) in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
        dr.line([(x, y), (x + dx * arm, y)], fill=col, width=w)
        dr.line([(x, y), (x, y + dy * arm)], fill=col, width=w)


def stretch_lut(grey: np.ndarray, valid: np.ndarray) -> np.ndarray:
    """Contrast stretch fixed per image (not per window): grey 1st..99th percentile of the non-padding px -> 0..255,
    with a range of at least MIN_RANGE grey levels, so a uniform bright window is not blown up into noise."""
    v = grey[valid] if valid is not None and valid.any() else grey.ravel()
    lo, hi = np.percentile(v, [1, 99])
    if hi - lo < MIN_RANGE:
        c = (lo + hi) / 2.0
        lo, hi = c - MIN_RANGE / 2.0, c + MIN_RANGE / 2.0
    x = np.arange(256, dtype=np.float32)
    return np.clip((x - lo) * 255.0 / (hi - lo), 0, 255).astype(np.uint8)


def render_panel(pid: str, grey: np.ndarray, ovA: tuple, ovB: tuple, dispute_bbox, out_path, valid=None):
    """One panel. ovA / ovB = (crack_mask, inactive_mask) over the full 512 x 512 image (raw binary masks; the crack is
    drawn as disp_crack, computed on the window plus an 8-px margin). dispute_bbox = [y0, x0, y1, x1] (full-image coords).
    Layout: row 1 = context (whole image, 0.5x, orange window box) | window at native 1:1 | legend;
    row 2 = window enlarged (Lanczos) with the per-image contrast stretch and no overlay | same + overlay A | same + B."""
    wy0, wx0, side = crop_window(dispute_bbox)
    sl = (slice(wy0, wy0 + side), slice(wx0, wx0 + side))
    g = grey[sl]
    my0, mx0 = max(wy0 - 8, 0), max(wx0 - 8, 0)
    msl = (slice(my0, min(wy0 + side + 8, 512)), slice(mx0, min(wx0 + side + 8, 512)))
    inner = (slice(wy0 - my0, wy0 - my0 + side), slice(wx0 - mx0, wx0 - mx0 + side))
    ovA = (disp_crack(ovA[0][msl])[inner], ovA[1][sl])
    ovB = (disp_crack(ovB[0][msl])[inner], ovB[1][sl])
    s = TILE / side
    by0, bx0, by1, bx1 = dispute_bbox
    bb = (int((by0 - wy0) * s) - 5, int((bx0 - wx0) * s) - 5, int((by1 + 1 - wy0) * s) + 4, int((bx1 + 1 - wx0) * s) + 4)
    bb = tuple(int(np.clip(v, 1, TILE - 2)) for v in bb)
    lut = stretch_lut(grey, valid)
    base = Image.fromarray(lut[g]).resize((TILE, TILE), Image.LANCZOS).convert("RGB")
    tiles = []
    for ov in (None, ovA, ovB):
        t = base.copy()
        if ov is not None:
            a = np.array(t).astype(np.float32)
            ui = _up(ov[1])
            a[ui] = (1 - TINT) * a[ui] + TINT * np.array(COL_INACT, np.float32)
            a = a.astype(np.uint8)
            a[_outline(ui)] = COL_INACT
            a[_outline(_up(ov[0]))] = COL_CRACK
            t = Image.fromarray(a)
        _brackets(ImageDraw.Draw(t), bb)
        tiles.append(t)
    ctx = Image.fromarray(grey).resize((CTX, CTX), Image.LANCZOS).convert("RGB")
    ImageDraw.Draw(ctx).rectangle([wx0 / 2, wy0 / 2, (wx0 + side) / 2 - 1, (wy0 + side) / 2 - 1], outline=COL_BOX, width=2)
    nat = Image.fromarray(g).convert("RGB")
    pad, cap = 8, 20
    W = 3 * TILE + 4 * pad
    H = pad + cap + max(CTX, CROP_MAX) + pad + cap + TILE + pad
    P = Image.new("RGB", (W, H), BG)
    dr = ImageDraw.Draw(P)
    f, fb = font(14), font(18)
    y = pad
    dr.text((pad, y), "context (whole image, 0.5x)", fill=(220, 220, 220), font=f)
    dr.text((pad + CTX + 2 * pad, y), "window, native 1:1", fill=(220, 220, 220), font=f)
    P.paste(ctx, (pad, y + cap))
    P.paste(nat, (pad + CTX + 2 * pad, y + cap))
    lx = pad + CTX + 2 * pad + CROP_MAX + 3 * pad
    lines = [(f"panel {pid}", fb, (255, 255, 255)),
             ("A, B: two annotations of the window;", f, (220, 220, 220)),
             ("which one is the dataset label is hidden.", f, (220, 220, 220)),
             ("red outline = crack (band around its centreline)", f, COL_CRACK),
             ("blue outline + tint = inactive area", f, COL_INACT),
             ("green brackets = region to judge", f, COL_BRACKET),
             ("orange box (context) = the window", f, COL_BOX),
             ("judge only inside the brackets", f, (220, 220, 220))]
    ly = y + cap
    for txt, ff, col in lines:
        dr.text((lx, ly), txt, fill=col, font=ff)
        ly += 26 if ff is fb else 20
    y2 = y + cap + max(CTX, CROP_MAX) + pad
    for i, (t, name) in enumerate(zip(tiles, ("window enlarged, contrast-stretched", "A", "B"))):
        x = pad + i * (TILE + pad)
        dr.text((x, y2), name, fill=(255, 255, 255), font=fb if name in ("A", "B") else f)
        P.paste(t, (x, y2 + cap))
    P.save(out_path, format="PNG", optimize=True)   # no text chunks: nothing but pixels
    return (wy0, wx0, side)


def bbox_of(m: np.ndarray):
    yx = np.argwhere(m)
    return [int(yx[:, 0].min()), int(yx[:, 1].min()), int(yx[:, 0].max()), int(yx[:, 1].max())]


def disc(r: int) -> np.ndarray:
    y, x = np.ogrid[-r:r + 1, -r:r + 1]
    return (y * y + x * x) <= r * r
