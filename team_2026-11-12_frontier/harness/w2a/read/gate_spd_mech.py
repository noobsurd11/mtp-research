"""Wave 2a gate, arm encoder_spd (LAUNCH_REQUEST_w2a.md section 8; cards/T1_recipes_spec.md arm 4, line 131;
cards/WAVE2_REVIEW.md X8): the mechanism gate at step 20,000.
  C1  layer3 and layer4 cosine to init >= 0.8                                  (spec: the G5 threshold used for PF)
  C2  layer3 and layer4 cosine >= 0.1 above the lambda-0 control w2a_spdctrl_f0_s5   (critic's addition)
  C3  conv1 and layer1 deviation larger than PF's                               (spec: "otherwise SPD is just PF")
Deviation = the probe's 'dev' = ||W - W0|| / ||W0|| per stage (src/trainers/enc_probe.py); 1 - cos is shown beside.

SPD and control values: the step-20000 row of each run's enc_probe.jsonl (written during training).
PF values: a CPU pass here over the W1-G checkpoints (latest.pth, models['model']) with the SAME function
(stage_stats and encoder_weights imported from bench_wt_w2/src/trainers/enc_probe.py) and the same init weights: the
model is built on the CPU as scripts/train.py builds it (torch.manual_seed(seed); build_model(cfg['model']) from the
run's config_used.yaml; ImageNet ResNet-34 file of the card, offline), and its encoder weights are W0.
Checks that W0 and the function are the training-time ones (all must hold, else the gate stops):
  V1  the weights file md5 equals the card's (f57b4305...)
  V2  W0 built with seed 5 = W0 built with seed 6, bit for bit (the encoder init does not depend on the seed)
  V3  for every run that has a training-time probe (10 spd, 1 control, 10 swad): stage_stats(W0, final weights) computed
      here equals the run's own step-20000 probe row (cos, nr, dev of the 5 stages) within 1e-9
  V4  for the 10 spd runs: the SPD anchors saved in latest.pth (the encoder parameters at optimizer build) equal the
      encoder parameters of the model built here, bit for bit (the lambda-0 control stores no anchors)
No metric of any held-out cell is read.

  CUDA_VISIBLE_DEVICES="" PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 nice -n 19 python gate_spd_mech.py --out <new folder>
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time

os.environ["HF_HUB_OFFLINE"] = "1"          # no network: the pretrained file comes from the local cache, as in the queue

import torch  # noqa: E402
import yaml  # noqa: E402

import w2agate as g  # noqa: E402

sys.path.insert(0, str(g.W2))
from src.models.model_factory import build_model  # noqa: E402
from src.trainers.enc_probe import encoder_weights, stage_stats  # noqa: E402

STAGES = ("conv1", "layer1", "layer2", "layer3", "layer4")
PF_SEEDS = (5, 6, 7, 8)
CARD = g.W2 / "bench/methods/encoder_spd_pf_v11.yaml"
TOL = 1e-9


def build_init(run, seed: int):
    """(W0 = encoder weight tensors with dim >= 2, encoder parameters in named_parameters order) of a fresh model."""
    cfg = yaml.safe_load((run / "config_used.yaml").read_text())
    torch.manual_seed(seed)
    model = build_model(cfg["model"])
    w0 = {k: v.detach().clone() for k, v in encoder_weights(model.state_dict()).items()}
    params = [(n, p.detach().clone().float()) for n, p in model.named_parameters() if n.startswith("encoder.")]
    return w0, params, cfg["model"]


def same_bits(a, b) -> bool:
    return a.dtype == b.dtype and a.shape == b.shape and a.contiguous().numpy().tobytes() == b.contiguous().numpy().tobytes()


def max_dev(a: dict, b: dict) -> float:
    return max(abs(a[s][f] - b[s][f]) for s in STAGES for f in ("cos", "nr", "dev"))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    g.guard_env()
    torch.set_num_threads(2)
    out = g.new_out(a.out)
    R = g.Report(out, "gate_spd_mech")
    t0 = time.time()
    head = subprocess.run(["git", "-C", str(g.W2), "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    R.p("# gate_spd_mech: mechanism gate of encoder_spd at step 20,000 (section 8)")
    R.p(f"started {time.strftime('%F %T')}; probe code {g.W2}/src/trainers/enc_probe.py md5 "
        f"{g.md5_file(g.W2 / 'src/trainers/enc_probe.py')[:8]}, model_factory.py md5 "
        f"{g.md5_file(g.W2 / 'src/models/model_factory.py')[:8]}, tree HEAD {head}, torch {torch.__version__}, "
        f"cuda available {torch.cuda.is_available()}")
    doc = {"checks": {}, "spd": {}, "pf": {}, "ctrl": {}}

    # ---- V1, V2: init weights
    card = yaml.safe_load(CARD.read_text())
    wf = card["weights"][0]
    v1 = g.md5_file(wf["path"]) == wf["md5"]
    w0, params, mcfg = build_init(g.pf_run(0, 5), 5)
    w0b, paramsb, mcfg_b = build_init(g.pf_run(0, 6), 6)
    w0c, _, mcfg_c = build_init(g.w2a_run("spd", 0, 5), 5)
    v2 = list(w0) == list(w0b) == list(w0c) and all(same_bits(w0[k], w0b[k]) and same_bits(w0[k], w0c[k]) for k in w0) \
        and all(n1 == n2 and same_bits(p1, p2) for (n1, p1), (n2, p2) in zip(params, paramsb)) and mcfg == mcfg_b == mcfg_c
    n_by = {}
    for k in w0:
        n_by[k.split(".")[1]] = n_by.get(k.split(".")[1], 0) + 1
    R.p(f"V1 weights file md5 = card ({wf['md5'][:8]}): {v1}")
    R.p(f"V2 W0 equal bit for bit for seed 5, seed 6 and the spd config; model section equal: {v2}; model {mcfg['name']}; "
        f"{len(w0)} encoder weight tensors with dim >= 2 by stage {n_by}; conv1 shape {tuple(w0['encoder.conv1.weight'].shape)}")
    doc["checks"].update({"V1_weights_md5": v1, "V2_init_seed_free": v2, "tensors_by_stage": n_by})
    if not (v1 and v2):
        R.p("STOP: init checks failed"); R.close(doc, "OPEN"); sys.exit(1)

    # ---- V3, V4: the function and W0 reproduce the training-time probe rows; anchors equal the built encoder
    R.p("\n## V3 / V4: this script's stage_stats(W0, final weights) against the run's own step-20000 probe row")
    R.p("run\tmax |difference| over 5 stages x (cos, nr, dev)\twithin 1e-9\tSPD anchors = built encoder parameters (bit for bit)")
    v3, v4, probe20 = True, True, {}
    probed = [("spd", k, s) for k in g.FOLDS for s in g.SEEDS] + [("spdctrl", 0, 5)] + \
             [("swad", k, s) for k in g.FOLDS for s in g.SEEDS]
    for arm, k, s in probed:
        run = g.w2a_run(arm, k, s)
        st = g.load_ckpt(run)
        mine = stage_stats(w0, st["models"]["model"])
        rows = g.probe_rows(run)
        assert sorted(rows) == list(range(2000, 20001, 2000)), (run, sorted(rows))
        theirs = rows[20000]
        assert tuple(theirs) == STAGES and all(theirs[x]["n"] == mine[x]["n"] for x in STAGES), (run, list(theirs))
        lg = g.probe_log(run)[20000]
        assert all(abs(theirs[x][f] - lg[x][f]) <= 5.01e-5 for x in STAGES for f in ("cos", "nr", "dev")), (run, "jsonl != log")
        d = max_dev(mine, theirs)
        ok = d <= TOL
        v3 &= ok
        anch = "n/a"
        spd = [o["spd"] for o in st["optimizers"].values() if isinstance(o, dict) and "spd" in o]
        if arm == "spd":
            assert len(spd) == 1 and list(spd[0]["anchors"]) == [1], (run, [list(x["anchors"]) for x in spd])
            A = spd[0]["anchors"][1]
            okA = len(A) == len(params) and all(same_bits(x, p) for x, (_, p) in zip(A, params))
            v4 &= okA
            anch = str(okA)
        elif arm == "spdctrl":
            anch = f"none stored (lambda 0): {not spd or not spd[0]['anchors']}"
        probe20[run.name] = theirs
        R.p(f"{run.name}\t{d:.2e}\t{ok}\t{anch}")
        del st
    R.p(f"V3 all 21 probe rows reproduced within {TOL:g}: {v3}; V4 anchors of the 10 spd runs equal the built encoder: {v4}")
    doc["checks"].update({"V3_probe_rows_reproduced": v3, "V4_anchors_equal": v4})
    if not (v3 and v4):
        R.p("STOP: the CPU pass does not reproduce the training-time probe"); R.close(doc, "OPEN"); sys.exit(1)

    # ---- PF: CPU pass over the W1-G checkpoints
    R.p("\n## PF (W1-G), CPU pass at step 20,000: cosine to init and deviation per stage")
    R.p("run\tcos conv1\tcos layer1\tcos layer2\tcos layer3\tcos layer4\tdev conv1\tdev layer1\tdev layer2\tdev layer3\tdev layer4")
    for k in g.FOLDS:
        for s in PF_SEEDS:
            run = g.pf_run(k, s)
            st = g.load_ckpt(run)
            assert st["cfg"]["model"] == mcfg and st["cfg"]["training"]["encoder_pf"]["lr_mult"] == 0.1, run
            doc["pf"][run.name] = stage_stats(w0, st["models"]["model"])
            v = doc["pf"][run.name]
            R.p(f"{run.name}\t" + "\t".join(f"{v[x]['cos']:.4f}" for x in STAGES) + "\t"
                + "\t".join(f"{v[x]['dev']:.4f}" for x in STAGES))
            del st

    def rng(d, stage, f):
        xs = [v[stage][f] for v in d.values()]
        return f"{min(xs):.4f} to {max(xs):.4f}"
    R.p(f"PF over 20 runs: cos layer3 {rng(doc['pf'], 'layer3', 'cos')}, layer4 {rng(doc['pf'], 'layer4', 'cos')}; "
        f"dev conv1 {rng(doc['pf'], 'conv1', 'dev')}, layer1 {rng(doc['pf'], 'layer1', 'dev')}")

    # ---- the gate
    ctrl = probe20["w2a_spdctrl_f0_s5"]
    doc["ctrl"] = ctrl
    R.p(f"\ncontrol w2a_spdctrl_f0_s5 (lambda 0) at 20k: cos layer3 {ctrl['layer3']['cos']:.4f}, layer4 "
        f"{ctrl['layer4']['cos']:.4f}; dev conv1 {ctrl['conv1']['dev']:.4f}, layer1 {ctrl['layer1']['dev']:.4f}")
    R.p("\n## gate per encoder_spd run (step 20,000)")
    R.p("run\tcos layer3\tcos layer4\tC1 both >= 0.8\tlayer3 - control\tlayer4 - control\tC2 both >= 0.1\tdev conv1 SPD / PF"
        "\tdev layer1 SPD / PF\tC3 both > PF\t1-cos conv1 SPD / PF\t1-cos layer1 SPD / PF")
    for k in g.FOLDS:
        for s in g.SEEDS:
            name = f"w2a_spd_f{k}_s{s}"
            v, pf = probe20[name], doc["pf"][f"w1g_pf_v11_f{k}_s{s}"]
            c1 = v["layer3"]["cos"] >= 0.8 and v["layer4"]["cos"] >= 0.8
            m3, m4 = v["layer3"]["cos"] - ctrl["layer3"]["cos"], v["layer4"]["cos"] - ctrl["layer4"]["cos"]
            c2 = m3 >= 0.1 and m4 >= 0.1
            c3 = v["conv1"]["dev"] > pf["conv1"]["dev"] and v["layer1"]["dev"] > pf["layer1"]["dev"]
            c3cos = (1 - v["conv1"]["cos"]) > (1 - pf["conv1"]["cos"]) and (1 - v["layer1"]["cos"]) > (1 - pf["layer1"]["cos"])
            doc["spd"][name] = {"stages": v, "C1": c1, "margin_layer3": m3, "margin_layer4": m4, "C2": c2, "C3": c3,
                                "C3_by_1_minus_cos": c3cos}
            R.p(f"{name}\t{v['layer3']['cos']:.4f}\t{v['layer4']['cos']:.4f}\t{'PASS' if c1 else 'FAIL'}\t{m3:+.4f}\t{m4:+.4f}\t"
                f"{'PASS' if c2 else 'FAIL'}\t{v['conv1']['dev']:.4f} / {pf['conv1']['dev']:.4f}\t"
                f"{v['layer1']['dev']:.4f} / {pf['layer1']['dev']:.4f}\t{'PASS' if c3 else 'FAIL'}\t"
                f"{1 - v['conv1']['cos']:.5f} / {1 - pf['conv1']['cos']:.5f}\t{1 - v['layer1']['cos']:.4f} / {1 - pf['layer1']['cos']:.4f}")
    S = doc["spd"]
    n1, n2, n3 = (sum(v[c] for v in S.values()) for c in ("C1", "C2", "C3"))
    f05 = S["w2a_spd_f0_s5"]
    C1 = "PASS" if n1 == 10 else "FAIL"
    # C2 as written: the control exists for fold 0, seed 5 only, so the rule is the matched run w2a_spd_f0_s5. The other
    # nine runs against that one control mix in fold and seed differences; their count is shown beside (run r1 of this
    # script used "all 10 runs" for C2 and printed FAIL, 7 of 10; the numbers are the same).
    C2 = "PASS" if f05["C2"] else "FAIL"
    C3 = "PASS" if n3 == 10 else "FAIL"
    verdict = "PASS" if (C1, C2, C3) == ("PASS", "PASS", "PASS") else "FAIL"
    m3s = [v["margin_layer3"] for v in S.values()]; m4s = [v["margin_layer4"] for v in S.values()]
    R.p(f"\nC1 layer3 / layer4 cosine >= 0.8: {C1} ({n1} of 10 runs; layer3 {rng({k: v['stages'] for k, v in S.items()}, 'layer3', 'cos')}, "
        f"layer4 {rng({k: v['stages'] for k, v in S.items()}, 'layer4', 'cos')}; fold 0 seed 5: {'PASS' if f05['C1'] else 'FAIL'})")
    R.p(f"C2 >= 0.1 above the control: {C2} (rule: the matched run fold 0 seed 5, margins layer3 / layer4 "
        f"{f05['margin_layer3']:+.4f} / {f05['margin_layer4']:+.4f}. Beside, not the rule: all 10 runs against the one "
        f"control run: {n2} of 10 clear 0.1 on both stages; margins layer3 {min(m3s):+.4f} to {max(m3s):+.4f} (mean "
        f"{sum(m3s) / 10:+.4f}), layer4 {min(m4s):+.4f} to {max(m4s):+.4f} (mean {sum(m4s) / 10:+.4f}))")
    R.p(f"C3 conv1 and layer1 deviation > PF's (same fold and seed): {C3} ({n3} of 10 runs; by 1 - cos instead of dev: "
        f"{sum(v['C3_by_1_minus_cos'] for v in S.values())} of 10)")
    R.p(f"VERDICT gate_spd_mech {verdict} (rule: C1 and C3 on all 10 runs, C2 on the matched run; fold 0 seed 5 alone, as "
        f"the spec wrote the pre-screen: {'PASS' if (f05['C1'] and f05['C2'] and f05['C3']) else 'FAIL'})")
    R.p("Pre-registered consequence if layer3 / layer4 < 0.8 (section 8; spec line 131), stated, not acted on here: one "
        "re-run at lambda 2.2 (new card version); if that also fails, drop SPD and record 'SPD does not preserve at lr "
        "1e-3'; L2-SP (alpha 0.01) then becomes the fallback arm.")
    doc.update({"C1": C1, "C2": C2, "C3": C3, "n_pass": [n1, n2, n3], "verdict": verdict, "C2_rule": "matched run f0 s5",
                "fold0_seed5": {c: f05[c] for c in ("C1", "C2", "C3")}, "seconds": round(time.time() - t0)})
    R.p(f"finished {time.strftime('%F %T')} ({doc['seconds']} s)")
    R.close(doc, verdict)


if __name__ == "__main__":
    main()
