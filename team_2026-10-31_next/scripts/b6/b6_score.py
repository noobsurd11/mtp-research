"""B6 held-out scorer (protocol_B6 v1.0.1 s3 'Held-out scorer', s8.2): per-cell m0 records of one B6 run on its own
held-out fold only. Inference only; never reads a real test or E1 file.

Per run (final weights, checkpoints/latest.pth; never best.pth), on the cells of --stems only:
  24x24 confusion matrix per cell (rows GT, cols prediction), argmax, bf16 autocast on CUDA (fp32 on CPU), TTA off;
  crack relaxed counts at 2 px; crack and inactive connected components (8-conn) with hit counts; crack p-bands.
comps / BANDS / cell_stats / dihedral / predict are line-identical to m0_audit_tau.py (el_f1, md5 d77241bb; diff in
build_b6.md). GT = <data.root>/<data.mask_subdir>/<stem>.png of the run's own config_used.yaml.

Asserts, per run, before the model is built:
  - method supervised; data.root absolute; data.mask_subdir = labeled/masks_escdd; training.total_steps = 20000;
  - --stems file == <data.root>/splits/test.txt (same stems, same order) == <data.root>/splits/val.txt;
  - no stem of --stems or of <data.root>/splits/train.txt is in --forbidden (real test 50 + ext117 117; md5 pinned);
  - held-out and train lists disjoint;
  - mode b6: the held-out set equals exactly one fold of b6_folds.tsv (md5 pinned) and train.txt = the other 4 folds;
    mode check (scorer check on opening-1 val cells): the held-out set = the 54 val stems (sha256 pinned);
  - latest.pth carries step 20000.
After inference: output cell set == --stems. Output <out>/<run>.<mode>.json (an existing file is skipped, as m0).

Usage: python b6_score.py --code <e544133 deploy> --out <dir> --forbidden b6_forbidden.txt --folds b6_folds.tsv \
           --runs <run dir> ... --stems <held-out list> ...   (one --stems file per run, same order)
"""
from __future__ import annotations

import argparse, hashlib, json, os, sys, time
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--code", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--runs", nargs="+", required=True)
ap.add_argument("--stems", nargs="+", required=True, help="held-out stem file per run (same order as --runs)")
ap.add_argument("--forbidden", required=True, help="b6_forbidden.txt: real test + ext117 stems (md5 pinned)")
ap.add_argument("--folds", default=None, help="b6_folds.tsv (md5 pinned); required in mode b6")
ap.add_argument("--mode", choices=["b6", "check"], default="b6")
ap.add_argument("--device", default="cuda")
a = ap.parse_args()
CODE = Path(a.code).resolve()
sys.path.insert(0, str(CODE))
os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")

import numpy as np  # noqa: E402
import torch  # noqa: E402
from PIL import Image  # noqa: E402
from scipy import ndimage as ndi  # noqa: E402
from torch.utils.data import DataLoader  # noqa: E402

from src.data.augmentations import get_weak_augmentation  # noqa: E402
from src.data.benchmark_el import BenchmarkELDataset  # noqa: E402
from src.data.splits import load_split  # noqa: E402
from src.models.model_factory import build_model  # noqa: E402
from src.utils.config import load_config  # noqa: E402

NC, CRACK, INACT = 24, 14, 11
DEV = torch.device(a.device)
S8 = np.ones((3, 3), bool)
FORBIDDEN_MD5 = "9bb4d919fc16b5b394ce6d71f53903a6"   # /home/noob/work/b6/b6_forbidden.txt (167 stems)
FOLDS_MD5 = "e2cafce1509bb0f2b95ce6d5db397caf"       # results/b6/b6_folds.tsv
VAL54_SHA = "4ae8cbeb6fdccfa3e60c10c8f3a78236d5ce5c85ea50db527379bf059fe861c2"  # sorted el_f3 val.txt stems
MASK_SUBDIR = "labeled/masks_escdd"


def comps(gt_m: np.ndarray, pr_m: np.ndarray, near_pr: np.ndarray | None, near_gt: np.ndarray | None):
    """GT components: [size, hit] where hit = px of the component covered (by pred, or within 2 px of pred if near_pr).
    Pred components: [size, hit] with hit = px overlapping GT (or within 2 px of GT if near_gt)."""
    out = {}
    lg, ng = ndi.label(gt_m, S8)
    cov = near_pr if near_pr is not None else pr_m
    if ng:
        sz = np.bincount(lg.ravel(), minlength=ng + 1)[1:]
        ht = np.bincount(lg[cov].ravel(), minlength=ng + 1)[1:]
        out["gt"] = np.stack([sz, ht], 1).tolist()
    else:
        out["gt"] = []
    lp, npc = ndi.label(pr_m, S8)
    cov = near_gt if near_gt is not None else gt_m
    if npc:
        sz = np.bincount(lp.ravel(), minlength=npc + 1)[1:]
        ht = np.bincount(lp[cov].ravel(), minlength=npc + 1)[1:]
        out["pr"] = np.stack([sz, ht], 1).tolist()
    else:
        out["pr"] = []
    return out


BANDS = [0, 0.001, 0.1, 0.5, 0.95, 1.0001]


def cell_stats(pred: np.ndarray, gt: np.ndarray, keep: np.ndarray | None, pc: np.ndarray | None = None) -> dict:
    k = np.ones_like(gt, bool) if keep is None else keep
    assert gt[k].max() < NC and pred.max() < NC, "label id out of range"
    conf = np.bincount(gt[k].astype(np.int64) * NC + pred[k], minlength=NC * NC)
    g, p = (gt == CRACK) & k, (pred == CRACK) & k
    dg = ndi.distance_transform_edt(~g) if g.any() else np.full(g.shape, np.inf)
    dp = ndi.distance_transform_edt(~p) if p.any() else np.full(g.shape, np.inf)
    rel = [int((dg[p] <= 2).sum()), int(p.sum()), int((dp[g] <= 2).sum()), int(g.sum())]
    o = {"conf": conf.tolist(), "crack_rel2": rel,
         "crack_cc": comps(g, p, (dp <= 2) & k, (dg <= 2) & k)}
    gi, pi = (gt == INACT) & k, (pred == INACT) & k
    o["inact_cc"] = comps(gi, pi, None, None)
    if pc is not None:  # p(crack) bands on GT crack px and on GT non-crack px
        o["crack_pband_gt"] = np.histogram(pc[g], BANDS)[0].tolist()
        o["crack_pband_neg"] = np.histogram(pc[k & ~g], BANDS)[0].tolist()
        b = np.clip((pc * 1000).astype(int), 0, 999)  # 1,000-bin histograms as the P-series binned AP (per source AP)
        o["crack_h1000_pos"] = np.bincount(b[g], minlength=1000).tolist()
        o["crack_h1000_neg"] = np.bincount(b[k & ~g], minlength=1000).tolist()
    return o


def dihedral(x: torch.Tensor, i: int, inv: bool = False) -> torch.Tensor:
    r, f = i % 4, i // 4
    if not inv:
        x = torch.rot90(x, r, (2, 3))
        return torch.flip(x, (3,)) if f else x
    if f:
        x = torch.flip(x, (3,))
    return torch.rot90(x, -r, (2, 3))


@torch.no_grad()
def predict(m, img_dir: Path, stems: list[str], cfg: dict, tta: bool):
    d = cfg["data"]
    ds = BenchmarkELDataset(img_dir, None, stems, get_weak_augmentation(d.get("mean", [0.5]), d.get("std", [0.25]), d["input_size"]))
    plain, tlp, got = [], [], []
    for b in DataLoader(ds, batch_size=8, shuffle=False, num_workers=4):
        x = b["image"].to(DEV)
        with torch.autocast("cuda", dtype=torch.bfloat16):
            lg = m(x).float()
        plain.append(lg.cpu())
        got += list(b["stem"])
        if tta:
            pr = torch.zeros_like(lg)
            for i in range(8):
                with torch.autocast("cuda", dtype=torch.bfloat16):
                    li = m(dihedral(x, i)).float()
                pr += torch.softmax(dihedral(li, i, inv=True), 1)
            tlp.append(torch.log(pr / 8 + 1e-12).cpu())
    assert got == stems, "stem order"
    plain = torch.cat(plain)
    return plain, (torch.cat(tlp) if tta else None)


def md5(p: Path) -> str:
    h = hashlib.md5()
    with open(p, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def check_lists(run: Path, cfg: dict, stems_file: Path, fb: set, folds: dict | None) -> tuple[list[str], Path, object]:
    """Every list assert of the module docstring; returns (held-out stems, data root, fold id or 'val54')."""
    assert cfg.get("method", "supervised") == "supervised", (run, cfg.get("method"))
    d = cfg["data"]
    root = Path(d["root"])
    assert root.is_absolute(), (run, "data.root must be absolute", root)
    assert d.get("mask_subdir") == MASK_SUBDIR, (run, d.get("mask_subdir"))
    assert int(cfg["training"]["total_steps"]) == 20000, (run, cfg["training"]["total_steps"])
    stems = load_split(stems_file)
    rt, rv, rtr = (load_split(root / "splits" / f"{n}.txt") for n in ("test", "val", "train"))
    assert stems == rt, (run, "--stems != the run's <data.root>/splits/test.txt")
    assert rv == rt, (run, "val.txt != test.txt in the run's root")
    assert len(set(stems)) == len(stems), (run, "duplicate stems")
    assert not (set(stems) | set(rtr)) & fb, (run, "real test / E1 stem in the run's lists")
    assert not set(stems) & set(rtr), (run, "held-out stems in train.txt")
    if folds is not None:
        ks = [k for k, s in folds.items() if s == set(stems)]
        assert len(ks) == 1, (run, "held-out set is not one B6 fold")
        k = ks[0]
        assert set(rtr) == set().union(*(s for j, s in folds.items() if j != k)), (run, "train.txt != other 4 folds")
        return stems, root, k
    sha = hashlib.sha256(("\n".join(sorted(stems)) + "\n").encode()).hexdigest()
    assert sha == VAL54_SHA, (run, "check mode needs the 54 val stems")
    return stems, root, "val54"


def main() -> None:
    torch.backends.cudnn.deterministic, torch.backends.cudnn.benchmark = True, False
    assert len(a.runs) == len(a.stems), "one --stems file per run"
    assert md5(Path(a.forbidden)) == FORBIDDEN_MD5, "forbidden list md5"
    fb = set(load_split(Path(a.forbidden)))
    assert len(fb) == 167, len(fb)
    folds = None
    if a.mode == "b6":
        assert a.folds and md5(Path(a.folds)) == FOLDS_MD5, "mode b6 needs b6_folds.tsv (md5 e2cafce1)"
        rows = [l.rstrip("\n").split("\t") for l in open(a.folds) if l.strip()]
        ix_s, ix_f = rows[0].index("stem"), rows[0].index("fold")
        folds = {}
        for r in rows[1:]:
            folds.setdefault(int(r[ix_f]), set()).add(r[ix_s])
        assert sorted(folds) == [0, 1, 2, 3, 4] and sum(map(len, folds.values())) == 532
    else:
        assert a.folds is None, "check mode takes no --folds"
    me = md5(Path(__file__))
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    for run, sf in zip(map(Path, a.runs), map(Path, a.stems)):
        f = out / f"{run.name}.{a.mode}.json"
        if f.exists():
            print("skip", run.name); continue
        t0 = time.time()
        cfg = load_config(run / "config_used.yaml")
        stems, root, fold = check_lists(run, cfg, sf, fb, folds)
        wpath = run / "checkpoints" / "latest.pth"  # final weights; best.pth is never read
        st = torch.load(wpath, map_location="cpu", weights_only=False)
        step = int(st.get("step", -1))
        assert step == 20000, (run, step)
        mcfg = {k: v for k, v in cfg["model"].items() if k != "encoder_init"}
        mcfg["encoder_weights"] = None
        m = build_model(mcfg).to(DEV); m.load_state_dict(st["models"]["model"]); m.eval()
        del st
        gts = [np.array(Image.open(root / MASK_SUBDIR / f"{s}.png")) for s in stems]
        lg, _ = predict(m, root / "labeled" / "images", stems, cfg, False)
        pred = lg.argmax(1).numpy()
        pcr = torch.softmax(lg, 1)[:, CRACK].numpy()
        cells = {s: cell_stats(p, g, None, c) for s, p, g, c in zip(stems, pred, gts, pcr)}
        assert list(cells) == stems and len(cells) == len(stems), "output cell set != --stems"
        rv = run.parent.parent / "REVISION"
        cv = CODE / "REVISION"
        res = {"run": run.name, "mode": a.mode, "fold": fold, "seed": int(cfg["seed"]),
               "arm": "PF" if cfg["training"].get("encoder_pf") else "house",
               "weights": "model", "weights_file": "checkpoints/latest.pth", "weights_md5": md5(wpath), "step": step,
               "data_root": str(root), "stems_file": str(sf), "stems_md5": md5(sf),
               "root_test_md5": md5(root / "splits" / "test.txt"), "root_train_md5": md5(root / "splits" / "train.txt"),
               "config_md5": md5(run / "config_used.yaml"), "scorer_md5": me, "device": str(DEV), "tta": False,
               "code_revision": rv.read_text().strip() if rv.exists() else "none (see protocol)",
               "scorer_code_revision": cv.read_text().strip() if cv.exists() else "none",
               "sets_scored": ["heldout"], "cells": {"heldout": cells}}
        f.write_text(json.dumps(res))
        print(f"{run.name:28s} {res['arm']:5s} fold {fold} step {step} cells {len(cells)} ({time.time() - t0:.0f}s)",
              flush=True)
        del m
        if DEV.type == "cuda":
            torch.cuda.empty_cache()


if __name__ == "__main__":
    main()
