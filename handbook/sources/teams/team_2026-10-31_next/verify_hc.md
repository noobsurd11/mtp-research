# coach verify: protocol_HC v1.1 opening (HC vs SUP100-PF, seeds 5-9; 100% labels, gaint, el_hc c2e6973); E1 opening #3

coach (respawned session), 2 Nov 2026 03:14 IST. Independent recompute. Tags: E (file), S (judgement).

## Verdict: **n.d.** (no co-primary BETTER, none WORSE). Mechanism **passed** (+0.123 ≥ +0.05). F51 harm guard **passed** (HC better).

## Inputs and code
- **Runs (E, nq/launch.log):** hc_HC_100pct_s5..9 trained rc 0 (21:41 → 02:17:01), each `config OK ... seed K + HC change only`; config diff vs pf2_SUPPF_100pct_s5 = seed (+ run_name) + `data.synth_halfcut {p 0.35, pool data/splits/synth_halfcut_pool_ap.tsv}` only (own diff). Per stdout (grep -c only): 1 header, `step 20000/20000`, 0 Tracebacks, 400 PF lr lines, synth lines present. GPU floor held (nq gpumem min free 2,880 MiB, 22:16:46).
- **Opening:** hc_post.sh (FROZEN a23994c4), 02:18:34-03:09:57, `nq scoring done: post rc=0`; decision passes e1_coprim / shv1 / f51 rc 0; extras (enc_cosine, hc_b5, hc_scuffign) rc 0; tau0 == default cells, step 20000, code_revision c2e6973 for all 5; PF2 comparator unchanged (MANIFEST 3827f7c0).
- **Where I recomputed (disclosed):** gaint CPU (nice 19, 8 threads, CUDA hidden), after the window ended, reading in place after `md5sum -c` of the HC post MANIFEST **d5c39e0d** (190 files), the PF2 comparator MANIFEST 3827f7c0 and the 30 syn_work dumps (val / rf / SHV1 × 10 runs). runner's pull `results/hc/raw/` has the same MANIFEST. Text outputs: `results/hc/coach_v/` (MD5 file there).
- **Code (coach's own):** `scripts/coach/coach_verify_hc_gaint.sh` 0347174b; test primaries by `coach_verify.py` b0456b28 (two sets, tau 0 / tau 1, paired image bootstrap, scuff-ignored); `scripts/coach/coach_hc.py` **850e056e** (E1 co-primaries via coach_thin.e1_agg 7562d97f; SHV1 readout from the el_metrics records with own pooling / matched / oracle code; F51 guard with own 1,000-bin AP and own 36-module bootstrap RNG); B5 (reported) by coach_thin.b5_arm on calib's raw records. **Self-test:** the SHV1 code reproduces the routing pre-check (FINAL +1.1 / +1.5, 0.892 / 0.730; SUPPF s0-4 +2.9 / +3.8, 0.876 / 0.694); E1 SUPPF s5-9 inactive IoU 0.2371 = verify_pf2.
- **Cross-check vs the opening's own decision outputs:** E1 co-primaries (hc_e1_coprim, self-test 10 / 10 True), SHV1 readout (hc_shv1_read) and F51 (hc_f51; AP and FA exact, bootstrap differs only by RNG) all equal mine to 4 dp. runner's pull `results/hc/raw/` (d5c39e0d) is the record copy; no runner-side test readout was drafted (build_hc_runner §4); judge's recompute is the second computation of the test numbers.

## Co-primaries (protocol_HC §4: rule 1 /3, 5 v 5; PASS = ≥ 1 BETTER, none WORSE; test with the two-set rule)
| co-primary | SUPPF | HC | Δ (thr) all 50 | Δ (thr) clean 49 | result |
|---|---|---|---|---|---|
| test crack IoU | 0.4651 | 0.4742 | +0.0092 (0.0100) | +0.0089 (0.0100) | n.d. |
| test crack relF1@2 | 0.8847 | 0.8874 | +0.0026 (0.0100) | +0.0023 (0.0100) | n.d. |
| test inactive IoU | 0.4557 | 0.4329 | −0.0228 (0.0289) | −0.0230 (0.0290) | n.d. |
| E1 crack relF1@2 (106, one set) | 0.4202 ± 0.0272 | 0.4338 ± 0.0253 | +0.0135 (0.0429) | | n.d. |
| E1 inactive IoU (106, one set) | 0.2371 ± 0.0271 | 0.2369 ± 0.0414 | −0.0002 (0.0572) | | n.d. |
- **Verdict n.d.** Same at LA tau 1 (crack IoU +0.0030, relF1@2 +0.0012, inactive −0.0207 / −0.0211, all n.d.) and on scuff-ignored test (same numbers to 4 dp). Width check ok (test relP@2 +0.0017).
- E1 per seed: relF1@2 SUPPF 0.443 / 0.428 / 0.440 / 0.414 / 0.376, HC 0.401 / 0.425 / 0.425 / 0.462 / 0.456; inactive SUPPF 0.247 / 0.225 / 0.207 / 0.279 / 0.228, HC 0.271 / 0.239 / 0.189 / 0.202 / 0.283.

## Mechanism (protocol_HC §4-5; SHV1, val-derived, non-E1)
| arm (5 seeds pooled) | matched relR@2 at relP@2 ≥ 0.90: V0 / SHV1 / SHV1-p | oracle b V0 / SHV1 (gap) | SHV1 at b 0: relR@2 / relP@2 / pixel R |
|---|---|---|---|
| SUPPF | 0.876 / 0.696 / 0.706 | +2.8 / +3.9 (+1.1) | 0.697 / 0.900 / 0.429 |
| HC | 0.889 / 0.819 / 0.836 | +1.8 / +1.3 (−0.5) | 0.823 / 0.897 / 0.606 |
| FINAL (opening readout from calib's records, b_dep 0.75; my self-test reproduces its matched / oracle values) | 0.892 / 0.730 / 0.731 | +1.1 / +1.5 (+0.4) | 0.691 / 0.922 / 0.477 |
- **HC − SUPPF matched SHV1 relR@2 = +0.1233 (kill if < +0.05): mechanism PASSED.** Per seed: SUPPF 0.681 / 0.675 / 0.725 / 0.681 / 0.722; HC 0.812 / 0.808 / 0.818 / 0.837 / 0.818 (seed ranges disjoint). SHV1-p +0.130; V0 +0.014; SHV1 relR@2 at b 0 +0.126.
- The §5 prediction holds in the simulator: the baseline's oracle b is higher on SHV1 than on V0 (+1.1) and HC removes that gap (−0.5).

## Non-E1 harm guard (F51) and _rf readouts
- **F51 crack AP: HC 0.5371 vs SUPPF 0.4702, Δ +0.0669; 36-module bootstrap 95% [+0.0144, +0.0870] (own RNG; opening's [+0.0125, +0.0867]): guard passed** (it fails only if the upper bound < 0). Per seed: SUPPF 0.474 / 0.480 / 0.472 / 0.478 / 0.447; HC 0.552 / 0.495 / 0.565 / 0.565 / 0.509 (every HC seed above every SUPPF seed). F51 crack modules: 6 up / 1 down / 5 missed by both (judge). **The AP gain is not the false-alarm effect** (judge, `judge/out/hc_f51_decomp.txt`): the 12 crack cells alone give +0.060, and swapping in the other arm's crack-free negatives still gives +0.055. On the crack cells HC predicts ~25% more px (pred / GT 0.90 → 1.13 at b 0) with relP@2 unchanged and pixel recall +0.10: extra near-GT coverage; whether the `_rf` labels are wider than the house masks is unmeasured.
- False alarms at each run's val b_rel (crack px on crack-free cells, arm means; b_rel HC +3.0 … +4.3, SUPPF +2.9 … +4.5, similar OPs): **H36 is the robust one:** HC 11 vs SUPPF 278, every HC seed (max 29) below every SUPPF seed (min 144); 4 vs 163 at b 0. **F51 is fragile:** HC 122 vs SUPPF 1,231, but one cell holds 71-96% of each SUPPF run's FA, the median ratio is ×7.6, HC's worst seed (250) is above SUPPF's best (70), and at b 0 the ratio is ×2.5 (judge).

## Reported (protocol_HC §6; never change the verdict)
- **Test inactive leans worse:** per seed SUPPF 0.458 / 0.481 / 0.425 / 0.466 / 0.448, HC 0.438 / 0.430 / 0.444 / 0.442 / 0.410. **n.d.** by the locked /3 rule (thr 0.029). Seed-aware two-stage bootstrap (modules + seeds drawn per arm; judge): [−0.054, +0.005], P(Δ < 0) 0.95. (The paired image bootstrap with the models fixed, [−0.039, −0.012], ignores seed noise.) The drop is broad: 11 of 16 test inactive cells down; leave-top-3-out −0.031. Same sign in every source (ARTS −0.21 on few px, CFVS −0.015, BMRK −0.029, CSIR −0.002).
- **Test crack leans better:** every HC seed's crack IoU (0.4705-0.4797) is above every SUPPF seed's (0.4573-0.4693); **n.d.**: Δ +0.0092 sits 0.0008 under the 0.01 floor. Seed-aware two-stage bootstrap (judge): [−0.002, +0.023], P(Δ > 0) 0.94, the mirror of inactive's P 0.95. Crack recall +0.024, precision −0.008; predicted volume +5% (pred / GT 0.954 → 1.004) with relP@2 flat, so not fattening. Per source (descriptive): ARTS +0.055, CSIR +0.026, BMRK +0.018, CFVS −0.001. Without the 7 D6 twins: crack IoU +0.016 (descriptive subset).
- **B5 (calib's records, coach's curves):** test comp recall at comp P ≥ 0.90, arm-pooled OP: +0.0370 / +0.0374 (thr 0.026), BETTER by rule-1 arithmetic in both sets (HC b_comp 5.3 vs SUPPF 3.9; pre-registered as reported, not a co-primary); per-run OPs +0.020 n.d. relR@2 at relP@2 ≥ 0.90: +0.006 n.d. (pooled and per run). Not a co-primary in protocol_HC (§4 lists 5); reported.
- **E1 strata (reported):** half-cut without scuff (29 cells, 11 GT crack components): recall up with ~27% more predicted volume (pred / GT 0.51 → 0.65; relR@2 +0.075, relP −0.007; E1 GT is ~1.5× wider, so part of the relR@2 gain is width); detection +0.6 components per seed (any-hit 8.2 → 8.8 of 11), n.d. (judge). Full cells (48): relF1@2 +0.040 n.d.; other 77: relF1@2 +0.050 n.d. (relR@2 +0.051); **scuff + half-cut (29): relF1@2 −0.010, inactive −0.053 (n.d.)**; half-cut 58 inactive −0.043 n.d. E1 crack px on E1's crack-free cells (GT crack px 0): HC 3,523 vs SUPPF 3,931 (−10%). E1 overall is not fattening: pred / GT 0.466 → 0.478, any-hit comp recall 0.381 → 0.377; the relF1@2 +0.014 comes from precision (relP@2 +0.029) (judge). E1 B5 (descriptive): n.d.
- 20k encoder cosine vs ImageNet R34: layer3 0.927-0.929, layer4 0.930-0.938 (PF held, as SUPPF).

## Reading (S, with E)
- **Pre-registered outcome: n.d.** HC does not change the house primaries on test or on E1 at 5 v 5. It is not closed by §8's kill rules (no WORSE, mechanism passed). "PASS → next" does not trigger.
- **The simulator mechanism works strongly in-simulator** (SHV1 matched relR@2 +0.12, every seed; the half-cut bias gap gone). The transfer to real half-cuts is what E1 measures, and E1 does not show it: overall relF1@2 +0.014 is n.d. against a 0.043 threshold and comes from precision, not detection; the non-scuff half-cuts gain pixel recall with more volume on only 11 components (+0.6 detected per seed, n.d.), and the scuff + half-cut cells, the larger E1 failure, do not move (scuff is not simulated, §3).
- **The largest non-E1 signals are on `_rf`:** F51 crack AP +0.067 with a module-bootstrap lower bound > 0, carried by the 12 crack cells (extra near-GT coverage), not by fewer false alarms; separately, false alarms on H36's crack-free half-cut cells fall robustly (11 vs 278 px, every seed), while the F51 false-alarm drop is fragile (one cell). The F51 term was a harm guard, so this is reported, not a pass.
- **Test crack and test inactive lean in opposite directions, symmetrically:** crack +0.009 (seed-aware P(Δ > 0) 0.94), inactive −0.023 (seed-aware [−0.054, +0.005], P(Δ < 0) 0.95; 11 / 16 inactive cells down); both n.d. E1 half-cut inactive −0.043 (n.d.). Replacing ~26% of views with synthetic half-cuts appears to cost some inactive recall. Any follow-up must carry a test-inactive guard.
- **Not claimable:** "HC improves E1" or "HC improves test". Claimable (descriptive): mechanism works in-simulator; F51 crack AP better (crack-cell coverage); H36 false alarms lower; test crack and test inactive lean in opposite directions, both under the threshold.

## judge: adversarial check (2026-11-02 03:17 IST; verify_hc as of md5 e619079e; HC post MANIFEST d5c39e0d, md5sum -c OK on the laptop; comparator PF2 post 3827f7c0)
**Verdict n.d. CONFIRMED.** All 5 co-primaries are n.d. in both test sets and on E1; no WORSE. Mechanism PASSED. F51 guard PASSED. Four readings overstate (items 2-5).

Code (own; imports no hc_* / el_metrics / a8_screen_score / coach code; gaint CPU after runner's 'window over' 03:10, nice 19, CUDA hidden; all PIDs exited rc 0):
- `judge/thin_recompute.py` 823bb60e (test two sets + E1 co-primaries + strata);
- `judge/hc_width_check.py` 0e70d44a;
- `judge/hc_gaint_recompute.py` 53d7e0ea (F51 AP + module bootstrap; SHV1 relP / relR from the dumps and SHV1 masks, own EDT-disk code). Smoke-tested before the opening: it reproduces the A8 F51 numbers and the routing pre-check (SUPPF5 0.876 / 0.694, +2.9 / +3.8; FINAL 0.892 / 0.730, +1.1 / +1.5) from calib's dumps;
- `judge/hc_test_inact.py` 7d3fc399, `judge/hc_extra.py` 843806fd, `judge/hc_f51_decomp.py` e06d4795.

Outputs: `judge/out/hc_{coprim,width,f51,shv1,test_inact,extra,f51_decomp}.txt`.

### 1. Recompute (E)
- **Test co-primaries:** crack IoU +0.0092 / +0.0089 (thr 0.0100); relF1@2 +0.0026 / +0.0023; inactive IoU -0.0228 / -0.0230 (thr 0.0289 / 0.0290).
- **E1 co-primaries:** relF1@2 +0.0135 (thr 0.0429); inactive IoU -0.0002 (thr 0.0572).
- **SHV1 matched relR@2:** HC 0.8192 vs SUPPF 0.6959 = **+0.1233** (seed ranges disjoint); bias gap +1.1 -> -0.5.
- **F51 crack AP:** +0.0669, module bootstrap seed 0 [+0.0125, +0.0867]. Seed-aware two-stage: [+0.011, +0.104].
- **FA at b_rel:** H36 10.6 vs 277.8, F51 122.4 vs 1,231.0. My own b_rel (from the val records) equals the scorer's for all 10 runs.
- All equal coach's and the opening's to 4 dp.

### 2. Test inactive: "the image bootstrap excludes 0" holds only with the predictions fixed (E)
- My module-cluster bootstrap (48 test modules, seed-pooled) gives [-0.040, -0.012], as coach's image bootstrap does. Both hold the 5 trained models fixed, so they contain no seed noise.
- **Seed-aware two-stage** (modules + 5 seeds drawn with replacement per arm): **[-0.054, +0.005], P(d* < 0) 0.95.** Once seed noise is in, 0 is not excluded.
- The drop is broad, not a few cells:
  - 11 of 16 inactive cells drop;
  - leave-top-3-out -0.031;
  - HC's 5 seeds (0.410-0.444) are all below the SUPPF mean (0.456).
- **Fix:**
  - Write "leans worse: n.d. by the locked rule; seed-aware bootstrap [-0.054, +0.005], P 0.95; fixed-prediction bootstraps exclude 0".
  - Drop "with the /n divisor (descriptive) it is WORSE": that is an unregistered rule, and it should not appear next to the verdict.

### 3. Test crack (b): n.d. is fair; present it symmetric with inactive (E)
- Every HC seed is above every SUPPF seed, by a 0.0012 margin (0.4705 vs 0.4693).
- Seed-aware two-stage: [-0.002, +0.023], P(d* > 0) 0.94. This is the mirror image of inactive's P 0.95.
- Part of it is volume: test pred/GT 0.954 -> 1.004 (+5%), pixel R +0.024, pixel P -0.008. relP@2 is unchanged (+0.0017), so this is not SKR-type fattening.
- "Per source ... (BETTER)" and "without the 7 D6 twins ... (BETTER)" put rule-1 labels on unregistered subsets. Write the deltas without BETTER. The D6 split marks the largest cracks, not a mechanism (THIN-B3 note).

### 4. E1 strata (c): the half-cut-without-scuff "BETTER" is mostly wider coverage of the same 11 components (E)
- That stratum holds **11 GT components (>= 20 px)**.
- Any-hit components: SUPPF 8 / 10 / 8 / 8 / 7, HC 9 / 9 / 9 / 9 / 8 of 11 (+0.6 per seed). The >= 50% count is 6.8 -> 7.2.
- Prediction volume pred/GT: 0.51 -> 0.65 (+27%; over the rule-1 threshold). relP@2 -0.007.
- E1 crack GT is ~1.5x wider than train (3.66 vs 2.41 px). So relR@2 +0.075 and pixel recall +0.089 there are partly a width effect, as with SKR.
- **Fix:** write "recall up with +27% predicted volume on 11 components; detection +0.6 component per seed (n.d.)", not "BETTER".
- "Scuff + half-cut flat" is right for crack (relF1@2 -0.010). Its inactive leans down (-0.053, n.d.).
- **E1 overall: not fattening.** pred/GT 0.466 -> 0.478; any-hit comp recall 0.381 -> 0.377. The +0.0135 relF1@2 comes from precision: relP@2 +0.029; crack px on the 74 crack-free cells 3,931 -> 3,523.
- **Full 48:** relF1@2 +0.040 n.d. with pred/GT -0.027, also precision-led.
- **E1 inactive** (7 source images, top-3 = 87% of px):
  - CSIR_01637 (4 half-cut scuff cells) -0.056, CSIR_01647 -0.106, CSIR_00400 -0.417, CSIR_01101 +0.171;
  - image-cluster bootstrap [-0.089, +0.078];
  - no half-cut inactive transfer is visible.

### 5. F51 (a, d): the AP gain and the false-alarm drop are two different things, and F51 FA is fragile (E)
- **AP decomposition (1,000-bin):**
  - all 51 cells +0.0669;
  - **the 12 crack cells alone +0.0597**;
  - crack cells plus the *other* arm's crack-free negatives +0.0547.
- So most of the AP gain is better ranking inside the crack cells, not fewer false alarms on crack-free cells.
- **Width on those 12 cells:**
  - pred/GT 0.90 -> 1.13 at b 0 and 1.16 -> 1.44 at b_rel (+25%);
  - pixel R +0.10, pixel P -0.03 / -0.04;
  - relP@2 unchanged (0.876 / 0.880 at b 0), relR@2 +0.03 / +0.04.
- HC marks more crack px, and the extra px are near GT. Whether `_rf` labels are wider than train is not measured. CSIR_00073 holds 76% of the crack px; without its module, d is +0.050.
- The sign count "6 / 12" is really 6 up, 1 down, 5 missed by both arms (module AP = prevalence in every run).
- **H36 FA is robust:**
  - 10.6 vs 277.8 at b_rel; every HC seed (max 29) is below every SUPPF seed (min 144);
  - at b 0: 4 vs 163 px per run.
  - This is the cleanest real-half-cut signal: HC rarely calls the real half-cut gap a crack.
- **F51 FA is fragile:**
  - one cell holds 71-96% of each SUPPF run's FA;
  - median x7.6 (mean x10.1);
  - HC's worst seed (250) is above SUPPF's best (70);
  - at b 0 it is only 114 vs 45 px per run (x2.5).
- **Fix:**
  - Replace "10-25x fewer false alarms on crack-free `_rf` cells" with: "H36 (crack-free real half-cuts) 11 vs 278 px, every seed; F51 crack-free 122 vs 1,231 (mean; one cell dominates each SUPPF run; x2.5 at b 0)".
  - Do not present the AP gain as a false-alarm effect.
  - "Pointing the same way as E1's full-cell relF1@2" is loose: E1's full-cell move is precision-led with no extra volume, while F51's comes with +25% volume. Keep the direction, drop the implied shared mechanism.

### 6. Reading (S)
- n.d. is the right pre-registered outcome. Mechanism and F51 guard pass. HC is not closed by §8.
- What it shows:
  - in the simulator, a large half-cut recall gain;
  - on real `_rf` half-cuts (H36), far fewer false alarms on the gap;
  - on real E1 half-cuts, no co-primary movement (half-cut 58 relF1@2 -0.0002);
  - on test, crack and inactive each lean about 0.02 in opposite directions at P ~0.95 each.
- A follow-up needs the test-inactive guard coach names. On E1 it would need the scuff case, which HC does not simulate.
- What this decides: no change to BEST (SUP100-PF).
