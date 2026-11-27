"""cv02 card variants (bench/methods_cv02/): each equals bench/methods/<same name> except the weights paths (cv02 HF cache);
the cv02 queue renders, cfgchecks and names dumps from the original card and uses the variant only for the weights md5 check."""
import difflib
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
CV = sorted((REPO / "bench" / "methods_cv02").glob("*.yaml"))
CV02_HF = "/tmp/noob_el/cache/hf/hub/"
GAINT_HF = "/home/noob/.cache/huggingface/hub/"


def test_variants_exist():
    assert {p.stem for p in CV} == {"house_r34_unetpp", "house_r34_unetpp_pf", "house_r34_unetpp_v11", "house_r34_unetpp_pf_v11"}


@pytest.mark.parametrize("p", CV, ids=lambda p: p.stem)
def test_only_weights_path_differs(p):
    orig = REPO / "bench" / "methods" / p.name
    a, b = orig.read_text().splitlines(), p.read_text().splitlines()
    d = [l for l in difflib.unified_diff(a, b, lineterm="", n=0) if l[:1] in "+-" and l[:3] not in ("+++", "---")]
    assert len(d) == 2 and d[0].startswith("-  - path: " + GAINT_HF) and d[1].startswith("+  - path: " + CV02_HF), d
    assert d[0].replace(GAINT_HF, CV02_HF)[1:] == d[1][1:]
    r = subprocess.run([sys.executable, str(REPO / "bench" / "q" / "cv02" / "cvcard.py"), str(orig), str(p)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    assert r.stdout.split()[0] == "f57b430554b18e1238c4f92eac566544" and r.stdout.split()[1].startswith(CV02_HF)


def test_cvcard_refuses_other_change(tmp_path):
    orig = REPO / "bench" / "methods" / "house_r34_unetpp_pf_v11.yaml"
    bad = tmp_path / "house_r34_unetpp_pf_v11.yaml"
    bad.write_text((REPO / "bench" / "methods_cv02" / "house_r34_unetpp_pf_v11.yaml").read_text()
                   .replace("training.encoder_pf.lr_mult=0.1", "training.encoder_pf.lr_mult=0.2"))
    r = subprocess.run([sys.executable, str(REPO / "bench" / "q" / "cv02" / "cvcard.py"), str(orig), str(bad)],
                       capture_output=True, text=True)
    assert r.returncode == 1 and "beyond weights paths" in r.stdout, r.stdout


def test_slim_ckpt(tmp_path):
    torch = pytest.importorskip("torch")
    run = tmp_path / "r"; (run / "checkpoints").mkdir(parents=True)
    sd = {"w": torch.randn(3, 4), "n": torch.tensor(7)}
    torch.save({"format": 1, "step": 50, "cfg": {"training": {"total_steps": 50}}, "models": {"model": sd},
                "optimizers": {"x": torch.zeros(10)}}, run / "checkpoints" / "latest.pth")
    r = subprocess.run([sys.executable, str(REPO / "bench" / "q" / "cv02" / "slim_ckpt.py"), "--run", str(run)],
                       capture_output=True, text=True, env={"CUDA_VISIBLE_DEVICES": "", "PATH": "/usr/bin:/bin"})
    assert r.returncode == 0 and r.stdout.startswith("slim r step 50 keys ['model']"), r.stdout + r.stderr
    st = torch.load(run / "checkpoints" / "slim.pth", map_location="cpu", weights_only=False)
    assert set(st) == {"format", "step", "cfg", "models", "slim_of"} and torch.equal(st["models"]["model"]["w"], sd["w"])
    r2 = subprocess.run([sys.executable, str(REPO / "bench" / "q" / "cv02" / "slim_ckpt.py"), "--run", str(run)],
                        capture_output=True, text=True)
    assert r2.returncode != 0 and "refuse" in r2.stderr
    torch.save({"format": 1, "step": 40, "cfg": {"training": {"total_steps": 50}}, "models": {"model": sd}},
               tmp_path / "x.pth")
    run2 = tmp_path / "r2"; (run2 / "checkpoints").mkdir(parents=True); (tmp_path / "x.pth").rename(run2 / "checkpoints" / "latest.pth")
    r3 = subprocess.run([sys.executable, str(REPO / "bench" / "q" / "cv02" / "slim_ckpt.py"), "--run", str(run2)],
                        capture_output=True, text=True)
    assert r3.returncode != 0 and not (run2 / "checkpoints" / "slim.pth").exists()
