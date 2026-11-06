# Team thermal (4 Nov 2026): can thermal (IR) imaging help our EL segmentation?

Source: Om's brief, `om_2026-11-04_thermal.md` (verbatim, md5 6677bc9f). team-lead orchestrates only and relays to the user.

## Mindset
- Be OPTIMISTIC and GENERATIVE: look for ways to make thermal work, not reasons to kill. Gather many ideas first; rank later.
- Still be honest. Tag every claim:
  - **E:** measured in our data or files (give the path);
  - **R:** from a source (give a Research MCP id or URL);
  - **S:** your own reasoning or speculation.
  An optimistic S claim is fine; an S claim dressed as R is not.

## Project context (read before working)
- **Task:** segment rare defects in EL (electroluminescence) images of solar cells: crack and inactive (dark, disconnected areas), plus other classes. Data: BenchmarkEL, 582 labelled cells (478 / 54 / 50).
- **Best model:** a 5-member U-Net++ R34 ensemble (E-PF). On test, crack IoU is ~0.49, near the labelling ceiling.
- **Open problem:** unseen modules (E1, 106 cells). Crack recall there is ~0.2, and 75% of missed crack px sit on scuff + half-cut cells. Inactive on E1 is small and concentrated. No method so far fixes scuff + half-cut.
- **Background reading:**
  - ~/mtp/research/handbook/00_START_HERE.md, 02 (EL primer), 03 (datasets), 11 (claims), 21 (latest experiments);
  - ~/mtp/research/literature/notes/F04_el_datasets_census.md (EL dataset census; check it for multimodal sets first);
  - ~/mtp/research/SESSION_RECORD_2026-11-01_to_11-03.md §1.
- **Industrial partner:** WattCycle. Institute: IIT Mandi.

## Roles and outputs
Each agent writes ONLY in its own folder, plus log.md.

| Agent | Question (Om's numbering) | Output |
|---|---|---|
| `datascout` | (1) public datasets with paired or co-registered EL + thermal; also EL + PL, EL + UV fluorescence, EL + RGB, and thermal-only PV sets with defect labels | `datasets/dataset_table.md` (one row per dataset: name, source / id, modalities, pairing level (module / cell / pixel), count, resolution, labels, licence, access, cell-level alignment possible?, notes) + `datasets/notes.md` |
| `ideas` | (2) every way thermal could help: multimodal fusion; cross-modal pretraining or distillation (thermal teacher, EL student); thermal as weak labels for inactive and hotspots; EL-to-thermal (or thermal-to-EL) synthesis; thermal for unseen-panel generalisation; the industrial pipeline (drone IR screening, EL for detail); anything else | `ideas/ideas_long.md`: aim for 25+ ideas, each with mechanism, which of our problems it targets (scuff / half-cut / inactive / unseen modules / deployment), data needed, rough cost, first experiment, E/R/S tags |
| `capture` | (3) can WattCycle or IIT Mandi capture paired EL + thermal on a few modules, and what does that need: equipment, setup (forward-bias EL, dark / steady-state / lock-in thermography, reverse-bias hotspots, outdoor IR), registration to cell level, protocol, number of modules, time, cost, safety, questions to ask WattCycle / IIT Mandi | `capture/capture_plan.md` |
| `synth` (after the three above) | rank all ideas by expected value, cost and data needed (public data vs own capture); pick the top 3 with concrete first steps | `synth/ranked_ideas.md`, `synth/top3.md`, `synth/SUMMARY.md` (1 page for Om) |
| `check` (after synth) | verify that cited sources exist and say what is claimed (dataset facts: size, resolution, labels, licence, URL); check E/R/S tags. Does NOT kill ideas; it corrects facts and tags | `check/factcheck.md`; fixes go back to the owner |

## Rules (binding)
- **No downloads:**
  - no dataset files, archives, model weights or pip / venv installs;
  - reading web pages, dataset cards, GitHub READMEs and paper abstracts or metadata is fine;
  - Research MCP: cite only ids it returns; fetch full text only for a short list (publisher downloads are capped per day);
  - PDFs in literature/ stay local and must not be uploaded or redistributed.
- **Servers read-only:**
  - gaint and cv02 are not needed for this task, so do not ssh;
  - no GPU work of any kind without Om's OK, via team-lead.
- **No contact with anyone outside:** no emails, no posts, no form submissions. Questions for WattCycle / IIT Mandi / dataset authors go into your output as a list for Om.
- **No manual labelling asks.** The user avoids hand labelling; if an idea needs labels, say how many hours and why.
- **Don't name the 3 Hanifi B2 panel cells.** Do not open team_2026-10-29_features/b2_mining/v2/b2v2_candidates.tsv, b2v2_hanifi_panels.txt, overlays/ or team_2026-10-31_next/judge/b2_key*.
- **No test or E1 reads:** don't open test or E1 images or labels for this task. It is a desk study.
- **No pattern kills:** never pkill -f / killall; stop only processes you started, by PID.
- **Log:** append steps to log.md as `YYYY-MM-DD HH:MM IST <agent>: ...`, with the stamp from `date`.
- **Style:** plain English, terse, no em-dashes.

## Flow
1. datascout, ideas and capture run in parallel. ideas and capture may read datascout's table as it grows.
2. When all three are done, synth ranks and writes the top 3.
3. check fact-checks; the owners fix.
4. team-lead reports to the user and Om.
