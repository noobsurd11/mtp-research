# A5: long-range context along the cell (axial / row-column attention or line-scan block) (Om, 1 Nov; "second round")

arch, 2 Nov 2026. Lighter treatment as asked. Tags: E measured (file), R literature (Research MCP id), S judgement. No new data read beyond `arch_A4.md`'s val / `_rf` readout; no test or E1 file opened.

## 0. Verdict (proposed): DROP for now (lowest rank of A1-A6).
- Premise: "cracks span whole cells and cross busbars; the local receptive field breaks them". Against it:
  1. **The receptive field is already cell-sized.** ResNet-34's theoretical receptive field is 547 px at layer3 and 899 px at layer4 (S: computed from the layer list; a 512-px input is one cell); U-Net++ decodes from those stages. The effective field is smaller, but the encoder can see across a cell.
  2. **Broken cracks are a small share of what is lost** (`arch_A4.md` §1, E): fragments are 7% of val GT components (4.7% of GT px), ≤ 5% on F51 (≤ 1.2% of px); whole-component misses dominate on F51 (9% of px) and E1 (62% of components, already-opened).
  3. **Busbars are not where cracks are lost**: missed crack px within 3 px of busbar / ribbon / spacing 11-12% on H36 and 15-19% on val / F51 vs 12-13% of all crack px (idea 4 §1.4; `arch_A3.md` §1.2). A crossing-the-busbar mechanism has ~1-6% of FN px to recover.
- S: long-range context could in principle help the scuff decision (is this dark streak a scuff or a crack?), which is the E1 failure; but no data or literature here shows axial attention separating scuff from crack, and scuff is broad and non-periodic (idea 4 §1.3: crack vs scuff ≤ 0.45 AUROC on every structure channel).

## 1. Prior tries in the repo (E)
- Phase 0 SA U-Net++: its "self-attention" was an elementwise sigmoid gate (`sigmoid(Q+K)*V`), no spatial mixing; the corrected rerun showed no effect (test 0.3399 ± 0.0104 vs 0.3435 ± 0.0329) (handbook 04 glossary "SA-UNet++", 06 §phase 0).
- Handbook 06 / 15 list "coarse non-local or axial / strip attention" as stage-2 ideas, never run.
- Track M design: SegFormer / Mask2Former not proposed (1/4-resolution decoders vs 1-2 px cracks; ViT patch features weak on crack, DINOv2 AP 0.18) (`team_2026-10-24_go/trackM/design.md`).
- idea 3 (neighbour reference, PARKED): the one non-local input tested (a comparison ~120-256 px away); in a linear probe its gain was mostly a busbar / gap indicator the CNN already has, and idea 3 says only a training arm could settle it (§1.6-1.7 there). Never trained.
- Not a repeat: no real long-range attention block has been trained here.

## 2. Literature (R)
- CCNet, criss-cross attention, doi:10.1109/iccv.2019.00069 (TPAMI doi:10.1109/tpami.2020.3007032): row + column attention, full-image context in two passes.
- Strip pooling, doi:10.1109/cvpr42600.2020.00406: long, narrow pooling kernels for elongated structures.
- SegFormer, arxiv:2105.15203; SETR, doi:10.1109/cvpr46437.2021.00681.
- S: gains are reported on scene parsing with large objects; I found no crack / EL result with a matched baseline at our resolution. Abstracts only.

## 3. Cost
- Dev ~1-1.5 days: a criss-cross or strip-pooling block at the 1/16 or 1/32 bottleneck (16×16 or 32×32 tokens at 512 px; attention cost negligible there), CPU identity (block as identity = house).
- At 1/4 or 1/2 resolution (where 2-3 px cracks live): 128² / 256² positions, row + column attention ~2 × N^1.5 terms; memory +2-4 GB per run (S), one fewer lane.
- GPU: one 5-seed arm ≈ 12.5-15 lane-h (bottleneck version, peak ~7 GB), 2-3 lanes beside finllm (24.7 GB usable).

## 4. Expected effect (S)
- Test: n.d. E1: crack 0 to +0.01; the scuff decision is the only plausible route and it is untested.

## 5. Kill criterion
- Om's: no component recall / E1 crack gain. Non-E1 first: B5 component recall and val partial-component share (A4 readout) vs SUP100-PF at 2 seeds 4k; no gain → KILL.

## 6. Protocol sketch
- None now. Revival (S): if an explicit scuff-vs-crack context failure is shown on non-E1 data (e.g. Hanifi scuff cells: crack FP on GT scuff falls when a model sees the whole streak), test the bottleneck strip-pooling block as one arm. Rank below A4.

## judge verdict (2026-11-02 11:43 IST; report md5 c309af33 as reviewed)
**Verdict: DROP for now. Agreed; lowest rank of A1-A6.**

### What I checked
- **(E, own arithmetic) R34 theoretical receptive field:**
  - conv1 7 + maxpool → 11; layer1 +48 → 59;
  - layer2 +8 +112 → 179; layer3 +16 +352 → **547**; layer4 +32 +320 → **899** px.
  - **Match.** The effective field is far smaller (S), as you note.
- **(E, via A4 check)** Fragment share is small non-E1; whole-component misses dominate.
- **(E, via A3)** FN are not enriched near busbars on H36.

### Note (S)
The one plausible route, scuff-vs-crack context, is untested and has no non-E1 handle yet. Your revival condition (show a scuff / crack context failure on non-E1 data first) is the right gate.
