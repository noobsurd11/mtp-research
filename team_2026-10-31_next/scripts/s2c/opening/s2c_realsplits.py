"""SKR2C real-splits assert (protocol_SKR2C §3: the opening reads the REAL splits, never <data.root>/splits of a run's config; each pass
asserts its test stems = a31fad14's list and its per-cell output stems = the real stems). New file (build_s2c_stage2.md §5). CPU, json /
numpy only, no model. Prints md5s, counts and booleans only (never a metric value).
Real lists: <wt>/data/splits/test.txt (md5 a31fad14, 50 stems), val.txt (9dcccf00, 54), <ext>/stems_eval.txt (5266806b, 106).
Modes (exit 0 iff every check holds, else 1):
  pre   --wt WT [--wt WT ...] --ext EXT [--root-splits FILE MD5]: md5 of each worktree's test.txt / val.txt and of the ext stem list; the
        S2C training root's SPLITS.md5 (test = val there; recorded to show the opening does not use it).
  m0    --wt WT --ext EXT DIR RUN [RUN ...]: <run>.json (+ .tau0 / .tau1 if present): cells val / val_tta / test / ext stems == real lists.
  rescore --wt WT DIR RUN [RUN ...]: <run>.json: 'test/<run>' n == 50 and 'val/<run>' n == 54.
  la    --wt WT FILE RUN [RUN ...]: every 'test/<run>/tau*' entry n == 50 and per_cell stems == test list; 'val/<run>/tau*' n == 54 and
        per_cell stems (if any) == val list; every run present.
  b5    --wt WT --ext EXT DUMPDIR RECDIR RUN [RUN ...]: dump npz 'stems' (only that array is read) and record JSON cells for val / test / ext.
  scuffign --wt WT --ext EXT DIR RUN [RUN ...]: <run>.scuffign.json cells val / val_tta / test / ext.
  d     --wt WT --ext EXT DIR [--val-only]: every <E>.b*.json: cells val / test / test_noscuff / ext. With --val-only (ruling 5 identity
        run on the opened s5-9 members): no E-*.b*.json may exist and s2c_d_identity.txt must hold the read-log line 'sets ['val'] ...
        == the 54 val stems: True (no test / E1 file opened)'.
Usage: python s2c_realsplits.py MODE [options] ARGS
"""
import argparse, hashlib, json, sys
from pathlib import Path

import numpy as np

TEST_MD5, VAL_MD5, EXT_MD5 = 'a31fad14fa27ee28e2a2319b8976aba3', '9dcccf00662dfca750f0b46628f8d5bb', '5266806b559f74bcf9eae167bb076b95'
ap = argparse.ArgumentParser(); ap.add_argument('mode', choices=['pre', 'm0', 'rescore', 'la', 'b5', 'scuffign', 'd'])
ap.add_argument('--wt', action='append', required=True); ap.add_argument('--ext'); ap.add_argument('--root-splits', nargs=2)  # one worktree per --wt
ap.add_argument('--val-only', action='store_true'); ap.add_argument('args', nargs='*')
a = ap.parse_intermixed_args()  # positional DIR / RUN args may follow options (python 3.12 parse_args refuses that)
md5b = lambda b: hashlib.md5(b).hexdigest()
md5f = lambda p: md5b(open(p, 'rb').read())
smd5 = lambda st: md5b(('\n'.join(sorted(st)) + '\n').encode())[:8]
OK = [True]


def say(lab, ok):
    OK[0] &= bool(ok); print(f'{lab} -> {bool(ok)}', flush=True)


def lists(wt):
    t, v = Path(wt) / 'data' / 'splits' / 'test.txt', Path(wt) / 'data' / 'splits' / 'val.txt'
    assert md5f(t) == TEST_MD5 and md5f(v) == VAL_MD5, (wt, 'real split md5')
    L = {'test': sorted(l.strip() for l in open(t) if l.strip()), 'val': sorted(l.strip() for l in open(v) if l.strip())}
    assert len(L['test']) == 50 and len(L['val']) == 54
    if a.ext:
        e = Path(a.ext) / 'stems_eval.txt'; assert md5f(e) == EXT_MD5, 'ext stems_eval.txt md5'
        L['ext'] = sorted(l.strip() for l in open(e) if l.strip()); assert len(L['ext']) == 106
    return L


SETMAP = {'val': 'val', 'val_tta': 'val', 'test': 'test', 'test_noscuff': 'test', 'ext': 'ext'}


def cells_ok(lab, cells, L, sets=None):
    sets = sets or [s for s in cells if s in SETMAP]
    good, parts = True, []
    for s in sets:
        st = sorted(cells.get(s, {})); ref = L[SETMAP[s]]; g = st == ref; good &= g
        parts.append(f'{s} {len(st)} ({smd5(st)}){"" if g else " != real " + str(len(ref)) + " (" + smd5(ref) + ")"}')
    say(f'{lab}: ' + ', '.join(parts), good and len(sets) > 0)


if a.mode == 'pre':
    for w in a.wt:
        t, v = md5f(Path(w) / 'data/splits/test.txt'), md5f(Path(w) / 'data/splits/val.txt')
        say(f'{w}/data/splits: test.txt {t[:8]} (real a31fad14), val.txt {v[:8]} (real 9dcccf00)', t == TEST_MD5 and v == VAL_MD5)
    if a.ext:
        e = md5f(Path(a.ext) / 'stems_eval.txt'); say(f'{a.ext}/stems_eval.txt {e[:8]} (real 5266806b)', e == EXT_MD5)
    if a.root_splits:
        r = md5f(a.root_splits[0]); say(f'S2C training root {a.root_splits[0]} {r[:8]} (expected {a.root_splits[1][:8]}; its test.txt = val, NOT read by any pass)',
                                       r == a.root_splits[1])
else:
    L = lists(a.wt[0])
    if a.mode == 'm0':
        d, runs = Path(a.args[0]), a.args[1:]
        for r in runs:
            for suf in ('', '.tau0', '.tau1'):
                f = d / f'{r}{suf}.json'
                if suf and not f.exists():
                    continue
                j = json.load(open(f)); cells_ok(f'm0 {f.name}', j['cells'], L, ['val', 'test', 'ext'] + (['val_tta'] if 'val_tta' in j['cells'] else []))
    elif a.mode == 'rescore':
        d, runs = Path(a.args[0]), a.args[1:]
        for r in runs:
            j = json.load(open(d / f'{r}.json'))
            say(f'rescore {r}.json: test/{r} n {j[f"test/{r}"]["n"]} (50), val/{r} n {j[f"val/{r}"]["n"]} (54)',
                j[f'test/{r}']['n'] == 50 and j[f'val/{r}']['n'] == 54)
    elif a.mode == 'la':
        j = json.load(open(a.args[0])); runs = a.args[1:]; bad, n = [], 0
        for k, v in j.items():
            sp = k.split('/')[0]
            if sp not in ('test', 'val'):
                continue
            n += 1; want = 50 if sp == 'test' else 54
            if v.get('n') != want or ('per_cell' in v and sorted(v['per_cell']) != L[sp]):
                bad.append(k)
        have = {k.split('/')[1] for k in j if '/' in k}
        say(f'LA {Path(a.args[0]).name}: {n} test / val entries, n 50 / 54 and per_cell stems == real lists; runs present {sorted(have) == sorted(runs)}'
            + (f'; bad {bad[:3]}' if bad else ''), not bad and n > 0 and sorted(have) == sorted(runs))
    elif a.mode == 'b5':
        dd, rd, runs = Path(a.args[0]), Path(a.args[1]), a.args[2:]
        for r in runs:
            for s in ('val', 'test', 'ext'):
                with np.load(dd / f'{r}.{s}.npz', allow_pickle=False) as z:
                    st = sorted(str(x) for x in z['stems'])
                say(f'b5 dump {r}.{s}.npz stems {len(st)} ({smd5(st)})', st == L[s])
                cells_ok(f'b5 records {rd.name}/{r}.{s}.json', {s: json.load(open(rd / f'{r}.{s}.json'))['cells']}, L, [s])
    elif a.mode == 'scuffign':
        d, runs = Path(a.args[0]), a.args[1:]
        for r in runs:
            j = json.load(open(d / f'{r}.scuffign.json')); cells_ok(f'scuffign {r}', j['cells'], L, [s for s in ('val', 'val_tta', 'test', 'ext') if s in j['cells']])
    elif a.mode == 'd':
        d = Path(a.args[0]); fs = sorted(d.glob('E-*.b*.json'))
        if a.val_only:  # ruling 5 identity run: it writes no E-* file (exits after the val identity); its own read log must show val only
            say(f'D val-only {d.name}: E-*.b*.json files written {len(fs)} (expected 0: no test / E1 cell computed)', len(fs) == 0)
            t = (d / 's2c_d_identity.txt').read_text().split('\n') if (d / 's2c_d_identity.txt').exists() else []
            say(f'D val-only {d.name}: identity read-log line "sets [\'val\'] ... == the 54 val stems: True (no test / E1 file opened)" present',
                any("sets ['val']" in l and l.endswith('== the 54 val stems: True (no test / E1 file opened)') for l in t))
        else:
            say(f'D files in {d}: {len(fs)}', len(fs) > 0)
            for f in fs:
                cells_ok(f'D {f.name}', json.load(open(f))['cells'], L, ['val', 'test', 'test_noscuff', 'ext'])
print('REALSPLITS', a.mode, 'PASS' if OK[0] else 'FAIL')
sys.exit(0 if OK[0] else 1)
