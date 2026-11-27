"""marker1 calibration scorer (prereg ideas/b2_agent_marking_prereg.md §5-§6). Pure python + PIL.
Usage: python3 m1_calib_score.py <calib_marks_marker1.tsv> <boxdir> <outfile>
Run ONLY after the marks file md5 is in the log. Opens E-SCDD _rf masks (crack 14, scuff 25)."""
import sys, os, glob, random
from PIL import Image

R = os.environ.get('M1_MASK_ROOT', os.path.expanduser('~/mtp/datasets/escdd_full'))  # env override for the synthetic unit test only
MARKS = ('scuff', 'crack', 'both', 'neither', 'unsure')

def counts(stem, box):
    p = glob.glob(R + '/el_masks_*/' + stem + '_rf.png')
    assert len(p) == 1, (stem, p)
    m = Image.open(p[0]); assert m.mode in ('L', 'P'), m.mode
    w, h = m.size; d = list(m.getdata())
    x0, y0, x1, y1 = box
    out = {}
    for reg in ('box', 'whole'):
        c14 = c25 = 0
        for y in range(h):
            if reg == 'box' and not (y0 <= y <= y1): continue
            row = d[y*w:(y+1)*w]
            if reg == 'box': row = row[x0:x1+1]
            c14 += row.count(14); c25 += row.count(25)
        out[reg] = (c14, c25)
    return out

def kappa(pairs):
    n = len(pairs); a = sum(1 for r, l in pairs if r and l); b = sum(1 for r, l in pairs if r and not l)
    c = sum(1 for r, l in pairs if not r and l); dd = n - a - b - c
    po = (a + dd) / n; pr = (a + b) / n; pl = (a + c) / n; pe = pr*pl + (1-pr)*(1-pl)
    k = (po - pe) / (1 - pe) if pe < 1 else float('nan')
    sens = a / (a + c) if a + c else float('nan'); spec = dd / (b + dd) if b + dd else float('nan')
    return k, sens, spec, (a, b, c, dd)

def boot(pairs, B=2000, seed=1):
    rnd = random.Random(seed); ks = []
    for _ in range(B):
        s = [pairs[rnd.randrange(len(pairs))] for _ in pairs]
        k = kappa(s)[0]
        ks.append(k if k == k else 0.0)  # degenerate resample (pe = 1): kappa undefined, count as 0
    ks.sort(); return ks[int(0.025*B)], ks[int(0.975*B) - 1]

def main(mf, boxdir, outf):
    rows = [l.rstrip('\n').split('\t') for l in open(mf) if l.strip()]
    if rows[0][0] == 'stem': rows = rows[1:]
    L = []
    for r in rows:
        st, mk = r[0], r[1]; assert mk in MARKS, r
        b = open(os.path.join(boxdir, st + '_box.txt')).read().split('\t')
        box = tuple(int(v) for v in b[1:5])
        L.append((st, mk, counts(st, box)))
    o = []; P = o.append
    P(f'n {len(L)}; marks file {mf}')
    P('stem\tmark\tbox_crack\tbox_scuff\twhole_crack\twhole_scuff')
    for st, mk, c in L: P(f"{st}\t{mk}\t{c['box'][0]}\t{c['box'][1]}\t{c['whole'][0]}\t{c['whole'][1]}")
    lab = {'crack': lambda c: c[0] >= 20, 'scuff': lambda c: c[1] >= 1, 'either': lambda c: c[0] >= 20 or c[1] >= 1}
    rat = {'crack': ('crack', 'both'), 'scuff': ('scuff', 'both'), 'either': ('crack', 'scuff', 'both')}
    res = {}
    for reg in ('box', 'whole'):
        for uns in ('neg', 'pos'):
            for ep in ('crack', 'scuff', 'either'):
                pairs = [((mk in rat[ep]) or (uns == 'pos' and mk == 'unsure'), lab[ep](c[reg])) for st, mk, c in L]
                k, se, sp, (a, b, cc, dd) = kappa(pairs); lo, hi = boot(pairs)
                res[(reg, uns, ep)] = (k, lo, hi, se, sp, a + cc, b + dd)
                P(f'{reg}\tunsure={uns}\t{ep}\tlabel+ {a+cc} / label- {b+dd}\tTP {a} FP {b} FN {cc} TN {dd}\tkappa {k:.3f} [{lo:.3f}, {hi:.3f}]\tsens {se:.3f}\tspec {sp:.3f}')
    for reg in ('box', 'whole'):
        P(f'5 x label table ({reg}; label class = crack>=20 / scuff>=1 / both / none):')
        cls = lambda c: ('both' if c[0] >= 20 and c[1] >= 1 else 'crack' if c[0] >= 20 else 'scuff' if c[1] >= 1 else 'none')
        for mk in MARKS:
            P('  ' + mk + '\t' + '\t'.join(f'{lc} {sum(1 for st, m, c in L if m == mk and cls(c[reg]) == lc)}' for lc in ('crack', 'scuff', 'both', 'none')))
    n_uns = sum(1 for st, mk, c in L if mk == 'unsure')
    k, lo, hi, se, sp, npos, nneg = res[('box', 'neg', 'either')]
    prim = 'box'
    if npos < 8 or nneg < 8:
        prim = 'whole'; k, lo, hi, se, sp, npos, nneg = res[('whole', 'neg', 'either')]
    conds = [k >= 0.40, lo > 0, se >= 0.60 and sp >= 0.60, n_uns <= 8]
    P(f'RULE primary region {prim} (either+, unsure=neg): kappa {k:.3f} >= 0.40 {conds[0]}; CI lo {lo:.3f} > 0 {conds[1]}; sens {se:.3f} spec {sp:.3f} >= 0.60 {conds[2]}; unsure {n_uns} <= 8 {conds[3]}')
    P('VERDICT ' + ('PASS' if all(conds) else 'FAIL'))
    open(outf, 'w').write('\n'.join(o) + '\n'); print('\n'.join(o))

if __name__ == '__main__':
    main(*sys.argv[1:4])
