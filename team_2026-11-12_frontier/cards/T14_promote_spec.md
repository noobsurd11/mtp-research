# T14 spec: arms from the ten PROMOTE papers (15 Nov 2026)

Analyst T14. Tags: R = paper (section) or repository page, E = our files, S = my judgement. Nothing here was run or built. Paper cards: `T14_promote_family.md`. Ledger: `ledger/T14.tsv` (10 papers: RUN_AFTER_GATE 4, PROTOCOL 1, BENCH_ONLY 1, PARKED 4; RUN_NOW 0).
Margins used below (E, `results/ROWS1_READ.md` 4, `results/W1C_READ.md` 2): M = 0.010 for strict crack IoU, crack relF1@2 and mIoU-R13 on both machines; 0.013 (cv02) and 0.011 (gaint) for relR@2; inactive IoU 0.049 / 0.054, so inactive is read by counts only.
Comparator of every trained arm: card `house_r34_unetpp_pf_v11` (PF), label set v1.1, cv5v2, 20k steps, batch 8, 512 px, final weights, seeds 5 and 6, same machine as its PF runs.

## 0. Summary for the lead

| # | Arm | Papers | Problem | Primary (pre-declared) | Route | Build h | GPU-h | Waits for | Priority |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `gap_census` | P117 | measurement (anatomy of missed crack px); orders 5 continuity arms | bound_gap = missed px in interior gaps / GT crack px, read against 0.013 | analysis_only (CPU) | 1.5 | 0 | nothing (W1-G PF dumps; confirm on W1-C1) | 55 |
| 2 | `dec_gn_pf` | P044 | crack + balance (normalisation) | crack relF1@2 at OP-A and OP-W, arm minus PF | config + 20-line model code | 1.5 | 1.1 + 11 | gate G-BN: `raw_bn` minus `raw` on the w2a ema dumps | 40 |
| 3 | `t3b_surgical_rules` | P166 | unseen_modules (T3b protocol) | crack relF1@2 on the LOSO-2 proxy score set at K = 16, rule minus R1 | training_recipe | 1.5 | 0.2 + 8.8 | T13 arm 3 `t3b_fewshot_rule` and its base models | 35 |
| 4 | `trace_crack` | P117 | crack (recall, continuity) | crack relR@2 at OP-W, arm minus PF and arm minus `skr01_pf_v11` | new_loss + aux target | 6 | 1.1 + 11 | `gap_census` opens; alt-route census; `skr01_pf_v11` row read; equations checked in the PDF | 30 |
| 5 | `label_version_strata` | P184 | measurement (benchmark view) | none (descriptive): relR@2 on stable crack px against px added by the label revision | analysis_only (CPU) | 1.5 | 0 | nothing | 30 |
| 6 | `label_jitter_crack` | P210 | crack (label jitter) | strict crack IoU at OP-A and OP-W, arm minus PF | data_pipeline | 2 | 1.1 + 11 | `soft_band_jml` minus `jml_hard` passes (w2a read); pre-check P-J | 25 |
| 7 | `wtconvnext_t_hrstem_unetpp_pf` | P220 | benchmark_row | crack relF1@2 at OP-A (table row); row minus the ConvNeXt-T control printed beside | new_model_code (vendored) | 3.5 | 1.5 + 16 | C3 ConvNeXt-T HR-stem control read; `bench_vendored` (S9) | 20 |

Totals: 17.5 build h and about 63 GPU-h if every gate opens. Firm now: 1.5 build h, 0 GPU-h (`gap_census`); 3 h with `label_version_strata`.

**First item and why (S).** `gap_census`: 1.5 h, CPU, existing dumps. It decides `trace_crack` before any build, and it tells whether the four wave-2 arms that claim continuity (`clce_crack`, `scnp_cedice`, `coletra_crack`) or short-component recall (`cc_dicece_crack`) can move their own primaries at all. It is to the continuity cluster what D0 was to the placement cluster. Nothing else in this file should take GPU time before its gate is read.

**How these differ from queued arms (E).** No queued arm changes a normalisation layer (arm 2). No T3b rule freezes part of the network (arm 3). No arm supervises a prediction-dependent pixel (arm 4; Skeleton Recall and clCE use a fixed skeleton). No read splits recall by label version (arm 5). Arm 6 is the stochastic sibling of `soft_band_jml`. Arm 7 is a third ConvNeXt-family row. Papers P059, P240, P258, P372 have no arm (cards give the reasons).

**Guards.** Every trained arm reports WAVE2_REVIEW section 5 items 1 to 12. From WAVE3_REVIEW section 6: G14 (arm 7 names its weights and md5; no arm has a teacher or a second data stream, so G13 and G17 do not apply), G15 (arm 3: a proxy read is never a claim about E1; arms 2 and 7: the transfer claim is "untested until the E1 opening", secondary reads U5, H36 false alarms, U1 only after a CV pass), G16 (arms 2, 4, 7 print step time and peak memory; arm 7 prints parameters and GFLOPs and, above 2x house cost, the PF 2-seed ensemble beside it), G18 (arm 2: any mIoU-R13 or inactive movement is read at OP-A and against PF at OP-C), G19 (arms 1 and 5: parameters fixed here, explored on W1-G, confirmed unchanged on W1-C1, variants counted in the ledger), G20 (arms 2 and 4: inactive by region counts, never pooled IoU).

---

## 1. Arm 1. `gap_census`: where the missed crack pixels are (CPU pre-check of arm 4)

### 1.1 Question and evidence
- **Question (S).** PF misses 20% of ground-truth crack px at 2 px tolerance (relR@2 0.799; E `results/w1c_read/read.txt`). A continuity loss can only win back missed px that lie between two found parts of the same crack. How large is that share?
- **Evidence (E).** Components of at least 20 px: any-hit recall 0.886, 50%-coverage recall 0.811 (same file). 88 and 95 of 989 components are missed by both seeds, and the 2-seed ensemble recovers none of them (E `results/stageA/A2_P1_G5.md`). So part of the deficit is whole cracks the model does not see; the split has not been measured.
- **Evidence (R, P117).** TRACE's gains are in Betti error and clDice (connectivity); Dice gains over Skeleton Recall are 0.2 to 0.9 points.

### 1.2 Exact computation
New file `scripts/bench_gap_census.py` (house venv, numpy + scipy; reuses `bench.m0core.S8`, the dump reader of `bench_score.py`, the group bootstrap of `crossfit_op`). Inputs: PF dumps (`pred`, `p_crack`), v1.1 strict masks and ignore of the 532 pool cells. No sealed set (the dump reader refuses them).

```
per cell: k = not ignore; g = (gt == 14) & k; p = (pred == 14) & k
dp = distance_transform_edt(~p)                      # distance to the nearest predicted crack px
miss = g & (dp > 2)                                  # exactly the px that relR@2 counts as missed
lab, n = ndimage.label(g, S8)                        # GT components, 8-connected, as m0core.comps
for each component C (size s, covered px c = |C & (dp <= 2)|):
    s < 20            -> all its missed px go to B_small
    s >= 20, c == 0   -> B_whole
    s >= 20, c > 0    -> for each 8-connected run R of (C & miss):
                           pieces = 8-connected components of C minus R
                           n_cov  = number of pieces that hold at least one covered px
                           n_cov >= 2 -> B_gap (the run separates two found parts)
                           else       -> B_end (a crack end or a branch tip not reached)
also per run in B_gap: length |R|; pmax = max p_crack over px within 2 px of R
outputs, pooled and per source (ARTS, BMRK, CFVS, CSIR), per seed, group-bootstrap interval (330 groups):
    share of |miss| in B_small, B_whole, B_gap, B_end           (the four sum to 1)
    bound_gap      = |B_gap| / |g|          # relR@2 gain if every interior gap were closed at no cost
    bound_gap_soft = |B_gap with pmax >= 0.01| / |g|
    frag = mean number of predicted components (8-connected) touching one GT component with c > 0
```
A gap of 4 px or less between two predicted segments is covered from both sides and never enters `miss`; `frag` is the only output that sees such gaps.

**Unit tests** (`tests/test_gap_census.py`): (1) a straight line with the middle third of the prediction removed: all missed px in B_gap; (2) one end removed: B_end; (3) no prediction: B_whole; (4) ignore px in no bucket; (5) the four buckets sum to `crack_rel2`'s missed count of `bench_score` on 20 real cells, exactly; (6) a Y-junction with one arm removed: B_end.

### 1.3 Reading rule (fixed now)
- bound_gap >= 0.013 with its interval above 0.008, on W1-G and again on W1-C1: continuity arms have room. Arm 4's first gate opens.
- bound_gap < 0.013 on both: a perfect gap-closing loss cannot move relR@2 by M. `trace_crack` is parked without a build. The lead is told that `clce_crack` (primary relR@2 at OP-W), `scnp_cedice` and `coletra_crack` share that ceiling: their primaries can then move only through whole missed cracks or ends, which is not their stated mechanism. `cc_dicece_crack` is read against B_small + B_whole instead.
- The machines disagree: the lead decides.
- It orders arms and closes none (the standing D0 has).

### 1.4 Cost, needs, risks
- Build 1.5 h (script 1, tests 0.5). About 10 CPU-minutes for 20 runs of 532 cells. Track: main. Variants read: 1.
- Risks: (1) a label that is itself dotted makes two GT components; a prediction bridging it is neither missed nor a gap, so the census under-counts continuity errors of that kind (`frag` shows them). (2) The 2 px tolerance hides gaps up to 4 px; that is a property of the headline metric, and the reason a topology gain may be invisible to it. State this beside the result.

---

## 2. Arm 2. `dec_gn_pf`: GroupNorm in the decoder, BatchNorm kept in the pretrained encoder

### 2.1 Hypothesis and evidence
- **Hypothesis (S).** Decoder BatchNorm uses running statistics averaged over five sources. If those statistics are a measurable error source, a decoder that normalises each image by itself removes it.
- **Evidence (R, P044 4.1, 4.3).** Scratch U-Net on Crack500 crops, 3 seeds: AP at 2 px tolerance 0.8119 (BatchNorm) and 0.8445 (GroupNorm, 8 groups, all 18 layers). The paper does not isolate the cause (3.6.2) and limits its claims to one network and one dataset (6).
- **Evidence (E).** Per-panel BatchNorm adaptation and input intensity normalisation at inference both failed (BRIEF 5): that is against the photometric route for unseen modules, not a test of training with another normaliser. No in-distribution evidence either way until G-BN is read.

### 2.2 Exact change
New file `src/models/norm_swap.py`; one call in `_build_core` for `model.name` in {`smp_unetpp`, `bench_smp`}; key absent = no call.
```
def swap_decoder_norm(model, groups=8):
    n = 0
    for name, mod in list(model.named_modules()):
        if name.startswith("decoder.") and isinstance(mod, nn.BatchNorm2d):
            c = mod.num_features; assert c % groups == 0
            parent, _, leaf = name.rpartition(".")
            setattr(model.get_submodule(parent), leaf, nn.GroupNorm(groups, c))   # weight 1, bias 0, eps 1e-5
            n += 1
    assert n > 0; return n
```
Card `dec_gn_pf_v11.yaml` = `house_r34_unetpp_pf_v11` opts plus `model.decoder_norm.type=groupnorm`, `model.decoder_norm.groups=8`. smp U-Net++ decoder widths are (256, 128, 64, 32, 16), all divisible by 8 (check in the test). The swap draws no random numbers and happens after the build, so decoder convolutions keep PF's initial values for the same seed and the batch stream is unchanged: the contrast is paired by fold x seed. Encoder BatchNorm, the PF parameter groups, loss, data and schedule are untouched. `bench_infer` rebuilds the model from `config_used.yaml`, so the key travels with the run.

**Unit tests** (`tests/test_norm_swap.py`): (1) key absent: 5-step CPU identity IDENTICAL for the PF and house cards; (2) number of swapped modules equals the number of `decoder.*` BatchNorm2d before the swap, encoder BatchNorm count unchanged; (3) the PF encoder group holds the same tensors as without the key; (4) decoder convolution weights at step 0 equal PF's for seed 5; (5) eval output of one image is the same alone and inside a batch of 8; (6) dump and reload through `bench_infer` on 5 cells.

### 2.3 Gate G-BN (free: an existing readout of wave 2a)
The w2a arm `ema_wise_posthoc_pf_v11` writes `raw` (= PF weights) and `raw_bn` (same weights, BatchNorm statistics recomputed on the fold's train images) for every run (E, its card). Contrast `raw_bn` minus `raw`, paired within run, two-stage bootstrap, gaint, seeds 5 and 6.
- **Opens** if the contrast is at least 0.003 in size with its interval off 0 on crack relF1@2, strict crack IoU or mIoU-R13, or at least 0.010 with its interval off 0 on one source with at least 40 cells.
- **Closed** otherwise: running statistics are not an error source in distribution; what is left is the per-sample operator, whose only evidence is one scratch network. My expected top is then about +0.008, below M: the arm is not built (finding Y9) and the paper is parked.

### 2.4 Pathfinder and screen
- Pathfinder: fold 0, seed 5, gaint (1.1 GPU-h): finite loss, step time at most 1.3x PF (GroupNorm runs in fp32 under autocast, S), crack relF1@2 at least PF fold 0 minus 0.05, width ratio 0.6 to 1.6. Never used to rank.
- Screen: cv5v2 x seeds 5, 6 = 10 runs on gaint against the 4-seed gaint PF baseline.
- **Primary:** crack relF1@2, arm minus PF at least 0.010 with the 95% interval above 0, at OP-A and at OP-W inside the width band (0.85 to 1.15 x PF, pooled and per source with at least 40 cells).
- Also printed: arm minus PF `raw_bn` (a gain that `raw_bn` gives for free is not credited to GroupNorm); strict crack IoU; mIoU-R13 at OP-A and against PF at OP-C; inactive region recall, inactive precision and predicted inactive px on inactive-free cells (per-image normalisation meets large dark regions here); U5, F51 and H36 false alarms as secondary reads.

### 2.5 What it should move, drop rule
- Expected (S): crack relF1@2 -0.005 to +0.012; prior 15% for a pass if G-BN opens. Top of the range is just above M, which is why the gate decides the build.
- Drop: primary fails, or a width, false-alarm or inactive count guard fails. A null closes "GroupNorm(8) in the smp U-Net++ decoder over a BatchNorm ResNet-34 under PF"; it does not close GroupNorm encoders or frozen-BatchNorm encoders (P309).
- Fake-gain paths: an operating-point shift (OP-W); a gain that is really recalibrated statistics (`raw_bn` row); a prior shift on inactive or weak classes (OP-C).

### 2.6 Cost, needs
Build 1.5 h (swap 0.5, tests 0.5, card and smoke 0.5). GPU 1.1 + 11. Nothing new to install or download. Track: main.

---

## 3. Arm 3. `t3b_surgical_rules`: two partial-freeze rules inside the T3b rule choice

### 3.1 Hypothesis and evidence
- **Hypothesis (S).** When K labelled cells of a new source arrive, tuning only the block that the shift touches forgets less than tuning everything.
- **Evidence (R, P166 2.1, Table 4, Fig. 2).** Best single block against full fine-tuning on small labelled target sets, 3 seeds: CIFAR-C 82.8 against 79.9, ImageNet-C 51.6 against 50.7; first block best for input-level shifts, last layer for output-level shifts; the edge shrinks with more target data. The paper picks the learning rate and the stopping point on held-out target data; we cannot, so our test is harder on the method.
- **Evidence (E).** T13 arm 3 already fixes the proxy (LOSO-2 roots pass review; E `harness/REVIEW_STAGEB.md`), the draws and the rules R0 (zero-shot), R1 (fine-tune everything with source replay), R1b (target only), R2 (retrain). The LOSO-2 shifts are an input shift (CSIR camera and contrast) and a mixed one (BMRK scale, padding, 3.0 px labels).

### 3.2 Exact change
New key `training.trainable_prefixes` (list of parameter-name prefixes; absent = all), read in `build_optimizer`: other parameters get `requires_grad_(False)` and enter no group; BatchNorm modules with no trainable parameter are put in eval mode at every `model.train()` call so their running statistics stay fixed.
- **R1e (early blocks):** R1's card with `training.trainable_prefixes=[encoder.conv1, encoder.bn1, encoder.layer1]` and `training.encoder_pf.lr_mult=1.0`, so the tuned block gets the run's lr of 1e-4. Under R1's 0.1 multiplier the only trainable block would move at 1e-5 and the rule would be R0 in practice. One learning rate, no sweep.
- **R1d (decoder only):** R1's card with `training.trainable_prefixes=[decoder., segmentation_head.]` and without `training.encoder_pf` (the encoder group would be empty; `build_optimizer` refuses that).
Everything else as R1 (E `T13_fewshot_open_spec.md` 3.2): init from the LOSO-2 base model's `latest.pth`, 2,000 steps, lr 1e-4, warmup 100, cosine, train list = source cells + the K shots repeated, the same proxy split, draws 0 to 4, K in {4, 16}, base seeds 5 and 6.

**Unit tests:** (1) key absent: 5-step CPU identity IDENTICAL; (2) after 10 steps under R1e every tensor outside the three prefixes is bit-equal to the base model, including BatchNorm running statistics; (3) under R1d every `encoder.*` tensor and buffer is bit-equal; (4) a 0-step run equals R0's dump (T13's identity check).

### 3.3 CPU pre-check (mechanism log, 0.5 h)
The paper's relative gradient norm (R 4.1): for each LOSO-2 base model (seed 5) and its K = 16, draw-0 shots, one backward pass of the house loss on CPU; RGN = ||gradient|| / ||parameter|| per tensor, averaged per block (stem, layer1 to layer4, decoder, head). It is printed beside the result and gates nothing. Fixed reading: the paper predicts the highest-RGN block is the one to tune; if that block is not the stem or layer1 for CSIR, R1e is expected to lose to R1.

### 3.4 Screen
- 2 rules x 2 sources x 2 K x 5 draws x 2 seeds = 80 runs of about 0.11 GPU-h = 8.8 GPU-h on gaint, in the same batch as T13 arm 3's runs. Pathfinder: one R1e run (0.11 GPU-h) for test (4).
- **Primary:** pooled score-set crack relF1@2 at OP-A, rule minus R1, K = 16, mean over draws and seeds, two sources averaged (CSIR alone if BMRK fails T13's count check). A surgical rule replaces R1 in T13's decision only if it beats R1 by at least 0.01 with at least 8 of the 10 draw x seed pairs positive in each source used, and its width ratio stays within 0.85 to 1.15 x R0. Otherwise T13's decision stands unchanged.
- Printed beside: K = 4; forgetting (each rule re-scored on the source model's cv5v2 fold-0 held-out cells); false alarms on crack-free score cells.

### 3.5 What it should move, drop rule
- Expected (S): rule minus R1 between -0.02 and +0.02 at K = 16, between 0.00 and +0.03 at K = 4; less forgetting for both rules. Prior 25% that one rule meets the replacement rule. There is no M for this proxy yet (effective n 8.3 and 16.2; E `results/stageB/B3.md`), which is why the rule asks for sign agreement over draws.
- A null closes: "with replay, 2,000 steps, lr 1e-4, K up to 16, tuning only the stem and layer1, or only the decoder, is not better than tuning everything". It does not close other learning rates.
- Fake-gain paths: draw luck (sign rule over 10 pairs); width learned from BMRK shots (width guard); a source shift is not E1's layout and scuff shift (G15: the proxy chooses a rule, it predicts nothing about E1).

### 3.6 Cost, needs
Build 1.5 h (key and BatchNorm handling 0.5, tests 0.5, cards and RGN script 0.5). GPU 0.2 + 8.8. Runs only if T13 arm 3 runs (after its base models; T3b itself only after the registered E1 opening, marked `trained_on_e1`; E PROTOCOL_v0.2 11 item 2). Track: main.
**Not specified:** holding layer3 and layer4 at ImageNet in the main training. The paper has no zero-shot evidence, PF already sits at cosine 0.93 / 0.94, and the transfer claim has no qualified instrument. Reopen if the `encoder_spd` read shows that more preservation helps U1 once LOSO-2 numbers exist.

---

## 4. Arm 4. `trace_crack`: prediction-adaptive reconnection loss on the crack class

### 4.1 Hypothesis and evidence
- **Hypothesis (S).** Where a crack is found in two parts, raising the crack margin at the weakest pixel of the easiest connecting route closes the gap without widening the rest.
- **Evidence (R, P117 Tables 1, 3, 5).** DeepCrack: Dice 82.49 to 84.53 (nnU-Net), 82.78 to 85.20 (CS2-Net); over Skeleton Recall +0.6 and +0.9. DRIVE ladder from Skeleton Recall: +0.2 Dice, Betti error 97.0 to 79.3. Per-image sd about 10 Dice; seeds not stated.
- **Evidence (E).** Skeleton Recall 0.1, the base of TRACE's ladder, failed its replication by an inactive guard and a precision guard (E `log.md` 14 Nov 05:58). On 1 to 2 px labels the published candidate set (target px of the 3x3 window) holds almost no alternative route (S; measured by 4.3 b).
- **BRIEF 5 overlap:** Skeleton Recall (w 1.0 wider; w 0.1 failed), soft clDice (failed). New here: the supervised pixel depends on the prediction.

### 4.2 Exact change
Config `loss.trace: {weight: 0.1, cls: 14, support: band1, protect: [11, 255]}` on the PF card (`loss.supervised=ce_dice` kept). Weight 0.1 = the lowest value of the paper's grid and the weight of `skr01_pf_v11`; no tuning.
- **Aux target** (data worker, through `AuxTargetDataset`; no random draw): `crack_carrier` uint8 (H, W) = skeleton of `mask == 14` by `bench/skel.py` (Zhang-Suen) and `crack_support` uint8 = `mask == 14`, or for `support: band1` its 3x3 dilation minus px labelled 11 or 255. Deviation from the paper: Zhang-Suen instead of the paper's simple-point thinning with isthmus protection (R 3.2). Test: carrier component count equals label component count on 200 pool masks; if more than 1% of masks differ, write the paper's thinning (plus 2 h).
- **Loss** (`src/losses/trace.py`, fp32, autocast off, ignore excluded). z = logits (B, 24, H, W). Reconstructed from the prose of R 3.3 and 3.4, **to be checked against equations 6 to 10 of the PDF before build**:
```
zbar_j = mean of z_j over the carrier px of the batch, for every channel j        # "center each logit channel by its mean over the carrier"
g(x)  = max_{j != 14} relu( (z_j(x) - z_14(x)) - (zbar_j - zbar_14) )            # centred rival-to-target margin; one foreground class here
phi   = increasing, phi(0) = 0, unit slope at 0, finite limit sqrt(2 pi)   (R 3.4; formula not in the tool's text)
for each carrier px v (N of them), 3x3 window nodes 0..8 (centre = 4):
    sup   = crack_support in the window (centre always in)             # candidate set T_v
    ring  = crack_carrier in the window, centre removed
    branches = 8-connected components of ring (fixed 9x9 adjacency A)
    if number of branches < 2:  q_v = phi(g(v))
    else:
        order the sup nodes by detached g, ties by raster index
        for k = 1..9: active = first k nodes; reach = transitive closure of A on active (4 boolean squarings)
                      ok_k = some active node reaches a node of every branch
        x* = the k-th node at the first ok_k                           # bottleneck of the easiest reconnection
        r_v = g(x*) (gathered, not detached)
        q_v = sqrt((phi(g(v))^2 + phi(r_v)^2) / 2)
L_trace = mean of q_v over carrier px ; loss = ce_dice + weight * L_trace ; batches without crack: house loss exactly
```
All of it is tensor code over N x 9 x 9 booleans (N about 5,000 per batch): no Python loop over points.
- **Unit tests** (`tests/test_trace.py`): (1) straight 1 px line, `support: label`: x* = v at every interior point; (2) 2 px wide line with a high g at v and a low g beside it: x* is not v and r_v < g(v); (3) three-branch junction; (4) r_v equals brute force over all subsets of the window on 2,000 random windows; (5) gradient reaches z only at x*, at v and through the carrier means zbar; (6) builders draw no random numbers, batch stream unchanged; (7) key absent: 5-step CPU identity IDENTICAL; (8) no crack in the batch: loss equals the house loss bit for bit.

### 4.3 Gates before any build (all CPU)
- (a) `gap_census` (arm 1): bound_gap >= 0.013. If not, parked.
- (b) Alt-route census on the 532 pool masks (0.5 h, part of the build's first hour): share of carrier points with at least two branches for which a reconnection avoiding v exists inside the label. Fixed reading: under 0.20 means the published support makes the term a pointwise skeleton penalty at more than 80% of points, the family `skr01` already tests; the arm then runs with `support: band1` only. At or above 0.20 it runs with `support: label` (the paper's).
- (c) `skr01_pf_v11` row read on cv5v2 (training on cv02): TRACE is run on the machine that holds that row and is credited only with what it adds over it.
- (d) The three formulas read from the PDF.

### 4.4 Pathfinder and screen
- Pathfinder: fold 0, seed 5. Width gate as the critic set for `clce_crack`: width ratio above 1.25 x PF fold 0 means one retry at weight 0.03, then drop; the gate reads width only. Step time at most 1.3x.
- Screen: 10 runs, cv5v2 x seeds 5, 6.
- **Primary:** crack relR@2 at OP-W, arm minus PF at least 0.013 with the interval above 0 and the frontier read (relR@2 at PF's relP@2) of the same sign; **and** arm minus `skr01_pf_v11` above 0 at OP-W with the interval above 0. Without the second clause the result is "pointwise skeleton supervision", not reconnection.
- Guards beside the section 5 list: component precision and crack-free false alarms (at most 1.5x); relF1@1 and strict IoU; inactive region recall and precision not down by more than 0.02 (the Skeleton Recall route met an inactive guard at three openings); per-source rows and the leave-top-3-groups value (fold 3 holds a third of crack px); `frag` of arm 1 as the mechanism log.

### 4.5 What it should move, drop rule
- Expected (S): relR@2 at OP-W 0.000 to +0.015, never above bound_gap; strict crack IoU -0.005 to +0.005; prior 12% for a pass. The top of the range clears M only if the census says so.
- Drop: any gate; primary fails; width or inactive guard fails. A null closes this term at weight 0.1 with the declared support and carrier. With `skr01` and `clce_crack` also null it would close skeleton-type losses at this weight on PF, not at other weights.
- Fake-gain paths: recall bought with width (OP-W, band); the pointwise half alone (the `skr01` control); a gain carried by a few long CFVS cracks (per-source and leave-top-3); the transfer claim that Skeleton Recall carried on E1 is "untested" here (Y3).

### 4.6 Cost, needs
Build 6 h (aux builders 1, loss 2.5, tests 1.5, card and smoke 1). GPU 1.1 + 11. No code exists to copy (R abstract). Track: main.

---

## 5. Arm 5. `label_version_strata`: recall on stable crack px against px the label revision added (CPU)

### 5.1 Question and evidence
- **Question (S).** Do the models miss the same cracks that the first annotation pass left out?
- **Evidence (E).** The revision joined dotted labels and added segments (+51% crack px on changed train images, 81 train images changed), and re-traced nothing: ring rate r(1) = 0.0054 (handbook `03_datasets_and_splits.md` 3.2; `harness/x2_check/p1/p1.out`). 142 of 234 pool crack cells are unchanged, 90 changed.
- **Evidence (R, P184 3.3).** Pixels where annotators disagree are the hard ones; the paper up-weights them. Here they are used only as a reporting stratum.
- This is not a training arm: the two versions are not two annotators, and training on the old one cost 0.082 crack IoU (family card).

### 5.2 Exact computation
New file `scripts/bench_label_strata.py` (house venv). Inputs: for the 532 pool stems only (assert against `forbidden_v1.txt`, fail closed), `masks_coded` (2021) and the v1.1 strict masks with ignore; PF dumps (W1-G, then W1-C1), HOUSE and the tranche rows for description.
```
g = v1.1 crack & keep ; o = 2021 crack & keep ; d_o = EDT to o ; d_g = EDT to g ; dp = EDT to pred crack
S (stable)  = g & (d_o <= 1)
A (added)   = g & (d_o > 2)            # 1 < d_o <= 2 is a border band, printed, in neither
D (deleted) = o & (d_g > 2)
per stratum X in {S, A}: recall_X = |X & (dp <= 2)| / |X| ; share of X with p_crack < 0.001
false px F = pred crack & (d_g > 2) ; contested share = |F & (EDT to D <= 2)| / |F|
reads: all crack cells; the 90 changed cells only (same cells for S and A); per source; group bootstrap on recall_A - recall_S
```
**Unit tests:** identical versions give A and D empty and recall_S = relR@2 of `bench_score`; a synthetic added segment lands in A; sealed stems raise.

### 5.3 Use (fixed now; no rule, no promotion)
- One table for the label-noise section of the protocol: |S|, |A|, |D|; recall on S and on A with the interval of the difference; contested share of false px. Printed for PF and beside it for every table row once dumps exist. Variants read: 1.
- Reading sentences fixed beforehand: "recall on px the revision added is lower by x [interval]" or "not separated". If recall_A - recall_S is above -0.05, the argument "models miss what annotators miss" is not supported and is not used for the missing-segment arms (`oof_selective_ignore`, `oof_add`).

### 5.4 Cost, needs, risks
Build 1.5 h, CPU minutes. Track: main (pool labels only). Risks: whether the revision was made with model help is not documented (unverified), so A may be biased toward what a model finds; 90 cells, fold 3 heavy, so per-source values are descriptive.

---

## 6. Arm 6. `label_jitter_crack`: random sub-pixel jitter of crack labels only

### 6.1 Hypothesis and evidence
- **Hypothesis (S).** Crack labels sit within about 1 px of the dark ridge. Redrawing each crack label with a new small displacement at every sample stops the network from fitting each cell's fixed offset.
- **Evidence (R, P210 Tables 1 to 4, 7).** Label-only elastic warps, 5 seeds: +0.2 to +0.9 mIoU points on average, on datasets of large objects, with segments of at most 1,000 px exempt because warping them hurts. No thin-structure result.
- **Evidence (E).** Under cross-entropy a jittered label equals a blurred soft target in expectation, which is what `soft_band_jml` trains (w2a, with control `jml_hard`). Offset-tolerant CE was n.d. (10% labels). D0 placement 0.60.
- **BRIEF 5 overlap:** offset-tolerant CE (a loss tolerance); this is a data change.

### 6.2 Exact change
Config `data.label_jitter: {classes: [14], p: 0.5, rms: [0.5, 1.5], sigma: [4, 8], protect: [11, 255]}` on the PF card; key absent = no wrapper. New file `src/data/label_jitter.py`, applied after the label-safe augmentation and before any aux builder:
```
rng = Generator(PCG64(item_seed))                 # the sampler's per-item seed: images and batch order stay PF's
if rng.random() >= p: return mask
sig = rng.choice(sigma); a = rng.uniform(rms[0], rms[1])
dx, dy = gaussian_filter(rng.uniform(-1, 1, (2, H, W)), sig); scale both so that sqrt(mean(dx^2 + dy^2)) = a
yc = (mask == 14); yj = nearest-neighbour remap of yc by (dx, dy)
out = mask.copy()
out[yc & ~yj] = class of the nearest px that is not crack in mask (EDT indices)     # vacated crack px
out[yj & ~yc & ~isin(mask, protect)] = 14                                            # new crack px, never over inactive or ignore
```
Deviation from the paper: the field is set by its RMS displacement in px, not by the paper's (alpha, sigma) grid, whose effective displacement the text does not give; the small-segment exemption is dropped on purpose (it would exempt every crack).
**Unit tests:** key absent: identity IDENTICAL; same item seed gives the same mask; images bit-equal to PF's for the same seed; crack px count ratio 0.9 to 1.1 over 1,000 draws; inactive and ignore px never change; a mask without crack is returned unchanged.

### 6.3 Gate and CPU pre-check
- **Gate:** `soft_band_jml` minus `jml_hard` at least M on strict crack IoU at OP-A and OP-W (the w2a read on gaint). If it fails, this arm is parked: the deterministic expectation of the jitter has then been tested and found flat.
- **P-J** (labels only, 1 h): 2,000 draws on 200 pool crack cells. (i) Mean jittered target on label px and at 1 and 2 px outside, printed beside the soft band's values (1, 0.30, 0.07): if the two profiles differ by less than 0.1 everywhere, say in the card that the arm is the stochastic form of `soft_band_jml`. (ii) Share of crack components under 20 px that lose more than half their px or split in a draw: above 20% means sigma = 8 only; still above 20% means the arm is not run (the paper's own finding on small segments applies).

### 6.4 Screen, expectation, drop rule
- Pathfinder fold 0 seed 5; screen 10 runs on gaint.
- **Primary:** strict crack IoU, arm minus PF at least 0.010 with the interval above 0 at OP-A and OP-W in the width band. Beside it: relF1@1; arm minus `soft_band_jml`; the D0 placement share (expected to rise above 0.65 if the mechanism works).
- Expected (S): -0.010 to +0.008 without the gate's evidence (prior 8%); if the soft band passes with a gain d, 0.5 d to 1.0 d. Top of the range is below M, so the arm exists only behind its gate (Y9).
- A null closes random crack-label jitter of 0.5 to 1.5 px under the house CE + Dice. Fake-gain paths: a width change at argmax (OP-W); lower confidence raising relP@2 (frontier read).
- Not specified: the paper-faithful form (jitter large segments of other classes). Its own average gain is under M for mIoU-R13.

### 6.5 Cost, needs
Build 2 h. GPU 1.1 + 11. Track: main.

---

## 7. Arm 7. `wtconvnext_t_hrstem_unetpp_pf`: a large-receptive-field ConvNeXt row

### 7.1 What the row is
- The C3 control card (HR-stem U-Net++ on ConvNeXt-T ImageNet-1k under PF; `bench_timm`, `model.decoder=unetplusplus`, `model.hr_stem_channels=64`) with `model.backbone=wtconvnext_tiny` and `model.backbone_weights=<WTConvNeXt_tiny_5_300e_ema.pth>`.
- **Evidence (R, P220 Tables 2, 3, 6).** Against ConvNeXt-T: +0.4 top-1, +0.6 mIoU on ADE20K, ImageNet-C error 52.0 against 53.2. Single runs. No thin-structure or defect result.
- At 512 px the stage resolutions are 128, 64, 32, 16, so the levels [5, 4, 3, 2] divide evenly and the first stage's field (160 px at stride 4) covers the cell (S, from R 4.1).

### 7.2 Build
- Vendor `wtconv/` and the WTConvNeXt model file from BGU-CS-VIL/WTConv (MIT) under `bench_vendored` (shared piece S9). The repository pins timm 1.0.7 and PyWavelets 1.6.0 (R, README); gaint has timm 1.0.30 and no PyWavelets (E). So: hard-code the four Haar filters (no install), and test first on CPU that the vendored class builds under timm 1.0.30 and gives the four stage outputs `bench_timm` needs (`forward_intermediates`); if not, wrap its stages (plus 1 h). 1-channel stem by RGB sum, as `build_backbone` does.
- Weights: one Google Drive file linked from the README, ImageNet-1k, md5 pinned at download; the README states no licence for the weights (R). Record it as "ImageNet-1k weights, licence not stated". Whether that passes "clear terms" follows the open ruling on ImageNet weights (E PROTOCOL_v0.2 11 item 7); until then the row is a benchmark row only.
- **Unit tests:** CPU build and forward at 512 px; PF groups (encoder = backbone only); loaded weights md5; stem = RGB sum; card diff against the ConvNeXt-T control = backbone and weights only.

### 7.3 Gate, read, expectation
- **Gate:** the C3 ConvNeXt-T HR-stem control is read first. The row is built only if that control's crack relF1@2 at OP-W is within 0.02 of PF and suite build time is left after tranche 3; otherwise it stays unbuilt and the card says why.
- Pathfinder with the T11 failure gates (step time at most 4x PF: the paper warns about running time, R 5). Screen 10 runs.
- **Read:** a table row with the G16 columns. Printed beside the ConvNeXt-T control (same wrapper): the difference in crack relF1@2 and mIoU-R13. Candidate rule as for every T11 row (against PF). Secondary reads U5 and H36 false alarms; U1 only if the row is non-inferior on CV.
- Expected (S): row minus control 0.000 to +0.006 mIoU-R13, under M (R scale: +0.3 to +0.6 mIoU). It cannot become a candidate through that contrast; it answers "does a near-global field change anything on EL" as a row. Prior 10% that it beats PF on crack.
- The transfer claim (large field helps half-cut layouts) is "untested until the E1 opening" (Y3).

### 7.4 Cost
Build 3.5 h (vendoring and timm check 2, card and tests 1, weights 0.5). GPU 1.5 + 16 (S, from the C3 estimate for ConvNeXt-T). Track: benchmark row.

---

## 8. Ranking against the plan of WAVE3_REVIEW section 4 (S)

No paper earns RUN_NOW as a GPU arm. No card beats what is already planned. In order of value:

1. **`gap_census` (P117), run now.** 1.5 build h, CPU. Place it in stage D7 before `clce_crack`, `scnp_cedice`, `cc_dicece_crack` and `coletra_crack` are built further (together 12 build h and about 49 GPU-h in wave 2b). It displaces nothing. If bound_gap is under 0.013 it saves arm 4 (6 h, 12 GPU-h) and lowers three wave-2 arms.
2. **`dec_gn_pf` (P044), after G-BN.** The gate is free with the w2a read. If it opens: 1.5 h, 12 GPU-h on gaint after the LOSO-2 block, beside `modern_recipe` in stage C4 (the same kind of one-line recipe change), ahead of the six deferred wave-2 crack arms, each of which costs more to build. If it is closed: parked.
3. **`t3b_surgical_rules` (P166), inside stage E1.** Adds 1.5 h and 8.8 GPU-h to `t3b_fewshot_rule`; no separate slot.
4. **`label_version_strata` (P184).** 1.5 h CPU, with the stage E2 reporting work. First item to drop if the 80-hour cut line binds.
5. **`trace_crack` (P117).** Only if arm 1 opens and the `skr01` row shows room; then after `clce_crack` (same family, 2 h against 6 h).
6. **`label_jitter_crack` (P210).** Only if the soft band passes.
7. **`wtconvnext_t_hrstem_unetpp_pf` (P220).** After C3, below `scsegamba` and nnU-Net in the suite order.
8. Parked: P059, P240, P258, P372.

## 9. What the lead must know (S)
1. Two PROMOTE rows were duplicates of carded papers (P059 = T4 rank 35; P258 = P186). The master ledger holds both records of FFPN.
2. Three scout mechanisms do not match their papers (P166 setting, P240 pre-training, P210 small segments); the cards give the sections.
3. TRACE's equations must be read from the PDF before arm 4 is built; the tool returned the prose only.
4. The PADL abstract names a code repository (github.com/Merrical/PADL); earlier cards say "no code found".
5. Licences noted: WTConv code MIT, weights unstated; MEMO code Apache-2.0, weights unstated; SAUGE code MIT, needs SAM checkpoints. None is needed for arms 1 to 6.
6. **Ledger: the ten are still PROMOTE in MASTER.tsv after the refresh (E, run at 17:09 IST).** `make_family_inputs.py` takes the last verdict in file-name order (`v = vs[-1]`), and `T14.tsv` sorts before `T1b.tsv` to `T5b.tsv`, so the sweepers' PROMOTE rows win. It printed: RUN_NOW 44, RUN_AFTER_GATE 57, PROTOCOL 61, PARKED 392, BENCH_ONLY 78, PROMOTE 10, VOID 2; the team column of the ten now reads `T14+T1b` and so on. I changed neither the script nor the sweepers' ledgers (outside my outputs). Tested on a scratch copy only: with line 158 changed to `v = ([x for x in vs if x['status'] != 'PROMOTE'] or vs)[-1]` the same command prints RUN_NOW 44, RUN_AFTER_GATE 61, PROTOCOL 62, PARKED 396, BENCH_ONLY 79, VOID 2, PROMOTE 0, and the ten carry the T14 statuses and arms. The lead decides whether to apply it.
