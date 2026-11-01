# Idea 8: foundation encoder done properly (found, 31 Oct 2026)

Om's idea 8: DINOv3 (arXiv 2508.10104) or a SAM / SAM2 encoder, PF-style or LoRA fine-tune, plus a high-resolution decoder or CNN branch; start with a cheap probe (Track D D1 design). Tags: E measured (file), R literature (Research MCP id), S judgement. CPU / read-only; no GPU, no download, no test cell read.

**v2, 31 Oct 14:18 IST (log.md): revised after judge's REVISE (items 1-7).**
- The probe gate now has a cell bootstrap, a cell-level AUROC and the 51 unseen-module full cells.
- A probe pass is stated as necessary, not sufficient, and is followed by a 1-seed PF fine-tune screen.
- There is a PF sanity row.
- §4b no longer uses E1 co-primaries (that needs a user decision) and is also gated on RN50-PF.
- The stem is needed for U-Net too; the ceil-IoU reading is tagged S; A8c weights are stated.
- Judge's verdict on v1 is kept below.

**v3, 31 Oct 14:29 IST (log.md): judge's v2 PASS-to-protocol items applied.** v3.1, 14:31 IST: val inactive IoU moved out of the screen's kill rule (report only); the stale "1-seed screen" in §4b fixed; stamps corrected to log.md times (handbook 13 D23).
- The probe is descriptive and only picks candidates.
- The 2-seed complete-short-schedule PF screen is the kill gate, with its rule on F51 (module bootstrap) and H36 for false alarms only.
- 4b has the "E1 co-primary slot (pending user)" and an F51 co-primary with a bootstrap co-condition. **Update 17:36 IST:** the user's E1 policy filled the slot: E1 co-primaries are pre-registered, read once at 4b's opening, never for selection.
- §5 says there is no usable labelled half-cut crack set outside E1.

**Verdict proposed: PASS to protocol, in three steps (judge: PASS-to-protocol for 4a / 4a', 4b conditional).**
1. P8-probe, a frozen-feature probe (~1 GPU-h; needs the user's OK for ~290 MB of weights). Descriptive only: it picks which hierarchical candidate enters the screen, and never closes the direction.
2. **The kill gate:** a PF fine-tune screen, A8 vs A8c, 2 seeds each on a complete 4k schedule (~1.5-2 GPU-h). The rule is on F51 with a module bootstrap.
3. If the screen says GO and PF2's RN50-PF is not a clear null: the full arm, DINOv3 ConvNeXt-T under PF with an ImageNet ConvNeXt-T-PF control.

Hierarchical encoders first (DINOv3 ConvNeXt, SAM2 Hiera). A ViT-S/16 + LoRA + HR branch only if the probe ranks it top. SAM ViT: not as the encoder.

**Files (md5):**
- `found_scripts/crack_resolution.py` b7a05fa4, output `crack_resolution.txt` 53e62e76;
- encoder census `found_scripts/enc_census.py` c904394c and `smp_check.py` 83829395 (run on gaint CPU via stdin; outputs quoted in §1).

## 1. Premise check (E)
- **Om's premise: PF says preserved general features help unseen panels.**
  - E, README / `verify_100_o1.md`: PF keeps layer3/4 (cos 0.93-0.96 vs ~0 for the house recipe).
  - E1 (descriptive): crack recall 0.169 → 0.213, inactive IoU 0.041 → 0.245.
  - Test n.d.
  - Consistent across three sources: bigger or preserved encoders raise E1 crack recall with test n.d.:
    - R3 RN50 +0.036 (`trackM/results_r3.md`);
    - D RN50-5 target +0.060 (`team_2026-10-29_features/verify_d.md`);
    - R5 2x +0.026 (`trackM/results_r5.md`).
  - So "a stronger preserved encoder moves E1" has support. Its size is not known.
- **Patch-16 vs 2-3 px cracks (E, `ideas/found_scripts/crack_resolution.txt`, masks_escdd train 478):**
  - Crack width (2·EDT on the skeleton): median 2.0 px, p90 4.0.
  - At stride 16 (a ViT-S/16 token at 512 px input):
    - 99.1% of train crack px are a minority in their 16×16 block;
    - 70.7% fill < 25% of it;
    - 79% of crack components share a block-level component with another;
    - a perfect block-level predictor upsampled by nearest has IoU ≤ 0.135.
  - At stride 4 (the first stage of ConvNeXt / Hiera / ResNet layer1) these are 42.8%, 8.5%, 57%, IoU ≤ 0.375. At stride 2 they are 7.9%, 0%, 22%, 0.637.
  - **(S)** These are nearest-upsampling, block-level ceilings. Bilinear logits and learned decoders can place some sub-patch structure, so "a plain ViT decoder on 16-px tokens cannot place cracks" is a judgement. The E support for "hierarchical first" is D1's DINOv2-S/14 fail (§2).
- **Which encoders are drop-in today (E, gaint CPU, no weights loaded; `timm` 1.0.30, `segmentation_models_pytorch` 0.5.0, torch 2.14.1):**

| Encoder (timm id) | Params | ≈ weights (fp32) | Licence (timm metadata) | Strides | smp U-Net | smp U-Net++ |
|---|---|---|---|---|---|---|
| DINOv3 ConvNeXt-T `convnext_tiny.dinov3_lvd1689m` | 27.8M | 106 MB | `dinov3-license` | 4, 8, 16, 32 | builds | **fails** (no stride-2 stage) |
| DINOv3 ConvNeXt-S / -B | 49.5M / 87.6M | 189 / 334 MB | `dinov3-license` | 4-32 | builds (S) | fails |
| DINOv3 ViT-S/16, S+/16 | 21.6M / 28.7M | 82 / 109 MB | `dinov3-license` | 16 only | fails ("unsupported downsampling") | fails |
| DINOv3 ViT-B/16, L/16 | 85.6M / 303M | 327 / 1,156 MB | `dinov3-license` | 16 | fails | fails |
| SAM ViT-B/16 `samvit_base_patch16.sa1b` (1024 native) | 89.7M | 342 MB | apache-2.0 | 16 | n/a | n/a |
| SAM2 Hiera-T `sam2_hiera_tiny.fb_r896` | 26.9M | 102 MB | apache-2.0 | 4, 8, 16, 32 | builds | fails |
| SAM2 Hiera-S / B+ | 33.9M / 68.7M | 130 / 262 MB | apache-2.0 | 4-32 | builds | fails |
| DINOv2 ViT-S/14 (cached on gaint) | 22.1M | 84 MB | apache-2.0 | 14 | fails | fails |
| for reference: R34 (house) | 21.8M | 83 MB | bsd-3 | 2, 4, 8, 16, 32 | builds | builds |

  - "builds" for smp U-Net: its encoder `out_channels` are [1, 0, 96, 192, 384, 768]. So **U-Net also gets no stride-2 skip**, and a stride-2 stem is needed for U-Net as well (judge).
  - "fails" for U-Net++: it constructs, then the forward fails on the 0-channel stride-2 stage.
  - `smp.DPT` with `tu-vit_small_patch16_dinov3` also fails out of the box.
  - Weight sizes are fp32 parameter bytes. Read the actual file size from the hub listing at download time.
  - **The DINOv3 licence is a custom Meta licence, not OSI, and the hub repos are gated (S).** The user should read it before the download. Thesis research use is the expected-allowed case; redistribution of weights is not needed.
- **What exists (E, `ls`, 31 Oct):**
  - **gaint** `~/.cache/torch/hub`: `dinov2_vits14_pretrain.pth`, `resnet50-11ad3fa6.pth`, `convnext_tiny-983f1562.pth`, the DINOv2 hub code, and HF `smp-hub` R34 / R50 / VGG16.
  - No DINOv3, SAM or SAM2 weights anywhere (gaint, laptop). Track D (24 Oct) checked cv02 for DINOv3: none.
  - Code: timm has all the encoders above. There is no `peft`, `transformers`, `segment_anything` or `sam2` package on gaint. LoRA would be ~50 lines of own code; no install is needed for encoders.
  - Laptop `.venv` has no torch.
  - The D1 probe code is reusable: `scripts_cv02/trackD_probe.py`, gaint copy `cv02_noob_el/el_trackD`.

## 2. Prior tries in the repo (E)
- **Track D D1 (24 Oct):** `team_2026-10-24_go/trackD/protocol_probe.md`, `verify_probe.md`; handbook 18 §D1.
  - Frozen DINOv2-S/14 at 518 px (37×37 tokens): BMRK test crack AP 0.122 / 0.133. It **failed**, below frozen ImageNet R34 (0.185 / 0.187).
  - IN R50 0.268 and IN ConvNeXt-T 0.278 passed (bar 0.215), as a low-precision ranking signal: at A5c+LA's precision they recall 0.02.
  - DINOv3 was skipped (no checkpoint, no gated download).
- **Track M R3 pilot (24 Oct):** U-Net + ImageNet ConvNeXt-T, house optimizer, val 0.6318 < reference 0.6398 (`trackM/results_r3.md`).
  - Under the house optimizer the encoder's deep features are re-learned (`coach_100.md` §0). That mechanism is shown for BN ResNets only; for LayerNorm ConvNeXt it is not established.
- **Track M R3 Part B, RN50 house:** test n.d. on crack, **inactive WORSE** (−0.0251, threshold 0.0227, clean); E1 crack recall +0.036.
- **27 Oct literature team:** SAM-family models fail on tree-like low-contrast objects, and fine-tuning does not fix it (`team_2026-10-27_unlabelled/lit.md` row 14).
- **30 Oct vetter, item 12:** DINOv3 PARKED, with "a frozen probe first (D1 design)" if wanted (`review_suggestions_2026-10-30.md` row 12). Om changed this to "cheap test after PF2" (om §B7).
- **Already planned:** RN50-PF is an arm of PF2 (om §A). It is the ImageNet bigger-CNN version of this idea and runs first.

## 3. Literature (R)
- **DINOv3:** arxiv:2508.10104.
  - Distilled ConvNeXt-T vs supervised IN-22k ConvNeXt-T (Table 15):
    - ImageNet-R 73.7 vs 45.0 (at 256 px);
    - ObjectNet 52.6 vs 44.5;
    - ADE20k linear 42.7 vs 24.8 mIoU.
  - So the CNN form keeps the OOD robustness and dense quality at stride 4. That is the property PF suggested matters.
  - High-resolution adaptation (512-768 crops, §5.1) makes ViT features improve with input size. Running at 1024 px (64×64 tokens, effective stride 8) is a supported mode.
- **Frozen or parameter-efficient vs full fine-tune for domain generalisation:** doi:10.1109/cvpr52733.2024.02704 (Rein, Table 2: GTAV → Cityscapes+BDD+Mapillary, mIoU averaged over the three):
  - DINOv2-L: Full 63.7, Freeze 61.1, Rein-LoRA (2.99M trainable) 66.4;
  - EVA02-L: Full 62.2, Rein-LoRA 65.3.
  - Fewer trainable parameters generalise better. This is the ViT analogue of PF. Urban scenes, not thin structures.
- **SAM family on thin, low-contrast structures:** doi:10.1109/wacv61042.2026.00505. SAM, SAM2 and HQ-SAM degrade with tree-likeness and low textural separability, and "targeted fine-tuning fails to resolve this".
- **SAM adapted to thin structures:**
  - arxiv:2601.02273 (TopoLoRA-SAM): LoRA in the SAM ViT, a spatial conv adapter and clDice give the best Dice on retinal vessels, with 5.2% of parameters trained. Vessels are high-contrast, so not our case.
  - doi:10.1016/j.conbuildmat.2024.136573 (CrackSAM): PEFT of SAM for concrete cracks. Those cracks are wider and more contrasted than EL cracks.
- **Few-shot / industrial DINOv3 uses:**
  - arxiv:2603.28297 (DinoDental: frozen vs full vs LoRA benchmark);
  - arxiv:2604.11162 (Boxes2Pixels: frozen DINOv2 decoder on wind-turbine defects).
  - None is EL, thin-crack or 100%-label evidence.
- **No EL paper with a foundation encoder for pixel crack segmentation was returned** (search "electroluminescence solar cell defect segmentation foundation model", 2023+).

## 4. Design
**Order (S): hierarchical first.** DINOv3 ConvNeXt-T and SAM2 Hiera-T have a stride-4 stage (crack signal 8.5% diluted below 1/4, vs 70.7% at stride 16). Both plug into smp, but need a light stride-2 stem in either U-Net or U-Net++ to supply the 1/2 skip. ViT-S/16 needs 1024 px input or an HR branch plus LoRA code. SAM ViT-B is 90M params with 16-px patches and the thin-structure failure evidence, so it is not tested as the encoder.

### 4a. P8-probe: descriptive only; it picks candidates, it does not gate (v3, judge re-review item 1)
- **Role:** choose which hierarchical candidate(s) enter the screen (DINOv3 ConvNeXt-T, SAM2 Hiera-T), and give a descriptive table. **A probe result never closes the direction.**
  - A linear probe is a weak instrument both ways: it favours SSL features by construction (DINOv3 T15 ADE20k linear 42.7 vs 24.8), and D1's passes did not carry to fine-tuning.
- **Encoders, frozen, eval mode:**
  - cached references: IN R34, IN R50, IN ConvNeXt-T, DINOv2-S/14;
  - fine-tuned sanity rows: SUP100-PF s0 vs SUP100-g s0 encoders (`f3_SUPPF_100pct_s0`, `f3_SUP_100pct_s0`; does the probe see what PF changes?);
  - candidates (download): DINOv3 ConvNeXt-T, SAM2 Hiera-T, DINOv3 ViT-S/16 (512 and 1024 px).
- **Features and head:** D1 recipe. Stride-4 + stride-8 stages; ViT last-layer tokens + 3 intermediate blocks; per-stage linear 1×1, summed; 24 classes, CE; Adam 1e-3, 2,000 steps, batch 8; probe seeds 0, 1; trained on all 478 train cells (masks_escdd).
- **Sets (judge, coach 14:23):**
  - **F51:** 51 full cells from unseen modules; 14,639 crack px, 12 crack cells, 36 modules. **The `_rf` crack decision set.**
  - **H36:** 36 half-cut cells; used **only for false alarms** on its 19 crack-free cells. Its crack labels are unusable: FINAL relR@2 0.036; 48% of its 1,792 crack px lie within 10 px of spacing, border or the cut line.
  - F19: in train modules, reported separately.
  - val 54.
  - **E1 not read in the probe.** Under the user's E1 policy (E1 is a second test set, read once at a protocol's opening), even descriptive E1 reads would be extra openings.
- **Metrics:**
  - crack AP (1,000-bin p(crack), full range);
  - cell AUROC (max p vs ≥ 20 px);
  - recall at matched precision;
  - H36 crack-free false-alarm px;
  - inactive AP.
- **Candidate pick (fixed now):** a candidate enters the screen if its F51 crack AP (2-seed mean) ≥ the best cached CNN reference − 0.02. If none qualifies, DINOv3 ConvNeXt-T enters anyway, as Om's named encoder.
- **Cost:** ~1 GPU-h at the scoring-pass gate via runner; download ~290 MB (user OK); builder ~0.5 day on the D1 script.

### 4a'. PF fine-tune screen: **the kill gate** (v3, judge re-review item 2)
- **Runs:** A8 (DINOv3 ConvNeXt-T-PF) and A8c (IN-1k ConvNeXt-T-PF), same wrapper as 4b, **seeds 0 and 1 each** (4 runs).
  - If the probe picks SAM2 Hiera-T too, add A8h (Hiera-T-PF), 2 seeds.
- **Complete short schedule, identical for every arm** (not a truncated 20k schedule):
  - 4,000 steps, warmup 200, cosine to 0 at step 4,000;
  - PF freeze and ramp scaled ×0.2 (freeze 200, ramp 200), lr_mult 0.1, encoder wd 0;
  - house batch, augmentation, loss and bf16; val off until the end; final weights.
  - No reuse of protocol_100's G5 smoke (truncated 20k schedule).
  - Optional descriptive reference: SUP100-PF (R34) on the same short schedule, 2 seeds.
- **Scored on:** val, F51, H36 (false alarms), F19. No test, no E1.
- **Rule (fixed before any screen number); seed means; GO to 4b only if all hold:**
  1. F51 crack AP: A8 − A8c > 0, **and** a paired module-cluster bootstrap over F51's 36 modules (2,000 resamples, seed 0) gives a lower 95% bound > 0;
  2. val crack AP (at each arm's val-chosen OP-rel b): A8 ≥ A8c − 0.02. Val inactive IoU is **reported only**: 6 val inactive cells, 3 holding 89% of px, so a −0.02 margin at 4k × 2 seeds would kill on noise (judge);
  3. crack-free false-alarm px at the val-chosen OP, on H36 (19 cells) and on F51's crack-free cells: A8 ≤ max(1.5 × A8c, A8c + 200 px).
  - Reported, not in the rule: per-seed values, F51 sign count over its crack modules, cell AUROC, F19, inactive AP, and the PF cosine table at the end.
- **KILL** if any term fails. Report the screen as the negative result (with D1).
- **Cost:** 4 runs × 4k steps. S: at ~1.3-1.6× the R34 step cost, ~0.3-0.5 GPU-h each, so ~1.5-2 GPU-h, within judge's ≤ ~2 GPU-h for 2 seeds.
  - Fine-tune gate from a measured smoke (runner).
  - Builder's wrapper (~1 day) is needed here already.

### 4b. Full arm (only if the 4a' screen says GO, after PF2)
- **Gate on PF2's RN50-PF as well** (judge item 6). RN50-PF is the first test of "a D1-probe-positive encoder under PF".
  - If RN50-PF − SUP100-PF is n.d. on test and on PF2's E1 co-primaries, re-decide with team-lead before launching 4b. The case would then rest on DINOv3 > IN in a probe and a 2-seed short screen.
- **Arms, 5 seeds each (PF2 seeds 5-9), gaint, one commit:**
  - **A8:** DINOv3 ConvNeXt-T-PF;
  - **A8c:** IN ConvNeXt-T-PF (control, same wrapper). **Weights: torchvision IN-1k ConvNeXt-T** (cached on gaint as `convnext_tiny-983f1562.pth`; also the weights of D1 and the R3 pilot).
    - DINOv3's Table 15 comparator is IN-22k supervised (timm `convnext_tiny.fb_in22k`, ~110 MB, Apache-2.0; another download).
    - IN-1k is chosen because it matches the house R34 (IN-1k) and the prior tries. Say so in the protocol.
  - comparator: SUP100-PF (BEST).
- **Contrasts:** A8 − SUP100-PF is the deployable question; A8 − A8c is the pretraining question (one change: the weights).
- **Wrapper (one encoder package):**
  - the timm ConvNeXt-T plus a light stride-2 stem (2× conv3×3, 64 ch, from the 1-channel input) as the 1/2 skip. This is needed for U-Net++ and for U-Net alike; the U-Net++ decoder stays unchanged;
  - 1-channel stem by summing the RGB filters (as the R3 pilot);
  - house normalisation (0.5, 0.25).
- **Optimizer:** PF as SUP100-PF on the ConvNeXt params (freeze 1k, ramp 1k, lr ×0.1, wd 0). The new stem trains at decoder lr.
- **Gate:** cosine to init at 2k steps ≥ 0.5 on stages 2-3, since the LayerNorm erasure mechanism is not established. Also the house identity checks.
- **Primaries (judge item 5: E1 co-primaries are authorised for PF2 only):**
  - house primaries (crack IoU, relF1@2, inactive IoU; two sets), plus component recall at component precision ≥ 0.90 and relR@2 at relP@2 ≥ 0.90.
  - **E1 co-primaries (user's E1 policy, team-lead 17:36 IST): E1 is a second test set.**
    - 4b pre-registers E1 co-primaries: E1 crack recall at the arm's val-chosen OP and E1 inactive IoU, plus the PF2 strata (29 scuff + half-cut, 77 other) reported. The rule is rule 1 over seeds, as PF2.
    - E1 is read **once, at 4b's own pre-registered opening**, together with test. It is never used for selection (screen, OP, bias, early stop).
  - **`_rf` co-primary as well:** F51 crack AP (H36 is unusable), with a co-condition that a paired module-cluster bootstrap lower 95% bound is > 0 (judge item 3). Rule 1 alone measures seed noise only. F51 is available before the opening; E1 is not.
  - Verdict wording: a win needs test primaries not worse, and at least one of {E1 co-primaries, F51 co-primary} BETTER, both disclosed. Multiplicity is listed in the protocol (coach).
- **Inactive is the named risk** (R3 RN50 WORSE).
- **Cost (S, to be measured in the smoke):**
  - FLOPs at 512: encoder ~23.5 vs 18.8 GFLOPs for R34. U-Net++ decoder skips 96/192/384/768 vs 64/128/256/512 channels, about 1.3× of the 148 GFLOPs total;
  - memory: S until the smoke. RN50-PF measured 11,186 MiB alone (runner, `log.md` 14:09). ConvNeXt-T's U-Net++ skips (96-768 ch) are smaller than RN50's (256-2048), but LayerNorm and the 4× MLP add activations, so ~8-11 GB per run and a gate of ~10-13 GB. That allows 2 lanes beside finllm at most (5.9 + 2×11 + 2 = 29.9 < 32.6);
  - ~3.5-4 h per run at 2-3 concurrent; 10 runs ≈ 35-40 lane-h ≈ 14-20 h wall;
  - code ~1 day (builder: wrapper, tests, identity).
- **ViT branch (only if the probe ranks DINOv3 ViT-S/16 at 1024 above ConvNeXt-T):**
  - ViT-S/16 + LoRA (rank 8-16, qkv/proj; own code) + CNN HR branch (stride 2 and 4) into a U-Net decoder;
  - 2-4 days dev; compute near R5's 4× at 1024 input.
  - This is the "LoRA" half of Om's idea. For ViTs (no BN) LoRA is the natural form of PF (R: Rein).

## 4c. P8-probe run 1 RESULT (E, descriptive; all encoders except DINOv3; gaint CPU 18:12-20:19 IST)
- **Run:** `p8_probe.py` f2033a3e; summary `/home/noob/work/found/p8/run1/p8_summary.json` md5 2dedd7e6 (local copy `found_scripts/p8_run1/`); per-cell hists md5 445a3e70.
- **Sets:** val + `_rf`; no test, no E1. P* = calib's SUPPF5 ensemble argmax precision: val 0.611, F51 0.635, H36 0.403, F19 0.330.

| Encoder (frozen, linear probe; 2 probe seeds) | F51 crack AP (mean) | val crack AP | F51 cell AUROC | F51 recall at P* | H36 crack-free FA px (argmax) | val inactive AP |
|---|---|---|---|---|---|---|
| IN R34 (house init) | 0.158 | 0.20 | 0.72 | 0.00 | 1,432-1,700 | 0.32 |
| **IN R50 (torchvision V2)** | **0.444** | 0.36 | 0.70-0.74 | 0.33 | 3-11 | 0.43-0.45 |
| IN ConvNeXt-T (torchvision V1) | 0.310 | 0.33 | 0.61 | 0.07-0.11 | 95-167 | 0.34 |
| DINOv2-S/14 | 0.173 | 0.17 | 0.71-0.74 | 0.00 | 0 | 0.39-0.40 |
| SAM2 Hiera-T | 0.198 | 0.25-0.26 | 0.73-0.76 | 0.01-0.02 | 698-921 | 0.23-0.25 |
| sanity: SUP100-PF s0 encoder | 0.295 | 0.27 | 0.70 | 0.00-0.01 | 1,030-1,097 | 0.45 |
| sanity: SUP100-g s0 encoder | 0.274 | 0.25 | 0.65 | 0.00 | 352-495 | 0.45 |

- **Pick rule (fixed), provisional until the DINOv3 rows exist:** reference = the best cached CNN on F51 = IN R50 0.444, so bar 0.424.
  - SAM2 Hiera-T 0.198 does not qualify, so **A8h is not in the screen.**
  - DINOv3 ConvNeXt-T enters as Om's named encoder whatever its probe value. Its rows are added when the user's route provides the file.
- **Reading (S, descriptive):**
  - H36 crack AP is ~0 for every encoder, as expected from its unusable labels.
  - The sanity row separates PF from house on F51 only slightly (+0.02 AP). PF's encoder keeps more of what a frozen linear probe can use, but the probe is a weak instrument (judge).
  - Frozen IN R50 is again the strongest frozen CNN feature set, as in D1. Its F51 AP (0.444) is even above the fine-tuned SUP100-PF encoder's (0.295).
  - That fits PF2's RN50-PF arm, which is already running. It is no evidence for the screen (probe ≠ fine-tuning).

## 4d. P8-probe run 2 RESULT: the DINOv3 rows (E, descriptive; gaint CPU 1 Nov 14:29-15:48 IST)
- **Run:** `p8_probe.py` f2033a3e (unchanged), `run2.sh` 13b17c17. Weights = route B timm files: ConvNeXt-T abf90463, ViT-S/16 d6f2118f (equivalence `found_scripts/dinov3_equiv.txt` 7a9d78d7).
- **Records:** summary `found/p8/run2/p8_summary.json` md5 ab01c61f. Merge with run 1 via `p8_merge.py` 361c0275 → `found/p8/p8_final.json` md5 7f3d840a. Local copies in `found_scripts/p8_run2/`.
- **Sets:** val + `_rf`; no test, no E1. P* is identical to run 1 (val 0.611, F51 0.635, H36 0.403, F19 0.330).

| Encoder (frozen, linear probe; 2 probe seeds) | F51 crack AP (mean; seeds) | val crack AP | F51 cell AUROC (vs 0-px cells) | F51 recall at P* | H36 crack-free FA px (argmax) | val inactive AP |
|---|---|---|---|---|---|---|
| **DINOv3 ConvNeXt-T** | **0.363** (0.370, 0.357) | 0.35 | 0.76-0.78 | 0.22-0.24 | 216-282 | 0.36-0.37 |
| DINOv3 ViT-S/16 at 512 | 0.147 (0.123, 0.171) | 0.19-0.21 | 0.77-0.81 | 0.00 | 0 | 0.42-0.45 |
| DINOv3 ViT-S/16 at 1024 | 0.212 (0.210, 0.215) | 0.31 | 0.60-0.65 | 0.00-0.01 | 53-143 | 0.48-0.51 |
| ref (run 1): IN R50 | 0.444 (0.443, 0.445) | 0.36 | 0.70-0.74 | 0.33 | 3-11 | 0.43-0.45 |
| ref (run 1): IN-1k ConvNeXt-T (= A8c's weights) | 0.310 (0.322, 0.297) | 0.33 | 0.61 | 0.07-0.11 | 95-167 | 0.34 |

- **Final pick (fixed rule, union of runs 1 + 2):** bar = 0.444 − 0.02 = 0.424.
  - DINOv3 ConvNeXt-T, at 0.363, is below the bar. It enters only as Om's named encoder.
  - SAM2 Hiera-T is out (0.198).
  - ViT-S/16 does not rank top, so it is not carried to a later LoRA + HR design (protocol_A8screen §2).
  - **The screen stays A8 vs A8c. Nothing changes from run 1's provisional pick.**
- **Reading (S, descriptive; the probe never gates the screen):**
  - Frozen DINOv3 ConvNeXt-T beats frozen IN-1k ConvNeXt-T on F51 AP by +0.053. The seed ranges do not overlap. That is above the protocol §4 expectation (0.00-0.04).
  - DINOv3 ConvNeXt-T also has the highest F51 cell AUROC of the CNNs (vs 0-px cells: the 5 F51 cells with 1-19 GT px are excluded; counting them as negatives moves it by up to 0.019, judge). But it has more H36 crack-free false-alarm px: 216-282, vs IN-1k ConvNeXt-T 95-167 and R50 3-11. Its +0.053 AP comes with more false alarms. Crack-free px is carried next to AP wherever A8 is compared to A8c (judge).
  - It stays 0.08 below frozen IN R50.
  - ViT-S/16 at stride 16 loses thin cracks at 512 (F51 recall at P* 0.00). Going to 1024 helps val AP but not F51.
  - Frozen-probe gains have not carried to fine-tuning before (D1 → R3). The A8 − A8c screen is the test.

## 5. Expected effect (S)
- **There is no usable labelled half-cut crack set outside E1** (judge; calib's idea 1: FINAL relR@2 0.036 on H36; domain).
  - The half-cut + scuff context, where 75% of E1 crack px sit, cannot be selected on before E1.
  - Every pre-E1 decision here (probe pick, screen, 4b's `_rf` co-primary) is about unseen **full-cell** panels (F51). The half-cut effect is seen only at the final E1 opening, descriptive unless the user grants the E1 slot.
- **Probe:** DINOv3 ConvNeXt-T ≥ IN ConvNeXt-T on F51 AP is likely (R: Table 15 OOD gains), and a probe win means little for fine-tuning (§4a). DINOv3 ViT-S/16 at 512 likely trails, as DINOv2 did; at 1024 it is open. SAM2 Hiera-T is open.
- **Screen:** P(GO) ≈ 0.3-0.4. F51 has only 12 crack cells, so the module bootstrap lower bound > 0 is a strict bar.
- **Full arm:**
  - test crack IoU −0.01 to +0.01 (n.d. likely; MDE 0.012);
  - E1 crack recall +0.02 to +0.06 over SUP100-PF;
  - inactive: unknown, with downside risk.
  - It could become BEST only through an unseen-panel co-primary (§4b options) and capture metrics, not test IoU.
  - Any E1 effect rests on ~20 crack cells (75% of E1 crack px are in the 29 scuff + half-cut cells; judge).

## 6. Kill criteria
- **Probe:** no kill. It only picks candidates (§4a).
- **Screen (4a'), the kill gate:** any rule term fails. Then close "foundation encoder" for this thesis, report it with D1 as a negative result, and download no larger variants.
- **Full arm:** A8 − SUP100-PF n.d. on test and the chosen unseen-panel co-primary not better, or inactive WORSE. Close it.
- **PF gate fails** (cos < 0.5): fix PF for LayerNorm before any arm runs.

## 7. Needs from others
- **User:** OK to download ~290 MB of weights (DINOv3 licence acceptance; SAM2 Apache-2.0).
- **team-lead:** batch this with other GPU requests.
- **runner:** probe slot (scoring-pass gate); smoke memory; 4 screen runs (~1.5-2 GPU-h).
- **builder:** probe script on top of D1; ConvNeXt wrapper (needed for the screen).
- **coach:** protocol covering 4a' (rule above) and 4b after PF2.
- Batched with idea 10's ask (judge item 5): the user's OK for DINOv3 + SAM2 weights.

---

## judge verdict (31 Oct 2026, 14:13 IST per log.md; report md5 83d5ea15 as reviewed)

**Verdict: REVISE.** The direction stays open, and the probe is cheap and worth running. But its gate metric is underpowered and has low specificity for the fine-tuned question. Step 4b also relies on an E1 use that is not authorised. Fix items 1 to 4 below and the probe passes to protocol. 4b stays gated as in item 5.

### What I reproduced (E)
- **Crack vs stride** (§1), recomputed from the local 20221008 release masks, independent of found's gaint copy (`judge/crack_width.py`, md5 87f57a58):
  - train stride 16: diluted < 25% 0.703 (found 0.707), ceil IoU 0.136 (0.135);
  - train stride 4: 0.084 (0.085), ceil IoU 0.377 (0.375);
  - train stride 2: 0.000, ceil IoU 0.639 (0.637);
  - val and E1 match to ≤ 0.004.
  - Small gaps: 4 of our cells are missing from the release, and masks_escdd differs from the release at scuff/star remaps.
- **Encoder census, spot check on gaint CPU** (nice 19, 1 thread, no weights):
  - `convnext_tiny.dinov3_lvd1689m` and `vit_small_patch16_dinov3.lvd1689m` are `dinov3-license`; `sam2_hiera_tiny.fb_r896` is apache-2.0.
  - ConvNeXt-T has 27,818,592 params without the head; reductions [4, 8, 16, 32].
  - smp 0.5.0 U-Net++ with `tu-convnext_tiny` constructs, but its **forward fails** (a 0-channel stride-2 stage). found's "fails" holds in substance.
  - Note: smp U-Net "builds", but its encoder out_channels are [1, 0, 96, 192, 384, 768]. So the U-Net also has **no stride-2 skip**. The stride-2 stem in 4b is needed for U-Net too, not only for U-Net++.
- **Hanifi `_rf` set after hygiene** (117 − 7 CSIR_00300 − 4 val/test-module = 106, matching calib's build), from local E-SCDD masks:

  | Group | Cells | Crack px | Crack cells ≥ 20 px |
  |---|---|---|---|
  | half-cut (all unseen-module) | 36 | **1,792** | 17 |
  | full, unseen-module | 51 | 14,639 | 12 |
  | full, in a train module | 19 | 6,811 | 9 |

  For scale, E1 half-cut cells hold 26,737 crack px.
- **Literature:** all 7 ids in §3 resolve (get_paper). Numbers checked against full text:
  - Rein, doi:10.1109/cvpr52733.2024.02704, Table 2: DINOv2-L Full 63.7 / Freeze 61.1 / Rein-LoRA 66.4; EVA02-L Full 62.2 / Rein-LoRA 65.3. **Match.**
  - DINOv3, arxiv:2508.10104, Table 15, CNX-T: IN-R@256 73.7 vs 45.0; ObjectNet 52.6 vs 44.5; ADE20k linear 42.7 vs 24.8. **Match.** The comparator is IN-22k supervised ConvNeXt; the cached gaint ConvNeXt-T is torchvision IN-1k.
  - doi:10.1109/wacv61042.2026.00505, arxiv:2601.02273 and doi:10.1016/j.conbuildmat.2024.136573: abstracts match the claims made.
- **Prior tries** (§2) are correct and complete as far as I can find: D1, the R3 pilot, R3 Part B, R5 and vetter item 12. The probe is not a repeat of D1. DINOv2-S/14 failed D1 at stride 14; DINOv3 ConvNeXt and SAM2 Hiera have a stride-4 stage and Gram-anchored dense features, so they test something D1 could not.

### What must change
1. **The probe gate metric is underpowered (E).**
   - Rule 1 rests on "_rf half-cut crack AP": 1,792 crack px in 17 cells, with Hanifi's speckled SAM crack labels.
   - A fixed +0.05 AP margin has no noise estimate. With 2 probe seeds and 17 cells, it can pass or fail on 2 to 3 cells.
   - Required:
     - (a) A paired cell bootstrap (2,000 resamples, over the 36 half-cut cells, both probe seeds averaged). Pass needs the lower CI bound > 0 in addition to the +0.05 margin.
     - (b) A cell-level readout that is robust to speckle, as the vetter's ≥ 20 px presence rule: cell AUROC of max p(crack) on the 36 half-cut cells.
     - (c) Report the 51 unseen-module full cells (14,639 crack px) as a second, better-powered `_rf` set. State before any number which set decides; I recommend half-cut AND not-worse on the 51.
2. **A frozen linear probe favours self-supervised features by construction (R + E).**
   - DINOv3's own Table 15: CNX-T ADE20k linear 42.7 vs 24.8 for the supervised ConvNeXt-T. So DINOv3 is likely to "pass" a linear-probe gate, whether or not it helps after fine-tuning.
   - Track record (E): D1's frozen passes, IN R50 and IN ConvNeXt-T, did not carry to fine-tuning. R3 RN50 was n.d. on test crack and WORSE on test inactive; the ConvNeXt-T pilot was below reference.
   - So a probe pass is necessary, not sufficient. The protocol must say so, and must not quote a pass as evidence the full arm will work.
   - Cheaper alternative that measures the right thing (S): a 1-seed, 4k-step PF fine-tune screen (A8 vs A8c only, about 2 × 0.5 GPU-h), scored on val + `_rf`. Run it in place of, or after, the linear probe.
3. **Probe sanity row (descriptive, labelled).**
   - Report the SUP100-PF s0 vs SUP100-g s0 encoder probes on `_rf` half-cut as a validity check: does the probe see the PF difference PF2 is testing?
   - This only reads a known contrast; it is not a selection. If the probe cannot separate those two, its half-cut readout carries little information.
4. **Unseen-module bookkeeping.** 19 of the 70 hygiene-kept full `_rf` cells sit in train modules (E, `judge/out/module_avail.tsv` logic). Report "unseen-module" numbers on the 51 only.
5. **4b relies on an unauthorised E1 use (rule).**
   - Om B1 and the README allow E1 co-primaries for **PF2 only**. §4b adds E1 crack recall and E1 inactive IoU as co-primaries for A8.
   - §5 itself expects test n.d. (crack −0.01 to +0.01 vs MDE 0.012), so without E1 co-primaries A8 has no pre-registered route to a win.
   - Options:
     - (a) Ask the user to extend E1 co-primary use to A8 (cost: E1 becomes a multi-protocol selection set);
     - (b) use `_rf` co-primaries (weak, as in item 1);
     - (c) one final pre-registered E1 opening for the combined candidate only.
   - This is a cross-idea issue; see the ranking note to team-lead.
6. **4b dependency (S).** Gate 4b on PF2's RN50-PF result as well as the probe. RN50-PF is the first test of "a D1-probe-positive encoder under PF". If RN50-PF − SUP100-PF is n.d. on test and on the E1 co-primaries, the case for A8 rests only on DINOv3 > IN in a linear probe (item 2). Re-decide then.
7. **Minor:**
   - §1's "a perfect block-level predictor ... IoU ≤ 0.135" is a nearest-upsampling ceiling. Probes upsample logits bilinearly, and decoders can place sub-patch structure. Tag the "cannot place cracks" conclusion S. The design choice, hierarchical first, still stands on D1's DINOv2 fail (E).
   - State A8c's weights: IN-1k torchvision (cached) vs IN-22k (DINOv3's comparator, needs a download).
   - Memory: RN50-PF measured 11,186 MiB alone (runner, log 14:09). ConvNeXt-T U-Net++ with 96/192/384/768 skips may exceed that, so the "8 to 10 GB" estimate is S until the smoke.

### Cost, effect, kill (S)
- **Probe:** ~1 GPU-h plus ~290 MB of gated weights (user OK). Kill: real ("no candidate passes"), once items 1 to 2 make "pass" meaningful.
- **Full arm:** 35 to 40 lane-h, ~1 day code. Expected test n.d. (below the 0.012 crack MDE); the E1 gain is unknown in size; inactive is the named risk. Value hinges on item 5.

### Tags
- E: crack/stride and census reproduced; `_rf` composition recounted.
- R: 7 ids verified; 2 tables matched.
- S: the specificity critique and the RN50-PF gate.

### judge addendum (31 Oct 14:19 IST per log.md, after team-lead's interim E1 rule)
- **Item 2, changed from an option to the ask:** make the primary screen a **1-seed, 4k-step PF fine-tune**: A8 (DINOv3 ConvNeXt-T-PF) and A8c (IN ConvNeXt-T-PF), same wrapper, scored on val + the `_rf` sets of item 1.
  - The linear probe may stay as a cheap descriptive side table, but it is not the gate.
  - The screen needs a pass rule on val + `_rf` fixed before any number: bootstrap lower bound > 0 on `_rf` half-cut, and not worse on val beyond a stated margin.
- **Item 5, per team-lead's interim rule:** select on val + `_rf` (hygiene), E1 descriptive only, and write "E1 co-primary slot (pending user)" in 4b instead of assuming one.

## judge re-review of v2 (31 Oct 2026, 14:20 IST per log.md; report md5 452d1d28 as reviewed)

**Verdict: PASS-to-protocol** for 4a / 4a', with 4b conditional as written. v2 fixes v1's items 1 to 7: the H36 / F51 / F19 sets, the bootstrap term, the "necessary, not sufficient" wording, the sanity row, the RN50-PF gate, the E1 co-primaries removed, and the stem, ceil-IoU and A8c-weights notes. v2 was written before my addendum, so items 1 and 2 below carry it into the protocol.

**The protocol (coach) must include:**
1. **The screen (4a') is the kill gate; the probe (4a) is not.**
   - A linear probe on 1,792 H36 crack px is a weak instrument both ways. A probe fail should not close the direction (false-DROP risk).
   - Use the probe only to pick which hierarchical candidate(s) enter the screen (DINOv3 ConvNeXt-T and/or SAM2 Hiera-T), plus its descriptive table.
   - The screen costs about the same GPU time as the probe, and needs builder's wrapper and the weights either way.
   - This is the version team-lead agreed (judge addendum above).
2. **Screen design:**
   - (a) A **complete short schedule**, identical for A8 and A8c: warmup + cosine to 0 at the last step, PF freeze/ramp scaled and stated. Scores from a truncated 20k schedule at 4k are taken mid-schedule at high lr and are noisy. Do not reuse the protocol_100 G5 smoke checkpoint as a reference unless it ran the same short schedule.
   - (b) **2 seeds per arm if the cost stays ≤ ~2 GPU-h.** Decide on the seed mean; report the paired cell bootstrap on H36 and F51.
   - (c) The go/kill rule is fixed in the protocol before any screen number.
3. **If 4b ever uses `_rf` co-primaries (option b), add a cell-bootstrap co-condition** (lower 95% bound > 0 on the passing `_rf` metric). Rule 1 measures seed noise only, and H36 rests on 17 crack cells in 7 modules.
4. **E1:** an "E1 co-primary slot (pending user)" line, per team-lead's interim rule. found's recommendation, `_rf` for A8 and E1 only at one final opening, is consistent with that rule.
5. **Approvals before anything runs:** the user's OK for the gated DINOv3 weights (+ SAM2 Hiera-T), batched with idea 10's; runner's fine-tune gate from a measured smoke.

**Reproduced claims:** as in the v1 verdict (crack/stride, census spot check, `_rf` composition, 7 ids, 2 tables). v2 adds no new E numbers.

## judge re-review of v3 (31 Oct 2026, 14:30 IST from date; report md5 26bc94ed as reviewed)
**PASS-to-protocol confirmed.**
- Every v2 item is in:
  - the probe only picks candidates;
  - the 2-seed complete-short-schedule PF screen is the kill gate, decided on F51 with a module bootstrap;
  - H36 is for false alarms only;
  - the E1 slot is pending;
  - the F51 co-primary carries a bootstrap co-condition.
- **One change for coach's protocol:** take **val inactive IoU out of the screen's kill rule (term 2)** and report it instead.
  - Val holds 6 inactive cells, 3 with 89% of the px (handbook 13 A2). At 4k steps and 2 seeds, a −0.02 margin there can KILL the arm on noise: a false DROP.
  - Inactive risk is covered by the full arm's test inactive primary (R3's WORSE was on test).
  - Keep val crack AP ≥ A8c − 0.02.
- **Wording:** §4b's RN50-PF bullet still says "a 1-seed screen". Make it 2 seeds.

### judge check of P8 probe run 1 (31 Oct 2026, 20:22 IST from date; summary md5 2dedd7e6, hists 445a3e70)
**Reproduced exactly.** I computed my own step-wise binned AP from found's per-cell pos/neg histograms (`judge/p8_recompute.py`, md5 19f56166, gaint CPU).

F51 crack AP, 2-seed mean (val in brackets):

| Encoder | F51 | val |
|---|---|---|
| R50 | 0.444 | 0.362 |
| IN ConvNeXt-T | 0.310 | 0.333 |
| SUP100-PF s0 encoder | 0.295 | 0.266 |
| SUP100-g s0 encoder | 0.274 | 0.248 |
| SAM2 Hiera-T | 0.198 | 0.254 |
| DINOv2-S | 0.173 | 0.169 |
| R34 | 0.158 | 0.203 |

- **Pick rule** (bar = 0.444 − 0.02), applied correctly:
  - SAM2 Hiera-T fails → no A8h;
  - DINOv3 ConvNeXt-T enters by rule, pending the weights after PF2.
- **Sanity row:** PF − house encoder +0.021 on F51 (seed ranges do not overlap: 0.285-0.305 vs 0.272-0.276). The probe separates them in PF's direction, weakly. So it is informative, not void.

**Reading (S):**
- Frozen IN R50 leads every other encoder by ≥ 0.13 F51 AP, including our fine-tuned R34 encoders. This repeats D1's R50 signal on unseen-module full cells.
- **For 4b:** A8c (IN-1k ConvNeXt-T) is a weaker reference than R50. If PF2's RN50-PF becomes BEST, A8's deployable comparator must be RN50-PF, not SUP100-PF. Coach should write that conditional into 4b.
- Probe passes stay necessary, not sufficient (D1 → R3 track record).

### judge check of P8 probe run 2, DINOv3 rows (1 Nov 2026, 18:57 IST from date; §4d as of file md5 c207ceab, summary ab01c61f, hists 8668826b)
**Reproduced exactly (E).** My own code ran on found's per-cell histograms, pulled read-only to the laptop:
- F51 / val crack AP: `judge/p8_recompute_v2.py` 5793dc68, which is 19f56166 with the input path as an argument;
- inactive AP, cell AUROC, crack-free FA px and recall at P*: `judge/p8_run2_extra.py`.

Every field of `p8_summary.json` matches with |Δ| = 0. That covers 3 encoders × 2 seeds × val / F51 / H36 / F19. Run 1 recomputes unchanged (R50 0.444, IN-1k ConvNeXt-T 0.310, ...).

| Encoder | F51 crack AP (s0, s1) | val crack AP | F51 cell AUROC | F51 R@P* | H36 FA px | val inactive AP |
|---|---|---|---|---|---|---|
| DINOv3 ConvNeXt-T | 0.363 (0.370, 0.357) | 0.351 / 0.353 | 0.777 / 0.760 | 0.236 / 0.219 | 282 / 216 | 0.363 / 0.370 |
| DINOv3 ViT-S/16 at 512 | 0.147 (0.123, 0.171) | 0.194 / 0.209 | 0.772 / 0.809 | 0.000 / 0.001 | 0 / 0 | 0.450 / 0.424 |
| DINOv3 ViT-S/16 at 1024 | 0.212 (0.210, 0.215) | 0.314 / 0.311 | 0.596 / 0.652 | 0.006 / 0.004 | 53 / 143 | 0.510 / 0.482 |

- **Pick rule** (bar 0.444 − 0.02 = 0.424): applied correctly.
  - DINOv3 ConvNeXt-T (0.363) is below the bar and enters only as Om's named encoder.
  - ViT-S/16 does not rank top.
  - The screen stays A8 vs A8c.
- **DINOv3 − IN-1k ConvNeXt-T on F51:** +0.053, seed ranges 0.357-0.370 vs 0.297-0.322 (non-overlapping). Confirmed.

**Notes (S, descriptive):**
1. **Cell AUROC definition.** It is max p(crack) on cells with ≥ 20 GT px vs cells with **0** GT px. The 5 F51 cells with 1-19 GT px are excluded. With those 5 counted as negatives, F51 AUROC moves by up to 0.019 (ViT-S/16 512 s0: 0.791 vs 0.772). §4d should say "vs 0-px cells".
2. **The false-alarm cost is the larger story.**
   - On H36 crack-free cells, DINOv3 ConvNeXt-T fires 216-282 px at argmax, against IN-1k ConvNeXt-T 95-167 and R50 3-11. That is about 20-90× R50's false alarms.
   - It also fires 347 / 496 px on F51's crack-free cells.
   - So its AP edge over IN-1k ConvNeXt-T comes with more false alarms. That matters for a model meant to be deployed. If A8 is ever compared to A8c on E1 or `_rf`, report crack-free px next to AP.
3. **The ViT-S/16 inactive AP is the highest on val** (0.42-0.51 vs ≤ 0.45 for every run-1 encoder). It has no crack recall at P*, so it does not change the pick (crack rule). Recorded only.
4. Probe results are necessary but not sufficient (D1 → R3). Nothing here gates the A8 screen. No test and no E1 data entered.
