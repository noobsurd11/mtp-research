# Arm builder brief (x4 wave, 27 to 28 Nov 2026)

You implement one or more screening arms for the EL-segmentation benchmark. The lead launches the 20k-step runs; you build, verify and hand over.

## Read first
- `/home/yugma/mtp/research/team_2026-11-27_arch/CONTEXT.md` (laptop): task, protocol, what was already tested.
- On gaint (`ssh -o BatchMode=yes noob@172.18.22.20`): `/home/yugma/mtp/research/team_2026-11-27_arch/harness/RUNBOOK.md`, `harness/x4/BUILD_LOG_x4.md`, `harness/x4/NEW_CARD_TEMPLATE.md`; `/home/yugma/mtp/research/team_2026-11-12_frontier/harness/LEAD_INSTRUCTIONS.md` (hard rules 1 to 10 apply: shared-lab rules on cv02, lane rule = never start on a GPU where another user holds > 4,096 MiB, record PIDs, stop only by PID, tmux exact-match names, never infer on test50 or e1_106, no pattern kills); `harness/DESIGN.md` sections 1.2 to 1.9 (config system, model factory, losses, trainer).
- The scout reports that motivate your arm are under `/home/yugma/mtp/research/team_2026-11-27_arch/scouts/<id>/REPORT.md` and `papers.tsv` (laptop).

## Base
- Code base: gaint worktree `/home/noob/work/bench_wt_x4`, branch `bench_x4` (from 03375d4, the COMBO commit). Make your own worktree `/home/noob/work/bench_wt_x4_<yourid>` on a new branch `x4_<yourid>` from bench_x4's HEAD. Never edit another worktree, the house venv, or existing data folders.
- Comparator: the COMBO card (HRNet-W18 encoder + U-Net++ decoder, PF schedule, SWAD steps 10k to 20k, swad readout, v1.1 labels, cv5v3 roots). Your arm = COMBO + exactly the change being tested, unless the arm is by nature a different recipe (say so in the card).
- New options are opt-in keys, default off. **Identity**: with your keys off, a 5-step CPU run must be bit-identical to COMBO (use the existing identity-check pattern, harness/x4/x4_idcheck.py or the I-check scripts). Record IDENTICAL.
- Installs: only into a new isolated venv that shares torch read-only (the venv_sam2 pattern in DESIGN.md), and only public weights. Record versions and weight md5s.

## Deliverables per arm
1. Commit(s) on your branch (small; message ends with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`), card YAML in `bench/methods/`, unit test for any new loss/module (shape, gradient, a hand-computed value).
2. Identity result (keys off), and a measured peak memory from a short GPU smoke on cv02 (at most 200 steps, lane rule, PID recorded, outputs removed after), giving the gate (= peak + 2,048 MiB).
3. If the arm needs precomputed inputs (teacher soft labels, pseudo-labels, distance maps), the script that makes them, run on the correct fold-safe data only: a teacher for fold k may only be a model that never trained on fold k's held-out cells; never use test50 or E1 cells. Inference on cv02 under the lane rule is allowed for this.
4. A handover note `/home/yugma/mtp/research/team_2026-11-27_arch/harness/x4/arms/<card>.md` on gaint: what the arm changes, paper ids it comes from, commit, identity result, peak, gate, any precomputed input with md5, and the exact jobs line(s) for x4_make_jobs.py (5 folds x seeds 5, 6).
5. Message the lead (SendMessage to team-lead) when an arm is ready. Do not launch 20k-step runs.

## Rules
Plain English, no em dashes. E = measured, S = judgement. Append progress to `harness/x4/arms/BUILD_<yourid>.md` after each step so a restart loses nothing. Never print credentials.
