"""PF2E verdict scorer (protocol_PF2E.md §3-4), CPU, on pf2e_infer.py's per-cell JSONs.
Test: paired image bootstrap of E-PF - E-g (Track M m1_analyze.boot, imported unchanged: 2,000 resamples, seed 0, rng.integers
over cells, 2.5 / 97.5 percentiles), at each ensemble's headline b (the verdict b), sets all 50 and clean (-CSIR_00070_r8_c4);
-twins / -both reported. Primaries crack IoU, relF1@2, inactive IoU (m1_analyze.prim_from order: crack IoU, inactive IoU,
relF1, mIoU_rob; mIoU_rob reported only). PASS: a 95% CI excludes 0 on >= 1 primary in both sets, or in one set with a
same-sign estimate in the other; FAIL: any primary's CI wholly below 0 in either set; else n.d.
E1 co-primaries: crack relF1@2 and inactive IoU (all 106), paired MODULE-CLUSTER bootstrap (2,000, seed 0): cluster = stem
without its _rN_cM / _cellN suffix (71 clusters asserted); clusters resampled with replacement, all their cells pooled.
Same pass / fail wording, one set. Reported: b 0, test_noscuff, per source, crack capture, crack-free px, E1 strata.
Usage: python pf2e_boot.py DIR E1_CONTEXT [--singles PF2_M0_DIR]    |    python pf2e_boot.py --selftest PF2_M0_DIR EXT_STEMS_EVAL_TXT
"""
import json, re, sys
from pathlib import Path

import numpy as np

sys.path.insert(0, '/home/yugma/mtp/research/team_2026-10-24_go/trackM/scripts')
import m1_analyze as M1  # noqa: E402  (boot, counts, prim_from; module constants NC / TL)
from m0_analyze import agg, TWINS, NOISY  # noqa: E402

PN = ["crack IoU", "inactive IoU", "relF1@2", "mIoU_rob"]; PRIM_IX = [0, 2, 1]  # the 3 protocol primaries, in protocol order


def verdict(rows):  # rows: {set: (full, lo, hi)} over the 3 primaries
    worse = any(rows[s][2][i] < 0 for s in rows for i in PRIM_IX)
    if worse:
        return "FAIL (a primary's CI wholly below 0)"
    sets = list(rows)
    for i in PRIM_IX:
        ex = {s: rows[s][1][i] > 0 for s in sets}
        if all(ex.values()) or (any(ex.values()) and all(rows[s][0][i] > 0 for s in sets)):
            return f"PASS ({PN[i]})"
    return "n.d."


MODULE = lambda s: re.sub(r'(_r\d+_c\d+|_cell\d+)$', '', s)  # cluster = source image (stem without its cell suffix)


def cluster_boot(cA, cB, stems, n=2000, seed=0, key=MODULE):
    cl = sorted({key(s) for s in stems}); idx = {c: [i for i, s in enumerate(stems) if key(s) == c] for c in cl}
    CA, RA = M1.counts(cA, stems); CB, RB = M1.counts(cB, stems)
    full = M1.prim_from(CB.sum(0), RB.sum(0)) - M1.prim_from(CA.sum(0), RA.sum(0))
    rng = np.random.default_rng(seed); out = np.empty((n, 4))
    for t in range(n):
        ix = np.concatenate([idx[cl[j]] for j in rng.integers(0, len(cl), len(cl))])
        out[t] = M1.prim_from(CB[ix].sum(0), RB[ix].sum(0)) - M1.prim_from(CA[ix].sum(0), RA[ix].sum(0))
    lo, hi = np.nanpercentile(out, [2.5, 97.5], 0)
    return full, lo, hi, np.nanmean(out > 0, 0), len(cl)


if '--selftest' in sys.argv:  # on already-opened PF2 per-cell files (test split; PF2 opening 1 Nov): no new model read
    d = Path(sys.argv[sys.argv.index('--selftest') + 1])
    A = json.load(open(d / 'pf2_SUP_100pct_s5.json'))['cells']['test']; B = json.load(open(d / 'pf2_SUPPF_100pct_s5.json'))['cells']['test']
    st = sorted(A); r1 = M1.boot([A], [B], st); r2 = M1.boot([A], [B], st)
    det = all(np.array_equal(x, y, equal_nan=True) for x, y in zip(r1, r2))
    # (1) one cell per cluster: cluster_boot must reproduce Track M m1_analyze.boot EXACTLY (same draws, same percentiles)
    c1 = cluster_boot(A, B, st, key=lambda s: s)
    eq = all(np.array_equal(x, y, equal_nan=True) for x, y in zip(r1, c1[:4])) and c1[4] == len(st)
    # (2) module clusters on test: point estimate = boot's (pooled counts do not depend on the grouping); CI differs
    c2 = cluster_boot(A, B, st)
    full_eq = np.array_equal(c2[0], r1[0], equal_nan=True)
    # (3) a cluster draw pools ALL cells of the drawn cluster: duplicate every cell into 2 copies under one cluster each;
    #     the cluster bootstrap over the copies must equal boot over the originals (counts doubled, ratios unchanged)
    A2 = {f'{s}_dup{j}': v for s, v in A.items() for j in (0, 1)}; B2 = {f'{s}_dup{j}': v for s, v in B.items() for j in (0, 1)}
    c3 = cluster_boot(A2, B2, sorted(A2), key=lambda s: s.rsplit('_dup', 1)[0])
    dup = all(np.allclose(x, y, equal_nan=True, rtol=0, atol=1e-12) for x, y in zip(r1, c3[:4])) and c3[4] == len(st)
    # (4) E1 grouping from the stem list only (no E1 score read): 71 clusters
    ext = [l.strip() for l in open(sys.argv[sys.argv.index('--selftest') + 2]) if l.strip()]
    ncl = len({MODULE(s) for s in ext})
    print(f'selftest: m1_analyze.boot deterministic {det} | (1) singleton cluster_boot == m1_analyze.boot exactly {eq} | '
          f'(2) module-cluster full == boot full {full_eq} (test clusters {c2[4]}) | (3) 2-cell clusters == boot on originals {dup} | '
          f'(4) E1 stems {len(ext)}, module clusters {ncl} (expect 106 / 71)')
    ok = det and eq and full_eq and dup and len(ext) == 106 and ncl == 71
    print('SELFTEST', 'PASS' if ok else 'FAIL'); sys.exit(0 if ok else 1)

D = Path(sys.argv[1]); ctx = {l.split('\t')[0]: l.rstrip('\n').split('\t')[1:] for l in open(sys.argv[2]) if l.strip()}
dec = json.load(open(D / 'pf2e_val_decisions.json'))
hb = {k: dec[k]['headline_bias'] for k in ('E-g', 'E-PF')}
J = {(k, b): json.load(open(D / f'{k}.b{b:g}.json')) for k in ('E-g', 'E-PF') for b in sorted({0.0, dec[k]['bias'], hb[k]})}
print(f"# PF2E: E-PF - E-g. Val decisions (pf2e_val_decisions.json): E-g b {dec['E-g']['bias']} ({dec['E-g']['why']}; precision drop "
      f"{dec['E-g']['val_crack_precision_drop_at_bias']:+.4f}; headline {hb['E-g']}); E-PF b {dec['E-PF']['bias']} ({dec['E-PF']['why']}; "
      f"drop {dec['E-PF']['val_crack_precision_drop_at_bias']:+.4f}; headline {hb['E-PF']})")
SETS = {'all 50': lambda s: True, 'clean 49': lambda s: s != NOISY, '-twins': lambda s: s not in TWINS, '-both': lambda s: s not in TWINS and s != NOISY}
for tag, (bg, bp) in (('VERDICT (headline b)', (hb['E-g'], hb['E-PF'])), ('reported: b 0', (0.0, 0.0))):
    for split in ('test', 'test_noscuff'):
        A = J[('E-g', bg)]['cells'][split]; B = J[('E-PF', bp)]['cells'][split]; rows = {}
        print(f"\n## {split}, {tag}: E-g b {bg} vs E-PF b {bp}; paired image bootstrap 2,000, seed 0 (Track M m1_analyze.boot)")
        for sn, f in SETS.items():
            st = sorted(s for s in A if f(s)); full, lo, hi, pp = M1.boot([A], [B], st)
            ga, gb = agg(A, f), agg(B, f)
            print(f"  {sn:9s} | " + " | ".join(f"{PN[i]} {full[i]:+.4f} [{lo[i]:+.4f}, {hi[i]:+.4f}] P>0 {pp[i]:.2f}" for i in PRIM_IX + [3])
                  + f" | E-g crack IoU {ga['iou'][14]:.4f} relF1 {ga['relF1']:.4f} inact {ga['iou'][11]:.4f} | E-PF {gb['iou'][14]:.4f} {gb['relF1']:.4f} {gb['iou'][11]:.4f}"
                  + f" | relR2 {ga['relR2']:.3f}->{gb['relR2']:.3f} relP2 {ga['relP2']:.3f}->{gb['relP2']:.3f} comp R {ga['cc_rec50_20']:.3f}->{gb['cc_rec50_20']:.3f} comp P {ga['cc_prec_20']:.3f}->{gb['cc_prec_20']:.3f}")
            if sn in ('all 50', 'clean 49'):
                rows[sn] = (full, lo, hi)
        print(f"  => {split} {tag}: {verdict(rows)}" + ("" if split == 'test' and tag.startswith('VERDICT') else "  (reported only)"))
        if split == 'test':
            src = sorted({s.split('_')[0] for s in A})
            print("  per source (E-g -> E-PF): " + "; ".join(
                f"{p} n {agg(A, lambda s, p=p: s.startswith(p))['n']} crack IoU {agg(A, lambda s, p=p: s.startswith(p))['iou'][14]:.3f}->{agg(B, lambda s, p=p: s.startswith(p))['iou'][14]:.3f} "
                f"inact {agg(A, lambda s, p=p: s.startswith(p))['iou'][11]:.3f}->{agg(B, lambda s, p=p: s.startswith(p))['iou'][11]:.3f}" for p in src))
    A = J[('E-g', bg)]['cells']['ext']; B = J[('E-PF', bp)]['cells']['ext']; st = sorted(A); assert len(st) == 106
    full, lo, hi, pp, ncl = cluster_boot(A, B, st); assert ncl == 71, ncl
    ga, gb = agg(A, lambda s: True), agg(B, lambda s: True)
    print(f"\n## E1 (106 cells, {ncl} module clusters), {tag}: paired module-cluster bootstrap 2,000, seed 0")
    print(f"  E1 crack relF1@2 {full[2]:+.4f} [{lo[2]:+.4f}, {hi[2]:+.4f}] P>0 {pp[2]:.2f} (E-g {ga['relF1']:.4f}, E-PF {gb['relF1']:.4f}) | "
          f"E1 inactive IoU {full[1]:+.4f} [{lo[1]:+.4f}, {hi[1]:+.4f}] P>0 {pp[1]:.2f} (E-g {ga['iou'][11]:.4f}, E-PF {gb['iou'][11]:.4f})")
    w = 'FAIL' if (hi[2] < 0 or hi[1] < 0) else ('PASS (' + ', '.join(n for n, i in (('E1 crack relF1@2', 2), ('E1 inactive IoU', 1)) if lo[i] > 0) + ')' if (lo[2] > 0 or lo[1] > 0) else 'n.d.')
    print(f"  => E1 {tag}: {w}" + ("" if tag.startswith('VERDICT') else "  (reported only)"))
    print("  E1 reported: crack R " + f"{ga['rec'][14]:.3f}->{gb['rec'][14]:.3f}, P {ga['prec'][14]:.3f}->{gb['prec'][14]:.3f}, relR2 {ga['relR2']:.3f}->{gb['relR2']:.3f}, "
          f"relP2 {ga['relP2']:.3f}->{gb['relP2']:.3f}, comp R {ga['cc_rec50_20']:.3f}->{gb['cc_rec50_20']:.3f}, comp P {ga['cc_prec_20']:.3f}->{gb['cc_prec_20']:.3f}")
    GR = (('scuff+half-cut', lambda s: ctx[s][0] == 'scuff_halfcut'), ('other', lambda s: ctx[s][0] == 'other'),
          ('half-cut', lambda s: ctx[s][2] == 'halfcut=1'), ('full', lambda s: ctx[s][2] == 'halfcut=0'))
    for gn, f in GR:  # E1 strata + width checks (relR@2 / relP@2 / relF1@2, component R / P), as pf2_e1_width.py, via m0_analyze.agg
        a_, b_ = agg(A, f), agg(B, f)
        print(f"  E1 stratum {gn} n {a_['n']}: crack R {a_['rec'][14]:.3f}->{b_['rec'][14]:.3f} inact IoU {a_['iou'][11]:.3f}->{b_['iou'][11]:.3f} "
              f"relR2 {a_['relR2']:.3f}->{b_['relR2']:.3f} relP2 {a_['relP2']:.3f}->{b_['relP2']:.3f} relF1 {a_['relF1']:.3f}->{b_['relF1']:.3f} "
              f"comp R {a_['cc_rec50_20']:.3f}->{b_['cc_rec50_20']:.3f} comp P {a_['cc_prec_20']:.3f}->{b_['cc_prec_20']:.3f}")
    for sp in ('test', 'val', 'ext'):
        cf = lambda cs: [np.array(v['conf']).reshape(24, 24) for v in cs.values() if np.array(v['conf']).reshape(24, 24)[14].sum() == 0]
        a_, b_ = cf(J[('E-g', bg)]['cells'][sp]), cf(J[('E-PF', bp)]['cells'][sp])
        print(f"  crack px on crack-free {sp} cells ({len(a_)}): E-g {int(sum(C[:, 14].sum() for C in a_))}, E-PF {int(sum(C[:, 14].sum() for C in b_))}")
if '--singles' in sys.argv:  # descriptive (protocol_PF2E §1): ensembles vs the PF2 single-seed means (already-opened m0 JSONs, argmax)
    sd = Path(sys.argv[sys.argv.index('--singles') + 1]); print("\n## reported: ensemble (headline b) vs PF2 single-seed mean +- sd (argmax), descriptive")
    for k, arm in (('E-g', 'SUP'), ('E-PF', 'SUPPF')):
        S = [json.load(open(sd / f'pf2_{arm}_100pct_s{q}.json'))['cells'] for q in range(5, 10)]
        for sp, f, nm in (('test', lambda s: True, 'test all 50'), ('test', lambda s: s != NOISY, 'test clean 49'), ('ext', lambda s: True, 'E1 106')):
            v = np.array([[g['iou'][14], g['relF1'], g['iou'][11]] for g in (agg(c[sp], f) for c in S)])
            e = agg(J[(k, hb[k])]['cells'][sp], f)
            print(f"  {k} {nm}: crack IoU {e['iou'][14]:.4f} vs {v[:, 0].mean():.4f} +- {v[:, 0].std(ddof=1):.4f} | relF1@2 {e['relF1']:.4f} vs "
                  f"{v[:, 1].mean():.4f} +- {v[:, 1].std(ddof=1):.4f} | inactive IoU {e['iou'][11]:.4f} vs {v[:, 2].mean():.4f} +- {v[:, 2].std(ddof=1):.4f}")
print("\nFINAL (cv02, R34 5-seed ensemble, b +0.75) clean-test crack IoU 0.492: descriptive only (other machine and commits).")
