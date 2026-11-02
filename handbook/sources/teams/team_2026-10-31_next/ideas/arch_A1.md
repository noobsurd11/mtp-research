# A1: two-branch encoder, frozen / PF DINOv3 ConvNeXt-T + high-resolution CNN branch (Om, 1 Nov)

arch, 2 Nov 2026. Tags: E measured (file), R literature (Research MCP id), S judgement. CPU only. No test or E1 file opened; new numbers are val / Hanifi `_rf` from existing records. Om wrote A1 before the A8 screen result (KILL, `verify_a8screen.md`, judge-confirmed).

## 0. Verdict (proposed): DROP
- **Most of A1 is what the A8 screen already tested**, and it found no sign of a gain (F51 AP −0.024, module bootstrap LB −0.046; FA px ×2-3; inactive IoU lower).
- **What is genuinely not a repeat:** (a) a fully frozen DINOv3 branch instead of PF fine-tuning; (b) gated instead of concat fusion; (c) a heavier HR branch; (d) keeping the R34-PF encoder and adding DINOv3 as a side branch. Only (d) changes the question, and for (d) the one piece of non-E1 evidence about frozen DINOv3 features points the wrong way: frozen DINOv3 ConvNeXt-T ranks **below** frozen IN R50 on F51 (probe AP 0.363 vs 0.444), and R50 under PF already FAILED (PF2 RN: test inactive WORSE; the E1 scuff + half-cut target −0.025).
- No non-E1 evidence predicts A1 would beat the KILL. Default DROP stands.
- Side finding (S, §1.3; not A1, not proposed now): the ConvNeXt-T family at 4k, either init, scores above R34-PF at 20k on F51, but the comparison is confounded by training length and is the same size as HC's F51 gain, which did not transfer to E1.

## 1. Premise check (E)
### 1.1 What A8 already covered (E, `protocol_A8screen.md`, `review_f8_wrapper.md`, `verify_a8screen.md`)
| A1 component (Om) | In the A8 screen? |
|---|---|
| Branch 1: DINOv3 ConvNeXt-T, PF-style | **Yes.** A8 = DINOv3 ConvNeXt-T under PF (4k schedule: freeze 200 / ramp 200 / lr_mult 0.1), validity cos stages 2-3 ≥ 0.98 |
| "or mostly frozen" | **Partly.** A8 moved 10× more than A8c under the same PF (1 − cos 0.013-0.038 vs 0.003-0.004); a hard freeze was not run |
| Branch 2: light HR CNN, stride ≤ 2 | **Yes.** el_f8 `hrstem_unetpp` adds a 2-conv stride-2 stem feeding the 1/2 skip (decoder x_0_* blocks) |
| Fusion in the decoder (concat) | **Yes.** U-Net++ concatenates encoder skips at 1/2-1/32 in every nested block |
| Gated fusion | No |
| Kill: no E1 gain vs SUP100-PF | A8's kill was non-E1 (F51 AP vs IN ConvNeXt-T); E1 was never read for A8 |
- A1 as written is therefore A8 + {hard freeze, gated fusion}. Neither has an argument from our data: the frozen-probe edge (DINOv3 − IN-1k ConvNeXt-T +0.053 F51 AP, `idea08_foundation.md` §4d) is exactly the edge that did not carry to fine-tuning, and a hard freeze moves the model back toward the probe regime, where DINOv3 ConvNeXt-T trails frozen IN R50 (0.363 vs 0.444) and has 20-90× R50's H36 crack-free FA (216-282 vs 3-11 px).

### 1.2 Non-E1 signals for and against DINOv3 (E, already verified)
- For (small n): A8 F19 crack AP 0.350 vs A8c 0.220 (9 crack cells, 37% of px in one cell); F51 cell AUROC 0.749 vs 0.671 (12 positives).
- Against (larger): F51 AP −0.024 (every leave-one-crack-module-out negative); H36 FA ×3.3, F51 FA ×1.95 at val b_rel; inactive IoU at b_rel val 0.376 vs 0.408, F51 0.222 vs 0.307, F19 0.061 vs 0.426.
- Encoder-family precedent under PF: RN50-PF (the best frozen probe, 0.444) FAILED on test inactive (−0.029, both sets) and did not lift E1 scuff + half-cut (−0.025) (`verify_pf2.md`).

### 1.3 Side check: ConvNeXt-T (either init) at 4k vs R34-PF at 20k (E, DESCRIPTIVE, cross-protocol, not pre-registered)
`scripts/arch/a1_cnx_vs_r34.py` 5ff50009 → `ideas/arch_out/a1_cnx_vs_r34.txt` ddf9cc95 (existing val + rf records; confounds stated in the script before computing). F51 AP from the shared 1,000-bin scorer (a8_screen_score 8eba76e5, used by both the A8 screen and the HC opening).
| arm (seeds) | steps | val crack AP | F51 crack AP | F51 relF1@2 at val b_rel | F51 crack IoU at b_rel | F51 / H36 FA px at b_rel | val inactive IoU at b_rel |
|---|---|---|---|---|---|---|---|
| A8 DINOv3 CNX-T-PF (2) | 4k | 0.525 | 0.545 | 0.847 | 0.436 | 392 / 92 | 0.376 |
| A8c IN-1k CNX-T-PF (2) | 4k | 0.529 | 0.569 | 0.854 | 0.447 | 201 / 28 | 0.408 |
| SUP100-PF R34 (5) | 20k | 0.483 | 0.470 | 0.820 | 0.413 | 1,231 / 278 | 0.508 |
| HC R34 (5) | 20k | 0.514 | 0.537 | 0.861 | 0.445 | 122 / 11 | 0.470 |
- **Post hoc, cross-protocol, hypothesis-generating only** (judge): this comparison was made after looking at already-opened screens and was never pre-registered. Confounds, all of them, not only training length:
  1. **Architecture and code:** A8 / A8c are el_f8's `hrstem_unetpp` (extra 2-conv stride-2 HR stem, timm ConvNeXt-T stages) on el_f8 c280e8c2; R34-PF is smp U-Net++ / ResNet-34 on e544133.
  2. **PF schedule:** freeze / ramp 200 / 200 at 4k vs 1,000 / 1,000 at 20k.
  3. **Training length:** 4k vs 20k steps (no R34-PF 4k checkpoint exists; val_every 20,000, checked on gaint).
  4. **Seeds:** 2 (s0-1) vs 5 (s5-9).
  5. **One cell:** F51 crack AP is 76% one cell (CSIR_00073_r9_c3_rf, 11,110 of 14,639 px); A8c's seed-1 0.602 is mostly that cell (judge, verify_a8screen §2). The ConvNeXt-T "lead" is a 2-seed, one-cell measurement.
  6. **Inactive goes the other way, by as much:** val inactive IoU at b_rel 0.408 (A8c) vs 0.508 (R34-PF 20k).
- Reading (S): both ConvNeXt-T screens sit about where HC sits on F51, above SUP100-PF, and lower on val inactive. This is not A1 evidence (DINOv3 < IN-1k here). It does hint that the ConvNeXt-T **family** might beat R34 on unseen full cells, but: 4k vs 20k (no R34-PF 4k checkpoint exists; val_every 20,000, checked on gaint), 2 vs 5 seeds, PF schedule scaled; and HC's F51 gain of the same size (+0.067 AP) was n.d. on E1. F51 is a weak predictor of E1.
- If anyone wants this followed (S, not proposed ahead of SKR2 / HC2, and not to be asked of the user now (judge agrees); needs the user's OK as a new arm; it could motivate only an IN-1k ConvNeXt-T encoder-swap arm, not a foundation arm): the confound is resolved by 2 R34-PF runs on el_f8 at A8's exact 4k schedule and data root, scored by the frozen a8 scorer (~1 GPU-h total, R34 peak ~6.4 GB). Only a clear ConvNeXt-T > R34-PF-4k F51 gap would justify a 5-seed ConvNeXt-T-IN encoder-swap arm, which would carry RN50-PF's inactive risk.

## 2. Prior tries in the repo
- Track D D1 (24 Oct): frozen-probe passes (DINOv2, IN R50) did not carry to fine-tuning (handbook 18 §D1; `team_2026-10-24_go/trackD/verify_probe.md`).
- idea 8 (`idea08_foundation.md`): P8 probe runs 1-2; A8 screen protocol, wrapper review, KILL; §5 consequence: "foundation encoder closed for this thesis; no larger variant; no full arm".
- idea 6 (`idea06_hires.md`): standalone HR branch DROP (R5 2× input n.d.; stride-2 skip holds the crack signal: 92% of train crack px are a 2×2-block majority).
- PF2 RN arm: RN50-PF FAIL. So A1 repeats A8 in its components and idea 6 in its HR branch.

## 3. Literature (R)
- Dual / side-branch use of frozen foundation features for dense prediction: Side Adapter Network, doi:10.1109/cvpr52729.2023.00288; Dino U-Net, doi:10.1007/978-3-032-38082-1_10; Dino-NestedUNet (DINOv3 + nested dense decoder), arxiv:2605.00894; cloud segmentation with adapted VFMs, doi:10.1109/tgrs.2025.3597410; crack segmentation with a fine-tuned VFM, doi:10.1016/j.conbuildmat.2024.136573.
- Already in idea 8 (judge-checked): Rein (doi:10.1109/cvpr52733.2024.02704) DG gains with frozen / LoRA VFMs on urban scenes; DINOv3 T15 linear-probe advantage over supervised ConvNeXt-T (why a probe favours SSL features).
- S: all report gains on in-domain or synthetic-to-real benchmarks with large objects; none tests 1-3 px structures under an unseen-panel shift with a PF-preserved CNN baseline. Abstracts only; no full text fetched.

## 4. Cost (if run anyway)
- Dev: R34-PF + frozen DINOv3 ConvNeXt-T side branch, per-scale 1×1 projection + gate into the U-Net++ skips: ~1.5-2 days (builder) + CPU identity (branch off = house) + equivalence on DINOv3 weights (already on gaint, route B).
- GPU: A8 alone peaked 9,254 MiB at 2.31 steps/s; R34 + frozen ConvNeXt-T forward ≈ 9-11 GB (S), gate ~13 GB → 1 lane beside other jobs (budget 32.6 − 5.9 finllm − 2 floor = 24.7 GB). 5 runs × 20k ≈ 2.5-3 h each ≈ 13-15 GPU-h, ~3 days wall if it runs alone in 1-2 lanes.

## 5. Expected effect (S)
- Test: n.d.; risk to inactive (every encoder change so far, RN50-PF, A8, A8c at 4k, cost inactive).
- E1: crack recall 0 to +0.02. The A8 screen showed no F51 gain from DINOv3 features under PF; a frozen side branch adds features that rank below R50's, which already did not help E1 under PF.

## 6. Kill criterion (if ever run)
- Non-E1 screen first, A8-style (2 seeds, 4k): two-branch − SUP100-PF-4k F51 AP module-bootstrap LB > 0 and H36 / F51 FA within 1.5× → else KILL. Only then a 5-seed arm with E1 co-primaries.

## 7. Protocol sketch
- None. DROP. The idea-8 closure (§5 of protocol_A8screen, fixed before the screen) covers A1's foundation part; the HR-branch part is idea 6's DROP.

## 8. Files
| file | md5 |
|---|---|
| `scripts/arch/a1_cnx_vs_r34.py` | 5ff50009 |
| `ideas/arch_out/a1_cnx_vs_r34.txt` | ddf9cc95 |

## judge verdict (2026-11-02 11:43 IST; report md5 d3aea620 as reviewed)
**Verdict: DROP. Agreed.** A1 = the A8 screen plus a hard freeze plus gated fusion. The idea-8 closure (protocol_A8screen §5, fixed before the screen) and idea 6's HR DROP cover it. Option (d) (R34-PF plus a frozen DINOv3 side branch) has no non-E1 support: frozen DINOv3 ConvNeXt-T F51 AP is 0.363 vs frozen IN R50's 0.444 (`idea08_foundation.md` l.196 / 219), and RN50-PF failed.

### What I checked (E)
- §1.1 matches my A8 review (verify_a8screen judge section):
  - A8 = DINOv3 ConvNeXt-T under PF;
  - the hrstem stride-2 stem feeds the 1/2 skip;
  - U-Net++ concatenates the skips;
  - A8 moved ~10x more than A8c.
- §1.3 F51 AP equals my own recomputes: A8 0.5448, A8c 0.5691 (`judge/out/a8_recompute_out.txt`); SUPPF s5-9 0.4702, HC 0.5371 (`judge/out/hc_f51.txt`).

### §1.3 confound wording (your question): not strong enough yet. Add these
1. **Architecture, not only training length.**
   - A8 / A8c run el_f8's `hrstem_unetpp` (extra stride-2 HR stem, timm ConvNeXt) with PF freeze / ramp 200 / 200, on el_f8 code.
   - R34-PF is smp U-Net++ with PF 1,000 / 1,000, on e544133.
   - "4k vs 20k" is one of several differences.
2. **F51 AP is 76% one cell** (CSIR_00073). A8c's seed-1 0.602 is mostly that cell (judge, A8 §2). The ConvNeXt-T "lead" is a 2-seed, one-cell measurement.
3. **The inactive cost moves the other way and is as large:** val inactive at b_rel 0.408 (A8c) vs 0.508 (R34-PF 20k).
4. **It is post hoc and cross-protocol.** The hypothesis "the ConvNeXt-T family beats R34 on unseen full cells" came from looking at already-opened screens. Label it hypothesis-generating only.

With these, the 2-run R34-PF-at-A8's-4k-schedule de-confounder (~1 GPU-h) is a fair *optional* item. But it can only motivate an IN-1k ConvNeXt-T encoder-swap arm (not foundation), and that arm would carry the encoder-swap inactive risk seen in RN50-PF, A8 and A8c. I rank it below SKR2 / HC2 and would not ask the user for it now.
