# Review: idea-8 wrapper `hrstem_unetpp` (found, el_f8 063f74f0)

builder, 31 Oct 2026, at coach's request, before any GPU use. Reviewed: `git -C /home/noob/work/el_f8 diff e544133 063f74f0` (4 files, +300 / −1). I read the code and re-ran the checks myself (gaint CPU, `CUDA_VISIBLE_DEVICES=""`, nice 19). Tags: E = measured, S = judgement.

## Verdict
**No blocking issue.** The wrapper is correct for the A8 screen. One should-fix before the A8 GPU runs (the LayerNorm coverage of the PF validity script), two items for the GPU smoke, three minor ones.

## What I verified independently (E)
- **Identity.** I ran my harness (`identity_cpu.py`, md5 962379a6), 5 real steps, at el_f8 with `model.name=smp_unetpp` against my own e544133-export records (A house, C PF). Result: house **IDENTICAL**, PF **IDENTICAL** (loss repr, lr, sha of all params and buffers, fixed-batch logits). Records: gaint `builder_scratch/idchk_f8/`.
- **Decoder and head = the house's.**
  - smp 0.5.0 `UnetPlusPlus` defaults are decoder (256, 128, 64, 32, 16), `batchnorm`, no attention, `nearest`, `center=False` for non-VGG encoders, head kernel 3. The wrapper passes exactly these.
  - Built side by side: 11 decoder blocks in both, centre `Identity` in both, block `x_0_0` = [Conv2dReLU, Attention(identity), Conv2dReLU, Attention].
  - smp drops `features[0]` (the input), so passing `[x, hr_stem(x), *stages]` with `encoder_channels=[in, 64, *chs]` follows smp's convention.
- **512 px (the training size; the tests use 128).** ConvNeXt-T (torchvision weights) and SAM2 Hiera-T (timm file):
  - features (96, 192, 384, 768) at strides 4 / 8 / 16 / 32;
  - output (2, 24, 512, 512), finite;
  - **0 parameters without a gradient for both** (Hiera's gradient completeness was not in the tests);
  - about 8 s per 2 × 512 forward + backward on CPU.
- **Init independent of the weight source.** Same seed, random backbone vs loaded weights (torchvision path for ConvNeXt, timm file for Hiera): `hr_stem` / decoder / head inits are identical, and so is the global RNG state after the build. A8 (DINOv3) vs A8c (IN-1k) therefore differ only in the encoder weights, provided the architecture is the same.
- **SAM2 files present** with the md5s protocol_A8screen records: timm `c453c074`, `sam2.1_hiera_tiny.pt` `6aa6761c`.

## Answers to found's three questions
1. **torchvision → timm remap: correct.**
   - The mapping: stem conv / LayerNorm2d → `stem.0/.1`; `features.{2,4,6}` (LN2d, conv) → `stages.{1,2,3}.downsample.0/.1`; CNBlock `block.0/2/3/5` → `conv_dw / norm / mlp.fc1 / mlp.fc2`; `layer_scale (C,1,1)` → `gamma (C,)`.
   - The only missing keys are `head.*`. found's equivalence test (timm stage outputs = torchvision `features[1,3,5,7]` within 1e-4) is the right proof.
2. **`forward_intermediates` feature path: correct.**
   - ConvNeXt: the stage outputs carry no final norm (`prune_norm`), as torchvision's features do.
   - Hiera returns NCHW at strides 4-32 at 512 px (window padding and pos-embed interpolation work).
   - `head = Identity` leaves no dangling tensors (0 params without a gradient).
3. **Stem init order: fine.**
   - `initialize_decoder(hr_stem)` runs last: kaiming-uniform (fan_in, relu) on both convs (no bias), BN 1 / 0, the same scheme smp uses for its decoder. Deterministic per seed.
   - The backbone's random init consumes the global RNG before the stem / decoder / head, so those inits depend on the backbone *architecture*, not on its weights (checked above).

## Should fix before A8's GPU runs
1. **`reports/enc_cosine_hr.py` misses 4 of ConvNeXt's 22 LayerNorm weights and all 18 layer-scale vectors (E).**
   - The 1-D selector requires `"norm"` in the key, so these are never counted: `encoder.stem.1.weight`, `encoder.stages.{1,2,3}.downsample.0.weight`.
   - The `gamma` vectors (1-D, no "norm") are skipped entirely.
   - Coach asked that LayerNorm be covered in the PF validity check.
   - Fix: classify 1-D tensors by their owning module (`isinstance(module, (nn.LayerNorm, timm LayerNorm2d))`, or the explicit names), and report `gamma` cosine per stage separately. Hiera's `norm1/norm2` are caught already.

## For the GPU smoke (runner)
2. **Determinism of the Hiera path.**
   - Hiera uses `F.scaled_dot_product_attention`. Its CUDA backward (efficient / flash kernels) can be non-deterministic.
   - The house relies on bit-identical reruns and resumes: protocol_100 v1.2 counted resumed runs as-is after the gaint reboot.
   - Smoke: two identical 200-step A8h runs, compare loss lines. If they differ, disclose it, and do not use resume-identity for Hiera arms (or force the math SDPA backend, at a speed cost).
   - ConvNeXt (depthwise conv, LayerNorm) has no such issue beyond the house's.
3. **DINOv3 ConvNeXt-T weights (A8's main arm) are not fetched, so their key format is unverified.**
   - timm-hub format (e.g. `convnext_tiny.dinov3_*`): the `timm` path loads strictly. Good.
   - Meta's original ConvNeXt format (`downsample_layers.*`, `stages.N.M.dwconv / pwconv1 / pwconv2 / gamma`): neither path loads it. The `timm` path fails loudly; a third remap would be needed, with an equivalence test like the torchvision one.
   - Either way, add an output-equivalence check against the reference implementation once the file arrives, before A8 launches.

## Minor
4. **Scorers reload the backbone file.** m0_audit sets `encoder_weights: None` to skip pretrained weights at scoring; `hrstem_unetpp` ignores that key and reloads `backbone_weights` on every scoring build (then the checkpoint overwrites it). Harmless, but scoring then depends on the weights file staying at that path. Suggest treating `encoder_weights: None` as "skip `backbone_weights`", or recording the dependency in the protocol.
5. **Tests at 128 px only.** Add a 512-px Hiera all-params-gradient case (I checked it passes, above).
6. **`test_house_model_unchanged_by_switch_code`** builds the same code twice, so it cannot fail. The real proof is the harness identity (re-run here, IDENTICAL). Keep it, but say what it checks.
7. **No drop-path** (timm default 0; torchvision trains ConvNeXt with 0.1). Good for determinism; state it as a design choice in the protocol.

## Not checked
- GPU memory and speed: runner's smoke.
- DINOv3 weights (not on gaint).
- DINOv2 / ViT-S paths: not in this wrapper.

## Follow-up (31 Oct, evening)
- found's **920c6695** fixes the should-fix and the minor items:
  - `enc_cosine_hr.py` classifies 1-D tensors by owning module type and asserts that none are unclassified;
  - a test checks 22 LayerNorm + 18 gamma for ConvNeXt-T;
  - a 512-px Hiera all-params-gradient test;
  - "no drop-path" is stated.
- E: `tests/test_f8_hrstem.py` at HEAD **c280e8c**: 11 passed on gaint CPU (CUDA hidden).
- **c280e8c** (explicit `model.backbone_drop_path`, coach): default 0.0 written into the run opts, so no draws. If it were ever > 0, timm's DropPath would draw from the global CUDA RNG, which `latest.pth` checkpoints, so resume stays exact; it would be its own arm change.
- **Review closed.** Smoke items (Hiera SDPA determinism; DINOv3 file equivalence) are in `ideas/idea08_runspec.md` §2b.
