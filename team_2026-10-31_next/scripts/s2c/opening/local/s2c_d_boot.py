"""SKR2C verdict D scorer (protocol_SKR2C §3b, §3c, §4; laptop, after the pull) = skr2e_boot.py 7520afc0 with: labels LA_ / LB_ as
module globals (default E-PF / E-SKR2, so the self-tests reproduce #6 verbatim; the SKR2C run uses E-SUPPF / E-SKR2 = E-SUPPF' / E-SKR2');
ONE verdict pair (both arms at b 0), guards at that pair only (no headline pair, no U x U grid); the matched-val-volume pair (E-SUPPF b 0 vs
E-SKR2 b_mv) reported with CIs; the E1 aggregate sweep lines; SKR2C §3b fixed wording (dverdict); singles = R's fresh s10-14 m0; --json
of the D result; self-test (5) reproduces #6's b 0 pair, E1 concentration and matched-volume blocks from #6's files, (6) the wording on
synthetic rows. Usage: python s2c_d_boot.py D_RAW_DIR E1_CONTEXT [--singles R_M0_SUPPF R_M0_SKR01] [--json OUT]
       python s2c_d_boot.py --selftest PF2E_DIR PF2E_BOOT_TXT E1_CONTEXT PF2_M0_DIR SKR2E_RAW_DIR SKR2E_BOOT_TXT
Original docstring follows.
SKR2E verdict scorer (protocol_SKR2E.md v1 §2-4, locked cbc3e015), CPU, on skr2e_infer.py's per-cell JSONs.
= pf2e_boot.py bee9e182 (functions verdict / MODULE / cluster_boot and its print formats kept verbatim; its report is kept as
pf2e_report() for the reproduction self-test) PLUS:
- E1 any-hit component recall (protocol_SKR2_HC2 §3a.3 = m0_analyze.agg cc_recany_20) as a 5th bootstrap column:
  cluster_boot5 = cluster_boot with the same RNG draws; any-hit = ratio of the POOLED component counts (hits / GT comps >= 20 px)
  over the resampled clusters' cells; columns 0-3 are cluster_boot's exactly (no extra RNG use).
- Contrast E-SKR2 - E-PF. VERDICT at b 0 for both arms (§2, D1). Test primaries crack IoU / relF1@2 / inactive IoU, paired image
  bootstrap (Track M m1_analyze.boot unchanged), sets all 50 + clean 49 (pf2e verdict(): pass = CI above 0 in both sets, or in one
  set with a same-sign estimate in the other; fail = CI wholly below 0 in either set). E1 co-primaries crack relF1@2 and any-hit,
  module-cluster bootstrap (2,000, seed 0, 71 clusters asserted): pass = CI above 0, fail = CI below 0.
- Guards (§3b; point estimates unless stated), each at b 0 AND at the headline pair (E-SKR2 at its headline b vs E-PF at its
  headline b); a trip at either FAILS: G2a test crack relP@2 delta (all 50) < -0.03; G2b E-SKR2 crack px on E1's crack-free cells
  (GT crack px 0, 74 asserted) > 1.5 x E-PF's; G1t test inactive IoU delta <= -0.015 in both sets; G1e E1 inactive IoU delta with
  module-cluster CI wholly below 0.
- Overall (§3c): PASS = >= 1 primary passes, none fails, no guard trips; FAIL = any primary fails or any guard trips; else n.d.;
  fixed wording lines.
- §4 readouts at every pair in U x U (U = union of written b's): four cell sets, per source, crack capture (relR / relP @2, pixel
  P / R, component R / P, any-hit on test), width (pred / GT crack px, test and E1), crack px on crack-free cells (test, val, E1),
  test_noscuff, E1 strata (29 / 29 / 48; 58 / 48; 29 / 77), E1 concentration (inactive px and any-hit comps per image, top 3 /
  top 10, n_eff; leave-top-3-images-out deltas), leave-one-cluster-out range of each E1 co-primary, matched-volume line from
  skr2e_e1_sweep.json (E1-oracle, descriptive), singles vs ensemble, FINAL line. B5 / cell-level: not in this script.
Usage: python skr2e_boot.py DIR E1_CONTEXT [--singles PF2_M0_DIR S2_M0_SKR01_DIR]
       python skr2e_boot.py --selftest PF2E_DIR PF2E_BOOT_TXT E1_CONTEXT PF2_M0_DIR
"""
import json, re, sys
from pathlib import Path

import numpy as np

sys.path.insert(0, '/home/yugma/mtp/research/team_2026-10-24_go/trackM/scripts')
import m1_analyze as M1  # noqa: E402  (boot, counts, prim_from; module constants NC / TL)
from m0_analyze import agg, TWINS, NOISY  # noqa: E402

PN = ["crack IoU", "inactive IoU", "relF1@2", "mIoU_rob"]; PRIM_IX = [0, 2, 1]  # the 3 protocol primaries, in protocol order


def verdict(rows):  # rows: {set: (full, lo, hi)} over the 3 primaries  (pf2e_boot bee9e182, verbatim)
    worse = any(rows[s][2][i] < 0 for s in rows for i in PRIM_IX)
    if worse:
        return "FAIL (a primary's CI wholly below 0)"
    sets = list(rows)
    for i in PRIM_IX:
        ex = {s: rows[s][1][i] > 0 for s in sets}
        if all(ex.values()) or (any(ex.values()) and all(rows[s][0][i] > 0 for s in sets)):
            return f"PASS ({PN[i]})"
    return "n.d."


def passing(rows):  # SKR2E: names EVERY test primary that passes by verdict()'s rule (verdict() names only the first)
    out = []
    for i in PRIM_IX:
        ex = {s: rows[s][1][i] > 0 for s in rows}
        if all(ex.values()) or (any(ex.values()) and all(rows[s][0][i] > 0 for s in rows)):
            out.append(PN[i])
    return out


MODULE = lambda s: re.sub(r'(_r\d+_c\d+|_cell\d+)$', '', s)  # cluster = source image (stem without its cell suffix)


def cluster_boot(cA, cB, stems, n=2000, seed=0, key=MODULE):  # pf2e_boot bee9e182, verbatim (kept for the self-test)
    cl = sorted({key(s) for s in stems}); idx = {c: [i for i, s in enumerate(stems) if key(s) == c] for c in cl}
    CA, RA = M1.counts(cA, stems); CB, RB = M1.counts(cB, stems)
    full = M1.prim_from(CB.sum(0), RB.sum(0)) - M1.prim_from(CA.sum(0), RA.sum(0))
    rng = np.random.default_rng(seed); out = np.empty((n, 4))
    for t in range(n):
        ix = np.concatenate([idx[cl[j]] for j in rng.integers(0, len(cl), len(cl))])
        out[t] = M1.prim_from(CB[ix].sum(0), RB[ix].sum(0)) - M1.prim_from(CA[ix].sum(0), RA[ix].sum(0))
    lo, hi = np.nanpercentile(out, [2.5, 97.5], 0)
    return full, lo, hi, np.nanmean(out > 0, 0), len(cl)


def hcounts(cells, stems):  # per cell [any-hit comps, GT crack comps >= 20 px] (hit = px within 2 px of a prediction)
    return np.array([[sum(1 for c in cells[s]["crack_cc"]["gt"] if c[0] >= 20 and c[1] >= 1),
                      sum(1 for c in cells[s]["crack_cc"]["gt"] if c[0] >= 20)] for s in stems], np.int64).reshape(len(stems), 2)


def m5(C, R, H):  # prim_from's 4 values + any-hit ratio of pooled counts
    h = H.sum(0)
    return np.append(M1.prim_from(C.sum(0), R.sum(0)), h[0] / h[1] if h[1] else np.nan)


def cluster_boot5(cA, cB, stems, n=2000, seed=0, key=MODULE):  # cluster_boot + any-hit column; same draws (one rng call per resample)
    cl = sorted({key(s) for s in stems}); idx = {c: [i for i, s in enumerate(stems) if key(s) == c] for c in cl}
    CA, RA = M1.counts(cA, stems); CB, RB = M1.counts(cB, stems); HA, HB = hcounts(cA, stems), hcounts(cB, stems)
    full = m5(CB, RB, HB) - m5(CA, RA, HA)
    rng = np.random.default_rng(seed); out = np.empty((n, 5))
    for t in range(n):
        ix = np.concatenate([idx[cl[j]] for j in rng.integers(0, len(cl), len(cl))])
        out[t] = m5(CB[ix], RB[ix], HB[ix]) - m5(CA[ix], RA[ix], HA[ix])
    lo, hi = np.nanpercentile(out, [2.5, 97.5], 0)
    return full, lo, hi, np.nanmean(out > 0, 0), len(cl)


LA_, LB_ = 'E-PF', 'E-SKR2'  # output labels and sweep keys (SKR2E's by default, so the self-tests reproduce #6 verbatim)
SETS = {'all 50': lambda s: True, 'clean 49': lambda s: s != NOISY, '-twins': lambda s: s not in TWINS, '-both': lambda s: s not in TWINS and s != NOISY}
cfree = lambda cs: [np.array(v['conf']).reshape(24, 24) for v in cs.values() if np.array(v['conf']).reshape(24, 24)[14].sum() == 0]
cfpx = lambda cs: int(sum(C[:, 14].sum() for C in cfree(cs)))


def pf2e_report(D, ctx, singles=None, cb=cluster_boot):  # pf2e_boot bee9e182's report (l.76-132), print() -> lines; cb = E1 bootstrap
    O = []; pr = O.append
    dec = json.load(open(D / 'pf2e_val_decisions.json'))
    hb = {k: dec[k]['headline_bias'] for k in ('E-g', 'E-PF')}
    J = {(k, b): json.load(open(D / f'{k}.b{b:g}.json')) for k in ('E-g', 'E-PF') for b in sorted({0.0, dec[k]['bias'], hb[k]})}
    pr(f"# PF2E: E-PF - E-g. Val decisions (pf2e_val_decisions.json): E-g b {dec['E-g']['bias']} ({dec['E-g']['why']}; precision drop "
       f"{dec['E-g']['val_crack_precision_drop_at_bias']:+.4f}; headline {hb['E-g']}); E-PF b {dec['E-PF']['bias']} ({dec['E-PF']['why']}; "
       f"drop {dec['E-PF']['val_crack_precision_drop_at_bias']:+.4f}; headline {hb['E-PF']})")
    for tag, (bg, bp) in (('VERDICT (headline b)', (hb['E-g'], hb['E-PF'])), ('reported: b 0', (0.0, 0.0))):
        for split in ('test', 'test_noscuff'):
            A = J[('E-g', bg)]['cells'][split]; B = J[('E-PF', bp)]['cells'][split]; rows = {}
            pr(f"\n## {split}, {tag}: E-g b {bg} vs E-PF b {bp}; paired image bootstrap 2,000, seed 0 (Track M m1_analyze.boot)")
            for sn, f in SETS.items():
                st = sorted(s for s in A if f(s)); full, lo, hi, pp = M1.boot([A], [B], st)
                ga, gb = agg(A, f), agg(B, f)
                pr(f"  {sn:9s} | " + " | ".join(f"{PN[i]} {full[i]:+.4f} [{lo[i]:+.4f}, {hi[i]:+.4f}] P>0 {pp[i]:.2f}" for i in PRIM_IX + [3])
                   + f" | E-g crack IoU {ga['iou'][14]:.4f} relF1 {ga['relF1']:.4f} inact {ga['iou'][11]:.4f} | E-PF {gb['iou'][14]:.4f} {gb['relF1']:.4f} {gb['iou'][11]:.4f}"
                   + f" | relR2 {ga['relR2']:.3f}->{gb['relR2']:.3f} relP2 {ga['relP2']:.3f}->{gb['relP2']:.3f} comp R {ga['cc_rec50_20']:.3f}->{gb['cc_rec50_20']:.3f} comp P {ga['cc_prec_20']:.3f}->{gb['cc_prec_20']:.3f}")
                if sn in ('all 50', 'clean 49'):
                    rows[sn] = (full, lo, hi)
            pr(f"  => {split} {tag}: {verdict(rows)}" + ("" if split == 'test' and tag.startswith('VERDICT') else "  (reported only)"))
            if split == 'test':
                src = sorted({s.split('_')[0] for s in A})
                pr("  per source (E-g -> E-PF): " + "; ".join(
                    f"{p} n {agg(A, lambda s, p=p: s.startswith(p))['n']} crack IoU {agg(A, lambda s, p=p: s.startswith(p))['iou'][14]:.3f}->{agg(B, lambda s, p=p: s.startswith(p))['iou'][14]:.3f} "
                    f"inact {agg(A, lambda s, p=p: s.startswith(p))['iou'][11]:.3f}->{agg(B, lambda s, p=p: s.startswith(p))['iou'][11]:.3f}" for p in src))
        A = J[('E-g', bg)]['cells']['ext']; B = J[('E-PF', bp)]['cells']['ext']; st = sorted(A); assert len(st) == 106
        full, lo, hi, pp, ncl = cb(A, B, st); assert ncl == 71, ncl
        ga, gb = agg(A, lambda s: True), agg(B, lambda s: True)
        pr(f"\n## E1 (106 cells, {ncl} module clusters), {tag}: paired module-cluster bootstrap 2,000, seed 0")
        pr(f"  E1 crack relF1@2 {full[2]:+.4f} [{lo[2]:+.4f}, {hi[2]:+.4f}] P>0 {pp[2]:.2f} (E-g {ga['relF1']:.4f}, E-PF {gb['relF1']:.4f}) | "
           f"E1 inactive IoU {full[1]:+.4f} [{lo[1]:+.4f}, {hi[1]:+.4f}] P>0 {pp[1]:.2f} (E-g {ga['iou'][11]:.4f}, E-PF {gb['iou'][11]:.4f})")
        w = 'FAIL' if (hi[2] < 0 or hi[1] < 0) else ('PASS (' + ', '.join(n for n, i in (('E1 crack relF1@2', 2), ('E1 inactive IoU', 1)) if lo[i] > 0) + ')' if (lo[2] > 0 or lo[1] > 0) else 'n.d.')
        pr(f"  => E1 {tag}: {w}" + ("" if tag.startswith('VERDICT') else "  (reported only)"))
        pr("  E1 reported: crack R " + f"{ga['rec'][14]:.3f}->{gb['rec'][14]:.3f}, P {ga['prec'][14]:.3f}->{gb['prec'][14]:.3f}, relR2 {ga['relR2']:.3f}->{gb['relR2']:.3f}, "
           f"relP2 {ga['relP2']:.3f}->{gb['relP2']:.3f}, comp R {ga['cc_rec50_20']:.3f}->{gb['cc_rec50_20']:.3f}, comp P {ga['cc_prec_20']:.3f}->{gb['cc_prec_20']:.3f}")
        GR = (('scuff+half-cut', lambda s: ctx[s][0] == 'scuff_halfcut'), ('other', lambda s: ctx[s][0] == 'other'),
              ('half-cut', lambda s: ctx[s][2] == 'halfcut=1'), ('full', lambda s: ctx[s][2] == 'halfcut=0'))
        for gn, f in GR:
            a_, b_ = agg(A, f), agg(B, f)
            pr(f"  E1 stratum {gn} n {a_['n']}: crack R {a_['rec'][14]:.3f}->{b_['rec'][14]:.3f} inact IoU {a_['iou'][11]:.3f}->{b_['iou'][11]:.3f} "
               f"relR2 {a_['relR2']:.3f}->{b_['relR2']:.3f} relP2 {a_['relP2']:.3f}->{b_['relP2']:.3f} relF1 {a_['relF1']:.3f}->{b_['relF1']:.3f} "
               f"comp R {a_['cc_rec50_20']:.3f}->{b_['cc_rec50_20']:.3f} comp P {a_['cc_prec_20']:.3f}->{b_['cc_prec_20']:.3f}")
        for sp in ('test', 'val', 'ext'):
            a_, b_ = cfree(J[('E-g', bg)]['cells'][sp]), cfree(J[('E-PF', bp)]['cells'][sp])
            pr(f"  crack px on crack-free {sp} cells ({len(a_)}): E-g {int(sum(C[:, 14].sum() for C in a_))}, E-PF {int(sum(C[:, 14].sum() for C in b_))}")
    if singles is not None:
        sd = Path(singles); pr("\n## reported: ensemble (headline b) vs PF2 single-seed mean +- sd (argmax), descriptive")
        for k, arm in (('E-g', 'SUP'), ('E-PF', 'SUPPF')):
            S = [json.load(open(sd / f'pf2_{arm}_100pct_s{q}.json'))['cells'] for q in range(5, 10)]
            for sp, f, nm in (('test', lambda s: True, 'test all 50'), ('test', lambda s: s != NOISY, 'test clean 49'), ('ext', lambda s: True, 'E1 106')):
                v = np.array([[g['iou'][14], g['relF1'], g['iou'][11]] for g in (agg(c[sp], f) for c in S)])
                e = agg(J[(k, hb[k])]['cells'][sp], f)
                pr(f"  {k} {nm}: crack IoU {e['iou'][14]:.4f} vs {v[:, 0].mean():.4f} +- {v[:, 0].std(ddof=1):.4f} | relF1@2 {e['relF1']:.4f} vs "
                   f"{v[:, 1].mean():.4f} +- {v[:, 1].std(ddof=1):.4f} | inactive IoU {e['iou'][11]:.4f} vs {v[:, 2].mean():.4f} +- {v[:, 2].std(ddof=1):.4f}")
    pr("\nFINAL (cv02, R34 5-seed ensemble, b +0.75) clean-test crack IoU 0.492: descriptive only (other machine and commits).")
    return "\n".join(O).split("\n")


def pair(JA, JB, ctx, bA, bB, O, full_report=True, role="verdict"):
    """LB_ (cells JB at bB) - LA_ (cells JA at bA); LA_ / LB_ = the module-level labels (default E-PF / E-SKR2). Returns test verdict rows, E1 bootstrap, guards. O = output line list.
    role: "verdict" (the b 0 pair; no label), "headline" (guards apply; primaries reported), "reported" (not a verdict)."""
    pr = O.append; res = {}
    lab = {"verdict": "", "headline": "  (guards apply; primaries reported)", "reported": "  (reported, not a verdict)"}[role]
    for split in ('test', 'test_noscuff'):
        A = JA['test' if split == 'test' else 'test_noscuff']; B = JB[split]; rows = {}
        pr(f"  [{split}] {LA_} b {bA} vs {LB_} b {bB}; paired image bootstrap 2,000, seed 0 (Track M m1_analyze.boot)")
        for sn, f in SETS.items():
            st = sorted(s for s in A if f(s)); full, lo, hi, pp = M1.boot([A], [B], st)
            ga, gb = agg(A, f), agg(B, f)
            pr(f"    {sn:9s} | " + " | ".join(f"{PN[i]} {full[i]:+.4f} [{lo[i]:+.4f}, {hi[i]:+.4f}] P>0 {pp[i]:.2f}" for i in PRIM_IX + [3])
               + f" | {LA_} crack IoU {ga['iou'][14]:.4f} relF1 {ga['relF1']:.4f} inact {ga['iou'][11]:.4f} | {LB_} {gb['iou'][14]:.4f} {gb['relF1']:.4f} {gb['iou'][11]:.4f}")
            if full_report:
                pr(f"              capture {LA_} -> {LB_}: relR2 {ga['relR2']:.3f}->{gb['relR2']:.3f} relP2 {ga['relP2']:.3f}->{gb['relP2']:.3f} "
                   f"pix R {ga['rec'][14]:.3f}->{gb['rec'][14]:.3f} pix P {ga['prec'][14]:.3f}->{gb['prec'][14]:.3f} comp R {ga['cc_rec50_20']:.3f}->{gb['cc_rec50_20']:.3f} "
                   f"comp P {ga['cc_prec_20']:.3f}->{gb['cc_prec_20']:.3f} any-hit {ga['cc_recany_20']:.3f}->{gb['cc_recany_20']:.3f} (n {ga['cc_n_20']}) "
                   f"pred/GT {ga['pr'][14] / max(ga['gt'][14], 1):.3f}->{gb['pr'][14] / max(gb['gt'][14], 1):.3f}")
            if sn in ('all 50', 'clean 49'):
                rows[sn] = (full, lo, hi)
        res[split] = rows
        pr(f"    => {split}: " + verdict(rows) + ("" if split == 'test' else "  (reported only)") + (f"; passing: {passing(rows)}" if split == 'test' else "") + lab)
        if split == 'test' and full_report:
            src = sorted({s.split('_')[0] for s in A})
            pr(f"    per source ({LA_} -> {LB_}): " + "; ".join(
                f"{p} n {agg(A, lambda s, p=p: s.startswith(p))['n']} crack IoU {agg(A, lambda s, p=p: s.startswith(p))['iou'][14]:.3f}->{agg(B, lambda s, p=p: s.startswith(p))['iou'][14]:.3f} "
                f"relF1 {agg(A, lambda s, p=p: s.startswith(p))['relF1']:.3f}->{agg(B, lambda s, p=p: s.startswith(p))['relF1']:.3f} "
                f"inact {agg(A, lambda s, p=p: s.startswith(p))['iou'][11]:.3f}->{agg(B, lambda s, p=p: s.startswith(p))['iou'][11]:.3f}" for p in src))
    A, B = JA['ext'], JB['ext']; st = sorted(A); assert len(st) == 106 and sorted(B) == st
    full, lo, hi, pp, ncl = cluster_boot5(A, B, st); assert ncl == 71, ncl
    ga, gb = agg(A, lambda s: True), agg(B, lambda s: True)
    pr(f"  [E1] 106 cells, {ncl} module clusters; paired module-cluster bootstrap 2,000, seed 0")
    pr(f"    E1 crack relF1@2 {full[2]:+.4f} [{lo[2]:+.4f}, {hi[2]:+.4f}] P>0 {pp[2]:.2f} ({LA_} {ga['relF1']:.4f}, {LB_} {gb['relF1']:.4f}) | "
       f"E1 any-hit {full[4]:+.4f} [{lo[4]:+.4f}, {hi[4]:+.4f}] P>0 {pp[4]:.2f} ({LA_} {ga['cc_recany_20']:.4f}, {LB_} {gb['cc_recany_20']:.4f}; n {ga['cc_n_20']}) | "
       f"E1 inactive IoU {full[1]:+.4f} [{lo[1]:+.4f}, {hi[1]:+.4f}] P>0 {pp[1]:.2f} ({LA_} {ga['iou'][11]:.4f}, {LB_} {gb['iou'][11]:.4f})")
    e1 = 'FAIL' if (hi[2] < 0 or hi[4] < 0) else (('PASS (' + ', '.join(n for n, i in (('E1 crack relF1@2', 2), ('E1 any-hit', 4)) if lo[i] > 0) + ')') if (lo[2] > 0 or lo[4] > 0) else 'n.d.')
    pr(f"    => E1 co-primaries: {e1}{lab}")
    res['e1'] = (full, lo, hi, e1)
    # guards (§3b)
    tA, tB = JA['test'], JB['test']
    rp = agg(tB, lambda s: True)['relP2'] - agg(tA, lambda s: True)['relP2']
    fa, fb = cfree(A), cfree(B); assert len(fa) == 74 and len(fb) == 74, (len(fa), len(fb))
    pa, pb = cfpx(A), cfpx(B)
    gi = {sn: res['test'][sn][0][1] for sn in ('all 50', 'clean 49')}
    G = {'G2a test relP@2 delta < -0.03': (rp < -0.03, f"delta {rp:+.4f}"),
         f'G2b E1 crack-free px > 1.5 x {LA_}': (pb > 1.5 * pa, f"{LB_} {pb} vs {LA_} {pa} (bar {1.5 * pa:.0f}; x{pb / max(pa, 1):.2f})"),
         'G1t test inactive delta <= -0.015 in both sets': (all(v <= -0.015 for v in gi.values()), f"all 50 {gi['all 50']:+.4f}, clean 49 {gi['clean 49']:+.4f}"),
         'G1e E1 inactive CI wholly below 0': (hi[1] < 0, f"{full[1]:+.4f} [{lo[1]:+.4f}, {hi[1]:+.4f}]")}
    pr("    guards: " + " | ".join(f"{n}: {'TRIP' if t else 'ok'} ({d})" for n, (t, d) in G.items()) + lab)
    res['guards'] = G
    if full_report:
        pr(f"    width: pred/GT crack px test {agg(tA, lambda s: True)['pr'][14] / max(agg(tA, lambda s: True)['gt'][14], 1):.3f}->"
           f"{agg(tB, lambda s: True)['pr'][14] / max(agg(tB, lambda s: True)['gt'][14], 1):.3f}, E1 {ga['pr'][14] / max(ga['gt'][14], 1):.3f}->{gb['pr'][14] / max(gb['gt'][14], 1):.3f}; "
           f"E1 relR2 {ga['relR2']:.3f}->{gb['relR2']:.3f} relP2 {ga['relP2']:.3f}->{gb['relP2']:.3f} pix R {ga['rec'][14]:.3f}->{gb['rec'][14]:.3f} pix P {ga['prec'][14]:.3f}->{gb['prec'][14]:.3f} "
           f"comp R {ga['cc_rec50_20']:.3f}->{gb['cc_rec50_20']:.3f} comp P {ga['cc_prec_20']:.3f}->{gb['cc_prec_20']:.3f}")
        for sp in ('test', 'val', 'ext'):
            pr(f"    crack px on crack-free {sp} cells ({len(cfree(JA[sp]))}): {LA_} {cfpx(JA[sp])}, {LB_} {cfpx(JB[sp])}")
        GR = (('scuff+half-cut', lambda s: ctx[s][0] == 'scuff_halfcut'), ('half-cut w/o scuff', lambda s: ctx[s][0] == 'other' and ctx[s][2] == 'halfcut=1'),
              ('full', lambda s: ctx[s][2] == 'halfcut=0'), ('half-cut', lambda s: ctx[s][2] == 'halfcut=1'), ('other', lambda s: ctx[s][0] == 'other'))
        for gn, f in GR:
            a_, b_ = agg(A, f), agg(B, f)
            pr(f"    E1 stratum {gn} n {a_['n']}: relF1 {a_['relF1']:.3f}->{b_['relF1']:.3f} any-hit {a_['cc_recany_20']:.3f}->{b_['cc_recany_20']:.3f} (n {a_['cc_n_20']}) "
               f"inact IoU {a_['iou'][11]:.3f}->{b_['iou'][11]:.3f} relR2 {a_['relR2']:.3f}->{b_['relR2']:.3f} relP2 {a_['relP2']:.3f}->{b_['relP2']:.3f} "
               f"crack R {a_['rec'][14]:.3f}->{b_['rec'][14]:.3f} pred/GT {a_['pr'][14] / max(a_['gt'][14], 1):.3f}->{b_['pr'][14] / max(b_['gt'][14], 1):.3f}")
    return res


def e1_concentration(JA, JB, O):  # descriptive: per-image (module cluster) concentration, leave-top-3-images-out, leave-one-cluster-out
    pr = O.append; A, B = JA['ext'], JB['ext']; st = sorted(A); cl = sorted({MODULE(s) for s in st})
    ip = {c: sum(np.array(A[s]['conf']).reshape(24, 24)[11].sum() for s in st if MODULE(s) == c) for c in cl}
    hc = {c: hcounts(A, [s for s in st if MODULE(s) == c])[:, 1].sum() for c in cl}
    for nm, w in (('GT inactive px', ip), ('GT crack comps >= 20 px', hc)):
        tot = sum(w.values()); srt = sorted(cl, key=lambda c: -w[c]); sh = np.array([w[c] / max(tot, 1) for c in srt])
        pr(f"  E1 {nm}: total {tot}, images with any {sum(1 for c in cl if w[c] > 0)}, top 3 share {sh[:3].sum():.3f}, top 10 {sh[:10].sum():.3f}, "
           f"n_eff {1 / max((sh ** 2).sum(), 1e-12):.1f}; top 3 = {[(c, int(w[c])) for c in srt[:3]]}")
    for c in sorted(cl, key=lambda c: -hc[c])[:10]:
        ss = [s for s in st if MODULE(s) == c]; ha, hb = hcounts(A, ss).sum(0), hcounts(B, ss).sum(0)
        pr(f"    any-hit comps in {c}: {LA_} {ha[0]}/{ha[1]}, {LB_} {hb[0]}/{hb[1]}")
    f5 = lambda ss: m5(*M1.counts(B, ss), hcounts(B, ss)) - m5(*M1.counts(A, ss), hcounts(A, ss))
    for nm, w in (('inactive px', ip), ('crack comps', hc)):
        top = set(sorted(cl, key=lambda c: -w[c])[:3]); ss = [s for s in st if MODULE(s) not in top]; d = f5(ss)
        pr(f"  leave-top-3-images-out (by GT {nm}; {len(ss)} cells): E1 relF1@2 {d[2]:+.4f}, any-hit {d[4]:+.4f}, inactive IoU {d[1]:+.4f}")
    L = np.array([f5([s for s in st if MODULE(s) != c]) for c in cl])
    pr(f"  leave-one-cluster-out range ({len(cl)} drops): E1 relF1@2 [{np.nanmin(L[:, 2]):+.4f}, {np.nanmax(L[:, 2]):+.4f}], "
       f"any-hit [{np.nanmin(L[:, 4]):+.4f}, {np.nanmax(L[:, 4]):+.4f}] (full {f5(st)[2]:+.4f} / {f5(st)[4]:+.4f})")


def matched(sweep, O):  # descriptive, E1-oracle, chooses nothing: LA_ at the b where its E1 pred / GT = LB_'s at b 0
    pr = O.append; tgt = sweep[LB_]['0.0']['pred_over_gt']; bs = sorted(float(b) for b in sweep[LA_])
    r = [sweep[LA_][str(b)]['pred_over_gt'] for b in bs]
    pr(f"  matched volume (E1-oracle, descriptive): {LB_} b 0 E1 pred/GT {tgt:.4f}, relF1@2 {sweep[LB_]['0.0']['relF1']:.4f}, "
       f"any-hit {sweep[LB_]['0.0']['anyhit']:.4f}; {LA_} pred/GT over b: " + ", ".join(f"{b:g}:{v:.3f}" for b, v in zip(bs, r)))
    if not all(r[i] <= r[i + 1] for i in range(len(r) - 1)):
        pr(f"    {LA_} pred/GT is not monotone in b on the grid: matched-volume line not computed"); return None
    if tgt < r[0] or tgt > r[-1]:
        pr(f"    target outside {LA_}'s grid range: matched-volume line not computed"); return None
    j = max(i for i in range(len(r)) if r[i] <= tgt); j = min(j, len(r) - 2); t = (tgt - r[j]) / (r[j + 1] - r[j]) if r[j + 1] > r[j] else 0.0
    ip = lambda q: sweep[LA_][str(bs[j])][q] + t * (sweep[LA_][str(bs[j + 1])][q] - sweep[LA_][str(bs[j])][q])
    out = {'b': bs[j] + t * (bs[j + 1] - bs[j]), 'relF1': ip('relF1'), 'anyhit': ip('anyhit')}
    pr(f"    {LA_} at b {out['b']:.3f} (linear between grid b {bs[j]:g} and {bs[j + 1]:g}): relF1@2 {out['relF1']:.4f}, any-hit {out['anyhit']:.4f}")
    return out


def dverdict(test_rows, e1, trips):  # SKR2C §3b verdict D + fixed wording (one pair, b 0); returns (V, carriers, lines)
    tp = passing(test_rows); ef = e1[3]
    car = [f"test {n}" for n in tp] + ([x.strip() for x in ef[6:-1].split(',')] if ef.startswith('PASS') else [])
    pfail = verdict(test_rows).startswith('FAIL') or ef == 'FAIL'
    V = 'FAIL' if (pfail or trips) else ('PASS' if car else 'n.d.')
    out = []
    if V == 'PASS':
        out.append(f"  => VERDICT D PASS, carried by: {', '.join(car)}")
        vol = {'test crack IoU', 'test relF1@2', 'E1 any-hit'}
        if set(car) <= vol:
            out.append("  carried by argmax readouts that were mostly volume on seeds 5-9 (SKR2E §3a); see the matched-volume lines (§4).")
        if not ef.startswith('PASS'):
            out.append("  SKR2's E1 gain is not replicated at ensemble level.")
    elif V == 'FAIL':
        why = ([f"primary fails ({'test: ' + verdict(test_rows) if verdict(test_rows).startswith('FAIL') else 'E1 co-primaries FAIL'})"] if pfail else []) + \
              ([f"guard trips: {', '.join(trips)}"] if trips else [])
        out.append(f"  => VERDICT D FAIL ({'; '.join(why)})")
        if not pfail and trips and all(t.startswith(('G1t', 'G1e')) for t in trips):
            out.append("  inactive guard alone: D's G1t null false-FAIL ~8%; with R's G1 ~9-15%, ~15% combined that a true null keeps SUP100-PF "
                       "through an inactive guard alone (protocol_SKR2C §3c, judge L2).")
    else:
        out.append("  => VERDICT D n.d.; the SUP100-PF ensemble stays (protocol_SKR2C §3c).")
    return V, car, out


if '--selftest' in sys.argv:  # on already-opened PF2E (#4) and SKR2E (#6) files + PF2 m0: no new model read
    i = sys.argv.index('--selftest'); PD, PT, CX, M0 = Path(sys.argv[i + 1]), Path(sys.argv[i + 2]), sys.argv[i + 3], Path(sys.argv[i + 4])
    SD, ST = Path(sys.argv[i + 5]), Path(sys.argv[i + 6])  # SKR2C: #6 SKR2E raw dir + skr2e_boot_runner.txt
    ctx = {l.split('\t')[0]: l.rstrip('\n').split('\t')[1:] for l in open(CX) if l.strip()}
    ref = PT.read_text().split("\n")
    if ref and ref[-1] == "":
        ref = ref[:-1]
    cb5 = lambda A, B, st: cluster_boot5(A, B, st)[:5]
    new = pf2e_report(PD, ctx, M0, cb=cb5); old = pf2e_report(PD, ctx, M0, cb=cluster_boot)
    t1 = new == ref; t1b = old == ref
    nd = [k for k, (x, y) in enumerate(zip(new, ref)) if x != y][:3]
    # (2) E-PF vs itself: every CI [0, 0], no guard trips, verdict n.d.
    E = json.load(open(PD / 'E-PF.b0.json'))['cells']; O = []
    r = pair(E, E, ctx, 0.0, 0.0, O, full_report=False)
    zero = all(np.all(np.nan_to_num(np.array(r[sp][sn][j]), nan=0.0) == 0) for sp in ('test', 'test_noscuff') for sn in r[sp] for j in range(3))
    zero &= all(np.all(np.nan_to_num(np.array(r['e1'][j]), nan=0.0) == 0) for j in range(3))
    noG = not any(t for t, _ in r['guards'].values())
    # (3) any-hit column: full = agg cc_recany_20 difference; columns 0-3 of cluster_boot5 == cluster_boot exactly (E-g vs E-PF, b 0 E1)
    Eg = json.load(open(PD / 'E-g.b0.json'))['cells']['ext']; Ep = E['ext']; st = sorted(Ep)
    c4, c5 = cluster_boot(Eg, Ep, st), cluster_boot5(Eg, Ep, st)
    cols = all(np.array_equal(x, y[:4], equal_nan=True) for x, y in zip(c4[:4], c5[:4]))
    ah = abs(c5[0][4] - (agg(Ep, lambda s: True)['cc_recany_20'] - agg(Eg, lambda s: True)['cc_recany_20'])) < 1e-12
    ngt = hcounts(Ep, st)[:, 1].sum()
    # (4) matched-volume interpolation on a synthetic sweep (known answer)
    sw = {'E-SKR2': {'0.0': {'pred_over_gt': 1.1, 'relF1': 0.5, 'anyhit': 0.4}},
          'E-PF': {str(b): {'pred_over_gt': 1.0 + 0.2 * b, 'relF1': 0.4 + 0.1 * b, 'anyhit': 0.3 + 0.05 * b} for b in (0.0, 0.25, 0.5, 0.75)}}
    mv = matched(sw, []); t4 = mv is not None and abs(mv['b'] - 0.5) < 1e-12 and abs(mv['relF1'] - 0.45) < 1e-12 and abs(mv['anyhit'] - 0.325) < 1e-12
    print(f"selftest (1) PF2E report via cluster_boot5 == {PT.name} line by line: {t1} ({len(new)} / {len(ref)} lines; first diffs {nd}) "
          f"[control: via pf2e cluster_boot {t1b}] | (2) E-PF vs itself: all CIs [0, 0] {zero}, no guard trips {noG}, test verdict {verdict(r['test'])}, "
          f"E1 {r['e1'][3]} | (3) cluster_boot5 cols 0-3 == cluster_boot exactly {cols}; any-hit full == agg cc_recany_20 diff {ah}; E1 GT comps >= 20 px {ngt} (expect 296) "
          f"| (4) matched-volume interpolation {t4}")
    ok = t1 and t1b and zero and noG and verdict(r['test']) == 'n.d.' and r['e1'][3] == 'n.d.' and cols and ah and ngt == 296 and t4
    # (5) SKR2C: #6's b 0 pair block, E1 concentration block and matched-volume lines reproduced verbatim from #6's files (labels E-PF / E-SKR2)
    R6 = ST.read_text().split("\n"); J6 = {k: json.load(open(SD / f'{k}.b0.json'))['cells'] for k in ('E-PF', 'E-SKR2')}
    def block(h):
        j = R6.index(h); k = j + 1
        while k < len(R6) and R6[k] != '':
            k += 1
        return R6[j + 1:k]
    O = []; pair(J6['E-PF'], J6['E-SKR2'], ctx, 0.0, 0.0, O, role='verdict'); t5a = O == block('## VERDICT: both arms at b 0: E-PF b 0.0 vs E-SKR2 b 0.0')
    O = []; e1_concentration(J6['E-PF'], J6['E-SKR2'], O); t5b = O == block('## reported: E1 concentration and robustness (b 0 pair)')
    O = []; matched(json.load(open(SD / 'skr2e_e1_sweep.json')), O); t5c = O == block('## reported: matched-volume check (skr2e_e1_sweep.json)')
    # (6) verdict-D wording on synthetic rows: CI above 0 in both sets for crack IoU -> PASS + volume line + E1-not-replicated line;
    #     an inactive guard alone -> FAIL + the ~15% line; E1 relF1 pass only -> PASS without the volume line; a CI below 0 -> FAIL
    up, dn, zr = (np.array([.02, .01, .02, 0]), np.array([.01, -.01, -.01, 0]), np.array([.03, .03, .03, 0])), \
        (np.array([-.02, 0, 0, 0]), np.array([-.03, -.01, -.01, 0]), np.array([-.01, .01, .01, 0])), \
        (np.zeros(4), np.array([-.01] * 4), np.array([.01] * 4))
    nd1 = (None, None, None, 'n.d.'); e1p = (None, None, None, 'PASS (E1 crack relF1@2)')
    v1 = dverdict({'all 50': up, 'clean 49': up}, nd1, []); v2 = dverdict({'all 50': zr, 'clean 49': zr}, nd1, ['G1t test inactive delta <= -0.015 in both sets'])
    v3 = dverdict({'all 50': zr, 'clean 49': zr}, e1p, []); v4 = dverdict({'all 50': dn, 'clean 49': zr}, e1p, [])
    t6 = (v1[0] == 'PASS' and v1[1] == ['test crack IoU'] and len(v1[2]) == 3 and v2[0] == 'FAIL' and len(v2[2]) == 2 and v3[0] == 'PASS'
          and v3[1] == ['E1 crack relF1@2'] and len(v3[2]) == 1 and v4[0] == 'FAIL')
    print(f"selftest (5) #6 SKR2E b 0 pair block == {ST.name} {t5a} | E1 concentration block {t5b} | matched-volume lines {t5c} "
          f"| (6) verdict-D wording on synthetic rows {t6}")
    ok = ok and t5a and t5b and t5c and t6
    print('SELFTEST', 'PASS' if ok else 'FAIL'); sys.exit(0 if ok else 1)

# ---- SKR2C verdict D (protocol_SKR2C §3b, §3c, §4): ONE verdict pair, both arms at b 0; b_mv pair reported with CIs
LA_, LB_ = "E-SUPPF", "E-SKR2"
D = Path(sys.argv[1]); ctx = {l.split('\t')[0]: l.rstrip('\n').split('\t')[1:] for l in open(sys.argv[2]) if l.strip()}
dec = json.load(open(D / 's2c_d_val_decisions.json')); chk = json.load(open(D / 's2c_d_checks.json'))
assert chk['rc'] == 0, "s2c_d_checks rc != 0: no verdict"
bmv = dec['b_mv']['b_mv']; assert dec['written_b'] == {LA_: [0.0], LB_: sorted({0.0, bmv})}, dec['written_b']
J = {(k, b): json.load(open(D / f'{k}.b{b:g}.json'))['cells'] for k in (LA_, LB_) for b in dec['written_b'][k]}
O = []; pr = O.append
pr(f"# SKR2C verdict D: {LB_}' - {LA_}' (5-member ensembles s2c_*_s10..14; same 50 test and 106 E1 cells as #5 / #6, 3rd look). Labels: "
   f"{LA_} = E-SUPPF' (s2c_SUPPF_100pct_s10..14), {LB_} = E-SKR2' (s2c_SKR01_100pct_s10..14).")
pr(f"# Val (reported only; s2c_d_val_decisions.json): " + "; ".join(
    f"{k} D2 b {dec[k]['bias']} ({dec[k]['why']}; val crack precision drop {dec[k]['val_crack_precision_drop_at_bias']:+.4f}; width flag "
    f"{'ON' if dec[k]['val_crack_precision_drop_at_bias'] > 0.05 else 'off'})" for k in (LA_, LB_))
   + f"; b_mv {bmv} (val pred/GT {dec['b_mv']['val_pred_over_gt_at_b_mv']:.4f} vs {LA_} b 0 {dec['b_mv']['target_val_pred_over_gt']:.4f}). "
   f"Checks: {chk}")
pr(f"\n## VERDICT: both arms at b 0: {LA_} b 0.0 vs {LB_} b 0.0")
v0 = pair(J[(LA_, 0.0)], J[(LB_, 0.0)], ctx, 0.0, 0.0, O, role='verdict')
trips = [n for n, (t, _) in v0['guards'].items() if t]
V, car, wl = dverdict(v0['test'], v0['e1'], trips)
pr("\n## SKR2C VERDICT D (protocol_SKR2C §3b; one pair, b 0 for both; guards at that pair)")
pr(f"  test primaries: {verdict(v0['test'])} (passing: {passing(v0['test'])}) | E1 co-primaries: {v0['e1'][3]} | guard trips: {trips if trips else 'none'}")
for l in wl:
    pr(l)
pr("  every any-hit line carries the per-image concentration line: see 'E1 concentration' below.")
pr("\n## reported: E1 concentration and robustness (b 0 pair)")
e1_concentration(J[(LA_, 0.0)], J[(LB_, 0.0)], O)
vm = None
if bmv != 0.0:
    pr(f"\n## reported: matched val volume (protocol §4): {LA_} b 0.0 vs {LB_} b_mv {bmv}  (reported, not a verdict)")
    vm = pair(J[(LA_, 0.0)], J[(LB_, bmv)], ctx, 0.0, bmv, O, role='reported')
else:
    pr(f"\n## reported: matched val volume (protocol §4): b_mv = 0, so the b_mv pair is the verdict pair above")
sw = json.load(open(D / 's2c_d_e1_sweep.json')); pr("\n## reported: E1 aggregate sweep (-1.5 .. 3, step 0.25) and E1 matched volume (E1-oracle, descriptive)")
for k in (LA_, LB_):
    pr(f"  {k}: " + ", ".join(f"{float(b):g}: pred/GT {v['pred_over_gt']:.3f} relF1 {v['relF1']:.4f} any-hit {v['anyhit']:.4f} cf px {v['crack_free_px']}"
                             for b, v in sorted(sw[k].items(), key=lambda x: float(x[0]))))
matched(sw, O)
if '--singles' in sys.argv:  # descriptive: ensembles at b 0 vs the fresh single-seed m0 JSONs of R (argmax)
    i = sys.argv.index('--singles'); sd = {LA_: (Path(sys.argv[i + 1]), 's2c_SUPPF_100pct_s'), LB_: (Path(sys.argv[i + 2]), 's2c_SKR01_100pct_s')}
    pr("\n## reported: ensemble (b 0) vs single-seed mean +- sd (argmax, s10-14), descriptive")
    for k, (d, pre) in sd.items():
        S = [json.load(open(d / f'{pre}{q}.json'))['cells'] for q in range(10, 15)]
        for sp, f, nm in (('test', lambda s: True, 'test all 50'), ('test', lambda s: s != NOISY, 'test clean 49'), ('ext', lambda s: True, 'E1 106')):
            v = np.array([[g['iou'][14], g['relF1'], g['iou'][11], g['cc_recany_20']] for g in (agg(c[sp], f) for c in S)])
            e = agg(J[(k, 0.0)][sp], f)
            pr(f"  {k} {nm}: crack IoU {e['iou'][14]:.4f} vs {v[:, 0].mean():.4f} +- {v[:, 0].std(ddof=1):.4f} | relF1@2 {e['relF1']:.4f} vs "
               f"{v[:, 1].mean():.4f} +- {v[:, 1].std(ddof=1):.4f} | inactive IoU {e['iou'][11]:.4f} vs {v[:, 2].mean():.4f} +- {v[:, 2].std(ddof=1):.4f} | "
               f"any-hit {e['cc_recany_20']:.4f} vs {v[:, 3].mean():.4f} +- {v[:, 3].std(ddof=1):.4f}")
pr("\nFINAL (cv02, R34 5-seed ensemble, b +0.75) clean-test crack IoU 0.492: descriptive only (other machine and commits).")
pr("B5 is not part of D (protocol_SKR2C §3b); B5 sits in R.")
print("\n".join(O))
if '--json' in sys.argv:
    tl = lambda x: [float(v) for v in np.asarray(x)]
    out = {'label': 'protocol_SKR2C §3b verdict D (one pair, b 0)', 'verdict': V, 'carriers': car, 'guard_trips': trips,
           'test': {sn: {'full': tl(v[0]), 'lo': tl(v[1]), 'hi': tl(v[2]), 'cols': PN} for sn, v in v0['test'].items()},
           'e1': {'full': tl(v0['e1'][0]), 'lo': tl(v0['e1'][1]), 'hi': tl(v0['e1'][2]), 'cols': PN + ['any-hit'], 'reading': v0['e1'][3]},
           'e1_relF1_primary_passes': bool(v0['e1'][1][2] > 0), 'b_mv': bmv,
           'b_mv_pair': None if vm is None else {'e1': {'full': tl(vm['e1'][0]), 'lo': tl(vm['e1'][1]), 'hi': tl(vm['e1'][2])},
                                                  'test': {sn: {'full': tl(v[0]), 'lo': tl(v[1]), 'hi': tl(v[2])} for sn, v in vm['test'].items()}},
           'guards': {n: {'trip': bool(t), 'detail': d} for n, (t, d) in v0['guards'].items()}}
    json.dump(out, open(sys.argv[sys.argv.index('--json') + 1], 'w'), indent=1)
