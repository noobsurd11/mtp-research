# T10 spec: inactive and the weak classes (4 arms + one CPU analysis)

Analyst T10, 13 Nov 2026. Tags: R = paper, E = our files, S = my judgement. Papers and evidence: `cards/T10_rare_classes_family.md`. Ledger: `cards/ledger/T10.tsv`.
Nothing here is launched. No GPU, no server, no sealed data touched.

## 0. Summary for the lead

| Order | Name | Route | Problem | Primary | Build h | GPU-h (screen) | Waits for |
|---|---|---|---|---|---|---|---|
| A0 | `ci_error_atlas` | analysis_only | inactive, weak classes, label errors | none (decides arms) | 4 | 0 | W1 PF v1.1 dumps (exist tonight) |
| 1 | `ci_rules_posthoc` | inference_only | inactive | inactive IoU | 2 | 0 (+0.2 for F51 dumps) | A0 part (d) |
| 2 | `classbias_xfit` | inference_only | weak classes (mIoU-R13) | mIoU-R13 | 4 | 0 | `crossfit_op`, `logp` dumps |
| 3 | `layered_ci` | new_model_code | inactive (crack-inactive overlap) | inactive IoU | 7 (5 if the shared aux-target hook is built) | 11 + 1.1 pathfinder | gate G-layer from A0 |
| 4 | `inact_paste` | data_pipeline | inactive (data-limited) | inactive IoU | 7 | 11 + 1.1 pathfinder | gate G-paste from A0, CPU paste pre-check |

Gated follow-up (not a separate arm): `la_ce`, training-time logit offsets, opens only if `classbias_xfit` passes (1 build h, 11 GPU-h).
Parked behind A0: `inact_refiner` (P183 / P082, ConvCRF P314 as its zero-training control), gate G-refine.

Why this order (S). Inactive and the weak classes can be measured far better post hoc than by training: a post-hoc rule is compared with the baseline on the **same** predictions, so seed noise drops out and only the cells it changes enter the contrast, whereas a trained inactive arm at 2 seeds needs about +0.08 to +0.11 inactive IoU to be seen (E, PROTOCOL 3.2: SE 0.038). Three CPU jobs (10 build hours, 0 GPU-h) therefore come first, and they decide which of the two GPU arms is worth its build.

What makes these arms different from wave 2 (E, WAVE2_REVIEW 4): `rcs` (T1) is the only arm on problems 2 and 4 and acts by resampling cells; none of mine resamples. `src_calib` (T4) fits a crack bias per source; `classbias_xfit` never touches the crack bias and fits one bias per non-crack class. `oof_selective_ignore` (T3) owns crack label flags; A0's label-quality list excludes crack.

Existing harness support used by the first arms (E, DESIGN 3.1 to 3.2, LEAD 13 Nov): canonical fp32 dumps with `pred`, `oth`, `m_crack`, `p_crack`, `p_inact`, `logp` for the PF v1.1 runs; `bench_score.py` (per-class IoU, inactive P / R and region recall, per-source tables); the two-stage group bootstrap of `b6_verdict.py` on `cv5v2_groups.tsv` (330 groups); `crossfit_op` (fold-wise cross-fitting pattern, reused for the class biases); house venv numpy + scipy (no install).

---

## A0. `ci_error_atlas`: where inactive and weak-class errors come from (CPU, before any GPU run)

- **Papers:** P196 (softmin label quality), P009 (out-of-fold ensemble 1 - IoU ranking), P015 (decision-rule diagnostics). Route analysis_only. Priority 95.
- **Inputs (E):** OOF dumps of `house_r34_unetpp_pf_v11` on `cv5v2`, every fold, seeds 5 and 6 (gaint W1-G now; repeat on W1-C1 seeds 5 to 9 when relayed). GT = held-out strict v1.1 masks and ignore masks, paths read from each run's `manifest.json` as `bench_score` does. Ignore px are excluded everywhere. Also the seed-mean softmax `pbar = mean_s exp(logp_s)`.
- **File:** `bench/analysis/t10_atlas.py` (el_bench), numpy + scipy only; outputs `bench_out/t10/atlas/{summary.txt, buckets.tsv, cells.tsv, label_issues_t10.tsv, gates.json}`. Runs in tmux `bench_t10_atlas` on gaint CPU; about 1 to 2 h for 2 seeds (S: 532 cells, 13 GB of `logp` streamed one cell at a time).
- **Notation:** `G` GT index mask, `P` the dump's `pred` (OP-A), `GI = G==11`, `GC = G==14`, `PI = P==11`, `PC = P==14`. Components are 8-connected (`scipy.ndimage.label` with a 3 x 3 structure). `dC` = Euclidean distance to the nearest GT crack px (`distance_transform_edt(~GC)`); `bI` = px within 3 px of the GT inactive boundary (inside or outside).

### (a) Inactive error buckets (pixel level, pooled over cells, per seed and seed-mean; per source; BMRK separately)
Each inactive false negative (`GI & ~PI`) gets the first bucket that applies:
1. FN-overlap: `P == 14` (wrong class at the overlap).
2. FN-missed: in a GT inactive component (>= 100 px) whose coverage by `PI` is < 10% (region missed).
3. FN-crackadj: `dC <= 3`.
4. FN-boundary: in `bI`.
5. FN-interior: the rest (holes inside a found region).

Each inactive false positive (`PI & ~GI`):
1. FP-on-crack: `G == 14`.
2. FP-spurious: in a predicted inactive component with < 10% of its px on `GI`; split by (cell has GT inactive or not) and by (a `PC` px within 5 px of the component or not).
3. FP-crackadj: `dC <= 3`. 4. FP-boundary: in `bI`. 5. FP-other.

Oracle IoU gains, each applied alone to `P` and scored pooled: O1 fix the overlap (FN-overlap -> 11, FP-on-crack -> 14); O2 find the missed regions; O3 delete spurious components; O4 fix boundary px; O5 fix crack-adjacent px. Each with a group-bootstrap interval. Also: number of GT inactive regions >= 100 px, region recall and region precision.

### (b) Crack at the overlap
GT crack px with distance <= 2 px to `GI` ("crack at inactive"; E says about 20% of train crack px): share predicted 14 / 11 / 0 / other; crack pixel recall and relR@2 there and elsewhere; share of all crack false negatives that are predicted inactive. This states whether crack loses px to inactive at the overlap (which would make any inactive gain cost crack).

### (c) Weak classes (gridline 15, splice 16, edge_dark 20, material 13)
- False negatives by predicted class (top 5, px shares) and false positives by GT class (top 5).
- GT components >= 20 px: share missed entirely (< 10% covered); share of error px within 2 px of the class boundary; per source.
- Margin of the false negatives: median and quartiles of `logp_c - max_{k != c} logp_k`. If most lie below -6 nats no bias can reach them.
- In-sample single-class bias oracle: the best IoU of class c over a bias on c alone (grid -2 to +6, step 0.25), fitted and scored on all 532 cells (optimistic upper bound for arm 2, never a result).

### (d) Co-occurrence rule statistics (pre-check of arm 1)
- GT side: share of GT inactive components (>= 100 px) with a GT crack px within d = 3, 5, 10 px.
- Prediction side: predicted inactive components with no `PC` px and no `p_crack >= 0.2` within d = 5: count, px, share of all predicted inactive px, and their precision (share on `GI`).
- Holes: px enclosed by components of `PI | PC` that hold >= 50 `PI` px, with `p_inact >= 0.05` and `P != 14`: count and precision.

### (e) Label-quality scores (P196, P009), no mask is changed
- Per cell: softmin over non-ignore px of `s = pbar[G]` with temperature 0.1, weights proportional to `exp(-s / 0.1)` (the extracted text of P196 lacks the equation; this is the soft minimum it describes; check against the PDF before quoting it as P196's exact score).
- Per GT component of classes 11, 13, 15, 16, 20 (>= 20 px; inactive >= 100 px): CoCo score = mean `pbar[c]` over the component. FL candidate = score < 0.05 in the seed-mean and in each seed.
- Per predicted component of class c (from `argmax pbar`) lying >= 80% on GT background with mean `pbar[c] >= 0.9` and >= 50 px (inactive >= 200 px): ML candidate.
- P009 score: per cell and class, 1 - IoU(seed-mean prediction, GT) and its spread over seeds.
- Positive control (no labelling needed, E: `benchmark/out/masks_v11/SUMMARY.txt`): on the W1-C3 dumps (PF on v1 masks), scored against v1 masks, `BMRK_00031_cell0091` (v1 crack 1,560 px, v1.1 66 px) and the scuff-as-crack cells (6 train cells) must rank in the worst 10% of the per-cell crack softmin. If they do not, the scorer is not trusted and the list is not published. Crack is used only for this control.
- Consistency check: overlap of inactive FL candidates with the B1 audit's 9 inactive-FL cells (handbook 19 §8.1; B1 used other models on 239 cells, so this is agreement, not truth).
- Output `label_issues_t10.tsv` (cell, class, type FL / ML, px, score, seeds agreeing). It goes to PROTOCOL 2.5 as an automatic label-issue list and gates a later ignore arm (parked).

### Gates written now (read from `gates.json`; thresholds are my judgement, fixed before any number)
- **G-rules (arm 1 variant choice):** if fewer than 97% of GT inactive components have a GT crack within 5 px, arm 1 uses d = 10 instead of 5. GT-only statistic, read before any rule result.
- **G-layer (opens arm 3):** (FN-overlap + FP-on-crack + FN-crackadj + FP-crackadj) >= 25% of inactive error px (FN + FP, seed-mean), or O1 + O5 >= +0.04 inactive IoU.
- **G-paste (opens arm 4):** FN-missed >= 35% of inactive FN px, and < 50% of FN-missed px lie in FL-candidate components (missed regions that look like label errors are not a data shortage).
- **G-refine (opens the parked `inact_refiner`):** FN-boundary + FP-boundary >= 40% of error px and O4 >= +0.05.
- **G-bias (sets arm 2's expectation, closes nothing):** the in-sample single-class oracle gains >= +0.05 IoU on gridline or splice.
- If neither G-layer nor G-paste opens, no T10 GPU arm runs in wave 2; the report says which error type dominates and which family owns it.

---

## Arm 1. `ci_rules_posthoc`: crack-inactive co-occurrence rules on the dumps

- **Papers:** P252 (cross-class interaction rules), P342 (rules at inference, parked as a method). Problem: inactive. Route inference_only. Priority 85.
- **Primary metric:** inactive IoU at OP-A, rule applied minus no rule, on the same dumps.
- **Hypothesis (S):** inactive precision is 0.63 (test). Inactive never occurs without a crack (E). A predicted inactive component with no crack evidence nearby is likely a false alarm (R-a). An area enclosed by predicted crack and inactive that the model left as background is likely a missed part of the region (R-b).
- **Exact change** (`bench/post/ci_rules.py`, numpy + scipy; applied to any dump; switched on by the method card key `post: ci_rules_a` or `ci_rules_b`; the scorer scores the post-processed `pred`):
  ```
  # inputs per cell: pred (512,512) u8, p_crack (512,512) f16, p_inact f16, logp (24,512,512) f16
  NOT_CI = [k for k in range(24) if k not in (11, 14)]
  def rule_a(pred, p_crack, logp, d=5, pc_min=0.2):          # d from gate G-rules
      lab, n = ndimage.label(pred == 11, structure=ones((3,3)))
      crack_ev = (pred == 14) | (p_crack >= pc_min)
      disk = disk_struct(d)                                    # Euclidean disk, radius d
      out = pred.copy()
      for k in 1..n:
          K = lab == k
          if not (binary_dilation(K, disk) & crack_ev).any():
              out[K] = NOT_CI[argmax(logp[NOT_CI][:, K], axis=0)]
      return out
  def rule_b(pred, p_inact, pi_min=0.05, min_inact=50):
      lab, n = ndimage.label((pred == 11) | (pred == 14), structure=ones((3,3)))
      out = pred.copy()
      for k in 1..n:
          U = lab == k
          if (pred[U] == 11).sum() < min_inact: continue
          H = binary_fill_holes(U) & ~U & (p_inact >= pi_min) & (pred != 14)
          out[H] = 11
      return out
  # stacked variant (only if both pass alone): rule_b(rule_a(pred))
  ```
  Invariant asserted per cell: `(out == 14) == (pred == 14)` (crack px never change).
- **Unit tests (`tests/test_ci_rules.py`):** (1) a cell with no predicted inactive is unchanged; (2) synthetic: an inactive blob 10 px from the nearest crack evidence is deleted at d = 5, a blob 3 px away is kept; (3) the replacement class is the argmax over the 22 classes; (4) rule_b fills a background hole inside an inactive ring and leaves a hole with p_inact 0 alone; (5) crack invariant on 50 real dumps; (6) idempotence: applying a rule twice equals once.
- **CPU pre-check:** A0 part (d) is the pre-check. Pass rule to spend the 2 build hours: R-a would delete >= 3% of predicted inactive px with precision of the deleted px <= 0.40, or R-b would add >= 3% with precision >= 0.50. Otherwise the variant is dropped without a readout.
- **Readout (no pathfinder, no GPU):** each variant against the baseline on the same dumps, seeds 5 and 6 (later 5 to 9), two-stage bootstrap (groups, then seeds). Two contrasts (Holm over 2). **Pass:** delta inactive IoU >= 0.01 with the 95% interval above 0; R-a may not lower inactive recall by more than 0.02, R-b may not lower inactive precision by more than 0.02. Guards: inactive P, R, region recall and precision; mIoU-R13; per source (BMRK row); predicted inactive px on the 484 inactive-free cells. Crack metrics are unchanged by construction (asserted).
- **Transfer check (required before the rule enters any final model):** F51 inactive IoU with and without the rule, paired over the 10 W1-C1 fold x seed models (needs F51 dumps: inference only, about 0.2 GPU-h); the rule may not lower it by more than 0.01. H36: deleted inactive px per cell, descriptive.
- **Should move (S):** inactive precision up (R-a) or recall up (R-b); inactive IoU +0.00 to +0.03. Paper evidence: none quantitative for this rule (P252 has no numbers on its abstract page).
- **Drop rule:** fails the pass rule on CV, or fails the F51 transfer check.
- **Cost:** build 2 h (reuses A0 component code), GPU 0 (+0.2 GPU-h F51 inference shared with arm 2).
- **Needs:** nothing new.
- **Risks and how it could mislead:** (1) **E1 transfer (largest risk):** on unseen half-cut cells crack recall is 0.17 (E, BRIEF 3), so R-a would delete true inactive whose bounding crack the model missed. F51 has no half-cut cells; H36 shows only how much is deleted. Declare this in any E1 read. (2) d and pc_min are fixed, not tuned; if a later tuning is wanted it must be cross-fitted with `crossfit_op`. (3) It is a post-processing entry: in the benchmark it is a labelled decision layer, not a model.

---

## Arm 2. `classbias_xfit`: cross-fitted per-class logit bias for the weak classes

- **Papers:** P015, P045 (post-hoc part), P152. Problem: weak classes (gridline, splice, edge_dark, material) and mIoU-R13. Route inference_only. Priority 80.
- **Primary metric:** mIoU-R13 at OP-A + fitted class biases, minus the baseline at OP-A, same dumps.
- **Hypothesis (S):** gridline (recall 0.33, precision 0.68) and splice (never predicted) are under-called at argmax. R2c showed that shifting gridline toward recall raises its IoU (0.283 -> 0.357, E) at no crack cost; a fitted bias may buy the same for free. P015 (R) shows a full prior correction (ML rule) loses more than 5% mIoU against argmax, so the bias must be fitted to IoU, not set to log priors.
- **Exact change** (`bench/post/classbias.py`; uses `logp`; cross-fitting through the same fold loop as `crossfit_op`):
  ```
  R13 = [0,1,2,4,5,7,11,13,14,15,16,20,21]
  FREE = [1,2,4,5,7,11,13,15,16,20,21]      # 11 biased classes; b[0] = 0 (reference); b[14] = 0 (crack has OP-A/F/W)
  ORDER = [16,20,11,13,15,21,5,4,2,1,7]       # rarest first
  GRID = arange(-1.5, 4.01, 0.25)             # 23 values
  # cache per cell: contested px = any FREE class within 4 nats of the top logp, or the top class in FREE;
  #   store logp (24, n_px) f16 + GT for those px; non-contested px keep pred (their argmax cannot change)
  def fit(cells):                              # cells of 4 folds, one seed
      b = zeros(24)
      for sweep in 1..3:
          for c in ORDER:
              b[c] = argmax_{v in GRID} mean_IoU_{R13 \ {14}}(argmax(logp + b_with(c=v)), GT over cells)
      return b                                  # ties: the value closest to 0
  for seed in seeds: for k in 0..4:
      b_k = fit(OOF cells of folds != k, this seed);  pred_k = argmax(logp + b_k) on fold k
  ```
  Output: `classbias_b.tsv` (seed, fold, 24 values) and post-processed dumps (`pred`, `oth` recomputed; `m_crack` recomputed from the biased logits so the crack readouts stay exact). Switched on by the card key `post: classbias_xfit`.
- **Unit tests:** (1) b = 0 reproduces `pred` exactly; (2) the contested-px cache gives the same confusion matrix as a full recompute on 20 cells for 50 random b; (3) cross-fit assert: the fit for fold k never reads a fold-k cell (fails closed); (4) b[14] and b[0] stay 0.
- **CPU pre-check:** A0 (c), the in-sample single-class oracle and the margin distribution. It cannot kill the arm (the arm is itself CPU), but if no weak class gains >= +0.02 in-sample, the arm is reported as "decision-limited share small" and `la_ce` stays closed.
- **Readout (no GPU):** cross-fitted result against the baseline on the same dumps, two-stage bootstrap. **Pass:** delta mIoU-R13 >= 0.01 with the 95% interval above 0; crack strict IoU and relF1@2 at OP-A not down by more than 0.005 (crack is not biased but neighbouring classes can take crack px); inactive IoU not down by more than 0.01; no R13 class down by more than 0.03. Guards: per-class IoU, P, R for all 13 classes; per source; fold-to-fold spread of each b_c (a b_c whose sign flips between folds is reported as unstable).
- **Should move:** gridline IoU up (S: +0.03 to +0.07, the R2c range), splice from 0 to something (S: 0 to +0.15; 60 P532 cells), edge_dark and material small. mIoU-R13 +0.005 to +0.02 (S). R: P015 rare-class instance recall +23 to 25% under the unfitted ML rule with lower mIoU; P045 post-hoc LA reaches most of the loss version's gain on ImageNet-LT and iNaturalist.
- **Drop rule:** fails the pass rule; `la_ce` then stays closed.
- **Cost:** build 4 h, GPU 0. CPU: about 2 to 4 h per seed (S; depends on the contested-px share, measured in A0).
- **Needs:** nothing new; the F51 dumps of arm 1 for a descriptive F51 row.
- **Risks and how it could mislead:** (1) An operating-point device: it changes the class prior at decision time. It is credited only against the same model's argmax and enters the benchmark as a labelled decision layer (needs the lead's ruling; PROTOCOL 5.3 allows one crack bias only). (2) Overfit through 11 parameters on 4 folds: cross-fitting controls it; a class with few groups (splice 60 cells, edge_dark 43) can still get a noisy bias, hence the per-fold spread table. (3) **Consequence for wave 2:** `rcs` raises rare-class priors by resampling (E, T1 pre-check: inactive 2.49x, splice 2.08x). Part of any `rcs` mIoU gain can be the same prior shift. I propose that `rcs` and `la_ce` be read also against baseline + `classbias_xfit`, exactly as crack gains are read at OP-W.
- **Gated follow-up `la_ce` (P045 loss, P152, P090 as the stochastic variant in the benchmark):** CE(z + o, y) with o_c = -mean over folds and seeds of b_c for c in FREE, 0 otherwise; the offset applies to the CE term only (not the crack / inactive Dice); plain argmax at test, with no post-hoc bias on top (P045 5.3). Config key `loss.logit_offset: [24 floats]` in `ce_dice.py`, absent = byte-identical. Gate: `classbias_xfit` passes. Screen 10 runs, 11 GPU-h; primary mIoU-R13 against baseline + `classbias_xfit` (the fair comparator); build 1 h.

---

## Arm 3. `layered_ci`: a sigmoid "inactive region" layer beside the softmax

- **Papers:** P027 (region-based training), P453 (region write order, and a null on one region). Problem: inactive (crack-inactive overlap). Route new_model_code. Priority 60.
- **Primary metric:** inactive IoU at the layered decision (rule `replace`, t_I = 0.5), arm minus PF baseline, CV5-G pooled OOF.
- **Hypothesis (S):** in the softmax, inactive regions are bounded and crossed by 1 to 2 px crack labels that are jittered, and the 20% of crack px in or at inactive force a single choice. A separate sigmoid channel trained on the filled region (inactive plus the crack px in or at it) learns the region as one blob without competing with crack; the decision writes inactive where the layer fires and crack did not win.
- **Gate:** G-layer from A0. Without it the arm is not built.
- **Exact change** (flag off = no keys = byte-identical; 5-step CPU identity IDENTICAL for the house and PF cards):
  - Card keys: `model.aux_heads: {inact_region: {channels: 1, kernel: 3}}`; `data.aux_targets: [inact_region_fill]`; `loss.aux: {inact_region: {type: bce_dice, weight: 1.0}}`; `eval.decision: {name: layered_ci_replace, t_I: 0.5}`.
  - `src/models/aux_heads.py`: wrapper around the smp UnetPlusPlus core. Forward: `f = core.encoder(x)` -> `d = core.decoder(f)` (B, 16, 512, 512 with decoder_channels ending in 16) -> `z24 = core.segmentation_head(d)` (B, 24, 512, 512) and `zI = conv3x3(16 -> 1)(d)` (B, 1, 512, 512). Returns `z24` to every existing caller and `{"inact_region": zI}` through `model.aux_out` for the aux loss. The aux conv is created after the core is built, so the core's initial weights equal the baseline's at the same seed (unit test). Parameter names keep the `encoder.` prefix (PF groups unchanged).
  - `src/data/aux_targets.py` (the shared aux-target hook of WAVE2_REVIEW 3.5; if not built yet, this arm builds it): after augmentation, from the index mask `y` (512, 512):
    ```
    MI = y == 11; MC = y == 14
    R = MI | (MC & binary_dilation(MI, disk(2)))
    R = binary_fill_holes(R)
    t = R.astype(uint8); t[y == 255] = 255
    ```
    Disk and fill-holes commute with flips and rot90, so computing after augmentation equals augmenting a precomputed target.
  - `src/losses/aux_losses.py`: `bce_dice(zI, t)`: BCE-with-logits mean over px with t != 255, plus 1 - batch soft Dice of sigmoid(zI) on the same px. Total loss = house `ce_dice(z24, y)` + 1.0 x `bce_dice`.
  - `bench/decision.py`, used by the trainer's eval and by the dump writer (DESIGN 2 (d)):
    ```
    def layered_ci_replace(z24, zI, t_I=0.5):
        p0 = argmax(z24); L = sigmoid(zI) > t_I
        pred = p0.copy()
        A = (p0 == 11) & ~L;  pred[A] = argmax over classes not in {11, 14} of z24[:, A]
        B = L & (p0 != 14);   pred[B] = 11
        return pred                     # crack px identical to p0 (crack written last, never overwritten)
    ```
    Dump: `pred` from this rule; `oth` = the same rule on the 23 non-crack classes; `m_crack` from `z24` unchanged, so the writer check `pred == where(m_crack > 0, 14, oth)` holds; `p_inact` = sigmoid(zI); extra key `p_inact_softmax`.
- **Unit tests:** (1) flag-off identity; (2) core init identical to the baseline at the same seed; with the aux head attached, `z24` equals the bare core's output bit for bit; (3) target: a cell without inactive gives t = 0 everywhere even with crack; a crack line on an inactive edge is inside t, a crack 10 px away is not; a healthy hole inside an inactive ring is filled; t of an augmented mask equals the augmented t for the 8 dihedral ops on 20 real masks; ignore propagates; (4) on P532 train masks the share of crack px inside t is within 15 to 25% (E says 20% "in or at"); (5) decision (P453): crack pixel count equals argmax's on 50 dumps; with zI = -inf the result equals argmax except former inactive px; with zI = +inf every non-crack px is 11; (6) the dump writer check passes.
- **CPU pre-check:** A0 gate G-layer. Also a free proxy on existing dumps (no head yet): "union" decision `pred[(p_crack + p_inact > max other class prob) & (pred != 14)] = 11`. If this alone gains >= 0.01 inactive IoU, the mechanism (pooling crack and inactive evidence) has signal before any training (descriptive, does not open or close the arm).
- **Pathfinder:** fold 0, seed 5, 20k steps on gaint (1.1 to 2 GPU-h). Pass: finite loss; step time <= 1.15x and peak memory <= +1 GB vs the baseline smoke; the layer's held-out fold-0 region Dice >= 0.3 at 20k. Not used to rank.
- **Screen:** cv02, folds 0 to 4, seeds 5 and 6 (10 runs, 11 GPU-h), against W1-C1 seeds 5 and 6 on the same machine.
- **Readouts (pre-declared, 2 contrasts):** primary as above (between models). Mechanism readout: within the arm's own dumps, `layered_ci_replace` minus plain argmax of `z24` (no seed noise: same model). Descriptive: `union` variant (`pred[L & p0 != 14] = 11` only).
- **Should move:** inactive recall and region recall up; inactive IoU up. R: P027 5-fold CV +0.64 mean Dice, inner regions +1.0 and +2.0, outer flat; P453 region vs label 0.713 vs 0.710 on ET (no gain). S: inactive IoU 0 to +0.04, which a 2-seed screen cannot resolve (needs about 0.08).
- **Promotion and drop:** promote to the 5-seed confirmation if (between-model delta >= M_inact with the interval above 0) or (within-model delta >= 0.02 with the interval above 0 and between-model delta > 0). Drop if the within-model delta <= 0, or the between-model delta < 0, or crack strict IoU or relF1@2 falls by more than M at OP-A or OP-W.
- **Cost:** build 7 h (5 h if the shared aux-target hook exists); GPU 11 + 1.1 pathfinder; +16.5 for confirmation.
- **Needs:** nothing new (smp 0.5.0, scipy).
- **Risks and how it could mislead:** (1) operating-point shift: a layer thresholded at 0.5 can simply predict more inactive area; guard: inactive precision beside recall and the predicted / GT inactive area ratio within 0.85 to 1.15 of the baseline's; (2) the layer learns crack px near inactive as region, so where the softmax misses a crack the decision writes inactive on GT crack (FP-on-crack): report A0 bucket FP-on-crack on the arm's dumps; (3) write-order bug (P453): unit test 5; (4) shared decoder: crack guards at OP-A and OP-W; (5) no leakage path: the target comes from the training mask only, held-out masks stay strict.

---

## Arm 4. `inact_paste`: in-place inactive-region paste with matched context

- **Papers:** none in the T10 digest; mechanism reference Ghiasi et al. 2021 (arXiv 2012.07177, extra paper). Problem: inactive (data-limited, 42 train cells). Route data_pipeline. Priority 45.
- **Primary metric:** inactive IoU at OP-A, CV5-G pooled OOF, arm minus PF baseline.
- **Hypothesis (S):** if A0 shows that whole regions are missed (FN-missed dominant), inactive is limited by the 42 to 48 examples. Pasting real inactive regions (with the cracks that bound them) into other cells of the same source and cell type, at the same cell coordinates, adds contexts without new labels. This differs from the crack copy-paste that was n.d. (E, BRIEF 5): that pasted crack onto pool cells; this pastes labelled inactive regions in place, within the training fold, with decoys.
- **Gate:** G-paste from A0, then the CPU paste pre-check below. Run alone (never stacked with `rcs`).
- **Exact change** (`src/data/inact_paste.py`; hooked in `BenchmarkELDataset.__getitem__` before Albumentations; flag off = byte-identical):
  - Card keys: `data.inact_paste: {enable: true, p_paste: 0.25, p_decoy: 0.25, min_px: 100, match: [source, celltype], feather_sigma: 2.0, ring: [3, 10], max_bad_frac: 0.05}`.
  - Donor bank, built at start from the root's `splits/train.txt` only (assert: no held-out stem): every GT inactive component >= min_px; its region `R` = the A0 / arm-3 filled region (inactive + crack within 2 px + filled holes); stored: source and cell type (from `benchmark/out/cells.tsv`), bbox of `dilate(R, 3)`, image px and mask px in the bbox.
  - Per sample: a generator seeded by (seed, stream id, sample index), so the batch stream (indices) is unchanged and each pasted sample is reproducible. With p_paste: draw a donor of the same source and cell type from another cell; recipient bbox px of class padding (7) or frame (21) > max_bad_frac, or overlapping recipient inactive, means skip. Image: `gain = median(recipient ring) / median(donor ring)` over the ring 3 to 10 px outside `R` (non-inactive, non-crack px); `alpha = gaussian_filter(R, feather_sigma)` clipped to [0, 1]; `img = alpha * gain * donor + (1 - alpha) * recipient`. Mask: px in `R` take the donor's labels (inactive and crack, plus busbar / gridline px inside R as labelled); px outside R keep the recipient's labels. With p_decoy instead: the same blend of a donor bbox taken from a healthy (class 0 only) area of a donor cell, mask unchanged, so the seam alone predicts nothing.
  - SDLE has no inactive: never pasted. BMRK: donor and recipient both BMRK, so padding geometry matches.
  - Log line at start: `PASTE: donors N per source, eligible recipients M`; `paste_stats.json` in the run dir.
- **Unit tests:** (1) flag-off identity; (2) same (seed, index) gives the same pasted image and mask; (3) donor bank holds train stems only; (4) no paste across source or cell type; (5) mask after paste: R px equal donor labels, outside px equal recipient labels; a decoy leaves the mask untouched; (6) after paste the ring median ratio is within 0.9 to 1.1.
- **CPU pre-check (no GPU; decides before the screen):** on fold-0 train stems, generate 200 pastes and 200 decoys. (i) Seam test: mean |LoG (sigma 1)| in the 2 px band on the paste border, divided by the same at the donor's own region border; pass if 0.7 to 1.3 in >= 80% of pastes. (ii) Artefact test: run the W1 fold-0 PF model (seed 5) on CPU over the 400 images: its inactive recall on pasted regions must be within +/- 0.15 of its OOF recall on real inactive regions of the same sources, and its predicted inactive px on decoys at most 2x its rate on real inactive-free OOF cells. Fail = fix the blend once, then drop.
- **Pathfinder:** fold 0, seed 5 (1.1 GPU-h): step time and memory (the paste is CPU work in the loader; data-loader time must stay below the GPU step time), finite loss.
- **Screen:** 10 runs on cv02, 11 GPU-h, against W1-C1 seeds 5 and 6.
- **Should move:** inactive recall and region recall up; inactive IoU up. R (Ghiasi, abstract): +3.6 mask AP on LVIS rare categories against the 2020 challenge winner (not an ablation). S: inactive IoU 0 to +0.05.
- **Drop rule:** delta inactive IoU <= 0, or predicted inactive px on the 484 inactive-free cells up by more than 25%, or crack strict IoU / relF1@2 down by more than M (pasted regions bring their cracks).
- **Cost:** build 7 h; GPU 11 + 1.1; CPU pre-check about 1 h.
- **Needs:** nothing new.
- **Risks and how it could mislead:** (1) an inactive-prior increase (more inactive px seen) moves the operating point like `rcs`: read the arm also against baseline + the inactive bias from `classbias_xfit`; (2) the seam or the gain change becomes a cue (decoys and pre-check (ii) guard it); (3) pasted cracks add crack exposure: crack width and false alarms in the guard table; (4) leakage: donors and recipients come only from the training fold (asserted); (5) same-position paste assumes similar layouts within a source and cell type; BMRK cells are padded ELPV crops and CSIR layouts vary (S): the per-source table shows where it hurts.

---

## Measurement: how inactive and the weak classes are read with so few cells

- **Post-hoc arms (A0, 1, 2):** compared on identical predictions. The contrast changes only the px the rule or bias touches, so the seed term of the bootstrap is the spread of the rule's effect over seeds, not two independent models. These can be decided now, at 2 seeds, with the 0.01 floor.
- **Trained arms (3, 4):** inactive IoU at 2 seeds has SE about 0.038 (E), so M_inact will be near 0.08 once the A/A null exists. A screen pass on inactive is therefore rare; the arms carry two cheaper readouts: (i) arm 3's within-model decision contrast (seed-free); (ii) inactive false-alarm px on the 484 inactive-free cells (large n, measures precision) and inactive region recall (regions >= 100 px). Neither is a substitute for the primary; they decide promotion to 5 seeds.
- **Robustness of every inactive number:** leave-top-3-groups-out (PROTOCOL 5.4), BMRK row separately, fold-level values listed.
- **mIoU-R13:** per-class table always beside it; splice and edge_dark rows carry their group counts.
- **Benchmark side (P007, S):** a second, independent module-grouped split of the 532 cells would roughly double the inactive evidence per arm at 5.5 GPU-h per seed; worth it only for the final candidates.

## GPU and build totals
- Before any T10 GPU run: A0 + arms 1 and 2 = 10 build hours, 0.2 GPU-h (F51 inference).
- If G-layer opens: arm 3, 7 build h, 12.1 GPU-h. If G-paste opens: arm 4, 7 build h, 12.1 GPU-h. `la_ce` if arm 2 passes: 1 build h, 11 GPU-h.
- Worst case all open: 25 build h, about 35 GPU-h, plus 16.5 GPU-h per confirmation.

## Decisions the lead must make
1. Benchmark policy: may fitted decision layers (per-class bias, co-occurrence rules) appear as labelled entries? PROTOCOL 5.3 allows one crack bias only.
2. Read `rcs` (and `la_ce`, `inact_paste`) against baseline + `classbias_xfit` as well as raw baseline: prior shifts otherwise count as model gains.
3. F51 dumps of the W1-C1 models (0.2 GPU-h inference) for the transfer checks of arms 1 and 2.
4. Accept that trained inactive arms promote on within-model and false-alarm readouts, because a 2-seed inactive IoU screen needs about +0.08.
5. Build order: A0, arm 1, arm 2 before T10 asks for any GPU time.
