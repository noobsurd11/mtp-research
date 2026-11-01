# coach verify: protocol_PF2 opening (seeds 5-9; SUP100-g, SUP100-PF, RN50-PF; 100% labels, gaint, e544133)

coach, 1 Nov 2026 08:30 IST. Independent recompute. Tags: E (file), S (judgement).
- **Inputs:** my own pull of gaint `el_f3/reports/pf2/post/` into `results/pf2/coach_raw/` (MANIFEST 3827f7c0, 290 files, `md5sum -c` OK; byte-identical to runner's `results/pf2/raw/`, `diff -rq` 0 lines).
- **Code:** `scripts/coach/coach_verify_pf2.sh` a74927f7 (pull + integrity); test verdicts by the predecessor's independent `team_2026-10-29_features/scripts/coach_verify.py`; E1 co-primaries, width checks and strata by my own `scripts/coach/coach_e1_pf2.py` c4fd3a97 (self-tested on opening 1: exact). Outputs `results/pf2/coach_v/` (MD5 file there).
- **vs runner's `results/pf2/results_pf2_runner.md` (8bc1512e): CONFIRMED.** Every test primary (both sets, both contrasts, tau 0 and tau 1), both E1 co-primaries with per-seed values, the E1 width numbers and the strata match to 4 decimals.

## Verdicts (protocol_PF2 §3, rule 1 /3, 5 v 5)
1. **PF2 (SUP100-PF − SUP100-g): PASS on both lines.**
   - **"E1 replicated" on inactive IoU, not on crack recall.** E1 inactive IoU 0.0481 → 0.2371, **+0.1890 (thr 0.0433) BETTER**; E1 crack recall 0.1715 → 0.1986, +0.0271 (thr 0.0370) n.d. No WORSE among the 5 co-primaries. Precision flag: not triggered (recall not BETTER; E1 crack precision −0.026).
   - **Test: relF1@2 BETTER in both sets** (all 50: 0.8730 → 0.8847, +0.0117, thr 0.0100; clean: 0.8772 → 0.8891, +0.0120, thr 0.0100); crack IoU n.d. (−0.0011 / −0.0009); inactive IoU n.d. (+0.0173 / +0.0171, thr ~0.029). Width check ok (relP@2 +0.0009). Same at tau 1 (relF1@2 +0.0126 / +0.0127 BETTER).
   - Wording (pre-registered §6): "PF lifts E1 inactive IoU, replicated on new seeds, same E1 cells." Crack recall: not replicated (n.d., same sign).
2. **RN (RN50-PF − SUP100-PF): FAIL.** Test inactive IoU **WORSE in both sets** (0.4557 → 0.4269, −0.0289, thr 0.0251; clean −0.0289, thr 0.0249), the pre-stated risk (Track M R3 −0.025). Crack IoU −0.0056 n.d., relF1@2 −0.0028 n.d. Same at tau 1. Named secondary (E1 scuff + half-cut crack recall): 0.1378 → 0.1153, −0.0225 n.d. (D's house RN50 +0.060 did not carry over under PF). **The encoder gate is closed for RN50 under PF** (§6).
3. Bottom (RN50-PF − SUP100-g), reported: n.d. on all three test primaries.

## Robustness and caveats (E / S)
- **The test relF1@2 pass is narrow.** It clears the 0.01 floor by 0.0017 / 0.0020. Paired image bootstrap: +0.0117 [−0.0034, +0.0292], P(Δ > 0) 0.93 (all 50); **leave-top-3-out +0.0015**. The pass rests on a few cells. Mechanism support: test relR@2 at relP@2 ≥ 0.90 (B5, reported) +0.034 in both sets with per-run and with arm-pooled OPs (thr 0.0155), and relR@2 at argmax 0.8145 → 0.8344 at unchanged relP@2. Seeds 0-4 had the same sign (+0.0117 all 50, +0.0050 clean; n.d.).
- **The E1 inactive gain is large and stable:** 5/5 PF seeds 0.207-0.279 vs 5/5 house 0.025-0.089; strata: half-cut 58 0.162 → 0.537, scuff + half-cut 29 0.178 → 0.572, full 48 0.025 → 0.097 (all BETTER by the arithmetic). It is concentrated on half-cut cells, as on seeds 0-4. Claim scope: same E1 cells; seed noise controlled, cell selection not (E1 was read many times before).
- **E1 crack (width-robust, reported):** relR@2 +0.051 (thr 0.0515, n.d. by 0.0007), component recall +0.055 (thr 0.0552, BETTER by 0.0002), relF1@2 +0.037 n.d.; same sign as recall. B5 on E1 (descriptive, val-chosen OPs): component recall at P ≥ 0.90 +0.066 / +0.067, relR@2 at relP@2 ≥ 0.90 +0.064 / +0.066 (per-run / pooled), both BETTER by the arithmetic.
- **10-seed pooled (seeds 0-9, descriptive, runner's file):** E1 crack recall 0.170 → 0.206; E1 inactive 0.044 → 0.241.
- **Crack px on crack-free cells** (mean over seeds): val 31 cells SUP 164.8 / SUPPF 6.8 / RN50-PF 17.0; E1 74 cells 3,626 / 3,931 / 4,327; test 2 cells ~0.
- **Encoder cosine at 20k:** SUP100-g layer3 / 4 0.007-0.017 / −0.000-0.004 (erased); SUP100-PF 0.928-0.929 / 0.931-0.941; RN50-PF 0.928-0.930 / 0.907-0.919. **Anomaly (descriptive):** RN50-PF s5 layer4 0.998 / norm 1.00 at 20k (as at its 4k gate), i.e. its layer4 hardly trained, unlike s6-s9. Same config (config OK) and the same schedule: runner compared s5 vs s6 'PF encoder lr' lines, IDENTICAL over 400 lines (also = SUPPF s5); s5's layer4 is already 0.998 at 4k with norm ratio 1.00 (s6-s9 1.10-1.12). Seed-specific: layer4 barely moved in that run (S: a near-dead path into layer4); not investigated further. Its test inactive is not an outlier (RN50-PF inactive sd 0.006), so it does not drive the RN verdict.
- **Per source (descriptive):** RN50-PF inactive drops in ARTS (0.534 → 0.000, few inactive px) and BMRK (0.360 → 0.313); crack and relF1@2 in CFVS drop by ~0.01.
- **Scuff-ignored test (descriptive, Om B2):** same verdict pattern (PF2 relF1@2 BETTER; RN inactive WORSE).
- **B5 OPs:** reachable for all 15 runs, no edge flag; val-chosen biases: SUP100-g b_rel ~2.3, SUP100-PF ~3.9, RN50-PF ~3.7 (pooled), i.e. PF needs a higher crack bias to reach the same val relP@2 (less confident on crack at argmax).
- **Integrity:** 15/15 rc 0, step 20000, 1 header, 0 tracebacks; PF lines in PF arms only (400 each); configs = one change + seed; G6 PASS (s5 4k); tau0 == default; e544133, 0 tracked changes; FROZEN extras rc 0 (scuffign; B5 45/45 self-checks PASS at exact, cuda).
- **Memory (runner, disclosed):** the LA pass peaked at 7,758 MiB (gate assumed 5,824 from a val-only smoke); min free 2,635 MiB beside two THIN training runs and finllm. The 2 GB floor held by 587 MiB; finllm unaffected. THIN's opening gate raised to 9,900 before any THIN number.

## What this decides (S, for team-lead and the user)
- **BEST stays SUP100-PF.** It is now **better on test relF1@2 (narrowly) and much better on E1 inactive IoU**, with no test cost. RN50-PF is closed (test inactive WORSE).
- **Pre-registered follow-ups (§6):**
  1. Test PASS → the ensemble follow-up: SUP100-PF 5-member mean-softmax ensemble vs SUP100-g's, crack bias by FINAL's val rule, paired image bootstrap; one more counted test opening; FINAL 0.492 descriptive. Needs a short protocol (inference only).
  2. "E1 replicated" on inactive → Om B6 (module-grouped CV for a powered inactive claim), by user decision.
- **Idea 8 full arm:** its deployable comparator stays SUP100-PF (RN50-PF did not win).
- THIN-B3 (running) and HC use SUP100-PF as BEST: unchanged.

## Addendum: RN named secondary, ensembles at +0.75 (pre-registered §3c; computed after the opening; descriptive)
- runner's `d_infer.py` v3 (9e8fa7b2, reviewed), gaint CPU fp32, val + E1 only, val gate passed (+0.0004 / +0.0004). Files `results/pf2/d_rn/` (MANIFEST OK; cells JSON 5fb73bda). **Recomputed by coach from the cells JSON: identical** (`results/pf2/coach_v/rn_ensemble_recompute.txt`).
- SUPPF_5 vs RN50PF_5: E1 scuff + half-cut (29) recall 0.168 → 0.143 (−0.025); half-cut without scuff (29) 0.504 → 0.574; full (48) 0.461 → 0.499; E1 crack P / R / IoU 0.414 / 0.244 / 0.182 → 0.425 / 0.237 / 0.180; crack px on 74 crack-free E1 cells 5,208 → 5,559; E1 inactive IoU 0.282 → 0.255. Val: crack IoU 0.4441 → 0.4496, relF1@2 0.9030 → 0.9088, inactive 0.5100 → 0.5637.
- Reading (S): under PF the RN50 target gain of D (+0.060 under the house recipe) does not appear (−0.025); RN50-PF helps the non-scuff half-cuts and full cells a little and loses on the scuff + half-cut group. The RN verdict (FAIL, test inactive WORSE) stands; RN50 is closed under PF.
