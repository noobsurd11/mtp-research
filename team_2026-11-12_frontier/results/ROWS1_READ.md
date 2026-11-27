# Benchmark rows tranche 1 and the gaint four-seed baseline (lead, 15 Nov 2026, 12:46 IST)

Tools: reviewed merged tree `bench_wt_w2` c57508e (`bench_read_w1.py`), run 15 Nov 09:55 to 10:06 (`harness/w1read/run_read_rows1.sh`, `run_read_w1g4.sh`). Tables: `results/rows1_read/read.txt`, `results/w1g4_read/read.txt`. Split cv5v2, out-of-fold predictions pooled over all 532 train + val cells, label set v1.1, 20,000 steps, batch 8, 512 px, every row under the house recipe with the encoder-preserving fine-tune (PF) unless stated. No sealed cell is in any number. E = measured, S = judgement.

## 1. Rows on cv02 (E; mean over seeds; rows have seeds 5 and 6, PF has 5 seeds)
| Row | Architecture | Output stride | Strict crack IoU | Crack relF1@2 | relP@2 / relR@2 | Inactive IoU | mIoU-R13 | Width ratio |
|---|---|---|---|---|---|---|---|---|
| PF (comparator) | U-Net++ / ResNet-34 | 1 | 0.365 | 0.844 | 0.894 / 0.799 | 0.503 | 0.612 | 1.00 |
| HOUSE | U-Net++ / ResNet-34, plain fine-tune | 1 | 0.382 | 0.850 | 0.897 / 0.807 | 0.522 | 0.609 | 1.11 |
| unet_r34_pf | U-Net / ResNet-34 | 1 | 0.364 | 0.843 | 0.896 / 0.795 | 0.522 | 0.612 | 1.00 |
| hanifi_vgg16_unet_pf | U-Net / VGG-16 (Hanifi et al.) | 1 | 0.349 | 0.838 | 0.882 / 0.798 | 0.498 | 0.610 | 0.96 |
| dlv3p_r34_pf | DeepLabV3+ / ResNet-34 | 4 | 0.354 | 0.835 | 0.884 / 0.791 | 0.478 | 0.609 | 1.21 |
| ucf_dlv3_r50_pf | DeepLabV3 / ResNet-50 (UCF-EL's model) | 8 | 0.287 | 0.767 | 0.809 / 0.729 | 0.497 | 0.574 | 1.23 |
| pratt_dlv3p_wcec | DeepLabV3+ / ResNet-34, the paper's weighted CE | 4 | 0.258 | 0.751 | 0.648 / 0.892 | 0.506 | 0.604 | 3.05 |

## 2. Contrasts against PF (E; row minus PF, two-stage group bootstrap 95% CI; M on cv02 = 0.010, inactive 0.050)
| Row | Strict crack IoU, argmax | Strict crack IoU, width-matched | relF1@2, argmax | relF1@2, width-matched | mIoU-R13, argmax |
|---|---|---|---|---|---|
| unet_r34_pf | -0.0004 [-0.0078, +0.0078] | 0.0000 [-0.0076, +0.0088] | -0.0016 [-0.0110, +0.0073] | -0.0014 [-0.0111, +0.0080] | 0.0000 [-0.0064, +0.0067] |
| hanifi_vgg16_unet_pf | -0.0158 [-0.0247, -0.0069] | -0.0134 [-0.0244, -0.0040] | -0.0064 [-0.0189, +0.0042] | -0.0066 [-0.0232, +0.0055] | -0.0027 [-0.0097, +0.0045] |
| dlv3p_r34_pf | -0.0105 [-0.0244, +0.0041] | -0.0242 [-0.0384, -0.0098] | -0.0093 [-0.0204, +0.0019] | -0.0199 [-0.0325, -0.0086] | -0.0030 [-0.0116, +0.0062] |
| ucf_dlv3_r50_pf | -0.0782 [-0.0944, -0.0587] | -0.0967 [-0.1121, -0.0787] | -0.0773 [-0.0892, -0.0594] | -0.0984 [-0.1113, -0.0799] | -0.0381 [-0.0455, -0.0296] |
| pratt_dlv3p_wcec | -0.1066 [-0.1282, -0.0842] | -0.0691 [-0.0851, -0.0517] | -0.0932 [-0.1113, -0.0774] | -0.0899 [-0.1130, -0.0693] | -0.0084 [-0.0161, +0.0012] |
Inactive IoU: no row is separated from PF (all intervals span 0; the largest point value is +0.020 for unet_r34_pf, inside M 0.050).

## 3. Reading (S)
- **The decoder does not matter here.** Plain U-Net equals U-Net++ on every metric (crack IoU 0.0000 width-matched). The nested decoder buys nothing on this data.
- **Output stride decides thin-crack quality.** Stride 4 costs 0.02 strict IoU and 0.02 relF1@2 once width is matched (DeepLabV3+ draws cracks 21% wider at argmax, which hides half of the loss); stride 8 costs about 0.08 to 0.10 on both. This is the pattern stage A's head-resolution probe predicted ("head binds"). Any stride-4 or stride-8 row in the table is printed with its stride.
- **The models of the EL papers sit well below the baseline under equal training:** UCF-EL's DeepLabV3 / ResNet-50 at 0.287 / 0.767, Pratt's weighted cross-entropy at 0.258 / 0.751 (its class weights make cracks three times too wide: precision 0.65, recall 0.89; width-matched it is still 0.07 below). Hanifi's VGG-16 U-Net is close: 0.013 to 0.016 below on strict IoU, not separated on relF1@2.
- **Nothing in this tranche beats PF or HOUSE.** The strongest in-distribution model so far is still the house recipe without PF (+0.011 to +0.017 strict IoU over PF).
- Limits: 2 seeds per row; one machine; pool cells only (no unseen-module statement); ucf row uses ImageNet weights (not COCO) and no auxiliary head, pratt row uses the house augmentation with the paper's loss (cards state each deviation).

## 4. gaint four-seed baseline and margin (E; W1-G + W1-G2, PF, seeds 5 to 8)
Strict crack IoU 0.365 (sd 0.004), relF1@2 0.844 (0.004), inactive IoU 0.503 (0.008), mIoU-R13 0.613 (0.002), relP@2 0.896, relR@2 0.799, width 1.009.
A/A {5, 6} against {7, 8}: crack IoU +0.0044 [-0.0023, +0.0123] SE 0.0038; relF1@2 +0.0052 [-0.0011, +0.0111] SE 0.0031; mIoU-R13 +0.0025 [-0.0036, +0.0088] SE 0.0032; inactive IoU +0.0090 [-0.0419, +0.0685] SE 0.0271.
**M on gaint = 0.010 for crack IoU, relF1@2 and mIoU-R13; 0.011 for relP@2 and relR@2; 0.054 for inactive IoU.** Equal to cv02's margins; the two machines' baselines agree to the third decimal (0.365 / 0.844 / 0.503 / 0.612 to 0.613). Wave 2a arms (gaint) are read against these four seeds with this M.
