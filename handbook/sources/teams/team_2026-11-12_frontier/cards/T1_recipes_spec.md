# T1 Training recipe and fine-tuning: experiment specifications (13 Nov 2026)

Analyst T1. Tags: R = paper, E = our files, S = my judgement. Paper cards: `T1_recipes_family.md`. Ledger: `ledger/T1.tsv`.
Six arms, in priority order. Code paths refer to the `el_bench` worktree (mirror `harness/el_bench_src/`); line numbers to the `el_f3` snapshot in `harness/src_snap/`.

## 0. Common frame (applies to every arm)
- **Comparator:** card `house_r34_unetpp_pf` (PF), label set v1.1, 20k steps, batch 8, 512 px, final weights, argmax24. W1a supplies PF and house runs on `cv5v2_v11_f{0..4}`, seeds 5 and 6. Every arm runs on the same machine type as its W1a comparator (cv02 A6000); one precision (canonical fp32 dumps, TF32 off).
- **Pairing (E, `src/data/stream.py`):** batches are a function of (seed, stream id, batch index) only. Arms that do not change sampling see the identical batch sequence and the identical init as PF for the same fold and seed, so contrasts are paired by fold x seed. RCS breaks this pairing (new sampler); its contrast is paired by fold x seed only through init.
- **Screen:** cv5v2, 5 folds x seeds 5, 6 = 10 runs, out-of-fold pooled, two-stage group bootstrap (330 groups of `cv5v2_groups.tsv`, then seed per fold x arm), as `b6_verdict.py`. Optional fold-0 seed-5 pre-screen (about 1.1 GPU-h) to catch failures only.
- **Headline:** crack relF1@2 with relP@2 / relR@2, strict crack IoU, inactive IoU, mIoU-R13. **Always also:** predicted / GT crack px (width flag), crack component precision, crack-free cell false-alarm rate (prediction >= 50 px on a cell with GT < 20 px), per-source table. F51 / H36: dumped from all 10 fold models of the arm and of PF, scored per model, compared as the paired mean over the 10 fold x seed pairs (development read only). Legacy test and E1 stay sealed.
- **Operating point:** argmax is primary. Secondary: crack bias chosen by cross-fitting (fold k uses the bias that maximises relF1@2 on the other 4 folds' OOF cells, width guard relP@2 drop <= 0.05, PROTOCOL 5.3). Any arm whose argmax gain disappears at the matched bias is reported as an operating-point shift, not a gain.
- **Pass margin:** "M(metric)" below = the margin the lead fixes after W1a measures seed and fold noise. Reference (E): inactive IoU contrast SE 0.038 to 0.039 at 2 seeds on CV, so inactive moves under about 0.1 are not resolvable unpaired; paired readout arms (2, 3) do not have that problem.
- **Weights keys:** arms 2, 3 and 5 add new keys to `latest.pth` `models` (`ema_999`, `ema_9998`, `swad`, `raw_bn`, `ema_999_bn`, `ema_9998_bn`, `swad_bn`). Proposal for the card schema: an optional `readouts: [{name, weights_key}]` list; `bench_infer.py --weights-key K` reads `models[K]`, records it in the manifest; a table row = card + weights key. Cards still validate with the old enum when `readouts` is absent.
- **Shared utility (built once, used by arms 2, 3, 5, 6):** `src/trainers/weight_avg.py` (averagers + BN recalibration), spec in arm 2.

---

## Arm 1. `rcs`: DAFormer rare class sampling on the R13 classes
- **Papers:** 021, 043 (RCS part), 033 (RCS part). Priority 85. Route: data_pipeline.
- **Hypothesis:** inactive (48 P532 cells), splice (60), edge_dark (43), material (116) are data-limited. Drawing cells by rare class raises their pixel share 1.6 to 2.5x (E, pre-check) and their IoU.
- **Change:** PF card plus
  - `data.rcs.enable=true`, `data.rcs.temperature=0.01`, `data.rcs.classes=[0,1,2,4,5,7,11,13,14,15,16,20,21]`, `data.rcs.min_px=20`.
  - New file `src/data/rcs.py`:
    ```
    def rcs_tables(mask_paths, classes, T, min_px):           # training stems of THIS root only (splits/train.txt)
        px = zeros(N, 24, int64)                              # per-cell class px; ignore (255) px skipped
        for i, p in enumerate(mask_paths): m = read(p); px[i] = bincount(m[m < 24], minlength=24)
        f = px[:, classes].sum(0) / px[:, :24].sum()          # pixel fraction, DAFormer Eq. 6, over all classes' px
        P = softmax((1 - f) / T)                              # Eq. 7, shape (len(classes),)
        lists = [nonzero(px[:, c] >= min_px) for c in classes]
        drop classes with empty list, renormalise P; assert len(lists) >= 1
        return P, lists, px
    class RCSSampler(Sampler):                                # same interface as SeededSampler
        __init__(n, bs, seed, stream, start_batch, P, lists)
        __iter__: for b from start_batch: for j in range(bs):
            rng = np.random.Generator(np.random.PCG64(mix_seed(seed, stream, 2, b, j)))
            k = rng.choice(len(P), p=P); idx = lists[k][rng.integers(len(lists[k]))]
            yield int(idx), mix_seed(seed, stream, 1, b, j)  # same item-seed rule as SeededSampler
    ```
  - `BatchStream.__init__(..., sampler_factory=None)`: when set, `iterate()` uses it instead of `SeededSampler`. `build_benchmark_data` (train.py l.325-476) builds the factory only when `data.rcs.enable`; flag off leaves the code path byte-identical.
  - At start, write `rcs_stats.json` to the run dir: P per class, list sizes, expected draw share of crack-free cells, inactive cells and each source, max per-cell multiplier; log one line `RCS: ...` for the queue's start check.
- **Unit tests (`tests/test_rcs.py`):** (1) flag off: 5-step CPU identity vs bench HEAD = IDENTICAL; (2) same seed gives the same index sequence; `start_batch=b` reproduces the tail from b (resume); (3) 100k draws: class frequencies within 1% absolute of P; every index drawn for class c is in lists[c]; (4) no held-out stem (root `splits/val.txt`) appears in any list; (5) toy masks with ignore 255: counts skip ignore.
- **CPU pre-check (done for P532, E):** `cards/T1_rcs_precheck.py` (md5 6b4c60d0). All 24 classes at T 0.01: inactive px share 0.81x, crack 0.82x, one cell drawn 34x (this is why the class list is R13). R13 at T 0.01, min 20 px: inactive 2.49x, splice 2.08x, crack 1.68x, edge_dark 1.59x, max cell multiplier 3.2, effective n 340, 2 cells never drawn, crack-free cells 0.49 of draws (uniform 0.56), SDLE 0.004 (uniform 0.032). **Engineer's re-run, per fold:** the same script on each `cv5v2` fold's train list with v1.1 masks. Pass rule: every fold has inactive px share >= 1.5x, max per-cell multiplier <= 5, no empty list. If a fold fails, use T = 0.1 for all folds (R13 at T 0.1: inactive 1.83x, max multiplier 2.3) and record it before any GPU run.
- **Screen:** 10 runs (11 GPU-h) + optional pre-screen (1.1).
- **Should move:** inactive IoU up, mIoU-R13 up (splice, edge_dark, material), inactive region recall up. Crack: recall and width up, precision down (crack px share 1.68x and fewer crack-free cells drawn: prior shift).
- **Side effects:** predicted / GT crack px expected up (S: by roughly 0.05 to 0.15); crack false alarms on crack-free cells up; inactive false alarms up; SDLE seen 8x less (17 SDLE cells in CV: per-source table only, not a drop criterion).
- **Drop rule:** drop if inactive IoU and mIoU-R13 both gain less than M at argmax, or if crack relF1@2 falls by more than M at the cross-fitted bias (argmax loss alone is an operating-point shift, reported), or if crack-free cell false alarms rise by more than 0.05 absolute.
- **Build:** 3 h. **Needs:** nothing new.
- **Risks / how it could mislead:** (a) an inactive gain that is really a larger inactive prior: check inactive precision and region precision, not IoU alone; (b) crack recall gains from prior shift: judge crack only at the matched bias; (c) class stats computed on the full pool would leak held-out masks: the tables are built from the root's train list only (test 4); (d) over-sampling 2 to 3x of a few inactive cells may overfit them: watch F51 inactive (unseen modules).

---

## Arm 2. `ema_wise_posthoc`: EMA weights and WiSE-style interpolation, read out from the same runs
- **Papers:** 030 (EMA), 077 (WiSE-FT). Priority 80. Route: training_recipe (small code) + inference-only readouts.
- **Hypothesis:** averaged weights (EMA) smooth the logits that 1 to 2 px label jitter makes noisy; interpolating the encoder back toward ImageNet trades a little in-distribution fit for unseen-module robustness. Both are read from runs that are bit-identical to PF in their raw weights, so the contrast is paired within run.
- **Change, part A (EMA, training-time, trajectory-neutral):** PF card plus `training.weight_avg=[{name: ema_999, mode: ema, decay: 0.999}, {name: ema_9998, mode: ema, decay: 0.9998}]`, `training.bn_recal=true`.
  - New file `src/trainers/weight_avg.py`:
    ```
    class WeightAverager:                     # holds a deep copy of model params AND float buffers, fp32, same device
        __init__(model, mode, decay=None, start=0, end=None)  # mode: 'ema' | 'uniform'
        update(model, step):                  # call after scheduler.step(), under no_grad, step = optimizer steps done
            if step < start or (end is not None and step > end): return
            if mode == 'ema': d = min(decay, (n + 1) / (n + 10)); avg = d * avg + (1 - d) * cur   # R: EMA paper warm-up
            else: avg += (cur - avg) / (n + 1)                                                  # running mean
            n += 1                            # integer buffers (num_batches_tracked) copied, not averaged
        state_dict() -> dict                   # model-shaped state dict, saved as checkpoint["models"][name]
    @torch.no_grad()
    def bn_recalibrate(model, loader, max_batches=None):
        reset running_mean / running_var / num_batches_tracked of every _BatchNorm; set momentum = None (cumulative)
        model.train(); for each batch (eval transforms, fixed order, all training cells once, batch 8): model(images)
        restore momenta; model.eval()
    ```
  - Trainer (`src/trainers/trainer.py`): build averagers after the optimizer when `training.weight_avg` is set; `update` after `self.scheduler.step()` (l.521); include averager states and `n` in `latest.pth` (resume); at the final step, for each averager and for the raw model, copy weights into a scratch model, run `bn_recalibrate` on the training fold (a new `BatchStream`-free DataLoader over `splits/train.txt` with the eval pipeline, `augmentations.py` l.62-74), save as `models[<name>_bn]` and `models["raw_bn"]`. The raw `models["model"]` is unchanged.
  - Cost: 2 extra fp32 copies of about 26M params (S, about 210 MB GPU); BN pass over 425 cells x 3 models (about 2 to 3 min, S).
- **Change, part B (WiSE readouts, inference-only):** `scripts/weight_interp.py --a CKPT_A --key-a K --b CKPT_B --key-b K --alpha a --scope encoder|all --bn-root ROOT --out CKPT` writes `theta = (1 - a) theta_A + a theta_B` for float params in scope (others from B), then `bn_recalibrate` on ROOT's train list. Readouts per fold x seed:
  - W1: A = ImageNet init (the build-time encoder, conv1 RGB-summed), B = PF final, scope encoder, a in {0.5, 0.75}; decoder from PF.
  - W2: A = house final, B = PF final (same fold, same seed), scope all, a = 0.5. Only if the identity check below passes.
  - Choice of a for the reported row: cross-fitted (fold k uses the a with the best mean relF1@2 over the other 4 folds); fixed-a rows also reported.
- **Unit tests (`tests/test_weight_avg.py`):** (1) `training.weight_avg` unset: 5-step CPU identity IDENTICAL; (2) set: raw param and buffer sha after 5 steps IDENTICAL to unset (the averager touches neither RNG nor model); (3) toy model: EMA after k steps equals the closed form with the warm-up decay; uniform average over [s, e] equals the mean of stored snapshots to 1e-6; (4) `bn_recalibrate` on a toy BN equals the exact population mean / var of its inputs to 1e-5; (5) resume at step k gives the same averager state as an uninterrupted run; (6) `weight_interp` with a = 0 and a = 1 returns A and B exactly (before BN recal).
- **CPU pre-checks (decide W2 and catch failures before any GPU):**
  - P1 (init identity): build house and PF configs on CPU with seed 5 and 6; decoder + head param sha at step 0 must be equal (PF only changes optimizer groups, S). If not equal, drop W2.
  - P2 (loss barrier), on existing B6 fold-0 checkpoints (house and PF, seed 5; open fold): CPU fp32 `bench_infer` of the house x PF midpoint and of W1 a = 0.5, BN recalibrated, held-out fold 0. Pass rule: midpoint crack relF1@2 not below min(endpoints) - 0.05 and inactive IoU not below min(endpoints) - 0.05. Fail = a loss barrier: drop that readout family. About 20 min CPU; prints pass / fail per readout only.
- **Screen:** if part A is in W1a's PF runs before launch (lead's call; test 2 makes it safe): 0 extra training GPU-h. Otherwise 10 PF runs with averaging on (11 GPU-h), whose `models["model"]` must equal W1a PF bit for bit on the same GPU type (a free determinism check). Readout dumps: about 10 runs x 6 keys x (107 held-out + 87 F51 / H36 cells), about 1 GPU-h (S).
- **Should move:** EMA: crack relP@2 up and crack-free false alarms down, relF1@2 up a little; inactive IoU flat or up. Expected small under cosine-to-0 (lr is under 7.4% of peak in the last 3,500 steps; R: EMA's benefit shrinks as lr decays). WiSE W1: F51 / H36 inactive and crack relF1@2 up, CV crack IoU flat or slightly down.
- **Side effects:** averaged and interpolated weights give smoother, slightly lower-confidence crack logits: predicted width may fall a little at argmax (S); faint-crack recall may drop. `raw_bn` isolates the effect of BN recalibration alone (batch-8 running stats vs population stats); every averaged readout is also compared with `raw_bn`, not only with raw.
- **Drop rule:** EMA: keep in the final recipe only if `ema_9998_bn` (pre-declared primary) beats raw by >= M on one headline metric with no headline loss > M (paired). Otherwise drop (it costs nothing to keep logging). WiSE: drop if no a (cross-fitted) beats PF raw by >= M on F51 / H36 crack relF1@2 or inactive IoU while CV headline metrics stay within M.
- **Build:** 4 h (averager 1.5, BN recal 1, trainer hooks + checkpoint keys 1, interp script 0.5). **Needs:** nothing new.
- **Risks:** (a) choosing a or the EMA decay on the scored fold: forbidden; primary decay pre-declared, a cross-fitted; (b) BN recal on held-out or F51 cells would be transductive leakage: training fold only; (c) a gain only from BN recal would be misattributed to averaging: `raw_bn` row; (d) six readouts per run are six contrasts: count them in the multiplicity ledger.

---

## Arm 3. `swad_const`: constant learning rate with dense uniform weight averaging
- **Papers:** 023 (SWAD), 030 (EMA under a constant tail). Priority 65. Route: training_recipe.
- **Hypothesis:** SWAD needs iterate diversity, which a cosine-to-0 schedule removes. With a constant lr after warmup and a dense average over the second half, the averaged model sits in a flatter region and transfers better to unseen modules.
- **Change:** PF card plus `training.lr_scheduler=constant` (keeps `warmup_steps=200`; PF freeze 1k / ramp 1k unchanged, `build_pf_lr_lambda` multiplies the constant base), `training.weight_avg=[{name: swad, mode: uniform, start: 10000, end: 20000}, {name: ema_9998, mode: ema, decay: 0.9998}]`, `training.bn_recal=true`. Card weights key for the arm: `swad_bn` (pre-declared primary). No new code beyond arm 2.
  - Window fixed in advance at steps 10,000 to 20,000, every step (10,001 iterates). The paper's validation-chosen window cannot be used: the held-out fold is the scored set. The paper's own ablation (R) puts a fixed window close to SWA (81.7 vs 83.0 for full SWAD), so a null here does not close the overfit-aware version.
- **Unit test:** a CPU run of 30 steps with `start=10, end=20` gives `n = 11` and the uniform mean of the stored iterates 10 to 20; constant schedule multiplier = 1 after warmup and the PF group still 0 for steps < freeze.
- **CPU pre-check:** none that decides anything. Fold-0 pre-screen (1.1 GPU-h) catches divergence at constant lr 1e-3: fail if the training loss over steps 15k to 20k is above PF's at 10k, or if `swad_bn` crack relF1@2 on fold 0 is below PF raw by more than 0.05.
- **Screen:** 10 runs (11 GPU-h) + dumps of `model`, `raw_bn`, `swad_bn`, `ema_9998_bn`.
- **Should move:** F51 / H36 crack relF1@2 and inactive IoU up (unseen-module proxy); CV crack relP@2 up. Comparison `swad_bn` vs PF raw, paired by fold x seed (same init, same batches).
- **Side effects:** the raw constant-lr final weights should be worse than PF (S); report but do not judge on them. Averaged logits near thin cracks are smoother: width may fall and faint-crack recall may drop (S).
- **Drop rule:** drop if `swad_bn` is not >= M better than PF raw on any headline metric (CV or F51 / H36), or if any CV headline metric is worse by more than M.
- **Build:** 1 h after arm 2. **Needs:** nothing new.
- **Risks:** (a) constant 1e-3 for the decoder may be too high to reach a good basin; the 10k-iterate mean can still be good (SWA practice) but if `swad_bn` loses, a constant-lr retry at 3e-4 is the one follow-up; (b) BN must be recalibrated (averaged running stats are not the stats of the averaged weights); the paper froze BN during training instead, which we do not; (c) do not compare `swad_bn` with PF's raw on a different machine.

---

## Arm 4. `encoder_spd`: selective projection decay replaces PF's uniform 0.1x encoder lr
- **Papers:** 009 (SPD), 032 (L2-SP, parked as the fallback). Priority 62. Route: new_loss (optimizer).
- **Hypothesis:** PF damps every encoder tensor by 0.1x. SPD lets tensors whose descent keeps pushing away from ImageNet move at the full lr (stem, layer1: EL contrast) and stops deviation growth where the loss no longer pushes outward. Expected: CV crack equal or better, unseen-module gains of PF kept or raised.
- **Change:** PF card with `training.encoder_pf.lr_mult=1.0` (freeze 1k, ramp 1k, wd 0 kept), plus `training.optimizer=adam_spd`, `training.spd.lambda=1.0`, `training.spd.groups=[encoder]`.
  - One mechanism swap (uniform damping to selective projection), so lr_mult and SPD change together. A PF + SPD at 0.1x variant would test "more preservation", a different question (PF already keeps layer3 / 4 at cosine 0.93 / 0.94 at 20k, E).
  - New file `src/optim/adam_spd.py` (written from the paper's Algorithm 2; the repository's licence is unverified, so no code copied):
    ```
    class AdamSPD(torch.optim.Adam):
        groups may carry 'spd_lambda' (float, default 0) and 'anchor' (list of tensors, same shapes, fp32, no grad)
        step():
            for groups with spd_lambda == 0: exactly torch Adam (coupled weight_decay as given)   # decoder: house Adam, wd 1e-4
            for groups with spd_lambda > 0 (weight_decay must be 0), per parameter tensor p with grad g, anchor a:
                prev = p.detach().clone()
                c = -(g * (prev - a)).sum()                        # scalar tensor, no .item()
                Adam update of p in place (bias-corrected; group lr from the PF lambda)  -> p = theta~
                gamma_new = (p - a).norm(); gamma_old = (prev - a).norm()
                r = clamp((gamma_new - gamma_old) / gamma_new.clamp_min(1e-12), 0, 1)
                p -= where(c < 0, spd_lambda * r, 0) * (p - a)   # Eq. 4, applied only when c < 0
    ```
    Anchor = copy of `encoder.*` params taken when the optimizer is built (after any `encoder_init`), so conv1's anchor is the RGB-summed 1-channel kernel the model was built with. Anchors are saved in `latest.pth` under `optimizers` state and their md5 is asserted equal to the build-time copy on resume. During the freeze (group lr 0) the Adam step is 0, so r = 0 and nothing moves.
  - `build_optimizer` (train.py l.108-131): new name `adam_spd`, requires `encoder_pf`; group 1 gets `spd_lambda` and anchors, `weight_decay` 0.
  - Log per-stage cosine to init and norm ratio (conv1, layer1 to layer4) every 2k steps (`reports/enc_cosine` logic).
- **Unit tests (`tests/test_adam_spd.py`):** (1) `spd_lambda=0` on all groups: 10 CPU steps bit-identical to `torch.optim.Adam`; (2) gradient with c >= 0: step identical to Adam; (3) c < 0 and lambda 1: `||p - a||` after the step <= before + 1e-6; (4) lambda 2.2 vs 1: deviation smaller or equal; (5) state_dict round trip (resume) gives identical next steps; (6) flag off: 5-step CPU identity of the PF card IDENTICAL.
- **Pre-check:** CPU unit tests above. Mechanism gate on the fold-0 seed-5 pre-screen (1.1 GPU-h): layer3 / layer4 cosine to init >= 0.8 at 20k (the G5 threshold used for PF), and conv1 / layer1 deviation larger than PF's at 20k (otherwise SPD is just PF). If layer3 / 4 < 0.8: one re-run with lambda 2.2 (the paper's segmentation value); if that also fails, drop SPD and record "SPD does not preserve at lr 1e-3"; L2-SP (alpha 0.01) then becomes the fallback arm.
- **Screen:** 10 runs (11 GPU-h), compared with W1a PF and W1a house, both paired by fold x seed (same init, same batches).
- **Should move:** F51 / H36 inactive IoU and crack relF1@2 up vs PF; CV crack IoU / relF1@2 equal or up vs PF; vs house: everything at least PF-like.
- **Side effects:** with a freer stem, crack width could rise toward the house's (S); watch predicted / GT px and the crack-free false-alarm rate.
- **Drop rule:** drop if no headline metric (CV or F51 / H36) beats PF by >= M, or if CV crack relF1@2 or inactive IoU falls below PF by more than M.
- **Build:** 3 h. **Needs:** nothing new.
- **Risks:** (a) per-tensor branching with `.item()` would add about 110 GPU syncs per step; the vectorised `where` form avoids it; (b) bf16 autocast: params and anchors stay fp32; GradScaler is disabled for bf16 (E, trainer l.235), so no unscale issue; (c) grad clip at 1.0 runs before the step as now; (d) a gain on F51 only could be noise from 51 cells: report the paired per-model distribution.

---

## Arm 5. `modern_recipe`: AdamW (decoupled wd 0.01) + 1.5k warmup, the DAFormer recipe on PF (stacked)
- **Papers:** 043 (DAFormer recipe and warmup ablation), 030 (EMA readout). Priority 55. Route: config_only (EMA readout uses arm 2 code if ready).
- **Why stacked:** both changes are from one paper's recipe, both act mainly on the decoder (the encoder is already frozen 1k, ramped 1k, wd 0 under PF), and each alone is expected to be under the noise. If the stack passes, one drop-one run (warmup back to 200) tells which part carries it.
- **Hypothesis:** the decoder trains under Adam with coupled L2 1e-4. With BN-followed (scale-invariant) convs, coupled L2 inside Adam shrinks norms and raises the effective step, the mechanism that erased the encoder in the house recipe (E, handbook 11 row 23; decoder norms never measured). Decoupled wd removes that coupling; DAFormer's longer warmup protects early training (R, Table 4: DeepLabV2 oracle 67.4 to 72.1 with warmup; ours already has 200 steps).
- **Change:** PF card plus `training.optimizer=adamw`, `training.weight_decay=0.01`, `training.warmup_steps=1500`; `training.encoder_pf.wd=0` stays. If arm 2's code is in: `training.weight_avg=[{name: ema_9998, mode: ema, decay: 0.9998}]`, `training.bn_recal=true` (readout only; primary key stays `model`). Existing keys only (`build_optimizer` already supports adamw with PF groups, E l.113-125).
  - Note (S): torch AdamW applies p *= (1 - lr x wd) per step; at lr 1e-3 and wd 0.01 that is about a 10% total shrink over the cosine run, small next to the coupled pathway.
- **CPU pre-check (informative, not a kill):** on B6 fold-0 house and PF checkpoints (seed 5), the ratio of final to init weight norm for every BN-followed decoder conv (init from a CPU build with the same seed). If the median ratio < 0.3, coupled wd is collapsing the decoder too and the arm's prior rises; if it is about 1, expect n.d. and run it last.
- **Screen:** 10 runs (11 GPU-h). Drop-one follow-up (only if it passes): 10 runs.
- **Should move:** crack IoU and relF1@2 (decoder quality), mIoU-R13; inactive flat.
- **Side effects:** none expected on width beyond noise (S); report anyway.
- **Drop rule:** drop if no headline metric beats PF by >= M or any falls by more than M.
- **Build:** 0.5 h (card only). **Needs:** nothing.
- **Risks:** stacked, so a pass does not say which part helped until the drop-one run; a fail could hide opposite effects (accepted: each part's prior is low).

---

## Arm 6. `sam`: sharpness-aware minimisation on top of PF
- **Papers:** 086. Priority 40. Route: training_recipe.
- **Hypothesis:** crack label jitter acts as label noise; SAM's worst-case step resists fitting it and finds flatter minima. Weak prior: SWAD's PACS table (R) shows SAM 85.5 vs ERM 85.3 OOD (not significant).
- **Change:** PF card plus `training.sam.rho=0.05`, `training.sam.adaptive=false`. In `_train_step` (trainer l.450-530), supervised branch only:
    ```
    loss1 = sup(model(x), y); loss1.backward()                 # pass 1: BN running stats update normally
    with no_grad: gn = global grad norm over params with grad; for p: e = rho * p.grad / (gn + 1e-12); p += e; store e
    zero_grad; with frozen_bn_stats(model): loss2 = sup(model(x), y); loss2.backward()   # pass 2, BN stats untouched
    with no_grad: for p: p -= e                                 # restore
    clip_grad_norm_(1.0) on pass-2 grads; optimizer.step(); scheduler.step()
    ```
    Uses the existing `frozen_bn_stats` (`ssl_ops.py` l.46). Refuse to start if the GradScaler is enabled (fp16). Perturb all params (encoder grads exist during the freeze; its lr is 0, so it does not move). Log loss1 and loss2.
- **Unit tests:** (1) `training.sam` unset: CPU identity IDENTICAL; (2) rho 0: one step equals the plain step except for BN buffers, which must equal the plain step's (pass 2 restores them); (3) after the step, params equal Adam applied to the pass-2 gradient at the unperturbed point (toy linear model, closed form).
- **Pre-check:** none on CPU. Fold-0 pre-screen (2.2 GPU-h): fail if loss diverges or crack relF1@2 on fold 0 is below PF by more than 0.05.
- **Screen:** 10 runs at about 2x cost (22 GPU-h).
- **Should move:** CV crack relP@2 and component precision up, crack-free false alarms down; F51 / H36 crack relF1@2 up.
- **Side effects:** may narrow predictions (less fitting of jittered edge px): width down, relR@2 down a little (S).
- **Drop rule:** drop if no headline metric beats PF by >= M or any falls by more than M. If engineering time is short, this arm moves to PARKED first.
- **Build:** 3 h. **Needs:** nothing.
- **Risks:** batch 8 BN: the perturbed pass must not update running stats (handled); doubled step time changes wall-clock but not the sample budget (still 20k x 8).

---

## Summary table
| # | Arm | Papers | Route | Build h | Screen GPU-h | Priority | Status |
|---|---|---|---|---|---|---|---|
| 1 | rcs | 021, 043, 033 | data_pipeline | 3 | 11 (+1.1 pre) | 85 | RUN_NOW |
| 2 | ema_wise_posthoc | 030, 077 | training_recipe | 4 | 0 to 11 + 1 dumps | 80 | EMA RUN_NOW; WiSE after W1a + P1 / P2 |
| 3 | swad_const | 023, 030 | training_recipe | 1 | 11 (+1.1) | 65 | RUN_NOW |
| 4 | encoder_spd | 009, 032 | new optimizer | 3 | 11 (+1.1, +1.1 if lambda 2.2) | 62 | RUN_NOW |
| 5 | modern_recipe | 043, 030 | config_only | 0.5 | 11 (+11 drop-one) | 55 | RUN_NOW |
| 6 | sam | 086 | training_recipe | 3 | 22 (+2.2) | 40 | RUN_NOW, lowest |

Total screen about 78 to 89 GPU-h (S): under half a day on 8 A6000. Build about 14.5 h, shared code first (weight_avg, then rcs, adam_spd, sam).
Parked: L2-SP (fallback inside arm 4), ImageNet feature distance (043 / 033, about 13 GPU-h when opened), schedule length (PF at 30k, 5 folds x 1 seed, about 8 GPU-h, after the stack).
Final-model stack (lead's call after the screens): PF base + every arm that passed alone, EMA or SWAD readout as the deliverable weights if they passed.
