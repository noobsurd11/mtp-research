"""Track D probe analysis (protocol team_2026-10-24_go/trackD/protocol_probe.md). Reads results/trackD_probe/{hists.npz,
percell.json,meta.json}. Prints the decision rule (BMRK test crack AP), per-source AP / IoU / relaxed recall /
matched-precision recall on test and pool, the 40 components, inactive AP, and the A5c identity check.
Usage: python scripts/trackD_probe_analysis.py > results/trackD_probe/analysis.txt
"""
import json, sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
R = Path(__file__).resolve().parent.parent / "results"
D = R / "trackD_probe"
H = np.load(D / "hists.npz")
PC = json.loads((D / "percell.json").read_text())
META = json.loads((D / "meta.json").read_text())
LA = json.loads((R / "sk1" / "la_sa_test.json").read_text())
STEMS = {"test": [str(s) for s in H["stems_test"]], "pool": [str(s) for s in H["stems_pool"]]}
SRC = ["BMRK", "ARTS", "CFVS", "CSIR", "SDLE", "all"]
A5C = ["p12_A_5pct_s0", "p12_A_5pct_s1", "p12_A_5pct_s2", "p13_A_5pct_s3", "p13_A_5pct_s4"]
ENC = ["rn50_random", "rn34_imagenet", "rn50_imagenet", "convnext_t", "dinov2_vits14", "ref_A5c_enc"]
RULE_ENC = ["rn34_imagenet", "rn50_imagenet", "convnext_t", "dinov2_vits14"]


def binned_ap(pos, neg):
    pos, neg = np.asarray(pos, np.float64), np.asarray(neg, np.float64)
    n = pos.sum()
    if n == 0:
        return float("nan")
    tp, fp = np.cumsum(pos[::-1]), np.cumsum(neg[::-1])
    rec = tp / n
    with np.errstate(divide="ignore", invalid="ignore"):
        prec = np.where(tp + fp > 0, tp / (tp + fp), 0.0)
    return float((np.diff(np.concatenate([[0.0], rec])) * prec).sum())


def idx(split, src):
    return [i for i, s in enumerate(STEMS[split]) if src == "all" or s.split("_")[0] == src]


def m(tag, split, src, cls=0):
    ix = idx(split, src)
    h = H[f"{tag}|{split}"][ix, cls]
    pos, neg = h[:, 0].sum(0), h[:, 1].sum(0)
    key = "crack" if cls == 0 else "inactive"
    v = np.sum([PC[tag][f"{split}/{STEMS[split][i]}"][key] for i in ix], 0)
    out = {"ap": binned_ap(pos, neg), "gt": int(pos.sum())}
    tp, fp, fn = v[:3]
    out.update(iou=tp / max(tp + fp + fn, 1), prec=tp / max(tp + fp, 1), rec=tp / max(tp + fn, 1))
    if cls == 0:
        out.update(relr=v[5] / max(v[6], 1), relp=v[3] / max(v[4], 1))
    out["pos"], out["neg"] = pos, neg
    return out


def matched_recall(pos, neg, target):
    tp, fp = np.cumsum(pos[::-1])[::-1], np.cumsum(neg[::-1])[::-1]
    with np.errstate(divide="ignore", invalid="ignore"):
        prec = np.where(tp + fp > 0, tp / (tp + fp), 0.0)
    ok = np.where(prec >= target)[0]
    return (float(tp[ok.min()] / max(pos.sum(), 1)), int(ok.min())) if len(ok) else (0.0, None)


def tags(name):
    if name.startswith("A5c"):
        tau = name.split("tau")[1]
        return [f"A5c/{r}/tau{tau}" for r in A5C]
    return [f"probe/{name}/seed{s}" for s in (0, 1)]


# ---- identity check vs la_sa_test.json
mx = 0.0
for r in A5C:
    for tau in ("0", "1"):
        ref = LA[f"test/{r}/tau{tau}"]["new_escdd"]
        x, y = m(f"A5c/{r}/tau{tau}", "test", "all", 0), m(f"A5c/{r}/tau{tau}", "test", "all", 1)
        mx = max(mx, abs(ref["crack"]["iou"] - x["iou"]), abs(ref["crack"]["ap"] - x["ap"]),
                 abs(ref["inactive"]["iou"] - y["iou"]), abs(ref["inactive"]["ap"] - y["ap"]))
print(f"## Checks\n  A5c tau 0/1 vs la_sa_test.json (crack/inactive IoU and AP, 5 runs): max |diff| {mx:.2e}")
print(f"  pool cells {len(STEMS['pool'])}; train {len(META['train'])}; twins excluded {META['twins_excluded']}")
for s in ("BMRK", "ARTS"):
    for sp in ("test", "pool"):
        ix = idx(sp, s)
        nc = sum(PC[f"A5c/{A5C[0]}/tau0"][f"{sp}/{STEMS[sp][i]}"]["crack"][6] > 0 for i in ix)
        print(f"  {s} {sp}: {len(ix)} cells, {nc} with crack, {m(f'A5c/{A5C[0]}/tau0', sp, s)['gt']} crack px")
print("  final probe train losses:", {k: round(v["final_train_loss"], 3) for k, v in META["models"].items() if "final_train_loss" in v})

# ---- decision rule
print("\n## Decision rule: BMRK test crack AP")
a0 = np.array([m(t, "test", "BMRK")["ap"] for t in tags("A5c_tau0")])
a1 = np.array([m(t, "test", "BMRK")["ap"] for t in tags("A5c_tau1")])
ref = max(a0.mean(), a1.mean())
print(f"  A5c tau0 {a0.mean():.4f} ± {a0.std(ddof=1):.4f}; A5c+LA {a1.mean():.4f} ± {a1.std(ddof=1):.4f}; R = {ref:.4f}; bar R + 0.05 = {ref + 0.05:.4f}")
any_pass = False
for e in ENC:
    v = np.array([m(t, "test", "BMRK")["ap"] for t in tags(e)])
    ok = e in RULE_ENC and v.mean() >= ref + 0.05 and (v >= ref + 0.05).all()
    any_pass |= ok
    pv = np.array([m(t, "pool", "BMRK")["ap"] for t in tags(e)])
    print(f"  {e:15s} seeds {v.round(4).tolist()} mean {v.mean():.4f}  Δ vs R {v.mean() - ref:+.4f}  "
          f"{'PASS' if ok else ('fail' if e in RULE_ENC else 'reference only')} | pool BMRK AP {pv.mean():.4f}")
p0 = np.array([m(t, "pool", "BMRK")["ap"] for t in tags("A5c_tau0")]); p1 = np.array([m(t, "pool", "BMRK")["ap"] for t in tags("A5c_tau1")])
print(f"  pool BMRK: A5c {p0.mean():.4f}, A5c+LA {p1.mean():.4f}, R_pool {max(p0.mean(), p1.mean()):.4f}")
print(f"  VERDICT: {'an encoder passes' if any_pass else 'no pretrained encoder passes'}")

# ---- per source tables
for split in ("test", "pool"):
    print(f"\n## {split}: crack AP / IoU / relaxed R@2 / recall at matched precision (target = A5c+LA pixel precision on that source)")
    srcs = [s for s in SRC if idx(split, s) and (s != "SDLE" or split == "pool")]
    targets = {s: np.mean([m(t, split, s)["prec"] for t in tags("A5c_tau1")]) for s in srcs}
    print("| model | " + " | ".join(f"{s} (P*={targets[s]:.2f})" for s in srcs) + " |")
    print("|---|" + "---|" * len(srcs))
    for name in ["A5c_tau0", "A5c_tau1"] + ENC:
        cells = []
        for s in srcs:
            xs = [m(t, split, s) for t in tags(name)]
            mr = np.mean([matched_recall(x["pos"], x["neg"], targets[s])[0] for x in xs])
            cells.append(f"{np.mean([x['ap'] for x in xs]):.3f} / {np.mean([x['iou'] for x in xs]):.3f} / "
                         f"{np.mean([x['relr'] for x in xs]):.3f} / {mr:.3f}")
        print(f"| {name.replace('A5c_tau0', 'A5c').replace('A5c_tau1', 'A5c+LA')} | " + " | ".join(cells) + " |")

# ---- inactive AP
print("\n## Inactive AP (test all / pool all), descriptive")
for name in ["A5c_tau0", "A5c_tau1"] + ENC:
    print(f"  {name:15s} test {np.mean([m(t, 'test', 'all', 1)['ap'] for t in tags(name)]):.3f}  pool {np.mean([m(t, 'pool', 'all', 1)['ap'] for t in tags(name)]):.3f}")

# ---- 40 components
print(f"\n## 40 always-missed components: px-weighted relaxed@2 recall and count with recall >= 0.5 (argmax | matched at P* = {META['comp40_target_precision_test_all']:.3f})")
for name in ["A5c_tau0", "A5c_tau1"] + ENC:
    res = []
    for key in ("comp40_argmax", "comp40_matched"):
        hit = tot = n05 = 0; ids = set()
        for t in tags(name):
            for k, v in PC[t].items():
                for cid, (h, a) in v.get(key, {}).items():
                    hit += h; tot += a; n05 += h / a >= 0.5; ids.add(cid)
        res.append(f"{hit / max(tot, 1):.3f}, {n05 / len(tags(name)):.1f}/40")
    print(f"  {name:15s} argmax {res[0]} | matched {res[1]}")
