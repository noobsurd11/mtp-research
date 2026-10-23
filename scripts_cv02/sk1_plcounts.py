import csv, re, glob
K = ["aux_pl_crack", "aux_pl_inactive", "aux_keep_u", "head_drift", "main_pred_crack", "aux_pred_crack", "gt_crack",
     "main_pred_inactive", "aux_pred_inactive", "gt_inactive"]
print("| run | step | conf_frac (500-step window) | main PL crack / unl px | main PL inactive / unl px | " + " | ".join(K) + " |")
print("|---" * (5 + len(K)) + "|")
for r in sorted(glob.glob("sk1_Bs*_s[0-9]")):
    rows = {int(x["step"]): x for x in csv.DictReader(open(r + "/pseudo_labels.csv"))}
    log = {}
    for ln in open(r + ".stdout"):
        m = re.search(r"step (\d+)/20000\s+(.*)", ln)
        if m:
            log[int(m.group(1))] = dict(kv.split("=", 1) for kv in m.group(2).split() if "=" in kv)
    for s in (4000, 20000):
        x, l = rows[s], log.get(s, {})
        vals = [l.get(k, "-") for k in K]
        print(f"| {r} | {s} | {float(x['confident_frac']):.3f} | {float(x['unl_share_14']):.5f} | {float(x['unl_share_11']):.5f} | " + " | ".join(vals) + " |")
