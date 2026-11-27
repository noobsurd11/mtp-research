"""elbench stage A6 (shared piece S3): one duplicate tool for three searches (WAVE3_REVIEW Y5; T12 leakage_audit_v02,
T8 C0, T9 pool_t9.txt). md5, then NCC, then a DINOv2 ViT-S/14 embedding, between every labelled / evaluation set (the
816 stems of cells.tsv: cv5v2 folds, legacy test 50, E1 106, 117 _rf, 11 aux_ext) and (a) each other, (b) the
11,938-cell unlabelled pool, (c) UCF-EL images on disk. Images only: no label and no prediction is read (sealed sets as
pixels only, lead's ruling L2). CPU only, deterministic, at most 8 workers; refuses to overwrite its outputs.
Reading rule and thresholds: results/stageA/A6_duplicates.md section 1 (bench/dup.py for the descriptors).

  python scripts/bench_dupsearch.py --out /home/noob/work/bench_reads/stageA/dup/run1 \
      --sheets /home/yugma/mtp/research/team_2026-11-12_frontier/results/stageA/dup_sheets --workers 8
Dry run on a subsample: --limit-pool 200 --limit-ucf 200 (outputs marked DRY).
"""
from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
import time
from multiprocessing import get_context
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from bench import derived, dumpfmt  # noqa: E402
from bench import dup as D  # noqa: E402

CELLS = Path("/home/noob/work/bench_data/meta/cells.tsv")
CELLS_MD5 = "a50521b4d0648766b28cc297869603ec"
GROUPS = Path("/home/noob/work/bench_data/meta/cv5v2_groups.tsv")
GROUPS_MD5 = "e44f06684df50607f4660d8d17e568ed"
LABELED_IMG = Path("/home/noob/work/el-fault-detection/data/labeled/images")
EXT_IMG = Path("/home/noob/work/el_f1/reports/f1/ext117/images")
RF_IMG = Path("/home/noob/work/calib/data/rf/images")
POOL_IMG = Path("/home/noob/work/el-fault-detection/data/unlabeled/images_512")
POOL_LIST = Path("/home/noob/work/el-fault-detection/data/splits/external_unlabeled.txt")
POOL_META = Path("/home/noob/work/el-fault-detection/data/splits/external_unlabeled_meta.csv")
UCF = Path("/home/noob/work/datasets/UCF-EL-Defect")
NCC_THR = 0.80
AUROC_MIN = 0.95
COLS = ("stem", "source", "image_id", "module_group", "cell_id", "role", "bench_set", "rf_set")


def git_state(root: Path) -> str:
    try:
        h = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True,
                           check=True).stdout.strip()
        dirty = subprocess.run(["git", "-C", str(root), "status", "--porcelain", "--untracked-files=no"],
                               capture_output=True, text=True, check=True).stdout.strip()
        return h + ("+dirty" if dirty else "")
    except Exception:
        return "unknown"


# ---------------------------------------------------------------- inventory
def labelled_items() -> tuple[list[dict], list[str]]:
    """The 816 labelled stems with image paths; only the COLS columns of cells.tsv are kept (no label columns)."""
    assert dumpfmt.md5_file(CELLS) == CELLS_MD5, "cells.tsv md5"
    assert dumpfmt.md5_file(GROUPS) == GROUPS_MD5, "cv5v2_groups.tsv md5"
    with open(CELLS) as f:
        r = csv.DictReader(f, delimiter="\t")
        rows = [{k: row[k] for k in COLS} for row in r]
    with open(GROUPS) as f:
        fold = {row["stem"]: int(row["fold"]) for row in csv.DictReader(f, delimiter="\t")}
    fb = derived.forbidden()
    items, missing = [], []
    for c in rows:
        bs = c["bench_set"]
        if bs.startswith("cv5v2:"):
            st, p = "P532", LABELED_IMG / f"{c['stem']}.png"
            assert int(bs.split(":f")[1]) == fold[c["stem"]], c["stem"]
        elif bs == "test50":
            st, p = "test50", LABELED_IMG / f"{c['stem']}.png"
        elif bs == "e1_106":
            st, p = "e1_106", EXT_IMG / f"{c['stem']}.png"
        elif bs == "aux_ext11":
            st, p = "ext11", EXT_IMG / f"{c['stem']}.png"
        elif bs == "aux_rf117":
            st = "rf_" + (c["rf_set"] or "none")
            p = RF_IMG / f"{c['stem']}.png"
            if not p.exists():                                  # rf cells kept out of rf/images: the pool copy if any
                q = POOL_IMG / f"{c['stem'][:-3]}.png"
                p = q if q.exists() else None
        else:
            raise AssertionError(f"unknown bench_set {bs!r}")
        it = {"stem": c["stem"], "set": st, "source": c["source"], "image_id": c["image_id"],
              "group": c["module_group"], "cell_id": c["cell_id"], "fold": fold.get(c["stem"], -1),
              "sealed": c["stem"] in fb, "path": str(p) if p else None}
        if p is None:
            missing.append(c["stem"])
            continue
        items.append(it)
    n = {s: sum(i["set"] == s for i in items) for s in ("P532", "test50", "e1_106", "ext11")}
    assert n == {"P532": 532, "test50": 50, "e1_106": 106, "ext11": 11}, n
    sealed_sets = {i["stem"] for i in items if i["set"] in ("test50", "e1_106")}
    assert sealed_sets <= fb, "a test50 / E1 stem is not on the forbidden list"
    return items, missing


def pool_items(limit: int = 0) -> list[dict]:
    stems = [l.strip() for l in open(POOL_LIST) if l.strip()]
    assert len(stems) == 11938, len(stems)
    meta = {r["stem"]: r for r in csv.DictReader(open(POOL_META))}
    if limit:
        stems = stems[:: max(1, len(stems) // limit)][:limit]
    return [{"stem": s, "set": "pool", "source": s[:4], "image_id": D.image_id(s), "celltype": meta[s]["group"],
             "native": f"{meta[s]['orig_w']}x{meta[s]['orig_h']}", "path": str(POOL_IMG / f"{s}.png")} for s in stems]


def ucf_items(limit: int = 0) -> list[dict]:
    split = {}
    for sp in ("train", "test"):
        for p in sorted((UCF / "training" / "data" / sp / "images").iterdir()):
            split[p.name] = sp
    names = sorted(p.name for p in (UCF / "Test_Images").iterdir())
    assert set(split) <= set(names), "UCF train / test images missing from Test_Images"
    if limit:
        names = names[:: max(1, len(names) // limit)][:limit]
    return [{"stem": n, "set": "ucf_" + split.get(n, "extra"), "path": str(UCF / "Test_Images" / n)} for n in names]


# ---------------------------------------------------------------- feature workers
def _feat(job):
    path, kind = job
    hb, hp, a = D.md5_pair(path)
    out = {"md5b": hb, "md5p": hp, "shape": list(a.shape)}
    if kind == "ucf":
        out["ncc"] = D.ncc_desc(a)
    else:
        out["ncc"] = D.ncc_desc(a)
        if kind == "lab":
            out["ncc_crop"] = D.ncc_desc(D.crop_cell(a))
        if kind == "pool":
            out["sd"] = D.content_sd(a)
    return out


_EMB = None


def _emb_init():
    global _EMB
    import os
    os.environ["OMP_NUM_THREADS"] = "1"
    _EMB = D.Embedder()


def _emb(job):
    paths, mode = job
    xs = []
    for p in paths:
        a = D.load_gray(p)
        if mode == "crop8":
            a = D.crop_cell(a)
        x = D.emb_input(a)
        if mode in ("full8", "crop8"):
            xs += [np.ascontiguousarray(D.dihedral(x, k)) for k in range(8)]
        else:
            xs.append(x)
    f = _EMB(np.stack(xs))
    return f.reshape(len(paths), -1, f.shape[-1])


def features(items: list[dict], kind: str, pool, fdir: Path, tag: str, t0: float) -> dict:
    p = fdir / f"feat_{tag}.npz"
    if p.exists():
        z = np.load(p, allow_pickle=False)
        assert list(z["stems"]) == [i["stem"] for i in items], f"{p}: stem list differs"
        print(f"[{time.time() - t0:.0f}s] features {tag}: reused {p}", flush=True)
        return {k: z[k] for k in z.files}
    res = pool.map(_feat, [(i["path"], kind) for i in items], chunksize=16)
    out = {"stems": np.array([i["stem"] for i in items]), "md5b": np.array([r["md5b"] for r in res]),
           "md5p": np.array([r["md5p"] for r in res]), "ncc": np.stack([r["ncc"] for r in res]).astype(np.float32)}
    if kind == "lab":
        out["ncc_crop"] = np.stack([r["ncc_crop"] for r in res]).astype(np.float32)
    if kind == "pool":
        out["sd"] = np.array([r["sd"] for r in res], np.float64)
    np.savez(p, **out)
    print(f"[{time.time() - t0:.0f}s] features {tag}: {len(items)} images -> {p}", flush=True)
    return out


def embeddings(items: list[dict], mode: str, epool, fdir: Path, tag: str, t0: float) -> np.ndarray:
    p = fdir / f"emb_{tag}_{mode}.npy"
    if p.exists():
        e = np.load(p)
        assert e.shape[0] == len(items)
        print(f"[{time.time() - t0:.0f}s] embeddings {tag} {mode}: reused {p}", flush=True)
        return e
    paths = [i["path"] for i in items]
    bs = 2 if mode in ("full8", "crop8") else 16
    chunks = [(paths[i:i + bs], mode) for i in range(0, len(paths), bs)]
    e = np.concatenate(epool.map(_emb, chunks, chunksize=1), 0).astype(np.float32)
    np.save(p, e)
    print(f"[{time.time() - t0:.0f}s] embeddings {tag} {mode}: {e.shape} -> {p}", flush=True)
    return e


# ---------------------------------------------------------------- outputs
def write_tsv(p: Path, header: list[str], rows: list) -> str:
    if p.exists():
        raise FileExistsError(p)
    with open(p, "w") as f:
        f.write("\t".join(header) + "\n")
        for r in rows:
            f.write("\t".join(f"{x:.4f}" if isinstance(x, float) else str(x) for x in r) + "\n")
    return dumpfmt.md5_file(p)


def sheet(pairs: list[tuple], out: Path, title: str, px: int = 160) -> None:
    """Contact sheet: one row per pair (query image in its best view, partner), caption with ids and scores.
    pairs: (path_a, view, path_b, caption). Never called with a sealed image (asserted by the caller)."""
    from PIL import Image, ImageDraw
    if out.exists():
        raise FileExistsError(out)
    n = len(pairs)
    ncol = 2
    nrow = (n + ncol - 1) // ncol
    cw, ch = 2 * px + 24, px + 30
    W = Image.new("L", (ncol * cw, 24 + max(nrow, 1) * ch), 255)
    dr = ImageDraw.Draw(W)
    dr.text((4, 4), title[:180], fill=0)
    for i, (pa, v, pb, cap) in enumerate(pairs):
        x0, y0 = (i % ncol) * cw, 24 + (i // ncol) * ch
        a = D.load_gray(pa)
        if a.shape == (512, 512) and "crop" in cap:
            a = D.crop_cell(a)
        a = np.ascontiguousarray(D.dihedral(a, int(v)))
        b = D.load_gray(pb)
        W.paste(Image.fromarray(a).resize((px, px)), (x0 + 4, y0 + 2))
        W.paste(Image.fromarray(b).resize((px, px)), (x0 + px + 12, y0 + 2))
        dr.text((x0 + 4, y0 + px + 4), cap[:60], fill=0)
    out.parent.mkdir(parents=True, exist_ok=True)
    W.save(out)


def main(argv=None) -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--sheets", required=True, help="folder for the contact sheet PNGs (no sealed image is drawn)")
    ap.add_argument("--feats", default=None, help="feature cache folder (default <out>/feats)")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--limit-pool", type=int, default=0)
    ap.add_argument("--limit-ucf", type=int, default=0)
    ap.add_argument("--no-ucf", action="store_true")
    ap.add_argument("--tau", type=float, default=None,
                    help="embedding threshold set by the lead (default: the T12 rule, 5th pct of known same-cell pairs)")
    a = ap.parse_args(argv)
    t0 = time.time()
    if a.workers > 8:
        sys.exit("at most 8 workers")
    out = Path(a.out)
    if (out / "summary.txt").exists():
        sys.exit(f"refuse: {out / 'summary.txt'} exists")
    dry = bool(a.limit_pool or a.limit_ucf)
    fdir = Path(a.feats) if a.feats else out / "feats"
    fdir.mkdir(parents=True, exist_ok=True)
    sheets = Path(a.sheets)
    tool_md5 = dumpfmt.md5_file(__file__)
    commit = git_state(ROOT)
    lab, missing = labelled_items()
    pool_it = pool_items(a.limit_pool)
    ucf_it = [] if a.no_ucf else ucf_items(a.limit_ucf)
    man = {"tool": "bench_dupsearch.py", "tool_md5": tool_md5, "dup_py_md5": dumpfmt.md5_file(ROOT / "bench" / "dup.py"),
           "code": commit, "cells_tsv": CELLS_MD5, "cv5v2_groups": GROUPS_MD5, "forbidden": derived.FORBIDDEN_MD5,
           "pool_list": dumpfmt.md5_file(POOL_LIST), "pool_meta": dumpfmt.md5_file(POOL_META),
           "weights": D.WEIGHTS_MD5, "dry": dry, "n_labelled": len(lab), "labelled_missing_image": missing,
           "n_pool": len(pool_it), "n_ucf": len(ucf_it)}
    print(f"inputs: {json.dumps(man)}", flush=True)
    pool = get_context("fork").Pool(a.workers) if a.workers > 1 else None

    class _Seq:
        map = staticmethod(lambda f, j, chunksize=1: list(map(f, j)))
    pool = pool or _Seq()
    FL = features(lab, "lab", pool, fdir, "lab", t0)
    FP = features(pool_it, "pool", pool, fdir, "pool" + ("_dry" if dry else ""), t0)
    FU = features(ucf_it, "ucf", pool, fdir, "ucf" + ("_dry" if dry else ""), t0) if ucf_it else None
    if a.workers > 1:
        pool.close(); pool.join()
    epool = get_context("fork").Pool(a.workers, initializer=_emb_init) if a.workers > 1 else None
    if epool is None:
        _emb_init()
        epool = _Seq()
    EL8 = embeddings(lab, "full8", epool, fdir, "lab", t0)                      # (816, 8, 384)
    EP = embeddings(pool_it, "full1", epool, fdir, "pool" + ("_dry" if dry else ""), t0)[:, 0]
    if ucf_it:
        ELc8 = embeddings(lab, "crop8", epool, fdir, "lab", t0)
        EU = embeddings(ucf_it, "full1", epool, fdir, "ucf" + ("_dry" if dry else ""), t0)[:, 0]
    if not isinstance(epool, _Seq):
        epool.close(); epool.join()

    # ---- (a) labelled x labelled
    nL = len(lab)
    QL = np.stack([D.views(d.reshape(D.S_NCC, D.S_NCC)) for d in FL["ncc"]])  # (816, 8, d)
    DL = FL["ncc"].reshape(nL, -1)
    Sn, Vn = D.max_over_views(QL, DL)
    Se, Ve = D.max_over_views(EL8, EL8[:, 0])
    print(f"[{time.time() - t0:.0f}s] labelled search done", flush=True)
    iu = np.triu_indices(nL, 1)
    def sym(S, V):
        a_, b_ = S[iu], S.T[iu]
        return np.maximum(a_, b_), np.where(a_ >= b_, V[iu], V.T[iu])
    sn, vn = sym(Sn, Vn)
    se, ve = sym(Se, Ve)
    I, J = iu
    src = np.array([i["source"] for i in lab]); grp = np.array([i["group"] for i in lab])
    cid = np.array([i["cell_id"] for i in lab]); sets_ = np.array([i["set"] for i in lab])
    fold = np.array([i["fold"] for i in lab]); sealed = np.array([i["sealed"] for i in lab])
    known = cid[I] == cid[J]
    diffsrc = src[I] != src[J]
    au_e, au_n = D.auroc(se[known], se[diffsrc]), D.auroc(sn[known], sn[diffsrc])
    tau_rule = D.tau_from_known(se[known])
    tau = tau_rule if a.tau is None else float(a.tau)
    fa_e = float((se[diffsrc] >= tau).mean()); fa_n = float((sn[diffsrc] >= NCC_THR).mean())
    pre_ok = bool(au_e >= AUROC_MIN)
    calib = {"n_known_pairs": int(known.sum()), "n_known_cells": int(len({c for c in cid[I][known]})),
             "n_diff_source_pairs": int(diffsrc.sum()), "auroc_emb": au_e, "auroc_ncc": au_n, "tau": tau,
             "tau_rule_t12": tau_rule, "tau_source": "T12 rule" if a.tau is None else "override (--tau)",
             "fa_emb_at_tau": fa_e, "fa_ncc_at_0.80": fa_n, "precheck_pass": pre_ok,
             "known_emb_min_med_max": [float(se[known].min()), float(np.median(se[known])), float(se[known].max())],
             "known_ncc_min_med_max": [float(sn[known].min()), float(np.median(sn[known])), float(sn[known].max())],
             "known_ncc_share_ge_0.80": float((sn[known] >= NCC_THR).mean()),
             "diffsrc_emb_p99_max": [float(np.percentile(se[diffsrc], 99)), float(se[diffsrc].max())],
             "diffsrc_ncc_p99_max": [float(np.percentile(sn[diffsrc], 99)), float(sn[diffsrc].max())]}
    print(f"[{time.time() - t0:.0f}s] calibration {json.dumps(calib)}", flush=True)
    emb_used = pre_ok
    md5L = {}
    for k, i in enumerate(lab):
        for h in (FL["md5b"][k], FL["md5p"][k]):
            md5L.setdefault(str(h), []).append(k)
    md5_pair = np.array([FL["md5b"][i] == FL["md5b"][j] or FL["md5p"][i] == FL["md5p"][j] for i, j in zip(I, J)])
    flag = md5_pair | (sn >= NCC_THR) | ((se >= tau) if emb_used else False)
    same_grp = grp[I] == grp[J]
    new = flag & ~same_grp

    def cat(i, j):
        s = {sets_[i], sets_[j]}
        if s == {"P532"}:
            return "P532_crossfold" if fold[i] != fold[j] else "P532_samefold"
        if "e1_106" in s:
            return "with_E1"
        if "test50" in s:
            return "test_P532" if "P532" in s else "test_other"
        if "P532" in s:
            return "P532_" + "_".join(sorted(s - {"P532"}))
        return "other_" + "_".join(sorted(s))
    keep = (sn >= 0.5) | (se >= tau - 0.05) | md5_pair | known
    rows = []
    for k in np.nonzero(keep)[0]:
        i, j = int(I[k]), int(J[k])
        rows.append([lab[i]["stem"], sets_[i], fold[i], lab[j]["stem"], sets_[j], fold[j], int(same_grp[k]),
                     int(known[k]), float(sn[k]), int(vn[k]), float(se[k]), int(ve[k]), int(md5_pair[k]), int(flag[k]),
                     cat(i, j)])
    rows.sort(key=lambda r: (-r[13], -max(r[8], r[10])))
    out.mkdir(parents=True, exist_ok=True)
    md5s = {}
    hdr = ["a", "a_set", "a_fold", "b", "b_set", "b_fold", "same_group", "known_same_cell", "ncc", "ncc_view", "cos",
           "cos_view", "md5", "flagged", "category"]
    md5s["pairs_labelled.tsv"] = write_tsv(out / "pairs_labelled.tsv", hdr, rows)
    links = [r for r in rows if r[13] and not r[6] and r[14] == "P532_crossfold"]
    md5s["new_group_links.tsv"] = write_tsv(out / "new_group_links.tsv", hdr, links)
    sealed_rows = [r for r in rows if r[13] and not r[6] and (r[1] in ("test50", "e1_106") or r[4] in ("test50", "e1_106"))]
    md5s["flagged_sealed_pairs.tsv"] = write_tsv(out / "flagged_sealed_pairs.tsv", hdr, sealed_rows)
    cats = {}
    for k in np.nonzero(new)[0]:
        c = cat(int(I[k]), int(J[k]))
        d = cats.setdefault(c, {"pairs": 0, "md5": 0, "ncc": 0, "emb": 0})
        d["pairs"] += 1; d["md5"] += int(md5_pair[k]); d["ncc"] += int(sn[k] >= NCC_THR); d["emb"] += int(se[k] >= tau)
    print(f"[{time.time() - t0:.0f}s] labelled: flagged new pairs per category {json.dumps(cats)}", flush=True)

    # ---- (b) pool
    nP = len(pool_it)
    Snp, Vnp = D.max_over_views(QL, FP["ncc"].reshape(nP, -1))
    Sep, Vep = D.max_over_views(EL8, EP)
    ids816 = {i["image_id"] for i in lab} | {i["group"] for i in lab} | {D.image_id(i["stem"]) for i in lab} | \
             {D.image_id(m) for m in missing}
    bn, be = Snp.max(0), Sep.max(0)
    an, ae = Snp.argmax(0), Sep.argmax(0)
    notsealed = ~sealed
    Snp_o, Sep_o = np.where(notsealed[:, None], Snp, -np.inf), np.where(notsealed[:, None], Sep, -np.inf)
    an_o, ae_o = Snp_o.argmax(0), Sep_o.argmax(0)
    prow, kept, excl, ncc_only = [], [], [], []
    for k, it in enumerate(pool_it):
        mod = it["image_id"] in ids816
        m5 = [lab[x]["stem"] for x in md5L.get(str(FP["md5b"][k]), []) + md5L.get(str(FP["md5p"][k]), [])]
        e_hit = bool(be[k] >= tau) if emb_used else False
        n_hit = bool(bn[k] >= NCC_THR)
        reasons = [r for r, f in (("module", mod), ("md5", bool(m5)), ("emb", e_hit),
                                  ("ncc_fallback", n_hit and not emb_used)) if f]
        prow.append([it["stem"], int(mod), ";".join(sorted(set(m5))) or "-", float(bn[k]), lab[an[k]]["stem"],
                     float(be[k]), lab[ae[k]]["stem"], int(n_hit), int(e_hit), ",".join(reasons) or "-"])
        if reasons:
            excl.append(it)
        else:
            kept.append(it)
            if n_hit:
                ncc_only.append([it["stem"], float(bn[k]), lab[an[k]]["stem"], lab[an[k]]["set"], float(be[k])])
    phdr = ["pool_stem", "module_hit", "md5_hit", "ncc_best", "ncc_partner", "cos_best", "cos_partner", "ncc_ge_0.80",
            "cos_ge_tau", "excluded_by"]
    md5s["pool_best.tsv"] = write_tsv(out / "pool_best.tsv", phdr, prow)
    md5s["pool_ncc_only.tsv"] = write_tsv(out / "pool_ncc_only.tsv", ["pool_stem", "ncc", "partner", "partner_set", "cos"],
                                          ncc_only)
    # fail-closed asserts on the list
    kept_ids = {i["image_id"] for i in kept}
    assert not (kept_ids & ids816), "pool_t9 shares an image id with a labelled / evaluation set"
    assert not ({i["stem"] for i in kept} & derived.forbidden()), "pool_t9 holds a forbidden stem"
    assert not ({i["stem"] for i in kept} & {i["stem"] for i in lab}), "pool_t9 holds a labelled stem"
    pl = out / "pool_t9.txt"
    if pl.exists():
        raise FileExistsError(pl)
    pl.write_text("".join(i["stem"] + "\n" for i in kept))
    md5s["pool_t9.txt"] = dumpfmt.md5_file(pl)
    sdk = {s: float(v) for s, v in zip(FP["stems"], FP["sd"])}
    md5s["pool_t9.meta.tsv"] = write_tsv(out / "pool_t9.meta.tsv", ["stem", "source", "cell_type", "native_size", "content_sd"],
                                         [[i["stem"], i["source"], i["celltype"], i["native"], sdk[i["stem"]]] for i in kept])
    pool_counts = {"pool": nP, "kept": len(kept), "excluded": len(excl),
                   "by_reason": {r: sum(1 for p in prow if r in p[9].split(",")) for r in ("module", "md5", "emb", "ncc_fallback")},
                   "only_emb": sum(1 for p in prow if p[9] == "emb"), "only_md5": sum(1 for p in prow if p[9] == "md5"),
                   "ncc_ge_0.80_not_excluded": len(ncc_only),
                   "emb_hits_by_partner_set": {}, "kept_by_type": {}}
    for p, it in zip(prow, pool_it):
        if p[8]:
            s = lab[[x["stem"] for x in lab].index(p[6])]["set"]
            pool_counts["emb_hits_by_partner_set"][s] = pool_counts["emb_hits_by_partner_set"].get(s, 0) + 1
    for i in kept:
        pool_counts["kept_by_type"][i["celltype"]] = pool_counts["kept_by_type"].get(i["celltype"], 0) + 1
    print(f"[{time.time() - t0:.0f}s] pool: {json.dumps(pool_counts)}", flush=True)

    # ---- (c) UCF
    ucf_counts = None
    if ucf_it:
        nU = len(ucf_it)
        QLc = np.stack([D.views(d.reshape(D.S_NCC, D.S_NCC)) for d in FL["ncc_crop"]])
        Snu, Vnu = D.max_over_views(QLc, FU["ncc"].reshape(nU, -1))
        Seu, Veu = D.max_over_views(ELc8, EU)
        Snu_o, Seu_o = np.where(notsealed[:, None], Snu, -np.inf), np.where(notsealed[:, None], Seu, -np.inf)
        bnu, beu, anu, aeu = Snu.max(0), Seu.max(0), Snu.argmax(0), Seu.argmax(0)
        urow, uex, uemb = [], [], []
        for k, it in enumerate(ucf_it):
            m5 = [lab[x]["stem"] for x in md5L.get(str(FU["md5b"][k]), []) + md5L.get(str(FU["md5p"][k]), [])]
            n_hit, e_hit = bool(bnu[k] >= NCC_THR), bool(beu[k] >= tau)
            urow.append([it["stem"], it["set"], ";".join(sorted(set(m5))) or "-", float(bnu[k]), lab[anu[k]]["stem"],
                         float(beu[k]), lab[aeu[k]]["stem"], int(n_hit), int(e_hit)])
            if m5 or n_hit:
                uex.append([it["stem"], it["set"], "md5" if m5 else "ncc", float(bnu[k]), lab[anu[k]]["stem"]])
            if e_hit:
                uemb.append([it["stem"], it["set"], float(beu[k]), lab[aeu[k]]["stem"], lab[aeu[k]]["set"]])
        uh = ["ucf_image", "ucf_split", "md5_hit", "ncc_best", "ncc_partner", "cos_best", "cos_partner", "ncc_ge_0.80",
              "cos_ge_tau"]
        md5s["ucf_best.tsv"] = write_tsv(out / "ucf_best.tsv", uh, urow)
        md5s["ucf_exclusions.tsv"] = write_tsv(out / "ucf_exclusions.tsv", ["ucf_image", "ucf_split", "rule", "ncc",
                                                                             "partner"], uex)
        md5s["ucf_emb_hits.tsv"] = write_tsv(out / "ucf_emb_hits.tsv", ["ucf_image", "ucf_split", "cos", "partner",
                                                                         "partner_set"], uemb)
        ucf_counts = {"ucf": nU, "excluded_c0": len(uex), "md5": sum(1 for r in uex if r[2] == "md5"),
                      "ncc": sum(1 for r in uex if r[2] == "ncc"), "emb_hits": len(uemb),
                      "ncc_max": float(bnu.max()), "cos_max": float(beu.max()),
                      "ncc_p99": float(np.percentile(bnu, 99)), "cos_p99": float(np.percentile(beu, 99))}
        print(f"[{time.time() - t0:.0f}s] ucf: {json.dumps(ucf_counts)}", flush=True)

    # ---- contact sheets (top 40 pairs per search and score; no sealed image is drawn)
    sheet_md5 = {}
    def emit(name, pairs, title):
        for pa, _, pb, _ in pairs:
            for p in (pa, pb):
                st = Path(p).stem
                assert st not in derived.forbidden() and st not in sealed_stems, f"sealed image {st} in a sheet"
        f = sheets / f"{'DRY_' if dry else ''}{name}.png"
        sheet(pairs, f, title)
        sheet_md5[f.name] = dumpfmt.md5_file(f)
    sealed_stems = {i["stem"] for i in lab if i["sealed"]}
    pathL = [i["path"] for i in lab]
    for score, col, vcol, nm in (("ncc", 8, 9, "NCC"), ("cos", 10, 11, "embedding")):
        cand = [r for r in rows if not r[6] and r[1] not in ("test50", "e1_106", "ext11")
                and r[4] not in ("test50", "e1_106", "ext11") and r[0] not in sealed_stems and r[3] not in sealed_stems]
        cand.sort(key=lambda r: -r[col])
        top = cand[:40]
        idx = {i["stem"]: k for k, i in enumerate(lab)}
        VV = Vn if score == "ncc" else Ve
        emit(f"labelled_{score}", [(pathL[idx[r[0]]], VV[idx[r[0]], idx[r[3]]], pathL[idx[r[3]]],
                                    f"{r[0]}|{r[3]} {score} {r[col]:.3f} {r[14]}") for r in top],
             f"(a) labelled pairs not in one module group, top {len(top)} by {nm}; left = first cell in its best view")
    for score, S_o, A_o, V_ in (("ncc", Snp_o, an_o, Vnp), ("cos", Sep_o, ae_o, Vep)):
        best = S_o.max(0)
        order = [k for k in np.argsort(-best, kind="stable") if not prow[k][1]][:40]
        emit(f"pool_{score}", [(pathL[A_o[k]], V_[A_o[k], k], pool_it[k]["path"],
                                f"{lab[A_o[k]]['stem']}|{pool_it[k]['stem']} {score} {best[k]:.3f}") for k in order],
             f"(b) pool cells (no module match) and their best open labelled partner, top {len(order)} by {score}")
    if ucf_it:
        for score, S_o, V_ in (("ncc", Snu_o, Vnu), ("cos", Seu_o, Veu)):
            best, arg = S_o.max(0), S_o.argmax(0)
            order = list(np.argsort(-best, kind="stable")[:40])
            emit(f"ucf_{score}", [(pathL[arg[k]], V_[arg[k], k], ucf_it[k]["path"],
                                   f"crop {lab[arg[k]]['stem']}|{ucf_it[k]['stem'][:28]} {score} {best[k]:.3f}") for k in order],
                 f"(c) UCF-EL images and their best open labelled partner (central cell crop), top {len(order)} by {score}")

    summ = {"manifest": man, "calibration": calib, "embedding_used_for_decisions": emb_used, "ncc_threshold": NCC_THR,
            "labelled_new_flagged_by_category": cats, "n_new_group_links": len(links),
            "n_flagged_sealed_pairs": len(sealed_rows), "pool": pool_counts, "ucf": ucf_counts, "md5": md5s,
            "sheets": sheet_md5, "seconds": round(time.time() - t0)}
    (out / "summary.json").write_text(json.dumps(summ, indent=1, default=float))
    L = [f"# duplicate search (bench_dupsearch.py {tool_md5[:8]}, dup.py {man['dup_py_md5'][:8]}, code {commit[:12]})"
         + (" DRY SUBSAMPLE" if dry else ""),
         f"inputs: cells.tsv {CELLS_MD5[:8]}, cv5v2_groups {GROUPS_MD5[:8]}, forbidden {derived.FORBIDDEN_MD5[:8]}, "
         f"pool list {man['pool_list'][:8]}, weights {D.WEIGHTS_MD5[:8]}; labelled {len(lab)} (no image: {missing}); "
         f"pool {nP}; UCF {len(ucf_it)}",
         "## calibration on known same-cell pairs (cells.tsv cell_id) vs different-source pairs",
         json.dumps(calib, default=float),
         f"embedding used for decisions: {emb_used} (pre-check AUROC >= {AUROC_MIN})",
         "## (a) labelled: flagged pairs not already in one module group, per category (pairs, md5, ncc>=0.80, cos>=tau)",
         json.dumps(cats), f"new group links (P532 across folds): {len(links)}; flagged pairs with a sealed cell: {len(sealed_rows)}",
         "## (b) pool", json.dumps(pool_counts), f"pool_t9.txt {len(kept)} stems md5 {md5s['pool_t9.txt']}",
         "## (c) UCF-EL", json.dumps(ucf_counts), "## output md5", json.dumps(md5s), json.dumps(sheet_md5),
         f"seconds {round(time.time() - t0)}"]
    (out / "summary.txt").write_text("\n".join(L) + "\n")
    print("\n".join(L), flush=True)


if __name__ == "__main__":
    main()
