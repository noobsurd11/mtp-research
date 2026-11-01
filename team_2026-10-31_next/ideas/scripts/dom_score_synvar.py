"""Idea 5 diagnostic scorer (CPU, read-only checkpoints): ensemble mean softmax of a model group on the val
half-cut variants (dom_synth_variants.py), crack at bias b (margin + b > 0), metrics per variant vs the transformed
GT: pooled crack recall / precision / IoU, relR@2, relP@2, cells detected (relR@2 >= 0.2 among GT >= 20 px), crack px
per crack-free image, inactive IoU (argmax). Model loading as calib_dump.py (step 20000 asserted).
Usage: python -I dom_score_synvar.py --code EL_F3 --dir SYNVAR --group NAME RUN... [--group ...] --bias B --threads 8 [--percell OUT.tsv]
v2 (31 Oct 17:40): optional per-image counts (--percell); aggregates unchanged."""
import argparse, sys, time, csv, collections
from pathlib import Path
import numpy as np, torch
from PIL import Image
from scipy import ndimage as ndi
ap = argparse.ArgumentParser(); ap.add_argument('--code', required=True); ap.add_argument('--dir', required=True)
ap.add_argument('--group', nargs='+', action='append', required=True); ap.add_argument('--bias', type=float, nargs='+', default=[0.0])
ap.add_argument('--threads', type=int, default=8); ap.add_argument('--percell', default='')
a = ap.parse_args()
pcw = open(a.percell, 'w') if a.percell else None
if pcw: pcw.write('group\tbias\tname\tvariant\tsrc\tgt_crack\ttp\tfp\tfn\trelR2_hit\trelP2_hit\tpred_px\tgt_inact\titp\tifp\tifn\n')
sys.path.insert(0, a.code)
from src.models.model_factory import build_model
from src.utils.config import load_config
torch.set_num_threads(a.threads); CR, IN = 14, 11
def load(run):
    run = Path(run); cfg = load_config(run / 'config_used.yaml')
    st = torch.load(run / 'checkpoints' / 'latest.pth', map_location='cpu', weights_only=False); assert int(st.get('step', -1)) == 20000, run
    mc = {k: v for k, v in cfg['model'].items() if k not in ('encoder_init', 'decoder_init')}; mc['encoder_weights'] = None
    m = build_model(mc); m.load_state_dict(st['models']['model']); m.eval(); return m
disk = np.array([[1 if (i - 2) ** 2 + (j - 2) ** 2 <= 4 else 0 for j in range(5)] for i in range(5)], bool)
D = Path(a.dir); items = [l.rstrip('\n').split('\t') for l in open(D / 'list.tsv') if l.strip()]
t0 = time.time()
for g in a.group:
    name, runs = g[0], g[1:]; ms = [load(r) for r in runs]
    acc = {b: collections.defaultdict(lambda: collections.Counter()) for b in a.bias}
    with torch.no_grad():
        for k, (nm, vn, src) in enumerate(items):
            u = np.array(Image.open(D / 'images' / f'{nm}.png').convert('L'), np.float32) / 255.0
            x = torch.from_numpy((u - 0.5) / 0.25)[None, None]
            p = sum(torch.softmax(m(x).float(), 1)[0] for m in ms) / len(ms)
            lq = torch.log(p + 1e-12); pc = lq[CR].clone(); lq[CR] = -1e30; mo, oth = lq.max(0)
            margin = (pc - mo).numpy(); oth = oth.numpy()
            gt = np.array(Image.open(D / 'masks' / f'{nm}.png')); g_ = gt == CR; gi = gt == IN
            for b in a.bias:
                pr = margin + b > 0; c = acc[b][vn]
                if pcw:
                    pi_ = (~pr) & (oth == IN); prd = ndi.binary_dilation(pr, disk); gtd = ndi.binary_dilation(g_, disk)
                    pcw.write(f'{name}\t{b}\t{nm}\t{vn}\t{src}\t{int(g_.sum())}\t{int((pr & g_).sum())}\t{int((pr & ~g_).sum())}\t{int((~pr & g_).sum())}\t'
                              f'{int((g_ & prd).sum())}\t{int((pr & gtd).sum())}\t{int(pr.sum())}\t{int(gi.sum())}\t{int((pi_ & gi).sum())}\t{int((pi_ & ~gi).sum())}\t{int((~pi_ & gi).sum())}\n')
                if g_.sum() >= 20:
                    c['n'] += 1; c['tp'] += int((pr & g_).sum()); c['fp'] += int((pr & ~g_).sum()); c['fn'] += int((~pr & g_).sum())
                    rr = int((g_ & ndi.binary_dilation(pr, disk)).sum()); c['rr'] += rr; c['gn'] += int(g_.sum())
                    c['rp'] += int((pr & ndi.binary_dilation(g_, disk)).sum()); c['pn'] += int(pr.sum()); c['det'] += int(rr / g_.sum() >= 0.2)
                elif g_.sum() == 0:
                    c['nfree'] += 1; c['free_px'] += int(pr.sum())
                pi = (~pr) & (oth == IN)
                c['itp'] += int((pi & gi).sum()); c['ifp'] += int((pi & ~gi).sum()); c['ifn'] += int((~pi & gi).sum())
            if k % 100 == 0: print(f'[{time.time() - t0:.0f}s] {name} {k}/{len(items)}', flush=True)
    for b in a.bias:
        print(f'== {name} bias {b}')
        for vn in sorted(acc[b]):
            c = acc[b][vn]
            print('  %s crack cells %3d  recall %.3f  prec %.3f  IoU %.3f  relR@2 %.3f  relP@2 %.3f  det %d/%d  free px/img %.0f (n %d)  inactive IoU %.3f' % (
                vn, c['n'], c['tp'] / max(c['tp'] + c['fn'], 1), c['tp'] / max(c['tp'] + c['fp'], 1), c['tp'] / max(c['tp'] + c['fp'] + c['fn'], 1),
                c['rr'] / max(c['gn'], 1), c['rp'] / max(c['pn'], 1), c['det'], c['n'], c['free_px'] / max(c['nfree'], 1), c['nfree'],
                c['itp'] / max(c['itp'] + c['ifp'] + c['ifn'], 1)), flush=True)
if pcw: pcw.close()
print(f'DONE {time.time() - t0:.0f}s', flush=True)
