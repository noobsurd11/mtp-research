#!/usr/bin/env python3
"""Merge phase A outputs into a ranked shortlist and the phase B inputs.

Reads the workflow journal (scout / critic paper lists, judge scores by index) and the judges'
own prompts (index -> title) from their transcripts. Writes:
  rank/shortlist.json      every deduped paper with scout and judge fields, sorted by final score
  rank/SHORTLIST.md        the ranked table
  cards/in/NNN.json        one input record per paper selected for phase B
  log/phaseB_args.json     the compact args for the phase B workflow
usage: merge_shortlist.py <workflow transcript dir> [--top 100] [--bench-min 70] [--bench-extra 20] [--pub 35]
"""
import argparse, glob, json, os, re, sys, collections

ROOT = '/home/yugma/mtp/research/team_2026-11-12_frontier'


def norm(s):
    return re.sub(r'[^a-z0-9]+', ' ', (s or '').lower()).strip()


def id_key(p):
    i = (p.get('paper_id') or '').lower().strip()
    i = re.sub(r'^https?://(dx\.)?doi\.org/', 'doi:', i)
    i = re.sub(r'^https?://arxiv\.org/abs/', 'arxiv:', i)
    i = re.sub(r'^(arxiv:\d{4}\.\d{4,5})v\d+$', r'\1', i)
    return i


def slugify(t, n=40):
    s = re.sub(r'[^a-z0-9]+', '_', (t or '').lower()).strip('_')
    return s[:n].rstrip('_') or 'paper'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('wdir')
    ap.add_argument('--top', type=int, default=100)
    ap.add_argument('--bench-min', type=int, default=70)
    ap.add_argument('--bench-extra', type=int, default=20)
    ap.add_argument('--per-cluster', type=int, default=2)
    ap.add_argument('--cluster-min', type=int, default=55)
    ap.add_argument('--pub', type=int, default=35)
    ap.add_argument('--dry', action='store_true')
    a = ap.parse_args()

    started, results = {}, {}
    for line in open(os.path.join(a.wdir, 'journal.jsonl')):
        try:
            j = json.loads(line)
        except Exception:
            continue
        if j.get('type') == 'started':
            started.setdefault(j['key'], []).append((j.get('label') or '', j.get('agentId')))
        elif j.get('type') == 'result':
            results[j['key']] = j

    # ---- scout and critic papers, in a stable order (direction id, then listing order)
    raw = []
    for key, j in results.items():
        r = j.get('result')
        lab = started.get(key, [('', None)])[-1][0]
        if not (isinstance(r, dict) and isinstance(r.get('papers'), list)):
            continue
        m = re.match(r'(scout|scout-retry|critic):([A-Z]\d+)', lab)
        did = m.group(2) if m else (r.get('direction_id') or '?')
        for p in r['papers']:
            if p and p.get('title'):
                q = dict(p); q['directions'] = [did]; raw.append(q)
    raw.sort(key=lambda p: (p['directions'][0], ))  # stable within a direction

    pool, by_title, by_id = [], {}, {}
    for p in raw:
        tk, ik = norm(p['title']), id_key(p)
        e = (tk and by_title.get(tk)) or (ik and by_id.get(ik))
        if e:
            dirs = sorted(set(e['directions'] + p['directions']))
            ss = e['scout_scores'] + [p.get('score')]
            alt = e.get('alt_notes', []) + [{'from': p['directions'][0], 'adaptation': p.get('adaptation'), 'min_experiment': p.get('min_experiment'), 'score': p.get('score')}]
            code = e.get('code_url') or p.get('code_url') or ''
            if (p.get('score') or 0) > (e.get('score') or 0):
                keep_alt = {'from': e['directions'][0], 'adaptation': e.get('adaptation'), 'min_experiment': e.get('min_experiment'), 'score': e.get('score')}
                e.clear(); e.update(p); alt = alt[:-1] + [keep_alt]
            e['directions'], e['scout_scores'], e['code_url'], e['alt_notes'] = dirs, ss, code, alt
        else:
            e = dict(p); e['scout_scores'] = [p.get('score')]
            pool.append(e)
        if tk: by_title[tk] = e
        if ik: by_id[ik] = e

    # ---- judges: index -> title from the judge's own prompt, scores from the journal
    n_j = 0
    for key, j in results.items():
        r = j.get('result')
        if not (isinstance(r, dict) and isinstance(r.get('scores'), list)):
            continue
        lab, aid = started.get(key, [('', None)])[-1]
        m = re.match(r'judge:(\d+):(\w+)', lab)
        if not m:
            continue
        lens = m.group(2)
        aid = j.get('agentId') or aid
        prompt = ''
        tf = os.path.join(a.wdir, f'agent-{aid}.jsonl')
        if os.path.exists(tf):
            with open(tf) as f:
                for line in f:
                    if 'Candidates:' in line:
                        try:
                            o = json.loads(line)
                            msg = o.get('message', {}).get('content', '')
                            if isinstance(msg, list):
                                msg = ' '.join(x.get('text', '') for x in msg if isinstance(x, dict))
                            prompt = msg
                        except Exception:
                            prompt = line
                        break
        idx2title = {}
        for mm in re.finditer(r'(?:^|\n)\[(\d+)\] (.+?) \((?:\d{4}|undefined|null), ', prompt):
            idx2title[int(mm.group(1))] = mm.group(2)
        for s in r['scores']:
            t = idx2title.get(s.get('idx'))
            e = by_title.get(norm(t)) if t else None
            if e is None:
                continue
            e.setdefault('judge', {})[lens] = {k: s.get(k) for k in ('score', 'bench', 'tier', 'cluster', 'reason')}
            n_j += 1

    for e in pool:
        js = list((e.get('judge') or {}).values())
        sc = [x['score'] for x in js if isinstance(x.get('score'), (int, float))]
        bs = [x['bench'] for x in js if isinstance(x.get('bench'), (int, float))]
        e['final'] = round(sum(sc) / len(sc)) if sc else (e.get('score') or 0)
        e['bench'] = round(sum(bs) / len(bs)) if bs else (e.get('bench_score') or 0)
        jj = e.get('judge') or {}
        e['cluster'] = (jj.get('realism') or jj.get('upside') or {}).get('cluster') or 'unjudged'
        e['tiers'] = '/'.join(str(x.get('tier')) for x in js)
        e['judged'] = len(sc)
    pool.sort(key=lambda e: (-e['final'], -e['bench'], norm(e['title'])))
    for i, e in enumerate(pool, 1):
        e['rank'] = i

    # ---- selection for phase B
    sel, why = [], {}
    for e in pool[:a.top]:
        sel.append(e); why[e['rank']] = 'top'
    extra = [e for e in pool[a.top:] if e['bench'] >= a.bench_min]
    extra.sort(key=lambda e: -e['bench'])
    for e in extra[:a.bench_extra]:
        sel.append(e); why[e['rank']] = 'bench'
    per = collections.defaultdict(list)
    for e in pool:
        per[e['cluster']].append(e)
    for cl, es in per.items():
        for e in es[:a.per_cluster]:
            if e['final'] >= a.cluster_min and e['rank'] not in why:
                sel.append(e); why[e['rank']] = 'cluster'
    sel.sort(key=lambda e: e['rank'])

    def free_copy(e):
        i = id_key(e); u = (e.get('url') or '').lower()
        return i.startswith('arxiv:') or '10.48550' in i or 'arxiv.org' in u or 'openaccess.thecvf' in u or 'openreview' in u or 'mdpi.com' in u
    pub_left = a.pub
    args = []
    for e in sel:
        pub = 0
        if not free_copy(e) and pub_left > 0:
            pub, pub_left = 1, pub_left - 1
        e['pub_allowed'] = pub; e['selected_for'] = why[e['rank']]
        args.append({'n': e['rank'], 'slug': slugify(e['title']), 'title': e['title'], 'pub': pub})

    stats = {'raw': len(raw), 'dedup': len(pool), 'judge_scores_mapped': n_j,
             'judged_both': sum(1 for e in pool if e['judged'] >= 2), 'judged_one': sum(1 for e in pool if e['judged'] == 1),
             'selected': len(sel), 'selected_why': dict(collections.Counter(why.values())), 'pub_allowed': a.pub - pub_left,
             'clusters_selected': dict(collections.Counter(e['cluster'] for e in sel))}
    print(json.dumps(stats, indent=1))
    if a.dry:
        for e in pool[:15]:
            print(e['rank'], e['final'], e['bench'], e['cluster'], e.get('year'), e['title'][:90])
        return

    os.makedirs(os.path.join(ROOT, 'rank'), exist_ok=True)
    os.makedirs(os.path.join(ROOT, 'cards', 'in'), exist_ok=True)
    json.dump(pool, open(os.path.join(ROOT, 'rank', 'shortlist.json'), 'w'), indent=1)
    json.dump({'papers': args}, open(os.path.join(ROOT, 'log', 'phaseB_args.json'), 'w'))
    for e in sel:
        json.dump(e, open(os.path.join(ROOT, 'cards', 'in', f"{e['rank']:03d}.json"), 'w'), indent=1)
    selset = {e['rank'] for e in sel}
    with open(os.path.join(ROOT, 'rank', 'SHORTLIST.md'), 'w') as f:
        f.write('# Ranked paper list (phase A)\n\n')
        f.write(f"{len(raw)} scout entries, {len(pool)} unique papers, {stats['judged_both']} judged by both lenses. "
                f"final = mean of the upside and realism scores (value for raising our scores); bench = value for the benchmark suite. "
                f"B = selected for a phase B card ({len(sel)}). Tiers: A first week, B after a gate, C reference, X void with evidence.\n\n")
        f.write('| # | B | final | up | real | bench | tier | cluster | year | paper | id | code | from |\n|---|---|---|---|---|---|---|---|---|---|---|---|---|\n')
        for e in pool:
            jj = e.get('judge') or {}
            f.write('| {} | {} | {} | {} | {} | {} | {} | {} | {} | {} | {} | {} | {} |\n'.format(
                e['rank'], 'B' if e['rank'] in selset else '', e['final'],
                (jj.get('upside') or {}).get('score', ''), (jj.get('realism') or {}).get('score', ''), e['bench'], e['tiers'], e['cluster'],
                e.get('year', ''), (e['title'] or '').replace('|', '/')[:110], (e.get('paper_id') or '').replace('|', '/'),
                'y' if e.get('code_url') else '', ','.join(e['directions'])))
    print('written: rank/shortlist.json, rank/SHORTLIST.md, cards/in/*.json, log/phaseB_args.json')


if __name__ == '__main__':
    main()
