# label_version_strata: crack recall on stable px against px the label revision added (T14 arm 5)

Builder T14-CPU, 15 Nov 2026. Spec: `cards/T14_promote_spec.md` section 5 (P184). Tags: E = measured here, S = judgement, R = card.
Code: branch `bench_udev` (worktree `/home/noob/work/bench_wt_udev`), `bench/label_strata.py`, `scripts/bench_label_strata.py`, `tests/test_label_strata.py`. Tool outputs: `/home/noob/work/bench_reads/stageC/label_version_strata/`.

**This read decides nothing.** It is a descriptive table for the label-noise section of the protocol. No arm is promoted, parked or ordered by it, except the one fixed sentence below about the argument "models miss what annotators miss".

## 1. Fixed computation and reading sentences (written 15 Nov 18:35 IST, before any code ran on a dump)

From the card (section 5.2, 5.3), with my choices stated:
- Cells: the 532 pool stems only (the cv5v2 held-out lists), asserted free of `forbidden_v1.txt` and of sealed stems (fail closed).
- Label versions: o = 2021 crack (`data/labeled/masks_coded`, dataset_20211104) & keep; g = v1.1 crack (the cv5v2 scoring masks) & keep; keep = not v1.1 ignore. d_o = EDT to o, d_g = EDT to g, dp = EDT to predicted crack (pred == 14) & keep.
- S (stable) = g & (d_o <= 1); A (added) = g & (d_o > 2); border band B = g & (1 < d_o <= 2), printed, in neither. D (deleted) = o & (d_g > 2).
- recall_X = |X & (dp <= 2)| / |X| for X in {S, A, B}; also the share of X with p_crack < 0.001.
- False px F = pred crack & keep & (d_g > 2); contested share = |F & (EDT to D <= 2)| / |F|.
- Reads: all crack cells (v1.1 crack px > 0 in keep); changed cells only = cells where the 2021 and v1.1 crack px sets (in keep) differ and both have crack (same cells for S and A); per source. Pooling over cells and seeds as in GAP_CENSUS.md section 1. Interval: two-stage group bootstrap (330 groups, then one seed per fold; 2,000 draws, `random.Random(0)`) on recall_A - recall_S, and on recall_S, recall_A alone.
- Dumps: PF W1-G (seeds 5 to 8) and W1-C1 (seeds 5 to 9); HOUSE W1-C2 (seeds 5, 6) printed beside as description where its dumps exist.
- Variants read: 1.

Reading sentences, fixed now:
- If the interval of recall_A - recall_S lies wholly below 0: "recall on px the revision added is lower by x [lo, hi]". Otherwise: "not separated".
- If recall_A - recall_S is above -0.05 (point value, PF, all crack cells, W1-G and W1-C1 each): the argument "models miss what annotators miss" is not supported and is not used for the missing-segment arms (`oof_selective_ignore`, `oof_add`). If it is at or below -0.05 on a machine, the sentence says so for that machine, and the argument is "consistent with" that read only (no arm is promoted by it).
- Risks printed with the table: whether the revision was made with model help is not documented (unverified), so A may be biased toward what a model finds; about 90 changed cells, fold 3 heavy, so per-source values are descriptive.

## 2. Result (written 15 Nov 18:55 IST, after the runs; section 1 unchanged, md5 of the rule-only file 13089a09)

Runs (E): code bench_udev 24aa039 (tool md5 f3c3f1f8, module cd026808); runner `bench_reads/stageC/label_version_strata/run_ls.sh`, 18:40 to 18:41 IST, rc 0 for all three, CPU only. Outputs `w1g_pf/strata.{txt,json}` (d72a0d2a, 0111a961), `w1c1_pf/` (14442c6d, 8d6fd510), `w1c2_house/` (42791b9d, a8323b5d). Unit tests 5 of 5 (identical versions give A and D empty and recall_S = relR@2 of `bench_score`; sealed and non-pool stems raise). Cross-check: share of GT crack px with p_crack < 0.001 on W1-G f0 s5 = the first p-band of `m0core.cell_stats` (0.2584 both).

### 2.1 Strata sizes (label-only, the same for every run)
- Cells: 229 pool cells with v1.1 crack (532 minus the 303 crack-free), 224 with 2021 crack, 222 with both. **Changed cells (both versions crack, crack px differ): 82**; unchanged 147; 7 cells have crack only in v1.1 (their px are all in A), 2 only in 2021. Changed cells per fold 11 / 20 / 17 / 15 / 19. (The card quotes 142 unchanged and 90 changed of 234 from an earlier count with another cell base; I did not reconcile it.)
- Px over the 229 cells: |g| 307,546 (v1.1), |o| 259,958 (2021); **S 293,554 (95.5%), A 7,028 (2.3%), border band 6,964 (2.3%)**, D 5,495. E: the revision added few px farther than 2 px from a 2021 label; most of the +18% crack px lie within 1 px of the old lines (joined dots, wider lines), as the handbook already says.

### 2.2 Recall on stable and on added px (relR@2 counting; two-stage interval)

| Read | Model, machine | recall_S | recall_A | recall_A - recall_S | border recall | p < 0.001 on S / A | contested share of false px |
|---|---|---|---|---|---|---|---|
| all 229 crack cells | PF, gaint (s5-8) | 0.7970 [0.7480, 0.8362] | 0.7851 [0.5983, 0.8810] | **-0.012 [-0.203, +0.091]** | 0.874 | 0.316 / 0.311 | 0.032 [0.004, 0.093] |
| all 229 crack cells | PF, cv02 (s5-9) | 0.7975 [0.7494, 0.8381] | 0.7923 [0.5818, 0.8884] | **-0.005 [-0.216, +0.100]** | 0.882 | 0.317 / 0.309 | 0.036 [0.004, 0.090] |
| all 229 crack cells | HOUSE, cv02 (s5-6), beside | 0.8050 [0.7577, 0.8426] | 0.7929 [0.5812, 0.8915] | -0.012 [-0.223, +0.095] | 0.892 | 0.253 / 0.249 | 0.023 [0.003, 0.060] |
| 82 changed cells | PF, gaint | 0.8103 [0.7558, 0.8590] | 0.8306 [0.6124, 0.9175] | +0.020 [-0.180, +0.116] | 0.874 | 0.306 / 0.280 | 0.071 [0.008, 0.171] |
| 82 changed cells | PF, cv02 | 0.8105 [0.7572, 0.8582] | 0.8457 [0.6407, 0.9311] | +0.035 [-0.149, +0.126] | 0.882 | 0.306 / 0.274 | 0.078 [0.010, 0.168] |
| 82 changed cells | HOUSE, cv02 | 0.8187 [0.7692, 0.8648] | 0.8485 [0.6108, 0.9359] | +0.030 [-0.190, +0.122] | 0.892 | 0.231 / 0.203 | 0.050 [0.008, 0.115] |

Per seed, PF, all crack cells (E): difference -0.031 to +0.002 (gaint), -0.019 to +0.003 (cv02).

Per source, all crack cells, recall_A - recall_S, PF gaint / cv02 (descriptive only; A holds 876 px in ARTS, 505 in BMRK, 4,140 in CFVS, 1,507 in CSIR):
- ARTS (47 cells): -0.377 [-0.688, -0.108] / -0.355 [-0.621, -0.085]
- BMRK (30): -0.266 [-0.721, +0.040] / -0.350 [-0.758, -0.030]
- CFVS (99): +0.083 [-0.005, +0.146] / +0.099 [+0.011, +0.156]
- CSIR (51): +0.057 [-0.707, +0.341] / +0.063 [-0.697, +0.341]
On the changed cells only, no source has an interval wholly off 0 (12 to 37 cells each).

### 2.3 Reading (sentences fixed in section 1)
- All crack cells, PF: **"not separated"** on both machines (gaint -0.012 [-0.203, +0.091]; cv02 -0.005 [-0.216, +0.100]). Changed cells: **"not separated"** on both.
- recall_A - recall_S is above -0.05 on both machines (PF): **the argument "models miss what annotators miss" is not supported** and is not used for the missing-segment arms (`oof_selective_ignore`, `oof_add`).
- S (not a decision): the pooled null hides opposite source patterns. In ARTS and BMRK the px the revision added are found much less often than stable px (about -0.3; ARTS wholly below 0 on both machines), in CFVS slightly more often. A is small (2.3% of crack px) and lies in few groups, so the pooled interval is wide (about 0.3 wide). Only 3 to 8% of the false crack px lie within 2 px of px the revision deleted, so deleted labels explain little of the false px.
- Risks: whether the revision was made with model help is not documented (unverified), so A may be biased toward what a model finds; 82 changed cells, so per-source values are descriptive. This read decides nothing; variants read: 1.
