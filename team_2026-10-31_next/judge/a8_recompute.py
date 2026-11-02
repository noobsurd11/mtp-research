"""judge a8_recompute (1 Nov 2026 ~23:40 IST): independent recompute of the A8 screen GO / KILL (protocol_A8screen v1.1 §3)
from the frozen dumps on gaint. Own code: imports nothing from a8_screen_score / el_metrics / calib_dump. CPU only, numpy/scipy.
Reads: a8_score/v1/work/dump/<run>.{val,rf}.npz (pc, margin, oth, stems), val masks (el_f8 labeled/masks_escdd), Hanifi _rf
masks + ignore (calib/data/rf), frozen rf_sets.tsv, each run's metrics.json (val_history / test_final only), the scorer's
records + json (cross-check only), and the NAMES in el_f8 splits/test.txt + ext117 stems_eval.txt (disjointness only).
No test or E1 image / mask / prediction is read.
Usage: python -B a8_recompute.py OUT_DIR
"""
import json
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

V1 = Path("/home/noob/work/a8_score/v1"); DUMP = V1 / "work/dump"; REC = V1 / "out/rec"
EL = Path("/home/noob/work/el_f8"); RF = Path("/home/noob/work/calib/data/rf"); EXPS = EL / "experiments"
SETS = V1 / "frozen/rf_sets.tsv"; E1LIST = Path("/home/noob/work/el_f1/reports/f1/ext117/stems_eval.txt")
ARMS = {"A8": ["f8_A8_4k_s0", "f8_A8_4k_s1"], "A8c": ["f8_A8c_4k_s0", "f8_A8c_4k_s1"]}
RUNS = ARMS["A8"] + ARMS["A8c"]
CR, IN = 14, 11
OPB = np.round(np.arange(-40, 121) / 10.0, 1)  # OP grid -4.0 .. +12.0 step 0.1
NCODE = 15361  # float16 codes 0x0000 .. 0x3C00 (= 1.0)
OFFS = [(dy, dx) for dy in range(-2, 3) for dx in range(-2, 3) if dy * dy + dx * dx <= 4]  # EDT <= 2 (13 offsets)
OUT = Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
LOG = open(OUT / "a8_recompute.txt", "w")


def say(*a):
    s = " ".join(str(x) for x in a); print(s, flush=True); LOG.write(s + "\n"); LOG.flush()


# ------------------------------------------------------------------ sets, GT
rows = [l.rstrip("\n").split("\t") for l in open(SETS) if l.strip()]
hdr, rows = rows[0], rows[1:]
SET = {r[0]: r[1] for r in rows}; MOD = {r[0]: r[3] for r in rows}
val_stems = sorted(l.strip() for l in open(EL / "data/splits/val.txt") if l.strip())
test_names = {l.strip() for l in open(EL / "data/splits/test.txt") if l.strip()}
e1_names = {l.strip() for l in open(E1LIST) if l.strip()}
GT, KEEP = {}, {}


def gt_of(s, sp):
    if s not in GT:
        if sp == "val":
            g = np.array(Image.open(EL / "data/labeled/masks_escdd" / f"{s}.png")); k = np.ones(g.shape, bool)
        else:
            g = np.array(Image.open(RF / "masks" / f"{s}.png")); k = ~(np.array(Image.open(RF / "ignore" / f"{s}.png")) > 0)
        GT[s], KEEP[s] = g, k
    return GT[s], KEEP[s]


def ap_hist(pos, neg):
    """step AP, thresholds descending over the hist bins (ties grouped)"""
    tp = np.cumsum(pos[::-1]).astype(float); fp = np.cumsum(neg[::-1]).astype(float)
    n = pos.sum()
    if n == 0:
        return float("nan")
    prec = np.divide(tp, tp + fp, out=np.zeros_like(tp), where=(tp + fp) > 0)
    rec = tp / n
    return float(np.sum(prec * np.diff(np.concatenate([[0.0], rec]))))


def dil2(m):
    """max over the EDT<=2 disk (13 offsets), -inf outside"""
    H, W = m.shape; p = np.full((H + 4, W + 4), -np.inf, np.float32); p[2:-2, 2:-2] = m
    out = np.full((H, W), -np.inf, np.float32)
    for dy, dx in OFFS:
        np.maximum(out, p[2 + dy:2 + dy + H, 2 + dx:2 + dx + W], out=out)
    return out


def val_cell(args):
    """per val cell: pred / relp_tp / relr_tp over OPB, b=0 crack + inactive counts"""
    m, oth, g = args
    gc = g == CR; ng = int(gc.sum())
    near = ndi.distance_transform_edt(~gc) <= 2 if ng else np.zeros(g.shape, bool)
    s_all = np.sort(m.ravel()); s_near = np.sort(m[near]); M2g = np.sort(dil2(m)[gc])
    cnt = lambda s: len(s) - np.searchsorted(s, -OPB, side="right")
    return cnt(s_all), cnt(s_near), cnt(M2g), ng


# ------------------------------------------------------------------ per run
code_val = np.arange(NCODE, dtype=np.uint16).view(np.float16).astype(np.float32)
bin_of_code = np.clip((code_val * 1000).astype(int), 0, 999)
R = {}
for r in RUNS:
    R[r] = {"hist": {}, "fa_m": {}, "val": None}
    for sp in ("val", "rf"):
        z = np.load(DUMP / f"{r}.{sp}.npz"); st = [str(s) for s in z["stems"]]
        pc, mg, oth = z["pc"], z["margin"], z["oth"]
        if sp == "val":
            assert st == val_stems, "val stems != val.txt"
        else:
            assert len(st) == 106 and all(s in SET for s in st), "rf stems != rf_sets"
        assert not (set(st) & test_names) and not (set(st) & e1_names), "TEST / E1 stem in a dump"
        codes = pc.view(np.uint16)
        assert int(codes.max()) < NCODE and not np.isnan(pc).any(), "pc outside [0, 1]"
        for i, s in enumerate(st):
            g, k = gt_of(s, sp)
            t = (g == CR) & k; c = codes[i]
            pos = np.bincount(c[t], minlength=NCODE); neg = np.bincount(c[k & ~t], minlength=NCODE)
            R[r]["hist"][s] = (pos, neg, int(t.sum()), float(pc[i][k].max()))
            if sp == "rf":
                R[r]["fa_m"][s] = (np.sort(mg[i][k].astype(np.float32)), (oth[i] == IN) & k, mg[i].astype(np.float32), int(t.sum()))
        if sp == "val":
            with Pool(8) as p:
                vc = p.map(val_cell, [(mg[i].astype(np.float32), oth[i], gt_of(s, "val")[0]) for i, s in enumerate(st)], chunksize=2)
            pred = sum(x[0] for x in vc); rp = sum(x[1] for x in vc); rr = sum(x[2] for x in vc); ng = sum(x[3] for x in vc)
            relP = np.where(pred > 0, rp / np.maximum(pred, 1), np.nan); relR = rr / ng
            ok = np.where(np.nan_to_num(relP, nan=-1) >= 0.90)[0]
            j = int(ok[np.argmax(relR[ok])]) if len(ok) else int(np.argmax(np.nan_to_num(relP, nan=-1)))
            b = float(OPB[j])
            # b = 0 gate + inactive at b and b_rel, pooled over val
            tpc = pc_ = gtc = ti = pi = gi = 0; tib = pib = 0
            for i, s in enumerate(st):
                g = gt_of(s, "val")[0]; m = mg[i].astype(np.float32)
                cp = m > 0; gtc_ = g == CR
                tpc += int((cp & gtc_).sum()); pc_ += int(cp.sum()); gtc += int(gtc_.sum())
                ip = (oth[i] == IN) & ~cp; gin = g == IN
                ti += int((ip & gin).sum()); pi += int(ip.sum()); gi += int(gin.sum())
                ipb = (oth[i] == IN) & ~(m + b > 0); tib += int((ipb & gin).sum()); pib += int(ipb.sum())
            R[r]["val"] = {"b_rel": b, "reachable": bool(len(ok)), "relP": float(relP[j]), "relR": float(relR[j]),
                           "crack_iou_b0": tpc / (pc_ + gtc - tpc), "inact_iou_b0": ti / (pi + gi - ti),
                           "inact_iou_brel": tib / (pib + gi - tib)}
            # spot check of the relR / relP definition by explicit EDT at b_rel on 10 cells
            ex = []
            for i, s in enumerate(st[:10]):
                g = gt_of(s, "val")[0]; m = mg[i].astype(np.float32); P_ = m + b > 0; gc = g == CR
                if P_.any() and gc.any():
                    ex.append((int((gc & (ndi.distance_transform_edt(~P_) <= 2)).sum()), int(vc[i][2][j]),
                               int((P_ & (ndi.distance_transform_edt(~gc) <= 2)).sum()), int(vc[i][1][j])))
            R[r]["val"]["edt_spot_equal"] = all(a == b_ and c == d for a, b_, c, d in ex); R[r]["val"]["edt_spot_n"] = len(ex)
        del z, pc, mg, oth
    say(f"run {r}: loaded; val OP b_rel {R[r]['val']['b_rel']} relP {R[r]['val']['relP']:.4f} relR {R[r]['val']['relR']:.4f} "
        f"reachable {R[r]['val']['reachable']} edt spot equal {R[r]['val']['edt_spot_equal']} (n {R[r]['val']['edt_spot_n']})")

rf_stems = [s for s in SET]
F51 = [s for s in rf_stems if SET[s] == "F51"]; H36 = [s for s in rf_stems if SET[s] == "H36"]; F19 = [s for s in rf_stems if SET[s] == "F19"]
SETD = {"F51": F51, "H36": H36, "F19": F19, "val": val_stems}
r0 = RUNS[0]
ngt = {s: R[r0]["hist"][s][2] for s in F51 + H36 + F19}
mods = sorted({MOD[s] for s in F51})
say("== sets (E)")
say(f"F51 cells {len(F51)} modules {len(mods)} crack cells (>=20 px in keep) {sum(ngt[s] >= 20 for s in F51)} "
    f"ambiguous 1-19 px {sum(0 < ngt[s] < 20 for s in F51)} crack-free {sum(ngt[s] == 0 for s in F51)} crack px {sum(ngt[s] for s in F51)}")
say(f"H36 cells {len(H36)} crack-free {sum(ngt[s] == 0 for s in H36)} | F19 cells {len(F19)} | val {len(val_stems)}")
say(f"dump stems vs real test.txt names: 0 shared; vs E1 stems_eval names: 0 shared (asserted per dump)")


def ap_of(r, stems, binned):
    pos = np.sum([R[r]["hist"][s][0] for s in stems], 0); neg = np.sum([R[r]["hist"][s][1] for s in stems], 0)
    if binned:
        pos, neg = np.bincount(bin_of_code, pos, 1000), np.bincount(bin_of_code, neg, 1000)
    return ap_hist(pos, neg)


say("== crack AP per run (1000-bin = the rule's definition; fp16-exact = ties at fp16 resolution)")
AP = {}
for r in RUNS:
    AP[r] = {k: (ap_of(r, v, True), ap_of(r, v, False)) for k, v in SETD.items()}
    say(r, " ".join(f"{k} {AP[r][k][0]:.4f}/{AP[r][k][1]:.4f}" for k in SETD))
mean = lambda arm, k, i: float(np.mean([AP[r][k][i] for r in ARMS[arm]]))
for i, nm in ((0, "1000-bin"), (1, "fp16-exact")):
    say(f"arm means {nm}: " + " | ".join(f"{k} A8 {mean('A8', k, i):.4f} A8c {mean('A8c', k, i):.4f} d {mean('A8', k, i) - mean('A8c', k, i):+.4f}" for k in SETD))
say("seed-pair dF51 (1000-bin): s0 {:+.4f}  s1 {:+.4f}; cross pairs A8s0-A8cs1 {:+.4f} A8s1-A8cs0 {:+.4f}".format(
    AP["f8_A8_4k_s0"]["F51"][0] - AP["f8_A8c_4k_s0"]["F51"][0], AP["f8_A8_4k_s1"]["F51"][0] - AP["f8_A8c_4k_s1"]["F51"][0],
    AP["f8_A8_4k_s0"]["F51"][0] - AP["f8_A8c_4k_s1"]["F51"][0], AP["f8_A8_4k_s1"]["F51"][0] - AP["f8_A8c_4k_s0"]["F51"][0]))

# ------------------------------------------------------------------ module bootstrap
by = {m: [s for s in F51 if MOD[s] == m] for m in mods}
MH = {}
for r in RUNS:
    for binned in (True, False):
        P = np.stack([np.sum([R[r]["hist"][s][0] for s in by[m]], 0) for m in mods]); N = np.stack([np.sum([R[r]["hist"][s][1] for s in by[m]], 0) for m in mods])
        if binned:
            P = np.stack([np.bincount(bin_of_code, p, 1000) for p in P]); N = np.stack([np.bincount(bin_of_code, n, 1000) for n in N])
        MH[r, binned] = (P.astype(np.float64), N.astype(np.float64))


def boot(binned, two_stage=False, seed=0, B=2000, drop=None):
    rng = np.random.default_rng(seed); rs = np.random.default_rng(1)
    keep_m = np.array([m != drop for m in mods], float)
    out = []
    for _ in range(B):
        c = np.bincount(rng.integers(0, len(mods), len(mods)), minlength=len(mods)) * keep_m
        ra = ARMS["A8"] if not two_stage else [ARMS["A8"][i] for i in rs.integers(0, 2, 2)]
        rc = ARMS["A8c"] if not two_stage else [ARMS["A8c"][i] for i in rs.integers(0, 2, 2)]
        f = lambda r: ap_hist(c @ MH[r, binned][0], c @ MH[r, binned][1])
        out.append(np.mean([f(r) for r in ra]) - np.mean([f(r) for r in rc]))
    out = np.array(out); out = out[~np.isnan(out)]
    return out


say("== F51 paired module-cluster bootstrap (2,000, seed 0, resample the 36 modules; rule term 1b = lower 2.5% > 0)")
for binned, nm in ((True, "1000-bin (rule)"), (False, "fp16-exact")):
    bs = boot(binned)
    say(f"{nm}: 2.5% {np.percentile(bs, 2.5):+.4f} 97.5% {np.percentile(bs, 97.5):+.4f} mean {bs.mean():+.4f} median {np.median(bs):+.4f} "
        f"P(d*>0) {np.mean(bs > 0):.3f} n {len(bs)}")
bs2 = boot(True, two_stage=True)
say(f"two-stage (modules + seed draw per arm, 1000-bin): 2.5% {np.percentile(bs2, 2.5):+.4f} 97.5% {np.percentile(bs2, 97.5):+.4f} P(d*>0) {np.mean(bs2 > 0):.3f}")
for sd in (1, 2):
    b_ = boot(True, seed=sd)
    say(f"bootstrap seed {sd} (1000-bin): 2.5% {np.percentile(b_, 2.5):+.4f} 97.5% {np.percentile(b_, 97.5):+.4f}")

say("== per crack module dAP (1000-bin, seed means) and leave-one-crack-module-out dF51")
crack_mods = [m for m in mods if any(ngt[s] >= 20 for s in by[m])]
for m in crack_mods:
    aps = {r: ap_of(r, by[m], True) for r in RUNS}
    d = np.mean([aps[r] for r in ARMS["A8"]]) - np.mean([aps[r] for r in ARMS["A8c"]])
    rest = [s for s in F51 if MOD[s] != m]
    dl = np.mean([ap_of(r, rest, True) for r in ARMS["A8"]]) - np.mean([ap_of(r, rest, True) for r in ARMS["A8c"]])
    say(f"{m}: cells {len(by[m])} crack px {sum(ngt[s] for s in by[m])} AP " + " ".join(f"{aps[r]:.3f}" for r in RUNS) + f" | dAP {d:+.4f} | F51 without it d {dl:+.4f}")

# ------------------------------------------------------------------ false alarms at b_rel
say("== false alarms: crack px (margin + b > 0, keep) on crack-free cells (n_gt == 0) at each run's own val b_rel; and at b 0 / common b")


def fa(r, stems, b):
    return int(sum(len(R[r]["fa_m"][s][0]) - np.searchsorted(R[r]["fa_m"][s][0], -b, side="right") for s in stems if R[r]["fa_m"][s][3] == 0))


FA = {}
for r in RUNS:
    b = R[r]["val"]["b_rel"]
    FA[r] = {k: fa(r, SETD[k], b) for k in ("H36", "F51")}
    say(f"{r} b_rel {b}: H36 {FA[r]['H36']} F51 {FA[r]['F51']} | at b 0: H36 {fa(r, H36, 0.0)} F51 {fa(r, F51, 0.0)} | at b 2.8: H36 {fa(r, H36, 2.8)} F51 {fa(r, F51, 2.8)}"
        f" | crack-free cells with >= 20 FA px at b_rel: H36 {sum(1 for s in H36 if R[r]['fa_m'][s][3] == 0 and fa(r, [s], b) >= 20)} F51 {sum(1 for s in F51 if R[r]['fa_m'][s][3] == 0 and fa(r, [s], b) >= 20)}")
for k in ("H36", "F51"):
    a_ = np.mean([FA[r][k] for r in ARMS["A8"]]); c_ = np.mean([FA[r][k] for r in ARMS["A8c"]]); bd = max(1.5 * c_, c_ + 200)
    say(f"term 3 {k}: A8 {a_:.1f} A8c {c_:.1f} bound max(1.5x, +200) {bd:.1f} -> {'PASS' if a_ <= bd else 'FAIL'} (ratio {a_ / max(c_, 1e-9):.2f}; "
        f"without the +200 floor: {'PASS' if a_ <= 1.5 * c_ else 'FAIL'})")

# ------------------------------------------------------------------ terms
dF = mean("A8", "F51", 0) - mean("A8c", "F51", 0); dV = mean("A8", "val", 0) - mean("A8c", "val", 0)
bs = boot(True)
say("== GO rule (own numbers)")
say(f"1a dF51 {dF:+.4f} -> {'PASS' if dF > 0 else 'FAIL'}; 1b boot lo {np.percentile(bs, 2.5):+.4f} -> {'PASS' if np.percentile(bs, 2.5) > 0 else 'FAIL'}; "
    f"2 dval {dV:+.4f} -> {'PASS' if dV >= -0.02 else 'FAIL'}")

# ------------------------------------------------------------------ reported: AUROC, inactive at b_rel, val gate
say("== reported only")


def auroc(pos, neg):
    v = np.array(pos + neg)
    order = np.argsort(v, kind="mergesort"); ranks = np.empty(len(v)); ranks[order] = np.arange(1, len(v) + 1)
    for u in np.unique(v):
        idx = v == u; ranks[idx] = ranks[idx].mean()
    return float((ranks[:len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


for r in RUNS:
    au = {k: auroc([R[r]["hist"][s][3] for s in v if R[r]["hist"][s][2] >= 20], [R[r]["hist"][s][3] for s in v if R[r]["hist"][s][2] == 0])
          for k, v in (("F51", F51), ("H36", H36), ("F19", F19))}
    b = R[r]["val"]["b_rel"]; inn = {}
    for k, v in (("F51", F51), ("F19", F19)):
        tp = pr = gtn = 0
        for s in v:
            srt, oi, m, _ = R[r]["fa_m"][s]; g, kp = gt_of(s, "rf"); ip = oi & ~(m + b > 0); gi = (g == IN) & kp
            tp += int((ip & gi).sum()); pr += int(ip.sum()); gtn += int(gi.sum())
        inn[k] = tp / max(pr + gtn - tp, 1)
    say(f"{r}: cell AUROC (max p, >=20 vs 0) F51 {au['F51']:.4f} H36 {au['H36']:.4f} F19 {au['F19']:.4f} | inactive IoU at b_rel val {R[r]['val']['inact_iou_brel']:.4f} "
        f"F51 {inn['F51']:.4f} F19 {inn['F19']:.4f}")

say("== CPU dump vs trainer val gate (own: pooled val IoU at b 0 from the dump vs metrics.json val_history[-1]; and test_final == val_history[-1])")
for r in RUNS:
    mj = json.load(open(EXPS / r / "metrics.json")); vh = mj["val_history"][-1]; tf = mj["test_final"]
    same = all(vh[k] == tf[k] for k in ("crack_iou", "inactive_iou", "miou_all", "defect_miou", "n_images", "n_crack_free_images", "pixel_accuracy"))
    gt_px_same = tf.get("per_class_gt_pixels") == vh.get("per_class_gt_pixels") if "per_class_gt_pixels" in vh else "n/a"
    v = R[r]["val"]
    say(f"{r}: step {vh['step']} | crack IoU dump {v['crack_iou_b0']:.5f} trainer {vh['crack_iou']:.5f} d {v['crack_iou_b0'] - vh['crack_iou']:+.5f} | "
        f"inactive IoU dump {v['inact_iou_b0']:.5f} trainer {vh['inactive_iou']:.5f} d {v['inact_iou_b0'] - vh['inactive_iou']:+.5f} | "
        f"test_final == val_history[-1] (7 scalars): {same}; test_final n_images {tf['n_images']}; per-class GT px equal: {gt_px_same}")

# ------------------------------------------------------------------ cross-check vs the scorer's json
sj = json.load(open(V1 / "out/a8_screen_score.json"))
say("== vs a8_screen_score.json")
for r in RUNS:
    say(r, "F51 AP scorer {:.6f} own {:.6f} | val AP scorer {:.6f} own {:.6f} | b_rel scorer {} own {} | FA H36 {} / {} F51 {} / {}".format(
        sj["per_run"][r]["F51"]["crack_ap"], AP[r]["F51"][0], sj["per_run"][r]["val"]["crack_ap"], AP[r]["val"][0], sj["b_rel"][r], R[r]["val"]["b_rel"],
        sj["per_run"][r]["H36"]["fa_px_crackfree_at_brel"], FA[r]["H36"], sj["per_run"][r]["F51"]["fa_px_crackfree_at_brel"], FA[r]["F51"]))
say(f"terms scorer {json.dumps(sj['terms'])}")
say("DONE")
