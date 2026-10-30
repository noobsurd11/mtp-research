# applies the F1 encoder_init switch to scripts/train.py (run once in el_f1)
from pathlib import Path
p = Path("scripts/train.py"); s = p.read_text()
anchor = '''        model_b = build_model(cfg["model"]).to(device)
        torch.manual_seed(seed)
'''
assert s.count(anchor) == 1 and "encoder_init" not in s
add = '''    # ``model.encoder_init`` (opt-in, F1 / MIM5; not in base.yaml): copy encoder weights from a file after the build.
    # Loading draws no random numbers, so the decoder init for this seed is unchanged; absent = no change.
    if cfg["model"].get("encoder_init"):
        logger.info("Encoder initialised from %s", load_encoder_init(model, cfg["model"]["encoder_init"]))
'''
s = s.replace(anchor, anchor + add)
imp = "from src.models.model_factory import build_model\n"
assert s.count(imp) == 1
s = s.replace(imp, imp + "from src.models.encoder_init import load_encoder_init\n")
p.write_text(s)
print("patched")
