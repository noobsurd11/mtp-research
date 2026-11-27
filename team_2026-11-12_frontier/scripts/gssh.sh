#!/usr/bin/env bash
# gssh.sh: run a command on gaint through the Cloudflare tunnel, retrying the flaky handshake.
# usage: gssh.sh '<remote command>'   (reads the command from $1; stdin is not forwarded)
# Exit code: the remote command's, or 255 if every attempt failed to connect.
tries=${GSSH_TRIES:-6}
# On gaint itself (hostname giant; the orchestrator moved there on 14 Nov 2026) the command runs locally.
if [ "$(hostname)" = giant ]; then bash -c "$1" < /dev/null; exit $?; fi
# Hosts: the direct address works on the institute VPN; the Cloudflare tunnel works anywhere but drops handshakes.
hosts=("noob@172.18.22.20" "ssh.noobsurd.info")
for i in $(seq 1 "$tries"); do
  host=${hosts[$(( (i - 1) % 2 ))]}
  ct=25; [ "$host" = "noob@172.18.22.20" ] && ct=6
  out=$(ssh -n -o BatchMode=yes -o ConnectTimeout=$ct -o ServerAliveInterval=15 -o ServerAliveCountMax=4 "$host" "echo __GSSH_OK__; $1" 2>&1)
  rc=$?
  if printf '%s' "$out" | grep -q '^__GSSH_OK__$'; then
    printf '%s\n' "$out" | sed '/^__GSSH_OK__$/d'
    exit $rc
  fi
  [ $((i % 2)) -eq 0 ] && sleep $((i * 2))
done
echo "gssh: no connection after $tries attempts: $(printf '%s' "$out" | head -1)" >&2
exit 255
