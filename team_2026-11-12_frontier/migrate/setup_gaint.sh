#!/usr/bin/env bash
# Run ON gaint after sync_to_gaint.sh (lead, 13 Nov 2026). Idempotent. Builds the two-account layout exactly as on the
# laptop: /home/yugma/.noobsurd (first account, holds the shared data) and /home/yugma/.other (second account) whose
# projects, history, settings, tasks etc. are symlinks into .noobsurd, so either login sees the same sessions, memory
# and projects. Credentials are created by the user's own /login in each dir; nothing here touches them.
set -eu
Y=/home/yugma
[ "$(hostname)" = giant ] || { echo "run this on gaint"; exit 1; }
[ -d $Y ] && [ -O $Y ] || { echo "STOP: run first: sudo install -d -o noob -g noob /home/yugma"; exit 1; }
[ -d $Y/.noobsurd/projects/-home-yugma-mtp ] || { echo "STOP: sync first (no project sessions under $Y/.noobsurd/projects)"; exit 1; }
mkdir -p $Y/.other
for n in agents commands feedback file-history jobs output-styles paste-cache plans projects session-env shell-snapshots tasks teams themes todos uploads; do
  mkdir -p $Y/.noobsurd/$n
  [ -L $Y/.other/$n ] || { [ -e $Y/.other/$n ] && { echo "STOP: $Y/.other/$n exists and is not a link"; exit 1; }; ln -s $Y/.noobsurd/$n $Y/.other/$n; }
done
for n in history.jsonl settings.json; do
  [ -e $Y/.noobsurd/$n ] || { echo "STOP: $Y/.noobsurd/$n missing (sync first)"; exit 1; }
  [ -L $Y/.other/$n ] || ln -s $Y/.noobsurd/$n $Y/.other/$n
done
chmod 700 $Y $Y/mtp/research/papers 2>/dev/null || true
# aliases (the plain `claude` on gaint keeps using ~/.claude for the other projects there)
if ! grep -q 'MTP orchestrator' ~/.bashrc; then
  cp ~/.bashrc ~/.bashrc.bak-mtp-move
  cat >> ~/.bashrc <<'A'

# MTP orchestrator (moved from the laptop, Nov 2026): two accounts, shared projects / sessions / memory.
alias claude-nb='CLAUDE_CONFIG_DIR=/home/yugma/.noobsurd ~/.local/bin/claude'
alias claude-oth='CLAUDE_CONFIG_DIR=/home/yugma/.other ~/.local/bin/claude'
A
fi
# paper-mcp: venv + user services (started only once the user has copied the .env and the tunnel credential)
if [ -d $Y/paper-mcp ] && [ ! -x $Y/paper-mcp/.venv/bin/python3 ]; then
  ( cd $Y/paper-mcp && ~/.local/bin/uv venv .venv --python 3.12 && ~/.local/bin/uv pip install --python .venv/bin/python3 -r requirements.txt )
fi
mkdir -p ~/.config/systemd/user $Y/.cloudflared; chmod 700 $Y/.cloudflared
cat > ~/.config/systemd/user/paper-mcp.service <<'U'
[Unit]
Description=Paper research MCP server
After=network-online.target

[Service]
WorkingDirectory=/home/yugma/paper-mcp
Environment=PAPERS_DIR=/home/yugma/papers
ExecStart=/home/yugma/paper-mcp/.venv/bin/python3 /home/yugma/paper-mcp/server.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
U
cat > ~/.config/systemd/user/researchmcp-tunnel.service <<'U'
[Unit]
Description=Cloudflare Tunnel for researchmcp.noobsurd.space
After=network-online.target paper-mcp.service

[Service]
ExecStart=/usr/local/bin/cloudflared tunnel --config /home/yugma/.cloudflared/researchmcp.yml run researchmcp
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
U
systemctl --user daemon-reload
echo "layout:"; ls -la $Y/.other | awk '{print $9, $10, $11}' | grep -- '->' | head -30
echo "paper-mcp: .env $( [ -s $Y/paper-mcp/.env ] && echo present || echo MISSING ), tunnel yml $( [ -s $Y/.cloudflared/researchmcp.yml ] && echo present || echo MISSING ), library $( [ -s $Y/paper-mcp/library.sqlite3 ] && echo present || echo missing )"
echo "SETUP DONE. Next: tmux new -s orch; cd /home/yugma/mtp; claude-oth  (then /login), then: claude-oth --resume 149c5b71-58ef-4f40-bd7c-5742a5e4643f"
