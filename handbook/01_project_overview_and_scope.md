# 01. Project overview and scope

**What this covers.** What the project is, who it is for, what it is trying to deliver, how the research question changed from the start until now, what is in and out of scope, the constraints, the deliverables, and where things stand on 11 Oct 2026, about 22:00 IST. Read this before any other doc except `00_START_HERE.md`.

**Sources**
- `~/mtp/MTP_session_handoff_2026-10-07.md` (phase 1 handoff, section 1, sections 11 to 13)
- The user's pasted phase 0 and phase 1 handoffs of 11 Oct (copy: `handbook/sources/chat/phase0_phase1_handoffs_pasted_2026-10-11.md`; original in the chat)
- `to_human/proposal_reframe_2026-10-11.md` section 1
- `to_human/directions_2026-10-10.md` sections 0 to 3
- `to_human/midterm_deck_outline.md` slide 1
- `to_human/results_2026-10-12.md`
- The user's chat messages, 7 to 11 Oct 2026

---

## 1. The project in one paragraph

This is an MTP (master's thesis project) done with WattCycle, a solar asset-management company. The topic is deep-learning segmentation of defects in electroluminescence (EL) images of solar cells. Segmentation means a label for every pixel. The defects that matter most are **cracks** (thin dark lines, class id 14) and **inactive areas** (dark regions cut off electrically, class id 11). Pixel labels are expensive and few: the main dataset, BenchmarkEL, has 582 labelled cells. So the original plan was **semi-supervised learning (SSL)**, which also learns from unlabelled images. The work so far covers part 1 of a three-part thesis, the **training methodology**. It has turned into a careful test of when, and how much, SSL and other label-efficient methods help on thin, rare, noisily labelled defects.

## 2. Who wants what

| Party | What they want | Source |
|---|---|---|
| WattCycle | Detect defects in EL images, grade their severity, estimate power loss, on deployable hardware | `to_human/proposal_reframe_2026-10-11.md` §1; phase 0 handoff |
| Faculty advisor | A submittable paper, with a lightweight model. Remembered as about 2M parameters (phase 0 handoff); the poster says about 4M (phase 1 handoff §12, §18), a figure the phase 1 answers say "came from your own thinking" | phase 0 and phase 1 handoffs |
| The user (the student) | Understand the problem properly before proposing a method ("analysis first"), then a method inspired by ALHVR that focuses on the rare classes | user messages, 7 Oct 2026 |

Later decisions by the user (11 Oct, answers to a batch of questions):
- Model size is not a constraint: "not a constraint even 5M works".
- Power loss is out of scope unless valid data appears: "will work on that later, not part of this project unless we get some valid data".
- No WattCycle data is available ("none").
- How the thesis is framed waits for the final results: "framing depends on final results, no presumptions, ever".

Identity details: the phase 1 handoff lists the student, the institute (IIT Mandi), the course (EE511 Computer Vision) and the supervisor from the poster. It also flags them as inconsistent across sources ("confirm which institute and template the MTP report uses"). Ask the user rather than assume.

## 3. The three parts of the thesis
The user split the thesis into three parts on 7 Oct 2026:

| Part | Topic | Status |
|---|---|---|
| 1 | **Training methodology**: how to learn from few, noisy labels plus unlabelled data | Active. Everything in this handbook. |
| 2 | **Architecture**: e.g. the self-attention U-Net++ question, a lightweight model, thin-structure-preserving designs | After part 1. Ideas from phase 0 are listed in `06_history_phase0_phase1.md`. |
| 3 | **Real-time deployment concerns**: severity grading, measurement pipeline, compression for edge hardware (Jetson, INT8 + TensorRT) | Later. Phase 0 had a plan ("Subpath A" post-processing, "Subpath B" compression). |

User's words (7 Oct): "i had divided this ips in three parts: training methodology(one were working on) 2. architecture(after this) 3. realtime deplotment concerns(severity detection and others) so lets focus on trainning methodology".

## 4. Why pixels matter only indirectly: the value chain
EL image → defect maps → per-cell quantities (crack length and connectivity, isolated area, inactive area fraction) → severity grade (Köntges A/B/C) → power-loss band.
- Power loss tracks the isolated and inactive area, not the number of crack pixels. This is a literature claim (`proposal_reframe` §1, tagged **lit**).
- So the headline metrics used so far (pixel IoU, AP) are proxies. Neither WattCycle nor the grading uses them directly. E1 adds per-cell task metrics for this reason (`10_experiments_P13_P16_E1.md`).
- Deployment has about 0.2 s per cell (lit; `directions_2026-10-10.md` §1.5). It is not the binding constraint.

## 5. How the research question evolved
Dates are 2026. Details are in `06_history_phase0_phase1.md`, `08`, `09`, `10` and `12_decisions_log.md`.

| Period | Question being asked | What happened |
|---|---|---|
| **Phase 0** (before early Oct) | Does SSL (Mean Teacher with a "SemiCE" loss) on a self-attention U-Net++ beat supervised? Reproduce published EL papers. | Paper reproductions done. Old SA and SSL results later found **invalid**: an augmentation bug erased cracks, and an 8x step mismatch created a fake +7.4 gain. A reset of the gaint server account lost the code. |
| **Phase 1** (2 to 7 Oct) | Rebuilt the code. Ported ALHVR (ICCV 2025) to EL. Ran low-label sweeps. | On BenchmarkEL no unlabelled loss showed any effect. ALHVR equalled its own loss-off control. Crack could not even be fitted on training images. UCF-EL showed a clean label gap. |
| **Restart, 7 Oct** | The user felt lost ("it trained on 47 images and tested on sam e47, to get 0.3 iou on cracks, definitely dsomething wrong", typos as written). New rule: analysis first, be skeptical, look for bugs. | Data analysis of both datasets. Literature survey. Diagnostic protocols. |
| **Diagnosis, P1 to P5** (7 to 10 Oct) | Can crack be fitted at all? Is SemiCE a valid loss? How much do label versions matter? Are features the bottleneck? How precise are crack pseudo-labels? | SemiCE is not a valid consistency loss (P2), so every old Mean Teacher result is void. Revised labels (E-SCDD) move crack IoU by +0.05 to +0.07, more than any SSL effect (P3). Crack pseudo-labels are right within 2 px but wrong pixel-exactly (P5). |
| **Corrected baseline, P6** (10 Oct) | Which supervised recipe is sound? | L3: U-Net++ with ImageNet ResNet34, CE+Dice, label-safe augmentation, revised masks. It is the base for everything after. |
| **SSL series, P7 to P12** (10 to 11 Oct) | Does an offset-tolerant pseudo-label loss help, at 10% and 5% labels, with an in-domain or external pool, on a pipeline matched to supervised? | The loss helps against its own loss-off control. But the Mean Teacher pipeline itself handicapped the student (BatchNorm mixing), so SSL beat plain supervised on cv02 only narrowly at 10% (P11: passes the seed rule; the inactive part is not robust over cells) and not at 5% (P12). The user: "cant believe bro, supervised beating ssl". |
| **Audit and fixes, P13 to P16** (11 Oct) | Fix the pipeline (separate BatchNorm, CutMix). Does tolerance help human labels (P14)? Does a related labelled dataset beat ImageNet (P15)? What about 20/50/100% labels (P16, the user's request)? | P13: SSL beats supervised at 5% on inactive IoU and crack relaxed F1, robust over test cells. P14: tolerance does not fix label noise. P15: a UCF-EL-pretrained encoder does not beat ImageNet init (5% n.d., 10% worse). P16: SSL is not detectably better than supervised at 20%, 50% or 100% labels. |
| **Follow-up, P17** (13 Oct) | The user asked about two recent papers (DCA, SKCDF). Does BsM5's gain need the labelled decoder to fit pseudo-labels (SKCDF-style decoupling)? BsM5 also gets seeds 3–4 (P13 Amendment 2). | P17: no detectable difference from BsM5; the decoupled arm still beats supervised on all three primaries. BsM5 on 5 seeds still beats supervised (+0.029 crack IoU instead of +0.036 on 3). DCA was not run. |

**Current problem statement** (draft, `proposal_reframe_2026-10-11.md` §1): this is "thin-structure and region segmentation, from few labels with imprecise geometry, with a long-tailed class distribution, several image sources, and a small test set, whose real output is a measurement". It is not mainly an SSL problem. The final framing is the user's call; all results are in (doc 15 §3).

## 6. Scope

| In scope (part 1) | Out of scope for now |
|---|---|
| Pixel segmentation of crack and inactive on BenchmarkEL `dataset_20211104` (582 cells), scored on revised E-SCDD masks (for crack and inactive = BenchmarkEL `20221008` masks; doc 17) | Power-loss estimation (no valid data; the user's decision) |
| Semi-supervised methods: Mean Teacher, tolerant and hard pseudo-labels, CutMix, in-domain and external unlabelled pools | WattCycle's own images (none available) |
| Supervised recipe: augmentation, loss, pretrained encoder, label version, offset-tolerant supervision | Architecture search (part 2) |
| Cross-dataset transfer (UCF-EL encoder, P15) | Deployment, compression, severity grading (part 3) |
| Evaluation method: locked protocols, seeds, bootstrap, per-cell task metrics, an unseen-module extension set | Tuning SSL hyperparameters (explicitly not claimed in every protocol) |
| UCF-EL as a second dataset (phase 1 runs; P15 transfer) | Other splits of BenchmarkEL (one split only) |

## 7. Constraints

| Constraint | Detail | Source |
|---|---|---|
| Labelled data | 582 cells: 478 train, 54 val, 50 test. Crack is about 0.19% of train pixels. Inactive is in 2 of 23 labelled cells at 5% labels. | `03_datasets_and_splits.md` |
| Test set | 50 cells, hand-picked by the dataset authors. All 50 contain crack on the old masks (48 on the revised masks); inactive is in 16 on the revised masks (17 on the old), and 3 cells hold 59% of the inactive pixels. | `results/p6/README.md` §4; `results/p13/README.md`; handoff §3.1 |
| Compute | gaint: 1 RTX PRO 4500 (32 GB, shared with one other process). cv02: 8 RTX A6000 (48 GB each), shared with many users. | `14_code_and_infrastructure.md` |
| Time | Mid-term presentation. On 10 Oct the user said it was "in 4 days". On 11 Oct: "youve 1 day for the work then ill startr on ppt". | user messages |
| Method rules | Locked protocols, step matching, final weights, within-machine comparisons, 5 or more seeds for small effects, one change per arm | `07_methodology_rules_and_statistics.md` |
| Model size | Not a constraint (up to about 5M parameters is fine) | user, 11 Oct |

## 8. Deliverables

| Deliverable | Status (11 Oct, ~22:00 IST) | Where |
|---|---|---|
| EE511 course poster | Done; partly outdated (phase 1 handoff) | not in this repo |
| Mean Teacher and ALHVR paper presentations (course) | Done (phase 1 handoff) | not in this repo |
| Mid-term presentation (part 1) | The outline exists, drafted 10 Oct before P9 to P17 results. The user starts the slides after the one-day push. | `to_human/midterm_deck_outline.md` |
| Results summary for the user | Being filled as experiments finish | `to_human/results_2026-10-12.md` |
| Proposal reframe | Draft of 11 Oct, before the P13 to P16 results. Not updated: any rewrite implies a framing, which is the user's call (doc 15 §2) | `to_human/proposal_reframe_2026-10-11.md` |
| MTP progress report (LaTeX) | Not started (phase 1 handoff) | n/a |

## 9. Where things stand (13 Oct 2026, ~16:30 IST)
- **Done:** P1 to P17 and E1, each with a README under `results/`, plus the E-SCDD audit (`results/escdd_audit/`, doc 17). Nothing is running (doc 15 §1c). cv02 checkpoints are copied to gaint (`cv02_noob_el`).
  - P15: the UCF-EL encoder does not beat ImageNet init; equal at 5%, worse at 10% (`results/p15/README.md`).
  - P16: SSL vs supervised is n.d. at 20%, 50% and 100% labels on all three primaries, 5 vs 5 seeds (`results/p16/README.md`). One noisy test cell (`CSIR_00070_r8_c4`) moved every crack contrast; without it every crack Δ is within ±0.003 (post hoc).
- **The short version of the evidence:**
  - Label version and supervised recipe move the numbers more than any SSL effect at 10%.
  - The old Mean Teacher pipeline handicapped the student through shared BatchNorm.
  - Once that is fixed (P13), SSL at 5% labels beats a 5-seed supervised baseline on inactive IoU (+0.117) and crack relaxed F1@2 (+0.033), robust over test cells. Crack IoU is not detectably better (+0.014).
  - Hard pseudo-labels with CutMix also lift crack IoU: +0.029 on 5 seeds (+0.036 on the first 3; seeds 3–4 added post hoc, P13 Amendment 2). A secondary contrast.
  - P17: keeping pseudo-labels out of the labelled decoder (SKCDF-style) changes nothing detectable against BsM5; the decoupled arm still beats supervised on all three primaries. A decoder share below about 40% of the gain is not excluded.
  - P16: at 20%, 50% and 100% labels SSL (P13's Cs recipe, no CutMix) adds nothing detectable. 10% has no separate-BN SSL arm, so where between 5% and 20% the P13 gain fades is not measured.
  - Full table: `11_results_synthesis_and_claims.md`.
- **Open:** the user's decisions (framing, deck, test set, standing checks): doc 15 §3.

## Related docs
- `00_START_HERE.md`: how to use this handbook
- `02_domain_primer_EL_and_defects.md`, `03_datasets_and_splits.md`: the problem and the data
- `06_history_phase0_phase1.md`: everything before 7 Oct
- `07_methodology_rules_and_statistics.md`: how experiments are judged
- `11_results_synthesis_and_claims.md`: what we can claim
- `12_decisions_log.md`: who decided what, when, why
- `15_status_remaining_work.md`: what is left
