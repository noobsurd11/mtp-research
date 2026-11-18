# T7 spec: unseen-module gap (BRIEF problem 3)

Analyst T7, 13 Nov 2026. Tags: R = paper, E = our files, S = my judgement. Paper cards: `T7_unseen_modules_family.md`. Ledger: `ledger/T7.tsv`.
Nothing here reads test or E1. All numbers about E1 quoted below were already opened and published in the handbook (docs 20, 21).

**Order:** section 0 (the development instrument, a prerequisite; mostly CPU) then three arms by priority: 1 `gin_ipa`, 2 `mic_halfcell`, 3 `msc_tta`.
**Where these differ from wave 2 (WAVE2_REVIEW 4):** no wave-2 arm targets the unseen layout (critic finding X11). The closest are T1 `ema_wise_posthoc` (robust fine-tuning, no target data) and the T5 perturbation probe (synthetic corruptions, not real target cells). None of the three arms below duplicates them; section 0.6 proposes reading those arms on the new instrument as well.

---

## 0. The development instrument U-dev (prerequisite, not an arm)

### 0.1 Why one number cannot do it (E)
- E1's crack loss sits in a stratum (half-cut + scuff: 75% of E1 crack px, recall 0.126) that has **no labelled non-E1 example** (idea 5 1.7: non-E1 scuff labels are small faint patches with no crack branches; H36 crack labels are unusable).
- Two documented instrument failures: (a) HC moved the synthetic half-cut set SHV1 by +0.123 matched relR@2 while E1 relF1@2 moved +0.0135 n.d.; (b) PF moved E1 inactive by +0.19 while CV5 (B6) showed nothing of that size. So neither a synthetic layout proxy nor in-distribution CV predicts E1 on its own.
- Therefore U-dev is a **panel** of five reads, each arm pre-declares one primary read from it, and the decisive test is one registered E1 opening for the family at the end (0.7).

### 0.2 The five reads
| Read | Cells | What it measures | Blind spot | Cost |
|---|---|---|---|---|
| **U1 LOSO-2** | P532 split by source: CSIR held out (114 cells, 51 crack, 11 inactive, 76 module groups; train 418) and BMRK held out (50 cells, 30 crack, 6 inactive, 50 groups; train 482). E from `benchmark/cells.tsv` | transfer to unseen camera / contrast / label width (CSIR is E1's source; BMRK is scale + padding + 3.0 px labels) | no half-cut, no scuff; strict IoU partly scores the held-out label convention, so tolerant metrics lead | 8 baseline runs (PF v1.1, seeds 5 to 8) = 8.8 GPU-h, once |
| **U2 SHV-OOF** | synthetic half-cut views of every P532 cell (both halves; gap found in about 97% of cells, E idea 5 4.1), each scored by the fold model that held that cell out | the half-cut geometry + pool-like intensity part of the gap (scale x1.34, gap, intensity) | no 9-busbar layout, no CSIR half-cell texture, no scuff, no letterbox. Gamed by any arm that trains on the same simulator (HC) or inverts its fixed 1.34 scale (msc_tta) | CPU 1 h to build; inference minutes |
| **U3 F51** | 51 `_rf` full cells from 36 unseen modules, 12 crack cells | real unseen-module full cells | 76% of crack AP sat in one cell in the A8 screen; F51-only pass = promotion only (WAVE2 X9) | inference minutes |
| **U4 real half-cell false alarms** | H36 19 crack-free half-cuts (labelled crack-free); 1,008 pool half-cells (unlabelled, `ideas/domain_out/ap_pool.tsv` md5 a78a2d2a, CSIR_00300 already excluded) | false alarms and crack volume on real half-cell context (9 busbars, cut gaps, real scuffs) | label-free on the pool: a volume rise can be recall or false alarm | inference minutes (pool: 2 models per arm) |
| **U5 CSIR-multi stratum of CV5** | 32 CSIR multi cells of P532, out-of-fold | the labelled real stratum closest to E1's cell type (unseen CSIR multi modules, full layout) | full layout only; 32 cells | free from CV5 dumps |

Metrics on every read: crack relF1@2 at OP-A with relP@2 / relR@2, relF1@1, strict IoU, width ratio (WAVE2 5 guards), matched-precision relR@2 (max relR@2 at relP@2 >= 0.90, from a bias sweep; descriptive frontier), crack-free false alarms (crack px per cell, share with >= 50 px), inactive IoU where inactive exists (U1: 17 cells; descriptive only).

### 0.3 Statistics
- **U1:** two-stage bootstrap within the held-out source (module groups, then seeds), 2,000 resamples; **M_U1 = max(0.01, 2 x SE of the A/A contrast** PF seeds {5,6} vs {7,8} on LOSO-2), same rule as WAVE2 X1.
- **U2, U5:** the CV5 bootstrap (330 groups, then seeds), M from the W1-C1 A/A split (seeds {5,6} vs {7,8}).
- **U3:** paired over the 10 fold x seed models; logged in the F51 read ledger.
- **U4:** ratios to the baseline; no test.

### 0.4 Build (engineer; S hours)
1. `benchmark/splits/loso2.json`: two folds (`loso_csir`, `loso_bmrk`), train = P532 minus the source, held = that source; roots by `bench_make_roots.py` with the B6 asserts (0 forbidden stems; held-outs equal the source's P532 cells; test.txt = val.txt = held). 1 h.
2. `bench/sets/shv_oof/`: run `ideas/scripts/dom_synth_val.py` (md5 6e702c36, deterministic, seed 20261031) on all 532 cells with v1.1 strict masks instead of the 54 val cells; write `images/`, `masks/`, `ignore/` (ignore = v1.1 ignore transformed with the mask), `stems_eval.txt`, a `fold` column (the fold of the source cell), MANIFEST.md5. Unit test: on the 54 val cells it reproduces SHV1 (MANIFEST 63dd5469) to |delta| <= 1 grey level, masks exact. Add set `shv_oof_f{k}` to `bench/sets.py` (the views of fold k's cells). 2 h.
3. Set `pool_half` in `bench/sets.py` (images only, no masks): the 1,008 stems; `bench_score.py --labelfree` writes per cell: crack px, crack components >= 20 px, px with p_crack in [0.01, 0.968), D4 stability (relF1@2 between the plain prediction and the D4-averaged one, if a TTA dump exists). 2 h.
4. U5 and U4-H36 rows: subsets in the scorer config (`cells.tsv` source + cell_type; H36 crack-free list). 0.5 h.
5. R0 retrodiction script (0.5 below). 1.5 h.
Total about 7 build hours; GPU 8.8 h (U1 baseline) + about 1 h of inference.

### 0.5 R0: a retrodiction check of the panel (CPU or about 1 GPU-h of inference; needs the lead's OK)
Old checkpoints whose E1 contrasts are already opened (handbook 20, 21; on gaint): SUP100-g s5-9, SUP100-PF s5-9, HC s5-9, SKR2 s5-9, RN50-PF s5-9 (and THIN-B3 SKR w1.0 if kept). These were trained on the 478 train cells, so SHV1 (from val), F51, H36 and the pool half-cells are held out for them. Compute U2' (SHV1), U3, U4 for each family and compare signs with the published E1 contrasts: PF - g inactive +0.189 (BETTER) and crack recall +0.027 (n.d.); SKR2 - PF crack relF1@2 +0.036 (BETTER); SKR - PF relF1@2 +0.059; HC - PF +0.0135 (n.d.); RN50-PF - PF scuff + half-cut recall -0.025 (n.d.).
- **Rule (fixed now):** a read is used as a crack primary only if it gives a positive contrast for both crack movers (SKR2, SKR) and does not rank HC above them on any read HC was not trained on (U3, U4). U2' is exempt from the HC clause (HC trained on its simulator). A read that fails is kept as a guard only.
- **Already known (E, idea 5 1.5):** on V4 (= SHV1 geometry and intensity) PF beats the house ensemble on inactive (0.467 vs 0.369), the same sign as E1. So U2 already agrees with E1 on the one decisive inactive contrast.
- **Caution (S):** 5 contrasts, 2 of them crack movers. R0 can falsify a read; it cannot validate one. It uses published E1 numbers to choose an instrument, not a model; the lead must accept that as allowed.

### 0.6 Cheap use of U-dev for arms already queued (S)
Every wave-2 arm keeps its OOF fold models. Reading them on U2, U3, U4 is inference only (about 0.1 GPU-h per arm). Do it for `ema_wise_posthoc`, `encoder_spd`, `crackcue_input`, `liot_input` and `swad_const` at least: robust fine-tuning and contrast-invariant inputs are the wave-2 arms most likely to move unseen modules. Multiplicity: these are descriptive unless the arm pre-declared U-dev before its screen.

### 0.7 The decisive read (lead decision)
One registered E1 opening for this family near the end (after 5-seed confirmation), at most 3 candidates chosen by the rules below, primaries written before the opening: E1 crack relF1@2 in the two strata (half-cut + scuff, rest) with relP@2 beside it, E1 any-hit component recall, crack px on the 74 crack-free E1 cells; E1 inactive IoU descriptive (3 images hold 87%).

### 0.8 What each arm must move, and how it can fool us
| Arm | Pre-declared primary (read) | Must also hold | Can look good and fail on E1 because |
|---|---|---|---|
| gin_ipa | U1 LOSO-2 crack relF1@2, OP-A | U2, U5, CV5 guards | LOSO is a source / contrast shift; E1 is the same source with a new layout and scuff. Photometric invariance can win LOSO-BMRK and not touch scuff + half-cut |
| mic_halfcell | U2 SHV-OOF crack relF1@2, OP-A | H36 false alarms, CV5 guards | SHV has no scuff and train texture; HC moved SHV without E1. Conversely a real E1 gain on scuff cells would be invisible on every read |
| msc_tta | U2 SHV-OOF crack relF1@2, OP-A (declared as an upper bound) | CV5 not worse, U4 false alarms | SHV is built at exactly 1.34x, so the 0.75 view inverts it by construction; HC already showed learned scale invariance moves E1 by about +0.01 |

---

## Arm 1: gin_ipa (P012; fallback P057; benchmark row P369)

- **Problem:** unseen_modules (BRIEF problem 3). **Primary:** U1 LOSO-2 pooled crack relF1@2 at OP-A (164 held-out cells), with the frontier read (relR@2 at the baseline's relP@2) as its matched-operating-point check. OP-W needs fold cross-fitting, which LOSO-2 cannot give, so the frontier replaces it here; on CV5 the usual OP-A + OP-W rule holds.
- **Hypothesis (S):** random nonlinear appearance maps (GIN) teach invariance to histogram shape, the one photometric E1 gap the house jitter cannot reach (60% of E1 half-cuts outside train p97.5, gamma covers 5 to 11%; idea 11). Spatially blended appearance (IPA) breaks "dark extended region next to a thin line" as a cue (scuff streaks; inactive regions that touch 99% of the time), the paper's confounder mechanism.
- **Harness support used:** PF card unchanged; trainer supervised step; `ce_dice` criterion called twice; the batch stream untouched (augmentation on GPU after loading, so `BatchStream` determinism is kept); `bench_infer` + `bench_score` + `crossfit_op` unchanged.

### 1.1 The change
New file `src/data/gin_ipa.py`; hook in `src/training/trainer.py` in the supervised train step, before the forward pass; config block (all off by default; flag-off must stay IDENTICAL on the 5-step CPU identity check):
```
aug_gpu:
  gin_ipa:
    enabled: true
    n_layer: 4               # R (paper / repo default)
    interm_channels: 2       # R
    kernel_pool: [1, 3]      # R (repo scale_pool), one size drawn per layer per call
    conv_bias: true          # repo behaviour unverified: read GradlessGCReplayNonlinBlock before build; if it has no bias, set false
    leaky_slope: 0.2         # unverified paper value (S)
    sign_correct: true       # S, EL adaptation
    ipa: true
    ipa_grid: 5              # 5x5 control points = spacing 1/4 of the side (R)
    lambda_div: 10.0         # R
```
Pseudo-code (x: (B,1,512,512) fp32, already normalised by the house pipeline; m: (B,512,512) int64 with 255 = ignore):
```
def gin(x, g):                                  # g: torch.Generator on x.device
    B,_,H,W = x.shape
    ch = [1] + [C]*(L-1) + [1]                  # C = interm_channels, L = n_layer
    h = x.reshape(1, B, H, W)                   # grouped conv: one random net per sample
    for l in range(L):
        k = kernel_pool[randint(len(kernel_pool), g)]
        w = randn(B*ch[l+1], ch[l], k, k, g)    # N(0,1)
        b = randn(B*ch[l+1], g) if conv_bias else None
        h = conv2d(h, w, b, padding=k//2, groups=B)        # (1, B*ch[l+1], H, W)
        if l < L-1: h = leaky_relu(h, leaky_slope)
    net = h.reshape(B,1,H,W)
    if sign_correct:                            # flip draws that invert contrast
        r = pearson(net.flatten(1), x.flatten(1))          # (B,)
        net = net * where(r < 0, -1, 1).view(B,1,1,1)
    a = rand(B,1,1,1, g)                        # alpha ~ U(0,1)
    y = a*net + (1-a)*x
    return y * (x.flatten(1).norm(dim=1) / (y.flatten(1).norm(dim=1) + 1e-5)).view(B,1,1,1)

def ipa_pair(x, g):
    y1, y2 = gin(x, g), gin(x, g)
    c = rand(B,1,ipa_grid,ipa_grid, g)
    bm = interpolate(c, size=(H,W), mode="bicubic", align_corners=True).clamp(0,1)
    return bm*y1 + (1-bm)*y2, (1-bm)*y1 + bm*y2

# train step, when enabled
g = torch.Generator(device).manual_seed((cfg.seed * 1_000_003 + step) % 2**63)
with torch.no_grad(): t1, t2 = ipa_pair(x.float(), g)          # outside autocast
logits = model(torch.cat([t1, t2]))                              # (2B,24,H,W), bf16 autocast as house
l_seg = 0.5*(sup_criterion(logits[:B], m) + sup_criterion(logits[B:], m))
lp1, lp2 = log_softmax(logits[:B].float(),1), log_softmax(logits[B:].float(),1)
kl = 0.5*((lp1.exp()*(lp1-lp2)).sum(1) + (lp2.exp()*(lp2-lp1)).sum(1))   # (B,H,W)
loss = l_seg + lambda_div * kl[m != 255].mean()
```
Deviations from the paper, all S: sign correction; symmetric KL (the paper's direction not stated in the text read); the two segmentation terms averaged (keeps the house loss scale and learning rate); applied after the house label-safe pipeline (paper: after its own geometric and intensity augmentation). Batch: 8 distinct images, 2 views each (16 forward), so the sample budget equals the house recipe.

**Unit tests** (`tests/test_gin_ipa.py`): (1) flag off: 5-step CPU identity IDENTICAL for the house and PF cards; (2) `gin` output finite, shape (B,1,H,W), per-sample Frobenius norm equal to the input's (rtol 1e-4); (3) alpha forced to 0 returns x exactly; (4) with sign_correct, Pearson(net, x) >= 0 on 1,000 draws; (5) IPA map in [0,1], and t1 + t2 = y1 + y2 exactly; (6) same seed and step give the same views, different steps different views; (7) KL term 0 when t1 == t2; (8) masks untouched (tensor equality); (9) no parameter of the GIN nets is in the optimizer.

### 1.2 CPU pre-check P-GIN (decides the variant before any GPU time; about 1 h build, 20 min CPU)
Script `bench/precheck/gin_cnr.py` on the 229 crack cells of P532 (v1.1 train masks; dev data), 20 draws per cell, fixed seed:
- (a) **crack contrast retention.** CNR = (median(ring) - median(crack)) / (1.4826 MAD(ring)), ring = dilate(crack, 6 px) minus dilate(crack, 2 px), on the normalised image before and after `ipa_pair` (view t1). Cells with original CNR >= 1 only. r = CNR_after / CNR_before. **Pass: median r >= 0.6 and 10th percentile >= 0.2.**
- (b) **histogram-shape coverage** (reported, not a kill): share of augmented P532 cells (5 draws each) with shape = (p50 - p5) / (p95 - p5) >= 0.84 on content px (0.84 = the pool and Hanifi half-cell p90, idea 11; non-E1). Expected well above the 5 to 11% that gamma reaches.
- (c) a 16-cell montage for the record (no decision).
- **Fallback chain (fixed now):** (a) fails -> rerun with `kernel_pool: [1]` (pointwise nonlinear intensity, no texture; IPA still spatial) -> (a) fails again -> replace GIN with SLAug GLA (P057: monotone cubic Bezier curve on content px, alpha ~ TN(1, 0.1), beta ~ TN(0, 0.5); no class-wise LLA, it would paint labels) inside the same IPA blend and loss. Whichever variant passes is the arm; the others are not run.

### 1.3 Pathfinder and screen (the arm runs where its comparator ran: U1 on gaint with the U1 baseline; CV5 on cv02 against W1-C1, or on gaint against W1-G if cv02 stays full)
- **Pathfinder:** 1,000-step smoke (peak memory, step time), then fold 0 seed 5 full 20k (about 2.2 GPU-h on an A6000; S estimate 1.9 to 2.0x the house step time because each step runs 16 images). Catches divergence, a crack collapse (OOF crack px < 0.5x baseline) or a width blow-up; not ranked.
- **Stage A (primary):** LOSO-2, seeds 5 and 6: 4 runs, about 8.8 GPU-h. Promote to stage B only if U1 crack relF1@2 delta >= M_U1 with bootstrap lower bound > 0, the frontier read has the same sign, and the width ratio is inside 0.85 to 1.15 x baseline on each held-out source.
- **Stage B (guards):** CV5 cv5v2_v11, seeds 5 and 6: 10 runs, about 22 GPU-h; dumps read on CV5, U2, U3, U4, U5 and the WAVE2 section 5 guard table.
- **GPU-h:** pathfinder 2.2 + stage A 8.8 + stage B 22 = 33 (stage B only after stage A passes; 11 GPU-h decide the arm). **Build:** about 5 h (module 1.5, trainer hook 1, tests 1.5, pre-check 1).
- **Needs:** nothing new (torch only). No weights.

### 1.4 Expected effect and drop rule
- **R:** +9.0 / +9.0 / +13.8 Dice over ERM on three medical shifts; IPA +0.3 to +5.3 over GIN-only, largest on the cross-centre (same-modality) shift.
- **S:** our shift is much milder (photometry inside the train envelope except histogram shape). U1 crack relF1@2 +0.01 to +0.04; CV5 crack relF1@2 -0.01 to +0.005; U2 0 to +0.02; E1 unknown, plausible 0 to +0.03.
- **Drop:** stage A fails -> drop (keep only the RandConv benchmark row, P369: `n_layer 1, ipa false, lambda_div 0`). Stage B: CV5 crack relF1@2 or strict IoU worse than -M at OP-A and at OP-W, or crack-free false alarms > 1.5x, or inactive IoU worse than -0.03 (descriptive; SE 0.038) -> one FIX run with GIN on half the samples (`apply_p 0.5`, the other half get t1 = t2 = x), else drop.

### 1.5 Risks and how it could mislead
- **Instrument transfer:** see 0.8. A LOSO pass says "robust to a new source's appearance", not "fixes half-cut + scuff".
- **Width / operating point:** the KL term to an augmented view tends to soften predictions; argmax recall can drop while relF1@2 at a tuned point rises. Read OP-A and the frontier on U1, OP-A and OP-W on CV5; width band enforced.
- **Faint cracks:** 7% of crack components are < 2% darker than their surround (BRIEF 2); GIN can erase them while the label stays (label noise). P-GIN (a) and the CV5 guard on component recall for small components catch it.
- **Leakage:** none (no target data, no new labels). LOSO roots must contain 0 cells of the held-out source in train (assert).
- **Strict IoU on LOSO** scores the held-out label convention (BMRK 3.0 px vs ARTS 1.5 px); it is reported, never the primary.

---

## Arm 2: mic_halfcell (P034; follow-up P394; rules from P560, P539)

- **Problem:** unseen_modules. **Primary:** U2 SHV-OOF crack relF1@2 at OP-A (matched relR@2 beside it). **Key guards:** H36 crack-free false alarms (H36 is never in the target pool), CV5 at OP-A and OP-W, U5.
- **Hypothesis (S):** the student adapts its features to real half-cell appearance (9 busbars at 36 to 39 px, smooth multi texture with mean |Laplacian| 2.8 vs train 10.7, cut gaps, real scuffs) through self-training on the 1,008 pool half-cells, with masked consistency forcing more robust context use. HC gave half-cut geometry with train texture; this arm gives real half-cell texture without labels.
- **Harness support used:** the Mean Teacher path of the trainer (teacher deep copy and `EMAUpdater`, trainer l.262-265; unlabelled stream; separate stream ids), PF card, `ce` with ignore 255. I have not read the SSL config keys of `train.py`; the keys below are new names that the engineer maps onto the existing `ssl` / `loss.consistency` keys, adding only what is missing.

### 2.1 The change
**Target list** `splits/target_pool_half.txt`: the 1,008 stems of `ap_pool.tsv` (group pool_half), minus every stem whose image id (module) occurs in E1 106, F51, H36, F19, test50, the 7 `CSIR_00300` `_rf` cells, the 17 unused `_rf` cells, or the 532 pool. Assert the count after exclusion, write md5. P532 has 0 half-cut cells, so no CV5 fold can share a module with the target (assert anyway by image id). Images go to `<root>/unlabeled/images/` on the training machine (pool cells are not sealed data).

Config (new keys; off by default):
```
uda:
  enabled: true
  target_list: splits/target_pool_half.txt
  target_batch: 4
  start_step: 2000          # after the PF 1k freeze; teacher EMA runs from step 0
  ema_decay: 0.999          # R
  tau: 0.968                # R
  lambda_t: 1.0             # R (DAFormer self-training weight)
  lambda_m: 1.0             # R
  mask_patch: 64            # R (full resolution)
  mask_ratio: 0.7           # R
  mask_fill: median         # S: median of the image's content px, not 0 (0 = dark = crack / inactive-like in EL)
  mic_loss_region: unmasked # S, from the paper's Table S1: unmasked-only 69.7 vs all 70.6 vs none 68.3
  pl_variant: A             # A or B, set by gate G-MIC
  concat_forward: true      # source and target in one forward, so BN batch statistics match the running statistics used at eval
  eval_weights: student     # report the student; the teacher is descriptive (an EMA is a separate wave-2 arm)
```
Pseudo-code per training step t (house loader gives xs (8,1,512,512), ys (8,512,512); target loader gives xt (4,1,512,512) after label-safe geometry only):
```
if t >= start_step:
    with no_grad: teacher.eval(); pt = softmax(teacher(xt).float(), 1)       # (4,24,H,W)
    conf, pl = pt.max(1)
    valid = conf >= tau                                                        # variant A
    if pl_variant == "B":                                                      # crack-safe (BAPA / CoTICA idea)
        risky = (pt[:,CRACK] >= 0.01) | (pt[:,INACT] >= 0.01)
        valid &= ~max_pool2d(risky.float()[:,None], 9, 1, 4)[:,0].bool()       # 4 px dilation
    xt_s = brightness_contrast(xt, 0.2, p=1.0)                                 # GPU, house ranges, same geometry
    Mk = (rand(4,1,8,8) > mask_ratio).float(); Mk = interpolate(Mk, (512,512), mode="nearest")
    xt_m = xt_s*Mk + median_content(xt_s).view(4,1,1,1)*(1-Mk)
    logits = student(cat([xs, xt_s, xt_m]))                                    # (16,24,H,W)
    l_sup = sup_criterion(logits[:8], ys)
    l_t = ce(logits[8:12], where(valid, pl, 255), ignore_index=255)
    l_m = ce(logits[12:16], where(valid & (Mk[:,0] > 0), pl, 255), ignore_index=255)
    loss = l_sup + lambda_t*l_t + lambda_m*l_m                                  # an all-ignore batch gives 0, not NaN
else:
    loss = sup_criterion(student(xs), ys)
after optimizer.step(): teacher <- ema_decay*teacher + (1-ema_decay)*student   (BN buffers copied)
```
**Unit tests** (`tests/test_mic_halfcell.py`): flag off IDENTICAL (5-step CPU, house and PF); target list contains no forbidden image id and no P532 image id; mask keeps 1 - r of the patches within +-0.05 over 1,000 draws; masked px equal the per-image content median; CE with an all-ignore target returns 0; variant B dilation on a synthetic single-pixel map gives a 9 x 9 block; EMA update equals the closed form on a 2-layer toy model; the teacher has no grad and is not in the optimizer; the target stream is a function of (seed, stream id, index) like `BatchStream`; the dump uses the student weights.

### 2.2 Gate G-MIC (before the trainer build; about 1 h build, 0.3 GPU-h or 2 h CPU)
Run two PF v1.1 fold-0 models (W1, seeds 5 and 6) on `pool_half` with `bench_infer` (U4 set, built in 0.4). Per model: (i) share of target px with max prob >= 0.968; (ii) number of half-cells with >= 20 px of confident crack (p_crack >= 0.968); (iii) share of px with p_crack in [0.01, 0.968); (iv) mean confident crack px per half-cell vs mean predicted crack px on the 303 crack-free CV5 cells (from the W1 dumps).
- **Variant rule (fixed now):** (ii) >= 3% of half-cells -> variant A; else variant B (otherwise the pseudo-labels say "half-cells have no crack", the failure suspected for R4, idea 5 2).
- **Kill:** (iv) ratio > 10 (the teacher's confident crack on half-cells is dominated by false alarms, which self-training would amplify), or under the chosen variant fewer than 50% of target px are supervised (pseudo-labels carry too little to adapt anything).

### 2.3 Pathfinder and screen
- **Pathfinder:** 1,000-step smoke (memory: S estimate 13 to 16 GB, one gaint lane), then fold 0 seed 5 full run (about 2.4 GPU-h; S: about 2.2x the house step time). Log per 500 steps: supervised / target loss ratio (P16 Sx100 had 2 to 7%; below 1% the target term is inert), share of valid target px, teacher confident crack px on target. Kill if student OOF crack px on fold 0 falls below 0.5x baseline.
- **Screen:** CV5 cv5v2_v11, seeds 5 and 6, 10 runs, about 24 GPU-h; reads U2 (primary), U3, H36 part of U4 (the pool part of U4 is in-sample for this arm and is descriptive only), U5, CV5 guards.
- **GPU-h:** gate 0.3 + pathfinder 2.4 + screen 24 = about 27. **Build:** about 9 h (target list + asserts 1, trainer UDA mode 4, tests 2, smoke and identity 1, gate 1).
- **Needs:** nothing new. The 1,008 pool half-cell PNGs copied to the training machine.

### 2.4 Expected effect and drop rule
- **R:** MIC +2.1 (HRDA) / +2.3 (DAFormer) mIoU on GTA -> CS; masking is the essential part (-20 without it); 20% pseudo-label noise costs about -4.
- **S:** U2 crack relF1@2 0 to +0.03; H36 false alarms flat or down; CV5 -0.01 to +0.005; E1 unknown (an effect on scuff cells is invisible to U-dev).
- **Drop:** U2 delta < M_U2 or interval includes 0 -> drop, unless H36 false alarms fall below 0.5x with CV5 flat (then it goes to the E1 opening as a precision candidate only). CV5 crack relF1@2 or inactive IoU worse than the WAVE2 guards -> drop. HRDA (P394) only after a screen pass.

### 2.5 Risks and how it could mislead
- **R4-type suppression:** pseudo-labels on half-cells are almost all background; the student may learn "half-cell => no crack". Variant B and the gate address it; watch predicted crack px on SHV-OOF crack cells.
- **BN statistics:** concatenated batches put half-cell statistics into the running BN buffers; full-cell in-distribution scores can shift (per-panel BN adaptation already failed, T9). CV5 guard.
- **Operating point:** self-training typically sharpens and shrinks rare-class predictions (argmax recall down, precision up). OP-W on CV5; the frontier on U2.
- **Instrument transfer:** U2 has no scuff and train texture (0.8). The arm can move U2 through intensity / scale robustness and leave E1 where HC left it.
- **Leakage:** target images come from the pool; module-level exclusion of every evaluation set is asserted. E1 modules: E1 cells are not in the pool by construction (handbook 03 7); the image-id assert also covers shared modules.

---

## Arm 3: msc_tta (P231; P384 parked as its selection variant)

- **Problem:** unseen_modules (and a benchmark TTA row). **Primary:** U2 SHV-OOF crack relF1@2 at OP-A, declared as an **upper bound** of the scale component (0.8). **Contrast:** D4 + scale views minus D4-only views on the same checkpoints (D4 alone was already run, handbook 18 R1).
- **Hypothesis (E/S):** half-cells appear at 1.34x the train cell pitch (342 vs 256 px) and their cracks are labelled about 1.5x wider (E); the house augmentation has no scale change, so a 0.75x view puts half-cell features at the train scale without retraining. HC bounds the E1 value: a model trained scale-invariant on the same geometry moved E1 relF1@2 by +0.0135 (n.d.).
- **Harness support used:** `scripts/bench_infer.py` (sets, dumps, sealed-set guard), the dump format, the scorer and `crossfit_op` unchanged. Checkpoints: W1 PF v1.1 (10 fold models, seeds 5 and 6), on the machine that trained them.

### 3.1 The change
New `bench/tta.py`; `bench_infer.py --tta {none,d4,d4ms} --scales 0.75,1.0,1.25`:
```
def predict_tta(model, x, scales, d4):           # x: (B,1,512,512) normalised fp32; model.eval(), TF32 off
    acc = zeros(B,24,512,512); n = 0
    for s in scales:
        side = 32*round(512*s/32)                 # 384, 512, 640 (U-Net++ R34 needs multiples of 32)
        xs = x if side == 512 else interpolate(x, (side,side), mode="bilinear", align_corners=False, antialias=(side < 512))
        for T, Tinv in (D4 if d4 else [(id,id)]):  # 8 dihedral maps
            lo = Tinv(model(T(xs)).float())
            if side != 512: lo = interpolate(lo, (512,512), mode="bilinear", align_corners=False)
            acc += softmax(lo, 1); n += 1
    p = acc / n                                   # probability average (R, PIE)
    return p                                      # dump: pred = argmax p; m_crack = log p_crack - max_{c != crack} log p_c; p_crack, p_inact; logp = log p
```
Unit tests: `--tta none` dumps byte-identical to the current dumps; each D4 pair round-trips a random tensor exactly; scales {1.0} with d4 equals the existing D4 code path within 1e-6; p sums to 1 (1e-5); 384 and 640 inputs run on R34 U-Net++; sealed sets still refused without `--opening`.

### 3.2 Pre-check, pathfinder, screen
- **No CPU pre-check decides anything** (the arm is itself inference). **Pathfinder:** one fold-0 model, all reads, to time it (S: 24 views x about 400 images per fold model, minutes).
- **Screen:** 10 W1 fold models x {d4, d4ms} on CV5 held-out folds, U2 (own fold's views), U3, U4 (pool for 2 models), U5. About 2 GPU-h in total (S), 0 training.
- **Build:** about 2.5 h. **Needs:** nothing.

### 3.3 Expected effect and drop rule
- **R:** PIE 0.7786 vs source 0.7680 Dice (+0.011), saturating at 28 views; online CTTA baselines below source.
- **S:** U2 crack relF1@2 +0.02 to +0.06 (overstated by construction); CV5 crack relF1@2 -0.005 to +0.01 (D4 alone gave about +0.01 on test); E1 at most about +0.015, mostly in half-cuts without scuff (8% of E1 crack px).
- **Drop as a score arm:** U2 delta < M_U2, or CV5 crack relF1@2 worse than -M at OP-A or OP-W, or crack px on H36 / pool half-cells > 1.5x. It stays a benchmark TTA row either way (no-TTA primary printed beside it, views and cost stated, P597).

### 3.4 Risks
- **Built-in proxy bias:** SHV's fixed 1.34 scale is exactly inverted by the 0.75 view (0.8); the U2 number is an upper bound, not an estimate of E1.
- **Width:** averaging 24 probability maps blurs 1 to 2 px cracks; argmax width and recall can change in either direction. OP-W and the width band decide; a gain at OP-A only is an operating-point shift.
- **Full-cell harm:** 0.75 and 1.25 views are off-scale for full cells; CV5 and F51 guard it. A routed variant (0.75 view only on cells the frozen half-cut detector R2b flags, held-out false-positive rate 1 to 4%) is a follow-up only if the uniform version passes U2 and fails CV5.

---

## Budget summary
| Item | Route | Build h | GPU-h | Waits for |
|---|---|---|---|---|
| U-dev (section 0) | analysis_only | 7 | 9.8 | W1 dumps for U5; lead OK for R0 |
| gin_ipa | training_recipe | 5 | 11 to decide, 33 if promoted | P-GIN, U1 baseline |
| mic_halfcell | training_recipe | 9 | 27 | G-MIC, U2 |
| msc_tta | inference_only | 2.5 | 2 | W1 checkpoints, U2 |

**First item by gain per build hour:** U-dev reads U2 + U4 (about 4 build hours) make every other arm in the project readable on unseen-module proxies; the first GPU arm is `gin_ipa` (5 build hours, no new dependencies, untested mechanism with the strongest published single-source DG evidence, and 11 GPU-h decide it).
