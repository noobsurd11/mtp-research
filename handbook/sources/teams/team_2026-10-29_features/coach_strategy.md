# coach: strategy for the user's goal, as a scarce-data lead (30 Oct 2026)

The user asked coach to guide, not only to review. This is my read of where the score is and what to run, ranked by expected test gain per cost. Tags: E measured (path), R literature (Research MCP id, [A] abstract or title only), S judgement.

## 1. Diagnosis: what limits the score (E)
1. **Labels dominate everything we have measured.**
   - Revising labels moved crack IoU +0.05 to +0.08: P14 L3 − L3o +0.082 at 10% (`handbook/11` claim 1).
   - Doubling labels 50% → 100% gave +0.026 crack on the clean set: 0.448 → 0.474 (`handbook/11` label curve).
   - Every unlabelled-pool method is null from 20% labels up: pseudo-label SSL (P16), MIM5 and DDeP5 (`verify_mim5.md`, `verify_ddep5.md`).
2. **The fine-tune discards pretrained deep features** (`coach_100.md` §0). layer3-4 end at cosine 0.00-0.02 to their init, for every init and at 100% too.
   - So every "init, backbone or pretraining does not help" result so far is conditional on one never-varied optimizer: P15, MIM5, Track M R3 (RN50, EffNet-B4, ConvNeXt) and DDeP.
   - That includes the R3 backbone null, although Track D showed frozen RN50/ConvNeXt features rank BMRK crack better than our fine-tuned encoder (`trackD/verify_probe.md`).
3. **The misses are about context, not capacity** (`team_2026-10-27_unlabelled/SYNTHESIS.md` §7).
   - On E1, 75% of crack sits in half-cut + scuff cells, and only 0.13 of it is found.
   - Training holds 0 half-cut cells and 12 scuff cells, and scuff has always been ignore. So the model paints scuff streaks as crack (about 8.7k px per run) and misses the crack branching off them.
   - In-split, the confident misses concentrate in BMRK (relR@2 0.745) and CFVS without twins.
4. **Evaluation:** 50 test cells give a clean MDE of 0.012 crack, 0.013 relF1 and 0.032 inactive. An intervention whose honest expectation sits below that cannot be shown however true it is (`team_2026-10-27_unlabelled/eval.md` §1.2).

## 2. What I would run, in order
**A. Fix the fine-tune (in flight: protocol_100, SUP100-PF).** Highest expected gain per GPU-hour; no labels needed.
- R [A] arxiv:2202.10054: full fine-tuning distorts pretrained features and can underperform out of distribution. Probing first, then fine-tuning, keeps them. That is our E1 problem in general form, and PF is that recipe for a segmentation net.
- If SUP100-PF passes or shows a same-sign gain on noNoisy:
  - **A2:** RN50 and ConvNeXt-T under PF, one arm each vs SUP100-PF. Their R3 null was under the erasing optimizer, and Track D says they carry BMRK crack signal.
  - **A3:** a weight average of the 5 PF seeds (model soup, R [A] arxiv:2203.05482) as a single-model alternative to the ensemble. It only makes sense when seeds stay near a shared init, which PF provides and the house recipe does not (layer4 seed-to-seed cosine 0.007). Inference only, val first.
- If SUP100-PF is n.d. or worse: erasure is benign for this task. Close the init/backbone/pretraining line for good, with a better reason than before.

**B. Labels: use the pool to choose what to label.** This is the user's "tie the unlabelled cells to the labels" in its highest-yield form. It was ranked #1 on 27 Oct and never run.
- **B1. Free label audit of train (no new training, CPU).**
  - The 5 seeds of `sl_20pct_s0-4` (cv02 backup on gaint) never saw 383 of the 478 train cells. Score those cells and flag:
    - GT crack or inactive that all 5 out-of-fold models confidently miss (possible false labels);
    - confident crack all 5 agree on where GT says background (possible missed labels).
  - Rank cells. The user reviews the top 30-50 (about 1 h).
  - Why: label revision is the biggest effect we ever measured (+0.08). A handful of wrong train masks teaches "crack = background" on exactly the hard cases.
- **B2. Mine the pool for the failure contexts** (27 Oct item 1a): the label-free proposer on the pool's half-cells.
  - The user checks the top 100 at cell level and pixel-labels 20-40 scuff + crack cells. Hygiene: R1-R4 (no val, test or E1 module).
  - Expected (S, 27 Oct): E1 crack recall +0.04 to +0.15, BMRK crack +0.02 to +0.05, pooled test ≤ +0.01.
  - Needs the user's time. team-lead asks.
- **B3. Scuff policy (user decision; a label-definition change, no new annotation).**
  - Train scuff as a class, or as "not crack", instead of ignore. One arm at 100% vs SUP100, judged on E1 scuff-cell crack false alarms and recall (descriptive) plus the test primaries.
  - Only 12 train cells carry scuff, so pair it with B2.

**C. Thin-structure crack loss** (the "catch almost all cracks" goal; relR@2 0.866 at relP@2 0.930, target 0.90/0.90).
- Skeleton Recall loss (R [A] doi:10.1007/978-3-031-72980-5_13, thin structures including concrete cracks, cheap). clDice is the alternative (R [A] doi:10.1109/cvpr46437.2021.01629).
- One arm at 100%, on top of the best recipe from A. Loss changes consume labels, so test at 100%, not 5% (`diag_5pct_to_100pct.md` §4).
- Named primary: relR@2 and component recall at matched relP@2.

**D. Unseen modules, inference only:** BN re-estimation on pool half-cells, and R34 + RN50 ensemble members (27 Oct item 4). Minutes each, E1 descriptive. Run while the GPU queue is busy.

**Stop:** further pool representation learning (contrastive, clustering, diffusion, DDeP) and pseudo-label SSL at ≥ 20%. Also stop screening label-consuming methods at 5%.

## 3. Methodology rules I would add to the house rules
1. **Every init or pretraining result reports the final-vs-init encoder cosine per stage.** It is free, and without it "pretraining does not help" may only mean "pretraining was erased".
2. **Test a method at the label fraction where its mechanism lives** (diag §4). Label-consuming methods (paste, loss, label fixes) run at 100%; only methods whose effect shrinks with labels get a 5% screen.
3. **MDE gate before any 5-seed arm.** If the pre-stated expectation is below the clean MDE (crack 0.012), run it only when the user wants the answer itself (thesis), and say so in the protocol.
4. **One best-recipe track.** Each component passes on its own first. Then combine them (recipe + backbone + loss + new labels) into one candidate, chosen on val, ensembled, and opened on test once against FINAL, as Track M's final did.
5. **Human time is a resource like GPU time.** 1-2 h of the user's review (B1, B2) has a larger expected gain than any 20 GPU-h arm on the table. Put it to the user explicitly.

## 4. Immediate actions (none blocks protocol_100)
- runner, CPU while the queue runs: B1 OOF audit on `sl_20pct_s0-4` (list of flagged train cells with px counts and an overlay PNG per cell); D BN re-estimation and ensemble checks (E1 descriptive).
- team-lead to the user:
  - 1 h to review B1's flagged cells;
  - yes/no on B2 (100 pool half-cells, cell-level check, 20-40 pixel masks);
  - the scuff policy (B3).
- protocol_100 settings from diag:
  - CP100 backgrounds stay pool-only. Labelled-train backgrounds would need GT-aware ring/ignore code, and the pool (11k cells) is already the more varied set.
  - Paste rate λ 1, batch 4. diag's estimate is +55% crack px per step over labelled.
  - SUP100-PF unconditional (accepted).

## Appendix: B1 flag rule (exact; 30 Oct 11:06; runner runs it, the user reviews)
**Auditors (out-of-fold for the cell):**
- `sl_20pct_s0-4`, final weights, for the 383 train cells outside their labelled list. Runner first confirms the recipe: masks_escdd, split seed 0, 20% list md5.
- If `p16_A_50pct_s0-4` are backed up, they also audit their 239 out-of-fold cells. Report both; a flag from either set counts, with the auditor named.
- Inference: 512 native, no TTA, fp32 softmax. Inputs are only images and the train masks.

**Excluded px (never flagged):**
- GT padding 7, border 5, frame_edge 21, jbox 22 (models hallucinate at frame edges; not label errors).
- E-SCDD scuff (25) and star (28) px. P6 remapped these to old labels in 17 cells (`handbook/17` l.119), in at least 2 test cells to crack. They go to list S below, not to the model flags.
- For crack: GT crack_rbn_edge 10 (taxonomy, not error) and px within 2 px of GT crack (width jitter).
- For inactive: GT dead_cell 17 and px within 3 px of the GT inactive edge.

**Flags, per class c in {crack 14, inactive 11}, component level (8-connected):**
- **ML (possible missed label):** a component of {px where all 5 auditors give p_c ≥ 0.9, GT ≠ c, not excluded}. Kept if ≥ 20 px for crack, ≥ 200 px for inactive.
- **FL (possible false label):** a GT component of c (≥ 20 px crack, ≥ 200 px inactive) where every auditor has relaxed recall@2 < 0.1 on it and mean p_c over it < 0.1.
- Expect FL to also catch hard real cracks: the 20% auditors have crack IoU about 0.40. The human decides; the rule only ranks.

**List S (deterministic, no model):** for each of the 17 remapped cells, the px where the E-SCDD mask says scuff/star and masks_escdd says crack (or inactive). Use gaint's raw E-SCDD masks; `el_m/data/escdd_masks` still holds class 25 for test.
- If train cells carry scuff labelled as crack, that alone could teach "streak = crack", which is the E1 failure (S).

**Base rate (descriptive):** the same ML/FL rule on the 54 val cells (out-of-fold for every auditor). It shows how much disagreement is normal on a reviewed set. Never test.

**Outputs:**
- `b1_flags.tsv`: cell, source, split role (train / D7 twin), auditor set, class, flag type, px, components.
- `b1_S.tsv`.
- Panel sheets (image | GT | 5-auditor consensus | flags, ML yellow, FL magenta, S cyan; cell id, source and px in the title):
  - sheet 1: top 30 cells by crack ML + FL px;
  - sheet 2: top 10 by inactive;
  - sheet 3: all train cells in S.
- The user marks each panel: label error / true hard case / unsure.
- No mask is edited until the user decides. Fixes go to a new mask version (`masks_escdd_v2`) with a diff list, and are never applied to val or test without a separate decision.
