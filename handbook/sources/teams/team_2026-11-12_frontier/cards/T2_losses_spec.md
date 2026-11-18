# T2 loss arms: experiment specification

Analyst T2, 13 Nov 2026. Paper evidence and statuses: `T2_losses_family.md`. Ledger: `ledger/T2.tsv`.
Tags: R = paper, E = our files, S = my judgement. Everything here is a proposal for the el_bench worktree (`/home/noob/work/el_bench`, branch `bench`); nothing is built yet.

## 0. Common frame (applies to every arm)

### 0.1 Baseline and screen
- **Baseline arm:** method card `house_r34_unetpp_pf` (U-Net++ / ResNet-34, PF fine-tune: encoder frozen 1k steps, then 0.1x lr, no encoder wd), label set v1.1, 20k steps, batch 8, 512 px, Adam 1e-3, CE + Dice{14, 11}, final weights, argmax. Every arm = baseline + exactly the change listed. Same commit, same machine type, same precision for arm and baseline (DESIGN 3.1).
- **Screen:** split `cv5v2` (md5 441d118f) on roots `cv5v2_v11_f{0..4}`, seeds 5 and 6, 10 runs per arm; held-out folds dumped in canonical fp32; out-of-fold (OOF) scores pooled over the 532 cells; two-stage group bootstrap (330 groups of `cv5v2_groups.tsv`, then seed). Baseline = W1a's PF runs (same 10 cells of the design).
- **Pre-screen (optional, 1 run):** fold 0, seed 5, full 20k steps. Kill only on obvious failure: NaN / divergence, crack IoU on fold 0 below baseline seed 5 by more than 0.05, or predicted / GT crack px outside 0.6 to 1.6. Never used to rank.
- **Sealed:** no test50, no E1. Unseen-module development reads only on F51 (and H36 for inactive only; H36 crack labels are speck-level, E BRIEF 2).

### 0.2 What every arm reports (from the dumps, CPU)
- Headline: crack relF1@2, relP@2, relR@2; strict crack IoU; inactive IoU; mIoU_rob (13 classes).
- Secondary: crack component recall (>= 20 px, >= 50% within 2 px), any-hit recall, component precision; **width ratio W = predicted crack px / GT crack px** (OOF pooled; house on test 0.95, Skeleton Recall w 1.0 1.54, E PROTOCOL 5.1); **false-alarm px on crack-free cells** (303 crack-free cells in P532, E PROTOCOL 3.2); per-source table (ARTS, BMRK, CFVS, CSIR, SDLE); gridline (15) IoU.
- **Matched operating point (mandatory, guards against bias-shift "gains"):** sweep the crack bias b over -4..+4 on `m_crack` / `oth` (dump format, DESIGN 3.1) and report (a) relR@2 of the arm at the baseline's argmax relP@2, (b) relP@2 of the arm at the baseline's argmax relR@2, (c) the cross-fitted bias point (bias chosen on the other four folds, DESIGN 3.2). A gain at argmax that vanishes at (a) and (b) is an operating-point shift and does not pass.
- Margins: the lead fixes them from the baseline wave's seed and fold noise. Below, `M_F1`, `M_IoU`, `M_cc`, `M_in`, `M_miou` are those margins for relF1@2 / relR@2 / relP@2, strict crack IoU, component recall, inactive IoU, mIoU_rob. If the lead has none yet, my placeholders (S, from the test-set 5 v 5 detection limits, E PROTOCOL 5.4; CV at 2 seeds is untested): M_F1 0.013, M_IoU 0.012, M_cc 0.020, M_in 0.04, M_miou 0.01.
- **Common guards (any arm):** drop if W rises by more than 15% relative to baseline without a relF1@2 gain >= M_F1; drop if crack-free-cell false-alarm px rise by more than 1.5x; drop if inactive IoU falls by more than M_in or mIoU_rob by more than M_miou (unless the arm's target is crack and the lead accepts the trade).

### 0.3 Shared infrastructure (build once, about 4 h; DESIGN 7 step 8)
1. **Aux target hook.** `src/data/aux_targets.py`: `AuxTargetDataset(ds, builders)` wraps the labelled training dataset exactly like el_thin's `TubedSkeletonDataset`: it calls the wrapped `__getitem__`, then each builder adds a key computed from the *augmented* `mask` (numpy, CPU worker). It draws no random numbers, so `BatchStream` batches are unchanged. Builders are registered by name; the loss declares `aux_keys`.
2. **Trainer call.** In the supervised step (trainer l.466-473), replace `sup_criterion(logits, masks)` by `sup_criterion(logits, masks, **{k: batch[k].to(dev, non_blocking=True) for k in getattr(sup_criterion, "aux_keys", ())})`. Empty tuple for the house loss, so flag-off runs are unchanged. The val loss path calls without aux; each loss must then build its targets from `targets` on the CPU (as thin does) or skip its extra term in eval.
3. **All extra terms in float32 with autocast disabled**, ignore 255 excluded, as `ThinCrackLoss` does. Each term logged in `last_terms`.
4. **Identity test:** the 5-step CPU identity script (`identity_cpu.py` 962379a6) for house and PF with every T2 flag absent must print IDENTICAL against e544133 (LEAD "Decisions in force").
5. Config: each arm lives under its own key (below). Factory rule: absent key or weight 0 = the house `CEDiceLoss` object, unwrapped.

### 0.4 Arms in priority order
| # | Arm | Papers (rank) | Route | Build h | Screen GPU-h | Priority | Status |
|---|---|---|---|---|---|---|---|
| A1 | `soft_band_jml` | JML (8), SVLS (41); GeoLS (63) as gated variant | new_loss + target hook | 4 | 11.5 | 85 | run now |
| A2 | `ens_kd_jml` | JML-KD (8), TopoMortar self-distillation (24) | training_recipe | 5 | 18 to 29 (+16.5 teacher seeds, shared with baseline) | 80 | after gate G5 |
| A3 | `clce_crack` | clCE (70) | new_loss | 2 | 12 | 70 | run now |
| A4 | `scnp_cedice` | SCNP (34) | new_loss | 2 | 12.5 | 65 | run now |
| A5 | `cc_dicece_crack` | CC-DiceCE (74); multi-class (82) as gated variant | new_loss + target hook | 4 | 12 | 60 | run now |
| A6 | `coletra_crack` | CoLeTra (36) | data_pipeline | 4 | 11 | 55 | run now |

Why not more loss arms (S): Lovasz, Jaccard on hard labels, focal and Tversky are config rows for the benchmark suite (BENCH_ONLY): on hard labels Jaccard is a monotone rescaling of the house Dice per batch (J = D / (2 - D)), Lovasz rewards the same pooled IoU, and Tversky tied CEDice on Crack500 / TopoMortar in SCNP's tables (R). T-Loss is BENCH_ONLY (its robustness is per image, not per pixel; family card 5). RankED, DconnNet, snakes are PARKED for cost.

Stacking (S): after the singles, one stacked arm of the passing arms (most likely A1 + A3 or A1 + A6) at the same budget; not specified here because it depends on which pass.

---

## A1. `soft_band_jml`: soft crack band + soft CE + Jaccard metric loss (priority 85)
**Papers:** JML (8), SVLS (41). GeoLS (63) is the gated variant A1g.
**Hypothesis (S):** labels jitter by about 1 px, so a hard one-hot target punishes a prediction that sits on the true ridge but 1 px off the drawn line. A soft crack band with measured strength removes that penalty; JML1 is minimised at the soft target (R, JML), unlike the house soft Dice, which pushes soft targets to 0/1. Expected: strict crack IoU and relF1@2 up, width at argmax unchanged because band values stay below 0.5.
**Why this is one arm and not two (S):** soft targets with the house Dice are broken (Dice is not minimised at a soft target, R JML Sec. 3); JML with hard targets equals soft Jaccard, a per-batch monotone rescaling of the house Dice, so it is not worth a run on its own. The pair is the smallest testable unit.

**Exact change**
- Config (new keys):
  ```yaml
  loss:
    supervised: soft_ce_jml
    soft_ce_jml:
      jml_classes: [14, 11]
      jml_weight: 1.0        # house Dice weight, kept
      jml_smooth: 1.0        # house Dice smooth, kept
      jml_reduce: batch      # sums over the whole batch (JML paper mIoUD; house Dice already does this)
      soft_target:
        kind: crack_band     # A1g: crack_band_geo
        cls: 14
        radius: 2.0          # px, Euclidean
        a: 0.5               # default; replaced by the P1 fit if P1 runs
        sigma: 1.0           # px
        zero_on: [11, 255]   # no band on inactive or ignore px
  ```
- Target builder `crack_band` (file `src/data/aux_targets.py`), per augmented mask `m` (H, W) int64:
  ```
  yc = (m == 14)                                   # bool (H, W)
  if not yc.any(): t = zeros(H, W, float16)
  else:
      d = scipy.ndimage.distance_transform_edt(~yc)    # px to nearest crack px
      t = where(yc, 1.0, where(d <= radius, a * exp(-d**2 / (2 * sigma**2)), 0.0))
      t[isin(m, zero_on)] = 0.0                    # inactive and ignore get no band (yc px are never 11/255)
  return {"crack_soft": t.astype(float16)}          # (H, W)
  ```
  With a 0.5, sigma 1: t = 0.303 at d 1, 0.184 at d sqrt 2, 0.068 at d 2, 0 beyond.
- Loss `SoftCEJML` (file `src/losses/soft_ce_jml.py`), logits z (B, 24, H, W), targets m (B, H, W), crack_soft t (B, H, W):
  ```
  z = z.float(); V = (m != 255)                                    # (B, H, W)
  Y = one_hot(m.clamp(max=23), 24).permute(0,3,1,2).float() * V[:,None]   # (B, 24, H, W)
  band = (t > 0) & (m != 14) & V                                   # px that receive crack mass
  Q = Y * (1 - t*band)[:,None];  Q[:,14] += t*band                  # rows sum to 1 on valid px; crack px stay one-hot
  logp = log_softmax(z, 1);  P = logp.exp()
  ce = -(Q * logp).sum(1)[V].mean()                                # soft CE over valid px
  jml = mean over c in jml_classes of:
        p = P[:,c]*V;  q = Q[:,c]
        S = p.sum() + q.sum();  D = (p - q).abs().sum()
        1 - (S - D + smooth) / (S + D + smooth)                    # JML1 (R), batch-level
  loss = ce + jml_weight * jml
  aux_keys = ("crack_soft",)
  ```
  Memory: Q is 8 x 24 x 512 x 512 float32 = 201 MB (fine on 48 GB; on gaint 32 GB check the smoke peak).
- Switch: `loss.supervised=soft_ce_jml`; house runs untouched.
- **Unit tests** (`tests/test_t2_soft_ce_jml.py`): (1) a = 0: `ce` equals `F.cross_entropy(z, m, ignore_index=255)` to 1e-6 and `jml` equals `1 - (2I + 1) / (2(P + Y - I) + 1)` computed independently; (2) metric property: with smooth 0 and soft q, JML(q, q) = 0 and JML(q + e, q) > 0 for small e; house soft Dice at p = q is > 0 (documents why Dice was replaced); (3) band values on a synthetic 1 px vertical line: t at d 1 = 0.3033, d 2 = 0.0677, d 3 = 0, and 0 on px labelled 11 or 255; (4) rows of Q sum to 1 on valid px; (5) `AuxTargetDataset` returns images and masks byte-identical to the unwrapped dataset for 20 (idx, seed) pairs; (6) flag-off CPU identity IDENTICAL.

**CPU pre-check P1 (calibrates a, sigma; can kill):** on the 532 pool cells (masks open), compare the 2021 masks (`masks_coded`) with the revised masks (`masks_escdd`). For each ring of Euclidean distance d in {1, sqrt 2, 2, sqrt 5, 2 sqrt 2} around the revised crack mask (excluding px that are crack in both), compute r(d) = share of ring px that are crack in the 2021 mask; repeat on the 22 same-cell stage pairs (E PROTOCOL 5.2) after their alignment. Fit t(d) = a exp(-d^2 / (2 sigma^2)) to r(d) for d in [1, 2]. Pass rule: if r(1) >= 0.02 in both sources, run A1 with the fitted a, sigma, capped so t(1) <= 0.45; if r(1) < 0.02 in both, the jitter model is not supported by our own labels: drop A1 (S). If only one source supports it, run with the default a 0.5, sigma 1.0 and record that. Script: about 60 lines, scipy only, gaint CPU or laptop; output a table r(d) per source (ARTS, CFVS, CSIR, BMRK, SDLE), because label width differs by source (1.5 to 3.25 px, E BRIEF 2).

**Screen:** as 0.1, 10 runs.
**Should move:** strict crack IoU up and relF1@2 up (both). Expected W within 0.95x to 1.10x of baseline.
**Drop rule:** drop if neither strict crack IoU gains >= M_IoU nor relF1@2 >= M_F1 at argmax, or if the gain is absent at the matched operating point (0.2 a, b), or if relP@2 falls by more than M_F1, or any common guard trips.
**Cost:** build 4 h (plus the shared 4 h); screen 10 runs x 1.15 GPU-h = 11.5 GPU-h; pre-check CPU < 1 h.
**Needs:** nothing new (scipy present).
**Risks / how it could mislead:**
- Soft targets shift calibration: crack probabilities inside the band rise to about 0.3, so the cross-fitted bias moves; that is why the matched-operating-point read is required.
- The band adds crack mass beside the line; if 24-way argmax splits the remaining 0.7 between two classes (gridline beside crack), crack can win at 0.3 and widen predictions. Watch W and per-source W (BMRK labels are 3 px wide already).
- The 2021 vs 2022 disagreement in P1 mixes relabelling with jitter; P1 calibrates, it does not prove the jitter model.
- No leakage path: targets come from the training mask only; held-out folds never pass through the hook.

**Variant A1g `soft_band_jml_geo` (GeoLS, run after gate):** identical except `kind: crack_band_geo`: d is the geodesic distance from the crack mask on the image intensity, inside a 5 px Euclidean band: graph on the band px with 8-neighbour edges, edge cost = step length x (1 + lambda |I_u - I_v| / s_I), s_I = robust std of the cell's intensity, lambda 10 (S; GeoLS's own cost form not verified), shortest paths by `scipy.sparse.csgraph.dijkstra` with all crack px as sources. Precompute once per training cell before training (the geodesic needs the un-augmented image; store d as float16 per stem and apply the same dihedral transform as the mask by registering it as an extra mask target in the Albumentations Compose). **Gate:** A1 not dropped, and pre-check P1g passes: on train crack cells, the t-weighted mean normalised intensity of band px is lower (darker) for the geodesic band than for the Euclidean band in >= 70% of cells, and the share of band mass on gridline / busbar px (15, 9) is not higher by more than 5 points. Cost: build 3 h, CPU precompute < 1 h, screen 11.5 GPU-h.

---

## A2. `ens_kd_jml`: distil the fold's PF ensemble with soft CE + JML (priority 80, after gate G5)
**Papers:** JML-KD (8), TopoMortar self-distillation (24).
**Hypothesis (S):** the 5-seed ensemble is the only clear win so far (+0.014 to +0.018 crack IoU on test, E BRIEF 3/5). A single student trained on the ensemble's soft maps should recover part of that gain at single-model cost, and the soft maps encode the jitter better than a hand-made band. TopoMortar's self-distillation lowered Betti errors under noisy labels (noisy + SD CEDice beta0 6.2 -> 2.4, R); JML-KD beat JML alone by +0.63 to +1.47 mIoU on VOC (R).

**Exact change**
- Teachers for fold k = the PF runs on root `cv5v2_v11_f{k}` (W1a seeds 5 and 6; plus seeds 7, 8, 9 if the lead adds them; they double as extra baseline seeds for the noise estimate). Loaded once in the trainer (`model.eval()`, `requires_grad_(False)`), final weights. **Assert** for every teacher: its `data.root` and `splits/train.txt` md5 equal the student's (no teacher has seen the student's held-out fold).
- Online targets: on each augmented batch, `T = mean_j softmax(teacher_j(x))` in bf16 autocast under `torch.no_grad()`, cast to float32 (B, 24, H, W). Temperature 1.
- Config:
  ```yaml
  loss:
    supervised: soft_ce_jml
    soft_ce_jml: {jml_classes: [14, 11], jml_weight: 1.0, jml_smooth: 1.0, jml_reduce: batch, soft_target: null}
  kd:
    teachers: [<run_dir_f{k}_s5>/latest.pth, <run_dir_f{k}_s6>/latest.pth]   # resolved per fold by the job builder
    weights_key: model
    lambda: 0.5
  ```
- Loss (reuses `SoftCEJML` with Q given explicitly):
  ```
  Lhard = SoftCEJML(z, m, Q = onehot(m))                    # = CE + JML on hard labels
  Q_kd  = T * V[:,None]                                      # teacher distribution on valid px
  Lsoft = SoftCEJML(z, m, Q = Q_kd)                          # soft CE + JML on crack, inactive (JML active classes: ALL of the two)
  loss  = (1 - lambda) * Lhard + lambda * Lsoft
  ```
  Ignore px excluded from both. Student seeds 5 and 6 (paired with the baseline's seeds), PF recipe, 20k steps.
- **Unit tests:** (1) lambda 0 equals the A1 loss with a 0; (2) a teacher identical to the one-hot labels gives Lsoft == Lhard; (3) teacher loading asserts fire on a mismatched root; (4) teacher forward under no_grad leaves no grad on teacher params; (5) the batch stream is unchanged (teachers draw no random numbers).

**Gate G5 (CPU, after W1a):** (a) W1a PF runs for all 5 folds exist with dumps; the 2 PF seeds are dumped on their held-out folds with `logp` (DESIGN 3.1 optional key; about 13 GB for 532 cells x 2 seeds); (b) the OOF 2-seed ensemble (mean softmax, argmax) beats the mean of the two single seeds by >= 0.005 on strict crack IoU or relF1@2 (if the ensemble gains nothing in CV, there is nothing to distil: drop); (c) teacher not a copy of the labels: on 50 training cells of fold 0 (open), the share of crack-label px with teacher p_crack in (0.1, 0.9) is >= 10%, or the teacher's in-sample crack IoU is <= 0.85. If (c) fails, run the cross-fitted variant (teacher for a training cell taken from a model that did not train on it; needs nested folds, cost about 4x) only on the lead's call.
**Pre-check:** G5 is the pre-check.
**Screen:** as 0.1, 10 student runs. Two teachers per fold: about 1.8 GPU-h per run (three U-Net++ forwards per step, S), 18 GPU-h; five teachers about 2.9 GPU-h per run, 29 GPU-h, plus 15 extra PF teacher runs (16.5 GPU-h) that also serve as baseline seeds 7 to 9.
**Should move:** strict crack IoU up and relF1@2 up (towards the OOF ensemble's value); inactive IoU flat or up.
**Expected side effects:** W up by 5 to 15%: the test ensemble predicts more crack px than single models (pixel P / R 0.621 / 0.703 vs 0.644 / 0.642, so W about 1.13 vs 1.00, E BRIEF 3). False alarms on crack-free cells flat or down (averaging suppresses isolated single-seed blobs, S).
**Drop rule:** drop if the student's strict crack IoU gain < M_IoU and relF1@2 gain < M_F1, or if the student recovers less than a third of the OOF ensemble's own gain on both, or a common guard trips.
**Cost:** build 5 h (teacher loading, assert, job builder that resolves teacher paths per fold). GPU as above.
**Needs:** W1a PF checkpoints kept (not slimmed) until A2 runs: 10 x 499 MB (E DESIGN 1.7).
**Risks / how it could mislead:**
- Leakage: a teacher trained on a different fold's training set has seen the student's held-out cells. The root/md5 assert is the guard; it must fail closed.
- Seed coupling: student seed 5 and teacher seed 5 share the init and batch stream; the student could copy its own init's teacher. Acceptable for a screen; note it. If it passes, confirm with student seeds 15, 16.
- A gain here is an ensemble gain moved into one model; it must be compared with the 2-seed (or 5-seed) ensemble itself in the benchmark (deployment-cost track), not sold as a new loss.

---

## A3. `clce_crack`: centerline cross-entropy on the crack class (priority 70)
**Paper:** clCE (70).
**Hypothesis (S):** CE averaged over the label skeleton (recall side) plus CE averaged over the predicted soft skeleton (precision side) lifts crack component recall and relR@2 like Skeleton Recall did on E1, while the predicted-skeleton term keeps thin false lines down, which Skeleton Recall lacked (R: clCE raised DSC and clDice on all 8 vessel sets; E: Skeleton Recall w 1.0 doubled E1 false-alarm px).

**Exact change**
- Config: `loss.supervised: ce_dice` (house) plus
  ```yaml
  loss:
    clce: {weight: 0.25, cls: 14, pred_iters: 3, norm: skeleton_mass}
  ```
  Weight 0.25 (S): between SKR w 0.1 (narrow E1 pass, no false-alarm cost) and w 1.0 (widening); clCE's log penalty is steeper than Skeleton Recall's linear recall, so a lower weight than the paper's 1 is used.
- Target builder `crack_skel` (aux): `tubed_skeleton(m, 14, radius=0)` from el_thin's `src/data/skeleton.py` (exact Zhang-Suen, equals skimage, E handbook) -> uint8 (H, W).
- Loss term (file `src/losses/clce.py`, wrapper around the house `CEDiceLoss` like `ThinCrackLoss`):
  ```
  base = house_ce_dice(z, m)                                    # unchanged
  V = (m != 255).float()
  lce = F.cross_entropy(z.float(), m, ignore_index=255, reduction="none") * V   # (B, H, W), 24-class CE
  p = softmax(z.float(), 1)[:,14] * V                            # (B, H, W)
  ST = crack_skel.float()                                        # (B, H, W)
  SP = soft_skel(p[:,None], iters=pred_iters)[:,0]               # el_thin soft_skel (clDice Alg. 1); NOT detached (paper code)
  L_rec  = (lce * ST).sum() / ST.sum().clamp(min=1)              # paper Eq. 5 ("CE-Tprec" in the paper's naming)
  L_prec = (lce * SP).sum() / (SP.sum() + 1e-6)                  # paper Eq. 6
  loss = base + weight * (L_rec + L_prec)
  aux_keys = ("crack_skel",)
  ```
  Batch without crack: L_rec = 0, L_prec still penalises predicted crack skeleton mass (wanted on crack-free cells). Normalisation by skeleton mass follows the paper's equations, not its Code 1 (`.mean()` over all px, about 500x weaker on a 0.19% class; family card 9).
- Switch: `loss.clce.weight > 0`; absent = house object.
- **Unit tests:** (1) weight 0 -> house loss object unchanged (identity); (2) on a synthetic 1 px line with p = one-hot labels, L_rec and L_prec are both ~ -log(1) = 0 within 1e-5; (3) a false 1 px line in a crack-free image with p 0.9 gives L_prec > 1 and L_rec = 0; (4) `soft_skel` of a 3 px wide bar with iters 3 peaks on its centre row; (5) gradients flow to z through both terms (autograd check).

**CPU pre-check:** none decides it. A cost check in the 1,000-step smoke: step time within 1.15x of the house.
**Screen:** as 0.1. Also read F51 crack relF1@2 and component recall descriptively (the motivation is unseen modules).
**Should move:** crack component recall up (>= M_cc) and relR@2 up, with relP@2 within M_F1 of baseline; strict IoU flat.
**Expected side effects:** W up 0 to 25% (S: the predicted-skeleton term does not punish a wide prediction centred on the label, because its skeleton stays on the label); crack-free-cell false alarms flat or down.
**Drop rule:** drop if component recall gain < M_cc and relR@2 gain at matched relP@2 < M_F1, or W rises > 15% with relF1@2 gain < M_F1, or crack-free false alarms rise > 1.5x.
**Cost:** build 2 h; screen 10 x 1.2 GPU-h = 12 GPU-h.
**Needs:** el_thin's `soft_skel` and `skeleton.py` (already cherry-picked into el_bench).
**Risks / how it could mislead:** recall bought with width (the Skeleton Recall failure mode); judge relR@2 at matched relP@2, never pixel recall. The skeleton of a 1 to 2 px jittered label is the label itself, so the recall term is close to a reweighted CE on crack px; if A3 equals "CE with crack weight about 500", that is a finding, not a topology effect.

---

## A4. `scnp_cedice`: same-class neighbour penalisation added to the house loss (priority 65)
**Paper:** SCNP (34).
**Hypothesis (S):** replacing each logit by its worst same-label neighbour (3 x 3) before a second house loss penalises gaps along a crack line and crack bleed beside it. On Crack500 this kept Dice (0.68) and cut beta0 errors 10.61 -> 9.32 (R). For us: fewer broken cracks and narrower predictions; gridline continuity as a side effect.

**Exact change**
- Config: `loss.supervised: ce_dice` plus
  ```yaml
  loss:
    scnp: {enabled: true, window: 3, mode: add}   # mode add = house(z) + house(scnp(z)); "replace" lost 0.02 Dice on Crack500 (R)
  ```
- Function (file `src/losses/scnp.py`), z (B, 24, H, W) float32, m (B, H, W):
  ```
  V = (m != 255)[:,None]                                         # (B, 1, H, W)
  Y = one_hot(m.clamp(max=23), 24).permute(0,3,1,2).bool() & V  # (B, 24, H, W)
  N = (~Y) & V                                                   # px not of class c (valid only)
  BIG = 1e4
  zf = where(Y, z, +BIG);  fg = -max_pool2d(-zf, window, 1, window//2)   # worst (lowest) logit among same-class neighbours
  zb = where(N, z, -BIG);  bg =  max_pool2d( zb, window, 1, window//2)   # worst (highest) logit among not-c neighbours
  z_bar = where(Y, fg, where(N, bg, z))                          # ignore px keep z (excluded from the loss anyway)
  loss = house_ce_dice(z, m) + house_ce_dice(z_bar, m)
  ```
  Each px is its own neighbour, so fg / bg are always finite on valid px. All 24 channels, as in the paper.
- Switch: `loss.scnp.enabled`; absent = house object.
- **Unit tests:** (1) constant logits: z_bar == z; (2) a 1 px crack line with one weak px (crack logit -2 among +3): every crack px within 1 px of it gets -2 on channel 14; a background px next to a false crack logit +5 gets +5 on channel 14; (3) ignore px are never chosen as neighbours and keep their logit; (4) autograd: gradient reaches only the arg-min / arg-max positions; (5) flag-off identity.

**CPU pre-check (support, not kill):** on 50 training cells of fold 0, build "jittered one-hot logits" (5 x one-hot of the 2021 mask) and score them against the revised mask with house(z) and house(z_bar): the ratio house(z_bar) / house(z) on crack-cells vs crack-free cells tells how much SCNP amplifies pure label jitter. If the ratio on crack cells exceeds 5 (S), use `window: 3` with the penalty applied only to channels {14, 15} (crack, gridline) as a fallback setting, decided before the screen.
**Screen:** as 0.1; also gridline (15) IoU and F51 component recall descriptively.
**Should move:** crack component recall up and relP@2 up; gridline IoU up (secondary).
**Expected side effects:** W down 5 to 15% (S); crack-free false alarms down; relR@2 may fall.
**Drop rule:** drop if component recall gain < M_cc and relF1@2 gain < M_F1 and gridline IoU gain < 0.02, or relR@2 falls by more than M_F1 at matched relP@2.
**Cost:** build 2 h; screen 10 x 1.25 GPU-h = 12.5 GPU-h (two softmaxes and 48 pooling maps per step).
**Needs:** nothing.
**Risks / how it could mislead:** under jitter the model may lower all crack confidence, which shows as higher relP@2 and lower relR@2 at argmax: an operating-point shift. The matched-operating-point read decides. The "worst neighbour" of a crack px is often a mislabelled px, so SCNP can amplify label noise; the pre-check estimates by how much.

---

## A5. `cc_dicece_crack`: component-wise DiceCE over Voronoi regions of crack components (priority 60)
**Papers:** CC-DiceCE (74). Multi-class extension (82) is the gated variant A5m.
**Hypothesis (S):** the house Dice sums over the batch, so the few long cracks dominate (fold 3 holds 100k of 310k crack px, E PROTOCOL 3.2) while 76 to 88% of crack components are under 20 px (E BRIEF 2). Giving every component its own DiceCE term raises recall on short cracks (R: recall +0.013 to +0.078 on 4 of 5 sets).

**Exact change**
- Config:
  ```yaml
  loss:
    cc: {weight: 1.0, cls: 14, merge_gap: 2, eps: 1.0e-6}    # 1:1 with the global loss (R)
  ```
- Target builder `crack_vor` (aux), per augmented mask m:
  ```
  yc = (m == 14)
  if not yc.any(): return {"crack_vor": zeros(H, W, int16)}
  yd = binary_dilation(yc, ones((3,3)), iterations=merge_gap // 2 + (merge_gap % 2))  # merge fragments <= merge_gap px apart
  lab, K = ndimage.label(yd, structure=ones((3,3)))             # 8-connected components of the merged mask
  _, (iy, ix) = distance_transform_edt(lab == 0, return_indices=True)
  vor = lab[iy, ix]                                              # (H, W) in 1..K: nearest merged component (Voronoi)
  vor[m == 255] = 0                                              # ignore px in no region
  return {"crack_vor": vor.astype(int16)}
  ```
  Components are defined on the merged mask; the Dice target inside a region is still the original label `yc`.
- Loss term (file `src/losses/cc_dicece.py`, wrapper on the house loss):
  ```
  base = house_ce_dice(z, m)
  V = (m != 255);  p = softmax(z.float(),1)[:,14];  y = (m == 14).float()
  lce = F.cross_entropy(z.float(), m, ignore_index=255, reduction="none")          # (B, H, W)
  K_b = crack_vor.amax((1,2));  off = cumsum(K_b) - K_b                               # region id offsets per image
  g = where(crack_vor > 0, crack_vor + off[:,None,None], 0).long().flatten()          # (B*H*W,), 0 = no region
  R = int(K_b.sum());  if R == 0: return base
  sum_r(x) = zeros(R+1).index_add_(0, g, x.flatten())[1:]
  I = sum_r(p*y);  P = sum_r(p*V);  Yr = sum_r(y);  n = sum_r(V.float());  C = sum_r(lce*V)
  dice_r = 1 - 2*I / (P + Yr + eps)                              # non-smooth Dice (R: smooth destabilised training)
  ce_r = C / n.clamp(min=1)
  L_cc = (dice_r + ce_r).mean()                                  # each component counts once
  loss = base + weight * L_cc
  aux_keys = ("crack_vor",)
  ```
- **Unit tests:** (1) one component -> one region covering the image; L_cc = (1 - Dice) + mean CE over valid px; (2) two components of 4 px and 400 px with equal per-region Dice contribute equally; (3) two 1 px wide segments separated by 2 background px -> one region with merge_gap 2 (one dilation step); separated by 4 px -> two; (4) no crack -> L_cc not computed and loss == house exactly; (5) region ids do not collide across images in a batch; (6) flag-off identity.

**CPU pre-check (support):** on the 532 pool masks, report the number of merged components per crack cell and per batch (expected regions per batch of 8), and the share of components under 20 px before and after merging at gap 2. If merging at gap 2 removes more than 60% of components (they were fragments), rerun the count at gap 1 and use the gap that leaves the median component >= 5 px (S); decided before the screen.
**Screen:** as 0.1; F51 component recall descriptively.
**Should move:** crack component recall (>= 20 px) and any-hit recall up; relR@2 up.
**Expected side effects:** more small predicted blobs: component precision and crack-free false alarms may worsen (R: precision collapsed on BraTS); W up 0 to 15%.
**Drop rule:** drop if component recall gain < M_cc, or component precision falls by more than M_cc, or crack-free false alarms rise > 1.5x, or relP@2 falls by more than M_F1.
**Cost:** build 4 h; screen 10 x 1.2 GPU-h = 12 GPU-h.
**Needs:** nothing (scipy present; the official code uses CuPy, not needed).
**Risks / how it could mislead:** component recall rises trivially if the model sprays small blobs; component precision and the crack-free false-alarm count are the guards. The Voronoi CE term reweights the CE of all 24 classes inside crack cells; a change in other classes' IoU is a side effect of that, not of crack learning.

**Variant A5m `cc_dicece_multi` (paper 82, after gate):** same term one-vs-rest for classes {14, 11, 15} (crack, inactive, gridline), classes averaged equally, inactive components without merging. Gate: A5 passes on component recall without tripping the precision guard. Should move inactive component recall (>= 100 px) and inactive IoU on CV5-G (whose inactive SE is 0.038, E PROTOCOL 3.2, so only a large effect is detectable).

---

## A6. `coletra_crack`: disconnect-to-connect augmentation on crack (priority 55)
**Paper:** CoLeTra (36).
**Hypothesis (S):** blending inpainted background over parts of crack labels, label unchanged, teaches the model that a crack continues where image evidence fades. That targets faint cracks (7% of components < 2% contrast) and E1-type misses. Labels are untouched, so no width bias by construction (R: Crack500 beta0e 9.687 -> 9.135, Dice 69.3 -> 69.7).

**Exact change**
- Pre-pass (CPU, once per pool cell, before training; `scripts/t2_inpaint.py`): `M = binary_dilation(mask == 14, iterations=3) & (mask != 255)`; `inp = cv2.inpaint(img_u8, M.astype(uint8), 3, cv2.INPAINT_TELEA)`; save `<bench_data>/aux/inpaint_v11/<stem>.png` with an md5 manifest. Paper used LaMa (R); Telea is the installed substitute (S).
- Online transform (file `src/data/coletra.py`), an Albumentations transform placed **first** in the training Compose so `BatchStream` seeds it (`stream.find_composes`); the inpainted image enters as an additional image target (`additional_targets={"inpaint": "image"}`) and is dropped after the transform. Parameters: `p 0.5` per image, `size s 15`, `sigma s/4`, `cover 0.5`, `max_n 20`, `exclude [11]`:
  ```
  if rng.random() > p or not (mask == 14).any(): return image
  cand = crack px not within 3 px of class 11
  centres = []; W = zeros(H, W)
  while covered_share(W > 0.5 on crack px) < cover and len(centres) < max_n:
      c = cand[rng.integers(len(cand))]; centres.append(c)
      W = maximum(W, gaussian_window(c, s, sigma))   # s x s window, peak 1
  image = (1 - W) * image + W * inpaint               # float, then back to uint8
  mask unchanged
  ```
- Config: `data.coletra: {p: 0.5, size: 15, cover: 0.5, max_n: 20, inpaint_dir: <path>, exclude: [11]}`; absent = off.
- **Unit tests:** (1) p 0 -> image unchanged and batch stream identical; (2) same seed -> same output; (3) mask never changes; (4) pixels farther than s/2 + 3 px from any crack px are unchanged; (5) inpainted files exist for exactly the train stems of each root and md5s match the manifest; (6) the held-out dataset has no CoLeTra transform (assert in the builder).

**CPU pre-check (can kill the Telea substitute):** on 50 training crack cells, measure the crack contrast (mean intensity in the crack mask / mean in a 3 to 6 px ring) in the original and in the inpainted image. Pass if the inpainted contrast is within 1% of 1.0 in >= 80% of cells and no new dark line > 10 px appears along the inpainted region (difference image check). If Telea leaves visible streaks (fails), switch to a row/column median fill along the cell's finger direction, re-check, and only then run.
**Screen:** as 0.1; F51 crack relF1@2 and component recall descriptively.
**Should move:** relR@2 at matched relP@2 up and any-hit component recall up; strict IoU flat.
**Expected side effects:** W unchanged (0.95x to 1.05x); false alarms may rise along dark linear structures (gridline, busbar edges, scuff in E1) because the model learns to trust weak evidence.
**Drop rule:** drop if relR@2 at matched relP@2 gain < M_F1 and any-hit recall gain < M_cc, or crack-free false alarms rise > 1.3x.
**Cost:** build 4 h (pre-pass, transform, determinism tests); screen 10 x 1.1 GPU-h = 11 GPU-h; CPU pre-pass about 532 cells x 50 ms.
**Needs:** OpenCV (present, opencv-headless 5.0). LaMa would need a separate venv (not requested).
**Risks / how it could mislead:** if Telea leaves a smooth dark band, the "erased" crack is still visible and the arm becomes a mild contrast augmentation. The pre-check guards this. The inpainted images depend on labels; they must be built per pool cell and only read for training stems, so no held-out label leaks into training.

---

## 7. Order of work (S)
1. Shared infra + A1 + A3 + A4 (one build day, about 12 h incl. tests); pre-checks P1, A4 jitter ratio (CPU).
2. Pre-screens (fold 0, seed 5) for A1, A3, A4 while W1a runs; full screens after W1a gives the noise margins.
3. A5 and A6 (about 8 h build) next; their pre-checks are CPU.
4. A2 when G5 is decided from W1a dumps.
5. Gated variants A1g and A5m only after their parents' screens.
6. Benchmark config rows (Lovasz, Jaccard, Tversky, focal, T-Loss on crack): 1 seed x 5 folds each, after the `composite` loss exists; they are suite entries, not candidates for the best score.

Total screen GPU (all six arms, 2 teachers for A2): about 77 GPU-h, plus 16.5 if A2 uses 5 teachers; on 8 A6000s at 1 run per GPU, about 10 to 12 hours of wall time.
