# sources/: primary documents behind the handbook

The handbook docs (`../00` to `../17`) summarise and explain. This folder holds the primary documents they cite, so a reader with only this folder still has the originals. When a handbook doc and a source disagree, the source wins; report the disagreement.

| Folder or file | What it is | Freshness |
|---|---|---|
| `chat/phase0_phase1_handoffs_pasted_2026-10-11.md` | The user's two pasted handoffs about earlier work (phase 0: before early Oct; phase 1: 2 to 6 Oct), plus the user's answers to questions about older work. These exist only in the chat. | static |
| `chat/claude_session_summaries_2026-10-07_to_11.md` | Claude's own running summaries of the work sessions 7 to 11 Oct (written at each context compaction). The fullest chronology of what was done and decided. Machine-written; treat numbers as pointers and check them against `results/`. | static |
| `chat/user_messages_2026-10-07_to_11.md` | The user's own messages in those sessions, verbatim, with UTC timestamps (IST = UTC + 5:30) | static |
| `chat/claude_session_summaries_2026-10-11_to_12.md` | Continuation: the three summaries written 11 Oct 18:08 UTC to 12 Oct 00:35 UTC (handbook build, E-SCDD audit, P16 analysis and the noisy test cell), then the final results message sent to the user (12 Oct 04:48 IST) | static |
| `chat/user_messages_2026-10-11_to_13.md` | Continuation: the user's messages from 11 Oct 16:34 UTC to the end of the session (13 Oct) | static |
| `MTP_session_handoff_2026-10-07.md` | The phase 1 handoff written 7 Oct 22:15 IST: machines, data, code, every old-era experiment, mistakes, plan | static |
| `protocols/` | Locked protocols P1 to P16, with their amendments. Each says what was seen before locking. | refreshed by `../sync_sources.sh` |
| `results/` | Each experiment's README, rules output (`*_rules.txt`) and bootstrap output (`*per_image_test.txt`), named `<experiment>__<file>` | refreshed |
| `to_human/` | Reports written for the user: situation report (8 Oct), directions (10 Oct), proposal reframe (11 Oct), mid-term deck outline, results summary (12 Oct) | refreshed |
| `analysis/` | Paper-metric reproduction notes (`papers_metrics.md`) and the ALHVR audit | refreshed |
| `data_analysis/` | BenchmarkEL and UCF-EL data reports, and the BenchmarkEL dataset README. From 12 Oct also: the E-SCDD dataset card (`escdd_dataset_card_README.md`), its class definitions (`escdd_class_explanation.json`, `escdd_ListOfClassesAndColorCodes.csv`), and the build note of our `masks_escdd` (`masks_escdd_README.txt`, from gaint) | refreshed |
| `literature/` | Survey, papers index, reading list, and 26 per-paper and per-topic notes in `notes/` | refreshed |
| `old_era_reports/` | Phase 1 reports from the training repo on gaint (`gaint__*`) and the cv02 results log (`cv02__el_results_cv02.md`). Old-era setup (original masks, from-scratch U-Net++, weighted CE, batch 4, SemiCE): never mix their numbers with P-series numbers. | refreshed |

The two `claude_session_summaries_*` files have the user's email address replaced with `[the user's email]`; otherwise the chat files are verbatim.

Not copied: figures (`results/*/fig_*.png`, `data_analysis/figs/`), raw JSONs, code, and paper PDFs (`~/mtp/research/papers`, local only, never redistribute). Read those in place; `../14_code_and_infrastructure.md` says where.
