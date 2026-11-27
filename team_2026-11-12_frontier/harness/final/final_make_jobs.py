"""final package: jobs.txt of the ONE cv02 queue `fin` (FINAL_RULE.md; LAUNCH_REQUEST_final.md section 3). 85 lines, cq.sh
format of F (821dfad; the two job kinds of 491e460). Nothing else; no sealed set can be named (a dump-only job's set is
the held-out set of its cv5v3 root; the full-pool root has no held-out set).

Usage: python final_make_jobs.py <out jobs.txt>       (refuses an existing file and any other argument)

Order (one queue, lane rule v2, LPG 1; MAXC 12 lets dump-only jobs run beside our trainings by the reviewed dump rule):
  1.  8 full-pool trainings: fin_hrnet_swad_v11_pool_s5..s9, fin_pf_v11_pool_s5..s7 (the long runs start first)
  2. 75 dump-only D4 jobs (no training): CS_D4 (swad, 25), PF_D4 (model, 25), CB_D4 (swad_bn, 25); each seed 5..9, fold 0..4
  3.  2 full-pool trainings: fin_pf_v11_pool_s8, s9 (take the first GPU without a lane once the dumps are dispatched)
Lines:
  full-pool candidate  fin_hrnet_swad_v11_pool_s<s>|bench/methods/hrnet_w18_unetpp_swad_const_pf_v11.yaml|<s>|DF|0|11510|6200|0||swad
  full-pool PF         fin_pf_v11_pool_s<s>|bench/methods/house_r34_unetpp_pf_v11.yaml|<s>|DF|0|9000|5262|0|
  CS_D4  c3x_hrnet_swad_v11_f<k>_s<s>.swad.tta_d4|<c3x card>|<s>|V3_f<k>|<k>|11510|6200|0|--dumpof XB/experiments/c3x_hrnet_swad_v11_f<k>_s<s> --key swad --tta d4
  PF_D4  c3_pf_v11_f<k>_s<s>.tta_d4|<PF card>|<s>|V3_f<k>|<k>|9000|6200|0|--dumpof PB/experiments/c3_pf_v11_f<k>_s<s> --key model --tta d4
  CB_D4  c3x_hrnet_swad_v11_f<k>_s<s>.swad_bn.tta_d4|<c3x card>|<s>|V3_f<k>|<k>|11510|6200|0|--dumpof XB/experiments/c3x_hrnet_swad_v11_f<k>_s<s> --key swad_bn --tta d4
  DF = /tmp/noob_el/bench_data_fin/roots/pool532_v11 (cq.sh DATA_F default); V3_f<k> = /tmp/noob_el/bench_data_v3b/roots/cv5v3_v11_f<k>;
  XB = /tmp/noob_el/bench_03375d4 (c3x deploy), PB = /tmp/noob_el/bench_89b9ea5 (c3base deploy, c3_pf_v11 runs).
Values:
  gate 11510 = the c3x job gate (c3x smoke RULE line; cv02 peak of the c3x runs 9,386 MiB, E gpumem logs); 9000 = PF card gate
    (cv02 PF peak 5,740 MiB). cq.sh refuses a gate below the card's. A dump-only job uses the gate for its strict-lane look.
  dump gate 6200 on every dump-only line: cv02 plain-dump peaks 3,944 (c3x) and 3,212 MiB (PF) (E gpumem logs); D4 adds two
    (8, 24, 512, 512) float32 tensors (about 0.4 GB) on the GPU; 6200 = the reviewed HRNet dump gate. On the full-pool
    lines the dump gate is unused (no dump) and kept at the card's usual value.
  logp 0 everywhere (FINAL_RULE section 1: no ensemble read in this package).
  10th field 'swad' on the candidate's full-pool lines: slim.pth keeps swad_bn (card weights_key) and swad (the final readout).
Run ids: the dump-only job name is the dump's run id (cq.sh: --run-id <name>); '<run>.<key>.tta_d4' (and '<run>.tta_d4' for
  the PF key model) = bench_infer's own default run id for --weights-key / --tta, so the names say what the dump is.
Relay patterns: the dumps are written in the F deploy (B = /tmp/noob_el/bench_<F 7 hex>), whose runs/ no other relay reads.
"""
import hashlib
import re
import sys
from pathlib import Path

DF = "/tmp/noob_el/bench_data_fin/roots/pool532_v11"
V3 = "/tmp/noob_el/bench_data_v3b/roots/cv5v3_v11_f{k}"
XB, PB = "/tmp/noob_el/bench_03375d4", "/tmp/noob_el/bench_89b9ea5"
CX = "bench/methods/hrnet_w18_unetpp_swad_const_pf_v11.yaml"
CP = "bench/methods/house_r34_unetpp_pf_v11.yaml"
SEEDS, FOLDS = (5, 6, 7, 8, 9), (0, 1, 2, 3, 4)
GX, GP, DGX, DGP, DGT = 11510, 9000, 6200, 5262, 6200


def pool_x(s): return f"fin_hrnet_swad_v11_pool_s{s}|{CX}|{s}|{DF}|0|{GX}|{DGX}|0||swad"
def pool_p(s): return f"fin_pf_v11_pool_s{s}|{CP}|{s}|{DF}|0|{GP}|{DGP}|0|"


def donly(arm, k, s):
    if arm == "PF_D4":
        src = f"c3_pf_v11_f{k}_s{s}"
        return f"{src}.tta_d4|{CP}|{s}|{V3.format(k=k)}|{k}|{GP}|{DGT}|0|--dumpof {PB}/experiments/{src} --key model --tta d4"
    src, key = f"c3x_hrnet_swad_v11_f{k}_s{s}", {"CS_D4": "swad", "CB_D4": "swad_bn"}[arm]
    return f"{src}.{key}.tta_d4|{CX}|{s}|{V3.format(k=k)}|{k}|{GX}|{DGT}|0|--dumpof {XB}/experiments/{src} --key {key} --tta d4"


def build() -> list[str]:
    L = [pool_x(s) for s in SEEDS] + [pool_p(s) for s in (5, 6, 7)]
    L += [donly(arm, k, s) for arm in ("CS_D4", "PF_D4", "CB_D4") for s in SEEDS for k in FOLDS]
    L += [pool_p(s) for s in (8, 9)]
    return L


def check(L: list[str]) -> None:
    names = [ln.split("|", 1)[0] for ln in L]
    assert len(L) == 85 and len(set(names)) == 85, "85 distinct jobs"
    rx_pool = re.compile(r"^fin_(hrnet_swad|pf)_v11_pool_s([5-9])$")
    rx_d = re.compile(r"^(c3x_hrnet_swad_v11|c3_pf_v11)_f([0-4])_s([5-9])\.((swad|swad_bn)\.)?tta_d4$")
    n_pool = n_d = 0
    for ln, n in zip(L, names):
        f = ln.split("|")
        assert all(ch.isalnum() or ch in "_.|/ -" for ch in ln) and "|" not in "".join(f[9:]), ln
        m = rx_pool.match(n)
        if m:
            n_pool += 1
            x = m.group(1) == "hrnet_swad"
            assert f[1] == (CX if x else CP) and f[2] == m.group(2) and f[3] == DF and f[4] == "0" and f[7] == "0" and f[8] == "", ln
            assert (f[5], f[6]) == ((str(GX), str(DGX)) if x else (str(GP), str(DGP))), ln
            assert (len(f) == 10 and f[9] == "swad") if x else len(f) == 9, ln
            continue
        m = rx_d.match(n)
        assert m and len(f) == 9, f"not a pool or dump-only line: {ln}"
        n_d += 1
        x, k, s, key = m.group(1) == "c3x_hrnet_swad_v11", m.group(2), m.group(3), m.group(5) or "model"
        src = f"{m.group(1)}_f{k}_s{s}"
        assert x == (key != "model"), ln
        assert f[1] == (CX if x else CP) and f[2] == s and f[3] == V3.format(k=k) and f[4] == k, ln
        assert f[5] == str(GX if x else GP) and f[6] == str(DGT) and f[7] == "0", ln
        assert f[8] == f"--dumpof {XB if x else PB}/experiments/{src} --key {key} --tta d4", ln
        assert n.startswith(src + "."), ln
    assert n_pool == 10 and n_d == 75, (n_pool, n_d)
    assert not any(t in ln for ln in L for t in ("test50", "e1_106", "--opening", "--logp", "ext117", "legacy_test")), "sealed"
    for arm, key in (("CS_D4", ".swad.tta_d4"), ("CB_D4", ".swad_bn.tta_d4")):
        assert sum(n.startswith("c3x_") and n.endswith(key) for n in names) == 25, arm
    assert sum(n.startswith("c3_pf_v11_") for n in names) == 25
    assert names[:8] == [f"fin_hrnet_swad_v11_pool_s{s}" for s in SEEDS] + [f"fin_pf_v11_pool_s{s}" for s in (5, 6, 7)]
    assert names[-2:] == ["fin_pf_v11_pool_s8", "fin_pf_v11_pool_s9"]


def main(argv) -> int:
    if len(argv) != 1 or argv[0].startswith("-"):
        sys.exit(__doc__)
    out = Path(argv[0])
    if out.exists():
        sys.exit(f"REFUSED: {out} exists")
    L = build()
    check(L)
    text = "".join(ln + "\n" for ln in L)
    out.write_text(text)
    print(f"fin list: {len(L)} lines = 10 full-pool trainings (candidate s5-9, PF s5-9) + 75 dump-only D4 jobs "
          f"(CS_D4, PF_D4, CB_D4 x 25); logp 0; no sealed set")
    print(f"wrote {out} md5 {hashlib.md5(text.encode()).hexdigest()}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
