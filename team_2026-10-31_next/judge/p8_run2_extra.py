"""judge (1 Nov): own recompute of P8 run-2 secondary columns from percell_hists.npz (+ P* from the summary meta):
cell AUROC (max p(crack) vs cells with >= 20 GT crack px; ties averaged), crack-free FA px (argmax tp+fp on cells with 0 GT
crack), inactive AP (binned, as crack AP), recall at P* = max recall over descending-bin thresholds with precision >= P*.
Compared against found's p8_summary.json. Usage: python -I p8_run2_extra.py HISTS.npz SUMMARY.json"""
import json, sys, numpy as np
d = json.loads(str(np.load(sys.argv[1])['data'])); S = json.load(open(sys.argv[2]))
PS = S.get('meta', {}).get('p_star') or S.get('p_star')
def ap(pos, neg):
    pos = np.asarray(pos, float)[::-1]; neg = np.asarray(neg, float)[::-1]
    tp, fp = np.cumsum(pos), np.cumsum(neg); P = tp / np.maximum(tp + fp, 1); R = tp / max(pos.sum(), 1)
    return float(np.sum(P * np.diff(np.concatenate([[0], R]))))
def rec_at(pos, neg, ps):
    pos = np.asarray(pos, float)[::-1]; neg = np.asarray(neg, float)[::-1]
    tp, fp = np.cumsum(pos), np.cumsum(neg); P = tp / np.maximum(tp + fp, 1); R = tp / max(pos.sum(), 1)
    ok = P >= ps; return float(R[ok].max()) if ok.any() else 0.0
def auroc(p, n):
    p, n = np.array(p), np.array(n); return float(((p[:, None] > n[None]).sum() + 0.5 * (p[:, None] == n[None]).sum()) / (len(p) * len(n)))
worst = {}
for run, cells in d.items():
    for st in ('val', 'F51', 'H36', 'F19'):
        cs = [v for v in cells.values() if v['set'] == st]
        pos = np.sum([v['crack']['pos'] for v in cs], 0); neg = np.sum([v['crack']['neg'] for v in cs], 0)
        ip = np.sum([v['inactive']['pos'] for v in cs], 0); ineg = np.sum([v['inactive']['neg'] for v in cs], 0)
        mine = dict(crack_ap=ap(pos, neg), inactive_ap=ap(ip, ineg) if ip.sum() else None,
                    cell_auroc=auroc([v['max_pc'] for v in cs if v['n_gt_crack'] >= 20], [v['max_pc'] for v in cs if v['n_gt_crack'] < 20]),
                    fa_px_crackfree_argmax=int(sum(v['crack']['tp'] + v['crack']['fp'] for v in cs if v['n_gt_crack'] == 0)),
                    recall_at_pstar=rec_at(pos, neg, PS[st]) if PS and st in PS else None)
        ref = S['summary'][run][st]
        for k, v in mine.items():
            if v is None or ref.get(k) is None: continue
            worst[k] = max(worst.get(k, 0), abs(v - ref[k]))
        if st in ('val', 'F51', 'H36'):
            print(f"{run:24s} {st:4s} AP {mine['crack_ap']:.3f} inactAP {mine['inactive_ap'] if mine['inactive_ap'] is None else round(mine['inactive_ap'],3)} "
                  f"AUROC {mine['cell_auroc']:.3f} (ref {ref['cell_auroc']:.3f}) FA {mine['fa_px_crackfree_argmax']} (ref {ref['fa_px_crackfree_argmax']}) "
                  f"R@P* {mine['recall_at_pstar'] if mine['recall_at_pstar'] is None else round(mine['recall_at_pstar'],3)} (ref {round(ref['recall_at_pstar'],3)})")
print('P*:', PS); print('max |mine - found| per field:', {k: round(v, 6) for k, v in worst.items()})
