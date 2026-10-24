# Track D: frozen-encoder probe per source, results (DX, 24 Oct 2026)

Protocol `protocol_probe.md` v1, APPROVED by C (`review_probe_v1.md`); the protocol was written before any probe number.
**Status: awaiting C's independent recompute of the BMRK rule.** Not for the user yet.

**Run:** cv02 GPU 6, tmux `=dxprobe2`, 24 Oct about 11:40-11:46 IST, rc 0. Inference and probe training only.
- First attempt (`=dxprobe`, 11:25) died downloading the ResNet-50 weights (connection reset, rc 1) and wrote nothing.
- The weights were then copied from gaint's torch cache. SHA256s match the torchvision and DINOv2 filenames and are recorded in `meta.json`.

**Files:**
- `results/trackD_probe/`:
  - `hists.npz`: per-cell 1,000-bin crack and inactive pos/neg histograms, test and pool;
  - `percell.json`: argmax counts, relaxed@2 counts, 40-component recall;
  - `meta.json`;
  - `probe.log`;
  - `analysis.txt`, from `scripts/trackD_probe_analysis.py`.
- Probe script `scripts_cv02/trackD_probe.py`, md5 `1cb5b7ad`.

## Checks
- **A5c τ 0 and τ 1** on test reproduce `results/sk1/la_sa_test.json`: crack and inactive IoU and AP, max |diff| 8.3e-6, under the protocol's 1e-4.
- **Pool:** 448 cells, the 7 D7 twins excluded, no val, test or labelled stem (asserted).
- **Probe training:** 23 cells (A5c's 5% set, revised masks).

**What carries the primary (C note 2):**
- **BMRK test:** 10 cells, all with crack, 25,235 crack px.
- **BMRK pool:** 39 cells, 22 with crack, 25,811 px.
- **40 always-missed components:** 17 are BMRK.

## 1. Decision rule: BMRK test crack AP (E)
| Encoder | seed 0 | seed 1 | mean | Δ vs R | Rule | Pool BMRK AP (robustness) |
|---|---|---|---|---|---|---|
| A5c (5 seeds) | | | 0.150 ± 0.017 | | | 0.223 |
| A5c+LA (5 seeds) | | | 0.165 ± 0.018 | R = 0.165, bar 0.215 | | 0.235 (bar 0.285) |
| rn50_random (floor) | 0.045 | 0.047 | 0.046 | −0.119 | not in rule | 0.019 |
| rn34_imagenet (our init) | 0.185 | 0.187 | 0.186 | +0.020 | fail | 0.183 |
| **rn50_imagenet** | 0.268 | 0.268 | **0.268** | **+0.103** | **PASS** | **0.322** (passes bar) |
| **convnext_t** | 0.278 | 0.271 | **0.275** | **+0.109** | **PASS** | 0.280 (below bar 0.285) |
| dinov2_vits14 | 0.122 | 0.133 | 0.128 | −0.038 | fail | 0.159 |
| ref: A5c s0 encoder | 0.171 | 0.171 | 0.171 | +0.006 | not in rule | 0.213 |

**Verdict per the locked rule:** two pretrained encoders pass.
- **ImageNet ResNet-50:** passes on test and on the pool.
- **ImageNet ConvNeXt-T:** passes on test only. Under the protocol's robustness clause that reads "test only, fragile".

**Consequence as pre-stated:**
- the encoder/distillation route stays open, as an input to Track M's backbone ladder;
- MIM pretraining (direction 7) is gated out, because an off-the-shelf encoder already ranks BMRK crack better than A5c.

## 2. What the AP gain is made of (E, exploratory)
Test, crack: AP / argmax IoU / relaxed R@2 / recall at matched precision. The target precision P* is A5c+LA's pixel precision on that source.

| Model | BMRK (P* 0.58) | CFVS (P* 0.59) | CSIR (P* 0.64) | ARTS (P* 0.62) | all (P* 0.59) |
|---|---|---|---|---|---|
| A5c | 0.150 / 0.165 / 0.355 / 0.208 | 0.352 / 0.360 / 0.730 / 0.499 | 0.335 / 0.350 / 0.647 / 0.458 | 0.149 / 0.164 / 0.305 / 0.201 | 0.287 / 0.304 / 0.603 / 0.405 |
| A5c+LA | 0.165 / 0.184 / 0.387 / 0.213 | 0.369 / 0.372 / 0.755 / 0.510 | 0.351 / 0.364 / 0.668 / 0.463 | 0.158 / 0.181 / 0.323 / 0.202 | 0.303 / 0.319 / 0.630 / 0.412 |
| rn50_imagenet | 0.268 / 0.088 / 0.209 / 0.022 | 0.430 / 0.228 / 0.459 / 0.158 | 0.117 / 0.075 / 0.192 / 0.000 | 0.085 / 0.012 / 0.041 / 0.000 | 0.329 / 0.167 / 0.344 / 0.054 |
| convnext_t | 0.275 / 0.035 / 0.092 / 0.002 | 0.456 / 0.224 / 0.442 / 0.225 | 0.161 / 0.017 / 0.045 / 0.018 | 0.031 / 0.012 / 0.032 / 0.000 | 0.357 / 0.148 / 0.284 / 0.127 |

- **The probes' AP gain comes without A5c's precision.** At A5c+LA's precision, both probes recall almost no BMRK crack (0.02 and 0.002, vs 0.21). Their argmax IoU is about half of A5c's.
- So the gain is in **ranking at moderate precision**: the probes give partial scores to BMRK crack that A5c scores near zero. A5c's crack scores are bimodal (C0.5: 57% of GT crack below 0.001).
- **CFVS:** both probes also beat A5c on AP (0.43-0.46 vs 0.35).
- **CSIR and ARTS:** both probes are far worse than A5c.
- **40 always-missed components:**
  - no encoder reaches 0.3 relaxed recall: best is rn50 at argmax, 0.097 px-weighted, 0 of 40 components at ≥ 0.5;
  - A5c gets 0.019;
  - the SYNTHESIS bound (≤ +0.02-0.03 pooled) stands.
- **Inactive AP** (test, descriptive): rn50 0.392 and convnext 0.395, vs A5c 0.253 and the A5c encoder probe 0.386.

## 3. Reading (R)
- Frozen ImageNet ResNet-50 and ConvNeXt-T stride-4/8 features linearly separate BMRK crack better than A5c ranks it after fine-tuning on the same 23 cells.
  - Our init (ResNet-34) does not; its probe is +0.02, inside the bar.
  - A5c's own fine-tuned encoder, probed, also does not (+0.006).
  - So the separation is a property of the larger pretrained encoders, not of fine-tuning, and fine-tuning on 23 cells does not create it.
- The separation is low-precision. It does not by itself say a fine-tuned ResNet-50/ConvNeXt U-Net++ would raise BMRK IoU or recall at a usable threshold.
  - It is evidence that the backbone, not only coverage, limits BMRK.
  - That is Track M's step (backbone ladder), now with a per-source prior: watch BMRK AP and recall, and CSIR/ARTS, where the probes are weak.
- For Track D's own question: the labelled-set experiment stays as designed. Ts tests whether BMRK coverage moves BMRK. This probe says the encoder is a second lever on BMRK.

## 4. Notes required by C
1. **DINOv2 runs at stride ~14** (37 × 37 tokens at 518 px). Its fail on 1-3 px cracks is partly a resolution artefact, not evidence that DINOv2 features lack crack information.
2. **Primary sample:** BMRK test is 10 cells, all with crack (25,235 px). The pool check adds 39 BMRK cells (22 with crack). 17 of the 40 components are BMRK.
3. **Limit:**
   - A probe's AP is not a fine-tuned model's AP.
   - A pass shows that frozen linear features rank BMRK crack better than the fine-tuned A5c. It does not show that a fine-tuned stronger backbone would score higher on IoU or recall.
   - A fail would not have shown the opposite either.

## 5. Other limits
- 2 probe seeds.
- One labelled draw (23 cells, 2 BMRK crack cells).
- Linear head on stride-4/8 features: no stride-2 features.
- AP is dataset-level per source, so a few large BMRK cells weigh most.
- ConvNeXt fails the pool check.
