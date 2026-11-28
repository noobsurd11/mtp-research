# D24: Vision foundation backbones with parameter-efficient tuning for dense prediction (low-data)

Scout: D24 literature agent. First pass 12 Nov 2026 (cut short by a Research MCP outage), completed 13 Nov 2026.
Labels: R = what the paper reports (tool output or full text read), E = what our files measured (BRIEF), S = my judgement.
Every id below came from a Research MCP result in this or the 12 Nov session. "unverified" = not confirmed by a tool.

## 1. Queries run

12 Nov (partial, see old status): search_papers "Rein vision foundation model domain generalized semantic segmentation", "DINOv3 dense prediction fine-tuning", "LoRA DINOv2 medical image segmentation few labels", "foundation model industrial defect segmentation crack"; 3 web searches (DINOv3 family, Rein repo, SAM2-UNet repo).

13 Nov (OpenAlex and arXiv answered; Scopus / ScienceDirect HTTP 401; Semantic Scholar rate-limited all session, so all 3 search_snippets calls failed):
1. DINOv3 dense prediction fine-tuning (2025+)
2. Rein vision foundation model domain generalized semantic segmentation (2023+)
3. SAM adapter fine-tuning thin structure segmentation vessel crack (2023+)
4. feature upsampling vision foundation model frozen ViT high resolution dense features (2024+)
5. RADIO agglomerative vision foundation model dense segmentation (2024+)
6. Perception Encoder spatial features dense prediction (2025+)
7. LoRA DINOv2 medical image segmentation limited data (2024+)
8. linear probing then fine-tuning layer-wise learning rate decay feature distortion segmentation (2021+)
9. parameter-efficient fine-tuning VFM semantic segmentation benchmark adapters LoRA comparison (2024+)
10. foundation model industrial surface defect segmentation DINOv2 SAM fine-tuning (2024+)
11. frozen DINOv2 backbone lightweight decoder segmentation few hundred training images (2024+)
12. ViT-Split efficient adaptation VFM frozen layers prior head (2025+)
13. electroluminescence solar cell defect segmentation foundation model SAM DINOv2 (2023+): 3 hits, none on EL
14. SigLIP 2 dense features semantic segmentation localization (2025+)
15. SAM3 fine-tuning semantic segmentation medical industrial (2025+)
16. Dino U-Net high-fidelity dense features foundation model medical segmentation adapter (2025+)
17. low-rank adaptation versus full fine-tuning ViT segmentation small dataset domain shift (2024+)
18. domain generalized semantic segmentation DINOv3 parameter-efficient tokens (2025+)
19. VFM teacher distillation unlabeled images compact segmentation student domain shift (2024+)
20-22. search_snippets (DINOv3 scaling in medical; Rein vs LoRA DG medical; how to benchmark VFMs): all failed, S2 rate limit
Snowball: get_citations on Rein (doi:10.1109/cvpr52733.2024.02704, 30 of 182) and ExPLoRA (arxiv:2406.10973); similar_papers on DINOv3-PEFT SAR + DINOv3-vs-ImageNet industrial + SegDINO.
Full text read: arxiv:2605.23472 (DINOv3 vs ImageNet, industrial; sections 4.2, 4.3, 5.1, 5.3, 6) and arxiv:2409.07960 (VFMs and DG in medical seg; datasets, PEFT tables, conclusion).
WebSearch: SegDINO repo; RADIO / C-RADIOv4 numbers and repo; Perception Encoder repo; Rein repo; ExPLoRA code.

## 2. What is closed and what is not (E)
- Closed: frozen linear probes (DINOv3 ViT-S, ConvNeXt-T, DINOv2-S, SAM2 Hiera-T); A8 = DINOv3 ConvNeXt-T vs ImageNet ConvNeXt-T under PF, 2 seeds, 4k steps, judged on F51 crack AP.
- R that weakens what those nulls mean: Kerssies et al. (row 16) report that linear probing does not predict end-to-end fine-tune ranking for segmentation. Gharbage et al. (row 4) find DINOv3 ConvNeXt-T equal to ImageNet ConvNeXt-T when frozen but +10.3 mIoU after full fine-tuning on a long Mask2Former schedule. So our probe nulls and a 4k-step PF screen say little about long-schedule fine-tunes or PEFT on ViT-L.
- Open: ViT-L and larger; Rein / LoRA / adapters; 20k-step schedules; any VFM judged on E1; domain-adaptive continued pretraining of a VFM on the EL pool; VFM teachers for distillation; SAM3 and C-RADIOv4 encoders.
- Constraint (E, idea08 stride analysis): at stride 16 on 512 px input, 70.7% of crack signal is diluted below 1/4. Every ViT arm needs a stride-2/4 detail path. The house encoder is the obvious one.

## 3. Shared harness (S)
"VFM-H" = house U-Net++ R34 under PF (keeps the crack detail path and every known recipe) + a VFM side branch whose features are projected and added at the stride-16 and stride-32 decoder inputs. The only change between baseline and arm is the side branch. VFM input: EL grey replicated to 3 channels, ImageNet normalisation, 1024 px (2x upsample; 64 x 64 tokens at patch 16). 20k steps, house loss and augmentation, bf16. Estimate 10 to 20 GPU-h per run on an A6000 for a ViT-L with backprop through frozen weights (Rein / LoRA), unverified until timed.
Instrument: module-grouped 5-fold CV over 532 train + val cells (fold roots exist), 1 seed per fold, then 3 seeds on clean-49 and one pre-registered E1 opening.
Default kill line: CV crack relF1@2 more than 0.005 below house PF AND E1 crack relF1@2 not at least +0.03 over house PF (about 0.42) AND E1 inactive IoU not above 0.24 (house PF).
Why the side-branch design: R from row 1 says VFMs match CNNs in-domain and win under domain shift. Our in-domain crack is label-noise limited, our E1 is context limited. A side branch can only add context; it cannot erase the house's crack skill.

## 4. Selected papers

| # | id | year | venue | code | mechanism | adaptation to our data | score | bench |
|---|---|---|---|---|---|---|---|---|
| 1 | doi:10.1007/978-3-031-91672-4_12 (arXiv 2409.07960) VFMs and DG in medical seg | 2025 | LNCS | github.com/kerem-cekmeceli/Foundation-Models-for-Medical-Imagery (in abstract) | Frozen VFM + Rein-LoRA + strong decoder. R: in-domain Dice equal to U-Nets, DG much better (lumbar spine DG 31 to 41 vs 1 to 6 for U-Nets; brain 52 to 55 vs 44), training sets of 10 to 198 greyscale MRI/CT volumes; larger VFMs help DG slightly, not ID | VFM-H with DINOv2-L (Apache) + Rein-LoRA side branch. Target is E1 (problem 3), not in-domain crack. Sources as domains: also run leave-one-source-out (train 4, test BMRK) as a cheap DG probe | 68 | 65 |
| 2 | doi:10.1109/cvpr52733.2024.02704 (arXiv 2312.04265) Rein | 2024 | CVPR | github.com/w1oves/Rein (web-verified) | Learnable tokens refine each layer's features of a frozen VFM, under 1% params; beat full fine-tune on unseen domains | Same harness, Rein in place of Rein-LoRA. Repo has DINOv2 / ConvNeXt / CLIP / SAM configs (mmseg); port only the token module into our trainer | 62 | 75 |
| 3 | doi:10.1109/tpami.2026.3681631 (arXiv 2508.01667) Rein++ | 2026 | TPAMI | paper says github.com/wloves/Rein; web shows w1oves/Rein; Rein++ code unverified | Rein-G (instance-aware tokens) for DG, then Rein-A: unsupervised adaptation at instance and logit level, plus a SAM-based boundary transfer on the target | Rein-G on the 5 labelled sources; Rein-A on unlabelled pool cells that resemble E1 (1,152 multi half-cells, CSIR), never E1 itself. Drop the SAM boundary module for cracks (SAM masks do not follow 1 px lines) | 58 | 60 |
| 4 | arxiv:2605.23472 DINOv3 vs ImageNet for industrial inspection | 2026 | arXiv | none found | Controlled study. R: frozen DINOv3 ConvNeXt-T = ImageNet ConvNeXt-T (62.4 vs 62.0 mIoU Severstal); full fine-tune DINOv3 +10.3 mIoU over ImageNet ConvNeXt-T and +10.6 over R50 (Mask2Former default schedule). But on greyscale X-ray, ImageNet wins frozen (21.3 vs 7.9 AP50) and fine-tuned (29.7 vs 27.8) | Rerun A8 properly: DINOv3 ConvNeXt-S/B in smp U-Net++ (stride-2 stem added), full fine-tune (not PF), 20k steps, vs ImageNet ConvNeXt of the same size. EL is greyscale like X-ray, so expect no gain in-domain; the test is cheap and closes the question | 50 | 70 |
| 5 | arxiv:2406.10973 ExPLoRA | 2024/2025 | ICML 2025 (PMLR 267, web) | project page samar-khanna.github.io/ExPLoRA (in abstract); repo unverified | Continue the VFM's own SSL objective (DINOv2) on unlabelled target-domain images, unfreezing 1 to 2 blocks and LoRA on the rest; then LoRA fine-tune. R: SOTA on satellite, up to +8% linear-probe top-1 | DINOv2-L (or DINOv3-L) continued DINO pretraining on the 11.9k server pool, 1,152 multi half-cells included; then VFM-H. Moonshot for E1: the encoder sees half-cut and scuff cells before supervision. Not the same as our MIM / DDeP on ResNet-34 | 55 | 40 |
| 6 | arxiv:2509.02379 MedDINOv3 | 2025 | arXiv | github.com/ricklisz/MedDINOv3 (in abstract) | Plain ViT with multi-scale token aggregation + domain-adaptive DINOv3 pretraining in stages on 3.87M CT slices | Two parts: (a) multi-scale token aggregation as the VFM-H fusion design; (b) domain-adaptive pretraining on the 159k pool (HF sasan/scdd-unlabeled) if ExPLoRA (row 5) shows any E1 sign. 159k is 4% of their 3.87M, so use the ExPLoRA budget form | 48 | 55 |
| 7 | arxiv:2508.20909 Dino U-Net | 2026 | LNCS (MICCAI-series) | github.com/yifangao112/DinoUNet (in abstract) | Frozen DINOv3 + adapter that fuses semantic features with low-level spatial detail + fidelity-aware projection; R: SOTA on 7 medical sets, accuracy rises with backbone size up to 7B | Closest ready-made VFM-H. Run as a stand-alone benchmark arm and as the source of the projection module. Overlaps D14 | 58 | 70 |
| 8 | doi:10.3390/rs18070973 DINOv3-PEFT (SAR roads) | 2026 | Remote Sensing | unverified | Dual encoder: adapter-tuned frozen DINOv3 for context + CNN branch for thin elongated detail, fused hierarchically. R: GF-3 SAR roads 82.6 F1, 76.5 IoU averaged over 4 resolutions | Closest domain: thin lines in noisy greyscale. Its CNN branch = our house R34; its fusion module is a candidate for VFM-H. Code unverified, so implement from paper | 55 | 40 |
| 9 | arxiv:2408.08870 SAM2-UNet | 2024/2026 | Visual Intelligence | github.com/WZH0120/SAM2-UNet (web-verified 12 Nov) | Frozen SAM2 Hiera + adapters before each stage + U-Net decoder | Hiera is hierarchical (stride 4), so no stride problem. Hiera-B+ / L at 512 and 1024 px, add stride-2 skip from the image. Linear probe of Hiera-T was null; adapters + Hiera-L untested. Overlaps D14 #1 | 60 | 85 |
| 10 | arxiv:2511.19425 SAM3-Adapter | 2025 | arXiv | "available" per abstract, URL unverified | Adapter prompts injected into the frozen SAM3 encoder for low-level tasks (medical, camouflage, shadow); R: beats SAM and SAM2 adapters | SAM3 encoder at 1008 px with adapters + U-Net decoder + house R34 detail path. Licence and gated weights need the user's OK | 45 | 60 |
| 11 | arxiv:2601.17237 C-RADIOv4 | 2026 | arXiv tech report | NVlabs/RADIO via torch.hub (web) | Agglomerative ViT distilled from SigLIP2, DINOv3 and SAM3; any-resolution; ViTDet windowed mode for high resolution; permissive licence. Web: ADE20k linear probe 55.2 / 57.0 at 512 / 1024 px (unverified from paper) | Backbone swap in VFM-H, no gated download. ViTDet mode makes 1024 px cheap. SO400M first | 52 | 60 |
| 12 | arxiv:2509.00833 SegDINO | 2025 | arXiv | github.com/script-Yang/SegDINO (web-verified, in arXiv) | Frozen DINOv3, multi-level features aligned to one resolution, MLP head | Benchmark baseline only: "frozen VFM + light head". Expect poor crack IoU at stride 16; report it to show why detail paths matter | 25 | 70 |
| 13 | doi:10.1016/j.knosys.2026.115713 (arXiv 2503.06976) Task-specific KD | 2026 | Knowledge-Based Systems | unverified | LoRA-fine-tune the VFM on the task, then distil into a small net on a transfer set (+ diffusion images). R: KidneyUS +28% Dice over task-agnostic KD with 80 labels | If a VFM-H arm wins on E1, distil it into house U-Net++ R34 using the 11.9k pool as transfer set (soft logits). Distillation never tried here | 45 | 45 |
| 14 | arxiv:2603.02554 GKD | 2026 | arXiv | github.com/Younger-hua/GKD ("will be available") | Two-stage KD for DG: student learns domain-agnostic features from the VFM by query-based selective feature distillation, then frozen for task training. R: +10.6% foundation-to-local over other KD on 5 DG benchmarks | Student = house R34 encoder; stage 1 feature distillation from DINOv2-L / C-RADIOv4 on the 11.9k pool; stage 2 house training with the encoder frozen then PF. Aims at E1 | 45 | 40 |
| 15 | doi:10.1109/tpami.2025.3528453 (arXiv 2410.10777) UniMatch V2 | 2025 | TPAMI | github.com/LiheYoung/UniMatch-V2 (in abstract) | Weak-to-strong consistency SSL on a DINOv2 encoder; R: encoder swap from ResNet to DINOv2 gives more than method design | SSL n.d. at 100% only for ResNet-34 U-Net++. Run VFM-H as student, 478 labelled + 11.9k pool. Also a must-have SSL baseline for the benchmark | 40 | 75 |
| 16 | doi:10.1109/cvprw63382.2024.00123 (arXiv 2404.12172) How to benchmark VFMs for seg | 2024 | CVPRW | tue-mps.github.io/benchmark-vfm-ss (in abstract) | R: ViT-B, patch 16, linear decoder ranks VFMs like larger settings at 13x less cost; linear probing does not predict fine-tune ranking; rankings change across datasets and domain shift | Two uses: (a) our linear-probe nulls do not close fine-tune arms; (b) benchmark protocol for the VFM part of the EL suite, with the caveat that thin cracks need a detail path, so "linear decoder" must be tested, not assumed | 30 | 80 |
| 17 | arxiv:2508.10104 DINOv3 | 2025/2026 | TMLR | HF facebook/dinov3-* (web-verified 12 Nov, gated) | Gram anchoring keeps dense features clean at scale; distilled ViT-S to H+ and ConvNeXt T to L | Default VFM for rows 2, 4, 7, 8. ViT-L/16 at 1024 px. Gated: needs the user's OK; DINOv2-L (Apache) and C-RADIOv4 are fallbacks | 45 | 80 |
| 18 | doi:10.1088/1361-6560/aeb29f Domain-aligned DINOv3 (PET/CT) | 2026 | Phys Med Biol | none | Evidence: with frozen encoders in nnU-Net, natural-image DINOv3 did not beat random init on PET/CT; CT-pretrained DINOv3 was best; domain proximity and scale both matter | Warns that natural-image DINOv3 may not transfer to EL, and supports row 5 (continued pretraining on EL) over more natural-image scale | 30 | 40 |

## 5. Minimum experiments (S)
All on VFM-H unless stated; baseline = house PF; instrument and default kill line from section 3.
1. Rein-LoRA side branch, DINOv2-L (row 1). Arm vs house PF. Metric: E1 crack relF1@2, E1 inactive IoU, CV crack relF1@2, leave-BMRK-out crack IoU. Kill: default. About 5 folds x 15 GPU-h + 3 seeds = 120 GPU-h, 2 days on cv02.
2. Rein vs Rein-LoRA vs frozen-only vs LoRA (rows 1, 2). Same metrics. Kill: keep only the PEFT variant with the best E1 relF1@2; drop all if none passes the default line. 4 arms x 75 GPU-h.
3. Backbone swap (rows 11, 17, 9): DINOv3-L vs C-RADIOv4-SO400M vs SAM2 Hiera-L in the winner of 2. Kill: drop a backbone if E1 relF1@2 is more than 0.02 below the best one.
4. A8 redone (row 4): DINOv3 ConvNeXt-B vs ImageNet ConvNeXt-B in U-Net++, full fine-tune, 20k steps, 3 seeds. Metric: CV crack IoU and relF1@2, inactive IoU. Kill: DINOv3 not above ImageNet by 0.01 crack IoU at CV. About 40 GPU-h.
5. ExPLoRA (row 5): DINOv2-L continued DINO pretraining on the 11.9k pool (about 1 to 2 days on 8 A6000, S estimate), then arm 1 with the adapted backbone. Kill: E1 relF1@2 not +0.02 over arm 1 with the original backbone.
6. Rein++ Rein-A (row 3): add Rein-A on 1,152 pool half-cells to the winner of 2. Kill: not +0.02 E1 relF1@2 over Rein-G alone.
7. Dino U-Net stand-alone (row 7) and DINOv3-PEFT dual branch (row 8): vs VFM-H. Kill: either arm more than 0.01 CV crack relF1@2 below VFM-H and no E1 gain.
8. SAM3-Adapter (row 10): only after the user OKs weights. Kill: default.
9. Distillation (rows 13, 14): only if an arm passes. Student = house R34. Kill: student keeps less than half of the teacher's E1 gain.
10. UniMatch V2 (row 15): VFM-H student, 478 labelled + 11.9k pool. Kill: CV crack relF1@2 and inactive IoU both n.d. vs VFM-H supervised.
11. Benchmark suite (rows 12, 16): SegDINO and a ViT-B linear decoder run once each under the benchmark protocol; no kill, they are reference rows.

## 6. Rejected (one line each)
- doi:10.1109/iccv51701.2025.00192 ViT-Split: ADE20K evidence only; removes the CNN branch, which is the part we need for cracks.
- doi:10.52202/085713-2036 Perception Encoder: PE-Spatial is a valid backbone, but nothing beyond the abstract and README numbers (web: ADE L/14 48.1) was verified; C-RADIOv4 already distils SigLIP2 + DINOv3 + SAM3.
- arxiv:2502.14786 SigLIP 2: dense features are improved, but it is a VLM encoder; reaches us through C-RADIOv4.
- arxiv:2607.21973 PIB prompt information bottleneck: classification benchmarks only.
- arxiv:2610.27960 DCR-SAM (SAM3 multi-class): needs text concepts per class; our classes have no text names SAM3 knows.
- arxiv:2505.13099 InsCore synthetic segment pretraining: instance occlusion pretraining, on par with IN-21k; belongs to D06 / D21 if anywhere.
- doi:10.58286/33444 X-ray NDT ViT + PEFT: supports row 5 (domain SSL + PEFT) but abstract only, no numbers.
- arxiv:2509.06467 DINOv3 medical benchmark: R: no consistent scaling with size or resolution in medical; kept as context for row 17, not an arm.
- arxiv:2603.28297 DinoDental, arxiv:2607.27087, arxiv:2601.08078, doi:10.3390/bioengineering13020133: DINOv3 medical adaptations on blob-like targets; nothing beyond rows 7 and 1.
- doi:10.1109/cvpr52734.2025.01354, arxiv:2504.12753, doi:10.52202/085713-5035: rely on text or depth cues absent in flat EL cells.
- arxiv:2603.19531, arxiv:2608.03023, arxiv:2603.28480: open-vocabulary or training-free in-context segmentation; we have 478 labelled cells.
- doi:10.1145/3664647.3680906 spectral tokens, doi:10.1609/aaai.v40i15.38290 Causal-Tune, doi:10.1109/tpami.2025.3649001 CrossEarth: Rein variants for DG; run only if arm 2 shows a Rein gain on E1 (kept from 12 Nov list, demoted).
- arxiv:2412.04077 SoMA: covered by D30.
- arxiv:2601.02273 TopoLoRA-SAM, arxiv:2504.04034 UCS, doi:10.1007/978-3-032-37627-5_22: covered by D14 / D22.
- arxiv:2504.14032 LoftUp, doi:10.1109/iccvw69036.2025.00028: feature upsamplers covered by D22.

## 7. Gaps
- No paper found that tests VFM + PEFT on EL images or on 1 to 2 px jittered labels. All transfer evidence is from medical greyscale, SAR, X-ray or RGB industrial data.
- Mixed evidence on greyscale: row 4 X-ray and row 18 PET/CT say natural-image VFMs can lose to ImageNet or random init; row 1 MRI/CT says VFMs win under domain shift. Only our own run decides.
- search_snippets failed all session (Semantic Scholar rate limit), so per-paper numbers for rows 3, 7, 8, 10, 11, 13, 14 are from abstracts only.
- Not covered: layer-wise lr decay / LP-FT studies for ViT segmentation (search 8 returned nothing usable); this is the ViT analogue of our PF finding and could be a short sub-direction.
- Licences: DINOv3 and SAM3 weights are gated (need the user's OK). DINOv2, SAM2 and C-RADIOv4 are not gated (C-RADIOv4 licence "permissive" per its report).
- Compute per ViT-L run at 1024 px is an estimate; time one run before planning folds.
