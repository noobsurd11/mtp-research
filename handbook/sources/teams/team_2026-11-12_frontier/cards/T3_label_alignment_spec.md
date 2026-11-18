# T3 experiment specification: misaligned and noisy thin labels

Analyst T3, 13 Nov 2026. Read with `T3_label_alignment_family.md` (paper cards and the metric analysis in its section 1).
Tags: **R** = paper or its code, **E** = our files, **S** = my judgement. "M" = the screen margin the lead fixes after wave 1 has measured seed and fold noise.

## 0. Common frame (applies to every arm)
- **Baseline:** `house_r34_unetpp_pf` (card `bench/methods/house_r34_unetpp_pf.yaml`) on `cv5v2_v11_f{0..4}`, seeds 5 and 6 (wave 1, W1a). The arms reuse these 10 runs and add none of their own baseline.
- **Arm runs:** the same card opts plus the arm's change only. Label set v1.1 (train masks with ignore 255, held-out strict). 20k steps, batch 8, 512 px, final weights. Canonical fp32 dumps of the held-out fold, scored on CPU by `bench_score.py`. Same machine and precision as the W1a baseline runs.
- **Screen:** 5 folds × seeds 5 and 6 = 10 runs, out-of-fold pooled, two-stage group bootstrap (`cv5v2_groups.tsv`, 330 groups). Pre-screen = fold 0, seed 5, to catch failures only.
- **Report for every arm:** the headline card (crack relF1@2 with relP@2 / relR@2, strict crack IoU, inactive IoU, mIoU-R13); **relF1@1** (the alignment-sensitive column; scorer already adds 1 and 3 px); crack component recall and precision; predicted / ground-truth crack px (width ratio); crack-free cell false-alarm rate; per-source table.
- **Operating-point guard:** every arm is also compared at matched predicted width. The crack bias is cross-fitted (chosen on the other 4 folds' OOF cells to make the width ratio equal the baseline's), then scored on the held-out fold. A gain that appears at argmax but vanishes at matched width is an operating-point shift, not a gain.
- **Why relF1@2 is not the main mechanism check (S, family file §1.2):** re-placing labels or predictions within 2 px leaves relP@2 and relR@2 unchanged to first order. Alignment shows up in relF1@1 and strict IoU. relF1@2 moves only through confidence on faint cracks (recall) or stray detections (precision).
- **Rules:** no test or E1 reads, no manual labelling, nothing in an existing worktree or mask folder changes. New code goes into `el_bench` behind opt-in keys, and each flag-off arm must stay IDENTICAL on the 5-step CPU identity check.

## 1. Arms in priority order

| # | Arm | Papers | Route | Priority | Build h | GPU-h screen | CPU pre-check decides first? |
|---|---|---|---|---|---|---|---|
| 1 | `matched_crack_head` | 4 (MatchED); model-driven alignment of 31 | new_loss + head | 72 | 8 | 13 (+12 for the τd = 0 control if it passes) | yes (P-M4 can kill) |
| 2 | `oof_soft_distill` | 10 (SGL) | training_recipe | 70 | 6 | 22 (11 teachers + 11 students) | teacher check only |
| 3 | `ridge_snap_labels` | 31 (STEAL alignment), 46 idea | data_pipeline | 60 | 4 | 11 | yes (P-RS1 can kill) |
| 4 | `oof_selective_ignore` | 20 (SelectSeg) | data_pipeline | 55 | 3 | 11 (reuses arm 2 teachers) | yes (flag-rate check) |
| 5 | `adele_confident_add` | 5 (ADELE), 83 noted | new_loss + trainer hook | 45 | 6 | 13.5 | yes (gate G2) |

Run order: CPU pre-checks P-M1 to P-M4 and P-RS1 to P-RS3 now (no GPU). Then the GPU pre-screen of arm 1 and the 10 teachers of arm 2, which also unlock arm 4. Arm 3 runs only if P-RS1 passes. Arm 5 runs after gate G2, which needs the W1a dumps.
No stacked arm is proposed now. If arms 1 and 2 both pass, a stacked arm (matched head on the distilled student) is the natural next step, because they act on different noise types (placement against missing segments).

---

## Arm 1. `matched_crack_head` (MatchED adapted to a 24-class softmax)

**Hypothesis (S).** Crack labels sit at a random ±1 to 2 px from the dark ridge (E, benchmark_el_report §4.2: 48% of label points within ±1 px of the darkest point, systematic offset only 0.2 px). The same appearance therefore gets inconsistent targets across cells, which lowers the model's confidence on faint cracks. A crack head trained on one-to-one matched targets gets consistent, width-preserving supervision. Unlike P14's max-pool tolerance, one-to-one matching keeps the number of target px equal to the label count, so it cannot reward width. Matching to the model's own output keeps any convention the model has learned (for example source width), because the target moves only where the model already fires.

### Change
New opt-in keys (all absent means the house model and loss, bit-identical):
```
model.crack_head.enable=true
model.crack_head.hidden=16
model.crack_head.depth=5
loss.matched.weight=1.0        # beta
loss.matched.tau_d=2           # Manhattan px
loss.matched.tau_c=0.05        # candidate threshold on sigmoid(h)
loss.matched.alpha=10          # confidence weight in the cost; P-M1 picks from {2, 10, 25}
loss.matched.start_step=10000  # head trained only in the second half, as the paper
loss.matched.dice=true
```
Card: `bench/methods/matched_crack_head.yaml`, `diff_ref: house_r34_unetpp_pf`, `decision_rule: crack_head` (implemented by the model's eval forward, see below, so the `argmax24` code path in the scorer and dumper is reused unchanged).

**File `src/models/crack_head.py`**
```python
class MatchedHead(nn.Module):                      # about 13.2K params at hidden 16, depth 5
    def __init__(self, in_ch=25, hidden=16, depth=5):
        layers, c = [], in_ch
        for _ in range(depth):
            layers += [nn.Conv2d(c, hidden, 3, padding=1), nn.ReLU(inplace=True), nn.GroupNorm(4, hidden)]
            c = hidden
        layers += [nn.Conv2d(hidden, 1, 3, padding=1)]
        self.net = nn.Sequential(*layers)
        nn.init.constant_(self.net[-1].bias, -4.0)  # sigmoid = 0.018 at start, below tau_c
    def forward(self, logits, image):              # logits (B,24,H,W), image (B,1,H,W)
        return self.net(torch.cat([logits, image], 1))   # (B,1,H,W) crack logit h

class CrackHeadSegModel(nn.Module):
    """Same forward as smp SegmentationModel (smp 0.5.0 base/model.py l.58-75) plus the head.
    encoder / decoder / segmentation_head are the core's own modules, so parameter names keep
    the 'encoder.' prefix that training.encoder_pf splits on (train.py l.117-123)."""
    def __init__(self, core, crack=14, hidden=16, depth=5):
        super().__init__()
        self.encoder, self.decoder, self.segmentation_head = core.encoder, core.decoder, core.segmentation_head
        self.crack = crack
        self.crack_head = MatchedHead(core.segmentation_head[0].out_channels + 1, hidden, depth)
    def forward(self, x):                                         # x (B,1,512,512)
        logits = self.segmentation_head(self.decoder(self.encoder(x)))   # (B,24,H,W)
        h = self.crack_head(logits, x)                            # (B,1,H,W)
        if self.training:
            return torch.cat([logits, h], 1)                      # (B,25,H,W): the loss splits it
        oth = logits.clone(); oth[:, self.crack] = torch.finfo(oth.dtype).min
        omax = oth.max(1).values                                  # (B,H,W)
        out = logits.clone(); out[:, self.crack] = omax + h[:, 0]
        return out    # argmax(out) = where(h > 0, 14, argmax of the other 23); dump margin m_crack = h exactly
```
`model_factory.build_model`: after `_build_core`, `if cfg.get("crack_head", {}).get("enable"): core = CrackHeadSegModel(core, ...)`. Only with `model.name=smp_unetpp` (raise otherwise).

**File `src/losses/matched.py`** (numpy + scipy; scipy 1.18.1 is in the house venv)
```python
def build_matched_target(p, gt, valid, tau_d=2, tau_c=0.05, alpha=10.0, cap=4_000_000, tile=128):
    """p (H,W) float32 sigmoid(h); gt (H,W) bool crack label; valid (H,W) bool (label != 255).
    Returns T (H,W) bool with |T| <= |gt|. Follows MatchED create_1to1_Label: cost = Manhattan - alpha*p,
    pairs farther than tau_d forbidden; matched label px move to the matched prediction; unmatched label px
    stay; confident unmatched predictions are 0."""
    T = gt.copy()
    if not gt.any(): return T
    diamond = ndimage.iterate_structure(ndimage.generate_binary_structure(2, 1), tau_d)
    band = ndimage.binary_dilation(gt, diamond)
    cand = (p >= tau_c) & band & valid
    if not cand.any(): return T
    lab, n = ndimage.label(band, structure=np.ones((3, 3)))
    vac, put = [], []
    for sl_idx, sl in enumerate(ndimage.find_objects(lab), start=1):
        # split very large components into tile x tile blocks (the official code tiles 4 x 4 at 512)
        for block in blocks(sl, lab == sl_idx, gi_count_times_pi_count > cap, tile):
            gi = argwhere(gt & block); pi = argwhere(cand & block)        # (nG,2), (nP,2) absolute coords
            if len(gi) == 0 or len(pi) == 0: continue
            D = abs(pi[:, None, 0] - gi[None, :, 0]) + abs(pi[:, None, 1] - gi[None, :, 1])   # (nP,nG)
            C = D - alpha * p[pi[:, 0], pi[:, 1]][:, None]
            C[D > tau_d] = 1e6
            r, c = linear_sum_assignment(C)
            keep = D[r, c] <= tau_d
            vac.append(gi[c[keep]]); put.append(pi[r[keep]])
    for a in vac: T[a[:, 0], a[:, 1]] = False          # vacate first ...
    for a in put: T[a[:, 0], a[:, 1]] = True           # ... then place
    return T

class MatchedHeadLoss(nn.Module):
    def __init__(self, base, crack=14, weight=1.0, tau_d=2, tau_c=0.05, alpha=10.0, start_step=10000,
                 dice=True, ignore=255): ...
    def set_step(self, step): self.step = int(step)
    def forward(self, out, masks):                     # out (B,25,H,W), masks (B,H,W) int64
        logits, h = out[:, :24], out[:, 24].float()
        L = self.base(logits, masks)                  # house CE + Dice, called unchanged
        if self.step < self.start_step:
            return L + 0.0 * h.sum()
        with torch.no_grad():
            p = torch.sigmoid(h).cpu().numpy()
            gt = (masks == self.crack).cpu().numpy(); valid = (masks != self.ignore).cpu().numpy()
            T = np.stack([build_matched_target(p[b], gt[b], valid[b], self.tau_d, self.tau_c, self.alpha)
                          for b in range(p.shape[0])])
        T = torch.from_numpy(T).to(h.device, torch.float32); V = (masks != self.ignore).float()
        bce = (F.binary_cross_entropy_with_logits(h, T, reduction="none") * V).sum() / V.sum().clamp_min(1)
        ph = torch.sigmoid(h) * V
        dice = 1 - (2 * (ph * T).sum() + 1) / (ph.sum() + (T * V).sum() + 1)   # batch soft Dice, as ce_dice
        Lh = bce + (dice if self.dice else 0.0)
        self.last_terms = {"matched": float(Lh), "t_over_gt": float(T.sum() / max(gt.sum(), 1)),
                           "moved_frac": float(((gt.astype(bool)) & ~T.cpu().numpy().astype(bool)).sum() / max(gt.sum(), 1))}
        return L + self.weight * Lh
```
- `loss_factory`: wrap `ce_dice` in `MatchedHeadLoss` when `loss.matched.weight > 0`; raise if `model.crack_head.enable` is not true.
- `trainer._train_step`: one added line before the loss, `if hasattr(self.sup_criterion, "set_step"): self.sup_criterion.set_step(step)`. `last_terms` reuses thin's term logging (`trainer.py` l.248, l.558); the engineer checks that it accepts these keys.
- Gradient: the head loss also flows into the base through `logits` (the paper trains both jointly). Knob for a later ablation, not for the screen: `loss.matched.detach_base`.
- sigmoid and the τc threshold are computed in fp32 (outside autocast).

**Unit tests `tests/test_matched.py` (CPU)**
1. `p = 0.9·gt` gives `T == gt`.
2. gt = vertical line on columns 100 to 101, p = 0.9 on columns 101 to 102: T is columns 101 to 102 and `|T| == |gt|`.
3. p on columns 104 to 105 (d = 4 > τd): `T == gt`.
4. Thick p on columns 99 to 103: `|T| == |gt|` and T is a subset of the p region.
5. No crack in gt: T is all False whatever p is.
6. Ignore: candidates with `valid == False` never receive a target px.
7. α: two candidate lines 1 px either side, p 0.3 left and 0.9 right: with α 10 the right one is matched.
8. Property test on 200 random real crack masks with random p: `|T| ≤ |gt|`; every px in T and not in gt lies within τd of a vacated gt px; no px moves more than τd.
9. Model: train-mode output (B,25,H,W); eval argmax equals `where(h > 0, 14, argmax of others)` on random inputs; `m_crack` computed as in `calib_dump` equals h (tolerance 1e-4 in fp32); the PF split finds the same number of `encoder.*` params as the plain core.
10. Flag off: 5-step CPU identity IDENTICAL against the `house_r34_unetpp_pf` path.

### CPU pre-checks (before any GPU)
- **P-M1 (target correctness on real masks).** Take 100 train crack masks from `benchmark/out/masks_v11/masks` (P532 stems only; assert none is in `b6_forbidden.txt`). Clean C = crack mask. Noisy N = each 16-px skeleton segment of C shifted along its normal by o ∈ {−2..2} with probabilities {0.1, 0.2, 0.4, 0.2, 0.1}. Prediction p = 0.9 on C, 0.02 elsewhere, plus Gaussian noise of sd 0.02.
  - **Pass:** `|T| ≤ |N|` everywhere. IoU(T, C) ≥ 0.85 while IoU(N, C) is about 0.5. With p = 0.9 on C dilated by 1 px, `|T| = |N|` and IoU(T, C) ≥ 0.6. With p = 0, `T == N`. A confident line 5 px away leaves T unchanged.
  - Run with α ∈ {2, 10, 25} and keep the α with the highest IoU(T, C) in the dilated case.
- **P-M2 (mechanism against P14).** For noisy N, compute the matched-head loss and the P14 tolerant loss (`TolerantPLLoss` max-pool rule on ground truth, R = 2) for three predictions: thin aligned (C), thick (C dilated by 1), thin shifted by 1 px.
  - **Pass:** matched loss(C) < matched loss(thick), and matched loss(C) < matched loss(shifted). The tolerant loss gives thick ≤ C, which documents why P14 could not control width.
- **P-M3 (speed).** 200 batches of 8 real train masks, p = Gaussian-blurred C (σ 1) scaled to [0, 0.95], single CPU thread.
  - **Pass:** median ≤ 60 ms per batch and p99 ≤ 400 ms. Otherwise set `cap` lower (tiling) and re-time.
- **P-M4 (decisive: does matching beat plain CE under random jitter?).** Synthetic data on CPU:
  - Images: 96 × 96, background 0.6 with low-frequency texture and noise of sd 0.03. Vertical "gridlines" carry their own class and are labelled exactly, so the softmax has 3 classes. One to three random gently curved lines with a Gaussian dark profile (FWHM 4 px) and relative contrast in {0.03, 0.05, 0.10, 0.20}.
  - Labels: clean label = 2 px band at the centreline. The training label for every drawn sample is the clean band shifted per 16-px segment by o as in P-M1, resampled each time the sample is drawn (many annotators).
  - Model: tiny U-Net (4 levels, 16 base channels), Adam 1e-3, batch 8, 1,500 steps, 3 seeds per configuration:
    - (a) CE + Dice on crack;
    - (b) (a) plus the matched head from step 750;
    - (c) (a) with the P14 tolerant loss.
  - Evaluate on 200 fresh images against the clean label: strict IoU, relF1@1, relF1@2, recall@2 per contrast bin, width ratio.
  - **Pass (go to GPU):** (b) − (a) strict IoU ≥ +0.03 in mean with no seed negative, or recall@2 on contrast ≤ 0.05 ≥ +0.05; and the width ratio of (b) in [0.8, 1.2].
  - **Kill (report to the lead, no GPU):** (b) − (a) within ±0.01 on strict IoU, relF1@1 and faint recall.
  - **Systematic sanity:** with every label shifted by a constant +1 px, (b) must keep the shift (IoU against the shifted clean band ≥ IoU against the unshifted).
  - About 1 to 1.5 CPU-h. A synthetic pass is necessary, not sufficient.

### Screen
- Pre-screen: fold 0, seed 5, about 1.3 GPU-h. Failure (stop and debug) if the width ratio is outside [0.7, 1.3], fold-0 crack IoU falls more than 0.05 below the W1a fold-0 runs, logged `t_over_gt` is below 0.9 (target collapse), or `moved_frac` is above 0.6 after step 12k.
- Screen: 10 runs, about 1.25 GPU-h each (head activations plus the CPU matching sync). Smoke 1,000 steps first for the memory gate; the head adds an estimated 1 to 1.5 GB (S).

### What it should move, side effects, drop rule
- **Should move (S):** relF1@1 up +0.01 to +0.03; strict crack IoU +0.00 to +0.015; relR@2 and component recall about +0.01; relP@2 within ±0.01.
- **Width:** ratio within ±0.05 of baseline (one-to-one).
- **False alarms:** flat or down (confident unmatched px are trained as negatives).
- **Inactive IoU, mIoU-R13:** no change expected; watch for drift through the head gradient into the base.
- **Drop if:** strict crack IoU, relF1@2 and component recall all gain less than M; or strict crack IoU or relF1@2 falls by more than M; or the width ratio leaves [0.85, 1.10] × baseline.
- **If it passes:** run the control `loss.matched.tau_d=0` (same head, raw labels as its target) on the same 10 slots before crediting alignment. If the control is within M of the arm, the gain comes from the head and decision rule, not from matching.

### Risks and how it could mislead
- **Operating point:** a sigmoid head at 0.5 replaces the softmax argmax for crack. Read the matched-width comparison (common frame) before any claim.
- **Self-confirmation:** labels move toward the model's own errors, bounded by τd = 2 px. Check that per-source signed shift in the logs stays within ±0.5 px.
- **Base drift:** watch mIoU-R13 and inactive IoU.
- **Leakage:** none. The arm uses only train labels and the current model.
- **Speed:** the CPU matching sync could slow steps. P-M3 bounds it.

**Needs:** scipy (present), no new weights. Harness: model wrapper, loss, one trainer line, card with `decision_rule: crack_head`.

---

## Arm 2. `oof_soft_distill` (Study Group Learning with nested folds)

**Hypothesis (S).** P14 showed that the label differences that matter are structural (dotted against joined segments, missing segments): the +0.082 old-to-revised gap was not recovered at all by tolerance (E). Out-of-fold teachers did not train on a cell's labels, so they carry segments the annotators missed and ensemble-like smoothing. Our only clear win so far is a 5-seed ensemble, +0.014 to +0.018 crack IoU (E). Distilling them with SGL's `L = CE(y) + λ·CE(q)` (λ = 1, R) should raise relR@2 and component recall at equal relP@2.

### Change
**Stage A, teachers (nested, no held-out label reaches any student).**
- New split definition `benchmark/splits/cv5v2n.json`: one entry per unordered fold pair {a, b} (10 entries). Train = P532 minus folds a and b (about 319 cells); held-out = fold a ∪ fold b. Built by `bench_make_roots.py` with the B6 asserts as roots `cv5v2n_v11_a{a}b{b}` (val = test = held-out).
- Teacher = card `house_r34_unetpp_pf`, seed 5, v1.1. Dump the held-out cells in canonical fp32 with the standard keys (`p_crack`, `p_inact` used here). Set name `cv5v2n_a{a}b{b}`. 10 runs = 11 GPU-h.
- For student fold k, a train cell c in fold j gets q from teacher {k, j}. That teacher's training set excludes fold k and cell c.

**Stage B, soft targets.** Script `bench/kd/build_soft.py` writes, per outer fold k, `<root cv5v2_v11_kd_f{k}>/soft/<stem>.npz` with `qc`, `qi` (float16, 512 × 512) for every train stem of fold k. Asserts:
- the teacher's `splits/train.txt` contains no fold-k stem and not c (md5 of the teacher root's SPLITS.md5 recorded);
- `qc + qi ≤ 1 + 1e-3`;
- every train stem of fold k has exactly one soft file;
- no held-out stem has one.

**Student keys:**
```
loss.kd3.weight=1.0
loss.kd3.subdir=soft          # resolved against data.root, so the card stays fold-free
```
Roots `cv5v2_v11_kd_f{k}` are identical to `cv5v2_v11_f{k}` plus `soft/`.

**Data.** `BenchmarkELDataset` gets an optional `extra_maps` hook. When set, it passes `masks=[mask, qc, qi]` to the Albumentations call, so flips and rot90 apply identically (brightness and contrast touch the image only). It returns `batch["kd3"]` (2, H, W) float32. A 512 → 512 resize must be a no-op; this is asserted.

**Loss `src/losses/kd3.py`**
```python
class KD3Loss(nn.Module):            # wraps the house ce_dice
    needs_kd3 = True
    def forward(self, logits, masks, kd3):          # logits (B,24,H,W); kd3 (B,2,H,W) = (q_crack, q_inactive)
        L = self.base(logits, masks)
        logp = F.log_softmax(logits.float(), 1)
        lp_c, lp_i = logp[:, 14], logp[:, 11]
        rest = [k for k in range(24) if k not in (11, 14)]
        lp_r = torch.logsumexp(logp[:, rest], 1)    # log of the summed probability of the other 22 classes
        qc, qi = kd3[:, 0], kd3[:, 1]; qr = (1 - qc - qi).clamp_min(0)
        ce = -(qc * lp_c + qi * lp_i + qr * lp_r)   # soft CE on the 3-way grouping (SGL Eq. 2, second term)
        V = (masks != 255).float()
        return L + self.weight * (ce * V).sum() / V.sum().clamp_min(1)
```
- The other 22 classes keep exactly the house supervision through `L`.
- Trainer: one branch next to thin's tube branch (`trainer.py` l.481), `elif getattr(self.sup_criterion, "needs_kd3", False): loss_sup = self.sup_criterion(self.model(images), masks, kd3=batch["kd3"].to(...))`.

**Unit tests:**
- weight 0 means the factory does not wrap (identity check);
- kd3 = grouped one-hot of masks gives the grouped CE exactly;
- all 8 dihedral transforms move qc and qi exactly like the mask;
- the builder refuses a planted teacher whose train list holds a fold-k stem;
- a missing soft file raises.

### Pre-checks
- **Teacher check (CPU, `bench_score` on the 10 teacher dumps).**
  - **Pass:** every teacher has crack relF1@2 ≥ 0.75 and crack IoU ≥ 0.30 on its held-out cells (house at 4/5 data: 0.83 / 0.37, E `H21` §3). Otherwise stop: 3/5-data teachers are too weak to distil from.
- **Descriptive** (no pass rule; it tells what KD carries), per source:
  - share of teacher crack mass (q_c ≥ 0.5) more than 2 px from labels;
  - share of labelled crack px with max q_c < 0.05 within 2 px.

### Screen
- Pre-screen: fold 0, seed 5. It needs teachers {0,1}, {0,2}, {0,3}, {0,4} first (4 × 1.1 + 1.1 = 5.5 GPU-h).
- Screen: 10 students. Total 22 GPU-h with the teachers. The teachers also serve arm 4 and give a 60%-data point for the benchmark.

### What it should move, side effects, drop rule
- **Should move (S):** relR@2 and component recall up +0.01 to +0.02; relP@2 0 to −0.01; strict crack IoU 0 to +0.01; inactive IoU flat to up (q_i is a smoothed target for a 42-cell class).
- **Width:** up to +10% (soft targets spread over the 3 to 4 px visible line).
- **False alarms:** crack-free cell rate up slightly (teacher-found unlabelled cracks score as FP against held-out labels with the same gaps).
- **Drop if:** relF1@2, relR@2 (at relP@2 within 0.01 of baseline) and component recall all gain less than M; or relP@2 falls by more than 0.02; or the width ratio exceeds 1.15 × baseline; or inactive IoU falls by more than M. Also read at matched width.

### Risks
- **Leakage** if teachers are not nested: blocked by the builder asserts. Never use the W1a OOF dumps as targets: their teachers saw the student's held-out fold.
- **Weak teachers** (3/5 data) can drag the student; the teacher check bounds this.
- **Width creep** from soft targets.
- **Gains that are only ensemble distillation:** fine for the score, but do not credit "label repair" without the descriptive check.

**Needs:** no packages, no weights. Harness: nested split json and roots, soft builder, dataset hook, KD3 loss, one trainer branch.

---

## Arm 3. `ridge_snap_labels` (STEAL-style alignment toward the image ridge, offline)

**Hypothesis (S).** Snapping each training crack label to the dark ridge within ±2 px, keeping its width, removes annotator placement noise. That gives a consistent target, and the model gains confidence on faint cracks. This is only true if snapping makes independent annotations of the same crack agree more. P-RS1 tests exactly that and can kill the arm on CPU. STEAL itself aligns to the network output with a level set (R); the model-driven version is arm 1. This arm uses the image ridge as the prior, because it can be checked without a model.

### Change
- New mask set `masks_v11rs` for P532 stems, used **only for training stems**. Held-out masks stay v1.1 strict, so every arm is scored on the same labels.
- Roots `cv5v2_v11rs_f{k}`: train stems linked to `masks_v11rs/masks/`, held-out to v1.1 strict, as the v1.1 roots. No trainer change; same card plus the mask link folder.
- Snapping uses only a cell's own image and label, so one mask set serves all folds without leakage.

**Script `benchmark/scripts/ridge_snap.py`** (CPU, numpy + scipy, `python -I`; `skeletonize_2d` copied from `el_thin/src/data/skeleton.py`, `tangents` from `data_analysis/scripts/annotation_consistency.py`):
```
for stem in P532 (assert not in b6_forbidden):
    I = image float32; Y = v1.1 mask (255 = ignore); Is = gaussian_filter(I, 0.7)
    plan = []
    for comp in label(Y == 14, 8-conn), size >= 3:
        S = skeletonize_2d(comp); pts = argwhere(S)                      # (n,2)
        nrm = unit normal from tangents(S, pts, r=3)                      # (n,2)
        offs = [-2, -1.5, ..., 2]                                         # 9 offsets
        prof = bilinear(Is, pts[:,None] + offs[:,None]*nrm[:,None])       # (n,9)
        ring = mean(bilinear(Is, pts + o*nrm) for o in (-5,-4,4,5))       # (n,)
        rel = (ring[:,None] - prof) / ring[:,None]                         # relative darkness
        o_best = offs[argmax(rel, 1)]
        o_s = median of o_best over skeleton pts within radius 4          # smooth along the crack
        ok = (rel_at(o_s) - rel_at(0) >= 0.02) & (rel_at(o_s) >= 0.03)
        o_s[~ok] = 0
        shift = round(o_s[:,None] * nrm)          # integer (dy,dx), enforce |dy|+|dx| <= 2
        nearest = edt_indices(~S within comp bbox)  # each comp px takes its nearest skeleton point's shift
        new = unique(comp_px + shift[nearest])
        drop new px off-image, on 255, or on padding / frame classes (ids from src/data/class_info)
        accept comp only if 0.9 <= |new| / |comp| <= 1.1 and any shift != 0
        plan.append((comp_px, new))
    Y2 = Y.copy()
    fill = nearest label among px with Y not in {14, 255} (distance_transform_edt return_indices)
    for comp_px, new in plan: Y2[vacated px] = fill[vacated px]
    for comp_px, new in plan: Y2[new] = 14
    write masks_v11rs/masks/<stem>.png; CHANGES.tsv (stem, comps, comps moved, px moved, mean |shift|,
          signed mean dy, dx, px ratio); MANIFEST.md5 (pixel md5)
```

### CPU pre-checks
- **P-RS1 (decisive: does snapping remove annotator noise?).**
  - Pairs, restricted to P532 (assert none forbidden):
    - `CFVS_00015_r7_c4` / `CFVS_00016_r7_c4`: one pixel-identical image, two masks, crack IoU 0.259 (E `out/label_checks_summary.txt` §3);
    - the same-cell crack mask pairs of `label_checks.py` §3, split into the non-copy pairs (22 on the full corpus, aligned IoU median 0.457) and the near-copy pairs (mask reused, about 1 px off).
  - Align each pair with `label_checks.best_shift`. Compute strict crack IoU and relF1@1 between the two masks before and after snapping each mask on its own image.
  - **Pass:** median pair IoU over the non-copy pairs rises by ≥ 0.08; the CFVS pair rises by ≥ 0.08; at most 20% of pairs fall by more than 0.05.
  - **Kill:** median gain < 0.03. Snapping then just imposes another convention.
  - The numbers enter the benchmark as a label-agreement ceiling either way.
- **P-RS2 (sanity), per source:** px ratio, moved px share, mean |shift|, signed mean shift (expect about −0.2 px in x, E).
  - **Pass:** px ratio in [0.97, 1.03] and moved share in [10%, 60%] for every source. Otherwise tune δ (0.02) and the visibility floor (0.03) once.
- **P-RS3 (descriptive, ground truth only):** snapped against original labels on P532: strict IoU, relF1@1, relF1@2 (≥ 0.99 by construction). This is the strict-IoU price of the new convention against the original labels.
- **P-RS4 (descriptive, after wave 1):** on the W1a OOF dumps, compare strict IoU of the house prediction against snapped and against original held-out labels. If it is already higher against the snapped labels, the house model already centres on the ridge and the arm has less to add (S).

### Screen
10 runs, 11 GPU-h. Pre-screen fold 0, seed 5.

### What it should move, side effects, drop rule
- **Should move (S):** strict crack IoU against original labels −0.01 to +0.01; relR@2 and component recall +0.005 to +0.015 (confidence on faint cracks); relF1@1 against snapped held-out labels up (descriptive only, biased toward this arm).
- **Width:** flat (component px ratio kept in [0.9, 1.1]).
- **False alarms:** flat.
- **Drop if:** no headline metric gains M; or strict crack IoU falls by more than M.

### Risks
- Snapping onto gridlines, busbar edges, dislocation clusters or a parallel crack. The ±2 px limit and the 2% dip margin bound this.
- BMRK cells are downscaled, so the ridge is blurred.
- A pair check of about 22 pairs, some at different stress stages with crack growth.
- Scoring on unsnapped labels penalises any convention change. That is why the drop rule reads strict IoU against original labels.

**Needs:** none beyond scipy. Harness: mask link folders, roots.

---

## Arm 4. `oof_selective_ignore` (SelectSeg adapted; RUN_AFTER_GATE G1)

**Gate G1:** arm 2's 10 nested teachers exist and pass the teacher check.

**Hypothesis (S).** Supervising against wrong crack labels (px with no teacher response and often no visible ridge) and against unlabelled real cracks teaches false alarms and suppresses true ones. Ignoring px where the out-of-fold teacher strongly disagrees should raise relP@2 and strict IoU with no new labels. SelectSeg reports that selective training helps on noisy crack data (R, listing; no number retrieved).

### Change
For each outer fold k, the training mask is v1.1 plus extra 255 (ignore) px, built from that fold's soft targets (arm 2, Stage B):
```
F1 = (Y == 14) & (maxpool5x5(q_c) < 0.02)          # labelled crack, no teacher response within 2 px
A  = (q_c >= 0.9) & (Y != 14) & (Y != 255) & (edt_to(Y == 14) > 3)
F2 = components of A (8-conn) with >= 10 px          # confident unlabelled crack, away from any label
Y_sel = Y; Y_sel[F1 | F2] = 255
```
- Inactive is untouched.
- Folder `masks_v11sel_k{k}`; roots `cv5v2_v11sel_f{k}` (train stems to that folder, held-out to v1.1 strict); `data.mask_ignore_value=255` (supported, E LABELS_V11 §4).
- No trainer code. Script `bench/kd/build_select.py` with the same leakage asserts as arm 2.

### CPU pre-check
- Per source: F1 as a share of train crack px; F2 px count.
- Enrichment: share of F1 + F2 px in the 24 B1-flagged train cells (`team_2026-10-29_features/b1_audit/`) divided by their share of train crack px.
- **Pass:** F1 in [0.5%, 15%] of crack px and enrichment ≥ 1.5.
- **No-op (drop):** F1 < 0.5% and F2 < 0.1% of crack px.
- **Too aggressive:** F1 > 15%. Lower the threshold to 0.01 once, else drop.

### Screen
10 runs, 11 GPU-h (no new teachers).

### What it should move, side effects, drop rule
- **Should move (S):** relP@2 and strict crack IoU up +0.005 to +0.015; relR@2 flat; component precision up.
- **Width:** flat.
- **False alarms:** down.
- **Drop if:** strict IoU, relF1@2 and relP@2 (at relR@2 within 0.01) all gain less than M; or relR@2 falls by more than M.

### Risks
- Ignoring faint true cracks that the teacher misses (7% of labelled components are < 2% darker than their surroundings, E). This is the main failure path; watch recall on the CSIR rows.
- F2 removes negative pressure where labels miss cracks, so held-out FP could rise.
- Per-fold masks add bookkeeping: md5 everything.

---

## Arm 5. `adele_confident_add` (ADELE adapted; RUN_AFTER_GATE G2)

**Gate G2 (CPU, on the W1a OOF dumps of `house_r34_unetpp_pf`, open fold roots).**
- Take predicted crack components (p ≥ 0.8, ≥ 10 px) that lie more than 2 px from ground-truth crack.
- Measure the share of their px with a visible dark ridge: relative darkness ≥ 0.03 against a 2 to 4 px ring, the measure of benchmark_el_report §4.3.
- **Pass:** at least 50%, in at least 20 cells.
- **Otherwise park the arm:** confident unlabelled detections are mostly dark spots or gridline edges, and adding them would teach false alarms.

**Hypothesis (S).** After the early-learning point, confident crack components mostly outside the label band are unlabelled cracks. Adding them as labels stops the loss from suppressing real faint cracks, so relR@2 and component recall rise. Additions inside the 2 px band are banned, so labels cannot widen.

### Change
Keys:
```
loss.adele.enable=true
loss.adele.tau=0.8          # R
loss.adele.r=0.9            # R
loss.adele.fit_every=500
loss.adele.min_start=2000
loss.adele.max_start=12000  # S: fallback if the curve criterion never fires
loss.adele.band=2
loss.adele.min_comp=10
loss.adele.outside_frac=0.5
loss.adele.view=hflip
```
Trainer hook (about 30 lines under the flag, in `_train_step`):
1. Every step, accumulate the training-batch crack IoU of argmax against the labels. Store one point per 100 steps, with t in units of 1k steps.
2. Every `fit_every` steps after `min_start`, fit `f(t) = a(1 − exp(−b·t^c))` with `scipy.optimize.curve_fit` (bounds 0 < a ≤ 1, b ≥ 0, c ≥ 0) and `f′(t) = a·b·c·exp(−b·t^c)·t^(c−1)`. Start correcting when `|f′(1) − f′(t)| / |f′(1)| > r` or `step ≥ max_start`. Log the start step.
3. After the start, build the corrected target each step:
```
with torch.no_grad():
    set BatchNorm modules to eval; logits2 = model(hflip(images)); restore train mode
    q = 0.5 * (softmax(logits.detach()) + hflip(softmax(logits2)))
add  = (q[:, 14] >= tau) & (Y != 14) & (Y != 255)
near = maxpool_{(2*band+1)^2}(Y == 14)                     # within band px of a label (Chebyshev)
for each 8-conn component of add (CPU ndimage.label, only images with any add px):
    keep if size >= min_comp and mean(~near over component) >= outside_frac
Y2 = Y; Y2[kept] = 14                                        # additions only; ADELE removes nothing
loss_sup = sup_criterion(logits, Y2)
```
- Only crack is corrected, never inactive (42 train cells; ADELE reports that correcting all classes at once hurts, R).
- The multiscale consistency term and scale views (0.7, 1.5) are left out: rescaling changes crack width in px and is not label-safe.
- SCHP's soft label averaging (`0.5·y + 0.5·q`) is a parked variant.

### Pre-checks
- G2 above.
- **P-A2 (curve fit):** on synthetic IoU series with a known knee, the start step falls within ±1k of the knee. A flat series triggers the `max_start` fallback.

### Screen
10 runs at about 1.35 GPU-h each (one extra no-grad forward from the start step on), 13.5 GPU-h.

### What it should move, side effects, drop rule
- **Should move (S):** relR@2 and component recall +0.01 to +0.02; relP@2 −0.005 to −0.02; strict IoU ±0.01.
- **Width:** flat (no additions in the band).
- **False alarms:** up slightly.
- **Drop if:** relR@2 at matched relP@2 (cross-fitted bias) gains less than M; or relP@2 falls by more than 0.02; or the crack-free cell false-alarm rate rises by more than 0.03 absolute.

### Risks
- Self-confirmation on scuff-like streaks (v1.1 makes scuff ignore in train, but not every streak is labelled), gridline edges, busbar edges.
- BN mode mixing between the two views.
- Curve-fit instability (fallback in place).
- Held-out labels share the gaps the arm fills, so precision falls by construction. Judge at matched width.

---

## 2. Parked papers (no arm) and what would revive them
- **PNT-Edge (49):** revive if arm 1 passes and its τd = 0 control shows the gain comes from alignment. A learned smooth displacement field is then the next step (about 10 build hours, three stages).
- **Align and Segment (51):** revive if per-source CV5-G tables show a width mismatch: predicted width more than 30% off a source's label width (BMRK 3.0, SDLE 3.25 px).
- **Spatial Correction (46):** needs clean validation labels that do not exist, and the measured bias of 0.2 px is below its own 1 px stopping rule. Possible only as a label-noise generator for a benchmark stress track, which is the lead's call.
- **Self-Correction (83):** weight averaging goes to the optimizer family (EMA / SWA); label averaging is a variant of arm 5.

## 3. Totals
- CPU first, about 6 h: P-M1 to P-M4, P-RS1 to P-RS3; G2 and P-RS4 after the W1a dumps.
- GPU for screens: arm 1 13 (+12 control), arm 2 22, arm 3 11, arm 4 11, arm 5 13.5. About 70 GPU-h for all five, 82 with the control.
- Build: about 27 h for all five; arms 1 to 3 = 18 h.
