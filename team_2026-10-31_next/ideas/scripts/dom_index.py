"""domain: cell index for train/val/test/E1/Hanifi _rf: module, row, col, half-cut flag, content box,
crack/inactive/scuff px. Masks: E-SCDD (= 20221008 for crack/inactive; class 29 marks half-cut) and, for
E1, the 20221008 release (crack/inactive identical). Writes dom_index.tsv. Usage: python -I dom_index.py OUT.tsv"""
import os, re, sys, glob, csv, numpy as np
from PIL import Image
H = os.path.expanduser('~')
D11 = H + '/mtp/datasets/BenchmarkELimages/dataset_20211104'
ES = H + '/mtp/datasets/escdd_full'
R22 = H + '/mtp/datasets/BenchmarkEL_releases/dataset_20221008'
SP = H + '/mtp/datasets/splits_benchmark'
E1CTX = H + '/mtp/research/team_2026-10-29_features/scripts/e1_context.tsv'
rx = re.compile(r'^([A-Z]+)_(\d+)_(?:r(\d+)_c(\d+)|cell(\d+)|(A\d+)-\S+-cell(\d+))(_rf)?$')
es_img = {os.path.basename(p)[:-4]: p for p in glob.glob(ES + '/el_images_*/*.png')}
es_msk = {os.path.basename(p)[:-4]: p for p in glob.glob(ES + '/el_masks_*/*.png')}
r22_img = {os.path.basename(p)[:-4]: p for p in glob.glob(R22 + '/el_images_*/*.png')}
r22_msk = {os.path.basename(p)[:-4]: p for p in glob.glob(R22 + '/el_masks_*/*.png')}
sets = {}
for s in ('train', 'val', 'test'):
    for l in open(f'{SP}/{s}.txt'):
        sets[l.strip()] = s
e1ctx = {}
for l in open(E1CTX):
    f = l.rstrip('\n').split('\t'); e1ctx[f[0]] = f[1:]
    sets[f[0]] = 'E1'
for st in es_img:
    if st.endswith('_rf') and not st[0].isdigit() and st not in sets:
        sets[st] = 'rf'
def content_box(a):
    keep_r = np.mean(a >= 250, axis=1) <= 0.98; keep_c = np.mean(a >= 250, axis=0) <= 0.98
    return int(keep_r.sum()), int(keep_c.sum())
out = open(sys.argv[1], 'w'); w = csv.writer(out, delimiter='\t')
w.writerow(['stem', 'set', 'src', 'module', 'row', 'col', 'img', 'mask', 'halfcut', 'content_h', 'content_w',
            'crack_px', 'inactive_px', 'scuff_px', 'mean', 'sd'])
dirs = {'train': 'images_train_original', 'val': 'images_val', 'test': 'images_test'}
for st, s in sorted(sets.items()):
    m_ = rx.match(st); src = m_.group(1)
    # module key: CSIR/ARTS/CFVS = numeric id; SDLE = A-token (image id is per cell); BMRK = none (ELPV names carry no module)
    mod = m_.group(2) if m_.group(3) else (m_.group(6) if m_.group(6) else '')
    row = m_.group(3) or ''; col = m_.group(4) or ''
    if s in dirs:
        ip = f'{D11}/{dirs[s]}/{st}.png'
    elif s == 'E1':
        ip = r22_img.get(st) or es_img.get(st)
    else:
        ip = es_img[st]
    mp = es_msk.get(st) or r22_msk.get(st) or ''
    a = np.asarray(Image.open(ip).convert('L'), dtype=np.float32)
    ch, cw = content_box(a)
    if mp:
        m = np.asarray(Image.open(mp))
        hc = int(bool(np.isin(m, [24, 29]).any()))
        cr, ia, sc = int((m == 14).sum()), int((m == 11).sum()), int((m == 25).sum())
    else:
        hc, cr, ia, sc = -1, -1, -1, -1
    if s == 'E1':
        hc = int(e1ctx[st][2].split('=')[1])
    w.writerow([st, s, src, mod, row, col, ip, mp, hc, ch, cw, cr, ia, sc, round(float(a.mean()), 1), round(float(a.std()), 1)])
out.close()
