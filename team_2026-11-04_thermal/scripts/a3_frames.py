"""A3 frame index: parse altitude (m) and irradiance bin from IR .raw names (both naming styles). Library + CLI listing."""
import glob, os, re
B = os.path.expanduser("~/mtp/datasets/thermal_public/A3_dtu/extracted/IRT DATASET/")
def parse(name):
    n = os.path.basename(name)
    alt = re.search(r"_(\d+)m(?:_|\.| )", n)
    irr = re.search(r"_(abv800|200|600|800)(?:_|\.)", n)
    return (int(alt.group(1)) if alt else None, irr.group(1) if irr else None)
def frames():
    out = []
    for f in sorted(glob.glob(B + "*/*/IRT/*.raw")):
        rel = os.path.relpath(f, B); cls, mod = rel.split("/")[0], rel.split("/")[1]
        a, i = parse(f); out.append({"class": cls, "module": mod, "path": f, "alt_m": a, "irr": i})
    return out
if __name__ == "__main__":
    import collections
    fr = frames(); print(len(fr), "frames; unparsed:", [os.path.basename(x["path"]) for x in fr if x["alt_m"] is None or x["irr"] is None][:5])
    print(collections.Counter((x["alt_m"], x["irr"]) for x in fr))
