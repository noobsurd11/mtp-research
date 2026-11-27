# T13 spec: few-shot, in-context and promptable segmentation (13 Nov 2026)

Analyst T13. Tags: R = paper or repository page, E = our files, S = my judgement. Nothing here was run. Paper cards: `T13_fewshot_open_family.md`. Ledger: `ledger/T13.tsv` (24 papers: RUN_NOW 1, RUN_AFTER_GATE 1, BENCH_ONLY 5, PROTOCOL 2, PARKED 15).

## 0. Summary for the lead

| # | Arm | Papers | Problem | Primary (pre-declared) | Route | Build h | GPU-h | Waits for | Priority |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `sam_prompt_refine` | P327 | inactive | inactive IoU at OP-A, refined minus unrefined, same dumps | inference_only | 5 | 0.2 (or 1 h CPU) | W1-G PF dumps (exist), T10 A0 bucket read, pre-check P-SAM | 60 |
| 2 | `icl_oof_probe` | P327, P588 (P410, P548, P557 follow) | measurement (labeller quality) + benchmark_row (T3b) | share of PF-missed inactive regions found by SAM 2 video mode, K = 4, retrieved supports | inference_only | 6 | 1 | nothing (GT + W1-G dumps) | 50 |
| 3 | `t3b_fewshot_rule` | P588 (P327 as comparator) | unseen_modules (T3b protocol) | crack relF1@2 gain over zero-shot at K = 16 on the LOSO-2 proxy | training_recipe | 4 | 17.6 | user decision D5 on T3b; T7 LOSO-2 roots and base models | 40 |

**First arm and why (S).** `sam_prompt_refine`: 5 build hours, almost no GPU, and it is read paired on the same predictions, so seed noise cancels (the same reason T10 puts its post-hoc arms first). It uses existing support only: the W1-G PF dumps (`pred`, `oth`, `p_inact`, `logp`), `bench/dumpfmt.py` to write derived dumps, `bench_score.py` and the two-stage bootstrap of `crossfit_op.py` / `bench_read_w1.py` (x3, E), and `venv_sam2` with SAM 2 source 2b90b9f (E, DESIGN 1.10).

**How these differ from queued arms (E, WAVE2_REVIEW 4, T6, T7, T10 specs).** No wave-2 or family arm uses a promptable or in-context model. T10's parked `inact_refiner` (gate G-refine) is a trained refiner with ConvCRF as control; arm 1 is a zero-training refiner and shares T10's A0 error atlas as its gate. T6 uses SAM 2 Hiera only as an encoder inside the house U-Net++; arms 1 and 2 use SAM 2's own prompt encoder, memory and mask decoder. T7's LOSO-2 instrument is reused by arm 3 for a different question (adaptation with K labelled target cells, not zero-shot transfer).

**What I decided about labelling (the focus question).**
- Which model: SAM 2.1 (Apache-2.0, public, E local Hiera-T, others downloadable). Not SAM 3 (gated), not SegGPT (canvas halves each cell). Hiera-S for video mode (best in GFDS, R: 47.9 v 43.8 for Hiera-L); Hiera-L for the single-image refiner if pre-check P-SAM prefers it.
- Prompt source: the house PF model's own inactive components (arm 1); labelled training-fold cells retrieved by image similarity (arm 2). Ridge filters are **not** used as prompts: they are line detectors, and SAM 2 returns 256 x 256 logits for a 1024 input (S), so a crack prompt cannot come back as a 1 to 2 px line. Crack labelling stays with T4 `ridge_snap`.
- Label quality without sealed sets: leave-fold-out on the 532 cv5v2 cells (supports from the training folds only), F51 for unseen full-cell modules, the 19 crack-free H36 half-cells for false alarms. Agreement with the house model on pool cells is not a quality measure and is never used as one.
- A pool-labelling GPU arm is **not** specified now. It opens only through gate G-lab of arm 2.

**T3b: what the protocol should fix now (S; details in arm 3, section 3.6).** K in {4, 16} plus "all"; shots one cell per image id, drawn from the training side of the frozen K = 5 E1 folds, at least ceil(K/2) crack cells; 3 draws with seeds 0, 1, 2 from a committed script, list md5 committed before the opening; 2 base seeds; report mean and range over draws, pooled out-of-fold, relF1@2 and any-hit recall primary, width ratio beside, false alarms on the 74 crack-free cells, 71-cluster interval, zero-shot row of the same base model beside. The adaptation rule (fine-tune with source replay, fine-tune target-only, or retrain) is chosen on the LOSO-2 proxy by arm 3 and frozen before T3b.

---

## 1. Arm 1. `sam_prompt_refine`: SAM 2 prompted by house inactive components

### 1.1 Hypothesis and evidence
- **Hypothesis (S).** Part of the inactive error is boundary and hole error around regions the house model already found (T10 A0 buckets FN-boundary, FP-boundary, FN-interior). Inactive regions in EL are dark areas bounded by cracks and cell edges, the kind of sharp-edged region SAM 2 segments well. Prompted with each house component (box + interior points), SAM 2 returns a mask whose boundary follows the image edges; replacing the component by that mask when the two agree raises inactive IoU without new labels and without training.
- **Evidence (R, P327).** On 54 industrial defect classes, refining a coarse feature-matching prediction with SAM masks by an overlap rule raised mIoU from 36.5 to 39.3 (union alone 37.8; SAM masks alone 22.1). SAM 2 at 1024 px input beats 512 px by 9.1 mIoU, so cells are upsampled. No EL or thin-structure evidence.
- **Evidence (E).** Inactive is blobby and well labelled (1 px shift IoU 0.94); PF inactive precision 0.63, recall 0.61 on test; CV out-of-fold inactive IoU 0.50 to 0.52 (B6). How much of the error sits at boundaries is not measured yet: T10 A0 measures it tonight.
- **BRIEF 5 overlap:** none. No refinement stage was ever run ("learned refinement stages" listed as open; SAM 2 only linear-probed as a frozen encoder).

### 1.2 Exact change
New file `bench/post/sam_refine.py` in el_bench (run with `venv_sam2/bin/python -I`; numpy and scipy come from the house site-packages through the existing `.pth`, E). No trainer, model factory or loss change. Switched on by running the script on existing dumps; the output is a derived method `house_r34_unetpp_pf_v11+samref` with its own manifest (base run id and md5s, SAM checkpoint md5, parameters below, script md5).

```
inputs per cell: img uint8 (512,512) from the run's labeled/images;
                 dump: pred u8 (512,512), oth u8, m_crack f16, p_crack f16, p_inact f16, logp f16 (24,512,512)
constants (fixed now): MIN_C = 100 px; PAD = 4 px; N_POS = 3; TAU_ACC = 0.5; MAX_GROW = 2.0;
                       PROTECT = {14 crack} plus the class ids of padding and frame_edge (from the 24-class list)
SAM: SAM2ImagePredictor(build_sam2(cfg, ckpt)), fp32, TF32 off; model chosen by pre-check P-SAM (Hiera-L or Hiera-T)

x = clip((img - p1) / (p99 - p1), 0, 1) * 255  -> uint8 -> stack 3 channels (512,512,3)    # p1, p99 per cell
predictor.set_image(x)                                   # SAM resizes to 1024 internally
alt = argmax over classes {0..23} minus {11, 14} of logp  -> u8 (512,512)   # fallback class for removed px
new = pred.copy()
lab, n = scipy.ndimage.label(pred == 11, structure=ones(3,3))
for each component C with |C| >= MIN_C:
    box = bbox(C) expanded by PAD, clipped to the image          # xyxy in 512 px coordinates
    dt  = distance_transform_edt(C)
    pos = argmax(dt) plus 2 more points by farthest-point sampling among px with dt >= 3 (fewer if none)
    masks, scores, _ = predictor.predict(point_coords=pos, point_labels=ones, box=box, multimask_output=True)
    # masks: (3,512,512) bool at original image size
    m = masks[argmax_j IoU(masks[j], C)]                         # anchored on the house component, not on SAM's score
    if IoU(m, C) >= TAU_ACC and |m| <= MAX_GROW * |C|:
        R = m & ~isin(pred, PROTECT) & ~(other components of lab)    # never touches crack or other inactive components
        new[C & ~R] = alt[C & ~R]
        new[R & ~C] = 11
    else: keep C unchanged                                       # logged as rejected with IoU(m, C)
components < MIN_C: unchanged
write dump: pred = new; oth = new where new != 14 else old oth; m_crack, p_crack, p_inact copied unchanged
assert (new == 14) == (pred == 14)                                # crack untouched by construction
```

Writer check `pred == where(m_crack > 0, 14, oth)` still holds because crack px and `m_crack` are unchanged and `oth` is updated wherever `pred` changed.

Secondary readouts (descriptive, Holm over 2 with the primary): `drop` = additionally delete a component when max_j IoU(masks[j], C) < 0.2 (SAM sees no object there, P327's tau1); `morph_ctrl` = the same components replaced by binary closing (radius 2) + hole filling, no SAM. `morph_ctrl` is the control: SAM is credited only with `samref` minus `morph_ctrl` as well as minus the unrefined dump.

**Unit tests** (`tests/test_sam_refine.py`, CPU, Hiera-T):
1. A cell with no inactive px: output dump byte-identical to input.
2. Synthetic image: a dark 120 x 80 rectangle on grey; house component = the rectangle eroded by 3 px plus a 5 px spur; refined IoU with the rectangle >= 0.9.
3. Crack invariance: random dumps from 5 real cells, `(new == 14) == (pred == 14)` everywhere.
4. Protected classes never become 11; px of a second inactive component never change.
5. Writer check passes on 20 real cells; the derived manifest names the base run md5.
6. Determinism: two runs give identical dumps (fp32, TF32 off).

### 1.3 CPU pre-check P-SAM (decides model and whether the arm runs; about 1 build hour, under 1 h on gaint CPU)
- Cells: the 48 P532 cells with GT inactive (E, PROTOCOL 3.2). Training-free model, so no leakage from using train labels.
- For each GT inactive component >= 100 px: prompt = GT bbox + PAD and 3 interior points chosen as above from the GT component; take the mask with the highest IoU against GT ("oracle choice") and the one with SAM's highest score ("blind choice").
- Run with Hiera-T (local) and Hiera-L (download).
- **Pass rule (fixed now):** with the better model, pooled IoU of the blind-choice masks against GT >= 0.80 and median component IoU >= 0.80. Fail = SAM cannot reproduce our inactive regions even from a perfect prompt; the arm is dropped (1 build hour spent). The better model is fixed for the arm.
- **Gate from T10 A0 (read, not computed here):** run the arm if FN-boundary + FP-boundary + FN-interior + FP-spurious >= 30% of inactive error px (seed-mean); otherwise report "dominant inactive errors are missed regions or the crack overlap, which a prompted refiner cannot act on" and stop.

### 1.4 Pathfinder and screen
- No training, no pathfinder. Readout 1: W1-G PF dumps (gaint, seeds 5 and 6, all 5 folds) with `logp`. Readout 2 (confirmation): the same script on W1-C1 seeds 5 to 9 once relayed. Scored by `bench_score.py`; the contrast against the unrefined dumps of the same runs, two-stage bootstrap (330 groups, then seeds).
- **Pass (fixed now, same form as T10 arm 1):** delta inactive IoU >= 0.01 with the 95% interval above 0; inactive precision and recall each not down by more than 0.02; inactive region precision not down by more than 0.02; mIoU-R13 not down by more than 0.005; crack metrics identical (asserted); and `samref` minus `morph_ctrl` > 0 with interval above 0. Since the contrast is paired on the same predictions, seed noise cancels and the 0.01 floor is the margin (S); the A/A null is still printed beside it as WAVE2 section 5 item 8 requires.
- **F51 look:** apply to F51 dumps of the 10 W1-C1 seed 5 and 6 models (shared job with T6), paired, read ledger only (X9).
- Guards: WAVE2 section 5 items 1 to 8 (crack items are identical by construction and printed as such); per-source inactive rows (BMRK separately, it is the weak inactive source); predicted inactive px on the 484 inactive-free cells; count and IoU distribution of rejected components.

### 1.5 What it should move, drop rule
- Expected (S, scaled from R): P327's +2.8 mIoU came from refining a coarse patch-level matcher; our house decoder predicts at full resolution, so the boundary error left is smaller. Estimate +0.00 to +0.03 inactive IoU, at most O4 + interior oracle from T10 A0.
- Drop: P-SAM fails; or the A0 gate is not met; or delta < 0.01; or a guard fails. A null closes "SAM 2.1 box + point refinement of PF inactive components at 1024 px with these thresholds", nothing else.

### 1.6 Cost, needs
- Build 5 h: script 2.5, tests 1, P-SAM 1, readout wiring 0.5. GPU: about 0.2 GPU-h for 10 runs (only cells with predicted inactive components, about 1 SAM call per component), or about 1 h on gaint CPU.
- Needs: `venv_sam2` (exists, E). Check before building that source 2b90b9f builds the 2.1 configs (E: SAM 2.1 Hiera-T weights are already used on gaint). SAM 2.1 Hiera-L checkpoint `sam2.1_hiera_large.pt`, Apache-2.0, public download from dl.fbaipublicfiles.com (R, SAM 2 README), not gated. No new package.

### 1.7 Risks and how it could mislead
1. **Operating-point shift.** SAM masks that are systematically larger than house components raise recall and lower precision: precision and recall guards, and the `morph_ctrl` row (a pure closing would show the same shift).
2. **Busbars and ribbons crossing an inactive region** can split SAM's mask, so a region loses px: recall guard, rejected-component log.
3. **Dark non-inactive areas** (edge_dark, padding of BMRK cells, scuff on pool cells) can pull SAM masks outward: MAX_GROW, protected classes, per-source table.
4. **Leakage:** none; SAM never saw EL, thresholds are fixed now. If any threshold is changed after a read, it must be cross-fitted over folds with `crossfit_op`'s loop.
5. **Transfer:** the readout is in-distribution. E1 inactive cannot be measured (3 images, E), so an unseen-module claim cannot come from this arm.

---

## 2. Arm 2. `icl_oof_probe`: SAM 2 video-mode in-context segmentation, leave-fold-out on cv5v2

### 2.1 Hypothesis and evidence
- **Question.** Does an in-context foundation model, given K labelled training-fold cells as supports, find what the house model misses on held-out cells? This decides (a) whether any automatic labeller (pool half-cells, second-opinion labels) is worth a GPU arm, and (b) the in-context rows of the T3b track and their support rule.
- **Evidence (R, P327).** SAM 2 video mode, support as the previous frame, 47.9 mIoU 1-shot on 54 defect classes; meta-learning FSS at most 19.2, Matcher 5.0. (R, P410) frozen SAM 2 in the same pseudo-video pipeline: 32.2 COCO-20i 1-shot; adapters raise it to 60.2. (R, P588, scout) retrieved supports beat random supports.
- **BRIEF 5 overlap (E):** pseudo-label SSL with the house teacher was n.d. at 100% labels on the 11.9k pool. That used the house model as teacher; an in-context foundation model has not been tested.

### 2.2 Exact change
New files in el_bench: `bench/icl/retrieve.py` (house venv), `bench/icl/sam2_video_fss.py` (venv_sam2), `bench/icl/icl_score.py` (house venv, numpy + scipy, reuses `bench_score` primitives `comps`, `cell_stats`).

```
classes C = {11 inactive, 14 crack, 16 splice, 20 edge_dark}
min px to be a support for class c: 11: 100, 14: 20, 16: 20, 20: 50
retrieval feature: DINOv2 ViT-S/14 CLS token (local weights dinov2_vits14_pretrain.pth, E), input = cell stretched as
    in arm 1, 3 channels, resized to 518 px; L2-normalised; one 384-d vector per cell; computed for the 532 cells and F51
support pool for a query in fold k and class c: cv5v2 cells NOT in fold k with >= min px of c (v1.1 strict masks)
    assert: no pool cell is in fold k; no sealed stem anywhere (forbidden list, fails closed)
rule 'ret': rank pool by cosine to the query; same source first, then other sources; take top K
rule 'rnd': K cells drawn uniformly from the pool with seed = crc32(f"{stem}|{c}|{K}")
K in {1, 4}            # SAM 2 keeps 7 memory frames by default (S, check num_maskmem in the config), so K <= 6

episode (one query cell q, one class c, one K, one rule):
    frames 0..K-1 = supports, frame K = q; each frame = stretched 3-channel uint8 written as JPEG quality 100
        into a fresh temp dir (the video predictor reads a frame folder; check whether 2b90b9f accepts arrays)
    state = predictor.init_state(dir)
    for i in 0..K-1: predictor.add_new_mask(state, frame_idx=i, obj_id=1, mask=(GT_support_i == c))
        # add_new_mask is not in the README; confirm it exists in sam2_video_predictor.py at 2b90b9f, else
        # fall back to add_new_points_or_box with the support's bbox + 3 interior points per support
    for (f, ids, logits) in predictor.propagate_in_video(state, start_frame_idx=0): keep logits at f == K
    out = (logits[0,0] > 0) at 512 x 512 -> uint8; save bench_out/t13/icl/<rule>_K<K>/<set>/<stem>_c<c>.npz
queries: every cell of cv5v2 fold k (all 532 over the 5 folds), for every c in C, whether or not q contains c
extra: F51 (supports from all 532, 'ret', K = 4); H36 crack-free 19 cells (classes 11, 14; false alarms only)
model: SAM 2.1 Hiera-S (best in P327, R), fp32, TF32 off; 1024 px internal
```

`icl_score.py` (per class c, pooled over the 532 out-of-fold queries; PF = W1-G seeds 5 and 6, each scored, then averaged):
1. IoU, P, R of ICL and of PF (`pred == c`); crack also relP@2, relR@2, relF1@2 and predicted width ratio.
2. Complementarity: share of PF false-negative px of c covered by ICL; precision of ICL px outside PF's prediction ("novel-px precision").
3. Inactive regions (GT components >= 100 px): PF-missed regions (< 10% covered by PF in the seed-mean) and how many ICL covers >= 50%; ICL-only predicted regions (>= 100 px, no PF overlap) and their precision.
4. Filter use: precision and recall of `PF & ICL` against PF alone.
5. ret minus rnd, K = 4 minus K = 1 (support-rule evidence for T3b).
6. False alarms: ICL px of c on query cells without c; on H36 crack-free cells.
Group bootstrap (330 groups) on every contrast with PF; seeds enter only through PF.

**Unit tests:** (1) retrieval never returns a fold-k cell for a fold-k query (all 532 x 4 classes x 2 rules); (2) `rnd` is reproducible; (3) with K = 1 and the query equal to the support image and mask (a self-episode on 5 cells, test only), ICL IoU with that mask >= 0.8 for inactive, proving the plumbing; (4) temp dirs are removed; (5) output file count = queries x classes x settings.

### 2.3 Pre-check
None needed before the run: it is itself a CPU-scored GPU-inference probe of about 1 GPU-h. Readable only if at least 8 PF-missed inactive regions exist in the 532 OOF predictions (count from T10 A0 (a) bucket FN-missed); if fewer, item 3 is reported as "not readable" and G-lab is decided on items 2 and 4 only.

### 2.4 Gates (fixed now)
- **G-lab** (opens P410 SANSA with an EL-episodic adapter and a pool-labelling arm, to be specified with T7, whose `mic_halfcell` is the natural consumer): for inactive, `ret`, K = 4: ICL covers >= 25% of the PF-missed GT inactive regions with ICL-only region precision >= 0.5; or the filter `PF & ICL` raises inactive precision by >= 0.05 at a recall loss <= 0.05, both with group-bootstrap intervals excluding 0. Otherwise the labeller route stays parked (not void; it closes only SAM 2.1-S video mode with these supports).
- **G-weak** (hand to T10): splice or edge_dark ICL IoU above PF IoU by >= 0.05 pooled OOF (PF never predicts splice on test, E BRIEF 3).
- **Crack:** no gate. Expected to fail on width (S); reported for the T3b table with the width ratio beside.
- **T3b rows:** produced regardless; the support rule for T3b in-context rows is `ret` unless `rnd` is within 0.02 on inactive IoU (then `rnd`, which needs no feature model).

### 2.5 What it should move, drop rule
- Expected (S): inactive ICL IoU well below PF (P327's industrial classes are larger and more distinct than ours); the value is in complementarity, which I cannot estimate from the papers. If G-lab fails, no labeller arm is built and the T13 GPU budget goes to arm 3 only.
- This probe changes no model, so it has no promotion; its outputs are gates and benchmark rows.

### 2.6 Cost, needs
- Build 6 h (retrieval 1, episodes 2.5, scorer 1.5, tests 1). GPU about 1 GPU-h: 532 x 4 classes x 4 settings = 8,512 episodes of 2 to 5 frames at 1024 px with Hiera-S (P327, R: 32 FPS at 1024 for 1-shot) plus F51 and H36; one gaint lane, peak memory to measure (S: under 4 GB).
- Needs: `venv_sam2` (E), SAM 2.1 Hiera-S checkpoint (public, Apache-2.0, R), DINOv2 ViT-S/14 weights (local, E; loading through timm or the hub code without network to be checked; fallback: the mean-pooled SAM 2 image embedding as the retrieval feature). Not gated.

### 2.7 Risks and how it could mislead
1. **Width.** SAM 2 logits are upsampled from 256 x 256; tolerant crack metrics flatter thick masks. Width ratio and relF1@1 are printed beside every crack row.
2. **"Finding" missed regions by dark-blob detection.** ICL-only region precision and false alarms on inactive-free cells guard it.
3. **Leakage.** Supports only from the training folds of the query (asserted); F51 supports from the 532 only; no sealed cell is read or used as a support.
4. **Selection on the probe.** Four settings are read; the gate fixes `ret`, K = 4 as the primary setting now.
5. **Transfer.** Full cells only; half-cell behaviour is seen only through H36 false alarms. A G-lab pass does not show the labeller works on pool half-cells; the follow-up arm must be scored on cv5v2 (does training on its labels help held-out folds) before any E1 claim.

---

## 3. Arm 3. `t3b_fewshot_rule`: choose the T3b adaptation rule on a proxy, then freeze it

### 3.1 Hypothesis and reason
- **Question (S).** When a few labelled cells of a new layout or source become available, which adaptation rule turns them into the largest gain: fine-tune the zero-shot model with source replay, fine-tune on the target cells alone, or retrain from scratch with the cells added? T3b cannot answer this on E1 itself (about 10 hard-stratum image ids, E `T3B_PROPOSAL.md` 4), and it must not tune on E1 (proposal rule 6.3). So the rule is chosen on a leave-one-source-out proxy and frozen.
- **Evidence:** P588 (R, scout): support choice matters for in-context methods; I found no paper in this family that compares adaptation rules for dense segmentation under a source shift (S). E: T7's LOSO-2 instrument (CSIR held out: 114 cells, 51 crack, 76 groups; BMRK held out: 50 cells, 30 crack, 50 groups) exists as a spec with base models planned (T7 0.4, 8.8 GPU-h).

### 3.2 Exact change (config and roots only)
- **Proxy split (new file `benchmark/splits/t3b_proxy.json`, by `bench/t3b/make_proxy.py`):** for each held-out source s in {CSIR, BMRK}, split the source's module groups 40 / 60 into a shot pool and a score set with seed 20261113, stratified by "group has a crack cell (>= 20 px)". Draws d in {0..4}, K in {4, 16}: K cells, one per group, from the shot pool, at least ceil(K/2) with crack >= 20 px, sampled with seed d. The score set is the same for every K and draw, so rows are comparable. md5 committed before any run.
- **Roots** (`bench_make_roots.py`, same asserts as B6 plus: score-set stems never in train.txt; shot stems only from the shot pool): train.txt = LOSO train stems (P532 minus source s) + the K shot stems repeated r times, r = round(N_train / K) (about 50% of samples are shots, S); test.txt = val.txt = score set. Unit test first: `BenchmarkELDataset` and `BatchStream` accept repeated stems and the sample share of shots over 2,000 draws is 0.45 to 0.55.
- **Rules** (card keys use the names in `house_r34_unetpp_pf_v11`; values below):
  - R0 zero-shot: the T7 LOSO-2 PF base model, dumped on the score set.
  - R1 replay fine-tune: `model.encoder_init` and `model.decoder_init` = base `latest.pth` (E, train.py l.263-268); total steps 2,000; lr 1e-4 (0.1 x house), warmup 100, cosine; PF groups kept with encoder lr x 0.1 and no encoder weight decay, freeze steps 0; train list as above (shots + source).
  - R1b target-only fine-tune: as R1, train.txt = the K shots only.
  - R2 retrain: house PF card from ImageNet, 20k steps, train list as R1 (shots repeated). K = 16 only, draws 0 and 1.
- Base seeds 5 and 6 (T7's U1 models). Each rule run gets the base seed as its training seed.

### 3.3 CPU pre-check (0.5 build h)
Counts of the proxy split per source: score-set crack cells, crack components >= 20 px, inactive cells; shot-pool crack groups. **Pass:** each score set has >= 15 crack cells and >= 100 crack components >= 20 px, and each shot pool has >= 8 crack groups (needed for K = 16 with ceil(K/2) crack). BMRK may fail (50 groups, 30 crack cells): then BMRK runs only K = 4 and the decision uses CSIR.

### 3.4 Pathfinder and screen
- Pathfinder: one R1 run, CSIR, K = 16, draw 0, seed 5 (0.11 GPU-h): failure, step time, memory, confirms that init loading reproduces the base model's score-set dump at step 0 (identity check: a 0-step run equals R0 bit for bit).
- Screen: R1 and R1b, 2 sources x 2 K x 5 draws x 2 seeds = 80 runs x 2k steps (about 0.11 GPU-h each, 8.8 GPU-h); R2, 2 sources x 2 draws x 2 seeds = 8 runs (8.8 GPU-h). All on gaint against T7's gaint base models (one machine per comparison).
- **Primary:** pooled score-set crack relF1@2 at OP-A, rule minus R0, mean over draws and seeds, at K = 16. Guards: any-hit component recall, width ratio (0.85 to 1.15 x R0), false alarms on crack-free score cells, inactive IoU and precision (descriptive), the in-distribution cost (each rule's model re-scored on the source model's own cv5v2 fold-0 held-out cells: forgetting).
- **Decision (fixed now):** the rule with the highest mean gain at K = 16 (average of the two sources, CSIR only if BMRK fails the pre-check) is frozen for T3b, provided its width and false-alarm guards hold; ties within 0.01 go to the cheaper rule (R1 or R1b before R2). If no rule gains >= +0.02 at K = 16, T3b keeps only the "all" row of the proposal and drops the few-shot rows (reported to the user). The spread over draws at K = 4 sets how many draws T3b needs (3 if the draw range is under 0.05, else 5).

### 3.5 What it should move, drop rule
- Expected (S): a sizeable gain for CSIR held out (zero-shot transfer to an unseen source is the weak case; any labelled target cells should help), smaller for BMRK. No paper number backs a size. This arm produces a rule, not a model for the final table, so there is no promotion; its drop rule is the "no rule gains >= +0.02" clause above.

### 3.6 What the T3b protocol fixes (recommendation for T3B_PROPOSAL, S)
1. K in {4, 16} plus "all" (the proposal's arm: every training-side E1 cell, about 85).
2. Shots per E1 fold: one cell per image id from the training side of the frozen K = 5 E1 folds; at least ceil(K/2) crack cells (>= 20 px); at K = 16 at least 2 from the hard stratum (half-cut + scuff), because 75% of E1 crack px are there (E).
3. Draws: 3 (or 5, from 3.4), seeds 0 to 2, generated by a committed script; list md5 committed and logged in `e1_openings.md` before the opening.
4. Base model: the final cv5v2 recipe trained on the 532 pool, seeds 5 and 6; rule frozen from this arm; final weights; argmax; any crack bias fitted on the shot cells only (never on held-out E1 cells).
5. Report: pooled out-of-fold headline card on the two E1 strata, relF1@2 and any-hit recall primary, width ratio beside (E1 labels are about 1.5x wider, E), false alarms on the 74 crack-free cells, 71-cluster interval, mean and range over draws, zero-shot row of the same base beside, `trained_on_e1` mark on every row.
6. In-context rows (arm 2's harness): SAM 2.1-S video mode with the same K = 4 shots as supports (K = 16 exceeds the memory bank); SegGPT (P548), FSSDINO (P557), FSS-SAM3 (P503, gated) only if added before the opening.
7. Cost of T3b itself with rule R1 or R1b: 2 K x 3 draws x 5 folds x 2 seeds = 60 runs x 0.11 = about 7 GPU-h, plus the proposal's "all" arm (about 11 GPU-h).

### 3.7 Cost, needs, risks
- Build 4 h (proxy split + script 1, roots with repeated stems + test 1.5, cards 0.5, readout 1). GPU 17.6 h (8.8 fine-tunes + 8.8 retrains), plus T7's base models (8.8 GPU-h, already in T7's plan; arm 3 waits for them).
- Needs: nothing new (house venv, existing init keys, T7's LOSO-2 roots).
- Risks: (1) **The proxy may not transfer.** A source shift (BMRK scale, CSIR camera) is not a layout shift (half-cut + scuff); the proxy chooses the rule, it does not predict E1 gains. (2) **Width learning.** Shots from a source with another label width (BMRK 3.0 px, E) teach width; relF1@2 can rise through width alone: width guard. (3) **Forgetting** shows only in the in-distribution re-score, which is reported. (4) **Draw luck:** the rule decision averages 5 draws x 2 seeds; with one draw the order of rules could flip. (5) **Leakage:** score-set stems must never appear in train.txt (asserted in the root builder; fails closed). (6) Runs only after the user's decision D5; if T3b is declined, arm 3 is not run.

---

## 4. What the lead must know (S)
1. Nothing in this family is expected to raise crack scores. Its value is one cheap inactive refiner (arm 1), one decision about labellers (arm 2), and a frozen T3b rule (arm 3).
2. No gated weights are needed for the three arms. Gated items for the user, only for benchmark rows: SAM 3 (`facebook/sam3`, HF access request; P503, P458) and DINOv3 ViT-L (P070, P557 at full size).
3. Licences to note for WattCycle: SOFS is CC BY-NC-SA 4.0 (benchmark row only); GFDS, FSS-SAM3, SANSA and CSWinUNETR state no licence on the pages read; SAM 2 and DINOv3-IML are Apache-2.0 and MIT.
4. Handed over from the open sweep (ledger notes give the status I would give): P137 to T11 (BENCH_ONLY), P070 to T6, P245 and P532 to T8, P306, P347, P421, P530 to T7, P376 to T10 / T3, P457 to T4, P635 to T12 (PROTOCOL), P466 to T11 / T6, P569 to T6 / T8 (all PARKED unless stated).
