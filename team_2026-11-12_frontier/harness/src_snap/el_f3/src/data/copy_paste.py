"""F2 / CP5 (opt-in ``cp.lambda`` > 0; spec_cp5.md v1.1): crack copy-paste onto unlabelled backgrounds.

Library (once, CPU, deterministic): 8-connected crack components (class 14, >= ``min_area`` px) of the fraction's
labelled cells, minus (1) components whose ring R8 = dilate(M, 8) minus dilate(M, 1) is more than 20% inactive (11),
(2) components whose R8 touches padding (7), frame edge (21) or border (5), (3) components with contrast
median(src on R8 minus crack) - median(src on M) < ``min_contrast`` grey levels. Per component: the residual
r = src - bg on T = dilate(M, 2), bg = G*(src (1 - T)) / G*(1 - T) with a Gaussian of sigma 3 (normalised
convolution), set to 0 on other crack px inside T (review P3), and the source ring robust sd (1.4826 x MAD on R8 minus
crack). Dilations are Euclidean (EDT <= k).

Composition (per stream image, a pure function of the item seed): background from list (a) or (b) with p 0.5 each,
K ~ U{1..kmax} components, each with a uniform dihedral transform (exact pixel permutations) and an integer location,
uniform over placements whose dilate(M, 6) lies inside the cell area (grey in [15, 245], 5x5 opening, largest
component, eroded 10 px), does not touch an earlier placement's dilate(M, 6), and whose target ring median is
>= ``ring_min`` GL; up to ``tries`` draws per component; a background with no placement is redrawn. Transfer:
new = clip(round(tgt + s r), 0, 255) on T, s = clip(sd_tgt / sd_src, 0.5, 2). Target map: 1 crack (M),
0 ignore (dilate(M, 1) minus M), 2 not-crack ring (dilate(M, 6) minus dilate(M, 1)), 0 everywhere else.
Then the label-safe augmentation is applied jointly to image and target map.
"""
from __future__ import annotations

from pathlib import Path

import albumentations as A
import numpy as np
import torch
from PIL import Image
from scipy import ndimage as ndi
from torch.utils.data import Dataset

CRACK, INACTIVE, EDGE_CLASSES = 14, 11, (7, 21, 5)
S8 = np.ones((3, 3), bool)


def dilate(m: np.ndarray, k: float) -> np.ndarray:
    """Euclidean dilation: pixels within distance k of m (m itself for k = 0)."""
    if not m.any():
        return m.copy()
    return ndi.distance_transform_edt(~m) <= k


def robust_sd(v: np.ndarray) -> float:
    v = v.astype(np.float64)
    return float(1.4826 * np.median(np.abs(v - np.median(v)))) if v.size else 0.0


def load_grey(p: Path) -> np.ndarray:
    return np.array(Image.open(p).convert("L"), dtype=np.uint8)


def build_library(img_dir: Path, msk_dir: Path, stems: list[str], min_area: int = 20, min_contrast: float = 3.0,
                  max_inactive_ring: float = 0.2) -> tuple[list[dict], list[dict]]:
    """Returns (kept components, every candidate's record). Each kept item carries crops on the bbox of dilate(M, 8)."""
    kept, records = [], []
    for stem in stems:
        src = load_grey(Path(img_dir) / f"{stem}.png").astype(np.float64)
        msk = np.array(Image.open(Path(msk_dir) / f"{stem}.png"))
        crack_all = msk == CRACK
        lab, n = ndi.label(crack_all, S8)
        for cid in range(1, n + 1):
            M = lab == cid
            area = int(M.sum())
            if area < min_area:
                continue
            D1, T, D8 = dilate(M, 1), dilate(M, 2), dilate(M, 8)
            R8 = D8 & ~D1
            ring_nc = R8 & ~crack_all
            inact = float((msk[R8] == INACTIVE).mean()) if R8.any() else 0.0
            edge = bool(np.isin(msk[R8], EDGE_CLASSES).any())
            contrast = float(np.median(src[ring_nc]) - np.median(src[M])) if ring_nc.any() else 0.0
            rec = dict(stem=stem, cid=cid, area=area, contrast=round(contrast, 3), inactive_ring=round(inact, 4),
                       edge=edge, kept=False, reason="")
            if inact > max_inactive_ring:
                rec["reason"] = "inactive_ring"
            elif edge:
                rec["reason"] = "edge_ring"
            elif contrast < min_contrast:
                rec["reason"] = "low_contrast"
            else:
                rec["kept"] = True
            records.append(rec)
            if not rec["kept"]:
                continue
            w = 1.0 - T.astype(np.float64)
            num, den = ndi.gaussian_filter(src * w, 3.0), ndi.gaussian_filter(w, 3.0)
            bg = num / np.maximum(den, 1e-6)
            r = np.where(T & ~(crack_all & ~M), src - bg, 0.0)  # P3: other crack px within T carry no residual
            ys, xs = np.nonzero(D8)
            y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
            kept.append(dict(stem=stem, cid=cid, area=area, contrast=contrast, sd_src=robust_sd(src[ring_nc]),
                             M=M[y0:y1, x0:x1].copy(), r=r[y0:y1, x0:x1].astype(np.float32)))
    return kept, records


def dihedral_np(a: np.ndarray, t: int) -> np.ndarray:
    """One of 8 exact transforms: rot90 by t % 4, then a horizontal flip if t >= 4."""
    a = np.rot90(a, t % 4)
    return np.ascontiguousarray(a[:, ::-1] if t >= 4 else a)


def prepare_variants(item: dict) -> list[dict]:
    """Per dihedral transform: M, T, D1, D6, R8 (ring) and r on the same crop, padded by 8 px so rings fit."""
    out = []
    for t in range(8):
        M = np.pad(dihedral_np(item["M"], t), 8)
        r = np.pad(dihedral_np(item["r"], t), 8)
        D1, D6, D8 = dilate(M, 1), dilate(M, 6), dilate(M, 8)
        out.append(dict(M=M, T=dilate(M, 2), D1=D1, D6=D6, R8=D8 & ~D1, r=r))
    return out


def cell_area(img: np.ndarray, lo: int = 15, hi: int = 245, erode: float = 10.0) -> np.ndarray:
    a = (img >= lo) & (img <= hi)
    a = ndi.binary_opening(a, structure=np.ones((5, 5), bool))
    lab, n = ndi.label(a, S8)
    if n == 0:
        return np.zeros_like(a)
    sizes = np.bincount(lab.ravel())[1:]
    a = lab == (1 + int(np.argmax(sizes)))
    return ndi.distance_transform_edt(a) > erode


def compose_one(bg: np.ndarray, library: list[dict], variants: list[list[dict]], rng: np.random.Generator,
                kmax: int = 3, tries: int = 50, ring_min: float = 30.0
                ) -> tuple[np.ndarray, np.ndarray, dict, list] | None:
    """Paste K components onto ``bg`` (uint8 H x W). Returns (image uint8, target uint8, stats, placements
    [(library index, transform, y, x)]), or None if nothing could be placed."""
    H, W = bg.shape
    area = cell_area(bg)
    out = bg.astype(np.float64).copy()
    tmap = np.zeros((H, W), np.uint8)
    occ = np.zeros((H, W), bool)
    K = int(rng.integers(1, kmax + 1))
    placed, fails, svals, rmeds, where = 0, 0, [], [], []
    for _ in range(K):
        j = int(rng.integers(len(library)))
        t = int(rng.integers(8))
        v = variants[j][t]
        h, w = v["M"].shape
        if h > H or w > W:
            fails += tries
            continue
        ok = False
        for _try in range(tries):
            y, x = int(rng.integers(0, H - h + 1)), int(rng.integers(0, W - w + 1))
            win = (slice(y, y + h), slice(x, x + w))
            if not area[win][v["D6"]].all() or occ[win][v["D6"]].any():
                fails += 1
                continue
            ring = bg[win][v["R8"]]
            rmed = float(np.median(ring))
            if rmed < ring_min:
                fails += 1
                continue
            s = float(np.clip(robust_sd(ring) / max(library[j]["sd_src"], 1e-6), 0.5, 2.0))
            o = out[win]
            o[v["T"]] = o[v["T"]] + s * v["r"][v["T"]]
            tm = tmap[win]
            tm[v["D6"] & ~v["D1"]] = 2
            tm[v["M"]] = 1
            occ[win] |= v["D6"]
            placed += 1; svals.append(s); rmeds.append(rmed); where.append((j, t, y, x)); ok = True
            break
        if not ok:
            continue
    if placed == 0:
        return None
    img = np.clip(np.rint(out), 0, 255).astype(np.uint8)
    stats = dict(placed=placed, fails=fails, crack_px=int((tmap == 1).sum()), ring_px=int((tmap == 2).sum()),
                 s=float(np.mean(svals)), ring_med=float(np.mean(rmeds)))
    return img, tmap, stats, where


class CPDataset(Dataset):
    """Stream of composed images. The item seed comes from the per-item reseeding of ``BatchStream`` (read from the
    ``_holder`` compose); the sampler index only sets the stream length."""

    def __init__(self, bg_a: list[Path], bg_b: list[Path], library: list[dict], aug: A.Compose, p_a: float = 0.5,
                 kmax: int = 3, tries: int = 50, ring_min: float = 30.0, max_redraw: int = 20) -> None:
        if not library:
            raise ValueError("empty copy-paste library")
        self.bg_a, self.bg_b, self.library = list(bg_a), list(bg_b), library
        self.variants = [prepare_variants(it) for it in library]
        self.aug = aug
        self._holder = A.Compose([])
        self.p_a, self.kmax, self.tries, self.ring_min, self.max_redraw = p_a, kmax, tries, ring_min, max_redraw

    def __len__(self) -> int:
        return len(self.bg_a) + len(self.bg_b)

    def compose(self, seed: int) -> tuple[np.ndarray, np.ndarray, dict, str]:
        rng = np.random.default_rng(seed)
        for k in range(self.max_redraw):
            lst = self.bg_a if (rng.random() < self.p_a or not self.bg_b) else self.bg_b
            p = lst[int(rng.integers(len(lst)))]
            res = compose_one(load_grey(p), self.library, self.variants, rng, self.kmax, self.tries, self.ring_min)
            if res is not None:
                img, tmap, st, _ = res
                st["redraws"] = k
                return img, tmap, st, str(p)
        raise RuntimeError(f"no placement after {self.max_redraw} backgrounds (seed {seed})")

    def __getitem__(self, idx: int) -> dict:
        seed = getattr(self._holder, "seed", None)
        seed = int(seed) if seed is not None else int(idx)
        img, tmap, st, _ = self.compose(seed)
        o = self.aug(image=img[..., None], mask=tmap)
        return {"image": o["image"], "cp_target": torch.as_tensor(np.asarray(o["mask"]), dtype=torch.long),
                **{f"cp_{k}": torch.tensor(float(v)) for k, v in st.items()}}


def read_list(p: Path) -> list[str]:
    return [ln.strip() for ln in Path(p).read_text().splitlines() if ln.strip()]


def build_cp_stream(cfg: dict, info: dict, seed: int, num_workers: int, pin_memory: bool):
    """``cp`` config section -> (BatchStream on stream id 3, library records, summary). Lists:
    (a) the pool part of ``cp.bg_pool_list`` (lines under unlabeled/), minus ``cp.heldout_list``;
    (b) ``data/splits/seed<k>/unlabeled_<P>pct.txt`` minus ``cp.bg_train_exclude`` (D7 twins)."""
    from src.data.augmentations import get_labelsafe_augmentation
    from src.data.stream import BatchStream
    c, d = cfg["cp"], cfg["data"]
    root = Path(d["root"])
    img_dir, msk_dir = root / "labeled" / "images", root / d.get("mask_subdir", "labeled/masks_coded")
    lab = read_list(Path(info["labeled_split"]))
    # F3 (100% labels): optional ``cp.library_exclude`` (a stem list kept out of the paste library only; those cells stay
    # in the labelled stream). Absent = no change.
    lib_excl = set(read_list(Path(c["library_exclude"]))) if c.get("library_exclude") else set()
    lib_stems = [s for s in lab if s not in lib_excl]
    library, records = build_library(img_dir, msk_dir, lib_stems, int(c.get("min_area", 20)),
                                     float(c.get("min_contrast", 3.0)))
    held = set(read_list(Path(c["heldout_list"]))) if c.get("heldout_list") else set()
    pool = [r for r in read_list(Path(c["bg_pool_list"])) if r.startswith("unlabeled/")]
    bg_a = [root / r for r in pool if r not in held]
    if not all(h.startswith("unlabeled/") for h in held) or held & {r for r in pool if (root / r) in set(bg_a)}:
        raise ValueError("cp.heldout_list must hold pool cells (unlabeled/...) that are not backgrounds")
    if float(d["labeled_fraction"]) >= 1:  # F3: at 100% every train cell is labelled: no (b) list, pool backgrounds only
        unl = []
    else:
        frac_tag = f"{round(float(d['labeled_fraction']) * 100)}pct"
        unl = read_list(root / "splits" / f"seed{int(info['split_seed'])}" / f"unlabeled_{frac_tag}.txt")
    excl = set(read_list(Path(c["bg_train_exclude"]))) if c.get("bg_train_exclude") else set()
    if set(lab) & set(unl):
        raise ValueError("labelled cells in the unlabelled list")
    bg_b = [img_dir / f"{s}.png" for s in unl if s not in excl]
    size, mean, std = d["input_size"], d.get("mean", [0.5]), d.get("std", [0.25])
    ds = CPDataset(bg_a, bg_b, library, get_labelsafe_augmentation(size, mean, std), float(c.get("p_pool", 0.5)),
                   int(c.get("kmax", 3)), int(c.get("tries", 50)), float(c.get("ring_min", 30.0)))
    stream = BatchStream(ds, int(c.get("batch", 4)), seed=seed, stream_id=3, num_workers=num_workers,
                         pin_memory=pin_memory)
    summary = dict(n_library=len(library), library_px=int(sum(x["area"] for x in library)), n_bg_pool=len(bg_a),
                   n_bg_train=len(bg_b), n_heldout=len(held), n_candidates=len(records), n_library_cells=len(lib_stems),
                   n_library_excluded=len(set(lab) & lib_excl))
    return stream, records, summary


def cp_loss(logits: torch.Tensor, tgt: torch.Tensor, n_lab: torch.Tensor, crack: int = CRACK) -> tuple[torch.Tensor,
                                                                                                         torch.Tensor]:
    """(loss, p_crack): crack px -log p_c, ring px -log(1 - p_c) (log-sum-exp of the other classes), summed and
    divided by ``n_lab``. fp32."""
    lsm = torch.log_softmax(logits.float(), 1)
    lp = lsm[:, crack]
    lnot = torch.logsumexp(torch.cat([lsm[:, :crack], lsm[:, crack + 1:]], 1), 1)
    loss = (-(lp[tgt == 1]).sum() - (lnot[tgt == 2]).sum()) / n_lab
    return loss, lp.detach().exp()
