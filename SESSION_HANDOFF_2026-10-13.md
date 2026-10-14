# Session handoff, 13 Oct 2026 (for the next Claude Code session)

Two sessions ran on 13 Oct:
- the 7 to 13 Oct session closed at about 01:30 IST;
- a follow-up session ran from about 01:30 to 20:30 IST.

The handbook (`handbook/`) explains the project to a human guide agent. This file is the short operational resume point for Claude. Where they disagree, `results/*/README.md` wins, then the handbook.

## 1. State at close (13 Oct, about 20:30 IST)
- **All experiments are done:** P1 to P19, E1, the E-SCDD audit, the EMA check and the qualitative panel. Each has a README under `results/`. Nothing of ours is running.
- **Added in the follow-up session** (the user: "how about we try the DCA paper and SKCDF? ...", then "cool, go with ur calls"; later "youve got 3hrs to wrap up ... experiment whatever you think useful"):
  - **P13 Amendment 2:** BsM5 seeds 3–4 (post hoc). BsM5 − A5c still passes, now +0.029 / +0.107 / +0.045. CsM5 − BsM5 is now n.d.
  - **P17:** SKCDF-style decoupled decoder on BsM5. BsD5 − BsM5 is n.d. (thresholds ≈ 40% of the gain); BsD5 − A5c passes. DCA was not run (`results/p17/README.md`).
  - **EMA check:** at step 20,000 the EMA teacher equals the student within ±0.005 (`results/ema_check/`). Doc 13 C11 is mostly resolved.
  - **Qualitative panel:** `results/qualitative/fig_qualitative_5pct.png`.
  - **P18 (exploratory):** the BsM recipe at 10% and 20%. 8 runs (17:31–19:40 IST), rc = 0, pipeline check passed. Arithmetic: BsM10 − A10 (3 v 3) and BsM20 − A20 (5 v 5) pass on inactive only (+0.132, +0.060); crack n.d. BsM20 s4 fails on the noisy cell; without that cell BsM10 passes on all three and BsM20 crack is just below (+0.013 vs 0.014). No locked verdict changes (`results/p18/README.md`).
- **14 Oct, P19:** at the user's request ("reproduce hanifi 2025, asap"; "no presumptions"), Hanifi et al. 2025 (IEA/AIE, 29-class Keras U-Net/SegNet) was reproduced with their code on the release split, no augmentation, 6 models + VGG16-UNet × 3 seeds (the user's choices). VGG16-UNet: features 0.678 vs 0.663, crack 0.352 vs 0.335, inactive 0.469 vs 0.550, defects 0.246 vs 0.326 (our test lacks dead cell and belt mark). `results/p19/README.md`. Backup pass 4 (09:33–09:36 IST): 101 files to gaint `cv02_noob_el/hanifi`, MD5 identical.
- **cv02 backup:** everything of ours under cv02 `/tmp/noob_el` (run dirs and checkpoints) is copied to gaint `/home/noob/work/cv02_noob_el/`, MD5-verified. Pass 3 (19:44–19:52 IST): P18 run dirs, `el_p13/reports/p18`, the queue spec, `diag/student`, `diag/e1v2`, `diag/e1p18.log`; 264 files including 16 checkpoints, MD5 identical on both sides.
- **Results summary:** `to_human/results_2026-10-12.md` is updated through P18. The user has seen the P17 report in chat.
- **Next, by the user's plan:** the mid-term presentation. The outline (`to_human/midterm_deck_outline.md`) and the proposal reframe were deliberately not rewritten: framing is the user's call.
- **Server state:** `handbook/15_status_remaining_work.md` §1c.

## 2. Read first
1. `handbook/15_status_remaining_work.md`: status, decisions waiting on the user (§3), remaining work (§4), housekeeping (§7).
2. `handbook/11_results_synthesis_and_claims.md`: the evidence table, and what can and cannot be claimed.
3. `to_human/results_2026-10-12.md`: what the user was told, with the evidence table for framing.
4. `results/p17/README.md`, `results/p18/README.md`, `results/ema_check/README.md`: the latest work.
5. `handbook/07_methodology_rules_and_statistics.md` and `14_code_and_infrastructure.md`: before designing or launching anything.

## 3. Figures for the deck (all cv02, test, revised labels unless stated)
| Figure | Shows |
|---|---|
| `results/p18/fig_p18_curve.png` | supervised vs the two SSL recipes against label fraction (5–100%); bottom row without the noisy cell |
| `results/qualitative/fig_qualitative_5pct.png` | predictions of A5c, CsM5, BsM5 and supervised 100% on 4 fixed test cells |
| `results/p13/fig_p13_bars.png`, `results/p17/fig_p17_bars.png` | the 5% arms, per seed |
| `results/p16/fig_p16_curve.png`, `fig_p16_curve_excell.png` | P16's curve (Cs recipe only) |
| `results/p6/fig_ladder.png`, `fig_label_scaling.png`, `fig_overlays.png` | the supervised recipe ladder and label scaling |
| `results/p5_region_pl/fig_p5_offset.png`, `results/figures/fig_method_routing.png` | pseudo-label offsets; the routing schematic |
| `results/e1/ext_montage.png`, `results/escdd_audit/escdd_samples.png` | the unseen-module extension; E-SCDD samples |

## 4. Waiting on the user (do nothing on these without an answer)
Full table in doc 15 §3. In short:
1. Thesis framing.
2. Whether "without `CSIR_00070_r8_c4`" becomes a standing check.
3. A larger test set, or E-SCDD's extra cells (data local, doc 17); wording for the label attribution.
4. Mid-term deck content.
5. Identity, institute and template for the MTP report.

## 5. Standing rules (the user's)
Also in memory: `mtp-el-ssl-project`, `ask-before-assuming`, `server-runs-tmux-parallel`, `cv02-shared-account-backup`.
- **No presumptions:** "framing depends on final results, no presumptions, ever". Batch questions and ask; hold launches while questions are open.
- **Experiments:**
  - lock a protocol in `protocols/` before launching;
  - match optimizer steps across arms; one change per arm;
  - final-step weights are primary; never compare arms across machines;
  - 5 vs 5 seeds for small effects;
  - label test-informed choices exploratory;
  - keep old-era numbers apart from P-series numbers.
- **Servers:**
  - Hosts: gaint `noob@172.18.22.20` (`/home/noob/work`); cv02 `cv02@10.8.1.106` (`/tmp/noob_el`, wiped on reboot; a shared lab login).
  - Run in tmux and use `tmux has-session -t "=name"`.
  - On cv02, never start on a GPU where another user holds > 4 GB.
  - Put new code in a git worktree on gaint.
  - Read-only unless the user asks. Never kill queues, processes or tmux sessions without the user's say-so.
  - The gaint `extpool_20261007` queue stays held and untouched.
  - Never use `ssh -A` into cv02 or place keys there; back up through the laptop relay.
- **Repo and secrets:**
  - Never push to GitHub without asking.
  - `papers/` and `literature/pdfs/` stay untracked and are never redistributed.
  - The Dropbox app secret is never exposed (rotation unconfirmed).
- **Commit trailers:** `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>` and `Claude-Session: https://claude.ai/code/session_01HzsHXC91MDtjqG2abZt5qU`.
- **Writing:** terse, no em-dashes, no buzzwords, they/them for the user. Sourced numbers; keep the locked verdict, the robustness check and the reading apart.
- **The handbook:** after any new result, update docs 10, 11, 15, 00 and 16 (plus any doc the result touches), run `bash handbook/sync_sources.sh`, then commit.

## 6. Tools and paths
- Local Python: `~/mtp/research/.venv/bin/python`.
- Post-analysis: `scripts/post_ssl.sh pN <cv02 gpu> <n>` (P9–P14, P17, P18), `scripts/post_p15.sh`, `scripts/post_p16.sh`. Also `scripts/p16_excell.py`, `p17_excell.py` and `p18_curve.py` (noisy-cell sensitivity), and `scripts/qualitative_panel.py`. Doc 14 lists them all.
- cv02 helpers: `scripts_cv02/rescore_weights.py` (score student or teacher), `scripts_cv02/pred_dump.py` (predictions for figures). Copies sit in cv02 `diag/student/`.
- Launch specs: `scripts_cv02/*.spec`. P13 Amendment 2, P17 and P18 used `launch_set_p13.sh` (in `el_p13`) and its `el_p17` copy.
- Data (local): `~/mtp/datasets/`.
- Transcripts:
  - the first 13 Oct session: `~/.claude/projects/-home-yugma/57bebbba-992f-43ae-8c6c-f7004d0f15c5.jsonl`;
  - the follow-up: `~/.claude/projects/-home-yugma-mtp/` (session `bc23d1ca…` and its continuations).

## 7. Housekeeping left open
- Idle tmux sessions of ours: about 20 older ones on cv02 plus `p13a2`, `p17run`, `p17smoke` and `p18`; 3 on gaint. Close them only if the user agrees.
- `scripts/aggregate_runs.py` has been untracked since 10 Oct; its origin is unrecorded. Left as is.
- Any run after 13 Oct needs another backup pass to gaint `cv02_noob_el`.
