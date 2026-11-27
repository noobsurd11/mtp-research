"""Wave 2a gate, arm swad_const (LAUNCH_REQUEST_w2a.md section 8; cards/T1_recipes_spec.md arm 3, line 98): the pre-screen
"fail if the training loss over steps 15k to 20k is above PF's at 10k, or if swad_bn crack relF1@2 on fold 0 is below PF
raw by more than 0.05", and the report of the layer3 / layer4 cosine to init at 20k (WAVE2_REVIEW: say so if below 0.8).

(a) Loss. Source: the trainer's lines 'step N/20000  loss=X' in train.log (log_every 50; X = mean loss of the 50 steps
    ending at N, 4 significant digits). swad side: the 100 lines N = 15050 ... 20000 of w2a_swad_f<k>_s<s>, averaged with
    equal weight = mean loss of steps 15,001 to 20,000. PF side: the one line N = 10000 of w1g_pf_v11_f<k>_s<s> (same fold
    and seed) = mean loss of steps 9,951 to 10,000. PASS per run: swad mean <= PF value. The same two values from
    metrics.json train_curve (full precision) are checked against the log lines. Shown beside, not part of the rule: PF's
    mean over the 20 lines N = 9550 ... 10500, and how many of the 100 swad lines lie above PF's line at 10000.
    The spec wrote the pre-screen for fold 0, seed 5; all 10 runs are trained, so every run is checked.
(b) Fold 0, pass / fail only (no value is printed or written by this script): scripts/bench_score.py of the reviewed read
    tree (bench_wt_b b5bf0ae) makes the records of the fold-0 dumps w1g_pf_v11_f0_s<s> (PF raw) and
    w2a_swad_f0_s<s>.swad_bn with --labels v11, then its summary gives relF1_2 on all 107 fold-0 cells (argmax).
    PASS per seed: swad_bn relF1_2 >= PF relF1_2 - 0.05. A seed whose swad_bn dump is missing, or whose dump job is not
    rc=0 in the dump launch.log, is OPEN and the commands are printed. The record files stay in <out>/b/ (they hold
    per-cell counts; nobody needs to open them before the read).
(c) Report: layer3 / layer4 cosine to init at step 20000 from enc_probe.jsonl (last row per step), checked against the
    'ENC probe step 20000' line of train.log. Not a pass / fail item; "below 0.8" is flagged.

  CUDA_VISIBLE_DEVICES="" PYTHONDONTWRITEBYTECODE=1 nice -n 19 python gate_swad_prescreen.py --out <new folder> [--skip-b]
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import time
from pathlib import Path

import w2agate as g

PY = "/home/noob/work/el-fault-detection/.venv/bin/python"
DLOG = g.W / "bq/w2a2/dump/launch.log"
SWAD_DUMPS = g.DUMPS_W2A / "swad_const_pf_v11"
TOL = 0.05


def loss_part(R: g.Report) -> dict:
    R.p("\n## (a) training loss: swad mean of steps 15,001 to 20,000 against PF's log line at step 10,000 (same fold, seed)")
    R.p("run\tswad mean 15k-20k (log)\tPF at 10k (log)\tverdict\tswad - PF\tswad mean (metrics.json)\tPF at 10k "
        "(metrics.json)\tPF mean 9,501-10,500\tswad lines above PF 10k (of 100)\tswad highest line\tresumes swad, PF"
        "\tfirst log lines equal to PF")
    res = {}
    for k in g.FOLDS:
        for s in g.SEEDS:
            sr, pr = g.w2a_run("swad", k, s), g.pf_run(k, s)
            sl, pl = g.loss_lines(sr), g.loss_lines(pr)
            (sc, sres), (pc, pres) = g.curve(sr), g.curve(pr)
            steps = list(range(15050, 20001, 50))
            assert len(steps) == 100 and all(n in sl for n in steps), (sr, "swad loss lines 15050..20000 incomplete")
            assert sorted(sl) == sorted(pl) == list(range(50, 20001, 50)), (sr, "expected 400 loss lines per run")
            sw = sum(sl[n] for n in steps) / 100
            sw_full = sum(sc[n] for n in steps) / 100
            pf, pf_full = pl[10000], pc[10000]
            pf_band = sum(pl[n] for n in range(9550, 10501, 50)) / 20
            assert abs(sw - sw_full) < 5e-4 and abs(pf - pf_full) < 5e-4 * max(1.0, pf), (sr, sw, sw_full, pf, pf_full)
            n_eq = 0
            for n in sorted(sl):
                if sc[n] != pc[n]:
                    break
                n_eq += 1
            ok = sw <= pf
            res[sr.name] = {"swad_mean_15k_20k_log": sw, "pf_10k_log": pf, "pass": ok, "swad_mean_15k_20k_full": sw_full,
                            "pf_10k_full": pf_full, "pass_full": sw_full <= pf_full, "pf_mean_9501_10500": pf_band,
                            "pass_vs_pf_band": sw <= pf_band, "swad_lines_above_pf10k": sum(sl[n] > pf for n in steps),
                            "swad_max_line": max(sl[n] for n in steps), "resumes": [sres, pres],
                            "first_lines_equal_to_pf": n_eq}
            R.p(f"{sr.name}\t{sw:.4f}\t{pf:.4f}\t{'PASS' if ok else 'FAIL'}\t{sw - pf:+.4f}\t{sw_full:.4f}\t{pf_full:.4f}"
                f"\t{pf_band:.4f}\t{res[sr.name]['swad_lines_above_pf10k']}\t{res[sr.name]['swad_max_line']:.4f}\t"
                f"{sres}, {pres}\t{n_eq}")
    n = sum(v["pass"] for v in res.values())
    nb = sum(v["pass_vs_pf_band"] for v in res.values())
    f0 = res["w2a_swad_f0_s5"]["pass"]
    R.p(f"(a) as written (fold 0, seed 5): {'PASS' if f0 else 'FAIL'}; all runs: {n} of 10 pass; full-precision values "
        f"agree on every verdict: {all(v['pass'] == v['pass_full'] for v in res.values())}; against PF's mean over "
        f"9,501 to 10,500 (beside, not the rule): {nb} of 10 pass")
    return {"runs": res, "n_pass": n, "fold0_seed5_pass": f0, "n_pass_vs_pf_band": nb}


def dump_ok(job: str) -> bool:
    return any(line.rstrip().endswith(f"trained {job} rc=0") for line in open(DLOG, errors="replace"))


def score_part(R: g.Report, out: Path, skip: bool) -> dict:
    R.p(f"\n## (b) fold 0: swad_bn crack relF1@2 >= PF raw - {TOL} (pass / fail only; argmax, labels v11, 107 cells)")
    env = dict(os.environ, CUDA_VISIBLE_DEVICES="", PYTHONDONTWRITEBYTECODE="1", OMP_NUM_THREADS="1")
    res = {}
    b = out / "b"
    for s in g.SEEDS:
        pf_id, sw_id = f"w1g_pf_v11_f0_s{s}", f"w2a_swad_f0_s{s}.swad_bn"
        pd, sd = g.DUMPS_PF / pf_id / "cv5v2_f0", SWAD_DUMPS / sw_id / "cv5v2_f0"
        job = f"dump_w2a_swad_f0_s{s}_swad_bn"
        cmds = [["nice", "-n", "19", PY, "scripts/bench_score.py", "records", "--dumps", str(d), "--set", "cv5v2_f0",
                 "--labels", "v11", "--out", str(b / f"rec_{rid}.json")] for d, rid in ((pd, pf_id), (sd, sw_id))]
        cmds.append(["nice", "-n", "19", PY, "scripts/bench_score.py", "summary", "--records", str(b / f"rec_{pf_id}.json"),
                     str(b / f"rec_{sw_id}.json"), "--arms", f"PF={pf_id}", f"SWADBN={sw_id.replace('.', chr(92) + '.')}",
                     "--out", str(b / f"sum_f0_s{s}.json")])
        have = (sd / "manifest.json").exists() and dump_ok(job) and (pd / "manifest.json").exists()
        if skip or not have:
            why = "--skip-b" if skip else f"dump missing or not rc=0 in {DLOG}: {sd}"
            res[f"s{s}"] = {"verdict": "OPEN", "why": why}
            R.p(f"seed {s}: OPEN ({why}). Commands (cwd {g.RB}):")
            for c in cmds:
                R.p("  " + " ".join(c))
            continue
        b.mkdir(exist_ok=True)
        for c in cmds:
            r = subprocess.run(c, cwd=g.RB, env=env, capture_output=True, text=True)
            if r.returncode != 0:
                raise SystemExit(f"bench_score.py failed ({' '.join(c)}):\n{r.stdout}\n{r.stderr}")
        doc = json.loads((b / f"sum_f0_s{s}.json").read_text())
        assert doc["n_cells"] == 107 and doc["arms"]["PF"]["runs"] == [pf_id] and doc["arms"]["SWADBN"]["runs"] == [sw_id]
        d = doc["arms"]["SWADBN"]["subsets"]["all"]["relF1_2"]["mean"] - doc["arms"]["PF"]["subsets"]["all"]["relF1_2"]["mean"]
        ok = d >= -TOL
        res[f"s{s}"] = {"verdict": "PASS" if ok else "FAIL", "scorer_md5": doc["scorer_md5"], "files": str(b)}
        R.p(f"seed {s}: {'PASS' if ok else 'FAIL'} ({sw_id} against {pf_id}; bench_score.py {doc['scorer_md5'][:8]}; "
            f"value not shown)")
    vs = [v["verdict"] for v in res.values()]
    res["as_written_fold0_seed5"] = res["s5"]["verdict"]
    res["overall"] = "FAIL" if "FAIL" in vs else ("OPEN" if "OPEN" in vs else "PASS")
    R.p(f"(b) as written (fold 0, seed 5): {res['s5']['verdict']}; both seeds: {res['overall']}")
    return res


def cos_part(R: g.Report) -> dict:
    R.p("\n## (c) report: cosine to init at step 20,000 per encoder stage (enc_probe.jsonl; not a pass / fail item)")
    R.p("run\tconv1\tlayer1\tlayer2\tlayer3\tlayer4\tlayer3 or layer4 below 0.8\tjsonl = train.log line (4 decimals)")
    res = {}
    for k in g.FOLDS:
        for s in g.SEEDS:
            run = g.w2a_run("swad", k, s)
            st, lg = g.probe_rows(run)[20000], g.probe_log(run)[20000]
            same = all(abs(st[x][f] - lg[x][f]) <= 5.01e-5 for x in st for f in ("cos", "nr", "dev"))
            below = st["layer3"]["cos"] < 0.8 or st["layer4"]["cos"] < 0.8
            res[run.name] = {"stages": st, "below_0.8": below, "jsonl_equals_log": same}
            R.p(f"{run.name}\t" + "\t".join(f"{st[x]['cos']:.4f}" for x in ("conv1", "layer1", "layer2", "layer3", "layer4"))
                + f"\t{below}\t{same}")
    l3 = [v["stages"]["layer3"]["cos"] for v in res.values()]; l4 = [v["stages"]["layer4"]["cos"] for v in res.values()]
    nb = sum(v["below_0.8"] for v in res.values())
    R.p(f"(c) layer3 cosine {min(l3):.4f} to {max(l3):.4f}, layer4 {min(l4):.4f} to {max(l4):.4f}; runs with layer3 or "
        f"layer4 below 0.8: {nb} of 10 (WAVE2_REVIEW: if below 0.8, say so beside the result)")
    return {"runs": res, "layer3_range": [min(l3), max(l3)], "layer4_range": [min(l4), max(l4)], "n_below_0.8": nb}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--skip-b", action="store_true", help="do not score; print the commands of part (b) and mark it OPEN")
    a = ap.parse_args()
    g.guard_env()
    out = g.new_out(a.out)
    R = g.Report(out, "gate_swad_prescreen")
    t0 = time.time()
    R.p("# gate_swad_prescreen: section 8 pre-screen of swad_const (a) loss, (b) fold-0 relF1@2, (c) cosine report")
    R.p(f"started {time.strftime('%F %T')}")
    A = loss_part(R)
    B = score_part(R, out, a.skip_b)
    C = cos_part(R)
    a_all = A["n_pass"] == 10
    if not a_all or B["overall"] == "FAIL":
        verdict = "FAIL"
    elif B["overall"] == "OPEN":
        verdict = "OPEN"
    else:
        verdict = "PASS"
    as_written = "FAIL" if (not A["fold0_seed5_pass"] or B["s5"]["verdict"] == "FAIL") else \
        ("OPEN" if B["s5"]["verdict"] == "OPEN" else "PASS")
    R.p(f"\nVERDICT gate_swad_prescreen {verdict} (rule used: (a) on all 10 runs and (b) on both fold-0 seeds; "
        f"as the spec wrote it, fold 0 seed 5 only: {as_written})")
    R.p(f"finished {time.strftime('%F %T')} ({round(time.time() - t0)} s)")
    R.close({"a": A, "b": B, "c": C, "verdict": verdict, "as_written_fold0_seed5": as_written}, verdict)


if __name__ == "__main__":
    main()
