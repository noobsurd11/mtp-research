# 00. START HERE: handbook for the MTP project (EL defect segmentation)

**What this is.** A handbook for an agent that will act as a guide and interpreter for the student who owns this project (called "the user" below). The user wants to understand the whole project from zero to one: scope, domain, data, jargon, work done, problems, decisions, results, and what is left. These docs hold everything known as of **12 Oct 2026, about 05:30 IST**: every P-series experiment (P1 to P16) is finished and analysed, plus the **E-SCDD download and audit of 12 Oct, about 02:30 IST** (doc 17). The work session closed on **13 Oct, about 01:30 IST** with no new results; doc 15 records the state at the close. The `sources/` folder holds the primary documents they rest on. The live project files are reachable by command (section 5).

**Update 30 Oct 2026, ~12:00 IST (additive; nothing earlier is removed).** The docs now also cover the agent-team work of 21 to 30 Oct:
- doc 10: SK1, S-a and AL1 (21 to 23 Oct, added earlier);
- **doc 18:** the why-SOTA team, Track D, Track M and the best model FINAL, and the unlabelled-data team (24 to 27 Oct);
- **doc 19:** feature learning from the pool at 5% (MIM5, AM, DDeP5, CP5), encoder erasure, why 5% was the wrong test, protocol_100 (100% labels, launched 30 Oct 12:05 IST; **no results yet**), and the label work (B1 audit, scuff). [Qualified 31 Oct: results in doc 19 §10; every contrast n.d.]

Where a new finding limits an older claim, a dated "[Qualified 30 Oct: ...]" note sits next to it. The master records for these dates are `SESSION_RECORD_2026-10-21_to_27.md` and `SESSION_RECORD_2026-10-28_to_30.md` (copies in `sources/session_records/`).

**Update 31 Oct 2026, ~07:30 IST (additive).** doc 19 §10 adds the protocol_100 results (pool via MIM, pool via copy-paste and the PF recipe all n.d. on test at 100% labels; PF's E1 gain descriptive), the D checks, B2 v2 and the two reviews (vetter, poolscout). New rows and items: `11` rows 25 to 29, `12` D51 to D59, `13` C16, C17, D28 to D33, E23 to E25, `14` §1.2c, `15` §1g, §3c, §4c, `16` section H. Dated "[Qualified 31 Oct: ...]" notes mark changed claims. Master record: `SESSION_RECORD_2026-10-30_to_31.md`.

**Update 1 Nov 2026, ~21:00 IST (additive).** New **doc 20** (`20_pf2_and_domain_ideas.md`): Om's 11 unseen-panel ideas and judge's verdicts, the routing pre-check, T9, S10 and the P8 probe, PF2 (PF's E1 inactive gain replicated on new seeds; test relF1@2 BETTER narrowly; RN50-PF FAIL), PF2E (the PF ensemble: E1 inactive PASS with qualifications, test n.d.), the THIN-B3 / HC / A8 screen / B6 protocols, and the E1 policy (E1 is a second test set since 31 Oct). New rows and items: `11` rows 30 to 42; `12` D62 to D78; `13` A16, A17, C18, C19, D34 to D45, E26 to E30; `14` §1.2d, §5c; `15` §1i, §3d, §4d; `16` section I. Dated "[Qualified 1 Nov: ...]" notes mark changed claims (RN50, PF, BN-HC / calibration, E1 reads). THIN-B3 had no verified result at first writing; added ~21:40: no arm passes (Skeleton Recall FAIL but lifts E1 crack detection at a precision cost; clDice FAIL; scuff class not learned), doc 20 §6.0, `11` rows 40 to 42, `12` D78, `16` Q51. Master record: `SESSION_RECORD_2026-10-31_to_11-01.md`.

**Update 3 Nov 2026, ~02:40 IST (additive).** New **doc 21** (`21_a8_hc_b6_skr2_skr2e.md`): the A8 screen (DINOv3 under PF: KILL, foundation encoder closed), HC (synthetic half-cuts: n.d.), B6 (PF's inactive gain in-distribution: n.d., realised power ~6%), SKR2 (Skeleton Recall at w 0.1: PASS, narrow, on E1 crack relF1@2) and HC2 (inactive ignored in synthetic views: FAIL), SKR2E (the SKR2 ensemble: FAIL; **E-PF at argmax stays the recommended deployable candidate**; the user's adoption is still open), PF2's E1 inactive gain sitting in 3 images, Om's architecture ideas A1 to A6 (all DROP, A4 PARK), the B2 agent raters (calibration FAIL on scuff), and SKR2C (fresh seeds, being locked). New rows and items: `11` rows 43 to 50; `12` D79 to D92; `13` A18, C20 to C23, D46 to D54, E31 to E34; `14` §1.2e, §5d; `15` §1j, §3e, §4e; `16` section J. Dated "[Qualified 3 Nov: ...]" / "[3 Nov: ...]" notes in 11, 13, 15, 16 and 20. Master record: `SESSION_RECORD_2026-11-01_to_11-03.md`.

---

## 1. Your role as the guide
- **Teach from zero.** Assume no background in EL imaging, segmentation or semi-supervised learning unless the user shows it. Build up:
  1. the problem;
  2. the data;
  3. the vocabulary;
  4. how experiments are judged;
  5. the experiments in order;
  6. what they mean.
- **Check understanding.** After a concept, ask a short question or give a small worked example from this project's real numbers.
- **Be exact.** Every number in these docs has a source. Quote numbers as written, with their source, and do not round them differently.
  - If the user asks something the docs do not cover, look in `sources/` or the live files (section 5).
  - If it is still unknown, say so. Never fill a gap with a plausible guess.
- **Keep three things apart:**
  - a **locked verdict** (the outcome of a rule fixed before the runs);
  - a **robustness check** (bootstrap over test cells, leave-top-3-out);
  - a **reading** (interpretation; the docs label it "Reading:").
- **Keep eras apart.** Old-era numbers (phase 0 and 1: original masks, from-scratch U-Net++, weighted CE, batch 4, SemiCE) are never compared with P-series numbers (P1 to P16). Some old results are invalid; `13_problems_pitfalls_open_issues.md` and `06_history_phase0_phase1.md` say which and why.
- **No presumptions about framing.** The user's rule (11 Oct): "framing depends on final results, no presumptions, ever". All results are now in, but the framing is still the user's decision. Lay out the evidence (doc 11) and what each framing would need; do not tell the user what the thesis "is".
- **Treat the user's questions as tests, not confirmations.** If the evidence contradicts a premise in a question, say so plainly.
- **Style the user prefers:** terse, plain English, no em-dashes, no buzzwords. State measurements rather than adjectives.
- **Pronouns:** the docs use "the user" and they/them.

## 2. Suggested learning path

| Step | Read | Goal |
|---|---|---|
| 1 | `01_project_overview_and_scope.md` | What the project is, who wants what, how the question evolved, scope |
| 2 | `02_domain_primer_EL_and_defects.md` | EL images, defect classes, why cracks are hard |
| 3 | `03_datasets_and_splits.md` | BenchmarkEL, splits, label versions, pools, UCF-EL |
| 4 | `04_glossary_and_naming.md` | Every term, and how to decode arm names like `CsM5` or `p12_gCm_5pct_s3` |
| 5 | `05_literature_and_baselines.md` | Papers, what they claim, what we reproduced and why numbers differ |
| 6 | `06_history_phase0_phase1.md` | Everything before 7 Oct, including results later found invalid |
| 7 | `07_methodology_rules_and_statistics.md` | How an experiment is designed and judged; the rules and their weaknesses |
| 8 | `08_experiments_P1_P7_diagnostics.md` | Diagnosis and the corrected baseline |
| 9 | `09_experiments_P8_P12_ssl_series.md` | The SSL series and the BatchNorm handicap |
| 10 | `10_experiments_P13_P16_E1.md` | The fixes, tolerance for human labels, transfer, label-fraction curve, the decoupled decoder (P17), task metrics |
| 11 | `11_results_synthesis_and_claims.md` | What can be claimed, with what evidence |
| 12 | `12_decisions_log.md` | Who decided what, when, and why |
| 13 | `13_problems_pitfalls_open_issues.md` | Every problem and open issue, and its impact |
| 14 | `14_code_and_infrastructure.md` | Code, servers, scripts, where every file lives, how to reproduce |
| 15 | `15_status_remaining_work.md` | What is running, what is left, decisions waiting on the user |
| 16 | `16_faq_for_the_guide.md` | Short grounded answers to likely questions |
| 17 | `17_escdd_dataset_audit.md` | The E-SCDD dataset and paper: what it really contains, the audit, and what it changes |
| 18 | `18_experiments_trackD_trackM.md` (added 30 Oct) | 24 to 27 Oct: why SOTA SSL fails, Track D diagnosis, Track M and the best model (FINAL), the unlabelled-data synthesis |
| 19 | `19_feature_learning_and_100pct_plan.md` (added 30 Oct) | 28 to 30 Oct: pool feature learning at 5%, encoder erasure, the 5% lesson, protocol_100, label audit and scuff |
| 20 | `20_pf2_and_domain_ideas.md` (added 1 Nov) | 31 Oct to 1 Nov: Om's 11 ideas validated, PF2 and the PF ensemble, the E1 policy, THIN-B3 / HC / A8 / B6 |
| 21 | `21_a8_hc_b6_skr2_skr2e.md` (added 3 Nov) | 1 to 3 Nov: A8 KILL, HC and B6 n.d., SKR2 PASS / HC2 FAIL, SKR2E FAIL (E-PF stays), Om's A1 to A6, B2 agent raters, SKR2C |

For a quick start, read 01, 04 (skim), 11 and 16. Then go back to 02 to 10 as questions come up.

(Added 30 Oct) For the current state, read 11 rows 18 to 24, then 18 §M7 (FINAL), 19 §4 (encoder erasure) and §7 (protocol_100), and 15 §1f and §3b (what runs and what waits on the user). 16 section G has short answers.

## 3. Ten facts to hold onto
1. **Data.** BenchmarkEL `dataset_20211104`: 582 labelled cells (478 train / 54 val / 50 test), 512×512, 24 classes.
   - Focus classes: crack (id 14), about 0.19% of train pixels; inactive (id 11).
   - Sources: `03`; `MTP_session_handoff_2026-10-07.md` §3.1.
2. **Label fractions.**
   - 5 / 10 / 20 / 50 / 100% of train = 23 / 47 / 95 / 239 / 478 cells.
   - Inactive is in 2 / 4 / 9 / 20 of those labelled cells (5 to 50%).
   - Source: `protocols/P16_label_fraction_curve.md`.
3. **Test set.** 50 cells. Inactive is in 16 of them on the revised masks (17 on the old masks), and 3 cells hold 59% of its pixels, so inactive results are fragile. Crack is in 48 (50 on the old masks). Source: `results/p6/README.md`; `03_datasets_and_splits.md` §2.2.
4. **Labels.** Revised (E-SCDD) crack labels change the picture more than any SSL effect at 10%:
   - re-scoring old models on them gives +0.05 to +0.07 crack IoU (P3);
   - training on them gives +0.082 (P14).
   - For crack and inactive these labels are BenchmarkEL's own `20221008` correction, which E-SCDD redistributes unchanged (audit, doc 17).
5. **Baseline.** The supervised base since P6 is **L3**: U-Net++, ImageNet ResNet34, CE+Dice, label-safe augmentation, revised masks.
   - Crack IoU: 0.396 at 10% labels, 0.471 at 100%.
   - Source: `results/p6/README.md`.
   - [Note 30 Oct: the best model is now FINAL (25 Oct), the 5-seed ensemble of this recipe at 100% labels with a +0.75 crack bias: clean test crack IoU 0.492 (fact 10; doc 18 §M7).]
6. **Invalid old results.** All old Mean Teacher results used SemiCE, which is not a valid consistency loss (P2). ALHVR-20's gain equals its loss-off control's.
7. **BatchNorm handicap.** Before P13, the Mean Teacher student was handicapped by sharing BatchNorm with unlabelled images:
   - loss-off arm −0.017 crack IoU against supervised at 5% (P12);
   - P13 fixed it with a separate forward pass.
8. **P13, 5% labels, 5 vs 5 seeds.** SSL with separate BN + CutMix beats supervised:
   - inactive IoU +0.117, crack relaxed F1@2 +0.033, both robust over test cells;
   - crack IoU +0.014, not detectable.
   - Hard pseudo-labels (BsM5, 5 seeds after P13 Amendment 2) beat supervised on all three primaries: +0.029 / +0.107 / +0.045 (secondary contrast).
9. **P14.** An offset-tolerant supervised loss recovers none of the old-vs-revised label gap.
10. **Latest results.**
    - P15 (UCF-EL encoder transfer, gaint): no better than ImageNet init at 5%, worse at 10% on all three primaries (`results/p15/README.md`).
      [Qualified 30 Oct: P15 used the house fine-tune, which erased encoder layer3/4 in every ResNet-34 run measured (doc 19 §4). So P15 likely tested little more than conv1/layer1 transfer (S; not measured on the P15 encoder); the claim holds for that recipe only.]
    - P16 (SSL vs supervised at 20 / 50 / 100%, cv02, 5 vs 5 seeds, P13's Cs recipe with CutMix off): **fails at all three fractions**, n.d. on every primary. The 5% inactive gain shrinks to +0.029, +0.006, +0.003 (`results/p16/README.md`).
    - P17 (13 Oct, cv02, 5 vs 5): SKCDF-style decoupled decoder on BsM5 (pseudo-labels kept out of the labelled decoder). BsD5 − BsM5 is **n.d.** on all three primaries; BsD5 still beats supervised on all three. The detection threshold is about 40% of BsM5's gain, so a smaller decoder share is not ruled out (`results/p17/README.md`).
    - P18 (13 Oct, cv02, **exploratory**: the BsM recipe chosen after seeing P13's test results): BsM10 − A10 (3 v 3) and BsM20 − A20 (5 v 5) pass the rule-1 arithmetic on inactive IoU only (+0.132, +0.060); crack +0.012 / −0.006 n.d. One BsM20 seed fails on the noisy cell. Without that cell (post hoc) BsM10 passes on all three (+0.017 / +0.138 / +0.020) and BsM20 on inactive only (crack +0.013 vs threshold 0.014). Inactive bootstrap excludes 0 at 10%, not at 20% (`results/p18/README.md`).
    - P19 (14 Oct, cv02): Hanifi et al. 2025 (IEA/AIE) reproduced with their released code on the release split. VGG16-UNet matches the paper on features, crack and gridline (crack 0.352 vs 0.335); the defect mean is lower (0.246 vs 0.326) mostly because the release test split lacks dead cell and belt mark (`results/p19/README.md`).
    - SK1 + S-a (22 Oct, agent team, post hoc additions):
      - SKCDF's balanced head gives no detectable gain at 5% (n.d.), and the SKCDF track is closed.
      - A fixed logit bias (τ = 1) adds +0.015 to +0.023 crack IoU to every 5% arm. With the bias on both sides, SSL's crack gain over supervised survives (BsM5 +0.037, passes).
      - That SSL crack gain is no larger than the bias alone gives supervised: BsM5 − (A5c + bias) is n.d. This is a yardstick, not a verdict against SSL.
      - Inactive gains survive either way.
      - About half of test crack is a confident miss, mainly faint and inactive-edge cracks (doc 13 A12).
      - Train/test twins and the D7 pool rule: doc 10 SK1, `team_2026-10-21/data/decision.md`.
    - AL1 (23 Oct, agent team, post hoc addition; D7 pool):
      - ALHVR adapted to EL, with its loss active from step 4k, is **WORSE** than supervised at 5% on all three primaries: −0.017 / −0.132 / −0.031.
      - Its routing and prototype modules add nothing (n.d.). Plain cross pseudo-supervision is level with supervised.
      - Post hoc reading: the ALHVR losses halve inactive recall (doc 13 A13).
      - The old ALHVR question (doc 13 B3/E11) is closed (doc 10 AL1).
    - Measurement warning from P16: one very noisy test cell, `CSIR_00070_r8_c4`, makes about 1 run in 6 call 15 to 31% of it crack, cutting that run's crack IoU by up to 0.18. Without it P16's verdict is the same (crack Δ within ±0.003). Read every crack contrast with this in mind (doc 13).
    - **Added 30 Oct: 24 to 30 Oct** (docs 18, 19; experiment verdicts recomputed by each team's critic):
      - **Best model, FINAL** (25 Oct, Track M, cv02): the 5-seed mean-softmax ensemble of the 100%-label L3 recipe, crack bias +0.75 chosen on val. Clean test (49 cells): crack IoU **0.492** (single model 0.474; +0.018 [+0.013, +0.025]), relF1@2 0.897, crack components found 0.834, inactive IoU 0.456 (n.d.), E1 crack recall 0.215. Bias 0 (0.488) is the robust operating point: +0.75 calls 10,867 crack px on the noisy cell. "Almost all cracks" (relR@2 ≥ 0.90 at relP@2 ≥ 0.90) not reached: 0.866 at 0.930 (`team_2026-10-24_go/trackM/results_final.md`).
      - **Track M ladder:** Dice on 12 classes WORSE; Dice on 3 classes, +107 E-SCDD cells, 2× resolution n.d.; ResNet-50 WORSE on inactive. None entered FINAL.
      - **Track D:** frozen ImageNet ResNet-50 ranks BMRK crack better than the 5% model (low precision only). At +12 labelled cells, crack-containing cells beat random cells (relF1@2 +0.030) and the best SSL arm (0.352 vs 0.331), oracle-selected. Inactive-edge banding moves no SSL verdict.
      - **27 Oct synthesis:** pseudo-label SSL is a tight null at 20 to 100% (+0.01 excluded at 100%); 75% of unseen-module crack sits in half-cut cells with scuff streaks (recall 0.126), a context training lacks.
      - **Pool feature learning at 5% (29 to 30 Oct, gaint):** MIM5 n.d., every estimate negative; DDeP5 n.d., a threshold shift below the free bias; AM killed; CP5 stopped unscored. The 5% screen was a mistake: the user's question was about 100% labels (doc 19 §5).
      - **Encoder erasure (30 Oct):** the house fine-tune (Adam lr 1e-3, coupled wd 1e-4, 20k steps) ends ResNet-34 encoder layer3/4 at cosine about 0 to their init, for ImageNet and MIM inits, at 5% and 100%; the direction is already lost by step 2,000. Every "init / pretraining / backbone does not help" result holds only under this never-varied optimizer (for P15's and R3's encoders erasure is likely, not measured).
      - **Now:** protocol_100 (gaint, 4 arms × 5 seeds at 100% labels: SUP100-g, an encoder-preserving fine-tune SUP100-PF, MIM100-PF, CP100) launched 30 Oct 12:05 IST on v1.1. CP100 is held behind a decoy gate (6b), pending at 12:22. First test opening (the 15 fine-tunes) about 00:00 to 01:00 IST 31 Oct. **No results yet.** [Qualified 31 Oct: done; every contrast n.d. (doc 19 §10)]
      - **Labels:** the B1 audit flags crack in 24 of 239 train cells (sheets with the user). Scuff is labelled crack in 6 train cells (649 px) and 2 test cells (236 px); the user decided to train scuff as its own class (doc 17 §5.11).
    - **Added 3 Nov: 1 to 3 Nov** (doc 21; every verdict recomputed by coach and confirmed by judge):
      - **Recommended deployable candidate:** E-PF, the 5-member PF ensemble at argmax (PF2E; coach and judge). The user's adoption is still open (doc 15 §3d row 19). The SKR2 ensemble failed its guards at its own operating point (SKR2E, decided by the val width flag by 0.0015). FINAL (0.492, cv02) is not comparable by rule.
      - **Closed:** foundation encoder (A8 screen KILL: F51 AP −0.0243); the HC2 ignore design; Om's A1, A2, A3, A5, A6. HC (synthetic half-cuts) n.d.; route kept open by the user.
      - **Skeleton Recall at w 0.1 (SKR2):** E1 crack relF1@2 +0.0364 vs a 0.0351 bar, PASS, no test or false-alarm cost; label fragile, effect robust. Fresh-seed replication (SKR2C) was locked 3 Nov 02:37; its launch waits on fixes to the guard code; its opening needs the user's OK.
      - **B6:** PF's inactive gain is not shown in-distribution (n.d., power ~6% at +0.017), but a gain as large as E1's is excluded there.
      - **E1 inactive is a 3-image readout:** the top 3 source images hold 87% of its pixels; PF2's +0.189 is +0.023 without them.
      - **B2:** agent raters failed the scuff calibration gate; B2 is unmarked and back with the user.

## 4. The `sources/` folder
Verbatim copies of the primary documents: protocols, results READMEs and rules outputs, reports to the user, literature notes, data reports, and old-era reports from the servers. It also holds three files that exist only in the chat:
- the user's phase 0 and phase 1 handoffs;
- Claude's session summaries;
- the user's own messages.

See `sources/README.md`. The handbook docs cite paths relative to `~/mtp/research/` (e.g. `results/p13/README.md`). The same file is in `sources/results/p13__README.md`.

## 5. Reaching the live project files
If you can run commands (the user may give you exec access), the primary places are below. Full details are in `14_code_and_infrastructure.md`.

| Where | What |
|---|---|
| Local, the user's machine: `~/mtp/research` (git repo, local only) | `protocols/`, `results/`, `to_human/`, `scripts/`, `scripts_cv02/`, `scripts_gaint/`, `literature/`, `analysis/`, `data_analysis/`, `handbook/`. `papers/` holds PDFs: local only, never redistribute. |
| Local: `~/mtp/datasets` | BenchmarkEL `dataset_20211104` (images, old masks, class CSV) and README, split files, UCF-EL repo files and split manifests |
| gaint: `noob@172.18.22.20`, `/home/noob/work/el-fault-detection` | Training code (branch `main`) and worktrees `el_p13`, `el_p14`, `el_p16`, `el_p17`; old-era `reports/` |
| gaint: `/home/noob/work/cv02_noob_el/` | Copy of cv02 `/tmp/noob_el` (13 Oct): all `el_p*` run dirs and checkpoints, `diag/`, MD5-verified. Made because a cv02 reboot wipes `/tmp`. |
| cv02: `cv02@10.8.1.106`, `/tmp/noob_el/` | Deployed code per experiment (`el_p6`, `el_p7`, `el_p11`, `el_p13`, `el_p14`, `el_p16`, `el_p17`), run dirs, logs, E1 in `diag/`. **Wiped on reboot**; copied to gaint `cv02_noob_el`. A shared lab login: never forward an ssh agent or put keys there. |

(Added 30 Oct) Newer places: gaint worktrees `el_f1` (603e0d5), `el_f2` (2751aa8), `el_f3` (e544133, protocol_100), with the gaint memory rule (≥ 2 GB free for root's `finllm_chat.py`); cv02 Track M deployments `el_mt`, `el_mt4`, `el_mt5`; team folders `team_2026-10-21/`, `team_2026-10-24_go/`, `team_2026-10-24_why/`, `team_2026-10-27_unlabelled/`, `team_2026-10-29_features/` in `~/mtp/research`. Details in doc 14 §1.2b, §1.3b, §5b.

Earlier sessions reached the servers through "Herald" exec connectors (`Gaint_Herald` on gaint, `Yugma_Herald` or `noob_herald` for ssh to cv02). Each has an allowlist; limits are in `sources/MTP_session_handoff_2026-10-07.md` §2.3.

**Rules for touching the servers** (the user's standing instructions):
- Read only, unless the user asks otherwise.
- Never kill or launch runs or queues without the user's say-so.
- The gaint `extpool_20261007` queue stays held and untouched.
- On cv02 never start anything on a GPU where another user holds more than 4 GB.
- Never print or copy credentials. A Dropbox app secret exists on gaint and must never be exposed.
- Do not push to GitHub without asking.

## 6. Keeping this current
- After each new result, Claude writes `results/<exp>/README.md` and updates `to_human/results_2026-10-12.md` and this handbook (P15 and P16 done 12 Oct, P17 and P13 Amendment 2 on 13 Oct).
- To refresh the source copies, run `bash ~/mtp/research/handbook/sync_sources.sh`.
- If a handbook statement conflicts with a newer results README, the README wins.
- (Added 30 Oct) Agent-team results live in the team folders, not `results/<exp>/README.md`. For them the verify or results file (`verify_*.md`, `results_*.md`) wins over a session record or this handbook. Docs 18 and 19 note the discrepancies found.

## Related docs
All files `01` to `17` in this folder, and `sources/README.md`.
