"""F3 patch 2 (runner, 30 Oct; coach_100.md (a)): encoder-preserving fine-tune (PF), opt-in ``training.encoder_pf``
{freeze, ramp, lr_mult, wd}. Run from the el_f3 worktree root. Absent: the optimizer and scheduler are built exactly as
before (one group, one lambda). Present: group 0 = everything but the encoder (house lr, wd, schedule), group 1 = encoder
(lr x lr_mult, weight decay wd, multiplier = house x 0 before ``freeze`` steps then a linear ramp over ``ramp`` steps).
No requires_grad toggling (the graph, BN train mode and RNG are unchanged). The encoder lr is logged on its own line
("PF encoder lr=..."), never in the step line."""
from pathlib import Path

tr = Path("src/trainers/trainer.py"); s = tr.read_text()
old_a = '''        raise ValueError(f"unknown lr_scheduler {schedule!r}")
    return f
'''
new_a = '''        raise ValueError(f"unknown lr_scheduler {schedule!r}")
    return f


def build_pf_lr_lambda(base, pf: dict):
    """F3 (opt-in ``training.encoder_pf``): encoder-group multiplier = base x (0 for steps < ``freeze``, then a linear ramp
    over ``ramp`` steps to 1; ramp 0 = no ramp). The group's lr (base lr x ``lr_mult``) and weight decay are set by
    ``build_optimizer`` in scripts/train.py. Neutral (freeze 0, ramp 0) returns exactly ``base(step)``."""
    fr, rp = int(pf.get("freeze", 1000)), int(pf.get("ramp", 1000))

    def g(step: int) -> float:
        if step < fr:
            return 0.0
        return base(step) * (min((step - fr + 1) / rp, 1.0) if rp > 0 else 1.0)
    return g


def build_lr_lambdas(t: dict, total_steps: int):
    """The scheduler's lr multiplier(s): the house lambda, or [house, encoder PF] with ``training.encoder_pf`` (F3)."""
    base = build_lr_lambda(total_steps, int(t.get("warmup_steps", 0)), t.get("lr_scheduler", "cosine"),
                           float(t.get("poly_power", 0.9)))
    pf = t.get("encoder_pf")
    return [base, build_pf_lr_lambda(base, pf)] if pf else base
'''
old_b = '''        self.scheduler = torch.optim.lr_scheduler.LambdaLR(
            optimizer,
            build_lr_lambda(self.total_steps, int(t.get("warmup_steps", 0)), t.get("lr_scheduler", "cosine"),
                            float(t.get("poly_power", 0.9))),
        )
        self.num_classes = cfg["model"]["num_classes"]
'''
new_b = '''        # F3 (opt-in ``training.encoder_pf``): group 0 = decoder + head (house), group 1 = encoder (PF multiplier).
        self.encoder_pf = t.get("encoder_pf") or None
        if self.encoder_pf and len(optimizer.param_groups) != 2:
            raise ValueError("training.encoder_pf needs the 2-group optimizer built by build_optimizer")
        self.scheduler = torch.optim.lr_scheduler.LambdaLR(optimizer, build_lr_lambdas(t, self.total_steps))
        self.num_classes = cfg["model"]["num_classes"]
'''
old_c = '''                logger.info("step %d/%d  %s", done, self.total_steps,
                            "  ".join(f"{k}={v:.4g}" for k, v in avg.items() if k != "step"))
                window = []
'''
new_c = '''                logger.info("step %d/%d  %s", done, self.total_steps,
                            "  ".join(f"{k}={v:.4g}" for k, v in avg.items() if k != "step"))
                if self.encoder_pf:  # F3: own line, so the step line (identity checks) is unchanged
                    logger.info("PF encoder lr=%.4g at step %d", self.optimizer.param_groups[1]["lr"], done)
                window = []
'''
for o, n in ((old_a, new_a), (old_b, new_b), (old_c, new_c)):
    assert s.count(o) == 1, o[:70]
    s = s.replace(o, n)
tr.write_text(s)

tp = Path("scripts/train.py"); s = tp.read_text()
old_d = '''    wd = t.get("weight_decay", 1e-4)
    if name == "adam":
        return torch.optim.Adam(model.parameters(), lr=t["lr"], weight_decay=wd)
'''
new_d = '''    wd = t.get("weight_decay", 1e-4)
    pf = t.get("encoder_pf")
    if pf:  # F3 (opt-in): encoder-preserving fine-tune. Group 0 = everything but the encoder (house lr and wd); group 1 =
        # encoder.* with lr x lr_mult and its own weight decay. Freeze / ramp: the trainer's per-group lr multiplier.
        if name not in ("adam", "adamw"):
            raise ValueError("training.encoder_pf supports adam / adamw")
        named = list(model.named_parameters())
        enc = [p for n, p in named if n.startswith("encoder.")]
        if not enc:
            raise ValueError("training.encoder_pf: the model has no encoder.* parameters")
        groups = [{"params": [p for n, p in named if not n.startswith("encoder.")]},
                  {"params": enc, "lr": t["lr"] * float(pf.get("lr_mult", 0.1)), "weight_decay": float(pf.get("wd", 0.0))}]
        return (torch.optim.Adam if name == "adam" else torch.optim.AdamW)(groups, lr=t["lr"], weight_decay=wd)
    if name == "adam":
        return torch.optim.Adam(model.parameters(), lr=t["lr"], weight_decay=wd)
'''
assert s.count(old_d) == 1
tp.write_text(s.replace(old_d, new_d))

Path("tests/test_f3_pf.py").write_text('''"""F3 PF (training.encoder_pf): absent = house (one group, one lambda); neutral = house bit for bit; freeze / ramp / wd."""
import importlib.util
import sys
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.trainers.trainer import build_lr_lambdas  # noqa: E402

_spec = importlib.util.spec_from_file_location("f3_train_mod", ROOT / "scripts" / "train.py")
train = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(train)


class Tiny(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.encoder = torch.nn.Sequential(torch.nn.Conv2d(1, 4, 3), torch.nn.BatchNorm2d(4), torch.nn.ReLU())
        self.decoder = torch.nn.Conv2d(4, 4, 1)
        self.segmentation_head = torch.nn.Conv2d(4, 2, 1)

    def forward(self, x):
        return self.segmentation_head(self.decoder(self.encoder(x)))


def _t(pf=None):
    t = {"optimizer": "adam", "lr": 1e-3, "weight_decay": 1e-4, "warmup_steps": 3, "lr_scheduler": "cosine"}
    if pf is not None:
        t["encoder_pf"] = pf
    return t


def _run(t, steps=12):
    torch.manual_seed(0); m = Tiny(); m.train()
    init = {k: v.clone() for k, v in m.state_dict().items()}
    opt = train.build_optimizer(m, {"training": t})
    sch = torch.optim.lr_scheduler.LambdaLR(opt, build_lr_lambdas(t, steps))
    g = torch.Generator().manual_seed(1); lrs = []
    for _ in range(steps):
        lrs.append([pg["lr"] for pg in opt.param_groups])
        loss = m(torch.randn(2, 1, 8, 8, generator=g)).pow(2).mean()
        opt.zero_grad(); loss.backward(); torch.nn.utils.clip_grad_norm_(m.parameters(), 1.0); opt.step(); sch.step()
    return m, init, opt, lrs


def test_pf_absent_is_one_group_one_lambda():
    m, _, opt, _ = _run(_t())
    assert len(opt.param_groups) == 1 and callable(build_lr_lambdas(_t(), 10))
    assert len(opt.param_groups[0]["params"]) == len(list(m.parameters()))


def test_pf_neutral_equals_house_bit_for_bit():
    mh, _, _, lh = _run(_t())
    mn, _, opt, ln = _run(_t({"freeze": 0, "ramp": 0, "lr_mult": 1.0, "wd": 1e-4}))
    assert len(opt.param_groups) == 2
    assert all(torch.equal(a, b) for a, b in zip(mh.state_dict().values(), mn.state_dict().values()))
    assert all(x[0] == y[0] == y[1] for x, y in zip(lh, ln))


def test_pf_freeze_ramp_and_wd():
    pf = {"freeze": 4, "ramp": 4, "lr_mult": 0.1, "wd": 0.0}
    lam = build_lr_lambdas(_t(pf), 100); base, enc = lam
    assert [enc(s) for s in range(4)] == [0.0] * 4
    assert abs(enc(4) - base(4) * 0.25) < 1e-15 and abs(enc(7) - base(7)) < 1e-15 and abs(enc(50) - base(50)) < 1e-15
    m, init, opt, lrs = _run(_t(pf), steps=4)
    assert opt.param_groups[1]["weight_decay"] == 0.0 and abs(opt.param_groups[1]["initial_lr"] - 1e-4) < 1e-15
    sd = m.state_dict()
    enc_w = [k for k in sd if k.startswith("encoder.") and not k.endswith(("running_mean", "running_var", "num_batches_tracked"))]
    assert all(torch.equal(sd[k], init[k]) for k in enc_w)            # frozen by lr 0 (no requires_grad toggle)
    assert not torch.equal(sd["encoder.1.running_mean"], init["encoder.1.running_mean"])  # BN in train mode adapts
    assert not torch.equal(sd["decoder.weight"], init["decoder.weight"])
    assert all(x[1] == 0.0 for x in lrs)


def test_pf_default_off_in_configs():
    for f in ("configs/base.yaml", "configs/supervised.yaml"):
        assert "encoder_pf" not in (ROOT / f).read_text()
''')
print("patched trainer.py, train.py; wrote tests/test_f3_pf.py")
