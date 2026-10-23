"""Agent 4 independent per-cell scorer for SK1 (and A5c references). Final latest.pth, EMA teacher for MT runs.
Per test cell: crack tp/gt/pred, relaxed@2 hits (p2_hit on pred, r2_hit on gt), inactive tp/union. Writes JSON."""
import sys, json
from pathlib import Path
import numpy as np, torch
from PIL import Image
from torch.utils.data import DataLoader
ROOT = Path('/tmp/noob_el/el_sk1'); sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / 'scripts'))
from rescore_label_versions import DATA, IMG, MSK, NEW, relaxed
from src.data.augmentations import get_weak_augmentation
from src.data.benchmark_el import BenchmarkELDataset
from src.data.splits import load_split
from src.models.model_factory import build_model
from src.utils.config import load_config
CR, IN = 14, 11
out = {}
stems = sorted(load_split(DATA / 'splits' / 'test.txt'))
gts = {s: np.array(Image.open(NEW / 'test' / f'{s}.png')) for s in stems}
dev = torch.device('cuda')
for run in sys.argv[2:]:
    d = ROOT / 'experiments' / run
    cfg = load_config(d / 'config_used.yaml'); dc = cfg['data']
    st = torch.load(d / 'checkpoints' / 'latest.pth', map_location=dev, weights_only=False)
    key = 'teacher' if cfg.get('method') == 'mean_teacher' else 'model'
    m = build_model(cfg['model']).to(dev); m.load_state_dict(st['models'][key]); m.eval()
    ds = BenchmarkELDataset(IMG, MSK, stems, get_weak_augmentation(dc.get('mean', [0.5]), dc.get('std', [0.25]), dc['input_size']))
    cells = {}
    with torch.no_grad():
        for b in DataLoader(ds, batch_size=8, shuffle=False, num_workers=2):
            with torch.autocast('cuda', dtype=torch.bfloat16):
                pr = m(b['image'].to(dev)).float().argmax(1).cpu().numpy()
            for s, p in zip(b['stem'], pr):
                g = gts[s]; pc, gc = p == CR, g == CR; pi_, gi = p == IN, g == IN
                r2 = relaxed(pc, gc, 2)
                cells[s] = dict(crack_tp=int((pc & gc).sum()), crack_gt=int(gc.sum()), crack_pred=int(pc.sum()),
                                crack_p2_hit=int(r2[0]), crack_r2_hit=int(r2[2]),
                                inact_tp=int((pi_ & gi).sum()), inact_union=int((pi_ | gi).sum()))
    out[run] = dict(step=int(st.get('step', -1)), weights=key, cells=cells)
    print(run, out[run]['step'], key, flush=True)
json.dump(out, open(sys.argv[1], 'w'))
