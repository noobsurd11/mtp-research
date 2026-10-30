"""F3 patch (runner, 30 Oct): CP at 100% labels. Run from the el_f3 worktree root. Edits src/data/copy_paste.py
build_cp_stream: (1) optional cp.library_exclude (stems kept out of the paste library only), (2) no unlabelled-train
list at labeled_fraction >= 1 (pool backgrounds only), (3) summary keys n_library_cells / n_library_excluded;
adds tests to tests/test_f2_cp.py."""
from pathlib import Path

p = Path("src/data/copy_paste.py"); s = p.read_text()
old1 = '''    lab = read_list(Path(info["labeled_split"]))
    library, records = build_library(img_dir, msk_dir, lab, int(c.get("min_area", 20)), float(c.get("min_contrast", 3.0)))
'''
new1 = '''    lab = read_list(Path(info["labeled_split"]))
    # F3 (100% labels): optional ``cp.library_exclude`` (a stem list kept out of the paste library only; those cells stay
    # in the labelled stream). Absent = no change.
    lib_excl = set(read_list(Path(c["library_exclude"]))) if c.get("library_exclude") else set()
    lib_stems = [s for s in lab if s not in lib_excl]
    library, records = build_library(img_dir, msk_dir, lib_stems, int(c.get("min_area", 20)),
                                     float(c.get("min_contrast", 3.0)))
'''
old2 = '''    frac_tag = f"{round(float(d['labeled_fraction']) * 100)}pct"
    unl = read_list(root / "splits" / f"seed{int(info['split_seed'])}" / f"unlabeled_{frac_tag}.txt")
'''
new2 = '''    if float(d["labeled_fraction"]) >= 1:  # F3: at 100% every train cell is labelled: no (b) list, pool backgrounds only
        unl = []
    else:
        frac_tag = f"{round(float(d['labeled_fraction']) * 100)}pct"
        unl = read_list(root / "splits" / f"seed{int(info['split_seed'])}" / f"unlabeled_{frac_tag}.txt")
'''
old3 = '''    summary = dict(n_library=len(library), library_px=int(sum(x["area"] for x in library)), n_bg_pool=len(bg_a),
                   n_bg_train=len(bg_b), n_heldout=len(held), n_candidates=len(records))
'''
new3 = '''    summary = dict(n_library=len(library), library_px=int(sum(x["area"] for x in library)), n_bg_pool=len(bg_a),
                   n_bg_train=len(bg_b), n_heldout=len(held), n_candidates=len(records), n_library_cells=len(lib_stems),
                   n_library_excluded=len(set(lab) & lib_excl))
'''
for o, n in ((old1, new1), (old2, new2), (old3, new3)):
    assert s.count(o) == 1, o[:70]
    s = s.replace(o, n)
p.write_text(s)

t = Path("tests/test_f2_cp.py"); ts = t.read_text()
assert "test_build_cp_stream_100pct" not in ts
ts += '''

def _stream_root(tmp, frac_unl=True):
    """tiny data root: 2 labelled cells (A has a crack line, T is a 'twin'), 3 pool cells, 1 held-out pool cell"""
    root = tmp / "data"
    (root / "labeled" / "images").mkdir(parents=True); (root / "labeled" / "masks_escdd").mkdir(parents=True)
    (root / "unlabeled" / "images_512").mkdir(parents=True); (root / "splits" / "seed0").mkdir(parents=True)
    for stem, row in (("A", 40), ("T", 80)):
        img = _textured(1, 256, 256); msk = np.zeros((256, 256), np.uint8)
        img[row, 60:140] = 100; msk[row, 60:140] = 14
        Image.fromarray(img).save(root / "labeled" / "images" / f"{stem}.png")
        Image.fromarray(msk).save(root / "labeled" / "masks_escdd" / f"{stem}.png")
    pool = []
    for i in range(4):
        r = f"unlabeled/images_512/P{i}.png"; Image.fromarray(_textured(10 + i, 256, 256)).save(root / r); pool.append(r)
    (tmp / "pool.txt").write_text("\\n".join(pool) + "\\n"); (tmp / "held.txt").write_text(pool[3] + "\\n")
    (tmp / "lab.txt").write_text("A\\nT\\n"); (tmp / "twins.txt").write_text("T\\n")
    if frac_unl:
        (root / "splits" / "seed0" / "unlabeled_50pct.txt").write_text("U\\n")
    return root


def _stream_cfg(root, tmp, frac, excl=None):
    cp = {"lambda": 1.0, "batch": 2, "bg_pool_list": str(tmp / "pool.txt"), "heldout_list": str(tmp / "held.txt")}
    if excl:
        cp["library_exclude"] = str(excl)
    return {"cp": cp, "data": {"root": str(root), "mask_subdir": "labeled/masks_escdd", "labeled_fraction": frac,
                               "input_size": 256}}


def test_build_cp_stream_100pct_needs_no_unlabelled_list(tmp_path):
    from src.data.copy_paste import build_cp_stream
    root = _stream_root(tmp_path, frac_unl=False)   # no splits/seed0/unlabeled_100pct.txt exists
    info = {"labeled_split": str(tmp_path / "lab.txt"), "split_seed": 0}
    _, _, sm = build_cp_stream(_stream_cfg(root, tmp_path, 1.0), info, 0, 0, False)
    assert sm["n_bg_train"] == 0 and sm["n_bg_pool"] == 3 and sm["n_heldout"] == 1
    assert sm["n_library_cells"] == 2 and sm["n_library_excluded"] == 0 and sm["n_library"] == 2


def test_build_cp_stream_library_exclude(tmp_path):
    from src.data.copy_paste import build_cp_stream
    root = _stream_root(tmp_path, frac_unl=False)
    info = {"labeled_split": str(tmp_path / "lab.txt"), "split_seed": 0}
    _, rec, sm = build_cp_stream(_stream_cfg(root, tmp_path, 1.0, tmp_path / "twins.txt"), info, 0, 0, False)
    assert sm["n_library_cells"] == 1 and sm["n_library_excluded"] == 1 and sm["n_library"] == 1
    assert all(r.get("stem", "A") != "T" for r in rec)


def test_build_cp_stream_below_100pct_still_reads_unlabelled_list(tmp_path):
    from src.data.copy_paste import build_cp_stream
    root = _stream_root(tmp_path, frac_unl=False)
    info = {"labeled_split": str(tmp_path / "lab.txt"), "split_seed": 0}
    with pytest.raises(FileNotFoundError):
        build_cp_stream(_stream_cfg(root, tmp_path, 0.5), info, 0, 0, False)
'''
t.write_text(ts)
print("patched src/data/copy_paste.py and tests/test_f2_cp.py")
