"""Near-duplicate check: UCF-EL train images vs BenchmarkEL val + test (+ optional extra stems), 8 dihedral variants.
Images -> grayscale 64x64 (area), z-scored; max normalised correlation per BenchmarkEL image."""
import sys, numpy as np, cv2, os
from pathlib import Path
ucf_dir = Path(sys.argv[1]); bench_dir = Path(sys.argv[2]); stems = [l.strip() for f in sys.argv[3:] for l in open(f) if l.strip()]
def vec(p):
    im = cv2.imread(str(p), cv2.IMREAD_GRAYSCALE)
    im = cv2.resize(im, (64, 64), interpolation=cv2.INTER_AREA).astype(np.float32)
    return im
def z(a):
    a = a.reshape(len(a), -1); a = a - a.mean(1, keepdims=True); return a / (np.linalg.norm(a, axis=1, keepdims=True) + 1e-6)
U = [p for p in sorted(ucf_dir.rglob("*")) if p.suffix.lower() in (".png", ".jpg", ".jpeg", ".tif", ".bmp") and "annotation" not in str(p).lower() and "mask" not in str(p).lower()]
print("ucf images:", len(U), "bench stems:", len(stems), flush=True)
UZ = z(np.stack([vec(p) for p in U]))
B = []
for s in stems:
    im = vec(bench_dir / f"{s}.png")
    B.append(np.stack([np.rot90(v, k) for v in (im, im[:, ::-1]) for k in range(4)]))
B = np.stack(B)  # n, 8, 64, 64
BZ = z(B.reshape(-1, 64, 64)).reshape(len(stems), 8, -1)
best = []
for i, s in enumerate(stems):
    c = (BZ[i] @ UZ.T).max(0)  # per UCF image, best variant
    j = int(c.argmax()); best.append((float(c[j]), s, str(U[j].name)))
best.sort(reverse=True)
print("top matches (corr, bench stem, ucf file):")
for b in best[:10]: print("  %.3f %s %s" % b)
print("n with corr >= 0.95:", sum(b[0] >= 0.95 for b in best), " >= 0.90:", sum(b[0] >= 0.90 for b in best))
