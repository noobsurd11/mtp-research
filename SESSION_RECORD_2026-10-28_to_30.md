# Session record, 28 to 30 Oct 2026: feature learning from the unlabelled pool, and the move to 100% labels

Covers the session after `SESSION_RECORD_2026-10-21_to_27.md`. Status as of 30 Oct 11:54 IST.
Team folder: `team_2026-10-29_features/` (brief `README.md`, append-only `log.md`). Tags: E = measured (file), R = literature (id), S = judgement.

## 0. In one screen
- **The user's question (28 Oct):** does learning features from the ~11.7k unlabelled cells, without labels, improve the model trained on all our labels?
- **What we ran overnight (29 to 30 Oct):** three pool-feature methods, but at **5% labels** (23 cells), not 100%. All verified null or stopped:
  - MIM5 (masked-image pretraining of the encoder): n.d., every estimate negative.
  - AM (MIM reconstruction error as a crack map): killed on val.
  - DDeP5 (denoising pretraining of the decoder): n.d., small positive, below the free logit-adjustment bias.
  - CP5 (crack copy-paste onto pool cells): gates passed, then stopped unscored when the user objected to 5%.
- **The 5% choice was a mistake.** It was copied from the 27 Oct synthesis without checking it against the user's question. An analyst (`diag`) showed that "null at 5% means null at 100%" depends on the method, and fails for label-consuming methods like copy-paste.
- **Biggest finding (coach, E):** the house fine-tune (Adam lr 1e-3, coupled wd 1e-4, 20k steps) erases encoder layer3/4 to cosine ~0 with their starting weights, for ANY init, even at 100%. So every earlier "pretraining / init / backbone does not help" result holds only under this one never-varied optimizer.
- **Now:** `protocol_100` v1 is APPROVED (conditional on gates). It has 4 arms x 5 seeds at 100% labels on gaint, including an encoder-preserving fine-tune (PF). Launch ~12:15 to 12:30 IST 30 Oct; first answer ~01:00 IST 31 Oct.
- **Label work started:** B1 label audit panels delivered to the user; pool mining for half-cut/scuff cells queued; scuff becomes its own class (user decision).

## 1. Timeline
| When (IST) | Event |
|---|---|
| 28 Oct | User asks for a one-paragraph answer. Answer: never run; only label propagation (MT, CPS, BsM, ALHVR, SKCDF) and a frozen ImageNet probe; P15 UCF-EL pretraining was n.d. at 5% and worse at 10%. |
| 29 Oct ~12:30 | User: launch a researcher, an executor and a practical critic; lead only orchestrates. Team `scout` / `runner` / `coach` created from `team_2026-10-29_features/README.md`. |
| 29 Oct 12:38 to 13:30 | scout `directions.md` v1 to v3.1 (ranked CP, DDeP, MIM5, AM). coach reviews; protocols `mim5` v1.1, `ddep5`, `cp5`, `am` APPROVED. Code: gaint worktrees `el_f1` (603e0d5) and `el_f2` (2751aa8). |
| 29 Oct 13:08 | MIM pretraining launched on gaint (gaint is free: the user's q3 jobs finished). |
| 29 Oct 15:40 | DDeP pretraining starts on cv02 (A6000, GPU 1). |
| 29 Oct 18:34 | MIM pretraining done (36,500 steps). |
| 29 Oct ~20:16 | Laptop reboot kills the teammates; runner and coach respawned (scout no longer needed). Server tmux unaffected. |
| 29 Oct 22:42 | DDeP pretraining done (40,000 steps); decoder relayed cv02 → laptop → gaint with md5 on each hop. |
| 30 Oct 02:17 to 02:42 | Last MIM5 run ends; scoring; coach verifies MIM5 (n.d.) and AM (kill). CP decoy gate and DDeP gate PASS. |
| 30 Oct 02:36 | DDeP5 s0/s1 and CP5 s1 start on gaint. |
| 30 Oct 09:45 | coach verifies DDeP5 (n.d.). |
| 30 Oct ~10:45 | User: "why 5%? I asked about adding the pool to 100% labels." CP5 stopped (10:50). Replan at 100%. |
| 30 Oct ~10:25 to 11:10 | coach finds encoder erasure; `diag` analysis; 4-arm `protocol_100` v1 APPROVED with gate G5. |
| 30 Oct 11:12 | User decisions: B1 audit yes; B2 mine only; scuff = own class. |
| 30 Oct 11:37 | B1 panels delivered. `diag` shut down at the user's request. |

## 2. Team, rules, infrastructure
- **Roles:**
  - `scout`: survey (Research MCP).
  - `runner`: code, servers, runs, scoring.
  - `coach`: settings advice, `APPROVED` / `CHANGES`, independent recompute of every primary contrast.
  - `diag` (30 Oct): a one-off analyst.
- **Rule 1 (house):** Δ > max(0.01, 2·sqrt((sdA²+sdB²)/3)), divisor 3 even at 5 v 5 (the README first said /n; corrected). Better on one primary, worse on none. Primaries: test crack IoU, crack relF1@2, inactive IoU, on all 50 cells and on 49 without `CSIR_00070_r8_c4`.
- **gaint:**
  - One RTX PRO 4500, 32.6 GB.
  - Root's `finllm_chat.py` (5.9 GB) must never OOM, so at least 2 GB is kept free at all times.
  - Start gate per run: own measured peak + 2 GB. CP runs need 9.5 GB, fine-tunes 6.8 GB.
- **cv02:** shared account, no keys, no `ssh -A`. All 8 GPUs held by other users for the whole session except the DDeP slot.
- **Data note (E):** gaint `data/escdd_masks/test` differs from cv02 at 2 cells (scuff class 25 vs crack 14). All scoring uses `labeled/masks_escdd` (cv02-identical).

## 3. Overnight 5% experiments (all vs A5c-f1 on gaint, 5 v 5, final-step weights)
Baseline reproducibility: A5c-f1 test crack IoU 0.300 vs 0.304 for the original A5c on cv02.

### 3.1 MIM pretraining (E, `protocol_mim5.md` v1.1, log 13:07 to 18:39)
- **Pool:** 11,690 cells (list md5 f0a5d74a), plus 256 held-out monitor cells.
  - Excluded: val/test/E1 modules (413), 11 ext117 stems, 50 near-duplicates (r ≥ 0.95; coach's first 0.85 would have dropped 624 ARTS cells), the 7 D7 twins.
- **Recipe:** SparK-style sparse MIM of the ImageNet ResNet-34 U-Net++ encoder.
  - Mask 0.6, 32 px patches at 512 px, masked-only normalised-pixel L2.
  - Batch 32, 36,500 steps, encoder warm-up 730 then a lr ramp.
- **Result:** monitor loss 0.914 → 0.208 (flat from ~26k). `encoder_final` md5 1c3df959.

### 3.2 MIM5 verdict (E, `verify_mim5.md`): n.d., closed
| Test (A5c-f1 → MIM5) | Crack IoU | Crack relF1@2 | Inactive IoU |
|---|---|---|---|
| all 50 | 0.300 → 0.289 (−0.012, thr 0.019) | 0.714 → 0.700 (−0.014, thr 0.030) | 0.279 → 0.230 (−0.050, thr 0.116) |
| without CSIR_00070 | −0.012 (0.019) | −0.014 (0.030) | −0.051 (0.120) |
- **Spread:** MIM5 seed sd is 3x A5c-f1's on crack (0.015 vs 0.005) and 2.4x on inactive. Only 1 of 5 MIM seeds is above the A5c-f1 mean.
- **LA-matched (τ 1):** crack 0.316 → 0.305, n.d.
- **E1 crack recall (descriptive):** 0.047 → 0.036.
- **Cross-check:** runner's own analysis matches coach's to 4 decimals.

### 3.3 AM, MIM reconstruction error as a crack-recall aid (E, val only): killed
- **Ranking:** map AP 0.017, 6.2x the crack base rate (0.0027).
- **Kill:** no threshold reaches relaxed precision 0.5, so 0 missed components are recovered (A5c-f1 misses 67 to 71 per run, SUP100 20 to 27).

### 3.4 DDeP pretraining and DDeP5 (E, `verify_ddep5.md`): n.d., closed
- **Pretraining:** cv02, 40,000 steps; encoder frozen, BN in train mode; ε-prediction, γ 0.95.
  - Monitor ε-MSE 1.046 → 0.0465.
  - `decoder_final` md5 dd786ff4, identical on cv02 and gaint.

| Test (A5c-f1 → DDeP5) | Crack IoU | Crack relF1@2 | Inactive IoU |
|---|---|---|---|
| all 50 | 0.300 → 0.307 (+0.007, thr 0.010) | 0.714 → 0.722 (+0.009, thr 0.017) | 0.279 → 0.287 (+0.008, thr 0.059) |
| without CSIR_00070 | +0.007 (0.010) | +0.009 (0.017) | +0.008 (0.061) |
- **Mechanism:** mostly a crack threshold shift (recall +0.019, precision −0.022).
  - With LA on both arms: +0.0045, n.d.
  - DDeP5 vs A5c-f1+LA: −0.009, i.e. below the free bias.
- **E1:** crack recall unchanged at 0.047.
- **Decoder change:** final decoder cosine to the pretrained init is 0.090, against 0.066 to 0.072 for unrelated inits; weights shrink to ~1/4 of init. Fine-tuning overwrote the pretraining, as the protocol predicted.
- **Disclosed:** the el_f2 `REVISION` file was written after the runs; it matches the checked-out commit.

### 3.5 CP5, crack copy-paste at 5% (E): gates passed, stopped unscored
- **Library:** 20 components (11,978 px; CFVS 13, CSIR 4, BMRK 2, ARTS 1).
- **Decoy gate at 2k: PASS.** Crack called on decoy spots 0.0049 for CP vs 0.0076 for A5c (the flag was > 2x or > 0.05). On real pastes, 0.2125 → 0.2334. 245 of 256 cells (11 skipped symmetrically).
- **Stopped:** s1 and s3 finished. s0 (11,800 steps) and s4 (12,350) were stopped at 10:50 IST 30 Oct; s2 cancelled. Not scored, no test opened.

### 3.6 Test openings so far
2 (MIM5, DDeP5). CP5's automatic per-run rescore files for s1/s3 exist, unopened.

## 4. Key finding: the house fine-tune erases the deep encoder (coach, E; runner re-derived to 3 decimals; `coach_100.md` §0)
Cosine of final vs initial conv weights:
| Encoder stage | A5c-f1 (5%) | MIM5 (vs MIM init) | SUP100 (100%) |
|---|---|---|---|
| conv1 | 0.98 | 0.98 | 0.96 to 0.99 |
| layer1 | 0.38 | 0.33 | 0.40 |
| layer2 | 0.14 | 0.14 | 0.15 |
| layer3 | 0.01 | 0.005 | 0.02 |
| layer4 | 0.00 | 0.00 | 0.00 |
- **Seeds and norms:** two SUP100 seeds are unrelated at layer4 (cosine 0.007). layer3/4 norms end at 2 to 9% of init.
- **Why MIM5 was null:** MIM changed mostly layer2 to layer4 (cosine to ImageNet 0.53 to 0.76), exactly what fine-tuning wipes. That explains MIM5's null.
- **The optimizer was never varied** in R1 to R5 or the P series. So every "init / pretraining / backbone does not matter" result is conditional on this recipe.
- **Likely cause (S):** coupled weight decay on BN-followed convs shrinks the weights, and their direction then drifts.

## 5. Why 5% was wrong, and `diag`'s analysis (`diag_5pct_to_100pct.md`)
- **The user's point:** a 5% null need not carry to 100%; it depends on the method. At 5% the defect classes are too scarce.
- **Power (E):** 100% is better powered, not worse. 80%-power MDE: crack IoU 0.012 at 100% vs 0.019 at 5%; inactive 0.032 vs 0.084. Only 2 training cells have inactive at 5%, so the 5% inactive nulls say nothing.

| Method | Does "null at 5% ⇒ null at 100%" hold? | Main reason |
|---|---|---|
| Copy-paste | No: 5% is the wrong test | Its dose is labels: the library grows from ~20 to ~560 components. Positive at every COCO fraction (R doi:10.1109/cvpr46437.2021.00294). |
| DDeP decoder init | Holds (strong) | The paper's gain falls to +0.3 to +1.3 at full labels (R arxiv:2205.11423), and our fine-tune overwrote the decoder |
| MIM encoder init | Holds only for the house recipe; unknown under an encoder-preserving fine-tune | MIM5 only tested conv1/layer1 transfer, because layer2 to layer4 were erased (addendum after §4) |
| Pseudo-label SSL | Holds for gains; fails for scarcity artefacts | BsM crack +0.029 / +0.012 / −0.006 at 5/10/20%; joint-BN MT n.d. at 5% but passed at 10% (a handicap that grows as labels shrink) |
- **Rule (S):** "null at 5% ⇒ null at 100%" is safe only if two things hold. The method does not consume labels, and the 5% estimate is tight.
- **Saved as feedback memory:** pool ideas are tested on top of 100% labels unless the user asks otherwise.

## 6. In general: SSL gain falling as labels rise (answer given to the user)
- **Gain shrinks to zero:** normal. The pool stood in for missing labels, and labels now supply that information.
- **Gain turns negative:** the unlabelled signal fights the labels. Usual causes:
  - pseudo-labels noisier than real labels (rare classes hit first);
  - the unlabelled loss weight, tuned at low labels, now dominates;
  - labelled cells see fewer passes in the same steps;
  - joint BN statistics;
  - pool vs test domain mismatch;
  - pretraining erased by the fine-tune.
- **Diagnosis, in order:**
  1. Confirm it beats seed noise (rule 1, MDE ~0.012 crack at 100%).
  2. Run the SSL pipeline with the unlabelled loss at 0. If that alone loses, the pipeline is the cause, not the pool.
  3. Sweep the unlabelled loss weight at 100% on val.
  4. Score the pseudo-labels against real labels on val, per class.
  5. Compare with a matched crack bias (LA) to separate threshold shift from better features.
  6. Break down per class and per source (domain mismatch).
  7. For pretraining, check the weight cosine to init.

## 7. The 100% plan (`protocol_100.md` v1 md5 200a6734, `review_100_v1.md`, `coach_100.md`)
- **Setup:** all 478 train labels, 20k steps, 5 seeds per arm, all on gaint. Deploy commit `el_f3` e544133 (suite 285 passed).

| Arm | Change |
|---|---|
| SUP100-g | fresh baseline on gaint (cv02 seeds are other hardware and commits) |
| SUP100-PF | encoder-preserving fine-tune: encoder lr 0 for 1k steps, ramp to 0.1x over 1k, encoder wd 0 |
| MIM100-PF | PF from `encoder_final` (1c3df959) |
| CP100 | house optimizer, copy-paste from all train cracks onto pool backgrounds |

- **Contrasts:**
  - pool via the encoder: MIM100-PF vs SUP100-PF;
  - recipe: SUP100-PF vs SUP100-g;
  - pool via copy-paste: CP100 vs SUP100-g (also with matched LA).
  - Rule 1 /3, both verdict sets.
  - A winner's 5-seed ensemble (crack bias chosen on val) is compared with its same-machine comparator ensemble. FINAL 0.492 is descriptive.
- **Expected:**
  - MIM100-PF: unknown.
  - CP100: crack IoU +0.005 to +0.015 against MDE 0.012 (coin flip); likelier on relR@2 / component recall.
  - SUP100-PF: the likeliest to move FINAL (S).
  - DDeP at 100% dropped.
- **CP100 library:**
  - 591 components from all train cells (vs 20 at 5%).
  - Excluded: 13 stems (list md5 903293c9), the 7 D7 twins (their cracks are test cracks) and the 6 cells whose E-SCDD scuff is labelled crack.
  - With the twins out, 566 components / 151,993 px (CFVS 302, CSIR 175, ARTS 68, BMRK 21; thin BMRK disclosed).
  - Backgrounds pool-only. cp.batch 4 (labelled stream 4,549 crack px/step, under the 12k trigger).
- **Gates before launch:**
  - identity at e544133 (no switch, PF-neutral, CP λ 0);
  - val-off bit-identity;
  - **G5:** PF smoke to 4k with layer3/4 cosine ≥ 0.8 in both PF arms (fallback encoder lr 0.03x, then stop);
  - MIM encoder md5;
  - CP decoy check;
  - memory per run.
- **Speed-ups:**
  - bf16 is already on everywhere;
  - val only at start/end if bit-identical (~5 to 10%);
  - a 4th lane via `expandable_segments` if a fine-tune fits in 5.5 GB.
  - No TF32 / channels_last / compile, because they would sit under the optimizer contrast.
- **Order and timing:**
  - Seed-matched waves of the three fine-tune arms first, then CP100 two at a time. ~19 h.
  - Opening 1: the 15 fine-tunes, scored together ~01:00 IST 31 Oct.
  - Opening 2: CP100 ~07:30 IST 31 Oct, reusing SUP100-g's opening-1 files unchanged (md5-checked).
  - CP100 runs to the end whatever opening 1 shows; no protocol change after opening 1.
- **Status 11:54 IST:** smokes and the G5 extension running; gate table ~12:05 to 12:10, then v1.1, coach re-check, launch.

## 8. Using the pool to choose labels (`coach_strategy.md`)
coach's diagnosis: labels dominate. Label revision gave +0.08 crack; 50 → 100% gave +0.026; every pool method has been null from 20% up. The E1 misses are context: half-cut and scuff cells, plus BMRK.

### B1 label audit (done; `b1_audit/`, MANIFEST 10 files md5 OK)
- **Auditors:** the five 50%-label models (house recipe, current masks) on the 239 train cells each never saw.
  - The old 20%-label models are a secondary column only (legacy recipe, old `masks_coded` labels).
- **Flag rule:** all 5 confident against GT. Missed-label regions ≥ 20 px crack / 200 px inactive; false-label regions all 5 miss. Frame/padding, scuff/star and 2 to 3 px edge jitter are never flagged.
- **Results (E):**
  - crack flags in 24 cells = 10.0 per 100 (false-label 15, missed-label 10);
  - inactive in 9 cells = 3.8 per 100.
  - Val base rate: crack false-label 16.7 per 100. So train is not flagged above a reviewed set, and many flags will be hard real cracks.
  - The uncovered half probably holds ~24 more crack cells and ~9 inactive.
- **Sheets sent to the user:**
  - `b1_sheet1_crack_top30.png` (24 panels);
  - `b1_sheet2_inactive_top10.png` (9);
  - `b1_sheet3_S_train.png` (15 scuff/star cells).
  - Mark each: label error / true hard case / unsure. No mask changes until then; fixes go to a new mask version with a change list.

### Scuff label facts (E, raw E-SCDD vs `masks_escdd`)
- **Train:** 12 cells carry scuff (3,246 px). In our masks: background 1,207, material 1,390, **crack 649 in 6 cells**.
  - The 5% "ARTS crack cell" `ARTS_00051_r6_c2` is scuff labelled crack.
- **Test:** 2 cells, 236 scuff px, labelled crack (`ARTS_00047_r3_c1`, `ARTS_00051_r3_c2`). Val: none. E1: scuff is in the ignore masks.
- **Star:** `CFVS_00024_r3_c3` has 54 px of E-SCDD "star" labelled crack. It is kept in the CP100 library (meaning undefined, 0.04% of library px) and stays on the review list.

### B2 pool mining (queued after launch; user: candidates only, labelling decided later)
- **Candidates:** 100 pool cells (70 half-cut, 30 full; at most 3 per module, at most 40 per source).
- **Ranking:** predicted crack, largest component, dark-streak count.
- **Check:** the ranking should recover the 12 known scuff cells.
- **Output:** contact sheets for the user.

### B3 scuff as its own class (user decision; `spec_b3_scuff.md`)
- **Design:** 25 classes, with predicted scuff mapped to background for the 24-class metrics. BEST vs BEST+S, 5 v 5, after protocol_100 on the winning recipe.
- **Labels:** none new needed for v0; the 12 cells come from the raw masks.
- **Expected (S):**
  - test primaries n.d.;
  - E1 crack-on-scuff false alarms −20 to −60%;
  - E1 crack precision +0.01 to +0.04.
  - With 20 to 40 mined cells labelled, E1 scuff-group recall +0.03 to +0.12.
- **Open user decision (§4 of the spec):** (a) keep test GT for the verdict (coach's recommendation, for comparability), (b) report a test version with the 236 px ignored, descriptive. Test masks untouched.

### Other ranked items (coach_strategy)
- **C:** a thin-structure crack loss (Skeleton Recall, R doi:10.1007/978-3-031-72980-5_13) at 100% on the best recipe, for relR@2 ≥ 0.90.
- **D:** inference-only E1 checks (BN re-estimation on pool cells, an RN50 ensemble member).
- **If PF wins:** RN50 / ConvNeXt under PF, and a PF seed soup.
- **Stop:** more pool representation learning, and 5% screens of label-consuming methods.

## 9. Operational incidents and fixes
- **Rule-1 divisor:** the brief said /n; corrected to the house /3 before any verdict.
- **gaint memory:** 0.8 GB headroom at one point; ordered ≥ 2 GB free at all times.
  - **Start race:** three f2 runs started on one free reading (02:36). A 5 s memory watch over vals and checkpoints showed a constant 2,232 MiB free, so all were kept. Starts now take a lock and are spaced 120 s apart.
  - **CP gate:** lowered from 12,000 to 11,600 MiB from the measured peak, so no slot sat idle.
- **Gate parse bug (cv02):** a good DDeP smoke was marked FAIL (the grep matched the STOPPED line) and the GPU was lost; fixed.
- **HOLD file:** a shared HOLD blocked the MIM5 lanes; replaced by an A-lane-only HOLD_A.
- **Laptop reboot (20:16 IST 29 Oct):** teammates respawned; tmux socket `claude-swarm-8262`.
- **Critical-path slip:** the A lane ran its seeds serially; rebalanced with an extra window (last run 05:00 → 02:21).
- **Log-path bug:** `f1_after_runs_gaint.sh` wrote its last lines to a relative path, so the DDeP5/CP5 release line never appeared. Written by hand (AM output verified complete); script fixed.
- **`rc=$?` after `$(date)` bug:** five status lines recorded `date`'s exit code (MIM pretrain, MIM5 post, DDeP5 post, cv02 DDeP, f100 smoke status).
  - Training-run rc lines (run_one.sh, all versions) were correct.
  - Each affected run was confirmed complete by its DONE line, md5 manifests and 0 Tracebacks. Verdicts unaffected.
- **Timestamps:** coach (up to ~1 h) and runner (up to 38 min) had stamped some log lines ahead of the clock. Corrected; coach marked its estimates with "~" and kept a pre-edit copy.
- **ARTS footnote (commit 882f929):** ARTS has 1 small labelled crack cell at 5%, not 0. It later turned out to be scuff labelled crack (§8).

## 10. Open decisions for the user
1. **B1:** review the three panel sheets.
2. **B2:** after the candidate sheets, whether to pixel-label 20 to 40 cells.
3. **Scuff test GT:** (a) keep it for the verdict (recommended) or (b) also report it ignored, descriptively.
4. **Still open from 27 Oct:**
   - the ELPV download;
   - the 40-segment crack audit and 4 label-convention questions;
   - closing the idle cv02 tmux shells;
   - the handbook refresh (Track D/M, 27 Oct, and now this session: encoder erasure, MIM5/DDeP5 nulls, the 5% lesson).

## 11. Files
- **Brief and log:** `team_2026-10-29_features/README.md`, `log.md`.
- **Research and specs:** `directions.md`, `spec_cp5.md`, `spec_b3_scuff.md`, `coach_strategy.md`, `diag_5pct_to_100pct.md`.
- **Protocols:**
  - `protocol_mim5.md` (v1.1 md5 70d65d2b), `protocol_ddep5.md`, `protocol_cp5.md`, `protocol_am.md`;
  - `protocol_100.md` (v1 200a6734; v0 kept).
- **Reviews:** `review_mim5_v0/v1.md`, `review_ddep5_cp5_v0.md`, `review_spec_cp5_v1.md`, `review_100_v1.md`, `coach_mim5.md`, `coach_100.md`.
- **Verifications:** `verify_mim5.md`, `verify_ddep5.md`, `identity_f1.txt`.
- **Results:** `results/{mim5,ddep5,cp5}/`.
  - Per-cell raw JSONs (~240 MB) are kept locally and on gaint, with `MANIFEST.md5`. They are not in git.
- **Audit and scripts:** `b1_audit/`, `scripts/`.
- **Servers:**
  - gaint worktrees `el_f1` (603e0d5), `el_f2` (2751aa8), `el_f3` (e544133);
  - DDeP pretraining backup at `cv02_noob_el/el_f2/experiments/f2_ddep_pre_s0/`.
