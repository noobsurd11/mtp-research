"""Profile sampled HF images and check exact / near-duplicate overlap against our local reference images.

Images are decoded with PIL only (untrusted data). Conversion = our pool pipeline: PIL convert("L"); if not 512 px,
area-downsample to 512 x 512 (PIL BOX, the area filter; gaint used cv2 INTER_AREA, not bit-identical).
Near-duplicate descriptor (r_hp, Track M variant, trackM/data_addendum.md): 512 -> 128 px by 4x4 mean, minus
Gaussian(sigma 3), z-scored; r = mean product (Pearson). Exact: md5 of the converted 512 L pixels, and md5 of the
decoded native pixels.
References (local): 582 labelled (BenchmarkEL 20211104), ext117 incl. E1 106 (BenchmarkEL 20221008), 117 E-SCDD _rf.
Usage: python -I profile_overlap.py <out_dir> <sample_dir> <sample_log.jsonl>
Writes sample_profile.tsv, sample_matches.tsv, calib_rhp.json, ref_stats.tsv.
"""
import csv
import hashlib
import io
import json
import struct
import sys
import time
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

out, sdir, slog = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
B11 = Path("/home/yugma/mtp/datasets/BenchmarkELimages/dataset_20211104")
B22 = Path("/home/yugma/mtp/datasets/BenchmarkEL_releases/dataset_20221008")
ESC = Path("/home/yugma/mtp/datasets/escdd_full")
refs = json.load(open(out / "refs.json"))


def to512(im):
    g = im.convert("L")
    if g.size != (512, 512):
        g = g.resize((512, 512), Image.BOX)
    return np.asarray(g, dtype=np.uint8)


def hp(a):
    d = a.astype(np.float64).reshape(128, 4, 128, 4).mean(axis=(1, 3))
    h = d - ndimage.gaussian_filter(d, 3)
    return ((h - h.mean()) / (h.std() + 1e-8)).astype(np.float32).ravel()


def stats(a):
    f = a.astype(np.float64)
    lap = np.abs(ndimage.laplace(f)).mean()
    b = np.concatenate([a[:8].ravel(), a[-8:].ravel(), a[:, :8].ravel(), a[:, -8:].ravel()])
    return dict(mean=f.mean(), sd=f.std(), p1=np.percentile(a, 1), p99=np.percentile(a, 99), share0=(a == 0).mean(),
                share255=(a == 255).mean(), lap=lap, border_mean=float(b.mean()), border_dark=float((b < 16).mean()),
                dark_frac=float((a < 16).mean()))


def ref_paths():
    sp = {"train": "images_train_original", "val": "images_val", "test": "images_test"}
    for k in ("train", "val", "test"):
        for s in refs[k]:
            yield k, s, B11 / sp[k] / f"{s}.png"
    e1 = set(refs["e1"])
    for s in refs["ext117"]:
        p = next((B22 / d / f"{s}.png" for d in ("el_images_train", "el_images_val", "el_images_test")
                  if (B22 / d / f"{s}.png").exists()), None)
        yield ("e1" if s in e1 else "ext117_inpool"), s, p
    rf17 = set(refs["rf17"])
    for s in refs["rf117"]:
        p = next((ESC / d / f"{s}_rf.png" for d in ("el_images_train", "el_images_val", "el_images_test")
                  if (ESC / d / f"{s}_rf.png").exists()), None)
        yield ("rf17" if s in rf17 else "rf_inpool"), s, p


R = [(k, s, p) for k, s, p in ref_paths()]
assert all(p is not None and p.exists() for _, _, p in R), [x for x in R if x[2] is None or not x[2].exists()][:5]
ref_arr, ref_md5, ref_hp, ref_rows = [], [], [], []
with open(out / "ref_stats.tsv", "w") as f:
    f.write("set\tstem\tsource\tw\th\tmode\t" + "\t".join(stats(np.zeros((512, 512), np.uint8)).keys()) + "\n")
    for k, s, p in R:
        im = Image.open(p)
        a = to512(im)
        ref_md5.append(hashlib.md5(a.tobytes()).hexdigest())
        ref_hp.append(hp(a))
        ref_rows.append((k, s))
        st = stats(a)
        f.write(f"{k}\t{s}\t{s.split('_')[0]}\t{im.size[0]}\t{im.size[1]}\t{im.mode}\t" +
                "\t".join(f"{v:.4f}" for v in st.values()) + "\n")
H = np.stack(ref_hp)
nref = len(R)

# calibration on our own data: the 7 D7 test-train twin pairs, and best non-twin same-source matches
idx = {(k, s): i for i, (k, s) in enumerate(ref_rows)}
twins = [("CFVS_00006_r5_c5", "CFVS_00003_r5_c5"), ("CFVS_00033_r8_c4", "CFVS_00037_r8_c4"),
         ("CFVS_00035_r8_c4", "CFVS_00037_r8_c4"), ("CFVS_00042_r8_c4", "CFVS_00037_r8_c4"),
         ("CFVS_00018_r4_c4", "CFVS_00020_r4_c4"), ("CFVS_00027_r4_c4", "CFVS_00031_r4_c4"),
         ("ARTS_00020_r5_c1", "ARTS_00081_r5_c1")]
cal = {"twin_pairs": {f"{a}~{b}": float(H[idx[("test", a)]] @ H[idx[("train", b)]] / H.shape[1]) for a, b in twins}}
tr = [i for i, (k, s) in enumerate(ref_rows) if k == "train"]
twin_tr = {b for _, b in twins} | {"CFVS_00032_r8_c4", "CFVS_00022_r4_c4"}
nontwin_best = {}
for i, (k, s) in enumerate(ref_rows):
    if k != "test" or s in {a for a, _ in twins}:
        continue
    cand = [j for j in tr if ref_rows[j][1].split("_")[0] == s.split("_")[0] and ref_rows[j][1] not in twin_tr]
    if cand:
        r = H[cand] @ H[i] / H.shape[1]
        nontwin_best[s] = float(r.max())
by_src = {}
for s, v in nontwin_best.items():
    by_src.setdefault(s.split("_")[0], []).append(v)
cal["nontwin_test_best_by_source"] = {k: dict(n=len(v), median=float(np.median(v)), max=float(np.max(v)))
                                      for k, v in by_src.items()}
# rf_inpool vs ext117 in-pool and labelled: identity sanity
json.dump(cal, open(out / "calib_rhp.json", "w"), indent=1)
print("calibration:", json.dumps(cal, indent=1))

# sample
if not slog.exists():
    sys.exit(0)
man = {int(r["global_row"]): r for r in csv.DictReader(open(out / "manifest.tsv"), delimiter="\t")}
log = [json.loads(x) for x in open(slog) if x.strip()]
ok = [r for r in log if r.get("ok")]
prof_f = open(out / "sample_profile.tsv", "w")
match_f = open(out / "sample_matches.tsv", "w")
SETS = ["train", "val", "test", "e1", "rf17", "ext117_inpool", "rf_inpool"]
set_idx = {k: np.array([i for i, (kk, _) in enumerate(ref_rows) if kk == k]) for k in SETS}
match_f.write("global_row\tstem\tlabel\tbest_set\tbest_stem\tr_hp\tsame_id\texact_512\ttop2_set\ttop2_stem\ttop2_r\t" +
              "\t".join(f"{k}_best_r\t{k}_best_stem" for k in SETS) + "\n")
hdr = None
S_hp, S_rows = [], []
for r in sorted(ok, key=lambda x: x["global_row"]):
    g = r["global_row"]
    p = sdir / f"r{g}.png"
    raw = p.read_bytes()
    m = man[g]
    stem = Path(m["file_path"]).stem
    ihdr = dict(w=struct.unpack(">I", raw[16:20])[0], h=struct.unpack(">I", raw[20:24])[0], bit_depth=raw[24],
                colour_type=raw[25], interlace=raw[28])
    rec = dict(global_row=g, stem=stem, label=m["label"], shard=m["shard"], png_bytes=len(raw),
               md5_png=hashlib.md5(raw).hexdigest(), **ihdr)
    try:
        im = Image.open(p)
        im.load()
        nat = np.asarray(im)
        rec["mode"] = im.mode
        rec["md5_pixels"] = hashlib.md5(nat.tobytes() + str(nat.shape).encode()).hexdigest()
        if nat.ndim == 3 and nat.shape[2] >= 3:
            d = np.abs(nat[..., 0].astype(int) - nat[..., 1]) + np.abs(nat[..., 1].astype(int) - nat[..., 2])
            rec["chan_maxdiff"] = int(d.max())
            rec["chan_diff_gt16"] = float((d > 16).mean())
        t_dec = time.time()
        a = to512(Image.open(p))
        h = hp(a)
        rec["secs_decode_conv_hp"] = round(time.time() - t_dec, 4)
        bio = io.BytesIO()
        Image.fromarray(a).save(bio, format="PNG")
        rec["png512L_bytes"] = bio.tell()
        rec["md5_512L"] = hashlib.md5(a.tobytes()).hexdigest()
        rec.update({k: round(float(v), 4) for k, v in stats(a).items()})
        rec["decode_ok"] = 1
        S_hp.append(h)
        S_rows.append(rec)
        rr = H @ h / H.shape[1]
        o = np.argsort(-rr)
        b0, b1 = o[0], o[1]
        same = [i for i, (k, s) in enumerate(ref_rows) if s == stem]
        ex = [f"{ref_rows[i][0]}:{ref_rows[i][1]}" for i in range(nref) if ref_md5[i] == rec["md5_512L"]]
        rec["best_r"] = round(float(rr[b0]), 4)
        rec["best_set"], rec["best_stem"] = ref_rows[b0]
        rec["same_id_r"] = round(float(max(rr[i] for i in same)), 4) if same else ""
        match_f.write(f"{g}\t{stem}\t{m['label']}\t{ref_rows[b0][0]}\t{ref_rows[b0][1]}\t{rr[b0]:.4f}\t"
                      f"{';'.join(ref_rows[i][0] + ':' + f'{rr[i]:.4f}' for i in same)}\t{';'.join(ex)}\t"
                      f"{ref_rows[b1][0]}\t{ref_rows[b1][1]}\t{rr[b1]:.4f}\t" +
                      "\t".join(f"{rr[set_idx[k]].max():.4f}\t{ref_rows[set_idx[k][rr[set_idx[k]].argmax()]][1]}"
                                for k in SETS) + "\n")
    except Exception as e:  # broken image
        rec["decode_ok"] = 0
        rec["err"] = f"{type(e).__name__}: {e}"
    if hdr is None:
        hdr = list(rec.keys()) + [k for k in ("mode", "md5_pixels", "chan_maxdiff", "chan_diff_gt16", "md5_512L", "mean",
                                               "sd", "p1", "p99", "share0", "share255", "lap", "border_mean",
                                               "border_dark", "dark_frac", "decode_ok", "err", "best_r", "best_set",
                                               "secs_decode_conv_hp", "png512L_bytes",
                                               "best_stem", "same_id_r") if k not in rec]
        prof_f.write("\t".join(hdr) + "\n")
    prof_f.write("\t".join(str(rec.get(k, "")) for k in hdr) + "\n")
prof_f.close()
match_f.close()
if S_hp:
    SH = np.stack(S_hp)
    np.save(out / "sample_hp.npy", SH)
    # within-sample near-duplicates
    rr = SH @ SH.T / SH.shape[1]
    np.fill_diagonal(rr, -1)
    pairs = [(S_rows[i]["stem"], S_rows[j]["stem"], float(rr[i, j])) for i in range(len(S_rows))
             for j in range(i + 1, len(S_rows)) if rr[i, j] >= 0.9]
    json.dump(dict(n=len(S_rows), within_sample_pairs_ge_0_9=pairs,
                   md5_512L_dups=len(S_rows) - len({r["md5_512L"] for r in S_rows})),
              open(out / "sample_within.json", "w"), indent=1)
print("profiled", len(ok), "of", len(log))
