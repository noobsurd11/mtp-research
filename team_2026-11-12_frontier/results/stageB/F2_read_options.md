# F2 read-tool options: score-exclude, crack-free n, OP-C class lines (stage B fix round, 15 Nov 2026)

Rulings: log.md 15 Nov 13:51 (final tables score 528 cells, the 532-cell value beside), PROTOCOL_v0.2 s3.1 and s11 items 5 and 8, REVIEW_STAGEB s4 note 2. Builder F2. Tags: E = measured, S = judgement. No sealed label or prediction read; all reads are CPU on open cv5v2 out-of-fold dumps.
Code: bench_b **fdb6a5c** (tools), **8f9178b** (same-cell matcher; separate file SAMECELL_AUDIT.md). Tests: tests/test_bench_bfix2.py.

## 1. What changed in the tools
- `--score-exclude FILE` in scripts/bench_read_w1.py, bench_src_calib.py, bench_dti.py, bench_d0.py and bench_classbias_read.py. FILE is a stem list or a dup_crossfold TSV (both cells of each pair). The list fails closed on a sealed or forbidden stem, and every listed stem must be in the read.
  - Default (option absent): outputs as before. E: the W1-G four-seed read (PF v1.1 seeds 5 to 8, gaint) rerun at fdb6a5c against the stored bench_reads/w1g4/read (tool c57508e): read.txt byte-equal after swapping the 8-character tool md5 in the header; read.json byte-equal after swapping `tool_md5` and `seconds` (325,821 bytes; stageBfix/F2/logs/w1g4_identity.log). The tool's own md5 and the run time are the only fields that differ, and they differ between any two runs or versions anyway.
  - With the option, the read is run a second time as if the listed cells were not in the pool: operating-point fits (OP-F, OP-W), tables, contrasts, A/A margin and frontier all use the kept cells (S: the 4 cells leak through their twins, so they should not steer a fit either; a unit test shows the kept-stem read equals the read of dumps with those cells removed). bench_read_w1 appends a section "every headline value on 528 cells beside 532 cells" to read.txt and writes the full 528-cell report to read_x528.txt (read.json key `x528`). src_calib / dti / d0 write `<tool>_x528.{json,txt}` and `<tool>_beside.txt`. bench_classbias_read appends a beside section.
- **Crack-free n.** With `--score-exclude` or an OP-C baseline, read.txt prints the guard's crack-free definition and n. The definition was already the scoring label set (see 2).
- **OP-C class lines.** When the baseline arm is an OP-C dump (manifest derivation `classbias_xfit*`), bench_read_w1 prints, per arm and operating point, gridline and splice IoU, precision, recall, their predicted px on cells without that class in GT (with the number of such cells) and the share of the class's predicted px that lands on those cells, beside mIoU-R13. ("Precision on cells without the class" is 0 by definition, so the false px and their share are what is printed.)
- Not changed (S): bench_udev_read already takes an explicit `--stems` list (a list without the 4 cells is the exclusion; the U-dev sets other than U2 do not contain them); bench_aa (A/A calibration), bench_headres, bench_ens_edge, bench_labelfree are not table reads. Say so if any of them should get the option.

## 2. Which definition of "crack-free" each number used (E)
- The guard in crossfit_op.guards (all versions since 69a60f5, the first W1-G read) counts a cell as crack-free when its GT crack px over the scored (non-ignore) px are 0, from the same masks the read scores. Every read so far used `--labels v11`, so every n was the v1.1 count.
- v1.1 count on the 532 pool cells: **303** (W1-C record caches: PF, PFV1, HOUSE each 303; cells.tsv crack_px_v11: 303). v1 (masks_escdd) count: **300** (cells.tsv crack_px_v1). The 3 cells CSIR_00176_r5_c2, ARTS_00051_r6_c2, CSIR_00117_r8_c4 have crack px in v1 that v1.1 moves to ignore (scuff), so v1.1 has 3 MORE crack-free cells than v1, not fewer.
- So "303" in W1C_READ (table row "false crack px on crack-free cells (303 cells)"), W1G_FIRST_READ ("0.5% of 303 cells") and PROTOCOL_v0.2 s5.2 is the v1.1 count and is correct for those reads. The PROTOCOL_DRAFT P532 row (303) was computed on the raw E-SCDD masks, where scuff is its own class, so it equals v1.1 for crack. The statement "303 from the v1 metadata" (PROTOCOL_v0.2 s10 item 6, s11 item 5) is the part that is wrong; nothing needs recomputing. The W1-C3 arm PFV1 (trained on v1) is also scored on v1.1, so its n is 303 too.
- On 528 cells the n is 301 (two of the 4 duplicate cells are crack-free).

## 3. Reruns with the 4 duplicate cells excluded (E; bench_b fdb6a5c; chain stageBfix/F2/run_f2.sh, 15 Nov 16:44 to 17:16)
Inputs as harness/w1read/run_read_rows1.sh and run_read_w1c.sh (same arms, regexes, labels v11, A/A PF {5,6} v {7,8}), run from bench_wt_b, fresh caches; list benchmark/splits/dup_crossfold_v1.tsv (fc89e708): ARTS_00165_r12_c5, ARTS_00166_r12_c5, CFVS_00076_r1_c1, CFVS_00082_r1_c1. Outputs: /home/noob/work/bench_reads/stageBfix/F2/{w1g4_x528, rows1_x528, w1c_x528}/ (read/read.txt with the beside section, read/read_x528.txt, table528.md; w1c_x528/{src_calib,dti,d0}/*_beside.txt). The 532-cell part of the new rows1 read equals the stored bench_reads/rows1/read in every numeric field.

### 3a. Rows tranche 1 (cv02 dumps; PF 5 seeds, the rest 2 seeds): headline 532 / 528
| arm | op | crack IoU 532 / 528 | relF1@2 | inactive IoU | mIoU-R13 |
|---|---|---|---|---|---|
| PF | OP-A | 0.3648 / 0.3646 | 0.8441 / 0.8439 | 0.5027 / 0.5027 | 0.6122 / 0.6119 |
| PF | OP-W | 0.3648 / 0.3646 | 0.8441 / 0.8439 | 0.5027 / 0.5027 | 0.6122 / 0.6119 |
| HOUSE | OP-A | 0.3821 / 0.3819 | 0.8496 / 0.8493 | 0.5217 / 0.5217 | 0.6093 / 0.6090 |
| HOUSE | OP-W | 0.3758 / 0.3755 | 0.8467 / 0.8465 | 0.5234 / 0.5234 | 0.6089 / 0.6086 |
| dlv3p_r34_pf | OP-A | 0.3543 / 0.3541 | 0.8349 / 0.8346 | 0.4779 / 0.4779 | 0.6092 / 0.6088 |
| dlv3p_r34_pf | OP-W | 0.3407 / 0.3404 | 0.8242 / 0.8239 | 0.4817 / 0.4817 | 0.6085 / 0.6081 |
| unet_r34_pf | OP-A | 0.3644 / 0.3641 | 0.8425 / 0.8422 | 0.5222 / 0.5222 | 0.6122 / 0.6118 |
| unet_r34_pf | OP-W | 0.3649 / 0.3646 | 0.8427 / 0.8424 | 0.5221 / 0.5221 | 0.6123 / 0.6119 |
| pratt_dlv3p_wcec | OP-A | 0.2582 / 0.2583 | 0.7510 / 0.7508 | 0.5063 / 0.5063 | 0.6039 / 0.6035 |
| pratt_dlv3p_wcec | OP-W | 0.2957 / 0.2956 | 0.7542 / 0.7539 | 0.5219 / 0.5219 | 0.6079 / 0.6075 |
| hanifi_vgg16_unet_pf | OP-A | 0.3491 / 0.3487 | 0.8377 / 0.8374 | 0.4979 / 0.4979 | 0.6095 / 0.6091 |
| hanifi_vgg16_unet_pf | OP-W | 0.3514 / 0.3511 | 0.8376 / 0.8373 | 0.4967 / 0.4967 | 0.6096 / 0.6092 |
| ucf_dlv3_r50_pf | OP-A | 0.2866 / 0.2864 | 0.7669 / 0.7667 | 0.4972 / 0.4972 | 0.5741 / 0.5737 |
| ucf_dlv3_r50_pf | OP-W | 0.2681 / 0.2680 | 0.7457 / 0.7455 | 0.5008 / 0.5008 | 0.5728 / 0.5724 |

Contrasts against PF, OP-A and OP-W (532 / 528), PASS* = delta >= M and interval low > 0:


| contrast | op | metric | 532: delta [95% CI] | 528: delta [95% CI] |
|---|---|---|---|---|
| HOUSE - PF | OP-A | crack_iou | +0.0173 [+0.0107, +0.0241] PASS* | +0.0173 [+0.0106, +0.0241] PASS* |
| HOUSE - PF | OP-A | relF1_2 | +0.0055 [-0.0034, +0.0135] | +0.0055 [-0.0034, +0.0135] |
| HOUSE - PF | OP-A | miou_rob | -0.0030 [-0.0102, +0.0045] | -0.0029 [-0.0102, +0.0046] |
| HOUSE - PF | OP-W | crack_iou | +0.0110 [+0.0028, +0.0187] PASS* | +0.0110 [+0.0033, +0.0188] PASS* |
| HOUSE - PF | OP-W | relF1_2 | +0.0026 [-0.0065, +0.0109] | +0.0026 [-0.0067, +0.0109] |
| HOUSE - PF | OP-W | miou_rob | -0.0033 [-0.0106, +0.0041] | -0.0033 [-0.0106, +0.0043] |
| dlv3p_r34_pf - PF | OP-A | crack_iou | -0.0105 [-0.0244, +0.0041] | -0.0105 [-0.0249, +0.0033] |
| dlv3p_r34_pf - PF | OP-A | relF1_2 | -0.0093 [-0.0204, +0.0019] | -0.0093 [-0.0199, +0.0013] |
| dlv3p_r34_pf - PF | OP-A | miou_rob | -0.0030 [-0.0116, +0.0062] | -0.0030 [-0.0119, +0.0063] |
| dlv3p_r34_pf - PF | OP-W | crack_iou | -0.0242 [-0.0384, -0.0098] | -0.0242 [-0.0389, -0.0102] |
| dlv3p_r34_pf - PF | OP-W | relF1_2 | -0.0199 [-0.0325, -0.0086] | -0.0199 [-0.0320, -0.0093] |
| dlv3p_r34_pf - PF | OP-W | miou_rob | -0.0038 [-0.0125, +0.0055] | -0.0038 [-0.0128, +0.0056] |
| unet_r34_pf - PF | OP-A | crack_iou | -0.0004 [-0.0078, +0.0078] | -0.0004 [-0.0089, +0.0082] |
| unet_r34_pf - PF | OP-A | relF1_2 | -0.0016 [-0.0110, +0.0073] | -0.0017 [-0.0118, +0.0074] |
| unet_r34_pf - PF | OP-A | miou_rob | -0.0000 [-0.0064, +0.0067] | -0.0000 [-0.0061, +0.0067] |
| unet_r34_pf - PF | OP-W | crack_iou | +0.0000 [-0.0076, +0.0088] | -0.0000 [-0.0087, +0.0088] |
| unet_r34_pf - PF | OP-W | relF1_2 | -0.0014 [-0.0111, +0.0080] | -0.0015 [-0.0119, +0.0078] |
| unet_r34_pf - PF | OP-W | miou_rob | +0.0000 [-0.0064, +0.0068] | -0.0000 [-0.0062, +0.0066] |
| pratt_dlv3p_wcec - PF | OP-A | crack_iou | -0.1066 [-0.1282, -0.0842] | -0.1063 [-0.1287, -0.0835] |
| pratt_dlv3p_wcec - PF | OP-A | relF1_2 | -0.0932 [-0.1113, -0.0774] | -0.0931 [-0.1121, -0.0773] |
| pratt_dlv3p_wcec - PF | OP-A | miou_rob | -0.0084 [-0.0161, +0.0012] | -0.0084 [-0.0163, +0.0007] |
| pratt_dlv3p_wcec - PF | OP-W | crack_iou | -0.0691 [-0.0851, -0.0517] | -0.0690 [-0.0862, -0.0512] |
| pratt_dlv3p_wcec - PF | OP-W | relF1_2 | -0.0899 [-0.1130, -0.0693] | -0.0900 [-0.1146, -0.0696] |
| pratt_dlv3p_wcec - PF | OP-W | miou_rob | -0.0043 [-0.0121, +0.0048] | -0.0043 [-0.0126, +0.0045] |
| hanifi_vgg16_unet_pf - PF | OP-A | crack_iou | -0.0158 [-0.0247, -0.0069] | -0.0158 [-0.0252, -0.0074] |
| hanifi_vgg16_unet_pf - PF | OP-A | relF1_2 | -0.0064 [-0.0189, +0.0042] | -0.0065 [-0.0203, +0.0039] |
| hanifi_vgg16_unet_pf - PF | OP-A | miou_rob | -0.0027 [-0.0097, +0.0045] | -0.0027 [-0.0098, +0.0044] |
| hanifi_vgg16_unet_pf - PF | OP-W | crack_iou | -0.0134 [-0.0244, -0.0040] | -0.0135 [-0.0248, -0.0045] |
| hanifi_vgg16_unet_pf - PF | OP-W | relF1_2 | -0.0066 [-0.0232, +0.0055] | -0.0066 [-0.0242, +0.0049] |
| hanifi_vgg16_unet_pf - PF | OP-W | miou_rob | -0.0026 [-0.0097, +0.0046] | -0.0027 [-0.0098, +0.0045] |
| ucf_dlv3_r50_pf - PF | OP-A | crack_iou | -0.0782 [-0.0944, -0.0587] | -0.0781 [-0.0945, -0.0594] |
| ucf_dlv3_r50_pf - PF | OP-A | relF1_2 | -0.0773 [-0.0892, -0.0594] | -0.0772 [-0.0895, -0.0612] |
| ucf_dlv3_r50_pf - PF | OP-A | miou_rob | -0.0381 [-0.0455, -0.0296] | -0.0382 [-0.0456, -0.0295] |
| ucf_dlv3_r50_pf - PF | OP-W | crack_iou | -0.0967 [-0.1121, -0.0787] | -0.0966 [-0.1119, -0.0793] |
| ucf_dlv3_r50_pf - PF | OP-W | relF1_2 | -0.0984 [-0.1113, -0.0799] | -0.0984 [-0.1113, -0.0819] |
| ucf_dlv3_r50_pf - PF | OP-W | miou_rob | -0.0394 [-0.0467, -0.0309] | -0.0395 [-0.0467, -0.0308] |

crack-free n: 303 of 532 / 301 of 528

### 3b. W1-C read (PF, HOUSE, PFV1): headline 532 / 528

| arm | op | crack IoU 532 / 528 | relF1@2 | inactive IoU | mIoU-R13 |
|---|---|---|---|---|---|
| PF | OP-A | 0.3648 / 0.3646 | 0.8441 / 0.8439 | 0.5027 / 0.5027 | 0.6122 / 0.6119 |
| PF | OP-W | 0.3648 / 0.3646 | 0.8441 / 0.8439 | 0.5027 / 0.5027 | 0.6122 / 0.6119 |
| HOUSE | OP-A | 0.3821 / 0.3819 | 0.8496 / 0.8493 | 0.5217 / 0.5217 | 0.6093 / 0.6090 |
| HOUSE | OP-W | 0.3758 / 0.3755 | 0.8467 / 0.8465 | 0.5234 / 0.5234 | 0.6089 / 0.6086 |
| PFV1 | OP-A | 0.3652 / 0.3649 | 0.8428 / 0.8425 | 0.4887 / 0.4887 | 0.6102 / 0.6099 |
| PFV1 | OP-W | 0.3641 / 0.3638 | 0.8424 / 0.8421 | 0.4893 / 0.4893 | 0.6102 / 0.6098 |

| PFV1 - PF | OP-A | crack_iou | +0.0004 [-0.0058, +0.0069] | +0.0003 [-0.0056, +0.0070] |
| PFV1 - PF | OP-A | relF1_2 | -0.0014 [-0.0099, +0.0064] | -0.0014 [-0.0105, +0.0069] |
| PFV1 - PF | OP-A | inact_iou | -0.0140 [-0.0690, +0.0362] | -0.0140 [-0.0687, +0.0383] |
| PFV1 - PF | OP-A | miou_rob | -0.0020 [-0.0081, +0.0038] | -0.0020 [-0.0078, +0.0041] |

A/A M at OP-A, 532 / 528: crack_iou 0.0100 / 0.0100; relF1_2 0.0100 / 0.0100; inact_iou 0.0503 / 0.0513; miou_rob 0.0100 / 0.0100
crack-free n: 303 of 532 / 301 of 528

### 3c. W1-G four-seed read (gaint PF seeds 5 to 8): headline 532 / 528

| arm | op | crack IoU 532 / 528 | relF1@2 | inactive IoU | mIoU-R13 |
|---|---|---|---|---|---|
| PF | OP-A | 0.3646 / 0.3643 | 0.8443 / 0.8440 | 0.5025 / 0.5025 | 0.6130 / 0.6126 |
| PF | OP-W | 0.3646 / 0.3643 | 0.8443 / 0.8440 | 0.5025 / 0.5025 | 0.6130 / 0.6126 |

A/A M at OP-A, 532 / 528: crack_iou 0.0100 / 0.0100; relF1_2 0.0100 / 0.0100; inact_iou 0.0543 / 0.0541; miou_rob 0.0100 / 0.0100
crack-free n: 303 of 532 / 301 of 528

### 3d. src_calib, dti, d0 on W1-C (528 beside 532; *_beside.txt)
- src_calib: every headline value moves by <= 0.0009 (fa_px of PF src_bias 624.4 -> 625.8); primary src_bias - glob_bias crack IoU PF +0.0003 [-0.0046, +0.0132] -> +0.0003 [-0.0047, +0.0143]; HOUSE -0.0026 both; PFV1 -0.0017 both.
- dti: every value moves by <= 0.0005.
- d0 (PF pooled): pred share within 1 px of the ridge 0.6058 -> 0.6035, GT share 0.4952 -> 0.4927.

### 3e. Reading (S)
- Excluding the 4 duplicate cells moves every headline value by at most 0.0004 (strict crack IoU, relF1@2, mIoU-R13; inactive IoU 0.0000), and no PASS* flag, interval sign or verdict changes in any of the three reads. The 532-cell screens made so far stand; the 528-cell values are now printed beside them as the ruling asks.
- The A/A margin on cv02 for inactive IoU moves 0.0503 -> 0.0513 (gaint 0.0543 -> 0.0541); the other margins stay at the 0.010 floor.
- The 4 cells are a lower bound on the duplicate problem: the masked same-cell audit (SAMECELL_AUDIT.md) finds more cross-fold pairs that share physical cell area. The exclude list is the lead's to extend; the option takes any list.

## 4. OP-C class lines on real dumps (E; bench_b b5bf0ae; stageBfix/F2/run_f2c.sh, 17:29 to 17:33)
`bench_read_w1.py --arm PFC=<opc/dumps_gaint>/pf_v11_opc --arm S1=<opc/dumps_gaint>/pf_v11_s1 --baseline PFC --aa PFC:5,6:7,8 --score-exclude dup_crossfold_v1.tsv` (gaint PF seeds 5 to 8; output stageBfix/F2/opc_demo/read/read.txt). The baseline is detected as OP-C from its manifests and read.txt prints, at OP-A (mean over seeds, 532 cells):

| arm | mIoU-R13 | class | IoU | precision | recall | pred px on cells without the class (cells) | share of the class's pred px on those cells |
|---|---|---|---|---|---|---|---|
| PFC (OP-C) | 0.6266 | gridline | 0.3623 | 0.4885 | 0.5840 | 46,389 (174) | 0.046 |
| PFC (OP-C) | 0.6266 | splice | 0.1126 | 0.1988 | 0.2068 | 12,710 (472) | 0.183 |
| S1 (argmax) | 0.6129 | gridline | 0.3021 | 0.6331 | 0.3663 | 15,648 (174) | 0.032 |
| S1 (argmax) | 0.6129 | splice | 0.0210 | 0.3362 | 0.0220 | 194 (472) | 0.095 |

These equal B1 section 2c / 2e (gridline 0.302 -> 0.362, splice 0.021 -> 0.113, splice px on splice-free cells 194 -> 12,710). The same lines are printed for OP-F and OP-W and on 528 cells. Crack-free line in the same read: "GT crack px == 0 over the scored (non-ignore) px of label set v11: n = 303 of 532" (301 of 528).

## 5. Owed / for the lead
- PROTOCOL_v0.2 s10 item 6 and s11 item 5 say the reads' 303 is the v1 count; it is the v1.1 count (section 2). The text needs that correction; no number changes.
- Whether more stems join the exclude list after the same-cell audit is the lead's ruling; the option takes any list (a new dup list version would be a new file with its own md5).
- Rows of wave 2a read against OP-C: pass `--score-exclude benchmark/splits/dup_crossfold_v1.tsv` and an OP-C baseline arm; the class lines then appear by themselves.
