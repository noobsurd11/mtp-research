# Session handoff, 13 Oct 2026 (for the next Claude Code session)

The 7 to 13 Oct session ends here. The handbook (`handbook/`) explains the project to a human guide agent. This file is the short operational resume point for Claude. Where they disagree, `results/*/README.md` wins, then the handbook.

## 1. State at close (13 Oct, about 01:30 IST)
- **All experiments are done:** P1 to P16, E1 and the E-SCDD audit. Each has a README under `results/`. Nothing of ours is running on either server.
- **Last commit:** the one containing this file. The previous commit is `1bbe631` (P16 results).
- **Results summary:** sent to the user on 12 Oct at 04:48 IST. The file is `to_human/results_2026-10-12.md` (row 8 corrected 13 Oct). The user has not replied. A one-line offer to turn it into a shareable web page is also unanswered.
- **The user's plan:** start the mid-term PPT after "1 day for the work" (11 Oct). The outline says the mid-term is "about 14 Oct (confirm the date)".
- **Server state** (tmux sessions, GPUs, `/tmp/noob_el` size, worktrees): `handbook/15_status_remaining_work.md` §1b.

## 2. Read first
1. `handbook/15_status_remaining_work.md`: status, the decisions waiting on the user (§3), remaining work (§4) and housekeeping (§7).
2. `handbook/11_results_synthesis_and_claims.md`: the evidence table, and what can and cannot be claimed.
3. `to_human/results_2026-10-12.md`: what the user was told.
4. `results/p16/README.md`: the latest experiment and the noisy test cell `CSIR_00070_r8_c4`.
5. `handbook/07_methodology_rules_and_statistics.md` and `14_code_and_infrastructure.md`: before designing or launching anything.

## 3. Waiting on the user (do nothing on these without an answer)
Full table in doc 15 §3. In short:
1. Thesis framing.
2. An exploratory BsM arm (hard PL + CutMix) at 20/50%.
   - 2b. Whether "without `CSIR_00070_r8_c4`" becomes a standing check.
3. A larger test set, or E-SCDD's extra cells (data local, doc 17).
   - 3b. Wording for the label attribution (the revised crack/inactive masks are BenchmarkEL `20221008`'s).
4. Mid-term deck content. `to_human/midterm_deck_outline.md` and `proposal_reframe_2026-10-11.md` were deliberately left untouched after P13 to P16: any rewrite implies a framing.
5. Identity, institute and template for the MTP report.

## 4. Standing rules (the user's)
Also in memory: `mtp-el-ssl-project`, `ask-before-assuming`, `server-runs-tmux-parallel`.
- **No presumptions:** "framing depends on final results, no presumptions, ever". Batch questions and ask them; hold launches while questions are open.
- **Experiments:**
  - lock a protocol in `protocols/` before launching;
  - match optimizer steps across arms; one change per arm;
  - final-step weights are primary; never compare arms across machines;
  - 5 vs 5 seeds for small effects;
  - keep old-era numbers apart from P-series numbers.
- **Servers:**
  - Hosts: gaint `noob@172.18.22.20` (`/home/noob/work`); cv02 `cv02@10.8.1.106` (`/tmp/noob_el`, wiped on reboot).
  - Run in tmux, one session per experiment, and use `tmux has-session -t "=name"`.
  - On cv02, never start on a GPU where another user holds > 4 GB.
  - Put new code in a git worktree on gaint.
  - Read-only unless the user asks. Never kill queues, processes or tmux sessions without the user's say-so.
  - The gaint `extpool_20261007` queue stays held and untouched.
- **Repo and secrets:**
  - Never push to GitHub without asking.
  - `papers/` stays untracked and is never redistributed.
  - The Dropbox app secret is never exposed (rotation unconfirmed).
- **Commit trailers:** `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>` and `Claude-Session: https://claude.ai/code/session_01HzsHXC91MDtjqG2abZt5qU`.
- **Writing:** terse, no em-dashes, no buzzwords, they/them for the user. Sourced numbers; keep the locked verdict, the robustness check and the reading apart.
- **The handbook:** after any new result, update docs 10, 11, 15, 00 and 16, run `bash handbook/sync_sources.sh`, then commit.

## 5. Tools and paths
- Local Python: `~/mtp/research/.venv/bin/python`. Post-analysis entry points: `scripts/post_p15.sh`, `scripts/post_p16.sh <cv02 gpu>`, `scripts/p16_excell.py`, `scripts/cell_noise_rank.py`, `scripts/diag_csir70.py` (doc 14 lists them all).
- Copies of the launch scripts and queue specs from the servers: `scripts_cv02/`, `scripts_gaint/`.
- Data (local): `~/mtp/datasets/` (BenchmarkEL, its 2022 releases, full E-SCDD and its mirror, UCF-EL, splits).
- This session's transcript: `~/.claude/projects/-home-yugma/57bebbba-992f-43ae-8c6c-f7004d0f15c5.jsonl`. The user's messages and the compaction summaries from it are in `handbook/sources/chat/`.
- **Gone with the old session scratchpad:**
  - the overnight watcher (`watch.sh`);
  - the checker agents' verification scripts.

  Their outcomes are recorded in the READMEs and the handbook. Nothing else depends on them.

## 6. Housekeeping left open
- About 20 idle tmux sessions of ours on cv02 and 3 on gaint (doc 15 §1b). Close them only if the user agrees.
- `scripts/aggregate_runs.py` has been untracked since 10 Oct; its origin is unrecorded. Left as is.
- Checkpoints exist only in cv02 `/tmp/noob_el` and on gaint, with no backup.
