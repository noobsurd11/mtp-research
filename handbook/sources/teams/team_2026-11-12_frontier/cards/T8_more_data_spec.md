# T8 More supervision: experiment specifications (13 Nov 2026)

Analyst T8. Tags: R = paper or dataset page, E = our files (path given), S = my judgement. Paper cards and dataset census: `T8_more_data_family.md`. Ledger: `ledger/T8.tsv`. Pre-checks already run: `cards/T8_precheck/*.out`.

Four arms, in priority order. Arm 1 is the first build. Arms 2 to 4 are gated.

| # | Arm | Problem | Primary | Build h | GPU-h (screen) | Status |
|---|---|---|---|---|---|---|
| 1 | `ucf_partial_joint` | inactive (2), unseen modules (3) | inactive IoU, OP-A, CV | 10 | 16 | RUN_NOW |
| 2 | `inactive_grid_paste` | inactive (2) | inactive IoU, OP-A, CV | 6 | 12 | after C-REAL |
| 3 | `elpv_bmrk_negatives` | weak source BMRK (2) | BMRK crack relF1@2, OP-W | 2.5 (on arm 1 code) | 14 | after C-BMRK + arm 1 code |
| 4 | `pvddpm_fold_synth` | inactive (2) | inactive IoU, OP-A, CV | 12 | about 70 (generators included, S) | after G4 |

## 0. Common frame
- **Comparator:** card `house_r34_unetpp_pf_v11` (PF, v1.1 labels, 20k steps, batch 8, 512 px, final weights, argmax). Same machine type and commit as the W1 PF runs it is compared with (one comparison, one machine). Per LEAD_INSTRUCTIONS 13 Nov: pathfinders on gaint, screens on cv02 against W1-C1 seeds 5, 6 (seeds 7, 8 give the A/A null). Canonical fp32 dumps.
- **Screen:** `cv5v2` 5 folds x seeds 5, 6, out-of-fold pooled, two-stage bootstrap (330 groups, then seeds). Pass = delta >= M and interval above 0, with M = max(0.01, 2 x SE of the A/A split); a pass promotes to the 5-seed confirmation only. Fold-0 seed-5 pathfinder first (failure, step time, peak memory; never ranks).
- **Guards (WAVE2_REVIEW 5, all of them):** OP-A / OP-F / OP-W from `crossfit_op`; crack width ratio pooled and per source (pass band 0.85 to 1.15 x PF); relP@2 beside relR@2, relF1@1 and strict IoU beside relF1@2; false alarms on the 303 crack-free cells; component precision beside recall; inactive precision, recall, region precision; per-source table; A/A contrast beside the arm contrast; step time and peak memory; flag-off identity; leak asserts; ledger line. A crack gain counts only at OP-A and OP-W.
- **F51 reads** (unseen-module development): paired over the 10 fold x seed models, logged in the read ledger, promotion only. H36 crack in no rule. Legacy test and E1 sealed.
- **Power warning (E, PROTOCOL 3.2):** an inactive IoU contrast on CV5-G at 2 seeds has SE 0.038 to 0.039, so M for inactive is about 0.08, and 80% power needs a true effect of about 0.11 (PROTOCOL 5.4 table). Arms 1, 2 and 4 must move inactive IoU by about 0.08 to pass the screen; a 2-seed null on inactive closes nothing below about 0.11. Each arm therefore also pre-declares region recall and inactive precision as the readouts that explain a pass or a null; neither can promote on its own.
- **Why no 5% screens:** memory rule "use full labels": all arms add data on top of 100% labels.

## 0.1 Harness support used
- Trainer, PF card, v1.1 masks with ignore 255 in train masks (LABELS_V11 4, DESIGN 1.6): used unchanged.
- `BatchStream` (seed, stream id, index) determinism (DESIGN 1.6): the external stream is a second `BatchStream` with its own stream id, so the BenchmarkEL batches of an arm are identical to PF's (paired contrast kept, unlike rcs).
- `sup_criterion(logits, masks)` call site (DESIGN 1.4, trainer l.466-473): one split at that site.
- Isolated venv pattern (`venv_sam2`, DESIGN 6) for arm 4 only.
- Not needed: new model code, new heads, new decision rule. Dumps and scorer unchanged (the model is the house model).

---

## Arm 1. `ucf_partial_joint`: joint training with UCF-EL under partial labels (RUN_NOW)

- **Papers:** P037 (marginal loss), P077 (NLL+), P011 (per-dataset loss terms, Dice only on the labelling dataset, summed losses), P223 (other-class positives as negatives). Route: data_pipeline + new_loss.
- **Problems:** 2 (inactive, 42 train cells) and 3 (unseen modules: 358 more modules from another lab).
- **Primary:** inactive IoU at OP-A on CV (pooled OOF). Readouts that explain it: inactive region recall (>= 100 px, >= 50% covered), inactive precision. Guards as section 0; crack relF1@2 and strict IoU must not drop by more than M at OP-A and OP-W; mIoU-R13 not down by more than M. F51 inactive and crack relF1@2 paired over 10 models (secondary, promotion only).
- **Differs from what was run (BRIEF 5):** the UCF-EL run was sequential encoder pretraining with the 4 released classes, then the house fine-tune that erased the encoder. Here UCF is in every batch for all 20k steps, under PF, with subtype-resolved labels mapped into our 24-class head, so the external data supervises the inactive logit directly. Differs from `rcs` (T1): rcs re-weights the same 42 inactive cells; this adds about 1,000 new inactive regions.

### Label mapping (E-based; codes in an 8-bit external mask)
Codes: 0..23 = hard class; 254 = NEG (any of the 22 classes except crack 14 and inactive 11); 255 = ignore.
Rasterise from `AnnotationsCombined.csv` (subtypes are lost in the released masks), at native UCF size, in this order (later overrides earlier):
1. Whole UCF image (cell area) -> 254 NEG. Contact (FrontGridInterruption, NearSolderPad), Interconnect_HighlyResistive, Contact_Corrosion rectangles / polygons -> 254 (P223: other-class positives are negatives for crack and inactive; they may still be gridline 15, corrosion 18, which NEG allows).
2. `Crack_Resistive` polygons -> 255 (E2: median darkness 0.90, not inactive in our convention; not safe as background either).
3. `Crack_Isolated` polygons: per region darkness ratio r = median(I in polygon eroded 2 px) / median(I in UCF background, released mask value 0). If r <= 0.60 (our inactive 90th percentile, E2): polygon eroded by 2 px -> 11; the 2 px inner ring and a 2 px outer ring -> 255. If r > 0.60: whole polygon dilated 2 px -> 255.
4. `Crack_Closed` polygons (if `ext.ucf.crack_positive=true`): polygon dilated 2 px -> 255; then its 1 px skeleton (skimage `skeletonize` on the filled polygon) -> 14. Our crack label is 1.75 px median, the polygon centre sits within 1 px of the dark ridge as often as our labels (51% against 48%, E `ucf_el_report.md` 4.1), so the skeleton is the closest match to our convention; the ignore band stops the polygon width from teaching width.
5. Ignore classes of UCF (Interconnect_Disconnected, Interconnect_BrightSpot, Unknown, Contact_BeltMarks; released value 128) -> 255.
6. Images excluded: the 247 `M9000` png cells (other technology, mostly ignore, E report 1); any image with Interconnect_Disconnected; any image with ignore share > 20%; any image hit by the duplicate search C0.
Geometry: resize image (bilinear) and code mask (nearest) by s = 0.85 x U(0.9, 1.1) (E1: our cell 250 px, UCF 295 px; FWHM then 4.25 px against our about 4 px); place on a 512 x 512 zero canvas with the cell centre at canvas centre + U(-60, 60) px in x and y; canvas pixels outside the cell -> hard 7 (padding), as in BMRK cells. Then the house label-safe augmentation (flips, rot90, brightness / contrast), normalise mean 0.5 std 0.25.
Pool: UCF train + test release (we never score UCF), minus exclusions. Expected about 11,300 images, about 1,000 with a kept inactive region (E3 x 57%).

### Exact change
- New script `scripts/ext/build_ucf_targets.py` (CPU, once; reuses the rasteriser of `data_analysis/scripts/ucf_provenance.py`, which rebuilds the release at 99.6% pixel agreement, E report 1): writes `<EXT>/ucf_v1/{images,codes}/<stem>.png` at native size, `index.tsv` (stem, has_inactive_kept, n_iso_kept, n_iso_dropped, has_closed, ignore_share), `MANIFEST.md5`. Unit tests: (a) code values in {0..23, 254, 255} only; (b) on 20 images, released-mask crack (value 1) px are a subset of {11, 14, 255} codes; (c) no 11 where r > 0.60; (d) rebuild is deterministic (md5 equal on two runs).
- New file `src/data/ext_mix.py`:
  ```
  class ExtCodesDataset(Dataset):          # returns image (1,512,512) f32, codes (512,512) int64, stem, is_ext=1
      __init__(root, index_tsv, scale=0.85, jitter=(0.9,1.1), shift=60, aug=house_label_safe)
      __getitem__(i, item_seed): rng from item_seed; resize img bilinear, codes nearest; paste on canvas
                                 (canvas codes = 7); aug applied to (img, codes) jointly; normalise
  class ExtSampler:                        # p_inactive share of draws from has_inactive_kept rows
      draw(seed, stream=7, batch_idx, j) -> index   (same mix_seed rule as SeededSampler)
  ```
  Collate: the trainer receives `batch` (8 BenchmarkEL samples, unchanged stream) and `ext_batch` (2 samples, stream id 7). Both on GPU; forward once on `cat([x, x_ext])` (B = 10); BN sees both (S: matches MultiTalent's joint batches).
- New file `src/losses/partial_ce.py`:
  ```
  def partial_ce(logits, codes, excl=(11, 14), NEG=254, IGN=255):   # logits (B,24,H,W) f32, codes (B,H,W) int64
      lse = torch.logsumexp(logits, 1)                                 # (B,H,W)
      hard = codes < 24
      l_hard = lse - logits.gather(1, codes.clamp(max=23).unsqueeze(1)).squeeze(1)
      keep = torch.ones(24, dtype=torch.bool, device=logits.device); keep[list(excl)] = False
      l_neg = lse - torch.logsumexp(logits[:, keep], 1)               # = -log(1 - p11 - p14)
      loss = torch.where(hard, l_hard, torch.where(codes == NEG, l_neg, torch.zeros_like(lse)))
      n = (hard | (codes == NEG)).sum().clamp(min=1)
      return loss.sum() / n
  ```
  Computed in fp32 (outside autocast). Unit tests: (1) codes all hard -> equals `F.cross_entropy(ignore_index=255)` to 1e-6; (2) a NEG pixel with p11 = p14 = 0.25 -> loss log 2; (3) all-255 -> 0 and no NaN; (4) gradient at a NEG pixel is zero for the 22 allowed logits when p11 = p14 = 0.
- Trainer hook (at the `sup_criterion` call, trainer l.466-473):
  ```
  if cfg.ext.enable:
      logits_all = model(cat([images, ext_images]))
      logits, logits_ext = logits_all[:B], logits_all[B:]
      loss = sup_criterion(logits, masks) + cfg.ext.weight * partial_ce(logits_ext.float(), ext_codes)
  else: unchanged
  ```
  House Dice on crack / inactive stays on BenchmarkEL samples only (P011: Dice only on the dataset that labels the class; UCF inactive regions are 10x larger and would dominate a batch Dice).
- Config keys (new, opt-in; card `t8_ucf_partial_joint` = PF v1.1 card plus):
  `ext.enable=true`, `ext.name=ucf_v1`, `ext.root=<EXT>/ucf_v1`, `ext.manifest_md5=<md5>`, `ext.per_batch=2`, `ext.weight=0.25` (per-pixel parity with 8 in-domain images, S), `ext.p_inactive=0.5`, `ext.scale=0.85`, `ext.scale_jitter=[0.9,1.1]`, `ext.shift=60`, `ext.ucf.crack_positive=true`, `ext.ucf.iso_ratio_max=0.60`, `ext.stream_id=7`.
- Flag off: 5-step CPU identity IDENTICAL for the house and PF cards. Flag on: the BenchmarkEL batch sequence must equal PF's (assert stems of the first 50 batches against a PF dry run).

### CPU pre-checks
- **C1 scale (done, E1):** our cell 250 px, UCF 295 px -> s = 0.85. Pass.
- **C2 convention (done, E2, E3):** isolated regions at r <= 0.60 are 57% of sampled isolated regions; about 1,000 images. Pass rule was >= 300 images with a kept inactive region. Pass.
- **C0 duplicate and provenance search (to run, 2 h build, CPU):** structure-cancelling descriptor of `ucf_twins.py` (128 px, DoG band-pass, row / column means removed) on all UCF images and on all 816 BenchmarkEL stems, the 106 E1 cells and the 117 `_rf` cells, at matched cell scale; plus md5. Pass: no pair with NCC >= 0.8 and no md5 match. Any hit: visual check, UCF image excluded, logged. Expected 0 (different labs, S).
- **C3 descriptive, on tonight's PF OOF dumps (0.5 h):** split PF's inactive errors into (a) regions >= 100 px missed (< 50% covered), (b) found regions with boundary error, (c) false regions. Pre-declared reading: new examples act on (a) and (c); if (b) holds > 70% of inactive FN + FP px, expect a null and say so before the screen.

### Pathfinder and screen
- Pathfinder: fold 0, seed 5, 20k steps, gaint (about 1.6 GPU-h at B = 10). Reads: step time, peak memory (S: about 8.5 GB against 6.8), loss curves of both terms, crack width ratio on fold 0 against PF fold 0 seed 5. Width rule (reads width only, never a score): ratio > 1.25 -> set `ext.ucf.crack_positive=false` for the screen (one retry).
- Screen: 10 runs (5 folds x seeds 5, 6), about 14 GPU-h at 1.3x the house step cost.

### Expected effect and drop rule
- R: marginal loss + pooling +4.7 Dice points on average, but only +0.5 points on the fully labelled set's own organs for two of four (P037); NLL+ +0.3 to +1.3 within domain, up to +2.4 cross-domain (P077); MultiTalent +1.26 Dice, larger on difficult classes (P011).
- S: inactive IoU +0.02 to +0.08 on CV; the larger end only if C3 shows missed regions dominate. F51 inactive and crack relF1@2: the direction should be positive if the external modules help transfer.
- Drop: screen delta below M or interval including 0 -> not promoted; if inactive precision falls by more than 0.05 while recall rises, record "prior shift", not a gain. If the A/A-calibrated CI excludes a gain of 0.04, close this mapping (not the route: variant 1b below stays open).
- **Variant 1b (fallback, not queued):** MultiTalent heads. Two extra sigmoid channels on the last decoder feature (`ucf_crack_region`, `ucf_isolated`), BCE + batch Dice on UCF samples only; main 24-class head trained on BenchmarkEL only; decision rule unchanged (argmax of the main head). Opens only if arm 1's pathfinder shows the main head's inactive precision on fold 0 dropping by > 0.10 (convention clash), since then the conventions must be kept apart rather than mapped.

### Cost
- Build: converter 2.5 h, ext dataset + sampler 3 h, loss + tests 1.5 h, trainer hook + card + identity 1.5 h, C0 2 h = about 10 h.
- GPU: 1.6 (pathfinder) + 14 (screen) = about 16 GPU-h.
- Needs: no install (skimage for skeletons exists in the laptop venv; on gaint the converter runs on the laptop or uses scipy-only thinning; masks are built once, offline). No weights. UCF copy exists on gaint (`data_analysis` copied it from gaint, E report header).

### Risks and how this could mislead
- **Prior shift:** UCF raises the share of inactive px seen in training. Inactive IoU can rise by over-predicting. Guard: inactive precision and region precision; crack-free cells' inactive false-alarm px.
- **Width:** crack skeleton positives with an ignore band leave width unconstrained near UCF cracks. Guard: width ratio per source, OP-W.
- **Convention leak:** UCF annotators include busbars in crack regions ("When labeling cracks, include busbars", E report 1); the 2 px rings and the r <= 0.60 rule limit this; the busbar overlap is ignored, not forced.
- **Missed UCF labels:** faint cracks without polygons become NEG and push crack recall down. Guard: relR@2 per source at OP-W.
- **Leakage:** none expected (different lab); C0 checks it. UCF's own train / test twins do not matter (we never score UCF).
- **Instrument:** a CV gain says nothing about half-cut cells (UCF has none known, S). E1 stays sealed; F51 is the unseen-module read.
- **Licence:** UCF has no licence file. Training use for a thesis is common practice but the benchmark must state it and must not redistribute UCF data.

---

## Arm 2. `inactive_grid_paste`: paste real inactive regions with their crack onto other labelled train cells (RUN_AFTER_GATE C-REAL)

- **Papers:** P233 (grid-aware paste on labelled cells), P199 (why inactive sits where a crack cuts a region off; used for placement only). Route: data_pipeline.
- **Problem:** 2. **Primary:** inactive IoU at OP-A on CV. Readouts: region recall, inactive precision.
- **Differs from what was run (BRIEF 5):** CP100 pasted crack px onto unlabelled pool cells and created decoys. Here inactive regions with their bounding crack are pasted onto labelled train cells of the same source and cell type, at the same relative cell position, with source-matched darkening. E4 showed a rule-based renderer has too few donor cells (18 of 180), so real shapes are used instead.
- **Change:** new transform `src/data/inactive_paste.py`, applied in `BenchmarkELDataset.__getitem__` before the label-safe augmentation, with probability `aug.inactive_paste.p=0.3`, seeded by the item seed:
  ```
  donors (built per root from splits/train.txt only; assert no held-out stem):
      for each train cell with inactive: components of (mask == 11) >= 100 px;
      unit = component U crack px (mask == 14) within 3 px of it; store patch of image, unit masks,
      position normalised to the cell bbox (largest cell-area component, as c_scale.py),
      source (ARTS/CFVS/CSIR/BMRK), cell type (sp mono 2 / sp multi 1 / none), r_donor = median(I in 11) / median(I in 0)
  paste(target img, target mask, rng):
      donor = rng.choice(donors with same source and cell type; else same source)
      optional mirror (h, v) consistent with the cell symmetry; place at the same normalised position in the target cell bbox
      reject if the unit overlaps target classes {11, 14, 4, 9, 7, 5, 21} on > 5% of its px, or leaves the cell bbox (retry 5x, else no paste)
      region R = donor inactive unit; Rc = donor crack px
      target_img[R] = target_img[R] * r_donor * (median(I_target[0]) / median(I_target[0]))   # multiplicative: target texture kept
      target_img[Rc] = target_img[Rc] * (I_donor[Rc] / local_bg_donor[Rc])                  # donor crack contrast profile
      feather: blend the edge of R over 1 px (Gaussian sigma 0.7)
      target_mask[R] = 11; target_mask[Rc] = 14
  ```
  Keys: `aug.inactive_paste.enable=true`, `p=0.3`, `same_type=true`, `max_overlap=0.05`. Flag off: identity IDENTICAL; the batch sequence of stems is unchanged (only the content of 30% of samples changes).
  Unit tests: pasted labels lie on darkened px only; no held-out stem among donors; r applied once; output dtype and range unchanged; determinism under the item seed.
- **CPU pre-check C-REAL (gate, 1.5 h build, CPU inference):** for each fold k, build 20 pasted cells with donors and targets both from held-out fold k, then run the W1 PF checkpoint of fold k seed 5 (it saw neither) on CPU in fp32. Compare its inactive region recall and pixel IoU on the pasted regions with the same on the real held-out inactive regions of fold k. Pass: pasted region recall within real +- 0.15, and predicted crack px along the feathered edge < 20% of edge px. Pasted recall far above real means an artefact the model can learn as a shortcut; far below means the paste is unrealistic. Fail: park the arm (record the numbers).
- **Pathfinder / screen:** fold 0 seed 5 (1.1 GPU-h), then 10 runs (11 GPU-h).
- **Expected:** R: grid-aware paste doubled the tail-class AP of one rare class (0.145 to 0.288, P233, detection). S: inactive IoU +0.01 to +0.05; mostly region recall. Drop: as arm 1. If arm 2 and `rcs` both pass, the stack is a later arm.
- **Cost:** build 6 h (transform 4, C-REAL 1.5, card 0.5); GPU 12.1 h. Needs: nothing new.
- **Risks:** the same 42 shapes are reused, so the model can memorise shapes (guard: region precision on crack-free cells); pasted crack px raise the crack prior (guard: width, crack-free false alarms); inactive is under-powered on CV (section 0).

---

## Arm 3. `elpv_bmrk_negatives`: ELPV defect-free cells as full negatives in exact BMRK geometry (RUN_AFTER_GATE C-BMRK and arm 1 code)

- **Papers:** P079 (negatives are fully labelled samples), P312 (ELPV image labels for cracks; positives are variant 3b, not queued). Route: data_pipeline (reuses arm 1's `ext_mix.py` and `partial_ce`).
- **Problem:** 2 (BMRK is the weak source: crack 0.379, inactive 0.324 on test, BRIEF 3). **Primary:** crack relF1@2 on the BMRK rows (50 P532 cells) at OP-W, with its own A/A null on the same rows. Guards as section 0 plus BMRK inactive precision and recall.
- **Data (E, page):** ELPV GitHub `zae-bayern/elpv-dataset`, CC BY-NC-SA 4.0, 2,624 cells 300 x 300, defect probability in {0, 1/3, 2/3, 1}, mono / poly. Not downloaded yet.
- **Change:** converter `scripts/ext/build_elpv_targets.py`: rotate and resize each ELPV cell exactly as BMRK cells were made (rotation direction and resampling chosen by NCC against the 65 BMRK corpus cells, must reach >= 0.99 on all 65), pad into 512 with the BMRK padding value and position; codes: padding px -> 7, cell px -> 254 NEG if probability == 0; cells with probability > 0 are not used. Exclusion: every ELPV cell that matches any of the 65 BMRK corpus cells (name `cellNNNN` and NCC >= 0.99) is dropped. Card: arm 1 keys with `ext.name=elpv_neg_v1`, `ext.per_batch=2`, `ext.weight=0.25`, `ext.p_inactive=0`, no scale jitter (geometry is exact).
- **CPU pre-check C-BMRK (gate, on tonight's PF OOF dumps, 1 h):** on the 50 BMRK P532 cells: share of crack-free BMRK cells with >= 50 predicted crack px; BMRK inactive FP px against FN px; BMRK crack relP@2 against the other sources. Pass (run the arm) if crack-free BMRK false alarms >= 20% of those cells, or BMRK inactive FP px > FN px with precision < 0.5, or BMRK relP@2 is the lowest source by >= 0.05. Otherwise park: negatives cannot fix misses.
- **Screen:** fold 0 pathfinder (1.4 GPU-h), then 10 runs (about 13 GPU-h).
- **Expected:** R: P079 shows negatives train the segmenter fully; no EL number. S: BMRK relP@2 up, relR@2 flat; relF1@2 +0.01 to +0.03 on BMRK rows; small elsewhere.
- **Cost:** build 2.5 h after arm 1; GPU about 14 h. Needs: ELPV download (public, no gate).
- **Risks:** **module-level leakage cannot be checked** (ELPV gives no module ids): siblings of the 10 BMRK legacy test cells and the 5 BMRK E1 cells may enter training as negatives. They carry no defect label, so the leak is appearance only; still, the benchmark row must be flagged and BMRK test / E1 rows reported separately. Probability-0 cells may contain faint unlabelled cracks (NEG then suppresses recall: guard relR@2 on BMRK). BMRK has only 50 CV cells: the per-source primary is noisy; the A/A null on the same rows sets M.
- **Variant 3b (not queued):** probability-1 cells as MIL positives: top-k mean of (p11 + p14) over the cell >= target via BCE (k = 0.5% of cell px). Opens only if arm 3 passes and C-BMRK shows FN-dominated errors.

---

## Arm 4. `pvddpm_fold_synth`: PV-DDPM retrained per fold, synthetic inactive cells filtered FreeMask-style (RUN_AFTER_GATE G4)

- **Papers:** P042 (PV-DDPM), P095 (FreeMask filtering and hardness-aware generation). Route: external_codebase (generator) + data_pipeline.
- **Problem:** 2. **Primary:** inactive IoU at OP-A on CV.
- **Why fold-wise:** the released PV-DDPM weights were trained on the complete SCDD set (R, P042 IV.A.3) which contains our legacy test and E1 cells, and the 93 synthetic E-SCDD cells derive from a test cell and F51 cells (E5). A generator for screen fold k may see only fold k's 425 training cells.
- **Change:**
  1. Isolated venv (pattern `venv_sam2`) from `sntubix/pv-ddpm` `environment.yml`, sharing torch; framework, resolution and licence of the repo unverified (no licence shown, E page).
  2. For each fold k: train PV-DDPM on fold-k train images with their v1.1 masks converted to the repo's binary conditioning masks (background mask; feature-defect masks for inactive and crack), no released weights.
  3. Generate 300 cells per fold conditioned on edited masks: train-fold masks of crack-only cells with an inactive unit added by arm 2's placement rule (real shapes), plus the train-fold inactive masks themselves.
  4. Filter (P095): drop synthetic px whose per-class CE under PF fold-k seed 5 (trained on the same fold-k train cells) exceeds that class's 90th-percentile CE on real fold-k train px; for crack, CE taken as the minimum within 2 px (label jitter); drop a cell if > 30% of its inactive px are dropped.
  5. Training: arm 1's ext path with `ext.name=pvddpm_f{k}`, `ext.per_batch=2`, `ext.weight=0.25`, codes = filtered labels (dropped px 255).
- **Gate G4 (all three):** (a) generator pathfinder on fold 0 measures GPU-h per generator; park if > 15 GPU-h per fold; (b) C-VIS on 100 fold-0 generated cells: inactive darkness ratio inside our IQR 0.22 to 0.46 for >= 70% of regions, and crack dip depth along the conditioning skeleton >= 0.5 x the real train median; (c) arm 1 or arm 2 has been read (if arm 2 passes, arm 4 asks whether a learned renderer adds to the paste; if both are null, arm 4 is the last inactive data route and runs only on the lead's call).
- **Expected:** R: no segmentation evidence for PV-DDPM; FreeMask +3.3 mIoU on ADE20K (scout summary, not re-read). S: at most the paste effect plus realism; +0 to +0.04 inactive IoU.
- **Cost:** build 12 h (venv and repo adaptation 4, mask conversion 2, generation + filter 4, C-VIS 2); GPU: 5 generators x 8 to 15 h (S, unmeasured) + 11 screen = about 50 to 90; noted as 70.
- **Risks:** generator memorises the 425 cells (synthetic near-copies add nothing; check nearest-neighbour NCC to train cells < 0.9); 1 to 2 px cracks not rendered (C-VIS b); every generator must be fold-pure (assert stems).

---

## 5. Data routes ranked (expected gain per build hour, S)

| Route | Inactive | Unseen modules | Build h | Verdict |
|---|---|---|---|---|
| UCF-EL joint, partial labels (arm 1) | about 1,000 new inactive regions, convention aligned by E2 | 358 new modules, another lab and camera | 10 | first |
| Inactive paste on labelled cells (arm 2) | new contexts for the 42 shapes | none | 6 | second, gated by realism |
| ELPV negatives (arm 3) | BMRK precision only | none | 2.5 on top of arm 1 | third, gated by failure mode |
| PV-DDPM per fold (arm 4) | learned rendering | none (no half-cut training labels) | 12 | gated |
| MultiSolSegment / PV-Vision / MSPS as extra training sets | dark class (MSS) only | more labs | 2 to 3 each on arm 1 code | after arm 1 reads; dedup MSS CWRU against SDLE |
| PVEL-AD boxes | none (no inactive) | another camera, crack only | 6+ | parked; signed form needed |
| Physics renderer (rule) | E4: rule explains 27% of labelled inactive, 18 donor cells | none | 6 | parked |
| Unpaired translators to half-cut style | none | targets E1 style; crack preservation unverified | 12+ | parked |

No data route here supplies labelled half-cut cells: none of the public sets is known to contain them (UCF unknown, S; E-SCDD half-cuts are H36 / sealed). The unseen-layout gap stays with other families.

## 6. What an "extra data" track of the benchmark must declare
1. Each external dataset: name, host, version / commit, file list with md5, licence text, and whether the data may be redistributed (UCF: no licence file; ELPV: CC BY-NC-SA; MSPS: CC BY; MSS: unstated on OSTI).
2. The label mapping table into the 24 classes (hard / allowed set / ignore), with the convention rules and thresholds (here: isolated-region darkness <= 0.60, ring widths, skeleton for closed cracks) and the per-dataset share of kept and dropped regions.
3. Geometry and intensity transforms (scale 0.85, canvas, padding class).
4. Duplicate and provenance search: method (descriptor, threshold, md5), the sets searched (all 816 BenchmarkEL stems, E1 106, `_rf` 117), hits and exclusions, and an explicit statement of what could not be checked (ELPV modules; MSS CWRU against SDLE until hashed).
5. Provenance of every generator or teacher: training cells by stem list; released third-party weights trained on SCDD / E-SCDD are forbidden because they saw the legacy test and E1 cells (E5, R P042).
6. Sampling ratio, loss weights and the number of external images seen during training.
7. Results with the per-source table, and BMRK / SDLE rows flagged when ELPV or MSS (CWRU) data was used.
8. The plain-data comparator: the same model and schedule without the external data, same machine and seeds.
