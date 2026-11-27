"""RCS pre-check (CPU): DAFormer rare class sampling on P532 (legacy train+val, masks_escdd px counts).
Prints P(c), expected per-draw share of each cell, per-class pixel share in the resampled stream vs uniform."""
import sys, numpy as np
B = sys.argv[1]
px = np.load(f'{B}/out/legacy_classpx.npy').astype(np.float64)  # (582, 24)
rows = [l.rstrip('\n').split('\t') for l in open(f'{B}/out/legacy_stems.txt')]
keep = np.array([r[1] in ('train', 'val') for r in rows])
px = px[keep]; N = px.shape[0]
names = ['bckgnd','sp_multi','sp_mono','sp_dogbone','ribbons','border','text','padding','clamp','busbars','crack_rbn_edge',
         'inactive','rings','material','crack','gridline','splice','dead_cell','corrosion_rbn','belt_mark','edge_dark',
         'frame_edge','jbox','meas_artifact']
MINPX = int(sys.argv[2]) if len(sys.argv) > 2 else 1
has = px >= MINPX
ncell = has.sum(0)
f = px.sum(0) / px.sum()
def run(T, classes, cap):
    cl = np.array(classes)
    if np.isinf(T): logits = np.zeros(len(cl))
    else: logits = (1 - f[cl]) / T
    P = np.exp(logits - logits.max()); P /= P.sum()
    w = np.zeros(N)
    for p, c in zip(P, cl):
        w[has[:, c]] += p / has[:, c].sum()
    if cap:
        for _ in range(50):
            w = np.minimum(w, cap / N); w /= w.sum()
    share = (w[:, None] * px).sum(0) / (w[:, None] * px).sum()
    ushare = px.sum(0) / px.sum()
    return P, w, share, ushare
print(f'N={N} cells; minpx={MINPX}')
print('class  cells  f_c')
for c in range(24): print(f'{c:2d} {names[c]:15s} {ncell[c]:4d} {f[c]:.5f}')
R13 = [0,1,2,4,5,7,11,13,14,15,16,20,21]
ge10 = [c for c in range(24) if ncell[c] >= 10]
for label, classes in (('all24', list(range(24))), ('cells>=10', ge10), ('R13', R13)):
    for T in (0.01, 0.1, np.inf):
        for cap in (None, 10):
            P, w, share, ushare = run(T, classes, cap)
            m = w * N
            top = np.argsort(-m)[:3]
            print(f'\n[{label} T={T} cap={cap}] max cell mult {m.max():.1f} (top3 {np.round(m[top],1)}), cells never drawn {int((m<1e-6).sum())}, '
                  f'median mult {np.median(m):.2f}, eff. n (1/sum w^2) {1/np.sum(w**2):.0f}')
            print('   px share x vs uniform: ' + ', '.join(f'{names[c]} {share[c]/ushare[c]:.2f}' for c in (0,7,11,14,15,16,20,13,9,21)))

print('\n== draw shares: crack-free cells, inactive cells, per source ==')
src = np.array([r[0].split('_')[0] for r, k in zip(rows, keep) if k])
for label, classes, T in (('R13', R13, 0.01), ('R13', R13, 0.1), ('R13-crack', [c for c in R13 if c != 14], 0.01), ('cells>=10', ge10, 0.01)):
    P, w, share, ushare = run(T, classes, None)
    cf = px[:, 14] == 0; ina = px[:, 11] > 0
    s = f'[{label} T={T}] crack-free cells {w[cf].sum():.3f} (uniform {cf.mean():.3f}); inactive cells {w[ina].sum():.3f} (uniform {ina.mean():.3f}); '
    s += 'sources ' + ', '.join(f'{k} {w[src==k].sum():.3f}/{(src==k).mean():.3f}' for k in ('ARTS','BMRK','CFVS','CSIR','SDLE'))
    s += f'; px share x: inactive {share[11]/ushare[11]:.2f} crack {share[14]/ushare[14]:.2f} splice {share[16]/ushare[16]:.2f} edge_dark {share[20]/ushare[20]:.2f} gridline {share[15]/ushare[15]:.2f}'
    print(s)
    print('   P(c): ' + ', '.join(f'{names[c]} {p:.3f}' for p, c in zip(P, classes) if p > 0.005))
