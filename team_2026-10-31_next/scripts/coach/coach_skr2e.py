"""coach (2 Nov): independent recompute of protocol_SKR2E v1's verdict from the per-cell JSONs (own metric and bootstrap code;
not Track M m1_analyze / runner's skr2e_boot). Point estimates must equal runner's exactly; CIs use my own resampling
(numpy default_rng(12345), cells or clusters with replacement), so they differ from runner's in the 3rd decimal: the verdict
must agree unless a bound sits within ~0.002 of 0 (then flagged).
- Val decisions re-derived for both arms (D2 rule + width flag on the stored sweep); union U checked.
- VERDICT at b 0 for both arms: test primaries (crack IoU, relF1@2, inactive IoU; all 50 / clean 49; paired image bootstrap;
  Track M pass / fail rule), E1 co-primaries (relF1@2, any-hit; 71-cluster bootstrap).
- Guards at b 0 and at the headline pair: G2a test relP@2 d (all 50) < -0.03; G2b E1 crack px on the 74 crack-free cells >
  1.5 x E-PF's; G1t test inactive d <= -0.015 in both sets; G1e E1 inactive cluster CI hi < 0.
Usage: python coach_skr2e.py run OUT_DIR | python coach_skr2e.py selftest PF2E_OUT_DIR"""
import json, re, sys
import numpy as np
from pathlib import Path

NC, CR, IN, NOISY, NB = 24, 14, 11, 'CSIR_00070_r8_c4', 2000
GRID = [round(0.25 * i, 2) for i in range(13)]
NAMES = ['crack IoU', 'relF1@2', 'inactive IoU', 'any-hit', 'relP@2']
key = lambda s: re.sub(r'(_r\d+_c\d+|_cell\d+)$', '', s)


def feats(cells, stems):
    C = np.stack([np.asarray(cells[s]['conf'], np.int64).reshape(NC, NC) for s in stems])
    R = np.stack([np.asarray(cells[s]['crack_rel2'], np.int64) for s in stems])
    H = np.array([[sum(1 for c in cells[s]['crack_cc']['gt'] if c[0] >= 20 and c[1] >= 1),
                   sum(1 for c in cells[s]['crack_cc']['gt'] if c[0] >= 20)] for s in stems], np.int64)
    return C, R, H


def metr(C, R, H):
    tp = np.diag(C); g = C.sum(1); p = C.sum(0)
    io = lambda k: tp[k] / (g[k] + p[k] - tp[k]) if (g[k] + p[k] - tp[k]) > 0 else np.nan
    rp, rr = R[0] / max(R[1], 1), R[2] / max(R[3], 1)
    return np.array([io(CR), 2 * rp * rr / max(rp + rr, 1e-9), io(IN), H[0] / max(H[1], 1), rp])


def boot(A, B, groups, rng):
    full = metr(*(x.sum(0) for x in B)) - metr(*(x.sum(0) for x in A))
    out = np.empty((NB, len(NAMES)))
    for t in range(NB):
        ix = np.concatenate([groups[j] for j in rng.integers(0, len(groups), len(groups))])
        out[t] = metr(*(x[ix].sum(0) for x in B)) - metr(*(x[ix].sum(0) for x in A))
    lo, hi = np.nanpercentile(out, [2.5, 97.5], 0)
    return full, lo, hi


def cfree_px(cells):
    n = px = 0
    for c in cells.values():
        M = np.asarray(c['conf'], np.int64).reshape(NC, NC)
        if M[CR].sum() == 0:
            n += 1; px += int(M[:, CR].sum())
    return n, px


def contrast(JA, JB, rng, tag, out):
    pr = out.append; res = {}
    rows = {}
    for sn, kp in (('all 50', lambda s: True), ('clean 49', lambda s: s != NOISY)):
        st = sorted(s for s in JA['test'] if kp(s)); assert sorted(JB['test']) == sorted(JA['test'])
        full, lo, hi = boot(feats(JA['test'], st), feats(JB['test'], st), [np.array([i]) for i in range(len(st))], rng)
        rows[sn] = (full, lo, hi)
        pr(f'  test {sn:8s} ' + ' | '.join(f'{NAMES[i]} {full[i]:+.4f} [{lo[i]:+.4f}, {hi[i]:+.4f}]' for i in (0, 1, 2)) + f' | relP@2 {full[4]:+.4f}')
    fail = any(rows[s][2][i] < 0 for s in rows for i in (0, 1, 2))
    pas = [NAMES[i] for i in (0, 1, 2) if all(rows[s][1][i] > 0 for s in rows) or
           (any(rows[s][1][i] > 0 for s in rows) and all(rows[s][0][i] > 0 for s in rows))]
    near = [f'{s} {NAMES[i]}' for s in rows for i in (0, 1, 2) if min(abs(rows[s][1][i]), abs(rows[s][2][i])) < 0.002]
    tv = 'FAIL' if fail else (f'PASS ({", ".join(pas)})' if pas else 'n.d.')
    pr(f'  => test {tag}: {tv}' + (f'  [bound within 0.002 of 0: {near}]' if near else ''))
    st = sorted(JA['ext']); assert len(st) == 106 and sorted(JB['ext']) == st
    cl = sorted({key(s) for s in st}); assert len(cl) == 71
    groups = [np.array([i for i, s in enumerate(st) if key(s) == c]) for c in cl]
    FA, FB = feats(JA['ext'], st), feats(JB['ext'], st); assert FA[2][:, 1].sum() == 296 == FB[2][:, 1].sum()
    full, lo, hi = boot(FA, FB, groups, rng)
    pr(f'  E1 (106, 71 clusters) ' + ' | '.join(f'{NAMES[i]} {full[i]:+.4f} [{lo[i]:+.4f}, {hi[i]:+.4f}]' for i in (1, 3, 2))
       + f' | any-hit E-PF {FA[2][:, 0].sum()}/296 E-SKR2 {FB[2][:, 0].sum()}/296')
    e1 = [1, 3]
    ev = 'FAIL' if any(hi[i] < 0 for i in e1) else ('PASS (' + ', '.join(NAMES[i] for i in e1 if lo[i] > 0) + ')' if any(lo[i] > 0 for i in e1) else 'n.d.')
    nearE = [NAMES[i] for i in e1 + [2] if min(abs(lo[i]), abs(hi[i])) < 0.002]
    pr(f'  => E1 {tag}: {ev}' + (f'  [bound within 0.002 of 0: {nearE}]' if nearE else ''))
    na, pa = cfree_px(JA['ext']); nb, pb = cfree_px(JB['ext']); assert na == nb == 74
    G = {'G2a': rows['all 50'][0][4] < -0.03, 'G2b': pb > 1.5 * pa,
         'G1t': rows['all 50'][0][2] <= -0.015 and rows['clean 49'][0][2] <= -0.015, 'G1e': hi[2] < 0}
    pr(f'  guards {tag}: G2a relP@2 {rows["all 50"][0][4]:+.4f} {"TRIP" if G["G2a"] else "ok"} | G2b E1 crack-free px {pb} vs {pa} '
       f'(x{pb / max(pa, 1):.2f}) {"TRIP" if G["G2b"] else "ok"} | G1t inactive {rows["all 50"][0][2]:+.4f} / {rows["clean 49"][0][2]:+.4f} '
       f'{"TRIP" if G["G1t"] else "ok"} | G1e E1 inactive {full[2]:+.4f} [{lo[2]:+.4f}, {hi[2]:+.4f}] {"TRIP" if G["G1e"] else "ok"}')
    return {'test': tv, 'test_pass': pas, 'test_fail': fail, 'e1': ev, 'guards': G}


def d2(sw):
    ok = [b for b in GRID if sw[b]['relR2'] >= 0.90]
    bias = ok[0] if ok and sw[ok[0]]['relP2'] >= 0.90 else max(GRID, key=lambda b: sw[b]['relF1'])
    width = sw[0.0]['crack_P'] - sw[bias]['crack_P']
    return bias, width, (0.0 if width > 0.05 else bias)


def run(D, arms=('E-PF', 'E-SKR2'), decf='skr2e_val_decisions.json'):
    D = Path(D); dec = json.load(open(D / decf)); out = []; pr = out.append; hb = {}
    pr('## val decisions (D2 + width flag re-applied to the stored sweep)')
    for k in arms:
        sw = {float(b): v for b, v in dec[k]['sweep'].items()}; bias, width, head = d2(sw)
        assert bias == dec[k]['bias'] and head == dec[k]['headline_bias'], (k, bias, head, dec[k])
        hb[k] = head; pr(f'  {k}: D2 b {bias}, val crack P drop {width:+.4f}, headline b {head}: = decisions file')
    U = sorted({0.0} | {dec[k]['bias'] for k in arms})
    if 'union_b' in dec:
        assert dec['union_b'] == U, (dec['union_b'], U)
    J = {(k, b): json.load(open(D / f'{k}.b{b:g}.json'))['cells'] for k in arms for b in U if (D / f'{k}.b{b:g}.json').exists()}
    rng = np.random.default_rng(12345)
    pr('\n## VERDICT pair: both arms at b 0'); V = contrast(J[(arms[0], 0.0)], J[(arms[1], 0.0)], rng, 'b 0 (verdict)', out)
    hp = (hb[arms[0]], hb[arms[1]]); H = None
    if hp != (0.0, 0.0):
        pr(f'\n## headline pair: {arms[0]} b {hp[0]} vs {arms[1]} b {hp[1]} (guards apply; primaries reported)')
        H = contrast(J[(arms[0], hp[0])], J[(arms[1], hp[1])], rng, 'headline pair (reported; guards apply)', out)
    trips = [f'{g} at b 0' for g, t in V['guards'].items() if t] + ([f'{g} at headline pair' for g, t in H['guards'].items() if t] if H else [])
    carry = [f'test {n}' for n in V['test_pass']] + ([V['e1'][6:-1]] if V['e1'].startswith('PASS') else [])
    pfail = V['test_fail'] or V['e1'] == 'FAIL'
    verdict = 'FAIL' if (pfail or trips) else ('PASS' if carry else 'n.d.')
    pr(f'\n## SKR2E VERDICT (coach recompute): {verdict}' + (f' carried by {carry}' if verdict == 'PASS' else '')
       + (f'; guard trips {trips}' if trips else '') + (f'; primary fails' if pfail else ''))
    return out, verdict


def selftest(pf2e):
    """PF2E's files as a 2-arm input (E-g as arm 0, E-PF as arm 1; no union_b): point estimates at b 0 = verify_pf2e (b 0 was
    PF2E's verdict b); identical arms -> all CIs [0, 0], no trip."""
    D = Path(pf2e); A = json.load(open(D / 'E-g.b0.json'))['cells']; B = json.load(open(D / 'E-PF.b0.json'))['cells']
    out = []; r = contrast(A, B, np.random.default_rng(12345), 'selftest E-PF - E-g b 0', out)
    print('\n'.join(out))
    exp = {'test all crack IoU': +0.0027, 'test all relF1@2': +0.0121, 'test all inactive': +0.0237, 'E1 relF1@2': +0.0355, 'E1 inactive': +0.2141}
    got = {}
    for l in out:
        if l.startswith('  test all 50'):
            v = [float(x.split()[-3]) for x in l.split('|')[:3]]; got.update({'test all crack IoU': v[0], 'test all relF1@2': v[1], 'test all inactive': v[2]})
        if l.startswith('  E1 (106'):
            parts = l.split('|'); got['E1 relF1@2'] = float(parts[0].split('relF1@2')[1].split()[0]); got['E1 inactive'] = float(parts[2].split('inactive IoU')[1].split()[0])
    ok1 = all(abs(got[k] - v) < 0.00015 for k, v in exp.items())
    out2 = []; r2 = contrast(B, B, np.random.default_rng(1), 'selftest identical', out2)
    ok2 = all('[+0.0000, +0.0000]' in seg or '[-0.0000, +0.0000]' in seg or 'relP@2' in seg or 'any-hit E-PF' in seg or 'test' not in seg and 'E1' not in seg
              for l in out2 if l.startswith(('  test', '  E1')) for seg in l.split('|')) and not any(r2['guards'].values()) and r2['test'] == 'n.d.' and r2['e1'] == 'n.d.'
    print(f'selftest point estimates vs verify_pf2e: {got} -> {ok1}; identical arms CIs [0, 0], no trip, n.d.: {ok2}')
    print('SELFTEST', 'PASS' if ok1 and ok2 else 'FAIL'); return ok1 and ok2


if __name__ == '__main__':
    if sys.argv[1] == 'selftest':
        sys.exit(0 if selftest(sys.argv[2]) else 1)
    out, v = run(sys.argv[2]); print('\n'.join(out))
