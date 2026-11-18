# Frontier team brief (12 Nov 2026)

Read this whole file before doing anything. It is the only project context you are guaranteed to have.
Deeper context, if you need it: `~/mtp/research/handbook/` (00 = entry, 03 = data, 11 = claims table, 18 to 22 = latest work).

## 1. The goal, in the user's words
"highest scores, a model which captures almost all of the cracks, inactive and other important defects balancing the miou for other classes as well."

- Deadline: about 12 Dec 2026 (one month). MTP thesis, IIT Mandi, with WattCycle (PV recycling / inspection startup).
- The mentor's instruction: use recently published work (roughly 2020 to 2026) and try it, adapted to this project, not copied.
- **The benchmark vision (the user, 12 Nov 2026):** "set a benchmark for this very unorganised field". Published EL segmentation numbers cannot be compared with each other (different releases and splits of the same data, leakage between train and test, different class lists and metrics, strict IoU on 1 to 2 px labels). The user first meant to beat older models, found those numbers are not comparable, and now wants a new, trustworthy benchmark: clean splits, a fixed protocol, metrics that fit thin noisy labels, an unseen-module test, and many recent methods run under that one protocol. Further steps such as post-evaluation and severity detection (crack mode, inactive area fraction, power-loss band) are wanted only if they add real value. So a paper is useful in two ways: it can raise the scores, or it belongs in the benchmark's method suite or shapes how the benchmark is built and scored.
- Earlier work was framed as semi-supervised learning. That framing is dropped. Any route to a better model is in scope: data, labels, architecture, loss, pretraining, foundation models, generative data, other modalities (thermal IR, PL, UVF), evaluation.
- Past experiments are context, not walls. A past null closes only the exact thing that was run, under the conditions it was run (section 5). Do not dismiss a paper because something with a similar name failed here. Do not re-propose the identical run either.

## 2. The task
Pixel-level semantic segmentation of electroluminescence (EL) images of silicon solar cells. Grayscale, 512 x 512, one cell plus fragments of neighbours per image.

| Item | Fact |
|---|---|
| Main labelled set | BenchmarkEL `dataset_20211104` (Pratt et al.): 582 cells = 478 train / 54 val / 50 test, 24 classes (12 structural "features", 12 defects) |
| Labels in use | "Revised" masks = BenchmarkEL `20221008` crack / inactive corrections (redistributed by E-SCDD, Hanifi et al. 2025) |
| Focus classes | crack (id 14): 0.19% of train pixels, in 209 of 478 train cells. inactive (id 11): in 42 of 478 train cells |
| Sources | 5 image sources with different contrast and label conventions: ARTS 195, CFVS 187, CSIR 122, BMRK 60 (= ELPV cells, downscaled and padded), SDLE 18 |
| Test set | 50 hand-picked cells, 48 with crack, 16 with inactive; 3 cells hold 59% of inactive pixels. One very noisy cell (`CSIR_00070_r8_c4`) wrecks about 1 run in 6 unless excluded ("clean" = 49 cells) |
| Unseen-module set E1 | 106 cells from 67 modules never seen in training (101 CSIR, 5 BMRK), 32 with crack, 10 with inactive. 58 of them are half-cut cells, many with long dark "scuff" streaks. Training has 0 half-cut cells |
| Extra labelled real cells | E-SCDD adds 117 newly annotated cells (`_rf`): 51 full cells (F51) and 36 half-cells (H36) are used as validation only; H36 crack labels are speck-level and unreliable |
| Unlabelled pool | 11,938 CSIR / ARTS cells on the servers (6,163 mono, 4,623 multi, 1,152 multi half-cells). The full pool is about 159k cells (Pratt's Dropbox; HF `sasan/scdd-unlabeled`), same two sources |
| Second labelled dataset | UCF-EL (Fioresi 2022): 9,562 train / 2,289 test cells, polygon masks, classes crack (a region class, about crack + inactive), contact, interconnect, corrosion. Heavy train/test leakage |
| Other public EL data, unused | ELPV (2,624 cells, image-level defect probability), PVEL-AD (36,543 NIR cells, boxes, by request), MultiSolSegment (585, multi-label), PV-Vision / LBNL crack sets, PVEL-S (1,200 binary masks), BenchmarkEL `20220723` / `20221008` (642 / 695 cells, reshuffled splits) |
| Thermal / other modalities | 3 public sets pair EL and IR on the same modules at module level, no masks (UCF OSF `csr6t`, `ar76v`; DTU drone IR, 43 modules). On disk: `~/mtp/datasets/thermal_public/`. WattCycle owns a drone thermal camera; its EL rig is months away |

### What a crack label is (this matters for every crack method)
- The physical crack is micrometres wide. The camera shows a dark line about 4 px wide (FWHM). Annotators traced a 1 to 2 px line (median 1.75 px) somewhere on it.
- Half of label points sit more than 1 px from the darkest ridge. Label width depends on the source: ARTS 1.5 px, CFVS / CSIR 1.75, BMRK 3.0, SDLE 3.25.
- A perfect mask shifted by 1 px scores crack IoU 0.56 on test (0.43 if shifted diagonally). Two annotations of the same cell agree at IoU 0.21 to 0.26 (0.82 to 0.99 within 2 px).
- 70% of the best model's crack IoU loss lies within 2 px of ground truth. So strict crack IoU near 0.5 is close to a labelling ceiling unless the model learns each source's labelling convention or the labels are improved.
- Inactive is the opposite: blobby, well labelled (1 px shift IoU 0.94), but rare. It never occurs without a crack; 99% of inactive regions touch a crack label. 20% of train crack pixels lie in or at inactive regions (single-label argmax must pick one).
- 76 to 88% of crack components are under 20 px. 7% are less than 2% darker than their surroundings.

## 3. Where the scores stand (the numbers to beat)

House model: U-Net++ (segmentation_models_pytorch), ImageNet ResNet-34 encoder, 1-channel input, 512 px, batch 8, Adam lr 1e-3 (200-step warmup, cosine), weight decay 1e-4, 20,000 steps, CE + soft Dice on crack and inactive, "label-safe" augmentation (flips, rot90, brightness / contrast only), bf16. About 1.1 GPU-h per run on an RTX A6000, 6 to 7 GB.
"PF" variant (encoder-preserving fine-tune): encoder frozen for 1k steps, then 0.1x lr, no encoder weight decay.

| Set | Metric | Single model (5-seed mean) | Best ensemble (5 seeds) |
|---|---|---|---|
| test, clean 49 | crack IoU | 0.474 | 0.492 (with a val-chosen crack logit bias; 0.485 to 0.488 at argmax) |
| test, clean 49 | crack relaxed F1 at 2 px (relF1@2) | 0.881 | 0.897 (relP@2 0.930, relR@2 0.866) |
| test, clean 49 | crack pixel P / R | 0.644 / 0.642 | 0.621 / 0.703 |
| test, clean 49 | crack components >= 20 px found | 0.798 | 0.834 |
| test, clean 49 | inactive IoU | 0.449 | 0.456 |
| test, clean 49 | mIoU over the 13 classes with ground truth in >= 3 test cells (mIoU_rob) | 0.580 | 0.583 |
| E1 unseen modules | crack IoU / recall | 0.15 / 0.17 to 0.21 | 0.172 / 0.215 |
| E1 unseen modules | crack relF1@2 | about 0.41 to 0.43 | about 0.43 to 0.47 |
| E1 unseen modules | inactive IoU | 0.05 (house), 0.24 (PF) | 0.28 (PF ensemble) |

"Almost all cracks" target set earlier: relR@2 >= 0.90 at relP@2 >= 0.90. Not reached (0.866 at 0.930).

Per-class test IoU of the house model (clean 49): background 0.926, sp_multi 0.803, sp_mono 0.740, ribbons 0.647, border 0.692, padding 0.994, inactive 0.449, material 0.411, crack 0.474, **gridline 0.283 (recall 0.33)**, **splice 0.000 (never predicted)**, edge_dark 0.306, frame_edge 0.817, busbars 0.420 (1 cell), corrosion 0.755 (1 cell).
Weak sources at 100% labels: BMRK (crack 0.379, inactive 0.324), CFVS cells without a train twin (crack 0.397), CSIR.
On E1, 70% of ground-truth crack pixels get p(crack) < 0.001 (the model does not see them at all). 75% of E1 crack pixels sit in 20 half-cut cells with scuff streaks (recall 0.13 there).

## 4. The five problems, stated plainly
1. **Crack, in-distribution:** noise-limited. Thin, jittered, source-dependent labels cap strict IoU. Detection within 2 px is already 0.88 to 0.90 F1.
2. **Inactive:** data-limited. 42 training cells. Recall 0.61, precision 0.63. BMRK is the weak source.
3. **Unseen modules (E1):** context-limited. New cell layout (half-cut), new confounder (scuff), crack IoU falls from 0.47 to 0.15.
4. **Other classes:** gridline, splice, edge_dark, material are weak; they drag all-class mIoU.
5. **Measurement:** 50 test cells. The smallest detectable crack IoU change is about 0.012 with 5 v 5 seeds; inactive is decided by 3 cells. A method needs a real effect, or a better instrument (for example module-grouped 5-fold CV over the 532 train + val cells, which already exists as fold roots).

## 5. What was already run, and under what conditions
Everything below used the house model (U-Net++ / ResNet-34, 512 px, Adam 1e-3, 20k steps) unless stated. "n.d." = no detectable difference under a pre-registered seed rule.

| Line | What was run | Outcome | What it does NOT close |
|---|---|---|---|
| Pseudo-label SSL (Mean Teacher, hard / tolerant pseudo-labels, CutMix, separate BN) | 5 to 100% labels, in-domain and 11.9k external pool | helps at 5% (inactive +0.11), n.d. from 20% up, n.d. at 100% with the external pool | SSL with foundation-model teachers; UDA-style methods aimed at E1 with target-like data; SSL on other architectures |
| ALHVR, SKCDF-style heads, CPS | 5% labels | worse / n.d. | |
| Pool feature learning: MIM pretraining, DDeP (decoder denoising) | ResNet-34, 11.9k pool, then fine-tune (also with PF at 100%) | n.d. | other SSL objectives, larger pool (159k), ViT / ConvNeXt backbones, dense or thin-structure-aware objectives |
| UCF-EL supervised pretraining of the encoder | house fine-tune (which erased the encoder) | n.d. / worse | joint multi-dataset training; pretraining kept by the fine-tune |
| Foundation encoders | frozen linear probes (DINOv3 ViT-S and ConvNeXt-T, DINOv2-S, SAM2 Hiera-T) and one fine-tune screen: DINOv3 ConvNeXt-T vs ImageNet ConvNeXt-T under PF, 2 seeds, 4k steps, judged on F51 crack AP (76% one cell) | no sign of a gain | large ViT backbones (ViT-L and up), adapters / LoRA / Rein, SAM or SAM2 / SAM3 fine-tuning, mask decoders, higher resolution, longer schedules |
| Backbone | ResNet-50 (house and PF) | worse on inactive | everything that is not ResNet-34 / 50 U-Net++ |
| Resolution | 2x input | n.d. at 4x compute | native-resolution crops (sources are 1200 px for part of the pool), super-resolution heads |
| Loss | Dice on 12 classes (worse), Dice on 3 (n.d.), soft clDice (fail), Skeleton Recall w 1.0 (wider predictions, test IoU worse, E1 detection up), Skeleton Recall w 0.1 (narrow pass on E1 relF1@2; fresh-seed replication trained, not scored), offset-tolerant CE (n.d.) | | Lovasz / Jaccard metric losses, soft-label losses, focal / Tversky families, boundary and distance losses, long-tail losses, component-wise losses, topology losses beyond clDice |
| Optimizer / fine-tune | found: the house fine-tune erases ResNet layer3 / layer4 (cosine to init about 0). PF keeps them: test n.d. to narrow gain on relF1@2, E1 inactive 0.05 -> 0.24 | | AdamW, layer-wise lr decay, SAM optimizer, EMA / SWA, longer schedules; never varied |
| Data | +107 E-SCDD cells (n.d.), crack copy-paste onto pool cells (n.d., more decoys), synthetic half-cut views (n.d. on test / E1, fewer half-cut false alarms), scuff as its own class (649 px, not learned) | | generative synthesis, physics-based synthesis, multi-dataset training (UCF-EL, MultiSolSegment, PVEL-AD boxes, ELPV image labels), relabelling / label refinement |
| Inference | 5-seed ensemble (+0.014 to +0.018 crack IoU, the only clear win), logit bias, per-panel BN adaptation (fail), intensity normalisation (fail), per-module thresholds (fail) | | flip / rot / multi-scale TTA, heterogeneous ensembles, distillation, learned refinement stages |
| Labels | label version matters more than any method (+0.05 to +0.08 crack IoU from the 2022 relabelling). An audit flagged crack label issues in 24 of 239 train cells; nothing was fixed | | automatic label refinement, noise-robust training, annotator / source-style modelling |
| Thermal | desk study only: thermal sees inactive / disconnected area and hot spots, not thin cracks. Dark forward-bias IR on public pairs is row-level, not cell-level. Sunlit drone IR arm not read | | everything experimental |

Never tried at all (as of today): any transformer or Mamba segmenter, mask-classification decoders, multi-label heads, edge-detection or centerline-regression formulations, snake / deformable convolutions, refinement networks, diffusion or GAN data synthesis, physics simulation of EL, anomaly-detection priors, noisy-label methods, source-conditional prediction, model distillation, long-tail segmentation losses, cross-dataset joint training, k-fold cross-validated selection, nnU-Net style auto-configuration.

## 6. Resources
- **gaint:** 1x RTX PRO 4500 (32 GB), shared with other processes; code at `/home/noob/work/el-fault-detection` plus worktrees; all checkpoints.
- **cv02:** 8x RTX A6000 (48 GB each), shared lab machine, `/tmp/noob_el` (wiped on reboot).
- Compute budget: no limit; the instruction is to use the GPUs fully. Time budget: one month.
- No manual labelling by the user unless a case is made that it is truly needed (then minimal).
- Public code and weights may be used. Gated downloads need the user's OK.

## 7. Rules for every agent on this team
1. **Sources.** Cite only papers you actually retrieved through a tool (Research MCP or a fetched page), with their ids (doi / arXiv). Never invent a reference, a number or a repo URL. If you cannot verify something, write "unverified".
2. **Research MCP.** Load its tools with ToolSearch (`select:mcp__claude_ai_Research_MCP__search_papers,mcp__claude_ai_Research_MCP__search_snippets,mcp__claude_ai_Research_MCP__get_paper,mcp__claude_ai_Research_MCP__similar_papers,mcp__claude_ai_Research_MCP__get_citations,mcp__claude_ai_Research_MCP__get_references,mcp__claude_ai_Research_MCP__fetch_fulltext,mcp__claude_ai_Research_MCP__read_paper`). Run many short queries rather than one long one. The laptop is off campus right now: publisher (IEEE / Elsevier) full text will fail, so use `fetch_fulltext` only for arXiv / open-access copies, and at most 3 per agent in the discovery phase. `search_snippets` works without downloads. If a call is rate-limited, wait and retry; do not hammer.
3. **Recency.** Your training data may be stale. Search explicitly for 2025 and 2026 work (use `year_from`), and use WebSearch (load with ToolSearch `select:WebSearch`) for very recent papers and for code repositories.
4. **No servers, no GPUs, no test data** in the literature phases. Do not ssh anywhere. Do not read test or E1 predictions.
5. **No installs, no pattern kills.** No pip / venv / npm installs. Never use `pkill -f` / `killall`.
6. **Write to disk as you go**, in the folder you are given, so work survives a dropped connection.
7. **Style.** Terse, plain English, no em-dashes, no buzzwords. Measurements over adjectives. Separate what a paper measured (R), what our files measured (E), and your judgement (S).
8. **Adapt, do not copy.** For each paper say exactly how it would be changed for this data: 1-channel EL, 512 px, 478 labelled cells, 1 to 2 px crack labels with jitter, 24 classes, the 5 sources, the E1 gap.
9. **A hypothesis is closed only by evidence.** "Probably will not help" is not a verdict. Either point to a run in section 5 that tested the same mechanism under the same conditions, or design the cheapest experiment that would decide it.
