# R5 results: internal resolution ×2 (input 1024 bilinear, logits pooled to 512), 100% labels

MD, 25 Oct 2026. Status: **draft for MC's recompute.**
Protocol: `protocol_r5.md` (APPROVED). Runs `m_r5_up2_s0..4`, cv02 `el_mt5` (`1be64e1`), `=mq5`: s0/s1 on GPU 3, s2/s3 on GPU 6, s4 on GPU 2. 24 Oct 19:17 IST to 25 Oct 03:41 IST. All rc = 0, step 20,000.
Files: `r5/m_r5_up2_s*.json` (MD5 = cv02, `r5/md5_cv02.txt`), `r5/*.stdout`, `r5/r5_tables.txt`.
Comparator: SUP100. This is Track M test opening no. 6.

## Verdict
**R5 is n.d.** on all four primaries in both cell sets; none is worse. **Val inclusion: EXCLUDE.**

| set | crack IoU Δ (thr) | inactive IoU Δ (thr) | relF1@2 Δ (thr) | mIoU_rob Δ (thr) |
|---|---|---|---|---|
| all 50 | +0.0303 (0.0897) | −0.0025 (0.0221) | +0.0464 (0.1212) | −0.0011 (0.0260) |
| without noisy | −0.0046 (0.0100) | −0.0036 (0.0216) | −0.0012 (0.0100) | −0.0113 (0.0140) |
| val | +0.0011 (0.0100) | +0.0389 (0.0500) | +0.0018 (0.0100) | +0.0073 (0.0100) |

- **Bootstrap, without noisy:** mIoU_rob −0.0113 [−0.0216, +0.0000], P(Δ>0) 0.03. Close to a cell-robust loss, though the seed rule says n.d. (thr 0.0140). The loss is on border, material, frame_edge and edge_dark.
- **All 50:** again no seed fails on the noisy cell (crack px 591 / 0 / 0 / 124 / 0).
- **Width flags:** none.

## Named secondaries (MC)
- **p(crack) < 0.001 share of GT crack** (the confident miss this rung targets):
  - test 0.189 → **0.208** (without noisy 0.184 → 0.201);
  - ext 0.704 → 0.687.
  - On test, ×2 resolution makes confident misses slightly more common, not less.
- **Crack recall** 0.642 → 0.630; relR@2 0.830 → 0.831; component recall 0.798 → 0.804 (without noisy).
- **Per source (crack IoU):** BMRK 0.379 → 0.379, ARTS 0.456 → 0.472, CFVS 0.522 → 0.513, CSIR without noisy 0.475 → 0.473. BMRK AP 0.462 → 0.462.
- **E1 ext** (never used for selection): crack 0.148 → 0.167, **recall 0.178 → 0.204**, inactive 0.064 → 0.082, mIoU 0.411 → 0.433. Same without `CSIR_00300_r25_c1`.

## Compute (the claim is "at about 4× compute")
- 591.9 vs 148.0 GFLOPs per forward at 512 (×4.0).
- Wall time 8.3 h per run at 2 per GPU (about 4.2 GPU-h), and 4.0 h for s4 almost alone (about 4 GPU-h), vs about 1.1 GPU-h for R34. Steps matched, FLOPs not.
- Grad norm 1.69 (clip rate 0.24) vs 1.80 (0.25).

## Reading
- Internal ×2 resolution does not help in-split crack at 100% labels. Whether more compute alone would help (R6, a longer schedule) stays untested.
- Like ResNet-50, R5 raises unseen-module crack recall (+0.026). Two bigger-compute rungs both helping E1 crack is a post hoc pattern worth a deployment-focused protocol, not a claim.

## Consequence for the final (locked protocol)
None of R3 Part B, R5 or R2c passes val inclusion, so the recipe is SUP100. **FINAL = the R1 model** if D1/D2 repeat; contrast 2 (FINAL − R1 model) is dropped (F2). The final scoring adds the one remaining item, **E1 for the final model**, along with the full final report.
