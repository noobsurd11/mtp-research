# 12. Decisions log (7 to 13 Oct 2026, with the pre-7-Oct decisions that still shape the work)

## What this covers
Every significant decision in the project from the restart on 7 Oct 2026 up to 11 Oct ~22:00 IST, extended to 13 Oct (D34 to D38). For each one it records:
- who made it (the user, or Claude);
- what was decided and why;
- what else was considered;
- what came of it.

It starts with the decisions inherited from the earlier phases (phase 0 and phase 1, before the gaint account reset), because several of them were later reversed. It ends with the rules that came out of mistakes.

Read it to answer "why did we do X and not Y?". For the experiments themselves see `08_`, `09_` and `10_`. For problems and open issues see `13_problems_pitfalls_open_issues.md`.

**Update 30 Oct 2026 (additive):** §4c adds the decisions of 24 to 30 Oct (D41 to D50), with index rows, K10 and K11, and four rules in §6. Experiments for these dates: `18_experiments_trackD_trackM.md`, `19_feature_learning_and_100pct_plan.md`.

**Conventions**
- **Times are IST** (UTC + 5:30).
  - User messages are timestamped in UTC in the transcript extract and converted here.
  - Git commit times in `~/mtp/research` are local IST.
  - cv02 logs are in UTC.
- **"Claude"** means the assistant working in this session. Earlier phases had other Claude sessions; they are called "phase 0" and "phase 1".
- **Arm names** (A5c, Cm, CsM5, L3, and so on) are defined in `04_glossary_and_naming.md`.

## Sources
- User messages with timestamps: scratchpad `docsrc/user_messages.md`, extracted from the session transcript `~/.claude/projects/-home-yugma/57bebbba-992f-43ae-8c6c-f7004d0f15c5.jsonl`.
- Session summaries 8–11 Oct: scratchpad `docsrc/session_summaries.md`. They are cited as "session summary <UTC time>".
- Phase 0 / phase 1 handoffs and the phase-1 answers, pasted by the user on 11 Oct: scratchpad `docsrc/phase0_phase1_handoffs.md`.
- The three scratchpad files have byte-identical stable copies in `sources/chat/`: `user_messages_2026-10-07_to_11.md`, `claude_session_summaries_2026-10-07_to_11.md`, `phase0_phase1_handoffs_pasted_2026-10-11.md`. The user-messages extract leaves out the two long pastes of 11 Oct (06:46Z and 07:02Z); they are in the handoffs file.
- Protocol headers sometimes state lock times that disagree with git (`13_problems_pitfalls_open_issues.md` D17). This log uses git commit times.
- `~/mtp/MTP_session_handoff_2026-10-07.md` (the 7 Oct handoff, "handoff 7 Oct").
- `to_human/situation_report_2026-10-08.md`, `to_human/directions_2026-10-10.md`, `to_human/proposal_reframe_2026-10-11.md`, `to_human/midterm_deck_outline.md`, `to_human/results_2026-10-12.md`.
- All protocols in `protocols/`, especially their "What I had seen", "Why this exists" and amendment sections.
- Results READMEs in `results/`.
- `git -C ~/mtp/research log`.
- Memory notes `~/.claude/projects/-home-yugma/memory/*.md`.

---

## 0. Index (one line per decision)

| # | When (IST) | Who | Decision |
|---|---|---|---|
| H1–H9 | before 7 Oct | phase 0 / 1 | inherited decisions (batch 4, SemiCE Mean Teacher, ALHVR port, final-step weights, step matching, within-machine only, external pool parked, ...) |
| D1 | 7 Oct 23:37 | user | restart: analysis first, be skeptical, ALHVR-inspired rare-class goal |
| D2 | 7 Oct 23:55 | user | direct SSH, not the Herald connectors; thesis split into 3 parts, training methodology first |
| D3 | 7–8 Oct | Claude | lock every protocol before running (confirmatory vs exploratory) |
| D4 | 8 Oct 01:18 | user (proposed by Claude) | hold the gaint external-pool Mean Teacher queue (SemiCE under audit) |
| D5 | 7 Oct 23:59–8 Oct 00:37 | Claude proposed, user approved | P1 (overfit check) and P2 (SemiCE probe) first |
| D6 | 8 Oct 12:05 | user | same first-hand data analysis for UCF-EL |
| D7 | 8 Oct | Claude | UCF-EL cannot carry a label-efficiency claim until re-split by physical module (not done since) |
| D8 | 10 Oct 09:29 | user | 2-hour directions scan with institutional PDFs |
| D9 | 10 Oct ~10:00 | Claude | P3 label re-score (exploratory), then P4 and P5 as locked offline probes |
| D10 | 10 Oct ~10:00 | Claude | method hook = offset-tolerant targets plus per-class routing (from P5) |
| D11 | 10 Oct 11:22 | user asked, Claude picked | two mid-term experiments: P6 (baseline ladder) and P7 (tolerant-PL pilot) |
| D12 | 10 Oct 11:38 | user | parallelise on cv02/gaint via tmux without affecting results |
| D13 | 10 Oct 11:42 | Claude | P6 design: revised E-SCDD masks, one-change ladder L0→L3, all arms on cv02 |
| D14 | 10 Oct 15:43 | locked rule | P7 base = L0 (val); headroom −0.001, so P7 becomes a pilot |
| D15 | 10 Oct 15:43 | Claude (disclosed post hoc) | P8: same arms on L3 (the base with a label gap); primaries switched from AP to IoU/IoU/relF1@2 |
| D16 | 10 Oct 17:14 | user ("fasten up"), Claude | launch P8 now, co-located with P7 |
| D17 | 10 Oct 22:31–22:53 | Claude proposed, user approved | P9 external pool; overnight SSL on all resources |
| D18 | 10 Oct 22:56–23:04 | Claude | P10 at 5% labels; B5 by amendment; gaint runs supervised references only |
| D19 | 10 Oct ~23:00 | Claude | queue race fixed; one queue per machine, chained queues |
| D20 | 11 Oct 00:11 | Claude | P11: matched labelled view (`ssl.labeled_aug=supervised`) because P8's loss-off control sat below supervised |
| D21 | 11 Oct 01:37 | Claude | P12: matched pipeline at 5%, a cv02 supervised A5c, gaint replication + calibration |
| D22 | 11 Oct 11:24–11:51 | user challenge, Claude audit | "supervised beating SSL": audit, then P13 (separate-BN forward + CutMix) |
| D23 | 11 Oct ~12:16–12:46 | user | "gather questions and ask"; launches held behind a GO file until answered |
| D24 | 11 Oct 12:37 | Claude | proposal re-framed from the effect-size budget (draft) |
| D25 | 11 Oct 12:46 | user | 8 answers: "framing depends on final results, no presumptions, ever", "your call", 1 day, etc. |
| D26 | 11 Oct 12:51 | Claude | P13 Amendment 1: 5% only, 5 vs 5 seeds, Ds5 dropped, gaint goes to P15 |
| D27 | 11 Oct 12:55 | Claude ("your call") | P14 (tolerant supervision) on cv02, P15 (UCF-EL encoder transfer) on gaint |
| D28 | 11 Oct 12:59–14:03 | Claude ("conside rit") | E1 per-cell metrics + 106-cell extension; amendment for unknown classes |
| D29 | 11 Oct 17:24 | user | "why 5 or 10%?": add 20/50/100% (P16); asked for all locked rules |
| D30 | 11 Oct ~17:30 | user (choice offered by Claude) | P16 CutMix setting picked on P13 **val** only ("Pick on P13 val") |
| D31 | 11 Oct 17:28–17:37 | Claude | P16 design: pool P6 seeds, external pool at 100%, train.py patch, automatic launcher |
| D32 | 11 Oct 21:05–21:11 | locked rule | CutMix = off; P16 SSL runs launched; flagged that test favoured CutMix/hard PL, nothing changed |
| D33 | 11 Oct 22:03 | user | build this handbook |
| D34 | 12 Oct ~01:15 | user | download the full E-SCDD, audit and analyse it, report in the handbook; also read the E-SCDD paper (done; doc 17) |
| D35 | 12 Oct ~04:40 | Claude (post hoc, disclosed) | P16 read under the locked rules (fails at all three fractions); added a without-`CSIR_00070_r8_c4` sensitivity check after seeing 4 failed runs; no rule changed; adopting it as a standing check left to the user |
| D41 | 24 Oct | user | "take the critics decisions, and go", with the max-score goal stated: Track D and Track M (added 30 Oct) |
| D42 | 24 Oct | critic C (locked rule) | MIM gated out after the frozen-encoder probe; judged too early by the 27 Oct team (added 30 Oct) |
| D43 | 25 Oct | locked rule (Track M) | FINAL = SUP100 5-seed ensemble, crack bias +0.75 (headline), bias 0 reported as the robust point (added 30 Oct) |
| D44 | 28 to 29 Oct | user; team-lead | the user's 100%-label question; team scout / runner / coach; the 5% screen copied from the 27 Oct synthesis (added 30 Oct) |
| D45 | 30 Oct ~10:45 | user | "why 5%?": stop the 5% screens (CP5 stopped unscored), test the pool at 100% labels (added 30 Oct) |
| D46 | 30 Oct ~10:25 to 11:12 | coach, diag, team-lead | protocol_100: 4 arms incl. SUP100-PF unconditional; DDeP100 and plain MIM100 dropped; APPROVED with G5 (added 30 Oct) |
| D47 | 30 Oct 11:12 | user | B1 label audit yes; B2 pool mining, candidates only; scuff as its own class (added 30 Oct) |
| D48 | 30 Oct 11:11 to 11:21 | coach, runner | CP100 excludes the 6 scuff-as-crack train cells; the star cell kept (added 30 Oct) |
| D49 | 30 Oct 11:13 to 11:18 | coach, team-lead | two protocol_100 test openings (15 fine-tunes, then CP100) with fixed conditions (added 30 Oct) |
| D50 | 30 Oct 12:04 to 12:10 | coach (post hoc gate amendment, disclosed) | gate 6b: a 4k decoy reading with 3 pre-stated GO conditions before any CP100 run (added 30 Oct) |
| K1–K8 | throughout | Claude / user | housekeeping: tmux, worktrees, REVISION, md5, GPU rules, watchers, commits |

---

## 1. Inherited decisions (before 7 Oct; from the handoffs, not re-verified)

These were made in phase 0 (lost) and phase 1 (up to 6 Oct). See `06_history_phase0_phase1.md` for the full history.

| # | Decision | Why at the time | What happened later | Source |
|---|---|---|---|---|
| H1 | Core model: SA U-Net++ ported to PyTorch, trained with Mean Teacher + **SemiCE** | Gangopadhyay's SA-UNet++ and the PV-S3 paper describe SemiCE | P2 (8 Oct) showed SemiCE is not a valid consistency loss. Every SemiCE Mean Teacher result is invalid. The SA gate gives no benefit (SA-SL-20 0.3399 vs SL-20 0.3435) | phase-0 doc; handoff 7 Oct §6.11; `results/p2/README.md` |
| H2 | Labelled batch 4 in every method (SL 4, SSL 4 + 4) | match labelled samples per step | Phase 1 called it "later regretted": BatchNorm sees 8 images in SSL arms against 4 in SL. That became the BN-mixing story (P11–P13) | handoff 7 Oct §5 (Oct 2), §10 item 3 |
| H3 | Match optimiser steps between SSL and SL | an 8× step mismatch had produced a fake +7.4 gain | kept as a standing rule | phase-0 doc; phase-1 §16 |
| H4 | Final-step weights are primary; best-val secondary | val is 54 images and best-val selection flips the sign of comparisons | kept. It also explains the old "SA SSL raised IoU" impression (a best-val artefact) | handoff 7 Oct §4.2; phase-1 answers item 1; session summary 2026-10-11T09:36Z |
| H5 | Never compare arms across machines | gaint and cv02 disagreed (e.g. SL-20-b8 0.346 vs 0.362) | kept. Enforced in every protocol from P6 on | phase-1 §16; handoff 7 Oct §6.3 |
| H6 | Port ALHVR following its **code** where paper and code disagree; drop plain CPS from the critical path | the user objected to CPS; the reference code has no CPS term | ALHVR equalled its loss-off control. Later found that its λ schedule barely switched the loss on under our optimiser, so it never had a fair test | handoff 7 Oct §5 (Oct 2), §9.1 |
| H7 | External 12k unlabelled pool parked on day one; SSL used the 383 hidden-label train cells | simplicity | Phase 1 admitted it "had become a weakness". The pool was prepared on 6 Oct and finally tested in P9–P12 | handoff 7 Oct §5 (Oct 6), §10 item 8 |
| H8 | Headline metric `defect_miou` = mean(crack IoU, inactive IoU); gridline excluded | gridline labels are noisy | replaced from P6 on by per-class metrics on revised labels (crack IoU, inactive IoU, crack relF1@2) | phase-1 §4–5; `protocols/P8_tolerant_pl_on_l3.md` |
| H9 | Goal order (phase 0): something WattCycle can pilot first, paper second | dual mandate (WattCycle and the advisor) | Phase 1 said it had "no record" of this order. Still unresolved; see `13_` (e) | phase-0 doc Part 2; phase-1 answers item 4 |

---

## 2. 7–8 Oct: restart, analysis first

### D1. Restart with analysis first (7 Oct, 23:37)
- **Who:** the user.
- **What:** stop running experiments and first analyse the datasets, models, issues and the metric mismatches against the papers. Be skeptical. The goal stays a method "inspired by ALVHR [ALHVR] to focus the rare classes".
- **Why (user's words):**
  - "i feel lost, coz it trained on 47 images and tested on sam e47, to get 0.3 iou on cracks, definitely dsomething wrong";
  - "i strongly doubt there are some bugs in the trainning(minor misconfigurations) causing the unlabelled losses having zero effect".
- **Outcome:** the 8 Oct situation report, the BenchmarkEL and UCF-EL data analyses, P1 and P2.
- **Source:** `docsrc/user_messages.md` (2026-10-07T18:07Z); `to_human/situation_report_2026-10-08.md`.

### D2. Direct SSH; three-part thesis; training methodology first (7 Oct, 23:55)
- **Who:** the user.
- **What:**
  - Use direct SSH to both servers with keys, not the Herald exec connectors suggested in the first message.
  - The thesis has three parts: (1) training methodology, (2) architecture, (3) real-time deployment (severity detection and others). Work on part 1 only for now.
  - Take time: "understand the situation, the dataset, the prblem more clearly and grounded, then ... find out the issues the existing paers in this fiedl are having".
- **Why:** "i feel i am doing withoug getting the context, like running before results without understanding the situation, not a reseacher supposed to do".
- **Outcome:** SSH allow-rules were added to `~/.claude/settings.json` (8 Oct). All later server work is direct SSH with `BatchMode=yes`.
- **Source:** `docsrc/user_messages.md` (2026-10-07T18:25Z, 19:07Z); session summary 2026-10-08T07:54Z §3.

### D3. Lock protocols before running (from 7–8 Oct, all experiments)
- **Who:** Claude, following the autoresearch skill's discipline. Kept by the user's later rules.
- **What:**
  - Every experiment gets a protocol in `protocols/`, committed before any run.
  - The protocol fixes the arms, metrics and decision rules.
  - Anything outside the rules is labelled EXPLORATORY.
  - Changes come only as dated amendments that say what had been seen.
- **Why:** past "gains" in this project came from comparison mistakes: step mismatch, val selection, metric conventions (phase-1 §13 "Meta-lesson").
- **Alternatives:** none were seriously considered.
- **Outcome:** P1–P16 all locked first. Some were chosen after seeing interim results, and this is disclosed (P8, P9, P10, P11, P12, P16).
- **Source:** first commit `f9708c0` (7 Oct 23:59); session summary 2026-10-08T07:54Z §2.

### D4. Hold the gaint external-pool queue (8 Oct, 01:18)
- **Who:** Claude proposed it. The user ran the hold command, because the auto-mode classifier blocked Claude from killing a process or editing the crontab ("Interfere With Workloads").
- **What:** stop the armed `extpool_20261007` Mean Teacher queue (external pool, `consistency: semi_ce`) from starting.
- **Why:** it would test SemiCE, which was under audit (P2). Running it would spend GPU hours on a loss that might be invalid.
- **Alternatives:** let it run and read it later.
- **Outcome:**
  - P2 confirmed SemiCE is invalid.
  - The queue has stayed held and untouched since. It is a standing constraint: "the gaint extpool queue stays held".
  - It can be relaunched with `bash scripts/resume_queues.sh extpool_20261007`.
- **Source:** `docsrc/user_messages.md` (2026-10-07T19:48Z, the user's bash line); session summary 2026-10-08T07:54Z §4, §7.

### D5. P1 and P2 first (protocols committed 7 Oct 23:59, `f9708c0`, whose header says "LOCKED ... 2026-10-08 00:15 IST"; the user approved at 00:37 on 8 Oct)
- **Who:** Claude proposed. The user: "add the ssh allow rules and run P1 and P2, till then ill read the literature part".
- **What:**
  - P1: an overfit check. Can the model fit crack on 10 of its own training images? Five arms separate loss, augmentation, labels and bf16.
  - P2: a SemiCE gradient probe on an existing Mean Teacher checkpoint.
- **Why:** these were the two cheapest tests of the user's two suspicions: "something wrong" with 0.3 crack IoU on training images, and "unlabelled losses having zero effect".
- **Outcome:**
  - P1: no pipeline bug. Augmentation is the main fitting cap (crack AP 0.93 without it, 0.59 with it). CE + Dice fits crack to 0.861.
  - P2: SemiCE's positive sets are incoherent (100% of pixels have ≥ 2 positive classes), so every SemiCE Mean Teacher result is invalid.
- **Source:** `protocols/P1_overfit_check.md`, `protocols/P2_semice_gradient_probe.md`, `results/p1/README.md`, `results/p2/README.md`; commits `fa373ed`, `771240a`, `d05091e`.

### D6. UCF-EL data analysis (8 Oct, 12:05)
- **Who:** the user ("do the same data analysis on UCF-EL").
- **Outcome:** `data_analysis/ucf_el_report.md` (commit `0deaf3c`).
  - The official code validates on test.
  - 25–44% of test cells have their physical twin in train.
  - UCF "crack" is a region class.
  - The label gap comes mostly from interconnect and corrosion.
- **Source:** `docsrc/user_messages.md` (2026-10-08T06:35Z); `to_human/situation_report_2026-10-08.md` §9.

### D7. UCF-EL needs a module-disjoint re-split before any label-efficiency claim (8 Oct)
- **Who:** Claude's conclusion; nothing was decided against it.
- **What:** do not use UCF-EL for SSL label-efficiency claims on its official split.
- **Outcome:**
  - The re-split was never done.
  - All later SSL experiments (P6–P16) are on BenchmarkEL.
  - UCF-EL is used only as a pretraining source (P15), with a near-duplicate check against BenchmarkEL val/test (maximum correlation 0.79).
- **Source:** `to_human/situation_report_2026-10-08.md` §9; `protocols/P15_ucf_encoder_transfer.md`.

---

## 3. 10 Oct: directions, mid-term experiments, overnight SSL

### D8. Two-hour directions scan (10 Oct, 09:29)
- **Who:** the user: "you got 2 hours, explore all the possible directions ... the papers ive insti access so scrap them using chorme and get the pdf, and report be brief markdown file".
- **What:**
  - 15 institutional PDFs were fetched through the user's Chrome profile. They are kept local and not redistributed (standing constraint).
  - 4 literature scouts plus 1 reader.
- **Outcome:** `to_human/directions_2026-10-10.md`, a ranked direction map (rows 0–9).
- **Source:** `docsrc/user_messages.md` (2026-10-10T03:59Z); commit `8614e10`.

### D9. P3 exploratory re-score, then P4 and P5 as locked offline probes (10 Oct, ~09:50–10:06)
- **Who:** Claude.
- **What:**
  - **P3 (no protocol, labelled EXPLORATORY):** re-score existing checkpoints on the revised E-SCDD labels.
  - **P4:** frozen-feature linear probe (ImageNet CNN vs random vs DINOv2).
  - **P5:** precision of rare-class pseudo-labels inside ALHVR's regions.
- **Why:** cheapest tests that decide direction rows 2, 3 and 6 without training.
- **Outcome:**
  - **P3:** the label version moves crack IoU by +0.05 to +0.07 for every model.
  - **P4:** ImageNet CNN features far exceed random (crack AP 0.33 vs 0.03). "Every future arm should start from an ImageNet (or in-domain MIM) CNN encoder."
  - **P5:** crack pseudo-labels are "right place, wrong pixel" (strict precision 0.27, relaxed 0.64 in Ω3).
- **Source:** `results/p3_label_versions/README.md`, `results/p4_feature_probe/README.md`, `results/p5_region_pl/README.md`; `to_human/directions_2026-10-10.md` §6.

### D10. Method hook: offset-tolerant targets plus per-class routing (10 Oct, ~10:00)
- **Who:** Claude, presented as "my pick; yours to decide".
- **What:** one offset-tolerant loss for human labels and pseudo-labels, with ALHVR-style per-class routing.
  - Fallback: tolerance-aware supervision plus MIM pretraining.
- **Why:**
  - P5: teacher crack pseudo-labels are 0.96 precise within 2 px but 0.59 pixel-exact.
  - Human labels have the same 1–2 px ambiguity (P1, P3).
- **Alternatives (direction map):** MIM pretraining (row 3), weak supervision (row 4), cross-dataset transfer (row 5), foundation-teacher distillation (row 6), synthesis (row 7).
- **Outcome:**
  - Became `tolerant_pl` (P7 onward).
  - Its supervised twin `tol_dice` was tested in P14: it recovers 0% of the label-noise gap.
  - Rows 3 and 5 were not run until P15 (row 5, as UCF transfer). The 11 Oct proposal draft calls this allocation "the main thing to correct".
- **Source:** `to_human/directions_2026-10-10.md` §1, §5; `to_human/proposal_reframe_2026-10-11.md` §2.

### D11. Two experiments for the mid-term: P6 and P7 (10 Oct, 11:22)
- **Who:** the user asked: "so what 2 experiments according to you will give the best results for presentation in 4 days? mid term ... what existed, what we done, what we propose, and further work". Claude picked.
- **What:**
  - **Exp 1 = P6:** a corrected supervised baseline ladder.
  - **Exp 2 = P7:** a pilot of the tolerant pseudo-label loss.
- **Why:** P6 fixes the ground (labels, augmentation, encoder, loss) before any SSL claim (direction row 0). P7 tests the method hook.
- **Outcome:**
  - Both ran on 10 Oct.
  - The mid-term date was assumed to be ~14 Oct. It was **never confirmed** (`to_human/midterm_deck_outline.md` §17).
- **Source:** `docsrc/user_messages.md` (2026-10-10T05:52Z); session summary 2026-10-10T09:17Z §1.

### D12. Parallelise on the servers with tmux, without affecting results (10 Oct, 11:38)
- **Who:** the user: "parallelize as much possible but making sure the results wont be affected, better use tmux on the servers, go".
- **What, decided by Claude under that instruction:**
  - one tmux window per run;
  - up to 3 runs per GPU;
  - all arms of one experiment on one hardware type (cv02 for P6);
  - one git commit deployed by `git archive`, recorded in `REVISION`;
  - data md5-checked across machines;
  - deterministic training, so co-location changes speed only.
- **Outcome:** written to memory (`server-runs-tmux-parallel.md`) and used for every later experiment.
- **Source:** `docsrc/user_messages.md` (2026-10-10T06:08Z); memory `server-runs-tmux-parallel.md`.

### D13. P6 design: revised masks and a one-change ladder (10 Oct, locked 11:42)
- **Who:** Claude.
- **What:**
  - Labels: E-SCDD revised masks (`data/labeled/masks_escdd`) for train, val, test and class weights.
  - Ladder at 10% labels, one change per step:
    - L0: old recipe (from-scratch U-Net++, strong augmentation, weighted CE);
    - L1: + label-safe augmentation;
    - L2: + ImageNet ResNet-34 (`smp_unetpp`);
    - L3: + CE+Dice.
  - Plus 20% and 100% points for L0/L3. 21 runs on cv02.
- **Why:** P1 (augmentation caps fitting), P3 (label version dominates), P4 (pretrained encoder). Fix the ground first.
- **Alternatives:** keep old labels (rejected: P3 showed they hide label effects).
- **Outcome:**
  - Label-safe augmentation helps crack robustly (+0.048 IoU).
  - L3 is the only recipe that turns more labels into better scores (crack IoU 0.396 → 0.471 from 10% to 100%).
  - AP saturates on L2/L3 (GT crack pixels scoring < 0.001: L2 19%, L3 42%).
- **Source:** `protocols/P6_corrected_baseline.md`; `results/p6/README.md`.

### D14. P7 base by locked rule = L0; P7 becomes a pilot (10 Oct, 15:43)
- **Who:** P6 rules 2 and 3, mechanically.
- **What:**
  - Rule 2 picked the 10% arm with the best val AP: L0 (0.480).
  - Rule 3 then found L0 has no headroom: pooled AP 10% → 100% is −0.001 < 0.02.
  - So P7 (on L0) is reported as a pilot.
- **Note:** an interim split-mean figure of +0.026 was first reported, then corrected to the literal pooled value.
- **Source:** `results/p6/README.md` (Rule 2, Rule 3); session summary 2026-10-10T15:56Z §4.

### D15. P8: the same arms on L3; primaries changed to IoU/IoU/relF1@2 (10 Oct, locked 15:43, before any P8 run)
- **Who:** Claude. Disclosed as a post-hoc base choice.
- **What:**
  - Run P7's arms (A, B hard PL, C tolerant PL, D loss-off) on L3, the base with a label gap.
  - Change the primary metrics from AP to test crack IoU, inactive IoU and crack relF1@2, because AP on L3 is dominated by saturated pixels.
- **Why:** SSL can only close a gap that exists (P6 exploratory 2). AP is not comparable across recipes (P6 exploratory 1).
- **Alternatives:** stop at P7 (pilot only).
- **Outcome:**
  - No unlabelled loss passes against loss-off.
  - Key side finding: the loss-off Mean Teacher control is **below** plain supervised (crack −0.013, inactive −0.101, both robust over cells).
  - This drove P11–P13.
- **Source:** `protocols/P8_tolerant_pl_on_l3.md`; `results/p8/README.md`.

### D16. Launch P8 immediately, co-located with P7 (10 Oct, 17:14)
- **Who:** the user: "what we have now? if the resources are free, we can fasten up and do things efficiently". Claude took this as approval.
- **Context:** an auto-start waiter for P8 was earlier denied by the auto-mode classifier ("Shared Cluster Mutation"), so Claude stopped and asked.
- **Outcome:**
  - P8 ran 17:15–23:53 alongside P7.
  - Claude later corrected its own claim that co-location was "nearly free": P7 slowed once P8's loss ramped up.
- **Source:** `docsrc/user_messages.md` (2026-10-10T11:44Z); session summary 2026-10-10T15:56Z §1, §4.

### D17. P9 external pool; overnight SSL on all resources (10 Oct, P9 drafted 22:31, the user approved 22:53)
- **Who:**
  - Claude proposed P9 in answer to "status? ... room for another useful experiment? ALVHR unlabelled loss gave anything?" (22:26).
  - The user: "go for p9 THEN, WE NEED TO FOCUS ON THE ssl AS WELL, NIGHT LONG WORKS FOR IT, USE ALL RESOURCES LIKE EXPLOIT ALL OF THEM, CV02, GAINT ALL OF THEM".
- **What:** P8's arms with the 11,938-cell external pool (Bx, Cx, Dx), 3 seeds, cv02.
- **Why:** interim P7/P8 nulls might come from the small pool (431 cells). ALHVR-style methods report 10–100× larger pools. Chosen after seeing interim numbers (disclosed).
- **Outcome:**
  - Cx − Dx passes on inactive (+0.056), but it is not robust over cells.
  - Pool-size effect ≈ 0.
  - Swapping the pool moves the loss-off control (Dx − D inactive +0.094), which is evidence of batch mixing.
- **Source:** `protocols/P9_external_pool.md`; `results/p9/README.md`; `docsrc/user_messages.md` (2026-10-10T16:56Z, 17:23Z).

### D18. P10 at 5% labels; B5 by amendment; gaint supervised references (10 Oct, 22:56 and 23:04)
- **Who:** Claude, under the overnight approval.
- **What:**
  - SSL at 5% labels (23 cells) with in-domain (455) and external pools.
  - B5 (hard PL) added by amendment before any B5 run.
  - gaint runs supervised L3 references at 5% and 50% (A5, A50), "reference only, never in a rule", because gaint is different hardware.
- **Why:** SSL gains usually grow as labels shrink. Chosen after interim P7/P8 numbers (disclosed).
- **Outcome:**
  - No loss passes.
  - Seed 2 collapses under both hard and tolerant PL (`rare_frac` 0.001–0.002 vs 0.007–0.009).
  - The external pool hurts crack on its own sources (−0.065 on CSIR+ARTS).
  - Inactive is in only 2 of the 23 labelled cells.
- **Source:** `protocols/P10_ssl_5pct.md`; `results/p10/README.md`.

### D19. Fix the queue race; one queue per machine, chained (10 Oct, ~23:00; rule written to memory)
- **Who:** Claude.
- **What:**
  - Two GPU queues polling "GPU free" raced. The main queue would have waited ~6 h.
  - Claude killed both queue loops (its own), launched two runs directly and started one combined queue.
  - New rule: chain queues (wait for "queue empty", then ~5 min), one queue per machine.
- **Source:** session summary 2026-10-10T19:37Z §4; memory `server-runs-tmux-parallel.md`.

---

## 4. 11 Oct: matched pipeline, audit, one-day push

### D20. P11: a matched labelled view (11 Oct, locked 00:11)
- **Who:** Claude. A post-hoc design, disclosed.
- **What:** opt-in switch `ssl.labeled_aug=supervised` (commit `24590fb`). Labelled images in Mean Teacher get exactly the supervised arm's augmentation.
  - Arms Dm, Cm (in-domain), Dmx, Cmx (external), 10%, 3 seeds.
  - New rule 3: "SSL beats supervised", credited only if rule 2 ("loss helps") also holds.
- **Why:** P8's D < A. The student equalled the teacher, so the EMA was not the cause. Remaining candidates: the stronger labelled view, BN mixing, data streams.
- **Outcome:**
  - The matched view removes most of the handicap (Dm − A crack −0.007, inactive +0.000).
  - Cm passes rule 2 (inactive +0.071, relF1@2 +0.018) and rule 3 vs supervised.
  - Cm − A inactive is not robust over cells.
- **Source:** `protocols/P11_matched_pipeline.md`; `results/p11/README.md`.

### D21. P12: matched pipeline at 5%, a cv02 supervised A5c, gaint replication and calibration (11 Oct, locked 01:37)
- **Who:** Claude.
- **What:**
  - cv02 arms A5c, Dm5, Cm5, Dmx5, Cmx5 (3 seeds).
  - gaint gDm5/gCm5 with fresh seeds 3–5 (replication, descriptive, can never rescue a failed cv02 rule).
  - gaint gA10 for calibration.
- **Why:** P10's A5 ran on gaint and could not enter a rule. The 5% setting has the largest label headroom. The gaint A5 numbers had been seen when locking (disclosed).
- **Outcome:**
  - Cm5 − Dm5 passes on crack (+0.023), replicated on gaint.
  - Cm5 − A5c **fails** on cv02 (+0.006).
  - gaint's gCm5 − A5 passes the arithmetic, but gaint has no vote.
  - Dm5 − A5c crack −0.017 is a robust handicap.
  - Calibration: gaint ≈ cv02 on crack (+0.004); inactive differs by about the seed spread.
- **Source:** `protocols/P12_matched_5pct.md`; `results/p12/README.md`.

### D22. The "supervised beating SSL" audit, and P13 (11 Oct, the user at 11:24; P13 locked 11:51)
- **Who:**
  - The user: "cant believe bro, supervised beating ssl, hows that possible, so many papers showed it, we doing something wrong? be skeptical, work like 11years experienced ... even earleir I tried in the SA SSL unetpp which had raised the iou, seems contradicting".
  - Claude audited and designed P13.
- **Audit finding:** no implementation bug in the Mean Teacher step. Checked:
  - shared geometry between views;
  - EMA covers BN buffers;
  - teacher detached and in eval mode;
  - evaluated weights are the teacher's;
  - no unlabelled/test overlap.

  The old "SA SSL raised IoU" was a best-val checkpoint artefact.
- **Two design gaps against published SSL:**
  - (1) weak perturbation, no CutMix; the unlabelled loss stayed ~10× below supervised;
  - (2) unlabelled images share the student's BatchNorm batch.

  A BN-recalibration diagnostic showed the handicap is in the trained weights, not in the evaluation statistics.
- **What:**
  - `ssl.student_forward=separate`: the unlabelled forward runs inside `frozen_bn_stats`. With λ = 0 the student is bit-identical to supervised.
  - `ssl.cutmix_p=0.5` (commit `bac5264`).
  - Arms Ds/Cs/CsM/BsM at 5% and 10%, plus gaint replication (original lock).
- **Outcome:** see D26 (amendment) and D32 (result).
- **Source:** `docsrc/user_messages.md` (2026-10-11T05:54Z); `protocols/P13_cutmix_separate_bn.md` "Why this exists"; `results/p13_audit/`; session summary 2026-10-11T09:36Z §5.

### D23. "Gather questions and ask"; launches on hold (11 Oct, ~12:16–12:46)
- **Who:** the user, mid-turn: "even if youve questions, gather them all and ask ill answer, rather preassuming anything". Also "naah, about the older work, ask me if anything you need to know that wasnt in the context".
- **Context:** the user pasted the phase 0 and phase 1 handoffs (12:16) and later the phase-1 answers (12:32), asking to "revisit our approach ... how would you classify the problem, what would be your goal, approach".
- **What:**
  - Claude had already locked and queued P13 on its own.
  - It then put launches on hold behind a GO file and asked a batch of questions.
  - New standing rule (memory `ask-before-assuming.md`): batch questions, hold launches, never act on an assumption.
- **Source:** memory `ask-before-assuming.md`; session summary 2026-10-11T09:36Z §1, §4; `docsrc/user_messages.md` (06:53Z); the pastes of 06:46Z and 07:02Z are in `sources/chat/phase0_phase1_handoffs_pasted_2026-10-11.md`. The "gather them all" quote is only in the session summaries (a mid-turn message, not in the extract).

### D24. Proposal re-framed from the evidence (11 Oct, 12:37, draft)
- **Who:** Claude, in answer to "revisit our approach".
- **What:** `to_human/proposal_reframe_2026-10-11.md`.
  - The problem is classified as "thin-structure and region segmentation, from few labels with imprecise geometry ... whose real output is a measurement", not mainly an SSL problem.
  - An effect-size budget: label version and recipe ≫ label count ≫ unlabelled loss.
  - Goals O1–O4.
  - Experiments E1–E6, ordered by information per cost.
- **Outcome:** the user's answer (D25) made framing conditional on final results. The draft must be reworded neutrally once results are in. Not done as of 13 Oct: Claude left it for the user, since any rewrite implies a framing (doc 15 §2).
- **Source:** commit `90ee4bb`; `to_human/proposal_reframe_2026-10-11.md`.

### D25. The user's eight answers (11 Oct, 12:46)
Verbatim, with the question each answered (from session summary 2026-10-11T09:36Z):

| # | Question (paraphrased) | Answer | Effect |
|---|---|---|---|
| 1 | Proposal framing | "framing depends on final results, no presumptions, ever" | No framing is chosen before the results; the evidence table decides |
| 2 | cv02 allocation | "your call, wiser" | Claude allocated (P13, P14, P16 on cv02) |
| 3 | gaint allocation | "again ur call" | gaint got P15 instead of the P13 replication |
| 4 | Extended test set / full E-SCDD | "conside rit" | E1's 106-cell extension was built. The full E-SCDD download was **not** done (the answer was read as ambiguous). The user asked for it explicitly on 12 Oct (D34); it is now downloaded and audited, but not used for training or scoring |
| 5 | WattCycle data | "none" | No customer data; all results are on public data |
| 6 | Time budget | "youve 1 day for the work then ill startr on ppt" | One-day push. P13 cut to 5% (D26) |
| 7 | Model size limit | "not a constraint even 5M works" | The 26M `smp_unetpp` stays the base; the small-model goal (O4) is not a constraint now |
| 8 | Power loss | "will work on that later, not part of this project unless we get some valid data" | Power-loss estimation is out of scope |

- **Source:** `docsrc/user_messages.md` (2026-10-11T07:16Z); session summary 2026-10-11T09:36Z §1.

### D26. P13 Amendment 1: 5% only, 5 vs 5 seeds, Ds5 dropped, gaint to P15 (11 Oct, 12:51, before any P13 run)
- **Who:** Claude.
- **What:**
  - Drop the 10% arms. Supervised crack gains only +0.002 from 10% to 20%, so there is little crack headroom.
  - CsM5 gets seeds 0–4. Two new supervised seeds (`p13_A_5pct` s3–4) are pooled with P12's A5c s0–2.
  - BsM5 and Cs5 keep 3 seeds.
  - Ds5 is dropped: with the separate forward and λ = 0 its student is bit-identical to supervised (verified for 100 steps on GPU). A5c is therefore the loss-off control, and rules 2 and 3 become one contrast.
  - The EMA-only effect is no longer measured (disclosed).
  - No gaint replication.
- **Why:** the user's one-day deadline (D25.6), their standing rule of ≥ 5 seeds for effects < 0.05, and GPU time for P14/P15.
- **Outcome:** primary claim CsM5 − A5c, 5 vs 5 seeds.
- **Source:** `protocols/P13_cutmix_separate_bn.md` Amendment 1; commit `8622f67`.

### D27. P14 and P15 added (11 Oct, locked 12:55, before any run)
- **Who:** Claude, under "your call" (D25.2/3).
- **What:**
  - **P14 (cv02):** does an offset-tolerant *supervised* loss (`tol_dice`, R = 2) recover the old-vs-revised label-noise gap? Directions row 1, proposal E2.
  - **P15 (gaint):** does a ResNet-34 encoder pretrained on UCF-EL's 9,562 labelled cells beat the ImageNet encoder at 5% and 10%? Rows 3 and 5, proposal E3.
- **Why:** the effect-size budget (D24). These rows had been rated strong and cheap but were never run.
- **Outcome:**
  - **P14:** gap +0.082 crack IoU; tolerance recovers 0%. On revised labels, inactive +0.037 passes the rule but is not robust over cells.
  - **P15:** done 11 Oct 22:26 IST. gU5 n.d. on all three; gU10 worse on all three, robust over cells (`results/p15/README.md`).
- **Source:** `protocols/P14_tolerant_supervision.md`, `protocols/P15_ucf_encoder_transfer.md`; commit `c9f5562`; `results/p14/README.md`.

### D28. E1 per-cell metrics and the 106-cell extension (11 Oct, definitions 12:59; first pass and amendment 13:16; v2 rescoring 14:03. The README header says ~14:00 and ~14:15)
- **Who:** Claude. Proposal E1; the "conside rit" answer (D25.4).
- **What:**
  - Fix per-cell task metrics before scoring: crack tolF1@2, length error, false alarm; inactive area error, detection F1, cell IoU.
  - Add 106 cells from BenchmarkEL release `20221008` that are in neither our 582 nor the external pool. They come from 67 modules, only 1 shared with ours.
- **Amendment:** the release has 4 defect classes our taxonomy lacks (25–28). The first pass mapped them to background. They are now ignored. This fix was prompted by first-pass numbers and is disclosed.
- **Outcome:**
  - Per-cell crack metrics are not more sensitive than pooled IoU, so pooled stays primary.
  - Inactive cell IoU is more sensitive.
  - Every model loses most of its crack performance on unseen modules (L3 100% crack IoU 0.471 → 0.152).
- **Source:** `results/e1/README.md`; commits `21b5a8f`, `f9ea897`, `c3d9b01`, `8e2c3ed`.

### D29. "Why 5 or 10%?": add 20/50/100% (P16); list the locked rules (11 Oct, 17:24)
- **Who:** the user: "okay why we using 5 or 10% for ssl? they are really low and on phase0 as well they gave bad results, try 20, 50 and 100 of the 592 images ig, correct me if i am wrong, and can you for once tell me all the locked rules, i things we self sabotaging our project in a way...".
- **What Claude answered (summary):**
  - **The correction:** the dataset has 582 labelled cells, not 592. Fractions are of the 478 train cells.
  - **All locked rules, R1–R8:**
    - R1: Δ > max(0.01, 2·√((sd_A² + sd_B²)/3)) on ≥ 1 primary, none worse;
    - R2: the loss helps;
    - R3: SSL beats supervised, only if R2;
    - R4: width check;
    - R5: gap closed;
    - R6: gaint descriptive;
    - R7: bootstrap and top-3 reported;
    - R8: lock before runs.
  - **An honest assessment:**
    - The rules are lenient (≈ 2 SE, one-sided p ≈ 0.06).
    - The design hurt us in five ways:
      1. the 5–10% regime (inactive is barely measurable);
      2. the joint-BN handicap;
      3. 3 seeds;
      4. an untuned SSL recipe against a laddered supervised recipe;
      5. a small in-domain pool and a mismatched external pool.
- **Decision:** P16 adds supervised references (Part A, locked first) and SSL arms (Part B) at 20%, 50% and 100%.
  - At 100% there is no in-domain unlabelled data, so the SSL arm uses the external pool.
- **Source:** `docsrc/user_messages.md` (2026-10-11T11:54Z); session summary 2026-10-11T13:25Z §1, §2, §5; `protocols/P16_label_fraction_curve.md`.

### D30. CutMix setting for P16 chosen on P13 validation only (11 Oct, ~17:30)
- **Who:** the user chose "Pick on P13 val (Recommended)" from Claude's question.
- **What:** P16's SSL recipe is P13's Cs or CsM, whichever scores higher on P13's **val** set.
  - Score = mean over the three primaries of the seed means; CsM5 s0–4 vs Cs5 s0–2.
  - P13 test numbers are never used.
- **Why:** choosing on test would contaminate P16. Val keeps it clean.
- **Alternatives:** CutMix fixed on; CutMix fixed off; wait for the user after P13 (would idle GPUs overnight).
- **Outcome:** CUTMIX=0 (D32).
- **Source:** session summary 2026-10-11T13:25Z §1; `protocols/P16_label_fraction_curve.md` Amendment 1.

### D31. P16 design details (11 Oct, Part A 17:28; Amendment 1 17:35; auto-launcher 17:37)
- **Who:** Claude.
- **What:**
  - **Pool P6's supervised seeds 0–2 with new seeds 3–4 at 20% and 100%.** The configs are identical except seed and fraction (checked by diff), and the supervised path is unchanged from `824fab0` to `bac5264`. A50 gets 5 new seeds.
  - **Patch `train.py` (commit `d51b60f`).** It refused SSL at `labeled_fraction` 1.0; the patch allows it only with `data.unlabeled_pool=external`, with 3 new tests.
  - **`p16b_auto.sh`.** It waits for P13 and the Part A queue, writes `selection.txt` from val only, then queues the 15 SSL runs (5 seeds each of S20, S50, Sx100) at 3 per GPU on free GPUs. This takes the selection out of human hands.
- **Source:** `protocols/P16_label_fraction_curve.md`; `scripts_cv02/p16b_auto.sh`; commits `0d7374c`, `71ccf31`, `3ed328a`.
- **Note:** the protocol text dates the user's prompt "~16:35" and Part A's lock "~16:50". The transcript timestamp of the prompt is 17:24 and the commit is 17:28. The order (prompt → Part A lock → first run 17:28:55 → Amendment) is the same either way. This log uses the transcript and git times.

### D32. P13 result; CutMix off by val; P16 SSL launched; no change made (11 Oct, 21:04–21:11)
- **Who:** the locked rules; Claude reported.
- **What:**
  - P13 val: CsM5 score 0.3507 vs Cs5 0.3652, so CUTMIX=0.
  - P16's 15 SSL runs launched at 21:05 on GPUs 0, 3, 4, 5 and 6 in one wave (ETA ~03:00–04:30 12 Oct).
  - P13 test (later): CsM5 − A5c **passes** (inactive +0.117, crack relF1@2 +0.033).
  - Secondary on test: hard PL + CutMix (BsM5) is best on crack (+0.036 vs A5c), and tolerant is worse than hard under CutMix (−0.022).
  - So P16 runs the recipe that was weakest on crack in P13's test.
- **Decision:**
  - Keep the locked choice.
  - Claude told the user that a BsM-style arm at 20%/50% would be a test-informed choice, so it could only be exploratory, and would need their go-ahead.
- **Source:** `results/p13/README.md`; `el_p16/reports/p16b/selection.txt` on cv02; commit `636952b`.

### D33. Build this handbook (11 Oct, 22:03)
- **Who:** the user: "create a folder/use exsiting one for docs, I need to discuss this project and understand it from scratch, from zero to one ... make sure you miss nothing".
- **Source:** `docsrc/user_messages.md` (2026-10-11T16:33Z).

### D34. Download and audit the full E-SCDD; read its paper (12 Oct, about 01:15–02:30 IST)
- **Who:** the user: "download the full ESCDD data, audit it analyse it, report it in the handbook, with precise details", then "also look at the E SCDD dataset paper it might give useful insights".
- **What Claude did:**
  - Downloaded HF `snt-ubix/escdd` (903 image/mask pairs, 1,810 files), its mirror `shivahanifi/extended-scdd` and BenchmarkEL `20221008`/`20220723` (originals). All files were verified by hash.
  - Read arXiv 2511.09604.
  - Audited contents, labels, splits, duplicates and the relation to our data. Nothing was trained or scored.
  - Only read-only copies were taken from gaint.
- **Outcome:**
  - E-SCDD crack and inactive labels = BenchmarkEL `20221008`'s, so the revised-label effect is BenchmarkEL's own correction.
  - The release differs from the paper: 903 vs 1,000 labelled; 93 synthetic in train.
  - 100 of 117 new cells are in our external pool.
  - E-SCDD's test is unusable with our split.
  - The P3/F04 "conflict" is resolved, and the 583rd `masks_escdd` entry is a README.
  - Whether to use the extra cells is left to the user.
- **Source:** `results/escdd_audit/README.md`; `literature/notes/A09_hanifi2025_escdd.md`; `17_escdd_dataset_audit.md`.

### D35. P16 read; a post-hoc check for one noisy test cell (12 Oct, about 04:25–05:30 IST)
- **Who:** Claude, under the standing plan (D31, D32). No user input since D34.
- **What happened:**
  - The watcher fired at 04:25 IST: all 15 SSL runs rescored, rc = 0.
  - `scripts/post_p16.sh` ran on cv02 GPU 0, which was idle.
  - The locked rules gave n.d. for S20, S50 and Sx100 against supervised.
- **What Claude added, after seeing the results:**
  - Four runs had test crack precision near 0.5 with normal val. Per-cell counts traced all four to `CSIR_00070_r8_c4`, the noisiest of the 582 cells.
  - Claude added `scripts/p16_excell.py` (the rule arithmetic without that cell) and `scripts/cell_noise_rank.py`.
  - A read-only diagnostic on cv02 confirmed the failing models are confident and the result is the same in bf16 and fp32.
- **What was not done:**
  - No rule was changed, and the verdict uses the locked numbers.
  - The without-cell numbers are labelled post hoc everywhere.
  - Whether to adopt the check going forward is left to the user (doc 15, decision 2b).
- **Outcome:**
  - The verdict is the same with and without the cell.
  - The same cell explains most of P6's secondary L1 − L0 crack IoU gain (doc 08 correction).
- **Source:** `results/p16/README.md`; `13_problems_pitfalls_open_issues.md` A11.

## 4b. 13 Oct: a follow-up session after the close

### D36. DCA vs SKCDF; P17 and BsM5 seeds 3–4 (13 Oct, ~01:30–01:51 IST)
- **Who:** the user asked; Claude recommended; the user approved.
- **The ask:** "how about we try the DCA paper and SKCDF? we still have 16hrs for experimenting, is there anything more important left" (same message as D37).
- **Claude's recommendation** (5 questions, each with a default):
  - Skip DCA: a 3D method built on three expert decoders and a head/medium/tail class split, with little to split for two focus classes, and too large to build and test in 16 h.
  - Take SKCDF's one component with the largest ablation credit (data-flow decoupling, +12.74 of +19.61 Dice) and test it on BsM5, the strongest SSL recipe. Score the teacher as primary and the unlabelled decoder as secondary.
  - Give BsM5 its seeds 3–4 first: its crack gain (+0.036) was below 0.05 on 3 seeds, against the ≥ 5-seed rule.
  - Put the deck and framing first, experiments in the background.
- **The user:** "cool, go with ur calls" (~01:45 IST).
- **What followed:** P13 Amendment 2 (commit `9d6fcdd`, 01:46) and the P17 protocol (`5919560`, 01:51) were locked before their runs; code `f2f20d3` in a new gaint worktree `el_p17`; 7 runs on cv02 01:55–04:08 IST.
- **Not considered further:** the full SKCDF (cross-attention, balanced heads, λ_u = 10), any tuning, a gaint replication.

### D37. Copy cv02's checkpoints to gaint (13 Oct, 01:37–16:33 IST)
- **Who:** the user: "we gotta move the trained models bck in gaint, cv02 restsart will delete them".
- **What:** everything under cv02 `/tmp/noob_el` except data and `.venv` copied to gaint `/home/noob/work/cv02_noob_el/`, then checked by file manifest and MD5 (pass 1: 373 checkpoints; pass 2 for P17 and BsM5 s3–4: 616 files, 18 checkpoints). cv02 was left untouched.
- **Route:** relayed through the user's laptop. cv02 and gaint cannot log into each other, and cv02's login is shared by many lab members, so Claude did not forward an ssh agent or place a key there. A direct key needs the user's explicit OK.
- **Snag:** a session drop cut pass 2 short at 07:57 IST; it was redone and re-verified at 16:28–16:33.
- **Source:** `15_status_remaining_work.md` §1c; memory `cv02-shared-account-backup.md`.

### D38. P17 and Amendment 2 read; nothing more launched (13 Oct, ~08:00 IST)
- **Who:** the locked rules; Claude reported.
- **What:**
  - P17 rule 1, BsD5 − BsM5: n.d. on all three primaries (thresholds about 40% of BsM5's gain). BsD5 − A5c passes on all three.
  - BsM5 on 5 seeds: − A5c still passes (+0.029 / +0.107 / +0.045). P13 rule 5 (CsM5 − BsM5) turns from "tolerant worse on crack" to n.d.
  - The without-noisy-cell check changes no P17 verdict.
- **Decision:** report as locked, label the post-hoc parts, and launch nothing else; the remaining hours go to the deck, which is the user's call.
- **Source:** `results/p17/README.md`; `results/p13/README.md` "Amendment 2"; commit `239abd6`.

---

### D39. Follow-up checks and P18 (13 Oct, ~17:25–20:00 IST)
- **Who:** Claude, under the user's "youve got 3hrs to wrap up ... experiment whatever you think useful".
- **What:**
  - descriptive checks: EMA teacher vs student (D-level answer to doc 13 C11), the qualitative panel, our models in Pratt 2023's convention;
  - P18, exploratory: the BsM recipe at 10% (3 seeds) and 20% (5 seeds), the one open experiment that bore on the deck (doc 15 §3 decision 2). Locked 17:31 IST (`a698ec8`) before any run.
- **Outcome:** P18 inactive passes the arithmetic at 10% and 20%; crack n.d. (without the noisy cell: passes at 10%, just below at 20%). No locked verdict changes.
- **Source:** `results/p18/README.md`, `results/ema_check/README.md`, `results/qualitative/README.md`, `results/pratt_compare/README.md`.

---

### D40. Reproduce Hanifi 2025 (14 Oct, ~08:33–09:00 IST)
- **Who:** the user ("reproduce hanifi 2025, asap"; then "use the researchmcp connector to get the paper then, no presumptions").
- **What:** Claude read the paper first (ORBilu copy; the Research MCP had no full text), then asked three questions. The user chose the release split, the code as released (no augmentation), and 6 models + VGG16-UNet seeds 1–2.
- **Why those questions:** the paper's 551/67/77 split and 4× augmentation are not released.
- **Outcome:** P19, `results/p19/README.md`.

---

## 4c. 24 to 30 Oct: agent teams, the best model, feature learning and the move to 100% (added 30 Oct)

Additive section, written 30 Oct ~12:00 IST from `SESSION_RECORD_2026-10-21_to_27.md`, `SESSION_RECORD_2026-10-28_to_30.md`, `team_2026-10-24_go/README.md` and `team_2026-10-29_features/log.md`. "team-lead" is the user's main Claude session, which orchestrates the agent teams. The 21 to 23 Oct team decisions (data decisions D1 to D7 of `team_2026-10-21/data/decision.md`, SK1, AL1) are in doc 10.

### D41. "Take the critics' decisions, and go" (24 Oct)
- **Who:** the user, after the why-SOTA team's synthesis (doc 18 §W).
- **What:** run the critic's ranked directions (Track D) and build the best-scoring model (Track M). The user's goal, verbatim: "highest scores, a model which captures almost all of the cracks, inactive and other important defects balancing the miou for other classes as well" (`team_2026-10-24_go/README.md`).
- **Also accepted by this:** the 3-seed-per-draw design of the labelled-set experiment (a deviation from the ≥ 5-seed rule).
- **Outcome:** Track D and Track M (doc 18), critic-verified, committed `6c50baf` and `b04cad3`.

### D42. MIM gated out on the frozen-encoder probe (24 Oct)
- **Who:** critic C, by the locked probe rule.
- **What:** frozen ImageNet ResNet-50 and ConvNeXt-T passed the BMRK crack-AP bar, so the encoder route went to Track M (R3), and MIM (direction 7) was gated out.
- **Later:** the 27 Oct team judged this too early as a test of the user's question and ranked one bounded MIM test (doc 18 §U). MIM5 ran 29 to 30 Oct (D44).

### D43. FINAL by the locked protocol (25 Oct)
- **Who:** the locked `protocol_final.md` rule (Track M designer MD, critic MC).
- **What:** no ladder rung passed val inclusion, so the recipe is SUP100. FINAL is its 5-seed mean-softmax ensemble with a +0.75 crack bias chosen on val. Bias 0 is reported beside it as the robust operating point, after the noisy-cell fragility.
- **Outcome:** clean crack IoU 0.492 (doc 18 §M7; doc 11 row 18).

### D44. The user's question, the team, and the 5% screen (28 to 29 Oct)
- **Who:** the user (question, team shape); team-lead (the 5% choice).
- **What:**
  - 28 Oct: does learning features from the ~11.7k unlabelled cells, without labels, improve the model trained on all our labels?
  - 29 Oct ~12:30: launch a researcher, an executor and a practical critic; the lead only orchestrates. Team `scout` / `runner` / `coach`.
  - The methods (MIM5, AM, DDeP5, CP5) were screened at 5% labels. This was copied from the 27 Oct synthesis without checking it against the question (doc 13 C14).
- **Outcome:** MIM5 and DDeP5 n.d., AM killed, CP5 stopped (doc 19 §2, §3).

### D45. Stop the 5% screens; test the pool at 100% labels (30 Oct ~10:45)
- **Who:** the user: "why 5%? I asked about adding the pool to 100% labels."
- **What:** all 5% work stops. CP5 stopped at 10:50 IST with s0/s4 mid-run and s2 cancelled; it is not scored and no test was opened. Everything moves to 100% labels.
- **Why:** a 5% null need not carry to 100%; it depends on the method. At 5% the defect classes are too scarce. `diag` then showed the rule holds only for methods that do not consume labels and when the 5% estimate is tight; 100% is also better powered (doc 19 §5).
- **Also:** saved as feedback memory: pool ideas are tested on top of 100% labels unless the user asks otherwise.

### D46. protocol_100 design (30 Oct ~10:25 to 11:12)
- **Who:** coach (settings, `coach_100.md`), `diag` (analysis), team-lead (accepted coach's settings in full); coach APPROVED v1 (`review_100_v1.md`).
- **What:**
  - Four arms on gaint, 5 seeds each: SUP100-g, SUP100-PF, MIM100-PF, CP100 (doc 19 §7).
  - SUP100-PF runs unconditionally (diag's and coach's advice), because MIM100-PF − SUP100-g would mix the init and the optimizer change.
  - Dropped: DDeP at 100% and plain MIM100.
  - Gate G5 added at approval: PF smokes to 4k with layer3/4 cosine ≥ 0.8, fallback lr_mult 0.03, then stop.
  - All on gaint because cv02 had 0 of 8 GPUs free at 10:51.
- **Why PF:** coach's encoder-erasure measurement (doc 19 §4).
- **Outcome:** v1.1 (md5 8dcb231b) records the gates: identity gates IDENTICAL (re-diffed by coach), G5 PASS (lr_mult 0.1 kept), no 4th lane, gate 6 FLAG (D50). The 15 fine-tunes launched 12:05:34 IST on gaint.

### D47. B1 audit, B2 mine only, scuff as its own class (30 Oct 11:12)
- **Who:** the user, answering team-lead (relayed in `log.md` 11:12 and the session record §1).
- **What:**
  - **B1:** yes to the free out-of-fold label audit of train. Sheets delivered 11:37.
  - **B2:** mine the pool for half-cut / scuff candidate cells only; whether to pixel-label 20 to 40 of them is decided later.
  - **Scuff:** train it as its own class (B3, `spec_b3_scuff.md`), after protocol_100.
- **Also that hour:** the user asked coach to lead as a scarce-data expert (`coach_strategy.md`); `diag` was shut down at the user's request (11:37).
- **Still open:** for B3, keep test GT for the verdict (coach's recommendation) or also report a version with the 236 scuff px ignored (doc 15 §3b).

### D48. CP100 excludes scuff-as-crack cells (30 Oct 11:11 to 11:21)
- **Who:** coach (finding and ruling), runner (verification on gaint).
- **What:** the 6 train cells whose E-SCDD scuff is labelled crack are excluded from the CP100 paste library, with the 7 D7 twins: 13 stems, md5 903293c9. The star cell `CFVS_00024_r3_c3` stays in the library (meaning undefined, 0.04% of library px) and on the review list.
- **Why:** CP100 would otherwise paste scuff streaks as crack onto pool cells.
- **Outcome:** the frozen v1.1 library has 554 components, 151,039 px from 465 cells (566 / 151,993 before this exclusion; kept-list md5 a326dffd).

### D49. Two test openings for protocol_100 (30 Oct 11:13 to 11:18)
- **Who:** coach ruled yes on early scoring; runner staged it "(coach + team-lead)" (`log.md` 11:13, 11:18). The sources do not say whether the user asked for it.
- **What:** opening 1 = the 15 fine-tunes (~01:00 IST 31 Oct); opening 2 = CP100 at the end (~07:30 IST 31 Oct), reusing SUP100-g's opening-1 files unchanged (md5-checked).
- **Conditions:** CP100 runs to completion whatever opening 1 shows; no protocol_100 change after opening 1.
- **Note:** `protocol_100.md` v1 and the first review said one scoring pass; v1.1 (12:02 IST) pre-registers the two openings. v1.1 ETA: opening 1 about 00:00 to 01:00 IST 31 Oct; opening 2 (if CP100 runs) about 07:00.

### D50. Gate 6b: one more decoy reading before CP100 runs (30 Oct 12:04 to 12:10)
- **Who:** coach, after gate 6 flagged; a post hoc amendment of gate 6, disclosed as such (`review_100_v1.md`, "Gate check and gate-6 ruling"). team-lead had asked whether the 2× relative line still makes sense at 100%.
- **What:** gate 6 flagged on the ratio only: CP decoy 0.0076 vs SUP 0.0031 (2.45×), both far below the 0.05 absolute line. Coach ruled: resume both smokes from 2k to 4k and rerun the same decoy. CP_GO only if, at 4k, CP decoy ≤ 0.05, and (≤ 2 × SUP decoy or ≤ 0.0094), and decoy/real ≤ 3.6%; else CP_STOP and no opening 2. All three conditions were written before the 4k numbers. The CP100 verdict rule is unchanged.
- **Why:** the decoy test is a futility and safety gate (test cells hold no pastes). At 100% the SUP baseline is more selective (decoy/real 1.1% vs 3.6% for A5c at 5%), so 2× is stricter than at 5%; a seam shortcut would grow with training, which one 2k point cannot show.
- **Outcome:** pending at 12:22 IST; CP100 waits in the queue for `CP_GO` / `CP_STOP`, decided before opening 1.

---

## 5. Housekeeping decisions (how the work is run)

| # | Decision | Who / why | Source |
|---|---|---|---|
| K1 | Long runs in tmux on the servers, one window per run; exact session names `-t "=name"` (prefix match found `p13smoke` once) | the user (D12); Claude after the tmux incident | memory `server-runs-tmux-parallel.md` |
| K2 | One commit per experiment, deployed with `git archive` to a fresh cv02 dir, recorded in `REVISION`; data md5-checked across machines | Claude; makes runs reproducible across machines | memory; `protocols/P6_corrected_baseline.md` |
| K3 | Code for a new experiment goes in a separate git worktree on gaint (`el_p13`, `el_p14`, `el_p16`, `el_p17`), never the main tree that running lanes launch from | Claude, 11 Oct | memory `server-runs-tmux-parallel.md` |
| K4 | GPU rules on cv02:<br>• never start where another user holds > 4 GB;<br>• queues launch only on GPUs with < 1,000 MiB used;<br>• at most 3 runs per GPU;<br>• gaint lanes wait for < 20,000 MiB | user constraint plus Claude's queue design | protocols P6–P16; memory |
| K5 | Never kill other queues or processes without the user's say-so; the gaint extpool queue stays held | auto-mode denials on 8 Oct and the user's instruction | session summaries 2026-10-08T07:54Z, 2026-10-10T19:37Z |
| K6 | Watchers (local polling loops over short ssh calls) fire on "set finished" or any rc ≠ 0; post-analysis scripts (`post_ssl.sh`, `post_p15.sh`, `post_p16.sh`) make each analysis one command | Claude, to keep the overnight pipeline moving | `scripts/post_*.sh`; scratchpad `watch.sh` |
| K7 | Commit to `~/mtp/research` after every result, with attribution trailers; never push to GitHub without asking; PDFs stay local | user constraints | session summaries |
| K8 | Fill idle machines overnight with the next locked experiment ("use all resources") | the user, 10 Oct | memory `server-runs-tmux-parallel.md` |
| K9 | Back up cv02 run dirs to gaint `cv02_noob_el` (laptop relay, manifest + MD5); no agent forwarding or keys on cv02's shared login | the user (D37); Claude on the shared account | memory `cv02-shared-account-backup.md` |
| K10 | (added 30 Oct) Agent teams from 21 Oct: every track has an executor and a critic; no launch without APPROVED; no result reported before the critic's own recompute | the user's team set-up | `team_2026-10-21/README.md`; `team_2026-10-29_features/README.md` |
| K11 | (added 30 Oct) gaint memory: ≥ 2 GB free at all times for root's `finllm_chat.py`; per-run start gate = own measured peak + 2 GB; starts under a flock gate, ≥ 120 s apart | team-lead, 29 Oct 13:31; race fix 30 Oct 02:37 to 02:47 | `team_2026-10-29_features/log.md`; doc 14 §1.2b |

---

## 6. Rules that came from mistakes

Each rule exists because a specific mistake produced a fake or misleading result.

| Rule | The mistake behind it | Source |
|---|---|---|
| Match optimiser steps across arms | an 8× step mismatch faked a +7.4 SSL gain | phase-0 doc; phase-1 §16 |
| Final-step weights primary; never select on test | best-val selection on 54 val cells flips comparison signs; "SL best over budgets" was selection on test | phase-1 §5, §13 |
| Name the metric convention | the "reproduction gaps" were Fioresi 4- vs 5-class, Pratt per-image median, PV-S3 dropping background | phase-1 §5; `to_human/situation_report_2026-10-08.md` §4 |
| Within-machine comparisons only; calibration runs when crossing | gaint and cv02 disagreed on SL-20-b8 (0.346 vs 0.362); later the "0.250 vs 0.310" BN gap was cross-machine (within-machine −0.015 to −0.028) | handoff 7 Oct §6.3; session summary 2026-10-11T09:36Z §4 |
| Every SSL arm gets a loss-off control with the same forward pass | MT and ALHVR "gains" equalled their λ = 0 controls | handoff 7 Oct §6.2 |
| Probe what a loss's target says before running it | SemiCE ran for weeks before P2 showed its targets are incoherent | `results/p2/README.md`; `to_human/proposal_reframe_2026-10-11.md` §6 |
| Show the baseline's label scaling first | L0 (and phase-1 SL-100 = SL-20) did not use extra labels, so there was no gap for SSL to close | `results/p6/README.md` rule 3 |
| The loss-off control must be bit-identical to supervised | joint-BN SSL arms made "loss-off" a handicapped control (P8, P12) | `protocols/P13_cutmix_separate_bn.md` |
| Report inactive with image bootstrap and leave-top-3-out | 3 test cells hold 59% of inactive pixels; the "inactive puzzle" flipped sign without them | `results/p6/README.md` exploratory 4–5 |
| ≥ 5 seeds for effects < 0.05 | 3-seed contrasts kept landing within the thresholds; BsM5's 3-seed sd (0.004) was a third of its 5-seed sd (0.011), and the rule-5 verdict built on it did not survive | phase-1 §16; P13 Amendments 1 and 2 |
| One change per arm | multi-change arms could not be attributed | phase-1 §16 |
| Keep old-era and P-series numbers in separate tables | pilot-era coupled augmentation, the GaussNoise bug and old masks make the numbers incomparable | phase-1 §8, §16; memory `mtp-el-ssl-project.md` |
| Batch questions, hold launches, no presumptions | Claude queued and amended P13 on its own; earlier, leading hypotheses were stated as findings | memory `ask-before-assuming.md`; handoff 7 Oct §10 item 14 |
| Treat the user's questions as tests, not confirmations | phase-1 corrections log | phase-1 §16 |
| Chain GPU queues, one per machine | the 10 Oct queue race | memory `server-runs-tmux-parallel.md` |
| Use exact tmux names (`-t "=name"`) | `has-session -t p13` matched `p13smoke`, so nothing launched | memory |
| (added 30 Oct) Check a protocol's label fraction against the user's question; test a method at the fraction where its mechanism lives | MIM5, DDeP5 and CP5 were screened at 5% for a question about 100% labels (D44, D45) | `SESSION_RECORD_2026-10-28_to_30.md` §5; `coach_strategy.md` §3 rule 2 |
| (added 30 Oct) Report the per-stage encoder cosine to init with every init or pretraining result | "pretraining does not help" turned out to mean "pretraining was erased" by the house optimizer | `coach_100.md` §0; `coach_strategy.md` §3 rule 1 |
| (added 30 Oct) Capture `rc=$?` before any `$(date)`, in every new script; judge completion from DONE lines and manifests | the 21 Oct bug recurred in five status lines on 29 to 30 Oct | doc 13 D20 |
| (added 30 Oct) Absolute log paths in scripts that `cd`; atomic start gates; log stamps from `date` only | a relative path hid the AFTER-RUNS line; three runs started on one memory reading; log lines were stamped up to about 75 min ahead | doc 13 D21 to D23 |

## Related docs
- `00_START_HERE.md`
- `01_project_overview_and_scope.md`
- `04_glossary_and_naming.md` (arm names used above)
- `06_history_phase0_phase1.md` (the inherited decisions H1–H9 in detail)
- `07_methodology_rules_and_statistics.md` (the rules R1–R8 and the standing rules)
- `08_experiments_P1_P7_diagnostics.md`, `09_experiments_P8_P12_ssl_series.md`, `10_experiments_P13_P16_E1.md` (what each decision produced)
- `11_results_synthesis_and_claims.md`
- `13_problems_pitfalls_open_issues.md`
- `14_code_and_infrastructure.md`
- `15_status_remaining_work.md`
- `16_faq_for_the_guide.md`
