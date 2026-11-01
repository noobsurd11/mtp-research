import sys, numpy as np
import types; sys.modules["torch"] = types.ModuleType("torch"); sys.modules["torch"].Tensor = object
sys.path.insert(0, '/home/yugma/mtp/research/team_2026-10-31_next/ideas/scripts')
sys.path.insert(0, '/home/yugma/mtp/research/team_2026-10-24_go/trackM/scripts')
import el_metrics as E
from m_common import cell_stats, NC
from scipy import ndimage as ndi
rng = np.random.default_rng(0)
bad = 0
for trial in range(12):
    H = 128
    gt = rng.integers(0, 3, (H, H)).astype(np.uint8) * 0
    # GT cracks: random lines
    for _ in range(rng.integers(0, 5)):
        y = rng.integers(5, H-5); x0, x1 = sorted(rng.integers(0, H, 2)); gt[y, x0:x1] = 14
        if rng.random() < .5: gt[y+1, x0:x1] = 14
    gt[rng.integers(0, H-20):, :][:10, :20] = 11  # inactive block
    gt[:, :3] = 7
    sm = ndi.gaussian_filter((gt == 14).astype(float), 1.5) * 20 - 6 + rng.normal(0, 2, (H, H))
    margin = sm.astype(np.float16)
    oth = np.where(gt == 11, 11, np.where(rng.random((H, H)) < 0.05, 11, 0)).astype(np.uint8)
    keep = None if trial % 2 else (rng.random((H, H)) > 0.1)
    rec = E.cell_record(margin, oth, gt, keep)
    for b in (0.0, 0.75, 2.0, -1.5):
        j = int(np.argmin(np.abs(E.GRID - b)))
        pred = np.where(margin.astype(np.float32) + b > 0, 14, oth).astype(np.int64)
        o = cell_stats(pred, gt, keep)
        C = np.array(o['conf']).reshape(NC, NC)
        k = np.ones_like(gt, bool) if keep is None else keep
        chk = {'pred': C[:, 14].sum(), 'tp': C[14, 14], 'relp_tp': o['crack_rel2'][0], 'relr_tp': o['crack_rel2'][2],
               'inact_pred': C[:, 11].sum(), 'inact_tp': C[11, 11]}
        for key, v in chk.items():
            if rec[key][j] != v: bad += 1; print('MISMATCH', trial, b, key, rec[key][j], v)
        assert o['crack_rel2'][1] == rec['pred'][j] and o['crack_rel2'][3] == rec['n_gt']
        # components
        gg = [c for c in o['crack_cc']['gt'] if c[0] >= 20]
        f_ref = sum(c[1] >= 0.5 * c[0] for c in gg)
        f_me = sum(x[1] + b > 0 for x in rec['gt_cc'] if x[0] >= 20)
        pp = [c for c in o['crack_cc']['pr'] if c[0] >= 20]
        if f_ref != f_me or len(pp) != rec['pc20_n'][j] or sum(c[1] > 0 for c in pp) != rec['pc20_hit'][j]:
            bad += 1; print('CC MISMATCH', trial, b, f_ref, f_me, len(pp), rec['pc20_n'][j])
        # speck guard (coach A1)
        pa = o['crack_cc']['pr']
        if len(pa) != rec['pc_n'][j] or sum(c[1] > 0 for c in pa) != rec['pc_hit'][j] or sum(c[0] for c in pa if c[0] < 20) != rec['speck_px'][j]:
            bad += 1; print('SPECK MISMATCH', trial, b)
        # cell flag
        npx = int(((pred == 14) & k).sum())
        if (npx >= 20) != (rec['s']['20'] + b > 0): bad += 1; print('FLAG MISMATCH', trial, b, npx, rec['s']['20'])
print('mismatches', bad)
print('auroc test', E._auroc([3, 2, 2], [2, 1, 0]))  # expect (1+1+... ) = ?


# ---- pooled arm-level OP (coach, 31 Oct): pooled curves and the chosen b vs brute force over all runs' cells ----
def _brute_pooled(runs_cells, b):
    rp = pp = rr = gg = 0; gf = gn = 0; ph = pn = 0
    for cells in runs_cells:
        for (margin, oth, gt, keep) in cells:
            pred = np.where(margin.astype(np.float32) + b > 0, 14, oth).astype(np.int64)
            o = cell_stats(pred, gt, keep)
            rp += o['crack_rel2'][0]; pp += o['crack_rel2'][1]; rr += o['crack_rel2'][2]; gg += o['crack_rel2'][3]
            g20 = [c for c in o['crack_cc']['gt'] if c[0] >= 20]; gn += len(g20); gf += sum(c[1] >= 0.5 * c[0] for c in g20)
            p20 = [c for c in o['crack_cc']['pr'] if c[0] >= 20]; pn += len(p20); ph += sum(c[1] > 0 for c in p20)
    return rp / max(pp, 1), rr / max(gg, 1), gf / max(gn, 1), ph / max(pn, 1) if pn else float('nan')


rng2 = np.random.default_rng(7); runs_cells = []; recs = []
H = 96
base = []
for k in range(5):
    gt = np.zeros((H, H), np.uint8)
    for _ in range(3):
        y = rng2.integers(5, H - 5); x0, x1 = sorted(rng2.integers(0, H, 2)); gt[y, x0:x1] = 14; gt[y + 1, x0:x1] = 14
    base.append(gt)
for r in range(3):
    cells = []; rc = {}
    for k, gt in enumerate(base):
        m = (ndi.gaussian_filter((gt == 14).astype(float), 1.3) * (14 + 4 * r) - 5 - r + rng2.normal(0, 2.2, (H, H))).astype(np.float16)
        oth = np.zeros((H, H), np.uint8)
        cells.append((m, oth, gt, None))
        rc[f"c{k}"] = {kk: (vv.tolist() if isinstance(vv, np.ndarray) else vv) for kk, vv in E.cell_record(m, oth, gt, None).items()}
    runs_cells.append(cells); recs.append({"set": "val", "cells": rc})
pc = E.curves(E.pool_cells(recs))
badp = 0
sub = [j for j in range(len(E.GRID)) if E.OPGRID[j]][::7]
for j in sub:
    b = float(E.GRID[j]); P, R, CR, CP = _brute_pooled(runs_cells, b)
    for name, mine, ref in (("relP", pc["relP"][j], P), ("relR", pc["relR"][j], R), ("compR", pc["compR"][j], CR), ("compP", pc["compP"][j], CP)):
        if not ((np.isnan(mine) and np.isnan(ref)) or abs(mine - ref) < 1e-12):
            badp += 1; print("POOLED MISMATCH", b, name, mine, ref)
# chosen b vs brute force over the full OP grid
cand = [j for j in range(len(E.GRID)) if E.OPGRID[j]]
bf = [(float(E.GRID[j]),) + _brute_pooled(runs_cells, float(E.GRID[j])) for j in cand]
for rk, pk, idx_r, idx_p in (("relR", "relP", 2, 1), ("compR", "compP", 3, 4)):
    ok = [t for t in bf if not np.isnan(t[idx_p]) and t[idx_p] >= 0.90]
    ref_b = (max(ok, key=lambda t: (t[idx_r], -t[0]))[0] if ok else max(bf, key=lambda t: (np.nan_to_num(t[idx_p], nan=-1), -t[0]))[0])
    got = E.choose_op(pc, rk, pk)
    if abs(got["b"] - ref_b) > 1e-9:
        badp += 1; print("POOLED OP MISMATCH", rk, got["b"], ref_b)
    print(f"pooled OP {rk}: b {got['b']} (brute {ref_b}) reachable {got['reachable']} edge {got['edge']}")
print("pooled mismatches", badp)


# ---- routing (protocol_PF2 §13): b_full / b_hc and routed vs unrouted E1 metrics vs brute force ----
def _cells(seed, n, H=96, shift=0.0):
    r_ = np.random.default_rng(seed); out = []
    for k in range(n):
        gt = np.zeros((H, H), np.uint8)
        if k % 3:
            for _ in range(2):
                y = r_.integers(5, H - 5); x0, x1 = sorted(r_.integers(0, H, 2)); gt[y, x0:x1] = 14; gt[y + 1, x0:x1] = 14
        m = (ndi.gaussian_filter((gt == 14).astype(float), 1.3) * 16 - 6 - shift + r_.normal(0, 2.0, (H, H))).astype(np.float16)
        out.append((m, np.zeros((H, H), np.uint8), gt, None))
    return out


def _rec(cells, set_, prefix):
    return {"set": set_, "runs": [prefix], "cells": {f"{prefix}{k}": {kk: (vv.tolist() if isinstance(vv, np.ndarray) else vv)
                                                       for kk, vv in E.cell_record(*c).items()} for k, c in enumerate(cells)}}


def _bf_f1(cell_lists, bmaps):
    rp = pp = rr = gg = 0
    for cells, bm in zip(cell_lists, bmaps):
        for (m, o, gt, kp), b in zip(cells, bm):
            pred = np.where(m.astype(np.float32) + b > 0, 14, o).astype(np.int64); st = cell_stats(pred, gt, kp)
            rp += st['crack_rel2'][0]; pp += st['crack_rel2'][1]; rr += st['crack_rel2'][2]; gg += st['crack_rel2'][3]
    P = rp / pp if pp else float('nan'); R = rr / gg if gg else float('nan')
    return 2 * P * R / (P + R) if (pp and gg and P + R > 0) else 0.0


badr = 0
VAL = [_cells(100 + i, 4) for i in range(2)]; SYN = [_cells(200 + i, 4, shift=3.0) for i in range(2)]; EXT = [_cells(300 + i, 6, shift=1.5) for i in range(2)]
vrec = [_rec(c, "val", "v") for c in VAL]; srec = [_rec(c, "synval", "s") for c in SYN]; erec = [_rec(c, "ext", "e") for c in EXT]
hc = {"e1", "e3", "e5"}
out = E.routing(vrec, srec, erec, hc)
cand = [float(E.GRID[j]) for j in range(len(E.GRID)) if E.OPGRID[j]]
for name, cl, key in (("b_full", VAL, "b_full"), ("b_hc", SYN, "b_hc")):
    f1s = [_bf_f1(cl, [[b] * len(c) for c in cl]) for b in cand]
    ref = cand[int(np.argmax(f1s))]
    if abs(out[key]["b"] - ref) > 1e-9:
        badr += 1; print("ROUTING B MISMATCH", name, out[key]["b"], ref)
bfull, bhc = out["b_full"]["b"], out["b_hc"]["b"]
for i, cells in enumerate(EXT):
    un = _bf_f1([cells], [[bfull] * len(cells)])
    ro = _bf_f1([cells], [[bhc if f"e{k}" in hc else bfull for k in range(len(cells))]])
    if abs(un - out["per_run"][i]["unrouted"]["relF1"]) > 1e-12 or abs(ro - out["per_run"][i]["routed"]["relF1"]) > 1e-12:
        badr += 1; print("ROUTING F1 MISMATCH", i, un, out["per_run"][i]["unrouted"]["relF1"], ro, out["per_run"][i]["routed"]["relF1"])
print(f"routing: b_full {bfull} b_hc {bhc} delta_b {out['delta_b']:.1f} no_op {out['no_op']}; routing mismatches", badr)
