#!/usr/bin/env bash
# Laptop -> gaint sync for the move of the MTP orchestrator (lead, 13 Nov 2026). Safe to run many times (rsync).
# Needs /home/yugma on gaint owned by noob (the user: sudo install -d -o noob -g noob /home/yugma).
# Copies only: /home/yugma/mtp, the MTP part of the Claude state, paper-mcp code and its fetched papers.
# Never copies credentials: no .credentials.json, no .claude.json, no paper-mcp .env, no Cloudflare credential files.
# usage: sync_to_gaint.sh quick|bulk|refresh|final
#   quick   = Claude state + MTP sessions and memory + the current team folder and handbook (minutes; enough to log in and resume)
#   bulk    = quick + the whole project tree + paper-mcp code + fetched papers
#   refresh = project tree + MTP agent transcripts and memory again, WITHOUT the main session file, history or settings
#             (use once a session runs on gaint, so its own files are not overwritten)
#   final   = refresh + the paper library database (paper-mcp must be stopped on the laptop)
set -u
MODE=${1:?quick|bulk|refresh|final}
SID=149c5b71-58ef-4f40-bd7c-5742a5e4643f
H=${GAINT_HOST:-noob@172.18.22.20}
E="ssh -o BatchMode=yes -o ConnectTimeout=10"
R=(rsync -a --partial --info=stats1 -e "$E")
$E $H 'test -d /home/yugma && test -O /home/yugma' || { echo "STOP: /home/yugma missing on gaint or not owned by noob"; exit 1; }
set -e
state(){
  echo "== Claude state of the first config dir (shared data; no credentials, no per-machine state)"
  "${R[@]}" --exclude '.credentials.json' --exclude '.claude.json*' --exclude 'policy-limits*' --exclude 'remote-settings*' \
    --exclude 'daemon' --exclude 'daemon.log' --exclude 'sessions' --exclude 'state' --exclude 'cache' --exclude 'backups' \
    --exclude 'mcp-needs-auth-cache.json' --exclude '.last-*' --exclude 'projects' \
    /home/yugma/.noobsurd/ $H:/home/yugma/.noobsurd/
  echo "== second config dir: its own plugins and skills"
  $E $H 'mkdir -p /home/yugma/.other /home/yugma/paper-mcp /home/yugma/.cloudflared && chmod 700 /home/yugma /home/yugma/.cloudflared'
  "${R[@]}" /home/yugma/.other/plugins /home/yugma/.other/skills $H:/home/yugma/.other/
}
projects(){ # $1 = extra rsync excludes
  echo "== sessions, memory and agent transcripts of the MTP project only"
  "${R[@]}" "$@" --include '/-home-yugma-mtp*/' --include '/-home-yugma-mtp*/**' --exclude '*' \
    /home/yugma/.noobsurd/projects/ $H:/home/yugma/.noobsurd/projects/
}
tree(){
  echo "== project tree /home/yugma/mtp"
  "${R[@]}" /home/yugma/mtp/ $H:/home/yugma/mtp/
}
mcp(){
  echo "== paper-mcp code (no .env, no venv, no log, no database) and fetched papers (private)"
  "${R[@]}" --exclude '.env' --exclude '.env.orig' --exclude '.venv' --exclude '__pycache__' --exclude 'server.log' --exclude 'library.sqlite3*' \
    /home/yugma/paper-mcp/ $H:/home/yugma/paper-mcp/
  [ -d /home/yugma/papers ] && "${R[@]}" /home/yugma/papers/ $H:/home/yugma/papers/ && $E $H 'chmod 700 /home/yugma/papers'
}
case $MODE in
  quick)
    state; projects
    echo "== current team folder, handbook and top-level files first"
    $E $H 'mkdir -p /home/yugma/mtp/research'
    "${R[@]}" --exclude '/research/' --exclude '/datasets/' /home/yugma/mtp/ $H:/home/yugma/mtp/
    "${R[@]}" /home/yugma/mtp/research/team_2026-11-12_frontier /home/yugma/mtp/research/handbook $H:/home/yugma/mtp/research/ ;;
  bulk) state; projects; tree; mcp ;;
  refresh) projects --exclude "/-home-yugma-mtp/$SID.jsonl"; tree ;;
  final)
    systemctl --user is-active --quiet paper-mcp.service && { echo "STOP: paper-mcp.service still runs here; stop it first"; exit 1; }
    projects --exclude "/-home-yugma-mtp/$SID.jsonl"; tree; mcp
    echo "== paper library database"; "${R[@]}" /home/yugma/paper-mcp/library.sqlite3 $H:/home/yugma/paper-mcp/ ;;
  *) echo "unknown mode"; exit 2 ;;
esac
echo "== sizes on gaint"; $E $H 'du -sh /home/yugma/mtp /home/yugma/.noobsurd /home/yugma/.other /home/yugma/paper-mcp 2>/dev/null; ls /home/yugma/.noobsurd/projects | head'
echo "SYNC $MODE DONE $(date '+%F %T')"
