"""evalx Q2: how much of the crack IoU gap is width / edge convention rather than missed cracks.
Part A (from scored outputs): split crack errors into near (within 2 px) and far, per run.
Part B (GT-only simulation on the 50 test masks from escdd_full; crack id 14): IoU and relF1@2 of a PERFECT
localiser that draws a different width or is offset by 1 px. The 236 test crack px P6 restored from old masks
(doc 17 5.3) are not in escdd_full; 0.26% of test crack px, ignored here."""
import json, glob
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from skimage.morphology import skeletonize

TM = '/home/yugma/mtp/research/team_2026-10-24_go/trackM/'
NC, CR = 24, 14
NOISY = 'CSIR_00070_r8_c4'


def dec(c):
    C = np.array(c['conf']).reshape(NC, NC)
    p2, pr, r2, g = c['crack_rel2']
    return np.array([C[CR, CR], p2, pr, r2, g], float)


def report(name, cellsets):
    """cellsets: list of dict cell -> dec; mean over runs"""
    out = []
    for R in cellsets:
        tp, p2, pr, r2, g = sum(R[c] for c in R if c != NOISY)
        fn_near, fn_far, fp_near, fp_far = r2 - tp, g - r2, p2 - tp, pr - p2
        U = tp + fn_near + fn_far + fp_near + fp_far
        iou = tp / U
        iou_tol = (tp + fn_near) / (tp + fn_near + fn_far + fp_far)   # near errors forgiven
        relR, relP = r2 / g, p2 / pr
        out.append([iou, fn_near / U, fn_far / U, fp_near / U, fp_far / U, iou_tol, relR, relP, 2 * relR * relP / (relR + relP), tp / g, tp / pr])
    o = np.mean(out, 0)
    print(f'{name}: IoU {o[0]:.3f} | share of union: FN near {o[1]:.3f}, FN far {o[2]:.3f}, FP near {o[3]:.3f}, FP far {o[4]:.3f} '
          f'| IoU with near errors forgiven {o[5]:.3f} | relR@2 {o[6]:.3f} relP@2 {o[7]:.3f} relF1@2 {o[8]:.3f} | R {o[9]:.3f} P {o[10]:.3f}')


print('# A. Crack error decomposition, test without the noisy cell (49 cells)')
ld = lambda f, k=None: {s: dec(v) for s, v in (json.load(open(f))['cells']['test'] if k is None else json.load(open(f))['test'][k]).items()}
A100 = [ld(f) for f in sorted(glob.glob(TM + 'm0/p6_L3_100pct_s*.json')) + sorted(glob.glob(TM + 'm0/p16_A_100pct_s*.json'))]
SX = [ld(f) for f in sorted(glob.glob(TM + 'm0/p16_Sx_100pct_s*.json'))]
report('A100 single (5 seeds)', A100)
report('Sx100 (5 seeds)', SX)
report('FINAL ensemble b0.75', [ld(TM + 'final/final_cells.json', 'final_b0.75')])
report('FINAL ensemble b0', [ld(TM + 'final/final_cells.json', 'final_b0')])
# low-label arms from E1 raw_v2 (counts only)
R = '/home/yugma/mtp/research/results/e1/raw_v2/'


def ldr(f):
    c = json.load(open(f))['cells']['test']
    return {s: np.array([v['crack_tp'], v.get('crack_p2_hit', 0), v['crack_pred'], v.get('crack_r2_hit', 0), v['crack_gt']], float) for s, v in c.items()}


for name, pats in [('A5c', ['p12_A_5pct', 'p13_A_5pct']), ('BsM5', ['p13_BsM_5pct']), ('L3 10%', ['p6_L3_10pct']), ('A50', ['p16_A_50pct'])]:
    report(name, [ldr(f) for p in pats for f in sorted(glob.glob(R + p + '_s*.json'))])

print('\n# B. Perfect localiser, different convention (GT-only; 50 test cells, all; pooled)')
E = '/home/yugma/mtp/datasets/escdd_full/'
stems = [l.strip() for l in open('/home/yugma/mtp/datasets/splits_benchmark/test.txt') if l.strip()]
G = []
for s in stems:
    for sp in ['train', 'val', 'test']:
        f = f'{E}el_masks_{sp}/{s}.png'
        try:
            G.append(np.array(Image.open(f)) == CR); break
        except FileNotFoundError:
            pass
assert len(G) == 50
disk = lambda r: (np.add.outer(np.arange(-r, r + 1)**2, np.arange(-r, r + 1)**2) <= r * r)


def score(P, G):
    tp = sum((p & g).sum() for p, g in zip(P, G)); pr = sum(p.sum() for p in P); g_ = sum(g.sum() for g in G)
    p2 = r2 = 0
    for p, g in zip(P, G):
        if g.any() and p.any():
            dg = ndi.distance_transform_edt(~g); dp = ndi.distance_transform_edt(~p)
            p2 += (dg[p] <= 2).sum(); r2 += (dp[g] <= 2).sum()
    rp, rr = p2 / max(pr, 1), r2 / max(g_, 1)
    return tp / (g_ + pr - tp), 2 * rp * rr / max(rp + rr, 1e-9), tp / g_, tp / max(pr, 1)


SK = [skeletonize(g) for g in G]
w = sum(g.sum() for g in G) / sum(s.sum() for s in SK)
print(f'GT crack px {sum(g.sum() for g in G)}, skeleton px {sum(s.sum() for s in SK)}, mean width {w:.2f} px')
widths = {}
for g in G:
    if g.any():
        d = ndi.distance_transform_edt(g)
        for s in [skeletonize(g)]:
            for v in (2 * d[s] - 1):
                widths[round(v)] = widths.get(round(v), 0) + 1
tot = sum(widths.values())
print('local width at skeleton (2*EDT-1) distribution:', {k: round(v / tot, 3) for k, v in sorted(widths.items()) if v / tot > 0.005})
cases = {
    'skeleton only (1 px line)': SK,
    'skeleton dilated r=1 (3 px line)': [ndi.binary_dilation(s, disk(1)) for s in SK],
    'skeleton dilated r=2 (5 px line)': [ndi.binary_dilation(s, disk(2)) for s in SK],
    'GT eroded 1 px (cross)': [ndi.binary_erosion(g, ndi.generate_binary_structure(2, 1)) | s for g, s in zip(G, SK)],
    'GT dilated 1 px (cross)': [ndi.binary_dilation(g, ndi.generate_binary_structure(2, 1)) for g in G],
    'GT dilated 1 px (3x3)': [ndi.binary_dilation(g, np.ones((3, 3), bool)) for g in G],
    'GT shifted 1 px (x)': [np.roll(g, 1, 1) for g in G],
    'GT shifted 1 px (x and y)': [np.roll(np.roll(g, 1, 1), 1, 0) for g in G],
    'GT shifted 2 px (x)': [np.roll(g, 2, 1) for g in G],
}
for k, P in cases.items():
    iou, f1, r, p = score(P, G)
    print(f'{k}: IoU {iou:.3f} relF1@2 {f1:.3f} R {r:.3f} P {p:.3f}')

print('\n# C. Same-image label disagreement already in the data (doc 03: train ARTS_00081_r5_c1 = test ARTS_00020_r5_c1)')
a = b = None
for sp in ['train', 'val', 'test']:
    for s, nm in [('ARTS_00081_r5_c1', 'a'), ('ARTS_00020_r5_c1', 'b')]:
        try:
            m = np.array(Image.open(f'{E}el_masks_{sp}/{s}.png')) == CR
            if nm == 'a': a = m
            else: b = m
        except FileNotFoundError:
            pass
if a is not None and b is not None:
    iou, f1, r, p = score([a], [b])
    print(f'escdd masks, same cell twice: crack IoU {iou:.3f} relF1@2 {f1:.3f} (px {a.sum()} vs {b.sum()})')
