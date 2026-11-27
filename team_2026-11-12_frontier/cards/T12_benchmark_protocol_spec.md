# T12 spec: protocol v0.2 changes and the CPU analyses that decide them (8 items)

Analyst T12, 13 Nov 2026. Tags: R = paper, E = our files, S = my judgement. Papers: `cards/T12_benchmark_protocol_family.md`. Ledger: `cards/ledger/T12.tsv`.
Nothing launched. No GPU, no server, no sealed data touched. Every item is `analysis_only` unless stated; none trains a model.

## 0. Summary for the lead

| # | Name | Papers | Problem | Primary (pre-declared) | Build h | GPU-h | Runs on | Priority |
|---|---|---|---|---|---|---|---|---|
| 1 | `aa_calibration` | P358, P501, P133, P271, P355, P357 | measurement | false-promotion rate of the screen rule over all A/A seed splits (crack relF1@2, OP-A) | 3 | 0 (optional split probe 5.5) | W1-C1 relayed dumps (part (d) on W1-G tonight) | 90 |
| 2 | `metric_validity_probe` | P439, P188, P134, P582, P601, P492 | measurement | z of a known real gain (2-seed ensemble vs single, at OP-W) per candidate crack metric, among metrics that pass the width probe | 4 | 0 | W1-G PF dumps with `logp` (tonight) | 85 |
| 3 | `rank_stability` | P578, P598, P595, P265, P133 | benchmark_row | median bootstrap Kendall tau of the method ranking per headline metric | 3 | 0 | W1-C sets + derived entries; re-run per wave | 70 |
| 4 | `tau_from_annotators` | P188, P601 | measurement | tau95 = 95th percentile of distances between two drawings of one crack | 1.5 | 0 | GT masks only (now) | 65 |
| 5 | `leakage_audit_v02` | P570, P579, P631, P443 | measurement | number of cross-set near-duplicate pairs not already in a group or forbidden list | 3 | 0 | images only, CPU | 55 |
| 6 | `t5_post_eval` | P617, P609, P263 (R only), P615 (T7's) | inactive / benchmark_row | per-cell inactive area fraction error (MAE, % of cell) | 3 | 0 | W1 dumps | 45 |
| 7 | `reporting_governance` | P570, P595, P545, P637, P439 | benchmark_row | none (text) | 3 | 0 | protocol text | 40 |
| 8 | `severity_external_elpvpower` | P263, P564 | benchmark_row | Spearman rho between module-summed predicted inactive fraction and relative power loss | 8 | about 1 (inference) | gated | 20 |

Totals: 28.5 build hours, 0 GPU-h for items 1 to 7 (5.5 optional in item 1), about 1 GPU-h for item 8 if its gate opens.

**First item and why (S).** `aa_calibration`: 3 build hours, and it sets the pass rule that about 20 wave-2 arms are judged by (WAVE2_REVIEW X1, X2). Each false promotion costs a 16.5 GPU-h confirmation; each false null loses a real gain. Harness support used (E): `scripts/bench_read_w1.py --aa` (one A/A split today), `bench/crossfit_op.py` `boot_pair`, `margins`, `fmetrics`, `point`; `bench/w1read.py` `discover`, `assemble`, `records` cache; `benchmark/splits/cv5v2_groups.tsv` (330 groups). It needs the 25 W1-C1 runs relayed to gaint; its part (d) (design effect) runs tonight on W1-G. If W1-C1 is late, item 2 runs first (it only needs W1-G).

**What I found in the existing bootstrap (E, `crossfit_op.py` l.278 to 325) that item 1 must check.** The point estimate is the mean over seeds of each seed's pooled metric, but each bootstrap draw uses ONE seed per fold and arm. So the bootstrap SE describes a one-seed-per-fold estimator, not the 2-seed mean it is attached to. My expectation (S): the seed part of the SE is overstated by up to about sqrt(2) at 2 seeds, the margin M is conservative, and real gains near M are missed. Item 1 measures this instead of assuming it.

**How these items differ from existing work (E, WAVE2_REVIEW 4, T10 spec, T7 spec).** `bench_read_w1.py --aa` computes M from one split ({5,6} vs {7,8}); item 1 enumerates all 15 splits and checks coverage. D0, src_calib and dti are arms on the dumps; items 2 and 3 judge the metrics and the ranking that those arms are read with. T10 A0(e) and T3 `oof_selective_ignore` produce label flags; item 3 only reuses them as a subset axis. T10 notes a second grouped split (P007); item 1's optional probe is that idea with a decision rule (run once, not twice). T7 P615 already set "module severity = worst cell"; item 6 adds what can be validated.

---

## 1. `aa_calibration`: does the screen rule hold its error rate?

- **Papers:** P358 (hierarchical bootstrap keeps nominal error on nested data; traditional tests above 45% false positives, R), P501 (naive CV intervals under-cover, R scout), P133 (data-split variance dominates; P(A>B), R full text), P271 (seed power analysis), P355 / P357 (CI choice and width). **Problem:** measurement. **Primary:** share of the 15 A/A splits that the screen rule would promote (delta >= M and CI low > 0), crack relF1@2 at OP-A. Secondary: the same for crack IoU, inactive IoU, mIoU-R13 at OP-A, OP-F, OP-W; the SD ratio r below.
- **Inputs (E):** W1-C1 dumps of `house_r34_unetpp_pf_v11`, cv5v2, folds 0 to 4, seeds 5 to 9 (25 runs, cv02, relayed). One machine only (`check_comparable`).
- **Code:** new `bench/aa.py` + `scripts/bench_aa.py` in the x3 layout. Pseudo-code:
  ```
  runs = w1read.discover(["PF=<relay>/elbench1/house_r34_unetpp_pf_v11:<C1 regex>"], labels="v11")
  arms, fold_of, stems, notes = w1read.assemble(runs, groups)          # arms["PF"] = {seed: [Run x5 folds]}
  recA = {seed: oof_records(...) at OP-A}; recF, recW likewise (crossfit_op.operating_points, baseline = PF itself)
  seeds = [5,6,7,8,9]
  splits2 = [(a, b) for a, b in disjoint unordered pairs of 2-seed subsets]           # 15
  splits1 = [({i}, {j}) for i < j]                                                   # 10
  for (A, B) in splits2 + splits1:
      bp = crossfit_op.boot_pair({s: rec[s] for s in A}, {s: rec[s] for s in B}, stems, fold_of, groups, n_boot=2000, seed=0)
      M = crossfit_op.margins(bp)          # the rule as it would be applied to an arm
      row = {k: (bp.delta, bp.se, bp.lo, bp.hi, promoted = delta >= M and lo > 0, excl0 = lo > 0 or hi < 0)}
  r[k] = sd(delta over splits2) / mean(se over splits2)       # empirical spread vs claimed SE; ~4 effective df (S)
  # (d) design effect, any 1 seed:  SE_flat (resample cells), SE_group (330 groups), SE_group+seed (as boot_pair)
  # (e) variance components: sigma2_seed = var over seeds of the pooled per-seed metric (5 values);
  #     V(k) fit a + b/k from the empirical A/A variances at k = 1 (10 splits) and k = 2 (15 splits);
  #     MDE(k) = 2.8 * sqrt(V(k)) for k in 2, 3, 5 (P271 rule, alpha 0.05 two-sided, power 0.8)
  ```
  Shapes: records are the m0 dicts; `_features` gives an (n_cells, 24*24 + 11) int64 matrix per seed. Switched on by running the script; nothing in the trainer changes.
- **Unit tests** (`tests/test_bench_aa.py`, synthetic records): (1) two arms that are the same seed dict give delta 0 and promotion False for every split; (2) 1,000 simulated A/A splits from i.i.d. per-cell noise (Poisson counts) give a CI-excludes-0 rate in 0.03 to 0.07; (3) the 15 split list has no repeated or overlapping pair.
- **Pre-check tonight (W1-G, 2 seeds; no A/A possible):** part (d) only. Reading: DEFF = (SE_group / SE_flat)^2 per headline metric. If DEFF < 1.2 for every metric, module grouping costs little power and P358's concern is small here; if > 2, any flat cell bootstrap in the protocol (L-test: cells are not grouped there) must be marked as anti-conservative wherever cells share modules (L-test twins).
- **Decision rules (fixed now):**
  - Promotion share <= 1 of 15 at every headline metric and r in [0.7, 1.5]: keep M = max(0.01, 2 x SE_AA).
  - r > 1.5 (bootstrap too narrow): M = max(0.01, 2 x SD of the 15 A/A deltas), and every arm CI is widened by r before the "CI low > 0" check.
  - r < 0.7 (bootstrap too wide, my expectation for the seed stage): replace the seed stage by drawing the seed SET (one draw per fold of a full k-seed mean, done by resampling seeds with replacement inside each arm and averaging) and re-run the 15 splits; adopt it only if the new r is in [0.7, 1.5] and the promotion share stays <= 1 of 15.
  - Power table printed for the lead: MDE at 2, 3, 5 seeds per headline metric. If MDE(2) for inactive IoU is above 0.08 (PROTOCOL 3.2 suggests about 0.11), inactive is never a screen primary; it is read on 5 seeds only.
- **Optional split-variance probe (P133; T10's P007 idea), gated:** after the above and only when cv02 has free GPUs: one new grouped fold assignment `cv5v3` (same 330 groups, same stratification rule as cv5v2 in `make_splits.py`, different seed), PF card unchanged, seed 5, 5 runs (5.5 GPU-h, cv02). Compare |metric(cv5v3, s5) - metric(cv5v2, s5)| with the seed SD from W1-C1. Rule: if the split difference exceeds 2 x seed SD on inactive IoU or crack relF1@2, the 5-seed table entries use one grouped assignment per seed (seed s on assignment s), at no extra GPU cost; screens keep cv5v2 for pairing.
- **What it should move (S):** no score. It may lower M toward 0.01 for crack metrics (if r < 0.7) or raise it. P133 says benchmark variance is of the order of published increments (R), so a well-set M is worth more than any single arm.
- **Risks:** the 15 splits share seeds, so r has about 4 effective degrees of freedom; the 1-of-15 rule only catches gross miscalibration. The probe must never be run on gaint dumps mixed with cv02 dumps. A/A tests seed noise only; it does not test fold-assignment noise (that is the optional probe).
- **Cost:** 3 build h; CPU about 1 to 2 h (25 x 2,000 draws on cached records); GPU 0 (optional 5.5).
- **Needs:** nothing new (numpy, scipy in the house venv).

---

## 2. `metric_validity_probe`: which crack metric can lead the table?

- **Papers:** P439 (fingerprint-driven metric choice; alt note: keep a metric only if its seed SD is below a known real gap), P188 (tolerance metrics), P134 (per-cell and worst-case IoU), P582 (thin subset, worst case), P601 (one implementation, unit tests), P492 (worst group). **Problem:** measurement. **Primary:** z_real(OP-W) = delta / SE for the 2-seed OOF ensemble minus the single-seed mean, per candidate crack metric, among metrics that pass the width probe.
- **Why (E):** tolerance metrics do not punish width (WAVE2 X4); relF1@2 is the headline (PROTOCOL 5.5); strict IoU sits near its label ceiling (0.48 to 0.60, PROTOCOL 5.2). No metric has been tested for whether it detects a known real gain and refuses a known fake one.
- **Inputs (E):** W1-G dumps of `house_r34_unetpp_pf_v11`, folds 0 to 4, seeds 5 and 6, with `logp` (LEAD 13 Nov: logp for the PF v1.1 runs). GT: v1.1 strict + ignore, from the manifests.
- **Derived dumps (shared with T2 gate G5):** `scripts/bench_ens_dump.py`: per cell `pbar = mean_s exp(logp_s)`; `pred = argmax pbar`; `oth = argmax over the 23 non-crack classes`; `m_crack = log pbar[14] - log max_{k != 14} pbar[k]`; `p_crack`, `p_inact` from pbar; written with `bench/dumpfmt.py` as method `pf_v11_ens2`, manifest field `derived_from` = the two run manifests' md5s. The writer's check `pred == where(m_crack > 0, 14, oth)` applies unchanged.
- **Probes** (all on the same OOF cells; each is a transform of a dump, applied before `crossfit_op.record`):
  - P-real: ens2 vs single-seed records (A = {5: rec5, 6: rec6}, B = {0: rec_ens2}); at OP-A and at OP-W (ens2's crack bias cross-fitted so its width ratio matches the single seeds', `crossfit_op.crossfit` objective width). The ensemble is about 13% wider (WAVE2 ens_kd_jml), so OP-W is the reading that removes width.
  - P-wide: single-seed map with crack dilated by 1 px (`score_ext.crack_dilated` applied to the prediction, not the GT). A fake gain.
  - P-thin: crack px off the 1-px skeleton (`bench/skel.py`) replaced by `oth`. A fake change in the other direction.
  - P-drop: 10% of the predicted crack components that touch GT within 2 px (chosen over the pooled list with `random.Random(0)`) replaced by `oth`. A known real loss.
  - P-shift: GT shifted 1 px right (`score_ext.shifted(gt, 0, 1)`, keep shifted the same way); jitter sensitivity S_j = (m(GT) - m(shifted GT)) / m(GT) on the single-seed maps.
- **Candidate metrics (new code in `bench/metrics_v02.py`; per-cell additions to the record, then pooled):**
  - crack: strict IoU; relF1@1, @2, @3 (exist); **centreline F1@2** = 2 Tp Ts / (Tp + Ts) with Tp = |skel(P) and EDT(G) <= 2| / |skel(P)|, Ts = |skel(G) and EDT(P) <= 2| / |skel(G)| (PROTOCOL 5.1 row "not measured yet"; record key `crack_cl2` = [skelP within 2, skelP, skelG within 2, skelG]); **component F1** = harmonic mean of `cc_rec50_20` and `cc_prec_20` (exist); per-cell mean crack IoU over cells with GT crack >= 20 px (P134 mIoU^C rule: GT-absent cells are NULL, not 0); worst-10% per-cell relF1@2 over the same cells (P134 q = 10, P582); worst-source relF1@2 over ARTS, BMRK, CFVS, CSIR (P492; sources with >= 40 cells).
  - inactive (reported, same probes not applied): pooled IoU; per-cell IoU over cells with GT inactive >= 0.5%; region F1 (`in_cc_rec50`, `in_cc_prec`); boundary IoU at d = 2 if T10's P549 code exists, else skipped.
- **Bootstrap:** a generic `boot_fn(A, B, stems, fold_of, groups, fn)` beside `boot_pair`: same two stages; `fn(records, weights)` computes a metric from per-cell records with integer weights (pooled metrics: weighted sums; per-cell means: weighted means; worst-q: cells repeated by weight, then the lowest q%). `boot_pair` itself is not edited (frozen; WAVE2 guard 10).
- **Unit tests** (`tests/test_bench_metrics_v02.py`): (1) 1-px diagonal GT line, perfect prediction: every metric = 1. (2) Same with the prediction dilated by the cross: strict IoU = n / (3n - 2) approximately 1/3, relF1@2 = 1, centreline F1@2 = 1. (3) A 3-px-wide GT bar and its 1-px skeleton as prediction: centreline F1@2 = 1. (4) EDT convention: a prediction px at (2, 1) offset from the only GT px (distance 2.24) is outside 2 px, one at (1, 1) and (2, 0) inside (P601: the convention is stated and tested, matching m0 `cell_stats`).
- **Decision rules (fixed now):** a crack metric is eligible to lead the table if all hold:
  - E1: z_real at OP-W >= 2;
  - E2: P-wide delta <= 0, or its 95% CI includes 0;
  - E3: P-drop delta < 0 with CI high < 0.
  The headline crack metric of v0.2 is the eligible metric with the largest z_real(OP-W); within 10% of each other, the lower S_j wins. Strict IoU stays printed beside its ceiling band. If relF1@2 fails E2, it stays in the table only as the pair (relF1@2, width ratio), never alone (as now, X4), and loses the first column.
- **Expected (S, not measured):** strict IoU passes E2 and E3 with high S_j (a 1-px shift of a perfect mask already costs 0.45 to 0.5, PROTOCOL 5.2); relF1@2 fails E2 (recall gains about as much as precision loses); centreline F1@2 passes E2 by construction and has low S_j; it is my candidate for the first column. This also answers the lead's question of whether the method ranking changes between strict IoU, relF1@2 and a matching metric, on the cheapest possible "methods" (probes); item 3 answers it on real methods.
- **What it should move:** the headline metric order of v0.2 and every arm's primary metric choice for wave 3. No score.
- **Risks:** the 2-seed ensemble gain is small on CV (on the test set a 5-seed ensemble gave +0.014 to +0.018 crack IoU, E BRIEF 3), so z_real may fall below 2 for every metric; then E1 is re-read with the 5-seed ensemble on W1-C1 (same code) before any metric is dropped. Probes are synthetic: a metric could pass all of them and still misjudge a real arm that changes shape (item 3 covers real methods). gaint dumps only, read alone (no cv02 mixing).
- **Cost:** 4 build h (2 for ens dump + probes, 2 for metrics + boot_fn + tests); CPU about 1 h; GPU 0.
- **Needs:** nothing new.

---

## 3. `rank_stability`: how stable is the method order, and does it depend on the metric?

- **Papers:** P578 (blob plots, Kendall tau violins, significance maps; R full text), P598 (low-data rankings unstable), P595 (rankings reverse across splits and metrics; R abstract), P265 (label errors flip rankings; R abstract), P133 (P(A>B) with gamma 0.75; R full text). **Problem:** benchmark_row. **Primary:** median Kendall tau between the full-data ranking and the bootstrap rankings, per headline metric.
- **Entries (E for what exists, S for derived):** W1-C1 PF v1.1 (5 seeds), W1-C2 house v1.1 (2), W1-C3 PF v1 labels (2, scored on v1.1); derived from PF: 2- and 5-seed ensembles (`bench_ens_dump.py`), OP-F, OP-W, src_calib, dti readouts. Then every wave-2 arm as it is scored (the tool is re-run; the entries list grows). One machine per read.
- **Code:** `scripts/bench_rank.py` over `w1read` records:
  ```
  for b in 1..1000: draw groups with replacement (330), per (fold, entry) one seed (as boot_pair)
      metric[e, b] for e in entries, for metric in HEADLINE + item-2 metrics
  rank_full[e] = rank of the point estimate; rank_b[e, b]
  blob[e, r] = share of draws with rank r; interval95[e] = percentiles 2.5, 97.5 of rank_b[e]
  tau_b = Kendall tau(rank_full, rank_b[:, b]); report median and 5th percentile
  P(A>B) = share of draws with metric[A] > metric[B]                     # significance map, one-sided
  tau_metric[m1, m2] = Kendall tau between metric orders (full data)
  subsets: all; minus noisy-flag cells (cells.tsv); minus label-flagged cells (T10 A0(e) list for inactive, T3 flag list for crack, when they exist); per source (ARTS, BMRK, CFVS, CSIR); worst source
  ```
- **Unit test:** entries with identical records give every rank interval = the full span and tau undefined (handled as NaN); entries separated by a large constant give tau = 1 in every draw.
- **Decision rules (fixed now):**
  - In the benchmark table, A is printed ahead of B only if P(A > B) >= 0.95 over the bootstrap; otherwise they share a rank ("tied"), and the table prints the 95% rank interval for every entry (P578). P133's gamma: P(A > B) >= 0.75 is printed as "meaningful" beside it.
  - A headline metric whose median bootstrap tau is < 0.8 is printed but does not order the table; the table is ordered by the eligible metric from item 2 with the highest median tau.
  - If strict IoU and the item-2 lead metric order the entries separated by >= M differently (tau between them < 0.6), the table prints both orders and states which goal each serves (placement vs capture).
  - Removing flagged cells: if any pair's P(A > B) crosses 0.5, the table marks that pair "label-sensitive" (P265).
- **What it should move:** how the benchmark prints rankings (ties, intervals); which wave-2 "wins" are reported as wins. No score.
- **Risks:** derived entries (OP variants, ensembles) are strongly correlated with PF, which makes their mutual ranking look stable; the tool prints entry families. With few independent methods before wave 2, the first read describes the instrument more than the field. One machine per read.
- **Cost:** 3 build h; CPU under 1 h per read; GPU 0.
- **Needs:** nothing new (Kendall tau from scipy.stats).

---

## 4. `tau_from_annotators`: is 2 px the right tolerance?

- **Papers:** P188 (tau = 95th percentile of inter-observer distances; R full text), P601 (convention). **Problem:** measurement. **Primary:** tau95 for crack, pooled over train + val same-cell pairs.
- **Inputs (E):** `benchmark/out/label_checks_summary.txt` section 3 and `pairs.tsv` (same physical cell, different image id, with image alignment shift); the double annotation `CFVS_00015_r7_c4` = `CFVS_00016_r7_c4`; v1.1 strict masks. **Excluded:** every pair with a legacy test cell (for example `ARTS_00020_r5_c1`, `CFVS_00006_r5_c5`) and every E1 cell (sealed); exact copies (raw IoU 1.0) and near copies (raw IoU >= 0.85 before alignment; about 10 pairs, PROTOCOL 2.5 row 3), which would pull tau toward 0.
- **Code:** `benchmark/scripts/tau_pairs.py` (CPU, `python -I`, reuses the alignment of `label_checks.py` and `data_analysis/scripts/annotation_consistency.py`):
  ```
  for pair (a, b) after alignment shift (dy, dx):
      A = crack(a) & keep, B = crack(b) & keep                 # 512x512 bool
      dA = EDT(~B)[A]; dB = EDT(~A)[B]                         # Euclidean, as m0 cell_stats
      matched = concat(dA[dA <= cut], dB[dB <= cut]); unmatched_share = share > cut   # cut = 10 px (also 5, 20 reported)
  tau95 = percentile(pooled matched distances, 95); CI from 2,000 bootstrap draws over pairs
  also: per source; per pair; inactive pairs (13) on region boundaries -> tau95_inactive
  ```
- **Decision rules (fixed now):** tau95 <= 2.0 (CI high <= 2.5): relF1@2 confirmed with a citable rule. 2.0 < tau95 <= 3.0: relF1@3 becomes the headline tolerance, @2 beside it. tau95 <= 1.0: relF1@1 headline. Reported in all cases: the unmatched share (crack growth between stages or missed branches), which tolerance cannot cover.
- **What it should move:** the tolerance written into v0.2 (and the centreline F1 tolerance of item 2). The BRIEF's "0.82 to 0.99 within 2 px" (E) suggests tau95 near or above 2 px (S).
- **Risks:** the pairs are images of one cell at different stress stages, so a crack can grow: distances mix annotation jitter with real change (the cutoff and the unmatched share separate them only roughly). About 12 usable pairs; one double annotation. BMRK and SDLE have no pairs, so per-source tau exists for ARTS and CFVS only. A second annotation of about 30 cells would settle it (PROTOCOL 8, optional manual item 2); not requested (no manual labelling).
- **Cost:** 1.5 build h; CPU minutes; GPU 0. **Needs:** nothing.

---

## 5. `leakage_audit_v02`: near-duplicates the module rule cannot see

- **Papers:** P570 (leakage taxonomy, model info sheets), P579 (embedding near-duplicate search), P631 (dedup across merged sources; random split as the counter-example), P443 (list of external EL sets). **Problem:** measurement. **Primary:** number of cross-set pairs at or above the twin threshold that are not already linked in `cv5v2_groups.tsv` / `groups_all.tsv` or listed in `forbidden_v1.txt`.
- **Why (E):** the module rule uses equal positions, crack-mask IoU and a CFVS high-pass correlation (PROTOCOL 2.1); "a module re-imaged upside down would be missed (not checked)" (PROTOCOL 3.1); BMRK cells have no module id (3.2); pool vs E1 is excluded by image id only (T7 spec l.160, 225), and pool-using arms (T7 target lists, SSL) need module-level exclusion of E1. Item 8 would add ELPVPower modules, from the same lab family as ELPV / BMRK.
- **Code:** `benchmark/scripts/dedup_embed.py` (CPU): DINOv2 ViT-S/14 from the local torch-hub file (`dinov2_vits14_pretrain.pth`, E DESIGN 1.10) loaded into timm `vit_small_patch14_dinov2` (timm 1.0.30; key mapping checked by a load with `strict=True`); input = grayscale cell copied to 3 channels, 224 px, also the 8 dihedral views (to catch re-imaged modules upside down); embedding = CLS token, L2-normalised; for each pair of cells in different sets take the max cosine over the 8 views. Sets: P532, F51, H36, F19, the 17 unused `_rf`, the 11.9k pool, and the legacy test / E1 images (images only: no labels, no predictions; the same use the module rule already made of them, PROTOCOL 2.1). The threshold = the 5th percentile of cosine over KNOWN same-cell pairs (7 test twins, 16 multi-stage physical cells, the CFVS_00015 / 16 duplicate); its false-alarm rate is estimated on pairs from different sources (which cannot be the same cell).
- **Pre-check:** the known pairs must separate: AUROC of cosine for known same-cell pairs vs different-source pairs >= 0.95; else fall back to the existing high-pass NCC rule on candidate pairs only (no new claim).
- **Decision rules (fixed now):** every flagged pair inside P532 across two folds -> a new group link and a `cv5v2b` split with a new md5 before the 5-seed table (screens already run on cv5v2 carry a one-line caveat); every flagged pool cell that matches an E1, F51 or H36 cell -> added to the pool exclusion list used by T7 and any pool-using arm; every flagged cell matching a legacy test cell -> listed in the L-test "twins" subset. Report counts per set pair.
- **What it should move:** no score; it removes optimistic bias from the unseen-module numbers of pool-using arms and from CV.
- **Risks:** EL cells of the same cell type look alike (busbar layout), so cosine may flag same-layout different cells; the different-source false-alarm estimate bounds this. Images of sealed cells are read (pixels only); the lead must confirm this matches the sealing rule (PROTOCOL treats sealing as labels and predictions).
- **Cost:** 3 build h; CPU about 30 to 60 min for about 12.7k cells x 8 views (S); GPU 0. **Needs:** local DINOv2-S weights (public, not gated, already on gaint).

---

## 6. `t5_post_eval`: the honest version of severity

- **Papers:** P617 (crack length and count not universal power predictors, non-isolating cracks; R abstract), P609 (isolated area drives heating; scout), P263 (per-cell loss roughly proportional to inactive area; inactive-area threshold MAE 8.5 W vs SVR 9.0 W; R full text), P615 (T7: module severity = worst cell). **Problem:** inactive (post-evaluation). **Primary:** per-cell inactive area fraction MAE (% of non-padding px) over P532 OOF.
- **Decision on value, with evidence (family card section 2):** no electrical ground truth for any cell; P532 bands 484 / 10 / 7 / 31 / 0 (E PROTOCOL 6). A power band cannot be scored. What has support in the literature is inactive (isolated) area; crack length does not. So v0.2 keeps T5 as a descriptive post-evaluation with three changes and one gated addition; it never ranks methods.
- **Per-cell outputs (new `bench/post_eval.py`, from dumps, no labels needed to compute; GT only to score):**
  - inactive area fraction a = inactive px / non-padding px (padding = class 7, ribbons = class 4 in the 24-class list, `make_masks_v11.py` NAMES); error a_pred - a_gt; bands {0, (0, 1%), >= 1%} (Gabor 1% "critical" threshold, handbook 05 section 15); 3x3 confusion matrix with counts; weighted kappa with group-bootstrap CI;
  - cell-level inactive detection at a >= 0.5% (sensitivity, false-alarm rate on the 484 inactive-free cells);
  - crack length (skeleton px) and its error: printed as descriptive, labelled "not a power proxy (P617)";
  - crack orientation: angle of each crack component's principal axis to the ribbon direction (principal axis of the predicted ribbon class); descriptive;
  - isolation risk (gated, below): area share of the cell that the predicted crack components, together with the cell border, cut off from every predicted ribbon (connected components of non-padding, non-crack px after removing crack px; regions not containing a ribbon px).
- **CPU pre-check for isolation risk (on GT masks only, P532, now):** compute the isolation area share from GT crack + GT ribbons; AUROC for "cell has GT inactive" over the 229 crack cells. Pass: AUROC >= 0.75 and the isolated area correlates with GT inactive area (Spearman >= 0.5). Pass -> isolation risk enters T5 as a label-free risk score; fail -> dropped (no power or label support).
- **Value test (fixed now):** T5 earns a place beside the headline only if, on the W1-C entries, the per-cell inactive area MAE either orders house vs PF differently from pooled inactive IoU, or separates them with a larger |z|. Otherwise it is a one-table appendix.
- **What it should move:** nothing in training. It gives WattCycle the quantity it would act on (inactive fraction per cell, worst cell per module) with an error bar.
- **Risks:** 31 cells in the >= 1% band (E): kappa is noisy; inactive is decided by few groups (34). The single-label convention (crack over inactive) puts crack px inside inactive regions; T5 uses PROTOCOL 4.4's derived region (inactive plus enclosed crack px) for both GT and prediction.
- **Cost:** 3 build h; CPU minutes; GPU 0. **Needs:** nothing.

---

## 7. `reporting_governance`: what every benchmark row must state

- **Papers:** P570 (model info sheets), P595 (reporting checklist; audit format), P545 (intervals for published numbers), P637 (published PV inspection numbers not comparable), P439. **Problem:** benchmark_row. **Primary:** none (text).
- **Changes to PROTOCOL_DRAFT (v0.2 text):**
  1. **Model info sheet per entry** (P570): split name + md5; pool and extra data with leakage exclusions applied (item 5 lists); declared resources (source id at test time: yes / no, a lead decision already in force); seeds; machine; operating-point rule (OP-A / OP-F / OP-W from `crossfit_op`); training compute; the dump manifest md5s. Generated from the method card + manifests by `scripts/bench_infosheet.py` (1 h of the 3).
  2. **Reporting checklist** (10 items, adapted from P595's 5-point idea and PROTOCOL 1): release and label set; split and grouping; class list and absent-class rule; metric definitions with tolerance and distance convention (item 4, P601); operating point; seeds and machine; interval method (item 1); number of contrasts and set openings (WAVE2 X2); with / without noisy and flagged cells; ranking with ties (item 3).
  3. **Test ledger** (exists, `benchmark/test_openings.md`): one opening per locked protocol, registered before reading; E1 the same (`e1_openings.md`).
  4. **Related-work table:** every published EL number with release, split, metric convention, and an interval, or "no interval reported"; P545's quadratic SD reconstruction is Dice-specific and is not applied to our metrics (S).
  5. PROTOCOL section 1 rewritten as an audit with counts of papers per problem (P595 format), citing P637 for PV inspection in general.
- **Cost:** 3 build h; GPU 0. **Risks:** none for scores; it adds writing time in the last week if left late.

---

## 8. `severity_external_elpvpower` (RUN_AFTER_GATE): the only public link to measured power

- **Papers:** P263 (ELPVPower: 719 module EL measurements of 137 module instances with Pmpp; code and models public; R full text), P564 (cells with staged damage and Isc / Voc per stage; scout). **Problem:** benchmark_row (severity). **Primary:** Spearman rho between the module sum of predicted inactive area fraction and relative power loss (Pmpp of the measurement / Pmpp of the same module's first measurement, or / nominal when no first measurement exists).
- **Gate (all three):** (a) user OK to download the Jülich DATA set (doi:10.26165/JUELICH-DATA/TVWUUP; licence and size unverified, the landing page refused my fetch); (b) a 20-module pilot cuts cells automatically (module rectification from the 10x6 / 12x6 grid by projection profiles, or the elpvpower preprocessing if it exposes cells) with >= 95% usable cells and no manual step; (c) item 5's embedding check finds no ELPVPower module among BMRK training cells (ELPV comes from the same lab family; R scout D02, unverified). Best time: after the final model exists; the PF baseline is enough to decide value.
- **Analysis:** cells resized to 512 px (as BMRK cells are), PF v1.1 models of the 5 folds averaged (no fold saw these images), per cell inactive area fraction and crack length; per measurement the sums; Spearman rho with relative power (grouped bootstrap over the 137 module instances); comparison rows: crack length sum (P617 expects weaker), and the paper's own baselines (R: inactive-area threshold MAE 8.5 W; ResNet18 MAE 7.3 W). Module types T1 / T2 / T3 reported separately (R: T3 does not transfer in the paper).
- **Decision rules (fixed now):** rho >= 0.6 and rho(inactive) > rho(crack length) by more than the bootstrap SE: v0.2 adds an external validity row "predicted inactive fraction vs measured power" and T5's inactive bands become a severity output with this evidence. Otherwise severity stays parked and the row reports the null.
- **Risks:** module-level power hides which cells cause it; on-site measurements carry >= 5% uncertainty (R); load-cycle series of one module are not independent (group by module instance); a domain gap (2048 px camera, 60-cell poly modules) may make our inactive predictions poor, which then measures transfer, not severity.
- **Cost:** 8 build h (download, cell cutting, inference script via `bench_infer` on a new unlabelled set, analysis); GPU about 1 h (about 43k cells x 5 fold models; S); CPU otherwise. **Needs:** ELPVPower data (public per paper; licence unverified; user OK needed); no new packages if the cell cutting is written in numpy / OpenCV (opencv-headless is in the house venv, E).

---

## Decisions the lead must make
1. Run `aa_calibration` as soon as W1-C1 is relayed, before any wave-2 verdict, and adopt its M rule.
2. Accept the eligibility rules of item 2 now, before the numbers: relF1@2 may lose the first column if it rewards a 1-px dilation.
3. Item 5 reads pixels of the legacy test and E1 images (no labels, no predictions) for the duplicate search: allowed under the sealing rule?
4. Benchmark tables print ties (P(A > B) < 0.95) and rank intervals (item 3).
5. Severity: v0.2 keeps T5 as descriptive post-evaluation only; ELPVPower (item 8) waits for the user's OK on the download and is best run after the final model.
