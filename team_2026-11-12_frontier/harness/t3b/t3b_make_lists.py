"""T3b frozen lists (T3B_RULE.md section 2): K = 5 folds by image id = column k5_fold of the draft file, and the fixed half
of each fold's training-side E1 image ids. Reads ONLY the draft file benchmark/out/t3b_draft_folds.tsv (md5 pinned; made
12 Nov 2026 by benchdesign from list files and ground-truth counts) and the E1 list ext117/stems_eval.txt (md5 pinned; stem
names only). No mask, ignore file, image or prediction is opened.

Half of fold k (deterministic, no random draw): U = the image ids with k5_fold != k; H = floor(|U| / 2) of them, chosen to
minimise J(H) = |hard(H) - hard(U) / 2| / hard(U) + |cells(H) - cells(U) / 2| / cells(U), where hard = crack px of the
cells with e1_stratum 'halfcut+scuff' (the hard stratum) and cells = cell count. Start: ids sorted by (-hard, -cells, id),
each put on the side (H or rest) whose running hard px is lower (cells, then the side H first on ties) while that side has
room; then best-swap descent: among all swaps (u in H, v in rest) take the one with the lowest J (ties: the
lexicographically smallest (u, v)); stop when no swap lowers J by more than 1e-12.

Writes (refuses an existing OUT): t3b_folds.tsv (stem, image_id, fold), e1t3b_f<k>.txt (held-out stems of fold k, E1 list
order), t3b_half_f<k>.txt (the half arm's training-side E1 stems of fold k, E1 list order), t3b_half_ids.tsv,
t3b_strata.tsv (stem, stratum from e1_stratum), t3b_hard_stems.txt, e1_106_stems.txt (copy of the E1 list),
LISTS_REPORT.txt (balance per fold), LISTS.md5.
Usage: python -I t3b_make_lists.py DRAFT_TSV E1_STEMS_EVAL OUT
"""
import hashlib
import sys
from collections import defaultdict
from pathlib import Path

DRAFT_MD5 = "49e704136824e951c8d460a20eb0eb2c"
E1_LIST_MD5 = "5266806b559f74bcf9eae167bb076b95"
K = 5
HARD = "halfcut+scuff"


def md5(p):
    return hashlib.md5(Path(p).read_bytes()).hexdigest()


def J(H, U, hard, cells):
    hU = sum(hard[u] for u in U)
    cU = sum(cells[u] for u in U)
    hH = sum(hard[u] for u in H)
    cH = sum(cells[u] for u in H)
    return abs(hH - hU / 2) / max(hU, 1) + abs(cH - cU / 2) / max(cU, 1)


def pick_half(U, hard, cells):
    U = sorted(U)
    n = len(U) // 2
    order = sorted(U, key=lambda u: (-hard[u], -cells[u], u))
    H, R = [], []
    for u in order:
        hh = (sum(hard[x] for x in H), sum(cells[x] for x in H), 0)
        hr = (sum(hard[x] for x in R), sum(cells[x] for x in R), 1)
        if len(H) >= n:
            R.append(u)
        elif len(R) >= len(U) - n:
            H.append(u)
        elif hh <= hr:
            H.append(u)
        else:
            R.append(u)
    H, R = set(H), set(R)
    cur = J(H, U, hard, cells)
    while True:
        best = None
        for u in sorted(H):
            for v in sorted(R):
                j = J((H - {u}) | {v}, U, hard, cells)
                if best is None or j < best[0] - 1e-15:
                    best = (j, u, v)
        if best is None or best[0] >= cur - 1e-12:
            break
        cur, u, v = best
        H, R = (H - {u}) | {v}, (R - {v}) | {u}
    assert len(H) == n
    return sorted(H), cur


def main(argv):
    draft, e1list, out = Path(argv[0]), Path(argv[1]), Path(argv[2])
    assert md5(draft) == DRAFT_MD5, f"draft file md5 {md5(draft)} != pinned {DRAFT_MD5}"
    assert md5(e1list) == E1_LIST_MD5, f"E1 list md5 {md5(e1list)} != pinned {E1_LIST_MD5}"
    if out.exists():
        sys.exit(f"refuse: {out} exists")
    rows = [l.rstrip("\n").split("\t") for l in open(draft) if l.strip()]
    hdr = rows[0]
    assert hdr == ["stem", "image_id", "family_gap5", "e1_stratum", "crack_px", "k3_fold", "k5_fold"], hdr
    R = [dict(zip(hdr, r)) for r in rows[1:]]
    e1 = [l.strip() for l in open(e1list) if l.strip()]
    assert len(e1) == 106 and len(set(e1)) == 106
    assert sorted(r["stem"] for r in R) == sorted(e1), "draft stems != E1 list"
    by = {r["stem"]: r for r in R}
    fold = {s: int(by[s]["k5_fold"]) for s in e1}
    img = {s: by[s]["image_id"] for s in e1}
    assert all(s.startswith(img[s] + "_") or s.startswith(img[s] + "-") for s in e1), "image id is not the stem prefix"
    idf = defaultdict(set)
    for s in e1:
        idf[img[s]].add(fold[s])
    assert all(len(v) == 1 for v in idf.values()), "an image id in two folds"
    assert set(fold.values()) == set(range(K))
    assert len(idf) == 71, len(idf)
    strat = {s: by[s]["e1_stratum"] for s in e1}
    assert set(strat.values()) <= {"full", "full+scuff", "halfcut", "halfcut+scuff"}
    cpx = {s: int(by[s]["crack_px"]) for s in e1}
    hard = defaultdict(int)
    cells = defaultdict(int)
    for s in e1:
        cells[img[s]] += 1
        if strat[s] == HARD:
            hard[img[s]] += cpx[s]
    out.mkdir(parents=True)
    files = {}
    files["e1_106_stems.txt"] = e1list.read_text()
    files["t3b_folds.tsv"] = "stem\timage_id\tfold\n" + "".join(f"{s}\t{img[s]}\t{fold[s]}\n" for s in e1)
    files["t3b_strata.tsv"] = "stem\tstratum\n" + "".join(f"{s}\t{strat[s]}\n" for s in e1)
    files["t3b_hard_stems.txt"] = "".join(f"{s}\n" for s in e1 if strat[s] == HARD)
    ids_rows = ["fold\timage_id\tin_half\tcells\thard_crack_px\n"]
    rep = ["T3b lists: K = 5 folds by image id (draft column k5_fold); half = floor(n_ids / 2) training-side ids per fold",
           f"draft {draft} md5 {DRAFT_MD5}; E1 list md5 {E1_LIST_MD5}",
           "fold | held-out cells / ids | train-side cells / ids / hard crack px / crack px | half ids / cells (share) / "
           "hard crack px (share) / crack px (share) / hard crack cells | J"]
    for k in range(K):
        ho = [s for s in e1 if fold[s] == k]
        tr = [s for s in e1 if fold[s] != k]
        U = sorted({img[s] for s in tr})
        H, j = pick_half(U, hard, cells)
        Hs = set(H)
        half = [s for s in tr if img[s] in Hs]
        files[f"e1t3b_f{k}.txt"] = "".join(f"{s}\n" for s in ho)
        files[f"t3b_half_f{k}.txt"] = "".join(f"{s}\n" for s in half)
        for u in U:
            ids_rows.append(f"{k}\t{u}\t{int(u in Hs)}\t{cells[u]}\t{hard[u]}\n")
        hU, cU = sum(hard[u] for u in U), sum(cells[u] for u in U)
        pU = sum(cpx[s] for s in tr)
        hH, cH = sum(hard[u] for u in H), sum(cells[u] for u in H)
        pH = sum(cpx[s] for s in half)
        hcc = sum(1 for s in half if strat[s] == HARD and cpx[s] >= 20)
        rep.append(f"f{k} | {len(ho)} / {len({img[s] for s in ho})} | {len(tr)} / {len(U)} / {hU} / {pU} | "
                   f"{len(H)} / {cH} ({cH / cU:.3f}) / {hH} ({hH / max(hU, 1):.3f}) / {pH} ({pH / max(pU, 1):.3f}) / {hcc} | {j:.4f}")
    files["t3b_half_ids.tsv"] = "".join(ids_rows)
    files["LISTS_REPORT.txt"] = "\n".join(rep) + "\n"
    for n, t in files.items():
        (out / n).write_text(t)
    man = "".join(f"{hashlib.md5((out / n).read_bytes()).hexdigest()}  {n}\n" for n in sorted(files))
    (out / "LISTS.md5").write_text(man)
    print(files["LISTS_REPORT.txt"], end="")
    print(f"LISTS.md5 {md5(out / 'LISTS.md5')}")


if __name__ == "__main__":
    main(sys.argv[1:])
