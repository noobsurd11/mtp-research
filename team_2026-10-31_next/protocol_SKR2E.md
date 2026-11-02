# Protocol SKR2E: SKR2 vs SUP100-PF as deployable 5-member ensembles (inference only, gaint CPU)

coach, 2 Nov 2026. **v1 LOCKED 2026-11-02 21:59 IST** (judge SIGNED the v1 candidate 1c45ab19; `judge/review_SKR2E_v09.md` ba54abf9). No SKR2E number exists at lock.
- Two post-sign edits, both from judge's non-blocking notes: the G1t false-FAIL wording becomes ~8-10% (§3b, §5); the §4 matched-volume source is made concrete as an E1 aggregate sweep (§6, reported only).
- History: v0.9 ce9e55ee; judge's review d5b62d63 applied in full (D1, G1t, Q2, Q3, Q5, wording 1-4).
- **Go:** the user's go was relayed by team-lead on 2 Nov, after verify_skr2_hc2 4d7dc311: "confirm SKR2 as deployable", built like PF2E, with E1 co-primaries (E1 opening #6) including any-hit recall, and precision / false-alarm guards analogous to G2.
- **No training.** Launch on coach's APPROVED after §6's build. Tags: E / R / S.

## 0. What I had seen (E)
- **SKR2 singles** (`verify_skr2_hc2.md`, judge CONFIRMED; skr2_SKR01_100pct_s5..9 vs pf2_SUPPF_100pct_s5..9, argmax):
  - E1 crack relF1@2 +0.0364 (thr 0.0351) BETTER. The label is fragile (5 / 10 seed drops); the effect is robust (seed-aware P 0.985) and is not a bias shift.
  - E1 any-hit +0.044 (n.d.).
  - Test crack IoU +0.009 (P 0.98) and relF1@2 +0.009 (both n.d.); inactive +0.010.
  - Precision: test relP@2 −0.012; E1 crack-free px ×0.97.
- **E-PF** (`verify_pf2e.md`; mean softmax, gaint CPU fp32, `pf2e_infer.py` 272463d3):
  - Operating point: D2 b 1.5 (val crack precision drop +0.075), so headline b 0.
  - Test at b 0: crack IoU 0.4815, relF1@2 0.8942, inactive 0.4613. E1 at b 0: relF1@2 0.4345; crack px on the 74 crack-free cells 2,528. E1 any-hit never computed.
- **Bias alone moves an ensemble by about the effect under test** (E, PF2E, judge):
  - E-PF b 0 → 1.5: E1 relF1@2 +0.039, test relF1@2 +0.014, test crack IoU +0.007;
  - E-g b 0 → 1.25: E1 relF1@2 +0.045;
  - any-hit is monotone in b.
- **The SKR2 singles start wider** (val pooled, judge `judge/out/skr2e_check_out.txt`):
  - relR@2 at b 0: 0.860 vs 0.846;
  - pixel-precision drop at b 1: 0.013 vs 0.0145.
  - So E-SKR2 may reach D2 at a smaller b, with a smaller drop, and pass the width flag where E-PF's tripped. That is why the verdict is at one shared b (§2).
- **E1 GT crack components** (E, GT only, judge): 296 components (≥ 20 px) sit in 21 of 71 images.
  - Concentration: the top 3 images hold 57%, the top 10 hold 94%; n_eff 7.1 images.
  - **274 of the 296 are in the 29 scuff + half-cut cells.**
  - So E1 any-hit is in effect a scuff + half-cut readout and will likely be n.d.
- **Disclosure (S):**
  - SKR2 was chosen for this protocol because of its opening #5. The members are those same 5 models, with test and E1 already opened, so **E1 #6 re-measures #5's effect on the deployable object; it is not new evidence** (as PF2E vs PF2).
  - E-PF's files are opened (#4) and are reused as the comparator only after the identity check (§6).

## 1. Question
Is SKR2 better than SUP100-PF as the deployable object, a 5-member mean-softmax ensemble?
- **Contrast:** E-SKR2 (skr2_SKR01_100pct_s5..9; el_thin c9bbb02) − E-PF (pf2_SUPPF_100pct_s5..9; el_f3 e544133).
- **Common settings:** final weights (latest.pth, step 20000), mean softmax, TTA off. Both arms run in one process, with one model-building code (el_f3 e544133, strict state-dict load), on gaint CPU fp32.
- **Arm difference:** the only training change is `loss.skel_recall.weight=0.1`. The architecture is the same (S0 identity at d93d9a1 = c9bbb02's training code).

## 2. Operating points (val only, fixed rule, before any test or E1 inference)
- **Verdict b: b 0 (argmax) for both arms (D1, judge).** Bias alone moves an ensemble by about the effect under test (§0), so the contrast is at one shared b.
  - b_D2(E-SKR2) is not shared: E-PF's own width flag rejects b > 0.
- **Deployable OP (FINAL's rule D2, Track M `m9_final.py`, exactly as PF2E §2), per ensemble:**
  - grid b ∈ {0, 0.25, …, 3};
  - the smallest b with val relR@2 ≥ 0.90, used if its val relP@2 ≥ 0.90; else the b with max val relF1@2;
  - **headline b = 0 if val crack (pixel) precision drops by > 0.05 from b 0 to the chosen b**, else the chosen b.
- **Written b's:** both arms are written at the union {0, b_D2(E-PF), b_D2(E-SKR2)}, which contains both headline b's.
- **Order:** decisions go to `skr2e_val_decisions.json` before any test or E1 cell is read.
- **E-PF check:** E-PF's decisions must equal PF2E's (b 1.5, drop 0.0753, headline 0), else stop (§6).
- **Reported, at the headline pair** (each arm at its own headline b), not the verdict:
  - the primaries;
  - E-PF at E-SKR2's headline b.

## 3. Verdict
### 3a. Primaries (all at b 0 for both arms; Track M contrast rule, as PF2E §3)
- **Test primaries:** crack IoU, crack relF1@2, inactive IoU.
  - Sets: all 50, and clean (without CSIR_00070_r8_c4).
  - Paired image bootstrap: 2,000 resamples, seed 0.
- **E1 co-primaries (E1 opening #6; second test set, read once here), all 106 cells:**
  - **E1 crack relF1@2**;
  - **E1 any-hit component recall** = (GT crack components ≥ 20 px with ≥ 1 px within 2 px of a prediction) / (GT crack components ≥ 20 px). It is read from the cells' `crack_cc` gt list ([size, hit]; hit = px within 2 px of the prediction, m_common 10f0d37c `comps` with `near_pr`). This is the definition of protocol_SKR2_HC2 §3a.3.
  - Bootstrap: paired **module-cluster**, 2,000 resamples, seed 0. Cluster = the stem minus `_rN_cM` / `_cellN` (source image): 71 clusters. any-hit = the ratio of pooled component counts over the resampled cells.
  - any-hit is mostly a scuff + half-cut readout (§0) and will likely be n.d.
- **Primary pass / fail:**
  - **pass:** the 95% CI lies wholly above 0. For test this must hold in both sets, or in one set with a same-sign estimate in the other.
  - **fail:** the 95% CI lies wholly below 0, in either set.
### 3b. Guards (pre-registered FAIL rules; any trip FAILS SKR2E). Each guard is evaluated **at b 0 AND at the headline pair** (E-SKR2 at its headline b vs E-PF at its headline b); point estimates; a trip at either FAILS.
- **G2a test precision:** test crack relP@2 Δ (all 50) **< −0.03** → FAIL.
- **G2b E1 false alarms:** E-SKR2's crack px on E1's crack-free cells (GT crack px 0; 74 cells) **> 1.5 ×** E-PF's → FAIL. At b 0, with E-PF at its PF2E value of 2,528 px, the bar is 3,792 px.
- **G1t test inactive** (judge Q2; the singles' G1): test inactive IoU Δ **≤ −0.015 in both sets** → FAIL.
  - Why: the inactive primary's fail rule alone is weak (CI half-width ~0.065), so an HC-size loss (−0.025) would pass silently.
  - Null false-FAIL ~8-10% (ensemble seed noise ~0.011, judge; ~8% at one OP, up to ~10% when E-SKR2's headline b > 0 adds a second). SKR2 singles are at +0.010.
- **G1e E1 inactive:** E1 inactive IoU Δ with module-cluster CI wholly below 0 → FAIL. **It trips only on a collapse:** the CI half-width is ~0.18 (PF2E), so it would not catch HC2's −0.08. It is a 3-image readout (n_eff 3.3).
- Context: SKR w 1.0 singles would trip G2a (−0.070) and G2b (×2.4). SKR2 singles trip none of G2a / G2b / G1t (−0.012, ×0.97, +0.010).
### 3c. Verdict (at b 0)
- **PASS:**
  - ≥ 1 primary passes (3 test, 2 E1);
  - no primary fails;
  - no guard trips (at b 0 or at the headline pair).
- **FAIL:** any primary fails, or any guard trips.
- **Else n.d.**
- **Wording (fixed now):**
  - A PASS names the primary that carries it.
  - A PASS carried by test primaries only must also say: "SKR2's single-model E1 gain is not confirmed at ensemble level."
  - n.d.: "SKR2's single-model E1 gain is not confirmed at ensemble level; E-PF stays the deployable candidate."
- **Multiplicity (S, judge Q5):**
  - Scope: 1 contrast; 3 test primaries × 2 sets (nearly the same cells); 2 E1 co-primaries; 4 guards (each at 2 OPs); one opening.
  - **For "these two ensembles as objects":** family-wise false PASS ≤ ~12% (crude; per primary ~2.5% one-sided).
  - **As a recipe claim ("SKR2 is better"):** ~15-20%. The fixed-model CIs leave out seed noise (per primary ~3-6%).
  - G1t's ~8-10% null false-FAIL is on the other side. No correction (house rule).

## 4. Reported (never change the verdict)
- **Every readout at the union of b's.** Explicitly:
  - the headline pair;
  - E-PF at E-SKR2's headline b;
  - each D2 b.
- **Cell sets and sources:** per source; four cell sets (all, clean, without twins, without both).
- **Crack capture:** relR@2, relP@2, pixel P / R, component R / P (≥ 50% covered), any-hit on test.
- **Width:** pred / GT crack px on test and E1; crack px on crack-free cells (test, E1, val).
- **E1 strata:** 29 scuff + half-cut / 29 half-cut without scuff / 48 full; 58 / 48; 29 / 77.
- **E1 concentration:** inactive concentration and leave-top-3-images-out; any-hit component counts per image (top 3 / top 10).
- **Robustness:** leave-one-cluster-out range for each E1 co-primary.
- **Matched-volume check** (judge's not-a-bias-shift form; E1-oracle, descriptive, chooses nothing): E-PF on E1 at the b where its pred / GT equals E-SKR2's at b 0, read from the E1 aggregate sweep (§6).
- **Other:**
  - scuff-ignored test (test_noscuff);
  - singles vs ensemble (descriptive);
  - FINAL 0.492 (cv02, b +0.75), descriptive only.
- **B5 operating points and cell-level:** if PF2E's `pf2e_b5.sh` pattern can be reused with only the arm list changed (frozen calib_dump c172717e group mode, el_metrics 6e73ff11, CPU), as a frozen extra pass after the verdict files are pulled. Else omitted, and that is disclosed.
- **Not applicable:** LA tau 1 (the bias is chosen on val).

## 5. Expectations (S)
- **Operating points:** E-PF's headline b is 0 (as PF2E). **E-SKR2's headline b may be > 0** (it starts wider and its precision falls more slowly, §0). **The verdict is at b 0 either way**; the headline pair is reported and guarded.
- **Test at b 0:**
  - crack IoU and relF1@2 +0.005 … +0.012. The singles' fixed-model image bootstrap excluded 0 ([+0.0025, +0.0180] / [+0.0010, +0.0209]), so a test pass on one of them is plausible (~40-50%);
  - inactive ±0.02. G1t null false-FAIL ~8-10%.
- **E1 at b 0:**
  - relF1@2 +0.02 … +0.04, with a cluster CI likely to touch 0 (PF2E: ±0.06);
  - any-hit +0.02 … +0.05, likely n.d. (scuff + half-cut readout).
- **Guards:** relP@2 −0.005 … −0.02; crack-free px ×0.9 … ×1.2. If E-SKR2's headline b > 0, G2a / G2b at the headline pair are the ones that may bind.
- **Likeliest:** a PASS carried by a test crack primary (with the "not confirmed at ensemble level" line for E1), or n.d.

## 6. Build, gates and cost (runner builds; coach reviews before APPROVED)
- **Script:** `skr2e_infer.py` = `pf2e_infer.py` 272463d3 with only these changes:
  - arm labels and lists E-PF / E-SKR2;
  - a per-arm REVISION assert (e544133 / c9bbb02);
  - a per-arm m0 reference for the gate;
  - writing both arms at the union of b's (§2);
  - outputs `<out>/E-{PF,SKR2}.b<b>.json` and `skr2e_val_decisions.json`;
  - the same image read, cell_stats (m_common 10f0d37c), bias, D2 rule and width flag.
  The diff vs 272463d3 is shown in the build note.
- **E1 aggregate sweep (reported only; judge note 1):** written after `skr2e_val_decisions.json`, per arm and per b on the D2 grid (0 … 3, step 0.25): E1 pred / GT crack px, relF1@2, any-hit, crack-free px (aggregates only; no per-cell E1 file at those b's). It feeds §4's matched-volume line and nothing else. If the build cannot store it, the §4 line is omitted and that is disclosed.
- **Model:** built with el_f3 e544133 code. `load_state_dict` is strict; SKR2 checkpoint keys and shapes are asserted equal to SUPPF's.
- **Gates before any test / E1 cell (any failure exits):**
  1. each arm's member s5 alone vs its opening m0 JSON (E-PF: PF2 m0; E-SKR2: `s2q/post/m0/SKR01`): val pooled crack IoU and relF1@2 at b 0 within |Δ| ≤ 0.005, and val any-hit within 0.01;
  2. **ensemble val GT crack components ≥ 20 px = m0's 125 exactly**: prediction-independent, so a mismatch STOPS;
  3. E-PF val decisions = PF2E's `pf2e_val_decisions.json` (b, drop, headline).
- **Before scoring:**
  - **E1 GT crack components ≥ 20 px = 296 exactly**, asserted; a mismatch STOPS.
  - **E-PF identity:** every E-PF cell (val, test, test_noscuff, ext) at b 0 and at b 1.5 must equal PF2E's `E-PF.b0.json` / `E-PF.b1.5.json` exactly (CPU fp32, same code). If not exact: disclosed, E-PF is taken from this run, and PF2E's files are not used.
  - **any-hit self-test:** E-PF b 0 E1 any-hit from this run = the count from PF2E's `E-PF.b0.json` crack_cc.
- **Scorer:** `skr2e_boot.py` = `pf2e_boot.py` bee9e182 + any-hit (cluster-pooled component counts) + G2a / G2b / G1t / G1e at b 0 and at the headline pair + §4 readouts.
  - Self-tests: E-PF vs E-g reproduces PF2E's verdict lines exactly; E-PF vs itself gives all CIs [0, 0].
  - md5s frozen before the run.
- **Coach's own recompute:** own code from the per-cell JSONs, own RNG.
- **Device and timing:** gaint CPU fp32, nice 19, 8 threads, CUDA hidden, tmux with a recorded PID. Not inside a runner-declared critical window (B6 scoring is GPU; this is CPU).
- **Cost:** 10 models × 210 cells at up to 3 b's: ~15-25 min CPU (PF2E 11 min). No GPU. No training.
- **Records:** E1 opening #6 is logged in `e1_openings.md` at start. Pull with a MANIFEST.

## 7. After the opening
- **PASS (b 0)** → E-SKR2 is the recommended deployable model over E-PF.
  - **"Recommended at its headline b" only if no guard trips at the headline pair** (judge D1). That is already a condition of PASS.
  - The user adopts it (handbook claim). A cv02 FINAL-style R34 SKR2 ensemble would need its own protocol.
- **n.d.** → E-PF stays the deployable candidate. SKR2's single-model E1 gain is recorded as a recipe effect not confirmed at ensemble level.
- **FAIL by G2a / G2b** → SKR2's ensemble pays a precision cost the singles hid. **FAIL by G1t** → it costs test inactive. E-PF stays in either case.

## 8. Before lock
1. judge: v0.9 reviewed (d5b62d63, NOT READY); v1 candidate 1c45ab19 SIGNED (ba54abf9). **v1 LOCKED 2026-11-02 21:59.** Judge's two build notes (E1 sweep stored or §4 line omitted; G1t ~8-10%) are checked at APPROVED.
2. Lock v1 → runner builds (§6) → coach reviews the diff, gates and self-tests → APPROVED.

## 9. Build review (coach, 2026-11-02 22:19 IST; build_skr2e.md 14c7775c; no design change)
- **Read:** skr2e_infer.py 5ba3c597 (full diff vs 272463d3, 047d3ec3), skr2e_run.sh b2816cb3 (diff bd7d7577), skr2e_boot.py 6de94f7e (verdict, guard and pair code).
- **Matches §2-§6:**
  - arms and REVISION asserts;
  - one model code, strict load; model-config and key / shape asserts (the extra assert is accepted);
  - gates (a) / (b) before the decisions, (c) after the decisions and before test / E1; the E1 GT count from the masks before any model sees an E1 image;
  - union U; the E1 aggregate sweep after the decisions (judge note 1, done);
  - E-PF identity and the any-hit self-test;
  - verdict at (0, 0); guards at (0, 0) and at the headline pair;
  - primary indices (PN: 0 crack IoU, 1 inactive IoU, 2 relF1@2) as pf2e_boot bee9e182.
- **Rulings on runner's questions:**
  - Q1: the val-only `gate` dry check is allowed before APPROVED (as PF2E).
  - Q2: the 1e-9 drop tolerance is accepted (b and headline exact).
  - Q3: the rc logic is accepted.
  - Q4: the U × U pairs are accepted, **with one fix**: the test / E1 verdict words and the guard TRIP words must be labelled "(reported, not a verdict)" at every pair other than (0, 0), and "(guards apply; primaries reported)" at the headline pair. Self-tests are re-run after the fix.
  - Q5: B5 / cell-level is omitted, and that is disclosed (§4 allows it).
- **APPROVED follows** the boot label fix (new md5 + self-test PASS) and a clean gate dry check (skr2e_gate.txt read by coach).
- **APPROVED (coach, 2026-11-02 22:24 IST).**
  - **Gate dry check** (val only; runner, 22:19:52-22:23:15, rc 0, 0 Tracebacks; gaint el_f3/reports/skr2e/, staged skr2e_infer.py 5ba3c597 and skr2e_run.sh b2816cb3, md5 read by coach on gaint): `out_gate/skr2e_gate.txt` **083c5050**, read by coach on gaint.
    - (a) E-PF s5: crack IoU +0.0004, relF1@2 +0.0004, val any-hit 110 / 125 = ref (= PF2E's own gate deltas);
    - (a) E-SKR2 s5: +0.0005 / +0.0000, any-hit 116 / 125 = ref;
    - (b) ensemble val GT comps 125 / 125.
    - No decisions file and no out/ exist.
  - **Boot label fix:** skr2e_boot.py **7520afc0** (role labels at the (0, 0), headline and other pairs). Self-test re-run by coach locally: SELFTEST PASS (PF2E report 65 / 65 lines; E-PF vs itself all CIs [0, 0]).
  - **Run:** `bash skr2e_run.sh full` once, in tmux with recorded PIDs; E1 opening #6 logged at start; pull out/ with a MANIFEST; skr2e_boot 7520afc0 locally. Then coach's own recompute; no verdict to team-lead before it.
