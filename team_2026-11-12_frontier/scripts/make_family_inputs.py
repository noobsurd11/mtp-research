#!/usr/bin/env python3
"""Batch 2 family inputs and the master ledger.

Reads rank/shortlist.json (merged scout records) and cards/ledger/T*.tsv (team verdicts).
Writes:
  rank/pid_map.tsv            stable paper ids (P001.. in the rank order of 13 Nov 17:00; kept once written)
  cards/in2/P###.json         full scout record per paper
  cards/fam_in/T<k>.md        digest for each batch 2 team: its papers, best first
  cards/fam_in/T<k>.pids      the pid list of that team
  cards/ledger/MASTER.tsv     every paper with its status (team verdict, or OPEN)
usage: make_family_inputs.py [--ledger-only]
"""
import csv, glob, json, os, re, sys, collections

ROOT = '/home/yugma/mtp/research/team_2026-11-12_frontier'

TEAMS = collections.OrderedDict([
    ('T6',  ['D14', 'D23', 'D24', 'D25']),
    ('T7',  ['D30', 'D31', 'D21', 'D08']),
    ('T8',  ['D02', 'D03', 'D06', 'D33', 'D36']),
    ('T9',  ['D07', 'D29', 'D32', 'D34', 'D39']),
    ('T10', ['D19', 'D20', 'D26', 'D27', 'D37']),
    ('T11', ['D01', 'D09', 'D12', 'D22', 'D40']),
    ('T12', ['D41', 'D43', 'D44', 'D04', 'D05']),
    ('T13', ['D38', 'D42']),
])
# batch 1 directions; their papers without a verdict stay OPEN under the owning family
B1 = {'D35': 'T1', 'D10': 'T2', 'D18': 'T2', 'D15': 'T3', 'D16': 'T3', 'D13': 'T4', 'D17': 'T4', 'D11': 'T5', 'D28': 'T5'}


def norm(s):
    return re.sub(r'[^a-z0-9]+', ' ', (s or '').lower()).strip()


def idk(s):
    i = (s or '').lower().strip()
    i = re.sub(r'^https?://(dx\.)?doi\.org/', 'doi:', i)
    i = re.sub(r'^https?://arxiv\.org/abs/', 'arxiv:', i)
    return re.sub(r'^(arxiv:\d{4}\.\d{4,5})v\d+$', r'\1', i)


def clip(s, n):
    s = re.sub(r'\s+', ' ', str(s or '')).strip()
    return s if len(s) <= n else s[:n - 3] + '...'


def main():
    pool = json.load(open(f'{ROOT}/rank/shortlist.json'))
    pool.sort(key=lambda e: e['rank'])

    # ---- stable ids
    mp = f'{ROOT}/rank/pid_map.tsv'
    by_key = {}
    if os.path.exists(mp):
        for r in csv.DictReader(open(mp), delimiter='\t'):
            by_key[(r['paper_id'], r['title_norm'])] = r['pid']
    nxt = 1 + max([int(v[1:]) for v in by_key.values()] or [0])
    for e in pool:
        k = (idk(e.get('paper_id')), norm(e['title']))
        hit = by_key.get(k)
        if not hit:  # same id or same title under another key
            for (i, t), v in by_key.items():
                if (i and i == k[0]) or t == k[1]:
                    hit = v; break
        if not hit:
            hit = f'P{nxt:03d}'; nxt += 1; by_key[k] = hit
        e['pid'] = hit
    with open(mp, 'w') as f:
        f.write('pid\tpaper_id\ttitle_norm\trank\ttitle\n')
        for e in sorted(pool, key=lambda e: e['pid']):
            f.write(f"{e['pid']}\t{idk(e.get('paper_id'))}\t{norm(e['title'])}\t{e['rank']}\t{clip(e['title'], 160)}\n")

    # ---- verdicts from the team ledgers (batch 1 keyed by rank of the old list, so match by id / title)
    verdict = {}
    for lf in sorted(glob.glob(f'{ROOT}/cards/ledger/T*.tsv')):
        team = os.path.basename(lf)[:-4]
        rows = list(csv.reader(open(lf), delimiter='\t'))
        if not rows:
            continue
        hdr = [h.strip().lower() for h in rows[0]]
        for r in rows[1:]:
            if len(r) < 4:
                continue
            d = dict(zip(hdr, r))
            pid_col = (d.get('pid') or '').strip()
            pk, tk = idk(d.get('paper_id')), norm(d.get('title'))
            e = None
            for x in pool:
                if (pid_col and x['pid'] == pid_col) or (pk and idk(x.get('paper_id')) == pk) or (tk and norm(x['title']) == tk):
                    e = x; break
            key = e['pid'] if e else f"X:{pk or tk}"
            verdict.setdefault(key, []).append({'team': team, 'status': (d.get('status') or '').strip(), 'arm': (d.get('arm') or '').strip(),
                                                'note': clip(list(d.values())[-1], 300), 'title': d.get('title'), 'paper_id': d.get('paper_id')})

    # ---- assignment
    assign = {}
    for e in pool:
        if e['pid'] in verdict:
            continue
        cnt = collections.Counter()
        for d in e['directions']:
            for t, ds in TEAMS.items():
                if d in ds:
                    cnt[t] += 1
        if cnt:
            best = max(cnt.values())
            assign[e['pid']] = next(t for t in TEAMS if cnt.get(t) == best)

    if '--ledger-only' not in sys.argv:
        os.makedirs(f'{ROOT}/cards/in2', exist_ok=True)
        os.makedirs(f'{ROOT}/cards/fam_in', exist_ok=True)
        for e in pool:
            json.dump(e, open(f"{ROOT}/cards/in2/{e['pid']}.json", 'w'), indent=1)
        for t, ds in TEAMS.items():
            mine = [e for e in pool if assign.get(e['pid']) == t]
            mine.sort(key=lambda e: (-(max(e.get('score') or 0, (e.get('bench_score') or 0) - 10)), e['rank']))
            with open(f'{ROOT}/cards/fam_in/{t}.pids', 'w') as f:
                f.write('\n'.join(e['pid'] for e in mine) + '\n')
            with open(f'{ROOT}/cards/fam_in/{t}.md', 'w') as f:
                f.write(f"# {t} input: {len(mine)} papers from scout directions {', '.join(ds)} (best first)\n\n")
                f.write('Fields from the scouts (not verified by you yet): score = value for raising our scores, bench = value for the benchmark suite (0 to 100). '
                        f'Full record of a paper: {ROOT}/cards/in2/<pid>.json.\n\n')
                for e in mine:
                    f.write(f"## {e['pid']} | {clip(e['title'], 150)}\n")
                    f.write(f"- id {e.get('paper_id') or '?'} | {e.get('year') or '?'} | {clip(e.get('venue'), 40)} | score {e.get('score')} | bench {e.get('bench_score')} | "
                            f"dirs {','.join(e['directions'])} | code {e.get('code_url') or 'none found'}\n")
                    f.write(f"- mechanism: {clip(e.get('mechanism'), 260)}\n")
                    f.write(f"- scout's adaptation: {clip(e.get('adaptation'), 300)}\n")
                    f.write(f"- evidence: {clip(e.get('evidence'), 220)} | prior overlap: {clip(e.get('prior_overlap'), 120)}\n\n")

    # ---- leftovers of the batch 1 directions: one digest per owning family (T1..T5)
    if '--ledger-only' not in sys.argv:
        left = collections.defaultdict(list)
        for e in pool:
            if e['pid'] in verdict or e['pid'] in assign:
                continue
            own = sorted({B1[d] for d in e['directions'] if d in B1})
            left[own[0] if own else 'T1'].append(e)
        for t, mine in sorted(left.items()):
            with open(f'{ROOT}/cards/fam_in/{t}_open.md', 'w') as f:
                f.write(f"# {t} open papers: {len(mine)} scout records the first {t} team did not take (best first)\n\n")
                for e in sorted(mine, key=lambda e: e['rank']):
                    f.write(f"## {e['pid']} | {clip(e['title'], 150)}\n")
                    f.write(f"- id {e.get('paper_id') or '?'} | {e.get('year') or '?'} | {clip(e.get('venue'), 40)} | score {e.get('score')} | bench {e.get('bench_score')} | "
                            f"dirs {','.join(e['directions'])} | code {e.get('code_url') or 'none found'}\n")
                    f.write(f"- mechanism: {clip(e.get('mechanism'), 260)}\n")
                    f.write(f"- scout's adaptation: {clip(e.get('adaptation'), 300)}\n")
                    f.write(f"- evidence: {clip(e.get('evidence'), 220)} | prior overlap: {clip(e.get('prior_overlap'), 120)}\n\n")
            print('open digest', t, len(mine))

    # ---- master ledger
    cnt = collections.Counter()
    with open(f'{ROOT}/cards/ledger/MASTER.tsv', 'w') as f:
        f.write('pid\trank\tscore\tbench\tpaper_id\ttitle\tdirections\tteam\tstatus\tarm\tnote\n')
        for e in pool:
            vs = verdict.get(e['pid'])
            if vs:
                # PROMOTE means "worth a card, not written yet": any other verdict (the card's) supersedes it,
                # whatever the ledger file order (T14.tsv sorts before T1b.tsv .. T5b.tsv)
                v = ([x for x in vs if x['status'] != 'PROMOTE'] or vs)[-1]
                team, status, arm, note = '+'.join(sorted({x['team'] for x in vs})), v['status'], v['arm'], v['note']
            elif e['pid'] in assign:
                team, status, arm, note = assign[e['pid']], 'OPEN', '', 'assigned to a batch 2 team; no verdict yet'
            else:
                own = sorted({B1[d] for d in e['directions'] if d in B1})
                team, status, arm, note = '+'.join(own) or '?', 'OPEN', '', 'scout record only; below the cut of the first family teams, not analysed yet'
            cnt[(team if status == 'OPEN' else 'verdict', status)] += 1
            f.write('\t'.join(str(x) for x in [e['pid'], e['rank'], e.get('score'), e.get('bench_score'), e.get('paper_id') or '', clip(e['title'], 160),
                                                 ','.join(e['directions']), team, status, arm, note]) + '\n')
        for k, vs in verdict.items():
            if k.startswith('X:'):
                v = vs[-1]
                f.write('\t'.join(['EXTRA', '', '', '', v['paper_id'] or '', clip(v['title'], 160), '', v['team'], v['status'], v['arm'], v['note']]) + '\n')
                cnt[('extra', v['status'])] += 1
    st = collections.Counter()
    for (a, b), n in cnt.items():
        st[b] += n
    print('papers', len(pool), '| status', dict(st))
    print('batch 2 teams', {t: sum(1 for v in assign.values() if v == t) for t in TEAMS})
    print('open under batch 1 families', {k[0]: n for k, n in cnt.items() if k[1] == 'OPEN' and k[0] not in TEAMS})


if __name__ == '__main__':
    main()
