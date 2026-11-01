"""FROZEN half-cut detector v1 (domain, 31 Oct 2026): apply rule R2b with fixed parameters to a features TSV written by
dom_halfcut_detector2.py (md5 afa6af10). half-cut iff max(F_x, F_y) < 0.14 AND max(S_x, S_y) >= 0.14
(F = autocorr peak at 240-272 px, S = peak at 140-190 px; NaN F -> treated as 1, i.e. not routed).
Parameters were chosen on the DEV split (train 478 + pool half modules 297-299) by dom_halfcut_rule2.py (md5 3f29a634).
Label-free: needs images only. Usage: python -I dom_halfcut_apply.py FEATURES.tsv OUT.tsv"""
import sys, csv, os, numpy as np
A, B = 0.14, 0.14
R = list(csv.DictReader(open(sys.argv[1]), delimiter='\t'))
def fv(r, k):
    try: return float(r[k])
    except ValueError: return float('nan')
with open(sys.argv[2], 'w') as o:
    o.write('group\tstem\thalfcut\tFmax\tSmax\n')
    for r in R:
        F = [fv(r, 'F_x'), fv(r, 'F_y')]; S = [fv(r, 'S_x'), fv(r, 'S_y')]
        Fm = 1.0 if not np.isfinite(F).all() else max(F)
        Sm = max([s for s in S if np.isfinite(s)], default=-1.0)
        o.write(f"{r['group']}\t{os.path.basename(r['img'])[:-4]}\t{int(Fm < A and Sm >= B)}\t{Fm:.4f}\t{Sm:.4f}\n")
