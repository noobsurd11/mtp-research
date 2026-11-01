"""coach (1 Nov): independent recompute of protocol_PF2E's verdict from runner's per-cell JSONs (own metric + bootstrap code;
not Track M m1_analyze / runner's pf2e_boot). Point estimates must equal runner's exactly; CIs use my own resampling
(numpy default_rng(12345), cell / cluster indices with replacement), so they differ from runner's in the 3rd decimal: the
verdict must agree unless a bound sits within ~0.002 of 0 (then flagged).
Also: val decisions re-derived (D2 rule on the stored sweep; the stored sweep entries at the scored b's re-computed from the val cells).
Usage: python coach_pf2e.py OUT_DIR"""
import json, re, sys
import numpy as np
from pathlib import Path

NC, CR, IN = 24, 14, 11
NOISY = 'CSIR_00070_r8_c4'
D = Path(sys.argv[1])
dec = json.load(open(D / 'pf2e_val_decisions.json'))
GRID = [round(0.25 * i, 2) for i in range(13)]


def prim(C, R):
    tp = np.diag(C); g = C.sum(1); p = C.sum(0)
    io = lambda k: tp[k] / (g[k] + p[k] - tp[k]) if (g[k] + p[k] - tp[k]) > 0 else np.nan
    rp, rr = R[0] / max(R[1], 1), R[2] / max(R[3], 1)
    return np.array([io(CR), 2 * rp * rr / max(rp + rr, 1e-9), io(IN)])  # crack IoU, relF1@2, inactive IoU


def arrays(cells, stems):
    return (np.stack([np.asarray(cells[s]['conf'], np.int64).reshape(NC, NC) for s in stems]),
            np.stack([np.asarray(cells[s]['crack_rel2'], np.int64) for s in stems]))


def summ(cells):
    C, R = arrays(cells, sorted(cells)); C, R = C.sum(0), R.sum(0)
    tp = np.diag(C); p = C.sum(0)
    rp, rr = R[0] / max(R[1], 1), R[2] / max(R[3], 1)
    return {'crack_iou': prim(C, R)[0], 'crack_P': tp[CR] / max(p[CR], 1), 'relP2': rp, 'relR2': rr, 'relF1': prim(C, R)[1]}


# ---- val decisions
print('## val decisions (D2 rule re-applied to the stored sweep; stored entries at scored b re-computed from val cells)')
hb = {}
for k in ('E-g', 'E-PF'):
    sw = {float(b): v for b, v in dec[k]['sweep'].items()}
    ok = [b for b in GRID if sw[b]['relR2'] >= 0.90]
    bias = ok[0] if ok and sw[ok[0]]['relP2'] >= 0.90 else max(GRID, key=lambda b: sw[b]['relF1'])
    width = sw[0.0]['crack_P'] - sw[bias]['crack_P']; head = 0.0 if width > 0.05 else bias
    assert bias == dec[k]['bias'] and head == dec[k]['headline_bias'], (k, bias, head, dec[k]['bias'], dec[k]['headline_bias'])
    hb[k] = head
    for b in sorted({0.0, bias, head}):
        j = json.load(open(D / f'{k}.b{b:g}.json')); assert j['bias'] == b and j['step'] == 20000 and j['code_revision'] == 'e544133'
        mine = summ(j['cells']['val'])
        for q in ('crack_iou', 'crack_P', 'relP2', 'relR2', 'relF1'):
            assert abs(mine[q] - sw[b][q]) < 1e-9, (k, b, q, mine[q], sw[b][q])
    print(f'  {k}: chosen b {bias} (val relR@2 {sw[bias]["relR2"]:.4f} relP@2 {sw[bias]["relP2"]:.4f} relF1 {sw[bias]["relF1"]:.4f}), '
          f'val crack P drop {width:+.4f} -> headline b {head}; sweep entries at scored b == own val recompute: OK')

rng = np.random.default_rng(12345); NB = 2000


def boot(A, B, groups):
    """groups: list of index arrays (cells or clusters). Paired: same draws for both arms."""
    CA, RA = A; CB, RB = B
    full = prim(CB.sum(0), RB.sum(0)) - prim(CA.sum(0), RA.sum(0))
    out = np.empty((NB, 3))
    for t in range(NB):
        ix = np.concatenate([groups[j] for j in rng.integers(0, len(groups), len(groups))])
        out[t] = prim(CB[ix].sum(0), RB[ix].sum(0)) - prim(CA[ix].sum(0), RA[ix].sum(0))
    lo, hi = np.nanpercentile(out, [2.5, 97.5], 0)
    return full, lo, hi


NAMES = ['crack IoU', 'relF1@2', 'inactive IoU']
for tag, bg, bp in (('VERDICT (headline b)', hb['E-g'], hb['E-PF']), ('reported: b 0', 0.0, 0.0)):
    JA = json.load(open(D / f'E-g.b{bg:g}.json'))['cells']; JB = json.load(open(D / f'E-PF.b{bp:g}.json'))['cells']
    print(f'\n## {tag}: E-g b {bg} vs E-PF b {bp}')
    for split in ('test', 'test_noscuff'):
        rows = {}
        for sn, keep in (('all 50', lambda s: True), ('clean 49', lambda s: s != NOISY)):
            st = sorted(s for s in JA[split] if keep(s)); assert sorted(JB[split]) == sorted(JA[split])
            full, lo, hi = boot(arrays(JA[split], st), arrays(JB[split], st), [np.array([i]) for i in range(len(st))])
            rows[sn] = (full, lo, hi)
            print(f'  {split:12s} {sn:8s} ' + ' | '.join(f'{n} {full[i]:+.4f} [{lo[i]:+.4f}, {hi[i]:+.4f}]' for i, n in enumerate(NAMES)))
        fail = any(rows[s][2][i] < 0 for s in rows for i in range(3))
        pas = [NAMES[i] for i in range(3) if all(rows[s][1][i] > 0 for s in rows) or
               (any(rows[s][1][i] > 0 for s in rows) and all(rows[s][0][i] > 0 for s in rows))]
        near = [f'{s} {NAMES[i]}' for s in rows for i in range(3) if min(abs(rows[s][1][i]), abs(rows[s][2][i])) < 0.002]
        print(f'  => {split} {tag}: ' + ('FAIL' if fail else f'PASS ({", ".join(pas)})' if pas else 'n.d.') + (f'  [bound within 0.002 of 0: {near}]' if near else ''))
    st = sorted(JA['ext']); assert len(st) == 106 and sorted(JB['ext']) == st
    key = lambda s: re.sub(r'(_r\d+_c\d+|_cell\d+)$', '', s)
    cl = sorted({key(s) for s in st}); assert len(cl) == 71
    groups = [np.array([i for i, s in enumerate(st) if key(s) == c]) for c in cl]
    full, lo, hi = boot(arrays(JA['ext'], st), arrays(JB['ext'], st), groups)
    print(f'  E1 (106 cells, 71 clusters) ' + ' | '.join(f'{n} {full[i]:+.4f} [{lo[i]:+.4f}, {hi[i]:+.4f}]' for i, n in enumerate(NAMES)))
    e1 = [1, 2]  # co-primaries: relF1@2, inactive IoU
    w = 'FAIL' if any(hi[i] < 0 for i in e1) else ('PASS (' + ', '.join(NAMES[i] for i in e1 if lo[i] > 0) + ')' if any(lo[i] > 0 for i in e1) else 'n.d.')
    nearE = [NAMES[i] for i in e1 if min(abs(lo[i]), abs(hi[i])) < 0.002]
    print(f'  => E1 {tag}: {w}' + ('' if tag.startswith('VERDICT') else '  (reported only)') + (f'  [bound within 0.002 of 0: {nearE}]' if nearE else ''))
