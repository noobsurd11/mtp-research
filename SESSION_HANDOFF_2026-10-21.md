# Session handoff, 21 Oct 2026 (about 21:00 IST)

The user asked for a 4-agent team. The leader (this session) orchestrated:

| Agent | Role | Agent ID (for SendMessage) | Watch |
|---|---|---|---|
| 1 | ALHVR trainer (1b, from 22 Oct; old a5efd62cb5e6c2017 stopped by user) | ac676f2a224595d3c | `watch-agent.sh alhvr` |
| 2 | ALHVR critic | a491a5b03f55f0617 | `watch-agent.sh alhvr-critic` |
| 3 | SKCDF trainer | ad89b81b8a0ae701a | `watch-agent.sh skcdf` |
| 4 | SKCDF critic | ad834c97eafc6292e | `watch-agent.sh skcdf-critic` |

- **Agents:** they run in-process in leader session `5e4cd451-b143-4f3b-97bd-3e9d0b41e0de` (config dir `~/.noobsurd`). Transcripts are in `~/.noobsurd/projects/-home-yugma-mtp/5e4cd451-b143-4f3b-97bd-3e9d0b41e0de/subagents/`.
  - Resuming that session (`claude --resume`) keeps the IDs valid: a SendMessage to an ID resumes that agent from its transcript.
  - In a fresh session, spawn new agents and point them at this file and `team_2026-10-21/`.
- **Watcher:** `/home/yugma/mtp/tools/agents/watch-agent.sh` has the agent IDs and session path hard-coded; edit them if new agents are spawned.
- **Team rules:** in `team_2026-10-21/README.md`. The critics hold launch authority.

## User decisions (21 Oct)
- **Data:** the local `~/mtp/datasets/escdd_full` (HF snt-ubix/escdd @ 8c8cba9a) is the release; no newer one exists.
  - Kaggle was searched too: nothing from Pratt.
  - Do not use the shivahanifi no-padding or per-class variants.
  - Recorded in `team_2026-10-21/data/decision.md` (D1 to D7 plus the "User answers" section).
- **D7 = yes:** the 7 train twins of test cells are dropped from the unlabelled pool, and the SSL references are re-run.
- **Old claims kept**, with "without twins" lines added alongside (commit `a4ac59f`).
- **Launcher bug:** the rc = 0 bug in the P-series launchers is documented (`16128f7`). All 28 P13/P17/P18 runs did reach step 20,000.
- **Machine:** cv02 for both tracks. Outputs are copied back to gaint `cv02_noob_el` with MD5 checks.
- **Extra arm:** ALd5 at λ 0.3 added (ALdh5).

## Running on cv02 at handoff (do not kill)
- **SK1 (SKCDF auxiliary balanced head):**
  - tmux `=sk1`, GPUs 4–6, 20 runs: sk1_BsD, sk1_BsDB, sk1_AB and sk1_BsDBn, seeds 0–4 each.
  - ETA about 05:00–06:00 IST, 22 Oct. At 20:50 the main runs were at steps 13k–14k; AB s0 and s1 were done.
  - Code: gaint `el_sk1` `0ea71df`; rescorer `41869d6`.
  - Files: `team_2026-10-21/skcdf/` (protocol_v2, review_v2, log).
- **AL1 v2 (ALHVR-EL):**
  - tmux `=al1`, GPUs 0–3 and 7, 35 runs: A5, AL5, ALd5, ALdh5, CPS5, CPSm5 and BsM5, seeds 0–4 each.
  - ETA 23 Oct, 20:00–24:00 IST.
  - The step-6k check passed for all five SSL arms (review_v2 addenda 1–3).
  - Watch item: ALdh5's gradient share; a single 2.62 at 6k, then 0.34–1.68.
  - Code: gaint `el_alhvr` `3a94457`.
  - Files: `team_2026-10-21/alhvr/`.
- **GPU ledger:** `team_2026-10-21/gpu_ledger.md`.

## Backup at handoff
- `scripts/relay_cv02_21oct.sh` copied the finished cv02 outputs to gaint `/home/noob/work/cv02_noob_el/{el_alhvr,el_sk1}` with an MD5 manifest check.
  - ALHVR: A5 s0–2, BsM5 s0 and s2, C1–C3 checks, reports.
  - SKCDF: identity checks, smoke runs, AB s0–1, reports.
- Runs still training were NOT copied. Relay them after they finish (same script, new run list).
- cv02 `/tmp` is wiped on reboot.

## Next steps
1. **SK1 done (about 06:00 on 22 Oct).** Resume agent 3 to:
   - send PL counts and conf_frac at 4k and 20k to the critic;
   - run the logit-adjustment control;
   - run the rule-1 analysis over the 4 cell sets (all 50 / without the noisy cell / without the 7 twins / without both), plus the bootstrap and E1.

   Then resume agent 4 to recompute everything independently. Relay to gaint with MD5. Report to the user only after the critic verifies.
2. **AL1 done (23 Oct evening).** The same pattern with agents 1 and 2. Agent 2 also checks that every scored checkpoint is step 20,000.
3. **Handbook:** refresh it after the verified results (docs 10, 11, 15, 00, 16), run `sync_sources.sh`, then commit.
4. **cv02 tmux:** the idle sessions `al1chk`, `sk1chk` and `sk1smoke` belong to us and can be closed once the runs are relayed.
