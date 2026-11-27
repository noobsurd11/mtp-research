# Model info sheet: template and worked example (benchmark protocol v1.0)

protocol_v1 (writer), 22 Nov 2026; review round 1 (`RVP`) applied. Companion of `benchmark/PROTOCOL_v1.0.md` (section 6.6 item 1, section 12). One sheet per entry. Written from files only; no sealed label or prediction read.
**Rules for filling.** Every value is copied from a file, with the file and its md5 prefix, or written "n/r" (not reported). A value computed for the sheet is marked "derived" with its formula. Tags: E = stated in the cited file; D = decision, with who and when; S = judgement. Short paths are those of PROTOCOL_v1.0.md (header).

## 1. Template
| # | Field | What to write |
|---|---|---|
| **A** | **Identity** | |
| A1 | Entry id and name | the id used in the reads and tables |
| A2 | Entry class | (a) single model, (b) decision layer, (c) ensemble, (d) uses source metadata (protocol 6.1); TTA view count if any |
| A3 | Recipe and card | architecture, schedule, readout; card path, md5, commit |
| A4 | Paper it stands for; deviations from the paper | ids of the papers; every deviation (weights, loss, augmentation, schedule) |
| A5 | Data track | main or extra-data (protocol 6.2); research-only data or weights flagged |
| A6 | Author, date | |
| **B** | **Data and split** | |
| B1 | Release and label sets | release; training and scoring label sets with manifest md5 |
| B2 | Training cells | CV5 fold models (split, folds) and any full-pool model (root, manifest md5) |
| B3 | Split and groups | split file md5; group file md5 and count; clean-cell list md5 and count |
| B4 | Unlabelled pool | list name, md5, count, the leakage rules applied (protocol 6.5); "none" |
| B5 | Extra labelled data | sets, versions, licence, duplicate search result (guard G13); "none" |
| B6 | Sealed stems in training lists | the check that none is present (`forbidden_v1.txt`) |
| B7 | E1 use | none / trained_on_e1 (which cells) / scored at which opening |
| B8 | Source id at test time | yes or no (yes = entry class (d)) |
| **C** | **Training** | |
| C1 | Steps x batch, resolution | |
| C2 | Pretraining | data, weights file md5, licence |
| C3 | Seeds | |
| C4 | Machine and precision | GPU model, fp32 or bf16 |
| C5 | Code | commits of training, dumps, reads |
| C6 | Checkpoint and readout | step, weights key; no best-validation checkpoint |
| C7 | Training compute | GPU-hours per run, with the record |
| C8 | Peak training memory | MiB, with the record |
| C9 | Selection on development cells | every choice made after looking at CV5 numbers (readout, component, threshold), or "none" |
| **D** | **Inference and operating point** | |
| D1 | Views | plain, or TTA with view count and averaging |
| D2 | Decision rule | OP-A, OP-W, OP-C; any bias or threshold and where it was fitted |
| D3 | Batch and precision | |
| D4 | Deployable unit | which single checkpoint, designated when |
| **E** | **Cost (guard G16)** | |
| E1 | Parameters | total, trainable, encoder |
| E2 | GFLOPs at 512 px | per view and per cell |
| E3 | Output stride | and the head-resolution ceiling if above 1 (protocol 6.4) |
| E4 | Step time | s per step, with the record |
| E5 | Latency per cell | measured, with hardware and what it includes |
| E6 | Equal-cost comparator | needed above 2 x house cost; which one was printed |
| **F** | **Leakage and provenance declarations** | |
| F1 | G13 external data provenance | |
| F2 | G14 generator, teacher, weights | |
| F3 | G15 unseen-module instruments | which reads support which claim |
| F4 | G17 BN contamination (if adopted) | which readout re-estimates BN, on which cells |
| F5 | G19 post-hoc parameters (if adopted) | fixed before the read or cross-fitted |
| F6 | G20 inactive reads (if adopted) | how inactive is reported |
| F7 | Split integrity of the cells scored | module grouping status; known leakage of each set |
| **G** | **Selection and multiplicity** | |
| G1 | Primary contrast | one per read |
| G2 | Set openings | ledger rows, REGISTERED.txt md5, rule md5, prior looks |
| G3 | Contrasts printed beside | list; they decide nothing |
| G4 | Flags and rulings | every flag raised by a rule and who ruled it |
| **H** | **Results** | copied with intervals and verdict words; each line says "selection-biased" where C9 applies |
| H1 | CV5 | levels on 532 and 416 cells; contrasts against PF; guards; verdict |
| H2 | Sealed sets | E1 and test50 values; verdict |
| H3 | Robustness | label-variant shifts; k_0 (groups carrying the gain) |
| **I** | **Artefacts** | md5 of dumps manifests, read outputs, verdict files, result files |
| **J** | **Deviations** | every departure from the protocol, with its record |

## 2. Worked example: C2, the final model
| # | Field | C2 | Record |
|---|---|---|---|
| A1 | Entry id | C2 = full-pool HRNet-W18 U-Net++ + SWAD (readout `swad`) + D4; its CV5 version is CS_D4 (cv5v3 fold models) | E `FRULE` s1, s2; `ORULE` s2 |
| A2 | Entry class | (c) by views under `v0.2` 6.1 (`RVO` N4): one weight set per seed, 8 views; each seed scored as a single model, headline = mean over seeds (`FRULE` s1); C3 is (c) as an ensemble. Class wording pending R7 | E `FRULE` s1; `ORULE` s2; `RVO` N4 |
| A3 | Recipe and card | HRNet-W18 encoder, U-Net++ decoder, PF encoder schedule, constant LR, SWAD uniform average over steps 10,000 to 20,000; `bench/methods/hrnet_w18_unetpp_swad_const_pf_v11.yaml` md5 98f152de, commit 03375d4 | E `FRULE` s1 |
| A4 | Papers and deviations | row card `hrnet_w18_unetpp_pf_v11` (c89314d8) plus the swad_const changes, proven equal by diff; deviation from the T11 row spec: timm loads the encoder file from the offline HF cache instead of an `encoder_weights_file` path (judged acceptable by the reviewer) | E `RR2` l12, l41; `log` 17 Nov 17:02 (C2), 17:07 (Q3) |
| A5 | Data track | pending R2; research-only as trained: the 50 BMRK pool cells are ELPV images under CC BY-NC-SA 4.0, and BenchmarkEL states no licence | E `LIC` s2, s7 D4; PROTOCOL_v1.0 s2.4, s11 |
| A6 | Author, date | lead's team; rule 21 Nov 00:45 IST, opening 21 Nov | E `FRULE` header; `FOR` |
| B1 | Release and label sets | BenchmarkEL 20211104, P532; trained and CV5-scored on v1.1 (masks_v11 MANIFEST 9c0e0687); E1 scored on ext117 (release 20221008) with ignore; test50 scored on v0 and v1.1 | E `ORULE` s3; `FRULE` s1 |
| B2 | Training cells | CV5: `c3x_hrnet_swad_v11_f<k>_s<s>`, folds 0 to 4, out of fold over 532 cells; full pool: all 532 cells, root `pool532_v11` (DATA_MANIFEST 33e65b3f) | E `FRULE` s1, s2; `log` 21 Nov 01:29 |
| B3 | Split and groups | cv5v3.json 7a700b00; cv5v3_groups.tsv d880a769 (285 groups); score_exclude_v3.txt 6d48dfbd (116 excluded, 416 clean) | E `CV3`; `FRULE` s3, s6 |
| B4 | Unlabelled pool | none | E `FRULE` s1 (training data = the 532 pool cells) |
| B5 | Extra labelled data | none | E `FRULE` s1 |
| B6 | Sealed stems in training lists | none: the full-pool root holds no sealed cell in any list | E `FRULE` s1 |
| B7 | E1 use | not trained on E1; scored once at E1 opening #8. The T3b models that train on E1 are separate runs (`t3b_*`, trained_on_e1) | E `ORULE` s1; `T3R` s9 |
| B8 | Source id at test time | no: the inference definition takes the image only | E `ORULE` s2 |
| C1 | Steps x batch, resolution | 20,000 x 8, 512 px | E `FRULE` s1; `T3R` s3 |
| C2 | Pretraining | ImageNet HRNet-W18 weights (timm), file md5 e6bb005d, licence MIT | E `RR2` l12, l85, l93 |
| C3 | Seeds | 5, 6, 7, 8, 9 | E `FRULE` s1 |
| C4 | Machine and precision | cv02, NVIDIA RTX A6000, fp32 | E `FRULE` s1, s6 |
| C5 | Code | CV5 runs commit 03375d4; CV5 D4 dumps bench_infer 32e0b67c at F; full-pool steps 1 to 18,000 under F 821dfad, steps 18,001 to 20,000 resumed under F2 9967d59; E1 and test50 dumps under G 8bd1c27 | E `FRULE` s6; `ADD1` items 1 to 4; `FOR` run record |
| C6 | Checkpoint and readout | latest.pth at step 20000, key `swad` (uniform average, no BN re-estimate); each sealed dump's checkpoint_md5 equals fin2's relayed LATEST.md5 | E `ORULE` s2, s8 |
| C7 | Training compute | about 1.9 h per training of this card on cv02 (planning estimate for the 33 T3b trainings of the same card); the HRNet screen card took about 107 min per run on cv02 with three of our runs training | E `log` 21 Nov 15:55; `R2` s2 |
| C8 | Peak training memory | 9,462 MiB on gaint (path smoke); cv02 estimate 8,634 to 8,740 MiB; job gate 11,510 MiB | E `log` 17 Nov 19:48 |
| C9 | Selection on development cells | **yes**: readout `swad` chosen after the c3x read on the same cv5v3 cells (the registered primary readout swad_bn was NOT CONFIRMED); D4 adopted from the B5 CV5 read; both on pool cells only | E `FRULE` s0; `C3X`; `ERR` item 5 |
| D1 | Views | D4: 8 views (rot90 by 0 to 3 quarter turns, each with and without a flip of W), softmax per view in fp32, probabilities averaged over views | E `ORULE` s2 |
| D2 | Decision rule | OP-A: argmax over 24 classes of log(p + 1e-12); no threshold, bias, class weight or view weight set on or chosen with any sealed cell | E `ORULE` s2 |
| D3 | Batch and precision | batch 8, CUDA fp32, TF32 off | E `ORULE` s2 |
| D4 | Deployable unit | seed 5, designated before any number (no selection by score) | E `FRULE` s1 |
| E1 | Parameters | 20,795,692 total = trainable; encoder 10,947,028 | E `RR2` s3; `IC` s2 |
| E2 | GFLOPs at 512 px | 218.0 per view; 1,744 per cell with D4 | E `RR2` s3; `IC` s2 |
| E3 | Output stride | 1 | E `RR2` s3 |
| E4 | Step time | 0.32 s per step (HRNet row card, request value) | E `RR2` s3 |
| E5 | Latency per cell | CPU: 3.88 s per cell median (p90 4.38), gaint CPU (Threadripper 7960X), 16 threads, batch 1, fp32, network time only; 18.0 x C1 in CPU time; peak RSS 1,376 MiB (batch 1). GPU (cv02, one RTX A6000, fp32, TF32 off, network time only; 22 Nov): 0.174 s per cell median (p90 0.177) at batch 1, 15.5 x C1; 0.133 s at batch 8; shared host, so upper bounds for an idle A6000. Observed cv02 wall time, fixed costs included: 0.94 s per cell on the E1 jobs (with logp writes), 0.45 s per cell on the CV5 D4 dumps | E `IC` s3.1, s3.3, s3.4, s4 |
| E6 | Equal-cost comparator | above the G16 line (1,744 GFLOPs per cell, 11.8 x C1). No equal-cost comparator printed. Same-view controls: PF_D4 on CV5, C1-D4 on E1 (0.68 x C2 FLOPs, derived; C2 / C1-D4 width 0.463 / 0.345 = 1.34, derived). E-PF (0.42 x C2 FLOPs, derived) on E1, set against C3 and C1 only (C2 - E-PF +0.0408 at point level, derived, no interval). Deviation from G16 not ruled before the opening (R7) | E `IC` s2; `TT` T11a; `FOR`; `RVP` B1; PROTOCOL_v1.0 s6.4 |
| F1 | G13 | no external data | E `FRULE` s1 |
| F2 | G14 | generic ImageNet weights only; no weights trained on SCDD or E-SCDD; no teacher, generator or labeller | E `RR2` l85 to l93; `FRULE` s1 |
| F3 | G15 | the E1 claim rests on the registered opening #8 only; no U-dev proxy supports it | E `ORULE` s0, s4 |
| F4 | G17 | readout `swad` has no BN re-estimate; swad_bn (BN re-estimated on the 532 training cells) is information only | E `FRULE` s1; `ADD1` item 5 |
| F5 | G19 | no post-hoc parameter at inference; D4 and the readout were fixed before the E1 opening (see C9 for the CV5 selection) | E `ORULE` s2, s10 |
| F6 | G20 | inactive IoU reported only on E1 (10 inactive cells), with both intervals | E `ORULE` s4 |
| F7 | Split integrity | CV5 on cv5v3 (no group spans folds; BMRK grouped by image id); E1: "unseen modules" supported, not proven; test50: 8 test cells are the same physical cell as a pool cell (7 by pixels, 1 by the cells.tsv link), 7 neighbouring crops, 19 share a module | E `CV3`; `SPI` 5a, 5b; `ERR` item 3 |
| G1 | Primary contrast | E1: P = C2 - C1, crack relF1@2, seeds 5 to 9, OP-A | E `ORULE` s4 |
| G2 | Set openings | E1 opening #8 and test50 opening #19, one registration: REGISTERED.txt 4c783a77, rule 065a7ddd; prior looks: "E1 7 registered openings (3 looks at one contrast) plus reads before 31 Oct and one use of published E1 contrasts (R0, 15 Nov); the final models were never scored on either set"; test50 after 18 counted openings | E `FOR`; `ERR` item 5; `TL`; `EL` |
| G3 | Contrasts beside | C2 - C1-D4, C1-D4 - C1, S1 to S5, A/A, strata, per class, components (E1); C2 - C1 on test50 v1.1 | E `ORULE` s5, s7 |
| G4 | Flags and rulings | FLAG D4 raised by the CV5 TTA read (b); ruled "keep D4, go ahead" by the user 21 Nov about 11:21 IST | E `TTA`; `log` 21 Nov 11:22 |
| H1 | CV5 (selection-biased) | CS_D4 on 532 cells: strict crack IoU 0.3942, relF1@2 0.8684, inactive IoU 0.5370, mIoU-R13 0.6232, false crack px 98, width ratio 1.0118; relF1@2 on 416 cells 0.8494. (c) CS_D4 - PF +0.0222 [+0.0138, +0.0308] (532, OP-A), +0.0230 [+0.0127, +0.0341] (416); ARTS width 1.159 on the 416 cells at OP-A and OP-W (named). verdict.txt prints both "(c) CS_D4 - PF: GAIN, FAILING GUARDS NAMED" (l126) and "C2 PASSES ITS CV5 CHECK (selection-biased; the E1 opening is the test)" (l170). (b) CS_D4 - CS +0.0055 [-0.0002, +0.0115]: NOT CONFIRMED, NO LOSS | E `TT` T5, T7a; `TTA`; `GAPS` G-D2 |
| H2 | Sealed sets | E1 (106 cells, 71 clusters, OP-A): C2 relF1@2 0.4897 [0.4656, 0.5067] (range over seeds); P +0.0430 [+0.0013, +0.1043] seed-aware, fixed-model [+0.0067, +0.1007]; G1 width 1.013, G2 CSIR width 1.013, G3 false crack px 2421 vs 3218 (0.75 x), G4 mIoU-R13 +0.0249; inactive +0.0996 [-0.0310, +0.2162] (reported only); strict crack IoU +0.0263 [+0.0022, +0.0651] (outside the band, decides nothing); **CONFIRMED**. Full cells +0.1464 [+0.0420, +0.2278]; half-cut cells +0.0110 [-0.0289, +0.0722]. Deployable seed 5 alone: +0.0189 [-0.0403, +0.1068]. test50 #19 (decides nothing; known leakage): v1.1 relF1@2 C2 0.901 (C1 0.891), C2 - C1 +0.0102 [-0.0094, +0.0291]; v0 Pratt rule A median IoU crack 0.383, inactive 0.588, mean of 3 0.424 | E `TT` T8, T11a; `FOR` |
| H3 | Robustness | not computed for CS_D4; for COMBO (same runs, readout swad_bn): relF1@2 gain passes under all four label variants, k_0 31 groups | E `AUD` s2 |
| I | Artefacts | CV5 D4 read: final_tta_read/verdict.txt a95f89e8, read.txt 54214525; read tool bench_read_w1.py fdb56b78. Sealed opening: jobs 3a308b9c, stage manifest 2b838801, CODE.md5 d9a250a2, read script 2525575e, verdict.txt bbb5f3b4, MD5_copy.txt e9169514. Full-pool models: `fin_hrnet_swad_v11_pool_s5..9`, relayed to /mnt/nas/noob_el_archive/bench_relay/fin2 with md5 checks. Result files: `FOR` 16e3f1e7, `ERR` af55915f, `TTA` b64f964e | E `TTA`; `FOR`; `ADD1` completion |
| J | Deviations | (1) readout chosen post hoc on CV5 (C9); (2) no equal-cost comparator for C2 (class (c), above the G16 line); only same-view controls (0.68 x C2 FLOPs) and, on E1, E-PF set against C3 (E6; R7); (3) full-pool runs resumed from step 18,000 under F2 after the final-validation stop; CPU resume bit-equal, GPU atomics noise only; (4) OP-W not computed on sealed sets (needs folds); (5) no held-out score of the full-pool model itself; the CV5 rows describe the recipe through the fold models | E `FRULE` s0; `ADD1`; `ORULE` s2; `GAPS` G-N6; `RVP` B1 |
