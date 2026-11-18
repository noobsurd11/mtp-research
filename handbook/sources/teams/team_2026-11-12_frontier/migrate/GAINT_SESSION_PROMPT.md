# Instructions for the gaint copy of the orchestrator session (written by the laptop copy, 14 Nov 2026, 00:10 IST)

You are the same orchestrator session (id 149c5b71-58ef-4f40-bd7c-5742a5e4643f), resumed on gaint (hostname `giant`) by the user just before they went to sleep. The user asked for this move because the laptop keeps rebooting (memory: `orchestrator-move-to-gaint`; plan: `migrate/README.md` in this folder).

## Until the handover: wait, change nothing
The laptop copy of this session is still running and still owns the work. Three of its workflows are in flight: wave 2a integration and review (`wf_5aac002b-60a`), the second batch of method teams with sweepers and critic (`wf_5a28a74b-3ac`), and the SKR2C stage-2 build and review (`wf_c2eda0f1-f61`). Two orchestrators acting at once would collide.
- Do not start agents or workflows, do not edit project files, do not touch any queue or GPU job, do not write memory files.
- Check every 20 minutes whether `/home/yugma/mtp/research/team_2026-11-12_frontier/migrate/HANDOVER.md` exists (use ScheduleWakeup; one `ls` per check, nothing else).

## When HANDOVER.md exists: take over
1. Read HANDOVER.md in full. It lists what finished, what is still owed and the first actions.
2. Read the memory file `mtp-session-handoff.md`, the last 30 lines of `log.md` and the tail of `harness/BUILD_LOG.md`.
3. From then on you are the only orchestrator. Everything runs on gaint: paths are identical (`/home/yugma/mtp`), and `scripts/gssh.sh`, `gput.sh`, `gget.sh` run locally here. cv02 is reached with `ssh cv02@10.8.1.106` as before (never with agent forwarding, never copy a key there).
4. Standing rules are unchanged: `harness/LEAD_INSTRUCTIONS.md`, `BRIEF.md` section 7, the memory files. Log every step in `log.md` with the clock time.

## If the laptop never hands over
If HANDOVER.md is still missing at 05:00 IST on 14 Nov, assume the laptop died. `cat /home/yugma/mtp/.last_sync_from_laptop` shows when the project tree was last copied; work written on the laptop after that time is not here. Then take over from what is on disk: read `migrate/README.md`, the memory handoff, `log.md` and `harness/BUILD_LOG.md`; check which outputs exist (`cards/T11..T13*`, `cards/WAVE3_REVIEW.md`, `harness/LAUNCH_REQUEST_w2a.md`, `harness/REVIEW_W2A.md`, `../team_2026-10-31_next/review_s2c_stage2.md`); relaunch only what is missing with the scripts in `log/` (`workflow_T2_family_teams.js`, `workflow_W1c_W2build.js`, `workflow_S2C_stage2.js`; try `resumeFromRunId` first, and if the engine refuses it on this machine, run the script fresh). The paper-mcp service and its tunnel on gaint (`systemctl --user start paper-mcp researchmcp-tunnel`) may be started only in this case or when HANDOVER.md says so, because the tunnel must run on one machine at a time.

## Usage
Both copies use the same account until the handover, so the 5-hour cap is shared. Keep the waiting checks minimal.
