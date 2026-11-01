# Protocol PF2E: SUP100-PF vs SUP100-g as deployable 5-member ensembles (inference only, gaint)

coach, 1 Nov 2026, **v1 LOCKED (2026-11-01 14:28 IST)**; v0 earlier the same day. User's go 1 Nov ~13:15 (team-lead), with E1 co-primaries. Pre-registered as PF2's follow-up (`protocol_PF2.md` §6). No training. Launch on coach's APPROVED after §6's build. Tags: E / S.

## 0. What I had seen (E)
- PF2's opening (`verify_pf2.md`): single-model verdicts, per-cell files of all 15 runs (test, val, E1). No ensemble number of seeds 5-9 exists.
- FINAL (cv02, R34 5-seed ensemble, +0.75): clean-test crack IoU 0.492 (Track M), E1 curves seen.

## 1. Question
Is the PF recipe also better as the deployable object, a 5-member mean-softmax ensemble with its crack bias chosen on val, than the house recipe built the same way?
- **Contrast:** E-PF (pf2_SUPPF_100pct_s5..9) − E-g (pf2_SUP_100pct_s5..9), same machine and commit (gaint, e544133), final weights, mean softmax, TTA off.
- Reported, descriptive: E-PF vs FINAL (different machine and commits); E-PF vs the PF2 single-seed means.

## 2. Operating point (val only, fixed rule, before any test inference)
- FINAL's rule D2 (Track M `protocol_final.md` step 2), per ensemble: grid b ∈ {0, 0.25, …, 3}; the smallest b with val relR@2 ≥ 0.90 and val relP@2 ≥ 0.90, else the b with max val relF1@2; headline b = 0 if the chosen b trips the width flag on val (crack precision drop > 0.05).
- Both b = 0 and the chosen b are reported; the verdict uses the chosen b. Decisions written to a file before any test or E1 inference.
- **Clarification (coach, 2026-11-01 19:04:56 IST; judge flag; written while `el_f3/reports/pf2e/out/` was EMPTY at 19:04:45, i.e. before `pf2e_val_decisions.json` existed and before any PF2E val / test / E1 number was read): "the chosen b" in the verdict sentence means each ensemble's **headline b** (= its D2-chosen b, or 0 if that b trips the val width flag, crack precision drop > 0.05), i.e. the deployable operating point, as Track M's FINAL D2 and as the approved scorer `pf2e_boot.py` bee9e182 ("VERDICT (headline b)"). b = 0 and the D2-chosen b (if different) are reported.**

## 3. Verdict (Track M contrast rule, paired image bootstrap)
- Test primaries: crack IoU, crack relF1@2, inactive IoU; sets all 50 and clean (without CSIR_00070_r8_c4).
- Paired image bootstrap, 2,000 resamples, seed 0. **Pass** if the 95% CI excludes 0 on ≥ 1 primary in both sets, or in one set with a same-sign estimate in the other; **fail** if any primary's CI lies wholly below 0 in either set.
- **E1 co-primaries (user, 1 Nov; second test set, read once here):** **E1 crack relF1@2 and E1 inactive IoU** (all 106), paired **module-cluster** bootstrap (2,000, seed 0): cluster = the stem without its cell suffix (`_rN_cM` / `_cellN`), i.e. the source image: **71 clusters** (CSIR 66 images for 101 cells, BMRK 5). Pass / fail wording as for test (one set).
- Multiplicity: 1 contrast × 3 (+2) primaries × 2 sets; a counted test opening, and **E1 opening #4** in `e1_openings.md`.

## 4. Reported
Four cell sets; per source; crack capture (relR@2, relP@2, component R / P); B5 operating points (frozen el_metrics, ensemble OP by the same val rule); cell-level; scuff-ignored test; E1 strata and width checks; crack px on crack-free cells; LA tau 1 not applicable (bias chosen on val); FINAL 0.492 descriptive.

## 5. Expectations (S)
- Test: relF1@2 +0.005 to +0.015 (singles +0.012); crack IoU ±0.01; inactive +0.00 to +0.03. A pass is possible on relF1@2; the CI is likely to touch 0 (single-seed bootstrap P 0.93).
- E1: inactive IoU +0.15 to +0.20 (singles +0.19); crack relF1@2 +0.02 to +0.05.

## 6. Build and cost
- **Device:** gaint **CPU fp32** for both ensembles (nice 19, ≤ 8 threads): it needs no GPU slot beside THIN-B3, and both arms are scored identically (the single-model PF2 numbers were GPU bf16; differences ~0.0005, D's cross-check). A val gate first: E-g and E-PF member s5 alone on CPU vs its PF2-opening m0 JSON, |Δ| ≤ 0.005 on val crack IoU and relF1@2, else stop before any test / E1 cell.
- Inference script (runner): mean-softmax ensemble of 5 final checkpoints, val first (b chosen and frozen to file), then test + E1; scorers as the opening (rescore conventions, m0 per-cell format); bootstrap by `per_image_analysis.py` (Track M) or coach's `coach_verify.py` with a cluster option; md5s frozen before running.
- Cost: 10 models × (54 + 50 + 106) cells: ~15-30 min GPU at the scoring gate or ~1 h CPU. No training.

## 7. Build record and APPROVED (coach, 2026-11-01 18:56 IST; verified on gaint and locally)
- Build: `build_pf2e.md` (runner, md5 d1977468). gaint `el_f3/reports/pf2e/`: `pf2e_infer.py` **272463d3** (= local), `pf2e_run.sh` **9df7d9a7** (= local; CPU fp32, nice 19, 8 threads, CUDA hidden, rc before date); local scorer `scripts/pf2e/pf2e_boot.py` **bee9e182** (Track M m1_analyze 8e566254, m0_analyze d5adbe6b, m_common 10f0d37c asserted).
- Checked by coach: D2 rule = Track M m9_final.py l.133-139; stats = m9_final.score; data paths = m9_final; decisions file before any test / E1 read; second-pass refusal; gate s5-alone |Δ| ≤ 0.005. **Gate dry check (val only, 18:50:57-18:54:34, rc 0):** E-g s5 crack IoU +0.0001, relF1 −0.0004; E-PF s5 +0.0004 / +0.0004 (`out_gate/pf2e_gate.txt`). **Bootstrap self-test re-run by coach locally: PASS** (singleton clusters == m1_analyze.boot exactly; 2-cell duplicate clusters == boot; E1 106 stems → 71 clusters); identical arms (E1 SUP s5 vs itself) → full / lo / hi all 0.
- **B5 + cell-level (§4, reported) ruling:** a frozen extra pass after the verdict files exist and are pulled: calib's frozen `calib_dump.py` c172717e with `--group E-g <5 runs> --group E-PF <5 runs>` (mean softmax, as its docstring), `--device cpu`, `--sets val ext test --opening protocol_PF2E`; frozen `el_metrics.py` 6e73ff11 records with the b = 0 self-check against PF2E's own `E-*.b0.json` (both CPU fp32; tol exact, the cpu profile only if exact fails, disclosed); summary per ensemble with its val-chosen OPs. Reported only; same E1 opening #4. Runner sends the wrapper + md5s for a short review before it runs.
- **APPROVED for launch (coach):** `bash pf2e_run.sh full` once (it repeats the gate first), tmux with recorded PID, not inside THIN's opening window if runner declares one (CPU job rules); E1 opening #4 logged in `e1_openings.md` at start; pull with MANIFEST; coach recomputes the verdict with own bootstrap code from the per-cell JSONs.
