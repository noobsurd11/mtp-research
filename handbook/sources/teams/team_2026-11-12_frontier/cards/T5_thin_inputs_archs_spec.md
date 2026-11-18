# T5 spec: thin-structure inputs and architecture modules (13 Nov 2026)

Analyst T5. Tags: R = paper, E = our files or a measurement I ran, S = judgement. Paper cards and the CPU pre-checks: `T5_thin_inputs_archs_family.md` (section 0 there holds the numbers quoted as "pre-check A / B / C" here).

## 0. Common frame for every arm
- **Baseline:** method card `house_r34_unetpp_pf` (ResNet-34 U-Net++, PF fine-tune), label set v1.1, 20k steps, batch 8, 512 px, final weights, argmax. Wave-1 W1a runs on `cv5v2_v11_f{0..4}`, seeds 5 and 6, are the reference for every arm; arms run on the same machine type as their reference (DESIGN 5.2 machine rule).
- **Screen:** cv5v2 folds 0 to 4 x seeds 5, 6 = 10 runs per arm, out-of-fold pooled, two-stage group bootstrap (`cv5v2_groups.tsv`), canonical fp32 dumps (TF32 off). Optional fold-0 seed-5 pre-screen (1 run) only to catch crashes, NaNs or a collapse (crack relF1@2 below baseline fold 0 by more than 0.05); it never ranks.
- **Margins:** the lead fixes them after W1a. Below, M_F = margin on crack relF1@2, M_I = strict crack IoU, M_A = inactive IoU, M_m = mIoU-R13, M_c = crack component recall. "Pass" = the named metric beats the baseline by its margin with the bootstrap lower bound above 0 and no guard failing.
- **Guards for every arm:** predicted / GT crack px ratio (house 0.95 on test) must stay in [0.80, 1.15] unless the arm says otherwise; crack-free cell false-alarm rate (prediction >= 50 px on cells with GT < 20 px, PROTOCOL 5.1) must not rise by more than 0.03; mIoU-R13 must not fall by more than M_m; per-source tables (ARTS, BMRK, CFVS, CSIR, SDLE) are read for any source losing more than 0.03 crack IoU.
- **Development reads:** F51 / H36 dumps (descriptive; H36 crack labels are speck-level). Legacy test and E1 stay sealed.
- **New harness feature asked for by arms 2 and 3 (and useful for all):** a perturbation probe in `scripts/bench_infer.py`: `--perturb {gamma0.6, gamma1.6, contrast0.5, blur1, noise0.02}` applied to the held-out fold image in [0, 1] before normalisation (I^0.6; I^1.6; 0.5 + 0.5 (I - mean(I)); Gaussian sigma 1 px; additive N(0, 0.02) with a fixed per-stem seed), dumped as set `cv5v2_f{k}@{name}` and scored against the fold's own GT. Inference only, about 5 GPU-min per run per perturbation (S). Reported as the drop in crack relF1@2 and relR@2 from clean. Held-out fold cells only, so nothing sealed is touched. Build about 2 h.

## Priority table

| # | Arm | Papers | Route | Build h | Screen GPU-h | Priority | Status |
|---|---|---|---|---|---|---|---|
| 1 | dti_hysteresis | 14 | inference_only | 3 | 0 (CPU) | 72 | RUN_NOW (needs W1a dumps) |
| 2 | crackcue_input | 7 | new_model_code (input-only) | 4 | 11 | 66 | RUN_NOW |
| 3 | liot_input | 18 | new_model_code (input-only) | 1.5 on top of arm 2 | 11 | 55 | RUN_NOW |
| 4 | thin_geometry_aux | 16, 37 | new_loss | 8 | 11.5 | 50 | RUN_NOW |
| 5 | fullres_detail_head | 14 | new_model_code | 3 + 1 (gate script) | 12.5 | 40 | RUN_AFTER_GATE (grid-snap index) |
| 6 | super_decoder_x03 | 22 (39 as a later variant) | new_model_code | 8 | 12 | 32 | RUN_AFTER_GATE (grid-snap index or arm 5) |

Input-only (cheap) = arms 2 and 3: they change only what the stem sees, through one shared wrapper, and the rest of the model, loss and recipe stay the house PF. Arm 1 needs no training at all. Arms 4 to 6 need model code.

---

## Arm 1. dti_hysteresis (FR-UNet's dual-threshold iteration, done properly)
**Papers:** rank 14 (FR-UNet). **Route:** inference_only.

**Hypothesis (S).** Faint crack segments that touch confident crack are real more often than faint pixels elsewhere. Growing the crack mask from confident seeds into low-margin pixels raises relR@2 at a fixed relP@2 more than the global logit bias (already run, BRIEF 5), because new pixels can only join existing detections.

**Change.** New CPU module `bench/postproc/hysteresis.py` and script `scripts/bench_dti.py` (numpy + scipy). Inputs: per-cell dumps `m_crack` (float16, log s_crack minus max other log s) and `oth` (uint8) from DESIGN 3.1.
```
def dti(m, oth, t_hi, t_lo):            # m: (512,512) float32 from float16; t_lo <= t_hi (margin units)
    low  = m > t_lo
    lab, n = ndi.label(low, structure=np.ones((3, 3), bool))     # 8-connected
    keep = np.unique(lab[(m > t_hi) & low]); keep = keep[keep > 0]
    crack = np.isin(lab, keep)
    return np.where(crack, 14, oth).astype(np.uint8)
```
- t_lo = t_hi = t is exactly the global bias rule with b = -t, so the bias comparator is nested in the grid.
- Grid: t_hi in {-1, -0.5, 0, 0.5, 1, 2}; t_lo in {-6, -5, -4, -3, -2, -1.5, -1, -0.5, 0, 0.5, 1, 2}, t_lo <= t_hi (60 pairs).
- Operating point by cross-fitting (PROTOCOL 3.2 rule): for held-out fold k and seed s, pick the pair that maximises pooled crack relF1@2 on the other four folds' OOF dumps of seed s; apply it to fold k. Comparator: the bias-only point (t_lo = t_hi) chosen the same way. Also report the full frontier: for each t_hi the best t_lo, as relR@2 vs relP@2, against the bias sweep curve.
- This is real hysteresis (all connected growth). FR-UNet's released code makes one raster pass (family card 1.1); not reproduced, since it depends on scan order (S).
- Unit tests (`tests/test_bench_dti.py`): (a) t_lo = t_hi = 0 reproduces `pred` except logged float16 ties (as I3); (b) toy map: a seed at m = 3 joined to a chain at m = -1 is grown with (t_hi 0, t_lo -2); an isolated blob at m = -1 is not; (c) output classes in 0..23; (d) refuses sealed set names (reuse the dump guard).

**CPU pre-check.** None needed; the arm is itself CPU (about 20 min for 60 pairs x 10 runs x 532 cells, S).

**Screen.** All 10 W1a baseline runs (cross-fitted per seed). Descriptive: the same frozen pair applied to F51 dumps.

**Should move:** crack relR@2 up at matched relP@2; crack component recall (>= 20 px) up; relF1@2 up at the cross-fitted point. Strict crack IoU flat or up.
**Drop if:** at the cross-fitted point, relF1@2 over the cross-fitted bias point is below M_F, or the frontier gain in relR@2 at relP@2 = 0.90 and at the baseline's relP@2 is below 0.01 with a bootstrap bound at or below 0, or the width ratio exceeds 1.15.
**Side effects:** width up (growth adds pixels beside cracks); new false-alarm components cannot appear (growth only from seeds), so component precision should hold; pixel relP@2 drifts down.
**Cost:** build 3 h, GPU 0.
**Needs:** W1a dumps with `m_crack` and `oth` (planned); nothing new to install.
**Risks / how it could mislead:** (1) an operating-point shift that looks like a gain: guarded by comparing to the nested, equally cross-fitted bias point and by the frontier at matched precision; (2) choosing on the same seed's other folds is clean (no held-out cell is used for its own threshold); (3) width inflation could raise relR@2 trivially: the 1.15 guard and the any-hit vs 50%-coverage component recall pair expose it.

---

## Arm 2. crackcue_input (training-free coarse crack cue as a second input channel)
**Papers:** rank 7 (CrackCue); the shared wrapper also hosts arm 3. **Route:** new_model_code, input-only.

**Hypothesis (S).** A cue that is high where a pixel is darker than the 8 px max-pooled background gives the stem a contrast-normalised, crack-shaped signal before the first stride. It should help weak-contrast sources (CSIR, BMRK) and faint cracks. In the paper, the coarse cue alone gives 0.043 of the 0.057 ODS gain (R, CrackLS315). Pre-check B (E): the coarse cue is the only fixed cue above raw darkness (AUROC 0.806 vs 0.762), above raw in 4 of 5 sources, with spread 0.159 vs 0.276.

**Change.** New file `src/models/cue_input.py`; factory branch `model.name: cue_unetpp` (add to `_build_core` and its error message). Config keys (model section): `cue: crackcue_coarse`, `cue_k: 8`, `cue_eps: 0.02`, `cue_mean: [0.0945]`, `cue_sd: [0.1494]` (pre-check C, label-free statistics of the 532 pool images), plus the house keys `encoder_name: resnet34`, `encoder_weights: imagenet`, `in_channels: 1`, `num_classes: 24`.
```
class CueTransform(nn.Module):                       # no parameters, no RNG
    def forward(self, x):                            # x: (B,1,512,512), normalised (I - 0.5) / 0.25
        with torch.autocast(x.device.type, enabled=False):
            I = (x.float() * 0.25 + 0.5).clamp(0, 1)
            if kind == "crackcue_coarse":
                mp = F.max_pool2d(I, k, stride=k)                                  # (B,1,64,64)
                Bc = F.interpolate(mp, size=I.shape[-2:], mode="bilinear", align_corners=False)
                q  = ((Bc - I) / (Bc + eps)).clamp(0, 1)                           # (B,1,512,512)
            elif kind == "liot":                                                    # arm 3
                P = F.pad(I, (8, 8, 8, 8), mode="replicate"); ch = []
                for dy, dx in ((0, -1), (0, 1), (-1, 0), (1, 0)):                   # left, right, top, bottom
                    c = torch.zeros_like(I)
                    for d in range(1, 9):
                        c += (I > P[..., 8+dy*d : 8+dy*d+H, 8+dx*d : 8+dx*d+W]).float() * 2 ** (d - 1)
                    ch.append(c / 255.0)
                q = torch.cat(ch, 1)                                                # (B,4,512,512)
            return (q - mean.view(1, -1, 1, 1)) / sd.view(1, -1, 1, 1)

class CueUnetPP(nn.Module):
    def __init__(self, cfg):
        net = smp.UnetPlusPlus(encoder_name="resnet34", encoder_weights="imagenet", in_channels=1, classes=24)
        self.encoder, self.decoder, self.segmentation_head = net.encoder, net.decoder, net.segmentation_head
        self.cue = CueTransform(cfg)
        self.cue_side = nn.Conv2d(k_c, 64, 7, stride=2, padding=3, bias=False)   # k_c = 1 (crackcue) or 4 (liot)
        nn.init.zeros_(self.cue_side.weight)                                      # function-preserving at init
        self._side = None
        self.encoder.conv1.register_forward_hook(lambda mod, inp, out: out + self._side)
    def forward(self, x):
        self._side = self.cue_side(self.cue(x))      # (B,64,256,256), added to conv1 output before bn1
        try:
            return self.segmentation_head(self.decoder(self.encoder(x)))
        finally:
            self._side = None
```
- Equivalent to a conv1 over [raw, cue] whose cue weights start at zero, but the cue weights live in `cue_side.*`, outside `encoder.*`, so under PF they train at the house lr from step 0 while the encoder is frozen for 1k steps (train.py l.117-123 splits on the `encoder.` prefix). Parameter names of the house model are unchanged, so `encoder_init`, PF and the scorers' factory build work as before.
- Brightness / contrast augmentation runs before the model, so the cue is computed on the augmented image, at train and test alike, with no dataset change. The dump writer and `bench_infer` see the cue automatically because it lives inside the model.
- Method card `bench/methods/cue_crackcue_unetpp_pf.yaml` = the PF card with `model.name=cue_unetpp` and the cue keys; `diff_ref: house_r34_unetpp_pf`.
- Unit tests (`tests/test_cue_input.py`): (a) with `cue_side` zero, logits equal `smp_unetpp` built from the same torch seed, max abs diff 0 (CPU fp32); (b) state-dict keys = house keys + `cue_side.weight`; PF group 2 holds every `encoder.*` and no `cue_side.*`; (c) a 1 px dark line of contrast 0.1 on a flat 0.6 field gives q about 0.1 / 0.62 on the line and 0 more than 8 px away; (d) CueTransform draws no RNG and is identical in train and eval mode; (e) cue mean / sd come from the config (asserted), not from the batch.

**CPU pre-check (done, E, pre-check B).** Pass rule: AUROC_all >= raw + 0.02 and per-source spread below raw. Result 0.806 vs 0.762 and 0.159 vs 0.276: **pass**. Shared risk flagged: AUROC vs line classes 0.349 (the cue lights up busbars, gridlines, ribbons and borders more than cracks).

**Screen.** 10 runs + perturbation probe on all 10 runs and the 10 W1a baseline runs.

**Should move:** crack relF1@2 and relR@2 up; CSIR and BMRK crack IoU up; smaller relF1@2 drop under gamma0.6 / contrast0.5 / blur1 than the baseline.
**Drop if:** no headline metric passes its margin and the mean probe drop is not smaller than the baseline's by at least 0.02; or the crack-free false-alarm rate rises by more than 0.03; or gridline or busbar IoU falls by more than 0.02.
**Side effects:** false alarms on lines and cell borders (the cue is high along dark borders next to bright cell area and in padding edges), predicted width about unchanged.
**Cost:** build 4 h (wrapper, both cue kinds, tests, two method cards); GPU 11 + 0.3 smoke; memory + about 0.3 GB (S), measured in the smoke.
**Needs:** nothing new (torch only).
**Risks / how it could mislead:** (1) the constants use the 532 pool images including held-out folds, without labels; if the lead wants zero contact, recompute them on each fold's train stems (expected change under 1%, S); (2) a gain in relR@2 bought by more line false alarms: read relP@2, component precision and the per-class FP table together; (3) BMRK cells are downscaled and padded, and their 3 px labelled cracks are blurrier, so k = 8 may be too small there (per-source table).

---

## Arm 3. liot_input (raw + LIOT order code)
**Papers:** rank 18 (LIOT). **Route:** new_model_code, input-only (same wrapper as arm 2).

**Hypothesis (S).** LIOT is invariant to any monotone intensity change, so a stem fed with it should depend less on source contrast. The paper's gains are under shift and perturbation, not in-distribution (R: in-dataset average F1 0.803 to 0.801; perturbed 0.455 to 0.691; cross-retina 0.735 to 0.767). Pre-check B (E): smallest per-source spread of any cue (0.099 vs raw 0.276), as good as raw against lines (0.517), weak on low-contrast cracks (0.445). Expect in-distribution CV to be flat; the probe is the main reading.

**Change.** As arm 2 with `cue: liot`, `cue_mean: [0.3905, 0.3896, 0.3723, 0.3732]`, `cue_sd: [0.4460, 0.4459, 0.4308, 0.4308]` (pre-check C), `cue_side` in_channels 4. Raw input kept (the paper replaces it; a LIOT-only follow-up is gated on this arm's probe result). Method card `cue_liot_unetpp_pf.yaml`.
- Extra unit tests: (a) LIOT output for a*I + b (a > 0, no clamping) equals that of I exactly; (b) a pixel brighter than all 8 left neighbours gets 255 in the left channel; (c) replicate padding: a constant image gives 0 everywhere.

**CPU pre-check (done, E).** Pass rule for an invariance cue: per-source spread <= raw - 0.10. Result 0.099 vs 0.276: **pass**. Its overall AUROC (0.725) is below raw, which is expected for a contrast-free code and is not a kill.

**Screen.** 10 runs + perturbation probe (as arm 2).
**Should move:** smaller relF1@2 / relR@2 drops under gamma, contrast and blur than the baseline; non-inferior in-distribution headline metrics; per-source spread of crack IoU narrower.
**Drop if:** the mean probe drop is not smaller than the baseline's by at least 0.02, or any headline metric falls by more than its margin.
**Side effects:** LIOT amplifies sensor noise and multi-crystalline grain in flat regions (a 1-grey-level difference sets a bit), so false alarms on crack-free multi cells may rise; width about unchanged.
**Cost:** build 1.5 h after arm 2; GPU 11; memory + about 0.5 GB (S).
**Needs:** nothing new.
**Risks / how it could mislead:** (1) the house already trains with brightness / contrast jitter of 0.2, which covers part of the invariance (so a null in-distribution is expected and is not evidence against E1 robustness); (2) the probe's perturbations are synthetic; E1's shift is layout (half-cut) and scuff, which LIOT does not address; claim only what the probe measures; (3) gamma changes are monotone, so LIOT is invariant by construction: the probe on gamma favours LIOT by design; read contrast0.5 and blur1 (not exactly invariant) as the fairer tests.

---

## Arm 4. thin_geometry_aux (auxiliary FIDT and orientation heads, training only)
**Papers:** rank 16 (FIDT maps), rank 37 (orientation + segmentation). **Route:** new_loss (+ a small head).

**Why stacked (S).** Both are dense auxiliary targets derived from the same crack skeleton, both are dropped at inference (so argmax, dumps and scorers are unchanged), they share every build part (target hook, aux head, loss term), and each alone is a small regulariser that may not show at screen resolution. If the stacked arm passes, a 2-arm decomposition (FIDT only, orientation only, 22 GPU-h) follows; if it fails cleanly (no metric moves, no guard fails), both are closed under this setting.

**Hypothesis (S).** A 1 px label jitter flips a binary target but moves a distance-based target only slightly (FIDT at 1 px = 0.5 vs 1 at the skeleton), and crack orientation is nearly unchanged by jitter. These targets push the shared decoder to encode where the centreline is and which way it runs, which should help keep long cracks connected (component recall) without widening predictions.

**Change.**
- `src/data/geom_targets.py`: `GeomTargetDataset(ds, crack_class=14, dmax=20, ori_bins=16, ori_radius=2)`, a wrapper like el_thin's `TubedSkeletonDataset` (computes on the **augmented** mask, draws no RNG, returns image and mask unchanged), adding `fidt` (float16 (H, W)) and `ori` (uint8 (H, W), 255 = ignore):
```
c = mask == 14                                     # ignore (255) px are not crack
skel = skeletonize_2d(c)                           # el_thin src/data/skeleton.py (equals skimage)
if not skel.any(): fidt = 0; ori = 255
d, (iy, ix) = ndi.distance_transform_edt(~skel, return_indices=True)
fidt = 1 / (d ** (0.02 * d + 0.75) + 1); fidt[d > dmax] = 0     # 1.0 at 0 px, 0.50 at 1, 0.37 at 2, 0.24 at 4
# orientation from second moments of skeleton px in a 7x7 box (closed form, vectorised):
S = skel.astype(f32); n = box7(S); mx = box7(S*X)/n; my = box7(S*Y)/n
sxx = box7(S*X*X)/n - mx**2; syy = box7(S*Y*Y)/n - my**2; sxy = box7(S*X*Y)/n - mx*my
theta = 0.5 * atan2(2*sxy, sxx - syy) mod pi
bin = floor((theta + pi/32) / (pi/16)) mod 16       # centred bins: horizontal = 0, vertical = 8 (pre-check found that
                                                    # un-centred floor(theta / (pi/16)) puts a horizontal line in bin 15)
valid_skel = skel & (n >= 3)
ori = where((d <= ori_radius) & valid_skel[iy, ix], bin[iy, ix], 255); ori[mask == 255] = 255
```
  (box7 = 7x7 box sum via `ndi.uniform_filter(..., 7, mode="constant") * 49`; X, Y = pixel coordinate grids.) The FIDT constants (0.02, 0.75, 1) are my choice (S); the paper's constants are unverified.
- `src/models/aux_heads.py`: `AuxGeomUnetPP` exposes `encoder`, `decoder`, `segmentation_head` of the house smp model plus `aux_head = Sequential(Conv2d(16, 32, 3, padding=1, bias=False), BatchNorm2d(32), ReLU, Conv2d(32, 17, 1))` on the decoder output (B, 16, 512, 512). `forward(x)` returns the 24-class logits only; `forward_train(x)` returns (logits, aux) with aux (B, 17, 512, 512).
- `src/losses/geom_aux.py`: `L = ce_dice(main, mask) + w_f * sum(w * (sigmoid(aux[:,0]) - fidt)^2) / sum(w) + w_o * CE(aux[:,1:17], ori, ignore_index=255)`, w = (mask != 255) * (1 + 9 * fidt); the orientation term is 0 when a batch has no valid px.
- Trainer: a branch like the existing `absh_on` path (trainer l.470-480 in el_thin): when `loss.geom_aux.enabled`, call `forward_train` and pass `batch["fidt"]`, `batch["ori"]`. Factory `model.name: auxgeom_unetpp`. Keys: `loss.geom_aux.{enabled: true, fidt_weight, ori_weight, dmax: 20, ori_bins: 16, ori_radius: 2}`.
- Weights fixed before the screen by one rule: a 500-step smoke on fold 0 train stems only; log the gradient norm at the decoder output from each term; set w_f and w_o so each auxiliary term's median gradient norm over steps 100 to 500 is 0.25x the main term's (one significant digit); write them into the method card. Default if the smoke is skipped: w_f 1.0, w_o 0.1 (S).
- Unit tests (`tests/test_geom_aux.py`): (a) the wrapper leaves image and mask byte-identical and draws no RNG (as thin's test); (b) fidt is 1 on the skeleton and 0.5 at 1 px; (c) a horizontal line gives bin 0 (not 15), a vertical line bin 8, a 45 degree line bin 4 or 12 (depending on the y axis sign; assert the convention); (d) hflip of the mask maps bin b to (16 - b) mod 16; (e) `forward` equals `segmentation_head(decoder(encoder(x)))` and a checkpoint without `aux_head.*` loads into `smp_unetpp` with only those keys unexpected; (f) the loss equals house ce_dice when both weights are 0.

**CPU pre-check (done, E, `T5_precheck/t5_geom_precheck.out` de9f3a60; 229 pool cells with >= 20 crack px, v1.1, skimage skeletonize, 1 px shifts in 4 directions).** Rules and results: (1) share of crack px with a valid orientation target >= 0.70: **0.992**; (2) orientation within +-1 bin (circular) under a 1 px label shift for >= 90% of px valid in both: **0.958**; (3) Pearson correlation of the FIDT targets of a mask and its 1 px shift >= 0.8: **median 0.919** (binary IoU of the same shifts: median 0.548). **Pass on all three.** The targets are as jitter-tolerant as the hypothesis needs; this says nothing yet about whether the decoder benefits.

**Screen.** 10 runs.
**Should move:** crack component recall (>= 20 px) and relR@2 up, relF1@2 up; strict crack IoU flat; width ratio at or below the baseline's.
**Drop if:** no headline metric passes its margin and component recall gains less than M_c (default 0.02 if the lead sets none).
**Side effects:** width neutral to narrower; false alarms neutral; possible small loss on other classes from sharing the 16-channel final features (watch mIoU-R13 and gridline IoU).
**Cost:** build 8 h; GPU 11.5 (skeleton + EDT per sample in data workers, about 10 to 30 ms, S; check steps/s in the smoke).
**Needs:** `src/data/skeleton.py` from el_thin (already cherry-picked into el_bench per LEAD_INSTRUCTIONS); scipy (present).
**Risks / how it could mislead:** (1) a too-high w_f pulls crack logits towards a smooth halo and widens predictions, which inflates relR@2; the width guard catches it; (2) targets must be computed after augmentation (flips and rot90 change orientation bins); test (d) enforces it; (3) cells without crack get FIDT 0 everywhere, which also teaches "no crack here" and could lower recall on faint cracks: read relR@2 per source.

---

## Arm 5. fullres_detail_head (FR-UNet's full-resolution stream, as a residual head)
**Papers:** rank 14. **Route:** new_model_code. **Status:** RUN_AFTER_GATE.

**Hypothesis (S).** Our full-resolution decoder node has no skip (family 0.1), so the position of a 1 to 2 px line inside each 2x2 block can only come from neighbouring stride-2 features. A shallow stride-1 branch on the image, fused at the end, lets the output follow the exact dark ridge. Evidence against a big effect: the stride-2 oracle ceiling is 0.692 (pre-check A, E), above the label ceiling, and 2x input (R5) was n.d.

**Gate (CPU, on W1a baseline dumps; build 1 h).** Grid-snap index. For the predicted crack mask P on each held-out fold and for grid offsets o = (0, 0) (aligned with conv1: output px 2i and 2i+1 copy stride-2 feature i) and o = (1, 1) (control): share(o) = fraction of P px that lie in a 2x2 block (offset o) fully inside P. GSI = share(0, 0) - share(1, 1). Compute the same on GT. **Pass if GSI_pred >= 0.10 and GSI_pred - GSI_GT >= 0.08, with the group-bootstrap 90% lower bound of GSI_pred - GSI_GT above 0.05.** Pass means the house output is snapped to the stride-2 grid and a full-resolution path has something to fix; fail parks the arm.

**Change.** New file `src/models/detail_head.py`; factory `model.name: detail_unetpp`; key `model.detail_channels: 16`.
```
class DetailUnetPP(nn.Module):
    def __init__(self, cfg):
        net = smp.UnetPlusPlus("resnet34", encoder_weights="imagenet", in_channels=1, classes=24)
        self.encoder, self.decoder, self.segmentation_head = net.encoder, net.decoder, net.segmentation_head
        c = 16
        self.detail = Sequential(conv3x3(1, c), BN(c), ReLU, conv3x3(c, c), BN(c), ReLU, conv3x3(c, c), BN(c), ReLU)  # stride 1
        self.fuse = Sequential(conv3x3(16 + c, 16), BN(16), ReLU, Conv2d(16, 24, 1))
        nn.init.zeros_(self.fuse[-1].weight); nn.init.zeros_(self.fuse[-1].bias)       # identical to house at init
    def forward(self, x):                                   # x (B,1,512,512)
        f = self.decoder(self.encoder(x))                   # (B,16,512,512)
        return self.segmentation_head(f) + self.fuse(torch.cat([f, self.detail(x)], 1))
```
- Parameter names `detail.*`, `fuse.*` are outside `encoder.*` (house lr under PF).
- Unit tests: (a) logits equal `smp_unetpp` from the same seed at init (fuse zero); (b) shapes and dtypes under bf16 autocast; (c) PF group split as arm 2 (b).

**Screen.** 10 runs.
**Should move:** strict crack IoU up; width ratio closer to 1; relF1@2 flat (pre-check A says a 2 px tolerance hides grid effects).
**Drop if:** strict crack IoU gain below M_I, or relR@2 falls by more than M_F.
**Side effects:** narrower predictions (lower width), possible speckle false alarms from a branch that sees pixel noise (watch component precision and crack-free false alarms).
**Cost:** build 3 h + 1 h gate; GPU 12.5 (+ about 1.5 GB activations at batch 8, S; measured in the smoke).
**Needs:** nothing new.
**Risks / how it could mislead:** a strict-IoU gain from narrower lines can come from matching the per-source label width convention, not from finding more cracks; report the per-source width ratio and relR@2 beside IoU.

---

## Arm 6. super_decoder_x03 (SUPER-style wavelet suppression block at the stride-2 node)
**Papers:** rank 22 (SUPER); rank 39 (HWD) as a later variant. **Route:** new_model_code. **Status:** RUN_AFTER_GATE.

**Gate.** Arm 5's gate passes, or arm 5 passes on strict crack IoU. (Both arms bet that the finest decoder stage limits crack shape; there is no reason to build the costlier one if the cheap test says the output is not grid-bound.)

**Hypothesis (S).** Learned suppression of detail subbands at the finest skip removes finger and texture responses while the inverse DWT keeps crack detail, so strict crack IoU and pixel precision rise. Paper (R): 0 to 2 px crack IoU 0.356 to 0.451 on CrackVision12K, no crack ablation, no code, stage placement not stated.

**Change.** New file `src/models/super_block.py`; factory `model.name: super_unetpp`; keys `model.super_cd: 128`, `model.super_scale_init: 0.1`. Replace only smp's `decoder.blocks["x_0_3"]` (in: x_0_2, 64 ch at 128 px; skip: cat[x_1_3, x_2_3, x_3_3, conv1 feature] = 256 ch at 256 px; out 32 ch at 256 px; smp decoder.py l.124-138, l.166-168).
```
haar(z): a=z[...,0::2,0::2], b=z[...,0::2,1::2], c=z[...,1::2,0::2], d=z[...,1::2,1::2]
         LL=(a+b+c+d)/2, LH=(a+b-c-d)/2, HL=(a-b+c-d)/2, HH=(a-b-c+d)/2  -> cat on channels (orthonormal)
ihaar: exact inverse.
class SuperBlock(nn.Module):           # signature as smp DecoderBlock: forward(x, skip)
    g  = Conv2d(256, 32, 1)            # skip compress, at 256 px
    h  = Conv2d(64, 32, 1)             # deeper decoder feature, at 128 px
    gn = GroupNorm(4, 128)             # one group per band
    Fd = Sequential(conv3x3(128,128), BN, ReLU, conv3x3(128,128), BN, ReLU)
    A  = CBAM(128, reduction=16, spatial_kernel=7)
    s  = Parameter(full(128, 0.1))
    g2 = Sequential(Conv2d(32, 32, 1, bias=False), BN(32), ReLU)
    def forward(self, x, skip):        # x (B,64,128,128), skip (B,256,256,256)
        W  = haar(self.g(skip))                         # (B,128,128,128): bands LL|LH|HL|HH, 32 ch each
        Z  = W.clone(); Z[:, :32] += self.h(x)          # sum fusion into LL
        Sx = torch.tanh(self.A(self.Fd(self.gn(Z)))) * self.s.view(1, -1, 1, 1)
        return self.g2(ihaar(W - Sx))                   # (B,32,256,256)
```
- The rest of the decoder (including `x_0_4`) is unchanged. Decoder state-dict keys for `x_0_3` change, so `decoder_init` from a house checkpoint must skip that block (state it in the method card).
- Unit tests: (a) ihaar(haar(z)) == z (max abs err < 1e-5); (b) with s = 0 the block output equals g2(g(skip)); (c) output shape (B, 32, 256, 256); (d) parameter count delta logged.
- HWD variant (rank 39) for later: replace `encoder.maxpool` with Haar DWT + 1x1 conv (4C to C) + BN + ReLU, the 1x1 initialised to pass LL / 2 (equals average pooling); only if this arm passes.

**Screen.** 10 runs.
**Should move:** strict crack IoU and crack pixel precision up; component precision up; width slightly down.
**Drop if:** strict crack IoU gain below M_I and crack pixel precision gain below 0.02.
**Side effects:** fewer line false alarms if suppression works; risk of losing faint cracks (relR@2 down).
**Cost:** build 8 h; GPU 12 (CBAM + 2 convs at 128 ch, 128 px: moderate, S).
**Needs:** nothing new (Haar as fixed slicing; no pytorch_wavelets).
**Risks / how it could mislead:** an implementation from the paper text, not the authors' code (call it "SUPER-style" in the benchmark); the placement at one node is my choice; a null closes only this placement.

---

## 7. Order of work (S)
1. Now: build the shared cue wrapper (arms 2, 3; 5.5 h) and the perturbation probe (2 h). Pre-checks for arms 2, 3 and 4 are done (pass). Queue arms 2 and 3 right after W1a (22 GPU-h; cv02 lanes).
2. When W1a dumps exist: arm 1 (CPU, 3 h build) and the grid-snap gate for arms 5 and 6 (CPU, 1 h).
3. Build arm 4 (8 h) while arms 2 and 3 train; then queue it (11.5 GPU-h).
4. Arms 5 / 6 only if the gate passes.
Total if all run: about 58 GPU-h and 30 build h.

## 8. Gated follow-ups (not arms; one line each)
- `crackcue_refined` (rank 7): learned background net per fold (train stems only; crack dilated to 5 px and inactive masked from L_rec), cue |I - B_f|; only if arm 2 passes. Build 6 h, GPU 11 + 2.
- `liot_only` (rank 18): LIOT replaces raw (conv1 re-learned from 4 channels); only if arm 3's probe passes but its in-distribution metrics are flat.
- `iternet_refine` (rank 79): 3 shared-weight mini-UNets (32-64-128 ch) on [x, softmax crack, softmax inactive, decoder output 16 ch], residual logits for crack / inactive, loss on every iteration; only if arm 1 passes. Build 6 h, GPU 13.
- `dsconv_x03` (rank 67): DSConv (x, y, standard, fused) replacing the 3x3 convs of `x_0_3`; only if arm 5 or 6 passes. The official DSCNet 2D model is a benchmark-suite entry regardless (BENCH_ONLY).
