# CPU analyses on COMBO out-of-fold dumps (27 Nov 2026, cpu agent)

E = measured by command (source given), S = judgement. gaint CPU only, nice 19, no GPU, no training. Inputs: relayed cv02
dumps of the cv5v3 held-out folds (532 pool cells, open sets only; the tools refuse sealed sets; test50 and e1_106 were never
touched). Scripts: `/home/yugma/mtp/research/team_2026-11-27_arch/cpu/` (C below). Outputs: `/home/noob/work/bench_reads/x4_cpu/`
(O below). The reviewed read tree `/home/noob/work/bench_wt_final` (89b9ea5, no tracked change, checked by every script) is
imported read-only with PYTHONDONTWRITEBYTECODE=1. COMBO = c3x HRNet-W18 U-Net++ PF + SWAD, swad readout (the x4
comparator; RUNBOOK s1). Statistics reused, not rewritten: `crossfit_op.crack_counts / cmetrics / boot_pair`,
`score_ext.summarize`, `gap_census.census_cell / boot`, `skel.skeletonize`, the read tool `bench_read_w1.py` (fdb56b78)
through `harness/x4/read_x4.py` and `x4_verdict.py`.

## Headline
- **Task 4 (added later), endpoint extension EXT (post-hoc): under M.** OP-A relF1@2 +0.0045 [+0.0002, +0.0092] (relR +0.0151,
  relP -0.0082; false crack px on crack-free cells 1.35 x), SCREEN FAIL (NO LOSS). Missed GT crack px have median margin
  -12.75: the margin does not hold them. See section 4.
- **Task 1, component post-processing (post-hoc arm): null.** Cross-fitting chose crack min-length L = 0 (no removal) in all
  10 seed x fold fits, because removing short predicted crack components lowers relF1@2 monotonically (relR@2 loss > relP@2
  gain). PPCC - COMBO, seeds 5, 6, 532 cells, OP-A: relF1@2 +0.0000 [-0.0041, +0.0041], relP@2 +0.0000, relR@2 +0.0000,
  false crack px on the 303 crack-free cells 286.5 vs 286.5 (1.00 x), inactive IoU -0.0019 [-0.0354, +0.0319], mIoU-R13
  -0.0001 [-0.0039, +0.0036]. x4_verdict: SCREEN FAIL (NO LOSS). COMBO's false-crack load is already about 1 px per crack-free cell.
- **Task 2, D4 audit: no class is orientation-specific; D4 is label-safe.** Training already uses the full D4 group. D4 lowers
  two thin-line classes, gridline (-0.0144 [-0.0212, -0.0079]: precision up, recall down) and splice (IoU 0.002 -> 0.0005),
  in all three model pairs. S: that is view averaging of faint thin lines, not a label-orientation fault.
- **Task 3, census: misses sit in long cracks, at crack ends, in CFVS and CSIR; false crack px sit on background and inactive.**
  Components of at least 100 skeleton px hold 0.75 of missed px (miss rate 0.16 to 0.17); components under 25 px hold 0.05
  (miss rate 0.36 to 0.54). By the 15 Nov buckets: ends 0.52, interior gaps 0.28, whole missed cracks 0.19, small 0.01.
  Source shares of the miss: CFVS 0.54, CSIR 0.29 (highest miss rate, 0.27), BMRK 0.12, ARTS 0.05. Busbar / ribbon contact
  is nearly universal (0.94 of GT crack px), so the contact split is coarse; isolated components (0.014 of GT px) have the
  highest miss rate (0.41). False crack px beyond 2 px of GT (27.5k px per seed, the relP@2 loss): background 0.56, inactive
  0.33, busbar / ribbons 0.07, gridline 0.016, scuff / star ignore px 0.013.

## 1. Per-class component post-processing (POST-HOC ARM)

**Status: post-hoc.** The COMBO dumps and these 532 cells were read before (c3x, final_tta, x4 posctl). Thresholds are
cross-fitted, but the arm was defined after those reads, so nothing here is a confirmed gain on unseen data.

Rule (Extending nnU-Net, arXiv 2208.10791, per-class small-component removal), on the dump's argmax map:
- crack: 8-connected components of pred = 14 with skeleton length < L px (bench/skel.py, at least 1) are removed; their px
  take `oth` (the dump's argmax over the 23 non-crack classes), m_crack there set to min(m, -8) so the dump stays consistent.
- inactive: 8-connected components of pred = 11 with < A px are removed and become background (0). The COMBO dumps hold no
  logp, so the runner-up class is unknown; nnU-Net's own removal also writes background.
- Grids: L in {0, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 25, 30, 40, 50, 60}; A in {0, 25, 50, 100, 200, 300, 500, 750, 1000,
  1500, 2000, 3000, 5000, 8000}.
- Cross-fitting: per seed (5, 6) and held-out fold k, L maximises pooled crack relF1@2 and A pooled inactive IoU on the
  out-of-fold cells of the other four folds of the same seed (never fold k); ties go to the smaller threshold. Fold k is
  then written with its own (L, A) as a derived dump (`dumpfmt.write_cell`, validated) and read against raw COMBO.

### 1.1 Choices (E, O/pp/sweep.txt, choices.json)
| seed | f0 | f1 | f2 | f3 | f4 |
|---|---|---|---|---|---|
| 5 (L, A) | 0, 50 | 0, 0 | 0, 25 | 0, 0 | 0, 25 |
| 6 (L, A) | 0, 300 | 0, 25 | 0, 25 | 0, 25 | 0, 25 |

L = 0 (no crack removal) in all 10 fits. Fit-set inactive IoU gain of the chosen A: at most +0.003 (s6 f0, 0.5430 -> 0.5460).

### 1.2 Why (E, descriptive in-sample curves on all OOF cells, O/pp/sweep.txt; not the result)
| L | relF1@2 s5 | relP@2 s5 | relR@2 s5 | false crack px on 303 crack-free cells s5 | relF1@2 s6 | fa px s6 |
|---|---|---|---|---|---|---|
| 0 (raw) | 0.8635 | 0.9107 | 0.8209 | 228 | 0.8660 | 345 |
| 5 | 0.8615 | 0.9130 | 0.8155 | 214 | 0.8639 | 325 |
| 10 | 0.8585 | 0.9147 | 0.8088 | 164 | 0.8621 | 253 |
| 20 | 0.8511 | 0.9194 | 0.7923 | 115 | 0.8540 | 201 |
| 50 | 0.8157 | 0.9239 | 0.7301 | 0 | 0.8173 | 0 |

relF1@2 falls monotonically with L: each step buys less relP@2 than it costs relR@2 (short predicted components are mostly
real crack pieces within 2 px of GT). The false-crack load on crack-free cells is already small for COMBO (228 / 345 px over
303 cells per seed, i.e. about 1 px per cell), so there is little for the filter to remove. Inactive: IoU is flat up to
A = 300 (0.5297 -> 0.5261 s5) and falls after; small predicted inactive islands are few.

### 1.3 Read (E, read_x4.py, O/read_pp; COMBO vs PPCC, seeds 5, 6; PFAA = PF seeds 5 to 8 for M; 2,000 draws)
Read folder O/read_pp (read.txt, read.json, verdict.txt); M from the A/A in the same read: relF1@2 0.0100 (A/A SE 0.0037),
inactive 0.0462, mIoU-R13 0.0100.

| metric (OP-A) | COMBO | PPCC | PPCC - COMBO [95% CI], 532 cells | 416 clean cells |
|---|---|---|---|---|
| crack relF1@2 | 0.8647 | 0.8647 | +0.0000 [-0.0041, +0.0041] | +0.0000 [-0.0052, +0.0054] |
| relP@2 | 0.9123 | 0.9123 | +0.0000 [-0.0058, +0.0056] | +0.0000 [-0.0074, +0.0077] |
| relR@2 | 0.8219 | 0.8219 | +0.0000 [-0.0049, +0.0048] | +0.0000 [-0.0060, +0.0060] |
| false crack px on crack-free cells (guard <= 1.5 x) | 286.5 | 286.5 | 1.00 x (PASS) | 214 vs 214, 1.00 x |
| inactive IoU | 0.5147 | 0.5128 | -0.0019 [-0.0354, +0.0319] | -0.0017 [-0.0394, +0.0340] |
| mIoU-R13 | 0.6191 | 0.6189 | -0.0001 [-0.0039, +0.0036] | -0.0001 [-0.0050, +0.0041] |
| width ratio | 1.0042 | 1.0042 | 1.000 | 1.000 |

OP-W is identical to OP-A (the read's width-matched bias is 0 for both arms). Verdict line (x4_verdict.py): **PPCC: SCREEN
FAIL (NO LOSS); headline items passing 0 of 4; failing guard items 0.** The crack contrast is exactly 0 because L = 0 left
every crack px unchanged; the only change is the small inactive island removal, which did not carry to the held-out folds
(inactive IoU -0.0019, n.d.; inactive recall 0.6289 -> 0.6263, inactive region precision 0.7751 -> 0.7703).

S: the nnU-Net-style filter has nothing to act on here: COMBO's isolated short false-crack components are rare (the
false-crack guard is about 1 px per crack-free cell), and its short components are mostly true crack pieces. Not worth a
GPU slot; do not add it to C2.

## 2. D4 label-safety audit, per class (E, C/d4_audit.py -> O/d4/d4_audit.txt)

Source: the registered final TTA read `bench_reads/final_tta` (read.json e9692e7e): its cached argmax records (24 x 24
confusion per cell, the very records that read scored), 532 cells, seeds 5 to 9. No dump or label re-read. Pairs: CS -> CS_D4
(COMBO swad readout without / with D4 TTA; primary), PF -> PF_D4 and CB -> CB_D4 beside it. Same checkpoints in each pair,
so the interval is paired (one seed draw per fold for both; crossfit_op.boot_pair paired_seeds=True, cv5v3 groups, 2,000
draws); the unpaired interval (the read's default) is in the file.

Prior facts (E): every arm trains with `data.augmentation=labelsafe` = HorizontalFlip + VerticalFlip + RandomRotate90
(el-fault-detection src/data/augmentations.py `get_labelsafe_augmentation`), i.e. the whole D4 group is already a training
augmentation with the mask transformed alike. None of the 24 classes (bench/cv5v3.py CLASS_NAMES) is orientation-specific by
definition: there is no half-cell, busbar-direction or "sp mono halfcut" class (sp_multi / sp_mono / sp_dogbone are spacing
types). The pool has no half-cut cells.

### 2.1 Classes D4 lowers (paired 95% CI below 0), CS -> CS_D4
| class | GT cells | IoU plain -> D4 | delta [paired 95% CI] | precision | recall | same in PF->PF_D4 / CB->CB_D4 |
|---|---|---|---|---|---|---|
| 15 gridline | 358 | 0.2976 -> 0.2832 | -0.0144 [-0.0212, -0.0079] | 0.639 -> 0.671 | 0.358 -> 0.329 | -0.0071 [-0.0134, -0.0019] / -0.0104 [-0.0162, -0.0046] |
| 16 splice | 60 | 0.0024 -> 0.0005 | -0.0020 [-0.0073, -0.0000] | 0.269 -> 0.269 | 0.002 -> 0.000 | -0.0118 [-0.0275, -0.0026] / -0.0044 [-0.0155, -0.0003] |

Down but n.d. (CS -> CS_D4): text (16 cells) -0.0136 [-0.0665, +0.0586]; jbox (9 cells) -0.0472 [-0.1730, +0.0193];
dead_cell (2 cells) -0.0001. Raised (CI above 0): background, sp_mono, crack +0.0128 [+0.0080, +0.0182]. Inactive +0.0167
[-0.0075, +0.0431] n.d. Classes 8, 10, 12, 19, 23 have IoU 0 in both (1 to 4 GT cells, never predicted).

S: the two lowered classes are thin, faint line classes; D4 raises their precision and lowers their recall, the signature of
averaging 8 views over low-confidence thin structures (a px must win in most views to survive). It is not a label-orientation fault: gridlines rotate with the image and their labels rotate
alike, training saw all 8 views, and no class name or definition depends on orientation. Text and jbox are the only classes
whose appearance is orientation-specific (printed characters, junction box); both are tiny and n.d. Both lowered classes are
in R13, so they cost mIoU-R13 a little; the registered final read already holds the mIoU-R13 guard for D4.

## 3. Error census of COMBO (E, C/census.py -> O/census/census.txt; seeds 5 to 9, 532 cells, argmax)

Not in the existing census: `results/stageC/GAP_CENSUS.md` (15 Nov) is PF on cv5v2 with the small / whole / gap / end
buckets only, and the ledger REPORT reuses it (gap_census OPEN). Added here: COMBO on cv5v3, length buckets, contact,
source, false-crack px by GT class; the 15 Nov buckets are recomputed on COMBO with `gap_census.census_cell` unchanged.
Definitions: missed = GT crack px with no predicted crack px within 2 px (exactly the relR@2 miss); missed length = skeleton
px of the GT crack mask that are missed. Component = 8-connected GT crack component; length = its skeleton px. Contact =
within 2 px of GT busbars (9) or ribbons (4) / of the image border or GT border (5), padding (7), frame_edge (21). Shares
are of all missed px summed over cells and seeds; intervals two-stage group bootstrap (gap_census.boot, cv5v3 groups).
relR@2 0.819 [0.769, 0.861]; GT crack 307,546 px, missed 55,623 px per seed.

### 3.1 By component length
| GT component length (skeleton px) | comps / seed | missed whole / seed | share of GT px | miss rate | share of missed px | share of missed length |
|---|---|---|---|---|---|---|
| 1 to 9 | 139 | 70.2 | 0.005 [0.003, 0.007] | 0.539 [0.426, 0.661] | 0.015 [0.008, 0.024] | 0.013 [0.006, 0.023] |
| 10 to 24 | 153 | 36.0 | 0.018 [0.014, 0.025] | 0.362 [0.269, 0.471] | 0.037 [0.024, 0.056] | 0.037 [0.022, 0.058] |
| 25 to 49 | 204 | 32.4 | 0.051 [0.038, 0.069] | 0.265 [0.196, 0.342] | 0.075 [0.052, 0.112] | 0.078 [0.051, 0.120] |
| 50 to 99 | 217 | 16.6 | 0.110 [0.080, 0.152] | 0.205 [0.154, 0.267] | 0.124 [0.082, 0.190] | 0.130 [0.083, 0.206] |
| 100 to 199 | 213 | 7.2 | 0.203 [0.162, 0.260] | 0.162 [0.118, 0.220] | 0.182 [0.135, 0.253] | 0.157 [0.120, 0.215] |
| 200 to 399 | 123 | 2.4 | 0.230 [0.178, 0.294] | 0.161 [0.111, 0.219] | 0.204 [0.144, 0.275] | 0.185 [0.128, 0.257] |
| >= 400 | 72 | 0.0 | 0.383 [0.243, 0.493] | 0.171 [0.101, 0.268] | 0.362 [0.185, 0.486] | 0.401 [0.216, 0.526] |

S: short components are missed most often (half of those under 10 px; 106 of the 292 components under 25 px per seed are missed whole), but they are 0.023 of GT px, so even perfect recall on them would add at most 0.05 of the miss = about 0.009 relR@2.
The miss is dominated by components of at least 100 px (0.75 of missed px), and inside them by ends and interior gaps
(3.4).

### 3.2 By contact
| contact | comps / seed | share of GT px | miss rate | share of missed px | share of missed length |
|---|---|---|---|---|---|
| none | 75 | 0.014 [0.008, 0.023] | 0.408 [0.195, 0.611] | 0.032 [0.012, 0.062] | 0.031 [0.013, 0.058] |
| busbar / ribbon only | 683 | 0.572 [0.492, 0.644] | 0.160 [0.123, 0.208] | 0.506 [0.416, 0.593] | 0.493 [0.396, 0.595] |
| cell edge only | 75 | 0.047 [0.028, 0.071] | 0.265 [0.130, 0.439] | 0.069 [0.027, 0.129] | 0.051 [0.022, 0.097] |
| both | 288 | 0.368 [0.292, 0.445] | 0.194 [0.132, 0.256] | 0.394 [0.294, 0.488] | 0.425 [0.303, 0.529] |

S: touching a busbar / ribbon is the normal case (ribbons are labelled in 523 of 532 cells and cracks start there), so it
does not single out a failure mode; the miss rate of busbar-touching components (0.16) is the lowest of the four. Edge-only
components miss more (0.27) but hold 0.07 of the miss. The length x contact point table is in census.txt.

### 3.3 By source
| source | share of GT px | miss rate | share of missed px | share of missed length |
|---|---|---|---|---|
| ARTS | 0.043 [0.019, 0.085] | 0.214 [0.120, 0.344] | 0.051 [0.020, 0.102] | 0.061 [0.024, 0.127] |
| BMRK | 0.111 [0.058, 0.201] | 0.189 [0.131, 0.253] | 0.116 [0.056, 0.222] | 0.071 [0.032, 0.142] |
| CFVS | 0.654 [0.457, 0.786] | 0.151 [0.100, 0.214] | 0.544 [0.306, 0.714] | 0.584 [0.345, 0.756] |
| CSIR | 0.191 [0.082, 0.351] | 0.274 [0.153, 0.483] | 0.289 [0.145, 0.479] | 0.284 [0.134, 0.491] |
| SDLE | 0.001 [0.000, 0.005] | 0.020 [0.010, 0.037] | 0.000 [0.000, 0.001] | 0.000 [0.000, 0.001] |

S: CSIR has the highest miss rate (0.27) and is the source of E1 (101 of 106 cells), consistent with recall being the weak
point on unseen modules.

### 3.4 The 15 Nov buckets on COMBO (PF cv5v2 in brackets from GAP_CENSUS.md, gaint / cv02)
share of miss: small 0.011 [0.005, 0.021] (0.010), whole 0.191 [0.110, 0.301] (0.17 / 0.20), gap 0.276 [0.191, 0.357]
(0.28), end 0.522 [0.436, 0.613] (0.53 / 0.51). Of GT px: bound_gap 0.050 [0.031, 0.074], bound_end 0.094 [0.075, 0.117],
bound_whole 0.035 [0.018, 0.061].

### 3.5 False crack px by the GT class under them
Two views: all predicted crack px not on GT crack (137,746 px per seed; most of them are the 1 to 2 px width margin next to
GT crack, which relF1@2 forgives), and those beyond 2 px of GT crack (27,482 px per seed: the px that cost relP@2).

| GT class under the false crack px | share, all false px | share, beyond 2 px of GT crack |
|---|---|---|
| background (0) | 0.801 [0.719, 0.877] | 0.558 [0.386, 0.752] |
| inactive (11) | 0.145 [0.077, 0.222] | 0.331 [0.126, 0.517] |
| busbars + ribbons (9, 4) | 0.028 [0.020, 0.036] | 0.067 [0.045, 0.090] |
| gridline (15) | 0.013 [0.003, 0.025] | 0.016 [0.003, 0.035] |
| scuff / star = ignore (v1.1, not scored) | 0.003 [0.000, 0.007] | 0.013 [0.000, 0.034] |
| spacing (1, 2, 3) | 0.004 [0.002, 0.006] | 0.010 [0.004, 0.018] |
| material (13) | 0.006 [0.000, 0.020] | 0.003 [0.000, 0.012] |
| other | 0.001 | 0.002 |

S: a third of the relP@2 loss is crack predicted inside GT inactive regions. That is likely partly a label convention (cracks
inside dark inactive areas are labelled inactive, not crack) rather than a pure model error; worth a look at a few cells
before any precision arm targets it. Gridline and busbar confusions, the usual suspects, are small (0.08 together).

## Commands (gaint)
```
cd /home/yugma/mtp/research/team_2026-11-27_arch/cpu
# task 1 (tmux bench_cpu_pp): sweep + cross-fit -> derived dumps -> read_x4
bash run_pp.sh > run_pp.log 2>&1
#   = PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=1 nice -n 19 <venv python> pp_sweep.py --seeds 5,6 --workers 8
#     ... pp_write.py --seeds 5,6 --workers 8
#     ... harness/x4/read_x4.py --out O/read_pp --base COMBO --cache O/cache --arm "COMBO=$COMBO_T:5,6:swad"
#         --arm "PPCC=O/pp_dumps/elbench1/hrnet_w18_unetpp_swad_const_pf_v11/c3x_hrnet_swad_v11_f{k}_s{s}.swad.ppcc:5,6:swad"
#         --arm "PFAA=$PF_T:5,6,7,8:model" --pair COMBO=PPCC --aa PFAA:5,6:7,8 --verdict PPCC   (templates: harness/x4/x4_arms.sh)
# task 2 (tmux bench_cpu_d4)
PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=1 nice -n 19 /home/noob/work/el-fault-detection/.venv/bin/python d4_audit.py
# task 3 (tmux bench_cpu_census)
PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=1 nice -n 19 /home/noob/work/el-fault-detection/.venv/bin/python census.py --seeds 5,6,7,8,9 --workers 8
```
census.py ran three times: tries 1 and 2 computed and cached the per-cell vectors, then failed in the summary step on a
module-attribute swap of my own (`census_try1.log`, `census_try2.log`); the third run reused the cached cells (cell code
unchanged) and finished. No other retry.

## md5
Scripts (C): cpu_common.py 2cd2450c, pp_sweep.py f6b280a5, pp_write.py a4f89f33, run_pp.sh 389620b8, d4_audit.py 4d6f55ed,
census.py d6683230. Reused: harness/x4/read_x4.py 72b81006, x4_verdict.py 97e81b86, x4_arms.sh e5f88e99; read tree
bench_wt_final 89b9ea5 (0 tracked changes after all runs), bench_read_w1.py fdb56b78.

Outputs (O):
| file | md5 |
|---|---|
| pp/choices.json | 489cc6342e7aa670969949bf559eb4e8 |
| pp/sweep.txt | 2246622276df576a92c02379b6a05858 |
| read_pp/read/read.txt | d8864766a9cbb5e89aae8c5902be6878 |
| read_pp/read/read.json | e29f0de260f25444f99be166f4ed215a |
| read_pp/read/read_x416.txt | cb1538adf13b77d2022c252e3c2bd8e7 |
| read_pp/verdict.txt | 12ba6f636ce72d71aae66fd3d0891171 |
| read_pp/expected_dumps.tsv | 982f4131cddaadf7162ee0c9cd81552d |
| pp_dumps (10 PPCC manifests; md5 of their md5sum lines) | 70e15f3da1dfde9de8512df27e0846e6 |
| d4/d4_audit.txt | 0ed87df7e0c9b7e2180aad010d0c7aa2 |
| d4/d4_audit.json | 198304e7bbf559dd723cd76a428b7845 |
| census/census.txt | 5545e05ef02c3f94f67ba769998dc57c |
| census/census.json | 54843ff4e2883aa93d66e4de60d2e940 |
| input: bench_reads/final_tta/read/read.json | e9692e7e324264dceffec9e15c8375cd |

Logs: C/run_pp.log, C/d4_audit.log, C/census.log (+ census_try1.log, census_try2.log). tmux sessions bench_cpu_pp,
bench_cpu_d4, bench_cpu_census have exited.

## Notes and limits
- Task 1 OP-F and OP-W of PPCC: the bias sweep of the read acts on the post-processed dump (removed crack px stay off at every
  bias; new components a positive bias would create are not filtered). With L = 0 everywhere this matters for nothing.
- Task 1 inactive removal writes background (no logp in the dumps); a runner-up-class rule would need logp dumps.
- Task 3 contact: ribbons are labelled in 523 of 532 cells, so most crack components touch a busbar / ribbon (physically
  cracks often start there); the contact split is therefore coarse.
- Disk: O/pp_dumps (1.3 GB) was deleted on the lead's word (27 Nov, after the read); the read's records stay cached in O/cache.

## 4. Endpoint extension + gap bridging on the crack margin (POST-HOC ARM EXT; added 27 Nov on the lead's request)

**Status: post-hoc.** The arm was motivated by section 3 (ends 0.52 and interior gaps 0.28 of the miss), which was read on these
very cells; the parameters are cross-fitted, the arm is still post-hoc.

**Margin available (E).** The dumps hold `m_crack` = log s_crack - max over the other 23 classes of log s (float16;
dumpfmt.py), which is exactly the margin the method needs. No logp is needed.

**Rule (C/ext.py 59c9cc60).** P = argmax crack; skeleton by bench/skel.py; endpoints = skeleton px with one skeleton
neighbour, traced back up to 8 px (skipped if fewer than 2 px behind them).
- Extension (k, t, ang, L): direction = endpoint minus the traced px k back. Each step takes the 8-neighbour within ang degrees
  of the direction that has the highest margin, and accepts it if margin > t. Px of the endpoint's own component are walked
  through and not added. Reaching another component or the image edge stops the walk. The direction is re-estimated over the
  last k px. At most L steps.
- Bridging (k, t, ang, d): two endpoints of different components, at most d px apart and facing each other (each
  direction within ang of the line to the other). The straight segment is added if every new px on it has margin > t.
- Walks and bridges start from the original P; result = P | added. Derived dump: pred = 14 and m_crack = max(m, +0.0005) on
  added px, so the dump stays consistent (any negative crack bias removes them again).
- Grid: k (4, 8) x t (-8, -5, -3, -2, -1.5, -1, -0.5) x ang (30, 50) x L (0, 3, 6, 12, 24) x d (0, 4, 8, 16) = 560, plus
  identity. t goes down to -8 because the smoke test showed the margin below -5 within 2 to 3 px of most endpoints.
- Cross-fitting as PPCC: per seed and held-out fold, the candidate with the highest pooled crack relF1@2 on the other four
  folds of the same seed (crossfit_op.crack_counts / cmetrics); ties -> the earlier candidate (identity first).

### 4.1 Where the missed crack sits on the margin (E, C/margin_hist.py -> O/ext/margin_hist.txt; seeds 5, 6; descriptive)
| px pool (keep px, summed over 2 seeds) | px | median m | m >= -8 | m >= -5 | m >= -3 | m >= -1 |
|---|---|---|---|---|---|---|
| missed GT crack (relR@2 miss) | 109,544 | -12.75 | 0.098 | 0.027 | 0.009 | 0.001 |
| missed GT crack within 8 px of P | 53,589 | -11.75 | 0.151 | 0.042 | 0.014 | 0.002 |
| non-crack px 1 to 8 px from P and > 2 px from GT crack | 2,386,437 | -15.25 | 0.055 | 0.020 | 0.010 | 0.003 |
| covered GT crack (for reference) | 505,548 | +4.75 | 0.876 | 0.794 | 0.744 | 0.698 |

In the 1 to 8 px band around predicted cracks, non-crack px with m >= t outnumber missed crack px with m >= t by 16:1 (t = -8),
22:1 (-5), 32:1 (-3) and 80:1 (-1). S: COMBO is confidently wrong on the crack it misses, so the margin carries little
information there; the direction prior is what keeps the walk from flooding.

### 4.2 Cross-fitted choices (E, O/ext/sweep.txt, choices.json)
All 10 fits chose ang 50, t = -8 (the lowest grid value) and k 4 (one fit k 8). L was 24 (4 fits), 12 (2) or 6 (4); d was 0
(7 fits), 4 (1) or 16 (2). Bridging hardly matters: bridge-only candidates give at most +0.0005 relF1@2 in-sample, from 100 to
650 added px per seed. Fit-set gains were +0.004 to +0.006.

### 4.3 Read (E, read_x4.py -> O/read_ext; EXT vs COMBO, seeds 5, 6; PFAA for M = 0.0100)
| metric | COMBO OP-A | EXT OP-A | EXT - COMBO, OP-A [95% CI], 532 cells | 416 clean cells | EXT - COMBO, OP-W |
|---|---|---|---|---|---|
| crack relF1@2 | 0.8647 | 0.8693 | **+0.0045 [+0.0002, +0.0092]** | +0.0054 [+0.0001, +0.0112] | -0.0005 [-0.0047, +0.0035] |
| relP@2 | 0.9123 | 0.9041 | -0.0082 [-0.0154, -0.0024] | -0.0088 [-0.0174, -0.0008] | +0.0014 |
| relR@2 | 0.8219 | 0.8371 | +0.0151 [+0.0104, +0.0206] | +0.0165 [+0.0102, +0.0232] | -0.0020 |
| strict crack IoU | 0.3822 | 0.3822 | +0.0000 | +0.0003 | -0.0012 |
| width ratio (band 0.85 to 1.15) | 1.0042 | 1.0297 | 1.025 x (PASS) | 1.028 x | 0.986 x |
| false crack px on crack-free cells (<= 1.5 x) | 286.5 | 385.5 | **1.35 x** (PASS) | 294 vs 214, 1.38 x | 0.95 x |
| inactive IoU / mIoU-R13 | 0.5147 / 0.6191 | 0.5138 / 0.6190 | -0.0009 / -0.0001 | -0.0009 / -0.0000 | +0.0003 / -0.0001 |

Per seed OP-A relF1@2: s5 +0.0048, s6 +0.0043. Verdict (x4_verdict.py): **EXT: SCREEN FAIL (NO LOSS); headline items passing
0 of 4; failing guard items 0.** The OP-A interval excludes 0 but the gain is under M = 0.010. OP-W is not an independent
test here: the width-matched bias for EXT is -0.25, which removes every added px (they carry m = +0.0005), so OP-W returns
COMBO at a slightly negative bias.

Against COMBO's own best plain crack bias (the read's cross-fitted OP-F): COMBO OP-F relF1@2 0.8665 (P 0.8948, R 0.8400). So
EXT at argmax (0.8693) is about +0.003 above what a global bias already gets. EXT OP-F - COMBO OP-F = +0.0010 [-0.0036, +0.0060].

### 4.4 Is the grid edge hiding more? (E, C/ext_boundary.py e5e7cd98 -> O/ext/boundary.txt; in-sample, k 4, ang 50, d 0)
| t | best L | relF1@2 s5 / s6 (identity 0.8635 / 0.8660) | relP@2 s5 | relR@2 s5 | width s5 | false px crack-free s5 (228) |
|---|---|---|---|---|---|---|
| -8 | 24 / 6 | 0.8685 / 0.8704 | 0.9015 | 0.8377 | 1.021 | 323 |
| -12 | 12 / 6 | 0.8691 / 0.8708 | 0.8956 | 0.8441 | 1.035 | 346 |
| -20 | 6 | 0.8673 / 0.8691 | 0.8948 | 0.8414 | 1.035 | 325 |
| none (geometry only) | 6 | 0.8664 / 0.8686 | 0.8929 | 0.8414 | 1.037 | 326 |

The in-sample peak is +0.0056 / +0.0048 (t = -12), only +0.0006 above t = -8. Extending every endpoint 6 px straight ahead,
with no margin at all, already gives +0.003. S: most of the gain is geometric. GT crack ends run a few px past COMBO's
predicted ends, and a short straight extension covers them within the 2 px tolerance. That looks like a label / end
convention effect rather than recovered cracks. No setting reaches M.

### 4.5 Relation to the closed DTI arm and to Curvi-Tracker
- DTI hysteresis (T5 arm 1, bench/postproc/hysteresis.py; closed 14 Nov) grew every 8-connected region of {m > t_lo} that
  touched a seed px of m > t_hi: isotropic growth, which was null on PF (+0.0003 [-0.0010, +0.0019] on W1-G, null on cv02).
  EXT restricts growth to 1-px walks from skeleton endpoints along the local direction (plus facing-endpoint bridges). Here
  that buys a measurable but sub-M gain (+0.0045 vs DTI's +0.0003), at the cost of 1.35 x the false crack px on crack-free
  cells. The direction prior lets it go much lower in t (-8 vs DTI's grid floor of -6 for t_lo, where isotropic growth floods).
- Curvi-Tracker (doi:10.1016/j.patcog.2025.112797; scouts/thin/REPORT.md item 4, NEW): a learned, patch-trained tracker run
  iteratively after a segmenter, scored with a 2 px slack; it raises completeness and slightly lowers correctness. EXT is its
  training-free counterpart: hand-set direction and margin rules on the segmenter's own margin. Our result shows the same
  pattern (relR +0.015, relP -0.008). S: the margin does not hold the missed cracks (4.1), so a tracker that reads only the
  segmenter's output inherits that ceiling. A learned tracker would need its own image evidence (it reads image patches)
  to do better; whether that evidence exists in EL images for the missed ends is open. Our cheap version stays under M.

### 4.6 Commands and md5 (gaint)
```
cd /home/yugma/mtp/research/team_2026-11-27_arch/cpu
bash run_ext.sh > run_ext.log 2>&1        # tmux bench_cpu_ext: ext.py sweep -> ext.py write -> read_x4 (COMBO, EXT, PFAA)
#   read_x4.py --out O/read_ext --base COMBO --cache O/cache --arm "COMBO=$COMBO_T:5,6:swad"
#     --arm "EXT=O/ext/dumps/elbench1/hrnet_w18_unetpp_swad_const_pf_v11/c3x_hrnet_swad_v11_f{k}_s{s}.swad.ext:5,6:swad"
#     --arm "PFAA=$PF_T:5,6,7,8:model" --pair COMBO=EXT --aa PFAA:5,6:7,8 --verdict EXT
PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=1 nice -n 19 <venv python> margin_hist.py --seeds 5,6 --workers 6
PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=1 nice -n 19 <venv python> ext_boundary.py > O/ext/boundary.txt
```
Scripts: ext.py 59c9cc60, margin_hist.py 31212340, ext_boundary.py e5e7cd98, run_ext.sh 181bb1e3 (cpu_common.py 2cd2450c).
ext_boundary.py's first launch failed at parse (an f-string quoting error); it was fixed by sed and rerun with no other change.

| file (O) | md5 |
|---|---|
| ext/choices.json | f06c1b06392e70457502f07c0c8ce49f |
| ext/sweep.txt | 6762656f951ce070eb81a7fbaf5cc0b9 |
| ext/margin_hist.txt | 12ef933c1dc26f68d13342b8dff22285 |
| ext/margin_hist.npy | cd00bd3ab5de5240ff28ea15b1131a49 |
| ext/boundary.txt | bfc57dc13d230fc1287c8d8aa01cec12 |
| read_ext/read/read.txt | 60b96fb292f563cf518c2c153dfbbf58 |
| read_ext/read/read.json | 47f33b654b80385592b2fcccb2698807 |
| read_ext/read/read_x416.txt | 4f1369152448796a2cb43e64ad7391ae |
| read_ext/verdict.txt | 32c94d15d68bf6191731eae5d402640a |
| read_ext/expected_dumps.tsv | e89a627033f5508106bb708a92e9c0f6 |
| ext/dumps (10 EXT manifests; md5 of their md5sum lines) | 87a8fef92cc4706034e67db45bc4d4a0 |

bench_wt_final: 0 tracked changes after all runs. O/ext/dumps holds 1.3 GB (gaint 28 GB free); to be deleted on the lead's
word, as pp_dumps was.

### 4.7 Reading (S)
A post-hoc, training-free endpoint extension buys about +0.004 to +0.005 relF1@2 on COMBO (relR +0.015, relP -0.008). That is
under M, and only about +0.003 above a plain crack bias. The gain is mostly geometric (end length), not recovered cracks:
the missed crack px have a median margin of -12.75, so no post-process on this model's margin can reach them. Closing the
recall gap needs a change in the model (training signal or evidence), not post-processing of its outputs.
