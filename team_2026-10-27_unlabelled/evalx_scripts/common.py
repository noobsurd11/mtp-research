"""evalx shared loaders. Reads results/e1/raw_v2 per-cell counts (test 50 + ext 106 per run)."""
import glob, json, re
import numpy as np

R = '/home/yugma/mtp/research/results/e1/raw_v2/'
NOISY = 'CSIR_00070_r8_c4'
TWINS = ["CFVS_00006_r5_c5", "CFVS_00033_r8_c4", "CFVS_00035_r8_c4", "CFVS_00042_r8_c4", "CFVS_00018_r4_c4",
         "CFVS_00027_r4_c4", "ARTS_00020_r5_c1"]

# 5-seed arms (pooled where the handbook pools them)
ARMS = {
    'A5c': ['p12_A_5pct', 'p13_A_5pct'], 'BsM5': ['p13_BsM_5pct'], 'CsM5': ['p13_CsM_5pct'],
    'BsD5': ['p17_BsD_5pct'], 'al1_A5': ['al1_A5'], 'al1_BsM5': ['al1_BsM5'], 'al1_AL5': ['al1_AL5'],
    'al1_CPS5': ['al1_CPS5'],
    'A20': ['p6_L3_20pct', 'p16_A_20pct'], 'S20': ['p16_S_20pct'],
    'A50': ['p16_A_50pct'], 'S50': ['p16_S_50pct'],
    'A100': ['p6_L3_100pct', 'p16_A_100pct'], 'Sx100': ['p16_Sx_100pct'],
    'L3_10': ['p6_L3_10pct'], 'BsM10': ['p18_BsM_10pct'], 'BsM20': ['p18_BsM_20pct'],
}


def runs(arm):
    fs = []
    for p in ARMS[arm]:
        fs += sorted(glob.glob(R + p + '_s*.json'))
    return fs


def load(arm, split='test'):
    """returns cells (sorted list), dict metric-> array [seed, cell]"""
    fs = runs(arm)
    js = [json.load(open(f))['cells'][split] for f in fs]
    cells = sorted(js[0].keys())
    keys = ['crack_gt', 'crack_pred', 'crack_tp', 'inact_gt', 'inact_pred', 'inact_tp']
    if split == 'test':
        keys += ['crack_p2_hit', 'crack_r2_hit']
    X = {k: np.array([[j[c].get(k, 0) for c in cells] for j in js], float) for k in keys}
    return cells, X, [re.sub(r'.*/', '', f)[:-5] for f in fs]


def pooled(X, idx=None, axis=-1):
    """pooled metrics per seed over cell subset idx (array of cell indices, may repeat)."""
    S = {k: (v[:, idx] if idx is not None else v).sum(axis) for k, v in X.items()}
    out = {}
    out['crack_iou'] = S['crack_tp'] / np.maximum(S['crack_gt'] + S['crack_pred'] - S['crack_tp'], 1)
    out['crack_rec'] = S['crack_tp'] / np.maximum(S['crack_gt'], 1)
    out['inact_iou'] = S['inact_tp'] / np.maximum(S['inact_gt'] + S['inact_pred'] - S['inact_tp'], 1)
    if 'crack_p2_hit' in S:
        rp = S['crack_p2_hit'] / np.maximum(S['crack_pred'], 1)
        rr = S['crack_r2_hit'] / np.maximum(S['crack_gt'], 1)
        out['relF1'] = 2 * rp * rr / np.maximum(rp + rr, 1e-9)
    return out


METRICS = ['crack_iou', 'relF1', 'crack_rec', 'inact_iou']


def subset(cells, name):
    if name == 'all':
        return np.arange(len(cells))
    if name == 'clean':
        return np.array([i for i, c in enumerate(cells) if c != NOISY])
    if name == 'clean_notwin':
        return np.array([i for i, c in enumerate(cells) if c != NOISY and c not in TWINS])
    raise ValueError(name)
