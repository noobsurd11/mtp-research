# B6 build: fold roots, data-build checks, held-out scorer, verdict script

builder, 1 Nov 2026 (respawned 23:28; the predecessor's 21:29-21:36 gaint work was re-verified, then completed). Code **e544133 unchanged** (no new code key). Protocol: `protocol_B6.md` v1.0.1, on disk md5 e1f1c894. Tags: E (measured, path given), S (judgement).

All gaint work: CPU only (`CUDA_VISIBLE_DEVICES=""`), `nice -n 19`, <= 8 threads. Nothing touched cv02. No test or E1 image, mask or prediction was read. The one m0 file used (opening-1, `f3_SUPPF_100pct_s0.json`) is indexed on its `val` block only.

## 0. Status for coach (§8.2)
| Item (§8.2) | State |
|---|---|
| 5 fold roots + md5s + 0-test / 0-E1 assert | DONE, re-verified (§2) |
| Per-root CPU data build ('Labelled: ...' + CE weights) | DONE (§3). **Protocol text issue:** the CE line is 'none (plain CE)' for every run (ce_dice); see §3.2 |
| Root-mechanism identity (judge B6-4: 5 steps) | DONE, IDENTICAL (§4) |
| Held-out scorer with the stem / step / no-test asserts | DONE (§5) |
| Scorer = opening-1 m0 val cells **exactly** | CPU fp32: within 0.0034, not exact (expected). **GPU bf16 on gaint: EXACT PASS** (2 Nov 01:23; §9) |
| Pooled OOF inactive IoU + two-stage paired bootstrap (§4) | DONE, self-tested (§6) |

## 1. Inputs (E, md5 checked by the build scripts)
| File | md5 |
|---|---|
| `results/b6/b6_folds.tsv` (coach) | e2cafce1 |
| `judge/out/b6_groups.tsv` (judge) | 5ff33e20 |
| el_f3 `data/splits/train.txt` / `val.txt` / `test.txt` | 842f27c4 / 9dcccf00 / a31fad14 |
| ext117 `stems_eval.txt` (106) / `stems.txt` (117), gaint `cv02_noob_el/ext117/` | 5266806b / 69e5cff3 |
| Code: gaint `el_f3`, HEAD e5441339 (REVISION e544133; untracked = experiments/ + REVISION only) | |
| `labeled/` = gaint `/home/noob/work/el-fault-detection/data/labeled` (= `el_f3/data/labeled` resolved) | DATA_MANIFEST below |

## 2. Fold roots (gaint `/home/noob/work/b6/`)
Built by `scripts/b6/b6_make_roots.py` fe70fbaf (log `b6_build/make_roots.log`).
- **Layout of `b6_root_k`:**
  - `splits/train.txt` = the 4 other folds; `splits/val.txt` = `splits/test.txt` (byte-identical) = fold k;
  - order: el_f3 train.txt order, then val.txt order;
  - `labeled` → symlink (gaint only; on cv02 runner deploys a fresh `labeled/` of the 532 stems).
  - `SPLITS.md5` (3 lines) and `DATA_MANIFEST.md5` (1,064 lines = images + masks_escdd of the 532 stems; identical in all roots).
- **Asserts in the script:**
  - pool = train ∪ val = 532;
  - phys_group = judge's for every stem; 0 of 334 groups split;
  - 0 test / 0 ext117 stems in the pool;
  - re-read from disk after writing; `md5sum -c` on both manifests.

| fold | train | held-out (val = test) | groups | SPLITS.md5 | train.txt | test.txt = val.txt |
|---|---|---|---|---|---|---|
| 0 | 425 | 107 | 66 | 09df4260 | 96d3154c | 7e107038 |
| 1 | 425 | 107 | 68 | 3a2c7677 | 00fb2ec7 | a2d5c07d |
| 2 | 426 | 106 | 64 | 8a55be01 | b544765b | 549f36cf |
| 3 | 426 | 106 | 69 | fdb319bd | 4d4e8904 | 20a03925 |
| 4 | 426 | 106 | 67 | 2f3f8ef1 | c57b0b94 | 40cda7ef |

- DATA_MANIFEST.md5 **2630f630**. ROOTS.md5 **e4100381** (25 lines: the 5 files × 5 roots + the forbidden list).
- `b6_forbidden.txt` **9bb4d919**: 167 stems, sorted = real test 50 ∪ ext117 117 (stems.txt ⊇ stems_eval.txt). This is the scorer's refusal list. Names only, no data. A copy is in `results/b6/b6_forbidden.txt`.
- **E, my re-check (23:35, own code, not the build script):**
  - `md5sum -c` of ROOTS.md5, and of each root's SPLITS.md5 and DATA_MANIFEST.md5: all OK;
  - forbidden list = test ∪ ext117 (50 + 117);
  - per root: val = test, held-out = fold k, train = the other 4 folds, no duplicates, 0 forbidden stems; held-outs partition the 532;
  - order rule holds for all 10 lists.

## 3. Per-root CPU data build (§3 run asserts)
`scripts/b6/b6_databuild_check.py` 061a3964. It uses e544133's own `apply_opts`, `build_benchmark_data` and `build_losses`, on pf2_{SUP,SUPPF}_100pct_s5 opts (pf2_jobs.txt) + `data.root=<root>`. Output: gaint `b6_build/databuild/databuild.txt` 72b05058, `databuild.json` def5e001.

### 3.1 Lines every B6 run must log (both arms identical; asserted)
- **Control:** with `data.root=data`, the harness prints the PF2 train.log lines exactly, and config = pf2 s5 `config_used.yaml` exactly, for both arms.

| fold | 'Labelled:' line (runner's per-run assert) | 'CE class weights:' | 'Zero-pixel classes in labelled subset (weight 0):' | train inactive px | train crack px |
|---|---|---|---|---|---|
| 0 | `Labelled: 425 (<root>/splits/train.txt)  unlabelled: 0 (-)  val: 107  test: 107` | none (plain CE) | ['belt_mark'] | 228,267 | 260,385 |
| 1 | `Labelled: 425 (...)  unlabelled: 0 (-)  val: 107  test: 107` | none (plain CE) | none | 227,455 | 251,108 |
| 2 | `Labelled: 426 (...)  unlabelled: 0 (-)  val: 106  test: 106` | none (plain CE) | ['rings'] | 227,878 | 250,382 |
| 3 | `Labelled: 426 (...)  unlabelled: 0 (-)  val: 106  test: 106` | none (plain CE) | ['clamp'] | 228,235 | 209,542 |
| 4 | `Labelled: 426 (...)  unlabelled: 0 (-)  val: 106  test: 106` | none (plain CE) | none | 228,245 | 267,555 |

- `<root>` is the absolute root path runner uses on cv02. The line prints it verbatim, so runner's assert should substitute it.
- Train inactive / crack px = pool total minus fold k's (asserted against b6_folds.tsv).
- The full 24-class count table per fold is in databuild.txt / databuild.json: this is the "CE-weight table" in its only meaningful form (§3.2).
- Config diff of each (fold, arm) build vs pf2 s5 = `data.root` only. In the real jobs, `seed` and `run_name` also differ, as runner's job file states.

### 3.2 Protocol text issue for coach (S; no design change)
- E: PF2 opts use `loss.supervised=ce_dice`. `CEDiceLoss` is unweighted (`src/losses/ce_dice.py` l.33). `build_losses` takes class counts only for weighted_ce and semi_ce (`loss_factory.py` l.41-47). `semi_ce` is built but never used for `method=supervised` (`trainer.py` l.256: `self.ssl` only for mean_teacher / pvs3).
- So every B6 run logs 'CE class weights: none (plain CE)', and fold class counts do not enter training.
- Consequences:
  - §3's "CE class weights equal to builder's CPU computation (tol 1e-3)" holds trivially;
  - judge B6-4's "assert they differ from the full-train weights" cannot hold.
- The fold-dependent asserts are the 'Labelled:' line and the 'Zero-pixel classes' line.
- **Suggested §3 wording:** "'CE class weights: none (plain CE)' (ce_dice) and the 'Zero-pixel classes' line equal to build_b6 §3.1".
- **Disclosure (both arms alike):** three classes have 0 training px in one fold each, because all their px sit in that fold's held-out cells (E, databuild class counts; ids from `src/data/class_info.py`):
  - belt_mark (id 19, defect): 21,935 px, fold 0;
  - rings (id 12, defect): 1,204 px, fold 2;
  - clamp (id 8, feature): 1,238 px, fold 3.
- These are not primaries.

## 4. Root-mechanism identity (judge B6-4)
`scripts/b6/identity_cpu.py` 962379a6: real e544133 training steps on CPU fp32, PF2 SUPPF s5 opts. A uses `data.root=data`; B uses gaint `b6_build/idroot` (real train.txt; val.txt = test.txt = the real val; `labeled` symlink).
- **3 steps** (predecessor, `idchk.sh` 96d925da, 21:34): IDENTICAL.
- **5 steps** (mine, `idchk5.sh` 81c42b58, 23:37-23:39; A d683d69a, B 3a66c3bf): IDENTICAL.
  - Same in A and B: init state 56a9ee7f, class counts 262f92a5, the fixed batch, and at every step 1-5 the loss repr, lr, parameter sha and fixed-batch logits sha.
  - Step-5 loss 4.154092311859131, param sha 4a216d9d.
- So a root that only re-points `data.root` changes nothing else in the training path.

## 5. Held-out scorer
`scripts/b6/b6_score.py` **981b5f29** (gaint `b6_build/scripts/`).

### 5.1 Behaviour
- Per run: `checkpoints/latest.pth` (never best.pth), argmax, bf16 autocast on CUDA, batch 8, TTA off, m0 per-cell schema (conf 24×24, crack_rel2, crack_cc, inact_cc, p-bands, h1000).
- Scores only the `--stems` cells. GT = `<data.root>/labeled/masks_escdd`, from the run's own config_used.yaml.
- **Line-identity with `el_f1/reports/f1/m0_audit_tau.py` d77241bb** (E, ast extraction, 23:31): `comps`, `BANDS`, `cell_stats`, `dihedral` and `predict` are IDENTICAL.
  - Model build: same lines as m0 (`encoder_init` dropped, `encoder_weights=None`, `models["model"]`).
- The 54 val masks in `escdd_masks/val` (m0's GT) are byte-identical to `labeled/masks_escdd` (E, `cmp`, 54/54).

### 5.2 Asserts (before the model is built, per run)
- method supervised; `data.root` absolute; mask_subdir `labeled/masks_escdd`; total_steps 20000.
- `--stems` == `<data.root>/splits/test.txt` (same stems, same order) == `val.txt`. This is coach's / builder's §3 assert.
- No stem of `--stems` or of the root's `train.txt` is in `b6_forbidden.txt` (md5 pinned 9bb4d919, 167 stems). Held-out and train are disjoint.
- **Mode b6:** the held-out set is exactly one fold of b6_folds.tsv (md5 pinned e2cafce1), and train.txt = the other 4 folds.
- **Mode check:** the held-out set = the 54 val stems (sha256 pinned).
- latest.pth carries **step 20000** (judge note 1).
- After inference: output cell set == `--stems`.
- Output `<out>/<run>.b6.json` records: fold, seed, arm (PF iff `training.encoder_pf` is set), the weights / config / stems / root-split md5s, scorer md5, device, and code revision.
- No m0_audit default, rescore or LA pass is ever run (§3).

### 5.3 Check on f3_SUPPF_100pct_s0, 54 val cells, vs its opening-1 m0 val block
`scripts/b6/b6_valcmp.py` 1ad95d68 (stdlib only; indexes `m0["cells"]["val"]` only). Check root: gaint `b6_build/check/valroot` (splits = el_f3 val.txt; config = the run's config_used.yaml with data.root changed only, `diff` checked).
- **CPU fp32** (`scorechk.sh` 0be80a2c, 21:35, rc 0; out f3_SUPPF_100pct_s0.check.json 1ee0b18d; `check/valcmp_cpu.txt` bf8437bc):

  | pooled over 54 | b6 CPU | m0 (GPU bf16) | Δ |
  |---|---|---|---|
  | crack IoU | 0.43131 | 0.43132 | −0.00001 |
  | relF1@2 | 0.88829 | 0.88877 | −0.00049 |
  | inactive IoU | 0.56395 | 0.56060 | +0.00335 |
  | crack comp R / P | 0.800 / 0.960 | 0.800 / 0.973 | 0 / −0.013 (one pred component) |
  | inactive comp R / P | 0.650 / 0.500 | 0.650 / 0.500 | 0 / 0 |
  | mIoU (24) | 0.47948 | 0.47904 | +0.00044 |

  - 0 of 54 conf records equal; 6,778 of 14.2 M px flip (4.8e-4); max 476 px in one cell.
  - This is fp32 vs bf16, as expected.
  - S: inactive IoU moves 0.003 with dtype, so **all 20 B6 runs must be scored on one device type in bf16** (one scoring pass on cv02, as planned). The verdict script asserts one scorer md5 and one device string over all 20.
- **GPU bf16 exact pass:** requested from runner at 23:4x (`scorechk_gpu.sh` a7322114: the same scorer, `--device cuda`, then `b6_valcmp.py --expect exact`; it writes only under `b6_build/check/`).
  - The check order equals m0's: val.txt is sorted, the same as m0's sorted list, so the batches are identical.
  - PASS = all 54 per-cell records identical.
  - **Result: EXACT PASS** (§9).

## 6. Verdict script: pooled OOF inactive IoU + two-stage paired bootstrap (§4)
`scripts/b6/b6_verdict.py` **6d807784** (stdlib only; runs on the laptop or gaint; copy in gaint `b6_build/scripts/`).

### 6.1 Asserts (before any number is printed)
- Inputs md5-pinned: folds e2cafce1, groups 5ff33e20, forbidden 9bb4d919.
- Exactly one `<run>.b6.json` per (fold 0-4, arm house / PF, seed 5 / 6): 20 files.
- Each file: mode b6, step 20000, latest.pth, TTA off, `heldout` block only, cell set == its fold, 0 forbidden stems.
- **Arm / fold / seed vs run name (judge ask 1, added 23:42):** the scorer's arm label comes only from `training.encoder_pf`, so each file must carry run name `b6_{SUP,SUPPF}_f<k>_s<seed>` (runner's b6_jobs.txt 1fea91f5) matching its (arm, fold, seed). A mislabelled config fails here.
  - judge also asked for config_md5 constant within (arm, fold). It cannot be: config_used.yaml carries seed and run_name, so the two seeds' md5s differ by design. The config itself is covered by runner's per-run re-diff vs pf2 s5 (= data.root + seed + run_name only), which runs before a run counts.
- One scorer md5, one device and one code revision over all 20. Per fold, the 4 runs share the root test.txt / train.txt md5s. 20 distinct weights md5s.
- The 4 folds of each (arm, seed) cover the 532 stems exactly once.
- **GT guard:** every cell's conf row sum for inactive and for crack equals b6_folds.tsv's inactive_px / crack_px (coach's frozen masks_escdd counts).

### 6.2 Primary and CI (as §4)
- **Primary:** IoU_inact(arm, seed) = ΣTP / (ΣTP + ΣFP + ΣFN) over the 532 out-of-fold cells, from conf (argmax).
- **Δ** = mean over seeds 5, 6 of PF − mean of house.
- **Two-stage paired bootstrap:** B = 2,000, `random.Random(0)`. Per resample, in this order:
  - (a) 334 group indices drawn uniformly with replacement (groups sorted by name);
  - (b) for fold 0..4, for arm (house, PF), one seed drawn from (5, 6).
  - Each arm pools the drawn groups' cells (with multiplicity), each from its (fold, arm, drawn seed) run; Δ* = IoU_PF* − IoU_house*.
  - 95% percentile CI, linear interpolation (numpy default).
- **Verdict:** PASS iff lo > 0 and Δ >= 0.01; FAIL iff hi < 0; else n.d. Wording is §4's, fixed in the script.
- S, on (b): one draw per (fold, arm) is the protocol's text. With 2 seeds, its expected variance equals the variance of the 2-seed mean (plug-in (n−1)/n·s² = s²/2), so it is not narrower than the estimator. Drawing 2 seeds and averaging would halve that (too narrow). I kept the text.
- **Reported (§4):**
  - seed-pair Δ (s5, s6) + same-sign flag; one-stage CI (same group draws, the 4 runs fixed);
  - crack IoU and crack relF1@2 (pooled relP / relR at 2 px);
  - per source; per fold (5 × 2 × 2 table, Δ per fold-seed, sign count x / 10);
  - inactive comp R / P (Track M rule, as el_metrics.selfcheck: GT comps >= 20 px found iff >= 50% covered; pred comps >= 20 px correct iff any GT overlap);
  - leave-top-3-groups-out by inactive px;
  - twin groups (judge groups with > 1 image id: 13 groups, 56 cells, 47.6% of px) vs the rest.
- **Optional `--metrics`:** the 20 runs' metrics.json. This is judge item 7's cross-check: the trainer's end-of-run TEST block (final weights; here = the held-out fold) inactive IoU and GT px vs the scorer, per run.

### 6.3 Tests (E)
- `--selftest` (synthetic records built from b6_folds.tsv px; no model, no data): **PASS** on the laptop (python 3, stdlib) and on gaint (python 3.12.3).

  | case | result |
  |---|---|
  | PF = house | Δ 0, both CIs [0, 0], n.d. |
  | planted gain (TP 0.5 → 0.6 of GT) | Δ 0.099863 = hand ΣTP/(GT+FP) to 1e-12; PASS |
  | seed noise in PF only | two-stage CI [0.000, 0.080] wider than one-stage [0.040, 0.040]; Δs5 0, Δs6 > 0 |
  | PF worse | FAIL |
  | a run missing; a fold file holding a forbidden stem; arm label swapped vs run name (fold 2, s5) | assert fires |

- A dry run of the full report on synthetic files reproduces §2's structure (E):
  - 532 cells, 334 groups;
  - top-3 groups CFVS_00016 / CFVS_00130 / CFVS_00146 = 0.388 of inactive px (= protocol §2's 38.8%);
  - twin groups 13, 135,595 px = 0.476 of px (= §2's 47.6%);
  - 2,000 resamples in 1.2 s.

## 7. Commands for runner (after the 20 runs; scoring on gaint per protocol_B6 v1.0.2 §9)
- **The scorer takes the data root from each run's `config_used.yaml`.** That root is the cv02 path, e.g. `/tmp/noob_el/el_b6/b6_roots/b6_root_<k>`. It reads `splits/{train,val,test}.txt` and `labeled/masks_escdd` there. So on gaint the same absolute path must resolve to the gaint roots, whose split files are md5-identical (SPLITS.md5 / ROOTS.md5) and whose masks match DATA_MANIFEST 2630f630.
  - Without a code change (scorer md5 stays 981b5f29, the one in the exact-match check), do right before scoring: `mkdir -p /tmp/noob_el/el_b6 && ln -s /home/noob/work/b6 /tmp/noob_el/el_b6/b6_roots`.
  - Then: `cd /tmp/noob_el/el_b6/b6_roots/b6_root_<k> && md5sum -c SPLITS.md5 DATA_MANIFEST.md5` for k 0-4.
  - Replace `/tmp/noob_el/el_b6/b6_roots` with the ROOTBASE coach fixes.
  - The scorer records each root's test.txt / train.txt md5s, and the verdict asserts them per fold.
- **Each relayed run dir must hold** `config_used.yaml` and `checkpoints/latest.pth` (md5 both ends). The run dir's grandparent should hold a `REVISION` file (e544133), so the scorer records the code revision.
```
# gaint GPU, ONE bf16 pass for all 20, behind the scoring gate (runner):
python b6_score.py --code /home/noob/work/el_f3 --out <gaint b6 score dir> --mode b6 --device cuda \
  --forbidden /home/noob/work/b6/b6_forbidden.txt --folds /home/noob/work/b6_build/inputs/b6_folds.tsv \
  --runs <relayed>/b6_SUP_f0_s5 ... (20) --stems <ROOTBASE>/b6_root_<k>/splits/test.txt ... (one per run, same order)
# laptop or gaint, after the scores are final (MANIFEST md5):
python3 b6_verdict.py --scores <score dir> --folds results/b6/b6_folds.tsv --groups judge/out/b6_groups.tsv \
  --forbidden results/b6/b6_forbidden.txt --out results/b6/verdict/b6_verdict [--metrics <20 metrics.json>]
```
- A cv02-side scoring pass is allowed only after `scorechk_gpu.sh`'s exact check passes on cv02 (§9 of the protocol). It would need `b6_score.py`, `b6_forbidden.txt` (names only) and `b6_folds.tsv` there.
- The trainer needs only `<root>/splits/*.txt` and `<root>/labeled/{images,masks_escdd}` (`train.py` l.329-466; supervised builds no unlabelled set).
- The expected per-run data-build lines are in runner's `results/b6/jobs/exp/` (EXP.md5 25ea29e3), built from `databuild.txt` with the cv02 paths. builder's check (E): all 10 files equal databuild.txt 72b05058's three lines per fold, with `/home/noob/work/b6/` replaced by `/tmp/noob_el/el_b6/b6_roots/`.

## 8. File md5s
| File | md5 | where |
|---|---|---|
| b6_make_roots.py | fe70fbaf | scripts/b6, gaint b6_build/scripts |
| b6_databuild_check.py | 061a3964 | same |
| b6_score.py | 981b5f29 | same |
| b6_valcmp.py | 1ad95d68 | same |
| b6_verdict.py | 6d807784 | same |
| scorechk_gpu.sh | a7322114 | same |
| identity_cpu.py / idchk.sh / idchk5.sh / scorechk.sh | 962379a6 / 96d925da / 81c42b58 / 0be80a2c | gaint b6_build/scripts |
| ROOTS.md5 / DATA_MANIFEST.md5 / b6_forbidden.txt | e4100381 / 2630f630 / 9bb4d919 | gaint /home/noob/work/b6 |
| databuild.txt / databuild.json | 72b05058 / def5e001 | gaint b6_build/databuild |
| idchk5 A / B | d683d69a / 3a66c3bf | gaint b6_build/idchk5 |
| check json (CPU) / valcmp_cpu.txt | 1ee0b18d / bf8437bc | gaint b6_build/check |

## 9. GPU exact-pass result: **EXACT PASS** (2 Nov 2026 01:23 IST, gaint)
- Run by runner at the user's OK for gaint scoring (training stays cv02-only): `scorechk_gpu.sh` a7322114 via runner's wrapper (tmux b6chk, PID 3249554, gate 9,900).
  - gaint `check/batch.log`: `[01:23:44] gpu check start pid 3646456`, `[01:23:55] score_gpu rc=0`, `[01:23:55] valcmp_gpu rc=0 (0 = EXACT PASS)`.
- E (builder read the files on gaint):
  - `check/valcmp_gpu.txt` 78c201dc: b6_score.py 981b5f29, device cuda, weights 15bea4c6 (f3_SUPPF_100pct_s0 latest.pth, step 20000), m0 code e544133, 54 val cells.
  - **Per-cell records equal: 54 / 54** for every field: conf, crack_rel2, crack_cc, inact_cc, crack_pband_gt / neg, crack_h1000_pos / neg.
  - 0 px changed of 14,155,776.
  - Pooled values equal to the m0 val block, all Δ +0.000000: crack IoU 0.43132, relP@2 0.93735, relR@2 0.84498, relF1@2 0.88877, inactive IoU 0.56060, crack comp R / P 0.800 / 0.973, inactive comp R / P 0.650 / 0.500, mIoU (24) 0.47904.
  - Output `check/out_gpu/f3_SUPPF_100pct_s0.check.json` 48b4eef6; `score_gpu.log` ed6a2b84. Wall time 8 s scoring, 11 s in all.
- Memory (runner): scorer peak 3,292 MiB; min free 8,842 MiB, beside finllm + HC s8 / s9.
- So the held-out scorer reproduces the opening-1 m0 per-cell records bit for bit on gaint's GPU in bf16. That is the device coach fixed for the 20-run B6 scoring (protocol_B6 v1.0.2 §9).
- builder's §8.2 items are all closed.

## judge: build review (2026-11-01 23:47 IST; build_b6 as of md5 c81d35cc; protocol_B6 v1.0.2 0eebb86c)
**PASS for launch.** Folds, roots, the no-test / no-E1 guard, the scorer's held-out asserts and the verdict bootstrap all check out. Two conditions remain:
- (a) the §5.3 GPU exact pass must PASS (and be appended in §9) before coach's APPROVED. §8.2 says "exactly", and the scoring device is fixed to gaint's GPU in bf16.
- (b) every per-run assert in runner's queue must use the exp/ lines, unchanged.

Code: `judge/b6_root_check.py` e06724c5 (names only). Inputs: the gaint roots' split files and manifests, pulled read-only.

### 1. Roots vs folds and groups (E, own code)
- For each root k:
  - held-out = fold k of `b6_folds.tsv` e2cafce1 exactly (107 / 107 / 106 / 106 / 106; groups 66 / 68 / 64 / 69 / 67);
  - val.txt == test.txt;
  - train = the other 4 folds, in el_f3 train.txt order then val.txt order;
  - no duplicates; SPLITS.md5 matches.
- The held-outs partition the 532 stems. The fold file's phys_group equals my `b6_groups.tsv` 5ff33e20 for all 532, and 0 of 334 groups are split.
- **0 test / 0 E1** stems in any of the 15 lists or in DATA_MANIFEST. DATA_MANIFEST has 1,064 lines = 532 stems x (labeled/images, labeled/masks_escdd), nothing else.
- `b6_forbidden.txt` 9bb4d919 = real test 50 + ext117 stems.txt 117, exactly.
- `labeled` resolves to el-fault-detection/data/labeled = el_f3's target.

### 2. Data build and jobs (E)
- databuild.txt 72b05058: train inactive px = 285,020 minus fold k's px for all 5 folds (fold px from §2 of the protocol).
- `exp/SUPPF_f2.txt` spot check = databuild fold 2 with the cv02 root path.
- **Runner's `b6_jobs.txt` 1fea91f5 (own parse, all 20):**
  - name = b6_{arm}_f{fold}_s{seed};
  - data.root = .../b6_root_{fold} (fold k -> root k, no cross-wiring);
  - seed and run_name once each;
  - all other opts = the pf2_{SUP,SUPPF}_100pct_s5 line of `pf2_jobs.txt` 210d0d6f exactly;
  - the 20 (arm, fold, seed) are complete.
- §3.2 is right: ce_dice is unweighted, so "CE weights differ per fold" (my B6-4) is void. The zero-pixel-class disclosure (belt_mark f0, rings f2, clamp f3) is in protocol §9.

### 3. Held-out scorer `b6_score.py` 981b5f29 (read in full)
- Before the model is built, it checks:
  - --stems == the run's root test.txt == val.txt;
  - forbidden list md5-pinned, applied to held-out and train;
  - held-out = exactly one fold, and train = the other 4 (folds md5-pinned);
  - total_steps 20000.
- On the weights: step 20000 is asserted on latest.pth; best.pth is never opened. After inference: output set == --stems. No m0_audit default / rescore / LA path exists in it.
- The arm label comes from `training.encoder_pf`: pf2_SUPPF's config has the block, pf2_SUP's has none. b6_verdict 6d807784 now cross-asserts arm / fold / seed against the run name (l.127-130, read).
- builder correctly declined my config_md5 ask: seed and run_name are in config_used.yaml, so the two seeds' configs differ by design. Runner's per-run re-diff covers the config.

### 4. Verdict script `b6_verdict.py` 6d807784 (read in full; selftest re-run by judge on 6d807784: PASS 7/7 incl. the swapped-arm assert)
- It matches protocol §4:
  - primary = pooled OOF inactive IoU per (arm, seed); Δ = seed-mean PF - house;
  - two-stage bootstrap: 334 groups with replacement, then one seed per (fold, arm); 2,000 resamples, random.Random(0);
  - PASS iff lo > 0 and Δ >= 0.01; FAIL iff hi < 0.
- Guards:
  - GT conf row sums == b6_folds px (masks guard);
  - 20 distinct weights;
  - one scorer / device / revision;
  - OOF cover once per (arm, seed).
- The --metrics cross-check (my item 7) uses `test_final.per_class_iou[11]` and per_class_gt_pixels. These are 24-long lists in e544133 metrics.json (E, pf2_SUPPF s5), so the index is right.
- S: the one-seed-draw variance argument is correct for 2 seeds. Keep it.

### 5. Notes (S, none blocking)
- The CPU check (inactive IoU +0.0034 vs bf16) shows the primary is sensitive to dtype at the 0.003 level, about 1/6 of the 0.020 SE. Coach's one-device ruling is right; never mix scorings.
- **Typed timestamps:** protocol_B6 §9's header said "2026-11-02 ~00:00 IST"; coach corrected it to 1 Nov 23:42 / 23:43 (checked 23:48). My own log stamps had the same fault and are corrected (log 23:46).
- **Zero-train-class px (report only):** belt_mark has 21,935 px, all in fold 0's held-out cells, never seen in fold 0 training. Whatever the fold-0 models predict there lands in other classes. Report the inactive FP on those px per arm (and on rings f2 / clamp f3), so a both-arms shift on fold 0 can be told apart from the PF effect.
