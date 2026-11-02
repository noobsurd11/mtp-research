# coach verify: protocol_B6 (in-distribution inactive test of PF by module-grouped 5-fold CV; SUP100-PF vs SUP100-g, seeds 5 / 6; trained on cv02, scored on gaint)

coach, 2 Nov 2026, 22:18 IST (from `date`). Independent recompute. Tags: E (file), S (judgement). No test cell and no E1 cell is used.

## Verdict: **n.d.**
- "No in-distribution inactive gain detectable at this power; PF's inactive gain is shown on unseen panels (E1) only" (§4 wording, fixed before any run).
- **Primary:** pooled out-of-fold inactive IoU over 532 cells. Δ (PF − house, mean of seeds 5 / 6) = **−0.0144**.
- **Two-stage CI** (groups, plus seed per (fold, arm)), 2,000 resamples:

  | computation | 95% CI |
  |---|---|
  | runner's frozen `b6_verdict.py` 6d807784, seed 0 (the pre-registered one) | **[−0.0977, +0.0570]** |
  | mine, own RNG 20261102 | [−0.0955, +0.0609] |
  | judge's (log 22:15) | [−0.0901, +0.0622] |

- **Rule:** PASS needs lo > 0 and Δ ≥ 0.01 (no); FAIL needs hi < 0 (no).

## Inputs and integrity (E)
- **Training (cv02, one machine type):**
  - Records (gaint relay copy `cv02_noob_el/el_b6/q/launch.log`): 20 trained rc 0, 20 `config OK`, 20 `databuild OK`, 0 HOLD / FAIL; `B6 ALL TRAINED (20 rc 0 of 20)` at 16:01:15 UTC (21:31 IST); REVISION e544133.
  - Per stdout (grep -c only): 1 header, step 20000/20000, 0 Tracebacks; PF lr lines 400 for the 10 PF runs, 0 for the 10 house runs.
  - Per-fold data build (`results/b6/jobs/databuild.txt`):
    - `Labelled: 425 / 425 / 426 / 426 / 426`, val = test = the fold's 107 / 107 / 106 / 106 / 106 held-out cells;
    - `CE class weights: none (plain CE)`;
    - zero-px classes belt_mark f0, rings f2, clamp f3 (as §9).
  - A6000 identity PASS before the queue (bd1ba77d, step lines 20 / 20, md5 ee0e092b).
- **Relay and scoring:**
  - Relay: cv02 → gaint, RELAY.md5 6e8806e9 (124 files) on both ends.
  - Scoring: one bf16 pass on gaint GPU, `b6_score.py` 981b5f29 (the §8.2 exact-match device), 22:11:25-22:13:45, rc 0; scorer peak 3,294 MiB, min free 22,504 MiB.
  - Scores MANIFEST **960ce11a**, md5sum -c OK on gaint. The 20 `.b6.json` md5s on gaint equal runner's list.
- **Fold and group files:** folds e2cafce1, groups 5ff33e20 (frozen), on gaint and locally.
- **Code (coach's own):** `scripts/coach/coach_b6.py` **463bab6c** (numpy; not b6_verdict).
  - Self-test PASS (synthetic null / gain / loss = hand calculation; null CI [0, 0]).
  - Its load asserts each file's arm / fold / seed against its run name, step 20000, held-out cells == fold k's stems, and each cell's GT inactive px == the folds table.
  - Ran on gaint CPU (nice 19, 8 threads, CUDA hidden), rc 0, 22:15:55. Output: `results/b6/coach_v/` (MD5 OK; coach_b6.txt ba2efcc0).
- **Cross-check vs runner's local readout:** `results/b6/verdict/b6_verdict.txt` c4c68e62 (post_local 08db9dbf, rc 0) equals mine to 4 dp on every point estimate:
  - the 4 (arm, seed) IoUs, Δ, the seed-pair Δs;
  - crack IoU and relF1@2;
  - per source, per fold, leave-top-3, twins.
  - The CIs differ only by RNG.
  - One aggregation difference: house inactive component precision is 0.6177 in mine (ratio of seed-mean counts) vs 0.6226 in runner's (mean of per-seed ratios). I reproduced both forms. PF is 0.7291 / 0.7288.
- **Trainer TEST block vs scorer** (runner's readout, reported): |Δ| ≤ 0.00046 on all 20 runs; GT px identical.

## Primary and reported (§4)
| (arm, seed) | house | PF |
|---|---|---|
| s5 | 0.4992 | 0.4996 |
| s6 | 0.5193 | 0.4901 |
| mean | 0.5093 | 0.4949 |
- **Seed-pair Δ:** s5 +0.0004, s6 −0.0291 (not the same sign).
- **One-stage CI** (groups only): runner [−0.0780, +0.0465], mine [−0.0816, +0.0462].
- **Per fold** (Δ, s5 / s6): f0 +0.063 / −0.094; f1 −0.125 / −0.036; f2 +0.067 / −0.048; f3 −0.009 / +0.048; f4 +0.028 / −0.031. Fold-seed sign count 4 of 10 positive.
- **Per source** (inactive IoU, seed means):
  - **CFVS** (29 inactive cells, 78% of px): 0.546 → 0.547 (+0.0007);
  - BMRK (6 cells): −0.096;
  - CSIR (11): +0.013;
  - ARTS (2 cells, 1,150 px): +0.054.
- **Leave-top-3-groups-out** (CFVS_00016 / 00130 / 00146, 38.8% of px): −0.029.
- **Twin groups** (13 groups, 56 cells): −0.0115; the rest −0.0161. PF gains no twin advantage here.
- **Inactive components (≥ 20 px):**
  - recall 0.517 → 0.575 (+0.058; s5 +0.061, s6 +0.054);
  - precision 0.623 → 0.729 (+0.106; s5 +0.174, s6 +0.038).
  - Reported only, no label.
- **Crack:** IoU 0.3715 → 0.3612 (−0.010; s5 −0.001, s6 −0.020); relF1@2 0.8346 → 0.8388 (+0.004).
- **Zero-train-px classes in their held-out fold:** inactive predicted on belt_mark (21,935 GT px, f0), rings (1,204, f2) and clamp (1,238, f3) is 0 px for every arm and seed. There is no fold shift of that kind.

## Power, as realised (E / S)
- **Pre-registered (§5):** SE ≈ 0.020, with PASS power ~13% at +0.017.
- **Realised:** the two-stage bootstrap sd is **0.039** (runner), **~2× judge's pre-registered estimate** (review_B6_v0 B6-2: 0.018 cell sampling scaled from test, plus 0.008 seeds). The realised split (judge):
  - groups only (one-stage): 0.031. Out-of-fold cells are scored by a different model pair in each fold, and the scaling from test ignored that fold-to-fold model variation;
  - seed draws: ~0.022.
  - Seed-pair Δs +0.000 / −0.029; per-fold seed Δs −0.125 … +0.067.
- **Realised power** (judge): ~6% at +0.017 (13% was stated before the run), ~12% at +0.03, ~26% at +0.05; 80% needs ~+0.11.
- **Consequence:** B6 bounds the in-distribution effect to about [−0.10, +0.06]. It cannot tell test's +0.017 from 0, or from a −0.05 loss.
- **But it does exclude an in-distribution gain the size of PF's E1 effect:** the CI upper bound is +0.06, against E1's +0.19 (singles, PF2) and +0.21 (ensemble, PF2E).
- §8.4 asked for B6 to be reported as low-powered either way. It is lower-powered than stated before the run.

## Reading (S, with E)
- **n.d. as pre-registered.** In-distribution, PF's pooled inactive IoU is not higher than the house recipe's (point −0.014; CFVS, which holds 78% of the inactive px, is flat at +0.001).
- **Component counts lean PF** (recall +0.058 and precision +0.106, same sign in both seeds) while pooled pixel IoU is flat: PF covers more GT inactive components and makes fewer false inactive components, but the largest groups, which dominate the px, do not move. This is descriptive, unregistered for a verdict, and gets no label.
- **What this decides:**
  - PF's inactive advantage stays an E1 (unseen panel) result (PF2 #1, PF2E #4). B6 supports reading it as an unseen-panel effect: an in-distribution gain of E1's size (+0.19 / +0.21) is excluded (CI hi +0.06). B6 does not claim an in-distribution null.
  - B6 neither confirms nor rules out an in-distribution gain of test's size.
  - E-PF stays the deployable candidate, on E1 grounds.
  - No claim of "PF improves inactive in-distribution".

## judge: adversarial check (2026-11-02 22:19 IST from date; verify_b6 as of md5 5d7a0957; scores MANIFEST 960ce11a, md5sum -c OK on my read-only pull)
**Verdict n.d. CONFIRMED.** Every point estimate in the verify matches mine to 4 dp. Fold integrity holds. The zero-train-px classes are clean. Two fixes: the power shortfall has two causes, not seed noise alone, and the pre-registered estimate that missed was judge's own (fix 1). B6 does exclude an E1-sized in-distribution gain (fix 2).

Code (own; computed before reading runner's or coach's B6 output, logged 22:14):
- `judge/b6_recompute.py` 406cd7c8 (numpy; self-tested on synthetic gain / null / swapped-fold files) → `judge/out/b6_recompute_out.txt` 82f7b20c;
- per-file metadata check → `judge/out/b6_meta_check_out.txt` 64b4550d.

### 1. Recompute and integrity (E)
- **Recompute:**
  - IoU: house s5 / s6 0.4992 / 0.5193, PF 0.4996 / 0.4901; **Δ −0.0144**.
  - Two-stage CI (groups + one seed per (fold, arm), rng 20261103): [−0.0901, +0.0622], sd 0.0384. One-stage: [−0.0779, +0.0440], sd 0.0313.
  - Both equal the frozen b6_verdict ([−0.0977, +0.0570], sd 0.0392) up to RNG.
  - Per-fold, per-source, leave-top-3 (−0.0290), twin (−0.0115) / rest (−0.0161), crack IoU (−0.0104) and relF1@2 (+0.0042) are identical.
- **Integrity, all checks pass:**
  - 20 files = runner's 20 jobs lines (arm / fold / seed, data.root = b6_root_<fold>, PF opts iff SUPPF).
  - Each file's cells = its fold = the gaint root's test.txt = val.txt, and stems md5 = root_test_md5 = the gaint root file I pulled.
  - Root train.txt = the other 4 folds, with no overlap.
  - 0 forbidden (test + E1) stems in any held-out or train list.
  - 334 phys groups, none split across folds.
  - GT inactive / crack px per cell = b6_folds.tsv; GT rows identical across all 20 runs.
  - One scorer 981b5f29, device cuda, code e544133; 20 distinct weights md5s; step 20000, latest.pth, TTA off, held-out only.
  - Trainer TEST block vs scorer: |Δ| ≤ 0.00046 on all 20. This independently confirms that each run's held-out set is what its trainer evaluated.
- **The two-stage bootstrap matches §4:**
  - groups drawn with replacement (334, judge's groups), then one seed from {5, 6} per (fold, arm), pooled counts;
  - PASS iff lo > 0 and Δ ≥ 0.01; FAIL iff hi < 0.
- **Zero-train-px classes** (belt_mark 19: f0, 21,935 px in 2 cells; rings 12: f2, 1,204 px in 1 cell; clamp 8: f3, 1,238 px in 1 cell; found from GT per fold, no others):
  - **0 px predicted inactive** in all 4 (arm, seed) runs.
  - Top predicted classes there: background, then 7 / 13 / 4 / 15 / 2 / 17 / 5.
  - Dropping those 4 cells leaves Δ unchanged (−0.0144). No fold-shift confound.

### 2. Power: the shortfall is judge's estimate, and it has two causes (E / S)
- **The pre-registered SE 0.020 was judge's** (`judge/review_B6_v0.md` B6-2):
  - cell-sampling 0.018, from test's fixed-model cluster SE 0.025 × sqrt(7.2 / 13.3);
  - plus ~0.008 for seed noise.
- **Realised:**

  | component | estimated | realised |
  |---|---|---|
  | groups only (one-stage) | 0.018 | **0.031** |
  | seed part, sqrt(0.0384² − 0.0313²) | 0.008 | **~0.022** |
  | total (two-stage) | 0.020 | 0.038-0.039 |

- **Why it missed (S):**
  - On test, one model pair scores every cell. In B6, each fold's cells are scored by a different model pair (5 per seed), so fold-to-fold model variation enters the group bootstrap as cell / group variation. The n_eff scaling ignored this.
  - The per-fold seed swings are large too: e.g. fold 0 house 0.267 vs 0.343, PF 0.330 vs 0.250.
- **Fix 1:** coach's "Seed noise is large" names only half of it. Write: "the realised SE is ~2× judge's pre-registered estimate; group resampling alone gives 0.031 (out-of-fold predictions come from different models per fold, which the estimate ignored), and seed draws add ~0.022."
- **Realised power (normal approx, SE 0.038):** ~6% at +0.017 (stated before the run: 13%), ~12% at +0.03, ~26% at +0.05; 80% at ~+0.11. Put "~6% at +0.017" next to "80% at ~+0.11".
- B6 was weaker than the user was told when deciding to spend the GPU. The decision itself was made knowing it was low-powered (§8.4).

### 3. What B6 can and cannot say (S, with E)
- It cannot separate test's +0.017 from 0 or from −0.05 (coach is right).
- **Fix 2:** it does exclude an in-distribution gain the size of PF's E1 inactive effect. The upper bound is +0.057 (frozen), while E1 showed +0.19 (singles) and +0.21 (ensemble). Add: "an in-distribution inactive gain as large as PF's E1 gain is excluded (CI upper bound +0.06)". This supports "PF's inactive gain is an unseen-panel effect" without claiming an in-distribution null.
- **Component lean:** reported with no label, correctly.
  - It rests on 2 seeds. The PF component-precision gain is +0.174 for s5 but +0.038 for s6, and it has no interval.
  - My all-size, any-hit version leans the same way: GT comps any-hit house 0.545 / 0.566 vs PF 0.594 / 0.618; predicted-comp precision 0.441 / 0.589 vs 0.667 / 0.668.
  - Keep it as "PF makes fewer false inactive components; pixel IoU does not move".
- CFVS flat (+0.0007) and BMRK −0.096 (6 cells): agreed; descriptive.
- The reading is right: no in-distribution claim; E-PF's advantage stays an E1 result. Note that SKR2E (locked) may change which ensemble is deployable on other grounds; B6 does not bear on that.

### 4. Fixes for coach (no verdict change)
1. Power-shortfall attribution, with the realised power at +0.017 (~6%); state that the pre-registered 0.020 was judge's estimate.
2. Add the E1-size exclusion (upper bound +0.06 vs +0.19 / +0.21).
