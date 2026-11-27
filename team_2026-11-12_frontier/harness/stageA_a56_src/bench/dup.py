"""elbench stage A6 (shared piece S3): duplicate search by md5, normalised cross-correlation (NCC) and a DINOv2 embedding.

Images only. Sealed sets (legacy test 50, E1 106) may be read as pixels (lead's ruling L2); nothing here reads a label or
a prediction. Descriptors:
  md5        md5 of the file bytes and of the decoded 8-bit grey pixels (PIL convert("L")).
  NCC        T8 C0 / data_analysis/scripts/ucf_twins.py `refined`: 128 px BOX resize, DoG(sigma 1) - DoG(sigma 6),
             row and column means removed, L2-normalised; NCC = dot product.
  embedding  DINOv2 ViT-S/14 CLS token (timm vit_small_patch14_dinov2, strict load), grey -> 3 channels, 224 px bilinear,
             ImageNet mean / std, L2-normalised; cosine = dot product.
Query images are scored in the 8 dihedral views (a cell re-imaged upside down or mirrored is still found); the database
side in one view. The NCC descriptor of a dihedral view equals the dihedral view of the descriptor (BOX blocks align,
the Gaussian is isotropic with symmetric borders, row / column mean removal maps onto itself): tested.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

S_NCC = 128
CROP = (128, 384)                 # central cell crop of a 512 px BenchmarkEL image (cell bbox median about 252 px)
EMB_PX = 224
MEAN = np.array([0.485, 0.456, 0.406], np.float32)
STD = np.array([0.229, 0.224, 0.225], np.float32)
WEIGHTS = Path("/home/noob/work/bench_a_io/weights/dinov2_vits14_pretrain.pth")
WEIGHTS_MD5 = "2e405cee1bad14912278296d4f42e993"


# ---------------------------------------------------------------- images, md5
def load_gray(path) -> np.ndarray:
    with Image.open(path) as im:
        return np.asarray(im.convert("L"), np.uint8).copy()


def md5_pair(path) -> tuple[str, str, np.ndarray]:
    """(md5 of the file bytes, md5 of the decoded grey pixels incl. shape, grey array)."""
    b = Path(path).read_bytes()
    a = load_gray(path)
    hp = hashlib.md5(np.asarray(a.shape, np.int64).tobytes() + a.tobytes()).hexdigest()
    return hashlib.md5(b).hexdigest(), hp, a


def crop_cell(a: np.ndarray) -> np.ndarray:
    assert a.shape == (512, 512), a.shape
    return a[CROP[0]:CROP[1], CROP[0]:CROP[1]]


def content_sd(a: np.ndarray) -> float:
    v = a[(a > 0) & (a < 255)]
    return float(v.std()) if v.size else float("nan")


# ---------------------------------------------------------------- dihedral views
def dihedral(x: np.ndarray, k: int) -> np.ndarray:
    """View k in 0..7 of the last two axes: rot90 by k % 4, after a left-right flip for k >= 4."""
    if k >= 4:
        x = x[..., ::-1]
    return np.rot90(x, k % 4, axes=(-2, -1))


# ---------------------------------------------------------------- NCC descriptor
def ncc_desc(a: np.ndarray, size: int = S_NCC) -> np.ndarray:
    """(size, size) float32 descriptor, unit L2 norm (ucf_twins.py `refined`)."""
    # float mode: PIL rounds the intermediate pass of an 8-bit resize, which breaks the dihedral equivalence (tested)
    x = np.asarray(Image.fromarray(np.asarray(a, np.float32), mode="F").resize((size, size), Image.BOX), np.float32)
    b = ndi.gaussian_filter(x, 1) - ndi.gaussian_filter(x, 6)
    b = b - b.mean(0, keepdims=True) - b.mean(1, keepdims=True) + b.mean()
    b -= b.mean()
    return (b / (np.linalg.norm(b) + 1e-6)).astype(np.float32)


def views(desc2d: np.ndarray) -> np.ndarray:
    """(8, d) flattened dihedral views of a 2-D descriptor."""
    return np.stack([np.ascontiguousarray(dihedral(desc2d, k)).ravel() for k in range(8)])


# ---------------------------------------------------------------- embedding
def emb_input(a: np.ndarray) -> np.ndarray:
    """(3, 224, 224) float32 network input from a grey uint8 image."""
    x = np.asarray(Image.fromarray(np.asarray(a, np.float32), mode="F").resize((EMB_PX, EMB_PX), Image.BILINEAR),
                   np.float32) / 255.0
    x = np.repeat(x[None], 3, 0)
    return (x - MEAN[:, None, None]) / STD[:, None, None]


class Embedder:
    def __init__(self, weights: Path = WEIGHTS, check_md5: bool = True):
        import timm
        import torch
        from timm.models.vision_transformer import checkpoint_filter_fn
        torch.set_num_threads(1)
        if check_md5:
            h = hashlib.md5(Path(weights).read_bytes()).hexdigest()
            assert h == WEIGHTS_MD5, f"weights md5 {h}"
        sd = torch.load(weights, map_location="cpu", weights_only=True)
        m = timm.create_model("vit_small_patch14_dinov2", pretrained=False, img_size=EMB_PX)
        m.load_state_dict(checkpoint_filter_fn(sd, m), strict=True)
        self.m = m.eval()
        self.torch = torch

    def __call__(self, x: np.ndarray) -> np.ndarray:
        """x (n, 3, 224, 224) -> (n, 384) unit-norm CLS embeddings."""
        with self.torch.inference_mode():
            f = self.m.forward_features(self.torch.from_numpy(np.ascontiguousarray(x)))[:, 0]
        f = f.numpy().astype(np.float32)
        return f / (np.linalg.norm(f, axis=1, keepdims=True) + 1e-12)


# ---------------------------------------------------------------- search and calibration
def max_over_views(Q: np.ndarray, D: np.ndarray, block: int = 4096) -> tuple[np.ndarray, np.ndarray]:
    """Q (nq, 8, d) query views, D (nd, d) -> (score (nq, nd) = max over views of Q_v . D, argmax view (nq, nd))."""
    nq, nv, _ = Q.shape
    S = np.full((nq, D.shape[0]), -np.inf, np.float32)
    V = np.zeros((nq, D.shape[0]), np.uint8)
    for j0 in range(0, D.shape[0], block):
        Dj = D[j0:j0 + block].astype(np.float32, copy=False)
        for v in range(nv):
            s = Q[:, v].astype(np.float32, copy=False) @ Dj.T
            better = s > S[:, j0:j0 + block]
            S[:, j0:j0 + block] = np.where(better, s, S[:, j0:j0 + block])
            V[:, j0:j0 + block] = np.where(better, v, V[:, j0:j0 + block])
    return S, V


def auroc(pos, neg) -> float:
    """P(score_pos > score_neg) + 0.5 P(tie) (Mann-Whitney)."""
    pos, neg = np.asarray(pos, np.float64), np.asarray(neg, np.float64)
    if not len(pos) or not len(neg):
        return float("nan")
    from scipy.stats import rankdata
    r = rankdata(np.concatenate([pos, neg]))
    return float((r[:len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def tau_from_known(pos) -> float:
    """5th percentile (numpy linear) of the known same-cell scores (T12)."""
    return float(np.percentile(np.asarray(pos, np.float64), 5))


def image_id(stem: str) -> str:
    """Module / image id of a pool or labelled stem: drop '_rf', then '_r<row>_c<col>' (BMRK '_cell<n>')."""
    s = stem[:-3] if stem.endswith("_rf") else stem
    parts = s.split("_")
    if len(parts) >= 4 and parts[-2].startswith("r") and parts[-1].startswith("c"):
        return "_".join(parts[:-2])
    if parts[-1].startswith("cell"):
        return "_".join(parts[:-1])
    return s
