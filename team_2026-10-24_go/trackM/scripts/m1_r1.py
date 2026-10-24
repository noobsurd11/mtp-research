"""Track M, rung R1 (protocol_r1.md): post hoc layer on the SUP100 checkpoints. Inference only.

Order of work (val decisions are written before any test number is computed):
  1. VAL: per-seed plain and TTA; 5-seed ensemble plain and TTA; 5 leave-one-out ensembles (plain).
     Decide TTA-on-ensemble (protocol rule D1) and the crack operating point (rule D2, grid 0..3 step 0.25).
     Write decisions to <out>/r1_val_decisions.json.
  2. TEST: per-seed plain and TTA; ensemble plain and TTA; LOO ensembles; the chosen R1 model at bias 0 and at the
     chosen bias. Nothing else is computed on test.
Per cell the same stats as M0 (24x24 confusion, crack rel2, components, p-bands) via m_common.cell_stats.

Usage (cv02): python m1_r1.py --code /tmp/noob_el/el_m --out r1 --runs <5 run dirs>
"""
from __future__ import annotations

import argparse, json, os, sys, time
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--code", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--runs", nargs=5, required=True)
a = ap.parse_args()
CODE = Path(a.code).resolve()
sys.path.insert(0, str(CODE)); sys.path.insert(0, str(Path(__file__).resolve().parent))
os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")

import numpy as np  # noqa: E402
import torch  # noqa: E402
from PIL import Image  # noqa: E402
from torch.utils.data import DataLoader  # noqa: E402

from src.data.augmentations import get_weak_augmentation  # noqa: E402
from src.data.benchmark_el import BenchmarkELDataset  # noqa: E402
from src.data.splits import load_split  # noqa: E402
from src.models.model_factory import build_model  # noqa: E402
from src.utils.config import load_config  # noqa: E402
from m_common import NC, CRACK, cell_stats, dihedral  # noqa: E402

DEV = torch.device("cuda")
DATA = CODE / "data"
VAL_LIST = [0, 1, 2, 4, 5, 7, 9, 11, 13, 14, 15, 16, 21]
GRID = [round(0.25 * i, 2) for i in range(13)]


def load(run: Path):
    cfg = load_config(run / "config_used.yaml")
    st = torch.load(run / "checkpoints" / "latest.pth", map_location="cpu", weights_only=False)
    assert int(st.get("step", -1)) == 20000
    key = "teacher" if cfg.get("method") == "mean_teacher" and "teacher" in st["models"] else "model"
    mcfg = {k: v for k, v in cfg["model"].items() if k != "encoder_init"}; mcfg["encoder_weights"] = None
    m = build_model(mcfg).to(DEV); m.load_state_dict(st["models"][key]); m.eval()
    return m, cfg


@torch.no_grad()
def probs(m, cfg, stems):
    """Returns (plain softmax, TTA mean softmax), float32 CPU tensors [N,24,H,W]."""
    d = cfg["data"]
    ds = BenchmarkELDataset(DATA / "labeled" / "images", None, stems, get_weak_augmentation(d.get("mean", [0.5]), d.get("std", [0.25]), d["input_size"]))
    P, T, got = [], [], []
    for b in DataLoader(ds, batch_size=8, shuffle=False, num_workers=4):
        x = b["image"].to(DEV); got += list(b["stem"])
        with torch.autocast("cuda", dtype=torch.bfloat16):
            lg = m(x).float()
        P.append(torch.softmax(lg, 1).cpu())
        acc = torch.zeros_like(lg)
        for i in range(8):
            with torch.autocast("cuda", dtype=torch.bfloat16):
                li = m(dihedral(x, i)).float()
            acc += torch.softmax(dihedral(li, i, inv=True), 1)
        T.append((acc / 8).cpu())
    assert got == stems
    return torch.cat(P), torch.cat(T)


def score(p: torch.Tensor, gts, stems, bias: float = 0.0) -> dict:
    out = {}
    for i, s in enumerate(stems):
        q = p[i].float()
        lq = torch.log(q + 1e-12)
        if bias:
            lq[CRACK] += bias
        pred = lq.argmax(0).numpy()
        pc = (q[CRACK] if not bias else torch.softmax(lq, 0)[CRACK]).numpy()
        out[s] = cell_stats(pred, gts[i], None, pc)
    return out


def summary(cells: dict, cls: list[int]) -> dict:
    C = sum(np.array(v["conf"], np.int64).reshape(NC, NC) for v in cells.values())
    tp = np.diag(C).astype(float); g = C.sum(1); p = C.sum(0); den = g + p - tp
    iou = np.where(den > 0, tp / np.maximum(den, 1), np.nan)
    rel = np.sum([v["crack_rel2"] for v in cells.values()], 0)
    rP, rR = rel[0] / max(rel[1], 1), rel[2] / max(rel[3], 1)
    return {"crack_iou": iou[CRACK], "crack_P": tp[CRACK] / max(p[CRACK], 1), "relP2": rP, "relR2": rR,
            "relF1": 2 * rP * rR / max(rP + rR, 1e-9), "miou_rob": float(np.nanmean([iou[c] for c in cls if g[c] > 0])),
            "inact_iou": iou[11]}


def main():
    torch.backends.cudnn.deterministic, torch.backends.cudnn.benchmark = True, False
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    runs = [Path(r) for r in a.runs]
    names = [r.name for r in runs]
    sets = {}
    for sp, n in (("val", 54), ("test", 50)):
        st = sorted(load_split(DATA / "splits" / f"{sp}.txt"))
        st = [s for s in st if (DATA / "escdd_masks" / sp / f"{s}.png").exists()]
        assert len(st) == n
        sets[sp] = (st, [np.array(Image.open(DATA / "escdd_masks" / sp / f"{s}.png")) for s in st])
    models = [load(r) for r in runs]
    res = {"runs": names, "code": str(CODE)}
    dec = None
    for sp in ("val", "test"):
        t0 = time.time()
        stems, gts = sets[sp]
        PT = [probs(m, c, stems) for m, c in models]
        R = {}
        for nm, (P, T) in zip(names, PT):
            R[f"single_plain/{nm}"] = score(P, gts, stems)
            R[f"single_tta/{nm}"] = score(T, gts, stems)
        EP = sum(P.float() for P, _ in PT) / 5
        ET = sum(T.float() for _, T in PT) / 5
        R["ens_plain"] = score(EP, gts, stems)
        R["ens_tta"] = score(ET, gts, stems)
        for k, nm in enumerate(names):
            R[f"loo_plain/-{nm}"] = score((EP * 5 - PT[k][0].float()) / 4, gts, stems)
        if sp == "val":
            sp_ = summary(R["ens_plain"], VAL_LIST); st_ = summary(R["ens_tta"], VAL_LIST)
            score_p = np.mean([sp_["crack_iou"], sp_["relF1"], sp_["miou_rob"]])
            score_t = np.mean([st_["crack_iou"], st_["relF1"], st_["miou_rob"]])
            use_tta = bool(score_t > score_p)
            base = ET if use_tta else EP
            sweep = {}
            for b in GRID:
                sweep[b] = summary(score(base, gts, stems, b), VAL_LIST)
            ok = [b for b in GRID if sweep[b]["relR2"] >= 0.90]
            if ok and sweep[ok[0]]["relP2"] >= 0.90:
                bias, why = ok[0], "smallest bias with val relR@2 >= 0.90 and relP@2 >= 0.90"
            else:
                bias = max(GRID, key=lambda b: sweep[b]["relF1"]); why = "max val relF1@2 (target not reachable at relP@2 >= 0.90)"
            dec = {"use_tta_on_ensemble": use_tta, "score_ens_plain": score_p, "score_ens_tta": score_t,
                   "crack_bias": bias, "why": why, "sweep": {str(k): v for k, v in sweep.items()}}
            R[f"r1_final_bias{bias}"] = score(base, gts, stems, bias)
            (out / "r1_val_decisions.json").write_text(json.dumps(dec, indent=1, default=float))
            print("VAL decisions:", json.dumps({k: v for k, v in dec.items() if k != "sweep"}, default=float), flush=True)
        else:
            base = ET if dec["use_tta_on_ensemble"] else EP
            R[f"r1_final_bias{dec['crack_bias']}"] = score(base, gts, stems, dec["crack_bias"])
        res[sp] = R
        del PT, EP, ET
        print(f"{sp} done ({time.time() - t0:.0f}s)", flush=True)
        (out / "r1_cells.json").write_text(json.dumps(res))


if __name__ == "__main__":
    main()
