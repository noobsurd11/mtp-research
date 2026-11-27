"""Stage A6 duplicate tool (S3): descriptors, dihedral equivalence, search, calibration helpers, inventory guards."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from bench import derived  # noqa: E402
from bench import dup as D  # noqa: E402


def img(seed=0, n=512):
    rng = np.random.default_rng(seed)
    a = rng.integers(0, 256, (n, n)).astype(np.uint8)
    a[::37, :] = 20                                            # some structure
    return a


@pytest.mark.parametrize("k", range(8))
def test_ncc_descriptor_commutes_with_dihedral(k):
    a = img(1)
    d = D.ncc_desc(a)
    dv = D.ncc_desc(np.ascontiguousarray(D.dihedral(a, k)))
    assert np.allclose(dv, D.dihedral(d, k), atol=1e-5)


def test_ncc_identity_and_rotated_copy_found():
    a, b = img(2), img(3)
    da, db = D.ncc_desc(a), D.ncc_desc(b)
    assert float((da * da).sum()) == pytest.approx(1.0, abs=1e-4)
    Q = D.views(da)[None]
    rot = D.ncc_desc(np.ascontiguousarray(np.rot90(a, 2)))
    S, V = D.max_over_views(Q, np.stack([rot.ravel(), db.ravel()]))
    assert S[0, 0] == pytest.approx(1.0, abs=1e-4) and S[0, 1] < 0.5
    assert int(V[0, 0]) == 2


def test_max_over_views_matches_brute_force():
    rng = np.random.default_rng(4)
    Q = rng.normal(size=(5, 8, 16)).astype(np.float32)
    Db = rng.normal(size=(7, 16)).astype(np.float32)
    S, V = D.max_over_views(Q, Db, block=3)
    B = np.einsum("qvd,nd->qvn", Q, Db)
    assert np.allclose(S, B.max(1), atol=1e-5) and np.array_equal(V, B.argmax(1))


def test_md5_pixels_equal_across_file_formats(tmp_path):
    a = img(5, 64)
    Image.fromarray(a).save(tmp_path / "a.png")
    Image.fromarray(np.repeat(a[..., None], 3, 2)).save(tmp_path / "b.png")
    ha = D.md5_pair(tmp_path / "a.png")
    hb = D.md5_pair(tmp_path / "b.png")
    assert ha[0] != hb[0] and ha[1] == hb[1]


def test_auroc_and_tau():
    assert D.auroc([2, 3], [0, 1]) == pytest.approx(1.0)
    assert D.auroc([0, 1], [2, 3]) == pytest.approx(0.0)
    assert D.auroc([1, 1], [1, 1]) == pytest.approx(0.5)
    assert D.tau_from_known(np.arange(101)) == pytest.approx(5.0)


def test_image_id():
    assert D.image_id("CSIR_00297_r10_c5_rf") == "CSIR_00297"
    assert D.image_id("ARTS_00004_r1_c6") == "ARTS_00004"
    assert D.image_id("BMRK_01502_cell2156") == "BMRK_01502"


def test_crop_and_content_sd():
    a = img(6)
    assert D.crop_cell(a).shape == (256, 256)
    with pytest.raises(AssertionError):
        D.crop_cell(a[:300])
    b = np.zeros((10, 10), np.uint8); b[:5] = 255
    assert np.isnan(D.content_sd(b))


def test_embedder_strict_load_and_dihedral_views():
    E = D.Embedder()
    x = D.emb_input(img(7))
    assert x.shape == (3, 224, 224)
    xs = np.stack([np.ascontiguousarray(D.dihedral(x, k)) for k in range(8)])
    f = E(xs)
    assert f.shape == (8, 384) and np.allclose(np.linalg.norm(f, axis=1), 1, atol=1e-4)
    assert float(f[0] @ E(x[None])[0]) == pytest.approx(1.0, abs=1e-4)      # deterministic


def test_inventory_reads_no_label_column_and_marks_sealed():
    sys.path.insert(0, str(ROOT / "scripts"))
    import bench_dupsearch as B
    items, missing = B.labelled_items()
    assert len(items) + len(missing) == 816
    keys = set(items[0])
    assert not any(k.startswith(("has_", "crack", "inactive", "scuff")) for k in keys), keys
    fb = derived.forbidden()
    for i in items:
        assert i["sealed"] == (i["stem"] in fb)
        if i["set"] in ("test50", "e1_106"):
            assert i["sealed"]
    assert all(i["path"] and Path(i["path"]).exists() for i in items)


def test_sheet_refuses_overwrite(tmp_path):
    sys.path.insert(0, str(ROOT / "scripts"))
    import bench_dupsearch as B
    a = img(8)
    Image.fromarray(a).save(tmp_path / "x.png")
    out = tmp_path / "s.png"
    B.sheet([(str(tmp_path / "x.png"), 3, str(tmp_path / "x.png"), "x|x ncc 1.000")], out, "t")
    assert out.exists()
    with pytest.raises(FileExistsError):
        B.sheet([], out, "t")
