"""Track M FINAL analysis (protocol_final.md step 3). CPU only. Usage: python m9_analyze.py final/final_cells.json m0b"""
import json, sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from m0_analyze import agg, NAMES, NOISY, TWINS, NC  # noqa: E402
from m1_analyze import boot, PRIM, CL  # noqa: E402

SETS = {"all": lambda s: True, "-noisy": lambda s: s != NOISY, "-twins": lambda s: s not in TWINS,
        "-both": lambda s: s not in TWINS and s != NOISY}
f = json.load(open(sys.argv[1])); m0b = Path(sys.argv[2])
sup = f["sup"]
S = {r: json.load(open(m0b / f"{r}.json"))["cells"] for r in sup}
T = f["test"]; heads = [k for k in T if k.startswith("final_b")]
print("rec_is_sup:", f["rec_is_sup"], "| finals:", heads)


def cap(A):
    return (f"crack IoU {A['iou'][14]:.3f} P {A['prec'][14]:.3f} R {A['rec'][14]:.3f} relP2 {A['relP2']:.3f} relR2 {A['relR2']:.3f} relF1 {A['relF1']:.3f} "
            f"comp rec {A['cc_rec50_20']:.3f} comp prec {A['cc_prec_20']:.3f} | inact IoU {A['iou'][11]:.3f} P {A['prec'][11]:.3f} R {A['rec'][11]:.3f} "
            f"comp rec {A['in_cc_rec50']:.3f} | mIoU_rob {A['miou_rob']:.3f} (no 0/7 {A['miou_rob_no07']:.3f}) mIoU24 {A['miou24']:.3f} FP-absent px {A['fp_absent_px']}")


for setn, kf in SETS.items():
    stems = [s for s in sorted(T["final_b0"]) if kf(s)]
    single = [agg(S[r]["test"], kf, CL) for r in sup]
    print(f"\n######## TEST {setn} (n={len(stems)})")
    print("  SUP100 mean single:", " | ".join(f"{nm} {np.mean([g(x) for x in single]):.4f}" for nm, g in PRIM),
          f"| crack P {np.mean([x['prec'][14] for x in single]):.3f} R {np.mean([x['rec'][14] for x in single]):.3f} relP2 {np.mean([x['relP2'] for x in single]):.3f} relR2 {np.mean([x['relR2'] for x in single]):.3f}")
    for h in heads:
        A = agg(T[h], kf, CL)
        print(f"  {h}: {cap(A)}")
        if setn in ("all", "-noisy"):
            full, lo, hi, pp = boot([S[r]["test"] for r in sup], [T[h]], stems)
            print(f"    contrast 1/3 {h} - SUP100 mean single: " + " | ".join(f"{nm} {full[i]:+.4f} [{lo[i]:+.4f}, {hi[i]:+.4f}]" for i, (nm, _) in enumerate(PRIM)))
        pb = np.sum([T[h][s]["crack_pband_gt"] for s in stems], 0); pb = pb / pb.sum()
        print(f"    p(crack) bands on GT crack: " + " / ".join(f"{v:.3f}" for v in pb))
print("\n######## per source (test, all): source | n | " + " | ".join(f"{h} crack IoU, R, relR2, inact IoU, mIoU_rob, FP-absent" for h in heads) + " | SUP100 single crack IoU")
for so in ("ARTS", "BMRK", "CFVS", "CSIR", "SDLE"):
    for tag, kf in (("all", lambda s, so=so: s.startswith(so)), ("-noisy", lambda s, so=so: s.startswith(so) and s != NOISY)):
        if tag == "-noisy" and so != "CSIR":
            continue
        row = []
        for h in heads:
            A = agg(T[h], kf, CL)
            row.append(f"{A['iou'][14]:.3f}, {A['rec'][14]:.3f}, {A['relR2']:.3f}, {A['iou'][11]:.3f}, {A['miou_rob']:.3f}, {A['fp_absent_px']}")
        si = np.mean([agg(S[r]["test"], kf, CL)["iou"][14] for r in sup])
        print(f"| {so} {tag} | {A['n']} | " + " | ".join(row) + f" | {si:.3f} |")
print("\n######## 24-class table (test, all / without noisy): class | GT px | GT cells | " + " | ".join(f"{h} IoU P R (all) ; IoU (-noisy)" for h in heads))
A0 = {h: agg(T[h], SETS["all"], CL) for h in heads}; A1 = {h: agg(T[h], SETS["-noisy"], CL) for h in heads}
for c in range(NC):
    a = A0[heads[0]]
    if a["gt"][c] == 0 and all(A0[h]["pr"][c] == 0 for h in heads):
        print(f"| {c} {NAMES[c]} | 0 | 0 | absent, never predicted |"); continue
    print(f"| {c} {NAMES[c]} | {int(a['gt'][c])} | {a['gt_cells'][c]} | " + " | ".join(
        (f"{A0[h]['iou'][c]:.3f} {A0[h]['prec'][c]:.3f} {A0[h]['rec'][c]:.3f} ; {A1[h]['iou'][c]:.3f}" if a["gt"][c] > 0 else f"absent; FP px {A0[h]['pr'][c]}") for h in heads) + " |")
print("\n######## noisy cell px (crack 14 / border 5 / text 6):")
for h in heads + ["r1_model"]:
    C = np.array(T[h][NOISY]["conf"]).reshape(NC, NC); print(f"  {h}: {C[:, 14].sum()} / {C[:, 5].sum()} / {C[:, 6].sum()}")
E = f["ext"]
e0 = agg(E["final_b0"], lambda s: True); el = ([c for c in range(NC) if e0["gt"][c] > 0], [c for c in range(NC) if e0["gt_cells"][c] >= 3])
print("\n######## E1 ext 106 (never used for selection): variant | crack IoU P R relR2 | inactive IoU R | mIoU (ext list)")
for nm, cells in [("SUP100 mean single", None)] + [(h, E[h]) for h in heads]:
    for tag, kf in (("all", lambda s: True), ("-CSIR_00300_r25_c1", lambda s: s != "CSIR_00300_r25_c1")):
        if cells is None:
            G = [agg(S[r]["ext"], kf, el) for r in sup]
            m = lambda k, c=None: np.mean([g[k][c] if c is not None else g[k] for g in G])
            print(f"  {nm} {tag}: {m('iou', 14):.3f} {m('prec', 14):.3f} {m('rec', 14):.3f} {m('relR2'):.3f} | {m('iou', 11):.3f} {m('rec', 11):.3f} | {m('miou_rob'):.3f}")
        else:
            A = agg(cells, kf, el)
            print(f"  {nm} {tag}: {A['iou'][14]:.3f} {A['prec'][14]:.3f} {A['rec'][14]:.3f} {A['relR2']:.3f} | {A['iou'][11]:.3f} {A['rec'][11]:.3f} | {A['miou_rob']:.3f}")
