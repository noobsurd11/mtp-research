"""PF2 opening extra pass (protocol_PF2.md section 4.3, Om B2): test primaries with the 236 raw E-SCDD scuff px (class 25) set to
ignore in ARTS_00047_r3_c1 (34 px) and ARTS_00051_r3_c2 (202 px). Descriptive only; the verdict uses the current test masks.
Per run: model built and test (50 cells) inferred exactly as el_f1 m0_audit.py (md5 d36f7438; predict / cell_stats / comps copied
below, code lines unchanged, docstring / comments / the TTA branch dropped; same batch 8, bf16 autocast, deterministic cuDNN). SELF-CHECK first: the 2 cells' stats with the original keep must
equal the opening's m0 JSON entries exactly, else exit 1 with nothing written. Output <out>/<run>.scuffign.json = the m0 JSON with
those 2 test cells replaced by their stats under keep = ~(raw E-SCDD class 25), so Track M m2_rung / ssl readers run unchanged.
--selfcheck-only: run the self-check and write nothing else (used once before PF2 on a protocol_100 run already opened: no new test
number is computed or stored).
Usage: python pf2_scuffign.py --code EL_F3 --m0 POST/m0 --out POST/m0_scuffign --runs RUN_DIR ... [--selfcheck-only]
"""
from __future__ import annotations

import argparse, json, os, sys
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--code", required=True); ap.add_argument("--m0", required=True); ap.add_argument("--out", required=True)
ap.add_argument("--runs", nargs="+", required=True); ap.add_argument("--selfcheck-only", action="store_true")
ap.add_argument("--raw", default="/home/noob/work/el-fault-detection/data/escdd_masks/test")
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

NC, CRACK, INACT, SCUFF = 24, 14, 11, 25
DEV = torch.device("cuda")
DATA = CODE / "data"
S8 = np.ones((3, 3), bool)
CELLS = {"ARTS_00047_r3_c1": 34, "ARTS_00051_r3_c2": 202}


# ---- copied from m0_audit.py (d36f7438): code lines unchanged; docstring, comments and the TTA branch dropped ----
def comps(gt_m: np.ndarray, pr_m: np.ndarray, near_pr: np.ndarray | None, near_gt: np.ndarray | None):
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
    if pc is not None:
        o["crack_pband_gt"] = np.histogram(pc[g], BANDS)[0].tolist()
        o["crack_pband_neg"] = np.histogram(pc[k & ~g], BANDS)[0].tolist()
        b = np.clip((pc * 1000).astype(int), 0, 999)
        o["crack_h1000_pos"] = np.bincount(b[g], minlength=1000).tolist()
        o["crack_h1000_neg"] = np.bincount(b[k & ~g], minlength=1000).tolist()
    return o


@torch.no_grad()
def predict(m, img_dir: Path, stems: list[str], cfg: dict):
    d = cfg["data"]
    ds = BenchmarkELDataset(img_dir, None, stems, get_weak_augmentation(d.get("mean", [0.5]), d.get("std", [0.25]), d["input_size"]))
    plain, got = [], []
    for b in DataLoader(ds, batch_size=8, shuffle=False, num_workers=4):
        x = b["image"].to(DEV)
        with torch.autocast("cuda", dtype=torch.bfloat16):
            lg = m(x).float()
        plain.append(lg.cpu())
        got += list(b["stem"])
    assert got == stems, "stem order"
    return torch.cat(plain)
# ---- end copy ----


def main() -> None:
    torch.backends.cudnn.deterministic, torch.backends.cudnn.benchmark = True, False
    st_ = sorted(load_split(DATA / "splits" / "test.txt"))
    st_ = [s for s in st_ if (DATA / "escdd_masks" / "test" / f"{s}.png").exists()]
    assert len(st_) == 50 and all(c in st_ for c in CELLS)
    gts = {s: np.array(Image.open(DATA / "escdd_masks" / "test" / f"{s}.png")) for s in CELLS}
    keep = {}
    for s, n in CELLS.items():
        raw = np.array(Image.open(Path(a.raw) / f"{s}.png"))
        sc = raw == SCUFF
        assert int(sc.sum()) == n and int((gts[s][sc] == CRACK).sum()) == n, (s, int(sc.sum()), n)
        keep[s] = ~sc
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    for run in map(Path, a.runs):
        cfg = load_config(run / "config_used.yaml")
        st = torch.load(run / "checkpoints" / "latest.pth", map_location="cpu", weights_only=False)
        assert int(st.get("step", -1)) == 20000, (run, st.get("step"))
        mcfg = {k: v for k, v in cfg["model"].items() if k != "encoder_init"}
        mcfg["encoder_weights"] = None
        m = build_model(mcfg).to(DEV); m.load_state_dict(st["models"]["model"]); m.eval()
        lg = predict(m, DATA / "labeled" / "images", st_, cfg)
        pred = lg.argmax(1).numpy(); pcr = torch.softmax(lg, 1)[:, CRACK].numpy()
        ref = json.load(open(Path(a.m0) / f"{run.name}.json"))
        idx = {s: st_.index(s) for s in CELLS}
        for s, i in idx.items():
            mine = json.loads(json.dumps(cell_stats(pred[i], gts[s], None, pcr[i])))
            if mine != ref["cells"]["test"][s]:
                print(f"SELF-CHECK FAIL {run.name} {s}", flush=True); sys.exit(1)
        print(f"self-check OK {run.name}: 2 cells equal the m0 JSON", flush=True)
        if not a.selfcheck_only:
            for s, i in idx.items():
                ref["cells"]["test"][s] = cell_stats(pred[i], gts[s], keep[s], pcr[i])
            ref["scuffign"] = {s: n for s, n in CELLS.items()}
            (out / f"{run.name}.scuffign.json").write_text(json.dumps(ref))
        del m; torch.cuda.empty_cache()


if __name__ == "__main__":
    main()
