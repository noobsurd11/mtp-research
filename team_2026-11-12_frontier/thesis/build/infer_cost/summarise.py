"""G-N7: tables from raw/{verify,flops}.json, raw/cpu/*.json and (when the lead has copied them) raw/gpu/*.json.
Output: raw/tables.md (pasted into thesis/INFERENCE_COST.md) and raw/summary_timing.tsv (one row per timing json).
Direct = the arm itself was timed (E). Composed (marked *) = forwards per cell x the unit forward of the same model, thread
count and batch (UPF = PF view, UHR = HRNet view; each includes its softmax): median x k and p90 x k (p90 x k is an upper
bound of the p90 of a sum of k forwards); a judgement (S) that per-cell cost is additive over forwards, checked against the
direct runs (raw/tables.md section 'additivity check').
"""
import json
import statistics as st
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"
ARMS = [("C1", "C1", "pf", 1), ("C1-D4", "C1D4", "pf", 8), ("C2", "C2", "hrnet", 8), ("C3", "C3", "hrnet", 40),
        ("E-PF", "EPF", "pf", 5)]
UNIT = {"pf": "UPF", "hrnet": "UHR"}


def load(d):
    out = {}
    for p in sorted((RAW / d).glob("*.json")) if (RAW / d).exists() else []:
        j = json.loads(p.read_text())
        if "timing" in j:
            out[p.stem] = j
    return out


def fmt(x):
    return f"{x:.3f}" if x < 1 else (f"{x:.2f}" if x < 10 else f"{x:.1f}")


def table(runs, hw, threads_list, gpu=False):
    def get(arm, b, th):
        key = f"{arm}_b{b}" + ("" if gpu else f"_t{th}")
        return runs.get(key)
    params = {a["arch"]: a["params"] for a in json.loads((RAW / "verify.json").read_text())["checkpoints"]}
    fl = json.loads((RAW / "flops.json").read_text())["flops"]
    rows, notes = [], []
    hdr = ["Row", "Parameters (M)", "GFLOPs per view", "Forwards per cell"]
    for b in (1, 8):
        for th in threads_list:
            hdr.append(f"s per cell, batch {b}" + ("" if gpu else f", {th} thr") + ": median (p90) [n]")
    hdr.append("Peak memory (MiB)" + (" GPU alloc b1 / b8" if gpu else " RSS b1 / b8, 16 thr"))
    for name, arm, arch, k in ARMS:
        mem_mult = 5 if arm in ("C3", "EPF") else 1
        r = [name, f"{params[arch] * mem_mult / 1e6:.1f}" + (" (5 x " + f"{params[arch] / 1e6:.1f})" if mem_mult > 1 else ""),
             f"{fl[arch]['GFLOPs_per_view']:.1f}", str(k)]
        for b in (1, 8):
            for th in threads_list:
                d = get(arm, b, th)
                if arm == "C1" and d is None:
                    d = get("UPF", b, th)
                if d:
                    t = d["timing"]
                    r.append(f"{fmt(t['cell_s_median'])} ({fmt(t['cell_s_p90'])}) [{t['timed_cells']}]")
                else:
                    u = get(UNIT[arch], b, th)
                    if u:
                        t = u["timing"]
                        r.append(f"{fmt(k * t['cell_s_median'])}* ({fmt(k * t['cell_s_p90'])}*)")
                    else:
                        r.append("not measured")
        mem = []
        for b in (1, 8):
            d = get(arm, b, 16) or (get("UPF", b, 16) if arm == "C1" else None)
            key = "gpu_peak_alloc_mib" if gpu else "cpu_peak_rss_mib"
            if d:
                mem.append(f"{d['timing'][key]:.0f}")
            else:
                mem.append("n.m.")   # memory only from a direct run of the arm itself
        r.append(" / ".join(mem))
        rows.append(r)
    lines = [f"### {hw}", "", "| " + " | ".join(hdr) + " |", "|" + "---|" * len(hdr)]
    lines += ["| " + " | ".join(r) + " |" for r in rows]
    return lines


def additivity(runs):
    lines = ["| Direct run | median s per cell | forwards x unit median (first unit run) | ratio | forwards x unit median "
             "(re-check, same host load) | ratio |", "|---|---|---|---|---|---|"]
    for key, j in sorted(runs.items()):
        t = j["timing"]
        if t["arm"] in ("UPF", "UHR", "C1") or key.endswith("_recheck"):
            continue
        th = j["env"]["threads"]
        u = runs.get(f"{'UPF' if t['arch'] == 'pf' else 'UHR'}_b{t['batch']}_t{th}")
        if not u:
            continue
        comp = t["forwards_per_cell"] * u["timing"]["cell_s_median"]
        r = runs.get(f"{'UPF' if t['arch'] == 'pf' else 'UHR'}_b1_t{th}_recheck")
        rc = t["forwards_per_cell"] * r["timing"]["cell_s_median"] * (t["batch"] == 1) if r else 0
        rtxt = f"{fmt(rc)} | {t['cell_s_median'] / rc:.3f}" if rc else "n.m. | "
        lines.append(f"| {key}{' (views batched)' if t['views_batched'] else ''} | {fmt(t['cell_s_median'])} | "
                     f"{fmt(comp)} | {t['cell_s_median'] / comp:.3f} | {rtxt} |")
    return lines


def main():
    cpu, gpu = load("cpu"), load("gpu")
    tsv = ["run\tdevice\tthreads\tarm\tbatch\tviews_batched\tforwards_per_cell\ttimed_cells\tcell_s_median\tcell_s_p90\t"
           "batch_s_median\tbatch_s_p90\tpeak_mib\tloadavg_start\tloadavg_end"]
    for src, runs in (("cpu", cpu), ("gpu", gpu)):
        for k, j in sorted(runs.items()):
            t, e = j["timing"], j["env"]
            pk = t.get("gpu_peak_alloc_mib", t.get("cpu_peak_rss_mib"))
            tsv.append("\t".join(map(str, [k, src, e["threads"], t["arm"], t["batch"], t["views_batched"],
                                           t["forwards_per_cell"], t["timed_cells"], round(t["cell_s_median"], 5),
                                           round(t["cell_s_p90"], 5), round(t["batch_s_median"], 5),
                                           round(t["batch_s_p90"], 5), round(pk or 0), e["loadavg"], e.get("loadavg_end")])))
    (RAW / "summary_timing.tsv").write_text("\n".join(tsv) + "\n")
    out = table(cpu, "gaint CPU: AMD Ryzen Threadripper 7960X (24 cores), fp32, torch threads 1 / 8 / 16", (1, 8, 16))
    out += ["", "#### Additivity check (gaint CPU)", ""] + additivity(cpu)
    if gpu:
        out += [""] + table(gpu, "cv02 GPU: one RTX A6000, fp32, TF32 off", (0,), gpu=True)
    else:
        out += ["", "### cv02 GPU: one RTX A6000", "", "Not measured yet (gpu/run_gpu_cv02.sh, ready, not run)."]
    (RAW / "tables.md").write_text("\n".join(out) + "\n")
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
