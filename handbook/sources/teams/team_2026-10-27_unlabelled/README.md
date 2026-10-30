# Team 27 Oct: how should we use the unlabelled data, and how should the user read the SSL result?

## The user's question (paraphrased, 27 Oct)
"Supervised training on our ~580 labelled cells gives some result. We also have ~12k unlabelled cells. Basic intuition: unlabelled data lets the model learn better features, which we then tie to the labels from the small labelled set, so adding the unlabelled pool should improve scores. Maybe we used the wrong training methodology: Mean Teacher suppressed the rare classes, multi-decoder methods (ALHVR, SKCDF) also did not work. How should I perceive this? Should we change the test set, or anything else? Think out of the box, do not be biased."

The user's goal (standing): the highest scores, a model that catches almost all cracks, inactive and other important defects, while keeping mIoU on the other classes balanced.

## What exists (read these, do not trust summaries)
All under `/home/yugma/mtp/research/` unless absolute.
- **Handbook:** `handbook/00_START_HERE.md` first. Then:
  - `03_datasets_and_splits.md`: splits; §6 external pool, 11,938 CSIR/ARTS cells; §7 E1 unseen modules; E-SCDD;
  - `09` (P8-P12 SSL series), `10` (P13-P16, E1), `11` (claims), `13` (pitfalls), `17` (E-SCDD audit).
- **Earlier why-analysis (24 Oct):** `team_2026-10-24_why/SYNTHESIS.md`, `critique.md`, `r1_data_side.md`, `r2_method_side.md`.
  - It is one view. You may disagree with it.
- **Track D (24-25 Oct, critic-verified):** `team_2026-10-24_go/trackD/`. Read `verify_probe.md`, `verify_edge.md`, `verify_labelset.md`, `critic_defaults.md`.
- **Track M (best model, critic-verified):** `team_2026-10-24_go/trackM/`. Read `baseline.md`, `results_final.md`, `results_r3.md` (ResNet-50), `results_r4.md` (+107 E-SCDD cells), `results_r5.md` (2x resolution).
- **Older SSL runs:** `team_2026-10-21/alhvr/results.md` (ALHVR, AL1), `team_2026-10-21/skcdf/results.md`, `null_diagnosis.md`, `labelling_plan.md` (SKCDF, SK1).
- **Raw per-run / per-cell outputs:** `results/` (e.g. `results/p16/`, `results/e1/`, `results/trackD_*`). Track M JSONs are in `team_2026-10-24_go/trackM/{m0,r1,...,final}/`.
- **Datasets:**
  - `~/mtp/datasets/`: `BenchmarkELimages`, `escdd_full` (HF snt-ubix/escdd @ 8c8cba9a, 30 classes), `UCF-EL-Defect`.
  - Do not use the `escdd_mirror_shivahanifi` variants: they rescale the cell and change crack width.
- **Literature:**
  - `literature/` and `papers/`: local PDFs. Never upload or redistribute them.
  - Research MCP tools (`mcp__claude_ai_Research_MCP__*`, load them with ToolSearch).
  - Cite only papers those tools return, with their ids. Fetch full text only for a shortlist (daily cap).

## Rules
- **No GPU, no training, no inference launches, no writes on gaint or cv02.**
  - Read-only ssh to look at files is fine: gaint `noob@172.18.22.20`, cv02 `cv02@10.8.1.106`, shared account, no `-A`, no keys.
  - CPU analysis of existing outputs on the laptop is fine. Put scripts in this folder.
- Separate **E** (measured here, with file path), **R** (reasoned / literature, with paper id) and **S** (speculation).
- Be unbiased. "Stop using unlabelled data", "change the metric", "change the test set" and "the earlier synthesis is wrong" are all allowed conclusions if the evidence supports them.
  - Changing the test set after seeing results is a p-hacking risk. Any such proposal must say how to do it honestly.
- Terse. No em-dashes.
- Write only in this folder.
- Talk to each other with SendMessage, by name:
  - `lit`: literature researcher;
  - `evalx`: measurement and test-set skeptic;
  - `ideas`: out-of-the-box methods;
  - `judge`: critic and synthesiser.
- Disagree openly. When a teammate's claim rests on a number, check the number.
