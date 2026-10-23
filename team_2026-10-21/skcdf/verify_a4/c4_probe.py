"""Agent 4 SK1 null-diagnosis probe (inference only). Final latest.pth, EMA teacher for MT runs.
Per test GT crack component (8-connected): area, width (2 * median EDT on ridge), length (area / width),
contrast (mean image in crack - mean in 1-3 px ring, / image sd), and per run: px recall, relaxed@2 recall,
mean p(crack), share of px with p < 0.001 (confident miss). Also per cell: predicted crack px, GT crack px,
p(crack) mean on GT-inactive and GT-background px is not needed. Inactive: per cell tp/gt/pred and bin-0 share."""
import sys, json
from pathlib import Path
import numpy as np, torch
from PIL import Image
from scipy import ndimage as ndi
from torch.utils.data import DataLoader
ROOT = Path('/tmp/noob_el/el_sk1'); sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / 'scripts'))
from rescore_label_versions import DATA, IMG, MSK, NEW
from src.data.augmentations import get_weak_augmentation
from src.data.benchmark_el import BenchmarkELDataset
from src.data.splits import load_split
from src.models.model_factory import build_model
from src.utils.config import load_config
CR, IN = 14, 11
stems = sorted(load_split(DATA / 'splits' / 'test.txt'))
gts = {s: np.array(Image.open(NEW / 'test' / f'{s}.png')) for s in stems}
imgs = {s: np.asarray(Image.open(IMG / f'{s}.png').convert('L'), dtype=np.float32) for s in stems}
st8 = np.ones((3, 3), bool)
comps = []  # (stem, label image idx, mask)
feat = []
for s in stems:
    g = gts[s] == CR
    lab, n = ndi.label(g, structure=st8)
    im = imgs[s]; sd = im.std() + 1e-6
    for k in range(1, n + 1):
        m = lab == k
        a = int(m.sum())
        edt = ndi.distance_transform_edt(m)
        ridge = m & (edt == ndi.maximum_filter(edt, 3))
        w = float(2 * np.median(edt[ridge])) if ridge.any() else 1.0
        ring = ndi.binary_dilation(m, st8, iterations=3) & ~ndi.binary_dilation(m, st8, iterations=1) & (gts[s] != CR)
        c = float((im[m].mean() - im[ring].mean()) / sd) if ring.any() else 0.0
        comps.append((s, m)); feat.append(dict(stem=s, area=a, width=w, length=a / max(w, 1e-6), contrast=c))
dev = torch.device('cuda')
res = {'components': feat, 'runs': {}}
for run in sys.argv[2:]:
    d = ROOT / 'experiments' / run
    cfg = load_config(d / 'config_used.yaml'); dc = cfg['data']
    st = torch.load(d / 'checkpoints' / 'latest.pth', map_location=dev, weights_only=False)
    key = 'teacher' if cfg.get('method') == 'mean_teacher' else 'model'
    m_ = build_model(cfg['model']).to(dev); m_.load_state_dict(st['models'][key]); m_.eval()
    ds = BenchmarkELDataset(IMG, MSK, stems, get_weak_augmentation(dc.get('mean', [0.5]), dc.get('std', [0.25]), dc['input_size']))
    P, A = {}, {}
    with torch.no_grad():
        for b in DataLoader(ds, batch_size=8, shuffle=False, num_workers=2):
            with torch.autocast('cuda', dtype=torch.bfloat16):
                lg = m_(b['image'].to(dev)).float()
            sm = torch.softmax(lg, 1)
            for i, s in enumerate(b['stem']):
                P[s] = sm[i, CR].cpu().numpy(); A[s] = lg[i].argmax(0).cpu().numpy()
    comp_out = []
    for (s, m) in comps:
        pc = A[s] == CR
        d_pr = ndi.distance_transform_edt(~pc) if pc.any() else np.full(pc.shape, np.inf)
        p = P[s][m]
        comp_out.append([float(pc[m].mean()), float((d_pr[m] <= 2).mean()), float(p.mean()), float((p < 1e-3).mean())])
    cells = {}
    for s in stems:
        g = gts[s]; a = A[s]
        gi, ai = g == IN, a == IN
        cells[s] = dict(crack_pred=int((a == CR).sum()), crack_gt=int((g == CR).sum()),
                        bg_pcrack_mean=float(P[s][g == 0].mean()) if (g == 0).any() else None,
                        inact_tp=int((gi & ai).sum()), inact_gt=int(gi.sum()), inact_pred=int(ai.sum()))
    res['runs'][run] = dict(step=int(st.get('step', -1)), comps=comp_out, cells=cells)
    print(run, len(comp_out), flush=True)
json.dump(res, open(sys.argv[1], 'w'))
