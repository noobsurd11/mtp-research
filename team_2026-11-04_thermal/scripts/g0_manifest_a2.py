"""Build the cellreg manifest for A2 per plan_pick1 Amendment 2: one IR capture per module (nearest in time to the EL frame)."""
import glob, os, re, datetime as dt
B = os.path.expanduser("~/mtp/datasets/thermal_public/A2_osf_ar76v/")
pat = re.compile(r"(\d{8}_\d{6})_SOLARWORLD_[^_]+_(\d{9})_")
ts = lambda s: dt.datetime.strptime(s, "%Y%m%d_%H%M%S")
el = {}
for f in glob.glob(B + "EL/*.NEF"):
    m = pat.search(os.path.basename(f)); el[m.group(2)] = (ts(m.group(1)), f)
ir = {}
for f in glob.glob(B + "IR/*.txt"):
    m = pat.search(os.path.basename(f)); ir.setdefault(m.group(2), []).append((ts(m.group(1)), f))
out = ["module\tgrid\tel\tir\tuvf"]
for s in sorted(el):
    t_el, fe = el[s]
    t_ir, fi = min(ir[s], key=lambda x: abs((x[0] - t_el).total_seconds()))
    out.append(f"A2_{s}\t6x12\t{fe}\t{fi}\t")
    if len(ir[s]) > 1: print("multi IR", s, [os.path.basename(x[1])[:15] for x in ir[s]], "->", os.path.basename(fi)[:15])
open(os.path.expanduser("~/mtp/research/team_2026-11-04_thermal/pick1/out/G0_A2_manifest.tsv"), "w").write("\n".join(out) + "\n")
print(len(out) - 1, "modules")
