"""SKR2C pre-opening gate (build_s2c_stage2.md §1 'Not done'; protocol_SKR2C §6 stage 2): load each fresh run's checkpoints/latest.pth on
CPU and print ONLY its step and its model state-dict key count, plus whether its key set and shapes equal the reference run's (the opened
pf2_SUPPF_100pct_s5, the D model-code reference). Reads nothing else from a checkpoint and prints no metric. CPU only (CUDA hidden by the
caller); one checkpoint in memory at a time.
Asserts: step == 20000 for every run; one key count for all runs; key set and shapes == the reference's. Exit 0 iff all hold.
Usage: python s2c_ckpt_check.py --ref REF_RUN_DIR RUN_DIR [RUN_DIR ...]
"""
import argparse, sys
from pathlib import Path

import torch

ap = argparse.ArgumentParser(); ap.add_argument('--ref', required=True); ap.add_argument('runs', nargs='+')
a = ap.parse_args()
torch.set_num_threads(4)


def keys(run):
    st = torch.load(Path(run) / 'checkpoints' / 'latest.pth', map_location='cpu', weights_only=False)
    sh = {k: tuple(v.shape) for k, v in st['models']['model'].items()}
    return int(st.get('step', -1)), sh


rs, rsh = keys(a.ref)
print(f'reference {Path(a.ref).name}: step {rs}, model state-dict keys {len(rsh)}', flush=True)
ok = rs == 20000
for r in a.runs:
    s, sh = keys(r)
    same = sh == rsh
    ok &= s == 20000 and len(sh) == len(rsh) and same
    print(f'{Path(r).name}: step {s} (== 20000 {s == 20000}) | model state-dict keys {len(sh)} | key set and shapes == reference {same}', flush=True)
print('CKPT CHECK', 'PASS' if ok else 'FAIL', f'({len(a.runs)} runs)')
sys.exit(0 if ok else 1)
