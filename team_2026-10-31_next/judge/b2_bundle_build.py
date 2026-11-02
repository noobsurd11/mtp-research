"""judge b2_bundle_build (2 Nov 2026): name-free, shuffled B2 marking bundles; judge holds the key.
Sets:
  calibration (72, mixed, shuffled): 40 CSIR train cells (20 with house crack px >= 100, 20 with 0; results/b6/b6_folds.tsv, whole crop,
  random.Random(20261102) on sorted stems) + 32 Hanifi _rf half-cells in the B2 pool minus b2v2_list (pool copies, images_512);
  B2 (100): b2v2_list.txt panels, shuffled.
Views per item: V1 = the 512 crop as greyscale ('L', as the house loader), pixel-identical, re-encoded (optimize=True);
  V2 = autocontrast (1% cutoff) of V1, 2x Lanczos to 1024 x 1024. No other processing.
Writes: OUT/cal/<ID>_v1.png, <ID>_v2.png; OUT/b2/<ID>_v1.png, <ID>_v2.png; OUT/MANIFEST.md5; KEY/key_cal.tsv, KEY/key_b2.tsv.
Usage: python b2_bundle_build.py SRC_DIR OUT_DIR KEY_DIR TEAM_DIR B2_LIST CAL_STEMS"""
import hashlib, random, sys
from pathlib import Path
from PIL import Image, ImageOps

SRC, OUT, KEY, TEAM, B2L, CAL = map(Path, sys.argv[1:7])
rows = [l.rstrip("\n").split("\t") for l in open(TEAM / "results/b6/b6_folds.tsv")][1:]
csir = sorted(r[0] for r in rows if r[1] == "train" and r[0].startswith("CSIR_"))
crk = sorted(r[0] for r in rows if r[1] == "train" and r[0].startswith("CSIR_") and int(r[5]) >= 100)
non = sorted(r[0] for r in rows if r[1] == "train" and r[0].startswith("CSIR_") and int(r[5]) == 0)
rng = random.Random(20261102)
pick = [(s, "csir_crack") for s in rng.sample(crk, 20)] + [(s, "csir_nocrack") for s in rng.sample(non, 20)]
han = [l.strip()[:-3] for l in open(CAL) if l.strip()]
b2 = [l.strip() for l in open(B2L) if l.strip()]
assert len(han) == 32 and len(b2) == 100 and not set(han) & set(b2)
assert not {s for s, _ in pick} & (set(han) | set(b2))
cal = pick + [(s, "hanifi") for s in han]
random.Random(20261103).shuffle(cal)
b2i = list(enumerate(b2, 1)); random.Random(20261104).shuffle(b2i)
(OUT / "cal").mkdir(parents=True, exist_ok=True); (OUT / "b2").mkdir(parents=True, exist_ok=True); KEY.mkdir(parents=True, exist_ok=True)


def render(stem, dst):
    im = Image.open(SRC / f"{stem}.png").convert("L")
    assert im.size == (512, 512), (stem, im.size)
    im.save(f"{dst}_v1.png", optimize=True)
    ImageOps.autocontrast(im, cutoff=1).resize((1024, 1024), Image.LANCZOS).save(f"{dst}_v2.png", optimize=True)


kc = ["id\tstem\tset"]
for i, (s, kind) in enumerate(cal, 1):
    render(s, OUT / "cal" / f"C{i:03d}"); kc.append(f"C{i:03d}\t{s}\t{kind}")
kb = ["id\tpanel\tstem"]
for i, (p, s) in enumerate(b2i, 1):
    render(s, OUT / "b2" / f"P{i:03d}"); kb.append(f"P{i:03d}\t{p}\t{s}")
(KEY / "key_cal.tsv").write_text("\n".join(kc) + "\n"); (KEY / "key_b2.tsv").write_text("\n".join(kb) + "\n")
man = []
for f in sorted(OUT.rglob("*.png")):
    man.append(f"{hashlib.md5(f.read_bytes()).hexdigest()}  {f.relative_to(OUT)}")
(OUT / "MANIFEST.md5").write_text("\n".join(man) + "\n")
src_md5 = {s: hashlib.md5((SRC / f"{s}.png").read_bytes()).hexdigest() for s, _ in cal + [(s, "") for s in b2]}
out_md5 = {l.split()[1]: l.split()[0] for l in man}
clash = sum(v in set(out_md5.values()) for v in src_md5.values())
print(f"cal {len(cal)} (csir crack 20, csir none 20, hanifi 32; of {len(crk)} / {len(non)} CSIR train candidates), b2 {len(b2)}; files {len(man)}; "
      f"bundle files byte-identical to a source file: {clash}")
