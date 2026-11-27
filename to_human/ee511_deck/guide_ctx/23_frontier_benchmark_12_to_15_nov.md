# 23. The frontier team and the new benchmark protocol: 12 to 15 Nov 2026 (state 15 Nov, 14:50 IST)

## What this covers
This file explains, from zero, the work of 12 to 15 Nov 2026, run by the agent team in `team_2026-11-12_frontier/`. It is written for the guide agent.
- **Why the work changed direction** on 12 Nov and what the user decided (§1).
- **The new benchmark protocol**: the split, the label set, the metrics, the decision margin (§2).
- **The paper sweep**: how 639 recent papers were found and what became of each (§3).
- **Results under the new protocol**: baselines, the house recipe against PF, the label-fix ablation, the first benchmark rows, the CPU analyses (§4).
- **SKR2C**, the last opening of the old test sets: both verdicts FAIL (§5).
- **Duplicates** found in the data (§6).
- **What is running and what comes next** (§7), **incidents** (§8), **where the files are** (§9).

**Tags.** E = measured in our files (path given), S = judgement. Every number below is E unless marked S. "PF" = the encoder-preserving fine-tune of doc 20; "house recipe" = the same model with a plain fine-tune.

## 1. What changed on 12 Nov, and the user's decisions
- **The user's request (12 Nov):** one month is left (to about 12 Dec 2026). The mentor wants recently published work tried. Find the papers of the last five years that can raise our scores, adapt them to this project, and close a hypothesis only after it has been tested. Later the same day the user added a second aim: **set a trustworthy benchmark for this field**, which has no agreed protocol.
- **Decisions of 12 Nov** (answers to the lead's questions): open SKR2C now; use the corrected label set v1.1 for all new runs; a few-shot track on E1 only in the last week; new software only in separate environments, only public non-gated weights.
- **Decisions of 15 Nov:**
  - **Two tracks.** The main model and the benchmark use only data and weights with clear terms, so WattCycle can use the result. A separate, clearly labelled extra-data track for the thesis may train on UCF-EL and MultiSolSegment (public, no licence stated). Nothing from those sets is redistributed.
  - **One labelling pass.** The user will review about 24 pool half-cut cells with scuff streaks, pre-labelled by the models (accept, delete or extend marks), about 2 to 3 hours, for development reads only. This is the single exception to "no manual labelling".
  - The checkpoints of the October cv02 backup on gaint were deleted to free disk (192 GB; logs and metrics kept; list in `team_2026-11-12_frontier/log/deleted_cv02_noob_el_pth_20261115.txt`).

## 2. The new benchmark protocol
The old protocol scored 50 test cells again and again (18 counted openings by 14 Nov, `benchmark/test_openings.md`). The new one does not touch the sealed sets during development.
- **Data.** The 532 labelled pool cells (the old train + val). The legacy test set (50 cells) and E1 (106 cells from unseen modules) stay sealed. One registered E1 opening is planned near the end, with at most 3 candidates.
- **Split: CV5-G** (`benchmark/splits/cv5v2.json`). Five folds; cells of one module always stay in one fold (330 module groups). Every cell is predicted once by a model that never saw its module, so all 532 cells are scored out-of-fold.
- **Labels: set v1.1** (`benchmark/LABELS_V11.md`). Known label errors are corrected or marked "ignore"; ignore pixels are not scored.
- **Headline metrics.** Crack relF1@2 (a 2 px tolerance F1 on crack skeletons, with its precision relP@2 and recall relR@2), strict crack IoU, inactive IoU, and mIoU over 13 robust classes (mIoU-R13).
- **Operating points.** OP-A = plain argmax. OP-W = a crack bias fitted on the other folds so the predicted crack width matches the baseline's (so a model cannot win by drawing wider cracks). OP-F (bias fitted for F1) is printed but decides nothing: it is unstable (§4.2).
- **Seeds and margin.** 2 seeds to screen, 5 seeds for a table row. A difference counts only if it is at least **M = max(0.01, 2 x the standard error of an A/A comparison)** and its interval excludes 0, at OP-A and at OP-W, with the crack width inside ±15% of the baseline's.
- **Machines.** gaint (one RTX PRO 4500 Blackwell, 32 GB, shared with another group's server process) and cv02 (eight A6000, a shared lab login). A read never mixes machines.
- **Harness.** Repository `el_bench` on gaint: method cards, a queue with a memory guard, canonical prediction dumps, CPU read tools. Every launch is built by one agent, reviewed by another, and started by the lead.

## 3. The paper sweep
- 44 scout agents searched 44 directions (losses for thin structures, label noise, foundation backbones, unseen-domain methods, extra data, rare classes, benchmark protocol, and more) and returned 1,148 entries; after merging, **639 unique papers** (`rank/SHORTLIST.md`, ids P001 to P639).
- 13 family teams read them and gave **every paper a status** (`cards/ledger/MASTER.tsv`): 43 RUN_NOW, 56 RUN_AFTER_GATE, 77 BENCH_ONLY (a benchmark row, not a candidate), 61 PROTOCOL (goes into the protocol text), 10 PROMOTE (worth a card, not written yet), 390 PARKED (with the reason), 2 VOID (tested and closed). No paper is left open.
- Two critics reviewed the proposed experiments (`cards/WAVE2_REVIEW.md`, `cards/WAVE3_REVIEW.md`: 47 items, 25 go, 13 fix first, 9 dropped) and fixed an order: cheap CPU analyses first, then benchmark rows, then post-hoc arms, then the unseen-module instrument, then at most one trained inactive arm and one data arm.

## 4. Results under the new protocol
All on the 532 pool cells, out-of-fold, label set v1.1. Files: `results/W1G_FIRST_READ.md`, `results/W1C_READ.md`, `results/ROWS1_READ.md`, `results/stageA/`.

### 4.1 Baseline (PF, U-Net++ / ResNet-34)
| Machine, seeds | Strict crack IoU | Crack relF1@2 | Inactive IoU | mIoU-R13 |
|---|---|---|---|---|
| cv02, 5 seeds | 0.365 | 0.844 | 0.503 | 0.612 |
| gaint, 4 seeds | 0.365 | 0.844 | 0.503 | 0.613 |
- relP@2 0.894, relR@2 0.799: recall is the weak side on every source. Per source (crack IoU / relF1@2): ARTS 0.301 / 0.821, BMRK 0.400 / 0.835, CFVS 0.371 / 0.859, CSIR 0.337 / 0.799.
- The legacy test set had flattered the model (crack IoU 0.474, relF1@2 0.881 there).

### 4.2 The decision margin (A/A comparisons)
- Seeds {5, 6} against {7, 8} of the same recipe: **M = 0.010** for crack IoU, relF1@2 and mIoU-R13 on both machines; **0.05** for inactive IoU.
- Of 15 possible two-seed A/A splits on cv02, none would have been promoted by the rule (`results/stageA/A1.md`).
- Two identical recipes differ by 0.02 on inactive IoU from seeds alone, so **inactive IoU cannot screen a trained arm at 2 seeds**; inactive arms are read by region counts or at 5 seeds.
- OP-F showed a "significant" A/A difference (-0.012 crack IoU), so it decides nothing.

### 4.3 House recipe against PF, and the label fix
- **House minus PF** (cv02, 2 seeds against 5): strict crack IoU **+0.017 [+0.011, +0.024]** at argmax and **+0.011 [+0.003, +0.019]** width-matched; relF1@2 +0.006 (inside M); the house model draws cracks 11% wider and doubles false crack pixels on crack-free cells. So on cells from known modules the plain fine-tune is the better crack segmenter by strict overlap; PF had been adopted for unseen modules (doc 20). **Ruling:** PF stays the comparator of every arm; the house recipe is its own table row; whether PF's unseen-module edge is real under the new protocol is a question for the instrument of §7.
- **Label-fix ablation** (PF trained on v1 against v1.1, both scored on v1.1): crack IoU +0.0004 [-0.006, +0.007]; nothing measurable. The fix matters for scoring, not for training.

### 4.4 First benchmark rows (cv02, 2 seeds each, equal training)
| Row | Output stride | Strict crack IoU | relF1@2 | Inactive IoU | mIoU-R13 |
|---|---|---|---|---|---|
| U-Net / ResNet-34 | 1 | 0.364 | 0.843 | 0.522 | 0.612 |
| U-Net / VGG-16 (Hanifi et al.) | 1 | 0.349 | 0.838 | 0.498 | 0.610 |
| DeepLabV3+ / ResNet-34 | 4 | 0.354 | 0.835 | 0.478 | 0.609 |
| DeepLabV3 / ResNet-50 (UCF-EL's model) | 8 | 0.287 | 0.767 | 0.497 | 0.574 |
| DeepLabV3+ with Pratt's weighted loss | 4 | 0.258 | 0.751 | 0.506 | 0.604 |
- No row beats PF or the house recipe. The decoder does not matter (U-Net equals U-Net++). The output stride does: width-matched, stride 4 costs about 0.02 and stride 8 about 0.08 to 0.10 on both crack metrics. Pratt's class weights make cracks three times too wide (precision 0.65).
- Limits (S): 2 seeds, one machine, pool cells only; each card lists its deviations from the paper it stands for.

### 4.5 CPU analyses (stage A, independently reviewed: no item failed)
- **Headline metric stays relF1@2; tolerance stays 2 px** (annotator disagreement is within 2 px on the few double-annotated pairs).
- **A 2-seed ensemble beats single models by +0.0116 strict crack IoU** on both machines, so the distillation arms may be built.
- **Post-hoc ideas closed, with evidence, on both machines:** per-source calibration (-0.0015 to +0.0003), hysteresis thresholding (+0.0003 to +0.0013), inactive post-hoc rules (they would change under 1% of pixels).
- **Inactive error atlas:** about half of the missed inactive area is whole regions the model does not see at all; the one trained inactive arm chosen for building is a layered decision head.
- **Head resolution:** a stride-4 head caps thin-crack quality, as the rows of §4.4 then showed.

## 5. SKR2C: the last opening of the old sets (final 14 Nov)
- **What:** Skeleton Recall loss (weight 0.1) against the PF baseline on fresh seeds 10 to 14, scored once on the legacy test set and E1 (E1 opening #7, test opening 18; the third look at the same cells for this contrast). Opened on the user's OK of 12 Nov; an independent coach recomputed it and a judge confirmed it (`team_2026-10-31_next/verify_skr2c.md`).
- **Verdict R (single models): FAIL** by two guards: test inactive IoU -0.020 (bar -0.015) and test crack precision -0.078 (bar -0.03; this trip is one run on one noisy test cell and stands as registered).
- **Verdict D (5-model ensembles): FAIL** by the test inactive guard alone (-0.027). Fixed wording: about a 15% chance that a true null fails through an inactive guard alone.
- **Outcome:** the SUP100-PF ensemble stays the deployable candidate; Skeleton Recall at weight 0.1 is closed for the deployable. The E1 crack relF1@2 difference appeared again in the ensemble pair (+0.034 [+0.012, +0.054]) but replication at recipe level was not shown (seed-aware interval [-0.0015, +0.059]).
- **Not claimable:** "SKR2 replicated", "E1 gain confirmed", "SKR2 hurts inactive", "SKR2 loses precision".
- **What it leaves open (S):** the same E1 difference has now shown at three looks on the same cells. Only cells from other modules can say whether it is real; a Skeleton Recall anchor run on the new leave-source-out roots (§7) is planned for that reason, as a test of the instrument, not as a candidate.

## 6. Duplicates in the data
- The duplicate search (md5, image correlation, DINOv2 embeddings; image pixels only) found that the module rule misses some copies.
- **Pool:** 74 unlabelled pool cells are near-exact copies of labelled or sealed cells. The one pool list for all pool arms (`benchmark/splits/pool_t9.txt`, 6,424 of 11,938 cells) excludes them and everything close to them.
- **Labelled cells:** two cells appear twice in different folds (checked by eye on the images): `ARTS_00165_r12_c5` = `ARTS_00166_r12_c5`, and `CFVS_00076_r1_c1` = `CFVS_00082_r1_c1` (the same cell at a later stress stage). **Ruling:** the split stays; final tables score 528 cells with these 4 excluded and print the 532-cell value beside it (`benchmark/splits/dup_crossfold_v1.tsv`). A full audit of the remaining same-position pairs is owed.
- **Added 15 Nov, 22:14: the full audit is done, and the problem is at module level** (`results/stageC/SPLIT_INTEGRITY.md`). One physical module can carry several image ids (on ARTS the printed serial numbers prove it). In the split, 24 physical modules span two folds, so **91 of the 532 cells are scored by a model that has seen another cell of their module** (4 of them the very same cell). **E1 shows no link to any training module** (checked from image pixels, for the third of the pairs that can be checked). 8 legacy test cells are the same physical cell as a training cell. **Rulings:** results are read on the clean cells (99 excluded, 433 left; the 532 value is printed beside); the baseline on clean cells is **0.347 strict crack IoU, 0.826 relF1@2, 0.50 inactive IoU, 0.606 mIoU-R13**, about 0.018 lower on the crack metrics than on all 532; no comparison between methods changes; the final 5-seed table will be trained on a corrected split (cv5v3). The pool list shrank to 4,949 cells for the same reason.

## 7. Running now, and next
- **Wave 2a on gaint** (first trained arms: rare-class sampling, weight averaging, soft-band and hard JML losses, SWAD, encoder SPD regularisation): 27 of 61 runs trained by 15 Nov 14:47; expected to finish about 17 Nov; read against the four gaint PF seeds with M = 0.010.
- **Stage B (being built):** the unseen-module development instrument (development sets and leave-source-out training roots, so unseen-module behaviour can be measured without E1), the labelling pack for the user, the cross-fitted class-bias arm, test-time augmentation.
- **Benchmark rows tranche 2 (being built):** SegFormer MiT-B2, HRNet-W18 U-Net++, the Skeleton Recall anchor. cv02 is crowded by other users, so these wait for free GPUs.
- **Then (S):** the leave-source-out baseline on gaint, the layered inactive head, further rows (Hiera, RIFT), the benchmark protocol text v0.2, one E1 opening in the last week.

## 7b. Severity track (added 16 Nov; user approved it on 15 Nov)
- **What was done:** a side track asked whether the segmentation output can be turned into a severity figure, using three public sets that have electrical measurements. No model was trained on them; they were used for inference and analysis only. Files: `results/severity/SEVERITY_SUMMARY.md` (start there), `S0` to `S4` beside it, review `harness/REVIEW_SEVERITY.md` (every number reproduced; no item fails; four wording fixes applied 16 Nov).
- **What the model now reports per cell (E):** the predicted inactive area in % of the cell, with a band (0 / under 1% / 1% or more). On our 532 pool cells, out of fold, the mean error is 0.12 percentage points; on the 48 cells that have inactive area it is about 1.25. A cell predicted at 1% or more is truly there in 93% of cases; the "under 1%" band is unreliable. The crack-isolation score was dropped: it works on clean labels, not on predictions.
- **Against measured power (E):** no claim holds.
  - Polenghi (2 mini-panels, 84 damage stages): null. Damage only accumulates there, so the stage number alone tracks the loss best.
  - ELPVPower (137 modules with measured Pmpp): null by the rule fixed in advance. Predicted inactive area ranks modules by loss at rho 0.87, but crack length does as well (0.89), and most of it is module type.
  - DTU A3 (lab-damaged modules, fill-factor loss): borderline. On the 16 modules that could be cut into cells, predicted inactive area tracks the loss better than plain EL darkness (rho 0.90 against 0.44), but the interval's lower end is about 0 and the four highest-loss modules could not be cut.
- **Thermal (E, module level):** drone thermal does not track loss from cracks, interconnects or PID (rho 0.19). It flags bypass-diode faults and soiling strongly (16 to 38 deg C against about 1). It is a screen for those faults, not a crack-severity measure.
- **Rulings (lead, 16 Nov):** severity goes into the thesis as an appendix table with the per-cell inactive-area output; no watt figure and no power band is claimed. What a pilot on WattCycle's own modules would have to measure is in section 6 of the summary (about 31 modules for a true rho of 0.5, within one module type, rule written before measuring).

## 8. Incidents (so nobody repeats them)
- **13 Nov:** a 5-hour usage cap stopped nine agents; the laptop rebooted six times. The orchestrator then moved from the laptop to gaint (`migrate/HANDOVER.md`); the laptop copy of the project is stale.
- **14 Nov 01:28:** a builder agent stalled for two hours on a file-permission prompt (a file tool used outside the session's folders). Fixed in the prompts; on 15 Nov the user added `/home/noob/work` as an allowed folder.
- **14 Nov, after 06:31:** the orchestrator process ended (cause unknown). For 27 hours nothing was read or launched; the queues ran on.
- **15 Nov 09:49:** the wave 2a queue and two trainings were stopped by a signal from inside their tmux session, not on purpose. Restarted at 12:43 from the reviewed job list (36 runs left). Attach to the orchestrator with `tmux attach -t orch`, never with a bare `tmux attach`.
- **15 Nov:** gaint's disk reached 95%; freed as in §1.
- **Shared GPUs:** another process used 8.8 GB of the gaint GPU on the night of 14 to 15 Nov, so wave 2a runs 2 lanes, not 3. On cv02 a run starts only on a GPU where other users hold under 4 GB.

## 9. Where the files are (all under `research/team_2026-11-12_frontier/` unless stated)
| What | File |
|---|---|
| Day-by-day record | `log.md` |
| Brief for agents, project facts | `BRIEF.md` |
| First numbers | `results/W1G_FIRST_READ.md`, `results/W1C_READ.md`, `results/ROWS1_READ.md` |
| Stage A analyses and their review | `results/stageA/`, `harness/REVIEW_STAGEA.md` |
| Paper list and statuses | `rank/SHORTLIST.md`, `cards/ledger/MASTER.tsv` |
| Experiment specs and the critics' plans | `cards/T*_spec.md`, `cards/WAVE2_REVIEW.md`, `cards/WAVE3_REVIEW.md` |
| Splits, pool list, duplicate list, openings registry | `benchmark/splits/`, `benchmark/test_openings.md` |
| Harness design, launch requests and reviews | `harness/` |
| SKR2C verify | `../team_2026-10-31_next/verify_skr2c.md` |
| Move to gaint | `migrate/HANDOVER.md` |
