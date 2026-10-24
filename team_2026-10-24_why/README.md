# Why standard SOTA SSL fails on our EL data: discussion team, 24 Oct 2026

The leader is team-lead (the user's main session). Three agents discuss, research and critique, then propose directions.

| # | Role | Owns |
|---|---|---|
| R1 | Data/problem-side researcher: what about our data, labels and metric breaks SOTA assumptions | `r1_data_side.md` |
| R2 | Method/literature-side researcher: what SOTA methods assume, and the evidence on when they fail | `r2_method_side.md` |
| C | Critic and moderator: cross-examines R1 and R2, demands evidence, writes the synthesis | `critique.md`, `SYNTHESIS.md` |

## The question
ALHVR (ICCV 2025) was WORSE than supervised. SKCDF's balanced head gave n.d. CPS gave n.d. Our BsM5 (FixMatch-style, 0.95 threshold, separate BN) helps inactive but crack only up to what a free logit bias gives supervised.
- Why do methods that win on medical and natural-image benchmarks fail here?
- What should the thesis try next?

## Evidence to read first (all under ~/mtp/research)
- Memory: `/home/yugma/.noobsurd/projects/-home-yugma-mtp/memory/`, all files (the standing rules).
- handbook/: 00, 03, 05, 07, 10, 11, 13 (A12, A13, B3, E11), 15, 16 and 17. These are the whole history: P1 to P19, AL1, SK1, S-a.
- team_2026-10-21/:
  - alhvr/: design.md (D0 diagnostics), results.md, review_v2.md;
  - skcdf/: results.md, null_diagnosis.md, second_opinion_a2.md, labelling_plan.md, verify_a4/, probe_a2/;
  - data/decision.md (twins, noisy cell).
- results/: al1/, sk1/ (la_sa.md, diag_trajectories.md), e1/, p13 to p19.
- literature/notes/ and literature/pdfs* (local only; never redistribute).

## Rules
- **Citations:** use the Research MCP tools (search_papers, get_paper, read_paper, search_snippets, get_citations and similar) for literature. Cite only papers they return, with their ids; never invent a reference. Fetch full text only for shortlisted papers, because daily publisher downloads are capped.
- **Facts:** every factual claim about our data or results needs a file path and number. Mark each claim as evidence, reading or speculation.
- **Compute:** CPU analysis of existing outputs is fine. Any GPU probe (inference only) needs team-lead's OK. No training.
- **Discussion:** discuss with each other by SendMessage, with at least two real rounds of challenge, not polite agreement. Disagreements that survive go into SYNTHESIS.md as open.
- **Directions:** each proposed direction needs:
  - a falsifiable hypothesis;
  - the evidence for it;
  - the cheapest test, preferably on existing checkpoints or inference only;
  - the cost in GPU-h and runs;
  - the expected effect size against the rule-1 thresholds and the S-a (LA) yardstick;
  - what result would kill it.

  Rank the directions. Include "stop SSL for crack, invest in labels/data" as a legitimate option if the evidence says so.
- **Writing:** for the user: terse, no em-dashes, sourced numbers, verdict separated from reading.
