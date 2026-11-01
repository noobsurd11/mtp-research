"""coach (1 Nov): protocol_B6 folds from judge's physical-module groups (judge/out/b6_groups.tsv, phys_group column).
Deterministic greedy, no random draw:
  1. groups with inactive px, by inactive px descending (ties: group id), each to the fold with the lowest running inactive px
     (ties: lower fold index);
  2. the other groups, source by source (ARTS, BMRK, CFVS, CSIR, SDLE), by cell count descending (ties: group id), each to the
     fold with the fewest cells of that source (ties: fewest cells in all, then lower fold index).
Train 478 + val 54 only (test / E1 never enter). Writes stem, split, phys_group, fold, inactive_px, crack_px; prints the per-fold table.
Usage: python b6_folds.py GROUPS_TSV OUT_TSV [K=5]"""
import sys, collections
src_of = lambda s: s.split('_')[0]
rows = [l.rstrip('\n').split('\t') for l in open(sys.argv[1])]
hdr, rows = rows[0], rows[1:]
ix = {h: i for i, h in enumerate(hdr)}
K = int(sys.argv[3]) if len(sys.argv) > 3 else 5
assert len(rows) == 532 and sum(r[ix['split']] == 'train' for r in rows) == 478 and sum(r[ix['split']] == 'val' for r in rows) == 54
G = collections.defaultdict(list)
for r in rows:
    G[r[ix['phys_group']]].append(r)
for g, rs in G.items():
    assert len({src_of(r[0]) for r in rs}) == 1, ('mixed-source group', g)
ina = {g: sum(int(r[ix['inactive_px']]) for r in rs) for g, rs in G.items()}
fold = {}; f_ina = [0] * K; f_n = [0] * K; f_src = [collections.Counter() for _ in range(K)]
def put(g, k):
    fold[g] = k; f_ina[k] += ina[g]; f_n[k] += len(G[g]); f_src[k][src_of(G[g][0][0])] += len(G[g])
for g in sorted((g for g in G if ina[g] > 0), key=lambda g: (-ina[g], g)):
    put(g, min(range(K), key=lambda k: (f_ina[k], k)))
for s in sorted({src_of(r[0]) for r in rows}):
    for g in sorted((g for g in G if ina[g] == 0 and src_of(G[g][0][0]) == s), key=lambda g: (-len(G[g]), g)):
        put(g, min(range(K), key=lambda k: (f_src[k][s], f_n[k], k)))
with open(sys.argv[2], 'w') as f:
    f.write('stem\tsplit\tphys_group\tfold\tinactive_px\tcrack_px\n')
    for r in sorted(rows):
        f.write(f"{r[0]}\t{r[ix['split']]}\t{r[ix['phys_group']]}\t{fold[r[ix['phys_group']]]}\t{r[ix['inactive_px']]}\t{r[ix['crack_px']]}\n")
print('fold | cells (train/val) | groups | inactive cells | inactive px (share) | crack cells | crack px | per source cells')
T = sum(ina.values())
for k in range(K):
    rs = [r for r in rows if fold[r[ix['phys_group']]] == k]
    print(f"{k} | {len(rs)} ({sum(r[ix['split']] == 'train' for r in rs)}/{sum(r[ix['split']] == 'val' for r in rs)}) | "
          f"{sum(1 for g in G if fold[g] == k)} | {sum(int(r[ix['inactive_px']]) > 0 for r in rs)} | "
          f"{sum(int(r[ix['inactive_px']]) for r in rs)} ({sum(int(r[ix['inactive_px']]) for r in rs) / T:.3f}) | "
          f"{sum(int(r[ix['crack_px']]) > 0 for r in rs)} | {sum(int(r[ix['crack_px']]) for r in rs)} | {dict(sorted(f_src[k].items()))}")
big = max(G, key=lambda g: ina[g])
print(f'largest inactive group {big}: {len(G[big])} cells, {ina[big] / T:.3f} of inactive px, fold {fold[big]}')
