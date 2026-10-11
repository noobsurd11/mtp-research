# 00. START HERE: handbook for the MTP project (EL defect segmentation)

**What this is.** A handbook for an agent that will act as a guide and interpreter for the student who owns this project (called "the user" below). The user wants to understand the whole project from zero to one: scope, domain, data, jargon, work done, problems, decisions, results, and what is left. These docs hold everything known as of **12 Oct 2026, about 05:30 IST**: every P-series experiment (P1 to P16) is finished and analysed, plus the **E-SCDD download and audit of 12 Oct, about 02:30 IST** (doc 17). The `sources/` folder holds the primary documents they rest on. The live project files are reachable by command (section 5).

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
| 10 | `10_experiments_P13_P16_E1.md` | The fixes, tolerance for human labels, transfer, label-fraction curve, task metrics |
| 11 | `11_results_synthesis_and_claims.md` | What can be claimed, with what evidence |
| 12 | `12_decisions_log.md` | Who decided what, when, and why |
| 13 | `13_problems_pitfalls_open_issues.md` | Every problem and open issue, and its impact |
| 14 | `14_code_and_infrastructure.md` | Code, servers, scripts, where every file lives, how to reproduce |
| 15 | `15_status_remaining_work.md` | What is running, what is left, decisions waiting on the user |
| 16 | `16_faq_for_the_guide.md` | Short grounded answers to likely questions |
| 17 | `17_escdd_dataset_audit.md` | The E-SCDD dataset and paper: what it really contains, the audit, and what it changes |

For a quick start, read 01, 04 (skim), 11 and 16. Then go back to 02 to 10 as questions come up.

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
6. **Invalid old results.** All old Mean Teacher results used SemiCE, which is not a valid consistency loss (P2). ALHVR-20's gain equals its loss-off control's.
7. **BatchNorm handicap.** Before P13, the Mean Teacher student was handicapped by sharing BatchNorm with unlabelled images:
   - loss-off arm −0.017 crack IoU against supervised at 5% (P12);
   - P13 fixed it with a separate forward pass.
8. **P13, 5% labels, 5 vs 5 seeds.** SSL with separate BN + CutMix beats supervised:
   - inactive IoU +0.117, crack relaxed F1@2 +0.033, both robust over test cells;
   - crack IoU +0.014, not detectable.
9. **P14.** An offset-tolerant supervised loss recovers none of the old-vs-revised label gap.
10. **Latest results.**
    - P15 (UCF-EL encoder transfer, gaint): no better than ImageNet init at 5%, worse at 10% on all three primaries (`results/p15/README.md`).
    - P16 (SSL vs supervised at 20 / 50 / 100%, cv02, 5 vs 5 seeds, P13's Cs recipe with CutMix off): **fails at all three fractions**, n.d. on every primary. The 5% inactive gain shrinks to +0.029, +0.006, +0.003 (`results/p16/README.md`).
    - Measurement warning from P16: one very noisy test cell, `CSIR_00070_r8_c4`, makes about 1 run in 6 call 15 to 31% of it crack, cutting that run's crack IoU by up to 0.18. Without it P16's verdict is the same (crack Δ within ±0.003). Read every crack contrast with this in mind (doc 13).

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
| gaint: `noob@172.18.22.20`, `/home/noob/work/el-fault-detection` | Training code (branch `main`) and worktrees `el_p13`, `el_p14`, `el_p16`; old-era `reports/` |
| cv02: `cv02@10.8.1.106`, `/tmp/noob_el/` | Deployed code per experiment (`el_p6`, `el_p7`, `el_p11`, `el_p13`, `el_p14`, `el_p16`), run dirs, logs, E1 in `diag/`. **Wiped on reboot.** |

Earlier sessions reached the servers through "Herald" exec connectors (`Gaint_Herald` on gaint, `Yugma_Herald` or `noob_herald` for ssh to cv02). Each has an allowlist; limits are in `sources/MTP_session_handoff_2026-10-07.md` §2.3.

**Rules for touching the servers** (the user's standing instructions):
- Read only, unless the user asks otherwise.
- Never kill or launch runs or queues without the user's say-so.
- The gaint `extpool_20261007` queue stays held and untouched.
- On cv02 never start anything on a GPU where another user holds more than 4 GB.
- Never print or copy credentials. A Dropbox app secret exists on gaint and must never be exposed.
- Do not push to GitHub without asking.

## 6. Keeping this current
- After each new result, Claude writes `results/<exp>/README.md` and updates `to_human/results_2026-10-12.md` and this handbook (P15 and P16 done 12 Oct).
- To refresh the source copies, run `bash ~/mtp/research/handbook/sync_sources.sh`.
- If a handbook statement conflicts with a newer results README, the README wins.

## Related docs
All files `01` to `17` in this folder, and `sources/README.md`.
