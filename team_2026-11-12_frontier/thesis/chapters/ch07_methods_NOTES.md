# NOTES for ch07_methods.tex (Chapter 7, Baselines and methods under the protocol)

Written 23 Nov 2026. Read only result text files, docs and tables; pool (CV5) results only; no E1 or test50 dump, label or prediction.

## Source keys (path relative to T = ~/mtp/research/team_2026-11-12_frontier; md5 prefix as read 23 Nov)
- TT = thesis/THESIS_TABLES.md (81c54378); line numbers below are TT lines (tables T5 l181 to l191, T6 l203 to l211, T7a l226 to
  l232, T7b l247 to l255, T15 l510 to l527, T16a l539 to l558, T19b l643 to l646)
- R1 = results/ROWS1_READ.md (07c93594); R2 = results/ROWS2_READ.md (3fef30d4); W2A = results/W2A_READ.md (90c781a8)
- HR = results/C3HRNET_READ.md (450bf943); SW = results/C3SWAD_READ.md (c841f618); CX = results/C3X_READ.md (da841902)
- FTR = results/FINAL_TTA_READ.md (b64f964e); VT = results/final_tta_read/verdict.txt (a95f89e8); RT = results/final_tta_read/read.txt (54214525)
- HP = results/HOUSEPF_READ.md (71e5a382); HC = results/HOUSECS_READ.md (9efd43ac)
- AUD = dataset_audit/REPORT.md (9d7e0d27); P02 = benchmark/PROTOCOL_v0.2.md (b8b7f66a); P10 = benchmark/PROTOCOL_v1.0.md (eeb3379a)
- GP = thesis/GAPS.md (86108083); BR = BRIEF.md (bc06edd2)

## Every number in the chapter, with its source
### Intro
| Number / fact | Source |
|---|---|
| 532 pool cells, out of fold; 416 clean cells | P10 l19; TT T5 caption |
| screens 2 seeds cv5v2; rows 5 seeds (5 to 9) cv5v3, no module spans folds | P10 l19; TT T15 caption, T5 caption |
| decision rule (OP-A and OP-W, 532 and 416, delta >= M, lower end > 0, guards) | TT T4 rows "A gain counts if", "Width guard", "False crack px guard", "mIoU-R13 guard"; P10 5.2, 5.5 |
| M = 0.010 | TT T4 "Margin M"; HR l11 |
| convention band +-0.019; strict IoU decides nothing | TT T4 "Strict crack IoU"; P10 l20 |
| "M covers seed noise, not the choice of folds" | P02 l256 |
| reads never mix machines | TT T15 caption |

### 7.1 PF and HOUSE
| Number | Source |
|---|---|
| house recipe (U-Net++, ResNet-34, 512 px, batch 8, Adam 1e-3, 200-step warm-up, cosine, wd 1e-4, 20,000 steps, CE + soft Dice, label-safe aug.) | BR l42 |
| PF: encoder frozen 1,000 steps, then ramped to 0.1 x lr over the next 1,000 steps, no encoder wd | H04 l410; method card house_r34_unetpp_pf_v11.yaml (training.encoder_pf: freeze 1000, ramp 1000, lr_mult 0.1, wd 0). BR l43 omits the ramp |
| plain fine-tune erases deep encoder stages; PF keeps them | TT T21 "Encoder audit" row (l707): layer3 0.005 to 0.018, layer4 -0.001 to 0.001 |
| PF 0.8463 / 0.8264 / 0.3653 / 0.5042 / 0.6116 / 212 / 1.0189 | TT T5 l181; RT l5 |
| HOUSE 0.852 / 0.383 / 0.514 / 0.607 / 774 / 1.13 | TT T5 l182 |
| HOUSE - PF relF1@2 +0.0059 [-0.0043, +0.0152]; +0.0034, +0.0066, +0.0025 | TT T6 l210; HP l12 |
| HOUSE - PF strict IoU +0.0179 [+0.0093, +0.0266], inside band | TT T6 l210; HP l13, l20 |
| 9 items: ARTS 1.307 / 1.167 / 1.370 / 1.190; CFVS 1.164; false px 2.55 to 3.66 x | TT T6 l210; HP l26, l27, l30 |
| HOUSE rule | P10 7.1 note (HOUSE rule bullet); HC l3 |

### 7.2 baseline suite (screens)
| Number | Source |
|---|---|
| deviations: ucf ImageNet not COCO, no aux head; pratt house aug. + paper's loss | R1 l31 |
| leak shared by all arms; comparisons valid | P02 l262 (section 11 item 9) |
| unet -0.0016 [-0.0110, +0.0073]; hanifi -0.0064 [-0.0189, +0.0042] | TT T16a l539, l540; R1 l19, l20 |
| dlv3p -0.0093 [-0.0204, +0.0019]; OP-W -0.0199 [-0.0325, -0.0086]; width 1.21 | TT T16a l541; TT T15 l514; R1 l21, l28 |
| ucf -0.0773 [-0.0892, -0.0594] | TT T16a l542; R1 l22 |
| pratt -0.0932 [-0.1113, -0.0774]; width 3.05; relP@2 0.648 / relR@2 0.892; OP-W -0.0899 [-0.1130, -0.0693] | TT T16a l543; TT T15 l516; R1 l14, l23 |
| "decoder does not matter"; stride 4 about 0.02, stride 8 about 0.08 to 0.10; "Nothing in this tranche beats PF or HOUSE" | R1 l27 to l30 (S readings, worded as judgement) |

### 7.3 screens
| Number | Source |
|---|---|
| HRNet screen +0.0114 [+0.0032, +0.0203] / OP-W +0.0128 [+0.0041, +0.0221] | R2 l21; P10 7.2 table |
| swad_const screen +0.0135 [+0.0051, +0.0221] | W2A l25; P10 7.2 table |
| skr01 +0.0039 [-0.0027, +0.0115]; 12% wider (1.13); within 0.005 when width-matched | TT T16a l544; R2 l39, l46 |
| segformer -0.0026 [-0.0132, +0.0095]; OP-W -0.0135 [-0.0259, -0.0005]; width 1.20, all sources outside band | TT T16a l545; R2 l53, l61 |
| rcs -0.0085 [-0.0187, -0.0004]; splice gain; false px 1.68 x | TT T16a l546; W2A section 4 (rcs paragraph) |
| ema +0.0018 [-0.0047, +0.0081] | TT T16a l547; W2A section 5 |
| jml_hard -0.0004 [-0.0086, +0.0064]; soft_band +0.0046 [-0.0033, +0.0127]; 7% wider | TT T16a l548, l550; W2A addendum ("crack drawn 7% wider") |
| encoder_spd gate failed; +0.0007 [-0.0272, +0.0130] | TT T16a l549; W2A section 7 |
| la_ce -0.0022 [-0.0112, +0.0060]; layered_ci -0.0140 [-0.0767, +0.0556]; src_calib +0.0003 [-0.0046, +0.0132]; dti +0.0011 [-0.0016, +0.0062]; OP-F -0.0118 [-0.0357, -0.0005] | TT T16a l551 to l555 |
| SKR01 on U1 +0.0206 [-0.0518, +0.0744], 164 cells | TT T16a l556 |
| gin_ipa parked, not run | TT T16a l558 |

### 7.4 5-seed confirmations
| Number | Source |
|---|---|
| HRNET - PF +0.0104 [+0.0012, +0.0203]; +0.0117 [+0.0019, +0.0220]; +0.0115 [+0.00001, +0.0259]; +0.0126 [+0.0006, +0.0273]; every seed positive | TT T6 l203; HR l10, l12 |
| false px 2.90 to 4.15 x; ARTS 1.162 (416 OP-W) | TT T6 l203; HR l3, l18, l19 |
| relR@2 +0.015 / +0.023; relP@2 +0.004 / -0.001 | HR l12 |
| strict IoU +0.0008 [-0.0105, +0.0111] | TT T6 l203 |
| about 1.8 px per crack-free cell; PF 212; bound tight | HR l27 (S, worded as the read's own reading) |
| HRNET - HOUSE +0.0045 [-0.0069, +0.0157] | TT T6 l209; HR l25 |
| SWAD arm description (constant lr, uniform average 10,000 to 20,000, swad_bn re-estimates BN) | W2A section 3, first line |
| SWADBN +0.0070 [-0.0007, +0.0156]; 416 OP-A +0.0098 [+0.0009, +0.0198]; SWAD +0.0064 [-0.0009, +0.0138] | TT T6 l204, l205; SW l10, l11 |
| 5 items (ARTS width; false px 1.60 x) | TT T6 l204; SW l15 |
| strict IoU +0.0180 [+0.0108, +0.0262]; centreline +0.0047 | TT T6 l204; TT T19b l645; AUD l157 |
| screen +0.0135 to 5-seed +0.0070; "shrank by about half" (S) | SW l29 |
| COMBO +0.0154 [+0.0065, +0.0260]; +0.0158 [+0.0069, +0.0264]; +0.0167; +0.0166; every seed positive | TT T6 l206; CX l20, l21, l28 |
| 8 items; ARTS 1.174 to 1.242; false px 1.62 to 1.84 x | CX l23, l24, l27 |
| COMBO - HRNET +0.0050 [-0.0041, +0.0141]; COMBO - SWADBN +0.0085 [-0.0017, +0.0183] NO LOSS | TT T6 l211; CX l29 |
| CS +0.0166 [+0.0082, +0.0263]; fails only ARTS 416; declared secondary | TT T6 l207; CX l24, l27, l33 |
| PF ARTS width ratio 0.7832, CS_D4 0.9078 (131 ARTS cells, 416 clean) | TT T7b l250 |

### 7.5 TTA
| Number | Source |
|---|---|
| D4 = 8 views, softmax averaged; 8 x forwards | OPENING_RULE.md l42 (harness/final/opening, 065a7ddd); TT T22 "Forwards per cell" |
| PF_D4 - PF +0.0134 [+0.0066, +0.0207]; +0.0132 x 3; CONFIRMED; 0 items | TT T7a l226; FTR l15 |
| false px 212 to 32 (0.15 x); width 1.021 | TT T7b l247, l249; FTR l21 |
| B5 D4 8 views +0.0173 [+0.0115, +0.0230]; D4MS 24 views +0.0142 [+0.0079, +0.0202], score claim PASS | TT T7b l254, l255 |
| "the one confirmed CV5 gain" | TT T20 claims 6 and 8; P10 7.5 |
| CS_D4 - CS +0.0055 [-0.0002, +0.0115] NOT CONFIRMED, NO LOSS | TT T7a l227 |
| 213 to 98 | FTR l21, l28 |
| CS_D4 - PF_D4 +0.0087 [+0.0017, +0.0157] | TT T7a l230 |
| FLAG D4 (8 x inference without confirmed gain); kept before registration | final_opening_read/verdict.txt l3, l7, quoting VT l169; TT T7a l227 |

### 7.6 final recipe
| Number | Source |
|---|---|
| no confirmed arm, no fallback | CX l3 |
| swad readout chosen after c3x read; D4 from B5; selection-biased | FTR l9 to l10; final_opening_read/verdict.txt l139 |
| CS_D4 - PF +0.0222 [+0.0138, +0.0308]; +0.0228; +0.0230; +0.0229 | TT T7a l228 |
| GP D1 sentence (verbatim) | GP l68 to l69 |
| false px 0.46 x (98 vs 212); mIoU-R13 +0.0117 [+0.0046, +0.0193]; inactive +0.0328 [-0.0128, +0.0826] | TT T7b l248, l251, l252 |
| strict IoU +0.0288 [+0.0197, +0.0374] | TT T7a l228 |
| per seed CS - PF +0.014 to +0.022 | TT T7b l253 |
| C2 here = CV5 version; full-pool models no CV5 score | GP l16 (G-N6), l67 (D1 (c)) |
| CS_D4 - HOUSE +0.0163 [+0.0051, +0.0284]; +0.0194 [+0.0080, +0.0319]; +0.0164 [+0.0033, +0.0318]; +0.0204 [+0.0073, +0.0369]; strict +0.0110 [+0.0029, +0.0198] | TT T7a l231; HC l16, l19 |
| ARTS 0.847 / 0.846 | TT T7a l231; HC l110 |
| no HOUSE D4 dumps | HC l35 |
| CS - HOUSE +0.0107 [-0.0009, +0.0229]; OP-W +0.0140 [+0.0017, +0.0269] | TT T7a l232; HC l27 |
| reading "model alone ... D4 does" (S) | HC l109 (the HC sentence is about strict IoU; the chapter states the relF1@2 version, which the T7a values support: CS - HOUSE holds 0 at OP-A, CS_D4 - HOUSE does not) |
| 0.90 / 0.90 target | BR l57 |
| CS_D4 relP@2 0.9216 / relR@2 0.8211; PF 0.8953 / 0.8024 (OP-A) | RT l14, l5 (not in TT: OUTLINE gap O1) |
| F21 caption: 190 clean cells with at least 20 crack px | FIGURES_B.md l218 (b2c8d9fb); F21_data.csv (3ddc7889), rows with clean416 = 1 and gt_crack_px_v11 >= 20: 190 (added 23 Nov, TRACE_REPORT s4) |

### 7.7 robustness
| Number | Source |
|---|---|
| four variants; at most 0.003 | AUD l159; TT T19b caption; TT T19a F1 ("at most 0.0031") |
| COMBO (C3X) +0.0128 to +0.0161 all PASS, k_0 31 | TT T19b l646 |
| HRNET +0.0104 to +0.0073 (3 px), k_0 17 | TT T19b l644 |
| HOUSE centreline +0.0015, k_0 4; SWADBN centreline +0.0047 | TT T19b l643, l645 |
| 125 groups hold crack px; greedy = worst case | TT T19a F9 row |

### 7.8 weak classes
| Number | Source |
|---|---|
| OP-C definition (11 of 13 classes, other 4 folds) | P10 l172 (5.3 table); P02 l101 |
| +0.0126 [+0.0077, +0.0167]; +0.0137 [+0.0107, +0.0169] | P02 l260 (section 11 item 8); P10 5.3 first bullet |
| gridline +0.060 / +0.058; splice +0.092 / +0.075 | P02 l103 |
| about a third splice at precision 0.15 to 0.20 | P02 l260 |
| adopted as comparator, decision layer; no final model uses it | P02 l260; P10 l172; OUTLINE 7.7 |
| E1 material and edge dark 0 | final_opening_read/verdict.txt l70, l74 (TT T12a) |

## Judgement sentences kept
1. 7.1: "HOUSE draws cracks wider and makes more false crack pixels than PF; its strict-IoU edge is within the size a change of line-width convention produces, and on relF1@2 it is not separated from PF."
2. 7.2: "The decoder does not matter here ... Output stride does ... Nothing in this tranche beats PF or HOUSE." (R1 S readings)
3. 7.3: "the loss moves the operating point, not the frontier" (R2 l48 S); "losses that reshape the crack drawing move along the precision and recall trade-off rather than past it, and the arms aimed at rare classes buy them with crack quality."
4. 7.4: "the screen effect shrank by about half, as an arm selected on a 2-seed screen is expected to" (SW l29 S).
5. 7.4: "the failing guards are partly a property of the reference ... the guard measures an annotation convention as much as a model."
6. 7.5: "D4 and the model change overlap, so on the candidate D4 adds less than on PF." (FTR l27 S)
7. 7.6: "in distribution, the HRNet + SWAD model alone is not separated from HOUSE at argmax, and D4 supplies the rest of the edge."
8. 7.7: "relF1@2 is the right decision metric for these labels, and a strict-IoU gain on this data should be read as a statement about the width of the drawn line until shown otherwise."

## Placeholders and citations
- \PENDING: 0. \CITE: 0. \FIG: 4 (F10, F11, F12, F21), referred to in the text as plain "Figure~F12".
- Citations: refs_extra.bib keys wang2021hrnet, zhou2018unetpp, chen2018deeplabv3plus, kirchhoff2024skeletonrecall; pratt2023benchmark
  (ch08_e1_result.bib, also ch04_data.bib and ch06_protocol.bib); 12 new entries in ch07_methods.bib: cha2021swad, xie2021segformer, hoyer2022daformer, wang2023jml,
  moralesbrotons2024ema, tian2024spd, ouyang2021ginipa, he2015resnet, ronneberger2015unet, chen2017deeplabv3, fioresi2022ucfel,
  hanifi2025multiclass.
  - Ids on disk: cards/ledger/MASTER.tsv paper_id (SWAD 2102.08604 P039, SegFormer 2105.15203 P260, DAFormer
    doi:10.1109/cvpr52688.2022.00969 P036, JML doi:10.52202/075280-3289 P017, EMA 2411.18704 P049, SPD 2411.01713 P018, GIN-IPA
    2111.12525 P012); RELATED_WORK.md l25 (Fioresi doi:10.1109/JPHOTOV.2021.3131059), l26 (Hanifi doi:10.1007/978-981-96-8892-0_4).
  - Not on disk, checked online: ResNet 1512.03385, U-Net 1505.04597, DeepLabV3 1706.05587 (ids chosen by me, titles and
    authors confirmed by the arXiv API).
  - Authors / titles / dates from the arXiv API (export.arxiv.org, 23 Nov); DAFormer, JML, Fioresi, Hanifi venue / pages from the
    Crossref API. arXiv-only entries are @misc preprints; venues recorded on disk but not checked are in the note field.
  - D4 TTA cites no paper (RELATED_WORK.md section 7: none exists for our D4 step).
- Cross-references assume: ch:intro (Ch 1, not yet defined), ch:data (Ch 4), ch:legacy (Ch 5), ch:protocol (Ch 6), ch:e1_result
  (Ch 8, mine); ch:data, ch:legacy, ch:protocol match the other writers' files (checked 23 Nov 09:00).
- Duplicate keys: cha2021swad and xie2021segformer are also in ch06_protocol.bib. The ch06 SWAD entry spells the 5th author
  'Seunghyuk Park'; the arXiv API (23 Nov) gives 'Seunghyun Park', as in ch07_methods.bib. Keep the ch07 entry.
- Tables referenced: T5, T6, T7a, T7b, T15, T16a, T16b, T19b.

## Departures from OUTLINE and things to check
- OUTLINE 7.1 says HOUSE - PF has "point values only" (pending HP); HP is in: intervals used as T6 prints them.
- OUTLINE 7.5's T7a now also holds the two HOUSE-rule rows (HC); they are in 7.6 with "selection-biased, printed intervals,
  no verdict". The 8-view vs single-view asymmetry is stated, and CS - HOUSE is given beside (HC l111 option (a)).
- OUTLINE 7.7 (OP-C, gap O6) is cited from P02 l103, l260 and P10 5.3, not from TT.
- Added: the CV5 relP@2 / relR@2 of PF and CS_D4 (RT l5, l14; OUTLINE gap O1) with the selection-bias note, so the 0.90 / 0.90
  target is shown as not reached on CV5 too.
- Machine names are not in the text ("one machine", "a second machine"); OP-C values are "on the machine of the 5-seed rows"
  (cv02) and "on the other" (gaint).
- Screen tier wording follows ruling R1 (2-seed rows as a separate screen tier; log.md 22 Nov 12:49).
