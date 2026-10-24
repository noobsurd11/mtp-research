# Frozen-encoder probe: independent recompute by C (24 Oct 2026)

**Verdict: CONFIRMED.** The locked rule passes for ImageNet ResNet-50 (test and pool) and for ConvNeXt-T (test only, "fragile").

## Checks
- My own binned AP (descending bins, step-wise precision × Δrecall) on `results/trackD_probe/hists.npz`, with BMRK cells taken from `stems_test` / `stems_pool`.
- **BMRK test crack AP:**
  - A5c 0.150 (5 seeds: 0.165, 0.150, 0.141, 0.168, 0.126);
  - A5c+LA 0.165, so R = 0.165 and the bar is 0.215;
  - rn50_imagenet 0.268 / 0.268 (pass, each seed);
  - convnext_t 0.278 / 0.271 (pass);
  - rn34_imagenet 0.185 / 0.187 (fail);
  - dinov2 0.122 / 0.133 (fail);
  - A5c's own encoder probed 0.171 / 0.171;
  - random 0.045 / 0.047.
- **Pool BMRK AP:** A5c+LA 0.235, bar 0.285. rn50 0.322 / 0.322 passes; convnext 0.282 / 0.278 (mean 0.280) does not.
- **All-source test AP:** A5c τ 0 0.287 and τ 1 0.303, matching `la_sa_test.json`.
- **Recall at matched precision** (BMRK test, P* 0.58), spot check: rn50 0.020 / 0.023, convnext 0.002 / 0.002. Matches `probe_results.md` §2.

## What the pass means (reading, agreed with DX's §3)
- **What it shows:** frozen ImageNet ResNet-50 / ConvNeXt-T stride-4/8 features rank BMRK crack better than the 5% fine-tuned U-Net++ does, with the same 23 labelled cells. Our ResNet-34 init does not, and neither does A5c's own fine-tuned encoder. The bigger pretrained encoder carries information our model throws away.
- **The limit:** the separation is at low precision. At A5c+LA's precision the probes recall 0.02 of BMRK crack, against A5c's 0.21. The pass is a ranking signal, not evidence of better masks.
- **Consequence per the locked rule:** the encoder/distillation route stays open, and MIM (SYNTHESIS direction 7) is gated out. This rests on a low-precision ranking pass. MIM was ranked 7th anyway; if Track M's fine-tuned ResNet-50/ConvNeXt steps fail on BMRK, MIM can be reopened with its own protocol.
- **For Track M:** test a fine-tuned ResNet-50 or ConvNeXt encoder with BMRK crack AP and recall as named secondary metrics. The probes are worse than A5c on CSIR and ARTS, so watch those sources for regressions.
- **The 40 components:** best relaxed recall 0.097 (rn50 at argmax), 0 of 40 at ≥ 0.5. The SYNTHESIS bound stands.
