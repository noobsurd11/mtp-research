# Moving the MTP orchestrator from the laptop to gaint (plan, 13 Nov 2026)

Why: the laptop rebooted six times on 13 Nov and each reboot stops every agent. gaint is always on, is on the campus network, and already holds the GPU work. The user asked (13 Nov 23:40) to move everything once the running agents finish, and to keep both accounts able to resume the same sessions, projects and connectors.

## User decisions (13 Nov 23:50)
1. gaint gets `/home/yugma` owned by `noob` (one sudo command by the user). Every recorded path stays valid.
2. The Research MCP (paper-mcp + its Cloudflare tunnel) moves to gaint. The user copies the two secret items; the lead never reads or copies them.
3. `research/papers` PDFs move too, into a folder only `noob` can read.

## Layout on gaint (mirror of the laptop)
- `/home/yugma/mtp` = the project tree (same path as on the laptop, so session ids, memory paths, script constants and old records all hold).
- `/home/yugma/.noobsurd` = config dir of the first account; it holds the shared data (projects, sessions, memory, history, settings, tasks, skills).
- `/home/yugma/.other` = config dir of the second account; `projects`, `history.jsonl`, `settings.json`, `tasks`, `teams`, `todos`, `file-history`, `session-env`, `shell-snapshots`, `plans`, `agents`, `commands` and the rest are symlinks into `.noobsurd`, as on the laptop. Each dir keeps its own login, plugins and skills.
- Aliases on gaint: `claude-oth` (second account) and `claude-nb` (first account). Plain `claude` on gaint is unchanged (it keeps `~/.claude` for the other projects there).
- claude.ai connectors (Research MCP, Docs and the others) belong to the account, so they come with the login. Run `/mcp` once after logging in.
- `scripts/gssh.sh`, `gput.sh`, `gget.sh` run locally when the host is gaint (hostname `giant`), so every documented command keeps working.

## Steps
| # | Who | Where | What |
|---|---|---|---|
| 0 | user | gaint | `sudo install -d -o noob -g noob /home/yugma` |
| 1 | lead | laptop | `migrate/sync_to_gaint.sh bulk` (repeatable; first pass while agents still run) |
| 2 | lead | gaint | `bash /home/yugma/mtp/research/team_2026-11-12_frontier/migrate/setup_gaint.sh` (links, aliases, paper-mcp venv, service files) |
| 3 | user | laptop | copy the two secret items (below) |
| 4 | lead | both | when every agent has finished: stop paper-mcp and its tunnel on the laptop, `sync_to_gaint.sh final`, start both services on gaint |
| 5 | user | gaint | `tmux new -s orch`, `cd /home/yugma/mtp`, `claude-oth`, `/login` (second account), `/mcp`, then `claude-oth --resume 149c5b71-58ef-4f40-bd7c-5742a5e4643f` |
| 6 | user | gaint | first account, any time after its weekly reset (16 Nov 05:30): `claude-nb`, `/login`. Either alias then resumes the same session id |

Step 3, run on the laptop by the user:
```
scp /home/yugma/paper-mcp/.env noob@172.18.22.20:/home/yugma/paper-mcp/.env
scp ~/.cloudflared/researchmcp.yml "$(awk '/credentials-file/{print $2}' ~/.cloudflared/researchmcp.yml)" noob@172.18.22.20:/home/yugma/.cloudflared/
```
Step 4 commands: laptop `systemctl --user disable --now researchmcp-tunnel paper-mcp`; gaint `systemctl --user enable --now paper-mcp researchmcp-tunnel`. The tunnel must run on one machine only, or requests are split between the two.

## What is not copied
`.credentials.json`, `.claude.json` (each login writes its own on gaint), per-machine state (`daemon`, `sessions`, `state`, `cache`), sessions of the other laptop projects, the paper-mcp `.env` and the Cloudflare credential (user copies those).

## Limits (stated plainly)
- Resuming this exact session on another machine is expected to work because the paths and session files are identical, but it is untested. If it fails, a fresh session there starts from the memory handoff and `log.md`; all state is on disk.
- A workflow cannot be moved while it runs. Move after the running ones finish.
- Usage caps belong to the account, not to the machine.
- After the move the laptop copy of `/home/yugma/mtp` is stale. Work only on gaint (from the laptop: `ssh` to gaint, `tmux attach -t orch`).
