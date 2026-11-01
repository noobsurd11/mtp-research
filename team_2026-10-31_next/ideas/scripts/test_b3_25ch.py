"""calib (1 Nov): does the FROZEN B5 path (calib_dump c172717e maps(), el_metrics 6e73ff11) handle B3's 25-channel head?
Reference = m0_audit_b3's rule: pred = argmax over all 25 channels, then class >= 24 -> 0 (fold_scuff); 24x24 conf via Track M
cell_stats. Our path: margin = log p_crack - max_{k != crack} log p_k over ALL channels (scuff included), oth = argmax over the
non-crack channels (may be 24); el_metrics uses oth only as (oth == 11). Exact equality is expected.
Part 1: synthetic 25-channel logits (no model). Part 2 (optional, --run): one real B3 checkpoint, val only, CPU fp32; the reference
is computed from the SAME CPU forward (so equality must be exact); the step assert is not applied (smoke checkpoint).
Runs on gaint (torch): python test_b3_25ch.py --code EL_THIN --calib FROZEN_DIR --tm TRACKM_SCRIPTS [--run RUN_DIR --n 54]
"""
import argparse
import ast
import sys
from pathlib import Path

import numpy as np
import torch
from PIL import Image

ap = argparse.ArgumentParser()
ap.add_argument("--code", required=True)
ap.add_argument("--calib", required=True, help="dir with the frozen calib_dump.py and el_metrics.py")
ap.add_argument("--tm", required=True, help="Track M scripts dir (m_common.py)")
ap.add_argument("--run")
ap.add_argument("--n", type=int, default=54)
a = ap.parse_args()
sys.path.insert(0, a.calib); sys.path.insert(0, a.tm)
import el_metrics as E  # noqa: E402  (frozen file)
from m_common import cell_stats, NC  # noqa: E402

CRACK = 14
# the frozen calib_dump.maps(), extracted verbatim from the file (not re-typed)
src = open(Path(a.calib) / "calib_dump.py").read()
fn = next(n for n in ast.parse(src).body if isinstance(n, ast.FunctionDef) and n.name == "maps")
ns = {"torch": torch, "np": np, "CRACK": CRACK}
exec(compile(ast.Module([fn], []), "calib_dump.maps", "exec"), ns)
maps = ns["maps"]


def fold(p):
    return np.where(p >= 24, 0, p)


def compare(prob, gt, keep=None):
    """prob: (25, H, W) softmax. Returns list of mismatches between the frozen path's records at b = 0 and the m0_audit_b3 rule."""
    mg, oth, _ = maps(prob)
    rec = E.cell_record(mg, oth, gt, keep)
    pred = fold(prob.argmax(0).numpy())
    ref = cell_stats(pred, gt, keep)
    C = np.array(ref["conf"]).reshape(NC, NC); j = int(np.argmin(np.abs(E.GRID)))
    chk = {"pred": C[:, 14].sum(), "tp": C[14, 14], "relp_tp": ref["crack_rel2"][0], "relr_tp": ref["crack_rel2"][2],
           "inact_pred": C[:, 11].sum(), "inact_tp": C[11, 11]}
    bad = [(k, int(rec[k][j]), int(v)) for k, v in chk.items() if int(rec[k][j]) != int(v)]
    g20 = [c for c in ref["crack_cc"]["gt"] if c[0] >= 20]
    if sum(c[1] >= 0.5 * c[0] for c in g20) != sum(x[1] > 0 for x in rec["gt_cc"] if x[0] >= 20):
        bad.append(("gt_found", None, None))
    p20 = [c for c in ref["crack_cc"]["pr"] if c[0] >= 20]
    if len(p20) != rec["pc20_n"][j] or sum(c[1] > 0 for c in p20) != rec["pc20_hit"][j]:
        bad.append(("pred_comps", None, None))
    return bad, ref, rec, int((oth == 24).sum()), int((prob.argmax(0) == 24).sum())


# ---- part 1: synthetic 25-channel logits with scuff often the top class, competing with crack and inactive
rng = np.random.default_rng(3); nbad = 0; n24 = 0
for t in range(20):
    H = 96
    gt = np.zeros((H, H), np.uint8); gt[rng.integers(0, H - 20):][:12, :30] = 11
    for _ in range(3):
        y = rng.integers(5, H - 5); x0, x1 = sorted(rng.integers(0, H, 2)); gt[y, x0:x1] = 14
    lg = torch.from_numpy(rng.normal(0, 1.5, (25, H, H)).astype(np.float32))
    lg[14] += torch.from_numpy((gt == 14) * 3.0 + rng.normal(0, 1, (H, H))).float()
    lg[11] += torch.from_numpy((gt == 11) * 3.0).float()
    lg[24] += torch.from_numpy(rng.normal(1.0, 1.5, (H, H))).float()  # scuff channel competes everywhere
    prob = torch.softmax(lg, 0)
    bad, _, _, o24, a24 = compare(prob, gt)
    nbad += len(bad); n24 += a24
    if bad:
        print("SYNTH MISMATCH", t, bad)
print(f"part 1 (synthetic 25-ch, 20 cells): px where the 25-way argmax is scuff {n24}; mismatches {nbad}")

# ---- part 2: a real B3 checkpoint on val (CPU fp32, same forward on both sides)
if a.run:
    sys.path.insert(0, a.code)
    from src.models.model_factory import build_model  # noqa: E402
    from src.utils.config import load_config  # noqa: E402
    run = Path(a.run); cfg = load_config(run / "config_used.yaml")
    st = torch.load(run / "checkpoints" / "latest.pth", map_location="cpu", weights_only=False)
    mc = {k: v for k, v in cfg["model"].items() if k not in ("encoder_init", "decoder_init")}; mc["encoder_weights"] = None
    m = build_model(mc); m.load_state_dict(st["models"]["model"]); m.eval()
    D = Path(a.code) / "data"
    val = sorted(l.strip() for l in open(D / "splits" / "val.txt") if l.strip())[:a.n]
    nb = 0; s24 = 0; tot = {"rec": np.zeros(4), "ref": np.zeros(4)}
    torch.set_num_threads(8)
    with torch.no_grad():
        for s in val:
            g = np.array(Image.open(D / "labeled" / "images" / f"{s}.png").convert("L"), np.float32) / 255.0
            x = torch.from_numpy((g - 0.5) / 0.25)[None, None]
            lg = m(x).float()
            assert lg.shape[1] == 25, lg.shape
            prob = torch.softmax(lg, 1)[0]
            gt = np.array(Image.open(D / "labeled" / "masks_escdd" / f"{s}.png"))
            bad, ref, rec, o24, a24 = compare(prob, gt)
            nb += len(bad); s24 += a24
            if bad:
                print("REAL MISMATCH", s, bad)
    print(f"part 2 ({run.name}, step {st.get('step')}, {len(val)} val cells, CPU fp32): px where the 25-way argmax is scuff {s24}; mismatches {nb}")
