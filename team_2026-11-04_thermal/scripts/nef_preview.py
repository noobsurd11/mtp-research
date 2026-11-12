"""Extract the largest embedded JPEG preview from a Nikon NEF (TIFF container) without decoding raw data.
Library use: from nef_preview import nef_largest_jpeg; arr, info = nef_largest_jpeg(path)  (arr: uint8 HxW grayscale, or HxWx3)
CLI: python -I nef_preview.py <file.NEF> [out.png]   prints the preview candidates and saves the largest (outside data dirs only).
Reads the file as data; nothing in it is executed."""
import io, sys
import numpy as np
import tifffile
from PIL import Image

def _candidates(path):
    out = []
    with tifffile.TiffFile(path) as tf:
        fh = tf.filehandle
        def visit(page, tag_prefix):
            tags = page.tags
            # JPEGInterchangeFormat (513) / Length (514): Nikon stores previews this way
            if 513 in tags and 514 in tags:
                ov, lv = tags[513].value, tags[514].value
                ov = ov if isinstance(ov, (tuple, list)) else (ov,)
                lv = lv if isinstance(lv, (tuple, list)) else (lv,)
                for off, ln in zip(ov, lv):
                    out.append((int(ln), int(off), f"{tag_prefix}:513"))
            # strip-based JPEG (compression 6 / 7) pages
            comp = tags[259].value if 259 in tags else None
            if comp in (6, 7) and 273 in tags and 279 in tags:
                offs, lens = tags[273].value, tags[279].value
                if isinstance(offs, int): offs, lens = [offs], [lens]
                if len(offs) == 1:
                    out.append((int(lens[0]), int(offs[0]), f"{tag_prefix}:strip"))
        for i, p in enumerate(tf.pages):
            visit(p, f"page{i}")
            for j, sp in enumerate(getattr(p, "pages", []) or []):
                visit(sp, f"page{i}.sub{j}")
        # SubIFDs exposed by tifffile as series/pages with is_subifd
        for s in tf.series:
            for k, p in enumerate(s.pages):
                if p is not None and hasattr(p, "tags"):
                    visit(p, f"series{s.index}.{k}")
        res = []
        seen = set()
        for ln, off, where in sorted(out, reverse=True):
            if (off, ln) in seen: continue
            seen.add((off, ln))
            fh.seek(off); b = fh.read(ln)
            if b[:2] == b"\xff\xd8":
                res.append((ln, off, where, b))
        return res

def nef_largest_jpeg(path):
    best = None
    for ln, off, where, b in _candidates(path):
        try:
            im = Image.open(io.BytesIO(b)); im.load()
        except Exception:
            continue
        key = im.size[0] * im.size[1]
        if best is None or key > best[0]:
            best = (key, im, where, ln)
    if best is None:
        raise ValueError("no embedded JPEG found")
    _, im, where, ln = best
    info = {"where": where, "bytes": ln, "size": im.size, "mode": im.mode}
    return np.asarray(im), info

if __name__ == "__main__":
    p = sys.argv[1]
    for ln, off, where, b in _candidates(p):
        try:
            im = Image.open(io.BytesIO(b)); print(where, ln, im.size, im.mode)
        except Exception as e:
            print(where, ln, "unreadable", e)
    arr, info = nef_largest_jpeg(p)
    print("largest:", info, arr.shape, arr.dtype)
    if len(sys.argv) > 2:
        Image.fromarray(arr).save(sys.argv[2])
