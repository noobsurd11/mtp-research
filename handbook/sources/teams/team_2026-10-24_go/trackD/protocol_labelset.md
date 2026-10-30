# Track D labelset protocol v1 (APPROVED by C, review_labelset_v1.md; C's three text items added): which 12 labelled cells to add at 5% (DX, 24 Oct 2026)

Direction 3 in `team_2026-10-24_why/SYNTHESIS.md` §2 (R1's D1, `r1_data_side.md` §6); main contrast and defaults set by C in `trackD/critic_defaults.md` §0-1. Replaces `team_2026-10-21/skcdf/labelling_plan.md` §2a. User: accepted 3 seeds per draw (adopted C's decisions, 24 Oct). Written before any training.

## 1. Question
At a fixed budget of +12 labelled cells over the seed-0 5% set (23 → 35), (a) does choosing crack cells beat choosing at random, and (b) among crack cells, does covering the weak sources (BMRK, ARTS, CSIR) beat drawing from all sources?

## 2. Hypotheses and pre-stated expectation
- **Primary 1 (mechanism, R1):** Ts − Tc > threshold on a primary metric: source coverage matters beyond crack-cell count.
- **Primary 2 (the user's question):** Tc − R > threshold: crack cells beat random cells at equal budget.
- **Secondary (R2's contrast, descriptive):** Ts − R.
- **Expectation (S, written now so it cannot be re-read later):** R ≈ A5c + 0.04 crack IoU (≈ 0.34); Ts ≈ Tc (n.d.); Tc − R positive. Read "Ts ≈ Tc" as "crack count, not source, is the lever".
- **Kill (SYNTHESIS):** Ts − Tc and Tc − R both n.d. **and** BMRK and ARTS crack recall move < +0.05 (Ts vs Tc and Tc vs R): then labelled-set composition is not a lever at this budget; Direction 4 (SSL on the better-covered set) does not run.

## 3. Arms (one change: which 12 cells are added; everything else is A5c)
| Arm | Labelled set | Draws | Seeds per draw |
|---|---|---|---|
| R | 23 + 12 random candidates | 3 (rng 101, 102, 103) | 0, 1, 2 |
| Tc | 23 + 12 random crack cells, any source | 3 (rng 201, 202, 203) | 0, 1, 2 |
| Ts | 23 + 12 crack cells: 6 BMRK, 4 ARTS, 2 CSIR, random within source | 3 (rng 301, 302, 303) | 0, 1, 2 |

27 runs. Training seed varies; the draw fixes the labelled set (`data.split_seed=0` as in A5c, the list overrides the file).

**Candidates and draws** (critic defaults §0, §1):
- Pool: the 455 seed-0 unlabelled 5% train cells minus the 7 D7 train twins = 448. Never val or test (asserted).
- Crack cell: ≥ 20 GT crack px on `masks_escdd`, **excluding P6 remap px** (crack in `masks_escdd` where E-SCDD's own mask is not crack; asserted to be only former scuff/star px). Inactive is not used to select.
- Script `~/mtp/research/scripts_cv02/trackD_draws.py`; `numpy.random.default_rng(seed).choice(sorted candidates, k, replace=False)`; Ts uses one generator per draw over BMRK, ARTS, CSIR in that order. List = the 23 base cells in `labeled_5pct.txt` order, then the 12 added cells sorted.
- Dry run (cv02, 24 Oct 11:50 IST; same script and seeds, staging dir): 448 candidates, 191 crack cells (ARTS 41, BMRK 22, CFVS 79, CSIR 48, SDLE 1); total remap px 703 (matches handbook 17 §5.3 train count). Base 5% set: 8 crack cells, 17,789 crack px, 2 inactive cells, 20,517 inactive px.

| Draw | + crack cells | + crack px | + inactive cells / px | added by source (cells / crack cells / crack px) |
|---|---|---|---|---|
| R_d0 | 9 | 8,761 | 1 / 4,339 | ARTS 3/1/215, BMRK 3/3/4,555, CFVS 3/2/2,950, CSIR 2/2/844, SDLE 1/1/197 |
| R_d1 | 4 | 5,309 | 2 / 24,256 | ARTS 5/1/122, BMRK 1/0/0, CFVS 5/3/5,187, CSIR 1/0/0 |
| R_d2 | 5 | 1,327 | 0 / 0 | ARTS 6/3/633, CFVS 4/1/371, CSIR 2/1/323 |
| Tc_d0 | 12 | 18,962 | 3 / 29,759 | ARTS 1, BMRK 1, CFVS 5, CSIR 5 |
| Tc_d1 | 12 | 11,070 | 1 / 1,695 | ARTS 2, BMRK 5, CFVS 4, CSIR 1 |
| Tc_d2 | 12 | 13,642 | 4 / 14,232 | ARTS 2, BMRK 3, CFVS 4, CSIR 3 |
| Ts_d0 | 12 | 21,184 | 2 / 12,668 | ARTS 4/823, BMRK 6/8,996, CSIR 2/11,365 |
| Ts_d1 | 12 | 8,315 | 1 / 4,339 | ARTS 4/505, BMRK 6/6,055, CSIR 2/1,755 |
| Ts_d2 | 12 | 20,318 | 4 / 26,857 | ARTS 4/1,455, BMRK 6/7,258, CSIR 2/11,605 |

The final lists are this same output, regenerated in `/tmp/noob_el/el_d1/draws/` after APPROVED, md5-compared with the staging lists, committed to `trackD/draws/` (lists + `audit.json`) before any training. No redraws.

**Module-position flag (C, review v1):** for every added cell `audit.json` records whether it shares source + module position (`rX_cY`) with a test cell (CFVS is a time series; only the 7 twins are excluded). If any flagged cell is added in any draw, the "no 7 test twins" rows become co-equal with the all-50 rows for every contrast.

**Known imbalance, stated now:** Ts adds more crack px than Tc in two of three draws (CSIR cells are large), and inactive px differ across draws (0 to 29,759). Crack px and inactive px added are reported per draw beside every result; a descriptive regression of draw-mean crack IoU on added crack px is reported (9 draw-means, not a rule).

## 4. Fixed settings (A5c recipe, `scripts_cv02/p12_queue.spec`)
`supervised.yaml seed=<s> data.labeled_fraction=0.05 training.total_steps=20000 data.split_seed=0 training.labeled_batch_size=8 data.mask_subdir=labeled/masks_escdd model.name=smp_unetpp data.augmentation=labelsafe loss.supervised=ce_dice data.labeled_list=/tmp/noob_el/el_d1/draws/<arm>_d<k>.txt`
- U-Net++ ResNet-34 ImageNet, CE + Dice, label-safe aug, Adam 1e-3, 20,000 steps, batch 8, bf16, deterministic. Final weights (step 20,000). No val selection.
- Code: gaint worktree `el_d1`, branch `d1`, commit `86197f3` (= `88a7e88` + `data.labeled_list`; diff: `scripts/train.py` +18/-3, `scripts/rescore_logit_adjust.py` +2, `tests/test_labeled_list.py` new; suite 229 passed, 3 skipped). Unset `labeled_list` leaves every path unchanged.
- Deployed by `git archive 86197f3` to cv02 `/tmp/noob_el/el_d1`, `REVISION`, `data -> /tmp/noob_el/el_p7/data`.

## 5. Metrics
- **Primary (each contrast):** test crack IoU, crack relF1@2, crack recall (50 cells, revised masks, argmax).
- **Secondary:** per-source crack recall and IoU (BMRK, ARTS; also CFVS, CSIR); inactive IoU; all-class mIoU (24 classes, test confusion matrix); E1 extension (106 cells) crack false alarm and tolF1 (`diag/e1_task_metrics_v2.py`).
- **Yardsticks, reported, not in the rule:** A5c (5 seeds), A5c+LA, BsM5 D7 re-run (`al1_BsM5`, crack IoU 0.331), each arm + LA (τ 1, prior from the run's own 35 cells), L3 10% (3 seeds).
- **Cell sets:** all 50 / no noisy cell / no 7 test twins / neither; per source.

## 6. Decision rule (C's, critic_defaults §1)
- Unit = draw. Draw-mean = mean over its 3 seeds. Δ = mean of 3 draw-means (B) − mean of 3 draw-means (A). Threshold = max(0.01, 2·sqrt(var_A/3 + var_B/3)), var = sample variance over the 3 draw-means.
- BETTER if Δ > threshold on ≥ 1 primary and no primary WORSE (Δ < −threshold); WORSE symmetric; else n.d.
- Applied to Primary 1 (Ts − Tc) and Primary 2 (Tc − R) separately; two primaries disclosed, no multiplicity correction (handbook 07 §5). Ts − R reported with the same arithmetic as secondary.
- Descriptive beside it: seed-level rule 1 (9 v 9, `ssl_rules.cmp`), so the reader sees how much draw variance adds; and image bootstrap CI on the primary Δ (2,000 paired resamples of test cells, the same resample for both arms, pooled metric per resample).
- **Power, stated now:** with equal draw-mean sds of 0.015 the threshold is 2·sqrt(2·0.015²/3) = 0.0245; with 0.010 it is 0.016. The expected Ts − Tc (0 to +0.02) is therefore below the threshold unless draws agree closely; an n.d. on Primary 1 is the likely outcome and is not evidence of no effect.
- Width check: crack relP@2 drop > 0.05 between contrasted arms is flagged.
- **Direction 4 gate (critic_defaults §1):** runs only if Ts − Tc is BETTER, or Tc − R is BETTER with BMRK recall ≥ +0.05; own protocol.

## 7. Checks before launch
1. **Identity:** new code with `data.labeled_list=<data/splits/seed0/labeled_5pct.txt>`, seed 0, `--exit_after_step 500`, on cv02; every training log line and the val @ 500 line equal `el_p11/experiments/p12_A_5pct_s0.stdout` as text (timing fields dropped), `scripts_cv02/sk1_identity_diff.py --upto 500`. At least 200 steps required (C); 500 gives 10 loss lines and one val line.
2. **Draw audit:** the regenerated lists equal the staging lists (md5); `audit.json` printed; Ts exactly 6/4/2; no twin, val, test or duplicate stem (asserted in the script and again by the loader).
3. **Smoke:** `d1_R_d0_s0` to 300 steps on a lane GPU beside a second smoke (`d1_Ts_d0_s0`), for peak memory and steps/s. The log must show `Labelled: 35 (/tmp/noob_el/el_d1/draws/...)`.
4. C reviews the code diff, identity diff and smoke logs before the 27 runs start.

## 8. Compute
- cv02 GPUs 0-3 (Track D's lanes by agreement with MD), 2 fixed lanes per GPU = 8 lanes, `lanes_sk1.sh` pattern (round-robin deal, one tmux window per lane, rc captured before `$(date)`, re-score only on rc 0). Session `=d1`. Runs ordered seed-major, then draw, then arm, so partial completion stays balanced.
- GPU rule: < 1,000 MiB used at launch on each lane GPU (another user's 470 MiB processes sit on 0-3 now; under the 4 GB rule). Booked in `gpu_ledger.md` before launch.
- Time: ~2.5 h per run on packed lanes (`results/al1/launch.log`), 27 runs over 8 lanes = 4 rounds, about 10-11 h wall, ~35 GPU-h.
- Post: per run `rescore_label_versions.py` (lane), then `trackD_edge_rescore.py` (per-cell standard counts with relaxed @2, τ 0 and 1; banded rows as a by-product) and an all-class confusion-matrix scorer; E1 scorer.

## 9. Outputs and verification
- Run dirs `el_d1/experiments/d1_<arm>_d<k>_s<s>`, re-score JSONs `reports/d1/`, launch log. Relayed to gaint `cv02_noob_el/el_trackD/el_d1` with MD5 manifests (`relay_cv02_al1.sh` pattern).
- Completion check per run: log reaches `step 20000/20000` and `TEST (final weights, step 20000)`, one header per stdout, re-score `step` 20,000.
- Analysis `trackD/labelset_results.md` (DX); C recomputes both primaries from the per-cell JSONs with C's own script before anything goes to team-lead.

## 10. Limits stated now
One split seed for the base set, 50 test cells (BMRK test crack comes from few cells), 3 draws per arm (draw variance estimated from 3 values), 3 seeds per draw (user-approved deviation from ≥ 5), retrospective (labels already exist, so no annotation-cost or annotator-error effect), cv02 only.
