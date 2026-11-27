"""Wave 2a gate, arm ema_wise_posthoc (LAUNCH_REQUEST_w2a.md section 8): the raw weights models['model'] of
w2a_ema_f<k>_s<s> must equal those of the W1-G run w1g_pf_v11_f<k>_s<s> bit for bit. No metric is computed.

For each of the 10 pairs: latest.pth of both runs (the file bench_infer.py dumps from) is loaded on the CPU; the two
state dicts are compared key by key on the raw bytes of every tensor (so NaN and -0.0 count as written), and one sha256
per state dict is taken over sorted keys (key name, dtype, shape, bytes). Per run: EQUAL or DIFFERENT; if different, the
keys that differ, how many elements, and the largest absolute difference.
Self-tests of the comparison (in memory, nothing written): a state dict against itself is EQUAL; against a copy with one
element moved by one float step it is DIFFERENT in exactly that key; PF fold 0 seed 5 against PF fold 0 seed 6 is DIFFERENT.
Also checks that the md5 of each latest.pth equals checkpoint_md5 in the manifests of the dumps made from it (where a
dump exists), so the compared weights are the dumped ones.

  CUDA_VISIBLE_DEVICES="" PYTHONDONTWRITEBYTECODE=1 nice -n 19 python gate_ema_hash.py --out <new folder>
"""
from __future__ import annotations

import argparse
import hashlib
import time

import numpy as np

import w2agate as g

EMA_KEYS = ["model", "ema_999", "ema_9998", "raw_bn", "ema_999_bn", "ema_9998_bn"]


def sd_hash(sd: dict) -> str:
    h = hashlib.sha256()
    for k in sorted(sd):
        a = sd[k].detach().cpu().contiguous().numpy()
        h.update(k.encode()); h.update(str(a.dtype).encode()); h.update(str(a.shape).encode()); h.update(a.tobytes())
    return h.hexdigest()


def compare(a: dict, b: dict) -> dict:
    """Key-by-key bit comparison of two state dicts."""
    only_a = sorted(set(a) - set(b)); only_b = sorted(set(b) - set(a))
    diff, max_abs, max_key, n_el = [], 0.0, None, 0
    for k in sorted(set(a) & set(b)):
        x, y = a[k].detach().cpu().contiguous().numpy(), b[k].detach().cpu().contiguous().numpy()
        if x.dtype != y.dtype or x.shape != y.shape:
            diff.append({"key": k, "why": f"dtype / shape {x.dtype}{x.shape} vs {y.dtype}{y.shape}"})
            continue
        if x.tobytes() == y.tobytes():
            continue
        d = np.abs(x.astype(np.float64) - y.astype(np.float64))
        nd = int((x.view(np.uint8).reshape(-1, x.itemsize) != y.view(np.uint8).reshape(-1, y.itemsize)).any(1).sum()) \
            if x.size else 0
        m = float(np.nanmax(d)) if d.size else 0.0
        diff.append({"key": k, "n_diff": nd, "n": int(x.size), "max_abs": m})
        n_el += nd
        if m >= max_abs:
            max_abs, max_key = m, k
    equal = not (only_a or only_b or diff)
    return {"equal": equal, "same_key_order": list(a) == list(b), "n_keys": len(set(a) | set(b)), "only_a": only_a,
            "only_b": only_b, "diff_keys": diff, "n_diff_keys": len(diff), "n_diff_elements": n_el,
            "max_abs": max_abs, "max_abs_key": max_key}


def selftest(R: g.Report, pf55: dict, pf56: dict) -> dict:
    import torch
    res = {}
    res["same"] = compare(pf55, pf55)["equal"] and sd_hash(pf55) == sd_hash(pf55)
    cp = {k: v.clone() for k, v in pf55.items()}
    k0 = "decoder.blocks.x_0_0.conv1.0.weight" if "decoder.blocks.x_0_0.conv1.0.weight" in cp else \
        next(k for k, v in cp.items() if v.is_floating_point() and v.dim() >= 2)
    flat = cp[k0].view(-1)
    flat[0] = torch.nextafter(flat[0], torch.tensor(float("inf")))
    c = compare(pf55, cp)
    res["one_step"] = (not c["equal"]) and c["n_diff_keys"] == 1 and c["diff_keys"][0]["key"] == k0 \
        and c["n_diff_elements"] == 1 and sd_hash(pf55) != sd_hash(cp)
    c2 = compare(pf55, pf56)
    res["other_seed"] = (not c2["equal"]) and sd_hash(pf55) != sd_hash(pf56)
    R.p(f"self-test: same dict EQUAL {res['same']}; one element moved by one float step in {k0} found "
        f"{res['one_step']} (max abs {c['max_abs']:.3g}); PF f0 s5 against PF f0 s6 DIFFERENT {res['other_seed']} "
        f"({c2['n_diff_keys']} of {c2['n_keys']} keys)")
    res["ok"] = all(res.values())
    return res


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    g.guard_env()
    out = g.new_out(a.out)
    R = g.Report(out, "gate_ema_hash")
    t0 = time.time()
    R.p("# gate_ema_hash: raw models['model'] of w2a_ema_f<k>_s<s> against w1g_pf_v11_f<k>_s<s> (latest.pth, step 20000)")
    R.p(f"started {time.strftime('%F %T')}; W1-G runs {g.EXP_PF}; wave 2a runs {g.EXP_W2A}")
    st55 = g.load_ckpt(g.pf_run(0, 5))["models"]["model"]
    st56 = g.load_ckpt(g.pf_run(0, 6))["models"]["model"]
    doc = {"selftest": selftest(R, st55, st56), "runs": {}}
    del st55, st56
    R.p("run\tverdict\tkeys\tkeys that differ\telements that differ\tlargest abs difference (key)\tsha256 PF\tsha256 ema raw"
        "\tckpt md5 = dump manifest (PF, ema)")
    n_equal = 0
    for k in g.FOLDS:
        for s in g.SEEDS:
            name = f"w2a_ema_f{k}_s{s}"
            pr, er = g.pf_run(k, s), g.w2a_run("ema", k, s)
            P, E = g.load_ckpt(pr), g.load_ckpt(er)
            assert list(P["models"]) == ["model"], list(P["models"])
            assert sorted(E["models"]) == sorted(EMA_KEYS), list(E["models"])
            c = compare(P["models"]["model"], E["models"]["model"])
            hp, he = sd_hash(P["models"]["model"]), sd_hash(E["models"]["model"])
            assert (hp == he) == c["equal"], "hash and key comparison disagree"
            mp, me = g.md5_file(pr / "checkpoints/latest.pth"), g.md5_file(er / "checkpoints/latest.pth")
            dp = g.manifest_ckpt_md5(g.DUMPS_PF / pr.name)
            de = {d.name: g.manifest_ckpt_md5(d) for d in sorted((g.DUMPS_W2A / "ema_wise_posthoc_pf_v11").glob(f"{name}*"))
                  if d.name == name or d.name.startswith(name + ".")}
            mok_p = None if dp is None else dp == mp
            mok_e = None if not de else all(v == me for v in de.values())
            by_part = {}
            for d in c["diff_keys"]:
                by_part[d["key"].split(".")[0]] = by_part.get(d["key"].split(".")[0], 0) + 1
            c.update({"sha256_pf": hp, "sha256_ema_raw": he, "ckpt_md5_pf": mp, "ckpt_md5_ema": me,
                      "pf_manifest_md5_equal": mok_p, "ema_manifests_md5_equal": mok_e, "ema_dumps_checked": sorted(de),
                      "diff_keys_by_part": by_part})
            doc["runs"][name] = c
            n_equal += c["equal"]
            R.p(f"{name}\t{'EQUAL' if c['equal'] else 'DIFFERENT'}\t{c['n_keys']}\t{c['n_diff_keys']}\t"
                f"{c['n_diff_elements']}\t{c['max_abs']:.3g} ({c['max_abs_key']})\t{hp[:16]}\t{he[:16]}\t"
                f"{mok_p}, {mok_e} ({len(de)} dumps)")
            if not c["equal"]:
                R.p(f"  {name}: keys that differ by part {by_part}; key order equal {c['same_key_order']}; only in PF "
                    f"{c['only_a'][:5]}; only in ema {c['only_b'][:5]}; first keys "
                    f"{[d['key'] for d in c['diff_keys'][:6]]}")
            del P, E
    ok_manifest = all(v["pf_manifest_md5_equal"] is not False and v["ema_manifests_md5_equal"] is not False
                      for v in doc["runs"].values())
    verdict = "PASS" if (n_equal == 10 and doc["selftest"]["ok"] and ok_manifest) else "FAIL"
    doc.update({"n_equal": n_equal, "n_runs": 10, "manifest_md5_ok": ok_manifest, "verdict": verdict,
                "seconds": round(time.time() - t0)})
    R.p(f"\nEQUAL {n_equal} of 10; self-test ok {doc['selftest']['ok']}; checkpoint md5 = dump manifests where dumps exist "
        f"{ok_manifest}")
    R.p(f"VERDICT gate_ema_hash {verdict} (rule: all 10 EQUAL bit for bit; section 8)")
    R.p(f"finished {time.strftime('%F %T')} ({doc['seconds']} s)")
    R.close(doc, verdict)


if __name__ == "__main__":
    main()
