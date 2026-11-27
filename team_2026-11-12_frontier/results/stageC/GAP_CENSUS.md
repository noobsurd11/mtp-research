# gap_census: where the missed crack pixels of PF are (T14 arm 1)

Builder T14-CPU, 15 Nov 2026. Spec: `cards/T14_promote_spec.md` section 1 (P117). Tags: E = measured here, S = judgement, R = card.
Code: branch `bench_udev` (worktree `/home/noob/work/bench_wt_udev`), `bench/gap_census.py`, `scripts/bench_gap_census.py`, `tests/test_gap_census.py`. Tool outputs: `/home/noob/work/bench_reads/stageC/gap_census/`.

## 1. Reading rule and fixed parameters (written 15 Nov 18:35 IST, before any code ran on a dump)

Copied from the card (section 1.3), not changed:
- bound_gap >= 0.013 with its interval above 0.008, on W1-G and again on W1-C1: continuity arms have room. Arm 4's (`trace_crack`) first gate opens.
- bound_gap < 0.013 on both: a perfect gap-closing loss cannot move relR@2 by M. `trace_crack` is parked without a build. The lead is told that `clce_crack` (primary relR@2 at OP-W), `scnp_cedice` and `coletra_crack` share that ceiling: their primaries can then move only through whole missed cracks or ends, which is not their stated mechanism. `cc_dicece_crack` is read against B_small + B_whole instead.
- The machines disagree: the lead decides.
- It orders arms and closes none.

How I apply the literal text (fixed now, S):
- "interval above 0.008" = the lower end of the 95% two-stage group-bootstrap interval of bound_gap is > 0.008.
- A machine "has room" only if bound_gap >= 0.013 AND its lower end > 0.008. A machine is "below" if bound_gap < 0.013. A machine with bound_gap >= 0.013 but lower end <= 0.008 is "unclear".
- Outcome: room on both -> OPEN; below on both -> CEILING (park `trace_crack`); any other combination (room / below, or any "unclear") -> LEAD DECIDES. Nothing else is read as a decision.
- Variants read: 1 (this parameter set). Explore on W1-G, confirm unchanged on W1-C1 (G19).

Fixed parameters (card section 1.2; where the card leaves a choice, my choice is stated):
- Inputs: PF dumps (`pred`, `p_crack`) of the cv5v2 held-out folds. W1-G = `house_r34_unetpp_pf_v11` seeds 5 to 8 (20 runs, gaint); W1-C1 = the same card, seeds 5 to 9 (25 runs, cv02, relayed). Ground truth: the label set the cv5v2 sets resolve to (`bench/sets.py`: v1.1 masks with ignore 255; ignore px are not scored), 532 pool cells. Dumps are read through `bench/w1read.discover` (manifest md5s verified, sealed sets refused, cell list = the set's list).
- Per cell: k = not ignore; g = (gt == 14) & k; p = (pred == 14) & k; dp = EDT of ~p (inf if p is empty); covered = dp <= 2; miss = g & (dp > 2). This is exactly the missed count of `crack_rel2` in `m0core.cell_stats` (g.sum() - (dp[g] <= 2).sum()).
- GT components: 8-connected (`m0core.S8`). s < 20 -> all missed px to B_small; s >= 20 and c == 0 -> B_whole; s >= 20 and c > 0 -> each 8-connected run R of (C & miss): pieces = 8-connected components of C minus R; n_cov = pieces with at least one covered px; n_cov >= 2 -> B_gap, else B_end.
- pmax of a gap run = max p_crack over keep px within Euclidean distance 2 of R (R included). bound_gap_soft counts B_gap px of runs with pmax >= 0.01.
- frag = (sum over GT components with c > 0 of the number of distinct 8-connected predicted components with at least one px within 2 px of the component) / (number of such GT components). Printed over all such components (the card's definition) and over those with s >= 20. Mechanism log only.
- Pooling: counts are summed over all cells and all seeds of a machine; bound_gap = |B_gap| / |g| with |g| summed the same way (|g| is the same for every seed, so this equals the mean over seeds of the per-seed bound_gap); shares = bucket px / missed px, summed the same way.
- Interval: two-stage group bootstrap as `crossfit_op.boot_pair` for one arm: (a) the 330 module groups of `cv5v2_groups.tsv` with replacement, (b) per fold one seed drawn uniformly from the machine's seeds; statistic on the drawn, weighted counts; 2,000 draws, `random.Random(0)`; 2.5 and 97.5 percentiles. Per source (ARTS, BMRK, CFVS, CSIR; SDLE printed without decision weight): the same over that source's cells and groups. Per seed: point values and a one-stage group interval (groups only).
- Known limits (card 1.4, stated beside the result): a dotted label makes two GT components, and a prediction bridging it is neither missed nor a gap (only frag sees it); the 2 px tolerance hides gaps up to 4 px between predicted segments.

## 2. Result (written 15 Nov 18:50 IST, after the runs; section 1 unchanged, md5 of the rule-only file 1b022849)

Runs (E): code bench_udev 1a7b4f2 (tool md5 3ddfa643, module cf918ccf); runner `bench_reads/stageC/gap_census/run_gc.sh`, 18:36 to 18:38 IST, rc 0 both, CPU only. 532 cells, GT crack px 307,546 per seed (= the v1.1 scored crack px of the pool). Outputs `w1g_pf/census.{txt,json}` (md5 8778d5df, dd5900d0) and `w1c1_pf/census.{txt,json}` (a75a650a, 8120c0b9). Unit tests 9 of 9 (bucket sum = `crack_rel2` missed count of `bench_score` on 20 real cells, exactly).

### 2.1 Outcome under the rule: **OPEN** (room on both machines)

| | W1-G (gaint, PF s5-8, 20 runs) | W1-C1 (cv02, PF s5-9, 25 runs) |
|---|---|---|
| relR@2 (check: card 0.799) | 0.7985 [0.7517, 0.8385] | 0.7993 [0.7544, 0.8378] |
| **bound_gap** = B_gap / GT px | **0.0573 [0.0371, 0.0784]** | **0.0559 [0.0364, 0.0787]** |
| bound_gap_soft (pmax >= 0.01) | 0.0571 [0.0370, 0.0781] | 0.0558 [0.0362, 0.0787] |
| machine verdict (>= 0.013, lower end > 0.008) | room | room |

Both machines: bound_gap is 4.3 to 4.4 times the 0.013 threshold and the lower ends (0.036, 0.037) are far above 0.008. Every seed alone: 0.055 to 0.059 (gaint), 0.053 to 0.061 (cv02).

### 2.2 The four buckets (share of missed px, and as a share of GT crack px)

| Bucket | gaint share of miss | cv02 share of miss | gaint / GT px | cv02 / GT px |
|---|---|---|---|---|
| B_small (components < 20 px) | 0.0095 [0.0047, 0.0173] | 0.0096 [0.0048, 0.0173] | 0.0019 [0.0010, 0.0031] | 0.0019 [0.0011, 0.0031] |
| B_whole (>= 20 px, nothing covered) | 0.1734 [0.1036, 0.2805] | 0.2044 [0.1274, 0.3098] | 0.0349 [0.0190, 0.0608] | 0.0410 [0.0235, 0.0682] |
| B_gap (interior gaps of found cracks) | 0.2846 [0.2097, 0.3490] | 0.2785 [0.2016, 0.3604] | 0.0573 [0.0371, 0.0784] | 0.0559 [0.0364, 0.0787] |
| B_end (ends and branch tips not reached) | 0.5324 [0.4462, 0.6078] | 0.5074 [0.4082, 0.5896] | 0.1073 [0.0868, 0.1313] | 0.1019 [0.0798, 0.1254] |

- Whole missed components of at least 20 px: 0.108 [0.077, 0.149] (gaint) and 0.115 [0.082, 0.158] (cv02) of all such components (E).
- frag (predicted pieces per GT component with c > 0): 1.52 [1.38, 1.68] / 1.53 [1.39, 1.69]; for components >= 20 px 1.56 / 1.57.
- Per source, bound_gap gaint / cv02 (descriptive; intervals wide): ARTS 0.024 / 0.024, BMRK 0.054 / 0.061, CFVS 0.058 / 0.057, CSIR 0.065 / 0.055, SDLE 0 / 0. ARTS loses most px as whole missed cracks (share 0.48 / 0.49 of its miss); CFVS and BMRK mostly at ends; CSIR splits between whole (0.40 / 0.44) and ends.
- Per fold (point): fold 2 is highest (bound_gap 0.100 / 0.101), fold 0 lowest (0.023 / 0.024).

### 2.3 What sits inside B_gap (descriptive prints beside the rule; not rule inputs; `conc/conc.out`, `runlen.out`, `longrun.out`)
- **Run length (E).** Half of the gap runs are 14 to 15 px or shorter, but long runs hold the px: runs of at least 100 px hold 0.62 (gaint) / 0.59 (cv02) of B_gap px. B_gap from runs of at most 4 px is 0.0006, at most 16 px 0.0050, at most 32 px 0.0108 / 0.0107, at most 64 px 0.0178 / 0.0180, under 100 px 0.022 / 0.023.
- **Where (E).** 122 (gaint) / 141 (cv02) cells hold any gap px; the top 3 module groups hold 0.38 / 0.37 of B_gap px; bound_gap without them 0.041 / 0.041. The longest runs (670 to 1,400 px) lie in large crack networks of CFVS, CSIR and BMRK cells, for example a 1,745 px component with 88 covered px in 5 pieces.
- **pmax (E).** 1,349 of 1,505 gap runs (gaint) have pmax in [0.1, 0.5); no run reaches 0.5. S: pmax is a weak filter here, because px within 2 px of a run's two ends lie 1 to 2 px from the found segments, where p_crack is raised anyway; that is why bound_gap_soft is nearly bound_gap. I did not change the definition.

### 2.4 Limits (card 1.4, stated beside the result)
- A dotted label makes two GT components; a prediction bridging it is neither missed nor a gap (frag sees only some of it).
- The 2 px tolerance hides gaps of up to 4 px between predicted segments; those never enter miss. A topology gain on such gaps is invisible to relR@2.
- bound_gap is an upper bound: relR@2 gain if every interior gap were closed at no cost and nothing else changed.
- M covers seed noise, not the choice of folds; numbers are "on cv5v2 as built" (PROTOCOL_v0.2 11 items 4 and 9).

### 2.5 What it implies for the named arms (S, except where marked)
- **`trace_crack`:** gate (a) of card 4.3 **opens** on both machines. Gates (b) alt-route census, (c) the `skr01_pf_v11` row read (rows 2, cv02, running) and (d) the equations from the PDF are still owed; nothing is built. Caution for whoever builds it: 0.6 of the room is in runs of at least 100 px inside crack networks, and runs of at most 32 px hold only 0.011 (under M). TRACE acts on a 3 x 3 window around carrier px; whether such a term closes 100 px breaks is not shown by this census. The card's expectation (relR@2 at OP-W 0.000 to +0.015) does not rise because of this read.
- **`clce_crack`, `scnp_cedice`, `coletra_crack`:** the ceiling branch of the rule does not apply; their stated mechanism (continuity) has room above M on relR@2 in principle (0.056). The larger bucket is B_end (0.10 to 0.11 of GT px): a loss that extends found cracks along their own direction has about twice the room of one that only bridges gaps.
- **`cc_dicece_crack`:** under OPEN the rule leaves its read as planned (crack component recall with component precision). For reference: B_small + B_whole = 0.037 [0.021, 0.063] (gaint) / 0.043 [0.026, 0.070] (cv02) of GT px, of which components under 20 px are only 0.0019, so small-component recall carries almost no relR@2 room; 11% of components >= 20 px are missed whole, which its own primary (component recall) counts.
- The census orders arms and closes none. Variants read: 1 (explored on W1-G, confirmed unchanged on W1-C1).
