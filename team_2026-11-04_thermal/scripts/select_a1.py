"""A1 selection per datasets/download_plan.md (md5 409481f7 + disclosure edit logged).
Reads listings + downloaded dark I-V txt files (as data). Writes datasets/download_selection_A1.tsv and names files."""
import csv, re, sys, os
import numpy as np
L = "scripts/listings/"
DARK = os.path.expanduser("~/mtp/datasets/thermal_public/A1_osf_csr6t/darkIV/")
rd = lambda f: [r for r in csv.DictReader(open(L + f), delimiter="\t") if r["kind"] == "file"]
ir, el, uvf, dk = rd("A1_IR.tsv"), rd("A1_EL.tsv"), rd("A1_UVF.tsv"), rd("A1_darkIV.tsv")
irraw, irjpg, irtxt = {}, {}, {}
for r in ir:
    n = r["name"]
    m = re.match(r"^(\d{8}_\d{6})_SHELL_M55_(\d{9,10})_180s_(3\.39[23])A\.txt$", n)
    if m: irraw.setdefault(m.group(2), []).append((m.group(1), n)); continue
    m = re.match(r"^(\d{9,10})_cropped\.(jpg|txt)$", n)
    if m: (irjpg if m.group(2) == "jpg" else irtxt)[m.group(1)] = n
elnef = {}
for r in el:
    m = re.match(r"^(\d{8}_\d{6})_SHELL_M55_(\d{9,10})_[\d.]+s_(3\.39[23])\d*A_.*\.NEF$", r["name"])
    if m: elnef.setdefault(m.group(2), []).append((m.group(1), r["name"]))
uv = {}
for r in uvf:
    m = re.match(r"^(\d{8}_\d{6})_SHELL_M55_(\d{9,10})\.jpg$", r["name"])
    if m: uv.setdefault(m.group(2), []).append((m.group(1), r["name"]))
dark = {}
for r in dk:
    m = re.match(r"^(\d{9,10})_EL-derived_cell-dark-I-V\.txt$", r["name"])
    if m: dark[m.group(1)] = r["name"]
elig = sorted(set(dark) & set(irraw) & set(irjpg) & set(irtxt) & set(uv) & set(elnef))
print("counts: dark", len(dark), "irraw", len(irraw), "irjpg", len(irjpg), "irtxt", len(irtxt), "uvf", len(uv), "elnef@3.39", len(elnef), "eligible", len(elig))
# severity
sev = {}
for s in elig:
    lines = open(DARK + dark[s], encoding="utf-8", errors="strict").read().splitlines()
    hdr = lines[0].split("\t")
    assert len(hdr) == 72 and hdr[0].startswith("voltage_(V)_Cell1") and hdr[1].startswith("current_(A)_Cell1"), (s, hdr[:2], len(hdr))
    arr = np.array([[float(x) for x in l.split("\t")] for l in lines[1:] if l.strip()])
    assert arr.shape[1] == 72, (s, arr.shape)
    V, I = arr[:, 0::2], arr[:, 1::2]
    k = int(np.argmax(I[:, 0]))
    assert np.allclose(I[k], I[k, 0]), s
    v = V[k]
    sev[s] = (float(np.median(v) - v.min()) * 1000.0, float(I[k, 0]), int(np.argmin(v)) + 1, arr.shape[0])
order = sorted(elig, key=lambda s: (sev[s][0], s))
bins = np.array_split(np.array(order), 5)
rng = np.random.default_rng(20261104)
pick = []
for b, members in enumerate(bins, start=1):
    mem = sorted(members.tolist())
    if b == 5:
        top = max(mem, key=lambda s: (sev[s][0], s))
        rest = [s for s in mem if s != top]
        pick += [(top, b, "max")] + [(x, b, "rand") for x in rng.choice(rest, 1, replace=False).tolist()]
    else:
        pick += [(x, b, "rand") for x in rng.choice(mem, 2, replace=False).tolist()]
edges = [(float(sev[m[0]][0]), float(sev[m[-1]][0])) for m in bins]
with open("datasets/download_selection_A1.tsv", "w") as f:
    f.write("# A1 selection, rule datasets/download_plan.md; rng default_rng(20261104); eligible %d; bin s-ranges mV %s\n" % (len(elig), "; ".join("%d:%.1f-%.1f" % (i + 1, a, b) for i, (a, b) in enumerate(edges))))
    f.write("serial\tbin\thow\ts_mV\tI_A\tworst_cell\tn_rows\tEL\tIR_raw\tIR_jpg\tIR_txt\tUVF\tdarkIV\n")
    names = []
    for s, b, how in pick:
        e = sorted(elnef[s])[0][1]; ir_r = sorted(irraw[s])[0][1]; u = sorted(uv[s])[0][1]
        f.write("\t".join(map(str, [s, b, how, "%.2f" % sev[s][0], sev[s][1], sev[s][2], sev[s][3], e, ir_r, irjpg[s], irtxt[s], u, dark[s]])) + "\n")
        names.append((e, ir_r, irjpg[s], irtxt[s], u))
open(L + "A1_EL_names.txt", "w").write("\n".join(n[0] for n in names) + "\n")
open(L + "A1_IR_names.txt", "w").write("\n".join(x for n in names for x in n[1:4]) + "\n")
open(L + "A1_UVF_names.txt", "w").write("\n".join(n[4] for n in names) + "\n")
print("picked", [(s, b, how, round(sev[s][0], 1)) for s, b, how in pick])
