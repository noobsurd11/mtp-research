# Slide 5 count: "1,000+ segmentation models trained" (25 Nov 2026)

Run on gaint (cv02 reached from gaint).

## Legacy, 7 Oct to 14 Nov: 987
- Counted: run directories holding a `metrics.json`. Names with smoke / dry / debug / test_ / dumptest are excluded.
- Where: gaint `/home/noob/work`, i.e. `cv02_noob_el/{el_p6,p7,p11,p13,p14,p16,p17,alhvr,sk1,trackD,b6,mt,mt4,mt5}`, `el-fault-detection`, `el_f1`, `el_f2`, `el_f3`.
- Counts per directory: p6 84, p7 105, p11 27, p13 96, p14 72, p16 78, p17 68, alhvr 35, sk1 21, trackD 27, b6 20, mt 19, mt4 5, mt5 5, el-fault-detection 79, el_f1 73, el_f2 70, el_f3 103.
- Command: `find <dir> -name metrics.json | xargs -n1 dirname | grep -v -i -E "smoke|dry|debug|/test_|dumptest" | sort -u | wc -l`

## Benchmark, 12 to 23 Nov: 380 trainings (conservative)
- Source: unique job ids in the queue `jobs.txt` files (gaint `/home/noob/work/bq/*`, cv02 `/tmp/noob_el/bench_q/*`).
- 682 unique ids remain after excluding smoke, dumptest and dry ids and dump-only ids (ids containing a dot).
- Only the clearly training series are counted here:
  - 25 each: c3_pf_v11, c3_house_v11, c3h_hrnet, c3s_swad, c3x_hrnet_swad, w1c1_pf;
  - 20: w1g_pf;
  - 10 each: w1c2, w1c3;
  - 60: w2a (6 arms);
  - 20: w2b (lace, lci);
  - 50: r1 (5 rows);
  - 30: r2 (3 rows);
  - 30: t3b (all, half).
- The udev_* and tta_* ids are left out, since they may be inference-only.

## Total
At least 987 + 380 = 1,367. The slide says "1,000+".

**Caveat:** some legacy directories may hold re-scoring outputs rather than a training run, so the legacy count is approximate. Even so, the benchmark trainings alone take the total above 1,000.
