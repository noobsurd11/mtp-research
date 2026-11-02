# coach verify: protocol_SKR2E v1 (E-SKR2 vs E-PF, 5-member mean-softmax ensembles; inference only, gaint CPU fp32); E1 opening #6

coach (respawned session), 2 Nov 2026, written 23:35-23:37 IST (`date`); judge CONFIRMED (section at the end, on b9d8c7da); judge's 5 fixes applied 23:40 IST (no number or verdict change). Independent recompute. Tags: E (file), S (judgement).

## Verdict
- **SKR2E: FAIL, by guards G2a and G2b at the headline pair** (E-PF at its headline b 0 vs E-SKR2 at its headline b 1.0).
  - G2a test relP@2 Δ −0.0379 (bar < −0.03).
  - G2b E1 crack-free px 5,358 vs 2,528 (×2.12; bar ×1.5 = 3,792).
  - protocol §3b: "a trip at either [OP] FAILS". §7: E-PF stays the deployable candidate.
- **At the verdict b 0 (both arms argmax), nothing fails and no guard trips:**
  - test crack IoU and crack relF1@2 pass (both sets);
  - both E1 co-primaries pass (crack relF1@2, any-hit).
  - Without the headline-pair guards this would be a PASS. The headline pair decides the verdict.
- **The FAIL rests on a 0.0015 val margin** (E, `skr2e_val_decisions.json`). E-SKR2's val width-flag drop is 0.0485, against a flag at > 0.05.
  - Had the flag tripped, E-SKR2's headline b would be 0 and the headline pair (0, 0), so the verdict would be PASS.
  - Pre-registered; the verdict is unchanged. Stated so the user sees how close it was.
  - **Structural point (judge fix 3, E):** against E-PF at b 0, G2b trips for **every** E-SKR2 headline b ≥ 0.5 on the grid (×1.58 at 0.5, ×1.83 at 0.75, ×2.12 at 1.0). Only b 0 and 0.25 escape (×1.06, ×1.21; `skr2e_e1_sweep.json`).
    - The trips are not noise (judge's bootstraps, E):
      - G2b cluster CI [×1.70, ×2.58], lying wholly above ×1.5 (P(> 1.5) 0.997);
      - G2a image CI [−0.052, −0.027], P(< −0.03) 0.91.
    - So G2b alone would carry the FAIL, and **the width flag (0.0485 vs 0.05) alone decided FAIL vs PASS.**
- **The b 0 E1 co-primary passes are not a confirmation of SKR2's E1 gain** (judge fix 1, S). The opening FAILED, and E1 #6 re-measures opening #5's members, so it is not new evidence. At ensemble level, SKR2's E1 relF1@2 gain is re-measured (+0.035; +0.024 at matched volume), not confirmed.
- **Multiplicity (judge fix 5, S), if anyone reads b 0 as a win:**
  - 4 of 5 primaries pass at b 0, and the test relF1@2 lower bound is within 0.002 of 0.
  - Family-wise false PASS is ~12% for these two objects and ~15-20% read as a recipe claim (protocol §3c).
  - These are re-measurements of opened effects. Read nothing confirmatory into them.
- **Runner's readout** (`results/skr2e/skr2e_boot_runner.txt` fc41eeaa; skr2e_boot 7520afc0) is **CONFIRMED to 4 dp**:
  - every point estimate, at all 9 b pairs, strata, width, concentration, LOCO and matched volume;
  - CIs differ by RNG only, with the same pass / fail sets;
  - same verdict and the same two trips.

## Inputs, order and code (E)
- **Run:** gaint `el_f3/reports/skr2e/`, `skr2e_run.sh full`, 22:24:38-22:36:52 IST, rc 0 (`run.log`). skr2e_infer.py 5ba3c597 / skr2e_run.sh b2816cb3, as APPROVED.
  - Pull: `results/skr2e/raw` (MANIFEST 9b43e636, 17 files, `md5sum -c` OK on the laptop; runner: both ends).
  - My own read-only copy of gaint out/ (rsync to my scratch, ~23:30) equals `raw/` byte for byte.
- **Order** (gaint mtimes, E):
  - val decisions `skr2e_val_decisions.json` 276ec790: **22:28:05**;
  - test / E1 per-cell files and the E1 sweep: 22:36:51;
  - checks: 22:36:52.
  - `run_full.log` prints "val decisions written" before "test done".
- **Gates** (`skr2e_gate.txt` 8790afce):
  - (a) s5 alone vs its opening m0: E-PF +0.0004 / +0.0004, any-hit 110/125 = ref; E-SKR2 +0.0005 / +0.0000, 116/125 = ref;
  - (b) 125 / 125 GT comps;
  - (c) E-PF decisions = PF2E's (b 1.5, headline 0, drop 0.0753082163, Δ 0);
  - E1 GT comps 296, counted from masks only.
- **Checks** (`skr2e_checks.txt` 1fe4d3b5):
  - **E-PF identity EXACT** vs PF2E's E-PF.b0 / b1.5, all 4 splits, 0 cells differ;
  - any-hit self-test 102/296 (cells = sweep = PF2E).
- **Members** (`member_latest_md5.txt`):
  - SUPPF s5-9 79802bb7 / cffdc5dc / 17bb85ca / 89521560 / 4dc95532 (= verify_pf2e);
  - SKR2 s5-9 26dcd39b / ec1346e3 / a85cfb42 / 15a7690e / b1d2badf (= S2 opening `results/s2/local/opening_outputs.txt`);
  - decisions meta: revisions e544133 / c9bbb02, model code el_f3 e544133, 350 state keys, m_common 10f0d37c, cpu fp32, 8 threads.
- **My code** (own metrics and resampling, not Track M or skr2e_boot):
  - `scripts/coach/coach_skr2e.py` **8460c004** (staged by my predecessor 22:25, self-test PASS on PF2E) → `results/skr2e/coach_v/skr2e_coach.txt` 851403ca. Run on the pulled files **before I read runner's readout**.
  - Reported readouts: `scripts/coach/coach_skr2e_extra.py` 6afcd11e (new; written after the verdict output, reported lines only) → `coach_v/skr2e_coach_extra.txt` dfd9cfa3.
  - My CIs use default_rng(12345) (pairs (0, 0) and headline) and 777 (other pairs); runner's use seed 0.

## Val decisions (E; re-derived by coach from the stored sweep; the sweep at b ∈ U re-summed from the val cells: Δ 0)
- **E-PF:** D2 b **1.5** (val relR@2 0.9089, relP@2 0.9011). Crack-precision drop 0.6046 → 0.5293 = +0.0753 > 0.05, so **headline b 0** (= PF2E).
- **E-SKR2:** D2 b **1.0** (relR@2 0.9034, relP@2 0.9056; at b 0.75 relR@2 is 0.8981). Drop 0.5802 → 0.5317 = **+0.0485 ≤ 0.05**, so **headline b 1.0**.
- U = {0, 1.0, 1.5}. All 9 pairs are written. As protocol §5 expected: "E-SKR2's headline b may be > 0 … G2a / G2b at the headline pair are the ones that may bind."

## 1. Verdict pair: both arms at b 0
**Test (paired image bootstrap): PASS on crack IoU and crack relF1@2, in both sets. Inactive n.d.**

| primary | E-PF | E-SKR2 | Δ all 50 [runner CI] [coach CI] | Δ clean 49 [runner] [coach] |
|---|---|---|---|---|
| crack IoU | 0.4815 | 0.4917 | **+0.0102** [+0.0031, +0.0197] [+0.0031, +0.0193] | +0.0101 [+0.0031, +0.0188] [+0.0029, +0.0192] |
| crack relF1@2 | 0.8942 | 0.9046 | **+0.0104** [+0.0016, +0.0232] [+0.0017, +0.0241] | +0.0103 [+0.0017, +0.0231] [+0.0015, +0.0230] |
| inactive IoU | 0.4613 | 0.4662 | +0.0050 [−0.0090, +0.0280] [−0.0099, +0.0293] | +0.0055 [−0.0104, +0.0317] [−0.0110, +0.0329] |

- The relF1@2 lower bounds sit within 0.002 of 0 in both RNGs. The crack IoU bounds do not.

**E1 co-primaries (106 cells, 71 module clusters): PASS on both.**

| co-primary | E-PF | E-SKR2 | Δ [runner CI] [coach CI] |
|---|---|---|---|
| E1 crack relF1@2 | 0.4345 | 0.4698 | **+0.0353** [+0.0102, +0.0613] [+0.0120, +0.0599] |
| E1 any-hit | 0.3446 (102/296) | 0.4122 (122/296) | **+0.0676** [+0.0253, +0.1282] [+0.0275, +0.1236] |
| E1 inactive IoU (G1e) | 0.2807 | 0.2389 | −0.0418 [−0.0545, +0.0123] [−0.0543, +0.0148] |

## 2. Guards (point estimates; both OPs)
| guard | bar | b 0 pair | headline pair (E-PF b 0, E-SKR2 b 1.0) |
|---|---|---|---|
| G2a test relP@2 Δ (all 50) | < −0.03 | −0.0110 ok | **−0.0379 TRIP** (0.954 → 0.916) |
| G2b E1 crack px on the 74 crack-free cells | > 1.5 × E-PF | 2,673 vs 2,528 (×1.06) ok | **5,358 vs 2,528 (×2.12) TRIP** |
| G1t test inactive Δ, both sets | ≤ −0.015 | +0.0050 / +0.0055 ok | +0.0097 / +0.0108 ok |
| G1e E1 inactive cluster CI | hi < 0 | −0.0418 [−0.0545, +0.0123] ok | −0.0377 [−0.0493, +0.0224] ok |

- **Headline pair primaries (reported; guards apply):**
  - test crack IoU +0.0103 (n.d.), relF1@2 **+0.0168** [+0.0031, +0.0391], inactive +0.0097 (clean: +0.0103 / +0.0162 / +0.0108);
  - E1 relF1@2 +0.0634 [+0.0085, +0.1057], any-hit **+0.1892** (102 → 158 / 296), inactive −0.0377.
  - E-SKR2 at b 1.0 finds much more on E1. It does so at a precision cost relative to E-PF at argmax that exceeds both bars.

## 3. Readings (judge style; reported, never the verdict)
### 3a. Bias share: how much is volume?
- **E1** (matched volume from the E1 aggregate sweep; E1-oracle, chooses nothing):
  - E-SKR2 at b 0 has E1 pred / GT 0.469. E-PF reaches that at b 0.353 (linear between 0.25 and 0.5).
  - There, relF1@2 Δ is +0.0353 → **+0.0238** (bias share **33%**) and any-hit Δ is +0.0676 → **+0.0273** (bias share **60%**).
  - **Most of the E1 relF1@2 gain is not volume; most of the any-hit gain is.**
- **Test** (crude, test-oracle, descriptive: linear in pred / GT between E-PF's stored b 0 and b 1). These are **likely upper bounds** on the remaining gain:
  - they assume E-PF is concave in pred / GT between b 0 and 1, which is unverified on test;
  - the E1 analogue supports it: the same two-point interpolation on E1 gives +0.030 where the fine sweep gives +0.024 (judge).
  - E-SKR2 b 0 test pred / GT 1.056 vs E-PF 0.943 / 1.149 at b 0 / 1.
  - At matched volume, crack IoU Δ +0.0102 → **≤ +0.0045** (bias share ≥ 56%); relF1@2 +0.0104 → **≤ +0.0040** (≥ 62%).
  - Stored pair (E-PF b 1, E-SKR2 b 0): crack IoU −0.0002, relF1@2 −0.0013. **E-PF at b 1 equals E-SKR2 at b 0 on test crack IoU / relF1@2 (−0.0002 / −0.0013). E-SKR2 keeps +0.012 relP@2 at less volume** (pred / GT 1.056 vs 1.149): a slightly better trade-off, not a higher score.
  - So the test pass at b 0 is mostly E-SKR2 being wider at argmax. This is the same caution as protocol §0: "bias alone moves an ensemble by about the effect under test".
- **The guard trips are volume, not an SKR2 precision defect** (E):
  - At equal b 1.0 (E-PF at E-SKR2's headline b): test relP@2 −0.0152; E1 crack-free px 5,358 vs 6,174 (×0.87).
  - At about matched test volume (E-PF b 1.5, pred / GT 1.285 vs 1.273): relP@2 **+0.0040**, crack IoU +0.0030.
  - At matched E1 volume (E-PF at b 1.255 on the sweep): E1 crack-free px 5,358 vs 7,369 (**×0.73**).
  - **So §7's reading "SKR2's ensemble pays a precision cost the singles hid" does not fit (S).** The trips measure E-SKR2's own D2 operating point (b 1.0, a wider OP that its width flag let through by 0.0015) against E-PF held at argmax by its flag. That is what the headline-pair guard was built to catch (judge D1: "recommended at its headline b only if no guard trips at the headline pair"). The consequence (E-PF stays) holds as locked.

### 3b. Width (E)
| | test pred / GT | test P / R | test relP / relR | E1 pred / GT | E1 relP / relR | crack-free px test (2) / E1 (74) / val (31) |
|---|---|---|---|---|---|---|
| E-PF b 0 | 0.943 | 0.670 / 0.631 | 0.954 / 0.841 | 0.381 | 0.588 / 0.345 | 0 / 2,528 / 0 |
| E-PF b 1 | 1.149 | 0.617 / 0.708 | 0.931 / 0.882 | 0.660 | 0.487 / 0.422 | 0 / 6,174 / 1 |
| E-PF b 1.5 | 1.285 | 0.584 / 0.750 | 0.912 / 0.904 | 0.906 | 0.451 / 0.498 | 0 / 9,431 / 27 |
| E-SKR2 b 0 | 1.056 | 0.642 / 0.678 | 0.943 / 0.869 | 0.469 | 0.589 / 0.391 | 0 / 2,673 / 0 |
| **E-SKR2 b 1 (headline)** | 1.273 | 0.589 / 0.749 | 0.916 / 0.906 | 0.747 | 0.518 / 0.479 | 0 / 5,358 / 30 |
| E-SKR2 b 1.5 | 1.417 | 0.554 / 0.785 | 0.893 / 0.924 | 1.017 | 0.476 / 0.552 | 0 / 8,464 / 274 |

- At argmax E-SKR2 predicts 12% more crack px on test and 23% more on E1. E1 relP@2 is unchanged (0.588 → 0.589); test relP@2 is −0.011.
- **Over the E1 sweep, E-SKR2 has fewer crack-free px than E-PF at every b ≥ 0.25** (only b 0 is higher: 2,673 vs 2,528; `skr2e_e1_sweep.json`). For a given b it is wider on cracked cells and not on clean ones.

### 3c. any-hit concentration in the scuff + half-cut cells (E)
- **GT:** 296 comps ≥ 20 px in 21 of 71 images; top 3 57%, top 10 94%, n_eff 7.1; **274 / 296 in the 29 scuff + half-cut cells.**
- **b 0 pair, +20 hits:**
  - **all 20 are in the 29 scuff + half-cut cells** (84 → 104 / 274);
  - the other 77 cells score 18 / 22 in both arms (half-cut without scuff 9 / 11 both; full 9 / 11 both);
  - six images carry the 20: CSIR_02222 +9 (one cell, 45%), CSIR_01717 +4, CSIR_01637 +3, CSIR_02026 +2, CSIR_01679 +1, CSIR_01621 +1.
  - Leave-one-cluster-out [+0.042, +0.075]; without the top 3 comp images +0.095.
- **Headline pair, +56 hits:** 55 in scuff + half-cut (84 → 139), +1 in full.
- **E1 relF1@2 is broader than any-hit** at b 0. It rises in every stratum:
  - scuff + half-cut 0.351 → 0.394;
  - half-cut without scuff 0.804 → 0.825;
  - full 0.517 → 0.544;
  - other 77 0.581 → 0.604.
  - LOCO [+0.026, +0.040]; without the top 3 comp images +0.037.
  - At the headline pair, full (0.517 → 0.485) and other 77 (0.581 → 0.558) fall: width costs precision on the cells without scuff + half-cut.
- **Reading (S):**
  - E1 any-hit is, as §0 predicted, a scuff + half-cut readout. Its pass at b 0 is 20 components in 6 source images, 60% of it volume.
  - The E1 relF1@2 gain (+0.035; +0.024 at matched volume) is the more general one.

### 3d. E1 inactive (G1e not tripped; flagged)
- **Δ −0.0418**, P>0 0.06; leave-one-cluster-out all negative [−0.048, −0.031].
- **But it sits in 3 images.** GT 9,158 px in 7 images, top 3 (CSIR_01637 / 01101 / 01647) hold 87%, n_eff 3.3. Without those 3 images: +0.0003.
- Strata: scuff + half-cut 0.637 → 0.613, half-cut without scuff 0.144 → 0.317, full 0.130 → 0.100.
- **Singles vs ensemble:**
  - single means are equal (E-PF 0.2371 ± 0.0271, E-SKR2 0.2393 ± 0.0725);
  - E-PF's ensemble gains from averaging (0.2807); E-SKR2's does not (0.2389).
- The loss is not on test (+0.005). It is a 3-image E1 readout. **If SKR2 is ever taken forward, PF2E's E1 inactive gain (+0.214) must not be assumed to carry over** (S).

### 3e. Other (E, reported)
- **Without twins:** crack IoU +0.0175 [+0.0066, +0.0277], relF1@2 +0.0184. Without both: the same.
- **test_noscuff:** the same as test (+0.0101 / +0.0104).
- **Per source, test crack IoU at b 0:** up in all four (ARTS 0.424 → 0.449, BMRK 0.387 → 0.402, CFVS 0.546 → 0.554, CSIR 0.417 → 0.425).
- **Singles vs ensemble (descriptive):**
  - test crack IoU: E-SKR2 0.4917 vs singles 0.4741 ± 0.0031; E-PF 0.4815 vs 0.4651 ± 0.0048.
  - E1 any-hit: both ensembles are below their single means (E-PF 0.3446 vs 0.3811; E-SKR2 0.4122 vs 0.4250). Averaging narrows predictions.
  - The single-model any-hit Δ (+0.044, #5) is +0.068 at ensemble level.
- **FINAL** (cv02, R34 5-seed, b +0.75) clean-test 0.492, descriptive only:
  - E-SKR2 clean 0.4947 at b 0 and 0.4949 at b 1.0;
  - E-PF 0.4846 at b 0, and 0.4948 at b 1. b 1 is not an E-PF OP: its D2 b is 1.5, flagged.
- **B5 operating points / cell-level:** omitted (build Q5 ruling), as §4 allows.

## 4. Deployable recommendation (S)
1. **By the locked protocol: E-PF at argmax (b 0) stays the deployable candidate.** E-SKR2 is not recommended at its D2 operating point b 1.0, where it fails both precision guards against E-PF.
2. **E-SKR2 at b 0 is not a pre-registered deployable option.** Its D2 rule chose b 1.0.
   - At b 0 it beats E-PF on test and E1 with no guard trip. But more than half of its test gain, and 60% of its any-hit gain, is volume that E-PF gets from a bias step.
   - Taking E-SKR2 at b 0 now would be an OP picked after seeing test and E1. That is a judgement, not a confirmation.
3. **What SKR2 adds at matched volume (E1, descriptive): relF1@2 +0.024 and any-hit +0.027, with fewer false-alarm px.** This is real-looking but small, and it is concentrated in scuff + half-cut cells. E1 inactive is −0.042 in 3 images.
4. **For the user** (team-lead to batch), three options:
   - (a) record the FAIL; E-PF stays (coach's recommendation);
   - (b) if an SKR2 deployable is wanted, a new protocol with a symmetric OP rule (e.g. both arms at matched val crack precision, or a shared b), on data not yet opened. **No unopened test-like set exists for these 10 models:** test and E1 are opened twice (#5, #6).
   - (c) the width-flag rule itself (0.05 on val pixel precision) decided this verdict by 0.0015. Any change to it is a new pre-registered question, not a re-pick here.

## Disclosures
1. **Predecessor's self-test read E1 any-hit early** (coach, logged 22:25). The self-test of `coach_skr2e.py` on PF2E's opened files printed E1 any-hit for PF2E's ensembles: house 81 / 296 (E-g) and E-PF 102 / 296 at b 0. This was a new readout on already-opened E1 files (#4).
   - **Timing (judge fix 2a, E):** `coach_skr2e.py` mtime is 22:25:11. That is after lock (21:59), APPROVED (22:24) and the #6 run start (22:24:38), and before any #6 output existed (decisions 22:28:05). So it was **during the #6 run, before any of its output**, not "before opening #6".
   - **Who printed it (judge fix 2b, E):** runner's boot self-test (3) (`skr2e_boot.py` l.277-282) computes the E-g vs E-PF any-hit difference internally and **prints only a boolean**. Only coach's self-test printed the counts.
   - **Status (judge fix 2c):** E-g 81 / 296 vs E-PF 102 / 296 (+21 hits, +0.071) **is not a PF2E result**. PF2E did not pre-register it. It must not be cited as "PF lifts E1 any-hit"; it is descriptive at most, and only with this disclosure.
   - SKR2E v1 was locked and every choice pre-set, so nothing depended on it.
   - E-PF's 102 is the comparator value. The opening recomputed it and found it equal (checks: 102 / 296).
2. **E1 #6 is not new evidence.** It re-measures #5's models (SKR2 s5-9, SUPPF s5-9) as ensembles. E-PF's files are PF2E's (#4), identity EXACT.
3. **My read-only copy of gaint out/.** After the respawn I copied gaint out/ to my scratch read-only (ssh `ls` / `md5sum` / `stat`, rsync). This was while runner's post_local was adding the record copies and MANIFEST.
   - No process of mine ran on gaint.
   - The copy equals runner's pull byte for byte (MANIFEST 9b43e636). No extra inference and no extra E1 read beyond the opening's files.
4. **`coach_skr2e_extra.py` was written after I saw the verdict.** It computes reported readouts only. Every number in it equals runner's independently built skr2e_boot §4 output.
5. **The test matched-volume numbers (§3a) are not a pre-registered readout.** They are a crude linear interpolation between two stored b's, test-oracle and descriptive. They choose nothing and are labelled so.
6. **B5 / cell-level omitted** (build Q5).
7. **CIs:** mine use my own RNG, so they differ from runner's in the 3rd decimal by design.

## 5. Checks requested of judge
- The verdict and the two trips, from the per-cell files.
- The 0.0485 width-flag drop and the D2 b 1.0 for E-SKR2.
- The matched-volume readings in §3a: are they fair as stated?
- The §7 mechanism qualification in §3a.
- The any-hit concentration in §3c.

## judge: adversarial check (2026-11-02 23:39 IST; verify_skr2e as of md5 b9d8c7da; raw MANIFEST 9b43e636, md5sum -c OK 17 / 17 by judge)
**Verdict: CONFIRMED. SKR2E FAILS by the locked rule** (protocol §3b / §3c: G2a and G2b trip at the headline pair, E-SKR2 b 1.0 vs E-PF b 0). **E-PF at argmax stays the deployable candidate.** Five fixes below (wording and disclosure; no number or verdict change).

Code (own, numpy, imports nothing from Track M / skr2e_boot / coach; laptop only):
- `judge/skr2e_recompute.py` 5299548d, written and self-tested **before any SKR2E number was read** (log 23:33). SELFTEST on PF2E's opened files: E-PF − E-g b 0 = verify_pf2e to 4 dp, CIs included (`judge/out/skr2e_recompute_selftest.txt`). It printed E-PF's E1 any-hit 102 / 296 (the SKR2E comparator); E-g's any-hit was deliberately not printed.
- Run on the pull → `judge/out/skr2e_recompute_out.txt` 96f838d0 (log 23:34, before I opened runner's or coach's output).
- Extras (reported only) `judge/skr2e_extra.py` dc419136 → `judge/out/skr2e_extra_out.txt` cda15388.
- Result: every point estimate = runner's fc41eeaa and coach's 851403ca / dfd9cfa3 to 4 dp; my seed-0 CIs = runner's exactly. Same pass / fail sets, same two trips.

**Integrity (E):**
- Members are s5-9 in both arms; latest.pth md5s = verify_pf2e (SUPPF) and the S2 opening (SKR01).
- Revisions e544133 / c9bbb02, model code e544133. U {0, 1, 1.5} written for both arms.
- GT counts: val 125 and E1 296 comps; 74 crack-free E1 cells; GT-only columns are equal across arms and b.
- **E-PF identity vs PF2E b 0 and b 1.5: 0 of 520 cells differ.**
- D2 re-derived from the stored sweep = the file (val cells re-summed at U: \|d\| 0).
- Order: `run_full.log` has the decisions (mtime 22:28:05) before "test done" and "ext done".

**The points team-lead asked for:**
1. **Verdict at b 0.**
   - Primaries: test crack IoU +0.0102 [+0.0031, +0.0197] and relF1@2 +0.0104 [+0.0016, +0.0232] PASS (clean the same); inactive n.d.; E1 relF1@2 +0.0353 [+0.0102, +0.0613] and any-hit +0.0676 [+0.0253, +0.1282] PASS. No primary fails.
   - §3c's PASS needs "no guard trips (at b 0 or at the headline pair)", so **the verdict at b 0 is FAIL**. Coach states this correctly. It is not "PASS at b 0, FAIL elsewhere": there is one verdict, FAIL.
2. **Bias share (both arms at every b in U, plus the E1 sweep).** Coach's §3a is right; I add three things:
   - **Test (E):** E-PF at b 1 (pred / GT 1.149, wider than E-SKR2 b 0's 1.056) equals E-SKR2 b 0 on both test crack primaries (−0.0002 / −0.0013). So **the test pass at b 0 is not distinguishable from a bias step on E-PF.** What E-SKR2 keeps is precision at equal score: relP@2 +0.012 at less volume. That is a slightly better trade-off, not a higher score.
   - **The test "upper bound" (S):** it rests on E-PF being concave in pred / GT between two stored points, which is unverified on test. The same two-point interpolation on E1 overstates the remaining gap (+0.030 against +0.024 from the fine sweep), so the direction is plausible. Say "likely upper bound".
   - **E1 relF1@2 is a curve shift, not a bias shift (E, sweep).** E-SKR2 is above E-PF at every grid b at equal b (+0.028 … +0.046) and at matched volume (+0.023 … +0.047, b 0 … 2.25), with fewer crack-free px at matched volume (−897 … −2,687). This is the strongest pro-SKR2 evidence in the opening. It is still a re-measurement of #5 (point 6).
   - **any-hit is mostly volume:** E-PF's own b 0 → 0.5 gain (+0.064) equals the whole b 0 gap (+0.068).
3. **Every guard at both OPs (E).** All four as in coach's §2. The two trips are not noise and not knife-edge:
   - G2a: −0.0379, image-bootstrap CI [−0.052, −0.027], P(< −0.03) 0.91.
   - G2b: ×2.12, cluster CI [×1.70, ×2.58], P(> 1.5) 0.997.
   - At b 0: G2a −0.011 [−0.018, −0.006]; G2b ×1.06 [×0.83, ×1.22].
   - **Structural point (fix 3 below):** against E-PF at b 0, G2b trips for **every** E-SKR2 headline b ≥ 0.5 on the grid (×1.58 at 0.5, ×1.83 at 0.75, ×2.12 at 1.0). Only b 0 / 0.25 escape. So once E-SKR2 cleared its width flag (by 0.0015), FAIL was near-certain from volume alone.
   - This is the asymmetry my predecessor's D1 accepted on purpose: "at an asymmetric headline pair it penalises the bias step, which is the right side". §5 foresaw it. judge owns that design and does not ask for any change to the verdict.
   - It answers the protocol's question as framed: **as deployed, E-SKR2 at b 1.0 makes 2.1× E-PF's false-alarm px on clean E1 cells and −0.038 test relP@2.** That is a real deployment cost. It is not a recipe defect: at equal b 1 the deltas are −0.015 / ×0.87.
4. **any-hit concentration (E).** Coach's §3c is right. Add:
   - the +20 hits sit in 6 images, with 0 images down (sign test p 0.031);
   - 45% of the gain is one cell (CSIR_02222 +9), and the top 3 images hold 80%; **n_eff of the gain is 3.6 images**;
   - all 20 hits are in scuff + half-cut cells; the other 77 cells are 18 / 22 in both arms.
   - So the any-hit pass = 20 components in ~4 effective scuff + half-cut images, 60% of it volume. Do not report it as "SKR2 finds more E1 cracks" without this sentence.
5. **"A PASS names its carrying primary."** Not triggered (FAIL). The b 0 passing primaries are named correctly (test crack IoU and relF1@2; E1 relF1@2 and any-hit).
6. **A test-only pass read as confirming E1.** Not the case here (E1 co-primaries pass at b 0 too). The mirror risk is real, though: a FAILED opening whose b 0 E1 lines pass will be read as "E1 gain confirmed at ensemble level". It is not. Fix 1.
7. **Disclosure of the PF2E any-hit readout.** Present (disclosure 1) and substantively right. It needs fix 2 for precision.

**Fixes (before anything goes to the user):**
1. **Add to Verdict (wording, S):** "The b 0 E1 co-primary passes are not a confirmation of SKR2's E1 gain. The opening FAILED, and E1 #6 re-measures opening #5's members (not new evidence). At ensemble level, SKR2's E1 relF1@2 gain is re-measured (+0.035; +0.024 at matched volume), not confirmed."
2. **Disclosure 1, precision (E):**
   - (a) Timing: `coach_skr2e.py` mtime 22:25:11. That is after lock (21:59) and APPROVED (22:24), and after the #6 run started (22:24:38), but before any #6 output existed (decisions 22:28:05). Say "during the #6 run, before any of its output", not "before opening #6".
   - (b) Runner's boot self-test (3) (`skr2e_boot.py` l.277-282) computes the E-g vs E-PF any-hit difference internally and **prints only a boolean**. Only coach's self-test printed the counts.
   - (c) E-g 81 / 296 vs E-PF 102 / 296 (+21 hits, +0.071) **is not a PF2E result**: PF2E did not pre-register it. It must not be cited as "PF lifts E1 any-hit"; descriptive at most, and only with this disclosure. I did not re-read E-g's count (no further readout).
3. **Add the structural point (3 above) to §3a or the Verdict:** G2b trips for any E-SKR2 headline b ≥ 0.5 vs E-PF b 0. G2b's CI lies wholly above ×1.5 ([×1.70, ×2.58]); G2a's lies mostly below −0.03 ([−0.052, −0.027], P 0.91), so G2b alone would carry the FAIL. So the width flag (0.0485 vs 0.05) alone decided FAIL vs PASS.
4. **§3a test line:** "upper bounds" → "likely upper bounds (assumes E-PF is concave in pred / GT between b 0 and 1; unverified on test; the E1 analogue supports it)". Also add the sentence "E-PF at b 1 equals E-SKR2 at b 0 on test crack IoU / relF1@2; E-SKR2 keeps +0.012 relP@2 at less volume".
5. **Multiplicity (if anyone reads b 0 as a win):** 4 of 5 primaries pass at b 0, and the test relF1@2 bound is within 0.002 of 0. The family-wise false-pass rate is ~12% for these objects and ~15-20% as a recipe claim (§3c). These are re-measurements of opened effects, so read nothing confirmatory into them.

**§4 recommendation:** I agree with (a): record the FAIL; E-PF stays.
- On (b): **E-SKR2 at b 0 is an OP chosen after seeing test and E1 twice (#5, #6).** If the user wants it anyway, it is the user's judgement on the recorded evidence, labelled post hoc. No opened set can confirm it. A new protocol needs new unseen-panel data, or must be framed as a val-only OP-rule change with no confirmatory claim.
- (c) is right: the 0.05 flag decided this by 0.0015. A change to it is a new pre-registered question.

**Suggested user summary (S, for team-lead):** "SKR2E FAILED as pre-registered. The val rule deploys E-SKR2 at bias 1.0 (its width flag passed by 0.0015). There it costs test relP@2 −0.038 and 2.1× the false-alarm pixels on crack-free E1 cells, against E-PF at argmax. E-PF stays the deployable model. At a shared argmax, E-SKR2 is ahead on test crack IoU / relF1@2 (+0.010), but E-PF matches that with a bias step. It is also ahead on E1 relF1@2 (+0.035, +0.024 at matched volume, a real curve shift) and on E1 any-hit (+0.068: 60% volume, 20 components in ~4 effective scuff + half-cut images). These are the same models as opening #5, so this is a re-measurement, not a confirmation. E1 inactive is −0.042 (3 images). Deploying E-SKR2 at argmax would be an operating point picked after test and E1; no unopened set exists to confirm it."
