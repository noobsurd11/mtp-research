# T4 spec: label refinement and source style, 6 arms (analyst, 13 Nov 2026)

Tags: R = paper, E = our files, S = my judgement. Paper cards: `T4_label_refine_style_family.md`.
Ordered by priority. Two CPU analyses (A0a, A0b) come first; together they decide whether any GPU hour goes to this family.

## 0. Shared frame

### 0.1 Baseline and screen (fixed by the lead)
- **Baseline arm B:** `house_r34_unetpp_pf` (card md5 68c64f36), label set v1.1, roots `cv5v2_v11_f{0..4}`, seeds 5 and 6, 20k steps, batch 8, 512 px, final weights, argmax. These are wave-1 job W1a; every T4 arm reuses them and does not retrain B.
- **Screen:** cv5v2 (md5 441d118f), folds 0 to 4, seeds 5 and 6 = 10 runs per arm, about 11 GPU-h on an A6000. Out-of-fold (OOF) scores pooled over the 532 cells; two-stage paired bootstrap (330 groups of `cv5v2_groups.tsv` e44f0668, then seed per fold x arm). Optional pre-screen: fold 0, seed 5 (about 1.1 GPU-h), to catch failures only.
- **Machine rule:** every T4 arm runs on the machine that ran its W1a baseline; canonical fp32 dumps, TF32 off.
- **Held-out ground truth is never refined.** Held-out cells are always scored against v1.1 `masks_strict` + `ignore` (as the harness scorer does for every arm). A refined-label view of held-out cells exists only as a secondary, labelled view (section 0.4).
- **Sealed:** no test50, no e1_106. Unseen-module development reads only on F51 (crack and inactive) and H36 (inactive only; its crack labels are speck-level, protocol 2.5 #5).

### 0.2 Metrics each arm reports (bench_score, CPU)
Headline: crack relF1@2 with relP@2 / relR@2; strict crack IoU; inactive IoU; mIoU_rob (13 classes).
Secondary, always: crack component recall and precision (>= 20 px, 2 px rule); any-hit recall; **width ratio** = predicted crack px / GT crack px, pooled and per source; **mean predicted width** = crack px / skeleton px (skeleton on the laptop venv, skimage 0.26; gaint has no skimage); **false alarms** = crack px predicted on the 303 crack-free pool cells, and the share of crack-free cells with >= 50 predicted crack px (protocol 5.1 cell flag); per-source table (ARTS, BMRK, CFVS, CSIR, SDLE; SDLE has 17 cells, read it as descriptive only).

### 0.3 Margins
The lead fixes margins after W1a measures seed and fold noise. Until then I use provisional values (S) written as M_*: M_iou = 0.010 strict crack IoU, M_f1 = 0.010 relF1@2, M_cc = 0.020 component recall, M_src = 0.030 strict crack IoU on one source with >= 40 pool cells (ARTS 182, CFVS 169, CSIR 114, BMRK 50; E, protocol 3.2 fold table), M_inact = 0.04 inactive IoU (CV SE about 0.038, E `H21` 3). Replace each M_* by the lead's number; the rules below do not change.

### 0.4 What a refined-label arm can and cannot move (S)
- Test (held-out) labels keep their jitter: 52% of label points are more than 1 px off the darkest line (E). A model trained on ridge-centred labels predicts ridge-centred cracks; against jittered labels the expected strict IoU of a ridge-centred line is about what the baseline already gets, because the baseline averages the symmetric jitter. So **strict IoU is not the target of ridge refinement**; it is a guard (must not fall by more than M_iou).
- What should move: relR@2 and component recall of faint cracks (positives become consistent pixels on the dark line; negatives beside the crack stop contradicting them), relP@2 flat or up, mean predicted width flat, crispness (secondary view below).
- Secondary view "snapped GT": held-out labels snapped by the same deterministic, image-only script, scored for every arm and the baseline. Labelled "refined GT, secondary". Never used for a pass. It shows how much of a gap is placement, which the benchmark wants.
- Strict IoU can rise only by matching each source's width convention (arms 1, 3, 5), because test labels keep source widths (ARTS 1.5 px to SDLE 3.25 px).

### 0.5 Operating-point rule for source-aware outputs
A per-source bias, width or head is an operating-point device. Every source-aware result is reported next to (i) argmax and (ii) one global cross-fitted crack bias. The gain credited to source awareness is (source-aware) minus (global bias), never minus argmax. Source-aware entries are labelled "source-aware" in every table (source known from the file name; unseen modules = CSIR, as the protocol says).

---

## Arm 1. `src_calib`: per-source output calibration on existing OOF dumps (also pre-check A0b)
- **Papers:** 6 (zero-training control the scout proposed), 28 (style-conditioned output). Route: inference_only. Priority 88.
- **Hypothesis:** the baseline draws one compromise crack width for all sources. If a per-source crack bias or 1 px width operation, chosen by cross-fitting, raises strict crack IoU beyond a single global bias, the per-source convention is learnable and arms 3 and 5 have room. If not, the model already adapts (it can see the source: BMRK padding, contrast) and arms 3 and 5 drop in priority.
- **Input:** W1a dumps of B (`house_r34_unetpp_pf`, cv5v2_v11, seeds 5, 6): per cell `pred`, `oth`, `m_crack` (DESIGN 3.1). 532 OOF cells per seed. No GPU.
- **Code:** `bench/score_src_calib.py` (new, numpy + scipy; runs on gaint CPU or the laptop), reusing `bench_score`'s `cell_stats` / `agg` and el_metrics' bias sweep (`cell_record` on `m_crack`, `oth`).
  ```
  SRC = stem.split('_')[0]  in {ARTS,BMRK,CFVS,CSIR,SDLE}; anything else -> raise
  BIAS = arange(-4, 4.01, 0.25)                      # 33 values; applied as m_crack + b > 0
  OPS  = {erode1_cross, none, dilate1_cross, dilate1_3x3}   # morphology on (pred==14)
  def apply(cell, b=None, op=None):
      crack = (m_crack + b) > 0 if b is not None else (pred == 14)
      crack = morph(crack, op)                         # erode: crack px removed -> class oth
      out = where(crack, 14, oth)                      # (512,512) uint8
      return out
  for seed in (5, 6):
    for k in 0..4:                                     # held-out fold k
      fit = cells of folds != k (their OOF dumps, scored against their own GT)
      b_glob[k]   = argmax_b  pooled strict crack IoU(fit, b)
      for s in sources:
        n_s = crack cells of source s in fit
        b_src[k,s]  = argmax_b IoU(fit cells of s, b) if n_s >= 20 else b_glob[k]   # SDLE falls back
        op_src[k,s] = argmax_op IoU(fit cells of s, op) if n_s >= 20 else 'none'
      apply to fold k cells -> records for variants: argmax, glob_bias, src_bias, src_morph
  pool OOF records over folds; bootstrap as 0.1; contrasts: src_bias - glob_bias, src_morph - argmax
  ```
  Ties: smallest |b|. Also print b_src per fold (stability) and the width table: per source, GT label width, predicted width at argmax, at src_bias.
- **Unit tests** (`tests/test_bench_src_calib.py`): (1) b = 0 with op none reproduces `pred` records exactly (bench_score identity); (2) a synthetic set where source A's GT is the prediction dilated by 1 px: cross-fit picks dilate (or a positive bias) for A and none for B; (3) a held-out fold's cells never enter its own fit (assert stem sets disjoint); (4) SDLE fallback path taken when n_s < 20.
- **CPU pre-check:** this arm is the pre-check. Also run on `house_r34_unetpp` (non-PF W1a) to see whether PF changes the width picture.
- **Pass rule (gates arms 3, 5, 6):** pooled OOF strict crack IoU of src_bias minus glob_bias >= M_iou with the bootstrap 95% interval above 0, **or** at least one of ARTS / CFVS / CSIR / BMRK improves by >= M_src with relP@2 on that source falling by no more than 0.03. Also report: if the argmax width ratio is already within 0.9 to 1.1 for every source with >= 40 cells, write "implicit conditioning present" and lower arm 3 to priority 40.
- **What it should move:** strict IoU per source (BMRK and SDLE up through a wider output; ARTS up through a narrower one). relF1@2 roughly flat; relR@2 up and relP@2 down where widened.
- **Drop rule:** both pass conditions fail on both seeds: drop src_calib as a result, and arms 3 and 5 go to PARKED with this table as the evidence.
- **Side effects:** width ratio per source moves toward 1.0 by construction of the objective; false alarms rise on sources given a positive bias (count crack px on crack-free cells of that source; refuse a source bias that doubles them).
- **Hours:** build 4 h; GPU 0 (needs W1a dumps; scoring CPU < 1 h).
- **Needs:** W1a dumps with `m_crack`; scikit-image only for the skeleton width (laptop).
- **Risks / how it could mislead:** (1) an operating-point shift that looks like a gain; handled by crediting only src_bias minus glob_bias (0.5). (2) Per-source fit on 4 folds, applied to the 5th: no leakage, but SDLE and BMRK fits are small (BMRK 40 cells per fit, fewer with crack); the fold-to-fold spread of b_src is printed and a source with spread > 1.0 logit is reported as unstable. (3) On F51 / E1 every cell is CSIR, so this arm cannot help unseen modules much; say so.
- **Benchmark use:** a labelled "source-aware calibration" post-processing entry that any method can take; zero training cost.

---

## Arm 2. `ridge_snap`: move crack labels onto the visible dark line (trust region 2 px), keep their width
- **Papers:** 1 (guided label refinement), 38 (appearance-model evidence, variant decided on CPU), 45 (trust-region rule). Route: data_pipeline. Priority 80.
- **Hypothesis:** half the training crack label points are off the dark line by more than 1 px (E). Training on labels moved onto the line gives a consistent target, raising confidence and recall on faint cracks without changing width.
- **The exact change:** new masks for the 532 pool cells, `masks_v11_snap/`, built on CPU once; new roots `cv5v2_v11snap_f{k}` whose **train stems** link to the snapped masks and **held-out stems** to v1.1 `masks_strict` (exactly as `cv5v2_v11_f{k}` does, only the train-mask source changes). Config: `data.root=<cv5v2_v11snap_fk>` only; all other opts = card `house_r34_unetpp_pf` (+ `data.mask_ignore_value=255` as W1a). New card `t4_ridge_snap_pf.yaml` with `diff_ref: house_r34_unetpp_pf` and the expected diff = data.root only.
- **Snap script** `bench/labels/snap_crack.py` (numpy, scipy, scikit-image; laptop venv `/home/yugma/mtp/research/.venv` has skimage 0.26 and scipy; images from the 532 pool, verified against `benchmark/splits/pool532_manifest.tsv` grey-pixel md5; v1.1 masks from `benchmark/out/masks_v11/masks`). Reuse `tangents` and `profiles` from `data_analysis/scripts/annotation_consistency.py` (the code that measured the 48% figure).
  ```
  in : I uint8 (512,512); M uint8 (512,512) values 0..23, 255 (v1.1 with ignore)
  PROTECT = {1,2,3,4,5,7,9,10,15,21}   # sp multi, sp mono, dogbone, ribbons, border, padding, busbars, crack rbn edge, gridline, frame edge
  C   = (M == 14)
  Is  = gaussian_filter(I/255, 0.7)
  S   = skeletonize(C); comp = label(C, 8-conn)
  for each skeleton point p (components with >= 5 skeleton px; shorter ones unchanged):
      t = tangent(p) (PCA, radius 3, same component; skip if not line-like -> d=0)
      n = normal(t)
      prof = Is at p + d*n, d in [-2,-1.75,...,2] ; shoulders = mean Is at d in {-4,-3.5,+3.5,+4}
      d* = argmin prof
      dip = (shoulders - prof[d*]) / shoulders
      dest = round(p + d* n)
      d(p) = d*  if dip >= DIP_MIN (0.03) and M[dest] not in PROTECT and M[dest] != 255 else 0
  d~(p) = median of d over skeleton points of the same component within radius 2 of p   # no zigzag
  v(p)  = round(d~(p) * n(p)) if |d~(p)| >= 0.75 else (0,0)                              # integer move, |v| <= 2
  # move every crack pixel with the shift of its nearest skeleton point (edt indices on ~S)
  C' = { q + v(nearest_skel(q)) : q in C }, clipped to image, minus PROTECT and ignore px
  U  = M with crack px replaced by the label of the nearest pixel that is not crack and not 255  # edt indices
  M' = U ; M'[C'] = 14 ; M'[M == 255] = 255
  out: M' uint8 ; per-cell stats: n skel pts, share moved, mean |v|, |C'|/|C|, share kept for low dip
  ```
  Evidence options (`--evidence`): `profile` (above, default), `sato` (skimage `sato(I, sigmas=[1,1.5,2], black_ridges=True)`, argmax along the normal instead of argmin intensity), `myopic` (paper 38: per-source 3x3-receptive-field classifier, sklearn `HistGradientBoostingClassifier` on 3x3 normalised patches, positives = label px minus the 10% least dark, negatives = px 3 to 6 px from any crack; trained per source on the fit cells only; argmax of its score along the normal). Constants DIP_MIN, the 2 px band and 0.75 rounding are fixed here before any run; only `--evidence` is chosen, by P4 below.
- **Unit tests** (`tests/test_snap_crack.py`): (1) synthetic dark Gaussian line, FWHM 4 px, at x = 100; label 2 px wide centred at x = 101.5: after snap the label centre is within 0.5 px of 100 and its px count is within 2%; (2) label 3 px off the line: moved by at most 2 px (trust region); (3) a darker ribbon (class 4) 2 px beside a crack: no crack px lands on class 4; (4) a flat image (no dip): output equals input exactly; (5) ignore px unchanged; class counts outside crack and the vacated / occupied px unchanged; (6) idempotence: snap(snap(M)) differs from snap(M) in < 1% of crack px; (7) determinism: same md5 on two runs.
- **CPU pre-check A0a** (laptop, about 1 h compute, all on pool cells only):
  - P1 sanity: share of skeleton points within 1 px of the profile minimum rises from about 0.48 (E) to >= 0.80 after snapping. If not, the code is wrong: fix, do not drop.
  - P2 **decisive, label noise reduction on independent drawings:** pairs from `benchmark/out/label_checks_summary.txt` section 3 with both members in the pool (roles train / val only; drop every pair with a test member), image NCC >= 0.85, raw mask IoU < 0.99 (drops exact copies). About a dozen pairs, mostly CFVS (S: small and CFVS-heavy; state that). Snap each mask on its own image, align with the listed shift, compute strict crack IoU and tolerant F1@2 between the two masks before and after. **Pass:** median pair IoU rises by >= 0.05 and pooled tolerant F1@2 does not fall by more than 0.01. Secondary P2b: cells with both a `20220723` and an E-SCDD crack mask that differ (strict IoU < 0.9): same before / after test.
  - P3 cost of placement: strict IoU of snapped vs original v1.1 masks over the 532 cells, per source. This is the strict IoU a perfect snapped-label learner would get against original labels. Report; if pooled < 0.55 (below the 1 px shift ceiling 0.547 to 0.578, E), write "strict IoU likely to drop" next to the arm before it runs.
  - P4 evidence choice: run P1 to P3 for `profile`, `sato`, `myopic`. Take `profile` unless another evidence beats it on P2 median IoU by >= 0.02 and is not worse on CSIR pairs or CSIR P1 coverage. Report per source the share of points kept for low dip (CSIR expected highest: 16% of its components are < 2% darker, E).
  - **Go to GPU** only if P2 passes for the chosen evidence.
- **Screen:** 10 runs as 0.1 on `cv5v2_v11snap_f{k}`; fold-0 seed-5 pre-screen first (1.1 GPU-h). Score against original held-out labels (primary) and the snapped-GT view (secondary).
- **What it should move:** relR@2 up and crack component recall up (at relP@2 not lower by more than 0.01); relF1@2 up. Strict crack IoU within M_iou of B. Width ratio within 0.95 to 1.05 of B's. Snapped-GT view: strict IoU clearly up (expected, not a pass).
- **Drop rule:** drop if relF1@2 gain < M_f1 and component recall gain < M_cc (both seeds pooled); drop also if strict crack IoU falls by > M_iou with no relF1@2 gain >= M_f1. Keep as "benchmark refined-GT tool" regardless (the snapped-GT view).
- **Side effects:** predicted width: expected unchanged (labels keep width); a fall of more than 5% means the model became crisper than the labels and strict IoU will pay. False alarms: may rise on multi cells if the snap pulled labels onto dislocation lines or grain boundaries; check component precision on `multi` cells and crack px on crack-free cells; P3's per-source move statistics flag it in advance.
- **Hours:** build 8 h (script 4, tests 2, P1 to P4 runs 1, roots + card 1); GPU 11 (+1.1 pre-screen).
- **Needs:** scikit-image (laptop has it; on gaint only in a new isolated venv, installs approved); the 532 pool images on the laptop (pull by `gget.sh` from `labeled/images`, pool stems only, md5 vs `pool532_manifest.tsv`); `bench_make_roots.py` needs a `--train-masks <dir>` option (train stems to that dir, held-out to `masks_strict`), with the B6 asserts kept.
- **Risks / how it could mislead:** (1) leakage: none, the snap uses only each cell's own image and label, and constants are fixed in advance; the evidence choice P4 uses pool labels only, never held-out scores. (2) The snapped-GT view flatters snapped arms by design: never a pass criterion. (3) A gain in relR@2 with a width rise is a width effect, not a placement effect: compare at matched width ratio (crack bias chosen on the other folds to match B's width ratio) before crediting it. (4) If dotted or missed labels dominate the noise (22 cells with dotted labels, E), snapping alone does nothing for them; gap bridging is a separate change, not in this arm.

---

## Arm 3. `src_film`: source-conditioned decoder (FiLM on the decoder norms)
- **Papers:** 6 (conditional norm per annotation style), 28 (style-conditioned output; continuous variant after gate). Route: new_model_code. Priority 70 (40 if arm 1 reports implicit conditioning).
- **Gate:** arm 1 passes.
- **Hypothesis:** with the source as an explicit input, the decoder can draw each source's width convention, which raises strict crack IoU on BMRK / SDLE / ARTS beyond what a per-source output bias (arm 1) can do, because width can then depend on local image content, not only on a global threshold.
- **The exact change.** File `src/models/source_cond.py` (new) + 3 call sites, in `el_bench`, flag-gated:
  ```
  SRC_IDS = {'ARTS':0,'BMRK':1,'CFVS':2,'CSIR':3,'SDLE':4}; UNK = 5
  def source_ids(stems) -> LongTensor[B]: SRC_IDS[stem.split('_')[0]] (raise on unknown prefix)

  class CondBN(nn.Module):                 # wraps one nn.BatchNorm2d of the decoder
      def __init__(self, bn, n=6):
          self.bn = bn
          self.g = nn.Embedding(n, bn.num_features); self.b = nn.Embedding(n, bn.num_features)
          nn.init.zeros_(self.g.weight); nn.init.zeros_(self.b.weight)
      def forward(self, x):                # x: (B,C,H,W); self.src: (B,) set by the wrapper
          y = self.bn(x)
          return y * (1 + self.g(self.src)[:, :, None, None]) + self.b(self.src)[:, :, None, None]

  class SourceCondModel(nn.Module):
      def __init__(self, core, n=6, p_drop=0.1):
          replace every nn.BatchNorm2d under core.decoder by CondBN   # names stay under 'decoder.'
      def forward(self, x, src):          # src: (B,) long
          if self.training and p_drop > 0: src = where(rand(B) < p_drop, UNK, src)
          for m in condbn_modules: m.src = src
          return self.core(x)             # (B,24,512,512)
  ```
  - Factory: `model.source_cond.type=film`, `model.source_cond.n_sources=5`, `model.source_cond.drop=0.1`; when the key is absent nothing is wrapped. Parameter names stay `core.encoder.*` / `core.decoder.*`; check that `training.encoder_pf` still splits on the `encoder.` prefix (it matches by substring or prefix: verify, and if prefix, keep names by registering the core's children directly instead of under `core.`).
  - Dataset already returns `stem`; the trainer's training step, the in-training eval and `bench_infer` call `model(images, src=source_ids(batch['stem']))` when `cfg.model.source_cond` is set, else `model(images)` unchanged.
  - `bench_infer --source-mode {own,unk}`: `own` = the cell's source, `unk` = id 5 for every cell. Each run is dumped twice (`<run_id>__own`, `<run_id>__unk`); both are scored. Dump time is minutes.
  - New card `t4_src_film_pf.yaml` = PF card + the three keys.
- **Unit tests** (`tests/test_source_cond.py`): (1) zero-init identity: wrapped and unwrapped model with the same weights give identical logits for any src (fp32, CPU); (2) setting g[1] non-zero changes outputs only for samples with src 1; (3) `p_drop` = 0 in eval mode always; (4) flag-off 5-step CPU identity of the house and PF cards vs el_bench HEAD (IDENTICAL, the harness rule); (5) `source_ids` maps all 532 pool stems and all F51 / H36 stems to 0..4 (if `_rf` stems do not carry a source prefix, map them to CSIR and say so); (6) PF param groups: the encoder group holds exactly the same tensors as without the wrapper.
- **CPU pre-check:** arm 1 result (gate). No other.
- **Screen:** 10 runs as 0.1; pre-screen fold 0 seed 5. Two dumps per run. Comparisons: `own` vs B; `own` vs B + arm-1 src_bias (the zero-training control); `unk` vs B (source-blind cost).
- **What it should move:** strict crack IoU, pooled `own`, up by >= M_iou over B + glob_bias and over B + src_bias; per-source width ratio closer to 1.0 than B's at argmax; relF1@2 within M_f1 of B; `unk` within M_f1 / M_iou of B on everything (so the model stays usable source-blind). F51 read: `own` (= CSIR) vs `unk` vs B, crack relF1@2 and inactive IoU, descriptive.
- **Drop rule:** drop if `own` does not beat B + src_bias (arm 1) by >= M_iou pooled and no source with >= 40 cells gains >= M_src over it. A model that only matches the free calibration is not worth the code.
- **Continuous-style follow-up (paper 28), only if this arm passes:** condition on z = (cell label width - source median) / pooled sd, via a 2-layer MLP (1 -> 32 -> 2C per CondBN, init zero) added to the source embedding; train z = the cell's own measured label width; test z = 0 (source median). Same screen and drop rule against `src_film`.
- **Side effects:** width rises on BMRK / SDLE and falls on ARTS, by design; false alarms on BMRK / SDLE crack-free cells may rise with width (report per source); inactive and mIoU_rob should not move (decoder norms are shared by all classes: check mIoU_rob within 0.01).
- **Hours:** build 6 h; GPU 11 (+1.1 pre-screen).
- **Needs:** nothing new (smp 0.5.0, torch in the house venv).
- **Risks / how it could mislead:** (1) source is also visible in the image, so `unk` may already be as good as `own`; that is a valid null, report it. (2) SDLE has 17 pool cells (about 14 per training fold): its embedding is weakly trained; do not read SDLE alone. (3) Extra parameters are a few thousand (S); a capacity effect is unlikely but `unk` controls for it. (4) On F51 / E1 the source is CSIR, a mid-width source, so expect little there; the arm targets the in-distribution table.

---

## Arm 4. `oof_snap`: model-guided trust-region label refinement (nested, leak-free)
- **Papers:** 59 (model-based correction of misplaced crack labels), 45 (foundation-model guidance inside a trust region; here the guide is a crack model, the FM swap stays open). Route: data_pipeline. Priority 50.
- **Gate:** arm 2 passes its screen on at least one headline metric, **or** A0a shows the image evidence fails where it matters (CSIR share of points kept for low dip > 0.30 while P2 passes on CFVS).
- **Hypothesis:** a crack model's margin is a better guide than raw intensity where the dark line is faint or confounded (CSIR, multi-crystalline texture), so labels move to where a model trained on other cells sees the crack.
- **The exact change:** the arm-2 script with `--evidence oof` and the evidence map E = m_crack from a model that saw neither the cell nor the screen's held-out fold.
  ```
  for screen fold k:
      T = cells of folds != k (the 4 training folds); split T into halves H1, H2 by fold
          (folds sorted, alternate: e.g. k=0 -> H1 = folds {1,3}, H2 = {2,4}); groups never cut
      train h1 = PF recipe on H1 (seed 5), dump m_crack on H2;  train h2 on H2, dump on H1
      refined train masks for screen fold k = snap(T labels, evidence = those cross-fitted m_crack)
      write masks_v11_oofsnap_f{k}/ (train stems only) ; root cv5v2_v11oofsnap_f{k}
  snap rule along the normal: d* = argmax over d in [-2,2] of m_crack(p + d n);
      accept if m_crack(p + d* n) > 0 (the model predicts crack there) else d = 0; same smoothing,
      rounding, PROTECT, ignore and width-keeping as arm 2
  ```
  Roots: train stems of fold k to `masks_v11_oofsnap_f{k}`, held-out to `masks_strict` (needs the same `--train-masks` option as arm 2, per fold).
- **Unit tests:** arm-2 tests with a synthetic m_crack map in place of the image; plus a leakage test: for every k, the stems used to train h1, h2 contain no stem of fold k (assert), and every refined stem's evidence came from the model that did not train on it.
- **CPU pre-check:** P1 to P3 of A0a with `--evidence oof` on the fold-k refinement outputs (after the 10 helper runs, before the screen). Pass as in arm 2 P2 (pairs whose members both lie in the training folds of that k).
- **Screen:** helper runs 10 (5 folds x 2 halves, seed 5, about 11 GPU-h, on half-size training sets) + the arm's 10 screen runs (11 GPU-h).
- **What it should move:** as arm 2, with the CSIR rows as the deciding table: relR@2 on CSIR up by >= M_cc over arm 2.
- **Drop rule:** drop if it does not beat arm 2 (not B) by M_f1 on relF1@2 or M_cc on component recall pooled; drop if CSIR relR@2 is not above arm 2.
- **Side effects:** confirmation bias: labels move toward what models already predict, so predicted width can shrink (labels drawn on the model's peak) and missed cracks stay missed (labels the model does not see are not moved, d = 0, so they are at least kept). False alarms: unchanged by construction (no label px is added).
- **Hours:** build 4 h (reuses arm 2); GPU 22.
- **Needs:** as arm 2.
- **Risks / how it could mislead:** (1) leakage if the helper models saw the held-out fold: the nested split above prevents it; never use W1a's OOF dumps for this (their models trained on folds that include the screen's held-out cells). (2) Helper models trained on about 213 cells are weaker; acceptable for a 2 px move, state it. (3) The FM-guided version (paper 45) stays open: swap E for any stronger crack model's cross-fitted margin when one exists.

---

## Arm 5. `src_cm`: per-source crack confusion model on top of the latent prediction
- **Papers:** 47 (per-annotator pixel confusion matrices with trace regulariser), 35 (annotator preference heads; its stochastic-error part stays parked). Route: new_loss. Priority 45.
- **Gate:** arm 1 passes, and arm 3 has been read (run arm 5 if arm 3 passes on `own` but its `unk` output loses > M_f1 relF1@2 against B, or if arm 3 fails while arm 1 passed; otherwise park it).
- **Hypothesis:** separating "what the source's annotator draws" from "where the crack is" gives two outputs from one model: a latent map that is source-neutral (for relF1@2, F51, E1) and a source map that reproduces each width convention (strict IoU).
- **The exact change.** File `src/losses/source_cm.py` (new) + a head in `source_cond.py`:
  ```
  z    = core(x)                                   # (B,24,H,W) latent logits
  f    = core.decoder output features             # (B,16,H,W) (smp U-Net++ last decoder channels; check)
  cm   = Conv2d(16, 2*5, 1)(f)                    # init: weight 0, bias a-channels +4, b-channels -6
  a_l, b_l = gather channels (2*src, 2*src+1)     # (B,1,H,W) each, per sample's source
  a = sigmoid(a_l)   # P(label crack | true crack)
  b = sigmoid(b_l)   # P(label crack | true not crack)
  p  = softmax(z); pc = p[:,14]
  qc = a*pc + b*(1-pc)
  q  = p * (1-qc)/(1-pc+1e-6) for k != 14 ; q[:,14] = qc     # noisy distribution, sums to 1
  loss = NLL(log q, mask, ignore 255) + DiceSoft(q, mask, classes (14,11)) + lam * mean(a + (1-b))
  ```
  Config: `model.source_cm.type=binary`, `loss.source_cm.lam=<chosen>`; supervised loss otherwise as `ce_dice` (same Dice classes and weight) but evaluated on q. Outputs: `latent` = argmax z; `own` = argmax log q with the cell's source. `bench_infer --source-mode {latent,own}` writes both dumps (m_crack from z, or from log q).
  - lam choice without held-out metrics: run fold 0 seed 5 for 2k steps at lam in {0.01, 0.1}; pick the largest lam for which, on training batches at step 2k, mean a over GT crack px >= 0.5 and mean b over px more than 5 px from any crack label <= 0.01. Log both statistics every 500 steps in the real runs.
- **Unit tests:** (1) at init (a about 0.982, b about 0.0025) q differs from p by < 0.02 on crack and the loss is within 2% of the house `ce_dice` on a fixed batch; (2) q sums to 1 per pixel, q >= 0; (3) gradient reaches both z and the cm head; (4) a source's cm channels get zero gradient from samples of other sources; (5) flag-off identity (5-step CPU) unchanged.
- **CPU pre-check:** arm 1 (gate); the lam diagnostics above (training statistics only, 2 x 0.12 GPU-h).
- **Screen:** 10 runs as 0.1; two dumps each.
- **What it should move:** `own`: strict crack IoU up by >= M_iou over B + src_bias, as arm 3. `latent`: relF1@2 not below B by more than M_f1 and, on F51, crack relF1@2 at or above B (descriptive). Width: `own` width ratio near 1.0 per source; `latent` width ratio below `own` (thinner, closer to the true line).
- **Drop rule:** drop if `own` does not beat B + src_bias by M_iou and `latent` does not beat B on relF1@2 by M_f1. Drop if a collapses (< 0.3 on GT crack) or b explodes (> 0.05 far from cracks) in the logged statistics.
- **Side effects:** `latent` thinner than labels: strict IoU of `latent` will be lower than `own`; do not score `latent` on strict IoU as a headline. False alarms: `own` can widen around every predicted crack for BMRK / SDLE.
- **Hours:** build 8 h; GPU 11 (+0.25 lam diagnostics, +1.1 pre-screen).
- **Needs:** nothing new. Reference code (MIT badge, unverified licence text): github.com/moucheng2017/Learn_Noisy_Labels_Medical_Images `Loss.py` for the trace term; re-implement, do not import.
- **Risks / how it could mislead:** (1) source and domain are confounded and there is one label per cell, so the latent / noisy split is not identifiable in principle; the trace term picks one split. The latent output is a model choice, not "the true crack". (2) The 2 x 2 model cannot express a 1 px shift, only widening / thinning; it targets width only. (3) The rare-class imbalance (crack 0.19% of px) can drive b up near every dark structure; the b statistic guards this.

---

## Arm 6. `snap_film`: stacked arm (refined labels + source conditioning)
- **Papers:** 1, 6. Route: training_recipe (combines arm 2's roots with arm 3's card). Priority 30.
- **Gate:** arms 2 and 3 both pass their own screens.
- **Why stack (S):** the two mechanisms act on different errors: arm 2 on placement, arm 3 on width. If both pass, the combination is the candidate for the final model, and the only test of whether the gains add.
- **The exact change:** card `t4_snap_film_pf.yaml` = `t4_src_film_pf` with `data.root=<cv5v2_v11snap_fk>`. No new code.
- **CPU pre-check:** none.
- **Screen:** 10 runs as 0.1; dumps `own` and `unk`.
- **What it should move:** relF1@2 at least arm 2's gain and strict crack IoU (`own`) at least arm 3's gain, both against B.
- **Drop rule:** drop if it does not beat the better single arm on that arm's own headline metric by M_f1 / M_iou; then the final model takes the better single arm.
- **Side effects:** as arms 2 and 3 (width follows the source; false alarms as arm 3).
- **Hours:** build 1 h; GPU 11.
- **Risks:** an additive reading needs both singles from the same machine and seeds; otherwise report the stack as a candidate only.

---

## Order of work and total cost (S)
1. A0a (arm 2 pre-check, laptop CPU) can start now: needs only pool images and v1.1 masks. Build arm 2's script and roots in parallel.
2. Arm 1 (`src_calib`) as soon as W1a dumps exist. It decides arms 3, 5, 6.
3. GPU: arm 2 (11 + 1.1) if P2 passes; arm 3 (11 + 1.1) if arm 1 passes; then arms 4, 5, 6 by their gates.
- Total if every gate opens: GPU about 70 h (arm 2 12.1, arm 3 12.1, arm 4 22, arm 5 12.35, arm 6 11); build about 31 h. If only arm 1 and arm 2 run: 12 GPU-h, 12 build hours.

## Benchmark outputs of this family (S)
- A deterministic, image-only crack label refiner (arm 2 script) and the "refined GT" secondary scoring view, with the GT-only reference rows (snapped vs original IoU per source, P3).
- A "source-aware calibration" post-processing entry (arm 1) that any method can take, and the rule that source-aware entries are labelled and compared against a global cross-fitted bias.
- Per-source width table (label width, predicted width) for every method: the benchmark's width flag broken down by source.
- Controlled-jitter study (paper 59's Syncrack idea): apply measured jitter (48% within 1 px) to snapped held-out labels and report how each method's strict IoU moves; CPU only; benchmark track, no score claim.
