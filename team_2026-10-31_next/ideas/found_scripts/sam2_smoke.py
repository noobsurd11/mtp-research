"""found, 31 Oct 2026: functional smoke of the sam2 venv on CPU (CUDA hidden). Builds SAM2.1 Hiera-T from the pinned source
and checkpoint, runs one box prompt on one val image. Prints shapes and timings only; no evaluation number."""
import os, time, hashlib
assert os.environ.get("CUDA_VISIBLE_DEVICES") == "", "CPU only"
import numpy as np, torch
from PIL import Image
import sam2
from sam2.build_sam import build_sam2
from sam2.sam2_image_predictor import SAM2ImagePredictor
torch.set_num_threads(8)
print("sam2 from", sam2.__file__, "| torch", torch.__version__, "| cuda avail", torch.cuda.is_available())
t0 = time.time()
m = build_sam2("configs/sam2.1/sam2.1_hiera_t.yaml", "/home/noob/work/weights/sam2.1_hiera_tiny.pt", device="cpu")
print(f"build {time.time() - t0:.1f}s params {sum(p.numel() for p in m.parameters())/1e6:.1f}M")
pred = SAM2ImagePredictor(m)
stem = sorted(l.strip() for l in open("/home/noob/work/el_f3/data/splits/val.txt") if l.strip())[0]
img = np.array(Image.open(f"/home/noob/work/el_f3/data/labeled/images/{stem}.png").convert("RGB"))
t0 = time.time(); pred.set_image(img); t1 = time.time()
masks, scores, _ = pred.predict(box=np.array([128, 128, 384, 384]), multimask_output=True)
print(f"set_image {t1 - t0:.1f}s predict {time.time() - t1:.2f}s masks {masks.shape} dtype {masks.dtype} n_scores {len(scores)}")
print("SMOKE OK")
