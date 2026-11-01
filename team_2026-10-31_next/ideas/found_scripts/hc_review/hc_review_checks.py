"""found (independent review of builder's HC code, el_hc c2e6973; protocol_HC §9 gate 1), 1 Nov 2026. CPU only.
Checks (coach's list):
  (2) eligibility rule_p on the 478 house train masks: builder's find_source vs an independent re-implementation from
      domain's reference gap code (dom_synth_val.py 6e702c36, gap_rows copied verbatim) + band padding fraction; counts,
      per-source split, the 0.4 cut's empty gap; eligibility draws no RNG (own generator, numpy global, torch global);
  (3) per-sample seeding: SeedSequence.generate_state prefix consistency; dataset with synth p = 0 == without synth for
      many (idx, seed) keys after the house labelsafe transform; with p = 0.35 every not-made sample == house sample;
      BatchStream resume (iterate(k)) == uninterrupted (iterate(0) then skip k), num_workers 0;
  (4) label mapping of the inserted band: made-mask labels subset of the source's, <= 23, no padding added; band spacing
      classes 1 / 2 by source; band composition;
  (5) pixel equivalence with domain's SHV1 on the SHV1-p list (80 names, md5 7f651fc7), plus regeneration of SHV1 cells
      with domain's own code path (copied) to confirm the stored files are the reference output.
Usage (from anywhere): CUDA_VISIBLE_DEVICES="" python hc_review_checks.py --code /home/noob/work/el_hc --out OUT.json
"""
import argparse
import csv
import hashlib
import json
import os
import sys
from pathlib import Path

import numpy as np

assert os.environ.get("CUDA_VISIBLE_DEVICES") == "", "CPU only"
ap = argparse.ArgumentParser()
ap.add_argument("--code", default="/home/noob/work/el_hc")
ap.add_argument("--shv1", default="/home/noob/work/domain_scratch/shv1")
ap.add_argument("--shv1p", default="/home/noob/work/domain_scratch/out/shv1p_stems_eval.txt")
ap.add_argument("--out", required=True)
ap.add_argument("--threads", type=int, default=4)
a = ap.parse_args()
import torch  # noqa: E402
torch.set_num_threads(a.threads)
ROOT = Path(a.code); sys.path.insert(0, str(ROOT))
from PIL import Image  # noqa: E402
from scipy import ndimage as ndi  # noqa: E402
from src.data.augmentations import get_labelsafe_augmentation  # noqa: E402
from src.data.benchmark_el import BenchmarkELDataset, load_index_mask  # noqa: E402
from src.data.stream import BatchStream, SeededDataset  # noqa: E402
from src.data.synth_halfcut import MADE, NOT_DRAWN, NOT_SOURCE, SynthHalfCut, find_source, gap_geometry, synthesize, load_pool  # noqa: E402

D = ROOT / "data"; IMG, MSK = D / "labeled" / "images", D / "labeled" / "masks_escdd"
POOL = D / "splits" / "synth_halfcut_pool_ap.tsv"
train = [l.strip() for l in open(D / "splits" / "train.txt") if l.strip()]
assert len(train) == 478
R = {"code_head": os.popen(f"git -C {ROOT} rev-parse HEAD").read().strip(), "pool_md5": hashlib.md5(POOL.read_bytes()).hexdigest()}


# ---------------------------------------------------------------- (2) independent rule_p from domain's reference code
def dom_gap_rows(I, valid):  # verbatim from dom_synth_val.py (6e702c36)
    rp = np.array([I[y][valid[y]].mean() if valid[y].sum() > 50 else np.nan for y in range(I.shape[0])])
    rp = np.nan_to_num(rp, nan=np.nanmedian(rp)); rs = ndi.uniform_filter1d(rp, 3); out = []
    for c in (128, 384):
        lo, hi = c - 45, c + 45; y = lo + int(np.argmin(rs[lo:hi])); pl = np.median(rs[max(0, y - 60):y + 60])
        half = rs[y] + 0.5 * (pl - rs[y]); aa = y; bb = y
        while aa > 0 and rs[aa] < half: aa -= 1
        while bb < len(rs) - 1 and rs[bb] < half: bb += 1
        out.append((y, aa, bb, 1 - rs[y] / max(pl, 1)))
    return out


def dom_rule_p(I, M):
    if I.shape != (512, 512):
        return False, None
    wr = np.mean(I >= 250, axis=1) > 0.98; wc = np.mean(I >= 250, axis=0) > 0.98; valid = (~wr[:, None]) & (~wc[None, :])
    (yt, at, bt, dt), (yb, ab, bb_, db) = dom_gap_rows(I, valid)
    found = dt > 0.08 and db > 0.08 and 200 < yb - yt < 310
    g = bt + 1 - at; band = M[at:bt + 1]; pf = float((band == 7).mean())
    return bool(found and g <= 20 and pf < 0.4), {"found": bool(found), "g": int(g), "pad_frac": pf}


ds_raw = BenchmarkELDataset(IMG, MSK, train, transform=None, return_raw=True)  # raw image (H,W,1) uint8 + mask, exactly what apply_pair receives
elig_b, elig_d, info = {}, {}, {}
synth_chk = SynthHalfCut(0.35, POOL)
rng_violations, glob_ok = 0, True
np_state0 = np.random.get_state()[1].copy(); t_state0 = torch.get_rng_state().clone()
for i, s in enumerate(train):
    smp = ds_raw[i]
    img, M = smp["image"], smp["mask"]
    img = img.numpy() if hasattr(img, "numpy") else np.asarray(img)
    M = M.numpy() if hasattr(M, "numpy") else np.asarray(M)
    if img.ndim == 3 and img.shape[0] == 1:
        img = np.transpose(img, (1, 2, 0))
    if img.ndim == 2:
        img = img[:, :, None]
    I = img[:, :, 0].astype(np.float64)
    elig_b[s] = find_source(I, M) is not None
    elig_d[s], info[s] = dom_rule_p(I, M)
    synth_chk.random_generator = np.random.default_rng(1000 + i)
    st0 = json.dumps(synth_chk.random_generator.bit_generator.state, default=str)
    _, _, code = synth_chk.apply_pair(img, M)
    st1 = json.dumps(synth_chk.random_generator.bit_generator.state, default=str)
    if code == NOT_SOURCE and st0 != st1:
        rng_violations += 1
glob_ok = bool(np.array_equal(np.random.get_state()[1], np_state0) and torch.equal(torch.get_rng_state(), t_state0))
src = lambda s: s.split("_")[0]
nb = sum(elig_b.values())
excl = [s for s in train if info[s] and info[s]["found"] and info[s]["g"] <= 20 and info[s]["pad_frac"] >= 0.4]
kept = [s for s in train if elig_d[s]]
R["eligibility"] = {
    "builder_find_source": nb, "domain_reimpl": sum(elig_d.values()),
    "per_cell_disagreements": [s for s in train if elig_b[s] != elig_d[s]],
    "by_source": {k: sum(1 for s in train if elig_b[s] and src(s) == k) for k in ("ARTS", "CFVS", "CSIR", "BMRK", "SDLE")},
    "found": sum(1 for s in train if info[s] and info[s]["found"]),
    "found_and_g_le_20": sum(1 for s in train if info[s] and info[s]["found"] and info[s]["g"] <= 20),
    "excluded_by_padding": len(excl), "excluded_by_source": {k: sum(1 for s in excl if src(s) == k) for k in ("BMRK", "SDLE", "ARTS", "CFVS", "CSIR")},
    "kept_pad_frac_max": round(max(info[s]["pad_frac"] for s in kept), 4), "excluded_pad_frac_min": round(min(info[s]["pad_frac"] for s in excl), 4) if excl else None,
    "ineligible_samples_that_changed_own_rng": rng_violations, "global_numpy_torch_rng_untouched": glob_ok}
print("eligibility", json.dumps(R["eligibility"]), flush=True)

# ---------------------------------------------------------------- (3) seeding
pref = all(np.array_equal(np.random.SeedSequence(sd).generate_state(n + 1)[:n], np.random.SeedSequence(sd).generate_state(n))
           for sd in range(200) for n in range(1, 12))
aug = get_labelsafe_augmentation(512)
house = BenchmarkELDataset(IMG, MSK, train, aug)
withp0 = BenchmarkELDataset(IMG, MSK, train, get_labelsafe_augmentation(512), synth=SynthHalfCut(0.0, POOL))
withp35 = BenchmarkELDataset(IMG, MSK, train, get_labelsafe_augmentation(512), synth=SynthHalfCut(0.35, POOL))
SH, S0, S35 = SeededDataset(house), SeededDataset(withp0), SeededDataset(withp35)
rng = np.random.default_rng(7); keys = [(int(rng.integers(478)), int(rng.integers(2 ** 62))) for _ in range(120)]
eq0 = eq35_notmade = n35_notmade = n35_made = 0
for k in keys:
    h, z, t = SH[k], S0[k], S35[k]
    same = lambda x, y: torch.equal(torch.as_tensor(x["image"]), torch.as_tensor(y["image"])) and torch.equal(torch.as_tensor(x["mask"]), torch.as_tensor(y["mask"]))
    eq0 += int(same(h, z) and int(z["synth"]) != MADE)
    if int(t["synth"]) == MADE:
        n35_made += 1
    else:
        n35_notmade += 1; eq35_notmade += int(same(h, t))
bs = BatchStream(withp35, 8, seed=5, stream_id=0, num_workers=0, pin_memory=False)
it0 = bs.iterate(0); full = [next(it0) for _ in range(6)]
it3 = bs.iterate(3); res3 = [next(it3) for _ in range(3)]
resume_ok = all(torch.equal(full[3 + j]["image"], res3[j]["image"]) and torch.equal(full[3 + j]["mask"], res3[j]["mask"])
                and torch.equal(full[3 + j]["synth"], res3[j]["synth"]) for j in range(3))
R["seeding"] = {"seedsequence_prefix_consistent": bool(pref), "p0_equals_house": f"{eq0}/{len(keys)}",
                "p035_not_made_equals_house": f"{eq35_notmade}/{n35_notmade}", "p035_made": n35_made,
                "resume_iterate3_equals_uninterrupted": bool(resume_ok),
                "synth_codes_in_6_batches": [int(c) for b in full for c in b["synth"].tolist()]}
print("seeding", json.dumps({k: v for k, v in R["seeding"].items() if k != "synth_codes_in_6_batches"}), flush=True)

# ---------------------------------------------------------------- (4) label mapping of the inserted band
pool, _ = load_pool(POOL)
comp, mixed, sub_ok, max_lab, padded_n, n_made = {}, 0, 0, 0, 0, 0
sp_by_type = {"band_has_1_only": 0, "band_has_2_only": 0, "band_has_both": 0, "band_has_neither": 0}
for i, s in enumerate(train):
    if not elig_b[s]:
        continue
    smp = ds_raw[i]; img = np.asarray(smp["image"]); M = np.asarray(smp["mask"])
    if img.ndim == 3 and img.shape[0] == 1:
        img = np.transpose(img, (1, 2, 0))
    I = img[:, :, 0].astype(np.float64) if img.ndim == 3 else img.astype(np.float64)
    geo = find_source(I, M); band = M[geo["at"]:geo["bt"] + 1]
    for c, n in zip(*np.unique(band, return_counts=True)):
        comp[int(c)] = comp.get(int(c), 0) + int(n)
    h1, h2 = (band == 1).any(), (band == 2).any()
    sp_by_type["band_has_both" if h1 and h2 else "band_has_1_only" if h1 else "band_has_2_only" if h2 else "band_has_neither"] += 1
    for half in (0, 1):
        O, OM, padded = synthesize(I, M, geo, 1.0, 1.0, half, tuple(pool[(i * 2 + half) % len(pool)]))
        n_made += 1; padded_n += int(padded)
        sub_ok += int(set(np.unique(OM)) <= set(np.unique(M)))
        max_lab = max(max_lab, int(OM.max()))
tot = sum(comp.values())
R["label_mapping"] = {"made_samples": n_made, "made_mask_labels_subset_of_source": f"{sub_ok}/{n_made}", "max_label": max_lab,
                      "padded_outputs": padded_n, "band_composition_share": {k: round(v / tot, 4) for k, v in sorted(comp.items())},
                      "band_spacing_classes_per_source": sp_by_type}
print("labels", json.dumps(R["label_mapping"]), flush=True)

# ---------------------------------------------------------------- (5) SHV1-p pixel equivalence + regeneration check
shv1p = [l.strip() for l in open(a.shv1p) if l.strip()]
rows = {r["name"]: r for r in csv.DictReader(open(Path(a.shv1) / "shv1_context.tsv"), delimiter="\t")}
eq_img = eq_msk = 0; bad = []
for name in shv1p:
    r = rows[name]; st = r["src_stem"]
    I = np.asarray(Image.open(IMG / f"{st}.png").convert("L"), dtype=np.float64); M = load_index_mask(MSK / f"{st}.png")
    geo = find_source(I, M)
    if geo is None:
        bad.append((name, "not eligible")); continue
    O, OM, padded = synthesize(I, M, geo, 1.0, 1.0, int(r["half"]), tuple(pool[int(r["pool_idx"])]))
    ref = np.asarray(Image.open(Path(a.shv1) / "images" / f"{name}.png")); refm = np.asarray(Image.open(Path(a.shv1) / "masks" / f"{name}.png"))
    a1 = np.array_equal(np.clip(np.rint(O), 0, 255).astype(np.uint8), ref); a2 = np.array_equal(OM.astype(np.uint8), refm)
    eq_img += int(a1); eq_msk += int(a2)
    if not (a1 and a2):
        bad.append((name, "differs", int(np.abs(np.clip(np.rint(O), 0, 255).astype(int) - ref.astype(int)).max())))
# regenerate 4 SHV1 images with domain's own code path (dom_rule geometry + domain's crop formula) and compare to the files
regen = 0
for name in shv1p[:4]:
    r = rows[name]; st = r["src_stem"]; half = int(r["half"])
    I = np.asarray(Image.open(IMG / f"{st}.png").convert("L"), dtype=np.float64); M = np.asarray(Image.open(MSK / f"{st}.png")).astype(np.uint8)
    wr = np.mean(I >= 250, axis=1) > 0.98; wc = np.mean(I >= 250, axis=0) > 0.98; valid = (~wr[:, None]) & (~wc[None, :])
    (yt, at, bt, dt), (yb, ab, bb_, db) = dom_gap_rows(I, valid)
    ymid = int(round((yt + yb) / 2)); g = bt + 1 - at
    I2 = np.concatenate([I[:ymid], I[at:bt + 1], I[ymid:]], 0); M2 = np.concatenate([M[:ymid], M[at:bt + 1], M[ymid:]], 0)
    V2 = np.concatenate([valid[:ymid], valid[at:bt + 1], valid[ymid:]], 0) & (M2 != 7)
    sx, sy = 342 / 256, 163 / (128 + g)
    I3 = ndi.zoom(I2, (sy, sx), order=1); M3 = ndi.zoom(M2, (sy, sx), order=0); V3 = ndi.zoom(V2.astype(np.uint8), (sy, sx), order=0).astype(bool)
    cy = ((yt + ymid) / 2 if half == 0 else (ymid + g + yb + g) / 2) * sy; cx = 256 * sx
    y0 = int(np.clip(round(cy - 256), 0, I3.shape[0] - 512)); x0 = int(np.clip(round(cx - 256), 0, I3.shape[1] - 512))
    O = I3[y0:y0 + 512, x0:x0 + 512].copy(); OM = M3[y0:y0 + 512, x0:x0 + 512]; OV = V3[y0:y0 + 512, x0:x0 + 512]
    mt, sdt = pool[int(r["pool_idx"])]; v = O[OV]; O[OV] = (v - v.mean()) / max(v.std(), 1e-3) * sdt + mt
    ref = np.asarray(Image.open(Path(a.shv1) / "images" / f"{name}.png"))
    regen += int(np.array_equal(np.clip(np.round(O), 0, 255).astype(np.uint8), ref))
R["shv1"] = {"shv1p_list_md5": hashlib.md5(Path(a.shv1p).read_bytes()).hexdigest(), "n": len(shv1p),
             "image_equal": eq_img, "mask_equal": eq_msk, "problems": bad[:10], "domain_code_regenerates_files": f"{regen}/4"}
print("shv1", json.dumps(R["shv1"]), flush=True)
json.dump(R, open(a.out, "w"), indent=1, default=str)
print("DONE")
