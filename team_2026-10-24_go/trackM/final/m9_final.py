"""Track M FINAL (protocol_final.md). Inference only.

VAL first (decisions written to <out>/final_val_decisions.json before any test inference):
  candidates E-rec (recipe's 5 seeds) and, if the recipe is not SUP100, E-union (recipe + SUP100, 10 models);
  E-union chosen only if its val score beats E-rec's by > 0.0016; TTA by R1 rule D1; crack bias by R1 rule D2 (grid 0..3
  step 0.25); headline bias = 0 if the chosen bias drops val crack precision by > 0.05.
TEST then: single plain per model (recipe and SUP100), the R1 model (SUP100 plain ensemble), FINAL at bias 0 and at the
chosen bias. EXT: FINAL at both biases, plus the R1 model.
Per cell: m_common.cell_stats (24x24 confusion, crack rel2, components, p-bands).
Usage (cv02): python m9_final.py --code /tmp/noob_el/el_mt5 --out final --rec <5 run dirs> --sup <5 run dirs>
"""
from __future__ import annotations

import argparse, json, os, sys, time
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--code", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--rec", nargs=5, required=True)
ap.add_argument("--sup", nargs=5, required=True)
ap.add_argument("--ext", default="/tmp/noob_el/ext117")
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
VL = [0, 1, 2, 4, 5, 7, 9, 11, 13, 14, 15, 16, 21]
GRID = [round(0.25 * i, 2) for i in range(13)]
SD_SCORE = 0.0016


def load(run: Path):
    cfg = load_config(run / "config_used.yaml")
    st = torch.load(run / "checkpoints" / "latest.pth", map_location="cpu", weights_only=False)
    assert int(st.get("step", -1)) == 20000, run
    key = "teacher" if cfg.get("method") == "mean_teacher" and "teacher" in st["models"] else "model"
    mcfg = {k: v for k, v in cfg["model"].items() if k != "encoder_init"}; mcfg["encoder_weights"] = None
    m = build_model(mcfg).to(DEV); m.load_state_dict(st["models"][key]); m.eval()
    return m, cfg


@torch.no_grad()
def probs(m, cfg, img_dir, stems, tta):
    d = cfg["data"]
    ds = BenchmarkELDataset(img_dir, None, stems, get_weak_augmentation(d.get("mean", [0.5]), d.get("std", [0.25]), d["input_size"]))
    P, T, got = [], [], []
    for b in DataLoader(ds, batch_size=8, shuffle=False, num_workers=4):
        x = b["image"].to(DEV); got += list(b["stem"])
        with torch.autocast("cuda", dtype=torch.bfloat16):
            lg = m(x).float()
        P.append(torch.softmax(lg, 1).cpu())
        if tta:
            acc = torch.zeros_like(lg)
            for i in range(8):
                with torch.autocast("cuda", dtype=torch.bfloat16):
                    li = m(dihedral(x, i)).float()
                acc += torch.softmax(dihedral(li, i, inv=True), 1)
            T.append((acc / 8).cpu())
    assert got == stems
    return torch.cat(P), (torch.cat(T) if tta else None)


def score(p, gts, keeps, stems, bias=0.0):
    out = {}
    for i, s in enumerate(stems):
        q = p[i].float(); lq = torch.log(q + 1e-12)
        if bias:
            lq[CRACK] += bias
        pc = (q[CRACK] if not bias else torch.softmax(lq, 0)[CRACK]).numpy()
        out[s] = cell_stats(lq.argmax(0).numpy(), gts[i], keeps[i], pc)
    return out


def summ(cells, cls):
    C = sum(np.array(v["conf"], np.int64).reshape(NC, NC) for v in cells.values())
    tp = np.diag(C).astype(float); g = C.sum(1); p = C.sum(0); den = g + p - tp
    iou = np.where(den > 0, tp / np.maximum(den, 1), np.nan)
    rel = np.sum([v["crack_rel2"] for v in cells.values()], 0)
    rP, rR = rel[0] / max(rel[1], 1), rel[2] / max(rel[3], 1)
    o = {"crack_iou": iou[CRACK], "crack_P": tp[CRACK] / max(p[CRACK], 1), "relP2": rP, "relR2": rR,
         "relF1": 2 * rP * rR / max(rP + rR, 1e-9), "miou_rob": float(np.nanmean([iou[c] for c in cls if g[c] > 0])), "inact_iou": iou[11]}
    o["score"] = float(np.mean([o["crack_iou"], o["relF1"], o["miou_rob"]]))
    return o


def main():
    torch.backends.cudnn.deterministic, torch.backends.cudnn.benchmark = True, False
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    rec, sup = [Path(r) for r in a.rec], [Path(r) for r in a.sup]
    same = [r.resolve() for r in rec] == [r.resolve() for r in sup]
    sets = {}
    for sp, n in (("val", 54), ("test", 50)):
        st = sorted(load_split(DATA / "splits" / f"{sp}.txt")); st = [s for s in st if (DATA / "escdd_masks" / sp / f"{s}.png").exists()]
        assert len(st) == n
        sets[sp] = (DATA / "labeled" / "images", st, [np.array(Image.open(DATA / "escdd_masks" / sp / f"{s}.png")) for s in st], [None] * n)
    ext = [l.strip() for l in open(Path(a.ext) / "stems_eval.txt") if l.strip()]; assert len(ext) == 106
    sets["ext"] = (Path(a.ext) / "images", ext, [np.array(Image.open(Path(a.ext) / "masks" / f"{s}.png")) for s in ext],
                   [~(np.array(Image.open(Path(a.ext) / "ignore" / f"{s}.png")) > 0) for s in ext])
    M_rec = [load(r) for r in rec]; M_sup = M_rec if same else [load(r) for r in sup]
    res = {"rec": [r.name for r in rec], "sup": [r.name for r in sup], "rec_is_sup": same, "code": str(CODE)}
    # ---------------- VAL
    img, stems, gts, keeps = sets["val"]
    PR = [probs(m, c, img, stems, True) for m, c in M_rec]
    PS = PR if same else [probs(m, c, img, stems, True) for m, c in M_sup]
    Erec_p = sum(p.float() for p, _ in PR) / 5; Erec_t = sum(t.float() for _, t in PR) / 5
    cand = {"E-rec": (Erec_p, Erec_t)}
    if not same:
        cand["E-union"] = ((Erec_p * 5 + sum(p.float() for p, _ in PS)) / 10, (Erec_t * 5 + sum(t.float() for _, t in PS)) / 10)
    vs = {k: summ(score(v[0], gts, keeps, stems), VL) for k, v in cand.items()}
    choice = "E-rec"
    if "E-union" in vs and vs["E-union"]["score"] > vs["E-rec"]["score"] + SD_SCORE:
        choice = "E-union"
    p_plain, p_tta = cand[choice]
    st_t = summ(score(p_tta, gts, keeps, stems), VL)
    use_tta = bool(st_t["score"] > vs[choice]["score"])
    base = p_tta if use_tta else p_plain
    sweep = {b: summ(score(base, gts, keeps, stems, b), VL) for b in GRID}
    ok = [b for b in GRID if sweep[b]["relR2"] >= 0.90]
    if ok and sweep[ok[0]]["relP2"] >= 0.90:
        bias, why = ok[0], "smallest bias with val relR@2 >= 0.90 and relP@2 >= 0.90"
    else:
        bias = max(GRID, key=lambda b: sweep[b]["relF1"]); why = "max val relF1@2"
    width = float(sweep[0.0]["crack_P"] - sweep[bias]["crack_P"])
    headline = 0.0 if width > 0.05 else bias
    dec = {"candidates_val": vs, "choice": choice, "tta_val": st_t, "use_tta": use_tta, "bias": bias, "why": why,
           "val_crack_precision_drop_at_bias": width, "headline_bias": headline, "sweep": {str(k): v for k, v in sweep.items()}}
    (out / "final_val_decisions.json").write_text(json.dumps(dec, indent=1, default=float))
    print("VAL decisions:", json.dumps({k: v for k, v in dec.items() if k not in ("sweep", "candidates_val", "tta_val")}, default=float), flush=True)
    res["val"] = {"final_b0": score(base, gts, keeps, stems), f"final_b{bias}": score(base, gts, keeps, stems, bias)}
    del PR, PS, cand, Erec_p, Erec_t, p_plain, p_tta, base
    # ---------------- TEST and EXT
    for sp in ("test", "ext"):
        t0 = time.time()
        img, stems, gts, keeps = sets[sp]
        PR = [probs(m, c, img, stems, use_tta) for m, c in M_rec]
        PS = PR if same else [probs(m, c, img, stems, use_tta) for m, c in M_sup]
        R = {}
        Erec = sum((t if use_tta else p).float() for p, t in PR) / 5
        F = Erec if choice == "E-rec" else (Erec * 5 + sum((t if use_tta else p).float() for p, t in PS)) / 10
        R["final_b0"] = score(F, gts, keeps, stems)
        if bias:
            R[f"final_b{bias}"] = score(F, gts, keeps, stems, bias)
        R["r1_model"] = score(sum(p.float() for p, _ in PS) / 5, gts, keeps, stems)
        if sp == "test":
            for (p, _), r in zip(PR, rec):
                R[f"rec_single/{r.name}"] = score(p, gts, keeps, stems)
            if not same:
                for (p, _), r in zip(PS, sup):
                    R[f"sup_single/{r.name}"] = score(p, gts, keeps, stems)
        res[sp] = R
        print(f"{sp} done ({time.time() - t0:.0f}s)", flush=True)
        (out / "final_cells.json").write_text(json.dumps(res))
        del PR, PS, Erec, F


if __name__ == "__main__":
    main()
