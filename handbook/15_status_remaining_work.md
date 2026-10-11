# 15. Status and remaining work

**What this covers.** The state of every experiment on 11 Oct 2026, about 22:30 IST. What is running, what happens automatically overnight, what is left for part 1 of the thesis, which decisions are waiting on the user, and the housekeeping debts. This doc goes stale fastest: check `results/p15/` and `results/p16/` and the git log of `~/mtp/research` for anything newer.

**Sources**
- Launch logs on the servers, read at about 22:15 IST:
  - gaint `/home/noob/work/el_p14/reports/p15/launch_gaint.log`;
  - cv02 `/tmp/noob_el/el_p16/reports/p16b/launch.log` (UTC) and `el_p16/reports/p16b_auto.log` (Part B has no `queue.log`); Part A: `el_p13/reports/p16/launch.log`.
- `to_human/results_2026-10-12.md`.
- `to_human/proposal_reframe_2026-10-11.md` §5 and §7.
- `to_human/directions_2026-10-10.md`.
- `~/mtp/MTP_session_handoff_2026-10-07.md` §12 and §13.
- Protocols P15 and P16.
- `scripts/post_p15.sh`, `scripts/post_p16.sh`.

---

## 1. Experiment status

| Exp | Status | Where results are |
|---|---|---|
| P1 to P12 | Done | `results/p1` … `results/p12` (P3 to P5 under `p3_label_versions`, `p4_feature_probe`, `p5_region_pl`) |
| P13 audit | Done | `results/p13_audit/` |
| P13 | Done, 21:04 IST 11 Oct. The primary claim passes. | `results/p13/README.md` |
| P14 | Done, 19:34 IST 11 Oct | `results/p14/README.md` |
| E1 (task metrics, 106-cell extension) | Done for P6 to P15; P16 is added when it finishes | `results/e1/` |
| **P15** (gaint, UCF-EL encoder transfer) | **Done**, 6 runs rc = 0 (17:01 to 22:26 IST); analysed about 22:40 IST. **Fails:** 5% n.d. on all three; 10% worse on all three, robust over cells. | `results/p15/README.md`, `results/e1/e1_p15.md` |
| **P16 Part A** (supervised 20/50/100%) | Done, 9 runs, rc = 0 (22:06 IST) | cv02 `el_p13/reports/p16/`; analysed with Part B |
| **P16 Part B** (SSL S20, S50, Sx100) | **Running.**<br>• 15 runs started 21:05 IST on cv02 GPUs 0, 3, 4, 5, 6, 3 per GPU.<br>• About 0.92 to 0.96 steps/s (stdout at 22:25 IST, steps 4,350 to 4,550), so done about 03:00 to 03:30 IST on 12 Oct, inside the ~03:00 to 04:30 window the other docs give.<br>• CutMix off, chosen from P13 val as locked. | will be `results/p16/` |

**Held, do not touch:** the gaint `extpool_20261007` night queue (old-era Mean Teacher runs with SemiCE). It was held by hand on 8 Oct, 01:18 IST (19:48 UTC on 7 Oct) while SemiCE was under audit, and P2 later showed SemiCE is invalid. The user's standing instruction is to leave it held and untouched. (Source: the user's command in `sources/chat/user_messages_2026-10-07_to_11.md`, 2026-10-07T19:48Z; session summaries.)

## 2. What happens automatically overnight (Claude's queue)
A watcher (`scratchpad/watch.sh`) polls both servers every 2 minutes and fires on each finished set. Planned handling:
1. **P15 (done 11 Oct ~22:40 IST):** `bash scripts/post_p15.sh <cv02 gpu>`.
   - Locked rules: gU5 − A5 and gU10 − gA10.
   - E1 per-cell scoring on cv02.
   - Write `results/p15/README.md`, then commit.
2. **P16:** `bash scripts/post_p16.sh <cv02 gpu>`.
   - Locked rules: S20 − A20, S50 − A50 and Sx100 − A100, 5 vs 5 seeds.
   - Bootstrap, source split, E1, bars, and the label-fraction curve (`scripts/p16_curve.py`).
   - Write `results/p16/README.md`, then commit.
3. **Morning, 12 Oct:**
   - Finalise `to_human/results_2026-10-12.md`.
   - Update `to_human/proposal_reframe_2026-10-11.md` and `midterm_deck_outline.md` neutrally ("framing depends on final results").
   - Refresh this handbook (§6 below).
   - Send the user one summary: results per experiment against the locked rules, plus the evidence table.

## 3. Decisions waiting on the user

| # | Decision | Why it is open | Source |
|---|---|---|---|
| 1 | Thesis framing (e.g. "SSL works once the pipeline is fixed" vs "a measurement and diagnosis study" vs a mix) | The user's rule: "framing depends on final results, no presumptions, ever". Needs P15 and P16. | user, 11 Oct |
| 2 | Whether to run hard pseudo-labels + CutMix (the BsM recipe) at 20% or 50% labels | P13's best crack arm was BsM5. P16 runs the Cs recipe because the locked val-based pick chose CutMix off. A BsM arm at 20/50% would be chosen after seeing test results, so it can only be reported as exploratory. | `results/p13/README.md`; chat 11 Oct |
| 3 | Larger test set, and whether to use E-SCDD's extra labelled cells | The user said "conside rit" (11 Oct).<br>• Done: a 106-cell extension from BenchmarkEL modules we never trained on (E1).<br>• Done 12 Oct: full E-SCDD and BenchmarkEL `20221008` downloaded and audited (doc 17).<br>• Facts for the decision:<br>&nbsp;&nbsp;– 233 labelled real cells we never trained on, 111 of them in our external pool;<br>&nbsp;&nbsp;– E-SCDD's own test is unusable with our split;<br>&nbsp;&nbsp;– a 172-cell test (ours + E1 + 17 new) has 26 inactive cells with a top-3 share of 53.5%.<br>• Open: use any of it (new base, held-out selection set, larger test) or not. | `results/escdd_audit/README.md` §8; `results/e1/README.md` |
| 3b | Thesis wording for the revised labels | They are BenchmarkEL `20221008` crack/inactive labels obtained via E-SCDD (doc 17 §5.2) | `results/escdd_audit/README.md` §4 |
| 4 | Mid-term deck content | The outline predates P9 to P16 | `to_human/midterm_deck_outline.md` |
| 5 | Identity, institute and report template for the MTP report | Inconsistent across sources (phase 1 handoff §1) | phase 1 handoff |

## 4. Remaining work for part 1 (training methodology)
Ordered roughly by information per cost. None of these is started; each would need its own locked protocol and the user's go-ahead.

| Item | What it answers | Rough cost | Source |
|---|---|---|---|
| Read P16 | Does SSL still help at 20/50/100%? (P15 is read: UCF-EL transfer does not beat ImageNet init) | overnight, automatic | protocol P16 |
| More seeds for BsM5 (hard PL + CutMix), and a gaint replication of P13 | BsM5's crack gain (+0.036) is secondary with 3 seeds. P13 had no gaint replication (Amendment 1). | 2 to 5 runs, about 7 h on cv02 | `results/p13/README.md` |
| In-domain self-supervised pretraining (masked image modelling) of the encoder | Uses unlabelled cells without pseudo-labels. Our directions report rates it the main "no-pseudo-label rival". | 1 to 2 GPU-days | `directions_2026-10-10.md` §4; proposal §5 E3 |
| Distillation into a 2 to 5M-parameter student | The deliverable model size | about 6 runs | proposal §5 E5 |
| Severity pipeline (components, skeleton, isolation, Köntges A/B/C) | The measurement WattCycle needs. It was lost in the reset and must be rebuilt. | CPU, 2 to 3 days | proposal §5 E6; phase 0 handoff "Subpath A" |
| Rare-class share floor and cap for pseudo-labels | Fixes the collapse at 5% (P10) and the over-prediction on UCF (phase 1) | a few runs | proposal §3 |
| More label subsets (split seeds 1, 2) or cross-validation over the 582 cells | Everything so far uses one labelled subset and one 50-cell test set | reruns | handoff §12.4 items 6 and 7 |
| Larger test set (data now local: doc 17) | Inactive is decided by about 3 test cells. The candidates add many crack cells but little inactive (A: +10 inactive cells, 9,158 px) | re-scoring existing checkpoints on the new cells (no training) | `results/escdd_audit/README.md` §8; E1 README |
| Tolerant Dice term; tuning the tolerance radius R | P14 tested only R = 2 with a tolerant CE term | a few runs | P14 "Not claimed" |

## 5. Parts 2 and 3 (after part 1)
- **Part 2, architecture.** Phase 0 ideas:
  - is the self-attention block in SA U-Net++ (`sigmoid(Q+K)*V`, an elementwise gate) worth anything (SA vs no-SA ablation);
  - native narrow models (base width 20 or 24, 1.79M or 2.58M parameters);
  - coarse non-local or axial attention;
  - thin-structure-preserving downsampling (check first whether cracks survive encoder pooling).

  Source: phase 0 handoff, Part 2.
- **Part 3, deployment.**
  - Latency harness on Jetson.
  - Compression: Torch-Pruning to about 2M, INT8 + TensorRT (the Jetson has no FP8).
  - Rerun the severity pipeline on every compressed model; Pareto plot.
  - About 0.2 s per cell is available (lit).

  Sources: phase 0 handoff "Subpath B"; `directions_2026-10-10.md` §1.5.
- **Power loss:** out of scope unless valid data appears (user, 11 Oct). Literature correlations exist (NREL crack-to-power-loss, Dhimish & Hu 2022, Kropp et al. 2018; links in the phase 0 handoff).

## 6. Keeping this handbook current
After P15 and P16, update these docs:
- `10_experiments_P13_P16_E1.md`: P15 and P16 sections.
- `11_results_synthesis_and_claims.md`: evidence table rows 3, 7, 10.
- `13_problems_pitfalls_open_issues.md`: open questions.
- This file.
- `handbook/sources/`: re-run `bash handbook/sync_sources.sh`.

## 7. Housekeeping debts

| Item | Note | Source |
|---|---|---|
| Rotate the Dropbox app secret | It was pasted in chat on 2 Oct; rotation not confirmed | phase 1 handoff §2.4 |
| cv02 `/tmp/noob_el` is wiped on reboot | Results are pulled into `~/mtp/research/results/` after each experiment; checkpoints are not backed up | handoff §2.2 |
| GitHub | The research notes repo is local only. Push nothing without asking the user. | standing instruction |
| gaint shutdowns | Unexplained reboots on 2, 6 and 7 Oct; the queue resumes from `latest.pth` | handoff §2.1 |

## Related docs
- `10_experiments_P13_P16_E1.md`: designs of P15 and P16
- `11_results_synthesis_and_claims.md`: what the pending results will decide
- `12_decisions_log.md`: decisions so far
- `13_problems_pitfalls_open_issues.md`: open issues in detail
- `14_code_and_infrastructure.md`: how runs and post-processing work
