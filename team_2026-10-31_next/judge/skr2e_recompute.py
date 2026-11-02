#!/usr/bin/env python3
"""judge skr2e_recompute (2 Nov 2026, respawned judge): independent recompute of the SKR2E opening (E1 opening #6) from the
pulled per-cell files. Own code: imports nothing from the run, Track M, coach or runner; numpy only; laptop.
 1 integrity: members / step / revision per file; union b written; val GT comps 125, E1 296; E1 crack-free cells 74.
 2 D2 re-derived from the stored val sweep (FINAL rule) + val cells re-summed at every written b vs the sweep.
 3 E-PF identity vs PF2E E-PF.b0 / b1.5 (every split, every cell, exact).
 4 verdict at b 0 (protocol §3): test crack IoU / relF1@2 / inactive IoU (all 50 + clean 49, paired image boot 2000 seed 0);
   E1 relF1@2 + any-hit (paired 71-cluster boot 2000 seed 0; any-hit = pooled count ratio); E1 inactive for G1e.
 5 guards G2a / G2b / G1t / G1e at (0, 0) and at the headline pair (point estimates; G1e on its cluster CI).
 6 bias share: every arm x b in U; all U x U pair deltas; E1 aggregate sweep both arms, all grid b (re-checked at U);
   E-PF's own bias gain vs the b 0 gap; matched-volume (E1 from the sweep; test from U only).
 7 any-hit concentration: per image / stratum / top-k / LOCO / leave-top-3-images-out; n_eff of GT comps and of the hit gap.
Δ = E-SKR2 - E-PF throughout.
Usage: skr2e_recompute.py OUT_DIR PF2E_RAW_DIR E1_CONTEXT_TSV  |  skr2e_recompute.py --selftest PF2E_RAW_DIR"""
import json, re, sys, math
from pathlib import Path
import numpy as np

CR, IN, NOISY = 14, 11, 'CSIR_00070_r8_c4'
MOD = lambda s: re.sub(r'(_r\d+_c\d+|_cell\d+)$', '', s)
NAMES = ['crack IoU', 'relF1@2', 'inact IoU', 'any-hit', 'relP@2', 'relR@2', 'crack P', 'crack R', 'pred/GT']
GRID = [i * 0.25 for i in range(13)]


def vec(c):
    m = np.asarray(c['conf'], np.int64); n = int(math.isqrt(m.size)); m = m.reshape(n, n)  # rows GT, cols pred
    g = [e for e in c['crack_cc']['gt'] if e[0] >= 20]
    return np.array([m[CR, CR], m[:, CR].sum() - m[CR, CR], m[CR, :].sum() - m[CR, CR],
                     m[IN, IN], m[:, IN].sum() - m[IN, IN], m[IN, :].sum() - m[IN, IN],
                     *c['crack_rel2'], sum(1 for e in g if e[1] >= 1), len(g), m[:, CR].sum(), m[CR, :].sum()], np.float64)


def X(cells, stems):
    return np.stack([vec(cells[s]) for s in stems])


def prim(S):
    d = lambda a, b: a / b if b > 0 else 0.0
    P, R = d(S[6], S[7]), d(S[8], S[9])
    return np.array([d(S[0], S[0] + S[1] + S[2]), 2 * P * R / (P + R) if P + R > 0 else 0.0, d(S[3], S[3] + S[4] + S[5]),
                     d(S[10], S[11]), P, R, d(S[0], S[0] + S[1]), d(S[0], S[0] + S[2]), d(S[12], S[13])])


def boot(A, B, stems, key=None, n=2000, seed=0):
    XA, XB = X(A, stems), X(B, stems)
    if key:
        gs = sorted({key(s) for s in stems}); gi = {g: i for i, g in enumerate(gs)}; lab = np.array([gi[key(s)] for s in stems])
        CA = np.stack([XA[lab == i].sum(0) for i in range(len(gs))]); CB = np.stack([XB[lab == i].sum(0) for i in range(len(gs))])
    else:
        gs = stems; CA, CB = XA, XB
    G = len(gs); full = prim(CB.sum(0)) - prim(CA.sum(0)); rng = np.random.default_rng(seed); out = np.empty((n, len(NAMES)))
    for t in range(n):
        w = np.bincount(rng.integers(0, G, G), minlength=G).astype(np.float64)
        out[t] = prim(w @ CB) - prim(w @ CA)
    lo, hi = np.percentile(out, [2.5, 97.5], 0)
    loo = np.array([prim(CB.sum(0) - CB[j]) - prim(CA.sum(0) - CA[j]) for j in range(G)])
    return dict(full=full, lo=lo, hi=hi, p=(out > 0).mean(0), n=G, loo=loo, groups=gs, CA=CA, CB=CB)


def fmt(r, i):
    return f"{NAMES[i]} {r['full'][i]:+.4f} [{r['lo'][i]:+.4f}, {r['hi'][i]:+.4f}] P>0 {r['p'][i]:.3f}"


def crackfree_px(cells):
    cf = [s for s in cells if vec(cells[s])[13] == 0]
    return len(cf), int(sum(vec(cells[s])[12] for s in cf))


if '--selftest' in sys.argv:  # E-g vs E-PF at b 0 from PF2E's opened files must give verify_pf2e; identical arms -> 0
    d = Path(sys.argv[sys.argv.index('--selftest') + 1])
    A = json.load(open(d / 'E-g.b0.json'))['cells']; B = json.load(open(d / 'E-PF.b0.json'))['cells']
    st = sorted(A['test']); r = boot(A['test'], B['test'], st)
    print('selftest PF2E test all 50 (E-PF - E-g, b 0): ' + ' | '.join(fmt(r, i) for i in (0, 1, 2)))
    print('   expected (verify_pf2e, runner CIs): +0.0027 [-0.0146, +0.0159] | +0.0121 [-0.0048, +0.0309] | +0.0237 [-0.0310, +0.0971]')
    e = sorted(A['ext']); r = boot(A['ext'], B['ext'], e, key=MOD)
    print(f'selftest PF2E E1 ({r["n"]} clusters): ' + ' | '.join(fmt(r, i) for i in (1, 2)) + '   [any-hit not printed for E-g: not part of SKR2E]')
    print('   expected: relF1@2 +0.0355 [-0.0232, +0.0912] | inact +0.2141 [+0.0303, +0.3820]')
    r0 = boot(B['ext'], B['ext'], e, key=MOD); print('identical arms (E-PF vs E-PF) all 0:', bool(np.allclose(r0['full'], 0) and np.allclose(r0['lo'], 0) and np.allclose(r0['hi'], 0)))
    XB = X(B['ext'], e).sum(0); print(f'E-PF b 0 E1 any-hit (the SKR2E comparator; = coach-disclosed 102/296): {int(XB[10])}/{int(XB[11])}; '
                                      f'crack-free cells / px {crackfree_px(B["ext"])} (verify_pf2e: 74 / 2,528)')
    sys.exit()

D, PF2E, CTX = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
ctx = {l.split('\t')[0]: l.rstrip('\n').split('\t') for l in open(CTX) if l.strip()}
dec = json.load(open(D / 'skr2e_val_decisions.json'))
J = {}
for f in sorted(D.glob('E-*.b*.json')):
    j = json.load(open(f)); J[(j['run'], float(j['bias']))] = j
ARMS = ('E-PF', 'E-SKR2')
U = sorted({b for (_, b) in J})
print('# files:', sorted(f'{k} b{b:g}' for k, b in J), '| union in decisions:', dec.get('union_b'))
print('\n## 1 integrity')
EXP = {'E-PF': ('pf2_SUPPF', 'e544133'), 'E-SKR2': ('skr2_SKR01', 'c9bbb02')}
for (k, b), j in sorted(J.items()):
    pre, rev = EXP[k]
    ok = (j['members'] == [f'{pre}_100pct_s{q}' for q in range(5, 10)] and j['step'] == 20000 and j['code_revision'] == rev
          and j.get('model_code_revision', 'e544133') == 'e544133')
    ns = {sp: len(v) for sp, v in j['cells'].items()}
    print(f'  {k} b{b:g}: members ok={ok} rev {j["code_revision"]} model {j.get("model_code_revision")} cells {ns} chosen {j["chosen_bias"]} headline {j["headline_bias"]}')
for k in ARMS:
    print(f'  {k} written at b {sorted(b for (kk, b) in J if kk == k)}; union U {U}: {"ok" if sorted(b for (kk, b) in J if kk == k) == U else "MISMATCH"}')
for k in ARMS:
    v = X(J[(k, 0.0)]['cells']['val'], sorted(J[(k, 0.0)]['cells']['val'])).sum(0); e = X(J[(k, 0.0)]['cells']['ext'], sorted(J[(k, 0.0)]['cells']['ext'])).sum(0)
    print(f'  {k}: val GT comps>=20 {int(v[11])} (125), E1 {int(e[11])} (296), E1 crack-free cells / px at b0 {crackfree_px(J[(k, 0.0)]["cells"]["ext"])}')
same = all(J[('E-PF', 0.0)]['cells'][sp].keys() == J[('E-SKR2', 0.0)]['cells'][sp].keys() for sp in ('val', 'test', 'test_noscuff', 'ext'))
print(f'  identical stem sets across arms: {same}; E1 clusters {len({MOD(s) for s in J[("E-PF", 0.0)]["cells"]["ext"]})}')
gtsame = all((X(J[('E-PF', 0.0)]['cells'][sp], sorted(J[('E-PF', 0.0)]['cells'][sp]))[:, [11, 13, 9]] ==
              X(J[('E-SKR2', b)]['cells'][sp], sorted(J[('E-PF', 0.0)]['cells'][sp]))[:, [11, 13, 9]]).all() for sp in ('val', 'test', 'ext') for b in U)
print(f'  GT-only columns (comps n, GT crack px, relR denominator) equal across arms and b: {gtsame}')

print('\n## 2 D2 re-derived from the stored val sweep')
H = {}
for k in ARMS:
    sw = {float(b): v for b, v in dec[k]['sweep'].items()}; G = sorted(sw)
    ok = [b for b in G if sw[b]['relR2'] >= 0.90]
    if ok and sw[ok[0]]['relP2'] >= 0.90: b, why = ok[0], 'smallest b relR>=.90 & relP>=.90'
    else: b, why = max(G, key=lambda x: sw[x]['relF1']), 'max relF1'
    drop = sw[0.0]['crack_P'] - sw[b]['crack_P']; hb = 0.0 if drop > 0.05 else b; H[k] = hb
    print(f'  {k}: mine b {b} ({why}), drop {drop:+.4f}, headline {hb} | file b {dec[k]["bias"]} drop {dec[k]["val_crack_precision_drop_at_bias"]:+.4f} '
          f'headline {dec[k]["headline_bias"]} | agree {b == dec[k]["bias"] and hb == dec[k]["headline_bias"]}')
    print('    val sweep relR/relP/crackP: ' + ' '.join(f'{x:g}:{sw[x]["relR2"]:.3f}/{sw[x]["relP2"]:.3f}/{sw[x]["crack_P"]:.3f}' for x in G))
    for bb in U:
        c = J[(k, bb)]['cells']['val']; p = prim(X(c, sorted(c)).sum(0))
        mine = {'crack_iou': p[0], 'relF1': p[1], 'inact_iou': p[2], 'relP2': p[4], 'relR2': p[5], 'crack_P': p[6]}
        print(f'    val cells at b{bb:g} re-summed vs sweep: max |d| {max(abs(mine[q] - sw[bb][q]) for q in mine if q in sw[bb]):.2e}')
pd = json.load(open(PF2E / 'pf2e_val_decisions.json'))['E-PF']
print(f'  E-PF vs PF2E decisions: b {dec["E-PF"]["bias"]} / {pd["bias"]}, headline {dec["E-PF"]["headline_bias"]} / {pd["headline_bias"]}, '
      f'drop {dec["E-PF"]["val_crack_precision_drop_at_bias"]:.6f} / {pd["val_crack_precision_drop_at_bias"]:.6f}')

print('\n## 3 E-PF identity vs PF2E (exact, every split / cell)')
for b in (0.0, 1.5):
    if ('E-PF', b) not in J:
        print(f'  b{b:g}: not written in this run'); continue
    me, pf = J[('E-PF', b)]['cells'], json.load(open(PF2E / f'E-PF.b{b:g}.json'))['cells']
    bad = [(sp, s) for sp in pf for s in pf[sp] if me[sp].get(s) != pf[sp][s]]
    print(f'  b{b:g}: splits {sorted(me) == sorted(pf)}, cells {sum(len(v) for v in pf.values())}, mismatches {len(bad)} {bad[:3]}')

A0, B0 = J[('E-PF', 0.0)]['cells'], J[('E-SKR2', 0.0)]['cells']
test = sorted(A0['test']); clean = [s for s in test if s != NOISY]; ext = sorted(A0['ext'])


def verdict_block(bP, bS, label):
    A, B = J[('E-PF', bP)]['cells'], J[('E-SKR2', bS)]['cells']
    rt = {sn: boot(A['test'], B['test'], st) for sn, st in (('all 50', test), ('clean 49', clean))}
    re1 = boot(A['ext'], B['ext'], ext, key=MOD); rc = boot(A['ext'], B['ext'], ext)
    print(f'\n## {label}: E-SKR2 b {bS:g} vs E-PF b {bP:g}')
    for sn, r in rt.items():
        print(f'  test {sn}: ' + ' | '.join(fmt(r, i) for i in (0, 1, 2)))
        print(f'      reported: ' + ' | '.join(f'{NAMES[i]} {r["full"][i]:+.4f}' for i in (4, 5, 6, 7, 8)) + f' | any-hit {r["full"][3]:+.4f}')
    print(f'  E1 ({re1["n"]} clusters): ' + ' | '.join(fmt(re1, i) for i in (1, 3, 2)))
    print(f'      LOCO range: relF1 [{re1["loo"][:, 1].min():+.4f}, {re1["loo"][:, 1].max():+.4f}] any-hit [{re1["loo"][:, 3].min():+.4f}, '
          f'{re1["loo"][:, 3].max():+.4f}] inact [{re1["loo"][:, 2].min():+.4f}, {re1["loo"][:, 2].max():+.4f}]')
    print(f'      cell-level (unclustered, comparison only): relF1 [{rc["lo"][1]:+.4f}, {rc["hi"][1]:+.4f}] any-hit [{rc["lo"][3]:+.4f}, {rc["hi"][3]:+.4f}]')
    print(f'      reported: ' + ' | '.join(f'{NAMES[i]} {re1["full"][i]:+.4f}' for i in (0, 4, 5, 6, 7, 8)))
    st = {}
    for i in (0, 1, 2):
        a, c = rt['all 50'], rt['clean 49']
        pas = (a['lo'][i] > 0 and c['lo'][i] > 0) or (a['lo'][i] > 0 and c['full'][i] > 0) or (c['lo'][i] > 0 and a['full'][i] > 0)
        fail = a['hi'][i] < 0 or c['hi'][i] < 0
        st['test ' + NAMES[i]] = 'PASS' if pas else ('FAIL' if fail else 'n.d.')
    for i in (1, 3):
        st['E1 ' + NAMES[i]] = 'PASS' if re1['lo'][i] > 0 else ('FAIL' if re1['hi'][i] < 0 else 'n.d.')
    cfA, cfB = crackfree_px(A['ext']), crackfree_px(B['ext'])
    g = {'G2a test relP@2 all 50 < -0.03': (rt['all 50']['full'][4], rt['all 50']['full'][4] < -0.03),
         'G2b E1 crack-free px > 1.5x E-PF': (cfB[1] / max(cfA[1], 1), cfB[1] > 1.5 * cfA[1]),
         'G1t test inact <= -0.015 both sets': ((rt['all 50']['full'][2], rt['clean 49']['full'][2]), rt['all 50']['full'][2] <= -0.015 and rt['clean 49']['full'][2] <= -0.015),
         'G1e E1 inact cluster CI wholly < 0': ((re1['full'][2], re1['hi'][2]), re1['hi'][2] < 0)}
    print(f'  primaries: {st}')
    print(f'  guards (E1 crack-free cells {cfA[0]}/{cfB[0]}; px E-PF {cfA[1]} E-SKR2 {cfB[1]}, bar {1.5 * cfA[1]:.0f}):')
    for kk, (v, t) in g.items():
        print(f'    {kk}: {np.round(v, 4).tolist() if isinstance(v, tuple) else round(float(v), 4)} -> {"TRIP" if t else "ok"}')
    return st, g, rt, re1


st0, g0, rt0, re0 = verdict_block(0.0, 0.0, 'VERDICT b 0 (both arms)')
hp = (H['E-PF'], H['E-SKR2'])
if hp != (0.0, 0.0):
    sth, gh, _, _ = verdict_block(hp[0], hp[1], 'HEADLINE PAIR (guards apply; primaries reported)')
else:
    gh = g0; print(f'\n## HEADLINE PAIR = (0, 0): guards at the headline pair are the b 0 guards')
trip = any(t for _, t in g0.values()) or any(t for _, t in gh.values())
npass = [k for k, v in st0.items() if v == 'PASS']; nfail = [k for k, v in st0.items() if v == 'FAIL']
V = 'FAIL' if (nfail or trip) else ('PASS' if npass else 'n.d.')
print(f'\n## SKR2E VERDICT (judge recompute, protocol §3c): {V}; carried by {npass or "-"}; primary FAIL {nfail or "-"}; guard trip {trip}')
if V == 'PASS' and not any(k.startswith('E1') for k in npass):
    print('   test-only PASS: "SKR2\'s single-model E1 gain is not confirmed at ensemble level" must be said with it')

print('\n## 6 bias share: every arm x b in U (readouts), then all U x U pairs (reported, not a verdict)')
R = {}
for k in ARMS:
    for b in U:
        c = J[(k, b)]['cells']
        t, tc, e = prim(X(c['test'], test).sum(0)), prim(X(c['test'], clean).sum(0)), prim(X(c['ext'], ext).sum(0)); R[(k, b)] = (t, tc, e)
        print(f'  {k} b{b:g}: test crack IoU {t[0]:.4f} (clean {tc[0]:.4f}) relF1 {t[1]:.4f} inact {t[2]:.4f} (clean {tc[2]:.4f}) relP {t[4]:.4f} relR {t[5]:.4f} '
              f'P {t[6]:.4f} pred/GT {t[8]:.3f} | E1 relF1 {e[1]:.4f} any-hit {e[3]:.4f} inact {e[2]:.4f} relP {e[4]:.4f} pred/GT {e[8]:.3f} cf px {crackfree_px(c["ext"])[1]}')
print('  pairs (dS - dP): test crack IoU / relF1 / inact (all 50) | E1 relF1 / any-hit | G2a relP, G2b ratio')
for bS in U:
    for bP in U:
        (tS, _, eS), (tP, _, eP) = R[('E-SKR2', bS)], R[('E-PF', bP)]
        cfr = crackfree_px(J[('E-SKR2', bS)]['cells']['ext'])[1] / max(crackfree_px(J[('E-PF', bP)]['cells']['ext'])[1], 1)
        print(f'    SKR2 b{bS:g} - PF b{bP:g}: {tS[0] - tP[0]:+.4f} / {tS[1] - tP[1]:+.4f} / {tS[2] - tP[2]:+.4f} | {eS[1] - eP[1]:+.4f} / {eS[3] - eP[3]:+.4f} | '
              f'{tS[4] - tP[4]:+.4f}, x{cfr:.2f}')
sw = json.load(open(D / 'skr2e_e1_sweep.json'))
print('  E1 aggregate sweep (reported only; re-checked at U from the cells):')
for k in ARMS:
    s = {float(b): v for b, v in sw[k].items()}
    print(f'    {k}: ' + ' '.join(f'{b:g}:{s[b]["relF1"]:.3f}/{s[b]["anyhit"]:.3f}/{s[b]["pred_over_gt"]:.2f}/{s[b]["crack_free_px"]}' for b in sorted(s)) + '  (relF1/any-hit/predGT/cf px)')
    for b in U:
        e = R[(k, b)][2]; print(f'      at b{b:g}: sweep vs cells relF1 {s[b]["relF1"] - e[1]:+.1e} any-hit {s[b]["anyhit"] - e[3]:+.1e} pred/GT {s[b]["pred_over_gt"] - e[8]:+.1e} '
                               f'cf px {s[b]["crack_free_px"] - crackfree_px(J[(k, b)]["cells"]["ext"])[1]:+d}')
sP = {float(b): v for b, v in sw['E-PF'].items()}; sS = {float(b): v for b, v in sw['E-SKR2'].items()}
gap = (sS[0.0]['relF1'] - sP[0.0]['relF1'], sS[0.0]['anyhit'] - sP[0.0]['anyhit'])
print(f'  b 0 E1 gap: relF1 {gap[0]:+.4f}, any-hit {gap[1]:+.4f}. E-PF own bias gain over b (relF1 / any-hit): ' +
      ' '.join(f'{b:g}:{sP[b]["relF1"] - sP[0.0]["relF1"]:+.3f}/{sP[b]["anyhit"] - sP[0.0]["anyhit"]:+.3f}' for b in GRID))
bs = sorted(sP); r = sS[0.0]['pred_over_gt']; v = [sP[b]['pred_over_gt'] for b in bs]
print(f'  E1 volume at b 0: E-SKR2 pred/GT {r:.4f}, E-PF {v[0]:.4f}')
if r <= v[0]:
    print('  matched volume: E-SKR2 at b 0 is not wider than E-PF at b 0 -> the gap is not a volume (bias) effect')
elif r > v[-1]:
    print('  matched volume: beyond E-PF\'s grid (b 3)')
else:
    j = max(i for i in range(len(bs) - 1) if v[i] <= r); t = (r - v[j]) / (v[j + 1] - v[j])
    ip = lambda q: sP[bs[j]][q] + t * (sP[bs[j + 1]][q] - sP[bs[j]][q])
    bm = bs[j] + t * (bs[j + 1] - bs[j])
    print(f'  matched volume: E-PF at b {bm:.3f} (interp {bs[j]:g}-{bs[j + 1]:g}) relF1 {ip("relF1"):.4f} any-hit {ip("anyhit"):.4f} -> '
          f'gap at matched volume relF1 {sS[0.0]["relF1"] - ip("relF1"):+.4f} ({(sS[0.0]["relF1"] - ip("relF1")) / gap[0] * 100 if gap[0] else float("nan"):.0f}% of the b 0 gap left), '
          f'any-hit {sS[0.0]["anyhit"] - ip("anyhit"):+.4f}')
tS0, tP0 = R[('E-SKR2', 0.0)][0], R[('E-PF', 0.0)][0]
print(f'  test volume at b 0: E-SKR2 pred/GT {tS0[8]:.4f}, E-PF {tP0[8]:.4f}; E-PF at U b: ' + ', '.join(f'b{b:g} {R[("E-PF", b)][0][8]:.4f} crack IoU {R[("E-PF", b)][0][0]:.4f} relF1 {R[("E-PF", b)][0][1]:.4f}' for b in U))

print('\n## 7 any-hit concentration at b 0 (E1)')
CA, CB, gs = re0['CA'], re0['CB'], re0['groups']
n, hA, hB = CA[:, 11], CA[:, 10], CB[:, 10]; dh = hB - hA
print(f'  GT comps {int(n.sum())} in {int((n > 0).sum())} of {len(gs)} images; n_eff images (GT comps) {n.sum() ** 2 / (n ** 2).sum():.1f}; '
      f'hits E-PF {int(hA.sum())} E-SKR2 {int(hB.sum())} (gap {int(dh.sum()):+d})')
o = np.argsort(-n)
print('  top images by GT comps (n, hits PF, hits SKR2, d): ' + '; '.join(f'{gs[i]} {int(n[i])} {int(hA[i])} {int(hB[i])} {int(dh[i]):+d}' for i in o[:10]))
print(f'  top-3 / top-10 share of GT comps {n[o[:3]].sum() / n.sum():.3f} / {n[o[:10]].sum() / n.sum():.3f}; '
      f'images with d>0 {int((dh > 0).sum())}, d<0 {int((dh < 0).sum())}, d=0 (with comps) {int(((dh == 0) & (n > 0)).sum())}')
od = np.argsort(-np.abs(dh)); ad = np.abs(dh)
print(f'  |d| gross {int(ad.sum())}; top-3 |d| images ' + ', '.join(f'{gs[i]} {int(dh[i]):+d}' for i in od[:3]) +
      f' share of gross {ad[od[:3]].sum() / max(ad.sum(), 1):.3f}; n_eff of |d| {ad.sum() ** 2 / max((ad ** 2).sum(), 1):.1f}')
keep = np.setdiff1d(np.arange(len(gs)), o[:3])
print(f'  leave-top-3-GT-images-out any-hit: E-PF {hA[keep].sum() / n[keep].sum():.4f} E-SKR2 {hB[keep].sum() / n[keep].sum():.4f} d {(hB[keep].sum() - hA[keep].sum()) / n[keep].sum():+.4f} (n {int(n[keep].sum())})')
XA, XB = X(A0['ext'], ext), X(B0['ext'], ext)
for nm, f in (('scuff+half-cut 29', lambda s: ctx[s][1] == 'scuff_halfcut'), ('other 77', lambda s: ctx[s][1] != 'scuff_halfcut'),
              ('half-cut 58', lambda s: ctx[s][3] == 'halfcut=1'), ('full 48', lambda s: ctx[s][3] != 'halfcut=1')):
    ix = [i for i, s in enumerate(ext) if f(s)]; a, b = XA[ix].sum(0), XB[ix].sum(0); pa, pb = prim(a), prim(b)
    print(f'  {nm} ({len(ix)} cells): comps {int(a[11])}, hits {int(a[10])} -> {int(b[10])} (any-hit {pa[3]:.4f} -> {pb[3]:.4f}); relF1 {pa[1]:.4f} -> {pb[1]:.4f}; '
          f'inact {pa[2]:.4f} -> {pb[2]:.4f}; crack R {pa[7]:.4f} -> {pb[7]:.4f}')
