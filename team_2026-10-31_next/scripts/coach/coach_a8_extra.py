"""coach (1 Nov, respawned session): A8 screen validity + dump-integrity recompute, own code, independent of a8_score.sh's passes 3b / 4.
(1) Encoder weight cosine at step 4000 vs the WEIGHTS FILE itself (not a8_init_dump's init.pth): A8 vs the DINOv3 timm safetensors
    (keys 1:1), A8c vs the torchvision IN-1k file through coach's own remap (features.{1,3,5,7} -> stages.{0..3}.blocks,
    features.{2,4,6} -> stages.{1,2,3}.downsample; block.0 conv_dw, block.3 fc1, block.5 fc2). Per stage: cosine of the concatenated
    >= 2-D weights (conv_dw, fc1, fc2, downsample conv; the stem conv is RGB-summed in el_f8, so stem is skipped here), plus the
    minimum per-tensor cosine. Validity (protocol_A8screen §3): stages 2 and 3 >= 0.5, every run.
(2) Val dump integrity: crack / inactive IoU at b 0 from the dump (pred = crack where margin > 0, else oth), pooled over the 54 val
    cells vs metrics.json val_history[-1] (step 4000); |d| <= 0.005.
(3) Step 4000 in latest.pth; stems: val dump == el_f8 val.txt order-free, rf dump == calib stems_eval; F51 / H36 / F19 sizes.
Usage: python -I coach_a8_extra.py V1_DIR EL_F8 RF_DIR RF_SETS_TSV DINOV3_SAFETENSORS TV_CONVNEXT_PTH"""
import json, re, sys
from pathlib import Path
import numpy as np, torch
from PIL import Image
from safetensors.torch import load_file

V, CODE, RF, RFS, W8, WC = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]), sys.argv[4], sys.argv[5], sys.argv[6]
ARMS = {'A8': ['f8_A8_4k_s0', 'f8_A8_4k_s1'], 'A8c': ['f8_A8c_4k_s0', 'f8_A8c_4k_s1']}
CRACK, INACT = 14, 11
torch.set_num_threads(8)


def tv_remap(sd):
    out = {}
    for k, v in sd.items():
        m = re.match(r'features\.(\d)\.(.*)', k)
        if not m:
            continue
        f, rest = int(m.group(1)), m.group(2)
        if f in (1, 3, 5, 7):
            s = (f - 1) // 2; mb = re.match(r'(\d+)\.block\.(\d)\.(weight|bias)', rest)
            if mb:
                nm = {'0': 'conv_dw', '2': 'norm', '3': 'mlp.fc1', '5': 'mlp.fc2'}[mb.group(2)]
                out[f'stages.{s}.blocks.{mb.group(1)}.{nm}.{mb.group(3)}'] = v
        elif f in (2, 4, 6):
            s = f // 2; md = re.match(r'(\d)\.(weight|bias)', rest)
            if md:
                out[f'stages.{s}.downsample.{md.group(1)}.{md.group(2)}'] = v
    return out


def stage_w(sd):
    """{stage: {name: tensor}} for >= 2-D weights under stages.N (prefix stripped)."""
    g = {}
    for k, v in sd.items():
        m = re.search(r'(?:^|\.)(stages\.(\d)\..*)$', k)
        if m and v.ndim >= 2 and k.endswith('weight'):
            g.setdefault(int(m.group(2)), {})[m.group(1)] = v.float()
    return g


ref = {'A8': stage_w(load_file(W8)), 'A8c': stage_w(tv_remap(torch.load(WC, map_location='cpu', weights_only=True)))}
print('## (1) encoder weight cosine at 4k vs the weights file (coach remap; concat cos | min per-tensor cos | n tensors | norm ratio)')
valid = {}
for arm, runs in ARMS.items():
    valid[arm] = True
    for r in runs:
        ck = torch.load(CODE / 'experiments' / r / 'checkpoints' / 'latest.pth', map_location='cpu', weights_only=False)
        step = ck.get('step', ck.get('global_step'))
        mods = ck['models']; mk = [k for k, m in mods.items() if any(n.startswith('encoder') for n in m)]
        assert len(mk) == 1, (r, list(mods))
        enc = {k: v for k, v in mods[mk[0]].items() if k.startswith('encoder')}
        g = stage_w(enc); line = []
        for s in range(4):
            rs, ts = ref[arm][s], g.get(s, {})
            assert set(rs) == set(ts), (r, s, sorted(set(rs) ^ set(ts))[:6])
            a = torch.cat([ts[k].flatten() for k in sorted(rs)]); b = torch.cat([rs[k].flatten() for k in sorted(rs)])
            cc = float(torch.nn.functional.cosine_similarity(a, b, 0)); nr = float(a.norm() / b.norm())
            mn = min(float(torch.nn.functional.cosine_similarity(ts[k].flatten(), rs[k].flatten(), 0)) for k in rs)
            line.append(f'stage{s} {cc:.4f} | {mn:.4f} | {len(rs)} | {nr:.4f}')
            if s in (2, 3) and cc < 0.5:
                valid[arm] = False
        print(f'  {r} step {step}: ' + '; '.join(line))
        assert int(step) == 4000, (r, step)
    print(f'  ARM {arm} {"VALID" if valid[arm] else "INVALID"} (stages 2-3 concat cos >= 0.5 in both runs)')

print('## (2) val dump at b 0 vs trainer metrics.json val_history[-1] (pooled 54 cells; tol 0.005)')
vtxt = [l.strip() for l in open(CODE / 'data' / 'splits' / 'val.txt') if l.strip()]
rows = [l.rstrip('\n').split('\t') for l in open(RFS) if l.strip()][1:]; rfset = {r[0]: r[1] for r in rows}
ev = [l.strip() for l in open(RF / 'stems_eval.txt') if l.strip()]
ok3 = True
for runs in ARMS.values():
    for r in runs:
        z = np.load(V / 'work' / 'dump' / f'{r}.val.npz'); st = [str(s) for s in z['stems']]
        assert sorted(st) == sorted(vtxt) and len(st) == 54, r
        zr = np.load(V / 'work' / 'dump' / f'{r}.rf.npz'); sr = [str(s) for s in zr['stems']]
        assert sorted(sr) == sorted(ev), r
        cnt = {k: sum(rfset[s] == k for s in sr) for k in ('F51', 'H36', 'F19')}
        I = {CRACK: [0, 0], INACT: [0, 0]}
        for i, s in enumerate(st):
            gt = np.array(Image.open(CODE / 'data' / 'labeled' / 'masks_escdd' / f'{s}.png'))
            pred = np.where(z['margin'][i].astype(np.float32) > 0, CRACK, z['oth'][i])
            for c in I:
                p, g = pred == c, gt == c
                I[c][0] += int((p & g).sum()); I[c][1] += int((p | g).sum())
        vh = json.load(open(CODE / 'experiments' / r / 'metrics.json'))['val_history'][-1]
        ci, ii = I[CRACK][0] / I[CRACK][1], I[INACT][0] / I[INACT][1]
        dc, di = ci - vh['crack_iou'], ii - vh['inactive_iou']; p = abs(dc) <= 0.005 and abs(di) <= 0.005 and vh['step'] == 4000
        ok3 &= p
        print(f'  {r}: crack {ci:.4f} vs {vh["crack_iou"]:.4f} ({dc:+.5f}); inactive {ii:.4f} vs {vh["inactive_iou"]:.4f} ({di:+.5f}); '
              f'step {vh["step"]}; rf {len(sr)} cells {cnt} -> {"PASS" if p else "FAIL"}')
print(f'## coach validity: {valid}; coach dump integrity: {"PASS" if ok3 else "FAIL"}')
