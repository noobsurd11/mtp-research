# A2: style-invariant early layers (IBN-Net: instance norm in early encoder stages) (Om, 1 Nov)

arch, 2 Nov 2026. Tags: E measured (file), R literature (Research MCP id), S judgement. CPU / read-only. No test or E1 file opened. No weights downloaded.

## 0. Verdict (proposed): DROP as an arm now (premise contradicted on non-E1 data). Weights exist; cost below if the user wants it anyway.
- Om's rationale: "new panels differ mainly in brightness / contrast / texture (style); IN removes per-image style". Our data say otherwise:
  1. Content brightness of E1 matches train (AUROC 0.52); the "brighter" signal is the white letterbox (idea 2, judge-reproduced). The house jitter already reaches 96-100% of E1 cells in content mean / sd (idea 11).
  2. Where E1 differs (contrast sd 27 vs 37; histogram shape: 60% of E1 half-cuts outside train's p97.5), Hanifi `_rf` differs from train **as much** (multivariate AUROC 0.81 vs E1 0.78), yet the models do well on its unseen-module full cells (F51 relF1@2 0.84-0.86, near val). Appearance distance does not predict failure.
  3. Within E1, recall follows the content stratum (half-cut without scuff 0.86 vs half-cut + scuff 0.16 at similar brightness), not brightness (ρ −0.03) or faintness (ρ −0.06).
  4. The nearest direct test, per-cell affine normalisation of the input at test time (an instance norm at layer 0), lowered val relF1@2 by 0.019-0.025 and F51 moved −0.03 … +0.016; histogram matching was worse (idea 2 §3). The models use absolute grey level as a cue.
  5. Inactive needs absolute low-frequency intensity: raw intensity separates inactive from background at AUROC 0.946, a high-pass of it 0.862 (idea 4 §1.2). IN removes per-image channel means early; IBN keeps half the channels on BN, which limits but does not remove that risk. Inactive is the class that broke for RN50-PF and leans down for HC.
- S: A2 targets a shift (style) that is not the measured failure (scuff + half-cut content). Expected E1 gain ≈ 0, with an inactive risk.

## 1. Premise check (E, from existing judge-checked reports; no new data read)
| claim | value | source |
|---|---|---|
| E1 content brightness vs train | median 143 vs 138, AUROC 0.52 | `idea02_intensity.md` §2.1-2.2 (judge reproduced) |
| whole-image "brighter" | letterbox: 55 / 58 E1 half-cuts, 0 elsewhere | idea 2 §2.1; idea 11 §2.3 |
| style distance from train, multivariate | E1 0.78; `_rf` 0.81 (F51 0.76) | idea 2 §2.2 |
| model on `_rf` F51 (unseen modules, full) | relF1@2 0.84-0.86 | idea 2 §1 item 3 |
| histogram shape outside train | E1 half-cut 60%; pool / Hanifi half 12-13% | idea 11 §2.2 |
| test-time per-cell affine (cellz) | val relF1@2 −0.025 (FINAL) / −0.019 (SUPPF); F51 +0.006 / +0.016 | idea 2 §3 table |
| E1 recall vs brightness / faintness | ρ −0.03 / −0.06 | idea 2 §2.4 |
| inactive vs background, raw vs high-pass | AUROC 0.946 vs 0.862 | idea 4 §1.2 |
- What the data do not test: training WITH an instance-normalised path (a test-time mapping on models trained without it is weaker evidence, idea 2 §6). That is the only open part of A2, and items 2-3 above remove its premise.

### 1.1 Do pretrained IBN-a ResNet-34 weights exist? (cost only; not fetched)
- **Yes.** The official IBN-Net repo (XingangPan/IBN-Net, README results table) lists ResNet-34 IBN-a with a pre-trained model, `releases/download/v1.0/resnet34_ibn_a-94bc1577.pth`; ImageNet top-1 / top-5 error 25.78 / 8.19 vs their ResNet-34 re-implementation 26.70 / 8.58 (= torchvision's R34, which the house uses via smp). Also ResNet-18 IBN-a. Size not shown; S: ~85-90 MB (21.8M fp32 params). torch.hub documents only `resnet50_ibn_a`; the R34 file is a direct release asset. (Web lookup, not Research MCP; 2 Nov.)
- Not on gaint (searched `/home/noob` for `*ibn*`, torch hub cache: none). timm on gaint has no `*ibn*` model. Downloading model weights needs the user's OK (README rule).

### 1.2 How IN interacts with PF (S, with E on PF)
- PF (handbook 19 §0, E): encoder frozen steps 0-999 **with BN in train mode** (running stats re-estimated on EL during the freeze), then encoder lr ramps to 0.1× base, wd 0.
- **IN inserted into the house torchvision R34 (no IBN weights):** the frozen convs after each new IN see a different input distribution from step 0, so PF would be preserving weights that no longer compute their pretrained features. That defeats PF's mechanism (preserve layer3 / 4, cos 0.93-0.96). Not coherent.
- **IBN-a R34 weights under PF:** coherent. IN layers have no running stats and only affine params; the BN half re-estimates stats during the freeze as now. It is then one change: the encoder init + normalisation (an encoder swap, like RN50-PF / A8).
- **IN only outside the encoder** (decoder skips): keeps PF intact, but removes style only after layers 1-4 have computed on it; weakest form, no literature support for it here.

## 2. Prior tries in the repo
- None with IN / IBN / whitening (grep over `research/` for IBN, InstanceNorm, instance norm: 0 hits outside Om's list).
- Related: idea 2 (normalisation premise, DROP), idea 11 (appearance augmentation, DROP as an arm; geometry → idea 5), P6 (blur / noise dropped as crack-erasing), house jitter ±0.2 at p 0.4 since P6.

## 3. Literature (R)
- IBN-Net, Pan et al. 2018, doi:10.1007/978-3-030-01225-0_29 (arXiv 1807.09441): IN in shallow layers learns appearance-invariant features, BN in deep layers keeps content; GTA5 ↔ Cityscapes gains without target data.
- RobustNet (instance selective whitening), doi:10.1109/cvpr46437.2021.01141: removes only style-sensitive covariance; urban-scene DG.
- Semantic-Aware DG segmentation, doi:10.1109/cvpr52688.2022.00262; WildNet, doi:10.1109/cvpr52688.2022.00970.
- Schwonberg et al. 2023, doi:10.1109/iv55152.2023.10186752 (also in idea 11): DG gains depend on the shift type.
- S: every benchmark here is a style shift (synthetic → real, weather, illumination) with the same object classes. Our measured shift is content (scuff context, half-cut layout). Full text not fetched (no shortlist case).

## 4. Cost (if the user wants it anyway)
- Weights: one ~85-90 MB file (user OK needed). Dev ~0.5-1 day (builder): an smp-compatible encoder (R34 layout unchanged; `bn1` of BasicBlocks in layers 1-3 → IBN-a; first conv summed over RGB as smp does), key remap + ImageNet-logit equivalence vs the reference implementation, CPU identity of the rest of the model.
- GPU: one 5-seed arm on SUP100-PF opts, 20k steps: ≈ 12.5 lane-h (R34 peak ~6.4 GB; IN adds negligible memory), 2-3 lanes beside finllm.

## 5. Expected effect (S)
- Test: n.d.; inactive −0.01 to −0.03 risk.
- E1: crack relF1@2 0 to +0.01; inactive unpredictable (letterboxed half-cuts are where absolute intensity differs most).

## 6. Kill criterion (if run)
- Non-E1 first: val crack relF1@2 not lower by > 0.01 AND F51 crack AP module-bootstrap LB > 0 vs SUP100-PF, at 2 seeds 4k (A8-style screen), else KILL. Then the house E1 co-primaries with a test-inactive guard (as protocol_SKR2_HC2 G1).

## 7. Protocol sketch
- None now (DROP). Revival condition (S): a non-E1 set whose failure tracks appearance (e.g. a new panel batch where F51-like cells fail and a style statistic separates the failures). None exists in our data.

## judge verdict (2026-11-02 11:43 IST; report md5 1297ec66 as reviewed)
**Verdict: DROP. Agreed.** The style premise is contradicted on non-E1 data, and idea 2's facts carry over: I reproduced them on 31 Oct (`ideas/idea02_intensity.md` judge section). Content brightness matches train (AUROC 0.52), appearance distance does not predict failure (`_rf` is as far from train as E1, yet F51 holds up), and per-cell input normalisation at test time cost val relF1@2 0.019 / 0.025.

### Notes (S)
- **"Test-time affine ≈ IN at layer 0" is an analogy, not an equivalence.** IN sits after conv1 and has learned affine params. arch says "nearest direct test", which is right; keep that wording. The decision does not depend on it: the premise fails on items 2-3 alone.
- **PF interaction (§1.2) is correct.** IN without IBN weights breaks what PF preserves. With IBN-a weights it is an encoder swap: download (user OK), remap and equivalence test, plus the inactive risk every encoder change has shown. Not worth it with no premise.
- **The weights location came from a web lookup** (official README asset), not Research MCP. That is fine for a file location, since it is not a citation; it is tagged as such.
