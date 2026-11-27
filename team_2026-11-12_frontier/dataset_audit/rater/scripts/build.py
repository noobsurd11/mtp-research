"""Build the AI-rater panels (PREREG.md sections 3 and 5): the 124 image-supported candidates of the dataset audit plus 60
calibration items with known answers, shuffled under random IDs.
- Candidates: every row of out/a_candidates.tsv with supported == 1. Overlays: v1.1 label vs 25-model consensus (>= 13 of 25).
- Calibration: planted differences on clean regions of pool cells outside the 49 candidate cells (one plant per cell):
  crack SHIFT (8 px), crack DEL (segment removed), crack FAKE (polyline on clean material), inactive DEL (region removed),
  inactive FAKE (polygon on clean bright material); each planted either in the label (truth: label_error) or in the consensus
  overlay (truth: label_correct), 6 + 6 per type.
- IDs, A/B assignment (balanced within strata) and the three rater orders come from a secret seed (os.urandom) that is stored
  only in the key. Calibration selection uses the public seed SEL_SEED (it reveals no answer without the key).
Writes panels/<ID>.png, orders/ORDER_R{1,2,3}.txt, key/key.tsv, and build_log.txt (counts only, no stems).
Usage: nice -n 19 python -I build.py [--workers 4] [--seed HEX] [--force]"""
from __future__ import annotations

import argparse
import csv
import json
import multiprocessing as mp
import os
import random
import sys
import time

os.environ.setdefault("OMP_NUM_THREADS", "1")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402
from scipy import ndimage as ndi  # noqa: E402

import rcommon as R  # noqa: E402

C = R.C
SEL_SEED = 20261121
N_PER = 6                                  # items per (plant type, side)
SHIFT_PX = 8
ALPH = "ACDEFHJKLMNPRTUVWXY34679"
FAKE_SRC_QUOTA = {"crack": {"CSIR": 6, "CFVS": 4, "ARTS": 1, "BMRK": 1},   # follows the supported crack candidates' sources
                  "inact": {"CSIR": 6, "CFVS": 5, "BMRK": 1}}              # follows the supported inactive candidates' sources


def supported_candidates():
    rows = list(csv.DictReader(open(C.OUT / "a_candidates.tsv"), delimiter="\t"))
    out = []
    for rank, r in enumerate(rows):
        if r["supported"] != "1":
            continue
        r = dict(r)
        r["cand_row"] = rank + 1           # 1-based data row in a_candidates.tsv
        out.append(r)
    return out


def dist_to(m):
    if not m.any():
        return np.full(m.shape, 1e9)
    return ndi.distance_transform_edt(~m)


def window_clean(d, bbox):
    wy0, wx0, side = R.crop_window(bbox)
    return not d["ign"][wy0:wy0 + side, wx0:wx0 + side].any()


def zc(d, comp, excl):
    return C.contrast_z(d["grey"], comp, excl, d["valid"])


def shift_mask(m, v):
    dy, dx = v
    out = np.zeros_like(m)
    ys, xs = np.nonzero(m)
    ys2, xs2 = ys + dy, xs + dx
    ok = (ys2 >= 0) & (ys2 < 512) & (xs2 >= 0) & (xs2 < 512)
    if not ok.all():
        return None
    out[ys2, xs2] = True
    return out


def placement_ok(d, F, min_def=8, min_other=3):
    """F on clean cell area: classes background / busbar only, away from every crack / inactive label, consensus vote and
    other class, and not darker than its ring (z > -0.3)."""
    gt = d["gt"]
    if not d["keep"][F].all() or not np.isin(gt[F], R.ALLOWED_PLACE).all():
        return False
    defect = d["lab_crack"] | d["lab_inact"] | (d["vc"] >= 2) | (d["vi"] >= 2)
    if dist_to(defect)[F].min() < min_def:
        return False
    other = ~np.isin(gt, R.ALLOWED_PLACE)
    if dist_to(other)[F].min() < min_other:
        return False
    z = zc(d, F, d["lab_crack"] | d["con_crack"])
    return np.isfinite(z) and z > -0.3


def crack_clean_comps(d, min_cov=25):
    """v1.1 crack components >= 40 px with >= 95% of px having >= min_cov of the 25 models (default all 25) within 2 px,
    visibly dark (z <= -1)."""
    lg, n = ndi.label(d["lab_crack"], C.S8)
    out = []
    excl = d["lab_crack"] | d["con_crack"]
    for i in range(1, n + 1):
        K = lg == i
        m = int(K.sum())
        if m < 40 or (d["ncov"][K] >= min_cov).mean() < 0.95:
            continue
        z = zc(d, K, excl)
        if np.isfinite(z) and z <= -1.0:
            out.append((K, z))
    return out


def try_shift(d, K0, rng):
    """Shift a clean crack by 8 px along its normal: the whole component if it spans <= 90 px, else a segment of it
    (the component px within 20 to 35 px of a random centreline point). The shifted line must land on clean material:
    away from other cracks, model votes and inactive areas, >= 90% on background / busbar and none on a ribbon, not dark."""
    bb = R.bbox_of(K0)
    if max(bb[2] - bb[0], bb[3] - bb[1]) + 1 <= 90:
        segs = [K0]
    else:
        pts = np.argwhere(C.skeletonize(K0))
        segs = []
        for _ in range(4):
            p = pts[rng.integers(len(pts))]
            r = int(rng.integers(20, 36))
            yy, xx = np.ogrid[:512, :512]
            seg = K0 & (((yy - p[0]) ** 2 + (xx - p[1]) ** 2) <= r * r)
            if seg.sum() >= 30:
                segs.append(seg)
    for K in segs:
        yx = np.argwhere(K).astype(float)
        w, V = np.linalg.eigh(np.cov((yx - yx.mean(0)).T))
        nrm = V[:, 0]                                  # eigenvector of the smallest eigenvalue = normal of the main axis
        sgn = 1 if rng.random() < 0.5 else -1
        for s in (sgn, -sgn):
            v = (int(round(s * SHIFT_PX * nrm[0])), int(round(s * SHIFT_PX * nrm[1])))
            if abs(v[0]) + abs(v[1]) < 6:
                continue
            Kc = d["con_crack"] & ndi.binary_dilation(K, structure=R.disc(4))
            if K is not K0:                            # segment mode: the consensus part of the same stretch only
                Kc &= ndi.binary_dilation(K, structure=R.disc(4))
            KS, KcS = shift_mask(K, v), shift_mask(Kc, v)
            if KS is None or KcS is None or not Kc.any():
                continue
            halo = ndi.binary_dilation(K, structure=R.disc(6))     # only the moved stretch may be near its old place
            rest_l = d["lab_crack"] & ~K
            rest_c = d["con_crack"] & ~Kc
            both = KS | KcS
            if dist_to(rest_l & ~halo | (d["vc"] >= 2) & ~halo)[both].min() < 5 or dist_to(rest_c & ~halo)[both].min() < 5:
                continue
            if dist_to(d["lab_inact"] | d["con_inact"])[both].min() < 3:
                continue
            gtS = d["gt"][both]
            if not d["keep"][both].all() or (gtS == 4).any() or np.isin(gtS, R.ALLOWED_PLACE).mean() < 0.9:
                continue
            z = zc(d, KS, d["lab_crack"] | d["con_crack"])
            if not (np.isfinite(z) and z > -0.5):
                continue
            bbox = R.bbox_of(K | KS)
            if not window_clean(d, bbox):
                continue
            return {"K": K, "Kc": Kc, "KS": KS, "KcS": KcS, "v": v, "bbox": bbox, "z_shift": z,
                    "seg_mode": int(K is not K0), "seg_px": int(K.sum())}
    return None


def try_delete_seg(d, K, rng):
    sk = C.skeletonize(K)
    pts = np.argwhere(sk)
    if len(pts) == 0:
        return None
    for _ in range(6):
        p = pts[rng.integers(len(pts))]
        r = int(rng.integers(10, 21))
        yy, xx = np.ogrid[:512, :512]
        dsk = ((yy - p[0]) ** 2 + (xx - p[1]) ** 2) <= r * r
        seg = K & dsk
        if seg.sum() < 20:
            continue
        D = ndi.binary_dilation(seg, structure=R.disc(4))
        if (d["lab_crack"] & D & ~K).any():
            continue
        if (d["con_crack"] & D).sum() < 15:
            continue
        z = zc(d, seg, d["lab_crack"] | d["con_crack"])
        if not (np.isfinite(z) and z <= -1.0):
            continue
        bbox = R.bbox_of(D & (d["lab_crack"] | d["con_crack"]))
        if not window_clean(d, bbox):
            continue
        return {"D": D, "seg_px": int(seg.sum()), "r": r, "bbox": bbox, "z_seg": z}
    return None


def try_fake_crack(d, rng):
    pts = np.argwhere(np.isin(d["gt"], R.ALLOWED_PLACE) & d["keep"])
    if len(pts) == 0:
        return None
    for _ in range(60):
        y, x = pts[rng.integers(len(pts))].astype(float)
        ang = rng.uniform(0, np.pi)
        poly = [(x, y)]
        for k in range(3):
            L = rng.uniform(12, 28)
            if k:
                ang += rng.uniform(-0.5, 0.5)
            x, y = x + L * np.cos(ang), y + L * np.sin(ang)
            poly.append((x, y))
        im = Image.new("L", (512, 512), 0)
        ImageDraw.Draw(im).line(poly, fill=255, width=2)
        F = np.array(im) > 0
        if F.sum() < 30 or not placement_ok(d, F):
            continue
        bbox = R.bbox_of(F)
        if not window_clean(d, bbox):
            continue
        return {"F": F, "bbox": bbox, "len_px": int(F.sum())}
    return None


def try_fake_blob(d, rng):
    pts = np.argwhere(np.isin(d["gt"], R.ALLOWED_PLACE) & d["keep"])
    if len(pts) == 0:
        return None
    for _ in range(60):
        cy, cx = pts[rng.integers(len(pts))].astype(float)
        k = int(rng.integers(4, 7))
        ang = np.sort(rng.uniform(0, 2 * np.pi, k))
        rad = rng.uniform(10, 22, k)
        poly = [(cx + r * np.cos(a), cy + r * np.sin(a)) for a, r in zip(ang, rad)]
        im = Image.new("L", (512, 512), 0)
        ImageDraw.Draw(im).polygon(poly, fill=255)
        B = np.array(im) > 0
        if B.sum() < 250 or not placement_ok(d, B, min_def=6, min_other=2):
            continue
        bbox = R.bbox_of(B)
        if not window_clean(d, bbox):
            continue
        return {"B": B, "bbox": bbox, "area": int(B.sum())}
    return None


def inact_clean_regions(d):
    li, n = ndi.label(d["lab_inact"], C.S8)
    out = []
    for i in range(1, n + 1):
        I = li == i
        m = int(I.sum())
        if m < 200 or m > 6000:
            continue
        bb = R.bbox_of(I)
        if max(bb[2] - bb[0], bb[3] - bb[1]) + 1 > 200:
            continue
        if (d["vi"][I] >= 20).mean() < 0.8:
            continue
        z = zc(d, I, d["lab_inact"] | d["con_inact"])
        if not (np.isfinite(z) and z <= -1.0):
            continue
        if not window_clean(d, bb):
            continue
        out.append((I, z, bb))
    return out


def select_calibration(stems, pool, exclude, excl_groups):
    """Returns a list of calibration item specs (no rendering yet). Deterministic given SEL_SEED and the data.
    exclude: the 49 rated cells (never used). excl_groups: cv5v3 groups (modules) of the rated cells, avoided by every
    type except inactive DEL (clean inactive regions are too rare; 9 of its 12 cells share a module with a rated cell)."""
    rng = np.random.default_rng(SEL_SEED)
    order = list(stems)
    rng.shuffle(order)
    g3 = C.groups(C.G3)
    in_rated_group = {s for s in stems if g3[s]["group"] in excl_groups}
    used = set()
    items = []
    # ---- inactive DEL on clean regions (rare: up to 2 regions per cell allowed)
    need = {"L": N_PER, "C": N_PER}
    per_cell = {}
    side_cycle = ["L", "C"]
    j = 0
    regions = []
    for s in order:
        if s in exclude or s in used:
            continue
        d = R.load_cell(s, pool)
        if not d["lab_inact"].any():
            continue
        for I, z, bb in inact_clean_regions(d):
            regions.append((s, I, z, bb))
    # one region per cell first, then a second region per cell if still needed
    first, second = [], []
    seen = set()
    for r in regions:
        (second if r[0] in seen else first).append(r)
        seen.add(r[0])
    for s, I, z, bb in first + second:
        if need["L"] == 0 and need["C"] == 0:
            break
        if per_cell.get(s, 0) >= 2:
            continue
        side = side_cycle[j % 2]
        if need[side] == 0:
            side = "C" if side == "L" else "L"
        j += 1
        need[side] -= 1
        per_cell[s] = per_cell.get(s, 0) + 1
        items.append({"stem": s, "cls": "inact", "plant": "DEL", "side": side, "I": I, "bbox": bb, "z_comp": z,
                      "area": int(I.sum())})
    assert need["L"] == 0 and need["C"] == 0, need
    used |= set(per_cell)
    # ---- crack SHIFT / DEL on clean components; CSIR cells first, then the rest (random order)
    order_c = [s for s in order if s.startswith("CSIR")] + [s for s in order if not s.startswith("CSIR")]
    queue = [("SHIFT", "L"), ("SHIFT", "C"), ("DEL", "L"), ("DEL", "C")] * N_PER   # interleaved slots
    passes = [(25, s) for s in order_c] + [(23, s) for s in order_c]     # all 25 models first; >= 23 only to fill gaps
    for min_cov, s in passes:
        if not queue:
            break
        if s in exclude or s in used or s in in_rated_group:
            continue
        d = R.load_cell(s, pool)
        if not d["lab_crack"].any():
            continue
        comps = crack_clean_comps(d, min_cov)
        if not comps:
            continue
        got, sl = None, None
        tried = []
        for cand_sl in queue:                      # head slot first, then the other open slot types
            if cand_sl in tried:
                continue
            tried.append(cand_sl)
            for K, z in [comps[i] for i in rng.permutation(len(comps))]:
                got = try_shift(d, K, rng) if cand_sl[0] == "SHIFT" else try_delete_seg(d, K, rng)
                if got:
                    got["z_comp"] = z
                    got["min_cov"] = min_cov
                    break
            if got:
                sl = cand_sl
                break
        if not got:
            continue
        queue.remove(sl)
        used.add(s)
        items.append({"stem": s, "cls": "crack", "plant": sl[0], "side": sl[1], **got})
    need = {"left": len(queue)}
    assert need["left"] == 0, queue
    # ---- FAKE crack / FAKE inactive on clean bright material, source quotas
    for cls, quota in FAKE_SRC_QUOTA.items():
        sides = ["L", "C"] * N_PER
        si = 0
        for src, q in quota.items():
            got_n = 0
            for s in order:
                if got_n == q:
                    break
                if not s.startswith(src) or s in exclude or s in used or s in in_rated_group:
                    continue
                d = R.load_cell(s, pool)
                got = try_fake_crack(d, rng) if cls == "crack" else try_fake_blob(d, rng)
                if not got:
                    continue
                used.add(s)
                items.append({"stem": s, "cls": cls, "plant": "FAKE", "side": sides[si], **got})
                si += 1
                got_n += 1
            assert got_n == q, (cls, src, got_n)
    return items, used


EXAMPLE_REAL = {  # real, unsupported audit candidates outside the rated modules and the calibration cells (chosen by eye)
    "EX3": ("CFVS_00125_r8_c5", "MC", "192,36,221,48"),   # model crack line along the edge of an area both mark inactive
    "EX4": ("CSIR_00086_r10_c5", "SC", "78,353,90,379"),  # faint line on grainy multi-crystalline texture
}


def build_examples(stems, pool, used, excl_groups, outdir):
    """Five non-scored example panels for RATER_BRIEF.md (never scored, never in the rated or calibration cells or modules).
    EX1 crack segment missing in A (A = label with a clean segment deleted; answer B). EX2 inactive blob on bright clean
    material in B (answer A). EX3 real convention case (answer CONVENTION). EX4 real faint line (answer AMBIGUOUS).
    EX5 clearly dark crack-bounded region not marked inactive in B (B = label with the region deleted; answer A)."""
    rng = np.random.default_rng(SEL_SEED + 1)
    g3 = C.groups(C.G3)
    free = [s for s in stems if s not in used and g3[s]["group"] not in excl_groups]
    order = [free[i] for i in rng.permutation(len(free))]
    cand_rows = {(r["stem"], r["type"], r["bbox_y0x0y1x1"]): r for r in csv.DictReader(open(C.OUT / "a_candidates.tsv"),
                                                                                      delimiter="\t")}
    os.makedirs(outdir, exist_ok=True)
    info = {}
    taken = set()
    # EX1
    for s in order:
        d = R.load_cell(s, pool)
        if not d["lab_crack"].any():
            continue
        got = None
        for K, z in crack_clean_comps(d, 20):          # examples only: >= 20 of 25 models (strict ones went to calibration)
            got = try_delete_seg(d, K, rng)
            if got:
                break
        if got:
            lab = (d["lab_crack"] & ~got["D"], d["lab_inact"])
            con = (d["con_crack"], d["con_inact"])
            R.render_panel("EX1", d["grey"], lab, con, got["bbox"], os.path.join(outdir, "EX1.png"), valid=d["valid"])
            info["EX1"] = s
            taken.add(s)
            break
    # EX2
    for s in order:
        if s in taken or not s.startswith("CSIR"):
            continue
        d = R.load_cell(s, pool)
        got = try_fake_blob(d, rng)
        if got:
            lab = (d["lab_crack"], d["lab_inact"])
            con = (d["con_crack"], d["con_inact"] | got["B"])
            R.render_panel("EX2", d["grey"], lab, con, got["bbox"], os.path.join(outdir, "EX2.png"), valid=d["valid"])
            info["EX2"] = s
            taken.add(s)
            break
    # EX3, EX4: real candidates, A = label
    for ex, (s, t, bb) in EXAMPLE_REAL.items():
        r = cand_rows[(s, t, bb)]
        assert r["supported"] == "0" and s not in used and g3[s]["group"] not in excl_groups, (ex, s)
        d = R.load_cell(s, pool)
        R.render_panel(ex, d["grey"], (d["lab_crack"], d["lab_inact"]), (d["con_crack"], d["con_inact"]),
                       [int(v) for v in bb.split(",")], os.path.join(outdir, f"{ex}.png"), valid=d["valid"])
        info[ex] = s
        taken.add(s)
    # EX5: a clearly dark inactive region bounded by cracks; B = label with the region deleted
    for s in order:
        if s in taken:
            continue
        d = R.load_cell(s, pool)
        if not d["lab_inact"].any():
            continue
        li, n = ndi.label(d["lab_inact"], C.S8)
        best = None
        for i in range(1, n + 1):
            I = li == i
            m = int(I.sum())
            bb = R.bbox_of(I)
            if m < 300 or m > 15000 or max(bb[2] - bb[0], bb[3] - bb[1]) + 1 > 200 or (d["vi"][I] >= 13).mean() < 0.7:
                continue
            z = zc(d, I, d["lab_inact"] | d["con_inact"])
            if np.isfinite(z) and z <= -2.0 and window_clean(d, bb):
                best = (I, bb)
                break
        if best:
            I, bb = best
            lab = (d["lab_crack"], d["lab_inact"] & ~I)
            con = (d["con_crack"], d["con_inact"])
            R.render_panel("EX5", d["grey"], con, lab, bb, os.path.join(outdir, "EX5.png"), valid=d["valid"])
            info["EX5"] = s
            break
    assert len(info) == 5, info
    return info


def overlays_for(item, d):
    """(label_overlay, consensus_overlay) as (crack, inactive) raw masks for one item, plant applied."""
    lab = [d["lab_crack"].copy(), d["lab_inact"].copy()]
    con = [d["con_crack"].copy(), d["con_inact"].copy()]
    if item["set"] == "cand":
        return tuple(lab), tuple(con)
    tgt = lab if item["side"] == "L" else con
    p, cls = item["plant"], item["cls"]
    if cls == "crack" and p == "SHIFT":
        if item["side"] == "L":
            tgt[0] = (tgt[0] & ~item["K"]) | item["KS"]
        else:
            tgt[0] = (tgt[0] & ~item["Kc"]) | item["KcS"]
    elif cls == "crack" and p == "DEL":
        tgt[0] = tgt[0] & ~item["D"]
    elif cls == "crack" and p == "FAKE":
        tgt[0] = tgt[0] | item["F"]
    elif cls == "inact" and p == "DEL":
        if item["side"] == "L":
            tgt[1] = tgt[1] & ~item["I"]
        else:
            tgt[1] = tgt[1] & ~ndi.binary_dilation(item["I"], structure=R.disc(6))
    elif cls == "inact" and p == "FAKE":
        tgt[1] = tgt[1] | item["B"]
    else:
        raise ValueError(item)
    return tuple(lab), tuple(con)


_POOL = None


def _render(job):
    item, pid, label_is, outdir = job
    d = R.load_cell(item["stem"], _POOL)
    lab, con = overlays_for(item, d)
    A, B = (lab, con) if label_is == "A" else (con, lab)
    win = R.render_panel(pid, d["grey"], A, B, item["bbox"], os.path.join(outdir, f"{pid}.png"), valid=d["valid"])
    return pid, win


def main():
    global _POOL
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--seed", default=None, help="hex secret seed (only to re-create a build; normally drawn from os.urandom)")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--panels", default=str(R.PANELS))
    ap.add_argument("--keyfile", default=str(R.KEYDIR / "key.tsv"))
    ap.add_argument("--orders", default=str(R.RATER / "orders"))
    a = ap.parse_args()
    assert a.workers <= 4
    if os.path.exists(a.keyfile) and not a.force:
        sys.exit(f"refused: {a.keyfile} exists (the build is frozen); use --force only before any rating exists")
    t0 = time.time()
    stems = C.pool_stems()
    pool = set(stems)
    _POOL = pool
    cands = supported_candidates()
    cand_cells = {r["stem"] for r in cands}
    assert len(cands) == 124 and len(cand_cells) == 49, (len(cands), len(cand_cells))
    for r in cands:
        C.guard(r["stem"], pool)
    g3 = C.groups(C.G3)
    rated_groups = {g3[s]["group"] for s in cand_cells}
    cal, used = select_calibration(stems, pool, cand_cells, rated_groups)
    assert not ({c["stem"] for c in cal} & cand_cells)
    ex_info = build_examples(stems, pool, used | cand_cells, rated_groups, str(R.EXAMPLES))
    items = []
    for r in cands:
        items.append({"set": "cand", "stem": r["stem"], "cls": "crack" if r["type"] in ("MC", "SC") else "inact",
                      "ctype": r["type"], "bbox": [int(v) for v in r["bbox_y0x0y1x1"].split(",")], "row": r})
    for c in cal:
        c["set"] = "cal"
        items.append(c)
    # ---- secret randomisation: IDs, A/B (balanced within strata), orders
    seed = int(a.seed, 16) if a.seed else int.from_bytes(os.urandom(8), "big")
    rs = random.Random(seed)
    ids = set()
    while len(ids) < len(items):
        ids.add("".join(rs.choice(ALPH) for _ in range(5)))
    ids = sorted(ids)
    rs.shuffle(ids)
    for it, pid in zip(items, ids):
        it["id"] = pid
    strata = {}
    for it in items:
        key = (it["set"], it["cls"], it.get("ctype", ""), it.get("plant", ""), it.get("side", ""))
        strata.setdefault(key, []).append(it)
    for key in sorted(strata):
        grp = strata[key]
        labs = ["A", "B"] * (len(grp) // 2) + ([rs.choice("AB")] if len(grp) % 2 else [])
        rs.shuffle(labs)
        for it, l in zip(grp, labs):
            it["label_is"] = l
    orders = []
    for _ in range(3):
        o = [it["id"] for it in items]
        rs.shuffle(o)
        orders.append(o)
    # ---- render (render in a random order so file times say nothing; then set one common mtime)
    os.makedirs(a.panels, exist_ok=True)
    jobs = [(it, it["id"], it["label_is"], a.panels) for it in items]
    rs.shuffle(jobs)
    wins = {}
    with mp.get_context("fork").Pool(a.workers) as P:
        for pid, win in P.imap_unordered(_render, jobs, chunksize=1):
            wins[pid] = win
    tfix = time.mktime((2026, 11, 21, 0, 0, 0, 0, 0, -1))
    for it in items:
        os.utime(os.path.join(a.panels, f"{it['id']}.png"), (tfix, tfix))
    # ---- orders
    os.makedirs(a.orders, exist_ok=True)
    for k, o in enumerate(orders, 1):
        with open(os.path.join(a.orders, f"ORDER_R{k}.txt"), "w") as f:
            f.write("\n".join(o) + "\n")
    # ---- key
    os.makedirs(os.path.dirname(a.keyfile), exist_ok=True)
    cols = ["id", "set", "cls", "type", "truth", "label_is", "stem", "source", "group", "bbox", "window_y0x0side", "px",
            "z", "kind", "replicated_w1g", "classes_under", "cand_row", "plant", "side", "plant_info"]
    with open(os.path.join(os.path.dirname(a.keyfile), "examples.tsv"), "w") as f:
        f.write("example\tstem\n" + "".join(f"{k}\t{v}\n" for k, v in sorted(ex_info.items())))
    with open(a.keyfile, "w") as f:
        f.write(f"# SEALED KEY of the AI-rater check (PREREG.md). secret_seed={seed:016x} sel_seed={SEL_SEED}\n")
        f.write("\t".join(cols) + "\n")
        for it in sorted(items, key=lambda x: x["id"]):
            s = it["stem"]
            if it["set"] == "cand":
                r = it["row"]
                typ, truth, px, z, kind, rep, cl, crow, plant, side, info = (
                    r["type"], "NA", r["px"], r["z"], r["kind"], r["replicated_w1g"], r["classes_under"], r["cand_row"],
                    "", "", "")
            else:
                analog = {("crack", "SHIFT", "L"): "SHIFT", ("crack", "SHIFT", "C"): "SHIFT",
                          ("crack", "DEL", "L"): "MC", ("crack", "DEL", "C"): "SC",
                          ("crack", "FAKE", "L"): "SC", ("crack", "FAKE", "C"): "MC",
                          ("inact", "DEL", "L"): "MI", ("inact", "DEL", "C"): "SI",
                          ("inact", "FAKE", "L"): "SI", ("inact", "FAKE", "C"): "MI"}[(it["cls"], it["plant"], it["side"])]
                typ = analog
                truth = "label_error" if it["side"] == "L" else "label_correct"
                info_d = {k: (v if not isinstance(v, (np.floating, float)) else round(float(v), 3)) for k, v in it.items()
                          if k in ("v", "z_shift", "z_comp", "z_seg", "seg_px", "seg_mode", "r", "len_px", "area", "min_cov")}
                info_d = {k: (list(v) if isinstance(v, tuple) else v) for k, v in info_d.items()}
                info = json.dumps(info_d, separators=(",", ":"))
                px, z, kind, rep, cl, crow, plant, side = "", "", "", "", "", "", it["plant"], it["side"]
            row = [it["id"], it["set"], it["cls"], typ, truth, it["label_is"], s, s.split("_")[0], g3[s]["group"],
                   ",".join(map(str, it["bbox"])), ",".join(map(str, wins[it["id"]])), str(px), str(z), kind, str(rep), cl,
                   str(crow), plant, side, info]
            f.write("\t".join(row) + "\n")
    # ---- build log (no stems, no IDs)
    n_cal = {}
    for it in items:
        if it["set"] == "cal":
            n_cal[(it["cls"], it["plant"], it["side"])] = n_cal.get((it["cls"], it["plant"], it["side"]), 0) + 1
    src_cal = {}
    for it in items:
        if it["set"] == "cal":
            src_cal[(it["cls"], it["stem"].split("_")[0])] = src_cal.get((it["cls"], it["stem"].split("_")[0]), 0) + 1
    sides = [wins[it["id"]][2] for it in items]
    with open(R.RATER / "build_log.txt", "w") as f:
        f.write(f"build {time.strftime('%Y-%m-%d %H:%M:%S')} | panels {len(items)} | candidates {len(cands)} in "
                f"{len(cand_cells)} cells | calibration {len(cal)} in {len({c['stem'] for c in cal})} cells | "
                f"{time.time() - t0:.0f} s\n")
        f.write("calibration (class, plant, side L=label planted / C=consensus planted): " +
                ", ".join(f"{k}: {v}" for k, v in sorted(n_cal.items())) + "\n")
        f.write("calibration sources: " + ", ".join(f"{k}: {v}" for k, v in sorted(src_cal.items())) + "\n")
        f.write(f"window side px: min {min(sides)}, median {int(np.median(sides))}, max {max(sides)}\n")
    print(open(R.RATER / "build_log.txt").read())


if __name__ == "__main__":
    main()
