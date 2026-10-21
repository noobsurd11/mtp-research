"""D0: read-only ALHVR region / target / prototype / gradient-share probe on the P-series base.

Surrogate network pair = two independently trained A5c supervised runs (L3 base, 5% labels, final weights).
Data = the 455 unlabelled cells of the seed-0 5% split; their revised masks are used ONLY to score
routing and targets, never in a loss that updates weights (no weights are updated at all).
Run from the root of an el-fault-detection checkout (imports src.*), gaint, one GPU.
"""
from __future__ import annotations

import argparse, json, random, sys
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader

sys.path.insert(0, ".")
from src.data.augmentations import get_weak_augmentation  # noqa: E402
from src.data.benchmark_el import BenchmarkELDataset  # noqa: E402
from src.data.splits import load_split  # noqa: E402
from src.losses.ce_dice import CEDiceLoss  # noqa: E402
from src.models.model_factory import build_model  # noqa: E402
from src.trainers.ssl_ops import cutmix_boxes, frozen_bn_stats, mix_with_next  # noqa: E402
from src.utils.config import load_config  # noqa: E402

CRACK, INACT = 14, 11
GROUPS = ("crack", "inactive", "other")
LAYERS = ("x_0_1", "x_0_4")
PERT = "coin"  # 1/8 res 128 ch (reference-like "deep") | full-res 16 ch (paper text: penultimate)


# ---------------- perturbations (reference networks/unet.py) ----------------
def feature_dropout(x):
    att = x.mean(1, keepdim=True)
    mx = att.view(x.size(0), -1).max(1, keepdim=True).values
    thr = (mx * np.random.uniform(0.7, 0.9)).view(x.size(0), 1, 1, 1)
    keep = (att >= thr).float()  # reference: drop where att < thr
    return x * keep, keep


def feature_noise(x, r=0.3):
    n = torch.empty(x.shape[1:], device=x.device).uniform_(-r, r).unsqueeze(0)
    return x + x * n


def forward(m, x, perturb, store_keep=None):
    feats = m.encoder(x)
    if perturb is not None:
        if perturb == "dropout":
            new = [feats[0]]
            for f in feats[1:]:
                p, keep = feature_dropout(f)
                new.append(p)
                if store_keep is not None:
                    store_keep.append(keep)
            feats = new
        else:
            feats = [feats[0]] + [feature_noise(f) for f in feats[1:]]
    cap = {}
    h = m.decoder.blocks["x_0_1"].register_forward_hook(lambda mod, i, o: cap.__setitem__("x_0_1", o))
    dec = m.decoder(feats)
    h.remove()
    cap["x_0_4"] = dec
    return m.segmentation_head(dec), cap


def load(run_dir: Path, dev):
    cfg = load_config(run_dir / "config_used.yaml")
    m = build_model(cfg["model"]).to(dev)
    st = torch.load(run_dir / "checkpoints" / "latest.pth", map_location=dev, weights_only=False)
    m.load_state_dict(st["models"]["model"])
    assert int(st["step"]) == 20000
    return m, cfg


def group_masks(gt):
    return {"crack": gt == CRACK, "inactive": gt == INACT, "other": (gt != CRACK) & (gt != INACT)}


def dilate(b, r=2):
    return F.max_pool2d(b.float().unsqueeze(1), 2 * r + 1, 1, r).squeeze(1) > 0


def protos(feat, lab, K=24):
    B, C = feat.shape[:2]
    oh = F.one_hot(lab, K).permute(0, 3, 1, 2).reshape(B, K, -1).float()
    cnt = oh.sum(2)
    s = torch.einsum("bkn,bcn->bkc", oh, feat.reshape(B, C, -1).float())
    per = s / (cnt.unsqueeze(2) + 1e-5)
    n = (cnt > 0).sum(0)
    return per.sum(0) / n.clamp_min(1).unsqueeze(1).float(), n > 0


def nearest_proto(feat, P, present):
    f = F.normalize(feat.float(), dim=1)
    p = F.normalize(P.float(), dim=1)
    cos = torch.einsum("bchw,kc->bkhw", f, p)
    cos[:, ~present] = -9
    return cos.argmax(1)


def sharpen_elem(p, T=0.1):
    pt = p ** (1 / T)
    return pt / (pt + (1 - p) ** (1 / T))


@torch.no_grad()
def probe_pair(ma, mb, dl, dev, beta, out, seed):
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)
    acc = {}
    def add(k, v):
        acc[k] = acc.get(k, 0.0) + float(v)
    nb = 0
    for b in dl:
        x = b["image"].to(dev); gt = b["mask"].to(dev).long()
        G = group_masks(gt)
        for m in (ma, mb):
            m.train()
        with frozen_bn_stats(ma), frozen_bn_stats(mb), torch.autocast("cuda", dtype=torch.bfloat16):
            la1, ca1 = forward(ma, x, None)
            lb1, cb1 = forward(mb, x, None)
            keeps_a = []
            pa = PERT if PERT != "coin" else ("dropout" if random.random() > 0.5 else "noise")
            la2, ca2 = forward(ma, x, pa, keeps_a)
            pb = PERT if PERT != "coin" else ("dropout" if random.random() > 0.5 else "noise")
            lb2, cb2 = forward(mb, x, pb)
        sa1, sb1, sa2, sb2 = (torch.softmax(t.float(), 1) for t in (la1, lb1, la2, lb2))
        conA1, plA = sa1.max(1); conB1, plB = sb1.max(1)
        conA2, conB2 = sa2.max(1).values, sb2.max(1).values
        con = ((conA2 + conB2) / 2).flatten()
        k = int(con.numel() * beta)
        gamma = con.sort().values[:k].mean()
        add("gamma", gamma); nb += 1
        r3 = (conA2 < gamma) & (conB2 < gamma)
        r2a = (conA2 <= gamma) & (conB2 > gamma)
        r2b = (conB2 <= gamma) & (conA2 > gamma)
        r2 = r2a | r2b
        r1 = ~(r2 | r3)
        for g, gm in G.items():
            add(f"n_{g}", gm.sum())
            for rn, rm in (("r1", r1), ("r2", r2), ("r3", r3)):
                add(f"{rn}_{g}", (gm & rm).sum())
        for rn, rm in (("r1", r1), ("r2", r2), ("r3", r3)):
            add(f"{rn}_all", rm.sum())
        add("n_all", gt.numel())
        # perturbation damage: perturbed vs clean argmax agreement on crack, per perturbation kind
        add(f"pert_{pa}_n", 1)
        add(f"pert_{pa}_crack_kept_clean_crack", ((plA == CRACK) & (sa2.argmax(1) == CRACK)).sum())
        add(f"pert_{pa}_clean_crack", (plA == CRACK).sum())
        add(f"pert_{pa}_conA2_mean", conA2.mean())
        add(f"pert_{pa}_conA2_gtcrack", conA2[G["crack"]].sum()); add(f"pert_{pa}_gtcrack_px", G["crack"].sum())
        if keeps_a:  # FeatureDropout keep rate per level, at GT-crack cells vs all cells
            for li, keep in enumerate(keeps_a):
                h, w = keep.shape[-2:]
                cr = F.adaptive_max_pool2d(G["crack"].float().unsqueeze(1), (h, w)) > 0
                add(f"fd_L{li+1}_keep_all", keep.mean()); add(f"fd_L{li+1}_n", 1)
                add(f"fd_L{li+1}_keep_crack_num", (keep * cr).sum()); add(f"fd_L{li+1}_keep_crack_den", cr.sum())
        # DTCT winner (clean) in r3
        a_w = conA1 > conB1
        win = torch.where(a_w.unsqueeze(1), sa1, sb1)
        wl = win.argmax(1); wmax = win.max(1).values
        gc = G["crack"]; gcd = dilate(gc)
        add("r3_win_crack_pred", (r3 & (wl == CRACK)).sum())
        add("r3_win_crack_tp", (r3 & (wl == CRACK) & gc).sum())
        add("r3_win_crack_tp_rel2", (r3 & (wl == CRACK) & gcd).sum())
        add("r3_gtcrack_win_crack", (r3 & gc & (wl == CRACK)).sum())
        add("r3_gtcrack_win_crack_rel2", (r3 & gc & dilate(wl == CRACK)).sum())
        gi = G["inactive"]
        add("r3_win_inact_pred", (r3 & (wl == INACT)).sum()); add("r3_win_inact_tp", (r3 & (wl == INACT) & gi).sum())
        add("r3_gtinact_win_inact", (r3 & gi & (wl == INACT)).sum())
        add("r3_win_correct_other", (r3 & G["other"] & (wl == gt)).sum())
        low = r3 & (wmax < 0.5)
        add("r3_wmax_lt05", low.sum()); add("r3_gtcrack_wmax_lt05", (low & gc).sum())
        es = sharpen_elem(win).sum(1)
        add("r3_elem_target_sum", es[r3].sum()); add("r3_gtcrack_elem_target_sum", es[r3 & gc].sum())
        # r2: confident partner's argmax as target
        tgt2 = torch.where(r2a, plB, plA)
        add("r2_tgt_crack_pred", (r2 & (tgt2 == CRACK)).sum()); add("r2_tgt_crack_tp", (r2 & (tgt2 == CRACK) & gc).sum())
        add("r2_tgt_crack_tp_rel2", (r2 & (tgt2 == CRACK) & gcd).sum())
        add("r2_gtcrack_tgt_crack", (r2 & gc & (tgt2 == CRACK)).sum())
        # BsM-like hard PL on net A clean (conf >= 0.95), whole image
        hp = conA1 >= 0.95
        add("hp_crack_pred", (hp & (plA == CRACK)).sum()); add("hp_crack_tp", (hp & (plA == CRACK) & gc).sum())
        add("hp_crack_tp_rel2", (hp & (plA == CRACK) & gcd).sum()); add("hp_gtcrack_cov", (hp & gc & (plA == CRACK)).sum())
        add("hp_px", hp.sum())
        # prototypes per layer, scored on r2a (A unsure, B sure): A perturbed features vs B / A prototypes
        for L in LAYERS:
            up = lambda f: F.interpolate(f.float(), size=x.shape[-2:], mode="bilinear", align_corners=False)
            fa2, fb1, fa1 = up(ca2[L]), up(cb1[L]), up(ca1[L])
            PB, prB = protos(fb1, plB); PA, prA = protos(fa1, plA)
            add(f"{L}_crack_proto_present_B", float(prB[CRACK])); add(f"{L}_nbatch", 1)
            for name, P, pr in (("cross", PB, prB), ("own", PA, prA)):
                npl = nearest_proto(fa2, P, pr)
                for g, gm in G.items():
                    sel = r2a & gm
                    add(f"{L}_{name}_r2a_{g}_n", sel.sum())
                    add(f"{L}_{name}_r2a_{g}_correct", (sel & (npl == gt)).sum())
                add(f"{L}_{name}_r2a_agree_target", (r2a & (npl == plB)).sum())
            add(f"{L}_r2a_n", r2a.sum())
            # cross-network alignment: mean cos between A's and B's clean prototypes of the same present class
            both = prA & prB
            add(f"{L}_proto_cos_AB", F.cosine_similarity(PA[both], PB[both], dim=1).mean())
        del fa2, fb1, fa1
    return {k: v for k, v in acc.items()}, nb


def summarise(acc, nb):
    s = {"batches": nb, "gamma_mean": acc["gamma"] / nb}
    for rn in ("r1", "r2", "r3"):
        s[f"frac_{rn}_all"] = acc[f"{rn}_all"] / acc["n_all"]
        for g in GROUPS:
            s[f"share_gt_{g}_in_{rn}"] = acc[f"{rn}_{g}"] / max(acc[f"n_{g}"], 1)
    d = lambda a, b: acc.get(a, 0) / max(acc.get(b, 0), 1)
    s.update({
        "r3_win_crack_precision": d("r3_win_crack_tp", "r3_win_crack_pred"),
        "r3_win_crack_precision_rel2": d("r3_win_crack_tp_rel2", "r3_win_crack_pred"),
        "r3_gtcrack_recall_win": d("r3_gtcrack_win_crack", "r3_crack"),
        "r3_gtcrack_recall_win_rel2": d("r3_gtcrack_win_crack_rel2", "r3_crack"),
        "r3_win_inact_precision": d("r3_win_inact_tp", "r3_win_inact_pred"),
        "r3_gtinact_recall_win": d("r3_gtinact_win_inact", "r3_inactive"),
        "r3_other_win_acc": d("r3_win_correct_other", "r3_other"),
        "r3_share_wmax_lt05": d("r3_wmax_lt05", "r3_all"),
        "r3_gtcrack_share_wmax_lt05": d("r3_gtcrack_wmax_lt05", "r3_crack"),
        "r3_mean_elem_target_sum": d("r3_elem_target_sum", "r3_all"),
        "r3_gtcrack_mean_elem_target_sum": d("r3_gtcrack_elem_target_sum", "r3_crack"),
        "r2_tgt_crack_precision": d("r2_tgt_crack_tp", "r2_tgt_crack_pred"),
        "r2_tgt_crack_precision_rel2": d("r2_tgt_crack_tp_rel2", "r2_tgt_crack_pred"),
        "r2_gtcrack_recall_tgt": d("r2_gtcrack_tgt_crack", "r2_crack"),
        "hp_frac_px": d("hp_px", "n_all"),
        "hp_crack_precision": d("hp_crack_tp", "hp_crack_pred"),
        "hp_crack_precision_rel2": d("hp_crack_tp_rel2", "hp_crack_pred"),
        "hp_gtcrack_coverage": d("hp_gtcrack_cov", "n_crack"),
    })
    for pk in ("dropout", "noise"):
        if acc.get(f"pert_{pk}_n"):
            s[f"pert_{pk}_batches"] = acc[f"pert_{pk}_n"]
            s[f"pert_{pk}_clean_crack_kept"] = d(f"pert_{pk}_crack_kept_clean_crack", f"pert_{pk}_clean_crack")
            s[f"pert_{pk}_conA2_mean"] = acc[f"pert_{pk}_conA2_mean"] / acc[f"pert_{pk}_n"]
            s[f"pert_{pk}_conA2_gtcrack_mean"] = d(f"pert_{pk}_conA2_gtcrack", f"pert_{pk}_gtcrack_px")
    for li in range(1, 6):
        if acc.get(f"fd_L{li}_n"):
            s[f"fd_L{li}_keep_all"] = acc[f"fd_L{li}_keep_all"] / acc[f"fd_L{li}_n"]
            s[f"fd_L{li}_keep_crack_cells"] = d(f"fd_L{li}_keep_crack_num", f"fd_L{li}_keep_crack_den")
    for L in LAYERS:
        s[f"{L}_crack_proto_present_B_rate"] = d(f"{L}_crack_proto_present_B", f"{L}_nbatch")
        s[f"{L}_proto_cos_AB_mean"] = acc[f"{L}_proto_cos_AB"] / max(acc[f"{L}_nbatch"], 1)
        for name in ("cross", "own"):
            for g in GROUPS:
                s[f"{L}_{name}_r2a_{g}_acc"] = d(f"{L}_{name}_r2a_{g}_correct", f"{L}_{name}_r2a_{g}_n")
            s[f"{L}_{name}_r2a_agree_target"] = d(f"{L}_{name}_r2a_agree_target", f"{L}_r2a_n")
    return s


# ---------------- gradient share ----------------
def grad_norm(loss, params):
    g = torch.autograd.grad(loss, params, retain_graph=False, allow_unused=True)
    return float(torch.sqrt(sum((x.float() ** 2).sum() for x in g if x is not None)))


def alhvr_unsup(sa1, sa2, sb1, sb2, fa2, fb1, beta, variant):
    """Network A's unlabelled loss terms (A's view) for a variant; returns dict of terms."""
    conA1, plA = sa1.max(1); conB1, plB = sb1.max(1)
    conA2, conB2 = sa2.max(1).values, sb2.max(1).values
    con = ((conA2 + conB2) / 2).detach().flatten()
    gamma = con.sort().values[: int(con.numel() * beta)].mean()
    r3 = ((conA2 < gamma) & (conB2 < gamma)).detach()
    r2a = ((conA2 <= gamma) & (conB2 > gamma)).detach()
    a_w = conA1 > conB1
    win = torch.where(a_w.unsqueeze(1), sa1, sb1)
    if variant["sharpen"] == "elementwise":
        tgt = sharpen_elem(win)
    else:
        tgt = torch.softmax(torch.log(win.clamp_min(1e-12)) * 10.0, 1)
    if variant["detach"]:
        tgt = tgt.detach()
    m3 = r3.float()
    mse = (((sa2 - tgt) ** 2).sum(1) * m3).sum() / (m3.sum() + 1e-16)
    def ent(p):
        pm = p * m3.unsqueeze(1)
        return (-(pm * torch.log(pm + 1e-6)).sum(1)).mean()
    terms = {"mse": mse, "ent": ent(sa1) + ent(sa2)}
    if variant["cpcl"]:
        PB, prB = protos(fb1, plB)
        f = F.normalize(fa2.float(), dim=1); p = F.normalize(PB.float(), dim=1)
        logits = torch.einsum("bchw,kc->bkhw", f, p) * variant["scale"]
        ce_l = logits.masked_fill((~prB).view(1, -1, 1, 1), -1e4)
        ce = F.cross_entropy(ce_l, plB, reduction="none")
        m2 = r2a.float()
        terms["ce"] = (ce * m2).sum() / (m2.sum() + 1e-16)
        if variant["pull_all"]:
            terms["cos"] = ((1 - logits[:, prB]) * m2.unsqueeze(1)).mean()
    return terms


def grad_probe(ma, mb, lab_dl, unl_dl, dev, beta, nbatch, seed, layer):
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)
    sup_crit = CEDiceLoss()
    params = [p for p in ma.parameters() if p.requires_grad]
    variants = {
        "ref_code": dict(sharpen="elementwise", detach=False, cpcl=True, scale=1.0, pull_all=True, layer="x_0_1"),
        "el_full": dict(sharpen="softmax", detach=True, cpcl=True, scale=10.0, pull_all=False, layer=layer),
        "el_dtct": dict(sharpen="softmax", detach=True, cpcl=False, scale=10.0, pull_all=False, layer=layer),
    }
    rec = {k: [] for k in ["sup", "bsm", "cps"] + list(variants)}
    term_rec = {k: {} for k in variants}
    li, ui = iter(lab_dl), iter(unl_dl)
    for i in range(nbatch):
        lb, ub = next(li), next(ui)
        xl, yl = lb["image"].to(dev), lb["mask"].to(dev).long()
        xu = ub["image"].to(dev)
        ma.train(); mb.train()
        with frozen_bn_stats(ma), frozen_bn_stats(mb):
            with torch.autocast("cuda", dtype=torch.bfloat16):
                lo = ma(xl)
            rec["sup"].append(grad_norm(sup_crit(lo.float(), yl), params))
            # BsM-like: teacher = A itself on the clean view, student on CutMix'd view, CE on conf >= 0.95 / all px
            g = torch.Generator().manual_seed(1000 + i)
            box = cutmix_boxes(xu.shape[0], xu.shape[-2], xu.shape[-1], 0.5, g).to(dev)
            with torch.no_grad(), torch.autocast("cuda", dtype=torch.bfloat16):
                tl = ma(xu).float()
            tl = mix_with_next(tl, box); xs = mix_with_next(xu, box)
            with torch.autocast("cuda", dtype=torch.bfloat16):
                sl = ma(xs).float()
            pt = torch.softmax(tl, 1); conf, lab = pt.max(1); msk = (conf >= 0.95).float()
            l_bsm = (F.cross_entropy(sl, lab, reduction="none") * msk).sum() / msk.numel()
            rec["bsm"].append(grad_norm(l_bsm, params))
            # ALHVR variants (A's loss; B forwards without grad)
            pa = PERT if PERT != "coin" else ("dropout" if random.random() > 0.5 else "noise")
            pb = PERT if PERT != "coin" else ("dropout" if random.random() > 0.5 else "noise")
            st_np = np.random.get_state(); st_t = torch.cuda.get_rng_state()
            for vn, v in variants.items():
                np.random.set_state(st_np); torch.cuda.set_rng_state(st_t)
                with torch.autocast("cuda", dtype=torch.bfloat16):
                    la1, ca1 = forward(ma, xu, None)
                    la2, ca2 = forward(ma, xu, pa)
                    with torch.no_grad():
                        lb1, cb1 = forward(mb, xu, None)
                        lb2, _ = forward(mb, xu, pb)
                up = lambda f: F.interpolate(f.float(), size=xu.shape[-2:], mode="bilinear", align_corners=False)
                sa1, sa2, sb1, sb2 = (torch.softmax(t.float(), 1) for t in (la1, la2, lb1, lb2))
                terms = alhvr_unsup(sa1, sa2, sb1, sb2, up(ca2[v["layer"]]), up(cb1[v["layer"]]).detach(), beta, v)
                tot = sum(terms.values())
                for tn, tv in terms.items():
                    term_rec[vn].setdefault(tn, []).append(float(tv.detach()))
                rec[vn].append(grad_norm(tot, params))
            # CPS-like on the perturbed pass: CE(A perturbed, B clean argmax), all pixels
            np.random.set_state(st_np); torch.cuda.set_rng_state(st_t)
            with torch.autocast("cuda", dtype=torch.bfloat16):
                la2, _ = forward(ma, xu, pa)
                with torch.no_grad():
                    lb1, _ = forward(mb, xu, None)
            l_cps = F.cross_entropy(la2.float(), lb1.float().argmax(1))
            rec["cps"].append(grad_norm(l_cps, params))
    out = {f"gnorm_{k}_median": float(np.median(v)) for k, v in rec.items()}
    for k in list(variants) + ["bsm", "cps"]:
        out[f"ratio_{k}_median"] = float(np.median(np.array(rec[k]) / np.array(rec["sup"])))
    for vn, tr in term_rec.items():
        for tn, tv in tr.items():
            out[f"term_{vn}_{tn}_mean"] = float(np.mean(tv))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pairs", nargs="+", required=True, help="runA:runB experiment dirs")
    ap.add_argument("--data", required=True)
    ap.add_argument("--beta", type=float, default=0.8)
    ap.add_argument("--grad_batches", type=int, default=12)
    ap.add_argument("--out", required=True)
    ap.add_argument("--perturb", default="coin", choices=["coin", "noise", "dropout"])
    a = ap.parse_args()
    global PERT
    PERT = a.perturb
    res_pert = a.perturb
    dev = torch.device("cuda")
    torch.backends.cudnn.benchmark = False
    D = Path(a.data)
    unl = sorted(load_split(D / "splits/seed0/unlabeled_5pct.txt"))
    labl = sorted(load_split(D / "splits/seed0/labeled_5pct.txt"))
    tf = get_weak_augmentation([0.5], [0.25], 512)
    g = torch.Generator().manual_seed(0)
    unl_ds = BenchmarkELDataset(D / "labeled/images", D / "labeled/masks_escdd", unl, tf)
    lab_ds = BenchmarkELDataset(D / "labeled/images", D / "labeled/masks_escdd", labl, tf)
    res = {"n_unlabelled": len(unl), "beta": a.beta, "perturb": res_pert, "pairs": {}}
    for pi, pr in enumerate(a.pairs):
        ra, rb = (Path(p) for p in pr.split(":"))
        ma, _ = load(ra, dev); mb, _ = load(rb, dev)
        dl = DataLoader(unl_ds, batch_size=8, shuffle=True, generator=torch.Generator().manual_seed(pi), drop_last=True, num_workers=4)
        acc, nb = probe_pair(ma, mb, dl, dev, a.beta, res, seed=pi)
        s = summarise(acc, nb)
        lab_dl = DataLoader(lab_ds, batch_size=8, shuffle=True, generator=torch.Generator().manual_seed(100 + pi), drop_last=True, num_workers=2)
        lab_dl_rep = [b for _ in range(8) for b in lab_dl]
        unl_dl = DataLoader(unl_ds, batch_size=8, shuffle=True, generator=torch.Generator().manual_seed(200 + pi), drop_last=True, num_workers=2)
        print(json.dumps({k: (round(v, 4) if isinstance(v, float) else v) for k, v in s.items()}, indent=0), flush=True)
        best_layer = "x_0_4" if s["x_0_4_cross_r2a_crack_acc"] >= s["x_0_1_cross_r2a_crack_acc"] - 0.02 else "x_0_1"
        s["grad"] = grad_probe(ma, mb, lab_dl_rep, unl_dl, dev, a.beta, a.grad_batches, seed=pi, layer=best_layer)
        s["grad"]["layer_used_for_el"] = best_layer
        res["pairs"][f"{ra.name}:{rb.name}"] = s
        print(json.dumps({k: (round(v, 4) if isinstance(v, float) else v) for k, v in s.items() if k != "grad"}, indent=0), flush=True)
        print(json.dumps(s["grad"], indent=0), flush=True)
        del ma, mb; torch.cuda.empty_cache()
    Path(a.out).write_text(json.dumps(res, indent=1))
    print("wrote", a.out)


if __name__ == "__main__":
    main()
