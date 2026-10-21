# Agent team, 21 Oct 2026: ALHVR and SKCDF retry

The leader (team-lead, the user's main session) orchestrates four agents:

| # | Role | Folder |
|---|---|---|
| 1 | ALHVR trainer | `alhvr/` |
| 2 | ALHVR critic | `alhvr/` (`review_*.md`) |
| 3 | SKCDF trainer | `skcdf/` |
| 4 | SKCDF critic | `skcdf/` (`review_*.md`) |

## Read first (everyone)
1. Memory: `/home/yugma/.noobsurd/projects/-home-yugma-mtp/memory/`. Read every file. These are the user's standing rules.
2. `~/mtp/research/SESSION_HANDOFF_2026-10-13.md`.
3. Handbook `~/mtp/research/handbook/`:
   - 00 (facts);
   - 03 and 17 (data, E-SCDD audit);
   - 05 §6 (ALHVR: paper, code, our port, audit) and the SKCDF part of §7;
   - 07 (rules and stats);
   - 10 (P13 to P19, esp. P17 SKCDF-style decoupling);
   - 11, 13 (pitfalls; B3 and E11 for ALHVR);
   - 14 (code, infra), 15.
4. Source notes: `analysis/alhvr_audit.md`, `literature/notes/`, papers in `literature/pdfs*/` (local only, never redistribute).

## User's goal
No more "dumb trainings". ALHVR and SKCDF come from medical imaging (ACDC, Synapse: 3-D volumes, organs, large unlabelled pools). Our data is 2-D EL solar-cell images with thin, rare cracks, small inactive regions and a small unlabelled pool. Adapt the method to the data; never copy-paste it. Every run must answer a stated question.

## Gate (critics hold full authority)
1. The trainer writes the protocol: question, hypothesis, arms (one change each), controls, seeds, fixed steps, metric, decision rule, data version and compute. It goes in `<track>/protocol_vN.md` and later in `~/mtp/research/protocols/`.
2. The critic replies in `<track>/review_vN.md` with `APPROVED`, `CHANGES` or `BLOCKED`, plus reasons. The critic also checks code diffs, smoke runs and logs during and after runs, and proposes new ideas in `<track>/ideas.md`.
3. No launch, real or smoke beyond a few hundred steps, without `APPROVED` on the current version. The critic may stop a running job if it finds a bug.
4. Results: the trainer writes the analysis; the critic verifies it independently, recomputing from the raw per-run files, before anything is reported to the leader as a finding.

## Data (owned jointly by both critics)
- The user says a newer E-SCDD (Pratt et al.) release adds images and a test split. Find it: HF hub, the paper, GitHub. Compare it with local `~/mtp/datasets/escdd_full` (audit 12 Oct, handbook 17).
- Decide how both tracks use it: splits, leakage with our external pool and test, synthetic `_rf` images, and whether old P-series baselines must be re-run on the new split for a fair comparison.
- Write the decision to `data/decision.md`. Both critics sign it, and the leader is told.
- Final runs wait for this decision. Anything that needs the user's manual work (login, licence, download): message the leader, who asks the user.

## Compute
- gaint (`noob@172.18.22.20`) first. cv02 (`cv02@10.8.1.106`, host himtenduh, `/tmp/noob_el`, shared account, wiped on reboot) only for extra capacity.
- Never split one experiment's arms or seeds across machines.
- Book GPUs in `gpu_ledger.md` (machine, GPU, track, tmux session, start, expected end) before launch, and free them after. Check `nvidia-smi` first.
- Every cv02 output gets copied back to gaint (`/home/noob/work/cv02_noob_el/`) with MD5 checks, per the memory note on the cv02 backup. Never put keys on cv02 and never use `ssh -A`.
- Use tmux on the servers, `-t "=name"`, one git worktree per experiment (`git worktree add ../el_<name>`), and record the commit in `REVISION`.

## Communication
- SendMessage to `team-lead` for:
  - decisions only the user can make;
  - manual steps;
  - a launch (after `APPROVED`);
  - a verified result;
  - a block lasting more than 30 min.
- Trainer and critic message each other directly. Keep `<track>/log.md` (timestamped IST, terse) so anyone can catch up.
- Writing style for the user: terse, no em-dashes, sourced numbers, verdict separated from reading.
