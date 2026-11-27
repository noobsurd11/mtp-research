"""fin2 (incident of 21 Nov 2026): jobs.txt of the cv02 queue fin2 = the 10 full-pool runs of fin, each RESUMED from its
step-18000 checkpoints/latest.pth under F2 (9330f8b; cq.sh job kind '--resume'). Same card, seed, root, gates and slim
keys as the fin lines (harness/final/final_make_jobs.py); the 9th field is '--resume'. The run dirs are copied from the F
deploy into the F2 deploy by final2_queue.sh resumecopy before arming (cq.sh refuses a resume line without them).

Usage: python final2_make_jobs.py <out jobs.txt>       (refuses an existing file and any other argument)
Lines:
  fin_hrnet_swad_v11_pool_s<s>|bench/methods/hrnet_w18_unetpp_swad_const_pf_v11.yaml|<s>|DF|0|11510|6200|0|--resume|swad
  fin_pf_v11_pool_s<s>|bench/methods/house_r34_unetpp_pf_v11.yaml|<s>|DF|0|9000|5262|0|--resume
Order: the 5 candidate runs (longer: 2,000 HRNet steps + BN re-estimate + final validation + test) first, then PF s5 to s9.
"""
import hashlib
import sys
from pathlib import Path

DF = "/tmp/noob_el/bench_data_fin/roots/pool532_v11"
CX = "bench/methods/hrnet_w18_unetpp_swad_const_pf_v11.yaml"
CP = "bench/methods/house_r34_unetpp_pf_v11.yaml"
SEEDS = (5, 6, 7, 8, 9)


def build() -> list[str]:
    return ([f"fin_hrnet_swad_v11_pool_s{s}|{CX}|{s}|{DF}|0|11510|6200|0|--resume|swad" for s in SEEDS]
            + [f"fin_pf_v11_pool_s{s}|{CP}|{s}|{DF}|0|9000|5262|0|--resume" for s in SEEDS])


def main(argv) -> int:
    if len(argv) != 1 or argv[0].startswith("-"):
        sys.exit(__doc__)
    out = Path(argv[0])
    if out.exists():
        sys.exit(f"REFUSED: {out} exists")
    L = build()
    fin = Path(__file__).resolve().parent.parent / "final" / "jobs" / "jobs_fin.txt"
    if fin.exists():   # same fields as fin's full-pool lines except the 9th ('' -> '--resume')
        old = {ln.split("|", 1)[0]: ln.split("|") for ln in fin.read_text().splitlines() if ln.startswith("fin_")}
        for ln in L:
            f = ln.split("|")
            o = old[f[0]]
            assert f[:8] == o[:8] and f[8] == "--resume" and o[8] == "" and f[9:] == o[9:], ln
        assert sorted(old) == sorted(ln.split("|", 1)[0] for ln in L)
    assert len(L) == 10 and len({ln.split("|", 1)[0] for ln in L}) == 10
    text = "".join(ln + "\n" for ln in L)
    out.write_text(text)
    print(f"fin2 list: {len(L)} resume lines (candidate s5-9, PF s5-9) = fin's full-pool lines with 9th field '--resume'")
    print(f"wrote {out} md5 {hashlib.md5(text.encode()).hexdigest()}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
