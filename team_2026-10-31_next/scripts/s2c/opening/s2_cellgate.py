"""SKR2 + HC2 opening, pass 10b: the "SKR + cell gate" line (protocol_SKR2_HC2 v1.0.1 §9 amendment; REPORTED ONLY, no verdict role).
DRAFT (runner's helper, 2 Nov 2026) for coach's FREEZE. CPU only; reads the opening's wide-grid B5 records (el_metrics_w, val / test / ext)
of SUPPF s5-9 (remade from PF2's dumps), SKR2 s5-9 and HC2 s5-9. Val chooses the gate; test and ext are read only inside the opening.
Rule = arch's (scripts/arch/a6_gate.py 7f789a47, written before any number): arrs() and metrics_at() below are copied VERBATIM from it,
and the gate lines (t, keep) are its one_run() lines; its fixed paths, its val / rf arm list and its b_rel readouts are not used.
  g(cell)  = record s['1'] = the largest crack margin (log p_crack - max_other log p) over the cell's keep px (el_metrics cell_record:
             srt = sort(mk[keep]) descending, s[str(M)] = srt[M - 1]); b-independent; crack is predicted at b 0 iff margin > 0.
  t        = per run, min of g over that run's VAL cells with n_gt >= 20 (n_gt = GT crack px in keep), minus 1e-3.
  gate     = a cell with g < t keeps NONE of its predicted crack px at every b (pred, tp, relp_tp, relr_tp -> 0); GT counts unchanged.
Readouts at b 0 (grid index of b = 0.0 in the record's own 'grid'), gated vs ungated, per run and seed means:
  E1 crack px on E1's crack-free cells (ext cells with n_gt == 0; metrics_at fa_px = sum of record 'pred' at b 0 over them);
  E1 any-hit component recall = share of GT crack components >= 20 px (record gt_cc entries [size, v50, vany], el_metrics: 'any-hit iff
    b > -vany') with vany + 0 > 0; a component in a gated cell counts as not hit;
  test crack relP@2 (all 50; metrics_at relP = sum relp_tp / sum pred at b 0).
  Also: t, gated cell counts per set (crack-free / crack-positive >= 20 px / ambiguous 1-19), and next to G2 (context only): the arm /
  SUPPF ratio of the E1 crack-free px seed means and the test relP@2 seed-mean delta, ungated and gated.
Records are used only if their self-check file ends 'SELFCHECK PASS' (written by el_metrics_w records --m0).
Usage: python s2_cellgate.py --arm SUPPF REC_DIR RUN x5 --arm SKR01 REC_DIR RUN x5 --arm HC2 REC_DIR RUN x5 --base SUPPF --json OUT.json
"""
import argparse, hashlib, json, sys
from pathlib import Path
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument('--arm', nargs='+', action='append', required=True, metavar='NAME REC RUN')
ap.add_argument('--base', default='SUPPF'); ap.add_argument('--json'); ap.add_argument('--score-key', default='1')
a = ap.parse_args()
CMIN = 20


# ---- copied verbatim from scripts/arch/a6_gate.py (7f789a47) ----
def arrs(cells, stems, keepmask=None):
    """sum arrays over stems; keepmask[stem] False -> crack pred zeroed."""
    pred = tp = rp = rr = 0
    ngt = 0
    for s in stems:
        c = cells[s]
        ngt += c["n_gt"]
        if keepmask is not None and not keepmask[s]:
            continue
        pred = pred + np.array(c["pred"], dtype=np.int64)
        tp = tp + np.array(c["tp"], dtype=np.int64)
        rp = rp + np.array(c["relp_tp"], dtype=np.int64)
        rr = rr + np.array(c["relr_tp"], dtype=np.int64)
    return pred, tp, rp, rr, ngt

def metrics_at(cells, stems, i, keep=None):
    n = len(next(iter(cells.values()))["pred"])
    z = np.zeros(n, dtype=np.int64)
    pred, tp, rp, rr, ngt = arrs(cells, stems, keep)
    pred = pred if isinstance(pred, np.ndarray) else z
    tp = tp if isinstance(tp, np.ndarray) else z
    rp = rp if isinstance(rp, np.ndarray) else z
    rr = rr if isinstance(rr, np.ndarray) else z
    relP = rp[i] / pred[i] if pred[i] else float("nan")
    relR = rr[i] / ngt if ngt else float("nan")
    relF = 2 * relP * relR / (relP + relR) if (relP == relP and relR == relR and relP + relR) else float("nan")
    iou = tp[i] / (pred[i] + ngt - tp[i]) if (pred[i] + ngt - tp[i]) else float("nan")
    fa = 0; fa_cells = 0; off_neg = 0; off_pos = 0
    for s in stems:
        c = cells[s]
        if keep is not None and not keep[s]:
            continue
        pr = c["pred"][i]
        if c["n_gt"] == 0:
            fa += pr; fa_cells += int(pr >= 20); off_neg += pr - c["relp_tp"][i]
        else:
            off_pos += pr - c["relp_tp"][i]
    return dict(relR=relR, relP=relP, relF=relF, iou=iou, fa_px=fa, fa_cells=fa_cells,
                pred_gt=(pred[i] / ngt if ngt else float("nan")), off_neg=off_neg, off_pos=off_pos)
# ---- end of the verbatim copy ----


def anyhit_b(cells, stems, g, i, keep=None):  # gt_cc [size, v50, vany]: hit at b iff vany + b > 0; gated cell -> no hit
    b = float(g[i]); comps = [(s, x) for s in stems for x in cells[s]['gt_cc'] if x[0] >= CMIN]
    hit = sum(1 for s, x in comps if (keep is None or keep[s]) and x[2] + b > 0)
    return (hit / len(comps) if comps else float('nan')), len(comps)


def sc_pass(p):
    q = Path(str(p) + '.selfcheck.txt')
    return q.exists() and q.read_text().strip().splitlines()[-1] == 'SELFCHECK PASS'


def one_run(d, run, score_key):
    R = {}
    for sp in ('val', 'test', 'ext'):
        p = d / f'{run}.{sp}.json'; assert sc_pass(p), (str(p), 'self-check not PASS')
        R[sp] = json.load(open(p)); assert R[sp]['set'] == sp, (str(p), R[sp]['set'])
    g = np.array(R['val']['grid'], dtype=float)
    assert all(list(map(float, R[sp]['grid'])) == list(g) for sp in R), (run, 'grids differ between sets')
    i0 = int(np.argmin(np.abs(g - 0.0))); assert abs(g[i0]) < 1e-9, (run, 'no b = 0 on the grid')
    cv = R['val']['cells']; vst = sorted(cv)
    assert len(vst) == 54 and len(R['test']['cells']) == 50 and len(R['ext']['cells']) == 106, run
    pos = [s for s in vst if cv[s]["n_gt"] >= 20]                       # a6_gate one_run()
    t = min(cv[s]["s"][score_key] for s in pos) - 1e-3                   # a6_gate one_run()
    out = {'run': run, 't': float(t), 'n_val_pos': len(pos), 'b0': float(g[i0])}
    for sp in ('test', 'ext'):
        cells = R[sp]['cells']; stems = sorted(cells)
        keep = {s: cells[s]["s"][score_key] >= t for s in stems}         # a6_gate one_run()
        cnt = lambda f: (sum(1 for s in stems if f(cells[s]['n_gt'])), sum(1 for s in stems if f(cells[s]['n_gt']) and not keep[s]))
        out[sp] = {'ungated': metrics_at(cells, stems, i0), 'gated': metrics_at(cells, stems, i0, keep),
                   'anyhit_ungated': anyhit_b(cells, stems, g, i0), 'anyhit_gated': anyhit_b(cells, stems, g, i0, keep),
                   'cells_crackfree_total_gated': cnt(lambda n: n == 0), 'cells_pos20_total_gated': cnt(lambda n: n >= 20),
                   'cells_ambiguous_total_gated': cnt(lambda n: 0 < n < 20)}
    return out


arms = {x[0]: (Path(x[1]), x[2:]) for x in a.arm}
assert a.base in arms and all(len(v[1]) == 5 for v in arms.values()), 'need 5 runs per arm'
V = {n: [one_run(d, r, a.score_key) for r in runs] for n, (d, runs) in arms.items()}
mean = lambda xs: float(np.nanmean(np.array(xs, float)))
S = {}
for n, rows in V.items():
    S[n] = {f'{lab}_{gt}': mean([f(r, gt) for r in rows]) for gt in ('ungated', 'gated')
            for lab, f in (('e1_crackfree_px', lambda r, gt: r['ext'][gt]['fa_px']), ('e1_anyhit', lambda r, gt: r['ext'][f'anyhit_{gt}'][0]),
                           ('test_relP2', lambda r, gt: r['test'][gt]['relP']))}
out = {'label': 'protocol_SKR2_HC2 §9 v1.0.1 "SKR + cell gate" line (REPORTED ONLY; arch a6_gate rule 7f789a47); b 0; B5 wide records', 'warning': 'REPORTED ONLY, UNSTABLE THRESHOLD (val-chosen t swings ~16 margin units across seeds; arch withdrew A6 §7)',
       'score_key': a.score_key, 'per_run': V, 'seed_means': S, 'vs_base': {},
       'md5': {'this_file': hashlib.md5(open(__file__, 'rb').read()).hexdigest()}}
L = [f'## REPORTED ONLY, UNSTABLE THRESHOLD (val-chosen t swings ~16 margin units across seeds; arch withdrew A6 §7)', f'## SKR + cell gate (protocol §9 v1.0.1; REPORTED ONLY, no verdict role): gate g = s[{a.score_key}], t = min over val cells with n_gt >= 20 '
     'minus 1e-3; gated cells lose all crack px; b 0; seed means (per-run values in the JSON)',
     'arm | E1 crack px on crack-free cells ungated -> gated | E1 any-hit ungated -> gated | test relP@2 ungated -> gated | '
     'E1 crack-free cells gated / total | E1 positive cells gated | test cells gated (crack-free / positive) | t per run']
for n, rows in V.items():
    e, tt = rows[0]['ext'], rows[0]['test']
    L.append(f"{n:6s} | {S[n]['e1_crackfree_px_ungated']:.0f} -> {S[n]['e1_crackfree_px_gated']:.0f} | {S[n]['e1_anyhit_ungated']:.4f} -> "
             f"{S[n]['e1_anyhit_gated']:.4f} | {S[n]['test_relP2_ungated']:.4f} -> {S[n]['test_relP2_gated']:.4f} | "
             f"{mean([r['ext']['cells_crackfree_total_gated'][1] for r in rows]):.1f} / {e['cells_crackfree_total_gated'][0]} | "
             f"{mean([r['ext']['cells_pos20_total_gated'][1] for r in rows]):.1f} / {e['cells_pos20_total_gated'][0]} | "
             f"{mean([r['test']['cells_crackfree_total_gated'][1] for r in rows]):.1f} / {mean([r['test']['cells_pos20_total_gated'][1] for r in rows]):.1f} "
             f"(of {tt['cells_crackfree_total_gated'][0]} / {tt['cells_pos20_total_gated'][0]}) | " + ' '.join(f"{r['t']:.2f}" for r in rows))
L.append(f'\n## next to G2 (context only; G2 itself is computed from m0 at argmax in the guards pass): arm vs {a.base}, ungated / gated')
for n in V:
    if n == a.base:
        continue
    vb = {gt: {'e1_crackfree_ratio': S[n][f'e1_crackfree_px_{gt}'] / max(S[a.base][f'e1_crackfree_px_{gt}'], 1e-9),
               'test_relP2_delta': S[n][f'test_relP2_{gt}'] - S[a.base][f'test_relP2_{gt}'],
               'e1_anyhit_delta': S[n][f'e1_anyhit_{gt}'] - S[a.base][f'e1_anyhit_{gt}']} for gt in ('ungated', 'gated')}
    out['vs_base'][n] = vb
    L.append(f"{n} vs {a.base}: E1 crack-free px x{vb['ungated']['e1_crackfree_ratio']:.2f} -> x{vb['gated']['e1_crackfree_ratio']:.2f} | "
             f"test relP@2 d {vb['ungated']['test_relP2_delta']:+.4f} -> {vb['gated']['test_relP2_delta']:+.4f} | "
             f"E1 any-hit d {vb['ungated']['e1_anyhit_delta']:+.4f} -> {vb['gated']['e1_anyhit_delta']:+.4f}")
print('\n'.join(L))
if a.json:
    json.dump(out, open(a.json, 'w'), indent=1, default=float)
