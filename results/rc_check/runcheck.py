import sys, os, re, json, glob
import torch
base = sys.argv[1]
runs = [f"p13_A_5pct_s{i}" for i in (3,4)] + [f"p13_Cs_5pct_s{i}" for i in range(3)] + [f"p13_CsM_5pct_s{i}" for i in range(5)] + \
       [f"p13_BsM_5pct_s{i}" for i in range(5)] + [f"p17_BsD_5pct_s{i}" for i in range(5)] + \
       [f"p18_BsM_10pct_s{i}" for i in range(3)] + [f"p18_BsM_20pct_s{i}" for i in range(5)]
for r in runs:
    cands = glob.glob(f"{base}/el_p1[378]/experiments/{r}")
    if not cands:
        print(r, "MISSING DIR"); continue
    d = cands[0]
    logs = [p for p in glob.glob(d + "/*.log") + glob.glob(d + ".stdout") if os.path.isfile(p)]
    last = None
    for p in logs:
        for m in re.finditer(r"step (\d+)/(\d+)", open(p, errors="ignore").read()):
            last = (int(m.group(1)), int(m.group(2)))
    test_line = any("TEST (final weights, step 20000)" in open(p, errors="ignore").read() for p in logs)
    ck = d + "/checkpoints/latest.pth"
    st = None
    if os.path.exists(ck):
        try: st = torch.load(ck, map_location="cpu", weights_only=False).get("step")
        except Exception as e: st = f"ERR {e}"
    mj = d + "/metrics.json"
    ms = None
    if os.path.exists(mj):
        m = json.load(open(mj)); ms = (m.get("test_final") or {}).get("step")
    print(f"{r:20s} {os.path.relpath(d, base):35s} last_log_step={last} TEST_final_line={test_line} latest.pth_step={st} metrics_test_final_step={ms}")
