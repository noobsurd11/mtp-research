"""A2 selection per download_plan.md: all indoor_IR files; per IR serial, the EL NEF with current closest to the IR current (ties: earliest timestamp)."""
import csv, re, sys
L = "scripts/listings/"
ir = [r for r in csv.DictReader(open(L + "A2_IR.tsv"), delimiter="\t") if r["kind"] == "file"]
el = [r for r in csv.DictReader(open(L + "A2_EL.tsv"), delimiter="\t") if r["kind"] == "file"]
pat = re.compile(r"^(\d{8}_\d{6})_SOLARWORLD_[^_]+_(\d{9})_X_[\d.]+s_([\d.]+)A")
irmods = {}
for r in ir:
    m = pat.match(r["name"]); assert m, r["name"]
    irmods.setdefault(m.group(2), set()).add(float(m.group(3)))
out_ir = sorted(r["name"] for r in ir)
out_el, rep = [], []
for s, cur in sorted(irmods.items()):
    c = max(cur)
    cands = []
    for r in el:
        m = pat.match(r["name"])
        if m and m.group(2) == s and r["name"].upper().endswith(".NEF"):
            cands.append((abs(float(m.group(3)) - c), m.group(1), r["name"], int(r["size"])))
    if not cands:
        rep.append((s, c, "NO_EL", "", 0)); continue
    cands.sort()
    d, ts, n, sz = cands[0]
    out_el.append(n); rep.append((s, c, n, d, sz))
open(L + "A2_IR_names.txt", "w").write("\n".join(out_ir) + "\n")
open(L + "A2_EL_names.txt", "w").write("\n".join(out_el) + "\n")
for x in rep: print(*x, sep="\t")
print("IR files", len(out_ir), "IR modules", len(irmods), "EL picked", len(out_el), "EL bytes", sum(x[4] for x in rep))
