"""c3x smoke check (rulings C5 a and b, the lead's Q1 and Q2 rulings of 17 Nov; called by `c3x_smoke.sh check` after 'chain
done'). Read only, CPU. For every point it prints PASS or FAIL with the line or value that proves it. Exit 0 only if nothing
FAILs; nothing is ever SKIPped (review B1: a missing slim.pth is a FAIL).

(a) MEMORY: smoke_c3x_mem_hrnet (plain HRNet card) and smoke_c3x_mem_combo (c3x card), 300 steps each: config OK, startup line,
    rc 3 by design ('exit_after_step=300 reached'); peaks from Q/gpumem.log (1 s per-process log, label run_name=<job>).
    Lead's Q1 ruling: P = the HIGHEST peak of the c3x card on gaint over the memory smoke and the path smoke; job gate =
    max(11000, P + 2,048). Pass criterion: P - (plain HRNet peak) <= 1,024 MiB; above it the memory model is wrong and the
    lead looks before anything is armed (FAIL). Printed beside it: the cv02 estimate 8,432 + (c3x - plain on gaint).
(b) PATH: smoke_c3x_path (smoke card = c3x card with total_steps 600, enc_probe_every 200, swad window 300 to 600, encoder_pf
    freeze 100 and ramp 100):
    P0 queue: 'config OK (= card)', 'startup line OK: Labelled: 425 ...', 'trained smoke_c3x_path rc=0' (Q/launch.log);
       order of events as in the real run (config): freeze + ramp <= enc_probe_every <= swad start; 'PF encoder lr=0' at a
       logged step before the freeze ends and 'PF encoder lr' > 0 at the first probe step;
    P1 averagers built as the card says: the 'WAVG: [...]' line (start / end of swad, ema_9998 decay, checkpoint keys);
    P2 first encoder-probe call: the first 'ENC probe step <every>  model: ...' line (one stage, 'model'); all probe steps;
       enc_probe.jsonl rows: every cos, nr, dev finite and every cos below 1 (a moving encoder);
    P3 start of the averaging window (the code logs no line there): latest.pth weight_avg.swad = {start 300, end 600,
       n 301}: 301 updates = steps 300 to 600, so the first update was at step 300; ema_9998 n = 600; swad != model;
    P4 BN re-estimate: the 'WAVG BN recal: [ema_9998_bn, raw_bn, swad_bn] on 425 train cells' line; in latest.pth swad_bn
       equals swad in every tensor except BN running statistics, which differ;
    P5 final save with all readouts: 'step 600/600', 'saved latest.pth at step 600'; latest.pth step 600 with the six models
       keys model, swad, ema_9998, raw_bn, swad_bn, ema_9998_bn;
    P6 the two dumps: Q/dump/launch.log 'trained dump_smoke_c3x_path rc=0' and '.swad rc=0'; their stdout 'dumped ...: 107
       cells, ... key swad_bn, step 600' and '... key swad, step 600'; manifests (run id, key, step, set, checkpoint md5);
    P7 slim with --keys: 'slim smoke_c3x_path step 600 keys ['swad', 'swad_bn'] ...'; slim.pth exists, holds the dumped keys
       swad_bn and swad, and its tensors = latest's (a missing slim.pth or a missing key is a FAIL);
    F  every logged loss value (all 'step N/T  ...' lines) and every logged probe value is finite.
--fixture: a CPU test run with other step counts; expected steps are then read from config_used.yaml (normal mode: they
must be 600 / 200 / 300 / 600 / 100 / 100) and the device is not checked.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from pathlib import Path

N1, N2, N3 = "smoke_c3x_mem_hrnet", "smoke_c3x_mem_combo", "smoke_c3x_path"
METHOD = "smoke_c3x_hrnet_swad_path"
KEYS6 = {"model", "swad", "ema_9998", "raw_bn", "swad_bn", "ema_9998_bn"}
GATE_MIN, DELTA_MAX, CV02_HRNET = 11000, 1024, 8432
FAILS = []
NUM = r"[-+]?(?:\d+\.?\d*(?:[eE][-+]?\d+)?|nan|inf|NaN|Inf)"


def say(ok, tag, text):
    s = "PASS" if ok is True else "FAIL" if ok is False else "SKIP"
    if ok is False:
        FAILS.append(tag)
    print(f"{s}\t{tag}\t{text}")


def grep1(path: Path, rx: str):
    if not path.exists():
        return None
    for line in path.read_text(errors="replace").splitlines():
        if re.search(rx, line):
            return line
    return None


def allm(path: Path, rx: str):
    if not path.exists():
        return []
    return [line for line in path.read_text(errors="replace").splitlines() if re.search(rx, line)]


def peak(gm: Path, name: str):
    if not gm.exists():
        return None
    v = [int(x) for x in re.findall(rf"run_name={re.escape(name)}:(\d+)", gm.read_text(errors="replace"))]
    return max(v) if v else None


def md5(p: Path) -> str:
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def queue_lines(L: Path, n: str, rc: int):
    a = grep1(L, rf"\] {re.escape(n)} config OK \(= card\)$")
    say(a is not None, f"{n} cfgcheck", a or "no 'config OK (= card)' line")
    b = grep1(L, rf"\] {re.escape(n)} startup line OK: Labelled: 425 \(\S+/cv5v3_v11_f0/splits/train.txt\)  unlabelled: 0 \(-\)  val: 107  test: 107$")
    say(b is not None, f"{n} startup", b or "no 'startup line OK: Labelled: 425 ... val: 107  test: 107' line")
    c = grep1(L, rf"\] trained {re.escape(n)} rc={rc}$")
    say(c is not None, f"{n} rc", c or f"no 'trained {n} rc={rc}' line")


def finite(x) -> bool:
    try:
        return math.isfinite(float(x))
    except (TypeError, ValueError):
        return False


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--q", required=True)
    ap.add_argument("--repo", required=True)
    ap.add_argument("--dumps", required=True)
    ap.add_argument("--card", required=True)
    ap.add_argument("--fixture", action="store_true")
    a = ap.parse_args()
    Q, R, D = Path(a.q), Path(a.repo), Path(a.dumps)
    L, LD, GM = Q / "launch.log", Q / "dump" / "launch.log", Q / "gpumem.log"
    E = R / "experiments"
    print(f"# c3x smoke check: Q {Q}, repo {R}, dumps {D}{' (FIXTURE: CPU test run, not the smoke)' if a.fixture else ''}")
    # ---- (a) memory
    print("\n## (a) MEMORY and the gate")
    for n in (N1, N2):
        queue_lines(L, n, 3)
        x = grep1(E / f"{n}.stdout", r"exit_after_step=300 reached")
        say(x is not None, f"{n} 300 steps", x or "no 'exit_after_step=300 reached' line")
    p1, p2, p3 = peak(GM, N1), peak(GM, N2), peak(GM, N3)
    say(p1 is not None, "peak plain HRNet", f"{p1} MiB (memory smoke, gaint)")
    say(p2 is not None, "peak c3x card, memory smoke", f"{p2} MiB (gaint)")
    say(p3 is not None, "peak c3x card, path smoke", f"{p3} MiB (gaint; to step 600 with the BN re-estimate and the final evaluation)")
    if p2 is not None and p3 is not None:
        P = max(p2, p3)
        gate = max(GATE_MIN, P + 2048)
        print(f"RULE\tgate\tP = max({p2}, {p3}) = {P} MiB; job gate = max(11000, P + 2,048) = {gate} MiB (lead's Q1 ruling); "
              f"job list: GATE={gate} (c3x_queue.sh build) = python c3x_make_jobs.py <out>{'' if gate == GATE_MIN else f' --gate {gate}'}")
        if p1 is not None:
            d = P - p1
            say(d <= DELTA_MAX, "pass criterion", f"P - plain HRNet = {P} - {p1} = {d:+d} MiB (at most {DELTA_MAX}; above it: the memory "
                f"model is wrong, the lead looks before anything is armed); memory smoke alone {p2 - p1:+d} MiB")
            print(f"INFO\tcv02 estimate\t{CV02_HRNET} + (c3x - plain on gaint, memory smoke) {p2 - p1:+d} = {CV02_HRNET + p2 - p1} MiB; "
                  f"with P instead {CV02_HRNET + d} MiB (+ 2,048 = {CV02_HRNET + d + 2048})")
    # ---- (b) path
    print("\n## (b) PATH")
    queue_lines(L, N3, 0)
    so = E / f"{N3}.stdout"
    run = E / N3
    import yaml
    cfg = yaml.safe_load((run / "config_used.yaml").read_text()) if (run / "config_used.yaml").exists() else None
    if cfg is None:
        say(False, "config_used", f"{run}/config_used.yaml missing; nothing more to check")
        print(f"\n# {len(FAILS)} FAIL: {', '.join(FAILS)}")
        return 1
    t = cfg["training"]
    T, EV = int(t["total_steps"]), int(t["enc_probe_every"])
    S0, S1 = int(t["weight_avg"]["swad"]["start"]), int(t["weight_avg"]["swad"]["end"])
    FR, RP = int(t["encoder_pf"]["freeze"]), int(t["encoder_pf"]["ramp"])
    sched = f"total_steps {T}, enc_probe_every {EV}, swad {S0} to {S1}, encoder_pf freeze {FR} ramp {RP}"
    if not a.fixture:
        say((T, EV, S0, S1, FR, RP) == (600, 200, 300, 600, 100, 100), "smoke schedule", sched)
    else:
        print(f"INFO\tschedule\tfixture: {sched}")
    say(FR + RP <= EV <= S0 < S1 <= T, "P0 order of events",
        f"encoder unfrozen at {FR}, ramped by {FR + RP} <= first probe {EV} <= window start {S0} (real run: 1000 + 1000 <= 2000 <= 10000)")
    lr = {int(m.group(2)): float(m.group(1)) for x in allm(so, r"PF encoder lr=") for m in [re.search(rf"PF encoder lr=({NUM}) at step (\d+)", x)] if m}
    before = sorted(s for s in lr if s < FR)
    say(bool(before) and all(lr[s] == 0 for s in before) and lr.get(EV, 0) > 0, "P0 encoder frozen, then moving",
        f"PF encoder lr at logged steps before {FR}: {[(s, lr[s]) for s in before[-2:]]}; at the first probe step {EV}: {lr.get(EV)}")
    w = grep1(so, r"WAVG: \[")
    want = (f"('swad', {{'mode': 'uniform', 'decay': None, 'start': {S0}, 'end': {S1}, 'n': 0}})" in (w or "")
            and "('ema_9998', {'mode': 'ema', 'decay': 0.9998, 'start': 0, 'end': None, 'n': 0})" in (w or "")
            and "bn_recal True; checkpoint keys ['ema_9998', 'swad', 'raw_bn', 'ema_9998_bn', 'swad_bn']" in (w or ""))
    say(want, "P1 averagers built", w or "no 'WAVG: [' line")
    pl = allm(so, r"ENC probe step \d+ ")
    first = pl[0] if pl else None
    st = re.findall(r"  (\S+): cos=", first or "")
    say(bool(first) and int(re.search(r"ENC probe step (\d+) ", first).group(1)) == EV and st == ["model"],
        "P2 first probe call", first or "no 'ENC probe step' line")
    steps = [int(re.search(r"ENC probe step (\d+) ", x).group(1)) for x in pl]
    say(steps == list(range(EV, T + 1, EV)), "P2 probe steps", f"{steps}")
    jl = run / "enc_probe.jsonl"
    rows = [json.loads(x) for x in jl.read_text().splitlines() if x.strip()] if jl.exists() else []
    vals = [(r["step"], k, r["stages"]["model"].get(k)) for r in rows if "model" in r["stages"] for k in ("cos", "nr", "dev")]
    cos = [(r["step"], r["stages"]["model"]["cos"]) for r in rows if "model" in r["stages"]]
    say([r["step"] for r in rows] == steps and all(list(r["stages"]) == ["model"] and r["stages"]["model"]["n"] == 321 for r in rows),
        "P2 enc_probe.jsonl", f"{len(rows)} rows, steps {[r['step'] for r in rows]}, stages {sorted({s for r in rows for s in r['stages']})}, "
        f"n {sorted({r['stages']['model']['n'] for r in rows if 'model' in r['stages']})}")
    say(bool(cos) and all(finite(v) for _, _, v in vals) and all(c < 1.0 for _, c in cos), "P2 moving encoder, finite probe",
        f"cos per step {[(s, round(c, 8)) for s, c in cos]}; every cos, nr, dev finite: {all(finite(v) for _, _, v in vals)}; every cos < 1: {all(c < 1.0 for _, c in cos)}")
    sl = allm(so, rf"INFO src\.trainers\.trainer — step \d+/{T}  ")
    losses = [(int(re.search(r"step (\d+)/", x).group(1)), k, v) for x in sl for k, v in re.findall(rf"\b(loss\w*)=({NUM})", x)]
    bad = [(s, k, v) for s, k, v in losses if not finite(v)]
    say(bool(losses) and not bad, "F losses finite", f"{len(losses)} loss values on {len(sl)} step lines; non-finite: {bad[:5]}")
    pv = [v for x in pl for v in re.findall(rf"(?:cos|nr|dev)=({NUM})", x)]
    say(bool(pv) and all(finite(v) for v in pv), "F probe log values finite", f"{len(pv)} values in {len(pl)} 'ENC probe' lines")
    b = grep1(so, r"WAVG BN recal: ")
    say(b is not None and "['ema_9998_bn', 'raw_bn', 'swad_bn'] on 425 train cells" in b, "P4 BN re-estimate line", b or "no 'WAVG BN recal' line")
    f1 = grep1(so, rf"INFO src\.trainers\.trainer — step {T}/{T}  ")
    say(f1 is not None, "P5 last step line", (f1 or "no final step line")[:160])
    f2 = grep1(so, rf"saved latest\.pth at step {T}$")
    say(f2 is not None, "P5 final save line", f2 or f"no 'saved latest.pth at step {T}' line")
    import torch
    lp = run / "checkpoints" / "latest.pth"
    st = torch.load(lp, map_location="cpu", weights_only=False)
    M = st["models"]
    say(int(st["step"]) == T and set(M) == KEYS6, "P5 latest.pth", f"step {st['step']}, models keys {sorted(M)}")
    wa = st.get("weight_avg", {})
    sw, em = wa.get("swad", {}), wa.get("ema_9998", {})
    say(sw == {"mode": "uniform", "decay": None, "start": S0, "end": S1, "n": S1 - S0 + 1} and em.get("n") == T,
        "P3 averaging window", f"weight_avg.swad {sw}; ema_9998 n {em.get('n')} (window start {S0}: n = {S1} - {S0} + 1 = {S1 - S0 + 1})")
    fl = [k for k, v in M["model"].items() if v.is_floating_point()]
    dsw = max(float((M["swad"][k] - M["model"][k]).abs().max()) for k in fl)
    say(dsw > 0, "P3 swad != model", f"max |swad - model| over float tensors {dsw:.3e}")
    bnk = [k for k in M["swad"] if k.endswith(("running_mean", "running_var"))]
    other = [k for k in M["swad"] if not k.endswith(("running_mean", "running_var", "num_batches_tracked"))]
    neq = sum(not torch.equal(M["swad"][k], M["swad_bn"][k]) for k in bnk)
    oeq = all(torch.equal(M["swad"][k], M["swad_bn"][k]) for k in other)
    say(neq > 0 and oeq, "P4 swad_bn vs swad", f"BN running stats differ in {neq} of {len(bnk)} tensors; the other {len(other)} tensors equal: {oeq}")
    nf = [k for key in sorted(M) for k, v in M[key].items() if v.is_floating_point() and not bool(torch.isfinite(v).all())]
    say(not nf, "F weights finite", f"non-finite tensors in latest.pth models: {nf[:5]}")
    lmd5 = md5(lp)
    for rid, key, job in ((N3, "swad_bn", f"dump_{N3}"), (f"{N3}.swad", "swad", f"dump_{N3}.swad")):
        c = grep1(LD, rf"\] trained {re.escape(job)} rc=0$")
        if a.fixture:
            print(f"INFO\t{job} queue\tfixture: no dump queue")
        else:
            say(c is not None, f"P6 {job} rc", c or f"no 'trained {job} rc=0' line")
        d = grep1(E / f"{job}.stdout", rf"^dumped {re.escape(rid)} cv5v3_f0: 107 cells, .* key {key}, step {T}, ")
        say(d is not None, f"P6 {job} line", (d or f"no 'dumped {rid} ...: 107 cells ... key {key}, step {T}' line")[:200])
        mf = D / "elbench1" / METHOD / rid / "cv5v3_f0" / "manifest.json"
        m = json.loads(mf.read_text()) if mf.exists() else {}
        ok = (m.get("run_id"), m.get("weights_key"), m.get("step"), m.get("set"), m.get("checkpoint_md5")) == (rid, key, T, "cv5v3_f0", lmd5)
        say(ok, f"P6 {job} manifest", f"run_id {m.get('run_id')}, weights_key {m.get('weights_key')}, step {m.get('step')}, set {m.get('set')}, "
            f"checkpoint md5 {'= latest.pth' if m.get('checkpoint_md5') == lmd5 else m.get('checkpoint_md5')}, device {m.get('device')}, "
            f"train_code_revision {m.get('train_code_revision')}")
    sp = run / "checkpoints" / "slim.pth"
    if not sp.exists():   # review B1: the slim step with --keys is part of the PATH smoke; missing = FAIL, never SKIP
        say(False, "P7 slim", "no slim.pth: the slim step did not run or failed ('c3x_smoke.sh slim' returns slim_ckpt.py's rc; "
            "log Q/slim_smoke_c3x_path.log)")
    else:
        s = torch.load(sp, map_location="cpu", weights_only=False)
        miss = sorted({"swad_bn", "swad"} - set(s["models"]))
        eq = not miss and set(s["models"]) == {"swad_bn", "swad"} and all(torch.equal(s["models"][k][n], M[k][n]) for k in s["models"] for n in M[k])
        say(eq and s["slim_of"].get("keys") == ["swad_bn", "swad"] and set(s["slim_of"].get("all_keys", [])) == KEYS6 and s["slim_of"]["md5"] == lmd5,
            "P7 slim", f"keys {sorted(s['models'])}{f' (dumped keys missing: {miss})' if miss else ''}, slim_of keys {s['slim_of'].get('keys')}, "
            f"all_keys {s['slim_of'].get('all_keys')}, tensors equal to latest.pth: {eq}")
        sl2 = grep1(Q / f"slim_{N3}.log", r"^slim ") if (Q / f"slim_{N3}.log").exists() else None
        if sl2:
            print(f"INFO\tP7 slim line\t{sl2}")
    print(f"\n# {len(FAILS)} FAIL{': ' + ', '.join(FAILS) if FAILS else ''}")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
