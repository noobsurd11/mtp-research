# applies the F2 decoder_init switch to scripts/train.py (run once in el_f2)
from pathlib import Path
p = Path("scripts/train.py"); s = p.read_text()
anchor = '''        logger.info("Encoder initialised from %s", load_encoder_init(model, cfg["model"]["encoder_init"]))
'''
assert s.count(anchor) == 1 and "decoder_init" not in s
add = '''    # ``model.decoder_init`` (opt-in, F2 / DDeP5; not in base.yaml): copy decoder.* weights (never the segmentation
    # head) from a file after the build; no random draw, so the head init for this seed is unchanged; absent = no change.
    if cfg["model"].get("decoder_init"):
        logger.info("Decoder initialised from %s", load_decoder_init(model, cfg["model"]["decoder_init"]))
'''
s = s.replace(anchor, anchor + add)
imp = "from src.models.encoder_init import load_encoder_init\n"
assert s.count(imp) == 1
s = s.replace(imp, "from src.models.encoder_init import load_decoder_init, load_encoder_init\n")
p.write_text(s)
print("patched")
